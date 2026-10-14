#!/usr/bin/env python3
"""Dependency context, planner repo map, land, and clean. Fixture and local git only."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.clean import clean_runs  # noqa: E402
from scripts.v3.harness.cli import main  # noqa: E402
from scripts.v3.harness.context import CONTEXT_LIMIT, repo_map, task_prompt  # noqa: E402
from scripts.v3.harness.dag import admit_goal, plan_prompt  # noqa: E402
from scripts.v3.harness.errors import HarnessError  # noqa: E402
from scripts.v3.harness.isolation import GitWorktreeIsolator  # noqa: E402
from scripts.v3.harness.land import land_run  # noqa: E402
from scripts.v3.harness.log import NullLog  # noqa: E402
from scripts.v3.harness.orchestrate import create_run, drive_run  # noqa: E402
from scripts.v3.harness.providers import FixtureProvider, ProviderResult  # noqa: E402
from scripts.v3.harness.state import RunStore  # noqa: E402


ROUTE = {"fixture_id": "F-M1B-001", "selected_route_id": "route-a", "status": "selected"}
TOKEN = "sk-ant-SECRETSECRET"


class OpsTests(unittest.TestCase):
    def test_dependency_prompt_includes_a_capped_summary_diff_and_commit(self) -> None:
        plain = task_prompt({"task": "Just this.", "depends_on": []}, [])
        self.assertEqual(plain, "Just this.")
        deps = []
        for index in range(4):
            deps.append(
                {
                    "commit": f"abc{index}",
                    "diff": "x" * 5000,
                    "id": f"dep-{index}",
                    "task": "Build",
                    "text": f"done {TOKEN}",
                }
            )
        prompt = task_prompt({"depends_on": [item["id"] for item in deps], "task": "Test it."}, deps)
        self.assertIn("Dependency context:", prompt)
        self.assertIn("Summary: done [REDACTED]", prompt)
        self.assertIn("Commit: abc0", prompt)
        self.assertIn("Diff:", prompt)
        self.assertNotIn(TOKEN, prompt)
        self.assertIn("[dependency context truncated]", prompt)
        self.assertLessEqual(len(prompt), len("Test it.\n\n") + CONTEXT_LIMIT + len("\n[dependency context truncated]"))
        missing = task_prompt({"depends_on": ["gone"], "task": "Test it."}, [])
        self.assertIn("Summary: missing", missing)

    def test_repo_map_is_capped_and_keeps_one_goal_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            (repo / "src").mkdir()
            (repo / "src" / "app.py").write_text("print(1)\n", encoding="utf-8")
            (repo / "README.md").write_text("Goal:\n" + ("word " * 400) + "TAILMARKER\n", encoding="utf-8")
            subprocess.run(["git", "add", "src/app.py", "README.md"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "docs"], cwd=repo, check=True, capture_output=True)
            mapped = repo_map(repo)
            self.assertIn("src/app.py", mapped)
            self.assertIn("README.md", mapped)
            self.assertNotIn("TAILMARKER", mapped)
            self.assertNotIn("Goal:\n", mapped)
            prompt = plan_prompt("Alpha task.\nBeta task.", repo=repo)
            self.assertEqual(prompt.count("Goal:\n"), 1)
            self.assertIn("src/app.py", prompt)
            planned = admit_goal(
                "Alpha task.\nBeta task.",
                candidates=["fixture"],
                allow_live=False,
                retries=0,
                backoff_seconds=0,
                timeout_seconds={},
                log=NullLog(),
                open_adapter=lambda name: FixtureProvider(),
                repo=repo,
            )
        self.assertEqual([task["id"] for task in planned["tasks"]], ["task-1", "task-2"])
        self.assertEqual(planned["source"], "provider")

    def test_dependent_run_sees_landed_context_and_land_merges_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            prompts: list[str] = []

            class Recording:
                def execute(self, request, *, allow_live=False, timeout_seconds=None):
                    del allow_live, timeout_seconds
                    prompts.append(request.task)
                    if "Dependency context:" not in request.task:
                        (Path(request.cwd) / "note.txt").write_text("from-run\n", encoding="utf-8")
                        return ProviderResult(provider="writer", argv=("writer",), text=f"wrote {TOKEN}", live=False)
                    return ProviderResult(provider="writer", argv=("writer",), text="used context", live=False)

            with tempfile.TemporaryDirectory() as state_name:
                state = Path(state_name)
                store = RunStore(state)
                record = create_run(
                    store,
                    goal="build\ntest",
                    planned=[
                        _planned("Write the note.", "build"),
                        _planned("Read the note.", "test", ["build"]),
                    ],
                    candidates=[["writer"], ["writer"]],
                    route=ROUTE,
                    concurrency=1,
                )
                finished = drive_run(
                    store,
                    record["run_id"],
                    allow_live=False,
                    retries=0,
                    backoff_seconds=0,
                    timeout_seconds={},
                    route_id="route-a",
                    open_adapter=lambda name: Recording(),
                    sleep=lambda seconds: None,
                    max_rounds=0,
                    isolator=GitWorktreeIsolator(repo),
                    base_ref="HEAD",
                )
                self.assertEqual(finished["status"], "completed")
                self.assertEqual(len(prompts), 2)
                self.assertIn("Summary: wrote [REDACTED]", prompts[1])
                self.assertIn("Commit:", prompts[1])
                self.assertIn("Diff:", prompts[1])
                self.assertIn("note.txt", prompts[1])
                self.assertNotIn(TOKEN, prompts[1])
                before = _rev(repo, "main")
                (repo / "DIRTY").write_text("nope\n", encoding="utf-8")
                with self.assertRaises(HarnessError) as dirty:
                    land_run(store, finished["run_id"], repo=repo, into="main")
                self.assertEqual(str(dirty.exception), "working tree is dirty")
                self.assertEqual(_rev(repo, "main"), before)
                self.assertEqual(store.load(finished["run_id"])["land"]["status"], "refused")
                (repo / "DIRTY").unlink()
                stdout = _Buffer()
                with patch("scripts.v3.harness.cli.ROOT", repo), patch("sys.stdout", stdout):
                    code = main(["land", finished["run_id"], "--into", "main", "--state-dir", str(state)])
                self.assertEqual(code, 0)
                payload = json.loads(stdout.getvalue())
                self.assertEqual(payload["land"]["status"], "merged")
                self.assertEqual(payload["land"]["branch"], "main")
                self.assertTrue(payload["land"]["commit"])
                report = json.loads((state / f"{finished['run_id']}.report.json").read_text(encoding="utf-8"))
                self.assertEqual(report["land"]["status"], "merged")
                markdown = (state / f"{finished['run_id']}.report.md").read_text(encoding="utf-8")
                self.assertIn("Land: merged into main", markdown)
                self.assertEqual(_show(repo, "main", "note.txt"), "from-run\n")
                parents = subprocess.run(
                    ["git", "rev-parse", "HEAD^2"], cwd=repo, capture_output=True, text=True, check=False
                )
                self.assertEqual(parents.returncode, 0)

    def test_land_refuses_an_unfinished_run_and_a_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            with tempfile.TemporaryDirectory() as state_name:
                store = RunStore(Path(state_name))
                pending = create_run(
                    store,
                    goal="later",
                    planned=[_planned("Later.", "later")],
                    candidates=[["writer"]],
                    route=ROUTE,
                    concurrency=1,
                )
                with self.assertRaises(HarnessError) as unfinished:
                    land_run(store, pending["run_id"], repo=repo, into="main")
                self.assertEqual(str(unfinished.exception), "run is not finished")

            class Writer:
                def execute(self, request, *, allow_live=False, timeout_seconds=None):
                    del allow_live, timeout_seconds
                    (Path(request.cwd) / "note.txt").write_text("from-run\n", encoding="utf-8")
                    return ProviderResult(provider="writer", argv=("writer",), text="wrote", live=False)

            with tempfile.TemporaryDirectory() as state_name:
                state = Path(state_name)
                store = RunStore(state)
                record = create_run(
                    store,
                    goal="write",
                    planned=[_planned("Write.", "write")],
                    candidates=[["writer"]],
                    route=ROUTE,
                    concurrency=1,
                )
                finished = drive_run(
                    store,
                    record["run_id"],
                    allow_live=False,
                    retries=0,
                    backoff_seconds=0,
                    timeout_seconds={},
                    route_id="route-a",
                    open_adapter=lambda name: Writer(),
                    sleep=lambda seconds: None,
                    max_rounds=0,
                    isolator=GitWorktreeIsolator(repo),
                    base_ref="HEAD",
                )
                (repo / "note.txt").write_text("from-main\n", encoding="utf-8")
                subprocess.run(["git", "add", "note.txt"], cwd=repo, check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", "main note"], cwd=repo, check=True, capture_output=True)
                main_sha = _rev(repo, "main")
                with self.assertRaises(HarnessError) as conflict:
                    land_run(store, finished["run_id"], repo=repo, into="main")
                self.assertEqual(str(conflict.exception), "merge conflict")
                self.assertEqual(_rev(repo, "main"), main_sha)
                self.assertEqual(_show(repo, "main", "note.txt"), "from-main\n")
                stored = store.load(finished["run_id"])
                self.assertEqual(stored["land"]["status"], "conflict")
                self.assertIn("note.txt", stored["land"]["paths"])
                status = subprocess.run(
                    ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, check=True
                )
                self.assertEqual(status.stdout.strip(), "")

    def test_clean_prunes_old_state_and_dry_run_keeps_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            state = root / "state"
            repo.mkdir()
            _git_repo(repo)
            store = RunStore(state)
            old = create_run(
                store,
                goal="old",
                planned=[_planned("Old.", "old")],
                candidates=[["writer"]],
                route=ROUTE,
                concurrency=1,
            )
            recent = create_run(
                store,
                goal="recent",
                planned=[_planned("Recent.", "recent")],
                candidates=[["writer"]],
                route=ROUTE,
                concurrency=1,
            )

            def backdate(current: dict) -> None:
                current["created"] = "2020-01-01T00:00:00Z"
                current["run_branch"] = f"recursion/run/{old['run_id']}"

            store.update(old["run_id"], backdate)
            run_branch = f"recursion/run/{old['run_id']}"
            task_branch = f"recursion/task/{old['run_id']}/task-0"
            subprocess.run(["git", "branch", run_branch], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "branch", task_branch], cwd=repo, check=True, capture_output=True)
            worktree = root / "task-tree"
            subprocess.run(
                ["git", "worktree", "add", "--force", str(worktree), task_branch],
                cwd=repo,
                check=True,
                capture_output=True,
            )
            (state / f"{old['run_id']}.jsonl").write_text("{}\n", encoding="utf-8")
            preview = clean_runs(store, repo=repo, older_than_days=7, dry_run=True, now=_epoch("2026-01-01T00:00:00Z"))
            self.assertEqual([item["run_id"] for item in preview["removed"]], [old["run_id"]])
            self.assertTrue((state / f"{old['run_id']}.json").is_file())
            self.assertTrue(worktree.is_dir())
            cleaned = clean_runs(store, repo=repo, older_than_days=7, dry_run=False, now=_epoch("2026-01-01T00:00:00Z"))
            self.assertEqual([item["run_id"] for item in cleaned["removed"]], [old["run_id"]])
            self.assertIn(task_branch, cleaned["removed"][0]["branches"])
            self.assertFalse((state / f"{old['run_id']}.json").is_file())
            self.assertFalse((state / f"{old['run_id']}.jsonl").is_file())
            self.assertFalse(worktree.exists())
            self.assertNotIn(task_branch, _heads(repo))
            self.assertNotIn(run_branch, _heads(repo))
            self.assertTrue((state / f"{recent['run_id']}.json").is_file())
            stdout = _Buffer()
            with patch("scripts.v3.harness.cli.ROOT", repo), patch("sys.stdout", stdout):
                code = main(["clean", "--state-dir", str(state), "--dry-run", "--older-than", "7"])
            self.assertEqual(code, 0)
            body = json.loads(stdout.getvalue())
            self.assertTrue(body["dry_run"])
            self.assertEqual(body["removed"], [])
            with patch("sys.stderr", _Buffer()):
                with self.assertRaises(SystemExit) as caught:
                    main(["clean", "--older-than", "-1", "--state-dir", str(state)])
            self.assertEqual(caught.exception.code, 2)

            kept = create_run(
                store,
                goal="checked-out",
                planned=[_planned("Stay.", "stay")],
                candidates=[["writer"]],
                route=ROUTE,
                concurrency=1,
            )

            def mark(current: dict) -> None:
                current["created"] = "2020-01-01T00:00:00Z"
                current["run_branch"] = f"recursion/run/{kept['run_id']}"

            store.update(kept["run_id"], mark)
            kept_branch = f"recursion/run/{kept['run_id']}"
            subprocess.run(["git", "branch", kept_branch], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "checkout", kept_branch], cwd=repo, check=True, capture_output=True)
            try:
                skipped = clean_runs(store, repo=repo, older_than_days=0, dry_run=False, now=_epoch("2026-01-01T00:00:00Z"))
                self.assertEqual(skipped["skipped"], [{"reason": "checked out", "run_id": kept["run_id"]}])
                self.assertTrue((state / f"{kept['run_id']}.json").is_file())
                self.assertIn(kept_branch, _heads(repo))
            finally:
                subprocess.run(["git", "checkout", "main"], cwd=repo, check=True, capture_output=True)


def _planned(task: str, task_id: str, depends_on: list[str] | None = None) -> dict:
    return {
        "depends_on": depends_on or [],
        "id": task_id,
        "intent_text": task,
        "packet_id": "PACKET-" + task_id,
        "projection_digest": "digest-" + task_id,
        "required_capabilities": [],
    }


def _git_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "ops-test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "ops-test"], cwd=path, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=path, check=True)
    (path / "README").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "README"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=path, check=True, capture_output=True, text=True)


def _rev(repo: Path, branch: str) -> str:
    return subprocess.check_output(["git", "rev-parse", branch], cwd=repo, text=True).strip()


def _show(repo: Path, branch: str, filename: str) -> str:
    return subprocess.check_output(["git", "show", f"{branch}:{filename}"], cwd=repo, text=True)


def _heads(repo: Path) -> set[str]:
    output = subprocess.check_output(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"], cwd=repo, text=True
    )
    return set(output.split())


def _epoch(text: str) -> float:
    from datetime import datetime, timezone

    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


class _Buffer:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def write(self, text: str) -> int:
        self.parts.append(text)
        return len(text)

    def flush(self) -> None:
        return None

    def getvalue(self) -> str:
        return "".join(self.parts)


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_OPS_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

#!/usr/bin/env python3
"""Recover a landing conflict on a fresh worktree. Fakes only. No live CLIs."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.cli import main  # noqa: E402
from scripts.v3.harness.config import load_config  # noqa: E402
from scripts.v3.harness.errors import HarnessError, RunCancelled  # noqa: E402
from scripts.v3.harness.isolation import GitWorktreeIsolator  # noqa: E402
from scripts.v3.harness.log import JsonLog  # noqa: E402
from scripts.v3.harness.orchestrate import create_run, drive_run, reopen_run  # noqa: E402
from scripts.v3.harness.providers import ProviderResult  # noqa: E402
from scripts.v3.harness.state import RunStore  # noqa: E402


ROUTE = {"fixture_id": "F-M1B-001", "selected_route_id": "route-a", "status": "selected"}
CONFIG = ROOT / "config" / "harness.json"
EXAMPLE = ROOT / "examples" / "harness.json"


class _Stop(BaseException):
    """Stand-in for a process interrupt. Exception is already handled in the worker."""


class RecoveryTests(unittest.TestCase):
    def test_config_accepts_conflict_retries_and_rejects_a_bad_value(self) -> None:
        self.assertEqual(load_config(CONFIG)["landing"]["conflict_retries"], 1)
        self.assertEqual(load_config(EXAMPLE)["landing"]["conflict_retries"], 1)
        with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
            self.assertEqual(main(["config", "validate", "--config", str(EXAMPLE)]), 0)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            negative = root / "negative.json"
            payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
            payload["landing"]["conflict_retries"] = -1
            negative.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(HarnessError) as caught:
                load_config(negative)
            self.assertIn("conflict_retries", str(caught.exception))
            missing = root / "missing.json"
            payload["landing"].pop("conflict_retries")
            missing.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(HarnessError) as caught:
                load_config(missing)
            self.assertIn("conflict_retries", str(caught.exception))
            store = RunStore(root / "state")
            record = create_run(
                store,
                goal="Write the note.",
                planned=[_planned("Write the note.")],
                candidates=[["worker"]],
                route=ROUTE,
                concurrency=1,
            )
            with self.assertRaises(HarnessError) as caught:
                drive_run(
                    store,
                    record["run_id"],
                    allow_live=False,
                    retries=0,
                    backoff_seconds=0,
                    timeout_seconds={},
                    route_id="route-a",
                    open_adapter=lambda name: None,
                    sleep=lambda seconds: None,
                    conflict_retries=True,
                )
            self.assertEqual(str(caught.exception), "landing.conflict_retries must be an integer >= 0")

    def test_parallel_conflict_is_reconciled_and_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            _git_repo(repo)
            head, branch = _head(repo), _branch(repo)
            prompts: list[str] = []
            adapters = _racing(prompts, reconcile="both\n")
            store_dir = Path(directory) / "state"
            progress = StringIO()
            events = StringIO()
            store = RunStore(store_dir)
            record = _create(store)
            log = JsonLog([events], state_dir=store_dir, progress=progress)
            log.bind(run_id=record["run_id"])
            finished = _drive(store, record["run_id"], repo, adapters, log=log, max_rounds=1)
            log.close()
            self.assertEqual(finished["status"], "completed")
            self.assertEqual(finished["conflict_retries"], 1)
            self.assertEqual(_show(repo, finished["run_branch"], "same.txt"), "both\n")
            self.assertEqual(_show(repo, finished["run_branch"], "checked.txt"), "both\n")
            recovered = [task for task in finished["tasks"] if isinstance(task.get("recovery"), dict)]
            self.assertEqual(len(recovered), 1)
            item = recovered[0]
            self.assertFalse(item["recovery"]["active"])
            self.assertEqual(item["status"], "completed")
            self.assertEqual(item["merge_status"], "landed")
            self.assertEqual(len(item["recovery"]["attempts"]), 1)
            attempt = item["recovery"]["attempts"][0]
            self.assertEqual(attempt["status"], "completed")
            self.assertEqual(attempt["merge_status"], "landed")
            self.assertGreaterEqual(len(item["reviews"]), 2)
            self.assertTrue(any(review["verdict"] == "approve" for review in item["reviews"]))
            self.assertIn("-recover-", item["branch"])
            refs = _ref_names(repo)
            self.assertIn(item["branch"], refs)
            self.assertNotIn(f"recursion/task/{finished['run_id']}/task-{item['index']}", refs)
            self.assertTrue(prompts)
            self.assertIn("Conflicting paths:", prompts[0])
            self.assertIn("- same.txt", prompts[0])
            self.assertIn("Reconcile your task on top of it.", prompts[0])
            self.assertIn(item["task"], prompts[0])
            landed = prompts[0].split("Already landed:", 1)[1]
            self.assertNotIn("Summary: none", landed)
            self.assertTrue("Task left:" in landed or "Task right:" in landed)
            names = [row["event"] for row in _parse_jsonl(events.getvalue())]
            self.assertIn("task.conflict_recovery", names)
            self.assertIn("task.conflict_recovered", names)
            self.assertIn(f"task {item['index']} recovering conflict 1", progress.getvalue())
            self.assertIn(f"task {item['index']} conflict recovery 1 completed", progress.getvalue())
            self.assertIn(f"task {item['index']} conflict recovered", progress.getvalue())
            markdown = Path(finished["report"]["markdown"]).read_text(encoding="utf-8")
            self.assertIn("Recovery 1: completed", markdown)
            self.assertIn("provider=", markdown)
            _assert_checkout(self, repo, head, branch)
            self.assertNotIn("recover", _worktrees(repo))
            with patch("sys.stdout", StringIO()) as stdout, patch("sys.stderr", StringIO()):
                code = main(
                    [
                        "logs",
                        finished["run_id"],
                        "--state-dir",
                        str(store_dir),
                    ]
                )
            self.assertEqual(code, 0)
            logged = [row["event"] for row in _parse_jsonl(stdout.getvalue())]
            self.assertIn("task.conflict_recovery", logged)
            self.assertIn("task.conflict_recovered", logged)
            with patch("sys.stdout", StringIO()) as stdout, patch("sys.stderr", StringIO()):
                code = main(
                    [
                        "status",
                        "--run",
                        finished["run_id"],
                        "--state-dir",
                        str(store_dir),
                        "--config",
                        str(CONFIG),
                    ]
                )
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            shown = [task for task in payload["run"]["tasks"] if isinstance(task.get("recovery"), dict)]
            self.assertEqual(shown[0]["recovery"]["attempts"][0]["status"], "completed")

    def test_disabled_recovery_records_the_conflict_and_skips_dependents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            _git_repo(repo)
            head, branch = _head(repo), _branch(repo)
            events = StringIO()
            finished = _drive(
                RunStore(Path(directory) / "state"),
                None,
                repo,
                _racing([], reconcile=None),
                log=JsonLog([events]),
                conflict_retries=0,
            )
            self.assertEqual(finished["status"], "conflict")
            self.assertEqual(finished["conflict_retries"], 0)
            conflicted = [task for task in finished["tasks"] if task["status"] == "conflict"]
            skipped = [task for task in finished["tasks"] if task["id"] == "check"]
            self.assertEqual(len(conflicted), 1)
            self.assertIsNone(conflicted[0]["recovery"])
            self.assertIn("same.txt", conflicted[0]["error"])
            self.assertIn(conflicted[0]["branch"], _ref_names(repo))
            self.assertNotIn("-recover-", conflicted[0]["branch"])
            self.assertEqual(skipped[0]["status"], "skipped")
            names = [row["event"] for row in _parse_jsonl(events.getvalue())]
            self.assertIn("task.conflict", names)
            self.assertNotIn("task.conflict_recovery", names)
            self.assertNotIn("task.conflict_recovered", names)
            markdown = Path(finished["report"]["markdown"]).read_text(encoding="utf-8")
            self.assertIn("Conflict: same.txt", markdown)
            self.assertNotIn("Recovery ", markdown)
            _assert_checkout(self, repo, head, branch)

    def test_exhausted_recovery_keeps_the_conflicted_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            _git_repo(repo)
            head, branch = _head(repo), _branch(repo)
            events = StringIO()
            finished = _drive(
                RunStore(Path(directory) / "state"),
                None,
                repo,
                _racing([], fail="cannot reconcile"),
                log=JsonLog([events]),
                conflict_retries=1,
            )
            self.assertEqual(finished["status"], "conflict")
            conflicted = [task for task in finished["tasks"] if task["status"] == "conflict"]
            self.assertEqual(len(conflicted), 1)
            item = conflicted[0]
            self.assertFalse(item["recovery"]["active"])
            self.assertEqual(len(item["recovery"]["attempts"]), 1)
            self.assertEqual(item["recovery"]["attempts"][0]["status"], "failed")
            self.assertIn("no provider completed the task", item["recovery"]["attempts"][0]["error"])
            self.assertIn("same.txt", item["error"])
            self.assertEqual(item["merge_status"], "conflict")
            refs = _ref_names(repo)
            self.assertIn(item["branch"], refs)
            self.assertNotIn("-recover-", " ".join(refs))
            check = [task for task in finished["tasks"] if task["id"] == "check"][0]
            self.assertEqual(check["status"], "skipped")
            names = [row["event"] for row in _parse_jsonl(events.getvalue())]
            self.assertIn("task.conflict_recovery", names)
            self.assertIn("task.conflict", names)
            self.assertNotIn("task.conflict_recovered", names)
            markdown = Path(finished["report"]["markdown"]).read_text(encoding="utf-8")
            self.assertIn("Recovery 1: failed", markdown)
            self.assertIn("Conflict: same.txt", markdown)
            _assert_checkout(self, repo, head, branch)
            self.assertNotIn("recover", _worktrees(repo))

    def test_resume_continues_an_interrupted_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            _git_repo(repo)
            head, branch = _head(repo), _branch(repo)
            store_dir = Path(directory) / "state"
            store = RunStore(store_dir)
            record = _create(store)
            adapters = _racing([], interrupt=True)
            isolator = GitWorktreeIsolator(repo)
            interrupted = _drive(
                store,
                record["run_id"],
                repo,
                adapters,
                isolator=isolator,
                max_rounds=1,
            )
            conflicted = [task for task in interrupted["tasks"] if task["status"] == "failed"]
            self.assertEqual(len(conflicted), 1)
            item = conflicted[0]
            self.assertEqual(item["error"], "recovery interrupted")
            self.assertTrue(item["recovery"]["active"])
            self.assertEqual(item["merge_status"], "conflict")
            self.assertIn("same.txt", item["merge_conflict"])
            self.assertNotIn("-recover-", item["branch"] or "")
            self.assertIn(item["branch"], _ref_names(repo))
            self.assertEqual([task["status"] for task in interrupted["tasks"] if task["id"] == "check"], ["skipped"])
            reopened = reopen_run(store, record["run_id"])
            self.assertEqual(
                [task["status"] for task in reopened["tasks"] if task["id"] == item["id"]],
                ["pending"],
            )
            self.assertTrue(reopened["tasks"][item["index"]]["recovery"]["active"])
            self.assertEqual(reopened["tasks"][item["index"]]["merge_status"], "conflict")
            with (
                patch("scripts.v3.harness.cli.GitWorktreeIsolator", lambda repo_path: isolator),
                patch("scripts.v3.harness.providers.open_provider", side_effect=adapters.get),
                patch("sys.stdout", StringIO()),
                patch("sys.stderr", StringIO()),
            ):
                code = main(
                    [
                        "resume",
                        "--run",
                        record["run_id"],
                        "--state-dir",
                        str(store_dir),
                        "--config",
                        str(CONFIG),
                    ]
                )
            self.assertEqual(code, 0)
            finished = store.load(record["run_id"])
            self.assertEqual(finished["status"], "completed")
            self.assertEqual(_show(repo, finished["run_branch"], "same.txt"), "both\n")
            self.assertEqual(_show(repo, finished["run_branch"], "checked.txt"), "both\n")
            resumed = finished["tasks"][item["index"]]
            self.assertEqual(resumed["status"], "completed")
            self.assertFalse(resumed["recovery"]["active"])
            self.assertEqual(resumed["recovery"]["attempts"][0]["status"], "completed")
            self.assertIn("-recover-", resumed["branch"])
            refs = _ref_names(repo)
            self.assertIn(resumed["branch"], refs)
            self.assertNotIn(f"recursion/task/{record['run_id']}/task-{item['index']}", refs)
            self.assertTrue(any(review["verdict"] == "approve" for review in resumed["reviews"]))
            _assert_checkout(self, repo, head, branch)

    def test_cancel_stops_a_recovery_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            _git_repo(repo)
            head, branch = _head(repo), _branch(repo)
            store_dir = Path(directory) / "state"
            store = RunStore(store_dir)
            record = _create(store)
            started = threading.Event()
            saw_stop = threading.Event()
            adapters = _racing([], cancel_at=(started, saw_stop))
            box: dict = {}

            def runner() -> None:
                try:
                    box["finished"] = _drive(store, record["run_id"], repo, adapters, conflict_retries=1)
                except BaseException as exc:  # noqa: BLE001 - the assertion reports it
                    box["error"] = exc

            thread = threading.Thread(target=runner)
            thread.start()
            self.assertTrue(started.wait(20), "recovery provider did not start")
            with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
                code = main(
                    [
                        "cancel",
                        "--run",
                        record["run_id"],
                        "--state-dir",
                        str(store_dir),
                        "--config",
                        str(CONFIG),
                    ]
                )
            self.assertEqual(code, 0)
            thread.join(30)
            self.assertFalse(thread.is_alive())
            self.assertNotIn("error", box)
            finished = box["finished"]
            self.assertEqual(finished["status"], "cancelled")
            self.assertTrue(saw_stop.is_set())
            cancelled = [task for task in finished["tasks"] if task["id"] in {"left", "right"} and task["status"] == "cancelled"]
            self.assertEqual(len(cancelled), 1)
            item = cancelled[0]
            self.assertEqual(item["error"], "run cancelled")
            self.assertFalse(item["recovery"]["active"])
            self.assertIn(item["branch"], _ref_names(repo))
            self.assertNotIn("-recover-", item["branch"] or "")
            self.assertNotIn("-recover-", " ".join(_ref_names(repo)))
            check = [task for task in finished["tasks"] if task["id"] == "check"][0]
            self.assertIn(check["status"], {"cancelled", "skipped"})
            _assert_checkout(self, repo, head, branch)
            self.assertNotIn("recover", _worktrees(repo))


def _racing(
    prompts: list[str],
    *,
    reconcile: str | None = "both\n",
    fail: str | None = None,
    interrupt: bool = False,
    cancel_at: tuple[threading.Event, threading.Event] | None = None,
) -> dict:
    barrier = threading.Barrier(2)
    state = {"interrupted": False}

    class Reviewer:
        def execute(self, request, *, allow_live=False, timeout_seconds=None, should_stop=None):
            del allow_live, timeout_seconds, should_stop
            if request.kind != "review":
                raise HarnessError("reviewer does not execute")
            return ProviderResult(provider="reviewer", argv=("reviewer",), text="VERDICT approve", live=False)

    def racer(name: str, body: str):
        class Racing:
            def execute(self, request, *, allow_live=False, timeout_seconds=None, should_stop=None):
                del allow_live, timeout_seconds
                text = request.task or ""
                if "Conflicting paths:" in text:
                    prompts.append(text)
                    if cancel_at is not None:
                        started, saw_stop = cancel_at
                        started.set()
                        deadline = time.monotonic() + 20
                        while not (should_stop is not None and should_stop()):
                            if time.monotonic() > deadline:
                                raise HarnessError("cancel was not observed")
                            time.sleep(0.02)
                        saw_stop.set()
                        raise RunCancelled("run cancelled")
                    if interrupt and not state["interrupted"]:
                        state["interrupted"] = True
                        raise _Stop()
                    if fail:
                        raise HarnessError(fail)
                    (Path(request.cwd) / "same.txt").write_text(reconcile or "both\n", encoding="utf-8")
                    return ProviderResult(provider=name, argv=(name,), text="reconciled", live=False)
                barrier.wait(timeout=20)
                (Path(request.cwd) / "same.txt").write_text(body, encoding="utf-8")
                return ProviderResult(provider=name, argv=(name,), text="wrote", live=False)

        return Racing()

    class Check:
        def execute(self, request, *, allow_live=False, timeout_seconds=None, should_stop=None):
            del allow_live, timeout_seconds, should_stop
            body = (Path(request.cwd) / "same.txt").read_text(encoding="utf-8")
            if body != "both\n":
                raise HarnessError("landed file was not reconciled")
            (Path(request.cwd) / "checked.txt").write_text(body, encoding="utf-8")
            return ProviderResult(provider="check", argv=("check",), text="checked", live=False)

    return {
        "left": racer("left", "left\n"),
        "right": racer("right", "right\n"),
        "check": Check(),
        "reviewer": Reviewer(),
    }


def _create(store: RunStore) -> dict:
    planned = [
        _planned("Write the left note.", "left"),
        _planned("Write the right note.", "right"),
        _planned("Check the reconciled note.", "check", ["left", "right"]),
    ]
    return create_run(
        store,
        goal="Write the left note.\nWrite the right note.\nCheck the reconciled note.",
        planned=planned,
        candidates=[["left", "reviewer"], ["right", "reviewer"], ["check", "reviewer"]],
        route=ROUTE,
        concurrency=2,
    )


def _drive(
    store: RunStore,
    run_id: str | None,
    repo: Path,
    adapters: dict,
    *,
    log=None,
    max_rounds: int = 0,
    conflict_retries: int = 1,
    isolator: GitWorktreeIsolator | None = None,
) -> dict:
    if run_id is None:
        record = _create(store)
        run_id = record["run_id"]
    return drive_run(
        store,
        run_id,
        allow_live=False,
        retries=0,
        backoff_seconds=0,
        timeout_seconds={},
        route_id="route-a",
        log=log,
        open_adapter=adapters.get,
        sleep=lambda seconds: None,
        max_rounds=max_rounds,
        isolator=isolator or GitWorktreeIsolator(repo),
        conflict_retries=conflict_retries,
    )


def _planned(task: str, task_id: str | None = None, depends_on: list[str] | None = None) -> dict:
    label = task_id or task
    return {
        "depends_on": depends_on or [],
        "id": label,
        "intent_text": task,
        "packet_id": "PACKET-" + label,
        "projection_digest": "digest-" + label,
        "required_capabilities": [],
    }


def _git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "recovery-test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "recovery-test"], cwd=path, check=True)
    (path / "README").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "README"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=path, check=True, capture_output=True, text=True)


def _head(repo: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


def _branch(repo: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo, text=True).strip()


def _show(repo: Path, branch: str, filename: str) -> str:
    return subprocess.check_output(["git", "show", f"{branch}:{filename}"], cwd=repo, text=True)


def _ref_names(repo: Path) -> list[str]:
    listed = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/recursion"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in listed.stdout.splitlines() if line]


def _worktrees(repo: Path) -> str:
    return subprocess.check_output(["git", "worktree", "list", "--porcelain"], cwd=repo, text=True)


def _parse_jsonl(text: str) -> list[dict]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _assert_checkout(case: unittest.TestCase, repo: Path, head: str, branch: str) -> None:
    case.assertEqual(_head(repo), head)
    case.assertEqual(_branch(repo), branch)
    case.assertNotIn("recursion/", branch)
    case.assertEqual((repo / "README").read_text(encoding="utf-8"), "base\n")
    case.assertFalse((repo / "same.txt").exists())
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True)
    case.assertEqual(status, "")


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_RECOVERY_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

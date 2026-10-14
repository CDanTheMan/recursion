#!/usr/bin/env python3
"""Land accepted work, plan a task graph, and harden review. Fakes only."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.cli import _assign_candidates  # noqa: E402
from scripts.v3.harness.config import load_config  # noqa: E402
from scripts.v3.harness.dag import admit_goal, parse_plan, plan_prompt  # noqa: E402
from scripts.v3.harness.errors import HarnessError  # noqa: E402
from scripts.v3.harness.isolation import GitWorktreeIsolator  # noqa: E402
from scripts.v3.harness.log import JsonLog  # noqa: E402
from scripts.v3.harness.orchestrate import create_run, drive_run, plan_goal, reopen_run  # noqa: E402
from scripts.v3.harness.providers import FixtureProvider, ProviderRequest, ProviderResult  # noqa: E402
from scripts.v3.harness.state import RunStore  # noqa: E402


ROUTE = {"fixture_id": "F-M1B-001", "selected_route_id": "route-a", "status": "selected"}


class LandingTests(unittest.TestCase):
    def test_plan_validation_rejects_bad_graphs_without_echoing_input(self) -> None:
        nodes = parse_plan(
            json.dumps(
                {
                    "tasks": [
                        {
                            "depends_on": [],
                            "description": "Build the note.",
                            "id": "build",
                            "required_capabilities": ["execute"],
                        },
                        {
                            "depends_on": ["build"],
                            "description": "Test the note.",
                            "id": "test",
                            "required_capabilities": [],
                        },
                    ]
                }
            )
        )
        self.assertEqual([node["id"] for node in nodes], ["build", "test"])
        for text, message in (
            ("SECRET not json", "planner returned invalid JSON"),
            (json.dumps({"tasks": [], "extra": 1}), "planner JSON keys are not exactly tasks"),
            (
                json.dumps(
                    {
                        "tasks": [
                            _node("a"),
                            _node("a"),
                        ]
                    }
                ),
                "planner task id is duplicated",
            ),
            (
                json.dumps({"tasks": [_node("a", depends_on=["missing"])]}),
                "planner dependency is unknown",
            ),
            (
                json.dumps(
                    {
                        "tasks": [
                            _node("a", depends_on=["b"]),
                            _node("b", depends_on=["a"]),
                        ]
                    }
                ),
                "planner tasks have a cycle",
            ),
        ):
            with self.assertRaises(HarnessError) as caught:
                parse_plan(text)
            self.assertEqual(str(caught.exception), message)
            self.assertNotIn("SECRET", str(caught.exception))

    def test_invalid_planner_output_falls_back_to_lines(self) -> None:
        sink = StringIO()

        class Garbage:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del request, allow_live, timeout_seconds
                return ProviderResult(provider="garbage", argv=("garbage",), text="SECRET-PLAN", live=False)

        planned = admit_goal(
            "Alpha task.\nBeta task.",
            candidates=["garbage"],
            allow_live=False,
            retries=0,
            backoff_seconds=0,
            timeout_seconds={},
            log=JsonLog([sink]),
            open_adapter=lambda name: Garbage(),
        )
        self.assertEqual(planned["source"], "lines")
        self.assertEqual(planned["fallback"], "planner returned invalid JSON")
        self.assertEqual([task["intent_text"] for task in planned["tasks"]], ["Alpha task.", "Beta task."])
        self.assertEqual([task["id"] for task in planned["tasks"]], ["task-1", "task-2"])
        self.assertNotIn("SECRET", sink.getvalue())
        request = ProviderRequest(task=plan_prompt("Alpha task.\nBeta task."), packet_id="PLAN", route_id="plan", kind="plan")
        fixture = parse_plan(FixtureProvider().execute(request).text)
        self.assertEqual([node["description"] for node in fixture], ["Alpha task.", "Beta task."])

    def test_dependency_waits_and_resume_retries_the_failed_task(self) -> None:
        calls: list[str] = []

        class Flaky:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del allow_live, timeout_seconds
                calls.append(request.task)
                if request.task.startswith("Build") and calls.count(request.task) == 1:
                    raise HarnessError("not yet")
                return ProviderResult(provider="flaky", argv=("flaky",), text="ok", live=False)

        planned = plan_goal(
            "Build the note.\nTest the note.",
            nodes=[
                _node("build", description="Build the note."),
                _node("test", description="Test the note.", depends_on=["build"]),
            ],
            source="provider",
        )
        with tempfile.TemporaryDirectory() as directory:
            store = RunStore(Path(directory))
            record = create_run(
                store,
                goal=planned["goal"],
                planned=planned["tasks"],
                candidates=[["flaky"], ["flaky"]],
                route=ROUTE,
                concurrency=2,
                plan_source="provider",
            )
            failed = _drive(store, record["run_id"], Flaky())
            self.assertEqual(failed["status"], "failed")
            self.assertEqual([task["status"] for task in failed["tasks"]], ["failed", "skipped"])
            self.assertEqual(failed["tasks"][1]["error"], "dependency build is failed")
            self.assertEqual(calls, ["Build the note."])
            reopen_run(store, record["run_id"])
            resumed = _drive(store, record["run_id"], Flaky())
        self.assertEqual(resumed["status"], "completed")
        self.assertEqual([task["status"] for task in resumed["tasks"]], ["completed", "completed"])
        self.assertEqual(
            [call.split("\n", 1)[0] for call in calls],
            ["Build the note.", "Build the note.", "Test the note."],
        )
        self.assertIn("Dependency context:", calls[2])
        self.assertEqual(resumed["tasks"][1]["depends_on"], ["build"])

    def test_unreviewed_dependency_skips_later_tasks(self) -> None:
        class Boom:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del allow_live, timeout_seconds
                if request.kind == "review":
                    raise HarnessError("reviewer down")
                return ProviderResult(provider=request.kind, argv=(request.kind,), text="draft", live=False)

        planned = plan_goal(
            "Build the note.\nTest the note.",
            nodes=[
                _node("build", description="Build the note."),
                _node("test", description="Test the note.", depends_on=["build"]),
            ],
            source="provider",
        )
        with tempfile.TemporaryDirectory() as directory:
            store = RunStore(Path(directory))
            record = create_run(
                store,
                goal=planned["goal"],
                planned=planned["tasks"],
                candidates=[["author", "reviewer"], ["author", "reviewer"]],
                route=ROUTE,
                concurrency=2,
                plan_source="provider",
            )
            finished = _drive(store, record["run_id"], Boom(), max_rounds=1)
        self.assertEqual([task["status"] for task in finished["tasks"]], ["unreviewed", "skipped"])
        self.assertEqual(finished["tasks"][1]["error"], "dependency build is unreviewed")
        self.assertEqual(finished["status"], "unreviewed")

    def test_required_capabilities_filter_candidates(self) -> None:
        config = load_config()
        assigned = _assign_candidates(
            ["fixture", "claude", "codex", "grok"],
            [{"required_capabilities": ["subscription"]}, {"required_capabilities": ["not-a-real-capability"]}],
            config,
        )
        self.assertEqual(assigned[0], ["claude", "codex", "grok"])
        self.assertEqual(assigned[1], [])
        with tempfile.TemporaryDirectory() as directory:
            store = RunStore(Path(directory))
            planned = plan_goal(
                "Build the note.\nTest the note.",
                nodes=[
                    _node("build", description="Build the note."),
                    _node("test", description="Test the note.", depends_on=["build"]),
                ],
            )
            record = create_run(
                store,
                goal=planned["goal"],
                planned=planned["tasks"],
                candidates=[[], ["fixture"]],
                route=ROUTE,
                concurrency=1,
            )
            finished = _drive(store, record["run_id"], FixtureProvider())
        self.assertEqual(finished["tasks"][0]["status"], "failed")
        self.assertEqual(finished["tasks"][0]["error"], "no provider has the required capabilities")
        self.assertEqual(finished["tasks"][1]["status"], "skipped")
        self.assertEqual(finished["tasks"][1]["error"], "dependency build is failed")

    def test_missing_review_is_unreviewed_and_records_attempts(self) -> None:
        class Boom:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del allow_live, timeout_seconds
                if request.kind == "review":
                    raise HarnessError("SECRET reviewer down")
                return ProviderResult(provider="author", argv=("author",), text="draft", live=False)

        with tempfile.TemporaryDirectory() as directory:
            store = RunStore(Path(directory))
            record = create_run(
                store,
                goal="Write the note.",
                planned=[_planned("Write the note.")],
                candidates=[["author", "reviewer"]],
                route=ROUTE,
                concurrency=1,
            )
            finished = _drive(store, record["run_id"], Boom(), max_rounds=1, accept_unreviewed=False)
        stored = json.dumps(finished)
        self.assertEqual(finished["status"], "unreviewed")
        self.assertEqual(finished["tasks"][0]["reviews"][0]["verdict"], "skipped")
        self.assertTrue(finished["tasks"][0]["reviews"][0]["attempts"])
        self.assertNotIn("SECRET", stored)
        accepted = _drive_fresh(Boom(), max_rounds=1, accept_unreviewed=True)
        self.assertEqual(accepted["status"], "completed")

    def test_accepted_edits_are_committed_and_merged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            isolator = GitWorktreeIsolator(repo)
            finished = _drive_repo(
                repo,
                isolator,
                {"left": _Writer("left", "a.txt", "alpha\n"), "right": _Writer("right", "b.txt", "beta\n")},
                ["left", "right"],
                concurrency=2,
            )
            run_branch = finished["run_branch"]
            self.assertEqual(finished["status"], "completed")
            self.assertEqual(_show(repo, run_branch, "a.txt"), "alpha\n")
            self.assertEqual(_show(repo, run_branch, "b.txt"), "beta\n")
            for task in finished["tasks"]:
                self.assertEqual(task["merge_status"], "landed")
                self.assertIsNotNone(task["commit"])
                self.assertIn("recursion: land", _log(repo, task["branch"]))
                self.assertFalse(task["branch"] is None)
            self.assertEqual(_refs(repo, "refs/heads/recursion/task"), 2)
            self.assertEqual(finished["report_body"]["run_branch"], run_branch)
            self.assertEqual(finished["report_body"]["tasks"][0]["commit"], finished["tasks"][0]["commit"])
            self.assertEqual(finished["report_body"]["tasks"][0]["branch"], finished["tasks"][0]["branch"])
            followed = _drive_follow(repo, isolator)
            self.assertEqual(followed["status"], "completed")
            self.assertEqual(_show(repo, followed["run_branch"], "c.txt"), "alpha\n")

    def test_provider_commit_is_kept_and_conflicts_are_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)

            class Committer:
                def execute(self, request, *, allow_live=False, timeout_seconds=None):
                    del allow_live, timeout_seconds
                    path = Path(request.cwd) / "note.txt"
                    path.write_text("from provider\n", encoding="utf-8")
                    subprocess.run(["git", "add", "note.txt"], cwd=request.cwd, check=True)
                    subprocess.run(
                        ["git", "-c", "user.email=p@example.com", "-c", "user.name=provider", "commit", "-m", "provider commit"],
                        cwd=request.cwd,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    return ProviderResult(provider="committer", argv=("committer",), text="committed", live=False)

            finished = _drive_repo(repo, GitWorktreeIsolator(repo), {"committer": Committer()}, ["committer"])
            self.assertEqual(finished["status"], "completed")
            self.assertEqual(_log(repo, finished["tasks"][0]["branch"]).strip(), "provider commit")
            self.assertEqual(_show(repo, finished["run_branch"], "note.txt"), "from provider\n")

        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            barrier = threading.Barrier(2)

            def racing(name: str, body: str):
                class Racing:
                    def execute(self, request, *, allow_live=False, timeout_seconds=None):
                        del allow_live, timeout_seconds
                        barrier.wait(timeout=10)
                        (Path(request.cwd) / "same.txt").write_text(body, encoding="utf-8")
                        return ProviderResult(provider=name, argv=(name,), text="wrote", live=False)

                return Racing()

            finished = _drive_repo(
                repo,
                GitWorktreeIsolator(repo),
                {"left": racing("left", "left\n"), "right": racing("right", "right\n")},
                ["left", "right"],
                concurrency=2,
                conflict_retries=0,
            )
            landed = [task for task in finished["tasks"] if task["status"] == "completed"]
            conflicted = [task for task in finished["tasks"] if task["status"] == "conflict"]
            self.assertEqual(finished["status"], "conflict")
            self.assertEqual(len(landed), 1)
            self.assertEqual(len(conflicted), 1)
            self.assertEqual(landed[0]["merge_status"], "landed")
            self.assertEqual(conflicted[0]["merge_status"], "conflict")
            self.assertIn("same.txt", conflicted[0]["error"])
            self.assertIn(_show(repo, finished["run_branch"], "same.txt"), {"left\n", "right\n"})
            self.assertIn(conflicted[0]["branch"], _ref_names(repo))
            self.assertIn("Conflict: same.txt", finished["report_markdown"])

    def test_failed_branch_is_removed_unless_kept(self) -> None:
        class Boom:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del request, allow_live, timeout_seconds
                raise HarnessError("boom")

        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            finished = _drive_repo(repo, GitWorktreeIsolator(repo), {"boom": Boom()}, ["boom"])
            self.assertEqual(finished["status"], "failed")
            self.assertEqual(_refs(repo, "refs/heads/recursion/task"), 0)
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            finished = _drive_repo(
                repo,
                GitWorktreeIsolator(repo),
                {"boom": Boom()},
                ["boom"],
                keep_worktrees=True,
            )
            self.assertEqual(_refs(repo, "refs/heads/recursion/task"), 1)
            self.assertTrue(finished["tasks"][0]["branch"])

    def test_reviewer_writes_are_reverted(self) -> None:
        class Author:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del allow_live, timeout_seconds
                if request.kind == "review":
                    raise HarnessError("author must not review")
                (Path(request.cwd) / "author.txt").write_text("kept\n", encoding="utf-8")
                return ProviderResult(provider="author", argv=("author",), text="draft", live=False)

        class Reviewer:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del allow_live, timeout_seconds
                (Path(request.cwd) / "evil.txt").write_text("SECRET-WRITE\n", encoding="utf-8")
                (Path(request.cwd) / "author.txt").write_text("tampered\n", encoding="utf-8")
                return ProviderResult(provider="reviewer", argv=("reviewer",), text="VERDICT approve\nship it", live=False)

        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            finished = _drive_repo(
                repo,
                GitWorktreeIsolator(repo),
                {"author": Author(), "reviewer": Reviewer()},
                [],
                groups=[["author", "reviewer"]],
                max_rounds=1,
                keep_worktrees=True,
            )
            task = finished["tasks"][0]
            self.assertEqual(finished["status"], "review-rejected")
            self.assertEqual(task["reviews"][0]["verdict"], "rejected-write")
            self.assertEqual(task["reviews"][0]["notes"], "reviewer modified the worktree")
            self.assertNotIn("ship it", json.dumps(task["reviews"]))
            self.assertNotIn("SECRET", json.dumps(task))
            self.assertEqual(_show(repo, task["branch"], "author.txt"), "kept\n")
            missing = subprocess.run(
                ["git", "cat-file", "-e", f"{task['branch']}:evil.txt"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(missing.returncode, 0)

        class CrashingReviewer:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del allow_live, timeout_seconds
                if request.kind == "review":
                    (Path(request.cwd) / "evil.txt").write_text("SECRET-WRITE\n", encoding="utf-8")
                    raise HarnessError("review crashed")
                (Path(request.cwd) / "author.txt").write_text("kept\n", encoding="utf-8")
                return ProviderResult(provider="author", argv=("author",), text="draft", live=False)

        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            finished = _drive_repo(
                repo,
                GitWorktreeIsolator(repo),
                {"author": Author(), "reviewer": CrashingReviewer()},
                [],
                groups=[["author", "reviewer"]],
                max_rounds=1,
            )
            task = finished["tasks"][0]
            self.assertEqual(finished["status"], "unreviewed")
            self.assertEqual(task["reviews"][0]["verdict"], "skipped")
            self.assertIn("reviewer modified the worktree", task["reviews"][0]["notes"])
            self.assertTrue(task["reviews"][0]["attempts"])
            self.assertNotIn("SECRET", json.dumps(task))
            self.assertEqual(_show(repo, task["branch"], "author.txt"), "kept\n")
            missing = subprocess.run(
                ["git", "cat-file", "-e", f"{task['branch']}:evil.txt"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(missing.returncode, 0)


def _drive(store: RunStore, run_id: str, adapter, *, max_rounds: int = 0, accept_unreviewed: bool = False) -> dict:
    return drive_run(
        store,
        run_id,
        allow_live=False,
        retries=0,
        backoff_seconds=0,
        timeout_seconds={},
        route_id="route-a",
        open_adapter=lambda name: adapter,
        sleep=lambda seconds: None,
        max_rounds=max_rounds,
        accept_unreviewed=accept_unreviewed,
    )


def _drive_fresh(adapter, *, max_rounds: int, accept_unreviewed: bool) -> dict:
    with tempfile.TemporaryDirectory() as directory:
        store = RunStore(Path(directory))
        record = create_run(
            store,
            goal="Write the note.",
            planned=[_planned("Write the note.")],
            candidates=[["author", "reviewer"]],
            route=ROUTE,
            concurrency=1,
        )
        return _drive(store, record["run_id"], adapter, max_rounds=max_rounds, accept_unreviewed=accept_unreviewed)


def _drive_repo(
    repo: Path,
    isolator: GitWorktreeIsolator,
    adapters: dict,
    names: list[str],
    *,
    concurrency: int = 1,
    max_rounds: int = 0,
    keep_worktrees: bool = False,
    groups: list[list[str]] | None = None,
    conflict_retries: int = 1,
) -> dict:
    chosen = groups if groups is not None else [[name] for name in names]
    tasks = [f"Write file {index}." for index in range(len(chosen))]
    with tempfile.TemporaryDirectory() as directory:
        store = RunStore(Path(directory))
        record = create_run(
            store,
            goal="\n".join(tasks),
            planned=[_planned(task) for task in tasks],
            candidates=chosen,
            route=ROUTE,
            concurrency=concurrency,
        )
        finished = drive_run(
            store,
            record["run_id"],
            allow_live=False,
            retries=0,
            backoff_seconds=0,
            timeout_seconds={},
            route_id="route-a",
            open_adapter=adapters.get,
            sleep=lambda seconds: None,
            max_rounds=max_rounds,
            isolator=isolator,
            keep_worktrees=keep_worktrees,
            conflict_retries=conflict_retries,
        )
        finished["report_body"] = json.loads(Path(finished["report"]["json"]).read_text(encoding="utf-8"))
        finished["report_markdown"] = Path(finished["report"]["markdown"]).read_text(encoding="utf-8")
        return finished


def _drive_follow(repo: Path, isolator: GitWorktreeIsolator) -> dict:
    """Run a second task that reads a file landed by an earlier task on this repo."""

    class First:
        def execute(self, request, *, allow_live=False, timeout_seconds=None):
            del allow_live, timeout_seconds
            (Path(request.cwd) / "a.txt").write_text("alpha\n", encoding="utf-8")
            return ProviderResult(provider="first", argv=("first",), text="wrote", live=False)

    class Second:
        def execute(self, request, *, allow_live=False, timeout_seconds=None):
            del allow_live, timeout_seconds
            text = (Path(request.cwd) / "a.txt").read_text(encoding="utf-8")
            if text != "alpha\n":
                raise HarnessError("landed file missing")
            (Path(request.cwd) / "c.txt").write_text(text, encoding="utf-8")
            return ProviderResult(provider="second", argv=("second",), text="copied", live=False)

    with tempfile.TemporaryDirectory() as directory:
        store = RunStore(Path(directory))
        planned = [
            _planned("Write a.", task_id="build"),
            _planned("Copy a.", task_id="follow", depends_on=["build"]),
        ]
        record = create_run(
            store,
            goal="Write a.\nCopy a.",
            planned=planned,
            candidates=[["first"], ["second"]],
            route=ROUTE,
            concurrency=2,
            plan_source="provider",
        )
        finished = drive_run(
            store,
            record["run_id"],
            allow_live=False,
            retries=0,
            backoff_seconds=0,
            timeout_seconds={},
            route_id="route-a",
            open_adapter={"first": First(), "second": Second()}.get,
            sleep=lambda seconds: None,
            isolator=isolator,
        )
        finished["report_body"] = json.loads(Path(finished["report"]["json"]).read_text(encoding="utf-8"))
        return finished


def _planned(task: str, task_id: str | None = None, depends_on: list[str] | None = None) -> dict:
    return {
        "depends_on": depends_on or [],
        "id": task_id or "task-" + task,
        "intent_text": task,
        "packet_id": "PACKET-" + task,
        "projection_digest": "digest-" + task,
        "required_capabilities": [],
    }


def _node(task_id: str, *, description: str = "Do the work.", depends_on: list[str] | None = None) -> dict:
    return {
        "depends_on": depends_on or [],
        "description": description,
        "id": task_id,
        "required_capabilities": [],
    }


class _Writer:
    def __init__(self, name: str, filename: str, body: str) -> None:
        self.name = name
        self.filename = filename
        self.body = body

    def execute(self, request, *, allow_live=False, timeout_seconds=None):
        del allow_live, timeout_seconds
        (Path(request.cwd) / self.filename).write_text(self.body, encoding="utf-8")
        return ProviderResult(provider=self.name, argv=(self.name,), text="wrote", live=False)


def _git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "landing-test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "landing-test"], cwd=path, check=True)
    (path / "README").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "README"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=path, check=True, capture_output=True, text=True)


def _show(repo: Path, branch: str, filename: str) -> str:
    return subprocess.check_output(["git", "show", f"{branch}:{filename}"], cwd=repo, text=True)


def _log(repo: Path, branch: str) -> str:
    return subprocess.check_output(["git", "log", "--format=%s", "HEAD.." + branch], cwd=repo, text=True)


def _refs(repo: Path, prefix: str) -> int:
    return len(_ref_names(repo, prefix))


def _ref_names(repo: Path, prefix: str = "refs/heads/recursion") -> list[str]:
    listed = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname:short)", prefix],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in listed.stdout.splitlines() if line]


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_LANDING_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

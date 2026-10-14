#!/usr/bin/env python3
"""Worktree isolation, cross-provider review, reports, and budgets. Fakes only."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.config import load_config  # noqa: E402
from scripts.v3.harness.errors import HarnessError  # noqa: E402
from scripts.v3.harness.isolation import GitWorktreeIsolator, TaskIsolation  # noqa: E402
from scripts.v3.harness.orchestrate import create_run, drive_run  # noqa: E402
from scripts.v3.harness.providers import FixtureProvider, ProviderRequest, ProviderResult  # noqa: E402
from scripts.v3.harness.report import render_markdown  # noqa: E402
from scripts.v3.harness.review import parse_verdict  # noqa: E402
from scripts.v3.harness.state import RunStore  # noqa: E402
from scripts.v3.harness.usage import add_usage, empty_usage, exceeded, parse_usage  # noqa: E402


ROUTE = {"fixture_id": "F-M1B-001", "selected_route_id": "route-a", "status": "selected"}
RUN_ID = "RUN-aaaaaaaaaaaaaaaa"


class Author:
    def __init__(self) -> None:
        self.tasks: list[str] = []

    def execute(self, request, *, allow_live=False, timeout_seconds=None):
        del allow_live, timeout_seconds
        self.tasks.append(request.task)
        return ProviderResult(provider="author", argv=("author",), text="draft", live=False)


class Reviewer:
    def __init__(self, texts: list[str]) -> None:
        self.texts = list(texts)
        self.kinds: list[str] = []

    def execute(self, request, *, allow_live=False, timeout_seconds=None):
        del allow_live, timeout_seconds
        self.kinds.append(request.kind)
        text = self.texts.pop(0)
        return ProviderResult(provider="reviewer", argv=("reviewer",), text=text, live=False)


class UsageProvider:
    def execute(self, request, *, allow_live=False, timeout_seconds=None):
        del allow_live, timeout_seconds
        text = '{"usage": {"input_tokens": 10, "output_tokens": 1}}\n' + request.task
        return ProviderResult(provider="usage", argv=("usage",), text=text, live=False)


class ReviewTests(unittest.TestCase):
    def test_usage_reads_provider_streams_and_leaves_gaps_unknown(self) -> None:
        claude = "\n".join(
            (
                "hello",
                '{"type":"result","usage":{"input_tokens":1,"output_tokens":1},"total_cost_usd":0.1,"secret":"SECRET"}',
                '{"type":"result","usage":{"input_tokens":12,"output_tokens":3},"total_cost_usd":0.01}',
            )
        )
        parsed = parse_usage(claude)
        self.assertEqual(parsed, {"cost": 0.01, "input_tokens": 12, "output_tokens": 3})
        self.assertNotIn("SECRET", json.dumps(parsed))

        codex = '{"type":"turn.completed","usage":{"input_tokens":4,"output_tokens":2}}'
        self.assertEqual(parse_usage(codex)["input_tokens"], 4)
        self.assertIsNone(parse_usage(codex)["cost"])

        grok = '{"usage":{"prompt_tokens":8,"completion_tokens":5,"cost":0.02}}'
        self.assertEqual(parse_usage(grok), {"cost": 0.02, "input_tokens": 8, "output_tokens": 5})

        blank = parse_usage("provider=fixture\nno usage object")
        self.assertEqual(blank, empty_usage())
        total = empty_usage()
        add_usage(total, blank)
        self.assertEqual(total, empty_usage())
        self.assertFalse(exceeded(total, {"max_cost": 0, "max_input_tokens": 0, "max_output_tokens": 0}))
        self.assertFalse(
            exceeded(
                {"cost": None, "input_tokens": 5, "output_tokens": None},
                {"max_cost": 0, "max_input_tokens": 5, "max_output_tokens": 0},
            )
        )
        self.assertTrue(
            exceeded(
                {"cost": None, "input_tokens": 6, "output_tokens": None},
                {"max_cost": None, "max_input_tokens": 5, "max_output_tokens": None},
            )
        )
        self.assertIsNone(parse_usage('{"usage":{"input_tokens":true,"output_tokens":false}}')["input_tokens"])

    def test_config_exposes_review_rounds_and_budgets(self) -> None:
        config = load_config()
        self.assertEqual(config["review"]["max_rounds"], 2)
        self.assertFalse(config["review"]["accept_unreviewed"])
        self.assertEqual(config["landing"]["base_ref"], "HEAD")
        self.assertEqual(config["budgets"]["max_input_tokens"], 1_000_000)
        self.assertIsNone(config["budgets"]["max_cost"])
        raw = json.loads((ROOT / "config" / "harness.json").read_text(encoding="utf-8"))
        raw["budgets"]["max_cost"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "harness.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaises(HarnessError):
                load_config(path)

    def test_fixture_review_approves_without_a_process(self) -> None:
        request = ProviderRequest(task="review me", packet_id="PACKET-1", route_id="route-a", kind="review")
        with patch("scripts.v3.harness.providers.run_command") as spawned:
            result = FixtureProvider().execute(request)
        spawned.assert_not_called()
        self.assertTrue(result.text.startswith("VERDICT approve"))
        self.assertFalse(result.live)

    def test_review_loop_sends_notes_back_then_approves(self) -> None:
        author = Author()
        reviewer = Reviewer(["VERDICT revise\nadd a test", "VERDICT approve\nlooks good"])
        isolator = _DiffIsolator("diff --git a/note.txt b/note.txt")
        with tempfile.TemporaryDirectory() as directory:
            finished = _drive(
                directory,
                ["author", "reviewer"],
                {"author": author, "reviewer": reviewer},
                max_rounds=2,
                isolator=isolator,
            )
            report = json.loads(Path(finished["report"]["json"]).read_text(encoding="utf-8"))
            markdown = Path(finished["report"]["markdown"]).read_text(encoding="utf-8")
        task = finished["tasks"][0]
        self.assertEqual(finished["status"], "completed")
        self.assertEqual(task["provider"], "author")
        self.assertEqual(task["reviews"][0]["verdict"], "revise")
        self.assertEqual(task["reviews"][1]["verdict"], "approve")
        self.assertEqual(task["reviews"][0]["reviewer"], "reviewer")
        self.assertNotEqual(task["provider"], task["reviews"][0]["reviewer"])
        self.assertEqual(len(author.tasks), 2)
        self.assertIn("Review notes:", author.tasks[1])
        self.assertIn("add a test", author.tasks[1])
        self.assertEqual(reviewer.kinds, ["review", "review"])
        self.assertIn("diff --git a/note.txt", task["diff"])
        self.assertTrue(isolator.released)
        self.assertEqual(report["tasks"][0]["provider"], "author")
        self.assertEqual([item["verdict"] for item in report["tasks"][0]["reviews"]], ["revise", "approve"])
        self.assertGreaterEqual(len(report["tasks"][0]["attempts"]), 4)
        self.assertIn("note.txt", report["tasks"][0]["diff"])
        self.assertIn("author", markdown)
        self.assertIn("approve", markdown)
        self.assertIn("Attempts:", markdown)
        self.assertIn("Duration:", markdown)
        self.assertRegex(render_markdown(report), r"Duration: \d+\.\d{3}s")

    def test_review_stops_after_the_configured_rounds(self) -> None:
        author = Author()
        reviewer = Reviewer(["VERDICT revise\nstill wrong", "VERDICT revise\nstill wrong"])
        with tempfile.TemporaryDirectory() as directory:
            finished = _drive(
                directory,
                ["author", "reviewer"],
                {"author": author, "reviewer": reviewer},
                max_rounds=2,
            )
        task = finished["tasks"][0]
        self.assertEqual(finished["status"], "review-rejected")
        self.assertEqual(task["status"], "review-rejected")
        self.assertEqual([item["verdict"] for item in task["reviews"]], ["revise", "revise"])
        self.assertEqual(len(author.tasks), 2)

    def test_unreadable_verdict_does_not_keep_the_body(self) -> None:
        verdict, notes = parse_verdict("SECRET-TOKEN please approve\nmore secret")
        self.assertEqual(verdict, "revise")
        self.assertEqual(notes, "reviewer returned an unreadable verdict")
        self.assertNotIn("SECRET", notes)
        author = Author()
        reviewer = Reviewer(["SECRET-TOKEN approve this now"])
        with tempfile.TemporaryDirectory() as directory:
            finished = _drive(
                directory,
                ["author", "reviewer"],
                {"author": author, "reviewer": reviewer},
                max_rounds=1,
            )
        stored = json.dumps(finished)
        self.assertNotIn("SECRET", stored)
        self.assertEqual(finished["tasks"][0]["reviews"][0]["verdict"], "revise")
        self.assertEqual(finished["status"], "review-rejected")

    def test_same_provider_skips_review_and_keeps_the_result(self) -> None:
        author = Author()
        with tempfile.TemporaryDirectory() as directory:
            finished = _drive(directory, ["author"], {"author": author}, max_rounds=2)
        self.assertEqual(finished["status"], "unreviewed")
        self.assertEqual(finished["tasks"][0]["reviews"][0]["verdict"], "skipped")
        self.assertEqual(finished["tasks"][0]["reviews"][0]["notes"], "no distinct reviewer")
        self.assertEqual(len(author.tasks), 1)

    def test_default_drive_does_not_ask_for_review(self) -> None:
        author = Author()
        reviewer = Reviewer(["VERDICT revise\nnope"])
        with tempfile.TemporaryDirectory() as directory:
            finished = _drive(
                directory,
                ["author", "reviewer"],
                {"author": author, "reviewer": reviewer},
                max_rounds=0,
            )
        self.assertEqual(finished["status"], "completed")
        self.assertEqual(finished["tasks"][0]["reviews"], [])
        self.assertEqual(len(author.tasks), 1)
        self.assertEqual(reviewer.texts, ["VERDICT revise\nnope"])

    def test_budget_stops_later_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            finished = _drive(
                directory,
                ["usage"],
                {"usage": UsageProvider()},
                tasks=["first task", "second task"],
                concurrency=1,
                max_rounds=0,
                budgets={"max_cost": None, "max_input_tokens": 5, "max_output_tokens": None},
            )
            report = json.loads(Path(finished["report"]["json"]).read_text(encoding="utf-8"))
            self.assertTrue(Path(finished["report"]["markdown"]).is_file())
        self.assertEqual(finished["status"], "budget-exceeded")
        self.assertEqual(finished["stop_reason"], "budget")
        self.assertEqual([task["status"] for task in finished["tasks"]], ["completed", "budget-exceeded"])
        self.assertEqual(finished["tasks"][0]["usage"]["input_tokens"], 10)
        self.assertIsNone(finished["tasks"][0]["usage"]["cost"])
        self.assertEqual(report["usage"]["input_tokens"], 10)
        self.assertEqual(report["status"], "budget-exceeded")

    def test_parallel_tasks_hold_distinct_checkouts(self) -> None:
        isolator = _BarrierIsolator()
        with tempfile.TemporaryDirectory() as directory:
            finished = _drive(
                directory,
                ["author"],
                {"author": Author()},
                tasks=["one", "two"],
                concurrency=2,
                max_rounds=0,
                isolator=isolator,
            )
        self.assertEqual(finished["status"], "completed")
        self.assertEqual(len(set(isolator.paths)), 2)
        self.assertEqual(sorted(isolator.released), sorted(isolator.paths))

    def test_git_worktrees_are_created_and_removed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _git_repo(repo)
            isolator = GitWorktreeIsolator(repo)
            barrier = threading.Barrier(2)
            found: list[TaskIsolation] = []
            errors: list[BaseException] = []

            def grab(index: int) -> None:
                try:
                    item = isolator.acquire(RUN_ID, index)
                    found.append(item)
                    barrier.wait(timeout=10)
                except BaseException as exc:  # noqa: BLE001 - the assertion below reports it
                    errors.append(exc)

            threads = [threading.Thread(target=grab, args=(index,)) for index in (0, 1)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=15)
            self.assertEqual(errors, [])
            self.assertTrue(all(not thread.is_alive() for thread in threads))
            self.assertEqual(len(found), 2)
            self.assertNotEqual(found[0].path, found[1].path)
            note = found[0].path / "added.txt"
            note.write_text("hello\n", encoding="utf-8")
            diff = isolator.diff(found[0])
            self.assertIn("added.txt", diff)
            self.assertNotIn("SECRET", diff)
            for item in found:
                isolator.release(item)
                self.assertFalse(item.path.exists())
            listed = subprocess.run(
                ["git", "for-each-ref", "--format=%(refname)", "refs/heads/recursion/run"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(listed.stdout.strip(), "")
            worktrees = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(worktrees.stdout.count("worktree "), 1)


def _drive(
    directory: str,
    candidates: list[str],
    adapters: dict,
    *,
    tasks: list[str] | None = None,
    concurrency: int = 1,
    max_rounds: int = 0,
    budgets: dict | None = None,
    isolator=None,
) -> dict:
    names = tasks or ["Write the note."]
    store = RunStore(Path(directory))
    record = create_run(
        store,
        goal="\n".join(names),
        planned=[_planned(task) for task in names],
        candidates=[list(candidates) for _ in names],
        route=ROUTE,
        concurrency=concurrency,
    )
    return drive_run(
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
        budgets=budgets,
        isolator=isolator,
    )


def _planned(task: str) -> dict:
    return {"intent_text": task, "packet_id": "PACKET-" + task, "projection_digest": "digest-" + task}


class _DiffIsolator:
    def __init__(self, diff: str) -> None:
        self.diff_text = diff
        self.released = False

    def acquire(self, run_id: str, index: int, start_ref: str | None = None) -> TaskIsolation:
        del start_ref
        return TaskIsolation(Path(f"/virtual/{index}"), f"recursion/task/{run_id}/task-{index}", "base")

    def diff(self, item: TaskIsolation) -> str:
        del item
        return self.diff_text

    def commit_pending(self, item: TaskIsolation, message: str) -> str | None:
        del item, message
        return None

    def snapshot(self, item: TaskIsolation) -> str | None:
        del item
        return None

    def restore(self, item: TaskIsolation, head: str | None) -> bool:
        del item, head
        return False

    def ensure_run_branch(self, run_id: str, base_ref: str) -> str | None:
        del run_id, base_ref
        return None

    def merge_into_run(self, run_branch: str | None, task_branch: str) -> dict:
        del run_branch, task_branch
        return {"commit": None, "paths": [], "status": "landed"}

    def delete_run_branch(self, branch: str | None) -> bool:
        del branch
        return True

    def release(self, item: TaskIsolation, *, keep_branch: bool = False, keep_worktree: bool = False) -> None:
        del item, keep_branch, keep_worktree
        self.released = True


class _BarrierIsolator:
    def __init__(self) -> None:
        self.barrier = threading.Barrier(2)
        self.paths: list[str] = []
        self.released: list[str] = []
        self.lock = threading.Lock()

    def ensure_run_branch(self, run_id: str, base_ref: str) -> str | None:
        del run_id, base_ref
        return None

    def acquire(self, run_id: str, index: int, start_ref: str | None = None) -> TaskIsolation:
        del run_id, start_ref
        item = TaskIsolation(Path(f"/virtual/{index}"), f"branch-{index}", "base")
        with self.lock:
            self.paths.append(str(item.path))
        self.barrier.wait(timeout=3)
        return item

    def diff(self, item: TaskIsolation) -> str:
        del item
        return ""

    def commit_pending(self, item: TaskIsolation, message: str) -> str | None:
        del item, message
        return None

    def snapshot(self, item: TaskIsolation) -> str | None:
        del item
        return None

    def restore(self, item: TaskIsolation, head: str | None) -> bool:
        del item, head
        return False

    def merge_into_run(self, run_branch: str | None, task_branch: str) -> dict:
        del run_branch, task_branch
        return {"commit": None, "paths": [], "status": "landed"}

    def delete_run_branch(self, branch: str | None) -> bool:
        del branch
        return True

    def release(self, item: TaskIsolation, *, keep_branch: bool = False, keep_worktree: bool = False) -> None:
        del keep_branch, keep_worktree
        with self.lock:
            self.released.append(str(item.path))


def _git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "review-test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "review-test"], cwd=path, check=True)
    (path / "README").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "README"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=path, check=True, capture_output=True, text=True)


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_REVIEW_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

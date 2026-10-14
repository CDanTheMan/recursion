#!/usr/bin/env python3
"""Multi-task orchestration, run state, timeouts, and packaging. No live provider process."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.cli import main  # noqa: E402
from scripts.v3.harness.config import load_config  # noqa: E402
from scripts.v3.harness.dispatch import execute_with_policy  # noqa: E402
from scripts.v3.harness.errors import ProviderCLIMissing, ProviderRateLimited, ProviderTimeout  # noqa: E402
from scripts.v3.harness.orchestrate import (  # noqa: E402
    cancel_run,
    create_run,
    drive_run,
    plan_goal,
    rotate_candidates,
)
from scripts.v3.harness.providers import (  # noqa: E402
    ClaudeHeadlessProvider,
    ProviderRequest,
    ProviderResult,
)
from scripts.v3.harness.state import RunStore  # noqa: E402


REQUEST = ProviderRequest(task="hello", packet_id="PACKET-TEST", route_id="route-a")
ROUTE = {"fixture_id": "F-M1B-001", "selected_route_id": "route-a", "status": "selected"}


class RecordingProvider:
    def __init__(self, name: str, used: list[str]) -> None:
        self.name = name
        self.used = used

    def execute(self, request: ProviderRequest, *, allow_live: bool = False, timeout_seconds: int | None = None):
        del allow_live, timeout_seconds
        self.used.append(self.name)
        return ProviderResult(provider=self.name, argv=(self.name,), text=request.task, live=False)


class OrchestrationTests(unittest.TestCase):
    def test_goal_plans_each_line_through_m1a(self) -> None:
        planned = plan_goal("Alpha task.\n\nBeta task.")
        self.assertEqual([item["intent_text"] for item in planned["tasks"]], ["Alpha task.", "Beta task."])
        self.assertEqual([item["accepted"] for item in planned["tasks"]], [7, 7])
        self.assertNotEqual(planned["tasks"][0]["packet_id"], planned["tasks"][1]["packet_id"])
        self.assertNotEqual(
            planned["tasks"][0]["projection_digest"],
            planned["tasks"][1]["projection_digest"],
        )

    def test_parallel_runs_stay_inside_the_concurrency_limit(self) -> None:
        limit = 2
        inflight = 0
        peak = 0
        overflow: list[int] = []
        lock = threading.Lock()
        barrier = threading.Barrier(limit)

        class Holding:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                nonlocal inflight, peak
                del allow_live, timeout_seconds
                with lock:
                    inflight += 1
                    peak = max(peak, inflight)
                    if inflight > limit:
                        overflow.append(inflight)
                barrier.wait(timeout=3)
                with lock:
                    inflight -= 1
                return ProviderResult(provider="holding", argv=("holding",), text=request.task, live=False)

        with tempfile.TemporaryDirectory() as directory:
            store = RunStore(Path(directory))
            planned = [_planned(f"task-{index}") for index in range(4)]
            record = create_run(
                store,
                goal="task-0\ntask-1\ntask-2\ntask-3",
                planned=planned,
                candidates=[["holding"]] * 4,
                route=ROUTE,
                concurrency=limit,
            )
            finished = drive_run(
                store,
                record["run_id"],
                allow_live=False,
                retries=0,
                backoff_seconds=0,
                timeout_seconds={},
                route_id="route-a",
                open_adapter=lambda name: Holding(),
                sleep=lambda seconds: None,
            )
        self.assertEqual(peak, limit)
        self.assertEqual(overflow, [])
        self.assertEqual(finished["status"], "completed")
        self.assertEqual([task["status"] for task in finished["tasks"]], ["completed"] * 4)

    def test_tasks_rotate_across_providers(self) -> None:
        names = ["fixture", "claude", "codex", "grok"]
        used: list[str] = []
        adapters = {name: RecordingProvider(name, used) for name in names}
        self.assertEqual(
            [item[0] for item in rotate_candidates(names, 4)],
            names,
        )
        with tempfile.TemporaryDirectory() as directory:
            store = RunStore(Path(directory))
            record = create_run(
                store,
                goal="a\nb\nc\nd",
                planned=[_planned(name) for name in names],
                candidates=rotate_candidates(names, 4),
                route=ROUTE,
                concurrency=4,
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
            )
        self.assertEqual([task["provider"] for task in finished["tasks"]], names)

    def test_cancel_then_resume_persists_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = RunStore(root)
            record = create_run(
                store,
                goal="first\nsecond",
                planned=[_planned("first"), _planned("second")],
                candidates=[["fixture"], ["fixture"]],
                route=ROUTE,
                concurrency=1,
            )
            cancelled = cancel_run(store, record["run_id"])
            self.assertEqual(cancelled["status"], "cancelled")
            self.assertTrue((root / f"{record['run_id']}.json").is_file())
            with patch("sys.stdout", _String()), patch("sys.stderr", _String()):
                resumed = main(
                    [
                        "resume",
                        "--run",
                        record["run_id"],
                        "--state-dir",
                        str(root),
                        "--config",
                        str(ROOT / "config" / "harness.json"),
                    ]
                )
            self.assertEqual(resumed, 2)
            stored = store.load(record["run_id"])
            self.assertEqual(stored["status"], "unreviewed")
            self.assertEqual([task["provider"] for task in stored["tasks"]], ["fixture", "fixture"])
            self.assertTrue(all(task["execution"]["live"] is False for task in stored["tasks"]))
            _drop_run_branches(record["run_id"])

    def test_cli_goal_plans_and_runs_without_a_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stdout = _String()
            with patch("sys.stdout", stdout), patch("sys.stderr", _String()), patch(
                "scripts.v3.harness.providers.subprocess.run"
            ) as spawned:
                code = main(["plan", "--goal", "Alpha task.\nBeta task.", "--state-dir", str(root)])
            spawned.assert_not_called()
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(len(payload["tasks"]), 2)
            self.assertEqual(payload["plan_source"], "provider")
            self.assertEqual([task["id"] for task in payload["tasks"]], ["task-1", "task-2"])
            self.assertEqual(payload["tasks"][1]["depends_on"], [])
            self.assertEqual(list(root.glob("RUN-*.json")), [])

            stdout = _String()
            with patch("sys.stdout", stdout), patch("sys.stderr", _String()), patch(
                "scripts.v3.harness.providers.subprocess.run"
            ) as spawned:
                code = main(["run", "--goal", "Alpha task.\nBeta task.", "--state-dir", str(root)])
            spawned.assert_not_called()
            self.assertEqual(code, 2)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["status"], "unreviewed")
            self.assertEqual(payload["plan_source"], "provider")
            self.assertEqual([task["id"] for task in payload["tasks"]], ["task-1", "task-2"])
            run_records = [path for path in root.glob("RUN-*.json") if path.stem.count(".") == 0]
            self.assertEqual(len(run_records), 1)
            self.assertTrue((root / f"{payload['run_id']}.report.json").is_file())
            self.assertTrue((root / f"{payload['run_id']}.report.md").is_file())
            self.assertEqual({task["status"] for task in payload["tasks"]}, {"unreviewed"})
            report = json.loads((root / f"{payload['run_id']}.report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["run_branch"], f"recursion/run/{payload['run_id']}")
            _drop_run_branches(payload["run_id"])

    def test_timeout_rate_limit_and_missing_cli(self) -> None:
        config = load_config()
        self.assertEqual(config["orchestration"]["concurrency"], 2)
        self.assertEqual(config["routing"]["backoff_seconds"], 1)
        self.assertTrue(all(item["timeout_seconds"] == 120 for item in config["providers"]))

        adapter = ClaudeHeadlessProvider()
        with patch(
            "scripts.v3.harness.providers.subprocess.run",
            side_effect=FileNotFoundError(2, "No such file"),
        ):
            with self.assertRaises(ProviderCLIMissing) as missing:
                adapter.execute(REQUEST, allow_live=True, timeout_seconds=5)
        self.assertIn("claude CLI was not found on PATH (claude)", str(missing.exception))

        with patch(
            "scripts.v3.harness.providers.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=5),
        ):
            with self.assertRaises(ProviderTimeout) as timed:
                adapter.execute(REQUEST, allow_live=True, timeout_seconds=5)
        self.assertIn("timed out after 5 seconds", str(timed.exception))

        completed = subprocess.CompletedProcess(args=[], returncode=429, stdout="", stderr="SECRET rate limit")
        with patch("scripts.v3.harness.providers.subprocess.run", return_value=completed):
            with self.assertRaises(ProviderRateLimited) as limited:
                adapter.execute(REQUEST, allow_live=True, timeout_seconds=5)
        self.assertNotIn("SECRET", str(limited.exception))

        calls = {"n": 0}

        class Once:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del request, allow_live, timeout_seconds
                calls["n"] += 1
                if calls["n"] == 1:
                    raise ProviderRateLimited("claude was rate-limited")
                return ProviderResult(provider="claude", argv=("claude",), text="ok", live=False)

        slept: list[float] = []
        result, attempts = execute_with_policy(
            REQUEST,
            ["claude"],
            allow_live=False,
            retries=1,
            backoff_seconds=3,
            sleep=slept.append,
            open_adapter=lambda name: Once(),
        )
        self.assertEqual(slept, [3])
        self.assertEqual(result.text, "ok")
        self.assertEqual([item["ok"] for item in attempts], [False, True])

    def test_package_declares_a_console_script(self) -> None:
        payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(payload["project"]["scripts"]["recursion"], "scripts.v3.harness.cli:main")
        self.assertGreaterEqual(tuple(int(part) for part in payload["project"]["requires-python"].removeprefix(">=").split(".")[:2]), (3, 11))


def _drop_run_branches(run_id: str) -> None:
    listed = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/recursion"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    prefixes = (f"recursion/run/{run_id}", f"recursion/task/{run_id}/")
    for name in listed.stdout.split():
        if name == prefixes[0] or name.startswith(prefixes[1]):
            completed = subprocess.run(
                ["git", "branch", "-D", name], cwd=ROOT, capture_output=True, text=True, check=False
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or f"could not delete {name}")
    subprocess.run(["git", "worktree", "prune"], cwd=ROOT, capture_output=True, check=False)


def _planned(task: str) -> dict:
    return {
        "intent_text": task,
        "packet_id": "PACKET-" + task,
        "projection_digest": "digest-" + task,
    }


class _String:
    """Small stdout stand-in that does not need io.StringIO's patch quirks."""

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
        print("HARNESS_ORCHESTRATION_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

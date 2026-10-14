#!/usr/bin/env python3
"""Concurrency override and plain progress lines. Fixture provider only; no live CLI."""

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
from scripts.v3.harness.log import JsonLog, progress_line, read_events  # noqa: E402
from scripts.v3.harness.providers import ProviderResult  # noqa: E402


GOAL = "Alpha task.\nBeta task."


class ProgressTests(unittest.TestCase):
    def test_progress_lines_name_the_outcome_and_omit_error_text(self) -> None:
        self.assertEqual(progress_line("task.started", {"index": 0}), "task 0 started")
        self.assertEqual(
            progress_line("task.completed", {"index": 1, "provider": "fixture"}),
            "task 1 completed provider=fixture",
        )
        self.assertEqual(
            progress_line("task.failed", {"index": 2, "error": "SECRET leaked"}),
            "task 2 failed",
        )
        self.assertEqual(progress_line("task.cancelled", {"index": 0}), "task 0 cancelled")
        self.assertEqual(progress_line("task.unreviewed", {"index": 0}), "task 0 unreviewed")
        self.assertEqual(progress_line("task.conflict", {"index": 3}), "task 3 conflict")
        self.assertEqual(progress_line("task.review_rejected", {"index": 4}), "task 4 review-rejected")
        self.assertEqual(
            progress_line("provider.attempt", {"attempt": 0, "provider": "fixture"}),
            "provider fixture attempt 0",
        )
        self.assertEqual(progress_line("provider.result", {"provider": "fixture"}), "provider fixture finished")
        self.assertEqual(
            progress_line("provider.failed", {"provider": "claude", "error": "ProviderTimeout"}),
            "provider claude failed ProviderTimeout",
        )
        self.assertEqual(progress_line("provider.skipped", {"provider": "grok"}), "provider grok skipped")
        self.assertEqual(progress_line("run.refused", {"error": "HarnessError"}), "run refused HarnessError")
        self.assertEqual(progress_line("run.resume", {"status": "running"}), "run resume running")
        self.assertEqual(progress_line("plan.admitted", {}), "plan admitted")
        self.assertEqual(progress_line("route.selected", {"selected_route_id": "route-a"}), "route route-a")
        self.assertEqual(
            progress_line("provider.candidates", {"candidates": ["fixture", "claude"]}),
            "candidates fixture,claude",
        )
        self.assertEqual(progress_line("task.other", {}), "task.other")

        json_sink = _Buffer()
        plain = _Buffer()
        JsonLog([json_sink], progress=plain).event("task.failed", index=0, error="SECRET leaked")
        logged = json.loads(json_sink.getvalue())
        self.assertEqual(logged["event"], "task.failed")
        self.assertEqual(logged["error"], "SECRET leaked")
        self.assertEqual(plain.getvalue().strip(), "task 0 failed")
        self.assertNotIn("SECRET", plain.getvalue())

    def test_concurrency_flag_rejects_zero_and_text(self) -> None:
        for value in ("0", "foo", "-1", "1.5"):
            with self.subTest(value=value):
                stderr = StringIO()
                with patch("sys.stdout", StringIO()), patch("sys.stderr", stderr):
                    with self.assertRaises(SystemExit) as caught:
                        main(["run", "--goal", "Alpha task.", "--concurrency", value])
                self.assertEqual(caught.exception.code, 2)
                self.assertIn("concurrency must be an integer >= 1", stderr.getvalue())

    def test_omitted_concurrency_stays_on_jsonl_stderr(self) -> None:
        self.assertEqual(load_config()["orchestration"]["concurrency"], 2)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = _fixture_config(root)
            stderr = StringIO()
            code, payload = _invoke(
                ["run", "--goal", GOAL, "--state-dir", str(root), "--config", str(config)],
                stderr,
            )
            _cleanup(root)
        self.assertEqual(code, 2)
        self.assertEqual(payload["concurrency"], 2)
        rows = _json_lines(stderr.getvalue())
        self.assertIn("task.started", [row["event"] for row in rows])
        self.assertIn("provider.attempt", [row["event"] for row in rows])
        self.assertTrue(all(isinstance(row.get("event"), str) for row in rows))

    def test_concurrency_override_is_stored_and_limits_overlap(self) -> None:
        counter = _Counting()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = _fixture_config(root)
            with patch("scripts.v3.harness.providers.open_provider", return_value=counter):
                code, payload = _invoke(
                    [
                        "run",
                        "--goal",
                        GOAL,
                        "--concurrency",
                        "1",
                        "--state-dir",
                        str(root),
                        "--config",
                        str(config),
                    ],
                    StringIO(),
                )
            _cleanup(root)
        self.assertEqual(code, 2)
        self.assertEqual(payload["concurrency"], 1)
        self.assertEqual(payload["status"], "unreviewed")
        self.assertEqual(counter.workers, 2)
        self.assertEqual(counter.peak, 1)
        self.assertEqual(counter.inflight, 0)

    def test_resume_keeps_stored_concurrency_unless_overridden(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = _fixture_config(root)
            code, payload = _invoke(
                [
                    "run",
                    "--goal",
                    GOAL,
                    "--concurrency",
                    "3",
                    "--state-dir",
                    str(root),
                    "--config",
                    str(config),
                ],
                StringIO(),
            )
            self.assertEqual(code, 2)
            self.assertEqual(payload["concurrency"], 3)
            run_id = payload["run_id"]
            code, resumed = _invoke(
                [
                    "resume",
                    "--run",
                    run_id,
                    "--state-dir",
                    str(root),
                    "--config",
                    str(config),
                ],
                StringIO(),
            )
            self.assertEqual(code, 2)
            self.assertEqual(resumed["concurrency"], 3)
            code, overridden = _invoke(
                [
                    "resume",
                    "--run",
                    run_id,
                    "--concurrency",
                    "1",
                    "--state-dir",
                    str(root),
                    "--config",
                    str(config),
                ],
                StringIO(),
            )
            _cleanup(root)
        self.assertEqual(code, 2)
        self.assertEqual(overridden["concurrency"], 1)
        self.assertEqual(overridden["run_id"], run_id)

    def test_progress_flag_prints_plain_lines_and_keeps_jsonl_on_the_log(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = _fixture_config(root)
            log_path = root / "events.jsonl"
            stderr = StringIO()
            code, payload = _invoke(
                [
                    "run",
                    "--goal",
                    GOAL,
                    "--progress",
                    "--log",
                    str(log_path),
                    "--state-dir",
                    str(root),
                    "--config",
                    str(config),
                ],
                stderr,
            )
            events = read_events(log_path)
            _cleanup(root)
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "unreviewed")
        lines = [line for line in stderr.getvalue().splitlines() if line.strip()]
        self.assertIn("task 0 started", lines)
        self.assertIn("provider fixture attempt 0", lines)
        self.assertIn("provider fixture finished", lines)
        self.assertIn("task 0 unreviewed", lines)
        self.assertTrue(all(not line.startswith("{") for line in lines))
        names = [item["event"] for item in events]
        self.assertIn("task.started", names)
        self.assertIn("provider.attempt", names)
        self.assertIn("task.unreviewed", names)

    def test_tty_stderr_prints_plain_lines_without_the_flag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = _fixture_config(root)
            stderr = _TTY()
            code, _payload = _invoke(
                [
                    "run",
                    "--goal",
                    GOAL,
                    "--state-dir",
                    str(root),
                    "--config",
                    str(config),
                ],
                stderr,
            )
            _cleanup(root)
        self.assertEqual(code, 2)
        lines = [line for line in stderr.getvalue().splitlines() if line.strip()]
        self.assertIn("task 0 started", lines)
        self.assertIn("provider fixture attempt 0", lines)
        self.assertIn("task 0 unreviewed", lines)
        self.assertTrue(all(not line.startswith("{") for line in lines))


class _Counting:
    def __init__(self) -> None:
        self.inflight = 0
        self.peak = 0
        self.workers = 0
        self._lock = threading.Lock()

    def execute(self, request, *, allow_live=False, timeout_seconds=None):
        del allow_live, timeout_seconds
        if getattr(request, "kind", "execute") != "execute":
            return ProviderResult(provider="fixture", argv=("fixture",), text="not-a-plan", live=False)
        with self._lock:
            self.inflight += 1
            self.peak = max(self.peak, self.inflight)
            self.workers += 1
        try:
            time.sleep(0.05)
            return ProviderResult(provider="fixture", argv=("fixture",), text=request.task, live=False)
        finally:
            with self._lock:
                self.inflight -= 1


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


class _TTY(_Buffer):
    def isatty(self) -> bool:
        return True


def _invoke(args: list[str], stderr) -> tuple[int, dict]:
    stdout = _Buffer()
    with patch("sys.stdout", stdout), patch("sys.stderr", stderr), patch(
        "scripts.v3.harness.providers.subprocess.run"
    ) as spawned:
        code = main(args)
    spawned.assert_not_called()
    return code, json.loads(stdout.getvalue())


def _json_lines(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _fixture_config(directory: Path) -> Path:
    payload = json.loads((ROOT / "config" / "harness.json").read_text(encoding="utf-8"))
    payload["routing"]["retries"] = 0
    payload["routing"]["backoff_seconds"] = 0
    for item in payload["providers"]:
        item["enabled"] = item["name"] == "fixture"
    path = directory / "harness.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _cleanup(state_dir: Path) -> None:
    if not state_dir.is_dir():
        return
    for path in state_dir.glob("RUN-*.json"):
        if path.stem.count(".") == 0:
            _drop_run_branches(path.stem)


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


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_PROGRESS_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

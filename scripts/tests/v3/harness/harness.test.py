#!/usr/bin/env python3
"""End-to-end harness slice: M1A plan, M1B route, fixture provider. No live CLI."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.errors import HarnessError, LiveProviderDisabled  # noqa: E402
from scripts.v3.harness.providers import ClaudeHeadlessProvider, ProviderRequest  # noqa: E402
from scripts.v3.harness.routing import require_selected  # noqa: E402
from scripts.v3.harness.run import main, run_task  # noqa: E402
from scripts.v3.planning.validation.canonical import digest  # noqa: E402


def _load_checker():
    path = ROOT / "tools" / "check_v3_orientation.py"
    spec = importlib.util.spec_from_file_location("check_v3_orientation", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HarnessSliceTests(unittest.TestCase):
    def test_fixture_provider_plans_and_executes(self) -> None:
        task = "Summarize the harness slice."
        with patch("scripts.v3.harness.providers.run_command") as spawned:
            first = run_task(task, provider="fixture")
            second = run_task(task, provider="fixture")
        spawned.assert_not_called()

        self.assertEqual(first, second)
        self.assertEqual(first["task"], task)
        planning = first["planning"]
        self.assertEqual(planning["accepted"], 7)
        self.assertEqual(
            planning["commands"],
            [
                "record-owner-intent",
                "accept-goal-spec",
                "start-arm-run",
                "propose-plan-revision",
                "record-capacity-observation",
                "reserve-budget",
                "derive-work-packet",
            ],
        )
        self.assertEqual(planning["intent_text"], task)
        self.assertEqual(planning["outcome"], task)
        self.assertEqual(planning["semantic_definition_digest"], digest(task))
        self.assertTrue(planning["packet_id"].startswith("PACKET-"))
        self.assertEqual(first["route"]["fixture_id"], "F-M1B-001")
        self.assertEqual(first["route"]["status"], "selected")
        self.assertEqual(first["route"]["selected_route_id"], "route-a")
        execution = first["execution"]
        self.assertEqual(execution["provider"], "fixture")
        self.assertFalse(execution["live"])
        self.assertEqual(execution["argv"], ["fixture-provider", "--output-format", "json"])
        self.assertIn(task, execution["text"])
        self.assertIn("route=route-a", execution["text"])
        self.assertIn(planning["packet_id"], execution["text"])

    def test_distinct_tasks_change_the_projection(self) -> None:
        left = run_task("Write the adapter interface.", provider="fixture")
        right = run_task("Write the fixture provider.", provider="fixture")
        self.assertNotEqual(left["planning"]["projection_digest"], right["planning"]["projection_digest"])
        self.assertNotEqual(
            left["planning"]["semantic_definition_digest"],
            right["planning"]["semantic_definition_digest"],
        )

    def test_empty_task_is_refused(self) -> None:
        with self.assertRaises(HarnessError):
            run_task("   ", provider="fixture")

    def test_unselected_route_does_not_execute(self) -> None:
        with self.assertRaises(HarnessError):
            require_selected({"status": "refused", "selected_route_id": None})

    def test_claude_argv_is_print_mode_and_does_not_spawn(self) -> None:
        request = ProviderRequest(task="hello", packet_id="PACKET-TEST", route_id="route-a")
        adapter = ClaudeHeadlessProvider()
        self.assertEqual(adapter.argv(request), ("claude", "-p", "--output-format", "stream-json"))
        with patch("scripts.v3.harness.providers.run_command") as spawned:
            with self.assertRaises(LiveProviderDisabled):
                adapter.execute(request)
        spawned.assert_not_called()

    def test_cli_prints_json_on_stdout(self) -> None:
        from io import StringIO

        stdout = StringIO()
        with patch("sys.stdout", stdout), patch("scripts.v3.harness.providers.run_command") as spawned:
            code = main(["--task", "Count the commands.", "--provider", "fixture"])
        spawned.assert_not_called()
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["execution"]["provider"], "fixture")
        self.assertFalse(payload["execution"]["live"])

    def test_contracts_gate_keeps_m1_and_includes_harness(self) -> None:
        checker = _load_checker()
        m1 = checker.m1_programs()
        harness = checker.harness_programs()
        self.assertEqual(len(m1), 23)
        self.assertEqual(
            [item[0] for item in harness],
            [
                "scripts/tests/v3/harness/adapters.test.py",
                "scripts/tests/v3/harness/doctor.test.py",
                "scripts/tests/v3/harness/dual_fixture.test.py",
                "scripts/tests/v3/harness/harness.test.py",
                "scripts/tests/v3/harness/landing.test.py",
                "scripts/tests/v3/harness/live.test.py",
                "scripts/tests/v3/harness/ops.test.py",
                "scripts/tests/v3/harness/orchestration.test.py",
                "scripts/tests/v3/harness/progress.test.py",
                "scripts/tests/v3/harness/recovery.test.py",
                "scripts/tests/v3/harness/review.test.py",
                "scripts/tests/v3/harness/routing.test.py",
                "scripts/tests/v3/harness/streams.test.py",
            ],
        )
        self.assertIn("scripts/v3/harness/run.py", checker.PRODUCT_SLICE)
        self.assertIn("docs/v3/HARNESS-SLICE.md", checker.PRODUCT_SLICE)


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_SLICE_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

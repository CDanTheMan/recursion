#!/usr/bin/env python3
"""Capability weights, availability classes, and persisted cooldowns. No live CLI."""

from __future__ import annotations

import json
import sys
import tempfile
import time
import types
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.availability import (  # noqa: E402
    classify_failure,
    default_cli_finder,
    provider_report,
)
from scripts.v3.harness.capabilities import select_candidates  # noqa: E402
from scripts.v3.harness.cli import main  # noqa: E402
from scripts.v3.harness.config import load_config  # noqa: E402
from scripts.v3.harness.cooldowns import CooldownStore, format_until  # noqa: E402
from scripts.v3.harness.dag import admit_goal, plan_prompt  # noqa: E402
from scripts.v3.harness.dispatch import execute_with_policy  # noqa: E402
from scripts.v3.harness.errors import (  # noqa: E402
    HarnessError,
    ProviderAuthExpired,
    ProviderQuotaExhausted,
    ProviderRateLimited,
    ProviderTransient,
)
from scripts.v3.harness.log import NullLog  # noqa: E402
from scripts.v3.harness.orchestrate import create_run, drive_run, reopen_run  # noqa: E402
from scripts.v3.harness.providers import FixtureProvider, ProviderRequest, ProviderResult  # noqa: E402
from scripts.v3.harness.state import RunStore  # noqa: E402


REQUEST = ProviderRequest(task="hello", packet_id="PACKET-ROUTE", route_id="route-a")
NOW = 1_700_000_000


class RoutingTests(unittest.TestCase):
    def test_failures_are_classified_without_copying_stderr(self) -> None:
        cases = (
            (401, "SECRET", ProviderAuthExpired, "authentication expired", "auth-expired"),
            (1, "please log in SECRET", ProviderAuthExpired, "authentication expired", "auth-expired"),
            (402, "SECRET", ProviderQuotaExhausted, "quota is exhausted", "quota-exhausted"),
            (1, "resource_exhausted SECRET", ProviderQuotaExhausted, "quota is exhausted", "quota-exhausted"),
            (429, "SECRET", ProviderRateLimited, "was rate-limited", "rate-limited"),
            (1, "overloaded SECRET", ProviderRateLimited, "was rate-limited", "rate-limited"),
            (503, "SECRET", ProviderTransient, "transient error", None),
            (1, "connection reset SECRET", ProviderTransient, "transient error", None),
            (7, "SECRET-TOKEN", HarnessError, "exited 7", None),
        )
        for code, stderr, kind, text, reason in cases:
            with self.subTest(code=code, stderr=stderr):
                error = classify_failure("claude", code, stderr)
                self.assertIsInstance(error, kind)
                self.assertIn(text, str(error))
                self.assertNotIn("SECRET", str(error))
                if reason is not None:
                    self.assertEqual(error.reason, reason)

    def test_reset_time_is_read_and_then_discarded(self) -> None:
        rate = classify_failure("claude", 1, "SECRET rate limit retry-after: 30")
        self.assertIsInstance(rate, ProviderRateLimited)
        self.assertEqual(rate.retry_after, 30)
        self.assertNotIn("SECRET", str(rate))
        minutes = classify_failure("codex", 429, "try again in 2 minutes SECRET")
        self.assertEqual(minutes.retry_after, 120)
        stamped = classify_failure("grok", 429, "reset 2026-10-14T08:35:00Z SECRET")
        self.assertEqual(stamped.until, "2026-10-14T08:35:00Z")
        self.assertNotIn("SECRET", str(stamped))

    def test_rate_limit_cools_down_and_the_next_provider_runs(self) -> None:
        calls: list[str] = []

        class Adapter:
            def __init__(self, name: str) -> None:
                self.name = name

            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del request, allow_live, timeout_seconds
                calls.append(self.name)
                if self.name == "claude":
                    raise ProviderRateLimited(
                        "claude was rate-limited",
                        until="2026-10-14T08:35:00Z",
                        retry_after=30,
                    )
                return ProviderResult(provider=self.name, argv=(self.name,), text="ok", live=False)

        with tempfile.TemporaryDirectory() as directory:
            store = CooldownStore(Path(directory) / "cooldowns.json")
            slept: list[float] = []
            result, attempts = execute_with_policy(
                REQUEST,
                ["claude", "codex"],
                allow_live=False,
                retries=2,
                backoff_seconds=3,
                sleep=slept.append,
                open_adapter=lambda name: Adapter(name),
                cooldowns=store,
                cooldown_seconds=60,
                now=lambda: NOW,
            )
            self.assertEqual(slept, [])
            self.assertEqual(calls, ["claude", "codex"])
            self.assertEqual(result.text, "ok")
            self.assertEqual(attempts[0]["reason"], "rate-limited")
            body = (Path(directory) / "cooldowns.json").read_text(encoding="utf-8")
            self.assertNotIn("SECRET", body)
            self.assertEqual(json.loads(body)["providers"]["claude"]["until"], "2026-10-14T08:35:00Z")
            calls.clear()
            again, skipped = execute_with_policy(
                REQUEST,
                ["claude", "codex"],
                allow_live=False,
                retries=1,
                backoff_seconds=0,
                open_adapter=lambda name: Adapter(name),
                cooldowns=store,
                now=lambda: NOW,
            )
            self.assertEqual(calls, ["codex"])
            self.assertEqual(again.provider, "codex")
            self.assertEqual(skipped[0]["error"], "cooldown")
            later = CooldownStore(Path(directory) / "cooldowns.json")
            self.assertNotIn("claude", later.active(NOW + 10**9))

    def test_transient_errors_retry_and_a_cooled_pin_does_not_fall_back(self) -> None:
        calls = {"n": 0}

        class Flaky:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del request, allow_live, timeout_seconds
                calls["n"] += 1
                if calls["n"] == 1:
                    raise ProviderTransient("claude hit a transient error")
                return ProviderResult(provider="claude", argv=("claude",), text="ok", live=False)

        slept: list[float] = []
        result, _attempts = execute_with_policy(
            REQUEST,
            ["claude"],
            allow_live=False,
            retries=1,
            backoff_seconds=3,
            sleep=slept.append,
            open_adapter=lambda name: Flaky(),
        )
        self.assertEqual(slept, [3])
        self.assertEqual(result.text, "ok")

        with tempfile.TemporaryDirectory() as directory:
            store = CooldownStore(Path(directory) / "cooldowns.json")
            store.record("grok", "quota-exhausted", NOW + 100)

            class Unused:
                def execute(self, request, *, allow_live=False, timeout_seconds=None):
                    del request, allow_live, timeout_seconds
                    raise AssertionError("cooled provider was called")

            with self.assertRaises(HarnessError) as caught:
                execute_with_policy(
                    REQUEST,
                    ["grok"],
                    allow_live=False,
                    retries=1,
                    backoff_seconds=0,
                    open_adapter=lambda name: Unused(),
                    cooldowns=store,
                    now=lambda: NOW,
                )
            self.assertIn("grok#cooldown", str(caught.exception))
            fallback, attempts = execute_with_policy(
                REQUEST,
                ["grok", "codex"],
                allow_live=False,
                retries=0,
                backoff_seconds=0,
                open_adapter=_Ok,
                cooldowns=store,
                now=lambda: NOW,
            )
            self.assertEqual(fallback.provider, "codex")
            self.assertEqual(attempts[0]["error"], "cooldown")

    def test_weights_change_order_and_config_rejects_a_bad_weight(self) -> None:
        config = load_config()
        self.assertEqual(config["routing"]["cooldown_seconds"], 60)
        self.assertEqual(config["routing"]["weights"]["fixture"], 1)
        config["routing"]["weights"]["grok"] = 5
        self.assertEqual(
            select_candidates(config, extra_capabilities=["subscription"]),
            ["grok", "claude", "codex"],
        )
        self.assertEqual(
            select_candidates(config, provider="claude", extra_capabilities=["subscription"], fallback=True),
            ["claude", "grok", "codex"],
        )
        raw = json.loads((ROOT / "config" / "harness.json").read_text(encoding="utf-8"))
        raw["routing"]["weights"]["claude"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "harness.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaises(HarnessError) as caught:
                load_config(path)
        self.assertIn("routing.weights.claude", str(caught.exception))

    def test_providers_command_reports_cli_and_cooldown_without_spawning(self) -> None:
        config = load_config()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = CooldownStore(root / "cooldowns.json")
            future = time.time() + 3600
            store.record("claude", "auth-expired", future)
            rows = provider_report(
                config,
                store,
                finder=lambda command: "/bin/claude" if command == "claude" else None,
            )
            by_name = {row["name"]: row for row in rows}
            self.assertTrue(by_name["fixture"]["cli_found"])
            self.assertTrue(by_name["claude"]["cli_found"])
            self.assertFalse(by_name["codex"]["cli_found"])
            self.assertEqual(by_name["claude"]["cooldown"]["reason"], "auth-expired")
            self.assertEqual(by_name["claude"]["cooldown"]["until"], format_until(future))
            self.assertIsNone(by_name["grok"]["cooldown"])
            self.assertEqual(by_name["grok"]["capabilities"], ["execute", "streaming-json", "subscription"])

            def finder(command: str):
                return "found" if command == "codex" else None

            stdout = StringIO()
            with patch("sys.stdout", stdout), patch("scripts.v3.harness.cli.default_cli_finder", finder), patch(
                "scripts.v3.harness.providers.subprocess.run"
            ) as spawned:
                code = main(["providers", "--state-dir", str(root)])
            spawned.assert_not_called()
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            reported = {row["name"]: row for row in payload["providers"]}
            self.assertTrue(reported["codex"]["cli_found"])
            self.assertFalse(reported["grok"]["cli_found"])
            self.assertEqual(reported["claude"]["cooldown"]["reason"], "auth-expired")
            body = (root / "cooldowns.json").read_text(encoding="utf-8")
            self.assertNotIn("SECRET", body)

    def test_cli_finder_uses_doctor_without_diagnose_or_a_process(self) -> None:
        calls: list[str] = []
        doctor = types.ModuleType("scripts.v3.harness.doctor")

        def resolve_executable(name: str, **kwargs):
            del kwargs
            calls.append(name)
            return Path("/usr/bin") / name

        def diagnose(*args, **kwargs):
            del args, kwargs
            raise AssertionError("diagnose")

        doctor.resolve_executable = resolve_executable
        doctor.diagnose = diagnose
        previous = sys.modules.get("scripts.v3.harness.doctor")
        sys.modules["scripts.v3.harness.doctor"] = doctor
        try:
            with patch("subprocess.run") as spawned:
                found = default_cli_finder("claude")
            spawned.assert_not_called()
        finally:
            if previous is None:
                sys.modules.pop("scripts.v3.harness.doctor", None)
            else:
                sys.modules["scripts.v3.harness.doctor"] = previous
        self.assertEqual(found, Path("/usr/bin/claude"))
        self.assertEqual(calls, ["claude"])

    def test_prompt_asks_for_depends_on_and_line_goals_stay_independent(self) -> None:
        prompt = plan_prompt("Alpha task.\nBeta task.")
        self.assertEqual(prompt.count("Goal:\n"), 1)
        self.assertIn('"depends_on":["build"]', prompt)
        planned = admit_goal(
            "Alpha task.\nBeta task.",
            candidates=["fixture"],
            allow_live=False,
            retries=0,
            backoff_seconds=0,
            timeout_seconds=None,
            log=NullLog(),
            open_adapter=lambda name: FixtureProvider(),
        )
        self.assertEqual(planned["source"], "provider")
        self.assertEqual([task["depends_on"] for task in planned["tasks"]], [[], []])
        self.assertEqual([task["id"] for task in planned["tasks"]], ["task-1", "task-2"])

    def test_fixture_graph_runs_dependents_only_after_the_dependency(self) -> None:
        planned = admit_goal(
            "graph\nbuild: Build the note. requires execute\ntest: Test the note. depends build",
            candidates=["fixture"],
            allow_live=False,
            retries=0,
            backoff_seconds=0,
            timeout_seconds=None,
            log=NullLog(),
            open_adapter=lambda name: FixtureProvider(),
        )
        self.assertEqual(planned["source"], "provider")
        self.assertIsNone(planned["fallback"])
        self.assertEqual(planned["tasks"][0]["required_capabilities"], ["execute"])
        self.assertEqual(planned["tasks"][1]["depends_on"], ["build"])
        calls: list[str] = []

        class Flaky:
            def execute(self, request, *, allow_live=False, timeout_seconds=None):
                del allow_live, timeout_seconds
                calls.append(request.task)
                if request.task.startswith("Build") and calls.count(request.task) == 1:
                    raise HarnessError("not yet")
                return ProviderResult(provider="flaky", argv=("flaky",), text="ok", live=False)

        with tempfile.TemporaryDirectory() as directory:
            store = RunStore(Path(directory))
            record = create_run(
                store,
                goal=planned["goal"],
                planned=planned["tasks"],
                candidates=[["flaky"], ["flaky"]],
                route={"fixture_id": "F-M1B-001", "selected_route_id": "route-a", "status": "selected"},
                concurrency=2,
                plan_source="provider",
            )
            failed = drive_run(
                store,
                record["run_id"],
                allow_live=False,
                retries=0,
                backoff_seconds=0,
                timeout_seconds={},
                route_id="route-a",
                open_adapter=lambda name: Flaky(),
                sleep=lambda seconds: None,
            )
            self.assertEqual([task["status"] for task in failed["tasks"]], ["failed", "skipped"])
            self.assertEqual(failed["tasks"][1]["error"], "dependency build is failed")
            self.assertEqual(calls, ["Build the note."])
            reopen_run(store, record["run_id"])
            resumed = drive_run(
                store,
                record["run_id"],
                allow_live=False,
                retries=0,
                backoff_seconds=0,
                timeout_seconds={},
                route_id="route-a",
                open_adapter=lambda name: Flaky(),
                sleep=lambda seconds: None,
            )
        self.assertEqual([task["status"] for task in resumed["tasks"]], ["completed", "completed"])
        self.assertEqual(calls, ["Build the note.", "Build the note.", "Test the note."])
        self.assertEqual(resumed["cooldowns"], {})

    def test_invalid_graph_falls_back_to_lines(self) -> None:
        planned = admit_goal(
            "graph\nnot a node",
            candidates=["fixture"],
            allow_live=False,
            retries=0,
            backoff_seconds=0,
            timeout_seconds=None,
            log=NullLog(),
            open_adapter=lambda name: FixtureProvider(),
        )
        self.assertEqual(planned["source"], "lines")
        self.assertEqual(planned["fallback"], "planner tasks must be a non-empty list")
        self.assertEqual(planned["tasks"][0]["depends_on"], [])


class _Ok:
    def __init__(self, name: str) -> None:
        self.name = name

    def execute(self, request, *, allow_live=False, timeout_seconds=None):
        del request, allow_live, timeout_seconds
        return ProviderResult(provider=self.name, argv=(self.name,), text=self.name, live=False)


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_ROUTING_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

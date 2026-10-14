#!/usr/bin/env python3
"""Fixture-backed adapter, routing, retry, and CLI tests. No live provider process."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.capabilities import select_candidates  # noqa: E402
from scripts.v3.harness.cli import main  # noqa: E402
from scripts.v3.harness.config import load_config  # noqa: E402
from scripts.v3.harness.dispatch import execute_with_policy  # noqa: E402
from scripts.v3.harness.errors import HarnessError, LiveProviderDisabled  # noqa: E402
from scripts.v3.harness.log import JsonLog, read_events  # noqa: E402
from scripts.v3.harness.providers import (  # noqa: E402
    ClaudeHeadlessProvider,
    CodexExecProvider,
    CursorHeadlessProvider,
    FixtureProvider,
    GeminiHeadlessProvider,
    GrokHeadlessProvider,
    OpenCodeHeadlessProvider,
    ProviderRequest,
    ProviderResult,
)


REQUEST = ProviderRequest(task="hello", packet_id="PACKET-TEST", route_id="route-a")


class ScriptedProvider:
    def __init__(self, failures: int) -> None:
        self.left = failures
        self.calls = 0

    def execute(self, request: ProviderRequest, *, allow_live: bool = False) -> ProviderResult:
        del request, allow_live
        self.calls += 1
        if self.left:
            self.left -= 1
            raise HarnessError("injected failure")
        return ProviderResult(provider="scripted", argv=("scripted",), text="ok", live=False)


class AdapterTests(unittest.TestCase):
    def test_each_adapter_argv_and_refuses_to_spawn(self) -> None:
        cases = (
            (ClaudeHeadlessProvider(), ("claude", "-p", "--output-format", "stream-json")),
            (CodexExecProvider(), ("codex", "exec", "--json", "hello")),
            (GrokHeadlessProvider(), ("grok", "-p", "hello", "--output-format", "streaming-json")),
            (GeminiHeadlessProvider(), ("gemini", "-p", "hello", "--output-format", "stream-json")),
            (CursorHeadlessProvider(), ("cursor-agent", "-p", "--output-format", "stream-json", "hello")),
            (OpenCodeHeadlessProvider(), ("opencode", "run", "--format", "json", "hello")),
            (FixtureProvider(), ("fixture-provider", "--output-format", "json")),
        )
        for adapter, argv in cases:
            with self.subTest(adapter=adapter.name):
                self.assertEqual(adapter.argv(REQUEST), argv)
                with patch("scripts.v3.harness.providers.subprocess.run") as spawned:
                    if adapter.name == "fixture":
                        result = adapter.execute(REQUEST)
                        self.assertFalse(result.live)
                        self.assertIn("hello", result.text)
                    else:
                        with self.assertRaises(LiveProviderDisabled):
                            adapter.execute(REQUEST)
                spawned.assert_not_called()

    def test_live_argv_uses_stdin_only_for_claude(self) -> None:
        cases = (
            (ClaudeHeadlessProvider(), ["claude", "-p", "--output-format", "stream-json"], "hello"),
            (CodexExecProvider(), ["codex", "exec", "--json", "hello"], None),
            (GrokHeadlessProvider(), ["grok", "-p", "hello", "--output-format", "streaming-json"], None),
            (GeminiHeadlessProvider(), ["gemini", "-p", "hello", "--output-format", "stream-json"], None),
            (CursorHeadlessProvider(), ["cursor-agent", "-p", "--output-format", "stream-json", "hello"], None),
            (OpenCodeHeadlessProvider(), ["opencode", "run", "--format", "json", "hello"], None),
        )
        for adapter, argv, stdin_text in cases:
            with self.subTest(adapter=adapter.name):
                completed = subprocess.CompletedProcess(args=argv, returncode=0, stdout="transcript\n", stderr="SECRET")
                with patch("scripts.v3.harness.providers.subprocess.run", return_value=completed) as spawned:
                    result = adapter.execute(REQUEST, allow_live=True)
                self.assertEqual(spawned.call_args.args[0], argv)
                self.assertTrue(result.live)
                self.assertEqual(result.text, "transcript\n")
                self.assertNotIn("SECRET", result.text)
                if stdin_text is None:
                    self.assertIs(spawned.call_args.kwargs["stdin"], subprocess.DEVNULL)
                    self.assertNotIn("input", spawned.call_args.kwargs)
                else:
                    self.assertEqual(spawned.call_args.kwargs["input"], stdin_text)

    def test_live_failure_omits_stderr(self) -> None:
        for adapter in (
            ClaudeHeadlessProvider(),
            CodexExecProvider(),
            GrokHeadlessProvider(),
            GeminiHeadlessProvider(),
            CursorHeadlessProvider(),
            OpenCodeHeadlessProvider(),
        ):
            with self.subTest(adapter=adapter.name):
                completed = subprocess.CompletedProcess(args=[], returncode=7, stdout="", stderr="SECRET-TOKEN")
                with patch("scripts.v3.harness.providers.subprocess.run", return_value=completed):
                    with self.assertRaises(HarnessError) as caught:
                        adapter.execute(REQUEST, allow_live=True)
                message = str(caught.exception)
                self.assertIn("exited 7", message)
                self.assertNotIn("SECRET-TOKEN", message)

    def test_config_matches_adapter_classes_and_rejects_secrets(self) -> None:
        config = load_config()
        by_name = {item["name"]: item for item in config["providers"]}
        self.assertEqual(
            list(by_name),
            ["fixture", "claude", "codex", "grok", "gemini", "cursor", "opencode"],
        )
        self.assertEqual(by_name["codex"]["argv"], ["codex", "exec", "--json"])
        self.assertEqual(by_name["grok"]["argv"], ["grok", "-p", "--output-format", "streaming-json"])
        self.assertEqual(by_name["gemini"]["argv"], ["gemini", "-p", "--output-format", "stream-json"])
        self.assertEqual(by_name["cursor"]["argv"], ["cursor-agent", "-p", "--output-format", "stream-json"])
        self.assertEqual(by_name["opencode"]["argv"], ["opencode", "run", "--format", "json"])
        self.assertFalse(by_name["gemini"]["enabled"])
        self.assertFalse(by_name["cursor"]["enabled"])
        self.assertFalse(by_name["opencode"]["enabled"])
        self.assertEqual(config["routing"]["retries"], 1)
        raw = json.loads((ROOT / "config" / "harness.json").read_text(encoding="utf-8"))
        raw["api_key"] = "nope"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "harness.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaises(HarnessError) as caught:
                load_config(path)
        self.assertIn("api_key", str(caught.exception))

    def test_capability_order_skips_providers_that_lack_the_capability(self) -> None:
        config = load_config()
        self.assertEqual(
            select_candidates(config, extra_capabilities=["subscription"]),
            ["claude", "codex", "grok"],
        )
        self.assertEqual(select_candidates(config, extra_capabilities=["jsonl"]), ["codex"])
        self.assertEqual(select_candidates(config, extra_capabilities=["streaming-json"]), ["grok"])
        self.assertEqual(
            select_candidates(config, provider="grok", extra_capabilities=["subscription"], fallback=True),
            ["grok", "claude", "codex"],
        )
        for item in config["providers"]:
            if item["name"] == "fixture":
                item["enabled"] = False
        self.assertEqual(select_candidates(config), ["claude", "codex", "grok"])
        with self.assertRaises(HarnessError):
            select_candidates(load_config(), provider="fixture", extra_capabilities=["subscription"])

    def test_retry_then_fallback(self) -> None:
        primary = ScriptedProvider(1)
        secondary = ScriptedProvider(0)
        opened = {"primary": primary, "secondary": secondary}
        sink = StringIO()
        result, attempts = execute_with_policy(
            REQUEST,
            ["primary", "secondary"],
            allow_live=False,
            retries=1,
            log=JsonLog([sink]),
            open_adapter=opened.get,
        )
        self.assertEqual(result.text, "ok")
        self.assertEqual(primary.calls, 2)
        self.assertEqual(secondary.calls, 0)
        self.assertEqual([item["ok"] for item in attempts], [False, True])
        events = [json.loads(line)["event"] for line in sink.getvalue().splitlines()]
        self.assertEqual(events, ["provider.attempt", "provider.failed", "provider.attempt", "provider.result"])

        primary = ScriptedProvider(2)
        secondary = ScriptedProvider(0)
        opened = {"primary": primary, "secondary": secondary}
        result, attempts = execute_with_policy(
            REQUEST,
            ["primary", "secondary"],
            allow_live=False,
            retries=1,
            log=JsonLog([StringIO()]),
            open_adapter=opened.get,
        )
        self.assertEqual(primary.calls, 2)
        self.assertEqual(secondary.calls, 1)
        self.assertEqual(result.provider, "scripted")
        self.assertEqual([item["provider"] for item in attempts], ["primary", "primary", "secondary"])

        primary = ScriptedProvider(3)
        with self.assertRaises(HarnessError) as caught:
            execute_with_policy(
                REQUEST,
                ["primary"],
                allow_live=False,
                retries=1,
                open_adapter=lambda name: primary,
            )
        self.assertIn("no provider completed", str(caught.exception))
        self.assertEqual(primary.calls, 2)

    def test_cli_plan_and_status_do_not_spawn(self) -> None:
        stdout = StringIO()
        stderr = StringIO()
        with patch("sys.stdout", stdout), patch("sys.stderr", stderr), patch(
            "scripts.v3.harness.providers.subprocess.run"
        ) as spawned:
            code = main(["plan", "--task", "Plan only."])
        spawned.assert_not_called()
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["planning"]["accepted"], 7)
        self.assertEqual(payload["route"]["selected_route_id"], "route-a")
        self.assertNotIn("execution", payload)
        events = [json.loads(line)["event"] for line in stderr.getvalue().splitlines() if line.startswith("{")]
        self.assertEqual(events, ["plan.admitted", "route.selected"])

        stdout = StringIO()
        with patch("sys.stdout", stdout), patch("scripts.v3.harness.providers.subprocess.run") as spawned:
            code = main(["status"])
        spawned.assert_not_called()
        self.assertEqual(code, 0)
        status = json.loads(stdout.getvalue())
        names = [item["name"] for item in status["providers"]]
        self.assertEqual(names, ["fixture", "claude", "codex", "grok", "gemini", "cursor", "opencode"])
        self.assertEqual(status["log"]["events"], 0)

    def test_cli_run_uses_fixture_then_falls_back_without_a_process(self) -> None:
        stdout = StringIO()
        with patch("sys.stdout", stdout), patch("sys.stderr", StringIO()), patch(
            "scripts.v3.harness.providers.subprocess.run"
        ) as spawned:
            code = main(["run", "--task", "Run the fixture."])
        spawned.assert_not_called()
        self.assertEqual(code, 2)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["status"], "unreviewed")
        self.assertEqual(payload["execution"]["provider"], "fixture")
        self.assertEqual(payload["candidates"], ["fixture", "claude", "codex", "grok"])
        self.assertFalse(payload["execution"]["live"])
        self.assertEqual(payload["route"]["selected_route_id"], "route-a")
        _drop_run_branches(payload["run_id"])

        stderr = StringIO()
        with patch("sys.stderr", stderr), patch("scripts.v3.harness.providers.subprocess.run") as spawned:
            code = main(["run", "--task", "Need a subscription.", "--capability", "subscription"])
        spawned.assert_not_called()
        self.assertEqual(code, 2)
        events = [json.loads(line) for line in stderr.getvalue().splitlines() if line.startswith("{")]
        failed = [item for item in events if item["event"] == "provider.failed"]
        self.assertEqual([item["provider"] for item in failed], ["claude", "claude", "codex", "codex", "grok", "grok"])
        self.assertTrue(all(item["error"] == "LiveProviderDisabled" for item in failed))
        self.assertEqual(events[-1]["event"], "run.refused")
        self.assertNotIn("SECRET", stderr.getvalue())
        leftover = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/recursion"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(leftover.stdout.strip(), "")

    def test_status_reads_a_log_and_the_entrypoint_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "harness.jsonl"
            with path.open("w", encoding="utf-8") as handle:
                JsonLog([handle]).event("run.completed", provider="fixture", live=False)
            stdout = StringIO()
            with patch("sys.stdout", stdout):
                code = main(["status", "--log", str(path)])
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["log"]["events"], 1)
            self.assertEqual(payload["log"]["last_event"], "run.completed")
            self.assertEqual(read_events(path)[0]["provider"], "fixture")
            path.write_text("{}\n", encoding="utf-8")
            with self.assertRaises(HarnessError):
                read_events(path)

        completed = subprocess.run(
            [sys.executable, "-X", "utf8", "-B", str(ROOT / "scripts" / "recursion"), "status"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        status = json.loads(completed.stdout)
        self.assertEqual(
            status["routing"]["preference"],
            ["fixture", "claude", "codex", "grok", "gemini", "cursor", "opencode"],
        )


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
        print("HARNESS_ADAPTERS_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

#!/usr/bin/env python3
"""Opt-in doctor --live. These tests never start a provider CLI."""

from __future__ import annotations

import json
import shutil
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

from scripts.v3.harness.cli import main  # noqa: E402
from scripts.v3.harness.config import load_config  # noqa: E402
from scripts.v3.harness.errors import HarnessError  # noqa: E402
from scripts.v3.harness.providers import ProviderResult  # noqa: E402
from scripts.v3.harness.smoke import LIVE_PROMPT, make_smoke_repo, smoke_live  # noqa: E402


def _row(name: str, **overrides) -> dict:
    base = {
        "auth_method": None,
        "command": name,
        "enabled": True,
        "installed": True,
        "name": name,
        "resolved": f"/bin/{name}",
        "signed_in": "signed-in",
        "usable": True,
        "version": "1",
    }
    base.update(overrides)
    return base


class SmokeTests(unittest.TestCase):
    def test_live_refuses_ci_before_any_prompt(self) -> None:
        def explode(*_args, **_kwargs):
            raise AssertionError("execute was called")

        for key in ("CI", "GITHUB_ACTIONS"):
            with self.subTest(key=key):
                with self.assertRaises(HarnessError) as caught:
                    smoke_live(load_config(), environ={key: "true"}, execute=explode, diagnose_fn=explode)
                self.assertIn("does not run in CI", str(caught.exception))

    def test_only_enabled_signed_in_providers_are_prompted(self) -> None:
        report = {
            "git": {"available": True, "longpaths": None, "version": "git"},
            "ok": True,
            "providers": [
                _row("fixture", signed_in="not-applicable", command="fixture-provider"),
                _row("claude"),
                _row("codex", installed=False, signed_in="unknown", resolved=None),
                _row("grok", enabled=False, usable=False),
                _row("gemini", signed_in="signed-out"),
            ],
        }
        calls: list[tuple[str, str, str]] = []

        def execute(name, request, timeout):
            calls.append((name, request.task, request.cwd))
            self.assertEqual(timeout, 120)
            self.assertTrue(Path(request.cwd).is_dir())
            return ProviderResult(
                provider=name,
                argv=(name,),
                text='{"type":"result","result":"pong","is_error":false}\n',
                live=True,
            )

        payload = smoke_live(
            load_config(),
            environ={},
            diagnose_fn=lambda _config: report,
            execute=execute,
            make_repo=lambda: Path(tempfile.mkdtemp(prefix="recursion-smoke-test-")),
        )
        self.assertEqual([item[0] for item in calls], ["claude"])
        self.assertEqual(calls[0][1], LIVE_PROMPT)
        self.assertFalse(Path(calls[0][2]).exists())
        by_name = {item["name"]: item for item in payload["live"]}
        self.assertEqual(by_name["fixture"]["reason"], "not-a-cli")
        self.assertEqual(by_name["codex"]["reason"], "not-installed")
        self.assertEqual(by_name["grok"]["reason"], "disabled")
        self.assertEqual(by_name["gemini"]["reason"], "not-signed-in")
        self.assertEqual(by_name["claude"]["status"], "ran")
        self.assertTrue(by_name["claude"]["ok"])
        self.assertEqual(by_name["claude"]["text"], "pong")
        self.assertTrue(payload["live_ok"])
        self.assertIsNone(by_name["fixture"]["text"])

    def test_a_failed_prompt_clears_live_ok_without_raw_stdout(self) -> None:
        report = {
            "git": {"available": True, "longpaths": None, "version": "git"},
            "ok": True,
            "providers": [_row("claude")],
        }

        def execute(name, request, timeout):
            del name, request, timeout
            raise HarnessError("claude authentication expired")

        payload = smoke_live(
            load_config(),
            environ={},
            diagnose_fn=lambda _config: report,
            execute=execute,
            make_repo=lambda: Path(tempfile.mkdtemp(prefix="recursion-smoke-test-")),
        )
        row = payload["live"][0]
        self.assertFalse(row["ok"])
        self.assertFalse(payload["live_ok"])
        self.assertIn("authentication expired", row["error"])
        self.assertIsNone(row["text"])

    def test_smoke_repo_commits_without_touching_global_git_config(self) -> None:
        before = subprocess.run(
            ["git", "config", "--global", "--get", "user.name"],
            capture_output=True,
            text=True,
            check=False,
        )
        repo = make_smoke_repo()
        try:
            author = subprocess.run(
                ["git", "log", "-1", "--format=%an <%ae>"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(author.stdout.strip(), "recursion <recursion@localhost>")
            self.assertTrue((repo / "README.md").is_file())
        finally:
            shutil.rmtree(repo, ignore_errors=True)
        after = subprocess.run(
            ["git", "config", "--global", "--get", "user.name"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(before.stdout, after.stdout)
        self.assertEqual(before.returncode, after.returncode)

    def test_doctor_without_live_does_not_prompt_and_live_failure_exits_1(self) -> None:
        diagnosed = {"ok": True, "git": {"available": True}, "providers": []}
        with patch("scripts.v3.harness.cli.diagnose", return_value=diagnosed) as doctor, patch(
            "scripts.v3.harness.smoke.smoke_live"
        ) as smoked:
            stdout = StringIO()
            with patch("sys.stdout", stdout):
                code = main(["doctor"])
        self.assertEqual(code, 0)
        doctor.assert_called_once()
        smoked.assert_not_called()
        self.assertNotIn("live", json.loads(stdout.getvalue()))

        with patch(
            "scripts.v3.harness.smoke.smoke_live",
            return_value={"ok": True, "live_ok": False, "live": [], "git": {}, "providers": []},
        ) as smoked:
            stdout = StringIO()
            with patch("sys.stdout", stdout):
                code = main(["doctor", "--live"])
        self.assertEqual(code, 1)
        smoked.assert_called_once()
        self.assertFalse(json.loads(stdout.getvalue())["live_ok"])


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_SMOKE_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

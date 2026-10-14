#!/usr/bin/env python3
"""Opt-in live smokes. Skipped unless RECURSION_LIVE=1 and the CLI is on PATH.

CI sets ``CI`` or ``GITHUB_ACTIONS``. Those runs never start a provider process,
even if ``RECURSION_LIVE`` is also set.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.doctor import live_requested  # noqa: E402
from scripts.v3.harness.providers import (  # noqa: E402
    CursorHeadlessProvider,
    GeminiHeadlessProvider,
    OpenCodeHeadlessProvider,
    ProviderRequest,
)
from scripts.v3.harness.usage import parse_usage  # noqa: E402


REQUEST = ProviderRequest(task="Reply with the single word pong.", packet_id="PACKET-LIVE", route_id="route-a")


class LiveGateTests(unittest.TestCase):
    def test_live_smoke_stays_off_in_ci_and_without_the_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "gemini"
            binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            binary.chmod(0o755)
            base = {"PATH": directory, "RECURSION_LIVE": "1"}
            self.assertFalse(live_requested("gemini", environ={**base, "CI": "true"}, platform="linux"))
            self.assertFalse(live_requested("gemini", environ={**base, "GITHUB_ACTIONS": "true"}, platform="linux"))
            self.assertFalse(live_requested("gemini", environ={"PATH": directory}, platform="linux"))
            self.assertTrue(live_requested("gemini", environ=base, platform="linux"))
            self.assertFalse(os.environ.get("RECURSION_LIVE") == "1" and bool(os.environ.get("CI")))


class LiveSmokeTests(unittest.TestCase):
    def test_gemini_smoke(self) -> None:
        if not live_requested("gemini"):
            self.skipTest("set RECURSION_LIVE=1 and install gemini; never runs in CI")
        result = GeminiHeadlessProvider().execute(REQUEST, allow_live=True, timeout_seconds=180)
        self._assert_stream(result.text)

    def test_cursor_smoke(self) -> None:
        if not live_requested("cursor-agent"):
            self.skipTest("set RECURSION_LIVE=1 and install cursor-agent; never runs in CI")
        result = CursorHeadlessProvider().execute(REQUEST, allow_live=True, timeout_seconds=180)
        self._assert_stream(result.text)

    def test_opencode_smoke(self) -> None:
        if not live_requested("opencode"):
            self.skipTest("set RECURSION_LIVE=1 and install opencode; never runs in CI")
        result = OpenCodeHeadlessProvider().execute(REQUEST, allow_live=True, timeout_seconds=180)
        self._assert_stream(result.text)

    def _assert_stream(self, text: str) -> None:
        self.assertTrue(text.strip())
        usage = parse_usage(text)
        for key in ("cost", "input_tokens", "output_tokens"):
            value = usage[key]
            self.assertTrue(value is None or isinstance(value, (int, float)))
            self.assertFalse(isinstance(value, bool))


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_LIVE_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

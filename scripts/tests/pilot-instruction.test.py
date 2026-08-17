#!/usr/bin/env python3
"""Adversarial controls for the shared Phase-8 Lucas instruction grammar."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pilot_instruction import require_affirmative_command  # noqa: E402


class PilotInstructionTest(unittest.TestCase):
    def assert_allowed(self, body: str, verb: str, terms: list[str]) -> None:
        require_affirmative_command(body, verb, terms)

    def assert_refused(self, body: str, verb: str, terms: list[str]) -> None:
        with self.assertRaises(ValueError):
            require_affirmative_command(body, verb, terms)

    def test_reviewed_natural_commands_are_allowed(self):
        digest = "a" * 64
        self.assert_allowed(
            f"Approve pilot plan plan-gsc-v2 with digest {digest}.",
            "pilot-plan-approve", ["plan-gsc-v2", digest])
        self.assert_allowed(
            "Open pilot window window-gsc-pilot-2 for goal goal-gsc-v2 for 14400 seconds.",
            "pilot-window-open", ["goal-gsc-v2", "window-gsc-pilot-2", "14400"])
        self.assert_allowed(
            "Close pilot window window-gsc-pilot-1 in golden-stallion-client",
            "pilot-window-close", ["window-gsc-pilot-1"])
        self.assert_allowed(
            "Authorize goal-gsc-v2 chiron-window-close 900",
            "pilot-window-open", ["goal-gsc-v2", "chiron-window-close", "900"])
        self.assert_allowed(
            "Close pilot window chiron-window-open",
            "pilot-window-close", ["chiron-window-open"])
        self.assert_allowed(
            f"Approve pilot plan reject-plan with digest {digest}",
            "pilot-plan-approve", ["reject-plan", digest])

    def test_project_named_window_command_binds_every_authority_value(self):
        body = (
            "Open pilot window window-gsc-pilot-5 for golden-stallion-client, "
            "goal goal-gsc-0x6c-shadetops-underemission-v2, for 14400 seconds."
        )
        terms = [
            "golden-stallion-client",
            "goal-gsc-0x6c-shadetops-underemission-v2",
            "window-gsc-pilot-5",
            "14400",
        ]
        self.assert_allowed(body, "pilot-window-open", terms)
        self.assert_refused(
            body,
            "pilot-window-open",
            ["chiron", terms[1], terms[2], terms[3]],
        )
        self.assert_refused(
            "For golden-stallion-client: Open pilot window window-gsc-pilot-5 "
            "for goal goal-gsc-0x6c-shadetops-underemission-v2 for 14400 seconds.",
            "pilot-window-open",
            ["chiron", terms[1], terms[2], terms[3]],
        )
        self.assert_refused(
            "Do not " + body[0].lower() + body[1:],
            "pilot-window-open",
            terms,
        )
        self.assert_refused(
            body + " Then close it.",
            "pilot-window-open",
            terms,
        )
        self.assert_allowed(
            "Open pilot window window-gsc-pilot-5 for goal "
            "goal-gsc-0x6c-shadetops-underemission-v2 for 14400 seconds.",
            "pilot-window-open",
            terms,
        )
        self.assert_allowed(
            "Open pilot window window-gsc-pilot-5 for goal "
            "goal-gsc-0x6c-shadetops-underemission-v2 for 14400 seconds.",
            "pilot-window-open",
            terms[1:],
        )
        self.assert_allowed(
            "Open pilot window window-gsc-pilot-5 for chiron-window-close, "
            "goal goal-gsc-0x6c-shadetops-underemission-v2, for 14400 seconds.",
            "pilot-window-open",
            ["chiron-window-close", terms[1], terms[2], terms[3]],
        )

    def test_negated_reversed_or_reordered_commands_are_refused(self):
        digest = "b" * 64
        cases = (
            (f"Do not approve plan-gsc-v2 {digest}", "pilot-plan-approve",
             ["plan-gsc-v2", digest]),
            (f"Reject plan-gsc-v2 {digest}", "pilot-plan-approve",
             ["plan-gsc-v2", digest]),
            ("Authorize window-gsc-pilot-2 goal-gsc-v2 14400", "pilot-window-open",
             ["goal-gsc-v2", "window-gsc-pilot-2", "14400"]),
            ("Close window-gsc-pilot-2", "pilot-window-open",
             ["goal-gsc-v2", "window-gsc-pilot-2", "14400"]),
            ("Authorize goal-gsc-v2 chiron-window-close 900 then close it", "pilot-window-open",
             ["goal-gsc-v2", "chiron-window-close", "900"]),
            ("Authorize goal-gsc-v2 chiron-window-close 900 then re-close it", "pilot-window-open",
             ["goal-gsc-v2", "chiron-window-close", "900"]),
            ("Authorize goal-gsc-v2 win-900 900 do-not close", "pilot-window-open",
             ["goal-gsc-v2", "win-900", "900"]),
            ("Authorize goal-gsc-v2 win-900 900 close2", "pilot-window-open",
             ["goal-gsc-v2", "win-900", "900"]),
            ("Authorize goal-gsc-v2 win-900 900 then reclose it", "pilot-window-open",
             ["goal-gsc-v2", "win-900", "900"]),
            ("Authorize goal-gsc-v2 win-900 900 then shut it", "pilot-window-open",
             ["goal-gsc-v2", "win-900", "900"]),
            ("Open window-gsc-pilot-1", "pilot-window-close", ["window-gsc-pilot-1"]),
            ("Close pilot window chiron-window-open then open it", "pilot-window-close",
             ["chiron-window-open"]),
            ("Close pilot window chiron-window-open then re-open it", "pilot-window-close",
             ["chiron-window-open"]),
            ("Close pilot window win-900 after chiron-window-open", "pilot-window-close",
             ["win-900"]),
            ("Close pilot window win-900 then reopen it", "pilot-window-close",
             ["win-900"]),
            ("Close pilot window win-900 then open's it", "pilot-window-close",
             ["win-900"]),
            (f"Approve pilot plan reject-plan with digest {digest} then reject-it",
             "pilot-plan-approve", ["reject-plan", digest]),
            (f"Approve pilot plan reject-plan with digest {digest} then reject's it",
             "pilot-plan-approve", ["reject-plan", digest]),
            (f"Approve pilot plan reject-plan with digest {digest} then denial",
             "pilot-plan-approve", ["reject-plan", digest]),
            (f"Don\u2019t approve pilot plan reject-plan with digest {digest}",
             "pilot-plan-approve", ["reject-plan", digest]),
        )
        for body, verb, terms in cases:
            with self.subTest(body=body):
                self.assert_refused(body, verb, terms)


if __name__ == "__main__":
    unittest.main(verbosity=2)

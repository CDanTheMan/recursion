#!/usr/bin/env python3
"""Parse checked-in headless transcripts. No live provider process.

The lines follow published and captured event shapes: Claude stream-json,
Codex jsonl, Grok streaming-json, Gemini stream-json, Cursor stream-json,
and OpenCode ``run --format json``. A missing usage or cost figure stays
unknown.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.errors import HarnessError  # noqa: E402
from scripts.v3.harness.streams import parse_transcript  # noqa: E402
from scripts.v3.harness.usage import empty_usage, parse_usage  # noqa: E402


def _load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class StreamTests(unittest.TestCase):
    def test_claude_result_is_the_assistant_text(self) -> None:
        parsed = parse_transcript("claude", _load("claude-stream.jsonl"))
        self.assertEqual(parsed["text"], "pong")
        self.assertNotIn("read", parsed["text"])
        self.assertEqual(parsed["usage"]["input_tokens"], 12)
        self.assertEqual(parsed["usage"]["output_tokens"], 3)
        self.assertEqual(parsed["usage"]["cost"], 0.01)

    def test_claude_api_error_message_is_not_the_fallback_text(self) -> None:
        text = "\n".join(
            (
                '{"type":"assistant","is_api_error_message":true,"error":"authentication_failed",'
                '"message":{"content":[{"type":"text","text":"Not logged in"}]}}',
            )
        )
        parsed = parse_transcript("claude", text)
        self.assertEqual(parsed["text"], "")

    def test_codex_agent_message_skips_command_output(self) -> None:
        parsed = parse_transcript("codex", _load("codex-stream.jsonl"))
        self.assertEqual(parsed["text"], "pong")
        self.assertNotIn("TOOL_OUTPUT_MARKER", parsed["text"])
        self.assertEqual(parsed["usage"]["input_tokens"], 20)
        self.assertEqual(parsed["usage"]["output_tokens"], 4)
        self.assertIsNone(parsed["usage"]["cost"])

    def test_grok_text_events_skip_thoughts_and_tool_output(self) -> None:
        parsed = parse_transcript("grok", _load("grok-stream.jsonl"))
        self.assertEqual(parsed["text"], "Here's a summary")
        self.assertNotIn("Analyzing", parsed["text"])
        self.assertNotIn("main.rs", parsed["text"])
        self.assertEqual(parsed["usage"]["input_tokens"], 812)
        self.assertEqual(parsed["usage"]["output_tokens"], 45)
        self.assertIsNone(parsed["usage"]["cost"])

    def test_gemini_stats_keep_a_known_zero_cache_and_an_unknown_cost(self) -> None:
        parsed = parse_transcript("gemini", _load("gemini-stream.jsonl"))
        self.assertEqual(parsed["text"], "Hello from Gemini.")
        self.assertNotIn("TOOL_OUTPUT_MARKER", parsed["text"])
        self.assertEqual(parsed["usage"]["input_tokens"], 50)
        self.assertEqual(parsed["usage"]["output_tokens"], 30)
        self.assertIsNone(parsed["usage"]["cost"])
        self.assertEqual(parsed["usage"]["input_tokens"], 50)

    def test_gemini_without_stats_stays_unknown(self) -> None:
        parsed = parse_transcript("gemini", _load("gemini-stream-no-usage.jsonl"))
        self.assertEqual(parsed["text"], "Hello from Gemini.")
        self.assertEqual(parsed["usage"], empty_usage())

    def test_cursor_usage_is_camel_case_and_cost_stays_unknown(self) -> None:
        parsed = parse_transcript("cursor", _load("cursor-stream.jsonl"))
        self.assertEqual(parsed["text"], "Hello from Cursor.")
        self.assertNotIn("TOOL_OUTPUT_MARKER", parsed["text"])
        self.assertEqual(parsed["usage"]["input_tokens"], 5749)
        self.assertEqual(parsed["usage"]["output_tokens"], 25)
        self.assertIsNone(parsed["usage"]["cost"])

    def test_cursor_without_usage_stays_unknown(self) -> None:
        parsed = parse_transcript("cursor", _load("cursor-stream-no-usage.jsonl"))
        self.assertEqual(parsed["text"], "Hello from Cursor.")
        self.assertEqual(parsed["usage"], empty_usage())

    def test_opencode_step_finish_reads_tokens_and_cost(self) -> None:
        parsed = parse_transcript("opencode", _load("opencode-stream.jsonl"))
        self.assertEqual(parsed["text"], "Hello from OpenCode.")
        self.assertNotIn("TOOL_OUTPUT_MARKER", parsed["text"])
        self.assertEqual(parsed["usage"]["input_tokens"], 13174)
        self.assertEqual(parsed["usage"]["output_tokens"], 11)
        self.assertEqual(parsed["usage"]["cost"], 0.0019827)

    def test_captured_opencode_pong_keeps_a_reported_zero_cost(self) -> None:
        parsed = parse_transcript("opencode", _load("opencode-stream-captured.jsonl"))
        self.assertEqual(parsed["text"], "pong")
        self.assertEqual(parsed["usage"]["input_tokens"], 105)
        self.assertEqual(parsed["usage"]["output_tokens"], 3)
        self.assertEqual(parsed["usage"]["cost"], 0.0)
        self.assertIsNotNone(parsed["usage"]["cost"])

    def test_opencode_without_step_finish_stays_unknown(self) -> None:
        parsed = parse_transcript("opencode", _load("opencode-stream-no-usage.jsonl"))
        self.assertEqual(parsed["text"], "Hello from OpenCode.")
        self.assertEqual(parsed["usage"], empty_usage())

    def test_opencode_steps_sum_and_a_reported_zero_stays_zero(self) -> None:
        summed = "\n".join(
            (
                '{"type":"step_finish","part":{"type":"step-finish","tokens":{"input":10,"output":1},"cost":0.2}}',
                '{"type":"step_finish","part":{"type":"step-finish","tokens":{"input":4,"output":2}}}',
            )
        )
        parsed = parse_usage(summed)
        self.assertEqual(parsed["input_tokens"], 14)
        self.assertEqual(parsed["output_tokens"], 3)
        self.assertEqual(parsed["cost"], 0.2)
        zero = '{"type":"step_finish","part":{"type":"step-finish","tokens":{"input":0,"output":2},"cost":0}}'
        parsed = parse_usage(zero)
        self.assertEqual(parsed["input_tokens"], 0)
        self.assertEqual(parsed["output_tokens"], 2)
        self.assertEqual(parsed["cost"], 0.0)
        self.assertIsNotNone(parsed["cost"])

    def test_a_broken_line_is_refused(self) -> None:
        with self.assertRaises(HarnessError):
            parse_transcript("gemini", '{"type":"message","role":"assistant","content":"Hi"}\nnot-json\n')


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_STREAMS_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

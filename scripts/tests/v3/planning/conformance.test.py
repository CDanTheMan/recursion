#!/usr/bin/env python3
"""Execute every frozen M1A command, decode, and replay oracle twice."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT))

from scripts.v3.planning.replay.kernel import admit, genesis, replay  # noqa: E402
from scripts.v3.planning.validation.canonical import M1AError, decode  # noqa: E402


def _execute_case(case: dict) -> tuple[int, int, int]:
    state = genesis(case["genesis"])
    command_count = event_count = decode_count = 0
    for commands, receipts, expected_events in (
        (case["initial_commands"], case["initial_receipts"], case["initial_events"]),
        (case["commands"], case["expected_receipts"], case["expected_events"]),
    ):
        event_position = 0
        for command, expected_receipt in zip(commands, receipts, strict=True):
            prior = state
            state, events, receipt = admit(
                state, state["content_digest"], command,
                case["authority_fixtures"], case["policy_fixtures"],
            )
            expected_count = len(events)
            oracle_events = expected_events[event_position:event_position + expected_count]
            event_position += expected_count
            assert receipt == expected_receipt, command["command_id"]
            assert events == oracle_events, command["command_id"]
            if expected_receipt["disposition"] != "accepted":
                assert state == prior, command["command_id"]
            command_count += 1
            event_count += len(events)
        assert event_position == len(expected_events)
    assert state == case["expected_final_state"]
    assert state["content_digest"] == case["expected_final_digest"]

    for raw, expected in zip(
        case["decode_inputs"], case["expected_decode_failures"], strict=True
    ):
        try:
            decode(raw, expected["schema_epoch"])
        except M1AError as error:
            assert error.code == expected["primary_error"]
        else:
            raise AssertionError("invalid decode input was accepted")
        decode_count += 1

    for replay_case in case["replay_cases"]:
        try:
            projected = replay(
                case["genesis"], replay_case["event_inputs"], replay_case["commands"],
                replay_case["receipts"], replay_case["checkpoint"],
            )
            disposition, error, projection_digest = (
                "accepted", None, projected["content_digest"]
            )
        except M1AError as exception:
            disposition, error, projection_digest = "refused", exception.code, None
        assert disposition == replay_case["expected_disposition"], replay_case["replay_id"]
        assert error == replay_case["primary_error"], replay_case["replay_id"]
        assert projection_digest == replay_case["expected_projection_digest"], replay_case["replay_id"]
    return command_count, event_count, decode_count


def run_conformance() -> tuple[int, int, int, int]:
    totals = [0, 0, 0]
    case_count = 0
    for path in sorted(FIXTURE_DIR.glob("F-M1A-*.json")):
        bundle = json.loads(path.read_text(encoding="utf-8"))
        for case in bundle["cases"]:
            first = _execute_case(case)
            second = _execute_case(case)
            assert first == second
            totals = [left + right for left, right in zip(totals, first, strict=True)]
            case_count += 1
    return case_count, *totals


def main() -> int:
    cases, commands, events, decodes = run_conformance()
    print(
        f"M1A_CONFORMANCE_PASS cases={cases} commands={commands} "
        f"events={events} decode_failures={decodes} runs=2"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"M1A_CONFORMANCE_FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from error

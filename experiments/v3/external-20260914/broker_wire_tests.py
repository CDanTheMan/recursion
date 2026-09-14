#!/usr/bin/env python3
"""Supplemental literal known-answer conformance tests for the M1B broker wire.

Scope: each test hand-builds a ``BrokerTraceInput@1`` literal by deep-copying
the frozen F-M1B-020 fixture input, replays it through the frozen stdlib
``reference_oracle.replay_broker``, and compares the emitted
``BrokerTraceDecision@1`` against expectations derived from
docs/v3/M1B-WIRE-PROFILE.md. This is a supplemental regression set, not
JSON-schema validation and not a live protocol implementation.

Boundary: a wire ``accepted-reset`` decision means only that the trace's RESET
satisfied the profile's cursor/recovery rules. It does not install a snapshot,
authenticate store evidence, recover a process, or deliver product Stop; none
of those is exercised or proved here.

Gate: python3 -B experiments/v3/external-20260914/broker_wire_tests.py
Prints V3_BROKER_WIRE_PASS only when every case passes.
"""

from __future__ import annotations

import base64
import copy
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ORACLE_DIR = REPO_ROOT / "scripts" / "tests" / "v3" / "execution"
FIXTURE_PATH = ORACLE_DIR / "fixtures" / "F-M1B-020.json"

sys.path.insert(0, str(ORACLE_DIR))

import reference_oracle  # noqa: E402

BUNDLE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
FIXTURE_HELLO = BUNDLE["input"]["messages"][0]
FIXTURE_WELCOME = BUNDLE["input"]["messages"][1]

WORK_COUNTERS = ("launch_count", "model_turn_count", "actor_create_count", "effect_count")


def fresh_input() -> dict:
    return copy.deepcopy(BUNDLE["input"])


def patched(template: dict, **fields) -> dict:
    message = copy.deepcopy(template)
    message.update(fields)
    return message


def hello(**fields) -> dict:
    return patched(FIXTURE_HELLO, **fields)


def welcome(**fields) -> dict:
    return patched(FIXTURE_WELCOME, **fields)


def credit(byte_count: int, event_count: int) -> dict:
    return {
        "type": "CREDIT",
        "protocol_version": "m1b-broker/1",
        "client_id": "client-a",
        "stream_id": "stream-a",
        "daemon_epoch": 2,
        "bytes": byte_count,
        "events": event_count,
    }


def event(cursor: int, text: str, unit: str = "event") -> dict:
    return {
        "type": "EVENT",
        "protocol_version": "m1b-broker/1",
        "stream_id": "stream-a",
        "daemon_epoch": 2,
        "cursor": cursor,
        "cursor_unit": unit,
        "event_class": "output",
        "process_id": "proc-a",
        "payload_base64": base64.b64encode(text.encode("utf-8")).decode("ascii"),
        "payload_untrusted": True,
    }


def ack(cursor: int, unit: str = "event") -> dict:
    return {
        "type": "ACK",
        "protocol_version": "m1b-broker/1",
        "client_id": "client-a",
        "stream_id": "stream-a",
        "daemon_epoch": 2,
        "cursor": cursor,
        "cursor_unit": unit,
    }


def reset(snapshot_cursor: int, unit: str = "event") -> dict:
    return {
        "type": "RESET",
        "protocol_version": "m1b-broker/1",
        "client_id": "client-a",
        "stream_id": "stream-a",
        "daemon_epoch": 2,
        "reason": "gap",
        "snapshot_cursor": snapshot_cursor,
        "cursor_unit": unit,
    }


class BrokerWireConformanceTest(unittest.TestCase):
    """Literal traces; expectations are doc-derived, not oracle-copied."""

    def run_trace(self, messages: list, **overrides) -> tuple[dict, dict]:
        self.assertLessEqual(len(messages), 15)
        trace = fresh_input()
        trace.update(overrides)
        trace["messages"] = messages
        return trace, reference_oracle.replay_broker(trace)

    def expect(
        self,
        trace: dict,
        decision: dict,
        *,
        status: str,
        reasons: list,
        cursor: int,
        unit: str = "event",
        needs_reset: bool = False,
    ) -> None:
        self.assertEqual(decision["type"], "BrokerTraceDecision@1")
        self.assertEqual(decision["status"], status)
        self.assertEqual(decision["reasons"], sorted(reasons))
        self.assertEqual(decision["final_cursor"], cursor)
        self.assertEqual(decision["cursor_unit"], unit)
        self.assertEqual(decision["requires_reset"], needs_reset)
        for field in WORK_COUNTERS:
            self.assertEqual(decision[field], trace[field])

    def test_literal_fixture_unchanged(self) -> None:
        self.assertEqual(BUNDLE["type"], "BrokerFixtureBundle@1")
        self.assertEqual(BUNDLE["fixture_id"], "F-M1B-020")
        trace = fresh_input()
        decision = reference_oracle.replay_broker(trace)
        self.assertEqual(decision, BUNDLE["expected"])

    def test_event_cursor_contiguous(self) -> None:
        # Event-unit cursors advance by exactly one; skipping a cursor is
        # nonmonotonic even though the event still lands.
        trace, decision = self.run_trace(
            [
                hello(),
                welcome(),
                credit(8, 4),
                event(1, "A"),
                event(3, "B"),
            ]
        )
        self.expect(
            trace,
            decision,
            status="refused",
            reasons=["cursor-nonmonotonic"],
            cursor=3,
        )

    def test_utf8_bytes_count_decoded_e_acute(self) -> None:
        # utf8-byte cursors count decoded UTF-8 bytes: "e-acute" is one
        # character but two bytes, so the first event lands at cursor 2.
        trace, decision = self.run_trace(
            [
                hello(cursor_unit="utf8-byte"),
                welcome(cursor_unit="utf8-byte"),
                credit(8, 4),
                event(2, "\u00e9", unit="utf8-byte"),
                event(3, "A", unit="utf8-byte"),
            ]
        )
        self.expect(
            trace,
            decision,
            status="accepted",
            reasons=[],
            cursor=3,
            unit="utf8-byte",
        )

    def test_ack_does_not_grant_credit(self) -> None:
        # ACK releases pending bytes but grants no new credit: after the only
        # credit is consumed and acknowledged, a further event is exhausted.
        trace, decision = self.run_trace(
            [
                hello(),
                welcome(),
                credit(1, 1),
                event(1, "A"),
                ack(1),
                event(2, "B"),
            ]
        )
        self.expect(
            trace,
            decision,
            status="refused",
            reasons=["credit-exhausted"],
            cursor=2,
            needs_reset=True,
        )

    def test_ack_cannot_advance(self) -> None:
        # An ACK ahead of the delivered cursor is refused.
        trace, decision = self.run_trace(
            [
                hello(),
                welcome(),
                credit(2, 2),
                event(1, "A"),
                ack(2),
            ]
        )
        self.expect(
            trace,
            decision,
            status="refused",
            reasons=["ack-ahead"],
            cursor=1,
        )

    def test_ack_cannot_go_back(self) -> None:
        # ACK cursors cannot move backward below the acknowledged cursor.
        trace, decision = self.run_trace(
            [
                hello(),
                welcome(),
                credit(4, 4),
                event(1, "A"),
                event(2, "B"),
                ack(2),
                ack(1),
            ]
        )
        self.expect(
            trace,
            decision,
            status="refused",
            reasons=["cursor-nonmonotonic"],
            cursor=2,
        )

    def test_gap_requires_immediate_reset(self) -> None:
        # Once WELCOME detects a replay gap, RESET is the only permitted
        # continuation; an intervening message is a permanent
        # replay-gap-continuation refusal even though a later RESET still
        # recovers at the same cursor.
        trace, decision = self.run_trace(
            [
                hello(last_cursor=0),
                welcome(replay_floor=1, snapshot_cursor=5),
                credit(4, 4),
                reset(5),
            ]
        )
        self.expect(
            trace,
            decision,
            status="refused",
            reasons=["replay-gap", "replay-gap-continuation"],
            cursor=5,
            needs_reset=True,
        )

    def test_reset_requires_fresh_credit(self) -> None:
        # RESET clears credit, so the next EVENT before fresh CREDIT is
        # credit-missing and unrecovered.
        trace, decision = self.run_trace(
            [
                hello(),
                welcome(),
                credit(1, 1),
                event(1, "A"),
                event(2, "B"),
                reset(2),
                event(3, "C"),
            ]
        )
        self.expect(
            trace,
            decision,
            status="refused",
            reasons=["credit-exhausted", "credit-missing"],
            cursor=3,
            needs_reset=True,
        )

    def test_gap_reset_fresh_credit_accepts(self) -> None:
        # Positive recovery 1 of 2: gap detected, immediate RESET, fresh
        # CREDIT, then delivery resumes -> accepted-reset.
        trace, decision = self.run_trace(
            [
                hello(last_cursor=0),
                welcome(replay_floor=1, snapshot_cursor=5),
                reset(5),
                credit(4, 4),
                event(6, "A"),
                ack(6),
            ]
        )
        self.expect(
            trace,
            decision,
            status="accepted-reset",
            reasons=["replay-gap"],
            cursor=6,
            needs_reset=True,
        )

    def test_exhaustion_reset_fresh_credit_accepts(self) -> None:
        # Positive recovery 2 of 2: ordinary credit exhaustion, RESET, fresh
        # CREDIT, delivery resumes -> accepted-reset.
        trace, decision = self.run_trace(
            [
                hello(),
                welcome(),
                credit(1, 1),
                event(1, "A"),
                event(2, "B"),
                reset(2),
                credit(4, 4),
                event(3, "C"),
                ack(3),
            ]
        )
        self.expect(
            trace,
            decision,
            status="accepted-reset",
            reasons=["credit-exhausted"],
            cursor=3,
            needs_reset=True,
        )

    def test_attach_cannot_launch_work(self) -> None:
        # A view-only attach creates no work; a trace that arrives with a
        # nonzero semantic-work counter is refused and counters stay as
        # supplied (the wire creates nothing).
        trace, decision = self.run_trace(
            [hello(), welcome()],
            launch_count=1,
        )
        self.expect(
            trace,
            decision,
            status="refused",
            reasons=["attach-created-work"],
            cursor=0,
        )

    def test_stale_epoch_refuses(self) -> None:
        # A message stamped with a foreign daemon epoch is skipped and the
        # trace is refused.
        trace, decision = self.run_trace(
            [
                hello(),
                welcome(daemon_epoch=3),
            ]
        )
        self.expect(
            trace,
            decision,
            status="refused",
            reasons=["stale-daemon-epoch"],
            cursor=0,
        )

    def test_cursor_unit_bound_at_zero(self) -> None:
        # The cursor unit binds once at cursor zero (here to "event" by the
        # handshake); a later utf8-byte message is a unit mismatch and the
        # trace keeps the originally bound unit.
        trace, decision = self.run_trace(
            [
                hello(),
                welcome(),
                credit(4, 4),
                event(1, "A", unit="utf8-byte"),
            ]
        )
        self.expect(
            trace,
            decision,
            status="refused",
            reasons=["cursor-unit-mismatch"],
            cursor=1,
            unit="event",
        )


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BrokerWireConformanceTest)
    outcome = unittest.TextTestRunner(verbosity=1).run(suite)
    if not outcome.wasSuccessful():
        raise SystemExit(1)
    print("V3_BROKER_WIRE_PASS")

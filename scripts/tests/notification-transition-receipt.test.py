#!/usr/bin/env python3
"""Crash controls for Phase 7 canonical projection -> audit-journal receipts."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("notification_outbox_receipts", SCRIPTS / "notification-outbox.py")
outbox = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(outbox)

from jsonl_durable import read_jsonl_objects  # noqa: E402
from transition_receipt import (  # noqa: E402
    TransitionReceiptError,
    commit_event,
    commit_transition,
    fields_mutation,
    json_mutation,
    recover_transitions,
)


@contextmanager
def failpoint(name: str):
    prior = os.environ.get("RECURSION_TRANSITION_FAILPOINT")
    os.environ["RECURSION_TRANSITION_FAILPOINT"] = name
    try:
        yield
    finally:
        if prior is None:
            os.environ.pop("RECURSION_TRANSITION_FAILPOINT", None)
        else:
            os.environ["RECURSION_TRANSITION_FAILPOINT"] = prior


class NotificationReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        for relative in (
            "state/.locks", "state/deliveries", "state/notification-events",
            "state/reports", "state/recovery", "state/project-config", "state/pilots",
        ):
            (self.base / relative).mkdir(parents=True, exist_ok=True)
        self.destination = "project-topic:telegram:-1001:7"
        (self.base / "state/project-config/alpha.json").write_text(json.dumps({
            "id": "alpha", "pilot_id": "pilot-alpha", "status": "active",
            "notification_targets": [
                self.destination,
                "head-hermes:telegram:-1001:8",
                "lucas-direct:telegram:42",
            ],
        }) + "\n", encoding="utf-8")
        (self.base / "state/pilots/pilot-alpha.json").write_text(json.dumps({
            "id": "pilot-alpha", "project_id": "alpha", "status": "active",
            "notification_targets": [
                self.destination,
                "head-hermes:telegram:-1001:8",
                "lucas-direct:telegram:42",
            ],
        }) + "\n", encoding="utf-8")
        self.prior_actuation = os.environ.get("RECURSION_QUEUE_ACTUATION")
        os.environ["RECURSION_QUEUE_ACTUATION"] = "1"

    def tearDown(self) -> None:
        if self.prior_actuation is None:
            os.environ.pop("RECURSION_QUEUE_ACTUATION", None)
        else:
            os.environ["RECURSION_QUEUE_ACTUATION"] = self.prior_actuation
        self.temporary.cleanup()

    def assert_recovers_one(self, journal: str, state_path: Path, invoke) -> None:
        with failpoint("state-write"):
            with self.assertRaises(outbox.OutboxError):
                invoke()
        self.assertTrue(state_path.is_file(), "canonical state must commit before its event")
        self.assertFalse((self.base / journal).exists())
        self.assertEqual(recover_transitions(self.base)["projected"], 1)
        recover_transitions(self.base)
        rows = read_jsonl_objects(self.base / journal)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].get("id"))

    def test_delivery_record_recovers_delivery_event_once(self) -> None:
        record = {
            "schema_version": 1, "id": "delivery-one", "event_id": "event-one",
            "project_id": "alpha", "goal_id": "goal-alpha", "task_id": None,
            "destination": self.destination, "attempt": 0, "acknowledgement": None,
            "status": "pending", "next_attempt_at": 0, "max_attempts": 3,
            "backoff_seconds": 0, "last_error": None, "attempt_token": None,
            "receipt_path": None, "message_digest": "a" * 64,
            "created_at": "2026-08-10T00:00:00Z", "updated_at": "2026-08-10T00:00:00Z",
        }
        self.assert_recovers_one(
            "state/delivery-events.jsonl",
            self.base / "state/deliveries/delivery-one.json",
            lambda: outbox.write_delivery(self.base, record, "enqueued"),
        )

    def test_notification_projection_recovers_creation_event_once(self) -> None:
        event = {
            "id": "event-projection", "source_event_id": "source-projection",
            "event_type": "worker-launched", "project_id": "alpha",
            "goal_id": "goal-alpha", "task_id": "task-alpha",
            "occurred_at": "2026-08-10T00:00:00Z",
        }
        self.assert_recovers_one(
            "state/notification-event-events.jsonl",
            self.base / "state/notification-events/event-projection.json",
            lambda: outbox.create_event(self.base, event),
        )
        self.assertTrue(outbox.recovery_needed(self.base, "alpha", "goal-alpha"))
        outbox.recover(self.base, "alpha", "goal-alpha")
        deliveries = outbox.delivery_records(self.base, "alpha")
        self.assertEqual(len(deliveries), 1)
        self.assertEqual(deliveries[0][1]["event_id"], "event-projection")
        self.assertFalse(outbox.recovery_needed(self.base, "alpha", "goal-alpha"))

    def test_audit_report_recovers_audit_event_once(self) -> None:
        chain = {
            "instruction": {"id": "1", "record": {"id": "1"}},
            "plan": [{"id": "plan"}], "actions": [{"id": "action"}],
            "tasks": [{"id": "task"}], "workers": [{"id": "worker"}],
            "commits": [{"id": "commit"}], "gates": [{"id": "gate"}],
            "verifier": [{"id": "verify"}], "pilot_report": {"id": "pilot-report"},
            "head_report": {"id": "head-report"}, "review_branch": {"name": "review/x"},
            "delivery_acknowledgements": [{"id": "delivery"}], "_all_acknowledged": True,
        }
        original_chain = outbox.build_chain
        original_events = outbox.notification_events
        outbox.build_chain = lambda *_args: chain
        outbox.notification_events = lambda *_args: []
        try:
            self.assert_recovers_one(
                "state/notification-audit-events.jsonl",
                self.base / "state/reports/goal-alpha-audit.json",
                lambda: outbox.audit_goal(self.base, "alpha", "goal-alpha"),
            )
        finally:
            outbox.build_chain = original_chain
            outbox.notification_events = original_events

    def test_recovery_snapshot_recovers_recovery_event_once(self) -> None:
        self.assert_recovers_one(
            "state/notification-recovery-events.jsonl",
            self.base / "state/recovery/notification-alpha-goal-alpha.json",
            lambda: outbox.recover(self.base, "alpha", "goal-alpha"),
        )

    def test_open_quarantine_blocks_projection_and_recovery(self) -> None:
        quarantine = self.base / "state/jsonl-quarantine"
        quarantine.mkdir()
        (quarantine / "open.json").write_text(json.dumps({
            "schema_version": 1, "status": "open", "requires_human_review": True,
            "journal": "state/delivery-events.jsonl",
        }) + "\n", encoding="utf-8")
        record = {
            "schema_version": 1, "id": "delivery-quarantine", "event_id": "event-one",
            "project_id": "alpha", "destination": self.destination, "status": "pending",
            "attempt": 0, "message_digest": "b" * 64,
        }
        with self.assertRaises(outbox.OutboxError):
            outbox.write_delivery(self.base, record, "enqueued")
        self.assertFalse((self.base / "state/deliveries/delivery-quarantine.json").exists())
        self.assertFalse((self.base / "state/delivery-events.jsonl").exists())
        self.assertEqual(recover_transitions(self.base)["projected"], 0)

    def test_direct_append_reports_repaired_tail_as_failure(self) -> None:
        path = self.base / "state/direct-events.jsonl"
        path.write_bytes(b'{"id":"torn"')
        with self.assertRaises(outbox.OutboxError):
            outbox.append_jsonl(path, {"id": "committed"})
        evidence = list((self.base / "state/jsonl-quarantine").glob("*.json"))
        self.assertEqual(len(evidence), 1)
        self.assertEqual(json.loads(evidence[0].read_text())["status"], "open")

    def test_enqueued_decision_names_narrow_notification_authority(self) -> None:
        captured: dict = {}
        original = outbox.subprocess.run

        def fake_run(*args, **kwargs):
            captured.update(json.loads(kwargs["input"]))
            return subprocess.CompletedProcess(args[0], 0, "", "")

        outbox.subprocess.run = fake_run
        try:
            outbox.enqueue(
                self.base, "pilot-alpha", "notification-deliver",
                ["alpha", "delivery-one"], "goal-alpha", "fixture",
                ["delivery-one", "pending"],
            )
        finally:
            outbox.subprocess.run = original
        self.assertEqual(captured.get("decision_source"), "notification-reconciler")
        self.assertEqual(captured.get("routed_decider"), "pilot-alpha")
        self.assertEqual(captured.get("actor"), "pilot-alpha")

    def test_running_state_crash_is_dead_lettered_without_ambiguous_resend(self) -> None:
        event = outbox.create_event(self.base, {
            "id": "event-ambiguous", "source_event_id": "source-ambiguous",
            "event_type": "worker-launched", "project_id": "alpha",
            "goal_id": "goal-alpha", "task_id": "task-alpha",
            "occurred_at": "2026-08-10T00:00:00Z",
        })
        path, record = outbox.delivery_records(self.base, "alpha")[0]
        record.update({
            "status": "running", "attempt": 1, "attempt_token": "attempt-ambiguous",
            "attempt_started_at": "2026-08-10T00:00:01Z", "next_attempt_at": None,
        })
        with failpoint("state-write"):
            with self.assertRaises(outbox.OutboxError):
                outbox.write_delivery(self.base, record, "attempt-started")

        commands: list[list[str]] = []
        original = outbox.subprocess.run
        original_escalate = outbox.escalate
        original_open = outbox.escalation_is_open
        escalations: set[str] = set()

        def fake_run(command, *args, **kwargs):
            commands.append([str(item) for item in command])
            return subprocess.CompletedProcess(command, 0, "", "")

        outbox.subprocess.run = fake_run
        outbox.escalate = lambda _base, key, *_args: escalations.add(key)
        outbox.escalation_is_open = lambda _base, key: key in escalations
        try:
            outbox.deliver(self.base, "alpha", str(record["id"]))
        finally:
            outbox.subprocess.run = original
            outbox.escalate = original_escalate
            outbox.escalation_is_open = original_open
        current = outbox.read_json(path)
        notify_calls = [row for row in commands if any(item.endswith("notify.sh") for item in row)]
        self.assertEqual(notify_calls, [])
        self.assertEqual(current["status"], "dead-letter")
        self.assertEqual(current["last_error"], "prior attempt outcome is ambiguous and has no transport evidence")
        self.assertEqual(event["id"], current["event_id"])

    def test_goal_less_digest_projection_restart_materializes_only_missing_pair(self) -> None:
        message = "Bounded project digest"
        source = {
            "schema_version": 1, "id": "source-project-digest", "ts": "2026-08-10T01:00:00Z",
            "event": "project-digest", "project": "alpha", "goal": "", "task": "",
            "detail": {
                "message": message, "message_digest": __import__("hashlib").sha256(message.encode()).hexdigest(),
                "occurrence_date": "2026-08-10",
            },
        }
        (self.base / "state/events.jsonl").write_text(json.dumps(source) + "\n", encoding="utf-8")
        event = outbox.all_mapped(self.base, "alpha")[0]
        original_create_delivery = outbox.create_delivery
        outbox.create_delivery = lambda *_args: (_ for _ in ()).throw(outbox.OutboxError("fixture crash"))
        try:
            with self.assertRaises(outbox.OutboxError):
                outbox.create_event(self.base, event)
        finally:
            outbox.create_delivery = original_create_delivery
        self.assertTrue((self.base / f"state/notification-events/{event['id']}.json").is_file())
        self.assertEqual(len(read_jsonl_objects(self.base / "state/notification-event-events.jsonl")), 1)
        self.assertEqual(outbox.delivery_records(self.base, "alpha"), [])

        queued: list[tuple[str, list[str]]] = []
        original_enqueue = outbox.enqueue
        outbox.enqueue = lambda _base, _actor, verb, args, *_rest: queued.append((verb, args))
        try:
            outbox.schedule(self.base, "alpha")
        finally:
            outbox.enqueue = original_enqueue
        self.assertIn(("notification-reconcile", ["alpha", event["id"]]), queued)

        outbox.reconcile_event(self.base, "alpha", event["id"])
        outbox.reconcile_event(self.base, "alpha", event["id"])
        deliveries = outbox.delivery_records(self.base, "alpha")
        self.assertEqual(len(deliveries), 1)
        self.assertEqual(deliveries[0][1]["goal_id"], None)
        self.assertEqual(deliveries[0][1]["id"], outbox.stable_id("delivery", event["id"], self.destination))
        self.assertEqual(len(read_jsonl_objects(self.base / "state/delivery-events.jsonl")), 1)
        changed = dict(event)
        changed["source_event_id"] = "different-source"
        with self.assertRaises(outbox.OutboxError):
            outbox.create_event(self.base, changed)

    def test_routing_error_projection_restart_is_exact_and_delivery_free(self) -> None:
        targets = ["head-hermes:telegram:-1001:8", "lucas-direct:telegram:42"]
        for path in (self.base / "state/project-config/alpha.json",
                     self.base / "state/pilots/pilot-alpha.json"):
            value = json.loads(path.read_text(encoding="utf-8"))
            value["notification_targets"] = targets
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
        message = "Routing-error digest"
        event = {
            "id": "event-routing-error", "source_event_id": "source-routing-error",
            "event_type": "project-digest", "project_id": "alpha", "goal_id": "", "task_id": "",
            "occurred_at": "2026-08-10T02:00:00Z", "occurrence_date": "2026-08-10",
            "source": {"ts": "2026-08-10T02:00:00Z", "detail": {
                "message": message, "message_digest": __import__("hashlib").sha256(message.encode()).hexdigest(),
                "occurrence_date": "2026-08-10",
            }},
        }
        with failpoint("state-write"):
            with self.assertRaises(outbox.OutboxError):
                outbox.create_event(self.base, event)
        outbox.recover_notification_transitions(self.base)
        escalations: set[str] = set()
        original_escalate = outbox.escalate
        original_open = outbox.escalation_is_open
        outbox.escalate = lambda _base, key, *_args: escalations.add(key)
        outbox.escalation_is_open = lambda _base, key: key in escalations
        try:
            first = outbox.create_event(self.base, event)
            second = outbox.create_event(self.base, event)
        finally:
            outbox.escalate = original_escalate
            outbox.escalation_is_open = original_open
        self.assertTrue(first["routing_error"])
        self.assertEqual(first, second)
        self.assertEqual(len(escalations), 1)
        self.assertEqual(outbox.delivery_records(self.base, "alpha"), [])
        self.assertEqual(len(read_jsonl_objects(self.base / "state/notification-event-events.jsonl")), 1)

        for path in (self.base / "state/project-config/alpha.json",
                     self.base / "state/pilots/pilot-alpha.json"):
            value = json.loads(path.read_text(encoding="utf-8"))
            value["notification_targets"] = [self.destination, *targets]
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
        with self.assertRaises(outbox.OutboxError):
            outbox.create_event(self.base, event)

    def test_escalation_return_code_is_not_suppressed(self) -> None:
        original = outbox.subprocess.run
        outbox.subprocess.run = lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 19, "", "fixture taskctl failure")
        try:
            with self.assertRaisesRegex(outbox.OutboxError, "fixture taskctl failure"):
                outbox.escalate(self.base, "fixture-key", "fixture title", "state/fixture", "alpha")
        finally:
            outbox.subprocess.run = original

    def test_dead_letter_restart_repairs_escalation_and_attention_without_resend(self) -> None:
        event = outbox.create_event(self.base, {
            "id": "event-dead-repair", "source_event_id": "source-dead-repair",
            "event_type": "worker-launched", "project_id": "alpha",
            "goal_id": "goal-alpha", "task_id": "task-alpha",
            "occurred_at": "2026-08-10T03:00:00Z",
        })
        path, record = outbox.delivery_records(self.base, "alpha")[0]
        escalations: set[str] = set()
        escalation_attempts = 0
        attention_attempts = 0
        original_escalate = outbox.escalate
        original_open = outbox.escalation_is_open
        original_create = outbox.create_event

        def flaky_escalate(_base, key, *_args):
            nonlocal escalation_attempts
            escalation_attempts += 1
            if escalation_attempts == 1:
                raise outbox.OutboxError("fixture escalation crash")
            escalations.add(key)

        def flaky_create(base, value):
            nonlocal attention_attempts
            if value.get("event_type") == "delivery-dead-letter":
                attention_attempts += 1
                if attention_attempts == 1:
                    raise outbox.OutboxError("fixture attention crash")
            return original_create(base, value)

        outbox.escalate = flaky_escalate
        outbox.escalation_is_open = lambda _base, key: key in escalations
        outbox.create_event = flaky_create
        try:
            with self.assertRaisesRegex(outbox.OutboxError, "fixture escalation crash"):
                outbox.dead_letter(self.base, record, "fixture permanent failure")
            self.assertEqual(outbox.read_json(path)["status"], "dead-letter")
            self.assertTrue(outbox.dead_letter_reconciliation_needed(self.base, outbox.read_json(path)))
            with self.assertRaisesRegex(outbox.OutboxError, "fixture attention crash"):
                outbox.deliver(self.base, "alpha", record["id"])
            self.assertTrue(outbox.dead_letter_reconciliation_needed(self.base, outbox.read_json(path)))
            outbox.recover(self.base, "alpha", "goal-alpha")
            outbox.recover(self.base, "alpha", "goal-alpha")
        finally:
            outbox.escalate = original_escalate
            outbox.escalation_is_open = original_open
            outbox.create_event = original_create
        attention_id = outbox.stable_id("event", record["id"], "delivery-dead-letter")
        attention = [row for _, row in outbox.notification_events(self.base, "alpha")
                     if row.get("id") == attention_id]
        attention_deliveries = [row for _, row in outbox.delivery_records(self.base, "alpha")
                                if row.get("event_id") == attention_id]
        self.assertEqual(escalation_attempts, 2)
        self.assertGreaterEqual(attention_attempts, 2)
        self.assertEqual(len(attention), 1)
        self.assertEqual(len(attention_deliveries), 1)
        self.assertEqual(attention_deliveries[0]["status"], "pending")
        self.assertEqual(outbox.read_json(path)["status"], "dead-letter")
        self.assertEqual(event["id"], record["event_id"])

    def test_terminal_report_crash_is_reenqueued_and_repaired_exactly_once(self) -> None:
        goal_path = self.base / "state/goals/goal-alpha.md"
        goal_path.parent.mkdir(parents=True, exist_ok=True)
        goal_path.write_text(
            "schema_version: 1\nversion: 1\nid: goal-alpha\nproject_id: alpha\n"
            "pilot_id: pilot-alpha\nstatus: verifying\nterminal_reported: 0\n",
            encoding="utf-8",
        )
        source = {
            "schema_version": 1, "id": "source-terminal-repair", "ts": "2026-08-10T04:00:00Z",
            "event": "goal-transition", "project": "alpha", "goal": "goal-alpha", "task": "",
            "detail": {"from": "verifying", "to": "achieved", "reason": "verified", "version": 2},
        }
        commit_transition(
            self.base,
            [fields_mutation(goal_path, {
                "status": "achieved", "version": "2", "last_transition_from": "verifying",
                "last_transition_at": source["ts"], "last_transition_reason": "verified",
            })],
            source,
        )
        terminal = outbox.all_mapped(self.base, "alpha")[0]
        outbox.create_event(self.base, terminal)
        chain = {
            "instruction": {"id": "1", "record": {"id": "1"}}, "plan": [{"id": "plan"}],
            "plan_approval": [], "pilot_windows": [], "actions": [{"id": "action"}],
            "goal": {"id": "goal-alpha", "budget": '{"publication_required":true}'},
            "tasks": [{"id": "task"}], "workers": [{"id": "worker"}],
            "commits": [{"id": "commit"}], "gates": [{"id": "gate"}],
            "verifier": [{"id": "verify"}], "review_branch": {"name": "review/alpha"},
        }
        original_chain = outbox.build_chain
        original_create = outbox.create_event
        original_fsync_dir = outbox.fsync_dir
        if os.name == "nt":
            outbox.fsync_dir = lambda *_args: None
            self.addCleanup(setattr, outbox, "fsync_dir", original_fsync_dir)
        failed = False

        def fail_pilot_event(base, value):
            nonlocal failed
            if value.get("event_type") == "pilot-terminal-report" and not failed:
                failed = True
                raise outbox.OutboxError("fixture terminal event crash")
            return original_create(base, value)

        outbox.build_chain = lambda *_args: chain
        outbox.create_event = fail_pilot_event
        try:
            with self.assertRaisesRegex(outbox.OutboxError, "fixture terminal event crash"):
                outbox.create_terminal_reports(self.base, outbox.read_json(
                    self.base / f"state/notification-events/{terminal['id']}.json"))
        finally:
            outbox.create_event = original_create
        report_path = self.base / "state/reports/goal-alpha-pilot.json"
        created_at = outbox.read_json(report_path)["created_at"]
        self.assertTrue(outbox.event_reconciliation_needed(self.base, terminal))
        queued: list[tuple[str, list[str]]] = []
        original_enqueue = outbox.enqueue
        outbox.enqueue = lambda _base, _actor, verb, args, *_rest: queued.append((verb, args))
        try:
            outbox.schedule(self.base, "alpha")
        finally:
            outbox.enqueue = original_enqueue
        self.assertIn(("notification-reconcile", ["alpha", terminal["id"]]), queued)
        try:
            outbox.reconcile_event(self.base, "alpha", terminal["id"])
            outbox.reconcile_event(self.base, "alpha", terminal["id"])
        finally:
            outbox.build_chain = original_chain
        pilot_id = outbox.stable_id("event", "goal-alpha", "pilot-terminal-report")
        pilot = [row for _, row in outbox.notification_events(self.base, "alpha") if row.get("id") == pilot_id]
        pilot_deliveries = [row for _, row in outbox.delivery_records(self.base, "alpha")
                            if row.get("event_id") == pilot_id]
        self.assertEqual(outbox.read_json(report_path)["created_at"], created_at)
        self.assertEqual(len(pilot), 1)
        self.assertEqual(len(pilot_deliveries), 1)
        self.assertFalse(outbox.event_reconciliation_needed(self.base, terminal))

    def test_audit_fingerprint_excludes_only_its_derived_report(self) -> None:
        audit_path = self.base / "state/reports/goal-alpha-audit.json"
        head_path = self.base / "state/reports/goal-alpha-head.json"
        audit_path.write_text('{"goal_id":"goal-alpha","revision":1,"project_id":"alpha"}\n',
                              encoding="utf-8")
        head_path.write_text('{"goal_id":"goal-alpha","revision":1,"project_id":"alpha"}\n',
                             encoding="utf-8")
        original = outbox.state_digest(self.base, "alpha", "goal-alpha")
        audit_path.write_text('{"goal_id":"goal-alpha","revision":2,"project_id":"alpha"}\n',
                              encoding="utf-8")
        self.assertEqual(outbox.state_digest(self.base, "alpha", "goal-alpha"), original)
        head_path.write_text('{"goal_id":"goal-alpha","revision":2,"project_id":"alpha"}\n',
                             encoding="utf-8")
        self.assertNotEqual(outbox.state_digest(self.base, "alpha", "goal-alpha"), original)

    def test_receipt_rejects_every_noncanonical_notification_journal(self) -> None:
        path = self.base / "state/reports/unknown.json"
        with self.assertRaises(TransitionReceiptError):
            commit_transition(
                self.base,
                [json_mutation(path, {"schema_version": 1, "id": "unknown"})],
                {"id": "notification-unknown-event", "schema_version": 1},
                journal="state/notification-arbitrary-events.jsonl",
            )
        self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)

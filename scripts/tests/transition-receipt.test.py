#!/usr/bin/env python3
"""Focused crash/interleaving controls for canonical transition receipts."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from jsonl_durable import read_jsonl_objects  # noqa: E402
from transition_receipt import (  # noqa: E402
    TransitionReceiptError,
    commit_event,
    commit_transition,
    fields_mutation,
    json_mutation,
    raw_text_mutation,
    recover_transitions,
    resume_transition,
    text_mutation,
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


class ReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        (self.base / "state/.locks").mkdir(parents=True)
        (self.base / "state/tasks").mkdir()
        self.task = self.base / "state/tasks/t1.md"
        self.task.write_text("id: t1\nstatus: ready\nevent_seq: 0\n\nbody\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def event(self, event_id: str = "source-test-transition") -> dict:
        return {"schema_version": 1, "id": event_id, "event": "task-transition",
                "project": "p", "goal": "g", "task": "t1", "pid": 1,
                "detail": {"from": "ready", "to": "running"}}

    def rows(self) -> list[dict]:
        return read_jsonl_objects(self.base / "state/events.jsonl")

    def test_receipt_fsync_without_state_never_projects_false_event(self) -> None:
        with failpoint("receipt-fsync"):
            with self.assertRaises(TransitionReceiptError):
                commit_transition(self.base, [fields_mutation(self.task, {"status": "running"})],
                                  self.event())
        self.assertIn("status: ready", self.task.read_text())
        result = recover_transitions(self.base)
        self.assertEqual(result["uncommitted"], 1)
        self.assertEqual(self.rows(), [])

    def test_state_commit_is_recovered_to_one_event(self) -> None:
        with failpoint("state-write"):
            with self.assertRaises(TransitionReceiptError):
                commit_transition(self.base, [fields_mutation(self.task, {"status": "running"})],
                                  self.event())
        self.assertIn("status: running", self.task.read_text())
        self.assertEqual(self.rows(), [])
        self.assertEqual(recover_transitions(self.base)["projected"], 1)
        self.assertEqual([row["id"] for row in self.rows()], ["source-test-transition"])

    def test_raw_text_projection_is_exact_and_never_receives_frontmatter(self) -> None:
        portfolio = self.base / "state/portfolio.tsv"
        portfolio.write_text("# header\n", encoding="utf-8")
        marker = self.base / "state/project.json"
        event = self.event("source-raw-text")
        commit_transition(
            self.base,
            [raw_text_mutation(portfolio, "# header\np\t/repo\tremote\tmain\tkey\t-\t-\tpending\n"),
             json_mutation(marker, {"schema_version": 1, "id": "p", "status": "pending"})],
            event,
            authoritative_index=1,
        )
        self.assertEqual(
            portfolio.read_text(encoding="utf-8"),
            "# header\np\t/repo\tremote\tmain\tkey\t-\t-\tpending\n",
        )
        self.assertNotIn("event_seq", portfolio.read_text(encoding="utf-8"))

    def test_absent_authoritative_text_starts_at_one_and_replays_exactly(self) -> None:
        created = self.base / "state/tasks/new-task.md"
        body = "id: new-task\nstatus: proposed\n\nbounded intent\n"
        event = self.event("source-new-authoritative-text")
        event["task"] = "new-task"

        transition_id = commit_transition(self.base, [text_mutation(created, body)], event)
        text = created.read_text(encoding="utf-8")
        header, intent = text.split("\n\n", 1)
        self.assertIn("event_seq: 1", header)
        self.assertIn(f"last_transition_id: {transition_id}", header)
        self.assertEqual(intent, "bounded intent\n")
        self.assertEqual(sum(row.get("id") == event["id"] for row in self.rows()), 1)

        self.assertEqual(commit_transition(self.base, [text_mutation(created, body)], event), transition_id)
        self.assertEqual(sum(row.get("id") == event["id"] for row in self.rows()), 1)
        with self.assertRaises(TransitionReceiptError):
            commit_transition(self.base, [text_mutation(created, body + "different\n")], event)

    def test_jsonl_failure_and_event_before_marker_replay_exactly_once(self) -> None:
        for point in ("jsonl-append", "event-before-projected"):
            with self.subTest(point=point):
                other = self.base / f"state/tasks/{point}.md"
                other.write_text(f"id: {point}\nstatus: ready\nevent_seq: 0\n", encoding="utf-8")
                event = self.event("source-" + point)
                event["task"] = point
                with failpoint(point):
                    with self.assertRaises(TransitionReceiptError):
                        commit_transition(self.base, [fields_mutation(other, {"status": "running"})], event)
                recover_transitions(self.base)
                recover_transitions(self.base)
                self.assertEqual(sum(row.get("id") == event["id"] for row in self.rows()), 1)

    def test_partial_multi_file_blocks_unrelated_but_exact_retry_finishes(self) -> None:
        second = self.base / "state/tasks/t2.md"
        second.write_text("id: t2\nstatus: ready\nevent_seq: 0\n", encoding="utf-8")
        event = self.event("source-multi")
        with failpoint("state-write-1"):
            with self.assertRaises(TransitionReceiptError):
                commit_transition(
                    self.base,
                    [fields_mutation(self.task, {"status": "running"}),
                     fields_mutation(second, {"status": "running"})],
                    event, authoritative_index=1,
                )
        self.assertIn("status: running", self.task.read_text())
        self.assertIn("status: ready", second.read_text())
        with self.assertRaises(TransitionReceiptError):
            recover_transitions(self.base)
        unrelated = self.base / "state/tasks/t3.md"
        unrelated.write_text("id: t3\nstatus: ready\nevent_seq: 0\n", encoding="utf-8")
        with self.assertRaises(TransitionReceiptError):
            commit_transition(self.base, [fields_mutation(unrelated, {"status": "running"})],
                              self.event("source-unrelated"))
        self.assertIsNotNone(resume_transition(self.base, event))
        self.assertIn("status: running", second.read_text())
        self.assertEqual(sum(row.get("id") == "source-multi" for row in self.rows()), 1)

    def test_pure_event_receipt_recovers_without_an_external_state_witness(self) -> None:
        event = {"schema_version": 1, "event": "decision-deferred", "project": "p",
                 "goal": "", "task": "", "pid": 1, "detail": "paused"}
        with failpoint("receipt-fsync"):
            with self.assertRaises(TransitionReceiptError):
                commit_event(self.base, event)
        self.assertEqual(self.rows(), [])
        self.assertEqual(recover_transitions(self.base)["projected"], 1)
        self.assertEqual(len(self.rows()), 1)

    def test_runtime_snapshot_lock_excludes_transition(self) -> None:
        (self.base / "state/.locks/runtime-state.lock").mkdir()
        prior = os.environ.get("RECURSION_LOCK_ATTEMPTS")
        os.environ["RECURSION_LOCK_ATTEMPTS"] = "1"
        try:
            with self.assertRaises(TransitionReceiptError):
                commit_transition(self.base, [fields_mutation(self.task, {"status": "running"})],
                                  self.event())
        finally:
            if prior is None: os.environ.pop("RECURSION_LOCK_ATTEMPTS", None)
            else: os.environ["RECURSION_LOCK_ATTEMPTS"] = prior
        self.assertIn("status: ready", self.task.read_text())

    @unittest.skipIf(os.name == "nt", "production PID/start witness reclamation requires /proc")
    def test_dead_taskctl_owner_is_reclaimed_for_exact_retry(self) -> None:
        lock = self.base / "state/.locks/taskctl.lock"
        lock.mkdir()
        (lock / "pid").write_text("99999999\n", encoding="ascii")
        (lock / "start").write_text("1\n", encoding="ascii")
        commit_transition(self.base, [fields_mutation(self.task, {"status": "running"})], self.event())
        self.assertIn("status: running", self.task.read_text())
        self.assertFalse(lock.exists())

    def test_json_witness_detects_content_divergence(self) -> None:
        record = self.base / "state/value.json"
        record.write_text(json.dumps({"schema_version": 1, "value": 1}) + "\n", encoding="utf-8")
        with failpoint("state-write"):
            with self.assertRaises(TransitionReceiptError):
                commit_transition(self.base, [json_mutation(record, {"schema_version": 1, "value": 2})],
                                  self.event("source-json"))
        value = json.loads(record.read_text()); value["value"] = 3
        record.write_text(json.dumps(value) + "\n", encoding="utf-8")
        with self.assertRaises(TransitionReceiptError):
            recover_transitions(self.base)

    def test_reserved_witness_shaped_body_is_preserved_and_header_is_authoritative(self) -> None:
        self.task.write_text("id: t1\nstatus: ready\n\nevent_seq: 999\nlast_transition_id: prose\n",
                             encoding="utf-8")
        commit_transition(self.base, [fields_mutation(self.task, {"status": "running"})], self.event())
        text = self.task.read_text(encoding="utf-8")
        header, body = text.split("\n\n", 1)
        self.assertIn("event_seq: 1", header)
        self.assertIn("last_transition_id: transition-", header)
        self.assertEqual(body, "event_seq: 999\nlast_transition_id: prose\n")

    def test_terminal_receipt_backlog_compacts_in_bounded_retryable_batches(self) -> None:
        active = self.base / "state/recovery/transitions"
        events: list[dict] = []
        for number in range(129):
            event = {
                "schema_version": 1,
                "id": f"source-legacy-{number:04d}",
                "event": "legacy-projected",
                "project": "p",
                "goal": "g",
                "task": "",
                "detail": {"number": number},
            }
            transition_id = "transition-" + hashlib.sha256(
                json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()[:32]
            frozen = dict(event, transition_id=transition_id, ts="2026-08-10T00:00:00Z")
            prepared = {
                "schema_version": 1,
                "kind": "transition-receipt",
                "id": transition_id,
                "event_seq": 0,
                "prepared_at": frozen["ts"],
                "event": frozen,
                "journal": "state/events.jsonl",
                "authoritative_path": None,
                "mutations": [],
            }
            directory = active / transition_id
            directory.mkdir(parents=True)
            (directory / "prepared.json").write_text(
                json.dumps(prepared, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            (directory / "projected.json").write_text(
                json.dumps({"schema_version": 1, "status": "projected"}) + "\n",
                encoding="utf-8",
            )
            events.append(event)

        attempts = 0
        while any(active.iterdir()):
            attempts += 1
            before = sum(1 for _ in active.iterdir())
            try:
                recover_transitions(self.base, limit=16)
            except TransitionReceiptError as exc:
                self.assertIn("made bounded progress", str(exc))
            after = sum(1 for _ in active.iterdir())
            self.assertGreater(before, after)
            self.assertLessEqual(before - after, 16)
            self.assertLess(attempts, 20)

        archives = list((self.base / "state/recovery/transition-archive").glob("*/*/prepared.json"))
        indexes = list((self.base / "state/recovery/transition-event-index").glob("*/*.json"))
        self.assertEqual(len(archives), 129)
        self.assertEqual(len(indexes), 129)
        self.assertGreater(attempts, 1)

        first = events[0]
        transition_id = commit_event(self.base, first)
        self.assertTrue((self.base / "state/recovery/transition-archive" /
                         transition_id[len("transition-"):len("transition-") + 2] /
                         transition_id / "prepared.json").is_file())
        with self.assertRaises(TransitionReceiptError):
            commit_event(self.base, {**first, "detail": {"number": "collision"}})


if __name__ == "__main__":
    unittest.main(verbosity=2)

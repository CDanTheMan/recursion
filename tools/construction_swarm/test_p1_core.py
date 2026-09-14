"""P1 S01/S02/S05: real child crashes, competing processes, and fake-only boundaries."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from .p1_core import (
    FakeHermes, FakeTransport, FakeWorker, FenceRejected, GOAL_ID,
    IdempotencyConflict, P1Store, PermissionDenied, REQUIREMENTS_DIGEST,
    RevisionConflict, SOURCE_COMMIT, request_digest,
)


class P1CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.hermes_path = self.root / "fake-hermes.sqlite"
        self.hermes = FakeHermes(self.hermes_path)
        self.hermes.create_task("task-a", "alpha")
        self.store = P1Store(self.root / "store")
        self.store.grant("grant-worker-alpha", "worker", "alpha")
        self.fence = self.store.acquire_leader("leader-a")

    def tearDown(self):
        self.store.close()
        self.hermes.close()
        self.temp.cleanup()

    @staticmethod
    def request(task="task-a", project="alpha", grant="grant-worker-alpha", key="key-1", revision=1, actor="owner"):
        value = {"protocol_version": 1, "goal_id": GOAL_ID, "task_id": task, "project": project,
                 "expected_revision": revision, "source_commit": SOURCE_COMMIT,
                 "requirements_digest": REQUIREMENTS_DIGEST, "grant_id": grant,
                 "idempotency_key": key, "claimed_actor": actor}
        value["content_digest"] = request_digest(value)
        return value

    def child_crash(self, phase):
        self.store.close()
        self.hermes.close()
        command = [sys.executable, "-X", "utf8", "-B", "-m", "tools.construction_swarm.p1_fixture_worker",
                   "crash", "--root", str(self.root / "store"), "--hermes", str(self.hermes_path),
                   "--owner", "crashed-incarnation", "--task", "task-a", "--project", "alpha",
                   "--grant", "grant-worker-alpha", "--phase", phase]
        result = subprocess.run(command, cwd=Path(__file__).parents[2], capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 19, result.stderr.decode())
        self.hermes = FakeHermes(self.hermes_path)
        self.store = P1Store(self.root / "store")

    def recover(self):
        crashed_fence = self.store.attempt("attempt-00000001")["fence"]
        fence = self.store.acquire_leader("recovery-incarnation", takeover=True)
        self.store.recover_after_crash(crashed_fence, "recovery-incarnation", fence)
        return fence

    def test_s01_abrupt_accept_reopen_replays_exactly_one_canonical_transition(self):
        self.child_crash("reserved")
        recovery_fence = self.recover()
        attempt = self.store.attempt("attempt-00000001")
        self.assertEqual((attempt["state"], attempt["charge_state"]), ("unknown", "held"))
        self.assertEqual(self.store.attempts_count(), 1)
        self.assertEqual(self.store.accept(self.hermes, FakeTransport("worker"), self.request(key="crash-reservation"),
                                           "recovery-incarnation", recovery_fence)["attempt_id"], "attempt-00000001")
        self.assertEqual(self.store.outbox_delivery("attempt-accepted:attempt-00000001"), "pending")
        self.assertEqual(self.store.replay_outbox(self.hermes, "recovery-incarnation", recovery_fence),
                         ["attempt-accepted:attempt-00000001"])
        self.assertEqual(self.store.replay_outbox(self.hermes, "recovery-incarnation", recovery_fence), [])
        self.assertEqual(self.store.outbox_delivery("attempt-accepted:attempt-00000001"), "delivered")
        self.assertEqual(self.hermes.receipt_count("task-a", "attempt_accepted"), 1)

    def test_s01_attempt_revision_cannot_be_relabelled_after_amendment(self):
        accepted = self.store.accept(self.hermes, FakeTransport("worker"), self.request(), "leader-a", self.fence)
        self.store.replay_outbox(self.hermes, "leader-a", self.fence)
        self.store.launch(FakeWorker(), FakeTransport("worker"), accepted["attempt_id"], "leader-a", self.fence)
        self.hermes.amend("task-a")
        with self.assertRaises(RevisionConflict):
            self.store.submit_result(self.hermes, FakeTransport("worker"), accepted["attempt_id"], 1,
                                     "result-retry", "leader-a", self.fence)
        self.assertEqual(self.store.result(accepted["attempt_id"])["state"], "revision_conflict")
        self.assertEqual(self.hermes.receipt_count("task-a", "attempt_result"), 0)

    def test_s01_result_retry_is_idempotent_for_the_bound_revision(self):
        accepted = self.store.accept(self.hermes, FakeTransport("worker"), self.request(), "leader-a", self.fence)
        self.store.launch(FakeWorker(), FakeTransport("worker"), accepted["attempt_id"], "leader-a", self.fence)
        first = self.store.submit_result(self.hermes, FakeTransport("worker"), accepted["attempt_id"], 1,
                                         "result-key", "leader-a", self.fence)
        self.assertEqual(first, self.store.submit_result(self.hermes, FakeTransport("worker"), accepted["attempt_id"], 1,
                                                         "result-key", "leader-a", self.fence))
        with self.assertRaises(IdempotencyConflict):
            self.store.submit_result(self.hermes, FakeTransport("worker"), accepted["attempt_id"], 1,
                                     "changed-key", "leader-a", self.fence)

    def test_s02_competing_processes_elect_once_and_stale_fence_cannot_effect(self):
        self.store.close()
        race_root, start, commands = self.root / "race-store", self.root / "start", []
        for owner in ("process-a", "process-b"):
            ready, output = self.root / (owner + ".ready"), self.root / (owner + ".json")
            command = [sys.executable, "-X", "utf8", "-B", "-m", "tools.construction_swarm.p1_fixture_worker",
                       "elect", "--root", str(race_root), "--owner", owner, "--ready", str(ready),
                       "--start", str(start), "--result", str(output)]
            commands.append((owner, ready, output, subprocess.Popen(command, cwd=Path(__file__).parents[2],
                                                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)))
        try:
            deadline = time.monotonic() + 10
            while not all(ready.exists() for _, ready, _, _ in commands) and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertTrue(all(ready.exists() for _, ready, _, _ in commands), "children did not reach race barrier")
            start.write_text("go", encoding="utf-8")
            for _, _, _, process in commands:
                stdout, stderr = process.communicate(timeout=20)
                self.assertEqual(process.returncode, 0, (stdout, stderr))
        finally:
            for _, _, _, process in commands:
                if process.poll() is None:
                    process.terminate()
                    process.wait(5)
        outcomes = {owner: json.loads(output.read_text(encoding="utf-8")) for owner, _, output, _ in commands}
        winners = [(owner, value) for owner, value in outcomes.items() if value["acquired"]]
        self.assertEqual(len(winners), 1, outcomes)
        loser = next(value for _, value in outcomes.items() if not value["acquired"])
        self.assertEqual(loser["error"], "FenceRejected")
        owner, value = winners[0]
        self.store = P1Store(race_root)
        self.store.grant("grant-worker-alpha", "worker", "alpha")
        fence = value["fence"]
        self.assertEqual(self.store.leader(), {"owner": owner, "fence": fence})
        accepted = self.store.accept(self.hermes, FakeTransport("worker"), self.request(), owner, fence)
        self.store.launch(FakeWorker(), FakeTransport("worker"), accepted["attempt_id"], owner, fence)
        replacement_fence = self.store.acquire_leader("replacement", takeover=True)
        with self.assertRaises(FenceRejected):
            self.store.accept(self.hermes, FakeTransport("worker"), self.request(key="old-fence"), owner, fence)
        with self.assertRaises(FenceRejected):
            self.store.submit_result(self.hermes, FakeTransport("worker"), accepted["attempt_id"], 1,
                                     "old-result", owner, fence)
        with self.assertRaises(FenceRejected):
            self.store.replay_outbox(self.hermes, "replacement", replacement_fence)
        self.assertEqual(self.hermes.receipt_count("task-a", "attempt_accepted"), 0)
        self.assertGreater(replacement_fence, fence)

    def test_s02_crash_after_launch_intent_is_unknown_and_charge_is_retained(self):
        self.child_crash("launch_intent")
        self.recover()
        attempt = self.store.attempt("attempt-00000001")
        self.assertEqual((attempt["state"], attempt["charge_state"]), ("unknown", "held"))
        self.assertIsNotNone(attempt["launch_identity"])
        self.assertIsNone(attempt["launch_receipt"])

    def test_s02_crash_after_observed_effect_before_receipt_is_unknown_and_held(self):
        self.child_crash("after_effect")
        self.assertTrue((self.root / "store" / "effect-observed").is_file())
        self.recover()
        attempt = self.store.attempt("attempt-00000001")
        self.assertEqual((attempt["state"], attempt["charge_state"]), ("unknown", "held"))
        self.assertIsNotNone(attempt["launch_identity"])
        self.assertIsNone(attempt["launch_receipt"])

    def test_s02_effect_boundary_holds_authorization_transaction_through_fake_effect(self):
        accepted = self.store.accept(self.hermes, FakeTransport("worker"), self.request(), "leader-a", self.fence)
        observed = []
        worker = FakeWorker(after_authorize=lambda: observed.append(self.store.db.in_transaction))
        self.store.launch(worker, FakeTransport("worker"), accepted["attempt_id"], "leader-a", self.fence)
        self.assertEqual(observed, [True])
        self.assertEqual(worker.launches[0]["attempt_id"], accepted["attempt_id"])

    def test_s02_effect_boundary_rechecks_grant_after_before_effect_hook(self):
        accepted = self.store.accept(self.hermes, FakeTransport("worker"), self.request(), "leader-a", self.fence)
        worker = FakeWorker(before_effect=lambda: self.store.revoke("grant-worker-alpha"))
        with self.assertRaises(PermissionDenied):
            self.store.launch(worker, FakeTransport("worker"), accepted["attempt_id"], "leader-a", self.fence)
        self.assertEqual(worker.launches, [])

    def test_s02_recovery_adopts_only_crashed_fence_pending_result_outbox(self):
        accepted = self.store.accept(self.hermes, FakeTransport("worker"), self.request(), "leader-a", self.fence)
        self.store.launch(FakeWorker(), FakeTransport("worker"), accepted["attempt_id"], "leader-a", self.fence)
        result = self.store.submit_result(self.hermes, FakeTransport("worker"), accepted["attempt_id"], 1,
                                          "pending-result", "leader-a", self.fence)
        replacement = self.store.acquire_leader("recovery", takeover=True)
        with self.assertRaises(FenceRejected):
            self.store.replay_outbox(self.hermes, "recovery", replacement)
        self.store.recover_after_crash(self.fence, "recovery", replacement)
        self.assertEqual(self.store.replay_outbox(self.hermes, "recovery", replacement),
                         ["attempt-accepted:attempt-00000001", result])
        self.assertEqual(self.hermes.receipt_count("task-a", "attempt_result"), 1)

    def test_s01_revision_conflict_outbox_does_not_block_later_receipts(self):
        self.hermes.create_task("task-c", "alpha")
        first = self.store.accept(self.hermes, FakeTransport("worker"), self.request(key="first"), "leader-a", self.fence)
        second = self.store.accept(self.hermes, FakeTransport("worker"), self.request("task-c", "alpha", key="second"),
                                   "leader-a", self.fence)
        self.hermes.amend("task-a")
        self.assertEqual(self.store.replay_outbox(self.hermes, "leader-a", self.fence), [second["receipt"]])
        self.assertEqual(self.store.outbox_delivery(first["receipt"]), "revision_conflict")
        self.assertEqual(self.hermes.receipt_count("task-c", "attempt_accepted"), 1)

    def test_s05_tampered_outbox_envelope_cannot_cross_the_fake_boundary(self):
        accepted = self.store.accept(self.hermes, FakeTransport("worker"), self.request(), "leader-a", self.fence)
        row = self.store.db.execute("SELECT body FROM outbox WHERE receipt=?", (accepted["receipt"],)).fetchone()
        body = json.loads(row["body"])
        body["identity"] = "forged-worker"
        with self.store.db:
            self.store.db.execute("UPDATE outbox SET body=? WHERE receipt=?", (json.dumps(body), accepted["receipt"]))
        with self.assertRaisesRegex(Exception, "outbox envelope mismatch"):
            self.store.replay_outbox(self.hermes, "leader-a", self.fence)
        self.assertEqual(self.hermes.receipt_count("task-a"), 0)

    def test_s05_transport_identity_project_idempotency_and_revocation(self):
        self.hermes.create_task("task-b", "beta")
        self.store.grant("grant-owner-alpha", "owner", "alpha")
        with self.assertRaises(PermissionDenied):
            self.store.accept(self.hermes, FakeTransport("worker"), self.request(grant="grant-owner-alpha", key="spoof"),
                              "leader-a", self.fence)
        with self.assertRaises(PermissionDenied):
            self.store.accept(self.hermes, FakeTransport("worker"), self.request("task-b", "beta", key="cross-project"),
                              "leader-a", self.fence)
        request = self.request(key="repeat")
        first = self.store.accept(self.hermes, FakeTransport("worker"), request, "leader-a", self.fence)
        self.assertEqual(first, self.store.accept(self.hermes, FakeTransport("worker"), request, "leader-a", self.fence))
        changed = self.request(key="repeat", actor="changed-body")
        with self.assertRaises(IdempotencyConflict):
            self.store.accept(self.hermes, FakeTransport("worker"), changed, "leader-a", self.fence)
        self.store.revoke("grant-worker-alpha")
        with self.assertRaises(PermissionDenied):
            self.store.accept(self.hermes, FakeTransport("worker"), request, "leader-a", self.fence)
        with self.assertRaises(PermissionDenied):
            self.store.replay_outbox(self.hermes, "leader-a", self.fence)
        self.assertEqual(self.store.outbox_delivery(first["receipt"]), "pending")


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Acceptance gate for the bounded, read-only foundry observation adapter."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from .contracts import digest, encoded
from .ledger import Ledger
from .p2_access import AccessGrant, AccessRefused, AccessService, GrantStore
from .p2_foundry_observation import FoundryObservationAdapter, main


ROOT = Path(__file__).resolve().parents[2]
TASK_BASE = "e627cd93bac473094bc99e8fa29c8d62bae526a2"
BRANCH = "codex/v3-p2-foundry-observation-20260914"
ALLOWED_PATHS = {
    "tools/construction_swarm/p2_foundry_observation.py",
    "tools/construction_swarm/test_p2_foundry_observation.py",
    "docs/v3/construction/p2-foundry-observation-20260914/SPEC.md",
    "docs/v3/construction/p2-foundry-observation-20260914/PROGRESS.md",
}
DEPENDENCY_BLOBS = {
    "tools/construction_swarm/foundry.py": "650a2871c912c20f37d2e822e911ae42ddfd24b6",
    "tools/construction_swarm/ledger.py": "6cc4b25466f99bf8a0e406db0eefb4b385a1ecaa",
    "tools/construction_swarm/runner.py": "16c69e6c3aad4b2a9b97910a751594f8d2b01678",
    "tools/construction_swarm/contracts.py": "aff5cc8f443272be3315e4f8bfba6734990eb50e",
    "tools/construction_swarm/p2_access.py": "6d41f0195b74d103269133c4279c1b002e3c8669",
}
SOURCE_A = "1" * 40
SOURCE_B = "2" * 40


def _job(job_id, kind="develop"):
    return {
        "id": job_id,
        "domain": "adapter",
        "kind": kind,
        "brief": "bounded fixture",
        "inputs": [],
        "depends_on": [],
        "allowed_paths": [],
        "allowed_tools": [],
    }


def _plan(run_id, source, jobs):
    return {
        "version": 3,
        "run_id": run_id,
        "parent_goal": "goal-recursion-v2-execution-fabric",
        "authorization": "fixture-only",
        "source_commit": source,
        "deadline_utc": "2099-01-01T00:00:00Z",
        "limits": {
            "model_slots": 16,
            "domain_slots": 16,
            "max_dispatches": 32,
            "max_attempts": 2,
        },
        "route": {"backend": "devin-tools", "model": "swe-2-max"},
        "jobs": jobs,
        "credentials": "/fixture/never-read",
        "sources": {},
        "legacy_roots": [],
        "campaign": {},
    }


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _returned(ledger, root, job_id, *, accepted=False, content=None):
    number = ledger.reserve(job_id)
    attempt = root / "attempts" / job_id / str(number)
    filing = encoded(content or {"job_id": job_id, "summary": "worker returned"})
    packet = encoded({"job": job_id, "attempt": number})
    transport = encoded({"exit_code": 0, "reason": None, "local_quiescent": True})
    export = encoded({"agent": {"model_name": "SWE-2 Max"}, "steps": []})
    request = encoded({"name": "list_files", "arguments": {}})
    tool_receipt = encoded({"request_sha256": digest(request), "accepted": True})
    _write(attempt / "filing.json", filing)
    _write(attempt / "packet.json", packet)
    _write(attempt / "transport.json", transport)
    _write(attempt / "client-output" / "export.json", export)
    _write(attempt / "tools" / "1" / "request.json", request)
    _write(attempt / "tools" / "1" / "receipt.json", tool_receipt)
    receipt = {
        "job": job_id,
        "attempt": number,
        "state": "returned",
        "accepted": False,
        "launch_entered": True,
        "packet_sha256": digest(packet),
        "transport_sha256": digest(transport),
        "export_sha256": digest(export),
        "filing_sha256": digest(filing),
        "tool_receipts": [{"number": 1, "sha256": digest(tool_receipt)}],
    }
    _write(attempt / "receipt.json", encoded(receipt))
    ledger.finish(job_id, number, "returned", receipt, digest(filing))
    if accepted:
        ledger.decision(job_id, True, "independent fixture review accepted this output")
    return attempt, filing


def _make_run(base, name="alpha-run", source=SOURCE_A, *, full=True, old=False):
    root = base / name
    root.mkdir(parents=True)
    jobs = [_job("returned"), _job("accepted"), _job("running", "research"),
            _job("unknown", "test"), _job("queued", "research")]
    patcher = mock.patch("tools.construction_swarm.ledger.now", return_value="2020-01-01T00:00:00Z")
    context = patcher if old else mock.patch("tools.construction_swarm.ledger.now", wraps=None)
    if old:
        context.__enter__()
    try:
        ledger = Ledger(root)
        ledger.initialize(_plan(name, source, jobs))
        if full:
            _returned(ledger, root, "returned")
            _returned(ledger, root, "accepted", accepted=True)
            ledger.reserve("running")
            number = ledger.reserve("unknown")
            ledger.finish("unknown", number, "unknown", {
                "job": "unknown", "attempt": number, "launch_entered": True,
                "error": "terminal evidence unavailable",
            })
        ledger.close()
    finally:
        if old:
            context.__exit__(None, None, None)
    return root


def _tree_bytes(root):
    root = Path(root)
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*")) if path.is_file()
    }


class FoundryObservationTests(unittest.TestCase):
    maxDiff = 6000

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="p2-foundry-observation-")
        self.base = Path(self.temporary.name)
        self.root = _make_run(self.base)
        self.adapter = FoundryObservationAdapter({"alpha": self.root})

    def tearDown(self):
        self.temporary.cleanup()

    def read_only(self, adapter, operation, project, params=None, roots=None):
        roots = list(roots or [self.root])
        before = [_tree_bytes(root) for root in roots]
        try:
            return adapter.read(operation, project, params or {})
        finally:
            self.assertEqual(before, [_tree_bytes(root) for root in roots])

    def test_completed_and_inflight_views_derive_actual_facts(self):
        view = self.read_only(self.adapter, "tasks", "alpha", {"limit": 20})
        items = {item["task_id"]: item for item in view["data"]["items"]}
        self.assertEqual(items["returned"]["attempt"]["state"], "returned")
        self.assertTrue(items["returned"]["result"]["worker_returned"])
        self.assertEqual(items["returned"]["result"]["availability"], "verified")
        self.assertFalse(items["returned"]["acceptance"]["independently_accepted"])
        self.assertTrue(items["accepted"]["acceptance"]["independently_accepted"])
        self.assertEqual(items["accepted"]["acceptance"]["scope"], "foundry_head_decision")
        self.assertTrue(items["running"]["attempt"]["held"])
        self.assertEqual(items["running"]["result"]["availability"], "in_flight")
        status = self.read_only(self.adapter, "status", "alpha")
        self.assertEqual(status["data"]["counts"]["accepted"], 1)
        self.assertEqual(status["data"]["retained_holds"], 2)
        self.assertIn("canonical.hermes_authority", status["unavailable_fields"])

    def test_returned_never_promotes_itself_to_accepted(self):
        returned = self.read_only(self.adapter, "task", "alpha", {"task_id": "returned"})
        accepted = self.read_only(self.adapter, "task", "alpha", {"task_id": "accepted"})
        self.assertTrue(returned["data"]["item"]["result"]["worker_returned"])
        self.assertEqual(returned["data"]["item"]["acceptance"]["state"], "pending")
        self.assertFalse(returned["data"]["item"]["acceptance"]["independently_accepted"])
        self.assertTrue(accepted["data"]["item"]["acceptance"]["independently_accepted"])
        self.assertIn("independent fixture review", accepted["data"]["item"]["acceptance"]["reference"])

    def test_running_and_unknown_attempts_remain_held(self):
        for job_id, effect in (("running", "in_flight"), ("unknown", "unknown")):
            with self.subTest(job_id=job_id):
                item = self.read_only(self.adapter, "task", "alpha", {"task_id": job_id})["data"]["item"]
                self.assertTrue(item["attempt"]["held"])
                self.assertEqual(item["attempt"]["effect_state"], effect)
                self.assertFalse(item["result"]["worker_returned"])

    def test_missing_malformed_and_partial_records_are_bounded(self):
        missing = FoundryObservationAdapter({"missing": self.base / "absent"})
        with self.assertRaisesRegex(AccessRefused, "run directory is unavailable"):
            self.read_only(missing, "status", "missing", roots=[self.base / "absent"])

        malformed_root = self.base / "malformed"
        malformed_root.mkdir()
        (malformed_root / "ledger.sqlite").write_bytes(b"partial sqlite")
        malformed = FoundryObservationAdapter({"malformed": malformed_root})
        with self.assertRaisesRegex(AccessRefused, "ledger is malformed or unavailable"):
            self.read_only(malformed, "status", "malformed", roots=[malformed_root])

        receipt = self.root / "attempts" / "returned" / "1" / "receipt.json"
        receipt.unlink()
        item = self.read_only(self.adapter, "task", "alpha", {"task_id": "returned"})["data"]["item"]
        self.assertEqual(item["result"]["availability"], "unavailable")
        self.assertEqual(item["result"]["reason"], "evidence_missing")
        self.assertIsNone(item["result"]["artifact_handle"])

    def test_authentication_and_project_isolation_are_preserved(self):
        beta_root = _make_run(self.base, "beta-run", SOURCE_B, full=False)
        adapter = FoundryObservationAdapter({"alpha": self.root, "beta": beta_root})
        grant = AccessGrant("alpha-reader", frozenset({"alpha"}), frozenset({"read"}))
        service = AccessService(TASK_BASE, GrantStore([]), adapter=adapter)
        request = {"protocol_version": 1, "op": "tasks", "request_id": "one",
                   "params": {"project": "beta", "limit": 10}}
        before = [_tree_bytes(self.root), _tree_bytes(beta_root)]
        with self.assertRaisesRegex(AccessRefused, "does not permit this project"):
            service.dispatch(grant, request)
        self.assertEqual(before, [_tree_bytes(self.root), _tree_bytes(beta_root)])
        alpha = self.read_only(adapter, "status", "alpha", roots=[self.root, beta_root])
        self.assertEqual(alpha["data"]["run_id"], "alpha-run")
        self.assertEqual(alpha["data"]["source_commit"], SOURCE_A)

    def test_stale_snapshot_uses_durable_event_time(self):
        stale_root = _make_run(self.base, "stale-run", SOURCE_A, full=False, old=True)
        adapter = FoundryObservationAdapter({"stale": stale_root})
        view = self.read_only(adapter, "status", "stale", roots=[stale_root])
        service = AccessService(TASK_BASE, GrantStore([]), adapter=adapter, stale_after_seconds=1)
        envelope = service.envelope("stale", ok=True, view=view, caller_identity="reader")
        self.assertTrue(envelope["freshness"]["stale"])
        self.assertEqual(envelope["canonical_observed_at"], "2020-01-01T00:00:00Z")

    def test_real_event_sequence_is_the_only_cursor(self):
        events = self.read_only(self.adapter, "events", "alpha", {"after_cursor": 0, "limit": 100})
        cursors = [item["cursor"] for item in events["data"]["items"]]
        self.assertEqual(cursors, list(range(1, events["last_event_cursor"] + 1)))
        with self.assertRaisesRegex(AccessRefused, "cursor is outside retained history"):
            self.read_only(self.adapter, "events", "alpha", {"after_cursor": 999, "limit": 10})

        gap_root = _make_run(self.base, "gap-run", SOURCE_A, full=False)
        db = sqlite3.connect(gap_root / "ledger.sqlite")
        db.execute("INSERT INTO events(at,event,detail) VALUES(?,?,?)",
                   ("2026-09-14T00:00:00Z", "second", "{}"))
        db.execute("DELETE FROM events WHERE seq=1")
        db.commit()
        db.close()
        gap = FoundryObservationAdapter({"gap": gap_root})
        with self.assertRaisesRegex(AccessRefused, "durable event history is not replayable"):
            self.read_only(gap, "events", "gap", {"after_cursor": 0}, roots=[gap_root])

    def test_artifact_view_requires_original_manifest_digests(self):
        task = self.read_only(self.adapter, "task", "alpha", {"task_id": "returned"})["data"]["item"]
        handle = task["result"]["artifact_handle"]
        artifact = self.read_only(self.adapter, "artifact", "alpha", {"handle": handle, "limit": 1024})
        self.assertEqual(json.loads(base64.b64decode(artifact["data"]["content"])),
                         {"job_id": "returned", "summary": "worker returned"})
        self.assertEqual(artifact["data"]["sha256"], task["result"]["filing_sha256"])

        filing = self.root / "attempts" / "returned" / "1" / "filing.json"
        filing.write_bytes(b"tampered")
        with self.assertRaisesRegex(AccessRefused, "artifact handle is unavailable"):
            self.read_only(self.adapter, "artifact", "alpha", {"handle": handle})

        missing_root = _make_run(self.base, "missing-digest", SOURCE_A)
        db = sqlite3.connect(missing_root / "ledger.sqlite")
        db.execute("UPDATE jobs SET result_hash=NULL WHERE id='returned'")
        db.commit()
        db.close()
        missing = FoundryObservationAdapter({"missing": missing_root})
        item = self.read_only(missing, "task", "missing", {"task_id": "returned"},
                              roots=[missing_root])["data"]["item"]
        self.assertEqual(item["result"]["reason"], "manifest_digest_missing")
        self.assertIsNone(item["result"]["artifact_handle"])

    def test_replaced_run_identity_is_refused(self):
        self.read_only(self.adapter, "status", "alpha")
        replacement = _make_run(self.base, "replacement", SOURCE_B, full=False)
        os.replace(replacement / "ledger.sqlite", self.root / "ledger.sqlite")
        with self.assertRaisesRegex(AccessRefused, "configured run was replaced"):
            self.read_only(self.adapter, "status", "alpha")

    def test_explicit_entry_point_only_constructs_read_service(self):
        grants = self.base / "grants.json"
        grants.write_text("[]", encoding="utf-8")
        before = _tree_bytes(self.root)
        with mock.patch("tools.construction_swarm.p2_foundry_observation.GrantStore.load",
                        return_value=GrantStore([])), \
                mock.patch("tools.construction_swarm.p2_foundry_observation.serve") as serve_call, \
                mock.patch("tools.construction_swarm.foundry.initialize",
                           side_effect=AssertionError("foundry initialization invoked")), \
                mock.patch("tools.construction_swarm.foundry.run",
                           side_effect=AssertionError("foundry worker invoked")), \
                mock.patch("tools.construction_swarm.runner.run",
                           side_effect=AssertionError("scheduler invoked")):
            result = main(["serve", "--socket", str(self.base / "read.sock"),
                           "--source-commit", TASK_BASE, "--grants", str(grants),
                           "--project-run", "alpha=" + str(self.root)])
        self.assertEqual(result, 0)
        self.assertEqual(serve_call.call_count, 1)
        access = serve_call.call_args.args[1]
        self.assertIsInstance(access.adapter, FoundryObservationAdapter)
        self.assertEqual(before, _tree_bytes(self.root))

    def test_fixture_budget_is_below_packet_limit(self):
        size = sum(len(value) for value in _tree_bytes(self.base).values())
        self.assertLess(size, 32 * 1024 * 1024)


class SourceScopeTests(unittest.TestCase):
    def git(self, *args, check=True):
        return subprocess.run(
            ["git", "-c", "core.longpaths=true", *args], cwd=ROOT,
            capture_output=True, text=True, timeout=15, check=check,
        )

    def test_exact_source_dependency_and_four_path_scope(self):
        self.assertEqual(self.git("branch", "--show-current").stdout.strip(), BRANCH)
        self.assertEqual(self.git("merge-base", TASK_BASE, "HEAD").stdout.strip(), TASK_BASE)
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=all").stdout, "")
        changed = set(self.git("diff", "--name-only", TASK_BASE, "HEAD", "--").stdout.splitlines())
        self.assertEqual(changed, ALLOWED_PATHS)
        self.assertEqual(self.git("diff", "--check", TASK_BASE, "HEAD").returncode, 0)
        for path, expected in DEPENDENCY_BLOBS.items():
            with self.subTest(path=path):
                base_blob = self.git("rev-parse", f"{TASK_BASE}:{path}").stdout.strip()
                head_blob = self.git("rev-parse", f"HEAD:{path}").stdout.strip()
                self.assertEqual(base_blob, expected)
                self.assertEqual(head_blob, expected)


if __name__ == "__main__":
    unittest.main()

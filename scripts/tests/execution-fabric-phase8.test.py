#!/usr/bin/env python3
"""Hermetic tests for the inert Recursion v2 Phase 8 execution fabric."""

from __future__ import annotations

import hashlib
import json
import math
import multiprocessing
import os
from multiprocessing.pool import ThreadPool
import threading
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from execution_fabric import (  # noqa: E402
    AdmissionError,
    DurableFabricStore,
    HostHeartbeat,
    HostRegistry,
    HostRegistration,
    IntegrationCoordinator,
    PlacementCandidate,
    PlacementRequirements,
    PoolStatus,
    PlacementGovernor,
    ReconciliationError,
    SchemaError,
    resolve_placement,
    classify_stale_base,
    validate_candidate_refs,
    verify_candidate_result,
)


NOW = "2026-08-28T12:00:00Z"
SHA = "a" * 64
SHA40 = "1" * 40
RESULT = "b" * 64


def host(host_id: str = "host-one", *, caps=("terminal", "workspace-edit", "structured-result"),
         sandbox=("workspace",), network=("provider-only",), max_concurrency=2,
         workload=None, registered_at=NOW):
    return HostRegistration.build(host_id=host_id, capabilities=caps, operating_system="linux",
                                 architectures=("x86_64",), sandbox_profiles=sandbox,
                                 network_profiles=network, trust_class="registered",
                                 max_concurrency=max_concurrency,
                                 workload_concurrency=workload or {"implementer": 2},
                                 registered_at=registered_at)


def heartbeat(registration, *, observed_at=NOW, sequence=1):
    return HostHeartbeat(registration.host_id, registration.registration_digest, sequence, observed_at, 1)


def pool(pool_id="pool-one", *, max_concurrency=2, in_flight=0, quota_remaining=10,
         allowed_projects=("project-one", "project-two"), allowed_roles=("implementer",),
         allowed_models=("model-one",), billing_basis="included", account_id=None):
    return PoolStatus(pool_id, billing_basis, allowed_roles, allowed_projects, allowed_models,
                      max_concurrency, in_flight, quota_remaining, "weekly", False, 0.0, account_id)


def candidate(candidate_id="candidate-one", *, host_id="host-one", pool_id="pool-one",
              caps=("terminal", "workspace-edit", "structured-result"), sandbox="workspace",
              network="provider-only", model="model-one", enabled=True):
    return PlacementCandidate(candidate_id, "engine-one", "provider-one", pool_id, model, host_id,
                              sandbox, network, caps, "linux", "included", 0.0,
                              ("implementer",), enabled)


def requirements(*, task_id="task-one", project_id="project-one", caps=("terminal", "workspace-edit", "structured-result"),
                  sandbox="workspace", network="provider-only", model=None, max_cost=0.0,
                  preferred_hosts=(), preferred_pools=(), policy="subscription-first", manual_candidate_id=None,
                  billing_basis=("included",)):
    return PlacementRequirements(task_id, project_id, "implementer", caps, "linux", sandbox, network,
                                 billing_basis, max_cost, model, preferred_hosts, preferred_pools, SHA,
                                 policy, manual_candidate_id)


def process_admit(args):
    path, task_id = args
    registered = host(max_concurrency=3, workload={"implementer": 3})
    store = DurableFabricStore(path)
    try:
        assignment, trace = store.admit_placement(requirements(task_id=task_id), [candidate()],
                                                  {registered.host_id: registered},
                                                  {registered.host_id: heartbeat(registered)},
                                                  {"pool-one": pool(max_concurrency=3)},
                                                  lease_id=f"lease-{task_id}", attempt_id=f"attempt-{task_id}",
                                                  remote_session_id=f"session-{task_id}", now=NOW,
                                                  expires_at="2026-08-28T12:05:00Z")
        return assignment is not None, trace[0].code if trace else None
    except Exception as error:  # child result is asserted by the parent test
        return False, type(error).__name__ + ":" + getattr(error, "code", "")


class FabricPlacementTests(unittest.TestCase):
    def test_registration_and_heartbeat_are_strict_and_bound(self):
        registered = host()
        with self.assertRaises(TypeError):
            registered.workload_concurrency["implementer"] = 99
        parsed = HostRegistration.from_dict(registered.to_dict())
        self.assertEqual(parsed.registration_digest, registered.registration_digest)
        with self.assertRaises(SchemaError) as error:
            HostRegistration.from_dict({**registered.to_dict(), "credential_ref": "secret:bad"})
        self.assertEqual(error.exception.code, "UNKNOWN_FIELD")

        hb = heartbeat(registered)
        self.assertEqual(HostHeartbeat.from_dict(hb.to_dict()), hb)
        stale = heartbeat(registered, observed_at="2026-08-28T11:00:00Z")
        assignment, trace = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                              {registered.host_id: stale}, {"pool-one": pool()},
                                              now_epoch=1787918400, heartbeat_ttl_s=120)
        self.assertIsNone(assignment)
        self.assertEqual(trace[0].code, "HEARTBEAT_STALE")

    def test_registry_enforces_monotonic_heartbeats_and_governor_reserves_capacity(self):
        registry = HostRegistry()
        registered = host(max_concurrency=1, workload={"implementer": 1})
        self.assertEqual(registry.register(registered), "registered")
        self.assertEqual(registry.register(registered), "duplicate")
        self.assertEqual(registry.heartbeat(heartbeat(registered, sequence=1)), "accepted")
        self.assertEqual(registry.heartbeat(heartbeat(registered, sequence=1)), "duplicate")
        with self.assertRaises(AdmissionError) as error:
            registry.heartbeat(heartbeat(registered, sequence=0))
        self.assertEqual(error.exception.code, "HEARTBEAT_OUT_OF_ORDER")
        governor = PlacementGovernor(registry, {"pool-one": pool(max_concurrency=1)})
        first, _ = governor.place(requirements(task_id="task-one"), [candidate()], now_epoch=1787918400, created_at=NOW)
        self.assertIsNotNone(first)
        second, trace = governor.place(requirements(task_id="task-two"), [candidate()], now_epoch=1787918400, created_at=NOW)
        self.assertIsNone(second)
        self.assertEqual(trace[0].code, "POOL_CONCURRENCY_EXHAUSTED")
        self.assertEqual(governor.release(first), "released")
        self.assertEqual(governor.release(first), "duplicate")
        third, _ = governor.place(requirements(task_id="task-three"), [candidate()], now_epoch=1787918400, created_at=NOW)
        self.assertIsNotNone(third)

    def test_deterministic_success_and_complete_rejection_trace(self):
        registered = host()
        candidates = [candidate("good"), candidate("disabled", enabled=False),
                      candidate("bad-network", network="wrong-network"),
                      candidate("missing-cap", caps=("terminal",))]
        assignment_a, trace_a = resolve_placement(requirements(), candidates, {registered.host_id: registered},
                                                  {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                  now_epoch=1787918400, created_at=NOW)
        assignment_b, trace_b = resolve_placement(requirements(), list(reversed(candidates)), {registered.host_id: registered},
                                                  {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                  now_epoch=1787918400, created_at=NOW)
        self.assertIsNotNone(assignment_a)
        self.assertEqual(assignment_a, assignment_b)
        self.assertEqual([item.to_dict() for item in trace_a], [item.to_dict() for item in trace_b])
        self.assertEqual(assignment_a.assignment_digest, assignment_b.assignment_digest)
        self.assertEqual([item.candidate_id for item in trace_a], ["bad-network", "disabled", "missing-cap"])

    def test_normal_git_sha_is_valid_and_schema_is_tracked(self):
        registered = host()
        req = PlacementRequirements(requirements(task_id="task-sha").task_id, "project-one", "implementer",
                                    requirements().capabilities, "linux", "workspace", "provider-only", ("included",),
                                    0.0, None, (), (), SHA40)
        assignment, _ = resolve_placement(req, [candidate()], {registered.host_id: registered},
                                          {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                          now_epoch=1787918400, created_at=NOW)
        self.assertEqual(assignment.source_sha, SHA40)
        self.assertEqual(type(assignment).from_dict(assignment.to_dict()), assignment)
        schema = Path(__file__).resolve().parents[2] / "schemas" / "control-plane" / "v1" / "execution-fabric.schema.json"
        self.assertEqual(json.loads(schema.read_text(encoding="utf-8"))["$defs"]["assignment"]["properties"]["kind"]["const"], "assignment")

    def test_incompatible_candidates_are_typed_and_no_fallback_is_silent(self):
        registered = host(max_concurrency=1)
        req = requirements(caps=("gpu",))
        assignment, trace = resolve_placement(req, [candidate("no-gpu")], {registered.host_id: registered},
                                              {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                              now_epoch=1787918400, created_at=NOW)
        self.assertIsNone(assignment)
        self.assertEqual(trace[0].code, "CAPABILITY_MISSING")

        assignment, trace = resolve_placement(requirements(), [candidate("full")], {registered.host_id: registered},
                                              {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                              now_epoch=1787918400, created_at=NOW, reserved_host={"host-one": 1})
        self.assertIsNone(assignment)
        self.assertEqual(trace[0].code, "HOST_CONCURRENCY_EXHAUSTED")

        assignment, trace = resolve_placement(requirements(), [candidate("quota")], {registered.host_id: registered},
                                              {registered.host_id: heartbeat(registered)}, {"pool-one": pool(quota_remaining=0)},
                                              now_epoch=1787918400, created_at=NOW)
        self.assertIsNone(assignment)
        self.assertEqual(trace[0].code, "POOL_QUOTA_EXHAUSTED")

    def test_duplicate_candidates_pause_and_nonfinite_values_fail_closed(self):
        registered = host()
        with self.assertRaises(SchemaError) as error:
            resolve_placement(requirements(), [candidate("same"), candidate("same")],
                              {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                              {"pool-one": pool()}, now_epoch=1787918400, created_at=NOW)
        self.assertEqual(error.exception.code, "DUPLICATE_CANDIDATE")
        assignment, trace = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                              {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                              now_epoch=1787918400, created_at=NOW, paused=True)
        self.assertIsNone(assignment); self.assertEqual(trace[0].code, "PAUSED")
        with self.assertRaises(SchemaError):
            PlacementCandidate.from_dict({**candidate().to_dict(), "cost_per_run": math.nan})
        with self.assertRaises(SchemaError) as error:
            HostRegistration.build(host_id="host-invalid", capabilities=registered.capabilities,
                                   operating_system="linux", architectures=registered.architectures,
                                   sandbox_profiles=registered.sandbox_profiles, network_profiles=registered.network_profiles,
                                   trust_class="registered", max_concurrency=1,
                                   workload_concurrency={"implementer": 1}, registered_at="2026-02-30T12:00:00Z")
        self.assertEqual(error.exception.code, "INVALID_TIMESTAMP")

    def test_heartbeat_epoch_future_skew_policies_and_protection_hooks(self):
        registered = host(); registry = HostRegistry(now=NOW, future_skew_s=10)
        registry.register(registered)
        with self.assertRaises(AdmissionError) as error:
            registry.heartbeat(heartbeat(registered, observed_at="2026-08-28T12:01:00Z"))
        self.assertEqual(error.exception.code, "HEARTBEAT_FUTURE")
        registry.heartbeat(heartbeat(registered, sequence=1))
        with self.assertRaises(AdmissionError) as error:
            registry.heartbeat(HostHeartbeat(registered.host_id, registered.registration_digest, 2, NOW, 0))
        self.assertEqual(error.exception.code, "LEASE_EPOCH_OUT_OF_ORDER")
        candidates = [replace(candidate("slow"), engine="engine-slow", speed_score=1, cost_per_run=3),
                      replace(candidate("fast"), engine="engine-fast", speed_score=9, cost_per_run=1),
                      replace(candidate("review"), engine="engine-review", reviewer_score=10, cost_per_run=2)]
        for policy, expected in (("fastest-eligible", "engine-fast"), ("strongest-reviewer", "engine-review"), ("cheapest-eligible", "engine-fast"),
                                 ("subscription-first", "engine-fast"), ("weighted-rotation", None)):
            req = requirements(task_id=f"task-{policy}", policy=policy, max_cost=5)
            selected, _ = resolve_placement(req, candidates, {registered.host_id: registered},
                                             {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                             now_epoch=1787918400, created_at=NOW)
            self.assertEqual(selected.engine, expected or selected.engine)
        manual, _ = resolve_placement(requirements(task_id="task-manual", policy="manual-pin", manual_candidate_id="review", max_cost=5),
                                       candidates, {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                                       {"pool-one": pool()}, now_epoch=1787918400, created_at=NOW)
        self.assertEqual(manual.engine, "engine-review")
        local_candidate = replace(candidate("local"), engine="engine-local", billing_basis="local")
        local_pool = pool(allowed_models=("model-one",), billing_basis="local")
        local = resolve_placement(requirements(task_id="task-local", policy="local-first", max_cost=5,
                                               billing_basis=("local",)), [local_candidate],
                                  {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                                  {"pool-one": local_pool}, now_epoch=1787918400, created_at=NOW)[0]
        self.assertEqual(local.engine, "engine-local")
        with self.assertRaises(AdmissionError) as error:
            validate_candidate_refs(result_ref="main", default_branch="main")
        self.assertEqual(error.exception.code, "PROTECTED_REF")
        self.assertEqual(classify_stale_base(assigned_source_sha=SHA, current_source_sha=SHA), "current-compatible")
        self.assertEqual(classify_stale_base(assigned_source_sha=SHA, current_source_sha="c" * 64), "stale-reviewable")
        self.assertEqual(classify_stale_base(assigned_source_sha=SHA, current_source_sha=SHA, integration_advanced=True), "stale-rebase-required")


class DurableStateTests(unittest.TestCase):
    def test_restart_reconciles_without_relaunch_and_is_idempotent(self):
        registered = host()
        assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                          {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                          now_epoch=1787918400, created_at=NOW)
        with tempfile.TemporaryDirectory() as temp:
            journal = Path(temp) / "state" / "fabric.jsonl"
            first = DurableFabricStore(journal)
            first.create_lease(assignment, lease_id="lease-one", attempt_id="attempt-one",
                               remote_session_id="session-one", now=NOW, expires_at="2026-08-28T12:05:00Z")
            restarted = DurableFabricStore(journal)
            recovered = restarted.reconcile_restart(now="2026-08-28T12:01:00Z")
            self.assertEqual(len(recovered), 1)
            self.assertEqual(recovered[0]["status"], "recovery_required")
            self.assertEqual(restarted.reconcile_restart(now="2026-08-28T12:02:00Z"), ())
            # A terminal result can be accepted after restart, but never replayed as a second result.
            self.assertEqual(restarted.accept_result(attempt_id="attempt-one", lease_id="lease-one",
                                                     assignment_digest_value=assignment.assignment_digest,
                                                     result_digest=RESULT, status="succeeded", observed_at=NOW), "accepted")
            self.assertEqual(restarted.accept_result(attempt_id="attempt-one", lease_id="lease-one",
                                                     assignment_digest_value=assignment.assignment_digest,
                                                     result_digest=RESULT, status="succeeded", observed_at=NOW), "duplicate")
            again = DurableFabricStore(journal)
            self.assertEqual(len(again.results), 1)
            with self.assertRaises(ReconciliationError) as error:
                again.accept_result(attempt_id="attempt-one", lease_id="lease-one",
                                    assignment_digest_value=assignment.assignment_digest, result_digest="c" * 64,
                                    status="succeeded", observed_at=NOW)
            self.assertEqual(error.exception.code, "CONFLICTING_RESULT")

    def test_late_and_mismatched_results_fail_closed(self):
        registered = host()
        assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                          {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                          now_epoch=1787918400, created_at=NOW)
        with tempfile.TemporaryDirectory() as temp:
            store = DurableFabricStore(Path(temp) / "fabric.jsonl")
            store.create_lease(assignment, lease_id="lease-one", attempt_id="attempt-one",
                               remote_session_id="session-one", now=NOW, expires_at="2026-08-28T12:01:00Z")
            self.assertEqual(store.expire(now="2026-08-28T12:02:00Z"), ("lease-one",))
            with self.assertRaises(ReconciliationError) as error:
                store.accept_result(attempt_id="attempt-one", lease_id="lease-one",
                                    assignment_digest_value=assignment.assignment_digest, result_digest=RESULT,
                                    status="succeeded", observed_at=NOW)
            self.assertEqual(error.exception.code, "LATE_RESULT")

    def test_result_at_expiry_is_rejected_without_expire_and_duplicate_identity_is_strict(self):
        registered = host(); assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                               {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                               now_epoch=1787918400, created_at=NOW)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fabric.jsonl"; store = DurableFabricStore(path)
            store.create_lease(assignment, lease_id="lease-exp", attempt_id="attempt-exp", remote_session_id="session-exp",
                               now=NOW, expires_at="2026-08-28T12:01:00Z")
            with self.assertRaises(ReconciliationError) as error:
                store.accept_result(attempt_id="attempt-exp", lease_id="lease-exp", assignment_digest_value=assignment.assignment_digest,
                                    result_digest=RESULT, status="succeeded", observed_at="2026-08-28T12:01:00Z")
            self.assertEqual(error.exception.code, "LATE_RESULT")
            # A conflicting status/lease/result identity is not an idempotent retry.
            store.create_lease(assignment, lease_id="lease-ok", attempt_id="attempt-ok", remote_session_id="session-ok",
                               now=NOW, expires_at="2026-08-28T12:05:00Z")
            store.accept_result(attempt_id="attempt-ok", lease_id="lease-ok", assignment_digest_value=assignment.assignment_digest,
                                result_digest=RESULT, status="succeeded", observed_at=NOW)
            with self.assertRaises(ReconciliationError) as error:
                store.accept_result(attempt_id="attempt-ok", lease_id="lease-ok", assignment_digest_value=assignment.assignment_digest,
                                    result_digest=RESULT, status="failed", observed_at=NOW)
            self.assertEqual(error.exception.code, "CONFLICTING_RESULT")

    def test_durable_admission_is_atomic_across_threads_and_processes(self):
        registered = host(max_concurrency=3, workload={"implementer": 3})
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / "fabric.jsonl")
            args = [(path, f"task-{index:02d}") for index in range(8)]
            with ThreadPool(4) as workers:
                thread_results = workers.map(process_admit, args[:4])
            context = multiprocessing.get_context("spawn")
            with context.Pool(4) as workers:
                process_results = workers.map(process_admit, args[4:])
            results = thread_results + process_results
            self.assertEqual(sum(item[0] for item in results), 3)
            reopened = DurableFabricStore(path)
            self.assertEqual(len(reopened.active_reservations()), 3)

    def test_restart_reconstructs_reservation_and_recovery_query_state(self):
        registered = host(); assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                               {registered.host_id: heartbeat(registered)}, {"pool-one": pool(account_id="acct-one")},
                                                               now_epoch=1787918400, created_at=NOW)
        self.assertEqual(assignment.account_id, "acct-one")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fabric.jsonl"; store = DurableFabricStore(path)
            store.create_lease(assignment, lease_id="lease-restart", attempt_id="attempt-restart", remote_session_id="session-restart",
                               now=NOW, expires_at="2026-08-28T12:05:00Z", role="implementer")
            restarted = DurableFabricStore(path)
            self.assertEqual(restarted.active_reservations()[0]["host"], "host-one")
            restarted.reconcile_restart(now="2026-08-28T12:01:00Z")
            self.assertEqual(restarted.record_recovery_query("lease-restart", state="unknown", observed_at="2026-08-28T12:02:00Z"), "recorded")
            self.assertEqual(DurableFabricStore(path).leases["lease-restart"]["recovery_state"], "query_unknown")

    def test_paused_durable_admission_creates_no_lease(self):
        registered = host()
        with tempfile.TemporaryDirectory() as temp:
            store = DurableFabricStore(Path(temp) / "fabric.jsonl")
            assignment, trace = store.admit_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                      {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                      lease_id="lease-paused", attempt_id="attempt-paused", remote_session_id="session-paused",
                                                      now=NOW, expires_at="2026-08-28T12:05:00Z", paused=True)
            self.assertIsNone(assignment); self.assertEqual(trace[0].code, "PAUSED"); self.assertFalse(store.leases)

    def test_journal_tamper_and_store_boundary_fail_closed(self):
        registered = host(); assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                               {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                               now_epoch=1787918400, created_at=NOW)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "root"; path = root / "fabric.jsonl"; store = DurableFabricStore(path, root=root)
            store.create_lease(assignment, lease_id="lease-tamper", attempt_id="attempt-tamper", remote_session_id="session-tamper",
                               now=NOW, expires_at="2026-08-28T12:05:00Z")
            event = json.loads(path.read_text(encoding="utf-8").splitlines()[0]); event["schema_version"] = 99
            path.write_text(json.dumps(event) + "\n", encoding="utf-8")
            with self.assertRaises(ReconciliationError) as error:
                DurableFabricStore(path, root=root)
            self.assertEqual(error.exception.code, "SCHEMA_VERSION")
            with self.assertRaises(ReconciliationError) as error:
                DurableFabricStore(Path(temp) / "outside.jsonl", root=root)
            self.assertEqual(error.exception.code, "STORE_OUTSIDE_ROOT")
            link = Path(temp) / "link"
            try:
                link.symlink_to(root, target_is_directory=True)
            except (OSError, NotImplementedError):
                pass  # Windows developer-mode policy may disallow symlink creation.
            else:
                with self.assertRaises(ReconciliationError) as error:
                    DurableFabricStore(link / "fabric.jsonl", root=link)
                self.assertEqual(error.exception.code, "UNSAFE_STORE_ROOT")


class IntegrationTests(unittest.TestCase):
    def test_same_project_is_serialized_but_other_projects_can_overlap(self):
        coordinator = IntegrationCoordinator()
        self.assertEqual(coordinator.admit(candidate_id="candidate-one", project_id="project-one",
                                            source_sha=SHA, result_commit=RESULT), "admitted")
        with self.assertRaises(AdmissionError) as error:
            coordinator.admit(candidate_id="candidate-two", project_id="project-one",
                              source_sha=SHA, result_commit=RESULT)
        self.assertEqual(error.exception.code, "INTEGRATION_SERIALIZED")
        self.assertEqual(coordinator.admit(candidate_id="candidate-two", project_id="project-two",
                                           source_sha=SHA, result_commit=RESULT), "admitted")
        self.assertEqual(coordinator.admit(candidate_id="candidate-two", project_id="project-two",
                                           source_sha=SHA, result_commit=RESULT), "duplicate")
        self.assertEqual(coordinator.complete("candidate-one"), "completed")
        self.assertEqual(coordinator.admit(candidate_id="candidate-three", project_id="project-one",
                                           source_sha=SHA, result_commit=RESULT), "admitted")

    def test_durable_integration_restarts_and_protects_refs(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "nested" / "integration.jsonl"
            coordinator = IntegrationCoordinator(path)
            coordinator.set_project_policy(project_id="project-one", default_branch="main", integration_branch="integration")
            coordinator.admit(candidate_id="candidate-one", project_id="project-one", source_sha=SHA,
                              result_commit=RESULT, result_ref="cursor/candidate-one")
            restarted = IntegrationCoordinator(path)
            self.assertEqual(restarted.active["project-one"], "candidate-one")
            with self.assertRaises(AdmissionError) as error:
                restarted.admit(candidate_id="candidate-two", project_id="project-one", source_sha=SHA,
                                result_commit=RESULT, result_ref="cursor/candidate-two")
            self.assertEqual(error.exception.code, "INTEGRATION_SERIALIZED")
            with self.assertRaises(AdmissionError) as error:
                restarted.admit(candidate_id="candidate-main", project_id="project-two", source_sha=SHA,
                                result_commit=RESULT, result_ref="main")
            self.assertEqual(error.exception.code, "PROTECTED_REF")
            self.assertEqual(restarted.complete("candidate-one"), "completed")
            self.assertEqual(IntegrationCoordinator(path).active, {})

    def test_verifier_hook_requires_assignment_source_and_pass(self):
        registered = host(); assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                               {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                               now_epoch=1787918400, created_at=NOW)
        self.assertEqual(verify_candidate_result(assignment=assignment, assignment_digest_value=assignment.assignment_digest,
                                                 source_sha=SHA, result_ref="cursor/candidate", verifier_passed=True), "verified")
        with self.assertRaises(ReconciliationError) as error:
            verify_candidate_result(assignment=assignment, assignment_digest_value=assignment.assignment_digest,
                                    source_sha=SHA, result_ref="cursor/candidate", verifier_passed=False)
        self.assertEqual(error.exception.code, "VERIFIER_REQUIRED")


if __name__ == "__main__":
    unittest.main(verbosity=2)

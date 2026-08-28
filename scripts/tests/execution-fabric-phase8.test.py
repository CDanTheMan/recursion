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
    Assignment,
    DurableFabricStore,
    DurableHostRegistry,
    HostHeartbeat,
    HostRegistry,
    HostRegistration,
    IntegrationCoordinator,
    PlacementCandidate,
    PlacementRequirements,
    PoolStatus,
    RoutingPolicy,
    PlacementGovernor,
    PauseGuard,
    ReconciliationError,
    SchemaError,
    resolve_placement,
    classify_stale_base,
    validate_candidate_refs,
    verify_candidate_result,
    VerificationReceipt,
    VerificationReceiptStore,
)


NOW = "2026-08-28T12:00:00Z"
SHA = "a" * 64
SHA40 = "1" * 40
RESULT = "b" * 64


def host(host_id: str = "host-one", *, caps=("terminal", "workspace-edit", "structured-result"),
         sandbox=("workspace",), network=("provider-only",), max_concurrency=2,
         workload=None, registered_at=NOW, network_endpoints=None):
    return HostRegistration.build(host_id=host_id, capabilities=caps, operating_system="linux",
                                 architectures=("x86_64",), sandbox_profiles=sandbox,
                                 network_profiles=network, trust_class="registered",
                                 max_concurrency=max_concurrency,
                                 workload_concurrency=workload or {"implementer": 2},
                                 registered_at=registered_at, network_endpoints=network_endpoints)


def heartbeat(registration, *, observed_at=NOW, sequence=1):
    return HostHeartbeat(registration.host_id, registration.registration_digest, sequence, observed_at, 1)


def pool(pool_id="pool-one", *, max_concurrency=2, in_flight=0, quota_remaining=10,
         allowed_projects=("project-one", "project-two"), allowed_roles=("implementer",),
         allowed_models=("model-one",), billing_basis="included", account_id=None):
    return PoolStatus(pool_id, billing_basis, allowed_roles, allowed_projects, allowed_models,
                      max_concurrency, in_flight, quota_remaining, "weekly", False, 0.0, account_id)


def candidate(candidate_id="candidate-one", *, host_id="host-one", pool_id="pool-one",
              caps=("terminal", "workspace-edit", "structured-result"), sandbox="workspace",
              network="provider-only", model="model-one", enabled=True, required_endpoints=()):
    return PlacementCandidate(candidate_id, "engine-one", "provider-one", pool_id, model, host_id,
                              sandbox, network, caps, "linux", "included", 0.0,
                              ("implementer",), enabled, required_endpoints=required_endpoints)


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


def receipt_for(assignment, candidate_id="candidate-one", result_commit=RESULT):
    return VerificationReceipt.build(receipt_id=f"receipt-{candidate_id}", assignment_digest=assignment.assignment_digest,
                                      source_sha=assignment.source_sha, candidate_id=candidate_id, result_commit=result_commit,
                                      diff_digest="c" * 64, scope_digest="d" * 64, gate_digest="e" * 64,
                                      verifier_identity="controller/verifier-one", verified_at=NOW)


def integration_assignment(candidate_id, project_id):
    registered = host()
    return resolve_placement(requirements(task_id=f"task-{candidate_id}", project_id=project_id), [candidate(candidate_id)],
                             {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                             {"pool-one": pool()}, now_epoch=1787918400, created_at=NOW)[0]


def integration_receipt(assignment, result_commit=RESULT):
    return VerificationReceipt.build(receipt_id=f"receipt-{assignment.project_id}-{assignment.candidate_id}", assignment_digest=assignment.assignment_digest,
                                      source_sha=assignment.source_sha, candidate_id=assignment.candidate_id, result_commit=result_commit,
                                      diff_digest="c" * 64, scope_digest="d" * 64, gate_digest="e" * 64,
                                      verifier_identity="controller/verifier-one", verified_at=NOW)


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

    def test_cheapest_is_cost_first_even_against_preferences(self):
        registered = host()
        expensive = replace(candidate("preferred"), cost_per_run=10)
        cheap = replace(candidate("cheap"), cost_per_run=1)
        selected, _ = resolve_placement(requirements(policy="cheapest-eligible", max_cost=20,
                                                      preferred_hosts=("host-one",)), [expensive, cheap],
                                        {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                                        {"pool-one": pool()}, now_epoch=1787918400, created_at=NOW)
        self.assertEqual(selected.candidate_id, "cheap")

    def test_endpoints_refs_weighted_and_routing_authority_fail_closed(self):
        registered = host(network_endpoints={"provider-only": ("registry-endpoint",)})
        selected, _ = resolve_placement(requirements(), [candidate(required_endpoints=("registry-endpoint",))],
                                        {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                                        {"pool-one": pool()}, now_epoch=1787918400, created_at=NOW)
        self.assertIsNotNone(selected)
        selected, trace = resolve_placement(requirements(), [candidate(required_endpoints=("missing-endpoint",))],
                                            {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                                            {"pool-one": pool()}, now_epoch=1787918400, created_at=NOW)
        self.assertIsNone(selected); self.assertEqual(trace[0].code, "NETWORK_ENDPOINT_MISSING")
        for bad_ref in ("../escape", "feature..name", "feature^{}", "feature@{bad}", "feature~1", "feature.lock/x"):
            with self.assertRaises(AdmissionError) as error:
                validate_candidate_refs(result_ref=bad_ref)
            self.assertEqual(error.exception.code, "INVALID_RESULT_REF")
        weighted = [replace(candidate("low"), weight=1), replace(candidate("high"), weight=3)]
        choices = [resolve_placement(requirements(task_id=f"weighted-{i}", policy="weighted-rotation"), weighted,
                                     {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                                     {"pool-one": pool()}, now_epoch=1787918400, created_at=NOW)[0].candidate_id
                   for i in range(80)]
        self.assertGreater(choices.count("high"), choices.count("low"))
        metered = replace(candidate(), billing_basis="metered")
        metered_pool = pool(billing_basis="metered")
        selected, trace = resolve_placement(requirements(billing_basis=("metered",)), [metered],
                                            {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                                            {"pool-one": metered_pool}, now_epoch=1787918400, created_at=NOW)
        self.assertIsNone(selected); self.assertEqual(trace[0].code, "METERED_NOT_AUTHORIZED")
        policy = RoutingPolicy.build(policy_id="human-policy", allowed_billing_basis=("metered",), allow_on_demand=False)
        selected, _ = resolve_placement(requirements(billing_basis=("metered",)), [metered],
                                        {registered.host_id: registered}, {registered.host_id: heartbeat(registered)},
                                        {"pool-one": metered_pool}, now_epoch=1787918400, created_at=NOW,
                                        routing_policy=policy)
        self.assertIsNotNone(selected)


class DurableStateTests(unittest.TestCase):
    def test_durable_host_registry_restarts_and_rejects_tampered_digest(self):
        registered = host()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "registry.json"
            registry = DurableHostRegistry(path, now=NOW)
            self.assertEqual(registry.register(registered), "registered")
            self.assertEqual(registry.heartbeat(heartbeat(registered), now=NOW), "accepted")
            restarted = DurableHostRegistry(path, now=NOW)
            hosts, beats = restarted.snapshot()
            self.assertEqual(hosts[registered.host_id], registered)
            self.assertEqual(beats[registered.host_id], heartbeat(registered))
            state = json.loads(path.read_text(encoding="utf-8")); state["state_digest"] = "0" * 64
            path.write_text(json.dumps(state), encoding="utf-8")
            with self.assertRaises(ReconciliationError) as error:
                DurableHostRegistry(path, now=NOW)
            self.assertEqual(error.exception.code, "DIGEST_MISMATCH")

    def test_lease_identity_role_expiry_and_nonfinite_time_fail_closed(self):
        registered = host(); assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                               {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                               now_epoch=1787918400, created_at=NOW)
        with tempfile.TemporaryDirectory() as temp:
            store = DurableFabricStore(Path(temp) / "fabric.jsonl")
            with self.assertRaises(AdmissionError) as error:
                store.create_lease(assignment, lease_id="lease-bad", attempt_id="attempt-bad", remote_session_id="session-bad",
                                   now=NOW, expires_at=NOW)
            self.assertEqual(error.exception.code, "INVALID_LEASE")
            store.create_lease(assignment, lease_id="lease-one", attempt_id="attempt-one", remote_session_id="session-one",
                               now=NOW, expires_at="2026-08-28T12:05:00Z")
            self.assertEqual(store.leases["lease-one"]["reservation"]["role"], "implementer")
            with self.assertRaises(AdmissionError) as error:
                store.create_lease(assignment, lease_id="lease-two", attempt_id="attempt-two", remote_session_id="session-one",
                                   now=NOW, expires_at="2026-08-28T12:05:00Z")
            self.assertEqual(error.exception.code, "DUPLICATE_REMOTE_SESSION")
        with self.assertRaises(SchemaError):
            resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                              {registered.host_id: heartbeat(registered)}, {"pool-one": pool()}, now_epoch=math.inf)
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
            with self.assertRaises(ReconciliationError) as error:
                restarted.accept_result(attempt_id="attempt-one", lease_id="lease-one",
                                        assignment_digest_value=assignment.assignment_digest,
                                        result_digest=RESULT, status="succeeded", observed_at="9999-12-31T23:59:59Z",
                                        controller_now=NOW)
            self.assertEqual(error.exception.code, "INVALID_CONTROLLER_TIME")
            self.assertEqual(restarted.accept_result(attempt_id="attempt-one", lease_id="lease-one",
                                                     assignment_digest_value=assignment.assignment_digest,
                                                     result_digest=RESULT, status="succeeded", observed_at=NOW,
                                                     controller_now="2026-08-28T12:02:00Z"), "accepted")
            self.assertEqual(restarted.accept_result(attempt_id="attempt-one", lease_id="lease-one",
                                                     assignment_digest_value=assignment.assignment_digest,
                                                     result_digest=RESULT, status="succeeded", observed_at=NOW,
                                                     controller_now="2026-08-28T12:02:00Z"), "duplicate")
            again = DurableFabricStore(journal)
            self.assertEqual(len(again.results), 1)
            with self.assertRaises(ReconciliationError) as error:
                again.accept_result(attempt_id="attempt-one", lease_id="lease-one",
                                    assignment_digest_value=assignment.assignment_digest, result_digest="c" * 64,
                                    status="succeeded", observed_at=NOW, controller_now=NOW)
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
                                    status="succeeded", observed_at=NOW, controller_now=NOW)
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
                                    result_digest=RESULT, status="succeeded", observed_at="2026-08-28T12:01:00Z", controller_now="2026-08-28T12:01:00Z")
            self.assertEqual(error.exception.code, "LATE_RESULT")
            # A conflicting status/lease/result identity is not an idempotent retry.
            store.create_lease(assignment, lease_id="lease-ok", attempt_id="attempt-ok", remote_session_id="session-ok",
                               now=NOW, expires_at="2026-08-28T12:05:00Z")
            store.accept_result(attempt_id="attempt-ok", lease_id="lease-ok", assignment_digest_value=assignment.assignment_digest,
                                result_digest=RESULT, status="succeeded", observed_at=NOW, controller_now=NOW)
            with self.assertRaises(ReconciliationError) as error:
                store.accept_result(attempt_id="attempt-ok", lease_id="lease-ok", assignment_digest_value=assignment.assignment_digest,
                                    result_digest=RESULT, status="failed", observed_at=NOW, controller_now=NOW)
            self.assertEqual(error.exception.code, "CONFLICTING_RESULT")

            # Worker-reported observation time is advisory: an extreme but valid
            # timestamp cannot bypass or invalidate trusted controller admission.
            store2 = DurableFabricStore(Path(temp) / "fabric-advisory.jsonl")
            store2.create_lease(assignment, lease_id="lease-advisory", attempt_id="attempt-advisory", remote_session_id="session-advisory",
                                now=NOW, expires_at="2026-08-28T12:05:00Z")
            self.assertEqual(store2.accept_result(attempt_id="attempt-advisory", lease_id="lease-advisory",
                                                  assignment_digest_value=assignment.assignment_digest, result_digest=RESULT,
                                                  status="succeeded", observed_at="1900-01-01T00:00:00Z", controller_now=NOW), "accepted")
            store3 = DurableFabricStore(Path(temp) / "fabric-advisory-future.jsonl")
            store3.create_lease(assignment, lease_id="lease-advisory-future", attempt_id="attempt-advisory-future", remote_session_id="session-advisory-future",
                                now=NOW, expires_at="2026-08-28T12:05:00Z")
            self.assertEqual(store3.accept_result(attempt_id="attempt-advisory-future", lease_id="lease-advisory-future",
                                                  assignment_digest_value=assignment.assignment_digest, result_digest=RESULT,
                                                  status="succeeded", observed_at="9999-12-31T23:59:59Z", controller_now=NOW), "accepted")

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
            self.assertEqual(restarted.record_recovery_query("lease-restart", state="unknown", observed_at="2026-08-28T12:02:00Z", controller_now="2026-08-28T12:02:00Z"), "recorded")
            with self.assertRaises(ReconciliationError) as error:
                restarted.record_recovery_query("lease-restart", state="unknown", observed_at="9999-12-31T23:59:59Z", controller_now="2026-08-28T12:03:00Z")
            self.assertEqual(error.exception.code, "OBSERVATION_FUTURE")
            with self.assertRaises(ReconciliationError) as error:
                restarted.record_recovery_query("lease-restart", state="terminal", terminal_status="succeeded",
                                                result_digest=RESULT, observed_at="1900-01-01T00:00:00Z",
                                                controller_now="2026-08-28T12:01:00Z")
            self.assertEqual(error.exception.code, "INVALID_CONTROLLER_TIME")
            self.assertEqual(restarted.leases["lease-restart"]["updated_at"], "2026-08-28T12:02:00Z")
            self.assertEqual(DurableFabricStore(path).leases["lease-restart"]["recovery_state"], "query_unknown")
            import jsonschema
            schema = json.loads((Path(__file__).resolve().parents[2] / "schemas" / "control-plane" / "v1" / "execution-fabric.schema.json").read_text(encoding="utf-8"))
            for line in path.read_text(encoding="utf-8").splitlines():
                jsonschema.validate(json.loads(line), schema)

    def test_recovery_terminal_requires_durable_result_evidence(self):
        registered = host(); assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                               {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                               now_epoch=1787918400, created_at=NOW)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fabric.jsonl"; store = DurableFabricStore(path)
            store.create_lease(assignment, lease_id="lease-recover", attempt_id="attempt-recover", remote_session_id="session-recover",
                               now=NOW, expires_at="2026-08-28T12:05:00Z")
            store.reconcile_restart(now="2026-08-28T12:01:00Z")
            with self.assertRaises(ReconciliationError) as error:
                store.record_recovery_query("lease-recover", state="terminal", terminal_status="succeeded", observed_at="2026-08-28T12:02:00Z", controller_now="2026-08-28T12:02:00Z")
            self.assertEqual(error.exception.code, "EVIDENCE_REQUIRED")
            self.assertEqual(store.leases["lease-recover"]["status"], "recovery_required")
            self.assertEqual(store.record_recovery_query("lease-recover", state="terminal", terminal_status="succeeded",
                                                         result_digest=RESULT, observed_at="2026-08-28T12:02:00Z",
                                                         controller_now="2026-08-28T12:02:00Z"), "recorded")
            self.assertEqual(DurableFabricStore(path).leases["lease-recover"]["status"], "succeeded")

    def test_pause_blocks_durable_retries_before_existing_assignment_return(self):
        registered = host(); assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                               {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                               now_epoch=1787918400, created_at=NOW)
        with tempfile.TemporaryDirectory() as temp:
            store = DurableFabricStore(Path(temp) / "fabric.jsonl")
            store.create_lease(assignment, lease_id="lease-pause", attempt_id="attempt-pause", remote_session_id="session-pause",
                               now=NOW, expires_at="2026-08-28T12:05:00Z")
            with self.assertRaises(AdmissionError) as error:
                store.create_lease(assignment, lease_id="lease-pause", attempt_id="attempt-pause", remote_session_id="session-pause",
                                   now=NOW, expires_at="2026-08-28T12:05:00Z", pause_guard=PauseGuard(True))
            self.assertEqual(error.exception.code, "PAUSED")
            with self.assertRaises(AdmissionError) as error:
                store.admit_placement(requirements(), [candidate()], {registered.host_id: registered},
                                      {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                      lease_id="lease-pause", attempt_id="attempt-pause", remote_session_id="session-pause",
                                      now=NOW, expires_at="2026-08-28T12:05:00Z", pause_guard=PauseGuard(True))
            self.assertEqual(error.exception.code, "PAUSED")

    def test_paused_durable_admission_creates_no_lease(self):
        registered = host()
        with tempfile.TemporaryDirectory() as temp:
            store = DurableFabricStore(Path(temp) / "fabric.jsonl")
            with self.assertRaises(AdmissionError) as error:
                store.admit_placement(requirements(), [candidate()], {registered.host_id: registered},
                                      {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                      lease_id="lease-paused", attempt_id="attempt-paused", remote_session_id="session-paused",
                                      now=NOW, expires_at="2026-08-28T12:05:00Z", paused=True)
            self.assertEqual(error.exception.code, "PAUSED"); self.assertFalse(store.leases)

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

    def test_receipt_assignment_binding_cannot_be_rewritten(self):
        registered = host(); assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                               {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                               now_epoch=1787918400, created_at=NOW)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "receipts.jsonl"
            store = VerificationReceiptStore(path, verification_keys={"controller/verifier-one": "test-key"})
            receipt = receipt_for(assignment); store.issue(receipt)
            forged = replace(receipt, assignment_digest="b" * 64)
            with self.assertRaises(ReconciliationError) as error:
                verify_candidate_result(assignment=assignment, receipt=forged, candidate_id="candidate-one",
                                         result_commit=RESULT, diff_digest="c" * 64, scope_digest="d" * 64,
                                         gate_digest="e" * 64, result_ref="cursor/candidate", receipt_store=store)
            self.assertEqual(error.exception.code, "VERIFIER_RECEIPT_NOT_REGISTERED")
            persisted = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
            persisted["assignment_digest"] = "b" * 64
            path.write_text(json.dumps(persisted) + "\n", encoding="utf-8")
            with self.assertRaises(SchemaError) as error:
                VerificationReceiptStore(path, verification_keys={"controller/verifier-one": "test-key"})
            self.assertEqual(error.exception.code, "DIGEST_MISMATCH")


class IntegrationTests(unittest.TestCase):
    def test_same_project_is_serialized_but_other_projects_can_overlap(self):
        with tempfile.TemporaryDirectory() as temp:
            receipts = VerificationReceiptStore(Path(temp) / "receipts.jsonl", verification_keys={"controller/verifier-one": "test-key"})
            a1 = integration_assignment("candidate-one", "project-one"); r1 = integration_receipt(a1); receipts.issue(r1); r1 = receipts.get(r1.receipt_id)
            coordinator = IntegrationCoordinator(receipt_store=receipts)
            self.assertEqual(coordinator.admit(candidate_id="candidate-one", project_id="project-one", assignment=a1,
                                                source_sha=SHA, result_commit=RESULT, classification="current-compatible",
                                                verification_receipt=r1), "admitted")
            a2 = integration_assignment("candidate-two", "project-one"); r2 = integration_receipt(a2); receipts.issue(r2); r2 = receipts.get(r2.receipt_id)
            with self.assertRaises(AdmissionError) as error:
                coordinator.admit(candidate_id="candidate-two", project_id="project-one", assignment=a2,
                                  source_sha=SHA, result_commit=RESULT, classification="current-compatible",
                                  verification_receipt=r2)
            self.assertEqual(error.exception.code, "INTEGRATION_SERIALIZED")
            a2p = integration_assignment("candidate-two", "project-two"); r2p = integration_receipt(a2p); receipts.issue(r2p); r2p = receipts.get(r2p.receipt_id)
            self.assertEqual(coordinator.admit(candidate_id="candidate-two", project_id="project-two", assignment=a2p,
                                               source_sha=SHA, result_commit=RESULT, classification="stale-reviewable",
                                               verification_receipt=r2p), "admitted")
            self.assertEqual(coordinator.admit(candidate_id="candidate-two", project_id="project-two", assignment=a2p,
                                               source_sha=SHA, result_commit=RESULT, classification="stale-reviewable",
                                               verification_receipt=r2p), "duplicate")
            self.assertEqual(coordinator.complete("candidate-two"), "completed")
            self.assertEqual(coordinator.admit(candidate_id="candidate-two", project_id="project-two", assignment=a2p,
                                               source_sha=SHA, result_commit=RESULT, classification="stale-reviewable",
                                               verification_receipt=r2p), "completed")
            self.assertEqual(coordinator.complete("candidate-one"), "completed")
            a3 = integration_assignment("candidate-three", "project-one"); r3 = integration_receipt(a3); receipts.issue(r3); r3 = receipts.get(r3.receipt_id)
            self.assertEqual(coordinator.admit(candidate_id="candidate-three", project_id="project-one", assignment=a3,
                                               source_sha=SHA, result_commit=RESULT, classification="current-compatible",
                                               verification_receipt=r3), "admitted")

    def test_durable_integration_restarts_and_protects_refs(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "nested" / "integration.jsonl"
            receipts = VerificationReceiptStore(Path(temp) / "receipts.jsonl", verification_keys={"controller/verifier-one": "test-key"})
            a1 = integration_assignment("candidate-one", "project-one"); r1 = integration_receipt(a1); receipts.issue(r1); r1 = receipts.get(r1.receipt_id)
            coordinator = IntegrationCoordinator(path, receipt_store=receipts)
            coordinator.set_project_policy(project_id="project-one", default_branch="main", integration_branch="integration")
            coordinator.admit(candidate_id="candidate-one", project_id="project-one", source_sha=SHA,
                              result_commit=RESULT, assignment=a1, result_ref="cursor/candidate-one", classification="current-compatible",
                              verification_receipt=r1)
            restarted = IntegrationCoordinator(path, receipt_store=receipts)
            self.assertEqual(restarted.active["project-one"], "candidate-one")
            with self.assertRaises(AdmissionError) as error:
                a2 = integration_assignment("candidate-two", "project-one"); r2 = integration_receipt(a2); receipts.issue(r2); r2 = receipts.get(r2.receipt_id)
                restarted.admit(candidate_id="candidate-two", project_id="project-one", assignment=a2, source_sha=SHA,
                                result_commit=RESULT, result_ref="cursor/candidate-two", classification="current-compatible",
                                verification_receipt=r2)
            self.assertEqual(error.exception.code, "INTEGRATION_SERIALIZED")
            with self.assertRaises(AdmissionError) as error:
                am = integration_assignment("candidate-main", "project-two"); rm = integration_receipt(am); receipts.issue(rm); rm = receipts.get(rm.receipt_id)
                restarted.admit(candidate_id="candidate-main", project_id="project-two", assignment=am, source_sha=SHA,
                                result_commit=RESULT, result_ref="main", classification="current-compatible",
                                verification_receipt=rm)
            self.assertEqual(error.exception.code, "PROTECTED_REF")
            self.assertEqual(restarted.complete("candidate-one"), "completed")
            self.assertEqual(IntegrationCoordinator(path, receipt_store=receipts).active, {})
            # The durable journal's concrete policy/admit/complete events must
            # validate against the public schema, not only the runtime parser.
            import jsonschema
            schema = json.loads((Path(__file__).resolve().parents[2] / "schemas" / "control-plane" / "v1" / "execution-fabric.schema.json").read_text(encoding="utf-8"))
            for line in path.read_text(encoding="utf-8").splitlines():
                jsonschema.validate(json.loads(line), schema)

    def test_verifier_hook_requires_assignment_source_and_pass(self):
        registered = host(); assignment, _ = resolve_placement(requirements(), [candidate()], {registered.host_id: registered},
                                                               {registered.host_id: heartbeat(registered)}, {"pool-one": pool()},
                                                               now_epoch=1787918400, created_at=NOW)
        receipt = receipt_for(assignment)
        with tempfile.TemporaryDirectory() as temp:
            receipts = VerificationReceiptStore(Path(temp) / "receipts.jsonl", verification_keys={"controller/verifier-one": "test-key"})
            with self.assertRaises(ReconciliationError) as error:
                verify_candidate_result(assignment=assignment, receipt=receipt, candidate_id="candidate-one",
                                        result_commit=RESULT, diff_digest="c" * 64, scope_digest="d" * 64,
                                        gate_digest="e" * 64, result_ref="cursor/candidate", receipt_store=receipts)
            self.assertEqual(error.exception.code, "VERIFIER_RECEIPT_NOT_REGISTERED")
            receipts.issue(receipt); receipt = receipts.get(receipt.receipt_id)
            self.assertEqual(verify_candidate_result(assignment=assignment, receipt=receipt, candidate_id="candidate-one",
                                                     result_commit=RESULT, diff_digest="c" * 64, scope_digest="d" * 64,
                                                     gate_digest="e" * 64, result_ref="cursor/candidate", receipt_store=receipts), "verified")
            with self.assertRaises(ReconciliationError) as error:
                verify_candidate_result(assignment=assignment, receipt=receipt, candidate_id="candidate-other",
                                    result_commit=RESULT, diff_digest="c" * 64, scope_digest="d" * 64,
                                    gate_digest="e" * 64, result_ref="cursor/candidate", receipt_store=receipts)
            self.assertEqual(error.exception.code, "CANDIDATE_MISMATCH")
            with self.assertRaises(SchemaError) as error:
                Assignment.from_dict({key: value for key, value in assignment.to_dict().items() if key != "candidate_id"})
            self.assertEqual(error.exception.code, "MISSING_FIELD")
            unknown = VerificationReceipt.build(receipt_id="receipt-unknown", assignment_digest=assignment.assignment_digest,
                                                 source_sha=assignment.source_sha, candidate_id="candidate-one", result_commit=RESULT,
                                                 diff_digest="c" * 64, scope_digest="d" * 64, gate_digest="e" * 64,
                                                 verifier_identity="controller/not-registered", verified_at=NOW)
            with self.assertRaises(ReconciliationError) as error:
                receipts.issue(unknown)
            self.assertEqual(error.exception.code, "VERIFIER_UNREGISTERED")


if __name__ == "__main__":
    unittest.main(verbosity=2)

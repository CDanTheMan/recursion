"""Adversarial, source-only coverage for the orchestration facade."""
from __future__ import annotations

import importlib.util
import copy
import json
import sys
import subprocess
import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import mvp_kernel as kernel
import mvp_contracts as contracts
from execution_fabric import (DurableFabricStore, PauseGuard, PlacementRequirements,
                              HostRegistration, HostHeartbeat, PlacementCandidate, PoolStatus)
import mvp_orchestrator as orchestrator
from mvp_orchestrator import AuthorityAnchor, MVPOrchestrator, OrchestrationError, VerificationRecord


def _packet():
    path = ROOT / "scripts/tests/mvp-kernel.test.py"
    spec = importlib.util.spec_from_file_location("kernel_fixture", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.packet()


def _fabric_inputs(packet, *, role="implementer", task_id=None):
    import execution_fabric as fabric
    task = packet["task"]
    task_id = task["id"] if task_id is None else task_id
    host = fabric.HostRegistration.build(host_id="host-one", capabilities=("workspace-edit",),
                                         operating_system="linux", architectures=("x86_64",),
                                         sandbox_profiles=("workspace",), network_profiles=("provider-only",),
                                         trust_class="registered", max_concurrency=4,
                                         workload_concurrency={role: 4}, registered_at=task["created_at"])
    heartbeat = fabric.HostHeartbeat(host.host_id, host.registration_digest, 1, task["created_at"], 1)
    candidate = fabric.PlacementCandidate("candidate-one", "engine-one", "provider-one", "pool-one", "model-one",
                                          host.host_id, "workspace", "provider-only", ("workspace-edit",), "linux",
                                          "included", 0.0, (role,))
    req = fabric.PlacementRequirements(task_id, task["project_id"], role, tuple(task["requested_capabilities"]),
                                       "linux", "workspace", "provider-only", ("included",), 0.0, None, (), (),
                                       task["source_sha"], "subscription-first", None, task["source_repository"],
                                       task["source_branch"], "0" * 64, {}, tuple(task["allowed_paths"]),
                                       task["gate_digest"], "verified-integration-only")
    return req, candidate, host, heartbeat, {"pool-one": fabric.PoolStatus("pool-one", "included", (role,),
        (task["project_id"],), ("model-one",), 4, 0, 4, "weekly", False, 0.0, None)}


def _verifier_packet():
    source = _packet().to_dict()
    task = copy.deepcopy(source["task"])
    task.update(id="task-verifier", depth=0, parent_task_id=None, parent_task_digest=None,
                budget_id="budget-verifier", task_digest="")
    task["task_digest"] = contracts.canonical_digest(task)
    budget = copy.deepcopy(source["budget"])
    budget.update(id="budget-verifier", task_id="task-verifier", task_digest=task["task_digest"],
                  parent_budget_id=None, budget_digest="")
    budget["budget_digest"] = contracts.canonical_digest(budget)
    assignment = copy.deepcopy(source["assignment"])
    assignment.update(id="assignment-verifier", task_id="task-verifier", task_digest=task["task_digest"],
                      assignment_digest="")
    assignment["assignment_digest"] = contracts.canonical_digest(assignment)
    grant = copy.deepcopy(source["grant"])
    grant.update(id="grant-verifier", task_id="task-verifier", task_digest=task["task_digest"], grant_digest="")
    grant["grant_digest"] = contracts.canonical_digest(grant)
    return kernel.build_packet(supervisor=source["supervisor"], task=task, assignment=assignment,
                               budget=budget, grant=grant, supervisor_digest=source["supervisor_digest"])


def _child_packet(parent):
    """Build the smallest valid child used only to exercise fabric anchors."""
    task = json.loads(json.dumps(dict(parent["task"])))
    task.update(id="child-fabric", depth=1, parent_task_id=task["id"],
                parent_task_digest=task["task_digest"], budget_id="budget-child-fabric", task_digest="")
    task["task_digest"] = contracts.canonical_digest(task)
    budget = json.loads(json.dumps(dict(parent["budget"])))
    budget.update(id="budget-child-fabric", task_id=task["id"], task_digest=task["task_digest"],
                  parent_budget_id=parent["budget"]["id"], budget_digest="")
    budget["budget_digest"] = contracts.canonical_digest(budget)
    assignment = json.loads(json.dumps(dict(parent["assignment"])))
    assignment.update(id=parent["assignment"]["id"], task_id=task["id"], task_digest=task["task_digest"],
                      assignment_digest="")
    assignment["assignment_digest"] = contracts.canonical_digest(assignment)
    grant = json.loads(json.dumps(dict(parent["grant"])))
    grant.update(id=parent["grant"]["id"], task_id=task["id"], task_digest=task["task_digest"], grant_digest="")
    grant["grant_digest"] = contracts.canonical_digest(grant)
    return kernel.spawn_child(parent, task=task, assignment=assignment, budget=budget, grant=grant,
                              expected_parent=parent)


class OrchestratorTest(unittest.TestCase):
    def test_kernel_bootstrap_survives_module_class_spoof_and_preimport_patches(self):
        """Consumers fail closed when the kernel is poisoned before import."""
        payload = json.dumps(_packet().to_dict(), sort_keys=True)
        script = f"""
import json, sys
from pathlib import Path
from types import ModuleType
sys.path.insert(0, {str(ROOT / 'scripts').__repr__()})
import mvp_kernel as kernel
body = json.loads({payload!r})
genuine = kernel.TaskPacket(body, body['packet_digest'])
class SpoofedKernelModule(ModuleType):
    def __getattribute__(self, name):
        if name == 'TaskPacket':
            return type('ForgedTaskPacket', (), {{}})
        if name == 'KernelError':
            return RuntimeError
        if name == 'validate_packet':
            return lambda *args, **kwargs: args[0]
        return ModuleType.__getattribute__(self, name)
kernel.__class__ = SpoofedKernelModule
# Also poison the actual module dictionary, covering callers that bypass the
# spoofed lookup with a pre-import public-symbol patch.
kernel.TaskPacket = type('ForgedTaskPacket', (), {{}})
kernel.KernelError = RuntimeError
kernel.validate_packet = lambda *args, **kwargs: args[0]
forged = object()
sys.modules.pop('execution_fabric', None)
sys.modules.pop('mvp_orchestrator', None)
import execution_fabric as fabric
import mvp_orchestrator as orchestrator
try:
    fabric._MVP_PACKET_BOUNDARY(genuine)
except fabric.AdmissionError:
    pass
else:
    raise AssertionError('fabric accepted a packet after kernel bootstrap poisoning')
import tempfile
with tempfile.TemporaryDirectory() as temp:
    controller = orchestrator.MVPOrchestrator(
        fabric=fabric.DurableFabricStore(Path(temp) / 'fabric.jsonl', root=temp))
    try:
        controller.validate_authority(forged)
    except orchestrator.OrchestrationError:
        pass
    else:
        raise AssertionError('orchestrator accepted a packet after kernel bootstrap poisoning')
"""
        result = subprocess.run([sys.executable, "-c", script], cwd=str(ROOT / "scripts"),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_preimport_trusted_issuance_globals_cannot_admit_an_exact_copy(self):
        """Consumers reject an exact-copy packet if the kernel graph is poisoned."""
        payload = json.dumps(_packet().to_dict(), sort_keys=True)
        script_template = f"""
import copy, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, {str(ROOT / 'scripts').__repr__()})
import mvp_kernel as kernel
source = json.loads({payload!r})
issued = kernel.build_packet(
    supervisor=source['supervisor'], task=source['task'],
    assignment=source['assignment'], budget=source['budget'],
    grant=source['grant'], supervisor_digest=source['supervisor_digest'])
assert kernel.validate_packet(issued) is issued
copy_body = copy.deepcopy(issued.to_dict())
exact_copy = kernel.TaskPacket(copy_body, issued.packet_digest)
try:
    kernel.validate_packet(exact_copy)
except kernel.KernelError:
    pass
else:
    raise AssertionError('kernel accepted an unissued exact-copy packet')

build_cells = dict(zip(kernel.build_packet.__code__.co_freevars,
                       kernel.build_packet.__closure__ or ()))
build_impl = build_cells['build_impl'].cell_contents
trusted = build_impl.__globals__
assert trusted[__POISON_NAME__] is not None
replacement = lambda *args, **kwargs: args[0] if args else None
if __CLOSURE_POISON__:
    for name, cell in zip(build_cells['enroll'].cell_contents.__code__.co_freevars,
                          build_cells['enroll'].cell_contents.__closure__ or ()):
        if name == __CLOSURE_NAME__:
            cell.cell_contents = replacement
            break
    else:
        raise AssertionError('issuance closure cell missing')
trusted[__POISON_NAME__] = replacement
sys.modules.pop('execution_fabric', None)
sys.modules.pop('mvp_orchestrator', None)
import execution_fabric as fabric
import mvp_orchestrator as orchestrator
assert fabric._capture_kernel_graph() is None
assert orchestrator._capture_kernel_graph() is None
for candidate in (issued, exact_copy):
    try:
        fabric._MVP_PACKET_BOUNDARY(candidate)
    except fabric.AdmissionError:
        pass
    else:
        raise AssertionError('fabric admitted a packet after issuance-graph poisoning')
with tempfile.TemporaryDirectory() as temp:
    controller = orchestrator.MVPOrchestrator(
        fabric=fabric.DurableFabricStore(Path(temp) / 'fabric.jsonl', root=temp))
    for candidate in (issued, exact_copy):
        try:
            controller.validate_authority(candidate)
        except orchestrator.OrchestrationError:
            pass
        else:
            raise AssertionError('orchestrator admitted a packet after issuance-graph poisoning')
        """
        for poison_name in ("_require_issued_packet", "_packet_issue"):
            script = script_template.replace("__POISON_NAME__", repr(poison_name))
            script = script.replace("__CLOSURE_POISON__", "False")
            script = script.replace("__CLOSURE_NAME__", repr(poison_name.removeprefix("_")))
            result = subprocess.run([sys.executable, "-c", script], cwd=str(ROOT / "scripts"),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0,
                             f"{poison_name}: {result.stderr or result.stdout}")
        for poison_name, closure_name in (("_require_issued_packet", "require_issued"),
                                          ("_packet_issue", "issue")):
            script = script_template.replace("__POISON_NAME__", repr(poison_name))
            script = script.replace("__CLOSURE_POISON__", "True")
            script = script.replace("__CLOSURE_NAME__", repr(closure_name))
            result = subprocess.run([sys.executable, "-c", script], cwd=str(ROOT / "scripts"),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0,
                             f"{poison_name}/{closure_name}: {result.stderr or result.stdout}")

    def test_preimport_validator_global_and_closure_pair_is_reject_only(self):
        """A selective validator cannot replace the sealed kernel graph."""
        payload = json.dumps(_packet().to_dict(), sort_keys=True)
        script = f"""
import copy, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, {str(ROOT / 'scripts').__repr__()})
import mvp_kernel as kernel
source = json.loads({payload!r})
issued = kernel.build_packet(
    supervisor=source['supervisor'], task=source['task'],
    assignment=source['assignment'], budget=source['budget'],
    grant=source['grant'], supervisor_digest=source['supervisor_digest'])
assert kernel.validate_packet(issued) is issued
copy_body = copy.deepcopy(issued.to_dict())
exact_copy = kernel.TaskPacket(copy_body, issued.packet_digest)
try:
    kernel.validate_packet(exact_copy)
except kernel.KernelError:
    pass
else:
    raise AssertionError('kernel accepted an unissued exact-copy packet')

# Replace both the trusted-global name and the enroll closure cell with a
# same-named, module-tagged function that rejects only the attestation shape.
replacement_ns = {{'kernel': kernel}}
exec('''def _validate_packet(packet, *args, **kwargs):
    if getattr(packet, "packet_digest", None) == "0" * 64:
        raise kernel.KernelError("malformed challenge")
    return packet
''', replacement_ns)
replacement = replacement_ns['_validate_packet']
replacement.__module__ = 'mvp_kernel'
build_cells = dict(zip(kernel.build_packet.__code__.co_freevars,
                       kernel.build_packet.__closure__ or ()))
enroll = build_cells['enroll'].cell_contents
trusted = build_cells['build_impl'].cell_contents.__globals__
for name, cell in zip(enroll.__code__.co_freevars, enroll.__closure__ or ()):
    if name == 'validate':
        cell.cell_contents = replacement
        break
else:
    raise AssertionError('validator closure cell missing')
trusted['_validate_packet'] = replacement

sys.modules.pop('execution_fabric', None)
sys.modules.pop('mvp_orchestrator', None)
import execution_fabric as fabric
import mvp_orchestrator as orchestrator
assert fabric._capture_kernel_graph() is None
assert orchestrator._capture_kernel_graph() is None
for candidate in (issued, exact_copy):
    try:
        fabric._MVP_PACKET_BOUNDARY(candidate)
    except fabric.AdmissionError:
        pass
    else:
        raise AssertionError('fabric admitted a packet after paired validator poisoning')
with tempfile.TemporaryDirectory() as temp:
    controller = orchestrator.MVPOrchestrator(
        fabric=fabric.DurableFabricStore(Path(temp) / 'fabric.jsonl', root=temp))
    for candidate in (issued, exact_copy):
        try:
            controller.validate_authority(candidate)
        except orchestrator.OrchestrationError:
            pass
        else:
            raise AssertionError('orchestrator admitted a packet after paired validator poisoning')

"""
        result = subprocess.run([sys.executable, "-c", script], cwd=str(ROOT / "scripts"),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_class_helper_replacements_cannot_bypass_mvp_admission_or_durability(self):
        with TemporaryDirectory() as d:
            packet = _packet(); req, candidate, host, heartbeat, pools = _fabric_inputs(packet)
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            controller = MVPOrchestrator(fabric=fabric)
            forged = copy.deepcopy(controller._mvp_reservation(packet, req, None))
            forged["budget"]["token_units"] += 1
            forged["budget"]["reservation_digest"] = orchestrator._value_digest(
                {key: value for key, value in forged["budget"].items() if key != "reservation_digest"})
            args = dict(requirements=req, candidates=[candidate], hosts={host.host_id: host},
                        heartbeats={host.host_id: heartbeat}, pools=pools,
                        lease_id="lease-helper-forge", attempt_id="attempt-helper-forge",
                        remote_session_id="session-helper-forge", now=packet["task"]["created_at"],
                        expires_at="2026-09-01T12:00:00Z", mvp_packet=packet,
                        mvp_reservation=forged)
            with patch.object(DurableFabricStore, "_validate_mvp_reservation",
                              lambda *a, **k: None):
                with self.assertRaises(Exception):
                    fabric.admit_placement(**args)
            self.assertNotIn("lease-helper-forge", fabric.leases)

            with patch.object(DurableFabricStore, "_create_lease_locked",
                              lambda *a, **k: {}):
                assignment, _ = fabric.admit_placement(
                    **{**args, "lease_id": "lease-helper-noop", "attempt_id": "attempt-helper-noop",
                       "remote_session_id": "session-helper-noop",
                       "mvp_reservation": controller._mvp_reservation(packet, req, None)})
            self.assertIsNotNone(assignment)
            self.assertIn("lease-helper-noop", fabric.leases)
            self.assertIn("lease-helper-noop", DurableFabricStore(
                Path(d) / "fabric.jsonl", root=d).leases)

    def test_mvp_admission_rejects_caller_supplied_internal_capabilities(self):
        with TemporaryDirectory() as d:
            packet = _packet(); req, candidate, host, heartbeat, pools = _fabric_inputs(packet)
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            controller = MVPOrchestrator(fabric=fabric)
            reservation = controller._mvp_reservation(packet, req, None)
            common = dict(requirements=req, candidates=[candidate], hosts={host.host_id: host},
                          heartbeats={host.host_id: heartbeat}, pools=pools,
                          lease_id="lease-capability", attempt_id="attempt-capability",
                          remote_session_id="session-capability", now=packet["task"]["created_at"],
                          expires_at="2026-09-01T12:00:00Z", mvp_packet=packet,
                          mvp_reservation=reservation)
            for key in ("_reservation_validator", "_lease_creator", "_reload_helper"):
                with self.assertRaises(Exception):
                    fabric.admit_placement(**common, **{key: lambda *a, **k: None})

    def test_kernel_authority_binding_rejects_unissued_packets_after_validator_patch(self):
        packet = _packet()
        forged_body = packet.to_dict()
        forged_body["task"]["acceptance"] = "forged"
        forged_body.pop("packet_digest")
        forged_body["packet_digest"] = contracts.canonical_digest(forged_body)
        forged = kernel.TaskPacket(forged_body, forged_body["packet_digest"])
        req, candidate, host, heartbeat, pools = _fabric_inputs(packet)
        original = kernel.validate_packet
        try:
            # The consumer was installed before this patch, but the object is
            # intentionally constructed while the public kernel name is forged.
            kernel.validate_packet = lambda *args, **kwargs: args[0]
            with TemporaryDirectory() as d:
                o = MVPOrchestrator(fabric=DurableFabricStore(Path(d) / "fabric.jsonl", root=d))
                with self.assertRaises(OrchestrationError):
                    o.validate_authority(forged)
                with self.assertRaises(OrchestrationError):
                    o.validate_authority(forged, _packet_type=kernel.TaskPacket,
                                         _packet_validator=lambda *_a, **_k: forged,
                                         _kernel_error=kernel.KernelError)
                with self.assertRaises(OrchestrationError):
                    o.dispatch(forged, requirements=req, candidates=[candidate],
                               hosts={host.host_id: host}, heartbeats={host.host_id: heartbeat},
                               pools=pools, lease_id="lease-forged", attempt_id="attempt-forged",
                               remote_session_id="session-forged", now=packet["task"]["created_at"],
                               expires_at="2026-09-01T12:00:00Z")
                # Class-level unbound calls use the same closure-guarded path.
                with self.assertRaises(OrchestrationError):
                    MVPOrchestrator.dispatch(o, forged, requirements=req, candidates=[candidate],
                                             hosts={host.host_id: host}, heartbeats={host.host_id: heartbeat},
                                             pools=pools, lease_id="lease-forged-2", attempt_id="attempt-forged-2",
                                             remote_session_id="session-forged-2", now=packet["task"]["created_at"],
                                             expires_at="2026-09-01T12:00:00Z")
        finally:
            kernel.validate_packet = original

    def test_public_operation_descriptors_are_callable_for_unbound_and_bound_calls(self):
        self.assertTrue(callable(MVPOrchestrator.dispatch))
        self.assertTrue(callable(MVPOrchestrator.verify))
        self.assertTrue(callable(MVPOrchestrator.review_intent))
        with TemporaryDirectory() as d:
            packet = _packet()
            req, candidate, host, heartbeat, pools = _fabric_inputs(packet)
            o = MVPOrchestrator(fabric=DurableFabricStore(Path(d) / "fabric.jsonl", root=d))
            record = MVPOrchestrator.dispatch(
                o, packet, requirements=req, candidates=[candidate],
                hosts={host.host_id: host}, heartbeats={host.host_id: heartbeat}, pools=pools,
                lease_id="lease-unbound", attempt_id="attempt-unbound",
                remote_session_id="session-unbound", now=packet["task"]["created_at"],
                expires_at="2026-09-01T12:00:00Z")
            self.assertEqual(record.task_id, packet["task"]["id"])

    def test_rejects_mapping_and_digest_only_authority(self):
        with TemporaryDirectory() as d:
            o = MVPOrchestrator(fabric=DurableFabricStore(Path(d) / "fabric.jsonl", root=d))
            p = _packet()
            with self.assertRaises(OrchestrationError):
                o.validate_authority(p.to_dict())  # type: ignore[arg-type]

    def test_pause_is_checked_before_any_fabric_mutation(self):
        with TemporaryDirectory() as d:
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            o = MVPOrchestrator(fabric=fabric, pause_guard=PauseGuard(paused=True))
            with self.assertRaises(Exception):
                o.reconcile_restart(now="2026-08-31T12:00:00Z")
            self.assertEqual(fabric.leases, {})

    def test_verification_requires_distinct_task_and_controller_receipt(self):
        with TemporaryDirectory() as d:
            o = MVPOrchestrator(fabric=DurableFabricStore(Path(d) / "fabric.jsonl", root=d))
            p = _packet()
            with self.assertRaises(OrchestrationError) as cm:
                o.verify(p, verifier_packet=p, receipt={})
            self.assertIn(cm.exception.code, {"SELF_VERIFICATION", "VERIFIER_AUTH_REQUIRED", "VERIFIER_REJECTED"})

    def test_review_intent_cannot_bypass_verification(self):
        with TemporaryDirectory() as d:
            o = MVPOrchestrator(fabric=DurableFabricStore(Path(d) / "fabric.jsonl", root=d))
            with self.assertRaises(OrchestrationError) as cm:
                o.review_intent(None, candidate_id="candidate-one", project_id="project-one",
                                source_sha="0" * 40, result_commit="1" * 40,
                                assignment={}, diff_digest="0" * 64, scope_digest="0" * 64,
                                gate_digest="0" * 64, result_ref="review/one")
            self.assertEqual(cm.exception.code, "REVIEW_NOT_READY")

    def test_dispatch_is_durable_content_addressed_and_malformed_inputs_are_typed(self):
        with TemporaryDirectory() as d:
            p = _packet(); req, candidate, host, heartbeat, pools = _fabric_inputs(p)
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            o = MVPOrchestrator(fabric=fabric)
            record = o.dispatch(p, requirements=req, candidates=[candidate], hosts={host.host_id: host},
                                heartbeats={host.host_id: heartbeat}, pools=pools, lease_id="lease-one",
                                attempt_id="attempt-one", remote_session_id="session-one",
                                now=p["task"]["created_at"], expires_at="2026-09-01T12:00:00Z")
            self.assertEqual(record.record_digest, orchestrator._record_digest(record.to_dict()))
            self.assertIn("budget", fabric.leases["lease-one"]["reservation"])
            with self.assertRaises(OrchestrationError):
                o.dispatch(p.to_dict(), requirements=req, candidates=[], hosts={}, heartbeats={}, pools={},
                           lease_id="bad", attempt_id="bad", remote_session_id="bad",
                           now=p["task"]["created_at"], expires_at="2026-09-01T12:00:00Z")

    def test_sibling_budget_reservation_replays_and_releases_with_terminal_lease(self):
        with TemporaryDirectory() as d:
            p = _packet(); req, candidate, host, heartbeat, pools = _fabric_inputs(p)
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            o = MVPOrchestrator(fabric=fabric)
            o.dispatch(p, requirements=req, candidates=[candidate], hosts={host.host_id: host},
                       heartbeats={host.host_id: heartbeat}, pools=pools, lease_id="lease-one",
                       attempt_id="attempt-one", remote_session_id="session-one",
                       now=p["task"]["created_at"], expires_at="2026-09-01T12:00:00Z")
            restarted = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            self.assertEqual(len(restarted.active_reservations()), 1)
            self.assertIn("budget", restarted.active_reservations()[0])
            # The same persisted lease is idempotent; it does not double reserve.
            replay_req = replace(req, mvp_authority=fabric.leases["lease-one"]["reservation"]["authority"])
            same, _ = restarted.admit_placement(replay_req, [candidate], {host.host_id: host}, {host.host_id: heartbeat},
                                                 pools, lease_id="lease-one", attempt_id="attempt-one",
                                                 remote_session_id="session-one", now=p["task"]["created_at"],
                                                 expires_at="2026-09-01T12:00:00Z",
                                                 mvp_packet=p,
                                                 mvp_reservation=fabric.leases["lease-one"]["reservation"] | {})
            self.assertIsNotNone(same)
            self.assertEqual(restarted.accept_result(attempt_id="attempt-one", lease_id="lease-one",
                                                     assignment_digest_value=same.assignment_digest, result_digest="1" * 64,
                                                     status="succeeded", observed_at=p["task"]["created_at"],
                                                     controller_now=p["task"]["created_at"]), "accepted")
            self.assertEqual(restarted.active_reservations(), ())

    def test_replay_validates_nested_mvp_reservation_before_idempotent_return(self):
        with TemporaryDirectory() as d:
            p = _packet(); req, candidate, host, heartbeat, pools = _fabric_inputs(p)
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            o = MVPOrchestrator(fabric=fabric)
            o.dispatch(p, requirements=req, candidates=[candidate], hosts={host.host_id: host},
                       heartbeats={host.host_id: heartbeat}, pools=pools, lease_id="lease-one",
                       attempt_id="attempt-one", remote_session_id="session-one",
                       now=p["task"]["created_at"], expires_at="2026-09-01T12:00:00Z")
            forged = copy.deepcopy(fabric.leases["lease-one"]["reservation"])
            forged["budget"]["token_units"] += 1
            replay_req = replace(req, mvp_authority=forged["authority"])
            with self.assertRaises(Exception):
                fabric.admit_placement(replay_req, [candidate], {host.host_id: host}, {host.host_id: heartbeat},
                                       pools, lease_id="lease-one", attempt_id="attempt-one",
                                       remote_session_id="session-one", now=p["task"]["created_at"],
                                       expires_at="2026-09-01T12:00:00Z", mvp_reservation=forged)

    def test_mvp_reservation_requires_request_authority_bridge_and_view_is_copy_safe(self):
        with TemporaryDirectory() as d:
            p = _packet(); req, candidate, host, heartbeat, pools = _fabric_inputs(p)
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            o = MVPOrchestrator(fabric=fabric)
            o.dispatch(p, requirements=req, candidates=[candidate], hosts={host.host_id: host},
                       heartbeats={host.host_id: heartbeat}, pools=pools, lease_id="lease-one",
                       attempt_id="attempt-one", remote_session_id="session-one",
                       now=p["task"]["created_at"], expires_at="2026-09-01T12:00:00Z")
            view = fabric.active_reservations()
            view[0]["budget"]["token_units"] = 99
            self.assertNotEqual(fabric.active_reservations()[0]["budget"]["token_units"], 99)
            with self.assertRaises(Exception):
                fabric.admit_placement(req, [candidate], {host.host_id: host}, {host.host_id: heartbeat}, pools,
                                       lease_id="lease-one", attempt_id="attempt-one",
                                       remote_session_id="session-one", now=p["task"]["created_at"],
                                       expires_at="2026-09-01T12:00:00Z",
                                       mvp_reservation=fabric.leases["lease-one"]["reservation"])

    def test_authority_forge_with_self_signed_request_is_rejected_by_direct_fabric(self):
        with TemporaryDirectory() as d:
            p = _packet(); req, candidate, host, heartbeat, pools = _fabric_inputs(p)
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            o = MVPOrchestrator(fabric=fabric)
            original = kernel.validate_packet
            forged_body = p.to_dict()
            forged_body["task"]["acceptance"] = "forged"
            forged_body.pop("packet_digest")
            forged_body["packet_digest"] = contracts.canonical_digest(forged_body)
            forged_packet = kernel.TaskPacket(forged_body, forged_body["packet_digest"])
            try:
                # A patched public validator must not turn a manually-created
                # packet into a trusted fabric authority anchor.
                kernel.validate_packet = lambda *args, **kwargs: args[0]
                reservation = o._mvp_reservation(forged_packet, req, None)
                with self.assertRaises(Exception):
                    fabric.admit_placement(req, [candidate], {host.host_id: host},
                                           {host.host_id: heartbeat}, pools, lease_id="lease-forge",
                                           attempt_id="attempt-forge", remote_session_id="session-forge",
                                           now=p["task"]["created_at"], expires_at="2026-09-01T12:00:00Z",
                                           mvp_packet=forged_packet, mvp_reservation=reservation)
                with self.assertRaises(Exception):
                    fabric.admit_placement(req, [candidate], {host.host_id: host}, {host.host_id: heartbeat},
                                           pools, lease_id="lease-forge-2", attempt_id="attempt-forge-2",
                                           remote_session_id="session-forge-2", now=p["task"]["created_at"],
                                           expires_at="2026-09-01T12:00:00Z", mvp_packet=forged_packet,
                                           mvp_reservation=reservation, _packet_boundary=lambda *_a, **_k: forged_packet)
            finally:
                kernel.validate_packet = original

    def test_direct_budget_forge_is_rejected_against_trusted_packet(self):
        with TemporaryDirectory() as d:
            p = _packet(); req, candidate, host, heartbeat, pools = _fabric_inputs(p)
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            o = MVPOrchestrator(fabric=fabric)
            forged = copy.deepcopy(o._mvp_reservation(p, req, None))
            forged["budget"]["token_units"] += 1
            forged["budget"]["reservation_digest"] = orchestrator._value_digest(
                {k: v for k, v in forged["budget"].items() if k != "reservation_digest"})
            with self.assertRaises(Exception):
                fabric.admit_placement(req, [candidate], {host.host_id: host}, {host.host_id: heartbeat}, pools,
                                       lease_id="lease-budget-forge", attempt_id="attempt-budget-forge",
                                       remote_session_id="session-budget-forge", now=p["task"]["created_at"],
                                       expires_at="2026-09-01T12:00:00Z", mvp_packet=p,
                                       mvp_reservation=forged)

    def test_child_parent_swap_rebuild_and_omission_are_rejected(self):
        with TemporaryDirectory() as d:
            parent = _packet(); child = _child_packet(parent)
            req, candidate, host, heartbeat, pools = _fabric_inputs(child)
            fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            o = MVPOrchestrator(fabric=fabric)
            reservation = o._mvp_reservation(child, req, parent)
            common = dict(requirements=req, candidates=[candidate], hosts={host.host_id: host},
                          heartbeats={host.host_id: heartbeat}, pools=pools, lease_id="lease-child",
                          attempt_id="attempt-child", remote_session_id="session-child",
                          now=child["task"]["created_at"], expires_at="2026-09-01T12:00:00Z",
                          mvp_packet=child, mvp_reservation=reservation)
            with self.assertRaises(Exception):
                fabric.admit_placement(**common)
            with self.assertRaises(Exception):
                fabric.admit_placement(**{**common, "mvp_parent": _verifier_packet()})
            rebuilt = replace(parent, packet_digest="f" * 64)
            with self.assertRaises(Exception):
                fabric.admit_placement(**{**common, "mvp_parent": rebuilt})

    def test_forged_passing_verification_record_never_enters_review(self):
        with TemporaryDirectory() as d:
            o = MVPOrchestrator(fabric=DurableFabricStore(Path(d) / "fabric.jsonl", root=d))
            forged = VerificationRecord("task-one", "1" * 64, "2" * 64, "task-verifier", "3" * 64,
                                        "4" * 64, "pass", ())
            with self.assertRaises(OrchestrationError) as cm:
                o.review_intent(forged, candidate_id="candidate-one", project_id="project-one",
                                source_sha="a" * 40, result_commit="b" * 40, assignment={},
                                diff_digest="c" * 64, scope_digest="d" * 64, gate_digest="e" * 64,
                                result_ref="review/one")
            self.assertIn(cm.exception.code, {"REVIEW_NOT_READY", "RECORD_UNAUTHENTICATED"})
            with self.assertRaises(Exception):
                o._review_intent_impl(forged, candidate_id="candidate-one", project_id="project-one",
                                      source_sha="a" * 40, result_commit="b" * 40, assignment={},
                                      diff_digest="c" * 64, scope_digest="d" * 64, gate_digest="e" * 64,
                                      result_ref="review/one",
                                      _record_require=lambda record, expected: record)

    def test_record_issuance_has_no_module_enrollment_capability(self):
        self.assertFalse(hasattr(kernel, "_FACTORY_PROVENANCE"))
        self.assertFalse(hasattr(orchestrator, "_issue_record"))
        self.assertFalse(hasattr(orchestrator, "_make_record_issuance"))
        self.assertFalse(hasattr(kernel, "_packet_issue"))
        self.assertFalse(hasattr(kernel, "_new_packet_issuance"))
        self.assertFalse(any("issue" in name.lower() and "require" not in name.lower() and callable(value)
                             for name, value in vars(kernel).items()))
        self.assertFalse(any("issue" in name.lower() and callable(value)
                             for name, value in vars(orchestrator).items()))

    def test_verify_binds_fabric_target_and_distinct_verifier_dispatch(self):
        with TemporaryDirectory() as d:
            p = _packet(); v = _verifier_packet(); fabric = DurableFabricStore(Path(d) / "fabric.jsonl", root=d)
            target_req, target_candidate, host, hb, target_pools = _fabric_inputs(p)
            verifier_req, verifier_candidate, _, _, verifier_pools = _fabric_inputs(v, role="verifier")
            o = MVPOrchestrator(fabric=fabric)
            o.dispatch(p, requirements=target_req, candidates=[target_candidate], hosts={host.host_id: host},
                       heartbeats={host.host_id: hb}, pools=target_pools, lease_id="lease-target",
                       attempt_id="attempt-target", remote_session_id="session-target",
                       now=p["task"]["created_at"], expires_at="2026-09-01T12:00:00Z")
            # Use a second eligible pool/host snapshot; durable fabric still serializes by task, not project.
            o.dispatch(v, requirements=verifier_req, candidates=[verifier_candidate], hosts={host.host_id: host},
                       heartbeats={host.host_id: hb}, pools=verifier_pools, lease_id="lease-verifier",
                       attempt_id="attempt-verifier", remote_session_id="session-verifier",
                       now=v["task"]["created_at"], expires_at="2026-09-01T12:00:00Z", verifier=True)
            authority = Path(d) / "authority.key"; authority.write_bytes(b"controller-test-key"); authority.chmod(0o600)
            registry = __import__("execution_fabric").VerificationKeyRegistry.provision(
                Path(d) / "registry.json", authority_key_path=authority,
                verification_keys={"controller/verifier-one": "verifier-key"})
            receipts = __import__("execution_fabric").VerificationReceiptStore(Path(d) / "receipts.jsonl",
                                                                                  verification_registry=registry)
            target_fabric = fabric.lease_for_mvp_assignment(p["assignment"]["assignment_digest"], role="implementer")
            self.assertIsNotNone(target_fabric)
            fabric.accept_result(attempt_id="attempt-target", lease_id="lease-target",
                                 assignment_digest_value=target_fabric["assignment_digest"], result_digest="1" * 64,
                                 status="succeeded", observed_at=p["task"]["created_at"],
                                 controller_now=p["task"]["created_at"])
            verifier_fabric = fabric.lease_for_mvp_assignment(v["assignment"]["assignment_digest"], role="verifier")
            self.assertIsNotNone(verifier_fabric)
            fabric.accept_result(attempt_id="attempt-verifier", lease_id="lease-verifier",
                                 assignment_digest_value=verifier_fabric["assignment_digest"], result_digest="2" * 64,
                                 status="succeeded", observed_at=v["task"]["created_at"],
                                 controller_now=v["task"]["created_at"])
            receipt = __import__("execution_fabric").VerificationReceipt.build(
                receipt_id="receipt-target", assignment_digest=target_fabric["assignment_digest"],
                source_sha=p["task"]["source_sha"], candidate_id="candidate-one", result_commit="b" * 40,
                diff_digest="c" * 64, scope_digest="d" * 64, gate_digest=p["task"]["gate_digest"],
                verifier_identity="controller/verifier-one", verified_at=p["task"]["created_at"])
            receipts.issue(receipt)
            o.receipt_store = receipts
            receipt = receipts.get("receipt-target")
            self.assertIsNotNone(receipt)
            verified = o.verify(p, verifier_packet=v, receipt=receipt)
            self.assertEqual(verified.status, "pass")
            self.assertTrue(verified.record_digest)
            object.__setattr__(verified, "packet_digest", "f" * 64)
            with self.assertRaises(OrchestrationError):
                o.review_intent(verified, candidate_id="candidate-one", project_id="project-one",
                                source_sha=p["task"]["source_sha"], result_commit="b" * 40,
                                assignment={}, diff_digest="c" * 64, scope_digest="d" * 64,
                                gate_digest=p["task"]["gate_digest"], result_ref="review/one",
                                target_packet=p, verifier_packet=v)
            with self.assertRaises(OrchestrationError):
                o.verify(p, verifier_packet=v, receipt=receipt, candidate_id="candidate-swapped")

    def test_public_operations_bind_impls_validators_and_reviewer_seam(self):
        self.assertTrue(hasattr(MVPOrchestrator, "dispatch"))
        self.assertTrue(hasattr(MVPOrchestrator, "verify"))
        self.assertTrue(hasattr(MVPOrchestrator, "review_intent"))

        class Child(MVPOrchestrator):
            def call_dispatch(self, *args, **kwargs):
                return super().dispatch(*args, **kwargs)

        with TemporaryDirectory() as d:
            p = _packet()
            req, candidate, host, heartbeat, pools = _fabric_inputs(p)
            o = Child(fabric=DurableFabricStore(Path(d) / "fabric.jsonl", root=d))
            original = {name: getattr(MVPOrchestrator, name) for name in
                        ("_dispatch_impl", "_verify_impl", "_review_intent_body",
                         "validate_authority")}
            try:
                # These are the exact historical reviewer repros: mutable
                # implementation and validator names must not change issuance.
                MVPOrchestrator._dispatch_impl = lambda *args, **kwargs: "forged-dispatch"
                MVPOrchestrator._verify_impl = lambda *args, **kwargs: "forged-verify"
                MVPOrchestrator._review_intent_body = lambda *args, **kwargs: (None, None, {})
                MVPOrchestrator.validate_authority = lambda *args, **kwargs: AuthorityAnchor(
                    "forged", "1" * 64, "2" * 64, 0, None, "3" * 64)
                o._dispatch_impl = lambda *args, **kwargs: "instance-forged"
                o._verify_impl = lambda *args, **kwargs: "instance-forged"
                o._review_intent_body = lambda *args, **kwargs: (None, None, {})
                o.validate_authority = lambda *args, **kwargs: AuthorityAnchor(
                    "instance-forged", "4" * 64, "5" * 64, 0, None, "6" * 64)

                dispatched = o.call_dispatch(
                    p, requirements=req, candidates=[candidate], hosts={host.host_id: host},
                    heartbeats={host.host_id: heartbeat}, pools=pools, lease_id="lease-one",
                    attempt_id="attempt-one", remote_session_id="session-one",
                    now=p["task"]["created_at"], expires_at="2026-09-01T12:00:00Z")
                self.assertEqual(dispatched.task_id, p["task"]["id"])
                with self.assertRaises(OrchestrationError):
                    o.verify(p, verifier_packet=p, receipt={})
                forged = VerificationRecord("task-one", "1" * 64, "2" * 64,
                                            "task-verifier", "3" * 64, "4" * 64,
                                            "pass", ())
                with self.assertRaises(OrchestrationError):
                    o.review_intent(forged, candidate_id="candidate-one", project_id="project-one",
                                    source_sha="a" * 40, result_commit="b" * 40,
                                    assignment={}, diff_digest="c" * 64,
                                    scope_digest="d" * 64, gate_digest="e" * 64,
                                    result_ref="review/one")
            finally:
                for name, value in original.items():
                    setattr(MVPOrchestrator, name, value)


if __name__ == "__main__":
    unittest.main()

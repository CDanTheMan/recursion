#!/usr/bin/env python3
"""Small, source-only orchestration facade for the Recursion v2 MVP.

The facade owns no durable state.  ``DurableFabricStore`` owns leases, attempts,
results, and restart reconciliation; the contract/kernel modules own packet
authority.  This module only composes those authorities and returns bounded,
immutable-ish event records for a controller to persist or display.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import copy
import weakref
from types import FunctionType, MappingProxyType, ModuleType
from typing import Any, Mapping, Sequence

import mvp_contracts as contracts
import mvp_kernel as kernel
from execution_fabric import (
    Assignment as FabricAssignment,
    DurableFabricStore,
    IntegrationCoordinator,
    PauseGuard,
    PlacementCandidate,
    PlacementRequirements,
    PoolStatus,
    HostHeartbeat,
    HostRegistration,
    VerificationReceipt,
    VerificationReceiptStore,
    verify_candidate_result,
)


class OrchestrationError(ValueError):
    """A fail-closed orchestration admission error."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class AuthorityAnchor:
    task_id: str
    task_digest: str
    packet_digest: str
    depth: int
    parent_task_id: str | None
    supervisor_digest: str


@dataclass(frozen=True)
class DispatchRecord:
    task_id: str
    task_digest: str
    packet_digest: str
    depth: int
    role: str
    mvp_assignment_digest: str
    fabric_assignment_digest: str
    lease_id: str
    attempt_id: str
    candidate_id: str
    engine: str
    model: str
    events: tuple[str, ...]
    source_repository: str = ""
    source_branch: str = ""
    source_sha: str = ""
    gate_digest: str = ""
    allowed_paths_digest: str = ""
    capabilities_digest: str = ""
    record_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "orchestration_dispatch",
                **{key: value for key, value in self.__dict__.items() if not key.startswith("_")},
                "events": list(self.events)}


@dataclass(frozen=True)
class VerificationRecord:
    task_id: str
    task_digest: str
    packet_digest: str
    verifier_task_id: str
    verifier_task_digest: str
    receipt_digest: str
    status: str
    events: tuple[str, ...]
    target_fabric_assignment_digest: str = ""
    target_lease_id: str = ""
    target_attempt_id: str = ""
    candidate_id: str = ""
    result_commit: str = ""
    source_sha: str = ""
    diff_digest: str = ""
    scope_digest: str = ""
    gate_digest: str = ""
    verifier_fabric_assignment_digest: str = ""
    verifier_lease_id: str = ""
    verifier_attempt_id: str = ""
    target_mvp_assignment_digest: str = ""
    verifier_mvp_assignment_digest: str = ""
    target_source_repository: str = ""
    target_source_branch: str = ""
    target_allowed_paths_digest: str = ""
    target_capabilities_digest: str = ""
    record_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "mvp_verification",
                **{key: value for key, value in self.__dict__.items() if not key.startswith("_")},
                "events": list(self.events)}


def _record_digest(value: Mapping[str, Any], field: str = "record_digest") -> str:
    """Digest a strict orchestration record without trusting its digest field."""
    body = dict(value)
    body.pop(field, None)
    try:
        return hashlib.sha256(contracts.canonical_json(body)).hexdigest()
    except Exception as exc:
        raise OrchestrationError("INVALID_RECORD", "orchestration record is not canonical JSON") from exc


def _checked_record(record: VerificationRecord, require_record) -> VerificationRecord:
    require_record(record, VerificationRecord)
    if record.status != "pass":
        raise OrchestrationError("REVIEW_NOT_READY", "record is not a passing verification record")
    raw = record.to_dict()
    if not record.record_digest or record.record_digest != _record_digest(raw):
        raise OrchestrationError("RECORD_UNAUTHENTICATED", "verification record is not factory-authenticated")
    required = (record.task_id, record.task_digest, record.packet_digest,
                record.target_fabric_assignment_digest, record.target_lease_id,
                record.target_attempt_id, record.candidate_id, record.result_commit,
                record.source_sha, record.diff_digest, record.scope_digest,
                record.gate_digest, record.verifier_task_id, record.verifier_task_digest,
                record.verifier_fabric_assignment_digest, record.verifier_lease_id,
                record.verifier_attempt_id, record.target_mvp_assignment_digest,
                record.verifier_mvp_assignment_digest, record.target_source_repository,
                record.target_source_branch, record.target_allowed_paths_digest,
                record.target_capabilities_digest, record.receipt_digest)
    if any(not isinstance(item, str) or not item for item in required):
        raise OrchestrationError("RECORD_UNAUTHENTICATED", "verification record is incomplete")
    return record


def _capture_kernel_graph() -> tuple[type, Any, type] | None:
    """Attest and capture the kernel authority graph at consumer import time.

    ``mvp_kernel`` is a normal, patchable Python module.  A consumer therefore
    must not trust attribute lookup on that module, nor a caller-supplied
    validator/type pair.  Read the real module dictionary through the base C
    ``ModuleType`` implementation, then prove that the public factory wrappers
    still have the expected closure-backed graph.  The manually constructed
    packet challenge proves that the captured validator still enforces the
    issuance ledger.  Failure is represented by ``None`` and leaves every
    authority operation fail-closed.
    """
    try:
        module_dict = ModuleType.__getattribute__(kernel, "__dict__")
        if (type(kernel) is not ModuleType or type(module_dict) is not dict or
                module_dict.get("__name__") != "mvp_kernel"):
            return None

        def closure(function: Any, name: str) -> Any:
            if not isinstance(function, FunctionType):
                raise TypeError("kernel graph node is not a function")
            if function.__module__ != "mvp_kernel":
                raise TypeError("kernel graph module mismatch")
            names = function.__code__.co_freevars
            cells = function.__closure__ or ()
            if name not in names or len(names) != len(cells):
                raise TypeError("kernel graph closure mismatch")
            return cells[names.index(name)].cell_contents

        public = {name: module_dict.get(name) for name in
                  ("TaskPacket", "KernelError", "build_packet", "spawn_child",
                   "retain_context", "validate_packet")}
        build = public["build_packet"]
        spawn = public["spawn_child"]
        retain = public["retain_context"]
        validate_public = public["validate_packet"]
        build_impl = closure(build, "build_impl")
        enroll = closure(build, "enroll")
        issue = closure(enroll, "issue")
        require_issued = closure(enroll, "require_issued")
        enroll_validate = closure(enroll, "validate")
        validator_code = closure(validate_public, "validator_code")
        spawn_impl = closure(spawn, "spawn_impl")
        retain_impl = closure(retain, "retain_impl")
        validator = closure(validate_public, "validate")
        if (build.__code__.co_name != "build_packet" or
                spawn.__code__.co_name != "spawn_child" or
                retain.__code__.co_name != "retain_context" or
                validate_public.__code__.co_name != "validate_packet_public" or
                build_impl.__code__.co_name != "_build_packet_impl" or
                spawn_impl.__code__.co_name != "_spawn_child_impl" or
                retain_impl.__code__.co_name != "_retain_context_impl" or
                validator.__code__.co_name != "_validate_packet" or
                validator.__code__ is not validator_code or
                enroll.__code__.co_name != "enroll"):
            return None

        trusted_globals = build_impl.__globals__
        if type(trusted_globals) is not dict or trusted_globals is module_dict:
            return None
        graph = {name: trusted_globals.get(name) for name in
                 ("TaskPacket", "KernelError", "_build_packet_impl", "_spawn_child_impl",
                  "_retain_context_impl", "_validate_packet", "_make_body",
                  "_validate_semantics", "_packet_issue", "_require_issued_packet")}
        if graph["TaskPacket"] is not public["TaskPacket"] or graph["KernelError"] is not public["KernelError"]:
            return None
        # The public build wrapper exposes ``build_impl`` and therefore its
        # private globals dictionary to a Python caller.  The issuance ledger
        # itself is independently captured by ``enroll``; require both
        # authorities in the attested globals to be the exact closure cells,
        # so replacing either trusted-global name cannot turn an unissued
        # exact-copy packet into an admitted packet.
        if (graph["_packet_issue"] is not issue or
                graph["_require_issued_packet"] is not require_issued or
                graph["_validate_packet"] is not enroll_validate):
            return None
        if (not isinstance(issue, FunctionType) or issue.__module__ != "mvp_kernel" or
                issue.__code__.co_name != "issue" or
                not isinstance(require_issued, FunctionType) or
                require_issued.__module__ != "mvp_kernel" or
                require_issued.__code__.co_name != "require"):
            return None
        packet_type = graph["TaskPacket"]
        kernel_error = graph["KernelError"]
        if not isinstance(packet_type, type) or packet_type.__module__ != "mvp_kernel":
            return None
        # Exercise the issuance authority independently of packet semantics.
        # This is intentionally a well-typed but never-issued packet: a
        # replacement that makes ``require_issued`` an identity function must
        # fail attestation even when the packet validator's separate malformed
        # challenge would fail for an unrelated reason.
        issuance_challenge = packet_type({"packet_digest": "0" * 64}, "0" * 64)
        try:
            require_issued(issuance_challenge)
        except kernel_error:
            pass
        except Exception:
            return None
        else:
            return None
        fields = getattr(packet_type, "__dataclass_fields__", None)
        params = getattr(packet_type, "__dataclass_params__", None)
        if (not isinstance(fields, dict) or tuple(fields) != ("value", "packet_digest") or
                params is None or not params.frozen or
                not isinstance(kernel_error, type) or
                not issubclass(kernel_error, ValueError) or kernel_error.__module__ != "mvp_kernel"):
            return None
        for name in ("_build_packet_impl", "_spawn_child_impl", "_retain_context_impl",
                     "_validate_packet", "_make_body", "_validate_semantics"):
            function = graph[name]
            if (not isinstance(function, FunctionType) or function.__globals__ is not trusted_globals or
                    function.__module__ != "mvp_kernel" or function.__code__.co_name != name):
                return None
        if (build.__globals__ is not module_dict or spawn.__globals__ is not module_dict or
                retain.__globals__ is not module_dict or validate_public.__globals__ is not module_dict or
                validator.__globals__ is not trusted_globals):
            return None
        if (closure(spawn, "enroll") is not enroll or closure(retain, "enroll") is not enroll or
                enroll_validate is not validator):
            return None

        challenge = packet_type({"packet_digest": "0" * 64}, "0" * 64)
        try:
            validator(challenge)
        except kernel_error:
            pass
        except Exception:
            return None
        else:
            return None
        return packet_type, validator, kernel_error
    except Exception:
        return None


def _orchestration_boundary(function):
    """Ensure hostile Python/lower-layer failures remain typed at this facade."""
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except OrchestrationError:
            raise
        except Exception as exc:
            raise OrchestrationError(getattr(exc, "code", "INVALID_INPUT"), str(exc) or "invalid orchestration input") from exc
    wrapped.__name__ = getattr(function, "__name__", "orchestration")
    wrapped.__doc__ = getattr(function, "__doc__", None)
    return wrapped


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise OrchestrationError("INVALID_INPUT", f"{name} must be an object")
    return value


def _anchor(packet: kernel.TaskPacket) -> AuthorityAnchor:
    task = _mapping(packet["task"], "task")
    return AuthorityAnchor(task["id"], task["task_digest"], packet.packet_digest,
                           packet["depth"], task.get("parent_task_id"), packet["supervisor_digest"])


def _value_digest(value: Any) -> str:
    try:
        return hashlib.sha256(contracts.canonical_json(value)).hexdigest()
    except Exception as exc:
        raise OrchestrationError("INVALID_RECORD", "authority projection is not canonical JSON") from exc


def _require_succeeded_result(fabric: DurableFabricStore, lease: Mapping[str, Any], label: str) -> Mapping[str, Any]:
    """Require the durable result/attempt/lease triple for a review leg."""
    lease_id = lease.get("lease_id"); attempt_id = lease.get("attempt_id")
    if not isinstance(lease_id, str) or not isinstance(attempt_id, str):
        raise OrchestrationError("RESULT_REQUIRED", f"{label} durable lease identity is malformed")
    attempt, result = fabric.attempt_result(attempt_id)
    if not isinstance(result, Mapping) or not isinstance(attempt, Mapping):
        raise OrchestrationError("RESULT_REQUIRED", f"{label} has no durable result")
    if (result.get("status") != "succeeded" or lease.get("status") != "succeeded"
            or attempt.get("status") != "succeeded"
            or result.get("lease_id") != lease_id
            or result.get("attempt_id") != attempt_id
            or result.get("assignment_digest") != lease.get("assignment_digest")
            or attempt.get("assignment_digest") != lease.get("assignment_digest")):
        raise OrchestrationError("RESULT_BINDING_MISMATCH", f"{label} durable result is not an exact succeeded lease result")
    return copy.deepcopy(result)


class MVPOrchestrator:
    """Compose packet admission, fabric placement, verification, and integration.

    The object is intentionally ephemeral.  ``events`` is bounded controller output,
    not a competing journal.  Callers must provide the controller-owned receipt store
    when using verification or integration.
    """

    def __init__(self, *, fabric: DurableFabricStore, pause_guard: PauseGuard | None = None,
                 receipt_store: VerificationReceiptStore | None = None,
                 integration: IntegrationCoordinator | None = None,
                 max_events: int = 256):
        if not isinstance(fabric, DurableFabricStore):
            raise OrchestrationError("INVALID_INPUT", "fabric must be DurableFabricStore")
        if pause_guard is not None and not isinstance(pause_guard, PauseGuard):
            raise OrchestrationError("INVALID_INPUT", "pause_guard is invalid")
        if type(max_events) is not int or not 1 <= max_events <= 4096:
            raise OrchestrationError("INVALID_INPUT", "max_events is out of bounds")
        self.fabric = fabric
        self.pause_guard = pause_guard
        self.receipt_store = receipt_store
        self.integration = integration
        self.max_events = max_events
        self._reserved_cost: dict[str, int] = {}
        self.events: list[str] = []

    def _check_pause(self) -> None:
        if self.pause_guard is not None:
            self.pause_guard.assert_open()

    def _event(self, name: str) -> None:
        self.events.append(name)
        if len(self.events) > self.max_events:
            del self.events[:-self.max_events]

    @_orchestration_boundary
    def validate_authority(self, packet: kernel.TaskPacket, *, parent: kernel.TaskPacket | None = None,
                           expected_lineage: Sequence[Any] | None = None,
                           _packet_type: type,
                           _packet_validator: Any,
                           _kernel_error: type[Exception]) -> AuthorityAnchor:
        packet_type = _packet_type
        packet_validator = _packet_validator
        kernel_error = _kernel_error
        if not isinstance(packet, packet_type):
            raise OrchestrationError("INVALID_PACKET", "packet must be immutable TaskPacket")
        try:
            if packet["depth"] == 0:
                packet_validator(packet)
            else:
                if parent is None:
                    raise OrchestrationError("PARENT_REQUIRED", "non-root admission requires its trusted parent")
                packet_validator(packet, expected_parent=parent,
                                 expected_parent_digest=parent.packet_digest,
                                 expected_lineage=expected_lineage)
        except (kernel_error, contracts.ContractError) as exc:
            raise OrchestrationError("AUTHORITY_REJECTED", str(exc)) from exc
        if packet["depth"] not in (0, 1, 2):
            raise OrchestrationError("DEPTH_REJECTED", "orchestration depth exceeds 2")
        try:
            return _anchor(packet)
        except (KeyError, TypeError, ValueError) as exc:
            raise OrchestrationError("AUTHORITY_REJECTED", "packet authority projection is malformed") from exc

    @staticmethod
    def _mvp_reservation(packet: kernel.TaskPacket, req: PlacementRequirements,
                         parent: kernel.TaskPacket | None) -> dict[str, Any]:
        task = _mapping(packet["task"], "task")
        budget = _mapping(packet["budget"], "budget")
        scope_budget = _mapping(parent["budget"], "parent budget") if parent is not None else budget
        # The reservation consumes the child budget while the immutable limit is
        # the exact parent budget (or the root budget for a root task).
        consume = {
            "token_units": budget["token_limit"],
            "wall_seconds": budget["wall_seconds"],
            "cost_cents": budget["cost_limit_cents"],
        }
        limits = {
            "token_limit": scope_budget["token_limit"],
            "wall_limit_seconds": scope_budget["wall_seconds"],
            "concurrency_limit": scope_budget["concurrency_limit"],
            "cost_limit_cents": scope_budget["cost_limit_cents"],
            "remaining_tokens": scope_budget["remaining_tokens"],
            "remaining_wall_seconds": scope_budget["remaining_wall_seconds"],
            "remaining_cost_cents": scope_budget["remaining_cost_cents"],
        }
        if any(type(item) is not int or item < 0 for item in (*consume.values(), *limits.values())):
            raise OrchestrationError("BUDGET_INVALID", "packet budget reservation contains invalid limits")
        if limits["concurrency_limit"] < 1:
            raise OrchestrationError("BUDGET_INVALID", "packet budget concurrency limit is invalid")
        if (consume["token_units"] > budget["remaining_tokens"]
                or consume["wall_seconds"] > budget["remaining_wall_seconds"]
                or consume["cost_cents"] > budget["remaining_cost_cents"]):
            raise OrchestrationError("BUDGET_EXHAUSTED", "requested child reservation exceeds remaining budget")
        budget_projection = {
            "scope_id": scope_budget["id"], "scope_task_id": scope_budget["task_id"],
            "scope_task_digest": scope_budget["task_digest"], "budget_digest": scope_budget["budget_digest"],
            **limits, **consume,
        }
        budget_projection["reservation_digest"] = _value_digest(budget_projection)
        authority = {
            "mvp_assignment_digest": _mapping(packet["assignment"], "assignment")["assignment_digest"],
            "packet_digest": packet.packet_digest, "task_id": task["id"],
            "task_digest": task["task_digest"], "source_repository": task["source_repository"],
            "source_branch": task["source_branch"], "source_sha": task["source_sha"],
            "capabilities_digest": _value_digest(list(req.capabilities)),
            "allowed_paths_digest": _value_digest(list(task["allowed_paths"])),
            "gate_digest": task["gate_digest"], "role": req.role,
        }
        authority["authority_digest"] = _value_digest(authority)
        return {"budget": budget_projection, "authority": authority}

    @staticmethod
    def _cost_cents(requirements: PlacementRequirements) -> int:
        # Placement cost is a float in dollars; contract budgets are integer cents.
        return max(0, int(round(requirements.max_cost_usd * 100)))

    @_orchestration_boundary
    def _dispatch_impl(self, packet: kernel.TaskPacket, *, requirements: PlacementRequirements,
                 candidates: Sequence[PlacementCandidate | Mapping[str, Any]],
                 hosts: Mapping[str, HostRegistration | Mapping[str, Any]],
                 heartbeats: Mapping[str, HostHeartbeat | Mapping[str, Any]],
                 pools: Mapping[str, PoolStatus | Mapping[str, Any]],
                 lease_id: str, attempt_id: str, remote_session_id: str,
                 now: str, expires_at: str, parent: kernel.TaskPacket | None = None,
                 expected_lineage: Sequence[Any] | None = None,
                 verifier: bool = False,
                 _authority_validator: Any | None = None,
                 _pause_checker: Any | None = None,
                 _cost_cents: Any | None = None,
                 _reservation_builder: Any | None = None) -> DispatchRecord:
        if _pause_checker is None:
            self._check_pause()
        else:
            _pause_checker(self)
        if _authority_validator is None:
            anchor = self.validate_authority(packet, parent=parent, expected_lineage=expected_lineage)
        else:
            anchor = _authority_validator(self, packet, parent=parent, expected_lineage=expected_lineage)
        task = _mapping(packet["task"], "task"); budget = _mapping(packet["budget"], "budget")
        assignment = _mapping(packet["assignment"], "assignment")
        try:
            req = requirements if isinstance(requirements, PlacementRequirements) else PlacementRequirements.from_dict(requirements)
        except Exception as exc:
            raise OrchestrationError("INVALID_INPUT", "placement requirements are malformed") from exc
        if (req.task_id != task["id"] or req.project_id != task["project_id"] or req.source_sha != task["source_sha"]
                or req.source_repository != task["source_repository"] or req.source_branch != task["source_branch"]
                or tuple(req.allowed_paths) != tuple(task["allowed_paths"])
                or tuple(req.capabilities) != tuple(task["requested_capabilities"])
                or req.gate_digest != task["gate_digest"]):
            raise OrchestrationError("REQUIREMENTS_MISMATCH", "placement requirements are not task-bound")
        if req.role != ("verifier" if verifier else req.role):
            raise OrchestrationError("ROLE_MISMATCH", "verifier dispatch must use verifier role")
        budget_id = budget["id"]
        cost = self._cost_cents(req) if _cost_cents is None else _cost_cents(req)
        remaining = int(budget.get("remaining_cost_cents", 0))
        if cost > remaining:
            raise OrchestrationError("BUDGET_EXHAUSTED", "sibling aggregate budget is exhausted")
        if req.role == "verifier" and not verifier:
            raise OrchestrationError("ROLE_MISMATCH", "verifier requirements require verifier dispatch")
        if verifier and req.role != "verifier":
            raise OrchestrationError("ROLE_MISMATCH", "verifier dispatch must use verifier requirements")
        try:
            reservation = (self._mvp_reservation(packet, req, parent)
                           if _reservation_builder is None
                           else _reservation_builder(packet, req, parent))
        except OrchestrationError:
            raise
        except (KeyError, TypeError, ValueError) as exc:
            raise OrchestrationError("BUDGET_INVALID", "packet budget reservation is malformed") from exc
        # Keep the legacy projection for journal compatibility; the fabric now
        # receives and validates the exact immutable packet as its authority.
        req = replace(req, mvp_authority=reservation["authority"])
        if _pause_checker is None:
            self._check_pause()
        else:
            _pause_checker(self)
        try:
            fabric_assignment, trace = self.fabric.admit_placement(
                req, candidates, hosts, heartbeats, pools, lease_id=lease_id,
                attempt_id=attempt_id, remote_session_id=remote_session_id, now=now,
                expires_at=expires_at, paused=False, pause_guard=self.pause_guard,
                mvp_reservation=reservation, mvp_packet=packet, mvp_parent=parent,
                mvp_lineage=expected_lineage)
        except Exception as exc:
            if isinstance(exc, OrchestrationError):
                raise
            raise OrchestrationError(getattr(exc, "code", "PLACEMENT_REJECTED"), str(exc)) from exc
        if _pause_checker is None:
            self._check_pause()
        else:
            _pause_checker(self)
        if fabric_assignment is None:
            raise OrchestrationError("NO_ELIGIBLE_PLACEMENT", "no eligible capacity candidate")
        if (fabric_assignment.task_id != task["id"] or fabric_assignment.project_id != task["project_id"]
                or fabric_assignment.source_sha != task["source_sha"]
                or fabric_assignment.source_repository != task["source_repository"]
                or fabric_assignment.source_branch != task["source_branch"]
                or tuple(fabric_assignment.allowed_paths) != tuple(task["allowed_paths"])
                or fabric_assignment.gate_digest != task["gate_digest"]
                or fabric_assignment.role != req.role):
            raise OrchestrationError("ASSIGNMENT_BINDING_MISMATCH", "fabric assignment is not packet-bound")
        self._event("placed")
        self._event("lease-created")
        role = "verifier" if verifier else task.get("role", req.role)
        record = DispatchRecord(anchor.task_id, anchor.task_digest, anchor.packet_digest, anchor.depth,
                                role, assignment["assignment_digest"], fabric_assignment.assignment_digest,
                                lease_id, attempt_id, fabric_assignment.candidate_id or "candidate-unknown",
                                fabric_assignment.engine, fabric_assignment.model, tuple(self.events[-8:]),
                                task["source_repository"], task["source_branch"], task["source_sha"],
                                task["gate_digest"], _value_digest(list(task["allowed_paths"])),
                                _value_digest(list(task["requested_capabilities"])), "")
        object.__setattr__(record, "record_digest", _record_digest(record.to_dict()))
        return record

    @_orchestration_boundary
    def reconcile_restart(self, *, now: str) -> tuple[dict[str, Any], ...]:
        self._check_pause()
        self._event("restart-reconcile")
        return self.fabric.reconcile_restart(now=now)

    @_orchestration_boundary
    def _verify_impl(self, packet: kernel.TaskPacket, *, verifier_packet: kernel.TaskPacket,
               receipt: VerificationReceipt | Mapping[str, Any],
               candidate_id: str | None = None, result_commit: str | None = None,
               diff_digest: str | None = None, scope_digest: str | None = None,
               gate_digest: str | None = None,
               target_parent: kernel.TaskPacket | None = None,
               target_lineage: Sequence[Any] | None = None,
               verifier_parent: kernel.TaskPacket | None = None,
               verifier_lineage: Sequence[Any] | None = None,
               _authority_validator: Any | None = None,
               _pause_checker: Any | None = None) -> VerificationRecord:
        if _pause_checker is None:
            self._check_pause()
        else:
            _pause_checker(self)
        if _authority_validator is None:
            target = self.validate_authority(packet, parent=target_parent, expected_lineage=target_lineage)
            verifier = self.validate_authority(verifier_packet, parent=verifier_parent,
                                               expected_lineage=verifier_lineage)
        else:
            target = _authority_validator(self, packet, parent=target_parent, expected_lineage=target_lineage)
            verifier = _authority_validator(self, verifier_packet, parent=verifier_parent,
                                            expected_lineage=verifier_lineage)
        if target.task_id == verifier.task_id or target.task_digest == verifier.task_digest:
            raise OrchestrationError("SELF_VERIFICATION", "verifier must be a distinct task and authority")
        if self.receipt_store is None:
            raise OrchestrationError("VERIFIER_AUTH_REQUIRED", "controller receipt store is required")
        try:
            checked = receipt if isinstance(receipt, VerificationReceipt) else VerificationReceipt.from_dict(receipt)
            self.receipt_store.require(checked)
        except Exception as exc:
            raise OrchestrationError("VERIFIER_REJECTED", str(exc)) from exc
        target_mvp = _mapping(packet["assignment"], "assignment")["assignment_digest"]
        target_lease = self.fabric.lease_for_mvp_assignment(target_mvp, role="implementer")
        if target_lease is None:
            raise OrchestrationError("TARGET_DISPATCH_REQUIRED", "target packet has no durable implementer dispatch")
        target_result = _require_succeeded_result(self.fabric, target_lease, "target")
        target_fabric_digest = target_lease["assignment_digest"]
        if checked.assignment_digest != target_fabric_digest:
            raise OrchestrationError("VERIFICATION_BINDING_MISMATCH", "receipt is not bound to target fabric assignment")
        verifier_mvp = _mapping(verifier_packet["assignment"], "verifier assignment")["assignment_digest"]
        verifier_lease = self.fabric.lease_for_mvp_assignment(verifier_mvp, role="verifier")
        if verifier_lease is None:
            raise OrchestrationError("VERIFIER_DISPATCH_REQUIRED", "verifier packet has no durable verifier dispatch")
        verifier_result = _require_succeeded_result(self.fabric, verifier_lease, "verifier")
        verifier_authority = verifier_lease["reservation"]["authority"]
        if verifier_authority["task_id"] != verifier.task_id or verifier_authority["packet_digest"] != verifier.packet_digest:
            raise OrchestrationError("VERIFIER_BINDING_MISMATCH", "verifier dispatch is not bound to verifier packet")
        if target_result["assignment_digest"] != target_fabric_digest or verifier_result["assignment_digest"] != verifier_lease["assignment_digest"]:
            raise OrchestrationError("RESULT_BINDING_MISMATCH", "durable result assignment binding changed")
        values = {
            "candidate_id": checked.candidate_id if candidate_id is None else candidate_id,
            "result_commit": checked.result_commit if result_commit is None else result_commit,
            "diff_digest": checked.diff_digest if diff_digest is None else diff_digest,
            "scope_digest": checked.scope_digest if scope_digest is None else scope_digest,
            "gate_digest": checked.gate_digest if gate_digest is None else gate_digest,
        }
        for key, value in values.items():
            if value != getattr(checked, key):
                raise OrchestrationError("VERIFICATION_BINDING_MISMATCH", f"{key} differs from authenticated receipt")
        target_task = _mapping(packet["task"], "task")
        if checked.source_sha != target_task["source_sha"]:
            raise OrchestrationError("SOURCE_MISMATCH", "receipt source differs from target packet")
        self._event("verified")
        record = VerificationRecord(target.task_id, target.task_digest, target.packet_digest,
                                    verifier.task_id, verifier.task_digest, checked.receipt_digest,
                                    "pass", ("verified",), target_fabric_digest,
                                    target_lease["lease_id"], target_lease["attempt_id"],
                                    checked.candidate_id, checked.result_commit, checked.source_sha,
                                    checked.diff_digest, checked.scope_digest, checked.gate_digest,
                                    verifier_lease["assignment_digest"], verifier_lease["lease_id"],
                                    verifier_lease["attempt_id"], target_mvp, verifier_mvp,
                                    target_lease["reservation"]["authority"]["source_repository"],
                                    target_lease["reservation"]["authority"]["source_branch"],
                                    target_lease["reservation"]["authority"]["allowed_paths_digest"],
                                    target_lease["reservation"]["authority"]["capabilities_digest"], "")
        raw = record.to_dict()
        object.__setattr__(record, "record_digest", _record_digest(raw))
        return record

    @_orchestration_boundary
    def _review_intent_body(self, record: VerificationRecord, *, candidate_id: str,
                      project_id: str, source_sha: str, result_commit: str,
                      assignment: FabricAssignment | Mapping[str, Any],
                      diff_digest: str, scope_digest: str, gate_digest: str,
                      result_ref: str, classification: str = "current-compatible",
                      target_packet: kernel.TaskPacket | None = None,
                      verifier_packet: kernel.TaskPacket | None = None,
                      target_parent: kernel.TaskPacket | None = None,
                      target_lineage: Sequence[Any] | None = None,
                      verifier_parent: kernel.TaskPacket | None = None,
                      verifier_lineage: Sequence[Any] | None = None,
                      _authority_validator: Any | None = None,
                      _pause_checker: Any | None = None) -> tuple[FabricAssignment, VerificationReceipt, dict[str, Any]]:
        """Admit a review candidate only after a registered passing receipt."""
        if _pause_checker is None:
            self._check_pause()
        else:
            _pause_checker(self)
        if self.integration is None or self.receipt_store is None:
            raise OrchestrationError("REVIEW_NOT_READY", "review intent requires passing independent verification")
        if target_packet is None or verifier_packet is None:
            raise OrchestrationError("REVIEW_REJECTED", "review admission requires exact target and verifier packets")
        if _authority_validator is None:
            target = self.validate_authority(target_packet, parent=target_parent, expected_lineage=target_lineage)
            verifier = self.validate_authority(verifier_packet, parent=verifier_parent,
                                                expected_lineage=verifier_lineage)
        else:
            target = _authority_validator(self, target_packet, parent=target_parent, expected_lineage=target_lineage)
            verifier = _authority_validator(self, verifier_packet, parent=verifier_parent,
                                            expected_lineage=verifier_lineage)
        target_task = _mapping(target_packet["task"], "target task")
        if (target.task_id != record.task_id or target.task_digest != record.task_digest
                or target.packet_digest != record.packet_digest
                or verifier.task_id != record.verifier_task_id
                or verifier.task_digest != record.verifier_task_digest
                or record.events != ("verified",)
                or _mapping(target_packet["assignment"], "target assignment")["assignment_digest"] != record.target_mvp_assignment_digest
                or _mapping(verifier_packet["assignment"], "verifier assignment")["assignment_digest"] != record.verifier_mvp_assignment_digest
                or target_task["source_sha"] != record.source_sha
                or target_task["source_repository"] != record.target_source_repository
                or target_task["source_branch"] != record.target_source_branch
                or target_task["gate_digest"] != record.gate_digest
                or _value_digest(list(target_task["allowed_paths"])) != record.target_allowed_paths_digest
                or _value_digest(list(target_task["requested_capabilities"])) != record.target_capabilities_digest):
            raise OrchestrationError("REVIEW_REJECTED", "verification record is not rederived from the exact packets")
        receipt = self.receipt_store.require_digest(record.receipt_digest)
        try:
            assignment_obj = assignment if isinstance(assignment, FabricAssignment) else FabricAssignment.from_dict(assignment)
            if assignment_obj.assignment_digest != record.target_fabric_assignment_digest:
                raise OrchestrationError("REVIEW_REJECTED", "review assignment differs from authenticated target")
            if source_sha != record.source_sha or gate_digest != record.gate_digest:
                raise OrchestrationError("REVIEW_REJECTED", "review source or gate differs from authenticated target")
            if candidate_id != record.candidate_id or result_commit != record.result_commit:
                raise OrchestrationError("REVIEW_REJECTED", "review candidate or result differs from authenticated receipt")
            if diff_digest != record.diff_digest or scope_digest != record.scope_digest:
                raise OrchestrationError("REVIEW_REJECTED", "review evidence differs from authenticated receipt")
            target_lease = self.fabric.lease_for_assignment(record.target_fabric_assignment_digest)
            if target_lease is None or target_lease["lease_id"] != record.target_lease_id or target_lease["attempt_id"] != record.target_attempt_id:
                raise OrchestrationError("REVIEW_REJECTED", "target durable dispatch no longer matches verification record")
            _require_succeeded_result(self.fabric, target_lease, "target")
            target_auth = target_lease["reservation"].get("authority", {})
            if (target_auth.get("packet_digest") != record.packet_digest or target_auth.get("task_id") != record.task_id
                    or target_auth.get("task_digest") != record.task_digest
                    or target_auth.get("mvp_assignment_digest") != record.target_mvp_assignment_digest
                    or target_auth.get("source_repository") != record.target_source_repository
                    or target_auth.get("source_branch") != record.target_source_branch
                    or target_auth.get("allowed_paths_digest") != record.target_allowed_paths_digest
                    or target_auth.get("capabilities_digest") != record.target_capabilities_digest
                    or target_auth.get("source_sha") != record.source_sha
                    or target_auth.get("gate_digest") != record.gate_digest):
                raise OrchestrationError("REVIEW_REJECTED", "target packet authority does not match durable dispatch")
            verifier_lease = self.fabric.lease_for_assignment(record.verifier_fabric_assignment_digest)
            if verifier_lease is None or verifier_lease["lease_id"] != record.verifier_lease_id or verifier_lease["attempt_id"] != record.verifier_attempt_id:
                raise OrchestrationError("REVIEW_REJECTED", "verifier durable dispatch no longer matches record")
            _require_succeeded_result(self.fabric, verifier_lease, "verifier")
            if verifier_lease["reservation"].get("role") != "verifier":
                raise OrchestrationError("REVIEW_REJECTED", "verifier dispatch role is not authenticated")
            verifier_auth = verifier_lease["reservation"].get("authority", {})
            if (verifier_auth.get("task_id") != record.verifier_task_id
                    or verifier_auth.get("task_digest") != record.verifier_task_digest
                    or verifier_auth.get("packet_digest") != verifier.packet_digest
                    or verifier_auth.get("mvp_assignment_digest") != record.verifier_mvp_assignment_digest):
                raise OrchestrationError("REVIEW_REJECTED", "verifier packet authority does not match durable dispatch")
            if (receipt.candidate_id != record.candidate_id or receipt.result_commit != record.result_commit
                    or receipt.source_sha != record.source_sha or receipt.diff_digest != record.diff_digest
                    or receipt.scope_digest != record.scope_digest or receipt.gate_digest != record.gate_digest):
                raise OrchestrationError("REVIEW_REJECTED", "verification record receipt bindings changed")
            verify_candidate_result(assignment=assignment, receipt=receipt, candidate_id=candidate_id,
                                    result_commit=result_commit, diff_digest=diff_digest,
                                    scope_digest=scope_digest, gate_digest=gate_digest,
                                    result_ref=result_ref, receipt_store=self.receipt_store)
            assignment_obj = assignment if isinstance(assignment, FabricAssignment) else FabricAssignment.from_dict(assignment)
            review_args = {"candidate_id": candidate_id, "project_id": project_id,
                           "source_sha": source_sha, "result_commit": result_commit,
                           "result_ref": result_ref, "classification": classification}
            return assignment_obj, receipt, review_args
        except Exception as exc:
            raise OrchestrationError("REVIEW_REJECTED", str(exc)) from exc


def _install_public_operations() -> None:
    """Install immutable class-level public operation descriptors.

    The public methods must not follow mutable instance attributes such as
    ``_dispatch_impl``.  These descriptors close over the exact unbound bodies
    and over a weak per-instance issuance state, while the review descriptor
    separately closes over the exact record checker and integration admission
    callable.  A descriptor is used (rather than assigning bound closures in
    ``__init__``) so ``hasattr`` and normal subclass/super lookup retain the
    ordinary class API.
    """
    states: weakref.WeakKeyDictionary[Any, tuple[Any, Any]] = weakref.WeakKeyDictionary()
    canonical_json = contracts.canonical_json

    # Give module-level security helpers a private globals dictionary.  This is
    # the orchestration analogue of the kernel's trusted callable graph: changing
    # a reachable helper name after installation cannot alter record admission.
    module_globals = globals()
    trusted_globals = dict(module_globals)
    trusted_helpers: dict[str, FunctionType] = {}
    for name, value in module_globals.items():
        if isinstance(value, FunctionType) and value.__globals__ is module_globals:
            clone = FunctionType(value.__code__, trusted_globals, value.__name__,
                                 value.__defaults__, value.__closure__)
            clone.__kwdefaults__ = (dict(value.__kwdefaults__)
                                    if value.__kwdefaults__ is not None else None)
            trusted_helpers[name] = clone
    trusted_globals.update(trusted_helpers)

    def trusted_method(method: Any) -> Any:
        """Clone a boundary-wrapped method while retaining its exact body."""
        raw = method
        if method.__closure__:
            for cell in method.__closure__:
                value = cell.cell_contents
                if isinstance(value, FunctionType):
                    raw = value
                    break
        clone = FunctionType(raw.__code__, trusted_globals, raw.__name__,
                             raw.__defaults__, raw.__closure__)
        clone.__kwdefaults__ = (dict(raw.__kwdefaults__)
                                if raw.__kwdefaults__ is not None else None)
        return trusted_helpers["_orchestration_boundary"](clone)

    def trusted_plain(function: Any) -> Any:
        """Clone an undecorated class helper into the trusted globals."""
        clone = FunctionType(function.__code__, trusted_globals, function.__name__,
                             function.__defaults__, function.__closure__)
        clone.__kwdefaults__ = (dict(function.__kwdefaults__)
                                if function.__kwdefaults__ is not None else None)
        return clone

    checked_record = trusted_helpers["_checked_record"]
    # Capture the kernel authority graph once.  If the module was poisoned
    # before this consumer imported, retain a typed fail-closed seam instead of
    # trusting any public replacement.
    kernel_binding = _capture_kernel_graph()
    kernel_ready = kernel_binding is not None
    if kernel_binding is None:
        packet_type = type(None)
        packet_validator = None
        kernel_error = ValueError
    else:
        packet_type, packet_validator, kernel_error = kernel_binding
    dispatch_impl = trusted_method(MVPOrchestrator._dispatch_impl)
    verify_impl = trusted_method(MVPOrchestrator._verify_impl)
    review_body = trusted_method(MVPOrchestrator._review_intent_body)
    authority_body = trusted_method(MVPOrchestrator.validate_authority)

    def authority_public_raw(instance: MVPOrchestrator, packet: Any, *,
                             parent: Any = None,
                             expected_lineage: Sequence[Any] | None = None) -> AuthorityAnchor:
        if not kernel_ready:
            raise OrchestrationError("KERNEL_UNTRUSTED", "kernel authority graph failed import attestation")
        return authority_body(instance, packet, parent=parent,
                              expected_lineage=expected_lineage,
                              _packet_type=packet_type,
                              _packet_validator=packet_validator,
                              _kernel_error=kernel_error)

    authority_public = trusted_helpers["_orchestration_boundary"](authority_public_raw)
    authority_public.__name__ = "validate_authority"
    authority_public.__doc__ = "Validate packet authority against the installed kernel boundary."
    # Direct ``o.validate_authority(...)`` calls must use the same immutable
    # authority bridge as dispatch/verify, not the legacy dynamic method body.
    MVPOrchestrator.validate_authority = authority_public
    authority_validator = authority_public
    check_pause = trusted_method(MVPOrchestrator._check_pause)
    event = trusted_method(MVPOrchestrator._event)
    cost_cents = trusted_plain(MVPOrchestrator._cost_cents)
    reservation_builder = trusted_plain(MVPOrchestrator._mvp_reservation)
    integration_admit = IntegrationCoordinator.admit

    def state_for(instance: MVPOrchestrator) -> tuple[Any, Any]:
        state = states.get(instance)
        if state is not None:
            return state
        issued: dict[int, tuple[weakref.ReferenceType[Any], bytes]] = {}

        def snapshot(record: Any) -> bytes:
            if isinstance(record, DispatchRecord):
                value = DispatchRecord.to_dict(record)
            elif isinstance(record, VerificationRecord):
                value = VerificationRecord.to_dict(record)
            else:
                raise OrchestrationError("REVIEW_NOT_READY", "record type is not authenticated")
            return canonical_json(value)

        def issue(record: Any) -> Any:
            identity = id(record)
            frozen = snapshot(record)

            def released(reference: weakref.ReferenceType[Any]) -> None:
                entry = issued.get(identity)
                if entry is not None and entry[0] is reference:
                    issued.pop(identity, None)

            issued[identity] = (weakref.ref(record, released), frozen)
            return record

        def require_record(record: Any, expected_type: type) -> Any:
            if not isinstance(record, expected_type):
                raise OrchestrationError("REVIEW_NOT_READY", "record type is not authenticated")
            entry = issued.get(id(record))
            if entry is None or entry[0]() is not record:
                raise OrchestrationError("REVIEW_NOT_READY", "record was not issued by the orchestrator")
            try:
                current = snapshot(record)
            except Exception as exc:
                raise OrchestrationError("RECORD_UNAUTHENTICATED", "issued record was mutated") from exc
            if current != entry[1]:
                raise OrchestrationError("RECORD_UNAUTHENTICATED", "issued record was mutated")
            return record

        state = (issue, require_record)
        states[instance] = state
        return state

    owner_type = MVPOrchestrator

    def descriptor(kind: str, implementation: Any) -> Any:
        """Create a data descriptor whose implementation is closure-bound."""
        def get(_descriptor_self: Any, instance: MVPOrchestrator | None,
                owner: type | None = None) -> Any:
            if instance is None:
                return descriptor_object
            issue, require_record = state_for(instance)
            def validated_kwargs(args: tuple[Any, ...], kwargs: Mapping[str, Any]) -> dict[str, Any]:
                call_kwargs = dict(kwargs)
                packet = args[0] if args else call_kwargs.get("packet")
                parent = call_kwargs.get("parent")
                lineage = call_kwargs.get("expected_lineage")
                if kind == "verify":
                    authority_validator(instance, packet, parent=call_kwargs.get("target_parent"),
                                        expected_lineage=call_kwargs.get("target_lineage"))
                    verifier_packet = call_kwargs.get("verifier_packet")
                    authority_validator(instance, verifier_packet,
                                        parent=call_kwargs.get("verifier_parent"),
                                        expected_lineage=call_kwargs.get("verifier_lineage"))
                elif kind == "review_intent":
                    target_packet = call_kwargs.get("target_packet")
                    verifier_packet = call_kwargs.get("verifier_packet")
                    authority_validator(instance, target_packet,
                                        parent=call_kwargs.get("target_parent"),
                                        expected_lineage=call_kwargs.get("target_lineage"))
                    authority_validator(instance, verifier_packet,
                                        parent=call_kwargs.get("verifier_parent"),
                                        expected_lineage=call_kwargs.get("verifier_lineage"))
                else:
                    authority_validator(instance, packet, parent=parent, expected_lineage=lineage)
                call_kwargs["_authority_validator"] = authority_validator
                call_kwargs["_pause_checker"] = check_pause
                if kind == "dispatch":
                    call_kwargs["_cost_cents"] = cost_cents
                    call_kwargs["_reservation_builder"] = reservation_builder
                return call_kwargs
            if kind == "dispatch":
                def public(*args: Any, **kwargs: Any) -> DispatchRecord:
                    return issue(implementation(instance, *args,
                                                **validated_kwargs(args, kwargs)))
            elif kind == "verify":
                def public(*args: Any, **kwargs: Any) -> VerificationRecord:
                    return issue(implementation(instance, *args,
                                                **validated_kwargs(args, kwargs)))
            else:
                def public(*args: Any, **kwargs: Any) -> str:
                    try:
                        record = args[0] if args else kwargs.get("record")
                        checked_record(record, require_record)
                        call_kwargs = validated_kwargs(args, kwargs)
                        assignment_obj, receipt, review_args = implementation(instance, *args, **call_kwargs)
                        check_pause(instance)
                        integration = instance.integration
                        if integration is None:
                            raise OrchestrationError("REVIEW_NOT_READY", "review integration is not configured")
                        outcome = integration_admit(
                            integration, **review_args, assignment=assignment_obj,
                            verification_receipt=receipt)
                        event(instance, "review-intent-emitted")
                        return outcome
                    except OrchestrationError:
                        raise
                    except Exception as exc:
                        raise OrchestrationError("REVIEW_REJECTED", str(exc)) from exc
            public.__name__ = kind
            public.__doc__ = f"Authenticated {kind} operation."
            return public

        def set_value(_descriptor_self: Any, instance: MVPOrchestrator, value: Any) -> None:
            raise AttributeError(f"{kind} is a class-level authenticated operation")

        def call(_descriptor_self: Any, *args: Any, **kwargs: Any) -> Any:
            """Support Python's normal unbound class-method call shape."""
            if not args or not isinstance(args[0], owner_type):
                raise TypeError(f"{kind}() missing a valid MVPOrchestrator instance")
            instance = args[0]
            bound = get(_descriptor_self, instance, type(instance))
            return bound(*args[1:], **kwargs)

        class OperationDescriptor:
            __slots__ = ()

        descriptor_object = OperationDescriptor()
        OperationDescriptor.__get__ = staticmethod(get)
        OperationDescriptor.__set__ = staticmethod(set_value)
        OperationDescriptor.__call__ = call
        return descriptor_object

    # Keep the helper reachable for compatibility, but it is deliberately the
    # non-actuating body only.  Integration admission exists only in review_intent.
    MVPOrchestrator._review_intent_impl = review_body
    MVPOrchestrator.dispatch = descriptor("dispatch", dispatch_impl)
    MVPOrchestrator.verify = descriptor("verify", verify_impl)
    MVPOrchestrator.review_intent = descriptor("review_intent", review_body)


_install_public_operations()
del _install_public_operations

Orchestrator = MVPOrchestrator

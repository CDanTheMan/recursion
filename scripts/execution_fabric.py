#!/usr/bin/env python3
"""Provider-neutral placement primitives for the Recursion v2 execution fabric.

This module is deliberately an inert library.  It has no network, process, git, credential,
PAUSE, or service integration.  Callers provide immutable registry snapshots and receive
deterministic placement decisions.  Durable state is an append-only local journal so a controller
restart can replay leases and attempts without relaunching remote work.

The wire records are schema-versioned and strict: unknown keys, missing required keys, malformed
identities, and secret-looking values fail closed.  The module is suitable for hermetic tests and
for a later adapter which explicitly opts into the control-plane seams.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = 1
FABRIC_SCHEMA = "recursion-execution-fabric-v1"
ZERO_DIGEST = "0" * 64

_ID = re.compile(r"[a-z][a-z0-9-]{1,63}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_ISO = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\Z")
_COMMIT = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
_SECRET_KEY = re.compile(r"(?:secret|token|password|private|credential|api[_-]?key)", re.I)


class FabricError(ValueError):
    """Base class for fail-closed fabric errors."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class SchemaError(FabricError):
    pass


class AdmissionError(FabricError):
    pass


class ReconciliationError(FabricError):
    pass


def _check_keys(value: Mapping[str, Any], required: set[str], optional: set[str], kind: str) -> None:
    if not isinstance(value, Mapping):
        raise SchemaError("INVALID_RECORD", f"{kind} must be an object")
    keys = set(value)
    missing = sorted(required - keys)
    unknown = sorted(keys - required - optional)
    if missing:
        raise SchemaError("MISSING_FIELD", f"{kind} missing fields: {', '.join(missing)}")
    if unknown:
        raise SchemaError("UNKNOWN_FIELD", f"{kind} has unknown fields: {', '.join(unknown)}")


def _string(value: Any, field: str, *, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise SchemaError("INVALID_FIELD", f"{field} must be a non-empty string")
    if pattern is not None and not pattern.fullmatch(value):
        raise SchemaError("INVALID_FIELD", f"{field} has an invalid value")
    return value


def _id(value: Any, field: str) -> str:
    return _string(value, field, pattern=_ID)


def _digest(value: Any, field: str) -> str:
    return _string(value, field, pattern=_SHA256)


def _commit(value: Any, field: str) -> str:
    """Validate a git object id (the normal 40-char form or a full SHA-256 id)."""
    return _string(value, field, pattern=_COMMIT)


def _timestamp(value: Any, field: str) -> str:
    return _string(value, field, pattern=_ISO)


def _string_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise SchemaError("INVALID_FIELD", f"{field} must be a list of strings")
    result = tuple(sorted(set(value)))
    if len(result) != len(value):
        raise SchemaError("INVALID_FIELD", f"{field} must not contain duplicates")
    return result


def _nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SchemaError("INVALID_FIELD", f"{field} must be a non-negative integer")
    return value


def _nonnegative_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise SchemaError("INVALID_FIELD", f"{field} must be a non-negative number")
    return float(value)


def _canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest_record(value: Mapping[str, Any]) -> str:
    """Return the stable SHA-256 identity of a schema record, excluding its digest field."""
    body = {key: item for key, item in value.items() if key not in {"digest", "assignment_digest"}}
    return hashlib.sha256(_canonical(body)).hexdigest()


@dataclass(frozen=True)
class HostRegistration:
    host_id: str
    capabilities: tuple[str, ...]
    operating_system: str
    architectures: tuple[str, ...]
    sandbox_profiles: tuple[str, ...]
    network_profiles: tuple[str, ...]
    trust_class: str
    max_concurrency: int
    workload_concurrency: Mapping[str, int]
    registration_digest: str
    registered_at: str

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "HostRegistration":
        required = {"schema_version", "kind", "host_id", "capabilities", "operating_system",
                    "architectures", "sandbox_profiles", "network_profiles", "trust_class",
                    "max_concurrency", "workload_concurrency", "registration_digest", "registered_at"}
        _check_keys(raw, required, set(), "host_registration")
        if raw["schema_version"] != SCHEMA_VERSION or raw["kind"] != "host_registration":
            raise SchemaError("SCHEMA_VERSION", "unsupported host registration schema")
        host_id = _id(raw["host_id"], "host_id")
        caps = _string_list(raw["capabilities"], "capabilities")
        os_name = _string(raw["operating_system"], "operating_system")
        architectures = _string_list(raw["architectures"], "architectures")
        sandbox = _string_list(raw["sandbox_profiles"], "sandbox_profiles")
        network = _string_list(raw["network_profiles"], "network_profiles")
        trust = _string(raw["trust_class"], "trust_class")
        max_concurrency = _nonnegative_int(raw["max_concurrency"], "max_concurrency")
        workloads = raw["workload_concurrency"]
        if not isinstance(workloads, Mapping):
            raise SchemaError("INVALID_FIELD", "workload_concurrency must be an object")
        normalized: dict[str, int] = {}
        for key, count in sorted(workloads.items()):
            normalized[_string(key, "workload_concurrency key")] = _nonnegative_int(count, f"workload_concurrency.{key}")
        return cls(host_id, caps, os_name, architectures, sandbox, network, trust, max_concurrency,
                   normalized, _digest(raw["registration_digest"], "registration_digest"),
                   _timestamp(raw["registered_at"], "registered_at"))

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "host_registration", "host_id": self.host_id,
                "capabilities": list(self.capabilities), "operating_system": self.operating_system,
                "architectures": list(self.architectures), "sandbox_profiles": list(self.sandbox_profiles),
                "network_profiles": list(self.network_profiles), "trust_class": self.trust_class,
                "max_concurrency": self.max_concurrency, "workload_concurrency": dict(self.workload_concurrency),
                "registration_digest": self.registration_digest, "registered_at": self.registered_at}

    @classmethod
    def build(cls, *, host_id: str, capabilities: Iterable[str], operating_system: str,
              architectures: Iterable[str], sandbox_profiles: Iterable[str],
              network_profiles: Iterable[str], trust_class: str, max_concurrency: int,
              workload_concurrency: Mapping[str, int], registered_at: str) -> "HostRegistration":
        body = {"schema_version": SCHEMA_VERSION, "kind": "host_registration", "host_id": host_id,
                "capabilities": sorted(set(capabilities)), "operating_system": operating_system,
                "architectures": sorted(set(architectures)), "sandbox_profiles": sorted(set(sandbox_profiles)),
                "network_profiles": sorted(set(network_profiles)), "trust_class": trust_class,
                "max_concurrency": max_concurrency, "workload_concurrency": dict(sorted(workload_concurrency.items())),
                "registered_at": registered_at}
        body["registration_digest"] = digest_record(body)
        return cls.from_dict(body)


@dataclass(frozen=True)
class HostHeartbeat:
    host_id: str
    registration_digest: str
    sequence: int
    observed_at: str
    lease_epoch: int

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "HostHeartbeat":
        required = {"schema_version", "kind", "host_id", "registration_digest", "sequence", "observed_at", "lease_epoch"}
        _check_keys(raw, required, set(), "host_heartbeat")
        if raw["schema_version"] != SCHEMA_VERSION or raw["kind"] != "host_heartbeat":
            raise SchemaError("SCHEMA_VERSION", "unsupported host heartbeat schema")
        return cls(_id(raw["host_id"], "host_id"), _digest(raw["registration_digest"], "registration_digest"),
                   _nonnegative_int(raw["sequence"], "sequence"), _timestamp(raw["observed_at"], "observed_at"),
                   _nonnegative_int(raw["lease_epoch"], "lease_epoch"))

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "host_heartbeat", "host_id": self.host_id,
                "registration_digest": self.registration_digest, "sequence": self.sequence,
                "observed_at": self.observed_at, "lease_epoch": self.lease_epoch}


@dataclass(frozen=True)
class PoolStatus:
    pool_id: str
    billing_basis: str
    allowed_roles: tuple[str, ...]
    allowed_projects: tuple[str, ...]
    allowed_models: tuple[str, ...]
    max_concurrency: int
    in_flight: int
    quota_remaining: int | None
    quota_period: str | None
    on_demand: bool
    cost_per_run: float

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "PoolStatus":
        required = {"schema_version", "kind", "pool_id", "billing_basis", "allowed_roles", "allowed_projects",
                    "allowed_models", "max_concurrency", "in_flight", "quota_remaining", "quota_period",
                    "on_demand", "cost_per_run"}
        _check_keys(raw, required, set(), "pool_status")
        if raw["schema_version"] != SCHEMA_VERSION or raw["kind"] != "pool_status":
            raise SchemaError("SCHEMA_VERSION", "unsupported pool status schema")
        quota = raw["quota_remaining"]
        if quota is not None:
            quota = _nonnegative_int(quota, "quota_remaining")
        period = raw["quota_period"]
        if period is not None:
            period = _string(period, "quota_period")
        if not isinstance(raw["on_demand"], bool):
            raise SchemaError("INVALID_FIELD", "on_demand must be boolean")
        return cls(_id(raw["pool_id"], "pool_id"), _string(raw["billing_basis"], "billing_basis"),
                   _string_list(raw["allowed_roles"], "allowed_roles"), _string_list(raw["allowed_projects"], "allowed_projects"),
                   _string_list(raw["allowed_models"], "allowed_models"), _nonnegative_int(raw["max_concurrency"], "max_concurrency"),
                   _nonnegative_int(raw["in_flight"], "in_flight"), quota, period, raw["on_demand"],
                   _nonnegative_number(raw["cost_per_run"], "cost_per_run"))


@dataclass(frozen=True)
class PlacementRequirements:
    task_id: str
    project_id: str
    role: str
    capabilities: tuple[str, ...]
    operating_system: str | None
    sandbox_profile: str | None
    network_profile: str | None
    billing_basis: tuple[str, ...]
    max_cost_usd: float
    model: str | None
    preferred_hosts: tuple[str, ...]
    preferred_pools: tuple[str, ...]
    source_sha: str

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "PlacementRequirements":
        required = {"schema_version", "kind", "task_id", "project_id", "role", "capabilities",
                    "operating_system", "sandbox_profile", "network_profile", "billing_basis", "max_cost_usd",
                    "model", "preferred_hosts", "preferred_pools", "source_sha"}
        _check_keys(raw, required, set(), "placement_requirements")
        if raw["schema_version"] != SCHEMA_VERSION or raw["kind"] != "placement_requirements":
            raise SchemaError("SCHEMA_VERSION", "unsupported placement requirements schema")
        optional_text = {key: (None if raw[key] is None else _string(raw[key], key))
                         for key in ("operating_system", "sandbox_profile", "network_profile", "model")}
        return cls(_id(raw["task_id"], "task_id"), _id(raw["project_id"], "project_id"),
                   _string(raw["role"], "role"), _string_list(raw["capabilities"], "capabilities"),
                   optional_text["operating_system"], optional_text["sandbox_profile"], optional_text["network_profile"],
                   _string_list(raw["billing_basis"], "billing_basis"), _nonnegative_number(raw["max_cost_usd"], "max_cost_usd"),
                   optional_text["model"], _string_list(raw["preferred_hosts"], "preferred_hosts"),
                   _string_list(raw["preferred_pools"], "preferred_pools"), _commit(raw["source_sha"], "source_sha"))


@dataclass(frozen=True)
class PlacementCandidate:
    candidate_id: str
    engine: str
    provider: str
    pool_id: str
    model: str
    host_id: str
    sandbox_profile: str
    network_profile: str
    capabilities: tuple[str, ...]
    operating_system: str
    billing_basis: str
    cost_per_run: float
    roles: tuple[str, ...]
    enabled: bool = True

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "PlacementCandidate":
        required = {"schema_version", "kind", "candidate_id", "engine", "provider", "pool_id", "model", "host_id",
                    "sandbox_profile", "network_profile", "capabilities", "operating_system", "billing_basis",
                    "cost_per_run", "roles", "enabled"}
        _check_keys(raw, required, set(), "placement_candidate")
        if raw["schema_version"] != SCHEMA_VERSION or raw["kind"] != "placement_candidate":
            raise SchemaError("SCHEMA_VERSION", "unsupported placement candidate schema")
        if not isinstance(raw["enabled"], bool):
            raise SchemaError("INVALID_FIELD", "enabled must be boolean")
        return cls(_id(raw["candidate_id"], "candidate_id"), _id(raw["engine"], "engine"), _id(raw["provider"], "provider"),
                   _id(raw["pool_id"], "pool_id"), _string(raw["model"], "model"), _id(raw["host_id"], "host_id"),
                   _string(raw["sandbox_profile"], "sandbox_profile"), _string(raw["network_profile"], "network_profile"),
                   _string_list(raw["capabilities"], "capabilities"), _string(raw["operating_system"], "operating_system"),
                   _string(raw["billing_basis"], "billing_basis"), _nonnegative_number(raw["cost_per_run"], "cost_per_run"),
                   _string_list(raw["roles"], "roles"), raw["enabled"])


@dataclass(frozen=True)
class Rejection:
    candidate_id: str
    code: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"schema_version": SCHEMA_VERSION, "kind": "placement_rejection", "candidate_id": self.candidate_id,
                "code": self.code, "reason": self.reason}


@dataclass(frozen=True)
class Assignment:
    task_id: str
    project_id: str
    source_sha: str
    engine: str
    provider: str
    capacity_pool: str
    model: str
    host: str
    sandbox_profile: str
    network_profile: str
    assignment_digest: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "assignment", "task_id": self.task_id,
                "project_id": self.project_id, "source_sha": self.source_sha, "engine": self.engine,
                "provider": self.provider, "capacity_pool": self.capacity_pool, "model": self.model,
                "host": self.host, "sandbox_profile": self.sandbox_profile, "network_profile": self.network_profile,
                "assignment_digest": self.assignment_digest, "created_at": self.created_at}

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "Assignment":
        required = {"schema_version", "kind", "task_id", "project_id", "source_sha", "engine", "provider",
                    "capacity_pool", "model", "host", "sandbox_profile", "network_profile", "assignment_digest", "created_at"}
        _check_keys(raw, required, set(), "assignment")
        if raw["schema_version"] != SCHEMA_VERSION or raw["kind"] != "assignment":
            raise SchemaError("SCHEMA_VERSION", "unsupported assignment schema")
        assignment = cls(_id(raw["task_id"], "task_id"), _id(raw["project_id"], "project_id"), _commit(raw["source_sha"], "source_sha"),
                         _id(raw["engine"], "engine"), _id(raw["provider"], "provider"), _id(raw["capacity_pool"], "capacity_pool"),
                         _string(raw["model"], "model"), _id(raw["host"], "host"), _string(raw["sandbox_profile"], "sandbox_profile"),
                         _string(raw["network_profile"], "network_profile"), _digest(raw["assignment_digest"], "assignment_digest"),
                         _timestamp(raw["created_at"], "created_at"))
        if assignment_digest(assignment) != assignment.assignment_digest:
            raise SchemaError("DIGEST_MISMATCH", "assignment digest does not match immutable fields")
        return assignment


def assignment_digest(assignment: Assignment) -> str:
    body = assignment.to_dict()
    body.pop("assignment_digest", None)
    return hashlib.sha256(_canonical(body)).hexdigest()


def _candidate_sort_key(candidate: PlacementCandidate, requirements: PlacementRequirements) -> tuple[Any, ...]:
    # Preferences are deterministic tie-breakers, never eligibility relaxations.
    return (0 if candidate.host_id in requirements.preferred_hosts else 1,
            0 if candidate.pool_id in requirements.preferred_pools else 1,
            candidate.cost_per_run, candidate.candidate_id)


def resolve_placement(requirements: PlacementRequirements | Mapping[str, Any],
                      candidates: Sequence[PlacementCandidate | Mapping[str, Any]],
                      hosts: Mapping[str, HostRegistration | Mapping[str, Any]],
                      heartbeats: Mapping[str, HostHeartbeat | Mapping[str, Any]],
                      pools: Mapping[str, PoolStatus | Mapping[str, Any]],
                      *, now_epoch: float | None = None, heartbeat_ttl_s: float = 120.0,
                      created_at: str | None = None,
                      reserved_host: Mapping[str, int] | None = None,
                      reserved_pool: Mapping[str, int] | None = None) -> tuple[Assignment | None, tuple[Rejection, ...]]:
    """Resolve one immutable assignment and a complete, deterministic rejection trace."""
    req = requirements if isinstance(requirements, PlacementRequirements) else PlacementRequirements.from_dict(requirements)
    parsed_candidates = [item if isinstance(item, PlacementCandidate) else PlacementCandidate.from_dict(item) for item in candidates]
    parsed_hosts = {key: item if isinstance(item, HostRegistration) else HostRegistration.from_dict(item) for key, item in hosts.items()}
    parsed_heartbeats = {key: item if isinstance(item, HostHeartbeat) else HostHeartbeat.from_dict(item) for key, item in heartbeats.items()}
    parsed_pools = {key: item if isinstance(item, PoolStatus) else PoolStatus.from_dict(item) for key, item in pools.items()}
    now = time.time() if now_epoch is None else now_epoch
    if created_at is None:
        created_at = _now_iso() if now_epoch is None else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_epoch))
    _timestamp(created_at, "created_at")
    host_used = reserved_host or {}
    pool_used = reserved_pool or {}
    trace: list[Rejection] = []
    selected: PlacementCandidate | None = None
    for candidate in sorted(parsed_candidates, key=lambda item: _candidate_sort_key(item, req)):
        host = parsed_hosts.get(candidate.host_id)
        pool = parsed_pools.get(candidate.pool_id)
        heartbeat = parsed_heartbeats.get(candidate.host_id)
        reason: tuple[str, str] | None = None
        if not candidate.enabled:
            reason = ("DISABLED", "candidate is disabled by policy")
        elif host is None:
            reason = ("HOST_UNKNOWN", "host is not registered")
        elif pool is None:
            reason = ("POOL_UNKNOWN", "capacity pool is not registered")
        elif heartbeat is None or heartbeat.registration_digest != host.registration_digest:
            reason = ("HEARTBEAT_MISSING", "host has no heartbeat matching its registration")
        elif now - _epoch(heartbeat.observed_at) > heartbeat_ttl_s:
            reason = ("HEARTBEAT_STALE", "host heartbeat exceeded its lease TTL")
        elif not set(req.capabilities) <= set(candidate.capabilities) or not set(req.capabilities) <= set(host.capabilities):
            missing = sorted(set(req.capabilities) - (set(candidate.capabilities) & set(host.capabilities)))
            reason = ("CAPABILITY_MISSING", f"missing capabilities: {', '.join(missing)}")
        elif req.operating_system is not None and candidate.operating_system != req.operating_system:
            reason = ("OS_INCOMPATIBLE", "candidate operating system does not satisfy the task")
        elif candidate.sandbox_profile not in host.sandbox_profiles or (req.sandbox_profile and candidate.sandbox_profile != req.sandbox_profile):
            reason = ("SANDBOX_INCOMPATIBLE", "host or task does not permit the sandbox profile")
        elif candidate.network_profile not in host.network_profiles or (req.network_profile and candidate.network_profile != req.network_profile):
            reason = ("NETWORK_INCOMPATIBLE", "host or task does not permit the network profile")
        elif candidate.billing_basis not in req.billing_basis:
            reason = ("BILLING_NOT_ALLOWED", "candidate billing basis is outside task policy")
        elif candidate.cost_per_run > req.max_cost_usd:
            reason = ("COST_EXCEEDED", "candidate cost exceeds task ceiling")
        elif req.model is not None and candidate.model != req.model:
            reason = ("MODEL_MISMATCH", "candidate model does not satisfy the task")
        elif req.role not in candidate.roles:
            reason = ("ROLE_UNSUPPORTED", "candidate does not support the requested role")
        elif req.project_id not in pool.allowed_projects and "*" not in pool.allowed_projects:
            reason = ("PROJECT_NOT_ALLOWED", "pool policy excludes this project")
        elif req.role not in pool.allowed_roles and "*" not in pool.allowed_roles:
            reason = ("ROLE_NOT_ALLOWED", "pool policy excludes this role")
        elif candidate.model not in pool.allowed_models and "*" not in pool.allowed_models:
            reason = ("MODEL_NOT_ALLOWED", "pool policy excludes this model")
        elif pool.in_flight + int(pool_used.get(pool.pool_id, 0)) >= pool.max_concurrency:
            reason = ("POOL_CONCURRENCY_EXHAUSTED", "capacity pool concurrency is exhausted")
        elif pool.quota_remaining is not None and pool.quota_remaining <= int(pool_used.get(pool.pool_id, 0)):
            reason = ("POOL_QUOTA_EXHAUSTED", "capacity pool quota is exhausted")
        elif host_used.get(host.host_id, 0) >= host.max_concurrency:
            reason = ("HOST_CONCURRENCY_EXHAUSTED", "host concurrency is exhausted")
        elif req.role in host.workload_concurrency and host_used.get(host.host_id, 0) + 1 > host.workload_concurrency[req.role]:
            reason = ("WORKLOAD_CONCURRENCY_EXHAUSTED", "host workload concurrency is exhausted")
        if reason is not None:
            trace.append(Rejection(candidate.candidate_id, reason[0], reason[1]))
            continue
        if selected is not None:
            # Continue evaluating later candidates so callers get a complete trace. Selection
            # remains the first eligible candidate under the deterministic ordering above.
            continue
        selected = candidate
    if selected is not None:
        candidate = selected
        body = {"schema_version": SCHEMA_VERSION, "kind": "assignment", "task_id": req.task_id,
                "project_id": req.project_id, "source_sha": req.source_sha, "engine": candidate.engine,
                "provider": candidate.provider, "capacity_pool": candidate.pool_id, "model": candidate.model,
                "host": candidate.host_id, "sandbox_profile": candidate.sandbox_profile,
                "network_profile": candidate.network_profile, "created_at": created_at}
        digest = hashlib.sha256(_canonical(body)).hexdigest()
        assignment = Assignment(req.task_id, req.project_id, req.source_sha, candidate.engine, candidate.provider,
                                candidate.pool_id, candidate.model, candidate.host_id, candidate.sandbox_profile,
                                candidate.network_profile, digest, body["created_at"])
        return assignment, tuple(trace)
    return None, tuple(trace)


def _epoch(timestamp: str) -> float:
    # ISO records are UTC and schema-validated; this parser intentionally avoids local timezone state.
    import calendar
    from datetime import datetime
    return calendar.timegm(datetime.strptime(timestamp.split(".")[0], "%Y-%m-%dT%H:%M:%SZ").timetuple())


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class HostRegistry:
    """Validated host registrations and monotonic heartbeat observations."""

    def __init__(self):
        self.hosts: dict[str, HostRegistration] = {}
        self.heartbeats: dict[str, HostHeartbeat] = {}

    def register(self, registration: HostRegistration) -> str:
        if not isinstance(registration, HostRegistration):
            raise SchemaError("INVALID_RECORD", "registration must be a HostRegistration")
        current = self.hosts.get(registration.host_id)
        if current is not None and current.registration_digest == registration.registration_digest:
            return "duplicate"
        self.hosts[registration.host_id] = registration
        # A new registration invalidates heartbeats from the previous capability set.
        self.heartbeats.pop(registration.host_id, None)
        return "registered"

    def heartbeat(self, value: HostHeartbeat) -> str:
        if not isinstance(value, HostHeartbeat):
            raise SchemaError("INVALID_RECORD", "heartbeat must be a HostHeartbeat")
        registration = self.hosts.get(value.host_id)
        if registration is None or registration.registration_digest != value.registration_digest:
            raise AdmissionError("HEARTBEAT_UNBOUND", "heartbeat does not match a registered host")
        current = self.heartbeats.get(value.host_id)
        if current is not None:
            if value.sequence < current.sequence:
                raise AdmissionError("HEARTBEAT_OUT_OF_ORDER", "heartbeat sequence moved backwards")
            if value.sequence == current.sequence:
                if value.to_dict() == current.to_dict():
                    return "duplicate"
                raise AdmissionError("HEARTBEAT_CONFLICT", "heartbeat sequence has conflicting data")
        self.heartbeats[value.host_id] = value
        return "accepted"

    def snapshot(self) -> tuple[dict[str, HostRegistration], dict[str, HostHeartbeat]]:
        return dict(self.hosts), dict(self.heartbeats)


class PlacementGovernor:
    """Atomic in-process host/pool admission around the pure resolver.

    Reservations are intentionally ephemeral.  A later durable lease adapter must persist the
    reservation and release it only after terminal reconciliation; this class never dispatches work.
    """

    def __init__(self, registry: HostRegistry, pools: Mapping[str, PoolStatus]):
        self.registry = registry
        self.pools = dict(pools)
        self._active: dict[str, Assignment] = {}

    def place(self, requirements: PlacementRequirements, candidates: Sequence[PlacementCandidate],
              *, now_epoch: float | None = None, created_at: str | None = None) -> tuple[Assignment | None, tuple[Rejection, ...]]:
        host_reserved: dict[str, int] = {}
        pool_reserved: dict[str, int] = {}
        for active in self._active.values():
            host_reserved[active.host] = host_reserved.get(active.host, 0) + 1
            pool_reserved[active.capacity_pool] = pool_reserved.get(active.capacity_pool, 0) + 1
        hosts, heartbeats = self.registry.snapshot()
        assignment, trace = resolve_placement(requirements, candidates, hosts, heartbeats, self.pools,
                                              now_epoch=now_epoch, created_at=created_at,
                                              reserved_host=host_reserved, reserved_pool=pool_reserved)
        if assignment is not None:
            self._active[assignment.assignment_digest] = assignment
        return assignment, trace

    def release(self, assignment: Assignment) -> str:
        digest = assignment.assignment_digest
        if digest not in self._active:
            return "duplicate"
        del self._active[digest]
        return "released"

    @property
    def active(self) -> tuple[Assignment, ...]:
        return tuple(self._active[key] for key in sorted(self._active))


class DurableFabricStore:
    """Crash-safe append-only lease/attempt/result journal with replay on construction."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.leases: dict[str, dict[str, Any]] = {}
        self.attempts: dict[str, dict[str, Any]] = {}
        self.results: dict[str, dict[str, Any]] = {}
        self._replay()

    def _replay(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                try:
                    event = json.loads(line)
                    if not isinstance(event, dict) or not isinstance(event.get("event"), str):
                        raise ValueError
                    self._apply(event)
                except (ValueError, TypeError, KeyError) as exc:
                    raise ReconciliationError("CORRUPT_JOURNAL", f"invalid fabric journal event at line {number}") from exc

    def _append(self, event: Mapping[str, Any]) -> None:
        data = (json.dumps(dict(event), sort_keys=True, separators=(",", ":")) + "\n").encode()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            view = memoryview(data)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise OSError("fabric journal write made no progress")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _apply(self, event: Mapping[str, Any]) -> None:
        kind = event["event"]
        if kind == "lease":
            self.leases[event["lease_id"]] = dict(event)
            self.attempts.setdefault(event["attempt_id"], {"event": "attempt", "schema_version": SCHEMA_VERSION,
                                                             "attempt_id": event["attempt_id"], "lease_id": event["lease_id"],
                                                             "assignment_digest": event["assignment_digest"],
                                                             "status": "active", "created_at": event["created_at"]})
        elif kind == "attempt":
            self.attempts[event["attempt_id"]] = dict(event)
        elif kind == "result":
            self.results[event["attempt_id"]] = dict(event)
            lease_id = event.get("lease_id")
            if lease_id in self.leases:
                self.leases[lease_id]["status"] = event["status"]
            if event["attempt_id"] in self.attempts:
                self.attempts[event["attempt_id"]]["status"] = event["status"]
        elif kind == "lease_status":
            self.leases[event["lease_id"]]["status"] = event["status"]
            self.leases[event["lease_id"]]["updated_at"] = event["updated_at"]
        else:
            raise ReconciliationError("UNKNOWN_EVENT", f"unknown fabric event: {kind}")

    def create_lease(self, assignment: Assignment, *, lease_id: str, attempt_id: str, remote_session_id: str,
                     now: str, expires_at: str) -> dict[str, Any]:
        _id(lease_id, "lease_id"); _id(attempt_id, "attempt_id"); _id(remote_session_id, "remote_session_id")
        _timestamp(now, "now"); _timestamp(expires_at, "expires_at")
        if lease_id in self.leases or attempt_id in self.attempts:
            raise AdmissionError("DUPLICATE_LEASE", "lease or attempt identity already exists")
        event = {"event": "lease", "schema_version": SCHEMA_VERSION, "lease_id": lease_id,
                 "attempt_id": attempt_id, "remote_session_id": remote_session_id,
                 "assignment_digest": assignment.assignment_digest, "assignment": assignment.to_dict(),
                 "status": "active", "created_at": now, "updated_at": now, "expires_at": expires_at}
        # Lease and attempt identity share one journal event.  A crash can therefore leave either
        # a complete lease/attempt record or no record, never a lease that cannot be reconciled.
        self._append(event); self._apply(event)
        return dict(event)

    def reconcile_restart(self, *, now: str) -> tuple[dict[str, Any], ...]:
        """Mark active leases as recovery-required exactly once; never relaunch remotely."""
        _timestamp(now, "now")
        recovered: list[dict[str, Any]] = []
        for lease_id, lease in sorted(self.leases.items()):
            if lease["status"] != "active":
                continue
            event = {"event": "lease_status", "schema_version": SCHEMA_VERSION, "lease_id": lease_id,
                     "status": "recovery_required", "updated_at": now}
            self._append(event); self._apply(event)
            recovered.append(dict(self.leases[lease_id]))
        return tuple(recovered)

    def expire(self, *, now: str) -> tuple[str, ...]:
        _timestamp(now, "now")
        expired: list[str] = []
        current = _epoch(now)
        for lease_id, lease in sorted(self.leases.items()):
            if lease["status"] in {"active", "recovery_required"} and current >= _epoch(lease["expires_at"]):
                event = {"event": "lease_status", "schema_version": SCHEMA_VERSION, "lease_id": lease_id,
                         "status": "expired", "updated_at": now}
                self._append(event); self._apply(event); expired.append(lease_id)
        return tuple(expired)

    def accept_result(self, *, attempt_id: str, lease_id: str, assignment_digest_value: str,
                      result_digest: str, status: str, observed_at: str) -> str:
        _id(attempt_id, "attempt_id"); _id(lease_id, "lease_id"); _digest(assignment_digest_value, "assignment_digest")
        _digest(result_digest, "result_digest"); _timestamp(observed_at, "observed_at")
        if status not in {"succeeded", "failed", "cancelled"}:
            raise ReconciliationError("INVALID_RESULT_STATUS", "result status is not terminal")
        existing = self.results.get(attempt_id)
        if existing is not None:
            if existing["result_digest"] == result_digest and existing["assignment_digest"] == assignment_digest_value:
                return "duplicate"
            raise ReconciliationError("CONFLICTING_RESULT", "attempt already has a different result")
        attempt = self.attempts.get(attempt_id)
        lease = self.leases.get(lease_id)
        if attempt is None or lease is None or attempt.get("lease_id") != lease_id:
            raise ReconciliationError("UNKNOWN_ATTEMPT", "result does not match a durable attempt")
        if assignment_digest_value != attempt["assignment_digest"]:
            raise ReconciliationError("ASSIGNMENT_MISMATCH", "result assignment does not match the attempt")
        if lease["status"] not in {"active", "recovery_required"}:
            raise ReconciliationError("LATE_RESULT", "result arrived after the lease was terminal")
        event = {"event": "result", "schema_version": SCHEMA_VERSION, "attempt_id": attempt_id,
                 "lease_id": lease_id, "assignment_digest": assignment_digest_value,
                 "result_digest": result_digest, "status": status, "observed_at": observed_at}
        self._append(event); self._apply(event)
        return "accepted"


class IntegrationCoordinator:
    """In-memory serialized same-project integration admission.

    This is a planning primitive only.  It never performs git operations.  Different projects can
    be admitted concurrently; one project has at most one active integration candidate.
    """

    def __init__(self):
        self._active: dict[str, str] = {}
        self._candidates: dict[str, dict[str, Any]] = {}

    def admit(self, *, candidate_id: str, project_id: str, source_sha: str, result_commit: str) -> str:
        _id(candidate_id, "candidate_id"); _id(project_id, "project_id"); _commit(source_sha, "source_sha"); _commit(result_commit, "result_commit")
        existing = self._candidates.get(candidate_id)
        if existing is not None:
            if existing["project_id"] == project_id and existing["source_sha"] == source_sha and existing["result_commit"] == result_commit:
                return "duplicate"
            raise AdmissionError("CONFLICTING_CANDIDATE", "candidate identity is already bound to another result")
        current = self._active.get(project_id)
        if current is not None:
            raise AdmissionError("INTEGRATION_SERIALIZED", f"project already has active integration candidate {current}")
        self._active[project_id] = candidate_id
        self._candidates[candidate_id] = {"project_id": project_id, "source_sha": source_sha, "result_commit": result_commit, "status": "active"}
        return "admitted"

    def complete(self, candidate_id: str) -> str:
        _id(candidate_id, "candidate_id")
        candidate = self._candidates.get(candidate_id)
        if candidate is None:
            raise AdmissionError("UNKNOWN_CANDIDATE", "candidate is not known")
        if candidate["status"] == "complete":
            return "duplicate"
        candidate["status"] = "complete"
        self._active.pop(candidate["project_id"], None)
        return "completed"

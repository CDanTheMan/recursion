"""Recursion v2 execution-fabric contracts.

This module is deliberately dependency-free.  It is the read-only contract boundary for
the first migration step: v2 registries are strict and fail closed, while readers for the
existing v1 files normalize legacy data without changing the v1 execution path.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40,64}$")
SECRET_REF = re.compile(r"^secret:[a-z][a-z0-9._/-]{1,127}$")
V2_VERSION = 2

REGISTRY_KINDS = {
    "engine", "provider", "capacity_pool", "model", "host", "sandbox_profile",
    "routing_policy", "project", "assignment",
}
ROLES = {"implementer", "verifier", "planner", "project-lead", "reviewer", "browser-qa"}
POLICIES = {
    "manual-pin", "subscription-first", "local-first", "cheapest-eligible",
    "fastest-eligible", "strongest-reviewer", "weighted-rotation", "no-metered-fallback",
}


class ContractError(ValueError):
    """A typed fail-closed contract error."""

    def __init__(self, message: str, code: str = "invalid-contract") -> None:
        super().__init__(message)
        self.code = code


def _obj(value: Any, where: str, allowed: set[str], required: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{where} must be an object")
    missing = required - set(value)
    extra = set(value) - allowed
    if missing:
        raise ContractError(f"{where} missing required fields: {', '.join(sorted(missing))}")
    if extra:
        raise ContractError(f"{where} has unknown fields: {', '.join(sorted(extra))}", "unknown-field")
    return value


def _str(value: Any, where: str, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{where} must be a non-empty string")
    if pattern is not None and not pattern.fullmatch(value):
        raise ContractError(f"{where} has an invalid format")
    return value


def _list(value: Any, where: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        raise ContractError(f"{where} must be a {'non-empty ' if nonempty else ''}list")
    if len(set(json.dumps(x, sort_keys=True) for x in value)) != len(value):
        raise ContractError(f"{where} must not contain duplicates")
    return value


def _strings(value: Any, where: str, *, nonempty: bool = False) -> list[str]:
    result = _list(value, where, nonempty=nonempty)
    if not all(isinstance(x, str) and x for x in result):
        raise ContractError(f"{where} must contain only non-empty strings")
    return result


def _bool(value: Any, where: str) -> bool:
    if not isinstance(value, bool):
        raise ContractError(f"{where} must be a boolean")
    return value


def _int(value: Any, where: str, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ContractError(f"{where} must be an integer >= {minimum}")
    return value


def _no_secrets(value: Any, where: str = "document") -> None:
    """Reject secret material, not merely obvious credential field names."""
    if isinstance(value, dict):
        for key, child in value.items():
            low = str(key).lower()
            secret_key = ("secret" in low or "password" in low or "private_key" in low
                          or "apikey" in low or "api_key" in low
                          or low == "token" or low.endswith("_token"))
            if secret_key:
                if low.endswith("_ref") and isinstance(child, str) and SECRET_REF.fullmatch(child):
                    continue
                raise ContractError(f"{where}.{key} contains secret material", "secret-material")
            _no_secrets(child, f"{where}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _no_secrets(child, f"{where}[{i}]")
    elif isinstance(value, str):
        if re.search(r"(?:sk-[A-Za-z0-9_-]{12,}|Bearer\s+\S+|-----BEGIN [A-Z ]+ KEY-----)", value, re.I):
            raise ContractError(f"{where} resembles a secret value", "secret-material")


def _common(record: Any, kind: str, fields: set[str], required: set[str]) -> dict[str, Any]:
    _no_secrets(record, kind)
    obj = _obj(record, kind, {"schema_version", "kind", "id", *fields}, {"schema_version", "kind", "id", *required})
    if obj["schema_version"] != V2_VERSION:
        raise ContractError(f"{kind}.schema_version must be {V2_VERSION}", "unsupported-version")
    if obj["kind"] != kind:
        raise ContractError(f"kind must be {kind!r}")
    _str(obj["id"], f"{kind}.id", IDENTIFIER)
    return obj


def _refs(value: Any, where: str) -> None:
    for item in _strings(value, where):
        _str(item, where, IDENTIFIER)


def validate_record(record: Any) -> dict[str, Any]:
    """Validate one v2 record and return it unchanged."""
    if not isinstance(record, dict) or not isinstance(record.get("kind"), str):
        raise ContractError("record.kind is required")
    kind = record["kind"]
    if kind not in REGISTRY_KINDS:
        raise ContractError(f"unknown registry kind {kind!r}", "unknown-kind")
    if kind == "engine":
        o = _common(record, kind, {"description", "runtime_layout", "argv_template", "structured_output", "roles", "capabilities", "health_probe", "cancellation", "resume", "usage_receipt", "network_capabilities", "compatible_sandbox_profiles", "compatible_host_capabilities", "enabled"}, {"description", "runtime_layout", "argv_template", "structured_output", "roles", "capabilities", "cancellation", "resume", "usage_receipt", "network_capabilities", "compatible_sandbox_profiles", "compatible_host_capabilities"})
        _str(o["description"], "engine.description")
        r = _obj(o["runtime_layout"], "engine.runtime_layout", {"kind", "executable", "runtime_paths", "read_only_mounts"}, {"kind", "executable", "runtime_paths", "read_only_mounts"})
        if r["kind"] not in {"bare", "runtime-tree"}: raise ContractError("engine.runtime_layout.kind is invalid")
        _str(r["executable"], "engine.runtime_layout.executable")
        _strings(r["runtime_paths"], "engine.runtime_layout.runtime_paths")
        _strings(r["read_only_mounts"], "engine.runtime_layout.read_only_mounts")
        _strings(o["argv_template"], "engine.argv_template", nonempty=True)
        _bool(o["structured_output"], "engine.structured_output")
        _strings(o["roles"], "engine.roles", nonempty=True)
        if not set(o["roles"]) <= ROLES: raise ContractError("engine.roles contains an unknown role")
        for name in ("capabilities", "network_capabilities", "compatible_sandbox_profiles", "compatible_host_capabilities"):
            _strings(o[name], f"engine.{name}")
        for name in ("cancellation", "resume", "usage_receipt"):
            _obj(o[name], f"engine.{name}", {"supported", "protocol"}, {"supported", "protocol"})
            _bool(o[name]["supported"], f"engine.{name}.supported"); _str(o[name]["protocol"], f"engine.{name}.protocol")
        if "health_probe" in o and o["health_probe"] is not None:
            p = _obj(o["health_probe"], "engine.health_probe", {"type", "endpoint", "timeout_s"}, {"type", "endpoint", "timeout_s"})
            if p["type"] not in {"none", "http", "command"}: raise ContractError("engine.health_probe.type is invalid")
            _str(p["endpoint"], "engine.health_probe.endpoint"); _int(p["timeout_s"], "engine.health_probe.timeout_s", 1)
        if "enabled" in o: _bool(o["enabled"], "engine.enabled")
    elif kind == "provider":
        o = _common(record, kind, {"endpoints", "egress_profile", "receipt_semantics", "error_classes", "data_classification"}, {"endpoints", "egress_profile", "receipt_semantics", "error_classes", "data_classification"})
        _strings(o["endpoints"], "provider.endpoints", nonempty=True); _str(o["egress_profile"], "provider.egress_profile"); _str(o["receipt_semantics"], "provider.receipt_semantics"); _strings(o["error_classes"], "provider.error_classes", nonempty=True); _str(o["data_classification"], "provider.data_classification")
    elif kind == "capacity_pool":
        o = _common(record, kind, {"account_id", "billing_basis", "credential_ref", "roles", "projects", "models", "hosts", "quota", "spend_ceiling_usd", "on_demand", "initial_concurrency", "cooldown_s", "fallback_policy", "status"}, {"account_id", "billing_basis", "credential_ref", "roles", "quota", "on_demand", "initial_concurrency", "fallback_policy", "status"})
        _str(o["account_id"], "capacity_pool.account_id"); _str(o["billing_basis"], "capacity_pool.billing_basis")
        _str(o["credential_ref"], "capacity_pool.credential_ref");
        if not SECRET_REF.fullmatch(o["credential_ref"]): raise ContractError("capacity_pool.credential_ref must be a secret reference")
        _strings(o["roles"], "capacity_pool.roles", nonempty=True); _refs(o.get("projects", []), "capacity_pool.projects"); _refs(o.get("models", []), "capacity_pool.models"); _refs(o.get("hosts", []), "capacity_pool.hosts")
        q = _obj(o["quota"], "capacity_pool.quota", {"period", "source", "confidence", "remaining"}, {"period", "source", "confidence"}); _str(q["period"], "capacity_pool.quota.period"); _str(q["source"], "capacity_pool.quota.source"); _str(q["confidence"], "capacity_pool.quota.confidence")
        if "remaining" in q: _int(q["remaining"], "capacity_pool.quota.remaining")
        if "spend_ceiling_usd" in o: _int(o["spend_ceiling_usd"], "capacity_pool.spend_ceiling_usd")
        _bool(o["on_demand"], "capacity_pool.on_demand"); _int(o["initial_concurrency"], "capacity_pool.initial_concurrency", 1); _str(o["fallback_policy"], "capacity_pool.fallback_policy"); _str(o["status"], "capacity_pool.status")
    elif kind == "model":
        o = _common(record, kind, {"provider_ids", "engine_ids", "roles", "data_classes", "capabilities", "reasoning_class", "speed_class", "cost_class", "efforts", "context_tokens", "status"}, {"provider_ids", "engine_ids", "roles", "data_classes", "capabilities", "reasoning_class", "speed_class", "cost_class", "efforts", "context_tokens", "status"})
        for name in ("provider_ids", "engine_ids", "roles", "data_classes", "capabilities", "efforts"): _strings(o[name], f"model.{name}")
        if not set(o["roles"]) <= ROLES: raise ContractError("model.roles contains an unknown role")
        for name in ("reasoning_class", "speed_class", "cost_class", "status"): _str(o[name], f"model.{name}")
        _int(o["context_tokens"], "model.context_tokens", 1)
    elif kind == "host":
        o = _common(record, kind, {"class", "operating_system", "architecture", "cpu", "ram_mb", "disk_mb", "gpu", "gui", "engine_ids", "sandbox_profile_ids", "capabilities", "network_profiles", "concurrency", "heartbeat", "recovery", "trust_class", "status"}, {"class", "operating_system", "architecture", "cpu", "ram_mb", "disk_mb", "gpu", "gui", "engine_ids", "sandbox_profile_ids", "capabilities", "network_profiles", "concurrency", "heartbeat", "recovery", "trust_class", "status"})
        for name in ("class", "operating_system", "architecture", "cpu", "gpu", "trust_class", "status"): _str(o[name], f"host.{name}")
        for name in ("ram_mb", "disk_mb"): _int(o[name], f"host.{name}", 1)
        _bool(o["gui"], "host.gui");
        for name in ("engine_ids", "sandbox_profile_ids", "capabilities", "network_profiles"): _strings(o[name], f"host.{name}")
        _int(o["concurrency"], "host.concurrency", 1)
        for name in ("heartbeat", "recovery"):
            x = _obj(o[name], f"host.{name}", {"protocol", "timeout_s"}, {"protocol", "timeout_s"}); _str(x["protocol"], f"host.{name}.protocol"); _int(x["timeout_s"], f"host.{name}.timeout_s", 1)
    elif kind == "sandbox_profile":
        o = _common(record, kind, {"isolation", "operating_system", "write_scope", "network_profiles", "capabilities", "trust_class", "controller_visibility"}, {"isolation", "operating_system", "write_scope", "network_profiles", "capabilities", "trust_class", "controller_visibility"})
        for name in ("isolation", "operating_system", "write_scope", "trust_class", "controller_visibility"): _str(o[name], f"sandbox_profile.{name}")
        _strings(o["network_profiles"], "sandbox_profile.network_profiles"); _strings(o["capabilities"], "sandbox_profile.capabilities")
    elif kind == "routing_policy":
        o = _common(record, kind, {"policy", "role", "candidate_order", "allow_metered", "fallback_policy", "weights"}, {"policy", "role", "candidate_order", "allow_metered", "fallback_policy"})
        if o["policy"] not in POLICIES: raise ContractError("routing_policy.policy is unknown")
        _str(o["role"], "routing_policy.role"); _strings(o["candidate_order"], "routing_policy.candidate_order"); _bool(o["allow_metered"], "routing_policy.allow_metered"); _str(o["fallback_policy"], "routing_policy.fallback_policy")
        if "weights" in o:
            if not isinstance(o["weights"], dict): raise ContractError("routing_policy.weights must be an object")
            for key, value in o["weights"].items(): _str(key, "routing_policy.weights key", IDENTIFIER); _int(value, "routing_policy.weights value", 1)
    elif kind == "project":
        o = _common(record, kind, {"repository", "default_branch", "integration_branch", "task_branch_pattern", "external_branch_patterns", "publication_policy", "source_policy", "allowed_paths", "gate_commands", "eligible_hosts", "eligible_pools", "status"}, {"repository", "default_branch", "integration_branch", "task_branch_pattern", "external_branch_patterns", "publication_policy", "source_policy", "allowed_paths", "gate_commands", "eligible_hosts", "eligible_pools", "status"})
        for name in ("repository", "default_branch", "integration_branch", "task_branch_pattern", "publication_policy", "source_policy", "status"): _str(o[name], f"project.{name}")
        for name in ("external_branch_patterns", "allowed_paths", "gate_commands", "eligible_hosts", "eligible_pools"): _strings(o[name], f"project.{name}")
        if o["publication_policy"] != "verified-integration-only" or o["source_policy"] != "exact-sha": raise ContractError("project publication/source policy is not fail-closed")
    else:  # assignment
        o = _common(record, kind, {"task_id", "project_id", "source_repository", "source_branch", "source_sha", "seed_manifest_digest", "engine_id", "provider_id", "capacity_pool_id", "model_id", "model_parameters", "host_id", "sandbox_profile_id", "network_profile", "allowed_paths", "gate_digest", "publication_policy", "created_at", "assignment_digest"}, {"task_id", "project_id", "source_repository", "source_branch", "source_sha", "seed_manifest_digest", "engine_id", "provider_id", "capacity_pool_id", "model_id", "model_parameters", "host_id", "sandbox_profile_id", "network_profile", "allowed_paths", "gate_digest", "publication_policy", "created_at", "assignment_digest"})
        for name in ("task_id", "project_id", "engine_id", "provider_id", "capacity_pool_id", "model_id", "host_id", "sandbox_profile_id"): _str(o[name], f"assignment.{name}")
        _str(o["source_sha"], "assignment.source_sha");
        if not COMMIT.fullmatch(o["source_sha"]): raise ContractError("assignment.source_sha is not a commit SHA")
        for name in ("seed_manifest_digest", "gate_digest", "assignment_digest"): _str(o[name], f"assignment.{name}", SHA256)
        _str(o["publication_policy"], "assignment.publication_policy")
        _strings(o["allowed_paths"], "assignment.allowed_paths", nonempty=True); _str(o["source_repository"], "assignment.source_repository"); _str(o["source_branch"], "assignment.source_branch"); _str(o["network_profile"], "assignment.network_profile"); _str(o["created_at"], "assignment.created_at")
        if not isinstance(o["model_parameters"], dict): raise ContractError("assignment.model_parameters must be an object")
        if o["assignment_digest"] != digest({key: value for key, value in o.items() if key != "assignment_digest"}):
            raise ContractError("assignment_digest does not match immutable assignment", "digest-mismatch")
    return record


def load_registry(path: Path | str, expected_kind: str | None = None) -> list[dict[str, Any]]:
    """Load a v2 collection (or one-record file), validating every entry."""
    try: raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc: raise ContractError(f"cannot read registry {path}: {exc}", "unavailable") from exc
    if isinstance(raw, dict) and "entries" in raw:
        allowed = {"schema_version", "registry", "entries"}
        _obj(raw, "registry", allowed, allowed)
        if raw["schema_version"] != V2_VERSION: raise ContractError("registry schema_version is unsupported", "unsupported-version")
        if expected_kind and raw["registry"] != expected_kind: raise ContractError("registry kind mismatch")
        entries = raw["entries"]
    else: entries = [raw]
    if not isinstance(entries, list): raise ContractError("registry.entries must be a list")
    result = [validate_record(x) for x in entries]
    ids = [x["id"] for x in result]
    if len(set(ids)) != len(ids): raise ContractError("registry has duplicate ids")
    return result


def validate_registry(records: Any, expected_kind: str | None = None) -> list[dict[str, Any]]:
    """Validate an already decoded collection without touching the filesystem."""
    if isinstance(records, Mapping) and "entries" in records:
        if records.get("schema_version") != V2_VERSION:
            raise ContractError("registry schema_version is unsupported", "unsupported-version")
        if expected_kind and records.get("registry") != expected_kind:
            raise ContractError("registry kind mismatch")
        records = records.get("entries")
    if not isinstance(records, list):
        raise ContractError("registry entries must be a list")
    result = [validate_record(item) for item in records]
    if len({item["id"] for item in result}) != len(result):
        raise ContractError("registry has duplicate ids")
    return result


def load_config(config_dir: Path | str) -> dict[str, list[dict[str, Any]]]:
    base = Path(config_dir)
    result: dict[str, list[dict[str, Any]]] = {}
    for kind in REGISTRY_KINDS:
        directory_name = {
            "capacity_pool": "capacity-pools",
            "sandbox_profile": "sandbox-profiles",
            "routing_policy": "routing-policies",
        }.get(kind, kind + "s")
        directory = base / directory_name
        files = sorted(directory.glob("*.json")) if directory.is_dir() else []
        result[kind] = []
        for file in files: result[kind].extend(load_registry(file, kind))
    return result


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str: return hashlib.sha256(_canonical(value)).hexdigest()


def _find(items: Iterable[Mapping[str, Any]], item_id: str, kind: str) -> dict[str, Any]:
    found = [dict(x) for x in items if x.get("id") == item_id]
    if len(found) != 1: raise ContractError(f"{kind} {item_id!r} is not uniquely registered", "unknown-reference")
    return found[0]


@dataclass(frozen=True)
class Resolution:
    assignment: dict[str, Any] | None
    trace: tuple[dict[str, Any], ...]
    status: str


def resolve_assignment(task: Mapping[str, Any], registries: Mapping[str, list[dict[str, Any]]], *, policy: str | None = None) -> Resolution:
    """Resolve a task without side effects.  Every candidate has a deterministic trace."""
    if not isinstance(task, Mapping): raise ContractError("task must be an object")
    _no_secrets(task, "task")
    for name in ("task_id", "project_id", "source_repository", "source_branch", "source_sha", "seed_manifest_digest", "gate_digest", "allowed_paths", "role", "requirements"): 
        if name not in task: raise ContractError(f"task missing required field {name}")
    _str(task["task_id"], "task.task_id"); _str(task["project_id"], "task.project_id"); _str(task["source_sha"], "task.source_sha"); _str(task["seed_manifest_digest"], "task.seed_manifest_digest", SHA256); _str(task["gate_digest"], "task.gate_digest", SHA256); _strings(task["allowed_paths"], "task.allowed_paths", nonempty=True); _str(task["role"], "task.role")
    requirements = task["requirements"]
    if not isinstance(requirements, Mapping): raise ContractError("task.requirements must be an object")
    policy = policy or str(task.get("routing_policy", "cheapest-eligible"))
    if policy not in POLICIES: raise ContractError(f"unknown routing policy {policy!r}", "unknown-policy")
    project = _find(registries.get("project", []), str(task["project_id"]), "project")
    engines = sorted(registries.get("engine", []), key=lambda x: x["id"]); providers = sorted(registries.get("provider", []), key=lambda x: x["id"]); pools = sorted(registries.get("capacity_pool", []), key=lambda x: x["id"]); models = sorted(registries.get("model", []), key=lambda x: x["id"]); hosts = sorted(registries.get("host", []), key=lambda x: x["id"]); sandboxes = sorted(registries.get("sandbox_profile", []), key=lambda x: x["id"])
    trace: list[dict[str, Any]] = []; candidates: list[dict[str, Any]] = []
    for e in engines:
      for p in providers:
       for pool in pools:
        for m in models:
         for h in hosts:
          for s in sandboxes:
            cid = ":".join((e["id"], p["id"], pool["id"], m["id"], h["id"], s["id"]))
            reasons: list[str] = []
            if e.get("status", "active") not in {"active", "ready"} or e.get("enabled", True) is False: reasons.append("engine-unavailable")
            if e["id"] not in h.get("engine_ids", []): reasons.append("host-missing-engine")
            if p["id"] not in m.get("provider_ids", []) or e["id"] not in m.get("engine_ids", []): reasons.append("model-incompatible")
            if task["role"] not in e.get("roles", []) or task["role"] not in m.get("roles", []) or task["role"] not in pool.get("roles", []): reasons.append("role-not-supported")
            if pool.get("status", "active") not in {"active", "ready"}: reasons.append("pool-unavailable")
            if pool.get("quota", {}).get("remaining") == 0: reasons.append("quota-exhausted")
            if pool.get("projects") and task["project_id"] not in pool["projects"]: reasons.append("pool-project-not-allowed")
            if pool.get("models") and m["id"] not in pool["models"]: reasons.append("pool-model-not-allowed")
            if pool.get("hosts") and h["id"] not in pool["hosts"]: reasons.append("pool-host-not-allowed")
            if project.get("eligible_hosts") and h["id"] not in project["eligible_hosts"]: reasons.append("project-host-not-allowed")
            if project.get("eligible_pools") and pool["id"] not in project["eligible_pools"]: reasons.append("project-pool-not-allowed")
            if s["id"] not in e.get("compatible_sandbox_profiles", []) or s["id"] not in h.get("sandbox_profile_ids", []): reasons.append("sandbox-incompatible")
            if s.get("network_profiles") and not (set(s["network_profiles"]) & set(h.get("network_profiles", []))): reasons.append("network-profile-unavailable")
            if requirements.get("operating_system") and h.get("operating_system") != requirements["operating_system"]: reasons.append("operating-system-mismatch")
            available = set(e.get("capabilities", [])) | set(m.get("capabilities", [])) | set(h.get("capabilities", [])) | set(s.get("capabilities", []))
            missing = sorted(set(requirements.get("capabilities", [])) - available)
            if missing: reasons.append("missing-capabilities:" + ",".join(missing))
            if requirements.get("isolation") and s.get("isolation") != requirements["isolation"]: reasons.append("isolation-mismatch")
            if requirements.get("data_class") and requirements["data_class"] not in m.get("data_classes", []): reasons.append("data-class-not-allowed")
            if requirements.get("billing") and pool.get("billing_basis") not in requirements["billing"]: reasons.append("billing-not-allowed")
            if requirements.get("network_profile") and requirements["network_profile"] not in h.get("network_profiles", []): reasons.append("network-profile-mismatch")
            if policy == "manual-pin":
                pin = task.get("manual_pin")
                if not isinstance(pin, Mapping): reasons.append("manual-pin-missing")
                elif any(pin.get(k) != c["id"] for k, c in (("engine", e), ("provider", p), ("capacity_pool", pool), ("model", m), ("host", h), ("sandbox_profile", s))): reasons.append("manual-pin-mismatch")
            if not project.get("publication_policy") == "verified-integration-only": reasons.append("publication-policy-invalid")
            if pool.get("billing_basis") == "metered" and (policy == "no-metered-fallback" or not pool.get("on_demand", False) or not task.get("allow_metered", False)): reasons.append("metered-not-approved")
            item = {"candidate": cid, "accepted": not reasons, "rejections": reasons}
            trace.append(item)
            if not reasons: candidates.append({"engine": e, "provider": p, "pool": pool, "model": m, "host": h, "sandbox": s})
    if not candidates: return Resolution(None, tuple(trace), "deferred")
    def score(c: dict[str, Any]) -> tuple[Any, ...]:
        e, p, pool, m, h, s = c["engine"], c["provider"], c["pool"], c["model"], c["host"], c["sandbox"]
        billing = {"local": 0, "included": 1, "weekly-included": 1, "flat-subscription": 1, "human": 2, "metered": 3}.get(pool.get("billing_basis"), 9)
        speed = {"fast": 0, "medium": 1, "slow": 2}.get(m.get("speed_class"), 9); reasoning = {"frontier": 0, "strong": 1, "standard": 2}.get(m.get("reasoning_class"), 9)
        if policy == "local-first": return (billing, h["id"], e["id"], m["id"], pool["id"], s["id"])
        if policy == "fastest-eligible": return (speed, billing, h["id"], e["id"], m["id"], pool["id"], s["id"])
        if policy == "strongest-reviewer": return (reasoning, speed, billing, m["id"], e["id"], pool["id"], h["id"], s["id"])
        if policy == "subscription-first": return (billing, pool["id"], m["id"], e["id"], h["id"], s["id"])
        if policy == "manual-pin":
            pin = task.get("manual_pin", {})
            return (0 if all(pin.get(k) == c[k]["id"] for k in ("engine", "provider", "capacity_pool", "model", "host", "sandbox_profile")) else 1,)
        if policy == "weighted-rotation":
            return (int(digest(task["task_id"] + ":" + pool["id"])[0:8], 16),)
        return (billing, speed, m.get("cost_class", "zz"), pool["id"], m["id"], e["id"], h["id"], s["id"])
    chosen = sorted(candidates, key=score)[0]
    network_profiles = sorted(set(chosen["sandbox"]["network_profiles"]) & set(chosen["host"].get("network_profiles", [])))
    safe_task_id = re.sub(r"[^a-z0-9-]", "-", str(task["task_id"]).lower()).strip("-") or digest(task["task_id"])[:16]
    assignment = {"schema_version": 2, "kind": "assignment", "id": f"assignment-{safe_task_id}", "task_id": task["task_id"], "project_id": task["project_id"], "source_repository": task["source_repository"], "source_branch": task["source_branch"], "source_sha": task["source_sha"], "seed_manifest_digest": task["seed_manifest_digest"], "engine_id": chosen["engine"]["id"], "provider_id": chosen["provider"]["id"], "capacity_pool_id": chosen["pool"]["id"], "model_id": chosen["model"]["id"], "model_parameters": dict(task.get("model_parameters", {})), "host_id": chosen["host"]["id"], "sandbox_profile_id": chosen["sandbox"]["id"], "network_profile": network_profiles[0], "allowed_paths": list(task["allowed_paths"]), "gate_digest": task["gate_digest"], "publication_policy": project["publication_policy"], "created_at": str(task.get("created_at", "dry-run"))}
    assignment["assignment_digest"] = digest({k: v for k, v in assignment.items() if k != "assignment_digest"})
    validate_record(assignment)
    return Resolution(assignment, tuple(trace), "assigned")


def read_v1_manifest(data: Mapping[str, Any]) -> dict[str, Any]:
    """Compatibility reader for scripts/engines/*.json (never mutates it)."""
    if not isinstance(data, Mapping) or data.get("schema_version") != 1: raise ContractError("unsupported v1 engine manifest", "unsupported-version")
    return {"schema_version": 1, "kind": "engine", "id": data.get("name"), "description": data.get("description", ""), "runtime_layout": {"kind": "bare", "executable": data.get("executable", ""), "runtime_paths": [], "read_only_mounts": []}, "argv_template": list(data.get("argv", [])), "structured_output": False, "roles": list(data.get("roles", [])), "capabilities": [], "health_probe": data.get("availability_probe"), "cancellation": {"supported": False, "protocol": "legacy"}, "resume": {"supported": False, "protocol": "legacy"}, "usage_receipt": {"supported": False, "protocol": "legacy"}, "network_capabilities": list(data.get("network", {}).get("endpoints", [])), "compatible_sandbox_profiles": ["strict-linux"], "compatible_host_capabilities": []}


read_v1_engine_manifest = read_v1_manifest


def read_v1_portfolio_row(row: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(row, str):
        cols = row.rstrip("\r\n").split("\t")
        if len(cols) != 8 or cols[0].startswith("#"): raise ContractError("invalid v1 portfolio row")
        row = dict(zip(("id", "repository", "remote", "default_branch", "credential_ref", "roadmap", "topic", "status"), cols))
    if not isinstance(row, Mapping): raise ContractError("invalid v1 portfolio row")
    return {"schema_version": 1, "kind": "project", "id": row.get("id", row.get("project")), "repository": row.get("repository", row.get("path")), "remote": row.get("remote"), "default_branch": row.get("default_branch", row.get("branch")), "credential_ref": row.get("credential_ref", row.get("sshkey")), "status": row.get("status")}


def read_v1_project_config(data: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(data, Mapping) or data.get("schema_version") != 1: raise ContractError("unsupported v1 project config", "unsupported-version")
    return {"schema_version": 1, "kind": "project", "id": data.get("id"), "repository": data.get("repo"), "remote": data.get("remote"), "default_branch": data.get("default_branch"), "credential_ref": data.get("deploy_key_ref"), "allowed_paths": list(data.get("allowed_paths", [])), "status": data.get("status")}


read_v1_portfolio = read_v1_portfolio_row
read_v1_project = read_v1_project_config


def _read_legacy_header(data: str | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(data, Mapping):
        return data
    if not isinstance(data, str):
        raise ContractError("invalid v1 header")
    values: dict[str, Any] = {}
    for line in data.splitlines():
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            continue
        if key in {"allowed_paths", "non_goals", "dependencies", "gate_files", "controller_gate_files"}:
            values[key] = [item for item in value.split(",") if item]
        else:
            values[key] = value
    return values


def read_v1_task_header(data: str | Mapping[str, Any]) -> dict[str, Any]:
    data = _read_legacy_header(data)
    if data.get("schema_version") not in (1, "1"): raise ContractError("unsupported v1 task header", "unsupported-version")
    return {"schema_version": 1, "kind": "task", "task_id": data.get("id"), "project_id": data.get("project_id"), "source_sha": data.get("base_commit", data.get("source_sha")), "role": "implementer", "model_alias": data.get("model_alias"), "allowed_paths": list(data.get("allowed_paths", [])), "gate_digest": (data.get("gate_contract") or {}).get("acceptance_sha256")}


def read_v1_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(data, Mapping) or data.get("schema_version") != 1: raise ContractError("unsupported v1 evidence", "unsupported-version")
    return {"schema_version": 1, "kind": "evidence", "run_id": data.get("id"), "task_id": data.get("task_id"), "source_sha": data.get("base_commit"), "engine_id": data.get("engine", data.get("worker")), "model_alias": data.get("model_alias"), "status": data.get("status")}


read_v1_run_evidence = read_v1_evidence
dry_resolve_assignment = resolve_assignment

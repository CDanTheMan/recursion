"""Recursion v2 execution-fabric contracts.

This module is deliberately dependency-free.  It is the read-only contract boundary for
the first migration step: v2 registries are strict and fail closed, while readers for the
existing v1 files normalize legacy data without changing the v1 execution path.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40,64}$")
SECRET_REF = re.compile(r"^secret:[a-z][a-z0-9._/-]{1,127}$")
PATH_PART = re.compile(r"^[^\x00/\\]+$")
ENDPOINT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
V2_VERSION = 2

REGISTRY_KINDS = {
    "engine", "provider", "capacity_pool", "model", "host", "sandbox_profile",
    "execution_profile", "routing_policy", "project", "assignment",
}
ROLES = {"implementer", "verifier", "planner", "project-lead", "reviewer", "browser-qa"}
POLICIES = {
    "manual-pin", "subscription-first", "local-first", "cheapest-eligible",
    "fastest-eligible", "strongest-reviewer", "weighted-rotation", "no-metered-fallback",
}
BILLING_BASES = {"included", "weekly-included", "metered", "local", "human"}
APPROVED_CONTROLLER_VISIBILITY = "none"
TRUST_COMPATIBILITY = {"coordinator": {"coordinator", "untrusted-worker"}, "untrusted-worker": {"untrusted-worker"}, "worker": {"worker", "untrusted-worker"}}
ROUTING_ORDER_FIELDS = {
    "billing_basis", "cost_class", "pool_id", "provider_id", "capacity_pool_id", "model_id", "engine_id", "host_id",
    "sandbox_profile_id", "speed_class", "reasoning_class", "manual_pin",
}
SECRET_PATTERN = r"(?:[sS][kK]-[A-Za-z0-9_-]{12,}|[gG][hH][pP]_[A-Za-z0-9]{12,}|[gG][iI][tT][hH][uU][bB]_[pP][aA][tT]_[A-Za-z0-9_]{12,}|[xX][oO][xX][bBaApPrRsS]-[A-Za-z0-9-]{12,}|[aA][kK][iI][aA][0-9A-Za-z]{16}|[nN][pP][mM]_[A-Za-z0-9]{12,}|[aA][iI][zZ][aA][0-9A-Za-z_-]{20,}|[bB][eE][aA][rR][eE][rR][ \\t]+[^ \\t]+|(?:[aA][pP][iI][-_]?[kK][eE][yY]|[pP][aA][sS][sS][wW][oO][rR][dD]|[sS][eE][cC][rR][eE][tT])[ \\t]*[:=]|-----BEGIN [A-Z ]+ KEY-----)"
TASK_FIELDS = {
    "task_id", "project_id", "source_repository", "source_branch", "source_sha",
    "seed_manifest_digest", "gate_digest", "allowed_paths", "role", "requirements",
    "model_parameters", "created_at", "manual_pin", "execution_profile", "preferences",
}
REQUIREMENT_FIELDS = {
    "capabilities", "engine_capabilities", "model_capabilities", "host_capabilities",
    "sandbox_capabilities", "operating_system", "isolation", "data_class", "billing",
    "network_profile", "max_cost_usd",
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


def _safe_relative_path(value: Any, where: str) -> str:
    """Validate a workspace-relative path; never normalize an unsafe path into safety."""
    value = _str(value, where)
    if value != value.strip() or "\x00" in value or value.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", value):
        raise ContractError(f"{where} must be a clean relative path", "unsafe-path")
    parts = re.split(r"[/\\]", value)
    if not parts or any(not part or part in {".", ".."} or not PATH_PART.fullmatch(part) for part in parts):
        raise ContractError(f"{where} contains an unsafe path component", "unsafe-path")
    return "/".join(parts)


def _secure_file(path: Path | str, *, root: Path | None = None) -> Path:
    """Resolve a config file while refusing traversal and symlink/reparse escapes."""
    raw = os.fspath(path)
    if "\x00" in raw:
        raise ContractError("path contains NUL", "unsafe-path")
    # A caller may provide an absolute root, but may not smuggle traversal into it.
    if any(part in {".", ".."} for part in Path(raw).parts):
        raise ContractError(f"unsafe path {raw!r}", "unsafe-path")
    candidate = Path(raw)
    original = candidate.absolute()
    cursor = original
    while True:
        if cursor.exists():
            try: attrs = getattr(cursor.stat(), "st_file_attributes", 0)
            except OSError as exc: raise ContractError(f"path is unavailable: {cursor}", "unavailable") from exc
            if cursor.is_symlink() or attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
                raise ContractError(f"symlink/reparse path is refused: {cursor}", "unsafe-path")
        if cursor.parent == cursor: break
        cursor = cursor.parent
    try:
        base = (root or candidate.parent).resolve(strict=True)
        target = candidate.resolve(strict=True)
    except OSError as exc:
        raise ContractError(f"path is unavailable: {candidate}", "unavailable") from exc
    if root is not None:
        try: target.relative_to(base)
        except ValueError as exc: raise ContractError("path escapes registry root", "unsafe-path") from exc
    cursor = target
    while True:
        try: cursor.stat()
        except OSError as exc: raise ContractError(f"path is unavailable: {cursor}", "unavailable") from exc
        if cursor.is_symlink() or bool(getattr(cursor.stat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT if hasattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT") else False):
            raise ContractError(f"symlink/reparse path is refused: {cursor}", "unsafe-path")
        if cursor == base or cursor.parent == cursor: break
        cursor = cursor.parent
    if not target.is_file():
        raise ContractError(f"registry path is not a file: {target}", "unavailable")
    return target


secure_file = _secure_file


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


def _workspace_paths(value: Any, where: str, *, nonempty: bool = False) -> list[str]:
    items = _strings(value, where, nonempty=nonempty)
    return [_safe_relative_path(item, f"{where}[{index}]") for index, item in enumerate(items)]


def _model_parameters(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{where} must be an object")
    allowed = {"effort", "context_tokens", "temperature", "structured_output"}
    extra = set(value) - allowed
    if extra: raise ContractError(f"{where} has unknown fields: {', '.join(sorted(extra))}", "unknown-field")
    if "effort" in value: _str(value["effort"], f"{where}.effort")
    if "context_tokens" in value: _int(value["context_tokens"], f"{where}.context_tokens", 1)
    if "temperature" in value and (not isinstance(value["temperature"], (int, float)) or isinstance(value["temperature"], bool) or not 0 <= value["temperature"] <= 2): raise ContractError(f"{where}.temperature is outside 0..2")
    if "structured_output" in value: _bool(value["structured_output"], f"{where}.structured_output")
    return value


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
        if _looks_secret(value):
            raise ContractError(f"{where} resembles a secret value", "secret-material")


def _looks_secret(value: str) -> bool:
    if SECRET_REF.fullmatch(value):
        return False
    # SECRET_PATTERN is stored in a raw Python literal; make its whitespace
    # escapes equivalent to the JSON-Schema expression before matching.
    return re.search(SECRET_PATTERN.replace(r"\\t", r"\t"), value) is not None


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
        _safe_relative_path(r["executable"], "engine.runtime_layout.executable")
        _workspace_paths(r["runtime_paths"], "engine.runtime_layout.runtime_paths")
        _workspace_paths(r["read_only_mounts"], "engine.runtime_layout.read_only_mounts")
        _strings(o["argv_template"], "engine.argv_template", nonempty=True)
        _bool(o["structured_output"], "engine.structured_output")
        _strings(o["roles"], "engine.roles", nonempty=True)
        if not set(o["roles"]) <= ROLES: raise ContractError("engine.roles contains an unknown role")
        for name in ("capabilities", "network_capabilities", "compatible_host_capabilities"):
            _strings(o[name], f"engine.{name}")
        _refs(o["compatible_sandbox_profiles"], "engine.compatible_sandbox_profiles")
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
        _strings(o["endpoints"], "provider.endpoints", nonempty=True)
        for endpoint in o["endpoints"]: _str(endpoint, "provider.endpoint", ENDPOINT)
        _str(o["egress_profile"], "provider.egress_profile"); _str(o["receipt_semantics"], "provider.receipt_semantics"); _strings(o["error_classes"], "provider.error_classes", nonempty=True); _str(o["data_classification"], "provider.data_classification")
    elif kind == "capacity_pool":
        o = _common(record, kind, {"account_id", "billing_basis", "credential_ref", "roles", "projects", "models", "hosts", "quota", "spend_ceiling_usd", "on_demand", "initial_concurrency", "cooldown_s", "fallback_policy", "status"}, {"account_id", "billing_basis", "credential_ref", "roles", "quota", "on_demand", "initial_concurrency", "fallback_policy", "status"})
        _str(o["account_id"], "capacity_pool.account_id"); _str(o["billing_basis"], "capacity_pool.billing_basis")
        if o["billing_basis"] not in BILLING_BASES: raise ContractError("capacity_pool.billing_basis is invalid")
        _str(o["credential_ref"], "capacity_pool.credential_ref");
        if not SECRET_REF.fullmatch(o["credential_ref"]): raise ContractError("capacity_pool.credential_ref must be a secret reference")
        _strings(o["roles"], "capacity_pool.roles", nonempty=True)
        if not set(o["roles"]) <= ROLES: raise ContractError("capacity_pool.roles contains an unknown role")
        _refs(o.get("projects", []), "capacity_pool.projects"); _refs(o.get("models", []), "capacity_pool.models"); _refs(o.get("hosts", []), "capacity_pool.hosts")
        q = _obj(o["quota"], "capacity_pool.quota", {"period", "source", "confidence", "remaining"}, {"period", "source", "confidence"}); _str(q["period"], "capacity_pool.quota.period"); _str(q["source"], "capacity_pool.quota.source"); _str(q["confidence"], "capacity_pool.quota.confidence")
        if "remaining" in q: _int(q["remaining"], "capacity_pool.quota.remaining")
        if "spend_ceiling_usd" in o: _int(o["spend_ceiling_usd"], "capacity_pool.spend_ceiling_usd")
        if "cooldown_s" in o: _int(o["cooldown_s"], "capacity_pool.cooldown_s", 0)
        _bool(o["on_demand"], "capacity_pool.on_demand"); _int(o["initial_concurrency"], "capacity_pool.initial_concurrency", 1); _str(o["fallback_policy"], "capacity_pool.fallback_policy");
        if o["fallback_policy"] not in {"defer", "approved", "allow-approved"}: raise ContractError("capacity_pool.fallback_policy is invalid")
        _str(o["status"], "capacity_pool.status")
    elif kind == "model":
        o = _common(record, kind, {"provider_ids", "engine_ids", "roles", "data_classes", "capabilities", "reasoning_class", "speed_class", "cost_class", "efforts", "context_tokens", "status"}, {"provider_ids", "engine_ids", "roles", "data_classes", "capabilities", "reasoning_class", "speed_class", "cost_class", "efforts", "context_tokens", "status"})
        _refs(o["provider_ids"], "model.provider_ids"); _refs(o["engine_ids"], "model.engine_ids")
        _strings(o["roles"], "model.roles", nonempty=True)
        for name in ("data_classes", "capabilities", "efforts"): _strings(o[name], f"model.{name}")
        if not set(o["roles"]) <= ROLES: raise ContractError("model.roles contains an unknown role")
        for name in ("reasoning_class", "speed_class", "cost_class", "status"): _str(o[name], f"model.{name}")
        _int(o["context_tokens"], "model.context_tokens", 1)
    elif kind == "host":
        o = _common(record, kind, {"class", "operating_system", "architecture", "cpu", "ram_mb", "disk_mb", "gpu", "gui", "engine_ids", "sandbox_profile_ids", "capabilities", "network_profiles", "network_endpoints", "concurrency", "heartbeat", "recovery", "trust_class", "status"}, {"class", "operating_system", "architecture", "cpu", "ram_mb", "disk_mb", "gpu", "gui", "engine_ids", "sandbox_profile_ids", "capabilities", "network_profiles", "network_endpoints", "concurrency", "heartbeat", "recovery", "trust_class", "status"})
        for name in ("class", "operating_system", "architecture", "cpu", "gpu", "trust_class", "status"): _str(o[name], f"host.{name}")
        for name in ("ram_mb", "disk_mb"): _int(o[name], f"host.{name}", 1)
        _bool(o["gui"], "host.gui");
        _refs(o["engine_ids"], "host.engine_ids"); _refs(o["sandbox_profile_ids"], "host.sandbox_profile_ids")
        for name in ("capabilities", "network_profiles", "network_endpoints"): _strings(o[name], f"host.{name}")
        for endpoint in o["network_endpoints"]: _str(endpoint, "host.network_endpoint", ENDPOINT)
        _int(o["concurrency"], "host.concurrency", 1)
        for name in ("heartbeat", "recovery"):
            x = _obj(o[name], f"host.{name}", {"protocol", "timeout_s"}, {"protocol", "timeout_s"}); _str(x["protocol"], f"host.{name}.protocol"); _int(x["timeout_s"], f"host.{name}.timeout_s", 1)
    elif kind == "sandbox_profile":
        o = _common(record, kind, {"isolation", "operating_system", "write_scope", "network_profiles", "network_endpoints", "capabilities", "trust_class", "controller_visibility"}, {"isolation", "operating_system", "write_scope", "network_profiles", "network_endpoints", "capabilities", "trust_class", "controller_visibility"})
        for name in ("isolation", "operating_system", "write_scope", "trust_class", "controller_visibility"): _str(o[name], f"sandbox_profile.{name}")
        if o["controller_visibility"] != APPROVED_CONTROLLER_VISIBILITY: raise ContractError("sandbox_profile.controller_visibility is not approved")
        _strings(o["network_profiles"], "sandbox_profile.network_profiles"); _strings(o["network_endpoints"], "sandbox_profile.network_endpoints"); _strings(o["capabilities"], "sandbox_profile.capabilities")
        for endpoint in o["network_endpoints"]: _str(endpoint, "sandbox_profile.network_endpoint", ENDPOINT)
    elif kind == "execution_profile":
        o = _common(record, kind, {"roles", "engine_ids", "provider_ids", "capacity_pool_ids", "model_ids", "host_ids", "sandbox_profile_ids", "network_profiles"}, {"roles", "engine_ids", "provider_ids", "capacity_pool_ids", "model_ids", "host_ids", "sandbox_profile_ids", "network_profiles"})
        _strings(o["roles"], "execution_profile.roles", nonempty=True)
        if not set(o["roles"]) <= ROLES: raise ContractError("execution_profile.roles contains an unknown role")
        for name in ("engine_ids", "provider_ids", "capacity_pool_ids", "model_ids", "host_ids", "sandbox_profile_ids"): _refs(o[name], f"execution_profile.{name}",)
        _strings(o["network_profiles"], "execution_profile.network_profiles", nonempty=True)
    elif kind == "routing_policy":
        o = _common(record, kind, {"policy", "role", "candidate_order", "allow_metered", "fallback_policy", "weights"}, {"policy", "role", "candidate_order", "allow_metered", "fallback_policy"})
        if o["policy"] not in POLICIES: raise ContractError("routing_policy.policy is unknown")
        _str(o["role"], "routing_policy.role")
        if o["role"] not in ROLES: raise ContractError("routing_policy.role is unknown role")
        _strings(o["candidate_order"], "routing_policy.candidate_order", nonempty=True)
        if not set(o["candidate_order"]) <= ROUTING_ORDER_FIELDS: raise ContractError("routing_policy.candidate_order contains an unknown field")
        if len(o["candidate_order"]) != len(set(o["candidate_order"])): raise ContractError("routing_policy.candidate_order is ambiguous", "duplicate-field")
        _bool(o["allow_metered"], "routing_policy.allow_metered"); _str(o["fallback_policy"], "routing_policy.fallback_policy")
        if o["fallback_policy"] not in {"defer", "approved", "allow-approved"}: raise ContractError("routing_policy.fallback_policy is invalid")
        if o["allow_metered"] and o["fallback_policy"] not in {"approved", "allow-approved"}: raise ContractError("metered routing requires an approved fallback")
        if "weights" in o:
            if not isinstance(o["weights"], dict): raise ContractError("routing_policy.weights must be an object")
            if o["policy"] != "weighted-rotation": raise ContractError("weights are only valid for weighted-rotation")
            for key, value in o["weights"].items(): _str(key, "routing_policy.weights key", IDENTIFIER); _int(value, "routing_policy.weights value", 1)
    elif kind == "project":
        o = _common(record, kind, {"repository", "default_branch", "integration_branch", "task_branch_pattern", "external_branch_patterns", "publication_policy", "source_policy", "allowed_paths", "gate_commands", "eligible_hosts", "eligible_pools", "status"}, {"repository", "default_branch", "integration_branch", "task_branch_pattern", "external_branch_patterns", "publication_policy", "source_policy", "allowed_paths", "gate_commands", "eligible_hosts", "eligible_pools", "status"})
        for name in ("repository", "default_branch", "integration_branch", "task_branch_pattern", "publication_policy", "source_policy", "status"): _str(o[name], f"project.{name}")
        _strings(o["external_branch_patterns"], "project.external_branch_patterns"); _workspace_paths(o["allowed_paths"], "project.allowed_paths"); _strings(o["gate_commands"], "project.gate_commands"); _refs(o["eligible_hosts"], "project.eligible_hosts"); _refs(o["eligible_pools"], "project.eligible_pools")
        if o["publication_policy"] != "verified-integration-only" or o["source_policy"] != "exact-sha": raise ContractError("project publication/source policy is not fail-closed")
    else:  # assignment
        o = _common(record, kind, {"task_id", "project_id", "source_repository", "source_branch", "source_sha", "seed_manifest_digest", "engine_id", "provider_id", "capacity_pool_id", "model_id", "model_parameters", "host_id", "sandbox_profile_id", "network_profile", "allowed_paths", "gate_digest", "publication_policy", "created_at", "assignment_digest"}, {"task_id", "project_id", "source_repository", "source_branch", "source_sha", "seed_manifest_digest", "engine_id", "provider_id", "capacity_pool_id", "model_id", "model_parameters", "host_id", "sandbox_profile_id", "network_profile", "allowed_paths", "gate_digest", "publication_policy", "created_at", "assignment_digest"})
        for name in ("task_id", "project_id", "engine_id", "provider_id", "capacity_pool_id", "model_id", "host_id", "sandbox_profile_id"): _str(o[name], f"assignment.{name}", IDENTIFIER)
        _str(o["source_sha"], "assignment.source_sha");
        if not COMMIT.fullmatch(o["source_sha"]): raise ContractError("assignment.source_sha is not a commit SHA")
        for name in ("seed_manifest_digest", "gate_digest", "assignment_digest"): _str(o[name], f"assignment.{name}", SHA256)
        _str(o["publication_policy"], "assignment.publication_policy")
        if o["publication_policy"] != "verified-integration-only": raise ContractError("assignment.publication_policy is not fail-closed")
        _workspace_paths(o["allowed_paths"], "assignment.allowed_paths", nonempty=True); _str(o["source_repository"], "assignment.source_repository"); _str(o["source_branch"], "assignment.source_branch"); _str(o["network_profile"], "assignment.network_profile"); _str(o["created_at"], "assignment.created_at")
        _model_parameters(o["model_parameters"], "assignment.model_parameters")
        if o["assignment_digest"] != digest({key: value for key, value in o.items() if key != "assignment_digest"}):
            raise ContractError("assignment_digest does not match immutable assignment", "digest-mismatch")
    return record


def load_registry(path: Path | str, expected_kind: str | None = None, *, root: Path | None = None) -> list[dict[str, Any]]:
    """Load a v2 collection (or one-record file), validating every entry."""
    safe_path = _secure_file(path, root=root)
    try:
        text = safe_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"cannot read registry {path}: {exc}", "unavailable") from exc
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractError(f"registry {path} is not valid JSON: {exc}", "malformed-registry") from exc
    wrapper_kind: str | None = None
    if isinstance(raw, dict) and "entries" in raw:
        allowed = {"schema_version", "registry", "entries"}
        _obj(raw, "registry", allowed, allowed)
        if raw["schema_version"] != V2_VERSION: raise ContractError("registry schema_version is unsupported", "unsupported-version")
        wrapper_kind = raw["registry"]
        if expected_kind and wrapper_kind != expected_kind: raise ContractError("registry kind mismatch")
        entries = raw["entries"]
    else: entries = [raw]
    if not isinstance(entries, list): raise ContractError("registry.entries must be a list")
    if not entries: raise ContractError("registry is empty", "empty-registry")
    result = [validate_record(x) for x in entries]
    required_kind = expected_kind or wrapper_kind
    if required_kind and any(item["kind"] != required_kind for item in result):
        raise ContractError("record kind does not match registry")
    ids = [x["id"] for x in result]
    if len(set(ids)) != len(ids): raise ContractError("registry has duplicate ids", "duplicate-id")
    return result


def validate_registry(records: Any, expected_kind: str | None = None) -> list[dict[str, Any]]:
    """Validate an already decoded collection without touching the filesystem."""
    wrapper_kind: str | None = None
    if isinstance(records, Mapping) and "entries" in records:
        _obj(records, "registry", {"schema_version", "registry", "entries"}, {"schema_version", "registry", "entries"})
        if records["schema_version"] != V2_VERSION:
            raise ContractError("registry schema_version is unsupported", "unsupported-version")
        if records["registry"] not in REGISTRY_KINDS:
            raise ContractError("registry kind is unknown", "unknown-kind")
        wrapper_kind = records["registry"]
        if expected_kind and wrapper_kind != expected_kind:
            raise ContractError("registry kind mismatch")
        records = records.get("entries")
    if not isinstance(records, list):
        raise ContractError("registry entries must be a list")
    if not records:
        raise ContractError("registry is empty", "empty-registry")
    result = [validate_record(item) for item in records]
    required_kind = expected_kind or wrapper_kind
    if required_kind and any(item["kind"] != required_kind for item in result):
        raise ContractError("record kind does not match registry")
    if len({item["id"] for item in result}) != len(result):
        raise ContractError("registry has duplicate ids", "duplicate-id")
    return result


def load_config(config_dir: Path | str) -> dict[str, list[dict[str, Any]]]:
    base = Path(config_dir)
    try:
        attrs = getattr(base.absolute().stat(), "st_file_attributes", 0)
    except OSError as exc:
        raise ContractError(f"config root is unavailable: {config_dir}", "unavailable") from exc
    if base.is_symlink() or attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
        raise ContractError("config root must not be a symlink/reparse path", "unsafe-path")
    try:
        base = base.resolve(strict=True)
    except OSError as exc:
        raise ContractError(f"config root is unavailable: {config_dir}", "unavailable") from exc
    if not base.is_dir() or base.is_symlink():
        raise ContractError("config root must be a real directory", "unsafe-path")
    directory_names = {
        "capacity_pool": "capacity-pools", "sandbox_profile": "sandbox-profiles",
        "routing_policy": "routing-policies", "execution_profile": "execution-profiles",
        "assignment": "assignments",
    }
    expected_directories = {directory_names.get(kind, kind + "s") for kind in REGISTRY_KINDS if kind != "assignment"} | {"assignments"}
    expected_root_files = {"README.md"}
    for child in base.iterdir():
        if child.is_dir() and child.name not in expected_directories:
            raise ContractError(f"unknown config directory: {child.name}", "unknown-field")
        if not child.is_dir() and child.name not in expected_root_files:
            raise ContractError(f"unknown config root file: {child.name}", "unknown-field")
    result: dict[str, list[dict[str, Any]]] = {}
    for kind in REGISTRY_KINDS:
        directory_name = directory_names.get(kind, kind + "s")
        directory = base / directory_name
        if kind == "assignment" and not directory.exists():
            continue
        if not directory.is_dir():
            raise ContractError(f"registry directory is missing: {directory}", "unavailable")
        children = list(directory.iterdir())
        if any(child.is_dir() or child.suffix.lower() != ".json" for child in children):
            raise ContractError(f"registry {kind} contains a non-JSON or nested path", "unsafe-path")
        files = sorted(children)
        if not files and kind != "assignment":
            raise ContractError(f"registry {kind} is empty", "empty-registry")
        result[kind] = []
        for file in files: result[kind].extend(load_registry(_secure_file(file, root=base), kind))
    return validate_config(result)


def validate_config(registries: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Validate every registry before a resolver may inspect a candidate."""
    if not isinstance(registries, Mapping):
        raise ContractError("registries must be an object")
    unknown = set(registries) - REGISTRY_KINDS
    if unknown: raise ContractError(f"unknown registry kinds: {', '.join(sorted(unknown))}", "unknown-kind")
    result: dict[str, list[dict[str, Any]]] = {}
    for kind in sorted(REGISTRY_KINDS):
        if kind == "assignment" and kind not in registries:
            continue
        values = registries.get(kind, [])
        if not isinstance(values, list): raise ContractError(f"registry {kind} must be a list")
        if (kind != "assignment" or kind in registries) and not values: raise ContractError(f"registry {kind} is empty", "empty-registry")
        checked: list[dict[str, Any]] = []
        for value in values:
            record = validate_record(value)
            if record["kind"] != kind: raise ContractError(f"record kind does not match registry {kind}")
            checked.append(record)
        if len({record["id"] for record in checked}) != len(checked):
            raise ContractError(f"registry {kind} has duplicate ids", "duplicate-id")
        if kind == "routing_policy":
            names = [record["policy"] for record in checked]
            if len(set(names)) != len(names):
                raise ContractError("routing policy names are ambiguous", "duplicate-policy")
        result[kind] = checked
    return result


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str: return hashlib.sha256(_canonical(value)).hexdigest()


def _find(items: Iterable[Mapping[str, Any]], item_id: str, kind: str) -> dict[str, Any]:
    found = [dict(x) for x in items if x.get("id") == item_id]
    if len(found) != 1: raise ContractError(f"{kind} {item_id!r} is not uniquely registered", "unknown-reference")
    return found[0]


def _paths_within(paths: Iterable[str], roots: Iterable[str]) -> bool:
    """Check canonical workspace paths with segment-aware prefix semantics."""
    canonical_roots = tuple(root.rstrip("/") for root in roots)
    return all(any(path == root or path.startswith(root + "/") for root in canonical_roots) for path in paths)


@dataclass(frozen=True)
class Resolution:
    assignment: dict[str, Any] | None
    trace: tuple[dict[str, Any], ...]
    status: str


def resolve_assignment(task: Mapping[str, Any], registries: Mapping[str, list[dict[str, Any]]], *, policy: str | None = None) -> Resolution:
    """Resolve a task without side effects.  Every candidate has a deterministic trace."""
    if not isinstance(task, Mapping): raise ContractError("task must be an object")
    _no_secrets(task, "task")
    registries = validate_config(registries)
    if "allow_metered" in task or "on_demand" in task:
        raise ContractError("task cannot authorize metered or on-demand execution", "policy-unauthorized")
    unknown_task_fields = set(task) - TASK_FIELDS
    if unknown_task_fields:
        raise ContractError(f"task has unknown fields: {', '.join(sorted(unknown_task_fields))}", "unknown-field")
    for name in ("task_id", "project_id", "source_repository", "source_branch", "source_sha", "seed_manifest_digest", "gate_digest", "allowed_paths", "role", "requirements", "execution_profile"):
        if name not in task: raise ContractError(f"task missing required field {name}")
    _str(task["task_id"], "task.task_id", IDENTIFIER); _str(task["project_id"], "task.project_id", IDENTIFIER); _str(task["source_repository"], "task.source_repository"); _str(task["source_branch"], "task.source_branch"); _str(task["source_sha"], "task.source_sha"); _str(task["seed_manifest_digest"], "task.seed_manifest_digest", SHA256); _str(task["gate_digest"], "task.gate_digest", SHA256); _workspace_paths(task["allowed_paths"], "task.allowed_paths", nonempty=True); _str(task["role"], "task.role")
    if task["role"] not in ROLES: raise ContractError("task.role is unknown role")
    requirements = task["requirements"]
    if not isinstance(requirements, Mapping): raise ContractError("task.requirements must be an object")
    unknown_requirement_fields = set(requirements) - REQUIREMENT_FIELDS
    if unknown_requirement_fields:
        raise ContractError(f"task.requirements has unknown fields: {', '.join(sorted(unknown_requirement_fields))}", "unknown-field")
    _model_parameters(task.get("model_parameters", {}), "task.model_parameters")
    for field in ("capabilities", "engine_capabilities", "model_capabilities", "host_capabilities", "sandbox_capabilities", "billing"):
        if field in requirements: _strings(requirements[field], f"task.requirements.{field}")
    if "billing" in requirements and not set(requirements["billing"]) <= BILLING_BASES:
        raise ContractError("task.requirements.billing contains an unknown billing basis")
    for field in ("operating_system", "isolation", "data_class", "network_profile"):
        if field in requirements: _str(requirements[field], f"task.requirements.{field}")
    if "max_cost_usd" in requirements:
        value = requirements["max_cost_usd"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or not math.isfinite(value):
            raise ContractError("task.requirements.max_cost_usd must be a finite number >= 0")
    _str(task["execution_profile"], "task.execution_profile", IDENTIFIER)
    if "preferences" in task:
        preferences = _obj(task["preferences"], "task.preferences", {"implementer_family", "verifier_family"}, set())
        for field, value in preferences.items(): _str(value, f"task.preferences.{field}")
    if "manual_pin" in task:
        pin = task["manual_pin"]
        _obj(pin, "task.manual_pin", {"engine", "provider", "capacity_pool", "model", "host", "sandbox_profile"}, {"engine", "provider", "capacity_pool", "model", "host", "sandbox_profile"})
        for field, value in pin.items(): _str(value, f"task.manual_pin.{field}", IDENTIFIER)
    if "routing_policy" in task:
        raise ContractError("task cannot select routing policy", "policy-unauthorized")
    policy_records = registries.get("routing_policy", [])
    if not policy_records: raise ContractError("routing policy registry is empty", "empty-registry")
    policy_record = None
    if policy is not None:
        policy_record = next((item for item in policy_records if item["id"] == policy or item["policy"] == policy), None)
        if policy_record is None: raise ContractError(f"unknown routing policy {policy!r}", "unknown-policy")
    else:
        policy_record = sorted(policy_records, key=lambda item: item["id"])[0]
    policy = policy_record["policy"]
    if policy_record.get("role") != task["role"]:
        raise ContractError("routing policy is not approved for task role", "policy-role-mismatch")
    project = _find(registries.get("project", []), str(task["project_id"]), "project")
    if not _paths_within(task["allowed_paths"], project["allowed_paths"]):
        raise ContractError("task.allowed_paths exceed project.allowed_paths", "path-not-authorized")
    if task["source_repository"] != project["repository"]:
        raise ContractError("task.source_repository does not match project.repository", "source-repository-mismatch")
    profile_matches = [dict(item) for item in registries.get("execution_profile", []) if item.get("id") == task["execution_profile"]]
    if len(profile_matches) != 1:
        raise ContractError(f"execution_profile {task['execution_profile']!r} is not uniquely registered", "unknown-profile")
    profile = profile_matches[0]
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
            if task["role"] not in profile.get("roles", []): reasons.append("profile-role-not-allowed")
            for field, value in (("engine_ids", e["id"]), ("provider_ids", p["id"]), ("capacity_pool_ids", pool["id"]), ("model_ids", m["id"]), ("host_ids", h["id"]), ("sandbox_profile_ids", s["id"])):
                if value not in profile.get(field, []): reasons.append(f"profile-{field}-not-allowed")
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
            if h.get("operating_system") != s.get("operating_system"): reasons.append("host-sandbox-os-mismatch")
            if s.get("controller_visibility") != APPROVED_CONTROLLER_VISIBILITY: reasons.append("sandbox-controller-boundary-invalid")
            if s.get("trust_class") not in TRUST_COMPATIBILITY.get(h.get("trust_class"), set()): reasons.append("trust-class-incompatible")
            if set(e.get("compatible_host_capabilities", [])) - set(h.get("capabilities", [])): reasons.append("host-capability-incompatible")
            if p.get("egress_profile") not in h.get("network_profiles", []) or p.get("egress_profile") not in s.get("network_profiles", []): reasons.append("provider-egress-profile-unavailable")
            endpoints = set(p.get("endpoints", []))
            if endpoints - set(h.get("network_endpoints", [])): reasons.append("provider-endpoint-unavailable-on-host")
            if endpoints - set(s.get("network_endpoints", [])): reasons.append("provider-endpoint-unavailable-in-sandbox")
            if requirements.get("operating_system") and (h.get("operating_system") != requirements["operating_system"] or s.get("operating_system") != requirements["operating_system"]): reasons.append("operating-system-mismatch")
            required_capabilities = requirements.get("capabilities", [])
            for component, record in (("engine", e), ("model", m), ("host", h), ("sandbox", s)):
                missing = sorted(set(required_capabilities) - set(record.get("capabilities", [])))
                if missing: reasons.append(f"missing-{component}-capabilities:" + ",".join(missing))
            for field, component in (("engine_capabilities", e), ("model_capabilities", m), ("host_capabilities", h), ("sandbox_capabilities", s)):
                missing = sorted(set(requirements.get(field, [])) - set(component.get("capabilities", [])))
                if missing: reasons.append(f"missing-{field}:" + ",".join(missing))
            if requirements.get("isolation") and s.get("isolation") != requirements["isolation"]: reasons.append("isolation-mismatch")
            if requirements.get("data_class") and (requirements["data_class"] not in m.get("data_classes", []) or requirements["data_class"] != p.get("data_classification")): reasons.append("data-class-not-allowed")
            if requirements.get("billing") and pool.get("billing_basis") not in requirements["billing"]: reasons.append("billing-not-allowed")
            requested_network = requirements.get("network_profile")
            provider_network = p.get("egress_profile")
            if requested_network and (requested_network != provider_network or requested_network not in h.get("network_profiles", []) or requested_network not in s.get("network_profiles", [])): reasons.append("network-profile-mismatch")
            if provider_network not in profile.get("network_profiles", []): reasons.append("profile-network-profile-not-allowed")
            if requested_network and (requested_network not in profile.get("network_profiles", [])): reasons.append("profile-network-profile-not-allowed")
            if not requested_network and (provider_network not in h.get("network_profiles", []) or provider_network not in s.get("network_profiles", [])): reasons.append("network-profile-mismatch")
            if policy == "manual-pin":
                pin = task.get("manual_pin")
                if not isinstance(pin, Mapping): reasons.append("manual-pin-missing")
                elif any(pin.get(k) != c["id"] for k, c in (("engine", e), ("provider", p), ("capacity_pool", pool), ("model", m), ("host", h), ("sandbox_profile", s))): reasons.append("manual-pin-mismatch")
            if not project.get("publication_policy") == "verified-integration-only": reasons.append("publication-policy-invalid")
            if pool.get("billing_basis") == "metered":
                if not policy_record.get("allow_metered", False): reasons.append("metered-not-approved")
                if policy_record.get("fallback_policy") not in {"approved", "allow-approved"}: reasons.append("routing-fallback-not-approved")
                if pool.get("fallback_policy") not in {"approved", "allow-approved"}: reasons.append("pool-fallback-not-approved")
            item = {"candidate": cid, "accepted": not reasons, "rejections": reasons}
            trace.append(item)
            if not reasons: candidates.append({"engine": e, "provider": p, "pool": pool, "model": m, "host": h, "sandbox": s})
    if not candidates: return Resolution(None, tuple(trace), "deferred")
    def score(c: dict[str, Any]) -> tuple[Any, ...]:
        e, p, pool, m, h, s = c["engine"], c["provider"], c["pool"], c["model"], c["host"], c["sandbox"]
        billing = {"local": 0, "included": 1, "weekly-included": 1, "human": 2, "metered": 3}.get(pool.get("billing_basis"), 9)
        cost = {"local": 0, "included": 1, "low": 2, "medium": 3, "high": 4, "metered": 5}.get(m.get("cost_class"), 9)
        speed = {"fast": 0, "medium": 1, "slow": 2}.get(m.get("speed_class"), 9)
        reasoning = {"frontier": 0, "strong": 1, "standard": 2}.get(m.get("reasoning_class"), 9)
        pin = task.get("manual_pin", {})
        features: dict[str, Any] = {
            "billing_basis": billing, "cost_class": cost, "pool_id": pool["id"], "provider_id": p["id"], "capacity_pool_id": pool["id"],
            "model_id": m["id"], "engine_id": e["id"], "host_id": h["id"],
            "sandbox_profile_id": s["id"], "speed_class": speed, "reasoning_class": reasoning,
            "manual_pin": 0 if isinstance(pin, Mapping) and all(pin.get(k) == c[k]["id"] for k in ("engine", "provider", "capacity_pool", "model", "host", "sandbox_profile")) else 1,
        }
        ordered = tuple(features[field] for field in policy_record["candidate_order"])
        # Weighted rotation uses a stable task/capacity hash; the declared
        # candidate_order contributes to the hash seed, while weights remain
        # the primary choice dimension and cannot be shadowed by that order.
        if policy == "weighted-rotation":
            weights = policy_record.get("weights", {})
            weight = next((weights[item_id] for item_id in (pool["id"], m["id"], e["id"], p["id"], h["id"], s["id"]) if item_id in weights), 1)
            rotation = (int(digest(task["task_id"] + ":" + json.dumps(ordered, separators=(",", ":")))[0:8], 16) / weight,)
            return rotation + ordered + (e["id"], p["id"], pool["id"], m["id"], h["id"], s["id"])
        else:
            rotation = ()
        return ordered + rotation + (e["id"], p["id"], pool["id"], m["id"], h["id"], s["id"])
    chosen = sorted(candidates, key=score)[0]
    selected_network = requirements.get("network_profile") or chosen["provider"]["egress_profile"]
    assignment = {"schema_version": 2, "kind": "assignment", "id": "pending", "task_id": task["task_id"], "project_id": task["project_id"], "source_repository": task["source_repository"], "source_branch": task["source_branch"], "source_sha": task["source_sha"], "seed_manifest_digest": task["seed_manifest_digest"], "engine_id": chosen["engine"]["id"], "provider_id": chosen["provider"]["id"], "capacity_pool_id": chosen["pool"]["id"], "model_id": chosen["model"]["id"], "model_parameters": dict(task.get("model_parameters", {})), "host_id": chosen["host"]["id"], "sandbox_profile_id": chosen["sandbox"]["id"], "network_profile": selected_network, "allowed_paths": list(task["allowed_paths"]), "gate_digest": task["gate_digest"], "publication_policy": project["publication_policy"], "created_at": str(task.get("created_at", "dry-run"))}
    assignment["id"] = "assignment-" + digest({key: value for key, value in assignment.items() if key != "id"})[:52]
    assignment["assignment_digest"] = digest({k: v for k, v in assignment.items() if k != "assignment_digest"})
    validate_record(assignment)
    return Resolution(assignment, tuple(trace), "assigned")


def read_v1_manifest(data: Mapping[str, Any]) -> dict[str, Any]:
    """Compatibility reader for scripts/engines/*.json (never mutates it)."""
    if not isinstance(data, Mapping) or data.get("schema_version") != 1: raise ContractError("unsupported v1 engine manifest", "unsupported-version")
    for field in ("name", "executable", "argv", "roles", "billing", "network", "env_passthrough"):
        if field not in data: raise ContractError(f"v1 engine manifest missing {field}")
    if not isinstance(data["argv"], list) or not data["argv"] or not isinstance(data["roles"], list) or not data["roles"]: raise ContractError("v1 engine manifest has invalid launch fields")
    billing = data["billing"] if isinstance(data["billing"], Mapping) else {}
    network = data["network"] if isinstance(data["network"], Mapping) else {}
    return {"schema_version": 1, "kind": "engine", "id": data["name"], "description": data.get("description", ""), "runtime_layout": {"kind": "bare", "executable": data["executable"], "runtime_paths": [], "read_only_mounts": []}, "argv_template": list(data["argv"]), "structured_output": False, "roles": list(data["roles"]), "capabilities": [], "health_probe": data.get("availability_probe"), "cancellation": {"supported": False, "protocol": "legacy"}, "resume": {"supported": False, "protocol": "legacy"}, "usage_receipt": {"supported": False, "protocol": "legacy"}, "network_capabilities": list(network.get("endpoints", [])), "compatible_sandbox_profiles": ["strict-linux"], "compatible_host_capabilities": [], "legacy": {"model": data.get("model"), "billing": billing, "env_passthrough": list(data["env_passthrough"]), "concurrency_cap": data.get("concurrency_cap")}}


read_v1_engine_manifest = read_v1_manifest


def read_v1_portfolio_row(row: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(row, str):
        cols = row.rstrip("\r\n").split("\t")
        if len(cols) != 8 or cols[0].startswith("#"): raise ContractError("invalid v1 portfolio row")
        row = dict(zip(("id", "repository", "remote", "default_branch", "credential_ref", "roadmap", "topic", "status"), cols))
    if not isinstance(row, Mapping): raise ContractError("invalid v1 portfolio row")
    result = {"schema_version": 1, "kind": "project", "id": row.get("id", row.get("project")), "repository": row.get("repository", row.get("path")), "remote": row.get("remote"), "default_branch": row.get("default_branch", row.get("branch")), "credential_ref": row.get("credential_ref", row.get("sshkey")), "roadmap": row.get("roadmap"), "topic": row.get("topic"), "status": row.get("status")}
    for field in ("id", "repository", "remote", "default_branch", "credential_ref", "status"):
        _str(result[field], f"v1 portfolio.{field}")
    return result


def read_v1_project_config(data: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(data, Mapping) or data.get("schema_version") != 1: raise ContractError("unsupported v1 project config", "unsupported-version")
    for field in ("id", "repo", "default_branch", "deploy_key_ref", "status"):
        _str(data.get(field), f"v1 project.{field}")
    return {"schema_version": 1, "kind": "project", "id": data["id"], "repository": data["repo"], "remote": data.get("remote"), "default_branch": data["default_branch"], "credential_ref": data["deploy_key_ref"], "allowed_paths": list(data.get("allowed_paths", [])), "charter": data.get("charter"), "topic": data.get("topic"), "pilot_id": data.get("pilot_id"), "activation_gate": data.get("activation_gate"), "notification_targets": list(data.get("notification_targets", [])), "goal_source": data.get("goal_source"), "status": data["status"]}


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
    for field in ("id", "goal_id", "acceptance", "worker_class", "status"):
        _str(data.get(field), f"v1 task.{field}")
    gate_contract = data.get("gate_contract") if isinstance(data.get("gate_contract"), Mapping) else {}
    return {"schema_version": 1, "kind": "task", "task_id": data["id"], "goal_id": data["goal_id"], "project_id": data.get("project_id"), "dependencies": list(data.get("dependencies", [])), "source_repository": data.get("repo"), "source_sha": data.get("base_commit", data.get("source_sha")), "role": "implementer", "engine": data.get("engine"), "model_alias": data.get("model_alias"), "worker_class": data["worker_class"], "acceptance": data["acceptance"], "allowed_paths": list(data.get("allowed_paths", [])), "non_goals": list(data.get("non_goals", [])), "gate_digest": gate_contract.get("acceptance_sha256"), "status": data["status"]}


def read_v1_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(data, Mapping) or data.get("schema_version") != 1: raise ContractError("unsupported v1 evidence", "unsupported-version")
    for field in ("id", "task_id", "status"):
        _str(data.get(field), f"v1 evidence.{field}")
    return {"schema_version": 1, "kind": "evidence", "run_id": data["id"], "task_id": data["task_id"], "source_sha": data.get("base_commit"), "engine_id": data.get("engine", data.get("worker")), "worker": data.get("worker"), "worktree": data.get("worktree"), "role": data.get("role"), "model_alias": data.get("model_alias"), "network_policy": data.get("network_policy"), "lease_expires": data.get("lease_expires"), "deadline": data.get("deadline"), "usage": data.get("usage"), "result": data.get("result"), "status": data["status"]}


read_v1_run_evidence = read_v1_evidence
dry_resolve_assignment = resolve_assignment

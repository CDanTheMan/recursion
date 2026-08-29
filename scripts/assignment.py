#!/usr/bin/env python3
"""Immutable run assignments (Phase 3, D-016 execution fabric).

Resolves and durably persists one immutable "assignment" record per launched arm
(implementer or verifier) BEFORE the worker starts: exact source identity, exact
engine/provider/capacity-pool/model, exact host/sandbox/network placement, and the
gate/publication contract the arm is bound to. The digest of that record is the
identity every downstream artifact (lease, run evidence, usage ledger row, scorecard
bucket, and returned-result validation) must carry from here on, instead of each
consumer independently re-deriving engine/provider facts from a MUTABLE task header
at report time (docs/audits/recursion-v2-infrastructure-audit-2026-08-28.md, "Missing
execution-fabric contracts").

An assignment is content-addressed and write-once: resolving the identical inputs
twice returns the identical digest and is a no-op; resolving with ANY different input
produces a different digest and a new, separate record. Nothing here ever rewrites a
persisted assignment file.

This module also loads capacity-pool manifests (scripts/capacity-pools/<id>.json,
declarative JSON, same house style as scripts/engines/<name>.json /
resolve-engine.py) — the minimal account/subscription/quota registry D-016 requires
for pool attribution and quota-period reconciliation. It is deliberately narrow: the
full config/ registry layer (engine, provider, model, host, sandbox-profile, routing-
policy, project registries) described in docs/plans/recursion-v2-execution-fabric.md
Phase 1 is NOT built here. Referencing capacity_pool remains optional; a legacy caller
that never names one gets capacity_pool=null and is unaffected.

Exit codes: 0 ok; 2 invalid arguments, malformed manifest, or content-address
collision (an existing assignment file disagrees with the freshly computed content —
this must never happen and is refused rather than overwritten).
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import hashlib
import json
import math
import os
import re
import stat
import sys
import time
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine_contract  # noqa: E402  (shared engine/alias contract helpers, D-015)
import jsonl_durable  # noqa: E402  (pinned assignment index transaction)

PROG = "assignment"
SCHEMA_VERSION = 1
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MAX_INPUT_BYTES = 8 * 1024 * 1024

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_ROOT = ROOT / "state" / "assignments"
DEFAULT_CAPACITY_POOL_DIR = Path(__file__).resolve().parent / "capacity-pools"

IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
SHA_RE = re.compile(r"[0-9a-f]{40,64}")
DIGEST_RE = re.compile(r"[0-9a-f]{64}")
PROVIDER_RE = re.compile(r"[a-z][a-z0-9-]{1,63}")
SLUG_RE = re.compile(r"[a-z][a-z0-9-]{1,63}")
MODEL_PARAM_KEY_RE = re.compile(r"[a-z][a-z0-9_]{0,63}")

ROLES = frozenset({"implementer", "verifier"})
NETWORK_PROFILES = frozenset({"provider-only", "none"})
# docs/plans/recursion-v2-execution-fabric.md "Sandbox profile" — the initial profile set.
SANDBOX_PROFILES = frozenset({
    "strict-linux", "workspace-linux", "vendor-cloud", "remote-linux",
    "windows-interactive", "trusted-interactive", "account-shared-supervisor",
})

CAPACITY_POOL_TOP_KEYS = {
    "schema_version", "id", "kind", "billing_basis", "provider", "quota",
    "on_demand", "roles", "host_id", "fallback_policy",
}
CAPACITY_POOL_KINDS = frozenset({"subscription", "supervisory", "local", "human"})
CAPACITY_POOL_BILLING_BASES = frozenset({
    "flat-subscription", "metered", "local", "weekly-included", "human",
})
QUOTA_KEYS = {"period", "source", "limit", "unit"}
QUOTA_PERIODS = frozenset({"daily", "weekly", "monthly"})
QUOTA_SOURCES = frozenset({"observed", "declared"})
FALLBACK_POLICIES = frozenset({"defer", "refuse"})
BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]{1,255}$")
ASSIGNMENT_FIELDS = frozenset({
    "schema_version", "task_id", "project_id", "role", "source_repository", "source_branch",
    "source_sha", "source_evidence", "seed_manifest_digest", "engine", "provider",
    "capacity_pool", "billing_basis", "metered_approved", "model", "model_parameters", "host",
    "sandbox_profile", "network_profile", "allowed_paths", "gate_digest", "publication_policy",
    "default_branch", "integration_branch", "created_at", "assignment_digest",
})
# This is the exact projection embedded in run evidence.  Keep it derived from the
# assignment schema so a newly authoritative attribution field cannot silently be omitted
# by one consumer (Phase 3, D-016).
ASSIGNMENT_PROJECTION_FIELDS = tuple(sorted(ASSIGNMENT_FIELDS))


class AssignmentError(Exception):
    """Invalid inputs, a malformed capacity-pool manifest, or a persistence conflict."""


class CapacityPoolNotFound(AssignmentError):
    """The optional default authority directory has no named pool."""


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def now_iso() -> str:
    return time.strftime(TS_FORMAT, time.gmtime())


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and value.strip() != "" and value == value.strip()


def _split_paths(value: str) -> list[str]:
    if not isinstance(value, str):
        raise AssignmentError("allowed_paths must be a comma-separated string")
    return _normalize_allowed_paths(
        [item.strip() for item in value.split(",") if item.strip()]
    )


def _normalize_allowed_paths(values: object) -> list[str]:
    """Return canonical repository-relative paths or refuse the whole assignment.

    Assignment paths are authority-bearing scope, so platform-dependent aliases,
    absolute paths, and parent traversal must never survive into the digest.
    """
    if not isinstance(values, list) or not values:
        raise AssignmentError("allowed_paths must be a nonempty list")
    normalized: set[str] = set()
    for raw in values:
        if not _nonempty(raw) or "\x00" in raw:
            raise AssignmentError("allowed_paths entries must be nonempty canonical strings")
        if "\\" in raw:
            raise AssignmentError(f"allowed_paths entry contains a backslash: {raw!r}")
        candidate = raw
        if candidate.startswith("/") or re.match(r"^[A-Za-z]:", candidate):
            raise AssignmentError(f"allowed_paths entry must be repository-relative: {raw!r}")
        parts = PurePosixPath(candidate).parts
        if not parts or any(part in {".", ".."} for part in parts):
            raise AssignmentError(f"allowed_paths entry escapes repository scope: {raw!r}")
        canonical = PurePosixPath(*parts).as_posix()
        if canonical != raw or canonical == ".." or canonical.startswith("../"):
            raise AssignmentError(f"allowed_paths entry escapes repository scope: {raw!r}")
        normalized.add(canonical)
    return sorted(normalized)


# --- capacity pool manifests --------------------------------------------------------------

def capacity_pool_dir() -> Path:
    override = os.environ.get("RECURSION_CAPACITY_POOL_DIR", "").strip()
    return Path(override) if override else DEFAULT_CAPACITY_POOL_DIR


def _require_keys(obj: object, keys: set, where: str) -> dict:
    if not isinstance(obj, dict):
        raise AssignmentError(f"{where} must be a JSON object")
    missing = keys - obj.keys()
    if missing:
        raise AssignmentError(f"{where} missing required key(s): {', '.join(sorted(missing))}")
    return obj


def validate_capacity_pool(data: object, pool_id: str) -> dict:
    if not isinstance(pool_id, str):
        raise AssignmentError("capacity-pool id must be a string")
    obj = _require_keys(data, {"schema_version", "id", "kind", "billing_basis", "provider", "quota", "on_demand"}, "capacity-pool manifest")
    if not all(isinstance(key, str) for key in obj):
        raise AssignmentError("capacity-pool manifest keys must be strings")
    extra = obj.keys() - CAPACITY_POOL_TOP_KEYS
    if extra:
        raise AssignmentError(f"capacity-pool manifest has unknown key(s): {', '.join(sorted(extra))}")
    if not isinstance(obj.get("schema_version"), int) or isinstance(obj.get("schema_version"), bool) \
            or obj.get("schema_version") != 1:
        raise AssignmentError("capacity-pool manifest schema_version must be 1")
    if obj.get("id") != pool_id:
        raise AssignmentError(f"capacity-pool id {obj.get('id')!r} does not match filename stem {pool_id!r}")
    if not IDENTIFIER_RE.fullmatch(pool_id):
        raise AssignmentError(f"invalid capacity-pool id {pool_id!r}")
    if not isinstance(obj.get("kind"), str) or obj.get("kind") not in CAPACITY_POOL_KINDS:
        raise AssignmentError(f"capacity-pool kind must be one of {sorted(CAPACITY_POOL_KINDS)}")
    if not isinstance(obj.get("billing_basis"), str) \
            or obj.get("billing_basis") not in CAPACITY_POOL_BILLING_BASES:
        raise AssignmentError(f"capacity-pool billing_basis must be one of {sorted(CAPACITY_POOL_BILLING_BASES)}")
    if not _nonempty(obj.get("provider")) or not PROVIDER_RE.fullmatch(obj["provider"]):
        raise AssignmentError("capacity-pool provider must be a nonempty lowercase-kebab string")
    quota = _require_keys(obj.get("quota"), {"period", "source"}, "capacity-pool quota")
    if not all(isinstance(key, str) for key in quota):
        raise AssignmentError("capacity-pool quota keys must be strings")
    extra_quota = quota.keys() - QUOTA_KEYS
    if extra_quota:
        raise AssignmentError(f"capacity-pool quota has unknown key(s): {', '.join(sorted(extra_quota))}")
    if not isinstance(quota.get("period"), str) or quota.get("period") not in QUOTA_PERIODS:
        raise AssignmentError(f"capacity-pool quota.period must be one of {sorted(QUOTA_PERIODS)}")
    if not isinstance(quota.get("source"), str) or quota.get("source") not in QUOTA_SOURCES:
        raise AssignmentError(f"capacity-pool quota.source must be one of {sorted(QUOTA_SOURCES)}")
    limit = quota.get("limit")
    if limit is not None:
        try:
            valid_limit = (
                isinstance(limit, (int, float)) and not isinstance(limit, bool)
                and math.isfinite(float(limit)) and limit >= 0
            )
        except (OverflowError, ValueError):
            valid_limit = False
        if not valid_limit:
            raise AssignmentError("capacity-pool quota.limit must be null or a non-negative number")
    unit = quota.get("unit")
    if unit is not None and (not isinstance(unit, str) or len(unit) < 1):
        raise AssignmentError("capacity-pool quota.unit must be null or a nonempty string")
    if not isinstance(obj.get("on_demand"), bool):
        raise AssignmentError("capacity-pool on_demand must be a boolean")
    roles = obj.get("roles")
    if roles is not None and (not isinstance(roles, list) or not roles
                              or not all(isinstance(r, str) and len(r) >= 1 for r in roles)):
        raise AssignmentError("capacity-pool roles must be null or a list of nonempty strings")
    host_id = obj.get("host_id")
    if host_id is not None and (not isinstance(host_id, str) or len(host_id) < 1):
        raise AssignmentError("capacity-pool host_id must be null or a nonempty string")
    fallback = obj.get("fallback_policy")
    if fallback is not None and (not isinstance(fallback, str) or fallback not in FALLBACK_POLICIES):
        raise AssignmentError(f"capacity-pool fallback_policy must be null or one of {sorted(FALLBACK_POLICIES)}")
    return obj


def load_capacity_pool(pool_dir: Path, pool_id: str) -> dict:
    if not isinstance(pool_id, str) or not IDENTIFIER_RE.fullmatch(pool_id):
        raise AssignmentError(f"invalid capacity-pool id {pool_id!r}")
    try:
        path = Path(pool_dir) / f"{pool_id}.json"
    except (TypeError, ValueError) as exc:
        raise AssignmentError("capacity-pool directory is not a path") from exc
    try:
        raw_bytes = jsonl_durable.read_durable_bytes(path, max_bytes=MAX_INPUT_BYTES)
        if raw_bytes is None:
            raise CapacityPoolNotFound(f"capacity-pool manifest not found: {path}")
        raw = raw_bytes.decode("utf-8")
    except CapacityPoolNotFound:
        raise
    except (OSError, UnicodeDecodeError, jsonl_durable.JsonlDurabilityError) as exc:
        raise AssignmentError(f"capacity-pool manifest not found: {path} ({exc})") from exc
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError, RecursionError, OverflowError) as exc:
        raise AssignmentError(f"capacity-pool manifest {path} is not valid JSON: {exc}") from exc
    return validate_capacity_pool(data, pool_id)


def engine_contract_attribution(engine: str) -> tuple[str | None, str | None]:
    if engine == "claude":
        return "anthropic-claude-code", "flat-subscription"
    path = Path(os.environ.get("RECURSION_ENGINE_DIR") or Path(__file__).resolve().parent / "engines") / f"{engine}.json"
    try:
        raw = jsonl_durable.read_durable_bytes(path, max_bytes=MAX_INPUT_BYTES)
        if raw is None:
            return None, None
        data = json.loads(raw.decode("utf-8"))
        billing = data.get("billing") if isinstance(data, dict) else None
        if isinstance(billing, dict): return billing.get("provider"), billing.get("basis")
    except (OSError, UnicodeDecodeError, jsonl_durable.JsonlDurabilityError,
            json.JSONDecodeError, TypeError, ValueError, OverflowError, RecursionError):
        pass
    return None, None


def canonical_branch(value: object, field: str = "branch") -> str:
    """Validate a git branch name without allowing platform/path aliases."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise AssignmentError(f"{field} must be a nonempty canonical branch")
    if "\\" in value or "//" in value or "@{" in value or not BRANCH_RE.fullmatch(value):
        raise AssignmentError(f"{field} is not a canonical git branch: {value!r}")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise AssignmentError(f"{field} contains a dot/path alias: {value!r}")
    if value.startswith("/") or value.endswith("/") or value.endswith("."):
        raise AssignmentError(f"{field} is not a canonical git branch: {value!r}")
    return value


def canonical_source_evidence(value: object, repository: str, branch: str, sha: str) -> dict:
    if not isinstance(value, dict):
        raise AssignmentError("source_evidence is required and must be an object")
    required = {"repository", "branch", "sha", "verified"}
    if set(value) not in (required, required | {"schema_version"}):
        raise AssignmentError("source_evidence must contain exactly repository, branch, sha, verified")
    if "schema_version" in value and (
            not isinstance(value.get("schema_version"), int)
            or isinstance(value.get("schema_version"), bool)
            or value.get("schema_version") != 1):
        raise AssignmentError("source_evidence schema_version must be 1")
    if not _nonempty(value.get("repository")):
        raise AssignmentError("source_evidence repository must be a nonempty string")
    evidence_branch = value.get("branch")
    if not isinstance(evidence_branch, str):
        raise AssignmentError("source_evidence branch must be a string")
    canonical_branch(evidence_branch, "source_evidence.branch")
    evidence_sha = value.get("sha")
    if not isinstance(evidence_sha, str) or not SHA_RE.fullmatch(evidence_sha):
        raise AssignmentError("source_evidence sha is invalid")
    if not isinstance(value.get("verified"), bool):
        raise AssignmentError("source_evidence verified must be boolean")
    if value.get("repository") != repository or value.get("branch") != branch or value.get("sha") != sha:
        raise AssignmentError("source_evidence does not match the assigned source")
    if value.get("verified") is not True:
        raise AssignmentError("source_evidence is not verified")
    result = {"repository": repository, "branch": branch, "sha": sha, "verified": True}
    if "schema_version" in value: result = {"schema_version": 1, **result}
    return result


# --- assignment resolution ----------------------------------------------------------------

def canonical_digest(value: dict) -> str:
    if not isinstance(value, dict):
        raise AssignmentError("assignment digest input must be an object")
    payload = {key: item for key, item in value.items() if key != "assignment_digest"}
    try:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeEncodeError) as exc:
        raise AssignmentError("assignment digest input is not serializable") from exc
    return hashlib.sha256(encoded).hexdigest()


def resolve_assignment(
    *, task_id: str, project_id: str, role: str, source_repository: str, source_branch: str,
    source_sha: str, engine: str, provider: str, host: str, sandbox_profile: str,
    network_profile: str, allowed_paths: list[str], publication_policy: str,
    seed_manifest_digest: str | None = None, capacity_pool: str | None = None,
    model: str | None = None, model_parameters: dict | None = None,
    gate_digest: str | None = None, capacity_pool_dir: Path | None = None,
    source_evidence: dict | None = None, billing_basis: str | None = None,
    metered_approved: bool = False, default_branch: str = "main",
    integration_branch: str = "recursion/integration",
    created_at: str | None = None,
) -> dict:
    if not isinstance(task_id, str) or not IDENTIFIER_RE.fullmatch(task_id):
        raise AssignmentError(f"invalid task_id {task_id!r}")
    if not isinstance(project_id, str) or not IDENTIFIER_RE.fullmatch(project_id):
        raise AssignmentError(f"invalid project_id {project_id!r}")
    if not isinstance(role, str) or role not in ROLES:
        raise AssignmentError(f"role must be one of {sorted(ROLES)}")
    if not _nonempty(source_repository):
        raise AssignmentError("source_repository must be a nonempty string")
    source_branch = canonical_branch(source_branch, "source_branch")
    if not isinstance(source_sha, str) or not SHA_RE.fullmatch(source_sha):
        raise AssignmentError(f"invalid source_sha {source_sha!r}")
    if seed_manifest_digest is not None and (
            not isinstance(seed_manifest_digest, str) or not DIGEST_RE.fullmatch(seed_manifest_digest)):
        raise AssignmentError(f"invalid seed_manifest_digest {seed_manifest_digest!r}")
    if not isinstance(engine, str) or not (
            engine in engine_contract.BUILTIN_ENGINES or engine_contract.plugin_engine_name_ok(engine)):
        raise AssignmentError(f"invalid engine {engine!r}")
    if not _nonempty(provider) or not PROVIDER_RE.fullmatch(provider):
        raise AssignmentError(f"invalid provider {provider!r}")
    pool = None
    if capacity_pool is not None:
        if not isinstance(capacity_pool, str) or not IDENTIFIER_RE.fullmatch(capacity_pool):
            raise AssignmentError(f"invalid capacity_pool {capacity_pool!r}")
        # Referencing a pool must resolve; a caller that names one is asserting it is real.
        pool = load_capacity_pool(capacity_pool_dir or capacity_pool_dir_default(), capacity_pool)
    if model is not None and not _nonempty(model):
        raise AssignmentError("model must be null or a nonempty string")
    if model_parameters is not None and not isinstance(model_parameters, dict):
        raise AssignmentError("model_parameters must be an object")
    params = dict(model_parameters) if model_parameters is not None else {}
    for key, item in params.items():
        if not isinstance(key, str) or not MODEL_PARAM_KEY_RE.fullmatch(key) \
                or not isinstance(item, str):
            raise AssignmentError(f"invalid model parameter {key!r}")
    if not _nonempty(host):
        raise AssignmentError("host must be a nonempty string")
    if not isinstance(sandbox_profile, str) or sandbox_profile not in SANDBOX_PROFILES:
        raise AssignmentError(f"sandbox_profile must be one of {sorted(SANDBOX_PROFILES)}")
    if not isinstance(network_profile, str) or network_profile not in NETWORK_PROFILES:
        raise AssignmentError(f"network_profile must be one of {sorted(NETWORK_PROFILES)}")
    normalized_allowed_paths = _normalize_allowed_paths(allowed_paths)
    if gate_digest is not None and (
            not isinstance(gate_digest, str) or not DIGEST_RE.fullmatch(gate_digest)):
        raise AssignmentError(f"invalid gate_digest {gate_digest!r}")
    if not isinstance(publication_policy, str) or not SLUG_RE.fullmatch(publication_policy):
        raise AssignmentError(f"invalid publication_policy {publication_policy!r}")
    default_branch = canonical_branch(default_branch, "default_branch")
    integration_branch = canonical_branch(integration_branch, "integration_branch")
    if default_branch == integration_branch:
        raise AssignmentError("default_branch and integration_branch must differ")
    if source_evidence is None:
        source_evidence = {"repository": source_repository, "branch": source_branch,
                           "sha": source_sha, "verified": True}
    source_evidence = canonical_source_evidence(
        source_evidence, source_repository, source_branch, source_sha)
    if billing_basis is not None and (
            not isinstance(billing_basis, str) or billing_basis not in CAPACITY_POOL_BILLING_BASES):
        raise AssignmentError(f"invalid billing_basis {billing_basis!r}")
    engine_provider, engine_basis = engine_contract_attribution(engine)
    if engine_provider is not None and engine_provider != provider:
        raise AssignmentError("assignment provider does not match engine manifest")
    if billing_basis is not None and engine_basis is not None and billing_basis != engine_basis:
        raise AssignmentError("assignment billing_basis does not match engine manifest")
    if not isinstance(metered_approved, bool):
        raise AssignmentError("metered_approved must be boolean")
    if pool is not None:
        if pool["provider"] != provider:
            raise AssignmentError("capacity pool provider does not match assignment provider")
        if pool.get("roles") is not None and role not in pool["roles"]:
            raise AssignmentError("assignment role is not allowed by capacity pool")
        if pool.get("host_id") is not None and pool["host_id"] != host:
            raise AssignmentError("assignment host does not match capacity pool host")
        pool_basis = pool["billing_basis"]
        if billing_basis is not None and billing_basis != pool_basis:
            raise AssignmentError("assignment billing_basis does not match capacity pool")
        billing_basis = pool_basis
    if billing_basis == "metered" and not metered_approved:
        raise AssignmentError("metered assignment requires explicit approval")

    if created_at is not None and not isinstance(created_at, str):
        raise AssignmentError("created_at must be a canonical UTC timestamp string")
    if created_at is not None:
        try:
            datetime.datetime.strptime(created_at, TS_FORMAT)
        except ValueError as exc:
            raise AssignmentError("created_at is not a canonical UTC timestamp") from exc

    value = {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "project_id": project_id,
        "role": role,
        "source_repository": source_repository,
        "source_branch": source_branch,
        "source_sha": source_sha,
        "source_evidence": source_evidence,
        "seed_manifest_digest": seed_manifest_digest,
        "engine": engine,
        "provider": provider,
        "capacity_pool": capacity_pool,
        "billing_basis": billing_basis,
        "metered_approved": metered_approved,
        "model": model,
        "model_parameters": params,
        "host": host,
        "sandbox_profile": sandbox_profile,
        "network_profile": network_profile,
        "allowed_paths": normalized_allowed_paths,
        "gate_digest": gate_digest,
        "publication_policy": publication_policy,
        "default_branch": default_branch,
        "integration_branch": integration_branch,
        "created_at": created_at if created_at is not None else now_iso(),
    }
    value["assignment_digest"] = canonical_digest(value)
    return value


def capacity_pool_dir_default() -> Path:
    return capacity_pool_dir()


# --- persistence ----------------------------------------------------------------------

def assignment_path(root: Path, task_id: str, digest: str) -> Path:
    if not isinstance(task_id, str) or not isinstance(digest, str) \
            or not IDENTIFIER_RE.fullmatch(task_id) or not DIGEST_RE.fullmatch(digest):
        raise AssignmentError("assignment path identity is not canonical")
    try:
        return Path(root) / task_id / f"{digest}.json"
    except (TypeError, ValueError) as exc:
        raise AssignmentError("assignment root is not a path") from exc


def index_path(root: Path) -> Path:
    try:
        return Path(root) / "index.jsonl"
    except (TypeError, ValueError) as exc:
        raise AssignmentError("assignment root is not a path") from exc


def _assignment_persistence_hook(stage: str) -> None:
    """Test seam for deterministic swaps while all trusted directories are pinned."""
    del stage


def _ensure_output_path_safe(path: Path) -> None:
    """Keep the optional human-readable --out copy's historical link refusal."""
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor) if absolute.anchor else Path()
    for part in absolute.parts[1:] if absolute.anchor else absolute.parts:
        current /= part
        try:
            metadata = os.lstat(current)
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode) or (
                os.name == "nt" and bool(getattr(
                    metadata, "st_file_attributes", 0
                ) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400))):
            raise AssignmentError(f"assignment output path contains a link or reparse point: {current}")


def _atomic_write(path: Path, text: str) -> None:
    try:
        if not isinstance(text, str):
            raise AssignmentError("assignment output must be text")
        _ensure_output_path_safe(Path(path))
        jsonl_durable.atomic_bytes(
            Path(path), text.encode("utf-8"), hook=_assignment_persistence_hook
        )
    except jsonl_durable.JsonlDurabilityError as exc:
        raise AssignmentError(f"assignment output publication refused: {path}") from exc
    except (OSError, UnicodeEncodeError, TypeError, ValueError, OverflowError,
            RecursionError) as exc:
        raise AssignmentError(f"assignment output publication refused: {path}") from exc


def _posix_open_directory(path: Path) -> int:
    """Create/open *path* one component at a time, retaining the final directory fd."""
    if os.name == "nt" or not hasattr(os, "supports_dir_fd") or not os.supports_dir_fd:
        raise AssignmentError("POSIX pinned-directory persistence is unavailable")
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if not nofollow:
        raise AssignmentError("O_NOFOLLOW is required for assignment persistence")
    absolute = Path(os.path.abspath(path))
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | nofollow | getattr(os, "O_CLOEXEC", 0)
    try:
        current_fd = os.open(absolute.anchor, flags)
    except OSError as exc:
        raise AssignmentError(f"cannot pin assignment path anchor {absolute.anchor}: {exc}") from exc
    try:
        for component in absolute.parts[1:]:
            try:
                os.mkdir(component, mode=0o700, dir_fd=current_fd)
            except FileExistsError:
                pass
            next_fd = os.open(component, flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _read_at_directory(directory: int, name: str) -> bytes | None:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=directory)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise AssignmentError(f"cannot open assignment record {name!r}: {exc}") from exc
    try:
        pinned_path = jsonl_durable._pinned_fd_path(directory, name)
        identity = jsonl_durable._capture_opened_leaf(pinned_path, descriptor)
        chunks: list[bytes] = []
        while True:
            jsonl_durable._revalidate_opened_leaf(pinned_path, descriptor, identity)
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(descriptor)


def _open_private_at(directory: int, prefix: str) -> tuple[int, str]:
    for _ in range(128):
        name = f"{prefix}{os.getpid()}-{time.time_ns():x}-{os.urandom(8).hex()}"
        try:
            return os.open(
                name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                0o600,
                dir_fd=directory,
            ), name
        except FileExistsError:
            continue
    raise AssignmentError("could not allocate an assignment temporary")


def _persist_record_posix(task_directory: int, digest: str, encoded: bytes) -> None:
    final_name = f"{digest}.json"
    jsonl_durable.validate_durable_leaf_at(task_directory, final_name, allow_missing=True)
    existing = _read_at_directory(task_directory, final_name)
    if existing is not None:
        if existing != encoded:
            raise AssignmentError("content-address collision — refusing to overwrite immutable assignment")
        return
    _assignment_persistence_hook("pre-mkstemp")
    descriptor, temporary_name = _open_private_at(task_directory, f".{final_name}.")
    temporary = jsonl_durable._pinned_fd_path(task_directory, temporary_name)
    try:
        temporary_identity = jsonl_durable._capture_opened_leaf(temporary, descriptor)
        _assignment_persistence_hook("pre-record-write")
        jsonl_durable._write_all(
            descriptor, encoded, leaf_path=temporary, leaf_identity=temporary_identity
        )
        os.fsync(descriptor)
        _assignment_persistence_hook("pre-record-publish")
        jsonl_durable._revalidate_opened_leaf(temporary, descriptor, temporary_identity)
        jsonl_durable.validate_durable_leaf_at(task_directory, final_name, allow_missing=True)
        try:
            os.link(
                temporary_name, final_name,
                src_dir_fd=task_directory, dst_dir_fd=task_directory,
                follow_symlinks=False,
            )
        except FileExistsError:
            existing = _read_at_directory(task_directory, final_name)
            if existing != encoded:
                raise AssignmentError("content-address collision — refusing to overwrite immutable assignment")
    finally:
        try:
            os.unlink(temporary_name, dir_fd=task_directory)
        except FileNotFoundError:
            pass
        finally:
            os.close(descriptor)
    os.fsync(task_directory)


def _assert_posix_pin(path: Path, descriptor: int, label: str) -> None:
    """Reject a changed pathname after the fd-only commit, without using it for writes."""
    try:
        current = os.stat(path, follow_symlinks=False)
    except OSError as exc:
        raise AssignmentError(f"pinned {label} pathname changed during persistence") from exc
    pinned = os.fstat(descriptor)
    if not stat.S_ISDIR(current.st_mode) or (current.st_dev, current.st_ino) != (
            pinned.st_dev, pinned.st_ino):
        raise AssignmentError(f"pinned {label} pathname changed during persistence")


if os.name == "nt":
    _KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
    _FILE_SHARE_READ = 0x00000001
    _FILE_SHARE_WRITE = 0x00000002
    _GENERIC_READ = 0x80000000
    _GENERIC_WRITE = 0x40000000
    _OPEN_EXISTING = 3
    _OPEN_ALWAYS = 4
    _CREATE_NEW = 1
    _FILE_ATTRIBUTE_NORMAL = 0x80
    _FILE_ATTRIBUTE_REPARSE_POINT = 0x400
    _FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
    _FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
    _FileAttributeTagInfo = 9

    class _FILE_ATTRIBUTE_TAG_INFO_STRUCT(ctypes.Structure):
        _fields_ = [("FileAttributes", ctypes.c_uint32), ("ReparseTag", ctypes.c_uint32),
                    ("Reserved", ctypes.c_uint32)]

    _KERNEL32.CreateFileW.restype = ctypes.c_void_p
    _KERNEL32.GetFileInformationByHandleEx.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                                        ctypes.c_void_p, ctypes.c_uint32]
    _KERNEL32.GetFileInformationByHandleEx.restype = ctypes.c_int
    _KERNEL32.CloseHandle.argtypes = [ctypes.c_void_p]
    _KERNEL32.CloseHandle.restype = ctypes.c_int

    def _win_handle_attributes(handle: int) -> int:
        info = _FILE_ATTRIBUTE_TAG_INFO_STRUCT()
        if not _KERNEL32.GetFileInformationByHandleEx(
                ctypes.c_void_p(handle), _FileAttributeTagInfo, ctypes.byref(info), ctypes.sizeof(info)):
            raise OSError(ctypes.get_last_error(), "GetFileInformationByHandleEx failed")
        return int(info.FileAttributes)

    def _win_open_directory(path: Path, disposition: int = _OPEN_EXISTING) -> int:
        handle = _KERNEL32.CreateFileW(
            str(path), _GENERIC_READ,
            _FILE_SHARE_READ | _FILE_SHARE_WRITE, None, disposition,
            _FILE_FLAG_BACKUP_SEMANTICS | _FILE_FLAG_OPEN_REPARSE_POINT, None,
        )
        if handle in (None, _INVALID_HANDLE_VALUE):
            raise OSError(ctypes.get_last_error(), f"cannot pin Windows directory {path}")
        try:
            if _win_handle_attributes(handle) & _FILE_ATTRIBUTE_REPARSE_POINT:
                raise AssignmentError(f"Windows directory is a reparse point: {path}")
            return int(handle)
        except BaseException:
            _KERNEL32.CloseHandle(ctypes.c_void_p(handle))
            raise

    def _win_pin_directory(path: Path) -> list[tuple[Path, int]]:
        absolute = Path(os.path.abspath(path))
        parts = absolute.parts
        if not parts:
            raise AssignmentError("cannot pin an empty Windows path")
        handles: list[tuple[Path, int]] = []
        current = Path(parts[0])
        try:
            handles.append((current, _win_open_directory(current)))
            for component in parts[1:]:
                current = current / component
                try:
                    # NTFS inherits the parent ACL; native handles below provide the
                    # rename/delete protection, while mode=0o700 can deny this user access.
                    current.mkdir(mode=0o777)
                except FileExistsError:
                    pass
                handles.append((current, _win_open_directory(current)))
            if len(parts) == 1:
                handles.append((current, _win_open_directory(current)))
            return handles
        except BaseException:
            for _, handle in reversed(handles):
                _KERNEL32.CloseHandle(ctypes.c_void_p(handle))
            raise

    def _win_open_file(path: Path, disposition: int) -> int:
        handle = _KERNEL32.CreateFileW(
            str(path), _GENERIC_READ | _GENERIC_WRITE,
            _FILE_SHARE_READ | _FILE_SHARE_WRITE, None, disposition,
            _FILE_ATTRIBUTE_NORMAL | _FILE_FLAG_OPEN_REPARSE_POINT, None,
        )
        if handle in (None, _INVALID_HANDLE_VALUE):
            raise OSError(ctypes.get_last_error(), f"cannot open pinned Windows file {path}")
        try:
            if _win_handle_attributes(handle) & _FILE_ATTRIBUTE_REPARSE_POINT:
                raise AssignmentError(f"Windows file is a reparse point: {path}")
            return int(handle)
        except BaseException:
            _KERNEL32.CloseHandle(ctypes.c_void_p(handle))
            raise

    def _win_fd(handle: int, flags: int) -> int:
        import msvcrt
        try:
            return msvcrt.open_osfhandle(handle, flags)
        except (OSError, TypeError, ValueError) as exc:
            _KERNEL32.CloseHandle(ctypes.c_void_p(handle))
            raise AssignmentError("cannot adopt pinned Windows file handle") from exc

    def _win_file_exists_error(exc: OSError) -> bool:
        return exc.errno in (80, 183) or getattr(exc, "winerror", None) in (80, 183)

    def _win_read_file(path: Path) -> bytes | None:
        try:
            handle = _win_open_file(path, _OPEN_EXISTING)
        except OSError as exc:
            if isinstance(exc, FileNotFoundError) or exc.errno in (2, 3) \
                    or getattr(exc, "winerror", None) in (2, 3):
                return None
            raise
        descriptor = _win_fd(handle, os.O_RDONLY | getattr(os, "O_BINARY", 0))
        try:
            identity = jsonl_durable._capture_opened_leaf(path, descriptor)
            chunks: list[bytes] = []
            while True:
                jsonl_durable._revalidate_opened_leaf(path, descriptor, identity)
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    return b"".join(chunks)
                chunks.append(chunk)
        finally:
            os.close(descriptor)

    def _persist_record_windows(task_path: Path, digest: str, encoded: bytes) -> None:
        final = task_path / f"{digest}.json"
        jsonl_durable.validate_durable_leaf(final, allow_missing=True)
        existing = _win_read_file(final)
        if existing is not None:
            if existing != encoded:
                raise AssignmentError("content-address collision — refusing to overwrite immutable assignment")
            return
        _assignment_persistence_hook("pre-mkstemp")
        handle = None
        temporary = None
        for _ in range(128):
            candidate = task_path / f".{digest}.json.{os.getpid()}.{time.time_ns():x}.{os.urandom(8).hex()}.tmp"
            try:
                handle = _win_open_file(candidate, _CREATE_NEW)
                temporary = candidate
                break
            except OSError as exc:
                if not _win_file_exists_error(exc):
                    raise
        if handle is None or temporary is None:
            raise AssignmentError("could not allocate a unique Windows assignment temporary")
        descriptor = _win_fd(handle, os.O_WRONLY | getattr(os, "O_BINARY", 0))
        handle = None
        try:
            temporary_identity = jsonl_durable._capture_opened_leaf(temporary, descriptor)
            _assignment_persistence_hook("pre-record-write")
            jsonl_durable._write_all(
                descriptor, encoded, leaf_path=temporary, leaf_identity=temporary_identity
            )
            os.fsync(descriptor)
            _assignment_persistence_hook("pre-record-publish")
            jsonl_durable._revalidate_opened_leaf(temporary, descriptor, temporary_identity)
            jsonl_durable.validate_durable_leaf(final, allow_missing=True)
            if not _KERNEL32.CreateHardLinkW(str(final), str(temporary), None):
                error = ctypes.get_last_error()
                if error not in (80, 183):  # ERROR_FILE_EXISTS / ERROR_ALREADY_EXISTS
                    raise OSError(error, "CreateHardLinkW failed")
                existing = _win_read_file(final)
                if existing != encoded:
                    raise AssignmentError("content-address collision — refusing to overwrite immutable assignment")
        except BaseException:
            try:
                _KERNEL32.DeleteFileW(str(temporary))
            finally:
                raise
        finally:
            try:
                os.close(descriptor)
            except OSError:
                pass
            # Publication can fail after the private file is completely durable (for
            # example, if an attacker races a junction into the immutable leaf).  The
            # task directory is handle-pinned without delete sharing, so this pathname
            # still names our private temporary and is safe to remove on every exit.
            if not _KERNEL32.DeleteFileW(str(temporary)):
                error = ctypes.get_last_error()
                if error not in (2, 3):  # already removed by the failed publication path
                    raise OSError(error, "cannot remove Windows assignment temporary")


def _assignment_index_record(value: dict) -> dict:
    return {
        "schema_version": SCHEMA_VERSION, "assignment_digest": value["assignment_digest"],
        "task_id": value["task_id"], "role": value["role"], "engine": value["engine"],
        "provider": value["provider"], "capacity_pool": value["capacity_pool"],
        "host": value["host"], "created_at": value["created_at"],
    }


def _persist_assignment_posix(root: Path, value: dict, encoded: bytes) -> Path:
    root_fd = _posix_open_directory(root)
    task_fd: int | None = None
    cache_fd: int | None = None
    try:
        task_id = value["task_id"]
        try:
            os.mkdir(task_id, mode=0o700, dir_fd=root_fd)
        except FileExistsError:
            pass
        task_fd = os.open(
            task_id,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=root_fd,
        )

        jsonl_durable.validate_durable_leaf_at(root_fd, "index.jsonl", allow_missing=True)

        cache_name = ".jsonl-index"
        try:
            os.mkdir(cache_name, mode=0o700, dir_fd=root_fd)
        except FileExistsError:
            pass
        cache_fd = os.open(
            cache_name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=root_fd,
        )
        identity = f"assignment-root/{value['task_id']}/index.jsonl"
        jsonl_durable.validate_durable_leaf_at(
            cache_fd, jsonl_durable.index_cache_name(identity), allow_missing=True
        )

        _persist_record_posix(task_fd, value["assignment_digest"], encoded)
        _assignment_persistence_hook("pre-index-open")
        jsonl_durable.append_jsonl_at(
            root_fd, "index.jsonl", _assignment_index_record(value), cache_fd, identity,
            dedupe_field="assignment_digest", dedupe_value=value["assignment_digest"],
            hook=_assignment_persistence_hook,
        )
        os.fsync(root_fd)
        _assert_posix_pin(root, root_fd, "root")
        _assert_posix_pin(root / task_id, task_fd, "task directory")
        return assignment_path(root, value["task_id"], value["assignment_digest"])
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, jsonl_durable.JsonlDurabilityError) as exc:
        raise AssignmentError(f"pinned assignment persistence failed: {exc}") from exc
    finally:
        if cache_fd is not None:
            os.close(cache_fd)
        if task_fd is not None:
            os.close(task_fd)
        os.close(root_fd)


def _persist_assignment_windows(root: Path, value: dict, encoded: bytes) -> Path:
    root = Path(os.path.abspath(root))
    root_pins = _win_pin_directory(root)
    task = root / value["task_id"]
    task_pins: list[tuple[Path, int]] = []
    cache_pins: list[tuple[Path, int]] = []
    index_handle: int | None = None
    try:
        task_pins = _win_pin_directory(task)
        cache = root / ".jsonl-index"
        cache_pins = _win_pin_directory(cache)
        index = root / "index.jsonl"
        index_native = _win_open_file(index, _OPEN_ALWAYS)
        index_handle = _win_fd(index_native, os.O_RDWR | getattr(os, "O_BINARY", 0))
        index_identity = jsonl_durable._capture_opened_leaf(index, index_handle)
        identity = f"assignment-root/{value['task_id']}/index.jsonl"
        jsonl_durable.validate_durable_leaf(
            cache / jsonl_durable.index_cache_name(identity), allow_missing=True
        )
        jsonl_durable._revalidate_opened_leaf(index, index_handle, index_identity)
        _persist_record_windows(task, value["assignment_digest"], encoded)
        _assignment_persistence_hook("pre-index-open")
        for attempt in range(8):
            try:
                with jsonl_durable.durable_lock(index):
                    jsonl_durable._revalidate_opened_leaf(index, index_handle, index_identity)
                    jsonl_durable.append_jsonl(
                        index, _assignment_index_record(value),
                        dedupe_field="assignment_digest", dedupe_value=value["assignment_digest"],
                        index_root=cache, index_identity=identity,
                        hook=_assignment_persistence_hook,
                    )
                break
            except jsonl_durable.JsonlDurabilityError as exc:
                if str(exc) != "durable JSONL transaction lock is contended" or attempt == 7:
                    raise
                time.sleep(0.01)
        return assignment_path(root, value["task_id"], value["assignment_digest"])
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, jsonl_durable.JsonlDurabilityError) as exc:
        raise AssignmentError(f"pinned Windows assignment persistence failed: {exc}") from exc
    finally:
        for descriptor in (index_handle,):
            if descriptor is not None:
                os.close(descriptor)
        for pins in (cache_pins, task_pins, root_pins):
            for _, handle in reversed(pins):
                _KERNEL32.CloseHandle(ctypes.c_void_p(handle))


def persist_assignment(root: Path, value: dict, *, capacity_pool_dir: Path | None = None) -> Path:
    validate_assignment(
        value, require_source_evidence=True, capacity_pool_dir=capacity_pool_dir
    )
    try:
        root = Path(root)
        encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeEncodeError) as exc:
        raise AssignmentError("assignment is not serializable") from exc
    try:
        if os.name == "nt":
            return _persist_assignment_windows(root, value, encoded)
        return _persist_assignment_posix(root, value, encoded)
    except AssignmentError:
        raise
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError) as exc:
        raise AssignmentError(f"assignment persistence refused: {exc}") from exc


def _is_reparse_point(path: Path) -> bool:
    """Detect POSIX links and every Windows reparse representation without following it."""
    try:
        junction = getattr(path, "is_junction", None)
        if callable(junction) and junction():
            return True
        metadata = os.lstat(path)
    except (OSError, ValueError):
        return False
    return stat.S_ISLNK(metadata.st_mode) or (
        os.name == "nt"
        and bool(getattr(metadata, "st_file_attributes", 0)
                 & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400))
    )


def _path_contains_reparse_point(path: Path) -> bool:
    """Inspect each existing component with lstat, including junctions on Windows."""
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor) if absolute.anchor else Path()
    parts = absolute.parts[1:] if absolute.anchor else absolute.parts
    for part in parts:
        current /= part
        if _is_reparse_point(current):
            return True
    return False


def load_assignment(root: Path, task_id: str, digest: str) -> dict | None:
    try:
        root = Path(root)
        path = assignment_path(root, task_id, digest)
        raw = jsonl_durable.read_durable_bytes(path, max_bytes=MAX_INPUT_BYTES)
    except (AssignmentError, jsonl_durable.JsonlDurabilityError, TypeError, ValueError,
            OSError, OverflowError, RecursionError, UnicodeDecodeError):
        return None
    if raw is None:
        return None
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError,
            OverflowError, RecursionError):
        return None
    if not isinstance(value, dict):
        return None
    return value


def validate_assignment(value: object, require_source_evidence: bool = False,
                        capacity_pool_dir: Path | None = None) -> dict:
    if not isinstance(require_source_evidence, bool):
        raise AssignmentError("require_source_evidence must be boolean")
    if not isinstance(value, dict):
        raise AssignmentError("assignment is not an object")
    required = {"schema_version", "task_id", "project_id", "role", "source_repository", "source_branch",
                "source_sha", "seed_manifest_digest", "engine", "provider", "capacity_pool", "model",
                "model_parameters", "host", "sandbox_profile", "network_profile", "allowed_paths",
                "gate_digest", "publication_policy", "created_at", "assignment_digest"}
    if require_source_evidence:
        required |= {"source_evidence", "billing_basis", "metered_approved",
                     "default_branch", "integration_branch"}
    missing = required - value.keys()
    if missing:
        raise AssignmentError("assignment missing required field(s): " + ", ".join(sorted(missing)))
    if value.get("schema_version") != SCHEMA_VERSION or set(value) - ASSIGNMENT_FIELDS:
        raise AssignmentError("assignment schema/runtime mismatch")
    if not isinstance(value.get("schema_version"), int) or isinstance(value.get("schema_version"), bool):
        raise AssignmentError("assignment schema_version must be an integer")
    task_id, project_id = value.get("task_id"), value.get("project_id")
    if not isinstance(task_id, str) or not IDENTIFIER_RE.fullmatch(task_id) \
            or not isinstance(project_id, str) or not IDENTIFIER_RE.fullmatch(project_id):
        raise AssignmentError("assignment identity is not canonical")
    role, source_repository = value.get("role"), value.get("source_repository")
    if not isinstance(role, str) or role not in ROLES or not _nonempty(source_repository):
        raise AssignmentError("assignment role or source repository is invalid")
    source_sha = value.get("source_sha")
    if not isinstance(source_sha, str) or not SHA_RE.fullmatch(source_sha):
        raise AssignmentError("assignment source_sha is invalid")
    source_branch = canonical_branch(value.get("source_branch"), "source_branch")
    if require_source_evidence or "source_evidence" in value:
        canonical_source_evidence(value.get("source_evidence"), source_repository, source_branch, source_sha)
    seed_manifest_digest = value.get("seed_manifest_digest")
    if seed_manifest_digest is not None and (
            not isinstance(seed_manifest_digest, str) or not DIGEST_RE.fullmatch(seed_manifest_digest)):
        raise AssignmentError("assignment seed_manifest_digest is invalid")
    engine = value.get("engine")
    if not isinstance(engine, str) \
            or not (engine in engine_contract.BUILTIN_ENGINES
                    or engine_contract.plugin_engine_name_ok(engine)):
        raise AssignmentError("assignment engine is invalid")
    provider = value.get("provider")
    if not isinstance(provider, str) or not PROVIDER_RE.fullmatch(provider):
        raise AssignmentError("assignment provider is invalid")
    engine_provider, engine_basis = engine_contract_attribution(engine)
    if engine_provider is not None and engine_provider != provider:
        raise AssignmentError("assignment provider does not match engine manifest")
    capacity_pool = value.get("capacity_pool")
    if capacity_pool is not None and (
            not isinstance(capacity_pool, str) or not IDENTIFIER_RE.fullmatch(capacity_pool)):
        raise AssignmentError("assignment capacity_pool is invalid")
    billing_basis = value.get("billing_basis")
    if billing_basis is not None and (
            not isinstance(billing_basis, str) or billing_basis not in CAPACITY_POOL_BILLING_BASES):
        raise AssignmentError("assignment billing_basis is invalid")
    if billing_basis is not None and engine_basis is not None and billing_basis != engine_basis:
        raise AssignmentError("assignment billing_basis does not match engine manifest")
    metered_approved = value.get("metered_approved")
    if "metered_approved" in value and not isinstance(metered_approved, bool):
        raise AssignmentError("assignment metered_approved must be boolean")
    if billing_basis == "metered" and metered_approved is not True:
        raise AssignmentError("metered assignment is not approved")

    if capacity_pool is not None:
        pool_dir = capacity_pool_dir if capacity_pool_dir is not None else capacity_pool_dir_default()
        try:
            pool = load_capacity_pool(pool_dir, capacity_pool)
        except CapacityPoolNotFound:
            # A validator without the authority directory can still validate an assignment
            # produced by a caller-owned test/controller registry.  When the directory is
            # explicitly supplied, a missing authority is a hard refusal; malformed
            # authority is always a hard refusal.
            if capacity_pool_dir is not None:
                raise
        else:
            if pool["provider"] != provider:
                raise AssignmentError("capacity pool provider does not match assignment provider")
            roles = pool.get("roles")
            if roles is not None and value.get("role") not in roles:
                raise AssignmentError("assignment role is not allowed by capacity pool")
            if pool.get("host_id") is not None and pool["host_id"] != value.get("host"):
                raise AssignmentError("assignment host does not match capacity pool")
            if billing_basis != pool["billing_basis"]:
                raise AssignmentError("assignment billing_basis does not match capacity pool")
    model = value.get("model")
    if model is not None and not _nonempty(model):
        raise AssignmentError("assignment model must be null or a nonempty string")
    parameters = value.get("model_parameters")
    if not isinstance(parameters, dict):
        raise AssignmentError("assignment model_parameters must be an object")
    for key, item in parameters.items():
        if not isinstance(key, str) or not MODEL_PARAM_KEY_RE.fullmatch(key) \
                or not isinstance(item, str):
            raise AssignmentError(f"assignment model parameter {key!r} is invalid")
    if not _nonempty(value.get("host")):
        raise AssignmentError("assignment host must be a nonempty string")
    if not isinstance(value.get("sandbox_profile"), str) or value.get("sandbox_profile") not in SANDBOX_PROFILES:
        raise AssignmentError("assignment sandbox_profile is invalid")
    if not isinstance(value.get("network_profile"), str) or value.get("network_profile") not in NETWORK_PROFILES:
        raise AssignmentError("assignment network_profile is invalid")
    _normalize_allowed_paths(value.get("allowed_paths"))
    gate_digest = value.get("gate_digest")
    if gate_digest is not None and (
            not isinstance(gate_digest, str) or not DIGEST_RE.fullmatch(gate_digest)):
        raise AssignmentError("assignment gate_digest is invalid")
    publication_policy = value.get("publication_policy")
    if not isinstance(publication_policy, str) or not SLUG_RE.fullmatch(publication_policy):
        raise AssignmentError("assignment publication_policy is invalid")
    default_branch = value.get("default_branch")
    integration_branch = value.get("integration_branch")
    if "default_branch" in value:
        default_branch = canonical_branch(default_branch, "default_branch")
    if "integration_branch" in value:
        integration_branch = canonical_branch(integration_branch, "integration_branch")
    if default_branch is not None and integration_branch is not None \
            and default_branch == integration_branch:
        raise AssignmentError("default_branch and integration_branch must differ")
    created_at = value.get("created_at")
    if not isinstance(created_at, str) or not created_at or created_at != created_at.strip():
        raise AssignmentError("assignment created_at must be a nonempty timestamp string")
    try:
        datetime.datetime.strptime(created_at, TS_FORMAT)
    except ValueError as exc:
        raise AssignmentError("assignment created_at is not a canonical UTC timestamp") from exc
    assignment_digest = value.get("assignment_digest")
    if not isinstance(assignment_digest, str) or not DIGEST_RE.fullmatch(assignment_digest):
        raise AssignmentError("assignment_digest is invalid")
    if canonical_digest(value) != value.get("assignment_digest"):
        raise AssignmentError("assignment digest does not match its content")
    return value


def assignment_projection(value: dict) -> dict:
    """Return the complete, exact run-evidence projection of an assignment."""
    if not isinstance(value, dict):
        raise AssignmentError("assignment projection requires an object")
    validate_assignment(value, require_source_evidence=True)
    return {key: value[key] for key in ASSIGNMENT_PROJECTION_FIELDS}


def type_aware_equal(left: object, right: object) -> bool:
    """Compare JSON values without Python's bool/int/float equality coercions."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        if len(left) != len(right):
            return False
        unmatched = list(right.items())
        for left_key, left_value in left.items():
            for index, (right_key, right_value) in enumerate(unmatched):
                if type_aware_equal(left_key, right_key) and type_aware_equal(left_value, right_value):
                    del unmatched[index]
                    break
            else:
                return False
        return not unmatched
    if isinstance(left, list):
        return len(left) == len(right) and all(type_aware_equal(left_item, right_item)
                   for left_item, right_item in zip(left, right))
    return left == right


def require_assignment_projection(run: object, persisted: dict) -> dict:
    """Require both nested and top-level run attribution to equal the persisted record."""
    if not isinstance(run, dict):
        raise AssignmentError("run evidence is not an object")
    validate_assignment(persisted, require_source_evidence=True)
    expected = assignment_projection(persisted)
    nested = run.get("assignment")
    if not type_aware_equal(nested, expected):
        raise AssignmentError("run assignment projection disagrees with persisted assignment")
    for key, expected_value in expected.items():
        if key not in run or not type_aware_equal(run[key], expected_value):
            raise AssignmentError(f"run attribution field {key!r} disagrees with persisted assignment")
    return expected


# --- CLI --------------------------------------------------------------------------------

def _parse_model_params(pairs: list[str]) -> dict:
    if not isinstance(pairs, list) or not all(isinstance(item, str) for item in pairs):
        raise AssignmentError("--model-param values must be strings")
    params: dict[str, str] = {}
    for item in pairs:
        key, sep, value = item.partition("=")
        if not sep:
            raise AssignmentError(f"invalid --model-param {item!r} (expected key=value)")
        params[key] = value
    return params


def command_resolve(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else DEFAULT_STATE_ROOT
    pool_dir = Path(args.capacity_pool_dir) if args.capacity_pool_dir else capacity_pool_dir()
    try:
        params = _parse_model_params(args.model_param)
        source_evidence = None
        if args.source_evidence_file:
            raw_source_evidence = jsonl_durable.read_durable_bytes(
                Path(args.source_evidence_file), max_bytes=MAX_INPUT_BYTES
            )
            if raw_source_evidence is None:
                raise AssignmentError("source evidence file is absent")
            source_evidence = json.loads(raw_source_evidence.decode("utf-8"))
        value = resolve_assignment(
            task_id=args.task_id, project_id=args.project_id, role=args.role,
            source_repository=args.source_repository, source_branch=args.source_branch,
            source_sha=args.source_sha, seed_manifest_digest=args.seed_manifest_digest,
            engine=args.engine, provider=args.provider, capacity_pool=args.capacity_pool,
            model=args.model, model_parameters=params, host=args.host,
            sandbox_profile=args.sandbox_profile, network_profile=args.network_profile,
            allowed_paths=_split_paths(args.allowed_paths), gate_digest=args.gate_digest,
            publication_policy=args.publication_policy, capacity_pool_dir=pool_dir,
            source_evidence=source_evidence,
            billing_basis=args.billing_basis, metered_approved=args.metered_approved,
            default_branch=args.default_branch, integration_branch=args.integration_branch,
        )
        if not args.no_persist:
            persist_assignment(root, value)
    except (AssignmentError, OSError, json.JSONDecodeError, TypeError, ValueError,
            OverflowError, RecursionError, UnicodeDecodeError):
        diag("invalid input or durable state")
        return 2
    if args.out:
        try:
            _atomic_write(Path(args.out), json.dumps(value, indent=2, sort_keys=True) + "\n")
        except (AssignmentError, OSError, TypeError, ValueError, OverflowError,
                RecursionError, UnicodeDecodeError, json.JSONDecodeError):
            diag("failed to write --out copy")
            return 2
    print(json.dumps(value, sort_keys=True))
    return 0


def command_show(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else DEFAULT_STATE_ROOT
    value = load_assignment(root, args.task_id, args.assignment_digest)
    if value is None:
        diag(f"no such assignment: task_id={args.task_id} digest={args.assignment_digest}")
        return 2
    print(json.dumps(value, sort_keys=True))
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROG, description="Immutable run-assignment resolver.")
    sub = parser.add_subparsers(dest="command", required=True)

    resolve = sub.add_parser("resolve", help="resolve, digest, and durably persist an assignment")
    for name in ("task-id", "project-id", "role", "source-repository", "source-branch",
                 "source-sha", "engine", "provider", "host", "sandbox-profile",
                 "network-profile", "allowed-paths", "publication-policy"):
        resolve.add_argument(f"--{name}", required=True)
    resolve.add_argument("--seed-manifest-digest", default=None)
    resolve.add_argument("--capacity-pool", default=None)
    resolve.add_argument("--model", default=None)
    resolve.add_argument("--model-param", action="append", default=[])
    resolve.add_argument("--gate-digest", default=None)
    resolve.add_argument("--root", default=None)
    resolve.add_argument("--capacity-pool-dir", default=None)
    resolve.add_argument("--source-evidence-file", default=None)
    resolve.add_argument("--billing-basis", default=None)
    resolve.add_argument("--metered-approved", action="store_true")
    resolve.add_argument("--default-branch", default="main")
    resolve.add_argument("--integration-branch", default="recursion/integration")
    resolve.add_argument("--out", default=None)
    resolve.add_argument("--no-persist", action="store_true",
                         help="emit a validated candidate without writing durable state")

    show = sub.add_parser("show", help="print a previously persisted assignment")
    show.add_argument("--task-id", required=True)
    show.add_argument("--assignment-digest", required=True)
    show.add_argument("--root", default=None)

    return parser.parse_args(argv)


def main() -> int:
    try:
        args = parse_args(sys.argv[1:])
        handlers = {"resolve": command_resolve, "show": command_show}
        return handlers[args.command](args)
    except (AssignmentError, OSError, json.JSONDecodeError, TypeError, ValueError,
            OverflowError, RecursionError, UnicodeDecodeError):
        diag("invalid input or durable state")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

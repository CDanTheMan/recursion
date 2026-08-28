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
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine_contract  # noqa: E402  (shared engine/alias contract helpers, D-015)

PROG = "assignment"
SCHEMA_VERSION = 1
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

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


class AssignmentError(Exception):
    """Invalid inputs, a malformed capacity-pool manifest, or a persistence conflict."""


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def now_iso() -> str:
    return time.strftime(TS_FORMAT, time.gmtime())


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and value.strip() != "" and value == value.strip()


def _split_paths(value: str) -> list[str]:
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
    obj = _require_keys(data, {"schema_version", "id", "kind", "billing_basis", "provider", "quota", "on_demand"}, "capacity-pool manifest")
    extra = obj.keys() - CAPACITY_POOL_TOP_KEYS
    if extra:
        raise AssignmentError(f"capacity-pool manifest has unknown key(s): {', '.join(sorted(extra))}")
    if obj.get("schema_version") != 1:
        raise AssignmentError("capacity-pool manifest schema_version must be 1")
    if obj.get("id") != pool_id:
        raise AssignmentError(f"capacity-pool id {obj.get('id')!r} does not match filename stem {pool_id!r}")
    if not IDENTIFIER_RE.fullmatch(pool_id):
        raise AssignmentError(f"invalid capacity-pool id {pool_id!r}")
    if obj.get("kind") not in CAPACITY_POOL_KINDS:
        raise AssignmentError(f"capacity-pool kind must be one of {sorted(CAPACITY_POOL_KINDS)}")
    if obj.get("billing_basis") not in CAPACITY_POOL_BILLING_BASES:
        raise AssignmentError(f"capacity-pool billing_basis must be one of {sorted(CAPACITY_POOL_BILLING_BASES)}")
    if not _nonempty(obj.get("provider")) or not PROVIDER_RE.fullmatch(obj["provider"]):
        raise AssignmentError("capacity-pool provider must be a nonempty lowercase-kebab string")
    quota = _require_keys(obj.get("quota"), {"period", "source"}, "capacity-pool quota")
    extra_quota = quota.keys() - QUOTA_KEYS
    if extra_quota:
        raise AssignmentError(f"capacity-pool quota has unknown key(s): {', '.join(sorted(extra_quota))}")
    if quota.get("period") not in QUOTA_PERIODS:
        raise AssignmentError(f"capacity-pool quota.period must be one of {sorted(QUOTA_PERIODS)}")
    if quota.get("source") not in QUOTA_SOURCES:
        raise AssignmentError(f"capacity-pool quota.source must be one of {sorted(QUOTA_SOURCES)}")
    limit = quota.get("limit")
    if limit is not None and not (isinstance(limit, (int, float)) and not isinstance(limit, bool) and limit >= 0):
        raise AssignmentError("capacity-pool quota.limit must be null or a non-negative number")
    unit = quota.get("unit")
    if unit is not None and not _nonempty(unit):
        raise AssignmentError("capacity-pool quota.unit must be null or a nonempty string")
    if not isinstance(obj.get("on_demand"), bool):
        raise AssignmentError("capacity-pool on_demand must be a boolean")
    roles = obj.get("roles")
    if roles is not None and (not isinstance(roles, list) or not all(isinstance(r, str) and r for r in roles)):
        raise AssignmentError("capacity-pool roles must be null or a list of nonempty strings")
    host_id = obj.get("host_id")
    if host_id is not None and not _nonempty(host_id):
        raise AssignmentError("capacity-pool host_id must be null or a nonempty string")
    fallback = obj.get("fallback_policy")
    if fallback is not None and fallback not in FALLBACK_POLICIES:
        raise AssignmentError(f"capacity-pool fallback_policy must be null or one of {sorted(FALLBACK_POLICIES)}")
    return obj


def load_capacity_pool(pool_dir: Path, pool_id: str) -> dict:
    if not IDENTIFIER_RE.fullmatch(pool_id or ""):
        raise AssignmentError(f"invalid capacity-pool id {pool_id!r}")
    path = pool_dir / f"{pool_id}.json"
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AssignmentError(f"capacity-pool manifest not found: {path} ({exc})") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssignmentError(f"capacity-pool manifest {path} is not valid JSON: {exc}") from exc
    return validate_capacity_pool(data, pool_id)


def engine_contract_attribution(engine: str) -> tuple[str | None, str | None]:
    if engine == "claude":
        return "anthropic-claude-code", "flat-subscription"
    path = Path(os.environ.get("RECURSION_ENGINE_DIR") or Path(__file__).resolve().parent / "engines") / f"{engine}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        billing = data.get("billing") if isinstance(data, dict) else None
        if isinstance(billing, dict): return billing.get("provider"), billing.get("basis")
    except (OSError, json.JSONDecodeError):
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
    if "schema_version" in value and value.get("schema_version") != 1:
        raise AssignmentError("source_evidence schema_version must be 1")
    if value.get("repository") != repository or value.get("branch") != branch or value.get("sha") != sha:
        raise AssignmentError("source_evidence does not match the assigned source")
    if value.get("verified") is not True:
        raise AssignmentError("source_evidence is not verified")
    result = {"repository": repository, "branch": branch, "sha": sha, "verified": True}
    if "schema_version" in value: result = {"schema_version": 1, **result}
    return result


# --- assignment resolution ----------------------------------------------------------------

def canonical_digest(value: dict) -> str:
    payload = {key: item for key, item in value.items() if key != "assignment_digest"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
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
    if not IDENTIFIER_RE.fullmatch(task_id or ""):
        raise AssignmentError(f"invalid task_id {task_id!r}")
    if not IDENTIFIER_RE.fullmatch(project_id or ""):
        raise AssignmentError(f"invalid project_id {project_id!r}")
    if role not in ROLES:
        raise AssignmentError(f"role must be one of {sorted(ROLES)}")
    if not _nonempty(source_repository):
        raise AssignmentError("source_repository must be a nonempty string")
    source_branch = canonical_branch(source_branch, "source_branch")
    if not SHA_RE.fullmatch(source_sha or ""):
        raise AssignmentError(f"invalid source_sha {source_sha!r}")
    if seed_manifest_digest is not None and not DIGEST_RE.fullmatch(seed_manifest_digest):
        raise AssignmentError(f"invalid seed_manifest_digest {seed_manifest_digest!r}")
    if not (engine in engine_contract.BUILTIN_ENGINES or engine_contract.plugin_engine_name_ok(engine)):
        raise AssignmentError(f"invalid engine {engine!r}")
    if not _nonempty(provider) or not PROVIDER_RE.fullmatch(provider):
        raise AssignmentError(f"invalid provider {provider!r}")
    pool = None
    if capacity_pool is not None:
        if not IDENTIFIER_RE.fullmatch(capacity_pool):
            raise AssignmentError(f"invalid capacity_pool {capacity_pool!r}")
        # Referencing a pool must resolve; a caller that names one is asserting it is real.
        pool = load_capacity_pool(capacity_pool_dir or capacity_pool_dir_default(), capacity_pool)
    if model is not None and not _nonempty(model):
        raise AssignmentError("model must be null or a nonempty string")
    params = dict(model_parameters or {})
    for key, item in params.items():
        if not MODEL_PARAM_KEY_RE.fullmatch(key) or not isinstance(item, str):
            raise AssignmentError(f"invalid model parameter {key!r}")
    if not _nonempty(host):
        raise AssignmentError("host must be a nonempty string")
    if sandbox_profile not in SANDBOX_PROFILES:
        raise AssignmentError(f"sandbox_profile must be one of {sorted(SANDBOX_PROFILES)}")
    if network_profile not in NETWORK_PROFILES:
        raise AssignmentError(f"network_profile must be one of {sorted(NETWORK_PROFILES)}")
    normalized_allowed_paths = _normalize_allowed_paths(allowed_paths)
    if gate_digest is not None and not DIGEST_RE.fullmatch(gate_digest):
        raise AssignmentError(f"invalid gate_digest {gate_digest!r}")
    if not SLUG_RE.fullmatch(publication_policy or ""):
        raise AssignmentError(f"invalid publication_policy {publication_policy!r}")
    default_branch = canonical_branch(default_branch, "default_branch")
    integration_branch = canonical_branch(integration_branch, "integration_branch")
    if default_branch == integration_branch:
        raise AssignmentError("default_branch and integration_branch must differ")
    source_evidence = canonical_source_evidence(
        source_evidence or {"repository": source_repository, "branch": source_branch,
                            "sha": source_sha, "verified": True},
        source_repository, source_branch, source_sha)
    if billing_basis is not None and billing_basis not in CAPACITY_POOL_BILLING_BASES:
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
        "created_at": created_at or now_iso(),
    }
    value["assignment_digest"] = canonical_digest(value)
    return value


def capacity_pool_dir_default() -> Path:
    return capacity_pool_dir()


# --- persistence ----------------------------------------------------------------------

def assignment_path(root: Path, task_id: str, digest: str) -> Path:
    if not IDENTIFIER_RE.fullmatch(task_id or "") or not DIGEST_RE.fullmatch(digest or ""):
        raise AssignmentError("assignment path identity is not canonical")
    return root / task_id / f"{digest}.json"


def index_path(root: Path) -> Path:
    return root / "index.jsonl"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, str(path))
        if os.name != "nt":
            dfd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def persist_assignment(root: Path, value: dict) -> Path:
    validate_assignment(value, require_source_evidence=True)
    root = Path(root)
    if root.exists() and root.is_symlink():
        raise AssignmentError("assignment root must not be a symlink")
    if index_path(root).is_symlink():
        raise AssignmentError("assignment index must not be a symlink")
    root.mkdir(parents=True, exist_ok=True)
    task_dir = root / value["task_id"]
    if task_dir.exists() and task_dir.is_symlink():
        raise AssignmentError("assignment task directory must not be a symlink")
    task_dir.mkdir(exist_ok=True)
    path = assignment_path(root, value["task_id"], value["assignment_digest"])
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.is_symlink():
        raise AssignmentError("assignment record must not be a symlink")
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing != encoded:
            raise AssignmentError(
                f"assignment {path} already exists with different content "
                "(content-address collision — refusing to overwrite an immutable record)"
            )
    else:
        # A rename can replace a concurrent writer's immutable record. Install via a hard link
    # from a fully fsynced temporary file: link(2) is create-if-absent, so the loser can only
    # compare the winner's bytes and never overwrite them. Windows falls back to O_EXCL.
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(task_dir))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(encoded); handle.flush(); os.fsync(handle.fileno())
            try:
                os.link(name, path)
                installed = True
            except FileExistsError:
                installed = False
            if not installed:
                if path.is_symlink():
                    raise AssignmentError("assignment record must not be a symlink")
                existing = path.read_text(encoding="utf-8")
                if existing != encoded:
                    raise AssignmentError("content-address collision — refusing to overwrite immutable assignment")
        finally:
            if os.path.exists(name):
                os.unlink(name)
    if os.name != "nt":
        dfd = os.open(task_dir, os.O_RDONLY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    try:
        from jsonl_durable import append_jsonl  # local import: only needed on the write path
        append_jsonl(
            index_path(root),
            {
                "schema_version": SCHEMA_VERSION, "assignment_digest": value["assignment_digest"],
                "task_id": value["task_id"], "role": value["role"], "engine": value["engine"],
                "provider": value["provider"], "capacity_pool": value["capacity_pool"],
                "host": value["host"], "created_at": value["created_at"],
            },
            dedupe_field="assignment_digest", dedupe_value=value["assignment_digest"],
        )
    except Exception as exc:
        raise AssignmentError(f"assignment index append failed: {exc}") from exc
    return path


def load_assignment(root: Path, task_id: str, digest: str) -> dict | None:
    try:
        path = assignment_path(root, task_id, digest)
    except AssignmentError:
        return None
    if Path(root).is_symlink() or (Path(root) / task_id).is_symlink():
        return None
    if path.is_symlink() or not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    return value


def validate_assignment(value: object, require_source_evidence: bool = False) -> dict:
    if not isinstance(value, dict):
        raise AssignmentError("assignment is not an object")
    missing = {"schema_version", "task_id", "project_id", "role", "source_repository", "source_branch",
               "source_sha", "seed_manifest_digest", "engine", "provider", "capacity_pool", "model",
               "model_parameters", "host", "sandbox_profile", "network_profile", "allowed_paths",
               "gate_digest", "publication_policy", "created_at", "assignment_digest"} - value.keys()
    if missing:
        raise AssignmentError("assignment missing required field(s): " + ", ".join(sorted(missing)))
    if value.get("schema_version") != SCHEMA_VERSION or set(value) - ASSIGNMENT_FIELDS:
        raise AssignmentError("assignment schema/runtime mismatch")
    if require_source_evidence:
        required_phase3 = {"source_evidence", "billing_basis", "metered_approved", "default_branch", "integration_branch"}
        missing_phase3 = required_phase3 - value.keys()
        if missing_phase3:
            raise AssignmentError("Phase 3 assignment missing: " + ", ".join(sorted(missing_phase3)))
    if not IDENTIFIER_RE.fullmatch(str(value.get("task_id") or "")) or not IDENTIFIER_RE.fullmatch(str(value.get("project_id") or "")):
        raise AssignmentError("assignment identity is not canonical")
    if value.get("role") not in ROLES or not _nonempty(value.get("source_repository")):
        raise AssignmentError("assignment role or source repository is invalid")
    source_sha = value.get("source_sha")
    if not SHA_RE.fullmatch(source_sha or ""):
        raise AssignmentError("assignment source_sha is invalid")
    source_branch = canonical_branch(value.get("source_branch"), "source_branch")
    if require_source_evidence or "source_evidence" in value:
        canonical_source_evidence(value.get("source_evidence"), value["source_repository"], source_branch, source_sha)
    _normalize_allowed_paths(value.get("allowed_paths"))
    if value.get("billing_basis") not in (None, *CAPACITY_POOL_BILLING_BASES):
        raise AssignmentError("assignment billing_basis is invalid")
    if "metered_approved" in value and not isinstance(value.get("metered_approved"), bool):
        raise AssignmentError("assignment metered_approved must be boolean")
    if value.get("billing_basis") == "metered" and value.get("metered_approved") is not True:
        raise AssignmentError("metered assignment is not approved")
    canonical_branch(value.get("default_branch"), "default_branch")
    canonical_branch(value.get("integration_branch"), "integration_branch")
    if canonical_digest(value) != value.get("assignment_digest"):
        raise AssignmentError("assignment digest does not match its content")
    return value


# --- CLI --------------------------------------------------------------------------------

def _parse_model_params(pairs: list[str]) -> dict:
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
        value = resolve_assignment(
            task_id=args.task_id, project_id=args.project_id, role=args.role,
            source_repository=args.source_repository, source_branch=args.source_branch,
            source_sha=args.source_sha, seed_manifest_digest=args.seed_manifest_digest,
            engine=args.engine, provider=args.provider, capacity_pool=args.capacity_pool,
            model=args.model, model_parameters=params, host=args.host,
            sandbox_profile=args.sandbox_profile, network_profile=args.network_profile,
            allowed_paths=_split_paths(args.allowed_paths), gate_digest=args.gate_digest,
            publication_policy=args.publication_policy, capacity_pool_dir=pool_dir,
            source_evidence=(json.loads(Path(args.source_evidence_file).read_text(encoding="utf-8"))
                             if args.source_evidence_file else None),
            billing_basis=args.billing_basis, metered_approved=args.metered_approved,
            default_branch=args.default_branch, integration_branch=args.integration_branch,
        )
        if not args.no_persist:
            persist_assignment(root, value)
    except (AssignmentError, OSError, json.JSONDecodeError) as exc:
        diag(str(exc))
        return 2
    if args.out:
        try:
            _atomic_write(Path(args.out), json.dumps(value, indent=2, sort_keys=True) + "\n")
        except OSError as exc:
            diag(f"failed to write --out copy: {exc}")
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
    args = parse_args(sys.argv[1:])
    handlers = {"resolve": command_resolve, "show": command_show}
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())

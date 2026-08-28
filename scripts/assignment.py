"""Strict, deterministic assignment identity for Phase 5 run evidence.

The assignment is controller-authored once, then treated as immutable.  Evidence does not
trust a digest supplied by a worker or caller: it loads this record, validates the fields and
recomputes the digest from canonical JSON.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

ID_RE = re.compile(r"[a-z][a-z0-9-]{1,63}\Z")
SHA_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
VALUE_RE = re.compile(r"[a-z][a-z0-9.-]{1,127}\Z")
BRANCH_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,255}\Z")
SANDBOXES = frozenset({
    "strict-linux", "workspace-linux", "vendor-cloud", "remote-linux",
    "windows-interactive", "trusted-interactive", "account-shared-supervisor",
})
REQUIRED = frozenset({
    "task_id", "project_id", "source_repository", "source_branch", "source_sha",
    "seed_manifest_digest", "engine", "provider", "capacity_pool", "model", "host",
    "sandbox_profile", "network_profile", "allowed_paths", "gate_digest",
    "publication_policy",
})


class AssignmentError(ValueError):
    pass


def _text(value: Any, name: str, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in value):
        raise AssignmentError(f"{name} must be a nonempty control-free string")
    if pattern is not None and not pattern.fullmatch(value):
        raise AssignmentError(f"{name} has an invalid value")
    return value


def _canonical_source(value: Any) -> str:
    raw = _text(value, "source_repository")
    path = Path(raw)
    if not path.is_absolute():
        raise AssignmentError("source_repository must be absolute")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise AssignmentError("source_repository is unavailable") from exc
    if not resolved.is_dir():
        raise AssignmentError("source_repository is not a directory")
    return os.path.normcase(str(resolved))


def _pool_policy(pool: str) -> dict[str, Any]:
    path = Path(__file__).resolve().parent / "capacity-pools.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        pools = value["pools"]
        policy = pools[pool]
    except (OSError, ValueError, KeyError, TypeError):
        raise AssignmentError("capacity_pool is not a declared local pool")
    if not isinstance(policy, dict):
        raise AssignmentError("capacity_pool policy is invalid")
    return policy


def validate_assignment(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AssignmentError("assignment must be an object")
    missing = REQUIRED - value.keys()
    if missing:
        raise AssignmentError("assignment is missing: " + ", ".join(sorted(missing)))
    extra = value.keys() - (REQUIRED | {"role_assignments"})
    if extra:
        raise AssignmentError("assignment has unknown fields: " + ", ".join(sorted(extra)))
    for field in ("task_id", "project_id", "engine", "capacity_pool", "host", "network_profile"):
        _text(value[field], field, ID_RE if field in {"task_id", "project_id", "capacity_pool", "host"} else VALUE_RE)
    _text(value["provider"], "provider", VALUE_RE)
    source = _canonical_source(value["source_repository"])
    branch = _text(value["source_branch"], "source_branch", BRANCH_RE)
    if ".." in branch or branch.endswith("/") or branch.endswith("."):
        raise AssignmentError("source_branch is unsafe")
    sha = _text(value["source_sha"], "source_sha", SHA_RE)
    seed = value["seed_manifest_digest"]
    if not isinstance(seed, str) or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in seed) \
            or (seed and not SHA_RE.fullmatch(seed)):
        raise AssignmentError("seed_manifest_digest is invalid")
    _text(value["model"], "model") if value["model"] else None
    sandbox = _text(value["sandbox_profile"], "sandbox_profile")
    if sandbox not in SANDBOXES:
        raise AssignmentError("sandbox_profile is unsupported")
    paths = value["allowed_paths"]
    if not isinstance(paths, list) or not paths or any(
        not isinstance(item, str) or not item or item != "." and item.startswith(("/", "\\"))
        or any(part in {"", ".", ".."} for part in item.replace("\\", "/").split("/"))
        or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in item) for item in paths
    ):
        raise AssignmentError("allowed_paths is not a safe nonempty relative-path list")
    _text(value["gate_digest"], "gate_digest", SHA_RE)
    _text(value["publication_policy"], "publication_policy", VALUE_RE)
    policy = _pool_policy(value["capacity_pool"])
    if value["provider"] not in policy.get("providers", []):
        raise AssignmentError("capacity_pool is not authorized for provider")
    if value["host"] not in policy.get("hosts", []):
        raise AssignmentError("capacity_pool is not authorized for host")
    if sandbox not in policy.get("sandbox_profiles", []):
        raise AssignmentError("capacity_pool is not authorized for sandbox profile")
    roles = value.get("role_assignments")
    if roles is not None:
        if not isinstance(roles, dict) or set(roles) - {"implementer", "verifier"}:
            raise AssignmentError("role_assignments is invalid")
        for role, spec in roles.items():
            if not isinstance(spec, dict):
                raise AssignmentError(f"role_assignments.{role} is invalid")
            for field in ("engine", "provider", "model"):
                _text(spec.get(field), f"role_assignments.{role}.{field}")
            if spec["provider"] not in policy.get("providers", []):
                raise AssignmentError(f"capacity_pool is not authorized for role {role} provider")
    normalized = dict(value)
    normalized["source_repository"] = source
    normalized["source_branch"] = branch
    normalized["source_sha"] = sha
    return normalized


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    normalized = validate_assignment(value)
    return hashlib.sha256(canonical_bytes(normalized)).hexdigest()


def load_assignment(path: str | Path) -> tuple[dict[str, Any], str]:
    candidate = Path(path)
    try:
        info = os.lstat(candidate)
    except OSError as exc:
        raise AssignmentError("assignment file is unreadable") from exc
    if candidate.is_symlink() or not candidate.is_file() \
            or bool(getattr(info, "st_file_attributes", 0) & 0x400):
        raise AssignmentError("assignment file must be a regular non-symlink file")
    if os.name != "nt" and stat.S_IMODE(info.st_mode) & 0o022:
        raise AssignmentError("assignment file is writable by group or other")
    try:
        value = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssignmentError("assignment file is unreadable") from exc
    normalized = validate_assignment(value)
    return normalized, hashlib.sha256(canonical_bytes(normalized)).hexdigest()

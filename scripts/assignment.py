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
import subprocess
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
    "sandbox_profile", "network_profile", "network_endpoints", "allowed_paths", "gate_digest",
    "gate_contract", "role_assignments", "publication_policy",
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
    probe = subprocess.run(
        ["git", "-C", str(resolved), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=False,
    )
    if probe.returncode != 0:
        raise AssignmentError("source_repository is not a canonical Git repository")
    try:
        git_root = Path(probe.stdout.strip()).resolve(strict=True)
    except OSError as exc:
        raise AssignmentError("source_repository Git root is unavailable") from exc
    if git_root != resolved:
        raise AssignmentError("source_repository must be the canonical Git worktree root")
    return os.path.normcase(str(resolved))


def _git_commit_exists(repo: str, sha: str) -> None:
    result = subprocess.run(
        ["git", "-C", repo, "cat-file", "-e", f"{sha}^{{commit}}"],
        capture_output=True, check=False,
    )
    if result.returncode != 0:
        raise AssignmentError("source_sha is not an existing commit in source_repository")
    resolved = subprocess.run(
        ["git", "-C", repo, "rev-parse", "--verify", f"{sha}^{{commit}}"],
        capture_output=True, text=True, check=False,
    )
    if resolved.returncode != 0 or resolved.stdout.strip().lower() != sha.lower():
        raise AssignmentError("source_sha is not the exact immutable commit identity")


def _provider_profiles() -> dict[str, Any]:
    path = Path(__file__).resolve().parent / "provider-egress-profiles.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        profiles = value["profiles"]
        if not isinstance(profiles, dict):
            raise TypeError
        return profiles
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise AssignmentError("provider profile registry is invalid") from exc


def _engine_binding(engine: str) -> tuple[str, str, list[str]]:
    if engine == "claude":
        provider, profile = "anthropic-claude-code", "anthropic"
    elif engine == "none":
        return "none", "none", []
    else:
        path = Path(__file__).resolve().parent / "engines" / f"{engine}.json"
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            provider = manifest["billing"]["provider"]
            profile = manifest["network"]["profile"]
            endpoints = manifest["network"]["endpoints"]
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise AssignmentError(f"engine manifest binding is unavailable for {engine}") from exc
        if not isinstance(provider, str) or not isinstance(profile, str) or not isinstance(endpoints, list):
            raise AssignmentError(f"engine manifest binding is invalid for {engine}")
        return provider, profile, endpoints
    profiles = _provider_profiles()
    try:
        endpoints = profiles[profile]["endpoints"]
    except (KeyError, TypeError) as exc:
        raise AssignmentError(f"provider profile is unavailable for {engine}") from exc
    return provider, profile, endpoints


def _validate_binding(engine: str, provider: str, profile: str, endpoints: Any, where: str) -> None:
    expected_provider, expected_profile, expected_endpoints = _engine_binding(engine)
    if (provider, profile) != (expected_provider, expected_profile):
        raise AssignmentError(f"{where} engine/provider/network profile does not match its manifest")
    if not isinstance(endpoints, list) or endpoints != expected_endpoints:
        raise AssignmentError(f"{where} network endpoints do not match its manifest/profile")
    profiles = _provider_profiles()
    if profile != "none":
        try:
            profile_value = profiles[profile]
        except KeyError as exc:
            raise AssignmentError(f"{where} network profile is not declared") from exc
        if profile_value.get("provider") != provider or profile_value.get("endpoints") != endpoints:
            raise AssignmentError(f"{where} network profile/provider/endpoints disagree")


def _validate_gate_contract(value: Any, expected_digest: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"acceptance_sha256", "gate_files", "controller_gate_files"}:
        raise AssignmentError("gate_contract is not the validated gate contract")
    if not isinstance(value["acceptance_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", value["acceptance_sha256"]):
        raise AssignmentError("gate_contract acceptance digest is invalid")
    for field in ("gate_files", "controller_gate_files"):
        paths = value[field]
        if not isinstance(paths, dict):
            raise AssignmentError(f"gate_contract.{field} is invalid")
        for path, item_digest in paths.items():
            if not isinstance(path, str) or not path or "\\" in path or path.startswith("/") \
                    or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in path) \
                    or any(part in {"", ".", ".."} for part in path.split("/")) \
                    or not isinstance(item_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", item_digest):
                raise AssignmentError(f"gate_contract.{field} contains an unsafe entry")
    actual = hashlib.sha256(canonical_bytes(value)).hexdigest()
    if actual != expected_digest:
        raise AssignmentError("gate_digest does not hash the validated gate contract")
    return value


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
    provider = _text(value["provider"], "provider", VALUE_RE)
    source = _canonical_source(value["source_repository"])
    branch = _text(value["source_branch"], "source_branch", BRANCH_RE)
    if ".." in branch or branch.endswith("/") or branch.endswith("."):
        raise AssignmentError("source_branch is unsafe")
    sha = _text(value["source_sha"], "source_sha", SHA_RE)
    _git_commit_exists(source, sha)
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
    gate_digest = _text(value["gate_digest"], "gate_digest", SHA_RE)
    gate_contract = _validate_gate_contract(value["gate_contract"], gate_digest)
    _text(value["publication_policy"], "publication_policy", VALUE_RE)
    policy = _pool_policy(value["capacity_pool"])
    if value["provider"] not in policy.get("providers", []):
        raise AssignmentError("capacity_pool is not authorized for provider")
    if value["host"] not in policy.get("hosts", []):
        raise AssignmentError("capacity_pool is not authorized for host")
    if sandbox not in policy.get("sandbox_profiles", []):
        raise AssignmentError("capacity_pool is not authorized for sandbox profile")
    roles = value["role_assignments"]
    if not isinstance(roles, dict) or set(roles) != {"implementer", "verifier"}:
        raise AssignmentError("role_assignments must bind implementer and verifier")
    top_endpoints = value["network_endpoints"]
    if not isinstance(top_endpoints, list) \
            or any(not isinstance(item, str) or not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", item) for item in top_endpoints) \
            or len(set(top_endpoints)) != len(top_endpoints):
        raise AssignmentError("network_endpoints is invalid")
    _validate_binding(value["engine"], provider, value["network_profile"], top_endpoints, "implementer")
    for role, spec in roles.items():
        if not isinstance(spec, dict) or set(spec) != {"engine", "provider", "model", "network_profile", "network_endpoints"}:
            raise AssignmentError(f"role_assignments.{role} is invalid")
        role_engine = _text(spec["engine"], f"role_assignments.{role}.engine", VALUE_RE)
        role_provider = _text(spec["provider"], f"role_assignments.{role}.provider", VALUE_RE)
        role_profile = _text(spec["network_profile"], f"role_assignments.{role}.network_profile", VALUE_RE)
        _text(spec["model"], f"role_assignments.{role}.model")
        role_endpoints = spec["network_endpoints"]
        _validate_binding(role_engine, role_provider, role_profile, role_endpoints, f"role_assignments.{role}")
        if role_provider not in policy.get("providers", []):
            raise AssignmentError(f"capacity_pool is not authorized for role {role} provider")
    normalized = dict(value)
    normalized["source_repository"] = source
    normalized["source_branch"] = branch
    normalized["source_sha"] = sha
    normalized["gate_contract"] = gate_contract
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

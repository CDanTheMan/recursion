#!/usr/bin/env python3
"""Recursion v2 repository, branch, and candidate contracts.

This module is deliberately independent of the worker and publisher processes.  It admits a
task against one exact source commit, verifies an externally-produced candidate, imports that
candidate into a canonical task ref with compare-and-swap semantics, and produces a read-only
integration plan while holding a per-repository serialization lock.

No function in this module pushes a remote or updates a default/integration ref.
"""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
import hashlib
import hmac
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterator


OID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$")
SCHEMA = "recursion-project-repository-contract/v2"
_DEFAULT_CONTROLLER_KEY_PATH = Path(__file__).resolve().parents[1] / "state" / "secrets" / "verifier-receipt.key"
CONTROLLER_KEY_PATH = _DEFAULT_CONTROLLER_KEY_PATH
OUTCOMES = {
    "current-compatible", "stale-reviewable", "stale-rebase-required", "invalidated",
    "source-unavailable", "unauthorized-result",
}


class ContractError(ValueError):
    """A fail-closed contract refusal."""

    def __init__(self, message: str, code: str = "contract-invalid") -> None:
        super().__init__(message)
        self.code = code


def _json_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _normalized_path(value: object, *, field: str = "path") -> str:
    if not isinstance(value, str) or not value or any(ord(char) < 32 for char in value):
        raise ContractError(f"{field} must be a non-empty path")
    if "\\" in value or value != value.strip() or value != "." and (
        value.startswith("./") or value.endswith("/") or "//" in value
    ):
        raise ContractError(f"{field} is not in canonical repository-relative form")
    if re.match(r"^[A-Za-z]:", value):
        raise ContractError(f"{field} must be repository-relative")
    path = PurePosixPath(value)
    raw_parts = value.split("/")
    if path.is_absolute() or value != "." and any(part in {".", ".."} for part in raw_parts):
        raise ContractError(f"{field} is unsafe")
    return "." if str(path) in {"", "."} else str(path)


def _normalized_paths(values: object, *, field: str) -> list[str]:
    if not isinstance(values, list) or not values:
        raise ContractError(f"{field} must be a non-empty string array")
    normalized = [_normalized_path(value, field=field) for value in values]
    if len(set(normalized)) != len(normalized):
        raise ContractError(f"{field} must contain unique normalized paths")
    return normalized


def _path_subset(child: str, parent: str) -> bool:
    child_path = PurePosixPath(child)
    parent_path = PurePosixPath(parent)
    return parent == "." or child == parent or parent_path in child_path.parents


def _gate_digest(contract: dict[str, Any]) -> str:
    declared = contract.get("gate_digest")
    computed = _json_digest(contract["gate_commands"])
    if declared is not None:
        if not isinstance(declared, str) or not re.fullmatch(r"[0-9a-f]{64}", declared):
            raise ContractError("gate_digest must be a lowercase SHA-256 digest")
        if declared != computed:
            raise ContractError("gate_digest does not match gate_commands")
        return declared
    return computed


def _require_path_subset(child: list[str], parent: list[str], *, field: str) -> list[str]:
    if any(not any(_path_subset(path, root) for root in parent) for path in child):
        raise ContractError(f"{field} widens the descriptor allowed_paths")
    return child


def _contains_legacy_chiron(value: object) -> bool:
    if isinstance(value, (list, tuple, set)):
        return any(_contains_legacy_chiron(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_legacy_chiron(item) for item in value.values())
    if not isinstance(value, str):
        return False
    normalized = re.sub(r"/{2,}", "/", value.replace("\\", "/")).lower()
    normalized = re.sub(r"/\./", "/", normalized)
    normalized = re.sub(r"(^|[\s'\"=:])\./", r"\1", normalized)
    return re.search(r"(?<![a-z0-9_])apps/chiron(?![a-z0-9_])", normalized) is not None


def _valid_git_ref(value: object) -> bool:
    if not isinstance(value, str) or not value or "*" in value \
            or any(ord(char) < 32 for char in value):
        return False
    try:
        result = subprocess.run(
            ["git", "check-ref-format", "--branch", value], stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def _valid_git_pattern(value: object) -> bool:
    if not isinstance(value, str) or not value or any(char in value for char in "?["):
        return False
    probe = value.replace("*", "probe")
    return _valid_git_ref(probe)


def _valid_gate_command(value: object) -> bool:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096 \
            or "\x00" in value or any(ord(char) < 32 and char != "\t" for char in value):
        return False
    validator = Path(__file__).with_name("validate-gate.py")
    try:
        result = subprocess.run(
            # Repository descriptors bind their gate command digest; gate-file ownership is a
            # separate contract.  Use an empty worker scope here so validator parsing does not
            # require a task-level gate_files declaration.
            [sys.executable, str(validator), "--acceptance", value, "--allowed-paths", "",
             "--strict-direct"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {
        key: value for key, value in os.environ.items()
        if key in {"PATH", "HOME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "SystemRoot", "WINDIR"}
    }
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"})
    return subprocess.run(
        ["git", "--no-replace-objects", "-c", f"safe.directory={repo}", "-C", str(repo), *args],
        env=env, stdin=subprocess.DEVNULL, text=True, capture_output=True, timeout=30, check=False,
    )


def _oid(repo: Path, ref: str, *, missing: str = "source-unavailable") -> str:
    result = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
    value = result.stdout.strip()
    if result.returncode or not OID.fullmatch(value):
        raise ContractError(f"commit is unavailable: {ref}", missing)
    return value


def _ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    result = _git(repo, "merge-base", "--is-ancestor", ancestor, descendant)
    if result.returncode not in (0, 1):
        raise ContractError("Git ancestry could not be measured", "verification-unavailable")
    return result.returncode == 0


def _git_dir(repo: Path) -> Path:
    result = _git(repo, "rev-parse", "--path-format=absolute", "--git-dir")
    if result.returncode:
        raise ContractError("repository Git directory could not be resolved", "repository-unavailable")
    path = Path(result.stdout.strip()).resolve()
    if not path.is_dir():
        raise ContractError("repository Git directory is unavailable", "repository-unavailable")
    return path


def _require_descriptor_repository(contract: dict[str, Any], repo: Path) -> Path:
    """Bind every operation to the descriptor's canonical checkout, not a caller-selected clone."""
    try:
        supplied = Path(repo).expanduser().resolve(strict=True)
        declared = Path(contract["repo"]).expanduser().resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ContractError("project repository is unavailable", "repository-unavailable") from exc
    if supplied != declared or not supplied.is_dir():
        raise ContractError("supplied repository does not match project descriptor", "unauthorized-result")
    return supplied


def _contract_fields(contract: dict[str, Any]) -> dict[str, Any]:
    """Validate and return the additive v2 fields from a v1-compatible descriptor."""
    required = {
        "id", "repo", "default_branch", "integration_branch", "task_branch_pattern",
        "external_branch_patterns", "publication_policy", "source_policy", "allowed_paths",
        "gate_commands", "eligible_hosts", "eligible_pools",
    }
    missing = sorted(key for key in required if key not in contract)
    if missing:
        raise ContractError(f"project contract is missing fields: {', '.join(missing)}")
    if not isinstance(contract["id"], str) or not IDENT.fullmatch(contract["id"]):
        raise ContractError("project id is invalid")
    if not isinstance(contract["repo"], str) or not contract["repo"].strip() \
            or any(ord(char) < 32 for char in contract["repo"]) \
            or contract["repo"] != contract["repo"].strip():
        raise ContractError("project repo must be a non-empty string")
    for key in ("default_branch", "integration_branch"):
        value = contract[key]
        if not isinstance(value, str) or not BRANCH.fullmatch(value) or value.startswith("/") \
                or not _valid_git_ref(value):
            raise ContractError(f"{key} is invalid")
    if contract["default_branch"] == contract["integration_branch"]:
        raise ContractError("default and integration branches must differ")
    pattern = contract["task_branch_pattern"]
    if not isinstance(pattern, str) or pattern.count("{task_id}") != 1:
        raise ContractError("task_branch_pattern must contain exactly one {task_id}")
    probe = pattern.replace("{task_id}", "probe")
    if not BRANCH.fullmatch(probe) or not _valid_git_ref(probe) \
            or probe in {contract["default_branch"], contract["integration_branch"]}:
        raise ContractError("task_branch_pattern is unsafe")
    patterns = contract["external_branch_patterns"]
    if not isinstance(patterns, list) or not patterns or any(
        not isinstance(item, str) or not item or item in {"*", "**"} or not _valid_git_pattern(item)
        for item in patterns
    ) or len(set(patterns)) != len(patterns):
        raise ContractError("external_branch_patterns must be a non-empty restricted list")
    task_probe = pattern.replace("{task_id}", "probe")
    task_prefix, task_suffix = pattern.split("{task_id}")
    if any(fnmatch.fnmatchcase(task_probe, item)
           or item.startswith(task_prefix)
           or task_prefix.startswith(item.rstrip("*")) for item in patterns):
        raise ContractError("external branch namespace overlaps task branch namespace")
    if contract["publication_policy"] != "verified-integration-only":
        raise ContractError("unsupported publication policy")
    if contract["source_policy"] != "exact-sha":
        raise ContractError("unsupported source policy")
    contract["allowed_paths"] = _normalized_paths(contract["allowed_paths"], field="allowed_paths")
    for key in ("gate_commands", "eligible_hosts", "eligible_pools"):
        values = contract[key]
        if not isinstance(values, list) or not values \
                or any(not isinstance(item, str) or not item or any(
                    ord(char) < 32 and (key != "gate_commands" or char != "\t") for char in item
                ) for item in values) \
                or len(set(values)) != len(values):
            raise ContractError(f"{key} must be a string array")
    if any(not _valid_gate_command(item) for item in contract["gate_commands"]):
        raise ContractError("gate_commands must contain non-vacuous commands")
    _gate_digest(contract)
    return contract


def validate_project_descriptor(contract: dict[str, Any]) -> dict[str, Any]:
    """Validate an active descriptor without changing its v1 representation."""
    if not isinstance(contract, dict):
        raise ContractError("project descriptor must be an object")
    return _contract_fields(contract)


def task_branch(contract: dict[str, Any], task_id: str) -> str:
    validate_project_descriptor(contract)
    if not isinstance(task_id, str) or not IDENT.fullmatch(task_id):
        raise ContractError("task id is invalid")
    result = contract["task_branch_pattern"].replace("{task_id}", task_id)
    if not BRANCH.fullmatch(result) or not _valid_git_ref(result) or result in {
        contract["default_branch"], contract["integration_branch"]
    }:
        raise ContractError("resolved task branch is unsafe")
    return result


def branch_kind(contract: dict[str, Any], branch: str) -> str:
    """Return a branch namespace, refusing default and integration as execution targets."""
    validate_project_descriptor(contract)
    if not isinstance(branch, str) or not BRANCH.fullmatch(branch) or not _valid_git_ref(branch):
        raise ContractError("branch name is invalid", "unauthorized-result")
    if branch == contract["default_branch"]:
        raise ContractError("executor may not target the default branch", "unauthorized-result")
    if branch == contract["integration_branch"]:
        raise ContractError("executor may not target the integration branch", "unauthorized-result")
    # A resolved task branch is checked by constructing it from the task id.  This avoids
    # accepting arbitrary refs under a broad prefix when a project chose a custom pattern.
    prefix, suffix = contract["task_branch_pattern"].split("{task_id}")
    if branch.startswith(prefix) and branch.endswith(suffix):
        task_id = branch[len(prefix):len(branch) - len(suffix) if suffix else None]
        if task_id and IDENT.fullmatch(task_id):
            return "task"
    if any(fnmatch.fnmatchcase(branch, pattern) for pattern in contract["external_branch_patterns"]):
        return "external"
    raise ContractError("branch is outside the project execution namespaces", "unauthorized-result")


def _path_allowed(path: str, allowed: list[str]) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        return False
    normalized = PurePosixPath(path)
    if normalized.is_absolute() or any(part in {".", ".."} for part in normalized.parts):
        return False
    for root in allowed:
        root_path = PurePosixPath(root.rstrip("/"))
        if root == "." or normalized == root_path or root_path in normalized.parents:
            return True
    return False


def _tree_entries(repo: Path, commit: str) -> dict[str, tuple[str, str, str]]:
    """Read the candidate tree, retaining modes so symlink/submodule escapes cannot hide."""
    try:
        result = _git(repo, "ls-tree", "-r", "-t", "-z", "--full-tree", commit)
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        raise ContractError("candidate tree could not be inspected", "verification-unavailable") from exc
    if result.returncode:
        raise ContractError("candidate tree could not be inspected", "verification-unavailable")
    entries: dict[str, tuple[str, str, str]] = {}
    folded_paths: set[str] = set()
    for record in result.stdout.split("\x00"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition("\t")
        fields = metadata.split()
        if not separator or len(fields) != 3:
            raise ContractError("candidate tree entry is malformed", "unauthorized-result")
        mode, entry_type, oid = fields
        try:
            path = _normalized_path(raw_path, field="candidate tree path")
        except ContractError as exc:
            raise ContractError("candidate tree contains an unsafe path", "unauthorized-result") from exc
        if path in entries:
            raise ContractError("candidate tree contains duplicate paths", "unauthorized-result")
        # Git permits case-distinct names, but Windows and other case-insensitive consumers do
        # not.  Refuse an ambiguous tree before any symlink lookup can overwrite one entry with
        # another (for example, `src/Escape` and `src/escape`).
        folded_path = path.casefold()
        if folded_path in folded_paths:
            raise ContractError("candidate tree contains a case-folded path collision", "unauthorized-result")
        entries[path] = (mode, entry_type, oid)
        folded_paths.add(folded_path)
    return entries


def _resolve_tree_path(path: str, symlinks: dict[str, str]) -> str:
    """Resolve a Git-tree path lexically through symlinks, refusing escapes and cycles."""
    pending = list(PurePosixPath(path).parts)
    seen: set[str] = set()
    symlink_lookup = {name.casefold(): (name, target) for name, target in symlinks.items()}
    for _ in range(64):
        current = "/".join(pending) or "."
        link_record = symlink_lookup.get(current.casefold())
        if link_record is None:
            return current
        link, target = link_record
        folded_link = link.casefold()
        if folded_link in seen:
            raise ContractError("candidate tree contains a symlink cycle", "unauthorized-result")
        seen.add(folded_link)
        if not target or any(char in target for char in ("\x00", "\n", "\r", "\\")) \
                or target.startswith("/") \
                or re.match(r"^[A-Za-z]:", target):
            raise ContractError("candidate tree contains an unsafe symlink target", "unauthorized-result")
        base = list(PurePosixPath(link).parent.parts)
        for component in target.split("/"):
            if component in ("", "."):
                continue
            if component == "..":
                if not base:
                    raise ContractError("candidate symlink escapes the repository", "unauthorized-result")
                base.pop()
            else:
                base.append(component)
        pending = base
    raise ContractError("candidate tree contains excessive symlink indirection", "unauthorized-result")


def _inspect_candidate_tree(repo: Path, commit: str, allowed: list[str]) -> None:
    """Reject tree modes and symlink resolutions that evade the declared scope."""
    entries = _tree_entries(repo, commit)
    symlinks: dict[str, str] = {}
    for path, (mode, entry_type, oid) in entries.items():
        components = PurePosixPath(path).parts
        protected = {".git", "control-plane"}
        if any(component.casefold() in protected for component in components):
            raise ContractError("candidate tree contains a protected path", "unauthorized-result")
        if mode == "160000" or entry_type == "commit":
            raise ContractError("candidate tree contains an unsafe submodule entry", "unauthorized-result")
        if mode != "120000":
            continue
        try:
            target_result = _git(repo, "cat-file", "blob", oid)
        except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
            raise ContractError("candidate symlink target could not be read", "verification-unavailable") from exc
        if target_result.returncode:
            raise ContractError("candidate symlink target could not be read", "verification-unavailable")
        symlinks[path] = target_result.stdout.rstrip("\n")
    for path in symlinks:
        resolved = _resolve_tree_path(path, symlinks)
        components = PurePosixPath(resolved).parts
        if any(component.casefold() in protected for component in components) \
                or (_path_allowed(path, allowed) and not _path_allowed(resolved, allowed)):
            raise ContractError("candidate symlink escapes allowed_paths", "unauthorized-result")


def admit_task(contract: dict[str, Any], task: dict[str, Any], repo: Path, *, new_generation: bool = True) -> dict[str, Any]:
    """Admit a task only when its source branch currently names its exact source SHA."""
    validate_project_descriptor(contract)
    repo = _require_descriptor_repository(contract, repo)
    if not isinstance(task, dict):
        raise ContractError("task must be an object")
    for key in ("workdir", "acceptance", "goal", "gate_command", "seed", "repo",
                "source_repository", "source_branch", "source_sha", "target_branch"):
        if key in task and (not isinstance(task[key], str)
                            or any(ord(char) < 32 and char != "\t" for char in task[key])):
            raise ContractError(f"task field {key} must be a string")
    if "gate_commands" in task and (
        not isinstance(task["gate_commands"], list)
        or any(not isinstance(item, str) for item in task["gate_commands"])
    ):
        raise ContractError("task field gate_commands must be a string array")
    task_id = task.get("id")
    task_branch(contract, task_id)
    source_branch = task.get("source_branch")
    source_sha = task.get("source_sha")
    if new_generation and (not isinstance(source_branch, str) or not source_branch):
        raise ContractError("new task requires source_branch", "source-unavailable")
    if new_generation and (not isinstance(source_sha, str) or not OID.fullmatch(source_sha)):
        raise ContractError("new task requires an exact source_sha", "source-unavailable")
    if source_branch is None:
        source_branch = contract["default_branch"]
    if not isinstance(source_branch, str) or not BRANCH.fullmatch(source_branch):
        raise ContractError("source_branch is invalid", "source-unavailable")
    if source_branch in {contract["integration_branch"]}:
        raise ContractError("source_branch may not be the integration branch", "unauthorized-result")
    if not isinstance(source_sha, str) or not OID.fullmatch(source_sha):
        if new_generation:
            raise ContractError("source_sha is absent or malformed", "source-unavailable")
        return task
    observed = _oid(repo, f"refs/heads/{source_branch}")
    if observed != source_sha:
        raise ContractError("source branch moved after exact SHA admission", "source-unavailable")
    declared_repo = task.get("source_repository", task.get("repo", contract["repo"]))
    try:
        same_repo = Path(str(declared_repo)).expanduser().resolve(strict=False) == \
            Path(contract["repo"]).expanduser().resolve(strict=False)
    except (OSError, ValueError):
        same_repo = False
    if not same_repo:
        raise ContractError("task source repository does not match project", "unauthorized-result")
    allowed = _normalized_paths(task.get("allowed_paths", contract["allowed_paths"]), field="task allowed_paths")
    if new_generation and any(_contains_legacy_chiron(task.get(key)) for key in (
        "workdir", "acceptance", "gate_command", "gate_commands", "seed", "repo", "goal",
    )):
        raise ContractError("new task generation may not target apps/chiron", "unauthorized-result")
    if new_generation and any(_contains_legacy_chiron(item) for item in contract["gate_commands"]):
        raise ContractError("new task generation may not target apps/chiron", "unauthorized-result")
    if new_generation and any(_contains_legacy_chiron(item) for item in allowed):
        raise ContractError("new task generation may not target apps/chiron", "unauthorized-result")
    _require_path_subset(allowed, contract["allowed_paths"], field="task allowed_paths")
    target = task.get("target_branch")
    if target is not None:
        branch_kind(contract, target)
    return {**task, "source_branch": source_branch, "source_sha": source_sha,
            "source_repository": declared_repo, "task_branch": task_branch(contract, task_id)}


def _candidate_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        raise ContractError("candidate must be an object", "unauthorized-result")
    try:
        json.dumps(candidate, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ContractError("candidate contains non-serializable input", "unauthorized-result") from exc
    required = {"project_id", "task_id", "source_branch", "source_sha", "external_branch", "candidate_commit"}
    missing = sorted(key for key in required if key not in candidate)
    if missing:
        raise ContractError(f"candidate is missing fields: {', '.join(missing)}")
    return candidate


def _controller_key() -> bytes:
    # This is deliberately not configurable through caller environment.  The controller installs
    # the key at this fixed path with owner-only permissions; allowing a candidate to select a key
    # file would turn the receipt into self-attestation.
    try:
        key_path = Path(CONTROLLER_KEY_PATH)
        def is_link(path: Path) -> bool:
            if path.is_symlink():
                return True
            # Windows junctions/reparse points are not always reported by is_symlink().
            return bool(getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0) & 0x400)

        if is_link(key_path) or not key_path.is_file():
            raise OSError("controller key is not a regular file")
        stat = key_path.stat()
        if hasattr(os, "getuid") and stat.st_uid != os.getuid():
            raise OSError("controller key owner is not the current controller")
        if os.name != "nt" and stat.st_mode & 0o077:
            raise OSError("controller key permissions are too broad")
        for parent in (key_path.parent, *key_path.parent.parents):
            if parent == parent.parent:
                break
            if is_link(parent) or not parent.is_dir():
                raise OSError("controller key parent is not a safe directory")
            if os.name != "nt":
                parent_mode = parent.stat().st_mode
                # A sticky temporary root (for hermetic controller tests) may be world-writable;
                # every non-sticky ancestor must remain private to its owner.
                if parent_mode & 0o022 and not (parent_mode & 0o1000 and parent_mode & 0o002):
                    raise OSError("controller key parent is writable by group or world")
        if os.name == "nt" and key_path == _DEFAULT_CONTROLLER_KEY_PATH:
            # The fixed production path is additionally checked against the Windows ACL.  Parse
            # ACE lines (never the path header: a username in C:\Users\name\... is not an ACE),
            # deny broad principals and inherited write access, and require an exact current-user
            # full-control ACE on both the key and its parent directories.
            username = os.environ.get("USERNAME", "").casefold()

            def check_acl(path: Path, require_owner: bool) -> None:
                acl = subprocess.run(["icacls", str(path)], capture_output=True, text=True,
                                      stdin=subprocess.DEVNULL, timeout=10, check=False)
                if acl.returncode or not acl.stdout:
                    raise OSError("controller key ACL could not be inspected")
                entries: list[tuple[str, str]] = []
                for line in acl.stdout.splitlines():
                    match = re.match(r"^\s*([^:]+):((?:\([^)]+\))+.*)$", line)
                    if match:
                        entries.append((match.group(1).strip(), match.group(2).strip()))
                if not entries:
                    raise OSError("controller key ACL has no parseable ACEs")
                broad = {"everyone", "authenticated users", "users", "codexsandboxusers",
                         "builtin\\users", "nt authority\\authenticated users"}
                owner = False
                for principal, permissions in entries:
                    folded = principal.casefold()
                    if folded in broad or folded.endswith("\\users"):
                        raise OSError("controller key ACL grants broad access")
                    if "(i)" in permissions.casefold() and re.search(r"\((?:f|m|w|wd|ad)\)",
                                                                        permissions, re.I):
                        raise OSError("controller key ACL grants inherited write access")
                    if require_owner and username and folded.rsplit("\\", 1)[-1] == username \
                            and re.search(r"\((?:f|m)\)", permissions, re.I):
                        owner = True
                if require_owner and not owner:
                    raise OSError("controller key ACL is not owned by the controller")

            check_acl(key_path, True)
            for parent in (key_path.parent, *key_path.parent.parents):
                if parent == parent.parent:
                    break
                check_acl(parent, False)
        raw = key_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ContractError("controller verifier key is unavailable", "verification-unavailable") from exc
    if not raw or "\n" in raw or "\r" in raw:
        raise ContractError("controller verifier authentication is unavailable", "verification-unavailable")
    return raw.encode("utf-8")


def _run_independent_gates(contract: dict[str, Any], repo: Path, commit: str) -> None:
    """Run the descriptor's gates on an isolated detached worktree under controller control."""
    with tempfile.TemporaryDirectory(prefix="recursion-gate-") as raw:
        worktree = Path(raw) / "candidate"
        created = _git(repo, "worktree", "add", "--detach", "--quiet", str(worktree), commit)
        if created.returncode:
            raise ContractError("controller gate worktree could not be created", "verification-unavailable")
        try:
            env = {key: value for key, value in os.environ.items()
                   if key in {"PATH", "HOME", "USERPROFILE", "SystemRoot", "WINDIR"}}
            env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                        "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"})
            for command in contract["gate_commands"]:
                try:
                    result = subprocess.run(command, shell=True, cwd=worktree, env=env,
                                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, text=True, timeout=120, check=False)
                except (OSError, subprocess.TimeoutExpired) as exc:
                    raise ContractError("controller gate execution was unavailable", "verification-unavailable") from exc
                if result.returncode:
                    raise ContractError("independent controller gate failed", "unauthorized-result")
        finally:
            removed = _git(repo, "worktree", "remove", "--force", str(worktree))
            if removed.returncode:
                raise ContractError("controller gate worktree cleanup failed", "verification-unavailable")


def verify_candidate(contract: dict[str, Any], candidate: dict[str, Any], repo: Path,
                     *, receipt: dict[str, Any] | None = None,
                     allow_canonical: bool = False) -> dict[str, Any]:
    """Independently verify branch identity, source ancestry, scope, and verifier evidence."""
    validate_project_descriptor(contract)
    repo = _require_descriptor_repository(contract, repo)
    _candidate_payload(candidate)
    if "verification_receipt" in candidate or "verified" in candidate:
        raise ContractError("candidate may not supply verification authority", "unauthorized-result")
    if candidate["project_id"] != contract["id"]:
        raise ContractError("candidate project identity does not match", "unauthorized-result")
    task_branch(contract, candidate["task_id"])
    if candidate["source_branch"] != contract["default_branch"]:
        raise ContractError("candidate source branch is not the project source branch", "unauthorized-result")
    source = candidate["source_sha"]
    commit = candidate["candidate_commit"]
    if not isinstance(source, str) or not OID.fullmatch(source) or not isinstance(commit, str) or not OID.fullmatch(commit):
        raise ContractError("candidate commit identity is malformed", "unauthorized-result")
    external_branch = candidate["external_branch"]
    kind = branch_kind(contract, external_branch)
    if allow_canonical:
        expected_canonical = task_branch(contract, candidate["task_id"])
        if external_branch != expected_canonical or kind != "task":
            raise ContractError("canonical candidate must use its exact task branch", "unauthorized-result")
    elif kind != "external":
        raise ContractError("candidate must arrive on an external branch", "unauthorized-result")
    observed = _oid(repo, f"refs/heads/{candidate['external_branch']}", missing="unauthorized-result")
    if observed != commit:
        raise ContractError("external branch tip does not equal candidate commit", "unauthorized-result")
    resolved_source = _oid(repo, source, missing="source-unavailable")
    if resolved_source != source:
        raise ContractError("candidate source_sha is not the full canonical commit SHA", "unauthorized-result")
    _oid(repo, commit, missing="unauthorized-result")
    if not _ancestor(repo, source, commit):
        raise ContractError("candidate is not descended from its exact source SHA", "unauthorized-result")
    changed = _git(repo, "diff", "--name-only", source, commit)
    if changed.returncode:
        raise ContractError("candidate diff could not be measured", "verification-unavailable")
    paths = [item for item in changed.stdout.splitlines() if item]
    allowed = _normalized_paths(candidate.get("allowed_paths", contract["allowed_paths"]), field="candidate allowed_paths")
    _require_path_subset(allowed, contract["allowed_paths"], field="candidate allowed_paths")
    if any(not _path_allowed(path, allowed) for path in paths):
        raise ContractError("candidate changed a path outside allowed_paths", "unauthorized-result")
    _inspect_candidate_tree(repo, commit, allowed)
    if not isinstance(receipt, dict):
        raise ContractError("controller verification receipt is required separately", "unauthorized-result")
    _run_independent_gates(contract, repo, commit)
    _verify_receipt(contract, candidate, receipt, source, commit, paths, allowed, repo)
    result = dict(candidate)
    result["allowed_paths"] = allowed
    result["changed_paths"] = paths
    result["candidate_digest"] = _json_digest({key: result[key] for key in sorted(result) if key != "candidate_digest"})
    return result


def _verify_receipt(contract: dict[str, Any], candidate: dict[str, Any], receipt: dict[str, Any],
                    source: str, commit: str, paths: list[str], allowed: list[str], repo: Path) -> None:
    """Validate the controller-verifier receipt, including its tamper-evident digest binding."""
    required = {"schema", "project_id", "task_id", "source_sha", "candidate_commit", "diff_sha256",
                "scope_digest", "gate_digest", "verdict", "verifier", "provenance", "receipt_digest", "signature"}
    if not required.issubset(receipt):
        raise ContractError("controller verification receipt is incomplete", "unauthorized-result")
    if receipt.get("schema") != "recursion-controller-verifier-receipt/v1" \
            or receipt.get("verdict") != "pass" \
            or receipt.get("verifier") != "controller-verifier" \
            or receipt.get("provenance") != "recursion-controller":
        raise ContractError("controller verification receipt provenance is not trusted", "unauthorized-result")
    diff = _git(repo, "diff", "--binary", source, commit)
    if diff.returncode:
        raise ContractError("candidate diff could not be hashed", "verification-unavailable")
    expected = {
        "schema": receipt["schema"], "project_id": contract["id"], "task_id": candidate["task_id"],
        "source_sha": source, "candidate_commit": commit,
        "diff_sha256": hashlib.sha256(diff.stdout.encode()).hexdigest(),
        "scope_digest": _json_digest(allowed), "gate_digest": _gate_digest(contract),
        "verdict": "pass", "verifier": "controller-verifier", "provenance": "recursion-controller",
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise ContractError(f"controller receipt binding mismatch: {key}", "unauthorized-result")
    body = {key: receipt[key] for key in expected}
    if receipt.get("receipt_digest") != _json_digest(body):
        raise ContractError("controller verification receipt digest is invalid", "unauthorized-result")
    expected_signature = hmac.new(_controller_key(), receipt["receipt_digest"].encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(receipt.get("signature", "")), expected_signature):
        raise ContractError("controller verification receipt authentication is invalid", "unauthorized-result")


@contextlib.contextmanager
def _serialization_lock(repo: Path, timeout: float = 10.0) -> Iterator[None]:
    lock = _git_dir(repo) / "recursion-integration.lock"
    deadline = time.monotonic() + timeout
    while True:
        try:
            lock.mkdir(mode=0o700)
            (lock / "owner").write_text(str(os.getpid()), encoding="ascii")
            try:
                yield
            finally:
                try:
                    (lock / "owner").unlink()
                finally:
                    lock.rmdir()
            return
        except FileExistsError:
            # A coordinator crash can leave mkdir-based locks behind. Reclaim only when the
            # recorded owner is definitely gone; an unknown owner remains fail-closed.
            owner = lock / "owner"
            try:
                owner_pid = int(owner.read_text(encoding="ascii").strip())
            except (OSError, ValueError):
                owner_pid = 0
            if owner_pid and owner_pid != os.getpid():
                try:
                    os.kill(owner_pid, 0)
                except (OSError, ProcessLookupError):
                    shutil.rmtree(lock, ignore_errors=True)
                    continue
            elif not owner_pid:
                try:
                    if time.time() - lock.stat().st_mtime > timeout:
                        shutil.rmtree(lock, ignore_errors=True)
                        continue
                except OSError:
                    pass
            if time.monotonic() >= deadline:
                raise ContractError("integration planning lock is busy", "integration-busy")
            time.sleep(0.02)


def _canonical_ref(contract: dict[str, Any], task_id: str) -> str:
    return f"refs/heads/{task_branch(contract, task_id)}"


def import_candidate(contract: dict[str, Any], candidate: dict[str, Any], repo: Path,
                     *, receipt: dict[str, Any] | None = None) -> dict[str, Any]:
    """Import one verified candidate exactly once; conflicting retries fail closed."""
    validate_project_descriptor(contract)
    repo = _require_descriptor_repository(contract, repo)
    with _serialization_lock(repo):
        verified = verify_candidate(contract, candidate, repo, receipt=receipt)
        digest = verified["candidate_digest"]
        git_dir = _git_dir(repo)
        ledger = git_dir / "recursion-candidates"
        ledger.mkdir(mode=0o700, exist_ok=True)
        idempotency_key = str(verified.get("idempotency_key") or digest)
        operation_key = _json_digest(["candidate-import", contract["id"], idempotency_key])
        record_path = ledger / f"{operation_key}.json"
        ref = _canonical_ref(contract, verified["task_id"])
        current_result = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
        current = current_result.stdout.strip() if current_result.returncode == 0 else ""
        if current and current != verified["candidate_commit"]:
            raise ContractError("canonical task ref already names a different candidate", "idempotency-conflict")
        if current == verified["candidate_commit"]:
            status = "idempotent"
        else:
            created = _git(repo, "update-ref", ref, verified["candidate_commit"], "0" * len(verified["candidate_commit"]))
            if created.returncode:
                # Another coordinator may have won the same import race. Re-read the ref and
                # reconcile an identical winner; only a different winner is a real conflict.
                raced = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
                raced_commit = raced.stdout.strip() if raced.returncode == 0 else ""
                if raced_commit == verified["candidate_commit"]:
                    status = "idempotent"
                else:
                    raise ContractError("canonical task ref changed during import", "idempotency-conflict")
            else:
                status = "imported"
        record = {"schema": SCHEMA, "idempotency_key": verified.get("idempotency_key", digest),
                  "candidate_digest": digest, "task_id": verified["task_id"],
                  "canonical_ref": ref.removeprefix("refs/heads/"),
                  "candidate_commit": verified["candidate_commit"], "status": status}
        if record_path.exists():
            try:
                existing = json.loads(record_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ContractError("candidate idempotency record is unreadable", "idempotency-conflict") from exc
            if existing.get("candidate_digest") != digest:
                raise ContractError("candidate idempotency key names a different candidate", "idempotency-conflict")
        else:
            tmp = record_path.with_name(f".{record_path.name}.tmp")
            try:
                if tmp.exists():
                    tmp.unlink()
                with tmp.open("w", encoding="utf-8", newline="\n") as stream:
                    stream.write(json.dumps(record, sort_keys=True, indent=2) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(tmp, record_path)
                if os.name != "nt":
                    fd = os.open(str(ledger), os.O_RDONLY)
                    try:
                        os.fsync(fd)
                    finally:
                        os.close(fd)
            except OSError as exc:
                try:
                    tmp.unlink()
                except OSError:
                    pass
                raise ContractError("candidate idempotency record could not be durably written", "verification-unavailable") from exc
        return record


def classify_stale_base(contract: dict[str, Any], candidate: dict[str, Any], repo: Path,
                        *, receipt: dict[str, Any] | None = None) -> str:
    """Classify a verified candidate against current default/integration ancestry."""
    try:
        canonical = isinstance(candidate, dict) and isinstance(candidate.get("task_id"), str) \
            and candidate.get("external_branch") == task_branch(contract, candidate["task_id"])
        candidate = verify_candidate(contract, candidate, repo, receipt=receipt, allow_canonical=canonical)
    except ContractError as exc:
        return exc.code if exc.code in OUTCOMES else "unauthorized-result"
    try:
        source = candidate["source_sha"]
        commit = candidate["candidate_commit"]
        external_branch = candidate["external_branch"]
        _oid(repo, source, missing="source-unavailable")
        _oid(repo, commit, missing="unauthorized-result")
        default = _oid(repo, f"refs/heads/{contract['default_branch']}", missing="source-unavailable")
        integration = _oid(repo, f"refs/heads/{contract['integration_branch']}", missing="source-unavailable")
    except ContractError as exc:
        return exc.code if exc.code in OUTCOMES else "invalidated"
    try:
        branch_kind(contract, external_branch)
        if _oid(repo, f"refs/heads/{external_branch}", missing="unauthorized-result") != commit:
            return "unauthorized-result"
    except ContractError:
        return "unauthorized-result"
    if not _ancestor(repo, source, commit):
        return "unauthorized-result"
    if source == default and integration == source:
        return "current-compatible"
    if _ancestor(repo, commit, default) or _ancestor(repo, commit, integration):
        return "stale-reviewable"
    if _ancestor(repo, source, default) and _ancestor(repo, source, integration):
        return "stale-rebase-required"
    return "stale-rebase-required"


def plan_integration(contract: dict[str, Any], candidate: dict[str, Any], repo: Path,
                     *, receipt: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a serialized, read-only integration plan with an expected destination tip."""
    validate_project_descriptor(contract)
    repo = _require_descriptor_repository(contract, repo)
    with _serialization_lock(repo):
        canonical = isinstance(candidate, dict) and isinstance(candidate.get("task_id"), str) \
            and candidate.get("external_branch") == task_branch(contract, candidate["task_id"])
        verified = verify_candidate(contract, candidate, repo, receipt=receipt, allow_canonical=canonical)
        outcome = classify_stale_base(contract, verified, repo, receipt=receipt)
        integration = _oid(repo, f"refs/heads/{contract['integration_branch']}", missing="source-unavailable")
        return {"schema": SCHEMA, "task_id": verified["task_id"], "candidate_commit": verified["candidate_commit"],
                "source_sha": verified["source_sha"], "destination_branch": contract["integration_branch"],
                "expected_destination_tip": integration, "outcome": outcome,
                "can_integrate": outcome == "current-compatible", "serialized": True}


def _load(path: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON contract {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON contract {path} must be an object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("validate-project", "admit-task", "verify-candidate", "import-candidate", "classify", "plan"):
        command = subs.add_parser(name)
        command.add_argument("project")
        command.add_argument("payload", nargs="?")
        command.add_argument("--repo")
        command.add_argument("--receipt")
    args = parser.parse_args(argv)
    try:
        contract = validate_project_descriptor(_load(args.project))
        if args.command == "validate-project":
            result: Any = {"valid": True, "schema": SCHEMA, "project_id": contract["id"]}
        else:
            if not args.payload or not args.repo:
                parser.error(f"{args.command} requires payload and --repo")
            payload = _load(args.payload)
            repo = Path(args.repo).resolve()
            if args.command != "admit-task" and not args.receipt:
                parser.error(f"{args.command} requires a controller receipt via --receipt")
            receipt = _load(args.receipt) if args.receipt else None
            if args.command == "admit-task":
                result = admit_task(contract, payload, repo)
            elif args.command == "verify-candidate":
                result = verify_candidate(contract, payload, repo, receipt=receipt)
            elif args.command == "import-candidate":
                result = import_candidate(contract, payload, repo, receipt=receipt)
            elif args.command == "classify":
                result = {"outcome": classify_stale_base(contract, payload, repo, receipt=receipt)}
            else:
                result = plan_integration(contract, payload, repo, receipt=receipt)
        print(json.dumps(result, sort_keys=True))
        return 0
    except ContractError as exc:
        print(json.dumps({"error": exc.code, "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

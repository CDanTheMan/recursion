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
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any, Iterator


OID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$")
SCHEMA = "recursion-project-repository-contract/v2"
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
    for key in ("default_branch", "integration_branch"):
        value = contract[key]
        if not isinstance(value, str) or not BRANCH.fullmatch(value) or value.startswith("/"):
            raise ContractError(f"{key} is invalid")
    if contract["default_branch"] == contract["integration_branch"]:
        raise ContractError("default and integration branches must differ")
    pattern = contract["task_branch_pattern"]
    if not isinstance(pattern, str) or pattern.count("{task_id}") != 1:
        raise ContractError("task_branch_pattern must contain exactly one {task_id}")
    probe = pattern.replace("{task_id}", "probe")
    if not BRANCH.fullmatch(probe) or probe in {contract["default_branch"], contract["integration_branch"]}:
        raise ContractError("task_branch_pattern is unsafe")
    patterns = contract["external_branch_patterns"]
    if not isinstance(patterns, list) or not patterns or any(
        not isinstance(item, str) or not item or item in {"*", "**"} for item in patterns
    ):
        raise ContractError("external_branch_patterns must be a non-empty restricted list")
    if contract["publication_policy"] != "verified-integration-only":
        raise ContractError("unsupported publication policy")
    if contract["source_policy"] != "exact-sha":
        raise ContractError("unsupported source policy")
    for key in ("allowed_paths", "gate_commands", "eligible_hosts", "eligible_pools"):
        values = contract[key]
        if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
            raise ContractError(f"{key} must be a string array")
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
    if not BRANCH.fullmatch(result) or result in {
        contract["default_branch"], contract["integration_branch"]
    }:
        raise ContractError("resolved task branch is unsafe")
    return result


def branch_kind(contract: dict[str, Any], branch: str) -> str:
    """Return a branch namespace, refusing default and integration as execution targets."""
    validate_project_descriptor(contract)
    if not isinstance(branch, str) or not BRANCH.fullmatch(branch):
        raise ContractError("branch name is invalid", "unauthorized-result")
    if branch == contract["default_branch"]:
        raise ContractError("executor may not target the default branch", "unauthorized-result")
    if branch == contract["integration_branch"]:
        raise ContractError("executor may not target the integration branch", "unauthorized-result")
    if branch == task_branch(contract, "probe")[:-5] + "probe":
        return "task"
    if any(fnmatch.fnmatchcase(branch, pattern) for pattern in contract["external_branch_patterns"]):
        return "external"
    # A resolved task branch is checked by constructing it from the task id.  This avoids
    # accepting arbitrary refs under a broad prefix when a project chose a custom pattern.
    prefix, suffix = contract["task_branch_pattern"].split("{task_id}")
    if branch.startswith(prefix) and branch.endswith(suffix):
        task_id = branch[len(prefix):len(branch) - len(suffix) if suffix else None]
        if task_id and IDENT.fullmatch(task_id):
            return "task"
    raise ContractError("branch is outside the project execution namespaces", "unauthorized-result")


def _path_allowed(path: str, allowed: list[str]) -> bool:
    normalized = PurePosixPath(path)
    if normalized.is_absolute() or ".." in normalized.parts:
        return False
    for root in allowed:
        root_path = PurePosixPath(root.rstrip("/"))
        if root == "." or normalized == root_path or root_path in normalized.parents:
            return True
    return False


def admit_task(contract: dict[str, Any], task: dict[str, Any], repo: Path, *, new_generation: bool = True) -> dict[str, Any]:
    """Admit a task only when its source branch currently names its exact source SHA."""
    validate_project_descriptor(contract)
    if not isinstance(task, dict):
        raise ContractError("task must be an object")
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
    if declared_repo != contract["repo"]:
        raise ContractError("task source repository does not match project", "unauthorized-result")
    allowed = task.get("allowed_paths", contract["allowed_paths"])
    if not isinstance(allowed, list) or any(not isinstance(item, str) for item in allowed):
        raise ContractError("task allowed_paths is invalid")
    if new_generation and any(item == "apps/chiron" or item.startswith("apps/chiron/") for item in allowed):
        raise ContractError("new task generation may not target apps/chiron", "unauthorized-result")
    target = task.get("target_branch")
    if target is not None:
        branch_kind(contract, target)
    return {**task, "source_branch": source_branch, "source_sha": source_sha,
            "source_repository": declared_repo, "task_branch": task_branch(contract, task_id)}


def _candidate_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    required = {"project_id", "task_id", "source_branch", "source_sha", "external_branch", "candidate_commit"}
    missing = sorted(key for key in required if key not in candidate)
    if missing:
        raise ContractError(f"candidate is missing fields: {', '.join(missing)}")
    return candidate


def verify_candidate(contract: dict[str, Any], candidate: dict[str, Any], repo: Path,
                     *, allow_canonical: bool = False) -> dict[str, Any]:
    """Independently verify branch identity, source ancestry, scope, and verifier evidence."""
    validate_project_descriptor(contract)
    _candidate_payload(candidate)
    if candidate["project_id"] != contract["id"]:
        raise ContractError("candidate project identity does not match", "unauthorized-result")
    task_branch(contract, candidate["task_id"])
    if candidate["source_branch"] != contract["default_branch"]:
        raise ContractError("candidate source branch is not the project source branch", "unauthorized-result")
    source = candidate["source_sha"]
    commit = candidate["candidate_commit"]
    if not isinstance(source, str) or not OID.fullmatch(source) or not isinstance(commit, str) or not OID.fullmatch(commit):
        raise ContractError("candidate commit identity is malformed", "unauthorized-result")
    kind = branch_kind(contract, candidate["external_branch"])
    if kind != "external" and not (allow_canonical and kind == "task"):
        raise ContractError("candidate must arrive on an external branch", "unauthorized-result")
    observed = _oid(repo, f"refs/heads/{candidate['external_branch']}", missing="unauthorized-result")
    if observed != commit:
        raise ContractError("external branch tip does not equal candidate commit", "unauthorized-result")
    _oid(repo, source, missing="source-unavailable")
    _oid(repo, commit, missing="unauthorized-result")
    if not _ancestor(repo, source, commit):
        raise ContractError("candidate is not descended from its exact source SHA", "unauthorized-result")
    changed = _git(repo, "diff", "--name-only", source, commit)
    if changed.returncode:
        raise ContractError("candidate diff could not be measured", "verification-unavailable")
    paths = [item for item in changed.stdout.splitlines() if item]
    allowed = candidate.get("allowed_paths", contract["allowed_paths"])
    if not isinstance(allowed, list) or any(not _path_allowed(path, allowed) for path in paths):
        raise ContractError("candidate changed a path outside allowed_paths", "unauthorized-result")
    verified = candidate.get("verified") is True or (
        isinstance(candidate.get("verification"), dict)
        and candidate["verification"].get("status") == "pass"
        and candidate["verification"].get("commit") in {None, commit}
    )
    if not verified:
        raise ContractError("candidate lacks independent passing verification", "unauthorized-result")
    result = dict(candidate)
    result["changed_paths"] = paths
    result["candidate_digest"] = _json_digest({key: result[key] for key in sorted(result) if key != "candidate_digest"})
    return result


@contextlib.contextmanager
def _serialization_lock(repo: Path, timeout: float = 10.0) -> Iterator[None]:
    lock = _git_dir(repo) / "recursion-integration.lock"
    deadline = time.monotonic() + timeout
    while True:
        try:
            lock.mkdir(mode=0o700)
            try:
                yield
            finally:
                lock.rmdir()
            return
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ContractError("integration planning lock is busy", "integration-busy")
            time.sleep(0.02)


def _canonical_ref(contract: dict[str, Any], task_id: str) -> str:
    return f"refs/heads/{task_branch(contract, task_id)}"


def import_candidate(contract: dict[str, Any], candidate: dict[str, Any], repo: Path) -> dict[str, Any]:
    """Import one verified candidate exactly once; conflicting retries fail closed."""
    verified = verify_candidate(contract, candidate, repo)
    digest = verified["candidate_digest"]
    ledger = _git_dir(repo) / "recursion-candidates"
    ledger.mkdir(mode=0o700, exist_ok=True)
    record_path = ledger / f"{digest}.json"
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
            raise ContractError("canonical task ref changed during import", "idempotency-conflict")
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
            raise ContractError("candidate idempotency record conflicts", "idempotency-conflict")
    else:
        record_path.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return record


def classify_stale_base(contract: dict[str, Any], candidate: dict[str, Any], repo: Path) -> str:
    """Classify a verified candidate against current default/integration ancestry."""
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


def plan_integration(contract: dict[str, Any], candidate: dict[str, Any], repo: Path) -> dict[str, Any]:
    """Return a serialized, read-only integration plan with an expected destination tip."""
    with _serialization_lock(repo):
        verified = verify_candidate(contract, candidate, repo, allow_canonical=True)
        outcome = classify_stale_base(contract, verified, repo)
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
            if args.command == "admit-task":
                result = admit_task(contract, payload, repo)
            elif args.command == "verify-candidate":
                result = verify_candidate(contract, payload, repo)
            elif args.command == "import-candidate":
                result = import_candidate(contract, payload, repo)
            elif args.command == "classify":
                result = {"outcome": classify_stale_base(contract, payload, repo)}
            else:
                result = plan_integration(contract, payload, repo)
        print(json.dumps(result, sort_keys=True))
        return 0
    except ContractError as exc:
        print(json.dumps({"error": exc.code, "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

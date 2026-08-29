"""Strict, deterministic assignment identity for Phase 5 run evidence.

The assignment is controller-authored once, then treated as immutable.  Evidence does not
trust a digest supplied by a worker or caller: it loads this record, validates the fields and
recomputes the digest from canonical JSON.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

class FirstPartyImportError(ImportError):
    """A required controller module is absent or malformed in the importing tree."""


try:
    from phase5_safety import BoundaryError, decode_json, is_plain_int, pinned_directory, read_bytes
except Exception as exc:
    module_name = getattr(exc, "name", None) or "phase5_safety"
    raise FirstPartyImportError(
        f"first-party module '{module_name}' is unavailable or malformed; searched {_SCRIPT_DIR}"
    ) from None

ID_RE = re.compile(r"[a-z][a-z0-9-]{1,63}\Z")
SHA_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
VALUE_RE = re.compile(r"[a-z][a-z0-9.-]{1,127}\Z")
BRANCH_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,255}\Z")
SANDBOXES = frozenset({
    "strict-linux", "workspace-linux", "vendor-cloud", "remote-linux",
    "windows-interactive", "trusted-interactive", "account-shared-supervisor",
})
CLAUDE_ARGV = ["claude", "-p", "{{PROMPT}}", "--permission-mode", "acceptEdits",
               "--allowedTools", "Bash(node:*)"]
CLAUDE_MODEL_SUFFIX = ["--model", "{{MODEL}}"]
REQUIRED = frozenset({
    "task_id", "project_id", "source_repository", "source_branch", "source_sha",
    "controller_repository", "controller_sha",
    "seed_manifest_digest", "engine", "provider", "capacity_pool", "model", "host",
    "sandbox_profile", "network_policy", "network_profile", "network_endpoints", "argv",
    "allowed_paths", "gate_digest",
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
        with pinned_directory(path) as (_, absolute):
            resolved = Path(absolute)
            probe = subprocess.run(
                ["git", "-C", str(resolved), "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=False,
            )
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        raise AssignmentError("source_repository is unavailable") from exc
    if probe.returncode != 0:
        raise AssignmentError("source_repository is not a canonical Git repository")
    try:
        with pinned_directory(probe.stdout.strip()) as (_, git_absolute):
            git_root = Path(git_absolute)
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        raise AssignmentError("source_repository Git root is unavailable") from exc
    if git_root != resolved:
        raise AssignmentError("source_repository must be the canonical Git worktree root")
    return os.path.normcase(str(resolved))


def _canonical_controller(value: Any) -> str:
    raw = _text(value, "controller_repository")
    path = Path(raw)
    if not path.is_absolute():
        raise AssignmentError("controller_repository must be absolute")
    try:
        with pinned_directory(path) as (_, absolute):
            resolved = Path(absolute)
            probe = subprocess.run(
                ["git", "-C", str(resolved), "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=False,
            )
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        raise AssignmentError("controller_repository is unavailable") from exc
    try:
        with pinned_directory(probe.stdout.strip()) as (_, git_absolute):
            git_root = Path(git_absolute)
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        raise AssignmentError("controller_repository Git root is unavailable") from exc
    if probe.returncode != 0 or git_root != resolved:
        raise AssignmentError("controller_repository is not the canonical Git worktree root")
    configured = os.environ.get("RECURSION_ROOT", "").strip()
    expected = Path(configured) if configured else Path(__file__).parent.parent
    if not expected.is_absolute():
        expected = Path(os.path.abspath(str(expected)))
    else:
        expected = Path(os.path.abspath(str(expected)))
    if resolved != expected:
        raise AssignmentError("controller_repository is not the canonical controller root")
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


def _git_head_is(repo: str, sha: str, label: str) -> None:
    resolved = subprocess.run(
        ["git", "-C", repo, "rev-parse", "--verify", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    if resolved.returncode or resolved.stdout.strip().lower() != sha.lower():
        raise AssignmentError(f"{label} HEAD is not the assigned immutable commit")


def _git_branch_is(repo: str, branch: str, sha: str) -> None:
    resolved = subprocess.run(
        ["git", "-C", repo, "rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}"],
        capture_output=True, text=True, check=False,
    )
    if resolved.returncode or resolved.stdout.strip().lower() != sha.lower():
        raise AssignmentError("source_branch does not identify the assigned source commit")


def _controller_file_bytes(repo: str, sha: str, relative: str) -> bytes:
    pure = PurePosixPath(relative)
    path = Path(repo, *pure.parts)
    if pure.is_absolute() or not pure.parts or pure.as_posix() != relative or "\\" in relative \
            or any(part in {"", ".", ".."} for part in pure.parts):
        raise AssignmentError(f"controller file is not a clean regular file: {relative}")
    tracked = subprocess.run(
        ["git", "-C", repo, "ls-files", "--error-unmatch", "--", relative],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    tree = subprocess.run(
        ["git", "-C", repo, "ls-tree", "-z", sha, "--", relative],
        capture_output=True, check=False,
    )
    committed = subprocess.run(
        ["git", "-C", repo, "show", f"{sha}:{relative}"], capture_output=True, check=False,
    )
    rows = [row for row in tree.stdout.split(b"\0") if row]
    mode = rows[0].split(b" ", 1)[0] if len(rows) == 1 else b""
    try:
        live = read_bytes(path, label=f"controller file {relative}")
    except BoundaryError as exc:
        raise AssignmentError(f"controller file is unreadable: {relative}") from exc
    if tracked.returncode or tree.returncode or len(rows) != 1 \
            or mode not in {b"100644", b"100755"} or committed.returncode \
            or live != committed.stdout:
        raise AssignmentError(f"controller file differs from its exact clean commit: {relative}")
    return committed.stdout


def _clean_controller_file(repo: str, sha: str, relative: str) -> None:
    _controller_file_bytes(repo, sha, relative)


def _validate_engine_manifest(manifest: object, engine: str, controller_repo: str,
                              controller_sha: str) -> None:
    """Run the controller's complete manifest validator before extracting fields.

    Assignment validation is an independent trust boundary.  Repeating only the
    handful of fields needed for argv/network binding would let an invalid plugin
    manifest enter an otherwise valid assignment.  The resolver itself is pinned
    to the same clean controller commit before it is loaded.
    """
    relative = "scripts/resolve-engine.py"
    _clean_controller_file(controller_repo, controller_sha, relative)
    path = Path(controller_repo, "scripts", "resolve-engine.py")
    module_name = f"assignment_resolver_{controller_sha[:16]}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError("resolver module specification is unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        validator = getattr(module, "validate_manifest")
        validator(manifest, engine, controller_root=Path(controller_repo),
                  controller_commit=controller_sha)
    except Exception as exc:
        raise AssignmentError(f"engine manifest for {engine} failed full validation") from exc


def _provider_profiles(controller_repo: str | None = None, controller_sha: str | None = None) -> dict[str, Any]:
    if (controller_repo is None) != (controller_sha is None):
        raise AssignmentError("controller policy provenance is incomplete")
    if controller_repo is not None:
        raw = _controller_file_bytes(controller_repo, controller_sha, "scripts/provider-egress-profiles.json")
    else:
        path = Path(__file__).parent / "provider-egress-profiles.json"
        try:
            raw = read_bytes(path, label="provider profile registry")
        except BoundaryError as exc:
            raise AssignmentError("provider profile registry is invalid") from exc
    try:
        value = decode_json(raw, "provider profile registry")
        profiles = value["profiles"]
        if not isinstance(profiles, dict):
            raise TypeError
        return profiles
    except (BoundaryError, OSError, ValueError, KeyError, TypeError,
            OverflowError, RecursionError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssignmentError("provider profile registry is invalid") from exc


def _engine_binding(engine: str, controller_repo: str, controller_sha: str) -> tuple[str, str, list[str], str, list[str], list[str] | None]:
    if engine == "claude":
        provider, profile, policy = "anthropic-claude-code", "anthropic", "provider-only"
        expected_argv, suffix = CLAUDE_ARGV, CLAUDE_MODEL_SUFFIX
    elif engine == "none":
        return "none", "none", [], "none", [], None
    else:
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,31}", engine):
            raise AssignmentError(f"engine manifest binding is unavailable for {engine}")
        relative = f"scripts/engines/{engine}.json"
        try:
            manifest = decode_json(
                _controller_file_bytes(controller_repo, controller_sha, relative),
                f"engine manifest {engine}",
            )
            _validate_engine_manifest(manifest, engine, controller_repo, controller_sha)
            provider = manifest["billing"]["provider"]
            profile = manifest["network"]["profile"]
            endpoints = manifest["network"]["endpoints"]
            policy = manifest["network"]["policy"]
            argv = manifest["argv"]
            suffix = manifest["model"]["argv_suffix"]
        except (BoundaryError, OSError, ValueError, KeyError, TypeError,
                OverflowError, RecursionError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AssignmentError(f"engine manifest binding is unavailable for {engine}") from exc
        if not isinstance(provider, str) or not isinstance(profile, str) or not isinstance(endpoints, list) \
                or not isinstance(policy, str) or not isinstance(argv, list) or not isinstance(suffix, list):
            raise AssignmentError(f"engine manifest binding is invalid for {engine}")
        return provider, profile, endpoints, policy, argv, suffix
    profiles = _provider_profiles(controller_repo, controller_sha)
    try:
        endpoints = profiles[profile]["endpoints"]
    except (KeyError, TypeError) as exc:
        raise AssignmentError(f"provider profile is unavailable for {engine}") from exc
    if engine == "claude":
        return provider, profile, endpoints, policy, expected_argv, suffix
    return provider, profile, endpoints, policy, [], None


def _declared_argv(argv: list[str], suffix: list[str] | None, model: str) -> list[str]:
    result = list(argv)
    if model and suffix:
        result.extend(suffix)
    return result


def _validate_argv(value: Any, where: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value) \
            or any(not isinstance(item, str) or not item or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in item)
                   for item in value):
        raise AssignmentError(f"{where} argv is invalid")
    return value


def _validate_binding(engine: str, provider: str, profile: str, endpoints: Any, policy: str,
                      argv: Any, model: str, where: str, *, controller_repo: str,
                      controller_sha: str) -> None:
    expected_provider, expected_profile, expected_endpoints, expected_policy, expected_argv, suffix = \
        _engine_binding(engine, controller_repo, controller_sha)
    if (provider, profile, policy) != (expected_provider, expected_profile, expected_policy):
        raise AssignmentError(f"{where} engine/provider/network profile does not match its manifest")
    if not isinstance(endpoints, list) or endpoints != expected_endpoints:
        raise AssignmentError(f"{where} network endpoints do not match its manifest/profile")
    declared_argv = _validate_argv(argv, where, allow_empty=engine == "none")
    expected_declared = _declared_argv(expected_argv, suffix, model)
    if declared_argv != expected_declared:
        raise AssignmentError(f"{where} argv does not match its immutable engine manifest")
    profiles = _provider_profiles(controller_repo, controller_sha)
    if profile != "none":
        try:
            profile_value = profiles[profile]
        except KeyError as exc:
            raise AssignmentError(f"{where} network profile is not declared") from exc
        if profile_value.get("provider") != provider or profile_value.get("endpoints") != endpoints:
            raise AssignmentError(f"{where} network profile/provider/endpoints disagree")
        if policy == "provider-only" and not endpoints:
            raise AssignmentError(f"{where} networked provider profile must declare an endpoint")
        if policy == "none" and (provider != "sentry-local" or profile != "sentry-local" or endpoints):
            raise AssignmentError(f"{where} no-egress policy is reserved for sentry-local")
    elif policy != "none" or provider != "none" or endpoints:
        raise AssignmentError(f"{where} no-egress binding is invalid")


def _validate_gate_contract(value: Any, expected_digest: str, *, source_repo: str,
                            source_sha: str, controller_repo: str, controller_sha: str,
                            allowed_paths: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) not in ({
        "acceptance", "acceptance_sha256", "gate_files", "controller_gate_files"
    }, {
        "acceptance", "acceptance_sha256", "gate_files", "controller_gate_files", "read_only_paths"
    }):
        raise AssignmentError("gate_contract is not the validated gate contract")
    if not isinstance(value["acceptance"], str) or not value["acceptance"]:
        raise AssignmentError("gate_contract acceptance program is absent")
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
    read_only_paths = value.get("read_only_paths", [])
    if not isinstance(read_only_paths, list) or any(
        not isinstance(path, str) or not path or "\\" in path or path.startswith("/")
        or ":" in path or any(part in {"", ".", ".."} for part in path.split("/"))
        for path in read_only_paths
    ) or len(set(read_only_paths)) != len(read_only_paths):
        raise AssignmentError("gate_contract.read_only_paths is unsafe")
    actual = hashlib.sha256(canonical_bytes(value)).hexdigest()
    if actual != expected_digest:
        raise AssignmentError("gate_digest does not hash the validated gate contract")
    _clean_controller_file(controller_repo, controller_sha, "scripts/validate-gate.py")
    command = [
        str(Path(controller_repo) / "scripts" / "validate-gate.py"),
        "--acceptance", value["acceptance"], "--allowed-paths", ",".join(allowed_paths),
        "--gate-files", ",".join(value["gate_files"]), "--repo", source_repo,
        "--source-commit", source_sha, "--controller-root", controller_repo,
        "--controller-commit", controller_sha,
        "--controller-gate-files", ",".join(value["controller_gate_files"]),
    ]
    if read_only_paths:
        command.extend(["--read-only-paths", ",".join(read_only_paths)])
    try:
        verified = subprocess.run(
            [sys.executable, *command],
            capture_output=True, text=True, check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AssignmentError("strict gate provenance validation was unavailable") from exc
    if verified.returncode != 0:
        detail = (verified.stderr or verified.stdout or "strict gate validation failed").strip()
        raise AssignmentError(f"gate_contract provenance is not independently valid: {detail}")
    try:
        observed = decode_json(verified.stdout, "strict gate validator output")
    except (BoundaryError, json.JSONDecodeError, TypeError, ValueError,
            OverflowError, RecursionError, UnicodeDecodeError) as exc:
        raise AssignmentError("strict gate validator returned malformed provenance") from exc
    if observed != value:
        raise AssignmentError("gate_contract differs from independently validated provenance")
    return value


def _authenticated_pool_policy(pool: str, controller_repo: str, controller_sha: str) -> dict[str, Any]:
    try:
        raw = _controller_file_bytes(controller_repo, controller_sha, "scripts/capacity-pools.json")
        value = decode_json(raw, "capacity pool policy")
        pools = value["pools"]
        policy = pools[pool]
    except (BoundaryError, OSError, UnicodeDecodeError, ValueError, KeyError,
            TypeError, OverflowError, RecursionError, json.JSONDecodeError):
        raise AssignmentError("capacity_pool is not a declared local pool")
    if not isinstance(policy, dict):
        raise AssignmentError("capacity_pool policy is invalid")
    return policy


def _validate_allowed_paths(paths: object) -> list[str]:
    if not isinstance(paths, list) or not paths or any(
        not isinstance(item, str) or not item or item != "." and item.startswith(("/", "\\"))
        or ":" in item
        or any(part in {"", ".", ".."} for part in item.replace("\\", "/").split("/"))
        or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in item) for item in paths
    ):
        raise AssignmentError("allowed_paths is not a safe nonempty relative-path list")
    return paths


def _validate_assignment(value: Any) -> dict[str, Any]:
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
    controller = _canonical_controller(value["controller_repository"])
    branch = _text(value["source_branch"], "source_branch", BRANCH_RE)
    if ".." in branch or branch.endswith("/") or branch.endswith("."):
        raise AssignmentError("source_branch is unsafe")
    sha = _text(value["source_sha"], "source_sha", SHA_RE)
    _git_commit_exists(source, sha)
    controller_sha = _text(value["controller_sha"], "controller_sha", SHA_RE)
    _git_commit_exists(controller, controller_sha)
    _git_head_is(source, sha, "source repository")
    _git_branch_is(source, branch, sha)
    _git_head_is(controller, controller_sha, "controller repository")
    branch_ref = subprocess.run(
        ["git", "-C", source, "symbolic-ref", "--quiet", "--short", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    if branch_ref.returncode or branch_ref.stdout.strip() != branch:
        raise AssignmentError("source_branch does not identify the checked-out source authority")
    branch_tip = subprocess.run(
        ["git", "-C", source, "rev-parse", "--verify", f"refs/heads/{branch}"],
        capture_output=True, text=True, check=False,
    )
    if branch_tip.returncode or branch_tip.stdout.strip().lower() != sha.lower():
        raise AssignmentError("source_branch does not identify source_sha")
    seed = value["seed_manifest_digest"]
    if not isinstance(seed, str) or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in seed) \
            or (seed and not SHA_RE.fullmatch(seed)):
        raise AssignmentError("seed_manifest_digest is invalid")
    _text(value["model"], "model") if value["model"] else None
    sandbox = _text(value["sandbox_profile"], "sandbox_profile")
    if sandbox not in SANDBOXES:
        raise AssignmentError("sandbox_profile is unsupported")
    paths = _validate_allowed_paths(value["allowed_paths"])
    gate_digest = _text(value["gate_digest"], "gate_digest", SHA_RE)
    gate_contract = _validate_gate_contract(
        value["gate_contract"], gate_digest, source_repo=source, source_sha=sha,
        controller_repo=controller, controller_sha=controller_sha, allowed_paths=paths,
    )
    _text(value["publication_policy"], "publication_policy", VALUE_RE)
    _text(value["network_policy"], "network_policy")
    top_argv = _validate_argv(value["argv"], "assignment", allow_empty=value["engine"] == "none")
    policy = _authenticated_pool_policy(value["capacity_pool"], controller, controller_sha)
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
    _validate_binding(value["engine"], provider, value["network_profile"], top_endpoints,
                      value["network_policy"], top_argv, value["model"], "implementer",
                      controller_repo=controller, controller_sha=controller_sha)
    for role, spec in roles.items():
        if not isinstance(spec, dict) or set(spec) != {
            "engine", "provider", "model", "network_policy", "network_profile", "network_endpoints", "argv"
        }:
            raise AssignmentError(f"role_assignments.{role} is invalid")
        role_engine = _text(spec["engine"], f"role_assignments.{role}.engine", VALUE_RE)
        role_provider = _text(spec["provider"], f"role_assignments.{role}.provider", VALUE_RE)
        role_policy = _text(spec["network_policy"], f"role_assignments.{role}.network_policy")
        role_profile = _text(spec["network_profile"], f"role_assignments.{role}.network_profile", VALUE_RE)
        role_model = _text(spec["model"], f"role_assignments.{role}.model")
        role_endpoints = spec["network_endpoints"]
        _validate_binding(role_engine, role_provider, role_profile, role_endpoints, role_policy,
                          spec["argv"], role_model, f"role_assignments.{role}",
                          controller_repo=controller, controller_sha=controller_sha)
        if role_provider not in policy.get("providers", []):
            raise AssignmentError(f"capacity_pool is not authorized for role {role} provider")
    normalized = dict(value)
    normalized["source_repository"] = source
    normalized["controller_repository"] = controller
    normalized["source_branch"] = branch
    normalized["source_sha"] = sha
    normalized["argv"] = top_argv
    normalized["gate_contract"] = gate_contract
    return normalized


def validate_assignment(value: Any) -> dict[str, Any]:
    """Validate one assignment inside a single typed input boundary."""
    try:
        return _validate_assignment(value)
    except AssignmentError:
        raise
    except (AttributeError, IndexError, KeyError, TypeError, ValueError,
            OverflowError, RecursionError, UnicodeDecodeError, OSError) as exc:
        raise AssignmentError("assignment contains invalid field types") from exc


def canonical_bytes(value: dict[str, Any]) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError) as exc:
        raise AssignmentError("assignment cannot be canonically encoded") from exc


def digest(value: Any) -> str:
    normalized = validate_assignment(value)
    return hashlib.sha256(canonical_bytes(normalized)).hexdigest()


def load_assignment(path: str | Path) -> tuple[dict[str, Any], str]:
    candidate = Path(path)
    try:
        raw = read_bytes(candidate, label="assignment file", private=True)
        value = decode_json(raw, "assignment file")
    except AssignmentError:
        raise
    except (BoundaryError, OSError, UnicodeDecodeError, json.JSONDecodeError,
            ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise AssignmentError("assignment file is unreadable") from exc
    normalized = validate_assignment(value)
    return normalized, hashlib.sha256(canonical_bytes(normalized)).hexdigest()


def validate_execution_evidence(execution: Any, run: dict[str, Any],
                                assignment: dict[str, Any]) -> dict[str, Any]:
    """Validate controller-owned execution facts against one immutable role assignment."""
    if not isinstance(execution, dict):
        raise AssignmentError("execution evidence must be an object")
    if not is_plain_int(execution.get("exit_code")) or not is_plain_int(run.get("exit_code")):
        raise AssignmentError("execution evidence and run exit codes must be integers")
    role = run.get("role")
    roles = assignment.get("role_assignments")
    role_spec = roles.get(role) if isinstance(roles, dict) else None
    if not isinstance(role_spec, dict):
        raise AssignmentError("execution evidence role is not assigned")
    expected = {
        "engine": role_spec.get("engine"),
        "provider": role_spec.get("provider"),
        "profile": role_spec.get("network_profile"),
        "endpoints": role_spec.get("network_endpoints"),
        "model": role_spec.get("model"),
        "argv": role_spec.get("argv"),
    }
    for field, expected_value in expected.items():
        if execution.get(field) != expected_value:
            raise AssignmentError(f"execution evidence {field} mismatch")
    assignment_digest = run.get("assignment_digest")
    if not isinstance(assignment_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", assignment_digest) \
            or execution.get("assignment_digest") != assignment_digest \
            or execution.get("assignment_identity") != assignment_digest:
        raise AssignmentError("execution evidence assignment identity mismatch")
    network = execution.get("network")
    if not isinstance(network, dict) or network != {
        "policy": role_spec.get("network_policy"),
        "profile": expected["profile"], "provider": expected["provider"],
        "endpoints": expected["endpoints"],
    }:
        raise AssignmentError("execution evidence network binding mismatch")

    run_status = run.get("status")
    execution_status = execution.get("status")
    if run_status == "cancelled":
        if execution_status != "cancelled" or execution.get("exit_code") != 143:
            raise AssignmentError("execution evidence status is not coherent with cancelled run")
    elif run_status in {"succeeded", "failed"}:
        if execution_status == "finished":
            if execution.get("exit_code") != run.get("exit_code"):
                raise AssignmentError("execution evidence exit code is not coherent with run")
        elif execution_status == "cancelled":
            if execution.get("exit_code") != 143 or run.get("exit_code") not in {75, 124, 143}:
                raise AssignmentError("execution evidence status is not coherent with run")
        else:
            raise AssignmentError("execution evidence status is not coherent with run")
    else:
        raise AssignmentError("run status is not terminal")
    return execution

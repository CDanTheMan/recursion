#!/usr/bin/env python3
"""Atomic Phase 5 run evidence for implementers and independent verifiers."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import math
import os
import secrets
import sys
import time
from pathlib import Path

import assignment as assignment_mod
from jsonl_durable import (
    JsonlDurabilityError, atomic_bytes, read_durable_bytes,
)
from run_contract import ASSIGNMENT_ATTRIBUTION_FIELDS, RunContractError, validate_run


class WorkerEvidenceError(Exception):
    """Malformed or unsafe evidence input refused before durable publication."""


_atomic_publish_hook = None
MAX_INPUT_BYTES = 8 * 1024 * 1024
NANOSECONDS = 1_000_000_000

RUN_STATUSES = frozenset({
    "pending", "prepared", "running", "succeeded", "failed", "blocked", "cancelled", "stale",
})

sys_path = Path(__file__).resolve().parent
if str(sys_path) not in sys.path:
    sys.path.insert(0, str(sys_path))

class FirstPartyImportError(ImportError):
    """A required controller module is absent or malformed in the importing tree."""


try:
    from phase5_safety import (BoundaryError, atomic_write, decode_json,
                               read_bytes, ensure_directory, absolute_lexical, MAX_JSON_BYTES)
    from assignment_contract import (AssignmentError as ContractAssignmentError,
                                     canonical_bytes, load_assignment,
                                     validate_assignment as assignment_validate,
                                     validate_bound_gate_files,
                                     validate_execution_evidence as assignment_execution_evidence)
except Exception as exc:
    module_name = getattr(exc, "name", None) or "phase5_safety/assignment_contract"
    import_error = FirstPartyImportError(
        f"first-party module '{module_name}' is unavailable or malformed; searched {sys_path}"
    )
    if __name__ == "__main__":
        print(f"worker-evidence: first-party import failed: {import_error}", file=sys.stderr)
        raise SystemExit(95)
    raise import_error from None


START_EVIDENCE_KIND = "worker-evidence-start-v1"
START_FIELDS = {
    "schema_version", "kind", "run_id", "task_id", "role", "evidence_path",
    "assignment_file", "assignment_digest", "assignment", "attribution", "worktree",
}


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def validate_run_evidence(value: object) -> dict:
    """Apply the control-plane run schema at every worker state boundary."""
    try:
        checked = validate_run(value)
    except RunContractError as exc:
        raise WorkerEvidenceError(str(exc)) from None
    for key in ("deadline_epoch_ns", "worker_finished_epoch_ns"):
        if key in checked:
            item = checked[key]
            if isinstance(item, bool) or not isinstance(item, int) or item < 0:
                raise WorkerEvidenceError(f"run evidence {key} is not a nonnegative integer")
    deadline_epoch = checked.get("deadline_epoch")
    if "deadline_epoch_ns" in checked and "deadline_epoch" in checked:
        if isinstance(deadline_epoch, bool) or not isinstance(deadline_epoch, int):
            raise WorkerEvidenceError("run evidence deadline_epoch is not an integer")
        if checked["deadline_epoch_ns"] // NANOSECONDS != deadline_epoch:
            raise WorkerEvidenceError("run evidence precise deadline disagrees with deadline_epoch")
    return checked


def iso(epoch: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def load(path: Path) -> dict:
    try:
        if not isinstance(path, Path):
            raise WorkerEvidenceError("run evidence path must be a path")
        raw = read_bytes(path, label="evidence file", max_bytes=MAX_INPUT_BYTES)
        value = decode_json(raw, "evidence file")
    except (BoundaryError, OSError, UnicodeDecodeError, json.JSONDecodeError,
            JsonlDurabilityError, TypeError, ValueError, OverflowError,
            RecursionError) as exc:
        raise SystemExit("worker-evidence: evidence file is unreadable") from exc
    if not isinstance(value, dict):
        raise SystemExit("worker-evidence: evidence file must contain an object")
    validate_run_evidence(value)
    digest = value.get("assignment_digest")
    if digest:
        parent = path.parent
        assignment_root = parent.parent / "assignments" if parent.name == "runs" else parent / "assignments"
        persisted = assignment_mod.load_assignment(assignment_root, str(value.get("task_id") or ""), str(digest))
        if persisted is None:
            embedded = value.get("assignment")
            if not isinstance(embedded, dict) or "controller_repository" not in embedded:
                raise WorkerEvidenceError("persisted assignment is unusable")
        else:
            try:
                assignment_mod.validate_assignment(persisted, require_source_evidence=True)
            except assignment_mod.AssignmentError as exc:
                raise WorkerEvidenceError("persisted assignment is unusable") from exc
            try:
                assignment_mod.require_assignment_projection(value, persisted)
            except assignment_mod.AssignmentError as exc:
                raise WorkerEvidenceError("run attribution disagrees with persisted assignment") from exc
    return value


def atomic(path: Path, value: dict) -> None:
    if not isinstance(path, Path) or not isinstance(value, dict):
        raise WorkerEvidenceError("evidence publication requires a path and object")
    try:
        encoded = (json.dumps(value, indent=2, sort_keys=True,
                              allow_nan=False) + "\n").encode("utf-8")
        if _atomic_publish_hook is not None:
            atomic_bytes(path, encoded, hook=_atomic_publish_hook)
        else:
            atomic_write(path, encoded, replace=True, mode=0o600, label="evidence output")
    except (BoundaryError, JsonlDurabilityError, OSError, TypeError, ValueError,
            OverflowError, RecursionError, UnicodeEncodeError) as exc:
        raise WorkerEvidenceError("evidence publication refused") from exc


def start_evidence_path(path: Path) -> Path:
    """Return the non-run-glob sidecar that records the immutable start binding."""
    absolute = Path(absolute_lexical(path))
    return absolute.with_name(f".{absolute.name}.start")


def evidence_key_path(controller_repository: str) -> Path:
    if os.environ.get("RECURSION_EVIDENCE_KEY_FILE", "").strip():
        raise SystemExit("worker-evidence: caller-supplied evidence key selection is refused")
    return Path(controller_repository) / "state" / ".worker-evidence.key"


def load_evidence_key(controller_repository: str) -> bytes:
    path = evidence_key_path(controller_repository)
    try:
        key = read_bytes(path, label="worker evidence key", max_bytes=1024,
                         private=True)
        if not key or len(key) < 32:
            raise BoundaryError("worker evidence key is too short")
        return key
    except (BoundaryError, OSError, TypeError, ValueError, OverflowError,
            RecursionError) as exc:
        raise SystemExit("worker-evidence: controller-provisioned evidence key is unavailable") from exc


def provision_evidence_key(controller_repository: str) -> None:
    """Provision the fixed controller key before a worker is launched.

    This is a controller lifecycle operation.  Worker transitions only call
    load_evidence_key(), and therefore cannot choose a key path or bootstrap a
    run under a caller-created key.
    """
    path = evidence_key_path(controller_repository)
    try:
        existing = read_bytes(path, label="worker evidence key", max_bytes=1024,
                              private=True, optional=True)
        if existing is not None:
            if len(existing) < 32:
                raise BoundaryError("worker evidence key is too short")
            return
        ensure_directory(path.parent)
        atomic_write(path, secrets.token_bytes(32), replace=False, mode=0o600,
                     label="worker evidence key")
        key = read_bytes(path, label="worker evidence key", max_bytes=1024,
                         private=True)
        if key is None or len(key) < 32:
            raise BoundaryError("worker evidence key is too short")
    except (BoundaryError, OSError, TypeError, ValueError, OverflowError,
            RecursionError) as exc:
        raise SystemExit("worker-evidence: controller could not provision evidence key") from exc


def _binding_mac(value: dict, key: bytes) -> str:
    try:
        payload = canonical_bytes(value)
        return hmac.new(key, payload, hashlib.sha256).hexdigest()
    except (ContractAssignmentError, TypeError, ValueError, OverflowError,
            RecursionError, UnicodeDecodeError) as exc:
        raise SystemExit("worker-evidence: start binding cannot be authenticated") from exc


def write_start_evidence(path: Path, value: dict, key: bytes) -> None:
    """Create the start binding exactly once; later transitions never rewrite it."""
    try:
        binding = dict(value)
        binding["binding_hmac_sha256"] = _binding_mac(value, key)
        encoded = (json.dumps(binding, indent=2, sort_keys=True,
                              allow_nan=False) + "\n").encode("utf-8")
        atomic_write(path, encoded, replace=False, mode=0o444,
                     label="immutable start evidence")
    except BoundaryError as exc:
        if "already exists" in str(exc):
            raise SystemExit("worker-evidence: immutable start evidence already exists") from exc
        raise SystemExit("worker-evidence: immutable start evidence could not be written") from exc
    except (OSError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise SystemExit("worker-evidence: immutable start evidence could not be written") from exc


def load_start_evidence(path: Path) -> dict:
    """Load and authenticate the start binding independently of mutable run JSON."""
    candidate = start_evidence_path(path)
    try:
        value = decode_json(read_bytes(candidate, label="immutable start evidence"),
                            "immutable start evidence")
        if not isinstance(value, dict) or set(value) != START_FIELDS | {"binding_hmac_sha256"}:
            raise ValueError("immutable start evidence is malformed")
        embedded = value["assignment"]
        assignment = validate_assignment_for_sidecar(embedded)
        if value["assignment_digest"] != hashlib.sha256(canonical_bytes(assignment)).hexdigest():
            raise ValueError("immutable start evidence assignment digest is invalid")
        supplied_attribution = value["attribution"]
        if not isinstance(supplied_attribution, dict):
            raise ValueError("immutable start evidence attribution is invalid")
        expected_attribution = assignment_attribution(
            assignment, value["role"],
            billing_basis=supplied_attribution.get("billing_basis", ""),
            metered_approved=supplied_attribution.get("metered_approved"),
            default_branch=supplied_attribution.get("default_branch", ""),
            integration_branch=supplied_attribution.get("integration_branch", ""),
        )
        if not assignment_mod.type_aware_equal(supplied_attribution, expected_attribution):
            raise ValueError("immutable start evidence attribution is inconsistent")
        key = load_evidence_key(assignment["controller_repository"])
        supplied = value.pop("binding_hmac_sha256")
        expected = _binding_mac(value, key)
        value["binding_hmac_sha256"] = supplied
        if not isinstance(supplied, str) or not hmac.compare_digest(supplied, expected):
            raise ValueError("immutable start evidence authentication failed")
        if value["evidence_path"] != os.path.normcase(os.path.abspath(str(path))):
            raise ValueError("immutable start evidence is bound to a different run path")
    except SystemExit:
        raise
    except (BoundaryError, OSError, UnicodeDecodeError, json.JSONDecodeError,
            ValueError, TypeError, OverflowError, RecursionError, KeyError) as exc:
        raise SystemExit("worker-evidence: immutable start evidence is unavailable") from exc
    if value["kind"] != START_EVIDENCE_KIND:
        raise SystemExit("worker-evidence: immutable start evidence is malformed")
    return value


def validate_assignment_for_sidecar(value: object) -> dict:
    try:
        return assignment_validate(value)
    except ContractAssignmentError as exc:
        raise ValueError("immutable start evidence assignment is invalid") from exc


def maybe_json(path: str | None) -> object:
    if not path:
        return {}
    # The sandbox pre-truncates the hermes usage file before mounting it; a worker that exits
    # without writing leaves it empty. An empty file means "no usage data", the same fact as
    # an absent file — it must not crash `finish` and lose the whole run record.
    try:
        raw = read_bytes(Path(path), label="auxiliary evidence", max_bytes=MAX_JSON_BYTES,
                         optional=True)
    except (BoundaryError, OSError, UnicodeDecodeError, TypeError, ValueError,
            OverflowError, RecursionError) as exc:
        raise SystemExit("worker-evidence: auxiliary evidence is unreadable") from exc
    if raw is None or not raw.strip():
        return {}
    try:
        return decode_json(raw, "auxiliary evidence")
    except (BoundaryError, json.JSONDecodeError, ValueError, TypeError,
            OverflowError, RecursionError, UnicodeDecodeError) as exc:
        raise SystemExit("worker-evidence: auxiliary evidence is malformed") from exc


def refresh_assignment(value: dict, start: dict) -> dict:
    """Re-read the immutable assignment whenever evidence is consumed.

    A valid assignment at process start is not enough: the file, embedded copy, or
    gate input may be replaced before finish/gate/verification evidence is recorded.
    Recomputing here makes every evidence transition bind to the same source commit,
    engine/provider profile, and validated gate contract.
    """
    assignment_file = start["assignment_file"]
    assignment, computed = load_assignment(assignment_file)
    if computed != start["assignment_digest"]:
        raise SystemExit("worker-evidence: assignment changed after run start")
    if "assignment_file" in value and value["assignment_file"] != assignment_file:
        raise SystemExit("worker-evidence: mutable assignment binding changed")
    if "assignment_digest" in value and value["assignment_digest"] != computed:
        raise SystemExit("worker-evidence: mutable assignment binding changed")
    embedded = value.get("assignment", assignment)
    if not isinstance(embedded, dict) or canonical_bytes(embedded) != canonical_bytes(assignment):
        raise SystemExit("worker-evidence: embedded assignment does not match its source file")
    return assignment


def validate_execution_evidence(execution: object, run: dict, assignment: dict) -> dict:
    try:
        return assignment_execution_evidence(execution, run, assignment)
    except ContractAssignmentError as exc:
        raise SystemExit(f"worker-evidence: {exc}") from exc


def assignment_from(path: str, digest: str, task_id: str, role: str = "", run_path: Path | None = None) -> dict:
    if run_path is not None:
        parent = run_path.parent
        assignment_root = parent.parent / "assignments" if parent.name == "runs" else parent / "assignments"
        try:
            expected = assignment_mod.assignment_path(assignment_root, task_id, digest)
        except assignment_mod.AssignmentError as exc:
            raise SystemExit(2) from exc
        if os.path.normcase(os.path.abspath(path)) != os.path.normcase(os.path.abspath(expected)):
            raise SystemExit(2)
    try:
        raw = read_durable_bytes(Path(path), max_bytes=MAX_INPUT_BYTES)
        if raw is None:
            raise WorkerEvidenceError("assignment is absent")
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite JSON number")),
        )
        assignment_mod.validate_assignment(value, require_source_evidence=True)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, JsonlDurabilityError,
            TypeError, ValueError,
            OverflowError, RecursionError, assignment_mod.AssignmentError) as exc:
        raise WorkerEvidenceError("invalid persisted assignment") from exc
    if value.get("assignment_digest") != digest or value.get("task_id") != task_id \
            or (role and value.get("role") != role):
        raise SystemExit(2)
    return value


def copy_assignment(value: dict) -> dict:
    return assignment_mod.assignment_projection(value)


def assignment_attribution(assignment: dict, role: str, *, billing_basis: str = "",
                           metered_approved: bool | None = None, default_branch: str = "",
                           integration_branch: str = "") -> dict:
    """Project one role's complete attribution from the immutable Phase 5 assignment.

    Phase 5 stores role-dependent execution facts under ``role_assignments`` and shared source,
    scope, and publication facts at the assignment top level. Five fields in the older run
    evidence projection are not part of the current Phase 5 envelope, so the controller supplies
    those already-resolved policy facts at the start boundary (billing_basis, metered_approved,
    default_branch, and integration_branch); source_evidence is rebuilt from the contract's
    validated source tuple. An absent fact is a refusal rather than a guessed value.
    """
    try:
        roles = assignment.get("role_assignments")
        role_spec = roles.get(role) if isinstance(roles, dict) else None
        if not isinstance(role_spec, dict):
            # Keep the Phase 3 assignment-native shape usable for its existing callers.
            role_spec = assignment

        source_evidence = assignment.get("source_evidence")
        if source_evidence is None:
            source_evidence = {
                "repository": assignment["source_repository"],
                "branch": assignment["source_branch"],
                "sha": assignment["source_sha"],
                "verified": True,
            }
        basis = assignment.get("billing_basis", billing_basis)
        approved = assignment.get("metered_approved", metered_approved)
        attribution = {
            "project_id": assignment["project_id"],
            "engine": role_spec["engine"],
            "provider": role_spec["provider"],
            "capacity_pool": assignment["capacity_pool"],
            "billing_basis": basis,
            "metered_approved": approved,
            "host": assignment["host"],
            "model": role_spec["model"],
            "sandbox_profile": assignment["sandbox_profile"],
            "network_profile": role_spec["network_profile"],
            "source_repository": assignment["source_repository"],
            "source_branch": assignment["source_branch"],
            "source_sha": assignment["source_sha"],
            "source_evidence": source_evidence,
            "allowed_paths": assignment["allowed_paths"],
            "publication_policy": assignment["publication_policy"],
            "default_branch": assignment.get("default_branch", default_branch),
            "integration_branch": assignment.get("integration_branch", integration_branch),
            "assignment": assignment,
            # The runtime schema does not require network_policy in the attribution conditional,
            # but it is role-specific and must follow the same immutable source.
            "network_policy": role_spec["network_policy"],
        }
    except (KeyError, TypeError, AttributeError) as exc:
        raise WorkerEvidenceError("strict assignment cannot provide complete attribution") from exc

    missing = [field for field in ASSIGNMENT_ATTRIBUTION_FIELDS
               if field not in attribution or (
                   field not in {"capacity_pool", "model", "billing_basis"}
                   and attribution[field] is None
               )]
    if missing:
        raise WorkerEvidenceError(
            "strict assignment cannot provide attribution: " + ", ".join(missing)
        )
    if not isinstance(attribution["metered_approved"], bool):
        raise WorkerEvidenceError("strict assignment cannot provide metered approval status")
    if attribution["billing_basis"] == "metered" and attribution["metered_approved"] is not True:
        raise WorkerEvidenceError("strict assignment does not approve metered usage")
    return attribution


def validate_usage(usage: object, assignment: dict | None) -> None:
    if not isinstance(usage, dict):
        raise WorkerEvidenceError("usage evidence must be an object")
    if usage == {}:
        return
    provider = usage.get("provider")
    basis = usage.get("billing_basis")
    if provider is not None and not isinstance(provider, str):
        raise WorkerEvidenceError("usage provider must be a string")
    if basis is not None and not isinstance(basis, str):
        raise WorkerEvidenceError("usage billing basis must be a string")
    if assignment is not None:
        if provider is not None and provider != assignment.get("provider"):
            raise SystemExit("worker-evidence: usage provider disagrees with persisted assignment")
        if basis is not None and basis != assignment.get("billing_basis"):
            raise SystemExit("worker-evidence: usage billing basis disagrees with persisted assignment")
        if assignment.get("billing_basis") == "metered" and not assignment.get("metered_approved"):
            raise SystemExit("worker-evidence: unapproved metered usage is refused")
    for key, minimum in (("tokens", 0), ("cost_usd", 0)):
        item = usage.get(key)
        if item is not None:
            valid = isinstance(item, (int, float)) and not isinstance(item, bool)
            if valid:
                try:
                    valid = math.isfinite(float(item)) and item >= minimum
                except (OverflowError, ValueError, TypeError):
                    valid = False
            if not valid:
                raise WorkerEvidenceError(f"invalid usage {key}")


def _main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    for name in ("path", "run_id", "task_id", "role", "model_alias", "worktree", "base_commit",
                 "log", "network_policy"):
        start.add_argument(f"--{name.replace('_', '-')}", required=True)
    start.add_argument("--pid", required=True, type=int)
    start.add_argument("--process-group", required=True, type=int)
    start.add_argument("--deadline-epoch", required=True, type=int)
    start.add_argument("--deadline-epoch-ns", type=int, default=None)
    start.add_argument("--implementer-run-id", default="")
    start.add_argument("--commit-oid", default="")
    start.add_argument("--seed-evidence", default="")
    start.add_argument("--engine", default="")
    start.add_argument("--provider", default="")
    start.add_argument("--capacity-pool", default="")
    start.add_argument("--model", default="")
    start.add_argument("--host", default="")
    start.add_argument("--sandbox-profile", default="")
    start.add_argument("--billing-basis", default="")
    start.add_argument("--metered-approved", action="store_true", default=False)
    start.add_argument("--default-branch", default="")
    start.add_argument("--integration-branch", default="")
    # Phase 3 (D-016): bind this run to its immutable pre-launch assignment so engine/
    # provider/pool/host/model attribution is read directly off the run record instead of
    # being reconstructed later from a mutable task header (docs/audits/
    # recursion-v2-infrastructure-audit-2026-08-28.md). Both flags are optional together —
    # a caller that omits them gets exactly the pre-Phase-3 record (legacy behavior
    # preserved); a caller that supplies only one is a controller bug, refused (exit 2).
    start.add_argument("--assignment-digest", default="")
    start.add_argument("--assignment-file", default="")
    start.add_argument("--attempt", type=int, default=None)
    prepare = sub.add_parser("prepare")
    for name in ("path", "run_id", "task_id", "role", "model_alias", "worktree", "base_commit",
                 "log", "network_policy"):
        prepare.add_argument(f"--{name.replace('_', '-')}", required=True)
    prepare.add_argument("--deadline-epoch", required=True, type=int)
    prepare.add_argument("--deadline-epoch-ns", type=int, default=None)
    prepare.add_argument("--implementer-run-id", default="")
    prepare.add_argument("--commit-oid", default="")
    prepare.add_argument("--seed-evidence", default="")
    prepare.add_argument("--assignment-digest", required=True)
    prepare.add_argument("--assignment-file", required=True)
    prepare.add_argument("--attempt", type=int, default=None)
    activate = sub.add_parser("activate")
    activate.add_argument("path"); activate.add_argument("pid", type=int); activate.add_argument("process_group", type=int)
    mark_finished = sub.add_parser("mark-finished")
    mark_finished.add_argument("path"); mark_finished.add_argument("finished_epoch_ns", type=int)
    heartbeat = sub.add_parser("heartbeat"); heartbeat.add_argument("path"); heartbeat.add_argument("lease_epoch", type=int)
    finish = sub.add_parser("finish"); finish.add_argument("path"); finish.add_argument("status")
    finish.add_argument("outcome"); finish.add_argument("exit_code", type=int)
    finish.add_argument("--result-file"); finish.add_argument("--scope-file"); finish.add_argument("--usage-file")
    finish.add_argument("--execution-evidence")
    finish.add_argument("--seed-evidence")
    finish.add_argument("--seed-verified-after", action="store_true")
    finish.add_argument("--keep-open", action="store_true")
    finish.add_argument("--commit-oid", default="")
    seal = sub.add_parser("seal"); seal.add_argument("path"); seal.add_argument("status")
    seal.add_argument("outcome"); seal.add_argument("exit_code", type=int)
    provision = sub.add_parser("provision-key"); provision.add_argument("--controller-root", required=True)
    gate = sub.add_parser("gate"); gate.add_argument("path"); gate.add_argument("commit_oid")
    gate.add_argument("acceptance"); gate.add_argument("exit_code", type=int); gate.add_argument("log")
    verify = sub.add_parser("verify"); verify.add_argument("path"); verify.add_argument("commit_oid")
    verify.add_argument("implementer_run_id"); verify.add_argument("verdict_file")
    link = sub.add_parser("link-verifier"); link.add_argument("path"); link.add_argument("verifier_run_id")
    link.add_argument("commit_oid"); link.add_argument("verdict_file")
    remote = sub.add_parser("remote-evidence")
    remote.add_argument("path")
    remote.add_argument("--session-id", default="")
    remote.add_argument("--branch", default="")
    remote.add_argument("--commit", default="")
    remote.add_argument("--artifact", action="append", default=[], help="relative/path=sha256")
    remote.add_argument("--event-type", choices=["session", "result", "artifact", "cancel", "terminal"], default="result")
    remote.add_argument("--terminal-status", choices=["succeeded", "failed", "cancelled"], default="")
    remote.add_argument("--cancelled-at", default="")
    remote.add_argument("--cancellation-reason", default="")
    args = parser.parse_args()
    path_arg = getattr(args, "path", None)
    path = Path(path_arg) if path_arg else None

    if args.command == "provision-key":
        provision_evidence_key(args.controller_root)
        return 0

    if args.command == "start":
        if args.pid < 1 or args.process_group < 1 or args.deadline_epoch < 0:
            raise SystemExit("worker-evidence: invalid process identity")
        if not args.assignment_file or not args.assignment_digest:
            raise SystemExit("worker-evidence: strict evidence requires an immutable assignment")
        value = {"schema_version": 1, "id": args.run_id, "task_id": args.task_id,
                 "worker": f"{args.role}:{args.model_alias}", "role": args.role,
                 "model_alias": args.model_alias, "worktree": args.worktree,
                 "base_commit": args.base_commit, "pid": args.pid, "process_group": args.process_group,
                 "lease_expires": iso(args.deadline_epoch), "deadline": iso(args.deadline_epoch),
                 "deadline_epoch": args.deadline_epoch, "network_policy": args.network_policy,
                 "heartbeat_at": now(), "log": args.log, "usage": {}, "result": {},
                 "changed_files": [], "status": "running", "started_at": now()}
        if args.deadline_epoch_ns is not None:
            value["deadline_epoch_ns"] = args.deadline_epoch_ns
        if args.implementer_run_id:
            value["implementer_run_id"] = args.implementer_run_id
        if args.commit_oid:
            value["verification_commit"] = args.commit_oid
        for field in ("engine", "provider", "capacity_pool", "model", "host", "sandbox_profile", "assignment_digest"):
            supplied = getattr(args, field)
            if supplied:
                value[field] = supplied
        if args.assignment_file:
            assignment_path = Path(args.assignment_file)
            assignment, computed = load_assignment(assignment_path)
            assignment_path = Path(absolute_lexical(assignment_path))
            if args.assignment_digest and args.assignment_digest != computed:
                raise SystemExit("worker-evidence: assignment digest mismatch")
            role_spec = assignment.get("role_assignments", {}).get(args.role, assignment)
            for field in ("engine", "provider", "capacity_pool", "model", "host", "sandbox_profile"):
                supplied = getattr(args, field)
                expected = role_spec.get(field, assignment.get(field, ""))
                if supplied and expected and supplied != expected:
                    raise SystemExit(f"worker-evidence: assignment {field} mismatch")
            if args.network_policy != role_spec.get("network_policy", assignment.get("network_policy")):
                raise SystemExit("worker-evidence: assignment network policy mismatch")
            attribution = assignment_attribution(
                assignment, args.role, billing_basis=args.billing_basis,
                metered_approved=args.metered_approved,
                default_branch=args.default_branch,
                integration_branch=args.integration_branch,
            )
            value.update(attribution)
            value["assignment_digest"] = computed
            value["assignment_file"] = str(assignment_path)
        binding = {
            "schema_version": 1, "kind": START_EVIDENCE_KIND, "run_id": args.run_id,
            "task_id": args.task_id, "role": args.role,
            "evidence_path": os.path.normcase(os.path.abspath(str(path))),
            "worktree": value["worktree"],
            "assignment_file": value["assignment_file"],
            "assignment_digest": value["assignment_digest"], "assignment": value["assignment"],
            "attribution": attribution,
        }
        seed = maybe_json(args.seed_evidence)
        if isinstance(seed, dict) and seed:
            value["seed_evidence"] = seed
        if args.attempt is not None:
            if args.attempt < 1: raise SystemExit(2)
            value["attempt"] = args.attempt
        validate_run_evidence(value)
        key = load_evidence_key(value["assignment"]["controller_repository"])
        write_start_evidence(start_evidence_path(path), binding, key)
        atomic(path, value); return 0

    if args.command == "prepare":
        assignment = assignment_from(args.assignment_file, args.assignment_digest, args.task_id, args.role, Path(args.path))
        value = {"schema_version": 1, "id": args.run_id, "task_id": args.task_id,
                 "worker": f"{args.role}:{args.model_alias}", "role": args.role,
                 "model_alias": args.model_alias, "worktree": args.worktree,
                 "base_commit": args.base_commit, "pid": 0, "process_group": 0,
                 "lease_expires": iso(args.deadline_epoch), "deadline": iso(args.deadline_epoch),
                 "deadline_epoch": args.deadline_epoch, "network_policy": args.network_policy,
                 "heartbeat_at": now(), "log": args.log, "usage": {}, "result": {},
                 "changed_files": [], "status": "prepared", "started_at": now(),
                 "assignment": copy_assignment(assignment)}
        if args.deadline_epoch_ns is not None:
            value["deadline_epoch_ns"] = args.deadline_epoch_ns
        value.update(copy_assignment(assignment))
        if args.attempt is not None:
            if args.attempt < 1: raise SystemExit(2)
            value["attempt"] = args.attempt
        if args.implementer_run_id: value["implementer_run_id"] = args.implementer_run_id
        if args.commit_oid: value["verification_commit"] = args.commit_oid
        seed = maybe_json(args.seed_evidence)
        if isinstance(seed, dict) and seed: value["seed_evidence"] = seed
        validate_run_evidence(value)
        atomic(Path(args.path), value); return 0

    if args.command == "activate":
        if args.pid < 1 or args.process_group < 1: raise SystemExit(2)
        value = load(path)
        if value.get("status") != "prepared": raise SystemExit(2)
        value.update(pid=args.pid, process_group=args.process_group, status="running", started_at=now())
        atomic(path, value); return 0

    if args.command == "mark-finished":
        value = load(path)
        # This command boundary deliberately keeps its own negative-value guard even though
        # validate_run_evidence(value) below rejects the same field.  The specific downstream
        # validator is validate_run_evidence; keeping this guard preserves mark-finished's
        # invalid-argument exit 2 contract instead of exposing its generic evidence error exit 1.
        if args.finished_epoch_ns < 0 or value.get("status") != "running":
            raise SystemExit(2)
        value["worker_finished_epoch_ns"] = args.finished_epoch_ns
        validate_run_evidence(value)
        atomic(path, value); return 0

    if args.command == "remote-evidence":
        from remote_evidence import RemoteEvidenceError, append_remote_event
        value = load(path)
        digest = value.get("assignment_digest")
        if digest:
            try: assignment_mod.validate_assignment(value.get("assignment"), require_source_evidence=True)
            except assignment_mod.AssignmentError as exc:
                raise WorkerEvidenceError("assignment is invalid") from exc
        try:
            event = append_remote_event(
                path=path, run=value, event_type=args.event_type, session_id=args.session_id,
                branch=args.branch, commit=args.commit, artifacts=args.artifact,
                cancelled_at=args.cancelled_at, cancellation_reason=args.cancellation_reason,
                terminal_status=args.terminal_status,
            )
        except RemoteEvidenceError as exc:
            raise WorkerEvidenceError("remote evidence is invalid") from exc
        print(json.dumps(event, sort_keys=True)); return 0

    if path is None:
        raise SystemExit("worker-evidence: evidence path is required")
    value = load(path)
    start_binding = load_start_evidence(path)
    for field, start_field in (("id", "run_id"), ("task_id", "task_id"), ("role", "role")):
        if field in value and value[field] != start_binding[start_field]:
            raise SystemExit(f"worker-evidence: mutable run identity changed: {field}")
    assignment = refresh_assignment(value, start_binding)
    terminal_statuses = {"succeeded", "failed", "blocked", "cancelled", "stale"}
    if value.get("status") in terminal_statuses:
        raise SystemExit("worker-evidence: terminal run metadata is immutable")
    # Every record produced by start is strict.  This decision comes from the
    # authenticated durable start binding, never from mutable run JSON fields.
    strict_run = start_binding["kind"] == START_EVIDENCE_KIND
    if not strict_run:
        raise SystemExit("worker-evidence: immutable start evidence is not strict")
    value["assignment_file"] = start_binding["assignment_file"]
    value["assignment_digest"] = start_binding["assignment_digest"]
    value["assignment"] = assignment
    value.update(start_binding["attribution"])
    if args.command == "heartbeat":
        if args.lease_epoch < 0:
            raise WorkerEvidenceError("invalid heartbeat lease epoch")
        value["heartbeat_at"] = now(); value["lease_expires"] = iso(args.lease_epoch)
    elif args.command == "finish":
        if args.status not in terminal_statuses:
            raise SystemExit("worker-evidence: finish status must be terminal")
        result = maybe_json(args.result_file)
        if not isinstance(result, (dict, str)):
            raise WorkerEvidenceError("finish result must be an object or string")
        value["result"] = result
        scope = maybe_json(args.scope_file)
        if isinstance(scope, dict):
            value["changed_files"] = scope.get("entries", [])
        usage = maybe_json(args.usage_file)
        validate_usage(usage, value.get("assignment") if value.get("assignment_digest") else None)
        if isinstance(usage, dict):
            value["usage"] = usage
        if not args.execution_evidence:
            raise SystemExit("worker-evidence: strict execution evidence is required to finish")
        execution_run = dict(value)
        execution_run.update(status=args.status, outcome=args.outcome, exit_code=args.exit_code)
        execution = validate_execution_evidence(
            maybe_json(args.execution_evidence), execution_run, assignment,
        )
        value["execution"] = execution
        if args.commit_oid:
            value["commit_oid"] = args.commit_oid
        seed = maybe_json(args.seed_evidence)
        if isinstance(seed, dict) and seed:
            seed = dict(seed)
            if args.seed_verified_after:
                seed["verified_after"] = True
            value["seed_evidence"] = seed
        if args.keep_open:
            value["worker_finished_at"] = now()
        else:
            value.update(status=args.status, outcome=args.outcome, exit_code=args.exit_code,
                         finished_at=now(), lease_expires="0")
    elif args.command == "seal":
        if args.status not in terminal_statuses:
            raise SystemExit("worker-evidence: seal status must be terminal")
        if value.get("status") != "running":
            raise SystemExit("worker-evidence: only a running record can be sealed")
        execution = value.get("execution")
        if not isinstance(execution, dict):
            raise SystemExit("worker-evidence: cannot seal without execution evidence")
        execution_run = dict(value)
        execution_run.update(status=args.status, exit_code=args.exit_code)
        validate_execution_evidence(execution, execution_run, assignment)
        value.update(status=args.status, outcome=args.outcome, exit_code=args.exit_code,
                     finished_at=now(), lease_expires="0")
    elif args.command == "gate":
        if assignment is None:
            raise SystemExit("worker-evidence: gate evidence has no validated assignment provenance")
        if value.get("worktree") != start_binding["worktree"]:
            raise SystemExit("worker-evidence: gate worktree binding changed")
        try:
            validate_bound_gate_files(assignment, start_binding["worktree"])
        except ContractAssignmentError as exc:
            raise SystemExit(f"worker-evidence: assigned gate bytes changed: {exc}") from exc
        contract = assignment["gate_contract"]
        if args.acceptance != contract["acceptance"]:
            raise SystemExit("worker-evidence: gate command does not match the assigned acceptance program")
        expected_acceptance = contract["acceptance_sha256"]
        observed_acceptance = hashlib.sha256(args.acceptance.encode()).hexdigest()
        if observed_acceptance != expected_acceptance:
            raise SystemExit("worker-evidence: gate command does not match the assigned gate contract")
        value["machine_gate"] = {"commit_oid": args.commit_oid,
                                  "acceptance_sha256": hashlib.sha256(args.acceptance.encode()).hexdigest(),
                                  "gate_contract_digest": assignment["gate_digest"],
                                  "acceptance": args.acceptance,
                                  "exit_code": args.exit_code, "passed": args.exit_code == 0,
                                  "log": args.log, "checked_at": now()}
    elif args.command == "verify":
        verdict = maybe_json(args.verdict_file)
        value["verification"] = {"commit_oid": args.commit_oid,
                                  "implementer_run_id": args.implementer_run_id,
                                  "verdict": verdict.get("verdict") if isinstance(verdict, dict) else None,
                                  "evidence": verdict, "checked_at": now()}
        value["result"] = verdict
    elif args.command == "link-verifier":
        verdict = maybe_json(args.verdict_file)
        value["verification"] = {"verifier_run_id": args.verifier_run_id,
                                  "commit_oid": args.commit_oid,
                                  "verdict": verdict.get("verdict") if isinstance(verdict, dict) else None,
                                  "evidence": verdict, "checked_at": now()}
    validate_run_evidence(value)
    atomic(path, value)
    return 0


def main() -> int:
    try:
        return _main()
    except WorkerEvidenceError as exc:
        raise SystemExit(f"worker-evidence: {exc}") from None
    except (OSError, JsonlDurabilityError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit("worker-evidence: invalid input or durable state") from None


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FirstPartyImportError as exc:
        print(f"worker-evidence: first-party import failed: {exc}", file=sys.stderr)
        raise SystemExit(95)
    except (ContractAssignmentError, BoundaryError, OSError, UnicodeDecodeError,
            json.JSONDecodeError, ValueError, TypeError, OverflowError,
            RecursionError, KeyError, IndexError, AttributeError) as exc:
        print(f"worker-evidence: invalid evidence transition: {exc}", file=sys.stderr)
        raise SystemExit(2)

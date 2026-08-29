#!/usr/bin/env python3
"""Atomic Phase 5 run evidence for implementers and independent verifiers."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
from pathlib import Path

sys_path = Path(__file__).parent
if str(sys_path) not in sys.path:
    sys.path.insert(0, str(sys_path))
from assignment import (AssignmentError, canonical_bytes, load_assignment,
                        validate_assignment as assignment_validate,
                        validate_execution_evidence as assignment_execution_evidence)
from phase5_safety import (BoundaryError, atomic_write, decode_json,
                           read_bytes, ensure_directory, absolute_lexical, MAX_JSON_BYTES)


START_EVIDENCE_KIND = "worker-evidence-start-v1"
START_FIELDS = {
    "schema_version", "kind", "run_id", "task_id", "role", "evidence_path",
    "assignment_file", "assignment_digest", "assignment",
}


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def iso(epoch: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def load(path: Path) -> dict:
    try:
        value = decode_json(read_bytes(path, label="evidence file"), "evidence file")
    except (BoundaryError, OSError, UnicodeDecodeError, json.JSONDecodeError,
            ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise SystemExit("worker-evidence: evidence file is unreadable") from exc
    if not isinstance(value, dict):
        raise SystemExit("worker-evidence: evidence file must contain an object")
    return value


def atomic(path: Path, value: dict) -> None:
    try:
        encoded = (json.dumps(value, indent=2, sort_keys=True,
                              allow_nan=False) + "\n").encode("utf-8")
        atomic_write(path, encoded, replace=True, mode=0o600, label="evidence output")
    except (BoundaryError, OSError, TypeError, ValueError, OverflowError,
            RecursionError) as exc:
        raise SystemExit("worker-evidence: evidence output could not be published") from exc


def start_evidence_path(path: Path) -> Path:
    """Return the non-run-glob sidecar that records the immutable start binding."""
    absolute = Path(absolute_lexical(path))
    return absolute.with_name(f".{absolute.name}.start")


def evidence_key_path(controller_repository: str) -> Path:
    override = os.environ.get("RECURSION_EVIDENCE_KEY_FILE", "").strip()
    if override:
        return Path(override)
    return Path(controller_repository) / "state" / ".worker-evidence.key"


def load_evidence_key(controller_repository: str) -> bytes:
    path = evidence_key_path(controller_repository)
    try:
        key = read_bytes(path, label="worker evidence key", max_bytes=1024,
                         private=True)
        if not key or len(key) < 32:
            raise BoundaryError("worker evidence key is too short")
        return key
    except BoundaryError as missing:
        # The controller's first strict start provisions the key in its own state
        # tree.  The key never lives in the run directory and is never emitted.
        try:
            ensure_directory(path.parent)
            try:
                atomic_write(path, secrets.token_bytes(32), replace=False,
                             mode=0o600, label="worker evidence key")
            except BoundaryError as provision_error:
                # Another legitimate strict start may win first-key provisioning.  Only
                # accept that race by re-opening the existing controller-owned key below;
                # malformed or unsafe replacements still fail closed in read_bytes().
                if "already exists" not in str(provision_error):
                    raise
            key = read_bytes(path, label="worker evidence key", max_bytes=1024,
                             private=True)
            if len(key) < 32:
                raise BoundaryError("worker evidence key is too short")
            return key
        except (BoundaryError, OSError, TypeError, ValueError, OverflowError,
                RecursionError) as exc:
            raise SystemExit("worker-evidence: authenticated evidence key is unavailable") from exc


def _binding_mac(value: dict, key: bytes) -> str:
    try:
        payload = canonical_bytes(value)
        return hmac.new(key, payload, hashlib.sha256).hexdigest()
    except (AssignmentError, TypeError, ValueError, OverflowError,
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
    except AssignmentError as exc:
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
    except AssignmentError as exc:
        raise SystemExit(f"worker-evidence: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    for name in ("path", "run_id", "task_id", "role", "model_alias", "worktree", "base_commit",
                 "log", "network_policy"):
        start.add_argument(f"--{name.replace('_', '-')}", required=True)
    start.add_argument("--pid", required=True, type=int)
    start.add_argument("--process-group", required=True, type=int)
    start.add_argument("--deadline-epoch", required=True, type=int)
    start.add_argument("--implementer-run-id", default="")
    start.add_argument("--commit-oid", default="")
    start.add_argument("--seed-evidence", default="")
    start.add_argument("--engine", default="")
    start.add_argument("--provider", default="")
    start.add_argument("--capacity-pool", default="")
    start.add_argument("--model", default="")
    start.add_argument("--host", default="")
    start.add_argument("--sandbox-profile", default="")
    start.add_argument("--assignment-digest", default="")
    start.add_argument("--assignment-file", default="")
    heartbeat = sub.add_parser("heartbeat"); heartbeat.add_argument("path"); heartbeat.add_argument("lease_epoch", type=int)
    finish = sub.add_parser("finish"); finish.add_argument("path"); finish.add_argument("status")
    finish.add_argument("outcome"); finish.add_argument("exit_code", type=int)
    finish.add_argument("--result-file"); finish.add_argument("--scope-file"); finish.add_argument("--usage-file")
    finish.add_argument("--execution-evidence")
    finish.add_argument("--seed-evidence")
    finish.add_argument("--seed-verified-after", action="store_true")
    finish.add_argument("--commit-oid", default="")
    gate = sub.add_parser("gate"); gate.add_argument("path"); gate.add_argument("commit_oid")
    gate.add_argument("acceptance"); gate.add_argument("exit_code", type=int); gate.add_argument("log")
    verify = sub.add_parser("verify"); verify.add_argument("path"); verify.add_argument("commit_oid")
    verify.add_argument("implementer_run_id"); verify.add_argument("verdict_file")
    link = sub.add_parser("link-verifier"); link.add_argument("path"); link.add_argument("verifier_run_id")
    link.add_argument("commit_oid"); link.add_argument("verdict_file")
    args = parser.parse_args(); path = Path(getattr(args, "path"))

    if args.command == "start":
        if args.pid < 1 or args.process_group < 1:
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
            value["assignment"] = assignment
            value["assignment_digest"] = computed
            value["assignment_file"] = str(assignment_path)
        binding = {
            "schema_version": 1, "kind": START_EVIDENCE_KIND, "run_id": args.run_id,
            "task_id": args.task_id, "role": args.role,
            "evidence_path": os.path.normcase(os.path.abspath(str(path))),
            "assignment_file": value["assignment_file"],
            "assignment_digest": value["assignment_digest"], "assignment": value["assignment"],
        }
        key = load_evidence_key(value["assignment"]["controller_repository"])
        write_start_evidence(start_evidence_path(path), binding, key)
        seed = maybe_json(args.seed_evidence)
        if isinstance(seed, dict) and seed:
            value["seed_evidence"] = seed
        atomic(path, value); return 0

    value = load(path)
    start_binding = load_start_evidence(path)
    for field, start_field in (("id", "run_id"), ("task_id", "task_id"), ("role", "role")):
        if field in value and value[field] != start_binding[start_field]:
            raise SystemExit(f"worker-evidence: mutable run identity changed: {field}")
    assignment = refresh_assignment(value, start_binding)
    # Every record produced by start is strict.  This decision comes from the
    # authenticated durable start binding, never from mutable run JSON fields.
    strict_run = start_binding["kind"] == START_EVIDENCE_KIND
    if not strict_run:
        raise SystemExit("worker-evidence: immutable start evidence is not strict")
    value["assignment_file"] = start_binding["assignment_file"]
    value["assignment_digest"] = start_binding["assignment_digest"]
    value["assignment"] = assignment
    if args.command == "heartbeat":
        value["heartbeat_at"] = now(); value["lease_expires"] = iso(args.lease_epoch)
    elif args.command == "finish":
        value.update(status=args.status, outcome=args.outcome, exit_code=args.exit_code,
                     finished_at=now(), lease_expires="0")
        value["result"] = maybe_json(args.result_file)
        scope = maybe_json(args.scope_file)
        if isinstance(scope, dict):
            value["changed_files"] = scope.get("entries", [])
        usage = maybe_json(args.usage_file)
        if isinstance(usage, dict):
            value["usage"] = usage
        if not args.execution_evidence:
            raise SystemExit("worker-evidence: strict execution evidence is required to finish")
        execution = validate_execution_evidence(maybe_json(args.execution_evidence), value, assignment)
        value["execution"] = execution
        if args.commit_oid:
            value["commit_oid"] = args.commit_oid
        seed = maybe_json(args.seed_evidence)
        if isinstance(seed, dict) and seed:
            seed = dict(seed)
            if args.seed_verified_after:
                seed["verified_after"] = True
            value["seed_evidence"] = seed
    elif args.command == "gate":
        if assignment is None:
            raise SystemExit("worker-evidence: gate evidence has no validated assignment provenance")
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
    atomic(path, value)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssignmentError, BoundaryError, OSError, UnicodeDecodeError,
            json.JSONDecodeError, ValueError, TypeError, OverflowError,
            RecursionError, KeyError, IndexError, AttributeError) as exc:
        print(f"worker-evidence: invalid evidence transition: {exc}", file=sys.stderr)
        raise SystemExit(2)

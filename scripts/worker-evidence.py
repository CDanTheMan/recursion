#!/usr/bin/env python3
"""Atomic Phase 5 run evidence for implementers and independent verifiers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import assignment as assignment_mod
from jsonl_durable import (
    JsonlDurabilityError, atomic_bytes, read_durable_bytes,
)


class WorkerEvidenceError(Exception):
    """Malformed or unsafe evidence input refused before durable publication."""


_atomic_publish_hook = None

RUN_STATUSES = frozenset({
    "pending", "prepared", "running", "succeeded", "failed", "blocked", "cancelled", "stale",
})


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def iso(epoch: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def load(path: Path) -> dict:
    try:
        if not isinstance(path, Path):
            raise WorkerEvidenceError("run evidence path must be a path")
        raw = read_durable_bytes(path)
        if raw is None:
            raise OSError(f"run evidence is absent: {path}")
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, JsonlDurabilityError,
            TypeError, ValueError,
            OverflowError, RecursionError) as exc:
        raise WorkerEvidenceError(f"run evidence is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise WorkerEvidenceError("run evidence is not an object")
    digest = value.get("assignment_digest")
    if digest:
        parent = path.parent
        assignment_root = parent.parent / "assignments" if parent.name == "runs" else parent / "assignments"
        persisted = assignment_mod.load_assignment(assignment_root, str(value.get("task_id") or ""), str(digest))
        try:
            assignment_mod.validate_assignment(persisted, require_source_evidence=True)
        except assignment_mod.AssignmentError as exc:
            raise SystemExit(f"worker-evidence: persisted assignment is unusable: {exc}") from exc
        try:
            assignment_mod.require_assignment_projection(value, persisted)
        except assignment_mod.AssignmentError as exc:
            raise SystemExit(f"worker-evidence: run attribution disagrees with persisted assignment: {exc}") from exc
    return value


def atomic(path: Path, value: dict) -> None:
    if not isinstance(path, Path) or not isinstance(value, dict):
        raise WorkerEvidenceError("evidence publication requires a path and object")
    try:
        encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
        atomic_bytes(path, encoded, hook=_atomic_publish_hook)
    except (JsonlDurabilityError, OSError, TypeError, ValueError, OverflowError,
            RecursionError, UnicodeEncodeError) as exc:
        raise WorkerEvidenceError(f"evidence publication refused: {path}") from exc


def maybe_json(path: str | None) -> object:
    try:
        if path is None:
            return {}
        if not isinstance(path, str):
            raise WorkerEvidenceError("evidence input path must be a string")
        if not path:
            return {}
        candidate = Path(path)
        raw = read_durable_bytes(candidate)
    except (OSError, JsonlDurabilityError, TypeError, ValueError, OverflowError,
            RecursionError, UnicodeDecodeError) as exc:
        raise WorkerEvidenceError("evidence input path is invalid") from exc
    if raw is None:
        return {}
    # The sandbox pre-truncates the hermes usage file before mounting it; a worker that exits
    # without writing leaves it empty. An empty file means "no usage data", the same fact as
    # an absent file — it must not crash `finish` and lose the whole run record.
    try:
        text = raw.decode("utf-8")
    except (UnicodeDecodeError, TypeError, ValueError) as exc:
        raise WorkerEvidenceError(f"evidence input is unreadable: {path}") from exc
    if not text.strip():
        return {}
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError) as exc:
        raise WorkerEvidenceError(f"evidence input is not valid JSON: {path}") from exc


def assignment_from(path: str, digest: str, task_id: str, role: str = "", run_path: Path | None = None) -> dict:
    if run_path is not None:
        parent = run_path.parent
        assignment_root = parent.parent / "assignments" if parent.name == "runs" else parent / "assignments"
        try:
            expected = assignment_mod.assignment_path(assignment_root, task_id, digest)
        except assignment_mod.AssignmentError as exc:
            raise SystemExit(2) from exc
        if os.path.realpath(path) != os.path.realpath(expected):
            raise SystemExit(2)
    try:
        raw = read_durable_bytes(Path(path))
        if raw is None:
            raise OSError(f"assignment is absent: {path}")
        value = json.loads(raw.decode("utf-8"))
        assignment_mod.validate_assignment(value, require_source_evidence=True)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, JsonlDurabilityError,
            TypeError, ValueError,
            OverflowError, RecursionError, assignment_mod.AssignmentError) as exc:
        raise SystemExit(f"worker-evidence: invalid persisted assignment: {exc}") from exc
    if value.get("assignment_digest") != digest or value.get("task_id") != task_id \
            or (role and value.get("role") != role):
        raise SystemExit(2)
    return value


def copy_assignment(value: dict) -> dict:
    return assignment_mod.assignment_projection(value)


def validate_usage(usage: object, assignment: dict | None) -> None:
    if assignment is None or not isinstance(usage, dict) or not usage:
        return
    provider = usage.get("provider")
    basis = usage.get("billing_basis")
    if provider is not None and provider != assignment.get("provider"):
        raise SystemExit("worker-evidence: usage provider disagrees with persisted assignment")
    if basis is not None and basis != assignment.get("billing_basis"):
        raise SystemExit("worker-evidence: usage billing basis disagrees with persisted assignment")
    if assignment.get("billing_basis") == "metered" and not assignment.get("metered_approved"):
        raise SystemExit("worker-evidence: unapproved metered usage is refused")
    for key, minimum in (("tokens", 0), ("cost_usd", 0)):
        item = usage.get(key)
        if item is not None and (isinstance(item, bool) or not isinstance(item, (int, float)) or item < minimum):
            raise SystemExit(f"worker-evidence: invalid usage {key}")


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
    start.add_argument("--implementer-run-id", default="")
    start.add_argument("--commit-oid", default="")
    start.add_argument("--seed-evidence", default="")
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
    prepare.add_argument("--implementer-run-id", default="")
    prepare.add_argument("--commit-oid", default="")
    prepare.add_argument("--seed-evidence", default="")
    prepare.add_argument("--assignment-digest", required=True)
    prepare.add_argument("--assignment-file", required=True)
    prepare.add_argument("--attempt", type=int, default=None)
    activate = sub.add_parser("activate")
    activate.add_argument("path"); activate.add_argument("pid", type=int); activate.add_argument("process_group", type=int)
    heartbeat = sub.add_parser("heartbeat"); heartbeat.add_argument("path"); heartbeat.add_argument("lease_epoch", type=int)
    finish = sub.add_parser("finish"); finish.add_argument("path"); finish.add_argument("status")
    finish.add_argument("outcome"); finish.add_argument("exit_code", type=int)
    finish.add_argument("--result-file"); finish.add_argument("--scope-file"); finish.add_argument("--usage-file")
    finish.add_argument("--seed-evidence")
    finish.add_argument("--seed-verified-after", action="store_true")
    finish.add_argument("--commit-oid", default="")
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
    args = parser.parse_args(); path = Path(getattr(args, "path"))

    if args.command == "start":
        if args.pid < 1 or args.process_group < 1:
            raise SystemExit("worker-evidence: invalid process identity")
        if bool(args.assignment_digest) != bool(args.assignment_file):
            raise SystemExit(2)
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
        seed = maybe_json(args.seed_evidence)
        if isinstance(seed, dict) and seed:
            value["seed_evidence"] = seed
        if args.assignment_digest:
            assignment = assignment_from(args.assignment_file, args.assignment_digest, args.task_id, args.role, path)
            value["assignment"] = copy_assignment(assignment)
            value.update(copy_assignment(assignment))
        if args.attempt is not None:
            if args.attempt < 1: raise SystemExit(2)
            value["attempt"] = args.attempt
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
        value.update(copy_assignment(assignment))
        if args.attempt is not None:
            if args.attempt < 1: raise SystemExit(2)
            value["attempt"] = args.attempt
        if args.implementer_run_id: value["implementer_run_id"] = args.implementer_run_id
        if args.commit_oid: value["verification_commit"] = args.commit_oid
        seed = maybe_json(args.seed_evidence)
        if isinstance(seed, dict) and seed: value["seed_evidence"] = seed
        atomic(Path(args.path), value); return 0

    if args.command == "activate":
        if args.pid < 1 or args.process_group < 1: raise SystemExit(2)
        value = load(path)
        if value.get("status") != "prepared": raise SystemExit(2)
        value.update(pid=args.pid, process_group=args.process_group, status="running", started_at=now())
        atomic(path, value); return 0

    if args.command == "remote-evidence":
        from remote_evidence import RemoteEvidenceError, append_remote_event
        value = load(path)
        digest = value.get("assignment_digest")
        if digest:
            try: assignment_mod.validate_assignment(value.get("assignment"), require_source_evidence=True)
            except assignment_mod.AssignmentError as exc: raise SystemExit(str(exc)) from exc
        try:
            event = append_remote_event(
                path=path, run=value, event_type=args.event_type, session_id=args.session_id,
                branch=args.branch, commit=args.commit, artifacts=args.artifact,
                cancelled_at=args.cancelled_at, cancellation_reason=args.cancellation_reason,
                terminal_status=args.terminal_status,
            )
        except RemoteEvidenceError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(event, sort_keys=True)); return 0

    value = load(path)
    if args.command == "heartbeat":
        value["heartbeat_at"] = now(); value["lease_expires"] = iso(args.lease_epoch)
    elif args.command == "finish":
        if args.status not in RUN_STATUSES:
            raise WorkerEvidenceError(f"finish status is not in the run schema enum: {args.status!r}")
        result = maybe_json(args.result_file)
        if not isinstance(result, (dict, str)):
            raise WorkerEvidenceError("finish result must be an object or string")
        value.update(status=args.status, outcome=args.outcome, exit_code=args.exit_code,
                     finished_at=now(), lease_expires="0")
        value["result"] = result
        scope = maybe_json(args.scope_file)
        if isinstance(scope, dict):
            value["changed_files"] = scope.get("entries", [])
        usage = maybe_json(args.usage_file)
        validate_usage(usage, value.get("assignment") if value.get("assignment_digest") else None)
        if isinstance(usage, dict):
            value["usage"] = usage
        if args.commit_oid:
            value["commit_oid"] = args.commit_oid
        seed = maybe_json(args.seed_evidence)
        if isinstance(seed, dict) and seed:
            seed = dict(seed)
            if args.seed_verified_after:
                seed["verified_after"] = True
            value["seed_evidence"] = seed
    elif args.command == "gate":
        value["machine_gate"] = {"commit_oid": args.commit_oid,
                                  "acceptance_sha256": hashlib.sha256(args.acceptance.encode()).hexdigest(),
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


def main() -> int:
    try:
        return _main()
    except WorkerEvidenceError as exc:
        raise SystemExit(f"worker-evidence: {exc}") from None
    except (OSError, JsonlDurabilityError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"worker-evidence: invalid input or durable state: {exc}") from None


if __name__ == "__main__":
    raise SystemExit(main())

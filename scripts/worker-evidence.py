#!/usr/bin/env python3
"""Atomic Phase 5 run evidence for implementers and independent verifiers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys_path = Path(__file__).resolve().parent
if str(sys_path) not in sys.path:
    sys.path.insert(0, str(sys_path))
from assignment import load_assignment


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def iso(epoch: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            json.dump(value, out, indent=2, sort_keys=True)
            out.write("\n"); out.flush(); os.fsync(out.fileno())
        os.replace(name, path)
        if os.name != "nt":  # directory fds cannot be opened on Windows (same guard as the sibling modules)
            dfd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def maybe_json(path: str | None) -> object:
    if not path or not Path(path).is_file():
        return {}
    # The sandbox pre-truncates the hermes usage file before mounting it; a worker that exits
    # without writing leaves it empty. An empty file means "no usage data", the same fact as
    # an absent file — it must not crash `finish` and lose the whole run record.
    raw = Path(path).read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    return json.loads(raw)


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
            if not assignment_path.is_file() or assignment_path.is_symlink():
                raise SystemExit("worker-evidence: assignment file must be a regular non-symlink file")
            assignment, computed = load_assignment(assignment_path)
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
        seed = maybe_json(args.seed_evidence)
        if isinstance(seed, dict) and seed:
            value["seed_evidence"] = seed
        atomic(path, value); return 0

    value = load(path)
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
        execution = maybe_json(args.execution_evidence)
        if isinstance(execution, dict):
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


if __name__ == "__main__":
    raise SystemExit(main())

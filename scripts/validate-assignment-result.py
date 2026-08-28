#!/usr/bin/env python3
"""Bind a returned run result to its exact persisted assignment, fail closed (Phase 3).

Generalizes the existing exact-commit binding already enforced elsewhere in the pipeline
(validate-verifier-result.py's --commit/--implementer-run check; work.sh's
phase5_assert_gate_commit re-check of CANDIDATE_OID) to full assignment identity: engine,
provider, capacity pool, model, host, sandbox, and source, not just a commit hash.

Refuses, with a distinct exit code per docs/plans/recursion-v2-execution-fabric.md Phase 3's
gate ("fail closed on late, duplicate, mismatched, or unauthorized results"):

  0  accepted — the result is bound to its assignment, on time, once, and in scope
  2  mismatched — the assignment record is missing/unreadable, tampered (its own content no
     longer hashes to its filename), or the run evidence names a different assignment digest
  3  late — received after the run's own recorded deadline
  4  duplicate — this exact run_id was already accepted once (durably recorded)
  5  unauthorized — the returned repository/branch/paths are outside what was assigned, or the
     branch is a protected default-branch name (D-016 invariant #6: no worker writes default
     or integration branches directly)
  6  source-unavailable — no assignment record exists for the given task_id/digest at all
"""

from __future__ import annotations

import argparse
import calendar
import json
import sys
import time
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assignment as assignment_mod  # noqa: E402
from jsonl_durable import JsonlDurabilityError, append_jsonl, find_jsonl_objects  # noqa: E402

PROG = "validate-assignment-result"
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
PROTECTED_BRANCHES = frozenset({"main", "master", "recursion/integration"})
SHA_RE = assignment_mod.SHA_RE


class RefusalError(Exception):
    def __init__(self, code: int, reason: str) -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def now_epoch() -> int:
    return int(time.time())


def _epoch_of(text: str | None) -> int | None:
    if not text:
        return None
    try:
        return calendar.timegm(time.strptime(text, TS_FORMAT))
    except ValueError:
        return None


def results_ledger(root: Path) -> Path:
    return root / "results.jsonl"


def path_within_allowed(path: str, allowed_paths: list[str]) -> bool:
    try:
        if not isinstance(path, str) or not path or path != path.strip() or "\\" in path:
            return False
        if path.startswith("/") or __import__("re").match(r"^[A-Za-z]:", path):
            return False
        parts = PurePosixPath(path).parts
        if not parts or any(part in {".", ".."} for part in parts):
            return False
        normalized = PurePosixPath(*parts).as_posix()
        if normalized != path:
            return False
    except (TypeError, ValueError):
        return False
    for prefix in allowed_paths:
        prefix = prefix.rstrip("/")
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return True
    return False


def load_run_evidence(path: str) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RefusalError(2, f"run evidence unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise RefusalError(2, "run evidence is not a JSON object")
    return value


def check(args: argparse.Namespace) -> dict:
    root = Path(args.assignment_root) if args.assignment_root else assignment_mod.DEFAULT_STATE_ROOT
    value = assignment_mod.load_assignment(root, args.task_id, args.assignment_digest)
    if value is None:
        raise RefusalError(6, f"no assignment on record for task_id={args.task_id} digest={args.assignment_digest}")
    try:
        assignment_mod.validate_assignment(value, require_source_evidence=True)
    except assignment_mod.AssignmentError as exc:
        raise RefusalError(2, f"persisted assignment is invalid or tampered: {exc}") from exc
    if value.get("assignment_digest") != args.assignment_digest:
        raise RefusalError(2, "persisted assignment failed its own digest check (tampered)")

    evidence = load_run_evidence(args.run_evidence)
    if evidence.get("assignment_digest") != args.assignment_digest:
        raise RefusalError(2, "run evidence is not bound to the given assignment digest")
    if evidence.get("task_id") != args.task_id:
        raise RefusalError(2, "run evidence names a different task_id than the assignment")
    if evidence.get("base_commit") not in {None, value["source_sha"]}:
        raise RefusalError(2, "run evidence base commit does not match assigned source SHA")
    source_evidence = evidence.get("source_evidence")
    if source_evidence != value["source_evidence"]:
        raise RefusalError(2, "run evidence is missing or has mismatched source evidence")

    ledger = results_ledger(root)
    try:
        prior = find_jsonl_objects(ledger, "run_id", args.run_id)
    except JsonlDurabilityError as exc:
        raise RefusalError(2, f"results ledger is unusable: {exc}") from exc
    if prior:
        raise RefusalError(4, f"run_id {args.run_id} was already accepted (duplicate result)")

    deadline_epoch = evidence.get("deadline_epoch")
    if isinstance(deadline_epoch, int) and not isinstance(deadline_epoch, bool):
        received_epoch = _epoch_of(args.received_at) if args.received_at else now_epoch()
        if received_epoch is None:
            raise RefusalError(2, f"invalid --received-at {args.received_at!r}")
        if received_epoch > deadline_epoch:
            raise RefusalError(3, f"result received at {received_epoch} is past the run deadline {deadline_epoch}")

    if args.result_repository and args.result_repository != value["source_repository"]:
        raise RefusalError(5, "returned repository does not match the assigned source_repository")
    if args.result_branch:
        try:
            branch = assignment_mod.canonical_branch(args.result_branch, "result_branch")
        except assignment_mod.AssignmentError as exc:
            raise RefusalError(5, str(exc)) from exc
        protected = set(PROTECTED_BRANCHES)
        protected.update({value.get("default_branch"), value.get("integration_branch")})
        if branch in protected:
            raise RefusalError(5, f"returned branch {args.result_branch!r} is a protected default branch")
        if not (branch == f"loop/work/{args.task_id}" or branch.startswith("cursor/")
                or branch.startswith("recursion/extern/")):
            raise RefusalError(5, f"returned branch {args.result_branch!r} is not an authorized result ref")
    for changed in args.changed_path:
        if not path_within_allowed(changed, value["allowed_paths"]):
            raise RefusalError(5, f"returned path {changed!r} is outside the assigned allowed_paths")
    if args.result_commit:
        if not SHA_RE.fullmatch(args.result_commit):
            raise RefusalError(2, "returned result commit is not a canonical object id")
        for label, observed in (
            ("run evidence commit", evidence.get("commit_oid")),
            ("machine gate commit", (evidence.get("machine_gate") or {}).get("commit_oid")
             if isinstance(evidence.get("machine_gate"), dict) else None),
        ):
            if observed and observed != args.result_commit:
                raise RefusalError(2, f"{label} does not match returned result commit")
    elif args.record:
        raise RefusalError(2, "durable result validation requires an exact result commit")

    record = {
        "schema_version": 1, "assignment_digest": args.assignment_digest, "task_id": args.task_id,
        "run_id": args.run_id, "result_repository": args.result_repository,
        "result_branch": args.result_branch, "result_commit": args.result_commit,
        "source_sha": value["source_sha"], "source_evidence": value["source_evidence"],
        "provider": value["provider"], "capacity_pool": value.get("capacity_pool"),
        "host": value["host"], "model": value.get("model"),
        "sandbox_profile": value["sandbox_profile"],
        "verified_at": assignment_mod.now_iso(), "status": "accepted",
    }
    if args.record:
        try:
            append_jsonl(ledger, record, dedupe_field="run_id", dedupe_value=args.run_id)
        except JsonlDurabilityError as exc:
            raise RefusalError(2, f"results ledger append failed: {exc}") from exc
    return record


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROG)
    parser.add_argument("--assignment-root", default=None)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--assignment-digest", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-evidence", required=True)
    parser.add_argument("--result-repository", default=None)
    parser.add_argument("--result-branch", default=None)
    parser.add_argument("--result-commit", default=None)
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--received-at", default=None)
    parser.add_argument("--record", action="store_true")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])
    try:
        record = check(args)
    except RefusalError as exc:
        diag(exc.reason)
        print(json.dumps({"status": "refused", "code": exc.code, "reason": exc.reason}, sort_keys=True))
        return exc.code
    print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

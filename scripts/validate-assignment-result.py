#!/usr/bin/env python3
"""Bind a returned run result to its exact persisted assignment, fail closed (Phases 3 and 5).

The optional ``--assignment-file`` selects the immutable Phase 5 contract.  Without it, the
validator retains the legacy Phase 3 task-id/digest lookup.

Generalizes the existing exact-commit binding already enforced elsewhere in the pipeline
(validate-verifier-result.py's --commit/--implementer-run check; work.sh's
phase5_assert_gate_commit re-check of CANDIDATE_OID) to full assignment identity: engine,
provider, capacity pool, model, host, sandbox, and source, not just a commit hash.

Refuses, with a distinct exit code per docs/plans/recursion-v2-execution-fabric.md Phase 3's
gate ("fail closed on late, duplicate, mismatched, or unauthorized results"):

  0  accepted — the result is bound to its assignment, on time, once, and in scope
  2  mismatched — the assignment record is missing/unreadable, tampered (its own content no
     longer hashes to its filename), or the run evidence names a different assignment digest
  3  late — the supervised worker completed after its own recorded deadline; later controller
     work (commit, verification, and final admission) is not part of that interval
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
import os
import sys
import time
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assignment as assignment_mod  # noqa: E402
import assignment_contract as contract_mod  # noqa: E402
from jsonl_durable import (JsonlDurabilityError, append_jsonl, durable_lock,
                           find_jsonl_objects, read_durable_bytes)  # noqa: E402
from run_contract import RunContractError, validate_run  # noqa: E402

PROG = "validate-assignment-result"
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
NANOSECONDS = 1_000_000_000
PROTECTED_BRANCHES = frozenset({"main", "master", "recursion/integration"})
SHA_RE = assignment_mod.SHA_RE
MAX_INPUT_BYTES = 8 * 1024 * 1024


class RefusalError(Exception):
    def __init__(self, code: int, reason: str) -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def now_epoch() -> int:
    return int(time.time())


def now_epoch_ns() -> int:
    return time.time_ns()


def _epoch_of(text: object) -> int | None:
    if not isinstance(text, str) or not text:
        return None
    try:
        return calendar.timegm(time.strptime(text, TS_FORMAT))
    except (OSError, TypeError, ValueError, OverflowError, RecursionError, UnicodeError):
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
        raw = read_durable_bytes(Path(path), max_bytes=MAX_INPUT_BYTES)
        if raw is None:
            raise RefusalError(2, "run evidence is unreadable")
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite JSON number")),
        )
    except RefusalError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError,
            OverflowError, RecursionError, JsonlDurabilityError):
        raise RefusalError(2, "run evidence is unreadable") from None
    if not isinstance(value, dict):
        raise RefusalError(2, "run evidence is not a JSON object")
    return value


def load_assignment_for_result(args: argparse.Namespace, root: Path) -> tuple[dict, bool]:
    """Load exactly the authority selected by the caller.

    Phase 5 passes its immutable contract explicitly because it is not persisted in the
    legacy task-id/digest directory.  An explicit path is authoritative: absence or
    corruption is a refusal and never triggers a lookup in the legacy layout.  Calls that
    do not supply a path retain the Phase 3 assignment loader and schema.
    """
    if args.assignment_file:
        try:
            candidate = Path(args.assignment_file)
            if not candidate.exists():
                raise RefusalError(
                    6,
                    f"no authoritative assignment on record for task_id={args.task_id} digest={args.assignment_digest}",
                )
            value, computed = contract_mod.load_assignment(candidate)
        except RefusalError:
            raise
        except (contract_mod.AssignmentError, OSError, TypeError, ValueError,
                OverflowError, RecursionError, UnicodeDecodeError):
            raise RefusalError(2, "authoritative assignment is invalid or unreadable") from None
        if value.get("task_id") != args.task_id:
            raise RefusalError(2, "authoritative assignment task_id does not match the requested task")
        if computed != args.assignment_digest:
            raise RefusalError(2, "authoritative assignment failed its digest check")
        return value, True

    value = assignment_mod.load_assignment(root, args.task_id, args.assignment_digest)
    if value is None:
        raise RefusalError(6, f"no assignment on record for task_id={args.task_id} digest={args.assignment_digest}")
    try:
        assignment_mod.validate_assignment(value, require_source_evidence=True)
    except assignment_mod.AssignmentError as exc:
        raise RefusalError(2, f"persisted assignment is invalid or tampered: {exc}") from exc
    if value.get("assignment_digest") != args.assignment_digest:
        raise RefusalError(2, "persisted assignment failed its own digest check (tampered)")
    return value, False


def strict_assignment_projection(run: dict, assignment: dict, assignment_file: str) -> dict:
    """Project strict run attribution from the immutable contract and role binding."""
    role = run.get("role")
    roles = assignment.get("role_assignments")
    role_spec = roles.get(role) if isinstance(roles, dict) else None
    if role not in {"implementer", "verifier"} or not isinstance(role_spec, dict):
        raise RefusalError(2, "strict run evidence names an unassigned role")

    # These facts are intentionally supplied by work.sh at the start boundary: they are
    # absent from the Phase 5 contract, so result validation must require them rather than
    # inventing legacy defaults.  The run contract already requires the fields for a strict
    # assignment; these checks keep their meaning explicit at this terminal boundary.
    for field in ("billing_basis", "metered_approved", "default_branch", "integration_branch"):
        if field not in run or run[field] is None:
            raise RefusalError(2, f"strict run evidence is missing controller-supplied {field}")
    if not isinstance(run["billing_basis"], str) or not run["billing_basis"].strip():
        raise RefusalError(2, "strict run evidence billing_basis is invalid")
    if not isinstance(run["metered_approved"], bool):
        raise RefusalError(2, "strict run evidence metered_approved is invalid")
    try:
        default_branch = assignment_mod.canonical_branch(run["default_branch"], "default_branch")
        integration_branch = assignment_mod.canonical_branch(
            run["integration_branch"], "integration_branch"
        )
    except assignment_mod.AssignmentError as exc:
        raise RefusalError(2, f"strict run evidence branch policy is invalid: {exc}") from exc
    if default_branch == integration_branch:
        raise RefusalError(2, "strict run evidence default and integration branches must differ")
    if run["billing_basis"] == "metered" and run["metered_approved"] is not True:
        raise RefusalError(2, "strict run evidence does not approve metered usage")

    try:
        recorded_assignment_file = run.get("assignment_file")
        expected_assignment_file = os.path.normcase(os.path.abspath(str(assignment_file)))
        observed_assignment_file = os.path.normcase(os.path.abspath(recorded_assignment_file)) \
            if isinstance(recorded_assignment_file, str) else ""
    except (OSError, TypeError, ValueError):
        observed_assignment_file = ""
        expected_assignment_file = ""
    if not observed_assignment_file or observed_assignment_file != expected_assignment_file:
        raise RefusalError(2, "strict run evidence assignment_file disagrees with the authoritative contract")

    nested = run.get("assignment")
    try:
        normalized_nested = contract_mod.validate_assignment(nested)
        if contract_mod.canonical_bytes(normalized_nested) != contract_mod.canonical_bytes(assignment):
            raise RefusalError(2, "strict run assignment projection disagrees with its source file")
    except contract_mod.AssignmentError as exc:
        raise RefusalError(2, f"strict run assignment projection is invalid: {exc}") from exc

    source_evidence = {
        "repository": assignment["source_repository"],
        "branch": assignment["source_branch"],
        "sha": assignment["source_sha"],
        "verified": True,
    }
    expected = {
        "project_id": assignment["project_id"],
        "engine": role_spec["engine"],
        "provider": role_spec["provider"],
        "capacity_pool": assignment["capacity_pool"],
        "billing_basis": run["billing_basis"],
        "metered_approved": run["metered_approved"],
        "host": assignment["host"],
        "model": role_spec["model"],
        "sandbox_profile": assignment["sandbox_profile"],
        "network_policy": role_spec["network_policy"],
        "network_profile": role_spec["network_profile"],
        "source_repository": assignment["source_repository"],
        "source_branch": assignment["source_branch"],
        "source_sha": assignment["source_sha"],
        "source_evidence": source_evidence,
        "allowed_paths": assignment["allowed_paths"],
        "publication_policy": assignment["publication_policy"],
        "default_branch": default_branch,
        "integration_branch": integration_branch,
        "assignment": assignment,
    }
    for field, expected_value in expected.items():
        if field not in run or not assignment_mod.type_aware_equal(run[field], expected_value):
            raise RefusalError(2, f"strict run attribution field {field!r} disagrees with the assignment")
    return expected


def _check_locked(args: argparse.Namespace) -> dict:
    root = Path(args.assignment_root) if args.assignment_root else assignment_mod.DEFAULT_STATE_ROOT
    value, strict = load_assignment_for_result(args, root)

    evidence = load_run_evidence(args.run_evidence)
    try:
        validate_run(evidence)
    except RunContractError as exc:
        raise RefusalError(2, f"run evidence violates the runtime contract: {exc}") from exc
    if evidence.get("id") != args.run_id:
        raise RefusalError(2, "run evidence id does not match the requested run_id")
    if "run_id" in evidence and evidence.get("run_id") != args.run_id:
        raise RefusalError(2, "run evidence run_id does not match the requested run_id")
    if strict:
        attribution = strict_assignment_projection(evidence, value, args.assignment_file)
    else:
        try:
            attribution = assignment_mod.require_assignment_projection(evidence, value)
        except assignment_mod.AssignmentError as exc:
            raise RefusalError(2, f"run evidence attribution projection is invalid: {exc}") from exc
    if evidence.get("assignment_digest") != args.assignment_digest:
        raise RefusalError(2, "run evidence is not bound to the given assignment digest")
    if evidence.get("task_id") != args.task_id:
        raise RefusalError(2, "run evidence names a different task_id than the assignment")
    if evidence.get("base_commit") != value["source_sha"]:
        raise RefusalError(2, "run evidence base commit does not match assigned source SHA")
    source_evidence = evidence.get("source_evidence")
    if not assignment_mod.type_aware_equal(source_evidence, attribution["source_evidence"]):
        raise RefusalError(2, "run evidence is missing or has mismatched source evidence")

    # These fields are optional for legacy evidence, but once a producer emits one of the
    # aliases it must be internally consistent.  This prevents a forged lease/attempt/run
    # binding from being accepted merely because the assignment digest is correct.
    attempt_values = []
    for key in ("attempt", "assignment_attempt", "lease_attempt"):
        if key in evidence:
            item = evidence[key]
            if isinstance(item, bool) or not isinstance(item, int) or item < 1:
                raise RefusalError(2, f"run evidence {key} is not a positive integer")
            attempt_values.append((key, item))
    if attempt_values and len({item for _, item in attempt_values}) != 1:
        raise RefusalError(2, "run evidence attempt/lease bindings disagree")
    requested_attempt = getattr(args, "attempt", None)
    if requested_attempt is not None and (not attempt_values or attempt_values[0][1] != requested_attempt):
        raise RefusalError(2, "run evidence attempt does not match the requested lease attempt")
    if "lease_assignment_digest" in evidence and evidence.get("lease_assignment_digest") != args.assignment_digest:
        raise RefusalError(2, "run evidence lease assignment digest disagrees")
    if "assignment_run_id" in evidence and evidence.get("assignment_run_id") != args.run_id:
        raise RefusalError(2, "run evidence assignment run binding disagrees")
    if "lease_expires" in evidence:
        lease_expires = evidence.get("lease_expires")
        if not isinstance(lease_expires, str) or (lease_expires != "0" and _epoch_of(lease_expires) is None):
            raise RefusalError(2, "run evidence lease_expires is not canonical")
    if "deadline_epoch" in evidence:
        deadline_epoch = evidence.get("deadline_epoch")
        if isinstance(deadline_epoch, bool) or not isinstance(deadline_epoch, int):
            raise RefusalError(2, "run evidence deadline_epoch is not an integer")
        if "deadline" in evidence and _epoch_of(evidence.get("deadline")) != deadline_epoch:
            raise RefusalError(2, "run evidence deadline and deadline_epoch disagree")

    deadline_epoch_ns = evidence.get("deadline_epoch_ns")
    if "deadline_epoch_ns" in evidence:
        if isinstance(deadline_epoch_ns, bool) or not isinstance(deadline_epoch_ns, int) or deadline_epoch_ns < 0:
            raise RefusalError(2, "run evidence deadline_epoch_ns is not a nonnegative integer")
        if isinstance(evidence.get("deadline_epoch"), int) \
                and not isinstance(evidence.get("deadline_epoch"), bool) \
                and deadline_epoch_ns // NANOSECONDS != evidence["deadline_epoch"]:
            raise RefusalError(2, "run evidence precise deadline disagrees with deadline_epoch")

    worker_finished_epoch_ns = evidence.get("worker_finished_epoch_ns")
    if "worker_finished_epoch_ns" in evidence:
        if (isinstance(worker_finished_epoch_ns, bool)
                or not isinstance(worker_finished_epoch_ns, int)
                or worker_finished_epoch_ns < 0):
            raise RefusalError(2, "run evidence worker_finished_epoch_ns is not a nonnegative integer")

    deadline_epoch = evidence.get("deadline_epoch")
    # A strict arm records its completion before the controller performs scope/gate/commit/
    # verifier work. Validate that worker interval here; using now_epoch() would measure the
    # end-to-end controller pipeline and reject a worker that completed within its arm budget.
    if deadline_epoch_ns is not None:
        if worker_finished_epoch_ns is not None:
            # The worker's completion witness is authoritative.  An override is permitted
            # only as an additional, stricter observation; it can never make a late worker
            # appear on time.
            received_epoch_ns = worker_finished_epoch_ns
            if args.received_at:
                received_epoch = _epoch_of(args.received_at)
                if received_epoch is None:
                    raise RefusalError(2, f"invalid --received-at {args.received_at!r}")
                received_epoch_ns = max(received_epoch_ns, received_epoch * NANOSECONDS)
        elif args.received_at:
            received_epoch = _epoch_of(args.received_at)
            if received_epoch is None:
                raise RefusalError(2, f"invalid --received-at {args.received_at!r}")
            received_epoch_ns = received_epoch * NANOSECONDS
        else:
            received_epoch_ns = now_epoch_ns()

        boundary_ns = deadline_epoch_ns
        if received_epoch_ns > boundary_ns:
            raise RefusalError(
                3,
                f"worker finished at {received_epoch_ns} is past the run deadline {boundary_ns}",
            )
    elif isinstance(deadline_epoch, int) and not isinstance(deadline_epoch, bool):
        if worker_finished_epoch_ns is not None:
            # Apply the same monotonic-stricter rule to legacy whole-second deadlines.
            received_epoch = worker_finished_epoch_ns // NANOSECONDS
            if args.received_at:
                override_epoch = _epoch_of(args.received_at)
                if override_epoch is None:
                    raise RefusalError(2, f"invalid --received-at {args.received_at!r}")
                received_epoch = max(received_epoch, override_epoch)
        elif args.received_at:
            received_epoch = _epoch_of(args.received_at)
            if received_epoch is None:
                raise RefusalError(2, f"invalid --received-at {args.received_at!r}")
        else:
            received_epoch = now_epoch()
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
        protected.update({attribution.get("default_branch"), attribution.get("integration_branch")})
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
        if args.record and evidence.get("commit_oid") != args.result_commit:
            raise RefusalError(2, "run evidence commit_oid does not match returned result commit")
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
        "source_sha": value["source_sha"], "source_evidence": attribution["source_evidence"],
        "provider": attribution["provider"], "capacity_pool": attribution.get("capacity_pool"),
        "host": attribution["host"], "model": attribution.get("model"),
        "sandbox_profile": attribution["sandbox_profile"],
        "verified_at": assignment_mod.now_iso(), "status": "accepted",
    }
    ledger = results_ledger(root)
    if args.record:
        try:
            prior = find_jsonl_objects(ledger, "run_id", args.run_id)
        except JsonlDurabilityError:
            raise RefusalError(2, "results ledger is unusable") from None
        if prior:
            stable = {key: item for key, item in record.items() if key != "verified_at"}
            if any({key: item for key, item in row.items() if key != "verified_at"} == stable
                   for row in prior):
                raise RefusalError(4, f"run_id {args.run_id} was already accepted (duplicate result)")
            raise RefusalError(2, f"run_id {args.run_id} has a conflicting accepted result")
        try:
            outcome = append_jsonl(ledger, record, dedupe_field="run_id", dedupe_value=args.run_id)
        except JsonlDurabilityError:
            raise RefusalError(2, "results ledger append failed") from None
        if not outcome.appended:
            try:
                existing = find_jsonl_objects(ledger, "run_id", args.run_id)
            except JsonlDurabilityError:
                raise RefusalError(2, "results ledger changed during append") from None
            if not existing:
                raise RefusalError(2, "results ledger append lost its compare-and-swap result")
            stable = {key: item for key, item in record.items() if key != "verified_at"}
            if any({key: item for key, item in row.items() if key != "verified_at"} == stable
                   for row in existing):
                raise RefusalError(4, f"run_id {args.run_id} was already accepted (duplicate result)")
            raise RefusalError(2, f"run_id {args.run_id} has a conflicting accepted result")
    return record


def check(args: argparse.Namespace) -> dict:
    ledger = results_ledger(Path(args.assignment_root) if args.assignment_root else assignment_mod.DEFAULT_STATE_ROOT)
    try:
        with durable_lock(ledger):
            return _check_locked(args)
    except JsonlDurabilityError:
        raise RefusalError(2, "results ledger transaction lock failed") from None


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROG)
    parser.add_argument("--assignment-root", default=None)
    parser.add_argument("--assignment-file", default=None)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--assignment-digest", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-evidence", required=True)
    parser.add_argument("--result-repository", default=None)
    parser.add_argument("--result-branch", default=None)
    parser.add_argument("--result-commit", default=None)
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--received-at", default=None)
    parser.add_argument("--attempt", type=int, default=None)
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
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError, json.JSONDecodeError,
            JsonlDurabilityError):
        diag("invalid input or durable state")
        print(json.dumps({"status": "refused", "code": 2,
                          "reason": "invalid input or durable state"}, sort_keys=True))
        return 2
    print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

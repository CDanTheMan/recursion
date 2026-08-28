"""Append-only, assignment-bound remote execution evidence.

This is the shared Phase 6/7 remote evidence API.  Adapters submit typed events; they never
rewrite a run projection or choose a different session/branch/commit after the first event.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path, PurePosixPath

from jsonl_durable import JsonlDurabilityError, append_jsonl, read_jsonl_objects
import assignment

SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA = re.compile(r"^[0-9a-f]{40,64}$")


class RemoteEvidenceError(Exception):
    pass


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def events_path(run_path: Path) -> Path:
    return run_path.parent / "remote-events.jsonl"


def assignment_root_for_run(run_path: Path) -> Path:
    parent = run_path.parent
    return parent.parent / "assignments" if parent.name == "runs" else parent / "assignments"


def _path(value: str, allowed: list[str]) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "\\" in value:
        raise RemoteEvidenceError("remote path is not canonical")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise RemoteEvidenceError("remote path must be repository-relative")
    parts = PurePosixPath(value).parts
    if not parts or any(part in {".", ".."} for part in parts) or PurePosixPath(*parts).as_posix() != value:
        raise RemoteEvidenceError("remote path contains an alias or traversal")
    if not any(value == prefix or value.startswith(prefix.rstrip("/") + "/") for prefix in allowed):
        raise RemoteEvidenceError(f"remote path is outside assigned allowed_paths: {value}")
    return value


def _branch(value: str, assignment_record: dict) -> str:
    try:
        value = assignment.canonical_branch(value, "remote branch")
    except assignment.AssignmentError as exc:
        raise RemoteEvidenceError(str(exc)) from exc
    protected = {"main", "master", "recursion/integration", assignment_record.get("default_branch"),
                 assignment_record.get("integration_branch")}
    if value in protected or not (value == f"loop/work/{assignment_record['task_id']}"
                                  or value.startswith("cursor/") or value.startswith("recursion/extern/")):
        raise RemoteEvidenceError("remote branch is protected or not authorized")
    return value


def _load_events(path: Path) -> list[dict]:
    if path.parent.is_symlink() or path.is_symlink():
        raise RemoteEvidenceError("remote evidence ledger path is a symlink")
    try:
        return [row for row in read_jsonl_objects(path) if isinstance(row, dict)]
    except JsonlDurabilityError as exc:
        raise RemoteEvidenceError(f"remote evidence ledger is unusable: {exc}") from exc


def read_events_for_run(run_path: Path) -> list[dict]:
    """Read the canonical remote event stream for Phase 6/7 reconciliation."""
    return _load_events(events_path(run_path))


def append_remote_event(*, path: Path, run: dict, event_type: str, session_id: str,
                        branch: str, commit: str, artifacts: list[str], cancelled_at: str,
                        cancellation_reason: str, terminal_status: str) -> dict:
    digest = run.get("assignment_digest")
    record = run.get("assignment")
    if not isinstance(record, dict) or not digest:
        raise RemoteEvidenceError("remote evidence requires a persisted assignment binding")
    persisted = assignment.load_assignment(assignment_root_for_run(path), str(run.get("task_id") or ""), digest)
    if persisted is None:
        raise RemoteEvidenceError("remote evidence assignment record is absent")
    record = persisted
    try:
        assignment.validate_assignment(record, require_source_evidence=True)
    except assignment.AssignmentError as exc:
        raise RemoteEvidenceError(f"remote assignment is invalid: {exc}") from exc
    digest = run["assignment_digest"]
    if record.get("assignment_digest") != digest or record.get("task_id") != run.get("task_id"):
        raise RemoteEvidenceError("remote assignment digest/task mismatch")
    if event_type not in {"session", "result", "artifact", "cancel", "terminal"}:
        raise RemoteEvidenceError("unknown remote evidence event type")
    if not session_id:
        raise RemoteEvidenceError("remote evidence requires an immutable session_id")
    events = _load_events(events_path(path))
    prior = [row for row in events if row.get("run_id") == run.get("id")]
    prior_session = next((row.get("session_id") for row in prior if row.get("session_id")), None)
    if prior_session and prior_session != session_id:
        raise RemoteEvidenceError("remote session_id is immutable")
    terminal = next((row for row in prior if row.get("terminal_status")), None)
    if terminal and event_type != "terminal":
        raise RemoteEvidenceError("remote run is terminal; no further transitions are allowed")
    if event_type == "cancel" and any(row.get("event_type") == "cancel" for row in prior):
        raise RemoteEvidenceError("remote cancellation transition already recorded")
    if event_type == "terminal" and terminal:
        # Replaying the exact terminal event is idempotent; a different terminal result is not.
        if terminal.get("terminal_status") == terminal_status:
            return {"status": "duplicate", **terminal}
        raise RemoteEvidenceError("conflicting terminal transition")
    if branch:
        branch = _branch(branch, record)
    if commit and not SHA.fullmatch(commit):
        raise RemoteEvidenceError("remote commit is not a canonical object id")
    expected_commit = run.get("commit_oid") or run.get("verification_commit")
    if expected_commit and commit and commit != expected_commit:
        raise RemoteEvidenceError("remote commit disagrees with the bound run commit")
    parsed_artifacts = []
    for item in artifacts:
        name, sep, sha = item.partition("=")
        if not sep or not SHA256.fullmatch(sha):
            raise RemoteEvidenceError("artifacts must be path=sha256 entries")
        parsed_artifacts.append({"path": _path(name, record["allowed_paths"]), "sha256": sha})
    event = {
        "schema_version": 1, "event_type": event_type, "event_id": "",
        "run_id": run["id"], "task_id": run["task_id"], "assignment_digest": digest,
        "session_id": session_id, "branch": branch or None, "commit": commit or None,
        "artifacts": sorted(parsed_artifacts, key=lambda x: x["path"]),
        "cancelled_at": cancelled_at or None, "cancellation_reason": cancellation_reason or None,
        "terminal_status": terminal_status or None, "recorded_at": now(),
    }
    if event_type == "cancel" and (not cancelled_at or not cancellation_reason):
        raise RemoteEvidenceError("cancel events require cancelled_at and cancellation_reason")
    if event_type == "terminal" and not terminal_status:
        raise RemoteEvidenceError("terminal events require terminal_status")
    payload = dict(event); payload.pop("event_id")
    event["event_id"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    try:
        outcome = append_jsonl(events_path(path), event, dedupe_field="event_id", dedupe_value=event["event_id"])
    except JsonlDurabilityError as exc:
        raise RemoteEvidenceError(f"remote evidence append failed: {exc}") from exc
    return {"status": "appended" if outcome.appended else "duplicate", **event}

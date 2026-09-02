"""Append-only, assignment-bound remote execution evidence.

This is the shared Phase 6/7 remote evidence API.  Adapters submit typed events; they never
rewrite a run projection or choose a different session/branch/commit after the first event.
The append-only state machine permits an initial session/artifact stream, one immutable terminal
result, one cancel transition (after which only terminal=cancelled is allowed), or one terminal
transition; after a terminal result, only its identical replay is idempotent.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path, PurePosixPath

from jsonl_durable import (JsonlDurabilityError, append_jsonl, durable_lock,
                           ensure_no_symlink, read_jsonl_objects)
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
    try:
        ensure_no_symlink(path)
    except JsonlDurabilityError as exc:
        raise RemoteEvidenceError(str(exc)) from exc
    try:
        return [row for row in read_jsonl_objects(path) if isinstance(row, dict)]
    except JsonlDurabilityError as exc:
        raise RemoteEvidenceError(f"remote evidence ledger is unusable: {exc}") from exc


def read_events_for_run(run_path: Path) -> list[dict]:
    """Read the canonical remote event stream for Phase 6/7 reconciliation."""
    return _load_events(events_path(run_path))


def _append_remote_event_locked(*, path: Path, run: dict, event_type: str, session_id: str,
                        branch: str, commit: str, artifacts: list[str], cancelled_at: str,
                        cancellation_reason: str, terminal_status: str) -> dict:
    if not isinstance(event_type, str) or not isinstance(session_id, str) \
            or not isinstance(branch, str) or not isinstance(commit, str) \
            or not isinstance(artifacts, list) or not all(isinstance(item, str) for item in artifacts) \
            or not isinstance(cancelled_at, str) or not isinstance(cancellation_reason, str) \
            or not isinstance(terminal_status, str):
        raise RemoteEvidenceError("remote evidence arguments have invalid types")
    digest = run.get("assignment_digest")
    record = run.get("assignment")
    run_id = run.get("id")
    task_id = run.get("task_id")
    if not isinstance(record, dict) or not digest or not isinstance(run_id, str) or not run_id \
            or not isinstance(task_id, str) or not task_id:
        raise RemoteEvidenceError("remote evidence requires a persisted assignment binding")
    persisted = assignment.load_assignment(assignment_root_for_run(path), task_id, digest)
    if persisted is None:
        raise RemoteEvidenceError("remote evidence assignment record is absent")
    record = persisted
    try:
        assignment.validate_assignment(record, require_source_evidence=True)
    except assignment.AssignmentError as exc:
        raise RemoteEvidenceError(f"remote assignment is invalid: {exc}") from exc
    digest = run["assignment_digest"]
    if record.get("assignment_digest") != digest or record.get("task_id") != task_id:
        raise RemoteEvidenceError("remote assignment digest/task mismatch")
    try:
        assignment.require_assignment_projection(run, record)
    except assignment.AssignmentError as exc:
        raise RemoteEvidenceError(f"remote run attribution disagrees with persisted assignment: {exc}") from exc
    if event_type not in {"session", "result", "artifact", "cancel", "terminal"}:
        raise RemoteEvidenceError("unknown remote evidence event type")
    if not session_id:
        raise RemoteEvidenceError("remote evidence requires an immutable session_id")
    events = _load_events(events_path(path))
    prior = [row for row in events if row.get("run_id") == run_id]
    if any(row.get("task_id") != task_id or row.get("assignment_digest") != digest
           for row in prior):
        raise RemoteEvidenceError("remote evidence contains an event with the wrong assignment binding")
    prior_session = next((row.get("session_id") for row in prior if row.get("session_id")), None)
    if prior_session and prior_session != session_id:
        raise RemoteEvidenceError("remote session_id is immutable")
    terminal = next((row for row in prior if row.get("terminal_status")), None)
    result_event = next((row for row in prior if row.get("event_type") == "result"), None)
    cancellation = next((row for row in prior if row.get("event_type") == "cancel"), None)
    if terminal and event_type != "terminal":
        raise RemoteEvidenceError("remote run is terminal; no further transitions are allowed")
    if result_event and event_type != "result":
        raise RemoteEvidenceError("remote run already has a terminal result")
    if cancellation and event_type in {"session", "result", "artifact"}:
        raise RemoteEvidenceError("remote run is cancellation-terminal; no further result transitions are allowed")
    if event_type == "session" and prior and not any(row.get("event_type") == "session" for row in prior):
        raise RemoteEvidenceError("session event must be the first remote transition")
    if branch:
        branch = _branch(branch, record)
    if commit and not SHA.fullmatch(commit):
        raise RemoteEvidenceError("remote commit is not a canonical object id")
    expected_commit = run.get("commit_oid") or run.get("verification_commit")
    if expected_commit and commit and commit != expected_commit:
        raise RemoteEvidenceError("remote commit disagrees with the bound run commit")
    parsed_artifacts = []
    seen_artifacts: dict[str, str] = {}
    for item in artifacts:
        name, sep, sha = item.partition("=")
        if not sep or not SHA256.fullmatch(sha):
            raise RemoteEvidenceError("artifacts must be path=sha256 entries")
        artifact_path = _path(name, record["allowed_paths"])
        if artifact_path in seen_artifacts and seen_artifacts[artifact_path] != sha:
            raise RemoteEvidenceError("one remote artifact path has conflicting hashes")
        seen_artifacts[artifact_path] = sha
    parsed_artifacts = [{"path": name, "sha256": sha} for name, sha in seen_artifacts.items()]
    frozen_branch = next((row.get("branch") for row in prior if row.get("branch")), None)
    frozen_commit = next((row.get("commit") for row in prior if row.get("commit")), None)
    frozen_artifacts: dict[str, str] = {}
    for row in prior:
        for item in row.get("artifacts") or []:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str) \
                    or not isinstance(item.get("sha256"), str):
                raise RemoteEvidenceError("remote evidence contains a malformed artifact identity")
            old = frozen_artifacts.setdefault(item["path"], item["sha256"])
            if old != item["sha256"]:
                raise RemoteEvidenceError("remote evidence contains conflicting artifact identities")
    if frozen_branch and branch and branch != frozen_branch:
        raise RemoteEvidenceError("remote branch is immutable for the session")
    if frozen_commit and commit and commit != frozen_commit:
        raise RemoteEvidenceError("remote commit is immutable for the session")
    for item in parsed_artifacts:
        if item["path"] in frozen_artifacts and frozen_artifacts[item["path"]] != item["sha256"]:
            raise RemoteEvidenceError("remote artifact identity is immutable for the session")
    event = {
        "schema_version": 1, "event_type": event_type, "event_id": "",
        "run_id": run_id, "task_id": task_id, "assignment_digest": digest,
        "session_id": session_id, "branch": branch or None, "commit": commit or None,
        "artifacts": sorted(parsed_artifacts, key=lambda x: x["path"]),
        "cancelled_at": cancelled_at or None, "cancellation_reason": cancellation_reason or None,
        "terminal_status": terminal_status or None, "recorded_at": now(),
    }
    if event_type == "cancel" and (not cancelled_at or not cancellation_reason):
        raise RemoteEvidenceError("cancel events require cancelled_at and cancellation_reason")
    if event_type == "terminal" and not terminal_status:
        raise RemoteEvidenceError("terminal events require terminal_status")
    if terminal_status and event_type != "terminal":
        raise RemoteEvidenceError("terminal_status is only valid on a terminal event")
    if (cancelled_at or cancellation_reason) and event_type != "cancel":
        raise RemoteEvidenceError("cancellation fields are only valid on a cancel event")
    if event_type == "terminal" and cancellation and terminal_status != "cancelled":
        raise RemoteEvidenceError("a cancelled remote run can only reach terminal_status=cancelled")
    payload = dict(event); payload.pop("event_id")
    payload.pop("recorded_at")
    event["event_id"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    identical = next((row for row in prior if row.get("event_id") == event["event_id"]), None)
    if identical is not None:
        # The event id excludes wall-clock time, so exact replays are idempotent.  State checks
        # above intentionally run first: replaying a result after cancellation is still refused.
        return {"status": "duplicate", **identical}
    if event_type == "session" and any(row.get("event_type") == "session" for row in prior):
        raise RemoteEvidenceError("conflicting duplicate session event")
    if event_type == "result" and result_event:
        raise RemoteEvidenceError("conflicting terminal result")
    if event_type == "cancel" and cancellation:
        raise RemoteEvidenceError("conflicting duplicate cancellation transition")
    if event_type == "terminal" and terminal:
        raise RemoteEvidenceError("conflicting terminal transition")
    try:
        outcome = append_jsonl(events_path(path), event, dedupe_field="event_id", dedupe_value=event["event_id"])
    except JsonlDurabilityError as exc:
        raise RemoteEvidenceError(f"remote evidence append failed: {exc}") from exc
    if outcome.appended:
        return {"status": "appended", **event}
    # A second writer may have won between the read and append in an implementation that does
    # not use the sibling lock.  Never report success without observing the winner's row.
    current = next((row for row in _load_events(events_path(path))
                    if row.get("run_id") == run_id and row.get("event_id") == event["event_id"]), None)
    if current is None:
        raise RemoteEvidenceError("remote evidence append lost its compare-and-swap result")
    return {"status": "duplicate", **current}


def append_remote_event(*, path: Path, run: dict, event_type: str, session_id: str,
                        branch: str, commit: str, artifacts: list[str], cancelled_at: str,
                        cancellation_reason: str, terminal_status: str) -> dict:
    """Validate one remote transition under the same durable lock as its append."""
    event_path = events_path(path)
    try:
        with durable_lock(event_path):
            return _append_remote_event_locked(
                path=path, run=run, event_type=event_type, session_id=session_id,
                branch=branch, commit=commit, artifacts=artifacts, cancelled_at=cancelled_at,
                cancellation_reason=cancellation_reason, terminal_status=terminal_status,
            )
    except JsonlDurabilityError as exc:
        raise RemoteEvidenceError(f"remote evidence transaction lock failed: {exc}") from exc

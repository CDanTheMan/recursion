"""Explicit, read-only P2 projection of one durable foundry run per project.

This module observes construction work performed on Recursion v3.  It neither
creates product-runtime agents nor supplies a canonical Hermes registry.
"""
from __future__ import annotations

import argparse
import base64
import hmac
import json
import os
import re
import sqlite3
import stat
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

from .contracts import Refused as FoundryRefused
from .contracts import digest, encoded, strict_json
from .p2_access import (
    AccessRefused,
    AccessService,
    DEFAULT_ARTIFACT_READ,
    DEFAULT_PAGE_SIZE,
    GrantStore,
    MAX_ARTIFACT_READ,
    MAX_PAGE_SIZE,
    _parse_timestamp,
    serve,
)


MAX_PROJECTS = 100
MAX_DATABASE_BYTES = 32 * 1024 * 1024
MAX_EVIDENCE_BYTES = 32 * 1024 * 1024
MAX_EVIDENCE_FILE_BYTES = 16 * 1024 * 1024
MAX_RECORD_BYTES = 1024 * 1024
MAX_JOBS = 256
MAX_ATTEMPTS = 2048
MAX_EVENTS = 4096
SHA256 = re.compile(r"[0-9a-f]{64}")
PROJECT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")

EXPECTED_SCHEMA = {
    "meta": ("key", "value"),
    "jobs": ("id", "spec", "state", "attempts", "result_hash"),
    "attempts": ("job", "number", "state", "started", "ended", "receipt"),
    "events": ("seq", "at", "event", "detail"),
}
JOB_STATES = frozenset({
    "queued", "running", "unknown", "returned", "accepted", "rejected",
    "failed", "cancelled", "blocked",
})
ATTEMPT_STATES = frozenset({"running", "unknown", "returned", "failed", "cancelled"})
COMMON_UNAVAILABLE = frozenset({
    "canonical.adapter",
    "canonical.ledger",
    "canonical_revision",
    "canonical.hermes_authority",
    "canonical.task_state",
    "canonical.acceptance",
    "status.goal_progress",
    "status.current_sources",
    "status.route_quota",
    "status.actual_spend",
    "status.external_leases",
})


def _refuse(code, message, **detail):
    raise AccessRefused(code, message, **detail)


def _valid_sha(value):
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def _parse_json_text(value, label):
    if not isinstance(value, str) or len(value.encode("utf-8")) > MAX_RECORD_BYTES:
        _refuse("foundry_unavailable", f"{label} is missing or oversized")
    try:
        return strict_json(value.encode("utf-8"))
    except (FoundryRefused, UnicodeError, ValueError, RecursionError) as exc:
        raise AccessRefused("foundry_unavailable", f"{label} is malformed") from exc


def _path_has_symlink(path):
    path = Path(path)
    anchor = Path(path.anchor)
    current = anchor
    for part in path.parts[1:]:
        current /= part
        try:
            if current.is_symlink():
                return True
        except OSError:
            return True
    return False


def _identity(path, *, directory=False):
    try:
        information = Path(path).lstat()
    except OSError as exc:
        raise AccessRefused("foundry_unavailable", "run directory is unavailable") from exc
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    if not expected(information.st_mode) or stat.S_ISLNK(information.st_mode):
        _refuse("foundry_unavailable", "run record type is unavailable")
    return information.st_dev, information.st_ino


def _file_signature(path):
    try:
        information = Path(path).lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise AccessRefused("foundry_unavailable", "foundry records changed during observation") from exc
    if not stat.S_ISREG(information.st_mode) or stat.S_ISLNK(information.st_mode):
        _refuse("foundry_unavailable", "foundry ledger sidecar is not a regular file")
    return (information.st_dev, information.st_ino, information.st_size, information.st_mtime_ns)


def _ledger_signature(database):
    wal = Path(database).with_name(Path(database).name + "-wal")
    return _file_signature(database), _file_signature(wal)


def _stable_bytes(path, limit):
    descriptor = None
    try:
        before = Path(path).lstat()
        if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode) or before.st_size > limit:
            _refuse("foundry_unavailable", "foundry ledger file exceeds its bounded regular-file contract")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
        opened = os.fstat(descriptor)
        if ((opened.st_dev, opened.st_ino, opened.st_size) !=
                (before.st_dev, before.st_ino, before.st_size)):
            _refuse("foundry_unavailable", "foundry records changed during observation")
        chunks = []
        remaining = opened.st_size
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                _refuse("foundry_unavailable", "foundry records changed during observation")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            _refuse("foundry_unavailable", "foundry records changed during observation")
        after = Path(path).lstat()
        if ((after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) !=
                (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)):
            _refuse("foundry_unavailable", "foundry records changed during observation")
        return b"".join(chunks)
    except AccessRefused:
        raise
    except OSError as exc:
        raise AccessRefused("foundry_unavailable", "foundry records changed during observation") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


@dataclass(frozen=True)
class _Snapshot:
    project: str
    root: Path
    root_identity: tuple[int, int]
    database_identity: tuple[int, int]
    plan: dict
    plan_hash: str
    jobs: tuple[dict, ...]
    attempts: dict
    events: tuple[dict, ...]
    observed_at: str | None
    last_cursor: int | None
    cursor_supported: bool

    @property
    def run_id(self):
        return self.plan["run_id"]

    @property
    def source_commit(self):
        return self.plan["source_commit"]

    @property
    def binding(self):
        return (
            self.root_identity,
            self.database_identity,
            self.plan_hash,
            self.run_id,
            self.source_commit,
        )


class _Budget:
    def __init__(self, limit=MAX_EVIDENCE_BYTES):
        self.remaining = limit

    def charge(self, size):
        if type(size) is not int or size < 0 or size > self.remaining:
            _refuse("artifact_refused", "evidence verification exceeds aggregate read bound")
        self.remaining -= size


class FoundryObservationAdapter:
    """Read adapter over source-bound foundry ledger and attempt records."""

    def __init__(self, project_runs, *, max_page_size=MAX_PAGE_SIZE,
                 max_artifact_read=MAX_ARTIFACT_READ,
                 max_artifact_size=MAX_EVIDENCE_FILE_BYTES):
        if not isinstance(project_runs, dict) or not project_runs or len(project_runs) > MAX_PROJECTS:
            _refuse("configuration_refused", "one to 100 project run mappings are required")
        if type(max_page_size) is not int or not 1 <= max_page_size <= MAX_PAGE_SIZE:
            _refuse("configuration_refused", "page bound is invalid")
        if type(max_artifact_read) is not int or not 1 <= max_artifact_read <= MAX_ARTIFACT_READ:
            _refuse("configuration_refused", "artifact read bound is invalid")
        if type(max_artifact_size) is not int or not 1 <= max_artifact_size <= MAX_EVIDENCE_FILE_BYTES:
            _refuse("configuration_refused", "artifact size bound is invalid")
        runs = {}
        aliases = set()
        for project, value in project_runs.items():
            if not isinstance(project, str) or PROJECT.fullmatch(project) is None:
                _refuse("configuration_refused", "project identifier is invalid")
            path = Path(value)
            if not path.is_absolute():
                _refuse("configuration_refused", "foundry run paths must be absolute")
            path = Path(os.path.abspath(path))
            alias = os.path.normcase(str(path))
            if alias in aliases:
                _refuse("configuration_refused", "one run cannot be aliased across projects")
            aliases.add(alias)
            runs[project] = path
        self.project_runs = runs
        self.max_page_size = max_page_size
        self.max_artifact_read = max_artifact_read
        self.max_artifact_size = max_artifact_size
        self._bindings = {}
        self._binding_lock = threading.Lock()

    def close(self):
        return None

    def _schema(self, connection):
        try:
            names = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            }
            if names != set(EXPECTED_SCHEMA):
                _refuse("foundry_unavailable", "foundry ledger schema differs from the bound schema")
            for table, columns in EXPECTED_SCHEMA.items():
                actual = tuple(row[1] for row in connection.execute(f"PRAGMA table_info({table})"))
                if actual != columns:
                    _refuse("foundry_unavailable", "foundry ledger columns differ from the bound schema")
        except sqlite3.Error as exc:
            raise AccessRefused("foundry_unavailable", "foundry ledger is malformed or unavailable") from exc

    def _load_snapshot(self, project):
        root = self.project_runs.get(project)
        if root is None:
            _refuse("not_found", "project has no configured foundry run")
        if _path_has_symlink(root):
            _refuse("foundry_unavailable", "symlinked foundry run paths are refused")
        root_identity = _identity(root, directory=True)
        database = root / "ledger.sqlite"
        if _path_has_symlink(database):
            _refuse("foundry_unavailable", "symlinked foundry ledger is refused")
        database_identity = _identity(database)
        try:
            size = database.stat().st_size
        except OSError as exc:
            raise AccessRefused("foundry_unavailable", "foundry ledger is unavailable") from exc
        if size > MAX_DATABASE_BYTES:
            _refuse("foundry_unavailable", "foundry ledger exceeds observation bound")
        connection = None
        temporary = None
        try:
            wal = database.with_name(database.name + "-wal")
            source_signature = _ledger_signature(database)
            wal_present = source_signature[1] is not None
            database_bytes = _stable_bytes(database, MAX_DATABASE_BYTES)
            wal_bytes = _stable_bytes(wal, MAX_DATABASE_BYTES - len(database_bytes)) if wal_present else None
            if _ledger_signature(database) != source_signature:
                _refuse("foundry_unavailable", "foundry records changed during observation")
            temporary = tempfile.TemporaryDirectory(prefix="foundry-observation-snapshot-")
            copied = Path(temporary.name) / "ledger.sqlite"
            copied.write_bytes(database_bytes)
            if wal_bytes is not None:
                copied.with_name(copied.name + "-wal").write_bytes(wal_bytes)
            connection = sqlite3.connect(copied.as_uri() + "?mode=ro", uri=True, timeout=0.1)
            connection.row_factory = sqlite3.Row
            connection.execute("BEGIN")
            self._schema(connection)
            meta_rows = list(connection.execute("SELECT key,value FROM meta LIMIT 3"))
            if len(meta_rows) != 2 or {row["key"] for row in meta_rows} != {"plan", "plan_hash"}:
                _refuse("foundry_unavailable", "foundry plan metadata is incomplete")
            meta = {row["key"]: row["value"] for row in meta_rows}
            plan = _parse_json_text(meta["plan"], "foundry plan")
            if not _valid_sha(meta["plan_hash"]) or digest(encoded(plan)) != meta["plan_hash"]:
                _refuse("foundry_unavailable", "foundry plan digest differs from ledger")
            if not isinstance(plan, dict):
                _refuse("foundry_unavailable", "foundry plan is malformed")
            plan_hash = digest(encoded(plan))
            run_id = plan.get("run_id")
            source_commit = plan.get("source_commit")
            plan_jobs = plan.get("jobs")
            if not isinstance(run_id, str) or not run_id or len(run_id) > 128:
                _refuse("foundry_unavailable", "foundry run id is malformed")
            if not isinstance(source_commit, str) or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None:
                _refuse("foundry_unavailable", "foundry source commit is malformed")
            if not isinstance(plan_jobs, list) or len(plan_jobs) > MAX_JOBS:
                _refuse("foundry_unavailable", "foundry plan job inventory is malformed")

            rows = [dict(row) for row in connection.execute(
                "SELECT id,spec,state,attempts,result_hash FROM jobs ORDER BY id LIMIT ?",
                (MAX_JOBS + 1,),
            )]
            if len(rows) > MAX_JOBS or len(rows) != len(plan_jobs):
                _refuse("foundry_unavailable", "foundry job inventory differs from the admitted plan")
            admitted = {}
            for job in plan_jobs:
                if not isinstance(job, dict) or not isinstance(job.get("id"), str) or job["id"] in admitted:
                    _refuse("foundry_unavailable", "foundry plan job is malformed")
                admitted[job["id"]] = job
            for row in rows:
                spec = _parse_json_text(row["spec"], "foundry job specification")
                if row["id"] not in admitted or spec != admitted[row["id"]]:
                    _refuse("foundry_unavailable", "foundry job differs from the admitted plan")
                if row["state"] not in JOB_STATES or type(row["attempts"]) is not int or row["attempts"] < 0:
                    _refuse("foundry_unavailable", "foundry job state is malformed")
                row["spec"] = spec

            attempt_rows = [dict(row) for row in connection.execute(
                "SELECT job,number,state,started,ended,receipt FROM attempts ORDER BY job,number LIMIT ?",
                (MAX_ATTEMPTS + 1,),
            )]
            if len(attempt_rows) > MAX_ATTEMPTS:
                _refuse("foundry_unavailable", "foundry attempt inventory exceeds observation bound")
            attempts = {job_id: {} for job_id in admitted}
            for row in attempt_rows:
                if row["job"] not in attempts or type(row["number"]) is not int or row["number"] <= 0:
                    _refuse("foundry_unavailable", "foundry attempt identity is malformed")
                if row["state"] not in ATTEMPT_STATES or not isinstance(row["started"], str):
                    _refuse("foundry_unavailable", "foundry attempt state is malformed")
                if row["ended"] is not None and not isinstance(row["ended"], str):
                    _refuse("foundry_unavailable", "foundry attempt terminal time is malformed")
                receipt = None
                if row["receipt"] is not None:
                    receipt = _parse_json_text(row["receipt"], "foundry attempt receipt")
                    if not isinstance(receipt, dict):
                        _refuse("foundry_unavailable", "foundry attempt receipt is malformed")
                row["receipt"] = receipt
                attempts[row["job"]][row["number"]] = row
            for row in rows:
                numbers = sorted(attempts[row["id"]])
                if numbers != list(range(1, row["attempts"] + 1)):
                    _refuse("foundry_unavailable", "foundry attempts are not a complete admitted prefix")

            events = [dict(row) for row in connection.execute(
                "SELECT seq,at,event,detail FROM events ORDER BY seq LIMIT ?", (MAX_EVENTS + 1,)
            )]
            if len(events) > MAX_EVENTS:
                _refuse("foundry_unavailable", "foundry event inventory exceeds observation bound")
            sequences = [row["seq"] for row in events]
            cursor_supported = bool(sequences) and sequences == list(range(1, sequences[-1] + 1))
            observed_at = events[-1]["at"] if events and isinstance(events[-1]["at"], str) else None
            if observed_at is not None:
                try:
                    _parse_timestamp(observed_at)
                except ValueError:
                    observed_at = None
            snapshot = _Snapshot(
                project=project,
                root=root,
                root_identity=root_identity,
                database_identity=database_identity,
                plan=plan,
                plan_hash=plan_hash,
                jobs=tuple(rows),
                attempts=attempts,
                events=tuple(events),
                observed_at=observed_at,
                last_cursor=sequences[-1] if cursor_supported else None,
                cursor_supported=cursor_supported,
            )
        except AccessRefused:
            raise
        except (FoundryRefused, sqlite3.Error, OSError, UnicodeError, ValueError, RecursionError) as exc:
            raise AccessRefused("foundry_unavailable", "foundry ledger is malformed or unavailable") from exc
        finally:
            if connection is not None:
                connection.close()
            if temporary is not None:
                temporary.cleanup()

        if _identity(root, directory=True) != root_identity or _identity(database) != database_identity:
            _refuse("foundry_unavailable", "foundry records were replaced during observation")
        with self._binding_lock:
            prior = self._bindings.get(project)
            if prior is not None and prior != snapshot.binding:
                _refuse("foundry_unavailable", "configured run was replaced")
            self._bindings[project] = snapshot.binding
        return snapshot

    def _ensure_identity(self, snapshot):
        database = snapshot.root / "ledger.sqlite"
        if (_identity(snapshot.root, directory=True) != snapshot.root_identity or
                _identity(database) != snapshot.database_identity):
            _refuse("foundry_unavailable", "foundry records were replaced during observation")
        with self._binding_lock:
            if self._bindings.get(snapshot.project) != snapshot.binding:
                _refuse("foundry_unavailable", "configured run was replaced")

    def _meta(self, snapshot, data, unavailable=()):
        missing = set(COMMON_UNAVAILABLE) | set(unavailable)
        if snapshot.observed_at is None:
            missing.add("foundry.observed_at")
        if not snapshot.cursor_supported:
            missing.update({"last_event_cursor", "foundry.event_replay"})
        return {
            "canonical_revision": None,
            "observed_at": snapshot.observed_at,
            "last_event_cursor": snapshot.last_cursor,
            "data": data,
            "unavailable_fields": sorted(missing),
        }

    def _limit(self, params):
        limit = params.get("limit", DEFAULT_PAGE_SIZE)
        if type(limit) is not int or not 1 <= limit <= self.max_page_size:
            _refuse("malformed_request", "page limit is outside the foundry observation bound",
                    max_page_size=self.max_page_size)
        return limit

    def _current_attempt(self, snapshot, job):
        number = job["attempts"]
        return snapshot.attempts[job["id"]].get(number) if number else None

    def _decision(self, snapshot, job):
        matches = []
        malformed = False
        for event in snapshot.events:
            if event["event"] != "head-decision":
                continue
            try:
                detail = _parse_json_text(event["detail"], "foundry head decision")
            except AccessRefused:
                malformed = True
                continue
            if isinstance(detail, dict) and detail.get("job") == job["id"]:
                matches.append(detail)
        if job["state"] == "accepted":
            valid = [value for value in matches if value.get("accepted") is True and
                     isinstance(value.get("reference"), str) and value["reference"]]
            if len(valid) == 1 and not malformed:
                return {"state": "accepted", "independently_accepted": True,
                        "scope": "foundry_head_decision", "reference": valid[0]["reference"]}
            return {"state": "unavailable", "independently_accepted": False,
                    "scope": "foundry_head_decision", "reference": None}
        if job["state"] == "rejected":
            valid = [value for value in matches if value.get("accepted") is False and
                     isinstance(value.get("reference"), str) and value["reference"]]
            return {"state": "rejected" if len(valid) == 1 and not malformed else "unavailable",
                    "independently_accepted": False, "scope": "foundry_head_decision",
                    "reference": valid[0]["reference"] if len(valid) == 1 and not malformed else None}
        if job["state"] == "returned":
            state = "pending"
        else:
            state = "not_reviewable"
        return {"state": state, "independently_accepted": False,
                "scope": "foundry_head_decision", "reference": None}

    def _evidence_path(self, root, job_id, number, *parts):
        path = root / "attempts" / job_id / str(number)
        for part in parts:
            path /= part
        try:
            relative = path.relative_to(root)
        except ValueError:
            _refuse("artifact_refused", "foundry evidence path escaped its run")
        if ".." in relative.parts or _path_has_symlink(path):
            _refuse("artifact_refused", "symlinked or escaping foundry evidence is refused")
        return path

    def _read_file(self, path, budget, *, expected=None, limit=MAX_EVIDENCE_FILE_BYTES):
        descriptor = None
        try:
            before = Path(path).lstat()
            if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode):
                _refuse("artifact_refused", "foundry evidence is not a regular file",
                        reason="evidence_missing")
            if before.st_size > limit:
                _refuse("artifact_refused", "foundry evidence exceeds file read bound",
                        reason="evidence_oversized")
            budget.charge(before.st_size)
            flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(path, flags)
            opened = os.fstat(descriptor)
            if ((opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino) or
                    not stat.S_ISREG(opened.st_mode)):
                _refuse("artifact_refused", "foundry evidence was replaced during read",
                        reason="evidence_replaced")
            chunks = []
            remaining = opened.st_size
            while remaining:
                chunk = os.read(descriptor, min(64 * 1024, remaining))
                if not chunk:
                    _refuse("artifact_refused", "foundry evidence was truncated during read",
                            reason="evidence_replaced")
                chunks.append(chunk)
                remaining -= len(chunk)
            if os.read(descriptor, 1):
                _refuse("artifact_refused", "foundry evidence grew during read",
                        reason="evidence_replaced")
            after = Path(path).lstat()
            final = os.fstat(descriptor)
            if ((after.st_dev, after.st_ino, after.st_size) !=
                    (opened.st_dev, opened.st_ino, opened.st_size) or
                    final.st_size != opened.st_size):
                _refuse("artifact_refused", "foundry evidence was replaced during read",
                        reason="evidence_replaced")
            data = b"".join(chunks)
            if expected is not None and not hmac.compare_digest(digest(data), expected):
                _refuse("artifact_refused", "foundry evidence digest differs from manifest",
                        reason="digest_mismatch")
            return data
        except AccessRefused:
            raise
        except FileNotFoundError as exc:
            raise AccessRefused("artifact_refused", "foundry evidence is unavailable",
                                reason="evidence_missing") from exc
        except OSError as exc:
            raise AccessRefused("artifact_refused", "foundry evidence read was refused",
                                reason="evidence_unavailable") from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)

    def _json_file(self, path, budget, *, expected=None, limit=MAX_RECORD_BYTES):
        data = self._read_file(path, budget, expected=expected, limit=limit)
        try:
            return strict_json(data), data
        except (FoundryRefused, UnicodeError, ValueError, RecursionError) as exc:
            raise AccessRefused("artifact_refused", "foundry evidence JSON is malformed",
                                reason="evidence_malformed") from exc

    def _verify_result(self, snapshot, job, attempt, budget):
        result_hash = job["result_hash"]
        if not _valid_sha(result_hash):
            return None, "manifest_digest_missing"
        if attempt is None or attempt["state"] != "returned" or not isinstance(attempt["receipt"], dict):
            return None, "receipt_missing"
        number = attempt["number"]
        receipt = attempt["receipt"]
        try:
            receipt_path = self._evidence_path(snapshot.root, job["id"], number, "receipt.json")
            retained, _ = self._json_file(receipt_path, budget)
            if encoded(retained) != encoded(receipt):
                _refuse("artifact_refused", "attempt receipt differs from ledger",
                        reason="digest_mismatch")
            if receipt.get("job") != job["id"] or receipt.get("attempt") != number:
                _refuse("artifact_refused", "attempt receipt identity differs from ledger",
                        reason="digest_mismatch")
            if receipt.get("filing_sha256") != result_hash:
                _refuse("artifact_refused", "filing digest differs between receipt and ledger",
                        reason="digest_mismatch")
            required = ("packet_sha256", "transport_sha256", "export_sha256")
            if not all(_valid_sha(receipt.get(field)) for field in required):
                return None, "manifest_digest_missing"
            filing_path = self._evidence_path(snapshot.root, job["id"], number, "filing.json")
            self._json_file(filing_path, budget, expected=result_hash,
                            limit=self.max_artifact_size)
            for parts, field in [
                (("packet.json",), "packet_sha256"),
                (("transport.json",), "transport_sha256"),
                (("client-output", "export.json"), "export_sha256"),
            ]:
                path = self._evidence_path(snapshot.root, job["id"], number, *parts)
                self._read_file(path, budget, expected=receipt[field])
            tools = receipt.get("tool_receipts")
            if not isinstance(tools, list) or len(tools) > MAX_JOBS:
                return None, "manifest_digest_missing"
            seen = set()
            for tool in tools:
                if (not isinstance(tool, dict) or set(tool) != {"number", "sha256"} or
                        type(tool["number"]) is not int or tool["number"] <= 0 or
                        tool["number"] in seen or not _valid_sha(tool["sha256"])):
                    return None, "manifest_digest_missing"
                seen.add(tool["number"])
                tool_root = ("tools", str(tool["number"]))
                tool_receipt, _ = self._json_file(
                    self._evidence_path(snapshot.root, job["id"], number, *tool_root, "receipt.json"),
                    budget, expected=tool["sha256"],
                )
                request_hash = tool_receipt.get("request_sha256") if isinstance(tool_receipt, dict) else None
                if not _valid_sha(request_hash):
                    return None, "manifest_digest_missing"
                self._read_file(
                    self._evidence_path(snapshot.root, job["id"], number, *tool_root, "request.json"),
                    budget, expected=request_hash,
                )
            return filing_path, None
        except AccessRefused as exc:
            return None, exc.detail.get("reason", "evidence_unavailable")

    def _task_view(self, snapshot, job, budget):
        attempt = self._current_attempt(snapshot, job)
        if attempt is None:
            attempt_view = {
                "number": 0, "state": "not_started", "started": None, "ended": None,
                "held": False, "effect_state": "not_started",
            }
        else:
            effect = "unknown" if attempt["state"] == "unknown" else (
                "in_flight" if attempt["state"] == "running" else "known"
            )
            attempt_view = {
                "number": attempt["number"], "state": attempt["state"],
                "started": attempt["started"], "ended": attempt["ended"],
                "held": attempt["state"] in {"running", "unknown"},
                "effect_state": effect,
            }
        worker_returned = bool(attempt and attempt["state"] == "returned" and
                               job["state"] in {"returned", "accepted", "rejected"})
        result = {
            "worker_returned": worker_returned,
            "availability": "not_returned",
            "reason": None,
            "filing_sha256": job["result_hash"] if _valid_sha(job["result_hash"]) else None,
            "artifact_handle": None,
        }
        if attempt and attempt["state"] == "running":
            result["availability"] = "in_flight"
        elif attempt and attempt["state"] == "unknown":
            result["availability"] = "unknown"
        elif worker_returned:
            filing_path, reason = self._verify_result(snapshot, job, attempt, budget)
            if filing_path is not None:
                result["availability"] = "verified"
                result["artifact_handle"] = (
                    f"foundry:{snapshot.plan_hash}:{job['id']}:{attempt['number']}:{job['result_hash']}"
                )
            else:
                result["availability"] = "unavailable"
                result["reason"] = reason
        elif job["state"] in {"returned", "accepted", "rejected"}:
            result["availability"] = "unavailable"
            result["reason"] = "receipt_missing"
        work = job["spec"]
        return {
            "task_id": job["id"],
            "foundry_state": job["state"],
            "work": {
                "domain": work.get("domain"),
                "kind": work.get("kind"),
                "depends_on": list(work.get("depends_on", ())) if isinstance(work.get("depends_on"), list) else None,
                "source_commit": snapshot.source_commit,
            },
            "attempt": attempt_view,
            "result": result,
            "acceptance": self._decision(snapshot, job),
            "canonical_state": None,
        }

    def _status(self, snapshot):
        counts = {state: 0 for state in sorted(JOB_STATES)}
        held = []
        for job in snapshot.jobs:
            counts[job["state"]] += 1
            attempt = self._current_attempt(snapshot, job)
            if attempt and attempt["state"] in {"running", "unknown"}:
                held.append({"task_id": job["id"], "attempt": attempt["number"],
                             "state": attempt["state"], "effect_state":
                             "unknown" if attempt["state"] == "unknown" else "in_flight"})
        return {
            "project": snapshot.project,
            "observation_kind": "foundry_run",
            "run_id": snapshot.run_id,
            "plan_sha256": snapshot.plan_hash,
            "source_commit": snapshot.source_commit,
            "counts": {key: value for key, value in counts.items() if value},
            "retained_holds": len(held),
            "held_attempts": held,
            "canonical_authority": None,
        }

    def _events(self, snapshot, params):
        if not snapshot.cursor_supported:
            _refuse("replay_unsupported", "durable event history is not replayable",
                    snapshot_required=True)
        after = params.get("after_cursor")
        if type(after) is not int or after < 0:
            _refuse("malformed_request", "after_cursor is required")
        if after > snapshot.last_cursor:
            _refuse("replay_gap", "cursor is outside retained history", snapshot_required=True,
                    first_available_cursor=1, last_event_cursor=snapshot.last_cursor)
        limit = self._limit(params)
        items = []
        for event in snapshot.events:
            if event["seq"] <= after:
                continue
            try:
                detail = _parse_json_text(event["detail"], "foundry event detail")
            except AccessRefused as exc:
                raise AccessRefused("replay_unsupported", "durable event record is malformed",
                                    snapshot_required=True) from exc
            items.append({"cursor": event["seq"], "at": event["at"],
                          "kind": event["event"], "detail": detail,
                          "run_id": snapshot.run_id})
            if len(items) == limit:
                break
        return {"project": snapshot.project, "run_id": snapshot.run_id,
                "cursor_scope": "foundry.events.seq", "items": items,
                "next_cursor": items[-1]["cursor"] if items else after,
                "snapshot_required": False}

    def _artifact(self, snapshot, params):
        handle = params.get("handle")
        if not isinstance(handle, str) or not 0 < len(handle) <= 512:
            _refuse("malformed_request", "artifact handle is required")
        budget = _Budget()
        match = None
        for job in snapshot.jobs:
            attempt = self._current_attempt(snapshot, job)
            if (attempt and attempt["state"] == "returned" and _valid_sha(job["result_hash"]) and
                    handle == f"foundry:{snapshot.plan_hash}:{job['id']}:{attempt['number']}:{job['result_hash']}"):
                item = self._task_view(snapshot, job, budget)
                if item["result"]["artifact_handle"] == handle:
                    match = (job, attempt, item)
                break
        if match is None:
            _refuse("artifact_refused", "artifact handle is unavailable")
        job, attempt, item = match
        offset = params.get("offset", 0)
        limit = params.get("limit", DEFAULT_ARTIFACT_READ)
        if type(limit) is not int or not 1 <= limit <= self.max_artifact_read:
            _refuse("malformed_request", "artifact read exceeds configured bound",
                    max_artifact_read=self.max_artifact_read)
        path = self._evidence_path(snapshot.root, job["id"], attempt["number"], "filing.json")
        data = self._read_file(path, budget, expected=job["result_hash"],
                               limit=self.max_artifact_size)
        if type(offset) is not int or not 0 <= offset <= len(data):
            _refuse("malformed_request", "artifact offset is invalid")
        content = data[offset:offset + limit]
        return {
            "project": snapshot.project,
            "handle": handle,
            "offset": offset,
            "size": len(data),
            "next_offset": offset + len(content) if offset + len(content) < len(data) else None,
            "sha256": job["result_hash"],
            "encoding": "base64",
            "content": base64.b64encode(content).decode("ascii"),
            "manifest_scope": "foundry.jobs.result_hash",
        }

    def read(self, operation, project, params):
        if operation not in {"status", "tasks", "task", "events", "artifact"}:
            _refuse("mutation_refused", "operation is not available in the read-only adapter")
        if not isinstance(params, dict):
            _refuse("malformed_request", "params must be an object")
        snapshot = self._load_snapshot(project)
        try:
            if operation == "status":
                data = self._status(snapshot)
            elif operation == "tasks":
                limit = self._limit(params)
                page = params.get("page_token", 0)
                if type(page) is not int or not 0 <= page <= len(snapshot.jobs):
                    _refuse("malformed_request", "invalid page token")
                selected = snapshot.jobs[page:page + limit]
                budget = _Budget()
                items = [self._task_view(snapshot, job, budget) for job in selected]
                data = {"project": project, "run_id": snapshot.run_id, "items": items,
                        "next_page_token": page + len(items)
                        if page + len(items) < len(snapshot.jobs) else None}
            elif operation == "task":
                task_id = params.get("task_id")
                if not isinstance(task_id, str) or not 0 < len(task_id) <= 256:
                    _refuse("malformed_request", "task_id is required")
                matches = [job for job in snapshot.jobs if job["id"] == task_id]
                if len(matches) != 1:
                    _refuse("not_found", "task is not visible in this project")
                data = {"project": project, "run_id": snapshot.run_id,
                        "item": self._task_view(snapshot, matches[0], _Budget())}
            elif operation == "events":
                data = self._events(snapshot, params)
            else:
                data = self._artifact(snapshot, params)
            return self._meta(snapshot, data)
        finally:
            self._ensure_identity(snapshot)


def _project_runs(values):
    runs = {}
    for value in values:
        project, separator, path = value.partition("=")
        if not separator or not project or not path or project in runs:
            _refuse("configuration_refused", "project runs must be unique PROJECT=ABSOLUTE_PATH values")
        runs[project] = path
    return runs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("serve", help="run the foreground P2 foundry observation service")
    command.add_argument("--socket", required=True)
    command.add_argument("--source-commit", required=True)
    command.add_argument("--grants", required=True)
    command.add_argument("--project-run", action="append", required=True,
                         metavar="PROJECT=ABSOLUTE_RUN_PATH")
    command.add_argument("--instance-id")
    command.add_argument("--fence", type=int)
    command.add_argument("--stale-after", type=float, default=30.0)
    command.add_argument("--max-readers", type=int, default=4)
    command.add_argument("--max-connections", type=int, default=16)
    command.add_argument("--request-timeout", type=float, default=2.0)
    command.add_argument("--max-page-size", type=int, default=MAX_PAGE_SIZE)
    command.add_argument("--max-artifact-read", type=int, default=MAX_ARTIFACT_READ)
    command.add_argument("--max-artifact-size", type=int, default=MAX_EVIDENCE_FILE_BYTES)
    args = parser.parse_args(argv)
    try:
        grants = GrantStore.load(args.grants)
        adapter = FoundryObservationAdapter(
            _project_runs(args.project_run),
            max_page_size=args.max_page_size,
            max_artifact_read=args.max_artifact_read,
            max_artifact_size=args.max_artifact_size,
        )
        access = AccessService(
            args.source_commit,
            grants,
            adapter=adapter,
            instance_id=args.instance_id,
            fence=args.fence,
            stale_after_seconds=args.stale_after,
            max_readers=args.max_readers,
            max_connections=args.max_connections,
            request_timeout=args.request_timeout,
        )
        try:
            serve(args.socket, access)
        except KeyboardInterrupt:
            pass
        return 0
    except AccessRefused as exc:
        print(json.dumps({"status": "REFUSED", "error": {
            "code": exc.code, "message": exc.message, **exc.detail,
        }}, sort_keys=True), flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

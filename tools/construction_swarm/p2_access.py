"""Explicitly started, read-only construction-service access protocol.

The service owns no scheduler, provider, leader election, or canonical state.  It
projects a supplied canonical adapter over an authenticated Unix-domain socket.
The only adapter shipped in this slice is an intentionally named fixture adapter
for tests and demonstrations; without it canonical fields are explicitly
unavailable.
"""
from __future__ import annotations

import argparse
import base64
import copy
import datetime as dt
import hashlib
import hmac
import json
import os
import re
import signal
import socket
import socketserver
import stat
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path


PROTOCOL_VERSION = 1
READ_OPERATIONS = frozenset({"status", "tasks", "task", "events", "artifact"})
MAX_REQUEST_BYTES = 16 * 1024
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_FIXTURE_BYTES = 8 * 1024 * 1024
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
DEFAULT_ARTIFACT_READ = 64 * 1024
MAX_ARTIFACT_READ = 1024 * 1024
TOKEN_PATTERN = re.compile(r"^[!-~]{16,512}$")


class AccessRefused(RuntimeError):
    """A typed refusal safe to return to an untrusted client."""

    def __init__(self, code, message, **detail):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail


def _json_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def _strict_json(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("duplicate JSON key")
            value[key] = item
        return value

    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("non-finite JSON number")))


def _utc_now():
    return dt.datetime.now(dt.timezone.utc)


def _timestamp(value):
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parse_timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp is not a string")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be UTC")
    return parsed.astimezone(dt.timezone.utc)


def _require(condition, code, message, **detail):
    if not condition:
        raise AccessRefused(code, message, **detail)


@dataclass(frozen=True)
class AccessGrant:
    identity: str
    projects: frozenset[str]
    capabilities: frozenset[str]
    expires_at: dt.datetime | None = None

    def permits(self, project):
        now = _utc_now()
        return (
            "read" in self.capabilities
            and project in self.projects
            and (self.expires_at is None or now < self.expires_at)
        )


class GrantStore:
    """Server-side token-to-identity binding loaded once at explicit start."""

    def __init__(self, grants):
        self._grants = tuple(grants)

    @classmethod
    def load(cls, filename):
        path = Path(filename).resolve(strict=True)
        _require(path.is_file(), "configuration_refused", "grant store must be a regular file")
        raw = path.read_bytes()
        _require(len(raw) <= 1024 * 1024, "configuration_refused", "grant store exceeds size limit")
        try:
            values = _strict_json(raw)
        except (UnicodeDecodeError, ValueError, RecursionError) as exc:
            raise AccessRefused("configuration_refused", "grant store is not strict JSON") from exc
        _require(isinstance(values, list) and values, "configuration_refused", "at least one grant is required")
        grants = []
        seen = set()
        for value in values:
            _require(isinstance(value, dict), "configuration_refused", "grant entry must be an object")
            _require(set(value) <= {"token_sha256", "identity", "projects", "capabilities", "expires_at"},
                     "configuration_refused", "grant entry has unknown fields")
            digest = value.get("token_sha256")
            _require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
                     "configuration_refused", "grant token digest is invalid")
            _require(digest not in seen, "configuration_refused", "duplicate grant token digest")
            seen.add(digest)
            identity = value.get("identity")
            projects = value.get("projects")
            capabilities = value.get("capabilities")
            _require(isinstance(identity, str) and identity and len(identity) <= 128,
                     "configuration_refused", "grant identity is invalid")
            _require(isinstance(projects, list) and projects and len(projects) <= 128 and
                     all(isinstance(item, str) and item and len(item) <= 128 for item in projects),
                     "configuration_refused", "grant projects are invalid")
            _require(isinstance(capabilities, list) and capabilities and
                     all(isinstance(item, str) for item in capabilities),
                     "configuration_refused", "grant capabilities are invalid")
            _require(set(capabilities) <= {"read"}, "configuration_refused",
                     "this slice accepts only the read capability")
            expires = value.get("expires_at")
            try:
                expires_at = _parse_timestamp(expires) if expires is not None else None
            except ValueError as exc:
                raise AccessRefused("configuration_refused", "grant expiry is invalid") from exc
            grants.append((digest, AccessGrant(identity, frozenset(projects), frozenset(capabilities), expires_at)))
        return cls(grants)

    def authenticate(self, token):
        _require(isinstance(token, str) and TOKEN_PATTERN.fullmatch(token),
                 "authentication_refused", "invalid credential presentation")
        presented = hashlib.sha256(token.encode("utf-8")).hexdigest()
        matched = None
        for digest, grant in self._grants:
            if hmac.compare_digest(digest, presented):
                matched = grant
        _require(matched is not None, "authentication_refused", "credential not recognized")
        _require(matched.expires_at is None or _utc_now() < matched.expires_at,
                 "authentication_refused", "credential grant expired")
        return matched


class UnavailableCanonicalAdapter:
    """Truthful default until a real canonical Hermes adapter exists."""

    def read(self, operation, project, params):
        if operation == "status":
            data = {
                "project": project,
                "goal_progress": None,
                "current_sources": None,
                "active_leases": None,
                "counts": None,
                "blockers": None,
                "route_quota": None,
                "retained_holds": None,
                "actual_spend": None,
                "quality_indicators": None,
            }
        elif operation == "tasks":
            data = {"project": project, "items": None, "next_page_token": None}
        elif operation == "task":
            data = {"project": project, "item": None}
        elif operation == "events":
            data = {"project": project, "items": None, "next_cursor": None, "snapshot_required": True}
        else:
            raise AccessRefused("canonical_unavailable", "artifact index is unavailable")
        fields = ["canonical.adapter", "canonical.ledger", "canonical_revision", "last_event_cursor"]
        if operation == "status":
            fields.extend("status." + key for key in data if key != "project")
        else:
            fields.append(operation)
        return {
            "canonical_revision": None,
            "observed_at": None,
            "last_event_cursor": None,
            "data": data,
            "unavailable_fields": fields,
        }


class FixtureCanonicalAdapter:
    """Read-only JSON adapter for local tests; never a live Hermes integration."""

    def __init__(self, filename, artifact_roots, max_page_size=MAX_PAGE_SIZE,
                 max_artifact_read=MAX_ARTIFACT_READ, max_artifact_size=MAX_ARTIFACT_READ):
        self.filename = Path(filename)
        self.artifact_roots = {name: Path(path) for name, path in artifact_roots.items()}
        self.max_page_size = max_page_size
        self.max_artifact_read = max_artifact_read
        self.max_artifact_size = max_artifact_size
        _require(os.name == "posix", "platform_unavailable",
                 "fixture artifact adapter requires POSIX descriptor-relative access")
        self._root_descriptors = {}
        flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
        try:
            for project, root in self.artifact_roots.items():
                self._root_descriptors[project] = os.open(root, flags)
        except OSError as exc:
            self.close()
            raise AccessRefused("configuration_refused", "artifact root could not be pinned") from exc

    def close(self):
        for descriptor in self._root_descriptors.values():
            try:
                os.close(descriptor)
            except OSError:
                pass
        self._root_descriptors.clear()

    def _load(self):
        try:
            path = self.filename.resolve(strict=True)
            _require(path.is_file(), "canonical_unavailable", "fixture adapter source is not a regular file")
            raw = path.read_bytes()
        except AccessRefused:
            raise
        except OSError as exc:
            raise AccessRefused("canonical_unavailable", "fixture canonical ledger is unavailable") from exc
        _require(len(raw) <= MAX_FIXTURE_BYTES, "canonical_unavailable", "fixture adapter source is oversized")
        try:
            value = _strict_json(raw)
        except (UnicodeDecodeError, ValueError, RecursionError) as exc:
            raise AccessRefused("canonical_unavailable", "fixture adapter source is malformed") from exc
        _require(isinstance(value, dict) and isinstance(value.get("projects"), dict),
                 "canonical_unavailable", "fixture adapter source has no projects")
        return value

    def _view(self, project):
        fixture = self._load()
        project_value = fixture["projects"].get(project)
        _require(isinstance(project_value, dict), "not_found", "project has no canonical fixture")
        delay = fixture.get("test_delays", {}).get("all", 0)
        return fixture, project_value, delay

    def _meta(self, fixture, data, unavailable=()):
        revision = fixture.get("canonical_revision")
        observed_at = fixture.get("observed_at")
        cursor = fixture.get("last_event_cursor")
        fields = list(unavailable)
        if type(revision) is not int or revision < 0:
            revision = None
            fields.append("canonical_revision")
        try:
            _parse_timestamp(observed_at)
        except ValueError:
            observed_at = None
            fields.append("canonical.observed_at")
        if type(cursor) is not int or cursor < 0:
            cursor = None
            fields.append("last_event_cursor")
        return {
            "canonical_revision": revision,
            "observed_at": observed_at,
            "last_event_cursor": cursor,
            "data": data,
            "unavailable_fields": fields,
        }

    def _limit(self, params):
        limit = params.get("limit", DEFAULT_PAGE_SIZE)
        _require(type(limit) is int and 1 <= limit <= self.max_page_size,
                 "malformed_request", "page limit is outside the negotiated bound",
                 max_page_size=self.max_page_size)
        return limit

    def read(self, operation, project, params):
        fixture, project_value, general_delay = self._view(project)
        delay = fixture.get("test_delays", {}).get(operation, general_delay)
        _require(type(delay) in {int, float} and 0 <= delay <= 10,
                 "canonical_unavailable", "fixture delay is invalid")
        if delay:
            time.sleep(delay)
        if operation == "status":
            required = (
                "goal_progress", "current_sources", "active_leases", "counts", "blockers",
                "route_quota", "retained_holds", "actual_spend", "quality_indicators",
            )
            supplied = project_value.get("status")
            _require(isinstance(supplied, dict), "canonical_unavailable", "fixture status is unavailable")
            data = {"project": project}
            unavailable = []
            for field in required:
                data[field] = copy.deepcopy(supplied.get(field))
                if field not in supplied:
                    unavailable.append("status." + field)
            return self._meta(fixture, data, unavailable)
        if operation == "tasks":
            tasks = project_value.get("tasks")
            _require(isinstance(tasks, list), "canonical_unavailable", "fixture task ledger is unavailable")
            limit = self._limit(params)
            page = params.get("page_token", 0)
            _require(type(page) is int and 0 <= page <= len(tasks),
                     "malformed_request", "invalid page token")
            items = copy.deepcopy(tasks[page:page + limit])
            return self._meta(fixture, {
                "project": project,
                "items": items,
                "next_page_token": page + len(items) if page + len(items) < len(tasks) else None,
            })
        if operation == "task":
            task_id = params.get("task_id")
            _require(isinstance(task_id, str) and 0 < len(task_id) <= 256,
                     "malformed_request", "task_id is required")
            tasks = project_value.get("tasks")
            _require(isinstance(tasks, list), "canonical_unavailable", "fixture task ledger is unavailable")
            matches = [item for item in tasks if isinstance(item, dict) and item.get("task_id") == task_id]
            _require(len(matches) == 1, "not_found", "task is not visible in this project")
            return self._meta(fixture, {"project": project, "item": copy.deepcopy(matches[0])})
        if operation == "events":
            events = project_value.get("events")
            _require(isinstance(events, list) and all(isinstance(item, dict) for item in events),
                     "canonical_unavailable", "fixture event ledger is unavailable")
            cursors = [item.get("cursor") for item in events]
            _require(all(type(cursor) is int and cursor >= 0 for cursor in cursors) and cursors == sorted(set(cursors)),
                     "canonical_unavailable", "fixture event cursors are invalid")
            latest = fixture.get("last_event_cursor")
            _require(type(latest) is int and latest >= 0,
                     "canonical_unavailable", "fixture last event cursor is unavailable")
            history_start = project_value.get("event_history_start")
            _require(type(history_start) is int and 0 <= history_start <= latest + 1,
                     "canonical_unavailable", "fixture event history watermark is unavailable")
            _require((not cursors and history_start == latest + 1) or
                     (cursors and history_start == cursors[0] and cursors[-1] <= latest),
                     "canonical_unavailable", "fixture event history watermark is inconsistent")
            after = params.get("after_cursor")
            _require(type(after) is int and after >= 0, "malformed_request", "after_cursor is required")
            limit = self._limit(params)
            if after < history_start - 1 or after > latest:
                raise AccessRefused(
                    "replay_gap", "event cursor is outside retained history",
                    snapshot_required=True, first_available_cursor=history_start,
                    last_event_cursor=latest,
                )
            items = [copy.deepcopy(item) for item in events if item["cursor"] > after][:limit]
            next_cursor = items[-1]["cursor"] if items else after
            return self._meta(fixture, {
                "project": project,
                "items": items,
                "next_cursor": next_cursor,
                "snapshot_required": False,
            })
        if operation == "artifact":
            return self._artifact(fixture, project, project_value, params)
        raise AccessRefused("mutation_refused", "operation is not available in the read-only slice")

    def _artifact(self, fixture, project, project_value, params):
        handle = params.get("handle")
        _require(isinstance(handle, str) and 0 < len(handle) <= 256,
                 "malformed_request", "artifact handle is required")
        records = project_value.get("artifacts")
        _require(isinstance(records, list), "canonical_unavailable", "fixture artifact index is unavailable")
        matches = [item for item in records if isinstance(item, dict) and item.get("handle") == handle]
        _require(len(matches) == 1, "not_found", "artifact handle is not visible in this project")
        record = matches[0]
        _require(record.get("project") == project, "permission_denied", "cross-project artifact handle refused")
        relative = record.get("path")
        _require(isinstance(relative, str) and relative and len(relative) <= 1024,
                 "artifact_refused", "artifact path is invalid")
        relative_path = Path(relative)
        _require(not relative_path.is_absolute() and ".." not in relative_path.parts,
                 "artifact_refused", "artifact path escape refused")
        _require(relative_path.parts, "artifact_refused", "artifact path is invalid")
        expected_digest = record.get("sha256")
        _require(isinstance(expected_digest, str) and re.fullmatch(r"[0-9a-f]{64}", expected_digest),
                 "artifact_refused", "artifact manifest digest is missing or invalid")
        root_descriptor = self._root_descriptors.get(project)
        _require(root_descriptor is not None, "canonical_unavailable", "project artifact root is unavailable")
        offset = params.get("offset", 0)
        limit = params.get("limit", DEFAULT_ARTIFACT_READ)
        _require(type(limit) is int and 1 <= limit <= self.max_artifact_read,
                 "malformed_request", "artifact read exceeds configured bound",
                 max_artifact_read=self.max_artifact_read)
        directory_descriptor = os.dup(root_descriptor)
        file_descriptor = None
        try:
            directory_flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
            for part in relative_path.parts[:-1]:
                next_descriptor = os.open(part, directory_flags, dir_fd=directory_descriptor)
                os.close(directory_descriptor)
                directory_descriptor = next_descriptor
            file_descriptor = os.open(
                relative_path.parts[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=directory_descriptor,
            )
            information = os.fstat(file_descriptor)
            _require(stat.S_ISREG(information.st_mode), "artifact_refused", "artifact is not a regular file")
            size = information.st_size
            _require(size <= self.max_artifact_size, "artifact_refused", "artifact exceeds configured size bound",
                     size=size, max_artifact_size=self.max_artifact_size)
            _require(type(offset) is int and 0 <= offset <= size,
                     "malformed_request", "artifact offset is invalid")
            with os.fdopen(file_descriptor, "rb", closefd=True) as stream:
                file_descriptor = None
                captured = bytearray()
                remaining = size
                while remaining:
                    chunk = stream.read(min(64 * 1024, remaining))
                    _require(chunk, "artifact_refused", "artifact changed during bounded read")
                    captured.extend(chunk)
                    remaining -= len(chunk)
                _require(not stream.read(1) and os.fstat(stream.fileno()).st_size == size,
                         "artifact_refused", "artifact size changed during bounded read")
                captured = bytes(captured)
                actual_digest = hashlib.sha256(captured).hexdigest()
                _require(hmac.compare_digest(actual_digest, expected_digest),
                         "artifact_refused", "artifact content digest differs from manifest")
                content = captured[offset:offset + limit]
        except AccessRefused:
            raise
        except FileNotFoundError as exc:
            raise AccessRefused("not_found", "artifact is unavailable") from exc
        except OSError as exc:
            raise AccessRefused("artifact_refused", "descriptor-relative artifact access refused") from exc
        finally:
            os.close(directory_descriptor)
            if file_descriptor is not None:
                os.close(file_descriptor)
        data = {
            "project": project,
            "handle": handle,
            "offset": offset,
            "size": size,
            "next_offset": offset + len(content) if offset + len(content) < size else None,
            "sha256": actual_digest,
            "encoding": "base64",
            "content": base64.b64encode(content).decode("ascii"),
        }
        return self._meta(fixture, data)


class AccessService:
    def __init__(self, source_commit, grants, adapter=None, instance_id=None, fence=None,
                 stale_after_seconds=30.0, max_readers=4, max_connections=16,
                 request_timeout=2.0):
        _require(isinstance(source_commit, str) and re.fullmatch(r"[0-9a-f]{40}", source_commit),
                 "configuration_refused", "source commit must be a full Git SHA-1")
        _require(instance_id is None or (isinstance(instance_id, str) and 0 < len(instance_id) <= 128),
                 "configuration_refused", "service instance is invalid")
        _require(fence is None or (type(fence) is int and fence >= 0),
                 "configuration_refused", "service fence is invalid")
        _require(type(stale_after_seconds) in {int, float} and stale_after_seconds > 0,
                 "configuration_refused", "freshness bound is invalid")
        _require(type(max_readers) is int and 1 <= max_readers <= 64,
                 "configuration_refused", "read concurrency bound is invalid")
        _require(type(max_connections) is int and max_readers + 2 <= max_connections <= 128,
                 "configuration_refused", "connection bound must reserve status capacity")
        _require(type(request_timeout) in {int, float} and 0.1 <= request_timeout <= 30,
                 "configuration_refused", "request timeout is invalid")
        self.source_commit = source_commit
        self.grants = grants
        self.adapter = adapter or UnavailableCanonicalAdapter()
        self.instance_id = instance_id or "p2-" + uuid.uuid4().hex
        self.fence = fence
        self.started_at = _timestamp(_utc_now())
        self.stale_after_seconds = float(stale_after_seconds)
        self.read_slots = threading.BoundedSemaphore(max_readers)
        self.status_slots = threading.BoundedSemaphore(2)
        self.max_connections = max_connections
        self.request_timeout = float(request_timeout)

    def envelope(self, request_id, *, ok, view=None, error=None, caller_identity=None):
        now = _utc_now()
        view = view or {}
        observed_at = view.get("observed_at")
        unavailable = set(view.get("unavailable_fields", ()))
        if observed_at is None:
            unavailable.add("canonical.observed_at")
            freshness = {"state": "unavailable", "stale": True, "age_seconds": None,
                         "stale_after_seconds": self.stale_after_seconds}
        else:
            try:
                age = max(0.0, (now - _parse_timestamp(observed_at)).total_seconds())
                stale = age > self.stale_after_seconds
                freshness = {"state": "stale" if stale else "fresh", "stale": stale,
                             "age_seconds": round(age, 3), "stale_after_seconds": self.stale_after_seconds}
            except ValueError:
                freshness = {"state": "unavailable", "stale": True, "age_seconds": None,
                             "stale_after_seconds": self.stale_after_seconds}
                unavailable.add("canonical.observed_at")
        if self.fence is None:
            unavailable.add("service_fence")
        if caller_identity is None:
            unavailable.add("caller_identity")
        if view.get("canonical_revision") is None:
            unavailable.add("canonical_revision")
        if view.get("last_event_cursor") is None:
            unavailable.add("last_event_cursor")
        result = {
            "protocol_version": PROTOCOL_VERSION,
            "request_id": request_id,
            "ok": bool(ok),
            "caller_identity": caller_identity,
            "source_commit": self.source_commit,
            "service_instance": self.instance_id,
            "service_fence": self.fence,
            "service_started_at": self.started_at,
            "observation_time": _timestamp(now),
            "canonical_observed_at": observed_at,
            "canonical_revision": view.get("canonical_revision"),
            "freshness": freshness,
            "last_event_cursor": view.get("last_event_cursor"),
            "unavailable_fields": sorted(unavailable),
        }
        if ok:
            result["data"] = view.get("data")
        else:
            result["error"] = error or {"code": "internal_error", "message": "request failed"}
        return result

    def authenticate(self, request):
        _require(isinstance(request, dict), "malformed_request", "authentication frame must be an object")
        _require(set(request) == {"protocol_version", "op", "token", "request_id"},
                 "malformed_request", "authentication frame fields are invalid")
        _require(request.get("protocol_version") == PROTOCOL_VERSION,
                 "unsupported_protocol", "unsupported protocol version")
        _require(request.get("op") == "authenticate", "authentication_refused", "authenticate first")
        _require(isinstance(request.get("request_id"), str) and 0 < len(request["request_id"]) <= 128,
                 "malformed_request", "request_id is invalid")
        return self.grants.authenticate(request.get("token"))

    def dispatch(self, grant, request):
        _require(isinstance(request, dict), "malformed_request", "request frame must be an object")
        _require(set(request) == {"protocol_version", "op", "request_id", "params"},
                 "malformed_request", "request frame fields are invalid")
        _require(request.get("protocol_version") == PROTOCOL_VERSION,
                 "unsupported_protocol", "unsupported protocol version")
        request_id = request.get("request_id")
        _require(isinstance(request_id, str) and 0 < len(request_id) <= 128,
                 "malformed_request", "request_id is invalid")
        operation = request.get("op")
        _require(operation in READ_OPERATIONS, "mutation_refused",
                 "operation is not exposed by the read-only service")
        params = request.get("params")
        _require(isinstance(params, dict), "malformed_request", "params must be an object")
        _require("actor" not in params and "identity" not in params,
                 "permission_denied", "body-supplied actor identity is refused")
        project = params.get("project")
        _require(isinstance(project, str) and 0 < len(project) <= 128,
                 "malformed_request", "project is required")
        _require(grant.permits(project), "permission_denied",
                 "transport-bound read grant does not permit this project")
        clean_params = dict(params)
        clean_params.pop("project", None)
        allowed_params = {
            "status": set(),
            "tasks": {"limit", "page_token"},
            "task": {"task_id"},
            "events": {"after_cursor", "limit"},
            "artifact": {"handle", "offset", "limit"},
        }
        _require(set(clean_params) <= allowed_params[operation], "malformed_request",
                 "operation parameters contain unknown fields")
        if operation == "status":
            acquired = self.status_slots.acquire(timeout=0.1)
            _require(acquired, "status_queue_saturated", "bounded status queue is saturated")
            try:
                try:
                    return self.adapter.read(operation, project, clean_params)
                except AccessRefused:
                    raise
                except (OSError, UnicodeError, ValueError, RecursionError) as exc:
                    raise AccessRefused("canonical_unavailable", "canonical adapter read failed") from exc
            finally:
                self.status_slots.release()
        acquired = self.read_slots.acquire(timeout=0.1)
        _require(acquired, "read_queue_saturated", "bounded read queue is saturated")
        try:
            try:
                return self.adapter.read(operation, project, clean_params)
            except AccessRefused:
                raise
            except (OSError, UnicodeError, ValueError, RecursionError) as exc:
                raise AccessRefused("canonical_unavailable", "canonical adapter read failed") from exc
        finally:
            self.read_slots.release()


def _decode_line(stream, *, limit=MAX_REQUEST_BYTES):
    line = stream.readline(limit + 2)
    _require(line, "connection_closed", "connection closed")
    _require(len(line) <= limit + 1 and line.endswith(b"\n"),
             "request_too_large", "request exceeds byte bound", max_request_bytes=limit)
    try:
        value = _strict_json(line)
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise AccessRefused("malformed_request", "request is not strict JSON") from exc
    return value


def _send(stream, value):
    encoded = _json_bytes(value) + b"\n"
    if len(encoded) > MAX_RESPONSE_BYTES:
        raise AccessRefused("response_too_large", "response exceeds service byte bound")
    stream.write(encoded)
    stream.flush()


class _SocketFrames:
    """Bounded newline frames with a total, not inactivity, deadline."""

    def __init__(self, channel, timeout):
        self.channel = channel
        self.timeout = timeout
        self.buffer = bytearray()

    def read(self):
        deadline = time.monotonic() + self.timeout
        while b"\n" not in self.buffer:
            _require(len(self.buffer) <= MAX_REQUEST_BYTES,
                     "request_too_large", "request exceeds byte bound",
                     max_request_bytes=MAX_REQUEST_BYTES)
            remaining = deadline - time.monotonic()
            _require(remaining > 0, "request_timeout", "request frame deadline exceeded")
            self.channel.settimeout(remaining)
            try:
                chunk = self.channel.recv(min(4096, MAX_REQUEST_BYTES + 2 - len(self.buffer)))
            except TimeoutError as exc:
                raise AccessRefused("request_timeout", "request frame deadline exceeded") from exc
            _require(chunk, "connection_closed", "connection closed")
            self.buffer.extend(chunk)
        line, _, retained = self.buffer.partition(b"\n")
        self.buffer = bytearray(retained)
        _require(len(line) <= MAX_REQUEST_BYTES,
                 "request_too_large", "request exceeds byte bound",
                 max_request_bytes=MAX_REQUEST_BYTES)
        try:
            return _strict_json(bytes(line))
        except (UnicodeDecodeError, ValueError, RecursionError) as exc:
            raise AccessRefused("malformed_request", "request is not strict JSON") from exc


def _send_socket(channel, value):
    encoded = _json_bytes(value) + b"\n"
    _require(len(encoded) <= MAX_RESPONSE_BYTES,
             "response_too_large", "response exceeds service byte bound")
    channel.sendall(encoded)


class _AccessHandler(socketserver.StreamRequestHandler):
    def setup(self):
        self.request.settimeout(self.server.access.request_timeout)
        super().setup()

    def handle(self):
        request_id = None
        grant = None
        frames = _SocketFrames(self.request, self.server.access.request_timeout)
        try:
            auth = frames.read()
            request_id = auth.get("request_id") if isinstance(auth, dict) else None
            grant = self.server.access.authenticate(auth)
            _send_socket(self.request, self.server.access.envelope(
                request_id, ok=True,
                view={"data": {"authenticated": True, "identity": grant.identity},
                      "unavailable_fields": ["canonical.adapter", "canonical.ledger",
                                             "canonical_revision", "last_event_cursor"]},
                caller_identity=grant.identity,
            ))
            request = frames.read()
            request_id = request.get("request_id") if isinstance(request, dict) else None
            view = self.server.access.dispatch(grant, request)
            _send_socket(self.request, self.server.access.envelope(
                request_id, ok=True, view=view, caller_identity=grant.identity,
            ))
        except AccessRefused as exc:
            error = {"code": exc.code, "message": exc.message, **exc.detail}
            error_view = {}
            if type(exc.detail.get("last_event_cursor")) is int:
                error_view["last_event_cursor"] = exc.detail["last_event_cursor"]
            try:
                _send_socket(self.request, self.server.access.envelope(
                    request_id, ok=False, error=error, view=error_view,
                    caller_identity=grant.identity if grant else None,
                ))
            except (AccessRefused, BrokenPipeError, ConnectionError, OSError):
                pass
        except (BrokenPipeError, ConnectionError, OSError):
            pass
        except Exception:  # The wire must not disclose internals.
            try:
                _send_socket(self.request, self.server.access.envelope(
                    request_id, ok=False,
                    error={"code": "internal_error", "message": "service request failed"},
                ))
            except (AccessRefused, BrokenPipeError, ConnectionError, OSError):
                pass


if hasattr(socketserver, "UnixStreamServer"):
    class ThreadingUnixAccessServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
        daemon_threads = True
        block_on_close = True
        request_queue_size = 16

        def __init__(self, socket_path, access):
            self.access = access
            self._connection_slots = threading.BoundedSemaphore(access.max_connections)
            super().__init__(str(socket_path), _AccessHandler)

        def process_request(self, request, client_address):
            if not self._connection_slots.acquire(blocking=False):
                self.shutdown_request(request)
                return
            try:
                super().process_request(request, client_address)
            except BaseException:
                self._connection_slots.release()
                raise

        def process_request_thread(self, request, client_address):
            try:
                super().process_request_thread(request, client_address)
            finally:
                self._connection_slots.release()
else:
    class ThreadingUnixAccessServer:  # pragma: no cover - importable Windows refusal path
        def __init__(self, *_args, **_kwargs):
            raise AccessRefused(
                "platform_unavailable",
                "Unix-domain sockets are required; use the WSL service path on Windows",
            )


def serve(socket_path, access):
    _require(hasattr(socket, "AF_UNIX") and hasattr(socketserver, "UnixStreamServer"),
             "platform_unavailable", "Unix-domain sockets are required; use the WSL service path on Windows")
    path = Path(socket_path)
    _require(not path.exists(), "configuration_refused", "socket path already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    server = ThreadingUnixAccessServer(path, access)
    try:
        os.chmod(path, 0o600)
        print(json.dumps({
            "status": "READY",
            "socket": str(path),
            "protocol_version": PROTOCOL_VERSION,
            "source_commit": access.source_commit,
            "service_instance": access.instance_id,
        }, sort_keys=True), flush=True)
        server.serve_forever(poll_interval=0.05)
    finally:
        server.shutdown()
        server.server_close()
        close = getattr(access.adapter, "close", None)
        if close:
            close()
        try:
            path.unlink()
        except FileNotFoundError:
            pass


class AccessClient:
    """Connecting client; it never owns or starts the service."""

    def __init__(self, socket_path, token, timeout=2.0, cache_path=None):
        _require(hasattr(socket, "AF_UNIX"), "platform_unavailable",
                 "Unix-domain sockets are required; invoke this client through WSL on Windows")
        _require(isinstance(token, str) and TOKEN_PATTERN.fullmatch(token),
                 "authentication_refused", "invalid client credential")
        self.socket_path = str(socket_path)
        self.token = token
        self.credential_digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self.timeout = float(timeout)
        self.cache_path = Path(cache_path) if cache_path else None
        self._cache = self._load_cache()

    def _load_cache(self):
        if not self.cache_path or not self.cache_path.exists():
            return {}
        try:
            raw = self.cache_path.read_bytes()
            if len(raw) > MAX_RESPONSE_BYTES:
                return {}
            value = _strict_json(raw)
            if not isinstance(value, dict) or set(value) != {"cache_version", "entries"} or \
                    value["cache_version"] != 1 or not isinstance(value["entries"], dict):
                return {}
            return value["entries"]
        except (OSError, UnicodeDecodeError, ValueError, RecursionError):
            return {}

    def _save_cache(self):
        if not self.cache_path:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        encoded = _json_bytes({"cache_version": 1, "entries": self._cache})
        _require(len(encoded) <= MAX_RESPONSE_BYTES, "cache_refused", "client cache exceeds byte bound")
        temporary = self.cache_path.with_name(self.cache_path.name + ".tmp-" + uuid.uuid4().hex)
        temporary.write_bytes(encoded)
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        os.replace(temporary, self.cache_path)

    def _cache_key(self, operation, params):
        return hashlib.sha256(_json_bytes({
            "credential_sha256": self.credential_digest,
            "service_endpoint": os.path.abspath(self.socket_path),
            "op": operation,
            "params": params,
        })).hexdigest()

    def _cache_binding(self, project):
        return {
            "credential_sha256": self.credential_digest,
            "service_endpoint": os.path.abspath(self.socket_path),
            "project": project,
        }

    def _invalidate_cache(self, project=None):
        expected = self._cache_binding(project)
        removed = False
        for key, entry in list(self._cache.items()):
            binding = entry.get("binding") if isinstance(entry, dict) else None
            if not isinstance(binding, dict):
                del self._cache[key]
                removed = True
                continue
            same_scope = (
                binding.get("credential_sha256") == expected["credential_sha256"]
                and binding.get("service_endpoint") == expected["service_endpoint"]
                and (project is None or binding.get("project") == project)
            )
            if same_scope:
                del self._cache[key]
                removed = True
        if removed:
            self._save_cache()

    @staticmethod
    def _receive(stream):
        line = stream.readline(MAX_RESPONSE_BYTES + 2)
        if not line or len(line) > MAX_RESPONSE_BYTES + 1 or not line.endswith(b"\n"):
            raise ConnectionError("invalid or missing service response")
        value = _strict_json(line)
        if not isinstance(value, dict):
            raise ConnectionError("service response is not an object")
        return value

    def request(self, operation, params, *, allow_stale=False):
        _require(operation in READ_OPERATIONS, "mutation_refused",
                 "client exposes only read operations")
        _require(isinstance(params, dict), "malformed_request", "params must be an object")
        project = params.get("project")
        key = self._cache_key(operation, params)
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
                channel.settimeout(self.timeout)
                channel.connect(self.socket_path)
                stream = channel.makefile("rwb", buffering=0)
                auth_id = uuid.uuid4().hex
                _send(stream, {"protocol_version": PROTOCOL_VERSION, "op": "authenticate",
                               "token": self.token, "request_id": auth_id})
                auth = self._receive(stream)
                if not auth.get("ok"):
                    self._invalidate_cache()
                    return auth
                request_id = uuid.uuid4().hex
                _send(stream, {"protocol_version": PROTOCOL_VERSION, "op": operation,
                               "request_id": request_id, "params": params})
                response = self._receive(stream)
            if response.get("ok"):
                self._cache[key] = {
                    "binding": self._cache_binding(project),
                    "response": response,
                }
                self._save_cache()
            elif response.get("error", {}).get("code") in {"authentication_refused", "permission_denied"}:
                self._invalidate_cache(project)
            return response
        except (ConnectionError, OSError, TimeoutError, ValueError, RecursionError) as exc:
            if allow_stale and key in self._cache:
                entry = self._cache[key]
                if not isinstance(entry, dict) or entry.get("binding") != self._cache_binding(project) or \
                        not isinstance(entry.get("response"), dict):
                    raise AccessRefused("service_unavailable", "construction access service is unavailable") from exc
                stale = copy.deepcopy(entry["response"])
                stale["freshness"] = {
                    "state": "stale_disconnected",
                    "stale": True,
                    "age_seconds": None,
                    "stale_after_seconds": stale.get("freshness", {}).get("stale_after_seconds"),
                    "disconnected_at": _timestamp(_utc_now()),
                }
                stale["unavailable_fields"] = sorted(set(stale.get("unavailable_fields", ())) | {"service.connection"})
                stale["stale_reason"] = type(exc).__name__
                return stale
            raise AccessRefused("service_unavailable", "construction access service is unavailable") from exc


def _artifact_roots(values):
    roots = {}
    for value in values:
        name, separator, path = value.partition("=")
        _require(separator and name and path and name not in roots, "configuration_refused",
                 "artifact roots must be unique PROJECT=PATH values")
        roots[name] = path
    return roots


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    command = subparsers.add_parser("serve", help="run the foreground read-only Unix-socket service")
    command.add_argument("--socket", required=True)
    command.add_argument("--source-commit", required=True)
    command.add_argument("--grants", required=True)
    command.add_argument("--instance-id")
    command.add_argument("--fence", type=int)
    command.add_argument("--stale-after", type=float, default=30.0)
    command.add_argument("--max-readers", type=int, default=4)
    command.add_argument("--max-connections", type=int, default=16)
    command.add_argument("--request-timeout", type=float, default=2.0)
    command.add_argument("--max-page-size", type=int, default=MAX_PAGE_SIZE)
    command.add_argument("--max-artifact-read", type=int, default=MAX_ARTIFACT_READ)
    command.add_argument("--max-artifact-size", type=int, default=MAX_ARTIFACT_READ)
    command.add_argument("--fixture-canonical", help="TEST ONLY: read canonical projections from fixture JSON")
    command.add_argument("--artifact-root", action="append", default=[], metavar="PROJECT=PATH")
    args = parser.parse_args(argv)
    try:
        grants = GrantStore.load(args.grants)
        roots = _artifact_roots(args.artifact_root)
        adapter = None
        if args.fixture_canonical:
            adapter = FixtureCanonicalAdapter(
                args.fixture_canonical,
                roots,
                max_page_size=args.max_page_size,
                max_artifact_read=args.max_artifact_read,
                max_artifact_size=args.max_artifact_size,
            )
        else:
            _require(not roots, "configuration_refused", "artifact roots require the fixture adapter in this slice")
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
        def stop_handler(_number, _frame):
            raise KeyboardInterrupt

        signal.signal(signal.SIGTERM, stop_handler)
        try:
            serve(args.socket, access)
        except KeyboardInterrupt:
            pass
        return 0
    except AccessRefused as exc:
        print(json.dumps({"status": "REFUSED", "error": {"code": exc.code, "message": exc.message, **exc.detail}},
                         sort_keys=True), flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

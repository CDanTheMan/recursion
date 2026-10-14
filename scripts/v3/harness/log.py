"""Structured JSONL logs. Events name the provider and the outcome, not secrets."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.redact import redact


_LEVELS = {"info": 10, "warning": 20, "error": 30}
_ERROR_EVENTS = {
    "provider.failed",
    "run.refused",
    "task.conflict",
    "task.failed",
    "task.review_rejected",
}
_WARNING_EVENTS = {"plan.fallback", "task.cancelled", "task.unreviewed"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def event_level(name: str) -> str:
    """Map an event name to info, warning, or error."""

    if name in _ERROR_EVENTS or name.endswith(".failed") or name.endswith(".refused"):
        return "error"
    if name in _WARNING_EVENTS or "budget" in name:
        return "warning"
    return "info"


class JsonLog:
    """Append one JSON object per event.

    When ``state_dir`` is set, ``bind(run_id=...)`` also appends the events to
    ``<state_dir>/<run-id>.jsonl``. Events emitted before ``bind`` are kept and
    written into that file with the run id filled in.
    """

    def __init__(self, streams: list, state_dir: Path | None = None) -> None:
        self.streams = streams
        self.state_dir = None if state_dir is None else Path(state_dir)
        self._lock = threading.Lock()
        self._buffer: list[dict] = []
        self._run_id: str | None = None
        self._state_handle = None

    def bind(self, **fields: object) -> None:
        run_id = fields.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            return
        with self._lock:
            self._run_id = run_id
            self._open_state_locked()
            pending = self._buffer
            self._buffer = []
        for record in pending:
            record.setdefault("run_id", run_id)
            self._emit_state(record)

    def event(self, name: str, **fields: object) -> None:
        payload = dict(fields)
        payload.setdefault("level", event_level(name))
        record = redact({"event": name, "ts": utc_now(), **payload})
        if not isinstance(record, dict):
            return
        with self._lock:
            if self._run_id and "run_id" not in record:
                record["run_id"] = self._run_id
            if self.state_dir is not None and self._run_id is None:
                self._buffer.append(dict(record))
            _write_jsonl(self.streams, record)

    def close(self) -> None:
        with self._lock:
            handle = self._state_handle
            self._state_handle = None
            self._buffer = []
        if handle is not None:
            handle.close()

    def _open_state_locked(self) -> None:
        if self.state_dir is None or self._state_handle is not None or self._run_id is None:
            return
        self.state_dir.mkdir(parents=True, exist_ok=True)
        handle = open(self.state_dir / f"{self._run_id}.jsonl", "a", encoding="utf-8")
        self._state_handle = handle
        self.streams.append(handle)

    def _emit_state(self, record: dict) -> None:
        with self._lock:
            handle = self._state_handle
        if handle is not None:
            _write_jsonl([handle], record)


class BoundLog:
    """Add the same fields to every event. Explicit fields on the event win."""

    def __init__(self, inner, **fields: object) -> None:
        self.inner = inner
        self.fields = fields

    def event(self, name: str, **fields: object) -> None:
        payload = {**self.fields, **fields}
        self.inner.event(name, **payload)

    def bind(self, **fields: object) -> None:
        bind = getattr(self.inner, "bind", None)
        if bind is not None:
            bind(**fields)


class NullLog:
    """Discard events. Used by the single-provider slice entry point."""

    def event(self, name: str, **fields: object) -> None:
        del name, fields

    def bind(self, **fields: object) -> None:
        del fields


def read_events(path: Path) -> list[dict]:
    """Read a JSONL log. A non-object line or a line without ``event`` is an error."""

    if not path.is_file():
        return []
    events = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise HarnessError(f"malformed log {path}:{number}") from exc
        if not isinstance(record, dict) or not isinstance(record.get("event"), str):
            raise HarnessError(f"malformed log {path}:{number}")
        events.append(record)
    return events


def select_events(
    events: list[dict],
    *,
    task_index: int | None = None,
    provider: str | None = None,
    level: str | None = None,
    tail: int | None = None,
) -> list[dict]:
    """Keep events for one task, provider, and minimum level, then take the tail."""

    minimum = None if level is None else _LEVELS[level]
    selected = []
    for event in events:
        if task_index is not None and event.get("index") != task_index:
            continue
        if provider is not None and event.get("provider") != provider:
            continue
        if minimum is not None and _LEVELS.get(_stored_level(event), 10) < minimum:
            continue
        selected.append(event)
    if tail is None:
        return selected
    if tail < 0:
        raise HarnessError("--tail must be an integer >= 0")
    return selected[-tail:]


def _stored_level(event: dict) -> str:
    stored = event.get("level")
    if isinstance(stored, str) and stored in _LEVELS:
        return stored
    name = event.get("event")
    return event_level(name if isinstance(name, str) else "")


def _write_jsonl(handles: list, record: dict) -> None:
    line = json.dumps(record, ensure_ascii=False, sort_keys=True)
    for stream in handles:
        stream.write(line + "\n")
        stream.flush()

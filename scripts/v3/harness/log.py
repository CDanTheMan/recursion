"""Structured JSONL logs. Events name the provider and the outcome, not secrets."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from scripts.v3.harness.errors import HarnessError


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class JsonLog:
    """Append one JSON object per event."""

    def __init__(self, streams: list) -> None:
        self.streams = streams
        self._lock = threading.Lock()

    def event(self, name: str, **fields: object) -> None:
        record = {"event": name, "ts": utc_now(), **fields}
        line = json.dumps(record, ensure_ascii=False, sort_keys=True)
        with self._lock:
            for stream in self.streams:
                stream.write(line + "\n")
                stream.flush()


class NullLog:
    """Discard events. Used by the single-provider slice entry point."""

    def event(self, name: str, **fields: object) -> None:
        del name, fields


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

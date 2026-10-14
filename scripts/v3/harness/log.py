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
    """Append one JSON object per event.

    ``progress`` receives a short plain line for the same event. JSONL streams
    stay JSONL. A progress stream is not also a JSONL stream.
    """

    def __init__(self, streams: list, progress=None) -> None:
        self.streams = streams
        self.progress = progress
        self._lock = threading.Lock()

    def event(self, name: str, **fields: object) -> None:
        record = {"event": name, "ts": utc_now(), **fields}
        line = json.dumps(record, ensure_ascii=False, sort_keys=True)
        text = progress_line(name, fields)
        with self._lock:
            for stream in self.streams:
                stream.write(line + "\n")
                stream.flush()
            if self.progress is not None:
                self.progress.write(text + "\n")
                self.progress.flush()


def progress_line(name: str, fields: dict) -> str:
    """One plain line. Names the outcome and omits error bodies."""

    index = fields.get("index")
    provider = fields.get("provider")
    if name == "task.started" and _is_index(index):
        return f"task {index} started"
    if name == "task.completed" and _is_index(index):
        return f"task {index} completed provider={provider}"
    if name == "task.failed" and _is_index(index):
        return f"task {index} failed"
    if name == "task.cancelled" and _is_index(index):
        return f"task {index} cancelled"
    if name == "task.unreviewed" and _is_index(index):
        return f"task {index} unreviewed"
    if name == "task.conflict" and _is_index(index):
        return f"task {index} conflict"
    if name == "task.review_rejected" and _is_index(index):
        return f"task {index} review-rejected"
    if name == "provider.attempt":
        return f"provider {provider} attempt {fields.get('attempt')}"
    if name == "provider.result":
        return f"provider {provider} finished"
    if name == "provider.failed":
        error = fields.get("error")
        if isinstance(error, str) and error:
            return f"provider {provider} failed {error}"
        return f"provider {provider} failed"
    if name == "provider.skipped":
        return f"provider {provider} skipped"
    if name == "run.refused":
        return f"run refused {fields.get('error')}"
    if name == "run.resume":
        return f"run resume {fields.get('status')}"
    if name == "plan.admitted":
        return "plan admitted"
    if name == "plan.fallback":
        return "plan fallback"
    if name == "plan.ready":
        return "plan ready"
    if name == "route.selected":
        return f"route {fields.get('selected_route_id')}"
    if name == "provider.candidates":
        names = fields.get("candidates")
        if isinstance(names, list):
            return "candidates " + ",".join(str(item) for item in names)
        return "candidates"
    return name


def _is_index(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


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

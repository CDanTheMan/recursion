#!/usr/bin/env python3
"""Deterministic Phase 7 reporting and notification outbox.

The scheduler only observes canonical state and enqueues schema-v1 decisions. Every mutation is
an actuator subcommand and requires RECURSION_QUEUE_ACTUATION=1. Human-visible delivery continues
to use scripts/notify.sh; this module owns durable policy, retry, acknowledgement, reporting, and
recovery state around that existing transport boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from jsonl_durable import JsonlDurabilityError, append_jsonl as durable_append_jsonl, read_jsonl_objects
from transition_receipt import (
    TransitionReceiptError,
    commit_transition,
    json_mutation,
    recover_transitions,
)


IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
DESTINATION = re.compile(
    r"^(project-topic|head-hermes|lucas-direct|portfolio-account|portfolio-channel):"
    r"telegram:(-?[1-9][0-9]*)(?::([1-9][0-9]*))?$"
)
PROJECT_EVENTS = {
    "plan-proposed", "goal-accepted", "plan-approved", "pilot-window-armed", "pilot-window-opened",
    "pilot-window-closed", "worker-launched", "task-passed", "task-failed",
    "task-blocked", "human-answer-received", "review-branch-published", "goal-verifying",
    "goal-achieved", "goal-stopped", "project-digest",
}
TERMINAL_EVENT_TYPES = {"goal-achieved", "goal-stopped"}


class OutboxError(RuntimeError):
    pass


def base_root() -> Path:
    return Path(os.environ.get("RECURSION_ROOT") or Path(__file__).resolve().parent.parent)


def now_epoch() -> int:
    return int(time.time())


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def fsync_dir(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    temporary = Path(name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, sort_keys=True, separators=(",", ":"))
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        fsync_dir(path.parent)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def append_jsonl(path: Path, value: dict) -> None:
    try:
        outcome = durable_append_jsonl(path, value)
    except (JsonlDurabilityError, OSError) as exc:
        raise OutboxError(f"JSONL append failed: {exc}") from exc
    if outcome.quarantine is not None:
        raise OutboxError(
            "JSONL append repaired a torn tail; human review required: "
            f"{outcome.quarantine.get('escalation_id')}"
        )


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise OutboxError(f"JSON object required: {path}")
    return value


def read_fields(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        if re.fullmatch(r"[A-Za-z0-9_]+", key.strip()):
            result[key.strip()] = value.strip()
    return result


def stable_id(prefix: str, *parts: object) -> str:
    raw = json.dumps(parts, sort_keys=True, separators=(",", ":"), default=str).encode()
    return f"{prefix}-{hashlib.sha256(raw).hexdigest()[:24]}"


def canonical_event_seq(value: dict) -> int:
    try:
        sequence = int(value.get("event_seq") or 0)
    except (TypeError, ValueError) as exc:
        raise OutboxError("canonical notification event sequence is invalid") from exc
    if sequence < 0:
        raise OutboxError("canonical notification event sequence is invalid")
    return sequence


def commit_json_projection(base: Path, path: Path, value: dict, event: dict,
                           journal: str) -> dict:
    """Atomically bind one canonical notification projection to its audit row."""
    canonical = dict(value)
    canonical.pop("event_seq", None)
    canonical.pop("last_transition_id", None)
    try:
        commit_transition(base, [json_mutation(path, canonical)], event, journal=journal)
        committed = read_json(path)
    except (TransitionReceiptError, OSError, ValueError, json.JSONDecodeError) as exc:
        raise OutboxError(f"notification transition failed: {exc}") from exc
    value.clear()
    value.update(committed)
    return value


def recover_notification_transitions(base: Path) -> None:
    try:
        recover_transitions(base)
    except (TransitionReceiptError, OSError, ValueError, json.JSONDecodeError) as exc:
        raise OutboxError(f"notification transition recovery failed: {exc}") from exc


def configured(base: Path, project: str) -> tuple[dict, dict, list[str]]:
    config = read_json(base / "state/project-config" / f"{project}.json")
    pilot_id = str(config.get("pilot_id") or "")
    pilot = read_json(base / "state/pilots" / f"{pilot_id}.json")
    if config.get("id") != project or pilot.get("project_id") != project or pilot.get("id") != pilot_id:
        raise OutboxError("project/pilot identity is inconsistent")
    if config.get("status") != "active" or pilot.get("status") != "active":
        raise OutboxError("project/pilot is not active")
    targets = config.get("notification_targets")
    if not isinstance(targets, list) or not all(isinstance(item, str) for item in targets):
        raise OutboxError("notification targets are absent or malformed")
    if targets != pilot.get("notification_targets"):
        raise OutboxError("project and pilot notification targets disagree")
    if len(set(targets)) != len(targets) or any(parse_destination(item) is None for item in targets):
        raise OutboxError("notification targets contain a duplicate, malformed, or unknown destination")
    return config, pilot, targets


def parse_destination(value: str) -> dict | None:
    match = DESTINATION.fullmatch(value)
    if not match:
        return None
    kind, chat, thread = match.groups()
    if kind in {"project-topic", "head-hermes", "portfolio-channel"} and thread is None:
        return None
    if kind in {"lucas-direct", "portfolio-account"} and thread is not None:
        return None
    if kind == "lucas-direct" and chat.startswith("-"):
        return None
    return {"kind": kind, "transport": "telegram", "chat_id": chat, "thread_id": thread}


def policy_destinations(base: Path, project: str, event_type: str) -> list[str]:
    _, _, targets = configured(base, project)
    parsed = [(item, parse_destination(item)) for item in targets]
    by_kind: dict[str, list[str]] = {}
    for item, value in parsed:
        assert value is not None
        by_kind.setdefault(str(value["kind"]), []).append(item)
    if len(by_kind.get("project-topic", [])) != 1:
        raise OutboxError("exactly one configured project topic is required")
    if len(by_kind.get("head-hermes", [])) != 1:
        raise OutboxError("exactly one configured Head Hermes destination is required")
    if len(by_kind.get("lucas-direct", [])) != 1:
        raise OutboxError("exactly one configured Lucas direct destination is required")
    if event_type in PROJECT_EVENTS:
        return by_kind["project-topic"]
    if event_type == "portfolio-brief":
        return by_kind["head-hermes"]
    if event_type == "pilot-terminal-report":
        return by_kind["head-hermes"]
    if event_type == "portfolio-result":
        return by_kind["head-hermes"] + by_kind.get("portfolio-account", []) + by_kind.get("portfolio-channel", [])
    if event_type in {"lucas-attention-required", "delivery-dead-letter"}:
        return by_kind["lucas-direct"]
    raise OutboxError(f"unknown notification event policy: {event_type}")


def raw_events(base: Path) -> list[dict]:
    path = base / "state/events.jsonl"
    result: list[dict] = []
    if not path.is_file():
        return result
    try:
        rows = read_jsonl_objects(path)
    except JsonlDurabilityError as exc:
        raise OutboxError(f"source event journal is corrupt: {exc}") from exc
    for value in rows:
        source_id = str(value.get("id") or "")
        if not IDENT.fullmatch(source_id):
            # The identity survives event rotation/restore; line number and file position are not
            # canonical. Exact duplicate source records intentionally collapse before fan-out.
            source_id = stable_id("source", value)
        value = dict(value)
        value["_source_id"] = source_id
        result.append(value)
    return result


def detail_object(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def digest_occurrence_date(raw: dict) -> str:
    detail = detail_object(raw.get("detail"))
    explicit = detail.get("occurrence_date")
    candidate = explicit if explicit is not None else str(raw.get("ts") or "")[:10]
    if not isinstance(candidate, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", candidate):
        raise OutboxError("project digest occurrence_date is absent or invalid")
    try:
        if date.fromisoformat(candidate).isoformat() != candidate:
            raise ValueError
    except ValueError as exc:
        raise OutboxError("project digest occurrence_date is absent or invalid") from exc
    return candidate


def mapped_events(raw: dict) -> list[dict]:
    kind = str(raw.get("event") or "")
    detail = raw.get("detail")
    detail_text = detail if isinstance(detail, str) else json.dumps(detail, sort_keys=True)
    event_types: list[str] = []
    if kind == "goal-transition":
        data = detail_object(detail)
        source, target = str(data.get("from") or ""), str(data.get("to") or "")
        if source == "approved" and target == "active":
            event_types.extend(("goal-accepted", "plan-approved"))
        if target == "verifying":
            event_types.append("goal-verifying")
        if target == "achieved":
            event_types.append("goal-achieved")
        elif target in {"blocked", "abandoned", "budget-exhausted", "paused"}:
            event_types.append("goal-stopped")
    elif kind == "start":
        event_types.append("worker-launched")
    elif kind == "pilot-plan-proposed":
        event_types.append("plan-proposed")
    elif kind == "pilot-plan-approved":
        event_types.append("plan-approved")
    elif kind == "pilot-window-opened":
        event_types.append("pilot-window-opened")
    elif kind == "pilot-window-armed":
        event_types.append("pilot-window-armed")
    elif kind == "pilot-window-closed":
        event_types.append("pilot-window-closed")
    elif kind == "assist-open":
        event_types.append("lucas-attention-required")
    elif kind == "finish":
        match = re.search(r"(?:^|\s)status=(passed|failed|blocked)(?:\s|$)", detail_text)
        if match:
            event_types.append(f"task-{match.group(1)}")
    elif kind in {"block", "task-blocked"}:
        event_types.append("task-blocked")
    elif kind == "task-contract-invalid":
        # One receipt owns both canonical mutations.  Fan it out as the task stop and goal stop;
        # goal-stopped reconciliation already creates the one Lucas-attention event.
        event_types.extend(("task-blocked", "goal-stopped"))
    elif kind == "assist-answer":
        event_types.append("human-answer-received")
    elif kind in {"review-published", "review-branch-published"}:
        event_types.append("review-branch-published")
    elif kind in {"portfolio-brief", "project-digest"}:
        event_types.append(kind)
    result = []
    for event_type in event_types:
        occurrence_date = digest_occurrence_date(raw) if event_type == "project-digest" else None
        identity = [raw["_source_id"], event_type]
        # Preserve the pre-occurrence identity for legacy source rows so deployment cannot replay
        # an already-delivered digest. Newly emitted rows carry the explicit date and use it.
        if occurrence_date and detail_object(raw.get("detail")).get("occurrence_date") is not None:
            identity.append(occurrence_date)
        event_id = stable_id("event", *identity)
        event = {
            "id": event_id, "source_event_id": raw["_source_id"], "event_type": event_type,
            "project_id": str(raw.get("project") or ""), "goal_id": str(raw.get("goal") or ""),
            "task_id": str(raw.get("task") or ""), "occurred_at": str(raw.get("ts") or now_iso()),
            "source": raw,
        }
        if occurrence_date:
            event["occurrence_date"] = occurrence_date
        result.append(event)
    return result


def all_mapped(base: Path, project: str | None = None) -> list[dict]:
    result: list[dict] = []
    for raw in raw_events(base):
        for event in mapped_events(raw):
            if not project or event["project_id"] == project:
                result.append(event)
    return result


def message_for(event: dict) -> str:
    labels = {
        "plan-proposed": "Plan proposed", "goal-accepted": "Goal accepted",
        "plan-approved": "Plan approved", "pilot-window-armed": "Pilot window armed",
        "pilot-window-opened": "Pilot window opened",
        "pilot-window-closed": "Pilot window closed",
        "worker-launched": "Worker launched", "task-passed": "Task passed",
        "task-failed": "Task failed", "task-blocked": "Task blocked",
        "human-answer-received": "Human answer received",
        "review-branch-published": "Review branch published",
        "goal-verifying": "Goal verifying", "goal-achieved": "Goal achieved",
        "goal-stopped": "Goal stopped", "pilot-terminal-report": "Project pilot terminal report",
        "portfolio-result": "Head Hermes portfolio result",
        "lucas-attention-required": "Lucas attention required",
        "delivery-dead-letter": "Delivery dead letter",
        "portfolio-brief": "Portfolio brief", "project-digest": "Project digest",
    }
    label = labels[event["event_type"]]
    detail = detail_object((event.get("source") or {}).get("detail"))
    if event["event_type"] in {"portfolio-brief", "project-digest"}:
        if event["event_type"] == "project-digest":
            occurrence_date = digest_occurrence_date(event.get("source") or {})
            if event.get("occurrence_date") != occurrence_date:
                raise OutboxError("project digest occurrence_date does not match its source")
        message = detail.get("message")
        digest = detail.get("message_digest")
        if not isinstance(message, str) or not message or len(message.encode()) > 3800:
            raise OutboxError("monitoring notification message is absent or oversized")
        if digest != hashlib.sha256(message.encode()).hexdigest():
            raise OutboxError("monitoring notification message digest is invalid")
        return message
    suffix = f" goal={event.get('goal_id') or '-'}"
    if event.get("task_id"):
        suffix += f" task={event['task_id']}"
    if event["event_type"] in {"plan-proposed", "plan-approved"}:
        suffix += f" plan={detail.get('plan_id') or '-'} digest={detail.get('plan_digest') or '-'}"
    if event["event_type"] in {"pilot-window-armed", "pilot-window-opened", "pilot-window-closed"}:
        suffix += f" window={detail.get('window_id') or '-'}"
    if event["event_type"] == "lucas-attention-required" and event.get("task_id"):
        raw_detail = str((event.get("source") or {}).get("detail") or "")[:300]
        suffix += f" question={raw_detail} reply='assist {event['task_id']} <answer>'"
    return f"{label}: project={event['project_id']}{suffix} event={event['id']}"


def delivery_records(base: Path, project: str | None = None) -> list[tuple[Path, dict]]:
    result: list[tuple[Path, dict]] = []
    for path in sorted((base / "state/deliveries").glob("*.json")):
        try:
            value = read_json(path)
        except (OSError, json.JSONDecodeError, OutboxError):
            continue
        if project and value.get("project_id") != project:
            continue
        result.append((path, value))
    return result


def notification_events(base: Path, project: str | None = None) -> list[tuple[Path, dict]]:
    result: list[tuple[Path, dict]] = []
    for path in sorted((base / "state/notification-events").glob("*.json")):
        try:
            value = read_json(path)
        except (OSError, json.JSONDecodeError, OutboxError):
            continue
        if project and value.get("project_id") != project:
            continue
        result.append((path, value))
    return result


def delivery_event(record: dict, transition: str, timestamp: str,
                   **extra: object) -> dict:
    next_sequence = canonical_event_seq(record) + 1
    return {
        "schema_version": 1,
        "id": stable_id("delivery-event", record["id"], next_sequence, transition),
        "ts": timestamp, "delivery_id": record["id"],
        "event_id": record["event_id"], "destination": record["destination"],
        "status": record["status"], "attempt": record.get("attempt", 0),
        "transition": transition, **extra,
    }


def write_delivery(base: Path, record: dict, transition: str, **extra: object) -> None:
    timestamp = now_iso()
    record["updated_at"] = timestamp
    event = delivery_event(record, transition, timestamp, **extra)
    commit_json_projection(
        base,
        base / "state/deliveries" / f"{record['id']}.json",
        record,
        event,
        "state/delivery-events.jsonl",
    )


def existing_pair(base: Path, event_id: str, destination: str) -> dict | None:
    matches = [(path, value) for path, value in delivery_records(base)
               if value.get("event_id") == event_id and value.get("destination") == destination]
    if not matches:
        return None
    if len(matches) != 1:
        raise OutboxError("duplicate delivery records exist for one event/destination pair")
    path, value = matches[0]
    expected_id = stable_id("delivery", event_id, destination)
    if value.get("id") != expected_id or path.name != f"{expected_id}.json":
        raise OutboxError("delivery pair does not use its deterministic canonical identity")
    return value


def create_delivery(base: Path, event: dict, destination: str) -> dict:
    prior = existing_pair(base, event["id"], destination)
    if prior:
        expected = {
            "id": stable_id("delivery", event["id"], destination),
            "event_id": event["id"], "project_id": event["project_id"],
            "goal_id": event.get("goal_id") or None, "task_id": event.get("task_id") or None,
            "destination": destination, "message_digest": event["message_digest"],
        }
        if any(prior.get(key) != value for key, value in expected.items()):
            raise OutboxError("existing delivery pair disagrees with canonical event/routing content")
        return prior
    delivery_id = stable_id("delivery", event["id"], destination)
    maximum = int(os.environ.get("RECURSION_DELIVERY_MAX_ATTEMPTS", "3"))
    if not 1 <= maximum <= 20:
        raise OutboxError("delivery attempt budget must be 1..20")
    record = {
        "schema_version": 1, "id": delivery_id, "event_id": event["id"],
        "project_id": event["project_id"], "goal_id": event.get("goal_id") or None,
        "task_id": event.get("task_id") or None, "destination": destination,
        "attempt": 0, "acknowledgement": None, "status": "pending",
        "next_attempt_at": 0, "max_attempts": maximum, "backoff_seconds": 0,
        "last_error": None, "attempt_token": None, "receipt_path": None,
        "message_digest": event["message_digest"], "created_at": now_iso(), "updated_at": now_iso(),
    }
    write_delivery(base, record, "enqueued")
    return record


def escalate(base: Path, key: str, title: str, pointer: str, project: str) -> None:
    process = subprocess.run(
        ["bash", str(base / "scripts/taskctl.sh"), "esc-record", key, title, project, pointer],
        cwd=base, env={**os.environ, "RECURSION_ROOT": str(base)},
        text=True, capture_output=True, check=False,
    )
    if process.returncode:
        detail = (process.stderr or process.stdout or "taskctl escalation failed").strip()
        raise OutboxError(f"durable escalation failed: {detail}")
    if not escalation_is_open(base, key):
        raise OutboxError("taskctl reported escalation success without one durable OPEN identity")


def escalation_is_open(base: Path, key: str) -> bool:
    path = base / "state/escalations.tsv"
    if not path.is_file():
        return False
    lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
    header = "#id\tkey\tstatus\tfirst_seen\tlast_seen\tcount\tworkstream\tpointer\ttitle"
    if not lines or lines[0] != header:
        raise OutboxError("escalation index schema is invalid")
    matches: list[str] = []
    for line in lines[1:]:
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) != 9 or fields[2] not in {"open", "resolved"} \
                or not fields[0].startswith("esc-") or not fields[5].isdigit():
            raise OutboxError("escalation index contains a malformed record")
        if fields[1] == key:
            matches.append(fields[2])
    if len(matches) > 1:
        raise OutboxError("escalation index contains duplicate routing identities")
    return matches == ["open"]


def event_input_from_projection(value: dict) -> dict:
    excluded = {
        "schema_version", "message", "message_digest", "created_at", "status", "routing_error",
        "event_seq", "last_transition_id",
    }
    return {key: item for key, item in value.items() if key not in excluded}


def expected_event_projection(base: Path, event: dict, created_at: str) -> tuple[dict, list[str]]:
    value = dict(event)
    value.update({"schema_version": 1, "message": message_for(event), "created_at": created_at,
                  "status": "recorded", "routing_error": None})
    value["message_digest"] = hashlib.sha256(value["message"].encode()).hexdigest()
    try:
        destinations = policy_destinations(base, value["project_id"], value["event_type"])
    except (OSError, json.JSONDecodeError, OutboxError) as exc:
        value["routing_error"] = str(exc)
        destinations = []
    return value, destinations


def inspect_event_projection(base: Path, event: dict) -> tuple[dict, list[str], list[str]]:
    path = base / "state/notification-events" / f"{event['id']}.json"
    value = read_json(path)
    if value.get("id") != event.get("id") or path.name != f"{event['id']}.json":
        raise OutboxError("notification projection identity is inconsistent")
    created_at = value.get("created_at")
    if not isinstance(created_at, str) or not created_at:
        raise OutboxError("notification projection lacks its canonical creation time")
    expected, destinations = expected_event_projection(base, event, created_at)
    comparable = dict(value)
    comparable.pop("event_seq", None)
    comparable.pop("last_transition_id", None)
    if comparable != expected:
        raise OutboxError("notification projection disagrees with exact event content or routing")
    records = [(path, row) for path, row in delivery_records(base)
               if row.get("event_id") == value["id"]]
    if value.get("routing_error") and records:
        raise OutboxError("routing-error notification unexpectedly owns delivery records")
    allowed = set(destinations)
    if any(str(row.get("destination") or "") not in allowed for _, row in records):
        raise OutboxError("notification projection has a delivery outside its exact routing policy")
    present: set[str] = set()
    for record_path, record in records:
        destination = str(record.get("destination") or "")
        if destination in present:
            raise OutboxError("notification projection has duplicate delivery routing pairs")
        present.add(destination)
        expected_id = stable_id("delivery", value["id"], destination)
        expected_fields = {
            "id": expected_id, "event_id": value["id"], "project_id": value["project_id"],
            "goal_id": value.get("goal_id") or None, "task_id": value.get("task_id") or None,
            "destination": destination, "message_digest": value["message_digest"],
        }
        if record_path.name != f"{expected_id}.json" \
                or any(record.get(key) != item for key, item in expected_fields.items()):
            raise OutboxError("notification delivery disagrees with exact projection identity/content")
    missing = [destination for destination in destinations if destination not in present]
    return value, destinations, missing


def create_event(base: Path, event: dict) -> dict:
    path = base / "state/notification-events" / f"{event['id']}.json"
    if path.is_file():
        value, destinations, missing = inspect_event_projection(base, event)
        if value["routing_error"]:
            key = f"notification-routing:{value['id']}"
            if not escalation_is_open(base, key):
                escalate(base, key, f"Notification routing failed for {value['event_type']}",
                         str(path), value["project_id"])
            return value
        for destination in missing:
            create_delivery(base, value, destination)
        return value
    value, destinations = expected_event_projection(base, event, now_iso())
    event = {
        "schema_version": 1,
        "id": stable_id("notification-event-event", value["id"], canonical_event_seq(value) + 1,
                        "created"),
        "ts": now_iso(), "event_id": value["id"],
        "event_type": value["event_type"], "project_id": value["project_id"],
        "goal_id": value.get("goal_id"), "source_event_id": value.get("source_event_id"),
        "transition": "created", "routing_error": value.get("routing_error"),
    }
    commit_json_projection(base, path, value, event, "state/notification-event-events.jsonl")
    if value["routing_error"]:
        escalate(base, f"notification-routing:{value['id']}",
                 f"Notification routing failed for {value['event_type']}", str(path), value["project_id"])
        return value
    for destination in destinations:
        create_delivery(base, value, destination)
    return value


def event_reconciliation_needed(base: Path, event: dict) -> bool:
    path = base / "state/notification-events" / f"{event['id']}.json"
    if not path.is_file():
        return True
    value, _, missing = inspect_event_projection(base, event)
    if value.get("routing_error"):
        return not escalation_is_open(base, f"notification-routing:{value['id']}")
    if missing:
        return True
    if value.get("event_type") in TERMINAL_EVENT_TYPES:
        return terminal_report_reconciliation_needed(base, value)
    return False


def find_mapped(base: Path, project: str, event_id: str) -> dict:
    for event in all_mapped(base, project):
        if event["id"] == event_id:
            return event
    raise OutboxError(f"mapped source event is absent: {event_id}")


def build_chain(base: Path, project: str, goal_id: str) -> dict:
    goal_path = base / "state/goals" / f"{goal_id}.md"
    if not goal_path.is_file():
        for candidate in (base / "state/goals").glob("*.md"):
            if read_fields(candidate).get("id") == goal_id:
                goal_path = candidate
                break
    goal = read_fields(goal_path)
    instruction_id = goal.get("instruction_id", "")
    instruction_path = base / "state/instructions" / (f"{int(instruction_id):08d}.md" if instruction_id.isdigit() else f"{instruction_id}.md")
    instruction = read_fields(instruction_path)
    plans = []
    for path in sorted((base / "state/pilot-requests" / project).glob("*.json")):
        try:
            row = read_json(path)
        except Exception:
            continue
        if row.get("goal_id") == goal_id and row.get("verb") == "pilot-plan-propose":
            plans.append(row)
    structured_plans = []
    for path in sorted((base / "state/plans" / project).glob("*.json")):
        try:
            row = read_json(path)
        except Exception:
            continue
        plan_goal = row.get("plan", {}).get("goal", {}) if isinstance(row.get("plan"), dict) else {}
        if plan_goal.get("id") == goal_id:
            structured_plans.append(row)
    plans.extend(structured_plans)
    approval_instructions = []
    for row in structured_plans:
        approval_id = str(row.get("approval_instruction_id") or "")
        if not approval_id:
            continue
        approval_path = base / "state/instructions" / (
            f"{int(approval_id):08d}.md" if approval_id.isdigit() else f"{approval_id}.md"
        )
        approval_instructions.append({"id": approval_id, "record": read_fields(approval_path)})
    windows = []
    for path in sorted((base / "state/pilot-windows").glob("*.json")):
        try:
            row = read_json(path)
        except Exception:
            continue
        if row.get("project_id") == project and row.get("goal_id") == goal_id:
            windows.append(row)
    tasks = []
    for path in sorted((base / "state/tasks").glob("*.md")):
        row = read_fields(path)
        if row.get("goal_id") == goal_id:
            tasks.append(row)
    task_ids = {row.get("id") for row in tasks}
    actions = []
    for path in sorted((base / "state/actions").glob("*.json")):
        try:
            row = read_json(path)
        except Exception:
            continue
        if row.get("goal_id") == goal_id or (instruction_id and row.get("instruction_id") == instruction_id):
            actions.append(row)
    runs = []
    for path in sorted((base / "state/runs").glob("*.json")):
        try:
            row = read_json(path)
        except Exception:
            continue
        if row.get("goal_id") == goal_id or row.get("task_id") in task_ids:
            runs.append(row)
    implementers = [row for row in runs if row.get("role") == "implementer"]
    verifiers = [row for row in runs if row.get("role") == "verifier"]
    commits = sorted({str(row.get("candidate_commit") or "") for row in tasks if row.get("candidate_commit")}
                     | {str(row.get("commit_oid") or "") for row in runs if row.get("commit_oid")})
    gates = [row.get("machine_gate") for row in implementers if isinstance(row.get("machine_gate"), dict)]
    review = []
    controller_rejections = []
    for raw in raw_events(base):
        if raw.get("project") != project or raw.get("goal") != goal_id:
            continue
        if raw.get("event") in {"review-published", "review-branch-published"}:
            review.append(raw)
        if raw.get("event") == "task-contract-invalid":
            controller_rejections.append(raw)
    pilot_path = base / "state/reports" / f"{goal_id}-pilot.json"
    head_path = base / "state/reports" / f"{goal_id}-head.json"
    pilot_report = read_json(pilot_path) if pilot_path.is_file() else None
    head_report = read_json(head_path) if head_path.is_file() else None
    acknowledgements = []
    event_ids = {row[1].get("id") for row in notification_events(base, project)
                 if row[1].get("goal_id") == goal_id}
    relevant_deliveries = [row for _, row in delivery_records(base, project) if row.get("event_id") in event_ids]
    for row in relevant_deliveries:
        receipt = valid_receipt(base, row)
        if row.get("status") == "succeeded" and receipt:
            acknowledgements.append({
                "delivery_id": row["id"], "event_id": row["event_id"],
                "destination": row["destination"], "transport": receipt["transport"],
                "transport_message_id": receipt["message_id"], "acknowledged_at": receipt["acknowledged_at"],
            })
    rejection_complete = False
    if len(controller_rejections) == 1:
        rejection = controller_rejections[0]
        rejection_task_id = str(rejection.get("task") or "")
        rejection_task = next((row for row in tasks if row.get("id") == rejection_task_id), {})
        transition_id = str(rejection.get("transition_id") or "")
        detail = detail_object(rejection.get("detail"))
        failed_work = [
            row for row in actions
            if row.get("verb") == "work" and row.get("status") == "failed"
            and rejection_task_id in [str(item) for item in (row.get("arguments") or [])]
        ]
        rejection_complete = bool(
            re.fullmatch(r"transition-[0-9a-f]{32}", transition_id)
            and goal.get("status") == "blocked"
            and goal.get("last_transition_reason") == "task-contract-invalid"
            and goal.get("last_transition_task") == rejection_task_id
            and goal.get("last_transition_id") == transition_id
            and rejection_task.get("status") == "blocked"
            and rejection_task.get("transition_reason") == "task-contract-invalid"
            and rejection_task.get("contract_rejection_event_id") == rejection.get("id")
            and rejection_task.get("last_transition_id") == transition_id
            and int(rejection_task.get("attempts") or 0) == 0
            and detail == {"attempts": 0, "reason": "invalid-acceptance-gate",
                           "stage": "controller-pre-worker"}
            and len(failed_work) == 1
            and not runs and not commits and not gates and not verifiers and not review
        )
    return {
        "goal": goal,
        "instruction": {"id": instruction_id, "record": instruction, "action_ids": instruction.get("action_ids")},
        "plan": plans, "plan_approval": approval_instructions, "pilot_windows": windows,
        "actions": actions, "tasks": tasks, "workers": runs, "commits": commits, "gates": gates,
        "verifier": verifiers, "review_branch": review, "controller_rejections": controller_rejections,
        "pilot_report": pilot_report,
        "head_report": head_report, "delivery_acknowledgements": acknowledgements,
        "_delivery_count": len(relevant_deliveries),
        "_all_acknowledged": bool(relevant_deliveries) and len(acknowledgements) == len(relevant_deliveries),
        "_controller_rejection_complete": rejection_complete,
    }


def terminal_report_event(base: Path, terminal: dict, create: bool) -> dict | None:
    project, goal_id = terminal["project_id"], terminal["goal_id"]
    report_path = base / "state/reports" / f"{goal_id}-pilot.json"
    if report_path.is_file():
        report = read_json(report_path)
        expected = {
            "id": f"pilot-report-{goal_id}", "project_id": project, "goal_id": goal_id,
            "terminal_event_id": terminal["id"], "terminal_status": terminal["event_type"],
        }
        if any(report.get(key) != value for key, value in expected.items()) \
                or not isinstance(report.get("created_at"), str) or not report.get("created_at") \
                or not isinstance(report.get("evidence"), dict):
            raise OutboxError("pilot terminal report disagrees with its canonical terminal event")
    else:
        if not create:
            return None
        chain = build_chain(base, project, goal_id)
        execution_prerequisites = bool(
            chain["instruction"]["id"] and chain["instruction"]["record"] and chain["plan"] and chain["actions"] and
            chain["tasks"] and chain["workers"] and chain["commits"] and chain["gates"] and chain["verifier"]
        )
        rejection_source = str((terminal.get("source") or {}).get("event") or "") \
            == "task-contract-invalid"
        rejection_prerequisites = bool(
            rejection_source and chain["instruction"]["id"] and chain["instruction"]["record"]
            and chain["plan"] and chain["actions"] and chain["tasks"]
            and chain.get("_controller_rejection_complete", False)
        )
        prerequisites = execution_prerequisites or rejection_prerequisites
        if any("plan_digest" in row for row in chain["plan"]):
            prerequisites = prerequisites and bool(chain["plan_approval"] and chain["pilot_windows"])
        if terminal["event_type"] == "goal-achieved":
            prerequisites = prerequisites and bool(chain["review_branch"])
        if not prerequisites:
            key = f"terminal-trace:{goal_id}"
            if not escalation_is_open(base, key):
                escalate(base, key, "Terminal goal lacks a complete pre-delivery trace",
                         f"state/goals/{goal_id}.md", project)
            return None
        report = {
            "schema_version": 1, "id": f"pilot-report-{goal_id}", "project_id": project,
            "goal_id": goal_id, "terminal_event_id": terminal["id"],
            "terminal_status": terminal["event_type"], "created_at": now_iso(),
            "evidence": {key: value for key, value in chain.items() if not key.startswith("_")},
        }
        atomic_json(report_path, report)
    return {
        "id": stable_id("event", goal_id, "pilot-terminal-report"),
        "source_event_id": terminal["id"], "event_type": "pilot-terminal-report",
        "project_id": project, "goal_id": goal_id, "task_id": "",
        "occurred_at": report["created_at"],
        "report_id": report["id"],
    }


def terminal_report_reconciliation_needed(base: Path, terminal: dict) -> bool:
    pilot_event = terminal_report_event(base, terminal, create=False)
    if pilot_event is None:
        return True
    return event_reconciliation_needed(base, pilot_event)


def create_terminal_reports(base: Path, terminal: dict) -> None:
    pilot_event = terminal_report_event(base, terminal, create=True)
    if pilot_event is not None:
        create_event(base, pilot_event)


def reconcile_event(base: Path, project: str, event_id: str) -> None:
    require_actuator()
    recover_notification_transitions(base)
    event = find_mapped(base, project, event_id)
    value = create_event(base, event)
    if value["event_type"] in TERMINAL_EVENT_TYPES and not value.get("routing_error"):
        create_terminal_reports(base, value)
    if value["event_type"] == "goal-stopped" and not value.get("routing_error"):
        attention = {
            "id": stable_id("event", value["id"], "lucas-attention-required"),
            "source_event_id": value["id"], "event_type": "lucas-attention-required",
            "project_id": project, "goal_id": value.get("goal_id") or "", "task_id": "",
            # This projection is replayable.  A fresh wall-clock value made an exact retry
            # disagree with the already-recorded attention event even though its id was stable.
            "occurred_at": value.get("occurred_at") or value.get("created_at") or now_iso(),
        }
        create_event(base, attention)


def valid_receipt(base: Path, delivery: dict) -> dict | None:
    receipt_path = delivery.get("receipt_path")
    if receipt_path:
        path = base / str(receipt_path)
    else:
        path = base / "state/transport-evidence" / f"{delivery.get('id')}.json"
    if not path.is_file():
        return None
    try:
        value = read_json(path)
    except Exception:
        return None
    valid = bool(
        value.get("accepted") is True and value.get("transport") == "telegram" and
        value.get("delivery_id") == delivery.get("id") and value.get("event_id") == delivery.get("event_id") and
        value.get("destination") == delivery.get("destination") and
        value.get("message_digest") == delivery.get("message_digest") and
        value.get("message_id") and value.get("acknowledged_at")
    )
    return value if valid else None


def backoff(attempt: int) -> int:
    base = int(os.environ.get("RECURSION_DELIVERY_BACKOFF_BASE_S", "10"))
    maximum = int(os.environ.get("RECURSION_DELIVERY_BACKOFF_MAX_S", "300"))
    if base < 1 or maximum < 1 or base > maximum or maximum > 86400:
        raise OutboxError("delivery backoff bounds are invalid")
    return min(maximum, base * (2 ** max(0, attempt - 1)))


def dead_letter_attention_event(base: Path, record: dict, source: dict) -> dict | None:
    if source.get("id") != record.get("event_id") \
            or source.get("project_id") != record.get("project_id") \
            or source.get("message_digest") != record.get("message_digest"):
        raise OutboxError("dead-letter source projection disagrees with the failed delivery")
    if source.get("event_type") == "delivery-dead-letter":
        return None
    event_id = stable_id("event", record["id"], "delivery-dead-letter")
    path = base / "state/notification-events" / f"{event_id}.json"
    occurred_at = record.get("updated_at") or now_iso()
    if path.is_file():
        occurred_at = read_json(path).get("occurred_at") or occurred_at
    return {
        "id": event_id, "source_event_id": str(record["event_id"]),
        "event_type": "delivery-dead-letter", "project_id": str(record["project_id"]),
        "goal_id": str(record.get("goal_id") or ""), "task_id": str(record.get("task_id") or ""),
        "occurred_at": occurred_at, "failed_delivery_id": record["id"],
    }


def reconcile_dead_letter(base: Path, record: dict) -> None:
    if record.get("status") != "dead-letter":
        raise OutboxError("dead-letter reconciliation requires terminal delivery state")
    key = f"delivery-dead-letter:{record['id']}"
    if not escalation_is_open(base, key):
        escalate(base, key, f"Permanent notification failure for {record['destination']}",
                 f"state/deliveries/{record['id']}.json",
                 str(record.get("project_id") or "recursion"))
    source = read_json(base / "state/notification-events" / f"{record.get('event_id')}.json")
    attention = dead_letter_attention_event(base, record, source)
    if attention is not None:
        create_event(base, attention)


def dead_letter_reconciliation_needed(base: Path, record: dict) -> bool:
    key = f"delivery-dead-letter:{record['id']}"
    if not escalation_is_open(base, key):
        return True
    source = read_json(base / "state/notification-events" / f"{record.get('event_id')}.json")
    attention = dead_letter_attention_event(base, record, source)
    return attention is not None and event_reconciliation_needed(base, attention)


def dead_letter(base: Path, record: dict, error: str) -> None:
    record.update({"status": "dead-letter", "acknowledgement": None, "next_attempt_at": None,
                   "last_error": error, "attempt_token": None})
    write_delivery(base, record, "dead-letter", error=error)
    reconcile_dead_letter(base, record)


def deliver(base: Path, project: str, delivery_id: str) -> None:
    require_actuator()
    recover_notification_transitions(base)
    path = base / "state/deliveries" / f"{delivery_id}.json"
    record = read_json(path)
    if record.get("id") != delivery_id or record.get("project_id") != project:
        raise OutboxError("delivery identity or project is inconsistent")
    if record.get("status") in {"succeeded", "cancelled"}:
        return
    if record.get("status") == "dead-letter":
        reconcile_dead_letter(base, record)
        return
    event = read_json(base / "state/notification-events" / f"{record.get('event_id')}.json")
    try:
        allowed = policy_destinations(base, project, str(event.get("event_type") or ""))
    except Exception as exc:
        dead_letter(base, record, f"routing policy invalid: {exc}")
        return
    if record.get("destination") not in allowed or not parse_destination(str(record.get("destination") or "")):
        dead_letter(base, record, "destination is not configured for this event policy")
        return
    if event.get("message_digest") != record.get("message_digest"):
        dead_letter(base, record, "message identity changed after enqueue")
        return
    receipt = valid_receipt(base, record)
    if receipt:
        record.update({"status": "succeeded", "acknowledgement": str(receipt["message_id"]),
                       "next_attempt_at": None, "last_error": None, "attempt_token": None,
                       "receipt_path": f"state/transport-evidence/{delivery_id}.json"})
        write_delivery(base, record, "acknowledged-from-durable-transport-evidence",
                       transport_message_id=receipt["message_id"])
        return
    if record.get("status") == "running":
        dead_letter(base, record, "prior attempt outcome is ambiguous and has no transport evidence")
        return
    due = int(record.get("next_attempt_at") or 0)
    if due > now_epoch():
        return
    attempt = int(record.get("attempt") or 0) + 1
    maximum = int(record.get("max_attempts") or 0)
    if maximum < 1 or attempt > maximum:
        dead_letter(base, record, "delivery retry budget exhausted")
        return
    token = stable_id("attempt", delivery_id, attempt, record["message_digest"])
    record.update({"status": "running", "attempt": attempt, "attempt_token": token,
                   "attempt_started_at": now_iso(), "next_attempt_at": None, "last_error": None})
    write_delivery(base, record, "attempt-started")
    receipt_relative = f"state/transport-evidence/{delivery_id}.json"
    command = [
        "bash", str(base / "scripts/notify.sh"), "--destination", str(record["destination"]),
        "--delivery-id", delivery_id, "--event-id", str(record["event_id"]),
        "--attempt-token", token, "--message-digest", str(record["message_digest"]),
        "--evidence", str(base / receipt_relative), str(event["message"]),
    ]
    process = subprocess.run(command, cwd=base, env={**os.environ, "RECURSION_ROOT": str(base)},
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    record = read_json(path)
    record["receipt_path"] = receipt_relative
    receipt = valid_receipt(base, record)
    if process.returncode == 0 and receipt:
        if os.environ.get("RECURSION_DELIVERY_CRASH_AFTER_RECEIPT") == "1":
            os._exit(97)
        record.update({"status": "succeeded", "acknowledgement": str(receipt["message_id"]),
                       "next_attempt_at": None, "last_error": None, "attempt_token": None})
        write_delivery(base, record, "acknowledged", transport_message_id=receipt["message_id"])
        return
    if process.returncode == 75:
        record.update({"status": "pending", "attempt": max(0, attempt - 1),
                       "acknowledgement": None, "next_attempt_at": 0, "backoff_seconds": 0,
                       "last_error": "PAUSE held delivery before transport acceptance",
                       "attempt_token": None, "attempt_started_at": None, "receipt_path": None})
        write_delivery(base, record, "pause-held")
        raise OutboxError("PAUSE interrupted notification delivery; pending state preserved")
    if process.returncode == 10 and attempt < maximum:
        delay = backoff(attempt)
        record.update({"status": "failed", "acknowledgement": None,
                       "next_attempt_at": now_epoch() + delay, "backoff_seconds": delay,
                       "last_error": "confirmed retryable transport failure", "attempt_token": None})
        write_delivery(base, record, "retry-scheduled", backoff_seconds=delay)
        return
    reason = "retry budget exhausted" if process.returncode == 10 else (
        "permanent transport rejection" if process.returncode == 11 else
        "transport returned no valid acceptance evidence"
    )
    dead_letter(base, record, reason)


def portfolio_report(base: Path, project: str, goal_id: str) -> None:
    require_actuator()
    recover_notification_transitions(base)
    pilot_event_id = stable_id("event", goal_id, "pilot-terminal-report")
    pilot_event = read_json(base / "state/notification-events" / f"{pilot_event_id}.json")
    pilot_deliveries = [value for _, value in delivery_records(base, project)
                        if value.get("event_id") == pilot_event_id]
    if len(pilot_deliveries) != 1 or pilot_deliveries[0].get("status") != "succeeded" or not valid_receipt(base, pilot_deliveries[0]):
        raise OutboxError("Head Hermes pilot report lacks durable transport acknowledgement")
    report = {
        "schema_version": 1, "id": f"head-report-{goal_id}", "project_id": project,
        "goal_id": goal_id, "pilot_report_id": pilot_event.get("report_id"),
        "pilot_delivery_id": pilot_deliveries[0]["id"], "created_at": now_iso(),
        "result": "terminal project result accepted by Head Hermes",
    }
    atomic_json(base / "state/reports" / f"{goal_id}-head.json", report)
    event = {
        "id": stable_id("event", goal_id, "portfolio-result"),
        "source_event_id": pilot_event_id, "event_type": "portfolio-result",
        "project_id": project, "goal_id": goal_id, "task_id": "", "occurred_at": now_iso(),
        "report_id": report["id"],
    }
    create_event(base, event)


def audit_goal(base: Path, project: str, goal_id: str) -> None:
    require_actuator()
    recover_notification_transitions(base)
    chain = build_chain(base, project, goal_id)
    execution_required = bool(
        chain["instruction"]["id"] and chain["instruction"]["record"] and chain["plan"] and chain["actions"] and
        chain["tasks"] and chain["workers"] and chain["commits"] and chain["gates"] and
        chain["verifier"] and chain["pilot_report"] and chain["head_report"] and
        chain["_all_acknowledged"]
    )
    rejection_required = bool(
        chain["instruction"]["id"] and chain["instruction"]["record"] and chain["plan"] and chain["actions"]
        and chain["tasks"] and chain.get("_controller_rejection_complete", False)
        and chain["pilot_report"] and chain["head_report"] and chain["_all_acknowledged"]
    )
    required = execution_required or rejection_required
    terminal_types = {value.get("event_type") for _, value in notification_events(base, project)
                      if value.get("goal_id") == goal_id and value.get("event_type") in TERMINAL_EVENT_TYPES}
    if "goal-achieved" in terminal_types:
        required = required and bool(chain["review_branch"])
    path = base / "state/reports" / f"{goal_id}-audit.json"
    prior = read_json(path) if path.is_file() else {}
    prior_sequence = canonical_event_seq(prior)
    audit = {
        "schema_version": 1, "id": f"goal-audit-{goal_id}", "project_id": project,
        "goal_id": goal_id, "complete": required, "updated_at": now_iso(),
        "chain": {key: value for key, value in chain.items() if not key.startswith("_")},
    }
    event = {
        "schema_version": 1,
        "id": stable_id("notification-audit-event", goal_id, prior_sequence + 1),
        "ts": now_iso(), "goal_id": goal_id,
        "project_id": project, "complete": required,
        "delivery_acknowledgements": len(chain["delivery_acknowledgements"]),
    }
    commit_json_projection(base, path, audit, event, "state/notification-audit-events.jsonl")


def recover(base: Path, project: str, goal_id: str) -> None:
    require_actuator()
    recover_notification_transitions(base)
    events = [value for _, value in notification_events(base, project)
              if not goal_id or value.get("goal_id") == goal_id]
    records = [value for _, value in delivery_records(base, project)
               if not goal_id or value.get("goal_id") == goal_id]
    for event in events:
        create_event(base, event_input_from_projection(event))
    records = [value for _, value in delivery_records(base, project)
               if not goal_id or value.get("goal_id") == goal_id]
    for record in records:
        if record.get("status") == "dead-letter":
            reconcile_dead_letter(base, record)
        elif record.get("status") == "running" and valid_receipt(base, record):
            record.update({"status": "succeeded", "acknowledgement": valid_receipt(base, record)["message_id"],
                           "next_attempt_at": None, "last_error": None, "attempt_token": None})
            write_delivery(base, record, "recovery-acknowledged")
        elif record.get("status") == "succeeded" and not valid_receipt(base, record):
            dead_letter(base, record, "legacy success lacks durable transport evidence")
    records = [value for _, value in delivery_records(base, project)
               if not goal_id or value.get("goal_id") == goal_id]
    pairs = [(row.get("event_id"), row.get("destination")) for row in records]
    path = base / "state/recovery" / f"notification-{project}-{goal_id or 'all'}.json"
    prior = read_json(path) if path.is_file() else {}
    prior_sequence = canonical_event_seq(prior)
    snapshot = {
        "schema_version": 1, "id": stable_id("notification-recovery", project, goal_id, pairs,
                                               [(row.get("id"), row.get("status"), row.get("attempt")) for row in records]),
        "project_id": project, "goal_id": goal_id or None, "observed_at": now_iso(),
        "events": len(events), "outbox_items": len(records),
        "acknowledgements": sum(row.get("status") == "succeeded" and valid_receipt(base, row) is not None for row in records),
        "retries": sum(row.get("status") == "failed" for row in records),
        "dead_letters": sum(row.get("status") == "dead-letter" for row in records),
        "transport_evidence": sum(valid_receipt(base, row) is not None for row in records),
        "existing_delivery_records": len(records), "duplicate_pairs": len(pairs) - len(set(pairs)),
    }
    event = dict(snapshot)
    event["id"] = stable_id("notification-recovery-event", project, goal_id,
                            prior_sequence + 1)
    event["ts"] = snapshot["observed_at"]
    commit_json_projection(base, path, snapshot, event,
                           "state/notification-recovery-events.jsonl")


def require_actuator() -> None:
    if os.environ.get("RECURSION_QUEUE_ACTUATION") != "1":
        raise OutboxError("Phase 7 mutation is permitted only inside the existing queue actuator")


def decision_key(*parts: object) -> str:
    return "phase7:" + hashlib.sha256(json.dumps(parts, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def retry_key_parts(base: Path, verb: str, key_parts: list[object]) -> list[object]:
    """Derive a bounded retry identity from the canonical terminal action chain."""
    maximum = int(os.environ.get("RECURSION_NOTIFICATION_ACTION_MAX_ATTEMPTS", "3"))
    if not 1 <= maximum <= 10:
        raise OutboxError("notification action attempt budget must be 1..10")
    original = list(key_parts)
    candidate = list(original)
    for attempt_number in range(1, maximum + 1):
        key = decision_key(verb, *candidate)
        action_id = "action-" + hashlib.sha256(key.encode()).hexdigest()[:24]
        path = base / "state/actions" / f"{action_id}.json"
        if not path.is_file():
            return candidate
        record = read_json(path)
        if record.get("id") != action_id or record.get("idempotency_key") != key:
            raise OutboxError(f"notification action identity is inconsistent: {action_id}")
        if record.get("status") != "failed":
            return candidate
        if attempt_number >= maximum:
            # Reuse the final failed identity so decision-queue deduplication enforces the bound.
            return candidate
        try:
            attempts = int(record.get("attempts") or 0)
        except (TypeError, ValueError) as exc:
            raise OutboxError(f"notification action attempts are invalid: {action_id}") from exc
        failure_nonce = stable_id(
            "notification-action-failure", action_id, record["status"], attempts,
            record.get("result_evidence"),
        )
        candidate = [*original, "failed-attempt", attempt_number, failure_nonce]
    return candidate


def enqueue(base: Path, actor: str, verb: str, args: list[str], goal_id: str,
            reason: str, key_parts: list[object]) -> None:
    raw = {
        "actor": actor, "verb": verb, "args": args, "project": args[0], "goal": goal_id,
        "why": reason, "wrong_if": "canonical event, policy, delivery, receipt, or report state changes",
        "idempotency_key": decision_key(verb, *key_parts),
        "decision_source": "notification-reconciler", "routed_decider": actor,
    }
    process = subprocess.run(
        [sys.executable, str(base / "scripts/decision-queue.py"), "enqueue"],
        input=json.dumps(raw), text=True, capture_output=True, cwd=base,
        env={**os.environ, "RECURSION_ROOT": str(base)}, check=False,
    )
    if process.returncode:
        raise OutboxError((process.stderr or process.stdout or "decision enqueue failed").strip())


def state_digest(base: Path, project: str, goal_id: str) -> str:
    digest = hashlib.sha256()
    paths = []
    for directory in ("state/notification-events", "state/deliveries", "state/transport-evidence", "state/reports"):
        for path in sorted((base / directory).glob("*.json")):
            # The audit report is the derived output of this fingerprint. Hashing it would make
            # each successful audit manufacture a new idempotency key for another audit forever.
            if directory == "state/reports" and path.name == f"{goal_id}-audit.json":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if project in text and (not goal_id or goal_id in text):
                paths.append(path)
    for path in paths:
        digest.update(str(path.relative_to(base)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def recovery_needed(base: Path, project: str, goal_id: str) -> bool:
    events = [value for _, value in notification_events(base, project)
              if not goal_id or value.get("goal_id") == goal_id]
    records = [value for _, value in delivery_records(base, project)
               if not goal_id or value.get("goal_id") == goal_id]
    pairs = [(row.get("event_id"), row.get("destination")) for row in records]
    if len(pairs) != len(set(pairs)):
        return True
    for event in events:
        if event.get("routing_error"):
            continue
        try:
            destinations = policy_destinations(base, project, str(event.get("event_type") or ""))
        except Exception:
            continue
        if any(not existing_pair(base, str(event["id"]), destination) for destination in destinations):
            return True
    return any(
        (row.get("status") == "running" and valid_receipt(base, row)) or
        (row.get("status") == "succeeded" and not valid_receipt(base, row))
        for row in records
    )


def schedule(base: Path, project: str | None) -> int:
    if (base / "state/PAUSE").exists():
        print(0)
        return 0
    projects = [project] if project else sorted(path.stem for path in (base / "state/project-config").glob("*.json"))
    count = 0
    for project_id in projects:
        try:
            _, pilot, _ = configured(base, project_id)
        except Exception:
            continue
        actor = str(pilot["id"])
        for event in all_mapped(base, project_id):
            if event_reconciliation_needed(base, event):
                retry_parts = retry_key_parts(
                    base, "notification-reconcile", [project_id, event["id"]],
                )
                enqueue(base, actor, "notification-reconcile", [project_id, event["id"]],
                        event.get("goal_id") or f"goal-{project_id}", "reconcile append-only event into outbox",
                        retry_parts)
                count += 1
        for _, record in delivery_records(base, project_id):
            status = record.get("status")
            due = int(record.get("next_attempt_at") or 0)
            receipt = valid_receipt(base, record) if status == "running" else None
            if (status in {"pending", "failed"} and due <= now_epoch()) or status == "running":
                enqueue(base, actor, "notification-deliver", [project_id, str(record["id"])],
                        str(record.get("goal_id") or f"goal-{project_id}"), "advance one durable delivery",
                        [record["id"], status, record.get("attempt"), record.get("next_attempt_at"),
                         bool(receipt)])
                count += 1
            elif status == "dead-letter" and dead_letter_reconciliation_needed(base, record):
                retry_parts = retry_key_parts(
                    base, "notification-deliver",
                    [record["id"], status, record.get("attempt"), "repair"],
                )
                enqueue(base, actor, "notification-deliver", [project_id, str(record["id"])],
                        str(record.get("goal_id") or f"goal-{project_id}"),
                        "repair durable dead-letter escalation and attention event", retry_parts)
                count += 1
        terminal_goals: set[str] = set()
        for _, event in notification_events(base, project_id):
            goal_id = str(event.get("goal_id") or "")
            if event.get("event_type") in TERMINAL_EVENT_TYPES and IDENT.fullmatch(goal_id):
                terminal_goals.add(goal_id)
        for goal_id in sorted(terminal_goals):
            pilot_id = stable_id("event", goal_id, "pilot-terminal-report")
            portfolio_id = stable_id("event", goal_id, "portfolio-result")
            pilot_deliveries = [row for _, row in delivery_records(base, project_id)
                                if row.get("event_id") == pilot_id]
            pilot_acked = len(pilot_deliveries) == 1 and pilot_deliveries[0].get("status") == "succeeded" and bool(valid_receipt(base, pilot_deliveries[0]))
            if pilot_acked and not (base / "state/notification-events" / f"{portfolio_id}.json").is_file():
                retry_parts = retry_key_parts(
                    base, "notification-portfolio", [project_id, goal_id, pilot_id],
                )
                enqueue(base, "head-hermes", "notification-portfolio", [project_id, goal_id], goal_id,
                        "emit one portfolio result after acknowledged pilot evidence", retry_parts)
                count += 1
            fingerprint = state_digest(base, project_id, goal_id)
            if recovery_needed(base, project_id, goal_id):
                enqueue(base, actor, "notification-recover", [project_id, goal_id], goal_id,
                        "reconcile notification runtime truth", [project_id, goal_id, fingerprint])
                count += 1
            if (base / "state/reports" / f"{goal_id}-head.json").is_file():
                enqueue(base, actor, "notification-audit", [project_id, goal_id], goal_id,
                        "refresh terminal correlated audit chain", [project_id, goal_id, fingerprint, "audit"])
                count += 1
        # Non-terminal delivery state still receives a recovery projection.
        if not terminal_goals and (notification_events(base, project_id) or delivery_records(base, project_id)):
            goal_ids = sorted({
                str(row.get("goal_id") or "")
                for collection in (notification_events(base, project_id), delivery_records(base, project_id))
                for _, row in collection
                if IDENT.fullmatch(str(row.get("goal_id") or ""))
            })
            for goal_id in goal_ids:
                if recovery_needed(base, project_id, goal_id):
                    fingerprint = state_digest(base, project_id, goal_id)
                    enqueue(base, actor, "notification-recover", [project_id, goal_id], goal_id,
                            "reconcile notification runtime truth", [project_id, goal_id, fingerprint])
                    count += 1
    print(count)
    return 0


def status(base: Path, project: str) -> None:
    records = [row for _, row in delivery_records(base, project)]
    counts: dict[str, int] = {}
    for row in records:
        counts[str(row.get("status") or "unknown")] = counts.get(str(row.get("status") or "unknown"), 0) + 1
    print(json.dumps({"project": project, "paused": (base / "state/PAUSE").exists(),
                      "events": len(notification_events(base, project)), "deliveries": counts}, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    schedule_parser = sub.add_parser("schedule")
    schedule_parser.add_argument("--project")
    status_parser = sub.add_parser("status")
    status_parser.add_argument("project")
    for name, second in (
        ("reconcile-event", "event"), ("deliver", "delivery"),
        ("portfolio-report", "goal"), ("audit", "goal"), ("recover", "goal"),
    ):
        command = sub.add_parser(name)
        command.add_argument("project")
        command.add_argument(second)
    args = parser.parse_args()
    base = base_root()
    try:
        if args.command == "schedule":
            return schedule(base, args.project)
        if args.command == "status":
            status(base, args.project)
        elif args.command == "reconcile-event":
            reconcile_event(base, args.project, args.event)
        elif args.command == "deliver":
            deliver(base, args.project, args.delivery)
        elif args.command == "portfolio-report":
            portfolio_report(base, args.project, args.goal)
        elif args.command == "audit":
            audit_goal(base, args.project, args.goal)
        else:
            recover(base, args.project, args.goal)
    except (OSError, ValueError, json.JSONDecodeError, OutboxError) as exc:
        print(f"notification-outbox: {exc}", file=sys.stderr)
        return 75 if "PAUSE" in str(exc) else 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

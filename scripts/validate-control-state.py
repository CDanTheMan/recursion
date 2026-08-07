#!/usr/bin/env python3
"""Validate Recursion control-plane JSON objects against the v1 invariants.

The repository keeps its proven Markdown/TSV projections. This validator is the schema boundary
for new durable queue objects and for adapters that project those files into typed records.
It intentionally has no third-party dependency so recovery still fails closed in a bare venv.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
STATUSES = {
    "project": {"pending", "active", "paused", "retired"},
    "pilot": {"pending", "active", "paused", "retired"},
    "goal": {"draft", "approved", "active", "verifying", "achieved", "blocked", "abandoned"},
    "task": {"proposed", "ready", "queued", "leased", "running", "verifying", "passed", "failed", "blocked", "stale", "cancelled", "moot", "resolved", "escalated"},
    "run": {"pending", "running", "succeeded", "failed", "blocked", "cancelled", "stale"},
    "decision": {"proposed", "accepted", "queued", "executed", "refused", "cancelled"},
    "escalation": {"open", "resolved", "cancelled"},
    "delivery": {"pending", "running", "succeeded", "failed", "cancelled", "dead-letter"},
    "instruction": {"open", "consumed", "acknowledged", "cancelled"},
    "action": {"pending", "running", "succeeded", "failed", "cancelled"},
}
REQUIRED = {
    "project": ("schema_version", "id", "repo", "default_branch", "deploy_key_ref", "charter", "topic", "pilot_id", "status"),
    "pilot": ("schema_version", "id", "project_id", "charter", "model_policy", "status"),
    "goal": ("schema_version", "id", "project_id", "outcome", "acceptance_suite", "falsifier", "budget", "status"),
    "task": ("schema_version", "id", "goal_id", "dependencies", "allowed_paths", "non_goals", "worker_class", "acceptance", "status"),
    "run": ("schema_version", "id", "task_id", "worker", "worktree", "base_commit", "pid", "lease_expires", "deadline", "usage", "result", "status"),
    "decision": ("schema_version", "id", "actor", "verb", "arguments", "reason", "goal_id", "idempotency_key", "status"),
    "escalation": ("schema_version", "id", "goal_id", "required_actor", "question", "evidence", "status"),
    "delivery": ("schema_version", "id", "event_id", "destination", "attempt", "acknowledgement", "status"),
    "instruction": ("schema_version", "id", "principal", "topic", "project_id", "deduplication_key", "status", "action_ids"),
    "action": ("schema_version", "id", "idempotency_key", "verb", "arguments", "goal_id", "status", "lease_expires", "attempts", "result_evidence"),
}


def fail(message: str) -> None:
    raise ValueError(message)


def require_identifier(value: object, field: str) -> None:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        fail(f"{field} is not a canonical identifier")


def validate(kind: str, value: object) -> dict:
    if kind not in REQUIRED:
        fail(f"unknown object type: {kind}")
    if not isinstance(value, dict):
        fail("record must be a JSON object")
    missing = [field for field in REQUIRED[kind] if field not in value]
    if missing:
        fail("missing required field(s): " + ", ".join(missing))
    if value.get("schema_version") != 1:
        fail("schema_version must be 1")
    require_identifier(value.get("id"), "id")
    if value.get("status") not in STATUSES[kind]:
        fail(f"invalid {kind} status: {value.get('status')!r}")

    non_empty = {
        "decision": ("actor", "reason", "goal_id", "idempotency_key"),
        "instruction": ("principal", "deduplication_key"),
    }
    for field in non_empty.get(kind, ()):
        if not isinstance(value.get(field), str) or not value[field].strip():
            fail(f"{field} must be a non-empty string")

    for field in ("project_id", "pilot_id", "goal_id", "task_id", "event_id", "verb"):
        if field in value and value[field] is not None:
            require_identifier(value[field], field)
    for field in ("dependencies", "action_ids"):
        if field in value:
            items = value[field]
            if not isinstance(items, list) or len(items) != len(set(items)):
                fail(f"{field} must be a unique array")
            for item in items:
                require_identifier(item, field)
    for field in ("arguments", "allowed_paths", "non_goals", "notification_targets"):
        if field in value and not isinstance(value[field], list):
            fail(f"{field} must be an array")
    if "concurrency_limit" in value and (
        not isinstance(value["concurrency_limit"], int) or value["concurrency_limit"] < 0
    ):
        fail("concurrency_limit must be a non-negative integer")
    if "budget" in value and kind == "pilot" and not isinstance(value["budget"], dict):
        fail("pilot budget must be an object")
    if "idempotency_key" in value:
        key = value["idempotency_key"]
        if not isinstance(key, str) or not key or len(key) > 256:
            fail("idempotency_key must contain 1..256 characters")
    if kind in {"action", "delivery"}:
        numeric = "attempts" if kind == "action" else "attempt"
        if not isinstance(value[numeric], int) or value[numeric] < 0:
            fail(f"{numeric} must be a non-negative integer")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=sorted(REQUIRED))
    parser.add_argument("path", nargs="?", help="JSON file; omit to read stdin")
    args = parser.parse_args()
    try:
        if args.path:
            record = json.loads(Path(args.path).read_text(encoding="utf-8"))
        else:
            record = json.load(sys.stdin)
        validate(args.kind, record)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERR {exc}", file=sys.stderr)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

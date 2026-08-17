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
    "plan": {"proposed", "approved", "rejected"},
    "goal": {"draft", "approved", "active", "verifying", "achieved", "blocked", "abandoned", "budget-exhausted", "paused"},
    "task": {"proposed", "ready", "queued", "leased", "running", "verifying", "passed", "failed", "blocked", "stale", "cancelled", "moot", "resolved", "escalated"},
    "run": {"pending", "running", "succeeded", "failed", "blocked", "cancelled", "stale"},
    "decision": {"proposed", "accepted", "queued", "executed", "refused", "cancelled"},
    "escalation": {"open", "resolved", "cancelled"},
    "delivery": {"pending", "running", "succeeded", "failed", "cancelled", "dead-letter"},
    "notification_event": {"recorded"},
    "instruction": {"open", "consumed", "acknowledged", "cancelled"},
    "action": {"pending", "running", "succeeded", "failed", "cancelled"},
}
DECISION_SOURCES = frozenset(
    {"hermes-model", "project-reconciler", "notification-reconciler", "routing-reconciler",
     "instruction-reconciler"}
)
REQUIRED = {
    "project": ("schema_version", "id", "repo", "default_branch", "deploy_key_ref", "charter", "topic", "pilot_id", "status"),
    "pilot": ("schema_version", "id", "project_id", "charter", "model_policy", "status"),
    "plan": ("schema_version", "id", "project_id", "pilot_id", "instruction_id", "plan_digest", "plan", "status"),
    "goal": ("schema_version", "id", "project_id", "outcome", "acceptance_suite", "falsifier", "budget", "status"),
    "task": ("schema_version", "id", "goal_id", "dependencies", "allowed_paths", "non_goals", "worker_class", "acceptance", "status"),
    "run": ("schema_version", "id", "task_id", "worker", "worktree", "base_commit", "pid", "lease_expires", "deadline", "usage", "result", "status"),
    "decision": ("schema_version", "id", "actor", "verb", "arguments", "reason", "goal_id", "idempotency_key", "status", "decision_source"),
    "escalation": ("schema_version", "id", "goal_id", "required_actor", "question", "evidence", "status"),
    "delivery": ("schema_version", "id", "event_id", "destination", "attempt", "acknowledgement", "status"),
    "notification_event": ("schema_version", "id", "source_event_id", "event_type", "project_id", "goal_id", "message", "message_digest", "status"),
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
        "decision": ("actor", "reason", "goal_id", "idempotency_key", "decision_source"),
        "instruction": ("principal", "deduplication_key"),
    }
    # Provenance binds a decision to an authority. conduct-hermes refuses any decision whose
    # decision_source is not one of these, so accepting a record here that can never actuate
    # only defers the failure to a point where it is invisible. Keep this set identical to
    # the provenance case arms in scripts/conduct-hermes.sh.
    if kind == "decision" and value.get("decision_source") not in DECISION_SOURCES:
        fail(f"invalid decision provenance: {value.get('decision_source')!r}")
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
    for field in ("arguments", "allowed_paths", "non_goals", "required_non_goals", "notification_targets"):
        if field in value and not isinstance(value[field], list):
            fail(f"{field} must be an array")
    if "concurrency_limit" in value and (
        not isinstance(value["concurrency_limit"], int) or value["concurrency_limit"] < 0
    ):
        fail("concurrency_limit must be a non-negative integer")
    if kind == "plan":
        if not isinstance(value.get("plan"), dict) or not re.fullmatch(r"[0-9a-f]{64}", str(value.get("plan_digest") or "")):
            fail("plan payload or digest is malformed")
    if "budget" in value and kind == "pilot" and not isinstance(value["budget"], dict):
        fail("pilot budget must be an object")
    # Empty Phase 2 goal-budget objects remain a valid pre-Phase-6 projection. A goal is not
    # autonomously schedulable until project-reconcile.parse_budget sees the complete policy.
    if kind == "goal" and isinstance(value.get("budget"), dict) and value["budget"]:
        required_budget = {
            "max_concurrency", "max_tokens", "max_cost_usd", "max_wall_clock_seconds",
            "max_task_attempts", "max_failures", "max_review_queue", "max_publish_attempts",
            "publication_required",
        }
        missing_budget = sorted(required_budget - value["budget"].keys())
        if missing_budget:
            fail("Phase 6 goal budget is missing: " + ", ".join(missing_budget))
        for field in required_budget - {"max_cost_usd", "publication_required"}:
            if isinstance(value["budget"][field], bool) or not isinstance(value["budget"][field], int) \
               or value["budget"][field] < 0:
                fail(f"invalid Phase 6 goal budget field: {field}")
        cost = value["budget"]["max_cost_usd"]
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0:
            fail("invalid Phase 6 goal budget field: max_cost_usd")
        if not isinstance(value["budget"]["publication_required"], bool):
            fail("invalid Phase 6 goal budget field: publication_required")
    if kind == "task" and value.get("evidence_contract") == "worker-result-v1":
        phase5 = (
            "model_alias", "verifier_model_alias", "deadline_seconds",
            "verifier_deadline_seconds", "network_policy", "verification",
            "expected_change", "gate_files",
        )
        missing_phase5 = [field for field in phase5 if field not in value]
        if missing_phase5:
            fail("Phase 5 task is missing: " + ", ".join(missing_phase5))
        if value["model_alias"] not in {"sonnet-routine", "opus-complex"}:
            fail("invalid implementer model alias")
        if value["verifier_model_alias"] not in {"opus-review", "opus-complex"}:
            fail("invalid verifier model alias")
        if value["model_alias"] == value["verifier_model_alias"]:
            fail("implementer and verifier aliases must be independent")
        if value["network_policy"] not in {"provider-only", "none"}:
            fail("invalid network policy")
        if value["verification"] != "independent":
            fail("generated work requires independent verification")
        if value["expected_change"] not in {"required", "optional"}:
            fail("invalid expected_change policy")
        # Historical Phase 5 task projections predate gate_class/gate_contract. New Phase 8
        # plans require and materialize them, but this generic reader must still admit durable
        # v1 evidence written before that hardening deployment.
        if "gate_class" in value and value["gate_class"] not in {"light", "heavy"}:
            fail("invalid gate_class policy")
        if not isinstance(value["gate_files"], list) \
                or len(value["gate_files"]) != len(set(value["gate_files"])):
            fail("gate_files must be a unique array")
        if "gate_contract" in value:
            contract = value["gate_contract"]
            hashes = contract.get("gate_files") if isinstance(contract, dict) else None
            controller_hashes = contract.get("controller_gate_files", {}) if isinstance(contract, dict) else None
            if not isinstance(contract, dict) \
                    or not re.fullmatch(r"[0-9a-f]{64}", str(contract.get("acceptance_sha256") or "")) \
                    or not isinstance(hashes, dict) or set(hashes) != set(value["gate_files"]) \
                    or not isinstance(controller_hashes, dict) \
                    or set(controller_hashes) != set(value.get("controller_gate_files") or []) \
                    or any(not re.fullmatch(r"[0-9a-f]{64}", str(digest))
                           for digest in [*hashes.values(), *controller_hashes.values()]):
                fail("gate_contract must contain acceptance and tracked-file hashes")
        for field in ("deadline_seconds", "verifier_deadline_seconds"):
            if not isinstance(value[field], int) or value[field] < 1:
                fail(f"{field} must be a positive integer")
        if str(value.get("acceptance", "")).strip() in {"", "true", ":", "/bin/true", "exit 0"}:
            fail("acceptance gate is structurally vacuous")
    if kind == "run":
        if "process_group" in value and (not isinstance(value["process_group"], int) or value["process_group"] < 1):
            fail("process_group must be a positive integer")
        if "role" in value and value["role"] not in {"implementer", "verifier"}:
            fail("invalid worker role")
    if "idempotency_key" in value:
        key = value["idempotency_key"]
        if not isinstance(key, str) or not key or len(key) > 256:
            fail("idempotency_key must contain 1..256 characters")
    if "decision_payload_sha256" in value and not re.fullmatch(
        r"[0-9a-f]{64}", str(value["decision_payload_sha256"])
    ):
        fail("decision_payload_sha256 must be sha256")
    if "action_payload_sha256" in value and not re.fullmatch(
        r"[0-9a-f]{64}", str(value["action_payload_sha256"])
    ):
        fail("action_payload_sha256 must be sha256")
    if kind in {"action", "delivery"}:
        numeric = "attempts" if kind == "action" else "attempt"
        if not isinstance(value[numeric], int) or value[numeric] < 0:
            fail(f"{numeric} must be a non-negative integer")
    if kind == "delivery":
        if "max_attempts" in value and (not isinstance(value["max_attempts"], int) or value["max_attempts"] < 1):
            fail("max_attempts must be a positive integer")
        if "message_digest" in value and not re.fullmatch(r"[0-9a-f]{64}", str(value["message_digest"])):
            fail("delivery message_digest must be sha256")
    if kind == "notification_event":
        if value["event_type"] not in {
            "goal-accepted", "plan-approved", "worker-launched", "task-passed", "task-failed",
            "task-blocked", "human-answer-received", "review-branch-published", "goal-verifying",
            "goal-achieved", "goal-stopped", "pilot-terminal-report", "portfolio-result",
            "lucas-attention-required", "delivery-dead-letter", "plan-proposed",
            "pilot-window-armed", "pilot-window-opened", "pilot-window-closed",
            "portfolio-brief", "project-digest",
        }:
            fail("unknown notification event type")
        if not re.fullmatch(r"[0-9a-f]{64}", str(value["message_digest"])):
            fail("notification message_digest must be sha256")
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

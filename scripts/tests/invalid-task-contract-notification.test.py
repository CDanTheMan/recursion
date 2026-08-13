#!/usr/bin/env python3
"""Focused Phase-7 projection controls for controller pre-worker rejection."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


phase7 = load(SOURCE / "scripts/tests/hermes-pilot-phase7-red.py", "phase7_fixture")


def prepare(fixture, *, attempts: int = 0) -> dict:
    transition_id = "transition-" + "c" * 32
    (fixture.root / "state/tasks/task-alpha.md").write_text(
        "schema_version: 1\nversion: 4\nid: task-alpha\nproject_id: alpha\n"
        "pilot_id: pilot-alpha\ngoal_id: goal-alpha\ndependencies:\nallowed_paths: app\n"
        "acceptance: true\nstatus: blocked\n"
        f"attempts: {attempts}\n"
        "lease_expires: 0\ntransition_reason: task-contract-invalid\n"
        "blocker_actor: controller\nblocked_on: invalid-acceptance-gate\n"
        "contract_rejection_event_id: source-contract-invalid\n"
        f"last_transition_id: {transition_id}\n",
        encoding="utf-8",
    )
    (fixture.root / "state/goals/goal-alpha.md").write_text(
        "schema_version: 1\nversion: 5\nid: goal-alpha\nproject_id: alpha\n"
        "pilot_id: pilot-alpha\ninstruction_id: 00000001\nplan_id: plan-alpha\n"
        "acceptance_suite: bash -n app/main.sh\nstatus: blocked\nterminal_reported: 1\n"
        "last_transition_reason: task-contract-invalid\nlast_transition_from: active\n"
        "last_transition_task: task-alpha\n"
        f"last_transition_id: {transition_id}\n",
        encoding="utf-8",
    )
    for directory in ("state/runs", "state/evidence"):
        for path in (fixture.root / directory).glob("*.json"):
            path.unlink()
    fixture.write_json("state/actions/action-contract-work.json", {
        "schema_version": 1, "id": "action-contract-work", "decision_id": "decision-contract-work",
        "instruction_id": None, "idempotency_key": "fixture:contract-work", "verb": "work",
        "arguments": ["task-alpha"], "goal_id": "goal-alpha", "status": "failed",
        "lease_expires": None, "attempts": 1, "result_evidence": "log=fixture rc=78",
    })
    raw = {
        "schema_version": 1, "id": "source-contract-invalid", "ts": "2026-08-07T19:00:00Z",
        "event": "task-contract-invalid", "project": "alpha", "goal": "goal-alpha",
        "task": "task-alpha", "pid": 1, "transition_id": transition_id,
        "detail": {"attempts": 0, "reason": "invalid-acceptance-gate",
                   "stage": "controller-pre-worker"},
    }
    with (fixture.root / "state/events.jsonl").open("a", encoding="utf-8") as output:
        output.write(json.dumps(raw, sort_keys=True) + "\n")
    return raw


def reconcile_source(fixture) -> object:
    outbox = load(fixture.root / "scripts/notification-outbox.py",
                  "contract_notification_outbox_" + fixture.temp.name.replace("-", "_"))
    prior_root = os.environ.get("RECURSION_ROOT")
    prior_actuation = os.environ.get("RECURSION_QUEUE_ACTUATION")
    os.environ["RECURSION_ROOT"] = str(fixture.root)
    os.environ["RECURSION_QUEUE_ACTUATION"] = "1"
    try:
        events = [event for event in outbox.all_mapped(fixture.root, "alpha")
                  if event.get("source_event_id") == "source-contract-invalid"]
        assert [event["event_type"] for event in events] == ["task-blocked", "goal-stopped"]
        for event in events:
            outbox.reconcile_event(fixture.root, "alpha", event["id"])
        for event in events:  # exact replay
            outbox.reconcile_event(fixture.root, "alpha", event["id"])
        return outbox
    finally:
        if prior_root is None:
            os.environ.pop("RECURSION_ROOT", None)
        else:
            os.environ["RECURSION_ROOT"] = prior_root
        if prior_actuation is None:
            os.environ.pop("RECURSION_QUEUE_ACTUATION", None)
        else:
            os.environ["RECURSION_QUEUE_ACTUATION"] = prior_actuation


def main() -> int:
    lawful = phase7.Fixture("contract-lawful")
    adversarial = phase7.Fixture("contract-adversarial")
    try:
        prepare(lawful)
        outbox = reconcile_source(lawful)
        types = [row.get("event_type") for row in lawful.events()]
        report_path = lawful.root / "state/reports/goal-alpha-pilot.json"
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
        evidence = report.get("evidence", {})
        assert types.count("task-blocked") == 1
        assert types.count("goal-stopped") == 1
        assert types.count("lucas-attention-required") == 1
        assert types.count("pilot-terminal-report") == 1
        assert len(phase7.event_deliveries(lawful, "task-blocked")) == 1
        assert len(phase7.event_deliveries(lawful, "goal-stopped")) == 1
        assert len(phase7.event_deliveries(lawful, "lucas-attention-required")) == 1
        assert evidence.get("workers") == [] and evidence.get("commits") == []
        assert evidence.get("gates") == [] and evidence.get("verifier") == []
        assert len(evidence.get("controller_rejections", [])) == 1
        assert outbox.build_chain(lawful.root, "alpha", "goal-alpha")["_controller_rejection_complete"]
        print("ok    lawful pre-worker rejection reports exactly once without execution evidence")

        prepare(adversarial, attempts=1)
        adversarial_outbox = reconcile_source(adversarial)
        assert not adversarial_outbox.build_chain(
            adversarial.root, "alpha", "goal-alpha")["_controller_rejection_complete"]
        assert not (adversarial.root / "state/reports/goal-alpha-pilot.json").exists()
        escalation = adversarial.root / "state/escalations.tsv"
        assert escalation.exists() and escalation.read_text(encoding="utf-8").count(
            "terminal-trace:goal-alpha") == 1
        print("ok    attempted worker evidence invalidates controller-rejection terminal reporting")
    finally:
        lawful.close()
        adversarial.close()
    print("invalid-task-contract-notification: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

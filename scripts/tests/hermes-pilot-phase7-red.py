#!/usr/bin/env python3
"""Phase 7 red-to-green controls.

Every delivery uses the fixture transport written by this test. No test process can reach
Hermes or Telegram. The controls intentionally fail as a group before Phase 7 exists.
"""

from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
OUTBOX = SOURCE / "scripts/notification-outbox.py"
CONTROLS = [
    "simulated Telegram failure eventually delivers exactly once",
    "repeated delivery ticks produce no duplicate human-visible report",
    "retry state is independent for every destination",
    "backoff is bounded and retry-budget exhaustion is terminal",
    "transport acknowledgement survives a process crash and fresh host process",
    "permanent delivery failure creates one dead-letter escalation",
    "PAUSE blocks human-visible sends while pending work and status remain visible",
    "malformed, missing, unknown, and unconfigured destinations fail closed",
    "project-detail events reach only the configured project topic",
    "portfolio summaries reach only Head Hermes and configured portfolio destinations",
    "Lucas direct routing occurs only for an event policy that explicitly requires it",
    "one terminal project-pilot report produces exactly one Head Hermes portfolio result",
    "terminal goals retain a complete instruction-to-delivery audit chain",
    "recovery reconciles events, outbox, acknowledgements, retries, dead letters, and delivery records",
    "a process saying sent without transport evidence cannot acknowledge delivery",
    "ticks after complete acknowledgement cause zero new sends",
]


class Fixture:
    def __init__(self, name: str):
        self.temp = Path(tempfile.mkdtemp(prefix=f"phase7-{name}-"))
        self.root = self.temp / "root"
        self.root.mkdir()
        shutil.copytree(SOURCE / "scripts", self.root / "scripts")
        shutil.copytree(SOURCE / "schemas", self.root / "schemas")
        for relative in (
            "state/project-config", "state/pilots", "state/goals", "state/tasks",
            "state/instructions", "state/actions", "state/pilot-requests/alpha",
            "state/runs", "state/evidence", "state/deliveries", "state/notification-events",
            "state/transport-evidence", "state/reports", "state/recovery", "state/.locks",
            "state/decision-queue", "loop/logs", "bin",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        (self.root / ".env").write_text("", encoding="utf-8")
        self.project_topic = "project-topic:telegram:-100100:11"
        self.head = "head-hermes:telegram:-100100:1"
        self.direct = "lucas-direct:telegram:8913126684"
        self.portfolio = "portfolio-channel:telegram:-100200:9"
        self.targets = [self.project_topic, self.head, self.direct, self.portfolio]
        self._write_project(self.targets)
        self._write_chain()
        self.stub_state = self.temp / "transport"
        self.stub_state.mkdir()
        (self.stub_state / "modes.json").write_text("{}\n", encoding="utf-8")
        self.transport = self.root / "bin/inert-telegram"
        self.transport.write_text(TRANSPORT_STUB, encoding="utf-8")
        self.transport.chmod(0o755)
        self.env = os.environ.copy()
        self.env.update({
            "RECURSION_ROOT": str(self.root),
            "RECURSION_NOTIFY_TRANSPORT": str(self.transport),
            "RECURSION_NOTIFY_STUB_STATE": str(self.stub_state),
            "RECURSION_NO_NOTIFY": "0",
            "RECURSION_DELIVERY_BACKOFF_BASE_S": "1",
            "RECURSION_DELIVERY_BACKOFF_MAX_S": "1",
            "RECURSION_DELIVERY_MAX_ATTEMPTS": "3",
            "RECURSION_LOCK_ATTEMPTS": "5",
            "RECURSION_LOCK_DELAY_S": "0.01",
        })

    def close(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def _write_project(self, targets: list[str]) -> None:
        cfg = {
            "schema_version": 1, "id": "alpha", "repo": str(self.root / "repo"),
            "remote": "origin", "default_branch": "main", "deploy_key_ref": "-",
            "charter": "Phase 7 inert reporting fixture.", "allowed_paths": ["app"],
            "topic": 11, "pilot_id": "pilot-alpha", "activation_gate": "fixture",
            "notification_targets": targets, "goal_source": "state/goals/goal-alpha.md",
            "status": "active",
        }
        pilot = {
            "schema_version": 1, "id": "pilot-alpha", "project_id": "alpha", "topic": 11,
            "charter": cfg["charter"], "model_policy": "project-pilot", "concurrency_limit": 1,
            "budget": {"max_inflight_workers": 1}, "notification_targets": targets,
            "goal_source": cfg["goal_source"], "memory_key": "fixture:11",
            "worktree_root": ".worktrees/alpha", "status": "active",
        }
        self.write_json("state/project-config/alpha.json", cfg)
        self.write_json("state/pilots/pilot-alpha.json", pilot)

    def set_targets(self, targets: list[str]) -> None:
        self.targets = targets
        self._write_project(targets)

    def _write_chain(self) -> None:
        (self.root / "state/goals/goal-alpha.md").write_text(
            "schema_version: 1\nversion: 4\nid: goal-alpha\nproject_id: alpha\n"
            "pilot_id: pilot-alpha\ninstruction_id: 00000001\nplan_id: plan-alpha\n"
            "acceptance_suite: bash -n app/main.sh\nstatus: verifying\nterminal_reported: 0\n",
            encoding="utf-8",
        )
        (self.root / "state/tasks/task-alpha.md").write_text(
            "schema_version: 1\nversion: 3\nid: task-alpha\nproject_id: alpha\n"
            "pilot_id: pilot-alpha\ngoal_id: goal-alpha\ndependencies:\nallowed_paths: app\n"
            "acceptance: bash -n app/main.sh\nstatus: passed\ncandidate_commit: " + "a" * 40 + "\n",
            encoding="utf-8",
        )
        (self.root / "state/instructions/00000001.md").write_text(
            "schema_version: 1\nid: 00000001\nprincipal: lucas\ntopic: 11\nproject_id: alpha\n"
            "pilot_id: pilot-alpha\ndeduplication_key: telegram:fixture:1\nstatus: acknowledged\n"
            "action_ids: action-instruction\n\nBuild the fixture.\n",
            encoding="utf-8",
        )
        self.write_json("state/actions/action-instruction.json", {
            "schema_version": 1, "id": "action-instruction", "decision_id": "decision-plan",
            "instruction_id": "00000001", "idempotency_key": "fixture:instruction",
            "verb": "pilot-plan-propose", "arguments": ["alpha", "goal-alpha"],
            "goal_id": "goal-alpha", "status": "succeeded", "lease_expires": None,
            "attempts": 1, "result_evidence": "plan accepted",
        })
        self.write_json("state/pilot-requests/alpha/plan-alpha.json", {
            "schema_version": 1, "id": "plan-alpha", "actor": "pilot-alpha",
            "project_id": "alpha", "goal_id": "goal-alpha", "verb": "pilot-plan-propose",
            "arguments": [], "text": "Implement one bounded fixture task.",
            "instruction_id": "00000001", "status": "requested",
        })
        implementer = {
            "schema_version": 1, "id": "run-implementer", "project_id": "alpha",
            "goal_id": "goal-alpha", "task_id": "task-alpha", "role": "implementer",
            "status": "succeeded", "pid": 101, "process_group": 101,
            "commit_oid": "a" * 40, "usage": {"tokens": 10, "cost_usd": 0},
            "machine_gate": {"passed": True, "exit_code": 0, "commit_oid": "a" * 40},
            "verification": {"verdict": "pass", "commit_oid": "a" * 40,
                             "verifier_run_id": "run-verifier"},
        }
        verifier = {
            "schema_version": 1, "id": "run-verifier", "project_id": "alpha",
            "goal_id": "goal-alpha", "task_id": "task-alpha", "role": "verifier",
            "status": "succeeded", "pid": 102, "process_group": 102,
            "commit_oid": "a" * 40, "usage": {"tokens": 5, "cost_usd": 0},
            "verification": {"verdict": "pass", "commit_oid": "a" * 40,
                             "implementer_run_id": "run-implementer"},
        }
        self.write_json("state/runs/run-implementer.json", implementer)
        self.write_json("state/runs/run-verifier.json", verifier)
        self.write_json("state/evidence/goal-alpha.json", {
            "schema_version": 1, "id": "goal-evidence-goal-alpha", "project_id": "alpha",
            "goal_id": "goal-alpha", "verdict": "pass", "commit_oid": "a" * 40,
            "implementer_run_id": "run-implementer", "verifier_run_id": "run-verifier",
            "machine_gate": implementer["machine_gate"],
            "independent_verifier": verifier["verification"],
        })

    def write_json(self, relative: str, value: dict) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")

    def append_event(self, event_id: str, event: str, *, detail=None, task="task-alpha") -> None:
        value = {
            "schema_version": 1, "id": event_id, "ts": "2026-08-07T19:00:00Z",
            "event": event, "project": "alpha", "goal": "goal-alpha", "task": task,
            "pid": 1, "detail": detail if detail is not None else "fixture",
        }
        with (self.root / "state/events.jsonl").open("a", encoding="utf-8") as output:
            output.write(json.dumps(value, sort_keys=True) + "\n")

    def set_modes(self, modes: dict[str, str]) -> None:
        (self.stub_state / "modes.json").write_text(json.dumps(modes) + "\n", encoding="utf-8")

    def run(self, command: list[str], *, env: dict[str, str] | None = None, check=False):
        active = self.env.copy()
        if env:
            active.update(env)
        return subprocess.run(command, cwd=self.root, env=active, text=True,
                              capture_output=True, check=check)

    def ticks(self, count=1, *, env=None) -> None:
        for _ in range(count):
            self.run(["python3", "scripts/notification-outbox.py", "schedule", "--project", "alpha"], env=env)
            self.run(["bash", "scripts/conduct-hermes.sh"], env=env)

    def deliveries(self) -> list[dict]:
        result = []
        for path in sorted((self.root / "state/deliveries").glob("*.json")):
            try:
                result.append(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                pass
        return result

    def events(self) -> list[dict]:
        result = []
        for path in sorted((self.root / "state/notification-events").glob("*.json")):
            result.append(json.loads(path.read_text(encoding="utf-8")))
        return result

    def calls(self) -> list[dict]:
        path = self.stub_state / "calls.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []

    def visible(self) -> list[dict]:
        path = self.stub_state / "visible.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


TRANSPORT_STUB = r'''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
state=Path(os.environ["RECURSION_NOTIFY_STUB_STATE"])
destination,message,delivery,event=sys.argv[1:5]
modes=json.loads((state/"modes.json").read_text())
counts={}
for line in (state/"calls.jsonl").read_text().splitlines() if (state/"calls.jsonl").exists() else []:
    row=json.loads(line); counts[row["destination"]]=counts.get(row["destination"],0)+1
attempt=counts.get(destination,0)+1
with (state/"calls.jsonl").open("a") as out:
    out.write(json.dumps({"destination":destination,"delivery_id":delivery,"event_id":event,"attempt":attempt})+"\n")
mode=modes.get(destination,modes.get("*","success"))
if mode=="liar":
    print("sent"); raise SystemExit(0)
if mode=="permanent":
    print(json.dumps({"ok":False,"accepted":False,"retryable":False,"error":"permanent"})); raise SystemExit(0)
if mode=="always-fail" or (mode=="fail-once" and attempt==1):
    print(json.dumps({"ok":False,"accepted":False,"retryable":True,"error":"temporary"})); raise SystemExit(0)
parts=destination.split(":")
chat=parts[2]; thread=parts[3] if len(parts)>3 else None
row={"destination":destination,"delivery_id":delivery,"event_id":event,"attempt":attempt}
with (state/"visible.jsonl").open("a") as out: out.write(json.dumps(row)+"\n")
print(json.dumps({"ok":True,"accepted":True,"transport":"telegram","message_id":"stub-%s-%s"%(delivery,attempt),"chat_id":chat,"thread_id":thread}))
'''


def event_deliveries(fixture: Fixture, event_type: str) -> list[dict]:
    ids = {row["id"] for row in fixture.events() if row.get("event_type") == event_type}
    return [row for row in fixture.deliveries() if row.get("event_id") in ids]


def report(ok: bool, text: str, results: list[bool]) -> None:
    results.append(ok)
    print(("ok    " if ok else "FAIL  ") + text)


def main() -> int:
    if not OUTBOX.is_file():
        for text in CONTROLS:
            print("FAIL  " + text + " (Phase 7 outbox is absent)")
        print(f"\nhermes-pilot-phase7-red: {len(CONTROLS)} FAILED (expected on the pre-Phase 7 base)")
        return 1

    results: list[bool] = []
    fixtures: list[Fixture] = []
    try:
        # Retry, dedup, and post-ack closure.
        first = Fixture("retry"); fixtures.append(first)
        first.append_event("source-worker", "start", detail="owner=fixture attempt=1")
        first.set_modes({first.project_topic: "fail-once"})
        first.ticks(2)  # normalize, then first failed attempt
        time.sleep(1.05); first.ticks(1)
        topic = event_deliveries(first, "worker-launched")
        report(len(topic) == 1 and topic[0].get("status") == "succeeded" and
               topic[0].get("attempt") == 2 and len(first.visible()) == 1,
               CONTROLS[0], results)
        before = len(first.visible()); first.ticks(1)
        report(len(first.visible()) == before == 1, CONTROLS[1], results)

        # Terminal fan-out: Head delivery succeeds while an extra portfolio destination retries.
        terminal = Fixture("terminal"); fixtures.append(terminal)
        terminal.set_modes({terminal.portfolio: "fail-once"})
        terminal.append_event("source-review", "review-published",
                              detail={"branch": "loop/work/task-alpha", "commit": "a" * 40})
        terminal.append_event("source-terminal", "goal-transition",
                              detail={"from": "verifying", "to": "achieved", "reason": "verified", "version": 5}, task="")
        terminal.ticks(4); time.sleep(1.05); terminal.ticks(2)
        portfolio_deliveries = event_deliveries(terminal, "portfolio-result")
        by_destination = {row["destination"]: row for row in portfolio_deliveries}
        report(by_destination.get(terminal.head, {}).get("attempt") == 1 and
               by_destination.get(terminal.portfolio, {}).get("attempt") == 2 and
               all(row.get("status") == "succeeded" for row in portfolio_deliveries),
               CONTROLS[2], results)

        # Retry budget and permanent dead-letter escalation.
        exhausted = Fixture("exhausted"); fixtures.append(exhausted)
        exhausted.append_event("source-fail", "start")
        exhausted.set_modes({"*": "always-fail"})
        exhausted.ticks(2)
        for _ in range(2):
            time.sleep(1.05); exhausted.ticks(1)
        dead = event_deliveries(exhausted, "worker-launched")
        history = (exhausted.root / "state/delivery-events.jsonl").read_text(encoding="utf-8")
        report(len(dead) == 1 and dead[0].get("status") == "dead-letter" and
               dead[0].get("attempt") == 3 and '"backoff_seconds":1' in history and
               len(exhausted.calls()) == 3, CONTROLS[3], results)

        crash = Fixture("crash"); fixtures.append(crash)
        crash.append_event("source-crash", "start")
        crash.ticks(1)
        crash.ticks(1, env={"RECURSION_DELIVERY_CRASH_AFTER_RECEIPT": "1"})
        calls_after_crash = len(crash.calls())
        receipt_exists = any((crash.root / "state/transport-evidence").glob("*.json"))
        crash.ticks(1)
        crash_delivery = event_deliveries(crash, "worker-launched")
        report(receipt_exists and calls_after_crash == 1 and len(crash.calls()) == 1 and
               len(crash_delivery) == 1 and crash_delivery[0].get("status") == "succeeded" and
               crash_delivery[0].get("acknowledgement"), CONTROLS[4], results)

        permanent = Fixture("permanent"); fixtures.append(permanent)
        permanent.append_event("source-permanent", "start")
        permanent.set_modes({"*": "permanent"}); permanent.ticks(2)
        permanent_delivery = event_deliveries(permanent, "worker-launched")
        dead_letter_delivery = event_deliveries(permanent, "delivery-dead-letter")
        escalation = (permanent.root / "state/escalations.tsv")
        report(len(permanent_delivery) == 1 and permanent_delivery[0].get("status") == "dead-letter" and
               len(dead_letter_delivery) == 1 and dead_letter_delivery[0].get("status") == "pending" and
               dead_letter_delivery[0].get("destination") == permanent.direct and
               escalation.exists() and escalation.read_text(encoding="utf-8").count("delivery-dead-letter:") == 1,
               CONTROLS[5], results)

        paused = Fixture("paused"); fixtures.append(paused)
        paused.append_event("source-paused", "start"); paused.ticks(1)
        (paused.root / "state/PAUSE").write_text("fixture pause\n", encoding="utf-8")
        paused.ticks(1)
        status = paused.run(["python3", "scripts/notification-outbox.py", "status", "alpha"])
        pending_before = event_deliveries(paused, "worker-launched")
        stayed_pending = len(pending_before) == 1 and pending_before[0].get("status") == "pending"
        no_paused_send = not paused.calls()
        (paused.root / "state/PAUSE").unlink(); paused.ticks(1)
        report(stayed_pending and no_paused_send and "pending" in status.stdout and
               len(paused.visible()) == 1, CONTROLS[6], results)

        destination_failures = True
        bad_target_sets = [
            [],
            ["project-topic:telegram:not-a-chat:11"],
            ["mystery:telegram:-100100:11"],
            ["head-hermes:telegram:-100100:1"],
        ]
        for index, targets in enumerate(bad_target_sets):
            bad = Fixture(f"bad-{index}"); fixtures.append(bad); bad.set_targets(targets)
            bad.append_event(f"source-bad-{index}", "start"); bad.ticks(1)
            destination_failures &= not bad.calls() and not event_deliveries(bad, "worker-launched")
        # A syntactically valid destination not present in project configuration also fails closed.
        rogue = Fixture("rogue"); fixtures.append(rogue)
        rogue.append_event("source-rogue", "start"); rogue.ticks(1)
        rogue_event = next(row for row in rogue.events() if row["event_type"] == "worker-launched")
        rogue.write_json("state/deliveries/delivery-rogue.json", {
            "schema_version": 1, "id": "delivery-rogue", "event_id": rogue_event["id"],
            "project_id": "alpha", "goal_id": "goal-alpha", "task_id": "task-alpha",
            "destination": "project-topic:telegram:-999999:99", "attempt": 0,
            "acknowledgement": None, "status": "pending", "next_attempt_at": 0,
            "max_attempts": 3, "message_digest": rogue_event["message_digest"],
        })
        rogue.ticks(1)
        rogue_row = next(row for row in rogue.deliveries() if row["id"] == "delivery-rogue")
        destination_failures &= rogue_row.get("status") == "dead-letter" and all(
            call.get("destination") != "project-topic:telegram:-999999:99" for call in rogue.calls()
        )
        report(destination_failures, CONTROLS[7], results)

        project_only = all(row["destination"] == terminal.project_topic
                           for event_type in ("review-branch-published", "goal-achieved")
                           for row in event_deliveries(terminal, event_type))
        report(project_only and bool(event_deliveries(terminal, "goal-achieved")), CONTROLS[8], results)
        report(set(by_destination) == {terminal.head, terminal.portfolio}, CONTROLS[9], results)
        direct_types = {event["event_type"] for event in terminal.events()
                        if any(d["event_id"] == event["id"] and d["destination"] == terminal.direct
                               for d in terminal.deliveries())}
        attention = Fixture("attention"); fixtures.append(attention)
        attention.append_event("source-stopped", "goal-transition",
                               detail={"from": "active", "to": "blocked", "reason": "assist", "version": 5}, task="")
        attention.ticks(1)
        attention_deliveries = event_deliveries(attention, "lucas-attention-required")
        stopped_deliveries = event_deliveries(attention, "goal-stopped")
        report(direct_types == set() and len(attention_deliveries) == 1 and
               attention_deliveries[0]["destination"] == attention.direct and
               len(stopped_deliveries) == 1 and stopped_deliveries[0]["destination"] == attention.project_topic,
               CONTROLS[10], results)
        portfolio_events = [row for row in terminal.events() if row.get("event_type") == "portfolio-result"]
        pilot_events = [row for row in terminal.events() if row.get("event_type") == "pilot-terminal-report"]
        report(len(portfolio_events) == 1 and len(pilot_events) == 1 and
               len([d for d in portfolio_deliveries if d["destination"] == terminal.head]) == 1,
               CONTROLS[11], results)
        audit_path = terminal.root / "state/reports/goal-alpha-audit.json"
        audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else {}
        required = {"instruction", "plan", "actions", "tasks", "workers", "commits", "gates", "verifier",
                    "review_branch", "pilot_report", "head_report", "delivery_acknowledgements"}
        report(audit.get("complete") is True and required <= set(audit.get("chain", {})) and
               all(item.get("transport_message_id") for item in audit["chain"]["delivery_acknowledgements"]),
               CONTROLS[12], results)

        recovery = Fixture("recovery"); fixtures.append(recovery)
        recovery.append_event("source-recovery", "start"); recovery.ticks(1)
        normal = event_deliveries(recovery, "worker-launched")[0]
        source_event = next(row for row in recovery.events() if row["event_type"] == "worker-launched")
        missing_event = dict(source_event)
        missing_event.update({"id": "event-recovery-missing", "source_event_id": "source-recovery-missing",
                              "event_type": "task-blocked", "message": "Task blocked: recovery fixture"})
        missing_event["message_digest"] = hashlib.sha256(missing_event["message"].encode()).hexdigest()
        recovery.write_json("state/notification-events/event-recovery-missing.json", missing_event)
        (recovery.root / "state/deliveries" / f"{normal['id']}.json").unlink()
        recovery.write_json("state/deliveries/delivery-retry.json", {
            **normal, "id": "delivery-retry", "attempt": 1, "status": "failed",
            "acknowledgement": None, "next_attempt_at": int(time.time()) + 999,
        })
        recovery.write_json("state/deliveries/delivery-dead.json", {
            **normal, "id": "delivery-dead", "destination": recovery.head, "attempt": 3,
            "status": "dead-letter", "acknowledgement": None,
        })
        recovery.ticks(1)
        snapshot_paths = list((recovery.root / "state/recovery").glob("notification-*.json"))
        pairs = [(row.get("event_id"), row.get("destination")) for row in recovery.deliveries()]
        preserved = {row["id"]: row["status"] for row in recovery.deliveries()}
        report(bool(snapshot_paths) and len(pairs) == len(set(pairs)) and
               preserved.get("delivery-retry") == "failed" and preserved.get("delivery-dead") == "dead-letter" and
               any(row.get("event_id") == "event-recovery-missing" and
                   row.get("destination") == recovery.project_topic for row in recovery.deliveries()),
               CONTROLS[13], results)

        liar = Fixture("liar"); fixtures.append(liar)
        liar.append_event("source-liar", "start"); liar.set_modes({"*": "liar"}); liar.ticks(2)
        liar_delivery = event_deliveries(liar, "worker-launched")
        report(len(liar_delivery) == 1 and liar_delivery[0].get("status") != "succeeded" and
               not liar_delivery[0].get("acknowledgement") and
               not any((liar.root / "state/transport-evidence").glob("*.json")), CONTROLS[14], results)
        complete_calls = len(first.calls()); first.ticks(1)
        report(len(first.calls()) == complete_calls, CONTROLS[15], results)
    finally:
        for fixture in fixtures:
            fixture.close()

    failed = len([value for value in results if not value])
    if failed:
        print(f"\nhermes-pilot-phase7-red: {failed} FAILED")
        return 1
    print("\nhermes-pilot-phase7-red: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

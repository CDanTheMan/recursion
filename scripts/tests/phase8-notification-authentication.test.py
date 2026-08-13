#!/usr/bin/env python3
"""Receipt/authentication controls for Phase 8 human-visible projections.

Every Phase 8 projection (plan proposal/approval, pilot-window arm/open/close, task
start/finish/block, goal transitions and stopped/achieved notices, Lucas attention, and the
terminal report chain) must cross one durable-receipt gate before it can create a
notification.  A raw or forged JSONL row, a forged canonical object, a tampered or missing
receipt, a tampered or missing action, a replayed journal row, or a mid-projection crash must
all fail closed -- and the lawful receipt-backed chain must project each notice exactly once.

This suite mirrors the adversarial matrix in the notification-hardening specification.  It
builds canonical state through the real transition-receipt machinery (never by writing files
behind its back), so the canonical current-or-archived witness checks run against genuine
receipt evidence.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]


def load(path: Path, name: str):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


@contextmanager
def failpoint(name: str):
    prior = os.environ.get("RECURSION_TRANSITION_FAILPOINT")
    os.environ["RECURSION_TRANSITION_FAILPOINT"] = name
    try:
        yield
    finally:
        if prior is None:
            os.environ.pop("RECURSION_TRANSITION_FAILPOINT", None)
        else:
            os.environ["RECURSION_TRANSITION_FAILPOINT"] = prior


def instruction_body(digest: str) -> str:
    return f"approve plan-alpha {digest}"


def plan_object() -> dict:
    gate_contract = {"gate_files": {"app/main.sh": "a" * 64}}
    return {
        "schema_version": 1,
        "id": "plan-alpha",
        "project_id": "alpha",
        "goal": {
            "id": "goal-alpha",
            "outcome": "Bounded fixture outcome.",
            "acceptance_suite": "bash -n app/main.sh",
            "falsifier": "The exact commit does not pass the fixture build.",
            "gate_class": "light",
            "gate_files": ["app/main.sh"],
            "controller_gate_files": [],
            "gate_contract": gate_contract,
            "budget": {
                "max_concurrency": 1, "max_tokens": 12000, "max_cost_usd": 5,
                "max_wall_clock_seconds": 3600, "max_task_attempts": 2,
                "max_failures": 1, "max_review_queue": 1, "max_publish_attempts": 1,
                "publication_required": True,
            },
        },
        "tasks": [{
            "id": "task-alpha", "intent": "Bounded fixture task.",
            "dependencies": [], "allowed_paths": ["app"],
            "non_goals": ["credentials", "merge", "deploy"],
            "worker_class": "claude", "engine": "claude", "model_alias": "sonnet-routine",
            "verifier_model_alias": "opus-review", "deadline_seconds": 1800,
            "verifier_deadline_seconds": 900, "network_policy": "provider-only",
            "evidence_contract": "worker-result-v1", "verification": "independent",
            "expected_change": "required", "gate_class": "light",
            "gate_files": ["app/main.sh"], "controller_gate_files": [],
            "gate_contract": gate_contract,
            "acceptance": "bash -n app/main.sh",
        }],
    }


class Fixture:
    def __init__(self, name: str, *, lawful: bool = True) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix=f"phase8-auth-{name}-"))
        self.root = self.temp / "root"
        self.root.mkdir()
        shutil.copytree(SOURCE / "scripts", self.root / "scripts")
        if os.name == "nt":
            # The controller is deployed on Linux. This no-contention shim lets the hermetic,
            # single-process fixture exercise the receipt machinery from the authoring host.
            (self.root / "scripts/fcntl.py").write_text(
                "LOCK_EX=2\nLOCK_NB=4\ndef flock(_file, _flags):\n    return None\n",
                encoding="utf-8",
            )
        for relative in (
            "state/project-config", "state/pilots", "state/goals", "state/tasks",
            "state/instructions", "state/actions", "state/runs", "state/evidence",
            "state/plans/alpha", "state/pilot-windows", "state/assists",
            "state/pilot-requests/alpha", "state/deliveries", "state/notification-events",
            "state/transport-evidence", "state/reports", "state/recovery", "state/.locks",
            "loop/logs", "bin",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        for relative in ("state/events.jsonl", "state/action-events.jsonl"):
            (self.root / relative).write_text("", encoding="utf-8")
        (self.root / ".env").write_text("", encoding="utf-8")
        self.receipt = load(self.root / "scripts/transition_receipt.py", "transition_receipt")
        if os.name == "nt":
            # Receipt authority is the subject of this hermetic, single-process suite; the
            # witnessed directory-lock implementation is separately exercised on Linux and
            # cannot model POSIX rename semantics on Windows. Keep the state/event machinery
            # real while replacing only that outer serialization guard.
            @contextmanager
            def unlocked_guard(_base, _already_held=False):
                yield

            self.receipt._taskctl_guard = unlocked_guard
            self.receipt.os.fchmod = lambda _fd, _mode: None
        self.outbox = load(self.root / "scripts/notification-outbox.py",
                           f"auth_outbox_{name}")
        if os.name == "nt":
            self.outbox.fsync_dir = lambda _path: None
        self.env = os.environ.copy()
        self.env.update({
            "RECURSION_ROOT": str(self.root),
            "RECURSION_QUEUE_ACTUATION": "1",
            "RECURSION_INTAKE_ALLOW": "8913126684",
            "RECURSION_NO_NOTIFY": "0",
        })
        self.project_topic = "project-topic:telegram:-100100:11"
        self.head = "head-hermes:telegram:-100100:1"
        self.direct = "lucas-direct:telegram:8913126684"
        self.targets = [self.project_topic, self.head, self.direct]
        self._write_project()
        self.plan = plan_object()
        self.digest = canonical_digest(self.plan)
        self._write_instruction()
        if lawful:
            self.build_lawful_chain()
        self._write_runs()
        self._process_env = {
            key: os.environ.get(key) for key in ("RECURSION_ROOT", "RECURSION_QUEUE_ACTUATION",
                                                 "RECURSION_INTAKE_ALLOW")
        }
        os.environ.update({
            "RECURSION_ROOT": str(self.root),
            "RECURSION_QUEUE_ACTUATION": "1",
            "RECURSION_INTAKE_ALLOW": "8913126684",
        })

    def close(self) -> None:
        for key, prior in self._process_env.items():
            if prior is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prior
        shutil.rmtree(self.temp, ignore_errors=True)

    def _write_project(self) -> None:
        cfg = {
            "schema_version": 1, "id": "alpha", "repo": str(self.root / "repo"),
            "remote": "origin", "default_branch": "main", "deploy_key_ref": "-",
            "charter": "Phase 8 notification authentication fixture.",
            "allowed_paths": ["app"], "topic": 11, "pilot_id": "pilot-alpha",
            "activation_gate": "fixture", "notification_targets": self.targets,
            "goal_source": "state/goals/goal-alpha.md", "status": "active",
        }
        pilot = {
            "schema_version": 1, "id": "pilot-alpha", "project_id": "alpha", "topic": 11,
            "charter": cfg["charter"], "model_policy": "project-pilot",
            "concurrency_limit": 1, "budget": {"max_inflight_workers": 1},
            "notification_targets": self.targets, "goal_source": cfg["goal_source"],
            "memory_key": "fixture:11", "worktree_root": ".worktrees/alpha",
            "window_required": True, "status": "active",
        }
        self.write_json("state/project-config/alpha.json", cfg)
        self.write_json("state/pilots/pilot-alpha.json", pilot)

    def _write_instruction(self) -> None:
        (self.root / "state/instructions/00000001.md").write_text(
            "schema_version: 1\nid: 1\nprincipal: 8913126684\ntopic: 11\n"
            "project_id: alpha\npilot_id: pilot-alpha\nrouting_target: head-hermes\n"
            "deduplication_key: fixture:approve\nstatus: open\naction_ids:\n\n"
            f"## INSTRUCTION\n{instruction_body(self.digest)}\n",
            encoding="utf-8",
        )
        (self.root / "state/instructions/00000002.md").write_text(
            "schema_version: 1\nid: 2\nprincipal: 8913126684\ntopic: 11\n"
            "project_id: alpha\npilot_id: pilot-alpha\nrouting_target: head-hermes\n"
            "deduplication_key: fixture:window\nstatus: open\naction_ids:\n\n"
            "## INSTRUCTION\nOpen pilot window window-alpha for goal goal-alpha for 900 seconds.\n",
            encoding="utf-8",
        )

    def _write_runs(self) -> None:
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

    def write_json(self, relative: str, value: dict) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
                        encoding="utf-8")
        return path

    def commit(self, mutations, event: dict, *, journal: str = "state/events.jsonl",
               authoritative_index: int = -1) -> str:
        return self.receipt.commit_transition(
            self.root, mutations, event, journal=journal,
            authoritative_index=authoritative_index,
        )

    def commit_event(self, event: dict) -> str:
        return self.receipt.commit_event(self.root, event)

    def raw_row(self, event_id: str, event: str, *, task: str = "", detail: object = "") -> None:
        value = {
            "schema_version": 1, "id": event_id, "ts": "2026-08-10T00:00:00Z",
            "event": event, "project": "alpha", "goal": "goal-alpha", "task": task,
            "pid": 1, "detail": detail,
        }
        with (self.root / "state/events.jsonl").open("a", encoding="utf-8") as output:
            output.write(json.dumps(value, sort_keys=True) + "\n")

    def build_lawful_chain(self) -> None:
        digest = self.digest
        plan_path = self.root / "state/plans/alpha/plan-alpha.json"
        goal_path = self.root / "state/goals/goal-alpha.md"
        task_path = self.root / "state/tasks/task-alpha.md"
        window_path = self.root / "state/pilot-windows/window-alpha.json"

        proposed = {
            "schema_version": 1, "id": "plan-alpha", "project_id": "alpha",
            "pilot_id": "pilot-alpha", "instruction_id": "1", "plan_digest": digest,
            "plan": self.plan, "status": "proposed", "proposed_at": "2026-08-10T00:00:00Z",
        }
        self.commit(
            [self.receipt.json_mutation(plan_path, proposed)],
            {"schema_version": 1, "id": "source-plan-proposed-lawful",
             "ts": "2026-08-10T00:00:01Z", "event": "pilot-plan-proposed",
             "project": "alpha", "goal": "goal-alpha", "task": "", "pid": 1,
             "detail": {"plan_id": "plan-alpha", "plan_digest": digest,
                        "instruction_id": "1"}},
        )

        goal_body = ("schema_version: 1\nversion: 1\nid: goal-alpha\nproject_id: alpha\n"
                     "pilot_id: pilot-alpha\ninstruction_id: 1\nplan_id: plan-alpha\n"
                     "plan_digest: " + digest + "\nstatus: active\noutcome: Bounded fixture.\n"
                     "acceptance_suite: bash -n app/main.sh\nfalsifier: The build fails.\n"
                     "gate_class: light\ngate_files: app/main.sh\n"
                     "controller_gate_files:\ngate_contract: {}\n"
                     "source_head: " + "b" * 40 + "\nsource_branch: main\n"
                     "charter_sha256: " + "c" * 64 + "\nbudget: {}\n"
                     "started_at_epoch: 1\nterminal_reported: 0\n")
        task_body = ("schema_version: 1\nversion: 1\nid: task-alpha\nproject_id: alpha\n"
                     "workstream: alpha\npilot_id: pilot-alpha\ngoal_id: goal-alpha\n"
                     "plan_id: plan-alpha\nplan_digest: " + digest + "\ndependencies:\n"
                     "allowed_paths: app\nnon_goals: credentials,merge,deploy\n"
                     "worker_class: claude\nengine: claude\nmodel_alias: sonnet-routine\n"
                     "verifier_model_alias: opus-review\ndeadline_seconds: 1800\n"
                     "verifier_deadline_seconds: 900\nnetwork_policy: provider-only\n"
                     "evidence_contract: worker-result-v1\nverification: independent\n"
                     "expected_change: required\ngate_class: light\ngate_files: app/main.sh\n"
                     "controller_gate_files:\nacceptance: bash -n app/main.sh\n"
                     "status: proposed\n\nBounded fixture task.\n")
        approved = dict(proposed)
        approved.update({"status": "approved", "approval_instruction_id": "1",
                         "approved_by": "8913126684",
                         "approved_at": "2026-08-10T00:00:02Z"})
        self.commit(
            [self.receipt.text_mutation(goal_path, goal_body),
             self.receipt.text_mutation(task_path, task_body),
             self.receipt.json_mutation(plan_path, approved)],
            {"schema_version": 1, "id": "source-plan-approved-lawful",
             "ts": "2026-08-10T00:00:02Z", "event": "pilot-plan-approved",
             "project": "alpha", "goal": "goal-alpha", "task": "", "pid": 1,
             "detail": {"plan_id": "plan-alpha", "plan_digest": digest,
                        "instruction_id": "1"}},
            authoritative_index=2,
        )

        action = {
            "schema_version": 1, "id": "action-approve-lawful", "decision_id": "decision-approve",
            "instruction_id": "1", "idempotency_key": "phase8:approve:lawful",
            "verb": "pilot-plan-approve", "arguments": ["alpha", "plan-alpha", digest],
            "goal_id": "goal-alpha", "status": "succeeded", "actor": "head-hermes",
            "project": "alpha", "decision_source": "phase8-fixture",
            "routed_decider": "head-hermes", "action_payload_sha256": "a" * 64,
            "lease_owner": None, "lease_expires": None, "attempts": 1,
            "result_evidence": "approved", "created_at": "2026-08-10T00:00:02Z",
            "updated_at": "2026-08-10T00:00:03Z",
        }
        self.commit(
            [self.receipt.json_mutation(self.root / "state/actions/action-approve-lawful.json", action)],
            {"schema_version": 1, "ts": "2026-08-10T00:00:03Z",
             "action_id": action["id"], "status": "succeeded", "attempt": 1,
             "idempotency_key": action["idempotency_key"], "evidence": "approved"},
            journal="state/action-events.jsonl",
        )

        armed_window = {
            "schema_version": 1, "id": "window-alpha", "project_id": "alpha",
            "pilot_id": "pilot-alpha", "goal_id": "goal-alpha", "plan_id": "plan-alpha",
            "plan_digest": digest, "instruction_id": "2", "opened_by": "8913126684",
            "status": "armed", "armed_at": "2026-08-10T00:00:04Z",
            "opened_at_epoch": 1000, "expires_at_epoch": 1900,
            "duration_seconds": 900,
            "max_inflight_workers": 1,
        }
        self.commit(
            [self.receipt.json_mutation(window_path, armed_window)],
            {"schema_version": 1, "id": "source-window-armed-lawful",
             "ts": "2026-08-10T00:00:04Z", "event": "pilot-window-armed",
             "project": "alpha", "goal": "goal-alpha", "task": "", "pid": 1,
             "detail": {"window_id": "window-alpha", "instruction_id": "2"}},
        )

        window_action = {
            "schema_version": 1, "id": "action-window-lawful", "decision_id": "decision-window",
            "instruction_id": "2", "idempotency_key": "phase8:window:lawful",
            "verb": "pilot-window-open",
            "arguments": ["alpha", "goal-alpha", "window-alpha", "900"],
            "goal_id": "goal-alpha", "status": "succeeded", "actor": "head-hermes",
            "project": "alpha", "decision_source": "phase8-fixture",
            "routed_decider": "head-hermes", "action_payload_sha256": "b" * 64,
            "lease_owner": None, "lease_expires": None, "attempts": 1,
            "result_evidence": "armed", "created_at": "2026-08-10T00:00:04Z",
            "updated_at": "2026-08-10T00:00:04Z",
        }
        self.commit(
            [self.receipt.json_mutation(
                self.root / "state/actions/action-window-lawful.json", window_action)],
            {"schema_version": 1, "ts": "2026-08-10T00:00:04Z",
             "action_id": window_action["id"], "status": "succeeded", "attempt": 1,
             "idempotency_key": window_action["idempotency_key"], "evidence": "armed"},
            journal="state/action-events.jsonl",
        )

        opened_window = dict(armed_window)
        opened_window.update({"status": "open", "opened_at": "2026-08-10T00:00:05Z"})
        self.commit(
            [self.receipt.json_mutation(window_path, opened_window)],
            {"schema_version": 1, "id": "source-window-opened-lawful",
             "ts": "2026-08-10T00:00:05Z", "event": "pilot-window-opened",
             "project": "alpha", "goal": "goal-alpha", "task": "", "pid": 1,
             "detail": {"window_id": "window-alpha", "instruction_id": "2"}},
        )

        self.commit(
            [self.receipt.fields_mutation(task_path, {
                "status": "running", "lease_owner": "worker", "lease_expires": "2000",
                "attempts": "1", "started_at": "2026-08-10T00:00:06Z"})],
            {"schema_version": 1, "id": "source-start-lawful", "ts": "2026-08-10T00:00:06Z",
             "event": "start", "project": "alpha", "goal": "goal-alpha",
             "task": "task-alpha", "pid": 1, "detail": "owner=worker attempt=1"},
        )

        self.commit(
            [self.receipt.fields_mutation(task_path, {
                "status": "passed", "lease_expires": "0", "finished_at": "2026-08-10T00:00:07Z",
                "candidate_commit": "a" * 40})],
            {"schema_version": 1, "id": "source-finish-lawful", "ts": "2026-08-10T00:00:07Z",
             "event": "finish", "project": "alpha", "goal": "goal-alpha",
             "task": "task-alpha", "pid": 1, "detail": "status=passed ok"},
        )

        self.commit(
            [self.receipt.fields_mutation(task_path, {
                "review_status": "published", "review_commit": "a" * 40,
                "review_published_at": "2026-08-10T00:00:08Z"})],
            {"schema_version": 1, "id": "source-review-published-lawful",
             "ts": "2026-08-10T00:00:08Z", "event": "review-published",
             "project": "alpha", "goal": "goal-alpha", "task": "task-alpha", "pid": 1,
             "detail": {"branch": "loop/work/task-alpha", "commit_oid": "a" * 40}},
        )

        self.commit(
            [self.receipt.fields_mutation(goal_path, {
                "status": "verifying", "version": "2", "last_transition_from": "active",
                "last_transition_at": "2026-08-10T00:00:09Z",
                "last_transition_reason": "phase6"})],
            {"schema_version": 1, "id": "source-goal-verifying-lawful",
             "ts": "2026-08-10T00:00:09Z", "event": "goal-transition",
             "project": "alpha", "goal": "goal-alpha", "task": "", "pid": 1,
             "detail": {"from": "active", "to": "verifying", "reason": "phase6",
                        "version": 2}},
        )

        self.commit(
            [self.receipt.fields_mutation(goal_path, {
                "status": "achieved", "version": "3", "last_transition_from": "verifying",
                "last_transition_at": "2026-08-10T00:00:10Z",
                "last_transition_reason": "verified", "terminal_reported": "1",
                "finished_at": "2026-08-10T00:00:10Z"})],
            {"schema_version": 1, "id": "source-goal-achieved-lawful",
             "ts": "2026-08-10T00:00:10Z", "event": "goal-transition",
             "project": "alpha", "goal": "goal-alpha", "task": "", "pid": 1,
             "detail": {"from": "verifying", "to": "achieved", "reason": "verified",
                        "version": 3}},
        )

    def mapped_types(self) -> list[str]:
        return [event.get("event_type") for event in self.outbox.all_mapped(self.root, "alpha")]

    def reconcile(self, event_id: str) -> None:
        self.outbox.reconcile_event(self.root, "alpha", event_id)

    def events(self) -> list[dict]:
        result = []
        for path in sorted((self.root / "state/notification-events").glob("*.json")):
            try:
                result.append(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                pass
        return result

    def deliveries(self) -> list[dict]:
        result = []
        for path in sorted((self.root / "state/deliveries").glob("*.json")):
            try:
                result.append(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                pass
        return result


def event_counts(events: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        key = str(event.get("event_type") or "")
        counts[key] = counts.get(key, 0) + 1
    return counts


def test_exact_once_lawful_projection() -> tuple[bool, str]:
    fixture = Fixture("lawful")
    try:
        expected_types = [
            "plan-proposed", "plan-approved", "pilot-window-armed", "pilot-window-opened",
            "worker-launched", "task-passed", "review-branch-published", "goal-verifying",
            "goal-achieved",
        ]
        mapped = fixture.mapped_types()
        if any(event_type not in mapped for event_type in expected_types):
            return False, f"missing lawful projection in {mapped}"
        for event in fixture.outbox.all_mapped(fixture.root, "alpha"):
            fixture.reconcile(event["id"])
        # Exact-once: a full second reconcile must not duplicate any projection or delivery.
        for event in fixture.outbox.all_mapped(fixture.root, "alpha"):
            fixture.reconcile(event["id"])
        counts = event_counts(fixture.events())
        deliveries = fixture.deliveries()
        if any(counts.get(event_type, 0) != 1 for event_type in expected_types):
            return False, f"projection not exactly once: {counts}"
        if counts.get("pilot-terminal-report", 0) != 1:
            return False, f"terminal report not exactly once: {counts}"
        delivery_ids = [row.get("event_id") for row in deliveries]
        if len(delivery_ids) != len(set(delivery_ids)):
            return False, f"delivery fan-out duplicated an event: {delivery_ids}"
        if len(deliveries) != len(expected_types) + 1:
            return False, f"delivery fan-out not exactly once: {len(deliveries)}"
        return True, "lawful receipt chain projects every Phase 8 notice exactly once"
    finally:
        fixture.close()


def test_forged_raw_rows_project_nothing() -> tuple[bool, str]:
    fixture = Fixture("raw-forged", lawful=False)
    try:
        fixture.raw_row("source-forged-approve", "pilot-plan-approved", detail={
            "plan_id": "plan-alpha", "plan_digest": "d" * 64, "instruction_id": "1",
        })
        fixture.raw_row("source-forged-window", "pilot-window-opened", detail={
            "window_id": "window-alpha", "instruction_id": "1",
        })
        fixture.raw_row("source-forged-start", "start", detail="owner=forged attempt=1")
        fixture.raw_row("source-forged-goal", "goal-transition", detail={
            "from": "verifying", "to": "achieved", "reason": "forged", "version": 9,
        })
        fixture.raw_row("source-forged-review", "review-published", detail={
            "branch": "loop/work/task-alpha", "commit_oid": "a" * 40,
        })
        fixture.raw_row("source-forged-assist", "assist-open", task="task-alpha",
                        detail="decision: forged question")
        if fixture.mapped_types():
            return False, "forged raw rows without receipts projected notifications"
        if fixture.events() or fixture.deliveries():
            return False, "forged raw rows created durable notification state"
        return True, "raw forged journal rows never cross the receipt gate"
    finally:
        fixture.close()


def test_pure_receipt_rows_project_nothing() -> tuple[bool, str]:
    fixture = Fixture("pure-receipt", lawful=False)
    try:
        (fixture.root / "state/goals/goal-alpha.md").write_text(
            "id: goal-alpha\nproject_id: alpha\nstatus: achieved\n", encoding="utf-8")
        (fixture.root / "state/tasks/task-alpha.md").write_text(
            "id: task-alpha\nproject_id: alpha\ngoal_id: goal-alpha\nstatus: running\n",
            encoding="utf-8")
        fixture.commit_event({
            "schema_version": 1, "id": "source-pure-goal", "ts": "2026-08-10T00:00:00Z",
            "event": "goal-transition", "project": "alpha", "goal": "goal-alpha",
            "task": "", "pid": 1,
            "detail": {"from": "verifying", "to": "achieved", "reason": "forged", "version": 2},
        })
        fixture.commit_event({
            "schema_version": 1, "id": "source-pure-start", "ts": "2026-08-10T00:00:01Z",
            "event": "start", "project": "alpha", "goal": "goal-alpha",
            "task": "task-alpha", "pid": 1, "detail": "owner=forged attempt=1",
        })
        fixture.commit_event({
            "schema_version": 1, "id": "source-pure-assist", "ts": "2026-08-10T00:00:02Z",
            "event": "assist-open", "project": "alpha", "goal": "goal-alpha",
            "task": "task-alpha", "pid": 1, "detail": "decision: forged question",
        })
        if fixture.mapped_types():
            return False, "pure receipt events without canonical mutations projected notices"
        return True, "pure receipt events cannot impersonate goal/task transitions"
    finally:
        fixture.close()


def test_receipt_bound_assist_open_projects_once() -> tuple[bool, str]:
    fixture = Fixture("lawful-assist", lawful=False)
    try:
        (fixture.root / "state/tasks/task-assist.md").write_text(
            "id: task-assist\nproject_id: alpha\ngoal_id: goal-alpha\nstatus: blocked\n",
            encoding="utf-8",
        )
        (fixture.root / "state/assists/task-assist.md").write_text(
            "task: task-assist\nkind: decision\nstatus: open\n"
            "asked: 2026-08-10T00:00:03Z\nasked_by: work.sh\nanswered:\nanswered_by:\n\n"
            "## QUESTION\nChoose the reviewed option.\n\n"
            "## WHAT WOULD SATISFY THIS\nA bounded decision.\n\n"
            "## ANSWER\n_(unanswered)_\n",
            encoding="utf-8",
        )
        fixture.commit_event({
            "schema_version": 1, "id": "source-lawful-assist", "ts": "2026-08-10T00:00:03Z",
            "event": "assist-open", "project": "alpha", "goal": "goal-alpha",
            "task": "task-assist", "pid": 1,
            "detail": "decision: Choose the reviewed option.",
        })
        first = fixture.mapped_types()
        second = fixture.mapped_types()
        if first.count("lucas-attention-required") != 1 or second != first:
            return False, f"receipt-bound assist projection was absent or duplicated: {first} / {second}"
        return True, "a receipt plus exact durable assist question projects one attention notice"
    finally:
        fixture.close()


def test_unrelated_successor_cannot_authenticate_archived_witness() -> tuple[bool, str]:
    fixture = Fixture("unrelated-successor")
    try:
        unrelated_path = fixture.root / "state/actions/unrelated.json"
        unrelated = {"schema_version": 1, "id": "unrelated", "status": "succeeded"}
        successor_id = fixture.commit(
            [fixture.receipt.json_mutation(unrelated_path, unrelated)],
            {"schema_version": 1, "id": "source-unrelated-successor",
             "ts": "2026-08-10T00:00:20Z", "event": "audit-only", "project": "alpha",
             "goal": "goal-alpha", "task": "", "pid": 1, "detail": "unrelated"},
        )
        plan_path = fixture.root / "state/plans/alpha/plan-alpha.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["event_seq"] = int(plan.get("event_seq") or 0) + 100
        plan["last_transition_id"] = successor_id
        fixture.write_json("state/plans/alpha/plan-alpha.json", plan)
        try:
            fixture.receipt.authenticated_chain_transition(
                fixture.root, "source-plan-proposed-lawful", journal="state/events.jsonl")
        except fixture.receipt.TransitionReceiptError:
            return True, "an unrelated receipt cannot own an archived canonical witness"
        return False, "unrelated successor receipt authenticated a hand-edited plan witness"
    finally:
        fixture.close()


def test_cross_journal_successor_cannot_authenticate_archived_witness() -> tuple[bool, str]:
    fixture = Fixture("cross-journal-successor")
    try:
        plan_path = fixture.root / "state/plans/alpha/plan-alpha.json"
        moved = json.loads(plan_path.read_text(encoding="utf-8"))
        moved["cross_journal_marker"] = "must-not-authenticate-state-history"
        fixture.commit(
            [fixture.receipt.json_mutation(plan_path, moved)],
            {"schema_version": 1, "ts": "2026-08-10T00:00:21Z",
             "action_id": "action-cross-journal-successor", "status": "succeeded",
             "attempt": 1, "idempotency_key": "cross-journal-successor",
             "evidence": "must-not-own-state-history"},
            journal="state/action-events.jsonl",
        )
        try:
            fixture.receipt.authenticated_chain_transition(
                fixture.root, "source-plan-proposed-lawful", journal="state/events.jsonl")
        except fixture.receipt.TransitionReceiptError:
            return True, "an action-journal receipt cannot advance state-journal authority"
        return False, "a cross-journal receipt authenticated archived state authority"
    finally:
        fixture.close()


def test_forged_objects_fail_closed() -> tuple[bool, str]:
    goal_forged = Fixture("object-goal", lawful=False)
    action_forged = Fixture("object-action", lawful=False)
    window_forged = Fixture("object-window", lawful=False)
    try:
        goal_forged.build_lawful_chain()
        goal_path = goal_forged.root / "state/goals/goal-alpha.md"
        goal_text = goal_path.read_text(encoding="utf-8")
        # Hand-edited canonical object: no receipt ever moved the goal, yet its version rewrites.
        goal_path.write_text(goal_text.replace("version: 3", "version: 99", 1),
                             encoding="utf-8")
        goal_mapped = goal_forged.mapped_types()
        if "goal-achieved" in goal_mapped or "goal-verifying" in goal_mapped:
            return False, f"hand-forged goal object projected terminal notices: {goal_mapped}"

        action_forged.build_lawful_chain()
        action_path = action_forged.root / "state/actions/action-approve-lawful.json"
        action = json.loads(action_path.read_text(encoding="utf-8"))
        action["last_transition_id"] = "transition-" + "f" * 32
        action_forged.write_json("state/actions/action-approve-lawful.json", action)
        action_mapped = action_forged.mapped_types()
        if "plan-approved" in action_mapped:
            return False, "forged approval action authorized the plan approval notice"

        window_forged.build_lawful_chain()
        window_path = window_forged.root / "state/pilot-windows/window-alpha.json"
        window = json.loads(window_path.read_text(encoding="utf-8"))
        window["plan_digest"] = "e" * 64
        window_forged.write_json("state/pilot-windows/window-alpha.json", window)
        window_mapped = window_forged.mapped_types()
        if "pilot-window-armed" in window_mapped or "pilot-window-opened" in window_mapped:
            return False, f"forged window object projected window notices: {window_mapped}"
        return True, "forged plan/window/goal/action objects fail closed"
    finally:
        goal_forged.close(); action_forged.close(); window_forged.close()


def test_tampered_and_missing_receipts_fail_closed() -> tuple[bool, str]:
    tampered = Fixture("receipt-tampered", lawful=False)
    missing = Fixture("receipt-missing", lawful=False)
    try:
        tampered.build_lawful_chain()
        index_root = tampered.root / "state/recovery/transition-event-index"
        approve_record = None
        for index_path in index_root.rglob("*.json"):
            record = json.loads(index_path.read_text(encoding="utf-8"))
            if record.get("event_id") == "source-plan-approved-lawful":
                approve_record = record
                break
        if approve_record is None:
            return False, "cannot locate the approval index entry"
        transition_id = str(approve_record["transition_id"])
        prepared_paths = list((tampered.root / "state/recovery/transition-archive")
                              .glob("*/" + transition_id + "/prepared.json"))
        if len(prepared_paths) != 1:
            return False, "cannot locate the archived approval receipt"
        prepared = json.loads(prepared_paths[0].read_text(encoding="utf-8"))
        prepared["event"]["detail"]["plan_digest"] = "d" * 64
        prepared_paths[0].write_text(json.dumps(prepared, sort_keys=True) + "\n", encoding="utf-8")
        tampered_types = tampered.mapped_types()
        if "plan-approved" in tampered_types or "plan-proposed" in tampered_types:
            return False, f"tampered receipt still projected plan notices: {tampered_types}"

        missing.build_lawful_chain()
        index_files = list((missing.root / "state/recovery/transition-event-index").rglob("*.json"))
        removed = 0
        for index_path in index_files:
            record = json.loads(index_path.read_text(encoding="utf-8"))
            if record.get("event_id") in {"source-plan-approved-lawful", "source-goal-achieved-lawful"}:
                index_path.unlink()
                removed += 1
        if removed != 2:
            return False, f"expected 2 index entries, removed {removed}"
        missing_types = missing.mapped_types()
        if "plan-approved" in missing_types or "goal-achieved" in missing_types:
            return False, f"missing receipt index still projected notices: {missing_types}"
        return True, "tampered and missing receipts fail closed"
    finally:
        tampered.close(); missing.close()


def test_replay_is_collapsed_and_journal_replay_fails() -> tuple[bool, str]:
    fixture = Fixture("replay")
    try:
        mapped = [event for event in fixture.outbox.all_mapped(fixture.root, "alpha")]
        if len(mapped) != 9:
            return False, f"expected 9 lawful projections, got {len(mapped)}"
        for event in mapped:
            fixture.reconcile(event["id"])
        before_events = len(fixture.events())
        before_deliveries = len(fixture.deliveries())
        for event in fixture.outbox.all_mapped(fixture.root, "alpha"):
            fixture.reconcile(event["id"])
        if len(fixture.events()) != before_events or len(fixture.deliveries()) != before_deliveries:
            return False, "second reconcile duplicated projections or deliveries"
        # A duplicated journal row is journal replay: the receipt evidence no longer matches.
        fixture.raw_row("source-goal-achieved-lawful", "goal-transition", detail={
            "from": "verifying", "to": "achieved", "reason": "verified", "version": 3,
        })
        if any(event.get("source_event_id") == "source-goal-achieved-lawful" for event in
               fixture.outbox.all_mapped(fixture.root, "alpha")):
            return False, "journal replay re-projected a duplicated row"
        return True, "replay collapses to exact-once and duplicated journal rows fail"
    finally:
        fixture.close()


def test_crash_recovery_projects_exactly_once() -> tuple[bool, str]:
    fixture = Fixture("crash")
    try:
        event = next(event for event in fixture.outbox.all_mapped(fixture.root, "alpha")
                     if event["event_type"] == "worker-launched")
        path = fixture.root / "state/notification-events" / f"{event['id']}.json"
        journal = fixture.root / "state/notification-event-events.jsonl"
        with failpoint("state-write"):
            try:
                fixture.outbox.create_event(fixture.root, event)
            except fixture.outbox.OutboxError:
                pass
        if not path.is_file():
            return False, "canonical notification projection did not commit before the crash"
        if journal.is_file() and list(journal.read_text(encoding="utf-8").splitlines()) != []:
            return False, "event journal advanced before recovery"
        fixture.outbox.recover_notification_transitions(fixture.root)
        rows = [line for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(rows) != 1:
            return False, f"recovery projected {len(rows)} audit rows instead of one"
        fixture.outbox.recover_notification_transitions(fixture.root)
        rows = [line for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(rows) != 1:
            return False, "recovery duplicated an already-projected receipt"
        return True, "mid-projection crash recovers the receipt exactly once"
    finally:
        fixture.close()


def main() -> int:
    controls = (
        ("forged raw Phase 8 journal rows project no notification", test_forged_raw_rows_project_nothing),
        ("pure receipt rows without canonical transitions project nothing", test_pure_receipt_rows_project_nothing),
        ("receipt-bound durable assist projects exactly one notice", test_receipt_bound_assist_open_projects_once),
        ("archived witnesses require a same-object authenticated successor", test_unrelated_successor_cannot_authenticate_archived_witness),
        ("archived witnesses cannot cross journal authority", test_cross_journal_successor_cannot_authenticate_archived_witness),
        ("forged nonempty plan/window/goal/action objects fail closed", test_forged_objects_fail_closed),
        ("tampered or missing receipts fail closed", test_tampered_and_missing_receipts_fail_closed),
        ("replay collapses exact-once and duplicated journal rows fail", test_replay_is_collapsed_and_journal_replay_fails),
        ("mid-projection crash recovers the receipt exactly once", test_crash_recovery_projects_exactly_once),
        ("exact-once lawful Phase 8 projection", test_exact_once_lawful_projection),
    )
    failures = 0
    for description, control in controls:
        try:
            passed, detail = control()
        except Exception as exc:  # A falsifier reports failure; it never aborts later controls.
            passed, detail = False, repr(exc)
        if passed:
            print(f"ok    {description}")
        else:
            failures += 1
            print(f"FAIL  {description}: {detail}")
    print(f"phase8-notification-authentication: {len(controls) - failures}/{len(controls)} controls passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

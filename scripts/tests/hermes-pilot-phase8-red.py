#!/usr/bin/env python3
"""Phase 8 red-to-green controls for plan synthesis and pilot-window admission."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
CONTROLS = [
    "a fresh instruction produces a new schema-complete plan without reusing legacy Chiron state",
    "a malformed or structurally vacuous autonomous plan is rejected without partial state",
    "Lucas exact-digest approval materializes one new goal DAG idempotently",
    "only the exact goal in an open bounded pilot window is schedulable",
    "observing PAUSE closes the window so resume cannot replay its authority",
    "an answered assist reopens the same goal and task once through the durable outbox path",
]


def canonical_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def fields(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            result.setdefault(key.strip(), value.strip())
    return result


class Fixture:
    def __init__(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="phase8-red-"))
        self.root = self.temp / "root"
        shutil.copytree(SOURCE / "scripts", self.root / "scripts")
        shutil.copytree(SOURCE / "schemas", self.root / "schemas")
        if os.name == "nt":
            # The controller is deployed on Linux. This no-contention shim lets the hermetic,
            # single-process fixture exercise its state machines from the Windows authoring host.
            (self.root / "scripts/fcntl.py").write_text(
                "LOCK_EX=2\nLOCK_NB=4\ndef flock(_file, _flags):\n    return None\n",
                encoding="utf-8",
            )
        for relative in (
            "state/project-config", "state/pilots", "state/goals", "state/tasks",
            "state/plans/chiron", "state/pilot-windows", "state/instructions",
            "state/actions", "state/assists", "state/pilot-requests/chiron",
            "state/decision-queue/pending", "state/decision-queue/running",
            "state/decision-queue/succeeded", "state/decision-queue/failed",
            "state/deliveries", "state/notification-events", "state/.locks", "loop/logs",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        for relative in ("state/events.jsonl", "state/action-events.jsonl", "state/decisions.jsonl", "state/INBOX.md"):
            (self.root / relative).write_text("", encoding="utf-8")
        (self.root / ".env").write_text("", encoding="utf-8")
        self.env = os.environ.copy()
        self.env.update({
            "RECURSION_ROOT": str(self.root),
            "RECURSION_QUEUE_ACTUATION": "1",
            "RECURSION_INTAKE_ALLOW": "8913126684",
            "RECURSION_NO_NOTIFY": "0",
        })
        self._write_project()
        self._write_legacy_state()
        self._write_instruction("101", "pilot-chiron")
        self.plan = self._plan()
        self.plan_id = str(self.plan["id"])
        self.digest = canonical_digest(self.plan)

    def close(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def _write_project(self) -> None:
        (self.root / "state/portfolio.tsv").write_text(
            "#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n"
            "chiron\t/fixture/chiron\torigin\tmain\t-\t-\t10\tactive\n",
            encoding="utf-8",
        )
        config = {
            "schema_version": 1, "id": "chiron", "repo": "/fixture/chiron",
            "remote": "origin", "default_branch": "main", "deploy_key_ref": "-",
            "charter": "Build-verifiable Chiron application changes only.",
            "allowed_paths": ["src", "tests"], "topic": 10, "pilot_id": "pilot-chiron",
            "activation_gate": "clone-auth-freshness-v1",
            "notification_targets": ["project-topic:telegram:-100:10", "head-hermes:telegram:-100:1"],
            "goal_source": "state/goals", "status": "active",
        }
        pilot = {
            "schema_version": 1, "id": "pilot-chiron", "project_id": "chiron", "topic": 10,
            "charter": config["charter"], "model_policy": "project-pilot",
            "concurrency_limit": 1, "budget": {"max_inflight_workers": 1},
            "notification_targets": config["notification_targets"], "goal_source": "state/goals",
            "memory_key": "telegram-topic:10", "worktree_root": ".worktrees/chiron",
            "window_required": True, "status": "active",
        }
        self.write_json("state/project-config/chiron.json", config)
        self.write_json("state/pilots/pilot-chiron.json", pilot)

    def _write_legacy_state(self) -> None:
        (self.root / "state/goals/goal-chiron-legacy.md").write_text(
            "schema_version: 1\nversion: 1\nid: goal-chiron-legacy\nproject_id: chiron\n"
            "status: active\noutcome: Historical shell.\nacceptance_suite: npm run build\n"
            "falsifier: The historical build fails.\nbudget: historical\n",
            encoding="utf-8",
        )
        (self.root / "state/tasks/chiron-legacy-task.md").write_text(
            "schema_version: 1\nversion: 1\nid: chiron-legacy-task\nproject_id: chiron\n"
            "goal_id: goal-chiron-legacy\nstatus: passed\nacceptance: npm run build\n",
            encoding="utf-8",
        )
        self.legacy_hash = canonical_digest({
            "goal": (self.root / "state/goals/goal-chiron-legacy.md").read_text(encoding="utf-8"),
            "task": (self.root / "state/tasks/chiron-legacy-task.md").read_text(encoding="utf-8"),
        })

    def _write_instruction(self, iid: str, target: str, body: str = "fixture instruction") -> None:
        name = f"{int(iid):08d}.md"
        (self.root / "state/instructions" / name).write_text(
            f"schema_version: 1\nid: {iid}\nprincipal: 8913126684\ntopic: 10\n"
            f"project_id: chiron\npilot_id: pilot-chiron\nrouting_target: {target}\n"
            f"deduplication_key: fixture\nstatus: open\naction_ids:\n\n## INSTRUCTION\n{body}\n",
            encoding="utf-8",
        )

    @staticmethod
    def _plan() -> dict:
        return {
            "schema_version": 1,
            "id": "chiron-phase8-plan",
            "project_id": "chiron",
            "goal": {
                "id": "goal-chiron-phase8-smoke",
                "outcome": "Add one reversible build-verifiable Chiron smoke marker.",
                "acceptance_suite": "npm run build",
                "falsifier": "The exact candidate commit does not pass the clean Chiron build.",
                "budget": {
                    "max_concurrency": 1, "max_tokens": 12000, "max_cost_usd": 5,
                    "max_wall_clock_seconds": 3600, "max_task_attempts": 2,
                    "max_failures": 1, "max_review_queue": 1, "max_publish_attempts": 1,
                    "publication_required": True,
                },
            },
            "tasks": [{
                "id": "chiron-phase8-smoke", "intent": "Add the bounded smoke marker.",
                "dependencies": [], "allowed_paths": ["src", "tests"],
                "non_goals": ["learning-loop", "credentials", "merge", "deploy"],
                "worker_class": "claude", "engine": "claude", "model_alias": "sonnet-routine",
                "verifier_model_alias": "opus-review", "deadline_seconds": 1800,
                "verifier_deadline_seconds": 900, "network_policy": "provider-only",
                "evidence_contract": "worker-result-v1", "verification": "independent",
                "expected_change": "required", "gate_files": ["package.json"],
                "acceptance": "npm run build",
            }],
        }

    def write_json(self, relative: str, value: dict) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        return path

    def decision(self, *, verb: str, args: list[str], iid: str, actor: str, goal: str,
                 text: str, extra: dict | None = None) -> Path:
        value = {
            "schema_version": 1, "id": f"decision-{verb}-{iid}", "actor": actor,
            "verb": verb, "args": args, "arguments": args, "project": "chiron",
            "goal": goal, "goal_id": goal, "text": text, "instruction_id": iid,
            "why": "Phase 8 bounded pilot control.", "reason": "Phase 8 bounded pilot control.",
            "wrong_if": "Exact correlated state or evidence disagrees.",
            "idempotency_key": f"phase8:{verb}:{iid}", "status": "queued",
        }
        value.update(extra or {})
        return self.write_json(f"decision-{verb}-{iid}.json", value)

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, cwd=self.root, env=self.env, text=True, capture_output=True, check=False)

    def legacy_unchanged(self) -> bool:
        return self.legacy_hash == canonical_digest({
            "goal": (self.root / "state/goals/goal-chiron-legacy.md").read_text(encoding="utf-8"),
            "task": (self.root / "state/tasks/chiron-legacy-task.md").read_text(encoding="utf-8"),
        })


def test_fresh_plan(f: Fixture) -> bool:
    decision = f.decision(
        verb="pilot-plan-propose", args=["chiron", f.plan_id], iid="101",
        actor="pilot-chiron", goal=str(f.plan["goal"]["id"]),
        text="Propose a fresh bounded Chiron Phase 8 plan.", extra={"plan": f.plan},
    )
    result = f.run("python3", "scripts/project-pilot.py", "execute", str(decision))
    path = f.root / f"state/plans/chiron/{f.plan_id}.json"
    if result.returncode or not path.is_file() or not f.legacy_unchanged():
        return False
    record = json.loads(path.read_text(encoding="utf-8"))
    return (
        record.get("status") == "proposed"
        and record.get("plan_digest") == f.digest
        and record.get("instruction_id") == "101"
        and record.get("plan") == f.plan
        and not (f.root / "state/goals/goal-chiron-phase8-smoke.md").exists()
    )


def test_invalid_plan(f: Fixture) -> bool:
    def refused(suffix: str, mutate) -> bool:
        bad = json.loads(json.dumps(f.plan)); bad["id"] = f"chiron-phase8-invalid-{suffix}"
        mutate(bad)
        decision = f.decision(
            verb="pilot-plan-propose", args=["chiron", bad["id"]], iid="101",
            actor="pilot-chiron", goal=str(bad["goal"]["id"]), text="Propose an invalid plan.",
            extra={"plan": bad, "id": f"decision-invalid-{suffix}",
                   "idempotency_key": f"phase8:invalid:{suffix}"},
        )
        result = f.run("python3", "scripts/project-pilot.py", "execute", str(decision))
        return result.returncode != 0 and not (f.root / f"state/plans/chiron/{bad['id']}.json").exists()

    return all((
        refused("gate", lambda p: p["tasks"][0].__setitem__("acceptance", "true")),
        refused("review-zero", lambda p: p["goal"]["budget"].__setitem__("max_review_queue", 0)),
        refused("metered", lambda p: p["tasks"][0].__setitem__("engine", "hermes")),
    ))


def test_approval(f: Fixture) -> bool:
    f._write_instruction("102", "head-hermes", f"approve {f.plan_id} {f.digest}")
    decision = f.decision(
        verb="pilot-plan-approve", args=["chiron", f.plan_id, f.digest], iid="102",
        actor="head-hermes", goal=str(f.plan["goal"]["id"]),
        text="Approve exactly this plan digest for materialization.",
    )
    first = f.run("python3", "scripts/project-pilot.py", "execute", str(decision))
    second = f.run("python3", "scripts/project-pilot.py", "execute", str(decision))
    goal_path = f.root / "state/goals/goal-chiron-phase8-smoke.md"
    task_path = f.root / "state/tasks/chiron-phase8-smoke.md"
    if first.returncode or second.returncode or not goal_path.is_file() or not task_path.is_file():
        return False
    proposal = json.loads((f.root / f"state/plans/chiron/{f.plan_id}.json").read_text(encoding="utf-8"))
    return (
        fields(goal_path).get("status") == "active"
        and fields(goal_path).get("instruction_id") == "101"
        and fields(goal_path).get("plan_id") == f.plan_id
        and fields(task_path).get("status") == "proposed"
        and fields(task_path).get("workstream") == "chiron"
        and fields(task_path).get("acceptance") == "npm run build"
        and proposal.get("status") == "approved"
        and proposal.get("approval_instruction_id") == "102"
        and len(list((f.root / "state/goals").glob("goal-chiron-phase8-smoke.md"))) == 1
        and len(list((f.root / "state/tasks").glob("chiron-phase8-smoke.md"))) == 1
        and f.legacy_unchanged()
    )


def open_window(f: Fixture) -> bool:
    f._write_instruction(
        "103", "head-hermes", "authorize goal-chiron-phase8-smoke chiron-window-1 900"
    )
    decision = f.decision(
        verb="pilot-window-open",
        args=["chiron", "goal-chiron-phase8-smoke", "chiron-window-1", "900"], iid="103",
        actor="head-hermes", goal="goal-chiron-phase8-smoke",
        text="Authorize only the Chiron success pilot window.",
    )
    (f.root / "state/PAUSE").write_text("phase8-preflight\n", encoding="utf-8")
    result = f.run("python3", "scripts/project-pilot.py", "execute", str(decision))
    (f.root / "state/PAUSE").unlink(missing_ok=True)
    return result.returncode == 0


def test_window_admission(f: Fixture) -> bool:
    bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe" \
        if os.name == "nt" else Path("bash")
    sink = f.run(str(bash), "scripts/work.sh", "chiron-phase8-smoke")
    if sink.returncode != 75:
        return False
    before = f.run("python3", "scripts/project-reconcile.py", "schedule")
    if before.returncode or before.stdout.strip() != "0" or list((f.root / "state/decision-queue/pending").glob("*.json")):
        return False
    # A matching duration in metadata is not human authority. The exact bound must be a
    # token in the instruction body itself.
    f._write_instruction("109", "head-hermes", "authorize goal-chiron-phase8-smoke chiron-window-bad")
    bad_instruction = f.root / "state/instructions/00000109.md"
    bad_instruction.write_text(
        bad_instruction.read_text(encoding="utf-8").replace("topic: 10", "topic: 900"),
        encoding="utf-8",
    )
    bad_decision = f.decision(
        verb="pilot-window-open",
        args=["chiron", "goal-chiron-phase8-smoke", "chiron-window-bad", "900"], iid="109",
        actor="head-hermes", goal="goal-chiron-phase8-smoke",
        text="Metadata must not satisfy an omitted instruction-body bound.",
    )
    (f.root / "state/PAUSE").write_text("phase8-preflight\n", encoding="utf-8")
    bad = f.run("python3", "scripts/project-pilot.py", "execute", str(bad_decision))
    (f.root / "state/PAUSE").unlink(missing_ok=True)
    if bad.returncode == 0 or (f.root / "state/pilot-windows/chiron-window-bad.json").exists():
        return False
    if not open_window(f):
        return False
    scheduled = f.run("python3", "scripts/project-reconcile.py", "schedule")
    rows = [json.loads(path.read_text(encoding="utf-8")) for path in (f.root / "state/decision-queue/pending").glob("*.json")]
    return (
        scheduled.returncode == 0 and scheduled.stdout.strip() == "1" and len(rows) == 1
        and rows[0].get("verb") == "reconcile-goal"
        and rows[0].get("args") == ["chiron", "goal-chiron-phase8-smoke"]
        and rows[0].get("project") == "chiron"
    )


def test_pause_closes_window(f: Fixture) -> bool:
    (f.root / "state/PAUSE").write_text("phase8-test\n", encoding="utf-8")
    result = f.run("python3", "scripts/project-reconcile.py", "schedule")
    window = f.root / "state/pilot-windows/chiron-window-1.json"
    if result.returncode or not window.is_file():
        return False
    value = json.loads(window.read_text(encoding="utf-8"))
    return value.get("status") == "closed" and value.get("close_reason") == "pause-observed"


def test_assist_resume(f: Fixture) -> bool:
    (f.root / "state/PAUSE").unlink(missing_ok=True)
    goal_path = f.root / "state/goals/goal-chiron-phase8-smoke.md"
    task_path = f.root / "state/tasks/chiron-phase8-smoke.md"
    goal_text = goal_path.read_text(encoding="utf-8").replace("status: active", "status: blocked")
    task_text = task_path.read_text(encoding="utf-8").replace("status: proposed", "status: blocked")
    goal_path.write_text(goal_text, encoding="utf-8")
    task_path.write_text(task_text + "blocked_on: ambiguous marker placement\n", encoding="utf-8")
    (f.root / "state/assists/chiron-phase8-smoke.md").write_text(
        "task: chiron-phase8-smoke\nkind: decision\nstatus: open\nasked: now\nasked_by: worker\n"
        "answered:\nanswered_by:\n\n## QUESTION\nWhich marker?\n\n## WHAT WOULD SATISFY THIS\nA decision.\n"
        "\n## ANSWER\n_(unanswered)_\n",
        encoding="utf-8",
    )
    assist_path = f.root / "state/assists/chiron-phase8-smoke.md"
    assist_path.write_text(
        assist_path.read_text(encoding="utf-8")
        .replace("answered:\n", "answered: 2026-08-10T00:00:00Z\n")
        .replace("answered_by:\n", "answered_by: 8913126684\n")
        .replace("_(unanswered)_", "Use the marker after the canonical header."),
        encoding="utf-8",
    )
    first = f.run("python3", "scripts/project-reconcile.py", "resume-assist", "chiron-phase8-smoke", "104")
    second = f.run("python3", "scripts/project-reconcile.py", "resume-assist", "chiron-phase8-smoke", "104")
    events = []
    for line in (f.root / "state/events.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("event") == "assist-answer" and row.get("task") == "chiron-phase8-smoke":
            events.append(row)
    return (
        first.returncode == 0 and second.returncode == 0
        and fields(goal_path).get("status") == "active"
        and fields(task_path).get("status") == "queued"
        and len(events) == 1
        and events[0].get("project") == "chiron"
        and events[0].get("goal") == "goal-chiron-phase8-smoke"
        and fields(assist_path).get("status") == "answered"
        and fields(assist_path).get("resume_applied") == "1"
    )


def main() -> int:
    fixture = Fixture()
    tests = [test_fresh_plan, test_invalid_plan, test_approval, test_window_admission,
             test_pause_closes_window, test_assist_resume]
    failures = 0
    try:
        for label, test in zip(CONTROLS, tests):
            try:
                passed = bool(test(fixture))
            except Exception as exc:  # A falsifier reports failure; it never aborts later controls.
                print(f"diag  {label}: {exc}")
                passed = False
            if passed:
                print(f"ok    {label}")
            else:
                print(f"FAIL  {label}")
                failures += 1
    finally:
        fixture.close()
    print(f"phase8: {len(CONTROLS) - failures}/{len(CONTROLS)} controls passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

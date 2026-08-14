#!/usr/bin/env python3
"""Phase 8 lifecycle race and Lucas-instruction authorization red-to-green controls.

Focused falsifiers for the armed->open window race, the arm PAUSE recheck, and instruction
parsing that must refuse negated or opposite-operation text even when it names the same ids.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
CONTROLS = [
    "an affirmative approve command materializes exactly once while negated or reversed text is refused",
    "an affirmative window-open command arms exactly once while negated or opposite text is refused",
    "a requested window duration is bound into the arm replay identity and equality",
    "an affirmative window-close command closes once while open/authorize text is refused",
    "an armed/open window for another goal prevents a second window in the same project from opening",
    "a competing project window appearing before the arm commit is rechecked and refuses the arm",
    "a PAUSE lifted between arm authorization and arm commit is rechecked and refused",
    "a PAUSE observed between armed read and open commit is rechecked and refuses the open",
    "an authenticated close racing the armed->open commit is rechecked and refuses the open",
    "provider capability loss before the armed->open commit refuses the open",
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
        self.temp = Path(tempfile.mkdtemp(prefix="phase8-race-"))
        self.root = self.temp / "root"
        self.repo = self.temp / "chiron-repo"
        shutil.copytree(SOURCE / "scripts", self.root / "scripts")
        shutil.copytree(SOURCE / "schemas", self.root / "schemas")
        if os.name == "nt":
            (self.root / "scripts/fcntl.py").write_text(
                "LOCK_EX=2\nLOCK_NB=4\ndef flock(_file, _flags):\n    return None\n",
                encoding="utf-8",
            )
        (self.root / "scripts/provider-network.sh").write_text(
            "#!/usr/bin/env bash\n"
            "[ ! -f \"${RECURSION_ROOT:?}/state/test-provider-down\" ]\n",
            encoding="utf-8",
        )
        (self.root / "scripts/provider-network.sh").chmod(0o755)
        for relative in (
            "state/project-config", "state/pilots", "state/goals", "state/tasks",
            "state/plans/chiron", "state/pilot-windows", "state/instructions",
            "state/actions", "state/assists", "state/pilot-requests/chiron",
            "state/decision-queue/pending", "state/decision-queue/running",
            "state/decision-queue/succeeded", "state/decision-queue/failed",
            "state/deliveries", "state/notification-events", "state/.locks", "loop/logs",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        for relative in ("state/events.jsonl", "state/action-events.jsonl", "state/decisions.jsonl"):
            (self.root / relative).write_text("", encoding="utf-8")
        (self.root / ".env").write_text("", encoding="utf-8")
        self.env = os.environ.copy()
        self.env.update({
            "RECURSION_ROOT": str(self.root),
            "RECURSION_QUEUE_ACTUATION": "1",
            "RECURSION_INTAKE_ALLOW": "8913126684",
            "RECURSION_NO_NOTIFY": "1",
        })
        self._write_repo()
        self._write_project()
        self.write_instruction("101", "pilot-chiron", "propose the race plan")
        self.planner_plan = self._plan()
        self.plan = json.loads(json.dumps(self.planner_plan))
        self.plan_id = str(self.plan["id"])
        self.goal_id = str(self.plan["goal"]["id"])
        self.digest = canonical_digest(self.plan)

    def close(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def _write_repo(self) -> None:
        gate = self.repo / "user-client/render/tools/native-diff.cjs"
        impl = self.repo / "user-client/render/shade-tops.js"
        gate.parent.mkdir(parents=True, exist_ok=True)
        gate.write_text(
            "const fs=require('fs'); const s=fs.readFileSync('user-client/render/shade-tops.js','utf8'); "
            "process.exit(s.includes('shadeTops') ? 0 : 1);\n", encoding="utf-8",
        )
        impl.write_text("export const shadeTops = false;\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Phase 8 Race Test"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "phase8race@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-q", "-m", "fixture"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "branch", "-M", "main"], check=True)

    def _write_project(self) -> None:
        (self.root / "state/portfolio.tsv").write_text(
            "#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n"
            f"chiron\t{self.repo}\torigin\tmain\t-\t-\t10\tactive\n",
            encoding="utf-8",
        )
        config = {
            "schema_version": 1, "id": "chiron", "repo": str(self.repo),
            "remote": str(self.repo), "default_branch": "main", "deploy_key_ref": "-",
            "charter": "Build-verifiable Chiron application changes only.",
            "allowed_paths": ["user-client/render"],
            "required_non_goals": [
                "tests", "fixtures", "oracles", "baselines", "live-game-access",
                "credentials", "merge", "deploy",
            ],
            "topic": 10, "pilot_id": "pilot-chiron",
            "activation_gate": "clone-auth-freshness-v1",
            "notification_targets": ["project-topic:telegram:-100:10", "head-hermes:telegram:-100:1"],
            "goal_source": "state/goals", "status": "active",
        }
        pilot = {
            "schema_version": 1, "id": "pilot-chiron", "project_id": "chiron", "topic": 10,
            "charter": config["charter"], "model_policy": "project-pilot",
            "required_non_goals": config["required_non_goals"],
            "concurrency_limit": 1, "budget": {"max_inflight_workers": 1},
            "notification_targets": config["notification_targets"], "goal_source": "state/goals",
            "memory_key": "telegram-topic:10", "worktree_root": ".worktrees/chiron",
            "window_required": True, "status": "active",
        }
        self.write_json("state/project-config/chiron.json", config)
        self.write_json("state/pilots/pilot-chiron.json", pilot)

    @staticmethod
    def _plan() -> dict:
        return {
            "schema_version": 1,
            "id": "chiron-phase8-race-plan",
            "project_id": "chiron",
            "goal": {
                "id": "goal-chiron-phase8-race",
                "outcome": "Add one reversible build-verifiable Chiron race marker.",
                "acceptance_suite": "node user-client/render/tools/native-diff.cjs --metric",
                "gate_class": "heavy",
                "gate_files": ["user-client/render/tools/native-diff.cjs"],
                "controller_gate_files": [],
                "falsifier": "The exact candidate commit does not pass the clean Chiron build.",
                "budget": {
                    "max_concurrency": 1, "max_tokens": 12000, "max_cost_usd": 5,
                    "max_wall_clock_seconds": 3600, "max_task_attempts": 2,
                    "max_failures": 1, "max_review_queue": 1, "max_publish_attempts": 1,
                    "publication_required": True,
                },
            },
            "tasks": [{
                "id": "chiron-phase8-race-task", "intent": "Add the bounded race marker.",
                "dependencies": [], "allowed_paths": ["user-client/render"],
                "non_goals": ["learning-loop", "credentials", "merge", "deploy"],
                "worker_class": "claude", "engine": "claude", "model_alias": "sonnet-routine",
                "verifier_model_alias": "opus-review", "deadline_seconds": 1800,
                "verifier_deadline_seconds": 900, "network_policy": "provider-only",
                "evidence_contract": "worker-result-v1", "verification": "independent",
                "expected_change": "required", "gate_class": "heavy",
                "gate_files": ["user-client/render/tools/native-diff.cjs"],
                "controller_gate_files": [],
                "acceptance": "node user-client/render/tools/native-diff.cjs --metric",
            }],
        }

    def write_json(self, relative: str, value: dict) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        return path

    def write_instruction(self, iid: str, target: str, body: str) -> Path:
        path = self.root / "state/instructions" / f"{int(iid):08d}.md"
        topic = "1" if target == "head-hermes" else "10"
        project = "" if target == "head-hermes" else "chiron"
        pilot = "" if target == "head-hermes" else "pilot-chiron"
        path.write_text(
            f"schema_version: 1\nid: {iid}\nprincipal: 8913126684\ntopic: {topic}\n"
            f"project_id: {project}\npilot_id: {pilot}\nrouting_target: {target}\n"
            f"deduplication_key: fixture\nstatus: open\naction_ids:\n\n## INSTRUCTION\n{body}\n",
            encoding="utf-8",
        )
        return path

    def decision(self, *, verb: str, args: list[str], iid: str, actor: str, goal: str,
                 text: str, extra: dict | None = None) -> Path:
        value = {
            "schema_version": 1, "id": f"decision-{verb}-{iid}", "actor": actor,
            "verb": verb, "args": args, "arguments": args, "project": "chiron",
            "goal": goal, "goal_id": goal, "text": text, "instruction_id": iid,
            "why": "Phase 8 race control.", "reason": "Phase 8 race control.",
            "wrong_if": "Exact correlated state or evidence disagrees.",
            "idempotency_key": f"phase8:{verb}:{iid}", "status": "queued",
        }
        value.update(extra or {})
        return self.write_json(f"decision-{verb}-{iid}.json", value)

    def run(self, *args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess[str]:
        env = dict(self.env)
        if env_extra:
            env.update(env_extra)
        return subprocess.run(args, cwd=self.root, env=env, text=True, capture_output=True, check=False)

    def propose(self) -> bool:
        decision = self.decision(
            verb="pilot-plan-propose", args=["chiron", self.plan_id], iid="101",
            actor="pilot-chiron", goal=self.goal_id, text="Propose the race plan.",
            extra={"plan": self.plan},
        )
        result = self.run("python3", "scripts/project-pilot.py", "execute", str(decision))
        path = self.root / f"state/plans/chiron/{self.plan_id}.json"
        if result.returncode or not path.is_file():
            return False
        record = json.loads(path.read_text(encoding="utf-8"))
        self.plan = record.get("plan") or self.plan
        self.digest = str(record.get("plan_digest") or canonical_digest(self.plan))
        return record.get("status") == "proposed"

    def approve(self, iid: str, body: str) -> subprocess.CompletedProcess[str]:
        self.write_instruction(iid, "head-hermes", body)
        decision = self.decision(
            verb="pilot-plan-approve", args=["chiron", self.plan_id, self.digest], iid=iid,
            actor="head-hermes", goal=self.goal_id, text="Approve the race plan.",
        )
        return self.run("python3", "scripts/project-pilot.py", "execute", str(decision))

    def open_window(self, iid: str, body: str, window: str, seconds: str,
                    env_extra: dict | None = None) -> subprocess.CompletedProcess[str]:
        self.write_instruction(iid, "head-hermes", body)
        decision = self.decision(
            verb="pilot-window-open", args=["chiron", self.goal_id, window, seconds], iid=iid,
            actor="head-hermes", goal=self.goal_id, text="Authorize the race window.",
        )
        return self.run("python3", "scripts/project-pilot.py", "execute", str(decision),
                        env_extra=env_extra)

    def close_window(self, iid: str, body: str, window: str) -> subprocess.CompletedProcess[str]:
        self.write_instruction(iid, "head-hermes", body)
        decision = self.decision(
            verb="pilot-window-close", args=["chiron", window], iid=iid,
            actor="head-hermes", goal=self.goal_id, text="Revoke the race window.",
        )
        return self.run("python3", "scripts/project-pilot.py", "execute", str(decision))

    def propose_and_approve(self) -> bool:
        if not self.propose():
            return False
        if self.approve("102", f"approve {self.plan_id} {self.digest}").returncode:
            return False
        return (self.root / f"state/goals/{self.goal_id}.md").is_file()

    def materialize_and_arm(self, window: str) -> bool:
        if not self.propose_and_approve():
            print(f"diag  {window}: proposal/approval setup failed")
            return False
        (self.root / "state/PAUSE").write_text("phase8-race\n", encoding="utf-8")
        result = self.open_window("103", f"authorize {self.goal_id} {window} 900", window, "900")
        passed = result.returncode == 0 and (self.root / f"state/pilot-windows/{window}.json").is_file()
        if not passed:
            print(f"diag  {window}: arm rc={result.returncode} stderr={result.stderr.strip()!r}")
        return passed


def window_status(f: Fixture, window: str) -> str:
    path = f.root / "state/pilot-windows" / f"{window}.json"
    if not path.is_file():
        return "absent"
    return str(json.loads(path.read_text(encoding="utf-8")).get("status") or "")


def test_approve_guards() -> bool:
    f = Fixture()
    try:
        if not f.propose():
            return False
        negated = f.approve("102", f"do not approve {f.plan_id} {f.digest}")
        reversed_ = f.approve("103", f"reject {f.plan_id} {f.digest}")
        goal_path = f.root / f"state/goals/{f.goal_id}.md"
        if negated.returncode == 0 or reversed_.returncode == 0 or goal_path.is_file():
            return False
        control = f.approve("104", f"approve {f.plan_id} {f.digest}")
        return (
            control.returncode == 0 and goal_path.is_file()
            and fields(goal_path).get("status") == "active"
            and len(list((f.root / "state/goals").glob(f"{f.goal_id}.md"))) == 1
        )
    finally:
        f.close()


def test_open_guards() -> bool:
    f = Fixture()
    try:
        if not f.propose_and_approve():
            return False
        (f.root / "state/PAUSE").write_text("phase8-race\n", encoding="utf-8")
        window = "chiron-window-open"
        negated = f.open_window("105", f"do not authorize {f.goal_id} {window} 900", window, "900")
        opposite = f.open_window("106", f"close {window}", window, "900")
        if negated.returncode == 0 or opposite.returncode == 0 \
                or (f.root / f"state/pilot-windows/{window}.json").is_file():
            return False
        control = f.open_window("107", f"authorize {f.goal_id} {window} 900", window, "900")
        return control.returncode == 0 and window_status(f, window) == "armed"
    finally:
        f.close()


def test_duration_binding() -> bool:
    f = Fixture()
    try:
        window = "chiron-window-duration"
        if not f.materialize_and_arm(window):
            return False
        replay = f.open_window("103", f"authorize {f.goal_id} {window} 900", window, "900")
        path = f.root / f"state/pilot-windows/{window}.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        f.write_instruction("109", "head-hermes", f"authorize {f.goal_id} {window} 1800")
        decision = f.decision(
            verb="pilot-window-open", args=["chiron", f.goal_id, window, "1800"], iid="109",
            actor="head-hermes", goal=f.goal_id, text="Replay with a different duration.",
        )
        different = f.run("python3", "scripts/project-pilot.py", "execute", str(decision))
        passed = (
            replay.returncode == 0 and record.get("duration_seconds") == 900
            and different.returncode != 0
            and window_status(f, window) == "armed"
            and json.loads(path.read_text(encoding="utf-8")).get("duration_seconds") == 900
        )
        if not passed:
            print("diag  duration replay:", json.dumps({
                "replay_rc": replay.returncode, "replay_stderr": replay.stderr,
                "different_rc": different.returncode, "different_stderr": different.stderr,
                "record": record, "final_status": window_status(f, window),
            }, sort_keys=True))
        return passed
    finally:
        f.close()


def test_close_guards() -> bool:
    f = Fixture()
    try:
        window = "chiron-window-close"
        if not f.materialize_and_arm(window):
            return False
        opposite = f.close_window("111", f"open {window}", window)
        if opposite.returncode == 0 or window_status(f, window) != "armed":
            print("diag  close opposite:", json.dumps({
                "rc": opposite.returncode, "stderr": opposite.stderr,
                "status": window_status(f, window),
            }, sort_keys=True))
            return False
        control = f.close_window(
            "112", f"Close pilot window {window} in chiron.", window)
        passed = control.returncode == 0 and window_status(f, window) == "closed"
        if not passed:
            print("diag  close guard:", json.dumps({
                "opposite_rc": opposite.returncode, "opposite_stderr": opposite.stderr,
                "control_rc": control.returncode, "control_stderr": control.stderr,
                "status": window_status(f, window),
            }, sort_keys=True))
        return passed
    finally:
        f.close()


def test_arm_pause_lift_race() -> bool:
    f = Fixture()
    try:
        if not f.propose_and_approve():
            return False
        (f.root / "state/PAUSE").write_text("phase8-race\n", encoding="utf-8")
        window = "chiron-window-arm-race"
        result = f.open_window("113", f"authorize {f.goal_id} {window} 900", window, "900",
                               env_extra={"RECURSION_TEST_PAUSE_LIFT_BEFORE_ARM": "1"})
        return result.returncode != 0 \
            and not (f.root / f"state/pilot-windows/{window}.json").is_file()
    finally:
        f.close()


def test_arm_singleton_race() -> bool:
    f = Fixture()
    try:
        if not f.propose_and_approve():
            return False
        (f.root / "state/PAUSE").write_text("phase8-race\n", encoding="utf-8")
        window = "chiron-window-arm-singleton-race"
        result = f.open_window(
            "114", f"authorize {f.goal_id} {window} 900", window, "900",
            env_extra={"RECURSION_TEST_WINDOW_ARM_RACE": "singleton"},
        )
        competing = f.root / "state/pilot-windows/test-arm-race.json"
        return result.returncode != 0 \
            and not (f.root / f"state/pilot-windows/{window}.json").is_file() \
            and competing.is_file()
    finally:
        f.close()


def test_open_pause_race() -> bool:
    f = Fixture()
    try:
        window = "chiron-window-open-pause"
        if not f.materialize_and_arm(window):
            return False
        (f.root / "state/PAUSE").unlink(missing_ok=True)
        result = f.run("python3", "scripts/project-reconcile.py", "schedule",
                       env_extra={"RECURSION_TEST_WINDOW_OPEN_RACE": "pause"})
        return result.returncode == 0 and result.stdout.strip() == "0" \
            and window_status(f, window) == "armed" \
            and (f.root / "state/PAUSE").is_file()
    finally:
        f.close()


def test_open_close_race() -> bool:
    f = Fixture()
    try:
        window = "chiron-window-open-close"
        if not f.materialize_and_arm(window):
            return False
        (f.root / "state/PAUSE").unlink(missing_ok=True)
        result = f.run("python3", "scripts/project-reconcile.py", "schedule",
                       env_extra={"RECURSION_TEST_WINDOW_OPEN_RACE": "close"})
        passed = result.returncode == 0 and result.stdout.strip() == "0" \
            and window_status(f, window) == "closed"
        if not passed:
            print("diag  open/close race:", json.dumps({
                "rc": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
                "status": window_status(f, window),
            }, sort_keys=True))
        return passed
    finally:
        f.close()


def test_open_capability_loss_race() -> bool:
    f = Fixture()
    try:
        window = "chiron-window-open-capability"
        if not f.materialize_and_arm(window):
            return False
        (f.root / "state/PAUSE").unlink(missing_ok=True)
        result = f.run("python3", "scripts/project-reconcile.py", "schedule",
                       env_extra={"RECURSION_TEST_WINDOW_OPEN_RACE": "capability"})
        return result.returncode == 0 and result.stdout.strip() == "0" \
            and window_status(f, window) == "armed"
    finally:
        f.close()


def test_project_wide_window_singleton() -> bool:
    f = Fixture()
    try:
        window = "chiron-window-singleton"
        if not f.materialize_and_arm(window):
            return False
        competing = {
            "schema_version": 1, "id": "chiron-other-goal-window", "project_id": "chiron",
            "pilot_id": "pilot-chiron", "goal_id": "goal-chiron-other",
            "plan_id": "other-plan", "plan_digest": "f" * 64,
            "instruction_id": "999", "status": "armed",
            "expires_at_epoch": int(time.time()) + 900,
        }
        path = f.root / "state/pilot-windows/chiron-other-goal-window.json"
        path.write_text(json.dumps(competing), encoding="utf-8")
        (f.root / "state/PAUSE").unlink(missing_ok=True)
        result = f.run("python3", "scripts/project-reconcile.py", "schedule")
        return result.returncode == 0 and result.stdout.strip() == "0" \
            and window_status(f, window) == "armed"
    finally:
        f.close()


def main() -> int:
    tests = [
        test_approve_guards, test_open_guards, test_duration_binding, test_close_guards,
        test_project_wide_window_singleton,
        test_arm_singleton_race, test_arm_pause_lift_race,
        test_open_pause_race, test_open_close_race,
        test_open_capability_loss_race,
    ]
    failures = 0
    for label, test in zip(CONTROLS, tests):
        try:
            passed = bool(test())
        except Exception as exc:  # noqa: BLE001
            print(f"diag  {label}: {exc}")
            passed = False
        print(("ok    " if passed else "FAIL  ") + label)
        if not passed:
            failures += 1
    print(f"phase8-race: {len(CONTROLS) - failures}/{len(CONTROLS)} controls passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Phase 8 pre-worker contract rejection red-to-green controls.

Proves that a failed project-reconcile rejection preserves its exit status in work.sh (never a
false success) and that PAUSE, window revocation, transition-receipt I/O, and projection
failures leave task/goal never falsely terminal.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
CONTROLS = [
    "work.sh preserves the reconcile failure rc and never reports a false success",
    "a clean rejection blocks the task and goal exactly once (control)",
    "PAUSE rechecked before the rejection commit refuses and leaves task/goal non-terminal",
    "a revoked pilot window rechecked before the rejection commit refuses non-terminal",
    "a transition-receipt I/O failure refuses without falsely terminal task/goal",
    "a task/goal projection divergence refuses without falsely terminal state",
]

DIGEST = "a" * 64


def fields(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            result.setdefault(key.strip(), value.strip())
    return result


class RejectFixture:
    def __init__(self, *, window_required: bool = False) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="phase8-reject-"))
        self.root = self.temp / "root"
        self.window_required = window_required
        for relative in (
            "scripts", "state/tasks", "state/goals", "state/project-config", "state/pilots",
            "state/pilot-windows", "state/.locks", "loop/logs",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        for name in (
            "work.sh", "project-reconcile.py", "transition_receipt.py", "seed_contract.py",
            "jsonl_durable.py", "runtime-state.py",
        ):
            shutil.copy2(SOURCE / "scripts" / name, self.root / "scripts" / name)
        if os.name == "nt":
            (self.root / "scripts/fcntl.py").write_text(
                "LOCK_EX=2\nLOCK_NB=4\ndef flock(_file, _flags):\n    return None\n", encoding="utf-8",
            )
        (self.root / "state/events.jsonl").write_text("", encoding="utf-8")
        (self.root / ".env").write_text("", encoding="utf-8")
        (self.root / "state/portfolio.tsv").write_text(
            "#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n"
            f"rjct\t{self.root}\torigin\tmain\t-\t-\t10\tactive\n",
            encoding="utf-8",
        )
        config = {
            "schema_version": 1, "id": "rjct", "repo": str(self.root), "remote": "origin",
            "default_branch": "main", "deploy_key_ref": "-", "charter": "Rejection fixture.",
            "allowed_paths": ["app"], "topic": 10, "pilot_id": "pilot-rjct",
            "activation_gate": "clone-auth-freshness-v1", "notification_targets": [],
            "goal_source": "state/goals", "status": "active",
        }
        pilot = {
            "schema_version": 1, "id": "pilot-rjct", "project_id": "rjct",
            "charter": "Rejection fixture.", "model_policy": "project-pilot",
            "concurrency_limit": 1, "budget": {"max_inflight_workers": 1},
            "window_required": window_required, "status": "active",
        }
        self.write_json("state/project-config/rjct.json", config)
        self.write_json("state/pilots/pilot-rjct.json", pilot)
        self.write_goal()
        self.write_task()
        self.env = os.environ.copy()
        self.env.update({
            "RECURSION_ROOT": str(self.root), "RECURSION_INTAKE_ALLOW": "8913126684",
            "RECURSION_NO_NOTIFY": "1",
        })

    def write_json(self, relative: str, value: dict) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        return path

    def write_goal(self, status: str = "active") -> None:
        (self.root / "state/goals/goal-rjct.md").write_text(
            "schema_version: 1\nversion: 1\nid: goal-rjct\nproject_id: rjct\n"
            f"status: {status}\noutcome: Rejection fixture goal.\nacceptance_suite: test -s app/out\n"
            "falsifier: The fixture gate fails.\nbudget: {\"max_concurrency\":1,\"max_tokens\":100,\"max_cost_usd\":1,"
            "\"max_wall_clock_seconds\":3600,\"max_task_attempts\":1,\"max_failures\":0,"
            "\"max_review_queue\":1,\"max_publish_attempts\":1,\"publication_required\":false}\n",
            encoding="utf-8",
        )

    def write_task(self, status: str = "ready", extra: dict | None = None) -> None:
        header = {
            "schema_version": "1", "version": "1", "id": "rjct-task", "project_id": "rjct",
            "workstream": "rjct", "pilot_id": "pilot-rjct", "goal_id": "goal-rjct",
            "engine": "claude", "status": status,
        }
        header.update(extra or {})
        lines = "".join(f"{key}: {value}\n" for key, value in header.items())
        (self.root / "state/tasks/rjct-task.md").write_text(lines + "\nfixture intent\n", encoding="utf-8")

    def open_window(self) -> None:
        self.write_json("state/pilot-windows/rjct-window.json", {
            "schema_version": 1, "id": "rjct-window", "project_id": "rjct",
            "pilot_id": "pilot-rjct", "goal_id": "goal-rjct", "status": "open",
            "expires_at_epoch": int(time.time()) + 600, "max_inflight_workers": 1,
        })

    def close(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def run(self, *args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess[str]:
        env = dict(self.env)
        if env_extra:
            env.update(env_extra)
        return subprocess.run(args, cwd=self.root, env=env, text=True, capture_output=True, check=False)

    def reject(self, category: str = "acceptance-missing", env_extra: dict | None = None):
        return self.run("python3", "scripts/project-reconcile.py", "reject-task-contract",
                        "rjct-task", category, DIGEST, env_extra=env_extra)

    def bash(self) -> str:
        if os.name == "nt":
            return str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe")
        return "bash"

    def task_status(self) -> str:
        return fields(self.root / "state/tasks/rjct-task.md").get("status", "")

    def goal_status(self) -> str:
        return fields(self.root / "state/goals/goal-rjct.md").get("status", "")


def test_work_rc_preserved() -> bool:
    f = RejectFixture(window_required=False)
    try:
        result = f.run(f.bash(), "scripts/work.sh", "rjct-task",
                       env_extra={"RECURSION_TRANSITION_FAILPOINT": "receipt-fsync"})
        # A reconcile failure must surface as a non-zero exit, never a false success, and it
        # must never leave the task/goal falsely terminal.
        return result.returncode != 0 \
            and f.task_status() in {"ready", "queued"} \
            and f.goal_status() == "active"
    finally:
        f.close()


def test_clean_rejection_control() -> bool:
    f = RejectFixture(window_required=False)
    try:
        result = f.run(f.bash(), "scripts/work.sh", "rjct-task")
        return result.returncode == 78 \
            and f.task_status() == "blocked" \
            and f.goal_status() == "blocked"
    finally:
        f.close()


def test_pause_rejection() -> bool:
    f = RejectFixture(window_required=False)
    try:
        result = f.reject(env_extra={"RECURSION_TEST_PAUSE_BEFORE_CONTRACT_COMMIT": "1"})
        return result.returncode != 0 \
            and f.task_status() in {"ready", "queued"} \
            and f.goal_status() == "active"
    finally:
        f.close()


def test_window_revocation_rejection() -> bool:
    f = RejectFixture(window_required=True)
    try:
        # No open window: the rejection precondition rechecks exact open-window authority and
        # refuses before the task/goal are made terminal.
        result = f.reject()
        return result.returncode != 0 \
            and f.task_status() in {"ready", "queued"} \
            and f.goal_status() == "active"
    finally:
        f.close()


def test_receipt_io_rejection() -> bool:
    f = RejectFixture(window_required=False)
    try:
        result = f.reject(env_extra={"RECURSION_TRANSITION_FAILPOINT": "receipt-fsync"})
        return result.returncode != 0 \
            and f.task_status() in {"ready", "queued"} \
            and f.goal_status() == "active"
    finally:
        f.close()


def test_projection_divergence_rejection() -> bool:
    f = RejectFixture(window_required=False)
    try:
        # A non-pre-worker projection (task already running) must refuse the compare-and-swap.
        f.write_task(status="running")
        result = f.reject()
        return result.returncode != 0 \
            and f.task_status() == "running" \
            and f.goal_status() == "active"
    finally:
        f.close()


def main() -> int:
    tests = [
        test_work_rc_preserved, test_clean_rejection_control, test_pause_rejection,
        test_window_revocation_rejection, test_receipt_io_rejection,
        test_projection_divergence_rejection,
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
    print(f"phase8-reject: {len(CONTROLS) - failures}/{len(CONTROLS)} controls passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

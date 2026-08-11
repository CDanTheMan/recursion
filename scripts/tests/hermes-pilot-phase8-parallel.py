#!/usr/bin/env python3
"""Phase 8 global/per-project parallel admission control (inert worker fixture)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def fixture() -> tuple[Path, dict[str, str]]:
    root = Path(tempfile.mkdtemp(prefix="phase8-parallel-"))
    shutil.copytree(SOURCE / "scripts", root / "scripts")
    shutil.copytree(SOURCE / "schemas", root / "schemas")
    if os.name == "nt":
        (root / "scripts/fcntl.py").write_text(
            "LOCK_EX=2\nLOCK_NB=4\ndef flock(_file, _flags):\n    return None\n", encoding="utf-8"
        )
    for relative in (
        "state/actions", "state/tasks", "state/goals", "state/project-config", "state/pilots",
        "state/pilot-windows", "state/decision-queue/pending", "state/decision-queue/running",
        "state/decision-queue/succeeded", "state/decision-queue/failed", "state/.locks", "loop/logs",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)
    for relative in ("state/decisions.jsonl", "state/action-events.jsonl", "state/events.jsonl"):
        (root / relative).write_text("", encoding="utf-8")
    (root / ".env").write_text("", encoding="utf-8")
    expiry = int(time.time()) + 600
    for project in ("alpha", "beta"):
        config = {
            "schema_version": 1, "id": project, "repo": f"/fixture/{project}", "remote": "origin",
            "default_branch": "main", "deploy_key_ref": "-", "charter": "Parallel fixture.",
            "allowed_paths": ["app"], "topic": 1 if project == "alpha" else 2,
            "pilot_id": f"pilot-{project}", "activation_gate": "clone-auth-freshness-v1",
            "notification_targets": [], "goal_source": "state/goals", "status": "active",
        }
        pilot = {
            "schema_version": 1, "id": f"pilot-{project}", "project_id": project,
            "charter": "Parallel fixture.", "model_policy": "project-pilot", "concurrency_limit": 1,
            "budget": {"max_inflight_workers": 1}, "window_required": True, "status": "active",
        }
        write_json(root / f"state/project-config/{project}.json", config)
        write_json(root / f"state/pilots/pilot-{project}.json", pilot)
        write_json(root / f"state/pilot-windows/window-{project}.json", {
            "schema_version": 1, "id": f"window-{project}", "project_id": project,
            "pilot_id": f"pilot-{project}", "goal_id": f"goal-{project}", "status": "open",
            "expires_at_epoch": expiry, "max_inflight_workers": 1,
        })
        (root / f"state/goals/goal-{project}.md").write_text(
            f"schema_version: 1\nid: goal-{project}\nproject_id: {project}\nstatus: active\n",
            encoding="utf-8",
        )
    tasks = {"alpha-1": "alpha", "alpha-2": "alpha", "beta-1": "beta"}
    for task, project in tasks.items():
        (root / f"state/tasks/{task}.md").write_text(
            f"schema_version: 1\nid: {task}\nproject_id: {project}\nproject: {project}\n"
            f"pilot_id: pilot-{project}\ngoal_id: goal-{project}\nacceptance: fixture-gate\nstatus: queued\n",
            encoding="utf-8",
        )
        decision = {
            "schema_version": 1, "id": f"decision-{task}", "actor": f"pilot-{project}",
            "decision_source": "project-reconciler", "routed_decider": f"pilot-{project}",
            "verb": "work", "args": [task], "arguments": [task], "project": project,
            "goal": f"goal-{project}", "goal_id": f"goal-{project}",
            "why": "parallel admission fixture", "reason": "parallel admission fixture",
            "wrong_if": "worker bounds overlap incorrectly", "idempotency_key": f"parallel:{task}",
            "status": "queued",
        }
        normalized = subprocess.run(
            ["python3", str(root / "scripts/decision-queue.py"), "normalize"],
            input=json.dumps(decision), env={**os.environ, "RECURSION_ROOT": str(root)},
            text=True, capture_output=True, check=False,
        )
        if normalized.returncode:
            raise RuntimeError(f"decision normalization failed: {normalized.stderr.strip()}")
        enqueued = subprocess.run(
            ["python3", str(root / "scripts/decision-queue.py"), "enqueue"],
            input=normalized.stdout, env={**os.environ, "RECURSION_ROOT": str(root)},
            text=True, capture_output=True, check=False,
        )
        if enqueued.returncode:
            raise RuntimeError(f"decision enqueue failed: {enqueued.stderr.strip()}")
    env = os.environ.copy()
    env.update({"RECURSION_ROOT": str(root), "RECURSION_PILOT_GLOBAL_CONCURRENCY": "2",
                "RECURSION_QUEUE_ACTUATION": "1", "RECURSION_NO_NOTIFY": "1"})
    return root, env


def queue_only(root: Path, env: dict[str, str]) -> bool:
    queue = root / "scripts/decision-queue.py"
    first = subprocess.run(["python3", str(queue), "claim-pending", "--kind", "work"],
                           env=env, text=True, capture_output=True, check=False)
    second = subprocess.run(["python3", str(queue), "claim-pending", "--kind", "work",
                             "--exclude-project", "alpha"], env=env, text=True,
                            capture_output=True, check=False)
    return first.returncode == 0 and "alpha-1" in first.stdout and second.returncode == 0 and "beta-1" in second.stdout


def linux_overlap(root: Path, env: dict[str, str]) -> bool:
    log = root / "state/worker-times.tsv"
    (root / "scripts/work.sh").write_text(
        "#!/usr/bin/env bash\nset -uo pipefail\n"
        "printf 'start\\t%s\\t%s\\n' \"$1\" \"$(date +%s%N)\" >> \"$RECURSION_ROOT/state/worker-times.tsv\"\n"
        "for _fixture_wait in $(seq 1 100); do\n"
        "  [ \"$(grep -c '^start' \"$RECURSION_ROOT/state/worker-times.tsv\")\" -ge 2 ] && break\n"
        "  sleep 0.02\n"
        "done\n"
        "sleep 0.10\n"
        "printf 'end\\t%s\\t%s\\n' \"$1\" \"$(date +%s%N)\" >> \"$RECURSION_ROOT/state/worker-times.tsv\"\n",
        encoding="utf-8",
    )
    (root / "scripts/work.sh").chmod(0o755)
    run = subprocess.run(["bash", str(root / "scripts/conduct-hermes.sh")], cwd=root, env=env,
                         text=True, capture_output=True, check=False, timeout=30)
    if run.returncode or not log.is_file():
        return False
    times: dict[str, dict[str, int]] = {}
    for line in log.read_text(encoding="utf-8").splitlines():
        kind, task, stamp = line.split("\t")
        times.setdefault(task, {})[kind] = int(stamp)
    if set(times) != {"alpha-1", "alpha-2", "beta-1"}:
        return False
    overlap = times["alpha-1"]["start"] < times["beta-1"]["end"] \
        and times["beta-1"]["start"] < times["alpha-1"]["end"]
    isolated = times["alpha-2"]["start"] >= times["alpha-1"]["end"]
    decisions = list((root / "state/decision-queue/succeeded").glob("*.json"))
    actions = [json.loads(path.read_text(encoding="utf-8")) for path in (root / "state/actions").glob("*.json")]
    return overlap and isolated and len(decisions) == 3 and len(actions) == 3 \
        and all(row.get("status") == "succeeded" and row.get("attempts") == 1 for row in actions)


def main() -> int:
    root, env = fixture()
    try:
        if os.name == "nt":
            passed = queue_only(root, env)
            label = "parallel queue skips a project at capacity (Linux overlap run still required)"
        else:
            passed = linux_overlap(root, env)
            label = "two projects overlap under global=2 while one project remains at capacity=1"
        print(("ok    " if passed else "FAIL  ") + label)
        return 0 if passed else 1
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

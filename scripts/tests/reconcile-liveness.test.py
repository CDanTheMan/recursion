#!/usr/bin/env python3
"""Linux controls for semantic reconciliation fingerprints."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]


def load_reconcile():
    spec = importlib.util.spec_from_file_location(
        "project_reconcile_liveness", SOURCE / "scripts/project-reconcile.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load project-reconcile.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    if os.name == "nt":
        print("reconcile-liveness: SKIP (Linux process-liveness control)")
        return 0
    reconcile = load_reconcile()
    with tempfile.TemporaryDirectory(prefix="reconcile-liveness-") as temporary:
        root = Path(temporary)
        for relative in ("state/goals", "state/tasks", "state/runs", "state/actions",
                         "state/deliveries"):
            (root / relative).mkdir(parents=True)
        goal = root / "state/goals/g.md"
        task = root / "state/tasks/t.md"
        run = root / "state/runs/t-impl.json"
        goal.write_text(
            "id: g\nproject_id: p\nstatus: active\nevent_seq: 1\n"
            "last_transition_id: transition-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n",
            encoding="utf-8",
        )
        task.write_text(
            "id: t\ngoal_id: g\nproject_id: p\nstatus: running\nlease_expires: 2000\n"
            "event_seq: 1\nlast_transition_id: transition-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n",
            encoding="utf-8",
        )
        write_json(run, {
            "schema_version": 1, "id": "t-impl", "task_id": "t", "status": "running",
            "pid": os.getpid(), "heartbeat_at": "2026-08-10T00:00:00Z",
            "lease_expires": "1970-01-01T00:33:20Z", "result": {}, "usage": {},
        })
        config = {"repo": str(root / "absent-repo")}
        before = reconcile.snapshot_digest(root, config, "g", observed_epoch=1000)

        task.write_text(
            "id: t\ngoal_id: g\nproject_id: p\nstatus: running\nlease_expires: 3000\n"
            "event_seq: 2\nlast_transition_id: transition-cccccccccccccccccccccccccccccccc\n",
            encoding="utf-8",
        )
        value = json.loads(run.read_text(encoding="utf-8"))
        value.update(heartbeat_at="2026-08-10T00:00:05Z",
                     lease_expires="1970-01-01T00:50:00Z")
        write_json(run, value)
        heartbeat = reconcile.snapshot_digest(root, config, "g", observed_epoch=1000)
        if heartbeat != before:
            raise AssertionError("heartbeat-only lease and witness churn changed the fingerprint")
        print("ok    heartbeat-only lease and receipt-witness churn has one stable fingerprint")

        expired = reconcile.snapshot_digest(root, config, "g", observed_epoch=4000)
        if expired == heartbeat:
            raise AssertionError("lease expiry did not change the semantic fingerprint")
        print("ok    a lease crossing its expiry changes the fingerprint once")

        sleeper = subprocess.Popen(["sleep", "30"])
        try:
            value.update(pid=sleeper.pid, lease_expires="1970-01-01T01:23:20Z")
            write_json(run, value)
            live = reconcile.snapshot_digest(root, config, "g", observed_epoch=1000)
            sleeper.terminate(); sleeper.wait(timeout=5)
            dead = reconcile.snapshot_digest(root, config, "g", observed_epoch=1000)
        finally:
            if sleeper.poll() is None:
                sleeper.terminate(); sleeper.wait(timeout=5)
        if live == dead:
            raise AssertionError("worker death did not change the semantic fingerprint")
        print("ok    worker liveness changes the fingerprint without heartbeat amplification")

        text = task.read_text(encoding="utf-8").replace("status: running", "status: passed")
        task.write_text(text, encoding="utf-8")
        semantic = reconcile.snapshot_digest(root, config, "g", observed_epoch=1000)
        if semantic == dead:
            raise AssertionError("semantic task state did not change the fingerprint")
        print("ok    semantic task state still mints a distinct reconciliation identity")
        print("reconcile-liveness: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

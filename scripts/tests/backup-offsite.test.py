#!/usr/bin/env python3
"""Hermetic encrypted-backup contract and disposable restore-drill controls."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "scripts/backup-offsite.py"
RUNTIME = ROOT / "scripts/runtime-state.py"


def run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, env=env)


def main() -> int:
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        print(("ok - " if condition else "FAIL - ") + label)
        if not condition:
            failures.append(label)

    policy = run("validate")
    check(policy.returncode == 0, "shipped backup policy validates",)
    check('"enabled": false' in policy.stdout, "shipped backup policy is disabled",)
    plan = run("plan")
    check(plan.returncode == 0, "backup plan is generated without side effects")
    check('"execution": "human-deployment-only"' in plan.stdout, "plan marks human deployment boundary")
    check('daily=14' in plan.stdout and 'age' in plan.stdout and 'sftp' in plan.stdout,
          "plan carries encryption, transfer, and retention stages")

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        fixture = base / "fixture"
        (fixture / "state/.locks").mkdir(parents=True)
        (fixture / "state/actions").mkdir()
        (fixture / "state/PAUSE").write_text("paused for test\n", encoding="utf-8")
        (fixture / "state/events.jsonl").write_text("event\n", encoding="utf-8")
        snapshot = base / "snapshot"
        env = dict(os.environ, RECURSION_ROOT=str(fixture))
        backup = subprocess.run([sys.executable, str(RUNTIME), "backup", str(snapshot)],
                                capture_output=True, text=True, env=env)
        check(backup.returncode == 0, "runtime snapshot fixture is created")
        (fixture / "state/goals").mkdir()
        (fixture / "state/goals/extra.md").write_text("not in snapshot\n", encoding="utf-8")
        drill = run("restore-drill", "--root", str(fixture), "--snapshot", str(snapshot))
        check(drill.returncode == 0, f"restore drill reconstructs snapshot ({drill.stderr.strip()})")
        if drill.returncode == 0:
            result = json.loads(drill.stdout)
            check(result["status"] == "passed" and result["temporary_target"] == "discarded",
                  "restore drill discards its temporary target")
    if failures:
        print(f"backup-offsite.test: {len(failures)} FAILED")
        return 1
    print("backup-offsite.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

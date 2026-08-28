#!/usr/bin/env python3
"""Hermetic controls for engine-scorecard.py's Phase 3 (D-016) join preference:
a run-evidence record that carries its own `engine` (assignment-native) is bucketed on that
value directly; only a record without one falls back to joining the CURRENT task header via
task_id + role, exactly as before (legacy behavior preserved).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
SCRIPTS = SOURCE / "scripts"
SCORECARD = SCRIPTS / "engine-scorecard.py"

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


TASK_LEGACY = """id: task-legacy
engine: claude
verifier_engine: claude
model_alias: sonnet-routine
verifier_model_alias: opus-review
status: passed

body
"""


def bucket(rows: list[dict], engine: str, alias: str) -> dict | None:
    for row in rows:
        if row["engine"] == engine and row["alias"] == alias:
            return row
    return None


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "state" / "tasks").mkdir(parents=True)
        (root / "state" / "runs").mkdir(parents=True)
        (root / "state" / "tasks" / "task-legacy.md").write_text(TASK_LEGACY, encoding="utf-8")

        # Legacy run evidence: no top-level "engine" -> must fall back to the task-header join.
        (root / "state" / "runs" / "run-legacy.json").write_text(json.dumps({
            "schema_version": 1, "id": "run-legacy", "task_id": "task-legacy", "role": "implementer",
            "model_alias": "sonnet-routine", "status": "succeeded", "outcome": "worker-complete",
        }), encoding="utf-8")

        # Assignment-native run evidence for the SAME task, but bound to a DIFFERENT engine than
        # the (mutable) task header currently says -- proves the run's own value wins.
        (root / "state" / "runs" / "run-assigned.json").write_text(json.dumps({
            "schema_version": 1, "id": "run-assigned", "task_id": "task-legacy", "role": "implementer",
            "model_alias": "sonnet-routine", "status": "succeeded", "outcome": "worker-complete",
            "engine": "hermes", "assignment_digest": "e" * 64,
        }), encoding="utf-8")

        # An assignment-native run whose task_id does not resolve at all: must NOT count toward
        # unknown_task_runs, because its engine is attributable directly off the record.
        (root / "state" / "runs" / "run-orphan-assigned.json").write_text(json.dumps({
            "schema_version": 1, "id": "run-orphan-assigned", "task_id": "task-does-not-exist",
            "role": "implementer", "model_alias": "legacy", "status": "succeeded",
            "outcome": "worker-complete", "engine": "claude",
        }), encoding="utf-8")

        # A legacy run whose task_id does not resolve: SHOULD still count toward unknown_task_runs.
        (root / "state" / "runs" / "run-orphan-legacy.json").write_text(json.dumps({
            "schema_version": 1, "id": "run-orphan-legacy", "task_id": "task-also-missing",
            "role": "implementer", "model_alias": "legacy", "status": "failed", "outcome": "error",
        }), encoding="utf-8")

        out_json = root / "scorecard.json"
        result = subprocess.run(
            [sys.executable, str(SCORECARD), "--root", str(root), "--json", str(out_json)],
            capture_output=True, text=True,
        )
        check(result.returncode == 0, f"engine-scorecard exits 0 (got {result.returncode}, stderr={result.stderr!r})")
        data = json.loads(out_json.read_text(encoding="utf-8"))
        rows = data["rows"]

        legacy_bucket = bucket(rows, "claude", "sonnet-routine")
        check(legacy_bucket is not None, "the legacy run (no record.engine) lands in the (claude, sonnet-routine) bucket via the task-header join")
        if legacy_bucket is not None:
            check(legacy_bucket["runs_by_role"].get("implementer", 0) >= 1,
                  "the legacy run is counted as an implementer run in its joined bucket")

        assigned_bucket = bucket(rows, "hermes", "sonnet-routine")
        check(assigned_bucket is not None,
              "the assignment-native run (record.engine='hermes') lands in the (hermes, sonnet-routine) bucket, NOT (claude, ...)")
        claude_bucket_run_count = (legacy_bucket or {}).get("runs_by_role", {}).get("implementer", 0)
        check(claude_bucket_run_count == 1,
              "the (claude, sonnet-routine) bucket counts only the legacy run, not the hermes-assigned one")

        orphan_assigned_bucket = bucket(rows, "claude", "legacy")
        check(orphan_assigned_bucket is not None,
              "an assignment-native run with an unresolvable task_id still lands in its own (engine, alias) bucket")

        check(data["unknown_task_runs"] == 1,
              f"only the LEGACY orphaned run (no record.engine) counts toward unknown_task_runs (got {data['unknown_task_runs']})")

    if failures:
        print(f"engine-scorecard-assignment.test: {len(failures)} FAILED")
        return 1
    print("engine-scorecard-assignment.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

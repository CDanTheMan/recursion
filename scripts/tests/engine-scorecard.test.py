#!/usr/bin/env python3
"""Fixture-driven tests for scripts/engine-scorecard.py.

Builds synthetic state/tasks, state/events.jsonl, and state/runs trees under a tempfile
root and runs the real CLI against them as a subprocess (same convention as
resolve-engine.test.py). No dependency on the real box's state/.

run: python scripts/tests/engine-scorecard.test.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
SCORECARD = SOURCE / "scripts" / "engine-scorecard.py"

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def run_scorecard(root: Path, *extra: str) -> subprocess.CompletedProcess:
    argv = [sys.executable, str(SCORECARD), "--root", str(root), *extra]
    return subprocess.run(argv, capture_output=True, text=True)


TASK_ALPHA = """schema_version: 1
id: task-alpha
workstream: demo
goal_id: goal-demo
dependencies:
goal: demo task alpha
engine: claude
model_alias: sonnet-routine
verifier_engine: claude
verifier_model_alias: opus-review
acceptance: true
workdir: .
allowed_paths: .
non_goals: none
autonomy: auto
status: passed

Body text is never a header field, even a line shaped like `engine: not-this`.
"""

TASK_BETA = """schema_version: 1
id: task-beta
workstream: demo
goal_id: goal-demo
dependencies:
goal: demo task beta
engine: gemini
model_alias: sonnet-routine
verifier_engine: gemini
verifier_model_alias: opus-review
acceptance: true
workdir: .
allowed_paths: .
non_goals: none
autonomy: auto
status: proposed

Beta has one still-running implementer run and no verifier run yet.
"""

TASK_MALFORMED = "# not a task\nthis file has no id: field at all\n"


def build_full_fixture(root: Path) -> None:
    tasks_dir = root / "state" / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "task-alpha.md").write_text(TASK_ALPHA, encoding="utf-8")
    (tasks_dir / "task-beta.md").write_text(TASK_BETA, encoding="utf-8")
    (tasks_dir / "broken.md").write_text(TASK_MALFORMED, encoding="utf-8")

    events = [
        {"schema_version": 1, "ts": "2026-08-06T09:00:00Z", "event": "escalation-open",
         "task": "task-alpha", "project": "demo", "goal": "goal-demo", "pid": 1, "detail": "attributable"},
        {"schema_version": 1, "ts": "2026-08-06T09:05:00Z", "event": "escalation-open",
         "task": "", "project": "demo", "goal": "", "pid": 1, "detail": "canonical esc-record shape: task field empty"},
        {"schema_version": 1, "ts": "2026-08-06T09:10:00Z", "event": "start",
         "task": "task-alpha", "project": "demo", "goal": "goal-demo", "pid": 1, "detail": ""},
    ]
    lines = [json.dumps(e) for e in events]
    lines.append("{this is not valid json")
    (root / "state").mkdir(exist_ok=True)
    (root / "state" / "events.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    runs_dir = root / "state" / "runs"
    runs_dir.mkdir(parents=True)

    def run_record(**kw):
        base = {"schema_version": 1, "worker": "x", "worktree": "x", "base_commit": "x",
                "pid": 1, "process_group": 1, "lease_expires": "0", "deadline": "0",
                "deadline_epoch": 0, "network_policy": "provider-only", "heartbeat_at": "now",
                "log": "x", "usage": {}, "result": {}, "changed_files": []}
        base.update(kw)
        return base

    # task-alpha implementer: a retry (2 runs), first fails, second succeeds.
    (runs_dir / "task-alpha-impl-a1.json").write_text(json.dumps(run_record(
        id="task-alpha-impl-a1", task_id="task-alpha", role="implementer", model_alias="sonnet-routine",
        status="failed", outcome="gate-failed", exit_code=1,
        started_at="2026-08-06T09:00:00Z", finished_at="2026-08-06T09:01:40Z",
    )), encoding="utf-8")
    (runs_dir / "task-alpha-impl-a2.json").write_text(json.dumps(run_record(
        id="task-alpha-impl-a2", task_id="task-alpha", role="implementer", model_alias="sonnet-routine",
        status="succeeded", outcome="candidate-committed", exit_code=0,
        started_at="2026-08-06T09:02:00Z", finished_at="2026-08-06T09:05:20Z",
    )), encoding="utf-8")
    # task-alpha verifier: one successful run.
    (runs_dir / "task-alpha-verify-v1.json").write_text(json.dumps(run_record(
        id="task-alpha-verify-v1", task_id="task-alpha", role="verifier", model_alias="opus-review",
        status="succeeded", outcome="verified", exit_code=0,
        started_at="2026-08-06T09:06:00Z", finished_at="2026-08-06T09:06:50Z",
    )), encoding="utf-8")
    # task-beta implementer: still running, no finished_at -> excluded from wall-clock stats.
    (runs_dir / "task-beta-impl-b1.json").write_text(json.dumps(run_record(
        id="task-beta-impl-b1", task_id="task-beta", role="implementer", model_alias="sonnet-routine",
        status="running", outcome="", exit_code=None,
        started_at="2026-08-06T09:00:00Z", finished_at=None,
    )), encoding="utf-8")
    # A run whose task id does not exist in state/tasks at all.
    (runs_dir / "ghost-impl-g1.json").write_text(json.dumps(run_record(
        id="ghost-impl-g1", task_id="ghost-task", role="implementer", model_alias="sonnet-routine",
        status="failed", outcome="timeout", exit_code=124,
        started_at="2026-08-06T09:00:00Z", finished_at="2026-08-06T09:10:00Z",
    )), encoding="utf-8")
    # Malformed run records: not JSON, and JSON missing required identity fields.
    (runs_dir / "malformed-not-json.json").write_text("{not json", encoding="utf-8")
    (runs_dir / "malformed-missing-fields.json").write_text(json.dumps({"id": "x"}), encoding="utf-8")


def test_full_fixture() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build_full_fixture(root)
        json_path = root / "out.json"
        result = run_scorecard(root, "--json", str(json_path))
        check(result.returncode == 0, f"full fixture exits 0 (got {result.returncode}, stderr={result.stderr!r})")
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            check(False, f"--json output parses as JSON ({exc})")
            return {}
        check(True, "--json output parses as JSON")

        ev = data["evidence"]
        check(ev["tasks"]["parsed"] == 2, f"2 valid tasks parsed (got {ev['tasks']['parsed']})")
        check(ev["tasks"]["skipped"] == 1, f"1 malformed task file skipped (got {ev['tasks']['skipped']})")
        check(ev["events"]["parsed"] == 3, f"3 valid events parsed (got {ev['events']['parsed']})")
        check(ev["events"]["skipped"] == 1, f"1 malformed event line skipped (got {ev['events']['skipped']})")
        check(ev["events"]["max_ts"] == "2026-08-06T09:10:00Z", f"max ts tracked (got {ev['events']['max_ts']!r})")
        check(ev["runs"]["parsed"] == 5, f"5 valid run records parsed (got {ev['runs']['parsed']})")
        check(ev["runs"]["skipped"] == 2, f"2 malformed run records skipped (got {ev['runs']['skipped']})")
        check(data["unknown_task_runs"] == 1, f"1 run attributed to an unknown task (got {data['unknown_task_runs']})")
        check(data["unattributed_escalations"] == 1,
              f"1 escalation with empty task field is unattributed (got {data['unattributed_escalations']})")

        rows = {(r["engine"], r["alias"]): r for r in data["rows"]}
        check(("claude", "sonnet-routine") in rows, "row exists for (claude, sonnet-routine)")
        check(("claude", "opus-review") in rows, "row exists for (claude, opus-review)")
        check(("gemini", "sonnet-routine") in rows, "row exists for (gemini, sonnet-routine)")
        check(("gemini", "opus-review") in rows, "row exists for (gemini, opus-review)")

        claude_sonnet = rows.get(("claude", "sonnet-routine"), {})
        check(claude_sonnet.get("task_status") == {"passed": 1},
              f"claude/sonnet-routine task status = passed:1 (got {claude_sonnet.get('task_status')})")
        check(claude_sonnet.get("runs_by_role") == {"implementer": 2},
              f"claude/sonnet-routine has 2 implementer runs (got {claude_sonnet.get('runs_by_role')})")
        check(claude_sonnet.get("retries") == 1,
              f"claude/sonnet-routine retry count = 1 (got {claude_sonnet.get('retries')})")
        check(claude_sonnet.get("outcomes") == {"fail": 1, "pass": 1},
              f"claude/sonnet-routine outcomes = fail:1 pass:1 (got {claude_sonnet.get('outcomes')})")
        check(claude_sonnet.get("escalations") == {"escalation-open": 1},
              f"claude/sonnet-routine has 1 attributable escalation (got {claude_sonnet.get('escalations')})")
        wc = claude_sonnet.get("wallclock_seconds", {})
        check(wc.get("n") == 2, f"claude/sonnet-routine wall-clock n=2 finished runs (got {wc.get('n')})")
        check(wc.get("total") == 100 + 200, f"claude/sonnet-routine wall-clock total=300s (got {wc.get('total')})")
        check(wc.get("median") == 150, f"claude/sonnet-routine wall-clock median=150s (got {wc.get('median')})")

        claude_opus = rows.get(("claude", "opus-review"), {})
        check(claude_opus.get("verifier_arms") == 1,
              f"claude/opus-review has 1 verifier-arm task (got {claude_opus.get('verifier_arms')})")
        check(claude_opus.get("runs_by_role") == {"verifier": 1},
              f"claude/opus-review has 1 verifier run (got {claude_opus.get('runs_by_role')})")
        check(claude_opus.get("outcomes") == {"pass": 1},
              f"claude/opus-review outcome = pass:1 (got {claude_opus.get('outcomes')})")

        gemini_sonnet = rows.get(("gemini", "sonnet-routine"), {})
        check(gemini_sonnet.get("task_status") == {"proposed": 1},
              f"gemini/sonnet-routine task status = proposed:1 (got {gemini_sonnet.get('task_status')})")
        check(gemini_sonnet.get("outcomes") == {"running": 1},
              f"gemini/sonnet-routine outcome = running:1 (got {gemini_sonnet.get('outcomes')})")
        check(gemini_sonnet.get("wallclock_seconds", {}).get("n") == 0,
              "gemini/sonnet-routine has no finished-run durations (still running)")

        unknown_row = rows.get(("(unknown-task)", "sonnet-routine"))
        check(unknown_row is not None, "unknown-task run is grouped under (unknown-task) with its own alias")
        if unknown_row is not None:
            check(unknown_row.get("outcomes") == {"timeout": 1},
                  f"unknown-task run categorized as timeout (got {unknown_row.get('outcomes')})")

        report = result.stdout
        check("Engine Scorecard" in report, "markdown report has a title")
        check(f"{ev['tasks']['parsed']} tasks" in report, "markdown evidence line reports task count")
        line_count = len(report.splitlines())
        check(line_count <= 60, f"report fits one page (<= 60 lines, got {line_count})")
        return data


def test_json_stable(fixture_data: dict) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build_full_fixture(root)
        json_a = root / "a.json"
        json_b = root / "b.json"
        r1 = run_scorecard(root, "--json", str(json_a))
        r2 = run_scorecard(root, "--json", str(json_b))
        check(r1.returncode == 0 and r2.returncode == 0, "two runs against identical fixture both exit 0")
        text_a = json_a.read_text(encoding="utf-8")
        text_b = json_b.read_text(encoding="utf-8")
        check(text_a == text_b, "--json output is byte-stable across repeated runs")


def test_missing_runs_dir() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        tasks_dir = root / "state" / "tasks"
        tasks_dir.mkdir(parents=True)
        (tasks_dir / "task-alpha.md").write_text(TASK_ALPHA, encoding="utf-8")
        # No state/runs directory at all, no state/events.jsonl either.
        json_path = root / "out.json"
        result = run_scorecard(root, "--json", str(json_path))
        check(result.returncode == 0, f"missing state/runs does not crash (rc={result.returncode}, stderr={result.stderr!r})")
        data = json.loads(json_path.read_text(encoding="utf-8"))
        check(data["evidence"]["runs"]["absent"] is True, "state/runs absence is reported as absent")
        check(data["evidence"]["runs"]["parsed"] == 0, "zero run records parsed when dir is absent")
        check(data["evidence"]["events"]["absent"] is True, "missing events.jsonl is reported as absent")
        check("run evidence: absent" in result.stdout, "markdown notes run evidence is absent")


def test_empty_events_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        tasks_dir = root / "state" / "tasks"
        tasks_dir.mkdir(parents=True)
        (tasks_dir / "task-alpha.md").write_text(TASK_ALPHA, encoding="utf-8")
        (root / "state" / "events.jsonl").write_text("", encoding="utf-8")
        json_path = root / "out.json"
        result = run_scorecard(root, "--json", str(json_path))
        check(result.returncode == 0, f"empty events.jsonl does not crash (rc={result.returncode})")
        data = json.loads(json_path.read_text(encoding="utf-8"))
        check(data["evidence"]["events"]["absent"] is False, "an existing-but-empty events.jsonl is NOT absent")
        check(data["evidence"]["events"]["parsed"] == 0, "an empty events.jsonl parses to zero events")
        check(data["evidence"]["events"]["max_ts"] == "", "an empty events.jsonl has no max ts")


def test_bad_root() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        missing = Path(tmp) / "does-not-exist"
        result = run_scorecard(missing)
        check(result.returncode == 2, f"nonexistent --root exits 2 (got {result.returncode})")


def test_hostile_header_values_sanitized() -> None:
    # Task headers are worker-adjacent input; a raw ESC byte or '|' from one must not
    # corrupt (or ANSI-style) the rendered table a human cats.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        tasks_dir = root / "state" / "tasks"
        tasks_dir.mkdir(parents=True)
        (tasks_dir / "task-evil.md").write_text(
            "schema_version: 1\nid: task-evil\nengine: \x1b[31mansi\n"
            "model_alias: a|b\nstatus: passed\n\nbody\n",
            encoding="utf-8",
        )
        result = run_scorecard(root)
        check(result.returncode == 0, f"hostile headers still render (got {result.returncode})")
        check("\x1b" not in result.stdout, "raw ESC byte does not survive into the report")
        check("?[31mansi" in result.stdout, "control characters are replaced, value still identifiable")
        check("a\\|b" in result.stdout, "a '|' in an alias is escaped, not a cell break")


def main() -> int:
    fixture_data = test_full_fixture()
    test_json_stable(fixture_data)
    test_missing_runs_dir()
    test_empty_events_file()
    test_bad_root()
    test_hostile_header_values_sanitized()

    if failures:
        print(f"engine-scorecard.test: {len(failures)} FAILED")
        return 1
    print("engine-scorecard.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

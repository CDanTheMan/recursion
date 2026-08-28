#!/usr/bin/env python3
"""Engine/model-alias scorecard, derived entirely from on-disk evidence.

Reads state/tasks/*.md (task headers), state/events.jsonl (append-only event log,
schema documented in taskctl.sh emit_event/emit_notification_event and the pilot
event helpers in project-pilot.py/project-reconcile.py), and state/runs/*.json (run
evidence records written by worker-evidence.py: start/heartbeat/finish/gate/verify/
link-verifier). Produces a ONE-PAGE plain-markdown scorecard keyed by (engine, alias).

Grounding notes (read the source before changing the joins below):
  - A task's IMPLEMENTER engine is its `engine:` header field, default "claude"
    (work.sh: ENGINE="${ENGINE:-claude}"). Its VERIFIER engine is `verifier_engine:`,
    default = the implementer engine (work.sh: VERIFIER_ENGINE="${VERIFIER_ENGINE:-$ENGINE}").
  - A task's IMPLEMENTER alias is `model_alias:`; its VERIFIER alias is
    `verifier_model_alias:`. Absent -> "legacy" (work.sh run_arm_supervised passes
    "${MODEL_ALIAS:-legacy}" into worker-evidence.py --model-alias, which is the exact
    string this script reads back out of a run record — "legacy" is not invented here,
    it is the literal sentinel the executor already writes).
  - A run-evidence record (worker-evidence.py) carries task_id/role/model_alias/status/
    outcome/exit_code/started_at/finished_at but NOT engine — engine is joined from the
    task header via task_id, using the run's role to pick implementer vs verifier engine.
  - Canonical escalation identity events (taskctl.sh esc-record -> emit_event
    escalation-open/escalation-resolve) are written with an EMPTY task field today, so a
    join on events.jsonl's task field will legitimately find zero attributable
    escalations for those rows; other event kinds (pilot-task-created, task-transition,
    block, stale, ...) do carry a real task id and join normally. This script does the
    generic join and reports what it finds — it does not manufacture a task id events
    were not written with.

Exit codes:
  0 - report produced (sources may be legitimately absent; that is reported, not fabricated)
  2 - usage error: --root is not a directory, or --out/--json cannot be opened for writing

Absent vs empty: "absent" means the file/directory does not exist on disk. A file that
exists but yields zero valid records is reported with a parsed count of 0, not "absent".
"""

from __future__ import annotations

import argparse
import calendar
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
MAX_TABLE_ROWS = 25  # bounded-output rule: prioritize by activity, drop the rest, never append
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# Canonical escalation-identity event kinds (taskctl.sh: "the ONE writer for ... escalation
# identity"). Deliberately narrow: this is the identity-bearing pair, not every event that
# happens to mention trouble.
ESCALATION_EVENTS = {"escalation-open", "escalation-resolve"}


# --------------------------------------------------------------------------------------
# Task headers
# --------------------------------------------------------------------------------------

class TaskInfo:
    __slots__ = ("id", "engine", "verifier_engine", "model_alias", "verifier_model_alias", "status")

    def __init__(self, id_: str, engine: str, verifier_engine: str,
                 model_alias: str, verifier_model_alias: str, status: str) -> None:
        self.id = id_
        self.engine = engine
        self.verifier_engine = verifier_engine
        self.model_alias = model_alias
        self.verifier_model_alias = verifier_model_alias
        self.status = status


def parse_task_header(text: str) -> dict[str, str]:
    """Header fields end at the first blank line; body lines never supply a field
    (work.sh reads verifier_engine the same way, precisely to prevent that)."""
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            break
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            fields.setdefault(key.strip(), value.strip())
    return fields


def load_tasks(root: Path) -> tuple[dict[str, TaskInfo], int, int]:
    """Returns (task_map, parsed_count, skipped_count). Skipped = unreadable file or no
    parseable `id:` field (covers state/tasks/README.md and any truncated header)."""
    task_dir = root / "state" / "tasks"
    tasks: dict[str, TaskInfo] = {}
    parsed = 0
    skipped = 0
    if not task_dir.is_dir():
        return tasks, 0, 0
    for path in sorted(task_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
        except OSError:
            skipped += 1
            continue
        fields = parse_task_header(text)
        task_id = fields.get("id", "").strip()
        if not task_id:
            skipped += 1
            continue
        engine = fields.get("engine") or "claude"
        verifier_engine = fields.get("verifier_engine") or engine
        model_alias = fields.get("model_alias") or "legacy"
        verifier_model_alias = fields.get("verifier_model_alias") or "legacy"
        status = fields.get("status") or "(none)"
        tasks[task_id] = TaskInfo(task_id, engine, verifier_engine, model_alias,
                                  verifier_model_alias, status)
        parsed += 1
    return tasks, parsed, skipped


# --------------------------------------------------------------------------------------
# events.jsonl
# --------------------------------------------------------------------------------------

def load_events(root: Path) -> tuple[list[dict], int, int, str]:
    """Returns (events, parsed_count, skipped_count, max_ts). A malformed line is one that
    is not valid JSON, is not a JSON object, or lacks a string `event` field."""
    path = root / "state" / "events.jsonl"
    events: list[dict] = []
    parsed = 0
    skipped = 0
    max_ts = ""
    if not path.is_file():
        return events, 0, 0, ""
    try:
        raw = path.read_text(encoding="utf-8", errors="surrogateescape")
    except OSError:
        return events, 0, 0, ""
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if not isinstance(record, dict) or not isinstance(record.get("event"), str):
            skipped += 1
            continue
        events.append(record)
        parsed += 1
        ts = record.get("ts")
        if isinstance(ts, str) and ts > max_ts:
            max_ts = ts
    return events, parsed, skipped, max_ts


# --------------------------------------------------------------------------------------
# state/runs/*.json (worker-evidence.py records)
# --------------------------------------------------------------------------------------

class RunRecord:
    __slots__ = ("id", "task_id", "role", "alias", "status", "outcome",
                 "started_epoch", "finished_epoch")

    def __init__(self, id_: str, task_id: str, role: str, alias: str, status: str,
                 outcome: str, started_epoch: int | None, finished_epoch: int | None) -> None:
        self.id = id_
        self.task_id = task_id
        self.role = role
        self.alias = alias
        self.status = status
        self.outcome = outcome
        self.started_epoch = started_epoch
        self.finished_epoch = finished_epoch


def _parse_ts(value: Any) -> int | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return calendar.timegm(time.strptime(value, TS_FORMAT))
    except ValueError:
        return None


def load_runs(root: Path) -> tuple[list[RunRecord], int, int, bool]:
    """Returns (runs, parsed_count, skipped_count, dir_absent). A malformed record is one
    that is not a JSON object, or lacks the minimal identity fields worker-evidence.py
    always writes at `start` time (id/task_id/role/model_alias/status)."""
    runs_dir = root / "state" / "runs"
    runs: list[RunRecord] = []
    parsed = 0
    skipped = 0
    if not runs_dir.is_dir():
        return runs, 0, 0, True
    for path in sorted(runs_dir.glob("*.json")):
        try:
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
            record = json.loads(text)
        except (OSError, json.JSONDecodeError):
            skipped += 1
            continue
        if not isinstance(record, dict):
            skipped += 1
            continue
        run_id = record.get("id")
        task_id = record.get("task_id")
        role = record.get("role")
        alias = record.get("model_alias")
        status = record.get("status")
        if not all(isinstance(v, str) and v for v in (run_id, task_id, role, alias, status)):
            skipped += 1
            continue
        outcome = record.get("outcome") if isinstance(record.get("outcome"), str) else ""
        started = _parse_ts(record.get("started_at"))
        finished = _parse_ts(record.get("finished_at"))
        runs.append(RunRecord(run_id, task_id, role, alias, status, outcome, started, finished))
        parsed += 1
    return runs, parsed, skipped, False


# --------------------------------------------------------------------------------------
# Aggregation
# --------------------------------------------------------------------------------------

class Bucket:
    def __init__(self, engine: str, alias: str) -> None:
        self.engine = engine
        self.alias = alias
        self.task_status: Counter[str] = Counter()
        self.verifier_arms = 0
        self.runs_by_role: Counter[str] = Counter()
        self.outcomes: Counter[str] = Counter()
        self.retries = 0
        self.durations: list[int] = []
        self.escalations: Counter[str] = Counter()

    def activity(self) -> int:
        return (sum(self.task_status.values()) + self.verifier_arms
                + sum(self.runs_by_role.values()) + sum(self.escalations.values()))

    def key(self) -> tuple[str, str]:
        return (self.engine, self.alias)


def _outcome_bucket(status: str, outcome: str) -> str:
    if outcome == "timeout":
        return "timeout"
    if status == "succeeded":
        return "pass"
    if status == "cancelled":
        return "deferred"
    if status == "failed":
        return "fail"
    if status == "running":
        return "running"
    return "other"


def build_buckets(
    tasks: dict[str, TaskInfo],
    runs: list[RunRecord],
    events: list[dict],
) -> tuple[dict[tuple[str, str], Bucket], int, int]:
    buckets: dict[tuple[str, str], Bucket] = {}

    def get(engine: str, alias: str) -> Bucket:
        key = (engine, alias)
        if key not in buckets:
            buckets[key] = Bucket(engine, alias)
        return buckets[key]

    # Tasks: implementer arm gets the status count; verifier arm gets a plain count.
    for task in tasks.values():
        get(task.engine, task.model_alias).task_status[task.status] += 1
        get(task.verifier_engine, task.verifier_model_alias).verifier_arms += 1

    # Run evidence: join engine via task_id + role. A run whose task_id is unknown still
    # carries its own alias (that came straight from the run record) but not a real engine.
    unknown_task_runs = 0
    by_bucket_task_role: dict[tuple[str, str], Counter[tuple[str, str]]] = {}
    for run in runs:
        task = tasks.get(run.task_id)
        if task is None:
            engine = "(unknown-task)"
            unknown_task_runs += 1
        else:
            engine = task.verifier_engine if run.role == "verifier" else task.engine
        bucket = get(engine, run.alias)
        bucket.runs_by_role[run.role] += 1
        bucket.outcomes[_outcome_bucket(run.status, run.outcome)] += 1
        if run.started_epoch is not None and run.finished_epoch is not None \
                and run.finished_epoch >= run.started_epoch:
            bucket.durations.append(run.finished_epoch - run.started_epoch)
        counter = by_bucket_task_role.setdefault(bucket.key(), Counter())
        counter[(run.task_id, run.role)] += 1
    for key, counter in by_bucket_task_role.items():
        buckets[key].retries += sum(max(0, n - 1) for n in counter.values())

    # Escalations: join events.jsonl `task` field to the task's (current) implementer
    # engine/alias. Events written with an empty task field (the canonical taskctl.sh
    # esc-record path today) cannot join and are counted as unattributed, not guessed at.
    unattributed_escalations = 0
    for event in events:
        kind = event.get("event")
        if kind not in ESCALATION_EVENTS:
            continue
        task_id = event.get("task")
        task = tasks.get(task_id) if isinstance(task_id, str) and task_id else None
        if task is None:
            unattributed_escalations += 1
            continue
        get(task.engine, task.model_alias).escalations[kind] += 1

    return buckets, unknown_task_runs, unattributed_escalations


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------

def _fmt_duration(seconds: int) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m{sec:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes:02d}m"


def _cell(value: object) -> str:
    """Neutralize header-sourced text for the markdown table: task headers are worker-adjacent
    input, and a raw ESC byte or '|' would corrupt (or ANSI-style) a report a human cats."""
    text = str(value)
    text = "".join("?" if (ord(ch) < 0x20 or ord(ch) == 0x7F) else ch for ch in text)
    return text.replace("|", "\\|")


def _fmt_counter(counter: Counter[str]) -> str:
    if not counter:
        return "-"
    return " ".join(f"{_cell(k)}:{v}" for k, v in sorted(counter.items()))


def _fmt_outcomes(counter: Counter[str]) -> str:
    order = ["pass", "fail", "timeout", "deferred", "running", "other"]
    parts = [f"{name}:{counter[name]}" for name in order if counter.get(name)]
    return " ".join(parts) if parts else "-"


def _row_wallclock(bucket: Bucket) -> str:
    if not bucket.durations:
        return "n/a"
    median = statistics.median(bucket.durations)
    total = sum(bucket.durations)
    return f"{_fmt_duration(median)} / {_fmt_duration(total)}"


def render_json(
    root: Path,
    tasks_parsed: int, tasks_skipped: int,
    events_parsed: int, events_skipped: int, events_max_ts: str, events_absent: bool,
    runs_parsed: int, runs_skipped: int, runs_absent: bool,
    buckets: dict[tuple[str, str], Bucket],
    unknown_task_runs: int, unattributed_escalations: int,
) -> dict:
    rows = []
    for key in sorted(buckets):
        bucket = buckets[key]
        rows.append({
            "engine": bucket.engine,
            "alias": bucket.alias,
            "task_status": dict(sorted(bucket.task_status.items())),
            "verifier_arms": bucket.verifier_arms,
            "runs_by_role": dict(sorted(bucket.runs_by_role.items())),
            "outcomes": dict(sorted(bucket.outcomes.items())),
            "retries": bucket.retries,
            "wallclock_seconds": {
                "median": statistics.median(bucket.durations) if bucket.durations else None,
                "total": sum(bucket.durations) if bucket.durations else None,
                "n": len(bucket.durations),
            },
            "escalations": dict(sorted(bucket.escalations.items())),
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "root": str(root),
        "evidence": {
            "tasks": {"parsed": tasks_parsed, "skipped": tasks_skipped, "absent": tasks_parsed == 0 and tasks_skipped == 0},
            "events": {"parsed": events_parsed, "skipped": events_skipped, "max_ts": events_max_ts, "absent": events_absent},
            "runs": {"parsed": runs_parsed, "skipped": runs_skipped, "absent": runs_absent},
        },
        "unknown_task_runs": unknown_task_runs,
        "unattributed_escalations": unattributed_escalations,
        "rows": rows,
    }


def render_markdown(data: dict) -> str:
    ev = data["evidence"]
    lines: list[str] = []
    generated = time.strftime(TS_FORMAT, time.gmtime())
    lines.append(f"# Engine Scorecard ({time.strftime('%Y-%m-%d', time.gmtime())})")
    lines.append("")
    max_ts = ev["events"]["max_ts"] or "none"
    lines.append(
        f"Evidence basis: {ev['tasks']['parsed']} tasks, {ev['runs']['parsed']} run records, "
        f"events through {max_ts}. Generated {generated}."
    )
    if ev["tasks"]["absent"]:
        lines.append("- tasks: absent (state/tasks not found or empty)")
    if ev["events"]["absent"]:
        lines.append("- events: absent (state/events.jsonl not found)")
    if ev["runs"]["absent"]:
        lines.append("- run evidence: absent (state/runs not found)")
    lines.append("")

    rows = list(data["rows"])
    for row in rows:
        row["_activity"] = (
            sum(row["task_status"].values()) + row["verifier_arms"]
            + sum(row["runs_by_role"].values()) + sum(row["escalations"].values())
        )
    rows.sort(key=lambda r: (-r["_activity"], r["engine"], r["alias"]))
    omitted = max(0, len(rows) - MAX_TABLE_ROWS)
    shown = rows[:MAX_TABLE_ROWS]

    if shown:
        lines.append("| Engine | Alias | Tasks (status) | Verifier-arms | Runs (by role) | Outcomes | Retries | Wall-clock median/total | Escalations |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for row in shown:
            task_status = Counter(row["task_status"])
            runs_by_role = Counter(row["runs_by_role"])
            outcomes = Counter(row["outcomes"])
            escalations = Counter(row["escalations"])
            wc = row["wallclock_seconds"]
            wallclock = "n/a" if wc["n"] == 0 else f"{_fmt_duration(wc['median'])} / {_fmt_duration(wc['total'])}"
            lines.append(
                f"| {_cell(row['engine'])} | {_cell(row['alias'])} | {_fmt_counter(task_status)} | "
                f"{row['verifier_arms'] or '-'} | {_fmt_counter(runs_by_role)} | "
                f"{_fmt_outcomes(outcomes)} | {row['retries'] or '-'} | {wallclock} | "
                f"{_fmt_counter(escalations)} |"
            )
    else:
        lines.append("(no engine/alias activity found in tasks or run evidence)")
    if omitted:
        lines.append("")
        lines.append(f"+{omitted} more (engine, alias) row(s) omitted (lowest activity; see --json for the full table).")

    lines.append("")
    footer = (
        f"Skipped: {ev['tasks']['skipped']} malformed task file(s), "
        f"{ev['events']['skipped']} malformed event line(s), "
        f"{ev['runs']['skipped']} malformed run record(s). "
        f"{data['unknown_task_runs']} run record(s) reference an unknown task id "
        f"(grouped under engine=(unknown-task)). "
        f"{data['unattributed_escalations']} escalation event(s) had no resolvable task "
        f"(unattributed)."
    )
    lines.append(footer)
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=None,
                        help="repo root (default: parent of this script's directory)")
    parser.add_argument("--out", default=None, help="write markdown report here (default: stdout)")
    parser.add_argument("--json", default=None, help="also write machine-readable JSON here")
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"engine-scorecard: --root is not a directory: {root}", file=sys.stderr)
        return 2

    tasks, tasks_parsed, tasks_skipped = load_tasks(root)
    events, events_parsed, events_skipped, events_max_ts = load_events(root)
    events_absent = not (root / "state" / "events.jsonl").is_file()
    runs, runs_parsed, runs_skipped, runs_absent = load_runs(root)

    buckets, unknown_task_runs, unattributed_escalations = build_buckets(tasks, runs, events)

    data = render_json(
        root, tasks_parsed, tasks_skipped,
        events_parsed, events_skipped, events_max_ts, events_absent,
        runs_parsed, runs_skipped, runs_absent,
        buckets, unknown_task_runs, unattributed_escalations,
    )
    report = render_markdown(data)

    if args.out:
        try:
            Path(args.out).write_text(report, encoding="utf-8")
        except OSError as exc:
            print(f"engine-scorecard: cannot write --out {args.out}: {exc}", file=sys.stderr)
            return 2
    else:
        sys.stdout.write(report)

    if args.json:
        try:
            Path(args.json).write_text(
                json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        except OSError as exc:
            print(f"engine-scorecard: cannot write --json {args.json}: {exc}", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

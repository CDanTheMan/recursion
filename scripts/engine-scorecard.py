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
  - Phase 5 run evidence carries its resolved engine directly. Older records without it are
     read through the task-header compatibility join; current assignment facts are not rebuilt
     from mutable headers when direct evidence exists.
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
import math
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import assignment as assignment_mod
import assignment_contract as assignment_contract_mod
from assignment_contract import AssignmentError as ContractAssignmentError
from jsonl_durable import JsonlDurabilityError, atomic_bytes, ensure_no_symlink, read_durable_bytes

SCHEMA_VERSION = 1
MAX_TABLE_ROWS = 25  # bounded-output rule: prioritize by activity, drop the rest, never append
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_INPUT_LINES = 20000
MAX_FIELD_BYTES = 1 << 20

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
    if not isinstance(text, str):
        return {}
    try:
        if len(text.encode("utf-8", "strict")) > MAX_INPUT_BYTES:
            return {}
    except UnicodeError:
        return {}
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            break
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            clean_key, clean_value = key.strip(), value.strip()
            try:
                within_bound = len(clean_value.encode("utf-8", "strict")) <= MAX_FIELD_BYTES
            except UnicodeError:
                within_bound = False
            if clean_key and within_bound:
                fields.setdefault(clean_key, clean_value)
    return fields


def load_tasks(root: Path) -> tuple[dict[str, TaskInfo], int, int]:
    """Returns (task_map, parsed_count, skipped_count). Skipped = unreadable file or no
    parseable `id:` field (covers state/tasks/README.md and any truncated header)."""
    task_dir = root / "state" / "tasks"
    tasks: dict[str, TaskInfo] = {}
    parsed = 0
    skipped = 0
    try:
        ensure_no_symlink(task_dir)
        if not task_dir.is_dir():
            return tasks, 0, 0
        paths = sorted(task_dir.glob("*.md"))
    except (OSError, ValueError, JsonlDurabilityError):
        return tasks, 0, 0
    for path in paths[:MAX_INPUT_LINES]:
        try:
            raw = read_durable_bytes(path, max_bytes=MAX_INPUT_BYTES)
            if raw is None:
                raise OSError
            text = raw.decode("utf-8", "strict")
        except (OSError, UnicodeDecodeError, JsonlDurabilityError, ValueError):
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
    try:
        raw_bytes = read_durable_bytes(path, max_bytes=MAX_INPUT_BYTES)
        if raw_bytes is None:
            return events, 0, 0, ""
        raw = raw_bytes.decode("utf-8", "strict")
    except (OSError, UnicodeDecodeError, JsonlDurabilityError, ValueError):
        return events, 0, 0, ""
    lines = raw.splitlines()
    skipped += max(0, len(lines) - MAX_INPUT_LINES)
    for line in lines[:MAX_INPUT_LINES]:
        if not line.strip():
            continue
        try:
            record = json.loads(
                line,
                parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite JSON number")),
            )
        except (json.JSONDecodeError, TypeError, ValueError, OverflowError, RecursionError,
                UnicodeDecodeError):
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
                 "started_epoch", "finished_epoch", "engine", "assignment_digest", "attribution")

    def __init__(self, id_: str, task_id: str, role: str, alias: str, status: str,
                 outcome: str, started_epoch: int | None, finished_epoch: int | None,
                 engine: str | None = None, assignment_digest: str | None = None,
                 attribution: dict | None = None) -> None:
        self.id = id_
        self.task_id = task_id
        self.role = role
        self.alias = alias
        self.status = status
        self.outcome = outcome
        self.started_epoch = started_epoch
        # Phase 3 (D-016): when the run's own assignment bound its engine at launch time, use
        # it directly instead of joining the task header (which can change after the run).
        self.engine = engine
        self.assignment_digest = assignment_digest
        self.attribution = attribution or {}
        self.finished_epoch = finished_epoch


def _parse_ts(value: Any) -> int | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return calendar.timegm(time.strptime(value, TS_FORMAT))
    except (OSError, TypeError, ValueError, OverflowError, RecursionError, UnicodeError):
        return None


def load_runs(root: Path) -> tuple[list[RunRecord], int, int, bool]:
    """Returns (runs, parsed_count, skipped_count, dir_absent). A malformed record is one
    that is not a JSON object, or lacks the minimal identity fields worker-evidence.py
    always writes at `start` time (id/task_id/role/model_alias/status)."""
    runs_dir = root / "state" / "runs"
    runs: list[RunRecord] = []
    parsed = 0
    skipped = 0
    try:
        ensure_no_symlink(runs_dir)
        if not runs_dir.is_dir():
            return runs, 0, 0, True
        paths = sorted(runs_dir.glob("*.json"))
    except (OSError, ValueError, JsonlDurabilityError):
        return runs, 0, 0, True
    for path in paths[:MAX_INPUT_LINES]:
        try:
            raw = read_durable_bytes(path, max_bytes=MAX_INPUT_BYTES)
            if raw is None:
                raise OSError
            record = json.loads(
                raw.decode("utf-8", "strict"),
                parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite JSON number")),
            )
        except (OSError, UnicodeDecodeError, JsonlDurabilityError, json.JSONDecodeError,
                TypeError, ValueError, OverflowError, RecursionError):
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
        assignment_digest = record.get("assignment_digest") \
            if isinstance(record.get("assignment_digest"), str) and record.get("assignment_digest") else None
        direct_engine = record.get("engine") \
            if isinstance(record.get("engine"), str) and record.get("engine") else None
        attribution = {}
        if assignment_digest:
            # Strict Phase 5 records carry the exact standalone contract path.  Read it
            # through assignment_contract; the run JSON is only an evidence projection.
            assignment_file = record.get("assignment_file")
            if isinstance(assignment_file, str) and assignment_file:
                try:
                    persisted, computed = assignment_contract_mod.load_assignment(assignment_file)
                except (ContractAssignmentError, OSError, TypeError, ValueError,
                        UnicodeDecodeError, OverflowError, RecursionError):
                    skipped += 1
                    continue
                if computed != assignment_digest or persisted.get("task_id") != task_id:
                    skipped += 1
                    continue
                role_assignment = persisted.get("role_assignments", {}).get(role)
                if not isinstance(role_assignment, dict):
                    skipped += 1
                    continue
                direct_engine = role_assignment["engine"]
                attribution = {key: persisted.get(key) for key in (
                    "assignment_digest", "capacity_pool", "provider", "host", "model",
                    "sandbox_profile", "source_repository", "source_branch", "source_sha")}
                attribution["provider"] = role_assignment["provider"]
                attribution["model"] = role_assignment["model"]
            elif isinstance(record.get("assignment"), dict) \
                    and "controller_repository" in record["assignment"]:
                # A strict embedded contract without its source file is not an authority.
                skipped += 1
                continue
            else:
                # Phase 3 compatibility: old assignment-native records used the
                # task-id/digest directory and have no assignment_file field.
                persisted = assignment_mod.load_assignment(
                    root / "state" / "assignments", task_id, assignment_digest,
                )
                if persisted is None:
                    skipped += 1
                    continue
                try:
                    assignment_mod.validate_assignment(persisted, require_source_evidence=True)
                except assignment_mod.AssignmentError:
                    skipped += 1
                    continue
                direct_engine = persisted["engine"]
                attribution = {key: persisted.get(key) for key in (
                    "assignment_digest", "capacity_pool", "provider", "host", "model",
                    "sandbox_profile", "source_repository", "source_branch", "source_sha")}
        engine = direct_engine
        runs.append(RunRecord(run_id, task_id, role, alias, status, outcome, started, finished,
                              engine, assignment_digest, attribution))
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
        self.attributions: dict[str, dict] = {}

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

    # Run evidence is authoritative when it carries the resolved engine.  Phase 3 assignment
    # attribution is joined for records that carry its digest; older records fall back to the
    # task-id compatibility join.
    unknown_task_runs = 0
    by_bucket_task_role: dict[tuple[str, str], Counter[tuple[str, str]]] = {}
    for run in runs:
        if run.engine:
            engine = run.engine
        else:
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
        if run.attribution:
            bucket.attributions[json.dumps(run.attribution, sort_keys=True, separators=(",", ":"))] = run.attribution
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
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        return "n/a"
    try:
        if not math.isfinite(float(seconds)) or seconds < 0:
            return "n/a"
    except (TypeError, ValueError, OverflowError):
        return "n/a"
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
    text = value if isinstance(value, str) else str(value)
    if len(text.encode("utf-8", "replace")) > MAX_FIELD_BYTES:
        text = text.encode("utf-8", "replace")[:MAX_FIELD_BYTES].decode("utf-8", "ignore")
    text = "".join("?" if (ord(ch) < 0x20 or ord(ch) == 0x7F) else ch for ch in text)
    return text.replace("|", "\\|")


def _fmt_counter(counter: Counter[str]) -> str:
    if not counter:
        return "-"
    return " ".join(f"{_cell(k)}:{v}" for k, v in sorted(counter.items()))


def _attribution_text(value: dict) -> str:
    keys = ("assignment_digest", "capacity_pool", "provider", "host", "model",
            "sandbox_profile", "source_repository", "source_branch", "source_sha")
    return ", ".join(f"{key}={value.get(key) if value.get(key) is not None else '-'}" for key in keys)


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
            "attribution": [bucket.attributions[key] for key in sorted(bucket.attributions)],
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
        lines.append("| Engine | Alias | Assignment attribution | Tasks (status) | Verifier-arms | Runs (by role) | Outcomes | Retries | Wall-clock median/total | Escalations |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for row in shown:
            task_status = Counter(row["task_status"])
            runs_by_role = Counter(row["runs_by_role"])
            outcomes = Counter(row["outcomes"])
            escalations = Counter(row["escalations"])
            wc = row["wallclock_seconds"]
            wallclock = "n/a" if wc["n"] == 0 else f"{_fmt_duration(wc['median'])} / {_fmt_duration(wc['total'])}"
            lines.append(
                f"| {_cell(row['engine'])} | {_cell(row['alias'])} | {_cell('; '.join(_attribution_text(item) for item in row.get('attribution', [])) or '-') } | {_fmt_counter(task_status)} | "
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

    try:
        root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
        ensure_no_symlink(root)
        if not root.is_dir():
            print("engine-scorecard: --root is not a directory", file=sys.stderr)
            return 2

        tasks, tasks_parsed, tasks_skipped = load_tasks(root)
        events, events_parsed, events_skipped, events_max_ts = load_events(root)
        events_path = root / "state" / "events.jsonl"
        events_absent = read_durable_bytes(events_path, max_bytes=MAX_INPUT_BYTES) is None
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
            atomic_bytes(Path(args.out), report.encode("utf-8"))
        else:
            sys.stdout.write(report)

        if args.json:
            atomic_bytes(
                Path(args.json),
                (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8"),
            )
        return 0
    except (OSError, UnicodeDecodeError, UnicodeEncodeError, JsonlDurabilityError,
            TypeError, ValueError, OverflowError, RecursionError, json.JSONDecodeError):
        print("engine-scorecard: invalid input or durable state", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

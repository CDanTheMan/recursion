"""Write the final run report as JSON and Markdown."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.v3.harness.redact import redact


def build_report(record: dict) -> dict:
    tasks = []
    totals = {"cost": None, "input_tokens": None, "output_tokens": None}
    duration = 0.0
    for task in record.get("tasks", []):
        usage = task.get("usage") or {"cost": None, "input_tokens": None, "output_tokens": None}
        _add(totals, usage)
        task_duration = task.get("duration_seconds")
        if isinstance(task_duration, (int, float)) and not isinstance(task_duration, bool):
            duration += float(task_duration)
        tasks.append(
            {
                "attempts": task.get("attempts") or [],
                "branch": task.get("branch"),
                "commit": task.get("commit"),
                "depends_on": task.get("depends_on") or [],
                "diff": task.get("diff") or "",
                "duration_seconds": task_duration,
                "id": task.get("id"),
                "index": task.get("index"),
                "merge_conflict": task.get("merge_conflict") or [],
                "merge_status": task.get("merge_status"),
                "provider": task.get("provider"),
                "reviews": task.get("reviews") or [],
                "status": task.get("status"),
                "task": task.get("task"),
                "usage": usage,
            }
        )
    wall = record.get("duration_seconds")
    if isinstance(wall, bool) or not isinstance(wall, (int, float)):
        wall = duration
    return {
        "duration_seconds": wall,
        "base_ref": record.get("base_ref"),
        "goal": record.get("goal"),
        "land": record.get("land"),
        "plan_fallback": record.get("plan_fallback"),
        "plan_source": record.get("plan_source"),
        "run_branch": record.get("run_branch"),
        "run_id": record.get("run_id"),
        "status": record.get("status"),
        "stop_reason": record.get("stop_reason"),
        "tasks": tasks,
        "usage": totals,
    }


def write_reports(directory: Path, record: dict) -> dict:
    payload = redact(build_report(record))
    if not isinstance(payload, dict):
        payload = {}
    json_path = directory / f"{record['run_id']}.report.json"
    markdown_path = directory / f"{record['run_id']}.report.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def render_markdown(report: dict) -> str:
    lines = [
        f"# Run {report['run_id']}",
        "",
        f"Status: {report['status']}",
        f"Run branch: {report.get('run_branch') or 'none'}",
    ]
    land = report.get("land")
    if isinstance(land, dict):
        lines.append(f"Land: {land.get('status')} into {land.get('branch') or 'none'}")
        lines.append(f"Land commit: {land.get('commit') or 'none'}")
        if land.get("error"):
            lines.append(f"Land error: {land['error']}")
        if land.get("paths"):
            lines.append("Land conflict: " + ", ".join(land["paths"]))
    lines.extend(
        [
            f"Duration: {_seconds(report['duration_seconds'])}",
            f"Usage: {_usage(report['usage'])}",
            "",
        ]
    )
    if report.get("stop_reason"):
        lines.append(f"Stop reason: {report['stop_reason']}")
        lines.append("")
    for task in report["tasks"]:
        lines.append(f"## Task {task['index']}")
        lines.append("")
        lines.append(f"Id: {task.get('id') or task['index']}")
        if task.get("depends_on"):
            lines.append("Depends on: " + ", ".join(task["depends_on"]))
        lines.append(f"Task: {task['task']}")
        lines.append(f"Provider: {task['provider']}")
        lines.append(f"Status: {task['status']}")
        lines.append(f"Branch: {task.get('branch') or 'none'}")
        lines.append(f"Commit: {task.get('commit') or 'none'}")
        lines.append(f"Merge: {task.get('merge_status') or 'none'}")
        if task.get("merge_conflict"):
            lines.append("Conflict: " + ", ".join(task["merge_conflict"]))
        lines.append(f"Duration: {_seconds(task['duration_seconds'])}")
        lines.append(f"Attempts: {len(task['attempts'])}")
        lines.append(f"Usage: {_usage(task['usage'])}")
        lines.append("")
        lines.append("Reviews:")
        if not task["reviews"]:
            lines.append("- none")
        for review in task["reviews"]:
            reviewer = review.get("reviewer") or "none"
            lines.append(f"- round {review['round']}: {reviewer} {review['verdict']}")
        lines.append("")
        lines.append("Diff:")
        lines.append("```")
        lines.append(task["diff"] or "(empty)")
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def _seconds(value: object) -> str:
    if not isinstance(value, (int, float)):
        return "unknown"
    return f"{float(value):.3f}s"


def _usage(usage: dict) -> str:
    return (
        f"input={_figure(usage.get('input_tokens'))} "
        f"output={_figure(usage.get('output_tokens'))} "
        f"cost={_figure(usage.get('cost'))}"
    )


def _figure(value: object) -> str:
    if value is None:
        return "unknown"
    return str(value)


def _add(total: dict, extra: dict) -> None:
    for key in ("cost", "input_tokens", "output_tokens"):
        value = extra.get(key)
        if value is None:
            continue
        total[key] = value if total[key] is None else total[key] + value

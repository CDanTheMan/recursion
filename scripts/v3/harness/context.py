"""Size-capped context for dependent tasks and the planner."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.v3.harness.redact import redact_text


SUMMARY_LIMIT = 500
DIFF_LIMIT = 2000
CONTEXT_LIMIT = 6000
REPO_MAP_LIMIT = 4000
TREE_LIMIT = 80
DOC_LIMIT = 600
KEY_DOCS = ("README.md", "docs/USER-GUIDE.md", "docs/v3/START-HERE.md")

_RUN = subprocess.run


def task_prompt(task: dict, tasks: list[dict]) -> str:
    """Return the worker prompt, including capped context for each dependency."""

    base = task.get("task") if isinstance(task.get("task"), str) else ""
    depends = task.get("depends_on") or []
    if not depends:
        return base
    by_id = {item.get("id"): item for item in tasks if isinstance(item, dict)}
    blocks = []
    for dep_id in depends:
        dep = by_id.get(dep_id)
        if not isinstance(dep, dict):
            blocks.append(f"Task {dep_id}:\nSummary: missing")
            continue
        lines = [f"Task {dep_id}:", "Summary: " + _clip(_summary(dep), SUMMARY_LIMIT)]
        commit = dep.get("commit")
        if isinstance(commit, str) and commit:
            lines.append(f"Commit: {commit}")
        diff = dep.get("diff") if isinstance(dep.get("diff"), str) else ""
        if diff.strip():
            lines.append("Diff:")
            lines.append(_clip(diff.strip(), DIFF_LIMIT))
        elif not isinstance(commit, str) or not commit:
            lines.append("Commit: none")
        blocks.append("\n".join(lines))
    section = "Dependency context:\n" + "\n\n".join(blocks)
    section = redact_text(section)
    if len(section) > CONTEXT_LIMIT:
        section = section[:CONTEXT_LIMIT] + "\n[dependency context truncated]"
    if not base:
        return section
    return base + "\n\n" + section


def repo_map(root: Path) -> str:
    """Compact tracked file tree plus the opening text of the key docs."""

    files = _tracked(root)
    lines = ["Repository files:"]
    lines.extend(files[:TREE_LIMIT])
    if len(files) > TREE_LIMIT:
        lines.append(f"... {len(files) - TREE_LIMIT} more files")
    for name in KEY_DOCS:
        path = Path(root) / name
        if not path.is_file():
            continue
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines.append(f"Doc {name}:")
        lines.append(_clip(body.strip(), DOC_LIMIT))
    text = redact_text("\n".join(lines)).replace("Goal:\n", "Goal: ")
    if len(text) > REPO_MAP_LIMIT:
        return text[:REPO_MAP_LIMIT] + "\n[repository map truncated]"
    return text


def recovery_prompt(task: dict, tasks: list[dict], paths: list[str]) -> str:
    """Prompt a provider to reconcile one task on top of the current run branch."""

    base = task.get("task") if isinstance(task.get("task"), str) else ""
    lines = [
        base,
        "",
        "The merge into the run branch conflicted.",
        "This worktree is the current run branch. Reconcile your task on top of it.",
        "Do not revert work that already landed.",
        "Conflicting paths:",
    ]
    shown = [path for path in paths if isinstance(path, str) and path][:20]
    if shown:
        lines.extend(f"- {path}" for path in shown)
    else:
        lines.append("- (none reported)")
    lines.append("")
    lines.append("Already landed:")
    landed = []
    for item in tasks:
        if not isinstance(item, dict) or item.get("index") == task.get("index"):
            continue
        if item.get("status") != "completed" or item.get("merge_status") not in {None, "landed"}:
            continue
        landed.append(item)
    if not landed:
        lines.append("Summary: none")
    for item in landed:
        lines.append(f"Task {item.get('id')}:")
        lines.append("Summary: " + _clip(_summary(item), SUMMARY_LIMIT))
        commit = item.get("commit")
        if isinstance(commit, str) and commit:
            lines.append(f"Commit: {commit}")
    text = redact_text("\n".join(lines))
    if len(text) > CONTEXT_LIMIT:
        return text[:CONTEXT_LIMIT] + "\n[recovery context truncated]"
    return text


def _summary(dep: dict) -> str:
    text = dep.get("text")
    if isinstance(text, str) and text.strip():
        return " ".join(text.split())
    task = dep.get("task")
    if isinstance(task, str) and task.strip():
        return " ".join(task.split())
    return ""


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n[truncated]"


def _tracked(root: Path) -> list[str]:
    completed = _RUN(
        ["git", "-c", "core.longpaths=true", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]

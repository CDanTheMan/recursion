"""Prune old run records, worktrees, and task branches."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.state import RunStore


_RUN = subprocess.run
_DAY = 86400


def clean_runs(
    store: RunStore,
    *,
    repo: Path,
    older_than_days: int = 7,
    dry_run: bool = False,
    now: float | None = None,
) -> dict:
    """Remove runs older than ``older_than_days``. ``dry_run`` lists them and deletes nothing."""

    if isinstance(older_than_days, bool) or not isinstance(older_than_days, int) or older_than_days < 0:
        raise HarnessError("older-than must be an integer >= 0")
    moment = datetime.now(timezone.utc).timestamp() if now is None else now
    cutoff = moment - older_than_days * _DAY
    head = _current_branch(repo)
    removed = []
    skipped = []
    for summary in store.list_runs():
        run_id = summary["run_id"]
        record = store.load(run_id)
        if _created(record, store.root / f"{run_id}.json") >= cutoff:
            continue
        branches = _run_branches(repo, run_id, record.get("run_branch"))
        worktrees = _worktrees(repo, branches)
        if head in branches:
            skipped.append({"reason": "checked out", "run_id": run_id})
            continue
        files = _files(store.root, run_id)
        entry = {
            "branches": branches,
            "files": [str(path) for path in files],
            "run_id": run_id,
            "worktrees": worktrees,
        }
        if not dry_run:
            for path in worktrees:
                _quiet(repo, "worktree", "remove", "--force", path)
            _quiet(repo, "worktree", "prune")
            for branch in branches:
                _quiet(repo, "branch", "-D", branch)
            for path in files:
                path.unlink(missing_ok=True)
        removed.append(entry)
    return {
        "dry_run": dry_run,
        "older_than_days": older_than_days,
        "removed": removed,
        "skipped": skipped,
    }


def _created(record: dict, path: Path) -> float:
    text = record.get("created")
    if isinstance(text, str):
        try:
            parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            return parsed.timestamp()
        except ValueError:
            pass
    if path.is_file():
        return path.stat().st_mtime
    return datetime.now(timezone.utc).timestamp()


def _files(root: Path, run_id: str) -> list[Path]:
    names = (
        f"{run_id}.json",
        f"{run_id}.jsonl",
        f"{run_id}.report.json",
        f"{run_id}.report.md",
    )
    return [root / name for name in names if (root / name).is_file()]


def _run_branches(repo: Path, run_id: str, recorded: object) -> list[str]:
    wanted = {f"recursion/run/{run_id}"}
    if isinstance(recorded, str) and recorded:
        wanted.add(recorded)
    prefix = f"recursion/task/{run_id}/"
    found = []
    for name in _branches(repo):
        if name in wanted or name.startswith(prefix):
            found.append(name)
    return found


def _branches(repo: Path) -> list[str]:
    completed = _run(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _worktrees(repo: Path, branches: list[str]) -> list[str]:
    if not branches:
        return []
    wanted = {f"refs/heads/{name}" for name in branches}
    completed = _run(repo, "worktree", "list", "--porcelain")
    if completed.returncode != 0:
        return []
    main = str(Path(repo).resolve())
    found = []
    current = None
    ref = None
    for line in completed.stdout.splitlines() + [""]:
        if line.startswith("worktree "):
            if current is not None and ref in wanted and str(Path(current).resolve()) != main:
                found.append(current)
            current = line.split(" ", 1)[1]
            ref = None
        elif line.startswith("branch "):
            ref = line.split(" ", 1)[1]
        elif line == "" and current is not None:
            if ref in wanted and str(Path(current).resolve()) != main:
                found.append(current)
            current = None
            ref = None
    return found


def _current_branch(repo: Path) -> str | None:
    completed = _run(repo, "rev-parse", "--abbrev-ref", "HEAD")
    if completed.returncode != 0:
        return None
    name = completed.stdout.strip()
    if not name or name == "HEAD":
        return None
    return name


def _quiet(cwd: Path, *args: str) -> None:
    _run(cwd, *args)


def _run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _RUN(
        ["git", "-c", "core.longpaths=true", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

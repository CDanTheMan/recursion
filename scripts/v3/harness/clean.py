"""Prune old run records, worktrees, and task branches."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.state import RunStore


_RUN = subprocess.run
_DAY = 86400
_RESUMABLE = {
    "budget-exceeded",
    "cancelled",
    "conflict",
    "failed",
    "review-rejected",
    "skipped",
    "unreviewed",
}


def clean_runs(
    store: RunStore,
    *,
    repo: Path,
    older_than_days: int = 7,
    dry_run: bool = False,
    include_unlanded: bool = False,
    now: float | None = None,
) -> dict:
    """Remove runs older than ``older_than_days``.

    Running, pending, and resumable runs are skipped. An unlanded run branch
    and a worktree with uncommitted changes are skipped unless
    ``include_unlanded`` is set. ``dry_run`` returns the same ``removed`` and
    ``skipped`` lists and deletes nothing.
    """

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
        reason = _nonterminal_reason(record)
        if reason is not None:
            skipped.append({"reason": reason, "run_id": run_id})
            continue
        branches = _run_branches(repo, run_id, record.get("run_branch"))
        if head in branches:
            skipped.append({"reason": "checked out", "run_id": run_id})
            continue
        plan = _partition(repo, record, run_id, branches, include_unlanded=include_unlanded)
        files = _files(store.root, run_id)
        skipped.extend(plan["skipped"])
        if plan["branches"] or plan["worktrees"] or files:
            entry = {
                "branches": plan["branches"],
                "files": [str(path) for path in files],
                "run_id": run_id,
                "worktrees": plan["worktrees"],
            }
            if not dry_run:
                _delete(repo, plan["worktrees"], plan["branches"], files)
            removed.append(entry)
    return {
        "dry_run": dry_run,
        "include_unlanded": include_unlanded,
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


def _nonterminal_reason(record: dict) -> str | None:
    """Running, pending, and resumable runs are not safe to prune."""

    status = record.get("status")
    tasks = record.get("tasks") if isinstance(record.get("tasks"), list) else []
    task_statuses = {task.get("status") for task in tasks if isinstance(task, dict)}
    if status == "running" or "running" in task_statuses:
        return "running"
    if status == "pending" or "pending" in task_statuses:
        return "pending"
    if status in _RESUMABLE or task_statuses & _RESUMABLE:
        return "resumable"
    if status != "completed":
        return "resumable"
    return None


def _partition(
    repo: Path,
    record: dict,
    run_id: str,
    branches: list[str],
    *,
    include_unlanded: bool,
) -> dict:
    """Split one run's branches and worktrees into removed and skipped."""

    recorded = record.get("run_branch")
    checked_out = _worktree_branches(repo, branches)
    dirty = []
    clean = []
    for path, _branch in checked_out:
        if not include_unlanded and _dirty_worktree(path):
            dirty.append(path)
        else:
            clean.append(path)
    held = {branch for path, branch in checked_out if path in dirty and branch}
    unlanded = []
    remove_branches = []
    for branch in branches:
        run_branch = _is_run_branch(branch, run_id, recorded)
        if run_branch and not include_unlanded and not _branch_is_landed(repo, record, branch):
            unlanded.append(branch)
            continue
        if branch in held:
            continue
        remove_branches.append(branch)
    skipped = []
    if unlanded:
        skipped.append({"branches": unlanded, "reason": "unlanded", "run_id": run_id})
    if dirty:
        entry = {"reason": "dirty worktree", "run_id": run_id, "worktrees": dirty}
        kept = sorted(branch for branch in held if branch not in unlanded)
        if kept:
            entry["branches"] = kept
        skipped.append(entry)
    return {"branches": remove_branches, "skipped": skipped, "worktrees": clean}


def _is_run_branch(branch: str, run_id: str, recorded: object) -> bool:
    if branch == f"recursion/run/{run_id}":
        return True
    return isinstance(recorded, str) and bool(recorded) and branch == recorded


def _branch_is_landed(repo: Path, record: dict, branch: str) -> bool:
    land = record.get("land")
    if isinstance(land, dict) and land.get("status") == "merged":
        return True
    if _is_ancestor(repo, branch, "HEAD"):
        return True
    default = _default_branch(repo)
    current = _current_branch(repo)
    if default and default != current and _is_ancestor(repo, branch, default):
        return True
    return False


def _is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    completed = _run(repo, "merge-base", "--is-ancestor", ancestor, descendant)
    return completed.returncode == 0


def _default_branch(repo: Path) -> str | None:
    origin = _run(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if origin.returncode == 0:
        name = origin.stdout.strip()
        if name.startswith("origin/"):
            name = name.split("/", 1)[1]
        if name and _ref_exists(repo, name):
            return name
    configured = _run(repo, "config", "--get", "init.defaultBranch")
    if configured.returncode == 0:
        name = configured.stdout.strip()
        if name and _ref_exists(repo, name):
            return name
    for candidate in ("main", "master"):
        if _ref_exists(repo, candidate):
            return candidate
    return None


def _ref_exists(repo: Path, branch: str) -> bool:
    completed = _run(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
    return completed.returncode == 0


def _dirty_worktree(path: str) -> bool:
    completed = _run(Path(path), "status", "--porcelain")
    if completed.returncode != 0:
        return True
    return bool(completed.stdout.strip())


def _delete(repo: Path, worktrees: list[str], branches: list[str], files: list[Path]) -> None:
    for path in worktrees:
        _quiet(repo, "worktree", "remove", "--force", path)
    if worktrees:
        _quiet(repo, "worktree", "prune")
    for branch in branches:
        _quiet(repo, "branch", "-D", branch)
    for path in files:
        path.unlink(missing_ok=True)


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


def _worktree_branches(repo: Path, branches: list[str]) -> list[tuple[str, str | None]]:
    """Linked worktrees checked out on ``branches``, as ``(path, short branch)``."""

    if not branches:
        return []
    wanted = {f"refs/heads/{name}": name for name in branches}
    completed = _run(repo, "worktree", "list", "--porcelain")
    if completed.returncode != 0:
        return []
    main = Path(repo).resolve()
    found = []
    current = None
    ref = None

    def keep(path: str | None, branch_ref: str | None) -> None:
        if path is None or branch_ref not in wanted:
            return
        try:
            if Path(path).resolve() == main:
                return
        except OSError:
            if path == str(main):
                return
        found.append((path, wanted[branch_ref]))

    for line in completed.stdout.splitlines() + [""]:
        if line.startswith("worktree "):
            keep(current, ref)
            current = line.split(" ", 1)[1]
            ref = None
        elif line.startswith("branch "):
            ref = line.split(" ", 1)[1]
        elif line == "" and current is not None:
            keep(current, ref)
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

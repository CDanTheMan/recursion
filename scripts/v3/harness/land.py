"""Merge a finished run branch into a target branch."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.report import write_reports
from scripts.v3.harness.state import RunStore


_RUN = subprocess.run
_AUTHOR = (
    "-c",
    "user.email=recursion@localhost",
    "-c",
    "user.name=recursion",
    "-c",
    "commit.gpgsign=false",
)


class _Conflict(Exception):
    def __init__(self, paths: list[str]) -> None:
        self.paths = paths


def land_run(store: RunStore, run_id: str, *, repo: Path, into: str | None = None) -> dict:
    """Merge the run branch with a normal merge commit. A dirty tree or conflict is refused."""

    record = store.load(run_id)
    if record.get("status") != "completed":
        raise HarnessError("run is not finished")
    run_branch = record.get("run_branch")
    if not isinstance(run_branch, str) or not run_branch or not _ref_exists(repo, run_branch):
        raise HarnessError("run branch is missing")
    target = _target(repo, into)
    if _dirty(repo):
        _remember(store, run_id, branch=target, commit=None, status="refused", error="working tree is dirty", paths=[])
        raise HarnessError("working tree is dirty")
    message = f"recursion: land {run_id}"
    try:
        commit = _merge(repo, target, run_branch, message)
    except _Conflict as exc:
        _remember(
            store,
            run_id,
            branch=target,
            commit=None,
            status="conflict",
            error="merge conflict",
            paths=exc.paths,
        )
        raise HarnessError("merge conflict") from exc
    _remember(store, run_id, branch=target, commit=commit, status="merged", error=None, paths=[])
    return store.load(run_id)


def _target(repo: Path, into: str | None) -> str:
    if into is None:
        current = _current_branch(repo)
        if current is None:
            raise HarnessError("pass --into when HEAD is detached")
        return current
    if "\n" in into or "\r" in into or into.startswith("-") or not into.strip():
        raise HarnessError("invalid branch name")
    checked = _run(repo, "check-ref-format", "--branch", into)
    if checked.returncode != 0:
        raise HarnessError("invalid branch name")
    if not _ref_exists(repo, into):
        raise HarnessError(f"unknown branch {into}")
    return into


def _remember(
    store: RunStore,
    run_id: str,
    *,
    branch: str,
    commit: str | None,
    status: str,
    error: str | None,
    paths: list[str],
) -> None:
    def remember(current: dict) -> None:
        current["land"] = {
            "branch": branch,
            "commit": commit,
            "error": error,
            "paths": list(paths),
            "status": status,
        }
        current["report"] = write_reports(store.root, current)

    store.update(run_id, remember)


def _merge(repo: Path, target: str, run_branch: str, message: str) -> str:
    if _current_branch(repo) == target:
        return _merge_here(repo, run_branch, message)
    path = Path(tempfile.mkdtemp(prefix="recursion-land-"))
    try:
        _git(repo, "worktree", "add", "--force", str(path), target)
        return _merge_here(path, run_branch, message)
    finally:
        _quiet(repo, "worktree", "remove", "--force", str(path))
        _quiet(repo, "worktree", "prune")
        shutil.rmtree(path, ignore_errors=True)


def _merge_here(cwd: Path, run_branch: str, message: str) -> str:
    completed = _run(cwd, *_AUTHOR, "merge", "--no-ff", "-m", message, run_branch)
    if completed.returncode != 0:
        listed = _run(cwd, "diff", "--name-only", "--diff-filter=U")
        paths = listed.stdout.split()[:20] if listed.returncode == 0 else []
        _quiet(cwd, "merge", "--abort")
        if paths:
            raise _Conflict(paths)
        raise HarnessError("merge failed")
    return _git(cwd, "rev-parse", "HEAD").strip()


def _dirty(repo: Path) -> bool:
    completed = _run(repo, "status", "--porcelain")
    if completed.returncode != 0:
        raise HarnessError("git status failed")
    return bool(completed.stdout.strip())


def _current_branch(repo: Path) -> str | None:
    name = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    if name == "HEAD":
        return None
    return name


def _ref_exists(repo: Path, branch: str) -> bool:
    completed = _run(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
    return completed.returncode == 0


def _git(cwd: Path, *args: str) -> str:
    completed = _run(cwd, *args)
    if completed.returncode != 0:
        raise HarnessError(f"git {args[0]} failed ({completed.returncode})")
    return completed.stdout


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

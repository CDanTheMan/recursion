"""One git worktree and branch per task, removed when the task finishes."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

from scripts.v3.harness.errors import HarnessError


DIFF_LIMIT = 8000
# Keep the real process starter. Provider tests replace
# scripts.v3.harness.providers.run_command to prove a provider CLI did not
# start, and that replacement must not swallow git.
_RUN = subprocess.run


class TaskIsolation:
    """A task checkout. ``path`` is None when isolation is not used."""

    def __init__(self, path: Path | None, branch: str | None, base: str | None) -> None:
        self.path = path
        self.branch = branch
        self.base = base


class NullIsolator:
    """No checkout. Used by library tests that do not need a worktree."""

    def acquire(self, run_id: str, index: int) -> TaskIsolation:
        del run_id, index
        return TaskIsolation(None, None, None)

    def diff(self, item: TaskIsolation) -> str:
        del item
        return ""

    def release(self, item: TaskIsolation) -> None:
        del item


class GitWorktreeIsolator:
    """Add ``recursion/run/<run-id>/task-<index>`` and delete it afterwards."""

    _locks: dict[str, threading.Lock] = {}
    _locks_guard = threading.Lock()

    def __init__(self, repo: Path) -> None:
        self.repo = Path(repo)

    def _lock(self) -> threading.Lock:
        key = str(self.repo.resolve())
        with self._locks_guard:
            lock = self._locks.get(key)
            if lock is None:
                lock = threading.Lock()
                self._locks[key] = lock
            return lock

    def acquire(self, run_id: str, index: int) -> TaskIsolation:
        branch = f"recursion/run/{run_id}/task-{index}"
        path = Path(tempfile.mkdtemp(prefix=f"recursion-{run_id}-{index}-"))
        try:
            with self._lock():
                base = _git(self.repo, "rev-parse", "HEAD").strip()
                _git(self.repo, "worktree", "add", "--force", "-b", branch, str(path), "HEAD")
        except Exception:
            _git_quiet(self.repo, "worktree", "remove", "--force", str(path))
            _git_quiet(self.repo, "branch", "-D", branch)
            shutil.rmtree(path, ignore_errors=True)
            raise
        return TaskIsolation(path, branch, base)

    def diff(self, item: TaskIsolation) -> str:
        if item.path is None or item.base is None:
            return ""
        parts = []
        commits = _git(item.path, "log", "--oneline", f"{item.base}..HEAD").strip()
        if commits:
            parts.append("commits:\n" + commits)
        changes = _git(item.path, "diff", item.base).strip()
        if changes:
            parts.append(changes)
        status = _git(item.path, "status", "--porcelain").strip()
        if status:
            parts.append("status:\n" + status)
        text = "\n".join(parts)
        if len(text) > DIFF_LIMIT:
            return text[:DIFF_LIMIT] + "\n[diff truncated]"
        return text

    def release(self, item: TaskIsolation) -> None:
        if item.path is None or item.branch is None:
            return
        with self._lock():
            _git_quiet(self.repo, "worktree", "remove", "--force", str(item.path))
            _git_quiet(self.repo, "worktree", "prune")
            _git_quiet(self.repo, "branch", "-D", item.branch)
        shutil.rmtree(item.path, ignore_errors=True)


def _git(cwd: Path, *args: str) -> str:
    completed = _run_git(cwd, *args)
    if completed.returncode != 0:
        raise HarnessError(f"git {args[0]} failed ({completed.returncode})")
    return completed.stdout


def _git_quiet(cwd: Path, *args: str) -> None:
    _run_git(cwd, *args)


def _run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _RUN(
        ["git", "-c", "core.longpaths=true", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

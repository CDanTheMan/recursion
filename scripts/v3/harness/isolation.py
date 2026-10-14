"""One git worktree and branch per task. Accepted work stays on the branch."""

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
_AUTHOR = ("-c", "user.email=recursion@localhost", "-c", "user.name=recursion")


class TaskIsolation:
    """A task checkout. ``path`` is None when isolation is not used."""

    def __init__(self, path: Path | None, branch: str | None, base: str | None) -> None:
        self.path = path
        self.branch = branch
        self.base = base


class NullIsolator:
    """No checkout. Used by library tests that do not need a worktree."""

    def acquire(self, run_id: str, index: int, start_ref: str | None = None) -> TaskIsolation:
        del run_id, index, start_ref
        return TaskIsolation(None, None, None)

    def diff(self, item: TaskIsolation) -> str:
        del item
        return ""

    def commit_pending(self, item: TaskIsolation, message: str) -> str | None:
        del item, message
        return None

    def snapshot(self, item: TaskIsolation) -> str | None:
        del item
        return None

    def restore(self, item: TaskIsolation, head: str | None) -> bool:
        del item, head
        return False

    def ensure_run_branch(self, run_id: str, base_ref: str) -> str | None:
        del run_id, base_ref
        return None

    def merge_into_run(self, run_branch: str | None, task_branch: str) -> dict:
        del run_branch, task_branch
        return {"commit": None, "paths": [], "status": "landed"}

    def delete_run_branch(self, branch: str | None) -> bool:
        del branch
        return True

    def release(self, item: TaskIsolation, *, keep_branch: bool = False, keep_worktree: bool = False) -> None:
        del item, keep_branch, keep_worktree


class GitWorktreeIsolator:
    """Check out ``recursion/task/<run-id>/task-<index>`` from the run branch.

    The run branch is ``recursion/run/<run-id>``. Task branches live in a
    separate namespace so git can store both refs.
    """

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

    def ensure_run_branch(self, run_id: str, base_ref: str) -> str:
        branch = run_branch_name(run_id)
        with self._lock():
            if _ref_exists(self.repo, branch):
                return branch
            _git(self.repo, "branch", branch, base_ref)
        return branch

    def acquire(self, run_id: str, index: int, start_ref: str | None = None) -> TaskIsolation:
        branch = task_branch_name(run_id, index)
        start = start_ref or "HEAD"
        path = Path(tempfile.mkdtemp(prefix=f"recursion-{run_id}-{index}-"))
        try:
            with self._lock():
                _git_quiet(self.repo, "worktree", "prune")
                for checkout in _worktrees_for(self.repo, branch):
                    _git_quiet(self.repo, "worktree", "remove", "--force", checkout)
                _git_quiet(self.repo, "branch", "-D", branch)
                base = _git(self.repo, "rev-parse", start).strip()
                _git(self.repo, "worktree", "add", "--force", "-b", branch, str(path), start)
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

    def commit_pending(self, item: TaskIsolation, message: str) -> str | None:
        """Commit uncommitted edits. A commit the provider already made is kept."""

        if item.path is None or item.base is None:
            return None
        status = _git(item.path, "status", "--porcelain").strip()
        if status:
            _git(item.path, "add", "-A")
            _git(item.path, *_AUTHOR, "commit", "-m", message)
        head = _git(item.path, "rev-parse", "HEAD").strip()
        if head == item.base:
            return None
        return head

    def snapshot(self, item: TaskIsolation) -> str | None:
        if item.path is None:
            return None
        return _git(item.path, "rev-parse", "HEAD").strip()

    def restore(self, item: TaskIsolation, head: str | None) -> bool:
        """Drop reviewer edits. Return true when the tree or HEAD changed."""

        if item.path is None or head is None:
            return False
        now = _git(item.path, "rev-parse", "HEAD").strip()
        status = _git(item.path, "status", "--porcelain").strip()
        if now == head and status == "":
            return False
        _git(item.path, "reset", "--hard", head)
        _git(item.path, "clean", "-fd")
        return True

    def merge_into_run(self, run_branch: str | None, task_branch: str) -> dict:
        """Merge one task branch. A conflict aborts and names the paths."""

        if run_branch is None:
            return {"commit": None, "paths": [], "status": "landed"}
        path = Path(tempfile.mkdtemp(prefix="recursion-integrate-"))
        try:
            with self._lock():
                _git_quiet(self.repo, "worktree", "prune")
                _git(self.repo, "worktree", "add", "--force", str(path), run_branch)
                completed = _run_git(
                    path,
                    *_AUTHOR,
                    "merge",
                    "--no-ff",
                    "-m",
                    f"recursion: integrate {task_branch}",
                    task_branch,
                )
                if completed.returncode != 0:
                    names = _git(path, "diff", "--name-only", "--diff-filter=U").split()
                    _git_quiet(path, "merge", "--abort")
                    return {"commit": None, "paths": names[:20], "status": "conflict"}
                commit = _git(path, "rev-parse", "HEAD").strip()
                return {"commit": commit, "paths": [], "status": "landed"}
        finally:
            with self._lock():
                _git_quiet(self.repo, "worktree", "remove", "--force", str(path))
                _git_quiet(self.repo, "worktree", "prune")
            shutil.rmtree(path, ignore_errors=True)

    def delete_run_branch(self, branch: str | None) -> bool:
        """Remove an empty run branch. Return true when it no longer exists."""

        if not branch:
            return True
        with self._lock():
            if not _ref_exists(self.repo, branch):
                return True
            for checkout in _worktrees_for(self.repo, branch):
                _git_quiet(self.repo, "worktree", "remove", "--force", checkout)
            completed = _run_git(self.repo, "branch", "-D", branch)
            return completed.returncode == 0

    def release(self, item: TaskIsolation, *, keep_branch: bool = False, keep_worktree: bool = False) -> None:
        if item.path is None or item.branch is None:
            return
        if keep_worktree:
            return
        with self._lock():
            _git_quiet(self.repo, "worktree", "remove", "--force", str(item.path))
            _git_quiet(self.repo, "worktree", "prune")
            if not keep_branch:
                _git_quiet(self.repo, "branch", "-D", item.branch)
        shutil.rmtree(item.path, ignore_errors=True)


def run_branch_name(run_id: str) -> str:
    return f"recursion/run/{run_id}"


def task_branch_name(run_id: str, index: int) -> str:
    return f"recursion/task/{run_id}/task-{index}"


def _worktrees_for(repo: Path, branch: str) -> list[str]:
    """Paths currently checked out at ``branch``, excluding the main worktree."""

    completed = _run_git(repo, "worktree", "list", "--porcelain")
    wanted = f"refs/heads/{branch}"
    found = []
    current = None
    ref = None
    main = str(repo.resolve())
    for line in completed.stdout.splitlines() + [""]:
        if line.startswith("worktree "):
            if current is not None and ref == wanted and str(Path(current).resolve()) != main:
                found.append(current)
            current = line.split(" ", 1)[1]
            ref = None
        elif line.startswith("branch "):
            ref = line.split(" ", 1)[1]
        elif line == "" and current is not None:
            if ref == wanted and str(Path(current).resolve()) != main:
                found.append(current)
            current = None
            ref = None
    return found


def _ref_exists(repo: Path, branch: str) -> bool:
    completed = _run_git(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
    return completed.returncode == 0


def _git(cwd: Path, *args: str) -> str:
    completed = _run_git(cwd, *args)
    if completed.returncode != 0:
        raise HarnessError(f"git {_command_name(args)} failed ({completed.returncode})")
    return completed.stdout


def _command_name(args: tuple[str, ...]) -> str:
    skip_value = False
    for arg in args:
        if skip_value:
            skip_value = False
            continue
        if arg == "-c":
            skip_value = True
            continue
        if not arg.startswith("-"):
            return arg
    return "command"


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

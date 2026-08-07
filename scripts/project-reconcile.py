#!/usr/bin/env python3
"""Deterministic Phase 6 measurable-goal reconciliation.

This module never launches a worker or publishes a ref from its scheduler/reconcile paths.
It observes canonical files plus process/git evidence and emits idempotent decisions into the
existing Phase 3 queue.  The existing sole actuator later executes those decisions as durable
actions.  Mutating subcommands are therefore actuator verbs, not alternate control paths.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable


IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
TERMINAL_GOALS = {"achieved", "blocked", "abandoned", "budget-exhausted", "paused"}
ACTIVE_GOALS = {"active", "verifying"}
TERMINAL_TASKS = {"passed", "failed", "blocked", "escalated", "cancelled", "moot", "resolved"}
TASK_TRANSITIONS = {
    ("proposed", "ready"),
    ("failed", "ready"),
    ("stale", "ready"),
    ("running", "stale"),
    ("leased", "stale"),
    ("ready", "blocked"),
    ("queued", "blocked"),
}
GOAL_TRANSITIONS = {
    ("approved", "active"),
    ("active", "verifying"),
    ("active", "blocked"),
    ("active", "abandoned"),
    ("active", "budget-exhausted"),
    ("active", "paused"),
    ("verifying", "achieved"),
    ("verifying", "active"),
    ("verifying", "blocked"),
    ("verifying", "budget-exhausted"),
    ("verifying", "paused"),
    ("blocked", "active"),
    ("paused", "active"),
}
REQUIRED_BUDGET = {
    "max_concurrency", "max_tokens", "max_cost_usd", "max_wall_clock_seconds",
    "max_task_attempts", "max_failures", "max_review_queue", "max_publish_attempts",
    "publication_required",
}


class ReconcileError(RuntimeError):
    pass


def root() -> Path:
    return Path(os.environ.get("RECURSION_ROOT") or Path(__file__).resolve().parent.parent)


def fail(message: str, code: int = 4) -> None:
    print(f"project-reconcile: {message}", file=sys.stderr)
    raise SystemExit(code)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            out.write(text)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
        fsync_dir(path.parent)
    finally:
        try:
            os.unlink(name)
        except FileNotFoundError:
            pass


def atomic_json(path: Path, value: dict) -> None:
    atomic_text(path, json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReconcileError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReconcileError(f"state record is not an object: {path}")
    return value


def read_fields(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    except OSError as exc:
        raise ReconcileError(f"cannot read {path}: {exc}") from exc
    for line in lines:
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            result.setdefault(key.strip(), value.strip())
    return result


def rewrite_fields(path: Path, changes: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    found: set[str] = set()
    output: list[str] = []
    for line in lines:
        key = line.split(":", 1)[0].strip() if ":" in line and not line.startswith((" ", "\t")) else ""
        if key in changes and key not in found:
            output.append(f"{key}: {changes[key]}")
            found.add(key)
        else:
            output.append(line)
    for key, value in changes.items():
        if key not in found:
            output.append(f"{key}: {value}")
    atomic_text(path, "\n".join(output) + "\n")


def append_event(base: Path, event: str, project: str, goal: str, task: str = "", detail: object = "") -> None:
    value = {
        "schema_version": 1,
        "ts": now_iso(),
        "event": event,
        "project": project,
        "goal": goal,
        "task": task,
        "pid": os.getpid(),
        "detail": detail,
    }
    path = base / "state/events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)


@contextmanager
def goal_lock(base: Path, goal_id: str):
    lock_dir = base / "state/.locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    path = lock_dir / f"reconcile-{goal_id}.lock"
    with path.open("a+", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ReconcileError(f"goal lock contended: {goal_id}") from exc
        yield


def goal_path(base: Path, goal_id: str) -> Path:
    direct = base / "state/goals" / f"{goal_id}.md"
    if direct.is_file() and read_fields(direct).get("id") == goal_id:
        return direct
    for path in sorted((base / "state/goals").glob("*.md")):
        if read_fields(path).get("id") == goal_id:
            return path
    raise ReconcileError(f"goal absent: {goal_id}")


def project_records(base: Path, project: str) -> tuple[dict, dict]:
    config = read_json(base / "state/project-config" / f"{project}.json")
    pilot_id = str(config.get("pilot_id") or "")
    if config.get("id") != project or not IDENT.fullmatch(pilot_id):
        raise ReconcileError("project identity or pilot binding is invalid")
    pilot = read_json(base / "state/pilots" / f"{pilot_id}.json")
    if pilot.get("id") != pilot_id or pilot.get("project_id") != project:
        raise ReconcileError("pilot identity is inconsistent")
    if config.get("status") != "active" or pilot.get("status") != "active":
        raise ReconcileError("project pilot is not active")
    return config, pilot


def goal_tasks(base: Path, goal_id: str) -> list[tuple[Path, dict[str, str]]]:
    result = []
    for path in sorted((base / "state/tasks").glob("*.md")):
        value = read_fields(path)
        if value.get("goal_id") == goal_id:
            result.append((path, value))
    return result


def dependencies(task: dict[str, str]) -> list[str]:
    raw = task.get("dependencies", "").replace(" ", ",")
    return [item for item in raw.split(",") if item and item != "-"]


def parse_budget(goal: dict[str, str]) -> dict:
    try:
        value = json.loads(goal.get("budget", ""))
    except json.JSONDecodeError as exc:
        raise ReconcileError("Phase 6 goal budget is not a JSON object") from exc
    if not isinstance(value, dict) or not REQUIRED_BUDGET <= value.keys():
        missing = sorted(REQUIRED_BUDGET - set(value if isinstance(value, dict) else {}))
        raise ReconcileError("Phase 6 goal budget is incomplete: " + ",".join(missing))
    integer_fields = (
        "max_concurrency", "max_tokens", "max_wall_clock_seconds", "max_task_attempts",
        "max_failures", "max_review_queue", "max_publish_attempts",
    )
    for field in integer_fields:
        if isinstance(value[field], bool) or not isinstance(value[field], int) or value[field] < 0:
            raise ReconcileError(f"invalid budget field: {field}")
    cost = value["max_cost_usd"]
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
        raise ReconcileError("invalid budget field: max_cost_usd")
    if not isinstance(value["publication_required"], bool):
        raise ReconcileError("invalid budget field: publication_required")
    if "max_retries" in value and (
        isinstance(value["max_retries"], bool) or not isinstance(value["max_retries"], int)
        or value["max_retries"] < 0
    ):
        raise ReconcileError("invalid budget field: max_retries")
    return value


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def process_alive(pid: object) -> bool:
    number = safe_int(pid)
    if number < 1:
        return False
    try:
        os.kill(number, 0)
        return True
    except (OSError, ProcessLookupError, PermissionError):
        return False


def run_records(base: Path, task_ids: set[str]) -> list[dict]:
    result = []
    for path in sorted((base / "state/runs").glob("*.json")):
        try:
            row = read_json(path)
        except ReconcileError:
            continue
        if row.get("task_id") in task_ids:
            row = dict(row)
            row["_path"] = str(path)
            result.append(row)
    return result


def action_records(base: Path, goal_id: str) -> list[dict]:
    result = []
    for path in sorted((base / "state/actions").glob("*.json")):
        try:
            row = read_json(path)
        except ReconcileError:
            continue
        if row.get("goal_id") == goal_id:
            row = dict(row)
            row["_path"] = str(path)
            result.append(row)
    return result


def usage_totals(runs: Iterable[dict]) -> tuple[int, float, bool]:
    tokens = 0
    cost = 0.0
    complete = True
    for row in runs:
        usage = row.get("usage")
        if not isinstance(usage, dict):
            complete = False
            continue
        token_value = usage.get("tokens", usage.get("total_tokens"))
        if token_value is None:
            incoming = usage.get("input_tokens")
            outgoing = usage.get("output_tokens")
            token_value = (incoming + outgoing) if isinstance(incoming, int) and isinstance(outgoing, int) else None
        cost_value = usage.get("cost_usd", usage.get("estimated_cost_usd"))
        if row.get("status") == "succeeded" and (token_value is None or cost_value is None):
            complete = False
        if isinstance(token_value, int) and not isinstance(token_value, bool) and token_value >= 0:
            tokens += token_value
        if isinstance(cost_value, (int, float)) and not isinstance(cost_value, bool) and math.isfinite(cost_value):
            cost += float(cost_value)
    return tokens, cost, complete


def git_output(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=False)
    if proc.returncode:
        raise ReconcileError((proc.stderr or proc.stdout or f"git {' '.join(args)} failed").strip())
    return proc.stdout.strip()


def git_environment(config: dict) -> dict[str, str]:
    env = os.environ.copy()
    key = str(config.get("deploy_key_ref") or "")
    remote = str(config.get("remote") or "")
    if key and key != "-" and remote.startswith("git@"):
        resolved = os.path.expanduser(key)
        env["GIT_SSH_COMMAND"] = (
            f"ssh -i {resolved} -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"
        )
    return env


def fresh_base(config: dict) -> tuple[bool, str, str]:
    repo = Path(str(config.get("repo") or ""))
    branch = str(config.get("default_branch") or "")
    remote = str(config.get("remote") or "origin")
    if not (repo / ".git").exists() or not branch:
        return False, "", "clone-absent"
    try:
        local = git_output(repo, "rev-parse", branch)
    except ReconcileError:
        return False, "", "default-branch-absent"
    proc = subprocess.run(
        ["git", "ls-remote", remote, f"refs/heads/{branch}"],
        text=True, capture_output=True, check=False, timeout=20, env=git_environment(config),
    )
    words = proc.stdout.split()
    if proc.returncode or not words:
        return False, local, "remote-head-unprovable"
    remote_head = words[0]
    return local == remote_head, local, "fresh" if local == remote_head else "stale-base"


def task_evidence(base: Path, repo: Path, task: dict[str, str], runs: list[dict]) -> tuple[bool, str, dict]:
    task_id = task.get("id", "")
    related = [row for row in runs if row.get("task_id") == task_id]
    implementers = [row for row in related if row.get("role") == "implementer"]
    verifiers = [row for row in related if row.get("role") == "verifier"]
    if not implementers or not verifiers:
        return False, "exact implementer/verifier evidence is absent", {}
    implementer = implementers[-1]
    gate = implementer.get("machine_gate") if isinstance(implementer.get("machine_gate"), dict) else {}
    link = implementer.get("verification") if isinstance(implementer.get("verification"), dict) else {}
    commit = str(task.get("candidate_commit") or gate.get("commit_oid") or implementer.get("commit_oid") or "")
    verifier_id = str(link.get("verifier_run_id") or "")
    verifier = next((row for row in verifiers if row.get("id") == verifier_id), verifiers[-1])
    verification = verifier.get("verification") if isinstance(verifier.get("verification"), dict) else {}
    valid = bool(
        re.fullmatch(r"[0-9a-f]{40,64}", commit)
        and gate.get("commit_oid") == commit
        and (gate.get("passed") is True or gate.get("exit_code") == 0)
        and link.get("commit_oid") == commit
        and link.get("verdict") == "pass"
        and verification.get("commit_oid") == commit
        and verification.get("implementer_run_id") == implementer.get("id")
        and verification.get("verdict") == "pass"
        and verifier.get("id") != implementer.get("id")
    )
    if not valid:
        return False, "machine gate and independent verifier disagree", {"commit_oid": commit}
    try:
        branch_commit = git_output(repo, "rev-parse", f"refs/heads/loop/work/{task_id}")
    except ReconcileError:
        return False, "canonical local review ref is absent", {"commit_oid": commit}
    if branch_commit != commit:
        return False, "review ref does not resolve to the verified commit", {"commit_oid": commit}
    return True, "verified", {
        "commit_oid": commit,
        "implementer_run_id": implementer.get("id"),
        "verifier_run_id": verifier.get("id"),
        "machine_gate": gate,
        "independent_verifier": verification,
    }


def remote_review_commit(config: dict, task_id: str) -> str:
    remote = str(config.get("remote") or "origin")
    proc = subprocess.run(
        ["git", "ls-remote", remote, f"refs/heads/loop/work/{task_id}"],
        text=True, capture_output=True, check=False, timeout=20, env=git_environment(config),
    )
    return proc.stdout.split()[0] if proc.returncode == 0 and proc.stdout.split() else ""


def decision_key(*parts: object) -> str:
    raw = json.dumps(parts, sort_keys=True, separators=(",", ":")).encode()
    return "phase6:" + hashlib.sha256(raw).hexdigest()


def enqueue_decision(base: Path, actor: str, verb: str, args: list[str], goal_id: str,
                     reason: str, key_parts: list[object]) -> Path:
    raw = {
        "actor": actor,
        "verb": verb,
        "args": args,
        "project": args[0] if args else "",
        "goal": goal_id,
        "why": reason,
        "wrong_if": "canonical state or exact evidence changes before compare-and-swap",
        "idempotency_key": decision_key(verb, *key_parts),
    }
    proc = subprocess.run(
        [sys.executable, str(base / "scripts/decision-queue.py"), "enqueue"],
        input=json.dumps(raw), text=True, capture_output=True, check=False,
        env={**os.environ, "RECURSION_ROOT": str(base)},
    )
    if proc.returncode:
        raise ReconcileError((proc.stderr or proc.stdout or "decision enqueue failed").strip())
    return Path(proc.stdout.strip())


def snapshot_digest(base: Path, config: dict, goal_id: str) -> str:
    paths: list[Path] = [goal_path(base, goal_id)]
    tasks = goal_tasks(base, goal_id)
    paths.extend(path for path, _ in tasks)
    task_ids = {value.get("id", "") for _, value in tasks}
    for directory in ("state/runs", "state/actions", "state/deliveries"):
        for path in sorted((base / directory).glob("*.json")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if goal_id in text or any(task_id and task_id in text for task_id in task_ids):
                paths.append(path)
    digest = hashlib.sha256()
    for path in sorted(set(paths)):
        digest.update(str(path.relative_to(base)).encode())
        digest.update(path.read_bytes())
    repo = Path(str(config.get("repo") or ""))
    if (repo / ".git").exists():
        for namespace in ("refs/heads/loop/work", "refs/remotes/origin/loop/work"):
            proc = subprocess.run(
                ["git", "-C", str(repo), "for-each-ref", "--format=%(refname) %(objectname)", namespace],
                text=True, capture_output=True, check=False,
            )
            digest.update(proc.stdout.encode())
    return digest.hexdigest()


def recovery_snapshot(base: Path, config: dict, goal: dict[str, str], tasks: list[tuple[Path, dict[str, str]]],
                      runs: list[dict], actions: list[dict]) -> dict:
    repo = Path(str(config.get("repo") or ""))
    running = [task.get("id") for _, task in tasks if task.get("status") in {"leased", "running"}]
    live = sorted({str(row.get("task_id")) for row in runs if row.get("status") == "running" and process_alive(row.get("pid"))})
    dead = sorted(set(filter(None, running)) - set(live))
    worktrees = []
    for root_path in (base / ".worktrees", repo / ".worktrees"):
        if root_path.is_dir():
            worktrees.extend(str(path) for path in sorted(root_path.iterdir()) if path.is_dir())
    refs = []
    if (repo / ".git").exists():
        proc = subprocess.run(
            ["git", "-C", str(repo), "for-each-ref", "--format=%(refname):%(objectname)", "refs/heads/loop/work"],
            text=True, capture_output=True, check=False,
        )
        refs = [line for line in proc.stdout.splitlines() if line]
    deliveries = []
    for path in sorted((base / "state/deliveries").glob("*.json")):
        try:
            row = read_json(path)
        except ReconcileError:
            deliveries.append({"file": str(path), "status": "corrupt"})
        else:
            deliveries.append({"id": row.get("id"), "event_id": row.get("event_id"), "status": row.get("status")})
    return {
        "task_files": len(tasks),
        "running_tasks": sorted(filter(None, running)),
        "live_process_tasks": live,
        "dead_process_tasks": dead,
        "run_records": len(runs),
        "worktrees": worktrees,
        "git_refs": refs,
        "action_records": len(actions),
        "event_log_present": (base / "state/events.jsonl").is_file(),
        "deliveries": deliveries,
    }


def record_recovery(base: Path, project: str, goal_id: str, snapshot: dict) -> None:
    interesting = bool(
        snapshot["dead_process_tasks"] or snapshot["worktrees"] or snapshot["git_refs"]
        or snapshot["deliveries"]
    )
    if not interesting:
        return
    raw = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()
    identity = hashlib.sha256(raw).hexdigest()
    projection = base / "state/recovery" / f"{goal_id}-{identity[:24]}.json"
    if projection.exists():
        return
    atomic_json(projection, {"schema_version": 1, "id": f"recovery-{identity[:24]}",
                             "project_id": project, "goal_id": goal_id,
                             "observed_at": now_iso(), "snapshot": snapshot})
    append_event(base, "recovery-reconciled", project, goal_id, detail=snapshot)


def transition_task(base: Path, project: str, goal_id: str, task_id: str,
                    expected: str, target: str, reason: str) -> None:
    if (expected, target) not in TASK_TRANSITIONS:
        raise ReconcileError(f"refusing task transition {expected}->{target}")
    path = base / "state/tasks" / f"{task_id}.md"
    current = read_fields(path)
    if current.get("project_id") != project or current.get("goal_id") != goal_id:
        raise ReconcileError("task transition crossed project or goal scope")
    proc = subprocess.run(
        ["bash", str(base / "scripts/taskctl.sh"), "cas", task_id, expected, target, reason],
        text=True, capture_output=True, check=False,
        env={**os.environ, "RECURSION_ROOT": str(base)},
    )
    if proc.returncode:
        raise ReconcileError((proc.stderr or proc.stdout or "task CAS failed").strip())


def transition_goal(base: Path, project: str, goal_id: str, expected: str, target: str, reason: str) -> None:
    if (expected, target) not in GOAL_TRANSITIONS:
        raise ReconcileError(f"refusing goal transition {expected}->{target}")
    path = goal_path(base, goal_id)
    with goal_lock(base, goal_id):
        current = read_fields(path)
        if current.get("project_id") != project or current.get("status") != expected:
            raise ReconcileError(f"goal compare-and-swap failed: expected {expected}, found {current.get('status')}")
        if expected == "verifying" and target == "active":
            evidence = goal_evidence(base, goal_id)
            if not evidence or evidence.get("verdict") not in {"fail", "blocked", "timeout", "corrupt"}:
                raise ReconcileError("verification may reopen a goal only with failing evidence")
        version = safe_int(current.get("version"), 1) + 1
        changes = {"status": target, "version": str(version), "last_transition_at": now_iso(),
                   "last_transition_reason": reason}
        if target in TERMINAL_GOALS:
            changes["terminal_reported"] = "1"
            changes["finished_at"] = now_iso()
        rewrite_fields(path, changes)
        append_event(base, "goal-transition", project, goal_id,
                     detail={"from": expected, "to": target, "reason": reason, "version": version})
        if target in TERMINAL_GOALS:
            append_event(base, "goal-terminal", project, goal_id,
                         detail={"status": target, "reason": reason, "version": version})


def publish_task(base: Path, project: str, goal_id: str, task_id: str) -> None:
    config, pilot = project_records(base, project)
    task = read_fields(base / "state/tasks" / f"{task_id}.md")
    if task.get("goal_id") != goal_id or task.get("status") != "passed":
        raise ReconcileError("only a passed task in this goal may be published")
    repo = Path(str(config["repo"]))
    runs = run_records(base, {task_id})
    valid, reason, evidence = task_evidence(base, repo, task, runs)
    if not valid:
        raise ReconcileError(f"publication lacks exact verification: {reason}")
    branch = f"loop/work/{task_id}"
    args = ["bash", str(base / "scripts/publish.sh"), "--branch", branch, "--repo", str(repo)]
    key = str(config.get("deploy_key_ref") or "")
    if key and key != "-":
        args.extend(["--key", key])
    proc = subprocess.run(args, text=True, capture_output=True, check=False,
                          env={**os.environ, "RECURSION_ROOT": str(base)})
    if proc.returncode:
        raise ReconcileError((proc.stderr or proc.stdout or "review publisher failed").strip())
    remote = remote_review_commit(config, task_id)
    if remote != evidence["commit_oid"]:
        raise ReconcileError("publisher returned success but exact remote review ref was not proven")
    append_event(base, "review-published", project, goal_id, task_id,
                 {"branch": branch, "commit_oid": remote})


def terminate_group(pgid: int) -> None:
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.05)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_gate_interruptibly(base: Path, cwd: Path, command: str, deadline: int) -> tuple[str, int]:
    process = subprocess.Popen(["bash", "-c", command], cwd=cwd, start_new_session=True)
    while process.poll() is None:
        if (base / "state/PAUSE").exists():
            terminate_group(process.pid)
            process.wait()
            return "paused", 75
        if time.time() >= deadline:
            terminate_group(process.pid)
            process.wait()
            return "timeout", 124
        time.sleep(0.05)
    return ("pass", 0) if process.returncode == 0 else ("fail", int(process.returncode or 1))


def verify_goal(base: Path, project: str, goal_id: str) -> None:
    config, pilot = project_records(base, project)
    goal = read_fields(goal_path(base, goal_id))
    if goal.get("status") != "verifying":
        raise ReconcileError("goal verification requires status=verifying")
    budget = parse_budget(goal)
    tasks = goal_tasks(base, goal_id)
    if not tasks or any(task.get("status") != "passed" for _, task in tasks):
        raise ReconcileError("goal verification requires every task passed")
    repo = Path(str(config["repo"]))
    runs = run_records(base, {task.get("id", "") for _, task in tasks})
    sink_ids = {task.get("id", "") for _, task in tasks}
    for _, task in tasks:
        sink_ids.difference_update(dependencies(task))
    if len(sink_ids) != 1:
        raise ReconcileError("goal has no unique final review commit")
    sink = next(task for _, task in tasks if task.get("id") in sink_ids)
    exact_by_task: dict[str, dict] = {}
    valid = True; reason = "verified"; exact: dict = {}
    for _, task in tasks:
        task_valid, task_reason, task_exact = task_evidence(base, repo, task, runs)
        if not task_valid:
            valid = False; reason = task_reason; exact = task_exact; break
        exact_by_task[str(task["id"])] = task_exact
    if valid:
        exact = exact_by_task[str(sink["id"])]
        for task_id, task_exact in exact_by_task.items():
            if task_id == sink["id"]:
                continue
            ancestor = subprocess.run(
                ["git", "-C", str(repo), "merge-base", "--is-ancestor",
                 str(task_exact["commit_oid"]), str(exact["commit_oid"])],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
            )
            if ancestor.returncode:
                valid = False
                reason = f"verified dependency commit {task_id} is absent from the final review commit"
                break
    evidence_path = base / "state/evidence" / f"{goal_id}.json"
    if not valid:
        value = {"schema_version": 1, "id": f"goal-evidence-{goal_id}", "project_id": project,
                 "goal_id": goal_id, "verdict": "fail", "reason": reason,
                 "checked_at": now_iso(), "commit_oid": exact.get("commit_oid")}
        atomic_json(evidence_path, value)
        append_event(base, "goal-verification", project, goal_id, detail=value)
        return
    if budget["publication_required"] and remote_review_commit(config, str(sink["id"])) != exact["commit_oid"]:
        raise ReconcileError("goal verification requires the exact published review ref")
    commit = exact["commit_oid"]
    verify_root = repo / ".worktrees"
    verify_root.mkdir(parents=True, exist_ok=True)
    worktree = verify_root / f"goal-{goal_id}-verify-{commit[:12]}-{os.getpid()}"
    proc = subprocess.run(["git", "-C", str(repo), "worktree", "add", "--detach", str(worktree), commit],
                          text=True, capture_output=True, check=False)
    if proc.returncode:
        raise ReconcileError((proc.stderr or proc.stdout or "goal verification worktree failed").strip())
    started = int(time.time())
    wall_deadline = safe_int(goal.get("started_at_epoch"), started) + int(budget["max_wall_clock_seconds"])
    try:
        outcome, rc = run_gate_interruptibly(base, worktree, goal["acceptance_suite"], wall_deadline)
        head = git_output(worktree, "rev-parse", "HEAD")
        dirty = git_output(worktree, "status", "--porcelain", "--untracked-files=all")
        if outcome == "pass" and rc == 0 and head == commit and not dirty:
            verdict = "pass"
        elif outcome == "pass":
            verdict = "fail"
        else:
            verdict = outcome
        value = {"schema_version": 1, "id": f"goal-evidence-{goal_id}", "project_id": project,
                 "goal_id": goal_id, "verdict": verdict, "exit_code": rc,
                 "commit_oid": commit, "acceptance_suite": goal["acceptance_suite"],
                 "implementer_run_id": exact["implementer_run_id"],
                 "verifier_run_id": exact["verifier_run_id"],
                 "machine_gate": exact["machine_gate"],
                 "independent_verifier": exact["independent_verifier"],
                 "checked_at": now_iso(), "worktree_clean": not bool(dirty)}
        atomic_json(evidence_path, value)
        append_event(base, "goal-verification", project, goal_id, detail=value)
        if outcome == "paused":
            raise ReconcileError("PAUSE interrupted exact-commit goal verification")
    finally:
        subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def goal_evidence(base: Path, goal_id: str) -> dict | None:
    path = base / "state/evidence" / f"{goal_id}.json"
    if not path.is_file():
        return None
    try:
        return read_json(path)
    except ReconcileError:
        return {"verdict": "corrupt"}


def enqueue_transition(base: Path, pilot: dict, project: str, goal_id: str, expected: str,
                       target: str, reason: str, version: str) -> None:
    enqueue_decision(base, str(pilot["id"]), "goal-transition",
                     [project, goal_id, expected, target, reason], goal_id, reason,
                     [project, goal_id, expected, target, reason, version])


def reconcile(base: Path, project: str, goal_id: str) -> None:
    config, pilot = project_records(base, project)
    goal_file = goal_path(base, goal_id)
    with goal_lock(base, goal_id):
        goal = read_fields(goal_file)
        if goal.get("project_id") != project:
            raise ReconcileError("goal is outside this project pilot")
        status = goal.get("status", "")
        if status in TERMINAL_GOALS:
            return
        if status not in ACTIVE_GOALS:
            raise ReconcileError(f"goal is not reconcilable: {status}")
        budget = parse_budget(goal)
        tasks = goal_tasks(base, goal_id)
        task_by_id = {task.get("id", ""): task for _, task in tasks}
        task_ids = set(task_by_id)
        runs = run_records(base, task_ids)
        actions = action_records(base, goal_id)
        recovery = recovery_snapshot(base, config, goal, tasks, runs, actions)
        record_recovery(base, project, goal_id, recovery)

        version = goal.get("version", "1")
        if status == "verifying":
            # Refusal to create tasks is also enforced by project-pilot.goal_for. Reconciliation
            # only verifies or evidence-backed reopens; it never plans new work in this state.
            invalid = None
            repo = Path(str(config["repo"]))
            for _, task in tasks:
                if task.get("status") != "passed":
                    invalid = "verification-task-not-passed"
                    break
                valid, reason, _ = task_evidence(base, repo, task, runs)
                if not valid:
                    invalid = "verification-evidence-disagreement"
                    break
            if invalid:
                enqueue_transition(base, pilot, project, goal_id, "verifying", "blocked", invalid, version)
                return
            evidence = goal_evidence(base, goal_id)
            if evidence is None:
                enqueue_decision(base, str(pilot["id"]), "verify-goal", [project, goal_id], goal_id,
                                 "run exact-commit goal acceptance", [project, goal_id, snapshot_digest(base, config, goal_id)])
            elif evidence.get("verdict") == "pass":
                enqueue_transition(base, pilot, project, goal_id, "verifying", "achieved",
                                   "exact-commit-verified", version)
            else:
                enqueue_transition(base, pilot, project, goal_id, "verifying", "active",
                                   "verification-reopened", version)
            return

        started = safe_int(goal.get("started_at_epoch"), int(time.time()))
        if int(time.time()) - started > budget["max_wall_clock_seconds"]:
            enqueue_transition(base, pilot, project, goal_id, "active", "budget-exhausted",
                               "wall-clock-budget", version)
            return
        tokens, cost, usage_complete = usage_totals(runs)
        if tokens > budget["max_tokens"]:
            enqueue_transition(base, pilot, project, goal_id, "active", "budget-exhausted",
                               "token-budget", version)
            return
        if cost > float(budget["max_cost_usd"]):
            enqueue_transition(base, pilot, project, goal_id, "active", "budget-exhausted",
                               "cost-budget", version)
            return
        if runs and not usage_complete:
            enqueue_transition(base, pilot, project, goal_id, "active", "blocked",
                               "usage-evidence-absent", version)
            return

        failures = sum(task.get("status") == "failed" for _, task in tasks)
        retries = sum(max(safe_int(task.get("attempts")) - 1, 0) for _, task in tasks)
        retry_limit = safe_int(budget.get("max_retries"),
                               max(len(tasks), 1) * max(budget["max_task_attempts"] - 1, 0))
        if failures > budget["max_failures"] or retries > retry_limit:
            enqueue_transition(base, pilot, project, goal_id, "active", "budget-exhausted",
                               "failure-budget", version)
            return

        # A dead process is first made stale by a dedicated CAS action. It is never relaunched
        # from the same observation that discovered the crash.
        for _, task in tasks:
            if task.get("status") in {"running", "leased"} and task.get("id") in recovery["dead_process_tasks"]:
                enqueue_decision(base, str(pilot["id"]), "task-transition",
                                 [project, goal_id, str(task["id"]), str(task["status"]), "stale", "recovery-crash"],
                                 goal_id, "reconcile dead worker lease", [task["id"], task["status"], "stale", task.get("version", "1")])
                return

        for _, task in tasks:
            task_status = task.get("status")
            attempts = safe_int(task.get("attempts"))
            if task_status in {"failed", "stale"}:
                if attempts >= budget["max_task_attempts"] or retries >= retry_limit:
                    enqueue_transition(base, pilot, project, goal_id, "active", "budget-exhausted",
                                       "retry-budget", version)
                else:
                    enqueue_decision(base, str(pilot["id"]), "task-transition",
                                     [project, goal_id, str(task["id"]), str(task_status), "ready", "bounded-retry"],
                                     goal_id, "bounded task retry", [task["id"], task_status, "ready", attempts])
                return
            if task_status in {"blocked", "escalated", "cancelled"}:
                enqueue_transition(base, pilot, project, goal_id, "active", "blocked",
                                   "task-blocked", version)
                return

        ready_or_proposed = [task for _, task in tasks if task.get("status") in {"proposed", "ready", "queued"}]
        review_backlog = [task for _, task in tasks if task.get("status") == "passed"
                          and task.get("review_status") != "accepted"]
        if ready_or_proposed and len(review_backlog) >= budget["max_review_queue"]:
            append_event(base, "review-backpressure", project, goal_id,
                         detail={"backlog": len(review_backlog), "limit": budget["max_review_queue"]})
            return

        fresh, base_commit, freshness = fresh_base(config)
        if ready_or_proposed and not fresh:
            enqueue_transition(base, pilot, project, goal_id, "active", "blocked", freshness, version)
            return

        for _, task in tasks:
            if task.get("status") != "proposed":
                continue
            deps = dependencies(task)
            if all(task_by_id.get(dep, {}).get("status") == "passed" for dep in deps):
                enqueue_decision(base, str(pilot["id"]), "task-transition",
                                 [project, goal_id, str(task["id"]), "proposed", "ready", "dependencies-passed"],
                                 goal_id, "unlock dependency-ready task",
                                 [task["id"], "proposed", "ready", task.get("version", "1")])
                return

        running_ids = {task.get("id") for _, task in tasks if task.get("status") in {"leased", "running"}}
        running_ids.update(str(row.get("task_id")) for row in runs
                           if row.get("status") == "running" and process_alive(row.get("pid")))
        pilot_limit = safe_int(pilot.get("concurrency_limit"))
        pilot_budget = pilot.get("budget") if isinstance(pilot.get("budget"), dict) else {}
        pilot_inflight = safe_int(pilot_budget.get("max_inflight_workers"), pilot_limit)
        limit = min(pilot_limit, pilot_inflight, budget["max_concurrency"])
        if len(running_ids) < limit:
            for _, task in tasks:
                if task.get("status") not in {"ready", "queued"}:
                    continue
                deps = dependencies(task)
                if not all(task_by_id.get(dep, {}).get("status") == "passed" for dep in deps):
                    continue
                capacity = subprocess.run(["bash", str(base / "scripts/capacity.sh"), "check", "arm"],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                          env={**os.environ, "RECURSION_ROOT": str(base)}, check=False)
                if capacity.returncode:
                    append_event(base, "capacity-deferred", project, goal_id, str(task.get("id")),
                                 {"exit_code": capacity.returncode})
                    return
                attempt = safe_int(task.get("attempts")) + 1
                enqueue_decision(base, str(pilot["id"]), "work", [str(task["id"])], goal_id,
                                 "capacity-admitted Phase 5 worker dispatch",
                                 [project, goal_id, task["id"], attempt, base_commit])
                return

        if not tasks:
            enqueue_transition(base, pilot, project, goal_id, "active", "blocked", "no-goal-tasks", version)
            return
        if not all(task.get("status") == "passed" for _, task in tasks):
            return

        repo = Path(str(config["repo"]))
        for _, task in tasks:
            valid, reason, exact = task_evidence(base, repo, task, runs)
            if not valid:
                enqueue_transition(base, pilot, project, goal_id, "active", "blocked",
                                   "verifier-disagreement", version)
                return
            if budget["publication_required"]:
                remote_commit = remote_review_commit(config, str(task["id"]))
                if remote_commit != exact["commit_oid"]:
                    publish_actions = [row for row in actions if row.get("verb") == "publish-task"
                                       and task.get("id") in (row.get("arguments") or [])]
                    failed = sum(row.get("status") == "failed" for row in publish_actions)
                    if failed >= budget["max_publish_attempts"]:
                        enqueue_transition(base, pilot, project, goal_id, "active", "blocked",
                                           "publisher-failure", version)
                    else:
                        enqueue_decision(base, str(pilot["id"]), "publish-task",
                                         [project, goal_id, str(task["id"])], goal_id,
                                         "publish exact verified review ref",
                                         [project, goal_id, task["id"], failed + 1, exact["commit_oid"]])
                    return

        enqueue_transition(base, pilot, project, goal_id, "active", "verifying",
                           "all-tasks-exactly-verified", version)


def schedule(base: Path, project: str | None, goal_id: str | None) -> int:
    if (base / "state/PAUSE").exists():
        return 0
    scheduled = 0
    paths = [goal_path(base, goal_id)] if goal_id else sorted((base / "state/goals").glob("*.md"))
    for path in paths:
        goal = read_fields(path)
        gid = goal.get("id", "")
        pid = goal.get("project_id", "")
        if not IDENT.fullmatch(gid) or not IDENT.fullmatch(pid):
            continue
        if project and pid != project:
            continue
        if goal.get("status") not in ACTIVE_GOALS:
            continue
        try:
            config, pilot = project_records(base, pid)
            parse_budget(goal)
        except ReconcileError:
            continue
        if safe_int(pilot.get("concurrency_limit")) <= 0:
            continue
        fingerprint = snapshot_digest(base, config, gid)
        enqueue_decision(base, str(pilot["id"]), "reconcile-goal", [pid, gid], gid,
                         "event-driven canonical truth reconciliation", [pid, gid, fingerprint])
        scheduled += 1
    print(scheduled)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    schedule_cmd = sub.add_parser("schedule")
    schedule_cmd.add_argument("--project")
    schedule_cmd.add_argument("--goal")
    for name in ("reconcile", "verify-goal"):
        cmd = sub.add_parser(name)
        cmd.add_argument("project")
        cmd.add_argument("goal")
    task_cmd = sub.add_parser("transition-task")
    for name in ("project", "goal", "task", "expected", "target", "reason"):
        task_cmd.add_argument(name)
    goal_cmd = sub.add_parser("transition-goal")
    for name in ("project", "goal", "expected", "target", "reason"):
        goal_cmd.add_argument(name)
    publish_cmd = sub.add_parser("publish-task")
    publish_cmd.add_argument("project")
    publish_cmd.add_argument("goal")
    publish_cmd.add_argument("task")
    args = parser.parse_args()
    base = root()
    try:
        if args.command == "schedule":
            return schedule(base, args.project, args.goal)
        if (base / "state/PAUSE").exists():
            raise ReconcileError("PAUSE blocks Phase 6 actuation")
        if args.command == "reconcile":
            reconcile(base, args.project, args.goal)
        elif args.command == "transition-task":
            transition_task(base, args.project, args.goal, args.task, args.expected, args.target, args.reason)
        elif args.command == "transition-goal":
            transition_goal(base, args.project, args.goal, args.expected, args.target, args.reason)
        elif args.command == "verify-goal":
            verify_goal(base, args.project, args.goal)
        else:
            publish_task(base, args.project, args.goal, args.task)
    except (OSError, ReconcileError, subprocess.TimeoutExpired) as exc:
        print(f"project-reconcile: {exc}", file=sys.stderr)
        return 75 if "PAUSE" in str(exc) else 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

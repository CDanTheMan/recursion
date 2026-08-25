#!/usr/bin/env python3
"""Deterministic Phase 6 measurable-goal reconciliation.

This module never launches a worker or publishes a ref from its scheduler/reconcile paths.
It observes canonical files plus process/git evidence and emits idempotent decisions into the
existing Phase 3 queue.  The existing sole actuator later executes those decisions as durable
actions.  Mutating subcommands are therefore actuator verbs, not alternate control paths.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import fcntl
import hashlib
import json
import math
import os
import re
import signal
import stat
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from transition_receipt import (
    TransitionReceiptError, authenticated_transition, commit_event, commit_transition,
    fields_mutation, json_mutation, resume_transition,
)
from seed_contract import SeedContractError, copy_seed_paths, validate_contract


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
    def __init__(self, message: str, code: int = 4) -> None:
        super().__init__(message)
        self.code = code


class ReconcileDeferral(TransitionReceiptError):
    """A precondition race that revoked authority without proving invalid state."""


def root() -> Path:
    return Path(os.environ.get("RECURSION_ROOT") or Path(__file__).resolve().parent.parent)


def fail(message: str, code: int = 4) -> None:
    print(f"project-reconcile: {message}", file=sys.stderr)
    raise SystemExit(code)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def canonical_sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def fsync_dir(path: Path) -> None:
    if os.name == "nt":
        return
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


def read_json(path: Path, *, unavailable_code: int | None = None) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ReconcileError(
            f"cannot read {path}: {exc}", unavailable_code if unavailable_code is not None else 4,
        ) from exc
    except OSError as exc:
        raise ReconcileError(f"cannot read {path}: {exc}", 74) from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReconcileError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReconcileError(f"state record is not an object: {path}")
    return value


def state_files(directory: Path, suffix: str) -> list[Path]:
    """Enumerate one lazy runtime directory without translating I/O failure into emptiness."""
    try:
        mode = os.lstat(directory).st_mode
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise ReconcileError(f"cannot inspect state directory {directory}: {exc}", 74) from exc
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise ReconcileError(f"state path is not a real directory: {directory}", 74)
    try:
        with os.scandir(directory) as entries:
            paths: list[Path] = []
            for entry in entries:
                if not entry.name.endswith(suffix):
                    continue
                path = directory / entry.name
                if entry.is_symlink():
                    raise ReconcileError(f"state record is a symlink: {path}", 74)
                if entry.is_file(follow_symlinks=False):
                    paths.append(path)
                elif not entry.is_dir(follow_symlinks=False):
                    raise ReconcileError(f"state record has an unsupported type: {path}", 74)
    except FileNotFoundError:
        return []
    except ReconcileError:
        raise
    except OSError as exc:
        raise ReconcileError(f"cannot enumerate state directory {directory}: {exc}", 74) from exc
    return sorted(paths)


def read_fields(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    except FileNotFoundError as exc:
        raise ReconcileError(f"cannot read {path}: {exc}") from exc
    except OSError as exc:
        raise ReconcileError(f"cannot read {path}: {exc}", 74) from exc
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


def append_event(base: Path, event: str, project: str, goal: str, task: str = "", detail: object = "",
                 event_id: str = "") -> None:
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
    if event_id:
        value["id"] = event_id
    try:
        commit_event(base, value)
    except OSError as exc:
        raise ReconcileError(f"event journal append unavailable: {exc}", 74) from exc
    except TransitionReceiptError as exc:
        raise ReconcileError(f"event journal append failed: {exc}") from exc


def transition_event(event: str, project: str, goal: str, task: str = "", detail: object = "",
                     event_id: str = "") -> dict:
    value = {"schema_version": 1, "ts": now_iso(), "event": event, "project": project,
             "goal": goal, "task": task, "pid": os.getpid(), "detail": detail}
    if event_id:
        value["id"] = event_id
    return value


def commit_reconcile_transition(base: Path, mutations: list, event: dict,
                                authoritative_index: int = -1,
                                precondition=None) -> None:
    try:
        commit_transition(base, mutations, event, authoritative_index=authoritative_index,
                          precondition=precondition)
    except ReconcileDeferral as exc:
        raise ReconcileError(f"crash-consistent transition deferred: {exc}", 75) from exc
    except OSError as exc:
        raise ReconcileError(f"crash-consistent transition unavailable: {exc}", 74) from exc
    except TransitionReceiptError as exc:
        raise ReconcileError(f"crash-consistent transition failed: {exc}") from exc


@contextmanager
def event_serialization_lock(base: Path):
    """Share taskctl's mkdir mutex and never append through runtime-state rotation."""
    lock_dir = base / "state/.locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    runtime_lock = lock_dir / "runtime-state.lock"
    path = lock_dir / "taskctl.lock"
    attempts = max(1, safe_int(os.environ.get("RECURSION_LOCK_ATTEMPTS"), 100))
    try:
        delay = max(0.0, float(os.environ.get("RECURSION_LOCK_DELAY_S", "0.1")))
    except ValueError:
        delay = 0.1
    held = False
    try:
        for _ in range(attempts):
            if not runtime_lock.is_dir():
                try:
                    path.mkdir()
                    held = True
                    (path / "pid").write_text(f"{os.getpid()}\n", encoding="ascii")
                    # Close the check/mkdir race: runtime-state must either pre-exist here or
                    # observe taskctl.lock and fail its own compatibility lock.
                    if runtime_lock.is_dir():
                        raise ReconcileError("runtime-state rotation acquired during event lock")
                    break
                except FileExistsError:
                    pass
            time.sleep(delay)
        if not held:
            raise ReconcileError("event journal lock is contended; refusing an unlocked append")
        yield
    finally:
        if held:
            (path / "start").unlink(missing_ok=True)
            (path / "pid").unlink(missing_ok=True)
            try:
                path.rmdir()
            except OSError:
                pass


@contextmanager
def goal_lock(base: Path, goal_id: str):
    lock_dir = base / "state/.locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    path = lock_dir / f"reconcile-{goal_id}.lock"
    with path.open("a+", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ReconcileError(f"goal lock contended: {goal_id}", 75) from exc
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


def close_paused_windows(base: Path) -> int:
    """PAUSE revokes every open window; a later resume needs fresh Lucas authority."""
    if not (base / "state/PAUSE").is_file():
        return 0
    closed = 0
    for path in sorted((base / "state/pilot-windows").glob("*.json")):
        try:
            value = read_json(path)
        except ReconcileError:
            continue
        if value.get("status") != "open":
            continue
        event_id = "source-window-pause-" + hashlib.sha256(str(value.get("id") or path.name).encode()).hexdigest()[:24]
        value.update({"status": "closed", "closed_at": now_iso(), "close_reason": "pause-observed"})
        event = transition_event("pilot-window-closed", str(value.get("project_id") or ""),
                                 str(value.get("goal_id") or ""),
                                 detail={"window_id": value.get("id"), "reason": "pause-observed"},
                                 event_id=event_id)
        commit_reconcile_transition(base, [json_mutation(path, value)], event); closed += 1
    return closed


def verify_phase8_goal_contract(base: Path, project: str, goal_id: str, *,
                                 terminal: bool = False, check_remote: bool = False) -> dict:
    helper = base / "scripts/project-pilot.py"
    if not helper.is_file():
        raise ReconcileError("Phase 8 contract verifier is absent", 74)
    argv = [sys.executable, str(helper), "verify-approved-goal", project, goal_id]
    if terminal:
        argv.append("--terminal")
    if check_remote:
        argv.append("--check-remote")
    try:
        proc = subprocess.run(
            argv,
            env={**os.environ, "RECURSION_ROOT": str(base)}, text=True,
            capture_output=True, timeout=300 if check_remote else 60, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReconcileError("Phase 8 contract verifier is unavailable", 74) from exc
    if proc.returncode:
        detail = (proc.stderr or proc.stdout or "contract verification failed").strip()[:500]
        raise ReconcileError(
            f"Phase 8 approved contract is invalid: {detail}",
            4 if proc.returncode == 4 else 74,
        )
    try:
        value = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ReconcileError("Phase 8 contract verifier returned malformed evidence", 74) from exc
    if not isinstance(value, dict):
        raise ReconcileError("Phase 8 contract verifier returned non-object evidence", 74)
    if value.get("project_id") != project or value.get("goal_id") != goal_id:
        raise ReconcileError("Phase 8 contract verifier returned mismatched authority", 74)
    return value


def require_provider_capability(base: Path, contract: dict) -> None:
    if contract.get("provider_only_required") is not True:
        return
    helper = base / "scripts/provider-network.sh"
    try:
        proc = subprocess.run(
            ["bash", str(helper), "check"],
            env={**os.environ, "RECURSION_ROOT": str(base)},
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=30, check=False,
        ) if helper.is_file() else None
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReconcileError("provider-only capability is unavailable", 74) from exc
    if proc is None or proc.returncode:
        raise ReconcileError("provider-only capability is absent or unhealthy", 74)


def record_authority_deferral(base: Path, project: str, goal_id: str, reason: str,
                              error: Exception | str | None = None) -> None:
    """Leave active authority untouched but make every unavailable proof operator-visible."""
    print(f"project-reconcile: deferred {project}/{goal_id}: {reason}", file=sys.stderr)
    event_recorded = False
    try:
        detail = {"reason": reason}
        if error is not None:
            print(
                "project-reconcile: deferral diagnostic "
                f"sha256={hashlib.sha256(str(error).encode()).hexdigest()}",
                file=sys.stderr,
            )
        append_event(
            base, "authority-proof-deferred", project, goal_id,
            detail=detail,
            event_id="source-authority-proof-deferred-" + hashlib.sha256(
                f"{project}:{goal_id}:{reason}".encode()
            ).hexdigest()[:24],
        )
        event_recorded = True
    except ReconcileError as exc:
        print(f"project-reconcile: deferral audit event unavailable: {exc}", file=sys.stderr)
    helper = base / "scripts/taskctl.sh"
    if not helper.is_file():
        print("project-reconcile: deferral escalation controller is absent", file=sys.stderr)
        if not event_recorded:
            raise ReconcileError("authority deferral has no durable audit channel", 74)
        return
    escalation_recorded = False
    key = f"phase8-authority-proof:{project}:{goal_id}"
    title = "Phase 8 remote authority proof is unavailable"
    pointer = f"state/goals/{goal_id}.md"
    try:
        proc = subprocess.run(
            ["bash", str(helper), "esc-record", key, title, project, pointer],
            env={**os.environ, "RECURSION_ROOT": str(base)},
            stdin=subprocess.DEVNULL, text=True, capture_output=True,
            timeout=30, check=False,
        )
        escalation_recorded = proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"project-reconcile: deferral escalation unavailable: {exc}", file=sys.stderr)
    else:
        if proc.returncode:
            detail = (proc.stderr or proc.stdout or "escalation failed").strip()[:300]
            print(f"project-reconcile: deferral escalation unavailable: {detail}", file=sys.stderr)
    if not event_recorded and not escalation_recorded:
        raise ReconcileError("authority deferral has no durable audit channel", 74)


def open_window(base: Path, project: str, goal_id: str, pilot: dict | None = None) -> dict | None:
    if pilot is None:
        _, pilot = project_records(base, project)
    if not pilot.get("window_required"):
        return {"id": "legacy-unwindowed", "project_id": project, "goal_id": goal_id,
                "status": "open", "max_inflight_workers": int(pilot.get("concurrency_limit") or 0)}
    now = int(time.time()); matches: list[tuple[Path, dict]] = []
    verified = False
    proved_contract_sha: str | None = None
    for path in state_files(base / "state/pilot-windows", ".json"):
        value = read_json(path, unavailable_code=74)
        if value.get("project_id") != project or value.get("goal_id") != goal_id \
                or value.get("status") not in {"armed", "open"}:
            continue
        if safe_int(value.get("expires_at_epoch")) <= now:
            event_id = "source-window-expired-" + hashlib.sha256(str(value.get("id") or path.name).encode()).hexdigest()[:24]
            value.update({"status": "closed", "closed_at": now_iso(), "close_reason": "expired"})
            event = transition_event("pilot-window-closed", project, goal_id,
                                     detail={"window_id": value.get("id"), "reason": "expired"},
                                     event_id=event_id)
            commit_reconcile_transition(base, [json_mutation(path, value)], event)
            continue
        if value.get("status") == "armed":
            if (base / "state/PAUSE").is_file():
                continue
            if proved_contract_sha is None:
                try:
                    contract = verify_phase8_goal_contract(
                        base, project, goal_id, check_remote=False,
                    )
                except ReconcileError as exc:
                    if exc.code != 4:
                        raise
                    event_id = "source-window-contract-refused-" + hashlib.sha256(
                        f"{value.get('id')}:{value.get('plan_digest')}".encode()).hexdigest()[:24]
                    append_event(base, "pilot-window-refused", project, goal_id,
                                 detail={"window_id": value.get("id"),
                                         "reason": "approved-contract-invalid",
                                         "error_sha256": hashlib.sha256(str(exc).encode()).hexdigest()},
                                 event_id=event_id)
                    raise
                verified = True
                proved_contract_sha = canonical_sha(contract)
            # An authenticated close (or a newly observed PAUSE) may commit between the read
            # above and this open commit. Re-prove the exact local contract, armed bytes,
            # expiry, singleton authority, and PAUSE immediately before committing, under the
            # same taskctl lock the close transition takes. Remote and provider I/O belongs at
            # worker admission, never inside this global transition lock or its heartbeat path.
            armed = dict(value)

            def open_precondition() -> None:
                race = os.environ.get("RECURSION_TEST_WINDOW_OPEN_RACE", "")
                if race == "pause":
                    (base / "state/PAUSE").write_text("race pause\n", encoding="utf-8")
                elif race == "close":
                    closed = dict(armed)
                    closed.update({"status": "closed", "closed_at": now_iso(),
                                   "close_reason": "race-close"})
                    atomic_json(path, closed)
                if (base / "state/PAUSE").exists():
                    raise ReconcileDeferral("PAUSE revokes an armed window before it opens")
                try:
                    current_contract = verify_phase8_goal_contract(
                        base, project, goal_id, check_remote=False,
                    )
                except ReconcileError as exc:
                    raise ReconcileDeferral(
                        f"pilot contract changed before its open commit: {exc}"
                    ) from exc
                if canonical_sha(current_contract) != proved_contract_sha:
                    raise ReconcileDeferral(
                        "pilot contract bytes changed during local open admission"
                    )
                current = read_json(path, unavailable_code=74)
                if current.get("status") != "armed" or canonical_sha(current) != canonical_sha(armed):
                    raise ReconcileDeferral("armed window changed before it opened")
                if safe_int(current.get("expires_at_epoch")) <= int(time.time()):
                    raise ReconcileDeferral("armed window expired before it opened")
                armed_or_open = 0
                for other in state_files(base / "state/pilot-windows", ".json"):
                    other_value = read_json(other, unavailable_code=74)
                    if other_value.get("project_id") == project \
                            and other_value.get("status") in {"armed", "open"}:
                        armed_or_open += 1
                if armed_or_open != 1:
                    raise ReconcileDeferral("pilot window singleton authority changed before it opened")

            event_id = "source-window-open-" + hashlib.sha256(
                f"{value.get('id')}:{value.get('instruction_id')}".encode()).hexdigest()[:24]
            activation_epoch = int(time.time())
            value.update({
                "status": "open",
                "opened_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(activation_epoch)),
                "activated_at_epoch": activation_epoch,
            })
            event = transition_event("pilot-window-opened", project, goal_id,
                                     detail={"window_id": value.get("id"),
                                             "instruction_id": value.get("instruction_id"),
                                             "activated_at_epoch": activation_epoch},
                                     event_id=event_id)
            commit_reconcile_transition(base, [json_mutation(path, value)], event,
                                        precondition=open_precondition)
            value = read_json(path, unavailable_code=74)
        elif not verified:
            verify_phase8_goal_contract(
                base, project, goal_id, check_remote=False,
            )
            verified = True
        matches.append((path, value))
    if len(matches) > 1:
        raise ReconcileError("multiple open pilot windows target one goal")
    return matches[0][1] if matches else None


def require_window(base: Path, project: str, goal_id: str, *, absent_code: int = 4) -> dict:
    _, pilot = project_records(base, project)
    window = open_window(base, project, goal_id, pilot)
    if not window:
        raise ReconcileError("exact open pilot window authority is absent", absent_code)
    return window


def authenticated_open_window(base: Path, window: dict, project: str,
                              goal_id: str) -> dict:
    """Rebind a caller snapshot to the exact current pilot-window-opened receipt."""
    window_id = str(window.get("id") or "")
    if not IDENT.fullmatch(window_id):
        raise ReconcileError("wall-clock budget window identity is invalid")
    path = base / "state/pilot-windows" / f"{window_id}.json"
    current = read_json(path)
    if canonical_sha(current) != canonical_sha(window):
        raise ReconcileError("wall-clock budget window changed after authority admission")
    event_id = "source-window-open-" + hashlib.sha256(
        f"{window_id}:{current.get('instruction_id')}".encode()
    ).hexdigest()[:24]
    try:
        prepared = authenticated_transition(base, event_id, journal="state/events.jsonl")
    except TransitionReceiptError as exc:
        raise ReconcileError("wall-clock budget window receipt is invalid") from exc
    event = prepared.get("event") if isinstance(prepared.get("event"), dict) else {}
    detail = event.get("detail") if isinstance(event.get("detail"), dict) else {}
    relative = path.relative_to(base).as_posix()
    matching = [
        mutation for mutation in prepared.get("mutations", [])
        if mutation.get("kind") == "json" and mutation.get("path") == relative
    ]
    if prepared.get("authoritative_path") != relative or len(matching) != 1 \
            or event.get("event") != "pilot-window-opened" \
            or event.get("project") != project or event.get("goal") != goal_id \
            or detail.get("window_id") != window_id \
            or str(detail.get("instruction_id") or "") != str(current.get("instruction_id") or ""):
        raise ReconcileError("wall-clock budget window receipt has mismatched authority")
    activation = current.get("activated_at_epoch")
    if activation is not None and detail.get("activated_at_epoch") != activation:
        raise ReconcileError("wall-clock budget activation differs from its receipt")
    return current


def window_activation_epoch(base: Path, window: dict, project: str, goal_id: str,
                            goal: dict[str, str], observed_epoch: int | None = None) -> int:
    """Return the authenticated execution start, never the earlier arm/materialization time."""
    observed = int(time.time()) if observed_epoch is None else observed_epoch
    window = authenticated_open_window(base, window, project, goal_id)
    if window.get("status") != "open" or window.get("project_id") != project \
            or window.get("goal_id") != goal_id:
        raise ReconcileError("wall-clock budget lacks exact open window authority")
    for key in ("plan_id", "plan_digest"):
        if goal.get(key) and window.get(key) != goal.get(key):
            raise ReconcileError("wall-clock budget window disagrees with approved goal authority")

    opened_at = str(window.get("opened_at") or "")
    try:
        opened_epoch = int(datetime.datetime.strptime(
            opened_at, "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=datetime.timezone.utc).timestamp())
    except (ValueError, OverflowError) as exc:
        raise ReconcileError("open window lacks a valid activation timestamp") from exc

    raw_activation = window.get("activated_at_epoch")
    if raw_activation is None:
        # Compatibility for windows opened before activation epochs were persisted. Their
        # opened_at string was written only by the armed->open transition and is receipt-bound.
        activation = opened_epoch
    elif isinstance(raw_activation, bool) or not isinstance(raw_activation, int):
        raise ReconcileError("open window activation epoch is invalid")
    else:
        activation = raw_activation
        if activation != opened_epoch:
            raise ReconcileError("open window activation timestamps disagree")

    armed_epoch = safe_int(window.get("opened_at_epoch"))
    expires_epoch = safe_int(window.get("expires_at_epoch"))
    if activation < 1 or (armed_epoch > 0 and activation < armed_epoch) \
            or expires_epoch <= activation or activation > observed:
        raise ReconcileError("open window activation lies outside its authenticated bounds")
    return activation


def goal_wall_clock_anchor(base: Path, project: str, goal_id: str,
                           goal: dict[str, str], pilot: dict,
                           window: dict | None = None,
                           observed_epoch: int | None = None) -> int:
    """Anchor windowed goal time to activation; retain legacy goal-start semantics otherwise."""
    observed = int(time.time()) if observed_epoch is None else observed_epoch
    if not pilot.get("window_required"):
        return safe_int(goal.get("started_at_epoch"), observed)
    raw_materialized = goal.get("started_at_epoch")
    if not str(raw_materialized or "").isdigit() or safe_int(raw_materialized) < 1:
        raise ReconcileError("windowed goal materialization timestamp is invalid")
    materialized = safe_int(raw_materialized)
    authority = window if window is not None else require_window(base, project, goal_id)
    activated = window_activation_epoch(base, authority, project, goal_id, goal, observed)
    if materialized > activated:
        raise ReconcileError("goal materialization timestamp follows window activation")
    return activated


def goal_wall_clock_deadline(base: Path, project: str, goal_id: str,
                             goal: dict[str, str], pilot: dict, budget: dict,
                             window: dict | None = None,
                             observed_epoch: int | None = None) -> int:
    return goal_wall_clock_anchor(
        base, project, goal_id, goal, pilot, window, observed_epoch,
    ) + int(budget["max_wall_clock_seconds"])


def window_authority_current(base: Path, window: dict | None,
                             observed_epoch: int | None = None) -> bool:
    if window is None:
        return True
    try:
        path = base / "state/pilot-windows" / f"{window['id']}.json"
        current = read_json(path)
    except (KeyError, OSError, ReconcileError):
        return False
    observed = int(time.time()) if observed_epoch is None else observed_epoch
    return bool(
        not (base / "state/PAUSE").exists()
        and canonical_sha(current) == canonical_sha(window)
        and current.get("status") == "open"
        and safe_int(current.get("expires_at_epoch")) > observed
    )


def terminal_window_authority(pilot: dict, window: dict | None) -> dict | None:
    """Only explicitly windowed pilots carry revocable window authority into terminal gates."""
    return window if pilot.get("window_required") else None


def admit_work(base: Path, task_id: str) -> dict:
    if not IDENT.fullmatch(task_id):
        raise ReconcileError("work task identity is invalid")
    path = base / "state/tasks" / f"{task_id}.md"
    task = read_fields(path)
    project, goal_id = task.get("project_id", ""), task.get("goal_id", "")
    if not IDENT.fullmatch(project) or not IDENT.fullmatch(goal_id):
        raise ReconcileError("work task lacks canonical project/goal identity")
    if (base / "state/PAUSE").exists():
        raise ReconcileError("PAUSE blocks Phase 8 worker admission", 75)
    try:
        contract = verify_phase8_goal_contract(base, project, goal_id, check_remote=True)
        require_provider_capability(base, contract)
    except ReconcileError as exc:
        if exc.code != 4:
            try:
                record_authority_deferral(
                    base, project, goal_id, "worker-admission-unavailable", exc,
                )
            except ReconcileError as audit_exc:
                print(
                    f"project-reconcile: worker-admission deferral audit unavailable: {audit_exc}",
                    file=sys.stderr,
                )
        else:
            try:
                append_event(
                    base, "pilot-window-refused", project, goal_id,
                    detail={"reason": "worker-admission-invalid",
                            "error_sha256": hashlib.sha256(str(exc).encode()).hexdigest()},
                    event_id="source-authority-proof-refused-" + hashlib.sha256(
                        f"{project}:{goal_id}:{exc}".encode()
                    ).hexdigest()[:24],
                )
            except ReconcileError as audit_exc:
                print(
                    f"project-reconcile: authority-refusal audit event unavailable: {audit_exc}",
                    file=sys.stderr,
                )
        raise
    if (base / "state/PAUSE").exists():
        raise ReconcileError("PAUSE blocks Phase 8 worker admission", 75)
    window = require_window(base, project, goal_id, absent_code=75)
    return {"project_id": project, "goal_id": goal_id, "window_id": window.get("id")}


def check_work_authority(base: Path, task_id: str) -> dict:
    """Recheck local revocation state on a previously admitted worker heartbeat."""
    if not IDENT.fullmatch(task_id):
        raise ReconcileError("work task identity is invalid")
    path = base / "state/tasks" / f"{task_id}.md"
    task = read_fields(path)
    project, goal_id = task.get("project_id", ""), task.get("goal_id", "")
    if not IDENT.fullmatch(project) or not IDENT.fullmatch(goal_id):
        raise ReconcileError("work task lacks canonical project/goal identity")
    if (base / "state/PAUSE").exists():
        raise ReconcileError("PAUSE blocks Phase 8 worker authority", 75)
    window = require_window(base, project, goal_id, absent_code=75)
    return {"project_id": project, "goal_id": goal_id, "window_id": window.get("id")}


CONTRACT_REJECTION_CATEGORIES = {
    "acceptance-missing", "acceptance-invalid", "deadline-invalid", "network-policy-invalid",
    "verification-policy-invalid", "worker-engine-invalid", "model-alias-invalid",
    "verifier-model-alias-invalid", "model-separation-invalid", "contract-projection-invalid",
    "gate-contract-drift", "source-head-drift", "seed-contract-invalid",
}


def task_contract_event_id(project: str, goal_id: str, task_id: str,
                           category: str, contract_digest: str) -> str:
    identity = f"{project}\0{goal_id}\0{task_id}\0{category}\0{contract_digest}\0pre-worker-contract-v2".encode()
    return "source-task-contract-invalid-" + hashlib.sha256(identity).hexdigest()[:24]


def task_contract_event(project: str, goal_id: str, task_id: str,
                        category: str, contract_digest: str) -> dict:
    return transition_event(
        "task-contract-invalid", project, goal_id, task_id,
        {
            "reason": "task-contract-invalid",
            "category": category,
            "contract_digest": contract_digest,
            "stage": "controller-pre-worker",
            "attempts": 0,
        },
        task_contract_event_id(project, goal_id, task_id, category, contract_digest),
    )


def reject_task_contract(base: Path, task_id: str, category: str, contract_digest: str) -> dict:
    """Atomically stop a pilot task and its goal before a worker can be leased.

    Gate validation runs inside work.sh after dispatch authority has been admitted but before
    taskctl increments attempts.  A controller rejection at that seam is terminal evidence,
    not a worker escalation: task and goal therefore share one mutation-backed receipt.  The
    stable source event also lets an exact retry finish a partial multi-file transition.
    """
    task_path = base / "state/tasks" / f"{task_id}.md"
    task = read_fields(task_path)
    project, goal_id = task.get("project_id", ""), task.get("goal_id", "")
    if not IDENT.fullmatch(task_id) or not IDENT.fullmatch(project) or not IDENT.fullmatch(goal_id):
        raise ReconcileError("contract rejection lacks canonical task/project/goal identity")
    if not task.get("pilot_id"):
        raise ReconcileError("contract rejection is reserved for project-pilot work")
    if category not in CONTRACT_REJECTION_CATEGORIES:
        raise ReconcileError("contract rejection category is not controller-defined")
    if re.fullmatch(r"[0-9a-f]{64}", contract_digest) is None:
        raise ReconcileError("contract rejection digest is invalid")
    event = task_contract_event(project, goal_id, task_id, category, contract_digest)
    goal_file = goal_path(base, goal_id)
    with goal_lock(base, goal_id):
        try:
            resumed = resume_transition(base, event)
        except (OSError, TransitionReceiptError) as exc:
            raise ReconcileError(f"task-contract rejection recovery failed: {exc}") from exc
        if resumed:
            ensure_terminal_events(base, project, goal_id, read_fields(goal_file))
            return {
                "project_id": project, "goal_id": goal_id, "task_id": task_id,
                "event_id": event["id"], "status": "blocked", "replayed": True,
            }

        task = read_fields(task_path)
        goal = read_fields(goal_file)
        if task.get("project_id") != project or task.get("goal_id") != goal_id \
                or goal.get("project_id") != project:
            raise ReconcileError("contract rejection crossed project or goal scope")
        if task.get("status") not in {"ready", "queued"} or goal.get("status") != "active":
            raise ReconcileError("contract rejection compare-and-swap found unrelated task or goal state")
        if safe_int(task.get("attempts")) != 0 or task.get("candidate_commit") \
                or run_records(base, {task_id}):
            raise ReconcileError("contract rejection is not pre-worker: execution evidence exists")

        timestamp = now_iso()
        task_version = safe_int(task.get("version"), 1) + 1
        goal_version = safe_int(goal.get("version"), 1) + 1
        task_changes = {
            "status": "blocked", "version": str(task_version), "lease_expires": "0",
            "transition_reason": "task-contract-invalid", "transition_at": timestamp,
            "blocker_actor": "controller", "blocked_on": category,
            "contract_rejection_category": category,
            "contract_digest": contract_digest,
            "contract_rejection_event_id": str(event["id"]),
        }
        goal_changes = {
            "status": "blocked", "version": str(goal_version),
            "last_transition_at": timestamp, "last_transition_reason": "task-contract-invalid",
            "last_transition_from": "active", "last_transition_task": task_id,
            "last_transition_category": category, "contract_digest": contract_digest,
            "terminal_reported": "1", "finished_at": timestamp,
        }

        def authority_precondition() -> None:
            if os.environ.get("RECURSION_TEST_PAUSE_BEFORE_CONTRACT_COMMIT") == "1":
                (base / "state/PAUSE").write_text("test pause before contract commit\n", encoding="utf-8")
            if (base / "state/PAUSE").exists():
                raise ReconcileDeferral("PAUSE blocks a new task-contract rejection")
            _, pilot = project_records(base, project)
            if not pilot.get("window_required"):
                return
            matches = []
            for window_path in sorted((base / "state/pilot-windows").glob("*.json")):
                window = read_json(window_path)
                if window.get("project_id") == project and window.get("goal_id") == goal_id \
                        and window.get("status") == "open" \
                        and safe_int(window.get("expires_at_epoch")) > int(time.time()):
                    matches.append(window)
            if len(matches) != 1:
                raise ReconcileDeferral("exact open pilot-window authority changed before commit")
        commit_reconcile_transition(
            base,
            [fields_mutation(task_path, task_changes), fields_mutation(goal_file, goal_changes)],
            event, authoritative_index=1, precondition=authority_precondition,
        )
        ensure_terminal_events(base, project, goal_id, read_fields(goal_file))
    return {
        "project_id": project, "goal_id": goal_id, "task_id": task_id,
        "event_id": event["id"], "status": "blocked", "replayed": False,
    }


def resume_assist(base: Path, task_id: str, instruction_id: str) -> dict:
    task_path = base / "state/tasks" / f"{task_id}.md"
    assist_path = base / "state/assists" / f"{task_id}.md"
    task = read_fields(task_path); assist = read_fields(assist_path)
    project, goal_id = task.get("project_id", ""), task.get("goal_id", "")
    if not IDENT.fullmatch(task_id) or not IDENT.fullmatch(project) or not IDENT.fullmatch(goal_id):
        raise ReconcileError("assist resume lacks canonical task/project/goal identity")
    def answer_is_durable(value: dict[str, str]) -> bool:
        document = assist_path.read_text(encoding="utf-8", errors="replace")
        answer = document.partition("## ANSWER")[2].strip()
        return (value.get("status") in {"open", "answered"}
                and bool(value.get("answered")) and bool(value.get("answered_by"))
                and bool(answer) and not answer.startswith("_(unanswered"))

    if assist.get("task") != task_id or not answer_is_durable(assist):
        raise ReconcileError("assist resume requires the same durably answered assist")
    goal_file = goal_path(base, goal_id)
    event_id = "source-assist-" + hashlib.sha256(f"{project}:{goal_id}:{task_id}:{instruction_id}".encode()).hexdigest()[:24]
    with goal_lock(base, goal_id):
        task = read_fields(task_path); goal = read_fields(goal_file); assist = read_fields(assist_path)
        if assist.get("task") != task_id or not answer_is_durable(assist):
            raise ReconcileError("assist answer changed before resume compare-and-swap")
        already = (task.get("status") == "queued" and goal.get("status") == "active"
                   and assist.get("resume_event_id") == event_id)
        event = transition_event(
            "assist-answer", project, goal_id, task_id,
            {"instruction_id": instruction_id, "answer_actor": assist.get("answered_by")}, event_id,
        )
        try:
            resumed = resume_transition(base, event)
        except (OSError, TransitionReceiptError) as exc:
            raise ReconcileError(f"assist resume recovery failed: {exc}") from exc
        if resumed:
            return {"project_id": project, "goal_id": goal_id, "task_id": task_id,
                    "event_id": event_id, "status": "resumed"}
        if already:
            return {"project_id": project, "goal_id": goal_id, "task_id": task_id,
                    "event_id": event_id, "status": "resumed"}
        if task.get("status") not in {"blocked", "queued"} or goal.get("status") not in {"blocked", "active"}:
            raise ReconcileError("assist resume compare-and-swap found unrelated task or goal state")
        task_changes = {"status": "queued", "blocked_on": "",
                        "assist_resume_instruction_id": instruction_id}
        goal_changes = {"status": "active", "transition_reason": "human-answer-received",
                        "transition_at": now_iso()}
        assist_changes = {"status": "answered", "resume_applied": "1",
                          "resume_event_id": event_id, "resume_instruction_id": instruction_id}
        commit_reconcile_transition(
            base,
            [fields_mutation(task_path, task_changes), fields_mutation(goal_file, goal_changes),
             fields_mutation(assist_path, assist_changes)],
            event, authoritative_index=2,
        )
    return {"project_id": project, "goal_id": goal_id, "task_id": task_id,
            "event_id": event_id, "status": "resumed"}


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
    if value["max_review_queue"] < 1:
        raise ReconcileError("invalid budget field: max_review_queue must be at least 1")
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
    if os.name == "nt":
        # Python's os.kill(pid, 0) is not a read-only existence probe on Windows:
        # it may call TerminateProcess for non-console targets.  Query the process
        # handle instead so reconciliation can never kill the worker it observes.
        process_query_limited_information = 0x1000
        still_active = 259
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.GetExitCodeProcess.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))
        kernel32.GetExitCodeProcess.restype = ctypes.c_int
        kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
        kernel32.CloseHandle.restype = ctypes.c_int
        handle = kernel32.OpenProcess(process_query_limited_information, 0, number)
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            return bool(kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))) \
                and exit_code.value == still_active
        finally:
            kernel32.CloseHandle(handle)
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
        cwd=str(repo), text=True, capture_output=True, check=False, timeout=20,
        env=git_environment(config),
    )
    words = proc.stdout.split()
    if proc.returncode or not words:
        return False, local, "remote-head-unprovable"
    remote_head = words[0]
    return local == remote_head, local, "fresh" if local == remote_head else "stale-base"


def phase8_fresh_base(base: Path, project: str, goal_id: str) \
        -> tuple[bool | None, str, str]:
    """Distinguish proof unavailability from a proved immutable-contract failure."""
    try:
        contract = verify_phase8_goal_contract(
            base, project, goal_id, check_remote=True,
        )
    except ReconcileError as exc:
        if exc.code == 4:
            return False, "", "authority-contract-stale"
        return None, "", "authority-proof-unavailable"
    source_head = str(contract.get("source_head") or "")
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", source_head):
        return None, "", "authority-proof-unavailable"
    return True, source_head, "fresh"


def task_evidence(base: Path, repo: Path, task: dict[str, str], runs: list[dict],
                  require_local_review_ref: bool = True) -> tuple[bool, str, dict]:
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
    expected_seed = task.get("seed_digest", "")
    if expected_seed:
        seed_rows = []
        for row in (implementer, verifier):
            evidence = row.get("seed_evidence") if isinstance(row.get("seed_evidence"), dict) else {}
            seed_rows.append(bool(
                evidence.get("content_sha256") == expected_seed
                and evidence.get("manifest_sha256") == task.get("seed_manifest_sha256")
                and evidence.get("verified_before") is True
                and evidence.get("verified_after") is True
            ))
        if not all(seed_rows):
            return False, "implementer/verifier seed evidence is absent or disagrees", {"commit_oid": commit}
    try:
        branch_commit = git_output(repo, "rev-parse", f"refs/heads/loop/work/{task_id}")
    except ReconcileError:
        branch_commit = ""
    if require_local_review_ref and not branch_commit:
        return False, "canonical local review ref is absent", {"commit_oid": commit}
    if branch_commit and branch_commit != commit:
        return False, "review ref does not resolve to the verified commit", {"commit_oid": commit}
    return True, "verified", {
        "commit_oid": commit,
        "implementer_run_id": implementer.get("id"),
        "verifier_run_id": verifier.get("id"),
        "machine_gate": gate,
        "independent_verifier": verification,
    }


def remote_review_commit(config: dict, task_id: str) -> str:
    repo = Path(str(config.get("repo") or ""))
    if not (repo / ".git").exists():
        return ""
    remote = str(config.get("remote") or "origin")
    proc = subprocess.run(
        ["git", "ls-remote", remote, f"refs/heads/loop/work/{task_id}"],
        cwd=str(repo), text=True, capture_output=True, check=False, timeout=20,
        env=git_environment(config),
    )
    return proc.stdout.split()[0] if proc.returncode == 0 and proc.stdout.split() else ""


def remote_default_ancestor_proof(config: dict, commit: str) -> dict:
    """Fetch and bind the advertised default head before proving commit ancestry."""
    repo = Path(str(config.get("repo") or ""))
    remote = str(config.get("remote") or "origin")
    branch = str(config.get("default_branch") or "")
    project = str(config.get("id") or "")
    if not (repo / ".git").exists() or not IDENT.fullmatch(branch) or not IDENT.fullmatch(project):
        raise ReconcileError("remote default-branch review proof has invalid identity")
    advertised = subprocess.run(
        ["git", "ls-remote", remote, f"refs/heads/{branch}"], text=True,
        cwd=str(repo), capture_output=True, check=False, timeout=20,
        env=git_environment(config),
    )
    rows = [line.split() for line in advertised.stdout.splitlines() if line.split()]
    if advertised.returncode or len(rows) != 1 or len(rows[0]) != 2 \
            or rows[0][1] != f"refs/heads/{branch}" \
            or not re.fullmatch(r"[0-9a-f]{40,64}", rows[0][0]):
        raise ReconcileError("remote default branch identity is unprovable")
    advertised_oid = rows[0][0]
    fetched_ref = f"refs/recursion/review-acceptance/{project}"
    fetched = subprocess.run(
        ["git", "-C", str(repo), "fetch", "--quiet", "--no-tags", "--force", remote,
         f"refs/heads/{branch}:{fetched_ref}"], text=True, capture_output=True,
        check=False, timeout=60, env=git_environment(config),
    )
    if fetched.returncode:
        raise ReconcileError((fetched.stderr or fetched.stdout or "remote default fetch failed").strip())
    fetched_oid = git_output(repo, "rev-parse", fetched_ref)
    if fetched_oid != advertised_oid:
        raise ReconcileError("fetched default branch disagrees with its advertised identity")
    ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, fetched_oid],
        text=True, capture_output=True, check=False,
    )
    if ancestor.returncode == 1:
        raise ReconcileError("verified commit is not an ancestor of the fetched remote default branch")
    if ancestor.returncode:
        raise ReconcileError((ancestor.stderr or ancestor.stdout or "remote ancestry proof failed").strip())
    return {"kind": "remote-default-ancestor", "branch": branch,
            "remote_sha256": hashlib.sha256(remote.encode()).hexdigest(),
            "remote_default_commit": fetched_oid}


def decision_key(*parts: object) -> str:
    raw = json.dumps(parts, sort_keys=True, separators=(",", ":")).encode()
    return "phase6:" + hashlib.sha256(raw).hexdigest()


def enqueue_decision(base: Path, actor: str, verb: str, args: list[str], goal_id: str,
                     reason: str, key_parts: list[object]) -> Path:
    project = args[0] if args else ""
    if verb == "work" and args:
        try:
            project = read_fields(base / "state/tasks" / f"{args[0]}.md").get("project_id", "")
        except ReconcileError:
            project = ""
    raw = {
        "actor": actor,
        "decision_source": "project-reconciler",
        "routed_decider": actor,
        "verb": verb,
        "args": args,
        "project": project,
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


def lease_state(value: object, observed_epoch: int) -> str | None:
    if value in (None, ""):
        return None
    raw = str(value)
    try:
        expires = int(raw)
    except ValueError:
        try:
            expires = int(datetime.datetime.strptime(
                raw, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=datetime.timezone.utc).timestamp())
        except ValueError:
            return "invalid:" + raw
    return "expired" if expires <= observed_epoch else "active"


def semantic_markdown(path: Path, observed_epoch: int) -> bytes:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    output: list[str] = []
    in_header = True
    lease: str | None = None
    for line in lines:
        if in_header and not line.strip():
            in_header = False
        if in_header and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            if key == "lease_expires":
                lease = lease_state(value.strip(), observed_epoch)
                continue
            if key in {"event_seq", "last_transition_id"}:
                continue
        output.append(line)
    return json.dumps(
        {"content": "".join(output), "lease_state": lease},
        sort_keys=True, separators=(",", ":"),
    ).encode()


def semantic_run(path: Path, observed_epoch: int) -> bytes:
    value = read_json(path)
    value.pop("heartbeat_at", None)
    lease = lease_state(value.pop("lease_expires", None), observed_epoch)
    value.pop("event_seq", None)
    value.pop("last_transition_id", None)
    value["lease_state"] = lease
    if value.get("status") == "running":
        value["process_alive"] = process_alive(value.get("pid"))
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def snapshot_digest(base: Path, config: dict, goal_id: str,
                    observed_epoch: int | None = None) -> str:
    observed_epoch = int(time.time()) if observed_epoch is None else observed_epoch
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
        relative = path.relative_to(base).as_posix()
        if relative.startswith(("state/goals/", "state/tasks/")) and path.suffix == ".md":
            digest.update(semantic_markdown(path, observed_epoch))
        elif relative.startswith("state/runs/") and path.suffix == ".json":
            digest.update(semantic_run(path, observed_epoch))
        else:
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
    event = transition_event(
        "recovery-reconciled", project, goal_id, detail=snapshot,
        event_id="source-recovery-" + hashlib.sha256(
            f"{project}\0{goal_id}\0{identity}".encode()).hexdigest()[:24],
    )
    if projection.exists():
        try:
            resumed = resume_transition(base, event)
        except (OSError, TransitionReceiptError) as exc:
            raise ReconcileError(f"recovery projection repair failed: {exc}") from exc
        if not resumed:
            append_event(base, event["event"], project, goal_id, detail=snapshot,
                         event_id=event["id"])
        return
    value = {"schema_version": 1, "id": f"recovery-{identity[:24]}",
             "project_id": project, "goal_id": goal_id,
             "observed_at": now_iso(), "snapshot": snapshot}
    commit_reconcile_transition(base, [json_mutation(projection, value)], event)


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
        if current.get("project_id") != project:
            raise ReconcileError("goal compare-and-swap crossed project scope")
        if current.get("status") == expected:
            version = safe_int(current.get("version"), 1) + 1
        elif current.get("status") == target and current.get("last_transition_from") == expected:
            version = safe_int(current.get("version"), 1)
        else:
            raise ReconcileError(f"goal compare-and-swap failed: expected {expected}, found {current.get('status')}")
        transition_id = terminal_event_id(project, goal_id, expected, target, version, "transition")
        event = transition_event(
            "goal-transition", project, goal_id,
            detail={"from": expected, "to": target, "reason": reason, "version": version},
            event_id=transition_id,
        )
        try:
            if resume_transition(base, event):
                if target in TERMINAL_GOALS:
                    ensure_terminal_events(base, project, goal_id, read_fields(path))
                return
        except (OSError, TransitionReceiptError) as exc:
            raise ReconcileError(f"goal transition recovery failed: {exc}") from exc
        if current.get("status") != expected:
            raise ReconcileError("goal transition has no matching durable receipt")
        mutations = []
        if expected == "verifying" and target == "active":
            evidence = goal_evidence(base, goal_id)
            if not evidence or evidence.get("verdict") not in {
                "fail", "blocked", "timeout", "corrupt", "paused", "authority-revoked",
            }:
                raise ReconcileError("verification may reopen a goal only with failing evidence")
            # Reopen evidence is single-use. Preserve it in immutable history before changing
            # goal state; otherwise the same stale verdict makes active->verifying bounce forever.
            evidence_path = base / "state/evidence" / f"{goal_id}.json"
            history = base / "state/evidence/history"
            history.mkdir(parents=True, exist_ok=True)
            verdict = re.sub(r"[^A-Za-z0-9._-]", "_", str(evidence.get("verdict") or "unknown"))
            archived = history / f"{goal_id}-reopen-v{safe_int(current.get('version'), 1)}-{verdict}.json"
            if archived.exists():
                if evidence_path.exists() and evidence_path.read_bytes() != archived.read_bytes():
                    raise ReconcileError("verification reopen evidence history collision")
            consumed = {
                "schema_version": 1, "id": f"goal-evidence-consumed-{goal_id}-v{version}",
                "project_id": project, "goal_id": goal_id, "verdict": "consumed",
                "consumed_reason": "verification-reopened", "consumed_for_version": version,
                "consumed_task_ids": sorted(
                    str(task.get("id") or "") for _, task in goal_tasks(base, goal_id)
                ),
                "source_verdict": evidence.get("verdict"),
                "source_sha256": hashlib.sha256(
                    json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
            }
            mutations.extend([json_mutation(archived, evidence),
                              json_mutation(evidence_path, consumed)])
        if expected == "active" and target == "blocked" and reason == "task-blocked":
            # Decisions are asynchronous.  An assist may have repaired the task after the
            # decision was queued but before this CAS reached the sink.  Re-check the cause
            # while holding the same goal lock used for the status CAS.
            still_blocked = any(
                task.get("status") in {"blocked", "escalated", "cancelled"}
                for _, task in goal_tasks(base, goal_id)
            )
            if not still_blocked:
                raise ReconcileError("stale task-blocked transition: no blocked task remains")
        changes = {"status": target, "version": str(version), "last_transition_at": now_iso(),
                   "last_transition_reason": reason, "last_transition_from": expected}
        if target in TERMINAL_GOALS:
            changes["terminal_reported"] = "1"
            changes["finished_at"] = now_iso()
        mutations.append(fields_mutation(path, changes))
        commit_reconcile_transition(base, mutations, event, authoritative_index=len(mutations) - 1)
        if target in TERMINAL_GOALS:
            ensure_terminal_events(base, project, goal_id, read_fields(path))


def terminal_event_id(project: str, goal_id: str, expected: str, target: str,
                      version: int, kind: str) -> str:
    identity = f"{project}\0{goal_id}\0{expected}\0{target}\0{version}\0{kind}".encode()
    return f"source-goal-{kind}-" + hashlib.sha256(identity).hexdigest()[:24]


def ensure_terminal_events(base: Path, project: str, goal_id: str, goal: dict[str, str]) -> None:
    """Idempotently repair the event projection after a state-write/event-append crash."""
    target = goal.get("status", "")
    if target not in TERMINAL_GOALS:
        return
    expected = goal.get("last_transition_from", "")
    reason = goal.get("last_transition_reason", "")
    version = safe_int(goal.get("version"), 1)
    if not expected or not reason:
        # Legacy terminal goals do not carry enough information to synthesize an honest
        # transition.  New transitions always persist both fields before projection.
        return
    if expected == "active" and target == "blocked" and reason == "task-contract-invalid":
        task_id = goal.get("last_transition_task", "")
        category = goal.get("last_transition_category", "")
        contract_digest = goal.get("contract_digest", "")
        if not IDENT.fullmatch(task_id):
            raise ReconcileError("terminal contract rejection lacks its task identity")
        transition = task_contract_event(project, goal_id, task_id, category, contract_digest)
    else:
        transition = transition_event(
            "goal-transition", project, goal_id,
            detail={"from": expected, "to": target, "reason": reason, "version": version},
            event_id=terminal_event_id(project, goal_id, expected, target, version, "transition"),
        )
    try:
        # The state-changing CAS already owns this identity. Reuse its mutation-backed receipt;
        # treating the same event as a new pure event would collide after a successful commit.
        if not resume_transition(base, transition):
            raise ReconcileError("terminal goal transition receipt is absent")
    except (OSError, TransitionReceiptError) as exc:
        raise ReconcileError(f"terminal goal transition recovery failed: {exc}") from exc
    append_event(base, "goal-terminal", project, goal_id,
                 detail={"status": target, "reason": reason, "version": version},
                 event_id=terminal_event_id(project, goal_id, expected, target, version, "terminal"))


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
    event = transition_event(
        "review-published", project, goal_id, task_id,
        {"branch": branch, "commit_oid": remote},
        "source-review-published-" + hashlib.sha256(
            f"{project}\0{goal_id}\0{task_id}\0{remote}".encode()).hexdigest()[:24],
    )
    with goal_lock(base, goal_id):
        commit_reconcile_transition(
            base, [fields_mutation(base / "state/tasks" / f"{task_id}.md",
                                   {"review_status": "published", "review_commit": remote,
                                    "review_published_at": now_iso()})], event,
        )


def accept_review(base: Path, project: str, goal_id: str, task_id: str,
                  commit: str, reviewed_by: str) -> dict:
    """Release review backpressure only through an explicit exact-commit human seam."""
    if reviewed_by != "lucas":
        raise ReconcileError("review acceptance is reserved for Lucas's local operator seam")
    if not re.fullmatch(r"[0-9a-f]{40,64}", commit):
        raise ReconcileError("review acceptance requires an exact commit oid")
    config, _ = project_records(base, project)
    task_path = base / "state/tasks" / f"{task_id}.md"
    with goal_lock(base, goal_id):
        task = read_fields(task_path)
        if task.get("project_id") != project or task.get("goal_id") != goal_id \
                or task.get("status") != "passed":
            raise ReconcileError("review acceptance crossed project/goal scope or task is not passed")
        if task.get("review_status") == "accepted":
            if task.get("review_accepted_commit") != commit or not review_acceptance_valid(base, task):
                raise ReconcileError("prior review acceptance is inconsistent with durable evidence")
            append_event(
                base, "review-accepted", project, goal_id, task_id,
                {"commit_oid": commit, "reviewed_by": reviewed_by,
                 "review_proof": task.get("review_proof")},
                "source-review-accepted-" + hashlib.sha256(
                    f"{project}\0{goal_id}\0{task_id}\0{commit}\0{reviewed_by}".encode()
                ).hexdigest()[:24],
            )
            return {"project_id": project, "goal_id": goal_id, "task_id": task_id,
                    "commit_oid": commit, "review_status": "accepted"}
        repo = Path(str(config["repo"]))
        runs = run_records(base, {task_id})
        valid, reason, exact = task_evidence(base, repo, task, runs, require_local_review_ref=False)
        if not valid or exact.get("commit_oid") != commit:
            raise ReconcileError(f"human review lacks exact verified evidence: {reason}")
        goal = read_fields(goal_path(base, goal_id))
        budget = parse_budget(goal)
        review_proof = {"kind": "local-exact-commit"}
        if budget["publication_required"]:
            published = remote_review_commit(config, task_id)
            if published == commit:
                review_proof = {"kind": "published-review-ref", "remote_commit": published}
            else:
                # Explicit human acceptance remains mandatory; this merely supports the normal
                # merge-then-prune review workflow with a freshly fetched ancestry proof.
                review_proof = remote_default_ancestor_proof(config, commit)
        evidence = {
            "schema_version": 1,
            "id": f"review-acceptance-{task_id}",
            "project_id": project,
            "goal_id": goal_id,
            "task_id": task_id,
            "commit_oid": commit,
            "reviewed_by": reviewed_by,
            "implementer_run_id": exact.get("implementer_run_id"),
            "verifier_run_id": exact.get("verifier_run_id"),
            "review_proof": review_proof,
            "accepted_at": now_iso(),
        }
        evidence_path = base / "state/evidence" / f"review-{task_id}.json"
        if evidence_path.exists():
            prior = read_json(evidence_path)
            stable = (prior.get("project_id"), prior.get("goal_id"), prior.get("task_id"),
                      prior.get("commit_oid"), prior.get("reviewed_by"))
            expected = (project, goal_id, task_id, commit, reviewed_by)
            if stable != expected:
                raise ReconcileError("review acceptance evidence collides with different authority")
            evidence = prior
            prior_proof = prior.get("review_proof") if isinstance(prior.get("review_proof"), dict) else {}
            if prior_proof.get("kind") not in {
                    "local-exact-commit", "published-review-ref", "remote-default-ancestor"}:
                raise ReconcileError("prior review acceptance lacks a durable authority proof")
            review_proof = prior_proof
        event = transition_event(
            "review-accepted", project, goal_id, task_id,
            {"commit_oid": commit, "reviewed_by": reviewed_by,
             "review_proof": review_proof["kind"]},
            "source-review-accepted-" + hashlib.sha256(
                f"{project}\0{goal_id}\0{task_id}\0{commit}\0{reviewed_by}".encode()
            ).hexdigest()[:24],
        )
        commit_reconcile_transition(
            base,
            [json_mutation(evidence_path, evidence),
             fields_mutation(task_path, {"candidate_commit": commit,
                                         "review_status": "accepted",
                                         "review_accepted_commit": commit,
                                         "review_proof": str(review_proof["kind"]),
                                         "reviewed_by": reviewed_by,
                                         "review_accepted_at": str(evidence["accepted_at"])})],
            event,
            authoritative_index=1,
        )
    return {"project_id": project, "goal_id": goal_id, "task_id": task_id,
            "commit_oid": commit, "review_status": "accepted"}


def review_acceptance_valid(base: Path, task: dict[str, str]) -> bool:
    if task.get("review_status") != "accepted" or task.get("reviewed_by") != "lucas":
        return False
    task_id = task.get("id", "")
    try:
        evidence = read_json(base / "state/evidence" / f"review-{task_id}.json")
    except ReconcileError:
        return False
    commit = task.get("review_accepted_commit", "")
    proof = evidence.get("review_proof") if isinstance(evidence.get("review_proof"), dict) else {}
    return bool(
        re.fullmatch(r"[0-9a-f]{40,64}", commit)
        and evidence.get("project_id") == task.get("project_id")
        and evidence.get("goal_id") == task.get("goal_id")
        and evidence.get("task_id") == task_id
        and evidence.get("commit_oid") == commit
        and evidence.get("reviewed_by") == "lucas"
        and proof.get("kind") in {"local-exact-commit", "published-review-ref", "remote-default-ancestor"}
        and task.get("review_proof") == proof.get("kind")
        and task.get("candidate_commit") == commit
    )


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


def run_gate_interruptibly(base: Path, cwd: Path, command: str, deadline: int,
                           network_policy: str, read_only_paths: Iterable[str] = (),
                           read_only_worktree: bool = False,
                           window: dict | None = None) -> tuple[str, int]:
    argv = ["bash", str(base / "scripts/worker-sandbox.sh"), "--engine", "gate", "--role", "gate",
            "--worktree", str(cwd), "--workdir", ".", "--network-policy", "none",
            "--gate-command", command]
    if read_only_worktree:
        argv.append("--read-only-worktree")
    for path in read_only_paths:
        argv.extend(("--read-only-path", path))
    process = subprocess.Popen(
        argv,
        cwd=base, start_new_session=True,
    )
    while process.poll() is None:
        if (base / "state/PAUSE").exists():
            terminate_group(process.pid)
            process.wait()
            return "paused", 75
        if not window_authority_current(base, window):
            terminate_group(process.pid)
            process.wait()
            return "authority-revoked", 75
        if time.time() >= deadline:
            terminate_group(process.pid)
            process.wait()
            return "timeout", 124
        time.sleep(0.05)
    return ("pass", 0) if process.returncode == 0 else ("fail", int(process.returncode or 1))


def goal_seed_contract(goal: dict[str, str]) -> dict | None:
    seed = goal.get("seed", "").replace(",", " ").split()
    values = (goal.get("seed_manifest", ""), goal.get("seed_manifest_sha256", ""),
              goal.get("seed_digest", ""))
    if not seed and not any(values):
        return None
    if not seed or not all(values) or any(not re.fullmatch(r"[0-9a-f]{64}", item) for item in values[1:]):
        raise SeedContractError("goal seed metadata is incomplete or malformed")
    return {"schema_version": 1, "manifest_path": values[0], "manifest_sha256": values[1],
            "content_sha256": values[2], "paths": seed}


def acquire_goal_heavy(base: Path, tag: str, deadline: int,
                       window: dict | None = None) -> tuple[str, int, bool]:
    env = os.environ.copy()
    env.update({"RECURSION_ROOT": str(base), "RECURSION_HEAVY_TAG": tag,
                "RECURSION_HEAVY_PID": str(os.getpid())})
    while True:
        if (base / "state/PAUSE").exists():
            return "paused", 75, False
        if not window_authority_current(base, window):
            return "authority-revoked", 75, False
        if time.time() >= deadline:
            return "timeout", 124, False
        attempt = subprocess.run(
            ["bash", str(base / "scripts/capacity.sh"), "heavy", "acquire", tag],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
        if attempt.returncode == 0:
            return "pass", 0, True
        if attempt.returncode != 4:
            raise ReconcileError("heavy goal gate capacity controller failed closed")
        time.sleep(0.05)


def release_goal_heavy(base: Path) -> None:
    env = os.environ.copy()
    env.update({"RECURSION_ROOT": str(base), "RECURSION_HEAVY_PID": str(os.getpid())})
    released = subprocess.run(
        ["bash", str(base / "scripts/capacity.sh"), "heavy", "release"], env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    if released.returncode:
        raise ReconcileError("heavy goal gate lock release failed closed")


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _observed_goal_gate(base: Path, worktree: Path, goal: dict[str, str],
                        config: dict) -> dict | None:
    """Run the execution validator against the goal worktree and parse its contract."""
    validator = subprocess.run(
        [sys.executable, str(base / "scripts/validate-gate.py"),
         "--acceptance", goal["acceptance_suite"],
         "--allowed-paths", ",".join(config.get("allowed_paths") or []),
         "--gate-files", goal.get("gate_files", ""), "--repo", str(worktree),
         "--controller-root", str(base),
         "--controller-gate-files", goal.get("controller_gate_files", ""),
         "--strict-direct"],
        text=True, capture_output=True, check=False,
    )
    if validator.returncode != 0:
        return None
    try:
        value = json.loads(validator.stdout)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def make_worktree_read_only(worktree: Path) -> None:
    """Make the terminal-gate worktree OS read-only before the conformance executes."""
    proc = subprocess.run(["chmod", "-R", "a-w", str(worktree)], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, check=False)
    if proc.returncode:
        raise ReconcileError("terminal gate worktree could not be made OS read-only")


def restore_worktree_permissions(worktree: Path) -> None:
    subprocess.run(["chmod", "-R", "u+w", str(worktree)], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False)


def log_terminal_gate_refused(base: Path, project: str, goal_id: str, exc: Exception) -> None:
    append_event(base, "terminal-gate-refused", project, goal_id,
                 detail={"goal_id": goal_id,
                         "reason": "read-only-grading-unavailable",
                         "error_sha256": hashlib.sha256(str(exc).encode()).hexdigest()},
                 event_id="source-terminal-gate-refused-" + hashlib.sha256(
                     f"{project}\0{goal_id}".encode()).hexdigest()[:24])


def _phase8_expected_task_values(config: dict, pilot: dict, plan: dict, plan_id: str,
                                 digest: str, goal_id: str, task: dict) -> dict[str, str]:
    """Mirror project-pilot.task_values so the materialized DAG can be re-proven exactly."""
    authority = plan.get("authority_contract") if isinstance(plan.get("authority_contract"), dict) else {}
    seed = plan.get("seed_contract") if isinstance(plan.get("seed_contract"), dict) else None
    values = {
        "schema_version": "1", "version": "1", "id": task["id"], "project_id": config["id"],
        "project": config["id"], "workstream": config["id"], "pilot_id": pilot["id"],
        "goal_id": goal_id, "plan_id": plan_id, "plan_digest": digest,
        "dependencies": ",".join(task.get("dependencies") or []), "goal": task["intent"],
        "allowed_paths": ",".join(task.get("allowed_paths") or []),
        "non_goals": ",".join(task.get("non_goals") or []), "worker_class": task["worker_class"],
        "engine": task["engine"], "model_alias": task["model_alias"],
        "verifier_model_alias": task["verifier_model_alias"],
        "deadline_seconds": str(task["deadline_seconds"]),
        "verifier_deadline_seconds": str(task["verifier_deadline_seconds"]),
        "network_policy": task["network_policy"], "evidence_contract": task["evidence_contract"],
        "verification": task["verification"], "expected_change": task["expected_change"],
        "gate_class": task["gate_class"],
        "gate_contract": json.dumps(task["gate_contract"], sort_keys=True, separators=(",", ":")),
        "gate_files": ",".join(task.get("gate_files") or []), "acceptance": task["acceptance"],
        "controller_gate_files": ",".join(task.get("controller_gate_files") or []),
        "source_head": str(authority.get("source_head") or ""),
        "source_branch": str(authority.get("default_branch") or ""),
        "charter_sha256": str(authority.get("charter_sha256") or ""),
        "repo": str(config.get("repo") or ""), "workdir": ".", "autonomy": "auto",
    }
    if task.get("source_task_id"):
        values["source_task_id"] = task["source_task_id"]
    if seed:
        values.update({
            "seed_manifest": seed["manifest_path"], "seed_manifest_sha256": seed["manifest_sha256"],
            "seed": ",".join(seed["paths"]), "seed_digest": seed["content_sha256"],
        })
    selection = plan.get("gate_profile_selection")
    if isinstance(selection, dict):
        values["gate_profile_selection"] = json.dumps(
            selection, sort_keys=True, separators=(",", ":"),
        )
    return values


def verify_phase8_goal_projection(base: Path, config: dict, pilot: dict,
                                  goal: dict[str, str], project: str, goal_id: str) -> None:
    """Re-prove the exact approved plan and its materialized goal/task projection.

    Terminal grading is authority only over the plan Lucas approved by digest.  The materialized
    goal/task files are controller-derived from that plan, so their immutable contract must still
    equal the plan's projection: a tampered goal or task, or a plan file that no longer re-hashes
    to its approved digest, fails closed before any worktree or gate runs.  Historical
    non-Phase-8 goals carry no plan_id and are not affected.
    """
    # Reuse the admission controller's canonical validator first. It rebinds the live project
    # charter, exact source HEAD, seed, gate hashes, and materialized DAG; this local mirror then
    # remains an independent fail-closed projection check rather than a weaker parallel source.
    verify_phase8_goal_contract(base, project, goal_id, terminal=True)
    plan_id = str(goal.get("plan_id") or "")
    if not plan_id:
        return
    if str(goal.get("project_id")) != project or str(goal.get("id") or "") != goal_id:
        raise ReconcileError("Phase 8 goal identity disagrees with its revalidation scope")
    try:
        proposal = read_json(base / "state/plans" / project / f"{plan_id}.json")
    except ReconcileError as exc:
        raise ReconcileError(f"approved plan is absent or unreadable: {exc}") from exc
    if proposal.get("project_id") != project or proposal.get("status") != "approved":
        raise ReconcileError("goal plan is not approved")
    plan = proposal.get("plan")
    if not isinstance(plan, dict) or str(plan.get("id") or "") != plan_id:
        raise ReconcileError("approved plan record lacks its canonical plan object")
    digest = canonical_digest(plan)
    planned_goal = plan.get("goal")
    if proposal.get("plan_digest") != digest or goal.get("plan_digest") != digest \
            or not isinstance(planned_goal, dict) or str(planned_goal.get("id") or "") != goal_id:
        raise ReconcileError("approved plan/goal digest projection differs")
    authority = plan.get("authority_contract") if isinstance(plan.get("authority_contract"), dict) else {}
    seed = plan.get("seed_contract") if isinstance(plan.get("seed_contract"), dict) else None
    expected_goal = {
        "id": goal_id, "project_id": project, "pilot_id": str(pilot.get("id") or ""),
        "plan_id": plan_id, "plan_digest": digest,
        "outcome": str(planned_goal.get("outcome") or ""),
        "acceptance_suite": str(planned_goal.get("acceptance_suite") or ""),
        "falsifier": str(planned_goal.get("falsifier") or ""),
        "gate_class": str(planned_goal.get("gate_class") or ""),
        "gate_files": ",".join(planned_goal.get("gate_files") or []),
        "controller_gate_files": ",".join(planned_goal.get("controller_gate_files") or []),
        "gate_contract": json.dumps(planned_goal.get("gate_contract"),
                                    sort_keys=True, separators=(",", ":")),
        "source_head": str(authority.get("source_head") or ""),
        "source_branch": str(authority.get("default_branch") or ""),
        "charter_sha256": str(authority.get("charter_sha256") or ""),
        "budget": json.dumps(planned_goal.get("budget"), sort_keys=True, separators=(",", ":")),
    }
    if seed:
        expected_goal.update({"seed_manifest": seed["manifest_path"],
                              "seed_manifest_sha256": seed["manifest_sha256"],
                              "seed": ",".join(seed["paths"]),
                              "seed_digest": seed["content_sha256"]})
    selection = plan.get("gate_profile_selection")
    if isinstance(selection, dict):
        expected_goal["gate_profile_selection"] = json.dumps(
            selection, sort_keys=True, separators=(",", ":"),
        )
    if any(goal.get(key, "") != str(value) for key, value in expected_goal.items()):
        raise ReconcileError("materialized goal immutable contract differs from its approved plan")
    planned = list(plan.get("tasks") or [])
    planned_ids = {str(task.get("id") or "") for task in planned}
    actual_ids = {value.get("id", "") for _, value in goal_tasks(base, goal_id)}
    if planned_ids != actual_ids:
        raise ReconcileError("materialized task DAG differs from the exact approved plan")
    for task in planned:
        task_id = str(task.get("id") or "")
        try:
            expected = _phase8_expected_task_values(config, pilot, plan, plan_id, digest, goal_id, task)
        except (KeyError, TypeError) as exc:
            raise ReconcileError("approved plan task is schema-incomplete") from exc
        expected.pop("status", None)
        actual = read_fields(base / "state/tasks" / f"{task_id}.md")
        if any(actual.get(key, "") != str(value) for key, value in expected.items()):
            raise ReconcileError(
                f"materialized task {task_id} immutable contract differs from its approved plan"
            )


def verify_goal(base: Path, project: str, goal_id: str,
                window: dict | None = None) -> None:
    config, pilot = project_records(base, project)
    window = terminal_window_authority(pilot, window)
    goal = read_fields(goal_path(base, goal_id))
    if goal.get("status") != "verifying":
        raise ReconcileError("goal verification requires status=verifying")
    budget = parse_budget(goal)
    tasks = goal_tasks(base, goal_id)
    if not tasks or any(task.get("status") != "passed" for _, task in tasks):
        raise ReconcileError("goal verification requires every task passed")
    evidence_path = base / "state/evidence" / f"{goal_id}.json"
    # Phase 8 goals are graded only against the plan Lucas approved by digest. Re-prove the
    # exact approved plan and the materialized goal/task projection BEFORE any worktree or gate
    # runs: a tampered projection fails closed here. Historical non-Phase-8 goals carry no
    # plan_id and are not affected.
    if goal.get("plan_id"):
        try:
            verify_phase8_goal_projection(base, config, pilot, goal, project, goal_id)
        except ReconcileError as exc:
            value = {"schema_version": 1, "id": f"goal-evidence-{goal_id}", "project_id": project,
                     "goal_id": goal_id, "verdict": "fail",
                     "reason": f"phase8-contract: {exc}", "checked_at": now_iso()}
            event = transition_event(
                "goal-verification", project, goal_id, detail=value,
                event_id="source-goal-verification-" + hashlib.sha256(
                    json.dumps([project, goal_id, value], sort_keys=True,
                               separators=(",", ":")).encode()).hexdigest()[:24],
            )
            with goal_lock(base, goal_id):
                commit_reconcile_transition(base, [json_mutation(evidence_path, value)], event)
            return
    repo = Path(str(config["repo"]))
    try:
        seed_contract = goal_seed_contract(goal)
        seed_live = validate_contract(repo, seed_contract) if seed_contract else None
    except (OSError, SeedContractError) as exc:
        value = {"schema_version": 1, "id": f"goal-evidence-{goal_id}", "project_id": project,
                 "goal_id": goal_id, "verdict": "fail", "reason": f"seed-contract: {exc}",
                 "checked_at": now_iso()}
        event = transition_event(
            "goal-verification", project, goal_id, detail=value,
            event_id="source-goal-verification-" + hashlib.sha256(
                json.dumps([project, goal_id, value], sort_keys=True,
                           separators=(",", ":")).encode()).hexdigest()[:24],
        )
        with goal_lock(base, goal_id):
            commit_reconcile_transition(
                base, [json_mutation(base / "state/evidence" / f"{goal_id}.json", value)], event,
            )
        return
    for _, task in tasks:
        if any(task.get(key, "") != goal.get(key, "")
               for key in ("seed_manifest", "seed_manifest_sha256", "seed", "seed_digest")):
            raise ReconcileError("task and goal seed contracts disagree")
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
    if not valid:
        value = {"schema_version": 1, "id": f"goal-evidence-{goal_id}", "project_id": project,
                 "goal_id": goal_id, "verdict": "fail", "reason": reason,
                 "checked_at": now_iso(), "commit_oid": exact.get("commit_oid")}
        event = transition_event(
            "goal-verification", project, goal_id, detail=value,
            event_id="source-goal-verification-" + hashlib.sha256(
                json.dumps([project, goal_id, value], sort_keys=True,
                           separators=(",", ":")).encode()).hexdigest()[:24],
        )
        with goal_lock(base, goal_id):
            commit_reconcile_transition(base, [json_mutation(evidence_path, value)], event)
        return
    if budget["publication_required"] and remote_review_commit(config, str(sink["id"])) != exact["commit_oid"]:
        raise ReconcileError("goal verification requires the exact published review ref")
    commit = exact["commit_oid"]
    if pilot.get("window_required") and window is None:
        window = require_window(base, project, goal_id)
    started = int(time.time())
    wall_deadline = goal_wall_clock_deadline(
        base, project, goal_id, goal, pilot, budget, window, started,
    )
    verify_root = repo / ".worktrees"
    verify_root.mkdir(parents=True, exist_ok=True)
    worktree = verify_root / f"goal-{goal_id}-verify-{commit[:12]}-{os.getpid()}"
    proc = subprocess.run(["git", "-C", str(repo), "worktree", "add", "--detach", str(worktree), commit],
                          text=True, capture_output=True, check=False)
    if proc.returncode:
        raise ReconcileError((proc.stderr or proc.stdout or "goal verification worktree failed").strip())
    heavy_held = False
    try:
        # Model calls may use provider-only capability. Acceptance never inherits it: product
        # and terminal gates are deterministic offline controller executions.
        network_policy = "none"
        gate_class = goal.get("gate_class", "light")
        if gate_class not in {"light", "heavy"}:
            raise ReconcileError("goal gate has an invalid gate class")
        try:
            approved_gate = json.loads(goal.get("gate_contract", "")) if goal.get("gate_contract") else None
        except json.JSONDecodeError as exc:
            raise ReconcileError("goal gate lacks its approved contract") from exc
        # Re-prove the repository/controller gate hashes BEFORE the gate.  A goal that declares no
        # approved contract (historical non-Phase-8 goal) still has its observed contract proven
        # structurally and, after the gate, proven byte-stable.
        gate_before = _observed_goal_gate(base, worktree, goal, config)
        gate_contract_valid = bool(
            gate_before is not None and (approved_gate is None or gate_before == approved_gate)
        )
        seed_evidence = None
        try:
            if seed_contract and seed_live:
                copied = copy_seed_paths(repo, worktree, seed_contract["paths"],
                                         seed_contract["content_sha256"])
                copied_contract = validate_contract(worktree, seed_contract)
                seed_evidence = {
                    "manifest_path": seed_contract["manifest_path"],
                    "manifest_sha256": seed_contract["manifest_sha256"],
                    "content_sha256": copied["content_sha256"],
                    "path_count": copied["path_count"], "file_count": copied["file_count"],
                    "verified_before": copied_contract["content_sha256"] == copied["content_sha256"],
                }
        except (OSError, SeedContractError):
            seed_evidence = {
                "manifest_path": seed_contract["manifest_path"] if seed_contract else "",
                "manifest_sha256": seed_contract["manifest_sha256"] if seed_contract else "",
                "content_sha256": seed_contract["content_sha256"] if seed_contract else "",
                "verified_before": False, "verified_after": False,
                "error": "copy-or-validation-failed",
            } if seed_contract else None
            outcome, rc = "fail", 99
        else:
            if not gate_contract_valid:
                outcome, rc = "fail", 98
            elif gate_class == "heavy":
                outcome, rc, heavy_held = acquire_goal_heavy(
                    base, f"goal-{goal_id}", wall_deadline, window,
                )
            else:
                outcome, rc = "pass", 0
            if outcome == "pass":
                # The whole gate runs against the exact-commit worktree made OS read-only: a
                # conformance that reversibly tampers with a gate file cannot write it, so the
                # tampering fails the gate instead of passing silently between two hash checks.
                try:
                    make_worktree_read_only(worktree)
                except ReconcileError as exc:
                    restore_worktree_permissions(worktree)
                    log_terminal_gate_refused(base, project, goal_id, exc)
                    outcome, rc = "fail", 99
                else:
                    try:
                        outcome, rc = run_gate_interruptibly(
                            base, worktree, goal["acceptance_suite"], wall_deadline, network_policy,
                            ([seed_contract["manifest_path"], *seed_contract["paths"]]
                             if seed_contract else ()),
                            read_only_worktree=True,
                            window=window,
                        )
                    finally:
                        restore_worktree_permissions(worktree)
                    # Re-prove repository/controller gate hashes AFTER the gate too.  Combined
                    # with the read-only run, before == after closes the TOCTOU window.
                    gate_after = _observed_goal_gate(base, worktree, goal, config)
                    if gate_after is None or gate_after != gate_before:
                        outcome, rc = "fail", 99
        if seed_contract and seed_evidence:
            try:
                after = validate_contract(worktree, seed_contract)
                seed_evidence["verified_after"] = (
                    after["content_sha256"] == seed_contract["content_sha256"]
                    and after["file_count"] == seed_evidence["file_count"]
                )
            except (OSError, SeedContractError):
                seed_evidence["verified_after"] = False
            if not seed_evidence["verified_after"]:
                outcome, rc = "fail", 99
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
                 "checked_at": now_iso(), "worktree_clean": not bool(dirty),
                 "gate_class": gate_class}
        if seed_evidence:
            value["seed_evidence"] = seed_evidence
        event = transition_event(
            "goal-verification", project, goal_id, detail=value,
            event_id="source-goal-verification-" + hashlib.sha256(
                json.dumps([project, goal_id, value], sort_keys=True,
                           separators=(",", ":")).encode()).hexdigest()[:24],
        )
        with goal_lock(base, goal_id):
            commit_reconcile_transition(base, [json_mutation(evidence_path, value)], event)
        if outcome in {"paused", "authority-revoked"}:
            raise ReconcileError("execution authority interrupted exact-commit goal verification")
    finally:
        release_error = None
        if heavy_held:
            try:
                release_goal_heavy(base)
            except ReconcileError as exc:
                release_error = exc
        subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if release_error:
            raise release_error


def goal_evidence(base: Path, goal_id: str) -> dict | None:
    path = base / "state/evidence" / f"{goal_id}.json"
    if not path.is_file():
        return None
    try:
        return read_json(path)
    except ReconcileError:
        return {"verdict": "corrupt"}


def consumed_evidence_has_new_task_graph(evidence: dict | None,
                                         tasks: list[tuple[Path, dict[str, str]]]) -> bool:
    """A consumed failure permits re-verification only after remediation changed the task graph."""
    if not evidence or evidence.get("verdict") != "consumed":
        return True
    prior = evidence.get("consumed_task_ids")
    current = sorted(str(task.get("id") or "") for _, task in tasks)
    return isinstance(prior, list) and all(isinstance(item, str) for item in prior) \
        and sorted(prior) != current


def consumed_revocation_allows_same_graph_retry(evidence: dict | None) -> bool:
    """Revoked authority did not judge the commit, so it may be retried unchanged."""
    return bool(
        evidence and evidence.get("verdict") == "consumed"
        and evidence.get("source_verdict") == "authority-revoked"
    )


def enqueue_transition(base: Path, pilot: dict, project: str, goal_id: str, expected: str,
                       target: str, reason: str, version: str) -> None:
    enqueue_decision(base, str(pilot["id"]), "goal-transition",
                     [project, goal_id, expected, target, reason], goal_id, reason,
                     [project, goal_id, expected, target, reason, version])


def reconcile(base: Path, project: str, goal_id: str,
              window: dict | None = None) -> None:
    config, pilot = project_records(base, project)
    goal_file = goal_path(base, goal_id)
    with goal_lock(base, goal_id):
        goal = read_fields(goal_file)
        if goal.get("project_id") != project:
            raise ReconcileError("goal is outside this project pilot")
        status = goal.get("status", "")
        if status in TERMINAL_GOALS:
            ensure_terminal_events(base, project, goal_id, goal)
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
            elif evidence.get("verdict") == "consumed":
                authority_retry = consumed_revocation_allows_same_graph_retry(evidence)
                if authority_retry or consumed_evidence_has_new_task_graph(evidence, tasks):
                    enqueue_decision(
                        base, str(pilot["id"]), "verify-goal", [project, goal_id], goal_id,
                        ("re-run exact-commit acceptance after execution authority returned"
                         if authority_retry else
                         "re-run exact-commit acceptance after remediation changed the task graph"),
                        [project, goal_id, snapshot_digest(base, config, goal_id),
                         "authority-retry" if authority_retry else "remediated"],
                    )
            else:
                enqueue_transition(base, pilot, project, goal_id, "verifying", "active",
                                   "verification-reopened", version)
            return

        observed_epoch = int(time.time())
        started = goal_wall_clock_anchor(
            base, project, goal_id, goal, pilot, window, observed_epoch,
        )
        if observed_epoch - started > budget["max_wall_clock_seconds"]:
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
                          and not review_acceptance_valid(base, task)]
        if ready_or_proposed and len(review_backlog) >= budget["max_review_queue"]:
            append_event(base, "review-backpressure", project, goal_id,
                         detail={"backlog": len(review_backlog), "limit": budget["max_review_queue"]})
            return

        if goal.get("plan_id"):
            fresh, base_commit, freshness = phase8_fresh_base(base, project, goal_id)
            if fresh is None:
                # Availability is not proof that immutable authority is stale. Leave the
                # active graph untouched, preserve one canonical event, and durably bump one
                # escalation identity on each supervised retry.
                try:
                    record_authority_deferral(base, project, goal_id, freshness)
                except ReconcileError as audit_exc:
                    print(
                        f"project-reconcile: reconcile deferral audit unavailable: {audit_exc}",
                        file=sys.stderr,
                    )
                return
        else:
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

        evidence = goal_evidence(base, goal_id)
        if evidence and evidence.get("verdict") == "consumed" \
                and not consumed_revocation_allows_same_graph_retry(evidence) \
                and not consumed_evidence_has_new_task_graph(evidence, tasks):
            # The failed exact-commit evidence has already reopened this exact task graph.
            # Wait for a bounded remediation task instead of bouncing active->verifying forever.
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
        close_paused_windows(base)
        print(0)
        return 0
    scheduled = 0
    paths = [goal_path(base, goal_id)] if goal_id else sorted((base / "state/goals").glob("*.md"))
    for path in paths:
        try:
            goal = read_fields(path)
        except ReconcileError as exc:
            if goal_id or exc.code != 74:
                raise
            print(
                f"project-reconcile: goal record unavailable for this scheduler tick "
                f"({path.name}): {exc}",
                file=sys.stderr,
            )
            continue
        gid = goal.get("id", "")
        pid = goal.get("project_id", "")
        if not IDENT.fullmatch(gid) or not IDENT.fullmatch(pid):
            continue
        if project and pid != project:
            continue
        if goal.get("status") in TERMINAL_GOALS:
            try:
                with goal_lock(base, gid):
                    current = read_fields(path)
                    if current.get("status") in TERMINAL_GOALS:
                        ensure_terminal_events(base, pid, gid, current)
            except ReconcileError:
                pass
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
        if pilot.get("window_required"):
            try:
                if not open_window(base, pid, gid, pilot):
                    continue
            except ReconcileError as exc:
                if exc.code != 4:
                    try:
                        record_authority_deferral(
                            base, pid, gid, "window-authority-unavailable", exc,
                        )
                    except ReconcileError as audit_exc:
                        print(
                            f"project-reconcile: window deferral audit unavailable: {audit_exc}",
                            file=sys.stderr,
                        )
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
    sub.add_parser("close-paused-windows")
    admit_cmd = sub.add_parser("admit-work")
    admit_cmd.add_argument("task")
    check_work_cmd = sub.add_parser("check-work-authority")
    check_work_cmd.add_argument("task")
    resume_cmd = sub.add_parser("resume-assist")
    resume_cmd.add_argument("task")
    resume_cmd.add_argument("instruction")
    reject_cmd = sub.add_parser("reject-task-contract")
    reject_cmd.add_argument("task")
    reject_cmd.add_argument("category")
    reject_cmd.add_argument("contract_digest")
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
    review_cmd = sub.add_parser("accept-review")
    review_cmd.add_argument("project")
    review_cmd.add_argument("goal")
    review_cmd.add_argument("task")
    review_cmd.add_argument("commit")
    review_cmd.add_argument("reviewed_by")
    args = parser.parse_args()
    base = root()
    try:
        if args.command == "schedule":
            return schedule(base, args.project, args.goal)
        if args.command == "close-paused-windows":
            print(close_paused_windows(base))
            return 0
        if args.command == "resume-assist":
            print(json.dumps(resume_assist(base, args.task, args.instruction),
                             sort_keys=True, separators=(",", ":")))
            return 0
        if args.command == "reject-task-contract":
            print(json.dumps(reject_task_contract(base, args.task, args.category, args.contract_digest),
                             sort_keys=True, separators=(",", ":")))
            return 0
        if (base / "state/PAUSE").exists():
            raise ReconcileError("PAUSE blocks Phase 6 actuation", 75)
        if args.command == "admit-work":
            print(json.dumps(admit_work(base, args.task), sort_keys=True, separators=(",", ":")))
        elif args.command == "check-work-authority":
            print(json.dumps(check_work_authority(base, args.task),
                             sort_keys=True, separators=(",", ":")))
        elif args.command == "accept-review":
            print(json.dumps(accept_review(base, args.project, args.goal, args.task,
                                           args.commit, args.reviewed_by),
                             sort_keys=True, separators=(",", ":")))
        elif args.command == "reconcile":
            window = require_window(base, args.project, args.goal)
            reconcile(base, args.project, args.goal, window)
        elif args.command == "transition-task":
            require_window(base, args.project, args.goal)
            transition_task(base, args.project, args.goal, args.task, args.expected, args.target, args.reason)
        elif args.command == "transition-goal":
            require_window(base, args.project, args.goal)
            transition_goal(base, args.project, args.goal, args.expected, args.target, args.reason)
        elif args.command == "verify-goal":
            window = require_window(base, args.project, args.goal)
            verify_goal(base, args.project, args.goal, window)
        else:
            require_window(base, args.project, args.goal)
            publish_task(base, args.project, args.goal, args.task)
    except ReconcileError as exc:
        print(f"project-reconcile: {exc}", file=sys.stderr)
        return exc.code
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"project-reconcile: {exc}", file=sys.stderr)
        return 74
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

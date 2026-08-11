#!/usr/bin/env python3
"""Rotate, back up, and restore ignored Recursion runtime state.

All mutating commands require state/PAUSE and a fail-closed runtime-state lock. Secrets, deploy
keys, repositories, and the Hermes SQLite database are intentionally outside this file backup;
the Phase 0 runbook retains their separate human-controlled procedures.
"""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import errno
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

try:
    import fcntl
except ImportError:  # pragma: no cover - production is Linux.
    fcntl = None  # type: ignore[assignment]


RUNTIME_FILE_PATHS = (
    "state/PAUSE",
    "state/events.jsonl",
    "state/action-events.jsonl",
    "state/decisions.jsonl",
    "state/delivery-events.jsonl",
    "state/notification-event-events.jsonl",
    "state/notification-audit-events.jsonl",
    "state/notification-recovery-events.jsonl",
    "state/escalations.tsv",
    "state/.intake-watermark",
    "state/.openrouter-usage.json",
)

RUNTIME_DIRECTORY_PATHS = (
    "state/actions",
    "state/decision-queue",
    "state/instructions",
    "state/goals",
    "state/tasks",
    "state/assists",
    "state/pilot-requests",
    "state/plans",
    "state/pilot-windows",
    "state/runs",
    "state/evidence",
    "state/recovery",
    "state/deliveries",
    "state/notification-events",
    "state/jsonl-quarantine",
    "state/transport-evidence",
    "state/reports",
    "state/event-archive",
)

RUNTIME_PATHS = RUNTIME_FILE_PATHS + RUNTIME_DIRECTORY_PATHS
RESTORE_TRANSACTION = "runtime-restore.transaction"
MANIFEST_SHA256 = re.compile(r"[0-9a-f]{64}")
MANIFEST_MODE = re.compile(r"0o[0-7]{3}")


def reconcile_transition_receipts(root: Path) -> None:
    """Project committed audit receipts before taking or restoring a maintenance cut."""
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    try:
        from transition_receipt import TransitionReceiptError, recover_transitions
    except ImportError as exc:
        raise RuntimeError("transition receipt projector is absent") from exc
    prior_owner = os.environ.get("RECURSION_TASKCTL_LOCK_OWNER_PID")
    prior_runtime_owner = os.environ.get("RECURSION_RUNTIME_LOCK_OWNER_PID")
    os.environ["RECURSION_TASKCTL_LOCK_OWNER_PID"] = str(os.getpid())
    os.environ["RECURSION_RUNTIME_LOCK_OWNER_PID"] = str(os.getpid())
    try:
        recover_transitions(root, taskctl_locked=True)
    except (OSError, TransitionReceiptError) as exc:
        raise RuntimeError(f"transition receipt recovery failed before maintenance: {exc}") from exc
    finally:
        if prior_owner is None:
            os.environ.pop("RECURSION_TASKCTL_LOCK_OWNER_PID", None)
        else:
            os.environ["RECURSION_TASKCTL_LOCK_OWNER_PID"] = prior_owner
        if prior_runtime_owner is None:
            os.environ.pop("RECURSION_RUNTIME_LOCK_OWNER_PID", None)
        else:
            os.environ["RECURSION_RUNTIME_LOCK_OWNER_PID"] = prior_runtime_owner


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def fsync_dir(path: Path) -> None:
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_bytes(path: Path, value: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    temporary = Path(name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as output:
            output.write(value)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        fsync_dir(path.parent)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _safe_remove_tree(path: Path) -> None:
    """Remove only a real, unlinked tree; never traverse a symlink during cleanup."""
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or not path.is_dir():
        raise RuntimeError(f"refusing unsafe runtime cleanup target: {path}")
    for item in path.rglob("*"):
        if item.is_symlink():
            raise RuntimeError(f"refusing symlink in runtime cleanup tree: {item}")
    shutil.rmtree(path)
    fsync_dir(path.parent)


def _process_identity(pid: int) -> tuple[int, str]:
    if pid < 1:
        raise RuntimeError("lock owner PID must be positive")
    start = process_start(pid)
    if not start or not start.isdigit():
        raise RuntimeError(f"cannot witness lock owner process start: {pid}")
    if process_is_live(pid) is not True:
        raise RuntimeError(f"lock owner process is not live: {pid}")
    return pid, start


def _owner_values_are_dead(pid: int, witnessed_start: str) -> bool:
    live = process_is_live(pid)
    if live is False:
        return True
    if live is not True:
        return False
    current_start = process_start(pid)
    return bool(witnessed_start and current_start and witnessed_start != current_start)


def _rename_noreplace(source: Path, target: Path) -> None:
    """Atomically publish a complete directory without replacing another owner."""
    if os.name == "nt":  # os.rename is no-replace on Windows; production is Linux.
        os.rename(source, target)
        return
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    if renameat2 is None:
        raise RuntimeError("renameat2(RENAME_NOREPLACE) is unavailable; refusing unsafe lock publish")
    renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
                          ctypes.c_uint]
    renameat2.restype = ctypes.c_int
    result = renameat2(-100, os.fsencode(source), -100, os.fsencode(target), 1)
    if result == 0:
        return
    error = ctypes.get_errno()
    if error in {errno.EEXIST, errno.ENOTEMPTY}:
        raise FileExistsError(error, os.strerror(error), str(target))
    raise OSError(error, os.strerror(error), str(target))


def _candidate_identity(path: Path, lock_name: str) -> tuple[int, str] | None:
    prefix = f".{lock_name}.candidate."
    if not path.name.startswith(prefix):
        return None
    fields = path.name[len(prefix):].split(".", 2)
    if len(fields) != 3 or not fields[0].isdigit() or not fields[1].isdigit():
        return None
    return int(fields[0]), fields[1]


def _cleanup_dead_lock_candidates(path: Path) -> None:
    for candidate in path.parent.glob(f".{path.name}.candidate.*"):
        identity = _candidate_identity(candidate, path.name)
        if identity is None or not _owner_values_are_dead(*identity):
            continue
        tomb = path.parent / f".{path.name}.candidate-dead.{os.getpid()}.{time.time_ns()}"
        try:
            _rename_noreplace(candidate, tomb)
        except (FileNotFoundError, FileExistsError):
            continue
        _safe_remove_tree(tomb)


def _allowed_lock_evidence(path: Path) -> set[str]:
    allowed = {"pid", "start", "owner"}
    if path.name == "heavy-gate.lock":
        allowed.add("holder")
    return allowed


def _lock_failpoint(name: str) -> None:
    if os.environ.get("RECURSION_LOCK_CRASH_AT") == name:
        os._exit(91)


def acquire_witnessed_directory_lock(path: Path, label: str, owner_pid: int) -> None:
    """Publish a fully witnessed mkdir-compatible lock in one no-replace rename."""
    owner_pid, owner_start = _process_identity(owner_pid)
    creator_pid, creator_start = _process_identity(os.getpid())
    path.parent.mkdir(parents=True, exist_ok=True)
    attempts = max(1, int(os.environ.get("RECURSION_LOCK_ATTEMPTS", "100")))
    delay = max(0.0, float(os.environ.get("RECURSION_LOCK_DELAY_S", "0.1")))
    for attempt in range(attempts):
        _assert_runtime_lock_compatible(path, owner_pid, owner_start)
        _cleanup_dead_lock_candidates(path)
        candidate = Path(tempfile.mkdtemp(
            prefix=f".{path.name}.candidate.{creator_pid}.{creator_start}.", dir=path.parent
        ))
        try:
            _lock_failpoint("after-candidate-mkdir")
            atomic_bytes(candidate / "pid", f"{owner_pid}\n".encode("ascii"))
            _lock_failpoint("after-candidate-pid")
            atomic_bytes(candidate / "start", f"{owner_start}\n".encode("ascii"))
            _lock_failpoint("after-candidate-start")
            fsync_dir(candidate)
            try:
                _rename_noreplace(candidate, path)
            except FileExistsError:
                _safe_remove_tree(candidate)
                if owner_is_dead(path):
                    tomb = path.with_name(f".{path.name}.dead.{os.getpid()}.{attempt}")
                    try:
                        _rename_noreplace(path, tomb)
                    except (FileNotFoundError, FileExistsError, OSError):
                        pass
                    else:
                        allowed = _allowed_lock_evidence(path)
                        unexpected = [item.name for item in tomb.iterdir()
                                      if item.name not in allowed]
                        if unexpected:
                            raise RuntimeError(
                                f"dead {label} lock contains unexpected evidence: {unexpected[0]}"
                            )
                        for name in allowed:
                            (tomb / name).unlink(missing_ok=True)
                        tomb.rmdir()
                        fsync_dir(path.parent)
                        continue
                if attempt + 1 < attempts:
                    time.sleep(delay)
                continue
            fsync_dir(path.parent)
            try:
                _assert_runtime_lock_compatible(path, owner_pid, owner_start)
            except BaseException:
                release_witnessed_directory_lock(path, label, owner_pid)
                raise
            return
        except BaseException:
            if candidate.exists():
                with contextlib.suppress(OSError, RuntimeError):
                    _safe_remove_tree(candidate)
            raise
    raise RuntimeError(f"{label} lock is contended; refusing an unlocked mutation")


def _assert_runtime_lock_compatible(path: Path, owner_pid: int, owner_start: str) -> None:
    """Close the writer/maintenance race on both sides of atomic lock publication."""
    runtime = path.parent / "runtime-state.lock"
    if path == runtime or not runtime.exists():
        return
    runtime_pid, runtime_start = lock_owner(runtime)
    if runtime_pid == owner_pid and runtime_start == owner_start:
        return
    raise RuntimeError("runtime-state maintenance is active; refusing a concurrent mutation")


def release_witnessed_directory_lock(path: Path, label: str, owner_pid: int) -> None:
    owner_pid, owner_start = _process_identity(owner_pid)
    observed_pid, observed_start = lock_owner(path)
    if observed_pid != owner_pid or observed_start != owner_start:
        raise RuntimeError(f"refusing to release {label} lock owned by another process")
    tomb = path.with_name(f".{path.name}.released.{owner_pid}.{time.time_ns()}")
    _rename_noreplace(path, tomb)
    fsync_dir(path.parent)
    allowed = _allowed_lock_evidence(path)
    unexpected = [item.name for item in tomb.iterdir() if item.name not in allowed]
    if unexpected:
        raise RuntimeError(f"released {label} lock contains unexpected evidence: {unexpected[0]}")
    for name in allowed:
        (tomb / name).unlink(missing_ok=True)
    tomb.rmdir()
    fsync_dir(path.parent)


def process_start(pid: int) -> str:
    if os.name == "nt":
        class FileTime(ctypes.Structure):
            _fields_ = [("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.GetProcessTimes.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(FileTime), ctypes.POINTER(FileTime),
            ctypes.POINTER(FileTime), ctypes.POINTER(FileTime),
        ]
        kernel32.GetProcessTimes.restype = ctypes.c_int
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return ""
        created = FileTime(); exited = FileTime(); kernel = FileTime(); user = FileTime()
        try:
            if not kernel32.GetProcessTimes(
                handle, ctypes.byref(created), ctypes.byref(exited),
                ctypes.byref(kernel), ctypes.byref(user),
            ):
                return ""
            return str((created.high << 32) | created.low)
        finally:
            kernel32.CloseHandle(handle)
    try:
        return (Path("/proc") / str(pid) / "stat").read_text(encoding="utf-8").split()[21]
    except (OSError, IndexError):
        return ""


def process_is_live(pid: int) -> bool | None:
    """Probe liveness without signalling the process; None means fail closed/unknown."""
    if os.name == "nt":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        kernel32.GetExitCodeProcess.restype = ctypes.c_int
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False if ctypes.get_last_error() == 87 else None  # ERROR_INVALID_PARAMETER
        exit_code = ctypes.c_uint32()
        try:
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return None
            return exit_code.value == 259  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (PermissionError, OSError):
        return None
    return True


def lock_owner(path: Path) -> tuple[int | None, str]:
    for candidate in (path / "pid", path / "owner"):
        try:
            raw = candidate.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if raw.isdigit():
            try:
                start = (path / "start").read_text(encoding="utf-8").strip()
            except OSError:
                start = ""
            return int(raw), start
    return None, ""


def owner_is_dead(path: Path) -> bool:
    pid, witnessed_start = lock_owner(path)
    if pid is None:
        return False
    return _owner_values_are_dead(pid, witnessed_start)


class DirectoryLock:
    """PID/start-witnessed mkdir lock with atomic stale-owner reclamation."""

    def __init__(self, path: Path, label: str) -> None:
        self.path = path
        self.label = label
        self.held = False

    def __enter__(self) -> "DirectoryLock":
        acquire_witnessed_directory_lock(self.path, self.label, os.getpid())
        self.held = True
        return self

    def __exit__(self, *_: object) -> None:
        if not self.held:
            return
        release_witnessed_directory_lock(self.path, self.label, os.getpid())
        self.held = False


class RuntimeLock(DirectoryLock):
    def __init__(self, root: Path) -> None:
        super().__init__(root / "state/.locks/runtime-state.lock", "runtime-state")


class EmptyLock(DirectoryLock):
    """PID/start-compatible ownership of taskctl's mkdir mutex."""

    def __init__(self, path: Path) -> None:
        super().__init__(path, path.name)


class DecisionQueueLock:
    """The exact flock used by decision-queue.py, held across a runtime snapshot/restore."""

    def __init__(self, root: Path) -> None:
        self.path = root / "state/.locks/decision-queue.lock"
        self.handle: object | None = None

    def __enter__(self) -> "DecisionQueueLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+", encoding="utf-8")
        if fcntl is None:
            return self
        attempts = int(os.environ.get("RECURSION_LOCK_ATTEMPTS", "100"))
        delay = float(os.environ.get("RECURSION_LOCK_DELAY_S", "0.1"))
        for attempt in range(attempts):
            try:
                fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except BlockingIOError:
                if attempt + 1 < attempts:
                    time.sleep(delay)
        self.handle.close()
        self.handle = None
        raise RuntimeError("decision queue lock is contended; refusing an inconsistent snapshot")

    def __exit__(self, *_: object) -> None:
        if self.handle is not None:
            self.handle.close()
            self.handle = None


def assert_no_execution_locks(root: Path) -> None:
    lock_dir = root / "state/.locks"
    active = sorted(
        path.name
        for pattern in (
            "action-*.lock", "project-*.lock", "ws-*.lock", "planner-*.lock",
            "ledger.lock", "heavy-gate.lock",
        )
        for path in lock_dir.glob(pattern)
    )
    if active:
        raise RuntimeError("execution/state locks remain under PAUSE: " + ", ".join(active))


def require_pause(root: Path) -> Path:
    pause = root / "state/PAUSE"
    if not pause.is_file():
        raise RuntimeError("state/PAUSE is absent; refusing runtime-state maintenance")
    return pause


def require_open_notification_routing_escalation(root: Path, event_id: str) -> None:
    """Require one canonical open escalation before archiving a routing-error source."""
    path = root / "state/escalations.tsv"
    key = f"notification-routing:{event_id}"
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RuntimeError(f"notification routing escalation index is absent or unreadable: {key}") from exc
    header = "#id\tkey\tstatus\tfirst_seen\tlast_seen\tcount\tworkstream\tpointer\ttitle"
    if not raw.endswith("\n"):
        raise RuntimeError("notification routing escalation index lacks a complete final row")
    lines = raw.splitlines()
    if not lines or lines[0] != header:
        raise RuntimeError("notification routing escalation index has a noncanonical header")

    rows: list[list[str]] = []
    identities: set[str] = set()
    for number, line in enumerate(lines[1:], 2):
        fields = line.split("\t")
        if len(fields) != 9:
            raise RuntimeError(f"notification routing escalation row {number} is malformed")
        escalation_id, escalation_key, status, first_seen, last_seen, count = fields[:6]
        if (
            not re.fullmatch(r"esc-[0-9]{4,}", escalation_id)
            or escalation_id in identities
            or not escalation_key
            or status not in {"open", "resolved"}
            or not count.isdigit()
            or int(count) < 1
        ):
            raise RuntimeError(f"notification routing escalation row {number} is malformed")
        try:
            time.strptime(first_seen, "%Y-%m-%dT%H:%M:%SZ")
            time.strptime(last_seen, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as exc:
            raise RuntimeError(
                f"notification routing escalation row {number} has invalid timestamps"
            ) from exc
        if first_seen > last_seen:
            raise RuntimeError(
                f"notification routing escalation row {number} reverses its timestamps"
            )
        identities.add(escalation_id)
        rows.append(fields)

    matches = [fields for fields in rows if fields[1] == key]
    if len(matches) != 1:
        raise RuntimeError(
            f"notification routing escalation key must appear exactly once: {key}"
        )
    match = matches[0]
    if match[2] != "open":
        raise RuntimeError(f"notification routing escalation is not open: {key}")


def assert_notification_projection_complete(root: Path) -> None:
    """Refuse to archive source events without canonical, recoverable outbox projections."""
    source = root / "scripts/notification-outbox.py"
    if not source.is_file():
        source = Path(__file__).resolve().parent / "notification-outbox.py"
    if not source.is_file():
        raise RuntimeError("notification mapper is absent; refusing event rotation")
    spec = importlib.util.spec_from_file_location("recursion_notification_outbox", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("notification mapper cannot be loaded; refusing event rotation")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        expected = module.all_mapped(root)
    except Exception as exc:  # noqa: BLE001 - rotation is a fail-closed maintenance boundary.
        raise RuntimeError(f"notification mapping failed; refusing event rotation: {exc}") from exc
    projection_root = root / "state/notification-events"
    delivery_root = root / "state/deliveries"
    for event in expected:
        event_id = str(event.get("id") or "")
        if not event_id:
            raise RuntimeError("mapped source event lacks a stable notification identity")
        path = projection_root / f"{event_id}.json"
        if not path.is_file():
            raise RuntimeError(f"mapped source event lacks notification projection: {event_id}")
        try:
            observed = module.read_json(path)
            message = module.message_for(event)
            try:
                destinations = module.policy_destinations(
                    root, str(event.get("project_id") or ""), str(event.get("event_type") or "")
                )
                routing_error = None
            except (OSError, json.JSONDecodeError, module.OutboxError) as exc:
                # Match create_event's explicit durable routing-error class exactly.
                destinations = []
                routing_error = str(exc)
        except Exception as exc:  # noqa: BLE001 - malformed projection must stop rotation.
            raise RuntimeError(
                f"notification projection cannot be validated for {event_id}: {exc}"
            ) from exc

        created_at = observed.get("created_at")
        try:
            if not isinstance(created_at, str):
                raise ValueError("created_at is not a string")
            time.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                f"notification projection has invalid created_at: {event_id}"
            ) from exc
        event_sequence = observed.get("event_seq")
        transition_id = observed.get("last_transition_id")
        if (
            isinstance(event_sequence, bool)
            or not isinstance(event_sequence, int)
            or event_sequence < 1
            or not isinstance(transition_id, str)
            or not transition_id
        ):
            raise RuntimeError(f"notification projection lacks transition provenance: {event_id}")

        canonical = dict(event)
        canonical.update(
            {
                "schema_version": 1,
                "message": message,
                "created_at": created_at,
                "status": "recorded",
                "routing_error": routing_error,
                "message_digest": hashlib.sha256(message.encode()).hexdigest(),
                "event_seq": event_sequence,
                "last_transition_id": transition_id,
            }
        )
        if observed != canonical:
            raise RuntimeError(f"notification projection content mismatch: {event_id}")
        if routing_error is not None:
            require_open_notification_routing_escalation(root, event_id)

        expected_destinations = set(destinations)
        observed_deliveries: dict[str, tuple[Path, dict]] = {}
        for delivery_path in sorted(delivery_root.glob("*.json")):
            try:
                delivery = module.read_json(delivery_path)
            except Exception:
                # A malformed unrelated delivery cannot authorize this source event's rotation;
                # the canonical deterministic filename for an expected pair is checked below.
                continue
            if delivery.get("event_id") != event_id:
                continue
            destination = str(delivery.get("destination") or "")
            if destination in observed_deliveries:
                raise RuntimeError(
                    f"notification event has duplicate delivery destination: {event_id} {destination}"
                )
            observed_deliveries[destination] = (delivery_path, delivery)
        if set(observed_deliveries) != expected_destinations:
            raise RuntimeError(f"notification delivery set mismatch: {event_id}")

        for destination in destinations:
            delivery_path, delivery = observed_deliveries[destination]
            delivery_id = module.stable_id("delivery", event_id, destination)
            immutable = {
                "schema_version": 1,
                "id": delivery_id,
                "event_id": event_id,
                "project_id": event["project_id"],
                "goal_id": event.get("goal_id") or None,
                "task_id": event.get("task_id") or None,
                "destination": destination,
                "message_digest": canonical["message_digest"],
            }
            if delivery_path.name != f"{delivery_id}.json" or any(
                delivery.get(key) != value for key, value in immutable.items()
            ):
                raise RuntimeError(
                    f"notification delivery identity/content mismatch: {event_id} {destination}"
                )
            status = delivery.get("status")
            attempt = delivery.get("attempt")
            maximum = delivery.get("max_attempts")
            if (
                status not in {"pending", "failed", "running", "succeeded", "dead-letter", "cancelled"}
                or isinstance(attempt, bool)
                or not isinstance(attempt, int)
                or attempt < 0
                or isinstance(maximum, bool)
                or not isinstance(maximum, int)
                or not 1 <= maximum <= 20
            ):
                raise RuntimeError(
                    f"notification delivery is not recoverable: {event_id} {destination}"
                )


def ensure_outside_root(root: Path, path: Path) -> None:
    resolved_root = root.resolve()
    resolved = path.resolve(strict=False)
    if resolved == resolved_root or resolved_root in resolved.parents:
        raise RuntimeError("snapshot paths must be outside the Recursion checkout")


def rotate_events(root: Path, maximum: int) -> None:
    require_pause(root)
    events = root / "state/events.jsonl"
    with RuntimeLock(root), EmptyLock(root / "state/.locks/taskctl.lock"), DecisionQueueLock(root):
        require_pause(root); assert_no_execution_locks(root)
        resolve_open_restore(root)
        reconcile_transition_receipts(root)
        if not events.exists() or events.stat().st_size <= maximum:
            size = events.stat().st_size if events.exists() else 0
            print(f"rotation not needed ({size} <= {maximum})")
            return
        assert_notification_projection_complete(root)
        archive = root / "state/event-archive"
        archive.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        target = archive / f"events-{stamp}-{digest(events)[:12]}.jsonl"
        if target.exists():
            raise RuntimeError(f"rotation target already exists: {target}")
        os.replace(events, target)
        atomic_bytes(events, b"")
        fsync_dir(archive)
        print(f"rotated {target.relative_to(root)} sha256={digest(target)}")


def collect_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for relative in RUNTIME_FILE_PATHS:
        path = root / relative
        if path.is_symlink():
            raise RuntimeError(f"managed runtime path is a symlink: {relative}")
        if path.is_file():
            files.append(path)
        elif path.exists():
            raise RuntimeError(f"managed runtime file has the wrong type: {relative}")
    for relative in RUNTIME_DIRECTORY_PATHS:
        path = root / relative
        if path.is_symlink():
            raise RuntimeError(f"managed runtime path is a symlink: {relative}")
        if path.is_file():
            raise RuntimeError(f"managed runtime directory has the wrong type: {relative}")
        if not path.exists():
            continue
        for item in path.rglob("*"):
            if item.is_symlink():
                raise RuntimeError(f"managed runtime path contains a symlink: {item.relative_to(root)}")
            if item.is_file():
                files.append(item)
    return sorted(set(files))


def _managed_manifest_path(raw: object) -> str:
    if not isinstance(raw, str) or not raw or "\\" in raw or "\x00" in raw:
        raise RuntimeError(f"unsafe manifest path: {raw!r}")
    relative = PurePosixPath(raw)
    if relative.is_absolute() or relative.as_posix() != raw or ".." in relative.parts \
            or "." in relative.parts or not relative.parts or relative.parts[0] != "state":
        raise RuntimeError(f"unsafe manifest path: {raw!r}")
    if raw in RUNTIME_FILE_PATHS:
        return raw
    if any(raw.startswith(directory + "/") for directory in RUNTIME_DIRECTORY_PATHS):
        return raw
    raise RuntimeError(f"manifest path is outside managed runtime state: {raw}")


def _native_relative(relative: str) -> Path:
    return Path(*PurePosixPath(relative).parts)


def _reject_symlink_components(base: Path, relative: str, *, leaf_may_be_missing: bool = True) -> Path:
    current = base
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            raise RuntimeError(f"symlink component is forbidden: {current}")
        if not current.exists() and (leaf_may_be_missing or index + 1 < len(parts)):
            continue
    return current


def load_manifest(snapshot: Path) -> dict:
    if snapshot.is_symlink() or not snapshot.is_dir():
        raise RuntimeError(f"snapshot is absent, not a directory, or a symlink: {snapshot}")
    manifest_path = snapshot / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise RuntimeError("backup manifest is absent or a symlink")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1 \
            or not isinstance(manifest.get("files"), list):
        raise RuntimeError("unsupported or malformed backup manifest")
    pause_sha = manifest.get("pause_sha256")
    if not isinstance(pause_sha, str) or not MANIFEST_SHA256.fullmatch(pause_sha):
        raise RuntimeError("backup manifest has an invalid PAUSE digest")
    expected_keys = {"path", "sha256", "size", "mode", "uid", "gid"}
    seen: set[str] = set()
    normalized: list[dict] = []
    files_root = snapshot / "files"
    if files_root.is_symlink() or not files_root.is_dir():
        raise RuntimeError("backup files directory is absent or a symlink")
    for record in manifest["files"]:
        if not isinstance(record, dict) or set(record) != expected_keys:
            raise RuntimeError("backup manifest file record has an invalid shape")
        relative = _managed_manifest_path(record.get("path"))
        if relative in seen:
            raise RuntimeError(f"duplicate manifest path: {relative}")
        seen.add(relative)
        sha256 = record.get("sha256")
        size = record.get("size")
        mode = record.get("mode")
        uid = record.get("uid")
        gid = record.get("gid")
        if not isinstance(sha256, str) or not MANIFEST_SHA256.fullmatch(sha256) \
                or isinstance(size, bool) or not isinstance(size, int) or size < 0 \
                or not isinstance(mode, str) or not MANIFEST_MODE.fullmatch(mode) \
                or isinstance(uid, bool) or not isinstance(uid, int) or uid < 0 \
                or isinstance(gid, bool) or not isinstance(gid, int) or gid < 0:
            raise RuntimeError(f"backup manifest record has invalid types: {relative}")
        source = _reject_symlink_components(files_root, relative, leaf_may_be_missing=False)
        if not source.is_file() or source.stat().st_size != size or digest(source) != sha256:
            raise RuntimeError(f"backup hash or size mismatch: {relative}")
        normalized.append(dict(record))
    pause = next((item for item in normalized if item["path"] == "state/PAUSE"), None)
    if pause is None or pause["sha256"] != pause_sha:
        raise RuntimeError("backup does not contain the declared state/PAUSE")
    manifest = dict(manifest)
    manifest["files"] = normalized
    return manifest


def _git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _write_snapshot_tree(root: Path, staging: Path) -> dict:
    pause = require_pause(root)
    if staging.exists():
        if staging.is_symlink() or not staging.is_dir() or any(staging.iterdir()):
            raise RuntimeError(f"snapshot staging is not a private empty directory: {staging}")
        staging.chmod(0o700)
    else:
        staging.mkdir(mode=0o700)
    records: list[dict] = []
    for source in collect_files(root):
        relative = source.relative_to(root)
        target = staging / "files" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        records.append({
            "path": relative.as_posix(), "sha256": digest(target),
            "size": target.stat().st_size, "mode": oct(target.stat().st_mode & 0o777),
            "uid": target.stat().st_uid, "gid": target.stat().st_gid,
        })
    manifest = {
        "schema_version": 1,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "commit": _git_commit(root), "pause_sha256": digest(pause), "files": records,
        "locks_observed": sorted(item.name for item in (root / "state/.locks").iterdir()),
    }
    atomic_bytes(staging / "manifest.json",
                 (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
    fsync_dir(staging)
    load_manifest(staging)
    return manifest


def _copy_snapshot(snapshot: Path, manifest: dict, target: Path) -> None:
    target.mkdir(mode=0o700)
    for record in manifest["files"]:
        relative = str(record["path"])
        source = _reject_symlink_components(snapshot / "files", relative,
                                             leaf_may_be_missing=False)
        destination = target / "files" / _native_relative(relative)
        atomic_bytes(destination, source.read_bytes(), int(record["mode"], 8))
    atomic_bytes(target / "manifest.json",
                 (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
    fsync_dir(target)
    load_manifest(target)


def _staging_identity(path: Path, prefix: str) -> tuple[int, str] | None:
    if not path.name.startswith(prefix):
        return None
    fields = path.name[len(prefix):].split(".", 2)
    if len(fields) != 3 or not fields[0].isdigit() or not fields[1].isdigit():
        return None
    return int(fields[0]), fields[1]


def _cleanup_backup_orphans(destination: Path) -> None:
    prefix = f".{destination.name}.tmp."
    for candidate in destination.parent.glob(prefix + "*"):
        identity = _staging_identity(candidate, prefix)
        if identity is None or not _owner_values_are_dead(*identity):
            continue
        tomb = destination.parent / f".{destination.name}.orphan.{os.getpid()}.{time.time_ns()}"
        try:
            _rename_noreplace(candidate, tomb)
        except (FileNotFoundError, FileExistsError):
            continue
        _safe_remove_tree(tomb)


def _witnessed_staging(parent: Path, prefix: str) -> Path:
    pid, start = _process_identity(os.getpid())
    return Path(tempfile.mkdtemp(prefix=f"{prefix}{pid}.{start}.", dir=parent))


def _transaction_path(root: Path) -> Path:
    return root / "state/.locks" / RESTORE_TRANSACTION


def _cleanup_completed_transactions(root: Path) -> None:
    lock_root = root / "state/.locks"
    candidate_prefix = f".{RESTORE_TRANSACTION}.candidate."
    for path in lock_root.glob(candidate_prefix + "*"):
        identity = _staging_identity(path, candidate_prefix)
        if identity is not None and _owner_values_are_dead(*identity):
            tomb = lock_root / f".{RESTORE_TRANSACTION}.candidate-dead.{os.getpid()}.{time.time_ns()}"
            try:
                _rename_noreplace(path, tomb)
            except (FileNotFoundError, FileExistsError):
                continue
            with contextlib.suppress(OSError, RuntimeError):
                _safe_remove_tree(tomb)
    for path in lock_root.glob(f".{RESTORE_TRANSACTION}.complete.*"):
        if path.is_dir() and not path.is_symlink():
            with contextlib.suppress(OSError, RuntimeError):
                _safe_remove_tree(path)


def _validate_restore_targets(root: Path, manifest: dict) -> None:
    collect_files(root)
    for record in manifest["files"]:
        target = _reject_symlink_components(root, str(record["path"]))
        resolved_parent = target.parent.resolve(strict=False)
        if root.resolve() not in (resolved_parent, *resolved_parent.parents):
            raise RuntimeError(f"restore target escapes checkout: {record['path']}")


def _create_restore_transaction(root: Path, snapshot: Path, manifest: dict) -> Path:
    transaction = _transaction_path(root)
    if transaction.exists() or transaction.is_symlink():
        raise RuntimeError("an unresolved runtime restore transaction already exists")
    lock_root = transaction.parent
    candidate = _witnessed_staging(
        lock_root, f".{RESTORE_TRANSACTION}.candidate."
    )
    try:
        preimage = candidate / "preimage"
        desired = candidate / "desired"
        preimage_manifest = _write_snapshot_tree(root, preimage)
        _copy_snapshot(snapshot, manifest, desired)
        metadata = {
            "schema_version": 1, "kind": "runtime-restore", "status": "prepared",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": str(snapshot.resolve()),
            "desired_manifest_sha256": digest(desired / "manifest.json"),
            "preimage_manifest_sha256": digest(preimage / "manifest.json"),
            "desired_files": len(manifest["files"]),
            "preimage_files": len(preimage_manifest["files"]),
        }
        atomic_bytes(candidate / "transaction.json",
                     (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode())
        fsync_dir(candidate)
        _rename_noreplace(candidate, transaction)
        fsync_dir(lock_root)
        return transaction
    except BaseException:
        if candidate.exists():
            with contextlib.suppress(OSError, RuntimeError):
                _safe_remove_tree(candidate)
        raise


def _restore_crash_boundary(boundary: int) -> None:
    raw = os.environ.get("RECURSION_RESTORE_CRASH_AFTER")
    if raw is not None and int(raw) == boundary:
        os._exit(92)


def _verify_exact_inventory(root: Path, manifest: dict) -> None:
    expected = {str(record["path"]): record for record in manifest["files"]}
    observed = {path.relative_to(root).as_posix(): path for path in collect_files(root)}
    if set(observed) != set(expected):
        extra = sorted(set(observed) - set(expected))
        missing = sorted(set(expected) - set(observed))
        detail = extra[0] if extra else missing[0] if missing else "unknown"
        raise RuntimeError(f"restored runtime inventory is not exact: {detail}")
    for relative, record in expected.items():
        path = observed[relative]
        stat_result = path.stat()
        if stat_result.st_size != record["size"] or digest(path) != record["sha256"] \
                or oct(stat_result.st_mode & 0o777) != record["mode"]:
            raise RuntimeError(f"restored runtime file differs from manifest: {relative}")
        if hasattr(os, "geteuid") and os.geteuid() == 0 \
                and (stat_result.st_uid != record["uid"] or stat_result.st_gid != record["gid"]):
            raise RuntimeError(f"restored runtime ownership differs from manifest: {relative}")


def _apply_exact_snapshot(root: Path, snapshot: Path, manifest: dict) -> None:
    _validate_restore_targets(root, manifest)
    boundary = 0
    _restore_crash_boundary(boundary)
    ordered = sorted(manifest["files"], key=lambda item: item["path"] != "state/PAUSE")
    desired = {str(record["path"]) for record in ordered}
    for record in ordered:
        relative = str(record["path"])
        source = _reject_symlink_components(snapshot / "files", relative,
                                             leaf_may_be_missing=False)
        target = _reject_symlink_components(root, relative)
        atomic_bytes(target, source.read_bytes(), int(record["mode"], 8))
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            os.chown(target, int(record["uid"]), int(record["gid"]))
        boundary += 1
        _restore_crash_boundary(boundary)
    for current in collect_files(root):
        relative = current.relative_to(root).as_posix()
        if relative in desired:
            continue
        current.unlink()
        fsync_dir(current.parent)
        boundary += 1
        _restore_crash_boundary(boundary)
    require_pause(root)
    _verify_exact_inventory(root, manifest)
    boundary += 1
    _restore_crash_boundary(boundary)


def _finish_restore_transaction(root: Path, transaction: Path) -> None:
    tomb = transaction.with_name(
        f".{RESTORE_TRANSACTION}.complete.{os.getpid()}.{time.time_ns()}"
    )
    _rename_noreplace(transaction, tomb)
    fsync_dir(transaction.parent)
    with contextlib.suppress(OSError, RuntimeError):
        _safe_remove_tree(tomb)


def resolve_open_restore(root: Path) -> str | None:
    transaction = _transaction_path(root)
    _cleanup_completed_transactions(root)
    if not transaction.exists() and not transaction.is_symlink():
        return None
    if transaction.is_symlink() or not transaction.is_dir():
        raise RuntimeError("runtime restore transaction marker has an unsafe type")
    metadata_path = transaction / "transaction.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("runtime restore transaction metadata is unreadable") from exc
    if not isinstance(metadata, dict) or metadata.get("schema_version") != 1 \
            or metadata.get("kind") != "runtime-restore" or metadata.get("status") != "prepared":
        raise RuntimeError("runtime restore transaction metadata is malformed")
    desired = transaction / "desired"
    preimage = transaction / "preimage"
    try:
        manifest = load_manifest(desired)
        if digest(desired / "manifest.json") != metadata.get("desired_manifest_sha256"):
            raise RuntimeError("runtime restore desired manifest changed after preparation")
        _apply_exact_snapshot(root, desired, manifest)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as desired_error:
        try:
            rollback = load_manifest(preimage)
            if digest(preimage / "manifest.json") != metadata.get("preimage_manifest_sha256"):
                raise RuntimeError("runtime restore preimage manifest changed after preparation")
            _apply_exact_snapshot(root, preimage, rollback)
            _finish_restore_transaction(root, transaction)
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as rollback_error:
            raise RuntimeError(
                f"runtime restore and preimage rollback both failed: restore={desired_error}; "
                f"rollback={rollback_error}"
            ) from rollback_error
        raise RuntimeError(f"runtime restore rolled back to its durable preimage: {desired_error}")
    _finish_restore_transaction(root, transaction)
    return "restored"


def backup(root: Path, destination: Path) -> None:
    require_pause(root)
    ensure_outside_root(root, destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    _cleanup_backup_orphans(destination)
    if destination.exists() or destination.is_symlink():
        raise RuntimeError(f"backup destination already exists: {destination}")
    staging: Path | None = None
    manifest: dict | None = None
    with RuntimeLock(root), EmptyLock(root / "state/.locks/taskctl.lock"), DecisionQueueLock(root):
        require_pause(root); assert_no_execution_locks(root)
        resolve_open_restore(root)
        reconcile_transition_receipts(root)
        staging = _witnessed_staging(destination.parent, f".{destination.name}.tmp.")
        try:
            manifest = _write_snapshot_tree(root, staging)
            _rename_noreplace(staging, destination)
            staging = None
            fsync_dir(destination.parent)
        finally:
            if staging is not None and staging.exists():
                _safe_remove_tree(staging)
    assert manifest is not None
    print(f"backup {destination} files={len(manifest['files'])} "
          f"pause_sha256={manifest['pause_sha256']}")


def restore(root: Path, snapshot: Path) -> None:
    require_pause(root)
    ensure_outside_root(root, snapshot)
    manifest = load_manifest(snapshot)
    _validate_restore_targets(root, manifest)
    with RuntimeLock(root), EmptyLock(root / "state/.locks/taskctl.lock"), DecisionQueueLock(root):
        require_pause(root); assert_no_execution_locks(root)
        resolve_open_restore(root)
        reconcile_transition_receipts(root)
        _create_restore_transaction(root, snapshot, manifest)
        resolve_open_restore(root)
        require_pause(root)
    print(f"restore {snapshot} files={len(manifest['files'])} "
          f"pause_sha256={manifest['pause_sha256']}")


def _operator_lock_path(root: Path, raw: Path) -> Path:
    path = raw if raw.is_absolute() else root / raw
    lock_root = (root / "state/.locks").resolve()
    supported = re.fullmatch(
        r"(?:taskctl|ledger|heavy-gate)\.lock|(?:project|planner|action)-[A-Za-z0-9._-]+\.lock|"
        r"wt-[0-9a-f]{12}\.lock",
        path.name,
    )
    if path.parent.resolve() != lock_root or supported is None:
        raise RuntimeError(f"operator lock path is outside the supported lock namespace: {raw}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    rotate = subparsers.add_parser("rotate-events")
    rotate.add_argument("--max-bytes", type=int, default=10 * 1024 * 1024)
    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("destination", type=Path)
    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("snapshot", type=Path)
    lock_acquire = subparsers.add_parser("lock-acquire")
    lock_acquire.add_argument("path", type=Path)
    lock_acquire.add_argument("owner_pid", type=int)
    lock_release = subparsers.add_parser("lock-release")
    lock_release.add_argument("path", type=Path)
    lock_release.add_argument("owner_pid", type=int)
    args = parser.parse_args()
    root = Path(os.environ.get("RECURSION_ROOT", Path(__file__).resolve().parents[1])).resolve()
    try:
        if args.command == "rotate-events":
            rotate_events(root, args.max_bytes)
        elif args.command == "backup":
            backup(root, args.destination)
        elif args.command == "restore":
            restore(root, args.snapshot)
        elif args.command == "lock-acquire":
            path = _operator_lock_path(root, args.path)
            acquire_witnessed_directory_lock(path, path.name, args.owner_pid)
        else:
            path = _operator_lock_path(root, args.path)
            release_witnessed_directory_lock(path, path.name, args.owner_pid)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"runtime-state: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

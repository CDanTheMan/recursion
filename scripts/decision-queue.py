#!/usr/bin/env python3
"""Durable, schema-checked queue for Head Hermes decisions.

The append-only ``state/decisions.jsonl`` journal remains the recovery source.  Individual
decision projections move through pending/running/succeeded/failed directories so an actuator
restart never depends on a singleton "latest" pointer.  The Phase 2 action journal remains the
authoritative record of whether actuation actually ran.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import ctypes
import hashlib
import json
import os
import re
import subprocess
import stat
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

if os.name == "nt":
    import msvcrt
    from ctypes import wintypes
    _KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _CREATE_FILE_W = _KERNEL32.CreateFileW
    _CREATE_FILE_W.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                               wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    _CREATE_FILE_W.restype = wintypes.HANDLE
    _CLOSE_HANDLE = _KERNEL32.CloseHandle
    _CLOSE_HANDLE.argtypes = [wintypes.HANDLE]
    _CLOSE_HANDLE.restype = wintypes.BOOL
    _SET_FILE_INFORMATION_BY_HANDLE = _KERNEL32.SetFileInformationByHandle
    _SET_FILE_INFORMATION_BY_HANDLE.argtypes = [wintypes.HANDLE, wintypes.INT,
                                                wintypes.LPVOID, wintypes.DWORD]
    _SET_FILE_INFORMATION_BY_HANDLE.restype = wintypes.BOOL

try:
    import fcntl
except ImportError:  # pragma: no cover - production is Linux; parser tests run on Windows.
    fcntl = None  # type: ignore[assignment]

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from jsonl_durable import (
    JsonlDurabilityError, acknowledge_jsonl, append_jsonl as durable_append_jsonl,
    find_jsonl_objects, read_jsonl_prefix, read_jsonl_since,
)


IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
TERMINAL_DIRS = ("succeeded", "failed")
QUEUE_DIRS = ("pending", "running", *TERMINAL_DIRS)
MAX_QUEUE_JSON_BYTES = 2 * 1024 * 1024
MAX_QUEUE_JOURNAL_BYTES = 64 * 1024 * 1024
LEGACY_PRE_SCHEMA_NOOP_SHA256 = (
    # One-time Phase 8 compatibility allowlist. These are the exact immutable line digests
    # captured from the five 2026-08-07 pre-schema PAUSE noops. Adding any digest is a reviewed
    # code change; shape matching alone never turns an invalid current record into legacy state.
    "d589999830dbae9f212aaefaa95dab3562e89654c799426799f6ce71e3afe081",
    "726c5d82795ee7b42def62b2601f36d0662cb0f5de6f5e4886b11b77f597cc8a",
    "3bd740a2f8242645af25a01dda28f3db636d8e67fb066db1c6c39e793fb6d7ee",
    "160cee2fed8ead1e0154bb3635cb19588a3ad312fb4ae4c5501a3b9da4e7784b",
    "6c14cb6556f79e81bc3b1b4a0a4cb3c14593cb22902e7170410c990372678dda",
)
LEGACY_PRE_SCHEMA_NOOP_KEYS = frozenset({
    "args", "confidence", "cost_usd", "goal", "project", "provider", "text", "ts",
    "verb", "why", "wrong_if",
})
LEGACY_PRE_PROVENANCE_NOOP_SHA256 = (
    # Second reviewed compatibility entry, same rule as the block above: an exact immutable
    # line digest, never a shape match. This 2026-08-09 record carries schema_version 1 and
    # a normalized id, so it clears the pre-schema quarantine, but it predates the
    # decision_source/routed_decider provenance model. normalize() can recompute its payload
    # digest; it cannot invent an authority, and forging one is exactly what the provenance
    # check exists to prevent. The record is a noop that can never actuate, so it is
    # recorded and never replayed.
    "17e365c897961b6699ffc868b42e9ba469a1c6b5797798686224d6a4bb73165b",
)
LEGACY_REVIEWED_NOOP_SHA256 = LEGACY_PRE_SCHEMA_NOOP_SHA256 + LEGACY_PRE_PROVENANCE_NOOP_SHA256
# A journal may hold the pre-schema block alone, or that block followed by the
# pre-provenance record. Nothing else is a reviewed set: comparing against an arbitrary
# PREFIX would silently accept a truncated migration, which is the failure
# hermes-pilot-phase8-legacy-journal-red::test_incomplete_prefix exists to catch.
COMPLETE_REVIEWED_NOOP_PREFIXES = (
    LEGACY_PRE_SCHEMA_NOOP_SHA256,
    LEGACY_REVIEWED_NOOP_SHA256,
)
LEGACY_PRE_PROVENANCE_NOOP_KEYS = frozenset({
    "actor", "args", "arguments", "confidence", "cost_usd", "goal", "goal_id", "id",
    "idempotency_key", "project", "provider", "reason", "schema_version", "status", "ts",
    "usage", "verb", "why", "wrong_if",
})


def root() -> Path:
    return Path(os.environ.get("RECURSION_ROOT") or Path(__file__).resolve().parent.parent)


def queue_root(base: Path) -> Path:
    return base / "state/decision-queue"


def fsync_dir(path: Path) -> None:
    if os.name == "nt":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise RuntimeError(f"queue path is unreadable: {path}") from exc
    return _is_reparse_info(info)


def _is_reparse_info(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0)) \
        or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _reject_reparse_components(path: Path, label: str) -> None:
    if not isinstance(path, Path) or not path.is_absolute() \
            or any(part in {".", ".."} for part in path.parts):
        raise RuntimeError(f"{label} must be a canonical absolute path")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise RuntimeError(f"{label} is unreadable") from exc
        if stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0)) \
                or bool(getattr(info, "st_file_attributes", 0) & 0x400):
            raise RuntimeError(f"{label} contains a symlink/reparse component")


def _path_identity(path: Path, label: str) -> tuple[int, int, int, int]:
    _reject_reparse_components(path, label)
    try:
        info = path.lstat()
    except OSError as exc:
        raise ValueError(f"{label} is unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0)) \
            or bool(getattr(info, "st_file_attributes", 0) & 0x400) \
            or not stat.S_ISREG(info.st_mode):
        raise ValueError(f"{label} is not a regular file")
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _open_pinned(path: Path, *, directory: bool = False, delete_access: bool = False) -> int:
    """Open without following reparse points and deny other processes delete-sharing."""
    if os.name != "nt":
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        if directory:
            flags |= getattr(os, "O_DIRECTORY", 0)
        return os.open(path, flags)
    access = 0x80000000 | (0x00010000 if delete_access else 0)  # GENERIC_READ | DELETE
    share = 0x00000001 | 0x00000002  # FILE_SHARE_READ | FILE_SHARE_WRITE
    flags = 0x00200000 | (0x02000000 if directory else 0)  # OPEN_REPARSE_POINT/BACKUP_SEMANTICS
    handle = _CREATE_FILE_W(str(path), access, share, None, 3, flags, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except OSError:
        _CLOSE_HANDLE(handle)
        raise


@contextlib.contextmanager
def _pin_directory_chain(path: Path, label: str):
    handles: list[int] = []
    current = Path(path.anchor)
    try:
        for component in path.parts[1:]:
            current /= component
            info = current.lstat()
            if _is_reparse_info(info) or not stat.S_ISDIR(info.st_mode):
                raise ValueError(f"{label} is unsafe")
            descriptor = _open_pinned(current, directory=True)
            try:
                opened = os.fstat(descriptor)
                if _is_reparse_info(opened) or not stat.S_ISDIR(opened.st_mode) \
                        or (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                    raise ValueError(f"{label} changed while opening")
            except BaseException:
                os.close(descriptor)
                raise
            handles.append(descriptor)
        yield
    except (FileNotFoundError, OSError) as exc:
        raise ValueError(f"{label} is unavailable") from exc
    finally:
        for descriptor in reversed(handles):
            try:
                os.close(descriptor)
            except OSError:
                pass


@contextlib.contextmanager
def _pinned_file(path: Path, label: str, *, delete_access: bool = False):
    _reject_reparse_components(path, label)
    with _pin_directory_chain(path.parent, f"{label} parent"):
        try:
            expected = path.lstat()
        except OSError as exc:
            raise ValueError(f"{label} is unavailable") from exc
        if _is_reparse_info(expected) or not stat.S_ISREG(expected.st_mode):
            raise ValueError(f"{label} is not a regular file")
        descriptor = _open_pinned(path, delete_access=delete_access)
        try:
            opened = os.fstat(descriptor)
            if _is_reparse_info(opened) or not stat.S_ISREG(opened.st_mode) \
                    or (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino) \
                    or opened.st_size != expected.st_size:
                raise ValueError(f"{label} changed while opening")
            yield descriptor, opened
        finally:
            try:
                os.close(descriptor)
            except OSError:
                pass


def _read_pinned(descriptor: int, maximum: int, label: str) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while total <= maximum:
        chunk = os.read(descriptor, min(1024 * 1024, maximum + 1 - total))
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        total += len(chunk)
    raise ValueError(f"{label} exceeds the bounded JSON input size")


def _delete_pinned(descriptor: int, path: Path) -> None:
    if os.name != "nt":
        path.unlink()
        return
    class _FileDispositionInfo(ctypes.Structure):
        _fields_ = [("DeleteFile", wintypes.BOOLEAN)]
    disposition = _FileDispositionInfo(True)
    if not _SET_FILE_INFORMATION_BY_HANDLE(
            msvcrt.get_osfhandle(descriptor), 4, ctypes.byref(disposition), ctypes.sizeof(disposition)):
        raise ctypes.WinError(ctypes.get_last_error())


def _load_json_bytes(raw: bytes, label: str) -> object:
    if len(raw) > MAX_QUEUE_JSON_BYTES:
        raise ValueError(f"{label} exceeds the bounded JSON input size")
    try:
        return json.loads(raw.decode("utf-8", "strict"), parse_constant=lambda name: (
            (_ for _ in ()).throw(ValueError(f"non-finite JSON number {name} is forbidden"))))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError, OverflowError,
            RecursionError) as exc:
        raise ValueError(f"{label} is invalid JSON") from exc


def _read_json_path_bytes(path: Path, label: str) -> bytes:
    try:
        with _pinned_file(path, label) as (descriptor, info):
            if info.st_size > MAX_QUEUE_JSON_BYTES:
                raise ValueError(f"{label} exceeds the bounded JSON input size")
            raw = _read_pinned(descriptor, MAX_QUEUE_JSON_BYTES, label)
            if len(raw) > MAX_QUEUE_JSON_BYTES:
                raise ValueError(f"{label} exceeds the bounded JSON input size")
            return raw
    except (OSError, ValueError, TypeError) as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError(f"{label} is unreadable") from exc


def _load_json_path(path: Path, label: str) -> object:
    return _load_json_bytes(_read_json_path_bytes(path, label), label)


def ensure_directory(path: Path) -> None:
    _reject_reparse_components(path, "queue directory")
    missing: list[Path] = []
    current = path
    while True:
        try:
            info = current.lstat()
        except FileNotFoundError:
            info = None
        except OSError as exc:
            raise RuntimeError(f"queue directory is unreadable: {current}") from exc
        if info is not None:
            if stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0)) \
                    or bool(getattr(info, "st_file_attributes", 0) & 0x400) \
                    or not stat.S_ISDIR(info.st_mode):
                raise RuntimeError(f"queue directory has an unsafe type: {current}")
            break
        missing.append(current)
        if current.parent == current:
            break
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    _reject_reparse_components(path, "queue directory")
    for created in reversed(missing):
        fsync_dir(created)
        fsync_dir(created.parent)


def atomic_json(path: Path, value: dict) -> None:
    ensure_directory(path.parent)
    _reject_reparse_components(path, "queue JSON target")
    try:
        encoded = (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeError) as exc:
        raise ValueError("queue record is not canonically JSON serializable") from exc
    if len(encoded) > MAX_QUEUE_JSON_BYTES:
        raise ValueError("queue record exceeds the bounded JSON input size")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            out.write(encoded.decode("utf-8"))
            out.flush()
            os.fsync(out.fileno())
        _reject_reparse_components(path.parent, "queue JSON parent")
        _reject_reparse_components(path, "queue JSON target")
        os.replace(tmp, path)
        fsync_dir(path.parent)
    except BaseException:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise


def atomic_bytes(path: Path, value: bytes) -> None:
    if not isinstance(value, bytes):
        raise ValueError("queue byte payload is invalid")
    ensure_directory(path.parent)
    _reject_reparse_components(path, "queue byte target")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(value)
            out.flush()
            os.fsync(out.fileno())
        _reject_reparse_components(path.parent, "queue byte parent")
        _reject_reparse_components(path, "queue byte target")
        os.replace(tmp, path)
        fsync_dir(path.parent)
    except BaseException:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise


def write_all(fd: int, value: bytes) -> None:
    view = memoryview(value)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("short append-only journal write")
        view = view[written:]


@contextmanager
def queue_lock(base: Path):
    if fcntl is None:
        raise RuntimeError("decision queue locking is unavailable on this platform")
    lock_dir = base / "state/.locks"
    ensure_directory(lock_dir)
    lock_path = lock_dir / "decision-queue.lock"
    _reject_reparse_components(lock_path, "decision queue lock")
    try:
        expected = lock_path.lstat()
    except FileNotFoundError:
        expected = None
    except OSError as exc:
        raise RuntimeError("decision queue lock is unreadable") from exc
    if expected is not None and (_is_reparse(lock_path) or not stat.S_ISREG(expected.st_mode)):
        raise RuntimeError("decision queue lock has an unsafe type")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = -1
    try:
        descriptor = os.open(lock_path, flags, 0o600)
        opened = os.fstat(descriptor)
        observed = lock_path.lstat()
        if _is_reparse_info(observed) or not stat.S_ISREG(opened.st_mode) \
                or (opened.st_dev, opened.st_ino) != (observed.st_dev, observed.st_ino) \
                or (expected is not None and
                    (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino)):
            raise RuntimeError("decision queue lock changed while opening")
        with os.fdopen(descriptor, "a+", encoding="utf-8") as lock:
            descriptor = -1
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RuntimeError("decision queue lock is contended; refusing an unlocked mutation") from exc
            yield
    except (OSError, ValueError, TypeError) as exc:
        raise RuntimeError("decision queue lock is unavailable") from exc
    finally:
        if descriptor != -1:
            try:
                os.close(descriptor)
            except OSError:
                pass


def digest(value: object) -> str:
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeError) as exc:
        raise ValueError("decision value is not canonically JSON serializable") from exc
    return hashlib.sha256(raw).hexdigest()


def decision_payload_digest(record: dict) -> str:
    """Bind an identity to every authority/effect-bearing decision field.

    Queue status, timestamps, provider accounting, and explanatory prose do not change what the
    actuator is allowed to do.  Everything that can change authority or the resulting effect is
    frozen here so an existing same-id projection cannot be reused with different content.
    """
    payload = {
        "actor": record.get("actor") or "",
        "verb": record.get("verb") or "",
        "args": record.get("args", record.get("arguments", [])) or [],
        "text": record.get("text") or "",
        "plan": record.get("plan") or None,
        "instruction_id": record.get("instruction_id") or None,
        "project": record.get("project") or "",
        "goal": record.get("goal", record.get("goal_id", "")) or "",
        "decision_source": record.get("decision_source") or "",
        "routed_decider": record.get("routed_decider") or "",
    }
    return digest(payload)


def assert_same_decision(existing: dict, incoming: dict, where: str) -> None:
    existing_digest = decision_payload_digest(existing)
    incoming_digest = decision_payload_digest(incoming)
    if existing.get("decision_payload_sha256") not in {None, existing_digest}:
        raise ValueError(f"stored decision authority/effect digest is inconsistent: {where}")
    if incoming.get("decision_payload_sha256") not in {None, incoming_digest}:
        raise ValueError(f"incoming decision authority/effect digest is inconsistent: {where}")
    if existing_digest != incoming_digest:
        raise ValueError(f"decision id collision with different authority/effect payload: {where}")


def normalize(raw: dict, stamp: str | None = None, provider: str | None = None,
              usage: dict | None = None) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("decision must be a JSON object")
    if "schema_version" in raw and (type(raw["schema_version"]) is not int
                                     or raw["schema_version"] != 1):
        raise ValueError("decision schema_version must be the integer 1")
    args = raw.get("args", raw.get("arguments", [])) or []
    verb = raw.get("verb", "")
    goal = raw.get("goal", raw.get("goal_id", ""))
    why = raw.get("why", raw.get("reason", ""))
    identity_payload = {
        "verb": verb,
        "args": args,
        "text": raw.get("text", "") or "",
        "plan": raw.get("plan") or None,
        "goal": goal,
        "instruction_id": raw.get("instruction_id") or None,
        "wrong_if": raw.get("wrong_if", ""),
    }
    key = raw.get("idempotency_key") or f"decision:{digest(identity_payload)}"
    decision_id = raw.get("id") or f"decision-{digest(key)[:24]}"
    if not IDENTIFIER.fullmatch(str(decision_id)):
        decision_id = f"decision-{digest(str(decision_id))[:24]}"
    record = dict(raw)
    record.update(
        {
            "schema_version": 1,
            "id": decision_id,
            "actor": raw.get("actor") or "head-hermes",
            "verb": verb,
            "arguments": args,
            "args": args,
            "reason": why,
            "why": why,
            "goal_id": goal,
            "goal": goal,
            "idempotency_key": key,
            "status": "queued",
        }
    )
    record["decision_payload_sha256"] = decision_payload_digest(record)
    if stamp:
        record["ts"] = stamp
    if provider:
        record["provider"] = provider
    if usage is not None:
        record["usage"] = usage
        record["cost_usd"] = usage.get("estimated_cost_usd")
    return record


def validate_record(base: Path, record: dict) -> None:
    validator = base / "scripts/validate-control-state.py"
    try:
        payload = json.dumps(record, allow_nan=False)
        proc = subprocess.run(
            [sys.executable, str(validator), "decision"],
            input=payload,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeError) as exc:
        raise ValueError("decision cannot be serialized for validation") from exc
    except (OSError, subprocess.TimeoutExpired, subprocess.SubprocessError) as exc:
        raise ValueError("decision schema validation was unavailable") from exc
    if proc.returncode:
        raise ValueError("decision schema validation failed")


def existing_path(base: Path, decision_id: str) -> Path | None:
    for state in QUEUE_DIRS:
        candidate = queue_root(base) / state / f"{decision_id}.json"
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ValueError(f"queue projection is unreadable: {candidate}") from exc
        if stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0)) \
                or bool(getattr(info, "st_file_attributes", 0) & 0x400):
            raise ValueError(f"queue projection is a symlink/reparse path: {candidate}")
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f"queue projection has an unsafe type: {candidate}")
        if info.st_size > MAX_QUEUE_JSON_BYTES:
            raise ValueError(f"queue projection is too large: {candidate}")
        if stat.S_ISREG(info.st_mode):
            return candidate
    return None


def validate_committed_journal_objects(data: bytes) -> list[dict]:
    """Fail closed on any complete non-object JSONL row without rewriting legacy objects."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"decision journal is not UTF-8: {exc}") from exc
    values: list[dict] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = _load_json_bytes(line.encode("utf-8"), f"decision journal line {number}")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError, RecursionError) as exc:
            raise ValueError(f"invalid decision journal line {number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"invalid decision journal line {number}: JSON object required")
        values.append(value)
    return values


def append_journal(base: Path, record: dict) -> bool:
    # enqueue() owns decision-queue.lock across this repair/validate/append boundary. Preserve the
    # exact reviewed legacy object rows: only an unterminated tail is removed, and complete rows
    # are inspected without normalization or rewriting.
    journal = base / "state/decisions.jsonl"
    ensure_directory(journal.parent)
    try:
        journal_info = journal.lstat()
    except FileNotFoundError:
        journal_info = None
    except OSError as exc:
        raise ValueError("decision journal is unreadable") from exc
    if journal_info is not None:
        if _is_reparse(journal) or not stat.S_ISREG(journal_info.st_mode):
            raise ValueError("decision journal has an unsafe type")
        repair_decision_journal_tail(base, journal)
    try:
        matches = find_jsonl_objects(journal, "id", record.get("id"))
    except JsonlDurabilityError as exc:
        raise ValueError(str(exc)) from exc
    if matches:
        for existing in matches:
            assert_same_decision(existing, record, f"journal decision {record.get('id')}")
        # A prior process may have died after fsync(journal) but before projection. Re-durabilize
        # the directory entry, reuse the semantic row, and let enqueue create the projection once.
        fsync_dir(journal.parent)
        return False
    try:
        outcome = durable_append_jsonl(journal, record, dedupe_field="id",
                                       dedupe_value=record.get("id"))
    except JsonlDurabilityError as exc:
        raise ValueError(str(exc)) from exc
    # Retain decision-queue's observable directory durability boundary even though the shared
    # append helper also persists a newly created journal entry.
    fsync_dir(journal.parent)
    return outcome.appended


def reviewed_legacy_marker(raw: dict, line: str, number: int, record: dict) -> dict | None:
    """Return a non-executable marker only for an exact reviewed pre-schema PAUSE noop."""
    source_sha256 = hashlib.sha256(line.encode()).hexdigest()
    if source_sha256 in LEGACY_PRE_PROVENANCE_NOOP_SHA256:
        # Post-schema, pre-provenance. Requiring the provenance fields to be ABSENT is what
        # keeps this from ever matching a record that merely carries a WRONG authority: such
        # a record must keep failing closed, not become legacy state.
        if (
            set(raw) != LEGACY_PRE_PROVENANCE_NOOP_KEYS
            or raw.get("verb") != "noop"
            or raw.get("args") != []
            or raw.get("arguments") != []
            or raw.get("actor") != "head-hermes"
            or type(raw.get("schema_version")) is not int
            or raw.get("schema_version") != 1
            or raw.get("provider") != "openai-codex"
            or raw.get("project") != "recursion"
            or raw.get("decision_source") is not None
            or raw.get("routed_decider") is not None
            or not all(
                isinstance(raw.get(field), str) and raw[field]
                for field in ("goal", "goal_id", "id", "ts", "why", "wrong_if")
            )
        ):
            return None
        classification = "reviewed-pre-provenance-noop"
        disposition_reason = (
            "reviewed historical PAUSE noop predates the decision-provenance model and must"
            " not be replayed"
        )
    elif source_sha256 in LEGACY_PRE_SCHEMA_NOOP_SHA256:
        if (
            set(raw) != LEGACY_PRE_SCHEMA_NOOP_KEYS
            or raw.get("verb") != "noop"
            or raw.get("args") != []
            or raw.get("confidence") != "high"
            or raw.get("cost_usd") != "0.0"
            or raw.get("provider") != "openai-codex"
            or raw.get("text") != ""
            or raw.get("project") not in {"recursion", "gsc"}
            or not all(isinstance(raw.get(field), str) and raw[field] for field in ("goal", "ts", "why", "wrong_if"))
        ):
            return None
        classification = "reviewed-pre-schema-noop"
        disposition_reason = "reviewed historical PAUSE noop predates schema-v1 and must not be replayed"
    else:
        return None
    marker_id = f"legacy-decision-{source_sha256[:24]}"
    return {
        "schema_version": 1,
        "id": marker_id,
        "source": "state/decisions.jsonl",
        "source_line": number,
        "source_sha256": source_sha256,
        "source_goal_sha256": hashlib.sha256(raw["goal"].encode()).hexdigest(),
        "normalized_decision_id": record["id"],
        "project": raw["project"],
        "verb": "noop",
        "classification": classification,
        "disposition": "not-enqueued",
        "reason": disposition_reason,
    }


def legacy_marker_path(base: Path, marker: dict) -> Path:
    return queue_root(base) / "legacy" / f"{marker['id']}.json"


def enqueue(base: Path, record: dict, journal: bool) -> Path:
    validate_record(base, record)
    with queue_lock(base):
        present = existing_path(base, record["id"])
        if present:
            try:
                existing = _load_json_path(present, "existing decision projection")
            except (OSError, ValueError, TypeError, UnicodeError, RecursionError) as exc:
                raise ValueError(f"existing decision projection is unreadable: {present}") from exc
            assert_same_decision(existing, record, str(present))
            return present
        if journal:
            # Journal first: if the process dies before the projection rename, import-journal
            # reconstructs it.  The reverse ordering could lose the only recovery record.
            append_journal(base, record)
        target = queue_root(base) / "pending" / f"{record['id']}.json"
        atomic_json(target, record)
        return target


def quarantine_torn_tail(base: Path, journal: Path, data: bytes) -> bytes:
    """Preserve and remove only an unterminated final write; committed corruption still fails."""
    if not data or data.endswith(b"\n"):
        return data
    offset = data.rfind(b"\n") + 1
    committed, tail = data[:offset], data[offset:]
    tail_sha = hashlib.sha256(tail).hexdigest()
    before_sha = hashlib.sha256(data).hexdigest()
    quarantine = queue_root(base) / "quarantine"
    payload = quarantine / f"decision-journal-tail-{tail_sha[:24]}.bin"
    metadata_path = quarantine / f"decision-journal-tail-{tail_sha[:24]}.json"
    metadata = {
        "schema_version": 1,
        "source": "state/decisions.jsonl",
        "classification": "unterminated-final-write",
        "disposition": "quarantined-before-journal-truncate",
        "journal_sha256_before": before_sha,
        "journal_offset": offset,
        "tail_bytes": len(tail),
        "tail_sha256": tail_sha,
        "payload": payload.relative_to(base).as_posix(),
    }
    try:
        payload_info = payload.lstat()
    except FileNotFoundError:
        payload_info = None
    except OSError as exc:
        raise ValueError(f"torn-tail quarantine payload is unreadable: {payload.name}") from exc
    if payload_info is not None:
        if _is_reparse(payload) or not stat.S_ISREG(payload_info.st_mode) \
                or payload.read_bytes() != tail:
            raise ValueError(f"torn-tail quarantine payload mismatch: {payload.name}")
    else:
        atomic_bytes(payload, tail)
    try:
        metadata_info = metadata_path.lstat()
    except FileNotFoundError:
        metadata_info = None
    except OSError as exc:
        raise ValueError(f"torn-tail quarantine metadata is unreadable: {metadata_path.name}") from exc
    if metadata_info is not None:
        try:
            observed = _load_json_path(metadata_path, "torn-tail quarantine metadata")
        except (OSError, ValueError, TypeError, UnicodeError, RecursionError) as exc:
            raise ValueError(f"invalid torn-tail quarantine metadata: {metadata_path.name}") from exc
        if observed != metadata:
            raise ValueError(f"torn-tail quarantine metadata mismatch: {metadata_path.name}")
    else:
        atomic_json(metadata_path, metadata)
    with journal.open("r+b") as source:
        source.truncate(offset)
        source.flush()
        os.fsync(source.fileno())
    fsync_dir(journal.parent)
    print(
        f"decision-queue: quarantined unterminated final journal write "
        f"sha256={tail_sha} bytes={len(tail)}",
        file=sys.stderr,
    )
    return committed


def repair_decision_journal_tail(base: Path, journal: Path) -> None:
    """Inspect one byte in the steady state; copy the journal only for a torn tail."""
    try:
        journal_info = journal.lstat()
    except FileNotFoundError:
        return
    except OSError as exc:
        raise ValueError("decision journal is unreadable") from exc
    if _is_reparse(journal) or not stat.S_ISREG(journal_info.st_mode):
        raise ValueError("decision journal has an unsafe type")
    with journal.open("rb") as source:
        source.seek(0, os.SEEK_END)
        size = source.tell()
        if not size:
            return
        source.seek(-1, os.SEEK_END)
        if source.read(1) == b"\n":
            return
    with journal.open("rb") as source:
        data = source.read(MAX_QUEUE_JOURNAL_BYTES + 1)
    if len(data) > MAX_QUEUE_JOURNAL_BYTES:
        raise ValueError("decision journal exceeds the bounded input size")
    quarantine_torn_tail(base, journal, data)


def _line_text(raw: bytes) -> str:
    payload = raw[:-1] if raw.endswith(b"\n") else raw
    if payload.endswith(b"\r"):
        payload = payload[:-1]
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"decision journal is not UTF-8: {exc}") from exc


def _expected_legacy_markers(base: Path, journal: Path) -> dict[Path, dict]:
    """Revalidate the permanently bounded reviewed compatibility prefix."""
    markers: list[dict] = []
    for line in read_jsonl_prefix(journal, len(LEGACY_REVIEWED_NOOP_SHA256) + 1):
        if line.value is None:
            continue
        raw = line.value
        record = normalize(raw)
        try:
            validate_record(base, record)
        except ValueError as exc:
            marker = reviewed_legacy_marker(raw, _line_text(line.raw), line.sequence, record)
            if marker is None:
                raise ValueError(f"invalid decision journal line {line.sequence}: {exc}") from exc
            markers.append(marker)
            continue
        break
    digests = tuple(marker["source_sha256"] for marker in markers)
    if digests and digests not in COMPLETE_REVIEWED_NOOP_PREFIXES:
        raise ValueError("reviewed legacy decision prefix is incomplete or out of order")
    return {legacy_marker_path(base, marker): marker for marker in markers}


def _validate_legacy_marker_store(base: Path, expected_markers: dict[Path, dict]) -> None:
    legacy_root = queue_root(base) / "legacy"
    try:
        legacy_info = legacy_root.lstat()
    except FileNotFoundError:
        legacy_info = None
    except OSError as exc:
        raise ValueError("legacy decision marker directory is unreadable") from exc
    if legacy_info is not None and (_is_reparse(legacy_root) or not stat.S_ISDIR(legacy_info.st_mode)):
        raise ValueError("legacy decision marker directory has an unsafe type")
    observed_markers = set(legacy_root.glob("*.json")) if legacy_info is not None else set()
    unexpected = observed_markers - expected_markers.keys()
    if unexpected:
        raise ValueError(f"unexpected legacy decision marker: {sorted(unexpected)[0].name}")
    for path, expected in expected_markers.items():
        try:
            marker_info = path.lstat()
        except FileNotFoundError:
            marker_info = None
        except OSError as exc:
            raise ValueError(f"legacy decision marker is unreadable: {path}") from exc
        if marker_info is None:
            continue
        try:
            observed = _load_json_path(path, "legacy decision marker")
        except (OSError, ValueError, TypeError, UnicodeError, RecursionError) as exc:
            raise ValueError(f"invalid legacy decision marker {path.name}: {exc}") from exc
        if observed != expected:
            raise ValueError(f"legacy decision marker mismatch: {path.name}")


def import_journal(base: Path) -> int:
    journal = base / "state/decisions.jsonl"
    try:
        journal_info = journal.lstat()
    except FileNotFoundError:
        journal_info = None
    except OSError as exc:
        raise ValueError("decision journal is unreadable") from exc
    if journal_info is None:
        legacy = queue_root(base) / "legacy"
        try:
            legacy_info = legacy.lstat()
        except FileNotFoundError:
            legacy_info = None
        except OSError as exc:
            raise ValueError("legacy decision marker directory is unreadable") from exc
        if legacy_info is not None and (_is_reparse(legacy) or not stat.S_ISDIR(legacy_info.st_mode)):
            raise ValueError("legacy decision marker directory has an unsafe type")
        if legacy_info is not None and any(legacy.glob("*.json")):
            raise ValueError("legacy decision markers exist without the append-only source journal")
        return 0
    if _is_reparse(journal) or not stat.S_ISREG(journal_info.st_mode):
        raise ValueError("decision journal has an unsafe type")
    with queue_lock(base):
        repair_decision_journal_tail(base, journal)
        expected_markers = _expected_legacy_markers(base, journal)
        _validate_legacy_marker_store(base, expected_markers)
        expected_by_digest = {
            marker["source_sha256"]: marker for marker in expected_markers.values()
        }
        batch = read_jsonl_since(journal, "decision-queue-import")
        prepared: list[tuple[str, dict]] = []
        for line in batch.lines:
            if line.value is None:
                continue
            raw = line.value
            record = normalize(raw)
            try:
                validate_record(base, record)
            except ValueError as exc:
                source_sha256 = hashlib.sha256(_line_text(line.raw).encode()).hexdigest()
                marker = expected_by_digest.get(source_sha256)
                if marker is not None and marker.get("source_line") == line.sequence:
                    prepared.append(("legacy", marker))
                    continue
                raise ValueError(f"invalid decision journal line {line.sequence}: {exc}") from exc
            prepared.append(("decision", record))

        # Validate every newly observed repeated identity against all indexed occurrences before
        # projecting any of the batch. Old rows were already validated before their checkpoint.
        prepared_decisions: dict[str, dict] = {}
        for kind, value in prepared:
            if kind != "decision":
                continue
            prior = prepared_decisions.get(value["id"])
            if prior is not None:
                assert_same_decision(prior, value, f"journal decision {value['id']}")
            else:
                prepared_decisions[value["id"]] = value
            for raw_match in find_jsonl_objects(journal, "id", value["id"]):
                assert_same_decision(normalize(raw_match), value,
                                     f"journal decision {value['id']}")

        imported = 0
        seen_decisions: set[str] = set()
        for kind, value in prepared:
            if kind == "legacy":
                path = legacy_marker_path(base, value)
                try:
                    marker_info = path.lstat()
                except FileNotFoundError:
                    marker_info = None
                except OSError as exc:
                    raise ValueError(f"legacy decision marker is unreadable: {path}") from exc
                if marker_info is None:
                    atomic_json(path, value)
                continue
            if value["id"] in seen_decisions:
                continue
            seen_decisions.add(value["id"])
            present = existing_path(base, value["id"])
            if present:
                try:
                    existing = _load_json_path(present, "existing decision projection")
                except (OSError, ValueError, TypeError, UnicodeError, RecursionError) as exc:
                    raise ValueError(f"existing decision projection is unreadable: {present}") from exc
                assert_same_decision(existing, value, str(present))
                continue
            target = queue_root(base) / "pending" / f"{value['id']}.json"
            atomic_json(target, value)
            imported += 1
        acknowledge_jsonl(journal, "decision-queue-import", batch)
        return imported


def validate_projection_authority(base: Path, path: Path, raw: bytes | None = None) -> dict:
    if raw is None:
        raw = _read_json_path_bytes(path, f"decision projection {path}")
    record = _load_json_bytes(raw, f"decision projection {path}")
    if not isinstance(record, dict):
        raise ValueError(f"decision projection is not an object: {path}")
    validate_record(base, record)
    assert_same_decision(record, record, str(path))
    decision_id = str(record.get("id") or "")
    try:
        matches = find_jsonl_objects(base / "state/decisions.jsonl", "id", decision_id)
    except JsonlDurabilityError as exc:
        raise ValueError(str(exc)) from exc
    if not matches:
        raise ValueError(f"decision projection lacks an authoritative journal row: {path}")
    for raw_match in matches:
        assert_same_decision(normalize(raw_match), record, str(path))
    return record


def claim(base: Path) -> Path | None:
    with queue_lock(base):
        running = sorted((queue_root(base) / "running").glob("*.json"))
        if running:
            validate_projection_authority(base, running[0])
            return running[0]
        pending = sorted((queue_root(base) / "pending").glob("*.json"))
        if not pending:
            return None
        source = pending[0]
        raw = _read_json_path_bytes(source, f"pending decision {source}")
        source_identity = _path_identity(source, f"pending decision {source}")
        validate_projection_authority(base, source, raw)
        target = queue_root(base) / "running" / source.name
        _reject_reparse_components(target.parent, "running decision directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        if _path_identity(source, f"pending decision {source}") != source_identity:
            raise ValueError("decision projection changed during claim")
        os.replace(source, target)
        fsync_dir(source.parent)
        fsync_dir(target.parent)
        return target


def claim_pending(base: Path, kind: str, excluded_projects: set[str], allowed_verbs: set[str],
                  with_snapshot: bool = False) -> Path | tuple[Path, str, str] | None:
    """Claim one pending projection without treating another running claim as singleton state."""
    if kind not in {"work", "non-work", "any"}:
        raise ValueError("claim kind must be work, non-work, or any")
    with queue_lock(base):
        for source in sorted((queue_root(base) / "pending").glob("*.json")):
            raw = _read_json_path_bytes(source, f"pending decision {source}")
            source_identity = _path_identity(source, f"pending decision {source}")
            record = _load_json_bytes(raw, f"pending decision {source}")
            if not isinstance(record, dict):
                raise ValueError(f"pending decision is not an object: {source}")
            is_work = record.get("verb") == "work"
            if allowed_verbs and str(record.get("verb") or "") not in allowed_verbs:
                continue
            if kind == "work" and not is_work:
                continue
            if kind == "non-work" and is_work:
                continue
            if str(record.get("project") or "") in excluded_projects:
                continue
            validate_projection_authority(base, source, raw)
            target = queue_root(base) / "running" / source.name
            _reject_reparse_components(target.parent, "running decision directory")
            target.parent.mkdir(parents=True, exist_ok=True)
            if _path_identity(source, f"pending decision {source}") != source_identity:
                raise ValueError("decision projection changed during claim")
            os.replace(source, target)
            fsync_dir(source.parent); fsync_dir(target.parent)
            source_sha256 = hashlib.sha256(raw).hexdigest()
            moved = _read_json_path_bytes(target, f"running decision {target}")
            if hashlib.sha256(moved).hexdigest() != source_sha256:
                raise ValueError("decision projection changed during claim")
            if with_snapshot:
                return target, source_sha256, base64.b64encode(raw).decode("ascii")
            return target
    return None


def snapshot(base: Path, source: Path) -> tuple[str, str]:
    """Return an authenticated immutable running projection snapshot under the queue lock."""
    running_root = queue_root(base) / "running"
    if source.parent != running_root or source.suffix != ".json" or _is_reparse(source):
        raise ValueError("refusing to snapshot a path outside the running decision queue")
    with queue_lock(base):
        raw = _read_json_path_bytes(source, f"decision projection {source}")
        validate_projection_authority(base, source, raw)
        return hashlib.sha256(raw).hexdigest(), base64.b64encode(raw).decode("ascii")


def transition(base: Path, source: Path, outcome: str, evidence: str,
               expected_sha256: str | None = None) -> Path:
    running_root = queue_root(base) / "running"
    if source.parent != running_root or source.suffix != ".json" \
            or outcome not in (*TERMINAL_DIRS, "pending") or _is_reparse(source):
        raise ValueError("refusing an invalid decision queue transition")
    if expected_sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("decision projection digest is invalid")
    with queue_lock(base):
        with _pinned_file(source, "decision projection", delete_access=True) as (descriptor, info):
            if info.st_size > MAX_QUEUE_JSON_BYTES:
                raise ValueError("decision projection exceeds the bounded JSON input size")
            raw = _read_pinned(descriptor, MAX_QUEUE_JSON_BYTES, "decision projection")
            source_identity = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
            observed_sha256 = hashlib.sha256(raw).hexdigest()
            if expected_sha256 is not None and observed_sha256 != expected_sha256:
                raise ValueError("decision projection changed before queue transition")
            record = _load_json_bytes(raw, "decision projection")
            if not isinstance(record, dict):
                raise ValueError("decision projection is not an object")
            if outcome == "pending":
                record["status"] = "queued"
            else:
                record["status"] = "executed" if outcome == "succeeded" else "refused"
                record["result_evidence"] = evidence
            target = queue_root(base) / outcome / source.name
            # Revalidate the source immediately before publishing the successor.  The earlier
            # read establishes the candidate record; it is not authority for a later publish.
            try:
                current = source.lstat()
            except OSError as exc:
                raise ValueError("decision projection changed before queue transition") from exc
            if (os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino,
                    os.fstat(descriptor).st_size, os.fstat(descriptor).st_mtime_ns) != source_identity \
                    or (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns) != source_identity:
                raise ValueError("decision projection changed before queue transition")
            with _pin_directory_chain(target.parent, "transition target"):
                atomic_json(target, record)
                try:
                    try:
                        current = source.lstat()
                    except OSError as exc:
                        raise ValueError("decision projection changed before queue transition") from exc
                    opened = os.fstat(descriptor)
                    opened_identity = (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
                    current_identity = (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns)
                    if opened_identity != source_identity or current_identity != source_identity:
                        raise ValueError("decision projection changed before queue transition")
                    _delete_pinned(descriptor, source)
                except OSError as exc:
                    raise ValueError("decision projection could not be removed after transition") from exc
            fsync_dir(source.parent)
            return target


def action_status(base: Path, decision_file: Path, expected_sha256: str | None = None) -> str:
    raw = _read_json_path_bytes(decision_file, "action decision projection")
    observed_sha256 = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None:
        if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256) \
                or observed_sha256 != expected_sha256:
            raise ValueError("action decision projection changed before status inspection")
    record = _load_json_bytes(raw, "action decision projection")
    if not isinstance(record, dict):
        raise ValueError("action decision projection is not an object")
    key = record.get("idempotency_key") or f"decision:{record.get('id') or digest(record)}"
    action_id = "action-" + hashlib.sha256(str(key).encode()).hexdigest()[:24]
    path = base / "state/actions" / f"{action_id}.json"
    try:
        _path_identity(path, "action record")
    except ValueError as exc:
        if "unavailable" in str(exc):
            return "absent"
        raise
    try:
        value = _load_json_path(path, "action record")
        return str(value.get("status") or "unknown") if isinstance(value, dict) else "corrupt"
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError):
        return "corrupt"


def emit_line(value: object) -> None:
    """Write protocol output with LF bytes even when Python runs on Windows."""
    sys.stdout.buffer.write(str(value).encode("utf-8") + b"\n")


def load_usage(path: str | None) -> dict | None:
    if not path:
        return None
    value = _load_json_path(Path(path), "usage record")
    if not isinstance(value, dict):
        raise ValueError("usage record must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("normalize", "enqueue"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--stamp")
        cmd.add_argument("--provider")
        cmd.add_argument("--usage-file")
    sub.add_parser("import-journal")
    sub.add_parser("claim")
    pending = sub.add_parser("claim-pending")
    pending.add_argument("--kind", choices=("work", "non-work", "any"), default="any")
    pending.add_argument("--exclude-project", action="append", default=[])
    pending.add_argument("--verb", action="append", default=[])
    pending.add_argument("--with-snapshot", action="store_true")
    snap = sub.add_parser("snapshot")
    snap.add_argument("file")
    status = sub.add_parser("action-status")
    status.add_argument("file")
    status.add_argument("--expected-sha256")
    for name in ("succeed", "fail", "defer"):
        cmd = sub.add_parser(name)
        cmd.add_argument("file")
        cmd.add_argument("evidence", nargs="?", default="")
        cmd.add_argument("--expected-sha256")
    args = parser.parse_args()
    base = root()
    try:
        if args.command in {"normalize", "enqueue"}:
            try:
                incoming = _load_json_bytes(
                    sys.stdin.buffer.read(MAX_QUEUE_JSON_BYTES + 1), "decision input"
                )
            except AttributeError:
                incoming = _load_json_bytes(
                    sys.stdin.read(MAX_QUEUE_JSON_BYTES + 1).encode("utf-8"), "decision input"
                )
            if not isinstance(incoming, dict):
                raise ValueError("decision must be a JSON object")
            record = normalize(
                incoming,
                stamp=args.stamp,
                provider=args.provider,
                usage=load_usage(args.usage_file),
            )
            validate_record(base, record)
            if args.command == "enqueue":
                path = enqueue(base, record, journal=True)
                emit_line(path)
            else:
                emit_line(json.dumps(record, sort_keys=True, separators=(",", ":")))
        elif args.command == "import-journal":
            emit_line(import_journal(base))
        elif args.command == "claim":
            path = claim(base)
            if path:
                emit_line(path)
                return 0
            return 4
        elif args.command == "claim-pending":
            result = claim_pending(base, args.kind, set(args.exclude_project), set(args.verb),
                                   args.with_snapshot)
            if isinstance(result, tuple):
                path, digest_value, snapshot_value = result
                emit_line(path)
                emit_line(digest_value)
                emit_line(snapshot_value)
                return 0
            path = result
            if path:
                emit_line(path)
                return 0
            return 4
        elif args.command == "action-status":
            emit_line(action_status(base, Path(args.file), args.expected_sha256))
        elif args.command == "snapshot":
            digest_value, snapshot_value = snapshot(base, Path(args.file))
            emit_line(digest_value)
            emit_line(snapshot_value)
        else:
            outcome = {"succeed": "succeeded", "fail": "failed", "defer": "pending"}[args.command]
            emit_line(transition(base, Path(args.file), outcome, args.evidence, args.expected_sha256))
    except (OSError, ValueError, TypeError, UnicodeError, OverflowError, RecursionError,
            json.JSONDecodeError, RuntimeError, subprocess.TimeoutExpired,
            subprocess.SubprocessError):
        print("decision-queue: operation refused", file=sys.stderr)
        return 73
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

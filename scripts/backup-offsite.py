#!/usr/bin/env python3
"""Fail-closed encrypted backup/restore controller.

The default policy is disabled and all mutating commands require ``--execute``.  Execution uses
only explicit argv vectors: age encrypts/decrypts a runtime snapshot and OpenSSH sftp transfers
the ciphertext.  Plaintext snapshots and decrypted archives live only in the configured
runtime-dir (intended to be tmpfs-backed) and are scavenged on every startup.  Evidence contains
hashes, counts, and dispositions, never credentials or decrypted content.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import hmac
import importlib.util
import io
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

if os.name == "nt":
    import ctypes
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


class BackupPolicyError(ValueError):
    pass


POLICY_KEYS = {
    "schema_version", "id", "enabled", "source", "destination", "encryption",
    "authentication", "retention", "log_rotation", "restore_drill", "archive_limits",
}
SOURCE_KEYS = {"runtime_root", "snapshot_directory", "runtime_directory"}
DESTINATION_KEYS = {"type", "user", "host", "port", "path", "credential_ref"}
AUTH_KEYS = {"type", "key_ref", "signature_file"}
STAMP_RE = re.compile(r"^backup-(\d{8}T\d{6}Z)\.tar\.age$")
WORK_RE = re.compile(r"^\.backup\.(\d+)\.(\d+)\.[0-9a-f]{16}$")
REMOTE_SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
MAX_REMOTE_LISTING = 1000
MAX_SFTP_OUTPUT = MAX_REMOTE_LISTING * 256
MAX_SFTP_ERROR = 64 * 1024
MAX_TOOL_ARGS_JSON = 64 * 1024
MAX_TOOL_ARGS = 64
MAX_TOOL_ARG_LENGTH = 4096
MAX_POLICY_BYTES = 2 * 1024 * 1024
MAX_CREDENTIAL_BYTES = 1024 * 1024
PIPE_JOIN_TIMEOUT = 5.0
PROCESS_TIMEOUT = 300.0


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
    handle = _CREATE_FILE_W(
        str(path), access, share, None, 3, flags, None,  # OPEN_EXISTING
    )
    invalid = ctypes.c_void_p(-1).value
    if handle == invalid:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except OSError:
        _CLOSE_HANDLE(handle)
        raise
    return descriptor


def _delete_pinned(descriptor: int, path: Path) -> None:
    """Delete the already-open file identity, avoiding a pathname unlink race on Windows."""
    if os.name != "nt":
        path.unlink()
        return
    class _FileDispositionInfo(ctypes.Structure):
        _fields_ = [("DeleteFile", wintypes.BOOLEAN)]
    disposition = _FileDispositionInfo(True)
    handle = msvcrt.get_osfhandle(descriptor)
    if not _SET_FILE_INFORMATION_BY_HANDLE(
            handle, 4, ctypes.byref(disposition), ctypes.sizeof(disposition)):
        raise ctypes.WinError(ctypes.get_last_error())


@contextlib.contextmanager
def _pin_directory_chain(path: Path, label: str):
    """Keep every existing directory ancestor pinned until the path operation completes."""
    handles: list[int] = []
    current = Path(path.anchor)
    try:
        for component in path.parts[1:]:
            current /= component
            try:
                info = current.lstat()
            except OSError as exc:
                raise BackupPolicyError(f"{label} parent is unavailable") from exc
            if _is_reparse(info) or not stat.S_ISDIR(info.st_mode):
                raise BackupPolicyError(f"{label} parent is unsafe")
            descriptor = _open_pinned(current, directory=True)
            try:
                opened = os.fstat(descriptor)
                if _is_reparse(opened) or not stat.S_ISDIR(opened.st_mode) \
                        or (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                    raise BackupPolicyError(f"{label} parent changed while opening")
            except BaseException:
                os.close(descriptor)
                raise
            handles.append(descriptor)
        yield
    finally:
        for descriptor in reversed(handles):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _is_reparse(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0)) \
        or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _reject_reparse_components(path: Path, label: str) -> None:
    """Check every existing component before any later resolution or use."""
    if not isinstance(path, Path) or not path.is_absolute() \
            or any(part in {".", ".."} for part in path.parts):
        raise BackupPolicyError(f"{label} must be an absolute path")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise BackupPolicyError(f"{label} is unreadable") from exc
        if _is_reparse(info):
            raise BackupPolicyError(f"{label} contains a symlink/reparse component")


def _validate_real_directory(path: Path, label: str) -> Path:
    _reject_reparse_components(path, label)
    try:
        info = path.lstat()
    except OSError as exc:
        raise BackupPolicyError(f"{label} is unavailable") from exc
    if _is_reparse(info) or not stat.S_ISDIR(info.st_mode):
        raise BackupPolicyError(f"{label} must be a real directory")
    return path


def _directory_identity(path: Path, label: str) -> tuple[int, int, int, int]:
    _validate_real_directory(path, label)
    try:
        info = path.lstat()
    except OSError as exc:
        raise BackupPolicyError(f"{label} is unavailable") from exc
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _file_identity(info: os.stat_result) -> tuple[int, int, int, int]:
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _unlink_if_identity(path: Path, expected: tuple[int, int, int, int]) -> None:
    """Best-effort cleanup that never removes a replacement at the old pathname."""
    try:
        with _pin_directory_chain(path.parent, "temporary cleanup"):
            descriptor = _open_pinned(path, delete_access=True)
            try:
                observed = os.fstat(descriptor)
                if _file_identity(observed) == expected:
                    _delete_pinned(descriptor, path)
            finally:
                os.close(descriptor)
    except (FileNotFoundError, OSError, ValueError, TypeError):
        return


def _read_real_file(path: Path, label: str, maximum: int) -> bytes:
    """Read a bounded regular file through one descriptor after reparse checks."""
    _reject_reparse_components(path, label)
    try:
        expected = path.lstat()
    except OSError as exc:
        raise BackupPolicyError(f"{label} is unavailable") from exc
    if _is_reparse(expected) or not stat.S_ISREG(expected.st_mode):
        raise BackupPolicyError(f"{label} is unavailable")
    flags = os.O_RDONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except (OSError, ValueError, TypeError) as exc:
        raise BackupPolicyError(f"{label} is unavailable") from exc
    try:
        info = os.fstat(descriptor)
        if _is_reparse(info) or not stat.S_ISREG(info.st_mode) \
                or (info.st_dev, info.st_ino) != (expected.st_dev, expected.st_ino) \
                or info.st_size != expected.st_size:
            raise BackupPolicyError(f"{label} is unavailable")
        if info.st_size < 0 or info.st_size > maximum:
            raise BackupPolicyError(f"{label} exceeds the bounded size")
        with os.fdopen(descriptor, "rb", closefd=True) as source:
            descriptor = -1
            value = source.read(maximum + 1)
        if len(value) > maximum:
            raise BackupPolicyError(f"{label} exceeds the bounded size")
        return value
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        raise BackupPolicyError(f"{label} is unreadable") from exc
    finally:
        if descriptor != -1:
            try:
                os.close(descriptor)
            except OSError:
                pass


def _object(value: object, keys: set[str], where: str) -> dict:
    if not isinstance(value, dict):
        raise BackupPolicyError(f"{where} must be an object")
    missing = keys - value.keys()
    extra = value.keys() - keys
    if missing:
        raise BackupPolicyError(f"{where} missing key(s): {', '.join(sorted(missing))}")
    if extra:
        raise BackupPolicyError(f"{where} has unknown key(s): {', '.join(sorted(extra))}")
    return value


def _positive(value: object, where: str, maximum: int = 3650) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise BackupPolicyError(f"{where} must be an integer in 1..{maximum}")
    return value


def _absolute(value: object, where: str) -> None:
    normalized = value.replace("\\", "/") if isinstance(value, str) else ""
    if not isinstance(value, str) or (not Path(value).is_absolute() and not value.startswith("/")) \
            or "\x00" in value or value.startswith(("\\\\", "//", "~")) \
            or "%" in value or re.match(r"^[A-Za-z]:[^\\/].*", value) \
            or any(part in {".", ".."} for part in normalized.split("/")) \
            or "//" in normalized[1:]:
        raise BackupPolicyError(f"{where} must be an absolute path")


def _secret_ref(value: object, where: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"secret:[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value):
        raise BackupPolicyError(f"{where} must reference a secret, not contain one")


def load_policy(path: Path) -> dict:
    try:
        raw = _read_real_file(path, "backup policy", MAX_POLICY_BYTES)
        policy = json.loads(raw.decode("utf-8"),
                            parse_constant=lambda name: (_ for _ in ()).throw(ValueError(name)))
    except (OSError, UnicodeDecodeError, ValueError, TypeError, OverflowError,
            json.JSONDecodeError, RecursionError, BackupPolicyError) as exc:
        raise BackupPolicyError("backup policy is unreadable") from exc
    policy = _object(policy, POLICY_KEYS, "policy")
    if not isinstance(policy["schema_version"], int) or isinstance(policy["schema_version"], bool) \
            or policy["schema_version"] != 1 or not isinstance(policy["enabled"], bool):
        raise BackupPolicyError("schema_version must be 1 and enabled must be boolean")
    if not isinstance(policy["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", policy["id"]):
        raise BackupPolicyError("policy.id must be a safe nonempty identifier")
    source = _object(policy["source"], SOURCE_KEYS, "source")
    for key in SOURCE_KEYS:
        _absolute(source[key], f"source.{key}")
    destination = _object(policy["destination"], DESTINATION_KEYS, "destination")
    if destination["type"] != "sftp":
        raise BackupPolicyError("destination.type must be sftp")
    for key in ("user", "host"):
        if not isinstance(destination[key], str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", destination[key]):
            raise BackupPolicyError(f"destination.{key} is invalid")
    _absolute(destination["path"], "destination.path")
    remote_path = PurePosixPath(destination["path"])
    if not destination["path"].startswith("/") or any(
            part in {"", ".", ".."} for part in remote_path.parts) \
            or any(ord(char) < 32 or char.isspace() for char in destination["path"]) \
            or any(not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", part)
                   for part in remote_path.parts if part != "/"):
        raise BackupPolicyError("destination.path must be a canonical absolute SFTP path")
    _positive(destination["port"], "destination.port", 65535)
    _secret_ref(destination["credential_ref"], "destination.credential_ref")
    encryption = _object(policy["encryption"], {"tool", "recipient_file", "identity_ref"}, "encryption")
    if encryption["tool"] != "age":
        raise BackupPolicyError("encryption.tool must be age")
    _absolute(encryption["recipient_file"], "encryption.recipient_file")
    _secret_ref(encryption["identity_ref"], "encryption.identity_ref")
    authentication = _object(policy["authentication"], AUTH_KEYS, "authentication")
    if authentication["type"] != "hmac-sha256":
        raise BackupPolicyError("authentication.type must be hmac-sha256")
    _secret_ref(authentication["key_ref"], "authentication.key_ref")
    _absolute(authentication["signature_file"], "authentication.signature_file")
    retention = _object(policy["retention"], {"daily", "weekly", "monthly"}, "retention")
    for key, maximum in (("daily", 3650), ("weekly", 520), ("monthly", 240)):
        _positive(retention[key], f"retention.{key}", maximum)
    rotation = _object(policy["log_rotation"], {"directory", "max_size_mb", "keep"}, "log_rotation")
    _absolute(rotation["directory"], "log_rotation.directory")
    _positive(rotation["max_size_mb"], "log_rotation.max_size_mb", 10240)
    _positive(rotation["keep"], "log_rotation.keep", 3650)
    drill = _object(policy["restore_drill"], {"cadence_days", "required"}, "restore_drill")
    _positive(drill["cadence_days"], "restore_drill.cadence_days", 3650)
    if drill["required"] is not True:
        raise BackupPolicyError("restore_drill.required must remain true")
    limits = _object(policy["archive_limits"], {"max_files", "max_bytes"}, "archive_limits")
    _positive(limits["max_files"], "archive_limits.max_files", 1000000)
    _positive(limits["max_bytes"], "archive_limits.max_bytes", 1073741824)
    return policy


def runtime_module():
    source = Path(__file__).resolve().with_name("runtime-state.py")
    spec = importlib.util.spec_from_file_location("recursion_runtime_state", source)
    if spec is None or spec.loader is None:
        raise BackupPolicyError("runtime-state helper is absent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def secret_runtime_module():
    source = Path(__file__).resolve().with_name("secret_runtime.py")
    spec = importlib.util.spec_from_file_location("recursion_secret_runtime", source)
    if spec is None or spec.loader is None:
        raise BackupPolicyError("secret runtime helper is absent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _credential_path(ref: str) -> Path:
    _secret_ref(ref, "credential reference")
    name = ref.split(":", 1)[1]
    directory = os.environ.get("CREDENTIALS_DIRECTORY") or os.environ.get("RECURSION_CREDENTIALS_DIRECTORY")
    if not directory:
        raise BackupPolicyError("systemd credentials directory is unavailable")
    path = Path(directory) / name
    _reject_reparse_components(path, "credential path")
    try:
        info = path.lstat()
    except OSError as exc:
        raise BackupPolicyError("referenced credential is unavailable") from exc
    if _is_reparse(info) or not stat.S_ISREG(info.st_mode):
        raise BackupPolicyError("referenced credential is unavailable")
    mode = stat.S_IMODE(info.st_mode)
    if os.name != "nt" and mode & 0o077:
        raise BackupPolicyError("referenced credential is group/other accessible")
    if os.name != "nt" and hasattr(os, "geteuid") and os.geteuid() == 0 \
            and info.st_uid != 0:
        raise BackupPolicyError("referenced credential is not root-owned")
    return path


def authenticate_policy(path: Path, policy: dict) -> None:
    key_path = _credential_path(policy["authentication"]["key_ref"])
    signature = Path(policy["authentication"]["signature_file"])
    key = _read_real_file(key_path, "authentication key", MAX_CREDENTIAL_BYTES)
    signature_bytes = _read_real_file(signature, "policy signature", 256)
    try:
        expected = signature_bytes.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise BackupPolicyError("authenticated policy signature is unreadable") from exc
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise BackupPolicyError("authenticated policy signature has invalid shape")
    policy_bytes = _read_real_file(path, "backup policy", MAX_POLICY_BYTES)
    observed = hmac.new(key, policy_bytes, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, observed):
        raise BackupPolicyError("authenticated policy signature does not match")


def require_execution(path: Path, policy: dict, execute: bool) -> None:
    if not execute:
        raise BackupPolicyError("mutating backup commands require explicit --execute")
    if not policy["enabled"]:
        raise BackupPolicyError("backup policy is disabled")
    authenticate_policy(path, policy)


def _safe_runtime_dir(path: Path) -> None:
    _reject_reparse_components(path, "backup runtime directory")
    try:
        info = path.lstat()
    except FileNotFoundError:
        info = None
    except OSError as exc:
        raise BackupPolicyError("backup runtime directory is unreadable") from exc
    if info is not None and (_is_reparse(info) or not stat.S_ISDIR(info.st_mode)):
        raise BackupPolicyError("backup runtime directory has an unsafe type")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    _reject_reparse_components(path, "backup runtime directory")
    try:
        info = path.lstat()
    except OSError as exc:
        raise BackupPolicyError("backup runtime directory is unavailable") from exc
    if _is_reparse(info) or not stat.S_ISDIR(info.st_mode):
        raise BackupPolicyError("backup runtime directory has an unsafe type")
    if os.name != "nt" and stat.S_IMODE(info.st_mode) & 0o077:
        raise BackupPolicyError("backup runtime directory is group/other accessible")
    if hasattr(os, "geteuid") and os.geteuid() == 0 and info.st_uid != 0:
        raise BackupPolicyError("backup runtime directory is not root-owned")


@contextlib.contextmanager
def private_workspace(path: Path):
    _safe_runtime_dir(path)
    secret_runtime = secret_runtime_module()
    secret_runtime.scavenge(path)
    for stale in path.iterdir():
        match = WORK_RE.fullmatch(stale.name)
        if match:
            try:
                stale_pid = int(match.group(1))
            except (ValueError, OverflowError):
                raise BackupPolicyError("backup runtime contains an invalid process identity") from None
            if len(match.group(1)) > 20:
                raise BackupPolicyError("backup runtime contains an invalid process identity")
            observed = secret_runtime.process_start(stale_pid)
            if observed is None or observed != match.group(2):
                try:
                    stale_info = stale.lstat()
                except FileNotFoundError:
                    continue
                except OSError as exc:
                    raise BackupPolicyError("backup runtime stale entry is unreadable") from exc
                if _is_reparse(stale_info) or not stat.S_ISDIR(stale_info.st_mode):
                    stale.unlink(missing_ok=True)
                else:
                    shutil.rmtree(stale)
    start = secret_runtime.process_start(os.getpid())
    if start is None:
        raise BackupPolicyError("cannot witness backup process identity")
    work = Path(tempfile.mkdtemp(prefix=f".backup.{os.getpid()}.{start}.", dir=path))
    try:
        work.chmod(0o700)
        yield work
    finally:
        try:
            shutil.rmtree(work)
        except OSError as exc:
            raise BackupPolicyError("backup plaintext workspace cleanup failed") from exc


def _validate_canonical_directory(path: Path, label: str) -> Path:
    _reject_reparse_components(path, label)
    if not path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise BackupPolicyError(f"{label} must be a canonical absolute directory")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            try:
                current.mkdir(mode=0o700)
            except FileExistsError:
                pass
            try:
                info = current.lstat()
            except OSError as exc:
                raise BackupPolicyError(f"{label} parent is unavailable") from exc
        except OSError as exc:
            raise BackupPolicyError(f"{label} parent is unreadable") from exc
        if _is_reparse(info):
            raise BackupPolicyError(f"{label} has a symlink/reparse parent")
        if not stat.S_ISDIR(info.st_mode) or (os.name != "nt" and (
                stat.S_IMODE(info.st_mode) & 0o022 and
                not (stat.S_IMODE(info.st_mode) & stat.S_ISVTX))):
            raise BackupPolicyError(f"{label} parent ownership/mode is unsafe")
        if hasattr(os, "geteuid") and os.geteuid() == 0 and info.st_uid != 0:
            raise BackupPolicyError(f"{label} parent is not root-owned")
    _reject_reparse_components(path, label)
    info = path.lstat()
    if _is_reparse(info) or not stat.S_ISDIR(info.st_mode) \
            or (os.name != "nt" and stat.S_IMODE(info.st_mode) & 0o077):
        raise BackupPolicyError(f"{label} ownership/mode is unsafe")
    if hasattr(os, "geteuid") and os.geteuid() == 0 and info.st_uid != 0:
        raise BackupPolicyError(f"{label} is not root-owned")
    return path


@contextlib.contextmanager
def pause_transfer(root: Path):
    """Atomically admit one external transfer while pause.sh is unable to race it."""
    runtime = runtime_module()
    lock = runtime.DirectoryLock(root / "state/.locks/pause-transfer.lock", "pause-transfer")
    try:
        with lock:
            pause = root / "state/PAUSE"
            try:
                pause_info = pause.lstat()
            except OSError as exc:
                raise BackupPolicyError("PAUSE admission is unavailable") from exc
            if _is_reparse(pause_info) or not stat.S_ISREG(pause_info.st_mode):
                raise BackupPolicyError("PAUSE admission is absent; refusing external transfer")
            yield
    except RuntimeError as exc:
        raise BackupPolicyError("PAUSE transfer admission failed") from exc


def _run(argv: list[str], *, input_bytes: bytes | None = None,
         max_stdout: int = MAX_SFTP_OUTPUT, max_stderr: int = MAX_SFTP_ERROR,
         file_size_limit: int | None = None) -> subprocess.CompletedProcess[bytes]:
    if not argv or any(not isinstance(item, str) or not item for item in argv):
        raise BackupPolicyError("external tool argv is invalid")
    if input_bytes is not None and not isinstance(input_bytes, bytes):
        raise BackupPolicyError("external tool input is invalid")
    try:
        popen_kwargs = dict(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.name == "nt":
            popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            popen_kwargs["start_new_session"] = True
        process = subprocess.Popen(argv, preexec_fn=(
                                       _limit_file_size(file_size_limit) if file_size_limit is not None
                                       and os.name != "nt" else None), **popen_kwargs)
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        raise BackupPolicyError(f"required backup tool is unavailable: {argv[0]}") from exc
    captured: dict[str, bytes] = {}
    overflow = threading.Event()

    def drain(name: str, stream, limit: int) -> None:
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                overflow.set()
                try:
                    process.kill()
                except OSError:
                    pass
                return
            chunks.append(chunk)
        captured[name] = b"".join(chunks)

    threads = [threading.Thread(target=drain, args=("stdout", process.stdout, max_stdout), daemon=True),
               threading.Thread(target=drain, args=("stderr", process.stderr, max_stderr), daemon=True)]
    for thread in threads:
        thread.start()
    if process.stdin is not None:
        try:
            if input_bytes:
                process.stdin.write(input_bytes)
            process.stdin.close()
        except (BrokenPipeError, OSError):
            pass
    try:
        returncode = process.wait(timeout=PROCESS_TIMEOUT)
    except subprocess.TimeoutExpired as exc:
        _terminate_process_tree(process)
        try:
            process.wait(timeout=PIPE_JOIN_TIMEOUT)
        except subprocess.TimeoutExpired as exc:
            raise BackupPolicyError("backup tool did not terminate after its bounded runtime") from exc
        raise BackupPolicyError("backup tool exceeded its bounded runtime") from exc
    for thread in threads:
        thread.join(PIPE_JOIN_TIMEOUT)
    if any(thread.is_alive() for thread in threads):
        _terminate_process_tree(process)
        for stream in (process.stdout, process.stderr):
            try:
                stream.close()
            except OSError:
                pass
        for thread in threads:
            thread.join(PIPE_JOIN_TIMEOUT)
        raise BackupPolicyError("backup tool retained an inherited output pipe")
    if overflow.is_set():
        raise BackupPolicyError("backup tool output exceeds the bounded limit")
    result = subprocess.CompletedProcess(argv, returncode, captured.get("stdout", b""),
                                         captured.get("stderr", b""))
    if result.returncode:
        raise BackupPolicyError(f"backup tool failed: {Path(argv[0]).name}")
    return result


def _terminate_process_tree(process: subprocess.Popen) -> None:
    """Terminate the external transfer and descendants that could retain its pipes."""
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=PIPE_JOIN_TIMEOUT, check=False)
        else:
            os.killpg(process.pid, signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        try:
            process.kill()
        except OSError:
            pass


def _limit_file_size(limit: int):
    """Return a child pre-exec hook that caps files created by an untrusted SFTP client."""
    def apply() -> None:
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))
        except (ImportError, OSError, ValueError):
            pass
    return apply


def _tool(name: str, environment_name: str) -> list[str]:
    value = os.environ.get(environment_name, "").strip() or shutil.which(name)
    if not value:
        raise BackupPolicyError(f"required backup tool is unavailable: {name}")
    raw_extra = os.environ.get(environment_name + "_ARGS_JSON", "[]")
    if len(raw_extra) > MAX_TOOL_ARGS_JSON:
        raise BackupPolicyError(f"backup tool arguments are invalid: {name}")
    try:
        extra = json.loads(raw_extra,
                           parse_constant=lambda constant: (_ for _ in ()).throw(ValueError(constant)))
    except (json.JSONDecodeError, ValueError, TypeError, UnicodeError, OverflowError,
            RecursionError) as exc:
        raise BackupPolicyError(f"backup tool arguments are invalid: {name}") from exc
    if not isinstance(extra, list) or len(extra) > MAX_TOOL_ARGS \
            or not all(isinstance(item, str) and item and len(item) <= MAX_TOOL_ARG_LENGTH for item in extra):
        raise BackupPolicyError(f"backup tool arguments are invalid: {name}")
    return [value, *extra]


def _sftp_base(policy: dict, key: Path) -> list[str]:
    destination = policy["destination"]
    return [*_tool("sftp", "RECURSION_SFTP_TOOL"), "-q", "-i", str(key), "-P",
            str(destination["port"]), "-b", "-", f"{destination['user']}@{destination['host']}"]


def _remote_path(policy: dict, name: str) -> str:
    if "/" in name or name in {"", ".", ".."} or not STAMP_RE.fullmatch(name):
        raise BackupPolicyError("remote artifact name is unsafe")
    return policy["destination"]["path"].rstrip("/") + "/" + name


def _remote_safe_path(policy: dict, name: str) -> str:
    if not REMOTE_SAFE_NAME_RE.fullmatch(name):
        raise BackupPolicyError("remote artifact name is unsafe")
    return policy["destination"]["path"].rstrip("/") + "/" + name


def sftp(policy: dict, batch: str, *, max_stdout: int = MAX_SFTP_OUTPUT) -> bytes:
    key = _credential_path(policy["destination"]["credential_ref"])
    return _run(_sftp_base(policy, key), input_bytes=batch.encode("utf-8"),
                max_stdout=max_stdout).stdout


def sftp_download(policy: dict, remote: str, destination: Path, max_bytes: int) -> None:
    """Download one ciphertext with a child file-size cap and a postcondition check."""
    key = _credential_path(policy["destination"]["credential_ref"])
    command = f"get {remote} {destination}\n"
    _run(_sftp_base(policy, key), input_bytes=command.encode("utf-8"),
         file_size_limit=max_bytes)
    try:
        observed = destination.stat().st_size
    except OSError as exc:
        raise BackupPolicyError("SFTP download did not produce a ciphertext") from exc
    if observed > max_bytes:
        destination.unlink(missing_ok=True)
        raise BackupPolicyError("downloaded ciphertext exceeds configured byte-size bound")


def _remote_listing(policy: dict) -> tuple[list[str], list[str]]:
    base = policy["destination"]["path"].rstrip("/")
    raw_output = sftp(policy, f"ls -1 {base}/*\n", max_stdout=MAX_SFTP_OUTPUT)
    if len(raw_output) > MAX_SFTP_OUTPUT:
        raise BackupPolicyError("remote artifact listing exceeds the bounded policy")
    output = raw_output.decode("utf-8", "replace")
    names: set[str] = set()
    invalid: list[str] = []
    entries = 0
    for line in output.splitlines():
        raw = line.strip()
        if not raw:
            continue
        entries += 1
        if entries > MAX_REMOTE_LISTING:
            raise BackupPolicyError("remote artifact listing exceeds the bounded policy")
        candidate = raw.rsplit("/", 1)[-1]
        if "/" in raw:
            remote = PurePosixPath(raw)
            if not remote.is_absolute() or remote.parent != PurePosixPath(base):
                raise BackupPolicyError("remote listing path is outside the configured destination")
        if not candidate or not REMOTE_SAFE_NAME_RE.fullmatch(candidate):
            raise BackupPolicyError("remote listing contains an unsafe artifact name")
        if STAMP_RE.fullmatch(candidate) and artifact_time(candidate) is not None:
            names.add(candidate)
        else:
            invalid.append(candidate)
    return sorted(names), sorted(set(invalid))


def remote_artifacts(policy: dict, root: Path | None = None) -> list[str]:
    if root is None:
        root = Path(policy["source"]["runtime_root"])
    with pause_transfer(root):
        names, _ = _remote_listing(policy)
    return names


def artifact_time(name: str) -> datetime | None:
    match = STAMP_RE.fullmatch(name)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def retention_keep(names: list[str], retention: dict, now: datetime | None = None) -> set[str]:
    dated = [(name, artifact_time(name)) for name in names]
    dated = [(name, stamp) for name, stamp in dated if stamp is not None]
    dated.sort(key=lambda item: item[1], reverse=True)
    days = []
    weeks = []
    months = []
    for name, stamp in dated:
        day = stamp.date()
        week = stamp.isocalendar()[:2]
        month = (stamp.year, stamp.month)
        if day not in days and len(days) < retention["daily"]:
            days.append(day)
        if week not in weeks and len(weeks) < retention["weekly"]:
            weeks.append(week)
        if month not in months and len(months) < retention["monthly"]:
            months.append(month)
    keep = {name for name, stamp in dated
            if stamp.date() in days or stamp.isocalendar()[:2] in weeks
            or (stamp.year, stamp.month) in months}
    return keep


def validate_archive_bounds(archive: Path, limits: dict) -> dict[str, int]:
    max_files, max_bytes = limits["max_files"], limits["max_bytes"]
    physical = archive.stat().st_size
    if physical > max_bytes:
        raise BackupPolicyError("archive exceeds configured byte-size bound")
    files = 0
    content_bytes = 0
    with tarfile.open(archive, "r:") as source:
        for member in source.getmembers():
            if member.isdir():
                continue
            if not member.isfile() or member.issym() or member.islnk():
                raise BackupPolicyError("archive contains an unsupported or linked entry")
            files += 1
            content_bytes += member.size
            if files > max_files or content_bytes > max_bytes:
                raise BackupPolicyError("archive exceeds configured file-count/byte-size bounds")
    return {"files": files, "bytes": content_bytes, "archive_bytes": physical}


def _remote_delete(policy: dict, name: str) -> None:
    if not REMOTE_SAFE_NAME_RE.fullmatch(name):
        raise BackupPolicyError("refusing to delete an unsafe remote artifact name")
    sftp(policy, f"rm {_remote_safe_path(policy, name)}\n")


def reconcile_remote(policy: dict) -> dict:
    root = Path(policy["source"]["runtime_root"])
    with pause_transfer(root):
        names, invalid_names = _remote_listing(policy)
        # A bounded, malformed-name policy: safely named unknown objects are deleted and recorded;
        # ambiguous names fail closed because no remote command can address them safely.
        invalid_deleted: list[str] = []
        for name in invalid_names:
            _remote_delete(policy, name)
            invalid_deleted.append(name)
        valid: list[str] = []
        invalid_archives: list[str] = []
        with private_workspace(Path(policy["source"]["runtime_directory"])) as work:
            for name in names:
                ciphertext = work / name
                archive = work / f"{name}.tar"
                try:
                    sftp_download(policy, _remote_path(policy, name), ciphertext,
                                  policy["archive_limits"]["max_bytes"])
                    decrypt(ciphertext, archive, policy)
                    validate_archive_bounds(archive, policy["archive_limits"])
                except (BackupPolicyError, OSError, tarfile.TarError):
                    invalid_archives.append(name)
                else:
                    valid.append(name)
                finally:
                    ciphertext.unlink(missing_ok=True)
                    archive.unlink(missing_ok=True)
        for name in invalid_archives:
            _remote_delete(policy, name)
        names = valid
    keep = retention_keep(names, policy["retention"])
    deleted: list[str] = []
    for name in names:
        if name in keep:
            continue
        with pause_transfer(root):
            _remote_delete(policy, name)
        deleted.append(name)
    return {"remote_seen": len(names), "retained": len(keep), "deleted": len(deleted),
            "deleted_artifacts": deleted, "invalid_deleted": invalid_deleted + invalid_archives}


def write_evidence(directory: Path, evidence: dict) -> Path:
    _reject_reparse_components(directory, "evidence directory")
    try:
        info = directory.lstat()
    except FileNotFoundError:
        info = None
    except OSError as exc:
        raise BackupPolicyError("evidence directory is unreadable") from exc
    if info is not None and (_is_reparse(info) or not stat.S_ISDIR(info.st_mode)):
        raise BackupPolicyError("evidence directory has an unsafe type")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    _validate_real_directory(directory, "evidence directory")
    directory.chmod(0o700)
    raw = (json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode("utf-8")
    target = directory / f"backup-evidence-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{time.time_ns()}-{hashlib.sha256(raw).hexdigest()[:12]}.json"
    fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.tmp.", dir=directory)
    temporary = Path(temporary_name)
    temporary_identity = _file_identity(os.fstat(fd))
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        _validate_real_directory(directory, "evidence directory")
        _publish_file_noreplace(temporary, target, "evidence file")
        if os.name != "nt":
            descriptor = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return target
    except BaseException:
        _unlink_if_identity(temporary, temporary_identity)
        raise


def archive_snapshot(snapshot: Path, target: Path) -> None:
    with tarfile.open(target, "w") as archive:
        archive.add(snapshot, arcname="snapshot", recursive=True)


def _publish_file_noreplace(source: Path, target: Path, label: str) -> None:
    """Publish a same-directory file without replacing a concurrent owner."""
    _reject_reparse_components(source, f"{label} source")
    _reject_reparse_components(target.parent, f"{label} parent")
    _reject_reparse_components(target, label)
    try:
        source_info = source.lstat()
    except OSError as exc:
        raise BackupPolicyError(f"{label} source is unavailable") from exc
    if _is_reparse(source_info) or not stat.S_ISREG(source_info.st_mode):
        raise BackupPolicyError(f"{label} source is unsafe")
    source_identity = _file_identity(source_info)
    with contextlib.ExitStack() as stack:
        stack.enter_context(_pin_directory_chain(source.parent, f"{label} source"))
        if target.parent != source.parent:
            stack.enter_context(_pin_directory_chain(target.parent, f"{label} target"))
        try:
            source_descriptor = _open_pinned(source, delete_access=True)
        except (OSError, ValueError, TypeError) as exc:
            raise BackupPolicyError(f"{label} source is unavailable") from exc
        try:
            opened = os.fstat(source_descriptor)
            if _is_reparse(opened) or not stat.S_ISREG(opened.st_mode) \
                    or _file_identity(opened) != source_identity:
                raise BackupPolicyError(f"{label} source changed while opening")
            try:
                os.link(source, target, follow_symlinks=False)
            except FileExistsError as exc:
                raise BackupPolicyError(f"{label} already exists") from exc
            except (OSError, ValueError, TypeError) as exc:
                raise BackupPolicyError(f"{label} could not be published") from exc
            # Recheck the pathname and the same pinned descriptor immediately before cleanup.
            # On Windows _open_pinned denies delete-sharing and _delete_pinned removes this
            # exact handle identity, so a replacement cannot be unlinked through the name.
            try:
                current = source.lstat()
            except OSError as exc:
                raise BackupPolicyError(f"{label} source changed before cleanup") from exc
            if _file_identity(current) != source_identity \
                    or _file_identity(os.fstat(source_descriptor)) != source_identity:
                raise BackupPolicyError(f"{label} source changed before cleanup")
            try:
                _delete_pinned(source_descriptor, source)
            except (OSError, ValueError, TypeError) as exc:
                raise BackupPolicyError(f"{label} temporary cleanup failed") from exc
        finally:
            try:
                os.close(source_descriptor)
            except OSError:
                pass
    if os.name != "nt":
        try:
            descriptor = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        except OSError as exc:
            raise BackupPolicyError(f"{label} directory durability failed") from exc


def encrypt(archive: Path, ciphertext: Path, policy: dict) -> None:
    recipient = Path(policy["encryption"]["recipient_file"])
    _read_real_file(recipient, "age recipient file", MAX_CREDENTIAL_BYTES)
    _run([*_tool("age", "RECURSION_AGE_TOOL"), "--encrypt", "--recipient-file",
          str(recipient), "--output", str(ciphertext), str(archive)])


def decrypt(ciphertext: Path, archive: Path, policy: dict) -> None:
    identity = _credential_path(policy["encryption"]["identity_ref"])
    _run([*_tool("age", "RECURSION_AGE_TOOL"), "--decrypt", "--identity", str(identity),
          "--output", str(archive), str(ciphertext)])


def extract_snapshot(archive: Path, target: Path) -> Path:
    target.mkdir(mode=0o700)
    with tarfile.open(archive, "r:") as source:
        for member in source.getmembers():
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or not name.parts or name.parts[0] != "snapshot":
                raise BackupPolicyError("encrypted backup contains an unsafe archive path")
            if member.isdir():
                continue
            if member.issym() or member.islnk():
                raise BackupPolicyError("encrypted backup contains a link entry")
            if not member.isfile():
                raise BackupPolicyError("encrypted backup contains an unsupported archive entry")
            destination = target.joinpath(*name.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source.extractfile(member) as input_stream, destination.open("wb") as output:
                assert input_stream is not None
                shutil.copyfileobj(input_stream, output)
            os.chmod(destination, stat.S_IMODE(member.mode) or 0o600)
    snapshot = target / "snapshot"
    runtime_module().load_manifest(snapshot)
    return snapshot


def execute_backup(config_path: Path, policy: dict) -> dict:
    root = Path(policy["source"]["runtime_root"])
    pause = root / "state/PAUSE"
    _reject_reparse_components(pause, "backup PAUSE path")
    try:
        pause_info = pause.lstat()
    except OSError as exc:
        raise BackupPolicyError("PAUSE is required for backup admission") from exc
    if _is_reparse(pause_info) or not stat.S_ISREG(pause_info.st_mode):
        raise BackupPolicyError("PAUSE is required for backup admission")
    snapshot_directory = _validate_canonical_directory(
        Path(policy["source"]["snapshot_directory"]), "snapshot directory"
    )
    runtime = runtime_module()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    name = f"backup-{stamp}.tar.age"
    with private_workspace(Path(policy["source"]["runtime_directory"])) as work:
        snapshot = work / "snapshot"
        with contextlib.redirect_stdout(io.StringIO()):
            runtime.backup(root, snapshot)
        archive = work / "snapshot.tar"
        ciphertext = work / name
        archive_snapshot(snapshot, archive)
        validate_archive_bounds(archive, policy["archive_limits"])
        encrypt(archive, ciphertext, policy)
        durable = snapshot_directory / name
        _reject_reparse_components(durable, "durable snapshot path")
        try:
            durable_info = durable.lstat()
        except FileNotFoundError:
            durable_info = None
        except OSError as exc:
            raise BackupPolicyError("durable snapshot path is unreadable") from exc
        if durable_info is not None:
            raise BackupPolicyError("snapshot artifact already exists")
        temporary = snapshot_directory / f".{name}.tmp.{os.getpid()}.{time.time_ns()}"
        try:
            with temporary.open("xb") as output, ciphertext.open("rb") as source:
                shutil.copyfileobj(source, output)
                output.flush()
                os.fsync(output.fileno())
            os.chmod(temporary, 0o600)
            temporary_identity = _file_identity(temporary.lstat())
            _validate_real_directory(snapshot_directory, "snapshot directory")
            _reject_reparse_components(durable, "durable snapshot path")
            _publish_file_noreplace(temporary, durable, "durable snapshot")
        except BaseException:
            if "temporary_identity" in locals():
                _unlink_if_identity(temporary, temporary_identity)
            raise
        try:
            with pause_transfer(root):
                sftp(policy, f"put {durable} {_remote_path(policy, name)}\n")
        except BaseException:
            # The durable canonical snapshot remains for an operator-authorized retry.
            raise
    retention = reconcile_remote(policy)
    evidence = {"schema_version": 1, "operation": "backup", "status": "succeeded",
                "artifact": name, "encrypted": True, "remote_uploaded": True,
                "retention": retention, "restore_evidence": "pending live evidence",
                "policy_id": policy["id"], "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    evidence["evidence_path"] = str(write_evidence(Path(policy["log_rotation"]["directory"]), evidence))
    return evidence


def execute_restore(config_path: Path, policy: dict, artifact: str | None) -> dict:
    root = Path(policy["source"]["runtime_root"])
    with private_workspace(Path(policy["source"]["runtime_directory"])) as work:
        with pause_transfer(root):
            names, _ = _remote_listing(policy)
            name = artifact or (names[-1] if names else None)
            if name is None:
                raise BackupPolicyError("no encrypted remote artifact is available")
            if not STAMP_RE.fullmatch(name) or artifact_time(name) is None:
                raise BackupPolicyError("restore artifact name is nonconforming")
            ciphertext = work / name
            archive = work / "snapshot.tar"
            sftp_download(policy, _remote_path(policy, name), ciphertext,
                          policy["archive_limits"]["max_bytes"])
        decrypt(ciphertext, archive, policy)
        validate_archive_bounds(archive, policy["archive_limits"])
        snapshot = extract_snapshot(archive, work / "extract")
        with contextlib.redirect_stdout(io.StringIO()):
            runtime_module().restore(root, snapshot)
    evidence = {"schema_version": 1, "operation": "restore", "status": "succeeded",
                "artifact": name, "encrypted": True, "remote_downloaded": True,
                "local_restore": True, "off_host_restore": "pending live evidence",
                "policy_id": policy["id"], "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    evidence["evidence_path"] = str(write_evidence(Path(policy["log_rotation"]["directory"]), evidence))
    return evidence


def restore_drill(root: Path, snapshot: Path) -> None:
    runtime = runtime_module()
    root_identity = _directory_identity(root, "restore drill root")
    snapshot_identity = _directory_identity(snapshot, "restore drill snapshot")
    with tempfile.TemporaryDirectory(prefix="recursion-restore-drill-") as temporary:
        target = Path(temporary) / "root"
        if _directory_identity(root, "restore drill root") != root_identity \
                or _directory_identity(snapshot, "restore drill snapshot") != snapshot_identity:
            raise BackupPolicyError("restore drill input directory changed before use")
        shutil.copytree(root, target, symlinks=True)
        if _directory_identity(snapshot, "restore drill snapshot") != snapshot_identity:
            raise BackupPolicyError("restore drill snapshot changed before restore")
        with contextlib.redirect_stdout(io.StringIO()):
            runtime.restore(target, snapshot)
        manifest = runtime.load_manifest(snapshot)
        observed = {item.relative_to(target).as_posix(): runtime.digest(item)
                    for item in runtime.collect_files(target)}
        expected = {item["path"]: item["sha256"] for item in manifest["files"]}
        if observed != expected:
            raise BackupPolicyError("restore drill did not reconstruct the manifest inventory")
    print(json.dumps({"status": "prepared", "files": len(expected), "temporary_target": "discarded",
                      "production_proven": False}, sort_keys=True))


def _safe_cli_message(exc: BaseException) -> str:
    """Expose only fixed, useful refusal classes; never reflect paths or OS text."""
    if not isinstance(exc, BackupPolicyError):
        return "operation refused"
    message = str(exc)
    if message == "backup policy is disabled":
        return message
    if message == "mutating backup commands require explicit --execute":
        return message
    if message in {
        "PAUSE admission is unavailable",
        "PAUSE admission is absent; refusing external transfer",
        "PAUSE transfer admission failed",
        "authenticated policy signature is unreadable",
        "authenticated policy signature has invalid shape",
        "authenticated policy signature does not match",
    }:
        return message
    if re.fullmatch(r"backup tool arguments are invalid: (?:age|sftp)", message):
        return "backup tool arguments are invalid"
    return "operation refused"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="backup-offsite")
    parser.add_argument("--config", type=Path,
                        default=Path(__file__).resolve().parents[1] / "deploy/backup/recursion-offsite.json")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("plan")
    drill = sub.add_parser("restore-drill")
    drill.add_argument("--root", type=Path, required=True)
    drill.add_argument("--snapshot", type=Path, required=True)
    backup = sub.add_parser("backup")
    backup.add_argument("--execute", action="store_true")
    restore = sub.add_parser("restore")
    restore.add_argument("--execute", action="store_true")
    restore.add_argument("--artifact")
    reconcile = sub.add_parser("reconcile")
    reconcile.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = load_policy(args.config)
        if args.command == "validate":
            print(json.dumps({"id": policy["id"], "enabled": policy["enabled"]}, sort_keys=True))
        elif args.command == "plan":
            print(json.dumps({"enabled": policy["enabled"], "explicit_execute_required": True,
                              "steps": [["runtime-state.py", "backup", "tmpfs-runtime-snapshot"],
                                         ["age", "--encrypt", "--recipient-file", "<recipient-file>"],
                                         ["sftp", "put", "<encrypted-snapshot>", policy["destination"]["path"]],
                                         ["retention", "daily=%d" % policy["retention"]["daily"],
                                          "weekly=%d" % policy["retention"]["weekly"],
                                          "monthly=%d" % policy["retention"]["monthly"]]],
                              "archive_limits": policy["archive_limits"],
                              "nonconforming_remote_policy": "delete only bounded safe names; refuse ambiguous names",
                              "execution": "disabled-until-explicit-enable-and-execute",
                              "off_host_restore": "pending live evidence"}, sort_keys=True))
        elif args.command == "restore-drill":
            restore_drill(args.root, args.snapshot)
        else:
            require_execution(args.config, policy, args.execute)
            if args.command == "backup":
                print(json.dumps(execute_backup(args.config, policy), sort_keys=True))
            elif args.command == "restore":
                print(json.dumps(execute_restore(args.config, policy, args.artifact), sort_keys=True))
            else:
                retention = reconcile_remote(policy)
                evidence = {"schema_version": 1, "operation": "reconcile", "status": "succeeded",
                            "retention": retention, "policy_id": policy["id"],
                            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                evidence["evidence_path"] = str(write_evidence(Path(policy["log_rotation"]["directory"]), evidence))
                print(json.dumps(evidence, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, UnicodeError, OverflowError, BackupPolicyError,
            tarfile.TarError, RecursionError, subprocess.TimeoutExpired,
            subprocess.SubprocessError) as exc:
        print(f"backup-offsite: {_safe_cli_message(exc)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

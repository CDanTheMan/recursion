#!/usr/bin/env python3
"""Small runtime-dir credential-file lifecycle helper.

Files produced here contain environment secrets for a short-lived systemd unit.  The directory
is intended to be tmpfs-backed.  Names carry the creating process identity so a later controller
startup can remove files left behind by SIGKILL or a host crash without deleting a live worker's
file.  Secret contents never appear in stdout, stderr, or evidence.
"""

from __future__ import annotations

import argparse
import os
import re
import secrets
import stat
import sys
from pathlib import Path


NAME_RE = re.compile(r"^\.secret\.(\d+)\.(\d+)\.[0-9a-f]{16}$")
DEFAULT_RUNTIME_ROOTS = (Path("/run/recursion-runner"), Path("/run/recursion-backup"))
MAX_SECRET_ENV_BYTES = 1024 * 1024


class SecretRuntimeError(ValueError):
    """A secret runtime path or lifecycle operation is unsafe."""


class SecretRuntimeCleanupError(SecretRuntimeError):
    """A secret could not be removed durably; the caller must remain non-green."""


def process_start(pid: int) -> str | None:
    if isinstance(pid, bool) or not isinstance(pid, int) or pid < 1:
        return None
    if os.name == "nt":
        # The production proof runs on Linux (/proc start times).  Windows review fixtures still
        # get PID-scoped cleanup; a PID other than this process is considered stale.
        return str(pid) if pid == os.getpid() else None
    try:
        with Path(f"/proc/{pid}/stat").open("rb") as source:
            raw = source.read(4097).decode("ascii", "strict")
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    tail = raw.rsplit(")", 1)[-1].split()
    return tail[19] if len(tail) > 19 else None


def _approved_root(directory: Path) -> Path:
    configured = os.environ.get("RECURSION_SECRET_RUNTIME_ROOT", "").strip()
    roots = (Path(configured),) if configured else DEFAULT_RUNTIME_ROOTS
    _reject_reparse_components(directory, "secret runtime directory")
    for root in roots:
        if not root.is_absolute() or any(part in {".", ".."} for part in root.parts):
            continue
        if directory == root:
            return root
    raise SecretRuntimeError("secret runtime directory is not an approved canonical runtime root")


def _reject_reparse_components(path: Path, label: str) -> None:
    if not isinstance(path, Path) or not path.is_absolute():
        raise SecretRuntimeError(f"{label} must be an absolute path")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise SecretRuntimeError(f"{label} is unreadable") from exc
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) \
                or (getattr(info, "st_file_attributes", 0) & 0x400):
            raise SecretRuntimeError(f"{label} contains a symlink/reparse component")


def _validate_component(path: Path, label: str, *, final: bool = False) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) \
            or (getattr(info, "st_file_attributes", 0) & 0x400):
        raise SecretRuntimeError(f"{label} contains a symlink/reparse component")
    if not stat.S_ISDIR(info.st_mode):
        raise SecretRuntimeError(f"{label} contains a non-directory component")
    mode = stat.S_IMODE(info.st_mode)
    if os.name != "nt" and ((final and mode & 0o077) or (not final and mode & 0o022)):
        raise SecretRuntimeError(f"{label} is group/other accessible")
    if os.name != "nt" and not final and mode & 0o002 and not (mode & stat.S_ISVTX):
        raise SecretRuntimeError(f"{label} is world-writable without sticky confinement")
    if hasattr(os, "geteuid") and os.geteuid() == 0 and info.st_uid != 0:
        raise SecretRuntimeError(f"{label} is not root-owned")


def ensure_directory(directory: Path) -> None:
    if not directory.is_absolute() or any(part in {".", ".."} for part in directory.parts):
        raise SecretRuntimeError("secret runtime directory must be canonical and absolute")
    _reject_reparse_components(directory, "secret runtime directory")
    root = _approved_root(directory)
    current = Path(root.anchor)
    for component in root.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            current.mkdir(mode=0o700)
        except OSError as exc:
            raise SecretRuntimeError("secret runtime parent is unreadable") from exc
        _validate_component(current, "secret runtime parent", final=current == root)
    _validate_component(root, "secret runtime directory", final=True)


def scavenge(directory: Path, current_pid: int | None = None) -> int:
    ensure_directory(directory)
    current_pid = os.getpid() if current_pid is None else current_pid
    current_start = process_start(current_pid)
    removed = 0
    for path in directory.iterdir():
        match = NAME_RE.fullmatch(path.name)
        if not match:
            if path.name.startswith(".secret."):
                _validate_secret_file(path)
                _remove_secret(path)
                removed += 1
            continue
        _validate_secret_file(path)
        try:
            pid = int(match.group(1))
        except (ValueError, OverflowError):
            raise SecretRuntimeError("secret runtime contains an invalid process identity") from None
        if len(match.group(1)) > 20:
            raise SecretRuntimeError("secret runtime contains an invalid process identity")
        start = match.group(2)
        if pid == current_pid and current_start == start:
            continue
        observed = process_start(pid)
        if observed is None or observed != start:
            _remove_secret(path)
            removed += 1
    return removed


def _validate_secret_file(path: Path) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) \
            or (getattr(info, "st_file_attributes", 0) & 0x400):
        raise SecretRuntimeError("secret runtime contains a symlink/reparse file")
    if not stat.S_ISREG(info.st_mode):
        raise SecretRuntimeError("secret runtime contains a non-regular secret file")
    if os.name != "nt" and (stat.S_IMODE(info.st_mode) & 0o077 or stat.S_IMODE(info.st_mode) != 0o600):
        raise SecretRuntimeError("secret runtime file permissions are unsafe")
    if hasattr(os, "geteuid") and os.geteuid() == 0 and info.st_uid != 0:
        raise SecretRuntimeError("secret runtime file is not root-owned")


def _remove_secret(path: Path) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) \
            or (getattr(info, "st_file_attributes", 0) & 0x400):
        raise SecretRuntimeCleanupError("refusing to remove a symlink/reparse secret path")
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except OSError as exc:
        raise SecretRuntimeCleanupError(f"secret cleanup failed for {path.name}") from exc
    if os.name != "nt":
        try:
            descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        except OSError as exc:
            raise SecretRuntimeCleanupError(f"secret cleanup durability failed for {path.name}") from exc


def write_env(directory: Path, content: bytes) -> Path:
    if not isinstance(content, bytes) or not content:
        raise ValueError("secret environment is empty")
    if len(content) > MAX_SECRET_ENV_BYTES:
        raise ValueError("secret environment is too large")
    if b"\x00" in content:
        raise ValueError("secret environment contains NUL")
    ensure_directory(directory)
    start = process_start(os.getpid()) or "unknown"
    if not start.isdigit():
        raise ValueError("cannot witness current process identity")
    name = f".secret.{os.getpid()}.{start}.{secrets.token_hex(8)}"
    path = directory / name
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            info = path.stat()
            if info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o600:
                raise ValueError("secret environment ownership is unsafe")
        _validate_secret_file(path)
        return path
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            _remove_secret(path)
        except SecretRuntimeCleanupError:
            raise
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="secret-runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("scavenge", "write-env"):
        command = sub.add_parser(name)
        command.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "scavenge":
            scavenge(args.directory)
        else:
            print(write_env(args.directory, sys.stdin.buffer.read()))
        return 0
    except (OSError, ValueError, TypeError, UnicodeError, OverflowError, RecursionError,
            SecretRuntimeError):
        print("secret-runtime: operation refused", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

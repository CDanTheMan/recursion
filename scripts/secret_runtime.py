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


def process_start(pid: int) -> str | None:
    if os.name == "nt":
        # The production proof runs on Linux (/proc start times).  Windows review fixtures still
        # get PID-scoped cleanup; a PID other than this process is considered stale.
        return str(pid) if pid == os.getpid() else None
    try:
        raw = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError):
        return None
    tail = raw.rsplit(")", 1)[-1].split()
    return tail[19] if len(tail) > 19 else None


def ensure_directory(directory: Path) -> None:
    if not directory.is_absolute():
        raise ValueError("secret runtime directory must be absolute")
    if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
        raise ValueError("secret runtime directory has an unsafe type")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    if hasattr(os, "geteuid") and os.geteuid() == 0 and directory.stat().st_uid != 0:
        raise ValueError("secret runtime directory is not root-owned")


def scavenge(directory: Path, current_pid: int | None = None) -> int:
    ensure_directory(directory)
    current_pid = os.getpid() if current_pid is None else current_pid
    current_start = process_start(current_pid)
    removed = 0
    for path in directory.iterdir():
        match = NAME_RE.fullmatch(path.name)
        if not match:
            if path.name.startswith(".secret."):
                path.unlink(missing_ok=True)
                removed += 1
            continue
        pid, start = int(match.group(1)), match.group(2)
        if pid == current_pid and current_start == start:
            continue
        observed = process_start(pid)
        if observed is None or observed != start:
            if path.is_symlink() or not path.is_file():
                path.unlink(missing_ok=True)
            else:
                path.unlink()
            removed += 1
    return removed


def write_env(directory: Path, content: bytes) -> Path:
    if not content:
        raise ValueError("secret environment is empty")
    if b"\x00" in content:
        raise ValueError("secret environment contains NUL")
    ensure_directory(directory)
    start = process_start(os.getpid()) or "unknown"
    if not start.isdigit():
        raise ValueError("cannot witness current process identity")
    name = f".secret.{os.getpid()}.{start}.{secrets.token_hex(8)}"
    path = directory / name
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
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
        return path
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        path.unlink(missing_ok=True)
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
    except (OSError, ValueError) as exc:
        print(f"secret-runtime: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

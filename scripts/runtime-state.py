#!/usr/bin/env python3
"""Rotate, back up, and restore ignored Recursion runtime state.

All mutating commands require state/PAUSE and a fail-closed runtime-state lock. Secrets, deploy
keys, repositories, and the Hermes SQLite database are intentionally outside this file backup;
the Phase 0 runbook retains their separate human-controlled procedures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


RUNTIME_PATHS = (
    "state/PAUSE",
    "state/events.jsonl",
    "state/action-events.jsonl",
    "state/actions",
    "state/instructions",
    "state/pilot-requests",
    "state/runs",
    "state/evidence",
    "state/recovery",
    "state/deliveries",
    "state/escalations.tsv",
    "state/.intake-watermark",
    "state/event-archive",
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def fsync_dir(path: Path) -> None:
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


class RuntimeLock:
    def __init__(self, root: Path) -> None:
        self.path = root / "state/.locks/runtime-state.lock"
        self.held = False

    def __enter__(self) -> "RuntimeLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        attempts = int(os.environ.get("RECURSION_LOCK_ATTEMPTS", "100"))
        delay = float(os.environ.get("RECURSION_LOCK_DELAY_S", "0.1"))
        for _ in range(attempts):
            try:
                self.path.mkdir()
                atomic_bytes(self.path / "owner", f"{os.getpid()}\n".encode())
                self.held = True
                return self
            except FileExistsError:
                time.sleep(delay)
        raise RuntimeError("runtime-state lock is contended; refusing an unlocked mutation")

    def __exit__(self, *_: object) -> None:
        if not self.held:
            return
        (self.path / "owner").unlink(missing_ok=True)
        self.path.rmdir()
        self.held = False


class EmptyLock:
    """Compatibility lock for taskctl's empty mkdir mutex."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.held = False

    def __enter__(self) -> "EmptyLock":
        attempts = int(os.environ.get("RECURSION_LOCK_ATTEMPTS", "100"))
        delay = float(os.environ.get("RECURSION_LOCK_DELAY_S", "0.1"))
        for _ in range(attempts):
            try:
                self.path.mkdir()
                self.held = True
                return self
            except FileExistsError:
                time.sleep(delay)
        raise RuntimeError(f"{self.path.name} is contended; refusing an unlocked snapshot")

    def __exit__(self, *_: object) -> None:
        if self.held:
            self.path.rmdir()
            self.held = False


def assert_no_execution_locks(root: Path) -> None:
    lock_dir = root / "state/.locks"
    active = sorted(
        path.name
        for pattern in ("action-*.lock", "ws-*.lock", "ledger.lock", "heavy-gate.lock")
        for path in lock_dir.glob(pattern)
    )
    if active:
        raise RuntimeError("execution/state locks remain under PAUSE: " + ", ".join(active))


def require_pause(root: Path) -> Path:
    pause = root / "state/PAUSE"
    if not pause.is_file():
        raise RuntimeError("state/PAUSE is absent; refusing runtime-state maintenance")
    return pause


def ensure_outside_root(root: Path, path: Path) -> None:
    resolved_root = root.resolve()
    resolved = path.resolve(strict=False)
    if resolved == resolved_root or resolved_root in resolved.parents:
        raise RuntimeError("snapshot paths must be outside the Recursion checkout")


def rotate_events(root: Path, maximum: int) -> None:
    require_pause(root)
    events = root / "state/events.jsonl"
    if not events.exists() or events.stat().st_size <= maximum:
        print(f"rotation not needed ({events.stat().st_size if events.exists() else 0} <= {maximum})")
        return
    with RuntimeLock(root), EmptyLock(root / "state/.locks/taskctl.lock"):
        require_pause(root); assert_no_execution_locks(root)
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
    for relative in RUNTIME_PATHS:
        path = root / relative
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(item for item in path.rglob("*") if item.is_file()))
    return sorted(set(files))


def backup(root: Path, destination: Path) -> None:
    pause = require_pause(root)
    ensure_outside_root(root, destination)
    if destination.exists():
        raise RuntimeError(f"backup destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(destination.name + f".tmp.{os.getpid()}")
    if staging.exists():
        raise RuntimeError(f"backup staging path already exists: {staging}")
    with RuntimeLock(root), EmptyLock(root / "state/.locks/taskctl.lock"):
        require_pause(root); assert_no_execution_locks(root)
        staging.mkdir(mode=0o700)
        records = []
        for source in collect_files(root):
            relative = source.relative_to(root)
            target = staging / "files" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            records.append({
                "path": relative.as_posix(),
                "sha256": digest(target),
                "size": target.stat().st_size,
                "mode": oct(target.stat().st_mode & 0o777),
                "uid": target.stat().st_uid,
                "gid": target.stat().st_gid,
            })
        try:
            commit = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            commit = "unavailable"
        manifest = {
            "schema_version": 1,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "commit": commit,
            "pause_sha256": digest(pause),
            "files": records,
            "locks_observed": sorted(item.name for item in (root / "state/.locks").iterdir()),
        }
        atomic_bytes(
            staging / "manifest.json",
            (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
        )
        fsync_dir(staging)
        os.replace(staging, destination)
        fsync_dir(destination.parent)
    print(f"backup {destination} files={len(records)} pause_sha256={manifest['pause_sha256']}")


def load_manifest(snapshot: Path) -> dict:
    manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), list):
        raise RuntimeError("unsupported or malformed backup manifest")
    for record in manifest["files"]:
        relative = Path(record["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"unsafe manifest path: {relative}")
        source = snapshot / "files" / relative
        if not source.is_file() or digest(source) != record["sha256"]:
            raise RuntimeError(f"backup hash mismatch: {relative}")
    return manifest


def restore(root: Path, snapshot: Path) -> None:
    require_pause(root)
    ensure_outside_root(root, snapshot)
    manifest = load_manifest(snapshot)
    pause_record = next((item for item in manifest["files"] if item["path"] == "state/PAUSE"), None)
    if not pause_record:
        raise RuntimeError("backup does not contain state/PAUSE")
    with RuntimeLock(root), EmptyLock(root / "state/.locks/taskctl.lock"):
        require_pause(root); assert_no_execution_locks(root)
        ordered = sorted(manifest["files"], key=lambda item: item["path"] != "state/PAUSE")
        for record in ordered:
            relative = Path(record["path"])
            source = snapshot / "files" / relative
            target = root / relative
            atomic_bytes(target, source.read_bytes(), int(record["mode"], 8))
            if os.geteuid() == 0:
                os.chown(target, int(record["uid"]), int(record["gid"]))
        require_pause(root)
    print(f"restore {snapshot} files={len(manifest['files'])} pause_sha256={manifest['pause_sha256']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    rotate = subparsers.add_parser("rotate-events")
    rotate.add_argument("--max-bytes", type=int, default=10 * 1024 * 1024)
    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("destination", type=Path)
    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    root = Path(os.environ.get("RECURSION_ROOT", Path(__file__).resolve().parents[1])).resolve()
    try:
        if args.command == "rotate-events":
            rotate_events(root, args.max_bytes)
        elif args.command == "backup":
            backup(root, args.destination)
        else:
            restore(root, args.snapshot)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"runtime-state: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

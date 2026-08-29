#!/usr/bin/env python3
"""Stage a declared engine runtime tree without following links out of it.

This is deliberately a small, offline helper.  The controller supplies a source
directory obtained from the reviewed engine plan and a destination inside the
disposable worktree.  Only regular files and directories are copied; symlinks,
devices, sockets, and FIFOs are refused so a wrapper cannot smuggle a host path
or socket into the worker namespace.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

class FirstPartyImportError(ImportError):
    """A required controller module is absent or malformed in the importing tree."""


try:
    from phase5_safety import (BoundaryError, atomic_write, chmod_directory,
                               ensure_directory, pinned_directory, read_bytes, verify_leaf)
except Exception as exc:
    module_name = getattr(exc, "name", None) or "phase5_safety"
    import_error = FirstPartyImportError(
        f"first-party module '{module_name}' is unavailable or malformed; searched {_SCRIPT_DIR}"
    )
    if __name__ == "__main__":
        print(f"runtime-layout: first-party import failed: {import_error}", file=sys.stderr)
        raise SystemExit(95)
    raise import_error from None


class LayoutError(Exception):
    pass


def _is_link_or_reparse(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _safe_source(path: Path) -> Path:
    if not path.is_absolute():
        raise LayoutError("runtime source must be an absolute path")
    try:
        with pinned_directory(path) as (_, absolute):
            source = Path(absolute)
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        raise LayoutError(f"runtime source is unavailable: {path}") from exc
    return source


def _git_index_metadata(source: Path) -> dict[str, int] | None:
    """Return tracked mode metadata for *source*, or None when it is not in Git.

    Git can check out a mode-120000 blob as an ordinary file when core.symlinks is
    false.  lstat() alone therefore cannot establish that a runtime tree is link-free.
    The index is the source-of-truth for a checked-out tree, so retain its mode for
    every tracked path below the source directory and compare it during the walk.
    """
    probe = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=False,
    )
    if probe.returncode != 0:
        marker = source
        while marker != marker.parent:
            if (marker / ".git").exists():
                raise LayoutError("runtime source Git root could not be inspected")
            marker = marker.parent
        return None
    try:
        repo = Path(os.path.abspath(probe.stdout.strip()))
        relative_source = source.relative_to(repo)
    except (OSError, ValueError):
        raise LayoutError("runtime source Git root could not be canonicalized")
    prefix = relative_source.as_posix().rstrip("/")
    if prefix == ".":
        prefix = ""
    listed = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--stage", "-z", "--"],
        capture_output=True, check=False,
    )
    if listed.returncode != 0:
        raise LayoutError("runtime source Git index could not be inspected")
    metadata: dict[str, int] = {}
    for record in listed.stdout.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", 1)
            mode_text = header.split(None, 1)[0].decode("ascii")
            tracked = raw_path.decode("utf-8", "surrogateescape")
            mode = int(mode_text, 8)
        except (ValueError, UnicodeDecodeError, TypeError, OverflowError):
            raise LayoutError("runtime source Git index contains malformed metadata")
        if prefix:
            if tracked == prefix:
                relative = Path(".")
            elif tracked.startswith(prefix + "/"):
                relative = Path(tracked[len(prefix) + 1 :])
            else:
                continue
        else:
            relative = Path(tracked)
        metadata[relative.as_posix()] = mode
    # A checked-out index can be deliberately altered.  The committed tree is an
    # independent witness: a runtime source is refused if either Git authority says
    # that an entry is a symlink or gitlink.
    tree = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "-z", "HEAD", "--"],
        capture_output=True, check=False,
    )
    if tree.returncode == 0:
        for record in tree.stdout.split(b"\0"):
            if not record:
                continue
            try:
                header, raw_path = record.split(b"\t", 1)
                mode = int(header.split(None, 1)[0].decode("ascii"), 8)
                tracked = raw_path.decode("utf-8", "surrogateescape")
            except (ValueError, UnicodeDecodeError, TypeError, OverflowError):
                raise LayoutError("runtime source Git tree contains malformed metadata")
            if prefix and not (tracked == prefix or tracked.startswith(prefix + "/")):
                continue
            relative = Path(tracked[len(prefix) + 1 :] if prefix and tracked != prefix else ("." if prefix else tracked))
            metadata[relative.as_posix()] = max(metadata.get(relative.as_posix(), 0), mode)
    elif tree.returncode not in (128, 129):
        raise LayoutError("runtime source Git tree could not be inspected")
    return metadata


def _entry_metadata(source: Path) -> dict[str, int] | None:
    try:
        return _git_index_metadata(source)
    except FileNotFoundError:
        # A non-Git source is still checked strictly with lstat().  Only a missing
        # Git executable is treated as non-Git; a detected repository is fail-closed.
        return None


def _remove_created_tree(path: Path) -> None:
    """Best-effort cleanup that never follows a swapped junction/reparse point."""
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return
    except (OSError, ValueError, TypeError):
        return
    if _is_link_or_reparse(path) or not stat.S_ISDIR(info.st_mode):
        return
    try:
        shutil.rmtree(path, ignore_errors=True)
    except (OSError, ValueError, TypeError):
        return


def _scan_tree(source: Path):
    """Yield one directory at a time while its no-follow directory handle is held.

    ``os.walk(..., followlinks=False)`` is not sufficient on Windows because a junction
    is not necessarily reported as a symlink.  The directory is therefore pinned before
    enumeration and every child is lstat'ed before it can be queued for descent.
    """
    pending = [source]
    while pending:
        current = pending.pop()
        try:
            with pinned_directory(current) as (descriptor, _):
                scan_target = descriptor if os.name != "nt" else current
                with os.scandir(scan_target) as iterator:
                    entries = list(iterator)
        except (BoundaryError, OSError, ValueError, TypeError, OverflowError,
                RecursionError) as exc:
            raise LayoutError(f"runtime tree could not be walked: {current}") from exc
        directories: list[str] = []
        files: list[str] = []
        for entry in entries:
            candidate = current / entry.name
            try:
                info = os.lstat(candidate)
            except (OSError, ValueError, TypeError) as exc:
                raise LayoutError(f"runtime tree entry disappeared: {candidate}") from exc
            mode = info.st_mode
            if _is_link_or_reparse(candidate):
                raise LayoutError(f"runtime tree contains a symlink or reparse point: {candidate}")
            if stat.S_ISDIR(mode):
                directories.append(entry.name)
            elif stat.S_ISREG(mode):
                files.append(entry.name)
            else:
                raise LayoutError(f"runtime tree contains a non-regular entry: {candidate}")
        yield current, directories, files
        pending.extend(current / name for name in reversed(directories))


def _safe_entrypoint(value: str) -> str:
    if not isinstance(value, str) or not value or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in value):
        raise LayoutError("runtime entrypoint must be a confined relative path")
    if "\\" in value or value.startswith("/") or ":" in value:
        raise LayoutError("runtime entrypoint must be a confined relative path")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise LayoutError("runtime entrypoint must be a confined relative path")
    return value


def _tree_snapshot(root: Path) -> dict[str, tuple]:
    """Return topology, identity, mode, and content for a link-free tree."""
    snapshot: dict[str, tuple] = {}
    for current, directories, files in _scan_tree(root):
        relative = current.relative_to(root).as_posix()
        try:
            info = os.lstat(current)
        except (OSError, ValueError, TypeError) as exc:
            raise LayoutError("runtime tree entry disappeared during final scan") from exc
        if _is_link_or_reparse(current) or not stat.S_ISDIR(info.st_mode):
            raise LayoutError("runtime tree changed into a non-directory during final scan")
        snapshot[relative] = (
            "dir", int(getattr(info, "st_dev", 0)), int(getattr(info, "st_ino", 0)),
            int(getattr(info, "st_nlink", 0)), stat.S_IMODE(info.st_mode),
        )
        for name in files:
            path = current / name
            try:
                before = os.lstat(path)
            except (OSError, ValueError, TypeError) as exc:
                raise LayoutError("runtime tree file disappeared during final scan") from exc
            if _is_link_or_reparse(path) or not stat.S_ISREG(before.st_mode) \
                    or int(getattr(before, "st_nlink", 0)) != 1:
                if int(getattr(before, "st_nlink", 0)) != 1:
                    raise LayoutError("runtime tree contains a hardlinked file during final scan")
                raise LayoutError("runtime tree contains an unsafe file during final scan")
            try:
                payload = read_bytes(path, label="runtime final scan")
                after = os.lstat(path)
            except (BoundaryError, OSError, ValueError, TypeError) as exc:
                raise LayoutError("runtime tree file could not be verified after locking") from exc
            if _is_link_or_reparse(path) or not stat.S_ISREG(after.st_mode) \
                    or int(getattr(after, "st_nlink", 0)) != 1 \
                    or (getattr(before, "st_dev", 0), getattr(before, "st_ino", 0),
                        getattr(before, "st_nlink", 0)) \
                    != (getattr(after, "st_dev", 0), getattr(after, "st_ino", 0),
                        getattr(after, "st_nlink", 0)):
                raise LayoutError("runtime tree file identity changed during final scan")
            snapshot[(current / name).relative_to(root).as_posix()] = (
                "file", int(getattr(after, "st_dev", 0)), int(getattr(after, "st_ino", 0)),
                int(getattr(after, "st_nlink", 0)), int(after.st_size),
                hashlib.sha256(payload).hexdigest(), stat.S_IMODE(after.st_mode),
            )
    return snapshot


def _identity_view(snapshot: dict[str, tuple]) -> dict[str, tuple]:
    return {
        path: (entry[0], entry[1], entry[2], entry[3])
        for path, entry in snapshot.items()
    }


def _content_view(snapshot: dict[str, tuple]) -> dict[str, tuple]:
    return {
        path: ((entry[0],) if entry[0] == "dir"
               else (entry[0], entry[4], entry[5]))
        for path, entry in snapshot.items()
    }


def _assert_locked(snapshot: dict[str, tuple]) -> None:
    # Windows ACLs, not POSIX directory mode bits, seal directories.  Files are
    # still published with the read-only attribute by atomic_write and remain
    # checked on both platforms.
    writable = [path for path, entry in snapshot.items()
                if (os.name != "nt" or entry[0] == "file") and entry[-1] & 0o222]
    if writable:
        raise LayoutError("runtime tree remained writable after locking")


def _copy_tree(source: Path, destination: Path, entrypoint: str | None = None) -> None:
    created = False
    directories_to_lock: list[Path] = []
    locked_directories: list[Path] = []
    try:
        source = _safe_source(source)
        destination = Path(destination)
        if not destination.is_absolute():
            raise LayoutError("runtime destination must be absolute")
        if entrypoint:
            entrypoint = _safe_entrypoint(entrypoint)
        source_before = _tree_snapshot(source)
        ensure_directory(destination.parent)
        with pinned_directory(source), pinned_directory(destination.parent) as (destination_parent_fd, _):
            metadata = _entry_metadata(source)
            try:
                if os.name == "nt":
                    # Python's POSIX mode argument can map to a restrictive ACL
                    # under Git Bash; Windows sealing is handled by ACLs, while
                    # the private POSIX mode below closes the staging window.
                    os.mkdir(destination)
                else:
                    # Keep the complete staged tree inaccessible to other users
                    # until every child has been published and verified.
                    os.mkdir(os.path.basename(str(destination)), 0o700, dir_fd=destination_parent_fd)
            except FileExistsError as exc:
                raise LayoutError(f"runtime destination already exists: {destination}") from exc
            created = True
            try:
                # Every directory is pinned without following links before it is
                # enumerated, and every file is copied from a single verified handle,
                # so a pre-walk lstat cannot be raced into a hardlink/reparse.
                for current, directories, files in _scan_tree(source):
                    current_path = Path(current)
                    for name in list(directories) + list(files):
                        candidate = current_path / name
                        try:
                            info = os.lstat(candidate)
                        except OSError as exc:
                            raise LayoutError(f"runtime tree entry disappeared: {candidate}") from exc
                        mode = info.st_mode
                        if _is_link_or_reparse(candidate):
                            raise LayoutError(f"runtime tree contains a symlink or reparse point: {candidate}")
                        if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                            raise LayoutError(f"runtime tree contains a non-regular entry: {candidate}")
                        if stat.S_ISREG(mode) and int(getattr(info, "st_nlink", 0)) != 1:
                            raise LayoutError(f"runtime tree contains a hardlinked file: {candidate}")
                        if metadata is not None:
                            relative_entry = candidate.relative_to(source).as_posix()
                            git_mode = metadata.get(relative_entry)
                            if git_mode in (0o120000, 0o160000):
                                raise LayoutError(f"runtime tree Git metadata marks {candidate} as a link/gitlink")
                            if git_mode is not None and not stat.S_ISREG(mode):
                                raise LayoutError(f"runtime tree entry disagrees with Git metadata: {candidate}")
                    relative = current_path.relative_to(source)
                    target_dir = destination / relative
                    ensure_directory(target_dir)
                    chmod_directory(target_dir, 0o700)
                    directories_to_lock.append(target_dir)
                    for name in files:
                        source_file = current_path / name
                        target_file = target_dir / name
                        source_info = os.lstat(source_file)
                        if _is_link_or_reparse(source_file) or not stat.S_ISREG(source_info.st_mode) \
                                or int(getattr(source_info, "st_nlink", 0)) != 1:
                            raise LayoutError(f"runtime source file is not a single-link regular file: {source_file}")
                        source_mode = stat.S_IMODE(source_info.st_mode)
                        if entrypoint and source_file.relative_to(source).as_posix() == entrypoint \
                                and os.name != "nt" and not (source_mode & 0o111):
                            raise LayoutError("runtime entrypoint is not executable")
                        # read_bytes pins the parent, opens no-follow, checks file-id,
                        # link count, and reparse state immediately around the copy.
                        payload = read_bytes(source_file, label="runtime source")
                        atomic_write(
                            target_file, payload, replace=False,
                            mode=(source_mode & 0o555) | (0o444 if source_mode & 0o444 else 0),
                            label="runtime destination",
                        )
            except BaseException:
                _remove_created_tree(destination)
                raise
        if entrypoint:
            candidate = destination / entrypoint
            try:
                entry_info = verify_leaf(candidate, allow_directory=False)
            except (BoundaryError, OSError, ValueError, TypeError) as exc:
                _remove_created_tree(destination)
                raise LayoutError("runtime entrypoint is not a regular file") from exc
            if entry_info is None or not stat.S_ISREG(entry_info.st_mode) \
                    or int(getattr(entry_info, "st_nlink", 0)) != 1:
                _remove_created_tree(destination)
                raise LayoutError("runtime entrypoint is not a regular file")
            if os.name != "nt" and not (stat.S_IMODE(entry_info.st_mode) & 0o111):
                _remove_created_tree(destination)
                raise LayoutError("runtime entrypoint is not executable")

        source_after_copy = _tree_snapshot(source)
        if _identity_view(source_before) != _identity_view(source_after_copy) \
                or _content_view(source_before) != _content_view(source_after_copy):
            raise LayoutError("runtime source changed during staging")
        before_lock = _tree_snapshot(destination)
        for target_dir in directories_to_lock:
            chmod_directory(target_dir, 0o555)
            locked_directories.append(target_dir)

        # The final scan is deliberately after the lock.  It proves that no entry
        # disappeared, appeared, or changed identity/content across publication and
        # sealing, and that every directory and file is actually non-writable.
        source_after_lock = _tree_snapshot(source)
        after_lock = _tree_snapshot(destination)
        if _identity_view(source_after_copy) != _identity_view(source_after_lock) \
                or _content_view(source_after_copy) != _content_view(source_after_lock):
            raise LayoutError("runtime source changed while staging was sealed")
        if _identity_view(before_lock) != _identity_view(after_lock) \
                or _content_view(before_lock) != _content_view(after_lock):
            raise LayoutError("runtime tree changed while staging was sealed")
        if _content_view(source_after_lock) != _content_view(after_lock):
            raise LayoutError("staged runtime is incomplete or differs from its source")
        _assert_locked(after_lock)
    except BaseException:
        # A failed post-lock verification must not leave a half-published destination
        # that blocks recovery.  Re-open write permission only for this owner's
        # immediate cleanup; successful returns never pass through this branch.
        for target_dir in reversed(locked_directories):
            try:
                chmod_directory(target_dir, 0o700)
            except (BoundaryError, OSError, ValueError, TypeError):
                pass
        if created:
            _remove_created_tree(destination)
        raise


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="runtime-layout")
    parser.add_argument("stage", choices=("stage",))
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--entrypoint")
    args = parser.parse_args(argv)
    try:
        source = _safe_source(Path(args.source))
        destination = Path(args.destination)
        if not destination.is_absolute():
            raise LayoutError("runtime destination must be absolute")
        if args.entrypoint:
            _safe_entrypoint(args.entrypoint)
        _copy_tree(source, destination, args.entrypoint)
    except (LayoutError, BoundaryError, OSError, ValueError, TypeError,
            OverflowError, RecursionError, UnicodeDecodeError):
        # Refusals are intentionally symbolic.  The source and destination are
        # caller-controlled paths and must not be echoed into the boundary log.
        print("runtime-layout: invalid runtime staging input", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except FirstPartyImportError as exc:
        print(f"runtime-layout: first-party import failed: {exc}", file=sys.stderr)
        raise SystemExit(95)

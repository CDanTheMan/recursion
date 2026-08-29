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
    """A required controller module is absent from the importing script's tree."""


try:
    from phase5_safety import (BoundaryError, atomic_write, chmod_directory,
                               ensure_directory, pinned_directory, read_bytes, verify_leaf)
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    import_error = FirstPartyImportError(
        f"first-party module 'phase5_safety' not found; searched {_SCRIPT_DIR}"
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


def _copy_tree(source: Path, destination: Path, entrypoint: str | None = None) -> None:
    created = False
    try:
        source = _safe_source(source)
        destination = Path(destination)
        if not destination.is_absolute():
            raise LayoutError("runtime destination must be absolute")
        if entrypoint:
            entrypoint = _safe_entrypoint(entrypoint)
        ensure_directory(destination.parent)
        with pinned_directory(source), pinned_directory(destination.parent) as (destination_parent_fd, _):
            metadata = _entry_metadata(source)
            try:
                if os.name == "nt":
                    os.mkdir(destination)
                else:
                    os.mkdir(os.path.basename(str(destination)), dir_fd=destination_parent_fd)
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
                    chmod_directory(target_dir, 0o555)
                    for name in files:
                        source_file = current_path / name
                        target_file = target_dir / name
                        source_info = os.lstat(source_file)
                        if _is_link_or_reparse(source_file) or not stat.S_ISREG(source_info.st_mode) \
                                or int(getattr(source_info, "st_nlink", 0)) != 1:
                            raise LayoutError(f"runtime source file is not a single-link regular file: {source_file}")
                        source_mode = stat.S_IMODE(source_info.st_mode)
                        if entrypoint and candidate.relative_to(source).as_posix() == entrypoint \
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
    except BaseException:
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
            OverflowError, RecursionError, UnicodeDecodeError) as exc:
        print(f"runtime-layout: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except FirstPartyImportError as exc:
        print(f"runtime-layout: first-party import failed: {exc}", file=sys.stderr)
        raise SystemExit(95)

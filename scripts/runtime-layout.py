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


class LayoutError(Exception):
    pass


def _is_link_or_reparse(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _safe_source(path: Path) -> Path:
    if _is_link_or_reparse(path):
        raise LayoutError("runtime source must not be a symlink or reparse point")
    try:
        source = path.resolve(strict=True)
    except OSError as exc:
        raise LayoutError(f"runtime source is unavailable: {path}") from exc
    if not source.is_dir():
        raise LayoutError("runtime source is not a directory")
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
        repo = Path(probe.stdout.strip()).resolve(strict=True)
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
        except (ValueError, UnicodeDecodeError):
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
            except (ValueError, UnicodeDecodeError):
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
    for parent in destination.parents:
        if _is_link_or_reparse(parent):
            raise LayoutError(f"runtime destination has a symlinked parent: {parent}")
    if _is_link_or_reparse(destination) or destination.exists():
        raise LayoutError(f"runtime destination already exists: {destination}")
    metadata = _entry_metadata(source)
    canonical_destination = destination.resolve(strict=False)
    destination.mkdir(parents=True)
    try:
        for current, directories, files in os.walk(source, topdown=True, followlinks=False):
            current_path = Path(current)
            for name in list(directories) + list(files):
                candidate = current_path / name
                info = os.lstat(candidate)
                mode = info.st_mode
                if _is_link_or_reparse(candidate):
                    raise LayoutError(f"runtime tree contains a symlink: {candidate}")
                if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                    raise LayoutError(f"runtime tree contains a non-regular entry: {candidate}")
                if metadata is not None:
                    relative_entry = candidate.relative_to(source).as_posix()
                    git_mode = metadata.get(relative_entry)
                    if git_mode in (0o120000, 0o160000):
                        raise LayoutError(f"runtime tree Git metadata marks {candidate} as a link/gitlink")
                    if git_mode is not None and not stat.S_ISREG(mode):
                        raise LayoutError(f"runtime tree entry disagrees with Git metadata: {candidate}")
            relative = current_path.relative_to(source)
            target_dir = destination / relative
            target_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(target_dir, 0o555)
            for name in files:
                source_file = current_path / name
                target_file = target_dir / name
                shutil.copyfile(source_file, target_file, follow_symlinks=False)
                source_mode = stat.S_IMODE(os.lstat(source_file).st_mode)
                # Runtime files are always read-only to the runner; retain execute/read
                # intent but strip every write bit.
                os.chmod(target_file, (source_mode & 0o555) | (0o444 if source_mode & 0o444 else 0))
    except BaseException:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    if entrypoint:
        entrypoint = _safe_entrypoint(entrypoint)
        candidate = destination / entrypoint
        try:
            candidate.resolve(strict=False).relative_to(canonical_destination)
        except ValueError:
            shutil.rmtree(destination, ignore_errors=True)
            raise LayoutError("runtime entrypoint escapes the staged runtime")
        if _is_link_or_reparse(candidate) or not candidate.is_file():
            shutil.rmtree(destination, ignore_errors=True)
            raise LayoutError("runtime entrypoint is not a regular file")
        if os.name != "nt" and not (stat.S_IMODE(os.lstat(candidate).st_mode) & 0o111):
            shutil.rmtree(destination, ignore_errors=True)
            raise LayoutError("runtime entrypoint is not executable")


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
    except (LayoutError, OSError) as exc:
        print(f"runtime-layout: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

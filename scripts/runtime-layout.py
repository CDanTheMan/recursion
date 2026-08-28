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


def _copy_tree(source: Path, destination: Path, entrypoint: str | None = None) -> None:
    for parent in destination.parents:
        if _is_link_or_reparse(parent):
            raise LayoutError(f"runtime destination has a symlinked parent: {parent}")
    if _is_link_or_reparse(destination) or destination.exists():
        raise LayoutError(f"runtime destination already exists: {destination}")
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
        candidate = destination / entrypoint
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
        if args.entrypoint and (args.entrypoint.startswith("/") or any(part in ("", ".", "..") for part in args.entrypoint.split("/"))):
            raise LayoutError("runtime entrypoint must be a confined relative path")
        _copy_tree(source, destination, args.entrypoint)
    except (LayoutError, OSError) as exc:
        print(f"runtime-layout: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Controller-owned contracts for gitignored project seed data.

Phase-8 plans may depend on data which intentionally cannot be carried by Git.  A tracked
``.seedlist`` is the authority for those paths; this module validates the manifest and binds
the exact content digest without ever printing corpus bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Iterable


class SeedContractError(RuntimeError):
    pass


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    command = ["git", "-C", str(repo), *args]
    try:
        return subprocess.run(
            command, input=input_bytes, capture_output=True, check=False, timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise SeedContractError("seed-contract git probe timed out") from exc


def _inside(root: Path, candidate: Path) -> bool:
    return candidate == root or root in candidate.parents


def parse_manifest(raw: bytes) -> list[str]:
    if len(raw) > 65536:
        raise SeedContractError("seed manifest exceeds the 64 KiB bound")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SeedContractError("seed manifest is not UTF-8") from exc
    paths: list[str] = []
    seen: set[str] = set()
    for number, line in enumerate(text.splitlines(), 1):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        rel = PurePosixPath(value)
        if (
            value != rel.as_posix()
            or rel.is_absolute()
            or value in {".", ".."}
            or ".." in rel.parts
            or "\\" in value
            or "," in value
            or any(char.isspace() or ord(char) < 32 for char in value)
        ):
            raise SeedContractError(f"unsafe seed manifest path on line {number}")
        secret_names = {".git", ".ssh", ".netrc", ".npmrc", "credentials", "secrets",
                        "id_rsa", "id_ed25519"}
        if any(part in secret_names or part == ".env" or part.startswith(".env.")
               or part.endswith((".pem", ".key")) for part in rel.parts):
            raise SeedContractError(f"secret-shaped seed manifest path on line {number}")
        if value in seen:
            raise SeedContractError(f"duplicate seed manifest path on line {number}")
        if any(value.startswith(prior + "/") or prior.startswith(value + "/") for prior in seen):
            raise SeedContractError(f"overlapping seed manifest path on line {number}")
        seen.add(value)
        paths.append(value)
    if not paths:
        raise SeedContractError("seed manifest contains no paths")
    return paths


def _seed_entries(root: Path, paths: Iterable[str]) -> tuple[list[tuple[Path, str]], int]:
    root = root.resolve(strict=True)
    entries: list[tuple[Path, str]] = []
    files = 0
    for raw in sorted(paths):
        rel = PurePosixPath(raw)
        if rel.is_absolute() or ".." in rel.parts or raw != rel.as_posix():
            raise SeedContractError("unsafe seed path")
        start = root.joinpath(*rel.parts)
        cursor = root
        for part in rel.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise SeedContractError(f"declared seed contains a symlink component: {raw}")
        try:
            resolved = start.resolve(strict=True)
        except OSError as exc:
            raise SeedContractError(f"declared seed is absent: {raw}") from exc
        if not _inside(root, resolved) or start.is_symlink():
            raise SeedContractError(f"declared seed is symlinked or escapes the repository: {raw}")
        candidates = [start]
        if start.is_dir():
            candidates.extend(sorted(start.rglob("*"), key=lambda path: path.as_posix()))
        for path in candidates:
            try:
                info = path.lstat()
            except OSError as exc:
                raise SeedContractError(f"declared seed became unreadable: {raw}") from exc
            if stat.S_ISLNK(info.st_mode):
                raise SeedContractError(f"declared seed contains a symlink: {raw}")
            if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                raise SeedContractError(f"declared seed contains a non-file entry: {raw}")
            if not _inside(root, path.resolve(strict=True)):
                raise SeedContractError(f"declared seed escapes the repository: {raw}")
            relative = path.relative_to(root).as_posix()
            entries.append((path, relative))
            files += int(stat.S_ISREG(info.st_mode))
    return entries, files


def content_digest(root: Path, paths: Iterable[str]) -> tuple[str, int]:
    entries, files = _seed_entries(root, paths)
    digest = hashlib.sha256()
    for path, relative in entries:
        info = path.lstat()
        encoded = relative.encode("utf-8", "surrogateescape")
        kind = b"d" if stat.S_ISDIR(info.st_mode) else b"f"
        digest.update(len(encoded).to_bytes(4, "big") + encoded + kind)
        digest.update(stat.S_IMODE(info.st_mode).to_bytes(4, "big"))
        if kind == b"f":
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
    return digest.hexdigest(), files


def inspect_repository(repo: Path, manifest_path: str = ".seedlist") -> dict | None:
    repo = repo.resolve(strict=True)
    manifest_rel = PurePosixPath(manifest_path)
    if manifest_rel.is_absolute() or ".." in manifest_rel.parts or manifest_rel.as_posix() != manifest_path:
        raise SeedContractError("unsafe seed manifest path")
    manifest = repo.joinpath(*manifest_rel.parts)
    if not manifest.exists():
        return None
    if manifest.is_symlink() or not manifest.is_file() or not _inside(repo, manifest.resolve(strict=True)):
        raise SeedContractError("seed manifest must be a root-contained regular file")
    tracked = _git(repo, "ls-files", "--error-unmatch", "--", manifest_path)
    if tracked.returncode:
        raise SeedContractError("seed manifest must be tracked by Git")
    if _git(repo, "diff", "--quiet", "--", manifest_path).returncode \
            or _git(repo, "diff", "--cached", "--quiet", "--", manifest_path).returncode:
        raise SeedContractError("seed manifest must match its tracked commit")
    raw = manifest.read_bytes()
    paths = parse_manifest(raw)
    for seed in paths:
        if _git(repo, "ls-files", "--", seed).stdout:
            raise SeedContractError(f"declared seed must be untracked: {seed}")
    entries, _ = _seed_entries(repo, paths)
    relative_entries = [relative for _, relative in entries]
    encoded_entries = b"\0".join(
        item.encode("utf-8", "surrogateescape") for item in relative_entries
    ) + b"\0"
    ignored = _git(repo, "check-ignore", "-z", "--stdin", input_bytes=encoded_entries)
    ignored_paths = {
        item.decode("utf-8", "surrogateescape")
        for item in ignored.stdout.split(b"\0") if item
    }
    missing_ignored = [item for item in relative_entries if item not in ignored_paths]
    if ignored.returncode not in {0, 1} or missing_ignored:
        raise SeedContractError(f"declared seed contains unignored content: {paths[0]}")
    digest, files = content_digest(repo, paths)
    repeated, repeated_files = content_digest(repo, paths)
    if (repeated, repeated_files) != (digest, files):
        raise SeedContractError("seed content changed while its digest was measured")
    return {
        "schema_version": 1,
        "manifest_path": manifest_path,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "content_sha256": digest,
        "paths": paths,
        "file_count": files,
    }


def validate_contract(repo: Path, expected: dict) -> dict:
    observed = inspect_repository(repo, str(expected.get("manifest_path") or ".seedlist"))
    if observed is None:
        raise SeedContractError("approved seed manifest is absent")
    for key in ("schema_version", "manifest_path", "manifest_sha256", "content_sha256", "paths"):
        if observed.get(key) != expected.get(key):
            raise SeedContractError(f"approved seed contract disagrees at {key}")
    return observed


def copy_seed_paths(source_root: Path, target_root: Path, paths: Iterable[str], expected_digest: str) -> dict:
    source_root = source_root.resolve(strict=True)
    target_root = target_root.resolve(strict=True)
    normalized = list(paths)
    observed, files = content_digest(source_root, normalized)
    if observed != expected_digest:
        raise SeedContractError("source seed content does not match the approved digest")
    for raw in normalized:
        rel = PurePosixPath(raw)
        source = source_root.joinpath(*rel.parts)
        target = target_root.joinpath(*rel.parts)
        if not _inside(target_root, target.resolve(strict=False)) or target.exists() or target.is_symlink():
            raise SeedContractError(f"seed target is unsafe or already exists: {raw}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, symlinks=False)
        else:
            shutil.copy2(source, target, follow_symlinks=False)
    copied, copied_files = content_digest(target_root, normalized)
    if copied != expected_digest or copied_files != files:
        raise SeedContractError("copied seed content does not match the approved digest")
    return {"content_sha256": copied, "file_count": copied_files, "path_count": len(normalized)}


def _paths(args: argparse.Namespace) -> list[str]:
    paths = list(args.path or [])
    if not paths:
        raise SeedContractError("at least one seed path is required")
    parse_manifest(("\n".join(paths) + "\n").encode())
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("--repo", required=True)
    inspect.add_argument("--manifest", default=".seedlist")
    digest = sub.add_parser("digest")
    digest.add_argument("--root", required=True)
    digest.add_argument("--path", action="append", default=[])
    copy = sub.add_parser("copy")
    copy.add_argument("--source", required=True)
    copy.add_argument("--target", required=True)
    copy.add_argument("--expected-digest", required=True)
    copy.add_argument("--path", action="append", default=[])
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            value = inspect_repository(Path(args.repo), args.manifest)
            print(json.dumps(value or {}, sort_keys=True, separators=(",", ":")))
        elif args.command == "digest":
            value, files = content_digest(Path(args.root), _paths(args))
            print(json.dumps({"content_sha256": value, "file_count": files},
                             sort_keys=True, separators=(",", ":")))
        else:
            value = copy_seed_paths(Path(args.source), Path(args.target), _paths(args), args.expected_digest)
            print(json.dumps(value, sort_keys=True, separators=(",", ":")))
    except (OSError, SeedContractError) as exc:
        print(f"seed-contract: {exc}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

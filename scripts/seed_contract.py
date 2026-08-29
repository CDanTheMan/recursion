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


def _is_reparse(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0)) \
        or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _audit_components(path: Path, label: str) -> Path:
    candidate = Path(path)
    if any(part in {".", ".."} for part in candidate.parts):
        raise SeedContractError(f"{label} contains traversal components")
    if not candidate.is_absolute():
        candidate = Path(os.path.abspath(candidate))
    current = Path(candidate.anchor or os.sep)
    for part in candidate.parts[1:] if candidate.anchor else candidate.parts:
        current /= part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            break
        except OSError as exc:
            raise SeedContractError(f"{label} is unreadable") from exc
        if _is_reparse(info):
            raise SeedContractError(f"{label} contains a symlink/reparse component")
    return candidate


def _audit_directory(path: Path, label: str) -> Path:
    candidate = _audit_components(path, label)
    try:
        info = os.lstat(candidate)
    except OSError as exc:
        raise SeedContractError(f"{label} is unavailable") from exc
    if _is_reparse(info) or not stat.S_ISDIR(info.st_mode):
        raise SeedContractError(f"{label} is not a regular directory")
    return candidate


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
    root = _audit_directory(root, "seed repository")
    entries: list[tuple[Path, str]] = []
    files = 0
    for raw in sorted(paths):
        rel = PurePosixPath(raw)
        if rel.is_absolute() or ".." in rel.parts or raw != rel.as_posix():
            raise SeedContractError("unsafe seed path")
        start = root.joinpath(*rel.parts)
        _audit_components(start, "declared seed")
        try:
            start_info = start.lstat()
        except OSError as exc:
            raise SeedContractError(f"declared seed is absent: {raw}") from exc
        if _is_reparse(start_info):
            raise SeedContractError(f"declared seed is symlinked or escapes the repository: {raw}")
        candidates = [start]
        if stat.S_ISDIR(start_info.st_mode):
            candidates.extend(sorted(start.rglob("*"), key=lambda path: path.as_posix()))
        for path in candidates:
            try:
                info = path.lstat()
            except OSError as exc:
                raise SeedContractError(f"declared seed became unreadable: {raw}") from exc
            if _is_reparse(info):
                raise SeedContractError(f"declared seed contains a symlink: {raw}")
            if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                raise SeedContractError(f"declared seed contains a non-file entry: {raw}")
            if not _inside(root, path):
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
    repo = _audit_directory(repo, "seed repository")
    manifest_rel = PurePosixPath(manifest_path)
    if manifest_rel.is_absolute() or ".." in manifest_rel.parts or manifest_rel.as_posix() != manifest_path:
        raise SeedContractError("unsafe seed manifest path")
    manifest = repo.joinpath(*manifest_rel.parts)
    try:
        manifest_info = manifest.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise SeedContractError("seed manifest is unreadable") from exc
    if _is_reparse(manifest_info) or not stat.S_ISREG(manifest_info.st_mode) \
            or not _inside(repo, manifest):
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
    if not isinstance(expected, dict) or type(expected.get("schema_version")) is not int \
            or expected["schema_version"] != 1:
        raise SeedContractError("approved seed contract has an invalid schema_version")
    observed = inspect_repository(repo, str(expected.get("manifest_path") or ".seedlist"))
    if observed is None:
        raise SeedContractError("approved seed manifest is absent")
    for key in ("schema_version", "manifest_path", "manifest_sha256", "content_sha256", "paths"):
        if key == "schema_version":
            equal = type(observed.get(key)) is int and type(expected.get(key)) is int \
                and observed[key] == expected[key]
        else:
            equal = observed.get(key) == expected.get(key)
        if not equal:
            raise SeedContractError(f"approved seed contract disagrees at {key}")
    return observed


def copy_seed_paths(source_root: Path, target_root: Path, paths: Iterable[str], expected_digest: str) -> dict:
    source_root = _audit_directory(source_root, "seed source")
    target_root = _audit_directory(target_root, "seed target")
    normalized = list(paths)
    observed, files = content_digest(source_root, normalized)
    if observed != expected_digest:
        raise SeedContractError("source seed content does not match the approved digest")
    for raw in normalized:
        rel = PurePosixPath(raw)
        source = source_root.joinpath(*rel.parts)
        target = target_root.joinpath(*rel.parts)
        _audit_components(source, "seed source")
        _audit_components(target, "seed target")
        try:
            target_info = target.lstat()
        except FileNotFoundError:
            target_info = None
        except OSError as exc:
            raise SeedContractError(f"seed target is unreadable: {raw}") from exc
        if not _inside(target_root, target) or target_info is not None:
            raise SeedContractError(f"seed target is unsafe or already exists: {raw}")
        _audit_components(target.parent, "seed target parent")
        target.parent.mkdir(parents=True, exist_ok=True)
        _audit_components(target.parent, "seed target parent")
        source_info = source.lstat()
        if _is_reparse(source_info):
            raise SeedContractError(f"seed source became a symlink: {raw}")
        if stat.S_ISDIR(source_info.st_mode):
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
    except (OSError, ValueError, TypeError, OverflowError, RecursionError,
            UnicodeError, json.JSONDecodeError, subprocess.TimeoutExpired,
            subprocess.SubprocessError, SeedContractError) as exc:
        print(f"seed-contract: {exc}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

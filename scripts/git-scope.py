#!/usr/bin/env python3
"""Collect and enforce complete base/index/worktree/untracked Git scope evidence."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import PurePosixPath


TEST_NAME = re.compile(r"(?:^|/)[^/]*\.test\.(?:cjs|js|mjs|py|sh)$")


def git(repo: str, *args: str) -> bytes:
    proc = subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode:
        raise ValueError(proc.stderr.decode(errors="replace").strip() or "git command failed")
    return proc.stdout


def diff_entries(repo: str, source: str, args: list[str]) -> list[dict]:
    cells = git(repo, *args).decode("utf-8", "surrogateescape").split("\0")
    if cells and cells[-1] == "":
        cells.pop()
    result: list[dict] = []
    i = 0
    while i < len(cells):
        status = cells[i]; i += 1
        if status.startswith(("R", "C")):
            if i + 1 >= len(cells):
                raise ValueError(f"truncated {source} rename/copy record")
            old_path, path = cells[i], cells[i + 1]; i += 2
            result.append({"source": source, "status": status, "old_path": old_path, "path": path})
        else:
            if i >= len(cells):
                raise ValueError(f"truncated {source} record")
            result.append({"source": source, "status": status, "path": cells[i]}); i += 1
    return result


def protected(path: str, extras: set[str]) -> bool:
    p = PurePosixPath(path)
    parts = p.parts
    if path in extras:
        return True
    if path in {"CONTROL_PLANE.md", "ANCHOR.md", "CLAUDE.md", ".env"} or path.startswith(".env."):
        return True
    if parts and parts[0] in {"scripts", "state", ".github"}:
        return True
    if any(part in {"tests", "test", "__tests__", "fixtures", "fixture", "golden", "oracle"} for part in parts):
        return True
    if len(parts) >= 2 and parts[0:2] == ("render", "data"):
        return True
    return bool(TEST_NAME.search(path) or "baseline" in p.name.lower())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--allowed-paths", default=".")
    parser.add_argument("--protected-extra", default="")
    parser.add_argument("--ignore", action="append", default=[])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        git(args.repo, "cat-file", "-e", f"{args.base}^{{commit}}")
        head = git(args.repo, "rev-parse", "HEAD").decode().strip()
        entries = []
        entries += diff_entries(args.repo, "base..HEAD", ["diff", "--name-status", "-z", "--find-renames", f"{args.base}..HEAD"])
        entries += diff_entries(args.repo, "staged", ["diff", "--cached", "--name-status", "-z", "--find-renames"])
        entries += diff_entries(args.repo, "unstaged", ["diff", "--name-status", "-z", "--find-renames"])
        for path in git(args.repo, "ls-files", "--others", "--exclude-standard", "-z").decode("utf-8", "surrogateescape").split("\0"):
            if path:
                entries.append({"source": "untracked", "status": "?", "path": path})
        ignored = set(args.ignore)
        filtered = [entry for entry in entries if entry["path"] not in ignored and entry.get("old_path") not in ignored]
        all_paths = sorted({value for entry in filtered for value in (entry.get("old_path"), entry.get("path")) if value})
        extras = set(args.protected_extra.replace(",", " ").split())
        protected_paths = sorted(path for path in all_paths if protected(path, extras))
        allowed = [item.rstrip("/") for item in args.allowed_paths.replace(",", " ").split() if item]
        if "." in allowed:
            outside: list[str] = []
        else:
            outside = sorted(path for path in all_paths if not any(path == root or path.startswith(root + "/") for root in allowed))
        evidence = {"base_commit": args.base, "head_commit": head, "entries": filtered,
                    "paths": all_paths, "protected_paths": protected_paths, "outside_paths": outside}
        print(json.dumps(evidence, sort_keys=True))
        if args.check and (protected_paths or outside):
            if protected_paths:
                print("modified PROTECTED paths: " + ", ".join(protected_paths[:10]), file=sys.stderr)
            if outside:
                print("modified paths outside allowed scope: " + ", ".join(outside[:10]), file=sys.stderr)
            return 1
    except ValueError as exc:
        print(f"ERR {exc}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

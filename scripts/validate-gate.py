#!/usr/bin/env python3
"""Fail closed for empty, vacuous, result-dependent, or worker-modifiable gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path, PurePosixPath


VACUOUS = re.compile(
    r"^(?:true|:|/bin/true|exit\s+0|test\s+1\s*(?:=|-eq)\s*1|\[\s*1\s*=\s*1\s*\])$"
)


def fail(message: str) -> None:
    raise ValueError(message)


def paths(value: str) -> list[str]:
    result: list[str] = []
    for item in value.replace(",", " ").split():
        p = PurePosixPath(item)
        if p.is_absolute() or ".." in p.parts or item in {"", "."}:
            fail(f"unsafe gate file: {item!r}")
        result.append(p.as_posix())
    return result


def under(path: str, roots: list[str]) -> bool:
    return "." in roots or any(path == root.rstrip("/") or path.startswith(root.rstrip("/") + "/") for root in roots)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acceptance", required=True)
    parser.add_argument("--allowed-paths", default=".")
    parser.add_argument("--gate-files", default="")
    parser.add_argument("--repo")
    args = parser.parse_args()
    try:
        gate = args.acceptance.strip()
        if not gate or len(gate) > 4096 or any(ord(ch) < 32 and ch not in "\t" for ch in gate):
            fail("acceptance gate must be bounded, single-line, and non-empty")
        compact = re.sub(r"\s+", " ", gate)
        if VACUOUS.fullmatch(compact) or re.search(r"(?:\|\||;)\s*(?:true|:|exit\s+0)\s*$", compact):
            fail("acceptance gate is structurally vacuous")
        if ".recursion-result.json" in gate:
            fail("acceptance gate may not grade the worker's own result report")
        allowed = [p.rstrip("/") for p in args.allowed_paths.replace(",", " ").split() if p]
        gate_files = paths(args.gate_files)
        for segment in re.split(r"\s*(?:&&|\|\||;)\s*", gate):
            try:
                words = shlex.split(segment)
            except ValueError as exc:
                fail(f"acceptance gate cannot be parsed: {exc}")
            if len(words) >= 2 and words[0] in {"bash", "sh", "python", "python3", "node"}:
                candidate = words[1].replace("\\", "/")
                if under(candidate, allowed) and candidate not in gate_files:
                    fail(f"worker-modifiable gate program must be declared in gate_files: {candidate}")
        hashes: dict[str, str] = {}
        if args.repo:
            repo = Path(args.repo)
            for item in gate_files:
                path = repo / item
                if not path.is_file():
                    fail(f"gate file is absent: {item}")
                tracked = subprocess.run(
                    ["git", "-C", str(repo), "ls-files", "--error-unmatch", "--", item],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
                if tracked.returncode:
                    fail(f"gate file is not tracked: {item}")
                hashes[item] = hashlib.sha256(path.read_bytes()).hexdigest()
        print(json.dumps({"acceptance_sha256": hashlib.sha256(gate.encode()).hexdigest(),
                          "gate_files": hashes}, sort_keys=True))
    except (OSError, ValueError) as exc:
        print(f"ERR {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

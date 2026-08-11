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


VACUOUS = re.compile(r"^(?:true|:|/bin/true|exit\s+0)$")


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


def vacuous_success(words: list[str]) -> bool:
    """Recognize commands whose success is independent of the code under review."""
    if not words:
        return True
    if words[0] in {"true", ":", "/bin/true"}:
        return True
    if words[:2] == ["exit", "0"]:
        return True
    if words[0] in {"echo", "printf"}:
        return True
    test = words
    if words[0] == "[" and words[-1:] == ["]"]:
        test = ["test", *words[1:-1]]
    if test[:1] != ["test"]:
        return False
    args = test[1:]
    if len(args) == 2 and args[0] in {"-e", "-d"} and args[1] == "/":
        return True
    if len(args) == 3 and args[1] in {"=", "==", "-eq"} and args[0] == args[2]:
        return True
    if len(args) == 2 and args[0] == "-n" and args[1] and not any(ch in args[1] for ch in "$*?["):
        return True
    return False


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
        raw_segments = re.split(r"\s*(?:&&|\|\||;)\s*", gate)
        operators = re.findall(r"&&|\|\||;", gate)
        parsed_segments: list[list[str]] = []
        for segment in raw_segments:
            try:
                parsed_segments.append(shlex.split(segment))
            except ValueError as exc:
                fail(f"acceptance gate cannot be parsed: {exc}")
        vacuous = [vacuous_success(words) for words in parsed_segments]
        hides_prior_result = any(op in {"||", ";"} and vacuous[index + 1]
                                 for index, op in enumerate(operators))
        vacuous_or_branch = any(
            op == "||" and (vacuous[index] or vacuous[index + 1])
            for index, op in enumerate(operators)
        )
        if VACUOUS.fullmatch(compact) or all(vacuous) or hides_prior_result or vacuous_or_branch:
            fail("acceptance gate is structurally vacuous")
        if ".recursion-result.json" in gate:
            fail("acceptance gate may not grade the worker's own result report")
        allowed = [p.rstrip("/") for p in args.allowed_paths.replace(",", " ").split() if p]
        gate_files = paths(args.gate_files)
        for words in parsed_segments:
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

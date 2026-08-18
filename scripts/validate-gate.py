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

# Shell reserved words and wrapper/detaching launchers that would let an admission string hide,
# invert, or detach the actual direct grading program. `env`/`npm`/etc. are already rejected as
# indirect launchers below; this set is the remaining reserved-word and privilege/detach class.
RESERVED = {
    "!", "command", "exec", "builtin", "source", ".", "time", "nohup", "setsid",
    "nice", "sudo", "su", "doas", "timeout", "chroot", "unshare", "nsenter",
    "runuser", "script", "eval", "trap", "set", "coproc", "systemd-run",
    "disown", "jobs", "wait", "bg", "fg", "ulimit", "prlimit", "strace", "gdb",
}


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


def clean_tracked_bytes(repo: Path, item: str) -> bytes:
    """Return the committed gate bytes and reject index/worktree substitution."""
    tracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--error-unmatch", "--", item],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    if tracked.returncode:
        fail(f"gate file is not tracked: {item}")
    committed = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{item}"], capture_output=True, check=False,
    )
    if committed.returncode:
        fail(f"gate file is absent from HEAD: {item}")
    path = repo / item
    dirty = subprocess.run(
        ["git", "-C", str(repo), "diff", "--quiet", "HEAD", "--", item], check=False,
    )
    if not path.is_file() or dirty.returncode:
        fail(f"gate file differs from clean HEAD: {item}")
    return committed.stdout


def entrypoint(words: list[str], strict: bool) -> str | None:
    """Identify the only executable source file in the admitted direct-command class."""
    if not words:
        return None
    command = words[0].replace("\\", "/")
    name = PurePosixPath(command).name
    if strict and name in RESERVED:
        fail(f"shell reserved word or wrapper is not admitted: {command}")
    if name in {"env", "npm", "npx", "yarn", "pnpm", "xargs", "find", "make"}:
        if strict:
            fail(f"indirect acceptance launcher is not admitted: {name}")
        return None
    if name in {"test", "["}:
        return None
    if name not in {"bash", "sh", "python", "python3", "node"}:
        if strict and "/" not in command:
            fail(f"bare acceptance launcher is not admitted: {name}")
        return PurePosixPath(command).as_posix() if "/" in command else None
    for word in words[1:]:
        if word in {"-c", "-e", "--eval", "-m"}:
            if strict:
                fail(f"dynamic {name} acceptance programs are not admitted")
            return None
        if word.startswith("-"):
            if strict:
                fail(f"option-bearing {name} acceptance programs are not admitted: {word}")
            continue
        return PurePosixPath(word.replace("\\", "/")).as_posix()
    fail(f"{name} acceptance has no explicit grading program")


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
    parser.add_argument("--controller-gate-files", default="")
    parser.add_argument("--controller-root")
    parser.add_argument("--strict-direct", action="store_true")
    args = parser.parse_args()
    try:
        gate = args.acceptance.strip()
        if not gate or len(gate) > 4096 or any(ord(ch) < 32 and ch not in "\t" for ch in gate):
            fail("acceptance gate must be bounded, single-line, and non-empty")
        compact = re.sub(r"\s+", " ", gate)
        if args.strict_direct and (
            any(token in gate for token in ("`", "$", "<(", ">(", "||", ";"))
            or re.search(r"(?<!\|)\|(?!\|)", gate)
            or re.search(r"(?<![&])&(?![&])", gate)
            or "<" in gate or ">" in gate
        ):
            fail("acceptance gate uses unreviewable shell indirection")
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
        controller_gate_files = paths(args.controller_gate_files)
        for words in parsed_segments:
            candidate = entrypoint(words, args.strict_direct)
            if candidate and PurePosixPath(candidate).is_absolute():
                if not args.controller_root:
                    fail("absolute acceptance program lacks a controller root")
                try:
                    relative = Path(candidate).resolve().relative_to(Path(args.controller_root).resolve()).as_posix()
                except ValueError:
                    fail(f"acceptance program is outside the controller root: {candidate}")
                if relative not in controller_gate_files:
                    fail(f"controller acceptance program must be declared: {relative}")
            elif candidate and under(candidate, allowed) and candidate not in gate_files:
                fail(f"worker-modifiable gate program must be declared in gate_files: {candidate}")
        hashes: dict[str, str] = {}
        if args.repo:
            repo = Path(args.repo)
            for item in gate_files:
                hashes[item] = hashlib.sha256(clean_tracked_bytes(repo, item)).hexdigest()
        controller_hashes: dict[str, str] = {}
        if controller_gate_files:
            if not args.controller_root:
                fail("controller gate files require --controller-root")
            controller = Path(args.controller_root)
            for item in controller_gate_files:
                controller_hashes[item] = hashlib.sha256(clean_tracked_bytes(controller, item)).hexdigest()
        print(json.dumps({"acceptance_sha256": hashlib.sha256(gate.encode()).hexdigest(),
                          "gate_files": hashes,
                          "controller_gate_files": controller_hashes}, sort_keys=True))
    except ValueError as exc:
        print(f"ERR {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERR controller I/O while validating gate: {exc}", file=sys.stderr)
        return 74
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

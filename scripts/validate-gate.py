#!/usr/bin/env python3
"""Fail closed for empty, vacuous, result-dependent, or worker-modifiable gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path, PurePosixPath

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from phase5_safety import BoundaryError, decode_json, pinned_directory, read_bytes, verify_leaf


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
        if p.is_absolute() or "\\" in item or ":" in item \
                or ".." in p.parts or item in {"", "."}:
            fail(f"unsafe gate file: {item!r}")
        result.append(p.as_posix())
    return result


def under(path: str, roots: list[str]) -> bool:
    return "." in roots or any(path == root.rstrip("/") or path.startswith(root.rstrip("/") + "/") for root in roots)


def resolved_under(repo: Path, candidate: str, roots: list[str]) -> bool:
    """Require a lexical gate path to remain inside the materialized allowed tree."""
    try:
        repo_root = Path(os.path.abspath(str(repo)))
        candidate_path = Path(os.path.abspath(str(repo / candidate)))
        resolved_roots = [Path(os.path.abspath(str(repo / root))) for root in roots]
        candidate_path.relative_to(repo_root)
        with pinned_directory(repo_root):
            with pinned_directory(candidate_path.parent):
                for root in resolved_roots:
                    with pinned_directory(root):
                        if candidate_path == root or root in candidate_path.parents:
                            # The lexical containment check and the actual leaf
                            # lookup share pinned, no-follow parent handles.  This
                            # rejects a final symlink/junction or hardlink swap,
                            # not only an escaping parent.
                            verify_leaf(candidate_path)
                            return True
        return False
    except (BoundaryError, OSError, ValueError, TypeError):
        return False


def canonical_controller_root(value: str) -> Path:
    """Return the one controller root this process is authorized to inspect.

    A commit is not a root identity: two worktrees can expose the same commit while one
    carries attacker-controlled live policy files.  The controller exports RECURSION_ROOT
    before invoking this helper; direct use falls back to the checked-out helper root.
    """
    try:
        with pinned_directory(value) as (_, requested_value):
            requested = Path(requested_value)
        configured = os.environ.get("RECURSION_ROOT", "").strip() or Path(__file__).parent.parent
        with pinned_directory(configured) as (_, configured_value):
            configured = Path(configured_value)
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        fail("controller root is unavailable")
    if requested != configured:
        fail("controller root is not the canonical controller root")
    return requested


def clean_tracked_bytes(repo: Path, item: str, commit: str | None = None) -> bytes:
    """Return exact committed bytes and reject index/worktree or mode substitution.

    A contract may name a source commit explicitly.  In that mode both the Git object and
    the materialized file must still be the same clean regular file; hashing ``HEAD`` alone
    would let a post-creation working-tree edit survive until evidence consumption.
    """
    path = repo / item
    if PurePosixPath(item).is_absolute() or "\\" in item or ":" in item \
            or any(part in {"", ".", ".."} for part in item.split("/")):
        fail(f"gate file resolves outside the source repository: {item}")
    try:
        live = read_bytes(path, label=f"gate file {item}")
    except BoundaryError as exc:
        fail(f"gate file is not a regular non-symlink file: {item}")
    target = commit or "HEAD"
    if commit:
        resolved = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", f"{commit}^{{commit}}"],
            capture_output=True, text=True, check=False,
        )
        if resolved.returncode or resolved.stdout.strip() != commit:
            fail(f"gate source commit is not the exact immutable commit: {commit}")
        tree = subprocess.run(
            ["git", "-C", str(repo), "ls-tree", "-z", commit, "--", item],
            capture_output=True, check=False,
        )
        rows = [row for row in tree.stdout.split(b"\0") if row]
        if tree.returncode or len(rows) != 1:
            fail(f"gate file is absent from the exact source commit: {item}")
        header, _, tree_path = rows[0].partition(b"\t")
        if tree_path.decode("utf-8", "strict") != item:
            fail(f"gate file path resolution is not exact: {item}")
        git_mode = header.split(b" ", 1)[0]
        if git_mode not in {b"100644", b"100755"}:
            fail(f"gate file has a non-regular Git mode: {item}")
    tracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--error-unmatch", "--", item],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    if tracked.returncode:
        fail(f"gate file is not tracked: {item}")
    committed = subprocess.run(
        ["git", "-C", str(repo), "show", f"{target}:{item}"], capture_output=True, check=False,
    )
    if committed.returncode:
        fail(f"gate file is absent from {target}: {item}")
    dirty = subprocess.run(
        ["git", "-C", str(repo), "diff", "--quiet", target, "--", item], check=False,
    )
    if dirty.returncode:
        fail(f"gate file differs from clean {target}: {item}")
    if live != committed.stdout:
        fail(f"gate file differs from clean {target}: {item}")
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


def validate_test_paths(words: list[str], allowed: list[str], gate_files: list[str], repo: Path | None) -> None:
    """Check file operands of direct ``test``/``[`` commands as well as launchers.

    The shell grammar is deliberately narrow, but a direct file test still executes a path
    lookup.  Only operands of the file-test operators are classified as paths; comparisons
    such as ``test a != b`` remain ordinary scalar comparisons.
    """
    test_words = words
    if words[:1] == ["["] and words[-1:] == ["]"]:
        test_words = ["test", *words[1:-1]]
    if test_words[:1] != ["test"]:
        return
    file_operators = {"-b", "-c", "-d", "-e", "-f", "-g", "-h", "-L", "-p", "-r", "-s", "-S", "-t", "-u", "-w", "-x"}
    for index, word in enumerate(test_words[1:-1], 1):
        if word not in file_operators:
            continue
        candidate = test_words[index + 1].replace("\\", "/")
        if not candidate or PurePosixPath(candidate).is_absolute() \
                or any(part in {"", ".", ".."} for part in candidate.split("/")):
            fail(f"acceptance file operand is outside the allowed tree: {candidate!r}")
        if not under(candidate, allowed):
            fail(f"acceptance file operand is outside the allowed tree: {candidate}")
        if repo is not None and not resolved_under(repo, candidate, allowed):
            fail(f"acceptance file operand resolves outside the allowed tree: {candidate}")


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
    parser.add_argument("--source-commit")
    parser.add_argument("--controller-gate-files", default="")
    parser.add_argument("--controller-root")
    parser.add_argument("--controller-commit")
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
            # POSIX-mode shlex consumes unquoted backslashes, so a Windows-style path reaches
            # entrypoint() pre-mangled ("app\check.py" -> "appcheck.py") and slips outside the
            # allowed roots — evading the gate_files declaration check. Normalize before the
            # split on Windows hosts only: on the box parsing stays byte-for-byte identical
            # (making it identical there too is PROPOSALS 2026-08-27 item 11's open remainder).
            if os.name == "nt":
                segment = segment.replace("\\", "/")
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
        if args.controller_root:
            controller_root = canonical_controller_root(args.controller_root)
            if args.controller_commit:
                clean_head = subprocess.run(
                    ["git", "-C", str(controller_root), "rev-parse", "--verify", "HEAD"],
                    capture_output=True, text=True, check=False,
                )
                if clean_head.returncode or clean_head.stdout.strip() != args.controller_commit:
                    fail("controller HEAD is not the exact immutable controller commit")
        else:
            controller_root = None
        for words in parsed_segments:
            validate_test_paths(words, allowed, gate_files, Path(args.repo) if args.repo else None)
            candidate = entrypoint(words, args.strict_direct)
            if candidate:
                candidate_path = PurePosixPath(candidate)
                if any(part in {"", ".", ".."} for part in candidate.split("/")):
                    fail(f"acceptance program uses an unsafe path: {candidate}")
            if candidate and PurePosixPath(candidate).is_absolute():
                if controller_root is None:
                    fail("absolute acceptance program lacks a controller root")
                try:
                    relative = Path(os.path.abspath(candidate)).relative_to(
                        Path(os.path.abspath(str(controller_root)))
                    ).as_posix()
                except ValueError:
                    fail(f"acceptance program is outside the controller root: {candidate}")
                except OSError:
                    fail(f"acceptance program is unavailable: {candidate}")
                if relative not in controller_gate_files:
                    fail(f"controller acceptance program must be declared: {relative}")
            elif candidate:
                if not under(candidate, allowed):
                    fail(f"acceptance program is outside the allowed tree: {candidate}")
                if args.repo and not resolved_under(Path(args.repo), candidate, allowed):
                    fail(f"acceptance program resolves outside the allowed tree: {candidate}")
                if candidate not in gate_files:
                    fail(f"worker-modifiable gate program must be declared in gate_files: {candidate}")
        hashes: dict[str, str] = {}
        if args.repo:
            repo = Path(args.repo)
            for item in gate_files:
                hashes[item] = hashlib.sha256(clean_tracked_bytes(repo, item, args.source_commit)).hexdigest()
        controller_hashes: dict[str, str] = {}
        if controller_gate_files:
            if controller_root is None:
                fail("controller gate files require --controller-root")
            controller = controller_root
            for item in controller_gate_files:
                controller_hashes[item] = hashlib.sha256(
                    clean_tracked_bytes(controller, item, args.controller_commit)
                ).hexdigest()
        print(json.dumps({"acceptance": gate,
                          "acceptance_sha256": hashlib.sha256(gate.encode()).hexdigest(),
                          "gate_files": hashes,
                          "controller_gate_files": controller_hashes}, sort_keys=True))
    except (ValueError, TypeError, OverflowError, RecursionError,
            UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"ERR {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERR controller I/O while validating gate: {exc}", file=sys.stderr)
        return 74
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

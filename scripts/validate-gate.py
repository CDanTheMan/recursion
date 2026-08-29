#!/usr/bin/env python3
"""Fail closed for empty, vacuous, result-dependent, or worker-modifiable gates."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shlex
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath


VACUOUS = re.compile(r"^(?:true|:|/bin/true|exit\s+0)$")
BOUNDARY_ERRORS = (json.JSONDecodeError, ValueError, TypeError, OverflowError,
                   RecursionError, UnicodeDecodeError, OSError, subprocess.TimeoutExpired)


def _native_handle_value(handle: object) -> int:
    try:
        value = handle.value if hasattr(handle, "value") else int(handle)  # type: ignore[attr-defined]
        if not isinstance(value, int) or value <= 0:
            raise ValueError("invalid native handle")
        return value
    except BOUNDARY_ERRORS as exc:
        raise OSError("invalid native handle") from exc


# Keep the descriptor schema and this runtime entry point on one deliberately small shell
# grammar.  The regular expression is the lexical boundary (balanced whole-token quoting,
# direct commands, and `&&` only); argv-aware checks below then enforce ownership and path policy.
# validate-gate.test.py differentially exercises this expression through both public
# admission surfaces so edits cannot silently widen only one side.
_DIRECT_COMMAND = r"(?:test|\[|git|bash|sh|python|python3|node)"
_DIRECT_ARGUMENT = r'''(?:[^\s&|<>`~%$*?\[(){};'\"]+|"[^"&|<>`~%$*?\[(){};\r\n]+"|'[^'&|<>`~%$*?\[(){};\r\n]+')'''
_DIRECT_SEGMENT = rf"{_DIRECT_COMMAND}(?:\s+{_DIRECT_ARGUMENT})*"
STRICT_DIRECT_PATTERN = re.compile(
    r"^(?!.*[\x00-\x08\x0A-\x1F])"
    r"(?!.*\.recursion-result\.json)"
    r"(?!.*(?:^|[\s\"'])(?:/|[A-Za-z]:[/\\]))"
    r"(?!.*(?:^|[/\\\s\"'])\.\.(?:[/\\\s\"']|$))"
    r"(?!.*(?:^|\s)[\"']-)"
    r"(?!.*(?:^|&&)\s*(?:bash|sh|python|python3|node)\s*(?:&&|$))"
    r"(?!.*(?:^|&&)\s*(?:bash|sh|python|python3|node)\s+-)"
    r"(?!.*(?:^|&&)\s*(?:test|\[)\s+-n(?:\s|$))"
    r"(?!.*(?:^|&&)\s*(?:test|\[)(?:(?!&&).)*\s(?:=|==|-eq)\s)"
    r"(?!.*(?:^|&&)\s*git(?:(?!&&).)*\s"
    r"(?:-C|-c|-o|--(?:git-dir|work-tree|super-prefix|exec-path|namespace|config|config-env|output))"
    r"[^\s&]*(?=\s|&&|$))"
    r"(?!.*(?:^|&&)\s*git\s+-)"
    r"(?!.*(?:^|&&)\s*git\s+(?!(?:diff|status|show|rev-parse|ls-files|cat-file)(?:\s|$))[^\s&]+(?:\s|$))"
    rf"\s*{_DIRECT_SEGMENT}(?:\s*&&\s*{_DIRECT_SEGMENT})*\s*$"
)

_CONTROLLER_COMMAND = r"(?:/(?:[^\s&|<>`~%$*?\[(){};'\"]+)|[A-Za-z]:[^\s&|<>`~%$*?\[(){};'\"]+)"
_CONTROLLER_SEGMENT = rf"(?:{_DIRECT_COMMAND}|{_CONTROLLER_COMMAND})(?:\s+{_DIRECT_ARGUMENT})*"
STRICT_CONTROLLER_PATTERN = re.compile(
    r"^(?!.*[\x00-\x08\x0A-\x1F])"
    r"(?!.*\.recursion-result\.json)"
    r"(?!.*(?:^|[/\\\s\"'])\.\.(?:[/\\\s\"']|$))"
    r"(?!.*(?:^|&&)\s*(?:bash|sh|python|python3|node)\s*(?:&&|$))"
    r"(?!.*(?:^|&&)\s*(?:bash|sh|python|python3|node)\s+-)"
    r"(?!.*(?:^|&&)\s*(?:test|\[)\s+-n(?:\s|$))"
    r"(?!.*(?:^|&&)\s*(?:test|\[)(?:(?!&&).)*\s(?:=|==|-eq)\s)"
    r"(?!.*(?:^|&&)\s*git(?:(?!&&).)*\s"
    r"(?:-C|-c|-o|--(?:git-dir|work-tree|super-prefix|exec-path|namespace|config|config-env|output))"
    r"[^\s&]*(?=\s|&&|$))"
    r"(?!.*(?:^|&&)\s*git\s+-)"
    r"(?!.*(?:^|&&)\s*git\s+(?!(?:diff|status|show|rev-parse|ls-files|cat-file)(?:\s|$))[^\s&]+(?:\s|$))"
    rf"\s*{_CONTROLLER_SEGMENT}(?:\s*&&\s*{_CONTROLLER_SEGMENT})*\s*$"
)

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
    if not isinstance(value, str):
        fail("gate file list must be text")
    result: list[str] = []
    for item in value.replace(",", " ").split():
        p = PurePosixPath(item)
        if (p.is_absolute() or ".." in p.parts or item in {"", "."}
                or any(char in item for char in "~%$`*?[")
                or item.startswith(("\\\\", "//"))
                or re.match(r"^[A-Za-z]:", item)):
            fail(f"unsafe gate file: {item!r}")
        if "\\" in item or p.as_posix() != item:
            fail(f"unsafe gate file: {item!r}")
        result.append(p.as_posix())
    return result


def under(path: str, roots: list[str]) -> bool:
    return "." in roots or any(path == root.rstrip("/") or path.startswith(root.rstrip("/") + "/") for root in roots)


def _is_reparse_or_link(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _lexical_absolute(path: Path | str) -> Path:
    try:
        raw = os.fspath(path)
        if not isinstance(raw, str) or not raw:
            raise ValueError("path must be non-empty")
        return Path(os.path.abspath(raw))
    except BOUNDARY_ERRORS as exc:
        raise ValueError("path could not be made absolute") from exc


def _same_file(left: os.stat_result, right: os.stat_result) -> bool:
    return (left.st_dev, left.st_ino, getattr(left, "st_nlink", 1)) == (
        right.st_dev, right.st_ino, getattr(right, "st_nlink", 1))


def _open_verified_file(path: Path) -> int:
    """Open one regular file without following a leaf reparse and pin its identity."""
    fd: int | None = None
    try:
        initial = os.lstat(path)
        if _is_reparse_or_link(initial) or not stat.S_ISREG(initial.st_mode) \
                or getattr(initial, "st_nlink", 1) != 1:
            fail(f"gate file is a symlink or reparse point: {path}")
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            import msvcrt
            kernel32 = ctypes.WinDLL("Kernel32", use_last_error=True)
            create_file = kernel32.CreateFileW
            create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                    ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
            create_file.restype = wintypes.HANDLE
            close_handle = kernel32.CloseHandle
            close_handle.argtypes = [wintypes.HANDLE]
            close_handle.restype = wintypes.BOOL
            handle = create_file(str(path), 0x80000000, 0x00000003, None, 3,
                                 0x00000080 | 0x00200000 | 0x02000000, None)
            handle_value = _native_handle_value(handle)
            if handle_value in {None, ctypes.c_void_p(-1).value}:
                raise OSError(ctypes.get_last_error(), "Windows no-follow open failed")
            try:
                fd = msvcrt.open_osfhandle(handle_value, os.O_RDONLY | os.O_BINARY)
            except OSError:
                close_handle(handle)
                raise
        else:
            flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(path, flags)
        current = os.fstat(fd)
        if _is_reparse_or_link(current) or not stat.S_ISREG(current.st_mode) \
                or getattr(current, "st_nlink", 1) != 1 \
                or not _same_file(initial, current):
            os.close(fd)
            fail(f"gate file changed while being opened: {path}")
        return fd
    except BOUNDARY_ERRORS as exc:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if isinstance(exc, ValueError):
            raise
        raise ValueError(f"gate file could not be opened without following links: {path}") from exc


def _read_pinned(fd: int, path: Path) -> bytes:
    try:
        before = os.fstat(fd)
        if _is_reparse_or_link(before) or not stat.S_ISREG(before.st_mode) \
                or getattr(before, "st_nlink", 1) != 1:
            fail(f"gate file changed before being read: {path}")
        os.lseek(fd, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        current = os.fstat(fd)
        if _is_reparse_or_link(current) or not stat.S_ISREG(current.st_mode) \
                or getattr(current, "st_nlink", 1) != 1 or not _same_file(before, current):
            fail(f"gate file changed while being read: {path}")
        return b"".join(chunks)
    except BOUNDARY_ERRORS as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError(f"gate file could not be read safely: {path}") from exc


@contextlib.contextmanager
def _pinned_file_parents(path: Path):
    """Hold every existing parent while a gate file is opened and executed."""
    absolute = _lexical_absolute(path)
    handles: list[int] = []
    identities: list[os.stat_result] = []
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            import msvcrt
            kernel32 = ctypes.WinDLL("Kernel32", use_last_error=True)
            create_file = kernel32.CreateFileW
            create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                    ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
            create_file.restype = wintypes.HANDLE
            close_handle = kernel32.CloseHandle
            close_handle.argtypes = [wintypes.HANDLE]
            close_handle.restype = wintypes.BOOL
            for parent in reversed(tuple(absolute.parents)):
                if parent == parent.parent:
                    continue
                initial = os.lstat(parent)
                if _is_reparse_or_link(initial) or not stat.S_ISDIR(initial.st_mode):
                    fail(f"gate file parent is not a real directory: {path}")
                native = create_file(str(parent), 0x00020000 | 0x00000080, 0x00000003,
                                     None, 3, 0x02000000 | 0x00200000, None)
                value = _native_handle_value(native)
                if value in {None, ctypes.c_void_p(-1).value}:
                    raise OSError(ctypes.get_last_error(), "gate parent could not be pinned")
                try:
                    fd = msvcrt.open_osfhandle(value, os.O_RDONLY | os.O_BINARY)
                except OSError:
                    close_handle(native)
                    raise
                pinned = os.fstat(fd)
                if _is_reparse_or_link(pinned) or not stat.S_ISDIR(pinned.st_mode) \
                        or not _same_file(initial, pinned):
                    os.close(fd)
                    fail(f"gate file parent changed while being pinned: {path}")
                handles.append(fd)
                identities.append(pinned)
            yield
            for fd, expected in zip(handles, identities):
                pinned = os.fstat(fd)
                if _is_reparse_or_link(pinned) or not stat.S_ISDIR(pinned.st_mode) \
                        or not _same_file(expected, pinned):
                    fail(f"gate file parent changed during execution: {path}")
            return

        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        parts = absolute.parts
        current = os.open(Path(absolute.anchor or os.sep), flags)
        handles.append(current)
        identities.append(os.fstat(current))
        if _is_reparse_or_link(identities[-1]) or not stat.S_ISDIR(identities[-1].st_mode):
            fail(f"gate file parent is not a real directory: {path}")
        for part in parts[1:-1] if absolute.anchor else parts[:-1]:
            current = os.open(part, flags, dir_fd=current)
            info = os.fstat(current)
            if _is_reparse_or_link(info) or not stat.S_ISDIR(info.st_mode):
                fail(f"gate file parent is not a real directory: {path}")
            handles.append(current)
            identities.append(info)
        yield
        for fd, expected in zip(handles, identities):
            info = os.fstat(fd)
            if _is_reparse_or_link(info) or not stat.S_ISDIR(info.st_mode) \
                    or not _same_file(expected, info):
                fail(f"gate file parent changed during execution: {path}")
    except BOUNDARY_ERRORS as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError(f"gate file parent could not be pinned: {path}") from exc
    finally:
        for fd in reversed(handles):
            try:
                os.close(fd)
            except OSError:
                pass


def _safe_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(*args, **kwargs)  # type: ignore[arg-type, return-value]
    except BOUNDARY_ERRORS as exc:
        raise ValueError("Git provenance command was unavailable") from exc


def clean_tracked_bytes(repo: Path, item: str, baseline_commit: str | None = None) -> bytes:
    """Return the committed gate bytes and reject index/worktree substitution."""
    if not isinstance(item, str):
        fail("gate file path must be text")
    pure = PurePosixPath(item)
    if (pure.is_absolute() or ".." in pure.parts or not pure.parts
            or pure.as_posix() != item or "\\" in item
            or any(char in item for char in "~%$`*?[")
            or item.startswith(("\\\\", "//"))
            or re.match(r"^[A-Za-z]:", item)):
        fail(f"gate file path is not a confined repository path: {item}")
    tracked = _safe_run(
        ["git", "-C", str(repo), "ls-files", "--error-unmatch", "--", item],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    if tracked.returncode:
        fail(f"gate file is not tracked: {item}")
    committed = _safe_run(
        ["git", "-C", str(repo), "show", f"HEAD:{item}"], capture_output=True, check=False,
    )
    if committed.returncode:
        fail(f"gate file is absent from HEAD: {item}")
    path = repo
    parts = PurePosixPath(item).parts
    try:
        root_info = os.lstat(path)
        if _is_reparse_or_link(root_info) or not stat.S_ISDIR(root_info.st_mode):
            fail(f"gate repository root is not a real directory: {repo}")
        for index, part in enumerate(parts):
            path = path / part
            info = os.lstat(path)
            if _is_reparse_or_link(info):
                fail(f"gate file is a symlink or reparse point: {item}")
            if index == len(parts) - 1:
                if not stat.S_ISREG(info.st_mode):
                    fail(f"gate file is not a regular file: {item}")
            elif not stat.S_ISDIR(info.st_mode):
                fail(f"gate file parent is not a real directory: {item}")
    except OSError as exc:
        fail(f"gate file cannot be inspected without following links: {item}: {exc}")
    dirty = _safe_run(
        ["git", "-C", str(repo), "diff", "--quiet", "HEAD", "--", item], check=False,
    )
    if dirty.returncode:
        fail(f"gate file differs from clean HEAD: {item}")
    if baseline_commit is not None:
        if not re.fullmatch(r"[0-9a-f]{40,64}", baseline_commit):
            fail("authoritative gate baseline is not an exact commit")
        baseline = _safe_run(
            ["git", "-C", str(repo), "show", f"{baseline_commit}:{item}"],
            capture_output=True, check=False,
        )
        if baseline.returncode:
            fail(f"authoritative gate baseline is missing: {item}")
        if baseline.stdout != committed.stdout:
            fail(f"gate file differs from authoritative baseline: {item}")
    actual_path = repo.joinpath(*parts)
    with _pinned_file_parents(actual_path):
        fd = _open_verified_file(actual_path)
        try:
            actual = _read_pinned(fd, actual_path)
        finally:
            os.close(fd)
    # Git's clean-index check is canonical-content based and Windows may materialize CRLF while
    # HEAD stores LF.  The execution transaction records the bytes from this verified handle;
    # baseline comparison above remains against Git's canonical blob.
    return actual


def entrypoint(words: list[str], strict: bool, *, controller_declared: bool = False) -> str | None:
    """Identify the only executable source file in the admitted direct-command class."""
    if not words:
        return None
    command = words[0].replace("\\", "/")
    name = PurePosixPath(command).name
    if strict and command != name and name in {
        "test", "[", "git", "bash", "sh", "python", "python3", "node",
    } and not controller_declared:
        fail(f"path-qualified acceptance launcher is not admitted: {command}")
    if strict and name in RESERVED:
        fail(f"shell reserved word or wrapper is not admitted: {command}")
    if name in {"env", "npm", "npx", "yarn", "pnpm", "xargs", "find", "make"}:
        if strict:
            fail(f"indirect acceptance launcher is not admitted: {name}")
        return None
    if name in {"test", "["}:
        return None
    # Repository descriptors may use read-only Git checks such as `git diff --check`; Git itself
    # is a controller-provided executable, not an admitted worker-modifiable grading file.
    if name == "git":
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


def _path_is_absolute(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return normalized.startswith("/") or bool(re.match(r"^[A-Za-z]:/", normalized))


def _path_has_traversal(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return any(part == ".." for part in normalized.split("/"))


def _controller_declared(value: str, controller_root: str | None,
                         controller_gate_files: list[str]) -> bool:
    if not controller_root or not _path_is_absolute(value):
        return False
    normalized = value.replace("\\", "/")
    logical_root = "/opt/recursion"
    if normalized == logical_root or normalized.startswith(logical_root + "/"):
        relative = normalized[len(logical_root):].lstrip("/")
        return relative in controller_gate_files
    root = _lexical_absolute(controller_root).as_posix().replace("\\", "/").rstrip("/")
    if normalized == root or normalized.startswith(root + "/"):
        return normalized[len(root):].lstrip("/") in controller_gate_files
    return False


def _reject_git_cwd_options(words: list[str]) -> None:
    """Reject Git options that can redirect a gate outside its detached worktree."""
    if not words or PurePosixPath(words[0].replace("\\", "/")).name != "git":
        return
    blocked_exact = {"-C", "--git-dir", "--work-tree", "--super-prefix", "--exec-path",
                     "--namespace", "-c", "--config", "--config-env", "-o", "--output"}
    blocked_prefixes = ("-C", "--git-dir", "--work-tree", "--super-prefix",
                       "--exec-path", "--namespace", "-c", "--config", "--config-env",
                       "-o", "--output")
    for word in words[1:]:
        if word in blocked_exact or any(word.startswith(prefix) and word != prefix
                                        for prefix in blocked_prefixes):
            fail(f"Git gate may not redirect its repository or configuration: {word}")


def _reject_shell_expansion(word: str) -> None:
    if any(char in word for char in "~%$`*?["):
        fail(f"acceptance operand contains shell expansion or glob syntax: {word}")
    normalized = word.replace("\\", "/")
    if normalized.startswith("//") or word.startswith("\\\\") \
            or re.match(r"^[A-Za-z]:(?:$|[^/])", normalized):
        fail(f"acceptance operand uses an absolute, UNC, or drive-relative path: {word}")


def _validate_git_subcommand(words: list[str]) -> None:
    if not words or PurePosixPath(words[0].replace("\\", "/")).name != "git":
        return
    if len(words) < 2 or words[1].startswith("-"):
        fail("Git gate must name an allowed read-only subcommand directly")
    allowed = {"diff", "status", "show", "rev-parse", "ls-files", "cat-file"}
    if words[1] not in allowed:
        fail(f"Git gate subcommand is not read-only and non-network: {words[1]}")
    # These read-only Git modes can still read or write paths outside the detached worktree.
    # Keep the allowlist useful for ordinary repository inspection without allowing that escape.
    for word in words[2:]:
        if word == "--no-index" or word.startswith("--no-index=") \
                or word == "--pathspec-file-nul" \
                or word == "--pathspec-from-file" \
                or word.startswith("--pathspec-from-file="):
            fail(f"Git gate option is not confined to the detached worktree: {word}")


def _declared_or_allowed(path: str, *, allowed: list[str], controller_root: str | None,
                         controller_gate_files: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    if _path_is_absolute(normalized):
        return _controller_declared(normalized, controller_root, controller_gate_files)
    return under(normalized, allowed) or normalized in controller_gate_files


def _path_operand_indexes(words: list[str]) -> set[int]:
    indexes: set[int] = set()
    test_words = words
    if words[:1] == ["["] and words[-1:] == ["]"]:
        test_words = ["test", *words[1:-1]]
    if test_words[:1] == ["test"]:
        # Only unary file predicates execute a path.  Comparison operands such as `test a != b`
        # remain literal values and are intentionally not treated as filesystem paths.
        file_predicates = {"-b", "-c", "-d", "-e", "-f", "-g", "-h", "-L", "-O", "-G",
                           "-k", "-p", "-r", "-s", "-S", "-u", "-w", "-x"}
        indexes.update(index + 1 for index, word in enumerate(test_words[1:], 1)
                       if word in file_predicates and index + 1 < len(test_words))
        for index, word in enumerate(test_words[1:], 1):
            if word in {"-ef", "-nt", "-ot"} and index + 1 < len(test_words):
                indexes.update({index, index + 1})
    if PurePosixPath(words[0].replace("\\", "/")).name == "git" and "--" in words[1:]:
        marker = words.index("--", 1)
        indexes.update(range(marker + 1, len(words)))
    return indexes


def validate_direct_argv(words: list[str], *, allowed: list[str], gate_files: list[str],
                         controller_root: str | None, controller_gate_files: list[str]) -> str | None:
    """Apply the strict direct-command policy to parsed argv, including every path operand."""
    if not words:
        return None
    test_words = words
    if words[0] == "[" and words[-1:] == ["]"]:
        test_words = ["test", *words[1:-1]]
    if test_words[:2] == ["test", "-n"] or (
        test_words[:1] == ["test"] and any(
            word in {"=", "==", "-eq"} for word in test_words[1:]
        )
    ):
        fail("literal test acceptance is structurally vacuous")
    if test_words[:1] == ["test"] and any(word in {"-ef", "-nt", "-ot"}
                                            for word in test_words[1:]):
        fail("binary filesystem test is not admitted as a confined gate")
    _validate_git_subcommand(words)
    _reject_git_cwd_options(words)
    command = words[0].replace("\\", "/")
    command_absolute = _path_is_absolute(command)
    if command_absolute:
        if not _controller_declared(command, controller_root, controller_gate_files):
            fail(f"absolute acceptance program is not controller-declared: {command}")
    elif _path_has_traversal(command):
        fail(f"acceptance executable path is unsafe: {command}")

    command_declared = command_absolute and _controller_declared(
        command, controller_root, controller_gate_files)
    candidate = entrypoint(words, True, controller_declared=command_declared)
    candidate_index = None
    if candidate is not None:
        # Locate the script operand in parsed argv rather than searching the raw command string.
        if command_declared:
            candidate_index = 0
        else:
            for index, word in enumerate(words[1:], 1):
                if not word.startswith("-"):
                    candidate_index = index
                    break
        normalized_candidate = candidate.replace("\\", "/")
        if _path_is_absolute(normalized_candidate):
            if not _controller_declared(normalized_candidate, controller_root, controller_gate_files):
                fail(f"absolute acceptance program is not controller-declared: {candidate}")
        elif _path_has_traversal(normalized_candidate):
            fail(f"acceptance program path is unsafe: {candidate}")
        elif under(normalized_candidate, allowed):
            if normalized_candidate not in gate_files:
                fail(f"worker-modifiable gate program must be declared in gate_files: {normalized_candidate}")
        elif normalized_candidate not in controller_gate_files:
            fail(f"gate program is outside allowed/controller-declared paths: {normalized_candidate}")

    path_indexes = _path_operand_indexes(words)
    for index, word in enumerate(words[1:], 1):
        _reject_shell_expansion(word)
        normalized = word.replace("\\", "/")
        if index == candidate_index:
            continue
        if _path_is_absolute(normalized) and not _controller_declared(
                normalized, controller_root, controller_gate_files):
            fail(f"acceptance path operand is outside declared controller files: {word}")
        if _path_has_traversal(normalized):
            fail(f"acceptance path operand is unsafe: {word}")
        if index in path_indexes and not _declared_or_allowed(
                normalized, allowed=allowed, controller_root=controller_root,
                controller_gate_files=controller_gate_files):
            fail(f"acceptance path operand is outside allowed/controller-declared paths: {word}")
    return candidate


def _execute_from_verified_files(command: str, repo: Path, controller_root: Path | None,
                                 gate_files: list[str], controller_gate_files: list[str],
                                 hashes: dict[str, str], controller_hashes: dict[str, str]) -> None:
    """Hash and execute from the same verified file handles.

    POSIX children receive `/proc/self/fd` spellings for every declared file that appears in the
    command, so the interpreter executes the inode that was hashed.  Windows keeps the
    no-follow handles open with delete sharing denied; the native gate files are controller-owned
    and cannot be replaced while this transaction is running.
    """
    opened: list[tuple[int, Path, str]] = []
    parent_pins = contextlib.ExitStack()
    try:
        for root, names, expected in ((repo, gate_files, hashes),
                                      (controller_root, controller_gate_files, controller_hashes)):
            if root is None:
                if names:
                    fail("controller gate files require a controller root")
                continue
            for item in names:
                path = root.joinpath(*PurePosixPath(item).parts)
                parent_pins.enter_context(_pinned_file_parents(path))
                fd = _open_verified_file(path)
                try:
                    actual = _read_pinned(fd, path)
                    if hashlib.sha256(actual).hexdigest() != expected.get(item):
                        fail(f"gate file changed before execution: {item}")
                    opened.append((fd, path, item))
                except BaseException:
                    os.close(fd)
                    raise

        executed = command
        if os.name != "nt":
            for fd, path, item in sorted(opened, key=lambda value: len(str(value[1])), reverse=True):
                fd_path = f"/proc/self/fd/{fd}"
                variants = {item, item.replace("\\", "/"), str(path),
                            str(path).replace("\\", "/"), f"/opt/recursion/{item}"}
                for variant in sorted((value for value in variants if value),
                                      key=len, reverse=True):
                    executed = executed.replace(variant, fd_path)
        environment = {key: value for key, value in os.environ.items()
                       if key in {"PATH", "HOME", "USERPROFILE", "SystemRoot", "WINDIR"}}
        environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                            "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"})
        run_args: dict[str, object] = {
            "shell": True, "cwd": repo, "env": environment, "stdin": subprocess.DEVNULL,
            "stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True,
            "encoding": "utf-8", "errors": "replace", "timeout": 120, "check": False,
        }
        if os.name != "nt":
            run_args["pass_fds"] = tuple(fd for fd, _, _ in opened)
        try:
            result = subprocess.run(executed, **run_args)  # type: ignore[arg-type]
        except BOUNDARY_ERRORS as exc:
            raise ValueError("controller gate execution was unavailable") from exc
        if result.returncode:
            fail("independent controller gate failed")
    finally:
        for fd, _, _ in reversed(opened):
            try:
                os.close(fd)
            except OSError:
                pass
        parent_pins.close()


def vacuous_success(words: list[str]) -> bool:
    """Recognize commands whose success is independent of the code under review."""
    if not words:
        return True
    # Shell grouping must not hide a literal success command.  shlex keeps `(true)` as
    # one token, so recognize balanced outer parentheses before the token checks below.
    grouped = " ".join(words).strip()
    while grouped.startswith("(") and grouped.endswith(")"):
        grouped = grouped[1:-1].strip()
    if grouped in {"true", ":", "/bin/true", "exit 0"}:
        return True
    if words[0] in {"true", ":", "/bin/true"}:
        return True
    if words[:2] == ["exit", "0"]:
        return True
    if words[0] in {"echo", "printf", "pwd"}:
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
    parser.add_argument("--baseline-commit")
    parser.add_argument("--strict-direct", action="store_true")
    parser.add_argument("--execute", action="store_true",
                        help="execute the exact gate after hash-at-execution provenance checks")
    args = parser.parse_args()
    try:
        raw_gate = args.acceptance
        gate = raw_gate.strip()
        if not gate or len(raw_gate) > 4096 or any(
            ord(ch) < 32 and ch not in "\t" for ch in raw_gate
        ):
            fail("acceptance gate must be bounded, single-line, and non-empty")
        if re.search(r"[~%$`]|(?<!&)&(?!&)|[|;<>]", gate):
            fail("acceptance gate contains shell expansion or metacharacters")
        compact = re.sub(r"\s+", " ", gate)
        if args.strict_direct and (
            any(token in gate for token in ("`", "$", "<(", ">(", "||", ";", "(", ")", "{", "}"))
            or re.search(r"(?<!\|)\|(?!\|)", gate)
            or re.search(r"(?<![&])&(?![&])", gate)
            or re.search(r"(?:^|[\s\"']|[/\\])\./", gate)
            or "<" in gate or ">" in gate
        ):
            fail("acceptance gate uses unreviewable shell indirection")
        if args.strict_direct:
            pattern = (STRICT_CONTROLLER_PATTERN
                       if args.controller_gate_files else STRICT_DIRECT_PATTERN)
            if not pattern.fullmatch(gate):
                fail("acceptance gate is outside the strict direct-command grammar")
        raw_segments = re.split(r"\s*(?:&&|\|\||;)\s*", gate)
        operators = re.findall(r"&&|\|\||;", gate)
        parsed_segments: list[list[str]] = []
        for segment in raw_segments:
            # Normalize Windows separators before POSIX-mode shlex can consume them. This keeps
            # quoted and unquoted argv forms on one path-policy implementation on every host.
            segment = segment.replace("\\", "/")
            try:
                parsed_segments.append(shlex.split(segment))
            except ValueError as exc:
                fail(f"acceptance gate cannot be parsed: {exc}")
        if any(not words for words in parsed_segments):
            fail("acceptance gate contains an empty command segment")
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
            if args.strict_direct:
                validate_direct_argv(words, allowed=allowed, gate_files=gate_files,
                                     controller_root=args.controller_root,
                                     controller_gate_files=controller_gate_files)
            else:
                candidate = entrypoint(words, args.strict_direct)
                if PurePosixPath(words[0].replace("\\", "/")).name == "git":
                    _validate_git_subcommand(words)
                path_indexes = _path_operand_indexes(words)
                for index, word in enumerate(words[1:], 1):
                    _reject_shell_expansion(word)
                    normalized = word.replace("\\", "/")
                    if _path_is_absolute(normalized) and not _controller_declared(
                            normalized, args.controller_root, controller_gate_files):
                        fail(f"acceptance path operand is outside declared controller files: {word}")
                    if _path_has_traversal(normalized):
                        fail(f"acceptance path operand is unsafe: {word}")
                    if index in path_indexes and not _declared_or_allowed(
                            normalized, allowed=allowed, controller_root=args.controller_root,
                            controller_gate_files=controller_gate_files):
                        fail(f"acceptance path operand is outside allowed/controller-declared paths: {word}")
                if candidate and PurePosixPath(candidate).is_absolute():
                    if not args.controller_root:
                        fail("absolute acceptance program lacks a controller root")
                    root = _lexical_absolute(args.controller_root).as_posix().replace("\\", "/").rstrip("/")
                    candidate_abs = candidate.replace("\\", "/")
                    if candidate_abs != root and not candidate_abs.startswith(root + "/"):
                        fail(f"acceptance program is outside the controller root: {candidate}")
                    relative = candidate_abs[len(root):].lstrip("/")
                    if relative not in controller_gate_files:
                        fail(f"controller acceptance program must be declared: {relative}")
                elif candidate and under(candidate, allowed) and candidate not in gate_files:
                    fail(f"worker-modifiable gate program must be declared in gate_files: {candidate}")
        hashes: dict[str, str] = {}
        if args.repo:
            repo = Path(args.repo)
            for item in gate_files:
                hashes[item] = hashlib.sha256(
                    clean_tracked_bytes(repo, item, args.baseline_commit)
                ).hexdigest()
        controller_hashes: dict[str, str] = {}
        if controller_gate_files:
            if not args.controller_root:
                fail("controller gate files require --controller-root")
            controller = Path(args.controller_root)
            for item in controller_gate_files:
                controller_hashes[item] = hashlib.sha256(clean_tracked_bytes(controller, item)).hexdigest()
        if args.execute:
            if not args.repo:
                fail("verified gate execution requires --repo")
            _execute_from_verified_files(
                gate, Path(args.repo),
                Path(args.controller_root) if args.controller_root else None,
                gate_files, controller_gate_files, hashes, controller_hashes,
            )
        print(json.dumps({"acceptance_sha256": hashlib.sha256(gate.encode()).hexdigest(),
                          "gate_files": hashes,
                          "controller_gate_files": controller_hashes}, sort_keys=True))
    except BOUNDARY_ERRORS as exc:
        print(f"ERR {exc}", file=sys.stderr)
        return 2
    except Exception:
        print("ERR gate validation failed", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

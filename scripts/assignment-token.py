#!/usr/bin/env python3
"""Mint one short-lived-in-practice provider capability for a controller assignment.

The key is read only from the human-owned credential path and the bearer token is written to
stdout for an in-memory caller.  Callers must not persist this output (plans and evidence are
intentionally token-free).
"""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import importlib.util
import os
import pathlib
import stat
import sys
from ctypes import wintypes


if os.name == "nt":
    import msvcrt
    _KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _CREATE_FILE_W = _KERNEL32.CreateFileW
    _CREATE_FILE_W.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                               wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    _CREATE_FILE_W.restype = wintypes.HANDLE
    _CLOSE_HANDLE = _KERNEL32.CloseHandle
    _CLOSE_HANDLE.argtypes = [wintypes.HANDLE]
    _CLOSE_HANDLE.restype = wintypes.BOOL


class AssignmentTokenRefusal(ValueError):
    """A safe, user-facing refusal message for capability issuance."""


def _is_reparse(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0)) \
        or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _open_pinned(path: pathlib.Path, *, directory: bool = False) -> int:
    """Open a path without following reparse points and without delete-sharing."""
    if os.name != "nt":
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        if directory:
            flags |= getattr(os, "O_DIRECTORY", 0)
        return os.open(path, flags)
    flags = 0x00200000 | (0x02000000 if directory else 0)  # OPEN_REPARSE_POINT/BACKUP_SEMANTICS
    handle = _CREATE_FILE_W(str(path), 0x80000000, 0x00000003, None, 3, flags, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except OSError:
        _CLOSE_HANDLE(handle)
        raise


@contextlib.contextmanager
def _pin_directory_chain(path: pathlib.Path):
    handles: list[int] = []
    current = pathlib.Path(path.anchor)
    try:
        for component in path.parts[1:]:
            current /= component
            info = current.lstat()
            if _is_reparse(info) or not stat.S_ISDIR(info.st_mode):
                raise AssignmentTokenRefusal("provider capability key is unavailable")
            descriptor = _open_pinned(current, directory=True)
            try:
                opened = os.fstat(descriptor)
                if _is_reparse(opened) or not stat.S_ISDIR(opened.st_mode) \
                        or (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                    raise AssignmentTokenRefusal("provider capability key is unavailable")
            except BaseException:
                os.close(descriptor)
                raise
            handles.append(descriptor)
        yield
    except (FileNotFoundError, OSError) as exc:
        raise AssignmentTokenRefusal("provider capability key is unavailable") from exc
    finally:
        for descriptor in reversed(handles):
            try:
                os.close(descriptor)
            except OSError:
                pass


def load_issue():
    path = pathlib.Path(__file__).with_name("provider-connect-proxy.py")
    spec = importlib.util.spec_from_file_location("recursion_provider_proxy", path)
    if spec is None or spec.loader is None:
        raise AssignmentTokenRefusal("provider capability issuer is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.issue_capability


def _reject_reparse_components(path: pathlib.Path) -> None:
    if not path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise AssignmentTokenRefusal("provider capability key path is not canonical")
    current = pathlib.Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise AssignmentTokenRefusal("provider capability key is unavailable") from exc
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) \
                or (getattr(info, "st_file_attributes", 0) & 0x400):
            raise AssignmentTokenRefusal("provider capability key is unavailable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="assignment-token")
    parser.add_argument("profile")
    parser.add_argument("assignment")
    parser.add_argument("--key-file", type=pathlib.Path,
                        default=pathlib.Path("/etc/recursion/provider-capability.key"))
    args = parser.parse_args(argv)
    try:
        path = args.key_file
        _reject_reparse_components(path)
        with _pin_directory_chain(path.parent):
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise AssignmentTokenRefusal("provider capability key is unavailable")
            if os.name != "nt" and stat.S_IMODE(info.st_mode) & 0o077:
                raise AssignmentTokenRefusal("provider capability key ownership/mode is unsafe")
            if hasattr(os, "geteuid") and os.geteuid() == 0 and info.st_uid != 0:
                raise AssignmentTokenRefusal("provider capability key ownership/mode is unsafe")
            if info.st_size < 32 or info.st_size > 1024 * 1024:
                raise AssignmentTokenRefusal("provider capability key has an invalid size")
            descriptor = _open_pinned(path)
            try:
                opened_info = os.fstat(descriptor)
                if _is_reparse(opened_info) or not stat.S_ISREG(opened_info.st_mode) \
                        or (opened_info.st_dev, opened_info.st_ino) != (info.st_dev, info.st_ino) \
                        or opened_info.st_size != info.st_size:
                    raise AssignmentTokenRefusal("provider capability key is unavailable")
                with os.fdopen(descriptor, "rb") as source:
                    descriptor = -1
                    secret = source.read(1024 * 1024 + 1)
            finally:
                if descriptor != -1:
                    os.close(descriptor)
        if len(secret) > 1024 * 1024:
            raise AssignmentTokenRefusal("provider capability key has an invalid size")
        token = load_issue()(args.profile, args.assignment, secret)
        sys.stdout.write(token + "\n")
        return 0
    except AssignmentTokenRefusal as exc:
        print(f"assignment-token: {exc}", file=sys.stderr)
        return 96
    except OSError:
        print("assignment-token: provider capability key is unavailable", file=sys.stderr)
        return 96
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError):
        print("assignment-token: provider capability issuance is unavailable", file=sys.stderr)
        return 96


if __name__ == "__main__":
    raise SystemExit(main())

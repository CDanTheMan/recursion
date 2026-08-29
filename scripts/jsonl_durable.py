#!/usr/bin/env python3
"""Crash-safe JSONL validation and append helpers.

Callers remain responsible for holding the journal's existing serialization lock.  This
module deliberately does not acquire taskctl.lock: discovering a damaged tail while that
lock is already held must still be able to preserve durable evidence without deadlocking.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import stat
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - production is Linux; Windows tests are sequential.
    fcntl = None  # type: ignore[assignment]
try:
    import msvcrt
except ImportError:  # pragma: no cover - production is Linux.
    msvcrt = None  # type: ignore[assignment]


if os.name == "nt":
    import ctypes

    _LOCK_KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _LOCK_INVALID_HANDLE = ctypes.c_void_p(-1).value
    _LOCK_GENERIC_READ = 0x80000000
    _LOCK_GENERIC_WRITE = 0x40000000
    _LOCK_SHARE_READ = 0x00000001
    _LOCK_SHARE_WRITE = 0x00000002
    _LOCK_OPEN_EXISTING = 3
    _LOCK_OPEN_ALWAYS = 4
    _LOCK_FILE_ATTRIBUTE_NORMAL = 0x00000080
    _LOCK_FILE_ATTRIBUTE_DIRECTORY = 0x00000010
    _LOCK_FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
    _LOCK_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
    _LOCK_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
    _LOCK_FILE_ATTRIBUTE_TAG_INFO = 9

    class _LOCK_FILE_ATTRIBUTE_TAG_INFO_STRUCT(ctypes.Structure):
        _fields_ = [
            ("FileAttributes", ctypes.c_uint32),
            ("ReparseTag", ctypes.c_uint32),
            ("Reserved", ctypes.c_uint32),
        ]

    class _LOCK_FILETIME_STRUCT(ctypes.Structure):
        _fields_ = [("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]

    class _LOCK_BY_HANDLE_FILE_INFORMATION_STRUCT(ctypes.Structure):
        _fields_ = [
            ("FileAttributes", ctypes.c_uint32),
            ("CreationTime", _LOCK_FILETIME_STRUCT),
            ("LastAccessTime", _LOCK_FILETIME_STRUCT),
            ("LastWriteTime", _LOCK_FILETIME_STRUCT),
            ("VolumeSerialNumber", ctypes.c_uint32),
            ("FileSizeHigh", ctypes.c_uint32),
            ("FileSizeLow", ctypes.c_uint32),
            ("NumberOfLinks", ctypes.c_uint32),
            ("FileIndexHigh", ctypes.c_uint32),
            ("FileIndexLow", ctypes.c_uint32),
        ]

    _LOCK_KERNEL32.CreateFileW.argtypes = [
        ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
    ]
    _LOCK_KERNEL32.CreateFileW.restype = ctypes.c_void_p
    _LOCK_KERNEL32.GetFileInformationByHandleEx.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32,
    ]
    _LOCK_KERNEL32.GetFileInformationByHandleEx.restype = ctypes.c_int
    _LOCK_KERNEL32.GetFileInformationByHandle.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(_LOCK_BY_HANDLE_FILE_INFORMATION_STRUCT),
    ]
    _LOCK_KERNEL32.GetFileInformationByHandle.restype = ctypes.c_int
    _LOCK_KERNEL32.CloseHandle.argtypes = [ctypes.c_void_p]
    _LOCK_KERNEL32.CloseHandle.restype = ctypes.c_int


def _win_lock_handle_attributes(handle: int) -> int:
    info = _LOCK_FILE_ATTRIBUTE_TAG_INFO_STRUCT()
    if not _LOCK_KERNEL32.GetFileInformationByHandleEx(
            ctypes.c_void_p(handle), _LOCK_FILE_ATTRIBUTE_TAG_INFO,
            ctypes.byref(info), ctypes.sizeof(info)):
        raise OSError(ctypes.get_last_error(), "cannot inspect Windows durable-lock path")
    return int(info.FileAttributes)


def _win_lock_handle_identity(handle: int) -> tuple[int, int, int]:
    info = _LOCK_BY_HANDLE_FILE_INFORMATION_STRUCT()
    if not _LOCK_KERNEL32.GetFileInformationByHandle(
            ctypes.c_void_p(handle), ctypes.byref(info)):
        raise OSError(ctypes.get_last_error(), "cannot identify Windows durable-lock path")
    return int(info.VolumeSerialNumber), int(info.FileIndexHigh), int(info.FileIndexLow)


def _win_lock_handle_links(handle: int) -> int:
    info = _LOCK_BY_HANDLE_FILE_INFORMATION_STRUCT()
    if not _LOCK_KERNEL32.GetFileInformationByHandle(
            ctypes.c_void_p(handle), ctypes.byref(info)):
        raise OSError(ctypes.get_last_error(), "cannot inspect Windows durable path links")
    return int(info.NumberOfLinks)


def _win_open_leaf_identity(path: Path) -> tuple[tuple[int, int, int], int]:
    handle = _LOCK_KERNEL32.CreateFileW(
        str(path), _LOCK_GENERIC_READ,
        _LOCK_SHARE_READ | _LOCK_SHARE_WRITE, None, _LOCK_OPEN_EXISTING,
        _LOCK_FILE_ATTRIBUTE_NORMAL | _LOCK_FILE_FLAG_OPEN_REPARSE_POINT, None,
    )
    if handle in (None, _LOCK_INVALID_HANDLE):
        raise OSError(ctypes.get_last_error(), f"cannot revalidate Windows durable leaf {path}")
    try:
        attributes = _win_lock_handle_attributes(int(handle))
        if attributes & _LOCK_FILE_ATTRIBUTE_REPARSE_POINT:
            raise JsonlDurabilityError(f"Windows durable leaf is a reparse point: {path}")
        if attributes & _LOCK_FILE_ATTRIBUTE_DIRECTORY:
            raise JsonlDurabilityError(f"Windows durable leaf is a directory: {path}")
        return _win_lock_handle_identity(int(handle)), _win_lock_handle_links(int(handle))
    finally:
        _LOCK_KERNEL32.CloseHandle(ctypes.c_void_p(handle))


def _win_validate_opened_leaf(path: Path, descriptor: int) -> None:
    handle = msvcrt.get_osfhandle(descriptor)
    attributes = _win_lock_handle_attributes(int(handle))
    if attributes & _LOCK_FILE_ATTRIBUTE_REPARSE_POINT:
        raise JsonlDurabilityError(f"Windows durable leaf is a reparse point: {path}")
    if attributes & _LOCK_FILE_ATTRIBUTE_DIRECTORY:
        raise JsonlDurabilityError(f"Windows durable leaf is a directory: {path}")
    identity = _win_lock_handle_identity(int(handle))
    links = _win_lock_handle_links(int(handle))
    if links != 1:
        raise JsonlDurabilityError(f"Windows durable leaf has {links} hard links: {path}")
    path_identity, path_links = _win_open_leaf_identity(path)
    if path_links != 1 or path_identity != identity:
        raise JsonlDurabilityError(f"Windows durable leaf changed while opening: {path}")


def _win_open_lock_directory(path: Path) -> int:
    """Pin one real directory without granting delete/rename sharing."""
    handle = _LOCK_KERNEL32.CreateFileW(
        str(path), _LOCK_GENERIC_READ,
        _LOCK_SHARE_READ | _LOCK_SHARE_WRITE, None, _LOCK_OPEN_EXISTING,
        _LOCK_FILE_FLAG_BACKUP_SEMANTICS | _LOCK_FILE_FLAG_OPEN_REPARSE_POINT, None,
    )
    if handle in (None, _LOCK_INVALID_HANDLE):
        error = ctypes.get_last_error()
        if error in (2, 3):
            raise FileNotFoundError(error, f"cannot pin Windows durable-lock directory {path}")
        raise OSError(error, f"cannot pin Windows durable-lock directory {path}")
    try:
        attributes = _win_lock_handle_attributes(int(handle))
        if attributes & _LOCK_FILE_ATTRIBUTE_REPARSE_POINT:
            raise JsonlDurabilityError(
                f"durable JSONL lock parent is a reparse point: {path}"
            )
        if not attributes & _LOCK_FILE_ATTRIBUTE_DIRECTORY:
            raise JsonlDurabilityError(
                f"durable JSONL lock parent is not a directory: {path}"
            )
        return int(handle)
    except BaseException:
        _LOCK_KERNEL32.CloseHandle(ctypes.c_void_p(handle))
        raise


def _win_pin_lock_parent(path: Path, *, create: bool = True) -> list[tuple[Path, int, tuple[int, int, int]]]:
    """Create and pin every parent component before the lock leaf is opened.

    Each already-pinned parent denies delete sharing before its child is created or
    inspected.  Consequently no checked prefix can be renamed and replaced with a
    junction while a later component or the lock leaf is opened by pathname.
    """
    absolute = Path(os.path.abspath(path))
    parts = absolute.parts
    if not parts:
        raise JsonlDurabilityError("cannot pin an empty Windows durable-lock parent")
    pins: list[tuple[Path, int, tuple[int, int, int]]] = []
    current = Path(parts[0])
    try:
        handle = _win_open_lock_directory(current)
        try:
            identity = _win_lock_handle_identity(handle)
        except BaseException:
            _LOCK_KERNEL32.CloseHandle(ctypes.c_void_p(handle))
            raise
        pins.append((current, handle, identity))
        for component in parts[1:]:
            current = current / component
            if create:
                try:
                    # Python's Windows mode=0o700 creates a directory ACL that can deny the
                    # current user its own inherited access.  NTFS permissions are inherited
                    # here; the native handles below provide the rename/delete protection.
                    current.mkdir(mode=0o777)
                except FileExistsError:
                    pass
            handle = _win_open_lock_directory(current)
            try:
                identity = _win_lock_handle_identity(handle)
            except BaseException:
                _LOCK_KERNEL32.CloseHandle(ctypes.c_void_p(handle))
                raise
            pins.append((current, handle, identity))
        return pins
    except BaseException:
        for _, handle, _ in reversed(pins):
            _LOCK_KERNEL32.CloseHandle(ctypes.c_void_p(handle))
        raise


def _win_validate_lock_parent_pins(
        pins: list[tuple[Path, int, tuple[int, int, int]]]) -> None:
    """Prove the post-open path still resolves to every pinned directory identity."""
    for path, _, identity in pins:
        current = _win_open_lock_directory(path)
        try:
            if _win_lock_handle_identity(current) != identity:
                raise JsonlDurabilityError(
                    f"durable JSONL lock parent changed while opening lock: {path}"
                )
        finally:
            _LOCK_KERNEL32.CloseHandle(ctypes.c_void_p(current))


def _win_close_lock_parent_pins(
        pins: list[tuple[Path, int, tuple[int, int, int]]]) -> None:
    for _, handle, _ in reversed(pins):
        _LOCK_KERNEL32.CloseHandle(ctypes.c_void_p(handle))


def _open_durable_lock(path: Path) -> int:
    """Atomically open a regular lock leaf without following a Windows reparse point."""
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0)
    if os.name != "nt":
        descriptor = os.open(path, flags | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            _validate_opened_leaf(path, descriptor)
            return descriptor
        except BaseException:
            os.close(descriptor)
            raise

    if msvcrt is None:  # pragma: no cover - CPython on Windows always provides it.
        raise JsonlDurabilityError("Windows durable locking requires msvcrt")
    handle = _LOCK_KERNEL32.CreateFileW(
        str(path), _LOCK_GENERIC_READ | _LOCK_GENERIC_WRITE,
        _LOCK_SHARE_READ | _LOCK_SHARE_WRITE, None, _LOCK_OPEN_ALWAYS,
        _LOCK_FILE_ATTRIBUTE_NORMAL | _LOCK_FILE_FLAG_OPEN_REPARSE_POINT, None,
    )
    if handle in (None, _LOCK_INVALID_HANDLE):
        raise OSError(ctypes.get_last_error(), f"cannot open Windows durable lock {path}")
    try:
        if _win_lock_handle_attributes(int(handle)) & _LOCK_FILE_ATTRIBUTE_REPARSE_POINT:
            raise JsonlDurabilityError(f"durable JSONL lock is a reparse point: {path}")
        links = _win_lock_handle_links(int(handle))
        if links != 1:
            raise JsonlDurabilityError(f"durable JSONL lock has {links} hard links: {path}")
        descriptor = msvcrt.open_osfhandle(
            int(handle), os.O_RDWR | getattr(os, "O_BINARY", 0),
        )
        handle = None  # the CRT descriptor now owns the native handle
        _validate_opened_leaf(path, descriptor)
        return descriptor
    finally:
        if handle not in (None, _LOCK_INVALID_HANDLE):
            _LOCK_KERNEL32.CloseHandle(ctypes.c_void_p(handle))


DEFAULT_MAX_RECORD_BYTES = 4 * 1024 * 1024
COPY_CHUNK_BYTES = 1024 * 1024
INDEX_SCHEMA_VERSION = 1
INDEX_AUTHORITY = "jsonl-verification-index-v1"
ZERO_CHAIN_SHA256 = "0" * 64


class JsonlDurabilityError(RuntimeError):
    """The existing journal cannot safely accept or expose another record."""


def _durable_path(path: Path) -> Path:
    try:
        return Path(path)
    except (TypeError, ValueError) as exc:
        raise JsonlDurabilityError("durable path is invalid") from exc


class _PinnedIndexConnection(sqlite3.Connection):
    """SQLite connection that releases the native cache pins when it closes."""

    _durable_parent_pins: list[tuple[Path, int, tuple[int, ...]]] = []
    _durable_leaf_descriptor: int | None = None
    _durable_leaf_identity: tuple[int, ...] | None = None
    _durable_leaf_path: Path | None = None
    _durable_index_path: Path | None = None
    _durable_journal_parent_pins: list[tuple[Path, int, tuple[int, ...]]] = []

    def _release_durable_pins(self) -> None:
        pins = self._durable_parent_pins
        descriptor = self._durable_leaf_descriptor
        self._durable_parent_pins = []
        self._durable_leaf_descriptor = None
        self._durable_leaf_identity = None
        self._durable_leaf_path = None
        self._durable_index_path = None
        journal_pins = self._durable_journal_parent_pins
        self._durable_journal_parent_pins = []
        if descriptor is not None:
            os.close(descriptor)
        if pins:
            _close_durable_parent_pins(pins)
        if journal_pins:
            _close_durable_parent_pins(journal_pins)

    def _detach_durable_leaf(self) -> int | None:
        """Transfer the verification descriptor to a caller before closing SQLite."""
        descriptor = self._durable_leaf_descriptor
        self._durable_leaf_descriptor = None
        self._durable_leaf_identity = None
        self._durable_leaf_path = None
        self._durable_index_path = None
        self._durable_parent_pins = []
        return descriptor

    def close(self) -> None:
        try:
            super().close()
        finally:
            self._release_durable_pins()

    def __del__(self) -> None:  # pragma: no cover - interpreter cleanup is not deterministic.
        try:
            self.close()
        except BaseException:
            pass


def _reject_symlink_components(path: Path) -> None:
    """Reject links/reparse points before any durable state operation follows them."""
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor) if absolute.anchor else Path()
    parts = absolute.parts[1:] if absolute.anchor else absolute.parts
    for part in parts:
        current = current / part
        try:
            metadata = os.lstat(current)
            reparse_attribute = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
            if stat.S_ISLNK(metadata.st_mode) or (
                os.name == "nt"
                and bool(getattr(metadata, "st_file_attributes", 0) & reparse_attribute)
            ):
                raise JsonlDurabilityError(f"JSONL path contains a link or reparse point: {current}")
        except FileNotFoundError:
            continue


def ensure_no_symlink(path: Path) -> None:
    """Public path-confinement check used by higher-level append transactions."""
    _reject_symlink_components(Path(path))


def _validate_opened_leaf(path: Path, descriptor: int) -> None:
    metadata = os.fstat(descriptor)
    if not stat.S_ISREG(metadata.st_mode):
        raise JsonlDurabilityError(f"JSONL durable leaf is not a regular file: {path}")
    if metadata.st_nlink != 1:
        raise JsonlDurabilityError(f"JSONL durable leaf has {metadata.st_nlink} hard links: {path}")
    if os.name == "nt":
        _win_validate_opened_leaf(path, descriptor)
        return
    try:
        opened = os.lstat(path)
    except OSError as exc:
        raise JsonlDurabilityError(f"JSONL durable leaf disappeared while opening: {path}") from exc
    if stat.S_ISLNK(opened.st_mode) or opened.st_nlink != 1 \
            or (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino):
        raise JsonlDurabilityError(f"JSONL durable leaf changed while opening: {path}")


def _leaf_identity(descriptor: int) -> tuple[int, ...]:
    """Return the stable identity used for same-handle write revalidation."""
    metadata = os.fstat(descriptor)
    if not stat.S_ISREG(metadata.st_mode):
        raise JsonlDurabilityError("JSONL durable write target is not a regular file")
    if metadata.st_nlink != 1:
        raise JsonlDurabilityError(
            f"JSONL durable write target has {metadata.st_nlink} hard links"
        )
    if os.name == "nt":
        handle = msvcrt.get_osfhandle(descriptor)
        attributes = _win_lock_handle_attributes(int(handle))
        if attributes & _LOCK_FILE_ATTRIBUTE_REPARSE_POINT:
            raise JsonlDurabilityError("Windows durable write target is a reparse point")
        if attributes & _LOCK_FILE_ATTRIBUTE_DIRECTORY:
            raise JsonlDurabilityError("Windows durable write target is a directory")
        return _win_lock_handle_identity(int(handle))
    return int(metadata.st_dev), int(metadata.st_ino)


def _capture_opened_leaf(path: Path, descriptor: int) -> tuple[int, ...]:
    """Validate and capture the identity of a leaf immediately after opening it."""
    _validate_opened_leaf(path, descriptor)
    try:
        return _leaf_identity(descriptor)
    except OSError as exc:
        raise JsonlDurabilityError(
            f"cannot identify JSONL durable write target {path}: {exc}"
        ) from exc


def _revalidate_opened_leaf(path: Path, descriptor: int,
                            expected: tuple[int, ...]) -> None:
    """Prove that an opened leaf is still the one-link file captured at open time.

    The descriptor check is the authoritative part: on Windows an open handle does not
    prevent a new hardlink from being created, so a pathname-only check immediately before
    ``os.write`` is not sufficient.  The by-name comparison also catches replacement of the
    pathname with a different regular file before a write or publication.
    """
    try:
        actual = _leaf_identity(descriptor)
        if actual != expected:
            raise JsonlDurabilityError(
                f"JSONL durable leaf identity changed while writing: {path}"
            )
        if os.name == "nt":
            path_identity, path_links = _win_open_leaf_identity(path)
            if path_links != 1 or path_identity != expected:
                raise JsonlDurabilityError(
                    f"Windows durable leaf changed while writing: {path}"
                )
        else:
            opened = os.lstat(path)
            if stat.S_ISLNK(opened.st_mode) or not stat.S_ISREG(opened.st_mode) \
                    or opened.st_nlink != 1 \
                    or (opened.st_dev, opened.st_ino) != expected:
                raise JsonlDurabilityError(
                    f"JSONL durable leaf changed while writing: {path}"
                )
    except JsonlDurabilityError:
        raise
    except OSError as exc:
        raise JsonlDurabilityError(
            f"cannot revalidate JSONL durable leaf {path}: {exc}"
        ) from exc


def validate_durable_leaf(path: Path, *, allow_missing: bool = False) -> None:
    """Reject non-regular, linked, or replaced by-name durable leaves."""
    path = _durable_path(path)
    try:
        metadata = os.lstat(path)
    except FileNotFoundError:
        if allow_missing:
            return
        raise JsonlDurabilityError(f"JSONL durable leaf is absent: {path}") from None
    except OSError as exc:
        raise JsonlDurabilityError(f"cannot inspect JSONL durable leaf {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise JsonlDurabilityError(f"JSONL durable leaf has unsafe type: {path}")
    if metadata.st_nlink != 1:
        raise JsonlDurabilityError(f"JSONL durable leaf has {metadata.st_nlink} hard links: {path}")
    if os.name == "nt":
        identity, links = _win_open_leaf_identity(path)
        if links != 1:
            raise JsonlDurabilityError(f"Windows durable leaf has {links} hard links: {path}")
        # The native open above is the authoritative reparse/type/identity check.  The
        # lstat check remains useful for detecting a non-Windows link representation.
        if not identity:
            raise JsonlDurabilityError(f"cannot identify Windows durable leaf: {path}")


def _connect_verified_index(index_path: Path) -> sqlite3.Connection:
    """Load a verified cache into memory without giving SQLite a switchable pathname.

    ``sqlite3.connect(index_path)`` opens its own native file handle after the caller's
    validation.  On Windows an attacker can add a hardlink in that interval, leaving the
    SQLite-owned handle outside the authority boundary even when a second validation handle
    still reports the original identity.  A verification index is a rebuildable derivative,
    so keep SQLite entirely in memory and publish only a serialized replacement through the
    pinned durable writer.
    """
    connection: sqlite3.Connection | None = None
    try:
        index_path = Path(index_path)
        raw = read_durable_bytes(index_path)
        if raw is None:
            raise FileNotFoundError(index_path)
        connection = sqlite3.connect(":memory:", factory=_PinnedIndexConnection)
        connection._durable_index_path = index_path
        connection.deserialize(raw)
        return connection
    except BaseException:
        if connection is not None:
            connection.close()
        raise


def _win_pin_durable_parent(path: Path, *, create: bool = True) -> list[tuple[Path, int, tuple[int, int, int]]]:
    if os.name != "nt":
        return []
    return _win_pin_lock_parent(Path(path), create=create)


def _posix_pin_durable_parent(path: Path, *, create: bool = True) -> list[tuple[Path, int, tuple[int, int]]]:
    """Open every POSIX parent component and retain the descriptor for each one.

    A pathname check cannot pin a directory: a peer can rename that directory after the
    check and replace it with a symlink or another tree.  Every child below is therefore
    opened relative to the already pinned parent, with ``O_NOFOLLOW|O_DIRECTORY``.  The
    descriptors remain live for the whole operation, so later creates, appends, and
    replacements can use the final descriptor rather than resolving the pathname again.
    """
    if os.name == "nt":
        return []
    required_dir_fd = (os.open, os.mkdir, os.stat)
    if (not hasattr(os, "supports_dir_fd")
            or not all(function in os.supports_dir_fd for function in required_dir_fd)):
        raise JsonlDurabilityError(
            "POSIX durable pinning requires openat-capable directory descriptors"
        )
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    if not nofollow or not directory_flag:
        raise JsonlDurabilityError("O_NOFOLLOW and O_DIRECTORY are required for POSIX durable pinning")
    absolute = Path(os.path.abspath(path))
    if not absolute.anchor:
        raise JsonlDurabilityError("cannot pin a relative POSIX durable parent")
    flags = os.O_RDONLY | directory_flag | nofollow | getattr(os, "O_CLOEXEC", 0)
    pins: list[tuple[Path, int, tuple[int, int]]] = []
    current = Path(absolute.anchor)
    try:
        current_fd = os.open(current, flags)
        try:
            anchor_stat = os.fstat(current_fd)
            if not stat.S_ISDIR(anchor_stat.st_mode):
                raise JsonlDurabilityError(
                    f"POSIX durable parent anchor is not a directory: {current}"
                )
            pins.append((current, current_fd, (int(anchor_stat.st_dev), int(anchor_stat.st_ino))))
        except BaseException:
            os.close(current_fd)
            raise
        for component in absolute.parts[1:]:
            current = current / component
            try:
                if create:
                    os.mkdir(component, mode=0o700, dir_fd=current_fd)
            except FileExistsError:
                pass
            child_fd = os.open(component, flags, dir_fd=current_fd)
            try:
                child_stat = os.fstat(child_fd)
                child_identity = (int(child_stat.st_dev), int(child_stat.st_ino))
                named_stat = os.stat(component, dir_fd=current_fd, follow_symlinks=False)
                if (not stat.S_ISDIR(child_stat.st_mode)
                        or stat.S_ISLNK(named_stat.st_mode)
                        or (int(named_stat.st_dev), int(named_stat.st_ino)) != child_identity):
                    raise JsonlDurabilityError(
                        f"POSIX durable parent changed or is not a directory: {current}"
                    )
            except BaseException:
                os.close(child_fd)
                raise
            pins.append((current, child_fd, child_identity))
            current_fd = child_fd
        return pins
    except BaseException:
        for _, descriptor, _ in reversed(pins):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise


def revalidate_durable_parent_pins(
        pins: list[tuple[Path, int, tuple[int, ...]]]) -> None:
    if not pins:
        return
    if os.name == "nt":
        _win_validate_lock_parent_pins(pins)
        return
    for path, descriptor, expected in pins:
        try:
            actual = os.fstat(descriptor)
            named = os.stat(path, follow_symlinks=False)
        except OSError as exc:
            raise JsonlDurabilityError(
                f"POSIX durable parent changed while writing: {path}"
            ) from exc
        if (not stat.S_ISDIR(actual.st_mode) or not stat.S_ISDIR(named.st_mode)
                or stat.S_ISLNK(named.st_mode)
                or (int(actual.st_dev), int(actual.st_ino)) != expected
                or (int(named.st_dev), int(named.st_ino)) != expected):
            raise JsonlDurabilityError(f"POSIX durable parent changed while writing: {path}")


def _close_durable_parent_pins(pins: list[tuple[Path, int, tuple[int, ...]]]) -> None:
    if not pins:
        return
    if os.name == "nt":
        _win_close_lock_parent_pins(pins)
        return
    for _, descriptor, _ in reversed(pins):
        try:
            os.close(descriptor)
        except OSError:
            pass


def _revalidate_index_connection(connection: sqlite3.Connection,
                                 index_path: Path | None = None) -> None:
    descriptor = getattr(connection, "_durable_leaf_descriptor", None)
    identity = getattr(connection, "_durable_leaf_identity", None)
    target = getattr(connection, "_durable_leaf_path", None) or index_path
    if descriptor is None and getattr(connection, "_durable_index_path", None) is not None:
        # The cache is memory-backed.  Its eventual disk publication is validated by the
        # serialized durable writer, so there is no disk handle to revalidate here.
        return
    if descriptor is None or identity is None or target is None:
        raise JsonlDurabilityError(
            f"JSONL verification cache has no revalidation handle: {target or '<unknown>'}"
        )
    _revalidate_opened_leaf(Path(target), descriptor, identity)


def _maybe_revalidate_index_connection(connection: sqlite3.Connection) -> None:
    """Revalidate disk-backed caches while leaving the in-memory pinned path unchanged."""
    revalidate_durable_parent_pins(getattr(connection, "_durable_parent_pins", []))
    if getattr(connection, "_durable_leaf_descriptor", None) is not None:
        _revalidate_index_connection(connection)


def _install_serialized_cache_path(index_path: Path, cache_bytes: bytes,
                                   hook: Callable[[str], None] | None = None) -> None:
    """Publish a memory-backed SQLite cache through the pinned atomic byte writer."""
    if not isinstance(cache_bytes, bytes):
        raise JsonlDurabilityError("serialized JSONL verification cache is not bytes")
    atomic_bytes(index_path, cache_bytes, hook=hook)


@contextmanager
def pinned_durable_parent(path: Path, *, create: bool = True):
    """Pin a durable parent tree while a by-name leaf is created or published."""
    pins = (_win_pin_durable_parent(Path(path), create=create)
            if os.name == "nt" else _posix_pin_durable_parent(Path(path), create=create))
    try:
        revalidate_durable_parent_pins(pins)
        yield pins
    finally:
        _close_durable_parent_pins(pins)


def _open_durable_leaf(path: Path, flags: int, mode: int = 0o600,
                       *, directory_fd: int | None = None) -> int:
    """Open a durable regular leaf and prove its identity before returning it."""
    path = Path(path)
    if os.name != "nt":
        open_name: str | Path = path
        validation_path = path
        if directory_fd is not None:
            if not path.name or path.name in {".", ".."}:
                raise JsonlDurabilityError("invalid pinned durable leaf name")
            open_name = path.name
            validation_path = _pinned_fd_path(directory_fd, path.name)
        descriptor = os.open(
            open_name, flags | getattr(os, "O_NOFOLLOW", 0), mode,
            **({"dir_fd": directory_fd} if directory_fd is not None else {}),
        )
        try:
            _validate_opened_leaf(validation_path, descriptor)
            return descriptor
        except BaseException:
            os.close(descriptor)
            raise
    else:
        if msvcrt is None:  # pragma: no cover - CPython on Windows always provides msvcrt.
            raise JsonlDurabilityError("Windows durable persistence requires msvcrt")
        access = _LOCK_GENERIC_WRITE if flags & (os.O_WRONLY | os.O_RDWR) else _LOCK_GENERIC_READ
        if flags & os.O_RDWR:
            access |= _LOCK_GENERIC_READ
        disposition = _LOCK_OPEN_ALWAYS if flags & os.O_CREAT else _LOCK_OPEN_EXISTING
        handle = _LOCK_KERNEL32.CreateFileW(
            str(path), access, _LOCK_SHARE_READ | _LOCK_SHARE_WRITE, None, disposition,
            _LOCK_FILE_ATTRIBUTE_NORMAL | _LOCK_FILE_FLAG_OPEN_REPARSE_POINT, None,
        )
        if handle in (None, _LOCK_INVALID_HANDLE):
            error = ctypes.get_last_error()
            if error in (2, 3):
                raise FileNotFoundError(error, f"cannot open Windows durable leaf {path}")
            raise OSError(error, f"cannot open Windows durable leaf {path}")
        try:
            descriptor = msvcrt.open_osfhandle(int(handle), flags | getattr(os, "O_BINARY", 0))
            handle = None
        finally:
            if handle not in (None, _LOCK_INVALID_HANDLE):
                _LOCK_KERNEL32.CloseHandle(ctypes.c_void_p(handle))
    try:
        _validate_opened_leaf(path, descriptor)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def read_durable_bytes(path: Path, *, max_bytes: int = 64 * 1024 * 1024) -> bytes | None:
    """Read one regular, one-link leaf while its checked parent tree is pinned.

    The pathname is used only to open the leaf.  All bytes are then read from that same
    descriptor, and the descriptor identity/link count is checked again immediately before
    each read.  ``None`` means the leaf or one of its parents is absent.
    """
    try:
        path = Path(path)
        if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes < 0:
            raise JsonlDurabilityError("durable read max_bytes must be a non-negative integer")
        if os.name != "nt":
            ensure_no_symlink(path.parent)
            ensure_no_symlink(path)
        with pinned_durable_parent(path.parent, create=False) as pins:
            revalidate_durable_parent_pins(pins)
            try:
                descriptor = _open_durable_leaf(
                    path, os.O_RDONLY | getattr(os, "O_BINARY", 0),
                    directory_fd=pins[-1][1] if os.name != "nt" else None,
                )
            except FileNotFoundError:
                return None
            opened_path = (_pinned_fd_path(pins[-1][1], path.name)
                           if os.name != "nt" else path)
            try:
                identity = _capture_opened_leaf(opened_path, descriptor)
                chunks: list[bytes] = []
                total = 0
                while True:
                    _revalidate_opened_leaf(opened_path, descriptor, identity)
                    chunk = os.read(descriptor, min(COPY_CHUNK_BYTES, max_bytes - total + 1))
                    if not chunk:
                        return b"".join(chunks)
                    total += len(chunk)
                    if total > max_bytes:
                        raise JsonlDurabilityError(
                            f"durable read exceeds {max_bytes} bytes: {path}"
                        )
                    chunks.append(chunk)
            finally:
                os.close(descriptor)
    except JsonlDurabilityError:
        raise
    except FileNotFoundError:
        return None
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError) as exc:
        raise JsonlDurabilityError(f"durable read refused: {path}: {exc}") from exc


def validate_durable_leaf_at(directory: int, name: str, *, allow_missing: bool = False) -> None:
    """Validate a single child addressed through a pinned POSIX directory descriptor."""
    if os.name == "nt" or not isinstance(directory, int) or not isinstance(name, str) \
            or not name or Path(name).name != name:
        raise JsonlDurabilityError("invalid pinned durable leaf name")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=directory)
    except FileNotFoundError:
        if allow_missing:
            return
        raise JsonlDurabilityError(f"pinned durable leaf is absent: {name}") from None
    try:
        path = _pinned_fd_path(directory, name)
        identity = _capture_opened_leaf(path, descriptor)
        _revalidate_opened_leaf(path, descriptor, identity)
    except (JsonlDurabilityError, OSError) as exc:
        if isinstance(exc, JsonlDurabilityError):
            raise
        raise JsonlDurabilityError(f"cannot validate pinned durable leaf {name}: {exc}") from exc
    finally:
        os.close(descriptor)


def _lock_attempts() -> tuple[int, float]:
    try:
        attempts = max(1, int(os.environ.get("RECURSION_DURABLE_LOCK_ATTEMPTS", "100")))
    except (TypeError, ValueError, OverflowError):
        attempts = 100
    try:
        delay = max(0.0, float(os.environ.get("RECURSION_DURABLE_LOCK_DELAY_S", "0.01")))
        if not math.isfinite(delay):
            raise ValueError("non-finite durable lock delay")
    except (TypeError, ValueError, OverflowError):
        delay = 0.01
    return attempts, delay


def _lock_file_descriptor(descriptor: int) -> None:
    attempts, delay = _lock_attempts()
    if fcntl is not None:
        for attempt in range(attempts):
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return
            except BlockingIOError:
                if attempt + 1 < attempts:
                    time.sleep(delay)
    elif msvcrt is not None:
        os.lseek(descriptor, 0, os.SEEK_SET)
        for attempt in range(attempts):
            try:
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                if attempt + 1 < attempts:
                    time.sleep(delay)
    else:  # pragma: no cover - a supported platform always has one locking primitive.
        raise JsonlDurabilityError("no cross-process lock primitive is available")
    raise JsonlDurabilityError("durable JSONL transaction lock is contended")


def _unlock_file_descriptor(descriptor: int) -> None:
    if fcntl is not None:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
    elif msvcrt is not None:
        os.lseek(descriptor, 0, os.SEEK_SET)
        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)


@contextmanager
def durable_lock(path: Path):
    """Hold one durable, cross-process transaction lock for a journal operation.

    The lock is a stable sibling of the journal, not the journal itself.  This lets callers
    hold it across read/validate/append while ``append_jsonl`` retains its lower-level file
    lock and crash/torn-tail/index checks.  The lock file is intentionally retained so a
    missing journal has the same serialization identity as a later append.
    """
    path = Path(os.path.abspath(path)) if os.name == "nt" else Path(path)
    parent_pins: list[tuple[Path, int, tuple[int, int, int]]] = []
    descriptor: int | None = None
    locked = False
    try:
        ensure_no_symlink(path)
        ensure_no_symlink(path.parent)
        if os.name == "nt":
            parent_pins = _win_pin_lock_parent(path.parent)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
        ensure_no_symlink(path.parent)
        ensure_no_symlink(path)
        lock_path = path.parent / f".{path.name}.lock"
        # This is deliberately the final pathname precheck.  On Windows every parent
        # component is already pinned without delete sharing, so a rename+junction swap
        # attempted here is rejected by the kernel before the lock leaf can be opened.
        ensure_no_symlink(lock_path)
        descriptor = _open_durable_lock(lock_path)
        if os.name == "nt":
            _win_validate_lock_parent_pins(parent_pins)
        lock_identity = _capture_opened_leaf(lock_path, descriptor)
        # msvcrt.locking needs a byte to lock; this also makes creation durable.
        if os.fstat(descriptor).st_size == 0:
            _revalidate_opened_leaf(lock_path, descriptor, lock_identity)
            _write_all(descriptor, b"\0", leaf_path=lock_path, leaf_identity=lock_identity)
            os.fsync(descriptor)
            if os.name != "nt":
                _fsync_dir(path.parent)
        _lock_file_descriptor(descriptor)
        locked = True
    except JsonlDurabilityError:
        try:
            if descriptor is not None:
                os.close(descriptor)
        finally:
            if parent_pins:
                _win_close_lock_parent_pins(parent_pins)
        raise
    except OSError as exc:
        try:
            if descriptor is not None:
                os.close(descriptor)
        finally:
            if parent_pins:
                _win_close_lock_parent_pins(parent_pins)
        raise JsonlDurabilityError(
            f"cannot establish durable JSONL transaction lock for {path}: {exc}"
        ) from exc
    try:
        yield
    finally:
        try:
            if locked:
                _unlock_file_descriptor(descriptor)
        finally:
            try:
                os.close(descriptor)
            finally:
                if parent_pins:
                    _win_close_lock_parent_pins(parent_pins)


@dataclass(frozen=True)
class AppendOutcome:
    appended: bool
    quarantine: dict | None


@dataclass(frozen=True)
class VerifiedLine:
    sequence: int
    start: int
    end: int
    raw: bytes
    value: dict | None
    chain_sha256: str


@dataclass(frozen=True)
class IndexedBatch:
    """Verified physical lines selected from one exact journal generation."""

    lines: tuple[VerifiedLine, ...]
    verified_size: int
    chain_sha256: str
    rebuilt: bool


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _fsync_dir(path: Path) -> None:
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_all(descriptor: int, value: bytes, *, leaf_path: Path | None = None,
               leaf_identity: tuple[int, ...] | None = None) -> None:
    if (leaf_path is None) != (leaf_identity is None):
        raise JsonlDurabilityError("JSONL write revalidation requires path and identity")
    view = memoryview(value)
    while view:
        if leaf_path is not None and leaf_identity is not None:
            _revalidate_opened_leaf(leaf_path, descriptor, leaf_identity)
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("JSONL write made no progress")
        view = view[written:]


def _read_at(descriptor: int, count: int, offset: int) -> bytes:
    if hasattr(os, "pread"):
        return os.pread(descriptor, count, offset)
    current = os.lseek(descriptor, 0, os.SEEK_CUR)
    try:
        os.lseek(descriptor, offset, os.SEEK_SET)
        return os.read(descriptor, count)
    finally:
        os.lseek(descriptor, current, os.SEEK_SET)


def _lock_descriptor(descriptor: int) -> None:
    """Bound contention between appenders that have distinct higher-level action locks."""
    if fcntl is None:
        return
    try:
        attempts = max(1, int(os.environ.get("RECURSION_JSONL_LOCK_ATTEMPTS", "100")))
    except (TypeError, ValueError, OverflowError):
        attempts = 100
    try:
        delay = max(0.0, float(os.environ.get("RECURSION_JSONL_LOCK_DELAY_S", "0.01")))
        if not math.isfinite(delay):
            raise ValueError("non-finite JSONL lock delay")
    except (TypeError, ValueError, OverflowError):
        delay = 0.01
    for attempt in range(attempts):
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            if attempt + 1 < attempts:
                time.sleep(delay)
    raise JsonlDurabilityError("JSONL journal lock is contended; refusing an unlocked append")


def _atomic_bytes(path: Path, value: bytes, mode: int = 0o600,
                  hook: Callable[[str], None] | None = None) -> None:
    path = Path(path)
    if not isinstance(value, bytes):
        raise JsonlDurabilityError("durable atomic write requires bytes")
    with pinned_durable_parent(path.parent, create=True) as pins:
        parent_fd = pins[-1][1] if os.name != "nt" else None
        if parent_fd is not None:
            validate_durable_leaf_at(parent_fd, path.name, allow_missing=True)
            descriptor, name = _open_unique_at(parent_fd, f".{path.name}.tmp.", mode)
            temporary = _pinned_fd_path(parent_fd, name)
        else:
            ensure_no_symlink(path)
            validate_durable_leaf(path, allow_missing=True)
            descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
            temporary = Path(name)
        try:
            leaf_identity = _capture_opened_leaf(temporary, descriptor)
            if hasattr(os, "fchmod"):  # absent on Windows; NTFS mode bits are meaningless
                os.fchmod(descriptor, mode)
            if hook is not None:
                hook("pre-write")
            # _write_all performs the required same-handle revalidation immediately before
            # each os.write; keeping that check there avoids a duplicate fstat per write.
            _write_all(descriptor, value, leaf_path=temporary, leaf_identity=leaf_identity)
            os.fsync(descriptor)
            # Revalidate while the same private descriptor is still open, immediately
            # before publication.  Windows cannot replace an open CRT leaf reliably, so
            # close only after this check and perform the final by-name check below.
            if hook is not None:
                hook("pre-replace")
            _revalidate_opened_leaf(temporary, descriptor, leaf_identity)
            os.close(descriptor)
            descriptor = -1
            if parent_fd is not None:
                validate_durable_leaf_at(parent_fd, name)
                revalidate_durable_parent_pins(pins)
                validate_durable_leaf_at(parent_fd, path.name, allow_missing=True)
                os.replace(name, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
                os.fsync(parent_fd)
            else:
                validate_durable_leaf(temporary)
                revalidate_durable_parent_pins(pins)
                validate_durable_leaf(path, allow_missing=True)
                os.replace(temporary, path)
                _fsync_dir(path.parent)
        except BaseException:
            # Cleanup must never replace the primary exception: close the descriptor first
            # (Windows cannot unlink an open file) and swallow only the cleanup's own OSError.
            try:
                if descriptor >= 0:
                    os.close(descriptor)
            except OSError:
                pass
            try:
                if parent_fd is not None:
                    os.unlink(name, dir_fd=parent_fd)
                else:
                    temporary.unlink(missing_ok=True)
            except FileNotFoundError:
                pass
            except OSError:
                pass
            raise


def atomic_bytes(path: Path, value: bytes, mode: int = 0o600,
                 hook: Callable[[str], None] | None = None) -> None:
    """Public typed boundary for crash-safe replacement of a durable byte leaf."""
    try:
        _atomic_bytes(Path(path), value, mode, hook)
    except JsonlDurabilityError:
        raise
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError) as exc:
        raise JsonlDurabilityError(f"durable atomic write refused: {path}: {exc}") from exc


def _journal_identity(path: Path) -> tuple[Path, str]:
    resolved = path.resolve(strict=False)
    for parent in (resolved.parent, *resolved.parents):
        if parent.name == "state":
            try:
                relative = resolved.relative_to(parent.parent).as_posix()
            except ValueError:
                break
            return parent / "jsonl-quarantine", relative
    return resolved.parent / "jsonl-quarantine", resolved.name


def _index_identity(path: Path) -> tuple[Path, str]:
    """Return the derived-cache directory and stable journal identity."""
    resolved = path.resolve(strict=False)
    for parent in (resolved.parent, *resolved.parents):
        if parent.name == "state":
            try:
                relative = resolved.relative_to(parent.parent).as_posix()
            except ValueError:
                break
            return parent / "jsonl-index", relative
    return resolved.parent / "jsonl-index", resolved.name


def _ensure_index_root(path: Path, index_root: Path | None = None,
                       index_identity: str | None = None) -> tuple[Path, str]:
    if index_root is None:
        root, identity = _index_identity(path)
    else:
        root = Path(index_root)
        identity = index_identity if index_identity is not None else path.name
    try:
        with pinned_durable_parent(root, create=True) as pins:
            revalidate_durable_parent_pins(pins)
            if os.name != "nt":
                descriptor = pins[-1][1]
                metadata = os.fstat(descriptor)
                if not stat.S_ISDIR(metadata.st_mode):
                    raise JsonlDurabilityError(f"JSONL index root has unsafe type: {root}")
                try:
                    os.fchmod(descriptor, 0o700)
                except OSError:
                    pass
            elif not root.is_dir():
                raise JsonlDurabilityError(f"JSONL index root has unsafe type: {root}")
            revalidate_durable_parent_pins(pins)
    except JsonlDurabilityError:
        raise
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError) as exc:
        raise JsonlDurabilityError(f"cannot establish JSONL index root {root}: {exc}") from exc
    return root, identity


def _index_path(path: Path, index_root: Path | None = None,
                index_identity: str | None = None) -> tuple[Path, str]:
    root, identity = _ensure_index_root(path, index_root, index_identity)
    name = index_cache_name(identity)
    return root / name, identity


def index_cache_name(identity: str) -> str:
    """Return the stable SQLite filename for a journal identity."""
    if not isinstance(identity, str):
        raise JsonlDurabilityError("JSONL index identity must be a string")
    try:
        return hashlib.sha256(identity.encode("utf-8")).hexdigest() + ".sqlite3"
    except (UnicodeEncodeError, TypeError, ValueError) as exc:
        raise JsonlDurabilityError("JSONL index identity is not encodable") from exc


def _last_newline(descriptor: int, size: int) -> int:
    """Return the offset immediately after the last newline, or zero."""
    cursor = size
    while cursor:
        start = max(0, cursor - COPY_CHUNK_BYTES)
        chunk = _read_at(descriptor, cursor - start, start)
        if len(chunk) != cursor - start:
            raise OSError("short JSONL tail read")
        index = chunk.rfind(b"\n")
        if index >= 0:
            return start + index + 1
        cursor = start
    return 0


def _quarantine_tail(path: Path, descriptor: int, offset: int, size: int,
                     hook: Callable[[str], None] | None = None) -> dict:
    quarantine, _ = _journal_identity(path)
    try:
        with pinned_durable_parent(quarantine, create=True) as pins:
            result = _quarantine_tail_unpinned(path, descriptor, offset, size, hook)
            revalidate_durable_parent_pins(pins)
            return result
    except JsonlDurabilityError:
        raise
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError, sqlite3.DatabaseError) as exc:
        raise JsonlDurabilityError(f"JSONL quarantine publication refused: {quarantine}") from exc


def _quarantine_tail_unpinned(path: Path, descriptor: int, offset: int, size: int,
                              hook: Callable[[str], None] | None = None) -> dict:
    quarantine, journal_name = _journal_identity(path)
    quarantine.mkdir(parents=True, exist_ok=True, mode=0o777 if os.name == "nt" else 0o700)
    try:
        os.chmod(quarantine, 0o700)
    except OSError:
        pass
    _fsync_dir(quarantine.parent)

    digest = hashlib.sha256()
    cursor = offset
    payload_fd, payload_name = tempfile.mkstemp(prefix=".jsonl-tail.tmp.", dir=quarantine)
    payload_tmp = Path(payload_name)
    try:
        try:
            _validate_opened_leaf(payload_tmp, payload_fd)
            payload_identity = _capture_opened_leaf(payload_tmp, payload_fd)
            if hasattr(os, "fchmod"):  # absent on Windows; NTFS mode bits are meaningless
                os.fchmod(payload_fd, 0o600)
            source_identity = _capture_opened_leaf(path, descriptor)
            if hook is not None:
                hook("pre-quarantine-payload-write")
            while cursor < size:
                _revalidate_opened_leaf(path, descriptor, source_identity)
                chunk = _read_at(descriptor, min(COPY_CHUNK_BYTES, size - cursor), cursor)
                if not chunk:
                    raise OSError("short JSONL quarantine read")
                digest.update(chunk)
                _write_all(payload_fd, chunk, leaf_path=payload_tmp,
                           leaf_identity=payload_identity)
                cursor += len(chunk)
            os.fsync(payload_fd)
        finally:
            os.close(payload_fd)
    except BaseException:
        payload_tmp.unlink(missing_ok=True)
        raise

    tail_sha = digest.hexdigest()
    safe_name = (re.sub(r"[^A-Za-z0-9._-]+", "_", journal_name).strip("._") or "journal")[:96]
    stem = f"{safe_name}-offset-{offset}-{tail_sha}"
    payload = quarantine / f"{stem}.bin"
    metadata = quarantine / f"{stem}.json"
    publication_fd = -1
    try:
        existing_payload = read_durable_bytes(payload, max_bytes=max(size - offset, 0))
        if existing_payload is not None:
            existing = hashlib.sha256(existing_payload).hexdigest()
            if existing != tail_sha or len(existing_payload) != size - offset:
                raise JsonlDurabilityError(f"JSONL quarantine payload conflicts: {payload}")
            payload_tmp.unlink(missing_ok=True)
        else:
            publication_fd = _open_durable_leaf(payload_tmp, os.O_RDONLY)
            publication_identity = _capture_opened_leaf(payload_tmp, publication_fd)
            if hook is not None:
                hook("pre-quarantine-payload-replace")
            _revalidate_opened_leaf(payload_tmp, publication_fd, publication_identity)
            # The Windows CRT handle used by _open_durable_leaf does not grant delete
            # sharing, so close only after the same-handle publication check and perform
            # the rename as the next operation.
            if os.name == "nt":
                os.close(publication_fd)
                publication_fd = -1
            os.replace(payload_tmp, payload)
            _fsync_dir(quarantine)
            if publication_fd >= 0:
                os.close(publication_fd)
                publication_fd = -1
        evidence = {
            "schema_version": 1,
            "kind": "jsonl-torn-tail",
            "status": "open",
            "escalation_id": "jsonl-tail-" + hashlib.sha256(
                f"{journal_name}\0{offset}\0{tail_sha}".encode()
            ).hexdigest()[:24],
            "journal": journal_name,
            "journal_offset": offset,
            "original_bytes": size,
            "tail_bytes": size - offset,
            "tail_sha256": tail_sha,
            "payload": payload.name,
            "quarantined_at": _now_iso(),
            "requires_human_review": True,
        }
        encoded = (json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n").encode()
        prior_bytes = read_durable_bytes(metadata)
        if prior_bytes is not None:
            try:
                prior = json.loads(prior_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError, TypeError,
                    ValueError, OverflowError, RecursionError) as exc:
                raise JsonlDurabilityError(
                    f"JSONL quarantine metadata is not valid JSON: {metadata}"
                ) from exc
            if not isinstance(prior, dict):
                raise JsonlDurabilityError(f"JSONL quarantine metadata is not an object: {metadata}")
            immutable = ("kind", "journal", "journal_offset", "original_bytes", "tail_bytes",
                         "tail_sha256", "payload")
            if any(prior.get(key) != evidence.get(key) for key in immutable):
                raise JsonlDurabilityError(f"JSONL quarantine metadata conflicts: {metadata}")
            evidence = prior
        else:
            _atomic_bytes(metadata, encoded, hook=hook)
        return evidence
    except BaseException:
        if publication_fd >= 0:
            try:
                os.close(publication_fd)
            except OSError:
                pass
        payload_tmp.unlink(missing_ok=True)
        raise


def _iter_complete_lines(descriptor: int, limit: int, path: Path,
                         max_record_bytes: int) -> Iterator[VerifiedLine]:
    """Stream and validate physical lines up to *limit* with bounded memory."""
    leaf_identity = _capture_opened_leaf(path, descriptor)
    with os.fdopen(os.dup(descriptor), "rb", closefd=True) as source:
        source.seek(0)
        remaining = limit
        line_number = 0
        offset = 0
        chain = ZERO_CHAIN_SHA256
        while remaining:
            _revalidate_opened_leaf(path, descriptor, leaf_identity)
            line = source.readline(min(remaining, max_record_bytes + 2))
            if not line:
                raise JsonlDurabilityError(f"short JSONL read before offset {limit}: {path}")
            line_number += 1
            remaining -= len(line)
            if len(line) > max_record_bytes + 1:
                raise JsonlDurabilityError(
                    f"JSONL record {line_number} exceeds {max_record_bytes} bytes: {path}"
                )
            if not line.endswith(b"\n"):
                raise JsonlDurabilityError(f"JSONL record {line_number} is not terminated: {path}")
            start = offset
            offset += len(line)
            raw = line[:-1]
            if raw.endswith(b"\r"):
                raw = raw[:-1]
            value: dict | None = None
            if not raw.strip():
                pass
            else:
                try:
                    value = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError,
                        OverflowError, RecursionError) as exc:
                    raise JsonlDurabilityError(
                        f"malformed complete JSONL record {line_number}: {path}: {exc}"
                    ) from exc
                if not isinstance(value, dict):
                    raise JsonlDurabilityError(
                        f"JSON object required at JSONL record {line_number}: {path}"
                    )
            raw_sha256 = hashlib.sha256(line).digest()
            chain = hashlib.sha256(bytes.fromhex(chain) + raw_sha256).hexdigest()
            yield VerifiedLine(
                sequence=line_number, start=start, end=offset, raw=line, value=value,
                chain_sha256=chain
            )
        if remaining != 0:
            raise JsonlDurabilityError(f"short JSONL validation read: {path}")


def _iter_complete_objects(descriptor: int, limit: int, path: Path,
                           max_record_bytes: int) -> Iterator[dict]:
    for line in _iter_complete_lines(descriptor, limit, path, max_record_bytes):
        if line.value is not None:
            yield line.value


def _create_index_schema(connection: sqlite3.Connection) -> None:
    statements = (
        "PRAGMA journal_mode=DELETE",
        "PRAGMA synchronous=FULL",
        "PRAGMA foreign_keys=ON",
        """CREATE TABLE metadata (
            singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
            schema_version INTEGER NOT NULL,
            authority TEXT NOT NULL,
            journal_identity TEXT NOT NULL,
            max_record_bytes INTEGER NOT NULL,
            device TEXT NOT NULL,
            inode TEXT NOT NULL,
            size INTEGER NOT NULL,
            mtime_ns INTEGER NOT NULL,
            ctime_ns INTEGER NOT NULL,
            line_count INTEGER NOT NULL,
            chain_sha256 TEXT NOT NULL
        )""",
        """CREATE TABLE records (
            sequence INTEGER PRIMARY KEY,
            start_offset INTEGER NOT NULL UNIQUE,
            end_offset INTEGER NOT NULL UNIQUE,
            raw BLOB NOT NULL,
            raw_sha256 TEXT NOT NULL,
            chain_sha256 TEXT NOT NULL,
            value_json TEXT,
            object_id_json TEXT
        )""",
        "CREATE INDEX records_object_id ON records(object_id_json)",
        """CREATE TABLE consumers (
            name TEXT PRIMARY KEY,
            end_offset INTEGER NOT NULL,
            chain_sha256 TEXT NOT NULL
        )""",
        f"PRAGMA user_version={INDEX_SCHEMA_VERSION}",
    )
    for statement in statements:
        _maybe_revalidate_index_connection(connection)
        connection.execute(statement)


def _stat_fields(stat: os.stat_result) -> tuple[str, str, int, int, int]:
    return (
        str(stat.st_dev), str(stat.st_ino), int(stat.st_size),
        int(stat.st_mtime_ns), int(stat.st_ctime_ns),
    )


def _metadata(connection: sqlite3.Connection) -> tuple | None:
    _maybe_revalidate_index_connection(connection)
    return connection.execute(
        "SELECT schema_version,authority,journal_identity,max_record_bytes,device,inode,size,"
        "mtime_ns,ctime_ns,line_count,chain_sha256 FROM metadata WHERE singleton=1"
    ).fetchone()


def _index_integer(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise JsonlDurabilityError(f"JSONL verification index {label} is not an integer")
    return value


def _validate_indexed_batch(batch: IndexedBatch) -> None:
    if not isinstance(batch, IndexedBatch):
        raise JsonlDurabilityError("invalid JSONL acknowledgement batch")
    _index_integer(batch.verified_size, "acknowledgement size")
    if batch.verified_size < 0:
        raise JsonlDurabilityError("JSONL acknowledgement size cannot be negative")
    if not isinstance(batch.chain_sha256, str) \
            or not re.fullmatch(r"[0-9a-f]{64}", batch.chain_sha256):
        raise JsonlDurabilityError("invalid JSONL acknowledgement chain")


def _index_matches(connection: sqlite3.Connection, identity: str, stat: os.stat_result,
                   max_record_bytes: int) -> bool:
    _maybe_revalidate_index_connection(connection)
    if connection.execute("PRAGMA user_version").fetchone()[0] != INDEX_SCHEMA_VERSION:
        return False
    row = _metadata(connection)
    if row is None:
        return False
    expected = (
        INDEX_SCHEMA_VERSION, INDEX_AUTHORITY, identity, max_record_bytes, *_stat_fields(stat)
    )
    if row[:9] != expected:
        return False
    line_count = _index_integer(row[9], "line count")
    chain = str(row[10])
    file_size = _index_integer(stat.st_size, "journal size")
    summary = connection.execute(
        "SELECT COUNT(*),COALESCE(MIN(start_offset),0),COALESCE(MAX(end_offset),0),"
        "COALESCE(MAX(sequence),0) FROM records"
    ).fetchone()
    if summary != (line_count, 0, file_size, line_count):
        return False
    if line_count:
        last = connection.execute(
            "SELECT chain_sha256 FROM records WHERE sequence=?", (line_count,)
        ).fetchone()
        if last is None or last[0] != chain:
            return False
    elif chain != ZERO_CHAIN_SHA256 or stat.st_size != 0:
        return False
    return True


def _insert_line(connection: sqlite3.Connection, sequence: int, line: VerifiedLine) -> None:
    value_json = None
    object_id_json = None
    if line.value is not None:
        value_json = json.dumps(line.value, sort_keys=True, separators=(",", ":"))
        if "id" in line.value:
            object_id_json = json.dumps(
                line.value.get("id"), sort_keys=True, separators=(",", ":")
            )
    _maybe_revalidate_index_connection(connection)
    connection.execute(
        "INSERT INTO records(sequence,start_offset,end_offset,raw,raw_sha256,chain_sha256,"
        "value_json,object_id_json) VALUES(?,?,?,?,?,?,?,?)",
        (
            sequence, line.start, line.end, sqlite3.Binary(line.raw),
            hashlib.sha256(line.raw).hexdigest(), line.chain_sha256,
            value_json, object_id_json,
        ),
    )


def _write_metadata(connection: sqlite3.Connection, identity: str, stat: os.stat_result,
                    max_record_bytes: int, line_count: int, chain_sha256: str) -> None:
    _maybe_revalidate_index_connection(connection)
    connection.execute("DELETE FROM metadata")
    _maybe_revalidate_index_connection(connection)
    connection.execute(
        "INSERT INTO metadata VALUES(1,?,?,?,?,?,?,?,?,?,?,?)",
        (
            INDEX_SCHEMA_VERSION, INDEX_AUTHORITY, identity, max_record_bytes,
            *_stat_fields(stat), line_count, chain_sha256,
        ),
    )


def _rebuild_index_unpinned(index_path: Path, identity: str, descriptor: int,
                             stat: os.stat_result, journal: Path, max_record_bytes: int,
                             hook: Callable[[str], None] | None = None) -> None:
    """Build a cache in memory, then publish one serialized durable replacement."""
    connection: sqlite3.Connection | None = None
    try:
        if hook is not None:
            hook("pre-sqlite-open")
        connection = sqlite3.connect(":memory:", factory=_PinnedIndexConnection)
        connection._durable_index_path = index_path
        _create_index_schema(connection)
        _maybe_revalidate_index_connection(connection)
        connection.execute("BEGIN IMMEDIATE")
        line_count = 0
        chain = ZERO_CHAIN_SHA256
        for line_count, line in enumerate(
                _iter_complete_lines(descriptor, stat.st_size, journal, max_record_bytes), 1):
            _insert_line(connection, line_count, line)
            chain = line.chain_sha256
        _write_metadata(
            connection, identity, stat, max_record_bytes, line_count, chain
        )
        _maybe_revalidate_index_connection(connection)
        connection.commit()
        if not hasattr(connection, "serialize"):
            raise JsonlDurabilityError("SQLite serialization is unavailable for cache rebuild")
        _install_serialized_cache_path(index_path, connection.serialize(), hook)
    except BaseException:
        if connection is not None:
            connection.close()
        raise
    finally:
        if connection is not None:
            connection.close()


def _rebuild_index(index_path: Path, identity: str, descriptor: int,
                   stat: os.stat_result, journal: Path, max_record_bytes: int,
                   hook: Callable[[str], None] | None = None) -> None:
    with pinned_durable_parent(index_path.parent) as pins:
        validate_durable_leaf(index_path, allow_missing=True)
        _rebuild_index_unpinned(
            index_path, identity, descriptor, stat, journal, max_record_bytes, hook
        )
        revalidate_durable_parent_pins(pins)


def _open_verified_index(path: Path, descriptor: int, size: int,
                         max_record_bytes: int, *,
                         index_root: Path | None = None,
                         index_identity: str | None = None,
                         rebuild_in_place: bool = False,
                         hook: Callable[[str], None] | None = None) -> tuple[sqlite3.Connection, bool]:
    stat = os.fstat(descriptor)
    if stat.st_size != size:
        raise JsonlDurabilityError(f"JSONL size changed while opening verification index: {path}")
    index_path, identity = _index_path(path, index_root, index_identity)
    validate_durable_leaf(index_path, allow_missing=True)
    if rebuild_in_place:
        # The caller pins the cache directory and (on Windows) the cache leaf before
        # entering this function.  A missing leaf is created by that caller, so this
        # branch never has to make a pathname-based create decision on its own.
        connection: sqlite3.Connection | None = None
        try:
            if hook is not None:
                hook("pre-sqlite-open")
            validate_durable_leaf(index_path)
            connection = _connect_verified_index(index_path)
            connection.execute("PRAGMA query_only=ON")
            if _index_matches(connection, identity, stat, max_record_bytes):
                connection.execute("PRAGMA query_only=OFF")
                return connection, False
        except (FileNotFoundError, JsonlDurabilityError, sqlite3.DatabaseError):
            if connection is not None:
                connection.close()
            connection = None
        else:
            connection.close()
            connection = None
        _rebuild_index_in_place(
            index_path, identity, descriptor, stat, path, max_record_bytes, hook
        )
        if hook is not None:
            hook("pre-sqlite-open")
        validate_durable_leaf(index_path)
        connection = _connect_verified_index(index_path)
        if not _index_matches(connection, identity, stat, max_record_bytes):
            connection.close()
            raise JsonlDurabilityError(f"rebuilt JSONL verification index is inconsistent: {path}")
        return connection, True
    connection: sqlite3.Connection | None = None
    try:
        if hook is not None:
            hook("pre-sqlite-open")
        connection = _connect_verified_index(index_path)
        connection.execute("PRAGMA query_only=ON")
        if _index_matches(connection, identity, stat, max_record_bytes):
            connection.execute("PRAGMA query_only=OFF")
            retained = connection
            connection = None
            return retained, False
    except (FileNotFoundError, JsonlDurabilityError, sqlite3.DatabaseError):
        pass
    finally:
        if connection is not None:
            connection.close()
    _rebuild_index(index_path, identity, descriptor, stat, path, max_record_bytes, hook)
    if hook is not None:
        hook("pre-sqlite-open")
    connection = _connect_verified_index(index_path)
    if not _index_matches(connection, identity, stat, max_record_bytes):
        connection.close()
        raise JsonlDurabilityError(f"rebuilt JSONL verification index is inconsistent: {path}")
    return connection, True


def _rows_to_lines(rows: Iterator[tuple]) -> tuple[VerifiedLine, ...]:
    result: list[VerifiedLine] = []
    for sequence, start, end, raw, value_json, chain in rows:
        if value_json is not None:
            try:
                value = json.loads(value_json)
            except (TypeError, ValueError, OverflowError, RecursionError) as exc:
                raise JsonlDurabilityError("JSONL verification index contains invalid JSON") from exc
        else:
            value = None
        if value is not None and not isinstance(value, dict):
            raise JsonlDurabilityError("JSONL verification index contains a non-object value")
        try:
            result.append(VerifiedLine(
                sequence=int(sequence), start=int(start), end=int(end), raw=bytes(raw), value=value,
                chain_sha256=str(chain),
            ))
        except (TypeError, ValueError, OverflowError) as exc:
            raise JsonlDurabilityError("JSONL verification index contains invalid row types") from exc
    return tuple(result)


def _verified_descriptor(path: Path, max_record_bytes: int) \
        -> tuple[int, sqlite3.Connection, bool]:
    path = _durable_path(path)
    if not isinstance(max_record_bytes, int) or isinstance(max_record_bytes, bool) \
            or max_record_bytes < 0:
        raise JsonlDurabilityError("JSONL max_record_bytes must be a non-negative integer")
    pins = (_win_pin_durable_parent(path.parent, create=False)
            if os.name == "nt" else _posix_pin_durable_parent(path.parent, create=False))
    journal_pins = pins
    try:
        revalidate_durable_parent_pins(journal_pins)
        descriptor = _open_durable_leaf(
            path, os.O_RDONLY | getattr(os, "O_BINARY", 0),
            directory_fd=journal_pins[-1][1] if os.name != "nt" else None,
        )
        revalidate_durable_parent_pins(journal_pins)
    except BaseException:
        if journal_pins:
            _close_durable_parent_pins(journal_pins)
        raise
    try:
        _lock_descriptor(descriptor)
        size = os.fstat(descriptor).st_size
        if size and _read_at(descriptor, 1, size - 1) != b"\n":
            raise JsonlDurabilityError(f"unterminated JSONL tail: {path}")
        connection, rebuilt = _open_verified_index(path, descriptor, size, max_record_bytes)
        connection._durable_journal_parent_pins = journal_pins
        journal_pins = []
        return descriptor, connection, rebuilt
    except BaseException:
        os.close(descriptor)
        if journal_pins:
            _close_durable_parent_pins(journal_pins)
        raise


def read_jsonl_objects(path: Path, max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> list[dict]:
    """Read objects from an intact journal through its verified derived index."""
    path = _durable_path(path)
    try:
        descriptor, connection, _rebuilt = _verified_descriptor(path, max_record_bytes)
    except FileNotFoundError:
        return []
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError, sqlite3.DatabaseError) as exc:
        raise JsonlDurabilityError(f"JSONL verification read refused: {path}: {exc}") from exc
    try:
        _maybe_revalidate_index_connection(connection)
        rows = connection.execute(
            "SELECT value_json FROM records WHERE value_json IS NOT NULL ORDER BY sequence"
        )
        result = []
        for row in rows:
            try:
                value = json.loads(row[0])
            except (TypeError, ValueError, OverflowError, RecursionError) as exc:
                raise JsonlDurabilityError(f"JSONL verification index contains invalid JSON: {path}") from exc
            if not isinstance(value, dict):
                raise JsonlDurabilityError(f"JSONL verification index contains a non-object value: {path}")
            result.append(value)
        return result
    except sqlite3.DatabaseError as exc:
        raise JsonlDurabilityError(f"JSONL verification index read failed: {path}: {exc}") from exc
    finally:
        connection.close()
        os.close(descriptor)


def read_jsonl_prefix(path: Path, count: int,
                      max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> tuple[VerifiedLine, ...]:
    """Return at most *count* verified physical lines from the journal prefix."""
    path = _durable_path(path)
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise JsonlDurabilityError("JSONL prefix count cannot be negative")
    if count == 0:
        return ()
    try:
        descriptor, connection, _rebuilt = _verified_descriptor(path, max_record_bytes)
    except FileNotFoundError:
        return ()
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError, sqlite3.DatabaseError) as exc:
        raise JsonlDurabilityError(f"JSONL verification read refused: {path}: {exc}") from exc
    try:
        _maybe_revalidate_index_connection(connection)
        rows = connection.execute(
            "SELECT sequence,start_offset,end_offset,raw,value_json,chain_sha256 FROM records "
            "ORDER BY sequence LIMIT ?", (count,),
        )
        return _rows_to_lines(rows)
    except sqlite3.DatabaseError as exc:
        raise JsonlDurabilityError(f"JSONL verification index read failed: {path}: {exc}") from exc
    finally:
        connection.close()
        os.close(descriptor)


def find_jsonl_objects(path: Path, field: str, value: object,
                       max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> list[dict]:
    """Find exact top-level field matches without rescanning verified journal bytes."""
    path = _durable_path(path)
    if not isinstance(field, str) or not field:
        raise JsonlDurabilityError("JSONL search field must be a nonempty string")
    try:
        descriptor, connection, _rebuilt = _verified_descriptor(path, max_record_bytes)
    except FileNotFoundError:
        return []
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError, sqlite3.DatabaseError) as exc:
        raise JsonlDurabilityError(f"JSONL verification read refused: {path}: {exc}") from exc
    try:
        _maybe_revalidate_index_connection(connection)
        if field == "id":
            try:
                encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
            except (TypeError, ValueError, OverflowError, RecursionError) as exc:
                raise JsonlDurabilityError("JSONL search value is not serializable") from exc
            rows = connection.execute(
                "SELECT value_json FROM records WHERE object_id_json=? ORDER BY sequence",
                (encoded,),
            )
            result = []
            for row in rows:
                try:
                    result.append(json.loads(row[0]))
                except (TypeError, ValueError, OverflowError, RecursionError) as exc:
                    raise JsonlDurabilityError(f"JSONL verification index contains invalid JSON: {path}") from exc
            return result
        result = []
        for row in connection.execute(
                "SELECT value_json FROM records WHERE value_json IS NOT NULL ORDER BY sequence"):
            try:
                candidate = json.loads(row[0])
            except (TypeError, ValueError, OverflowError, RecursionError) as exc:
                raise JsonlDurabilityError(f"JSONL verification index contains invalid JSON: {path}") from exc
            if not isinstance(candidate, dict):
                raise JsonlDurabilityError(f"JSONL verification index contains a non-object value: {path}")
            if candidate.get(field) == value:
                result.append(candidate)
        return result
    except sqlite3.DatabaseError as exc:
        raise JsonlDurabilityError(f"JSONL verification index read failed: {path}: {exc}") from exc
    finally:
        connection.close()
        os.close(descriptor)


def _chain_at(connection: sqlite3.Connection, offset: int) -> str | None:
    if offset == 0:
        return ZERO_CHAIN_SHA256
    _maybe_revalidate_index_connection(connection)
    row = connection.execute(
        "SELECT chain_sha256 FROM records WHERE end_offset=?", (offset,)
    ).fetchone()
    return None if row is None else str(row[0])


def read_jsonl_since(path: Path, consumer: str,
                     max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> IndexedBatch:
    """Return only lines not durably acknowledged by *consumer*.

    Consumer cursors live inside the derived index.  Rebuilding the index intentionally drops
    them, causing a safe full replay from the authoritative journal.
    """
    if not isinstance(consumer, str) or not consumer or len(consumer) > 128:
        raise JsonlDurabilityError("invalid JSONL index consumer")
    path = _durable_path(path)
    try:
        descriptor, connection, rebuilt = _verified_descriptor(path, max_record_bytes)
    except FileNotFoundError:
        return IndexedBatch((), 0, ZERO_CHAIN_SHA256, False)
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError, sqlite3.DatabaseError) as exc:
        raise JsonlDurabilityError(f"JSONL verification read refused: {path}: {exc}") from exc
    try:
        _maybe_revalidate_index_connection(connection)
        checkpoint = connection.execute(
            "SELECT end_offset,chain_sha256 FROM consumers WHERE name=?", (consumer,)
        ).fetchone()
        if checkpoint is None:
            offset = 0
            expected_chain = ZERO_CHAIN_SHA256
        else:
            offset = _index_integer(checkpoint[0], "consumer checkpoint offset")
            expected_chain = str(checkpoint[1])
        if _chain_at(connection, offset) != expected_chain:
            raise JsonlDurabilityError(f"JSONL consumer checkpoint is inconsistent: {consumer}")
        rows = connection.execute(
            "SELECT sequence,start_offset,end_offset,raw,value_json,chain_sha256 FROM records "
            "WHERE end_offset>? ORDER BY sequence", (offset,),
        )
        lines = _rows_to_lines(rows)
        metadata = _metadata(connection)
        if metadata is None:
            raise JsonlDurabilityError(f"JSONL verification metadata is absent: {path}")
        verified_size = _index_integer(metadata[6], "journal size")
        return IndexedBatch(lines, verified_size, str(metadata[10]), rebuilt)
    except sqlite3.DatabaseError as exc:
        raise JsonlDurabilityError(f"JSONL verification index read failed: {path}: {exc}") from exc
    finally:
        connection.close()
        os.close(descriptor)


def acknowledge_jsonl(path: Path, consumer: str, batch: IndexedBatch,
                      max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> None:
    """Durably advance a consumer after its selected projections are durable."""
    if not isinstance(consumer, str) or not consumer or len(consumer) > 128:
        raise JsonlDurabilityError("invalid JSONL index consumer")
    _validate_indexed_batch(batch)
    path = _durable_path(path)
    try:
        descriptor, connection, _rebuilt = _verified_descriptor(path, max_record_bytes)
    except FileNotFoundError:
        if batch.verified_size == 0:
            return
        raise JsonlDurabilityError(f"JSONL disappeared before acknowledgement: {path}") from None
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError, sqlite3.DatabaseError) as exc:
        raise JsonlDurabilityError(f"JSONL verification read refused: {path}: {exc}") from exc
    try:
        if _chain_at(connection, batch.verified_size) != batch.chain_sha256:
            raise JsonlDurabilityError(
                f"JSONL changed before consumer acknowledgement: {consumer}"
            )
        current = connection.execute(
            "SELECT end_offset,chain_sha256 FROM consumers WHERE name=?", (consumer,)
        ).fetchone()
        current_offset = None if current is None else _index_integer(
            current[0], "consumer checkpoint offset"
        )
        if current_offset is not None and current_offset > batch.verified_size:
            return
        if current_offset is not None and current_offset == batch.verified_size \
                and str(current[1]) != batch.chain_sha256:
            raise JsonlDurabilityError(f"JSONL consumer checkpoint collision: {consumer}")
        _maybe_revalidate_index_connection(connection)
        connection.execute("BEGIN IMMEDIATE")
        _maybe_revalidate_index_connection(connection)
        connection.execute(
            "INSERT INTO consumers(name,end_offset,chain_sha256) VALUES(?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET end_offset=excluded.end_offset,"
            "chain_sha256=excluded.chain_sha256",
            (consumer, batch.verified_size, batch.chain_sha256),
        )
        _maybe_revalidate_index_connection(connection)
        # This verification connection is memory-backed; commit alone would discard the
        # consumer checkpoint when it closes, so publish the committed image durably.
        connection.commit()
        index_path = getattr(connection, "_durable_index_path", None)
        if not isinstance(index_path, Path):
            raise JsonlDurabilityError(
                "JSONL acknowledgement index has no durable publication path"
            )
        if not hasattr(connection, "serialize"):
            raise JsonlDurabilityError("SQLite serialization is unavailable for acknowledgement")
        _install_serialized_cache_path(index_path, connection.serialize())
    except sqlite3.DatabaseError as exc:
        connection.rollback()
        raise JsonlDurabilityError(f"cannot acknowledge JSONL consumer {consumer}: {exc}") from exc
    finally:
        connection.close()
        os.close(descriptor)


def _duplicate_in_index(connection: sqlite3.Connection, field: str | None,
                        value: object) -> bool:
    if field is None:
        return False
    _maybe_revalidate_index_connection(connection)
    if field == "id":
        try:
            encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise JsonlDurabilityError("JSONL dedupe value is not serializable") from exc
        return connection.execute(
            "SELECT 1 FROM records WHERE object_id_json=? LIMIT 1", (encoded,)
        ).fetchone() is not None
    for row in connection.execute(
            "SELECT value_json FROM records WHERE value_json IS NOT NULL ORDER BY sequence"):
        try:
            candidate = json.loads(row[0])
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise JsonlDurabilityError("JSONL verification index contains invalid JSON") from exc
        if not isinstance(candidate, dict):
            raise JsonlDurabilityError("JSONL verification index contains a non-object value")
        if candidate.get(field) == value:
            return True
    return False


def _update_index_after_append(connection: sqlite3.Connection, descriptor: int, path: Path,
                               encoded: bytes, max_record_bytes: int) -> None:
    metadata = _metadata(connection)
    if metadata is None:
        raise JsonlDurabilityError(f"JSONL verification metadata is absent: {path}")
    old_size = _index_integer(metadata[6], "journal size")
    line_count = _index_integer(metadata[9], "journal line count")
    prior_chain = str(metadata[10])
    stat = os.fstat(descriptor)
    if stat.st_size != old_size + len(encoded):
        raise JsonlDurabilityError(f"JSONL size changed during indexed append: {path}")
    try:
        value = json.loads(encoded[:-1].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError,
            OverflowError, RecursionError) as exc:  # defensive; caller encoded it.
        raise JsonlDurabilityError(f"new JSONL record cannot be indexed: {path}") from exc
    raw_digest = hashlib.sha256(encoded).digest()
    try:
        chain = hashlib.sha256(bytes.fromhex(prior_chain) + raw_digest).hexdigest()
    except (TypeError, ValueError) as exc:
        raise JsonlDurabilityError(f"JSONL verification metadata has an invalid chain: {path}") from exc
    line = VerifiedLine(line_count + 1, old_size, stat.st_size, encoded, value, chain)
    try:
        _maybe_revalidate_index_connection(connection)
        connection.execute("BEGIN IMMEDIATE")
        _insert_line(connection, line_count + 1, line)
        _write_metadata(
            connection, str(metadata[2]), stat, max_record_bytes, line_count + 1, chain
        )
        _maybe_revalidate_index_connection(connection)
        connection.commit()
    except sqlite3.DatabaseError as exc:
        connection.rollback()
        raise JsonlDurabilityError(f"cannot advance JSONL verification index: {path}: {exc}") from exc


def _rebuild_index_in_place_unpinned(
        index_path: Path, identity: str, descriptor: int, stat: os.stat_result,
        journal: Path, max_record_bytes: int,
        hook: Callable[[str], None] | None = None) -> None:
    """Rebuild a cache without replacing its leaf name.

    The historical name is retained for callers that already pin the cache directory.  The
    cache itself is rebuilt in memory and published through the same serialized durable
    replacement as the pathname API; SQLite never mutates a pathname-opened cache leaf.
    """
    connection: sqlite3.Connection | None = None
    try:
        if hook is not None:
            hook("pre-replace")
        validate_durable_leaf(index_path, allow_missing=True)
        connection = sqlite3.connect(":memory:", factory=_PinnedIndexConnection)
        connection._durable_index_path = index_path
        if hook is not None:
            hook("pre-sqlite-write")
        _revalidate_index_connection(connection)
        _create_index_schema(connection)
        _revalidate_index_connection(connection)
        connection.execute("BEGIN IMMEDIATE")
        line_count = 0
        chain = ZERO_CHAIN_SHA256
        for line_count, line in enumerate(
                _iter_complete_lines(descriptor, stat.st_size, journal, max_record_bytes), 1):
            _insert_line(connection, line_count, line)
            chain = line.chain_sha256
        _write_metadata(connection, identity, stat, max_record_bytes, line_count, chain)
        _maybe_revalidate_index_connection(connection)
        connection.commit()
        if not hasattr(connection, "serialize"):
            raise JsonlDurabilityError("SQLite serialization is unavailable for cache rebuild")
        _install_serialized_cache_path(index_path, connection.serialize(), hook)
    except BaseException:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if connection is not None:
            connection.close()


def _rebuild_index_in_place(index_path: Path, identity: str, descriptor: int,
                            stat: os.stat_result, journal: Path, max_record_bytes: int,
                            hook: Callable[[str], None] | None = None) -> None:
    with pinned_durable_parent(index_path.parent) as pins:
        # The retained-name branch also serves the first cache build, where no leaf
        # exists yet; the serialized replacement writer performs the safe create.
        validate_durable_leaf(index_path, allow_missing=True)
        _rebuild_index_in_place_unpinned(
            index_path, identity, descriptor, stat, journal, max_record_bytes, hook
        )
        revalidate_durable_parent_pins(pins)


def _append_jsonl_unpinned(path: Path, value: dict,
                           max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES,
                           dedupe_field: str | None = None, dedupe_value: object = None, *,
                           index_root: Path | None = None, index_identity: str | None = None,
                           rebuild_in_place: bool = False,
                           hook: Callable[[str], None] | None = None,
                           parent_directory: int | None = None) -> AppendOutcome:
    """Repair a torn tail, validate committed rows, and durably append one object.

    The exact torn bytes and fail-closed escalation metadata are stored in the canonical
    ``state/jsonl-quarantine`` directory before truncation.  Complete malformed rows are
    never truncated or skipped.
    """
    if not isinstance(value, dict):
        raise JsonlDurabilityError("JSONL append requires an object")
    if not isinstance(max_record_bytes, int) or isinstance(max_record_bytes, bool) \
            or max_record_bytes < 0:
        raise JsonlDurabilityError("JSONL max_record_bytes must be a non-negative integer")
    try:
        encoded = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeDecodeError) as exc:
        raise JsonlDurabilityError(f"JSONL append value is not serializable: {path}") from exc
    if len(encoded) - 1 > max_record_bytes:
        raise JsonlDurabilityError(f"new JSONL record exceeds {max_record_bytes} bytes: {path}")
    if parent_directory is None:
        ensure_no_symlink(path.parent)
        path.parent.mkdir(parents=True, exist_ok=True)
        ensure_no_symlink(path.parent)
        ensure_no_symlink(path)
    journal_path = (_pinned_fd_path(parent_directory, path.name)
                    if parent_directory is not None else path)
    descriptor = _open_durable_leaf(
        path, os.O_RDWR | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0), 0o600,
        directory_fd=parent_directory,
    )
    try:
        leaf_identity = _capture_opened_leaf(journal_path, descriptor)
    except BaseException:
        os.close(descriptor)
        raise
    evidence: dict | None = None
    connection: sqlite3.Connection | None = None
    try:
        _lock_descriptor(descriptor)
        _revalidate_opened_leaf(journal_path, descriptor, leaf_identity)
        size = os.fstat(descriptor).st_size
        committed = size
        if size:
            _revalidate_opened_leaf(journal_path, descriptor, leaf_identity)
        if size and _read_at(descriptor, 1, size - 1) != b"\n":
            committed = _last_newline(descriptor, size)
            evidence = _quarantine_tail(path, descriptor, committed, size, hook)
            _revalidate_opened_leaf(journal_path, descriptor, leaf_identity)
            os.ftruncate(descriptor, committed)
            os.fsync(descriptor)
        # Resolve the derived-cache destination before any caller hook can rename the
        # journal parent.  The later publication still re-pins this saved path, so a
        # swapped ancestor is refused rather than followed.
        index_path, _ = _index_path(path, index_root, index_identity)
        connection, _rebuilt = _open_verified_index(
            path, descriptor, committed, max_record_bytes,
            index_root=index_root, index_identity=index_identity,
            rebuild_in_place=rebuild_in_place, hook=hook,
        )
        if _duplicate_in_index(connection, dedupe_field, dedupe_value):
            return AppendOutcome(appended=False, quarantine=evidence)
        if hook is not None:
            hook("pre-journal-write")
        _write_all(descriptor, encoded, leaf_path=journal_path, leaf_identity=leaf_identity)
        os.fsync(descriptor)
        if parent_directory is not None:
            os.fsync(parent_directory)
        else:
            _fsync_dir(path.parent)
        _update_index_after_append(connection, descriptor, journal_path, encoded, max_record_bytes)
        if not hasattr(connection, "serialize"):
            raise JsonlDurabilityError("SQLite serialization is unavailable for cache update")
        _install_serialized_cache_path(index_path, connection.serialize(), hook)
    finally:
        if connection is not None:
            connection.close()
        os.close(descriptor)
    return AppendOutcome(appended=True, quarantine=evidence)


def append_jsonl(path: Path, value: dict,
                 max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES,
                 dedupe_field: str | None = None, dedupe_value: object = None, *,
                 index_root: Path | None = None, index_identity: str | None = None,
                 rebuild_in_place: bool = False,
                 hook: Callable[[str], None] | None = None) -> AppendOutcome:
    try:
        path = Path(path)
        with pinned_durable_parent(path.parent, create=True) as pins:
            revalidate_durable_parent_pins(pins)
            result = _append_jsonl_unpinned(
                path, value, max_record_bytes, dedupe_field, dedupe_value,
                index_root=index_root, index_identity=index_identity,
                rebuild_in_place=rebuild_in_place, hook=hook,
                parent_directory=pins[-1][1] if os.name != "nt" else None,
            )
            revalidate_durable_parent_pins(pins)
            return result
    except JsonlDurabilityError:
        raise
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError, sqlite3.DatabaseError) as exc:
        raise JsonlDurabilityError(f"JSONL append refused for {path}: {exc}") from exc


def _pinned_fd_path(descriptor: int, name: str) -> Path:
    """Address a child through an already-open directory on POSIX."""
    if os.name == "nt" or not Path("/proc/self/fd").is_dir():
        raise JsonlDurabilityError("pinned JSONL persistence requires /proc/self/fd on POSIX")
    if not name or Path(name).name != name or name in {".", ".."}:
        raise JsonlDurabilityError("pinned JSONL child name is not a single path component")
    return Path("/proc/self/fd") / str(descriptor) / name


def _open_unique_at(directory: int, prefix: str, mode: int = 0o600) -> tuple[int, str]:
    """Create a private file with openat semantics and return its fd/name."""
    for _ in range(128):
        name = f"{prefix}{os.getpid()}-{time.time_ns():x}-{os.urandom(8).hex()}"
        try:
            descriptor = os.open(
                name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                mode,
                dir_fd=directory,
            )
            return descriptor, name
        except FileExistsError:
            continue
    raise JsonlDurabilityError("could not allocate a private pinned JSONL temporary")


def _install_serialized_cache(cache_directory: int, cache_name: str, cache_bytes: bytes,
                              hook: Callable[[str], None] | None = None) -> None:
    temporary_fd, temporary_name = _open_unique_at(cache_directory, ".jsonl-cache.tmp.")
    temporary = _pinned_fd_path(cache_directory, temporary_name)
    try:
        temporary_identity = _capture_opened_leaf(temporary, temporary_fd)
        if hook is not None:
            hook("pre-write")
        _revalidate_opened_leaf(temporary, temporary_fd, temporary_identity)
        _write_all(temporary_fd, cache_bytes, leaf_path=temporary,
                   leaf_identity=temporary_identity)
        os.fsync(temporary_fd)
        if hook is not None:
            hook("pre-replace")
        _revalidate_opened_leaf(temporary, temporary_fd, temporary_identity)
        validate_durable_leaf_at(cache_directory, cache_name, allow_missing=True)
        os.replace(temporary_name, cache_name,
                   src_dir_fd=cache_directory, dst_dir_fd=cache_directory)
        os.fsync(cache_directory)
    except BaseException:
        try:
            os.unlink(temporary_name, dir_fd=cache_directory)
        except OSError:
            pass
        raise
    finally:
        os.close(temporary_fd)


def _append_jsonl_at(root_descriptor: int, journal_name: str, value: dict,
                     cache_directory: int, identity: str,
                     max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES,
                     dedupe_field: str | None = None,
                     dedupe_value: object = None,
                     hook: Callable[[str], None] | None = None) -> AppendOutcome:
    """Append a JSONL object using pinned POSIX directory descriptors.

    This is intentionally a separate primitive from :func:`append_jsonl`: the latter's
    pathname API is retained for existing journals, while this API never resolves the root,
    journal, cache, temporary, or replacement names through an attacker-switchable parent.
    """
    if os.name == "nt" or not hasattr(os, "supports_dir_fd") or not os.supports_dir_fd:
        raise JsonlDurabilityError("pinned JSONL persistence is unavailable on this platform")
    if not isinstance(value, dict):
        raise JsonlDurabilityError("JSONL append requires an object")
    if not isinstance(max_record_bytes, int) or isinstance(max_record_bytes, bool) \
            or max_record_bytes < 0:
        raise JsonlDurabilityError("JSONL max_record_bytes must be a non-negative integer")
    try:
        encoded = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeDecodeError) as exc:
        raise JsonlDurabilityError("JSONL append value is not serializable") from exc
    if len(encoded) - 1 > max_record_bytes:
        raise JsonlDurabilityError(f"new JSONL record exceeds {max_record_bytes} bytes")
    cache_name = index_cache_name(identity)
    journal = _pinned_fd_path(root_descriptor, journal_name)
    journal_descriptor = os.open(
        journal_name,
        os.O_RDWR | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0),
        0o600, dir_fd=root_descriptor,
    )
    connection: sqlite3.Connection | None = None
    try:
        journal_identity = _capture_opened_leaf(journal, journal_descriptor)
        _lock_descriptor(journal_descriptor)
        _revalidate_opened_leaf(journal, journal_descriptor, journal_identity)
        size = os.fstat(journal_descriptor).st_size
        if size:
            _revalidate_opened_leaf(journal, journal_descriptor, journal_identity)
        if size and _read_at(journal_descriptor, 1, size - 1) != b"\n":
            raise JsonlDurabilityError(f"unterminated pinned JSONL tail: {journal_name}")
        journal_stat = os.fstat(journal_descriptor)
        validate_durable_leaf_at(cache_directory, cache_name, allow_missing=True)
        if hook is not None:
            hook("pre-sqlite-open")
        # Keep SQLite entirely in memory for this descriptor-based path.  sqlite3's filename
        # API cannot consume an open directory fd without reopening a switchable leaf, and
        # its rollback journal would introduce more pathnames.  The authoritative journal is
        # already fsynced; the serialized verification cache is only a rebuildable derivative.
        connection = sqlite3.connect(":memory:")
        _create_index_schema(connection)
        connection.execute("BEGIN IMMEDIATE")
        line_count = 0
        chain = ZERO_CHAIN_SHA256
        for line_count, line in enumerate(
                _iter_complete_lines(journal_descriptor, journal_stat.st_size, journal, max_record_bytes), 1):
            _insert_line(connection, line_count, line)
            chain = line.chain_sha256
        _write_metadata(connection, identity, journal_stat, max_record_bytes, line_count, chain)
        connection.commit()
        if _duplicate_in_index(connection, dedupe_field, dedupe_value):
            if not hasattr(connection, "serialize"):
                raise JsonlDurabilityError("SQLite serialization is unavailable for pinned persistence")
            _install_serialized_cache(cache_directory, cache_name, connection.serialize(), hook)
            return AppendOutcome(appended=False, quarantine=None)
        if hook is not None:
            hook("pre-journal-write")
        _write_all(journal_descriptor, encoded, leaf_path=journal,
                   leaf_identity=journal_identity)
        os.fsync(journal_descriptor)
        _update_index_after_append(
            connection, journal_descriptor, journal, encoded, max_record_bytes
        )
        if not hasattr(connection, "serialize"):
            raise JsonlDurabilityError("SQLite serialization is unavailable for pinned persistence")
        _install_serialized_cache(cache_directory, cache_name, connection.serialize(), hook)
        os.fsync(root_descriptor)
        return AppendOutcome(appended=True, quarantine=None)
    finally:
        if connection is not None:
            connection.close()
        _unlock_file_descriptor(journal_descriptor)
        os.close(journal_descriptor)


def append_jsonl_at(root_descriptor: int, journal_name: str, value: dict,
                    cache_directory: int, identity: str,
                    max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES,
                    dedupe_field: str | None = None,
                    dedupe_value: object = None,
                    hook: Callable[[str], None] | None = None) -> AppendOutcome:
    """Typed boundary for the descriptor-pinned POSIX JSONL append primitive."""
    try:
        return _append_jsonl_at(
            root_descriptor, journal_name, value, cache_directory, identity,
            max_record_bytes, dedupe_field, dedupe_value, hook,
        )
    except JsonlDurabilityError:
        raise
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeDecodeError, UnicodeEncodeError, sqlite3.DatabaseError) as exc:
        raise JsonlDurabilityError(f"pinned JSONL append refused: {exc}") from exc

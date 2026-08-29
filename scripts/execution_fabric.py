#!/usr/bin/env python3
"""Provider-neutral placement primitives for the Recursion v2 execution fabric.

This module is deliberately an inert library.  It has no network, process, git, credential,
PAUSE, or service integration.  Callers provide immutable registry snapshots and receive
deterministic placement decisions.  Durable state is an append-only local journal so a controller
restart can replay leases and attempts without relaunching remote work.

The wire records are schema-versioned and strict: unknown keys, missing required keys, malformed
identities, and secret-looking values fail closed.  The module is suitable for hermetic tests and
for a later adapter which explicitly opts into the control-plane seams.
"""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import math
import os
import re
import secrets
import stat
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from types import MappingProxyType


SCHEMA_VERSION = 1
FABRIC_SCHEMA = "recursion-execution-fabric-v1"
ZERO_DIGEST = "0" * 64
DEFAULT_HEARTBEAT_FUTURE_SKEW = 30.0
MAX_JSON_BYTES = 1_048_576
MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 10_000
MAX_JSON_INTEGER_BITS = 1024
MAX_JSON_INTEGER_DIGITS = 310
# Largest finite IEEE-754 binary64 value expressed exactly as an integer.
MAX_FINITE_INTEGER = (1 << 1024) - (1 << 971)
_WINDOWS_FILE_ATTRIBUTE_DIRECTORY = 0x10
_WINDOWS_FILE_ATTRIBUTE_REPARSE_POINT = 0x400

_ID = re.compile(r"[a-z][a-z0-9-]{1,63}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_ISO = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\Z")
_COMMIT = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
_SECRET_KEY = re.compile(r"(?:secret|token|password|private|credential|api[_-]?key)", re.I)
_VERIFIER_IDENTITY = re.compile(r"controller/.+\Z")
_BRANCH = re.compile(r"(?!/)(?!.*//)(?!.*/$)(?!.*\.\.)(?!\.)(?!.*/\.)(?!refs/)(?!HEAD)[A-Za-z0-9_./-]+\Z")
_ALLOWED_PATH = re.compile(r"(?!/)(?![A-Za-z]:)(?!.*\.\.)[A-Za-z0-9_./-]+\Z")
_KEY_HEX = re.compile(r"(?:[0-9a-f]{2})+\Z")
_PLACEMENT_POLICIES = frozenset({"manual-pin", "subscription-first", "local-first", "cheapest-eligible",
                                "fastest-eligible", "strongest-reviewer", "weighted-rotation"})

_INPUT_ERRORS = (json.JSONDecodeError, ValueError, TypeError, OverflowError,
                 RecursionError, UnicodeDecodeError, UnicodeError, OSError, AttributeError)


class FabricError(ValueError):
    """Base class for fail-closed fabric errors."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class SchemaError(FabricError):
    pass


class AdmissionError(FabricError):
    pass


class ReconciliationError(FabricError):
    pass


class _JsonInputError(SchemaError):
    """Internal marker so durable reloads can classify malformed JSON correctly."""


def _typed_boundary(kind: str):
    """Turn hostile Python/JSON boundary failures into a fabric error."""
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except FabricError:
                raise
            except _INPUT_ERRORS as exc:
                raise SchemaError("INVALID_INPUT", f"invalid {kind}") from exc
        return wrapped
    return decorate


def _regex_fullmatch(pattern: re.Pattern[str], value: Any, field: str) -> str | None:
    try:
        return pattern.fullmatch(value)  # type: ignore[arg-type]
    except _INPUT_ERRORS as exc:
        raise SchemaError("INVALID_FIELD", f"{field} has an invalid value") from exc


def _strict_int(value: Any, field: str, *, minimum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum):
        qualifier = "integer" if minimum is None else f"integer >= {minimum}"
        raise SchemaError("INVALID_FIELD", f"{field} must be a {qualifier}")
    return value


def _schema_version(value: Any, kind: str) -> None:
    if type(value) is not int or value != SCHEMA_VERSION:
        raise SchemaError("SCHEMA_VERSION", f"unsupported {kind} schema")


def _finite_number(value: Any, field: str, *, minimum: float | None = None) -> float:
    if type(value) not in {int, float}:
        raise SchemaError("INVALID_FIELD", f"{field} must be a finite number")
    if type(value) is int and value > MAX_FINITE_INTEGER:
        raise SchemaError("INVALID_FIELD", f"{field} must be a finite number")
    try:
        converted = float(value)
    except _INPUT_ERRORS as exc:
        raise SchemaError("INVALID_FIELD", f"{field} must be a finite number") from exc
    if not math.isfinite(converted) or (minimum is not None and converted < minimum):
        raise SchemaError("INVALID_FIELD", f"{field} must be a finite number")
    return converted


def _bounded_json_text(text: Any) -> str:
    if not isinstance(text, str):
        raise SchemaError("INVALID_JSON", "JSON input must be text")
    if len(text.encode("utf-8", errors="strict")) > MAX_JSON_BYTES:
        raise SchemaError("INPUT_TOO_LARGE", "JSON input exceeds the size limit")
    depth = 0
    escaped = False
    in_string = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                raise SchemaError("INPUT_TOO_DEEP", "JSON nesting exceeds the depth limit")
        elif char in "]}":
            depth -= 1
            if depth < 0:
                raise SchemaError("INVALID_JSON", "JSON delimiters are unbalanced")
    if in_string or depth != 0:
        # Let the parser provide the ordinary malformed-json classification,
        # but keep it behind the typed boundary below.
        return text
    return text


def _json_node_budget(item: Any, field: str, *, depth: int, budget: list[int]) -> None:
    if depth > MAX_JSON_DEPTH:
        raise SchemaError("INPUT_TOO_DEEP", f"{field} nesting exceeds the depth limit")
    budget[0] += 1
    if budget[0] > MAX_JSON_NODES:
        raise SchemaError("INPUT_TOO_LARGE", f"{field} contains too many values")


def _safe_int(value: Any, field: str, *, base: int | None = None) -> int:
    try:
        if base is None:
            if type(value) is not int:
                raise TypeError
            converted = value
        else:
            if type(value) is not str:
                raise TypeError
            converted = int(value, base)
    except _INPUT_ERRORS as exc:
        raise SchemaError("INVALID_FIELD", f"{field} must be an integer") from exc
    return converted


def _json_line(value: Mapping[str, Any], kind: str) -> bytes:
    try:
        return (json.dumps(dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")
    except _INPUT_ERRORS as exc:
        raise ReconciliationError("INVALID_RECORD", f"{kind} cannot be serialized") from exc


def _check_keys(value: Mapping[str, Any], required: set[str], optional: set[str], kind: str) -> None:
    if not isinstance(value, Mapping):
        raise SchemaError("INVALID_RECORD", f"{kind} must be an object")
    keys = set(value)
    missing = sorted(required - keys)
    unknown = sorted(keys - required - optional)
    if missing:
        raise SchemaError("MISSING_FIELD", f"{kind} missing fields: {', '.join(missing)}")
    if unknown:
        raise SchemaError("UNKNOWN_FIELD", f"{kind} has unknown fields: {', '.join(unknown)}")


def _string(value: Any, field: str, *, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise SchemaError("INVALID_FIELD", f"{field} must be a non-empty string")
    if pattern is not None and _regex_fullmatch(pattern, value, field) is None:
        raise SchemaError("INVALID_FIELD", f"{field} has an invalid value")
    return value


def _id(value: Any, field: str) -> str:
    return _string(value, field, pattern=_ID)


def _digest(value: Any, field: str) -> str:
    return _string(value, field, pattern=_SHA256)


def _commit(value: Any, field: str) -> str:
    """Validate a git object id (the normal 40-char form or a full SHA-256 id)."""
    return _string(value, field, pattern=_COMMIT)


def _timestamp(value: Any, field: str) -> str:
    text = _string(value, field, pattern=_ISO)
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except _INPUT_ERRORS as exc:
        raise SchemaError("INVALID_TIMESTAMP", f"{field} is not a real UTC timestamp") from exc
    if parsed.tzinfo != timezone.utc:
        raise SchemaError("INVALID_TIMESTAMP", f"{field} must be UTC")
    return text


def _string_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise SchemaError("INVALID_FIELD", f"{field} must be a list of strings")
    result = tuple(sorted(set(value)))
    if len(result) != len(value):
        raise SchemaError("INVALID_FIELD", f"{field} must not contain duplicates")
    return result


def _branch(value: Any, field: str) -> str:
    value = _string(value, field)
    if _regex_fullmatch(_BRANCH, value, field) is None:
        raise SchemaError("INVALID_FIELD", f"{field} has an invalid value")
    return value


def _allowed_path_list(value: Any, field: str) -> tuple[str, ...]:
    values = _string_list(value, field)
    for item in values:
        if _regex_fullmatch(_ALLOWED_PATH, item, field) is None:
            raise SchemaError("INVALID_FIELD", f"{field} contains a path outside the project")
    return values


def _nonnegative_int(value: Any, field: str) -> int:
    if (type(value) is not int or value < 0 or value.bit_length() > MAX_JSON_INTEGER_BITS or
            value > MAX_FINITE_INTEGER):
        raise SchemaError("INVALID_FIELD", f"{field} must be a non-negative integer")
    return value


def _nonnegative_number(value: Any, field: str) -> float:
    try:
        converted = _finite_number(value, field, minimum=0)
    except SchemaError:
        raise SchemaError("INVALID_FIELD", f"{field} must be a non-negative number")
    return converted


def _json_value(item: Any, field: str = "record", *, _depth: int = 0, _budget: list[int] | None = None) -> Any:
    budget = [0] if _budget is None else _budget
    _json_node_budget(item, field, depth=_depth, budget=budget)
    if item is None or type(item) in {str, bool}:
        return item
    if type(item) is int:
        if item.bit_length() > MAX_JSON_INTEGER_BITS or item > MAX_FINITE_INTEGER or item < -MAX_FINITE_INTEGER:
            raise SchemaError("INPUT_TOO_LARGE", f"{field} contains an oversized integer")
        return item
    if type(item) is float:
        if not math.isfinite(item):
            raise SchemaError("NONFINITE_NUMBER", "records cannot contain NaN or infinity")
        return item
    if isinstance(item, Mapping):
        normalized: dict[str, Any] = {}
        for key, nested in item.items():
            if type(key) is not str:
                raise SchemaError("INVALID_FIELD", f"{field} object keys must be strings")
            normalized[key] = _json_value(nested, f"{field}.{key}", _depth=_depth + 1, _budget=budget)
        return normalized
    if isinstance(item, list):
        return [_json_value(nested, field, _depth=_depth + 1, _budget=budget) for nested in item]
    raise SchemaError("INVALID_FIELD", f"{field} contains a non-JSON value")


def _ensure_finite(item: Any) -> None:
    _json_value(item)


def _canonical(value: Mapping[str, Any]) -> bytes:
    normalized = _json_value(value)
    if not isinstance(normalized, dict):
        raise SchemaError("INVALID_RECORD", "canonical values must be objects")
    try:
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    except _INPUT_ERRORS as exc:
        raise SchemaError("INVALID_RECORD", "canonical values cannot be serialized") from exc


def _json_load(text: str) -> Any:
    def reject_constant(value: str) -> Any:
        raise ValueError(f"non-finite JSON number: {value}")
    def parse_int(value: str) -> int:
        if len(value.lstrip("-")) > MAX_JSON_INTEGER_DIGITS:
            raise ValueError("JSON integer exceeds the size limit")
        return int(value)
    def parse_float(value: str) -> float:
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError("non-finite JSON number")
        return parsed
    try:
        try:
            bounded = _bounded_json_text(text)
        except SchemaError as exc:
            raise _JsonInputError(exc.code, str(exc)) from exc
        return json.loads(bounded, parse_constant=reject_constant,
                          parse_int=parse_int, parse_float=parse_float)
    except _JsonInputError:
        raise
    except _INPUT_ERRORS as exc:
        raise _JsonInputError("INVALID_JSON", "JSON input cannot be decoded") from exc


def _windows_kernel32() -> Any:
    import ctypes
    return ctypes.WinDLL("kernel32", use_last_error=True)


def _windows_handle_value(handle: Any) -> int:
    return _safe_int(handle.value if hasattr(handle, "value") else handle, "Windows handle")


def _windows_file_info(handle: Any) -> tuple[tuple[int, int, int], bool, int, bool]:
    import ctypes
    from ctypes import wintypes

    class FileInformation(ctypes.Structure):
        _fields_ = [("attributes", wintypes.DWORD), ("creation", wintypes.FILETIME),
                    ("access", wintypes.FILETIME), ("write", wintypes.FILETIME),
                    ("volume", wintypes.DWORD), ("size_high", wintypes.DWORD),
                    ("size_low", wintypes.DWORD), ("links", wintypes.DWORD),
                    ("index_high", wintypes.DWORD), ("index_low", wintypes.DWORD)]

    info = FileInformation()
    kernel32 = _windows_kernel32()
    if not kernel32.GetFileInformationByHandle(handle, ctypes.byref(info)):
        raise OSError(ctypes.get_last_error(), "GetFileInformationByHandle failed")
    identity = (_safe_int(info.volume, "Windows volume"), _safe_int(info.index_high, "Windows file id"),
                _safe_int(info.index_low, "Windows file id"))
    attributes = _safe_int(info.attributes, "Windows file attributes")
    links = _safe_int(info.links, "Windows link count")
    return identity, bool(attributes & _WINDOWS_FILE_ATTRIBUTE_DIRECTORY), links, bool(attributes & _WINDOWS_FILE_ATTRIBUTE_REPARSE_POINT)


def _leaf_info_for_handle(handle: Any) -> tuple[tuple[int, int, int], bool, int, bool]:
    return _windows_file_info(handle)


def _leaf_info_for_descriptor(descriptor: int) -> Any:
    if os.name == "nt":
        import msvcrt
        return _leaf_info_for_handle(msvcrt.get_osfhandle(descriptor))
    return os.fstat(descriptor)


def _windows_open(path: Path, *, directory: bool, write: bool, create: bool = False,
                  exclusive: bool = False, deny_delete: bool = False, rename: bool = False) -> tuple[Any, tuple[int, int, int], bool, int, bool]:
    import ctypes
    from ctypes import wintypes

    kernel32 = _windows_kernel32()
    kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                     wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    desired_access = 0 if directory else (0x40000000 if write else 0x80000000)
    if rename and not directory:
        desired_access |= 0x00010000  # DELETE is required by SetFileInformationByHandle.
    share_mode = 0x00000001 | 0x00000002  # FILE_SHARE_READ | FILE_SHARE_WRITE
    if not deny_delete:
        share_mode |= 0x00000004  # FILE_SHARE_DELETE; directory pins deliberately omit it.
    disposition = 1 if exclusive else (4 if create else 3)  # CREATE_NEW / OPEN_ALWAYS / OPEN_EXISTING
    flags = 0x02000000 | 0x00200000  # FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT
    handle = kernel32.CreateFileW(str(path), desired_access, share_mode, None, disposition, flags, None)
    invalid = ctypes.c_void_p(-1).value
    if handle is None or _windows_handle_value(handle) in {-1, invalid}:
        raise OSError(ctypes.get_last_error(), f"cannot open durable store path: {path}")
    try:
        identity, is_directory, links, is_reparse = _leaf_info_for_handle(handle)
        return handle, identity, is_directory, links, is_reparse
    except BaseException:
        _close_windows(handle)
        raise


def _close_windows(handle: Any) -> None:
    import ctypes
    from ctypes import wintypes

    kernel32 = _windows_kernel32()
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    if not kernel32.CloseHandle(handle):
        raise OSError(ctypes.get_last_error(), "CloseHandle failed")


def _windows_path_is_reparse(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise ReconciliationError("UNSAFE_STORE_PATH", "store ancestor cannot be inspected safely") from exc
    return bool(stat.S_ISLNK(info.st_mode) or
                _safe_int(getattr(info, "st_file_attributes", 0), "file attributes") & _WINDOWS_FILE_ATTRIBUTE_REPARSE_POINT or
                _safe_int(getattr(info, "st_reparse_tag", 0), "reparse tag"))


class _WindowsPinnedDirectory:
    """Native pins and identities for every component of a store directory path."""

    def __init__(self, entries: Sequence[tuple[Path, Any, tuple[int, int, int]]]):
        self.entries = tuple(entries)
        self.handle = self.entries[-1][1]

    def validate(self) -> None:
        """Confirm the pinned objects and their current path names still agree."""
        for path, handle, expected_identity in self.entries:
            identity, is_directory, _, is_reparse = _leaf_info_for_handle(handle)
            if (not is_directory or is_reparse or identity != expected_identity or
                    _windows_path_is_reparse(path)):
                raise ReconciliationError("UNSAFE_STORE_PATH", "store ancestor identity changed")
            probe, probe_identity, probe_directory, _, probe_reparse = _windows_open(
                path, directory=True, write=False, deny_delete=True)
            try:
                if (not probe_directory or probe_reparse or probe_identity != expected_identity):
                    raise ReconciliationError("UNSAFE_STORE_PATH", "store ancestor identity changed")
            finally:
                _close_windows(probe)


def _validate_pinned_directory(directory: Any) -> None:
    if os.name == "nt":
        directory.validate()


def _windows_replace_by_handle(source_descriptor: int, source_identity: Any, directory: Any,
                               source_path: Path, destination_path: Path) -> None:
    """Atomically publish a validated root-local temporary leaf."""
    import ctypes
    from ctypes import wintypes
    import msvcrt

    destination = Path(destination_path)
    if not destination.is_absolute() or not destination.name:
        raise OSError("destination path must be absolute")
    source = Path(source_path)
    if not source.is_absolute() or not source.name:
        raise OSError("source path must be absolute")
    _validate_pinned_directory(directory)
    _validate_leaf_info(_leaf_info_for_descriptor(source_descriptor), identity=source_identity)

    class RenameInfo(ctypes.Structure):
        # FILE_RENAME_INFO uses a one-byte BOOLEAN followed by an aligned
        # HANDLE.  FileRenameInfoEx (class 22) is not available on all
        # supported Windows filesystems and returned ERROR_INVALID_PARAMETER
        # for ordinary durable files.
        _fields_ = [
            ("replace_if_exists", ctypes.c_ubyte),
            ("root_directory", wintypes.HANDLE),
            ("file_name_length", wintypes.DWORD),
            ("file_name", wintypes.WCHAR * 1),
        ]

    encoded_name = str(destination).encode("utf-16-le")
    name_offset = RenameInfo.file_name.offset
    # The native variable-tail contract is sizeof(FILE_RENAME_INFO) plus the
    # UTF-16 name length; allocating only through the tail offset is rejected
    # by SetFileInformationByHandle with ERROR_INVALID_PARAMETER.
    buffer_size = ctypes.sizeof(RenameInfo) + len(encoded_name)
    buffer = ctypes.create_string_buffer(buffer_size)
    info = ctypes.cast(buffer, ctypes.POINTER(RenameInfo)).contents
    info.replace_if_exists = 1
    # The absolute path avoids relying on filesystem-specific support for a
    # non-NULL RootDirectory in FILE_RENAME_INFO. The caller has already
    # pinned and revalidated this path's complete ancestor chain.
    info.root_directory = None
    info.file_name_length = len(encoded_name)
    ctypes.memmove(ctypes.addressof(buffer) + name_offset, encoded_name, len(encoded_name))

    kernel32 = _windows_kernel32()
    kernel32.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
    kernel32.SetFileInformationByHandle.restype = wintypes.BOOL
    source_handle = wintypes.HANDLE(msvcrt.get_osfhandle(source_descriptor))
    if kernel32.SetFileInformationByHandle(source_handle, 3, ctypes.byref(buffer), buffer_size):
        return
    raise OSError(ctypes.get_last_error(), "cannot atomically replace durable store leaf")


@contextmanager
def _pin_store_directory(path: Path):
    if os.name == "nt":
        handles: list[Any] = []
        try:
            ancestors = list(path.parents)
            ancestors.reverse()
            ancestors.append(path)
            for ancestor in ancestors:
                # lstat is an independent path-level check.  The native open
                # below also uses OPEN_REPARSE_POINT, but keeping both checks
                # makes a junction swap fail even on filesystems where the
                # handle's basic attributes do not expose the reparse bit.
                if _windows_path_is_reparse(ancestor):
                    raise ReconciliationError("UNSAFE_STORE_PATH", "store parent is not a real directory")
                handle, identity, is_directory, _, is_reparse = _windows_open(
                    ancestor, directory=True, write=False, deny_delete=True)
                if not is_directory or is_reparse:
                    _close_windows(handle)
                    raise ReconciliationError("UNSAFE_STORE_PATH", "store parent is not a real directory")
                handles.append((ancestor, handle, identity))
            pinned = _WindowsPinnedDirectory(handles)
            pinned.validate()
            yield pinned
        finally:
            for _, handle, _ in reversed(handles):
                _close_windows(handle)
        return

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    try:
        # Open each component relative to the descriptor for its already-open
        # parent.  This is the POSIX equivalent of holding every Windows
        # ancestor handle: a rename/reparse swap cannot redirect the next
        # component lookup.
        absolute = Path(os.path.abspath(os.fspath(path)))
        anchor = absolute.anchor or os.path.sep
        descriptor = os.open(anchor, flags)
        descriptors.append(descriptor)
        for part in absolute.parts[1:]:
            descriptor = os.open(part, flags, dir_fd=descriptor)
            descriptors.append(descriptor)
        info = os.fstat(descriptors[-1])
        if not stat.S_ISDIR(info.st_mode):
            raise OSError("store parent is not a directory")
    except OSError as exc:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise ReconciliationError("UNSAFE_STORE_PATH", "store parent cannot be pinned safely") from exc
    try:
        yield descriptors[-1]
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _validate_leaf_info(info: Any, *, identity: Any = None) -> Any:
    if os.name == "nt":
        actual, is_directory, links, is_reparse = info
        if is_directory or is_reparse or links != 1:
            raise ReconciliationError("UNSAFE_STORE_PATH", "durable store leaf is not a unique regular file")
    else:
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ReconciliationError("UNSAFE_STORE_PATH", "durable store leaf is not a unique regular file")
        actual = (info.st_dev, info.st_ino)
    if identity is not None and actual != identity:
        raise ReconciliationError("UNSAFE_STORE_PATH", "durable store leaf identity changed")
    return actual


def _open_leaf_in_directory(directory: Any, path: Path, *, write: bool, create: bool, append: bool = False,
                            exclusive: bool = False, deny_delete: bool = False, rename: bool = False,
                            expected_identity: Any = None) -> tuple[int, Any]:
    _validate_pinned_directory(directory)
    if os.name == "nt":
        handle, identity, is_directory, links, is_reparse = _windows_open(
            path, directory=False, write=write, create=create, exclusive=exclusive, deny_delete=deny_delete,
            rename=rename)
        try:
            actual = _validate_leaf_info((identity, is_directory, links, is_reparse), identity=expected_identity)
            import msvcrt
            fd_flags = (os.O_WRONLY if write else os.O_RDONLY) | (getattr(os, "O_APPEND", 0) if append else 0) | getattr(os, "O_BINARY", 0)
            descriptor = msvcrt.open_osfhandle(_windows_handle_value(handle), fd_flags)
            return descriptor, actual
        except BaseException:
            _close_windows(handle)
            raise
    name = path.name
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    try:
        before = os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        if not create:
            raise
        descriptor = os.open(name, (os.O_WRONLY if write else os.O_RDONLY) | (getattr(os, "O_APPEND", 0) if append else 0) | os.O_CREAT | os.O_EXCL | nofollow,
                             0o600, dir_fd=directory)
        try:
            actual = _validate_leaf_info(_leaf_info_for_descriptor(descriptor), identity=expected_identity)
            return descriptor, actual
        except BaseException:
            os.close(descriptor)
            raise
    before_identity = _validate_leaf_info(before, identity=expected_identity)
    descriptor = os.open(name, (os.O_WRONLY if write else os.O_RDONLY) | (getattr(os, "O_APPEND", 0) if append else 0) | nofollow, dir_fd=directory)
    try:
        actual = _validate_leaf_info(_leaf_info_for_descriptor(descriptor), identity=before_identity)
        return descriptor, actual
    except BaseException:
        os.close(descriptor)
        raise


@contextmanager
def _open_store_leaf(path: Path, *, write: bool, create: bool, append: bool = False,
                     expected_identity: Any = None, deny_delete: bool = False):
    with _pin_store_directory(path.parent) as directory:
        descriptor, identity = _open_leaf_in_directory(directory, path, write=write, create=create, append=append,
                                                       expected_identity=expected_identity, deny_delete=deny_delete)
        try:
            yield descriptor, identity, directory
        finally:
            os.close(descriptor)


def _read_store_bytes(path: Path, *, expected_identity: Any = None) -> tuple[bytes, Any] | None:
    try:
        with _open_store_leaf(path, write=False, create=False, expected_identity=expected_identity,
                              deny_delete=False) as (descriptor, identity, directory):
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            _validate_pinned_directory(directory)
            _validate_leaf_info(_leaf_info_for_descriptor(descriptor), identity=identity)
            return b"".join(chunks), identity
    except FileNotFoundError:
        return None
    except ReconciliationError:
        raise
    except (OSError, UnicodeError) as exc:
        raise ReconciliationError("UNSAFE_STORE_PATH", "durable store leaf cannot be read safely") from exc


def _write_new_leaf(directory: Any, path: Path, data: bytes) -> tuple[int, Any]:
    """Create and fully write a new leaf while it is still private to root."""
    descriptor, identity = _open_leaf_in_directory(
        directory, path, write=True, create=True, exclusive=True, deny_delete=False, rename=True)
    try:
        view = memoryview(data)
        while view:
            _validate_pinned_directory(directory)
            _validate_leaf_info(_leaf_info_for_descriptor(descriptor), identity=identity)
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("durable store write made no progress")
            view = view[written:]
        os.fsync(descriptor)
        _validate_pinned_directory(directory)
        _validate_leaf_info(_leaf_info_for_descriptor(descriptor), identity=identity)
        return descriptor, identity
    except BaseException:
        os.close(descriptor)
        raise


def _revalidate_destination(directory: Any, path: Path, *, expected_identity: Any,
                            must_exist: bool) -> None:
    """Re-open the destination through the pinned parent immediately before commit."""
    _validate_pinned_directory(directory)
    try:
        descriptor, identity = _open_leaf_in_directory(
            directory, path, write=False, create=False,
            # The leaf is always opened no-follow. Delete-sharing exclusion is
            # provided by the pinned parent/ancestor handles; allowing leaf
            # delete sharing also permits the post-commit probe while the
            # source handle remains open after an atomic rename.
            expected_identity=expected_identity if must_exist else None, deny_delete=False)
    except FileNotFoundError:
        if must_exist:
            raise ReconciliationError("UNSAFE_STORE_PATH", "durable store destination disappeared")
        return
    try:
        if not must_exist:
            raise ReconciliationError("UNSAFE_STORE_PATH", "durable store destination appeared before commit")
        _validate_leaf_info(_leaf_info_for_descriptor(descriptor), identity=identity)
    finally:
        os.close(descriptor)


def _commit_absent_leaf(directory: Any, temporary_path: Path, path: Path,
                        temporary_descriptor: int, temporary_identity: Any) -> None:
    """Bind a replacement to an absent directory entry without overwriting a race."""
    _validate_pinned_directory(directory)
    try:
        if os.name == "nt":
            # os.link has no useful dir_fd implementation on Windows.  The
            # absolute paths are safe because every ancestor remains pinned.
            os.link(temporary_path, path, follow_symlinks=False)
        else:
            os.link(temporary_path.name, path.name, src_dir_fd=directory, dst_dir_fd=directory,
                    follow_symlinks=False)
    except FileExistsError as exc:
        raise ReconciliationError("UNSAFE_STORE_PATH", "durable store destination appeared before commit") from exc
    _validate_pinned_directory(directory)
    try:
        if os.name == "nt":
            temporary_path.unlink()
        else:
            os.unlink(temporary_path.name, dir_fd=directory)
    except OSError as exc:
        raise ReconciliationError("UNSAFE_STORE_PATH", "durable store temporary cannot be retired") from exc
    # The link operation necessarily makes the inode have two names for this
    # short interval.  Verify the final single-link invariant only after the
    # private temporary name has been retired.
    _validate_leaf_info(_leaf_info_for_descriptor(temporary_descriptor), identity=temporary_identity)
    _revalidate_destination(directory, path, expected_identity=temporary_identity, must_exist=True)


def _append_bytes(path: Path, data: bytes, *, expected_identity: Any = None) -> Any:
    """Append by replacing a fully-written root-local snapshot.

    Writing directly through an existing inode is unsafe: a hardlink can be
    added after its final handle check and make the append visible outside the
    configured root.  A private replacement means every byte is written only
    to a fresh root-local leaf, and the old leaf is never mutated.
    """
    try:
        stored = _read_store_bytes(path, expected_identity=expected_identity)
        prior, identity = (b"", None) if stored is None else stored
        if not isinstance(data, bytes):
            raise TypeError("durable append data must be bytes")
        return _replace_store_bytes(path, prior + data, expected_identity=identity)
    except ReconciliationError:
        raise
    except _INPUT_ERRORS as exc:
        raise ReconciliationError("UNSAFE_STORE_PATH", "durable store leaf cannot be appended safely") from exc


def _replace_store_bytes(path: Path, data: bytes, *, expected_identity: Any = None) -> Any:
    try:
        with _pin_store_directory(path.parent) as directory:
            current = None
            current_descriptor = None
            try:
                current_descriptor, current = _open_leaf_in_directory(
                    directory, path, write=False, create=False, expected_identity=expected_identity,
                    deny_delete=False)
            except FileNotFoundError:
                if expected_identity is not None:
                    raise ReconciliationError("UNSAFE_STORE_PATH", "durable store leaf disappeared")
            temporary_name = f".{path.name}.tmp.{os.getpid()}.{threading.get_ident()}.{secrets.token_hex(8)}"
            temporary_path = path.parent / temporary_name
            temporary_descriptor = None
            committed = False
            try:
                if not isinstance(data, bytes):
                    raise TypeError("durable replacement data must be bytes")
                temporary_descriptor, temporary_identity = _write_new_leaf(directory, temporary_path, data)
                if os.name == "nt":
                    # Reopen the flushed private leaf with the access profile
                    # accepted by FileRenameInfo. The reopen is no-follow and
                    # identity-bound, so a replacement between the write and
                    # the commit handle is rejected rather than followed.
                    written_identity = temporary_identity
                    os.close(temporary_descriptor)
                    temporary_descriptor = None
                    temporary_descriptor, temporary_identity = _open_leaf_in_directory(
                        directory, temporary_path, write=False, create=False, rename=True,
                        expected_identity=written_identity)
                _validate_pinned_directory(directory)
                _validate_leaf_info(_leaf_info_for_descriptor(temporary_descriptor), identity=temporary_identity)
                if current_descriptor is not None:
                    # The same original handle is retained through commit;
                    # this catches a hardlink or unlink race even if the
                    # path-level probe was stale.
                    _validate_leaf_info(_leaf_info_for_descriptor(current_descriptor), identity=current)
                _revalidate_destination(directory, path, expected_identity=current, must_exist=current is not None)
                if current_descriptor is not None:
                    # Re-check the original handle after the final name probe;
                    # the probe itself is a deterministic race-injection seam
                    # in the hostile-writer harness.
                    _validate_leaf_info(_leaf_info_for_descriptor(current_descriptor), identity=current)
                _revalidate_destination(directory, path, expected_identity=current, must_exist=current is not None)
                if current_descriptor is not None:
                    _validate_leaf_info(_leaf_info_for_descriptor(current_descriptor), identity=current)
                if current is None:
                    _commit_absent_leaf(directory, temporary_path, path, temporary_descriptor, temporary_identity)
                    committed = True
                else:
                    _validate_pinned_directory(directory)
                    if os.name == "nt":
                        # The destination handle shares delete so a hostile
                        # unlink/relink race remains observable through the
                        # same-handle link-count check above. Release that
                        # leaf handle before the atomic rename; the pinned
                        # parent handles continue to block ancestor replacement.
                        os.close(current_descriptor)
                        current_descriptor = None
                        _windows_replace_by_handle(
                            temporary_descriptor, temporary_identity, directory, temporary_path, path)
                    else:
                        # POSIX os.replace names the source path rather than
                        # consuming the already-open descriptor. Revalidate
                        # that same descriptor at the last possible moment so
                        # a hardlink/replacement race cannot publish a source
                        # whose identity changed after the earlier probes.
                        _validate_leaf_info(_leaf_info_for_descriptor(temporary_descriptor), identity=temporary_identity)
                        os.replace(temporary_name, path.name, src_dir_fd=directory, dst_dir_fd=directory)
                    committed = True
                    # The source handle is now the newly published leaf.  The
                    # post-commit probe binds that identity to the pinned name.
                    if temporary_descriptor is not None:
                        _validate_leaf_info(_leaf_info_for_descriptor(temporary_descriptor), identity=temporary_identity)
                    _revalidate_destination(directory, path, expected_identity=temporary_identity, must_exist=True)
                if temporary_descriptor is not None:
                    _validate_leaf_info(_leaf_info_for_descriptor(temporary_descriptor), identity=temporary_identity)
                return temporary_identity
            finally:
                if temporary_descriptor is not None:
                    os.close(temporary_descriptor)
                if current_descriptor is not None:
                    os.close(current_descriptor)
                if not committed:
                    try:
                        if os.name == "nt":
                            temporary_path.unlink(missing_ok=True)
                        else:
                            os.unlink(temporary_name, dir_fd=directory)
                    except FileNotFoundError:
                        pass
    except ReconciliationError:
        raise
    except OSError as exc:
        raise ReconciliationError("UNSAFE_STORE_PATH", "durable store replacement was not safe") from exc


@_typed_boundary("record")
def digest_record(value: Mapping[str, Any]) -> str:
    """Return the stable SHA-256 identity excluding only the record digest field."""
    if not isinstance(value, Mapping):
        raise SchemaError("INVALID_RECORD", "digest input must be an object")
    body = {key: item for key, item in value.items() if key != "digest"}
    return hashlib.sha256(_canonical(body)).hexdigest()


def _frozen_mapping(value: Mapping[str, int], field: str) -> Mapping[str, int]:
    if not isinstance(value, Mapping):
        raise SchemaError("INVALID_FIELD", f"{field} must be an object")
    return MappingProxyType(dict(sorted(((_string(key, f"{field} key"), _nonnegative_int(count, f"{field}.{key}")) for key, count in value.items()))))


def _reservation_counts(value: Mapping[Any, Any] | None, field: str) -> dict[Any, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise SchemaError("INVALID_FIELD", f"{field} must be an object")
    return {key: _nonnegative_int(count, f"{field}.{key}") for key, count in value.items()}


def _identity_bound_mapping(value: Any, field: str, record_type: type,
                            identity_field: str, parser: Any) -> dict[str, Any]:
    """Parse a registry map only when its caller key names the parsed object."""
    parsed: dict[str, Any] = {}
    for raw_key, item in value.items():
        key = _id(raw_key, f"{field} key")
        record = item if isinstance(item, record_type) else parser(item)
        record = parser(record.to_dict())
        if getattr(record, identity_field) != key:
            raise SchemaError("IDENTITY_MISMATCH", f"{field} key does not match {identity_field}")
        parsed[key] = record
    return parsed


def _file_is_reparse_or_symlink(path: Path) -> bool:
    if path.is_symlink():
        return True
    if os.name == "nt":
        try:
            info = os.lstat(path)
        except OSError:
            return False
        if bool(_safe_int(getattr(info, "st_file_attributes", 0), "file attributes") & _WINDOWS_FILE_ATTRIBUTE_REPARSE_POINT):
            return True
        # lstat on older Python/filesystem combinations does not expose the
        # junction bit consistently.  OPEN_REPARSE_POINT asks the kernel for
        # the final object itself and never follows it.
        try:
            handle, _, _, _, is_reparse = _windows_open(path, directory=True, write=False)
        except OSError:
            return False
        try:
            return is_reparse
        finally:
            _close_windows(handle)
    return False


def _safe_store_path(path: Path | str, root: Path | str | None) -> tuple[Path, Path]:
    raw = Path(path)
    root_path = Path(root) if root is not None else raw.parent
    # Normalize only lexically.  Path.resolve() is intentionally forbidden:
    # it follows a junction/reparse point and turns an escape into an apparently
    # safe path before the handle discipline gets a chance to reject it.
    root_abs = Path(os.path.abspath(os.fspath(root_path)))
    target_abs = Path(os.path.abspath(os.fspath(raw)))
    try:
        target_abs.relative_to(root_abs)
    except ValueError as exc:
        raise ReconciliationError("STORE_OUTSIDE_ROOT", "durable store path is outside the configured store root") from exc
    # Check existing components before creating anything. This rejects symlink/reparse escapes,
    # including a symlinked root or journal, instead of trusting resolve() to hide the boundary.
    current = root_abs
    while True:
        if _file_is_reparse_or_symlink(current):
            raise ReconciliationError("UNSAFE_STORE_ROOT", "store root path contains a symlink or reparse point")
        if current.parent == current:
            break
        current = current.parent
    try:
        relative = target_abs.relative_to(root_abs)
    except ValueError as exc:
        raise ReconciliationError("STORE_OUTSIDE_ROOT", "durable store path is outside the configured store root") from exc
    # The loop above ends at the filesystem root; restart from the configured
    # root before checking each in-root component, including every ancestor.
    current = root_abs
    for part in relative.parts:
        current = current / part
        if _file_is_reparse_or_symlink(current):
            raise ReconciliationError("UNSAFE_STORE_PATH", "durable store path contains a symlink or reparse point")
    return target_abs, root_abs


def _ensure_store_directory(path: Path) -> None:
    """Create missing store directories one component at a time, never through a reparse point."""
    path = Path(os.path.abspath(os.fspath(path)))
    try:
        os.lstat(path)
    except FileNotFoundError:
        if path.parent == path:
            raise ReconciliationError("UNSAFE_STORE_ROOT", "store root cannot be created safely")
        _ensure_store_directory(path.parent)
        try:
            if os.name == "nt":
                # Hold every existing ancestor while the missing component is
                # created. This closes the check-to-create junction swap
                # window before any durable leaf can be opened below it.
                with _pin_store_directory(path.parent):
                    path.mkdir()
            else:
                with _pin_store_directory(path.parent) as parent:
                    os.mkdir(path.name, 0o700, dir_fd=parent)
        except FileExistsError:
            pass
    except OSError as exc:
        raise ReconciliationError("UNSAFE_STORE_PATH", "store directory cannot be inspected safely") from exc
    # This is both the post-create validation and the last boundary check
    # before a caller obtains a leaf handle.  A concurrent replacement with a
    # junction is therefore observed before any descendant can be created.
    with _pin_store_directory(path):
        pass


_THREAD_LOCKS: dict[str, threading.RLock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()


@contextmanager
def _journal_lock(lock_path: Path):
    """Serialize journal mutations across threads and cooperating processes."""
    key = str(lock_path)
    with _THREAD_LOCKS_GUARD:
        lock = _THREAD_LOCKS.setdefault(key, threading.RLock())
    with lock:
        _ensure_store_directory(lock_path.parent)
        with _open_store_leaf(lock_path, write=True, create=True, deny_delete=True) as (descriptor, identity, directory):
            _validate_pinned_directory(directory)
            _validate_leaf_info(_leaf_info_for_descriptor(descriptor), identity=identity)
            try:
                if os.name == "nt":
                    import msvcrt
                    while True:
                        try:
                            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                            break
                        except OSError:
                            time.sleep(0.01)
                else:
                    import fcntl
                    fcntl.flock(descriptor, fcntl.LOCK_EX)
                yield
            finally:
                if os.name == "nt":
                    import msvcrt
                    try:
                        os.lseek(descriptor, 0, os.SEEK_SET)
                        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
                    except OSError:
                        pass
                else:
                    import fcntl
                    fcntl.flock(descriptor, fcntl.LOCK_UN)


@dataclass(frozen=True)
class HostRegistration:
    host_id: str
    capabilities: tuple[str, ...]
    operating_system: str
    architectures: tuple[str, ...]
    sandbox_profiles: tuple[str, ...]
    network_profiles: tuple[str, ...]
    trust_class: str
    max_concurrency: int
    workload_concurrency: Mapping[str, int]
    registration_digest: str
    registered_at: str
    network_endpoints: Mapping[str, tuple[str, ...]] = MappingProxyType({})

    def __post_init__(self) -> None:
        _nonnegative_int(self.max_concurrency, "max_concurrency")
        object.__setattr__(self, "workload_concurrency", _frozen_mapping(self.workload_concurrency, "workload_concurrency"))
        if not isinstance(self.network_endpoints, Mapping):
            raise SchemaError("INVALID_FIELD", "network_endpoints must be an object")
        endpoints: dict[str, tuple[str, ...]] = {}
        for profile, values in self.network_endpoints.items():
            profile = _string(profile, "network_endpoints profile")
            if isinstance(values, tuple):
                values = list(values)
            if not isinstance(values, list):
                raise SchemaError("INVALID_FIELD", f"network_endpoints.{profile} must be a list of strings")
            endpoints[profile] = _string_list(values, f"network_endpoints.{profile}")
        object.__setattr__(self, "network_endpoints", MappingProxyType(endpoints))

    @classmethod
    @_typed_boundary("host registration")
    def from_dict(cls, raw: Mapping[str, Any]) -> "HostRegistration":
        required = {"schema_version", "kind", "host_id", "capabilities", "operating_system",
                    "architectures", "sandbox_profiles", "network_profiles", "trust_class",
                    "max_concurrency", "workload_concurrency", "registration_digest", "registered_at", "network_endpoints"}
        _check_keys(raw, required, set(), "host_registration")
        _schema_version(raw["schema_version"], "host registration")
        if raw["kind"] != "host_registration":
            raise SchemaError("SCHEMA_VERSION", "unsupported host registration schema")
        host_id = _id(raw["host_id"], "host_id")
        caps = _string_list(raw["capabilities"], "capabilities")
        os_name = _string(raw["operating_system"], "operating_system")
        architectures = _string_list(raw["architectures"], "architectures")
        sandbox = _string_list(raw["sandbox_profiles"], "sandbox_profiles")
        network = _string_list(raw["network_profiles"], "network_profiles")
        trust = _string(raw["trust_class"], "trust_class")
        max_concurrency = _nonnegative_int(raw["max_concurrency"], "max_concurrency")
        workloads = raw["workload_concurrency"]
        if not isinstance(workloads, Mapping):
            raise SchemaError("INVALID_FIELD", "workload_concurrency must be an object")
        normalized: dict[str, int] = {}
        for key, count in sorted(workloads.items()):
            normalized[_string(key, "workload_concurrency key")] = _nonnegative_int(count, f"workload_concurrency.{key}")
        endpoints_raw = raw["network_endpoints"]
        if not isinstance(endpoints_raw, Mapping):
            raise SchemaError("INVALID_FIELD", "network_endpoints must be an object")
        endpoints: dict[str, tuple[str, ...]] = {}
        for profile, values in endpoints_raw.items():
            endpoints[_string(profile, "network_endpoints profile")] = _string_list(values, f"network_endpoints.{profile}")
        registration_digest = _digest(raw["registration_digest"], "registration_digest")
        expected = digest_record({key: value for key, value in raw.items() if key != "registration_digest"})
        if registration_digest != expected:
            raise SchemaError("DIGEST_MISMATCH", "host registration digest does not match immutable fields")
        return cls(host_id, caps, os_name, architectures, sandbox, network, trust, max_concurrency,
                   normalized, registration_digest, _timestamp(raw["registered_at"], "registered_at"), endpoints)

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "host_registration", "host_id": self.host_id,
                "capabilities": list(self.capabilities), "operating_system": self.operating_system,
                "architectures": list(self.architectures), "sandbox_profiles": list(self.sandbox_profiles),
                "network_profiles": list(self.network_profiles), "trust_class": self.trust_class,
                "max_concurrency": self.max_concurrency, "workload_concurrency": dict(self.workload_concurrency),
                "registration_digest": self.registration_digest, "registered_at": self.registered_at,
                "network_endpoints": {key: list(value) for key, value in self.network_endpoints.items()}}

    @classmethod
    @_typed_boundary("host registration")
    def build(cls, *, host_id: str, capabilities: Iterable[str], operating_system: str,
              architectures: Iterable[str], sandbox_profiles: Iterable[str],
              network_profiles: Iterable[str], trust_class: str, max_concurrency: int,
              workload_concurrency: Mapping[str, int], registered_at: str,
              network_endpoints: Mapping[str, Iterable[str]] | None = None) -> "HostRegistration":
        body = {"schema_version": SCHEMA_VERSION, "kind": "host_registration", "host_id": host_id,
                "capabilities": sorted(set(capabilities)), "operating_system": operating_system,
                "architectures": sorted(set(architectures)), "sandbox_profiles": sorted(set(sandbox_profiles)),
                "network_profiles": sorted(set(network_profiles)), "trust_class": trust_class,
                "max_concurrency": max_concurrency, "workload_concurrency": dict(sorted(workload_concurrency.items())),
                "registered_at": registered_at, "network_endpoints": {key: sorted(set(value)) for key, value in (network_endpoints or {}).items()}}
        body["registration_digest"] = digest_record(body)
        return cls.from_dict(body)


@dataclass(frozen=True)
class HostHeartbeat:
    host_id: str
    registration_digest: str
    sequence: int
    observed_at: str
    lease_epoch: int

    def __post_init__(self) -> None:
        _nonnegative_int(self.sequence, "sequence")
        _nonnegative_int(self.lease_epoch, "lease_epoch")

    @classmethod
    @_typed_boundary("host heartbeat")
    def from_dict(cls, raw: Mapping[str, Any]) -> "HostHeartbeat":
        required = {"schema_version", "kind", "host_id", "registration_digest", "sequence", "observed_at", "lease_epoch"}
        _check_keys(raw, required, set(), "host_heartbeat")
        _schema_version(raw["schema_version"], "host heartbeat")
        if raw["kind"] != "host_heartbeat":
            raise SchemaError("SCHEMA_VERSION", "unsupported host heartbeat schema")
        return cls(_id(raw["host_id"], "host_id"), _digest(raw["registration_digest"], "registration_digest"),
                   _nonnegative_int(raw["sequence"], "sequence"), _timestamp(raw["observed_at"], "observed_at"),
                   _nonnegative_int(raw["lease_epoch"], "lease_epoch"))

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "host_heartbeat", "host_id": self.host_id,
                "registration_digest": self.registration_digest, "sequence": self.sequence,
                "observed_at": self.observed_at, "lease_epoch": self.lease_epoch}


@dataclass(frozen=True)
class PoolStatus:
    pool_id: str
    billing_basis: str
    allowed_roles: tuple[str, ...]
    allowed_projects: tuple[str, ...]
    allowed_models: tuple[str, ...]
    max_concurrency: int
    in_flight: int
    quota_remaining: int | None
    quota_period: str | None
    on_demand: bool
    cost_per_run: float
    account_id: str | None = None
    account_quota_remaining: int | None = None

    def __post_init__(self) -> None:
        _nonnegative_int(self.max_concurrency, "max_concurrency")
        _nonnegative_int(self.in_flight, "in_flight")
        if self.quota_remaining is not None:
            _nonnegative_int(self.quota_remaining, "quota_remaining")
        if self.account_quota_remaining is not None:
            _nonnegative_int(self.account_quota_remaining, "account_quota_remaining")
        _nonnegative_number(self.cost_per_run, "cost_per_run")
        if not isinstance(self.on_demand, bool):
            raise SchemaError("INVALID_FIELD", "on_demand must be boolean")

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "pool_status", "pool_id": self.pool_id,
                "account_id": self.account_id, "billing_basis": self.billing_basis,
                "allowed_roles": list(self.allowed_roles), "allowed_projects": list(self.allowed_projects),
                "allowed_models": list(self.allowed_models), "max_concurrency": self.max_concurrency,
                "in_flight": self.in_flight, "quota_remaining": self.quota_remaining,
                "quota_period": self.quota_period, "on_demand": self.on_demand, "cost_per_run": self.cost_per_run,
                "account_quota_remaining": self.account_quota_remaining}

    @classmethod
    @_typed_boundary("pool status")
    def from_dict(cls, raw: Mapping[str, Any]) -> "PoolStatus":
        required = {"schema_version", "kind", "pool_id", "billing_basis", "allowed_roles", "allowed_projects",
                    "allowed_models", "max_concurrency", "in_flight", "quota_remaining", "quota_period",
                    "on_demand", "cost_per_run"}
        _check_keys(raw, required, {"account_id", "account_quota_remaining"}, "pool_status")
        _schema_version(raw["schema_version"], "pool status")
        if raw["kind"] != "pool_status":
            raise SchemaError("SCHEMA_VERSION", "unsupported pool status schema")
        quota = raw["quota_remaining"]
        if quota is not None:
            quota = _nonnegative_int(quota, "quota_remaining")
        period = raw["quota_period"]
        if period is not None:
            period = _string(period, "quota_period")
        if not isinstance(raw["on_demand"], bool):
            raise SchemaError("INVALID_FIELD", "on_demand must be boolean")
        account_id = raw.get("account_id")
        if account_id is not None:
            account_id = _id(account_id, "account_id")
        account_quota = raw.get("account_quota_remaining")
        if account_quota is not None:
            account_quota = _nonnegative_int(account_quota, "account_quota_remaining")
        return cls(_id(raw["pool_id"], "pool_id"), _string(raw["billing_basis"], "billing_basis"),
                   _string_list(raw["allowed_roles"], "allowed_roles"), _string_list(raw["allowed_projects"], "allowed_projects"),
                   _string_list(raw["allowed_models"], "allowed_models"), _nonnegative_int(raw["max_concurrency"], "max_concurrency"),
                   _nonnegative_int(raw["in_flight"], "in_flight"), quota, period, raw["on_demand"],
                   _nonnegative_number(raw["cost_per_run"], "cost_per_run"), account_id, account_quota)


@dataclass(frozen=True)
class RoutingPolicy:
    """Human-owned, versioned routing authority; absent policy fails closed for metered work."""

    policy_id: str
    allowed_billing_basis: tuple[str, ...]
    allow_on_demand: bool
    authority: str
    policy_digest: str

    @classmethod
    @_typed_boundary("routing policy")
    def build(cls, *, policy_id: str, allowed_billing_basis: Iterable[str], allow_on_demand: bool,
              authority: str = "human-owned") -> "RoutingPolicy":
        body = {"schema_version": SCHEMA_VERSION, "kind": "routing_policy", "policy_id": policy_id,
                "allowed_billing_basis": sorted(set(allowed_billing_basis)), "allow_on_demand": allow_on_demand,
                "authority": authority}
        body["policy_digest"] = digest_record(body)
        return cls.from_dict(body)

    @classmethod
    @_typed_boundary("routing policy")
    def from_dict(cls, raw: Mapping[str, Any]) -> "RoutingPolicy":
        required = {"schema_version", "kind", "policy_id", "allowed_billing_basis", "allow_on_demand", "authority", "policy_digest"}
        _check_keys(raw, required, set(), "routing_policy")
        _schema_version(raw["schema_version"], "routing policy")
        if raw["kind"] != "routing_policy":
            raise SchemaError("SCHEMA_VERSION", "unsupported routing policy schema")
        if not isinstance(raw["allow_on_demand"], bool):
            raise SchemaError("INVALID_FIELD", "allow_on_demand must be boolean")
        digest = _digest(raw["policy_digest"], "policy_digest")
        if digest != digest_record({key: raw[key] for key in required if key != "policy_digest"}):
            raise SchemaError("DIGEST_MISMATCH", "routing policy digest does not match immutable fields")
        return cls(_id(raw["policy_id"], "policy_id"), _string_list(raw["allowed_billing_basis"], "allowed_billing_basis"),
                   raw["allow_on_demand"], _string(raw["authority"], "authority"), digest)

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "routing_policy", "policy_id": self.policy_id,
                "allowed_billing_basis": list(self.allowed_billing_basis), "allow_on_demand": self.allow_on_demand,
                "authority": self.authority, "policy_digest": self.policy_digest}


@dataclass(frozen=True)
class PlacementRequirements:
    task_id: str
    project_id: str
    role: str
    capabilities: tuple[str, ...]
    operating_system: str | None
    sandbox_profile: str | None
    network_profile: str | None
    billing_basis: tuple[str, ...]
    max_cost_usd: float
    model: str | None
    preferred_hosts: tuple[str, ...]
    preferred_pools: tuple[str, ...]
    source_sha: str
    policy: str = "subscription-first"
    manual_candidate_id: str | None = None
    source_repository: str = "unknown-repository"
    source_branch: str = "unknown-source"
    seed_manifest_digest: str = ZERO_DIGEST
    model_parameters: Mapping[str, Any] = MappingProxyType({})
    allowed_paths: tuple[str, ...] = ()
    gate_digest: str = ZERO_DIGEST
    publication_policy: str = "verified-integration-only"

    def __post_init__(self) -> None:
        _nonnegative_number(self.max_cost_usd, "max_cost_usd")
        if not isinstance(self.model_parameters, Mapping):
            raise SchemaError("INVALID_FIELD", "model_parameters must be an object")
        parameters = _json_value(self.model_parameters, "model_parameters")
        object.__setattr__(self, "model_parameters", MappingProxyType(parameters))

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "placement_requirements", "task_id": self.task_id,
                "project_id": self.project_id, "role": self.role, "capabilities": list(self.capabilities),
                "operating_system": self.operating_system, "sandbox_profile": self.sandbox_profile,
                "network_profile": self.network_profile, "billing_basis": list(self.billing_basis),
                "max_cost_usd": self.max_cost_usd, "model": self.model, "preferred_hosts": list(self.preferred_hosts),
                "preferred_pools": list(self.preferred_pools), "source_sha": self.source_sha,
                "policy": self.policy, "manual_candidate_id": self.manual_candidate_id,
                "source_repository": self.source_repository, "source_branch": self.source_branch,
                "seed_manifest_digest": self.seed_manifest_digest, "model_parameters": dict(self.model_parameters),
                "allowed_paths": list(self.allowed_paths), "gate_digest": self.gate_digest,
                "publication_policy": self.publication_policy}

    @classmethod
    @_typed_boundary("placement requirements")
    def from_dict(cls, raw: Mapping[str, Any]) -> "PlacementRequirements":
        required = {"schema_version", "kind", "task_id", "project_id", "role", "capabilities",
                    "operating_system", "sandbox_profile", "network_profile", "billing_basis", "max_cost_usd",
                    "model", "preferred_hosts", "preferred_pools", "source_sha"}
        _check_keys(raw, required, {"policy", "manual_candidate_id", "source_repository", "source_branch", "seed_manifest_digest", "model_parameters", "allowed_paths", "gate_digest", "publication_policy"}, "placement_requirements")
        _schema_version(raw["schema_version"], "placement requirements")
        if raw["kind"] != "placement_requirements":
            raise SchemaError("SCHEMA_VERSION", "unsupported placement requirements schema")
        optional_text = {key: (None if raw[key] is None else _string(raw[key], key))
                         for key in ("operating_system", "sandbox_profile", "network_profile", "model")}
        policy = _string(raw.get("policy", "subscription-first"), "policy")
        if policy not in _PLACEMENT_POLICIES:
            raise SchemaError("UNKNOWN_POLICY", f"unsupported placement policy: {policy}")
        manual = raw.get("manual_candidate_id")
        if manual is not None:
            manual = _id(manual, "manual_candidate_id")
        source_repository = _string(raw.get("source_repository", "unknown-repository"), "source_repository")
        source_branch = _branch(raw.get("source_branch", "unknown-source"), "source_branch")
        seed_manifest_digest = _digest(raw.get("seed_manifest_digest", ZERO_DIGEST), "seed_manifest_digest")
        params = raw.get("model_parameters", {})
        if not isinstance(params, Mapping):
            raise SchemaError("INVALID_FIELD", "model_parameters must be an object")
        allowed_paths = _allowed_path_list(raw.get("allowed_paths", []), "allowed_paths")
        gate_digest = _digest(raw.get("gate_digest", ZERO_DIGEST), "gate_digest")
        publication_policy = _string(raw.get("publication_policy", "verified-integration-only"), "publication_policy")
        return cls(_id(raw["task_id"], "task_id"), _id(raw["project_id"], "project_id"),
                   _string(raw["role"], "role"), _string_list(raw["capabilities"], "capabilities"),
                   optional_text["operating_system"], optional_text["sandbox_profile"], optional_text["network_profile"],
                   _string_list(raw["billing_basis"], "billing_basis"), _nonnegative_number(raw["max_cost_usd"], "max_cost_usd"),
                   optional_text["model"], _string_list(raw["preferred_hosts"], "preferred_hosts"),
                   _string_list(raw["preferred_pools"], "preferred_pools"), _commit(raw["source_sha"], "source_sha"), policy, manual,
                   source_repository, source_branch, seed_manifest_digest, params, allowed_paths, gate_digest, publication_policy)


@dataclass(frozen=True)
class PlacementCandidate:
    candidate_id: str
    engine: str
    provider: str
    pool_id: str
    model: str
    host_id: str
    sandbox_profile: str
    network_profile: str
    capabilities: tuple[str, ...]
    operating_system: str
    billing_basis: str
    cost_per_run: float
    roles: tuple[str, ...]
    enabled: bool = True
    speed_score: float = 0.0
    reviewer_score: float = 0.0
    weight: int = 1
    required_endpoints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field in ("cost_per_run", "speed_score", "reviewer_score"):
            value = getattr(self, field)
            _nonnegative_number(value, field)
        _nonnegative_int(self.weight, "weight")
        if self.weight == 0:
            raise SchemaError("INVALID_FIELD", "weight must be positive")

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "placement_candidate", "candidate_id": self.candidate_id,
                "engine": self.engine, "provider": self.provider, "pool_id": self.pool_id, "model": self.model,
                "host_id": self.host_id, "sandbox_profile": self.sandbox_profile, "network_profile": self.network_profile,
                "capabilities": list(self.capabilities), "operating_system": self.operating_system,
                "billing_basis": self.billing_basis, "cost_per_run": self.cost_per_run, "roles": list(self.roles),
                "enabled": self.enabled, "speed_score": self.speed_score, "reviewer_score": self.reviewer_score,
                "weight": self.weight, "required_endpoints": list(self.required_endpoints)}

    @classmethod
    @_typed_boundary("placement candidate")
    def from_dict(cls, raw: Mapping[str, Any]) -> "PlacementCandidate":
        required = {"schema_version", "kind", "candidate_id", "engine", "provider", "pool_id", "model", "host_id",
                    "sandbox_profile", "network_profile", "capabilities", "operating_system", "billing_basis",
                    "cost_per_run", "roles", "enabled"}
        _check_keys(raw, required, {"speed_score", "reviewer_score", "weight", "required_endpoints"}, "placement_candidate")
        _schema_version(raw["schema_version"], "placement candidate")
        if raw["kind"] != "placement_candidate":
            raise SchemaError("SCHEMA_VERSION", "unsupported placement candidate schema")
        if not isinstance(raw["enabled"], bool):
            raise SchemaError("INVALID_FIELD", "enabled must be boolean")
        speed = _nonnegative_number(raw.get("speed_score", 0.0), "speed_score")
        reviewer = _nonnegative_number(raw.get("reviewer_score", 0.0), "reviewer_score")
        weight = _nonnegative_int(raw.get("weight", 1), "weight")
        if weight == 0:
            raise SchemaError("INVALID_FIELD", "weight must be positive")
        endpoints = _string_list(raw.get("required_endpoints", []), "required_endpoints")
        return cls(_id(raw["candidate_id"], "candidate_id"), _id(raw["engine"], "engine"), _id(raw["provider"], "provider"),
                   _id(raw["pool_id"], "pool_id"), _string(raw["model"], "model"), _id(raw["host_id"], "host_id"),
                   _string(raw["sandbox_profile"], "sandbox_profile"), _string(raw["network_profile"], "network_profile"),
                   _string_list(raw["capabilities"], "capabilities"), _string(raw["operating_system"], "operating_system"),
                   _string(raw["billing_basis"], "billing_basis"), _nonnegative_number(raw["cost_per_run"], "cost_per_run"),
                   _string_list(raw["roles"], "roles"), raw["enabled"], speed, reviewer, weight, endpoints)


@dataclass(frozen=True)
class Rejection:
    candidate_id: str
    code: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"schema_version": SCHEMA_VERSION, "kind": "placement_rejection", "candidate_id": self.candidate_id,
                "code": self.code, "reason": self.reason}


@dataclass(frozen=True)
class Assignment:
    task_id: str
    project_id: str
    source_sha: str
    engine: str
    provider: str
    capacity_pool: str
    model: str
    host: str
    sandbox_profile: str
    network_profile: str
    assignment_digest: str
    created_at: str
    account_id: str | None = None
    role: str = "unknown"
    source_repository: str = "unknown-repository"
    source_branch: str = "unknown-source"
    seed_manifest_digest: str = ZERO_DIGEST
    model_parameters: Mapping[str, Any] = MappingProxyType({})
    allowed_paths: tuple[str, ...] = ()
    gate_digest: str = ZERO_DIGEST
    publication_policy: str = "verified-integration-only"
    candidate_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.model_parameters, Mapping):
            raise SchemaError("INVALID_FIELD", "model_parameters must be an object")
        parameters = _json_value(self.model_parameters, "model_parameters")
        object.__setattr__(self, "model_parameters", MappingProxyType(parameters))

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "kind": "assignment", "task_id": self.task_id,
                "project_id": self.project_id, "source_sha": self.source_sha, "engine": self.engine,
                "provider": self.provider, "capacity_pool": self.capacity_pool, "model": self.model,
                "host": self.host, "sandbox_profile": self.sandbox_profile, "network_profile": self.network_profile,
                "assignment_digest": self.assignment_digest, "created_at": self.created_at, "account_id": self.account_id,
                "role": self.role, "source_repository": self.source_repository, "source_branch": self.source_branch,
                "seed_manifest_digest": self.seed_manifest_digest, "model_parameters": dict(self.model_parameters),
                "allowed_paths": list(self.allowed_paths), "gate_digest": self.gate_digest,
                "publication_policy": self.publication_policy, "candidate_id": self.candidate_id}

    @classmethod
    @_typed_boundary("assignment")
    def from_dict(cls, raw: Mapping[str, Any]) -> "Assignment":
        required = {"schema_version", "kind", "task_id", "project_id", "source_sha", "engine", "provider",
                    "capacity_pool", "model", "host", "sandbox_profile", "network_profile", "assignment_digest", "created_at",
                    "account_id", "role", "source_repository", "source_branch", "seed_manifest_digest", "model_parameters",
                    "allowed_paths", "gate_digest", "publication_policy", "candidate_id"}
        _check_keys(raw, required, set(), "assignment")
        _schema_version(raw["schema_version"], "assignment")
        if raw["kind"] != "assignment":
            raise SchemaError("SCHEMA_VERSION", "unsupported assignment schema")
        account_id = raw["account_id"]
        if account_id is not None:
            account_id = _id(account_id, "account_id")
        role = _string(raw["role"], "role")
        source_repository = _string(raw["source_repository"], "source_repository")
        source_branch = _branch(raw["source_branch"], "source_branch")
        seed_manifest_digest = _digest(raw["seed_manifest_digest"], "seed_manifest_digest")
        model_parameters = raw["model_parameters"]
        if not isinstance(model_parameters, Mapping):
            raise SchemaError("INVALID_FIELD", "model_parameters must be an object")
        allowed_paths = _allowed_path_list(raw["allowed_paths"], "allowed_paths")
        gate_digest = _digest(raw["gate_digest"], "gate_digest")
        publication_policy = _string(raw["publication_policy"], "publication_policy")
        candidate_id = _id(raw["candidate_id"], "candidate_id")
        assignment = cls(_id(raw["task_id"], "task_id"), _id(raw["project_id"], "project_id"), _commit(raw["source_sha"], "source_sha"),
                         _id(raw["engine"], "engine"), _id(raw["provider"], "provider"), _id(raw["capacity_pool"], "capacity_pool"),
                         _string(raw["model"], "model"), _id(raw["host"], "host"), _string(raw["sandbox_profile"], "sandbox_profile"),
                         _string(raw["network_profile"], "network_profile"), _digest(raw["assignment_digest"], "assignment_digest"),
                         _timestamp(raw["created_at"], "created_at"), account_id, role, source_repository, source_branch,
                         seed_manifest_digest, model_parameters, allowed_paths, gate_digest, publication_policy, candidate_id)
        if assignment_digest(assignment) != assignment.assignment_digest:
            raise SchemaError("DIGEST_MISMATCH", "assignment digest does not match immutable fields")
        return assignment


@_typed_boundary("assignment")
def assignment_digest(assignment: Assignment) -> str:
    if not isinstance(assignment, Assignment):
        raise SchemaError("INVALID_RECORD", "assignment digest requires an Assignment")
    body = assignment.to_dict()
    body.pop("assignment_digest", None)
    return hashlib.sha256(_canonical(body)).hexdigest()


def _revalidate_assignment(value: Assignment | Mapping[str, Any]) -> Assignment:
    """Re-enter the strict wire parser at every caller-controlled Assignment boundary."""
    return Assignment.from_dict(value.to_dict() if isinstance(value, Assignment) else value)


def _candidate_sort_key(candidate: PlacementCandidate, requirements: PlacementRequirements) -> tuple[Any, ...]:
    # Preferences are deterministic tie-breakers, never eligibility relaxations.
    policy = requirements.policy
    if policy == "manual-pin":
        return (0 if candidate.candidate_id == requirements.manual_candidate_id else 1, candidate.candidate_id)
    if policy in {"subscription-first", "local-first"}:
        preferred = "included" if policy == "subscription-first" else "local"
        return (0 if candidate.billing_basis == preferred else 1,
                0 if candidate.host_id in requirements.preferred_hosts else 1,
                0 if candidate.pool_id in requirements.preferred_pools else 1,
                candidate.cost_per_run, candidate.candidate_id)
    if policy == "fastest-eligible":
        return (0 if candidate.host_id in requirements.preferred_hosts else 1, -candidate.speed_score, candidate.candidate_id)
    if policy == "strongest-reviewer":
        return (0 if candidate.host_id in requirements.preferred_hosts else 1, -candidate.reviewer_score, candidate.candidate_id)
    if policy == "weighted-rotation":
        return (candidate.candidate_id,)
    # Cheapest is cost-first; host/pool preferences only break equal-cost ties.
    return (candidate.cost_per_run,
            0 if candidate.host_id in requirements.preferred_hosts else 1,
            0 if candidate.pool_id in requirements.preferred_pools else 1,
            candidate.candidate_id)


@dataclass(frozen=True)
class PauseGuard:
    paused: bool = False

    def assert_open(self) -> None:
        if self.paused:
            raise AdmissionError("PAUSED", "PAUSE is asserted; execution fabric mutations are halted")


@_typed_boundary("placement input")
def resolve_placement(requirements: PlacementRequirements | Mapping[str, Any],
                      candidates: Sequence[PlacementCandidate | Mapping[str, Any]],
                      hosts: Mapping[str, HostRegistration | Mapping[str, Any]],
                      heartbeats: Mapping[str, HostHeartbeat | Mapping[str, Any]],
                      pools: Mapping[str, PoolStatus | Mapping[str, Any]],
                      *, now_epoch: float | None = None, heartbeat_ttl_s: float = 120.0,
                      created_at: str | None = None,
                      paused: bool = False,
                      pause_guard: PauseGuard | None = None,
                      routing_policy: RoutingPolicy | Mapping[str, Any] | None = None,
                      reserved_host: Mapping[str, int] | None = None,
                      reserved_pool: Mapping[str, int] | None = None,
                      reserved_workload: Mapping[tuple[str, str], int] | None = None) -> tuple[Assignment | None, tuple[Rejection, ...]]:
    """Resolve one immutable assignment and a complete, deterministic rejection trace."""
    req = requirements if isinstance(requirements, PlacementRequirements) else PlacementRequirements.from_dict(requirements)
    req = PlacementRequirements.from_dict(req.to_dict())
    if pause_guard is not None:
        pause_guard.assert_open()
    if req.policy not in _PLACEMENT_POLICIES:
        raise SchemaError("UNKNOWN_POLICY", f"unsupported placement policy: {req.policy}")
    if req.policy == "manual-pin" and req.manual_candidate_id is None:
        raise SchemaError("MISSING_FIELD", "manual-pin requires manual_candidate_id")
    if routing_policy is not None and not isinstance(routing_policy, (RoutingPolicy, Mapping)):
        raise SchemaError("INVALID_FIELD", "routing_policy must be an object")
    policy = None if routing_policy is None else RoutingPolicy.from_dict(
        routing_policy.to_dict() if isinstance(routing_policy, RoutingPolicy) else routing_policy)
    if policy is not None and policy.authority != "human-owned":
        raise AdmissionError("ROUTING_POLICY_UNTRUSTED", "routing policy is not human-owned")
    try:
        ttl = _finite_number(heartbeat_ttl_s, "heartbeat_ttl_s", minimum=0)
    except SchemaError as exc:
        raise SchemaError("INVALID_FIELD", "heartbeat_ttl_s must be finite and non-negative") from exc
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes, bytearray)):
        raise SchemaError("INVALID_FIELD", "candidates must be an array")
    if not isinstance(hosts, Mapping):
        raise SchemaError("INVALID_FIELD", "hosts must be an object")
    if not isinstance(heartbeats, Mapping):
        raise SchemaError("INVALID_FIELD", "heartbeats must be an object")
    if not isinstance(pools, Mapping):
        raise SchemaError("INVALID_FIELD", "pools must be an object")
    parsed_candidates = [item if isinstance(item, PlacementCandidate) else PlacementCandidate.from_dict(item) for item in candidates]
    parsed_candidates = [PlacementCandidate.from_dict(item.to_dict()) for item in parsed_candidates]
    candidate_ids = [item.candidate_id for item in parsed_candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise SchemaError("DUPLICATE_CANDIDATE", "placement candidates must have unique candidate_id values")
    parsed_hosts = _identity_bound_mapping(hosts, "hosts", HostRegistration, "host_id", HostRegistration.from_dict)
    parsed_heartbeats = _identity_bound_mapping(heartbeats, "heartbeats", HostHeartbeat, "host_id", HostHeartbeat.from_dict)
    parsed_pools = _identity_bound_mapping(pools, "pools", PoolStatus, "pool_id", PoolStatus.from_dict)
    now = time.time() if now_epoch is None else _finite_number(now_epoch, "now_epoch")
    if created_at is None:
        if now_epoch is None:
            created_at = _now_iso()
        else:
            try:
                created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
            except _INPUT_ERRORS as exc:
                raise SchemaError("INVALID_FIELD", "now_epoch cannot be converted to a timestamp") from exc
    _timestamp(created_at, "created_at")
    host_used = _reservation_counts(reserved_host, "reserved_host")
    pool_used = _reservation_counts(reserved_pool, "reserved_pool")
    workload_used = (_reservation_counts(reserved_workload, "reserved_workload") if reserved_workload is not None
                     else {(host_id, req.role): count for host_id, count in host_used.items()})
    trace: list[Rejection] = []
    if paused:
        return None, tuple(Rejection(item.candidate_id, "PAUSED", "PAUSE is asserted; placement is halted")
                           for item in sorted(parsed_candidates, key=lambda item: _candidate_sort_key(item, req)))
    ordered = sorted(parsed_candidates, key=lambda item: _candidate_sort_key(item, req))
    eligible: list[PlacementCandidate] = []
    for candidate in ordered:
        host = parsed_hosts.get(candidate.host_id)
        pool = parsed_pools.get(candidate.pool_id)
        heartbeat = parsed_heartbeats.get(candidate.host_id)
        reason: tuple[str, str] | None = None
        if req.policy == "manual-pin" and candidate.candidate_id != req.manual_candidate_id:
            reason = ("MANUAL_PIN_MISMATCH", "candidate is outside the manual pin")
        elif not candidate.enabled:
            reason = ("DISABLED", "candidate is disabled by policy")
        elif host is None:
            reason = ("HOST_UNKNOWN", "host is not registered")
        elif pool is None:
            reason = ("POOL_UNKNOWN", "capacity pool is not registered")
        elif heartbeat is None or heartbeat.registration_digest != host.registration_digest:
            reason = ("HEARTBEAT_MISSING", "host has no heartbeat matching its registration")
        elif now - _epoch(heartbeat.observed_at) > ttl:
            reason = ("HEARTBEAT_STALE", "host heartbeat exceeded its lease TTL")
        elif not set(req.capabilities) <= set(candidate.capabilities) or not set(req.capabilities) <= set(host.capabilities):
            missing = sorted(set(req.capabilities) - (set(candidate.capabilities) & set(host.capabilities)))
            reason = ("CAPABILITY_MISSING", f"missing capabilities: {', '.join(missing)}")
        elif req.operating_system is not None and candidate.operating_system != req.operating_system:
            reason = ("OS_INCOMPATIBLE", "candidate operating system does not satisfy the task")
        elif candidate.sandbox_profile not in host.sandbox_profiles or (req.sandbox_profile and candidate.sandbox_profile != req.sandbox_profile):
            reason = ("SANDBOX_INCOMPATIBLE", "host or task does not permit the sandbox profile")
        elif candidate.network_profile not in host.network_profiles or (req.network_profile and candidate.network_profile != req.network_profile):
            reason = ("NETWORK_INCOMPATIBLE", "host or task does not permit the network profile")
        elif candidate.required_endpoints and not set(candidate.required_endpoints) <= set(host.network_endpoints.get(candidate.network_profile, ())):
            reason = ("NETWORK_ENDPOINT_MISSING", "selected network profile lacks a required endpoint")
        elif candidate.billing_basis not in req.billing_basis:
            reason = ("BILLING_NOT_ALLOWED", "candidate billing basis is outside task policy")
        elif candidate.billing_basis == "metered" and (policy is None or candidate.billing_basis not in policy.allowed_billing_basis):
            reason = ("METERED_NOT_AUTHORIZED", "metered execution requires an explicit human-owned routing policy")
        elif pool.on_demand and (policy is None or not policy.allow_on_demand):
            reason = ("ON_DEMAND_NOT_AUTHORIZED", "on-demand capacity requires explicit human-owned policy")
        elif candidate.billing_basis != pool.billing_basis:
            reason = ("POOL_BILLING_MISMATCH", "candidate billing basis does not match capacity pool")
        elif candidate.cost_per_run > req.max_cost_usd:
            reason = ("COST_EXCEEDED", "candidate cost exceeds task ceiling")
        elif req.model is not None and candidate.model != req.model:
            reason = ("MODEL_MISMATCH", "candidate model does not satisfy the task")
        elif req.role not in candidate.roles:
            reason = ("ROLE_UNSUPPORTED", "candidate does not support the requested role")
        elif req.project_id not in pool.allowed_projects and "*" not in pool.allowed_projects:
            reason = ("PROJECT_NOT_ALLOWED", "pool policy excludes this project")
        elif req.role not in pool.allowed_roles and "*" not in pool.allowed_roles:
            reason = ("ROLE_NOT_ALLOWED", "pool policy excludes this role")
        elif candidate.model not in pool.allowed_models and "*" not in pool.allowed_models:
            reason = ("MODEL_NOT_ALLOWED", "pool policy excludes this model")
        elif pool.in_flight + pool_used.get(pool.pool_id, 0) >= pool.max_concurrency:
            reason = ("POOL_CONCURRENCY_EXHAUSTED", "capacity pool concurrency is exhausted")
        elif pool.quota_remaining is not None and pool.quota_remaining <= pool_used.get(pool.pool_id, 0):
            reason = ("POOL_QUOTA_EXHAUSTED", "capacity pool quota is exhausted")
        elif pool.account_id is not None and any(item.account_id == pool.account_id and item.account_quota_remaining is not None for item in parsed_pools.values()):
            account_used = sum(pool_used.get(item.pool_id, 0) + item.in_flight
                               for item in parsed_pools.values() if item.account_id == pool.account_id)
            account_limits = [item.account_quota_remaining for item in parsed_pools.values()
                              if item.account_id == pool.account_id and item.account_quota_remaining is not None]
            if account_used >= min(account_limits):
                reason = ("ACCOUNT_QUOTA_EXHAUSTED", "shared account quota is exhausted")
        elif host_used.get(host.host_id, 0) >= host.max_concurrency:
            reason = ("HOST_CONCURRENCY_EXHAUSTED", "host concurrency is exhausted")
        elif req.role in host.workload_concurrency and workload_used.get((host.host_id, req.role), 0) + 1 > host.workload_concurrency[req.role]:
            reason = ("WORKLOAD_CONCURRENCY_EXHAUSTED", "host workload concurrency is exhausted")
        if reason is not None:
            trace.append(Rejection(candidate.candidate_id, reason[0], reason[1]))
            continue
        eligible.append(candidate)
    selected: PlacementCandidate | None = None
    if eligible:
        if req.policy == "weighted-rotation":
            # Weight only candidates that actually passed admission.  Including a
            # disabled/stale candidate in the ticket space would skew the advertised
            # distribution toward whichever eligible candidate followed it.
            eligible = sorted(eligible, key=lambda item: item.candidate_id)
            total_weight = sum(item.weight for item in eligible)
            ticket = _safe_int(hashlib.sha256(f"{req.task_id}:weighted-rotation".encode()).hexdigest(),
                               "weighted rotation ticket", base=16) % total_weight
            cursor = 0
            for candidate in eligible:
                cursor += candidate.weight
                if ticket < cursor:
                    selected = candidate
                    break
        else:
            selected = eligible[0]
    if selected is not None:
        candidate = selected
        selected_pool = parsed_pools[selected.pool_id]
        body = {"schema_version": SCHEMA_VERSION, "kind": "assignment", "task_id": req.task_id,
                "project_id": req.project_id, "source_sha": req.source_sha, "engine": candidate.engine,
                "provider": candidate.provider, "capacity_pool": candidate.pool_id, "model": candidate.model,
                "host": candidate.host_id, "sandbox_profile": candidate.sandbox_profile,
                "network_profile": candidate.network_profile, "created_at": created_at,
                "account_id": selected_pool.account_id, "role": req.role, "source_repository": req.source_repository,
                "source_branch": req.source_branch, "seed_manifest_digest": req.seed_manifest_digest,
                "model_parameters": dict(req.model_parameters), "allowed_paths": list(req.allowed_paths),
                "gate_digest": req.gate_digest, "publication_policy": req.publication_policy,
                "candidate_id": selected.candidate_id}
        digest = hashlib.sha256(_canonical(body)).hexdigest()
        assignment = Assignment(req.task_id, req.project_id, req.source_sha, candidate.engine, candidate.provider,
                                candidate.pool_id, candidate.model, candidate.host_id, candidate.sandbox_profile,
                                candidate.network_profile, digest, body["created_at"], selected_pool.account_id, req.role,
                                req.source_repository, req.source_branch, req.seed_manifest_digest, req.model_parameters,
                                req.allowed_paths, req.gate_digest, req.publication_policy, selected.candidate_id)
        return assignment, tuple(trace)
    return None, tuple(trace)


def _epoch(timestamp: str) -> float:
    # ISO records are UTC and schema-validated; preserve fractional seconds.
    try:
        return datetime.fromisoformat(timestamp[:-1] + "+00:00").timestamp()
    except _INPUT_ERRORS as exc:
        raise SchemaError("INVALID_TIMESTAMP", "timestamp is not a real UTC timestamp") from exc


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class HostRegistry:
    """Validated host registrations and monotonic heartbeat observations."""

    def __init__(self, *, now: str | None = None, future_skew_s: float = DEFAULT_HEARTBEAT_FUTURE_SKEW):
        self.hosts: dict[str, HostRegistration] = {}
        self.heartbeats: dict[str, HostHeartbeat] = {}
        self._lock = threading.RLock()
        self.now = _timestamp(now, "now") if now is not None else _now_iso()
        try:
            skew = _finite_number(future_skew_s, "future_skew_s", minimum=0)
        except SchemaError as exc:
            raise SchemaError("INVALID_FIELD", "future_skew_s must be finite and non-negative") from exc
        self.future_skew_s = skew

    @_typed_boundary("host registration")
    def register(self, registration: HostRegistration) -> str:
        with self._lock:
            if not isinstance(registration, HostRegistration):
                raise SchemaError("INVALID_RECORD", "registration must be a HostRegistration")
            registration = HostRegistration.from_dict(registration.to_dict())
            current = self.hosts.get(registration.host_id)
            if current is not None and current.registration_digest == registration.registration_digest:
                return "duplicate"
            self.hosts[registration.host_id] = registration
            # A new registration invalidates heartbeats from the previous capability set.
            self.heartbeats.pop(registration.host_id, None)
            return "registered"

    @_typed_boundary("host heartbeat")
    def heartbeat(self, value: HostHeartbeat, *, now: str | None = None) -> str:
        with self._lock:
            if not isinstance(value, HostHeartbeat):
                raise SchemaError("INVALID_RECORD", "heartbeat must be a HostHeartbeat")
            value = HostHeartbeat.from_dict(value.to_dict())
            registration = self.hosts.get(value.host_id)
            if registration is None or registration.registration_digest != value.registration_digest:
                raise AdmissionError("HEARTBEAT_UNBOUND", "heartbeat does not match a registered host")
            reference = _timestamp(now, "now") if now is not None else self.now
            if reference is not None and _epoch(value.observed_at) > _epoch(reference) + self.future_skew_s:
                raise AdmissionError("HEARTBEAT_FUTURE", "heartbeat observed time is too far in the future")
            current = self.heartbeats.get(value.host_id)
            if current is not None:
                if value.sequence < current.sequence:
                    raise AdmissionError("HEARTBEAT_OUT_OF_ORDER", "heartbeat sequence moved backwards")
                if value.lease_epoch < current.lease_epoch:
                    raise AdmissionError("LEASE_EPOCH_OUT_OF_ORDER", "heartbeat lease epoch moved backwards")
                if value.sequence == current.sequence:
                    if value.to_dict() == current.to_dict():
                        return "duplicate"
                    raise AdmissionError("HEARTBEAT_CONFLICT", "heartbeat sequence has conflicting data")
            self.heartbeats[value.host_id] = value
            return "accepted"

    def snapshot(self) -> tuple[dict[str, HostRegistration], dict[str, HostHeartbeat]]:
        with self._lock:
            return dict(self.hosts), dict(self.heartbeats)


class DurableHostRegistry(HostRegistry):
    """Restart-safe host registration/heartbeat records with digest-checked snapshots."""

    def __init__(self, path: Path | str, *, root: Path | str | None = None,
                 now: str | None = None, future_skew_s: float = DEFAULT_HEARTBEAT_FUTURE_SKEW):
        super().__init__(now=now, future_skew_s=future_skew_s)
        self.path, self.root = _safe_store_path(path, root)
        _ensure_store_directory(self.path.parent)
        self.lock_path = _safe_store_path(self.path.with_name(self.path.name + ".lock"), self.root)[0]
        self._path_identity = None
        with _journal_lock(self.lock_path):
            self._reload_durable_locked()

    def _reload_durable_locked(self) -> None:
        self.hosts.clear(); self.heartbeats.clear()
        stored = _read_store_bytes(self.path, expected_identity=self._path_identity)
        if stored is None:
            self._path_identity = None
            return
        payload, self._path_identity = stored
        try:
            state = _json_load(payload.decode("utf-8"))
        except _JsonInputError as exc:
            raise ReconciliationError("CORRUPT_REGISTRY", "host registry snapshot cannot be decoded") from exc
        except (UnicodeError, ValueError) as exc:
            raise ReconciliationError("CORRUPT_REGISTRY", "host registry snapshot cannot be decoded") from exc
        if not isinstance(state, Mapping):
            raise ReconciliationError("CORRUPT_REGISTRY", "host registry snapshot is not an object")
        required = {"schema_version", "kind", "hosts", "heartbeats", "state_digest"}
        _check_keys(state, required, set(), "host_registry")
        if type(state["schema_version"]) is not int or state["schema_version"] != SCHEMA_VERSION or state["kind"] != "host_registry":
            raise ReconciliationError("SCHEMA_VERSION", "unsupported host registry snapshot")
        if state["state_digest"] != digest_record({key: state[key] for key in required if key != "state_digest"}):
            raise ReconciliationError("DIGEST_MISMATCH", "host registry snapshot digest is invalid")
        if not isinstance(state["hosts"], list) or not isinstance(state["heartbeats"], list):
            raise ReconciliationError("CORRUPT_REGISTRY", "host registry collections are malformed")
        for raw in state["hosts"]:
            item = HostRegistration.from_dict(raw)
            if item.host_id in self.hosts:
                raise ReconciliationError("CONFLICTING_REPLAY", "duplicate host registration")
            self.hosts[item.host_id] = item
        for raw in state["heartbeats"]:
            item = HostHeartbeat.from_dict(raw)
            if item.host_id not in self.hosts or self.hosts[item.host_id].registration_digest != item.registration_digest:
                raise ReconciliationError("HEARTBEAT_UNBOUND", "persisted heartbeat is not registration-bound")
            if item.host_id in self.heartbeats:
                raise ReconciliationError("CONFLICTING_REPLAY", "duplicate host heartbeat")
            self.heartbeats[item.host_id] = item

    def _persist_locked(self) -> None:
        body = {"schema_version": SCHEMA_VERSION, "kind": "host_registry",
                "hosts": [item.to_dict() for _, item in sorted(self.hosts.items())],
                "heartbeats": [item.to_dict() for _, item in sorted(self.heartbeats.items())]}
        body["state_digest"] = digest_record(body)
        self._path_identity = _replace_store_bytes(self.path, _canonical(body), expected_identity=self._path_identity)

    @_typed_boundary("durable host registration")
    def register(self, registration: HostRegistration) -> str:
        with _journal_lock(self.lock_path):
            self._reload_durable_locked(); result = super().register(registration); self._persist_locked(); return result

    @_typed_boundary("durable host heartbeat")
    def heartbeat(self, value: HostHeartbeat, *, now: str | None = None) -> str:
        with _journal_lock(self.lock_path):
            self._reload_durable_locked(); result = super().heartbeat(value, now=now); self._persist_locked(); return result


class PlacementGovernor:
    """Atomic in-process host/pool admission around the pure resolver.

    Reservations are intentionally ephemeral.  A later durable lease adapter must persist the
    reservation and release it only after terminal reconciliation; this class never dispatches work.
    """

    def __init__(self, registry: HostRegistry, pools: Mapping[str, PoolStatus], *, pause_guard: PauseGuard | None = None):
        self.registry = registry
        self.pools = dict(pools)
        self.pause_guard = pause_guard
        self._active: dict[str, Assignment] = {}
        self._lock = threading.RLock()

    @_typed_boundary("governed placement input")
    def place(self, requirements: PlacementRequirements, candidates: Sequence[PlacementCandidate],
              *, now_epoch: float | None = None, created_at: str | None = None) -> tuple[Assignment | None, tuple[Rejection, ...]]:
        if self.pause_guard is not None:
            self.pause_guard.assert_open()
        with self._lock:
            host_reserved: dict[str, int] = {}
            pool_reserved: dict[str, int] = {}
            workload_reserved: dict[tuple[str, str], int] = {}
            for active in self._active.values():
                host_reserved[active.host] = host_reserved.get(active.host, 0) + 1
                pool_reserved[active.capacity_pool] = pool_reserved.get(active.capacity_pool, 0) + 1
                workload_reserved[(active.host, active.role)] = workload_reserved.get((active.host, active.role), 0) + 1
            hosts, heartbeats = self.registry.snapshot()
            assignment, trace = resolve_placement(requirements, candidates, hosts, heartbeats, self.pools,
                                                  now_epoch=now_epoch, created_at=created_at,
                                                  reserved_host=host_reserved, reserved_pool=pool_reserved,
                                                  reserved_workload=workload_reserved)
            if assignment is not None:
                self._active[assignment.assignment_digest] = assignment
            return assignment, trace

    def release(self, assignment: Assignment | Mapping[str, Any]) -> str:
        assignment = _revalidate_assignment(assignment)
        with self._lock:
            digest = assignment.assignment_digest
            if digest not in self._active:
                return "duplicate"
            del self._active[digest]
            return "released"

    @property
    def active(self) -> tuple[Assignment, ...]:
        with self._lock:
            return tuple(self._active[key] for key in sorted(self._active))


class DurableFabricStore:
    """Crash-safe append-only lease/attempt/result journal with strict replay.

    Each mutation holds a process/thread lock, reloads the journal, and appends one chained event.
    This makes placement plus lease reservation an atomic admission transaction for cooperating
    controller processes.  No adapter or remote call is made here.
    """

    def __init__(self, path: Path | str, *, root: Path | str | None = None):
        self.path, self.root = _safe_store_path(path, root)
        _ensure_store_directory(self.path.parent)
        self.lock_path = _safe_store_path(self.path.with_name(self.path.name + ".lock"), self.root)[0]
        self.leases: dict[str, dict[str, Any]] = {}
        self.attempts: dict[str, dict[str, Any]] = {}
        self.results: dict[str, dict[str, Any]] = {}
        self._tail_digest = ZERO_DIGEST
        self._path_identity = None
        with _journal_lock(self.lock_path):
            self._reload_locked()

    def _reload_locked(self) -> None:
        self.leases.clear(); self.attempts.clear(); self.results.clear(); self._tail_digest = ZERO_DIGEST
        stored = _read_store_bytes(self.path, expected_identity=self._path_identity)
        if stored is None:
            self._path_identity = None
            return
        payload, self._path_identity = stored
        try:
            lines = payload.decode("utf-8").splitlines()
        except UnicodeError as exc:
            raise ReconciliationError("CORRUPT_JOURNAL", "journal cannot be decoded safely") from exc
        for number, line in enumerate(lines, 1):
            try:
                event = _json_load(line)
                if not isinstance(event, dict):
                    raise ValueError("event is not an object")
                self._validate_event(event)
                self._apply(event)
                self._tail_digest = event["event_digest"]
            except _JsonInputError as exc:
                raise ReconciliationError("CORRUPT_JOURNAL", f"invalid fabric journal event at line {number}") from exc
            except FabricError:
                raise
            except (ValueError, TypeError, KeyError, UnicodeError) as exc:
                raise ReconciliationError("CORRUPT_JOURNAL", f"invalid fabric journal event at line {number}") from exc

    def _validate_event(self, event: Mapping[str, Any]) -> None:
        kind = event.get("event")
        common = {"event", "schema_version", "event_digest", "prev_event_digest"}
        if type(event.get("schema_version")) is not int or event.get("schema_version") != SCHEMA_VERSION:
            raise ReconciliationError("SCHEMA_VERSION", "unsupported fabric journal event schema")
        if not isinstance(kind, str):
            raise ReconciliationError("INVALID_EVENT", "journal event kind is missing")
        _digest(event.get("event_digest"), "event_digest")
        previous = _digest(event.get("prev_event_digest"), "prev_event_digest")
        if previous != self._tail_digest:
            raise ReconciliationError("JOURNAL_CHAIN", "journal event chain is broken")
        body = {key: value for key, value in event.items() if key != "event_digest"}
        if hashlib.sha256(_canonical(body)).hexdigest() != event["event_digest"]:
            raise ReconciliationError("DIGEST_MISMATCH", "journal event digest is invalid")
        if kind == "lease":
            expected = common | {"lease_id", "attempt_id", "remote_session_id", "assignment_digest", "assignment", "status", "created_at", "updated_at", "expires_at", "reservation", "recovery_state"}
            _check_keys(event, expected, set(), "lease_event")
            _id(event["lease_id"], "lease_id"); _id(event["attempt_id"], "attempt_id"); _id(event["remote_session_id"], "remote_session_id")
            assignment = Assignment.from_dict(event["assignment"])
            if assignment.assignment_digest != event["assignment_digest"]:
                raise ReconciliationError("ASSIGNMENT_MISMATCH", "lease assignment digest does not match assignment")
            _digest(event["assignment_digest"], "assignment_digest")
            _timestamp(event["created_at"], "created_at"); _timestamp(event["updated_at"], "updated_at"); _timestamp(event["expires_at"], "expires_at")
            if (_epoch(event["updated_at"]) < _epoch(event["created_at"]) or
                    _epoch(event["expires_at"]) <= _epoch(event["created_at"]) or
                    _epoch(event["updated_at"]) >= _epoch(event["expires_at"] )):
                raise ReconciliationError("INVALID_TRANSITION", "lease expiry must follow creation")
            if event["status"] != "active" or event["recovery_state"] != "none":
                raise ReconciliationError("INVALID_TRANSITION", "new leases must be active with no recovery state")
            reservation = event["reservation"]
            if not isinstance(reservation, Mapping) or set(reservation) != {"host", "pool", "role"}:
                raise ReconciliationError("INVALID_EVENT", "lease reservation is malformed")
            _id(reservation["host"], "reservation.host"); _id(reservation["pool"], "reservation.pool"); _string(reservation["role"], "reservation.role")
            if reservation["host"] != assignment.host or reservation["pool"] != assignment.capacity_pool or reservation["role"] != assignment.role:
                raise ReconciliationError("ASSIGNMENT_MISMATCH", "lease reservation is not bound to the assignment")
        elif kind == "lease_status":
            expected = common | {"lease_id", "status", "updated_at", "observed_at", "recovery_state"}
            _check_keys(event, expected, set(), "lease_status_event")
            _id(event["lease_id"], "lease_id"); _timestamp(event["updated_at"], "updated_at"); _timestamp(event["observed_at"], "observed_at")
            if event["status"] not in {"recovery_required", "expired", "succeeded", "failed", "cancelled"}:
                raise ReconciliationError("INVALID_TRANSITION", "invalid lease status")
            if event["recovery_state"] not in {"query_pending", "query_running", "query_unknown", "query_terminal", "none"}:
                raise ReconciliationError("INVALID_TRANSITION", "invalid lease recovery state")
        elif kind == "result":
            expected = common | {"attempt_id", "lease_id", "assignment_digest", "result_digest", "status", "observed_at"}
            _check_keys(event, expected, set(), "result_event")
            _id(event["attempt_id"], "attempt_id"); _id(event["lease_id"], "lease_id")
            _digest(event["assignment_digest"], "assignment_digest"); _digest(event["result_digest"], "result_digest")
            _timestamp(event["observed_at"], "observed_at")
            if event["status"] not in {"succeeded", "failed", "cancelled"}:
                raise ReconciliationError("INVALID_RESULT_STATUS", "result status is not terminal")
        else:
            raise ReconciliationError("UNKNOWN_EVENT", f"unknown fabric event: {kind}")

    def _append(self, event: Mapping[str, Any]) -> None:
        data = _json_line(event, "fabric journal event")
        _ensure_store_directory(self.path.parent)
        self._path_identity = _append_bytes(self.path, data, expected_identity=self._path_identity)

    def _record_locked(self, event: Mapping[str, Any]) -> dict[str, Any]:
        body = dict(event)
        body["schema_version"] = SCHEMA_VERSION
        body["prev_event_digest"] = self._tail_digest
        body["event_digest"] = hashlib.sha256(_canonical(body)).hexdigest()
        self._validate_event(body)
        leases, attempts, results = self.leases, self.attempts, self.results
        self.leases = copy.deepcopy(leases); self.attempts = copy.deepcopy(attempts); self.results = copy.deepcopy(results)
        try:
            self._apply(body)
        finally:
            self.leases, self.attempts, self.results = leases, attempts, results
        self._append(body)
        self._apply(body)
        self._tail_digest = body["event_digest"]
        return body

    def _apply(self, event: Mapping[str, Any]) -> None:
        kind = event["event"]
        if kind == "lease":
            previous = self.leases.get(event["lease_id"])
            if previous is not None and previous != dict(event):
                raise ReconciliationError("CONFLICTING_REPLAY", "lease identity has conflicting replay data")
            old_attempt = self.attempts.get(event["attempt_id"])
            if old_attempt is not None and old_attempt.get("lease_id") != event["lease_id"]:
                raise ReconciliationError("CONFLICTING_REPLAY", "attempt identity is bound to another lease")
            self.leases[event["lease_id"]] = dict(event)
            self.attempts.setdefault(event["attempt_id"], {"event": "attempt", "schema_version": SCHEMA_VERSION,
                                                             "attempt_id": event["attempt_id"], "lease_id": event["lease_id"],
                                                             "assignment_digest": event["assignment_digest"],
                                                             "status": "active", "created_at": event["created_at"]})
        elif kind == "attempt":
            previous = self.attempts.get(event["attempt_id"])
            if previous is not None and previous != dict(event):
                raise ReconciliationError("CONFLICTING_REPLAY", "attempt identity has conflicting replay data")
            self.attempts[event["attempt_id"]] = dict(event)
        elif kind == "result":
            previous = self.results.get(event["attempt_id"])
            if previous is not None and previous != dict(event):
                raise ReconciliationError("CONFLICTING_REPLAY", "result identity has conflicting replay data")
            lease = self.leases.get(event["lease_id"])
            attempt = self.attempts.get(event["attempt_id"])
            if lease is None or attempt is None or attempt.get("lease_id") != event["lease_id"]:
                raise ReconciliationError("UNKNOWN_ATTEMPT", "result references no durable attempt")
            if attempt.get("assignment_digest") != event["assignment_digest"] or lease.get("assignment_digest") != event["assignment_digest"]:
                raise ReconciliationError("ASSIGNMENT_MISMATCH", "result assignment differs from the lease")
            if lease["status"] not in {"active", "recovery_required"} and previous is None:
                raise ReconciliationError("INVALID_TRANSITION", "result cannot transition a terminal lease")
            self.results[event["attempt_id"]] = dict(event)
            self.leases[event["lease_id"]]["status"] = event["status"]
            self.leases[event["lease_id"]]["recovery_state"] = "none"
            self.attempts[event["attempt_id"]]["status"] = event["status"]
        elif kind == "lease_status":
            lease = self.leases.get(event["lease_id"])
            if lease is None:
                raise ReconciliationError("UNKNOWN_LEASE", "lease status references no lease")
            current = lease["status"]
            allowed = {"active": {"recovery_required", "expired"}, "recovery_required": {"recovery_required", "expired", "succeeded", "failed", "cancelled"},
                       "expired": set(), "succeeded": set(), "failed": set(), "cancelled": set()}
            if event["status"] not in allowed[current]:
                raise ReconciliationError("INVALID_TRANSITION", f"cannot move lease {current} to {event['status']}")
            if event["status"] in {"succeeded", "failed", "cancelled"}:
                attempt_id = lease["attempt_id"]
                result = self.results.get(attempt_id)
                if result is None or result.get("lease_id") != event["lease_id"] or result.get("status") != event["status"]:
                    raise ReconciliationError("EVIDENCE_REQUIRED", "terminal recovery requires a durable result event")
            if _epoch(event["updated_at"]) < _epoch(lease["updated_at"]):
                raise ReconciliationError("INVALID_TRANSITION", "lease status timestamp moved backwards")
            if current == "recovery_required" and event["status"] == "recovery_required":
                states = {"none": {"query_pending", "none"}, "query_pending": {"query_pending", "query_running", "query_unknown", "query_terminal"},
                          "query_running": {"query_running", "query_unknown", "query_terminal"},
                          "query_unknown": {"query_unknown", "query_running", "query_terminal"},
                          "query_terminal": {"query_terminal"}}
                if event["recovery_state"] not in states.get(lease["recovery_state"], set()):
                    raise ReconciliationError("INVALID_TRANSITION", "recovery query state moved backwards")
            lease["status"] = event["status"]
            lease["recovery_state"] = event["recovery_state"]
            lease["updated_at"] = event["updated_at"]
        else:
            raise ReconciliationError("UNKNOWN_EVENT", f"unknown fabric event: {kind}")

    def _create_lease_locked(self, assignment: Assignment | Mapping[str, Any], *, lease_id: str, attempt_id: str,
                             remote_session_id: str, now: str, expires_at: str, role: str = "unknown") -> dict[str, Any]:
        assignment = _revalidate_assignment(assignment)
        _id(lease_id, "lease_id"); _id(attempt_id, "attempt_id"); _id(remote_session_id, "remote_session_id")
        _timestamp(now, "now"); _timestamp(expires_at, "expires_at")
        if _epoch(expires_at) <= _epoch(now):
            raise AdmissionError("INVALID_LEASE", "lease expiry must be after lease creation")
        if role == "unknown":
            role = assignment.role
        if lease_id in self.leases:
            existing = self.leases[lease_id]
            if existing["attempt_id"] == attempt_id and existing["remote_session_id"] == remote_session_id and existing["assignment_digest"] == assignment.assignment_digest:
                return dict(existing)
            raise AdmissionError("DUPLICATE_LEASE", "lease identity has conflicting fields")
        if attempt_id in self.attempts:
            raise AdmissionError("DUPLICATE_ATTEMPT", "attempt identity already exists")
        if any(item.get("remote_session_id") == remote_session_id for item in self.leases.values()):
            raise AdmissionError("DUPLICATE_REMOTE_SESSION", "remote session identity already exists")
        for item in self.leases.values():
            if item["status"] in {"active", "recovery_required"} and item["assignment"].get("task_id") == assignment.task_id:
                raise AdmissionError("DUPLICATE_TASK_LEASE", "task already has an active lease")
        event = {"event": "lease", "lease_id": lease_id, "attempt_id": attempt_id,
                 "remote_session_id": remote_session_id, "assignment_digest": assignment.assignment_digest,
                 "assignment": assignment.to_dict(), "status": "active", "created_at": now,
                 "updated_at": now, "expires_at": expires_at,
                "reservation": {"host": assignment.host, "pool": assignment.capacity_pool,
                                  "role": role}, "recovery_state": "none"}
        return self._record_locked(event)

    @_typed_boundary("lease input")
    def create_lease(self, assignment: Assignment | Mapping[str, Any], *, lease_id: str, attempt_id: str, remote_session_id: str,
                     now: str, expires_at: str, role: str = "unknown", paused: bool = False,
                     pause_guard: PauseGuard | None = None) -> dict[str, Any]:
        if paused:
            raise AdmissionError("PAUSED", "PAUSE is asserted; lease admission is halted")
        if pause_guard is not None:
            pause_guard.assert_open()
        assignment = _revalidate_assignment(assignment)
        with _journal_lock(self.lock_path):
            if paused:
                raise AdmissionError("PAUSED", "PAUSE is asserted; lease admission is halted")
            if pause_guard is not None:
                pause_guard.assert_open()
            self._reload_locked()
            return self._create_lease_locked(assignment, lease_id=lease_id, attempt_id=attempt_id,
                                             remote_session_id=remote_session_id, now=now, expires_at=expires_at, role=role)

    @_typed_boundary("placement admission")
    def admit_placement(self, requirements: PlacementRequirements | Mapping[str, Any],
                        candidates: Sequence[PlacementCandidate | Mapping[str, Any]],
                        hosts: Mapping[str, HostRegistration | Mapping[str, Any]],
                        heartbeats: Mapping[str, HostHeartbeat | Mapping[str, Any]],
                        pools: Mapping[str, PoolStatus | Mapping[str, Any]], *, lease_id: str,
                        attempt_id: str, remote_session_id: str, now: str, expires_at: str,
                        heartbeat_ttl_s: float = 120.0, paused: bool = False,
                        pause_guard: PauseGuard | None = None,
                        routing_policy: RoutingPolicy | Mapping[str, Any] | None = None) -> tuple[Assignment | None, tuple[Rejection, ...]]:
        """Atomically resolve placement, reserve capacity, and create its durable lease."""
        if paused:
            raise AdmissionError("PAUSED", "PAUSE is asserted; lease admission is halted")
        if pause_guard is not None:
            pause_guard.assert_open()
        with _journal_lock(self.lock_path):
            if paused:
                raise AdmissionError("PAUSED", "PAUSE is asserted; lease admission is halted")
            if pause_guard is not None:
                pause_guard.assert_open()
            self._reload_locked()
            req = requirements if isinstance(requirements, PlacementRequirements) else PlacementRequirements.from_dict(requirements)
            for existing in self.leases.values():
                if existing["status"] in {"active", "recovery_required"} and existing["assignment"].get("task_id") == req.task_id:
                    if existing["assignment"].get("source_sha") == req.source_sha:
                        if (existing["lease_id"], existing["attempt_id"], existing["remote_session_id"]) != (lease_id, attempt_id, remote_session_id):
                            raise AdmissionError("DUPLICATE_LEASE", "task/source identity is already bound to another lease session")
                        return Assignment.from_dict(existing["assignment"]), ()
                    raise AdmissionError("DUPLICATE_TASK_LEASE", "task already has an active lease")
            host_reserved: dict[str, int] = {}; pool_reserved: dict[str, int] = {}
            workload_reserved: dict[tuple[str, str], int] = {}
            for lease in self.leases.values():
                if lease["status"] in {"active", "recovery_required"}:
                    host_reserved[lease["reservation"]["host"]] = host_reserved.get(lease["reservation"]["host"], 0) + 1
                    pool_reserved[lease["reservation"]["pool"]] = pool_reserved.get(lease["reservation"]["pool"], 0) + 1
                    key = (lease["reservation"]["host"], lease["reservation"]["role"])
                    workload_reserved[key] = workload_reserved.get(key, 0) + 1
            assignment, trace = resolve_placement(req, candidates, hosts, heartbeats, pools,
                                                  now_epoch=_epoch(now), created_at=now,
                                                  heartbeat_ttl_s=heartbeat_ttl_s,
                                                  paused=paused,
                                                  reserved_host=host_reserved, reserved_pool=pool_reserved,
                                                  reserved_workload=workload_reserved,
                                                  routing_policy=routing_policy, pause_guard=pause_guard)
            if assignment is None:
                return None, trace
            self._create_lease_locked(assignment, lease_id=lease_id, attempt_id=attempt_id,
                                      remote_session_id=remote_session_id, now=now, expires_at=expires_at,
                                      role=req.role)
            return assignment, trace

    def active_reservations(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(lease["reservation"], lease_id=lease_id)
                     for lease_id, lease in sorted(self.leases.items())
                     if lease["status"] in {"active", "recovery_required"})

    @_typed_boundary("restart reconciliation")
    def reconcile_restart(self, *, now: str) -> tuple[dict[str, Any], ...]:
        """Mark active leases as recovery-required exactly once; never relaunch remotely."""
        _timestamp(now, "now")
        with _journal_lock(self.lock_path):
            self._reload_locked()
            # Expiration wins over restart recovery.  Never turn an already
            # expired lease back into a capacity reservation.
            self._expire_due_locked(now)
            recovered: list[dict[str, Any]] = []
            for lease_id, lease in sorted(self.leases.items()):
                if lease["status"] != "active":
                    continue
                event = {"event": "lease_status", "lease_id": lease_id,
                         "status": "recovery_required", "updated_at": now, "observed_at": now,
                         "recovery_state": "query_pending"}
                self._record_locked(event)
                recovered.append(dict(self.leases[lease_id]))
            return tuple(recovered)

    @_typed_boundary("lease expiry")
    def expire(self, *, now: str) -> tuple[str, ...]:
        _timestamp(now, "now")
        with _journal_lock(self.lock_path):
            self._reload_locked()
            return self._expire_due_locked(now)

    def _expire_due_locked(self, now: str) -> tuple[str, ...]:
        expired: list[str] = []
        current = _epoch(now)
        for lease_id, lease in sorted(self.leases.items()):
            if lease["status"] in {"active", "recovery_required"} and current >= _epoch(lease["expires_at"]):
                event = {"event": "lease_status", "lease_id": lease_id,
                         "status": "expired", "updated_at": now, "observed_at": now, "recovery_state": "none"}
                self._record_locked(event); expired.append(lease_id)
        return tuple(expired)

    @_typed_boundary("recovery observation")
    def record_recovery_query(self, lease_id: str, *, state: str, observed_at: str,
                              terminal_status: str | None = None, result_digest: str | None = None,
                              controller_now: str) -> str:
        _id(lease_id, "lease_id"); _timestamp(observed_at, "observed_at")
        _timestamp(controller_now, "controller_now")
        if _epoch(observed_at) > _epoch(controller_now) + DEFAULT_HEARTBEAT_FUTURE_SKEW:
            raise ReconciliationError("OBSERVATION_FUTURE", "remote recovery observation is too far in the future")
        if state not in {"running", "terminal", "unknown"}:
            raise ReconciliationError("INVALID_RECOVERY_STATE", "unsupported remote recovery state")
        if state == "terminal" and terminal_status not in {"succeeded", "failed", "cancelled"}:
            raise ReconciliationError("INVALID_RECOVERY_STATE", "terminal recovery requires a terminal result status")
        if state == "terminal" and result_digest is None:
            raise ReconciliationError("EVIDENCE_REQUIRED", "terminal recovery requires a durable result digest")
        if result_digest is not None:
            _digest(result_digest, "result_digest")
        with _journal_lock(self.lock_path):
            self._reload_locked()
            lease = self.leases.get(lease_id)
            if lease is None:
                raise ReconciliationError("UNKNOWN_LEASE", "recovery query references no lease")
            # A remote observation cannot revive an expired lease or keep its
            # reservation active.  Use trusted controller time for this check
            # on every recovery state, including running and unknown.
            if _epoch(controller_now) >= _epoch(lease["expires_at"]):
                self._expire_due_locked(controller_now)
                raise ReconciliationError("LATE_RESULT", "recovery observation arrived at or after lease expiry")
            recovery_state = {"running": "query_running", "terminal": "query_terminal", "unknown": "query_unknown"}[state]
            if lease["status"] != "recovery_required":
                return "duplicate" if lease["recovery_state"] == recovery_state else "ignored"
            current = _epoch(controller_now)
            if current < _epoch(lease["created_at"]):
                raise ReconciliationError("INVALID_CONTROLLER_TIME", "trusted controller time predates lease creation")
            if current < _epoch(lease["updated_at"]):
                raise ReconciliationError("INVALID_CONTROLLER_TIME", "trusted controller time moves lease lifecycle backwards")
            if state == "terminal":
                if current >= _epoch(lease["expires_at"]):
                    self._expire_due_locked(controller_now)
                    raise ReconciliationError("LATE_RESULT", "recovered result arrived at or after lease expiry")
                self._record_locked({"event": "result", "attempt_id": lease["attempt_id"], "lease_id": lease_id,
                                     "assignment_digest": lease["assignment_digest"], "result_digest": result_digest,
                                     "status": terminal_status, "observed_at": observed_at})
                return "recorded"
            self._record_locked({"event": "lease_status", "lease_id": lease_id,
                                 "status": terminal_status if state == "terminal" else "recovery_required",
                                 "updated_at": controller_now, "observed_at": observed_at,
                                 "recovery_state": recovery_state if state != "terminal" else "none"})
            return "recorded"

    @_typed_boundary("result input")
    def accept_result(self, *, attempt_id: str, lease_id: str, assignment_digest_value: str,
                      result_digest: str, status: str, observed_at: str, controller_now: str) -> str:
        _id(attempt_id, "attempt_id"); _id(lease_id, "lease_id"); _digest(assignment_digest_value, "assignment_digest")
        _digest(result_digest, "result_digest"); _timestamp(observed_at, "observed_at")
        if status not in {"succeeded", "failed", "cancelled"}:
            raise ReconciliationError("INVALID_RESULT_STATUS", "result status is not terminal")
        _timestamp(controller_now, "controller_now")
        with _journal_lock(self.lock_path):
            self._reload_locked()
            existing = self.results.get(attempt_id)
            if existing is not None:
                identity = (existing["lease_id"], existing["assignment_digest"], existing["result_digest"], existing["status"])
                proposed = (lease_id, assignment_digest_value, result_digest, status)
                if identity == proposed:
                    return "duplicate"
                raise ReconciliationError("CONFLICTING_RESULT", "attempt already has a different result identity")
            attempt = self.attempts.get(attempt_id); lease = self.leases.get(lease_id)
            if attempt is None or lease is None or attempt.get("lease_id") != lease_id:
                raise ReconciliationError("UNKNOWN_ATTEMPT", "result does not match a durable attempt")
            if assignment_digest_value != attempt["assignment_digest"]:
                raise ReconciliationError("ASSIGNMENT_MISMATCH", "result assignment does not match the attempt")
            if lease["status"] not in {"active", "recovery_required"}:
                raise ReconciliationError("LATE_RESULT", "result arrived after the lease was terminal")
            if _epoch(controller_now) < _epoch(lease["created_at"]):
                raise ReconciliationError("INVALID_CONTROLLER_TIME", "trusted controller time predates lease creation")
            if _epoch(controller_now) < _epoch(lease["updated_at"]):
                raise ReconciliationError("INVALID_CONTROLLER_TIME", "trusted controller time moves lease lifecycle backwards")
            if _epoch(controller_now) >= _epoch(lease["expires_at"]):
                self._expire_due_locked(controller_now)
                raise ReconciliationError("LATE_RESULT", "result arrived at or after lease expiry")
            event = {"event": "result", "attempt_id": attempt_id, "lease_id": lease_id,
                     "assignment_digest": assignment_digest_value, "result_digest": result_digest,
                     "status": status, "observed_at": observed_at}
            self._record_locked(event)
            return "accepted"


@dataclass(frozen=True)
class VerificationReceipt:
    """Controller-owned independent verification evidence; workers cannot self-assert this."""

    receipt_id: str
    assignment_digest: str
    source_sha: str
    candidate_id: str
    result_commit: str
    diff_digest: str
    scope_digest: str
    gate_digest: str
    verifier_identity: str
    verified_at: str
    verification_status: str
    receipt_digest: str
    authentication_tag: str = ""

    @classmethod
    @_typed_boundary("verification receipt")
    def build(cls, *, receipt_id: str, assignment_digest: str, source_sha: str, candidate_id: str,
              result_commit: str, diff_digest: str, scope_digest: str, gate_digest: str,
              verifier_identity: str, verified_at: str, verification_status: str = "pass") -> "VerificationReceipt":
        body = {"schema_version": SCHEMA_VERSION, "kind": "verification_receipt", "receipt_id": receipt_id,
                "assignment_digest": assignment_digest, "source_sha": source_sha, "candidate_id": candidate_id,
                "result_commit": result_commit, "diff_digest": diff_digest, "scope_digest": scope_digest,
                "gate_digest": gate_digest, "verifier_identity": verifier_identity, "verified_at": verified_at,
                "verification_status": verification_status}
        body["receipt_digest"] = digest_record(body)
        return cls.from_dict(body)

    @classmethod
    @_typed_boundary("verification receipt")
    def from_dict(cls, raw: Mapping[str, Any]) -> "VerificationReceipt":
        required = {"schema_version", "kind", "receipt_id", "assignment_digest", "source_sha", "candidate_id", "result_commit", "diff_digest", "scope_digest", "gate_digest", "verifier_identity", "verified_at", "verification_status", "receipt_digest"}
        _check_keys(raw, required, {"authentication_tag"}, "verification_receipt")
        _schema_version(raw["schema_version"], "verification receipt")
        if raw["kind"] != "verification_receipt":
            raise SchemaError("SCHEMA_VERSION", "unsupported verification receipt schema")
        digest = _digest(raw["receipt_digest"], "receipt_digest")
        if digest != digest_record({key: raw[key] for key in required if key != "receipt_digest"}):
            raise SchemaError("DIGEST_MISMATCH", "verification receipt digest is invalid")
        if raw["verification_status"] != "pass":
            raise ReconciliationError("VERIFIER_REQUIRED", "verification receipt is not a passing receipt")
        authentication_tag = raw.get("authentication_tag", "")
        if "authentication_tag" in raw and not authentication_tag:
            raise SchemaError("INVALID_FIELD", "authentication_tag cannot be empty when present")
        if authentication_tag and _regex_fullmatch(_SHA256, authentication_tag, "authentication_tag") is None:
            raise SchemaError("INVALID_FIELD", "authentication_tag must be a SHA-256 digest")
        verifier_identity = _string(raw["verifier_identity"], "verifier_identity")
        if _regex_fullmatch(_VERIFIER_IDENTITY, verifier_identity, "verifier_identity") is None:
            raise ReconciliationError("VERIFIER_UNTRUSTED", "verification identity is not controller-owned")
        return cls(_id(raw["receipt_id"], "receipt_id"), _digest(raw["assignment_digest"], "assignment_digest"),
                   _commit(raw["source_sha"], "source_sha"), _id(raw["candidate_id"], "candidate_id"),
                   _commit(raw["result_commit"], "result_commit"), _digest(raw["diff_digest"], "diff_digest"),
                   _digest(raw["scope_digest"], "scope_digest"), _digest(raw["gate_digest"], "gate_digest"),
                   verifier_identity, _timestamp(raw["verified_at"], "verified_at"),
                   "pass", digest, authentication_tag)

    def to_dict(self) -> dict[str, Any]:
        result = {"schema_version": SCHEMA_VERSION, "kind": "verification_receipt", "receipt_id": self.receipt_id,
                "assignment_digest": self.assignment_digest, "source_sha": self.source_sha, "candidate_id": self.candidate_id,
                "result_commit": self.result_commit, "diff_digest": self.diff_digest, "scope_digest": self.scope_digest,
                "gate_digest": self.gate_digest, "verifier_identity": self.verifier_identity, "verified_at": self.verified_at,
                "verification_status": self.verification_status, "receipt_digest": self.receipt_digest}
        if self.authentication_tag:
            result["authentication_tag"] = self.authentication_tag
        return result


class VerificationKeyRegistry:
    """Authenticated controller-owned verifier key registry.

    Receipt stores deliberately cannot bootstrap trust from a caller-supplied
    mapping.  A controller provisions this registry once with a protected
    authority key, and subsequent rotation rewrites the authenticated state.
    """

    def __init__(self, path: Path | str, *, authority_key_path: Path | str | None = None,
                 root: Path | str | None = None):
        self.path, self.root = _safe_store_path(path, root)
        authority = Path(authority_key_path) if authority_key_path is not None else self.path.with_suffix(".authority")
        self.authority_key_path, _ = _safe_store_path(authority, self.root)
        self.lock_path, _ = _safe_store_path(self.path.with_name(self.path.name + ".lock"), self.root)
        self._keys: Mapping[str, bytes] = MappingProxyType({})
        self._retired_keys: Mapping[str, tuple[bytes, ...]] = MappingProxyType({})
        self._epoch = 0
        self._path_identity = None
        with _journal_lock(self.lock_path):
            self._reload_locked()

    @staticmethod
    def _private_file(path: Path, field: str) -> None:
        if _file_is_reparse_or_symlink(path):
            raise SchemaError("UNSAFE_REGISTRY_PATH", f"{field} is a symlink or reparse point")
        try:
            info = path.lstat()
        except OSError as exc:
            raise SchemaError("CONTROLLER_AUTH_REQUIRED", f"{field} is not available") from exc
        if not stat.S_ISREG(info.st_mode):
            raise SchemaError("INVALID_FIELD", f"{field} must be a regular file")
        if getattr(info, "st_nlink", 1) != 1:
            raise SchemaError("UNSAFE_REGISTRY_PATH", f"{field} has unexpected hard links")
        # POSIX deployments must keep controller material owner-only.  Windows
        # ACL inspection is platform-specific; reparse checks remain enforced,
        # and Linux CI is the production proof for this boundary.
        if os.name != "nt":
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise SchemaError("UNSAFE_REGISTRY_PERMISSIONS", f"{field} is not owner-only")

    @staticmethod
    def _secret(path: Path) -> bytes:
        VerificationKeyRegistry._private_file(path, "controller authority key")
        try:
            stored = _read_store_bytes(path)
        except ReconciliationError as exc:
            raise SchemaError("UNSAFE_REGISTRY_PATH", "controller authority key cannot be read safely") from exc
        if stored is None:
            raise SchemaError("CONTROLLER_AUTH_REQUIRED", "controller authority key cannot be read")
        secret, _ = stored
        if not secret:
            raise SchemaError("CONTROLLER_AUTH_REQUIRED", "controller authority key is empty")
        return secret

    @staticmethod
    def _normalize_keys(keys: Mapping[str, str | bytes]) -> dict[str, bytes]:
        if not isinstance(keys, Mapping) or not keys:
            raise SchemaError("VERIFICATION_KEY_REQUIRED", "controller registry requires verifier keys")
        normalized: dict[str, bytes] = {}
        for identity, key in keys.items():
            identity = _string(identity, "verifier_identity")
            if _regex_fullmatch(_VERIFIER_IDENTITY, identity, "verifier_identity") is None:
                raise SchemaError("VERIFIER_UNTRUSTED", "registry identities must be controller-owned")
            if not isinstance(key, (str, bytes)):
                raise SchemaError("INVALID_FIELD", "verifier keys must be strings or bytes")
            value = key.encode() if isinstance(key, str) else key
            if not value:
                raise SchemaError("INVALID_FIELD", "verifier keys must be non-empty")
            normalized[identity] = bytes(value)
        return normalized

    @classmethod
    @_typed_boundary("verification key registry")
    def provision(cls, path: Path | str, *, authority_key_path: Path | str,
                  verification_keys: Mapping[str, str | bytes],
                  root: Path | str | None = None) -> "VerificationKeyRegistry":
        """Provision deployment-owned state from an existing protected authority key.

        The authority file is intentionally an input, never generated here: a
        receipt caller cannot bootstrap trust by choosing both a key registry
        and its signing key.
        """
        registry_path, root_path = _safe_store_path(path, root)
        authority = Path(authority_key_path)
        authority_path, _ = _safe_store_path(authority, root_path)
        secret = cls._secret(authority_path)
        if registry_path.exists():
            raise SchemaError("REGISTRY_EXISTS", "controller verifier registry is already provisioned")
        _ensure_store_directory(registry_path.parent)
        instance = cls.__new__(cls)
        instance.path, instance.root = registry_path, root_path
        instance.authority_key_path = authority_path
        instance.lock_path, _ = _safe_store_path(registry_path.with_name(registry_path.name + ".lock"), root_path)
        instance._keys = MappingProxyType({}); instance._retired_keys = MappingProxyType({}); instance._epoch = 0
        instance._path_identity = None
        with _journal_lock(instance.lock_path):
            instance._write_locked(cls._normalize_keys(verification_keys), 1, secret)
            instance._reload_locked()
        return instance

    def _write_locked(self, keys: Mapping[str, bytes], epoch: int, secret: bytes | None = None,
                      retired_keys: Mapping[str, Sequence[bytes]] | None = None) -> None:
        secret = self._secret(self.authority_key_path) if secret is None else secret
        entries = [{"verifier_identity": identity, "key_hex": value.hex()} for identity, value in sorted(keys.items())]
        retired = retired_keys if retired_keys is not None else self._retired_keys
        retired_entries = [{"verifier_identity": identity, "key_hex": value.hex()}
                           for identity, values in sorted(retired.items())
                           for value in sorted(set(values), key=lambda item: item.hex())]
        body = {"schema_version": SCHEMA_VERSION, "kind": "verification_key_registry", "registry_epoch": epoch,
                "keys": entries, "retired_keys": retired_entries}
        body["registry_digest"] = digest_record(body)
        body["authentication_tag"] = hmac.new(secret, body["registry_digest"].encode(), hashlib.sha256).hexdigest()
        self._path_identity = _replace_store_bytes(self.path, _canonical(body), expected_identity=self._path_identity)

    def _reload_locked(self) -> None:
        if not self.path.exists():
            raise SchemaError("VERIFICATION_REGISTRY_REQUIRED", "controller verifier registry is not provisioned")
        self._private_file(self.path, "controller verifier registry")
        try:
            stored = _read_store_bytes(self.path, expected_identity=self._path_identity)
        except ReconciliationError as exc:
            raise SchemaError("UNSAFE_REGISTRY_PATH", "controller verifier registry cannot be read safely") from exc
        if stored is None:
            raise SchemaError("VERIFICATION_REGISTRY_REQUIRED", "controller verifier registry is not provisioned")
        secret = self._secret(self.authority_key_path)
        payload, self._path_identity = stored
        try:
            state = _json_load(payload.decode("utf-8"))
        except _JsonInputError as exc:
            raise SchemaError("CORRUPT_REGISTRY", "controller verifier registry cannot be read") from exc
        except (UnicodeError, ValueError) as exc:
            raise SchemaError("CORRUPT_REGISTRY", "controller verifier registry cannot be read") from exc
        required = {"schema_version", "kind", "registry_epoch", "keys", "registry_digest", "authentication_tag"}
        _check_keys(state, required, {"retired_keys"}, "verification_key_registry")
        _schema_version(state["schema_version"], "controller verifier registry")
        if state["kind"] != "verification_key_registry":
            raise SchemaError("SCHEMA_VERSION", "unsupported controller verifier registry schema")
        epoch = _nonnegative_int(state["registry_epoch"], "registry_epoch")
        if epoch < 1:
            raise SchemaError("INVALID_FIELD", "registry_epoch must be positive")
        digest = _digest(state["registry_digest"], "registry_digest")
        body = {key: state[key] for key in required if key not in {"registry_digest", "authentication_tag"}}
        if "retired_keys" in state:
            body["retired_keys"] = state["retired_keys"]
        if digest != digest_record(body):
            raise SchemaError("DIGEST_MISMATCH", "controller verifier registry digest is invalid")
        tag = _digest(state["authentication_tag"], "authentication_tag")
        if not hmac.compare_digest(tag, hmac.new(secret, digest.encode(), hashlib.sha256).hexdigest()):
            raise SchemaError("CONTROLLER_AUTH_FAILED", "controller verifier registry authentication failed")
        if not isinstance(state["keys"], list) or not state["keys"]:
            raise SchemaError("VERIFICATION_KEY_REQUIRED", "controller verifier registry has no keys")
        normalized: dict[str, bytes] = {}
        for entry in state["keys"]:
            _check_keys(entry, {"verifier_identity", "key_hex"}, set(), "verification_key")
            identity = _string(entry["verifier_identity"], "verifier_identity")
            if _regex_fullmatch(_VERIFIER_IDENTITY, identity, "verifier_identity") is None or identity in normalized:
                raise SchemaError("VERIFIER_UNTRUSTED", "controller verifier registry identity is invalid")
            key_hex = _string(entry["key_hex"], "key_hex")
            if _regex_fullmatch(_KEY_HEX, key_hex, "key_hex") is None:
                raise SchemaError("INVALID_FIELD", "registry key encoding is invalid")
            try:
                value = bytes.fromhex(key_hex)
            except _INPUT_ERRORS as exc:
                raise SchemaError("INVALID_FIELD", "registry key encoding is invalid") from exc
            if not value:
                raise SchemaError("INVALID_FIELD", "registry key is empty")
            normalized[identity] = value
        retired_normalized: dict[str, list[bytes]] = {}
        retired_entries = state.get("retired_keys", [])
        if not isinstance(retired_entries, list):
            raise SchemaError("INVALID_FIELD", "retired verifier keys must be a list")
        for entry in retired_entries:
            _check_keys(entry, {"verifier_identity", "key_hex"}, set(), "retired_verification_key")
            identity = _string(entry["verifier_identity"], "verifier_identity")
            if _regex_fullmatch(_VERIFIER_IDENTITY, identity, "verifier_identity") is None:
                raise SchemaError("VERIFIER_UNTRUSTED", "retired registry identity is invalid")
            key_hex = _string(entry["key_hex"], "key_hex")
            if _regex_fullmatch(_KEY_HEX, key_hex, "key_hex") is None:
                raise SchemaError("INVALID_FIELD", "retired registry key encoding is invalid")
            try:
                value = bytes.fromhex(key_hex)
            except _INPUT_ERRORS as exc:
                raise SchemaError("INVALID_FIELD", "retired registry key encoding is invalid") from exc
            if not value or value == normalized.get(identity):
                raise SchemaError("INVALID_FIELD", "retired registry key duplicates an active key")
            values = retired_normalized.setdefault(identity, [])
            if value in values:
                raise SchemaError("CONFLICTING_REPLAY", "retired registry key is duplicated")
            values.append(value)
        self._keys = MappingProxyType(normalized)
        self._retired_keys = MappingProxyType({identity: tuple(values) for identity, values in retired_normalized.items()})
        self._epoch = epoch

    @_typed_boundary("verification key registry")
    def reload(self) -> None:
        with _journal_lock(self.lock_path):
            self._reload_locked()

    @property
    def keys(self) -> Mapping[str, bytes]:
        return self._keys

    @property
    def retired_keys(self) -> Mapping[str, tuple[bytes, ...]]:
        return self._retired_keys

    @property
    def epoch(self) -> int:
        return self._epoch

    @_typed_boundary("verification key rotation")
    def rotate(self, verifier_identity: str, key: str | bytes) -> int:
        identity = _string(verifier_identity, "verifier_identity")
        if _regex_fullmatch(_VERIFIER_IDENTITY, identity, "verifier_identity") is None:
            raise SchemaError("VERIFIER_UNTRUSTED", "registry identities must be controller-owned")
        value = key.encode() if isinstance(key, str) else key
        if not isinstance(value, bytes) or not value:
            raise SchemaError("INVALID_FIELD", "verifier key must be non-empty")
        with _journal_lock(self.lock_path):
            self._reload_locked()
            value = bytes(value)
            if value in self._retired_keys.get(identity, ()):
                raise SchemaError("INVALID_FIELD", "verifier key was previously retired")
            updated = dict(self._keys)
            retired = {key: list(values) for key, values in self._retired_keys.items()}
            previous = updated.get(identity)
            if previous is not None and previous != value:
                retired.setdefault(identity, []).append(previous)
            updated[identity] = value
            self._write_locked(updated, self._epoch + 1, retired_keys=retired)
            self._reload_locked()
            return self._epoch


class VerificationReceiptStore:
    """Durable controller-owned receipt index used by candidate integration admission."""

    def __init__(self, path: Path | str, *, root: Path | str | None = None,
                 verification_registry: VerificationKeyRegistry | Path | str | None = None,
                 verification_authority_key_path: Path | str | None = None,
                 verification_keys: Mapping[str, str | bytes] | None = None):
        self.path, self.root = _safe_store_path(path, root)
        _ensure_store_directory(self.path.parent)
        self.lock_path = _safe_store_path(self.path.with_name(self.path.name + ".lock"), self.root)[0]
        if verification_keys is not None:
            raise SchemaError("VERIFICATION_REGISTRY_REQUIRED", "caller-supplied verifier keys cannot bootstrap trust")
        if verification_registry is None:
            raise SchemaError("VERIFICATION_REGISTRY_REQUIRED", "receipt store requires a controller verifier registry")
        if isinstance(verification_registry, VerificationKeyRegistry):
            self.verification_registry = verification_registry
        else:
            self.verification_registry = VerificationKeyRegistry(
                verification_registry, authority_key_path=verification_authority_key_path, root=self.root)
        self.verification_keys: Mapping[str, bytes] = MappingProxyType({})
        self.retired_verification_keys: Mapping[str, tuple[bytes, ...]] = MappingProxyType({})
        self.receipts: dict[str, VerificationReceipt] = {}
        self._path_identity = None
        with _journal_lock(self.lock_path):
            self._reload_locked()

    def _reload_locked(self, *, registry_locked: bool = False) -> None:
        if registry_locked:
            self.verification_registry._reload_locked()
        else:
            self.verification_registry.reload()
        self.verification_keys = MappingProxyType(dict(self.verification_registry.keys))
        self.retired_verification_keys = MappingProxyType(
            {identity: tuple(keys) for identity, keys in self.verification_registry.retired_keys.items()})
        self.receipts.clear()
        stored = _read_store_bytes(self.path, expected_identity=self._path_identity)
        if stored is None:
            self._path_identity = None
            return
        payload, self._path_identity = stored
        try:
            lines = payload.decode("utf-8").splitlines()
        except UnicodeError as exc:
            raise ReconciliationError("CORRUPT_RECEIPT_STORE", "receipt store cannot be decoded safely") from exc
        for line in lines:
            try:
                raw = _json_load(line)
            except _JsonInputError as exc:
                raise ReconciliationError("CORRUPT_RECEIPT_STORE", "receipt store contains malformed JSON") from exc
            receipt = VerificationReceipt.from_dict(raw)
            old = self.receipts.get(receipt.receipt_id)
            if old is not None and old != receipt:
                raise ReconciliationError("CONFLICTING_REPLAY", "receipt identity has conflicting data")
            self._authenticate(receipt)
            self.receipts[receipt.receipt_id] = receipt

    def _key(self, verifier_identity: str) -> bytes:
        key = self.verification_keys.get(verifier_identity)
        if key is None:
            raise ReconciliationError("VERIFIER_UNREGISTERED", "receipt verifier is not registered")
        return key

    def _verification_keys(self, verifier_identity: str, *, active_only: bool = False) -> tuple[bytes, ...]:
        active = self.verification_keys.get(verifier_identity)
        if active is None:
            raise ReconciliationError("VERIFIER_UNREGISTERED", "receipt verifier is not registered")
        if active_only:
            return (active,)
        return (active, *self.retired_verification_keys.get(verifier_identity, ()))

    def _authenticate(self, receipt: VerificationReceipt, *, active_only: bool = False) -> None:
        if not receipt.authentication_tag:
            raise ReconciliationError("VERIFIER_AUTH_FAILED", "verification receipt authentication failed")
        expected_tags = (hmac.new(key, receipt.receipt_digest.encode(), hashlib.sha256).hexdigest()
                         for key in self._verification_keys(receipt.verifier_identity, active_only=active_only))
        if not any(hmac.compare_digest(expected, receipt.authentication_tag) for expected in expected_tags):
            raise ReconciliationError("VERIFIER_AUTH_FAILED", "verification receipt authentication failed")

    @_typed_boundary("verification receipt lookup")
    def get(self, receipt_id: str) -> VerificationReceipt | None:
        _id(receipt_id, "receipt_id")
        with _journal_lock(self.lock_path):
            self._reload_locked()
            return self.receipts.get(receipt_id)

    @_typed_boundary("verification receipt")
    def require(self, receipt: VerificationReceipt) -> VerificationReceipt:
        stored = self.get(receipt.receipt_id)
        if stored is None or stored != receipt:
            raise ReconciliationError("VERIFIER_RECEIPT_NOT_REGISTERED", "receipt is not the exact registered controller receipt")
        self._authenticate(stored)
        return stored

    @_typed_boundary("verification receipt digest")
    def require_digest(self, receipt_digest: str) -> VerificationReceipt:
        _digest(receipt_digest, "receipt_digest")
        with _journal_lock(self.lock_path):
            self._reload_locked()
            for receipt in self.receipts.values():
                if receipt.receipt_digest == receipt_digest:
                    self._authenticate(receipt)
                    return receipt
        raise ReconciliationError("VERIFIER_RECEIPT_NOT_REGISTERED", "receipt digest is not registered")

    @_typed_boundary("verification receipt")
    def issue(self, receipt: VerificationReceipt) -> str:
        if not isinstance(receipt, VerificationReceipt):
            raise SchemaError("INVALID_RECORD", "verification receipt must be a VerificationReceipt")
        receipt = VerificationReceipt.from_dict(receipt.to_dict())
        with _journal_lock(self.lock_path):
            # Rotation and issue share the registry lock. The registry is
            # reloaded while that lock is held, then the active key is used to
            # authenticate/sign and the receipt is appended before rotation
            # can publish a new epoch.
            with _journal_lock(self.verification_registry.lock_path):
                self._reload_locked(registry_locked=True)
                old = self.receipts.get(receipt.receipt_id)
                if old is not None:
                    if old == receipt:
                        return "duplicate"
                    raise ReconciliationError("CONFLICTING_RECEIPT", "receipt identity already exists")
                if receipt.authentication_tag:
                    self._authenticate(receipt, active_only=True)
                else:
                    tag = hmac.new(self._key(receipt.verifier_identity), receipt.receipt_digest.encode(), hashlib.sha256).hexdigest()
                    receipt = replace(receipt, authentication_tag=tag)
                self._path_identity = _append_bytes(self.path, _json_line(receipt.to_dict(), "verification receipt"),
                                                    expected_identity=self._path_identity)
                self.receipts[receipt.receipt_id] = receipt
                return "issued"
@_typed_boundary("candidate reference")
def validate_candidate_refs(*, result_ref: str, default_branch: str = "main",
                            integration_branch: str = "recursion/integration") -> None:
    """Reject protected or malformed refs using git-check-ref-format rules."""
    def normalize(value: str, field: str) -> str:
        value = _string(value, field).removeprefix("refs/heads/")
        invalid = (
            not value or value == "@" or value.startswith("/") or value.endswith("/") or
            "//" in value or ".." in value or "@{" in value or value.endswith(".") or
            any(part.endswith(".lock") for part in value.split("/")) or
            any(ord(char) < 32 or ord(char) == 127 for char in value) or
            any(char in value for char in (" ", "~", "^", ":", "?", "*", "[", "\\")) or
            any(part in {".", ".."} or part.startswith(".") for part in value.split("/"))
        )
        if invalid:
            raise AdmissionError("INVALID_RESULT_REF", f"{field} is not a valid git ref")
        return value

    result = normalize(result_ref, "result_ref")
    default = normalize(default_branch, "default_branch")
    integration = normalize(integration_branch, "integration_branch")
    if result in {default, integration}:
        raise AdmissionError("PROTECTED_REF", "candidate result ref targets a default or integration branch")
    if result.startswith("refs/") or result.startswith("HEAD"):
        raise AdmissionError("INVALID_RESULT_REF", "candidate result ref is not a named external branch")


def classify_stale_base(*, assigned_source_sha: str, current_source_sha: str,
                        integration_advanced: bool = False, source_available: bool = True,
                        assumptions_changed: bool = False) -> str:
    """Classify a candidate without rebasing or mutating any repository."""
    _commit(assigned_source_sha, "assigned_source_sha"); _commit(current_source_sha, "current_source_sha")
    if not source_available:
        return "source-unavailable"
    if assumptions_changed:
        return "invalidated"
    if integration_advanced:
        return "stale-rebase-required"
    if assigned_source_sha != current_source_sha:
        return "stale-reviewable"
    return "current-compatible"


@_typed_boundary("candidate result")
def verify_candidate_result(*, assignment: Assignment | Mapping[str, Any], receipt: VerificationReceipt | Mapping[str, Any],
                            candidate_id: str, result_commit: str, diff_digest: str, scope_digest: str, gate_digest: str,
                            result_ref: str, default_branch: str = "main",
                            integration_branch: str = "recursion/integration",
                            receipt_store: VerificationReceiptStore | None = None) -> str:
    """Validate a durable independent-verifier receipt for candidate import admission."""
    assignment = _revalidate_assignment(assignment)
    receipt = receipt if isinstance(receipt, VerificationReceipt) else VerificationReceipt.from_dict(receipt)
    if receipt_store is None:
        raise ReconciliationError("VERIFIER_AUTH_REQUIRED", "candidate verification requires a controller receipt store")
    receipt_store.require(receipt)
    if assignment.assignment_digest != receipt.assignment_digest:
        raise ReconciliationError("ASSIGNMENT_MISMATCH", "candidate result assignment digest differs")
    if assignment.source_sha != receipt.source_sha:
        raise ReconciliationError("SOURCE_MISMATCH", "candidate result source differs from assignment")
    if receipt.candidate_id != _id(candidate_id, "candidate_id"):
        raise ReconciliationError("CANDIDATE_MISMATCH", "candidate identity differs from receipt")
    if assignment.candidate_id is not None and assignment.candidate_id != receipt.candidate_id:
        raise ReconciliationError("CANDIDATE_MISMATCH", "candidate identity differs from assignment")
    if receipt.result_commit != _commit(result_commit, "result_commit"):
        raise ReconciliationError("RESULT_MISMATCH", "result commit differs from receipt")
    for field, value in (("diff_digest", diff_digest), ("scope_digest", scope_digest), ("gate_digest", gate_digest)):
        if getattr(receipt, field) != _digest(value, field):
            raise ReconciliationError("VERIFICATION_BINDING_MISMATCH", f"{field} differs from receipt")
    validate_candidate_refs(result_ref=result_ref, default_branch=default_branch, integration_branch=integration_branch)
    if _regex_fullmatch(_VERIFIER_IDENTITY, receipt.verifier_identity, "verifier_identity") is None:
        raise ReconciliationError("VERIFIER_UNTRUSTED", "verification identity is not controller-owned")
    return "verified"


class IntegrationCoordinator:
    """Durable, serialized same-project integration admission; never performs git operations."""

    def __init__(self, path: Path | str | None = None, *, root: Path | str | None = None,
                 pause_guard: PauseGuard | None = None,
                 receipt_store: VerificationReceiptStore | None = None):
        self.pause_guard = pause_guard
        if receipt_store is None:
            raise ReconciliationError("VERIFIER_AUTH_REQUIRED", "integration coordinator requires a controller receipt store")
        self.receipt_store = receipt_store
        self.path = None if path is None else _safe_store_path(path, root)[0]
        self.root = None if path is None else _safe_store_path(path, root)[1]
        if self.path is not None:
            _ensure_store_directory(self.path.parent)
            self.lock_path = _safe_store_path(self.path.with_name(self.path.name + ".lock"), self.root)[0]
        self._active: dict[str, str] = {}
        self._candidates: dict[str, dict[str, Any]] = {}
        self._policies: dict[str, dict[str, str]] = {}
        self._tail_digest = ZERO_DIGEST
        self._path_identity = None
        if self.path is not None:
            with _journal_lock(self.lock_path):
                self._reload_locked()

    def _reload_locked(self) -> None:
        self._active.clear(); self._candidates.clear(); self._policies.clear(); self._tail_digest = ZERO_DIGEST
        if self.path is None:
            return
        stored = _read_store_bytes(self.path, expected_identity=self._path_identity)
        if stored is None:
            self._path_identity = None
            return
        payload, self._path_identity = stored
        try:
            lines = payload.decode("utf-8").splitlines()
        except UnicodeError as exc:
            raise ReconciliationError("CORRUPT_JOURNAL", "integration journal cannot be decoded safely") from exc
        for number, line in enumerate(lines, 1):
            try:
                event = _json_load(line)
                self._validate_event(event)
                if event.get("event") == "admit" and self.receipt_store is not None:
                    self.receipt_store.require_digest(event["receipt_digest"])
                self._apply_event(event)
                self._tail_digest = event["event_digest"]
            except _JsonInputError as exc:
                raise ReconciliationError("CORRUPT_JOURNAL", f"invalid integration event at line {number}") from exc
            except FabricError:
                raise
            except (ValueError, TypeError, KeyError, UnicodeError) as exc:
                raise ReconciliationError("CORRUPT_JOURNAL", f"invalid integration event at line {number}") from exc

    def _validate_event(self, event: Mapping[str, Any]) -> None:
        if not isinstance(event, Mapping) or type(event.get("schema_version")) is not int or event.get("schema_version") != SCHEMA_VERSION:
            raise ReconciliationError("SCHEMA_VERSION", "unsupported integration event")
        _digest(event.get("event_digest"), "event_digest"); _digest(event.get("prev_event_digest"), "prev_event_digest")
        if event["prev_event_digest"] != self._tail_digest:
            raise ReconciliationError("JOURNAL_CHAIN", "integration journal chain is broken")
        body = {key: value for key, value in event.items() if key != "event_digest"}
        if hashlib.sha256(_canonical(body)).hexdigest() != event["event_digest"]:
            raise ReconciliationError("DIGEST_MISMATCH", "integration event digest is invalid")
        kind = event.get("event")
        if kind == "policy":
            _check_keys(event, {"event", "schema_version", "event_digest", "prev_event_digest", "project_id", "default_branch", "integration_branch"}, set(), "integration_policy")
            _id(event["project_id"], "project_id"); _string(event["default_branch"], "default_branch"); _string(event["integration_branch"], "integration_branch")
        elif kind == "admit":
            _check_keys(event, {"event", "schema_version", "event_digest", "prev_event_digest", "candidate_id", "project_id", "assignment_digest", "source_sha", "result_commit", "source_ref", "result_ref", "default_branch", "integration_branch", "classification", "receipt_digest"}, set(), "integration_admit")
            _id(event["candidate_id"], "candidate_id"); _id(event["project_id"], "project_id"); _commit(event["source_sha"], "source_sha"); _commit(event["result_commit"], "result_commit")
            _string(event["source_ref"], "source_ref")
            _digest(event["assignment_digest"], "assignment_digest")
            if event["classification"] not in {"current-compatible", "stale-reviewable"}:
                raise ReconciliationError("STALE_CLASSIFICATION_REQUIRED", "integration journal classification is invalid")
            _digest(event["receipt_digest"], "receipt_digest")
            validate_candidate_refs(result_ref=event["result_ref"], default_branch=event["default_branch"], integration_branch=event["integration_branch"])
        elif kind == "complete":
            _check_keys(event, {"event", "schema_version", "event_digest", "prev_event_digest", "candidate_id"}, set(), "integration_complete")
            _id(event["candidate_id"], "candidate_id")
        else:
            raise ReconciliationError("UNKNOWN_EVENT", "unknown integration event")

    def _record_locked(self, event: Mapping[str, Any]) -> None:
        body = dict(event); body["schema_version"] = SCHEMA_VERSION; body["prev_event_digest"] = self._tail_digest
        body["event_digest"] = hashlib.sha256(_canonical(body)).hexdigest()
        self._validate_event(body)
        data = _json_line(body, "integration journal event")
        self._path_identity = _append_bytes(self.path, data, expected_identity=self._path_identity)
        self._apply_event(body); self._tail_digest = body["event_digest"]

    def _apply_event(self, event: Mapping[str, Any]) -> None:
        kind = event["event"]
        if kind == "policy":
            self._policies[event["project_id"]] = {"default_branch": event["default_branch"], "integration_branch": event["integration_branch"]}
        elif kind == "admit":
            existing = self._candidates.get(event["candidate_id"])
            value = {key: event[key] for key in ("project_id", "assignment_digest", "source_sha", "result_commit", "source_ref", "result_ref", "classification", "receipt_digest")}
            value["status"] = "active"
            if existing is not None:
                same_identity = all(existing.get(key) == value[key] for key in value if key != "status")
                if not same_identity:
                    raise ReconciliationError("CONFLICTING_REPLAY", "candidate identity has conflicting replay data")
                if existing.get("status") == "complete":
                    return
            current = self._active.get(event["project_id"])
            if current is not None and current != event["candidate_id"]:
                raise ReconciliationError("INTEGRATION_SERIALIZED", "journal replays two active candidates for one project")
            self._candidates[event["candidate_id"]] = value; self._active[event["project_id"]] = event["candidate_id"]
        elif kind == "complete":
            candidate = self._candidates.get(event["candidate_id"])
            if candidate is None:
                raise ReconciliationError("UNKNOWN_CANDIDATE", "completion references no candidate")
            candidate["status"] = "complete"; self._active.pop(candidate["project_id"], None)

    @_typed_boundary("integration policy")
    def set_project_policy(self, *, project_id: str, default_branch: str, integration_branch: str) -> str:
        if self.pause_guard is not None:
            self.pause_guard.assert_open()
        _id(project_id, "project_id"); _string(default_branch, "default_branch"); _string(integration_branch, "integration_branch")
        validate_candidate_refs(result_ref="candidate-policy-check", default_branch=default_branch, integration_branch=integration_branch)
        if self.path is None:
            self._policies[project_id] = {"default_branch": default_branch, "integration_branch": integration_branch}; return "set"
        with _journal_lock(self.lock_path):
            self._reload_locked(); self._record_locked({"event": "policy", "project_id": project_id, "default_branch": default_branch, "integration_branch": integration_branch}); return "set"

    @_typed_boundary("integration admission")
    def admit(self, *, candidate_id: str, project_id: str, source_sha: str, result_commit: str,
              assignment: Assignment | Mapping[str, Any] | None = None,
              source_ref: str = "source", result_ref: str | None = None,
              default_branch: str | None = None, integration_branch: str | None = None,
              classification: str | None = None,
              verification_receipt: VerificationReceipt | Mapping[str, Any] | None = None) -> str:
        if self.pause_guard is not None:
            self.pause_guard.assert_open()
        _id(candidate_id, "candidate_id"); _id(project_id, "project_id"); _commit(source_sha, "source_sha"); _commit(result_commit, "result_commit")
        if assignment is None:
            raise ReconciliationError("ASSIGNMENT_REQUIRED", "integration requires the immutable assignment record")
        assignment = _revalidate_assignment(assignment)
        if assignment.project_id != project_id or assignment.source_sha != source_sha:
            raise ReconciliationError("ASSIGNMENT_MISMATCH", "assignment does not match integration source")
        if assignment.candidate_id != candidate_id:
            raise ReconciliationError("CANDIDATE_MISMATCH", "candidate does not match immutable assignment")
        if classification not in {"current-compatible", "stale-reviewable"}:
            raise ReconciliationError("STALE_CLASSIFICATION_REQUIRED", "integration requires current or stale-reviewable classification")
        if verification_receipt is None:
            raise ReconciliationError("VERIFIER_REQUIRED", "integration requires an independent verification receipt")
        if self.receipt_store is None:
            raise ReconciliationError("VERIFIER_AUTH_REQUIRED", "integration requires a controller receipt store")
        receipt = verification_receipt if isinstance(verification_receipt, VerificationReceipt) else VerificationReceipt.from_dict(verification_receipt)
        self.receipt_store.require(receipt)
        if receipt.assignment_digest != assignment.assignment_digest or receipt.candidate_id != candidate_id or receipt.source_sha != source_sha or receipt.result_commit != result_commit:
            raise ReconciliationError("VERIFICATION_BINDING_MISMATCH", "verification receipt is not bound to this candidate")
        def policy_refs() -> tuple[str, str, str]:
            policy = self._policies.get(project_id, {"default_branch": "main", "integration_branch": "recursion/integration"})
            if default_branch is not None and default_branch != policy["default_branch"]:
                raise AdmissionError("POLICY_MISMATCH", "caller default branch differs from the configured project policy")
            if integration_branch is not None and integration_branch != policy["integration_branch"]:
                raise AdmissionError("POLICY_MISMATCH", "caller integration branch differs from the configured project policy")
            default = policy["default_branch"]; integration = policy["integration_branch"]
            resolved_result_ref = result_ref or f"recursion/candidate/{candidate_id}"
            _string(source_ref, "source_ref")
            validate_candidate_refs(result_ref=resolved_result_ref, default_branch=default, integration_branch=integration)
            return default, integration, resolved_result_ref
        if self.path is None:
            default, integration, result_ref = policy_refs()
            return self._admit_memory(candidate_id, project_id, assignment.assignment_digest, source_sha, result_commit, source_ref, result_ref, default, integration, classification, receipt.receipt_digest)
        with _journal_lock(self.lock_path):
            self._reload_locked()
            default, integration, result_ref = policy_refs()
            return self._admit_locked(candidate_id, project_id, assignment.assignment_digest, source_sha, result_commit, source_ref, result_ref, default, integration, classification, receipt.receipt_digest)

    def _admit_memory(self, candidate_id: str, project_id: str, assignment_digest: str, source_sha: str, result_commit: str, source_ref: str, result_ref: str, default: str, integration: str, classification: str, receipt_digest: str) -> str:
        existing = self._candidates.get(candidate_id)
        proposed = {"project_id": project_id, "assignment_digest": assignment_digest, "source_sha": source_sha, "result_commit": result_commit, "source_ref": source_ref, "result_ref": result_ref, "classification": classification, "receipt_digest": receipt_digest, "status": "active"}
        if existing is not None:
            same_identity = all(existing.get(key) == proposed[key] for key in proposed if key != "status")
            if same_identity: return "completed" if existing.get("status") == "complete" else "duplicate"
            raise AdmissionError("CONFLICTING_CANDIDATE", "candidate identity is already bound to another result")
        current = self._active.get(project_id)
        if current is not None: raise AdmissionError("INTEGRATION_SERIALIZED", f"project already has active integration candidate {current}")
        self._candidates[candidate_id] = proposed; self._active[project_id] = candidate_id; return "admitted"

    def _admit_locked(self, candidate_id: str, project_id: str, assignment_digest: str, source_sha: str, result_commit: str, source_ref: str, result_ref: str, default: str, integration: str, classification: str, receipt_digest: str) -> str:
        existing = self._candidates.get(candidate_id)
        proposed = {"project_id": project_id, "assignment_digest": assignment_digest, "source_sha": source_sha, "result_commit": result_commit, "source_ref": source_ref, "result_ref": result_ref, "classification": classification, "receipt_digest": receipt_digest, "status": "active"}
        if existing is not None:
            same_identity = all(existing.get(key) == proposed[key] for key in proposed if key != "status")
            if same_identity: return "completed" if existing.get("status") == "complete" else "duplicate"
            raise AdmissionError("CONFLICTING_CANDIDATE", "candidate identity is already bound to another result")
        current = self._active.get(project_id)
        if current is not None: raise AdmissionError("INTEGRATION_SERIALIZED", f"project already has active integration candidate {current}")
        self._record_locked({"event": "admit", "candidate_id": candidate_id, "project_id": project_id, "assignment_digest": assignment_digest, "source_sha": source_sha, "result_commit": result_commit, "source_ref": source_ref, "result_ref": result_ref, "default_branch": default, "integration_branch": integration, "classification": classification, "receipt_digest": receipt_digest})
        return "admitted"

    @_typed_boundary("integration completion")
    def complete(self, candidate_id: str) -> str:
        if self.pause_guard is not None:
            self.pause_guard.assert_open()
        _id(candidate_id, "candidate_id")
        if self.path is None:
            candidate = self._candidates.get(candidate_id)
            if candidate is None: raise AdmissionError("UNKNOWN_CANDIDATE", "candidate is not known")
            if candidate["status"] == "complete": return "duplicate"
            candidate["status"] = "complete"; self._active.pop(candidate["project_id"], None); return "completed"
        with _journal_lock(self.lock_path):
            self._reload_locked()
            candidate = self._candidates.get(candidate_id)
            if candidate is None: raise AdmissionError("UNKNOWN_CANDIDATE", "candidate is not known")
            if candidate["status"] == "complete": return "duplicate"
            self._record_locked({"event": "complete", "candidate_id": candidate_id}); return "completed"

    @property
    def active(self) -> Mapping[str, str]:
        return MappingProxyType(dict(self._active))

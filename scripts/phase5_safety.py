"""Small, dependency-free safety primitives shared by the Phase 5 boundaries.

The controller consumes attacker-influenced JSON and paths.  This module keeps the
size/depth and exception boundary in one place, and provides descriptor/handle based
file operations so a check is not separated from the read or write it authorizes.
"""

from __future__ import annotations

import ctypes
import json
import math
import os
import secrets
import stat
import subprocess
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Iterator


MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 128
MAX_JSON_INT_DIGITS = 1024
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_FILE_BYTES = 16 * 1024 * 1024
REPARSE_POINT = 0x400


class BoundaryError(ValueError):
    """A controlled failure caused by malformed or unsafe caller input."""


def is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value} is not permitted")


def _parse_int(value: str) -> int:
    if len(value.lstrip("-")) > MAX_JSON_INT_DIGITS:
        raise ValueError("JSON integer is too large")
    return int(value)


def _check_json_depth(raw: bytes, label: str) -> None:
    depth = 0
    maximum = 0
    quoted = False
    escaped = False
    for byte in raw:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 0x5C:  # backslash
                escaped = True
            elif byte == 0x22:  # quote
                quoted = False
            continue
        if byte == 0x22:
            quoted = True
        elif byte in (0x7B, 0x5B):  # {[
            depth += 1
            maximum = max(maximum, depth)
            if maximum > MAX_JSON_DEPTH:
                raise BoundaryError(f"{label} exceeds the maximum JSON nesting depth")
        elif byte in (0x7D, 0x5D):  # }]
            depth -= 1
            if depth < 0:
                raise BoundaryError(f"{label} has malformed JSON nesting")
    if quoted or escaped or depth != 0:
        # json.loads supplies the detailed syntax diagnostic after this cheap scan;
        # this branch only keeps the scanner itself inside the typed boundary.
        return


def decode_json(raw: bytes | str, label: str = "JSON") -> object:
    try:
        if isinstance(raw, str):
            encoded = raw.encode("utf-8")
        elif isinstance(raw, (bytes, bytearray)):
            encoded = bytes(raw)
        else:
            raise TypeError("JSON input must be bytes or text")
        if len(encoded) > MAX_JSON_BYTES:
            raise BoundaryError(f"{label} is too large")
        _check_json_depth(encoded, label)
        text = encoded.decode("utf-8")
        value = json.loads(text, parse_int=_parse_int, parse_constant=_reject_constant)
        pending = [value]
        while pending:
            item = pending.pop()
            if isinstance(item, float) and not math.isfinite(item):
                raise BoundaryError(f"{label} contains a non-finite number")
            if isinstance(item, dict):
                pending.extend(item.values())
            elif isinstance(item, list):
                pending.extend(item)
        return value
    except BoundaryError:
        raise
    except (json.JSONDecodeError, ValueError, TypeError, OverflowError,
            RecursionError, UnicodeDecodeError, OSError) as exc:
        raise BoundaryError(f"{label} is malformed") from exc


def read_bounded_stream(stream: object, *, label: str = "input",
                        max_bytes: int = MAX_JSON_BYTES) -> bytes:
    """Read at most one byte beyond a caller-input limit before decoding."""
    try:
        if not is_plain_int(max_bytes) or max_bytes < 0:
            raise ValueError(f"{label} has an invalid size limit")
        read = getattr(stream, "read")
        raw = read(max_bytes + 1)
        if not isinstance(raw, (bytes, bytearray)):
            raise TypeError(f"{label} stream did not return bytes")
        if len(raw) > max_bytes:
            raise BoundaryError(f"{label} is too large")
        return bytes(raw)
    except BoundaryError:
        raise
    except (AttributeError, OSError, ValueError, TypeError, OverflowError, RecursionError,
            UnicodeDecodeError) as exc:
        raise BoundaryError(f"{label} is unreadable") from exc


def _git_show_bounded(root: Path, commit: str, relative: str,
                      max_bytes: int, *, label: str | None = None) -> tuple[int, bytes]:
    """Read one Git blob through a bounded pipe and terminate an over-limit producer."""
    stream_label = label or f"controller policy file {relative}"
    try:
        process = subprocess.Popen(
            ["git", "-C", str(root), "show", f"{commit}:{relative}"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
    except (OSError, TypeError, ValueError) as exc:
        raise BoundaryError(f"{stream_label} is unreadable") from exc
    try:
        if process.stdout is None:
            raise OSError("git show did not provide a stdout pipe")
        committed = read_bounded_stream(
            process.stdout, label=stream_label, max_bytes=max_bytes,
        )
        returncode = process.wait()
    except BoundaryError:
        raise
    except (OSError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise BoundaryError(f"{stream_label} is unreadable") from exc
    finally:
        if process.poll() is None:
            try:
                process.kill()
            except OSError:
                pass
        try:
            process.wait()
        except OSError:
            pass
    return returncode, committed


def _reparse(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & REPARSE_POINT
    )


def _identity(info: os.stat_result) -> tuple[int, int, int, bool]:
    return (int(getattr(info, "st_dev", 0)), int(getattr(info, "st_ino", 0)),
            int(getattr(info, "st_nlink", 0)), _reparse(info))


def _verify_regular(fd: int, label: str, before: os.stat_result | None = None) -> os.stat_result:
    try:
        info = os.fstat(fd)
    except (OSError, ValueError, TypeError) as exc:
        raise BoundaryError(f"{label} cannot be inspected") from exc
    if not stat.S_ISREG(info.st_mode) or _reparse(info) or int(getattr(info, "st_nlink", 0)) != 1:
        raise BoundaryError(f"{label} is not a single-link regular file")
    if before is not None and _identity(before) != _identity(info):
        raise BoundaryError(f"{label} changed identity during use")
    return info


def _win_handle(path: str, directory: bool, *, add_file: bool = False) -> int:
    # Open with OPEN_REPARSE_POINT so the final component is inspected, not
    # traversed.  Omitting FILE_SHARE_DELETE pins the directory and its ancestors
    # against rename/delete while the caller uses the child handle.
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel32.CreateFileW
    create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    create.restype = ctypes.c_void_p
    access = 0x80000000 if not directory else 0x00000080  # GENERIC_READ / FILE_READ_ATTRIBUTES
    if directory and add_file:
        access = 0x80000000 | 0x00000002  # GENERIC_READ | FILE_ADD_FILE
    share = 0x00000001 | 0x00000002  # FILE_SHARE_READ | FILE_SHARE_WRITE; deny delete
    flags = 0x02000000 | 0x00200000 if directory else 0x00200000  # BACKUP_SEMANTICS / OPEN_REPARSE_POINT
    handle = create(path, access, share, None, 3, flags, None)  # OPEN_EXISTING
    if handle in (None, ctypes.c_void_p(-1).value):
        error = ctypes.get_last_error()
        raise OSError(error, f"cannot open {path}")
    import msvcrt
    try:
        return msvcrt.open_osfhandle(handle, os.O_RDONLY | getattr(os, "O_BINARY", 0))
    except BaseException:
        kernel32.CloseHandle(handle)
        raise


def _win_create_temp(parent: str, basename: str) -> tuple[int, str]:
    """Create a same-directory temporary file with DELETE access already granted."""
    try:
        import msvcrt
        import ctypes.wintypes as wintypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel32.CreateFileW
        create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.c_void_p]
        create.restype = ctypes.c_void_p
        access = 0x80000000 | 0x40000000 | 0x00010000  # GENERIC_READ/WRITE | DELETE
        share = 0x00000001 | 0x00000002 | 0x00000004
        flags = 0x00000080 | 0x00200000  # FILE_ATTRIBUTE_NORMAL | OPEN_REPARSE_POINT
        for attempt in range(32):
            name = f".{basename}.{os.getpid()}.{secrets.token_hex(8)}-{attempt}"
            path = os.path.join(parent, name)
            handle = create(path, access, share, None, 1, flags, None)  # CREATE_NEW
            if handle in (None, ctypes.c_void_p(-1).value):
                error = ctypes.get_last_error()
                if error == 80:  # ERROR_FILE_EXISTS
                    continue
                raise OSError(error, "cannot create atomic publication temporary")
            try:
                return msvcrt.open_osfhandle(handle, os.O_RDWR | getattr(os, "O_BINARY", 0)), path
            except BaseException:
                kernel32.CloseHandle(handle)
                raise
        raise BoundaryError("could not allocate temporary output")
    except BoundaryError:
        raise
    except (ImportError, OSError, ValueError, TypeError, OverflowError) as exc:
        raise BoundaryError("could not allocate temporary output") from exc


def _open_directory(path: str, *, add_file: bool = False) -> int:
    if os.name == "nt":
        return _win_handle(path, True, add_file=add_file)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    return os.open(path, flags)


def _open_file(path: str) -> int:
    if os.name == "nt":
        return _win_handle(path, False)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    return os.open(path, flags)


def _open_file_at(path: str, parent_fd: int) -> int:
    if os.name == "nt":
        return _open_file(path)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    return os.open(os.path.basename(path), flags, dir_fd=parent_fd)


def _win_fd_handle(fd: int):
    try:
        import msvcrt
        import ctypes.wintypes as wintypes
        value = msvcrt.get_osfhandle(fd)
    except (ImportError, OSError, ValueError, TypeError) as exc:
        raise BoundaryError("Windows file handle is unavailable") from exc
    if value in (-1, None):
        raise BoundaryError("Windows file handle is invalid")
    return wintypes.HANDLE(value)


def _win_final_path(fd: int) -> str:
    try:
        import ctypes.wintypes as wintypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        getter = kernel32.GetFinalPathNameByHandleW
        getter.argtypes = [wintypes.HANDLE, ctypes.c_wchar_p, wintypes.DWORD, wintypes.DWORD]
        getter.restype = wintypes.DWORD
        size = 512
        while size <= 32768:
            buffer = ctypes.create_unicode_buffer(size)
            length = getter(_win_fd_handle(fd), buffer, size, 0)
            if length == 0:
                raise OSError(ctypes.get_last_error(), "GetFinalPathNameByHandleW failed")
            if length < size:
                value = buffer.value
                if value.startswith("\\\\?\\"):
                    value = value[4:]
                return value
            size *= 2
        raise BoundaryError("pinned directory path is too long")
    except BoundaryError:
        raise
    except (ImportError, OSError, ValueError, TypeError, OverflowError) as exc:
        raise BoundaryError("pinned directory path is unavailable") from exc


def _win_rename_by_handle(source_fd: int, parent_fd: int, name: str,
                          *, replace: bool) -> None:
    """Rename an open file beneath an already pinned Windows parent handle.

    SetFileInformationByHandle consumes the source handle.  The destination is
    derived from the already pinned parent handle; the parent handle denies
    rename/delete while it is held, and the destination identity is rechecked
    immediately before this call.  This keeps the commit independent of the
    caller's mutable pathname namespace.
    """
    try:
        import ctypes.wintypes as wintypes
        class FileRenameInfo(ctypes.Structure):
            _fields_ = [
                ("ReplaceIfExists", wintypes.BOOLEAN),
                ("RootDirectory", wintypes.HANDLE),
                ("FileNameLength", wintypes.DWORD),
                ("FileName", wintypes.WCHAR * 1),
            ]
        destination = os.path.join(_win_final_path(parent_fd), name)
        encoded = destination.encode("utf-16-le")
        size = FileRenameInfo.FileName.offset + len(encoded) + 2
        buffer = ctypes.create_string_buffer(size)
        info = FileRenameInfo.from_buffer(buffer)
        info.ReplaceIfExists = bool(replace)
        # Windows accepts a fully qualified name for FileRenameInfo.  The name
        # is obtained from the pinned parent handle, never from the caller's
        # destination pathname, so a swapped parent pathname cannot redirect it.
        info.RootDirectory = None
        info.FileNameLength = len(encoded) + 2
        ctypes.memmove(ctypes.addressof(info) + FileRenameInfo.FileName.offset,
                       encoded, len(encoded))
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        setter = kernel32.SetFileInformationByHandle
        setter.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
        setter.restype = wintypes.BOOL
        if not setter(_win_fd_handle(source_fd), 3, ctypes.byref(info), len(buffer)):
            error = ctypes.get_last_error()
            raise OSError(error, "SetFileInformationByHandle(FileRenameInfo) failed")
    except BoundaryError:
        raise
    except (ImportError, OSError, ValueError, TypeError, OverflowError) as exc:
        raise BoundaryError("atomic publication could not commit by pinned handle") from exc


def _absolute_lexical(path: Path | str) -> str:
    try:
        raw = os.fspath(path)
        if not isinstance(raw, str) or not raw:
            raise BoundaryError("path must be a nonempty string")
        if ".." in raw.replace("\\", "/").split("/"):
            raise BoundaryError("path traversal is not admitted")
        if os.name == "nt":
            if raw.startswith(("\\\\", "//")):
                raise BoundaryError("UNC paths are not admitted")
            drive, tail = os.path.splitdrive(raw)
            if drive and not tail.startswith(("\\", "/")):
                raise BoundaryError("drive-relative paths are not admitted")
        return os.path.abspath(raw)
    except BoundaryError:
        raise
    except (OSError, ValueError, TypeError, OverflowError, RecursionError,
            UnicodeDecodeError) as exc:
        raise BoundaryError("path is not a valid lexical path") from exc


def absolute_lexical(path: Path | str) -> str:
    """Return a checked lexical absolute path without resolving links."""
    return _absolute_lexical(path)


@contextmanager
def pinned_directory(path: Path | str, *, for_publication: bool = False) -> Iterator[tuple[int, str]]:
    """Pin every directory component without following a reparse/symlink."""
    absolute = _absolute_lexical(path)
    if os.name == "nt":
        drive, tail = os.path.splitdrive(absolute)
        if not drive:
            raise BoundaryError("Windows path must have a drive")
        current = drive + os.sep
        components = [item for item in tail.replace("/", os.sep).split(os.sep) if item]
        root = current
    else:
        root = os.sep
        components = [item for item in absolute.split(os.sep) if item]
        current = root
    with ExitStack() as stack:
        try:
            descriptor = _open_directory(root)
            stack.callback(os.close, descriptor)
            info = os.fstat(descriptor)
            if _reparse(info):
                raise BoundaryError("path root is a reparse point")
            for component in components:
                current = os.path.join(current, component)
                child = (_open_directory(current, add_file=for_publication and component == components[-1]) if os.name == "nt"
                         else os.open(component, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                                     | getattr(os, "O_NOFOLLOW", 0), dir_fd=descriptor))
                stack.callback(os.close, child)
                child_info = os.fstat(child)
                if not stat.S_ISDIR(child_info.st_mode) or _reparse(child_info):
                    raise BoundaryError(f"path component is not a real directory: {current}")
                descriptor = child
        except BoundaryError:
            raise
        except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
            raise BoundaryError(f"directory is unavailable: {path}") from exc
        yield descriptor, absolute


@contextmanager
def _pinned_parent(path: Path | str) -> Iterator[tuple[int, str]]:
    absolute = _absolute_lexical(path)
    parent = os.path.dirname(absolute) or os.curdir
    name = os.path.basename(absolute)
    if not name or name in {".", ".."}:
        raise BoundaryError("path must name a file")
    with pinned_directory(parent, for_publication=True) as (descriptor, _):
        yield descriptor, absolute


def _read_open_file(fd: int, path: Path | str, max_bytes: int,
                    private: bool = False,
                    path_before: os.stat_result | None = None) -> bytes:
    before = _verify_regular(fd, str(path), path_before)
    if private and os.name != "nt" and stat.S_IMODE(before.st_mode) & 0o022:
        raise BoundaryError(f"{path} is writable by group or other")
    if before.st_size > max_bytes:
        raise BoundaryError("file is too large")
    pieces: list[bytes] = []
    remaining = int(before.st_size)
    while remaining:
        chunk = os.read(fd, min(1024 * 1024, remaining))
        if not chunk:
            break
        pieces.append(chunk)
        remaining -= len(chunk)
    if remaining:
        raise BoundaryError("file changed while being read")
    after = _verify_regular(fd, str(path), before)
    if after.st_size != before.st_size:
        raise BoundaryError("file changed size during use")
    return b"".join(pieces)


def read_bytes(path: Path | str, *, label: str = "file", max_bytes: int = MAX_FILE_BYTES,
               private: bool = False, optional: bool = False) -> bytes | None:
    try:
        with _pinned_parent(path) as (_parent_fd, absolute):
            # Parent handles are retained while the no-follow leaf is opened and read.
            try:
                path_before = os.lstat(absolute)
            except FileNotFoundError:
                path_before = None
            fd = _open_file_at(absolute, _parent_fd)
            try:
                if path_before is None:
                    raise BoundaryError(f"{label} changed before it was opened")
                return _read_open_file(fd, path, max_bytes, private, path_before)
            finally:
                os.close(fd)
    except FileNotFoundError:
        if optional:
            return None
        raise BoundaryError(f"{label} is unavailable")
    except OSError as exc:
        missing = getattr(exc, "winerror", None) in (2, 3) or getattr(exc, "errno", None) in (2, 3)
        if optional and missing:
            return None
        raise BoundaryError(f"{label} is unavailable") from exc
    except BoundaryError:
        raise
    except (UnicodeDecodeError, ValueError, TypeError, OverflowError,
            RecursionError) as exc:
        raise BoundaryError(f"{label} is unavailable") from exc


def read_text(path: Path | str, *, label: str = "file", max_bytes: int = MAX_FILE_BYTES,
              private: bool = False) -> str:
    try:
        return read_bytes(path, label=label, max_bytes=max_bytes,
                          private=private).decode("utf-8")
    except BoundaryError:
        raise
    except UnicodeDecodeError as exc:
        raise BoundaryError(f"{label} is not valid UTF-8") from exc


def verify_leaf(path: Path | str, *, allow_directory: bool = True) -> os.stat_result | None:
    """Verify one existing leaf without following a link/reparse substitution.

    The result is None only when the leaf is absent.  A directory is pinned with
    the same no-follow rules as its ancestors; a regular file is opened relative to
    its pinned parent and its pre-open identity is checked against the file handle.
    """
    absolute = _absolute_lexical(path)
    try:
        with _pinned_parent(absolute) as (parent_fd, _):
            try:
                before = os.lstat(absolute)
            except FileNotFoundError:
                return None
            if _reparse(before):
                raise BoundaryError(f"path is a reparse point: {path}")
            if stat.S_ISDIR(before.st_mode):
                if not allow_directory:
                    raise BoundaryError(f"path is not a regular file: {path}")
                with pinned_directory(absolute) as (directory_fd, _):
                    after = os.fstat(directory_fd)
                    if _identity(before)[:2] != _identity(after)[:2] or _reparse(after):
                        raise BoundaryError(f"directory changed while being inspected: {path}")
                return after
            fd = _open_file_at(absolute, parent_fd)
            try:
                after = _verify_regular(fd, str(path), before)
            finally:
                os.close(fd)
            return after
    except FileNotFoundError:
        return None
    except BoundaryError:
        raise
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise BoundaryError(f"path cannot be inspected safely: {path}") from exc


def load_json_file(path: Path | str, *, label: str = "JSON") -> object:
    return decode_json(read_bytes(path, label=label, max_bytes=MAX_JSON_BYTES), label)


def ensure_directory(path: Path | str) -> str:
    """Create missing directory components while opening each one no-follow."""
    absolute = _absolute_lexical(path)
    if os.name == "nt":
        drive, tail = os.path.splitdrive(absolute)
        if not drive:
            raise BoundaryError("Windows path must have a drive")
        current = drive + os.sep
        components = [item for item in tail.replace("/", os.sep).split(os.sep) if item]
    else:
        current = os.sep
        components = [item for item in absolute.split(os.sep) if item]
    if os.name != "nt":
        descriptor = _open_directory(os.sep)
        try:
            for component in components:
                current = os.path.join(current, component)
                try:
                    child = os.open(component, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                                    | getattr(os, "O_NOFOLLOW", 0), dir_fd=descriptor)
                except FileNotFoundError:
                    try:
                        os.mkdir(component, 0o755, dir_fd=descriptor)
                    except FileExistsError:
                        pass
                    child = os.open(component, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                                    | getattr(os, "O_NOFOLLOW", 0), dir_fd=descriptor)
                info = os.fstat(child)
                if not stat.S_ISDIR(info.st_mode) or _reparse(info):
                    os.close(child)
                    raise BoundaryError(f"directory component is unsafe: {current}")
                os.close(descriptor)
                descriptor = child
        finally:
            os.close(descriptor)
        return absolute
    for component in components:
        current = os.path.join(current, component)
        try:
            _open_fd = _open_directory(current)
        except FileNotFoundError:
            try:
                os.mkdir(current, 0o755)
            except FileExistsError:
                pass
            _open_fd = _open_directory(current)
        try:
            info = os.fstat(_open_fd)
            if not stat.S_ISDIR(info.st_mode) or _reparse(info):
                raise BoundaryError(f"directory component is unsafe: {current}")
        finally:
            os.close(_open_fd)
    return absolute


def chmod_directory(path: Path | str, mode: int) -> None:
    """Change a directory through its pinned descriptor where the platform permits it."""
    try:
        with pinned_directory(path) as (descriptor, absolute):
            if os.name != "nt":
                os.fchmod(descriptor, mode)
            else:
                # Windows ACL inheritance, not the POSIX mode bits, controls the
                # staging tree.  The directory handle still verifies that the
                # target is a real directory and pins it for the caller.
                _ = absolute
    except BoundaryError:
        raise
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise BoundaryError(f"directory cannot be changed safely: {path}") from exc


def atomic_write(path: Path | str, data: bytes, *, replace: bool = True,
                 mode: int = 0o600, label: str = "output") -> None:
    if not isinstance(data, (bytes, bytearray)):
        raise BoundaryError(f"{label} data is not bytes")
    if len(data) > MAX_FILE_BYTES:
        raise BoundaryError(f"{label} is too large")
    absolute = _absolute_lexical(path)
    ensure_directory(os.path.dirname(absolute) or os.curdir)
    try:
        with _pinned_parent(absolute) as (parent_fd, _):
            try:
                existing_before = os.lstat(absolute)
            except FileNotFoundError:
                existing_before = None
            if existing_before is not None and _reparse(existing_before):
                raise BoundaryError(f"{label} is a reparse point")
            try:
                existing = _open_file_at(absolute, parent_fd)
            except FileNotFoundError:
                existing = None
            if existing is not None:
                try:
                    if existing_before is None:
                        raise BoundaryError(f"{label} appeared during publication")
                    _verify_regular(existing, str(path), existing_before)
                finally:
                    os.close(existing)
                if not replace:
                    raise BoundaryError(f"{label} already exists")
            temporary = ""
            fd = -1
            committed = False
            if os.name == "nt":
                fd, temporary = _win_create_temp(
                    _win_final_path(parent_fd), os.path.basename(absolute))
            else:
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
                for attempt in range(32):
                    temporary = f".{os.path.basename(absolute)}.{os.getpid()}.{attempt}"
                    try:
                        fd = os.open(temporary, flags, 0o600, dir_fd=parent_fd)
                        break
                    except FileExistsError:
                        continue
                else:
                    raise BoundaryError(f"could not allocate temporary {label}")
            try:
                view = memoryview(bytes(data))
                while view:
                    written = os.write(fd, view)
                    if not written:
                        raise OSError("atomic publication made no write progress")
                    view = view[written:]
                os.fsync(fd)
                _verify_regular(fd, str(path))
                if os.name != "nt":
                    os.fchmod(fd, mode)
                else:
                    # Windows exposes the owner-write bit through its read-only
                    # file attribute.  Apply the requested mode while the
                    # same-directory temporary is still private, so runtime
                    # files are non-writable before the atomic publication.
                    os.chmod(temporary, mode)
                if os.name == "nt":
                    _verify_regular(fd, str(path))
                    try:
                        commit_before = os.lstat(absolute)
                    except FileNotFoundError:
                        commit_before = None
                    if (existing_before is None) != (commit_before is None):
                        raise BoundaryError(f"{label} changed before publication")
                    if commit_before is not None:
                        commit_fd = _open_file_at(absolute, parent_fd)
                        try:
                            _verify_regular(commit_fd, str(path), commit_before)
                        finally:
                            os.close(commit_fd)
                    _win_rename_by_handle(fd, parent_fd, os.path.basename(absolute),
                                          replace=replace)
                    committed = True
                else:
                    # Re-open and verify the destination immediately before the
                    # directory-handle-relative commit.  A missing target uses
                    # link+noreplace below, so a concurrent creator can only make
                    # the commit fail; an existing target must retain its identity.
                    try:
                        commit_before = os.lstat(absolute)
                    except FileNotFoundError:
                        commit_before = None
                    if (existing_before is None) != (commit_before is None):
                        raise BoundaryError(f"{label} changed before publication")
                    if commit_before is not None:
                        commit_fd = _open_file_at(absolute, parent_fd)
                        try:
                            _verify_regular(commit_fd, str(path), commit_before)
                        finally:
                            os.close(commit_fd)
                    if replace:
                        os.rename(temporary, os.path.basename(absolute),
                                  src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
                    else:
                        # link()+unlink() is the POSIX equivalent of rename-noreplace:
                        # the destination is never overwritten after the initial check.
                        os.link(temporary, os.path.basename(absolute),
                                src_dir_fd=parent_fd, dst_dir_fd=parent_fd,
                                follow_symlinks=False)
                        os.unlink(temporary, dir_fd=parent_fd)
                    committed = True
                _verify_regular(fd, str(path))
                if os.name != "nt":
                    os.fsync(parent_fd)
            finally:
                if fd >= 0:
                    try:
                        os.close(fd)
                    except OSError:
                        pass
                try:
                    if temporary and not committed and os.name == "nt":
                        os.unlink(temporary)
                    elif temporary and not committed:
                        os.unlink(temporary, dir_fd=parent_fd)
                except FileNotFoundError:
                    pass
    except BoundaryError:
        raise
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise BoundaryError(f"could not publish {label}") from exc


def copy_regular(source: Path | str, destination: Path | str, *, mode: int = 0o444) -> None:
    atomic_write(destination, read_bytes(source, label="runtime source"), replace=False,
                 mode=mode, label="runtime destination")

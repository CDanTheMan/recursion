#!/usr/bin/env python3
"""Crash-safe JSONL validation and append helpers.

Callers remain responsible for holding the journal's existing serialization lock.  This
module deliberately does not acquire taskctl.lock: discovering a damaged tail while that
lock is already held must still be able to preserve durable evidence without deadlocking.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import stat
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - production is Linux; Windows tests are sequential.
    fcntl = None  # type: ignore[assignment]


DEFAULT_MAX_RECORD_BYTES = 4 * 1024 * 1024
COPY_CHUNK_BYTES = 1024 * 1024
INDEX_SCHEMA_VERSION = 1
INDEX_AUTHORITY = "jsonl-verification-index-v1"
ZERO_CHAIN_SHA256 = "0" * 64


class JsonlDurabilityError(RuntimeError):
    """The existing journal cannot safely accept or expose another record."""


class _MissingDirectory(JsonlDurabilityError):
    """A read-only pin found no parent chain; this is distinct from an unsafe chain."""


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


def _lexical_absolute(path: Path) -> Path:
    """Make a path absolute without resolving any link or reparse point."""
    path = Path(path)
    return path if path.is_absolute() else Path.cwd() / path


def _same_identity(left: os.stat_result, right: os.stat_result) -> bool:
    return (int(left.st_dev), int(left.st_ino)) == (int(right.st_dev), int(right.st_ino))


def _relative_directory_open_supported() -> bool:
    return os.open in getattr(os, "supports_dir_fd", set()) and \
        os.stat in getattr(os, "supports_dir_fd", set())


def _directory_open_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0))


def _directory_create_mode() -> int:
    # The mode argument is an ACL request on this Windows host; 0o700 creates a directory
    # that even its creating process cannot reopen.  POSIX keeps the least-privilege mode.
    return 0o777 if os.name == "nt" else 0o700


def _verify_directory_descriptor(descriptor: int) -> os.stat_result:
    try:
        info = os.fstat(descriptor)
    except OSError:
        raise JsonlDurabilityError("JSONL parent directory could not be inspected safely") from None
    if not stat.S_ISDIR(info.st_mode):
        raise JsonlDurabilityError("JSONL parent path is not a directory")
    if bool(getattr(info, "st_file_attributes", 0) & 0x400):
        raise JsonlDurabilityError("JSONL parent directory is a reparse point")
    return info


def _is_reparse_directory(path: Path, info: os.stat_result) -> bool:
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & 0x400)


class _PinnedDirectory:
    """A directory chain held open so later leaf operations cannot follow a swapped ancestor."""

    def __init__(self, path: Path, *, create: bool = True) -> None:
        self.path = _lexical_absolute(path)
        self.create = create
        self.descriptor: int | None = None
        self._fds: list[int] = []
        self._components: list[tuple[int, str, int, tuple[int, int]]] = []
        self._relative = _relative_directory_open_supported()

    def __enter__(self) -> "_PinnedDirectory":
        try:
            if self._relative:
                current = os.open(self.path.anchor, _directory_open_flags())
                self._fds.append(current)
                for name in self.path.parts[1:]:
                    try:
                        child = os.open(name, _directory_open_flags(), dir_fd=current)
                    except FileNotFoundError:
                        if not self.create:
                            raise _MissingDirectory("JSONL parent directory is absent") from None
                        created = False
                        try:
                            os.mkdir(name, _directory_create_mode(), dir_fd=current)
                            created = True
                        except FileExistsError:
                            pass
                        if created and os.name != "nt":
                            os.fsync(current)
                        child = os.open(name, _directory_open_flags(), dir_fd=current)
                    child_info = _verify_directory_descriptor(child)
                    entry_info = os.stat(name, dir_fd=current, follow_symlinks=False)
                    if not _same_identity(child_info, entry_info):
                        os.close(child)
                        raise JsonlDurabilityError(
                            "JSONL parent directory changed while it was being opened"
                        )
                    self._components.append(
                        (current, name, child, (int(child_info.st_dev), int(child_info.st_ino)))
                    )
                    self._fds.append(child)
                    current = child
                self.descriptor = current
            else:
                current = Path(self.path.anchor)
                for name in self.path.parts[1:]:
                    current /= name
                    try:
                        info = current.lstat()
                    except FileNotFoundError:
                        if not self.create:
                            raise _MissingDirectory("JSONL parent directory is absent") from None
                        try:
                            current.mkdir(mode=_directory_create_mode())
                        except FileExistsError:
                            pass
                        info = current.lstat()
                    if _is_reparse_directory(current, info) or not stat.S_ISDIR(info.st_mode):
                        raise JsonlDurabilityError("JSONL parent directory is unsafe")
                self.descriptor = None
            self.verify()
            return self
        except BaseException as exc:
            self.close()
            if isinstance(exc, JsonlDurabilityError):
                raise
            raise JsonlDurabilityError("JSONL parent directory could not be opened safely") from None

    def __exit__(self, *_: object) -> bool:
        self.close()
        return False

    def verify(self) -> None:
        if self._relative:
            assert self.descriptor is not None
            for parent, name, child, identity in self._components:
                child_info = _verify_directory_descriptor(child)
                try:
                    entry_info = os.stat(name, dir_fd=parent, follow_symlinks=False)
                except OSError:
                    raise JsonlDurabilityError(
                        "JSONL parent directory changed after it was opened"
                    ) from None
                if (int(child_info.st_dev), int(child_info.st_ino)) != identity \
                        or not _same_identity(child_info, entry_info):
                    raise JsonlDurabilityError(
                        "JSONL parent directory changed after it was opened"
                    )
            _verify_directory_descriptor(self.descriptor)
            return
        current = Path(self.path.anchor)
        for name in self.path.parts[1:]:
            current /= name
            try:
                info = current.lstat()
            except OSError:
                raise JsonlDurabilityError(
                    "JSONL parent directory changed after it was opened"
                ) from None
            if _is_reparse_directory(current, info) or not stat.S_ISDIR(info.st_mode):
                raise JsonlDurabilityError("JSONL parent directory changed after it was opened")

    def open_leaf(self, name: str, flags: int, mode: int = 0o600) -> int:
        self.verify()
        try:
            if self._relative:
                assert self.descriptor is not None
                return os.open(name, flags, mode, dir_fd=self.descriptor)
            return os.open(self.path / name, flags, mode)
        except OSError:
            raise JsonlDurabilityError("JSONL journal leaf could not be opened safely") from None

    def leaf_stat(self, name: str) -> os.stat_result | None:
        try:
            if self._relative:
                assert self.descriptor is not None
                return os.stat(name, dir_fd=self.descriptor, follow_symlinks=False)
            return (self.path / name).lstat()
        except FileNotFoundError:
            return None
        except OSError:
            raise JsonlDurabilityError("JSONL journal leaf could not be inspected safely") from None

    def fsync(self) -> None:
        if os.name == "nt" or self.descriptor is None:
            return
        os.fsync(self.descriptor)

    def close(self) -> None:
        for descriptor in reversed(self._fds):
            try:
                os.close(descriptor)
            except OSError:
                pass
        self._fds.clear()
        self.descriptor = None


def _before_journal_leaf_open(_path: Path) -> None:
    """Test seam for the exact check-to-open window; production has no side effect."""


def _create_relative_temp(parent: _PinnedDirectory, prefix: str, mode: int = 0o600) \
        -> tuple[int, str]:
    if not parent._relative:
        try:
            descriptor, name = tempfile.mkstemp(prefix=prefix, dir=str(parent.path))
        except OSError:
            raise JsonlDurabilityError("JSONL temporary file could not be created safely") from None
        return descriptor, Path(name).name
    assert parent.descriptor is not None
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    generator = getattr(tempfile, "_get_candidate_names")()
    for _attempt in range(100):
        name = prefix + next(generator)
        try:
            return os.open(name, flags, mode, dir_fd=parent.descriptor), name
        except FileExistsError:
            continue
        except OSError:
            break
    raise JsonlDurabilityError("JSONL temporary file could not be created safely")


def _replace_relative(parent: _PinnedDirectory, temporary: str, target: str) -> None:
    parent.verify()
    try:
        if parent._relative:
            assert parent.descriptor is not None
            os.replace(temporary, target, src_dir_fd=parent.descriptor, dst_dir_fd=parent.descriptor)
        else:
            os.replace(parent.path / temporary, parent.path / target)
    except OSError:
        raise JsonlDurabilityError("JSONL durable replacement could not be completed safely") from None
    parent.verify()


def _unlink_relative(parent: _PinnedDirectory, name: str) -> None:
    try:
        if parent._relative:
            assert parent.descriptor is not None
            os.unlink(name, dir_fd=parent.descriptor)
        else:
            os.unlink(parent.path / name)
    except FileNotFoundError:
        return
    except OSError:
        raise JsonlDurabilityError("JSONL temporary file cleanup failed") from None


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _fsync_dir(path: Path, descriptor: int | None = None) -> None:
    if os.name == "nt":
        return
    close_descriptor = descriptor is None
    if descriptor is None:
        descriptor = os.open(path, _directory_open_flags())
    try:
        os.fsync(descriptor)
    finally:
        if close_descriptor:
            os.close(descriptor)


def _write_all(descriptor: int, value: bytes) -> None:
    view = memoryview(value)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("JSONL write made no progress")
        view = view[written:]


def _verify_journal_descriptor(descriptor: int,
                               expected_identity: tuple[int, int] | None = None,
                               parent: _PinnedDirectory | None = None,
                               leaf_name: str | None = None) \
        -> tuple[int, int]:
    """Authenticate the leaf and, when supplied, its current pinned pathname."""
    try:
        info = os.fstat(descriptor)
    except OSError:
        raise JsonlDurabilityError("JSONL journal leaf could not be inspected safely") from None
    identity = (int(info.st_dev), int(info.st_ino))
    if not stat.S_ISREG(info.st_mode) or int(getattr(info, "st_nlink", 0)) != 1:
        raise JsonlDurabilityError("JSONL journal leaf is not a single-link regular file")
    if expected_identity is not None and identity != expected_identity:
        raise JsonlDurabilityError("JSONL journal identity changed before append")
    if parent is not None and leaf_name is not None:
        parent.verify()
        try:
            current = parent.leaf_stat(leaf_name)
        except JsonlDurabilityError:
            raise JsonlDurabilityError("JSONL journal pathname changed after it was opened") from None
        if current is None or not stat.S_ISREG(current.st_mode) \
                or int(getattr(current, "st_nlink", 0)) != 1 \
                or not _same_identity(info, current):
            raise JsonlDurabilityError("JSONL journal pathname changed after it was opened")
    return identity


def _open_journal_leaf(path: Path, flags: int, mode: int = 0o600,
                       parent: _PinnedDirectory | None = None) \
        -> tuple[int, tuple[int, int]]:
    owned_parent = parent is None
    if owned_parent:
        parent = _PinnedDirectory(path.parent)
        parent.__enter__()
    assert parent is not None
    leaf_name = Path(path).name
    try:
        parent.verify()
        expected_leaf = parent.leaf_stat(leaf_name)
        _before_journal_leaf_open(path)
        descriptor = parent.open_leaf(leaf_name, flags, mode)
    except BaseException:
        if owned_parent:
            parent.close()
        raise
    try:
        identity = _verify_journal_descriptor(descriptor, parent=parent, leaf_name=leaf_name)
        current_leaf = parent.leaf_stat(leaf_name)
        if expected_leaf is not None and (
                current_leaf is None or not _same_identity(expected_leaf, current_leaf)
        ):
            raise JsonlDurabilityError("JSONL journal pathname changed before it was opened")
        if expected_leaf is None and current_leaf is None:
            raise JsonlDurabilityError("JSONL journal pathname disappeared after it was opened")
    except BaseException:
        os.close(descriptor)
        if owned_parent:
            parent.close()
        raise
    if owned_parent:
        # The caller only gets an unlinked-handle-style guarantee on platforms without dir_fd;
        # POSIX callers that need continued pathname checks pass their parent explicitly.
        parent.close()
    return descriptor, identity


def _journal_leaf_exists(path: Path) -> bool:
    """Check one journal leaf without following its parent chain or a final link."""
    try:
        with _PinnedDirectory(path.parent, create=False) as parent:
            info = parent.leaf_stat(path.name)
            if info is None:
                return False
            if (not stat.S_ISREG(info.st_mode)
                    or int(getattr(info, "st_nlink", 0)) != 1
                    or bool(getattr(info, "st_file_attributes", 0) & 0x400)):
                raise JsonlDurabilityError("JSONL journal leaf is not a single-link regular file")
            return True
    except _MissingDirectory:
        return False


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
    except ValueError:
        attempts = 100
    try:
        delay = max(0.0, float(os.environ.get("RECURSION_JSONL_LOCK_DELAY_S", "0.01")))
    except ValueError:
        delay = 0.01
    for attempt in range(attempts):
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            if attempt + 1 < attempts:
                time.sleep(delay)
    raise JsonlDurabilityError("JSONL journal lock is contended; refusing an unlocked append")


def _atomic_bytes(path: Path, value: bytes, mode: int = 0o600) -> None:
    with _PinnedDirectory(path.parent) as parent:
        existing = parent.leaf_stat(path.name)
        if existing is not None and (
                stat.S_ISLNK(existing.st_mode) or not stat.S_ISREG(existing.st_mode)
                or int(getattr(existing, "st_nlink", 1)) != 1):
            raise JsonlDurabilityError("JSONL durable artifact has an unsafe type")
        descriptor, temporary = _create_relative_temp(
            parent, f".{path.name}.tmp.", mode
        )
        try:
            if hasattr(os, "fchmod"):  # absent on Windows; NTFS mode bits are meaningless
                os.fchmod(descriptor, mode)
            with os.fdopen(descriptor, "wb") as output:
                _write_all(output.fileno(), value)
                output.flush()
                os.fsync(output.fileno())
            _replace_relative(parent, temporary, path.name)
            _fsync_dir(path.parent, parent.descriptor)
        except BaseException:
            try:
                os.close(descriptor)
            except OSError:
                pass
            try:
                _unlink_relative(parent, temporary)
            except (OSError, JsonlDurabilityError):
                pass
            raise


def _journal_identity(path: Path) -> tuple[Path, str]:
    # This identity is derived from the already-pinned lexical name.  Resolving here would
    # follow a pathname swap after the descriptor checks and could bind evidence to an attacker
    # controlled target rather than to the journal that was authenticated.
    lexical = _lexical_absolute(path)
    for parent in (lexical.parent, *lexical.parents):
        if parent.name == "state":
            try:
                relative = lexical.relative_to(parent.parent).as_posix()
            except ValueError:
                break
            return parent / "jsonl-quarantine", relative
    return lexical.parent / "jsonl-quarantine", lexical.name


def _index_identity(path: Path) -> tuple[Path, str]:
    """Return the derived-cache directory and stable journal identity."""
    lexical = _lexical_absolute(path)
    for parent in (lexical.parent, *lexical.parents):
        if parent.name == "state":
            try:
                relative = lexical.relative_to(parent.parent).as_posix()
            except ValueError:
                break
            return parent / "jsonl-index", relative
    return lexical.parent / "jsonl-index", lexical.name


def _ensure_index_root(path: Path) -> tuple[Path, str]:
    root, identity = _index_identity(path)
    with _PinnedDirectory(root) as pinned:
        pinned.verify()
        try:
            if os.name != "nt" and pinned.descriptor is not None:
                os.fchmod(pinned.descriptor, 0o700)
            elif os.name != "nt":
                os.chmod(root, 0o700)
        except OSError:
            pass
        parent_fd = pinned._components[-1][0] if pinned._components else pinned.descriptor
        _fsync_dir(root.parent, parent_fd)
    return root, identity


def _index_path(path: Path) -> tuple[Path, str]:
    root, identity = _ensure_index_root(path)
    name = hashlib.sha256(identity.encode("utf-8")).hexdigest() + ".sqlite3"
    candidate = root / name
    with _PinnedDirectory(candidate.parent) as pinned:
        existing = pinned.leaf_stat(candidate.name)
        if existing is not None and (
                stat.S_ISLNK(existing.st_mode) or not stat.S_ISREG(existing.st_mode)
                or int(getattr(existing, "st_nlink", 1)) != 1):
            raise JsonlDurabilityError("JSONL index has an unsafe type")
    return candidate, identity


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


def _quarantine_tail(path: Path, descriptor: int, offset: int, size: int) -> dict:
    quarantine, journal_name = _journal_identity(path)
    with _PinnedDirectory(quarantine) as quarantine_dir:
        parent_fd = quarantine_dir._components[-1][0] if quarantine_dir._components \
            else quarantine_dir.descriptor
        _fsync_dir(quarantine.parent, parent_fd)

        digest = hashlib.sha256()
        cursor = offset
        payload_fd, payload_tmp = _create_relative_temp(quarantine_dir, ".jsonl-tail.tmp.")
        temporary_exists = True
        try:
            if hasattr(os, "fchmod"):  # absent on Windows; NTFS mode bits are meaningless
                os.fchmod(payload_fd, 0o600)
            while cursor < size:
                chunk = _read_at(descriptor, min(COPY_CHUNK_BYTES, size - cursor), cursor)
                if not chunk:
                    raise OSError("short JSONL quarantine read")
                digest.update(chunk)
                _write_all(payload_fd, chunk)
                cursor += len(chunk)
            os.fsync(payload_fd)
            os.close(payload_fd)
            payload_fd = -1

            tail_sha = digest.hexdigest()
            safe_name = (re.sub(r"[^A-Za-z0-9._-]+", "_", journal_name).strip("._")
                         or "journal")[:96]
            stem = f"{safe_name}-offset-{offset}-{tail_sha}"
            payload_name = f"{stem}.bin"
            metadata_name = f"{stem}.json"
            existing = quarantine_dir.leaf_stat(payload_name)
            if existing is not None:
                if (not stat.S_ISREG(existing.st_mode)
                        or int(getattr(existing, "st_nlink", 1)) != 1):
                    raise JsonlDurabilityError("JSONL quarantine payload has an unsafe type")
                existing_digest = hashlib.sha256()
                existing_fd = quarantine_dir.open_leaf(
                    payload_name, os.O_RDONLY | getattr(os, "O_BINARY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                )
                with os.fdopen(existing_fd, "rb") as current:
                    for chunk in iter(lambda: current.read(COPY_CHUNK_BYTES), b""):
                        existing_digest.update(chunk)
                if (existing_digest.hexdigest() != tail_sha
                        or existing.st_size != size - offset):
                    raise JsonlDurabilityError("JSONL quarantine payload conflicts")
                _unlink_relative(quarantine_dir, payload_tmp)
                temporary_exists = False
            else:
                _replace_relative(quarantine_dir, payload_tmp, payload_name)
                temporary_exists = False
                _fsync_dir(quarantine, quarantine_dir.descriptor)
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
                "payload": payload_name,
                "quarantined_at": _now_iso(),
                "requires_human_review": True,
            }
            encoded = (json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n").encode()
            prior_stat = quarantine_dir.leaf_stat(metadata_name)
            if prior_stat is not None:
                if (not stat.S_ISREG(prior_stat.st_mode)
                        or int(getattr(prior_stat, "st_nlink", 1)) != 1):
                    raise JsonlDurabilityError("JSONL quarantine metadata has an unsafe type")
                prior_fd = quarantine_dir.open_leaf(
                    metadata_name, os.O_RDONLY | getattr(os, "O_BINARY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                )
                with os.fdopen(prior_fd, "r", encoding="utf-8") as current:
                    try:
                        prior = json.load(current)
                    except (OSError, json.JSONDecodeError):
                        raise JsonlDurabilityError("JSONL quarantine metadata is unreadable") from None
                immutable = ("kind", "journal", "journal_offset", "original_bytes", "tail_bytes",
                             "tail_sha256", "payload")
                if any(prior.get(key) != evidence.get(key) for key in immutable):
                    raise JsonlDurabilityError("JSONL quarantine metadata conflicts")
                evidence = prior
            else:
                _atomic_bytes(quarantine / metadata_name, encoded)
            return evidence
        except BaseException:
            if payload_fd >= 0:
                try:
                    os.close(payload_fd)
                except OSError:
                    pass
            if temporary_exists:
                try:
                    _unlink_relative(quarantine_dir, payload_tmp)
                except (OSError, JsonlDurabilityError):
                    pass
            raise


def _iter_complete_lines(descriptor: int, limit: int, path: Path,
                         max_record_bytes: int) -> Iterator[VerifiedLine]:
    """Stream and validate physical lines up to *limit* with bounded memory."""
    with os.fdopen(os.dup(descriptor), "rb", closefd=True) as source:
        source.seek(0)
        remaining = limit
        line_number = 0
        offset = 0
        chain = ZERO_CHAIN_SHA256
        while remaining:
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
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
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
    connection.executescript(
        """
        PRAGMA journal_mode=DELETE;
        PRAGMA synchronous=FULL;
        PRAGMA foreign_keys=ON;
        CREATE TABLE metadata (
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
        );
        CREATE TABLE records (
            sequence INTEGER PRIMARY KEY,
            start_offset INTEGER NOT NULL UNIQUE,
            end_offset INTEGER NOT NULL UNIQUE,
            raw BLOB NOT NULL,
            raw_sha256 TEXT NOT NULL,
            chain_sha256 TEXT NOT NULL,
            value_json TEXT,
            object_id_json TEXT
        );
        CREATE INDEX records_object_id ON records(object_id_json);
        CREATE TABLE consumers (
            name TEXT PRIMARY KEY,
            end_offset INTEGER NOT NULL,
            chain_sha256 TEXT NOT NULL
        );
        """
    )
    connection.execute(f"PRAGMA user_version={INDEX_SCHEMA_VERSION}")


def _stat_fields(stat_result: os.stat_result) -> tuple[str, str, int, int, int]:
    return (
        str(stat_result.st_dev), str(stat_result.st_ino), int(stat_result.st_size),
        int(stat_result.st_mtime_ns), int(stat_result.st_ctime_ns),
    )


def _metadata(connection: sqlite3.Connection) -> tuple | None:
    return connection.execute(
        "SELECT schema_version,authority,journal_identity,max_record_bytes,device,inode,size,"
        "mtime_ns,ctime_ns,line_count,chain_sha256 FROM metadata WHERE singleton=1"
    ).fetchone()


def _index_matches(connection: sqlite3.Connection, identity: str, stat_result: os.stat_result,
                   max_record_bytes: int) -> bool:
    if connection.execute("PRAGMA user_version").fetchone()[0] != INDEX_SCHEMA_VERSION:
        return False
    row = _metadata(connection)
    if row is None:
        return False
    expected = (
        INDEX_SCHEMA_VERSION, INDEX_AUTHORITY, identity, max_record_bytes,
        *_stat_fields(stat_result)
    )
    if row[:9] != expected:
        return False
    line_count, chain = int(row[9]), str(row[10])
    summary = connection.execute(
        "SELECT COUNT(*),COALESCE(MIN(start_offset),0),COALESCE(MAX(end_offset),0),"
        "COALESCE(MAX(sequence),0) FROM records"
    ).fetchone()
    if summary != (line_count, 0, int(stat_result.st_size), line_count):
        return False
    if line_count:
        last = connection.execute(
            "SELECT chain_sha256 FROM records WHERE sequence=?", (line_count,)
        ).fetchone()
        if last is None or last[0] != chain:
            return False
    elif chain != ZERO_CHAIN_SHA256 or stat_result.st_size != 0:
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
    connection.execute(
        "INSERT INTO records(sequence,start_offset,end_offset,raw,raw_sha256,chain_sha256,"
        "value_json,object_id_json) VALUES(?,?,?,?,?,?,?,?)",
        (
            sequence, line.start, line.end, sqlite3.Binary(line.raw),
            hashlib.sha256(line.raw).hexdigest(), line.chain_sha256,
            value_json, object_id_json,
        ),
    )


def _write_metadata(connection: sqlite3.Connection, identity: str, stat_result: os.stat_result,
                    max_record_bytes: int, line_count: int, chain_sha256: str) -> None:
    connection.execute("DELETE FROM metadata")
    connection.execute(
        "INSERT INTO metadata VALUES(1,?,?,?,?,?,?,?,?,?,?,?)",
        (
            INDEX_SCHEMA_VERSION, INDEX_AUTHORITY, identity, max_record_bytes,
            *_stat_fields(stat_result), line_count, chain_sha256,
        ),
    )


def _rebuild_index(index_path: Path, identity: str, descriptor: int,
                   stat_result: os.stat_result,
                   journal: Path, max_record_bytes: int,
                   journal_parent: _PinnedDirectory | None = None,
                   journal_identity: tuple[int, int] | None = None) -> None:
    with _PinnedDirectory(index_path.parent) as parent:
        temporary_fd, temporary_name = _create_relative_temp(
            parent, f".{index_path.name}.tmp."
        )
        temporary = parent.path / temporary_name
        os.close(temporary_fd)
        connection: sqlite3.Connection | None = None
        try:
            if journal_parent is not None and journal_identity is not None:
                _verify_journal_descriptor(
                    descriptor, journal_identity, journal_parent, journal.name
                )
            parent.verify()
            connection = sqlite3.connect(temporary)
            parent.verify()
            _create_index_schema(connection)
            connection.execute("BEGIN IMMEDIATE")
            line_count = 0
            chain = ZERO_CHAIN_SHA256
            for line_count, line in enumerate(
                    _iter_complete_lines(descriptor, stat_result.st_size, journal,
                                         max_record_bytes), 1):
                _insert_line(connection, line_count, line)
                chain = line.chain_sha256
            if journal_parent is not None and journal_identity is not None:
                _verify_journal_descriptor(
                    descriptor, journal_identity, journal_parent, journal.name
                )
            _write_metadata(
                connection, identity, stat_result, max_record_bytes, line_count, chain
            )
            connection.commit()
            connection.close()
            connection = None
            cache_fd = parent.open_leaf(
                temporary_name, os.O_RDWR | getattr(os, "O_BINARY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
            )
            try:
                os.fsync(cache_fd)
            finally:
                os.close(cache_fd)
            _replace_relative(parent, temporary_name, index_path.name)
            _fsync_dir(index_path.parent, parent.descriptor)
        except BaseException:
            if connection is not None:
                connection.close()
            try:
                _unlink_relative(parent, temporary_name)
            except (OSError, JsonlDurabilityError):
                pass
            raise


def _open_verified_index(path: Path, descriptor: int, size: int,
                         max_record_bytes: int,
                         journal_parent: _PinnedDirectory | None = None,
                         journal_identity: tuple[int, int] | None = None) \
        -> tuple[sqlite3.Connection, bool]:
    if journal_parent is not None and journal_identity is not None:
        _verify_journal_descriptor(descriptor, journal_identity, journal_parent, path.name)
    journal_stat = os.fstat(descriptor)
    if journal_stat.st_size != size:
        raise JsonlDurabilityError(f"JSONL size changed while opening verification index: {path}")
    index_path, identity = _index_path(path)
    with _PinnedDirectory(index_path.parent) as index_parent:
        existing = index_parent.leaf_stat(index_path.name)
        if existing is not None:
            if (stat.S_ISLNK(existing.st_mode) or not stat.S_ISREG(existing.st_mode)
                    or int(getattr(existing, "st_nlink", 1)) != 1):
                raise JsonlDurabilityError("JSONL index has an unsafe type")
            expected_index = existing
            connection: sqlite3.Connection | None = None
            try:
                connection = sqlite3.connect(index_path)
                index_parent.verify()
                current_index = index_parent.leaf_stat(index_path.name)
                if current_index is None or not _same_identity(expected_index, current_index):
                    raise JsonlDurabilityError("JSONL index pathname changed while opening")
                connection.execute("PRAGMA query_only=ON")
                if _index_matches(connection, identity, journal_stat, max_record_bytes):
                    connection.execute("PRAGMA query_only=OFF")
                    retained = connection
                    connection = None
                    return retained, False
            except sqlite3.DatabaseError:
                pass
            finally:
                if connection is not None:
                    connection.close()
    _rebuild_index(index_path, identity, descriptor, journal_stat, path, max_record_bytes,
                   journal_parent, journal_identity)
    with _PinnedDirectory(index_path.parent) as index_parent:
        rebuilt_index = index_parent.leaf_stat(index_path.name)
        if (rebuilt_index is None or stat.S_ISLNK(rebuilt_index.st_mode)
                or not stat.S_ISREG(rebuilt_index.st_mode)
                or int(getattr(rebuilt_index, "st_nlink", 1)) != 1):
            raise JsonlDurabilityError("rebuilt JSONL verification index has an unsafe type")
        connection = sqlite3.connect(index_path)
        try:
            index_parent.verify()
            current_index = index_parent.leaf_stat(index_path.name)
            if current_index is None or not _same_identity(rebuilt_index, current_index):
                connection.close()
                raise JsonlDurabilityError("rebuilt JSONL index pathname changed while opening")
        except BaseException:
            connection.close()
            raise
    if not _index_matches(connection, identity, journal_stat, max_record_bytes):
        connection.close()
        raise JsonlDurabilityError(f"rebuilt JSONL verification index is inconsistent: {path}")
    if journal_parent is not None and journal_identity is not None:
        _verify_journal_descriptor(descriptor, journal_identity, journal_parent, path.name)
    return connection, True


def _rows_to_lines(rows: Iterator[tuple]) -> tuple[VerifiedLine, ...]:
    result: list[VerifiedLine] = []
    for sequence, start, end, raw, value_json, chain in rows:
        value = json.loads(value_json) if value_json is not None else None
        if value is not None and not isinstance(value, dict):
            raise JsonlDurabilityError("JSONL verification index contains a non-object value")
        result.append(VerifiedLine(
            sequence=int(sequence), start=int(start), end=int(end), raw=bytes(raw), value=value,
            chain_sha256=str(chain),
        ))
    return tuple(result)


def _verified_descriptor(path: Path, max_record_bytes: int) \
        -> tuple[int, sqlite3.Connection, bool, _PinnedDirectory] | None:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    parent = _PinnedDirectory(path.parent, create=False)
    try:
        parent.__enter__()
    except _MissingDirectory:
        return None
    descriptor: int | None = None
    connection: sqlite3.Connection | None = None
    try:
        if parent.leaf_stat(path.name) is None:
            parent.close()
            return None
        descriptor, identity = _open_journal_leaf(path, flags, parent=parent)
        _lock_descriptor(descriptor)
        size = os.fstat(descriptor).st_size
        if size and _read_at(descriptor, 1, size - 1) != b"\n":
            raise JsonlDurabilityError(f"unterminated JSONL tail: {path}")
        connection, rebuilt = _open_verified_index(
            path, descriptor, size, max_record_bytes, parent, identity
        )
        _verify_journal_descriptor(descriptor, identity, parent, path.name)
        return descriptor, connection, rebuilt, parent
    except BaseException:
        if connection is not None:
            connection.close()
        if descriptor is not None:
            os.close(descriptor)
        parent.close()
        raise


def read_jsonl_objects(path: Path, max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> list[dict]:
    """Read objects from an intact journal through its verified derived index."""
    verified = _verified_descriptor(path, max_record_bytes)
    if verified is None:
        return []
    descriptor, connection, _rebuilt, parent = verified
    try:
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
        rows = connection.execute(
            "SELECT value_json FROM records WHERE value_json IS NOT NULL ORDER BY sequence"
        )
        values = [json.loads(row[0]) for row in rows]
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
        return values
    finally:
        connection.close()
        os.close(descriptor)
        parent.close()


def read_jsonl_prefix(path: Path, count: int,
                      max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> tuple[VerifiedLine, ...]:
    """Return at most *count* verified physical lines from the journal prefix."""
    if count < 0:
        raise JsonlDurabilityError("JSONL prefix count cannot be negative")
    if count == 0:
        return ()
    verified = _verified_descriptor(path, max_record_bytes)
    if verified is None:
        return ()
    descriptor, connection, _rebuilt, parent = verified
    try:
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
        rows = connection.execute(
            "SELECT sequence,start_offset,end_offset,raw,value_json,chain_sha256 FROM records "
            "ORDER BY sequence LIMIT ?", (count,),
        )
        lines = _rows_to_lines(rows)
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
        return lines
    finally:
        connection.close()
        os.close(descriptor)
        parent.close()


def find_jsonl_objects(path: Path, field: str, value: object,
                       max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> list[dict]:
    """Find exact top-level field matches without rescanning verified journal bytes."""
    verified = _verified_descriptor(path, max_record_bytes)
    if verified is None:
        return []
    descriptor, connection, _rebuilt, parent = verified
    try:
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
        if field == "id":
            encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
            rows = connection.execute(
                "SELECT value_json FROM records WHERE object_id_json=? ORDER BY sequence",
                (encoded,),
            )
            values = [json.loads(row[0]) for row in rows]
            _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
            return values
        result = []
        for row in connection.execute(
                "SELECT value_json FROM records WHERE value_json IS NOT NULL ORDER BY sequence"):
            candidate = json.loads(row[0])
            if candidate.get(field) == value:
                result.append(candidate)
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
        return result
    finally:
        connection.close()
        os.close(descriptor)
        parent.close()


def _chain_at(connection: sqlite3.Connection, offset: int) -> str | None:
    if offset == 0:
        return ZERO_CHAIN_SHA256
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
    if not consumer or len(consumer) > 128:
        raise JsonlDurabilityError("invalid JSONL index consumer")
    verified = _verified_descriptor(path, max_record_bytes)
    if verified is None:
        return IndexedBatch((), 0, ZERO_CHAIN_SHA256, False)
    descriptor, connection, rebuilt, parent = verified
    try:
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
        checkpoint = connection.execute(
            "SELECT end_offset,chain_sha256 FROM consumers WHERE name=?", (consumer,)
        ).fetchone()
        offset = int(checkpoint[0]) if checkpoint is not None else 0
        expected_chain = str(checkpoint[1]) if checkpoint is not None else ZERO_CHAIN_SHA256
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
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
        return IndexedBatch(lines, int(metadata[6]), str(metadata[10]), rebuilt)
    finally:
        connection.close()
        os.close(descriptor)
        parent.close()


def acknowledge_jsonl(path: Path, consumer: str, batch: IndexedBatch,
                      max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> None:
    """Durably advance a consumer after its selected projections are durable."""
    if not consumer or len(consumer) > 128:
        raise JsonlDurabilityError("invalid JSONL index consumer")
    verified = _verified_descriptor(path, max_record_bytes)
    if verified is None:
        if batch.verified_size == 0:
            return
        raise JsonlDurabilityError(f"JSONL disappeared before acknowledgement: {path}")
    descriptor, connection, _rebuilt, parent = verified
    try:
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
        if _chain_at(connection, batch.verified_size) != batch.chain_sha256:
            raise JsonlDurabilityError(
                f"JSONL changed before consumer acknowledgement: {consumer}"
            )
        current = connection.execute(
            "SELECT end_offset,chain_sha256 FROM consumers WHERE name=?", (consumer,)
        ).fetchone()
        if current is not None and int(current[0]) > batch.verified_size:
            return
        if current is not None and int(current[0]) == batch.verified_size \
                and str(current[1]) != batch.chain_sha256:
            raise JsonlDurabilityError(f"JSONL consumer checkpoint collision: {consumer}")
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO consumers(name,end_offset,chain_sha256) VALUES(?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET end_offset=excluded.end_offset,"
            "chain_sha256=excluded.chain_sha256",
            (consumer, batch.verified_size, batch.chain_sha256),
        )
        connection.commit()
        _verify_journal_descriptor(descriptor, parent=parent, leaf_name=path.name)
    except sqlite3.DatabaseError as exc:
        connection.rollback()
        raise JsonlDurabilityError(f"cannot acknowledge JSONL consumer {consumer}: {exc}") from exc
    finally:
        connection.close()
        os.close(descriptor)
        parent.close()


def _duplicate_in_index(connection: sqlite3.Connection, field: str | None,
                        value: object) -> bool:
    if field is None:
        return False
    if field == "id":
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
        return connection.execute(
            "SELECT 1 FROM records WHERE object_id_json=? LIMIT 1", (encoded,)
        ).fetchone() is not None
    for row in connection.execute(
            "SELECT value_json FROM records WHERE value_json IS NOT NULL ORDER BY sequence"):
        if json.loads(row[0]).get(field) == value:
            return True
    return False


def _update_index_after_append(connection: sqlite3.Connection, descriptor: int, path: Path,
                               encoded: bytes, max_record_bytes: int) -> None:
    metadata = _metadata(connection)
    if metadata is None:
        raise JsonlDurabilityError(f"JSONL verification metadata is absent: {path}")
    old_size = int(metadata[6])
    line_count = int(metadata[9])
    prior_chain = str(metadata[10])
    stat_result = os.fstat(descriptor)
    if stat_result.st_size != old_size + len(encoded):
        raise JsonlDurabilityError(f"JSONL size changed during indexed append: {path}")
    try:
        value = json.loads(encoded[:-1].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:  # defensive; caller encoded it.
        raise JsonlDurabilityError(f"new JSONL record cannot be indexed: {path}") from exc
    raw_digest = hashlib.sha256(encoded).digest()
    chain = hashlib.sha256(bytes.fromhex(prior_chain) + raw_digest).hexdigest()
    line = VerifiedLine(line_count + 1, old_size, stat_result.st_size, encoded, value, chain)
    try:
        connection.execute("BEGIN IMMEDIATE")
        _insert_line(connection, line_count + 1, line)
        _write_metadata(
            connection, str(metadata[2]), stat_result, max_record_bytes, line_count + 1, chain
        )
        connection.commit()
    except sqlite3.DatabaseError as exc:
        connection.rollback()
        raise JsonlDurabilityError(f"cannot advance JSONL verification index: {path}: {exc}") from exc


def append_jsonl(path: Path, value: dict, max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES,
                 dedupe_field: str | None = None, dedupe_value: object = None) -> AppendOutcome:
    """Repair a torn tail, validate committed rows, and durably append one object.

    The exact torn bytes and fail-closed escalation metadata are stored in the canonical
    ``state/jsonl-quarantine`` directory before truncation.  Complete malformed rows are
    never truncated or skipped.
    """
    if not isinstance(value, dict):
        raise JsonlDurabilityError("JSONL append requires an object")
    encoded = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(encoded) - 1 > max_record_bytes:
        raise JsonlDurabilityError(f"new JSONL record exceeds {max_record_bytes} bytes: {path}")
    flags = os.O_RDWR | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    identity: tuple[int, int] | None = None
    evidence: dict | None = None
    connection: sqlite3.Connection | None = None
    with _PinnedDirectory(path.parent) as parent:
        try:
            descriptor, identity = _open_journal_leaf(path, flags, parent=parent)
            _lock_descriptor(descriptor)
            size = os.fstat(descriptor).st_size
            committed = size
            if size and _read_at(descriptor, 1, size - 1) != b"\n":
                committed = _last_newline(descriptor, size)
                _verify_journal_descriptor(descriptor, identity, parent, path.name)
                evidence = _quarantine_tail(path, descriptor, committed, size)
                _verify_journal_descriptor(descriptor, identity, parent, path.name)
                os.ftruncate(descriptor, committed)
                os.fsync(descriptor)
            connection, _rebuilt = _open_verified_index(
                path, descriptor, committed, max_record_bytes, parent, identity
            )
            if _duplicate_in_index(connection, dedupe_field, dedupe_value):
                return AppendOutcome(appended=False, quarantine=evidence)
            _verify_journal_descriptor(descriptor, identity, parent, path.name)
            _write_all(descriptor, encoded)
            os.fsync(descriptor)
            _verify_journal_descriptor(descriptor, identity, parent, path.name)
            _fsync_dir(path.parent, parent.descriptor)
            _update_index_after_append(connection, descriptor, path, encoded, max_record_bytes)
            _verify_journal_descriptor(descriptor, identity, parent, path.name)
        finally:
            if connection is not None:
                connection.close()
            if descriptor is not None:
                os.close(descriptor)
    return AppendOutcome(appended=True, quarantine=evidence)

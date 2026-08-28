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


def _write_all(descriptor: int, value: bytes) -> None:
    view = memoryview(value)
    while view:
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
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    temporary = Path(name)
    try:
        if hasattr(os, "fchmod"):  # absent on Windows; NTFS mode bits are meaningless
            os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as output:
            _write_all(output.fileno(), value)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        _fsync_dir(path.parent)
    except BaseException:
        # Cleanup must never replace the primary exception: close the descriptor first
        # (Windows cannot unlink an open file) and swallow only the cleanup's own OSError.
        try:
            os.close(descriptor)
        except OSError:
            pass
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise


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


def _ensure_index_root(path: Path) -> tuple[Path, str]:
    root, identity = _index_identity(path)
    if root.exists():
        if root.is_symlink() or not root.is_dir():
            raise JsonlDurabilityError(f"JSONL index root has unsafe type: {root}")
    else:
        root.mkdir(mode=0o700)
        _fsync_dir(root.parent)
    try:
        os.chmod(root, 0o700)
    except OSError:
        pass
    return root, identity


def _index_path(path: Path) -> tuple[Path, str]:
    root, identity = _ensure_index_root(path)
    name = hashlib.sha256(identity.encode("utf-8")).hexdigest() + ".sqlite3"
    candidate = root / name
    if candidate.exists() and (candidate.is_symlink() or not candidate.is_file()):
        raise JsonlDurabilityError(f"JSONL index has unsafe type: {candidate}")
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
    quarantine.mkdir(parents=True, exist_ok=True, mode=0o700)
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
    try:
        if payload.exists():
            existing_digest = hashlib.sha256()
            with payload.open("rb") as current:
                for chunk in iter(lambda: current.read(COPY_CHUNK_BYTES), b""):
                    existing_digest.update(chunk)
            existing = existing_digest.hexdigest()
            if existing != tail_sha or payload.stat().st_size != size - offset:
                raise JsonlDurabilityError(f"JSONL quarantine payload conflicts: {payload}")
            payload_tmp.unlink(missing_ok=True)
        else:
            os.replace(payload_tmp, payload)
            _fsync_dir(quarantine)
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
        if metadata.exists():
            prior = json.loads(metadata.read_text(encoding="utf-8"))
            immutable = ("kind", "journal", "journal_offset", "original_bytes", "tail_bytes",
                         "tail_sha256", "payload")
            if any(prior.get(key) != evidence.get(key) for key in immutable):
                raise JsonlDurabilityError(f"JSONL quarantine metadata conflicts: {metadata}")
            evidence = prior
        else:
            _atomic_bytes(metadata, encoded)
        return evidence
    except BaseException:
        payload_tmp.unlink(missing_ok=True)
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


def _stat_fields(stat: os.stat_result) -> tuple[str, str, int, int, int]:
    return (
        str(stat.st_dev), str(stat.st_ino), int(stat.st_size),
        int(stat.st_mtime_ns), int(stat.st_ctime_ns),
    )


def _metadata(connection: sqlite3.Connection) -> tuple | None:
    return connection.execute(
        "SELECT schema_version,authority,journal_identity,max_record_bytes,device,inode,size,"
        "mtime_ns,ctime_ns,line_count,chain_sha256 FROM metadata WHERE singleton=1"
    ).fetchone()


def _index_matches(connection: sqlite3.Connection, identity: str, stat: os.stat_result,
                   max_record_bytes: int) -> bool:
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
    line_count, chain = int(row[9]), str(row[10])
    summary = connection.execute(
        "SELECT COUNT(*),COALESCE(MIN(start_offset),0),COALESCE(MAX(end_offset),0),"
        "COALESCE(MAX(sequence),0) FROM records"
    ).fetchone()
    if summary != (line_count, 0, int(stat.st_size), line_count):
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
    connection.execute("DELETE FROM metadata")
    connection.execute(
        "INSERT INTO metadata VALUES(1,?,?,?,?,?,?,?,?,?,?,?)",
        (
            INDEX_SCHEMA_VERSION, INDEX_AUTHORITY, identity, max_record_bytes,
            *_stat_fields(stat), line_count, chain_sha256,
        ),
    )


def _rebuild_index(index_path: Path, identity: str, descriptor: int, stat: os.stat_result,
                   journal: Path, max_record_bytes: int) -> None:
    temporary_fd, temporary_name = tempfile.mkstemp(
        prefix=f".{index_path.name}.tmp.", dir=index_path.parent
    )
    temporary = Path(temporary_name)
    os.close(temporary_fd)
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(temporary)
        _create_index_schema(connection)
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
        connection.commit()
        connection.close()
        connection = None
        cache_fd = os.open(temporary, os.O_RDWR | getattr(os, "O_BINARY", 0))
        try:
            os.fsync(cache_fd)
        finally:
            os.close(cache_fd)
        os.replace(temporary, index_path)
        _fsync_dir(index_path.parent)
    except BaseException:
        if connection is not None:
            connection.close()
        temporary.unlink(missing_ok=True)
        raise


def _open_verified_index(path: Path, descriptor: int, size: int,
                         max_record_bytes: int) -> tuple[sqlite3.Connection, bool]:
    stat = os.fstat(descriptor)
    if stat.st_size != size:
        raise JsonlDurabilityError(f"JSONL size changed while opening verification index: {path}")
    index_path, identity = _index_path(path)
    if index_path.exists():
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(index_path)
            connection.execute("PRAGMA query_only=ON")
            if _index_matches(connection, identity, stat, max_record_bytes):
                connection.execute("PRAGMA query_only=OFF")
                retained = connection
                connection = None
                return retained, False
        except sqlite3.DatabaseError:
            pass
        finally:
            if connection is not None:
                connection.close()
    _rebuild_index(index_path, identity, descriptor, stat, path, max_record_bytes)
    connection = sqlite3.connect(index_path)
    if not _index_matches(connection, identity, stat, max_record_bytes):
        connection.close()
        raise JsonlDurabilityError(f"rebuilt JSONL verification index is inconsistent: {path}")
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
        -> tuple[int, sqlite3.Connection, bool]:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        _lock_descriptor(descriptor)
        size = os.fstat(descriptor).st_size
        if size and _read_at(descriptor, 1, size - 1) != b"\n":
            raise JsonlDurabilityError(f"unterminated JSONL tail: {path}")
        connection, rebuilt = _open_verified_index(path, descriptor, size, max_record_bytes)
        return descriptor, connection, rebuilt
    except BaseException:
        os.close(descriptor)
        raise


def read_jsonl_objects(path: Path, max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> list[dict]:
    """Read objects from an intact journal through its verified derived index."""
    if not path.is_file():
        return []
    descriptor, connection, _rebuilt = _verified_descriptor(path, max_record_bytes)
    try:
        rows = connection.execute(
            "SELECT value_json FROM records WHERE value_json IS NOT NULL ORDER BY sequence"
        )
        return [json.loads(row[0]) for row in rows]
    finally:
        connection.close()
        os.close(descriptor)


def read_jsonl_prefix(path: Path, count: int,
                      max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> tuple[VerifiedLine, ...]:
    """Return at most *count* verified physical lines from the journal prefix."""
    if count < 0:
        raise JsonlDurabilityError("JSONL prefix count cannot be negative")
    if not path.is_file() or count == 0:
        return ()
    descriptor, connection, _rebuilt = _verified_descriptor(path, max_record_bytes)
    try:
        rows = connection.execute(
            "SELECT sequence,start_offset,end_offset,raw,value_json,chain_sha256 FROM records "
            "ORDER BY sequence LIMIT ?", (count,),
        )
        return _rows_to_lines(rows)
    finally:
        connection.close()
        os.close(descriptor)


def find_jsonl_objects(path: Path, field: str, value: object,
                       max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> list[dict]:
    """Find exact top-level field matches without rescanning verified journal bytes."""
    if not path.is_file():
        return []
    descriptor, connection, _rebuilt = _verified_descriptor(path, max_record_bytes)
    try:
        if field == "id":
            encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
            rows = connection.execute(
                "SELECT value_json FROM records WHERE object_id_json=? ORDER BY sequence",
                (encoded,),
            )
            return [json.loads(row[0]) for row in rows]
        result = []
        for row in connection.execute(
                "SELECT value_json FROM records WHERE value_json IS NOT NULL ORDER BY sequence"):
            candidate = json.loads(row[0])
            if candidate.get(field) == value:
                result.append(candidate)
        return result
    finally:
        connection.close()
        os.close(descriptor)


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
    if not path.is_file():
        return IndexedBatch((), 0, ZERO_CHAIN_SHA256, False)
    descriptor, connection, rebuilt = _verified_descriptor(path, max_record_bytes)
    try:
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
        return IndexedBatch(lines, int(metadata[6]), str(metadata[10]), rebuilt)
    finally:
        connection.close()
        os.close(descriptor)


def acknowledge_jsonl(path: Path, consumer: str, batch: IndexedBatch,
                      max_record_bytes: int = DEFAULT_MAX_RECORD_BYTES) -> None:
    """Durably advance a consumer after its selected projections are durable."""
    if not consumer or len(consumer) > 128:
        raise JsonlDurabilityError("invalid JSONL index consumer")
    if not path.is_file():
        if batch.verified_size == 0:
            return
        raise JsonlDurabilityError(f"JSONL disappeared before acknowledgement: {path}")
    descriptor, connection, _rebuilt = _verified_descriptor(path, max_record_bytes)
    try:
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
    stat = os.fstat(descriptor)
    if stat.st_size != old_size + len(encoded):
        raise JsonlDurabilityError(f"JSONL size changed during indexed append: {path}")
    try:
        value = json.loads(encoded[:-1].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:  # defensive; caller encoded it.
        raise JsonlDurabilityError(f"new JSONL record cannot be indexed: {path}") from exc
    raw_digest = hashlib.sha256(encoded).digest()
    chain = hashlib.sha256(bytes.fromhex(prior_chain) + raw_digest).hexdigest()
    line = VerifiedLine(line_count + 1, old_size, stat.st_size, encoded, value, chain)
    try:
        connection.execute("BEGIN IMMEDIATE")
        _insert_line(connection, line_count + 1, line)
        _write_metadata(
            connection, str(metadata[2]), stat, max_record_bytes, line_count + 1, chain
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
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    flags = os.O_RDWR | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    evidence: dict | None = None
    connection: sqlite3.Connection | None = None
    try:
        _lock_descriptor(descriptor)
        size = os.fstat(descriptor).st_size
        committed = size
        if size and _read_at(descriptor, 1, size - 1) != b"\n":
            committed = _last_newline(descriptor, size)
            evidence = _quarantine_tail(path, descriptor, committed, size)
            os.ftruncate(descriptor, committed)
            os.fsync(descriptor)
        connection, _rebuilt = _open_verified_index(
            path, descriptor, committed, max_record_bytes
        )
        if _duplicate_in_index(connection, dedupe_field, dedupe_value):
            return AppendOutcome(appended=False, quarantine=evidence)
        _write_all(descriptor, encoded)
        os.fsync(descriptor)
        if not existed:
            _fsync_dir(path.parent)
        _update_index_after_append(connection, descriptor, path, encoded, max_record_bytes)
    finally:
        if connection is not None:
            connection.close()
        os.close(descriptor)
    return AppendOutcome(appended=True, quarantine=evidence)

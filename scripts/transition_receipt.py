#!/usr/bin/env python3
"""Crash-consistent canonical-state transition receipts.

The canonical state files remain authoritative.  A receipt freezes the audit event and
the exact commit witnesses *before* a mutation.  Recovery may project the event only when
every witness matches; it never completes a state mutation or invokes an actuator.

Callers must continue to hold their existing object/task lock while calling
``commit_transition``.  Receipts are not a scheduler, queue, or second state store.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from jsonl_durable import JsonlDurabilityError, append_jsonl


ALLOWED_JOURNALS = frozenset({
    "state/events.jsonl",
    "state/action-events.jsonl",
    "state/delivery-events.jsonl",
    "state/notification-event-events.jsonl",
    "state/notification-audit-events.jsonl",
    "state/notification-recovery-events.jsonl",
})
TRANSITION_ID = re.compile(r"transition-[0-9a-f]{32}")


class TransitionReceiptError(RuntimeError):
    pass


def _compact(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_compact(value)).hexdigest()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _fsync_dir(path: Path) -> None:
    if os.name == "nt":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    temporary = Path(raw)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as out:
            view = memoryview(payload)
            while view:
                written = out.write(view)
                if not written:
                    raise OSError("transition receipt write made no progress")
                view = view[written:]
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
        _fsync_dir(path.parent)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _atomic_json(path: Path, value: dict) -> None:
    _atomic_bytes(path, _compact(value) + b"\n")


def _failpoint(name: str) -> None:
    if os.environ.get("RECURSION_TRANSITION_FAILPOINT") == name:
        raise TransitionReceiptError(f"transition failpoint: {name}")


def _relative_state_path(base: Path, path: Path) -> str:
    base = base.resolve()
    path = path.resolve(strict=False)
    try:
        relative = path.relative_to(base)
    except ValueError as exc:
        raise TransitionReceiptError(f"transition path escapes root: {path}") from exc
    if not relative.parts or relative.parts[0] != "state" or ".." in relative.parts:
        raise TransitionReceiptError(f"transition path is outside canonical state: {relative}")
    return relative.as_posix()


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TransitionReceiptError(f"cannot read transition JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TransitionReceiptError(f"transition JSON is not an object: {path}")
    return value


def _read_fields(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    except OSError as exc:
        raise TransitionReceiptError(f"cannot read transition fields {path}: {exc}") from exc
    result: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            break
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            result.setdefault(key.strip(), value.strip())
    return result


def _atomic_fields(path: Path, changes: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
    header_end = next((i for i, line in enumerate(lines) if not line.strip()), len(lines))
    found: set[str] = set()
    output: list[str] = []
    for index, line in enumerate(lines):
        key = line.split(":", 1)[0].strip() if index < header_end and ":" in line \
            and not line.startswith((" ", "\t")) else ""
        if key in changes and key not in found:
            output.append(f"{key}: {changes[key]}")
            found.add(key)
        else:
            output.append(line)
    missing: list[str] = []
    for key, value in changes.items():
        if key not in found:
            missing.append(f"{key}: {value}")
    output[header_end:header_end] = missing
    _atomic_bytes(path, ("\n".join(output) + "\n").encode("utf-8", "surrogateescape"))


@dataclass(frozen=True)
class Mutation:
    path: Path
    kind: str
    changes: dict[str, str] | None = None
    value: dict | None = None
    text: str | None = None


def fields_mutation(path: Path, changes: dict[str, object]) -> Mutation:
    return Mutation(path=path, kind="fields", changes={str(k): str(v) for k, v in changes.items()})


def json_mutation(path: Path, value: dict) -> Mutation:
    return Mutation(path=path, kind="json", value=dict(value))


def text_mutation(path: Path, text: str) -> Mutation:
    return Mutation(path=path, kind="text", text=text)


def raw_text_mutation(path: Path, text: str) -> Mutation:
    """Replace a non-frontmatter text projection (for example portfolio.tsv) byte-exactly."""
    return Mutation(path=path, kind="raw-text", text=text)


def _with_text_witness(text: str, transition_id: str, event_seq: int) -> str:
    lines = text.splitlines()
    header_end = next((i for i, line in enumerate(lines) if not line.strip()), len(lines))
    changes = {"event_seq": str(event_seq), "last_transition_id": transition_id}
    found: set[str] = set()
    output: list[str] = []
    for index, line in enumerate(lines):
        key = line.split(":", 1)[0].strip() if index < header_end and ":" in line \
            and not line.startswith((" ", "\t")) else ""
        if key in changes and key not in found:
            output.append(f"{key}: {changes[key]}"); found.add(key)
        else:
            output.append(line)
    insert_at = header_end
    for key, value in changes.items():
        if key not in found:
            output.insert(insert_at, f"{key}: {value}"); insert_at += 1
    return "\n".join(output) + "\n"


def _plan_mutation(base: Path, mutation: Mutation, transition_id: str, event_seq: int) -> dict:
    relative = _relative_state_path(base, mutation.path)
    if mutation.kind == "fields":
        before = _read_fields(mutation.path)
        changes = dict(mutation.changes or {})
        changes.update({"event_seq": str(event_seq), "last_transition_id": transition_id})
        expected = {key: value for key, value in changes.items()}
        prior = {key: before.get(key) for key in expected}
        return {"path": relative, "kind": "fields", "before": prior,
                "expect": expected, "changes": expected}
    if mutation.kind == "json":
        before = _read_json(mutation.path) if mutation.path.exists() else None
        value = dict(mutation.value or {})
        value.update({"event_seq": event_seq, "last_transition_id": transition_id})
        return {"path": relative, "kind": "json", "before_sha256": _digest(before),
                "expect_sha256": _digest(value), "value": value}
    if mutation.kind == "text":
        before = mutation.path.read_bytes() if mutation.path.exists() else None
        source = mutation.text or ""
        value = _with_text_witness(source, transition_id, event_seq)
        return {"path": relative, "kind": "text",
                "before_sha256": hashlib.sha256(before).hexdigest() if before is not None else _digest(None),
                "expect_sha256": hashlib.sha256(value.encode("utf-8", "surrogateescape")).hexdigest(),
                "source_sha256": hashlib.sha256(source.encode("utf-8", "surrogateescape")).hexdigest(),
                "text": value}
    if mutation.kind == "raw-text":
        before = mutation.path.read_bytes() if mutation.path.exists() else None
        source = mutation.text or ""
        encoded = source.encode("utf-8", "surrogateescape")
        return {"path": relative, "kind": "raw-text",
                "before_sha256": hashlib.sha256(before).hexdigest() if before is not None else _digest(None),
                "expect_sha256": hashlib.sha256(encoded).hexdigest(),
                "source_sha256": hashlib.sha256(encoded).hexdigest(), "text": source}
    raise TransitionReceiptError(f"unsupported transition mutation kind: {mutation.kind}")


def _receipt_root(base: Path) -> Path:
    return base / "state/recovery/transitions"


def _ensure_receipt_root(base: Path) -> Path:
    """Create and durably link each missing receipt-directory component."""
    current = base / "state"
    for name in ("recovery", "transitions"):
        child = current / name
        if not child.exists():
            child.mkdir(mode=0o700)
            _fsync_dir(current)
        current = child
    return current


def _ensure_recovery_directory(base: Path, name: str) -> Path:
    current = base / "state"
    for component in ("recovery", name):
        child = current / component
        if not child.exists():
            child.mkdir(mode=0o700)
            _fsync_dir(current)
        elif child.is_symlink() or not child.is_dir():
            raise TransitionReceiptError(f"transition recovery path has unsafe type: {child}")
        current = child
    return current


def _archive_directory(base: Path, transition_id: str, *, create: bool = False) -> Path:
    if TRANSITION_ID.fullmatch(transition_id) is None:
        raise TransitionReceiptError(f"invalid transition receipt id: {transition_id}")
    root = base / "state/recovery/transition-archive"
    if create:
        root = _ensure_recovery_directory(base, "transition-archive")
        shard = root / transition_id[len("transition-"):len("transition-") + 2]
        if not shard.exists():
            shard.mkdir(mode=0o700)
            _fsync_dir(root)
        elif shard.is_symlink() or not shard.is_dir():
            raise TransitionReceiptError(f"transition archive shard has unsafe type: {shard}")
    else:
        shard = root / transition_id[len("transition-"):len("transition-") + 2]
    return shard / transition_id


def _receipt_directory(base: Path, transition_id: str) -> Path:
    active = _receipt_root(base) / transition_id
    archived = _archive_directory(base, transition_id)
    active_exists = active.is_dir() and not active.is_symlink()
    archived_exists = archived.is_dir() and not archived.is_symlink()
    if active_exists and archived_exists:
        raise TransitionReceiptError(f"transition receipt exists in active and archive stores: {transition_id}")
    if active_exists:
        return active
    if archived_exists:
        return archived
    raise TransitionReceiptError(f"transition receipt evidence is absent: {transition_id}")


def _event_index_path(base: Path, event_id: str, *, create: bool = False) -> Path:
    root = base / "state/recovery/transition-event-index"
    digest = hashlib.sha256(event_id.encode("utf-8")).hexdigest()
    if create:
        root = _ensure_recovery_directory(base, "transition-event-index")
        shard = root / digest[:2]
        if not shard.exists():
            shard.mkdir(mode=0o700)
            _fsync_dir(root)
        elif shard.is_symlink() or not shard.is_dir():
            raise TransitionReceiptError(f"transition event index shard has unsafe type: {shard}")
    else:
        shard = root / digest[:2]
    return shard / f"{digest}.json"


def _index_event(base: Path, prepared: dict) -> None:
    event_id = str(prepared.get("event", {}).get("id") or "")
    transition_id = str(prepared.get("id") or "")
    if not event_id or TRANSITION_ID.fullmatch(transition_id) is None:
        raise TransitionReceiptError("transition receipt lacks an indexable identity")
    directory = _receipt_directory(base, transition_id)
    prepared_path = directory / "prepared.json"
    prepared_sha256 = hashlib.sha256(prepared_path.read_bytes()).hexdigest()
    record = {
        "schema_version": 1,
        "kind": "transition-event-index",
        "event_id": event_id,
        "transition_id": transition_id,
        "prepared_sha256": prepared_sha256,
    }
    path = _event_index_path(base, event_id, create=True)
    if path.exists():
        if _read_json(path) != record:
            raise TransitionReceiptError(f"transition event identity collision: {event_id}")
        return
    _atomic_json(path, record)


def _indexed_prepared(base: Path, event_id: str) -> dict | None:
    path = _event_index_path(base, event_id)
    if not path.exists():
        return None
    record = _read_json(path)
    if set(record) != {
        "schema_version", "kind", "event_id", "transition_id", "prepared_sha256"
    } or record.get("schema_version") != 1 or record.get("kind") != "transition-event-index" \
            or record.get("event_id") != event_id:
        raise TransitionReceiptError(f"invalid transition event index: {path}")
    transition_id = str(record.get("transition_id") or "")
    directory = _receipt_directory(base, transition_id)
    prepared_path = directory / "prepared.json"
    try:
        observed = hashlib.sha256(prepared_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise TransitionReceiptError(f"indexed transition receipt is unreadable: {transition_id}") from exc
    if observed != record.get("prepared_sha256"):
        raise TransitionReceiptError(f"indexed transition receipt digest changed: {transition_id}")
    prepared = _load_prepared(prepared_path)
    if prepared.get("event", {}).get("id") != event_id or prepared.get("id") != transition_id:
        raise TransitionReceiptError(f"indexed transition receipt identity changed: {transition_id}")
    return prepared


def _authenticated_prepared(base: Path, event_id: str,
                            *, journal: str | None) -> dict:
    """Read one fully projected indexed receipt and verify its durable identity evidence."""
    prepared = _indexed_prepared(base, event_id)
    if prepared is None:
        raise TransitionReceiptError(f"transition event index is absent: {event_id}")
    if journal is not None and prepared.get("journal") != journal:
        raise TransitionReceiptError(f"transition receipt journal disagrees: {event_id}")
    directory = _receipt_directory(base, str(prepared["id"]))
    marker = _read_json(directory / "projected.json")
    if set(marker) != {"schema_version", "status", "at", "event_id"} \
            or marker.get("schema_version") != 1 or marker.get("status") != "projected" \
            or marker.get("event_id") != event_id:
        raise TransitionReceiptError(f"transition projected marker is invalid: {event_id}")
    source = base / str(prepared.get("journal") or "state/events.jsonl")
    try:
        from jsonl_durable import read_jsonl_objects
        matches = [row for row in read_jsonl_objects(source) if row.get("id") == event_id]
    except (JsonlDurabilityError, OSError) as exc:
        raise TransitionReceiptError(f"transition journal is unreadable: {event_id}") from exc
    if matches != [prepared["event"]]:
        raise TransitionReceiptError(f"transition journal evidence disagrees: {event_id}")
    return prepared


def _require_archived_witness(base: Path, mutation: dict, event_seq: int) -> None:
    """Require that a moved-on canonical witness advanced through the receipt chain.

    ``_witness_state`` returns ``other`` (or ``before``) when the object no longer matches this
    mutation's frozen post/pre snapshots.  That is legitimate only when a *later* receipt owns
    the object's current state: the object must carry a strictly newer ``event_seq`` and its
    current ``last_transition_id`` must itself authenticate.  A hand-edited object, or one that
    drifted without a receipt, cannot name such a successor and fails closed.
    """
    path = base / mutation["path"]
    if mutation["kind"] == "json":
        current = _read_json(path)
    else:
        # Fields, text, and raw-text witnesses carry their sequence markers in frontmatter.
        current = _read_fields(path)
    try:
        observed_seq = int(current.get("event_seq") or 0)
    except (TypeError, ValueError) as exc:
        raise TransitionReceiptError(
            f"archived transition witness event_seq is invalid: {mutation['path']}"
        ) from exc
    if observed_seq <= event_seq:
        raise TransitionReceiptError(
            f"transition canonical witnesses disagree (archived): {mutation['path']}"
        )
    successor = str(current.get("last_transition_id") or "")
    if TRANSITION_ID.fullmatch(successor) is None:
        raise TransitionReceiptError(
            f"archived transition witness lacks a canonical successor: {mutation['path']}"
        )
    successor_directory = _receipt_directory(base, successor)
    successor_prepared = _load_prepared(successor_directory / "prepared.json")
    successor_event_id = str((successor_prepared.get("event") or {}).get("id") or "")
    if not successor_event_id:
        raise TransitionReceiptError(
            f"archived transition witness successor lacks an event id: {mutation['path']}"
        )
    try:
        authenticated_chain_transition(base, successor_event_id)
    except TransitionReceiptError as exc:
        raise TransitionReceiptError(
            f"archived transition witness successor is invalid: {mutation['path']}"
        ) from exc


def authenticated_transition(base: Path, event_id: str,
                             *, journal: str | None = None) -> dict:
    """Read one fully projected indexed receipt and verify every durable witness."""
    prepared = _authenticated_prepared(base, event_id, journal=journal)
    states = [_witness_state(base, mutation) for mutation in prepared.get("mutations", [])]
    if any(state != "expected" for state in states):
        raise TransitionReceiptError(
            f"transition canonical witnesses disagree: {event_id} states={states}"
        )
    return prepared


def authenticated_chain_transition(base: Path, event_id: str,
                                   *, journal: str | None = None) -> dict:
    """Authenticate a receipt whose canonical witnesses are current OR archived.

    The index entry, projected marker, exact journal evidence, and unmodified receipt bytes are
    always required.  A mutation witness still matching the current canonical state is
    ``expected``; a witness the state has since moved past must have been superseded by an
    authenticated successor receipt (see ``_require_archived_witness``).  Pure audit events
    carry no mutations and authenticate on their identity evidence alone.
    """
    prepared = _authenticated_prepared(base, event_id, journal=journal)
    event_seq = int(prepared.get("event_seq") or 0)
    for mutation in prepared.get("mutations", []):
        state = _witness_state(base, mutation)
        if state == "expected":
            continue
        _require_archived_witness(base, mutation, event_seq)
    return prepared


def _archive_receipt(base: Path, prepared: dict) -> None:
    transition_id = str(prepared["id"])
    _index_event(base, prepared)
    active = _receipt_root(base) / transition_id
    archived = _archive_directory(base, transition_id)
    if archived.is_dir() and not archived.is_symlink():
        if active.exists() or active.is_symlink():
            raise TransitionReceiptError(
                f"transition receipt exists in active and archive stores: {transition_id}"
            )
        return
    if active.is_symlink() or not active.is_dir():
        raise TransitionReceiptError(f"active transition receipt has unsafe type: {active}")
    archived = _archive_directory(base, transition_id, create=True)
    if archived.exists() or archived.is_symlink():
        raise TransitionReceiptError(f"transition archive target already exists: {archived}")
    os.rename(active, archived)
    _fsync_dir(active.parent)
    _fsync_dir(archived.parent)


@contextmanager
def _taskctl_guard(base: Path, already_held: bool = False):
    """Serialize receipt, canonical mutation, and event against runtime snapshots."""
    lock_root = base / "state/.locks"
    lock_root.mkdir(parents=True, exist_ok=True)
    path = lock_root / "taskctl.lock"
    runtime = lock_root / "runtime-state.lock"
    if already_held:
        if not path.is_dir():
            raise TransitionReceiptError("claimed taskctl lock is absent")
        if runtime.is_dir():
            try:
                runtime_holder = int((runtime / "pid").read_text(encoding="ascii").strip())
                expected_runtime = int(os.environ["RECURSION_RUNTIME_LOCK_OWNER_PID"])
            except (KeyError, OSError, ValueError) as exc:
                raise TransitionReceiptError(
                    "runtime-state is active without a matching maintenance owner"
                ) from exc
            if runtime_holder != expected_runtime:
                raise TransitionReceiptError(
                    "runtime-state maintenance owner does not match transition recovery"
                )
        try:
            holder = int((path / "pid").read_text(encoding="ascii").strip())
        except (OSError, ValueError) as exc:
            raise TransitionReceiptError("claimed taskctl lock has no complete owner witness") from exc
        expected = int(os.environ.get("RECURSION_TASKCTL_LOCK_OWNER_PID") or os.getppid())
        if holder != expected:
            raise TransitionReceiptError(
                f"claimed taskctl lock owner mismatch: holder={holder} expected={expected}"
            )
        yield
        return
    held = False
    helper = Path(__file__).resolve().parent / "runtime-state.py"
    try:
        if not helper.is_file():
            raise TransitionReceiptError("witnessed taskctl lock helper is absent")
        acquired = subprocess.run(
            [sys.executable, str(helper), "lock-acquire", str(path), str(os.getpid())],
            env={**os.environ, "RECURSION_ROOT": str(base)},
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=False,
        )
        if acquired.returncode:
            raise TransitionReceiptError(
                f"taskctl lock contended during transition: {acquired.stderr.strip()[:240]}"
            )
        held = True
        yield
    finally:
        if held:
            released = subprocess.run(
                [sys.executable, str(helper), "lock-release", str(path), str(os.getpid())],
                env={**os.environ, "RECURSION_ROOT": str(base)},
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=False,
            )
            if released.returncode:
                raise TransitionReceiptError(
                    f"taskctl transition lock release failed: {released.stderr.strip()[:240]}"
                )


def _open_quarantines(base: Path, journal: str) -> list[Path]:
    result: list[Path] = []
    directory = base / "state/jsonl-quarantine"
    if not directory.is_dir():
        return result
    for path in directory.glob("*.json"):
        try:
            value = _read_json(path)
        except TransitionReceiptError:
            result.append(path)
            continue
        if value.get("journal") == journal and value.get("requires_human_review") is True \
                and value.get("status") == "open":
            result.append(path)
    return result


def _load_prepared(path: Path) -> dict:
    value = _read_json(path)
    if value.get("schema_version") != 1 or value.get("kind") != "transition-receipt":
        raise TransitionReceiptError(f"invalid transition receipt: {path}")
    return value


def _marker(directory: Path, name: str, detail: dict | None = None) -> None:
    value = {"schema_version": 1, "status": name, "at": _now()}
    if detail:
        value.update(detail)
    _atomic_json(directory / f"{name}.json", value)


def _witness_state(base: Path, mutation: dict) -> str:
    path = base / mutation["path"]
    if not path.is_file():
        return "before" if mutation["kind"] in {"json", "text", "raw-text"} \
            and mutation.get("before_sha256") == _digest(None) else "other"
    if mutation["kind"] == "fields":
        current = _read_fields(path)
        expect = mutation["expect"]
        before = mutation["before"]
        if all(current.get(key) == value for key, value in expect.items()):
            return "expected"
        if all(current.get(key) == value for key, value in before.items()):
            return "before"
        return "other"
    if mutation["kind"] in {"text", "raw-text"}:
        current_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    else:
        current_sha = _digest(_read_json(path))
    if current_sha == mutation["expect_sha256"]:
        return "expected"
    if current_sha == mutation["before_sha256"]:
        return "before"
    return "other"


def project_receipt(base: Path, prepared: dict, *, replay: bool = False) -> bool:
    directory = _receipt_directory(base, str(prepared["id"]))
    if (directory / "projected.json").is_file():
        _archive_receipt(base, prepared)
        return True
    if replay:
        _failpoint("replay")
    states = [_witness_state(base, mutation) for mutation in prepared["mutations"]]
    if all(state == "expected" for state in states):
        _failpoint("jsonl-append")
        event = prepared["event"]
        journal = str(prepared.get("journal") or "state/events.jsonl")
        journal_path = (base / journal).resolve(strict=False)
        if _relative_state_path(base, journal_path) not in ALLOWED_JOURNALS:
            raise TransitionReceiptError(f"transition receipt has invalid journal: {journal}")
        open_quarantines = _open_quarantines(base, journal)
        if open_quarantines:
            raise TransitionReceiptError(
                f"open JSONL quarantine blocks transition projection: {open_quarantines[0]}"
            )
        try:
            outcome = append_jsonl(journal_path, event,
                                   dedupe_field="id", dedupe_value=event["id"])
        except (JsonlDurabilityError, OSError) as exc:
            raise TransitionReceiptError(f"transition event append failed: {exc}") from exc
        if outcome.quarantine is not None:
            raise TransitionReceiptError(
                f"transition repaired a torn journal tail; human review required: "
                f"{outcome.quarantine.get('escalation_id')}"
            )
        _failpoint("event-before-projected")
        _marker(directory, "projected", {"event_id": event["id"]})
        _archive_receipt(base, prepared)
        return True
    if all(state == "before" for state in states):
        _marker(directory, "uncommitted")
        _archive_receipt(base, prepared)
        return False
    raise TransitionReceiptError(
        f"ambiguous transition receipt {prepared['id']}; witness states={states}"
    )


def _recover_transitions_locked(base: Path, limit: int = 1000) -> dict[str, int]:
    if limit < 1:
        raise TransitionReceiptError("transition recovery limit must be positive")
    counts = {"projected": 0, "uncommitted": 0, "already": 0,
              "archived": 0, "backlog": 0}
    root = _receipt_root(base)
    if not root.is_dir():
        return counts
    processed = 0
    with os.scandir(root) as entries:
        for entry in entries:
            if processed >= limit:
                counts["backlog"] = 1
                break
            processed += 1
            directory = Path(entry.path)
            if entry.is_symlink() or not entry.is_dir(follow_symlinks=False):
                raise TransitionReceiptError(f"invalid active transition receipt path: {directory}")
            prepared = _load_prepared(directory / "prepared.json")
            _index_event(base, prepared)
            terminal = (directory / "projected.json").is_file() \
                or (directory / "uncommitted.json").is_file()
            if terminal:
                counts["already"] += 1
                _archive_receipt(base, prepared)
                counts["archived"] += 1
            elif project_receipt(base, prepared, replay=True):
                counts["projected"] += 1
                counts["archived"] += 1
            else:
                counts["uncommitted"] += 1
                counts["archived"] += 1
    return counts


def _require_recovery_complete(counts: dict[str, int]) -> None:
    if counts.get("backlog"):
        raise TransitionReceiptError(
            f"transition recovery made bounded progress ({counts['archived']} archived); retry"
        )


def recover_transitions(base: Path, limit: int = 1000, *, taskctl_locked: bool = False) -> dict[str, int]:
    with _taskctl_guard(base, taskctl_locked):
        counts = _recover_transitions_locked(base, limit)
        _require_recovery_complete(counts)
        return counts


def resume_transition(base: Path, event: dict, *, taskctl_locked: bool = False) -> str | None:
    """Operation-specific retry of the one receipt bound to an explicit event id."""
    event_id = str(event.get("id") or "")
    if not event_id:
        raise TransitionReceiptError("transition resume requires an explicit event id")
    with _taskctl_guard(base, taskctl_locked):
        prepared = _indexed_prepared(base, event_id)
        if prepared is None:
            counts = _recover_transitions_locked(base)
            _require_recovery_complete(counts)
            prepared = _indexed_prepared(base, event_id)
            if prepared is None:
                return None
        supplied = dict(event); frozen = dict(prepared["event"])
        for value in (supplied, frozen):
            value.pop("ts", None); value.pop("pid", None); value.pop("transition_id", None)
        if supplied != frozen:
            raise TransitionReceiptError(f"event id collides with a different retry: {event_id}")
        authoritative = prepared["authoritative_path"]
        order = [item for item in prepared["mutations"] if item["path"] != authoritative]
        order += [item for item in prepared["mutations"] if item["path"] == authoritative]
        for mutation in order:
            state = _witness_state(base, mutation)
            if state == "expected":
                continue
            if state != "before":
                raise TransitionReceiptError(
                    f"transition retry found unrelated divergence: {mutation['path']}"
                )
            path = base / mutation["path"]
            if mutation["kind"] == "fields":
                _atomic_fields(path, mutation["changes"])
            elif mutation["kind"] == "json":
                _atomic_json(path, mutation["value"])
            else:
                _atomic_bytes(path, mutation["text"].encode("utf-8", "surrogateescape"))
        _failpoint("state-write")
        if not project_receipt(base, prepared):
            raise TransitionReceiptError(f"transition retry did not commit all witnesses: {event_id}")
        return str(prepared["id"])


def _reuse_pure_event(base: Path, event: dict, prepared: dict) -> str:
    if prepared.get("mutations"):
        raise TransitionReceiptError(f"pure event id receipt collision: {event['id']}")
    frozen = dict(prepared["event"]); supplied = dict(event)
    for value in (frozen, supplied):
        value.pop("ts", None); value.pop("pid", None); value.pop("transition_id", None)
    if frozen != supplied:
        raise TransitionReceiptError(f"pure event id content collision: {event['id']}")
    project_receipt(base, prepared)
    return str(prepared["id"])


def commit_event(base: Path, event: dict, *, journal: str = "state/events.jsonl",
                 taskctl_locked: bool = False) -> str:
    """Durably commit a pure audit event using its receipt as the recovery witness."""
    if journal not in ALLOWED_JOURNALS:
        raise TransitionReceiptError(f"unsupported pure-event journal: {journal}")
    with _taskctl_guard(base, taskctl_locked):
        open_quarantines = _open_quarantines(base, journal)
        if open_quarantines:
            raise TransitionReceiptError(
                f"open JSONL quarantine blocks transition projection: {open_quarantines[0]}"
            )
        event = dict(event)
        event.setdefault("schema_version", 1)
        event.setdefault("ts", _now())
        event.setdefault("id", "source-event-" + hashlib.sha256(_compact(event)).hexdigest()[:32])
        prepared = _indexed_prepared(base, str(event["id"]))
        if prepared is not None:
            return _reuse_pure_event(base, event, prepared)
        counts = _recover_transitions_locked(base)
        _require_recovery_complete(counts)
        prepared = _indexed_prepared(base, str(event["id"]))
        if prepared is not None:
            return _reuse_pure_event(base, event, prepared)
        transition_id = "transition-" + hashlib.sha256(
            _compact({"journal": journal, "event": event})).hexdigest()[:32]
        event["transition_id"] = transition_id
        prepared = {"schema_version": 1, "kind": "transition-receipt", "id": transition_id,
                    "event_seq": 0, "prepared_at": event["ts"], "event": event,
                    "journal": journal, "authoritative_path": None, "mutations": []}
        directory = _ensure_receipt_root(base) / transition_id
        receipt_path = directory / "prepared.json"
        if receipt_path.exists():
            if _load_prepared(receipt_path) != prepared:
                raise TransitionReceiptError(f"pure event receipt collision: {transition_id}")
        else:
            directory.mkdir(parents=True, mode=0o700)
            _fsync_dir(directory.parent)
            _atomic_json(receipt_path, prepared)
        _index_event(base, prepared)
        _failpoint("receipt-fsync")
        if not project_receipt(base, prepared):
            raise TransitionReceiptError(f"pure event was not projected: {event['id']}")
        return transition_id


def commit_transition(base: Path, mutations: list[Mutation], event: dict,
                      *, authoritative_index: int = -1,
                      journal: str = "state/events.jsonl",
                      taskctl_locked: bool = False,
                      precondition: Callable[[], None] | None = None) -> str:
    """Commit state then its frozen event, with the authoritative witness written last.

    An interrupted partial multi-file transaction is safely retryable only by calling this
    exact operation again.  Generic recovery refuses to complete state and therefore cannot
    manufacture an event for a half-committed transition.
    """
    with _taskctl_guard(base, taskctl_locked):
        return _commit_transition_locked(base, mutations, event,
                                         authoritative_index=authoritative_index,
                                         journal=journal, precondition=precondition)


def _retry_prepared_transition(base: Path, prior: dict, event: dict,
                               mutations: list[Mutation], authoritative_index: int,
                               requested_id: str) -> str:
    frozen_event = dict(prior["event"])
    supplied_event = dict(event)
    for value in (frozen_event, supplied_event):
        value.pop("ts", None); value.pop("pid", None); value.pop("transition_id", None)
    if frozen_event != supplied_event:
        raise TransitionReceiptError(f"event id collides with different transition: {requested_id}")
    prior_mutations = prior.get("mutations") or []
    if len(prior_mutations) != len(mutations):
        raise TransitionReceiptError(f"transition retry mutation count differs: {requested_id}")
    for requested, frozen in zip(mutations, prior_mutations):
        if _relative_state_path(base, requested.path) != frozen.get("path") \
                or requested.kind != frozen.get("kind"):
            raise TransitionReceiptError(f"transition retry target differs: {requested_id}")
        if requested.kind == "fields":
            wanted = {str(k): str(v) for k, v in (requested.changes or {}).items()}
            actual = {k: v for k, v in frozen["changes"].items()
                      if k not in {"event_seq", "last_transition_id"}}
            if wanted != actual:
                raise TransitionReceiptError(f"transition retry fields differ: {requested_id}")
        elif requested.kind == "json":
            actual = dict(frozen["value"])
            actual.pop("event_seq", None); actual.pop("last_transition_id", None)
            if dict(requested.value or {}) != actual:
                raise TransitionReceiptError(f"transition retry JSON differs: {requested_id}")
        elif hashlib.sha256((requested.text or "").encode(
                "utf-8", "surrogateescape")).hexdigest() != frozen.get("source_sha256"):
            raise TransitionReceiptError(f"transition retry text differs: {requested_id}")
    order = [i for i in range(len(prior_mutations)) if i != authoritative_index]
    order.append(authoritative_index)
    for index in order:
        mutation = prior_mutations[index]
        state = _witness_state(base, mutation)
        if state == "expected":
            continue
        if state != "before":
            raise TransitionReceiptError(
                f"transition retry found unrelated divergence: {mutation['path']}"
            )
        path = base / mutation["path"]
        if mutation["kind"] == "fields":
            _atomic_fields(path, mutation["changes"])
        elif mutation["kind"] == "json":
            _atomic_json(path, mutation["value"])
        else:
            _atomic_bytes(path, mutation["text"].encode("utf-8", "surrogateescape"))
    _failpoint("state-write")
    if not project_receipt(base, prior):
        raise TransitionReceiptError(f"transition retry did not commit all witnesses: {requested_id}")
    return str(prior["id"])


def _commit_transition_locked(base: Path, mutations: list[Mutation], event: dict,
                              *, authoritative_index: int,
                              journal: str,
                              precondition: Callable[[], None] | None = None) -> str:
    if not mutations:
        raise TransitionReceiptError("transition requires at least one canonical mutation")
    if authoritative_index < 0:
        authoritative_index += len(mutations)
    if not 0 <= authoritative_index < len(mutations):
        raise TransitionReceiptError("invalid authoritative transition mutation")
    if journal not in ALLOWED_JOURNALS:
        raise TransitionReceiptError(f"unsupported transition journal: {journal}")
    open_quarantines = _open_quarantines(base, journal)
    if open_quarantines:
        raise TransitionReceiptError(
            f"open JSONL quarantine blocks transition projection: {open_quarantines[0]}"
        )
    event = dict(event)
    event.setdefault("schema_version", 1)
    event.setdefault("ts", _now())
    identity_seed = {"event": event, "paths": [_relative_state_path(base, item.path) for item in mutations]}
    requested_id = str(event.get("id") or "")

    if requested_id:
        prior = _indexed_prepared(base, requested_id)
        if prior is not None:
            return _retry_prepared_transition(
                base, prior, event, mutations, authoritative_index, requested_id
            )

    # Linearize new authority under taskctl.lock. Exact receipt retries above remain lawful
    # after revocation because completing their frozen multi-file mutation is recovery.
    if precondition is not None:
        precondition()

    # Before advancing any canonical sequence, repair every fully committed receipt and
    # reject any mixed-witness transaction.  Exact-ID retry above remains the sole path that
    # may finish a partial multi-file mutation.
    counts = _recover_transitions_locked(base)
    _require_recovery_complete(counts)
    if requested_id:
        prior = _indexed_prepared(base, requested_id)
        if prior is not None:
            return _retry_prepared_transition(
                base, prior, event, mutations, authoritative_index, requested_id
            )

    # A caller-provided event id makes a partially applied multi-file operation retryable.
    # Otherwise the primary's next sequence plus the frozen event supplies uniqueness.
    primary = mutations[authoritative_index]
    if primary.kind == "fields":
        current = _read_fields(primary.path)
        next_seq = int(current.get("event_seq") or 0) + 1
    elif primary.kind == "text":
        # A text mutation may author a brand-new canonical record (for example a
        # project pilot creating its first task).  Absence is the sequence-zero
        # witness already frozen by _plan_mutation, not an unreadable-state error.
        current = _read_fields(primary.path) if primary.path.exists() else {}
        next_seq = int(current.get("event_seq") or 0) + 1
    elif primary.kind == "json":
        current = _read_json(primary.path) if primary.path.exists() else {}
        next_seq = int(current.get("event_seq") or 0) + 1
    else:
        raise TransitionReceiptError("raw/text projection cannot be the authoritative sequence witness")
    seed = {**identity_seed, "event_seq": next_seq}
    transition_id = "transition-" + hashlib.sha256(_compact(seed)).hexdigest()[:32]
    event.setdefault("id", requested_id or transition_id)
    event["transition_id"] = transition_id

    planned = [_plan_mutation(base, mutation, transition_id, next_seq) for mutation in mutations]
    prepared = {"schema_version": 1, "kind": "transition-receipt", "id": transition_id,
                "event_seq": next_seq, "prepared_at": event["ts"], "event": event,
                "journal": journal,
                "authoritative_path": planned[authoritative_index]["path"],
                "mutations": planned}
    directory = _ensure_receipt_root(base) / transition_id
    receipt_path = directory / "prepared.json"
    if receipt_path.exists():
        prior = _load_prepared(receipt_path)
        if prior != prepared:
            raise TransitionReceiptError(f"transition receipt identity collision: {transition_id}")
    else:
        directory.mkdir(parents=True, mode=0o700)
        _fsync_dir(directory.parent)
        _atomic_json(receipt_path, prepared)
    _index_event(base, prepared)
    _failpoint("receipt-fsync")

    # Non-authoritative files first, authoritative commit marker last.
    order = [i for i in range(len(planned)) if i != authoritative_index] + [authoritative_index]
    for ordinal, index in enumerate(order, 1):
        mutation = planned[index]
        state = _witness_state(base, mutation)
        if state == "expected":
            continue
        if state != "before":
            raise TransitionReceiptError(
                f"transition {transition_id} cannot resume after unrelated state divergence: {mutation['path']}"
            )
        path = base / mutation["path"]
        if mutation["kind"] == "fields":
            _atomic_fields(path, mutation["changes"])
        elif mutation["kind"] == "json":
            _atomic_json(path, mutation["value"])
        else:
            _atomic_bytes(path, mutation["text"].encode("utf-8", "surrogateescape"))
        _failpoint(f"state-write-{ordinal}")
    _failpoint("state-write")
    if not project_receipt(base, prepared):
        raise TransitionReceiptError(f"transition {transition_id} did not commit all witnesses")
    return transition_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=os.environ.get("RECURSION_ROOT"))
    sub = parser.add_subparsers(dest="command", required=True)
    apply_fields = sub.add_parser("apply-fields")
    apply_fields.add_argument("path")
    apply_fields.add_argument("changes_json")
    apply_fields.add_argument("event_json")
    recover = sub.add_parser("recover")
    recover.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()
    base = Path(args.root or Path(__file__).resolve().parent.parent)
    held = os.environ.get("RECURSION_TASKCTL_LOCK_HELD") == "1"
    try:
        if args.command == "recover":
            print(json.dumps(recover_transitions(base, args.limit, taskctl_locked=held),
                             sort_keys=True, separators=(",", ":")))
        else:
            changes = json.loads(args.changes_json)
            event = json.loads(args.event_json)
            if not isinstance(changes, dict) or not isinstance(event, dict):
                raise TransitionReceiptError("apply-fields arguments must be JSON objects")
            path = Path(args.path)
            if not path.is_absolute():
                path = base / path
            print(commit_transition(base, [fields_mutation(path, changes)], event,
                                    taskctl_locked=held))
    except (OSError, ValueError, json.JSONDecodeError, TransitionReceiptError) as exc:
        print(f"transition-receipt: {exc}", file=os.sys.stderr)
        return 74
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

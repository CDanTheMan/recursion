#!/usr/bin/env python3
"""Durable, schema-checked queue for Head Hermes decisions.

The append-only ``state/decisions.jsonl`` journal remains the recovery source.  Individual
decision projections move through pending/running/succeeded/failed directories so an actuator
restart never depends on a singleton "latest" pointer.  The Phase 2 action journal remains the
authoritative record of whether actuation actually ran.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from jsonl_durable import (
    JsonlDurabilityError, acknowledge_jsonl, append_jsonl as durable_append_jsonl,
    find_jsonl_objects, read_jsonl_prefix, read_jsonl_since,
)


IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
TERMINAL_DIRS = ("succeeded", "failed")
QUEUE_DIRS = ("pending", "running", *TERMINAL_DIRS)
LEGACY_PRE_SCHEMA_NOOP_SHA256 = (
    # One-time Phase 8 compatibility allowlist. These are the exact immutable line digests
    # captured from the five 2026-08-07 pre-schema PAUSE noops. Adding any digest is a reviewed
    # code change; shape matching alone never turns an invalid current record into legacy state.
    "d589999830dbae9f212aaefaa95dab3562e89654c799426799f6ce71e3afe081",
    "726c5d82795ee7b42def62b2601f36d0662cb0f5de6f5e4886b11b77f597cc8a",
    "3bd740a2f8242645af25a01dda28f3db636d8e67fb066db1c6c39e793fb6d7ee",
    "160cee2fed8ead1e0154bb3635cb19588a3ad312fb4ae4c5501a3b9da4e7784b",
    "6c14cb6556f79e81bc3b1b4a0a4cb3c14593cb22902e7170410c990372678dda",
)
LEGACY_PRE_SCHEMA_NOOP_KEYS = frozenset({
    "args", "confidence", "cost_usd", "goal", "project", "provider", "text", "ts",
    "verb", "why", "wrong_if",
})
LEGACY_PRE_PROVENANCE_NOOP_SHA256 = (
    # Second reviewed compatibility entry, same rule as the block above: an exact immutable
    # line digest, never a shape match. This 2026-08-09 record carries schema_version 1 and
    # a normalized id, so it clears the pre-schema quarantine, but it predates the
    # decision_source/routed_decider provenance model. normalize() can recompute its payload
    # digest; it cannot invent an authority, and forging one is exactly what the provenance
    # check exists to prevent. The record is a noop that can never actuate, so it is
    # recorded and never replayed.
    "17e365c897961b6699ffc868b42e9ba469a1c6b5797798686224d6a4bb73165b",
)
LEGACY_REVIEWED_NOOP_SHA256 = LEGACY_PRE_SCHEMA_NOOP_SHA256 + LEGACY_PRE_PROVENANCE_NOOP_SHA256
LEGACY_PRE_PROVENANCE_NOOP_KEYS = frozenset({
    "actor", "args", "arguments", "confidence", "cost_usd", "goal", "goal_id", "id",
    "idempotency_key", "project", "provider", "reason", "schema_version", "status", "ts",
    "usage", "verb", "why", "wrong_if",
})


def root() -> Path:
    return Path(os.environ.get("RECURSION_ROOT") or Path(__file__).resolve().parent.parent)


def queue_root(base: Path) -> Path:
    return base / "state/decision-queue"


def fsync_dir(path: Path) -> None:
    if os.name == "nt":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def ensure_directory(path: Path) -> None:
    missing: list[Path] = []
    current = path
    while not current.exists():
        missing.append(current)
        if current.parent == current:
            break
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for created in reversed(missing):
        fsync_dir(created)
        fsync_dir(created.parent)


def atomic_json(path: Path, value: dict) -> None:
    ensure_directory(path.parent)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            json.dump(value, out, sort_keys=True, separators=(",", ":"))
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
        fsync_dir(path.parent)
    except BaseException:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise


def atomic_bytes(path: Path, value: bytes) -> None:
    ensure_directory(path.parent)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(value)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
        fsync_dir(path.parent)
    except BaseException:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise


def write_all(fd: int, value: bytes) -> None:
    view = memoryview(value)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("short append-only journal write")
        view = view[written:]


@contextmanager
def queue_lock(base: Path):
    lock_dir = base / "state/.locks"
    ensure_directory(lock_dir)
    lock_path = lock_dir / "decision-queue.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("decision queue lock is contended; refusing an unlocked mutation") from exc
        yield


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def decision_payload_digest(record: dict) -> str:
    """Bind an identity to every authority/effect-bearing decision field.

    Queue status, timestamps, provider accounting, and explanatory prose do not change what the
    actuator is allowed to do.  Everything that can change authority or the resulting effect is
    frozen here so an existing same-id projection cannot be reused with different content.
    """
    payload = {
        "actor": record.get("actor") or "",
        "verb": record.get("verb") or "",
        "args": record.get("args", record.get("arguments", [])) or [],
        "text": record.get("text") or "",
        "plan": record.get("plan") or None,
        "instruction_id": record.get("instruction_id") or None,
        "project": record.get("project") or "",
        "goal": record.get("goal", record.get("goal_id", "")) or "",
        "decision_source": record.get("decision_source") or "",
        "routed_decider": record.get("routed_decider") or "",
    }
    return digest(payload)


def assert_same_decision(existing: dict, incoming: dict, where: str) -> None:
    existing_digest = decision_payload_digest(existing)
    incoming_digest = decision_payload_digest(incoming)
    if existing.get("decision_payload_sha256") not in {None, existing_digest}:
        raise ValueError(f"stored decision authority/effect digest is inconsistent: {where}")
    if incoming.get("decision_payload_sha256") not in {None, incoming_digest}:
        raise ValueError(f"incoming decision authority/effect digest is inconsistent: {where}")
    if existing_digest != incoming_digest:
        raise ValueError(f"decision id collision with different authority/effect payload: {where}")


def normalize(raw: dict, stamp: str | None = None, provider: str | None = None,
              usage: dict | None = None) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("decision must be a JSON object")
    args = raw.get("args", raw.get("arguments", [])) or []
    verb = raw.get("verb", "")
    goal = raw.get("goal", raw.get("goal_id", ""))
    why = raw.get("why", raw.get("reason", ""))
    identity_payload = {
        "verb": verb,
        "args": args,
        "text": raw.get("text", "") or "",
        "plan": raw.get("plan") or None,
        "goal": goal,
        "instruction_id": raw.get("instruction_id") or None,
        "wrong_if": raw.get("wrong_if", ""),
    }
    key = raw.get("idempotency_key") or f"decision:{digest(identity_payload)}"
    decision_id = raw.get("id") or f"decision-{digest(key)[:24]}"
    if not IDENTIFIER.fullmatch(str(decision_id)):
        decision_id = f"decision-{digest(str(decision_id))[:24]}"
    record = dict(raw)
    record.update(
        {
            "schema_version": 1,
            "id": decision_id,
            "actor": raw.get("actor") or "head-hermes",
            "verb": verb,
            "arguments": args,
            "args": args,
            "reason": why,
            "why": why,
            "goal_id": goal,
            "goal": goal,
            "idempotency_key": key,
            "status": "queued",
        }
    )
    record["decision_payload_sha256"] = decision_payload_digest(record)
    if stamp:
        record["ts"] = stamp
    if provider:
        record["provider"] = provider
    if usage is not None:
        record["usage"] = usage
        record["cost_usd"] = usage.get("estimated_cost_usd")
    return record


def validate_record(base: Path, record: dict) -> None:
    validator = base / "scripts/validate-control-state.py"
    proc = subprocess.run(
        [sys.executable, str(validator), "decision"],
        input=json.dumps(record),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode:
        raise ValueError((proc.stderr or proc.stdout or "decision schema validation failed").strip())


def existing_path(base: Path, decision_id: str) -> Path | None:
    for state in QUEUE_DIRS:
        candidate = queue_root(base) / state / f"{decision_id}.json"
        if candidate.exists():
            return candidate
    return None


def validate_committed_journal_objects(data: bytes) -> list[dict]:
    """Fail closed on any complete non-object JSONL row without rewriting legacy objects."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"decision journal is not UTF-8: {exc}") from exc
    values: list[dict] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid decision journal line {number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"invalid decision journal line {number}: JSON object required")
        values.append(value)
    return values


def append_journal(base: Path, record: dict) -> bool:
    # enqueue() owns decision-queue.lock across this repair/validate/append boundary. Preserve the
    # exact reviewed legacy object rows: only an unterminated tail is removed, and complete rows
    # are inspected without normalization or rewriting.
    journal = base / "state/decisions.jsonl"
    ensure_directory(journal.parent)
    if journal.exists():
        repair_decision_journal_tail(base, journal)
    try:
        matches = find_jsonl_objects(journal, "id", record.get("id"))
    except JsonlDurabilityError as exc:
        raise ValueError(str(exc)) from exc
    if matches:
        for existing in matches:
            assert_same_decision(existing, record, f"journal decision {record.get('id')}")
        # A prior process may have died after fsync(journal) but before projection. Re-durabilize
        # the directory entry, reuse the semantic row, and let enqueue create the projection once.
        fsync_dir(journal.parent)
        return False
    try:
        outcome = durable_append_jsonl(journal, record, dedupe_field="id",
                                       dedupe_value=record.get("id"))
    except JsonlDurabilityError as exc:
        raise ValueError(str(exc)) from exc
    # Retain decision-queue's observable directory durability boundary even though the shared
    # append helper also persists a newly created journal entry.
    fsync_dir(journal.parent)
    return outcome.appended


def reviewed_legacy_marker(raw: dict, line: str, number: int, record: dict) -> dict | None:
    """Return a non-executable marker only for an exact reviewed pre-schema PAUSE noop."""
    source_sha256 = hashlib.sha256(line.encode()).hexdigest()
    if source_sha256 in LEGACY_PRE_PROVENANCE_NOOP_SHA256:
        # Post-schema, pre-provenance. Requiring the provenance fields to be ABSENT is what
        # keeps this from ever matching a record that merely carries a WRONG authority: such
        # a record must keep failing closed, not become legacy state.
        if (
            set(raw) != LEGACY_PRE_PROVENANCE_NOOP_KEYS
            or raw.get("verb") != "noop"
            or raw.get("args") != []
            or raw.get("arguments") != []
            or raw.get("actor") != "head-hermes"
            or raw.get("schema_version") != 1
            or raw.get("provider") != "openai-codex"
            or raw.get("project") != "recursion"
            or raw.get("decision_source") is not None
            or raw.get("routed_decider") is not None
            or not all(
                isinstance(raw.get(field), str) and raw[field]
                for field in ("goal", "goal_id", "id", "ts", "why", "wrong_if")
            )
        ):
            return None
        classification = "reviewed-pre-provenance-noop"
        disposition_reason = (
            "reviewed historical PAUSE noop predates the decision-provenance model and must"
            " not be replayed"
        )
    elif source_sha256 in LEGACY_PRE_SCHEMA_NOOP_SHA256:
        if (
            set(raw) != LEGACY_PRE_SCHEMA_NOOP_KEYS
            or raw.get("verb") != "noop"
            or raw.get("args") != []
            or raw.get("confidence") != "high"
            or raw.get("cost_usd") != "0.0"
            or raw.get("provider") != "openai-codex"
            or raw.get("text") != ""
            or raw.get("project") not in {"recursion", "gsc"}
            or not all(isinstance(raw.get(field), str) and raw[field] for field in ("goal", "ts", "why", "wrong_if"))
        ):
            return None
        classification = "reviewed-pre-schema-noop"
        disposition_reason = "reviewed historical PAUSE noop predates schema-v1 and must not be replayed"
    else:
        return None
    marker_id = f"legacy-decision-{source_sha256[:24]}"
    return {
        "schema_version": 1,
        "id": marker_id,
        "source": "state/decisions.jsonl",
        "source_line": number,
        "source_sha256": source_sha256,
        "source_goal_sha256": hashlib.sha256(raw["goal"].encode()).hexdigest(),
        "normalized_decision_id": record["id"],
        "project": raw["project"],
        "verb": "noop",
        "classification": classification,
        "disposition": "not-enqueued",
        "reason": disposition_reason,
    }


def legacy_marker_path(base: Path, marker: dict) -> Path:
    return queue_root(base) / "legacy" / f"{marker['id']}.json"


def enqueue(base: Path, record: dict, journal: bool) -> Path:
    validate_record(base, record)
    with queue_lock(base):
        present = existing_path(base, record["id"])
        if present:
            try:
                existing = json.loads(present.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"existing decision projection is unreadable: {present}") from exc
            assert_same_decision(existing, record, str(present))
            return present
        if journal:
            # Journal first: if the process dies before the projection rename, import-journal
            # reconstructs it.  The reverse ordering could lose the only recovery record.
            append_journal(base, record)
        target = queue_root(base) / "pending" / f"{record['id']}.json"
        atomic_json(target, record)
        return target


def quarantine_torn_tail(base: Path, journal: Path, data: bytes) -> bytes:
    """Preserve and remove only an unterminated final write; committed corruption still fails."""
    if not data or data.endswith(b"\n"):
        return data
    offset = data.rfind(b"\n") + 1
    committed, tail = data[:offset], data[offset:]
    tail_sha = hashlib.sha256(tail).hexdigest()
    before_sha = hashlib.sha256(data).hexdigest()
    quarantine = queue_root(base) / "quarantine"
    payload = quarantine / f"decision-journal-tail-{tail_sha[:24]}.bin"
    metadata_path = quarantine / f"decision-journal-tail-{tail_sha[:24]}.json"
    metadata = {
        "schema_version": 1,
        "source": "state/decisions.jsonl",
        "classification": "unterminated-final-write",
        "disposition": "quarantined-before-journal-truncate",
        "journal_sha256_before": before_sha,
        "journal_offset": offset,
        "tail_bytes": len(tail),
        "tail_sha256": tail_sha,
        "payload": payload.relative_to(base).as_posix(),
    }
    if payload.exists():
        if payload.read_bytes() != tail:
            raise ValueError(f"torn-tail quarantine payload mismatch: {payload.name}")
    else:
        atomic_bytes(payload, tail)
    if metadata_path.exists():
        try:
            observed = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid torn-tail quarantine metadata: {metadata_path.name}") from exc
        if observed != metadata:
            raise ValueError(f"torn-tail quarantine metadata mismatch: {metadata_path.name}")
    else:
        atomic_json(metadata_path, metadata)
    with journal.open("r+b") as source:
        source.truncate(offset)
        source.flush()
        os.fsync(source.fileno())
    fsync_dir(journal.parent)
    print(
        f"decision-queue: quarantined unterminated final journal write "
        f"sha256={tail_sha} bytes={len(tail)}",
        file=sys.stderr,
    )
    return committed


def repair_decision_journal_tail(base: Path, journal: Path) -> None:
    """Inspect one byte in the steady state; copy the journal only for a torn tail."""
    if not journal.is_file():
        return
    with journal.open("rb") as source:
        source.seek(0, os.SEEK_END)
        size = source.tell()
        if not size:
            return
        source.seek(-1, os.SEEK_END)
        if source.read(1) == b"\n":
            return
    quarantine_torn_tail(base, journal, journal.read_bytes())


def _line_text(raw: bytes) -> str:
    payload = raw[:-1] if raw.endswith(b"\n") else raw
    if payload.endswith(b"\r"):
        payload = payload[:-1]
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"decision journal is not UTF-8: {exc}") from exc


def _expected_legacy_markers(base: Path, journal: Path) -> dict[Path, dict]:
    """Revalidate the permanently bounded reviewed compatibility prefix."""
    markers: list[dict] = []
    for line in read_jsonl_prefix(journal, len(LEGACY_REVIEWED_NOOP_SHA256) + 1):
        if line.value is None:
            continue
        raw = line.value
        record = normalize(raw)
        try:
            validate_record(base, record)
        except ValueError as exc:
            marker = reviewed_legacy_marker(raw, _line_text(line.raw), line.sequence, record)
            if marker is None:
                raise ValueError(f"invalid decision journal line {line.sequence}: {exc}") from exc
            markers.append(marker)
            continue
        break
    digests = tuple(marker["source_sha256"] for marker in markers)
    if digests and digests != LEGACY_REVIEWED_NOOP_SHA256[: len(digests)]:
        raise ValueError("reviewed legacy decision prefix is incomplete or out of order")
    return {legacy_marker_path(base, marker): marker for marker in markers}


def _validate_legacy_marker_store(base: Path, expected_markers: dict[Path, dict]) -> None:
    legacy_root = queue_root(base) / "legacy"
    observed_markers = set(legacy_root.glob("*.json")) if legacy_root.exists() else set()
    unexpected = observed_markers - expected_markers.keys()
    if unexpected:
        raise ValueError(f"unexpected legacy decision marker: {sorted(unexpected)[0].name}")
    for path, expected in expected_markers.items():
        if not path.exists():
            continue
        try:
            observed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid legacy decision marker {path.name}: {exc}") from exc
        if observed != expected:
            raise ValueError(f"legacy decision marker mismatch: {path.name}")


def import_journal(base: Path) -> int:
    journal = base / "state/decisions.jsonl"
    if not journal.exists():
        legacy = queue_root(base) / "legacy"
        if legacy.exists() and any(legacy.glob("*.json")):
            raise ValueError("legacy decision markers exist without the append-only source journal")
        return 0
    with queue_lock(base):
        repair_decision_journal_tail(base, journal)
        expected_markers = _expected_legacy_markers(base, journal)
        _validate_legacy_marker_store(base, expected_markers)
        expected_by_digest = {
            marker["source_sha256"]: marker for marker in expected_markers.values()
        }
        batch = read_jsonl_since(journal, "decision-queue-import")
        prepared: list[tuple[str, dict]] = []
        for line in batch.lines:
            if line.value is None:
                continue
            raw = line.value
            record = normalize(raw)
            try:
                validate_record(base, record)
            except ValueError as exc:
                source_sha256 = hashlib.sha256(_line_text(line.raw).encode()).hexdigest()
                marker = expected_by_digest.get(source_sha256)
                if marker is not None and marker.get("source_line") == line.sequence:
                    prepared.append(("legacy", marker))
                    continue
                raise ValueError(f"invalid decision journal line {line.sequence}: {exc}") from exc
            prepared.append(("decision", record))

        # Validate every newly observed repeated identity against all indexed occurrences before
        # projecting any of the batch. Old rows were already validated before their checkpoint.
        prepared_decisions: dict[str, dict] = {}
        for kind, value in prepared:
            if kind != "decision":
                continue
            prior = prepared_decisions.get(value["id"])
            if prior is not None:
                assert_same_decision(prior, value, f"journal decision {value['id']}")
            else:
                prepared_decisions[value["id"]] = value
            for raw_match in find_jsonl_objects(journal, "id", value["id"]):
                assert_same_decision(normalize(raw_match), value,
                                     f"journal decision {value['id']}")

        imported = 0
        seen_decisions: set[str] = set()
        for kind, value in prepared:
            if kind == "legacy":
                path = legacy_marker_path(base, value)
                if not path.exists():
                    atomic_json(path, value)
                continue
            if value["id"] in seen_decisions:
                continue
            seen_decisions.add(value["id"])
            present = existing_path(base, value["id"])
            if present:
                try:
                    existing = json.loads(present.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise ValueError(f"existing decision projection is unreadable: {present}") from exc
                assert_same_decision(existing, value, str(present))
                continue
            target = queue_root(base) / "pending" / f"{value['id']}.json"
            atomic_json(target, value)
            imported += 1
        acknowledge_jsonl(journal, "decision-queue-import", batch)
        return imported


def validate_projection_authority(base: Path, path: Path) -> dict:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"decision projection is unreadable: {path}") from exc
    validate_record(base, record)
    assert_same_decision(record, record, str(path))
    decision_id = str(record.get("id") or "")
    try:
        matches = find_jsonl_objects(base / "state/decisions.jsonl", "id", decision_id)
    except JsonlDurabilityError as exc:
        raise ValueError(str(exc)) from exc
    if not matches:
        raise ValueError(f"decision projection lacks an authoritative journal row: {path}")
    for raw_match in matches:
        assert_same_decision(normalize(raw_match), record, str(path))
    return record


def claim(base: Path) -> Path | None:
    with queue_lock(base):
        running = sorted((queue_root(base) / "running").glob("*.json"))
        if running:
            validate_projection_authority(base, running[0])
            return running[0]
        pending = sorted((queue_root(base) / "pending").glob("*.json"))
        if not pending:
            return None
        source = pending[0]
        validate_projection_authority(base, source)
        target = queue_root(base) / "running" / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, target)
        fsync_dir(source.parent)
        fsync_dir(target.parent)
        return target


def claim_pending(base: Path, kind: str, excluded_projects: set[str], allowed_verbs: set[str]) -> Path | None:
    """Claim one pending projection without treating another running claim as singleton state."""
    if kind not in {"work", "non-work", "any"}:
        raise ValueError("claim kind must be work, non-work, or any")
    with queue_lock(base):
        for source in sorted((queue_root(base) / "pending").glob("*.json")):
            record = json.loads(source.read_text(encoding="utf-8"))
            is_work = record.get("verb") == "work"
            if allowed_verbs and str(record.get("verb") or "") not in allowed_verbs:
                continue
            if kind == "work" and not is_work:
                continue
            if kind == "non-work" and is_work:
                continue
            if str(record.get("project") or "") in excluded_projects:
                continue
            validate_projection_authority(base, source)
            target = queue_root(base) / "running" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, target)
            fsync_dir(source.parent); fsync_dir(target.parent)
            return target
    return None


def transition(base: Path, source: Path, outcome: str, evidence: str) -> Path:
    resolved = source.resolve()
    running_root = (queue_root(base) / "running").resolve()
    if resolved.parent != running_root or outcome not in (*TERMINAL_DIRS, "pending"):
        raise ValueError("refusing an invalid decision queue transition")
    with queue_lock(base):
        record = json.loads(resolved.read_text(encoding="utf-8"))
        if outcome == "pending":
            record["status"] = "queued"
        else:
            record["status"] = "executed" if outcome == "succeeded" else "refused"
            record["result_evidence"] = evidence
        target = queue_root(base) / outcome / resolved.name
        atomic_json(target, record)
        resolved.unlink()
        fsync_dir(resolved.parent)
        return target


def action_status(base: Path, decision_file: Path) -> str:
    record = json.loads(decision_file.read_text(encoding="utf-8"))
    key = record.get("idempotency_key") or f"decision:{record.get('id') or digest(record)}"
    action_id = "action-" + hashlib.sha256(str(key).encode()).hexdigest()[:24]
    path = base / "state/actions" / f"{action_id}.json"
    if not path.exists():
        return "absent"
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("status") or "unknown")
    except (OSError, json.JSONDecodeError):
        return "corrupt"


def load_usage(path: str | None) -> dict | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("normalize", "enqueue"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--stamp")
        cmd.add_argument("--provider")
        cmd.add_argument("--usage-file")
    sub.add_parser("import-journal")
    sub.add_parser("claim")
    pending = sub.add_parser("claim-pending")
    pending.add_argument("--kind", choices=("work", "non-work", "any"), default="any")
    pending.add_argument("--exclude-project", action="append", default=[])
    pending.add_argument("--verb", action="append", default=[])
    status = sub.add_parser("action-status")
    status.add_argument("file")
    for name in ("succeed", "fail", "defer"):
        cmd = sub.add_parser(name)
        cmd.add_argument("file")
        cmd.add_argument("evidence", nargs="?", default="")
    args = parser.parse_args()
    base = root()
    try:
        if args.command in {"normalize", "enqueue"}:
            record = normalize(
                json.load(sys.stdin),
                stamp=args.stamp,
                provider=args.provider,
                usage=load_usage(args.usage_file),
            )
            validate_record(base, record)
            if args.command == "enqueue":
                path = enqueue(base, record, journal=True)
                print(path)
            else:
                print(json.dumps(record, sort_keys=True, separators=(",", ":")))
        elif args.command == "import-journal":
            print(import_journal(base))
        elif args.command == "claim":
            path = claim(base)
            if path:
                print(path)
                return 0
            return 4
        elif args.command == "claim-pending":
            path = claim_pending(base, args.kind, set(args.exclude_project), set(args.verb))
            if path:
                print(path)
                return 0
            return 4
        elif args.command == "action-status":
            print(action_status(base, Path(args.file)))
        else:
            outcome = {"succeed": "succeeded", "fail": "failed", "defer": "pending"}[args.command]
            print(transition(base, Path(args.file), outcome, args.evidence))
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"decision-queue: {exc}", file=sys.stderr)
        return 73
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

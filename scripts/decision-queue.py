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


IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
TERMINAL_DIRS = ("succeeded", "failed")
QUEUE_DIRS = ("pending", "running", *TERMINAL_DIRS)


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


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


@contextmanager
def queue_lock(base: Path):
    lock_dir = base / "state/.locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
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


def append_journal(base: Path, record: dict) -> None:
    journal = base / "state/decisions.jsonl"
    journal.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(journal, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)


def enqueue(base: Path, record: dict, journal: bool) -> Path:
    validate_record(base, record)
    with queue_lock(base):
        present = existing_path(base, record["id"])
        if present:
            return present
        if journal:
            # Journal first: if the process dies before the projection rename, import-journal
            # reconstructs it.  The reverse ordering could lose the only recovery record.
            append_journal(base, record)
        target = queue_root(base) / "pending" / f"{record['id']}.json"
        atomic_json(target, record)
        return target


def import_journal(base: Path) -> int:
    journal = base / "state/decisions.jsonl"
    if not journal.exists():
        return 0
    imported = 0
    with queue_lock(base):
        for number, line in enumerate(journal.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = normalize(json.loads(line))
                validate_record(base, record)
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"invalid decision journal line {number}: {exc}") from exc
            if existing_path(base, record["id"]):
                continue
            target = queue_root(base) / "pending" / f"{record['id']}.json"
            atomic_json(target, record)
            imported += 1
    return imported


def claim(base: Path) -> Path | None:
    with queue_lock(base):
        running = sorted((queue_root(base) / "running").glob("*.json"))
        if running:
            return running[0]
        pending = sorted((queue_root(base) / "pending").glob("*.json"))
        if not pending:
            return None
        source = pending[0]
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

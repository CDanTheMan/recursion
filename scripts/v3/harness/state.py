"""On-disk run records. One JSON file per run, replaced atomically."""

from __future__ import annotations

import json
import os
import re
import threading
import time
from contextlib import contextmanager
from pathlib import Path

from scripts.v3.harness.config import ROOT
from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.redact import redact


_RUN_ID = re.compile(r"RUN-[0-9a-f]{16}")


def default_state_dir() -> Path:
    return ROOT / ".recursion" / "runs"


class RunStore:
    """Read and write run records under one directory."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._thread_lock = threading.Lock()

    def update(self, run_id: str, mutator) -> object:
        """Lock the store, mutate the record, and write it. Return the mutator's result."""

        with self._thread_lock:
            with self._locked():
                record = self._read(run_id) if self._path(run_id).is_file() else None
                if record is None:
                    record = {}
                result = mutator(record)
                if not isinstance(record.get("run_id"), str):
                    raise HarnessError("run record is missing run_id")
                self._write(record)
                return result

    def load(self, run_id: str) -> dict:
        with self._thread_lock:
            with self._locked():
                path = self._path(run_id)
                if not path.is_file():
                    raise HarnessError(f"unknown run {run_id}")
                return self._read(run_id)

    def list_runs(self) -> list[dict]:
        with self._thread_lock:
            with self._locked():
                if not self.root.is_dir():
                    return []
                found = []
                for path in sorted(self.root.glob("RUN-*.json")):
                    if not _RUN_ID.fullmatch(path.stem):
                        continue
                    found.append(_summary(self._read(path.stem)))
                return found

    def _path(self, run_id: str) -> Path:
        if _RUN_ID.fullmatch(run_id) is None:
            raise HarnessError(f"not a run id: {run_id}")
        return self.root / f"{run_id}.json"

    def _read(self, run_id: str) -> dict:
        path = self._path(run_id)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise HarnessError(f"malformed run record {path}") from exc
        if not isinstance(payload, dict) or payload.get("run_id") != run_id:
            raise HarnessError(f"malformed run record {path}")
        return payload

    def _write(self, record: dict) -> None:
        path = self._path(record["run_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".json.tmp")
        stored = redact(record)
        temporary.write_text(json.dumps(stored, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(path)

    @contextmanager
    def _locked(self):
        self.root.mkdir(parents=True, exist_ok=True)
        handle = open(self.root / ".lock", "a+b")
        try:
            if os.name == "nt":
                import msvcrt

                # Another handle may already have byte 0 locked. Windows
                # refuses to read that byte (PermissionError) instead of
                # waiting, so retry until LK_LOCK can run.
                deadline = time.monotonic() + 30
                while True:
                    try:
                        handle.seek(0)
                        if handle.read(1) != b"\0":
                            handle.seek(0)
                            handle.write(b"\0")
                            handle.flush()
                        handle.seek(0)
                        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
                        break
                    except PermissionError:
                        if time.monotonic() > deadline:
                            raise
                        time.sleep(0.05)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            if os.name == "nt":
                import msvcrt

                try:
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            handle.close()


def _summary(record: dict) -> dict:
    tasks = record.get("tasks") if isinstance(record.get("tasks"), list) else []
    completed = sum(1 for task in tasks if isinstance(task, dict) and task.get("status") == "completed")
    return {
        "completed": completed,
        "goal": record.get("goal"),
        "run_id": record.get("run_id"),
        "status": record.get("status"),
        "tasks": len(tasks),
    }

#!/usr/bin/env python3
"""Linux controls for runtime maintenance lock ownership and decision-queue serialization."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - the control is authoritative on Linux.
    fcntl = None  # type: ignore[assignment]


SOURCE = Path(__file__).resolve().parents[2]


def run_runtime(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SOURCE / "scripts/runtime-state.py"), *args],
        env={**os.environ, "RECURSION_ROOT": str(root), "RECURSION_LOCK_ATTEMPTS": "2",
             "RECURSION_LOCK_DELAY_S": "0.02"},
        text=True, capture_output=True, check=False,
    )


def witness(lock: Path, pid: int) -> None:
    lock.mkdir(parents=True)
    start = (Path("/proc") / str(pid) / "stat").read_text(encoding="utf-8").split()[21]
    (lock / "pid").write_text(f"{pid}\n", encoding="ascii")
    (lock / "start").write_text(f"{start}\n", encoding="ascii")


def main() -> int:
    if os.name == "nt" or fcntl is None:
        print("runtime-state-locks: SKIP (Linux production control)")
        return 0
    parent = Path(tempfile.mkdtemp(prefix="runtime-locks-"))
    root = parent / "runtime"
    snapshot = parent / "snapshot"
    try:
        (root / "state/.locks").mkdir(parents=True)
        (root / "state/PAUSE").write_text("test pause\n", encoding="utf-8")
        (root / "state/decisions.jsonl").write_text('{"id":"one"}\n', encoding="utf-8")
        lock_path = root / "state/.locks/decision-queue.lock"
        with lock_path.open("a+", encoding="utf-8") as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            blocked = run_runtime(root, "backup", str(snapshot))
        if blocked.returncode == 0 or snapshot.exists() or "decision queue lock is contended" not in blocked.stderr:
            print("FAIL  backup did not fail closed behind decision-queue.lock")
            print((blocked.stdout + blocked.stderr)[-500:])
            return 1

        for index, name in enumerate((
            "action-a.lock", "project-a.lock", "ws-a.lock", "planner-a.lock",
            "ledger.lock", "heavy-gate.lock",
        )):
            active = root / "state/.locks" / name
            witness(active, os.getpid())
            destination = parent / f"blocked-{index}"
            blocked = run_runtime(root, "backup", str(destination))
            shutil.rmtree(active)
            if blocked.returncode == 0 or destination.exists() or name not in blocked.stderr:
                print(f"FAIL  maintenance ignored active execution lock {name}")
                print((blocked.stdout + blocked.stderr)[-500:])
                return 1
        print("ok    action, project, legacy, planner, ledger, and heavy locks block maintenance")

        stale = root / "state/.locks/taskctl.lock"
        stale.mkdir()
        (stale / "pid").write_text("999999999\n", encoding="utf-8")
        (stale / "start").write_text("1\n", encoding="utf-8")
        result = run_runtime(root, "backup", str(snapshot))
        if result.returncode or not snapshot.is_dir() or stale.exists():
            print("FAIL  backup did not atomically reclaim a witnessed dead taskctl owner")
            print((result.stdout + result.stderr)[-500:])
            return 1

        crash_lock = root / "state/.locks/project-crash.lock"
        crashed = subprocess.run(
            [
                "bash", "-c", 'exec "$1" "$2" lock-acquire "$3" "$$"', "_",
                sys.executable, str(SOURCE / "scripts/runtime-state.py"), str(crash_lock),
            ],
            env={
                **os.environ, "RECURSION_ROOT": str(root),
                "RECURSION_LOCK_CRASH_AT": "after-candidate-pid",
            },
            text=True, capture_output=True, check=False,
        )
        candidates = list(crash_lock.parent.glob(f".{crash_lock.name}.candidate.*"))
        if crashed.returncode != 91 or crash_lock.exists() or len(candidates) != 1:
            print("FAIL  crash before witness completion published a canonical lock")
            return 1
        acquired = run_runtime(root, "lock-acquire", str(crash_lock), str(os.getpid()))
        released = run_runtime(root, "lock-release", str(crash_lock), str(os.getpid()))
        candidates = list(crash_lock.parent.glob(f".{crash_lock.name}.candidate.*"))
        if acquired.returncode or released.returncode or crash_lock.exists() or candidates:
            print("FAIL  a dead unpublished lock candidate was not reclaimed safely")
            print((acquired.stdout + acquired.stderr + released.stdout + released.stderr)[-500:])
            return 1
        print("ok    a lock crash cannot expose an ownerless canonical directory")

        sleeper = subprocess.Popen(["sleep", "30"])
        runtime_lock = root / "state/.locks/runtime-state.lock"
        try:
            witness(runtime_lock, sleeper.pid)
            raced = run_runtime(
                root, "lock-acquire", str(root / "state/.locks/project-race.lock"),
                str(os.getpid()),
            )
            if raced.returncode == 0 or "runtime-state maintenance is active" not in raced.stderr:
                print("FAIL  writer crossed an active runtime-state maintenance lock")
                return 1
        finally:
            sleeper.terminate()
            sleeper.wait(timeout=5)
            shutil.rmtree(runtime_lock, ignore_errors=True)
        print("ok    writer lock publication is interlocked with runtime maintenance")
        print("ok    runtime snapshot is serialized with the decision queue")
        print("ok    runtime maintenance reclaims only a witnessed dead taskctl owner")
        print("runtime-state-locks: ALL PASS")
        return 0
    finally:
        shutil.rmtree(parent, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

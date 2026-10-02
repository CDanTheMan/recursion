#!/usr/bin/env python3
"""FU-04 kickoff: non-destructive Windows platform probes.

Runs only safe, non-destructive probes on this host and records each result with its evidence
class. Destructive negative traces (descendant escape, forced kill, disk exhaustion, OOM,
suspend/resume, network interruption) are explicitly NOT run: they require a disposable,
Owner-approved test system and its own authorization.

    python -X utf8 -B experiments/v3/fu-04-os-conformance/probe_windows.py

Nothing here certifies any OS build. Every result is `locally_observed` for this one host only.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

NOT_RUN = [
    {"id": "PF01", "reason": "descendant escape/containment; requires a disposable approved scope"},
    {"id": "PF02", "reason": "parent death before registration; requires forced process kills"},
    {"id": "PF05", "reason": "atomic-replace crash durability; requires crash/power-loss target"},
    {"id": "PF08", "reason": "disk full/quota between write and flush; destructive to the host"},
    {"id": "PF09", "reason": "memory pressure/OOM; destructive to the host"},
    {"id": "PF11", "reason": "supervisor restart race with forced kills"},
    {"id": "PF12", "reason": "suspend/resume across a deadline; requires controllable power state"},
    {"id": "PF13", "reason": "network-storage interruption; requires an approved network mount"},
]


def atomic_replace() -> dict:
    d = Path(tempfile.mkdtemp(prefix="fu04_"))
    target, tmp = d / "target.bin", d / "target.tmp"
    target.write_bytes(b"old")
    with open(tmp, "wb") as f:
        f.write(b"new")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, target)
    ok = target.read_bytes() == b"new"
    return {
        "id": "atomic_replace",
        "mechanism": "os.replace + os.fsync on a local temp file",
        "evidence_class": "locally_observed",
        "status": "observed" if ok else "rejected",
        "detail": "rename replaced target contents atomically at the application-visible level; "
                  "this does NOT test crash or power-loss durability",
    }


def lock_release() -> dict:
    import msvcrt  # Windows only

    d = Path(tempfile.mkdtemp(prefix="fu04_"))
    p = d / "lock.bin"
    p.write_bytes(b"0123456789")
    with open(p, "r+b") as f:
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        locked = True
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
    return {
        "id": "lock_release",
        "mechanism": "msvcrt.locking LK_NBLCK then LK_UNLCK",
        "evidence_class": "locally_observed",
        "status": "observed" if locked else "unknown",
        "detail": "byte-range lock acquired and released; does not establish exit-time release "
                  "under forced termination",
    }


def monotonic_clock() -> dict:
    a = time.monotonic()
    time.sleep(0.02)
    b = time.monotonic()
    return {
        "id": "monotonic_clock",
        "mechanism": "time.monotonic across a short sleep",
        "evidence_class": "locally_observed",
        "status": "observed" if b >= a else "rejected",
        "detail": "monotonic reading is non-decreasing; monotonic vs boottime semantics not tested",
    }


def process_exit() -> dict:
    cp = subprocess.run(["cmd", "/c", "exit", "0"], capture_output=True)
    return {
        "id": "process_exit",
        "mechanism": "subprocess.run a short shell child",
        "evidence_class": "locally_observed",
        "status": "observed" if cp.returncode == 0 else "unknown",
        "detail": "child process exit status observed; this is 'process exited', not 'execution "
                  "settled'",
    }


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    probes = [atomic_replace(), lock_release(), monotonic_clock(), process_exit()]
    record = {
        "experiment": "fu-04-os-conformance kickoff",
        "evidence_class": "locally_observed (this host only)",
        "certification": "none; no OS build is certified",
        "host": {
            "platform": platform.platform(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "probes": probes,
        "destructive_not_run": NOT_RUN,
    }
    (RESULTS / "probes.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record["host"], indent=2))
    for p in probes:
        print(f"{p['status']:9} {p['id']}")
    print(f"not_run: {len(NOT_RUN)} destructive traces")
    return 0


if __name__ == "__main__":
    sys.exit(main())

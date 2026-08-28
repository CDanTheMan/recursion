#!/usr/bin/env python3
"""Hermetic race, path, PAUSE-admission, and ambiguity regressions for Phases 6/7."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SOURCE / "scripts"))

import remote_backend as rb  # noqa: E402
from remote_assignment import RemoteError  # noqa: E402

PYTHON = sys.executable
failures: list[str] = []


def check(condition: bool, label: str) -> None:
    print(("ok - " if condition else "FAIL - ") + label)
    if not condition:
        failures.append(label)


def child(base: Path, code: str, *args: str) -> subprocess.Popen:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SOURCE / "scripts") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.Popen([PYTHON, "-c", code, str(base), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


BEGIN = r'''
import sys
sys.path.insert(0, sys.argv[2] + r"/scripts")
import remote_backend as rb
from pathlib import Path
try:
    h = rb.begin_attempt(Path(sys.argv[1]), "grok-bot", dispatch_id="dispatch-race",
                         operation="dispatch", assignment_digest="d" * 64,
                         request_digest="r" * 64, max_attempts=3)
    print("replay" if h.replayed else "unreconciled" if h.unreconciled else "open")
except Exception as exc:
    print(type(exc).__name__ + ":" + str(exc))
'''

RECONCILE = r'''
import sys
sys.path.insert(0, sys.argv[2] + r"/scripts")
import remote_backend as rb
from pathlib import Path
try:
    rb.reconcile_attempt(Path(sys.argv[1]), "grok-bot", sys.argv[3],
                         observed="unknown", observer="race-test")
    print("closed")
except Exception as exc:
    print(type(exc).__name__ + ":" + str(exc))
'''

with tempfile.TemporaryDirectory(prefix="recursion-remote-hardening-") as raw:
    base = Path(raw)
    (base / "state").mkdir()

    first = child(base, BEGIN, str(SOURCE))
    second = child(base, BEGIN, str(SOURCE))
    first_out, first_err = first.communicate(timeout=30)
    second_out, second_err = second.communicate(timeout=30)
    rows = rb.read_attempts(base, "grok-bot")
    states = {line.strip() for line in (first_out + second_out).splitlines()}
    check(len(rows) == 1 and "open" in states and
          ("unreconciled" in states or "open" in states),
          "concurrent processes reserve one idempotency key atomically: " +
          repr((first_out, first_err, second_out, second_err)))

    handle = rb.begin_attempt(base, "grok-bot", dispatch_id="dispatch-race",
                              operation="dispatch", assignment_digest="d" * 64,
                              request_digest="r" * 64, max_attempts=3)
    rb.reconcile_attempt(base, "grok-bot", handle.attempt_id,
                         observed="landed", observer="hardening-test")
    third = child(base, BEGIN, str(SOURCE))
    fourth = child(base, BEGIN, str(SOURCE))
    third_out, third_err = third.communicate(timeout=30)
    fourth_out, fourth_err = fourth.communicate(timeout=30)
    rows = rb.read_attempts(base, "grok-bot")
    check(len(rows) == 2 and third_out.strip() == "replay" and fourth_out.strip() == "replay",
          "a closed successful reservation remains idempotent across processes: " +
          repr((third_out, third_err, fourth_out, fourth_err)))

    open_handle = rb.begin_attempt(base, "grok-bot", dispatch_id="dispatch-reconcile",
                                   operation="dispatch", assignment_digest="e" * 64,
                                   request_digest="s" * 64, max_attempts=3)
    left = child(base, RECONCILE, str(SOURCE), open_handle.attempt_id)
    right = child(base, RECONCILE, str(SOURCE), open_handle.attempt_id)
    left_out, left_err = left.communicate(timeout=30)
    right_out, right_err = right.communicate(timeout=30)
    check(sorted((left_out.strip(), right_out.strip())) == [
        "RemoteError:request-invalid: attempt " + open_handle.attempt_id +
        " is 'unreconciled', not open",
        "closed",
    ], "concurrent reconciliation has one transactional winner: " +
          repr((left_out, left_err, right_out, right_err)))

    path_base = base / "path"
    (path_base / "state").mkdir(parents=True)
    (path_base / "state" / "remote").write_text("not a directory", encoding="utf-8")
    try:
        rb.write_session(path_base, "grok-bot", "dispatch-path", {"a": 1})
        path_refused = False
    except RemoteError as exc:
        path_refused = exc.code == "request-invalid"
    check(path_refused, "runtime storage refuses a non-directory path component")

    del_path = path_base / "state" / "remote"
    del_path.unlink()
    outside = base / "outside"
    outside.mkdir()
    try:
        del_path.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        if os.name != "nt":
            raise AssertionError(f"symlink hardening test could not create its fixture: {exc}")
        junction = subprocess.run(["cmd", "/c", "mklink", "/J", str(del_path),
                                   str(outside)], capture_output=True, text=True)
        if junction.returncode != 0:
            raise AssertionError(f"link hardening fixture could not be created: {junction.stderr}")
    try:
        rb.write_session(path_base, "grok-bot", "dispatch-path", {"a": 1})
        symlink_refused = False
    except RemoteError as exc:
        symlink_refused = exc.code == "request-invalid"
    check(symlink_refused and not (outside / "grok-bot").exists(),
          "runtime storage refuses symlink traversal")

    journal_base = base / "journal"
    journal_parent = journal_base / "state" / "remote"
    journal_parent.mkdir(parents=True)
    journal_target = outside / "journal-target"
    journal_target.mkdir()
    journal_link = journal_parent / "grok-bot"
    try:
        journal_link.symlink_to(journal_target, target_is_directory=True)
    except OSError as exc:
        if os.name != "nt":
            raise AssertionError(f"journal symlink fixture could not be created: {exc}")
        junction = subprocess.run(["cmd", "/c", "mklink", "/J", str(journal_link),
                                   str(journal_target)], capture_output=True, text=True)
        if junction.returncode != 0:
            raise AssertionError(f"journal link fixture could not be created: {junction.stderr}")
    try:
        rb.read_attempts(journal_base, "grok-bot")
        journal_refused = False
    except RemoteError as exc:
        journal_refused = exc.code == "request-invalid"
    check(journal_refused, "journal reads refuse a symlinked storage directory")

    # The outbound lock gives PAUSE and send a total order: a pause setter waits for an
    # admitted operation, then the next operation sees PAUSE before its transport call.
    safe_base = base / "safe"
    (safe_base / "state").mkdir(parents=True)
    entered = threading.Event()
    release = threading.Event()

    def hold_admission() -> None:
        with rb.outbound_admission(safe_base, "grok-bot", "race probe"):
            entered.set()
            release.wait(5)

    holder = threading.Thread(target=hold_admission)
    holder.start()
    check(entered.wait(5), "outbound admission can be held for the PAUSE race proof")
    setter = child(safe_base, r'''
import sys
sys.path.insert(0, sys.argv[2] + r"/scripts")
import remote_backend as rb
from pathlib import Path
with rb.remote_state_lock(Path(sys.argv[1]), "pause-control"):
    rb.atomic_bytes(rb.pause_path(Path(sys.argv[1])), b"PAUSED race\n")
print("paused")
''', str(SOURCE))
    # The setter must not publish PAUSE while an outbound critical section owns the lock.
    try:
        setter.wait(timeout=0.2)
        blocked = setter.poll() is None
    except subprocess.TimeoutExpired:
        blocked = True
    check(blocked, "PAUSE publication waits behind an admitted outbound critical section")
    release.set()
    holder.join(timeout=10)
    setter_out, _ = setter.communicate(timeout=30)
    check(setter_out.strip() == "paused" and rb.is_paused(safe_base),
          "PAUSE publishes after admission and blocks the next operation")

if failures:
    print(f"{len(failures)} check(s) failed")
    raise SystemExit(1)
print("all checks passed")

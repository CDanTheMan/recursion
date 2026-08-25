#!/usr/bin/env python3
"""Mark systemd's exact Hermes gateway MainPID for intentional SIGTERM."""

from __future__ import annotations

from dataclasses import dataclass
import errno
import os
from pathlib import Path
import re
import select
import sys
import time
from typing import Sequence


EX_USAGE = 64
EX_IDENTITY_FAILURE = 65
EX_MARKER_FAILURE = 70
EX_INTERNAL_FAILURE = 71
EX_WAIT_TIMEOUT = 73
EX_WAIT_FAILURE = 74
EX_WAIT_CONFIG = 69
WAIT_SECONDS_ENV = "RECURSION_GATEWAY_PLANNED_STOP_WAIT_S"
MAX_WAIT_SECONDS = 50
MAX_LINUX_PID = 4_194_304
PROC_POLL_SECONDS = 0.05


@dataclass(frozen=True)
class ProcessWitness:
    pid: int
    pidfd: int | None
    start_time: bytes | None
    already_exited: bool = False


def configured_wait_seconds() -> int:
    raw = os.environ.get(WAIT_SECONDS_ENV, "").strip()
    if re.fullmatch(r"[1-9][0-9]*", raw) is None:
        raise ValueError(f"{WAIT_SECONDS_ENV} is not a canonical positive integer")
    seconds = int(raw)
    if seconds > MAX_WAIT_SECONDS:
        raise ValueError(f"{WAIT_SECONDS_ENV} exceeds the fail-closed maximum")
    return seconds


def read_proc_identity(target_pid: int) -> tuple[bytes, bytes] | None:
    try:
        raw = Path(f"/proc/{target_pid}/stat").read_bytes()
    except FileNotFoundError:
        return None
    close = raw.rfind(b")")
    if close < 0:
        raise OSError("process stat has no closing command delimiter")
    fields = raw[close + 2 :].split()
    if len(fields) < 20:
        raise OSError("process stat is truncated")
    return fields[0], fields[19]


def open_process_witness(target_pid: int) -> ProcessWitness:
    pidfd_open = getattr(os, "pidfd_open", None)
    if pidfd_open is not None:
        try:
            return ProcessWitness(target_pid, pidfd_open(target_pid, 0), None)
        except OSError as exc:
            if exc.errno == errno.ESRCH:
                return ProcessWitness(target_pid, None, None, already_exited=True)
            if exc.errno not in {errno.ENOSYS, errno.EPERM, errno.EACCES, errno.EINVAL}:
                raise

    identity = read_proc_identity(target_pid)
    if identity is None or identity[0] == b"Z":
        return ProcessWitness(target_pid, None, None, already_exited=True)
    return ProcessWitness(target_pid, None, identity[1])


def process_witness_exited(witness: ProcessWitness, timeout_ms: int) -> bool:
    if witness.already_exited:
        return True
    if witness.pidfd is not None:
        poller = select.poll()
        poller.register(witness.pidfd, select.POLLIN)
        events = poller.poll(timeout_ms)
        if not events:
            return False
        if all(mask & select.POLLIN for _, mask in events):
            return True
        raise OSError("pidfd poll returned without process-exit readiness")

    if witness.start_time is None:
        raise OSError("fallback witness has no process start time")
    deadline = time.monotonic() + (timeout_ms / 1000)
    while True:
        identity = read_proc_identity(witness.pid)
        if identity is None or identity[0] == b"Z" or identity[1] != witness.start_time:
            return True
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(PROC_POLL_SECONDS, remaining))


def close_process_witness(witness: ProcessWitness) -> None:
    if witness.pidfd is not None:
        os.close(witness.pidfd)


def main(argv: Sequence[str]) -> int:
    if (
        len(argv) != 1
        or len(argv[0]) > 10
        or re.fullmatch(r"[1-9][0-9]*", argv[0]) is None
    ):
        print("hermes-gateway-planned-stop: expected one canonical positive PID", file=sys.stderr)
        return EX_USAGE

    target_pid = int(argv[0])
    if target_pid <= 1 or target_pid > MAX_LINUX_PID:
        print("hermes-gateway-planned-stop: refusing unsafe PID", file=sys.stderr)
        return EX_USAGE

    try:
        wait_seconds = configured_wait_seconds()
    except ValueError as exc:
        print(f"hermes-gateway-planned-stop: invalid wait contract: {exc}", file=sys.stderr)
        return EX_WAIT_CONFIG

    try:
        witness = open_process_witness(target_pid)
    except (OSError, ValueError) as exc:
        print(
            "hermes-gateway-planned-stop: target identity unavailable "
            f"({type(exc).__name__})",
            file=sys.stderr,
        )
        return EX_IDENTITY_FAILURE

    try:
        try:
            if process_witness_exited(witness, 0):
                return 0
        except (OSError, ValueError) as exc:
            print(
                "hermes-gateway-planned-stop: initial target check failed "
                f"({type(exc).__name__})",
                file=sys.stderr,
            )
            return EX_IDENTITY_FAILURE

        try:
            from gateway.status import _get_planned_stop_marker_path, write_planned_stop_marker

            home_raw = os.environ.get("HERMES_HOME", "").strip()
            if not home_raw or not Path(home_raw).is_absolute():
                raise ValueError("HERMES_HOME is not an absolute path")
            home = Path(home_raw).resolve(strict=True)
            marker = Path(_get_planned_stop_marker_path()).resolve(strict=False)
            if marker == home or not marker.is_relative_to(home):
                raise ValueError("planned-stop marker is outside HERMES_HOME")

        except Exception as exc:
            print(
                "hermes-gateway-planned-stop: marker creation raised "
                f"({type(exc).__name__})",
                file=sys.stderr,
            )
            return EX_MARKER_FAILURE

        marker_error: Exception | None = None
        try:
            marked = write_planned_stop_marker(target_pid)
        except Exception as exc:
            marked = False
            marker_error = exc

        if marked is not True:
            # The writer may have persisted the marker before reporting an
            # error. Keep ExecStop active for the same bounded interval so a
            # watcher-owned drain cannot race systemd's fallback SIGTERM.
            try:
                process_witness_exited(witness, wait_seconds * 1000)
            except (OSError, ValueError) as exc:
                print(
                    "hermes-gateway-planned-stop: marker-failure wait failed "
                    f"({type(exc).__name__})",
                    file=sys.stderr,
                )
            detail = type(marker_error).__name__ if marker_error else "false return"
            print(
                f"hermes-gateway-planned-stop: marker creation failed ({detail})",
                file=sys.stderr,
            )
            return EX_MARKER_FAILURE

        # Hermes polls this marker on every platform. Keep ExecStop active
        # until that watcher-owned clean shutdown has completed, so systemd
        # cannot deliver a second marker-less SIGTERM to a draining MainPID.
        try:
            if process_witness_exited(witness, wait_seconds * 1000):
                return 0
        except (OSError, ValueError) as exc:
            print(
                "hermes-gateway-planned-stop: target wait failed "
                f"({type(exc).__name__})",
                file=sys.stderr,
            )
            return EX_WAIT_FAILURE

        # Preserve the identity-bound marker. If the watcher has not consumed
        # it, systemd's fallback SIGTERM can still classify the stop as
        # planned. If a slow drain already consumed it, the fallback may make
        # the main process exit 1. Either way this nonzero ExecStop result
        # keeps the timeout visible and never launders a genuine runtime exit.
        print("hermes-gateway-planned-stop: timed out waiting for target exit", file=sys.stderr)
        return EX_WAIT_TIMEOUT
    finally:
        close_process_witness(witness)


if __name__ == "__main__":
    try:
        exit_code = main(sys.argv[1:])
    except Exception as exc:
        print(
            "hermes-gateway-planned-stop: unexpected internal failure "
            f"({type(exc).__name__})",
            file=sys.stderr,
        )
        exit_code = EX_INTERNAL_FAILURE
    raise SystemExit(exit_code)

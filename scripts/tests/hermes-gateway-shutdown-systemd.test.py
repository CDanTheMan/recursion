#!/usr/bin/env python3
"""Disposable Linux proof of systemd's planned-stop ordering."""

from __future__ import annotations

import os
from pathlib import Path
import grp
import pwd
import shutil
import subprocess
import sys
import tempfile
import time
import uuid


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "scripts" / "hermes-gateway-planned-stop.py"
SYSTEMD_DIR = Path("/run/systemd/system")


STATUS_SOURCE = r'''\
import json
import os
from pathlib import Path


def _start_time(pid):
    return Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()[21]


def _marker_path():
    return Path(os.environ["FAKE_PLANNED_STOP_MARKER"])


def _get_planned_stop_marker_path():
    return _marker_path()


def write_planned_stop_marker(target_pid):
    record = {
        "target_pid": target_pid,
        "target_start_time": _start_time(target_pid),
    }
    _marker_path().write_text(json.dumps(record), encoding="utf-8")
    if os.environ.get("FAKE_MARKER_MODE") == "partial-raise":
        raise RuntimeError("synthetic failure after marker persistence")
    return True


def consume_planned_stop_marker_for_self():
    path = _marker_path()
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    path.unlink(missing_ok=True)
    return (
        record.get("target_pid") == os.getpid()
        and record.get("target_start_time") == _start_time(os.getpid())
    )
'''


GATEWAY_SOURCE = r'''\
import os
from pathlib import Path
import signal
import time

from gateway.status import consume_planned_stop_marker_for_self


def stop(_signum, _frame):
    raise SystemExit(0 if consume_planned_stop_marker_for_self() else 1)


signal.signal(signal.SIGTERM, stop)
Path(os.environ["FAKE_READY"]).write_text(str(os.getpid()), encoding="utf-8")
if os.environ.get("FAKE_RUNTIME_FAILURE") == "1":
    raise SystemExit(1)
while True:
    time.sleep(0.05)
'''


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, timeout=20, check=check)


def properties(unit: str) -> dict[str, str]:
    output = run(
        "systemctl",
        "show",
        unit,
        "--property=ActiveState,SubState,Result,ExecMainCode,ExecMainStatus,ExecStop,MainPID",
        "--no-pager",
    ).stdout
    return dict(line.split("=", 1) for line in output.splitlines() if "=" in line)


def main() -> int:
    if (
        os.geteuid() != 0
        or shutil.which("systemctl") is None
        or run("systemctl", "is-system-running", check=False).returncode != 0
    ):
        if os.environ.get("RECURSION_ALLOW_SYSTEMD_SHUTDOWN_SKIP") == "1":
            print("hermes-gateway-shutdown-systemd: EXPLICIT SKIP (root systemd unavailable)")
            return 0
        print("hermes-gateway-shutdown-systemd: FAIL (root systemd unavailable)", file=sys.stderr)
        return 77

    nobody = pwd.getpwnam("nobody")
    nobody_group = grp.getgrgid(nobody.pw_gid).gr_name
    base = Path(tempfile.mkdtemp(prefix="hermes-gateway-shutdown-", dir="/var/tmp"))
    os.chown(base, nobody.pw_uid, nobody.pw_gid)
    base.chmod(0o750)
    package = base / "gateway"
    package.mkdir(mode=0o750)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "status.py").write_text(STATUS_SOURCE, encoding="utf-8")
    gateway = base / "fake_gateway.py"
    gateway.write_text(GATEWAY_SOURCE, encoding="utf-8")
    for path in (package, package / "__init__.py", package / "status.py", gateway):
        os.chown(path, nobody.pw_uid, nobody.pw_gid)
    for path in (package / "__init__.py", package / "status.py", gateway):
        path.chmod(0o640)

    names: list[str] = []
    try:
        results: dict[str, dict[str, str]] = {}
        for case in ("unplanned", "planned", "partial-marker-failure", "runtime-failure"):
            suffix = uuid.uuid4().hex[:12]
            unit = f"recursion-gateway-stop-{suffix}.service"
            names.append(unit)
            marker = base / f"{suffix}.json"
            ready = base / f"{suffix}.ready"
            stop_line = (
                f"ExecStop=/usr/bin/python3 {ADAPTER} $MAINPID\n"
                if case != "unplanned"
                else ""
            )
            failure_line = "Environment=FAKE_RUNTIME_FAILURE=1\n" if case == "runtime-failure" else ""
            marker_mode_line = (
                "Environment=FAKE_MARKER_MODE=partial-raise\n"
                if case == "partial-marker-failure"
                else ""
            )
            restart = "no" if case == "runtime-failure" else "always"
            body = (
                "[Unit]\nDescription=Disposable Hermes gateway shutdown proof\n\n"
                f"[Service]\nType=simple\nUser=nobody\nGroup={nobody_group}\n"
                f"Environment=PYTHONPATH={base}\n"
                f"Environment=FAKE_PLANNED_STOP_MARKER={marker}\n"
                f"Environment=FAKE_READY={ready}\n"
                f"{failure_line}"
                f"{marker_mode_line}"
                f"Environment=HERMES_HOME={base}\n"
                f"ExecStart=/usr/bin/python3 {gateway}\n"
                f"{stop_line}"
                f"Restart={restart}\nKillMode=control-group\nKillSignal=SIGTERM\n"
                "TimeoutStopSec=10\nNoNewPrivileges=yes\nProtectSystem=strict\n"
                f"ReadWritePaths={base}\n"
            )
            unit_path = SYSTEMD_DIR / unit
            unit_path.write_text(body, encoding="utf-8")
            run("systemctl", "daemon-reload")
            run("systemctl", "start", unit)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and not ready.exists():
                time.sleep(0.05)
            if not ready.exists():
                raise RuntimeError(f"{unit} did not become ready: {properties(unit)}")
            if case == "runtime-failure":
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline and properties(unit).get("ActiveState") != "failed":
                    time.sleep(0.05)
            else:
                run("systemctl", "stop", unit, check=False)
            results[case] = properties(unit)

        unplanned = results["unplanned"]
        if not (
            unplanned.get("ActiveState") == "failed"
            and unplanned.get("Result") == "exit-code"
            and unplanned.get("ExecMainCode") == "1"
            and unplanned.get("ExecMainStatus") == "1"
            and unplanned.get("MainPID") == "0"
        ):
            raise AssertionError(f"unmarked SIGTERM did not reproduce exit-1 failure: {unplanned}")

        planned = results["planned"]
        if not (
            planned.get("ActiveState") == "inactive"
            and planned.get("Result") == "success"
            and planned.get("ExecMainCode") == "0"
            and planned.get("ExecMainStatus") == "0"
            and planned.get("MainPID") == "0"
        ):
            raise AssertionError(f"marked SIGTERM was not a clean manager stop: {planned}")

        runtime_failure = results["runtime-failure"]
        if not (
            runtime_failure.get("ActiveState") == "failed"
            and runtime_failure.get("Result") == "exit-code"
            and runtime_failure.get("ExecMainStatus") == "1"
            and runtime_failure.get("MainPID") == "0"
        ):
            raise AssertionError(f"genuine runtime exit 1 was masked: {runtime_failure}")

        partial_marker_failure = results["partial-marker-failure"]
        if not (
            partial_marker_failure.get("ActiveState") == "failed"
            and partial_marker_failure.get("Result") == "exit-code"
            and "code=exited" in partial_marker_failure.get("ExecStop", "")
            and "status=1" in partial_marker_failure.get("ExecStop", "")
            and partial_marker_failure.get("MainPID") == "0"
            and not any(base.glob("*.json"))
        ):
            raise AssertionError(
                "partial marker persistence did not fail closed: "
                f"{partial_marker_failure}"
            )

        print("hermes-gateway-shutdown-systemd: ALL PASS")
        return 0
    finally:
        for unit in names:
            run("systemctl", "stop", unit, check=False)
            run("systemctl", "reset-failed", unit, check=False)
            (SYSTEMD_DIR / unit).unlink(missing_ok=True)
        run("systemctl", "daemon-reload", check=False)
        shutil.rmtree(base, ignore_errors=False)


if __name__ == "__main__":
    raise SystemExit(main())

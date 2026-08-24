#!/usr/bin/env python3
"""Fail-closed controls for systemd-initiated Hermes gateway shutdown."""

from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "scripts" / "hermes-gateway-planned-stop.py"
UNIT = ROOT / "deploy" / "systemd" / "hermes-gateway.service"


FAKE_STATUS = r'''\
import json
import os
from pathlib import Path


def _start_time(pid):
    fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
    return fields[21]


def _marker_path():
    if os.environ.get("FAKE_MARKER_MODE") == "outside":
        return Path(os.environ["FAKE_OUTSIDE_MARKER"])
    return Path(os.environ["FAKE_PLANNED_STOP_MARKER"])


def _get_planned_stop_marker_path():
    return _marker_path()


def write_planned_stop_marker(target_pid):
    mode = os.environ.get("FAKE_MARKER_MODE", "ok")
    if mode == "false":
        return False
    if mode == "raise":
        raise RuntimeError("synthetic marker failure")
    record = {
        "target_pid": target_pid,
        "target_start_time": _start_time(target_pid),
    }
    _marker_path().write_text(json.dumps(record), encoding="utf-8")
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


FAKE_GATEWAY = r'''\
import os
from pathlib import Path
import signal
import sys
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


class GatewayShutdownContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="hermes-gateway-shutdown-")
        self.base = Path(self.temp.name)
        package = self.base / "gateway"
        package.mkdir()
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "status.py").write_text(FAKE_STATUS, encoding="utf-8")
        self.gateway = self.base / "fake_gateway.py"
        self.gateway.write_text(FAKE_GATEWAY, encoding="utf-8")
        self.home = self.base / "home"
        self.home.mkdir()
        self.marker = self.home / "planned-stop.json"
        self.outside_marker = self.base / "outside-planned-stop.json"
        self.ready = self.base / "ready"
        self.env = dict(os.environ)
        self.env.update(
            {
                "PYTHONPATH": str(self.base),
                "FAKE_PLANNED_STOP_MARKER": str(self.marker),
                "FAKE_OUTSIDE_MARKER": str(self.outside_marker),
                "FAKE_READY": str(self.ready),
                "HERMES_HOME": str(self.home),
            }
        )
        self.processes: list[subprocess.Popen[str]] = []

    def tearDown(self) -> None:
        for process in self.processes:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)
        self.temp.cleanup()

    def start_gateway(self, **environment: str) -> subprocess.Popen[str]:
        self.ready.unlink(missing_ok=True)
        env = dict(self.env)
        env.update(environment)
        process = subprocess.Popen(
            [sys.executable, str(self.gateway)],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.processes.append(process)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.ready.exists():
                self.assertEqual(self.ready.read_text(encoding="utf-8"), str(process.pid))
                return process
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self.fail(f"fake gateway exited early rc={process.returncode}: {stdout!r} {stderr!r}")
            time.sleep(0.02)
        process.kill()
        process.wait(timeout=5)
        self.fail("fake gateway did not become ready")

    def stop_gateway(self, process: subprocess.Popen[str]) -> int:
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=5)
        assert process.returncode is not None
        return process.returncode

    def run_adapter(self, *args: str, mode: str = "ok") -> subprocess.CompletedProcess[str]:
        env = dict(self.env)
        env["FAKE_MARKER_MODE"] = mode
        return subprocess.run(
            [sys.executable, str(ADAPTER), *args],
            env=env,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )

    def test_unit_marks_exact_main_pid_without_whitelisting_exit_one(self) -> None:
        unit = UNIT.read_text(encoding="utf-8")
        self.assertIn(
            "ExecStop=/usr/local/lib/hermes-agent/venv/bin/python "
            "/opt/recursion/scripts/hermes-gateway-planned-stop.py $MAINPID\n",
            unit,
        )
        directives = {
            key: value.split()
            for line in unit.splitlines()
            if "=" in line
            for key, value in (line.split("=", 1),)
        }
        self.assertNotIn("1", directives.get("SuccessExitStatus", []))
        self.assertNotIn("1", directives.get("RestartPreventExitStatus", []))
        self.assertIn("KillMode=control-group\n", unit)
        self.assertIn("KillSignal=SIGTERM\n", unit)

    def test_unmarked_manager_sigterm_reproduces_exit_one(self) -> None:
        process = self.start_gateway()
        self.assertEqual(self.stop_gateway(process), 1)
        self.assertFalse(self.marker.exists())

    def test_exact_marked_manager_sigterm_exits_zero(self) -> None:
        process = self.start_gateway()
        marked = self.run_adapter(str(process.pid))
        self.assertEqual(marked.returncode, 0, marked.stderr)
        record = json.loads(self.marker.read_text(encoding="utf-8"))
        self.assertEqual(record["target_pid"], process.pid)
        self.assertEqual(self.stop_gateway(process), 0)
        self.assertFalse(self.marker.exists())

    def test_genuine_runtime_exit_one_remains_failure(self) -> None:
        failed = self.start_gateway(FAKE_RUNTIME_FAILURE="1")
        failed.communicate(timeout=5)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(self.marker.exists())

    def test_marker_failure_and_unsafe_arguments_fail_closed(self) -> None:
        process = self.start_gateway()
        try:
            for args in ((), ("0",), ("1",), ("01",), (str(process.pid), "extra")):
                with self.subTest(args=args):
                    result = self.run_adapter(*args)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(self.marker.exists())
            for mode in ("false", "raise", "outside"):
                with self.subTest(mode=mode):
                    result = self.run_adapter(str(process.pid), mode=mode)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(self.marker.exists())
                    self.assertFalse(self.outside_marker.exists())
        finally:
            self.assertEqual(self.stop_gateway(process), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

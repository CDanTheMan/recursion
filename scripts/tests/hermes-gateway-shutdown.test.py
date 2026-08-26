#!/usr/bin/env python3
"""Fail-closed controls for systemd-initiated Hermes gateway shutdown."""

from __future__ import annotations

import errno
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "scripts" / "hermes-gateway-planned-stop.py"
UNIT = ROOT / "deploy" / "systemd" / "hermes-gateway.service"


FAKE_STATUS = r'''\
import json
import os
from pathlib import Path
import time


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
    audit = os.environ.get("FAKE_MARKER_AUDIT")
    if audit:
        Path(audit).write_text(json.dumps(record), encoding="utf-8")
    time.sleep(float(os.environ.get("FAKE_MARKER_WRITE_DELAY", "0")))
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
import threading
import time

from gateway.status import consume_planned_stop_marker_for_self


watcher_enabled = os.environ.get("FAKE_ENABLE_MARKER_WATCHER") == "1"
shutdown = {"exit_code": None, "deadline": None}


def stop(_signum, _frame):
    planned = consume_planned_stop_marker_for_self()
    if not watcher_enabled:
        raise SystemExit(0 if planned else 1)
    if not planned:
        shutdown["exit_code"] = 1
    elif shutdown["exit_code"] is None:
        shutdown["exit_code"] = 0
    if shutdown["deadline"] is None:
        shutdown["deadline"] = time.monotonic() + float(
            os.environ.get("FAKE_DRAIN_DELAY", "0.4")
        )


def watch_for_marker():
    marker = Path(os.environ["FAKE_PLANNED_STOP_MARKER"])
    while shutdown["deadline"] is None:
        if marker.exists():
            stop(None, None)
            return
        time.sleep(0.005)


signal.signal(signal.SIGTERM, stop)
Path(os.environ["FAKE_READY"]).write_text(str(os.getpid()), encoding="utf-8")
if os.environ.get("FAKE_RUNTIME_FAILURE") == "1":
    raise SystemExit(1)
if watcher_enabled:
    threading.Thread(target=watch_for_marker, daemon=True).start()
while True:
    if shutdown["deadline"] is not None and time.monotonic() >= shutdown["deadline"]:
        raise SystemExit(shutdown["exit_code"])
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
        self.marker_audit = self.base / "marker-audit.json"
        self.ready = self.base / "ready"
        self.env = dict(os.environ)
        self.env.update(
            {
                "PYTHONPATH": str(self.base),
                "FAKE_PLANNED_STOP_MARKER": str(self.marker),
                "FAKE_OUTSIDE_MARKER": str(self.outside_marker),
                "FAKE_MARKER_AUDIT": str(self.marker_audit),
                "FAKE_READY": str(self.ready),
                "HERMES_HOME": str(self.home),
                "RECURSION_GATEWAY_PLANNED_STOP_WAIT_S": "2",
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
            timeout=4,
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
        self.assertIn("Environment=RECURSION_GATEWAY_PLANNED_STOP_WAIT_S=45\n", unit)
        self.assertIn("TimeoutStopSec=60\n", unit)
        wait_seconds = int(
            next(
                line.rsplit("=", 1)[1]
                for line in unit.splitlines()
                if line.startswith("Environment=RECURSION_GATEWAY_PLANNED_STOP_WAIT_S=")
            )
        )
        timeout_seconds = int(
            next(
                line.split("=", 1)[1]
                for line in unit.splitlines()
                if line.startswith("TimeoutStopSec=")
            )
        )
        self.assertLess(wait_seconds, timeout_seconds)
        self.assertLessEqual(wait_seconds, 50)

    def test_unmarked_manager_sigterm_reproduces_exit_one(self) -> None:
        process = self.start_gateway()
        self.assertEqual(self.stop_gateway(process), 1)
        self.assertFalse(self.marker.exists())

    def test_exact_marked_watcher_stop_exits_zero(self) -> None:
        process = self.start_gateway(FAKE_ENABLE_MARKER_WATCHER="1")
        marked = self.run_adapter(str(process.pid))
        self.assertEqual(marked.returncode, 0, marked.stderr)
        process.communicate(timeout=5)
        self.assertEqual(process.returncode, 0)
        record = json.loads(self.marker_audit.read_text(encoding="utf-8"))
        self.assertEqual(record["target_pid"], process.pid)
        self.assertFalse(self.marker.exists())

    def test_marker_watcher_cannot_consume_before_systemd_sigterm(self) -> None:
        process = self.start_gateway(
            FAKE_ENABLE_MARKER_WATCHER="1",
            FAKE_MARKER_WRITE_DELAY="0.2",
            FAKE_DRAIN_DELAY="1.0",
        )
        started = time.monotonic()
        marked = self.run_adapter(str(process.pid))
        returned = time.monotonic()
        self.assertEqual(marked.returncode, 0, marked.stderr)
        self.assertIsNotNone(process.poll())
        process.communicate(timeout=5)
        self.assertEqual(process.returncode, 0)
        self.assertGreater(returned - started, 0.9)
        self.assertFalse(self.marker.exists())

    def test_invalid_wait_contract_fails_before_marker_creation(self) -> None:
        process = self.start_gateway()
        try:
            for value in ("", "0", "01", "51", "1.0", "unsafe"):
                with self.subTest(value=value):
                    self.env["RECURSION_GATEWAY_PLANNED_STOP_WAIT_S"] = value
                    result = self.run_adapter(str(process.pid))
                    self.assertEqual(result.returncode, 69)
                    self.assertFalse(self.marker.exists())
        finally:
            self.env["RECURSION_GATEWAY_PLANNED_STOP_WAIT_S"] = "2"
            self.assertEqual(self.stop_gateway(process), 1)

    def test_proc_identity_fallback_tracks_the_exact_process(self) -> None:
        spec = importlib.util.spec_from_file_location("gateway_planned_stop_adapter", ADAPTER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
            process = self.start_gateway()
            unavailable = OSError(errno.ENOSYS, "synthetic pidfd unavailability")
            with mock.patch.object(module.os, "pidfd_open", side_effect=unavailable, create=True):
                witness = module.open_process_witness(process.pid)
            self.assertIsNone(witness.pidfd)
            self.assertIsNotNone(witness.start_time)
            self.assertFalse(module.process_witness_exited(witness, 0))
            changed = module.ProcessWitness(process.pid, None, b"0")
            self.assertTrue(module.process_witness_exited(changed, 0))
            self.assertEqual(self.stop_gateway(process), 1)
            self.assertTrue(module.process_witness_exited(witness, 1000))
            module.close_process_witness(witness)
        finally:
            sys.modules.pop(spec.name, None)

    def test_genuine_runtime_exit_one_remains_failure(self) -> None:
        failed = self.start_gateway(FAKE_RUNTIME_FAILURE="1")
        failed.communicate(timeout=5)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(self.marker.exists())

    def test_already_exited_target_needs_no_marker(self) -> None:
        failed = self.start_gateway(FAKE_RUNTIME_FAILURE="1")
        failed.communicate(timeout=5)
        self.assertEqual(failed.returncode, 1)
        result = self.run_adapter(str(failed.pid))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.marker.exists())

    def test_timeout_preserves_marker_and_returns_distinct_failure(self) -> None:
        process = self.start_gateway()
        self.env["RECURSION_GATEWAY_PLANNED_STOP_WAIT_S"] = "1"
        try:
            result = self.run_adapter(str(process.pid))
            self.assertEqual(result.returncode, 73, result.stderr)
            record = json.loads(self.marker.read_text(encoding="utf-8"))
            self.assertEqual(record["target_pid"], process.pid)
        finally:
            self.env["RECURSION_GATEWAY_PLANNED_STOP_WAIT_S"] = "2"
            self.assertEqual(self.stop_gateway(process), 0)
        self.assertFalse(self.marker.exists())

    def test_identity_and_wait_errors_have_distinct_non_one_codes(self) -> None:
        spec = importlib.util.spec_from_file_location("gateway_planned_stop_error_adapter", ADAPTER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        process = self.start_gateway()
        gateway_module = types.ModuleType("gateway")
        gateway_module.__path__ = []
        status_module = types.ModuleType("gateway.status")
        status_module._get_planned_stop_marker_path = lambda: self.marker
        status_module.write_planned_stop_marker = lambda _pid: True
        gateway_module.status = status_module
        saved_gateway = sys.modules.get("gateway")
        saved_status = sys.modules.get("gateway.status")
        try:
            spec.loader.exec_module(module)
            with mock.patch.dict(module.os.environ, self.env):
                with mock.patch.object(
                    module,
                    "open_process_witness",
                    side_effect=OSError(errno.EIO, "synthetic identity failure"),
                ):
                    self.assertEqual(module.main([str(process.pid)]), 65)

                sys.modules["gateway"] = gateway_module
                sys.modules["gateway.status"] = status_module
                witness = module.ProcessWitness(process.pid, None, b"1")
                with (
                    mock.patch.object(module, "open_process_witness", return_value=witness),
                    mock.patch.object(module, "process_witness_exited", side_effect=[False, OSError()]),
                ):
                    self.assertEqual(module.main([str(process.pid)]), 74)
        finally:
            if saved_gateway is None:
                sys.modules.pop("gateway", None)
            else:
                sys.modules["gateway"] = saved_gateway
            if saved_status is None:
                sys.modules.pop("gateway.status", None)
            else:
                sys.modules["gateway.status"] = saved_status
            sys.modules.pop(spec.name, None)
            self.assertEqual(self.stop_gateway(process), 1)

    def test_marker_failure_and_unsafe_arguments_fail_closed(self) -> None:
        process = self.start_gateway()
        try:
            for args in (
                (),
                ("0",),
                ("1",),
                ("01",),
                ("4194305",),
                ("9" * 100,),
                (str(process.pid), "extra"),
            ):
                with self.subTest(args=args):
                    result = self.run_adapter(*args)
                    self.assertEqual(result.returncode, 64)
                    self.assertFalse(self.marker.exists())
            for mode in ("false", "raise", "outside"):
                with self.subTest(mode=mode):
                    result = self.run_adapter(str(process.pid), mode=mode)
                    self.assertEqual(result.returncode, 70)
                    self.assertFalse(self.marker.exists())
                    self.assertFalse(self.outside_marker.exists())
        finally:
            self.assertEqual(self.stop_gateway(process), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

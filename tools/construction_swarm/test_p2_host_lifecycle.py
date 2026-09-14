from __future__ import annotations

import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path

from tools.construction_swarm import p2_host_lifecycle as lifecycle


REPOSITORY = Path(__file__).resolve().parents[2]
MODULE = [
    sys.executable,
    "-X",
    "utf8",
    "-B",
    "-m",
    "tools.construction_swarm.p2_host_lifecycle",
]
CHILD_DEADLINE = 15


def _head():
    return subprocess.run(
        ["git", "-C", str(REPOSITORY), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        timeout=CHILD_DEADLINE,
    ).stdout.strip()


def _wait_until(predicate, timeout=8):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            last = predicate()
            if last:
                return last
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        time.sleep(0.02)
    raise AssertionError(f"condition not met within {timeout}s; last={last!r}")


def _pid_exists(pid):
    try:
        lifecycle.process_identity(pid)
        return True
    except lifecycle.LifecycleRefused:
        return False


class HostLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_alarm_handler = signal.signal(
            signal.SIGALRM,
            lambda _number, _frame: (_ for _ in ()).throw(
                TimeoutError("focused lifecycle suite exceeded 120 seconds")
            ),
        )
        signal.alarm(120)

    @classmethod
    def tearDownClass(cls):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, cls.previous_alarm_handler)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="p2-host-lifecycle-")
        self.root = Path(self.temporary.name)
        self.cgroup_root = Path("/sys/fs/cgroup") / (
            f"recursion-p2-test-{os.getpid()}-{uuid.uuid4().hex}"
        )
        self.cgroup_root.mkdir(mode=0o700)
        self.processes = []
        self.unrelated = []
        self.config_path = self.root / "config.json"
        self.spec_path = self.root / "fixture.json"
        self.state_root = self.root / "state"
        self.socket_path = self.root / "read.sock"
        self.pause_path = self.root / "PAUSE"
        self.grants_path = self.root / "grants.json"
        self.grants_path.write_text("[]\n", encoding="utf-8")
        self.launch_count_path = self.root / "launch-count"
        self.grandchild_pid_path = self.root / "grandchild-pid"
        self.write_config()
        self.write_fixture("stable")

    def tearDown(self):
        for process in self.processes:
            if process.poll() is None:
                process.send_signal(signal.SIGTERM)
        for process in self.processes:
            if process.poll() is None:
                try:
                    process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate(timeout=3)
            elif process.stdout is not None and not process.stdout.closed:
                process.communicate(timeout=1)
        for process in self.unrelated:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        for domain in self.cgroup_root.iterdir():
            if domain.is_dir():
                events = domain / "cgroup.events"
                if events.is_file() and "populated 1" in events.read_text(encoding="ascii"):
                    (domain / "cgroup.kill").write_text("1", encoding="ascii")
                    _wait_until(lambda: "populated 0" in events.read_text(encoding="ascii"), timeout=3)
                domain.rmdir()
        self.cgroup_root.rmdir()
        self.temporary.cleanup()

    def write_config(self, **overrides):
        value = {
            "version": 1,
            "enabled": True,
            "source_commit": _head(),
            "repository_root": str(REPOSITORY),
            "python_executable": sys.executable,
            "socket_path": str(self.socket_path),
            "grants_file": str(self.grants_path),
            "state_root": str(self.state_root),
            "cgroup_root": str(self.cgroup_root),
            "pause_path": str(self.pause_path),
            "restart_cap": 2,
            "backoff_initial_seconds": 0.05,
            "backoff_max_seconds": 0.1,
            "startup_timeout_seconds": 1.5,
            "shutdown_timeout_seconds": 2.5,
        }
        value.update(overrides)
        self.config_path.write_text(json.dumps(value), encoding="utf-8")
        return value

    def write_fixture(self, mode, *, grandchild=False, delay=0.03):
        value = {
            "mode": mode,
            "launch_count_path": str(self.launch_count_path),
            "grandchild_pid_path": str(self.grandchild_pid_path) if grandchild else "",
            "exit_delay_seconds": delay,
        }
        self.spec_path.write_text(json.dumps(value), encoding="utf-8")

    def start(self):
        process = subprocess.Popen(
            MODULE + ["run", "--config", str(self.config_path), "--fixture-spec", str(self.spec_path)],
            cwd=REPOSITORY,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.processes.append(process)
        return process

    def state(self):
        return json.loads((self.state_root / "state.json").read_text(encoding="utf-8"))

    def wait_health(self, health, timeout=8):
        return _wait_until(
            lambda: (value if (value := self.state()).get("health") == health else None),
            timeout,
        )

    def stop(self, controller):
        result = subprocess.run(
            MODULE + ["stop", "--state-root", str(self.state_root), "--timeout", "8"],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
            timeout=CHILD_DEADLINE,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        controller.communicate(timeout=CHILD_DEADLINE)
        self.assertEqual(controller.returncode, 0)
        return result

    def test_competing_watchdogs_elect_one_and_loser_starts_nothing(self):
        first = self.start()
        second = self.start()
        running = self.wait_health("running")
        loser = _wait_until(lambda: first if first.poll() is not None else second if second.poll() is not None else None)
        winner = second if loser is first else first
        loser_output, loser_error = loser.communicate(timeout=CHILD_DEADLINE)
        self.assertEqual(loser.returncode, 3, loser_output + loser_error)
        self.assertIn('"code": "watchdog_busy"', loser_output)
        self.assertIsNone(winner.poll())
        self.assertEqual(self.launch_count_path.read_text(encoding="ascii"), "1")
        self.assertTrue(_pid_exists(running["service_identity"]["pid"]))
        self.stop(winner)

    def test_client_disconnect_does_not_end_service_incarnation(self):
        controller = self.start()
        before = self.wait_health("running")
        for _ in range(3):
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(1)
                client.connect(str(self.socket_path))
        time.sleep(0.1)
        after = self.state()
        self.assertIsNone(controller.poll())
        self.assertEqual(after["health"], "running")
        self.assertEqual(after["service_incarnation"], before["service_incarnation"])
        self.assertEqual(after["service_identity"], before["service_identity"])
        self.stop(controller)

    def test_child_crash_restarts_with_bounded_backoff_and_new_fence(self):
        self.write_fixture("crash_once")
        controller = self.start()
        state = _wait_until(
            lambda: (
                value
                if (value := self.state()).get("health") == "running"
                and value.get("restart_count") == 1
                else None
            )
        )
        self.assertEqual(state["service_incarnation"], 2)
        self.assertEqual(state["service_fence"], 2)
        self.assertFalse(state["canonical_writer_authority"])
        self.assertEqual(self.launch_count_path.read_text(encoding="ascii"), "2")
        self.assertIsNone(controller.poll())
        self.stop(controller)

    def test_killed_child_reconciles_left_socket_before_restart(self):
        controller = self.start()
        first = self.wait_health("running")
        first_pid = first["service_identity"]["pid"]
        os.kill(first_pid, signal.SIGKILL)
        restarted = _wait_until(
            lambda: (
                value
                if (value := self.state()).get("health") == "running"
                and value.get("restart_count") == 1
                else None
            )
        )
        self.assertNotEqual(restarted["service_identity"]["pid"], first_pid)
        self.assertIn("restart_stale_socket_removed", restarted["reconciliation"])
        self.assertEqual(self.launch_count_path.read_text(encoding="ascii"), "2")
        self.stop(controller)

    def test_killed_leader_cleans_pinned_descendant_before_restart(self):
        self.write_fixture("stable", grandchild=True)
        controller = self.start()
        first = self.wait_health("running")
        old_grandchild = int(self.grandchild_pid_path.read_text(encoding="ascii"))
        domain = Path(first["service_domain"])
        _wait_until(lambda: len((domain / "cgroup.procs").read_text(encoding="ascii").splitlines()) >= 2)
        os.kill(first["service_identity"]["pid"], signal.SIGKILL)
        restarted = _wait_until(
            lambda: (
                value
                if (value := self.state()).get("health") == "running"
                and value.get("restart_count") == 1
                else None
            )
        )
        self.assertFalse(_pid_exists(old_grandchild))
        self.assertTrue(restarted["last_cleanup"]["quiescent"])
        self.assertEqual(restarted["last_cleanup"]["ownership_domain"], "cgroup_v2")
        self.stop(controller)

    def test_unobserved_fork_survives_leader_only_until_domain_cleanup(self):
        self.write_fixture("fork_then_crash_once", grandchild=True)
        controller = self.start()
        old_grandchild = int(_wait_until(
            lambda: self.grandchild_pid_path.read_text(encoding="ascii")
            if self.grandchild_pid_path.exists()
            else None
        ))
        restarted = _wait_until(
            lambda: (
                value
                if (value := self.state()).get("health") == "running"
                and value.get("restart_count") == 1
                else None
            )
        )
        self.assertFalse(_pid_exists(old_grandchild))
        self.assertTrue(restarted["last_cleanup"]["quiescent"])
        self.assertGreaterEqual(restarted["last_cleanup"]["member_count"], 1)
        self.assertEqual(restarted["last_cleanup"]["ownership_domain"], "cgroup_v2")
        self.stop(controller)

    def test_restart_exhaustion_is_explicit_outage(self):
        self.write_fixture("always_crash")
        controller = self.start()
        output, error = controller.communicate(timeout=CHILD_DEADLINE)
        self.assertEqual(controller.returncode, 4, output + error)
        state = self.state()
        self.assertEqual(state["health"], "outage")
        self.assertTrue(state["unavailable"])
        self.assertEqual(state["outage_reason"], "restart_exhausted")
        self.assertEqual(state["restart_count"], 2)
        self.assertEqual(state["service_incarnation"], 3)
        self.assertEqual(self.launch_count_path.read_text(encoding="ascii"), "3")

    def test_stale_pid_and_socket_preserve_unrelated_process(self):
        unrelated = subprocess.Popen(["sleep", "12"])
        self.unrelated.append(unrelated)
        identity = lifecycle.process_identity(unrelated.pid)
        identity["start_ticks"] += 1
        self.state_root.mkdir(mode=0o700)
        stale = {
            "state_version": lifecycle.STATE_VERSION,
            "source_commit": _head(),
            "service_incarnation": 7,
            "service_identity": identity,
        }
        lifecycle.StateStore(self.state_root).write(stale)
        stale_listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        stale_listener.bind(str(self.socket_path))
        stale_listener.close()

        controller = self.start()
        state = self.wait_health("running")
        self.assertEqual(state["service_incarnation"], 8)
        self.assertIn("stale_pid_unrelated_preserved", state["reconciliation"])
        self.assertIn("stale_socket_removed", state["reconciliation"])
        self.assertIsNone(unrelated.poll())
        self.stop(controller)

    def test_active_unowned_socket_is_refused_without_unlink(self):
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            listener.bind(str(self.socket_path))
            listener.listen(1)
            controller = self.start()
            output, error = controller.communicate(timeout=CHILD_DEADLINE)
            self.assertEqual(controller.returncode, 3, output + error)
            self.assertIn('"code": "socket_in_use"', output)
            self.assertTrue(self.socket_path.exists())
        finally:
            listener.close()

    def test_old_incarnation_health_update_is_rejected(self):
        controller = self.start()
        state = self.wait_health("running")
        state_path = self.state_root / "state.json"
        before = state_path.read_bytes()
        store = lifecycle.StateStore(self.state_root)
        with self.assertRaises(lifecycle.LifecycleRefused) as caught:
            store.publish_health(
                state["controller_id"],
                state["service_incarnation"] - 1,
                state["service_identity"],
                "outage",
            )
        self.assertEqual(caught.exception.code, "stale_incarnation")
        self.assertEqual(state_path.read_bytes(), before)
        self.stop(controller)

    def test_current_health_outage_updates_availability_atomically(self):
        controller = self.start()
        state = self.wait_health("running")
        updated = lifecycle.StateStore(self.state_root).publish_health(
            state["controller_id"],
            state["service_incarnation"],
            state["service_identity"],
            "outage",
        )
        self.assertEqual(updated["health"], "outage")
        self.assertTrue(updated["unavailable"])
        self.assertEqual(updated["outage_reason"], "health_published_outage")
        self.stop(controller)

    def test_stop_requires_matching_quiescent_cleanup_receipt(self):
        fake_root = self.root / "fake-controller-state"
        fake = subprocess.Popen([sys.executable, "-X", "utf8", "-B", "-c", "import time; time.sleep(12)"])
        self.unrelated.append(fake)
        state = {
            "state_version": lifecycle.STATE_VERSION,
            "source_commit": _head(),
            "controller_id": "fake-controller",
            "controller_identity": lifecycle.process_identity(fake.pid),
            "service_incarnation": 3,
            "health": "running",
            "unavailable": False,
        }
        lifecycle.StateStore(fake_root).write(state)
        with self.assertRaises(lifecycle.LifecycleRefused) as caught:
            lifecycle.request_stop(fake_root, 2)
        self.assertEqual(caught.exception.code, "stop_cleanup_unknown")
        fake.wait(timeout=CHILD_DEADLINE)

    def test_stop_cleans_only_owned_process_tree(self):
        self.write_fixture("stable", grandchild=True)
        unrelated = subprocess.Popen(["sleep", "12"])
        self.unrelated.append(unrelated)
        controller = self.start()
        state = self.wait_health("running")
        grandchild_pid = int(_wait_until(
            lambda: self.grandchild_pid_path.read_text(encoding="ascii")
            if self.grandchild_pid_path.exists()
            else None
        ))
        service_pid = state["service_identity"]["pid"]
        self.assertTrue(_pid_exists(service_pid))
        self.assertTrue(_pid_exists(grandchild_pid))
        self.stop(controller)
        stopped = self.state()
        self.assertEqual(stopped["health"], "stopped")
        self.assertTrue(stopped["unavailable"])
        self.assertTrue(stopped["cleanup"]["quiescent"])
        self.assertFalse(_pid_exists(service_pid))
        self.assertFalse(_pid_exists(grandchild_pid))
        self.assertIsNone(unrelated.poll())

    def test_pause_and_disabled_refuse_without_state_or_child(self):
        cases = ((False, False, "disabled"), (True, True, "paused"))
        for index, (enabled, paused, reason) in enumerate(cases):
            with self.subTest(reason=reason):
                case_root = self.root / f"refusal-{index}"
                case_root.mkdir()
                config = case_root / "config.json"
                grants = case_root / "grants.json"
                grants.write_text("[]", encoding="utf-8")
                pause = case_root / "PAUSE"
                if paused:
                    pause.write_text("operator pause\n", encoding="utf-8")
                value = {
                    "version": 1,
                    "enabled": enabled,
                    "source_commit": _head(),
                    "repository_root": str(REPOSITORY),
                    "python_executable": sys.executable,
                    "socket_path": str(case_root / "read.sock"),
                    "grants_file": str(grants),
                    "state_root": str(case_root / "state"),
                    "cgroup_root": str(self.cgroup_root),
                    "pause_path": str(pause),
                    "restart_cap": 1,
                    "backoff_initial_seconds": 0.05,
                    "backoff_max_seconds": 0.05,
                    "startup_timeout_seconds": 0.5,
                    "shutdown_timeout_seconds": 0.5,
                }
                config.write_text(json.dumps(value), encoding="utf-8")
                before_config = config.read_bytes()
                before_pause = pause.read_bytes() if paused else None
                result = subprocess.run(
                    MODULE + ["run", "--config", str(config), "--fixture-spec", str(self.spec_path)],
                    cwd=REPOSITORY,
                    capture_output=True,
                    text=True,
                    timeout=CHILD_DEADLINE,
                )
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertIn(f"lifecycle startup is {reason}", result.stdout)
                self.assertFalse((case_root / "state").exists())
                self.assertFalse((case_root / "read.sock").exists())
                self.assertEqual(config.read_bytes(), before_config)
                if paused:
                    self.assertEqual(pause.read_bytes(), before_pause)

    def test_production_command_is_fixed_and_contains_no_credential(self):
        config = lifecycle.load_config(self.config_path)
        command = lifecycle.Controller(config)._child_argv(9)
        self.assertEqual(command[:7], [sys.executable, "-X", "utf8", "-B", "-m", "tools.construction_swarm.p2_access", "serve"])
        self.assertIn("--grants", command)
        self.assertNotIn("--token", command)
        self.assertNotIn("--token-file", command)
        self.assertEqual(command[command.index("--fence") + 1], "9")
        source = (REPOSITORY / "tools/construction_swarm/p2_host_lifecycle.py").read_text(encoding="utf-8")
        self.assertNotIn("os.kill(", source)
        self.assertNotIn("os.killpg(", source)
        self.assertIn("pidfd_send_signal", source)

    @unittest.skipUnless(sys.platform.startswith("linux"), "WSL/Linux qualification only")
    def test_windows_wrapper_constructs_literal_injection_safe_argv(self):
        powershell = Path("/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
        self.assertTrue(powershell.is_file(), "Windows PowerShell is required for wrapper coverage")
        script = REPOSITORY / "tools/construction_swarm/p2_windows_watchdog.ps1"
        converted = subprocess.run(
            ["wslpath", "-w", str(script)],
            check=True,
            capture_output=True,
            text=True,
            timeout=CHILD_DEADLINE,
        ).stdout.strip()
        marker = self.root / "injection-marker"
        adversarial = f"/tmp/config $(touch {marker}); literal.json"
        result = subprocess.run(
            [
                str(powershell),
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                converted,
                "-Distro",
                "Ubuntu-24.04",
                "-LinuxRepository",
                "/opt/recursion foundry/repository",
                "-Config",
                adversarial,
                "-DryRun",
            ],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
            timeout=CHILD_DEADLINE,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        dry_run = json.loads(result.stdout)
        self.assertEqual(dry_run["executable"], "wsl.exe")
        self.assertFalse(dry_run["contains_credentials"])
        self.assertIn("/opt/recursion foundry/repository", dry_run["argument_list"])
        self.assertIn(adversarial, dry_run["argument_list"])
        self.assertFalse(marker.exists())
        lowered = " ".join(dry_run["argument_list"]).lower()
        self.assertNotIn("--token", lowered)
        source = script.read_text(encoding="utf-8")
        self.assertNotIn("Invoke-Expression", source)
        self.assertNotIn("Start-Process", source)


if __name__ == "__main__":
    unittest.main()

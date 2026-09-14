"""Real-process composition tests; no providers, workers, or production services."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

from . import p2_foundry_lifecycle as combined
from . import p2_host_lifecycle as host
from .test_p2_foundry_observation import _make_run, _tree_bytes, SOURCE_A, SOURCE_B

ROOT = Path(__file__).resolve().parents[2]
MODULE = [sys.executable, "-X", "utf8", "-B", "-m"]
DEADLINE = 15


def wait_for(predicate, timeout=4):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            result = predicate()
            if result:
                return result
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        time.sleep(.02)
    raise AssertionError("bounded condition did not become true")


class FoundryLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.started = time.monotonic()
        self.temp = tempfile.TemporaryDirectory(prefix="p2fi-")
        self.root = Path(self.temp.name)
        self.cg = Path("/sys/fs/cgroup") / (f"p2fi-test-{os.getpid()}-" + uuid.uuid4().hex)
        self.cg.mkdir(mode=0o700)
        (self.cg / "cgroup.subtree_control").write_text("+pids", encoding="ascii")
        self.processes = []
        self.controllers = []
        self.run_a = _make_run(self.root, "alpha-run", SOURCE_A)
        self.run_b = _make_run(self.root, "beta-run", SOURCE_B)
        self.run_old = _make_run(self.root, "old-run", SOURCE_A, old=True)
        self.before = self.inputs()
        self.socket = self.root / "read.sock"
        self.state_root = self.root / "state"
        self.grants_file = self.root / "grants.json"
        self.token_file = self.root / "token"
        self.bad_token = self.root / "bad-token"
        # Disposable randomized fixture tokens never enter argv or retained logs.
        token = uuid.uuid4().hex
        self.token_file.write_text(token, encoding="ascii")
        self.token_file.chmod(0o600)
        self.bad_token.write_text(uuid.uuid4().hex, encoding="ascii")
        self.bad_token.chmod(0o600)
        self.grants_file.write_text(json.dumps([{
            "token_sha256": hashlib.sha256(token.encode()).hexdigest(),
            "identity": "fixture-reader", "projects": ["alpha", "old", "missing"],
            "capabilities": ["read"],
        }]), encoding="utf-8")
        self.grants_file.chmod(0o600)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        self.config = {
            "version": 1, "enabled": True, "source_commit": head,
            "repository_root": str(ROOT), "python_executable": sys.executable,
            "socket_path": str(self.socket), "grants_file": str(self.grants_file),
            "state_root": str(self.state_root), "cgroup_root": str(self.cg),
            "pause_path": str(self.root / "PAUSE"), "restart_cap": 2,
            "backoff_initial_seconds": .05, "backoff_max_seconds": .1,
            "startup_timeout_seconds": 1.5, "shutdown_timeout_seconds": 2.0,
        }
        self.inner = self.root / "lifecycle.json"
        self.outer = self.root / "observation.json"
        self.mapping = {
            "alpha": str(self.run_a), "beta": str(self.run_b),
            "old": str(self.run_old), "missing": str(self.root / "absent-run"),
        }
        self.save()

    def inputs(self):
        return [_tree_bytes(p) for p in (self.run_a, self.run_b, self.run_old)]

    def save(self, **outer_changes):
        self.inner.write_text(json.dumps(self.config), encoding="utf-8")
        self.outer.write_text(json.dumps({
            "version": 1, "lifecycle_config": str(self.inner), "project_runs": self.mapping,
            **outer_changes,
        }), encoding="utf-8")

    def tearDown(self):
        try:
            for process in self.controllers:
                if process.poll() is None:
                    process.terminate()
            for process in self.processes:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate(timeout=3)
            for domain in self.cg.iterdir():
                if domain.is_dir():
                    (domain / "cgroup.kill").write_text("1", encoding="ascii")
                    wait_for(lambda: "populated 0" in
                             (domain / "cgroup.events").read_text(), 3)
                    domain.rmdir()
            self.assertEqual(self.before, self.inputs(), "observation changed source run bytes")
            self.assertLess(sum(len(v) for tree in self.inputs() for v in tree.values()),
                            32 * 1024 * 1024)
            self.assertLess(time.monotonic() - self.started, DEADLINE,
                            "owned test child lifetime exceeded packet bound")
        finally:
            self.cg.rmdir()
            self.temp.cleanup()

    def command(self, *args, input=None):
        return subprocess.run(MODULE + list(args), input=input, capture_output=True,
                              text=True, cwd=ROOT, timeout=DEADLINE)

    def start(self):
        process = subprocess.Popen(
            MODULE + ["tools.construction_swarm.p2_foundry_lifecycle", "run",
                      "--config", str(self.outer)],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.controllers.append(process)
        self.processes.append(process)
        return process

    def state(self):
        return json.loads((self.state_root / "state.json").read_text())

    def running(self, after=0):
        return wait_for(lambda: (s if (s := self.state())["health"] == "running"
                                 and s["service_incarnation"] > after else None))

    def cli(self, operation="status", project="alpha", token=None, *extra):
        result = self.command(
            "tools.construction_swarm.p2_cli", "--socket", str(self.socket),
            "--token-file", str(token or self.token_file), "--timeout", ".5",
            operation, "--project", project, *extra,
        )
        self.assertIn(result.returncode, (0, 2), result.stderr)
        return json.loads(result.stdout)

    def mcp(self):
        process = subprocess.Popen(
            MODULE + ["tools.construction_swarm.p2_mcp", "--socket", str(self.socket),
                      "--token-file", str(self.token_file), "--timeout", ".5"],
            cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        self.processes.append(process)
        return process

    def call(self, process, operation="status", project="alpha", **kwargs):
        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "construction_" + operation, "arguments": {"project": project, **kwargs},
        }}
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        self.assertTrue(select.select([process.stdout], [], [], 3)[0], "MCP response timeout")
        raw = process.stdout.readline(2 * 1024 * 1024 + 1)
        self.assertLessEqual(len(raw), 2 * 1024 * 1024)
        response = json.loads(raw)
        return json.loads(response["result"]["content"][0]["text"])

    def stop(self, process):
        result = self.command("tools.construction_swarm.p2_foundry_lifecycle", "stop",
                              "--state-root", str(self.state_root), "--timeout", "3")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        process.communicate(timeout=3)
        self.assertEqual(process.returncode, 0)
        state = self.state()
        self.assertTrue(state["cleanup"]["quiescent"])
        self.assertTrue(state["unavailable"])
        self.assertEqual(state["health"], "stopped")
        return state

    def crash_service(self):
        fd = host._open_verified_pidfd(self.state()["service_identity"])
        try:
            signal.pidfd_send_signal(fd, signal.SIGKILL)
        finally:
            os.close(fd)

    def test_real_cli_mcp_views_and_digest_bound_artifact(self):
        controller = self.start()
        state = self.running()
        response = self.cli()
        self.assertTrue(response["ok"])
        self.assertEqual(response["source_commit"], self.config["source_commit"])
        self.assertEqual(response["data"]["source_commit"], SOURCE_A)
        self.assertIsNone(response["data"]["canonical_authority"])
        self.assertIsNone(response["canonical_revision"])
        self.assertFalse(state["canonical_writer_authority"])
        bridge = self.mcp()
        items = self.call(bridge, "tasks")["data"]["items"]
        by_id = {item["task_id"]: item for item in items}
        self.assertFalse(by_id["returned"]["acceptance"]["independently_accepted"])
        self.assertTrue(by_id["accepted"]["acceptance"]["independently_accepted"])
        self.assertEqual(by_id["accepted"]["acceptance"]["scope"], "foundry_head_decision")
        self.assertTrue(by_id["unknown"]["attempt"]["held"])
        self.assertEqual(by_id["unknown"]["attempt"]["effect_state"], "unknown")
        item = self.call(bridge, "task", task_id="returned")["data"]["item"]
        handle = item["result"]["artifact_handle"]
        artifact = self.call(bridge, "artifact", handle=handle)["data"]
        # Decode only the adapter's bounded payload; digest is original filing evidence.
        data = base64.b64decode(artifact["content"])
        expected = (self.run_a / "attempts/returned/1/filing.json").read_bytes()
        self.assertEqual(data, expected)
        self.assertEqual(hashlib.sha256(data).hexdigest(), item["result"]["filing_sha256"])
        self.stop(controller)

    def test_authentication_project_isolation_and_replay_refusal(self):
        controller = self.start()
        self.running()
        self.assertFalse(self.cli(token=self.bad_token)["ok"])
        self.assertFalse(self.cli(project="beta")["ok"])
        bridge = self.mcp()
        self.assertFalse(self.call(bridge, project="beta")["ok"])
        replay = self.call(bridge, "events", after_cursor=0)
        self.assertFalse(replay["ok"])
        self.assertEqual(replay["error"]["code"], "replay_unsupported")
        self.stop(controller)

    def test_client_exit_preserves_identity_and_reconnects(self):
        controller = self.start()
        before = self.running()
        self.assertTrue(self.cli()["ok"])
        bridge = self.mcp()
        self.assertTrue(self.call(bridge)["ok"])
        bridge.stdin.close()
        bridge.stdin = None
        bridge.communicate(timeout=3)
        self.assertEqual(bridge.returncode, 0)
        after = self.state()
        self.assertEqual(before["service_identity"], after["service_identity"])
        self.assertEqual(before["service_incarnation"], after["service_incarnation"])
        self.assertIsNone(controller.poll())
        self.assertTrue(self.cli()["ok"])
        self.stop(controller)

    def test_restart_updates_persistent_mcp_and_preserves_stale_semantics(self):
        controller = self.start()
        before = self.running()
        bridge = self.mcp()
        first = self.call(bridge)
        old = self.call(bridge, project="old")
        self.assertEqual(old["freshness"]["state"], "stale")
        self.crash_service()
        after = self.running(before["service_incarnation"])
        second = self.call(bridge)
        self.assertTrue(second["ok"])
        self.assertGreater(second["service_fence"], first["service_fence"])
        self.assertNotEqual(second["service_instance"], first["service_instance"])
        self.assertEqual(second["data"]["run_id"], first["data"]["run_id"])
        self.assertNotEqual(after["service_identity"], before["service_identity"])
        self.assertEqual(self.call(bridge, project="old")["freshness"]["state"], "stale")
        self.assertEqual(self.call(bridge, "events", after_cursor=0)["error"]["code"],
                         "replay_unsupported")
        self.stop(controller)

    def test_outage_retains_labelled_mcp_cache_then_new_controller_recovers(self):
        controller = self.start()
        first = self.running()
        bridge = self.mcp()
        response = self.call(bridge)
        self.stop(controller)
        self.assertFalse(self.cli()["ok"])
        cached = self.call(bridge)
        self.assertEqual(cached["freshness"]["state"], "stale_disconnected")
        self.assertEqual(cached["service_fence"], response["service_fence"])
        successor = self.start()
        self.running(first["service_incarnation"])
        current = self.call(bridge)
        self.assertTrue(current["ok"])
        self.assertGreater(current["service_fence"], response["service_fence"])
        self.assertNotEqual(current["service_instance"], response["service_instance"])
        self.stop(successor)

    def test_process_readiness_does_not_claim_missing_data_health(self):
        controller = self.start()
        state = self.running()
        self.assertEqual(state["health_scope"], "process_and_socket_transition")
        self.assertEqual(state["application_health"], "read_response_required")
        missing = self.cli(project="missing")
        self.assertFalse(missing["ok"])
        self.assertEqual(missing["error"]["code"], "foundry_unavailable")
        self.assertFalse(self.state()["unavailable"])
        self.stop(controller)

    def test_stop_quiesces_only_owned_domain(self):
        canary = subprocess.Popen([sys.executable, "-B", "-c", "import time; time.sleep(12)"])
        self.processes.append(canary)
        controller = self.start()
        running = self.running()
        domain = Path(running["service_domain"])
        self.assertEqual((domain / "pids.max").read_text().strip(), "256")
        stopped = self.stop(controller)
        self.assertTrue(stopped["cleanup"]["quiescent"])
        self.assertIn("populated 0", (domain / "cgroup.events").read_text())
        self.assertIsNone(canary.poll())

    def test_competing_controllers_start_only_one_service(self):
        one, two = self.start(), self.start()
        state = self.running()
        loser = wait_for(lambda: one if one.poll() is not None else
                         two if two.poll() is not None else None)
        out, err = loser.communicate(timeout=3)
        self.assertEqual(loser.returncode, 3, out + err)
        self.assertIn("watchdog_busy", out)
        self.assertEqual(state["service_incarnation"], 1)
        self.assertEqual(self.state()["service_identity"], state["service_identity"])
        self.stop(two if loser is one else one)

    def test_pause_and_disabled_refuse_without_state_or_service(self):
        for disabled in (False, True):
            with self.subTest(disabled=disabled):
                self.config["enabled"] = not disabled
                if not disabled:
                    (self.root / "PAUSE").write_text("fixture pause")
                else:
                    (self.root / "PAUSE").unlink()
                self.save()
                process = self.start()
                out, err = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 3, out + err)
                self.assertIn("startup_refused", out)
                self.assertFalse(self.state_root.exists())
                self.assertFalse(self.socket.exists())

    def test_invalid_outer_config_and_mappings_refuse(self):
        cases = [
            {"version": True}, {"command": "arbitrary"},
            {"project_runs": []}, {"project_runs": {"alpha": ["not", "a", "path"]}},
            {"project_runs": {"alpha": "relative"}},
            {"project_runs": {"alpha": str(self.run_a), "beta": str(self.run_a / "../alpha-run")}},
            {"project_runs": {"alpha;touch marker": str(self.run_a)}},
            {"project_runs": {"alpha": "/tmp/invalid\npath"}},
        ]
        for change in cases:
            with self.subTest(change=change):
                self.save(**change)
                result = self.command("tools.construction_swarm.p2_foundry_lifecycle", "run",
                                      "--config", str(self.outer))
                self.assertEqual(result.returncode, 3, result.stderr)
                self.assertIn("configuration_refused", result.stdout)
                self.assertFalse(self.state_root.exists())

    def test_changed_prior_binding_refuses_before_domain_effect(self):
        controller = self.start()
        state = self.running()
        # Kill only our controller via a verified pidfd, preserving its service as a canary.
        fd = host._open_verified_pidfd(state["controller_identity"])
        try:
            signal.pidfd_send_signal(fd, signal.SIGKILL)
        finally:
            os.close(fd)
        controller.communicate(timeout=3)
        state_bytes = (self.state_root / "state.json").read_bytes()
        domain = Path(state["service_domain"])
        controls = [(domain / key).read_bytes() for key in ("pids.max", "cgroup.procs")]
        self.mapping["alpha"] = str(self.root / "different-run")
        self.save()
        rejected = self.start()
        out, err = rejected.communicate(timeout=3)
        self.assertEqual(rejected.returncode, 3, out + err)
        self.assertIn("prior observation binding differs", out)
        self.assertTrue(host.identity_matches(state["service_identity"]))
        self.assertEqual(state_bytes, (self.state_root / "state.json").read_bytes())
        self.assertEqual(controls, [(domain / key).read_bytes() for key in ("pids.max", "cgroup.procs")])
        # Restore the exact mapping; authorized takeover may now clean/restart the old service.
        self.mapping["alpha"] = str(self.run_a)
        self.save()
        successor = self.start()
        self.running(state["service_incarnation"])
        self.stop(successor)

    def test_empty_domain_endpoint_and_legacy_binding_refusals(self):
        controller = self.start()
        self.running()
        self.stop(controller)
        original = (self.state_root / "state.json").read_bytes()
        domain = Path(self.state()["service_domain"])
        original_socket = self.config["socket_path"]
        for variant in ("endpoint", "legacy"):
            if variant == "endpoint":
                self.config["socket_path"] = str(self.root / "other.sock")
            else:
                self.config["socket_path"] = original_socket
                state = json.loads(original)
                del state["observation_binding"]
                (self.state_root / "state.json").write_text(json.dumps(state))
            self.save()
            before = (self.state_root / "state.json").read_bytes()
            bound = (domain / "pids.max").read_bytes()
            process = self.start()
            out, err = process.communicate(timeout=3)
            self.assertEqual(process.returncode, 3, out + err)
            self.assertIn("state_refused", out)
            self.assertEqual(before, (self.state_root / "state.json").read_bytes())
            self.assertEqual(bound, (domain / "pids.max").read_bytes())
            (self.state_root / "state.json").write_bytes(original)

    def test_actual_service_crashes_exhaust_restart_cap(self):
        self.config["restart_cap"] = 1
        self.save()
        controller = self.start()
        first = self.running()
        self.crash_service()
        second = self.running(first["service_incarnation"])
        self.assertEqual(second["restart_count"], 1)
        self.crash_service()
        controller.communicate(timeout=4)
        self.assertEqual(controller.returncode, 4)
        state = self.state()
        self.assertEqual(state["health"], "outage")
        self.assertEqual(state["outage_reason"], "restart_exhausted")
        self.assertTrue(state["cleanup"]["quiescent"])
        self.assertEqual(state["service_incarnation"], second["service_incarnation"])
        self.assertFalse(self.cli()["ok"])

    def test_fixed_argv_contains_only_literal_mapping_arguments(self):
        shell_path = str(self.root / "literal;$(touch marker)")
        self.mapping["alpha"] = shell_path
        self.save()
        config, projects = combined.load_config(str(self.outer))
        controller = combined.FoundryController(config, projects)
        argv = controller._child_argv(7)
        self.assertEqual(argv[5], "tools.construction_swarm.p2_foundry_observation")
        self.assertIn("alpha=" + shell_path, argv)
        self.assertEqual(argv.count("--project-run"), len(self.mapping))
        self.assertNotIn(self.token_file.read_text(), "\n".join(argv))
        self.assertNotIn("--fixture-spec", argv)
        self.assertFalse((self.root / "marker").exists())


if __name__ == "__main__":
    unittest.main()
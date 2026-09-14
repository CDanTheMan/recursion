"""Acceptance gate for the P2 read-only construction access slice.

Windows CPython does not expose AF_UNIX on the qualified host.  The Windows
gate therefore launches this same module in the installed WSL2 distribution;
all protocol, CLI, MCP, disconnect, saturation, and filesystem cases then use
real Linux processes and Unix sockets.  The outer Windows process is only the
documented wsl.exe client/host seam.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock
from pathlib import Path

from .p2_access import (
    AccessClient, AccessRefused, FixtureCanonicalAdapter, MAX_REQUEST_BYTES,
    PROTOCOL_VERSION, READ_OPERATIONS,
)


REPO = Path(__file__).resolve().parents[2]
SOURCE_A = "1" * 40
SOURCE_B = "2" * 40


def _run(command, *, input_value=None, timeout=15):
    return subprocess.run(
        command,
        cwd=REPO,
        input=input_value,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


if not hasattr(socket, "AF_UNIX"):
    class WindowsWslGate(unittest.TestCase):
        def test_required_suite_through_actual_wsl2_process(self):
            drive = REPO.drive.rstrip(":").lower()
            relative = str(REPO)[len(REPO.drive):].lstrip("\\/").replace("\\", "/")
            linux_repo = f"/mnt/{drive}/{relative}"
            command = [
                "wsl.exe", "--cd", linux_repo, "env", "P2_NATIVE_SUITE=1",
                "python3", "-X", "utf8", "-B", "-m", "unittest", "-v",
                "tools.construction_swarm.test_p2_access",
            ]
            result = _run(command, timeout=115)
            # Preserve the nested case names as gate evidence in the outer run.
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
            self.assertEqual(result.returncode, 0, "WSL2 P2 gate failed")


if hasattr(socket, "AF_UNIX"):
    class P2AccessTests(unittest.TestCase):
        maxDiff = 4000

        def setUp(self):
            self.temporary = tempfile.TemporaryDirectory(prefix="p2-access-")
            self.root = Path(self.temporary.name)
            self.socket_path = self.root / "access.sock"
            self.fixture_path = self.root / "canonical.json"
            self.grants_path = self.root / "grants.json"
            self.alpha_token_path = self.root / "alpha.token"
            self.beta_token_path = self.root / "beta.token"
            self.alpha_token = "alpha-test-token-00000001"
            self.beta_token = "beta-test-token-00000002"
            self.alpha_token_path.write_text(self.alpha_token + "\n", encoding="utf-8")
            self.beta_token_path.write_text(self.beta_token + "\n", encoding="utf-8")
            grants = [
                {
                    "token_sha256": hashlib.sha256(self.alpha_token.encode()).hexdigest(),
                    "identity": "alpha-reader",
                    "projects": ["alpha"],
                    "capabilities": ["read"],
                },
                {
                    "token_sha256": hashlib.sha256(self.beta_token.encode()).hexdigest(),
                    "identity": "beta-reader",
                    "projects": ["beta"],
                    "capabilities": ["read"],
                },
            ]
            self.grants = grants
            self.grants_path.write_text(json.dumps(grants), encoding="utf-8")
            self.alpha_artifacts = self.root / "alpha-artifacts"
            self.beta_artifacts = self.root / "beta-artifacts"
            self.alpha_artifacts.mkdir()
            self.beta_artifacts.mkdir()
            (self.alpha_artifacts / "report.txt").write_text("bounded-alpha-report", encoding="utf-8")
            (self.alpha_artifacts / "large.bin").write_bytes(b"x" * 2048)
            (self.beta_artifacts / "secret.txt").write_text("beta-secret", encoding="utf-8")
            self.outside = self.root / "outside.txt"
            self.outside.write_text("outside", encoding="utf-8")
            (self.alpha_artifacts / "link.txt").symlink_to(self.outside)
            self.fixture = self._fixture()
            self.write_fixture()
            self.process = None
            self.start_service()

        def tearDown(self):
            self.stop_service()
            self.temporary.cleanup()

        def _fixture(self):
            observed = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            common_status = {
                "goal_progress": {"open": 2, "complete": 1},
                "current_sources": [SOURCE_A],
                "active_leases": [{"attempt": "attempt-1", "state": "busy"}],
                "counts": {"submitted": 1, "verified": 0, "review_pending": 1},
                "blockers": [{"id": "blocker-1", "next_actor": "owner"}],
                "route_quota": {"state": "unavailable"},
                "retained_holds": 1,
                "actual_spend": {"state": "unavailable"},
                "quality_indicators": {"accepted": False},
            }
            return {
                "canonical_revision": 7,
                "observed_at": observed,
                "last_event_cursor": 5,
                "projects": {
                    "alpha": {
                        "status": common_status,
                        "tasks": [
                            {"task_id": "a-1", "state": "running"},
                            {"task_id": "a-2", "state": "review_pending"},
                            {"task_id": "a-3", "state": "blocked"},
                        ],
                        "events": [
                            {"cursor": 3, "kind": "submitted", "task_id": "a-1"},
                            {"cursor": 4, "kind": "running", "task_id": "a-1"},
                            {"cursor": 5, "kind": "review_pending", "task_id": "a-2"},
                        ],
                        "event_history_start": 3,
                        "artifacts": [
                            {"handle": "alpha-report", "project": "alpha", "path": "report.txt",
                             "sha256": hashlib.sha256(b"bounded-alpha-report").hexdigest()},
                            {"handle": "escape", "project": "alpha", "path": "../outside.txt",
                             "sha256": hashlib.sha256(b"outside").hexdigest()},
                            {"handle": "symlink", "project": "alpha", "path": "link.txt",
                             "sha256": hashlib.sha256(b"outside").hexdigest()},
                            {"handle": "large", "project": "alpha", "path": "large.bin",
                             "sha256": hashlib.sha256(b"x" * 2048).hexdigest()},
                            {"handle": "misbound", "project": "beta", "path": "report.txt",
                             "sha256": hashlib.sha256(b"bounded-alpha-report").hexdigest()},
                        ],
                    },
                    "beta": {
                        "status": {**common_status, "active_leases": []},
                        "tasks": [{"task_id": "b-secret", "state": "open"}],
                        "events": [{"cursor": 5, "kind": "created", "task_id": "b-secret"}],
                        "event_history_start": 5,
                        "artifacts": [
                            {"handle": "beta-secret", "project": "beta", "path": "secret.txt",
                             "sha256": hashlib.sha256(b"beta-secret").hexdigest()},
                        ],
                    },
                },
            }

        def write_fixture(self):
            temporary = self.fixture_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.fixture), encoding="utf-8")
            os.replace(temporary, self.fixture_path)

        def start_service(self, *, fixture=True, source=SOURCE_A, instance=None):
            self.assertIsNone(self.process)
            self.socket_path.unlink(missing_ok=True)
            command = [
                sys.executable, "-X", "utf8", "-B", "-m", "tools.construction_swarm.p2_access",
                "serve", "--socket", str(self.socket_path), "--source-commit", source,
                "--grants", str(self.grants_path), "--max-readers", "2", "--max-page-size", "2",
                "--max-connections", "4", "--request-timeout", "1.2",
                "--max-artifact-read", "64", "--max-artifact-size", "1024",
            ]
            if instance:
                command += ["--instance-id", instance]
            if fixture:
                command += [
                    "--fixture-canonical", str(self.fixture_path),
                    "--artifact-root", "alpha=" + str(self.alpha_artifacts),
                    "--artifact-root", "beta=" + str(self.beta_artifacts),
                ]
            self.process = subprocess.Popen(
                command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            deadline = time.monotonic() + 10
            while not self.socket_path.exists() and time.monotonic() < deadline:
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    self.fail(f"service exited before ready: {stdout!r} {stderr!r}")
                time.sleep(0.01)
            self.assertTrue(self.socket_path.exists(), "service Unix socket did not appear")

        def stop_service(self):
            if self.process is None:
                return
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(5)
            self.process.communicate(timeout=1)
            self.process = None
            deadline = time.monotonic() + 1
            while self.socket_path.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.socket_path.unlink(missing_ok=True)

        def client(self, token=None, cache=None):
            return AccessClient(self.socket_path, token or self.alpha_token, timeout=2, cache_path=cache)

        def cli(self, operation, *arguments, token_path=None):
            command = [
                sys.executable, "-X", "utf8", "-B", "-m", "tools.construction_swarm.p2_cli",
                "--socket", str(self.socket_path), "--token-file", str(token_path or self.alpha_token_path),
                operation, *arguments,
            ]
            result = _run(command)
            self.assertIn(result.returncode, {0, 2}, (result.stdout, result.stderr))
            return result, json.loads(result.stdout)

        def common(self, response):
            self.assertEqual(response["protocol_version"], PROTOCOL_VERSION)
            self.assertEqual(response["source_commit"], SOURCE_A)
            self.assertEqual(response["caller_identity"], "alpha-reader")
            self.assertIsInstance(response["service_instance"], str)
            self.assertIn("service_fence", response)
            self.assertIn("observation_time", response)
            self.assertIn("freshness", response)
            self.assertIn("last_event_cursor", response)
            self.assertIn("unavailable_fields", response)

        def raw_request(self, request_bytes):
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
                channel.settimeout(2)
                channel.connect(str(self.socket_path))
                stream = channel.makefile("rwb", buffering=0)
                auth = {
                    "protocol_version": PROTOCOL_VERSION,
                    "op": "authenticate",
                    "token": self.alpha_token,
                    "request_id": "auth",
                }
                stream.write(json.dumps(auth).encode() + b"\n")
                json.loads(stream.readline())
                stream.write(request_bytes)
                return json.loads(stream.readline())

        def mcp(self, requests):
            lines = "".join(json.dumps(item) + "\n" for item in requests)
            command = [
                sys.executable, "-X", "utf8", "-B", "-m", "tools.construction_swarm.p2_mcp",
                "--socket", str(self.socket_path), "--token-file", str(self.alpha_token_path),
                "--cache", str(self.root / "mcp-cache.json"),
            ]
            result = _run(command, input_value=lines)
            self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
            return [json.loads(line) for line in result.stdout.splitlines()]

        def test_two_independent_cli_processes_see_same_bounded_snapshot(self):
            results = []

            def invoke():
                results.append(self.cli("tasks", "--project", "alpha", "--limit", "2")[1])

            first = threading.Thread(target=invoke)
            second = threading.Thread(target=invoke)
            first.start()
            second.start()
            first.join(15)
            second.join(15)
            self.assertFalse(first.is_alive() or second.is_alive())
            self.assertEqual(len(results), 2)
            for response in results:
                self.common(response)
                self.assertTrue(response["ok"])
                self.assertEqual(len(response["data"]["items"]), 2)
                self.assertEqual(response["data"]["next_page_token"], 2)
            stable = ("service_instance", "canonical_revision", "last_event_cursor", "data", "source_commit")
            self.assertEqual({key: results[0][key] for key in stable}, {key: results[1][key] for key in stable})

        def test_project_isolation_and_spoofed_actor_are_refused(self):
            cross = self.client().request("status", {"project": "beta"})
            self.assertFalse(cross["ok"])
            self.assertEqual(cross["error"]["code"], "permission_denied")
            spoofed = self.client().request("status", {"project": "alpha", "actor": "owner"})
            self.assertFalse(spoofed["ok"])
            self.assertEqual(spoofed["error"]["code"], "permission_denied")
            hidden = self.client().request("task", {"project": "alpha", "task_id": "b-secret"})
            self.assertFalse(hidden["ok"])
            self.assertEqual(hidden["error"]["code"], "not_found")

        def test_only_read_verbs_are_exposed_and_mutations_cannot_launch(self):
            before = hashlib.sha256(self.fixture_path.read_bytes()).hexdigest()
            self.assertEqual(READ_OPERATIONS, {"status", "tasks", "task", "events", "artifact"})
            for operation in ("stop", "submit", "launch_provider", "mutate"):
                request = {
                    "protocol_version": PROTOCOL_VERSION, "op": operation,
                    "request_id": operation, "params": {"project": "alpha"},
                }
                response = self.raw_request(json.dumps(request).encode() + b"\n")
                self.assertFalse(response["ok"])
                self.assertEqual(response["error"]["code"], "mutation_refused")
            listed = self.mcp([
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            ])[1]["result"]["tools"]
            self.assertEqual({item["name"] for item in listed}, {
                "construction_status", "construction_tasks", "construction_task",
                "construction_events", "construction_artifact",
            })
            self.assertEqual(hashlib.sha256(self.fixture_path.read_bytes()).hexdigest(), before)
            self.assertFalse((self.root / "provider-launched").exists())

        def test_missing_canonical_adapter_and_ledger_are_explicitly_unavailable(self):
            self.stop_service()
            self.start_service(fixture=False)
            response = self.client().request("status", {"project": "alpha"})
            self.common(response)
            self.assertTrue(response["ok"])
            self.assertIsNone(response["data"]["active_leases"])
            self.assertIsNone(response["canonical_revision"])
            self.assertIsNone(response["last_event_cursor"])
            self.assertTrue(response["freshness"]["stale"])
            self.assertIn("canonical.adapter", response["unavailable_fields"])
            self.assertIn("canonical.ledger", response["unavailable_fields"])
            self.assertIn("status.active_leases", response["unavailable_fields"])

        def test_server_loss_returns_only_labelled_stale_cached_snapshot(self):
            cache = self.root / "client-cache.json"
            client = self.client(cache=cache)
            current = client.request("status", {"project": "alpha"})
            self.assertTrue(current["ok"])
            original_leases = current["data"]["active_leases"]
            self.stop_service()
            stale = client.request("status", {"project": "alpha"}, allow_stale=True)
            self.assertTrue(stale["ok"])
            self.assertEqual(stale["data"]["active_leases"], original_leases)
            self.assertEqual(stale["freshness"]["state"], "stale_disconnected")
            self.assertTrue(stale["freshness"]["stale"])
            self.assertIn("service.connection", stale["unavailable_fields"])
            with self.assertRaises(AccessRefused):
                client.request("tasks", {"project": "alpha", "limit": 1, "page_token": 0})

        def test_stale_cache_is_bound_to_credential_and_service_endpoint(self):
            cache = self.root / "shared-cache.json"
            alpha = self.client(cache=cache)
            self.assertTrue(alpha.request("status", {"project": "alpha"})["ok"])
            beta = self.client(token=self.beta_token, cache=cache)
            denied = beta.request("status", {"project": "alpha"})
            self.assertFalse(denied["ok"])
            self.assertEqual(denied["error"]["code"], "permission_denied")
            self.stop_service()
            with self.assertRaises(AccessRefused):
                beta.request("status", {"project": "alpha"}, allow_stale=True)
            # The originally authorized credential can still inspect its clearly
            # stale, endpoint-bound copy.
            stale = alpha.request("status", {"project": "alpha"}, allow_stale=True)
            self.assertEqual(stale["freshness"]["state"], "stale_disconnected")

        def test_authentication_refusal_invalidates_entire_credential_endpoint_cache(self):
            cache = self.root / "expiry-cache.json"
            client = self.client(cache=cache)
            self.assertTrue(client.request("status", {"project": "alpha"})["ok"])
            task_params = {"project": "alpha", "limit": 1, "page_token": 0}
            self.assertTrue(client.request("tasks", task_params)["ok"])
            self.stop_service()
            self.grants[0]["expires_at"] = "2000-01-01T00:00:00Z"
            self.grants_path.write_text(json.dumps(self.grants), encoding="utf-8")
            self.start_service()
            refused = client.request("status", {"project": "alpha"})
            self.assertFalse(refused["ok"])
            self.assertEqual(refused["error"]["code"], "authentication_refused")
            self.stop_service()
            with self.assertRaises(AccessRefused):
                client.request("tasks", task_params, allow_stale=True)

        def test_permission_refusal_invalidates_all_cached_operations_for_project(self):
            cache = self.root / "permission-cache.json"
            client = self.client(cache=cache)
            status_params = {"project": "alpha"}
            task_params = {"project": "alpha", "limit": 1, "page_token": 0}
            self.assertTrue(client.request("status", status_params)["ok"])
            self.assertTrue(client.request("tasks", task_params)["ok"])
            self.stop_service()
            self.grants[0]["projects"] = ["beta"]
            self.grants_path.write_text(json.dumps(self.grants), encoding="utf-8")
            self.start_service()
            refused = client.request("status", status_params)
            self.assertFalse(refused["ok"])
            self.assertEqual(refused["error"]["code"], "permission_denied")
            self.stop_service()
            with self.assertRaises(AccessRefused):
                client.request("tasks", task_params, allow_stale=True)

        def test_event_replay_gap_demands_snapshot_refresh(self):
            gap = self.client().request("events", {"project": "alpha", "after_cursor": 0, "limit": 2})
            self.assertFalse(gap["ok"])
            self.assertEqual(gap["error"]["code"], "replay_gap")
            self.assertTrue(gap["error"]["snapshot_required"])
            page = self.client().request("events", {"project": "alpha", "after_cursor": 2, "limit": 2})
            self.assertTrue(page["ok"])
            self.assertEqual([item["cursor"] for item in page["data"]["items"]], [3, 4])
            self.assertEqual(page["data"]["next_cursor"], 4)
            future = self.client().request("events", {"project": "alpha", "after_cursor": 99, "limit": 2})
            self.assertFalse(future["ok"])
            self.assertEqual(future["error"]["code"], "replay_gap")
            self.fixture["projects"]["alpha"]["events"] = []
            self.fixture["projects"]["alpha"]["event_history_start"] = 6
            self.write_fixture()
            empty_retention = self.client().request(
                "events", {"project": "alpha", "after_cursor": 0, "limit": 2},
            )
            self.assertFalse(empty_retention["ok"])
            self.assertTrue(empty_retention["error"]["snapshot_required"])

        def test_malformed_and_oversize_requests_are_refused(self):
            malformed = self.raw_request(b"{not-json}\n")
            self.assertFalse(malformed["ok"])
            self.assertEqual(malformed["error"]["code"], "malformed_request")
            oversized = self.raw_request(b"x" * (MAX_REQUEST_BYTES + 1) + b"\n")
            self.assertFalse(oversized["ok"])
            self.assertEqual(oversized["error"]["code"], "request_too_large")
            too_large_page = self.client().request("tasks", {"project": "alpha", "limit": 3, "page_token": 0})
            self.assertFalse(too_large_page["ok"])
            self.assertEqual(too_large_page["error"]["code"], "malformed_request")
            duplicate = self.raw_request(
                b'{"protocol_version":1,"op":"status","op":"task","request_id":"d","params":{"project":"alpha"}}\n'
            )
            self.assertFalse(duplicate["ok"])
            self.assertEqual(duplicate["error"]["code"], "malformed_request")

        def test_artifacts_are_bounded_and_reject_escape_symlink_and_cross_project(self):
            good = self.client().request("artifact", {
                "project": "alpha", "handle": "alpha-report", "offset": 0, "limit": 7,
            })
            self.assertTrue(good["ok"])
            self.assertEqual(base64.b64decode(good["data"]["content"]), b"bounded")
            for handle, code in (
                ("escape", "artifact_refused"), ("symlink", "artifact_refused"),
                ("large", "artifact_refused"), ("misbound", "permission_denied"),
                ("beta-secret", "not_found"),
            ):
                with self.subTest(handle=handle):
                    response = self.client().request("artifact", {
                        "project": "alpha", "handle": handle, "offset": 0, "limit": 8,
                    })
                    self.assertFalse(response["ok"])
                    self.assertEqual(response["error"]["code"], code)

        def test_artifact_manifest_digest_and_descriptor_open_defeat_replacement(self):
            record = self.fixture["projects"]["alpha"]["artifacts"][0]
            record["sha256"] = "0" * 64
            self.write_fixture()
            wrong_digest = self.client().request("artifact", {
                "project": "alpha", "handle": "alpha-report", "offset": 0, "limit": 7,
            })
            self.assertFalse(wrong_digest["ok"])
            self.assertEqual(wrong_digest["error"]["code"], "artifact_refused")

            race_root = self.root / "race-artifacts"
            race_root.mkdir()
            target = race_root / "target.txt"
            target.write_bytes(b"inside")
            outside = self.root / "race-outside.txt"
            outside.write_bytes(b"outside")
            race_fixture = self.root / "race-fixture.json"
            value = {
                "canonical_revision": 1,
                "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "last_event_cursor": 0,
                "projects": {"alpha": {
                    "status": {}, "tasks": [], "events": [], "event_history_start": 1,
                    "artifacts": [{"handle": "race", "project": "alpha", "path": "target.txt",
                                   "sha256": hashlib.sha256(b"inside").hexdigest()}],
                }},
            }
            race_fixture.write_text(json.dumps(value), encoding="utf-8")
            adapter = FixtureCanonicalAdapter(race_fixture, {"alpha": race_root})
            real_open = os.open
            replaced = False

            def replace_then_open(path, flags, *args, **kwargs):
                nonlocal replaced
                if path == "target.txt" and not replaced:
                    replaced = True
                    target.unlink()
                    target.symlink_to(outside)
                return real_open(path, flags, *args, **kwargs)

            try:
                with mock.patch("tools.construction_swarm.p2_access.os.open", side_effect=replace_then_open):
                    with self.assertRaises(AccessRefused) as refused:
                        adapter.read("artifact", "alpha", {"handle": "race", "offset": 0, "limit": 7})
                self.assertEqual(refused.exception.code, "artifact_refused")

                target.unlink()
                target.write_bytes(b"inside")
                real_compare = hmac.compare_digest

                def change_after_compare(actual, expected):
                    matched = real_compare(actual, expected)
                    if matched:
                        target.write_bytes(b"changed-after-hash")
                    return matched

                with mock.patch("tools.construction_swarm.p2_access.hmac.compare_digest",
                                side_effect=change_after_compare):
                    stable = adapter.read(
                        "artifact", "alpha", {"handle": "race", "offset": 0, "limit": 7},
                    )
                returned = base64.b64decode(stable["data"]["content"])
                self.assertEqual(returned, b"inside")
                self.assertEqual(hashlib.sha256(returned).hexdigest(), stable["data"]["sha256"])
            finally:
                adapter.close()

        def test_fifo_artifact_is_nonblocking_and_does_not_consume_read_slots(self):
            pipe = self.alpha_artifacts / "pipe"
            os.mkfifo(pipe)
            self.fixture["projects"]["alpha"]["artifacts"].append({
                "handle": "pipe", "project": "alpha", "path": "pipe", "sha256": "0" * 64,
            })
            self.write_fixture()
            outcomes = []

            def read_pipe():
                outcomes.append(self.client().request("artifact", {
                    "project": "alpha", "handle": "pipe", "offset": 0, "limit": 8,
                }))

            workers = [threading.Thread(target=read_pipe) for _ in range(2)]
            began = time.monotonic()
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(2)
            self.assertTrue(all(not worker.is_alive() for worker in workers))
            self.assertEqual(len(outcomes), 2)
            self.assertTrue(all(item["error"]["code"] == "artifact_refused" for item in outcomes))
            task = self.client().request("task", {"project": "alpha", "task_id": "a-1"})
            self.assertTrue(task["ok"])
            self.assertLess(time.monotonic() - began, 1.0)

        def test_disappeared_fixture_ledger_returns_structured_unavailable_response(self):
            missing = self.fixture_path.with_suffix(".missing")
            self.fixture_path.rename(missing)
            try:
                response = self.client().request("status", {"project": "alpha"})
            finally:
                missing.rename(self.fixture_path)
            self.common(response)
            self.assertFalse(response["ok"])
            self.assertEqual(response["error"]["code"], "canonical_unavailable")
            self.assertIn("canonical_revision", response["unavailable_fields"])
            self.assertIn("last_event_cursor", response["unavailable_fields"])

        def test_mcp_disconnect_preserves_service_and_reconnect_sees_current_cursor(self):
            first = self.mcp([
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
                    "name": "construction_status", "arguments": {"project": "alpha"},
                }},
            ])
            first_status = json.loads(first[1]["result"]["content"][0]["text"])
            self.assertEqual(first_status["last_event_cursor"], 5)
            self.assertIsNone(self.process.poll(), "stdio bridge exit killed independently owned service")
            direct = self.cli("status", "--project", "alpha")[1]
            self.assertTrue(direct["ok"])
            self.fixture["canonical_revision"] = 8
            self.fixture["last_event_cursor"] = 6
            self.fixture["projects"]["alpha"]["events"].append(
                {"cursor": 6, "kind": "verified", "task_id": "a-2"},
            )
            self.write_fixture()
            second = self.mcp([
                {"jsonrpc": "2.0", "id": 3, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
                    "name": "construction_status", "arguments": {"project": "alpha"},
                }},
            ])
            second_status = json.loads(second[1]["result"]["content"][0]["text"])
            self.assertEqual(second_status["source_commit"], SOURCE_A)
            self.assertEqual(second_status["canonical_revision"], 8)
            self.assertEqual(second_status["last_event_cursor"], 6)

        def test_client_reconnect_recovers_new_service_source_instance_and_cursor(self):
            client = self.client(cache=self.root / "reconnect-cache.json")
            first = client.request("status", {"project": "alpha"})
            old_instance = first["service_instance"]
            self.stop_service()
            self.fixture["canonical_revision"] = 9
            self.fixture["last_event_cursor"] = 6
            self.write_fixture()
            self.start_service(source=SOURCE_B, instance="replacement-instance")
            second = client.request("status", {"project": "alpha"})
            self.assertTrue(second["ok"])
            self.assertNotEqual(second["service_instance"], old_instance)
            self.assertEqual(second["service_instance"], "replacement-instance")
            self.assertEqual(second["source_commit"], SOURCE_B)
            self.assertEqual(second["last_event_cursor"], 6)
            self.assertFalse(second["freshness"]["state"] == "stale_disconnected")

        def test_status_stays_responsive_while_bounded_read_slots_are_saturated(self):
            self.fixture["test_delays"] = {"tasks": 0.8}
            self.write_fixture()
            outcomes = []
            start = threading.Barrier(3)

            def slow_read():
                start.wait()
                outcomes.append(self.client().request(
                    "tasks", {"project": "alpha", "limit": 1, "page_token": 0},
                ))

            workers = [threading.Thread(target=slow_read) for _ in range(2)]
            for worker in workers:
                worker.start()
            start.wait()
            time.sleep(0.2)
            began = time.monotonic()
            status = self.client().request("status", {"project": "alpha"})
            elapsed = time.monotonic() - began
            for worker in workers:
                worker.join(3)
            self.assertTrue(all(not worker.is_alive() for worker in workers))
            self.assertEqual(len(outcomes), 2)
            self.assertTrue(all(item["ok"] for item in outcomes))
            self.assertTrue(status["ok"])
            self.assertLess(elapsed, 0.5, f"reserved status path took {elapsed:.3f}s")

        def test_idle_handshakes_have_bounded_threads_and_lifetimes(self):
            channels = []
            try:
                for _ in range(32):
                    channel = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    channel.settimeout(0.2)
                    try:
                        channel.connect(str(self.socket_path))
                        channels.append(channel)
                    except OSError:
                        channel.close()
                time.sleep(0.2)
                status_text = Path(f"/proc/{self.process.pid}/status").read_text(encoding="utf-8")
                thread_line = next(line for line in status_text.splitlines() if line.startswith("Threads:"))
                self.assertLessEqual(int(thread_line.split()[1]), 5, thread_line)
                time.sleep(1.3)
                status_text = Path(f"/proc/{self.process.pid}/status").read_text(encoding="utf-8")
                thread_line = next(line for line in status_text.splitlines() if line.startswith("Threads:"))
                self.assertLessEqual(int(thread_line.split()[1]), 2, thread_line)
            finally:
                for channel in channels:
                    channel.close()

        def test_partial_frame_trickle_cannot_extend_total_handshake_deadline(self):
            channels = []
            try:
                for _ in range(4):
                    channel = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    channel.settimeout(0.5)
                    channel.connect(str(self.socket_path))
                    channels.append(channel)
                deadline = time.monotonic() + 1.5
                while time.monotonic() < deadline:
                    for channel in channels:
                        try:
                            channel.sendall(b" ")
                        except OSError:
                            pass
                    time.sleep(0.2)
                time.sleep(0.2)
                status = self.client().request("status", {"project": "alpha"})
                self.assertTrue(status["ok"])
                status_text = Path(f"/proc/{self.process.pid}/status").read_text(encoding="utf-8")
                thread_line = next(line for line in status_text.splitlines() if line.startswith("Threads:"))
                self.assertLessEqual(int(thread_line.split()[1]), 2, thread_line)
            finally:
                for channel in channels:
                    channel.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)

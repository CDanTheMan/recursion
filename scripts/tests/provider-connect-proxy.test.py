#!/usr/bin/env python3
"""Hermetic contract tests for the provider-only CONNECT capability."""

from __future__ import annotations

import importlib.util
import asyncio
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PROXY = ROOT / "scripts" / "provider-connect-proxy.py"


def load_proxy():
    spec = importlib.util.spec_from_file_location("provider_connect_proxy", PROXY)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load provider proxy")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ConnectContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proxy = load_proxy()
        cls.allowed = {("api.anthropic.com", 443)}

    def parse(self, request: bytes):
        return self.proxy.parse_connect_request(request, self.allowed)

    def test_exact_provider_authority_is_accepted_case_insensitively(self):
        self.assertEqual(
            self.parse(b"CONNECT API.ANTHROPIC.COM:443 HTTP/1.1\r\nHost: api.anthropic.com:443\r\n\r\n"),
            ("api.anthropic.com", 443),
        )

    def test_other_hosts_ports_and_non_connect_methods_are_denied(self):
        denied = (
            b"CONNECT example.com:443 HTTP/1.1\r\n\r\n",
            b"CONNECT api.anthropic.com:80 HTTP/1.1\r\n\r\n",
            b"GET https://api.anthropic.com/ HTTP/1.1\r\n\r\n",
        )
        for request in denied:
            with self.subTest(request=request):
                with self.assertRaises(self.proxy.ConnectDenied):
                    self.parse(request)

    def test_ambiguous_or_smuggled_requests_are_malformed(self):
        malformed = (
            b"CONNECT api.anthropic.com:443 HTTP/1.0\r\n\r\n",
            b"CONNECT api.anthropic.com:443 HTTP/1.1\n\n",
            b"CONNECT api.anthropic.com:443 HTTP/1.1\r\n folded\r\n\r\n",
            b"CONNECT api.anthropic.com:443 HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n",
            b"CONNECT api.anthropic.com:443 HTTP/1.1\r\nContent-Length: 1\r\n\r\nX",
            b"CONNECT api.anthropic.com:443@evil.test:443 HTTP/1.1\r\n\r\n",
            b"CONNECT 1.2.3.4:443 HTTP/1.1\r\n\r\n",
        )
        for request in malformed:
            with self.subTest(request=request):
                with self.assertRaises(self.proxy.MalformedConnect):
                    self.parse(request)

    def test_allowlist_parser_requires_canonical_dns_name_and_port(self):
        self.assertEqual(
            self.proxy.parse_allowlist(["api.anthropic.com:443"]),
            {("api.anthropic.com", 443)},
        )
        for value in ("https://api.anthropic.com:443", "*.anthropic.com:443", "1.2.3.4:443", "api.anthropic.com"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.proxy.parse_allowlist([value])

    def test_signed_capability_binds_transport_to_one_profile(self):
        key = b"k" * 32
        anthropic = {("api.anthropic.com", 443)}
        cursor = {("api.cursor.com", 443)}
        token = self.proxy.issue_capability("anthropic", "assignment-a", key)
        request = (
            b"CONNECT api.anthropic.com:443 HTTP/1.1\r\n"
            + f"Proxy-Authorization: Bearer {token}\r\n\r\n".encode("ascii")
        )
        self.assertEqual(self.proxy.parse_connect_request(
            request, capability_key=key,
            profile_authorities={"anthropic": anthropic, "cursor": cursor},
        ), ("api.anthropic.com", 443))
        cross_provider = request.replace(b"api.anthropic.com", b"api.cursor.com")
        with self.assertRaises(self.proxy.ConnectDenied):
            self.proxy.parse_connect_request(
                cross_provider, capability_key=key,
                profile_authorities={"anthropic": anthropic, "cursor": cursor},
            )
        forged = token[:-1] + ("A" if token[-1] != "A" else "B")
        with self.assertRaises(self.proxy.ConnectDenied):
            self.proxy.parse_connect_request(
                request.replace(token.encode("ascii"), forged.encode("ascii")),
                capability_key=key, profile_authorities={"anthropic": anthropic},
            )

    def test_signed_capability_must_match_active_assignment(self):
        key = b"k" * 32
        token = self.proxy.issue_capability("anthropic", "assignment-a", key)
        request = (
            b"CONNECT api.anthropic.com:443 HTTP/1.1\r\n"
            + f"Proxy-Authorization: Bearer {token}\r\n\r\n".encode("ascii")
        )
        with self.assertRaises(self.proxy.ConnectDenied):
            self.proxy.parse_connect_request(
                request, capability_key=key,
                profile_authorities={"anthropic": self.allowed},
                active_assignment="assignment-b",
            )
        self.assertEqual(self.proxy.parse_connect_request(
            request, capability_key=key,
            profile_authorities={"anthropic": self.allowed},
            active_assignment="assignment-a",
        ), ("api.anthropic.com", 443))

    def test_basic_proxy_identity_cannot_be_swapped_between_assignments(self):
        import base64
        key = b"k" * 32
        token = self.proxy.issue_capability("anthropic", "assignment-a", key)
        basic = base64.b64encode(f"assignment-b:{token}".encode("ascii")).decode("ascii")
        request = (
            b"CONNECT api.anthropic.com:443 HTTP/1.1\r\n"
            + f"Proxy-Authorization: Basic {basic}\r\n\r\n".encode("ascii")
        )
        with self.assertRaises(self.proxy.ConnectDenied):
            self.proxy.parse_connect_request(
                request, capability_key=key,
                profile_authorities={"anthropic": self.allowed},
            )

    def test_signed_capability_is_required_when_profile_authorization_is_enabled(self):
        with self.assertRaises(self.proxy.ConnectDenied):
            self.proxy.parse_connect_request(
                b"CONNECT api.anthropic.com:443 HTTP/1.1\r\n\r\n",
                capability_key=b"k" * 32,
                profile_authorities={"anthropic": {("api.anthropic.com", 443)}},
            )

    def test_dns_rejects_private_and_rebinding_answers_before_connect(self):
        for address in ("127.0.0.1", "10.0.0.1", "169.254.1.1", "224.0.0.1", "::1"):
            with self.subTest(address=address):
                self.assertTrue(self.proxy.forbidden_destination(address))
        original = self.proxy.socket.getaddrinfo
        try:
            self.proxy.socket.getaddrinfo = lambda *args, **kwargs: [
                (self.proxy.socket.AF_INET, self.proxy.socket.SOCK_STREAM,
                 self.proxy.socket.IPPROTO_TCP, "", ("203.0.113.10", 443)),
                (self.proxy.socket.AF_INET, self.proxy.socket.SOCK_STREAM,
                 self.proxy.socket.IPPROTO_TCP, "", ("127.0.0.1", 443)),
            ]
            with self.assertRaises(self.proxy.ConnectDenied):
                self.proxy.resolve_approved_addresses("provider.example", 443)
        finally:
            self.proxy.socket.getaddrinfo = original

    def test_connected_peer_must_match_the_approved_dns_answer(self):
        async def exercise():
            async def sink(reader, writer):
                writer.close()
                await writer.wait_closed()

            server = await asyncio.start_server(sink, "127.0.0.1", 0)
            try:
                port = server.sockets[0].getsockname()[1]
                destinations = [(
                    self.proxy.socket.AF_INET, self.proxy.socket.SOCK_STREAM,
                    self.proxy.socket.IPPROTO_TCP, ("127.0.0.1", port), "203.0.113.10",
                )]
                with self.assertRaises(self.proxy.ConnectDenied):
                    await self.proxy.open_approved_connection(destinations, port)
            finally:
                server.close()
                await server.wait_closed()

        asyncio.run(exercise())


def build_client_hello(sni: str) -> bytes:
    """Assemble one TLS handshake record carrying a single ClientHello with the given SNI."""
    host = sni.encode("ascii")
    server_name = b"\x00" + len(host).to_bytes(2, "big") + host
    ext = (
        (0).to_bytes(2, "big")
        + (len(server_name) + 2).to_bytes(2, "big")
        + len(server_name).to_bytes(2, "big")
        + server_name
    )
    body = (0x0303).to_bytes(2, "big") + b"\x00" * 32  # legacy version + random
    body += b"\x00"  # empty session id
    body += (2).to_bytes(2, "big") + b"\x13\x01"  # one cipher suite
    body += b"\x01\x00"  # one compression method
    body += len(ext).to_bytes(2, "big") + ext
    handshake = b"\x01" + len(body).to_bytes(3, "big") + body
    return b"\x16\x03\x01" + len(handshake).to_bytes(2, "big") + handshake


def record(payload: bytes) -> bytes:
    return b"\x16\x03\x01" + len(payload).to_bytes(2, "big") + payload


class ClientHelloContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proxy = load_proxy()

    def test_pinned_sni_is_extracted_case_insensitively(self):
        hello = build_client_hello("API.ANTHROPIC.COM")
        sni, consumed = self.proxy.parse_client_hello(hello)
        self.assertEqual(sni, "api.anthropic.com")
        self.assertEqual(consumed, len(hello))

    def test_fragmented_client_hello_is_reassembled(self):
        hello = build_client_hello("api.anthropic.com")
        handshake = hello[5:]
        half = len(handshake) // 2
        fragmented = record(handshake[:half]) + record(handshake[half:])
        sni, consumed = self.proxy.parse_client_hello(fragmented)
        self.assertEqual(sni, "api.anthropic.com")
        self.assertEqual(consumed, len(fragmented))

    def test_wrong_sni_is_visible_for_fail_closed_comparison(self):
        hello = build_client_hello("evil.example.com")
        self.assertEqual(self.proxy.parse_client_hello(hello)[0], "evil.example.com")

    def test_non_tls_non_client_hello_and_empty_record_are_malformed(self):
        for data in (
            b"GET / HTTP/1.1\r\n\r\n",  # not TLS
            record(b"\x02\x00\x00\x00"),  # ServerHello, not ClientHello
            b"\x16\x03\x01\x00\x00",  # zero-length handshake record
        ):
            with self.subTest(data=data[:12]):
                with self.assertRaises(self.proxy.MalformedClientHello):
                    self.proxy.parse_client_hello(data)

    def test_incomplete_client_hello_returns_none_not_malformed(self):
        hello = build_client_hello("api.anthropic.com")
        self.assertIsNone(self.proxy.parse_client_hello(hello[:4]))

    def test_client_hello_without_server_name_is_malformed(self):
        host = b""
        server_name = b"\x00" + len(host).to_bytes(2, "big")
        ext = (0).to_bytes(2, "big") + (len(server_name) + 2).to_bytes(2, "big") \
            + len(server_name).to_bytes(2, "big") + server_name
        body = (0x0303).to_bytes(2, "big") + b"\x00" * 32 + b"\x00" \
            + (2).to_bytes(2, "big") + b"\x13\x01" + b"\x01\x00" \
            + len(ext).to_bytes(2, "big") + ext
        handshake = b"\x01" + len(body).to_bytes(3, "big") + body
        with self.assertRaises(self.proxy.MalformedClientHello):
            self.proxy.parse_client_hello(record(handshake))


class DeploymentContractTest(unittest.TestCase):
    def test_v1_production_unit_retains_legacy_capability_boundary(self):
        unit = (ROOT / "deploy/systemd/recursion-provider-proxy.service").read_text()
        self.assertIn("--allow api.anthropic.com:443", unit)
        self.assertNotIn("--resolve", unit)
        self.assertIn("NoNewPrivileges=yes", unit)
        self.assertIn("CapabilityBoundingSet=CAP_SYS_ADMIN", unit)
        self.assertIn("LimitNOFILE=256", unit)
        self.assertIn("MemoryMax=256M", unit)

    def test_phase4_unit_uses_the_deployed_explicit_profile_directory(self):
        unit = (ROOT / "deploy/systemd/recursion-provider-proxy-phase4.service.example").read_text()
        self.assertIn("--profile-dir /etc/recursion/providers", unit)
        self.assertIn("--enabled-profiles", unit)

    def test_profile_selection_refuses_all_disabled_and_selects_only_enabled(self):
        import tempfile
        import json
        from provider_contract import enabled_allowlist, enabled_profile_names, ProviderProfileError
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            for name, authorities in {
                "anthropic": ["api.anthropic.com:443"],
                "cursor": ["api.cursor.com:443"],
                "google-gemini": ["generativelanguage.googleapis.com:443"],
                "openrouter-via-opencode": ["openrouter.ai:443"],
            }.items():
                value = {"schema_version": 1, "id": name, "provider": name, "enabled": name == "cursor",
                         "namespace": "recursion-provider-only",
                         "proxy": {"type": "connect-proxy", "host": "127.0.0.1", "port": 18080,
                                   "env": ["HTTP_PROXY", "HTTPS_PROXY"]}, "authorities": authorities}
                (directory / f"{name}.json").write_text(json.dumps(value), encoding="utf-8")
            self.assertEqual(enabled_profile_names(directory), ["cursor"])
            self.assertEqual(enabled_allowlist(directory), {("api.cursor.com", 443)})
            (directory / "cursor.json").write_text(
                (directory / "cursor.json").read_text().replace('"enabled": true', '"enabled": false'),
                encoding="utf-8")
            with self.assertRaises(ProviderProfileError):
                enabled_profile_names(directory)

    def test_namespace_unit_and_worker_share_the_fixed_capability(self):
        network = (ROOT / "deploy/systemd/recursion-provider-network.service").read_text()
        worker = (ROOT / "scripts/worker-sandbox.sh").read_text()
        self.assertIn("provider-network.sh create", network)
        self.assertIn("provider-network.sh delete", network)
        self.assertIn("NetworkNamespacePath=$PROVIDER_NETNS", worker)
        self.assertIn('provider-network.sh" check', worker)

    def test_claude_uses_only_local_proxy_and_disables_nonessential_traffic(self):
        worker = (ROOT / "scripts/worker-sandbox.sh").read_text()
        self.assertIn("HTTPS_PROXY=http://127.0.0.1:18080", worker)
        self.assertIn("HTTP_PROXY=http://127.0.0.1:18080", worker)
        self.assertIn("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1", worker)

    def test_worker_sandbox_masks_host_run_sockets_for_gate_and_model_arms(self):
        worker = (ROOT / "scripts/worker-sandbox.sh").read_text()
        inaccessible_lines = [line for line in worker.splitlines() if "InaccessiblePaths=" in line]
        self.assertEqual(len(inaccessible_lines), 2)
        for line in inaccessible_lines:
            self.assertIn("/run", line)
            self.assertIn("/var/run", line)
        # The shared base line covers the gate arm; the model-arm branch repeats the mask.
        self.assertIn("InaccessiblePaths=", inaccessible_lines[0])
        self.assertIn("/opt", inaccessible_lines[1])
        # The provider egress is the loopback CONNECT proxy over TCP, not a host socket.
        self.assertIn("HTTPS_PROXY=http://127.0.0.1:18080", worker)

    def test_assignment_capability_stays_ephemeral_outside_durable_plans(self):
        worker = (ROOT / "scripts/worker-sandbox.sh").read_text()
        work = (ROOT / "scripts/work.sh").read_text()
        self.assertIn("RECURSION_ASSIGNMENT_PROXY_TOKEN", worker)
        self.assertIn("assignment-token.py", work)
        self.assertIn("token-free plan", work)
        self.assertNotIn('print("TOKEN=" + token)', worker)


if __name__ == "__main__":
    unittest.main(verbosity=2)

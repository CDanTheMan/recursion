#!/usr/bin/env python3
"""Hermetic contract tests for the provider-only CONNECT capability."""

from __future__ import annotations

import importlib.util
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


class DeploymentContractTest(unittest.TestCase):
    def test_production_unit_has_one_anthropic_authority_and_no_test_override(self):
        unit = (ROOT / "deploy/systemd/recursion-provider-proxy.service").read_text()
        self.assertIn("--allow api.anthropic.com:443", unit)
        self.assertNotIn("--resolve", unit)
        self.assertIn("NoNewPrivileges=yes", unit)
        self.assertIn("CapabilityBoundingSet=CAP_SYS_ADMIN", unit)
        self.assertIn("LimitNOFILE=256", unit)
        self.assertIn("MemoryMax=256M", unit)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)

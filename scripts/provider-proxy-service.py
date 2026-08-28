#!/usr/bin/env python3
"""Exec the provider CONNECT proxy from the root-owned egress profile."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    profile = os.environ.get("RECURSION_PROVIDER_PROFILE", "")
    provider = os.environ.get("RECURSION_PROVIDER_ID", "")
    endpoints = os.environ.get("RECURSION_PROVIDER_ENDPOINTS", "").split()
    resolver = [sys.executable, str(ROOT / "provider-egress.py"), profile, "--provider", provider]
    for endpoint in endpoints:
        resolver += ["--endpoint", endpoint]
    try:
        item = json.loads(subprocess.check_output(resolver, text=True))
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"provider-proxy-service: invalid provider profile: {exc}", file=sys.stderr)
        return 96
    allowed = [f"{endpoint}:443" for endpoint in item["endpoints"]]
    if not allowed:
        print("provider-proxy-service: profile has no permitted endpoint", file=sys.stderr)
        return 96
    command = [str(ROOT / "provider-connect-proxy.py"), "serve",
               "--namespace", f"/run/netns/{item['namespace']}",
               "--listen-port", str(item["proxy_port"]), "--drop-user", "recursion-provider-proxy",
               "--concurrency", "16"]
    for authority in allowed:
        command += ["--allow", authority]
    os.execv(sys.executable, [sys.executable] + command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

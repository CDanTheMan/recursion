#!/usr/bin/env python3
"""Exec the provider CONNECT proxy from the root-owned egress profile."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMMIT_RE = re.compile(r"[0-9a-f]{40,64}\Z")


def controller_provenance() -> tuple[str, str]:
    configured_root = os.environ.get("RECURSION_ROOT", "").strip() or str(ROOT.parent)
    requested_root = os.environ.get("RECURSION_CONTROLLER_ROOT", "").strip()
    requested_commit = os.environ.get("RECURSION_CONTROLLER_COMMIT", "").strip()
    if (requested_root or requested_commit) and not (requested_root and requested_commit):
        raise ValueError("incomplete controller policy provenance")
    controller_root = requested_root or configured_root
    controller_commit = requested_commit
    if not controller_commit:
        try:
            observed = subprocess.run(
                ["git", "-C", controller_root, "rev-parse", "--verify", "HEAD"],
                capture_output=True, text=True, check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ValueError("controller policy provenance is unavailable") from exc
        if observed.returncode != 0:
            raise ValueError("controller policy provenance is unavailable")
        controller_commit = observed.stdout.strip()
    if not COMMIT_RE.fullmatch(controller_commit):
        raise ValueError("controller policy provenance is invalid")
    return controller_root, controller_commit


def main() -> int:
    profile = os.environ.get("RECURSION_PROVIDER_PROFILE", "")
    provider = os.environ.get("RECURSION_PROVIDER_ID", "")
    endpoints = os.environ.get("RECURSION_PROVIDER_ENDPOINTS", "").split()
    try:
        controller_root, controller_commit = controller_provenance()
        resolver = [sys.executable, str(ROOT / "provider-egress.py"), profile,
                    "--provider", provider, "--controller-root", controller_root,
                    "--controller-commit", controller_commit]
        for endpoint in endpoints:
            resolver += ["--endpoint", endpoint]
        resolved = subprocess.run(resolver, capture_output=True, text=True, check=False)
        if resolved.returncode != 0:
            raise ValueError("provider profile resolution failed")
        item = json.loads(resolved.stdout)
        if not isinstance(item, dict) or not isinstance(item.get("endpoints"), list):
            raise ValueError("provider profile is malformed")
    except (OSError, subprocess.SubprocessError, ValueError, TypeError,
            json.JSONDecodeError, UnicodeDecodeError, KeyError):
        print("provider-proxy-service: invalid provider profile", file=sys.stderr)
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

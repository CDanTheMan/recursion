#!/usr/bin/env python3
"""Validate provider profiles and emit only the proxy environment boundary.

The command is intentionally small and side-effect free. ``inject`` prints non-secret
loopback proxy variables for the sandbox to consume; it never opens a socket, edits a
namespace, or reads a credential value.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from provider_contract import (
    ProviderProfileError,
    enabled_allowlist,
    profile_directory,
    profile_for_provider,
    proxy_environment,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="provider-egress")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("provider")
    inject = sub.add_parser("inject")
    inject.add_argument("provider")
    inject.add_argument("--endpoint", action="append", required=True)
    allowlist = sub.add_parser("allowlist")
    allowlist.add_argument("--provider", action="append", dest="providers")
    args = parser.parse_args(argv)
    directory = profile_directory(Path(__file__).resolve().parent)
    try:
        if args.command == "validate":
            profile = profile_for_provider(args.provider, directory)
            print(json.dumps({"id": profile["id"], "enabled": profile["enabled"]}, sort_keys=True))
        elif args.command == "inject":
            profile = profile_for_provider(args.provider, directory)
            for key, value in sorted(proxy_environment(profile, args.endpoint).items()):
                print(f"{key}={value}")
        else:
            for host, port in sorted(enabled_allowlist(directory, args.providers)):
                print(f"{host}:{port}")
        return 0
    except (OSError, ValueError, ProviderProfileError) as exc:
        print(f"provider-egress: {exc}", file=sys.stderr)
        return 96 if args.command == "inject" else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Mint one short-lived-in-practice provider capability for a controller assignment.

The key is read only from the human-owned credential path and the bearer token is written to
stdout for an in-memory caller.  Callers must not persist this output (plans and evidence are
intentionally token-free).
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import pathlib
import stat
import sys


def load_issue():
    path = pathlib.Path(__file__).with_name("provider-connect-proxy.py")
    spec = importlib.util.spec_from_file_location("recursion_provider_proxy", path)
    if spec is None or spec.loader is None:
        raise ValueError("provider capability issuer is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.issue_capability


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="assignment-token")
    parser.add_argument("profile")
    parser.add_argument("assignment")
    parser.add_argument("--key-file", type=pathlib.Path,
                        default=pathlib.Path("/etc/recursion/provider-capability.key"))
    args = parser.parse_args(argv)
    try:
        path = args.key_file
        if path.is_symlink() or not path.is_file():
            raise ValueError("provider capability key is unavailable")
        info = path.stat()
        if stat.S_IMODE(info.st_mode) & 0o077:
            raise ValueError("provider capability key ownership/mode is unsafe")
        if hasattr(os, "geteuid") and os.geteuid() == 0 and info.st_uid != 0:
            raise ValueError("provider capability key ownership/mode is unsafe")
        secret = path.read_bytes()
        token = load_issue()(args.profile, args.assignment, secret)
        sys.stdout.write(token + "\n")
        return 0
    except (OSError, ValueError) as exc:
        print(f"assignment-token: {exc}", file=sys.stderr)
        return 96


if __name__ == "__main__":
    raise SystemExit(main())

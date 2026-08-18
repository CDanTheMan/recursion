#!/usr/bin/env python3
"""Resolve a reviewed role alias from human-owned environment configuration."""

from __future__ import annotations

import argparse
import os
import sys


ALIASES = {
    "sonnet-routine": ("RECURSION_MODEL_ALIAS_SONNET_ROUTINE", {"implementer"}),
    "opus-complex": ("RECURSION_MODEL_ALIAS_OPUS_COMPLEX", {"implementer", "verifier"}),
    "opus-review": ("RECURSION_MODEL_ALIAS_OPUS_REVIEW", {"verifier"}),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("alias")
    parser.add_argument("role", choices=("implementer", "verifier"))
    args = parser.parse_args()
    spec = ALIASES.get(args.alias)
    if spec is None:
        print(f"model-alias: unknown alias {args.alias!r}", file=sys.stderr)
        return 2
    env_name, roles = spec
    if args.role not in roles:
        print(f"model-alias: {args.alias} is not approved for {args.role}", file=sys.stderr)
        return 2
    value = os.environ.get(env_name, "").strip()
    if not value:
        print(f"model-alias: human-owned mapping {env_name} is absent", file=sys.stderr)
        return 3
    if any(ord(ch) < 33 or ch in "'\"`$;&|<>" for ch in value):
        print(f"model-alias: {env_name} contains unsafe characters", file=sys.stderr)
        return 2
    print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

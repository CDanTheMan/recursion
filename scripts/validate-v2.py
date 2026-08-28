#!/usr/bin/env python3
"""Validate one v2 record or registry file; never writes or enables anything."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from v2_contracts import ContractError, load_registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="validate-v2")
    parser.add_argument("path", type=Path)
    parser.add_argument("--kind")
    args = parser.parse_args(argv)
    try:
        records = load_registry(args.path, args.kind)
    except ContractError as exc:
        print(f"validate-v2: {exc}", file=sys.stderr)
        return 2
    print(f"valid: {len(records)} {args.kind or records[0]['kind']} record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

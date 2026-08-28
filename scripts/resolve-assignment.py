#!/usr/bin/env python3
"""Pure, dry-run assignment resolver for Recursion v2.

No filesystem writes, process execution, network access, credential lookup, or feature
flag mutation occurs here.  The output is suitable for review and later persistence by
the control plane.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from v2_contracts import ContractError, load_config, resolve_assignment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="resolve-assignment")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--config-dir", required=True, type=Path)
    parser.add_argument("--policy")
    args = parser.parse_args(argv)
    try:
        task = json.loads(args.task.read_text(encoding="utf-8"))
        result = resolve_assignment(task, load_config(args.config_dir), policy=args.policy)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ContractError) as exc:
        print(json.dumps({"status": "refused", "error": str(exc), "error_code": getattr(exc, "code", "invalid-input")}, sort_keys=True))
        return 2
    print(json.dumps({"status": result.status, "assignment": result.assignment, "trace": list(result.trace)}, indent=2, sort_keys=True))
    return 0 if result.status == "assigned" else 3


if __name__ == "__main__":
    raise SystemExit(main())

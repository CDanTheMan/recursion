#!/usr/bin/env python3
"""Validate an independent verifier verdict against its exact implementation commit."""

from __future__ import annotations

import argparse
import json
import re
import sys


OID = re.compile(r"^[0-9a-f]{40,64}$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("verdict")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--implementer-run", required=True)
    args = parser.parse_args()
    try:
        value = json.load(open(args.verdict, encoding="utf-8"))
        if not isinstance(value, dict) or value.get("verdict") not in {"pass", "fail", "blocked"}:
            raise ValueError("verifier verdict must be pass, fail, or blocked")
        if not OID.fullmatch(args.commit) or value.get("commit_oid") != args.commit:
            raise ValueError("verifier verdict is not bound to the exact candidate commit")
        if value.get("implementer_run_id") != args.implementer_run:
            raise ValueError("verifier verdict names the wrong implementer run")
        if not isinstance(value.get("summary"), str) or not value["summary"].strip():
            raise ValueError("verifier summary is required")
        evidence = value.get("evidence")
        risks = value.get("risks")
        if not isinstance(evidence, list) or not evidence or any(not isinstance(item, str) or not item.strip() for item in evidence):
            raise ValueError("verifier evidence must be a non-empty string array")
        if not isinstance(risks, list) or any(not isinstance(item, str) for item in risks):
            raise ValueError("verifier risks must be a string array")
        print(json.dumps(value, sort_keys=True))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERR {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

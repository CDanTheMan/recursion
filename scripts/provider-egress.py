#!/usr/bin/env python3
"""Resolve a reviewed provider-egress profile without probing or changing a system."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROFILE_RE = re.compile(r"[a-z][a-z0-9-]{1,63}\Z")
HOST_RE = re.compile(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\Z")
ROOT = Path(__file__).resolve().parent


def load(profile: str) -> dict:
    if not PROFILE_RE.fullmatch(profile):
        raise ValueError("invalid provider profile")
    value = json.loads((ROOT / "provider-egress-profiles.json").read_text(encoding="utf-8"))
    item = value["profiles"][profile]
    if not isinstance(item, dict) or item.get("provider") is None:
        raise ValueError("provider profile is invalid")
    endpoints = item.get("endpoints")
    if not isinstance(endpoints, list) or len(set(endpoints)) != len(endpoints) \
            or any(not isinstance(v, str) or not HOST_RE.fullmatch(v) for v in endpoints):
        raise ValueError("provider profile endpoints are invalid")
    if not isinstance(item.get("namespace"), str) or not PROFILE_RE.fullmatch(item["namespace"]):
        raise ValueError("provider profile namespace is invalid")
    if not isinstance(item.get("proxy_port"), int) or not 1024 <= item["proxy_port"] <= 65535:
        raise ValueError("provider profile proxy port is invalid")
    return {"profile": profile, **item}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile")
    parser.add_argument("--provider", required=True)
    parser.add_argument("--endpoint", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        item = load(args.profile)
        if item["provider"] != args.provider:
            raise ValueError("provider does not match egress profile")
        if sorted(args.endpoint) != sorted(item["endpoints"]):
            raise ValueError("endpoints do not match egress profile")
        print(json.dumps(item, sort_keys=True, separators=(",", ":")))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"provider-egress: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

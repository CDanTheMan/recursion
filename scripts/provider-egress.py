#!/usr/bin/env python3
"""Resolve a reviewed provider-egress profile without probing or changing a system."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROFILE_RE = re.compile(r"[a-z][a-z0-9-]{1,63}\Z")
HOST_RE = re.compile(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\Z")
ENV_RE = re.compile(r"[A-Z][A-Z0-9_]{2,63}\Z")
ROOT = Path(__file__).resolve().parent

_SCRIPT_DIR = ROOT
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

class FirstPartyImportError(ImportError):
    """The controller safety module is absent or malformed."""


try:
    from phase5_safety import BoundaryError, pinned_directory, read_bytes
except Exception as exc:
    module_name = getattr(exc, "name", None) or "phase5_safety"
    import_error = FirstPartyImportError(
        f"first-party module '{module_name}' is unavailable or malformed; searched {_SCRIPT_DIR}"
    )
    if __name__ == "__main__":
        print(f"provider-egress: first-party import failed: {import_error}", file=sys.stderr)
        raise SystemExit(95)
    raise import_error from None


def canonical_controller_root(value: str) -> Path:
    try:
        with pinned_directory(value) as (_, requested_value):
            requested = Path(requested_value)
        configured_value = os.environ.get("RECURSION_ROOT", "").strip()
        with pinned_directory(configured_value or ROOT.parent) as (_, configured_path):
            configured = Path(configured_path)
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        raise ValueError("controller root is unavailable") from exc
    if requested != configured:
        raise ValueError("controller root is not the canonical controller root")
    return requested


def authenticated_profile_bytes(root: Path, commit: str) -> bytes:
    relative = "scripts/provider-egress-profiles.json"
    path = root / relative
    try:
        # read_bytes performs the reparse-attribute check, pins the parent, opens
        # the leaf relative to that pinned handle, and verifies the opened handle
        # before returning.  Check and use are therefore one operation; no
        # resolve()/is_symlink() pathname decision can race the read.
        live = read_bytes(path, label="provider profile registry", private=True)
        if live is None:
            raise BoundaryError("provider profile registry is unavailable")
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        raise ValueError("provider profile registry is not a regular non-reparse file") from exc
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
                          capture_output=True, text=True, check=False)
    tree = subprocess.run(["git", "-C", str(root), "ls-tree", "-z", commit, "--", relative],
                          capture_output=True, check=False)
    committed = subprocess.run(["git", "-C", str(root), "show", f"{commit}:{relative}"],
                                capture_output=True, check=False)
    rows = [row for row in tree.stdout.split(b"\0") if row]
    mode = rows[0].split(b" ", 1)[0] if len(rows) == 1 else b""
    if head.returncode or head.stdout.strip() != commit or tree.returncode or committed.returncode or len(rows) != 1 \
            or mode not in {b"100644", b"100755"} or live != committed.stdout:
        raise ValueError("provider profile registry differs from controller commit")
    return committed.stdout


def load(profile: str, controller_root: str | None = None, controller_commit: str | None = None) -> dict:
    if not PROFILE_RE.fullmatch(profile):
        raise ValueError("invalid provider profile")
    if (controller_root is None) != (controller_commit is None):
        raise ValueError("controller policy provenance is incomplete")
    if controller_root is not None:
        value = json.loads(authenticated_profile_bytes(canonical_controller_root(controller_root), controller_commit).decode("utf-8"))
    else:
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
    env_allowlist = item.get("env_allowlist")
    if not isinstance(env_allowlist, list) or len(set(env_allowlist)) != len(env_allowlist) \
            or any(not isinstance(v, str) or not ENV_RE.fullmatch(v) for v in env_allowlist):
        raise ValueError("provider profile env allowlist is invalid")
    return {"profile": profile, **item}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile")
    parser.add_argument("--provider", required=True)
    parser.add_argument("--endpoint", action="append", default=[])
    parser.add_argument("--controller-root")
    parser.add_argument("--controller-commit")
    args = parser.parse_args(argv)
    try:
        item = load(args.profile, args.controller_root, args.controller_commit)
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
    try:
        raise SystemExit(main(sys.argv[1:]))
    except FirstPartyImportError as exc:
        print(f"provider-egress: first-party import failed: {exc}", file=sys.stderr)
        raise SystemExit(95)

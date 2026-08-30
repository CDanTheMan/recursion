#!/usr/bin/env python3
"""Resolve provider-egress policy at either the Phase 4 or Phase 5 boundary.

The Phase 4 subcommands retain the deployed profile-directory and proxy-environment
contract.  The positional Phase 5 form authenticates the controller-owned registry
against an exact commit before returning a profile.  Neither form probes a provider or
changes a system.
"""

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
    """A required controller safety module is absent or malformed."""


try:
    from phase5_safety import (BoundaryError, MAX_MANIFEST_BYTES, _git_show_bounded,
                               pinned_directory, read_bytes)
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
        live = read_bytes(path, label="provider profile registry",
                          max_bytes=MAX_MANIFEST_BYTES, private=True)
        if live is None:
            raise BoundaryError("provider profile registry is unavailable")
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        if "is too large" in str(exc):
            raise ValueError("provider profile registry is too large") from exc
        raise ValueError("provider profile registry is not a regular non-reparse file") from exc
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
                          capture_output=True, text=True, check=False)
    tree = subprocess.run(["git", "-C", str(root), "ls-tree", "-z", commit, "--", relative],
                          capture_output=True, check=False)
    try:
        committed_returncode, committed_stdout = _git_show_bounded(
            root, commit, relative, MAX_MANIFEST_BYTES, label="provider profile registry",
        )
    except BoundaryError as exc:
        if "is too large" in str(exc):
            raise ValueError("provider profile registry is too large") from exc
        raise ValueError("provider profile registry is unavailable") from exc
    rows = [row for row in tree.stdout.split(b"\0") if row]
    mode = rows[0].split(b" ", 1)[0] if len(rows) == 1 else b""
    # Defense in depth: an unexpected row count sets mode to b"", so the following
    # mode not in {b"100644", b"100755"} guard rejects the same malformed tree.
    # Keep this row-count refusal if that mode guard is narrowed.
    if head.returncode or head.stdout.strip() != commit or tree.returncode or committed_returncode or len(rows) != 1 \
            or mode not in {b"100644", b"100755"} or live != committed_stdout:
        raise ValueError("provider profile registry differs from controller commit")
    return committed_stdout


def load(profile: str, controller_root: str | None = None, controller_commit: str | None = None) -> dict:
    if not PROFILE_RE.fullmatch(profile):
        raise ValueError("invalid provider profile")
    if (controller_root is None) != (controller_commit is None):
        raise ValueError("controller policy provenance is incomplete")
    if controller_root is not None:
        raw = authenticated_profile_bytes(
            canonical_controller_root(controller_root), controller_commit,
        )
        value = json.loads(raw.decode("utf-8"), parse_constant=lambda name: (_ for _ in ()).throw(ValueError(name)))
    else:
        value = json.loads(
            (ROOT / "provider-egress-profiles.json").read_text(encoding="utf-8"),
            parse_constant=lambda name: (_ for _ in ()).throw(ValueError(name)),
        )
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


def phase5_refusal(exc: BaseException) -> str:
    """Map resolver failures to actionable, path-free caller diagnostics."""
    if isinstance(exc, OSError):
        return "provider profile registry is unavailable"
    if isinstance(exc, (json.JSONDecodeError, UnicodeDecodeError)):
        return "provider profile registry is invalid"
    if isinstance(exc, KeyError):
        return "provider profile is unavailable"
    detail = str(exc)
    known = (
        "controller policy provenance is incomplete",
        "controller root is unavailable",
        "controller root is not the canonical controller root",
        "provider policy provenance is unavailable",
        "provider profile registry is not a regular non-reparse file",
        "provider profile registry is too large",
        "provider profile registry differs from controller commit",
        "provider profile registry is unavailable",
        "provider profile registry is invalid",
        "invalid provider profile",
        "provider profile is invalid",
        "provider profile endpoints are invalid",
        "provider profile namespace is invalid",
        "provider profile proxy port is invalid",
        "provider profile env allowlist is invalid",
        "provider does not match egress profile",
        "endpoints do not match egress profile",
    )
    for message in known:
        if detail == message:
            return message
    if isinstance(exc, (ValueError, TypeError, OverflowError, RecursionError)):
        return "provider profile registry is invalid"
    return "provider egress request is invalid"


def phase4_main(argv: list[str]) -> int:
    try:
        from provider_contract import (
            ProviderProfileError,
            enabled_allowlist,
            enabled_profile_names,
            engine_profile,
            profile_directory,
            profile_for_provider,
            proxy_environment,
        )
    except Exception:
        print("provider-egress: first-party import failed: provider_contract", file=sys.stderr)
        return 95

    parser = argparse.ArgumentParser(prog="provider-egress")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("provider")
    inject = sub.add_parser("inject")
    inject.add_argument("provider")
    inject.add_argument("--endpoint", action="append", required=True)
    allowlist = sub.add_parser("allowlist")
    allowlist.add_argument("--provider", action="append", dest="providers")
    admission = sub.add_parser("admit-engine")
    admission.add_argument("engine")
    admission.add_argument("--endpoint", action="append", dest="endpoints")
    args = parser.parse_args(argv)
    try:
        directory = profile_directory(Path(__file__).resolve().parent)
        if args.command == "validate":
            profile = profile_for_provider(args.provider, directory)
            print(json.dumps({"id": profile["id"], "enabled": profile["enabled"]}, sort_keys=True))
        elif args.command == "inject":
            profile = profile_for_provider(args.provider, directory)
            # The controller passes bearer capabilities through an ephemeral environment value;
            # accepting it here keeps the token out of process argv and durable plan artifacts.
            token = os.environ.get("RECURSION_ASSIGNMENT_PROXY_TOKEN")
            identity = os.environ.get("RECURSION_ASSIGNMENT_IDENTITY")
            for key, value in sorted(proxy_environment(profile, args.endpoint, token, identity).items()):
                print(f"{key}={value}")
        elif args.command == "allowlist":
            for host, port in sorted(enabled_allowlist(directory, args.providers)):
                print(f"{host}:{port}")
        else:
            profile = engine_profile(args.engine, directory, args.endpoints)
            print(json.dumps({"engine": args.engine, "profile": profile["id"],
                              "authorities": profile["authorities"]}, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, UnicodeError, OverflowError,
            RecursionError, json.JSONDecodeError, ProviderProfileError) as exc:
        # Do not expose path-bearing loader details or platform OS text at a caller boundary.
        detail = str(exc)
        if "authorization is required" in detail:
            message = "assignment proxy authorization is required"
        elif "disabled" in detail:
            message = "provider egress profile is disabled"
        elif "unavailable" in detail:
            message = "provider egress is unavailable"
        else:
            message = "provider egress request is invalid"
        print(f"provider-egress: {message}", file=sys.stderr)
        return 96 if args.command in {"inject", "admit-engine"} else 2


def phase5_main(argv: list[str]) -> int:
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
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError,
            UnicodeDecodeError, OverflowError, RecursionError) as exc:
        print(f"provider-egress: {phase5_refusal(exc)}", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if argv is None else argv)
    if values and values[0] in {"validate", "inject", "allowlist", "admit-engine"}:
        return phase4_main(values)
    return phase5_main(values)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FirstPartyImportError as exc:
        print(f"provider-egress: first-party import failed: {exc}", file=sys.stderr)
        raise SystemExit(95)

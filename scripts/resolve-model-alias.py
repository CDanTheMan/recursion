#!/usr/bin/env python3
"""Resolve a reviewed role alias from human-owned environment configuration."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


ALIASES = {
    "sonnet-routine": ("RECURSION_MODEL_ALIAS_SONNET_ROUTINE", {"implementer"}),
    "opus-complex": ("RECURSION_MODEL_ALIAS_OPUS_COMPLEX", {"implementer", "verifier"}),
    "opus-review": ("RECURSION_MODEL_ALIAS_OPUS_REVIEW", {"verifier"}),
}

ALIAS_NAME_RE = re.compile(r"[a-z][a-z0-9-]{2,31}")
ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]{2,63}")
ENGINE_RE = re.compile(r"[a-z][a-z0-9-]{1,31}")
VALID_ROLES = {"implementer", "verifier"}
MAX_REGISTRY_BYTES = 1024 * 1024


class RegistryError(Exception):
    """The alias registry is absent, unreadable, or does not match the schema."""


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _registry_path() -> Path:
    override = os.environ.get("RECURSION_ALIAS_REGISTRY")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "engines" / "model-aliases.json"


def load_registry() -> dict[str, tuple[str, set[str]]]:
    path = _registry_path()
    try:
        raw = path.read_bytes()
        if len(raw) > MAX_REGISTRY_BYTES:
            raise RegistryError(f"alias registry {path} exceeds the 1 MiB bound")
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError, RegistryError) as exc:
        raise RegistryError(f"alias registry {path} is missing or unreadable ({exc})") from exc
    try:
        doc = json.loads(text, parse_constant=_reject_json_constant)
    except (json.JSONDecodeError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise RegistryError(f"alias registry {path} is not valid JSON ({exc})") from exc
    if not isinstance(doc, dict) or type(doc.get("schema_version")) is not int \
            or doc["schema_version"] != 1:
        raise RegistryError(f"alias registry {path} has an invalid schema")
    aliases = doc.get("aliases")
    if not isinstance(aliases, dict):
        raise RegistryError(f"alias registry {path} has an invalid schema")
    resolved: dict[str, tuple[str, set[str]]] = {}
    for name, entry in aliases.items():
        if not isinstance(name, str) or not ALIAS_NAME_RE.fullmatch(name):
            raise RegistryError(f"alias registry {path} has an invalid alias name {name!r}")
        if name in ALIASES:
            raise RegistryError(f"alias registry {path} redefines reserved alias {name!r}")
        if not isinstance(entry, dict):
            raise RegistryError(f"alias registry {path} has an invalid entry for {name!r}")
        env_name = entry.get("env")
        roles = entry.get("roles")
        if not isinstance(env_name, str) or not ENV_NAME_RE.fullmatch(env_name):
            raise RegistryError(f"alias registry {path} has an invalid env name for {name!r}")
        if not isinstance(roles, list) or not roles or not set(roles) <= VALID_ROLES:
            raise RegistryError(f"alias registry {path} has invalid roles for {name!r}")
        resolved[name] = (env_name, set(roles))
    return resolved


def _run_main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("alias")
    parser.add_argument("role", choices=("implementer", "verifier"))
    args = parser.parse_args()

    spec = ALIASES.get(args.alias)
    if spec is None:
        try:
            registry = load_registry()
        except RegistryError as exc:
            print(f"model-alias: {exc}", file=sys.stderr)
            return 2
        spec = registry.get(args.alias)
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
    if ":" in value:
        engine, _, model = value.partition(":")
        if not ENGINE_RE.fullmatch(engine) or not model:
            print(f"model-alias: invalid engine-qualified model {value!r}", file=sys.stderr)
            return 2
    print(value)
    return 0


def main() -> int:
    try:
        return _run_main()
    except (OSError, ValueError, TypeError, OverflowError, RecursionError,
            UnicodeError, json.JSONDecodeError) as exc:
        print(f"model-alias: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())

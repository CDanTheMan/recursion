"""Shared engine/alias contract helpers for the declarative engine plugins (D-015).

Consumed by the pilot-side validators (project-pilot.py, validate-control-state.py) so
the engine-name and model-alias rules live in one place. resolve-model-alias.py keeps
its own self-contained copy of the legacy table by design: it is the execution-time
authority and must not gain import surface.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from jsonl_durable import JsonlDurabilityError, read_durable_bytes

BUILTIN_ENGINES = frozenset({"claude", "hermes", "gate", "none", "deepseek", "openrouter"})
ENGINE_NAME_RE = re.compile(r"[a-z][a-z0-9-]{1,31}")
ALIAS_NAME_RE = re.compile(r"[a-z][a-z0-9-]{2,31}")
ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]{2,63}")
ROLES = frozenset({"implementer", "verifier"})
MAX_REGISTRY_BYTES = 1024 * 1024

LEGACY_ALIASES = {
    "sonnet-routine": frozenset({"implementer"}),
    "opus-complex": frozenset({"implementer", "verifier"}),
    "opus-review": frozenset({"verifier"}),
}
MAX_INPUT_BYTES = 8 * 1024 * 1024


def plugin_engine_name_ok(name: object) -> bool:
    """A well-formed plugin engine name: the manifest pattern, never a builtin."""
    return isinstance(name, str) and bool(ENGINE_NAME_RE.fullmatch(name)) \
        and name not in BUILTIN_ENGINES


def pilot_engine_ok(name: object) -> bool:
    """An engine a pilot plan may name: claude, or a well-formed plugin engine.

    hermes stays refused for pilot tasks (metered tool-calls were never sanctioned for
    the pilot hierarchy); enablement of a plugin engine is checked at execution time by
    work.sh admission, not here — an unenabled engine defers or escalates fail-closed.
    """
    return name == "claude" or plugin_engine_name_ok(name)


def default_registry_path(script_dir: Path | str) -> Path:
    return Path(script_dir) / "engines" / "model-aliases.json"


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _load_registry(registry_path: Path | str) -> dict[str, frozenset[str]] | None:
    """Return alias -> roles from a valid registry, or None when the registry is
    absent, unparseable, schema-invalid, or redefines a legacy alias (poisoned)."""
    try:
        encoded = read_durable_bytes(Path(registry_path), max_bytes=MAX_INPUT_BYTES)
        if encoded is None:
            return None
        raw = json.loads(
            encoded.decode("utf-8"),
            parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite JSON number")),
        )
    except (JsonlDurabilityError, OSError, ValueError, TypeError, OverflowError,
            RecursionError, UnicodeDecodeError):
        # read_durable_bytes raises JsonlDurabilityError (a RuntimeError subclass) when the
        # registry path is a reparse point or carries traversal components.  Without it here,
        # an unsafe registry path escapes as a raw traceback and absolute path, violating this
        # function's documented swallow-to-None contract and leaking at the callers'
        # (validate-control-state, project-pilot) boundaries.  RecursionError is a sibling of
        # JsonlDurabilityError under RuntimeError and does not cover it.
        return None
    if not isinstance(raw, dict) or type(raw.get("schema_version")) is not int \
            or raw["schema_version"] != 1:
        return None
    aliases = raw.get("aliases")
    if not isinstance(aliases, dict):
        return None
    loaded: dict[str, frozenset[str]] = {}
    for alias, spec in aliases.items():
        if not isinstance(alias, str) or not ALIAS_NAME_RE.fullmatch(alias) \
                or alias in LEGACY_ALIASES:
            return None
        if not isinstance(spec, dict):
            return None
        env_name = spec.get("env")
        roles = spec.get("roles")
        if not isinstance(env_name, str) or not ENV_NAME_RE.fullmatch(env_name):
            return None
        # Mirror resolve-model-alias.py's rules exactly (it is the execution authority);
        # duplicated role entries are tolerated there, so they are tolerated here.
        if not isinstance(roles, list) or not roles or not set(roles) <= ROLES:
            return None
        loaded[alias] = frozenset(roles)
    return loaded


def alias_role_ok(alias: object, role: str, registry_path: Path | str) -> bool:
    """True when the alias exists (legacy table first, then the registry) and approves
    the role. Every registry defect fails closed for registry aliases only."""
    if not isinstance(alias, str) or role not in ROLES:
        return False
    if alias in LEGACY_ALIASES:
        return role in LEGACY_ALIASES[alias]
    registry = _load_registry(registry_path)
    if registry is None:
        return False
    roles = registry.get(alias)
    return roles is not None and role in roles

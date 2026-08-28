#!/usr/bin/env python3
"""Red control: the shared engine/alias contract module for cross-engine verification.

Frozen contract (docs/plans/engine-plugin-architecture.md, Component 7): a task may name
`verifier_engine` distinct from `engine`; the pilot-side validators accept claude or a
well-formed plugin engine name, and accept model aliases from the legacy set or the
shipped registry with role enforcement. scripts/engine_contract.py does not exist yet,
so this control fails red until the implementation commit.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SOURCE / "scripts"))

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def main() -> int:
    try:
        import engine_contract as ec
    except ImportError as exc:
        print(f"FAIL - engine_contract module imports ({exc})")
        print("cross-engine-contract.test: 1 FAILED")
        return 1

    check(ec.BUILTIN_ENGINES == frozenset(
        {"claude", "hermes", "gate", "none", "deepseek", "openrouter"}
    ), "BUILTIN_ENGINES is the exact builtin set")

    for name, expect in [
        ("gemini", True), ("opencode-local", True), ("claude", False), ("hermes", False),
        ("gate", False), ("none", False), ("deepseek", False), ("openrouter", False),
        ("Gemini", False), ("a", False), ("x" * 40, False), ("", False), ("../etc", False),
    ]:
        check(ec.plugin_engine_name_ok(name) is expect,
              f"plugin_engine_name_ok({name!r}) is {expect}")

    for name, expect in [
        ("claude", True), ("gemini", True), ("cursor", True), ("opencode-local", True),
        ("hermes", False), ("gate", False), ("none", False), ("deepseek", False),
        ("openrouter", False), ("Cursor", False), ("", False),
    ]:
        check(ec.pilot_engine_ok(name) is expect, f"pilot_engine_ok({name!r}) is {expect}")

    with tempfile.TemporaryDirectory() as tmp:
        registry = Path(tmp) / "model-aliases.json"

        # Legacy aliases work regardless of the registry file state.
        for alias, role, expect in [
            ("sonnet-routine", "implementer", True), ("sonnet-routine", "verifier", False),
            ("opus-review", "verifier", True), ("opus-review", "implementer", False),
            ("opus-complex", "implementer", True), ("opus-complex", "verifier", True),
        ]:
            check(ec.alias_role_ok(alias, role, registry) is expect,
                  f"legacy alias_role_ok({alias!r}, {role!r}) is {expect} with absent registry")

        # Non-legacy aliases fail closed while the registry is absent.
        check(ec.alias_role_ok("cursor-primary", "implementer", registry) is False,
              "registry alias fails closed when the registry is absent")

        registry.write_text(json.dumps({
            "schema_version": 1,
            "aliases": {
                "stub-alias": {"env": "STUB_ALIAS_MODEL", "roles": ["implementer"]},
            },
        }), encoding="utf-8")
        check(ec.alias_role_ok("stub-alias", "implementer", registry) is True,
              "registry alias resolves with its approved role")
        check(ec.alias_role_ok("stub-alias", "verifier", registry) is False,
              "registry alias refuses an unapproved role")
        check(ec.alias_role_ok("missing-alias", "implementer", registry) is False,
              "unknown alias fails closed")

        # A registry redefining a legacy alias poisons registry lookups, never legacy ones.
        registry.write_text(json.dumps({
            "schema_version": 1,
            "aliases": {
                "opus-review": {"env": "X_OVERRIDE", "roles": ["implementer"]},
                "stub-alias": {"env": "STUB_ALIAS_MODEL", "roles": ["implementer"]},
            },
        }), encoding="utf-8")
        check(ec.alias_role_ok("stub-alias", "implementer", registry) is False,
              "legacy-colliding registry poisons registry alias lookups")
        check(ec.alias_role_ok("opus-review", "verifier", registry) is True,
              "legacy alias still resolves against a colliding registry")

        registry.write_text("{ not json", encoding="utf-8")
        check(ec.alias_role_ok("stub-alias", "implementer", registry) is False,
              "unparseable registry fails closed")

    # The shipped registry passes through the same helper.
    shipped = ec.default_registry_path(SOURCE / "scripts")
    check(shipped == SOURCE / "scripts" / "engines" / "model-aliases.json",
          "default_registry_path points at the shipped registry")
    check(ec.alias_role_ok("cursor-primary", "verifier", shipped) is True,
          "shipped cursor-primary allows the verifier role")
    check(ec.alias_role_ok("sentry-local", "verifier", shipped) is False,
          "shipped sentry-local refuses the verifier role")

    if failures:
        print(f"cross-engine-contract.test: {len(failures)} FAILED")
        return 1
    print("cross-engine-contract.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

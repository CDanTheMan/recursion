#!/usr/bin/env python3
"""Red control: resolve-model-alias.py v2 contract (legacy compatibility + registry).

Frozen contract: docs/plans/engine-plugin-architecture.md, "Controls" #3, and the
worked spec handed down with this control set. scripts/resolve-model-alias.py is
still v1 (no registry support) and scripts/engines/model-aliases.json does not exist,
so the registry-related cases below are expected to fail until Component 3 lands.
The legacy-alias cases test byte-identical v1 behavior and may already pass.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
RESOLVE_ALIAS = SOURCE / "scripts" / "resolve-model-alias.py"
SHIPPED_REGISTRY = SOURCE / "scripts" / "engines" / "model-aliases.json"

LEGACY = {
    "sonnet-routine": ("RECURSION_MODEL_ALIAS_SONNET_ROUTINE", {"implementer"}),
    "opus-complex": ("RECURSION_MODEL_ALIAS_OPUS_COMPLEX", {"implementer", "verifier"}),
    "opus-review": ("RECURSION_MODEL_ALIAS_OPUS_REVIEW", {"verifier"}),
}
CLEARED_NAMES = [env for env, _ in LEGACY.values()] + [
    "RECURSION_ALIAS_REGISTRY", "STUB_ALIAS_MODEL", "STUB_COLLIDE_ENV", "STUB_ALIAS2_MODEL",
]

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def clean_env(**overrides: str) -> dict:
    env = dict(os.environ)
    for name in CLEARED_NAMES:
        env.pop(name, None)
    env.update(overrides)
    return env


def run_alias(alias: str, role: str, env: dict) -> subprocess.CompletedProcess:
    argv = [sys.executable, str(RESOLVE_ALIAS), alias, role]
    return subprocess.run(argv, capture_output=True, text=True, env=env)


def write_registry(tmp_dir: Path, data: dict, name: str) -> Path:
    path = tmp_dir / name
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def test_legacy_basic() -> None:
    role_for = {"sonnet-routine": "implementer", "opus-complex": "implementer", "opus-review": "verifier"}
    for alias, (env_name, _roles) in LEGACY.items():
        role = role_for[alias]
        env = clean_env(**{env_name: "claude-sonnet-5"})
        result = run_alias(alias, role, env)
        check(
            result.returncode == 0 and result.stdout == "claude-sonnet-5\n",
            f"legacy {alias} resolves byte-identically (exit {result.returncode}, stdout {result.stdout!r})",
        )


def test_legacy_role_violation() -> None:
    env = clean_env(**{LEGACY["sonnet-routine"][0]: "claude-sonnet-5"})
    result = run_alias("sonnet-routine", "verifier", env)
    check(result.returncode == 2, f"sonnet-routine as verifier exits 2 (got {result.returncode})")

    env = clean_env(**{LEGACY["opus-review"][0]: "claude-sonnet-5"})
    result = run_alias("opus-review", "implementer", env)
    check(result.returncode == 2, f"opus-review as implementer exits 2 (got {result.returncode})")


def test_legacy_env_absent() -> None:
    env = clean_env()
    result = run_alias("sonnet-routine", "implementer", env)
    check(result.returncode == 3, f"legacy alias with absent env exits 3 (got {result.returncode})")


def test_legacy_unsafe_value() -> None:
    env = clean_env(**{LEGACY["sonnet-routine"][0]: "bad;model"})
    result = run_alias("sonnet-routine", "implementer", env)
    check(result.returncode == 2, f"legacy alias with unsafe characters exits 2 (got {result.returncode})")


def test_registry_resolution(tmp_dir: Path) -> None:
    registry = write_registry(
        tmp_dir,
        {"schema_version": 1, "aliases": {"stub-alias": {"env": "STUB_ALIAS_MODEL", "roles": ["implementer"]}}},
        "registry-basic.json",
    )

    env = clean_env(RECURSION_ALIAS_REGISTRY=str(registry), STUB_ALIAS_MODEL="deepseek-x")
    result = run_alias("stub-alias", "implementer", env)
    check(
        result.returncode == 0 and result.stdout == "deepseek-x\n",
        f"registry alias resolves (exit {result.returncode}, stdout {result.stdout!r})",
    )

    env = clean_env(RECURSION_ALIAS_REGISTRY=str(registry), STUB_ALIAS_MODEL="deepseek-x")
    result = run_alias("stub-alias", "verifier", env)
    check(result.returncode == 2, f"registry alias role enforcement exits 2 (got {result.returncode})")

    env = clean_env(RECURSION_ALIAS_REGISTRY=str(registry))
    result = run_alias("stub-alias", "implementer", env)
    check(result.returncode == 3, f"registry alias with absent env exits 3 (got {result.returncode})")


def test_engine_prefixed_values() -> None:
    env = clean_env(**{LEGACY["sonnet-routine"][0]: "cursor:gpt-5.2"})
    result = run_alias("sonnet-routine", "implementer", env)
    check(
        result.returncode == 0 and result.stdout == "cursor:gpt-5.2\n",
        f"engine:model value passes through unchanged (exit {result.returncode}, stdout {result.stdout!r})",
    )

    env = clean_env(**{LEGACY["sonnet-routine"][0]: ":model"})
    result = run_alias("sonnet-routine", "implementer", env)
    check(result.returncode == 2, f"empty engine part before colon exits 2 (got {result.returncode})")

    env = clean_env(**{LEGACY["sonnet-routine"][0]: "Cursor:gpt"})
    result = run_alias("sonnet-routine", "implementer", env)
    check(result.returncode == 2, f"invalid-case engine part exits 2 (got {result.returncode})")


def test_registry_collision(tmp_dir: Path) -> None:
    registry = write_registry(
        tmp_dir,
        {
            "schema_version": 1,
            "aliases": {
                "opus-review": {"env": "STUB_COLLIDE_ENV", "roles": ["verifier"]},
                "stub-alias": {"env": "STUB_ALIAS_MODEL", "roles": ["implementer"]},
            },
        },
        "registry-collide.json",
    )

    env = clean_env(RECURSION_ALIAS_REGISTRY=str(registry), **{LEGACY["opus-review"][0]: "claude-sonnet-5"})
    result = run_alias("opus-review", "verifier", env)
    check(
        result.returncode == 0 and result.stdout == "claude-sonnet-5\n",
        f"legacy opus-review still resolves despite colliding registry (exit {result.returncode})",
    )

    env = clean_env(RECURSION_ALIAS_REGISTRY=str(registry), STUB_ALIAS_MODEL="deepseek-x")
    result = run_alias("stub-alias", "implementer", env)
    check(result.returncode == 2, f"colliding registry poisons its own other aliases (got {result.returncode})")


def test_registry_absent(tmp_dir: Path) -> None:
    missing = tmp_dir / "does-not-exist.json"
    env = clean_env(RECURSION_ALIAS_REGISTRY=str(missing), STUB_ALIAS_MODEL="deepseek-x")
    result = run_alias("stub-alias", "implementer", env)
    check(result.returncode == 2, f"absent registry file: non-legacy alias exits 2 (got {result.returncode})")

    env = clean_env(RECURSION_ALIAS_REGISTRY=str(missing), **{LEGACY["sonnet-routine"][0]: "claude-sonnet-5"})
    result = run_alias("sonnet-routine", "implementer", env)
    check(
        result.returncode == 0 and result.stdout == "claude-sonnet-5\n",
        f"absent registry file: legacy alias still resolves (exit {result.returncode})",
    )


def test_shipped_registry() -> None:
    if not SHIPPED_REGISTRY.is_file():
        check(False, "shipped scripts/engines/model-aliases.json exists")
        return
    try:
        data = json.loads(SHIPPED_REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        check(False, f"shipped registry parses as JSON ({exc})")
        return
    check(data.get("schema_version") == 1, "shipped registry schema_version == 1")
    aliases = data.get("aliases", {})
    expected = {
        "cursor-primary": ("RECURSION_MODEL_ALIAS_CURSOR_PRIMARY", {"implementer", "verifier"}),
        "gemini-review": ("RECURSION_MODEL_ALIAS_GEMINI_REVIEW", {"verifier"}),
        "opencode-flex": ("RECURSION_MODEL_ALIAS_OPENCODE_FLEX", {"implementer", "verifier"}),
        "sentry-local": ("RECURSION_MODEL_ALIAS_SENTRY_LOCAL", {"implementer"}),
    }
    check(
        set(aliases) == set(expected),
        f"shipped registry has exactly the four starter aliases (found {sorted(aliases)})",
    )
    for name, (env_name, roles) in expected.items():
        entry = aliases.get(name)
        if entry is None:
            check(False, f"shipped alias present: {name}")
            continue
        check(
            entry.get("env") == env_name and set(entry.get("roles", [])) == roles,
            f"shipped alias {name} has contract env/roles",
        )


def main() -> int:
    test_legacy_basic()
    test_legacy_role_violation()
    test_legacy_env_absent()
    test_legacy_unsafe_value()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        test_registry_resolution(tmp_dir)
        test_engine_prefixed_values()
        test_registry_collision(tmp_dir)
        test_registry_absent(tmp_dir)
    test_shipped_registry()

    if failures:
        print(f"resolve-model-alias.test: {len(failures)} FAILED")
        return 1
    print("resolve-model-alias.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

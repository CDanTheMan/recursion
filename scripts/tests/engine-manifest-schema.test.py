#!/usr/bin/env python3
"""Validate every shipped engine with both the runtime resolver and the published schema."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - the hardening environment supplies it
    raise SystemExit(f"engine-manifest-schema.test: jsonschema is required: {exc}")

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "schemas/control-plane/v1/engine-manifest.schema.json").read_text())
ENGINES = ROOT / "scripts/engines"

resolver_spec = importlib.util.spec_from_file_location("resolve_engine", ROOT / "scripts/resolve-engine.py")
assert resolver_spec is not None and resolver_spec.loader is not None
resolver = importlib.util.module_from_spec(resolver_spec)
resolver_spec.loader.exec_module(resolver)


def main() -> int:
    jsonschema.Draft7Validator.check_schema(SCHEMA)
    # Use the stock Draft-7 validator as the schema authority.  Its standard
    # integer semantics intentionally admit 1.0; the runtime's plain-Python-int
    # rule is a stricter, safe-direction runtime check and is not expressible in
    # standard JSON Schema.  Do not replace this checker with a custom one.
    validator = jsonschema.Draft7Validator(SCHEMA)
    failures: list[str] = []
    for path in sorted(ENGINES.glob("*.json")):
        if path.name == "model-aliases.json":
            continue
        data = json.loads(path.read_text())
        errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
        if errors:
            failures.append(f"{path.name}: schema: {errors[0].message}")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/resolve-engine.py"), path.stem, "--validate"],
            capture_output=True, text=True,
        )
        if result.returncode:
            failures.append(f"{path.name}: resolver exit {result.returncode}: {result.stderr.strip()}")
    cursor = json.loads((ENGINES / "cursor.json").read_text())
    target = copy.deepcopy(cursor)
    target["runtime_layout"]["target"] = "."
    if not list(validator.iter_errors(target)):
        failures.append("schema accepted dot runtime target")
    target = copy.deepcopy(cursor)
    del target["network"]["profile"]
    if not list(validator.iter_errors(target)):
        failures.append("schema accepted provider-only network without profile")
    local = json.loads((ENGINES / "opencode-local.json").read_text())
    if list(validator.iter_errors(local)):
        failures.append("schema rejected the declared sentry-local no-egress engine")
    target = copy.deepcopy(local)
    target["network"]["policy"] = "provider-only"
    if not list(validator.iter_errors(target)):
        failures.append("schema accepted endpointless provider-only sentry-local network")
    target = copy.deepcopy(local)
    target["network"]["profile"] = "cursor"
    if not list(validator.iter_errors(target)):
        failures.append("schema accepted no-egress policy for a networked profile")

    # The published schema and the runtime validator must speak the same language for
    # the Phase 5 layout defaults/null compatibility and exit-code disjointness.
    sibling_missing_target = copy.deepcopy(cursor)
    del sibling_missing_target["runtime_layout"]["target"]
    schema_ok = not list(validator.iter_errors(sibling_missing_target))
    try:
        runtime_ok = resolver.validate_runtime_layout(sibling_missing_target["runtime_layout"]) is None
    except resolver.ManifestError:
        runtime_ok = False
    if not (schema_ok and runtime_ok):
        failures.append("schema/runtime disagree on sibling-tree default target")

    executable_null_source = copy.deepcopy(local)
    executable_null_source["runtime_layout"]["source"] = None
    schema_ok = not list(validator.iter_errors(executable_null_source))
    try:
        runtime_ok = resolver.validate_runtime_layout(executable_null_source["runtime_layout"]) is None
    except resolver.ManifestError:
        runtime_ok = False
    if not (schema_ok and runtime_ok):
        failures.append("schema/runtime disagree on executable-only null source")

    numeric_schema_only = []
    for field in ("schema_version", "concurrency_cap"):
        numeric = copy.deepcopy(cursor)
        numeric[field] = 1.0
        schema_ok = not list(validator.iter_errors(numeric))
        try:
            resolver.validate_manifest(numeric, "cursor")
        except resolver.ManifestError:
            runtime_ok = False
        else:
            runtime_ok = True
        if schema_ok and not runtime_ok:
            numeric_schema_only.append(field)
        else:
            failures.append(f"schema/runtime numeric semantics changed for field: {field}")

    expected_numeric_schema_only = {"schema_version", "concurrency_cap"}
    if set(numeric_schema_only) != expected_numeric_schema_only:
        failures.append("schema/runtime numeric exception inventory changed")

    overlapping_exit_codes = copy.deepcopy(cursor)
    overlapping_exit_codes["execution"]["exit_codes"]["auth"] = [0]
    schema_ok = not list(validator.iter_errors(overlapping_exit_codes))
    try:
        resolver.validate_execution(overlapping_exit_codes["execution"])
    except resolver.ManifestError:
        runtime_ok = False
    else:
        runtime_ok = True
    if schema_ok != runtime_ok or schema_ok:
        failures.append("schema/runtime disagree on overlapping execution exit codes")
    for provider, profile, endpoints, forbidden in (
        ("anthropic-claude-code", "anthropic", ["api.anthropic.com"], "GEMINI_API_KEY"),
        ("google-gemini", "gemini", ["generativelanguage.googleapis.com"], "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"),
        ("openrouter-via-opencode", "openrouter", ["openrouter.ai", "api.deepseek.com"], "GEMINI_API_KEY"),
        ("cursor", "cursor", ["api.cursor.com", "api2.cursor.sh",
                              "agentn.global.api5.cursor.sh", "agentn.global.api5lat.cursor.sh",
                              "agentn.global.api5geo.cursor.sh"], "OPENROUTER_API_KEY"),
    ):
        target = copy.deepcopy(cursor)
        target["billing"]["provider"] = provider
        target["network"] = {"policy": "provider-only", "profile": profile, "endpoints": endpoints}
        target["env_passthrough"] = [forbidden]
        if not list(validator.iter_errors(target)):
            failures.append(f"schema accepted {profile} provider env cross-smuggle")
    if failures:
        print("\n".join(failures))
        return 1
    print("schema/runtime differential: schema_only=2 runtime_only=0 "
          "(zero-fraction integers are standard-schema semantics)")
    print("engine-manifest-schema.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

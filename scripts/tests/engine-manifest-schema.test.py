#!/usr/bin/env python3
"""Validate every shipped engine with both the runtime resolver and the published schema."""

from __future__ import annotations

import copy
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


def main() -> int:
    jsonschema.Draft7Validator.check_schema(SCHEMA)
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
    for provider, profile, endpoints, forbidden in (
        ("anthropic-claude-code", "anthropic", ["api.anthropic.com"], "GEMINI_API_KEY"),
        ("google-gemini", "gemini", ["generativelanguage.googleapis.com"], "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"),
        ("openrouter-via-opencode", "openrouter", ["openrouter.ai", "api.deepseek.com"], "GEMINI_API_KEY"),
        ("cursor", "cursor", ["api.cursor.com", "api2.cursor.sh"], "OPENROUTER_API_KEY"),
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
    print("engine-manifest-schema.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

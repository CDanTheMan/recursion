#!/usr/bin/env python3
"""Red control: engine manifest field-rule validation, resolve-engine.py --validate.

Frozen contract: docs/plans/engine-plugin-architecture.md, "Controls" #1, and the
worked spec handed down with this control set. Neither scripts/resolve-engine.py nor
scripts/engines/*.json exist yet, so every case in this file is expected to fail until
Component 1 (manifests) and Component 2 (resolver --validate mode) land.
"""

from __future__ import annotations

import copy
from contextlib import contextmanager
import importlib.util
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
RESOLVE_ENGINE = SOURCE / "scripts" / "resolve-engine.py"
ENGINES_DIR = SOURCE / "scripts" / "engines"

resolver_spec = importlib.util.spec_from_file_location("resolve_engine", RESOLVE_ENGINE)
assert resolver_spec is not None and resolver_spec.loader is not None
resolver = importlib.util.module_from_spec(resolver_spec)
resolver_spec.loader.exec_module(resolver)

SHIPPED_MANIFESTS = ["gemini.json", "cursor.json", "opencode.json", "opencode-local.json"]

BASE_MANIFEST = {
    "schema_version": 1,
    "name": "sampleeng",
    "description": "Sample engine for red-control tests",
    "executable": "sampleeng",
    "argv": ["{{EXE}}", "-p", "{{PROMPT}}"],
    "model": {"required": False, "argv_suffix": ["--model", "{{MODEL}}"]},
    "roles": ["implementer"],
    "billing": {"basis": "flat-subscription", "provider": "google-gemini"},
    "network": {"policy": "provider-only", "profile": "gemini",
                 "endpoints": ["generativelanguage.googleapis.com"]},
    "availability_probe": None,
    "concurrency_cap": None,
    "env_passthrough": [],
}

failures: list[str] = []


@contextmanager
def test_directory(label: str):
    configured = os.environ.get("PHASE5_TEST_ROOT", "").strip()
    if configured:
        root = Path(configured)
        root.mkdir(parents=True, exist_ok=True)
        path = root / f"{label}-{secrets.token_hex(8)}"
        path.mkdir()
        try:
            yield path
        finally:
            shutil.rmtree(path, ignore_errors=True)
    else:
        with tempfile.TemporaryDirectory() as raw:
            yield Path(raw)


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def run_validate(engine: str, engine_dir: Path | None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if engine_dir is None:
        env.pop("RECURSION_ENGINE_DIR", None)
    else:
        env["RECURSION_ENGINE_DIR"] = str(engine_dir)
    argv = [sys.executable, str(RESOLVE_ENGINE), engine, "--validate"]
    return subprocess.run(argv, capture_output=True, text=True, env=env)


def write_manifest(engine_dir: Path, filename: str, data: dict) -> None:
    (engine_dir / filename).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_case(label: str, filename: str, engine_arg: str, data: dict, expected: int) -> None:
    with test_directory("engine-case") as tmp_dir:
        write_manifest(tmp_dir, filename, data)
        result = run_validate(engine_arg, tmp_dir)
        check(
            result.returncode == expected,
            f"{label} (exit {result.returncode}, want {expected})",
        )


def test_shipped_manifests() -> None:
    for filename in SHIPPED_MANIFESTS:
        engine = filename[: -len(".json")]
        path = ENGINES_DIR / filename
        if not path.is_file():
            check(False, f"shipped manifest present: {filename}")
            continue
        result = run_validate(engine, None)
        check(result.returncode == 0, f"shipped manifest validates: {filename} (exit {result.returncode})")


def test_missing_file() -> None:
    with test_directory("missing-manifest") as tmp_dir:
        result = run_validate("ghostengine", tmp_dir)
        check(result.returncode == 3, f"missing manifest file exits 3 (got {result.returncode})")


def test_mutations() -> None:
    baseline = copy.deepcopy(BASE_MANIFEST)
    run_case("valid manifest in temp dir validates", "sampleeng.json", "sampleeng", baseline, 0)

    missing_field = copy.deepcopy(BASE_MANIFEST)
    del missing_field["roles"]
    run_case("missing required field (roles) rejected", "sampleeng.json", "sampleeng", missing_field, 2)

    name_mismatch = copy.deepcopy(BASE_MANIFEST)
    name_mismatch["name"] = "othername"
    run_case("name not matching filename stem rejected", "sampleeng.json", "sampleeng", name_mismatch, 2)

    builtin_collision = copy.deepcopy(BASE_MANIFEST)
    builtin_collision["name"] = "claude"
    builtin_collision["executable"] = "claude"
    run_case("builtin-name collision (claude) rejected", "claude.json", "claude", builtin_collision, 2)

    exe_not_first = copy.deepcopy(BASE_MANIFEST)
    exe_not_first["argv"] = ["not-exe", "-p", "{{PROMPT}}"]
    run_case("argv element 0 not {{EXE}} rejected", "sampleeng.json", "sampleeng", exe_not_first, 2)

    missing_prompt = copy.deepcopy(BASE_MANIFEST)
    missing_prompt["argv"] = ["{{EXE}}", "-p", "hello"]
    run_case("argv missing {{PROMPT}} rejected", "sampleeng.json", "sampleeng", missing_prompt, 2)

    double_prompt = copy.deepcopy(BASE_MANIFEST)
    double_prompt["argv"] = ["{{EXE}}", "{{PROMPT}}", "{{PROMPT}}"]
    run_case("argv with two {{PROMPT}} elements rejected", "sampleeng.json", "sampleeng", double_prompt, 2)

    unknown_placeholder = copy.deepcopy(BASE_MANIFEST)
    unknown_placeholder["argv"] = ["{{EXE}}", "{{OTHER}}", "{{PROMPT}}"]
    run_case("unknown placeholder element rejected", "sampleeng.json", "sampleeng", unknown_placeholder, 2)

    bad_billing = copy.deepcopy(BASE_MANIFEST)
    bad_billing["billing"] = {"basis": "prepaid", "provider": "x"}
    run_case("billing.basis 'prepaid' rejected", "sampleeng.json", "sampleeng", bad_billing, 2)

    bad_passthrough = copy.deepcopy(BASE_MANIFEST)
    bad_passthrough["env_passthrough"] = ["lower_case"]
    run_case("env_passthrough lowercase entry rejected", "sampleeng.json", "sampleeng", bad_passthrough, 2)

    cross_provider_passthrough = copy.deepcopy(BASE_MANIFEST)
    cross_provider_passthrough["env_passthrough"] = ["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"]
    run_case("provider-scoped env cross-smuggle rejected", "sampleeng.json", "sampleeng",
             cross_provider_passthrough, 2)

    missing_profile = copy.deepcopy(BASE_MANIFEST)
    del missing_profile["network"]["profile"]
    run_case("provider-only network without profile rejected", "sampleeng.json", "sampleeng",
             missing_profile, 2)

    for engine, provider, profile, endpoints, forbidden in (
        ("gemini-test", "google-gemini", "gemini", ["generativelanguage.googleapis.com"],
         "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"),
        ("opencode-test", "openrouter-via-opencode", "openrouter", ["openrouter.ai", "api.deepseek.com"],
         "GEMINI_API_KEY"),
        ("cursor-test", "cursor", "cursor", ["api.cursor.com", "api2.cursor.sh"],
         "OPENROUTER_API_KEY"),
    ):
        cross = copy.deepcopy(BASE_MANIFEST)
        cross["name"] = engine
        cross["billing"]["provider"] = provider
        cross["network"] = {"policy": "provider-only", "profile": profile, "endpoints": endpoints}
        cross["env_passthrough"] = [forbidden]
        run_case(f"{profile} provider env cross-smuggle rejected", f"{engine}.json", engine, cross, 2)

    bad_probe = copy.deepcopy(BASE_MANIFEST)
    bad_probe["availability_probe"] = {
        "type": "tcp",
        "url_env": "RECURSION_ENGINE_SAMPLEENG_HEALTH_URL",
        "timeout_s": 5,
    }
    run_case("availability_probe type 'tcp' rejected", "sampleeng.json", "sampleeng", bad_probe, 2)

    bad_cap = copy.deepcopy(BASE_MANIFEST)
    bad_cap["concurrency_cap"] = 0
    run_case("concurrency_cap 0 rejected", "sampleeng.json", "sampleeng", bad_cap, 2)


def test_malformed_container_elements_are_typed() -> None:
    for field in ("roles", "env_passthrough"):
        malformed = copy.deepcopy(BASE_MANIFEST)
        malformed[field] = [[]]
        try:
            resolver.validate_manifest(malformed, "sampleeng")
        except resolver.ManifestError:
            pass
        except Exception as exc:  # the regression must not leak TypeError from set()
            check(False, f"{field} malformed element raises ManifestError, not {type(exc).__name__}")
        else:
            check(False, f"{field} malformed element rejected with ManifestError")
        with test_directory("malformed-element") as tmp_dir:
            write_manifest(tmp_dir, "sampleeng.json", malformed)
            result = run_validate("sampleeng", tmp_dir)
            check(result.returncode == 2 and "Traceback" not in result.stderr,
                  f"{field} malformed element is a typed resolver refusal")


def main() -> int:
    test_shipped_manifests()
    test_missing_file()
    test_mutations()
    test_malformed_container_elements_are_typed()

    if failures:
        print(f"engine-manifest.test: {len(failures)} FAILED")
        return 1
    print("engine-manifest.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

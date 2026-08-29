#!/usr/bin/env python3
"""Red control: resolve-engine.py full resolution (--role / --emit-plan) contract.

Frozen contract: docs/plans/engine-plugin-architecture.md, "Controls" #2, and the
worked spec handed down with this control set. scripts/resolve-engine.py does not
exist yet, so every case here is expected to fail until Component 2 lands.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
RESOLVE_ENGINE = SOURCE / "scripts" / "resolve-engine.py"

STUB_MANIFEST = {
    "schema_version": 1,
    "name": "stubeng",
    "description": "Stub engine manifest for resolve-engine.py controls",
    "executable": "stubeng",
    "argv": ["{{EXE}}", "-p", "{{PROMPT}}"],
    "model": {"required": False, "argv_suffix": ["--model", "{{MODEL}}"]},
    "roles": ["implementer"],
    "billing": {"basis": "metered", "provider": "google-gemini"},
    "network": {"policy": "provider-only", "profile": "gemini",
                 "endpoints": ["generativelanguage.googleapis.com"]},
    "availability_probe": {
        "type": "http",
        "url_env": "RECURSION_ENGINE_STUBENG_HEALTH_URL",
        "timeout_s": 5,
    },
    "concurrency_cap": 1,
    "env_passthrough": ["GEMINI_API_KEY"],
}

EXPECTED_PLAN = {
    "schema_version": 1,
    "engine": "stubeng",
    "executable": "stubeng",
    "argv": ["{{EXE}}", "-p", "{{PROMPT}}"],
    "model_required": False,
    "model_argv_suffix": ["--model", "{{MODEL}}"],
    "billing": {"basis": "metered", "provider": "google-gemini"},
    "availability_probe": {
        "type": "http",
        "url_env": "RECURSION_ENGINE_STUBENG_HEALTH_URL",
        "timeout_s": 5,
    },
    "concurrency_cap": 1,
    "env_passthrough": ["GEMINI_API_KEY"],
    "network": {"policy": "provider-only", "profile": "gemini",
                 "endpoints": ["generativelanguage.googleapis.com"]},
}

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def build_env(engine_dir: Path, plugins: str | None, enabled: str | None) -> dict:
    env = dict(os.environ)
    env["RECURSION_ENGINE_DIR"] = str(engine_dir)
    env.pop("RECURSION_ENGINE_PLUGINS", None)
    env.pop("RECURSION_ENGINE_STUBENG_ENABLED", None)
    if plugins is not None:
        env["RECURSION_ENGINE_PLUGINS"] = plugins
    if enabled is not None:
        env["RECURSION_ENGINE_STUBENG_ENABLED"] = enabled
    return env


def run_resolve(
    engine: str,
    role: str,
    plan_path: Path,
    engine_dir: Path,
    plugins: str | None,
    enabled: str | None,
) -> subprocess.CompletedProcess:
    env = build_env(engine_dir, plugins, enabled)
    argv = [
        sys.executable, str(RESOLVE_ENGINE), engine,
        "--role", role, "--emit-plan", str(plan_path),
    ]
    return subprocess.run(argv, capture_output=True, text=True, env=env)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        (tmp_dir / "stubeng.json").write_text(
            json.dumps(STUB_MANIFEST, indent=2) + "\n", encoding="utf-8"
        )

        # 1. Unknown engine -> 3, even with plugins fully enabled.
        plan = tmp_dir / "plan-unknown.json"
        result = run_resolve("ghostengine", "implementer", plan, tmp_dir, "1", "1")
        check(result.returncode == 3, f"unknown engine exits 3 (got {result.returncode})")
        check(not plan.exists(), "unknown engine emits no plan file")

        # 2. Plugins globally disabled -> 3.
        plan = tmp_dir / "plan-noplugins.json"
        result = run_resolve("stubeng", "implementer", plan, tmp_dir, None, "1")
        check(result.returncode == 3, f"plugins globally disabled exits 3 (got {result.returncode})")
        check(not plan.exists(), "plugins-disabled run emits no plan file")

        # 3. Plugins on, per-engine flag unset -> 3.
        plan = tmp_dir / "plan-noengineflag.json"
        result = run_resolve("stubeng", "implementer", plan, tmp_dir, "1", None)
        check(result.returncode == 3, f"per-engine flag disabled exits 3 (got {result.returncode})")
        check(not plan.exists(), "per-engine-disabled run emits no plan file")

        # 4. Both flags on, role not permitted -> 2.
        plan = tmp_dir / "plan-wrongrole.json"
        result = run_resolve("stubeng", "verifier", plan, tmp_dir, "1", "1")
        check(result.returncode == 2, f"role not permitted exits 2 (got {result.returncode})")
        check(not plan.exists(), "role-rejected run emits no plan file")

        # 5. Both flags on, valid role -> 0, plan matches the contract exactly.
        plan = tmp_dir / "plan-ok.json"
        result = run_resolve("stubeng", "implementer", plan, tmp_dir, "1", "1")
        check(result.returncode == 0, f"valid + enabled resolution exits 0 (got {result.returncode})")
        if result.returncode == 0 and plan.exists():
            try:
                emitted = json.loads(plan.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                check(False, f"emitted plan parses as JSON ({exc})")
            else:
                check(emitted == EXPECTED_PLAN, "emitted plan matches contract exactly")
        elif result.returncode == 0:
            check(False, "emitted plan file exists after successful resolution")

    if failures:
        print(f"resolve-engine.test: {len(failures)} FAILED")
        return 1
    print("resolve-engine.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

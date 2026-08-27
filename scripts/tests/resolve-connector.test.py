#!/usr/bin/env python3
"""Control: resolve-connector.py resolution (--name / --emit-plan) contract.

Frozen contract: docs/plans/engine-plugin-architecture.md Component 6 and
scripts/connectors/README.md. Mirrors scripts/tests/resolve-engine.test.py.

Exit-code roles under test: 3 = absent or disabled (nothing to run, and that is not an
error), 2 = present but invalid or malformed request (a broken manifest must never be
reported as merely absent), 0 = resolved, plan written.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
RESOLVE_CONNECTOR = SOURCE / "scripts" / "resolve-connector.py"

STUB_MANIFEST = {
    "schema_version": 1,
    "name": "stubconn",
    "description": "Stub connector manifest for resolve-connector.py controls",
    "executable": "/usr/local/bin/stubconn-send",
    "transport_argv": ["{{EXE}}", "--to", "{{DESTINATION}}", "--text", "{{MESSAGE}}", "--json"],
    "ack_contract": "telegram",
    "env_passthrough": ["STUBCONN_ENDPOINT"],
    "timeout_seconds": 20,
}

EXPECTED_PLAN = {
    "schema_version": 1,
    "connector": "stubconn",
    "executable": "/usr/local/bin/stubconn-send",
    "transport_argv": ["{{EXE}}", "--to", "{{DESTINATION}}", "--text", "{{MESSAGE}}", "--json"],
    "ack_contract": "telegram",
    "env_passthrough": ["STUBCONN_ENDPOINT"],
    "timeout_seconds": 20,
}

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def build_env(connector_dir: Path, connectors: str | None, enabled: str | None) -> dict:
    env = dict(os.environ)
    env["RECURSION_CONNECTOR_DIR"] = str(connector_dir)
    env.pop("RECURSION_CONNECTORS", None)
    env.pop("RECURSION_CONNECTOR_STUBCONN_ENABLED", None)
    if connectors is not None:
        env["RECURSION_CONNECTORS"] = connectors
    if enabled is not None:
        env["RECURSION_CONNECTOR_STUBCONN_ENABLED"] = enabled
    return env


def run_resolve(
    connector: str,
    plan_path: Path,
    connector_dir: Path,
    connectors: str | None,
    enabled: str | None,
) -> subprocess.CompletedProcess:
    argv = [
        sys.executable, str(RESOLVE_CONNECTOR),
        "--name", connector, "--emit-plan", str(plan_path),
    ]
    return subprocess.run(
        argv, capture_output=True, text=True, env=build_env(connector_dir, connectors, enabled)
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        (tmp_dir / "stubconn.json").write_text(
            json.dumps(STUB_MANIFEST, indent=2) + "\n", encoding="utf-8"
        )

        # 1. Unknown connector -> 3, even with both flags on.
        plan = tmp_dir / "plan-unknown.json"
        result = run_resolve("ghostconn", plan, tmp_dir, "1", "1")
        check(result.returncode == 3, f"unknown connector exits 3 (got {result.returncode})")
        check(not plan.exists(), "unknown connector emits no plan file")

        # 2. Connectors globally disabled -> 3.
        plan = tmp_dir / "plan-noconnectors.json"
        result = run_resolve("stubconn", plan, tmp_dir, None, "1")
        check(result.returncode == 3, f"connectors globally disabled exits 3 (got {result.returncode})")
        check(not plan.exists(), "connectors-disabled run emits no plan file")

        # 3. Global flag on, per-connector flag unset -> 3.
        plan = tmp_dir / "plan-noconnflag.json"
        result = run_resolve("stubconn", plan, tmp_dir, "1", None)
        check(result.returncode == 3, f"per-connector flag disabled exits 3 (got {result.returncode})")
        check(not plan.exists(), "per-connector-disabled run emits no plan file")

        # 4. A flag value other than exactly "1" is not enablement.
        plan = tmp_dir / "plan-flagtrue.json"
        result = run_resolve("stubconn", plan, tmp_dir, "1", "true")
        check(result.returncode == 3, f"flag value 'true' is not enablement (got {result.returncode})")
        check(not plan.exists(), "non-'1' flag value emits no plan file")

        # 5. Reserved builtin names are refused as malformed requests, not as absent.
        for reserved in ("telegram", "hermes"):
            plan = tmp_dir / f"plan-{reserved}.json"
            result = run_resolve(reserved, plan, tmp_dir, "1", "1")
            check(result.returncode == 2, f"reserved name {reserved!r} exits 2 (got {result.returncode})")
            check(not plan.exists(), f"reserved name {reserved!r} emits no plan file")

        # 6. Malformed connector name -> 2.
        plan = tmp_dir / "plan-badname.json"
        result = run_resolve("Stub Conn", plan, tmp_dir, "1", "1")
        check(result.returncode == 2, f"malformed connector name exits 2 (got {result.returncode})")
        check(not plan.exists(), "malformed-name run emits no plan file")

        # 7. Present but invalid -> 2, and 2 even when the flags are OFF: a broken manifest
        #    must not hide behind a disabled flag until someone flips it.
        broken_dir = tmp_dir / "broken"
        broken_dir.mkdir()
        broken = copy.deepcopy(STUB_MANIFEST)
        broken["ack_contract"] = "slack"
        (broken_dir / "stubconn.json").write_text(
            json.dumps(broken, indent=2) + "\n", encoding="utf-8"
        )
        plan = tmp_dir / "plan-invalid.json"
        result = run_resolve("stubconn", plan, broken_dir, "1", "1")
        check(result.returncode == 2, f"invalid manifest exits 2 (got {result.returncode})")
        check(not plan.exists(), "invalid-manifest run emits no plan file")
        plan = tmp_dir / "plan-invalid-off.json"
        result = run_resolve("stubconn", plan, broken_dir, None, None)
        check(result.returncode == 2, f"invalid manifest exits 2 with flags off (got {result.returncode})")

        # 8. Both flags on, valid manifest -> 0, plan matches the contract exactly.
        plan = tmp_dir / "plan-ok.json"
        result = run_resolve("stubconn", plan, tmp_dir, "1", "1")
        check(result.returncode == 0, f"valid + enabled resolution exits 0 (got {result.returncode})")
        if result.returncode == 0 and plan.exists():
            try:
                emitted = json.loads(plan.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                check(False, f"emitted plan parses as JSON ({exc})")
            else:
                check(emitted == EXPECTED_PLAN, "emitted plan matches contract exactly")
            leftovers = sorted(p.name for p in tmp_dir.glob(".connector-plan-*"))
            check(leftovers == [], f"atomic write leaves no temp file (found {leftovers})")
        elif result.returncode == 0:
            check(False, "emitted plan file exists after successful resolution")

        # 9. --validate cannot be combined with --name/--emit-plan; missing pair -> 2.
        combined = subprocess.run(
            [sys.executable, str(RESOLVE_CONNECTOR), "--validate", "--name", "stubconn"],
            capture_output=True, text=True, env=build_env(tmp_dir, "1", "1"),
        )
        check(combined.returncode == 2, f"--validate with --name exits 2 (got {combined.returncode})")
        lonely = subprocess.run(
            [sys.executable, str(RESOLVE_CONNECTOR), "--name", "stubconn"],
            capture_output=True, text=True, env=build_env(tmp_dir, "1", "1"),
        )
        check(lonely.returncode == 2, f"--name without --emit-plan exits 2 (got {lonely.returncode})")

    if failures:
        print(f"resolve-connector.test: {len(failures)} FAILED")
        return 1
    print("resolve-connector.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

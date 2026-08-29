#!/usr/bin/env python3
"""Phase 5 controls for wrapper runtime layout and inert machine discovery."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "scripts" / "runtime-layout.py"
MACHINE = ROOT / "scripts" / "registered-machine-capabilities.py"
RESOLVER = ROOT / "scripts" / "resolve-engine.py"
failures: list[str] = []


def check(condition: bool, label: str) -> None:
    print(("ok - " if condition else "FAIL - ") + label)
    if not condition:
        failures.append(label)


def test_runtime_tree_is_complete_and_read_only() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        source = base / "cursor-runtime"
        destination = base / "staged"
        source.mkdir()
        (source / "cursor-agent").write_text("#!/bin/sh\n", encoding="utf-8")
        (source / "index.js").write_text("console.log('sibling');\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(RUNTIME), "stage", "--source", str(source), "--destination", str(destination)],
            capture_output=True, text=True,
        )
        check(result.returncode == 0, "declared runtime directory stages successfully")
        check((destination / "cursor-agent").read_text(encoding="utf-8") == "#!/bin/sh\n",
              "wrapper entrypoint is copied")
        check((destination / "index.js").is_file(), "wrapper sibling runtime file is copied")
        check(not (destination / "index.js").stat().st_mode & 0o222,
              "staged runtime files have no write bit")
        outside = base / "outside.txt"
        outside.write_text("must not copy", encoding="utf-8")
        try:
            (source / "escape").symlink_to(outside)
        except (OSError, NotImplementedError):
            print("SKIP - symlink escape control requires symlink support")
        else:
            second = base / "staged-second"
            result = subprocess.run(
                [sys.executable, str(RUNTIME), "stage", "--source", str(source), "--destination", str(second)],
                capture_output=True, text=True,
            )
            check(result.returncode == 2, "runtime tree containing a symlink is refused")
            check(not (second / "escape").exists(), "symlink target is not copied into the worker tree")


def test_cursor_manifest_carries_phase5_contract() -> None:
    manifest = json.loads((ROOT / "scripts" / "engines" / "cursor.json").read_text(encoding="utf-8"))
    layout = manifest.get("runtime_layout", {})
    execution = manifest.get("execution", {})
    check(layout.get("mode") == "sibling-tree", "Cursor opts into sibling-tree runtime layout")
    check(layout.get("source") == "executable-directory", "Cursor runtime source is executable directory")
    check(execution.get("cancellation", {}).get("signal") == "TERM",
          "Cursor cancellation contract records TERM")
    check(set(execution.get("exit_codes", {})) == {"success", "auth", "runtime", "egress"},
          "Cursor exit evidence has distinct classifications")


def test_machine_adapter_is_disabled_and_local_only_when_explicitly_enabled() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        machine_dir = base / "machines"
        machine_dir.mkdir()
        (machine_dir / "test-machine.json").write_text(json.dumps({
            "schema_version": 1, "id": "test-machine", "kind": "registered-machine",
            "capabilities": ["workspace-edit", "structured-result"],
        }) + "\n", encoding="utf-8")
        output = base / "capabilities.json"
        env = dict(os.environ, RECURSION_MACHINE_DIR=str(machine_dir))
        disabled = subprocess.run(
            [sys.executable, str(MACHINE), "test-machine", "--emit", str(output)],
            capture_output=True, text=True, env=env,
        )
        check(disabled.returncode == 3 and not output.exists(),
              "registered-machine adapter is disabled by default")
        env.update({"RECURSION_REGISTERED_MACHINE_ADAPTER": "1",
                    "RECURSION_REGISTERED_MACHINE_TEST_MACHINE_ENABLED": "1"})
        enabled = subprocess.run(
            [sys.executable, str(MACHINE), "test-machine", "--emit", str(output)],
            capture_output=True, text=True, env=env,
        )
        value = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
        check(enabled.returncode == 0, "explicit machine adapter enablement reads descriptor")
        check(value.get("source") == "declared-local" and value.get("capabilities") == ["workspace-edit", "structured-result"],
              "machine capability result is attributed to the declared local record")


def test_legacy_manifest_still_resolves_without_new_fields() -> None:
    base = {
        "schema_version": 1, "name": "legacyeng", "description": "compat",
        "executable": "legacyeng", "argv": ["{{EXE}}", "-p", "{{PROMPT}}"],
        "model": {"required": False, "argv_suffix": ["--model", "{{MODEL}}"]},
        "roles": ["implementer"], "billing": {"basis": "local", "provider": "sentry-local"},
        "network": {"policy": "none", "profile": "sentry-local", "endpoints": []},
        "availability_probe": None, "concurrency_cap": None, "env_passthrough": [],
    }
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        (directory / "legacyeng.json").write_text(json.dumps(base) + "\n", encoding="utf-8")
        env = dict(os.environ, RECURSION_ENGINE_DIR=str(directory))
        result = subprocess.run([sys.executable, str(RESOLVER), "legacyeng", "--validate"],
                                capture_output=True, text=True, env=env)
        check(result.returncode == 0, "v1 local/no-egress manifest without Phase 5 fields remains valid")


def test_sentry_local_manifest_is_available_without_egress() -> None:
    result = subprocess.run(
        [sys.executable, str(RESOLVER), "opencode-local", "--validate"],
        capture_output=True, text=True,
    )
    check(result.returncode == 0, "sentry-local engine remains available as a no-egress engine")


def test_endpointless_networked_profile_is_rejected() -> None:
    base = {
        "schema_version": 1, "name": "endpointless", "description": "invalid",
        "executable": "endpointless", "argv": ["{{EXE}}", "-p", "{{PROMPT}}"],
        "model": {"required": False, "argv_suffix": []}, "roles": ["implementer"],
        "billing": {"basis": "local", "provider": "sentry-local"},
        "network": {"policy": "provider-only", "profile": "sentry-local", "endpoints": []},
        "availability_probe": None, "concurrency_cap": None, "env_passthrough": [],
    }
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        (directory / "endpointless.json").write_text(json.dumps(base) + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(RESOLVER), "endpointless", "--validate"],
            capture_output=True, text=True, env=dict(os.environ, RECURSION_ENGINE_DIR=str(directory)),
        )
        check(result.returncode == 2, "provider-only policy rejects a declared endpointless profile")


def test_provider_network_requires_profile() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        manifest = {
            "schema_version": 1, "name": "missingprofile", "description": "invalid",
            "executable": "missingprofile", "argv": ["{{EXE}}", "-p", "{{PROMPT}}"],
            "model": {"required": False, "argv_suffix": []}, "roles": ["implementer"],
            "billing": {"basis": "local", "provider": "sentry-local"},
            "network": {"policy": "provider-only", "endpoints": []},
            "availability_probe": None, "concurrency_cap": None, "env_passthrough": [],
        }
        (directory / "missingprofile.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(RESOLVER), "missingprofile", "--validate"],
            capture_output=True, text=True, env=dict(os.environ, RECURSION_ENGINE_DIR=str(directory)),
        )
        check(result.returncode == 2, "runtime resolver rejects provider-only network without profile")


def main() -> int:
    test_runtime_tree_is_complete_and_read_only()
    test_cursor_manifest_carries_phase5_contract()
    test_machine_adapter_is_disabled_and_local_only_when_explicitly_enabled()
    test_legacy_manifest_still_resolves_without_new_fields()
    test_sentry_local_manifest_is_available_without_egress()
    test_endpointless_networked_profile_is_rejected()
    test_provider_network_requires_profile()
    if failures:
        print(f"phase5-runtime-contract.test: {len(failures)} FAILED")
        return 1
    print("phase5-runtime-contract.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

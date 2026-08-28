#!/usr/bin/env python3
"""Hermetic Phase 4 provider-profile and proxy-injection controls."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from provider_contract import ProviderProfileError, assert_endpoints_match, load_profile, proxy_environment  # noqa: E402


def check(condition: bool, label: str, failures: list[str]) -> None:
    print(("ok - " if condition else "FAIL - ") + label)
    if not condition:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    profiles = sorted((ROOT / "scripts/providers").glob("*.json"))
    check(len(profiles) == 4, "all shipped provider profiles are present", failures)
    for path in profiles:
        profile = load_profile(path, path.stem)
        check(profile["enabled"] is False, f"shipped profile is disabled: {path.stem}", failures)
    cursor = load_profile(ROOT / "scripts/providers/cursor.json", "cursor")
    assert_endpoints_match(cursor, ["api.cursor.com", "api2.cursor.sh"])
    try:
        proxy_environment(cursor, ["api.cursor.com", "api2.cursor.sh"])
    except ProviderProfileError as exc:
        check("disabled" in str(exc), "disabled profile refuses proxy injection", failures)
    else:
        check(False, "disabled profile refuses proxy injection", failures)

    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        enabled = dict(cursor)
        enabled["enabled"] = True
        (directory / "cursor.json").write_text(json.dumps(enabled) + "\n", encoding="utf-8")
        env = dict(os.environ, RECURSION_PROVIDER_DIR=str(directory))
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/provider-egress.py"), "inject", "cursor",
             "--endpoint", "api.cursor.com", "--endpoint", "api2.cursor.sh"],
            capture_output=True, text=True, env=env,
        )
        check(result.returncode == 0, "enabled profile emits proxy environment", failures)
        check(result.stdout.splitlines() == sorted([
            "HTTP_PROXY=http://127.0.0.1:18080", "HTTPS_PROXY=http://127.0.0.1:18080"
        ]), "injection emits only the fixed loopback proxy", failures)
        mismatch = subprocess.run(
            [sys.executable, str(ROOT / "scripts/provider-egress.py"), "inject", "cursor",
             "--endpoint", "evil.example.com"],
            capture_output=True, text=True, env=env,
        )
        check(mismatch.returncode == 96, "endpoint outside the profile is typed refusal", failures)

    bad = json.loads((ROOT / "scripts/providers/cursor.json").read_text(encoding="utf-8"))
    bad["proxy"]["credential"] = "must-not-validate"
    try:
        load_profile_from_value = __import__("provider_contract").validate_profile
        load_profile_from_value(bad)
    except ProviderProfileError:
        check(True, "credential-shaped profile fields fail closed", failures)
    else:
        check(False, "credential-shaped profile fields fail closed", failures)
    if failures:
        print(f"provider-egress.test: {len(failures)} FAILED")
        return 1
    print("provider-egress.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

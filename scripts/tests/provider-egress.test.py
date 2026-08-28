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
from provider_contract import (DEPLOYED_PROFILE_DIR, ProviderProfileError, assert_endpoints_match,
                               engine_profile, load_profile, profile_directory,
                               proxy_environment)  # noqa: E402


def check(condition: bool, label: str, failures: list[str]) -> None:
    print(("ok - " if condition else "FAIL - ") + label)
    if not condition:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    profiles = sorted((ROOT / "scripts/providers").glob("*.json"))
    check(len(profiles) == 4, "all shipped provider profiles are present", failures)
    check(profile_directory(ROOT / "scripts") == DEPLOYED_PROFILE_DIR,
          "default provider directory is the deployed /etc directory", failures)
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
        for source in profiles:
            enabled = json.loads(source.read_text(encoding="utf-8"))
            enabled["enabled"] = True
            (directory / source.name).write_text(json.dumps(enabled) + "\n", encoding="utf-8")
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
        token = "A" * 64 + "." + "B" * 64
        authorized = subprocess.run(
            [sys.executable, str(ROOT / "scripts/provider-egress.py"), "inject", "cursor",
             "--endpoint", "api.cursor.com", "--endpoint", "api2.cursor.sh",
             "--assignment-token", token],
            capture_output=True, text=True, env=env,
        )
        check(authorized.returncode == 0 and "assignment:" in authorized.stdout
              and token in authorized.stdout,
              "assignment token is bound into the proxy transport URL", failures)
        issued = subprocess.run(
            [sys.executable, str(ROOT / "scripts/assignment-token.py"), "cursor", "assignment-a",
             "--key-file", str(directory / "capability.key")],
            capture_output=True, text=True, env=dict(env),
        )
        # The fixture key is deliberately absent: issuance must never silently fall back to a
        # public/default key or mint an unbound token.
        check(issued.returncode == 96 and "unavailable" in issued.stderr,
              "assignment capability issuance fails closed without the human-owned key", failures)
        required_env = dict(env, RECURSION_PROVIDER_PROXY_REQUIRED="1")
        missing_token = subprocess.run(
            [sys.executable, str(ROOT / "scripts/provider-egress.py"), "inject", "cursor",
             "--endpoint", "api.cursor.com", "--endpoint", "api2.cursor.sh"],
            capture_output=True, text=True, env=required_env,
        )
        check(missing_token.returncode == 96 and "authorization is required" in missing_token.stderr,
              "required proxy authorization fails closed when assignment is absent", failures)
        mismatch = subprocess.run(
            [sys.executable, str(ROOT / "scripts/provider-egress.py"), "inject", "cursor",
             "--endpoint", "evil.example.com"],
            capture_output=True, text=True, env=env,
        )
        check(mismatch.returncode == 96, "endpoint outside the profile is typed refusal", failures)

        engine_endpoints = {
            "cursor": ["api.cursor.com", "api2.cursor.sh"],
            "gemini": ["generativelanguage.googleapis.com"],
            "opencode": ["openrouter.ai", "api.deepseek.com"],
            "claude": ["api.anthropic.com"],
        }
        for engine, endpoints in engine_endpoints.items():
            try:
                admitted = engine_profile(engine, directory, endpoints)
            except ProviderProfileError as exc:
                check(False, f"enabled {engine} is admitted to its exact provider ({exc})", failures)
            else:
                check(admitted["enabled"] is True, f"enabled {engine} is admitted to its exact provider", failures)
        admission = subprocess.run(
            [sys.executable, str(ROOT / "scripts/provider-egress.py"), "admit-engine", "gemini"],
            capture_output=True, text=True, env=env,
        )
        check(admission.returncode == 0 and '"profile": "google-gemini"' in admission.stdout,
              "CLI admission is bound to the Gemini assignment", failures)
        disabled = json.loads((directory / "cursor.json").read_text(encoding="utf-8"))
        disabled["enabled"] = False
        (directory / "cursor.json").write_text(json.dumps(disabled) + "\n", encoding="utf-8")
        refusal = subprocess.run(
            [sys.executable, str(ROOT / "scripts/provider-egress.py"), "admit-engine", "cursor"],
            capture_output=True, text=True, env=env,
        )
        check(refusal.returncode == 96 and "disabled" in refusal.stderr,
              "assignment refuses when its provider profile is disabled", failures)

    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        for source in profiles:
            directory.joinpath(source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        try:
            __import__("provider_contract").enabled_profile_names(directory)
        except ProviderProfileError as exc:
            check("all provider profiles are disabled" in str(exc), "all-disabled profile set refuses", failures)
        else:
            check(False, "all-disabled profile set refuses", failures)

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

#!/usr/bin/env python3
"""Control: connector manifest field-rule validation, resolve-connector.py --validate.

Frozen contract: schemas/control-plane/v1/connector-manifest.schema.json and
docs/plans/engine-plugin-architecture.md Component 6. Mirrors
scripts/tests/engine-manifest.test.py: one mutation per rule, each rejected.

Two of these cases are inertness controls rather than field rules: the shipped
scripts/connectors/ directory must contain zero loadable manifests, and a file with the
.example extension must not be picked up by --validate.
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
CONNECTORS_DIR = SOURCE / "scripts" / "connectors"
EXAMPLE = CONNECTORS_DIR / "examples" / "telegram-alt.json.example"

BASE_MANIFEST = {
    "schema_version": 1,
    "name": "sampleconn",
    "description": "Sample connector for control tests",
    "executable": "/usr/local/bin/sampleconn-send",
    "transport_argv": ["{{EXE}}", "--to", "{{DESTINATION}}", "--text", "{{MESSAGE}}"],
    "ack_contract": "telegram",
    "env_passthrough": [],
    "timeout_seconds": 20,
}

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def run_validate(connector_dir: Path | None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if connector_dir is None:
        env.pop("RECURSION_CONNECTOR_DIR", None)
    else:
        env["RECURSION_CONNECTOR_DIR"] = str(connector_dir)
    argv = [sys.executable, str(RESOLVE_CONNECTOR), "--validate"]
    return subprocess.run(argv, capture_output=True, text=True, env=env)


def run_case(label: str, filename: str, data: dict, expected: int) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        (tmp_dir / filename).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        result = run_validate(tmp_dir)
        check(result.returncode == expected, f"{label} (exit {result.returncode}, want {expected})")


def mutated(**overrides) -> dict:
    data = copy.deepcopy(BASE_MANIFEST)
    data.update(overrides)
    return data


def test_shipped_directory_is_inert() -> None:
    loadable = sorted(path.name for path in CONNECTORS_DIR.glob("*.json"))
    check(loadable == [], f"scripts/connectors/ ships zero loadable manifests (found {loadable})")
    result = run_validate(None)
    check(result.returncode == 0, f"shipped connectors dir validates (exit {result.returncode})")
    check(EXAMPLE.is_file(), "examples/telegram-alt.json.example is present")


def test_example_is_real_but_unloadable() -> None:
    if not EXAMPLE.is_file():
        check(False, "example manifest content validates when copied to <name>.json")
        return
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    run_case("example content validates when copied to <name>.json", "telegram-alt.json", data, 0)
    # The extension alone is what keeps it inert: same bytes, .example suffix, not loaded.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        (tmp_dir / "telegram-alt.json.example").write_text(
            EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (tmp_dir / "garbage.json.example").write_text("{ not json at all", encoding="utf-8")
        result = run_validate(tmp_dir)
        check(result.returncode == 0, f".example files are not loaded by --validate (exit {result.returncode})")


def test_missing_directory() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        missing = Path(tmp) / "no-such-dir"
        result = run_validate(missing)
        check(result.returncode == 3, f"absent connector directory exits 3 (got {result.returncode})")


def test_mutations() -> None:
    run_case("valid manifest validates", "sampleconn.json", copy.deepcopy(BASE_MANIFEST), 0)

    missing_field = copy.deepcopy(BASE_MANIFEST)
    del missing_field["ack_contract"]
    run_case("missing required field (ack_contract) rejected", "sampleconn.json", missing_field, 2)

    unknown_key = mutated(retry_policy="exponential")
    run_case("unknown top-level key rejected", "sampleconn.json", unknown_key, 2)

    run_case("schema_version 2 rejected", "sampleconn.json", mutated(schema_version=2), 2)

    run_case(
        "name not matching filename stem rejected",
        "sampleconn.json",
        mutated(name="othername"),
        2,
    )
    run_case("uppercase name rejected", "Sampleconn.json", mutated(name="Sampleconn"), 2)

    reserved_telegram = mutated(name="telegram")
    run_case("reserved builtin name (telegram) rejected", "telegram.json", reserved_telegram, 2)
    reserved_hermes = mutated(name="hermes")
    run_case("reserved builtin name (hermes) rejected", "hermes.json", reserved_hermes, 2)

    run_case("empty description rejected", "sampleconn.json", mutated(description=""), 2)

    run_case(
        "relative executable rejected",
        "sampleconn.json",
        mutated(executable="sampleconn-send"),
        2,
    )
    run_case(
        "executable with '..' segment rejected",
        "sampleconn.json",
        mutated(executable="/usr/local/bin/../../tmp/evil"),
        2,
    )

    run_case(
        "transport_argv[0] not {{EXE}} rejected",
        "sampleconn.json",
        mutated(transport_argv=["sampleconn-send", "{{DESTINATION}}", "{{MESSAGE}}"]),
        2,
    )
    run_case(
        "transport_argv missing {{DESTINATION}} rejected",
        "sampleconn.json",
        mutated(transport_argv=["{{EXE}}", "--to", "home", "{{MESSAGE}}"]),
        2,
    )
    run_case(
        "transport_argv missing {{MESSAGE}} rejected",
        "sampleconn.json",
        mutated(transport_argv=["{{EXE}}", "--to", "{{DESTINATION}}"]),
        2,
    )
    run_case(
        "transport_argv with two {{MESSAGE}} elements rejected",
        "sampleconn.json",
        mutated(transport_argv=["{{EXE}}", "{{DESTINATION}}", "{{MESSAGE}}", "{{MESSAGE}}"]),
        2,
    )
    run_case(
        "transport_argv with a second {{EXE}} rejected",
        "sampleconn.json",
        mutated(transport_argv=["{{EXE}}", "{{EXE}}", "{{DESTINATION}}", "{{MESSAGE}}"]),
        2,
    )
    run_case(
        "unknown placeholder element rejected",
        "sampleconn.json",
        mutated(transport_argv=["{{EXE}}", "{{TOKEN}}", "{{DESTINATION}}", "{{MESSAGE}}"]),
        2,
    )

    run_case("ack_contract 'slack' rejected", "sampleconn.json", mutated(ack_contract="slack"), 2)
    run_case("ack_contract 'generic' rejected", "sampleconn.json", mutated(ack_contract="generic"), 2)

    run_case(
        "env_passthrough TELEGRAM_BOT_TOKEN rejected",
        "sampleconn.json",
        mutated(env_passthrough=["TELEGRAM_BOT_TOKEN"]),
        2,
    )
    run_case(
        "env_passthrough *_API_KEY rejected",
        "sampleconn.json",
        mutated(env_passthrough=["SAMPLECONN_API_KEY"]),
        2,
    )
    run_case(
        "env_passthrough *_SECRET rejected",
        "sampleconn.json",
        mutated(env_passthrough=["SAMPLECONN_SECRET"]),
        2,
    )
    run_case(
        "env_passthrough *_PASSWORD rejected",
        "sampleconn.json",
        mutated(env_passthrough=["SAMPLECONN_PASSWORD"]),
        2,
    )
    run_case(
        "env_passthrough lowercase entry rejected",
        "sampleconn.json",
        mutated(env_passthrough=["lower_case"]),
        2,
    )
    run_case(
        "env_passthrough duplicate entry rejected",
        "sampleconn.json",
        mutated(env_passthrough=["SAMPLECONN_ENDPOINT", "SAMPLECONN_ENDPOINT"]),
        2,
    )
    run_case(
        "env_passthrough non-credential name accepted",
        "sampleconn.json",
        mutated(env_passthrough=["SAMPLECONN_ENDPOINT"]),
        0,
    )

    run_case("timeout_seconds 0 rejected", "sampleconn.json", mutated(timeout_seconds=0), 2)
    run_case("timeout_seconds 121 rejected", "sampleconn.json", mutated(timeout_seconds=121), 2)
    run_case(
        "timeout_seconds non-integer rejected",
        "sampleconn.json",
        mutated(timeout_seconds=1.5),
        2,
    )


def test_bad_filename_stem() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        (tmp_dir / "Bad_Name.json").write_text(
            json.dumps(BASE_MANIFEST, indent=2) + "\n", encoding="utf-8"
        )
        result = run_validate(tmp_dir)
        check(result.returncode == 2, f"invalid filename stem rejected (got {result.returncode})")


def main() -> int:
    test_shipped_directory_is_inert()
    test_example_is_real_but_unloadable()
    test_missing_directory()
    test_mutations()
    test_bad_filename_stem()

    if failures:
        print(f"connector-manifest.test: {len(failures)} FAILED")
        return 1
    print("connector-manifest.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Resolve a declarative notification connector manifest, fail closed.

Validates scripts/connectors/<name>.json against the self-contained contract
described in schemas/control-plane/v1/connector-manifest.schema.json and, once
enablement is confirmed, emits a normalized transport plan for
scripts/connector-transport.py. See docs/plans/engine-plugin-architecture.md
Component 6 and scripts/connectors/README.md.

Nothing here sends anything. The resolver is pure validation plus plan emission;
notify.sh remains the sole sender and the sole acknowledgement validator.

Exit codes (mirroring scripts/resolve-engine.py):
  0  --validate: every *.json in the connectors dir is valid (zero files counts)
     --name:     the connector resolved and the plan was written
  2  a manifest exists but violates the contract, or the request is malformed
     (bad name, reserved builtin name, missing/contradictory flags on argv)
  3  the requested manifest is absent, or enablement is off

Usage:
  resolve-connector.py --validate
  resolve-connector.py --name <connector> --emit-plan <path>

RECURSION_CONNECTOR_DIR overrides the manifest directory. It is a control-only
hook so the hermetic tests can build disposable dirs; it is never set on the box.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

PROG = "resolve-connector"

NAME_RE = re.compile(r"[a-z][a-z0-9-]{1,31}")
ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]{2,63}")
# Deliberately over-broad substring match, no allowlist: a connector manifest is a
# tracked file, and the one credential this system holds (TELEGRAM_BOT_TOKEN) must
# never leave notify.sh. A false positive costs a rename; a false negative costs a leak.
SECRET_SUBSTRING_RE = re.compile(r"TOKEN|SECRET|KEY|PASSWORD")
POSIX_ABS_RE = re.compile(r"(/[^/\\]+)+")
WINDOWS_ABS_RE = re.compile(r"[A-Za-z]:[\\/]([^\\/]+[\\/])*[^\\/]+")
DOTDOT_SEGMENT_RE = re.compile(r"(^|[/\\])\.\.([/\\]|$)")
CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")

# notify.sh implements these two transports natively; a manifest may never shadow them.
BUILTIN_CONNECTORS = {"telegram", "hermes"}
KNOWN_PLACEHOLDERS = {"{{EXE}}", "{{DESTINATION}}", "{{MESSAGE}}"}
# One member until D-014 closes: notify.sh's validator accepts only a telegram-shaped ack.
ACK_CONTRACTS = {"telegram"}

TOP_LEVEL_KEYS = {
    "schema_version",
    "name",
    "description",
    "executable",
    "transport_argv",
    "ack_contract",
    "env_passthrough",
    "timeout_seconds",
}


class ConnectorError(Exception):
    """A manifest or request violates the contract (exit code 2)."""


class ConnectorUnavailable(Exception):
    """No such manifest, or enablement is off (exit code 3)."""


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def require_object_keys(obj: object, keys: set, where: str) -> dict:
    if not isinstance(obj, dict):
        raise ConnectorError(f"{where} must be a JSON object")
    missing = keys - obj.keys()
    if missing:
        raise ConnectorError(f"{where} missing required key(s): {', '.join(sorted(missing))}")
    extra = obj.keys() - keys
    if extra:
        raise ConnectorError(f"{where} has unknown key(s): {', '.join(sorted(extra))}")
    return obj


def validate_executable(executable: object) -> None:
    if not isinstance(executable, str) or not executable:
        raise ConnectorError("executable must be a nonempty string")
    if CONTROL_CHAR_RE.search(executable):
        raise ConnectorError("executable contains a control character")
    # Absolute is the invariant: no PATH search, no cwd-relative resolution, no shell.
    if not (POSIX_ABS_RE.fullmatch(executable) or WINDOWS_ABS_RE.fullmatch(executable)):
        raise ConnectorError("executable must be an absolute path with no empty segment")
    if DOTDOT_SEGMENT_RE.search(executable):
        raise ConnectorError("executable must not contain a '..' segment")


def validate_transport_argv(argv: object) -> None:
    if not isinstance(argv, list) or not argv:
        raise ConnectorError("transport_argv must be a nonempty list of strings")
    if not all(isinstance(item, str) and item for item in argv):
        raise ConnectorError("transport_argv elements must be nonempty strings")
    if argv[0] != "{{EXE}}":
        raise ConnectorError("transport_argv[0] must be the literal placeholder {{EXE}}")
    if argv.count("{{EXE}}") != 1:
        raise ConnectorError("{{EXE}} may appear only at transport_argv[0]")
    if argv.count("{{DESTINATION}}") != 1:
        raise ConnectorError("transport_argv must contain exactly one {{DESTINATION}} element")
    if argv.count("{{MESSAGE}}") != 1:
        raise ConnectorError("transport_argv must contain exactly one {{MESSAGE}} element")
    for item in argv:
        if item.startswith("{{") and item.endswith("}}") and item not in KNOWN_PLACEHOLDERS:
            raise ConnectorError(f"transport_argv contains an unknown placeholder {item!r}")
        if CONTROL_CHAR_RE.search(item):
            raise ConnectorError("transport_argv contains a control character")


def validate_env_passthrough(names: object) -> None:
    if not isinstance(names, list):
        raise ConnectorError("env_passthrough must be a list of strings")
    if len(set(names)) != len(names):
        raise ConnectorError("env_passthrough must not contain duplicates")
    for item in names:
        if not isinstance(item, str) or not ENV_NAME_RE.fullmatch(item):
            raise ConnectorError(f"env_passthrough contains an invalid env var name {item!r}")
        if SECRET_SUBSTRING_RE.search(item):
            raise ConnectorError(
                f"env_passthrough name {item!r} looks like a credential; connectors carry no "
                "secrets and there is no allowlist"
            )


def validate_manifest(data: object, connector: str) -> dict:
    obj = require_object_keys(data, TOP_LEVEL_KEYS, "manifest")
    if not is_plain_int(obj["schema_version"]) or obj["schema_version"] != 1:
        raise ConnectorError("schema_version must be 1")
    name = obj["name"]
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise ConnectorError("name must match ^[a-z][a-z0-9-]{1,31}$")
    if name != connector:
        raise ConnectorError(f"name {name!r} does not match manifest filename stem {connector!r}")
    if name in BUILTIN_CONNECTORS:
        raise ConnectorError(f"name {name!r} collides with a transport notify.sh implements natively")
    if not isinstance(obj["description"], str) or not obj["description"]:
        raise ConnectorError("description must be a nonempty string")
    validate_executable(obj["executable"])
    validate_transport_argv(obj["transport_argv"])
    if obj["ack_contract"] not in ACK_CONTRACTS:
        raise ConnectorError(f"ack_contract must be one of {sorted(ACK_CONTRACTS)}")
    validate_env_passthrough(obj["env_passthrough"])
    timeout = obj["timeout_seconds"]
    if not is_plain_int(timeout) or not (1 <= timeout <= 120):
        raise ConnectorError("timeout_seconds must be an integer in 1..120")
    return obj


def manifest_dir() -> Path:
    override = os.environ.get("RECURSION_CONNECTOR_DIR", "").strip()
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "connectors"


def manifest_path(connector: str) -> Path:
    return manifest_dir() / f"{connector}.json"


def load_manifest(path: Path, connector: str) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConnectorError(f"could not read manifest {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConnectorError(f"manifest {path} is not valid JSON: {exc}") from exc
    return validate_manifest(data, connector)


def enabled_env_name(connector: str) -> str:
    return "RECURSION_CONNECTOR_" + connector.upper().replace("-", "_") + "_ENABLED"


def build_plan(data: dict) -> dict:
    return {
        "schema_version": 1,
        "connector": data["name"],
        "executable": data["executable"],
        "transport_argv": list(data["transport_argv"]),
        "ack_contract": data["ack_contract"],
        "env_passthrough": list(data["env_passthrough"]),
        "timeout_seconds": data["timeout_seconds"],
    }


def resolve_connector(connector: str) -> dict:
    """Name -> validated plan, or raise. The one authority; the adapter imports this."""
    if not isinstance(connector, str) or not NAME_RE.fullmatch(connector):
        raise ConnectorError(f"invalid connector name {connector!r}: must match ^[a-z][a-z0-9-]{{1,31}}$")
    if connector in BUILTIN_CONNECTORS:
        raise ConnectorError(f"{connector!r} is a transport notify.sh implements natively, not a connector")
    path = manifest_path(connector)
    if not path.is_file():
        raise ConnectorUnavailable(f"manifest not found: {path}")
    data = load_manifest(path, connector)
    # Enablement is checked last so an invalid manifest is reported as invalid (2) rather
    # than hidden behind a disabled flag (3): a broken manifest must not look like an
    # absent one when a human later flips the flags.
    if os.environ.get("RECURSION_CONNECTORS", "") != "1":
        raise ConnectorUnavailable("RECURSION_CONNECTORS is not enabled")
    enable_var = enabled_env_name(connector)
    if os.environ.get(enable_var, "") != "1":
        raise ConnectorUnavailable(f"{enable_var} is not enabled")
    return build_plan(data)


def write_plan_atomically(plan: dict, out_path: Path) -> None:
    directory = out_path.parent if str(out_path.parent) else Path(".")
    fd, tmp_name = tempfile.mkstemp(prefix=".connector-plan-", suffix=".tmp", dir=str(directory))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(plan, handle, indent=2, sort_keys=False)
            handle.write("\n")
        os.replace(tmp_name, str(out_path))
    except BaseException:
        try:
            os.remove(tmp_name)
        except OSError:
            pass
        raise


def validate_directory() -> int:
    directory = manifest_dir()
    if not directory.is_dir():
        diag(f"connector directory not found: {directory}")
        return 3
    # Top level only, and *.json only: scripts/connectors/README.md and the
    # examples/*.json.example files are unloadable by construction.
    paths = sorted(directory.glob("*.json"))
    invalid = 0
    for path in paths:
        stem = path.name[: -len(".json")]
        if not NAME_RE.fullmatch(stem):
            diag(f"{path.name}: filename stem must match ^[a-z][a-z0-9-]{{1,31}}$")
            invalid += 1
            continue
        try:
            load_manifest(path, stem)
        except ConnectorError as exc:
            diag(f"{path.name}: {exc}")
            invalid += 1
    if invalid:
        diag(f"{invalid} of {len(paths)} manifest(s) invalid in {directory}")
        return 2
    diag(f"{len(paths)} manifest(s) valid in {directory}")
    return 0


def parse_args(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROG)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--name")
    parser.add_argument("--emit-plan", metavar="PATH")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])

    if args.validate:
        if args.name is not None or args.emit_plan is not None:
            diag("--validate cannot be combined with --name or --emit-plan")
            return 2
        return validate_directory()

    if args.name is None or args.emit_plan is None:
        diag("--name and --emit-plan are required unless --validate is given")
        return 2

    try:
        plan = resolve_connector(args.name)
    except ConnectorError as exc:
        diag(str(exc))
        return 2
    except ConnectorUnavailable as exc:
        diag(str(exc))
        return 3

    out_path = Path(args.emit_plan)
    try:
        write_plan_atomically(plan, out_path)
    except OSError as exc:
        diag(f"failed to write plan to {out_path}: {exc}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

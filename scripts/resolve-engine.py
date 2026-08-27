#!/usr/bin/env python3
"""Resolve a declarative engine plugin manifest, fail closed.

Validates scripts/engines/<engine>.json against the self-contained contract
described in schemas/control-plane/v1/engine-manifest.schema.json and, once
enablement is confirmed, emits a normalized launch plan for the sandbox
controller. See docs/plans/engine-plugin-architecture.md Component 2.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

PROG = "resolve-engine"

NAME_RE = re.compile(r"^[a-z][a-z0-9-]{1,31}$")
ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")
ENDPOINT_RE = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")

BUILTIN_ENGINES = {"claude", "hermes", "gate", "none", "deepseek", "openrouter"}
ROLE_CHOICES = ("implementer", "verifier")
KNOWN_PLACEHOLDERS = {"{{EXE}}", "{{PROMPT}}", "{{MODEL}}"}

TOP_LEVEL_KEYS = {
    "schema_version",
    "name",
    "description",
    "executable",
    "argv",
    "model",
    "roles",
    "billing",
    "network",
    "availability_probe",
    "concurrency_cap",
    "env_passthrough",
}
MODEL_KEYS = {"required", "argv_suffix"}
BILLING_KEYS = {"basis", "provider"}
BILLING_BASES = {"flat-subscription", "metered", "local"}
NETWORK_KEYS = {"policy", "endpoints"}
PROBE_KEYS = {"type", "url_env", "timeout_s"}


class ManifestError(Exception):
    """A manifest file exists but violates the contract (exit code 2)."""


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def is_plain_bool(value: object) -> bool:
    return isinstance(value, bool)


def is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def require_object_keys(obj: object, keys: set, where: str) -> dict:
    if not isinstance(obj, dict):
        raise ManifestError(f"{where} must be a JSON object")
    missing = keys - obj.keys()
    if missing:
        raise ManifestError(f"{where} missing required key(s): {', '.join(sorted(missing))}")
    extra = obj.keys() - keys
    if extra:
        raise ManifestError(f"{where} has unknown key(s): {', '.join(sorted(extra))}")
    return obj


def validate_argv(argv: object) -> None:
    if not isinstance(argv, list) or not argv:
        raise ManifestError("argv must be a nonempty list of strings")
    if not all(isinstance(item, str) and item for item in argv):
        raise ManifestError("argv elements must be nonempty strings")
    if argv[0] != "{{EXE}}":
        raise ManifestError("argv[0] must be the literal placeholder {{EXE}}")
    if argv.count("{{EXE}}") != 1:
        raise ManifestError("{{EXE}} may appear only at argv[0]")
    if argv.count("{{PROMPT}}") != 1:
        raise ManifestError("argv must contain exactly one {{PROMPT}} element")
    if argv.count("{{MODEL}}") > 1:
        raise ManifestError("{{MODEL}} may appear at most once in argv")
    for item in argv:
        if item.startswith("{{") and item.endswith("}}") and item not in KNOWN_PLACEHOLDERS:
            raise ManifestError(f"argv contains an unknown placeholder {item!r}")


def validate_model(model: object) -> None:
    obj = require_object_keys(model, MODEL_KEYS, "model")
    if not is_plain_bool(obj["required"]):
        raise ManifestError("model.required must be a boolean")
    suffix = obj["argv_suffix"]
    if not isinstance(suffix, list) or not all(isinstance(item, str) and item for item in suffix):
        raise ManifestError("model.argv_suffix must be a list of nonempty strings")
    for item in suffix:
        if item.startswith("{{") and item.endswith("}}") and item != "{{MODEL}}":
            raise ManifestError(f"model.argv_suffix contains an unknown placeholder {item!r}")
    if suffix.count("{{MODEL}}") > 1:
        raise ManifestError("{{MODEL}} may appear at most once in model.argv_suffix")


def validate_roles(roles: object) -> None:
    if not isinstance(roles, list) or not roles:
        raise ManifestError("roles must be a nonempty list")
    if len(set(roles)) != len(roles):
        raise ManifestError("roles must not contain duplicates")
    if not all(role in ROLE_CHOICES for role in roles):
        raise ManifestError(f"roles must be a subset of {ROLE_CHOICES}")


def validate_billing(billing: object) -> None:
    obj = require_object_keys(billing, BILLING_KEYS, "billing")
    if obj["basis"] not in BILLING_BASES:
        raise ManifestError(f"billing.basis must be one of {sorted(BILLING_BASES)}")
    if not isinstance(obj["provider"], str) or not obj["provider"]:
        raise ManifestError("billing.provider must be a nonempty string")


def validate_network(network: object) -> None:
    obj = require_object_keys(network, NETWORK_KEYS, "network")
    if obj["policy"] != "provider-only":
        raise ManifestError('network.policy must be "provider-only"')
    endpoints = obj["endpoints"]
    if not isinstance(endpoints, list):
        raise ManifestError("network.endpoints must be a list of strings")
    for item in endpoints:
        if not isinstance(item, str) or not ENDPOINT_RE.match(item):
            raise ManifestError(f"network.endpoints contains an invalid hostname {item!r}")


def validate_probe(probe: object) -> None:
    if probe is None:
        return
    obj = require_object_keys(probe, PROBE_KEYS, "availability_probe")
    if obj["type"] != "http":
        raise ManifestError('availability_probe.type must be "http"')
    if not isinstance(obj["url_env"], str) or not ENV_NAME_RE.match(obj["url_env"]):
        raise ManifestError("availability_probe.url_env is not a valid env var name")
    timeout = obj["timeout_s"]
    if not is_plain_int(timeout) or not (0 < timeout <= 60):
        raise ManifestError("availability_probe.timeout_s must be an integer in 1..60")


def validate_env_passthrough(names: object) -> None:
    if not isinstance(names, list):
        raise ManifestError("env_passthrough must be a list of strings")
    if len(set(names)) != len(names):
        raise ManifestError("env_passthrough must not contain duplicates")
    for item in names:
        if not isinstance(item, str) or not ENV_NAME_RE.match(item):
            raise ManifestError(f"env_passthrough contains an invalid env var name {item!r}")


def validate_manifest(data: object, engine: str) -> dict:
    obj = require_object_keys(data, TOP_LEVEL_KEYS, "manifest")
    if not is_plain_int(obj["schema_version"]) or obj["schema_version"] != 1:
        raise ManifestError("schema_version must be 1")
    name = obj["name"]
    if not isinstance(name, str) or not NAME_RE.match(name):
        raise ManifestError("name must match ^[a-z][a-z0-9-]{1,31}$")
    if name != engine:
        raise ManifestError(f"name {name!r} does not match manifest filename stem {engine!r}")
    if name in BUILTIN_ENGINES:
        raise ManifestError(f"name {name!r} collides with a builtin engine")
    if not isinstance(obj["description"], str) or not obj["description"]:
        raise ManifestError("description must be a nonempty string")
    executable = obj["executable"]
    if not isinstance(executable, str) or not NAME_RE.match(executable):
        raise ManifestError("executable must be a bare basename matching ^[a-z][a-z0-9-]{1,31}$")
    validate_argv(obj["argv"])
    validate_model(obj["model"])
    validate_roles(obj["roles"])
    validate_billing(obj["billing"])
    validate_network(obj["network"])
    validate_probe(obj["availability_probe"])
    cap = obj["concurrency_cap"]
    if cap is not None and not (is_plain_int(cap) and cap >= 1):
        raise ManifestError("concurrency_cap must be null or an integer >= 1")
    validate_env_passthrough(obj["env_passthrough"])
    return obj


def manifest_dir() -> Path:
    override = os.environ.get("RECURSION_ENGINE_DIR", "").strip()
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "engines"


def manifest_path(engine: str) -> Path:
    return manifest_dir() / f"{engine}.json"


def load_manifest(path: Path, engine: str) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManifestError(f"could not read manifest {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ManifestError(f"manifest {path} is not valid JSON: {exc}") from exc
    return validate_manifest(data, engine)


def enabled_env_name(engine: str) -> str:
    return "RECURSION_ENGINE_" + engine.upper().replace("-", "_") + "_ENABLED"


def build_plan(data: dict) -> dict:
    return {
        "schema_version": 1,
        "engine": data["name"],
        "executable": data["executable"],
        "argv": list(data["argv"]),
        "model_required": data["model"]["required"],
        "model_argv_suffix": list(data["model"]["argv_suffix"]),
        "billing": {
            "basis": data["billing"]["basis"],
            "provider": data["billing"]["provider"],
        },
        "availability_probe": data["availability_probe"],
        "concurrency_cap": data["concurrency_cap"],
        "env_passthrough": list(data["env_passthrough"]),
    }


def write_plan_atomically(plan: dict, out_path: Path) -> None:
    directory = out_path.parent if str(out_path.parent) else Path(".")
    fd, tmp_name = tempfile.mkstemp(prefix=".engine-plan-", suffix=".tmp", dir=str(directory))
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


def parse_args(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROG)
    parser.add_argument("engine")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--role", choices=ROLE_CHOICES)
    parser.add_argument("--emit-plan", metavar="PATH")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])

    if args.validate:
        if args.role is not None or args.emit_plan is not None:
            diag("--validate cannot be combined with --role or --emit-plan")
            return 2
    elif args.role is None or args.emit_plan is None:
        diag("--role and --emit-plan are required unless --validate is given")
        return 2

    engine = args.engine
    if not NAME_RE.match(engine):
        diag(f"invalid engine name {engine!r}: must match ^[a-z][a-z0-9-]{{1,31}}$")
        return 2
    if engine in BUILTIN_ENGINES:
        diag(f"{engine!r} is a builtin engine, not a plugin")
        return 2

    path = manifest_path(engine)
    if not path.is_file():
        diag(f"manifest not found: {path}")
        return 3

    try:
        data = load_manifest(path, engine)
    except ManifestError as exc:
        diag(str(exc))
        return 2

    if args.validate:
        return 0

    if os.environ.get("RECURSION_ENGINE_PLUGINS", "") != "1":
        diag("RECURSION_ENGINE_PLUGINS is not enabled")
        return 3
    enable_var = enabled_env_name(engine)
    if os.environ.get(enable_var, "") != "1":
        diag(f"{enable_var} is not enabled")
        return 3

    if args.role not in data["roles"]:
        diag(f"role {args.role!r} is not permitted for engine {engine!r}")
        return 2

    plan = build_plan(data)
    out_path = Path(args.emit_plan)
    try:
        write_plan_atomically(plan, out_path)
    except OSError as exc:
        diag(f"failed to write plan to {out_path}: {exc}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

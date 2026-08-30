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
import stat
import sys
import tempfile
from pathlib import Path

from provider_contract import HOST_RE, ProviderProfileError, assert_endpoints_match, profile_directory, profile_for_provider

PROG = "resolve-engine"

NAME_RE = re.compile(r"[a-z][a-z0-9-]{1,31}")
PROFILE_NAME_RE = re.compile(r"[a-z][a-z0-9-]{1,63}")
ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]{2,63}")
ENDPOINT_RE = HOST_RE

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
NETWORK_OPTIONAL_KEYS = {"profile"}
PROBE_KEYS = {"type", "url_env", "timeout_s"}
MAX_MANIFEST_BYTES = 2 * 1024 * 1024


class ManifestError(Exception):
    """A manifest file exists but violates the contract (exit code 2)."""


def reject_reparse_components(path: Path, where: str) -> None:
    if not isinstance(path, Path) or not path.is_absolute() \
            or any(part in {".", ".."} for part in path.parts):
        raise ManifestError(f"{where} must be a canonical absolute path")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ManifestError(f"{where} is unreadable") from exc
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) \
                or (getattr(info, "st_file_attributes", 0) & 0x400):
            raise ManifestError(f"{where} contains a symlink/reparse component")


def reject_json_constant(name: str) -> object:
    raise ValueError(f"non-finite JSON number {name} is forbidden")


def diag(message: str) -> None:
    # Diagnostics are a caller boundary: neither user-controlled paths nor host OS wording may
    # escape. Validation details stay deliberately structural and path-free.
    safe = re.sub(r"(?:[A-Za-z]:[\\/]|\\\\|(?<![A-Za-z0-9_])/)[^\s,;)]*", "<path>", str(message))
    print(f"{PROG}: {safe}", file=sys.stderr)


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
        raise ManifestError(f"{where} has unknown key(s)")
    return obj


def validate_argv(argv: object) -> None:
    if not isinstance(argv, list) or not argv:
        raise ManifestError("argv must be a nonempty list of strings")
    if not all(isinstance(item, str) and item for item in argv):
        raise ManifestError("argv elements must be nonempty strings")
    if len(set(argv)) != len(argv):
        raise ManifestError("argv elements must be unique")
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
            raise ManifestError("argv contains an unknown placeholder")


def validate_model(model: object) -> None:
    obj = require_object_keys(model, MODEL_KEYS, "model")
    if not is_plain_bool(obj["required"]):
        raise ManifestError("model.required must be a boolean")
    suffix = obj["argv_suffix"]
    if not isinstance(suffix, list) or not all(isinstance(item, str) and item for item in suffix):
        raise ManifestError("model.argv_suffix must be a list of nonempty strings")
    if len(set(suffix)) != len(suffix):
        raise ManifestError("model.argv_suffix elements must be unique")
    for item in suffix:
        if item.startswith("{{") and item.endswith("}}") and item != "{{MODEL}}":
            raise ManifestError("model.argv_suffix contains an unknown placeholder")
    if suffix.count("{{MODEL}}") > 1:
        raise ManifestError("{{MODEL}} may appear at most once in model.argv_suffix")


def validate_roles(roles: object) -> None:
    if not isinstance(roles, list) or not roles or len(roles) > 2:
        raise ManifestError("roles must contain one or two unique roles")
    if not all(isinstance(role, str) and role in ROLE_CHOICES for role in roles):
        raise ManifestError("roles contains an unsupported role")
    if len(set(roles)) != len(roles):
        raise ManifestError("roles must not contain duplicates")


def validate_billing(billing: object) -> None:
    obj = require_object_keys(billing, BILLING_KEYS, "billing")
    if not isinstance(obj["basis"], str) or obj["basis"] not in BILLING_BASES:
        raise ManifestError("billing.basis is unsupported")
    if not isinstance(obj["provider"], str) or not obj["provider"]:
        raise ManifestError("billing.provider must be a nonempty string")


def validate_network(network: object) -> None:
    if not isinstance(network, dict):
        raise ManifestError("network must be a JSON object")
    missing = NETWORK_KEYS - network.keys()
    extra = network.keys() - NETWORK_KEYS - NETWORK_OPTIONAL_KEYS
    if missing:
        raise ManifestError(f"network missing required key(s): {', '.join(sorted(missing))}")
    if extra:
        raise ManifestError(f"network has unknown key(s): {', '.join(sorted(extra))}")
    obj = network
    if obj["policy"] != "provider-only":
        raise ManifestError('network.policy must be "provider-only"')
    endpoints = obj["endpoints"]
    if not isinstance(endpoints, list):
        raise ManifestError("network.endpoints must be a list of strings")
    for item in endpoints:
        if not isinstance(item, str) or not ENDPOINT_RE.fullmatch(item):
            raise ManifestError("network.endpoints contains an invalid hostname")
    profile = obj.get("profile")
    if "profile" in obj and (not isinstance(profile, str) or not PROFILE_NAME_RE.fullmatch(profile)):
        raise ManifestError("network.profile must be a valid provider profile name")


def validate_probe(probe: object) -> None:
    if probe is None:
        return
    obj = require_object_keys(probe, PROBE_KEYS, "availability_probe")
    if obj["type"] != "http":
        raise ManifestError('availability_probe.type must be "http"')
    if not isinstance(obj["url_env"], str) or not ENV_NAME_RE.fullmatch(obj["url_env"]):
        raise ManifestError("availability_probe.url_env is not a valid env var name")
    timeout = obj["timeout_s"]
    if not is_plain_int(timeout) or not (0 < timeout <= 60):
        raise ManifestError("availability_probe.timeout_s must be an integer in 1..60")


def validate_env_passthrough(names: object) -> None:
    if not isinstance(names, list):
        raise ManifestError("env_passthrough must be a list of strings")
    for item in names:
        if not isinstance(item, str) or not ENV_NAME_RE.fullmatch(item):
            raise ManifestError(f"env_passthrough contains an invalid env var name {item!r}")
    if len(set(names)) != len(names):
        raise ManifestError("env_passthrough must not contain duplicates")


def validate_manifest(data: object, engine: str | None = None) -> dict:
    """Validate manifest content; filename binding is checked by ``load_manifest``.

    JSON Schema validates a manifest object without knowing which filename will carry it.  Keep
    this function at that same content-validation boundary so schema/runtime differential checks
    compare like with like; the file/engine binding is enforced immediately before use below.
    """
    obj = require_object_keys(data, TOP_LEVEL_KEYS, "manifest")
    if not is_plain_int(obj["schema_version"]) or obj["schema_version"] != 1:
        raise ManifestError("schema_version must be 1")
    name = obj["name"]
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise ManifestError("name must match ^[a-z][a-z0-9-]{1,31}$")
    if name in BUILTIN_ENGINES:
        raise ManifestError(f"name {name!r} collides with a builtin engine")
    if not isinstance(obj["description"], str) or not obj["description"]:
        raise ManifestError("description must be a nonempty string")
    executable = obj["executable"]
    if not isinstance(executable, str) or not NAME_RE.fullmatch(executable):
        raise ManifestError("executable must be a bare basename matching ^[a-z][a-z0-9-]{1,31}$")
    validate_argv(obj["argv"])
    validate_model(obj["model"])
    validate_roles(obj["roles"])
    validate_billing(obj["billing"])
    validate_network(obj["network"])
    profile_name = obj["network"].get("profile")
    if profile_name is not None:
        try:
            profile = profile_for_provider(profile_name, profile_directory(Path(__file__).resolve().parent))
            if profile["provider"] != obj["billing"]["provider"]:
                raise ProviderProfileError("profile provider does not match billing.provider")
            assert_endpoints_match(profile, obj["network"]["endpoints"])
        except ProviderProfileError as exc:
            raise ManifestError("network.profile is invalid") from exc
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
    reject_reparse_components(path, "engine manifest")
    try:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_reparse_tag", 0)) \
                or bool(getattr(info, "st_file_attributes", 0) & 0x400) \
                or not stat.S_ISREG(info.st_mode) or info.st_size > MAX_MANIFEST_BYTES:
            raise ManifestError("engine manifest is unavailable or too large")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags)
        try:
            opened_info = os.fstat(descriptor)
            if stat.S_ISLNK(opened_info.st_mode) or bool(getattr(opened_info, "st_reparse_tag", 0)) \
                    or bool(getattr(opened_info, "st_file_attributes", 0) & 0x400) \
                    or not stat.S_ISREG(opened_info.st_mode) \
                    or (opened_info.st_dev, opened_info.st_ino) != (info.st_dev, info.st_ino) \
                    or opened_info.st_size != info.st_size:
                raise ManifestError("engine manifest changed while reading")
            with os.fdopen(descriptor, "rb") as source:
                descriptor = -1
                raw_bytes = source.read(MAX_MANIFEST_BYTES + 1)
        finally:
            if descriptor != -1:
                os.close(descriptor)
        if len(raw_bytes) > MAX_MANIFEST_BYTES:
            raise ManifestError("engine manifest is too large")
        raw = raw_bytes.decode("utf-8", "strict")
    except ManifestError:
        raise
    except (OSError, UnicodeError, ValueError, TypeError, OverflowError) as exc:
        raise ManifestError("could not read engine manifest") from exc
    try:
        data = json.loads(raw, parse_constant=reject_json_constant)
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError) as exc:
        raise ManifestError("engine manifest is not valid JSON") from exc
    filename_stem = path.name[:-len(".json")] if path.name.endswith(".json") else ""
    if not NAME_RE.fullmatch(filename_stem) or filename_stem != engine:
        raise ManifestError("engine manifest filename stem is invalid")
    validated = validate_manifest(data, engine)
    if validated["name"] != filename_stem:
        raise ManifestError("manifest name does not match its filename stem")
    return validated


def enabled_env_name(engine: str) -> str:
    return "RECURSION_ENGINE_" + engine.upper().replace("-", "_") + "_ENABLED"


def build_plan(data: dict) -> dict:
    plan = {
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
    # Optional metadata keeps the v1 plan byte-for-byte compatible for manifests that do not
    # declare a Phase 4 profile. New manifests carry the provider boundary explicitly.
    profile = data["network"].get("profile")
    if profile is not None:
        plan["egress_profile"] = profile
        plan["network_endpoints"] = list(data["network"]["endpoints"])
    return plan


def write_plan_atomically(plan: dict, out_path: Path) -> None:
    directory = out_path.parent if str(out_path.parent) else Path(".")
    reject_reparse_components(directory, "engine plan output directory")
    reject_reparse_components(out_path, "engine plan output")
    fd, tmp_name = tempfile.mkstemp(prefix=".engine-plan-", suffix=".tmp", dir=str(directory))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(plan, handle, indent=2, sort_keys=False, allow_nan=False)
            handle.write("\n")
        reject_reparse_components(directory, "engine plan output directory")
        reject_reparse_components(out_path, "engine plan output")
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
    # Assignment authorization is deliberately not accepted here.  A resolved plan is a
    # durable/public controller artifact; bearer capabilities are minted by work.sh at launch
    # and carried out-of-band to the worker.  Keeping the resolver pure prevents a token from
    # being written into state/runs or appearing in a plan digest.
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
    if not NAME_RE.fullmatch(engine):
        diag("invalid engine name")
        return 2
    if engine in BUILTIN_ENGINES:
        diag(f"{engine!r} is a builtin engine, not a plugin")
        return 2

    path = manifest_path(engine)
    try:
        path_info = path.lstat()
    except OSError:
        path_info = None
    if path_info is None or stat.S_ISLNK(path_info.st_mode) \
            or bool(getattr(path_info, "st_reparse_tag", 0)) \
            or bool(getattr(path_info, "st_file_attributes", 0) & 0x400) \
            or not stat.S_ISREG(path_info.st_mode):
        diag("engine manifest is unavailable")
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
        reject_reparse_components(out_path.parent, "engine plan output directory")
    except ManifestError as exc:
        diag(str(exc))
        return 2
    try:
        write_plan_atomically(plan, out_path)
    except (OSError, TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as exc:
        diag("failed to write engine plan")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

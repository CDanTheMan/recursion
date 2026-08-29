#!/usr/bin/env python3
"""Resolve a declarative engine plugin manifest, fail closed.

Validates scripts/engines/<engine>.json against the self-contained contract
described in schemas/control-plane/v1/engine-manifest.schema.json and, once
enablement is confirmed, emits a normalized launch plan for the sandbox
controller. See docs/plans/engine-plugin-architecture.md Component 2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

class FirstPartyImportError(ImportError):
    """A required controller module is absent from the importing script's tree."""


try:
    from phase5_safety import (BoundaryError, atomic_write, decode_json,
                               pinned_directory, read_bytes)
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    import_error = FirstPartyImportError(
        f"first-party module 'phase5_safety' not found; searched {_SCRIPT_DIR}"
    )
    if __name__ == "__main__":
        print(f"resolve-engine: first-party import failed: {import_error}", file=sys.stderr)
        raise SystemExit(95)
    raise import_error from None

PROG = "resolve-engine"

NAME_RE = re.compile(r"[a-z][a-z0-9-]{1,31}")
ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]{2,63}")
ENDPOINT_RE = re.compile(r"[a-z0-9]([a-z0-9.-]*[a-z0-9])?")
COMMIT_RE = re.compile(r"[0-9a-f]{40,64}\Z")

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
    # Phase 5 contracts are optional for the original v1 manifests.  A missing
    # value means the v1 executable-only behavior, which keeps old fixtures and
    # builtin execution compatible while allowing wrapper engines to opt in.
    "runtime_layout",
    "execution",
    "auth",
}
REQUIRED_TOP_LEVEL_KEYS = TOP_LEVEL_KEYS - {"runtime_layout", "execution", "auth"}
MODEL_KEYS = {"required", "argv_suffix"}
BILLING_KEYS = {"basis", "provider"}
BILLING_BASES = {"flat-subscription", "metered", "local"}
NETWORK_KEYS = {"policy", "profile", "endpoints"}
NETWORK_OPTIONAL_KEYS = set()
PROBE_KEYS = {"type", "url_env", "timeout_s"}
RUNTIME_LAYOUT_KEYS = {"mode", "source", "root", "target", "entrypoint"}
EXECUTION_KEYS = {"structured_output", "output_format", "cancellation", "exit_codes"}
CANCELLATION_KEYS = {"signal", "grace_s"}
AUTH_KEYS = {"mode", "required", "marker"}
EXIT_CODE_KEYS = {"success", "auth", "runtime", "egress"}
PROVIDER_PROFILE_RE = re.compile(r"[a-z][a-z0-9-]{1,63}")
PROVIDER_CHOICES = frozenset({
    "anthropic-claude-code", "cursor", "google-gemini",
    "openrouter-via-opencode", "sentry-local",
})
PROFILE_CHOICES = frozenset({"anthropic", "cursor", "gemini", "openrouter", "sentry-local"})


class ManifestError(Exception):
    """A manifest file exists but violates the contract (exit code 2)."""


def has_control(value: str) -> bool:
    return any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in value)


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
    if not all(isinstance(item, str) and item and not has_control(item) for item in argv):
        raise ManifestError("argv elements must be nonempty strings")
    if len(set(argv)) != len(argv):
        raise ManifestError("argv must not contain duplicate elements")
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
    if not isinstance(suffix, list) or not all(isinstance(item, str) and item and not has_control(item) for item in suffix):
        raise ManifestError("model.argv_suffix must be a list of nonempty strings")
    if len(set(suffix)) != len(suffix):
        raise ManifestError("model.argv_suffix must not contain duplicate elements")
    for item in suffix:
        if item.startswith("{{") and item.endswith("}}") and item != "{{MODEL}}":
            raise ManifestError(f"model.argv_suffix contains an unknown placeholder {item!r}")
    if suffix.count("{{MODEL}}") > 1:
        raise ManifestError("{{MODEL}} may appear at most once in model.argv_suffix")


def validate_roles(roles: object) -> None:
    if not isinstance(roles, list) or not roles or len(roles) > 2:
        raise ManifestError("roles must be a nonempty list")
    if not all(isinstance(role, str) for role in roles):
        raise ManifestError("roles must contain only strings")
    if len(set(roles)) != len(roles):
        raise ManifestError("roles must not contain duplicates")
    if not all(role in ROLE_CHOICES for role in roles):
        raise ManifestError(f"roles must be a subset of {ROLE_CHOICES}")


def validate_billing(billing: object) -> dict:
    obj = require_object_keys(billing, BILLING_KEYS, "billing")
    if not isinstance(obj["basis"], str) or obj["basis"] not in BILLING_BASES:
        raise ManifestError(f"billing.basis must be one of {sorted(BILLING_BASES)}")
    if not isinstance(obj["provider"], str) or obj["provider"] not in PROVIDER_CHOICES:
        raise ManifestError("billing.provider is not a reviewed provider")
    return obj


def canonical_controller_root(value: str) -> Path:
    try:
        with pinned_directory(value) as (_, requested_value):
            requested = Path(requested_value)
        configured_value = os.environ.get("RECURSION_ROOT", "").strip()
        with pinned_directory(configured_value or Path(__file__).parent.parent) as (_, configured_path):
            configured = Path(configured_path)
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        raise ManifestError("controller root is unavailable") from exc
    if requested != configured:
        raise ManifestError("controller root is not the canonical controller root")
    return requested


def authenticated_file(root: Path, commit: str, relative: str) -> tuple[bytes, str]:
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        raise ManifestError("controller policy commit is not a full hexadecimal object id")
    if not isinstance(relative, str) or not relative:
        raise ManifestError("controller policy file path is invalid")
    pure = Path(relative)
    if pure.is_absolute() or "\\" in relative or any(part in {"", ".", ".."} for part in pure.parts):
        raise ManifestError(f"controller policy file is not a regular file: {relative}")
    path = root.joinpath(*pure.parts)
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", relative],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    tree = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-z", commit, "--", relative],
        capture_output=True, check=False,
    )
    committed = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{relative}"],
        capture_output=True, check=False,
    )
    rows = [row for row in tree.stdout.split(b"\0") if row]
    mode = rows[0].split(b" ", 1)[0] if len(rows) == 1 else b""
    try:
        live = read_bytes(path, label=f"controller policy file {relative}")
    except BoundaryError as exc:
        raise ManifestError(f"controller policy file is unreadable: {relative}") from exc
    if tracked.returncode or tree.returncode or committed.returncode or len(rows) != 1 \
            or mode not in {b"100644", b"100755"} or live != committed.stdout:
        raise ManifestError(f"controller policy file differs from controller_sha: {relative}")
    return committed.stdout, hashlib.sha256(committed.stdout).hexdigest()


def provider_profiles(controller_root: Path | None = None, controller_commit: str | None = None) -> dict:
    if (controller_root is None) != (controller_commit is None):
        raise ManifestError("controller policy provenance is incomplete")
    if controller_root is not None:
        raw, _ = authenticated_file(controller_root, controller_commit, "scripts/provider-egress-profiles.json")
    else:
        profile_path = Path(__file__).parent / "provider-egress-profiles.json"
        try:
            raw = read_bytes(profile_path, label="provider profile registry")
        except BoundaryError as exc:
            raise ManifestError("provider profile registry is unavailable") from exc
    try:
        profiles = decode_json(raw, "provider profile registry")["profiles"]
    except (BoundaryError, OSError, ValueError, KeyError, TypeError,
            OverflowError, RecursionError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError("provider profile registry is unavailable") from exc
    if not isinstance(profiles, dict):
        raise ManifestError("provider profile registry is invalid")
    return profiles


def validate_network(network: object, provider: str | None = None, billing_basis: str | None = None,
                     controller_root: Path | None = None, controller_commit: str | None = None) -> dict:
    if not isinstance(network, dict):
        raise ManifestError("network must be a JSON object")
    missing = NETWORK_KEYS - network.keys()
    extra = network.keys() - NETWORK_KEYS - NETWORK_OPTIONAL_KEYS
    if missing or extra:
        raise ManifestError("network has invalid fields")
    obj = network
    if not isinstance(obj["policy"], str) or obj["policy"] not in {"provider-only", "none"}:
        raise ManifestError('network.policy must be "provider-only" or "none"')
    endpoints = obj["endpoints"]
    if not isinstance(endpoints, list):
        raise ManifestError("network.endpoints must be a list of strings")
    for item in endpoints:
        if not isinstance(item, str) or not ENDPOINT_RE.fullmatch(item) or has_control(item):
            raise ManifestError(f"network.endpoints contains an invalid hostname {item!r}")
    if len(set(endpoints)) != len(endpoints):
        raise ManifestError("network.endpoints must not contain duplicates")
    profile = obj["profile"]
    if not isinstance(profile, str) or profile not in PROFILE_CHOICES \
            or not PROVIDER_PROFILE_RE.fullmatch(profile):
        raise ManifestError("network.profile is invalid")
    declared = provider_profiles(controller_root, controller_commit).get(profile)
    if not isinstance(declared, dict) or not isinstance(declared.get("endpoints"), list):
        raise ManifestError("network.profile is not a declared provider profile")
    declared_endpoints = declared["endpoints"]
    if any(not isinstance(item, str) or not ENDPOINT_RE.fullmatch(item) or has_control(item)
           for item in declared_endpoints) or len(set(declared_endpoints)) != len(declared_endpoints):
        raise ManifestError("declared provider profile endpoints are invalid")
    if provider is not None and declared.get("provider") != provider:
        raise ManifestError("network.profile provider does not match billing.provider")
    if sorted(declared["endpoints"]) != sorted(endpoints):
        raise ManifestError("network.endpoints do not match the declared provider profile")
    if obj["policy"] == "provider-only" and not endpoints:
        raise ManifestError("networked provider profiles must declare at least one endpoint")
    if obj["policy"] == "none" and (provider != "sentry-local" or profile != "sentry-local"
                                       or endpoints or billing_basis != "local"):
        raise ManifestError("network.policy none is reserved for the local sentry profile")
    allowlist = declared.get("env_allowlist")
    if not isinstance(allowlist, list) or not all(isinstance(v, str) for v in allowlist) \
            or len(set(allowlist)) != len(allowlist) \
            or any(not ENV_NAME_RE.fullmatch(v) for v in allowlist):
        raise ManifestError("provider profile env allowlist is invalid")
    return {"profile": profile, "provider": declared.get("provider"),
            "endpoints": list(declared["endpoints"]), "env_allowlist": list(allowlist)}


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


def validate_env_passthrough(names: object, allowed: list[str]) -> None:
    if not isinstance(names, list):
        raise ManifestError("env_passthrough must be a list of strings")
    if not all(isinstance(item, str) for item in names):
        raise ManifestError("env_passthrough must be a list of strings")
    if len(set(names)) != len(names):
        raise ManifestError("env_passthrough must not contain duplicates")
    for item in names:
        if not isinstance(item, str) or not ENV_NAME_RE.fullmatch(item):
            raise ManifestError(f"env_passthrough contains an invalid env var name {item!r}")
        if item not in allowed:
            raise ManifestError(f"env_passthrough name {item!r} is not allowlisted for this provider/profile")


def validate_relative_path(value: object, where: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str) or (not value and not allow_empty) \
            or value.startswith("/") or "\\" in value or ":" in value \
            or has_control(value) \
            or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ManifestError(f"{where} must be a relative path without . or .. components")


def validate_runtime_layout(layout: object) -> None:
    if layout is None:
        return
    if not isinstance(layout, dict):
        raise ManifestError("runtime_layout must be a JSON object or null")
    extra = layout.keys() - RUNTIME_LAYOUT_KEYS
    if extra:
        raise ManifestError(f"runtime_layout has unknown key(s): {', '.join(sorted(extra))}")
    if "mode" not in layout:
        raise ManifestError("runtime_layout missing required key(s): mode")
    obj = layout
    mode = obj["mode"]
    if not isinstance(mode, str) or mode not in {"executable-only", "sibling-tree"}:
        raise ManifestError('runtime_layout.mode must be "executable-only" or "sibling-tree"')
    if mode == "executable-only":
        if any(obj.get(key) is not None for key in ("source", "root", "target", "entrypoint")):
            raise ManifestError("executable-only runtime_layout may not declare tree paths")
        return
    source = obj.get("source", obj.get("root"))
    if source is None:
        raise ManifestError("sibling-tree runtime_layout requires source")
    if source != "executable-directory":
        raise ManifestError('runtime_layout.source must be "executable-directory"')
    if obj.get("source") is not None and obj.get("root") is not None and obj["source"] != obj["root"]:
        raise ManifestError("runtime_layout.source and root disagree")
    if obj.get("source") is not None and obj.get("root") is not None:
        raise ManifestError("runtime_layout may declare only one of source or root")
    validate_relative_path(obj.get("target", ".recursion-runtime"), "runtime_layout.target")
    validate_relative_path(obj.get("entrypoint"), "runtime_layout.entrypoint")


def validate_execution(execution: object) -> None:
    if execution is None:
        return
    obj = require_object_keys(execution, EXECUTION_KEYS, "execution")
    structured = obj["structured_output"]
    if not isinstance(structured, bool):
        raise ManifestError("execution.structured_output must be a boolean")
    output_format = obj["output_format"]
    if not isinstance(output_format, str) or output_format not in {"text", "json"}:
        raise ManifestError('execution.output_format must be "text" or "json"')
    cancel = require_object_keys(obj["cancellation"], CANCELLATION_KEYS, "execution.cancellation")
    if not isinstance(cancel["signal"], str) or cancel["signal"] not in {"TERM", "INT"}:
        raise ManifestError("execution.cancellation.signal must be TERM or INT")
    if not is_plain_int(cancel["grace_s"]) or not (1 <= cancel["grace_s"] <= 60):
        raise ManifestError("execution.cancellation.grace_s must be an integer in 1..60")
    codes = require_object_keys(obj["exit_codes"], EXIT_CODE_KEYS, "execution.exit_codes")
    seen: set[int] = set()
    for name, values in codes.items():
        if not isinstance(values, list) or not values or \
                not all(is_plain_int(value) and 0 <= value <= 255 for value in values):
            raise ManifestError(f"execution.exit_codes.{name} must be a nonempty list of 0..255 integers")
        if len(set(values)) != len(values) or seen.intersection(values):
            raise ManifestError("execution.exit_codes must be disjoint and contain no duplicates")
        seen.update(values)


def validate_auth(auth: object) -> None:
    if auth is None:
        return
    obj = require_object_keys(auth, AUTH_KEYS, "auth")
    if not isinstance(obj["mode"], str) or obj["mode"] not in {"none", "runner-home-marker"}:
        raise ManifestError('auth.mode must be "none" or "runner-home-marker"')
    if not is_plain_bool(obj["required"]):
        raise ManifestError("auth.required must be a boolean")
    if obj["mode"] == "runner-home-marker":
        validate_relative_path(obj["marker"], "auth.marker")
    elif obj["marker"] is not None:
        raise ManifestError("auth.marker is only valid for runner-home-marker auth")


def _validate_manifest(data: object, engine: str, *, controller_root: Path | None = None,
                       controller_commit: str | None = None) -> dict:
    if not isinstance(data, dict):
        raise ManifestError("manifest must be a JSON object")
    missing = REQUIRED_TOP_LEVEL_KEYS - data.keys()
    if missing:
        raise ManifestError(f"manifest missing required key(s): {', '.join(sorted(missing))}")
    extra = data.keys() - TOP_LEVEL_KEYS
    if extra:
        raise ManifestError(f"manifest has unknown key(s): {', '.join(sorted(extra))}")
    obj = data
    if not is_plain_int(obj["schema_version"]) or obj["schema_version"] != 1:
        raise ManifestError("schema_version must be 1")
    name = obj["name"]
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise ManifestError("name must match ^[a-z][a-z0-9-]{1,31}$")
    if name != engine:
        raise ManifestError(f"name {name!r} does not match manifest filename stem {engine!r}")
    if name in BUILTIN_ENGINES:
        raise ManifestError(f"name {name!r} collides with a builtin engine")
    if not isinstance(obj["description"], str) or not obj["description"] or has_control(obj["description"]):
        raise ManifestError("description must be a nonempty string")
    executable = obj["executable"]
    if not isinstance(executable, str) or not NAME_RE.fullmatch(executable):
        raise ManifestError("executable must be a bare basename matching ^[a-z][a-z0-9-]{1,31}$")
    validate_argv(obj["argv"])
    validate_model(obj["model"])
    validate_roles(obj["roles"])
    billing = validate_billing(obj["billing"])
    network = validate_network(obj["network"], billing["provider"], billing["basis"],
                               controller_root, controller_commit)
    validate_probe(obj["availability_probe"])
    cap = obj["concurrency_cap"]
    if cap is not None and not (is_plain_int(cap) and cap >= 1):
        raise ManifestError("concurrency_cap must be null or an integer >= 1")
    validate_env_passthrough(obj["env_passthrough"], network["env_allowlist"])
    validate_runtime_layout(obj.get("runtime_layout"))
    if "execution" in obj and obj["execution"] is None:
        raise ManifestError("execution must be an object when present")
    if "auth" in obj and obj["auth"] is None:
        raise ManifestError("auth must be an object when present")
    validate_execution(obj.get("execution"))
    validate_auth(obj.get("auth"))
    return obj


def validate_manifest(data: object, engine: str, *, controller_root: Path | None = None,
                      controller_commit: str | None = None) -> dict:
    """Expose one typed failure domain for all malformed manifest inputs."""
    try:
        return _validate_manifest(data, engine, controller_root=controller_root,
                                  controller_commit=controller_commit)
    except ManifestError:
        raise
    except (AttributeError, IndexError, KeyError, TypeError, ValueError,
            OverflowError, RecursionError, UnicodeDecodeError, OSError) as exc:
        raise ManifestError("manifest contains invalid field types") from exc


def manifest_dir() -> Path:
    override = os.environ.get("RECURSION_ENGINE_DIR", "").strip()
    if override:
        return Path(override)
    return Path(__file__).parent / "engines"


def manifest_path(engine: str) -> Path:
    return manifest_dir() / f"{engine}.json"


def load_manifest(path: Path, engine: str, *, controller_root: Path | None = None,
                  controller_commit: str | None = None) -> tuple[dict, dict[str, str]]:
    provenance: dict[str, str] = {}
    try:
        if controller_root is not None:
            relative = f"scripts/engines/{engine}.json"
            expected = Path(os.path.abspath(str(controller_root / relative)))
            if Path(os.path.abspath(str(path))) != expected:
                raise ManifestError("manifest path is not under the canonical controller root")
            raw_bytes, manifest_digest = authenticated_file(controller_root, controller_commit, relative)
            provenance[relative] = manifest_digest
            raw = raw_bytes.decode("utf-8")
        else:
            raw = read_bytes(path, label=f"manifest {path}").decode("utf-8")
    except (BoundaryError, OSError, UnicodeDecodeError, ValueError, TypeError,
            OverflowError, RecursionError) as exc:
        raise ManifestError(f"could not read manifest {path}: {exc}") from exc
    try:
        data = decode_json(raw, f"manifest {path}")
    except (BoundaryError, json.JSONDecodeError, ValueError, TypeError,
            OverflowError, RecursionError, UnicodeDecodeError) as exc:
        raise ManifestError(f"manifest {path} is not valid JSON: {exc}") from exc
    if controller_root is not None:
        _, profile_digest = authenticated_file(controller_root, controller_commit,
                                               "scripts/provider-egress-profiles.json")
        provenance["scripts/provider-egress-profiles.json"] = profile_digest
    return validate_manifest(data, engine, controller_root=controller_root, controller_commit=controller_commit), provenance


def enabled_env_name(engine: str) -> str:
    return "RECURSION_ENGINE_" + engine.upper().replace("-", "_") + "_ENABLED"


def build_plan(data: dict, provenance: dict[str, str] | None = None,
               controller_root: Path | None = None, controller_commit: str | None = None) -> dict:
    if provenance is None or controller_root is None or controller_commit is None:
        raise ManifestError("authenticated controller provenance is required to build an execution plan")
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
    if "profile" in data["network"]:
        plan["network"] = {
            "policy": data["network"]["policy"],
            "profile": data["network"]["profile"],
            "endpoints": list(data["network"]["endpoints"]),
        }
    plan["authority"] = {
        "controller_repository": str(controller_root),
        "controller_sha": controller_commit,
        "policy_files": dict(sorted(provenance.items())),
    }
    if "runtime_layout" in data:
        layout = data["runtime_layout"]
        if layout is None or layout["mode"] == "executable-only":
            plan["runtime_layout"] = {"mode": "executable-only"}
        else:
            plan["runtime_layout"] = {
                "mode": "sibling-tree",
                "source": layout.get("source", layout.get("root")),
                "target": layout.get("target", ".recursion-runtime"),
                "entrypoint": layout["entrypoint"],
            }
    for key in ("execution", "auth"):
        if key in data:
            plan[key] = data[key]
    return plan


def write_plan_atomically(plan: dict, out_path: Path) -> None:
    try:
        encoded = (json.dumps(plan, indent=2, sort_keys=False,
                              allow_nan=False) + "\n").encode("utf-8")
        atomic_write(out_path, encoded, replace=True, mode=0o600,
                     label="engine execution plan")
    except BoundaryError:
        raise
    except (OSError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ManifestError("engine execution plan could not be published") from exc


def parse_args(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROG)
    parser.add_argument("engine")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--role", choices=ROLE_CHOICES)
    parser.add_argument("--emit-plan", metavar="PATH")
    parser.add_argument("--controller-root", metavar="PATH")
    parser.add_argument("--controller-commit", metavar="SHA")
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
        diag(f"invalid engine name {engine!r}: must match ^[a-z][a-z0-9-]{{1,31}}$")
        return 2
    if engine in BUILTIN_ENGINES:
        diag(f"{engine!r} is a builtin engine, not a plugin")
        return 2

    if (args.controller_root is None) != (args.controller_commit is None):
        diag("--controller-root and --controller-commit must be supplied together")
        return 2
    if args.controller_commit is not None and not COMMIT_RE.fullmatch(args.controller_commit):
        diag("--controller-commit must be a full hexadecimal object id")
        return 2
    if not args.validate and args.controller_root is None:
        diag("--controller-root and --controller-commit are required to emit an execution plan")
        return 2
    controller_root = None
    if args.controller_root is not None:
        try:
            controller_root = canonical_controller_root(args.controller_root)
            head = subprocess.run(
                ["git", "-C", str(controller_root), "rev-parse", "--verify", "HEAD"],
                capture_output=True, text=True, check=False,
            )
            if head.returncode or head.stdout.strip() != args.controller_commit:
                raise ManifestError("controller HEAD is not the exact immutable controller commit")
        except (ManifestError, OSError, ValueError, TypeError, OverflowError,
                RecursionError, UnicodeDecodeError) as exc:
            diag(str(exc))
            return 2
    path = manifest_path(engine) if controller_root is None else controller_root / "scripts" / "engines" / f"{engine}.json"
    try:
        present = read_bytes(path, label=f"manifest {path}", optional=True)
    except (BoundaryError, OSError, ValueError, TypeError, OverflowError,
            RecursionError, UnicodeDecodeError) as exc:
        diag(f"could not inspect manifest {path}: {exc}")
        return 2
    if present is None:
        diag(f"manifest not found: {path}")
        return 3

    try:
        data, provenance = load_manifest(path, engine, controller_root=controller_root,
                                          controller_commit=args.controller_commit)
    except ManifestError as exc:
        diag(str(exc))
        return 2
    except (AttributeError, IndexError, KeyError, TypeError, ValueError,
            OverflowError, RecursionError, UnicodeDecodeError, OSError) as exc:
        diag(f"invalid manifest {path}: {exc}")
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

    plan = build_plan(data, provenance, controller_root, args.controller_commit)
    out_path = Path(args.emit_plan)
    try:
        write_plan_atomically(plan, out_path)
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        diag(f"failed to write plan to {out_path}: {exc}")
        return 2

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FirstPartyImportError as exc:
        diag(f"first-party import failed: {exc}")
        raise SystemExit(95)
    except (ManifestError, BoundaryError, OSError, UnicodeDecodeError,
            json.JSONDecodeError, ValueError, TypeError, OverflowError,
            RecursionError, KeyError, IndexError, AttributeError) as exc:
        diag(f"invalid input: {exc}")
        raise SystemExit(2)

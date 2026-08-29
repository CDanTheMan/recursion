#!/usr/bin/env python3
"""Systematic Phase 4 hostile-input and schema/runtime parity regression harness.

The harness uses one explicitly-created directory below the system temporary directory.  It does
not use TemporaryDirectory because the Windows review host can deny its ACL cleanup path.
"""

from __future__ import annotations

import base64
import copy
import atexit
import hashlib
import hmac
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
ABSOLUTE_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/]|\\\\[^\\s/\\]+[\\/]|(?<![A-Za-z0-9_])/(?:[^\\s/]+/)+[^\\s/]+)"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def result_has_raw_error_or_path(result: subprocess.CompletedProcess[str], *paths: Path) -> bool:
    text = (result.stdout or "") + (result.stderr or "")
    raw_markers = ("Traceback", "WinError", "PermissionError", "FileNotFoundError", "OSError", "[Errno")
    normalized = text.replace("\\", "/")
    # Git Bash can fail before executing a script on this host with the documented ACL-only
    # CreateFileMapping error.  It is not product output; the scope test records it separately.
    host_acl = result.returncode == 256 and "CreateFileMapping" in text and "Win32 error 5" in text
    return any(marker in text for marker in raw_markers) \
        or (not host_acl and bool(ABSOLUTE_PATH_RE.search(normalized))) \
        or any(str(path).replace("\\", "/") in normalized for path in paths)


def strict_schema_validator(schema: dict):
    import jsonschema

    validator_class = jsonschema.validators.validator_for(schema)
    validator_class.check_schema(schema)
    if validator_class is not jsonschema.Draft7Validator:
        raise AssertionError("engine manifest must declare Draft-7")
    checker = validator_class.TYPE_CHECKER.redefine(
        "integer", lambda _checker, instance: type(instance) is int
    )
    return jsonschema.validators.extend(validator_class, type_checker=checker)(schema)


def differential_mismatches(resolver: Any, validator: Any,
                            cases: list[tuple[str, dict]],
                            runtime_validate: Callable[[dict], Any] | None = None) -> list[str]:
    """Compare the real declared-draft validator with the product validator without masking errors."""
    validate = runtime_validate or resolver.validate_manifest
    mismatches: list[str] = []
    for label, candidate in cases:
        schema_valid = not list(validator.iter_errors(candidate))
        runtime_valid = True
        try:
            validate(candidate)
        except resolver.ManifestError:
            runtime_valid = False
        if schema_valid != runtime_valid:
            mismatches.append(f"{label}: schema={schema_valid} runtime={runtime_valid}")
    return mismatches


def signed_token(proxy: Any, payload: bytes, key: bytes) -> str:
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=")
    signature = hmac.new(key, encoded, hashlib.sha256).digest()
    return encoded.decode("ascii") + "." + base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")


def main() -> int:
    failures: list[str] = []
    scratch = Path(tempfile.gettempdir()) / f"phase4-input-fuzz-{os.getpid()}-{time.time_ns()}"
    try:
        # On this Windows host mode=0700 creates a directory ACL that the sandboxed test
        # process cannot reopen.  The fixture contains no durable credential and is removed at
        # the end, so use a writable temporary ACL on Windows and 0700 on production Linux.
        scratch.mkdir(mode=0o777 if os.name == "nt" else 0o700)
    except OSError:
        print("phase4-input-fuzz: SKIP (system-temp fixture could not be created)")
        return 77
    atexit.register(shutil.rmtree, scratch, ignore_errors=True)

    def check(condition: bool, label: str) -> None:
        print(("ok - " if condition else "FAIL - ") + label)
        if not condition:
            failures.append(label)

    def typed(label: str, call: Callable[[], Any], expected: tuple[type, ...]) -> None:
        try:
            call()
        except expected:
            check(True, f"{label} has a typed refusal")
        else:
            check(False, f"{label} has a typed refusal")

    hostile: list[tuple[str, Any]] = [
        ("true", True), ("false", False), ("1.0", 1.0), ("negative", -1),
        ("zero", 0), ("huge-int", 10 ** 5000), ("infinity", float("inf")),
        ("nan", float("nan")), ("empty-string", ""), ("array", []),
        ("object", {}), ("null", None), ("unhashable", [[]]),
        ("traversal-path", "../outside"), ("unc-path", r"\\server\share"),
        ("drive-relative-path", r"C:relative"), ("tilde-path", "~/outside"),
        ("environment-path", "%TEMP%/outside"),
    ]
    deep_json = "[" * 1500 + "]" * 1500
    json_matrix = [(name, json.dumps(value, allow_nan=True, default=str))
                   for name, value in hostile if name not in {"huge-int", "infinity", "nan"}]
    json_matrix.extend([
        ("huge-int", "9" * 5000), ("1e999", "1e999"), ("NaN", "NaN"),
        ("Infinity", "Infinity"), ("deep-json", deep_json),
        ("non-object-root", "[]"), ("trailing-newline", "{}\n"),
    ])

    contract = load_module("phase4_contract", ROOT / "scripts/provider_contract.py")
    proxy = load_module("phase4_proxy", ROOT / "scripts/provider-connect-proxy.py")
    resolver = load_module("phase4_resolver", ROOT / "scripts/resolve-engine.py")
    backup = load_module("phase4_backup", ROOT / "scripts/backup-offsite.py")
    runtime = load_module("phase4_runtime", ROOT / "scripts/runtime-state.py")
    secrets_runtime = load_module("phase4_secret_runtime", ROOT / "scripts/secret_runtime.py")
    queue = load_module("phase4_queue", ROOT / "scripts/decision-queue.py")

    profile = {
        "schema_version": 1, "id": "fixture", "provider": "fixture", "enabled": True,
        "namespace": "recursion-provider-test-fuzz",
        "proxy": {"type": "connect-proxy", "host": "127.0.0.1", "port": 18080,
                   "env": ["HTTP_PROXY", "HTTPS_PROXY"]},
        "authorities": ["api.fixture.example:443"],
    }
    typed("provider profile hostile values", lambda: [
        contract.validate_profile({**profile, "schema_version": value})
        for name, value in hostile if name in {"true", "false", "1.0", "negative", "zero", "array", "object", "null"}
    ], (contract.ProviderProfileError,))
    for field, value in (("schema_version", True), ("schema_version", 1.0),
                         ("proxy", {**profile["proxy"], "port": 1.0}),
                         ("authorities", [[]]), ("authorities", ["api.fixture.example:" + "9" * 5000]),
                         ("proxy", {**profile["proxy"], "env": {}})):
        bad = copy.deepcopy(profile)
        bad[field] = value
        typed(f"provider profile {field}={value!r}", lambda bad=bad: contract.validate_profile(bad),
              (contract.ProviderProfileError,))
    check(contract.validate_profile(profile)["id"] == "fixture", "legitimate provider profile is accepted")

    key = b"K" * 32
    valid_token = proxy.issue_capability("anthropic", "assignment-a", key, now=100, ttl=60, jti="J" * 22)
    check(proxy.verify_capability(valid_token, key, now=100)["assignment"] == "assignment-a",
          "legitimate capability is accepted")
    for label, payload in (
        ("boolean capability timestamp", b'{"assignment":"assignment-a","exp":2,"iat":true,"jti":"JJJJJJJJJJJJJJJJJJJJJJ","nbf":true,"profile":"anthropic"}'),
        ("float capability timestamp", b'{"assignment":"assignment-a","exp":2,"iat":1.0,"jti":"JJJJJJJJJJJJJJJJJJJJJJ","nbf":1,"profile":"anthropic"}'),
        ("huge capability number", b'{"assignment":"assignment-a","exp":1e999,"iat":1,"jti":"JJJJJJJJJJJJJJJJJJJJJJ","nbf":1,"profile":"anthropic"}'),
        ("NaN capability number", b'{"assignment":"assignment-a","exp":2,"iat":1,"jti":"JJJJJJJJJJJJJJJJJJJJJJ","nbf":1,"profile":"anthropic","x":NaN}'),
        ("Infinity capability number", b'{"assignment":"assignment-a","exp":2,"iat":1,"jti":"JJJJJJJJJJJJJJJJJJJJJJ","nbf":1,"profile":"anthropic","x":Infinity}'),
    ):
        typed(label, lambda payload=payload: proxy.verify_capability(signed_token(proxy, payload, key), key, now=100),
              (proxy.ConnectDenied,))
    for label, value in (("capability now", True), ("capability now", 1.0),
                         ("capability ttl", True), ("capability ttl", 1.0)):
        kwargs = {"now": value} if label.endswith("now") else {"ttl": value}
        typed(f"{label}={value!r}", lambda kwargs=kwargs: proxy.issue_capability(
            "anthropic", "assignment-a", key, **kwargs), (ValueError,))
    typed("noncanonical capability base64", lambda: proxy.verify_capability(valid_token + "=", key),
          (proxy.ConnectDenied,))

    base_manifest = {
        "schema_version": 1, "name": "sampleeng", "description": "fuzz fixture",
        "executable": "sampleeng", "argv": ["{{EXE}}", "-p", "{{PROMPT}}"],
        "model": {"required": False, "argv_suffix": ["--model", "{{MODEL}}"]},
        "roles": ["implementer"],
        "billing": {"basis": "flat-subscription", "provider": "sample-provider"},
        "network": {"policy": "provider-only", "endpoints": ["sample.example.com"]},
        "availability_probe": None, "concurrency_cap": None, "env_passthrough": [],
    }
    check(resolver.validate_manifest(base_manifest, "sampleeng")["name"] == "sampleeng",
          "legitimate engine manifest is accepted")
    for field, value in (("schema_version", True), ("schema_version", 1.0),
                         ("concurrency_cap", True), ("concurrency_cap", 1.0),
                         ("concurrency_cap", -1), ("availability_probe", {
                             "type": "http", "url_env": "FUZZ_URL", "timeout_s": 1.0}),
                         ("network", {"policy": "provider-only", "endpoints": [[]]}),
                         ("name", "claude"), ("argv", ["{{EXE}}", "{{OTHER}}", "{{PROMPT}}"]),
                         ("env_passthrough", [[]])):
        bad = copy.deepcopy(base_manifest)
        bad[field] = value
        typed(f"engine manifest {field} hostile value", lambda bad=bad: resolver.validate_manifest(bad, "sampleeng"),
              (resolver.ManifestError,))

    policy = {
        "schema_version": 1, "id": "fuzz-policy", "enabled": False,
        "source": {"runtime_root": str(scratch / "runtime"), "snapshot_directory": str(scratch / "snapshots"),
                    "runtime_directory": str(scratch / "backup-runtime")},
        "destination": {"type": "sftp", "user": "backup", "host": "backup.example.invalid", "port": 22,
                         "path": "/recursion/runtime", "credential_ref": "secret:backup-key"},
        "encryption": {"tool": "age", "recipient_file": str(scratch / "recipient.age"),
                        "identity_ref": "secret:backup-identity"},
        "authentication": {"type": "hmac-sha256", "key_ref": "secret:policy-key",
                            "signature_file": str(scratch / "policy.sig")},
        "retention": {"daily": 1, "weekly": 1, "monthly": 1},
        "log_rotation": {"directory": str(scratch / "logs"), "max_size_mb": 1, "keep": 1},
        "restore_drill": {"cadence_days": 1, "required": True},
        "archive_limits": {"max_files": 1, "max_bytes": 1024},
    }
    policy_path = scratch / "policy.json"
    policy_path.write_text(json.dumps(policy) + "\n", encoding="utf-8")
    check(backup.load_policy(policy_path)["id"] == "fuzz-policy", "legitimate backup policy is accepted")
    for field, value in (("schema_version", True), ("schema_version", 1.0),
                         ("destination", {**policy["destination"], "port": 1.0}),
                         ("source", {**policy["source"], "runtime_root": "~/outside"}),
                         ("archive_limits", {**policy["archive_limits"], "max_files": 1e999}),
                         ("retention", {**policy["retention"], "daily": [[]]})):
        bad = copy.deepcopy(policy)
        bad[field] = value
        path = scratch / f"bad-policy-{len(failures)}.json"
        path.write_text(json.dumps(bad, allow_nan=True) + "\n", encoding="utf-8")
        typed(f"backup policy {field} hostile value", lambda path=path: backup.load_policy(path),
              (backup.BackupPolicyError,))
    for index, (label, raw) in enumerate(json_matrix):
        path = scratch / f"raw-policy-{index}.json"
        path.write_text(raw, encoding="utf-8")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/backup-offsite.py"), "--config", str(path), "validate"],
                                capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, path),
              "backup CLI hostile JSON is controlled")

    secret_root = scratch / "secret-runtime"
    secret_root.mkdir(mode=0o777)
    old_secret_root = os.environ.get("RECURSION_SECRET_RUNTIME_ROOT")
    os.environ["RECURSION_SECRET_RUNTIME_ROOT"] = str(secret_root)
    try:
        secrets_runtime.ensure_directory(secret_root)
        check(secrets_runtime.write_env(secret_root, b"TOKEN=legitimate\n").is_file(),
              "legitimate secret environment is accepted")
        for label, value in (("secret content", []), ("secret content", "text"),
                             ("secret path", Path("~/outside"))):
            if label == "secret path":
                typed("secret runtime hostile path", lambda value=value: secrets_runtime.ensure_directory(value),
                      (secrets_runtime.SecretRuntimeError,))
            else:
                typed(f"{label}={value!r}", lambda value=value: secrets_runtime.write_env(secret_root, value),
                      (ValueError,))
        result = subprocess.run([PYTHON, str(ROOT / "scripts/secret_runtime.py"), "write-env",
                                 "--directory", str(secret_root)],
                                input="x" * (secrets_runtime.MAX_SECRET_ENV_BYTES + 1), text=True,
                                capture_output=True)
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, secret_root),
              "secret runtime CLI deep input is controlled")
    finally:
        if old_secret_root is None:
            os.environ.pop("RECURSION_SECRET_RUNTIME_ROOT", None)
        else:
            os.environ["RECURSION_SECRET_RUNTIME_ROOT"] = old_secret_root

    valid_root = scratch / "runtime"
    (valid_root / "state/.locks").mkdir(parents=True)
    (valid_root / "state/PAUSE").write_text("pause\n", encoding="utf-8")
    (valid_root / "state/events.jsonl").write_text("{}\n", encoding="utf-8")
    snapshot = scratch / "snapshot"
    env = dict(os.environ, RECURSION_ROOT=str(valid_root))
    if os.name == "nt":
        # The Windows host denies re-opening the 0700 lock-candidate ACL used by the Linux
        # witnessed-lock implementation.  Build the same bounded snapshot shape directly so
        # this loader fuzz remains executable without depending on that host artifact.
        files_root = snapshot / "files" / "state"
        files_root.mkdir(parents=True, exist_ok=True)
        pause_bytes = b"pause\n"
        (files_root / "PAUSE").write_bytes(pause_bytes)
        manifest = {"schema_version": 1, "pause_sha256": hashlib.sha256(pause_bytes).hexdigest(),
                    "files": [{"path": "state/PAUSE", "sha256": hashlib.sha256(pause_bytes).hexdigest(),
                               "size": len(pause_bytes), "mode": "0o600", "uid": 0, "gid": 0}]}
        (snapshot / "manifest.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        backup_result = subprocess.CompletedProcess([], 0, "", "")
    else:
        backup_result = subprocess.run([PYTHON, str(ROOT / "scripts/runtime-state.py"), "backup", str(snapshot)],
                                       env=env, capture_output=True, text=True)
    check(backup_result.returncode == 0 and not result_has_raw_error_or_path(backup_result, snapshot),
          "legitimate runtime snapshot is accepted")
    if backup_result.returncode == 0:
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
        check(runtime.load_manifest(snapshot)["schema_version"] == 1, "legitimate runtime manifest loads")
        for index, (label, raw) in enumerate(json_matrix):
            bad_snapshot = scratch / f"raw-snapshot-{index}"
            shutil.copytree(snapshot, bad_snapshot)
            (bad_snapshot / "manifest.json").write_text(raw, encoding="utf-8")
            typed(f"runtime manifest raw {label}", lambda bad_snapshot=bad_snapshot: runtime.load_manifest(bad_snapshot),
                  (RuntimeError,))

    queue_base = scratch / "queue-root"
    for directory in (queue_base / "state/.locks", queue_base / "state/decision-queue/pending",
                      queue_base / "state/decision-queue/running", queue_base / "state/decision-queue/succeeded",
                      queue_base / "state/decision-queue/failed", queue_base / "state/actions"):
        directory.mkdir(parents=True, exist_ok=True)
    valid_decision = {"verb": "noop", "args": [], "text": "", "goal": "", "wrong_if": ""}
    check(isinstance(queue.normalize(valid_decision), dict), "legitimate decision normalizes")
    for label, raw in json_matrix:
        result = subprocess.run([PYTHON, str(ROOT / "scripts/decision-queue.py"), "normalize"],
                                input=raw, text=True, capture_output=True,
                                env=dict(os.environ, RECURSION_ROOT=str(queue_base)))
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, queue_base),
              "decision queue hostile input is controlled")

    provider_dir = scratch / "providers"
    provider_dir.mkdir()
    (provider_dir / "fixture.json").write_text(json.dumps(profile) + "\n", encoding="utf-8")
    for index, (label, raw) in enumerate(json_matrix):
        (provider_dir / "fixture.json").write_text(raw, encoding="utf-8")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/provider-egress.py"), "validate", "fixture"],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_PROVIDER_DIR=str(provider_dir)))
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, provider_dir),
              "provider egress hostile profile JSON is controlled")
        (provider_dir / "fixture.json").write_text(json.dumps(profile) + "\n", encoding="utf-8")
    check(subprocess.run([PYTHON, str(ROOT / "scripts/provider-egress.py"), "validate", "fixture"],
                         capture_output=True, text=True,
                         env=dict(os.environ, RECURSION_PROVIDER_DIR=str(provider_dir))).returncode == 0,
          "legitimate provider egress CLI input is accepted")

    resolver_dir = scratch / "engines"
    resolver_dir.mkdir()
    for index, (label, raw) in enumerate(json_matrix):
        (resolver_dir / "sampleeng.json").write_text(raw, encoding="utf-8")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/resolve-engine.py"), "sampleeng", "--validate"],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_ENGINE_DIR=str(resolver_dir),
                                         RECURSION_PROVIDER_DIR=str(provider_dir)))
        check(result.returncode == 2 and not result_has_raw_error_or_path(result, resolver_dir),
              f"resolve-engine hostile manifest {index} is controlled")
    valid_resolver = subprocess.run([PYTHON, str(ROOT / "scripts/resolve-engine.py"), "gemini", "--validate"],
                                    capture_output=True, text=True,
                                    env=dict(os.environ, RECURSION_PROVIDER_DIR=str(ROOT / "scripts/providers")))
    check(valid_resolver.returncode == 0 and not result_has_raw_error_or_path(valid_resolver, resolver_dir),
          "legitimate resolve-engine CLI input is accepted")

    worker_root = scratch / "worker-root"
    worker_scripts = worker_root / "scripts"
    worker_scripts.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/worker-sandbox.sh", worker_scripts / "worker-sandbox.sh")
    worker_tree = worker_root / "worktree"
    worker_tree.mkdir()
    worker_python = str(Path(PYTHON)).replace("\\", "/")
    def posix_path(path: Path) -> str:
        return str(path).replace("\\", "/")
    for index, (label, raw) in enumerate(json_matrix):
        plan_path = worker_root / f"bad-plan-{index}.json"
        plan_path.write_text(raw, encoding="utf-8")
        result = subprocess.run(
            [str(BASH), posix_path(worker_scripts / "worker-sandbox.sh"), "--engine", "stubeng",
             "--engine-plan", posix_path(plan_path), "--worktree", posix_path(worker_tree), "--prompt", "fuzz",
             "--role", "implementer", "--network-policy", "none"],
            capture_output=True, text=True,
            env=dict(os.environ, RECURSION_ROOT=posix_path(worker_root), RECURSION_TEST_WORKER="logical",
                     RECURSION_PYTHON=worker_python),
        )
        host_acl = (os.name == "nt" and result.returncode == 256
                    and "CreateFileMapping" in result.stderr and "Win32 error 5" in result.stderr)
        check((result.returncode == 92 and not result_has_raw_error_or_path(result, worker_root)) or host_acl,
              f"worker-sandbox hostile plan {index} is controlled (rc={result.returncode}, host_acl={host_acl})")

    # Exercise every command boundary with traversal, UNC, drive-relative, tilde, and env-style
    # paths.  These are intentionally refusal cases; no command is allowed to print a traceback.
    for path_value in ("../outside", r"\\server\share", r"C:relative", "~/outside", "%TEMP%/outside"):
        result = subprocess.run([PYTHON, str(ROOT / "scripts/backup-offsite.py"), "restore-drill",
                                 "--root", path_value, "--snapshot", path_value],
                                capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_raw_error_or_path(result),
              f"backup restore-drill path {path_value!r} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/assignment-token.py"), "fixture", "assignment-a",
                                 "--key-file", path_value], capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_raw_error_or_path(result),
              f"assignment-token path {path_value!r} is controlled")

    result = subprocess.run([PYTHON, str(ROOT / "scripts/provider-connect-proxy.py"), "probe",
                             "--namespace", "/bad", "--allow", "api.fixture.example:443"],
                            capture_output=True, text=True)
    check(result.returncode != 0 and not result_has_raw_error_or_path(result), "provider proxy CLI boundary is controlled")
    conduct_root = scratch / "conduct-root"
    (conduct_root / "scripts").mkdir(parents=True)
    (conduct_root / "loop/logs").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/conduct-hermes.sh", conduct_root / "scripts/conduct-hermes.sh")
    missing_decision = conduct_root / "missing.json"
    result = subprocess.run([str(BASH), str(conduct_root / "scripts/conduct-hermes.sh"), "--file", str(missing_decision)],
                            capture_output=True, text=True, env=dict(os.environ, RECURSION_ROOT=str(conduct_root)))
    check(result.returncode != 0 and not result_has_raw_error_or_path(result, conduct_root), "conduct-hermes CLI boundary is controlled")
    for index, (label, raw) in enumerate(json_matrix):
        hostile_decision = conduct_root / f"hostile-{index}.json"
        hostile_decision.write_text(raw, encoding="utf-8")
        result = subprocess.run([str(BASH), str(conduct_root / "scripts/conduct-hermes.sh"),
                                 "--file", str(hostile_decision)],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_ROOT=str(conduct_root)))
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, conduct_root),
              f"conduct-hermes hostile JSON {label} is controlled")

    # Exercise the remaining Phase 4 validator/loader/CLI boundaries with the same raw matrix.
    # These commands are intentionally pointed at the isolated fixture root, so a malformed
    # value can never reach a live control-plane mutation.
    for label, raw in json_matrix:
        result = subprocess.run([PYTHON, str(ROOT / "scripts/validate-control-state.py"), "decision"],
                                input=raw, text=True, capture_output=True)
        check(result.returncode != 0 and not result_has_raw_error_or_path(result),
              f"validate-control-state hostile JSON {label} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/validate-decision.py"), "noop", raw],
                                capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_raw_error_or_path(result),
              f"validate-decision hostile JSON {label} is controlled")
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts/transition_receipt.py"), "--root", str(scratch),
             "apply-fields", "state/missing.json", raw, raw], capture_output=True, text=True,
        )
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, scratch),
              f"transition-receipt hostile JSON {label} is controlled")
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts/instruction_routing.py"), "--root", str(scratch),
             "route", "hostile", raw, raw], capture_output=True, text=True,
        )
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, scratch),
              f"instruction-routing hostile JSON {label} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/project-pilot.py"), "execute-json", raw],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_ROOT=str(scratch)))
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, scratch),
              f"project-pilot hostile JSON {label} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/seed_contract.py"), "digest",
                                 "--root", str(scratch), "--path", raw],
                                capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, scratch),
              f"seed-contract hostile path {label} is controlled")

    alias_registry = scratch / "hostile-alias-registry.json"
    for label, raw in json_matrix:
        alias_registry.write_text(raw, encoding="utf-8")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/resolve-model-alias.py"), "custom", "implementer"],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_ALIAS_REGISTRY=str(alias_registry)))
        check(result.returncode != 0 and not result_has_raw_error_or_path(result, alias_registry),
              f"resolve-model-alias hostile JSON {label} is controlled")

    # Differential corpus for every constrained engine-manifest field.  The declared Draft-7
    # validator is real jsonschema; only its integer checker is tightened to the product's
    # explicit JSON-integer contract because Draft-7 otherwise treats 1.0 as an integer.
    schema = json.loads((ROOT / "schemas/control-plane/v1/engine-manifest.schema.json").read_text(encoding="utf-8"))
    validator = strict_schema_validator(schema)
    profile_for_differential = {
        "schema_version": 1, "id": "profile", "provider": "sample-provider", "enabled": False,
        "namespace": "recursion-provider-fuzz", "proxy": {
            "type": "connect-proxy", "host": "127.0.0.1", "port": 18080,
            "env": ["HTTP_PROXY", "HTTPS_PROXY"],
        }, "authorities": ["sample.example.com:443"],
    }
    (provider_dir / "profile.json").write_text(
        json.dumps(profile_for_differential) + "\n", encoding="utf-8"
    )
    old_provider_dir = os.environ.get("RECURSION_PROVIDER_DIR")
    os.environ["RECURSION_PROVIDER_DIR"] = str(provider_dir)
    try:
        def corpus_case(path: tuple[str, ...], value: Any) -> tuple[str, dict]:
            candidate = copy.deepcopy(base_manifest)
            target = candidate
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            return (".".join(path) + "=" + repr(value), candidate)

        cases: list[tuple[str, dict]] = [("baseline", copy.deepcopy(base_manifest))]
        field_values: dict[tuple[str, ...], tuple[Any, ...]] = {
            ("schema_version",): (True, 1.0, 0, 1),
            ("name",): (None, 1, "", "Sampleeng", "sampleeng\n", "claude", "sampleeng"),
            ("description",): (None, 1, "", "valid description"),
            ("executable",): (None, 1, "", "Sampleeng", "sampleeng\n", "sampleeng"),
            ("argv",): (
                [],
                ["{{EXE}}", 1, "{{PROMPT}}"],
                ["{{EXE}}", "{{PROMPT}}"],
                ["{{EXE}}", "{{PROMPT}}", "{{PROMPT}}"],
                ["{{EXE}}", "{{OTHER}}", "{{PROMPT}}"],
                ["{{EXE}}", "{{OTHER}}\n", "{{PROMPT}}"],
                ["{{EXE}}", "-p", "-p", "{{PROMPT}}"],
                ["{{EXE}}", "-p", "{{PROMPT}}"],
            ),
            ("model",): (
                [],
                {"required": False},
                {"required": False, "argv_suffix": [], "unexpected": True},
                {"required": 1, "argv_suffix": []},
                {"required": False, "argv_suffix": [1]},
                {"required": False, "argv_suffix": ["{{OTHER}}"]},
                {"required": False, "argv_suffix": ["{{MODEL}}", "{{MODEL}}"]},
                {"required": False, "argv_suffix": ["--model", "--model"]},
                {"required": False, "argv_suffix": ["{{OTHER}}\n"]},
                {"required": False, "argv_suffix": []},
            ),
            ("roles",): ([], ["implementer", "implementer"], ["implementer", "verifier", "implementer"],
                           ["other"], ["implementer", "verifier"]),
            ("billing",): ([], {"basis": "flat-subscription"},
                             {"basis": "flat-subscription", "provider": "sample-provider", "unexpected": True}),
            ("billing", "basis"): (1, "prepaid", "flat-subscription"),
            ("billing", "provider"): (None, 1, "", "sample-provider"),
            ("network",): ([], {"policy": "provider-only", "endpoints": [], "unexpected": True}),
            ("network", "policy"): (1, "none", "provider-only"),
            ("network", "profile"): (1, "P", "profile\n", "profile"),
            ("network", "endpoints"): (
                "not-a-list", [1], [[]], ["bad"], ["sample.example.com\n"], [], ["sample.example.com"],
            ),
            ("availability_probe",): (
                [],
                {"type": "http", "url_env": "FUZZ_URL", "timeout_s": 1, "unexpected": True},
                {"type": "http", "url_env": "FUZZ_URL"},
                {"type": 1, "url_env": "FUZZ_URL", "timeout_s": 1},
                {"type": "http", "url_env": 1, "timeout_s": 1},
                {"type": "tcp", "url_env": "FUZZ_URL", "timeout_s": 1},
                {"type": "http", "url_env": "bad", "timeout_s": 1},
                {"type": "http", "url_env": "FUZZ_URL\n", "timeout_s": 1},
                {"type": "http", "url_env": "FUZZ_URL", "timeout_s": True},
                {"type": "http", "url_env": "FUZZ_URL", "timeout_s": 1.0},
                {"type": "http", "url_env": "FUZZ_URL", "timeout_s": 0},
                {"type": "http", "url_env": "FUZZ_URL", "timeout_s": 1},
                None,
            ),
            ("concurrency_cap",): (True, 1.0, 0, -1, 1, None),
            ("env_passthrough",): (1, [1], [[]], ["bad"], ["FUZZ_ENV\n"],
                                     ["FUZZ_ENV", "FUZZ_ENV"], [], ["FUZZ_ENV"]),
        }
        for path, values in field_values.items():
            for value in values:
                cases.append(corpus_case(path, value))
        for required in sorted(base_manifest):
            candidate = copy.deepcopy(base_manifest)
            del candidate[required]
            cases.append((f"missing {required}", candidate))
        unknown = copy.deepcopy(base_manifest)
        unknown["unexpected"] = True
        cases.append(("unknown top-level key", unknown))

        runtime_validate = lambda candidate: resolver.validate_manifest(candidate, "sampleeng")
        if os.environ.get("PHASE4_FUZZ_DISABLE_MANIFEST_GUARD") == "1":
            # Test-only fault injection used by the review proof below. It is never enabled by
            # normal runs and deliberately makes the differential report a mismatch.
            def runtime_validate(candidate: dict) -> Any:
                if candidate.get("schema_version") in {True, 1.0} \
                        or candidate.get("concurrency_cap") in {True, 1.0}:
                    return candidate
                return resolver.validate_manifest(candidate, "sampleeng")

        mismatches = differential_mismatches(resolver, validator, cases, runtime_validate)
        check(not mismatches, "engine schema/runtime differential has zero mismatches")
        print(f"SCHEMA_DIFFERENTIAL cases={len(cases)} mismatches={len(mismatches)}")
        for mismatch in mismatches:
            print(f"  {mismatch}")
    finally:
        if old_provider_dir is None:
            os.environ.pop("RECURSION_PROVIDER_DIR", None)
        else:
            os.environ["RECURSION_PROVIDER_DIR"] = old_provider_dir

    try:
        if failures:
            print(f"phase4-input-fuzz.test: {len(failures)} FAILED")
            return 1
        print(f"phase4-input-fuzz.test: ALL PASS hostile_cases={len(hostile)} json_cases={len(json_matrix)}")
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

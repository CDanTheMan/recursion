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


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def result_has_traceback(result: subprocess.CompletedProcess[str]) -> bool:
    return "Traceback" in (result.stdout or "") + (result.stderr or "")


def strict_schema_validator(schema: dict):
    import jsonschema

    checker = jsonschema.Draft7Validator.TYPE_CHECKER.redefine(
        "integer", lambda _checker, instance: type(instance) is int
    )
    return jsonschema.validators.extend(jsonschema.Draft7Validator, type_checker=checker)(schema)


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
    except OSError as exc:
        print(f"phase4-input-fuzz: SKIP (system-temp fixture could not be created: {exc})")
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
        except Exception as exc:  # pragma: no cover - diagnostic guard
            check(False, f"{label} has a typed refusal (raw {type(exc).__name__})")
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
        typed(f"engine manifest {field}={value!r}", lambda bad=bad: resolver.validate_manifest(bad, "sampleeng"),
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
        typed(f"backup policy {field}={value!r}", lambda path=path: backup.load_policy(path),
              (backup.BackupPolicyError,))
    for index, (label, raw) in enumerate(json_matrix):
        path = scratch / f"raw-policy-{index}.json"
        path.write_text(raw, encoding="utf-8")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/backup-offsite.py"), "--config", str(path), "validate"],
                                capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_traceback(result),
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
        check(result.returncode != 0 and not result_has_traceback(result),
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
    check(backup_result.returncode == 0 and not result_has_traceback(backup_result),
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
        check(result.returncode != 0 and not result_has_traceback(result),
              "decision queue hostile input is controlled")

    provider_dir = scratch / "providers"
    provider_dir.mkdir()
    (provider_dir / "fixture.json").write_text(json.dumps(profile) + "\n", encoding="utf-8")
    for index, (label, raw) in enumerate(json_matrix):
        (provider_dir / "fixture.json").write_text(raw, encoding="utf-8")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/provider-egress.py"), "validate", "fixture"],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_PROVIDER_DIR=str(provider_dir)))
        check(result.returncode != 0 and not result_has_traceback(result),
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
        check(result.returncode == 2 and not result_has_traceback(result),
              f"resolve-engine hostile manifest {index} is controlled")
    valid_resolver = subprocess.run([PYTHON, str(ROOT / "scripts/resolve-engine.py"), "gemini", "--validate"],
                                    capture_output=True, text=True,
                                    env=dict(os.environ, RECURSION_PROVIDER_DIR=str(ROOT / "scripts/providers")))
    check(valid_resolver.returncode == 0 and not result_has_traceback(valid_resolver),
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
        check((result.returncode == 92 and not result_has_traceback(result)) or host_acl,
              f"worker-sandbox hostile plan {index} is controlled (rc={result.returncode}, host_acl={host_acl})")

    # Exercise every command boundary with traversal, UNC, drive-relative, tilde, and env-style
    # paths.  These are intentionally refusal cases; no command is allowed to print a traceback.
    for path_value in ("../outside", r"\\server\share", r"C:relative", "~/outside", "%TEMP%/outside"):
        result = subprocess.run([PYTHON, str(ROOT / "scripts/backup-offsite.py"), "restore-drill",
                                 "--root", path_value, "--snapshot", path_value],
                                capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_traceback(result),
              f"backup restore-drill path {path_value!r} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/assignment-token.py"), "fixture", "assignment-a",
                                 "--key-file", path_value], capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_traceback(result),
              f"assignment-token path {path_value!r} is controlled")

    result = subprocess.run([PYTHON, str(ROOT / "scripts/provider-connect-proxy.py"), "probe",
                             "--namespace", "/bad", "--allow", "api.fixture.example:443"],
                            capture_output=True, text=True)
    check(result.returncode != 0 and not result_has_traceback(result), "provider proxy CLI boundary is controlled")
    conduct_root = scratch / "conduct-root"
    (conduct_root / "scripts").mkdir(parents=True)
    (conduct_root / "loop/logs").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/conduct-hermes.sh", conduct_root / "scripts/conduct-hermes.sh")
    missing_decision = conduct_root / "missing.json"
    result = subprocess.run([str(BASH), str(conduct_root / "scripts/conduct-hermes.sh"), "--file", str(missing_decision)],
                            capture_output=True, text=True, env=dict(os.environ, RECURSION_ROOT=str(conduct_root)))
    check(result.returncode != 0 and not result_has_traceback(result), "conduct-hermes CLI boundary is controlled")
    for index, (label, raw) in enumerate(json_matrix):
        hostile_decision = conduct_root / f"hostile-{index}.json"
        hostile_decision.write_text(raw, encoding="utf-8")
        result = subprocess.run([str(BASH), str(conduct_root / "scripts/conduct-hermes.sh"),
                                 "--file", str(hostile_decision)],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_ROOT=str(conduct_root)))
        check(result.returncode != 0 and not result_has_traceback(result),
              f"conduct-hermes hostile JSON {label} is controlled")

    # Exercise the remaining Phase 4 validator/loader/CLI boundaries with the same raw matrix.
    # These commands are intentionally pointed at the isolated fixture root, so a malformed
    # value can never reach a live control-plane mutation.
    for label, raw in json_matrix:
        result = subprocess.run([PYTHON, str(ROOT / "scripts/validate-control-state.py"), "decision"],
                                input=raw, text=True, capture_output=True)
        check(result.returncode != 0 and not result_has_traceback(result),
              f"validate-control-state hostile JSON {label} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/validate-decision.py"), "noop", raw],
                                capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_traceback(result),
              f"validate-decision hostile JSON {label} is controlled")
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts/transition_receipt.py"), "--root", str(scratch),
             "apply-fields", "state/missing.json", raw, raw], capture_output=True, text=True,
        )
        check(result.returncode != 0 and not result_has_traceback(result),
              f"transition-receipt hostile JSON {label} is controlled")
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts/instruction_routing.py"), "--root", str(scratch),
             "route", "hostile", raw, raw], capture_output=True, text=True,
        )
        check(result.returncode != 0 and not result_has_traceback(result),
              f"instruction-routing hostile JSON {label} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/project-pilot.py"), "execute-json", raw],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_ROOT=str(scratch)))
        check(result.returncode != 0 and not result_has_traceback(result),
              f"project-pilot hostile JSON {label} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/seed_contract.py"), "digest",
                                 "--root", str(scratch), "--path", raw],
                                capture_output=True, text=True)
        check(result.returncode != 0 and not result_has_traceback(result),
              f"seed-contract hostile path {label} is controlled")

    alias_registry = scratch / "hostile-alias-registry.json"
    for label, raw in json_matrix:
        alias_registry.write_text(raw, encoding="utf-8")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/resolve-model-alias.py"), "custom", "implementer"],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_ALIAS_REGISTRY=str(alias_registry)))
        check(result.returncode != 0 and not result_has_traceback(result),
              f"resolve-model-alias hostile JSON {label} is controlled")

    # Differential corpus for the engine schema.  Draft-7's stock Python type checker treats
    # 1.0 as an integer; the strict checker models the runtime's deliberate plain-int contract.
    schema = json.loads((ROOT / "schemas/control-plane/v1/engine-manifest.schema.json").read_text(encoding="utf-8"))
    validator = strict_schema_validator(schema)
    cases: list[tuple[str, dict]] = [("baseline", copy.deepcopy(base_manifest))]
    for field, value in (("schema_version", True), ("schema_version", False), ("schema_version", 1.0),
                         ("schema_version", 1), ("concurrency_cap", True), ("concurrency_cap", 1.0),
                         ("concurrency_cap", 0), ("concurrency_cap", 1), ("availability_probe", {
                             "type": "http", "url_env": "FUZZ_URL", "timeout_s": 1.0}),
                         ("availability_probe", {"type": "http", "url_env": "FUZZ_URL", "timeout_s": 1}),
                         ("argv", ["{{EXE}}", "{{OTHER}}", "{{PROMPT}}"]),
                         ("model", {"required": False, "argv_suffix": ["{{OTHER}}"]}),
                         ("roles", ["implementer", "implementer"]),
                         ("network", {"policy": "provider-only", "endpoints": ["bad"]}),
                         ("env_passthrough", [[]])):
        mutated = copy.deepcopy(base_manifest)
        mutated[field] = value
        cases.append((f"{field}={value!r}", mutated))
    mismatches: list[str] = []
    for label, candidate in cases:
        schema_valid = not list(validator.iter_errors(candidate))
        try:
            resolver.validate_manifest(candidate, "sampleeng")
            runtime_valid = True
        except resolver.ManifestError:
            runtime_valid = False
        except Exception as exc:  # pragma: no cover - differential must expose raw leaks
            mismatches.append(f"{label}: raw runtime {type(exc).__name__}")
            runtime_valid = False
        if schema_valid != runtime_valid:
            mismatches.append(f"{label}: schema={schema_valid} runtime={runtime_valid}")
    check(not mismatches, "engine schema/runtime differential has zero mismatches")
    print(f"SCHEMA_DIFFERENTIAL cases={len(cases)} mismatches={len(mismatches)}")
    if mismatches:
        for mismatch in mismatches:
            print(f"  {mismatch}")

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

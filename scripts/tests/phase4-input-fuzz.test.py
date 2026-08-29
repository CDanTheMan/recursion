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


def find_bash() -> Path | None:
    discovered = shutil.which("bash")
    if discovered:
        candidate = Path(discovered)
        if candidate.is_file():
            return candidate
    if os.name == "nt":
        program_files = os.environ.get("ProgramFiles") or os.environ.get("ProgramW6432")
        if program_files:
            candidate = Path(program_files) / "Git/bin/bash.exe"
        else:
            candidate = Path(Path(sys.executable).anchor) / "Program Files/Git/bin/bash.exe"
        if candidate.is_file():
            return candidate
    return None


BASH = find_bash()
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


def is_git_bash_acl_artifact(result: subprocess.CompletedProcess[str]) -> bool:
    text = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 256 and "CreateFileMapping" in text and "Win32 error 5" in text


def has_controlled_refusal(result: subprocess.CompletedProcess[str], markers: tuple[str, ...],
                            *paths: Path) -> bool:
    """Require a product refusal signal in addition to the no-traceback/path invariant."""
    text = (result.stdout or "") + (result.stderr or "")
    return result.returncode != 0 and any(marker in text for marker in markers) \
        and not result_has_raw_error_or_path(result, *paths)


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
                            runtime_validate: Callable[[dict], Any] | None = None
                            ) -> tuple[list[str], int, int]:
    """Compare the real declared-draft validator with the product validator without masking errors."""
    validate = runtime_validate or resolver.validate_manifest
    mismatches: list[str] = []
    forward = 0
    reverse = 0
    for label, candidate in cases:
        schema_valid = not list(validator.iter_errors(candidate))
        runtime_valid = True
        try:
            validate(candidate)
        except resolver.ManifestError:
            runtime_valid = False
        if schema_valid != runtime_valid:
            mismatches.append(f"{label}: schema={schema_valid} runtime={runtime_valid}")
            if schema_valid:
                forward += 1
            else:
                reverse += 1
    return mismatches, forward, reverse


def signed_token(proxy: Any, payload: bytes, key: bytes) -> str:
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=")
    signature = hmac.new(key, encoded, hashlib.sha256).digest()
    return encoded.decode("ascii") + "." + base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")


def main() -> int:
    if BASH is None:
        print("phase4-input-fuzz: SKIP (no usable bash interpreter found)")
        return 77
    failures: list[str] = []
    cases_run = 0
    cases_passed = 0
    cases_skipped = 0
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
        nonlocal cases_run, cases_passed
        cases_run += 1
        if condition:
            cases_passed += 1
        print(("ok - " if condition else "FAIL - ") + label)
        if not condition:
            failures.append(label)

    def skip_case(label: str, reason: str) -> None:
        nonlocal cases_skipped
        cases_skipped += 1
        print(f"SKIP - {label}: {reason}")

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
    content_name_mismatch = copy.deepcopy(base_manifest)
    content_name_mismatch["name"] = "othername"
    check(resolver.validate_manifest(content_name_mismatch, "sampleeng")["name"] == "othername",
          "engine content validation accepts a schema-valid name without filename context")
    filename_binding_dir = scratch / "filename-binding"
    filename_binding_dir.mkdir()
    filename_binding_path = filename_binding_dir / "sampleeng.json"
    filename_binding_path.write_text(json.dumps(content_name_mismatch) + "\n", encoding="utf-8")
    try:
        resolver.load_manifest(filename_binding_path, "sampleeng")
    except resolver.ManifestError:
        check(True, "engine loader refuses a name that does not match its filename stem")
    else:
        check(False, "engine loader refuses a name that does not match its filename stem")
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
        check(has_controlled_refusal(result, ("backup-offsite:",), path),
              "backup CLI hostile JSON is controlled")

    secret_root = scratch / "secret-runtime"
    # The final directory hosts secret files and must remain owner-only.  The product guard
    # correctly rejects the previous 0777 fixture rather than repairing or accepting it on Linux.
    # Windows mode bits are not a portable ACL contract, and mode=0700 creates an inaccessible
    # review-host ACL, so retain a writable fixture there while the product's Windows tolerance
    # remains exercised.
    secret_root.mkdir(mode=0o777 if os.name == "nt" else 0o700)
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
        check(has_controlled_refusal(result, ("secret-runtime:",), secret_root),
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
    backup_result: subprocess.CompletedProcess[str] | None = None
    snapshot_available = False
    if os.name == "nt":
        # The Windows host denies re-opening the 0700 lock-candidate ACL used by the Linux
        # witnessed-lock implementation.  Do not replace that unavailable production proof
        # with a fabricated subprocess result or hand-built snapshot.
        skip_case(
            "legitimate runtime snapshot is accepted",
            "Windows cannot reopen the 0700 lock-candidate ACL used by the Linux witnessed-lock "
            "implementation; runtime snapshot acceptance is not proven",
        )
        # Keep the independent manifest-loader fuzz executable with a snapshot produced by the
        # real writer.  This does not substitute for the skipped backup acceptance proof.  The
        # adapter changes only the temporary fixture ACL; the writer still creates and validates
        # the complete snapshot tree and manifest.
        class WritableSnapshotPath(type(snapshot)):
            def mkdir(self, mode: int = 0o777, parents: bool = False,
                      exist_ok: bool = False) -> None:
                super().mkdir(mode=0o777, parents=parents, exist_ok=exist_ok)

        runtime._write_snapshot_tree(valid_root, WritableSnapshotPath(snapshot))
        snapshot_available = True
    else:
        backup_result = subprocess.run(
            [PYTHON, str(ROOT / "scripts/runtime-state.py"), "backup", str(snapshot)],
            env=env, capture_output=True, text=True,
        )
        backup_output = backup_result.stdout or ""
        check(backup_result.returncode == 0 and not result_has_raw_error_or_path(backup_result, snapshot)
              and f"backup destination={snapshot.name} files=" in backup_output
              and "pause_sha256=" in backup_output,
              "legitimate runtime snapshot is accepted")
        snapshot_available = backup_result.returncode == 0
    digest_victim = scratch / "digest-victim"
    digest_replacement = scratch / "digest-replacement"
    digest_victim.write_bytes(b"original digest input\n")
    digest_replacement.write_bytes(b"replacement digest input\n")
    real_open = runtime.os.open
    def swapping_open(path: object, flags: int, *args: Any) -> int:
        if Path(path) == digest_victim:
            os.replace(digest_victim, scratch / "digest-victim-original")
            os.replace(digest_replacement, digest_victim)
        return real_open(path, flags, *args)
    digest_swap_refused = False
    runtime.os.open = swapping_open
    try:
        try:
            runtime.digest(digest_victim)
        except RuntimeError as exc:
            digest_swap_refused = str(exc) == "runtime digest path changed while opening"
    finally:
        runtime.os.open = real_open
    check(digest_swap_refused, "runtime digest refuses a deterministic open-path replacement")
    if snapshot_available:
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
        check(has_controlled_refusal(result, ("decision-queue:",), queue_base),
              "decision queue hostile input is controlled")

    provider_dir = scratch / "providers"
    provider_dir.mkdir()
    (provider_dir / "fixture.json").write_text(json.dumps(profile) + "\n", encoding="utf-8")
    for index, (label, raw) in enumerate(json_matrix):
        (provider_dir / "fixture.json").write_text(raw, encoding="utf-8")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/provider-egress.py"), "validate", "fixture"],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_PROVIDER_DIR=str(provider_dir)))
        check(has_controlled_refusal(result, ("provider-egress:",), provider_dir),
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
        check(result.returncode == 2 and has_controlled_refusal(result, ("resolve-engine:",), resolver_dir),
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
        check(has_controlled_refusal(result, ("backup-offsite:",)),
              f"backup restore-drill path {path_value!r} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/assignment-token.py"), "fixture", "assignment-a",
                                 "--key-file", path_value], capture_output=True, text=True)
        check(has_controlled_refusal(result, ("assignment-token:",)),
              f"assignment-token path {path_value!r} is controlled")

    result = subprocess.run([PYTHON, str(ROOT / "scripts/provider-connect-proxy.py"), "probe",
                             "--namespace", "/bad", "--allow", "api.fixture.example:443"],
                            capture_output=True, text=True)
    check(has_controlled_refusal(result, ("provider-connect-proxy:",)), "provider proxy CLI boundary is controlled")
    conduct_script = Path("scripts/conduct-hermes.sh")
    # Keep the fixture's runtime closure explicit.  conduct-hermes invokes the queue and
    # runtime helpers on its durable --file path; transition_receipt imports jsonl_durable, and
    # the final decision-executed event invokes taskctl.  seed_contract is included with the
    # first-party boundary helpers so a future shared import cannot silently turn this into an
    # environmental refusal again.
    conduct_fixture_scripts = (
        "conduct-hermes.sh", "validate-decision.py", "decision-queue.py", "runtime-state.py",
        "transition_receipt.py", "seed_contract.py", "jsonl_durable.py", "taskctl.sh",
    )

    def stage_conduct_fixture(root: Path) -> None:
        root.mkdir(parents=True)
        # This is a hermetic copy of the actuator's runtime closure, not an empty directory.  A
        # positive noop must reach action_transition and taskctl so a hostile case cannot pass
        # merely because the validator or durable action machinery is absent.
        scripts_dir = root / "scripts"
        scripts_dir.mkdir()
        for script_name in conduct_fixture_scripts:
            shutil.copy2(ROOT / "scripts" / script_name, scripts_dir / script_name)
        for relative in (
            "loop/logs", "state/.locks", "state/actions", "state/decision-queue",
            "state/recovery", "state/instructions", "state/tasks",
        ):
            (root / relative).mkdir(parents=True, exist_ok=True)
        # Direct --file execution still runs the durable controller path: action transitions append
        # to action-events.jsonl, and the final decision-executed event goes through taskctl's
        # events.jsonl writer.  Seed those journals (and the decision journal) so the fixture has
        # the same empty controller state as a newly initialized checkout.  Keep .env empty so a
        # host environment cannot retarget the hermetic root, and keep all subprocess scratch
        # files below this fixture.
        (root / ".env").write_text("", encoding="utf-8")
        for relative in ("state/events.jsonl", "state/action-events.jsonl", "state/decisions.jsonl"):
            (root / relative).write_bytes(b"")
        (root / "tmp").mkdir()

    def write_raw(path: Path, raw: str | bytes) -> None:
        path.write_bytes(raw if isinstance(raw, bytes) else raw.encode("utf-8"))

    def run_conduct(root: Path, decision: Path, extra_env: dict[str, str] | None = None):
        environment = dict(os.environ, RECURSION_ROOT=str(root), TMPDIR=str(root / "tmp"))
        if extra_env:
            environment.update(extra_env)
        return subprocess.run(
            [str(BASH), str(root / conduct_script), "--file", str(decision)],
            capture_output=True, text=True, env=environment,
        )

    def run_runtime(root: Path, *args: str):
        return subprocess.run(
            [PYTHON, str(root / "scripts/runtime-state.py"), *args],
            capture_output=True, text=True,
            env=dict(os.environ, RECURSION_ROOT=str(root), TMPDIR=str(root / "tmp")),
        )

    def conduct_text(result: subprocess.CompletedProcess[str]) -> str:
        return (result.stdout or "") + (result.stderr or "")

    def conduct_refusal(result: subprocess.CompletedProcess[str], marker: str,
                        root: Path) -> bool:
        text = conduct_text(result)
        return result.returncode != 0 and marker in text \
            and "boundary=decision-path-unavailable" not in text \
            and not result_has_raw_error_or_path(result, root)

    def action_payload_digest(row: dict[str, Any]) -> str:
        payload = {
            "actor": row.get("actor") or "", "verb": row.get("verb") or "",
            "args": row.get("args", row.get("arguments", [])) or [],
            "text": row.get("text") or "", "plan": row.get("plan") or None,
            "instruction_id": row.get("instruction_id") or None,
            "project": row.get("project") or "",
            "goal": row.get("goal", row.get("goal_id", "")) or "",
            "decision_source": row.get("decision_source") or "",
            "routed_decider": row.get("routed_decider") or "",
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    conduct_positive: dict[str, Any] = {
        "schema_version": 1, "id": "conduct-positive", "actor": "head-hermes",
        "routed_decider": "head-hermes", "decision_source": "hermes-model", "verb": "noop",
        "args": [], "goal": "conduct fixture positive control",
        "wrong_if": "the noop action does not complete", "text": "",
        "idempotency_key": "conduct-positive-key",
    }
    conduct_positive["decision_payload_sha256"] = action_payload_digest(conduct_positive)
    positive_raw = json.dumps(conduct_positive, ensure_ascii=False,
                              separators=(",", ":")).encode("utf-8") + b"\n"

    conduct_root = scratch / "conduct-root"
    stage_conduct_fixture(conduct_root)
    check(all((conduct_root / "scripts" / name).is_file() for name in conduct_fixture_scripts),
          "conduct-hermes fixture stages its complete dependency set")
    print("CONDUCT_FIXTURE_DEPENDENCIES " + ",".join(conduct_fixture_scripts))
    runtime_namespace_probe = run_runtime(
        conduct_root, "lock-acquire", str(conduct_root / "state/.locks/a.lock"), "4242"
    )
    check(runtime_namespace_probe.returncode != 0
          and "operator lock path is outside the supported lock namespace" in
          (runtime_namespace_probe.stdout + runtime_namespace_probe.stderr)
          and "runtime-state: operation refused" in
          (runtime_namespace_probe.stdout + runtime_namespace_probe.stderr)
          and not result_has_raw_error_or_path(runtime_namespace_probe, conduct_root),
          "runtime-state lock namespace refusal names its precondition")
    runtime_owner_probe = run_runtime(
        conduct_root, "lock-acquire",
        str(conduct_root / "state/.locks/action-0123456789abcdef01234567.lock"), "4242"
    )
    check(runtime_owner_probe.returncode != 0
          and "cannot witness lock owner process start: 4242" in
          (runtime_owner_probe.stdout + runtime_owner_probe.stderr),
          "runtime-state lock owner refusal names its precondition")
    runtime_live_lock = conduct_root / "state/.locks/action-0123456789abcdef01234568.lock"
    runtime_live_acquire = run_runtime(
        conduct_root, "lock-acquire", str(runtime_live_lock), str(os.getpid())
    )
    runtime_live_release = run_runtime(
        conduct_root, "lock-release", str(runtime_live_lock), str(os.getpid())
    )
    check(runtime_live_acquire.returncode == 0 and runtime_live_release.returncode == 0
          and not runtime_live_lock.exists(),
          "runtime-state lock candidate is acquired and released by a live owner")
    missing_decision = conduct_root / "missing.json"
    result = run_conduct(conduct_root, missing_decision)
    conduct_host_acl = is_git_bash_acl_artifact(result)

    def conduct_check(condition: bool, label: str) -> None:
        if conduct_host_acl:
            check(True, label + " (truthful Git Bash host-ACL skip)")
        else:
            check(condition, label)

    conduct_check(result.returncode == 2 and "boundary=decision-path-unavailable" in conduct_text(result)
                  and not result_has_raw_error_or_path(result, conduct_root),
                  "conduct-hermes missing-file outcome is a distinct controlled refusal")

    positive_decision = conduct_root / "positive.json"
    write_raw(positive_decision, positive_raw)
    result = run_conduct(conduct_root, positive_decision)
    positive_action_id = "action-" + hashlib.sha256(
        conduct_positive["idempotency_key"].encode("utf-8")
    ).hexdigest()[:24]
    positive_action = conduct_root / "state/actions" / f"{positive_action_id}.json"
    try:
        positive_action_row = json.loads(positive_action.read_text(encoding="utf-8"))
        positive_action_events = [
            json.loads(line) for line in
            (conduct_root / "state/action-events.jsonl").read_text(encoding="utf-8").splitlines()
            if line
        ]
        positive_durable = (
            positive_action_row.get("id") == positive_action_id
            and positive_action_row.get("verb") == "noop"
            and positive_action_row.get("status") == "succeeded"
            and positive_action_row.get("attempts") == 1
            and [event.get("status") for event in positive_action_events
                 if event.get("action_id") == positive_action_id]
            == ["pending", "running", "succeeded"]
        )
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, AttributeError):
        positive_durable = False
    conduct_check(result.returncode == 0 and "done (verb=noop rc=0)" in conduct_text(result)
                  and positive_durable and not result_has_raw_error_or_path(result, conduct_root),
                  "conduct-hermes well-formed decision succeeds in the fixture")

    conduct_expected = {
        "object": "boundary=semantic-validation", "trailing-newline": "boundary=semantic-validation",
        "deep-json": "boundary=depth", "huge-int": "boundary=integer-range",
        "1e999": "boundary=non-finite-number", "NaN": "boundary=json-constant",
        "Infinity": "boundary=json-constant",
    }
    for index, (label, raw) in enumerate(json_matrix):
        hostile_decision = conduct_root / f"hostile-{index}.json"
        write_raw(hostile_decision, raw)
        result = run_conduct(conduct_root, hostile_decision)
        marker = conduct_expected.get(label, "boundary=non-object-root")
        conduct_check(conduct_refusal(result, marker, conduct_root),
                      f"conduct-hermes hostile JSON {label} has typed refusal {marker}")

    def conduct_variant(label: str, **changes: Any) -> bytes:
        row = copy.deepcopy(conduct_positive)
        row["id"] = f"conduct-{label}"
        row["idempotency_key"] = f"conduct-{label}-key"
        row.update(changes)
        row["decision_payload_sha256"] = action_payload_digest(row)
        return json.dumps(row, ensure_ascii=False, allow_nan=True,
                          separators=(",", ":")).encode("utf-8") + b"\n"

    deep_value: Any = "leaf"
    for _ in range(65):
        deep_value = {"nested": deep_value}
    in_bounds_value: Any = "leaf"
    for _ in range(63):
        in_bounds_value = {"nested": in_bounds_value}
    in_bounds_decision = conduct_root / "in-bounds-depth.json"
    write_raw(in_bounds_decision, conduct_variant("in-bounds-depth", unknown=in_bounds_value))
    result = run_conduct(conduct_root, in_bounds_decision)
    conduct_check(result.returncode == 0 and "done (verb=noop rc=0)" in conduct_text(result)
                  and not result_has_raw_error_or_path(result, conduct_root),
                  "conduct-hermes in-bounds JSON depth is accepted")
    empty_in_bounds_value: Any = []
    for _ in range(63):
        empty_in_bounds_value = [empty_in_bounds_value]
    empty_in_bounds_decision = conduct_root / "in-bounds-empty-depth.json"
    write_raw(empty_in_bounds_decision,
              conduct_variant("in-bounds-empty-depth", unknown=empty_in_bounds_value))
    result = run_conduct(conduct_root, empty_in_bounds_decision)
    conduct_check(result.returncode == 0 and "done (verb=noop rc=0)" in conduct_text(result)
                  and not result_has_raw_error_or_path(result, conduct_root),
                  "conduct-hermes maximum empty-container JSON depth is accepted")
    brace_string = "{}[]" * 512
    brace_string_decision = conduct_root / "braces-in-string.json"
    write_raw(brace_string_decision, conduct_variant("braces-in-string", unknown=brace_string))
    result = run_conduct(conduct_root, brace_string_decision)
    conduct_check(result.returncode == 0 and "done (verb=noop rc=0)" in conduct_text(result)
                  and not result_has_raw_error_or_path(result, conduct_root),
                  "conduct-hermes braces inside a legitimate string are ignored by depth")
    deep_brace_value: Any = brace_string
    for _ in range(65):
        deep_brace_value = {"nested": deep_brace_value}
    deep_brace_decision = conduct_root / "deep-braces-in-string.json"
    write_raw(deep_brace_decision, conduct_variant("deep-braces-in-string", unknown=deep_brace_value))
    result = run_conduct(conduct_root, deep_brace_decision)
    conduct_check(conduct_refusal(result, "boundary=depth", conduct_root),
                  "conduct-hermes hostile depth with braces in a string is refused")
    utf8_probe = "replacement \ufffd"
    utf8_raw = conduct_variant("utf8", unknown=utf8_probe)
    # The replacement character is valid JSON after strict decoding, so replacing only its
    # encoded bytes with a bare continuation byte makes the pre-boundary snapshot invalid while
    # preserving the exact post-replacement value and action digest.  The mutant must therefore
    # reach the successful noop, not merely another unrelated refusal.
    utf8_raw = utf8_raw.replace("\ufffd".encode("utf-8"), b"\x80", 1)
    targeted_cases: list[tuple[str, bytes, str, str, str]] = [
        ("string-length", conduct_variant("string-length", unknown="x" * 4097),
         "boundary=string", "MAX_STRING string-length guard", "string"),
        ("integer-type", conduct_variant("integer-type", max_tokens=1.0),
         "boundary=integer-type", "INTEGER_FIELDS type guard", "integer"),
        ("real-string", conduct_variant("real-string", max_cost_usd="1"),
         "boundary=real-type", "REAL_FIELDS numeric-type guard", "real"),
        ("real-bool", conduct_variant("real-bool", max_cost_usd=True),
         "boundary=real-type", "REAL_FIELDS bool guard", "real"),
        ("path-type", conduct_variant("path-type", path=1),
         "boundary=path-type", "PATH_FIELDS type guard", "path-type"),
        ("path-unsafe", conduct_variant("path-unsafe", path="../outside"),
         "boundary=path-unsafe", "check_path guard", "check-path"),
        ("depth", conduct_variant("depth", unknown=deep_value),
         "boundary=depth", "MAX_DEPTH guard", "depth"),
        ("non-object-root", b"[]", "boundary=non-object-root", "object-root guard", "root"),
        ("utf8", utf8_raw, "boundary=utf8-strict", "strict UTF-8 decode guard", "utf8"),
        ("parse-constant", conduct_variant("parse-constant", unknown=float("nan")),
         "boundary=json-constant", "parse_constant guard", "constant"),
    ]
    for index, (label, raw, marker, _guard, _mutation_key) in enumerate(targeted_cases):
        decision = conduct_root / f"targeted-{index}.json"
        write_raw(decision, raw)
        result = run_conduct(conduct_root, decision)
        conduct_check(conduct_refusal(result, marker, conduct_root),
                      f"conduct-hermes targeted JSON {label} has typed refusal {marker}")

    long_path = str(conduct_root / ("long-" + "x" * 4096))
    result = run_conduct(conduct_root, Path(long_path))
    conduct_check(result.returncode == 2 and "boundary=decision-path-invalid" in conduct_text(result)
                  and not result_has_raw_error_or_path(result, conduct_root),
                  "conduct-hermes decision path size has a typed refusal")

    # The child receives the immutable bytes and their digest separately from the projection path.
    # A projection rewrite must remain refused, and a forged snapshot must hit the original
    # immutable-digest refusal rather than making the integrity check vacuous.
    tamper_decision = conduct_root / "tamper.json"
    snapshot_digest = hashlib.sha256(positive_raw).hexdigest()
    snapshot_b64 = base64.b64encode(positive_raw).decode("ascii")
    write_raw(tamper_decision, positive_raw.replace(b'"noop"', b'"work"', 1))
    result = run_conduct(conduct_root, tamper_decision, {
        "RECURSION_DECISION_FILE_DIGEST": snapshot_digest,
        "RECURSION_DECISION_SNAPSHOT_B64": snapshot_b64,
    })
    conduct_check(result.returncode == 74
                  and "REFUSED - decision projection changed before child action" in conduct_text(result)
                  and not result_has_raw_error_or_path(result, conduct_root),
                  "conduct-hermes refuses a decision projection tampered after snapshot")

    write_raw(tamper_decision, positive_raw)
    forged_snapshot = base64.b64encode(positive_raw + b" ").decode("ascii")
    result = run_conduct(conduct_root, tamper_decision, {
        "RECURSION_DECISION_FILE_DIGEST": snapshot_digest,
        "RECURSION_DECISION_SNAPSHOT_B64": forged_snapshot,
    })
    conduct_check(result.returncode == 74
                  and "REFUSED - immutable decision snapshot digest changed" in conduct_text(result)
                  and not result_has_raw_error_or_path(result, conduct_root),
                  "conduct-hermes refuses a tampered immutable snapshot with the digest message")

    # Each mutation is applied to a fresh fixture and only the named guard is disabled.  The
    # original assertion includes the typed boundary marker from the enabled-guard control and
    # must fail once that guard is removed: acceptance is expected for typed extra fields and the
    # UTF-8 case, while the root/constant cases must reach a specific downstream signal.
    conduct_source = (conduct_root / conduct_script).read_text(encoding="utf-8")
    mutation_specs: list[tuple[str, str, str, str, bytes | None, str, str]] = [
        ("file-path-size", "decision file path byte-size guard",
         "if not isinstance(raw,str) or not raw or len(raw.encode(\"utf-8\")) > 4096:",
         "if False:", None, "boundary=decision-path-invalid", "boundary=decision-path-unavailable"),
        ("string-length", "MAX_STRING value-length guard",
         "if len(value) > MAX_STRING or any(ord(char) < 32 for char in value):", "if False:",
         conduct_variant("string-length", unknown="x" * 4097), "boundary=string", "accepted"),
        ("integer-type", "INTEGER_FIELDS type guard",
         "if key in INTEGER_FIELDS and type(value) is not int:",
         "if False:", conduct_variant("integer-type", max_tokens=1.0), "boundary=integer-type", "accepted"),
        ("real-bool", "REAL_FIELDS numeric/bool guard",
         "if key in REAL_FIELDS and value is not None",
         "if False and value is not None", conduct_variant("real-bool", max_cost_usd=True),
         "boundary=real-type", "accepted"),
        ("path-type", "PATH_FIELDS type guard",
         "if value is not None and not isinstance(value, str):",
         "if False:", conduct_variant("path-type", path=1), "boundary=path-type", "accepted"),
        ("check-path", "PATH_FIELDS check_path guard", "            check_path(value)", "            pass",
         conduct_variant("path-unsafe", path="../outside"), "boundary=path-unsafe", "accepted"),
        ("depth", "MAX_DEPTH guard", "if depth > MAX_DEPTH:", "if False:",
         conduct_variant("depth", unknown=deep_value), "boundary=depth", "accepted"),
        ("object-root", "non-object root guard", "if not isinstance(value, dict):", "if False:",
         b"[]", "boundary=non-object-root", "boundary=semantic-validation"),
        ("utf8", "strict UTF-8 snapshot decode guard",
         "text=raw.decode(\"utf-8\", \"strict\")",
         "text=raw.decode(\"utf-8\", \"replace\")", utf8_raw,
         "boundary=utf8-strict", "accepted"),
        ("parse-constant", "parse_constant guard",
         "value=json.loads(text, parse_int=bounded_int, parse_float=bounded_float,\n                     parse_constant=lambda name: (_ for _ in ()).throw(ValueError(\n                         \"decision JSON constant is forbidden\")))",
         "value=json.loads(text, parse_int=bounded_int, parse_float=bounded_float)",
         conduct_variant("parse-constant", unknown=float("nan")), "boundary=json-constant",
         "boundary=non-finite-number"),
    ]
    mutation_rows: list[str] = []
    for index, (label, guard_description, needle, replacement, raw, expected_marker,
                expected_mutation_outcome) in enumerate(mutation_specs):
        occurrences = conduct_source.count(needle)
        check(occurrences == 1, f"conduct-hermes mutation {label} marker is unique")
        if occurrences != 1:
            mutation_rows.append(
                f"{label} -> expected {expected_marker}; guard disabled -> MUTATION MARKER NOT UNIQUE"
            )
            continue
        mutant_root = scratch / f"conduct-mutant-{index}"
        stage_conduct_fixture(mutant_root)
        mutant_source = conduct_source.replace(needle, replacement, 1)
        mutant_script = mutant_root / conduct_script
        mutant_script.write_text(mutant_source, encoding="utf-8")
        syntax = subprocess.run([str(BASH), "-n", str(mutant_script)], capture_output=True, text=True)
        conduct_check(syntax.returncode == 0,
                      f"conduct-hermes mutation {label} remains bash-syntax-valid")
        if raw is None:
            decision = Path(str(mutant_root / ("long-" + "x" * 4096)))
        else:
            decision = mutant_root / f"mutation-{label}.json"
            write_raw(decision, raw)
        result = run_conduct(mutant_root, decision)
        if is_git_bash_acl_artifact(result):
            check(True, f"conduct-hermes mutation {label} is a truthful host-ACL skip")
            mutation_rows.append(
                f"{label} -> {guard_description} disabled; expected {expected_marker} -> HOST-ACL SKIP"
            )
            continue
        text_output = conduct_text(result)
        if expected_mutation_outcome == "accepted":
            assertion_failed = result.returncode == 0 and "done (verb=noop rc=0)" in text_output \
                and expected_marker not in text_output \
                and not result_has_raw_error_or_path(result, mutant_root)
        else:
            assertion_failed = result.returncode != 0 and expected_mutation_outcome in text_output \
                and expected_mutation_outcome != expected_marker \
                and not result_has_raw_error_or_path(result, mutant_root)
        conduct_check(assertion_failed,
                      f"conduct-hermes mutation {label} fails its original assertion")
        if result.returncode == 0:
            observed = "accepted (rc=0)"
        elif result_has_raw_error_or_path(result, mutant_root):
            observed = "downstream raw failure exposed"
        else:
            observed = ", ".join(sorted({
                marker for marker in (
                    "boundary=decision-path-unavailable", "boundary=decision-path-invalid",
                    "boundary=semantic-validation", "boundary=non-finite-number",
                    "boundary=controlled-input-failure",
                ) if marker in text_output
            })) or f"controlled rc={result.returncode}"
        mutation_rows.append(
            f"{label} -> {guard_description} disabled; expected {expected_marker} -> "
            f"assertion observed ({observed})"
        )

    print("CONDUCT_MUTATION_TABLE")
    for row in mutation_rows:
        print("  " + row)

    # Exercise the remaining Phase 4 validator/loader/CLI boundaries with the same raw matrix.
    # These commands are intentionally pointed at the isolated fixture root, so a malformed
    # value can never reach a live control-plane mutation.
    for label, raw in json_matrix:
        result = subprocess.run([PYTHON, str(ROOT / "scripts/validate-control-state.py"), "decision"],
                                input=raw, text=True, capture_output=True)
        check(has_controlled_refusal(result, ("ERR",)),
              f"validate-control-state hostile JSON {label} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/validate-decision.py"), "noop", raw],
                                capture_output=True, text=True)
        check(has_controlled_refusal(result, ("ERR",)),
              f"validate-decision hostile JSON {label} is controlled")
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts/transition_receipt.py"), "--root", str(scratch),
             "apply-fields", "state/missing.json", raw, raw], capture_output=True, text=True,
        )
        check(has_controlled_refusal(result, ("transition-receipt:",), scratch),
              f"transition-receipt hostile JSON {label} is controlled")
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts/instruction_routing.py"), "--root", str(scratch),
             "route", "hostile", raw, raw], capture_output=True, text=True,
        )
        check(has_controlled_refusal(result, ("instruction-routing:",), scratch),
              f"instruction-routing hostile JSON {label} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/project-pilot.py"), "execute-json", raw],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_ROOT=str(scratch)))
        check(has_controlled_refusal(result, ("project-pilot:",), scratch),
              f"project-pilot hostile JSON {label} is controlled")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/seed_contract.py"), "digest",
                                 "--root", str(scratch), "--path", raw],
                                capture_output=True, text=True)
        check(has_controlled_refusal(result, ("seed-contract:",), scratch),
              f"seed-contract hostile path {label} is controlled")

    alias_registry = scratch / "hostile-alias-registry.json"
    for label, raw in json_matrix:
        alias_registry.write_text(raw, encoding="utf-8")
        result = subprocess.run([PYTHON, str(ROOT / "scripts/resolve-model-alias.py"), "custom", "implementer"],
                                capture_output=True, text=True,
                                env=dict(os.environ, RECURSION_ALIAS_REGISTRY=str(alias_registry)))
        check(has_controlled_refusal(result, ("model-alias:",), alias_registry),
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
            ("name",): (None, 1, "", "Sampleeng", "sampleeng\n", "claude", "othername", "sampleeng"),
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

        mismatches, forward_mismatches, reverse_mismatches = differential_mismatches(
            resolver, validator, cases, runtime_validate
        )
        check(not mismatches, "engine schema/runtime differential has zero mismatches")
        print(f"SCHEMA_DIFFERENTIAL cases={len(cases)} mismatches={len(mismatches)}")
        print(f"SCHEMA_DIFFERENTIAL_DIRECTIONS forward={forward_mismatches} reverse={reverse_mismatches}")
        for mismatch in mismatches:
            print(f"  {mismatch}")
    finally:
        if old_provider_dir is None:
            os.environ.pop("RECURSION_PROVIDER_DIR", None)
        else:
            os.environ["RECURSION_PROVIDER_DIR"] = old_provider_dir

    try:
        if failures:
            print(
                f"phase4-input-fuzz.test: SUMMARY ran={cases_run} passed={cases_passed} "
                f"failed={len(failures)} skipped={cases_skipped}"
            )
            return 1
        print(
            f"phase4-input-fuzz.test: SUMMARY ran={cases_run} passed={cases_passed} "
            f"failed=0 skipped={cases_skipped}"
        )
        print(f"phase4-input-fuzz.test: ALL PASS hostile_cases={len(hostile)} json_cases={len(json_matrix)}")
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

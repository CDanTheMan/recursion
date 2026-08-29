#!/usr/bin/env python3
"""Hostile input, path, sidecar, and schema/runtime differential sweep for Phase 5."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - supplied by the Phase 5 image
    raise SystemExit(f"phase5-boundary-sweep.test: jsonschema is required: {exc}")

ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path(sys.executable)
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
sys.path.insert(0, str(ROOT / "scripts"))

import assignment
import phase5_safety


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


resolver = load_module("phase5_sweep_resolver", ROOT / "scripts" / "resolve-engine.py")
runtime_layout = load_module("phase5_sweep_runtime", ROOT / "scripts" / "runtime-layout.py")
provider_egress = load_module("phase5_sweep_provider", ROOT / "scripts" / "provider-egress.py")
validate_gate = load_module("phase5_sweep_gate", ROOT / "scripts" / "validate-gate.py")
control_state = load_module("phase5_sweep_control", ROOT / "scripts" / "validate-control-state.py")
registered = load_module("phase5_sweep_registered", ROOT / "scripts" / "registered-machine-capabilities.py")
worker_evidence = load_module("phase5_sweep_evidence", ROOT / "scripts" / "worker-evidence.py")

SCHEMA = json.loads(
    (ROOT / "schemas" / "control-plane" / "v1" / "engine-manifest.schema.json").read_text(
        encoding="utf-8"
    )
)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"ok - {message}")


def run_command(command: list[str | Path], *, env: dict[str, str] | None = None,
                input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [str(item) for item in command], cwd=ROOT, env=env, input=input_bytes,
        capture_output=True,
    )
    combined = result.stdout + result.stderr
    check(b"Traceback" not in combined, f"no raw traceback: {' '.join(map(str, command[:3]))}")
    return result


def expect_typed(call, label: str, marker: str) -> None:
    try:
        call()
    except (assignment.AssignmentError, phase5_safety.BoundaryError,
            resolver.ManifestError, runtime_layout.LayoutError, ValueError,
            LookupError, SystemExit) as exc:
        check(marker in str(exc), f"typed refusal identifies {label}")
    else:
        raise AssertionError(f"hostile input was accepted: {label}")


HOSTILE_JSON = [
    ("true", b"true"),
    ("false", b"false"),
    ("one-point-zero", b"1.0"),
    ("negative-one", b"-1"),
    ("huge-int", (b"9" * 5000)),
    ("infinite-exp", b"1e999"),
    ("nan", b"NaN"),
    ("empty-string", b'""'),
    ("array", b"[]"),
    ("object", b"{}"),
    ("null", b"null"),
    ("deep-json", b"[" * 140 + b"0" + b"]" * 140),
    ("non-object-root", b"[[]]"),
    ("invalid-utf8", b"\xff\xfe\xfa"),
]

CONTROL_MARKERS = {
    "true": b"record must be a JSON object", "false": b"record must be a JSON object",
    "one-point-zero": b"record must be a JSON object", "negative-one": b"record must be a JSON object",
    "empty-string": b"record must be a JSON object", "array": b"record must be a JSON object",
    "null": b"record must be a JSON object", "non-object-root": b"record must be a JSON object",
    "object": b"missing required field(s)", "huge-int": b"control-state record is malformed",
    "infinite-exp": b"contains a non-finite number", "nan": b"control-state record is malformed",
    "deep-json": b"exceeds the maximum JSON nesting depth", "invalid-utf8": b"control-state record is malformed",
}
ENGINE_MARKERS = {
    "true": b"manifest must be a JSON object", "false": b"manifest must be a JSON object",
    "one-point-zero": b"manifest must be a JSON object", "negative-one": b"manifest must be a JSON object",
    "empty-string": b"manifest must be a JSON object", "array": b"manifest must be a JSON object",
    "null": b"manifest must be a JSON object", "non-object-root": b"manifest must be a JSON object",
    "object": b"manifest missing required key(s)", "huge-int": b"is not valid JSON",
    "infinite-exp": b"contains a non-finite number", "nan": b"is not valid JSON",
    "deep-json": b"exceeds the maximum JSON nesting depth", "invalid-utf8": b"could not read manifest",
}
MACHINE_UNREADABLE = {"huge-int", "infinite-exp", "nan", "deep-json", "invalid-utf8"}
WORKER_OBJECT = {"true", "false", "one-point-zero", "negative-one", "empty-string",
                 "array", "null", "non-object-root"}


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def run_json_cli_sweep(scratch: Path) -> None:
    control_dir = scratch / "control"
    engine_dir = scratch / "engines"
    machine_dir = scratch / "machines"
    run_dir = scratch / "runs"
    for directory in (control_dir, engine_dir, machine_dir, run_dir):
        directory.mkdir(parents=True, exist_ok=True)
    base_env = dict(os.environ)

    valid_project = {
        "schema_version": 1, "id": "project-1", "repo": "repo", "default_branch": "main",
        "deploy_key_ref": "key", "charter": "charter", "topic": "topic",
        "pilot_id": "pilot-1", "status": "pending",
    }
    valid_engine = json.loads((ROOT / "scripts" / "engines" / "cursor.json").read_text(encoding="utf-8"))
    valid_engine["name"] = "sampleeng"
    valid_descriptor = {
        "schema_version": 1, "id": "machine-1", "kind": "registered-machine",
        "capabilities": ["linux", "network"],
    }
    for label, raw in HOSTILE_JSON:
        control_path = control_dir / f"{label}.json"
        engine_path = engine_dir / "sampleeng.json"
        machine_path = machine_dir / "machine-1.json"
        run_path = run_dir / f"{label}.json"
        for path in (control_path, engine_path, machine_path, run_path):
            write(path, raw)

        control_result = run_command([
            PYTHON, ROOT / "scripts" / "validate-control-state.py", "project", control_path
        ])
        check(control_result.returncode == 2 and CONTROL_MARKERS[label] in control_result.stderr,
              f"control-state typed refusal for {label}")

        engine_env = dict(base_env, RECURSION_ENGINE_DIR=str(engine_dir))
        engine_result = run_command([
            PYTHON, ROOT / "scripts" / "resolve-engine.py", "sampleeng", "--validate"
        ], env=engine_env)
        check(engine_result.returncode == 2 and ENGINE_MARKERS[label] in engine_result.stderr,
              f"resolve-engine typed refusal for {label}")

        machine_env = dict(base_env, RECURSION_MACHINE_DIR=str(machine_dir),
                           RECURSION_REGISTERED_MACHINE_ADAPTER="1",
                           RECURSION_REGISTERED_MACHINE_MACHINE_1_ENABLED="1")
        machine_result = run_command([
            PYTHON, ROOT / "scripts" / "registered-machine-capabilities.py", "machine-1",
            "--emit", scratch / f"cap-{label}.json",
        ], env=machine_env)
        machine_marker = (b"machine descriptor is unreadable" if label in MACHINE_UNREADABLE
                          else b"machine descriptor has invalid fields")
        check(machine_result.returncode == 2 and machine_marker in machine_result.stderr,
              f"registered capabilities typed refusal for {label}")

        evidence_result = run_command([
            PYTHON, ROOT / "scripts" / "worker-evidence.py", "finish", run_path,
            "failed", "hostile", "1",
        ], env=base_env)
        evidence_marker = (b"evidence file must contain an object" if label in WORKER_OBJECT
                           else (b"immutable start evidence is unavailable"
                                 if label == "object" else b"evidence file is unreadable"))
        check(evidence_result.returncode == 1 and evidence_marker in evidence_result.stderr,
              f"worker evidence typed refusal for {label}")

        try:
            expect_typed(lambda: assignment.load_assignment(run_path), f"assignment loader {label}",
                         "assignment")
        except AssertionError:
            raise

    # Positive control-plane and descriptor values remain accepted.
    valid_control_path = control_dir / "valid-project.json"
    write(valid_control_path, json.dumps(valid_project).encode("utf-8"))
    positive = run_command([
        PYTHON, ROOT / "scripts" / "validate-control-state.py", "project", valid_control_path
    ])
    check(positive.returncode == 0, "valid control-state record is accepted")

    write(engine_dir / "sampleeng.json", json.dumps(valid_engine).encode("utf-8"))
    positive = run_command([
        PYTHON, ROOT / "scripts" / "resolve-engine.py", "sampleeng", "--validate"
    ], env=dict(base_env, RECURSION_ENGINE_DIR=str(engine_dir)))
    check(positive.returncode == 0, "valid plugin manifest is accepted")

    write(machine_dir / "machine-1.json", json.dumps(valid_descriptor).encode("utf-8"))
    positive = run_command([
        PYTHON, ROOT / "scripts" / "registered-machine-capabilities.py", "machine-1",
        "--emit", scratch / "cap-valid.json",
    ], env=dict(base_env, RECURSION_MACHINE_DIR=str(machine_dir),
                RECURSION_REGISTERED_MACHINE_ADAPTER="1",
                RECURSION_REGISTERED_MACHINE_MACHINE_1_ENABLED="1"))
    check(positive.returncode == 0, "valid machine capability input is accepted")


def run_path_sweep(scratch: Path) -> None:
    _, controller, assignment_value, controller_sha = make_assignment_fixture(scratch)
    os.environ["RECURSION_ROOT"] = str(controller)
    positive_profile = provider_egress.load("cursor", str(controller), controller_sha)
    check(positive_profile["provider"] == "cursor",
          "legitimate controller-bound provider profile is accepted")
    for label, value in (
        ("traversal", "../outside"),
        ("windows-traversal", r"..\outside"),
        ("unc", r"\\server\share"),
        ("drive-relative", "C:outside"),
    ):
        expect_typed(lambda value=value: runtime_layout._safe_entrypoint(value),
                     f"runtime entrypoint path {label}", "confined relative path")
        expect_typed(lambda value=value: resolver.validate_relative_path(value, "path"),
                     f"manifest path {label}", "relative path")
        expect_typed(lambda value=value: validate_gate.paths(value), f"gate path {label}",
                     "unsafe gate file")
        expect_typed(lambda value=value: assignment._validate_allowed_paths([value]),
                     f"assignment path {label}", "allowed_paths is")

    check(assignment._validate_allowed_paths(["scripts"]) == ["scripts"],
          "legitimate assignment allowed_paths validation succeeds")

    source = scratch / "layout-source"
    source.mkdir()
    executable = source / "engine"
    executable.write_bytes(b"engine\n")
    executable.chmod(0o755)
    check(phase5_safety.verify_leaf(executable) is not None, "single-link runtime source is inspectable")
    hardlink = source / "hardlink"
    os.link(executable, hardlink)
    expect_typed(lambda: runtime_layout._copy_tree(source, scratch / "hardlink-destination", "engine"),
                 "runtime staging hardlink substitution", "hardlinked file")
    outside = scratch / "outside.txt"
    outside.write_bytes(b"outside")
    profile_path = controller / "scripts" / "provider-egress-profiles.json"
    profile_backup = scratch / "provider-egress-profiles.json.backup"
    profile_backup.write_bytes(profile_path.read_bytes())
    profile_replaced = False
    profile_symlink = False
    profile_junction = False
    try:
        profile_path.unlink()
        profile_replaced = True
        try:
            profile_path.symlink_to(outside)
            profile_symlink = True
        except (OSError, NotImplementedError):
            profile_junction_result = subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J", str(profile_path), str(scratch)],
                capture_output=True,
            )
            if profile_junction_result.returncode == 0:
                profile_junction = True
            else:
                print("ok - provider profile reparse battery skipped because link creation is unavailable")
    except (OSError, NotImplementedError):
        print("ok - provider profile reparse battery skipped because this Windows account cannot replace the profile")
    else:
        if profile_symlink or profile_junction:
            expect_typed(lambda: provider_egress.load("cursor", str(controller), controller_sha),
                         "provider profile reparse leaf", "regular non-reparse")
    finally:
        if profile_symlink:
            profile_path.unlink()
        if profile_junction:
            subprocess.run(["cmd.exe", "/c", "rmdir", str(profile_path)],
                           capture_output=True)
        if profile_replaced:
            profile_path.write_bytes(profile_backup.read_bytes())
    linked = source / "linked.txt"
    try:
        linked.symlink_to(outside)
    except (OSError, NotImplementedError):
        print("ok - symlink battery skipped because this Windows account cannot create symlinks")
    else:
        expect_typed(lambda: phase5_safety.verify_leaf(linked), "final symlink leaf", "reparse")
        expect_typed(lambda: runtime_layout._copy_tree(source, scratch / "symlink-destination", "engine"),
                     "runtime staging symlink source", "link")

    outside_dir = scratch / "outside-dir"
    outside_dir.mkdir()
    junction = scratch / "junction-source"
    junction_result = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(junction), str(outside_dir)],
        capture_output=True,
    )
    if junction_result.returncode == 0:
        expect_typed(lambda: runtime_layout._safe_source(junction), "Windows junction runtime source", "unavailable")
    else:
        print("ok - junction battery skipped because junction creation is unavailable")

    output_link = scratch / "output-link"
    try:
        output_link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pass
    else:
        expect_typed(lambda: phase5_safety.atomic_write(output_link, b"overwrite"),
                     "atomic publish refuses final symlink", "reparse")

    gate_root = scratch / "gate-root"
    (gate_root / "scripts").mkdir(parents=True)
    gate_file = gate_root / "scripts" / "gate.sh"
    gate_file.write_text("#!/bin/sh\n", encoding="utf-8")
    gate_link = gate_root / "scripts" / "linked.sh"
    try:
        gate_link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pass
    else:
        check(not validate_gate.resolved_under(gate_root, "scripts/linked.sh", ["scripts"]),
              "gate final symlink leaf is refused")

    gate_ok = run_command([
        PYTHON, ROOT / "scripts" / "validate-gate.py",
        "--acceptance", "test -f scripts/gate.sh", "--allowed-paths", "scripts",
    ])
    check(gate_ok.returncode == 0, "legitimate gate validation succeeds")

    clean_source = scratch / "positive-source"
    clean_source.mkdir()
    clean_entry = clean_source / "engine"
    clean_entry.write_bytes(b"engine\n")
    clean_entry.chmod(0o755)
    runtime_ok = run_command([
        PYTHON, ROOT / "scripts" / "runtime-layout.py", "stage",
        "--source", clean_source, "--destination", scratch / "positive-runtime", "--entrypoint", "engine",
    ])
    check(runtime_ok.returncode == 0, "legitimate runtime staging succeeds through the CLI")


def make_assignment_fixture(scratch: Path) -> tuple[Path, Path, dict, str]:
    fixture = scratch / ("assignment-fixture-" + secrets.token_hex(4))
    fixture.mkdir()
    source = fixture / "assignment-source"
    (source / "scripts").mkdir(parents=True)
    (source / "scripts" / "gate.sh").write_text("#!/bin/sh\ntest -s result.txt\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main", str(source)], check=True)
    subprocess.run(["git", "-C", str(source), "config", "core.autocrlf", "false"], check=True)
    subprocess.run(["git", "-C", str(source), "add", "."], check=True)
    subprocess.run(["git", "-C", str(source), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-qm", "source"], check=True)

    controller = fixture / "assignment-controller"
    (controller / "scripts" / "engines").mkdir(parents=True)
    for relative in (
        "validate-gate.py", "phase5_safety.py", "resolve-engine.py",
        "provider-egress-profiles.json", "capacity-pools.json",
    ):
        source_path = ROOT / "scripts" / relative
        if relative == "phase5_safety.py":
            destination = controller / "scripts" / relative
        elif relative.endswith(".py"):
            destination = controller / "scripts" / relative
        else:
            destination = controller / "scripts" / relative
        shutil.copy2(source_path, destination)
    shutil.copy2(ROOT / "scripts" / "engines" / "cursor.json",
                 controller / "scripts" / "engines" / "cursor.json")
    subprocess.run(["git", "init", "-q", "-b", "main", str(controller)], check=True)
    subprocess.run(["git", "-C", str(controller), "config", "core.autocrlf", "false"], check=True)
    subprocess.run(["git", "-C", str(controller), "add", "."], check=True)
    subprocess.run(["git", "-C", str(controller), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-qm", "controller"], check=True)
    (controller / "state").mkdir()
    key = controller / "state/.worker-evidence.key"
    key.write_bytes(os.urandom(32)); key.chmod(0o600)

    source_sha = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    controller_sha = subprocess.check_output(["git", "-C", str(controller), "rev-parse", "HEAD"], text=True).strip()
    gate_bytes = (source / "scripts" / "gate.sh").read_bytes()
    gate_contract = {
        "acceptance": "bash scripts/gate.sh",
        "acceptance_sha256": hashlib.sha256(b"bash scripts/gate.sh").hexdigest(),
        "gate_files": {"scripts/gate.sh": hashlib.sha256(gate_bytes).hexdigest()},
        "controller_gate_files": {},
    }
    role = {
        "engine": "cursor", "provider": "cursor", "model": "cursor-primary",
        "network_policy": "provider-only", "network_profile": "cursor",
        "argv": ["{{EXE}}", "-p", "{{PROMPT}}", "--output-format", "text", "--force",
                 "--model", "{{MODEL}}"],
        "network_endpoints": ["api.cursor.com", "api2.cursor.sh"],
    }
    value = {
        "task_id": "task-1", "project_id": "project-1", "source_repository": str(source),
        "source_branch": "main", "source_sha": source_sha,
        "controller_repository": str(controller), "controller_sha": controller_sha,
        "seed_manifest_digest": "", "engine": "cursor", "provider": "cursor",
        "capacity_pool": "cursor-ultra-grok-bot", "model": "cursor-primary",
        "host": "gs-recursion", "sandbox_profile": "strict-linux", "network_policy": "provider-only",
        "network_profile": "cursor", "network_endpoints": list(role["network_endpoints"]),
        "argv": list(role["argv"]), "allowed_paths": ["scripts"],
        "gate_digest": hashlib.sha256(assignment.canonical_bytes(gate_contract)).hexdigest(),
        "gate_contract": gate_contract,
        "role_assignments": {"implementer": role, "verifier": dict(role)},
        "publication_policy": "verified-integration-only",
    }
    return source, controller, value, controller_sha


def run_sidecar_battery(scratch: Path) -> None:
    source, controller, value, _ = make_assignment_fixture(scratch)
    os.environ["RECURSION_ROOT"] = str(controller)
    os.environ.pop("RECURSION_EVIDENCE_KEY_FILE", None)
    assignment_path = scratch / "assignment.json"
    assignment_path.write_text(json.dumps(value), encoding="utf-8")
    normalized, digest = assignment.load_assignment(assignment_path)
    evidence = scratch / "evidence.json"
    start_command = [
        PYTHON, ROOT / "scripts" / "worker-evidence.py", "start", "--path", evidence,
        "--run-id", "run-1", "--task-id", "task-1", "--role", "implementer",
        "--model-alias", "cursor-primary", "--worktree", source, "--base-commit", "0" * 40,
        "--pid", "1", "--process-group", "1", "--deadline-epoch", "2000000000",
        "--log", "run.log", "--network-policy", "provider-only", "--engine", "cursor",
        "--provider", "cursor", "--capacity-pool", "cursor-ultra-grok-bot",
        "--model", "cursor-primary", "--host", "gs-recursion", "--sandbox-profile", "strict-linux",
        "--assignment-digest", digest, "--assignment-file", assignment_path,
    ]
    started = run_command(start_command, env=dict(os.environ))
    check(started.returncode == 0, "legitimate strict evidence start succeeds")
    sidecar = worker_evidence.start_evidence_path(evidence)
    check(sidecar.is_file(), "authenticated durable start sidecar is created")
    original_sidecar = sidecar.read_bytes()
    original_evidence = evidence.read_bytes()

    caller_key = scratch / "caller-selected-key"
    caller_key.write_bytes(os.urandom(32))
    caller_selected = run_command(start_command, env=dict(
        os.environ, RECURSION_EVIDENCE_KEY_FILE=str(caller_key)))
    check(caller_selected.returncode != 0 and
          b"caller-supplied evidence key selection is refused" in caller_selected.stderr,
          "caller-selected evidence key is explicitly refused")

    recreated = run_command(start_command, env=dict(os.environ))
    check(recreated.returncode != 0 and
          b"immutable start evidence already exists" in recreated.stderr,
          "start sidecar recreation is refused by the immutable binding guard")
    check(sidecar.read_bytes() == original_sidecar, "sidecar recreation cannot replace the original binding")

    forged = json.loads(original_sidecar.decode("utf-8"))
    forged["binding_hmac_sha256"] = "0" * 64
    sidecar.chmod(0o666)
    sidecar.write_text(json.dumps(forged), encoding="utf-8")
    forged_finish = run_command([
        PYTHON, ROOT / "scripts" / "worker-evidence.py", "finish", evidence,
        "succeeded", "forged", "0",
    ], env=dict(os.environ))
    check(forged_finish.returncode != 0 and
          b"immutable start evidence is unavailable" in forged_finish.stderr,
          "edited start sidecar is refused by authentication")
    sidecar.write_bytes(original_sidecar)
    sidecar.chmod(0o444)
    evidence.write_bytes(original_evidence)

    other_value = copy.deepcopy(value)
    other_value["task_id"] = "task-2"
    other_assignment = scratch / "assignment-other.json"
    other_assignment.write_text(json.dumps(other_value), encoding="utf-8")
    _, other_digest = assignment.load_assignment(other_assignment)
    other_evidence = scratch / "evidence-other.json"
    other_start = [item for item in start_command]
    other_start[other_start.index("--path") + 1] = other_evidence
    other_start[other_start.index("--run-id") + 1] = "run-2"
    other_start[other_start.index("--task-id") + 1] = "task-2"
    other_start[other_start.index("--assignment-digest") + 1] = other_digest
    other_start[other_start.index("--assignment-file") + 1] = other_assignment
    other_result = run_command(other_start, env=dict(os.environ))
    check(other_result.returncode == 0, "second legitimate assignment/run starts")
    sidecar.chmod(0o666)
    sidecar.write_bytes(worker_evidence.start_evidence_path(other_evidence).read_bytes())
    cross_bound = run_command([
        PYTHON, ROOT / "scripts" / "worker-evidence.py", "finish", evidence,
        "succeeded", "cross-bound", "0",
    ], env=dict(os.environ))
    check(cross_bound.returncode != 0 and
          b"immutable start evidence is unavailable" in cross_bound.stderr,
          "cross-assignment/run sidecar binding is refused by identity")
    sidecar.write_bytes(original_sidecar)
    sidecar.chmod(0o444)
    evidence.write_bytes(original_evidence)

    execution = {
        "engine": "cursor", "provider": "cursor", "profile": "cursor",
        "endpoints": ["api.cursor.com", "api2.cursor.sh"], "model": "cursor-primary",
        "argv": normalized["role_assignments"]["implementer"]["argv"],
        "assignment_digest": digest, "assignment_identity": digest,
        "status": "finished", "exit_code": 0,
        "network": {"policy": "provider-only", "profile": "cursor", "provider": "cursor",
                    "endpoints": ["api.cursor.com", "api2.cursor.sh"]},
    }
    execution_path = scratch / "execution.json"
    execution_path.write_text(json.dumps(execution), encoding="utf-8")
    finished = run_command([
        PYTHON, ROOT / "scripts" / "worker-evidence.py", "finish", evidence,
        "succeeded", "done", "0", "--execution-evidence", execution_path,
    ], env=dict(os.environ))
    check(finished.returncode == 0, "legitimate strict evidence finish succeeds")
    terminal_bytes = evidence.read_bytes()
    immutable = run_command([
        PYTHON, ROOT / "scripts" / "worker-evidence.py", "heartbeat", evidence, "2000000000",
    ], env=dict(os.environ))
    check(immutable.returncode != 0 and
          b"terminal run metadata is immutable" in immutable.stderr and
          evidence.read_bytes() == terminal_bytes,
          "terminal run metadata is immutable")


def run_worker_plan_sweep(scratch: Path) -> None:
    worker_root = scratch / "worker-root"
    (worker_root / "scripts").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "worker-sandbox.sh", worker_root / "scripts" / "worker-sandbox.sh")
    shutil.copy2(ROOT / "scripts" / "phase5_safety.py", worker_root / "scripts" / "phase5_safety.py")
    shutil.copy2(ROOT / "scripts" / "provider-egress-profiles.json",
                 worker_root / "scripts" / "provider-egress-profiles.json")
    engines = worker_root / "scripts" / "engines"
    engines.mkdir()
    manifest = json.loads((ROOT / "scripts" / "engines" / "cursor.json").read_text(encoding="utf-8"))
    manifest["name"] = "sampleeng"
    write(engines / "sampleeng.json", json.dumps(manifest).encode("utf-8"))
    subprocess.run(["git", "init", "-q", "-b", "main", str(worker_root)], check=True)
    subprocess.run(["git", "-C", str(worker_root), "config", "core.autocrlf", "false"], check=True)
    subprocess.run(["git", "-C", str(worker_root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(worker_root), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-qm", "controller"], check=True)
    controller_sha = subprocess.check_output(
        ["git", "-C", str(worker_root), "rev-parse", "HEAD"], text=True,
    ).strip()
    policy_files = {
        "scripts/engines/sampleeng.json": hashlib.sha256(
            (engines / "sampleeng.json").read_bytes()
        ).hexdigest(),
        "scripts/provider-egress-profiles.json": hashlib.sha256(
            (worker_root / "scripts" / "provider-egress-profiles.json").read_bytes()
        ).hexdigest(),
    }
    worktree = worker_root / "worktree"
    worktree.mkdir()
    for label, raw in HOSTILE_JSON:
        plan = scratch / f"plan-{label}.json"
        write(plan, raw)
        result = run_command([
            BASH, worker_root / "scripts" / "worker-sandbox.sh", "--engine", "sampleeng",
            "--engine-plan", plan, "--worktree", worktree, "--prompt", "prompt",
            "--model", "model", "--network-policy", "none",
        ], env=dict(os.environ, RECURSION_ROOT=str(worker_root), RECURSION_PYTHON=str(PYTHON),
                    RECURSION_TEST_WORKER="logical"))
        if b"CreateFileMapping" in result.stderr and b"Win32 error 5" in result.stderr:
            print("ok - worker plan battery skipped because Git Bash hit the documented CreateFileMapping ACL artifact")
            return
        check(result.returncode == 92 and b"refusal=invalid-engine-plan" in result.stderr,
              f"worker plan parser refuses {label} with a typed plan refusal")

    positive_plan = {
        "schema_version": 1, "engine": "sampleeng", "executable": "true",
        "argv": ["{{EXE}}", "{{PROMPT}}"], "model_required": False,
        "model_argv_suffix": [], "env_passthrough": [],
        "billing": {"basis": "local", "provider": "sentry-local"},
        "network": {"policy": "none", "profile": "sentry-local", "endpoints": []},
        "authority": {"controller_repository": str(worker_root),
                       "controller_sha": controller_sha, "policy_files": policy_files},
    }
    positive_path = scratch / "plan-positive.json"
    write(positive_path, json.dumps(positive_plan).encode("utf-8"))
    positive = run_command([
        BASH, worker_root / "scripts" / "worker-sandbox.sh", "--engine", "sampleeng",
        "--engine-plan", positive_path, "--worktree", worktree, "--prompt", "prompt",
        "--model", "model", "--network-policy", "none",
    ], env=dict(os.environ, RECURSION_ROOT=str(worker_root), RECURSION_PYTHON=str(PYTHON),
                RECURSION_TEST_WORKER="logical"))
    check(positive.returncode == 0 and b"refusal=invalid-engine-plan" not in positive.stderr,
          "well-formed worker engine plan succeeds in the same fixture")


def run_differential() -> None:
    strict_types = jsonschema.Draft7Validator.TYPE_CHECKER.redefine(
        "integer", lambda _checker, value: isinstance(value, int) and not isinstance(value, bool)
    )
    strict_validator = jsonschema.validators.extend(
        jsonschema.Draft7Validator, type_checker=strict_types
    )
    validator = strict_validator(SCHEMA)
    base = json.loads((ROOT / "scripts" / "engines" / "cursor.json").read_text(encoding="utf-8"))
    base["name"] = "sampleeng"
    deep_value: list[object] = []
    for _ in range(140):
        deep_value = [deep_value]
    candidate_values: list[object] = [
        True, False, 1.0, -1, 10**1000, float("inf"), float("nan"), "", [], {}, None, deep_value, [[]]
    ]
    fields = tuple(base)
    mismatches: list[str] = []
    schema_only: list[str] = []
    runtime_only: list[str] = []
    cases: list[tuple[str, dict]] = [("baseline", base)]
    for field in fields:
        for index, candidate in enumerate(candidate_values):
            mutated = copy.deepcopy(base)
            mutated[field] = candidate
            cases.append((f"{field}[{index}]", mutated))
    both_layout = copy.deepcopy(base)
    both_layout["runtime_layout"] = {
        "mode": "sibling-tree", "source": "executable-directory", "root": "executable-directory",
        "target": ".runtime", "entrypoint": "cursor-agent",
    }
    cases.append(("runtime_layout.both-source-root", both_layout))
    builtin = copy.deepcopy(base)
    builtin["name"] = "claude"
    cases.append(("builtin-name", builtin))

    # Exercise every reviewed provider/profile branch, including the order-insensitive
    # two-endpoint profiles and the exact no-egress local branch.  These are positive
    # corpus members: a schema/runtime mismatch here is a regression even when all the
    # hostile mutations are refused.
    provider_variants = (
        ("anthropic", "anthropic-claude-code", ["api.anthropic.com"],
         ["ANTHROPIC_API_KEY"], "provider-only", "flat-subscription"),
        ("cursor", "cursor", ["api.cursor.com", "api2.cursor.sh"],
         [], "provider-only", "metered"),
        ("gemini", "google-gemini", ["generativelanguage.googleapis.com"],
         ["GEMINI_API_KEY"], "provider-only", "metered"),
        ("openrouter", "openrouter-via-opencode", ["openrouter.ai", "api.deepseek.com"],
         ["OPENROUTER_API_KEY"], "provider-only", "metered"),
        ("sentry-local", "sentry-local", [], [], "none", "local"),
    )
    for profile, provider, endpoints, env_names, policy, basis in provider_variants:
        variant = copy.deepcopy(base)
        variant["billing"] = {"basis": basis, "provider": provider}
        variant["network"] = {"policy": policy, "profile": profile, "endpoints": list(endpoints)}
        variant["env_passthrough"] = list(env_names)
        cases.append((f"positive-{profile}", variant))
        if len(endpoints) == 2:
            reversed_variant = copy.deepcopy(variant)
            reversed_variant["network"]["endpoints"] = list(reversed(endpoints))
            cases.append((f"positive-{profile}-reversed-endpoints", reversed_variant))

    def schema_accepts(value: dict) -> bool:
        try:
            return not list(validator.iter_errors(value))
        except (ValueError, TypeError, OverflowError, RecursionError, UnicodeDecodeError):
            # jsonschema's diagnostic formatter can itself inspect hostile huge
            # integers.  That is a schema refusal, never a corpus-test traceback.
            return False

    for label, value in cases:
        schema_ok = schema_accepts(value)
        try:
            resolver.validate_manifest(value, "sampleeng")
        except resolver.ManifestError:
            runtime_ok = False
        except Exception as exc:  # differential harness must also catch raw boundary leaks
            raise AssertionError(f"runtime leaked {type(exc).__name__} in {label}") from exc
        else:
            runtime_ok = True
        if schema_ok != runtime_ok:
            mismatches.append(f"{label}: schema={schema_ok} runtime={runtime_ok}")
            if schema_ok:
                schema_only.append(label)
            else:
                runtime_only.append(label)
    if mismatches:
        print("schema/runtime mismatches:\n" + "\n".join(mismatches))
    print(f"schema/runtime numeric parity: schema_only={len(schema_only)} runtime_only={len(runtime_only)}")
    check(not schema_only and not runtime_only,
          "schema/runtime numeric parity has zero mismatches in both directions")
    check(not mismatches, "schema/runtime differential corpus has zero mismatches")
    check(schema_accepts(base), "schema accepts the positive differential baseline")
    resolver.validate_manifest(base, "sampleeng")
    print("ok - runtime accepts the positive differential baseline")


def main() -> int:
    supplied = os.environ.get("PHASE5_SWEEP_ROOT", "").strip()
    owned = not supplied
    if supplied:
        scratch = Path(supplied)
        scratch.mkdir(parents=True, exist_ok=True)
    else:
        # The Windows image denies access to directories created by tempfile's
        # TemporaryDirectory/mkdtemp helpers.  Own one explicit directory under the
        # system temp root instead, and remove only that exact directory below.
        scratch = Path(tempfile.gettempdir()) / f"codex-phase5-boundary-{secrets.token_hex(8)}"
        scratch.mkdir()
    try:
        run_json_cli_sweep(scratch)
        run_path_sweep(scratch)
        run_sidecar_battery(scratch)
        run_worker_plan_sweep(scratch)
        run_differential()
    finally:
        if owned:
            shutil.rmtree(scratch, ignore_errors=True)
    print("phase5-boundary-sweep.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

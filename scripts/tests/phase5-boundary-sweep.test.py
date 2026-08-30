#!/usr/bin/env python3
"""Hostile input, path, sidecar, and schema/runtime differential sweep for Phase 5."""

from __future__ import annotations

import copy
import ast
import hashlib
import importlib.util
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
import types
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - supplied by the Phase 5 image
    raise SystemExit(f"phase5-boundary-sweep.test: jsonschema is required: {exc}")

ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path(sys.executable)


def discover_bash() -> str | None:
    """Find bash from PATH, then from the Windows installation directories."""
    discovered = shutil.which("bash")
    if discovered:
        return discovered
    if os.name == "nt":
        for variable in ("ProgramFiles", "ProgramW6432"):
            program_files = os.environ.get(variable, "").strip()
            if not program_files:
                continue
            candidate = Path(program_files) / "Git" / "bin" / "bash.exe"
            if candidate.is_file():
                return str(candidate)
    return None


BASH = discover_bash()
sys.path.insert(0, str(ROOT / "scripts"))

import assignment_contract
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
    except (assignment_contract.AssignmentError, phase5_safety.BoundaryError,
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

# Every controller path whose raw materialized bytes are compared with a Git blob
# in this phase.  The engine path is a template: git check-attr applies the same
# committed glob to a concrete future engine name.
CONTROLLER_BYTE_AUTHENTICATED_PATHS = (
    "scripts/resolve-engine.py",
    "scripts/validate-gate.py",
    "scripts/provider-egress-profiles.json",
    "scripts/capacity-pools.json",
    "scripts/engines/{engine}.json",
)


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
        check(str(engine_path).encode() not in engine_result.stderr,
              f"resolve-engine refusal for {label} does not disclose its absolute path")
        check(b'codec can\'t decode' not in engine_result.stderr
              and b'Errno' not in engine_result.stderr,
              f'resolve-engine refusal for {label} does not disclose raw OS text')

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
            expect_typed(lambda: assignment_contract.load_assignment(run_path), f"assignment loader {label}",
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


def _literal_auth_path(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for item in node.values:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                parts.append(item.value)
            elif isinstance(item, ast.FormattedValue) and isinstance(item.value, ast.Name):
                parts.append('{' + item.value.id + '}')
            else:
                return None
        return ''.join(parts)
    return None


def _has_lf_attribute(relative: str) -> bool:
    result = subprocess.run(
        ["git", "check-attr", "eol", "--", relative], cwd=ROOT,
        capture_output=True, text=True, check=False,
    )
    return result.returncode == 0 and result.stdout.strip().endswith(": eol: lf")


def _normalise_auth_path(value: str) -> str:
    if value == "scripts/engines/{engine}.json":
        return "scripts/engines/*.json"
    return value


def _enumerated_shell_auth_paths(source: Path) -> set[str]:
    """Find shell/embedded-script Git-blob comparisons against live controller bytes.

    Production shell helpers may embed Python, so this intentionally looks for the
    same small semantic shape in both languages: a path variable is used by a Git
    ``show`` call and by a live-file read/comparison in the same helper.
    """
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    assignments: dict[str, set[str]] = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
        if not match:
            continue
        name, expression = match.groups()
        literals = set(re.findall(r"['\"](scripts/[^'\"]+)['\"]", expression))
        if "scripts/engines/" in expression and "engine" in expression:
            literals = {value for value in literals if not value.endswith("/")}
            literals.add("scripts/engines/{engine}.json")
        if literals:
            assignments[name] = literals
    result: set[str] = set()
    for line in text.splitlines():
        is_git_show = bool(re.search(r"\bgit\s+[^#\n]*\bshow\b", line)) \
            or bool(re.search(r"['\"]show['\"]", line))
        if not is_git_show:
            continue
        for name, values in assignments.items():
            if re.search(rf"\b{re.escape(name)}\b", line):
                result.update(values)
        result.update(re.findall(r"(?::|['\"])(scripts/[^'\"\s]+)", line))
    return {_normalise_auth_path(value) for value in result
            if value.startswith("scripts/")}


def _enumerated_controller_paths(extra_shell_sources: tuple[Path, ...] = ()) -> set[str]:
    # This path is deliberate: it names Phase 5's contract module, not Phase 3's execution module.
    sources = (
        ROOT / 'scripts' / 'assignment_contract.py',
        ROOT / 'scripts' / 'resolve-engine.py',
        ROOT / 'scripts' / 'provider-egress.py',
    )
    result: set[str] = set()
    for source in sources:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        assigned: dict[str, set[str]] = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            value = _literal_auth_path(node.value)
            if value is None:
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned.setdefault(target.id, set()).add(value)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id in {'_controller_file_bytes', '_clean_controller_file', 'authenticated_file'} \
                    and len(node.args) >= 3:
                value = _literal_auth_path(node.args[2])
                if value is not None:
                    result.add(value)
                elif isinstance(node.args[2], ast.Name):
                    result.update(assigned.get(node.args[2].id, set()))
        result.update(assigned.get("relative", set()))
    if 'scripts/engines/{engine}.json' in result:
        result.remove('scripts/engines/{engine}.json')
        result.add('scripts/engines/*.json')
    shell_sources = [
        source for source in (ROOT / "scripts").rglob("*.sh")
        if "tests" not in source.relative_to(ROOT / "scripts").parts
        and "audit" not in source.relative_to(ROOT / "scripts").parts
    ]
    for source in (*shell_sources, *extra_shell_sources):
        result.update(_enumerated_shell_auth_paths(source))
    return result


def _assert_controller_paths_pinned(paths: tuple[str, ...]) -> None:
    missing = [relative for relative in paths if not _has_lf_attribute(relative)]
    if missing:
        raise AssertionError("authenticated controller paths are not LF-pinned: " + ", ".join(missing))


def run_controller_authentication_pin_sweep(scratch: Path) -> None:
    """Check the complete byte-vs-blob inventory through Git's attribute engine."""
    enumerated = _enumerated_controller_paths()
    expected = {
        'scripts/engines/*.json' if path == 'scripts/engines/{engine}.json' else path
        for path in CONTROLLER_BYTE_AUTHENTICATED_PATHS
    }
    check(enumerated == expected,
          'byte-authenticated controller call sites are completely enumerated')
    _assert_controller_paths_pinned(tuple(sorted(enumerated)))
    for relative in sorted(enumerated):
        check(True, f"byte-authenticated controller path is pinned LF: {relative}")

    # Mutation proof for this coverage guard: a new embedded shell authenticator is
    # discovered and then fails the pin assertion until its path is pinned.
    future_source = scratch / "future-authenticator.sh"
    future_source.write_text(
        """#!/bin/sh
relative = \"scripts/future-authenticator.json\"
committed = subprocess.run([\"git\", \"-C\", root, \"show\", f\"{sha}:{relative}\"])
live = read_bytes(Path(root) / relative)
if live != committed.stdout:
    raise SystemExit(1)
""",
        encoding="utf-8",
    )
    future_unpinned = "scripts/future-authenticator.json"
    mutated = _enumerated_controller_paths((future_source,))
    check(future_unpinned in mutated,
          "shell authenticator discovery sees a newly added embedded byte comparison")
    try:
        _assert_controller_paths_pinned(tuple(sorted(mutated)))
    except AssertionError as exc:
        check(future_unpinned in str(exc),
              "byte-authentication pin coverage fails for a newly discovered unpinned shell path")
    else:
        raise AssertionError("byte-authentication pin coverage accepted a newly discovered unpinned shell path")


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
        expect_typed(lambda value=value: assignment_contract._validate_allowed_paths([value]),
                     f"assignment path {label}", "allowed_paths is")

    check(assignment_contract._validate_allowed_paths(["scripts"]) == ["scripts"],
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
            if os.name == "nt":
                profile_junction_result = subprocess.run(
                    ["cmd.exe", "/c", "mklink", "/J", str(profile_path), str(scratch)],
                    capture_output=True,
                )
                if profile_junction_result.returncode == 0:
                    profile_junction = True
                else:
                    print("ok - provider profile reparse battery skipped because link creation is unavailable")
            else:
                print("ok - provider profile reparse battery skipped because symlinks are unavailable on this host")
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
    if os.name == "nt":
        junction = scratch / "junction-source"
        junction_result = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(junction), str(outside_dir)],
            capture_output=True,
        )
        if junction_result.returncode == 0:
            expect_typed(lambda: runtime_layout._safe_source(junction), "Windows junction runtime source", "unavailable")
        else:
            print("ok - junction battery skipped because junction creation is unavailable")
    else:
        print("ok - Windows junction battery skipped on non-Windows host")

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

    missing_source = scratch / "missing-runtime-source"
    missing_runtime = run_command([
        PYTHON, ROOT / "scripts" / "runtime-layout.py", "stage",
        "--source", missing_source, "--destination", scratch / "missing-runtime-destination",
    ])
    check(missing_runtime.returncode == 2 and str(missing_source).encode() not in missing_runtime.stderr,
          "missing runtime staging refuses without disclosing the absolute source path")


def run_publication_race_probe(scratch: Path) -> None:
    """Make a concurrent creator appear at the final POSIX publication check."""
    target = scratch / "publication-race-target"
    target.parent.mkdir(parents=True, exist_ok=True)
    target_absolute = os.path.abspath(os.fspath(target))
    real_lstat = phase5_safety.os.lstat
    lstat_calls = 0

    def race_lstat(path):
        nonlocal lstat_calls
        if os.path.abspath(os.fspath(path)) == target_absolute:
            lstat_calls += 1
            if lstat_calls == 2:
                target.write_bytes(b"concurrent creator")
        return real_lstat(path)

    phase5_safety.os.lstat = race_lstat
    try:
        try:
            phase5_safety.atomic_write(target, b"new publication", label="race output")
        except phase5_safety.BoundaryError as exc:
            check("changed before publication" in str(exc),
                  "publication race is refused at the point of use")
        else:
            raise AssertionError("publication race was accepted")
    finally:
        phase5_safety.os.lstat = real_lstat
        try:
            target.unlink()
        except FileNotFoundError:
            pass


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
        "gate_digest": hashlib.sha256(assignment_contract.canonical_bytes(gate_contract)).hexdigest(),
        "gate_contract": gate_contract,
        "role_assignments": {"implementer": role, "verifier": dict(role)},
        "publication_policy": "verified-integration-only",
    }
    return source, controller, value, controller_sha


def run_resolver_symbolic_refusal_sweep(scratch: Path) -> None:
    source, controller, _, controller_sha = make_assignment_fixture(scratch)
    _ = source
    env = dict(
        os.environ,
        RECURSION_ROOT=str(controller),
        RECURSION_ENGINE_PLUGINS="1",
        RECURSION_ENGINE_CURSOR_ENABLED="1",
    )
    hostile_name = str(controller / "leak")
    invalid_name = run_command([
        PYTHON, ROOT / "scripts" / "resolve-engine.py", hostile_name, "--validate",
    ], env=env)
    check(invalid_name.returncode == 2
          and b"refusal=invalid-engine-name" in invalid_name.stderr
          and hostile_name.encode() not in invalid_name.stderr,
          "invalid engine refusal is symbolic and does not disclose caller input")

    output_path = controller / "scripts"
    publication = run_command([
        PYTHON, ROOT / "scripts" / "resolve-engine.py", "cursor", "--role", "implementer",
        "--emit-plan", output_path, "--controller-root", controller,
        "--controller-commit", controller_sha,
    ], env=env)
    check(publication.returncode == 2
          and b"refusal=plan-publication-failed" in publication.stderr
          and str(output_path).encode() not in publication.stderr,
          "plan publication refusal is symbolic and does not disclose its absolute target")

    valid_output = scratch / "resolver-positive-plan.json"
    legitimate = run_command([
        PYTHON, ROOT / "scripts" / "resolve-engine.py", "cursor", "--role", "implementer",
        "--emit-plan", valid_output, "--controller-root", controller,
        "--controller-commit", controller_sha,
    ], env=env)
    check(legitimate.returncode == 0 and valid_output.is_file(),
          "legitimate authenticated resolver plan publication still succeeds")


def run_sidecar_battery(scratch: Path) -> None:
    source, controller, value, _ = make_assignment_fixture(scratch)
    os.environ["RECURSION_ROOT"] = str(controller)
    os.environ.pop("RECURSION_EVIDENCE_KEY_FILE", None)
    assignment_path = scratch / "assignment.json"
    assignment_path.write_text(json.dumps(value), encoding="utf-8")
    normalized, digest = assignment_contract.load_assignment(assignment_path)
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
    _, other_digest = assignment_contract.load_assignment(other_assignment)
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


EXPECTED_SCHEMA_ONLY = {
    "schema_version[2]",
    "concurrency_cap[2]",
    "float-availability_probe.timeout_s",
    "float-execution.cancellation.grace_s",
    "float-execution.exit_codes.auth",
}


def _assert_no_runtime_only(runtime_only: list[str]) -> None:
    check(not runtime_only,
          "schema/runtime differential has zero runtime-only cases (runtime is never looser)")


def _assert_expected_schema_only(schema_only: list[str]) -> None:
    check(set(schema_only) == EXPECTED_SCHEMA_ONLY,
          "schema-only cases are exactly the five justified zero-fraction numeric cases")


def _assert_no_new_schema_mismatches(mismatches: list[str]) -> None:
    check(set(label.split(":", 1)[0] for label in mismatches) == EXPECTED_SCHEMA_ONLY,
          "no new unjustified schema/runtime mismatch appeared")


def run_differential() -> None:
    # The stock Draft-7 validator is authoritative.  In Draft-7/2020-12 JSON
    # Schema, 1.0 is an integer because its fractional part is zero; the runtime
    # deliberately has the stricter Python-int contract, which a standard schema
    # cannot express.  A custom integer checker here would mask that safe-direction
    # difference instead of proving parity.
    validator = jsonschema.Draft7Validator(SCHEMA)
    base = json.loads((ROOT / "scripts" / "engines" / "cursor.json").read_text(encoding="utf-8"))
    base["name"] = "sampleeng"
    deep_value: list[object] = []
    for _ in range(140):
        deep_value = [deep_value]
    candidate_values: list[object] = [
        True, False, 1.0, -1, 10**1000, float("inf"), float("nan"), "", [], {}, None, "\n", deep_value, [[]]
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

    # Differential probes for every nested constrained string family. A terminal
    # newline is the important edge: Python fullmatch rejects it while a JSON
    # Schema pattern accepts it unless the schema uses an absolute end anchor.
    terminal_string_cases = (
        ("name", lambda value: value.__setitem__("name", value["name"] + "\n")),
        ("description", lambda value: value.__setitem__("description", value["description"] + "\n")),
        ("executable", lambda value: value.__setitem__("executable", value["executable"] + "\n")),
        ("argv", lambda value: value["argv"].__setitem__(1, value["argv"][1] + "\n")),
        ("model.argv_suffix", lambda value: value["model"]["argv_suffix"].__setitem__(0, value["model"]["argv_suffix"][0] + "\n")),
        ("roles", lambda value: value["roles"].__setitem__(0, value["roles"][0] + "\n")),
        ("billing.basis", lambda value: value["billing"].__setitem__("basis", value["billing"]["basis"] + "\n")),
        ("billing.provider", lambda value: value["billing"].__setitem__("provider", value["billing"]["provider"] + "\n")),
        ("network.policy", lambda value: value["network"].__setitem__("policy", value["network"]["policy"] + "\n")),
        ("network.profile", lambda value: value["network"].__setitem__("profile", value["network"]["profile"] + "\n")),
        ("network.endpoints", lambda value: value["network"]["endpoints"].__setitem__(0, value["network"]["endpoints"][0] + "\n")),
        ("availability_probe.type", lambda value: value["availability_probe"].__setitem__("type", "http\n")),
        ("availability_probe.url_env", lambda value: value["availability_probe"].__setitem__("url_env", "CURSOR_URL\n")),
        ("runtime_layout.mode", lambda value: value["runtime_layout"].__setitem__("mode", value["runtime_layout"]["mode"] + "\n")),
        ("runtime_layout.source", lambda value: value["runtime_layout"].__setitem__("source", "executable-directory\n")),
        ("runtime_layout.root", lambda value: (value["runtime_layout"].pop("source"), value["runtime_layout"].__setitem__("root", "executable-directory\n"))),
        ("runtime_layout.target", lambda value: value["runtime_layout"].__setitem__("target", value["runtime_layout"]["target"] + "\n")),
        ("runtime_layout.entrypoint", lambda value: value["runtime_layout"].__setitem__("entrypoint", value["runtime_layout"]["entrypoint"] + "\n")),
        ("execution.output_format", lambda value: value["execution"].__setitem__("output_format", value["execution"]["output_format"] + "\n")),
        ("execution.cancellation.signal", lambda value: value["execution"]["cancellation"].__setitem__("signal", value["execution"]["cancellation"]["signal"] + "\n")),
        ("auth.mode", lambda value: value["auth"].__setitem__("mode", value["auth"]["mode"] + "\n")),
        ("auth.marker", lambda value: value["auth"].__setitem__("marker", value["auth"]["marker"] + "\n")),
        ("env_passthrough", lambda value: value.__setitem__("env_passthrough", ["GEMINI_API_KEY\n"])),
    )
    for label, mutate in terminal_string_cases:
        mutated = copy.deepcopy(base)
        if mutated.get("availability_probe") is None and label.startswith("availability_probe"):
            mutated["availability_probe"] = {"type": "http", "url_env": "CURSOR_URL", "timeout_s": 5}
        mutate(mutated)
        cases.append((f"terminal-{label}", mutated))

    # Probe every integer field.  The five expected schema-only cases below are
    # deliberately retained as an explicit, justified exception: they are JSON
    # numbers with zero fractional part and are therefore inexpressible as a
    # standard-schema rejection.  Every schema-only case must remain in this list,
    # and every runtime-only case remains a hard failure.
    numeric_cases: list[tuple[str, dict]] = []
    probe_numeric = copy.deepcopy(base)
    probe_numeric["availability_probe"] = {"type": "http", "url_env": "CURSOR_URL", "timeout_s": 1.0}
    numeric_cases.append(("float-availability_probe.timeout_s", probe_numeric))
    grace_numeric = copy.deepcopy(base)
    grace_numeric["execution"]["cancellation"]["grace_s"] = 1.0
    numeric_cases.append(("float-execution.cancellation.grace_s", grace_numeric))
    for category in ("success", "auth", "runtime", "egress"):
        exit_numeric = copy.deepcopy(base)
        exit_numeric["execution"]["exit_codes"][category][0] = 1.0
        numeric_cases.append((f"float-execution.exit_codes.{category}", exit_numeric))
    cases.extend(numeric_cases)

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
    print(f"schema/runtime differential corpus: cases={len(cases)} "
          f"schema_only={len(schema_only)} runtime_only={len(runtime_only)}")
    _assert_no_runtime_only(runtime_only)
    _assert_expected_schema_only(schema_only)
    _assert_no_new_schema_mismatches(mismatches)
    check(schema_accepts(base), "schema accepts the positive differential baseline")
    resolver.validate_manifest(base, "sampleeng")
    print("ok - runtime accepts the positive differential baseline")


def _module_mutant(scratch: Path, label: str, source_path: Path, old: str, new: str):
    original = source_path.read_text(encoding="utf-8")
    if original.count(old) != 1:
        raise AssertionError(f"mutation target for {label} was not unique")
    mutated_source = original.replace(old, new, 1)
    mutant_path = scratch / f"mutation-{label}.py"
    mutant_path.write_text(mutated_source, encoding="utf-8")
    module = types.ModuleType(f"phase5_mutant_{label}")
    module.__file__ = str(source_path.resolve())
    module.__name__ = f"phase5_mutant_{label}"
    module._MUTATION_SOURCE = mutated_source
    exec(compile(mutated_source, str(mutant_path), "exec"), module.__dict__)
    return module, mutant_path


def _boundary_mutant(scratch: Path, label: str, old: str, new: str):
    return _module_mutant(scratch, label, Path(__file__), old, new)


class MutationSkipped(Exception):
    """A mutation oracle is unavailable on the current platform."""


def _kill_mutation(rows: list[dict[str, str]], guard: str, mutated_file: str,
                   failing_case: str, original_case, mutant_case) -> None:
    """Run one mutation as an individual test; a surviving mutant is a defect."""
    try:
        original_case()
    except MutationSkipped as exc:
        rows.append({
            "guard": guard,
            "mutated": mutated_file,
            "case": failing_case,
            "assertion": f"SKIP - {exc}",
        })
        print(f"ok - individual mutation skipped: {guard} ({exc})")
        return
    except AssertionError as exc:
        raise AssertionError(f"mutation oracle failed for {guard}: {exc}") from exc
    try:
        mutant_case()
    except AssertionError as exc:
        rows.append({
            "guard": guard,
            "mutated": mutated_file,
            "case": failing_case,
            "assertion": str(exc),
        })
        print(f"ok - individual mutation killed: {guard}")
    else:
        raise AssertionError(
            f"mutation survived for {guard}; zero failures for {mutated_file} "
            f"on {failing_case}"
        )


def _resolver_mutant(scratch: Path, label: str, old: str, new: str) -> Path:
    original = (ROOT / "scripts" / "resolve-engine.py").read_text(encoding="utf-8")
    if original.count(old) != 1:
        raise AssertionError(f"resolver mutation target for {label} was not unique")
    mutant_scripts = scratch / f"mutation-resolver-{label}" / "scripts"
    mutant_scripts.mkdir(parents=True, exist_ok=True)
    mutant_path = mutant_scripts / "resolve-engine.py"
    mutant_path.write_text(original.replace(old, new, 1), encoding="utf-8")
    shutil.copy2(ROOT / "scripts" / "phase5_safety.py", mutant_scripts / "phase5_safety.py")
    return mutant_path


def _remove_mutation_tree(path: Path) -> None:
    if not path.exists():
        return
    for child in sorted(path.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if child.is_dir():
            try:
                os.chmod(child, 0o700)
            except OSError:
                pass
    shutil.rmtree(path, ignore_errors=True)


def run_individual_guard_mutations(scratch: Path) -> None:
    """Individually kill every meaningful Phase 5 guard added in this round.

    The composite sweeps above establish the normal contract.  These probes mutate
    one guard at a time in a scratch copy and then run the focused negative case that
    must fail.  This keeps a vacuous composite assertion from counting as proof.
    """
    scratch.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    boundary_source = Path(__file__).resolve().relative_to(ROOT).as_posix()
    boundary_text = Path(__file__).read_text(encoding="utf-8")
    resolver_text = (ROOT / "scripts" / "resolve-engine.py").read_text(encoding="utf-8")
    runtime_text = (ROOT / "scripts" / "runtime-layout.py").read_text(encoding="utf-8")

    def line_of(text: str, needle: str) -> str:
        return f"{boundary_source}:{text.splitlines().index(needle) + 1}"

    def containing_line(text: str, needle: str, path: str) -> str:
        return f"{path}:{next(index for index, line in enumerate(text.splitlines(), 1) if needle in line)}"

    def differential_case(function_name: str, argument, message: str) -> None:
        def case(module) -> None:
            try:
                getattr(module, function_name)(argument)
            except AssertionError:
                return
            raise AssertionError(message)
        return case

    runtime_old = "    check(not runtime_only,\n"
    runtime_new = "    check(True,\n"
    runtime_mutant, _ = _boundary_mutant(scratch, "runtime-only", runtime_old, runtime_new)
    runtime_line = line_of(boundary_text, runtime_old.rstrip("\n"))
    runtime_case = differential_case(
        "_assert_no_runtime_only", ["synthetic-runtime-only"],
        "runtime-only differential case was accepted",
    )
    _kill_mutation(
        rows, "stock differential runtime_only==0", runtime_line,
        "synthetic runtime-only schema mismatch", lambda: runtime_case(sys.modules[__name__]),
        lambda: runtime_case(runtime_mutant),
    )

    schema_old = "    check(set(schema_only) == EXPECTED_SCHEMA_ONLY,\n"
    schema_new = "    check(True,\n"
    schema_mutant, _ = _boundary_mutant(scratch, "schema-only", schema_old, schema_new)
    schema_line = line_of(boundary_text, schema_old.rstrip("\n"))
    schema_case = differential_case(
        "_assert_expected_schema_only", ["unexpected-schema-only"],
        "new unjustified schema-only case was accepted",
    )
    _kill_mutation(
        rows, "stock differential schema_only enumeration", schema_line,
        "synthetic unjustified schema-only mismatch", lambda: schema_case(sys.modules[__name__]),
        lambda: schema_case(schema_mutant),
    )

    mismatch_old = "    check(set(label.split(\":\", 1)[0] for label in mismatches) == EXPECTED_SCHEMA_ONLY,\n"
    mismatch_new = "    check(True,\n"
    mismatch_mutant, _ = _boundary_mutant(scratch, "new-mismatch", mismatch_old, mismatch_new)
    mismatch_line = line_of(boundary_text, mismatch_old.rstrip("\n"))
    mismatch_case = differential_case(
        "_assert_no_new_schema_mismatches", ["unexpected-case: schema=True runtime=False"],
        "new unjustified schema/runtime mismatch was accepted",
    )
    _kill_mutation(
        rows, "stock differential new-mismatch guard", mismatch_line,
        "synthetic new schema/runtime mismatch", lambda: mismatch_case(sys.modules[__name__]),
        lambda: mismatch_case(mismatch_mutant),
    )

    future_source = scratch / "mutation-future-authenticator.sh"
    future_source.write_text(
        "relative = \"scripts/future-authenticator.json\"\n"
        "committed = subprocess.run([\"git\", \"show\", relative])\n"
        "live = read_bytes(Path(root) / relative)\n"
        "if live != committed.stdout: raise SystemExit(1)\n",
        encoding="utf-8",
    )
    future_path = "scripts/future-authenticator.json"
    discovery_old = "        result.update(_enumerated_shell_auth_paths(source))\n"
    discovery_new = "        pass\n"
    discovery_mutant, _ = _boundary_mutant(scratch, "shell-discovery", discovery_old, discovery_new)
    discovery_line = line_of(boundary_text, discovery_old.rstrip("\n"))

    def shell_discovery_case(module) -> None:
        if future_path not in module._enumerated_controller_paths((future_source,)):
            raise AssertionError("new embedded shell authenticator was not discovered")

    _kill_mutation(
        rows, "shell authenticator discovery", discovery_line,
        future_path, lambda: shell_discovery_case(sys.modules[__name__]),
        lambda: shell_discovery_case(discovery_mutant),
    )

    pin_old = (
        "def _assert_controller_paths_pinned(paths: tuple[str, ...]) -> None:\n"
        "    missing = [relative for relative in paths if not _has_lf_attribute(relative)]\n"
        "    if missing:\n"
        "        raise AssertionError(\"authenticated controller paths are not LF-pinned: \" + \", \".join(missing))\n"
    )
    pin_new = "def _assert_controller_paths_pinned(paths: tuple[str, ...]) -> None:\n    return\n"
    pin_mutant, _ = _boundary_mutant(scratch, "pin-coverage", pin_old, pin_new)
    pin_line = line_of(boundary_text, "    missing = [relative for relative in paths if not _has_lf_attribute(relative)]")

    def pin_case(module) -> None:
        try:
            module._assert_controller_paths_pinned((future_path,))
        except AssertionError:
            return
        raise AssertionError("new unpinned authenticated path was accepted")

    _kill_mutation(
        rows, "authenticated-path LF pin coverage", pin_line,
        future_path, lambda: pin_case(sys.modules[__name__]),
        lambda: pin_case(pin_mutant),
    )

    mutation_fixture = scratch / "mutation-fixture"
    mutation_fixture.mkdir(parents=True, exist_ok=True)
    _, mutation_controller, _, mutation_controller_sha = make_assignment_fixture(mutation_fixture)
    resolver_env = dict(
        os.environ, RECURSION_ROOT=str(mutation_controller),
        RECURSION_ENGINE_PLUGINS="1", RECURSION_ENGINE_CURSOR_ENABLED="1",
    )
    hostile_name = str(mutation_controller / "mutation-caller-controlled-name")
    invalid_old = "        diag(REFUSAL_INVALID_ENGINE_NAME)\n"
    invalid_new = "        diag(f\"invalid engine name {engine!r}\")\n"
    invalid_mutant = _resolver_mutant(scratch, "invalid-name", invalid_old, invalid_new)
    invalid_line = containing_line(resolver_text, invalid_old.strip(), "scripts/resolve-engine.py")

    def invalid_case(path: Path) -> None:
        result = subprocess.run(
            [PYTHON, path, hostile_name, "--validate"],
            cwd=ROOT, env=resolver_env, capture_output=True,
        )
        if result.returncode != 2 or hostile_name.encode() in result.stderr \
                or b"invalid engine name" in result.stderr:
            raise AssertionError("invalid engine refusal disclosed caller-controlled path")

    _kill_mutation(
        rows, "invalid-engine symbolic refusal", invalid_line,
        hostile_name, lambda: invalid_case(ROOT / "scripts" / "resolve-engine.py"),
        lambda: invalid_case(invalid_mutant),
    )

    publication_old = "        diag(REFUSAL_PLAN_PUBLICATION)\n"
    publication_new = "        diag(f\"failed to write plan to {out_path}: publication error\")\n"
    publication_mutant = _resolver_mutant(scratch, "plan-publication", publication_old, publication_new)
    publication_line = containing_line(resolver_text, publication_old.strip(), "scripts/resolve-engine.py")
    publication_target = mutation_controller / "scripts"

    def publication_case(path: Path) -> None:
        result = subprocess.run(
            [PYTHON, path, "cursor", "--role", "implementer", "--emit-plan", publication_target,
             "--controller-root", mutation_controller, "--controller-commit", mutation_controller_sha],
            cwd=ROOT, env=resolver_env, capture_output=True,
        )
        if result.returncode != 2 or str(publication_target).encode() in result.stderr:
            raise AssertionError("plan publication refusal disclosed caller-controlled path")

    _kill_mutation(
        rows, "plan-publication symbolic refusal", publication_line,
        str(publication_target), lambda: publication_case(ROOT / "scripts" / "resolve-engine.py"),
        lambda: publication_case(publication_mutant),
    )

    private_old = "os.mkdir(os.path.basename(str(destination)), 0o700, dir_fd=destination_parent_fd)"
    private_new = "os.mkdir(os.path.basename(str(destination)), 0o755, dir_fd=destination_parent_fd)"
    private_mutant, _ = _module_mutant(
        scratch, "private-staging", ROOT / "scripts" / "runtime-layout.py", private_old, private_new,
    )
    private_line = containing_line(runtime_text, private_old, "scripts/runtime-layout.py")

    def private_staging_case(module) -> None:
        source = scratch / f"private-source-{secrets.token_hex(4)}"
        destination = scratch / f"private-destination-{secrets.token_hex(4)}"
        if os.name == "nt":
            raise MutationSkipped(
                "POSIX directory modes do not seal the staging window on Windows"
            )
        source.mkdir()
        (source / "payload").write_bytes(b"payload\n")
        observed: list[int] = []
        real_chmod = module.chmod_directory

        def observe(path, mode):
            if Path(path) == destination and not observed:
                # This hook runs immediately before the root's first child is
                # published.  Neutralize the host umask so a 0755 mutant cannot
                # be silently narrowed to 0700 and survive the oracle.
                observed.append(stat.S_IMODE(os.lstat(path).st_mode))
            real_chmod(path, mode)

        previous_umask = os.umask(0)
        module.chmod_directory = observe
        try:
            module._copy_tree(source, destination)
        finally:
            module.chmod_directory = real_chmod
            os.umask(previous_umask)
            _remove_mutation_tree(destination)
            _remove_mutation_tree(source)
        if not observed:
            raise AssertionError("first-child publication hook did not observe the runtime destination")
        if observed[0] != 0o700:
            raise AssertionError(
                f"runtime destination was not owner-only before first child publication "
                f"(mode={oct(observed[0])})"
            )

    _kill_mutation(
        rows, "owner-only private runtime staging", private_line,
        "destination mode before first child publication", lambda: private_staging_case(runtime_layout),
        lambda: private_staging_case(private_mutant),
    )

    final_old = "        source_after_lock = _tree_snapshot(source)\n"
    final_new = "        source_after_lock = source_after_copy\n"
    final_mutant, _ = _module_mutant(
        scratch, "post-lock-scan", ROOT / "scripts" / "runtime-layout.py", final_old, final_new,
    )
    final_line = containing_line(runtime_text, final_old.strip(), "scripts/runtime-layout.py")

    def final_scan_case(module) -> None:
        source = scratch / f"final-source-{secrets.token_hex(4)}"
        destination = scratch / f"final-destination-{secrets.token_hex(4)}"
        source.mkdir()
        payload = source / "payload"
        payload.write_bytes(b"original\n")
        real_snapshot = module._tree_snapshot
        source_snapshots = 0
        changed = False

        def tampering_snapshot(path):
            nonlocal source_snapshots, changed
            result = real_snapshot(path)
            if Path(path) == source:
                source_snapshots += 1
                if source_snapshots == 2 and not changed:
                    payload.write_bytes(b"tampered-after-publication\n")
                    changed = True
            return result

        module._tree_snapshot = tampering_snapshot
        try:
            try:
                module._copy_tree(source, destination)
            except module.LayoutError:
                return
        finally:
            module._tree_snapshot = real_snapshot
            _remove_mutation_tree(destination)
            _remove_mutation_tree(source)
        raise AssertionError("post-lock source mutation was accepted by the final scan")

    _kill_mutation(
        rows, "post-lock completeness and identity scan", final_line,
        "source mutation after child publication", lambda: final_scan_case(runtime_layout),
        lambda: final_scan_case(final_mutant),
    )

    if len(rows) != 9:
        raise AssertionError(f"individual mutation table is incomplete: {len(rows)} rows, expected 9")
    print("individual guard mutation table:")
    for row in rows:
        print("  " + " | ".join(f"{key}={value}" for key, value in row.items()))


def main() -> int:
    if BASH is None or not Path(BASH).is_file():
        print("SKIP - bash interpreter was not discoverable on PATH or via ProgramFiles/ProgramW6432 (exit 77)")
        return 77
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
        run_controller_authentication_pin_sweep(scratch)
        run_resolver_symbolic_refusal_sweep(scratch)
        run_path_sweep(scratch)
        run_publication_race_probe(scratch)
        run_sidecar_battery(scratch)
        run_worker_plan_sweep(scratch)
        run_differential()
        run_individual_guard_mutations(scratch)
    finally:
        if owned:
            shutil.rmtree(scratch, ignore_errors=True)
    print("phase5-boundary-sweep.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

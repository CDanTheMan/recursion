#!/usr/bin/env python3
"""Phase 2 class sweep: hostile boundaries, schema/runtime parity, and positive paths."""

from __future__ import annotations

import hashlib
import hmac
import importlib.util
import itertools
import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import jsonschema


SOURCE = Path(__file__).parents[2]
PYTHON = sys.executable
SCRATCH_BASE = Path(os.environ.get(
    "RECURSION_PHASE2_SCRATCH",
    r"C:\Users\Lucas\AppData\Local\Temp\codex-w2c-2d5c9f",
))
GATE = SOURCE / "scripts" / "validate-gate.py"
SCHEMA_PATH = SOURCE / "schemas" / "control-plane" / "v2" / "repository-contract.schema.json"
_STRICT_INTEGER_TYPES = jsonschema.Draft202012Validator.TYPE_CHECKER.redefine(
    "integer", lambda _checker, instance: type(instance) is int)
StrictDraft202012Validator = jsonschema.validators.extend(
    jsonschema.Draft202012Validator, type_checker=_STRICT_INTEGER_TYPES)


def load_gate_module():
    spec = importlib.util.spec_from_file_location("phase2_validate_gate", GATE)
    if spec is None or spec.loader is None:
        raise AssertionError("validate-gate module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_process(args: list[str], *, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, input=input_bytes, capture_output=True, check=False)


class Phase2BoundarySweep(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        SCRATCH_BASE.mkdir(parents=True, exist_ok=True)
        cls.root = SCRATCH_BASE / f"phase2-sweep-{uuid.uuid4().hex}"
        cls.root.mkdir()
        cls.repo = cls.root / "repo"
        cls.repo.mkdir()
        cls.key = cls.root / "controller.key"
        cls.key.write_text("sweep-controller-key\n", encoding="utf-8")
        os.chmod(cls.key, 0o600)

    @classmethod
    def tearDownClass(cls) -> None:
        # Git's Windows object store may retain host-denied mappings after worktree cleanup.  This
        # is cleanup of this test's uniquely-created scratch directory only, never a test result.
        shutil.rmtree(cls.root, ignore_errors=True)

    def setUp(self) -> None:
        sys.path.insert(0, str(SOURCE / "scripts"))
        import repository_contract as rc
        self.rc = rc
        self.old_key = rc.CONTROLLER_KEY_PATH
        rc.CONTROLLER_KEY_PATH = self.key

    def tearDown(self) -> None:
        self.rc.CONTROLLER_KEY_PATH = self.old_key

    def descriptor(self, **updates: object) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": 1,
            "id": "phase2-sweep",
            "repo": str(self.repo),
            "default_branch": "main",
            "integration_branch": "recursion/integration",
            "task_branch_pattern": "recursion/task/{task_id}",
            "external_branch_patterns": ["cursor/*", "recursion/extern/*"],
            "publication_policy": "verified-integration-only",
            "source_policy": "exact-sha",
            "allowed_paths": ["src"],
            "gate_commands": ["git diff --check"],
            "eligible_hosts": ["gs-recursion"],
            "eligible_pools": ["local"],
        }
        value.update(updates)
        return value

    def hostile_json_bytes(self) -> list[bytes]:
        deep = "[" * 1100 + "0" + "]" * 1100
        return [
            b"true", b"false", b"1.0", b"999999999999999999999999999999999999999999999999999",
            b"1e999", b"NaN", b"\"\"", b"[]", b"{}", b"null", deep.encode(),
            b"[[]]", b"\xff\xfe\xfd", b"{\"schema_version\": 1}\n",
        ]

    def test_every_json_cli_boundary_is_controlled(self) -> None:
        for index, raw in enumerate(self.hostile_json_bytes()):
            path = self.root / f"hostile-{index}.json"
            path.write_bytes(raw)
            result = run_process([PYTHON, str(SOURCE / "scripts" / "repository_contract.py"),
                                  "validate-project", str(path)])
            with self.subTest(index=index):
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(b"Traceback", result.stderr)

        valid_path = self.root / "valid.json"
        valid_path.write_text(json.dumps(self.descriptor()), encoding="utf-8")
        accepted = run_process([PYTHON, str(SOURCE / "scripts" / "repository_contract.py"),
                                "validate-project", str(valid_path)])
        self.assertEqual(accepted.returncode, 0, accepted.stderr.decode(errors="replace"))

    def test_shared_hostile_matrix_reaches_runtime_entrypoints(self) -> None:
        hostile: list[object] = [True, False, 1.0, 10 ** 200, float("inf"), "", [], {}, None,
                                 [[[]]], [[]]]
        for value in hostile:
            with self.subTest(value=repr(value)):
                with self.assertRaises(self.rc.ContractError):
                    self.rc.validate_project_descriptor(value)  # type: ignore[arg-type]
                with self.assertRaises(self.rc.ContractError):
                    self.rc._candidate_payload(value)  # type: ignore[arg-type]
                with self.assertRaises(self.rc.ContractError):
                    self.rc.admit_task(self.descriptor(), value, self.repo)  # type: ignore[arg-type]
                with self.assertRaises(self.rc.ContractError):
                    self.rc._validate_task_workdir(self.repo, value)  # type: ignore[arg-type]
                self.assertFalse(self.rc._valid_gate_command(value, allowed_paths=["src"]))
                outcome = self.rc.classify_stale_base(
                    self.descriptor(), value, self.repo)  # type: ignore[arg-type]
                self.assertIn(outcome, self.rc.OUTCOMES)
        self.assertEqual(self.rc._valid_gate_command("git diff --check", allowed_paths=["src"]), True)

    def test_gate_cli_hostile_matrix_and_positive_read_only_gate(self) -> None:
        hostile = ["true", "false", "1.0", "999999999999999999999", "1e999", "NaN", "",
                   "[]", "{}", "null", "[[]]", "test -s ../outside", r"test -s \\server\share\x",
                   "test -s C:relative", "test -s ~", "test -s %ENV%", "test -s src/*.txt",
                   "test -s src/[x].txt", "test -s src/result.txt\n"]
        for value in hostile:
            result = run_process([PYTHON, str(GATE), "--acceptance", value, "--strict-direct"])
            with self.subTest(value=value):
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(b"Traceback", result.stderr)
        positive = run_process([PYTHON, str(GATE), "--acceptance", "git diff --check", "--strict-direct"])
        self.assertEqual(positive.returncode, 0, positive.stderr.decode(errors="replace"))
        self.assertEqual(run_process([PYTHON, str(GATE), "--acceptance", "git status --short",
                                      "--strict-direct"]).returncode, 0)
        for command in ("git push", "git fetch", "git reset --hard"):
            result = run_process([PYTHON, str(GATE), "--acceptance", command, "--strict-direct"])
            with self.subTest(command=command):
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(b"Traceback", result.stderr)

    def test_runtime_and_schema_gate_differential_is_zero(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema["properties"]["gate_commands"]["items"])
        corpus = [
            "git diff --check", "git status --short", "git show HEAD", "git ls-files",
            "test -s src/result.txt", "[ -e src/result.txt ]", "test -e src/a && test -s src/b",
            "git diff --check && test -s \"src/result file.txt\"",
            "python3 src/check.py", "bash src/check.sh", "node src/check.js",
            "", "true", "false", "echo ok", "pwd", "python3 -c true", "bash -c true",
             "python3 ../outside.py", "python3 src/../check.py", "test -s /tmp/result.txt",
             r"test -s \\server\share\result.txt", "test -s C:relative", "test -s ~",
            "test -s %ENV%", "test -s src/*.txt", "test -s src/[x].txt",
            "git -C ../other diff --check", "git --git-dir=../other/.git diff",
            "git --work-tree=/tmp diff", "git -c core.hooksPath=/tmp diff",
            "git push", "git fetch", "git reset --hard", "test -s src/a || test -s src/b",
            "test -s src/a; test -s src/b", "test -s src/a &&", "test -s src/a &&& test -s src/b",
        ]
        generated_segments = ["git diff --check", "git status --short", "git show HEAD",
                              "git ls-files", "test -s src/result.txt", "[ -e src/result.txt ]",
                              "python3 src/check.py", "bash src/check.sh", "node src/check.js"]
        generated_operands = ["src/result.txt", "src/check.py", "../outside", "/tmp/result.txt",
                              r"\\server\share\result.txt", "C:relative", "~", "%ENV%",
                              "src/*.txt", "src/[x].txt"]
        corpus.extend(
            f"test -s {operand}" for operand in generated_operands)
        corpus.extend(
            f"{left} && {right}" for left, right in itertools.product(
                generated_segments[:5], generated_segments[4:6]))
        mismatches: list[str] = []
        for command in corpus:
            schema_accepts = validator.is_valid(command)
            runtime_accepts = self.rc._valid_gate_command(
                command, allowed_paths=["src"],
                gate_files=["src/check.py", "src/check.sh", "src/check.js"],
                controller_gate_files=[])
            if schema_accepts != runtime_accepts:
                mismatches.append(command)
        self.assertEqual(mismatches, [], f"schema/runtime gate mismatches: {mismatches}")

    def test_runtime_and_schema_descriptor_differential_is_zero(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = StrictDraft202012Validator(schema)
        cases = [
            self.descriptor(),
            self.descriptor(default_branch="main", integration_branch="main"),
            self.descriptor(external_branch_patterns=["recursion/*"]),
            self.descriptor(allowed_paths=["src//nested"]),
            self.descriptor(gate_commands=["python3 ./src/check.py"]),
            self.descriptor(gate_commands=["python3 src/check.py"]),
            self.descriptor(gate_commands=[r"test -s \\server\share\x"]),
            self.descriptor(eligible_hosts=[True]), self.descriptor(eligible_pools=[1.0]),
            self.descriptor(schema_version=True), self.descriptor(schema_version=1.0),
            self.descriptor(gate_commands=["git diff --check && test -s src/a"]),
        ]
        for gate in ("git status --short", "git show HEAD", "test -s src/result.txt"):
            cases.append(self.descriptor(gate_commands=[gate]))
        cases.extend([
            self.descriptor(
                gate_commands=["python3 src/check.py"],
                required_gate_profile={"acceptance": "python3 src/check.py", "gate_class": "light",
                                       "gate_files": ["src/check.py"], "controller_gate_files": []}),
            self.descriptor(
                gate_commands=["bash src/check.sh"],
                required_gate_profile={"acceptance": "bash src/check.sh", "gate_class": "heavy",
                                       "gate_files": ["src/check.sh"], "controller_gate_files": []}),
        ])
        mismatches: list[tuple[int, bool, bool]] = []
        for index, case in enumerate(cases):
            schema_accepts = not list(validator.iter_errors(case))
            try:
                self.rc.validate_project_descriptor(dict(case))
            except self.rc.ContractError:
                runtime_accepts = False
            else:
                runtime_accepts = True
            if schema_accepts != runtime_accepts:
                mismatches.append((index, schema_accepts, runtime_accepts))
        self.assertEqual(mismatches, [])
        self.assertEqual(validator.is_valid(self.descriptor(schema_version=True)), False)
        self.assertEqual(validator.is_valid(self.descriptor(schema_version=1.0)), False)
        with self.assertRaises(self.rc.ContractError):
            self.rc.validate_project_descriptor(self.descriptor(schema_version=1.0))

    def test_class_a_json_integer_boundary_is_explicit(self) -> None:
        for value in (True, False, 1.0, 1e999, "1", [], {}, None):
            with self.subTest(value=value):
                with self.assertRaises(self.rc.ContractError):
                    self.rc.validate_project_descriptor(self.descriptor(schema_version=value))
        self.rc.validate_project_descriptor(self.descriptor(schema_version=1))

    def test_windows_or_posix_controller_key_positive_and_acl_negative(self) -> None:
        if os.name == "nt":
            account = f"{os.environ.get('USERDOMAIN', '')}\\{os.environ['USERNAME']}"
            acl = run_process(["icacls", str(self.key), "/inheritance:r", "/grant:r", f"{account}:F"])
            if acl.returncode:
                self.skipTest(f"host ACL setup denied: {acl.stderr.decode(errors='replace').strip()}")
        self.assertEqual(self.rc._controller_key(), b"sweep-controller-key")
        self.rc._validate_windows_acl_records("S-1-owner", "S-1-owner", [], True)
        with self.assertRaises(OSError):
            self.rc._validate_windows_acl_records(
                "S-1-owner", "S-1-owner", [("S-1-foreign", 0, 0x001F01FF, 0)], True)
        with self.assertRaises(OSError):
            self.rc._validate_windows_acl_records(
                "S-1-owner", "S-1-owner", [("S-1-foreign", 0x10, 0x001F01FF, 0)], True)

    def test_all_nine_project_configs_still_admit(self) -> None:
        configs = sorted((SOURCE / "state" / "project-config").glob("*.json"))
        self.assertEqual(len(configs), 9)
        for path in configs:
            with self.subTest(path=path.name):
                value = json.loads(path.read_text(encoding="utf-8"))
                self.rc.validate_project_descriptor(value)

    def test_path_sites_reject_reparses_hardlinks_and_swap_identity(self) -> None:
        workdir = self.repo / "src"
        workdir.mkdir()
        self.assertEqual(self.rc._validate_task_workdir(self.repo, "src"), "src")
        with self.assertRaises(self.rc.ContractError):
            self.rc._validate_task_workdir(self.repo, "../outside")
        hardlink = self.root / "hardlink.txt"
        original = self.root / "original.txt"
        original.write_text("gate\n", encoding="utf-8")
        os.link(original, hardlink)
        module = load_gate_module()
        with self.assertRaises(ValueError):
            module._open_verified_file(hardlink)

        swapped = self.root / "swap.txt"
        swapped.write_text("one\n", encoding="utf-8")
        initial = os.lstat(swapped)
        replacement = self.root / "replacement.txt"
        replacement.write_text("two\n", encoding="utf-8")
        swapped.unlink()
        replacement.rename(swapped)
        with self.assertRaises(self.rc.ContractError):
            # A recheck against a previously captured identity must fail closed.
            if not self.rc._same_file(initial, os.lstat(swapped)):
                raise self.rc.ContractError("path identity changed")

        gate_repo = self.root / "gate-repo"
        gate_repo.mkdir()
        run_process(["git", "-C", str(gate_repo), "init", "-q", "-b", "main"])
        (gate_repo / "src").mkdir()
        gate_file = gate_repo / "src" / "check.py"
        gate_file.write_text("print('original')\n", encoding="utf-8")
        run_process(["git", "-C", str(gate_repo), "add", "."])
        run_process(["git", "-C", str(gate_repo), "config", "user.name", "phase2"])
        run_process(["git", "-C", str(gate_repo), "config", "user.email", "phase2@example.invalid"])
        run_process(["git", "-C", str(gate_repo), "commit", "-qm", "gate"])
        module = load_gate_module()
        expected_hash = hashlib.sha256(module.clean_tracked_bytes(gate_repo, "src/check.py")).hexdigest()
        gate_file.write_text("print('swapped')\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            module._execute_from_verified_files(
                "python3 src/check.py", gate_repo, None, ["src/check.py"], [],
                {"src/check.py": expected_hash}, {})

    def test_path_sites_reject_junction_leaf_and_ancestor(self) -> None:
        target = self.root / "junction-target"
        target.mkdir()
        (target / "gate.py").write_text("print('gate')\n", encoding="utf-8")
        junction = self.repo / "junction"
        if os.name == "nt":
            result = run_process(["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(target)])
            if result.returncode:
                self.skipTest(f"junction creation is unavailable on this host: {result.stderr!r}")
        else:
            try:
                junction.symlink_to(target, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"directory reparse fixture is unavailable on this host: {exc}")
        try:
            with self.assertRaises(self.rc.ContractError):
                self.rc._validate_task_workdir(self.repo, "junction")
            with self.assertRaises(self.rc.ContractError):
                self.rc._validate_task_workdir(self.repo, "junction/gate.py")
            module = load_gate_module()
            with self.assertRaises(ValueError):
                with module._pinned_file_parents(junction / "gate.py"):
                    pass
            ledger_junction = self.root / "ledger-junction"
            if os.name == "nt":
                result = run_process(["cmd.exe", "/d", "/c", "mklink", "/J",
                                      str(ledger_junction), str(target)])
                if result.returncode:
                    self.skipTest(f"ledger junction creation is unavailable on this host: {result.stderr!r}")
            else:
                ledger_junction.symlink_to(target, target_is_directory=True)
            with self.assertRaises(self.rc.ContractError):
                with self.rc._pinned_ledger(ledger_junction):
                    pass
            with mock.patch.object(
                    self.rc, "_checked_git",
                    return_value=SimpleNamespace(returncode=0, stdout=str(junction))):
                with self.assertRaises(self.rc.ContractError):
                    self.rc._git_dir(self.repo)
        finally:
            if junction.exists() or junction.is_symlink():
                junction.rmdir()
            ledger_junction = self.root / "ledger-junction"
            if ledger_junction.exists() or ledger_junction.is_symlink():
                ledger_junction.rmdir()

    def test_normal_candidate_import_publish_path_is_bound(self) -> None:
        # This is a real fixture import, including the controller gate and idempotency record.
        # If the host denies Git's temporary worktree mapping, report that environment seam rather
        # than replacing the positive path with a mocked verifier.
        repo = self.root / "import-repo"
        repo.mkdir()
        def git(*args: str) -> str:
            result = subprocess.run(["git", "-C", str(repo), *args], text=True,
                                    capture_output=True, check=True)
            return result.stdout.strip()
        git("init", "-q", "-b", "main")
        git("config", "user.name", "phase2")
        git("config", "user.email", "phase2@example.invalid")
        (repo / "src").mkdir()
        (repo / "src" / "base.txt").write_text("base\n", encoding="utf-8")
        git("add", "."); git("commit", "-qm", "base")
        source = git("rev-parse", "HEAD")
        git("branch", "recursion/integration", source)
        git("checkout", "-qb", "cursor/task-one")
        (repo / "src" / "feature.txt").write_text("candidate\n", encoding="utf-8")
        git("add", "."); git("commit", "-qm", "candidate")
        commit = git("rev-parse", "HEAD")
        contract = self.descriptor(repo=str(repo))
        candidate = {"project_id": "phase2-sweep", "task_id": "task-one", "source_branch": "main",
                     "source_sha": source, "external_branch": "cursor/task-one",
                     "candidate_commit": commit, "idempotency_key": "sweep-import"}
        # Receipt provenance is the complete diff stream.  The ordinary git() helper strips the
        # trailing newline for scalar values such as commit IDs; stripping a patch changes the
        # bytes being authenticated and makes the fixture receipt unlike a controller receipt.
        diff = subprocess.run(["git", "-C", str(repo), "diff", "--binary", source, commit],
                              text=True, capture_output=True, check=True).stdout
        body = {"schema": "recursion-controller-verifier-receipt/v1", "project_id": "phase2-sweep",
                "task_id": "task-one", "source_sha": source, "candidate_commit": commit,
                "diff_sha256": hashlib.sha256(diff.encode()).hexdigest(),
                "scope_digest": self.rc._json_digest(["src"]),
                "gate_digest": self.rc._json_digest(["git diff --check"]), "verdict": "pass",
                "verifier": "controller-verifier", "provenance": "recursion-controller"}
        receipt_digest = self.rc._json_digest(body)
        receipt = {**body, "receipt_digest": receipt_digest,
                   "signature": hmac.new(b"sweep-controller-key", receipt_digest.encode("ascii"),
                                         hashlib.sha256).hexdigest()}
        try:
            result = self.rc.import_candidate(contract, candidate, repo, receipt=receipt)
        except self.rc.ContractError as exc:
            cause = repr(exc.__cause__).lower()
            if exc.code == "verification-unavailable" and (
                    "createfilemapping" in cause or "permission denied" in cause
                    or (os.name == "nt" and "ledger directory could not be pinned" in cause)):
                self.skipTest(f"host Git/ACL permission artifact: {exc}")
            raise
        self.assertIn(result["status"], {"imported", "idempotent"})
        again = self.rc.import_candidate(contract, candidate, repo, receipt=receipt)
        self.assertEqual(again["status"], "idempotent")


if __name__ == "__main__":
    unittest.main(verbosity=2)

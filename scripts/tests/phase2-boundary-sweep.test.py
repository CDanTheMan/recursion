#!/usr/bin/env python3
"""Phase 2 class sweep: hostile boundaries, schema/runtime parity, and positive paths."""

from __future__ import annotations

import hashlib
import hmac
import importlib.util
import itertools
import json
import os
import stat
import subprocess
import sys
import tempfile
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
    tempfile.gettempdir(),
))
GATE = SOURCE / "scripts" / "validate-gate.py"
SCHEMA_PATH = SOURCE / "schemas" / "control-plane" / "v2" / "repository-contract.schema.json"

# These are punctuation boundary patterns for the external namespace.  The runtime and schema
# must agree with actual branch creation on the supported Windows host, not only check-ref-format.
EXTERNAL_PATTERN_RECONCILIATION = (
    "cursor/!*", 'cursor/"*', "cursor/#*", "cursor/$*", "cursor/%*", "cursor/&*",
    "cursor/'*", "cursor/(*", "cursor/)*", "cursor/+*", "cursor/,*", "cursor/;*",
    "cursor/<*", "cursor/=*", "cursor/>*", "cursor/@*", "cursor/]*", "cursor/`*",
    "cursor/{*", "cursor/|*", "cursor/}*",
    "!cursor/*", '"cursor/*', "#cursor/*", "$cursor/*", "%cursor/*", "&cursor/*",
    "'cursor/*", "(cursor/*", ")cursor/*", "*cursor/*", "+cursor/*", ",cursor/*",
)

WINDOWS_UNREALIZABLE_EXTERNAL_PATTERNS = frozenset({
    'cursor/"*', "cursor/<*", "cursor/>*", "cursor/|*", '"cursor/*',
})

# The stock Draft 2020-12 validator intentionally remains authoritative.  These cases are
# schema-only because the standard schema cannot express the corresponding runtime relation.
SCHEMA_ONLY_JUSTIFICATIONS = {
    "schema-version-float": "Draft 2020-12 integer includes 1.0; runtime requires exact Python int.",
    "default-integration-sibling-equality": "JSON Schema has no general sibling-property inequality.",
    "task-probe-collides-with-default": "JSON Schema cannot resolve task_branch_pattern against default_branch.",
    "external-pattern-overlaps-task-namespace": "JSON Schema cannot compare a pattern with the task namespace.",
    "profile-acceptance-differs": "JSON Schema cannot join gate_commands and compare the result to acceptance.",
    "profile-gate-files-name-different-worker": "JSON Schema cannot derive the worker executable from acceptance and compare it to gate_files.",
    "profile-worker-program-undeclared": "JSON Schema cannot require every worker executable in a command string to occur in gate_files.",
}

# These boundary cases were found by the expanded generated corpus.  They are expressible by
# the standard schema and therefore must agree with runtime admission, rather than becoming new
# permanent schema-only exceptions.
SCHEMA_EXPRESSIBLE_CASES = {
    "task-pattern-trailing-slash",
    "profile-acceptance-test-n",
    "profile-acceptance-comparison",
    "profile-acceptance-absolute-operand",
    "profile-acceptance-traversal",
    "profile-acceptance-glob",
    "profile-acceptance-dynamic-python",
    "profile-acceptance-option-bash",
}

TRAILING_SLASH_PATTERNS = (
    "cursor/", "cursor/x/", "cursor/*/", "cursor/x/*/", "cursor/extern/", "release/", "cursor/a/b/",
)


def load_gate_module():
    spec = importlib.util.spec_from_file_location("phase2_validate_gate", GATE)
    if spec is None or spec.loader is None:
        raise AssertionError("validate-gate module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_process(args: list[str], *, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, input=input_bytes, capture_output=True, check=False)


def remove_reparse_point(path: Path) -> None:
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return
    def remove() -> None:
        if os.name == "nt" and stat.S_ISDIR(info.st_mode):
            path.rmdir()
        else:
            path.unlink()
    try:
        remove()
    except PermissionError:
        if os.name != "nt":
            raise
        # Git's private temporary object files can carry the read-only DOS attribute.  This
        # retry is limited to this test-owned scratch entry and does not suppress the failure.
        os.chmod(path, stat.S_IWRITE)
        remove()


def remove_tree(path: Path) -> None:
    """Remove this test-owned tree without traversing symlinks or Windows reparses."""
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        remove_reparse_point(path)
        return
    if not stat.S_ISDIR(info.st_mode):
        try:
            path.unlink()
        except PermissionError:
            if os.name != "nt":
                raise
            os.chmod(path, stat.S_IWRITE)
            path.unlink()
        return
    for child in path.iterdir():
        remove_tree(child)
    try:
        path.rmdir()
    except PermissionError:
        if os.name != "nt":
            raise
        os.chmod(path, stat.S_IWRITE)
        path.rmdir()


def git_raw_bytes(repo: Path, *args: str) -> bytes:
    env = {
        key: value for key, value in os.environ.items()
        if key in {"PATH", "HOME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "SystemRoot", "WINDIR"}
    }
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"})
    result = subprocess.run(["git", "--no-replace-objects", "-c", f"safe.directory={repo}",
                             "-C", str(repo), *args], env=env,
                            capture_output=True, check=True)
    return result.stdout


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
        cls.inherited_key = cls.root / "inherited-controller.key"
        cls.inherited_key.write_text("sweep-controller-key\n", encoding="utf-8")
        cls.acl_setup_error = None
        if os.name == "nt":
            account = f"{os.environ.get('USERDOMAIN', '')}\\{os.environ['USERNAME']}"
            acl = run_process(["icacls", str(cls.key), "/inheritance:r", "/grant:r", f"{account}:F"])
            if acl.returncode:
                cls.acl_setup_error = acl.stderr.decode(errors="replace").strip()

    @classmethod
    def tearDownClass(cls) -> None:
        # This is cleanup of this test's uniquely-created scratch directory only.  Surface any
        # refusal and remove reparse entries without traversing their targets.
        remove_tree(cls.root)

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
        self.assertNotIn(str(self.root), self.rc._public_error_message(str(self.root)))
        for index, raw in enumerate(self.hostile_json_bytes()):
            path = self.root / f"hostile-{index}.json"
            path.write_bytes(raw)
            result = run_process([PYTHON, str(SOURCE / "scripts" / "repository_contract.py"),
                                  "validate-project", str(path)])
            with self.subTest(index=index):
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(b"Traceback", result.stderr)

        missing = self.root / "missing-contract.json"
        result = run_process([PYTHON, str(SOURCE / "scripts" / "repository_contract.py"),
                              "validate-project", str(missing)])
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(str(self.root).encode(), result.stderr)
        self.assertNotIn(str(self.root).replace("\\", "\\\\").encode(), result.stderr)
        self.assertNotIn(b"missing-contract.json", result.stderr)
        self.assertNotIn(b"No such file", result.stderr)
        error = json.loads(result.stderr.decode("utf-8"))
        self.assertEqual(set(error), {"error", "message"})

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
        module = load_gate_module()
        with self.assertRaises(ValueError):
            module._validate_git_subcommand(["git", "push"])
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
        corpus.extend([
            "test -s [",
            "[ --check",
            "[ --check [",
            "test -s src/[x]",
            "test -s \"src/[x]\"",
            "git diff --no-index src/a src/b",
            "git status --pathspec-from-file=src/list",
        ])
        mismatches: list[str] = []
        for command in corpus:
            schema_accepts = validator.is_valid(command)
            runtime_accepts = self.rc._valid_gate_command(
                command, allowed_paths=["src"],
                gate_files=["src/check.py", "src/check.sh", "src/check.js"],
                controller_gate_files=[])
            if schema_accepts != runtime_accepts:
                mismatches.append(command)
        schema_only = [item for item in mismatches if validator.is_valid(item)]
        runtime_only = [item for item in mismatches if not validator.is_valid(item)]
        self.assertEqual(
            mismatches, [],
            f"schema/runtime gate mismatches: schema-accept/runtime-reject={len(schema_only)} "
            f"schema-reject/runtime-accept={len(runtime_only)} values={mismatches}")

    def descriptor_parity_corpus(self) -> list[tuple[str, dict[str, object]]]:
        cases: list[tuple[str, dict[str, object]]] = []

        def add(label: str, **updates: object) -> None:
            cases.append((label, self.descriptor(**updates)))

        # The stock validator accepts 1.0 for an integer const and cannot express the runtime's
        # exact-Python-int check.  The remaining cross-field cases are likewise intentionally
        # retained as named, safe-direction exceptions below.
        add("schema-version-float", schema_version=1.0)
        add("default-integration-sibling-equality",
            default_branch="release", integration_branch="release")
        add("task-probe-collides-with-default",
            default_branch="recursion/task/probe", integration_branch="release")
        add("external-pattern-overlaps-task-namespace",
            external_branch_patterns=["recursion/task*"])
        add(
            "profile-acceptance-differs",
            gate_commands=["python3 src/check.py"],
            required_gate_profile={
                "acceptance": "python3 src/other.py", "gate_class": "light",
                "gate_files": ["src/check.py", "src/other.py"], "controller_gate_files": [],
            },
        )
        add(
            "profile-gate-files-name-different-worker",
            gate_commands=["python3 src/check.py"],
            required_gate_profile={
                "acceptance": "python3 src/check.py", "gate_class": "light",
                "gate_files": ["src/other.py"], "controller_gate_files": [],
            },
        )
        add(
            "profile-worker-program-undeclared",
            gate_commands=["python3 src/check.py", "python3 src/other.py"],
            required_gate_profile={
                "acceptance": "python3 src/check.py && python3 src/other.py", "gate_class": "light",
                "gate_files": ["src/check.py"], "controller_gate_files": [],
            },
        )
        add("task-pattern-trailing-slash",
            task_branch_pattern="recursion/task/{task_id}/")
        for label, acceptance in (
            ("profile-acceptance-test-n", "test -n foo"),
            ("profile-acceptance-comparison", "test a = b"),
            ("profile-acceptance-absolute-operand", "test -s /tmp/a"),
            ("profile-acceptance-traversal", "test -s ../a"),
            ("profile-acceptance-glob", "test -s src/[x]"),
            ("profile-acceptance-dynamic-python", "python3 -c true"),
            ("profile-acceptance-option-bash", "bash -e src/check.sh"),
        ):
            add(
                label,
                gate_commands=["python3 src/check.py"],
                required_gate_profile={
                    "acceptance": acceptance, "gate_class": "light",
                    "gate_files": ["src/check.py"], "controller_gate_files": [],
                },
            )

        for pattern in TRAILING_SLASH_PATTERNS:
            add(f"external-pattern-trailing-slash:{pattern}", external_branch_patterns=[pattern])
        for pattern in EXTERNAL_PATTERN_RECONCILIATION:
            add(f"external-pattern-git-punctuation:{pattern}", external_branch_patterns=[pattern])

        # Fill the remainder with distinct ordinary descriptors so the corpus has a stable,
        # explicit size while the named boundary cases above remain easy to audit.
        for index in range(202):
            add(f"ordinary-{index:03d}", id=f"phase2-ordinary-{index:03d}")
        self.assertEqual(len(cases), 257)
        return cases

    def test_runtime_and_schema_descriptor_differential_uses_stock_validator(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        mismatches: list[tuple[str, bool, bool]] = []
        schema_only: list[str] = []
        runtime_only: list[str] = []
        agree = 0
        for label, case in self.descriptor_parity_corpus():
            schema_accepts = validator.is_valid(case)
            try:
                self.rc.validate_project_descriptor(dict(case))
            except self.rc.ContractError:
                runtime_accepts = False
            else:
                runtime_accepts = True
            if schema_accepts == runtime_accepts:
                agree += 1
            else:
                mismatches.append((label, schema_accepts, runtime_accepts))
                if schema_accepts:
                    schema_only.append(label)
                else:
                    runtime_only.append(label)

        self.assertEqual(
            runtime_only, [],
            "runtime_only descriptor cases are severe: " + repr(runtime_only),
        )
        self.assertEqual(set(schema_only), set(SCHEMA_ONLY_JUSTIFICATIONS))
        self.assertTrue(
            SCHEMA_EXPRESSIBLE_CASES.isdisjoint(schema_only),
            "schema-expressible cases became unjustified schema-only exceptions: "
            + repr(sorted(SCHEMA_EXPRESSIBLE_CASES.intersection(schema_only))),
        )
        self.assertEqual(
            (agree, len(schema_only), len(runtime_only)), (250, 7, 0),
            f"schema/runtime descriptor counts: agree={agree} schema_only={len(schema_only)} "
            f"runtime_only={len(runtime_only)} mismatches={mismatches}",
        )

        # Keep the stock validator's integer semantics visible in the regression itself; this
        # is deliberately supplementary to the authoritative stock differential above.
        float_case = self.descriptor(schema_version=1.0)
        self.assertTrue(validator.is_valid(float_case))
        with self.assertRaises(self.rc.ContractError):
            self.rc.validate_project_descriptor(float_case)

        for label, justification in SCHEMA_ONLY_JUSTIFICATIONS.items():
            with self.subTest(schema_only=label):
                self.assertIsInstance(justification, str)
                self.assertIn(label, schema_only)

    def test_external_patterns_require_actual_branch_creation(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(
            schema["properties"]["external_branch_patterns"]["items"])
        branch_repo = self.root / "external-pattern-branches"
        branch_repo.mkdir()
        init = run_process(["git", "-C", str(branch_repo), "init", "-q", "-b", "main"])
        self.assertEqual(init.returncode, 0, init.stderr.decode(errors="replace"))
        (branch_repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        self.assertEqual(
            run_process(["git", "-C", str(branch_repo), "add", "seed.txt"]).returncode, 0)
        self.assertEqual(
            run_process(["git", "-C", str(branch_repo), "-c", "user.name=phase2",
                         "-c", "user.email=phase2@example.invalid", "commit", "-qm", "seed"]).returncode, 0)
        actual: dict[str, bool] = {}
        for pattern in EXTERNAL_PATTERN_RECONCILIATION:
            probe = pattern.replace("*", "probe")
            created = run_process(["git", "-C", str(branch_repo), "branch", probe])
            actual[pattern] = created.returncode == 0
            expected = pattern not in WINDOWS_UNREALIZABLE_EXTERNAL_PATTERNS
            with self.subTest(pattern=pattern, probe=probe):
                self.assertEqual(
                    actual[pattern], expected,
                    f"actual git branch creation disagreed for {pattern!r}: "
                    f"rc={created.returncode} stderr={created.stderr.decode(errors='replace')!r}",
                )
                self.assertEqual(self.rc._valid_git_pattern(pattern), expected)
                self.assertEqual(validator.is_valid(pattern), expected)
        self.assertEqual(
            sum(actual.values()), len(EXTERNAL_PATTERN_RECONCILIATION) - len(
                WINDOWS_UNREALIZABLE_EXTERNAL_PATTERNS))

    def test_class_a_json_integer_boundary_is_explicit(self) -> None:
        for value in (True, False, 1.0, 1e999, "1", [], {}, None):
            with self.subTest(value=value):
                with self.assertRaises(self.rc.ContractError):
                    self.rc.validate_project_descriptor(self.descriptor(schema_version=value))
        self.rc.validate_project_descriptor(self.descriptor(schema_version=1))

    def test_windows_or_posix_controller_key_positive_and_acl_negative(self) -> None:
        if not self.acl_setup_error:
            self.assertEqual(self.rc._controller_key(), b"sweep-controller-key")
        self.rc._validate_windows_acl_records("S-1-owner", "S-1-owner", [], True)
        with self.assertRaises(OSError):
            self.rc._validate_windows_acl_records(
                "S-1-owner", "S-1-owner", [("S-1-foreign", 0, 0x001F01FF, 0)], True)
        with self.assertRaises(OSError):
            self.rc._validate_windows_acl_records(
                "S-1-owner", "S-1-owner", [("S-1-foreign", 0x10, 0x001F01FF, 0)], True)

    def test_windows_inherited_write_controller_key_is_rejected(self) -> None:
        if os.name != "nt":
            self.skipTest("inherited Windows ACLs are not available on this host")
        self.rc.CONTROLLER_KEY_PATH = self.inherited_key
        with self.assertRaises(self.rc.ContractError) as failure:
            self.rc._controller_key()
        self.assertIn("controller key ACL grants inherited write access",
                      str(failure.exception.__cause__))

    def test_all_nine_project_configs_still_admit(self) -> None:
        configs = sorted((SOURCE / "state" / "project-config").glob("*.json"))
        self.assertEqual(len(configs), 9)
        for path in configs:
            with self.subTest(path=path.name):
                value = json.loads(path.read_text(encoding="utf-8"))
                self.rc.validate_project_descriptor(value)
        with self.assertRaises(self.rc.ContractError):
            self.rc.validate_project_descriptor(
                self.descriptor(default_branch="feature", integration_branch="feature"))

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
        replacement = self.root / "replacement.txt"
        replacement.write_text("two\n", encoding="utf-8")
        fd = os.open(swapped, os.O_RDONLY)
        before = os.fstat(fd)
        after = os.stat(replacement)
        try:
            with mock.patch.object(module.os, "fstat", side_effect=[before, after]):
                with self.assertRaises(ValueError):
                    module._read_pinned(fd, swapped)
        finally:
            os.close(fd)

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
        committed_bytes = gate_file.read_bytes()
        self.assertEqual(module.clean_tracked_bytes(gate_repo, "src/check.py"), committed_bytes)
        self.assertEqual(self.rc._git_dir(gate_repo), gate_repo / ".git")
        expected_hash = hashlib.sha256(module.clean_tracked_bytes(gate_repo, "src/check.py")).hexdigest()
        module._execute_from_verified_files(
            "python3 src/check.py", gate_repo, None, ["src/check.py"], [],
            {"src/check.py": expected_hash}, {})
        gate_file.write_text("print('changed')\n", encoding="utf-8")
        direct_diff = git_raw_bytes(gate_repo, "diff", "--binary", "HEAD", "--", "src/check.py")
        product_diff = self.rc._checked_git_raw(
            gate_repo, "diff", "--binary", "HEAD", "--", "src/check.py").stdout
        self.assertEqual(product_diff, direct_diff)
        self.assertEqual(hashlib.sha256(product_diff).hexdigest(), hashlib.sha256(direct_diff).hexdigest())
        gate_file.write_text("print('swapped')\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            module._execute_from_verified_files(
                "python3 src/check.py", gate_repo, None, ["src/check.py"], [],
                {"src/check.py": expected_hash}, {})

    def test_directory_handle_identity_recheck_is_not_vacuous(self) -> None:
        expected = self.repo.stat()
        changed = self.root.stat()
        with mock.patch.object(self.rc.os, "fstat", return_value=changed):
            with self.assertRaisesRegex(
                    OSError, "directory identity changed while pinned",
                    msg="directory handle recheck accepted a different directory",
            ):
                self.rc._verify_directory_handle(123, expected)

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
            git_repo = self.root / "git-junction-repo"
            git_target = self.root / "git-junction-target"
            git_repo.mkdir()
            git_target.mkdir()
            init = run_process(["git", "-C", str(git_repo), "init", "-q", "-b", "main"])
            self.assertEqual(init.returncode, 0, init.stderr.decode(errors="replace"))
            redirected_git = git_target / "git-dir"
            (git_repo / ".git").rename(redirected_git)
            actual_git_junction = git_repo / ".git"
            if os.name == "nt":
                result = run_process(["cmd.exe", "/d", "/c", "mklink", "/J",
                                      str(actual_git_junction), str(redirected_git)])
                if result.returncode:
                    self.skipTest(f".git junction creation is unavailable on this host: {result.stderr!r}")
            else:
                actual_git_junction.symlink_to(redirected_git, target_is_directory=True)
            with self.assertRaises(self.rc.ContractError):
                self.rc._git_dir(git_repo)
            with mock.patch.object(
                    self.rc, "_checked_git",
                    return_value=SimpleNamespace(returncode=0, stdout=str(junction))):
                with self.assertRaises(self.rc.ContractError):
                    self.rc._git_dir(self.repo)
            failure_parent = self.root / "handle-failure-parent"
            failure_parent.mkdir()
            with mock.patch.object(module.os, "name", "posix"), \
                    mock.patch.object(module.os, "open", return_value=123), \
                    mock.patch.object(module.os, "fstat", side_effect=OSError("fstat failure")), \
                    mock.patch.object(module.os, "close") as close:
                with self.assertRaises(ValueError):
                    with module._pinned_file_parents(failure_parent / "gate.py"):
                        pass
            self.assertEqual(close.call_count, 1,
                             "failed parent pin did not release its opened handle")
            with mock.patch.object(self.rc.os, "name", "posix"), \
                    mock.patch.object(self.rc.os, "open", return_value=456), \
                    mock.patch.object(self.rc.os, "fstat", side_effect=OSError("fstat failure")), \
                    mock.patch.object(self.rc.os, "close") as close:
                with self.assertRaises(OSError):
                    with self.rc._pinned_real_directory(self.root / "repo"):
                        pass
            self.assertEqual(close.call_count, 1,
                             "failed directory pin did not release its opened handle")
            real_directory = self.root / "repo"
            real_info = real_directory.stat()
            with mock.patch.object(self.rc.os, "name", "posix"), \
                    mock.patch.object(self.rc.os, "open", return_value=789), \
                    mock.patch.object(self.rc.os, "fstat", side_effect=[real_info, OSError("recheck failure")]), \
                    mock.patch.object(self.rc.os, "close") as close:
                with self.assertRaises(OSError):
                    with self.rc._pinned_real_directory(real_directory):
                        pass
            self.assertEqual(close.call_count, 2,
                             "directory recheck failure did not release its pinned handle")
        finally:
            for reparse_point in (
                    junction,
                    self.root / "ledger-junction",
                    self.root / "git-junction-repo" / ".git",
            ):
                remove_reparse_point(reparse_point)

    def test_normal_candidate_import_publish_path_is_bound(self) -> None:
        # This is a real fixture import, including the controller gate and idempotency record.
        # If the host denies Git's temporary worktree mapping, report that environment seam rather
        # than replacing the positive path with a mocked verifier.
        if self.acl_setup_error:
            self.skipTest(f"host ACL setup denied: {self.acl_setup_error}")
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
        diff = git_raw_bytes(repo, "diff", "--binary", source, commit)
        body = {"schema": "recursion-controller-verifier-receipt/v1", "project_id": "phase2-sweep",
                "task_id": "task-one", "source_sha": source, "candidate_commit": commit,
                "diff_sha256": hashlib.sha256(diff).hexdigest(),
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
        forged = dict(receipt, diff_sha256="0" * 64)
        receipt_body = {key: forged[key] for key in (
            "schema", "project_id", "task_id", "source_sha", "candidate_commit", "diff_sha256",
            "scope_digest", "gate_digest", "verdict", "verifier", "provenance")}
        forged["receipt_digest"] = self.rc._json_digest(receipt_body)
        forged["signature"] = hmac.new(
            b"sweep-controller-key", forged["receipt_digest"].encode("ascii"), hashlib.sha256
        ).hexdigest()
        with self.assertRaises(self.rc.ContractError):
            self.rc._verify_receipt(
                contract, candidate, forged, source, commit, ["src/feature.txt"], ["src"], repo)


if __name__ == "__main__":
    unittest.main(verbosity=2)

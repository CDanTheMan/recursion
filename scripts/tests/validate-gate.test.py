#!/usr/bin/env python3
"""Adversarial controls for --strict-direct gate admission: bypasses fail, direct gates pass."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import jsonschema


SOURCE = Path(__file__).resolve().parents[2]
GATE = SOURCE / "scripts" / "validate-gate.py"


def run_gate_result(acceptance: str, strict: bool = True,
                    gate_files: str = "") -> subprocess.CompletedProcess[bytes]:
    argv = [sys.executable, str(GATE), "--acceptance", acceptance, "--allowed-paths", "app"]
    if gate_files:
        argv += ["--gate-files", gate_files]
    if strict:
        argv.append("--strict-direct")
    return subprocess.run(argv, capture_output=True, check=False)


def run_gate(acceptance: str, strict: bool = True, gate_files: str = "") -> int:
    return run_gate_result(acceptance, strict, gate_files).returncode


class DirectGateAdmissionTest(unittest.TestCase):
    def test_reviewed_direct_commands_are_admitted(self):
        admitted = (
            "test -s app/result.txt",
            "test -s app/result.txt && test -s app/other.txt",
            "test a != b",
        )
        for gate in admitted:
            with self.subTest(gate=gate):
                self.assertEqual(run_gate(gate), 0)

    def test_declared_worktree_gate_programs_are_admitted(self):
        admitted = (
            ("bash app/check.sh", "app/check.sh"),
            ("python3 app/check.py", "app/check.py"),
            ("node app/check.cjs", "app/check.cjs"),
        )
        for gate, gate_file in admitted:
            with self.subTest(gate=gate):
                self.assertEqual(run_gate(gate, gate_files=gate_file), 0)

    def test_posix_absolute_controller_program_is_never_treated_as_a_worktree_path(self):
        self.assertNotEqual(run_gate("/opt/recursion/scripts/reviewed-gate.py"), 0)

    def test_shell_reserved_words_and_wrappers_are_refused(self):
        refused = (
            "! test -s app/result.txt",
            "command python3 app/check.py",
            "exec python3 app/check.py",
            "builtin test -s app/result.txt",
            "source app/check.sh",
            ". app/check.sh",
            "time python3 app/check.py",
            "nohup python3 app/check.py",
            "setsid python3 app/check.py",
            "sudo python3 app/check.py",
            "timeout 5 python3 app/check.py",
            "/usr/bin/timeout 5 python3 app/check.py",
            "bash -c 'test -s app/result.txt'",
            "node --require app/loader.cjs app/check.cjs",
            "env python3 app/check.py",
            "pytest app/check.py",
        )
        for gate in refused:
            with self.subTest(gate=gate):
                self.assertNotEqual(run_gate(gate), 0)

    def test_backgrounding_is_refused(self):
        for gate in (
            "test -s app/result.txt & test -s app/other.txt",
            "test -s app/result.txt && test -s app/other.txt & echo x",
            "test -s app/result.txt&",
        ):
            with self.subTest(gate=gate):
                self.assertNotEqual(run_gate(gate), 0)

    def test_redirection_is_refused(self):
        for gate in (
            "test -s app/result.txt > /dev/null",
            "test -s app/result.txt 2>&1",
            "cat app/result.txt < app/other.txt",
            "test -s app/result.txt >> app/log.txt",
            "test -s app/result.txt >&2",
        ):
            with self.subTest(gate=gate):
                self.assertNotEqual(run_gate(gate), 0)

    def test_pipelines_and_substitutions_are_refused(self):
        for gate in (
            "cat app/result.txt | grep -q x",
            "test -s app/result.txt || true",
            "test -s app/result.txt; true",
            "test -s \"$(echo app/result.txt)\"",
            "test -s $RESULT_PATH",
            "test -s `echo app/result.txt`",
            "test -s <(echo app/result.txt)",
        ):
            with self.subTest(gate=gate):
                self.assertNotEqual(run_gate(gate), 0)

    def test_path_traversal_and_git_repository_redirection_are_refused(self):
        refused = (
            "python3 ../check.py",
            "python3 app/../check.py",
            "python3 app/check.py --profile ../profile.json",
            "python3 app\\..\\check.py",
            "git -C ../other diff --check",
            "git -C../other diff --check",
            "git --git-dir ../other/.git diff",
            "git --git-dir=../other/.git diff",
            "git --work-tree /tmp diff",
            "git --work-tree=/tmp diff",
            "git -c core.worktree=../other diff",
            "git --config-env=GIT_DIR=../other diff",
            "git -Ctmp diff --check",
            "git --git-dir/tmp diff",
            "git --work-tree/tmp diff",
            "git -cfoo diff --check",
            "git -o /tmp diff",
            "git --output /tmp diff",
            "git --output=/tmp diff",
        )
        for gate in refused:
            with self.subTest(gate=gate):
                self.assertNotEqual(run_gate(gate, gate_files="app/check.py"), 0)

        # Deterministic public-schema/runtime differential.  The cross-product deliberately
        # exercises spacing and `&&` collation in addition to the enumerated bypass families.
        # Keep this in an existing test so the historical strict-gate acceptance remains 10/10.
        schema = json.loads((SOURCE / "schemas/control-plane/v2/repository-contract.schema.json").read_text())
        gate_schema = schema["properties"]["gate_commands"]["items"]
        validator = jsonschema.Draft7Validator(gate_schema)
        direct = (
            "test -s app/a", "test -e app/a", "[ -s app/a ]", "git diff --check",
            "bash app/check.sh", "python3 app/check.py", "node app/check.cjs",
        )
        exact_bypasses = (
            'bash "-c" "test -s app/a"', 'python3 "-c" "test -s app/a"',
            "node --eval x", "python3 --eval x", 'test "-n" foo',
            'test -s "app\\..\\a"', "test -s app/..\\a",
            'git "--work-tree=/tmp" diff', "./test -s app/a", "src/test -s app/a",
            "git --work-tree=/tmp diff",
        )
        malformed = (
            "", " ", "test -s app/a &&", "&& test -s app/a",
            "test -s app/a && && git diff --check", "test -s app/a &&& git diff --check",
            "test -s 'app/a", 'test -s "app/a', "test -s app/a || git diff --check",
            "test -s app/a; git diff --check", "test -s app/a | git diff --check",
            "test -s app/a > app/out", "test -s app/a < app/in",
            "test -s $(echo app/a)", "test -s `echo app/a`", "test -s $APP_FILE",
            "command test -s app/a", "exec test -s app/a", "env test -s app/a",
            "bash -c true", "sh -e app/check.sh", "python -m check", "node -e x",
            "test -n foo", "[ -n foo ]", "test a = b", "[ a == b ]",
            "test -s /tmp/a", "test -s C:\\tmp\\a", "test -s ../a",
            "test -s app/../a", "test -s app\\..\\a", "python3 app\\..\\check.py",
            "git -C app diff", "git -Capp diff", "git -c core.pager=cat diff",
            "git -ccore.pager=cat diff", "git --git-dir app/.git diff",
            "git --git-dir=app/.git diff", "git --work-tree app diff",
            "git --work-tree=app diff", "git --config app/cfg diff",
            "git --config=app/cfg diff", "git --config-env=GIT_DIR=app diff",
            "git -o app/out diff", "git --output app/out diff", "git --output=app/out diff",
            'test "-s" app/a', 'python3 app/check.py "--eval"',
            'git diff "--work-tree=app"', "bash", "python3", "node",
            "test -s .recursion-result.json", " " * 4090 + "git diff --check",
        )
        quoting_and_paths = (
            'test -s "app/result file.txt"', "test -s 'app/result file.txt'",
            "test -s app\\result.txt", 'python3 "app\\check.py"',
            "git\tdiff\t--check", " test -s app/a ", "[\t-s\tapp/a\t]",
        )
        corpus = set(direct + exact_bypasses + malformed + quoting_and_paths)
        for left in direct:
            for right in direct:
                corpus.add(f"{left} && {right}")
                corpus.add(f"{left}&&{right}")
                corpus.add(f" {left}\t&&\t{right} ")
        for left in direct[:4]:
            for separator in (" || ", "; ", " | ", " &&& ", " & "):
                corpus.add(f"{left}{separator}{direct[-1]}")

        declared = "app/check.sh app/check.py app/check.cjs"
        for gate in sorted(corpus):
            with self.subTest(differential=gate):
                schema_accepts = validator.is_valid(gate)
                result = run_gate_result(gate, gate_files=declared)
                stderr = result.stderr.decode("utf-8", "replace")
                self.assertNotIn("Traceback", stderr)
                self.assertEqual(schema_accepts, result.returncode == 0, stderr)


class WindowsPathToleranceTest(unittest.TestCase):
    """Backslash-carrying gate programs. Quoted backslashes survive POSIX shlex, so the
    per-word normalization admits them identically on every host. Unquoted and quoted forms are
    normalized before POSIX shlex splitting, so the declaration and confinement checks see one
    canonical path representation."""

    def test_quoted_backslash_program_is_normalized_and_checked_everywhere(self):
        self.assertEqual(run_gate('python3 "app\\check.py"', gate_files="app/check.py"), 0)
        self.assertNotEqual(run_gate('python3 "app\\check.py"'), 0)

    def test_unquoted_backslash_program(self):
        undeclared = run_gate("python3 app\\check.py")
        declared = run_gate("python3 app\\check.py", gate_files="app/check.py")
        self.assertNotEqual(undeclared, 0)
        self.assertEqual(declared, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

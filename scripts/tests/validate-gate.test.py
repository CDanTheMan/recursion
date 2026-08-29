#!/usr/bin/env python3
"""Adversarial controls for --strict-direct gate admission: bypasses fail, direct gates pass."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
GATE = SOURCE / "scripts" / "validate-gate.py"


def run_gate(acceptance: str, strict: bool = True, gate_files: str = "") -> int:
    argv = [sys.executable, str(GATE), "--acceptance", acceptance, "--allowed-paths", "app"]
    if gate_files:
        argv += ["--gate-files", gate_files]
    if strict:
        argv.append("--strict-direct")
    return subprocess.run(argv, capture_output=True, check=False).returncode


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

    def test_interpreter_and_file_operand_traversals_are_refused_even_with_another_hashed_gate(self):
        traversal = (
            "python3 ../outside.py && test -s app/result.txt",
            "python3 app/../outside.py && test -s app/result.txt",
            "python3 app/sub/../../outside.py && test -s app/result.txt",
            'python3 "app\\..\\outside.py" && test -s app/result.txt',
            "test -s ../outside.txt && python3 app/check.py",
        )
        for gate in traversal:
            with self.subTest(gate=gate):
                self.assertNotEqual(run_gate(gate, gate_files="app/check.py"), 0)


class WindowsPathToleranceTest(unittest.TestCase):
    """Backslash-carrying gate programs. Quoted backslashes survive POSIX shlex, so the
    per-word normalization admits them identically on every host. UNQUOTED backslashes are
    consumed by the split itself; on Windows the segment is normalized before splitting, while
    on the box the mangled word ("appcheck.py") falls outside the allowed roots and today's
    verdicts are preserved byte-for-byte — these tests pin that difference so a change to
    Linux parsing cannot land silently (PROPOSALS 2026-08-27 item 11 holds that remainder)."""

    def test_quoted_backslash_program_is_normalized_and_checked_everywhere(self):
        self.assertEqual(run_gate('python3 "app\\check.py"', gate_files="app/check.py"), 0)
        self.assertNotEqual(run_gate('python3 "app\\check.py"'), 0)

    def test_unquoted_backslash_program(self):
        undeclared = run_gate("python3 app\\check.py")
        declared = run_gate("python3 app\\check.py", gate_files="app/check.py")
        if os.name == "nt":
            self.assertNotEqual(undeclared, 0)
            self.assertEqual(declared, 0)
        else:
            # POSIX shlex consumes an unquoted backslash.  The resulting
            # mangled program is not the declared path and must remain refused.
            self.assertNotEqual(undeclared, 0)
            self.assertEqual(declared, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

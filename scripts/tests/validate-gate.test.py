#!/usr/bin/env python3
"""Adversarial controls for --strict-direct gate admission: bypasses fail, direct gates pass."""

from __future__ import annotations

import json
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

import jsonschema


SOURCE = Path(__file__).resolve().parents[2]
GATE = SOURCE / "scripts" / "validate-gate.py"
SCRATCH_ROOT = Path(os.environ.get(
    "RECURSION_PHASE2_SCRATCH",
    tempfile.gettempdir(),
))


def explicit_scratch(prefix: str) -> Path:
    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
    path = SCRATCH_ROOT / f"{prefix}-{uuid.uuid4().hex}"
    path.mkdir()
    return path


def run_gate_result(
        acceptance: str, strict: bool = True, gate_files: str = "",
        read_only_paths: str = "", legacy: bool = False,
        ) -> subprocess.CompletedProcess[bytes]:
    argv = [sys.executable, str(GATE), "--acceptance", acceptance, "--allowed-paths", "app"]
    if gate_files:
        argv += ["--gate-files", gate_files]
    if read_only_paths:
        argv += ["--read-only-paths", read_only_paths]
    if legacy:
        argv.append("--legacy-compound")
    if strict:
        argv.append("--strict-direct")
    return subprocess.run(argv, capture_output=True, check=False)


def run_gate(acceptance: str, strict: bool = True, gate_files: str = "") -> int:
    return run_gate_result(acceptance, strict, gate_files).returncode


def load_gate_module():
    spec = importlib.util.spec_from_file_location("validate_gate_isolated", GATE)
    if spec is None or spec.loader is None:
        raise AssertionError("validate-gate module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_gate_cli(
    acceptance: str,
    strict: bool = True,
    gate_files: str = "",
    allowed_paths: str = "app",
    controller_root: Path | None = None,
    controller_commit: str = "",
    controller_gate_files: str = "",
) -> subprocess.CompletedProcess[str]:
    argv = [sys.executable, str(GATE), "--acceptance", acceptance, "--allowed-paths", allowed_paths]
    if gate_files:
        argv += ["--gate-files", gate_files]
    if controller_root is not None:
        argv += ["--controller-root", str(controller_root)]
    if controller_commit:
        argv += ["--controller-commit", controller_commit]
    if controller_gate_files:
        argv += ["--controller-gate-files", controller_gate_files]
    if strict:
        argv.append("--strict-direct")
    environment = os.environ.copy()
    if controller_root is not None:
        environment["RECURSION_ROOT"] = str(controller_root)
    return subprocess.run(argv, capture_output=True, text=True, env=environment, check=False)


def run_gate(acceptance: str, strict: bool = True, gate_files: str = "") -> int:
    return run_gate_cli(acceptance, strict, gate_files).returncode


def posix_absolute(path: Path) -> str:
    """Spell a path as a POSIX absolute path on both the Linux product host and this host."""
    resolved = path.resolve()
    volume_root = Path(resolved.anchor)
    return "/" + resolved.relative_to(volume_root).as_posix()


def git_head(repository: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


class DirectGateAdmissionTest(unittest.TestCase):
    def test_strict_direct_pattern_rejects_an_incomplete_command_chain(self):
        module = load_gate_module()
        self.assertIsNone(
            module.STRICT_DIRECT_PATTERN.fullmatch("git diff --check &&"),
            "strict direct grammar accepted an incomplete command chain",
        )

    def test_non_strict_path_traversal_guard_isolated_from_scope_checks(self):
        result = run_gate_result("test app/../left != app/../right", strict=False)
        self.assertNotEqual(
            result.returncode, 0,
            "path traversal guard accepted traversal in non-path comparison operands",
        )

    def test_legacy_conditional_gate_is_typed_and_explicit(self):
        acceptance = "if [ -e app/result.txt ]; then exit 0; else exit 1; fi"
        self.assertNotEqual(
            run_gate_result(acceptance, strict=False).returncode,
            0,
            "legacy conditional gate was admitted without its explicit caller opt-in",
        )
        self.assertEqual(
            run_gate_result(acceptance, strict=False, legacy=True).returncode,
            0,
            "typed legacy conditional gate was not admitted for non-pilot work.sh tasks",
        )
        self.assertNotEqual(
            run_gate_result(acceptance, strict=True, legacy=True).returncode,
            0,
            "legacy conditional gate bypassed strict direct admission",
        )
        # This semicolon-free case reaches the strict/legacy opt-in guard itself.  If that
        # guard is weakened, strict direct validation admits the otherwise valid command.
        isolated = run_gate_result("test -s app/result.txt", strict=True, legacy=True)
        self.assertEqual(isolated.returncode, 2)
        self.assertEqual(
            isolated.stderr.decode("utf-8", "replace").strip(),
            "ERR legacy compound gates are not admitted in strict direct mode",
        )
        self.assertNotEqual(
            run_gate_result(
                "if [ -e /tmp/outside ]; then exit 0; else exit 1; fi",
                strict=False, legacy=True,
            ).returncode,
            0,
            "legacy conditional gate escaped filesystem operand confinement",
        )

    def test_hostile_absolute_path_refusals_are_symbolic_and_positive_paths_remain_admitted(self):
        git_result = run_gate_result("git status --pathspec-from-file=/tmp/paths")
        self.assertEqual(git_result.returncode, 2)
        self.assertEqual(
            git_result.stderr.decode("utf-8", "replace").strip(),
            "ERR Git gate option is not confined to the detached worktree: --pathspec-from-file",
        )

        module = load_gate_module()
        with self.assertRaisesRegex(
                ValueError, "^acceptance path operand is outside declared controller files$"):
            # Direct invocation reaches validate_direct_argv's strict path-operand guard;
            # strict CLI grammar rejects this absolute command earlier by design.
            module.validate_direct_argv(
                ["test", "-s", "/tmp/outside"], allowed=["app"], gate_files=[],
                controller_root=None, controller_gate_files=[],
            )

        non_strict = run_gate_result("test -s /tmp/outside", strict=False)
        self.assertEqual(non_strict.returncode, 2)
        self.assertEqual(
            non_strict.stderr.decode("utf-8", "replace").strip(),
            "ERR acceptance path operand is outside declared controller files",
        )
        strict = run_gate_result("test -s /tmp/outside", strict=True)
        self.assertNotEqual(strict.returncode, 0)
        self.assertNotIn("/tmp/", strict.stderr.decode("utf-8", "replace"))
        for result in (git_result, non_strict, strict):
            self.assertNotIn("Traceback", result.stderr.decode("utf-8", "replace"))

        self.assertEqual(
            run_gate_result("test -s fixtures/truth.json", read_only_paths="fixtures").returncode,
            0,
        )

    def test_touch_is_not_an_admitted_acceptance_command(self):
        for acceptance in ("touch", "touch app/a", "touch /tmp/phase5-marker", "touch C:/phase5-marker"):
            for strict in (False, True):
                with self.subTest(acceptance=acceptance, strict=strict):
                    result = run_gate_result(acceptance, strict=strict)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("acceptance", result.stderr.decode("utf-8", "replace"))

    def test_legacy_direct_mode_has_no_hostile_relaxations(self):
        hostile = (
            ("test a = b", "ERR literal test acceptance is structurally vacuous"),
            ("test a != b", "ERR literal test acceptance is structurally vacuous"),
            ("bash -c true", "ERR dynamic bash acceptance programs are not admitted"),
            ("python3 -c true", "ERR dynamic python3 acceptance programs are not admitted"),
            ("env test -s app/a", "ERR indirect acceptance launcher is not admitted: env"),
            ("./outside.sh", "ERR acceptance executable path is unsafe: ./outside.sh"),
            ("../outside.sh", "ERR acceptance executable path is unsafe: ../outside.sh"),
            ("bash ../../evil.sh", "ERR acceptance program path is unsafe: ../../evil.sh"),
        )
        for acceptance, expected in hostile:
            with self.subTest(acceptance=acceptance):
                result = run_gate_result(acceptance, strict=False, legacy=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stderr.decode("utf-8", "replace").strip(), expected)

    def test_launcher_guards_are_reachable_from_cli(self):
        cases = (
            ("/usr/bin/python3 app/check.py", "ERR path-qualified acceptance launcher is not admitted"),
            ("command python3 app/check.py", "ERR shell reserved word or wrapper is not admitted: command"),
            ("env test -s app/a", "ERR indirect acceptance launcher is not admitted: env"),
            ("pytest app/check.py", "ERR bare acceptance launcher is not admitted: pytest"),
            ("python3", "ERR python3 acceptance has no explicit grading program"),
            ("python3 -c true", "ERR dynamic python3 acceptance programs are not admitted"),
            ("python3 --version", "ERR option-bearing python3 acceptance programs are not admitted: --version"),
            ("python3 ../outside.py", "ERR acceptance program path is unsafe: ../outside.py"),
        )
        for acceptance, expected in cases:
            with self.subTest(acceptance=acceptance):
                result = run_gate_result(acceptance, strict=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stderr.decode("utf-8", "replace").strip(), expected)

    def test_git_redirection_options_are_rejected_by_cli_in_both_modes(self):
        blocked = (
            ("--work-tree", "--work-tree=/tmp", "--work-tree /tmp"),
            ("--git-dir", "--git-dir=/tmp/x", "--git-dir /tmp/x"),
            ("-C", "-C/tmp", "-C /tmp"),
            ("--exec-path", "--exec-path=/tmp", "--exec-path /tmp"),
            ("--namespace", "--namespace=/tmp", "--namespace /tmp"),
            ("--super-prefix", "--super-prefix=/tmp", "--super-prefix /tmp"),
            ("-c", "-ccore.worktree=/tmp", "-c core.worktree=/tmp"),
            ("--config", "--config=/tmp", "--config /tmp"),
            ("--config-env", "--config-env=GIT_DIR=/tmp", "--config-env GIT_DIR=/tmp"),
            ("-o", "-o/tmp", "-o /tmp"),
            ("--output", "--output=/tmp", "--output /tmp"),
        )
        for symbol, joined, spaced in blocked:
            for option_form in (joined, spaced):
                for acceptance in (
                    f"git diff {option_form}",
                    f"test -s app/result.txt && git diff {option_form}",
                ):
                    for strict in (False, True):
                        with self.subTest(symbol=symbol, option_form=option_form,
                                          acceptance=acceptance, strict=strict):
                            result = run_gate_result(acceptance, strict=strict)
                            stderr = result.stderr.decode("utf-8", "replace").strip()
                            self.assertEqual(result.returncode, 2)
                            self.assertEqual(
                                stderr,
                                "ERR Git gate may not redirect its repository or configuration: "
                                + symbol,
                            )
                            self.assertNotIn("/tmp", stderr)
                            self.assertNotIn("Traceback", stderr)

    def test_required_positive_controls_are_admitted_in_both_modes(self):
        for acceptance in (
            "git diff app",
            "git status app",
        ):
            for strict in (False, True):
                with self.subTest(acceptance=acceptance, strict=strict):
                    result = run_gate_result(acceptance, strict=strict)
                    self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        for strict in (False, True):
            with self.subTest(read_only=True, strict=strict):
                result = run_gate_result(
                    "test -s fixtures/truth.json", strict=strict, read_only_paths="fixtures",
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))

    def test_declared_read_only_paths_are_admitted_but_not_widened(self):
        acceptance = "test -s fixtures/truth.json"
        self.assertEqual(
            run_gate_result(acceptance, read_only_paths="fixtures").returncode,
            0,
            "a declared read-only gate path was rejected",
        )
        self.assertNotEqual(
            run_gate_result(acceptance).returncode,
            0,
            "a read-only gate path was admitted without declaration",
        )

    def test_gate_contract_has_optional_read_only_paths_only_when_declared(self):
        core = {"acceptance", "acceptance_sha256", "gate_files", "controller_gate_files"}
        plain = json.loads(run_gate_result("test -s app/result.txt").stdout.decode("utf-8"))
        seeded = json.loads(
            run_gate_result("test -s fixtures/truth.json", read_only_paths="fixtures")
            .stdout.decode("utf-8")
        )
        self.assertEqual(set(plain), core)
        self.assertEqual(set(seeded), core | {"read_only_paths"})
        self.assertEqual(seeded["read_only_paths"], ["fixtures"])

    def test_non_strict_git_cwd_redirection_guard_isolated_from_subcommand_checks(self):
        module = load_gate_module()
        with self.assertRaisesRegex(
                ValueError, "Git gate may not redirect",
                msg="Git cwd redirection guard accepted an otherwise allowed read-only subcommand",
        ):
            module.validate_direct_argv(
                ["git", "diff", "--work-tree=/tmp"],
                allowed=["app"], gate_files=[], controller_root=None,
                controller_gate_files=[],
            )

    def test_path_qualified_launcher_guard_is_individually_sensitive(self):
        module = load_gate_module()
        with self.assertRaisesRegex(
                ValueError, "path-qualified acceptance launcher",
                msg="path-qualified launcher guard accepted an undeclared direct launcher",
        ):
            # python3 is an admitted direct command, so this reaches line 380 and cannot be
            # refused by the downstream RESERVED wrapper guard.
            module.entrypoint(["/usr/bin/python3", "app/check.py"], True)

    def test_absolute_path_operands_remain_confined_in_both_modes(self):
        marker = str(Path(tempfile.gettempdir()) / "phase5-marker")
        for strict in (False, True):
            with self.subTest(strict=strict):
                self.assertNotEqual(run_gate(f"test -s {marker}", strict=strict), 0)

    def test_grouped_success_guard_classifies_the_inner_literal(self):
        module = load_gate_module()
        self.assertTrue(
            module.vacuous_success(["(", "true", ")"]),
            "grouped literal success was not classified as vacuous",
        )

    def test_reviewed_direct_commands_are_admitted(self):
        admitted = (
            "test -s app/result.txt",
            "test -s app/result.txt && test -s app/other.txt",
            "git diff app",
            "git status app",
        )
        for gate in admitted:
            with self.subTest(gate=gate):
                self.assertEqual(run_gate(gate), 0)

    def test_unsafe_gate_file_path_is_typed_and_symbolic(self):
        for path in ("/tmp/private-gate.py", r"C:\tmp\private-gate.py"):
            with self.subTest(path=path):
                result = run_gate_result("git diff --check", gate_files=path)
                stderr = result.stderr.decode("utf-8", "replace")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(stderr.strip(), "ERR gate-file-path-invalid")
                self.assertNotIn(path, stderr)

        self.assertEqual(
            run_gate_result("git diff --check", gate_files="app/check.py").returncode,
            0,
        )

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

    def test_shell_expansion_globs_drive_relative_and_unc_operands_are_refused(self):
        refused = (
            "test -s ~",
            "test -s *",
            "test -s ?.txt",
            "test -s %USERPROFILE%",
            "test -s $TEMP",
            "test -s `echo app/result.txt`",
            "test -s C:outside.txt",
            r"test -s \\server\share\a",
        )
        for gate in refused:
            with self.subTest(gate=gate):
                result = run_gate_result(gate)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(b"Traceback", result.stderr)

    def test_git_gate_subcommands_are_read_only_and_non_network(self):
        admitted = ("git diff --check", "git status --short", "git show HEAD",
                    "git rev-parse HEAD", "git ls-files", "git cat-file -t HEAD")
        refused = ("git push", "git fetch", "git clone https://example.invalid/repo",
                   "git config user.name attacker", "git clean -fd",
                   "git diff --no-index outside other",
                   "git status --pathspec-from-file=/tmp/paths", "test src/a -nt outside",
                   "[ src/a -ef outside ]")
        for gate in admitted:
            with self.subTest(admitted=gate):
                self.assertEqual(run_gate(gate), 0)
        for gate in refused:
            with self.subTest(refused=gate):
                result = run_gate_result(gate)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(b"Traceback", result.stderr)

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
            "test -n foo", "[ -n foo ]", "test a = b", "test a != b", "[ a == b ]", "[ a != b ]",
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
            "test -s .recursion-result.json", "touch", "touch app/a",
            " " * 4090 + "git diff --check",
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


class AbsoluteControllerProgramTest(unittest.TestCase):
    controller_root = SOURCE.resolve()
    controller_commit = git_head(controller_root)
    controller_gate_file = "scripts/phase5_safety.py"
    controller_program = posix_absolute(controller_root / controller_gate_file)

    def run_controller_gate(self, candidate: str, controller_gate_files: str = controller_gate_file):
        return run_gate_cli(
            f"python3 {candidate}",
            allowed_paths=".",
            controller_root=self.controller_root,
            controller_commit=self.controller_commit,
            controller_gate_files=controller_gate_files,
        )

    def test_absolute_program_under_controller_root_and_declared_is_admitted(self):
        result = self.run_controller_gate(self.controller_program)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_absolute_program_outside_controller_root_reports_containment_reason(self):
        candidate = "/validate-gate-outside.py"
        result = self.run_controller_gate(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(
            result.stderr.strip(),
            "ERR acceptance program is outside the controller root",
        )
        self.assertNotIn(candidate, result.stderr)

    def test_absolute_program_under_controller_root_must_be_declared(self):
        result = self.run_controller_gate(self.controller_program, controller_gate_files="")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(
            result.stderr.strip(),
            f"ERR controller acceptance program must be declared: {self.controller_gate_file}",
        )

    def test_unsafe_program_paths_report_the_unsafe_path_reason(self):
        """Every unsafe spelling is refused, and each names the rule it broke.

        The reason differs by shape and that is deliberate, not an inconsistency:

        - an ABSOLUTE candidate is refused without echoing it, because an absolute path
          discloses host filesystem layout;
        - a RELATIVE candidate is echoed, because the caller supplied that exact spelling and
          it reveals nothing. The controls at lines 207-226 already pin that behaviour;
        - a `.` segment reads as shell indirection and is caught by that earlier rule.

        Asserting one message for all eight would either force absolute paths back into
        refusals or drop the specificity that says which rule fired.
        """
        refused = (
            ("scripts//gate.py", "ERR acceptance program path is unsafe: scripts//gate.py"),
            ("/opt/recursion//gate.py", "ERR acceptance program uses an unsafe path"),
            ("scripts/./gate.py", "ERR acceptance gate uses unreviewable shell indirection"),
            ("/opt/./gate.py", "ERR acceptance gate uses unreviewable shell indirection"),
            ("scripts/../../gate.py", "ERR acceptance program path is unsafe: scripts/../../gate.py"),
            ("/opt/recursion/../gate.py", "ERR acceptance program uses an unsafe path"),
            ("scripts/gate.py/", "ERR acceptance program path is unsafe: scripts/gate.py/"),
            ("/opt/recursion/gate.py/", "ERR acceptance program uses an unsafe path"),
        )
        for candidate, expected in refused:
            with self.subTest(candidate=candidate):
                result = self.run_controller_gate(candidate)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stderr.strip(), expected)
                if candidate.startswith("/"):
                    self.assertNotIn(candidate, result.stderr)

    def test_relative_declared_controller_program_is_admitted_outside_worker_scope(self):
        result = run_gate_cli(
            "python3 scripts/phase5_safety.py",
            allowed_paths="src",
            controller_root=self.controller_root,
            controller_commit=self.controller_commit,
            controller_gate_files=self.controller_gate_file,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


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


class GateFileIdentityTest(unittest.TestCase):
    def test_tracked_symlink_gate_file_is_rejected_without_following(self):
        spec = __import__("importlib.util").util.spec_from_file_location("validate_gate", GATE)
        module = __import__("importlib.util").util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        try:
            repo = explicit_scratch("validate-gate")
        except OSError as exc:
            self.skipTest(f"explicit scratch repository is unavailable on this host: {exc}")
        try:
            try:
                subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True)
            except (OSError, subprocess.CalledProcessError) as exc:
                self.skipTest(f"temporary test repository is unavailable on this host: {exc}")
            (repo / "app").mkdir()
            target = repo / "outside.txt"
            target.write_text("outside\n", encoding="utf-8")
            gate = repo / "app" / "check.py"
            gate.write_text("print('gate')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "gate-test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "gate-test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
            gate.unlink()
            try:
                gate.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable on this host: {exc}")
            with self.assertRaisesRegex(ValueError, "symlink or reparse"):
                module.clean_tracked_bytes(repo, "app/check.py")
        finally:
            try:
                shutil.rmtree(repo)
            except OSError:
                pass

    def test_candidate_gate_bytes_must_match_authoritative_baseline(self):
        spec = __import__("importlib.util").util.spec_from_file_location("validate_gate", GATE)
        module = __import__("importlib.util").util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        try:
            repo = explicit_scratch("validate-gate-baseline")
        except OSError as exc:
            self.skipTest(f"explicit scratch repository is unavailable on this host: {exc}")
        try:
            try:
                subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True)
            except (OSError, subprocess.CalledProcessError) as exc:
                self.skipTest(f"temporary test repository is unavailable on this host: {exc}")
            (repo / "app").mkdir()
            gate = repo / "app" / "check.py"
            gate.write_text("print('baseline')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "gate-test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "gate-test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
            baseline = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                      capture_output=True, text=True, check=True).stdout.strip()
            gate.write_text("print('substituted')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "candidate"], check=True)
            with self.assertRaisesRegex(ValueError, "authoritative baseline"):
                module.clean_tracked_bytes(repo, "app/check.py", baseline)
        finally:
            try:
                shutil.rmtree(repo)
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main(verbosity=2)

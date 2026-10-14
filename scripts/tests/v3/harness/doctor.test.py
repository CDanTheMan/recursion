#!/usr/bin/env python3
"""Doctor and init. Probes are fakes. No live provider process."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.cli import main  # noqa: E402
from scripts.v3.harness.config import load_config, starter_config, write_starter  # noqa: E402
from scripts.v3.harness.doctor import diagnose, discover_installed, resolve_executable  # noqa: E402
from scripts.v3.harness.errors import HarnessError  # noqa: E402


SECRET = "SECRET-TOKEN-VALUE"


def _completed(argv, code: int, stdout: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(argv, code, stdout=stdout, stderr=SECRET)


def _touch(directory: Path, name: str) -> None:
    path = directory / name
    path.write_text("", encoding="utf-8")


class DoctorTests(unittest.TestCase):
    def test_windows_shims_resolve_cmd_and_exe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _touch(root, "gemini.cmd")
            _touch(root, "cursor-agent.EXE")
            _touch(root, "opencode.CMD")
            search = str(root)
            gemini = resolve_executable("gemini", path=search, platform="win32", pathext=".EXE")
            cursor = resolve_executable("cursor-agent", path=search, platform="win32", pathext="")
            opencode = resolve_executable("opencode", path=search, platform="win32")
            self.assertIsNotNone(gemini)
            self.assertEqual(gemini.name, "gemini.cmd")
            self.assertIsNotNone(cursor)
            self.assertEqual(cursor.name, "cursor-agent.EXE")
            self.assertIsNotNone(opencode)
            self.assertEqual(opencode.name.casefold(), "opencode.cmd")
            _touch(root, "grok.ps1")
            grok = resolve_executable("grok", path=search, platform="win32", pathext=".EXE")
            self.assertIsNotNone(grok)
            self.assertEqual(grok.name, "grok.ps1")
            self.assertIsNone(resolve_executable("gemini", path=search, platform="linux"))

    def test_posix_uses_the_bare_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _touch(root, "gemini")
            _touch(root, "gemini.cmd")
            found = resolve_executable("gemini", path=str(root), platform="linux")
            self.assertIsNotNone(found)
            self.assertEqual(found.name, "gemini")

    def test_sign_in_checks_do_not_print_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            bindir = root / "bin"
            bindir.mkdir()
            home.mkdir()
            for name in ("claude", "codex", "grok", "gemini", "cursor-agent", "opencode"):
                _touch(bindir, name)
            (home / ".gemini").mkdir()
            (home / ".gemini" / "oauth_creds.json").write_text(SECRET, encoding="utf-8")
            (home / ".grok").mkdir()
            (home / ".grok" / "auth.json").write_text(SECRET, encoding="utf-8")
            calls: list[list[str]] = []

            def run(argv, timeout):
                del timeout
                calls.append(list(argv))
                self.assertNotIn(SECRET, " ".join(argv))
                if argv[1:] == ["--version"]:
                    return _completed(argv, 0, f"{Path(argv[0]).name} 1.2.3 {SECRET}\n")
                if argv[1:] == ["auth", "status"]:
                    body = json.dumps({"authMethod": "claude.ai", "token": SECRET})
                    return _completed(argv, 0, body + "\n")
                if argv[1:] == ["login", "status"]:
                    return _completed(argv, 0, f"logged in {SECRET}\n")
                if argv[1:] == ["status", "--format", "json"]:
                    return _completed(argv, 0, json.dumps({"loggedIn": True, "token": SECRET}))
                if argv[1:] == ["auth", "list"]:
                    return _completed(argv, 0, json.dumps([{"id": "openai", "token": SECRET}]))
                raise AssertionError(argv)

            def git_run(argv, timeout):
                del timeout
                self.assertNotIn("core.longpaths", argv)
                return _completed(argv, 0, "git version 2.45.0\n")

            config = load_config()
            report = diagnose(
                config,
                environ={"GEMINI_API_KEY": SECRET},
                platform="linux",
                home=home,
                path=str(bindir),
                run=run,
                git_run=git_run,
            )
            rendered = json.dumps(report)
            self.assertNotIn(SECRET, rendered)
            self.assertIn("[redacted]", rendered)
            rows = {item["name"]: item for item in report["providers"]}
            self.assertEqual(rows["fixture"]["signed_in"], "not-applicable")
            self.assertTrue(rows["fixture"]["usable"])
            self.assertEqual(rows["claude"]["signed_in"], "signed-in")
            self.assertEqual(rows["claude"]["auth_method"], "claude.ai")
            self.assertEqual(rows["claude"]["version"], "claude 1.2.3 [redacted]")
            self.assertEqual(rows["codex"]["auth_method"], "login-status")
            self.assertEqual(rows["grok"]["auth_method"], "cached")
            self.assertEqual(rows["gemini"]["auth_method"], "env")
            self.assertTrue(rows["gemini"]["installed"])
            self.assertFalse(rows["gemini"]["usable"])
            self.assertEqual(rows["cursor"]["signed_in"], "signed-in")
            self.assertEqual(rows["cursor"]["auth_method"], "status")
            self.assertFalse(rows["cursor"]["usable"])
            self.assertEqual(rows["opencode"]["auth_method"], "auth-list")
            self.assertTrue(report["ok"])
            self.assertTrue(report["git"]["available"])
            self.assertIsNone(report["git"]["longpaths"])
            self.assertTrue(all(SECRET not in " ".join(call) for call in calls))

    def test_cursor_signed_out_and_unknown_do_not_copy_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bindir = Path(directory)
            _touch(bindir, "cursor-agent")

            def run(argv, timeout):
                del timeout
                if argv[1:] == ["--version"]:
                    return _completed(argv, 0, "cursor-agent 2026.10.12\n")
                if argv[1:] == ["status", "--format", "json"]:
                    return _completed(
                        argv,
                        0,
                        '{"status":"unauthenticated","isAuthenticated":false,"message":"Not logged in '
                        + SECRET
                        + '"}\n',
                    )
                raise AssertionError(argv)

            config = starter_config({"cursor"})
            report = diagnose(
                config,
                environ={},
                platform="linux",
                home=bindir / "empty-home",
                path=str(bindir),
                run=run,
                git_run=lambda argv, timeout: _completed(argv, 0, "git version 2.45.0\n"),
            )
            cursor = {item["name"]: item for item in report["providers"]}["cursor"]
            self.assertEqual(cursor["signed_in"], "signed-out")
            self.assertNotIn(SECRET, json.dumps(report))

    def test_opencode_auth_list_reads_json_and_the_default_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bindir = Path(directory)
            _touch(bindir, "opencode")

            def run_signed_out(argv, timeout):
                del timeout
                if argv[1:] == ["--version"]:
                    return _completed(argv, 0, "opencode 1.0.0\n")
                if argv[1:] == ["auth", "list"]:
                    return _completed(argv, 0, "[]\n")
                raise AssertionError(argv)

            report = diagnose(
                starter_config({"opencode"}),
                environ={},
                platform="linux",
                home=bindir / "empty-home",
                path=str(bindir),
                run=run_signed_out,
                git_run=lambda argv, timeout: _completed(argv, 0, "git version 2.45.0\n"),
            )
            row = {item["name"]: item for item in report["providers"]}["opencode"]
            self.assertEqual(row["signed_in"], "signed-out")
            self.assertEqual(row["auth_method"], "auth-list")

            def run_text(argv, timeout):
                del timeout
                if argv[1:] == ["--version"]:
                    return _completed(argv, 0, "opencode 1.0.0\n")
                if argv[1:] == ["auth", "list"]:
                    return _completed(
                        argv,
                        0,
                        "\u250c  Credentials \x1b[90m~/.local/share/opencode/auth.json\n\u2502\n\u2514  0 credentials\n",
                    )
                raise AssertionError(argv)

            text_report = diagnose(
                starter_config({"opencode"}),
                environ={},
                platform="linux",
                home=bindir / "empty-home",
                path=str(bindir),
                run=run_text,
                git_run=lambda argv, timeout: _completed(argv, 0, "git version 2.45.0\n"),
            )
            text_row = {item["name"]: item for item in text_report["providers"]}["opencode"]
            self.assertEqual(text_row["signed_in"], "signed-out")

            creds = bindir / "home" / ".local" / "share" / "opencode"
            creds.mkdir(parents=True)
            (creds / "auth.json").write_text(SECRET, encoding="utf-8")
            calls: list[list[str]] = []

            def run_cached(argv, timeout):
                del timeout
                calls.append(list(argv))
                if argv[1:] == ["--version"]:
                    return _completed(argv, 0, "opencode 1.0.0\n")
                raise AssertionError(argv)

            cached = diagnose(
                starter_config({"opencode"}),
                environ={},
                platform="linux",
                home=bindir / "home",
                path=str(bindir),
                run=run_cached,
                git_run=lambda argv, timeout: _completed(argv, 0, "git version 2.45.0\n"),
            )
            cached_row = {item["name"]: item for item in cached["providers"]}["opencode"]
            self.assertEqual(cached_row["signed_in"], "signed-in")
            self.assertEqual(cached_row["auth_method"], "cached")
            self.assertNotIn(SECRET, json.dumps(cached))
            self.assertTrue(all(call[1:] == ["--version"] for call in calls))

    def test_windows_longpaths_and_missing_git(self) -> None:
        config = starter_config({"fixture"})

        def git_true(argv, timeout):
            del timeout
            if argv[-1:] == ["core.longpaths"]:
                return _completed(argv, 0, "true\n")
            return _completed(argv, 0, "git version 2.45.0\n")

        enabled = diagnose(config, environ={}, platform="win32", home=Path("/unused"), path="", run=_unused, git_run=git_true)
        self.assertTrue(enabled["git"]["longpaths"])
        self.assertTrue(enabled["ok"])

        def git_unset(argv, timeout):
            del timeout
            if argv[-1:] == ["core.longpaths"]:
                return _completed(argv, 1, "")
            return _completed(argv, 0, "git version 2.45.0\n")

        unset = diagnose(config, environ={}, platform="win32", home=Path("/unused"), path="", run=_unused, git_run=git_unset)
        self.assertFalse(unset["git"]["longpaths"])

        def git_missing(argv, timeout):
            del argv, timeout
            raise FileNotFoundError("git")

        missing = diagnose(
            config, environ={}, platform="win32", home=Path("/unused"), path="", run=_unused, git_run=git_missing
        )
        self.assertFalse(missing["git"]["available"])
        self.assertIsNone(missing["git"]["longpaths"])
        self.assertTrue(missing["ok"])

    def test_no_enabled_provider_is_a_failure(self) -> None:
        report = diagnose(
            starter_config(set()),
            environ={},
            platform="linux",
            home=Path("/unused"),
            path="",
            run=_unused,
            git_run=lambda argv, timeout: _completed(argv, 0, "git version 2.45.0\n"),
        )
        self.assertFalse(report["ok"])
        self.assertTrue(all(not item["usable"] for item in report["providers"]))

    def test_init_refuses_overwrite_and_enables_installed_providers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bindir = root / "bin"
            bindir.mkdir()
            _touch(bindir, "gemini.cmd")
            _touch(bindir, "cursor-agent.exe")
            found = discover_installed(environ={}, platform="win32", path=str(bindir))
            self.assertEqual(found, ["fixture", "gemini", "cursor"])
            target = root / "nested" / "harness.json"
            payload = write_starter(target, set(found))
            loaded = load_config(target)
            enabled = [item["name"] for item in loaded["providers"] if item["enabled"]]
            self.assertEqual(enabled, ["fixture", "gemini", "cursor"])
            self.assertEqual(
                payload["providers"][4]["argv"],
                ["gemini", "-p", "--output-format", "stream-json", "--approval-mode", "yolo", "--skip-trust"],
            )
            target.write_text('{"keep": true}\n', encoding="utf-8")
            with self.assertRaises(HarnessError) as caught:
                write_starter(target, set(found))
            self.assertIn("--force", str(caught.exception))
            self.assertEqual(target.read_text(encoding="utf-8"), '{"keep": true}\n')
            write_starter(target, {"fixture"}, force=True)
            self.assertEqual(
                [item["name"] for item in load_config(target)["providers"] if item["enabled"]],
                ["fixture"],
            )

    def test_cli_doctor_exits_nonzero_and_init_writes(self) -> None:
        stdout = StringIO()
        with patch("scripts.v3.harness.cli.diagnose", return_value={"ok": False, "git": {}, "providers": []}), patch(
            "sys.stdout", stdout
        ):
            code = main(["doctor"])
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(stdout.getvalue())["ok"])

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "harness.json"
            target.write_text("{}\n", encoding="utf-8")
            stderr = StringIO()
            with patch("sys.stderr", stderr):
                code = main(["init", str(target)])
            self.assertEqual(code, 2)
            self.assertEqual(target.read_text(encoding="utf-8"), "{}\n")
            self.assertIn("--force", stderr.getvalue())
            stdout = StringIO()
            with patch("scripts.v3.harness.cli.discover_installed", return_value=["fixture", "opencode"]), patch(
                "sys.stdout", stdout
            ):
                code = main(["init", str(target), "--force"])
            self.assertEqual(code, 0)
            loaded = load_config(target)
            enabled = [item["name"] for item in loaded["providers"] if item["enabled"]]
            self.assertEqual(enabled, ["fixture", "opencode"])
            self.assertEqual(
                [item["argv"] for item in loaded["providers"] if item["name"] == "opencode"],
                [["opencode", "run", "--format", "json", "--auto"]],
            )


def _unused(argv, timeout):
    del timeout
    raise AssertionError(argv)


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_DOCTOR_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

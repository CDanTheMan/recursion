#!/usr/bin/env python3
"""Adversarial controls for Phase 8 allowed_paths: injection is refused before materialization."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
PILOT = SOURCE / "scripts" / "project-pilot.py"


def load_pilot():
    if "fcntl" not in sys.modules:
        fcntl = types.ModuleType("fcntl")
        fcntl.LOCK_EX = 2
        fcntl.LOCK_NB = 4
        fcntl.flock = lambda _file, _flags: None  # type: ignore[attr-defined]
        sys.modules["fcntl"] = fcntl
    spec = importlib.util.spec_from_file_location("project_pilot_hardening", PILOT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load project-pilot")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AllowedPathTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pilot = load_pilot()
        cls.cfg = {"allowed_paths": ["user-client/render"]}

    def valid(self, scope: str) -> bool:
        return self.pilot.valid_allowed_path(scope)

    def test_specific_relative_paths_are_materializable(self):
        for scope in ("app", "user-client/render", "src/main", "a.b/c-d/e_f", "0x6c"):
            with self.subTest(scope=scope):
                self.assertTrue(self.valid(scope))

    def test_commas_whitespace_and_control_bytes_are_refused(self):
        for scope in (
            "app,scripts",
            "app scripts",
            "app, scripts",
            "app\tx",
            "app\nx",
            "app\rx",
            "app\x00x",
            "app\x1fx",
        ):
            with self.subTest(scope=scope):
                self.assertFalse(self.valid(scope))

    def test_absolute_dot_and_dotdot_paths_are_refused(self):
        for scope in (
            "/etc/passwd",
            "\\etc\\passwd",
            ".",
            "..",
            "app/../scripts",
            "app/../../etc",
            "../app",
            "./app",
            "app/./sub",
            "app/",
            "/app",
            "C:\\windows",
        ):
            with self.subTest(scope=scope):
                self.assertFalse(self.valid(scope))

    def test_shell_and_delimiter_injection_is_refused(self):
        for scope in (
            "app;rm",
            "app|sh",
            "app&sh",
            "app>x",
            "app<x",
            "app`id`",
            "app$(id)",
            "app$HOME",
            "app'",
            'app"',
            "app*",
            "app?",
            "app[1]",
            "app=scripts",
        ):
            with self.subTest(scope=scope):
                self.assertFalse(self.valid(scope))

    def test_scope_membership_rejects_injected_and_out_of_charter_paths(self):
        for scope in (
            "user-client/render",
            "user-client/render/tools",
            "user-client/render/tools/native-diff.cjs",
        ):
            with self.subTest(scope=scope):
                self.assertTrue(self.pilot.scope_allowed(self.cfg, scope))
        for scope in (
            "user-client/render,scripts",
            "user-client/render scripts",
            "user-client/../scripts",
            "/etc/passwd",
            ".",
            "..",
            "user-client",
            "other",
        ):
            with self.subTest(scope=scope):
                self.assertFalse(self.pilot.scope_allowed(self.cfg, scope))


if __name__ == "__main__":
    unittest.main(verbosity=2)

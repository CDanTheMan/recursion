#!/usr/bin/env python3
"""Scope-check tests for tools/check_v3_orientation.py.

These cover the merge-base comparison only. They do not replace the three
schema checks, three fixture checks, or seventeen M1 test programs.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_v3_orientation as gate  # noqa: E402


HISTORICAL = "797be4f18edf3f9e0f2dbac9432f190dbe1ed969"


class GitRepo:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._git("init", "-b", "master")
        self._git("config", "user.name", "Scope Test")
        self._git("config", "user.email", "scope@example.com")
        self._git("config", "commit.gpgsign", "false")
        self._git("config", "core.autocrlf", "false")
        self._git("config", "core.eol", "lf")

    def _git(self, *args: str) -> str:
        return subprocess.check_output(
            ["git", *args], cwd=self.root, encoding="utf-8"
        ).strip()

    def write(self, name: str, text: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def commit(self, message: str, *paths: str) -> None:
        if paths:
            self._git("add", "--", *paths)
        else:
            self._git("add", "-A")
        self._git("commit", "-m", message)

    def rev(self, ref: str = "HEAD") -> str:
        return self._git("rev-parse", ref)

    def checkout(self, branch: str, new: bool = False) -> None:
        if new:
            self._git("checkout", "-q", "-b", branch)
        else:
            self._git("checkout", "-q", branch)

    def outside(self, baseline: str | None = None) -> list[str]:
        head = self.rev()
        base = gate.comparison_base(self.root, head, baseline)
        changed, untracked = gate.scope_paths(self.root, base)
        return gate.out_of_scope(changed, untracked, gate.ALLOWED)


class ScopeCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = GitRepo(Path(self.tmp.name))
        self.repo.write("README.md", "allowed\n")
        self.repo.write("notes.txt", "on master, not in the allowlist\n")
        self.repo.commit("base")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_historical_pin_is_unchanged(self) -> None:
        self.assertEqual(gate.HISTORICAL_BASELINE, HISTORICAL)
        self.assertEqual(gate.BASELINE, HISTORICAL)

    def test_clean_master_has_no_out_of_scope_changes(self) -> None:
        self.assertEqual(self.repo.outside(), [])
        self.assertEqual(gate.comparison_base(self.repo.root, self.repo.rev(), None), self.repo.rev())

    def test_master_advance_is_in_scope_until_the_worktree_diverges(self) -> None:
        pin = self.repo.rev()
        self.repo.write("later.txt", "landed on master after the pin\n")
        self.repo.commit("later master file", "later.txt")
        self.assertEqual(self.repo.outside(), [])
        self.assertEqual(self.repo.outside(pin), ["later.txt"])

    def test_work_branch_flags_its_own_out_of_scope_file_only(self) -> None:
        self.repo.checkout("work", new=True)
        self.repo.write("evil.txt", "branch-only\n")
        self.repo.commit("out of scope", "evil.txt")
        self.repo.checkout("master")
        self.repo.write("later.txt", "merged to master\n")
        self.repo.commit("master moves on", "later.txt")
        self.repo.checkout("work")
        self.assertEqual(self.repo.outside(), ["evil.txt"])

    def test_work_branch_allowed_edit_passes(self) -> None:
        self.repo.checkout("work", new=True)
        self.repo.write("README.md", "allowed edit\n")
        self.repo.commit("in scope", "README.md")
        self.assertEqual(self.repo.outside(), [])

    def test_dirty_master_flags_untracked_and_edited_paths_outside_the_allowlist(self) -> None:
        self.repo.write("evil.txt", "untracked\n")
        self.repo.write("notes.txt", "edited\n")
        self.assertEqual(self.repo.outside(), ["evil.txt", "notes.txt"])

    def test_dirty_master_allows_an_allowlisted_edit(self) -> None:
        self.repo.write("README.md", "dirty but allowed\n")
        self.assertEqual(self.repo.outside(), [])

    def test_stale_local_master_does_not_flag_origin_master(self) -> None:
        stale = self.repo.rev()
        self.repo.checkout("upstream", new=True)
        self.repo.write("upstream.txt", "on origin/master\n")
        self.repo.commit("upstream", "upstream.txt")
        self.repo._git("update-ref", "refs/remotes/origin/master", "HEAD")
        self.repo.checkout("feature", new=True)
        self.repo.write("evil.txt", "real branch change\n")
        self.repo.commit("feature change", "evil.txt")
        self.repo._git("update-ref", "refs/heads/master", stale)
        self.assertEqual(self.repo.outside(), ["evil.txt"])

    def test_origin_master_alone_is_enough(self) -> None:
        self.repo._git("update-ref", "refs/remotes/origin/master", "HEAD")
        self.repo._git("checkout", "-q", "--detach")
        self.repo._git("update-ref", "-d", "refs/heads/master")
        self.assertEqual(self.repo.outside(), [])

    def test_missing_master_ref_fails(self) -> None:
        self.repo._git("checkout", "-q", "--detach")
        self.repo._git("update-ref", "-d", "refs/heads/master")
        with self.assertRaises(ValueError):
            self.repo.outside()

    def test_baseline_that_is_not_an_ancestor_fails(self) -> None:
        self.repo.checkout("side", new=True)
        self.repo.write("side.txt", "side\n")
        self.repo.commit("side", "side.txt")
        side = self.repo.rev()
        self.repo.checkout("master")
        with self.assertRaises(ValueError):
            self.repo.outside(side)

    def test_whitespace_on_master_is_not_judged_against_an_older_pin(self) -> None:
        pin = self.repo.rev()
        self.repo.write("notes.txt", "trailing space \n")
        self.repo.commit("whitespace landed on master", "notes.txt")
        gate.check_whitespace(self.repo.root, self.repo.rev())
        with self.assertRaises(ValueError):
            gate.check_whitespace(self.repo.root, pin)

    def test_work_branch_trailing_whitespace_still_fails(self) -> None:
        self.repo.checkout("work", new=True)
        self.repo.write("README.md", "allowed but trailing \n")
        self.repo.commit("whitespace", "README.md")
        base = gate.comparison_base(self.repo.root, self.repo.rev(), None)
        with self.assertRaises(ValueError):
            gate.check_whitespace(self.repo.root, base)

    def test_allowlist_still_rejects_paths_outside_the_repair(self) -> None:
        self.assertIn("tools/check_v3_orientation.py", gate.ALLOWED)
        self.assertIn(".github/workflows/ci.yml", gate.ALLOWED)
        self.assertIn("requirements.txt", gate.ALLOWED)
        self.assertIn(".gitattributes", gate.ALLOWED)
        self.assertIn("tests/test_v3_checks.py", gate.ALLOWED)
        self.assertIn("tests/test_docs_drift.py", gate.ALLOWED)
        self.assertIn("tests/test_adapter_streams.py", gate.ALLOWED)
        self.assertIn("tests/test_e2e_console.py", gate.ALLOWED)
        self.assertIn("tests/test_process_lifecycle.py", gate.ALLOWED)
        self.assertIn("examples/sample-goal.txt", gate.ALLOWED)
        self.assertIn("examples/harness.json", gate.ALLOWED)
        self.assertIn("examples/stubs/provider_stub.py", gate.ALLOWED)
        self.assertIn("tests/test_config_logs.py", gate.ALLOWED)
        self.assertIn("config/harness.schema.json", gate.PRODUCT_SLICE)
        self.assertIn("scripts/v3/harness/redact.py", gate.PRODUCT_SLICE)
        self.assertIn("pyproject.toml", gate.ALLOWED)
        self.assertIn("docs/USER-GUIDE.md", gate.ALLOWED)
        self.assertIn("docs/ARCHITECTURE.md", gate.ALLOWED)
        self.assertIn("CHANGELOG.md", gate.ALLOWED)
        self.assertIn(".github/workflows/release.yml", gate.ALLOWED)
        self.assertNotIn("docs/v3/RESEARCH-SCOPE.md", gate.ALLOWED)
        self.assertNotIn("schemas/control-plane/v3/planning/materialize.py", gate.ALLOWED)
        self.assertNotIn("scripts/v3/harness/cli.py", gate.ALLOWED)
        self.assertEqual(gate.normalize_git_path('"tools\\check.py"'), "tools/check.py")
        self.assertEqual(
            gate.out_of_scope({"scripts\\v3\\harness\\cli.py"}, set(), gate.ALLOWED),
            ["scripts/v3/harness/cli.py"],
        )
        self.assertEqual(
            gate.out_of_scope({"README.md", "docs/v3/RESEARCH-SCOPE.md"}, set(), gate.ALLOWED),
            ["docs/v3/RESEARCH-SCOPE.md"],
        )

    def test_contract_inventory_is_unchanged(self) -> None:
        programs = gate.contract_programs()
        schemas = [p for p in programs if p[0].endswith("/materialize.py")]
        fixtures = [p for p in programs if p[0].endswith("/materialize_fixtures.py")]
        tests = [p for p in programs if p[0].endswith(".test.py")]
        self.assertEqual(len(programs), 23)
        self.assertEqual(len(schemas), 3)
        self.assertEqual(len(fixtures), 3)
        self.assertEqual(len(tests), 17)
        self.assertEqual(
            [p[0] for p in schemas],
            [
                "schemas/control-plane/v3/planning/materialize.py",
                "schemas/control-plane/v3/execution/materialize.py",
                "schemas/control-plane/v3/integrity/materialize.py",
            ],
        )
        self.assertTrue(all(p[1:] == ("--check",) for p in schemas + fixtures))
        self.assertTrue(all(len(p) == 1 for p in tests))
        areas = ("planning", "execution", "integrity")
        self.assertEqual(
            [p[0] for p in fixtures],
            [f"scripts/tests/v3/{area}/materialize_fixtures.py" for area in areas],
        )


if __name__ == "__main__":
    unittest.main()

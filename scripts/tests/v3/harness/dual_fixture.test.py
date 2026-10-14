#!/usr/bin/env python3
"""Shipped config: two offline fixtures review, one fixture stays unreviewed."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.clean import clean_runs  # noqa: E402
from scripts.v3.harness.cli import main  # noqa: E402
from scripts.v3.harness.config import load_config  # noqa: E402
from scripts.v3.harness.land import land_run  # noqa: E402
from scripts.v3.harness.state import RunStore  # noqa: E402


class DualFixtureTests(unittest.TestCase):
    def test_default_config_reviews_lands_and_can_be_cleaned(self) -> None:
        config = load_config()
        self.assertFalse(config["review"]["accept_unreviewed"])
        enabled = [item["name"] for item in config["providers"] if item["enabled"]]
        self.assertIn("fixture", enabled)
        self.assertIn("fixture-b", enabled)
        self.assertEqual(config["routing"]["weights"]["fixture"], config["routing"]["weights"]["fixture-b"])
        self.assertLess(
            config["routing"]["preference"].index("fixture"),
            config["routing"]["preference"].index("fixture-b"),
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = None
            land_branch = None
            land_tree = None
            land_parent = None
            try:
                code, payload = _run(["run", "--task", "Say hello", "--state-dir", str(root)])
                self.assertEqual(code, 0)
                self.assertEqual(payload["status"], "completed")
                self.assertEqual(payload["execution"]["provider"], "fixture")
                self.assertFalse(payload["execution"]["live"])
                self.assertIn("fixture", payload["candidates"])
                self.assertIn("fixture-b", payload["candidates"])
                self.assertEqual(payload["reviews"][0]["verdict"], "approve")
                self.assertEqual(payload["reviews"][0]["reviewer"], "fixture-b")
                self.assertNotEqual(payload["execution"]["provider"], payload["reviews"][0]["reviewer"])
                self.assertIn("fixture-b review", payload["reviews"][0]["notes"])

                run_id = payload["run_id"]
                head = _rev("HEAD")
                land_branch = f"fixture-land-{run_id[4:].lower()}"
                land_parent = Path(tempfile.mkdtemp(prefix="recursion-fixture-land-"))
                land_tree = land_parent / "wt"
                added = subprocess.run(
                    ["git", "worktree", "add", "-b", land_branch, str(land_tree), "HEAD"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(added.returncode, 0, added.stderr)
                landed = land_run(RunStore(root), run_id, repo=land_tree, into=land_branch)
                self.assertEqual(landed["status"], "completed")
                self.assertEqual(landed["land"]["status"], "merged")
                self.assertEqual(landed["land"]["branch"], land_branch)
                self.assertTrue(landed["land"]["commit"])
                self.assertEqual(_rev("HEAD"), head)

                cleaned = clean_runs(
                    RunStore(root),
                    repo=ROOT,
                    older_than_days=0,
                    dry_run=True,
                    now=time.time() + 86400 * 2,
                )
                removed = [item["run_id"] for item in cleaned["removed"]]
                self.assertIn(run_id, removed)
                self.assertFalse(
                    any(
                        item.get("run_id") == run_id and item.get("reason") == "unlanded"
                        for item in cleaned["skipped"]
                    )
                )
            finally:
                if land_tree is not None:
                    subprocess.run(
                        ["git", "worktree", "remove", "--force", str(land_tree)],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                subprocess.run(["git", "worktree", "prune"], cwd=ROOT, capture_output=True, check=False)
                if land_branch is not None:
                    subprocess.run(
                        ["git", "branch", "-D", land_branch], cwd=ROOT, capture_output=True, text=True, check=False
                    )
                if land_parent is not None:
                    shutil.rmtree(land_parent, ignore_errors=True)
                if payload is not None and payload.get("run_id"):
                    _drop_run_branches(payload["run_id"])

    def test_rotated_tasks_let_either_fixture_review_the_other(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, payload = _run(
                ["run", "--goal", "Alpha task.\nBeta task.", "--state-dir", str(root)]
            )
            try:
                self.assertEqual(code, 0)
                self.assertEqual(payload["status"], "completed")
                self.assertEqual([task["provider"] for task in payload["tasks"]], ["fixture", "fixture-b"])
                self.assertEqual(
                    [task["reviews"][0]["reviewer"] for task in payload["tasks"]],
                    ["fixture-b", "fixture"],
                )
                self.assertTrue(all(task["reviews"][0]["verdict"] == "approve" for task in payload["tasks"]))
                self.assertTrue(all(task["execution"]["live"] is False for task in payload["tasks"]))
            finally:
                _drop_run_branches(payload["run_id"])

    def test_one_fixture_stays_unreviewed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            only = _config(root / "only.json", enabled={"fixture"})
            code, payload = _run(
                ["run", "--task", "Say hello", "--state-dir", str(root), "--config", str(only)]
            )
            try:
                self.assertEqual(code, 2)
                self.assertEqual(payload["status"], "unreviewed")
                self.assertEqual(payload["candidates"], ["fixture"])
                self.assertEqual(payload["reviews"][0]["verdict"], "skipped")
                self.assertEqual(payload["reviews"][0]["notes"], "no distinct reviewer")
                self.assertIsNone(payload["reviews"][0]["reviewer"])
            finally:
                _drop_run_branches(payload["run_id"])

            shipped = _config(root / "shipped-minus-b.json", enabled=None, disable={"fixture-b"})
            code, payload = _run(
                ["run", "--task", "Say hello", "--state-dir", str(root / "state"), "--config", str(shipped)]
            )
            try:
                self.assertEqual(code, 2)
                self.assertEqual(payload["status"], "unreviewed")
                self.assertNotIn("fixture-b", payload["candidates"])
                self.assertIn("fixture", payload["candidates"])
                self.assertEqual(payload["reviews"][0]["verdict"], "skipped")
                self.assertEqual(payload["reviews"][0]["notes"], "no reviewer completed")
            finally:
                _drop_run_branches(payload["run_id"])


def _run(args: list[str]) -> tuple[int, dict]:
    stdout = StringIO()
    stderr = StringIO()
    with patch("sys.stdout", stdout), patch("sys.stderr", stderr), patch(
        "scripts.v3.harness.providers.run_command"
    ) as spawned:
        code = main(args)
    spawned.assert_not_called()
    if not stdout.getvalue():
        raise AssertionError(stderr.getvalue())
    return code, json.loads(stdout.getvalue())


def _config(path: Path, *, enabled: set[str] | None, disable: set[str] | None = None) -> Path:
    raw = json.loads((ROOT / "config" / "harness.json").read_text(encoding="utf-8"))
    if raw["review"]["accept_unreviewed"] is not False:
        raise AssertionError("shipped config must keep accept_unreviewed false")
    for item in raw["providers"]:
        if enabled is not None:
            item["enabled"] = item["name"] in enabled
        elif disable and item["name"] in disable:
            item["enabled"] = False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(raw), encoding="utf-8")
    return path


def _rev(ref: str) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", ref], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return completed.stdout.strip()


def _drop_run_branches(run_id: str) -> None:
    listed = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/recursion"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    prefixes = (f"recursion/run/{run_id}", f"recursion/task/{run_id}/")
    for name in listed.stdout.split():
        if name == prefixes[0] or name.startswith(prefixes[1]):
            completed = subprocess.run(
                ["git", "branch", "-D", name], cwd=ROOT, capture_output=True, text=True, check=False
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or f"could not delete {name}")
    subprocess.run(["git", "worktree", "prune"], cwd=ROOT, capture_output=True, check=False)


def main_tests() -> int:
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("HARNESS_DUAL_FIXTURE_PASS")
    return 0 if result.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main_tests())

#!/usr/bin/env python3
"""The project status surface must never translate unreadable state into empty state."""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock


SOURCE = pathlib.Path(__file__).resolve().parents[2]


def load_project_pilot():
    if os.name == "nt":
        sys.modules.setdefault(
            "fcntl",
            types.SimpleNamespace(LOCK_EX=2, LOCK_NB=4, flock=lambda *_args: None),
        )
    spec = importlib.util.spec_from_file_location(
        "project_pilot_status_control", SOURCE / "scripts/project-pilot.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PROJECT_PILOT = load_project_pilot()


class Fixture:
    def __init__(self) -> None:
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="project-status-"))
        for relative in (
            "state/project-config",
            "state/pilots",
            "state/goals",
            "state/tasks",
            "state/runs",
            "state/evidence",
            "state/plans/chiron",
            "state/pilot-windows",
            "state/assists",
            "loop/logs",
        ):
            (self.root / relative).mkdir(parents=True)
        (self.root / "state/portfolio.tsv").write_text(
            "#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n"
            "chiron\t/repo\torigin\tmain\t-\t-\t10\tactive\n",
            encoding="utf-8",
        )
        config = {
            "id": "chiron",
            "pilot_id": "pilot-chiron",
            "topic": 10,
            "charter": "fixture charter",
            "status": "active",
        }
        pilot = {
            "id": "pilot-chiron",
            "project_id": "chiron",
            "topic": 10,
            "charter": "fixture charter",
            "status": "active",
        }
        self.write_json("state/project-config/chiron.json", config)
        self.write_json("state/pilots/pilot-chiron.json", pilot)
        self.goal = self.root / "state/goals/goal-chiron.md"
        self.goal.write_text(
            "id: goal-chiron\nproject_id: chiron\nstatus: active\n", encoding="utf-8"
        )
        (self.root / "state/tasks/task-chiron.md").write_text(
            "id: task-chiron\nproject_id: chiron\ngoal_id: goal-chiron\nstatus: proposed\n",
            encoding="utf-8",
        )
        self.write_json(
            "state/plans/chiron/plan-chiron.json",
            {"id": "plan-chiron", "project_id": "chiron", "status": "approved"},
        )
        self.write_json(
            "state/pilot-windows/window-chiron.json",
            {
                "id": "window-chiron",
                "project_id": "chiron",
                "goal_id": "goal-chiron",
                "status": "armed",
            },
        )

    def write_json(self, relative: str, value: object) -> None:
        (self.root / relative).write_text(
            json.dumps(value, sort_keys=True) + "\n", encoding="utf-8"
        )

    def close(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


class StatusFailClosedTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = Fixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_readable_status_contains_authoritative_records(self) -> None:
        value = PROJECT_PILOT.scoped_state(self.fixture.root, "chiron")
        self.assertEqual(len(value["plans"]), 1)
        self.assertEqual(len(value["goals"]), 1)
        self.assertEqual(len(value["tasks"]), 1)
        self.assertEqual(len(value["pilot_windows"]), 1)

    def test_unlistable_control_directory_is_not_reported_as_empty(self) -> None:
        denied = self.fixture.root / "state/plans/chiron"
        original = os.scandir

        def controlled_scandir(path):
            if pathlib.Path(path) == denied:
                raise PermissionError(13, "permission denied", str(path))
            return original(path)

        with mock.patch.object(PROJECT_PILOT.os, "scandir", side_effect=controlled_scandir):
            with self.assertRaises(SystemExit) as raised:
                PROJECT_PILOT.scoped_state(self.fixture.root, "chiron")
        self.assertEqual(raised.exception.code, 74)

    def test_unreadable_control_record_is_not_silently_omitted(self) -> None:
        original = pathlib.Path.read_text

        def controlled_read(path, *args, **kwargs):
            if path == self.fixture.goal:
                raise PermissionError(13, "permission denied", str(path))
            return original(path, *args, **kwargs)

        with mock.patch.object(pathlib.Path, "read_text", controlled_read):
            with self.assertRaises(SystemExit) as raised:
                PROJECT_PILOT.scoped_state(self.fixture.root, "chiron")
        self.assertEqual(raised.exception.code, 74)


if __name__ == "__main__":
    unittest.main(verbosity=2)

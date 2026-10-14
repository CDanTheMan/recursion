"""Drive the installed recursion console script against PATH stubs.

The stubs are the only claude, codex, and grok executables on PATH. Live mode
is enabled only for those stubs. The goal and config come from examples/.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
GOAL_PATH = EXAMPLES / "sample-goal.txt"
CONFIG_PATH = EXAMPLES / "harness.json"
STUB_SOURCE = EXAMPLES / "stubs" / "provider_stub.py"
PROVIDERS = ("claude", "codex", "grok")


def _goal_lines() -> list[str]:
    text = GOAL_PATH.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    assert len(lines) >= 2
    return lines


def _install_stubs(directory: Path) -> None:
    directory.mkdir()
    stub = directory / "provider_stub.py"
    shutil.copyfile(STUB_SOURCE, stub)
    executable = sys.executable
    for name in PROVIDERS:
        if os.name == "nt":
            launcher = directory / f"{name}.cmd"
            launcher.write_text(
                "\r\n".join(
                    (
                        "@echo off",
                        f"set RECURSION_STUB_PROVIDER={name}",
                        f"\"{executable}\" -X utf8 \"{stub}\" %*",
                        "",
                    )
                ),
                encoding="utf-8",
                newline="",
            )
        else:
            launcher = directory / name
            launcher.write_text(
                "\n".join(
                    (
                        "#!/bin/sh",
                        f"export RECURSION_STUB_PROVIDER={name}",
                        f"exec \"{executable}\" -X utf8 \"{stub}\" \"$@\"",
                        "",
                    )
                ),
                encoding="utf-8",
            )
            launcher.chmod(launcher.stat().st_mode | stat.S_IEXEC)


def _env(stub_dir: Path, log_path: Path, *, fail: bool) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = str(stub_dir) + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["RECURSION_STUB_LOG"] = str(log_path)
    if fail:
        env["RECURSION_STUB_MODE"] = "fail"
    else:
        env.pop("RECURSION_STUB_MODE", None)
    return env


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _head() -> str:
    completed = _git("rev-parse", "HEAD")
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


def _recursion_branches() -> set[str]:
    completed = _git("for-each-ref", "--format=%(refname:short)", "refs/heads/recursion")
    return {line.strip() for line in completed.stdout.splitlines() if line.strip()}


def _cleanup_branches(before: set[str]) -> None:
    extra = _recursion_branches() - before
    listed = _git("worktree", "list", "--porcelain")
    path = None
    branch = None
    removals: list[str] = []
    for line in listed.stdout.splitlines() + [""]:
        if line.startswith("worktree "):
            path = line.split(" ", 1)[1]
            branch = None
        elif line.startswith("branch "):
            branch = line.split(" ", 1)[1].removeprefix("refs/heads/")
        elif line == "" and path is not None:
            if branch in extra and Path(path).resolve() != ROOT.resolve():
                removals.append(path)
            path = None
            branch = None
    for checkout in removals:
        _git("worktree", "remove", "--force", checkout)
    _git("worktree", "prune")
    if extra:
        _git("branch", "-D", *sorted(extra))


def _recursion() -> str:
    found = shutil.which("recursion")
    if not found:
        pytest.fail("recursion is not on PATH; install with python -m pip install -e .")
    return found


def _run(recursion: str, args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [recursion, *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _json_stdout(completed: subprocess.CompletedProcess[str]) -> dict:
    assert completed.stdout, completed.stderr
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{completed.stderr}\n{completed.stdout}") from exc
    assert isinstance(payload, dict)
    return payload


def test_windows_stub_cmd_starts_python_directly(tmp_path: Path) -> None:
    stub = tmp_path / "provider_stub.py"
    stub.write_text("print('ok')\n", encoding="utf-8")
    executable = r"C:\Python\python.exe"
    launcher = tmp_path / "claude.cmd"
    launcher.write_text(
        "\r\n".join(
            (
                "@echo off",
                "set RECURSION_STUB_PROVIDER=claude",
                f"\"{executable}\" -X utf8 \"{stub}\" %*",
                "",
            )
        ),
        encoding="utf-8",
        newline="",
    )
    from scripts.v3.harness.providers import _stub_launch

    command, overlay = _stub_launch(str(launcher))
    assert command == [executable, "-X", "utf8", str(stub)]
    assert overlay == {"RECURSION_STUB_PROVIDER": "claude"}


def test_console_script_plans_runs_cancels_and_resumes(tmp_path: Path) -> None:
    goal_lines = _goal_lines()
    goal = "\n".join(goal_lines)
    stub_dir = tmp_path / "bin"
    state_dir = tmp_path / "state"
    stub_log = tmp_path / "stub-log.txt"
    _install_stubs(stub_dir)
    recursion = _recursion()
    common = ["--config", str(CONFIG_PATH), "--state-dir", str(state_dir)]
    head = _head()
    branches = _recursion_branches()

    try:
        _exercise(recursion, common, goal, goal_lines, stub_dir, stub_log, state_dir, head)
    finally:
        _cleanup_branches(branches)
        assert _head() == head
        assert _recursion_branches() == branches


def _exercise(
    recursion: str,
    common: list[str],
    goal: str,
    goal_lines: list[str],
    stub_dir: Path,
    stub_log: Path,
    state_dir: Path,
    head: str,
) -> None:
    planned = _run(recursion, ["plan", "--goal", goal, *common], _env(stub_dir, stub_log, fail=False))
    assert planned.returncode == 0, planned.stderr
    plan_payload = _json_stdout(planned)
    assert plan_payload["route"]["status"] == "selected"
    assert plan_payload["plan_source"] == "lines"
    assert [item["intent_text"] for item in plan_payload["tasks"]] == goal_lines

    failed = _run(
        recursion,
        ["run", "--goal", goal, "--allow-live", *common],
        _env(stub_dir, stub_log, fail=True),
    )
    assert failed.returncode == 2, failed.stderr
    assert "SECRET" not in failed.stdout
    assert "SECRET" not in failed.stderr
    failed_payload = _json_stdout(failed)
    run_id = failed_payload["run_id"]
    assert failed_payload["status"] == "failed"
    for item in failed_payload["tasks"]:
        assert item["error"].startswith("no provider completed the task:")
        for name in PROVIDERS:
            assert f"{name}#0:HarnessError" in item["error"]
    failed_calls = stub_log.read_text(encoding="utf-8").split()
    for name in PROVIDERS:
        assert failed_calls.count(name) >= len(goal_lines)

    status = _run(recursion, ["status", *common], _env(stub_dir, stub_log, fail=False))
    assert status.returncode == 0, status.stderr
    listed = _json_stdout(status)
    assert any(item["run_id"] == run_id and item["status"] == "failed" for item in listed["runs"])

    one = _run(recursion, ["status", "--run", run_id, *common], _env(stub_dir, stub_log, fail=False))
    assert one.returncode == 0, one.stderr
    assert _json_stdout(one)["run"]["run_id"] == run_id

    cancelled = _run(recursion, ["cancel", "--run", run_id, *common], _env(stub_dir, stub_log, fail=False))
    assert cancelled.returncode == 0, cancelled.stderr
    assert _json_stdout(cancelled)["status"] == "cancelled"
    assert "SECRET" not in cancelled.stdout

    resumed = _run(
        recursion,
        ["resume", "--run", run_id, "--allow-live", *common],
        _env(stub_dir, stub_log, fail=False),
    )
    assert resumed.returncode == 0, resumed.stderr
    finished = _json_stdout(resumed)
    assert finished["status"] == "completed"
    assert [item["task"] for item in finished["tasks"]] == goal_lines
    assert {item["provider"] for item in finished["tasks"]} == set(PROVIDERS)
    for task in finished["tasks"]:
        assert task["status"] == "completed"
        assert task["execution"]["live"] is True
        assert task["execution"]["text"].startswith("VERDICT approve\n")
        assert f"stub provider={task['provider']}" in task["execution"]["text"]
        assert task["reviews"][0]["verdict"] == "approve"
        assert task["usage"]["input_tokens"] is not None
    report = finished["report"]
    json_report = Path(report["json"])
    markdown_report = Path(report["markdown"])
    assert json_report.is_file()
    assert markdown_report.is_file()
    assert json_report.parent == state_dir
    body = json.loads(json_report.read_text(encoding="utf-8"))
    assert body["status"] == "completed"
    assert body["run_id"] == run_id
    markdown = markdown_report.read_text(encoding="utf-8")
    for line in goal_lines:
        assert line in markdown
    assert "SECRET" not in markdown
    assert "SECRET" not in json_report.read_text(encoding="utf-8")
    assert _head() == head

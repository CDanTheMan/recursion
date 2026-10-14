"""Schema checks, secret redaction, and the logs command."""

from __future__ import annotations

import json
import subprocess
from io import StringIO
from pathlib import Path

import pytest

from scripts.v3.harness.cli import main
from scripts.v3.harness.config import load_config
from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.log import JsonLog, read_events
from scripts.v3.harness.redact import redact, redact_text
from scripts.v3.harness.report import write_reports
from scripts.v3.harness.state import RunStore

ROOT = Path(__file__).resolve().parents[1]
SECRET = "sk-" + ("a" * 24)
RUN_ID = "RUN-" + ("ab" * 8)


def _shipped() -> dict:
    return json.loads((ROOT / "config" / "harness.json").read_text(encoding="utf-8"))


def test_schema_names_the_failing_field(tmp_path: Path) -> None:
    raw = _shipped()
    raw["routing"]["retries"] = -1
    path = tmp_path / "harness.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(HarnessError) as caught:
        load_config(path)
    message = str(caught.value)
    assert "routing.retries" in message
    assert "minimum of 0" in message


def test_schema_rejects_a_non_integer(tmp_path: Path) -> None:
    raw = _shipped()
    raw["providers"][0]["timeout_seconds"] = "soon"
    path = tmp_path / "harness.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(HarnessError) as caught:
        load_config(path)
    assert "providers[0].timeout_seconds" in str(caught.value)
    assert "integer" in str(caught.value)


def test_validate_command_accepts_the_sample_config(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["config", "validate", "--config", str(ROOT / "examples" / "harness.json")])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["version"] == 1


def test_validate_command_reports_a_schema_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    raw = _shipped()
    raw["orchestration"]["concurrency"] = 0
    path = tmp_path / "harness.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    code = main(["config", "validate", "--config", str(path)])
    assert code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "orchestration.concurrency" in captured.err
    assert "minimum of 1" in captured.err


def test_redact_hides_tokens_and_leaves_ordinary_text() -> None:
    assert redact_text("Summarize the repository layout") == "Summarize the repository layout"
    assert SECRET not in redact_text(f"note {SECRET} end")
    assert redact_text("token=super-secret-value") == "token=[REDACTED]"
    assert "Bearer" not in redact_text("Authorization: Bearer abcdefghijklmnop")
    assert "ghp_" not in redact_text("ghp_" + ("b" * 36))
    cleaned = redact({"api_key": SECRET, "goal": "plain", "nested": {"token": "xyz"}})
    assert cleaned["api_key"] == "[REDACTED]"
    assert cleaned["nested"]["token"] == "[REDACTED]"
    assert cleaned["goal"] == "plain"


def test_logs_reports_and_run_state_store_redacted_text(tmp_path: Path) -> None:
    state = tmp_path / "state"
    sink = StringIO()
    log = JsonLog([sink], state_dir=state)
    log.event("plan.admitted", goal=f"token={SECRET}")
    log.bind(run_id=RUN_ID)
    log.event("provider.failed", provider="claude", error="HarnessError", index=0)
    log.close()
    stored_log = (state / f"{RUN_ID}.jsonl").read_text(encoding="utf-8")
    assert SECRET not in stored_log
    assert SECRET not in sink.getvalue()
    assert "plan.admitted" in stored_log
    events = read_events(state / f"{RUN_ID}.jsonl")
    assert events[0]["run_id"] == RUN_ID
    assert events[0]["level"] == "info"
    assert events[1]["level"] == "error"

    store = RunStore(state)

    def put(record: dict) -> None:
        record["goal"] = f"keep {SECRET} out"
        record["run_id"] = RUN_ID
        record["status"] = "failed"
        record["tasks"] = [
            {
                "attempts": [],
                "diff": SECRET,
                "index": 0,
                "provider": "claude",
                "reviews": [{"notes": SECRET, "reviewer": "codex", "round": 1, "verdict": "approve"}],
                "status": "failed",
                "task": f"api_key={SECRET}",
                "usage": {"cost": None, "input_tokens": 1, "output_tokens": 1},
            }
        ]

    store.update(RUN_ID, put)
    assert SECRET not in (state / f"{RUN_ID}.json").read_text(encoding="utf-8")
    paths = write_reports(state, store.load(RUN_ID))
    assert SECRET not in Path(paths["json"]).read_text(encoding="utf-8")
    assert SECRET not in Path(paths["markdown"]).read_text(encoding="utf-8")
    assert "[REDACTED]" in Path(paths["markdown"]).read_text(encoding="utf-8")


def test_logs_command_filters_by_task_provider_and_level(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    state = tmp_path / "state"
    log = JsonLog([StringIO()], state_dir=state)
    log.bind(run_id=RUN_ID)
    log.event("task.started", index=0, provider="fixture", run_id=RUN_ID)
    log.event("provider.failed", index=0, provider="claude", error="HarnessError", run_id=RUN_ID)
    log.event("task.completed", index=1, provider="codex", run_id=RUN_ID)
    log.close()
    store = RunStore(state)

    def put(record: dict) -> None:
        record["run_id"] = RUN_ID
        record["status"] = "failed"
        record["tasks"] = [
            {"id": "task-1", "index": 0, "status": "failed"},
            {"id": "task-2", "index": 1, "status": "completed"},
        ]

    store.update(RUN_ID, put)
    code = main(
        [
            "logs",
            RUN_ID,
            "--state-dir",
            str(state),
            "--task",
            "task-1",
            "--provider",
            "claude",
            "--level",
            "error",
            "--tail",
            "5",
        ]
    )
    assert code == 0
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert len(lines) == 1
    assert lines[0]["event"] == "provider.failed"
    assert lines[0]["provider"] == "claude"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _branches() -> set[str]:
    completed = _git("for-each-ref", "--format=%(refname:short)", "refs/heads/recursion")
    return {line.strip() for line in completed.stdout.splitlines() if line.strip()}


def _cleanup(before: set[str]) -> None:
    extra = _branches() - before
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


def test_run_stores_a_log_without_the_token(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    state = tmp_path / "state"
    before = _branches()
    head = _git("rev-parse", "HEAD").stdout.strip()
    try:
        code = main(
            [
                "run",
                "--task",
                f"note token={SECRET}",
                "--provider",
                "fixture",
                "--state-dir",
                str(state),
            ]
        )
        captured = capsys.readouterr()
        assert SECRET not in captured.out
        assert SECRET not in captured.err
        assert code == 2
        payload = json.loads(captured.out)
        run_id = payload["run_id"]
        log_path = state / f"{run_id}.jsonl"
        assert log_path.is_file()
        assert SECRET not in log_path.read_text(encoding="utf-8")
        assert SECRET not in (state / f"{run_id}.json").read_text(encoding="utf-8")
        report = payload["report"]
        assert SECRET not in Path(report["json"]).read_text(encoding="utf-8")
        assert SECRET not in Path(report["markdown"]).read_text(encoding="utf-8")
        listed = main(["logs", run_id, "--state-dir", str(state), "--provider", "fixture"])
        assert listed == 0
        events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
        assert events
        assert all(item["provider"] == "fixture" for item in events)
    finally:
        _cleanup(before)
        assert _git("rev-parse", "HEAD").stdout.strip() == head
        assert _branches() == before

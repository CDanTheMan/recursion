"""Stream contracts for the claude, codex, and grok adapters.

The supervisor is replaced. These tests never start the real CLIs.
``allow_live=True`` only reaches that supervisor. Without it, the adapter
refuses before PATH is consulted. Captured text is the supervisor's UTF-8
stdout, including the task passed on stdin for claude.
"""

from __future__ import annotations

import json
import subprocess
from unittest.mock import patch

import pytest

from scripts.v3.harness.cooldowns import CooldownStore
from scripts.v3.harness.dispatch import execute_with_policy
from scripts.v3.harness.errors import (
    HarnessError,
    LiveProviderDisabled,
    ProviderCLIMissing,
    ProviderRateLimited,
)
from scripts.v3.harness.providers import (
    ClaudeHeadlessProvider,
    CodexExecProvider,
    GrokHeadlessProvider,
    ProviderRequest,
)
from scripts.v3.harness.usage import empty_usage, parse_usage


TASK = "Say café"
REQUEST = ProviderRequest(task=TASK, packet_id="PACKET-STREAM", route_id="route-a")

CLAUDE_SUCCESS = "\n".join(
    (
        '{"type":"system","subtype":"init"}',
        "not-json preamble",
        '{"type":"assistant","message":{"content":[{"type":"text","text":"café done"}]}}',
        '{"type":"result","usage":{"input_tokens":12,"output_tokens":3},"total_cost_usd":0.01}',
    )
)
CODEX_SUCCESS = "\n".join(
    (
        '{"type":"thread.started","thread_id":"t1"}',
        '{"type":"item.completed","item":{"type":"agent_message","text":"café done"}}',
        '{"type":"turn.completed","usage":{"input_tokens":4,"output_tokens":2}}',
    )
)
GROK_SUCCESS = "\n".join(
    (
        '{"type":"content","content":"café done"}',
        '{"usage":{"prompt_tokens":8,"completion_tokens":5,"cost":0.02}}',
    )
)

STREAMS = (
    pytest.param(
        ClaudeHeadlessProvider,
        CLAUDE_SUCCESS,
        {"cost": 0.01, "input_tokens": 12, "output_tokens": 3},
        id="claude",
    ),
    pytest.param(
        CodexExecProvider,
        CODEX_SUCCESS,
        {"cost": None, "input_tokens": 4, "output_tokens": 2},
        id="codex",
    ),
    pytest.param(
        GrokHeadlessProvider,
        GROK_SUCCESS,
        {"cost": 0.02, "input_tokens": 8, "output_tokens": 5},
        id="grok",
    ),
)


def _completed(argv: list[str], *, stdout: str, stderr: str = "", returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=argv, returncode=returncode, stdout=stdout, stderr=stderr)


def _execute(adapter, completed: subprocess.CompletedProcess[str]):
    result = None
    spawned = None
    with patch("scripts.v3.harness.providers.run_command", return_value=completed) as spawned:
        result = adapter.execute(REQUEST, allow_live=True, timeout_seconds=15)
    return result, spawned


def _assert_runner_contract(adapter, spawned) -> None:
    argv = list(adapter.argv(REQUEST))
    assert spawned.call_args.args[0] == argv
    kwargs = spawned.call_args.kwargs
    assert kwargs["timeout_seconds"] == 15
    assert kwargs["cwd"] is None
    if adapter.name == "claude":
        assert kwargs["stdin_text"] == TASK
    else:
        assert kwargs["stdin_text"] is None


@pytest.mark.parametrize("adapter_cls,stdout,usage", STREAMS)
def test_success_stream_keeps_text_and_usage(adapter_cls, stdout: str, usage: dict) -> None:
    adapter = adapter_cls()
    result, spawned = _execute(adapter, _completed(list(adapter.argv(REQUEST)), stdout=stdout))
    _assert_runner_contract(adapter, spawned)
    assert result.live is True
    assert result.provider == adapter.name
    assert result.text == stdout
    assert "café done" in result.text
    assert parse_usage(result.text) == usage


@pytest.mark.parametrize("adapter_cls,stdout,usage", STREAMS)
def test_malformed_lines_leave_the_last_real_usage(adapter_cls, stdout: str, usage: dict) -> None:
    adapter = adapter_cls()
    broken = stdout + "\n{not-json SECRET\n" + '{"usage":{"input_tokens":999,"output_tokens":'
    result, _spawned = _execute(adapter, _completed(list(adapter.argv(REQUEST)), stdout=broken))
    assert result.text == broken
    parsed = parse_usage(result.text)
    assert parsed == usage
    assert "SECRET" not in json.dumps(parsed)


@pytest.mark.parametrize("adapter_cls", (ClaudeHeadlessProvider, CodexExecProvider, GrokHeadlessProvider))
def test_only_malformed_stdout_does_not_invent_usage(adapter_cls) -> None:
    adapter = adapter_cls()
    stdout = "not json\n{truncated SECRET\n"
    result, _spawned = _execute(adapter, _completed([], stdout=stdout))
    assert result.text == stdout
    assert parse_usage(result.text) == empty_usage()


@pytest.mark.parametrize("adapter_cls", (ClaudeHeadlessProvider, CodexExecProvider, GrokHeadlessProvider))
@pytest.mark.parametrize(
    ("returncode", "stderr"),
    (
        (429, "SECRET body"),
        (1, "Too Many Requests SECRET"),
    ),
)
def test_rate_limit_failure_omits_stderr(adapter_cls, returncode: int, stderr: str) -> None:
    adapter = adapter_cls()
    completed = _completed([], stdout="partial", stderr=stderr, returncode=returncode)
    with patch("scripts.v3.harness.providers.run_command", return_value=completed):
        with pytest.raises(ProviderRateLimited) as caught:
            adapter.execute(REQUEST, allow_live=True)
    message = str(caught.value)
    assert message == f"{adapter.name} was rate-limited"
    assert "SECRET" not in message
    assert "partial" not in message


@pytest.mark.parametrize("adapter_cls", (ClaudeHeadlessProvider, CodexExecProvider, GrokHeadlessProvider))
def test_missing_executable_fails_cleanly(adapter_cls) -> None:
    adapter = adapter_cls()
    binary = adapter.argv(REQUEST)[0]

    with patch("scripts.v3.harness.providers.run_command") as spawned:
        with pytest.raises(LiveProviderDisabled) as refused:
            adapter.execute(REQUEST, allow_live=False)
    spawned.assert_not_called()
    assert binary in str(refused.value)
    assert "SECRET" not in str(refused.value)

    def missing(*_args, **_kwargs):
        raise FileNotFoundError(2, "No such file or directory", binary)

    with patch("scripts.v3.harness.providers.run_command", side_effect=missing):
        with pytest.raises(ProviderCLIMissing) as caught:
            adapter.execute(REQUEST, allow_live=True)
    message = str(caught.value)
    assert message == (
        f"{adapter.name} CLI was not found on PATH ({binary}). "
        "Install it, or choose another provider."
    )
    assert "SECRET" not in message


def test_rate_limit_falls_back_without_retrying(tmp_path) -> None:
    claude = ClaudeHeadlessProvider()
    codex = CodexExecProvider()
    limited = _completed([], stdout="", stderr="SECRET rate limit", returncode=429)
    ok = _completed(list(codex.argv(REQUEST)), stdout=CODEX_SUCCESS)
    pauses: list[float] = []
    store = CooldownStore(tmp_path / "cooldowns.json")
    with patch("scripts.v3.harness.providers.run_command", side_effect=[limited, ok]):
        result, attempts = execute_with_policy(
            REQUEST,
            ["claude", "codex"],
            allow_live=True,
            retries=1,
            backoff_seconds=1,
            sleep=pauses.append,
            timeout_seconds={"claude": 15, "codex": 15},
            open_adapter={"claude": claude, "codex": codex}.get,
            cooldowns=store,
            cooldown_seconds=60,
            now=lambda: 1_000_000,
        )
    assert pauses == []
    assert [item["error"] if not item["ok"] else None for item in attempts] == ["ProviderRateLimited", None]
    assert result.text == CODEX_SUCCESS
    assert parse_usage(result.text)["input_tokens"] == 4
    body = (tmp_path / "cooldowns.json").read_text(encoding="utf-8")
    assert "SECRET" not in body
    assert "rate-limited" in body
    with pytest.raises(HarnessError):
        execute_with_policy(
            REQUEST,
            ["claude"],
            allow_live=True,
            retries=1,
            backoff_seconds=1,
            sleep=pauses.append,
            open_adapter=lambda _name: claude,
            cooldowns=store,
            now=lambda: 1_000_000,
        )
    assert pauses == []

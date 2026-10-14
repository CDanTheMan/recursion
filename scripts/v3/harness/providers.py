"""Provider adapters. Headless CLIs, plus a fixture that never starts a process.

Each adapter builds argv and starts a process only when ``allow_live`` is set.
The harness does not read credentials. Retries and fallback live in
``dispatch.py``, not inside an adapter.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from scripts.v3.harness.availability import classify_failure
from scripts.v3.harness.errors import (
    HarnessError,
    LiveProviderDisabled,
    ProviderCLIMissing,
    ProviderTimeout,
)


_GRAPH_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
_GRAPH_CAPABILITY = re.compile(r"^[a-z0-9][a-z0-9+-]{0,63}$")


@dataclass(frozen=True)
class ProviderRequest:
    """Work handed to a provider after M1B has selected a route.

    ``kind`` is ``execute`` for the task, ``review`` for a diff review, and ``plan`` for a task graph.
    ``cwd`` is the task worktree when isolation is on.
    """

    task: str
    packet_id: str
    route_id: str
    kind: str = "execute"
    cwd: str | None = None


@dataclass(frozen=True)
class ProviderResult:
    """Adapter output. ``live`` is false when no provider process was started."""

    provider: str
    argv: tuple[str, ...]
    text: str
    live: bool

    def to_dict(self) -> dict:
        return {
            "argv": list(self.argv),
            "live": self.live,
            "provider": self.provider,
            "text": self.text,
        }


class ProviderAdapter:
    """Headless execution behind one interface."""

    name = ""
    STATIC_ARGV: tuple[str, ...] = ()
    CAPABILITIES: tuple[str, ...] = ()

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        raise NotImplementedError

    def execute(self, request: ProviderRequest, *, allow_live: bool = False) -> ProviderResult:
        raise NotImplementedError


class FixtureProvider(ProviderAdapter):
    """Deterministic stand-in used by local runs and the contracts gate."""

    name = "fixture"
    STATIC_ARGV = ("fixture-provider", "--output-format", "json")
    CAPABILITIES = ("execute", "deterministic")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        del request
        return self.STATIC_ARGV

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
    ) -> ProviderResult:
        del allow_live, timeout_seconds
        if request.kind == "review":
            text = "VERDICT approve\nfixture review"
        elif request.kind == "plan":
            text = _fixture_plan(request.task)
        else:
            text = "\n".join(
                (
                    "provider=fixture",
                    f"route={request.route_id}",
                    f"packet={request.packet_id}",
                    request.task,
                )
            )
        return ProviderResult(provider=self.name, argv=self.argv(request), text=text, live=False)


def _fixture_plan(task: str) -> str:
    """Turn the goal section of a plan prompt into tasks.

    A goal whose first line is ``graph`` is a dependency list. Any other goal
    stays one independent task per line.
    """

    marker = "Goal:\n"
    goal = task.split(marker, 1)[1] if marker in task else ""
    lines = [line.strip() for line in goal.splitlines() if line.strip()]
    if lines and lines[0] == "graph":
        return json.dumps({"tasks": _fixture_graph(lines[1:])})
    tasks = [
        {
            "depends_on": [],
            "description": line,
            "id": f"task-{index}",
            "required_capabilities": [],
        }
        for index, line in enumerate(lines, start=1)
    ]
    return json.dumps({"tasks": tasks})


def _fixture_graph(lines: list[str]) -> list[dict]:
    tasks = []
    for line in lines:
        parsed = _graph_line(line)
        if parsed is None:
            return []
        tasks.append(parsed)
    return tasks


def _graph_line(line: str) -> dict | None:
    """Parse ``id: description``, then optional ``requires`` and ``depends``."""

    body = line
    depends: list[str] = []
    requires: list[str] = []
    if " depends " in body:
        body, raw = body.rsplit(" depends ", 1)
        depends = [part.strip() for part in raw.split(",") if part.strip()]
        if not depends or any(_GRAPH_ID.fullmatch(item) is None for item in depends):
            return None
    if " requires " in body:
        body, raw = body.rsplit(" requires ", 1)
        requires = [part.strip() for part in raw.split(",") if part.strip()]
        if not requires or any(_GRAPH_CAPABILITY.fullmatch(item) is None for item in requires):
            return None
    if ":" not in body:
        return None
    task_id, description = body.split(":", 1)
    task_id = task_id.strip()
    description = description.strip()
    if _GRAPH_ID.fullmatch(task_id) is None or description == "":
        return None
    return {
        "depends_on": depends,
        "description": description,
        "id": task_id,
        "required_capabilities": requires,
    }


def _refuse_unless_live(adapter: ProviderAdapter, allow_live: bool) -> None:
    if not allow_live:
        raise LiveProviderDisabled(
            f"{adapter.name} headless CLI is not started unless --allow-live is set"
        )


_STUB_PROVIDER = re.compile(r"(?im)^set\s+RECURSION_STUB_PROVIDER=([A-Za-z0-9_-]+)\s*$")
_STUB_LAUNCH = re.compile(r'(?im)^"([^"]+)"\s+-X\s+utf8\s+"([^"]+)"\s+%\*\s*$')


def _spawn_plan(argv: tuple[str, ...]) -> tuple[list[str], dict[str, str] | None]:
    """Return the process argv and an optional environment overlay.

    ``CreateProcess`` does not execute a ``.cmd`` or ``.bat`` named without an
    extension. A generated provider stub is started with Python directly so a
    multiline prompt is not parsed again by ``cmd.exe``. Any other batch shim
    goes through ``cmd.exe``. Real ``.exe`` commands stay unchanged.
    """

    if os.name != "nt":
        return list(argv), None
    found = shutil.which(argv[0])
    if not found or not found.lower().endswith((".cmd", ".bat")):
        return list(argv), None
    direct = _stub_launch(found)
    if direct is not None:
        return direct
    comspec = os.environ.get("ComSpec") or "cmd.exe"
    return [comspec, "/d", "/c", found, *argv[1:]], None


def _stub_launch(launcher: str) -> tuple[list[str], dict[str, str]] | None:
    try:
        text = Path(launcher).read_text(encoding="utf-8")
    except OSError:
        return None
    provider = _STUB_PROVIDER.search(text)
    launch = _STUB_LAUNCH.search(text)
    if provider is None or launch is None:
        return None
    executable, stub = launch.groups()
    return [executable, "-X", "utf8", stub], {"RECURSION_STUB_PROVIDER": provider.group(1)}


def _run_cli(
    adapter: ProviderAdapter,
    request: ProviderRequest,
    *,
    stdin_text: str | None,
    timeout_seconds: int | None,
) -> ProviderResult:
    argv = adapter.argv(request)
    command, overlay = _spawn_plan(argv)
    kwargs: dict = {
        "text": True,
        "encoding": "utf-8",
        "capture_output": True,
        "check": False,
    }
    if timeout_seconds is not None:
        kwargs["timeout"] = timeout_seconds
    if request.cwd:
        kwargs["cwd"] = request.cwd
    if overlay:
        kwargs["env"] = {**os.environ, **overlay}
    if stdin_text is None:
        kwargs["stdin"] = subprocess.DEVNULL
    else:
        kwargs["input"] = stdin_text
    try:
        completed = subprocess.run(command, **kwargs)
    except FileNotFoundError as exc:
        raise ProviderCLIMissing(
            f"{adapter.name} CLI was not found on PATH ({argv[0]}). "
            "Install it, or choose another provider."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ProviderTimeout(f"{adapter.name} timed out after {timeout_seconds} seconds") from exc
    failure = classify_failure(adapter.name, completed.returncode, completed.stderr or "")
    if failure is not None:
        raise failure
    return ProviderResult(provider=adapter.name, argv=argv, text=completed.stdout, live=True)


class ClaudeHeadlessProvider(ProviderAdapter):
    """Claude Code print mode: ``claude -p --output-format stream-json``.

    The prompt is written to the process stdin. This adapter does not start
    ``claude`` unless ``allow_live`` is true.
    """

    name = "claude"
    STATIC_ARGV = ("claude", "-p", "--output-format", "stream-json")
    CAPABILITIES = ("execute", "stream-json", "subscription")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        del request
        return self.STATIC_ARGV

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(self, request, stdin_text=request.task, timeout_seconds=timeout_seconds)


class CodexExecProvider(ProviderAdapter):
    """Codex noninteractive mode: ``codex exec --json <prompt>``.

    The task is the prompt argument. Stdin is not attached. The process starts
    only when ``allow_live`` is true.
    """

    name = "codex"
    STATIC_ARGV = ("codex", "exec", "--json")
    CAPABILITIES = ("execute", "jsonl", "subscription")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        return self.STATIC_ARGV + (request.task,)

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(self, request, stdin_text=None, timeout_seconds=timeout_seconds)


class GrokHeadlessProvider(ProviderAdapter):
    """Grok Build headless mode: ``grok -p <prompt> --output-format streaming-json``.

    The task is the ``-p`` prompt argument. The process starts only when
    ``allow_live`` is true.
    """

    name = "grok"
    STATIC_ARGV = ("grok", "-p", "--output-format", "streaming-json")
    CAPABILITIES = ("execute", "streaming-json", "subscription")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        return ("grok", "-p", request.task, "--output-format", "streaming-json")

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(self, request, stdin_text=None, timeout_seconds=timeout_seconds)


class GeminiHeadlessProvider(ProviderAdapter):
    """Gemini CLI headless mode: ``gemini -p <prompt> --output-format stream-json``.

    ``-p`` forces non-interactive execution. The task is that prompt argument.
    Stdin is not attached. The process starts only when ``allow_live`` is true.
    """

    name = "gemini"
    STATIC_ARGV = ("gemini", "-p", "--output-format", "stream-json")
    CAPABILITIES = ("execute", "stream-json", "subscription")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        return ("gemini", "-p", request.task, "--output-format", "stream-json")

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(self, request, stdin_text=None, timeout_seconds=timeout_seconds)


class CursorHeadlessProvider(ProviderAdapter):
    """Cursor Agent print mode: ``cursor-agent -p --output-format stream-json <prompt>``.

    ``cursor-agent`` is the installed binary (``agent`` is the same program).
    ``-p`` is print mode. The task is the positional prompt. Stdin is not
    attached. The process starts only when ``allow_live`` is true.
    """

    name = "cursor"
    STATIC_ARGV = ("cursor-agent", "-p", "--output-format", "stream-json")
    CAPABILITIES = ("execute", "stream-json", "subscription")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        return ("cursor-agent", "-p", "--output-format", "stream-json", request.task)

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(self, request, stdin_text=None, timeout_seconds=timeout_seconds)


class OpenCodeHeadlessProvider(ProviderAdapter):
    """OpenCode non-interactive mode: ``opencode run --format json <prompt>``.

    ``--format json`` writes one JSON event per line. The task is the positional
    message. Stdin is not attached. The process starts only when ``allow_live``
    is true.
    """

    name = "opencode"
    STATIC_ARGV = ("opencode", "run", "--format", "json")
    CAPABILITIES = ("execute", "json")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        return ("opencode", "run", "--format", "json", request.task)

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(self, request, stdin_text=None, timeout_seconds=timeout_seconds)


def adapters() -> dict[str, type[ProviderAdapter]]:
    """Registered adapter classes, keyed by provider name."""

    classes = (
        FixtureProvider,
        ClaudeHeadlessProvider,
        CodexExecProvider,
        GrokHeadlessProvider,
        GeminiHeadlessProvider,
        CursorHeadlessProvider,
        OpenCodeHeadlessProvider,
    )
    return {cls.name: cls for cls in classes}


def open_provider(name: str) -> ProviderAdapter:
    """Return the one adapter registered under ``name``."""

    known = adapters()
    try:
        return known[name]()
    except KeyError as exc:
        names = ", ".join(sorted(known))
        raise HarnessError(f"unknown provider {name!r}; known providers: {names}") from exc

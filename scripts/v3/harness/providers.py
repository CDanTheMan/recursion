"""Provider adapters. Headless CLIs, plus a fixture that never starts a process.

Each adapter builds argv and starts a process only when ``allow_live`` is set.
The harness does not read credentials. Retries and fallback live in
``dispatch.py``, not inside an adapter. Cancel and timeout stop the process
and the children it started.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from scripts.v3.harness.availability import classify_failure
from scripts.v3.harness.errors import (
    HarnessError,
    LiveProviderDisabled,
    ProviderCLIMissing,
    ProviderTimeout,
    RunCancelled,
)
from scripts.v3.proc.lifecycle import ProcessCancelled, run_command


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
        should_stop=None,
    ) -> ProviderResult:
        del allow_live, timeout_seconds, should_stop
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

    On Windows, ``CreateProcess`` does not run a ``.cmd``, ``.bat``, or
    ``.ps1`` that is named without going through a shell. A generated provider
    stub is started with Python directly so a multiline prompt is not parsed
    again by ``cmd.exe``. Any other batch shim goes through ``cmd.exe``. A
    PowerShell shim goes through ``-File``. A ``.exe`` stays a direct argv.
    """

    if os.name != "nt":
        return list(argv), None
    from scripts.v3.harness.doctor import resolve_executable

    found = resolve_executable(argv[0])
    if found is None:
        return list(argv), None
    if found.suffix.lower() in {".cmd", ".bat"}:
        direct = _stub_launch(str(found))
        if direct is not None:
            return direct
    return windows_command(argv, found), None


def windows_command(
    argv: tuple[str, ...] | list[str],
    resolved: str | Path,
    *,
    powershell: str | None = None,
    comspec: str | None = None,
) -> list[str]:
    """Build a Windows spawn argv for an ``.exe``, ``.cmd``, ``.bat``, or ``.ps1``."""

    path = Path(resolved)
    rest = list(argv[1:])
    suffix = path.suffix.lower()
    found = str(path)
    if suffix in {".cmd", ".bat"}:
        shell = comspec or os.environ.get("ComSpec") or "cmd.exe"
        return [shell, "/d", "/c", found, *rest]
    if suffix == ".ps1":
        shell = powershell or _powershell_executable()
        return [shell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", found, *rest]
    return [found, *rest]


def _powershell_executable() -> str:
    for name in ("pwsh", "powershell"):
        found = shutil.which(name)
        if found:
            return found
    return "powershell.exe"


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
    should_stop=None,
) -> ProviderResult:
    argv = adapter.argv(request)
    command, overlay = _spawn_plan(argv)
    env = None if not overlay else {**os.environ, **overlay}
    try:
        completed = run_command(
            command,
            cwd=request.cwd,
            stdin_text=stdin_text,
            timeout_seconds=timeout_seconds,
            should_stop=should_stop,
            env=env,
        )
    except FileNotFoundError as exc:
        raise ProviderCLIMissing(
            f"{adapter.name} CLI was not found on PATH ({argv[0]}). "
            "Install it, or choose another provider."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ProviderTimeout(f"{adapter.name} timed out after {timeout_seconds} seconds") from exc
    except ProcessCancelled as exc:
        raise RunCancelled("run cancelled") from exc
    failure = classify_failure(
        adapter.name,
        completed.returncode,
        completed.stderr or "",
        stdout=completed.stdout or "",
    )
    if failure is not None:
        raise failure
    return ProviderResult(provider=adapter.name, argv=argv, text=completed.stdout, live=True)


# cmd.exe's command-line limit is about 8191 characters. Prompts longer than
# this budget go through stdin or a file when that CLI accepts it.
PROMPT_ARGV_LIMIT = 7000
GEMINI_LONG_PROMPT = " "
OPENCODE_LONG_PROMPT = "Carry out the task in the attached file."


def prompt_fits(task: str) -> bool:
    """True when ``task`` can sit in argv without nearing the Windows limit."""

    return len(task) <= PROMPT_ARGV_LIMIT


def grok_prompt_path(packet_id: str) -> Path:
    """Temp file for one Grok prompt. The name comes from the packet id."""

    return Path(tempfile.gettempdir()) / f"recursion-grok-{_packet_token(packet_id)}.txt"


def opencode_prompt_path(request: ProviderRequest) -> Path:
    """Prompt file inside the task directory. OpenCode reads ``--file`` from there."""

    root = Path(request.cwd) if request.cwd else Path.cwd()
    return root / f".recursion-prompt-{_packet_token(request.packet_id)}.txt"


def _packet_token(packet_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", packet_id).strip("-")[:80]
    return safe or "prompt"


def _insert_after(argv: tuple[str, ...], flag: str, value: str) -> tuple[str, ...]:
    items = list(argv)
    items.insert(items.index(flag) + 1, value)
    return tuple(items)


def _with_flag(argv: tuple[str, ...], flag: str, value: str | None) -> tuple[str, ...]:
    if not value:
        return argv
    return argv + (flag, value)


def _write_prompt(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _remove_prompt(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        return


class ClaudeHeadlessProvider(ProviderAdapter):
    """Claude Code print mode.

    ``claude -p --output-format stream-json`` exits unless ``--verbose`` is
    also set. ``--dangerously-skip-permissions`` lets a headless tool call
    proceed. The prompt is the process stdin. There is no working-directory
    flag; the process cwd is the task directory. The model flag is left unset
    so the signed-in CLI default is used. This adapter does not start
    ``claude`` unless ``allow_live`` is true.
    """

    name = "claude"
    STATIC_ARGV = (
        "claude",
        "-p",
        "--output-format",
        "stream-json",
        "--verbose",
        "--dangerously-skip-permissions",
    )
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
        should_stop=None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(
            self,
            request,
            stdin_text=request.task,
            timeout_seconds=timeout_seconds,
            should_stop=should_stop,
        )


class CodexExecProvider(ProviderAdapter):
    """Codex noninteractive mode: ``codex exec --json --approve-for-me``.

    ``exec`` does not accept ``--ask-for-approval``. ``--approve-for-me`` is
    the unattended workspace-write path, and it cannot be combined with
    ``--sandbox``. The prompt is stdin, passed as ``-``, so a long task stays
    off argv. ``--cd`` is the workspace root when the task has one. The model
    flag is left unset. The process starts only when ``allow_live`` is true.
    """

    name = "codex"
    STATIC_ARGV = ("codex", "exec", "--json", "--approve-for-me")
    CAPABILITIES = ("execute", "jsonl", "subscription")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        return _with_flag(self.STATIC_ARGV, "--cd", request.cwd) + ("-",)

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
        should_stop=None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(
            self,
            request,
            stdin_text=request.task,
            timeout_seconds=timeout_seconds,
            should_stop=should_stop,
        )


class GrokHeadlessProvider(ProviderAdapter):
    """Grok Build headless mode.

    Headless Grok does not read the prompt from stdin. The task is written to
    a temp file and passed with ``--prompt-file``. ``--always-approve`` lets
    tool calls proceed, and ``--no-auto-update`` keeps the CLI from updating
    mid-run. ``--cwd`` is the task directory when one is set. The model flag
    is left unset. The process starts only when ``allow_live`` is true.
    """

    name = "grok"
    STATIC_ARGV = (
        "grok",
        "--output-format",
        "streaming-json",
        "--always-approve",
        "--no-auto-update",
    )
    CAPABILITIES = ("execute", "streaming-json", "subscription")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        argv = self.STATIC_ARGV + ("--prompt-file", str(grok_prompt_path(request.packet_id)))
        return _with_flag(argv, "--cwd", request.cwd)

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
        should_stop=None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        path = grok_prompt_path(request.packet_id)
        _write_prompt(path, request.task)
        try:
            return _run_cli(
                self,
                request,
                stdin_text=None,
                timeout_seconds=timeout_seconds,
                should_stop=should_stop,
            )
        finally:
            _remove_prompt(path)


class GeminiHeadlessProvider(ProviderAdapter):
    """Gemini CLI headless mode.

    ``-p`` is non-interactive. ``--approval-mode yolo`` approves tool calls,
    and ``--skip-trust`` accepts the workspace. A prompt that fits in argv is
    the ``-p`` value. A longer prompt is stdin, and ``-p`` is a single space
    so the flag still has a value. There is no working-directory flag; the
    process cwd is the task directory. The model flag is left unset. The
    process starts only when ``allow_live`` is true.
    """

    name = "gemini"
    STATIC_ARGV = (
        "gemini",
        "-p",
        "--output-format",
        "stream-json",
        "--approval-mode",
        "yolo",
        "--skip-trust",
    )
    CAPABILITIES = ("execute", "stream-json", "subscription")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        prompt = request.task if prompt_fits(request.task) else GEMINI_LONG_PROMPT
        return _insert_after(self.STATIC_ARGV, "-p", prompt)

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
        should_stop=None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        stdin = None if prompt_fits(request.task) else request.task
        return _run_cli(
            self,
            request,
            stdin_text=stdin,
            timeout_seconds=timeout_seconds,
            should_stop=should_stop,
        )


class CursorHeadlessProvider(ProviderAdapter):
    """Cursor Agent print mode.

    ``cursor-agent`` is the installed binary (``agent`` is the same program).
    ``-p`` is print mode. ``--force`` approves tool calls and ``--trust``
    accepts the workspace. ``--workspace`` is the task directory when one is
    set. A short prompt is the positional argument after ``--``. A longer
    prompt is stdin and the positional is omitted. The model flag is left
    unset. The process starts only when ``allow_live`` is true.
    """

    name = "cursor"
    STATIC_ARGV = ("cursor-agent", "-p", "--output-format", "stream-json", "--force", "--trust")
    CAPABILITIES = ("execute", "stream-json", "subscription")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        argv = _with_flag(self.STATIC_ARGV, "--workspace", request.cwd)
        if prompt_fits(request.task):
            return argv + ("--", request.task)
        return argv

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
        should_stop=None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        stdin = None if prompt_fits(request.task) else request.task
        return _run_cli(
            self,
            request,
            stdin_text=stdin,
            timeout_seconds=timeout_seconds,
            should_stop=should_stop,
        )


class OpenCodeHeadlessProvider(ProviderAdapter):
    """OpenCode non-interactive mode: ``opencode run --format json --auto``.

    ``--format json`` writes one JSON event per line. ``--auto`` approves
    permissions that are not explicitly denied. ``--dir`` is the task
    directory when one is set. ``-p`` on this command is a password flag and
    is not used. A short task is the positional message. A longer task is
    written to a file in that directory and passed with ``--file``, because
    this CLI has no stdin prompt. The model flag is left unset. The process
    starts only when ``allow_live`` is true.
    """

    name = "opencode"
    STATIC_ARGV = ("opencode", "run", "--format", "json", "--auto")
    CAPABILITIES = ("execute", "json")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        argv = _with_flag(self.STATIC_ARGV, "--dir", request.cwd)
        if prompt_fits(request.task):
            return argv + (request.task,)
        return argv + ("--file", str(opencode_prompt_path(request)), OPENCODE_LONG_PROMPT)

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
        should_stop=None,
    ) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        path = None
        if not prompt_fits(request.task):
            path = opencode_prompt_path(request)
            _write_prompt(path, request.task)
        try:
            return _run_cli(
                self,
                request,
                stdin_text=None,
                timeout_seconds=timeout_seconds,
                should_stop=should_stop,
            )
        finally:
            if path is not None:
                _remove_prompt(path)


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

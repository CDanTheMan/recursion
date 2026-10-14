"""Provider adapters. Headless CLIs, plus a fixture that never starts a process.

Each adapter builds argv and starts a process only when ``allow_live`` is set.
The harness does not read credentials. Retries and fallback live in
``dispatch.py``, not inside an adapter.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from scripts.v3.harness.errors import HarnessError, LiveProviderDisabled


@dataclass(frozen=True)
class ProviderRequest:
    """Work handed to a provider after M1B has selected a route."""

    task: str
    packet_id: str
    route_id: str


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

    def execute(self, request: ProviderRequest, *, allow_live: bool = False) -> ProviderResult:
        del allow_live
        text = "\n".join(
            (
                "provider=fixture",
                f"route={request.route_id}",
                f"packet={request.packet_id}",
                request.task,
            )
        )
        return ProviderResult(provider=self.name, argv=self.argv(request), text=text, live=False)


def _refuse_unless_live(adapter: ProviderAdapter, allow_live: bool) -> None:
    if not allow_live:
        raise LiveProviderDisabled(
            f"{adapter.name} headless CLI is not started unless --allow-live is set"
        )


def _run_cli(adapter: ProviderAdapter, request: ProviderRequest, *, stdin_text: str | None) -> ProviderResult:
    argv = adapter.argv(request)
    kwargs: dict = {
        "text": True,
        "encoding": "utf-8",
        "capture_output": True,
        "check": False,
    }
    if stdin_text is None:
        kwargs["stdin"] = subprocess.DEVNULL
    else:
        kwargs["input"] = stdin_text
    completed = subprocess.run(list(argv), **kwargs)
    if completed.returncode != 0:
        raise HarnessError(f"{adapter.name} exited {completed.returncode}")
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

    def execute(self, request: ProviderRequest, *, allow_live: bool = False) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(self, request, stdin_text=request.task)


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

    def execute(self, request: ProviderRequest, *, allow_live: bool = False) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(self, request, stdin_text=None)


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

    def execute(self, request: ProviderRequest, *, allow_live: bool = False) -> ProviderResult:
        _refuse_unless_live(self, allow_live)
        return _run_cli(self, request, stdin_text=None)


def adapters() -> dict[str, type[ProviderAdapter]]:
    """Registered adapter classes, keyed by provider name."""

    classes = (
        FixtureProvider,
        ClaudeHeadlessProvider,
        CodexExecProvider,
        GrokHeadlessProvider,
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

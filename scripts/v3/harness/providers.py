"""Provider adapters. Headless CLIs, plus a fixture that never starts a process.

Each adapter builds argv and starts a process only when ``allow_live`` is set.
The harness does not read credentials. Retries and fallback live in
``dispatch.py``, not inside an adapter.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from scripts.v3.harness.errors import (
    HarnessError,
    LiveProviderDisabled,
    ProviderCLIMissing,
    ProviderRateLimited,
    ProviderTimeout,
)


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

    def execute(
        self,
        request: ProviderRequest,
        *,
        allow_live: bool = False,
        timeout_seconds: int | None = None,
    ) -> ProviderResult:
        del allow_live, timeout_seconds
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


def _rate_limited(completed: subprocess.CompletedProcess[str]) -> bool:
    """Classify a failed process as rate-limited without copying its output."""

    if completed.returncode == 0:
        return False
    if completed.returncode == 429:
        return True
    stderr = (completed.stderr or "").lower()
    return "rate limit" in stderr or "too many requests" in stderr


def _run_cli(
    adapter: ProviderAdapter,
    request: ProviderRequest,
    *,
    stdin_text: str | None,
    timeout_seconds: int | None,
) -> ProviderResult:
    argv = adapter.argv(request)
    kwargs: dict = {
        "text": True,
        "encoding": "utf-8",
        "capture_output": True,
        "check": False,
    }
    if timeout_seconds is not None:
        kwargs["timeout"] = timeout_seconds
    if stdin_text is None:
        kwargs["stdin"] = subprocess.DEVNULL
    else:
        kwargs["input"] = stdin_text
    try:
        completed = subprocess.run(list(argv), **kwargs)
    except FileNotFoundError as exc:
        raise ProviderCLIMissing(
            f"{adapter.name} CLI was not found on PATH ({argv[0]}). "
            "Install it, or choose another provider."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ProviderTimeout(f"{adapter.name} timed out after {timeout_seconds} seconds") from exc
    if _rate_limited(completed):
        raise ProviderRateLimited(f"{adapter.name} was rate-limited")
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

"""Provider adapters. One headless CLI, plus a fixture that never starts a process."""

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
    """Headless execution behind one interface.

    Adapters build an argv and, only when explicitly allowed, start that process.
    The harness does not read credentials and does not invent a fallback provider.
    """

    name = ""

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        raise NotImplementedError

    def execute(self, request: ProviderRequest, *, allow_live: bool = False) -> ProviderResult:
        raise NotImplementedError


class FixtureProvider(ProviderAdapter):
    """Deterministic stand-in used by local runs and the contracts gate."""

    name = "fixture"

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        return ("fixture-provider", "--output-format", "json")

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


class ClaudeHeadlessProvider(ProviderAdapter):
    """Claude Code print mode: ``claude -p --output-format stream-json``.

    The prompt is written to the process stdin. This adapter does not start
    ``claude`` unless ``allow_live`` is true. Tests and the contracts gate leave
    that flag unset.
    """

    name = "claude"
    ARGV = ("claude", "-p", "--output-format", "stream-json")

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        del request
        return self.ARGV

    def execute(self, request: ProviderRequest, *, allow_live: bool = False) -> ProviderResult:
        if not allow_live:
            raise LiveProviderDisabled(
                "claude headless CLI is not started unless --allow-live is set"
            )
        completed = subprocess.run(
            list(self.argv(request)),
            input=request.task,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise HarnessError(f"claude exited {completed.returncode}")
        return ProviderResult(
            provider=self.name,
            argv=self.argv(request),
            text=completed.stdout,
            live=True,
        )


def open_provider(name: str) -> ProviderAdapter:
    """Return the one adapter registered under ``name``."""

    adapters: dict[str, ProviderAdapter] = {
        FixtureProvider.name: FixtureProvider(),
        ClaudeHeadlessProvider.name: ClaudeHeadlessProvider(),
    }
    try:
        return adapters[name]
    except KeyError as exc:
        known = ", ".join(sorted(adapters))
        raise HarnessError(f"unknown provider {name!r}; known providers: {known}") from exc

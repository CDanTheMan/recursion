"""Retry one provider, then fall back to the next capable provider."""

from __future__ import annotations

import time

from scripts.v3.harness.errors import HarnessError, ProviderRateLimited, RunCancelled
from scripts.v3.harness.log import NullLog
from scripts.v3.harness.providers import ProviderRequest, ProviderResult, open_provider


def execute_with_policy(
    request: ProviderRequest,
    candidates: list[str],
    *,
    allow_live: bool,
    retries: int,
    log: object | None = None,
    open_adapter=open_provider,
    backoff_seconds: float = 0,
    sleep=None,
    should_stop=None,
    timeout_seconds: dict[str, int] | None = None,
) -> tuple[ProviderResult, list[dict]]:
    """Try each candidate up to ``retries`` extra times.

    A raised ``HarnessError`` is a failed attempt. Rate limits wait
    ``backoff_seconds * (attempt + 1)`` before the next try of the same
    provider. ``RunCancelled`` stops the policy immediately. Stderr from a
    live process is not recorded.
    """

    if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
        raise HarnessError("retries must be an integer >= 0")
    if isinstance(backoff_seconds, bool) or not isinstance(backoff_seconds, (int, float)) or backoff_seconds < 0:
        raise HarnessError("backoff_seconds must be a number >= 0")
    if not candidates:
        raise HarnessError("no provider candidates")
    sink = log if log is not None else NullLog()
    pause = time.sleep if sleep is None else sleep
    attempts: list[dict] = []
    failures: list[str] = []
    for name in candidates:
        adapter = open_adapter(name)
        for attempt in range(retries + 1):
            if should_stop is not None and should_stop():
                raise RunCancelled("run cancelled")
            sink.event(
                "provider.attempt",
                attempt=attempt,
                packet_id=request.packet_id,
                provider=name,
                route_id=request.route_id,
            )
            try:
                result = _execute(adapter, request, allow_live=allow_live, timeout_seconds=timeout_seconds, name=name)
            except RunCancelled:
                raise
            except HarnessError as exc:
                error = type(exc).__name__
                sink.event("provider.failed", attempt=attempt, error=error, provider=name)
                attempts.append({"attempt": attempt, "error": error, "ok": False, "provider": name})
                failures.append(f"{name}#{attempt}:{error}")
                if isinstance(exc, ProviderRateLimited) and attempt < retries:
                    pause(backoff_seconds * (attempt + 1))
                continue
            sink.event("provider.result", attempt=attempt, live=result.live, provider=name)
            attempts.append(
                {"attempt": attempt, "live": result.live, "ok": True, "provider": name}
            )
            return result, attempts
    raise HarnessError("no provider completed the task: " + ", ".join(failures))


def _execute(adapter, request: ProviderRequest, *, allow_live: bool, timeout_seconds, name: str) -> ProviderResult:
    if timeout_seconds is None:
        return adapter.execute(request, allow_live=allow_live)
    return adapter.execute(
        request,
        allow_live=allow_live,
        timeout_seconds=timeout_seconds.get(name),
    )

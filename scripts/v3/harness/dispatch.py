"""Retry transient failures, then fall back to the next capable provider.

Rate limits, exhausted quotas, and expired auth are recorded as cooldowns
and are not retried. The next eligible provider runs immediately.
"""

from __future__ import annotations

import inspect
import time

from scripts.v3.harness.cooldowns import resolve_until
from scripts.v3.harness.errors import (
    HarnessError,
    ProviderAvailability,
    ProviderTimeout,
    ProviderTransient,
    RunCancelled,
)
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
    cooldowns=None,
    cooldown_seconds: float = 60,
    now=None,
) -> tuple[ProviderResult, list[dict]]:
    """Try each candidate that is not cooling down.

    ``ProviderTransient`` and ``ProviderTimeout`` wait
    ``backoff_seconds * (attempt + 1)`` before another try of the same
    provider. Availability failures record a cooldown and move on. Other
    ``HarnessError`` values are retried without waiting, then the next
    candidate runs. ``RunCancelled`` stops the policy immediately. Stderr
    from a live process is not recorded.
    """

    if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
        raise HarnessError("retries must be an integer >= 0")
    if isinstance(backoff_seconds, bool) or not isinstance(backoff_seconds, (int, float)) or backoff_seconds < 0:
        raise HarnessError("backoff_seconds must be a number >= 0")
    if (
        isinstance(cooldown_seconds, bool)
        or not isinstance(cooldown_seconds, (int, float))
        or cooldown_seconds < 0
    ):
        raise HarnessError("cooldown_seconds must be a number >= 0")
    if not candidates:
        raise HarnessError("no provider candidates")
    sink = log if log is not None else NullLog()
    pause = time.sleep if sleep is None else sleep
    clock = time.time if now is None else now
    attempts: list[dict] = []
    failures: list[str] = []
    for name in candidates:
        if cooldowns is not None:
            cooled = cooldowns.active(clock())
            if name in cooled:
                reason = cooled[name].get("reason")
                sink.event(
                    "provider.skipped",
                    packet_id=request.packet_id,
                    provider=name,
                    reason="cooldown",
                    route_id=request.route_id,
                )
                attempts.append(
                    {"attempt": 0, "error": "cooldown", "ok": False, "provider": name, "reason": reason}
                )
                failures.append(f"{name}#cooldown")
                continue
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
                result = _execute(
                    adapter,
                    request,
                    allow_live=allow_live,
                    timeout_seconds=timeout_seconds,
                    name=name,
                    should_stop=should_stop,
                )
            except RunCancelled:
                raise
            except HarnessError as exc:
                error = type(exc).__name__
                sink.event("provider.failed", attempt=attempt, error=error, provider=name)
                row = {"attempt": attempt, "error": error, "ok": False, "provider": name}
                reason = getattr(exc, "reason", None)
                if isinstance(reason, str):
                    row["reason"] = reason
                attempts.append(row)
                failures.append(f"{name}#{attempt}:{error}")
                if isinstance(exc, ProviderAvailability):
                    if cooldowns is not None:
                        moment = clock()
                        cooldowns.record(
                            name,
                            exc.reason,
                            resolve_until(exc.until, exc.retry_after, moment, float(cooldown_seconds)),
                        )
                    break
                if isinstance(exc, (ProviderTransient, ProviderTimeout)) and attempt < retries:
                    pause(backoff_seconds * (attempt + 1))
                continue
            sink.event("provider.result", attempt=attempt, live=result.live, provider=name)
            attempts.append(
                {"attempt": attempt, "live": result.live, "ok": True, "provider": name}
            )
            return result, attempts
    error = HarnessError("no provider completed the task: " + ", ".join(failures))
    error.attempts = attempts
    raise error


def _execute(
    adapter,
    request: ProviderRequest,
    *,
    allow_live: bool,
    timeout_seconds,
    name: str,
    should_stop,
) -> ProviderResult:
    kwargs: dict = {"allow_live": allow_live}
    if timeout_seconds is not None:
        kwargs["timeout_seconds"] = timeout_seconds.get(name)
    if _accepts(adapter.execute, "should_stop"):
        kwargs["should_stop"] = should_stop
    return adapter.execute(request, **kwargs)


def _accepts(func, name: str) -> bool:
    """True when ``func`` can take ``name`` without surprising older test doubles."""

    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return False
    parameters = signature.parameters
    if name in parameters:
        return True
    return any(item.kind is inspect.Parameter.VAR_KEYWORD for item in parameters.values())

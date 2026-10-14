"""Retry one provider, then fall back to the next capable provider."""

from __future__ import annotations

from scripts.v3.harness.errors import HarnessError
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
) -> tuple[ProviderResult, list[dict]]:
    """Try each candidate up to ``retries`` extra times.

    A raised ``HarnessError`` is a failed attempt. The next attempt uses the
    same provider until its retries are spent, then the next candidate. Stderr
    from a live process is not recorded.
    """

    if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
        raise HarnessError("retries must be an integer >= 0")
    if not candidates:
        raise HarnessError("no provider candidates")
    sink = log if log is not None else NullLog()
    attempts: list[dict] = []
    failures: list[str] = []
    for name in candidates:
        adapter = open_adapter(name)
        for attempt in range(retries + 1):
            sink.event(
                "provider.attempt",
                attempt=attempt,
                packet_id=request.packet_id,
                provider=name,
                route_id=request.route_id,
            )
            try:
                result = adapter.execute(request, allow_live=allow_live)
            except HarnessError as exc:
                error = type(exc).__name__
                sink.event("provider.failed", attempt=attempt, error=error, provider=name)
                attempts.append({"attempt": attempt, "error": error, "ok": False, "provider": name})
                failures.append(f"{name}#{attempt}:{error}")
                continue
            sink.event("provider.result", attempt=attempt, live=result.live, provider=name)
            attempts.append(
                {"attempt": attempt, "live": result.live, "ok": True, "provider": name}
            )
            return result, attempts
    raise HarnessError("no provider completed the task: " + ", ".join(failures))

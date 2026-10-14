"""Classify adapter failures and order capable providers.

Stderr is read for a failure class and a reset time, then discarded. The
exception text never includes the process output.
"""

from __future__ import annotations

import json
import re
import shutil

from scripts.v3.harness.errors import (
    HarnessError,
    ProviderAuthExpired,
    ProviderQuotaExhausted,
    ProviderRateLimited,
    ProviderTransient,
)


_ISO = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_RETRY_AFTER = re.compile(r"retry[- ]after:?\s*(\d+)", re.IGNORECASE)
_TRY_AGAIN = re.compile(r"try again in\s+(\d+)\s*(second|minute)s?", re.IGNORECASE)
_AUTH = (
    "auth expired",
    "authentication expired",
    "authentication required",
    "authentication_failed",
    "login expired",
    "not logged in",
    "not signed in",
    "please log in",
    "please login",
    "invalid api key",
    "invalid_api_key",
    "unauthorized",
    "session expired",
    "oauth token expired",
    "re-authenticate",
    "run /login",
    "codex login",
    "set an auth method",
)
_QUOTA = (
    "insufficient_quota",
    "quota exceeded",
    "quota",
    "usage limit",
    "credit balance",
    "out of credits",
    "billing",
    "billing_error",
    "resource_exhausted",
    "spend limit",
)
_RATE = (
    "rate limit",
    "rate_limit",
    "too many requests",
    "overloaded",
)
_TRANSIENT = (
    "temporarily unavailable",
    "connection reset",
    "connection refused",
    "timed out",
)


def classify_failure(
    name: str,
    returncode: int,
    stderr: str,
    stdout: str = "",
) -> HarnessError | None:
    """Return a classified error, or None when the process succeeded.

    Stderr is scanned for the failure phrases. Stdout is not scanned as a
    whole: only JSON fields that a CLI uses to report a failure (an ``error``
    event, an error string, or a result with ``is_error``). A task that
    mentions those words stays out of the classification.
    """

    signals = _failure_signals(stdout)
    if returncode == 0 and not signals:
        return None
    text = "\n".join(part for part in ((stderr or ""), signals) if part).lower()
    code = returncode if returncode else 1
    until, retry_after = _reset("\n".join(part for part in ((stderr or ""), signals) if part))
    if code == 401 or _contains(text, _AUTH):
        return ProviderAuthExpired(
            f"{name} authentication expired", until=until, retry_after=retry_after
        )
    if code == 402 or _contains(text, _QUOTA):
        return ProviderQuotaExhausted(
            f"{name} quota is exhausted", until=until, retry_after=retry_after
        )
    if code == 429 or _contains(text, _RATE):
        return ProviderRateLimited(f"{name} was rate-limited", until=until, retry_after=retry_after)
    if code in {500, 502, 503, 504} or _contains(text, _TRANSIENT):
        return ProviderTransient(f"{name} hit a transient error")
    return HarnessError(f"{name} exited {code}")


def _failure_signals(stdout: str) -> str:
    """Join failure fields from a JSON line stream. Empty when none are present."""

    pieces: list[str] = []
    failed = False
    for line in (stdout or "").splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("type") == "error" and isinstance(payload.get("message"), str):
            pieces.append(payload["message"])
            failed = True
        error = payload.get("error")
        if isinstance(error, str) and error:
            pieces.append(error)
            failed = True
        elif isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message:
                pieces.append(message)
                failed = True
        item = payload.get("item")
        if (
            isinstance(item, dict)
            and item.get("type") == "error"
            and isinstance(item.get("message"), str)
        ):
            pieces.append(item["message"])
            failed = True
        if payload.get("type") == "result" and payload.get("is_error") is True:
            failed = True
            result = payload.get("result")
            if isinstance(result, str) and result:
                pieces.append(result)
            reason = payload.get("terminal_reason")
            if isinstance(reason, str) and reason:
                pieces.append(reason)
    if failed and not pieces:
        pieces.append("is_error")
    return "\n".join(pieces) if failed else ""


def order_candidates(
    names: list[str],
    *,
    preference: list[str],
    weights: dict[str, int] | None = None,
) -> list[str]:
    """Higher weight first. Equal weights keep preference order."""

    weight_of = weights or {}
    rank = {name: index for index, name in enumerate(preference)}
    return sorted(
        names,
        key=lambda name: (-int(weight_of.get(name, 1)), rank.get(name, len(rank))),
    )


def provider_report(config: dict, cooldowns, *, finder) -> list[dict]:
    """One row per configured provider. ``finder`` is not asked to run the CLI."""

    active = {} if cooldowns is None else cooldowns.active()
    weights = config["routing"].get("weights") or {}
    rows = []
    for item in config["providers"]:
        name = item["name"]
        command = item["argv"][0]
        found = True if _offline(name) else finder(command) is not None
        cool = active.get(name)
        rows.append(
            {
                "capabilities": list(item["capabilities"]),
                "cli_found": bool(found),
                "command": command,
                "cooldown": None
                if cool is None
                else {"reason": cool.get("reason"), "until": cool.get("until")},
                "enabled": item["enabled"],
                "name": name,
                "weight": weights.get(name, 1),
            }
        )
    return rows


def _offline(name: str) -> bool:
    """True for a fixture that never starts a process.

    Imported lazily. ``providers`` already imports ``classify_failure`` from
    this module.
    """

    from scripts.v3.harness.providers import adapters

    cls = adapters().get(name)
    return cls is not None and bool(getattr(cls, "OFFLINE", False))


def default_cli_finder(command: str):
    """Use doctor's PATH search when that module is installed, else ``which``.

    This does not call ``diagnose`` and does not start the provider.
    """

    try:
        from scripts.v3.harness import doctor
    except ImportError:
        doctor = None
    resolve = getattr(doctor, "resolve_executable", None) if doctor is not None else None
    if resolve is not None:
        return resolve(command)
    return shutil.which(command)


def _contains(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def _reset(stderr: str) -> tuple[str | None, float | None]:
    found = _ISO.search(stderr)
    until = found.group(0) if found else None
    retry = _RETRY_AFTER.search(stderr)
    if retry:
        return until, float(retry.group(1))
    again = _TRY_AGAIN.search(stderr)
    if again:
        amount = float(again.group(1))
        if again.group(2).lower().startswith("minute"):
            amount *= 60
        return until, amount
    return until, None

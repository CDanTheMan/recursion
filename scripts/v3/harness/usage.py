"""Read token and cost figures from provider streams. Missing figures stay unknown."""

from __future__ import annotations

import json
import threading


def empty_usage() -> dict:
    return {"cost": None, "input_tokens": None, "output_tokens": None}


def parse_usage(text: str) -> dict:
    """Return the last usage object a stream actually reported.

    Claude result events, Codex ``turn.completed`` events, and Grok streaming
    JSON lines are all accepted. Text with no usage object does not become zero.
    """

    found = empty_usage()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        parsed = _from_event(payload)
        if parsed is not None:
            found = parsed
    return found


def add_usage(total: dict, extra: dict) -> dict:
    """Add known figures. An unknown figure does not contribute a zero."""

    for key in ("cost", "input_tokens", "output_tokens"):
        if extra.get(key) is None:
            continue
        total[key] = extra[key] if total.get(key) is None else total[key] + extra[key]
    return total


def exceeded(spent: dict, budgets: dict) -> bool:
    """True when a known figure is above its configured ceiling."""

    pairs = (
        ("input_tokens", "max_input_tokens"),
        ("output_tokens", "max_output_tokens"),
        ("cost", "max_cost"),
    )
    for spent_key, limit_key in pairs:
        limit = budgets.get(limit_key)
        value = spent.get(spent_key)
        if limit is not None and value is not None and value > limit:
            return True
    return False


class BudgetGuard:
    """Thread-safe running total for one run."""

    def __init__(self, budgets: dict) -> None:
        self.budgets = budgets
        self.spent = empty_usage()
        self.tripped = False
        self._lock = threading.Lock()

    def add(self, usage: dict) -> bool:
        with self._lock:
            add_usage(self.spent, usage)
            if exceeded(self.spent, self.budgets):
                self.tripped = True
            return self.tripped


def _from_event(payload: object) -> dict | None:
    if not isinstance(payload, dict):
        return None
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        usage = payload if _looks_like_usage(payload) else None
    if not isinstance(usage, dict):
        return None
    parsed = empty_usage()
    parsed["input_tokens"] = _int_field(usage, "input_tokens", "prompt_tokens")
    parsed["output_tokens"] = _int_field(usage, "output_tokens", "completion_tokens")
    parsed["cost"] = _number_field(payload, "total_cost_usd", "cost")
    if parsed["cost"] is None:
        parsed["cost"] = _number_field(usage, "cost", "total_cost_usd")
    if parsed["input_tokens"] is None and parsed["output_tokens"] is None and parsed["cost"] is None:
        return None
    return parsed


def _looks_like_usage(payload: dict) -> bool:
    return any(key in payload for key in ("input_tokens", "output_tokens", "prompt_tokens", "completion_tokens"))


def _int_field(payload: dict, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        if value >= 0:
            return value
    return None


def _number_field(payload: dict, *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value >= 0:
            return float(value)
    return None

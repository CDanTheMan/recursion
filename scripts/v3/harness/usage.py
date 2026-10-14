"""Read token and cost figures from provider streams. Missing figures stay unknown."""

from __future__ import annotations

import json
import threading


def empty_usage() -> dict:
    return {"cost": None, "input_tokens": None, "output_tokens": None}


def parse_usage(text: str) -> dict:
    """Return usage a stream actually reported.

    Claude result events, Codex ``turn.completed`` events, Grok streaming JSON,
    Gemini ``result.stats``, Cursor ``result.usage``, and OpenCode
    ``step_finish`` parts are accepted. OpenCode reports one cost and token
    object per step, so those steps are summed. Other CLIs repeat an aggregate
    on the final result, so the last of those events wins. Text with no usage
    object does not become zero.
    """

    found = empty_usage()
    opencode_total = empty_usage()
    saw_opencode = False
    saw_other = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and _is_opencode_step(payload):
            parsed = _opencode_usage(payload)
            if parsed is not None:
                add_usage(opencode_total, parsed)
                saw_opencode = True
            continue
        parsed = _from_event(payload)
        if parsed is not None:
            found = parsed
            saw_other = True
    if saw_other:
        return found
    if saw_opencode:
        return opencode_total
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
        stats = payload.get("stats")
        if isinstance(stats, dict) and _looks_like_usage(stats):
            usage = stats
        elif _looks_like_usage(payload):
            usage = payload
        else:
            usage = None
    if not isinstance(usage, dict):
        return None
    parsed = empty_usage()
    parsed["input_tokens"] = _int_field(usage, "input_tokens", "prompt_tokens", "inputTokens")
    parsed["output_tokens"] = _int_field(usage, "output_tokens", "completion_tokens", "outputTokens")
    parsed["cost"] = _number_field(payload, "total_cost_usd", "cost")
    if parsed["cost"] is None:
        parsed["cost"] = _number_field(usage, "cost", "total_cost_usd")
    if parsed["input_tokens"] is None and parsed["output_tokens"] is None and parsed["cost"] is None:
        return None
    return parsed


def _is_opencode_step(payload: dict) -> bool:
    if payload.get("type") == "step_finish":
        return True
    part = payload.get("part")
    return isinstance(part, dict) and part.get("type") == "step-finish"


def _opencode_usage(payload: dict) -> dict | None:
    part = payload.get("part")
    if not isinstance(part, dict):
        part = payload
    parsed = empty_usage()
    tokens = part.get("tokens")
    if isinstance(tokens, dict):
        parsed["input_tokens"] = _int_field(tokens, "input", "input_tokens", "inputTokens")
        parsed["output_tokens"] = _int_field(tokens, "output", "output_tokens", "outputTokens")
    if "cost" in part:
        parsed["cost"] = _number_field(part, "cost")
    if parsed["input_tokens"] is None and parsed["output_tokens"] is None and parsed["cost"] is None:
        return None
    return parsed


def _looks_like_usage(payload: dict) -> bool:
    keys = ("input_tokens", "output_tokens", "prompt_tokens", "completion_tokens", "inputTokens", "outputTokens")
    return any(key in payload for key in keys)


def _int_field(payload: dict, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int) and value >= 0:
            return value
        if isinstance(value, float) and value >= 0 and value.is_integer():
            return int(value)
    return None


def _number_field(payload: dict, *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value >= 0:
            return float(value)
    return None

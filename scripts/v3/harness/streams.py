"""Separate assistant text from headless JSON streams.

Token and cost figures stay in ``usage.parse_usage``. A missing figure there is
unknown, not zero. Tool output is not the assistant text.
"""

from __future__ import annotations

import json

from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.usage import parse_usage


def parse_transcript(provider: str, text: str) -> dict:
    """Return assistant text and the usage object for one recorded stream."""

    events = _events(text)
    if provider == "gemini":
        body = _gemini_text(events)
    elif provider == "cursor":
        body = _cursor_text(events)
    elif provider == "opencode":
        body = _opencode_text(events)
    else:
        raise HarnessError(f"no transcript parser for {provider!r}")
    return {"text": body, "usage": parse_usage(text)}


def _events(text: str) -> list[dict]:
    events = []
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise HarnessError(f"stream line {number} is not JSON") from exc
        if not isinstance(payload, dict):
            raise HarnessError(f"stream line {number} is not an object")
        events.append(payload)
    return events


def _gemini_text(events: list[dict]) -> str:
    parts: list[str] = []
    for event in events:
        if event.get("type") != "message" or event.get("role") != "assistant":
            continue
        content = event.get("content")
        if isinstance(content, str):
            parts.append(content)
    return "".join(parts)


def _cursor_text(events: list[dict]) -> str:
    result = None
    for event in events:
        if event.get("type") == "result" and isinstance(event.get("result"), str):
            result = event["result"]
    if result is not None:
        return result
    parts: list[str] = []
    for event in events:
        if event.get("type") != "assistant":
            continue
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if isinstance(content, str):
            parts.append(content)
            continue
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    parts.append(block["text"])
    return "".join(parts)


def _opencode_text(events: list[dict]) -> str:
    parts: list[str] = []
    for event in events:
        if event.get("type") != "text":
            continue
        part = event.get("part")
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            parts.append(part["text"])
    return "\n".join(parts)

"""Replace token-shaped text before it is written to a log, report, or run."""

from __future__ import annotations

import re


REDACTED = "[REDACTED]"
_SECRET_KEY = re.compile(
    r"(?i)^(api[_-]?key|token|secret|password|authorization|credential|xai[_-]?api[_-]?key)$"
)
_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|auth[_-]?token|token|secret|password|"
    r"authorization|credential|xai[_-]?api[_-]?key)\b(\s*[:=]\s*)([\"']?)\S+"
)
_TOKEN = re.compile(
    "|".join(
        (
            r"sk-ant-[A-Za-z0-9_-]{8,}",
            r"sk-or-v1-[A-Za-z0-9_-]{8,}",
            r"sk-[A-Za-z0-9_-]{16,}",
            r"xai-[A-Za-z0-9_-]{8,}",
            r"ghp_[A-Za-z0-9]{20,}",
            r"github_pat_[A-Za-z0-9_]{16,}",
            r"glpat-[A-Za-z0-9_-]{8,}",
            r"AKIA[0-9A-Z]{16}",
            r"ASIA[0-9A-Z]{16}",
            r"xox[baprs]-[A-Za-z0-9-]{8,}",
            r"AIza[0-9A-Za-z_-]{20,}",
            r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
        )
    )
)
_BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}", re.IGNORECASE)


def redact_text(text: str) -> str:
    """Hide assignments and recognizable token shapes. Ordinary words stay."""

    text = _ASSIGNMENT.sub(lambda match: f"{match.group(1)}{match.group(2)}{match.group(3)}{REDACTED}", text)
    text = _BEARER.sub(REDACTED, text)
    return _TOKEN.sub(REDACTED, text)


def redact(value: object) -> object:
    """Return a copy with secret-shaped strings replaced."""

    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if isinstance(key, str) and _SECRET_KEY.fullmatch(key):
                cleaned[key] = REDACTED
            else:
                cleaned[key] = redact(item)
        return cleaned
    return value

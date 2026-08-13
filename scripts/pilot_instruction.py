#!/usr/bin/env python3
"""Small fail-closed grammar for authenticated Lucas Phase-8 commands."""

from __future__ import annotations

import re


NEGATION_PATTERN = re.compile(
    r"\b(?:do\s+not|don'?t|doesn'?t|never|not|cannot|can'?t|won'?t|"
    r"shouldn'?t|must\s+not|shall\s+not)\b",
    re.IGNORECASE,
)
OPPOSITE_PATTERN = {
    "pilot-plan-approve": re.compile(
        r"\b(?:reject\w*|refus\w*|revok\w*|deny\w*|denied|declin\w*|unapprov\w*)\b",
        re.IGNORECASE,
    ),
    "pilot-window-open": re.compile(
        r"\b(?:clos\w*|revok\w*|withdraw\w*|rescind\w*)\b",
        re.IGNORECASE,
    ),
    "pilot-window-close": re.compile(
        r"\b(?:open\w*|authoriz\w*|arm\w*)\b",
        re.IGNORECASE,
    ),
}
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}")


def _sequences(verb: str, terms: list[str]) -> list[list[str]]:
    # An @ prefix marks case-insensitive grammar words. Authority-bound identifiers and digests
    # remain byte-exact and therefore carry no prefix.
    if verb == "pilot-plan-approve" and len(terms) == 2:
        plan_id, digest = terms
        return [
            ["@approve", plan_id, digest],
            ["@approve", "@pilot", "@plan", plan_id, "@with", "@digest", digest],
            ["@approve", "@plan", plan_id, "@digest", digest],
        ]
    if verb == "pilot-window-open" and len(terms) == 3:
        goal_id, window_id, seconds = terms
        return [
            ["@authorize", goal_id, window_id, seconds],
            ["@open", goal_id, window_id, seconds],
            ["@authorize", "@pilot", "@window", window_id, "@for", "@goal", goal_id,
             "@for", seconds, "@seconds"],
            ["@open", "@pilot", "@window", window_id, "@for", "@goal", goal_id,
             "@for", seconds, "@seconds"],
        ]
    if verb == "pilot-window-close" and len(terms) == 1:
        window_id = terms[0]
        return [["@close", window_id], ["@close", "@pilot", "@window", window_id]]
    return []


def require_affirmative_command(body: str, verb: str, terms: list[str]) -> None:
    """Require one exact affirmative command and reject negated/opposite language."""
    if verb not in OPPOSITE_PATTERN:
        raise ValueError("unsupported Phase 8 authority verb")
    tokens = [token.rstrip(".") for token in TOKEN.findall(body)]
    sequences = _sequences(verb, [str(term) for term in terms])
    found = any(
        all(actual.lower() == expected[1:] if expected.startswith("@") else actual == expected
            for actual, expected in zip(tokens[index:index + len(sequence)], sequence))
        for sequence in sequences
        for index in range(len(tokens) - len(sequence) + 1)
    )
    if not found:
        raise ValueError("instruction does not name the exact Phase 8 command and bounds")
    normalized = re.sub(r"\s+", " ", body).strip()
    if NEGATION_PATTERN.search(normalized) or OPPOSITE_PATTERN[verb].search(normalized):
        raise ValueError("instruction is negated or ambiguous for the requested Phase 8 operation")

"""Reference model (candidate under test) for the R-PC literal specimen.

Minimal provider-free model of the deterministic assembler used by F01/F11/F12:

- sources are an unordered SET; the render order comes from a pinned declared ``order`` key and a
  stable tie-break on ``id`` — **never** from enumeration order, filesystem order or arrival order;
- ranges are half-open **UTF-8 byte** offsets;
- the canonical manifest is deterministic JSON (sorted keys, no whitespace).

This model is the *candidate*; the expected values live in the independent ``oracle`` module.
"""
from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    id: str
    data: bytes
    order: int


def render(sources: list[Source]) -> tuple[bytes, dict[str, tuple[int, int]], list[tuple[str, int, int]]]:
    ordered = sorted(sources, key=lambda s: (s.order, s.id))
    out = bytearray()
    ranges: dict[str, tuple[int, int]] = {}
    spans: list[tuple[str, int, int]] = []
    for source in ordered:
        start = len(out)
        out += source.data
        end = len(out)
        ranges[source.id] = (start, end)
        spans.append((source.id, start, end))
    return bytes(out), ranges, spans


def canonical_manifest(ranges: dict[str, tuple[int, int]], total: int) -> bytes:
    obj = {"ranges": {k: [v[0], v[1]] for k, v in sorted(ranges.items())}, "total": total}
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def prefix_plan(output: bytes, n: int = 18) -> bytes:
    return output[:n]


def render_by_enumeration(sources: list[Source]) -> bytes:
    """A deliberately wrong mutant: renders in list/enumeration order."""
    out = bytearray()
    for source in sources:
        out += source.data
    return bytes(out)

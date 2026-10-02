"""R-PC literal-specimen fixture definitions (F01/F11/F12).

Values are taken verbatim from the R-PC report section 9 "Concrete literal specimen" and the
F01/F11/F12 predicate rows. Each item is ``(id, utf8_bytes, declared_order)``. These are synthetic
test inputs, not a selected product encoding.
"""
from __future__ import annotations

# F01 / F11 base specimen: CONTROL\n + PROCEDURE\n + DATA\n = 23 bytes, ranges [0,8) [8,18) [18,23).
BASE: list[tuple[str, bytes, int]] = [
    ("core", b"CONTROL\n", 0),
    ("skill", b"PROCEDURE\n", 1),
    ("evidence", b"DATA\n", 2),
]

# F11 tail change: DATA\n -> FACT\n preserves the first 18 bytes, same total length 23.
TAIL_CHANGE: list[tuple[str, bytes, int]] = [
    ("core", b"CONTROL\n", 0),
    ("skill", b"PROCEDURE\n", 1),
    ("evidence", b"FACT\n", 2),
]

# F11 core change: CONTROL\n -> CONTROL2\n changes the prefix, total length 24, offsets shift.
CORE_CHANGE: list[tuple[str, bytes, int]] = [
    ("core", b"CONTROL2\n", 0),
    ("skill", b"PROCEDURE\n", 1),
    ("evidence", b"DATA\n", 2),
]

# F12 Unicode: a two-byte non-ASCII character (U+00E9) appended as evidence; ranges are byte-based.
UNICODE: list[tuple[str, bytes, int]] = [
    ("core", b"CONTROL\n", 0),
    ("skill", b"PROCEDURE\n", 1),
    ("evidence", b"DATA\n", 2),
    ("note", "\u00e9".encode("utf-8"), 3),  # 2 UTF-8 bytes, 1 codepoint
]

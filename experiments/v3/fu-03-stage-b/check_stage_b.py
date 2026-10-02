#!/usr/bin/env python3
"""FU-03 Stage B design gate.

Deterministic and provider-free. Validates the Stage B design artifacts under this directory
ONLY: the crash-cut matrix parses, every fixture carries the required fields with valid enum
values, every named lane-case reference is present, no fixture is marked executed, and no field
claims a run result. It runs nothing and reads no other project.

    python -X utf8 -B experiments/v3/fu-03-stage-b/check_stage_b.py

A pass certifies the design is internally complete and unexecuted. It is NOT a Stage B result,
not IT-02 acceptance and not a kernel or receiver qualification.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES_PATH = HERE / "fixtures.json"

REQUIRED_DOCS = ["README.md", "fixtures.json", "USING-SESSION-A-ORACLE.md", "check_stage_b.py"]

REQUIRED_FIELDS = [
    "id",
    "status",
    "cut_point",
    "injected_schedule",
    "receiver_fence_state",
    "stop_mode",
    "observation_oracle",
    "expected_disposition",
    "decidable_predicate",
    "references",
]

CUT_POINTS = {
    "admit",
    "prepared",
    "commit",
    "dispatch",
    "response-loss-before-receipt",
    "response-loss-after-dispatch",
}
FENCE_STATES = {"not-installed", "installed-old-epoch", "installed-current"}
STOP_MODES = {"Aggressive", "Full", "Lazy"}

# The named lane cases the packet requires Stage B to retain (LOCAL-SESSION-HANDOFF.md section B).
REQUIRED_REFS = {
    "rx:RX-F06", "rx:RX-F07", "rx:RX-F08", "rx:RX-F09", "rx:RX-F10", "rx:RX-F11", "rx:RX-F12",
    "rx:RX-F21", "rx:RX-F22", "rx:RX-F23",
    "rr:F03", "rr:F07", "rr:F10", "rr:F11", "rr:F17", "rr:F18", "rr:F20",
    "rv:V-F04", "rv:V-F07", "rv:V-F11", "rv:V-F18",
    "rf:RF-F05", "rf:RF-F06", "rf:RF-F11", "rf:RF-F12", "rf:RF-F14", "rf:RF-F15",
    "rf:RF-F16", "rf:RF-F17", "rf:RF-F18", "rf:RF-F19", "rf:RF-F20",
    "protocol:MCP01", "protocol:MCP04", "protocol:MCP05", "protocol:MCP06",
}

# A key whose mere presence would claim a run happened. Exact match, case-insensitive.
FORBIDDEN_KEYS = {
    "executed", "executing", "execution_result", "execution_evidence", "run", "ran",
    "result", "observed_result", "actual_result", "observed_state", "observed_outcome",
    "actual_outcome", "verdict", "pass", "fail", "exit_code", "test_result",
}

# A string value that would claim an execution verdict. Exact match, case-insensitive.
VERDICT_VALUES = {"executed", "executing", "ran", "run", "pass", "passed", "fail", "failed"}

UNEXECUTED = "unexecuted"


def fail(message: str) -> None:
    print(f"STAGE_B_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def scan_for_run_claims(node, path: str) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            key_text = str(key)
            if key_text.strip().lower() in FORBIDDEN_KEYS:
                fail(f"field {path}.{key_text} claims a run result; design must stay unexecuted")
            scan_for_run_claims(value, f"{path}.{key_text}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            scan_for_run_claims(value, f"{path}[{index}]")
    elif isinstance(node, str):
        if node.strip().lower() in VERDICT_VALUES:
            fail(f"value at {path} claims an execution verdict: {node!r}")
    elif isinstance(node, bool):
        if node is True and "execut" in path.lower():
            fail(f"boolean at {path} claims execution")


def main() -> int:
    for rel in REQUIRED_DOCS:
        if not (HERE / rel).exists():
            fail(f"missing design artifact: {rel}")

    try:
        doc = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"fixtures.json did not parse: {error}")

    if not isinstance(doc, dict):
        fail("fixtures.json must be a JSON object")
    fixtures = doc.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        fail("fixtures.json must contain a non-empty 'fixtures' list")

    seen_ids: set[str] = set()
    covered_refs: set[str] = set()
    for index, fixture in enumerate(fixtures):
        where = f"fixtures[{index}]"
        if not isinstance(fixture, dict):
            fail(f"{where} is not an object")

        for field in REQUIRED_FIELDS:
            if field not in fixture:
                fail(f"{where} missing required field {field!r}")

        fid = fixture["id"]
        if not isinstance(fid, str) or not fid.strip():
            fail(f"{where}.id must be a non-empty string")
        if fid in seen_ids:
            fail(f"duplicate fixture id {fid}")
        seen_ids.add(fid)

        status = fixture["status"]
        if status != UNEXECUTED:
            fail(f"{fid}: status {status!r} is not {UNEXECUTED!r}; no fixture may be marked executed")

        if fixture["cut_point"] not in CUT_POINTS:
            fail(f"{fid}: invalid cut_point {fixture['cut_point']!r}")
        if fixture["receiver_fence_state"] not in FENCE_STATES:
            fail(f"{fid}: invalid receiver_fence_state {fixture['receiver_fence_state']!r}")
        if fixture["stop_mode"] not in STOP_MODES:
            fail(f"{fid}: invalid stop_mode {fixture['stop_mode']!r}")

        for list_field in ("injected_schedule", "observation_oracle", "references"):
            value = fixture[list_field]
            if not isinstance(value, list) or not value:
                fail(f"{fid}: {list_field} must be a non-empty list")
            if not all(isinstance(item, str) and item.strip() for item in value):
                fail(f"{fid}: {list_field} must contain non-empty strings")

        for text_field in ("expected_disposition", "decidable_predicate"):
            value = fixture[text_field]
            if not isinstance(value, str) or not value.strip():
                fail(f"{fid}: {text_field} must be a non-empty string")

        for ref in fixture["references"]:
            if ref not in REQUIRED_REFS:
                fail(f"{fid}: reference {ref!r} is not a named Stage B lane case")
            covered_refs.add(ref)

    missing = sorted(REQUIRED_REFS - covered_refs)
    if missing:
        fail(f"named lane-case references not covered: {missing}")

    scan_for_run_claims(fixtures, "fixtures")

    print(
        f"STAGE_B_DESIGN_PASS fixtures={len(fixtures)} refs_covered={len(covered_refs)} "
        f"unexecuted={len(fixtures)} cut_points={len(CUT_POINTS)} "
        f"fence_states={len(FENCE_STATES)} stop_modes={len(STOP_MODES)}"
    )
    print("NOTE: design-only matrix; no fixture executed and no Stage B result claimed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

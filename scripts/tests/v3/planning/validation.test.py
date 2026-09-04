#!/usr/bin/env python3
"""Focused tests for strict decoding, canonicalization, and DAG validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT))

from scripts.v3.planning.validation.canonical import (  # noqa: E402
    M1AError, canonical_bytes, decode, digest,
)
from scripts.v3.planning.validation.contracts import validate_dag  # noqa: E402


def main() -> int:
    decoded = dag_cases = 0
    for path in sorted(FIXTURE_DIR.glob("F-M1A-*.json")):
        for case in json.loads(path.read_text(encoding="utf-8"))["cases"]:
            for raw, expected in zip(
                case["decode_inputs"], case["expected_decode_failures"], strict=True
            ):
                try:
                    decode(raw, expected["schema_epoch"])
                except M1AError as error:
                    assert error.code == expected["primary_error"]
                else:
                    raise AssertionError("strict decoder accepted a negative oracle")
                decoded += 1
            for command, receipt in zip(
                case["initial_commands"] + case["commands"],
                case["initial_receipts"] + case["expected_receipts"], strict=True,
            ):
                assert digest(command, omit_content_digest=True) == command["content_digest"]
                assert canonical_bytes(command) == canonical_bytes(
                    dict(reversed(list(command.items())))
                )
                if command["command_type"] not in ("propose-plan-revision", "propose-replan"):
                    continue
                payload = command["payload"]
                plan = payload.get("plan_revision", payload.get("new_plan_revision"))
                error, witness = validate_dag(plan, payload["task_nodes"])
                if receipt["primary_error"] in {"E-DAG-CYCLE", "E-DAG-DEPENDENCY", "E-DAG-CONFLICT"}:
                    assert error == receipt["primary_error"]
                    assert witness == receipt["witness"]
                elif receipt["primary_error"] is None:
                    assert error is None and witness is None
                dag_cases += 1
    assert canonical_bytes({"\uffff": 1, "\U00010000": 2}) == b'{"\xf0\x90\x80\x80":2,"\xef\xbf\xbf":1}'
    print(f"M1A_VALIDATION_PASS decode_failures={decoded} dag_cases={dag_cases}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"M1A_VALIDATION_FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from error

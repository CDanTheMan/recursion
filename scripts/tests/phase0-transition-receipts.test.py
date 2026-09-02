#!/usr/bin/env python3
"""Verify the sealed Phase 0 receipt snapshot against tracked canonical state."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECEIPTS = ROOT / "docs/audits/recursion-v2-phase0-transition-receipts"


def compact(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(compact(value)).hexdigest()


def read_fields(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="surrogateescape").splitlines():
        if not line.strip():
            break
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            result.setdefault(key.strip(), value.strip())
    return result


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    manifest = json.loads((RECEIPTS / "manifest.json").read_text(encoding="utf-8"))
    check(manifest.get("kind") == "sealed-transition-receipt-snapshot", "manifest kind")

    events = [json.loads(line) for line in
              (ROOT / "state/events.jsonl").read_text(encoding="utf-8").splitlines()
              if line.strip()]
    by_id: dict[str, list[dict]] = {}
    for event in events:
        by_id.setdefault(str(event.get("id")), []).append(event)

    for item in manifest.get("receipts", []):
        transition_id = item["id"]
        prepared_path = RECEIPTS / f"{transition_id}.prepared.json"
        projected_path = RECEIPTS / f"{transition_id}.projected.json"
        prepared_bytes = prepared_path.read_bytes()
        projected_bytes = projected_path.read_bytes()
        check(hashlib.sha256(prepared_bytes).hexdigest() == item["prepared_sha256"],
              f"{transition_id}: prepared snapshot hash")
        check(hashlib.sha256(projected_bytes).hexdigest() == item["projected_sha256"],
              f"{transition_id}: projected snapshot hash")

        receipt = json.loads(prepared_bytes)
        projected = json.loads(projected_bytes)
        check(receipt.get("schema_version") == 1 and receipt.get("kind") == "transition-receipt",
              f"{transition_id}: receipt envelope")
        check(receipt.get("id") == transition_id, f"{transition_id}: receipt identity")
        event = dict(receipt["event"])
        check(event.get("transition_id") == transition_id,
              f"{transition_id}: event transition identity")
        journal_rows = by_id.get(str(event.get("id")), [])
        check(len(journal_rows) == 1 and journal_rows[0] == event,
              f"{transition_id}: frozen event must equal tracked journal event")
        check(projected == {
            "at": projected["at"], "event_id": event["id"],
            "schema_version": 1, "status": "projected",
        }, f"{transition_id}: projected marker")

        frozen_event = dict(event)
        frozen_event.pop("transition_id")
        mutations = receipt.get("mutations") or []
        if mutations:
            seed = {
                "event": frozen_event,
                "paths": [mutation["path"] for mutation in mutations],
                "event_seq": receipt["event_seq"],
            }
        else:
            seed = {"journal": receipt["journal"], "event": frozen_event}
        expected_id = "transition-" + hashlib.sha256(compact(seed)).hexdigest()[:32]
        check(expected_id == transition_id, f"{transition_id}: deterministic receipt identity")

        for mutation in mutations:
            path = ROOT / mutation["path"]
            check(path.is_file(), f"{transition_id}: canonical target exists")
            if mutation["kind"] == "fields":
                current = read_fields(path)
                check(all(current.get(key) == value for key, value in mutation["expect"].items()),
                      f"{transition_id}: canonical field witness")
            elif mutation["kind"] == "json":
                current = json.loads(path.read_text(encoding="utf-8"))
                check(digest(current) == mutation["expect_sha256"],
                      f"{transition_id}: canonical JSON witness")
            else:
                raise AssertionError(f"{transition_id}: unexpected mutation kind")

    print(f"phase0-transition-receipts: PASS ({len(manifest['receipts'])} sealed receipts)")


if __name__ == "__main__":
    main()

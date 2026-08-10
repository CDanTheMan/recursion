#!/usr/bin/env python3
"""Red controls for PAUSE-held monitoring notifications.

The test reuses the Phase 7 inert transport fixture. No process can reach Hermes or Telegram.
It fails on the 2026-08-10 production implementation because brief/digest source events and the
taskctl notification boundary do not yet exist.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(value: bool, text: str, results: list[bool]) -> None:
    results.append(value)
    print(("ok    " if value else "FAIL  ") + text)


def main() -> int:
    phase7 = load("phase7_fixture", SOURCE / "scripts/tests/hermes-pilot-phase7-red.py")
    fixture = phase7.Fixture("phase8-monitoring")
    results: list[bool] = []
    try:
        digest = "Project digest: exact fixture body"
        brief = "Portfolio brief: exact fixture body"

        (fixture.root / "state/PAUSE").write_text("fixture PAUSE\n", encoding="utf-8")
        paused = fixture.run([
            "bash", "scripts/taskctl.sh", "notify-event", "project-digest", "alpha", digest,
        ])
        events_path = fixture.root / "state/events.jsonl"
        check(paused.returncode == 75 and not events_path.exists(),
              "PAUSE refuses even source-event enqueue at the canonical taskctl boundary", results)
        (fixture.root / "state/PAUSE").unlink()

        first = fixture.run([
            "bash", "scripts/taskctl.sh", "notify-event", "project-digest", "alpha", digest,
        ])
        duplicate = fixture.run([
            "bash", "scripts/taskctl.sh", "notify-event", "project-digest", "alpha", digest,
        ])
        portfolio = fixture.run([
            "bash", "scripts/taskctl.sh", "notify-event", "portfolio-brief", "alpha", brief,
        ])
        raw = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()] \
            if events_path.exists() else []
        digests = [row for row in raw if row.get("event") == "project-digest"]
        briefs = [row for row in raw if row.get("event") == "portfolio-brief"]
        check(first.returncode == duplicate.returncode == portfolio.returncode == 0 and
              len(digests) == 1 and len(briefs) == 1 and digests[0].get("id"),
              "monitoring source events are append-only, stable, and idempotent", results)

        bad_kind = fixture.run([
            "bash", "scripts/taskctl.sh", "notify-event", "arbitrary-send", "alpha", "no",
        ])
        bad_project = fixture.run([
            "bash", "scripts/taskctl.sh", "notify-event", "project-digest", "../alpha", "no",
        ])
        check(bad_kind.returncode != 0 and bad_project.returncode != 0,
              "the canonical source boundary rejects unknown kinds and malformed projects", results)

        fixture.ticks(6)
        events = fixture.events()
        mapped_digest = [row for row in events if row.get("event_type") == "project-digest"]
        mapped_brief = [row for row in events if row.get("event_type") == "portfolio-brief"]
        check(len(mapped_digest) == 1 and mapped_digest[0].get("message") == digest and
              len(mapped_brief) == 1 and mapped_brief[0].get("message") == brief,
              "Phase 7 maps the exact monitored body without a model/process delivery claim", results)

        digest_deliveries = phase7.event_deliveries(fixture, "project-digest")
        brief_deliveries = phase7.event_deliveries(fixture, "portfolio-brief")
        receipts = list((fixture.root / "state/transport-evidence").glob("*.json"))
        check(len(digest_deliveries) == 1 and
              digest_deliveries[0].get("destination") == fixture.project_topic and
              digest_deliveries[0].get("status") == "succeeded" and
              len(brief_deliveries) == 1 and
              brief_deliveries[0].get("destination") == fixture.head and
              brief_deliveries[0].get("status") == "succeeded" and len(receipts) == 2,
              "digest and brief use policy routing and exact durable transport acknowledgements", results)
    finally:
        fixture.close()

    failed = len([result for result in results if not result])
    if failed:
        print(f"\nhermes-pilot-phase8-notification-red: {failed} FAILED")
        return 1
    print("\nhermes-pilot-phase8-notification-red: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Red controls for PAUSE-held monitoring notifications.

The test reuses the Phase 7 inert transport fixture. No process can reach Hermes or Telegram.
It fails on the 2026-08-10 production implementation because brief/digest source events and the
taskctl notification boundary do not yet exist.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from unittest import mock

from windows_test_support import bash_command


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

        # The same rendered digest is one occurrence today and a new occurrence on another UTC
        # day. Reuse the source id deliberately: the outbox must include occurrence_date in its
        # mapped identity instead of trusting content identity alone.
        second_occurrence = dict(digests[0])
        second_occurrence.update({"ts": "2099-12-31T06:30:00Z"})
        second_detail = dict(second_occurrence["detail"])
        second_detail["occurrence_date"] = "2099-12-31"
        second_occurrence["detail"] = second_detail
        with events_path.open("a", encoding="utf-8") as output:
            output.write(json.dumps(second_occurrence, sort_keys=True) + "\n")
        fixture.ticks(3)
        mapped_digest = [row for row in fixture.events() if row.get("event_type") == "project-digest"]
        digest_deliveries = phase7.event_deliveries(fixture, "project-digest")
        check(len(mapped_digest) == 2 and
              {row.get("occurrence_date") for row in mapped_digest} >= {"2099-12-31"} and
              len(digest_deliveries) == 2 and all(row.get("status") == "succeeded" for row in digest_deliveries),
              "daily digest identity includes occurrence_date while same-occurrence duplicates collapse", results)

        outbox_identity = load("notification_outbox_identity", SOURCE / "scripts/notification-outbox.py")
        legacy_source = dict(second_occurrence)
        legacy_source["_source_id"] = str(legacy_source["id"])
        legacy_detail = dict(legacy_source["detail"])
        legacy_detail.pop("occurrence_date", None)
        legacy_source["detail"] = legacy_detail
        legacy_mapped = outbox_identity.mapped_events(legacy_source)[0]
        check(legacy_mapped["id"] == outbox_identity.stable_id(
                  "event", legacy_source["_source_id"], "project-digest") and
              legacy_mapped.get("occurrence_date") == "2099-12-31",
              "legacy digest identity stays stable while its occurrence date is projected", results)

        # PAUSE after attempt-started is a temporary hold, not a permanent transport failure. The
        # patched subprocess boundary creates PAUSE immediately before notify.sh starts.
        mid_pause = phase7.Fixture("mid-delivery-pause")
        try:
            mid_pause.append_event("source-mid-pause", "start")
            mid_pause.ticks(1)
            pending = phase7.event_deliveries(mid_pause, "worker-launched")[0]
            outbox = load("notification_outbox_mid_pause", SOURCE / "scripts/notification-outbox.py")
            original_run = outbox.subprocess.run

            def pause_then_run(*args, **kwargs):
                (mid_pause.root / "state/PAUSE").write_text("mid-delivery fixture\n", encoding="utf-8")
                return original_run(*args, **kwargs)

            held = False
            try:
                outbox.subprocess.run = pause_then_run
                with mock.patch.dict(os.environ, {**mid_pause.env, "RECURSION_QUEUE_ACTUATION": "1"}):
                    try:
                        outbox.deliver(mid_pause.root, "alpha", pending["id"])
                    except outbox.OutboxError as exc:
                        held = "PAUSE" in str(exc)
            finally:
                outbox.subprocess.run = original_run
            after = next(row for row in mid_pause.deliveries() if row["id"] == pending["id"])
            check(held and after.get("status") == "pending" and after.get("attempt") == 0 and
                  not mid_pause.calls() and not phase7.event_deliveries(mid_pause, "delivery-dead-letter"),
                  "PAUSE after attempt-started restores pending delivery without dead-letter or send", results)
        finally:
            mid_pause.close()

        # Fallback metered spend observed under PAUSE remains in the prior snapshot and in the
        # durable escalation index. On resume the same delta is sent through notify.sh and only
        # then becomes the new snapshot baseline.
        fallback = phase7.Fixture("fallback-pause")
        try:
            fake_curl = fallback.root / "bin/curl"
            fake_curl.write_text(phase7.FAKE_CURL_STUB, encoding="utf-8")
            fake_curl.chmod(0o755)
            hermes_log = fallback.temp / "hermes.log"
            fake_hermes = fallback.root / "bin/hermes"
            fake_hermes.write_text(
                "#!/usr/bin/env bash\nprintf 'called\\n' >> \"$FALLBACK_HERMES_LOG\"\n",
                encoding="utf-8",
            )
            fake_hermes.chmod(0o755)
            snapshot = fallback.root / "state/.openrouter-usage.json"
            snapshot.write_text('{"total_usage":10,"total_credits":100,"at":"fixture"}\n', encoding="utf-8")
            fallback_env = {
                "OPENROUTER_API_KEY": "fixture-key-never-sent",
                "FAKE_CURL_MODE": "openrouter-credits",
                "FAKE_OPENROUTER_USAGE": "12",
                "FAKE_OPENROUTER_CREDITS": "100",
                "FALLBACK_HERMES_LOG": str(hermes_log),
                "PATH": str(fallback.root / "bin") + os.pathsep + fallback.env.get("PATH", ""),
                "RECURSION_LOCK_ATTEMPTS": "1",
                "RECURSION_LOCK_DELAY_S": "0.01",
            }
            lock = fallback.root / "state/.locks/taskctl.lock"
            lock.mkdir()
            locked_watch = fallback.run(bash_command("scripts/fallback-watch.sh"), env=fallback_env)
            locked_usage = json.loads(snapshot.read_text(encoding="utf-8"))["total_usage"]
            lock.rmdir()
            durable_guard = locked_watch.returncode == 73 and locked_usage == 10 and not hermes_log.exists()

            (fallback.root / "state/PAUSE").write_text("fallback fixture\n", encoding="utf-8")
            paused_watch = fallback.run(bash_command("scripts/fallback-watch.sh"), env=fallback_env)
            paused_usage = json.loads(snapshot.read_text(encoding="utf-8"))["total_usage"]
            escalations = fallback.root / "state/escalations.tsv"
            durable = escalations.is_file() and "fallback-spend:openrouter" in escalations.read_text(encoding="utf-8")
            no_paused_send = not hermes_log.exists()
            (fallback.root / "state/PAUSE").unlink()
            resumed_watch = fallback.run(bash_command("scripts/fallback-watch.sh"), env=fallback_env)
            resumed_usage = json.loads(snapshot.read_text(encoding="utf-8"))["total_usage"]
            calls = hermes_log.read_text(encoding="utf-8").splitlines() if hermes_log.exists() else []
            check(durable_guard and paused_watch.returncode == resumed_watch.returncode == 0 and paused_usage == 10 and
                  durable and no_paused_send and resumed_usage == 12 and calls == ["called"],
                  "paused fallback spend remains durable and advances only after resumed notification", results)
        finally:
            fallback.close()
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

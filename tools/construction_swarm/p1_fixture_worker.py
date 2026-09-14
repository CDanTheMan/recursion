"""Child-process fixture used only by P1 durability and leader-election tests."""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from .p1_core import (
    FakeHermes,
    FakeTransport,
    GOAL_ID,
    REQUIREMENTS_DIGEST,
    SOURCE_COMMIT,
    P1Store,
    request_digest,
)


def _wait(path):
    while not Path(path).exists():
        time.sleep(.005)


def _request(task, project, grant):
    value = {"protocol_version": 1, "goal_id": GOAL_ID, "task_id": task, "project": project,
             "expected_revision": 1, "source_commit": SOURCE_COMMIT,
             "requirements_digest": REQUIREMENTS_DIGEST, "grant_id": grant,
             "idempotency_key": "crash-reservation", "claimed_actor": "owner"}
    value["content_digest"] = request_digest(value)
    return value


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    elect = commands.add_parser("elect")
    elect.add_argument("--root", required=True)
    elect.add_argument("--owner", required=True)
    elect.add_argument("--ready", required=True)
    elect.add_argument("--start", required=True)
    elect.add_argument("--result", required=True)
    crash = commands.add_parser("crash")
    crash.add_argument("--root", required=True)
    crash.add_argument("--hermes", required=True)
    crash.add_argument("--owner", required=True)
    crash.add_argument("--task", required=True)
    crash.add_argument("--project", required=True)
    crash.add_argument("--grant", required=True)
    crash.add_argument("--phase", choices=("reserved", "launch_intent"), required=True)
    args = parser.parse_args()
    store = P1Store(args.root)
    if args.command == "elect":
        Path(args.ready).write_text("ready", encoding="utf-8")
        _wait(args.start)
        try:
            result = {"acquired": True, "fence": store.acquire_leader(args.owner)}
        except Exception as exc:  # fixture records a refusal for the parent assertion
            result = {"acquired": False, "error": type(exc).__name__}
        Path(args.result).write_text(json.dumps(result), encoding="utf-8")
        store.close()
        return 0
    hermes = FakeHermes(args.hermes)
    fence = store.acquire_leader(args.owner, takeover=True)
    accepted = store.accept(hermes, FakeTransport("worker"), _request(args.task, args.project, args.grant), args.owner, fence)
    if args.phase == "launch_intent":
        store.begin_launch(FakeTransport("worker"), accepted["attempt_id"], args.owner, fence)
    # Abruptly exit after the durable reserve or launch intent, before the next effect/receipt.
    os._exit(19)


if __name__ == "__main__":
    raise SystemExit(main())

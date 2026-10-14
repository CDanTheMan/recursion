"""``recursion`` command: plan, run, and status."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.v3.harness.capabilities import select_candidates
from scripts.v3.harness.config import load_config
from scripts.v3.harness.dispatch import execute_with_policy
from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.log import JsonLog, read_events
from scripts.v3.harness.planning import plan_task
from scripts.v3.harness.providers import ProviderRequest
from scripts.v3.harness.routing import require_selected, select_route


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="recursion", description="Plan a task and run it through a provider adapter.")
    parser.add_argument("--config", type=Path, help="provider config JSON (default: config/harness.json)")
    commands = parser.add_subparsers(dest="command", required=True)

    plan = commands.add_parser("plan", help="admit the task and the M1B route; do not start a provider")
    plan.add_argument("--task", required=True)
    plan.add_argument("--log", help="append JSONL events to this file as well as stderr")

    run = commands.add_parser("run", help="plan, admit a route, and execute a capable provider")
    run.add_argument("--task", required=True)
    run.add_argument("--provider", help="use this provider instead of capability order")
    run.add_argument("--capability", action="append", default=None, help="extra capability the provider must have")
    run.add_argument("--fallback", action="store_true", help="after an explicit provider fails, try the next capable provider")
    run.add_argument("--allow-live", action="store_true", help="start a headless CLI; omitted in tests and CI")
    run.add_argument("--log", help="append JSONL events to this file as well as stderr")

    status = commands.add_parser("status", help="show configured providers and a log summary")
    status.add_argument("--log", help="JSONL file to summarize")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    log: JsonLog | None = None
    handle = None
    try:
        if args.command in {"plan", "run"}:
            log, handle = _open_log(getattr(args, "log", None))
        if args.command == "plan":
            payload = plan_command(args, log)
        elif args.command == "run":
            payload = run_command(args, log)
        elif args.command == "status":
            payload = status_command(args)
        else:
            raise HarnessError(f"unknown command {args.command}")
    except HarnessError as exc:
        if log is not None:
            log.event("run.refused", error=type(exc).__name__)
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        if handle is not None:
            handle.close()
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    print()
    return 0


def plan_command(args: argparse.Namespace, log: JsonLog) -> dict:
    planned = plan_task(args.task)
    route = select_route()
    route_id = require_selected(route["decision"])
    log.event(
        "plan.admitted",
        accepted=planned["accepted"],
        packet_id=planned["packet_id"],
        projection_digest=planned["projection_digest"],
    )
    log.event(
        "route.selected",
        fixture_id=route["fixture_id"],
        selected_route_id=route_id,
        status=route["status"],
    )
    return {"planning": planned, "route": _route_view(route, route_id), "task": planned["intent_text"]}


def run_command(args: argparse.Namespace, log: JsonLog) -> dict:
    if args.fallback and not args.provider:
        raise HarnessError("--fallback applies to an explicit --provider")
    config = load_config(args.config)
    planned = plan_task(args.task)
    route = select_route()
    route_id = require_selected(route["decision"])
    log.event(
        "plan.admitted",
        accepted=planned["accepted"],
        packet_id=planned["packet_id"],
        projection_digest=planned["projection_digest"],
    )
    log.event(
        "route.selected",
        fixture_id=route["fixture_id"],
        selected_route_id=route_id,
        status=route["status"],
    )
    candidates = select_candidates(
        config,
        provider=args.provider,
        extra_capabilities=args.capability,
        fallback=args.fallback,
    )
    log.event("provider.candidates", candidates=candidates)
    request = ProviderRequest(task=planned["intent_text"], packet_id=planned["packet_id"], route_id=route_id)
    result, attempts = execute_with_policy(
        request,
        candidates,
        allow_live=args.allow_live,
        retries=config["routing"]["retries"],
        log=log,
    )
    log.event("run.completed", live=result.live, provider=result.provider)
    return {
        "attempts": attempts,
        "candidates": candidates,
        "execution": result.to_dict(),
        "planning": planned,
        "route": _route_view(route, route_id),
        "task": planned["intent_text"],
    }


def status_command(args: argparse.Namespace) -> dict:
    config = load_config(args.config)
    log_path = args.log
    events = read_events(Path(log_path)) if log_path else []
    last = events[-1]["event"] if events else None
    return {
        "config_version": config["version"],
        "log": {"events": len(events), "last_event": last, "path": log_path},
        "providers": [
            {
                "argv": item["argv"],
                "capabilities": item["capabilities"],
                "enabled": item["enabled"],
                "name": item["name"],
            }
            for item in config["providers"]
        ],
        "routing": config["routing"],
    }


def _route_view(route: dict, route_id: str) -> dict:
    return {
        "fixture_id": route["fixture_id"],
        "selected_route_id": route_id,
        "status": route["status"],
    }


def _open_log(path: str | None) -> tuple[JsonLog, object | None]:
    streams: list = [sys.stderr]
    handle = None
    if path:
        handle = open(path, "a", encoding="utf-8")
        streams.append(handle)
    return JsonLog(streams), handle


if __name__ == "__main__":
    raise SystemExit(main())

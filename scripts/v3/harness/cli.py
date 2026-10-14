"""``recursion`` command: plan, run, status, resume, cancel, providers, doctor, init, config, logs, land, and clean."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.v3.harness.availability import default_cli_finder, provider_report
from scripts.v3.harness.capabilities import select_candidates
from scripts.v3.harness.config import ROOT, default_config_path, load_config, write_starter
from scripts.v3.harness.clean import clean_runs
from scripts.v3.harness.cooldowns import CooldownStore
from scripts.v3.harness.dag import admit_goal
from scripts.v3.harness.doctor import diagnose, discover_installed
from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.isolation import GitWorktreeIsolator
from scripts.v3.harness.land import land_run
from scripts.v3.harness.log import JsonLog, read_events, select_events
from scripts.v3.harness.orchestrate import (
    cancel_run,
    create_run,
    drive_run,
    plan_goal,
    reopen_run,
    rotate_candidates,
    split_goal,
)
from scripts.v3.harness.planning import plan_task
from scripts.v3.harness.redact import redact
from scripts.v3.harness.routing import require_selected, select_route
from scripts.v3.harness.state import RunStore, default_state_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="recursion", description="Plan tasks and run them through provider adapters.")
    commands = parser.add_subparsers(dest="command", required=True)

    plan = commands.add_parser("plan", help="admit tasks and the M1B route; do not start a provider")
    _add_common(plan)
    plan.add_argument("--task", help="one task admitted through M1A")
    plan.add_argument("--goal", help="plan a task graph, or one task per line when planning falls back")
    plan.add_argument(
        "--log",
        help="append JSONL events to this file, and to stderr when progress lines are off",
    )

    run = commands.add_parser("run", help="plan, admit a route, and execute capable providers")
    _add_common(run)
    run.add_argument("--task", help="one task admitted through M1A")
    run.add_argument("--goal", help="plan a task graph and run it; line splitting is the fallback")
    run.add_argument("--provider", help="use this provider instead of capability order")
    run.add_argument("--capability", action="append", default=None, help="extra capability the provider must have")
    run.add_argument("--fallback", action="store_true", help="after an explicit provider fails, try the next capable provider")
    run.add_argument("--allow-live", action="store_true", help="start a headless CLI; omitted in tests and CI")
    run.add_argument("--base-ref", help="git ref the run branch is cut from (default: config landing.base_ref)")
    run.add_argument("--keep-worktrees", action="store_true", help="keep worktrees and branches for failed tasks")
    run.add_argument(
        "--concurrency",
        type=_concurrency_arg,
        help="override orchestration.concurrency for this invocation",
    )
    run.add_argument("--progress", action="store_true", help="print plain progress lines on stderr instead of JSONL")
    run.add_argument(
        "--log",
        help="append JSONL events to this file, and to stderr when progress lines are off",
    )

    status = commands.add_parser("status", help="show providers, log summary, and saved runs")
    _add_common(status)
    status.add_argument("--log", help="JSONL file to summarize")
    status.add_argument("--run", help="print one saved run")

    resume = commands.add_parser("resume", help="continue unfinished tasks from a saved run")
    _add_common(resume)
    resume.add_argument("--run", required=True)
    resume.add_argument("--allow-live", action="store_true")
    resume.add_argument("--base-ref", help="git ref used when the run branch does not exist yet")
    resume.add_argument("--keep-worktrees", action="store_true", help="keep worktrees and branches for failed tasks")
    resume.add_argument(
        "--concurrency",
        type=_concurrency_arg,
        help="override orchestration.concurrency for this invocation",
    )
    resume.add_argument("--progress", action="store_true", help="print plain progress lines on stderr instead of JSONL")
    resume.add_argument(
        "--log",
        help="append JSONL events to this file, and to stderr when progress lines are off",
    )

    cancel = commands.add_parser("cancel", help="cancel unfinished tasks in a saved run")
    _add_common(cancel)
    cancel.add_argument("--run", required=True)

    providers = commands.add_parser(
        "providers",
        help="show each provider, whether its CLI is found, its capabilities, and cooldown status",
    )
    _add_common(providers)

    doctor = commands.add_parser("doctor", help="check git and each configured provider executable")
    doctor.add_argument("--config", type=Path, help="provider config JSON (default: config/harness.json)")

    init = commands.add_parser("init", help="write a starter config that enables providers doctor can see")
    init.add_argument("path", type=Path, help="config path to create")
    init.add_argument("--force", action="store_true", help="overwrite an existing file")

    config = commands.add_parser("config", help="check a provider config")
    config_commands = config.add_subparsers(dest="config_command", required=True)
    validate = config_commands.add_parser("validate", help="check the config against the schema and the adapters")
    validate.add_argument("--config", type=Path, help="provider config JSON (default: config/harness.json)")

    logs = commands.add_parser("logs", help="show JSONL events for one saved run")
    logs.add_argument("run_id", help="saved run id")
    logs.add_argument("--state-dir", type=Path, help="directory for resumable run records")
    logs.add_argument("--task", help="task index or task id")
    logs.add_argument("--provider", help="provider name")
    logs.add_argument("--level", choices=("info", "warning", "error"), help="minimum level: info, warning, or error")
    logs.add_argument("--tail", type=int, help="print only the last N matching events")

    land = commands.add_parser("land", help="merge a finished run branch into a target branch")
    _add_common(land)
    land.add_argument("run_id", help="saved run id")
    land.add_argument("--into", help="branch that receives the run (default: the current branch)")

    clean = commands.add_parser("clean", help="prune old run state, worktrees, and task branches")
    _add_common(clean)
    clean.add_argument("--older-than", type=_days_arg, default=7, help="prune runs older than this many days")
    clean.add_argument("--dry-run", action="store_true", help="list what would be removed or skipped")
    clean.add_argument(
        "--include-unlanded",
        action="store_true",
        help="also remove unlanded run branches and worktrees with uncommitted changes",
    )
    return parser


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, help="provider config JSON (default: config/harness.json)")
    parser.add_argument("--state-dir", type=Path, help="directory for resumable run records")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    log: JsonLog | None = None
    handle = None
    try:
        if args.command in {"plan", "run", "resume"}:
            log, handle = _open_log(
                getattr(args, "log", None),
                _state_dir(args),
                progress=bool(getattr(args, "progress", False)),
            )
        if args.command == "plan":
            payload = plan_command(args, log)
        elif args.command == "run":
            payload = run_command(args, log)
        elif args.command == "status":
            payload = status_command(args)
        elif args.command == "resume":
            payload = resume_command(args, log)
        elif args.command == "cancel":
            payload = cancel_command(args)
        elif args.command == "providers":
            payload = providers_command(args)
        elif args.command == "doctor":
            payload = doctor_command(args)
        elif args.command == "init":
            payload = init_command(args)
        elif args.command == "config":
            payload = config_command(args)
        elif args.command == "logs":
            payload = logs_command(args)
        elif args.command == "land":
            payload = land_command(args)
        elif args.command == "clean":
            payload = clean_command(args)
        else:
            raise HarnessError(f"unknown command {args.command}")
    except HarnessError as exc:
        if log is not None:
            log.event("run.refused", error=type(exc).__name__)
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        if log is not None:
            log.close()
        if handle is not None:
            handle.close()
    if args.command == "logs":
        for record in payload:
            print(json.dumps(redact(record), ensure_ascii=False, sort_keys=True))
        return 0
    json.dump(redact(payload), sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    print()
    if args.command == "doctor" and not payload.get("ok"):
        return 1
    if args.command in {"run", "resume"} and payload.get("status") in {
        "budget-exceeded",
        "cancelled",
        "conflict",
        "failed",
        "review-rejected",
        "skipped",
        "unreviewed",
    }:
        return 2
    return 0


def plan_command(args: argparse.Namespace, log: JsonLog) -> dict:
    goal, single = _goal_text(args)
    route = select_route()
    route_id = require_selected(route["decision"])
    if single:
        planned = plan_task(goal)
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
    config = load_config(args.config)
    planned_goal = _admit(args, log, config, goal, allow_live=False)
    for item in planned_goal["tasks"]:
        log.event(
            "plan.admitted",
            accepted=item["accepted"],
            packet_id=item["packet_id"],
            projection_digest=item["projection_digest"],
        )
    log.event(
        "route.selected",
        fixture_id=route["fixture_id"],
        selected_route_id=route_id,
        status=route["status"],
    )
    return {
        "goal": planned_goal["goal"],
        "plan_fallback": planned_goal["fallback"],
        "plan_source": planned_goal["source"],
        "route": _route_view(route, route_id),
        "tasks": planned_goal["tasks"],
    }


def run_command(args: argparse.Namespace, log: JsonLog) -> dict:
    if args.fallback and not args.provider:
        raise HarnessError("--fallback applies to an explicit --provider")
    goal, single = _goal_text(args)
    config = load_config(args.config)
    route = select_route()
    route_id = require_selected(route["decision"])
    if single:
        planned = [plan_task(goal)]
        shown_goal = planned[0]["intent_text"]
    else:
        planned_goal = _admit(args, log, config, goal, allow_live=args.allow_live)
        planned = planned_goal["tasks"]
        shown_goal = planned_goal["goal"]
    for item in planned:
        log.event(
            "plan.admitted",
            accepted=item["accepted"],
            packet_id=item["packet_id"],
            projection_digest=item["projection_digest"],
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
    record = _drive_new_run(
        args,
        log,
        config=config,
        goal=shown_goal,
        planned=planned,
        candidates=_assign_candidates(candidates, planned, config),
        route=_route_view(route, route_id),
        route_id=route_id,
        plan_source=planned_goal["source"] if not single else "lines",
        plan_fallback=planned_goal["fallback"] if not single else None,
    )
    if single:
        task = record["tasks"][0]
        if record["status"] not in {"completed", "unreviewed"}:
            if record["status"] == "budget-exceeded":
                raise HarnessError("budget exceeded")
            raise HarnessError(task["error"] or "no provider completed the task")
        return {
            "attempts": task["attempts"],
            "candidates": task["candidates"],
            "execution": task["execution"],
            "planning": planned[0],
            "report": record.get("report"),
            "reviews": task.get("reviews"),
            "route": record["route"],
            "run_id": record["run_id"],
            "status": record["status"],
            "task": task["task"],
        }
    return record


def resume_command(args: argparse.Namespace, log: JsonLog) -> dict:
    config = load_config(args.config)
    store = _store(args)
    record = reopen_run(store, args.run)
    override = getattr(args, "concurrency", None)
    if override is not None:

        def apply_concurrency(current: dict) -> None:
            current["concurrency"] = override

        store.update(record["run_id"], apply_concurrency)
    log.bind(run_id=record["run_id"])
    route_id = record["route"]["selected_route_id"]
    log.event("run.resume", run_id=record["run_id"], status=record["status"])
    return _drive_existing(args, log, config, store, record["run_id"], route_id)


def config_command(args: argparse.Namespace) -> dict:
    if args.config_command != "validate":
        raise HarnessError(f"unknown config command {args.config_command}")
    path = args.config if args.config is not None else default_config_path()
    loaded = load_config(path)
    return {"ok": True, "path": str(path), "version": loaded["version"]}


def logs_command(args: argparse.Namespace) -> list[dict]:
    store = _store(args)
    record = store.load(args.run_id)
    path = store.root / f"{args.run_id}.jsonl"
    if not path.is_file():
        raise HarnessError(f"no log for {args.run_id}")
    if args.tail is not None and args.tail < 0:
        raise HarnessError("--tail must be an integer >= 0")
    return select_events(
        read_events(path),
        task_index=_task_index(record, args.task),
        provider=args.provider,
        level=args.level,
        tail=args.tail,
    )


def land_command(args: argparse.Namespace) -> dict:
    return land_run(_store(args), args.run_id, repo=ROOT, into=args.into)


def clean_command(args: argparse.Namespace) -> dict:
    return clean_runs(
        _store(args),
        repo=ROOT,
        older_than_days=args.older_than,
        dry_run=bool(args.dry_run),
        include_unlanded=bool(args.include_unlanded),
    )


def cancel_command(args: argparse.Namespace) -> dict:
    return cancel_run(_store(args), args.run)


def providers_command(args: argparse.Namespace) -> dict:
    config = load_config(args.config)
    return {"providers": provider_report(config, _cooldowns(args), finder=default_cli_finder)}


def doctor_command(args: argparse.Namespace) -> dict:
    return diagnose(load_config(args.config))


def init_command(args: argparse.Namespace) -> dict:
    target = Path(args.path)
    if target.is_dir():
        raise HarnessError(f"{target} is a directory")
    if target.exists() and not args.force:
        raise HarnessError(f"refusing to overwrite {target}; pass --force")
    enabled = discover_installed()
    write_starter(target, set(enabled), force=args.force)
    return {"enabled": enabled, "path": str(target)}


def status_command(args: argparse.Namespace) -> dict:
    config = load_config(args.config)
    log_path = args.log
    events = read_events(Path(log_path)) if log_path else []
    last = events[-1]["event"] if events else None
    store = _store(args)
    payload = {
        "config_version": config["version"],
        "log": {"events": len(events), "last_event": last, "path": log_path},
        "providers": [
            {
                "argv": item["argv"],
                "capabilities": item["capabilities"],
                "enabled": item["enabled"],
                "name": item["name"],
                "timeout_seconds": item["timeout_seconds"],
            }
            for item in config["providers"]
        ],
        "routing": config["routing"],
        "runs": store.list_runs(),
    }
    if args.run:
        payload["run"] = store.load(args.run)
    return payload


def _drive_new_run(
    args,
    log,
    *,
    config,
    goal,
    planned,
    candidates,
    route,
    route_id,
    plan_source: str,
    plan_fallback: str | None,
) -> dict:
    store = _store(args)
    override = getattr(args, "concurrency", None)
    concurrency = config["orchestration"]["concurrency"] if override is None else override
    record = create_run(
        store,
        goal=goal,
        planned=planned,
        candidates=candidates,
        route=route,
        concurrency=concurrency,
        plan_source=plan_source,
        plan_fallback=plan_fallback,
    )
    log.bind(run_id=record["run_id"])
    return _drive_existing(args, log, config, store, record["run_id"], route_id)


def _drive_existing(args, log, config, store, run_id: str, route_id: str) -> dict:
    base_ref = args.base_ref if getattr(args, "base_ref", None) else config["landing"]["base_ref"]
    return drive_run(
        store,
        run_id,
        allow_live=args.allow_live,
        retries=config["routing"]["retries"],
        backoff_seconds=config["routing"]["backoff_seconds"],
        timeout_seconds=_timeouts(config),
        route_id=route_id,
        log=log,
        max_rounds=config["review"]["max_rounds"],
        budgets=config["budgets"],
        isolator=GitWorktreeIsolator(ROOT),
        accept_unreviewed=config["review"]["accept_unreviewed"],
        base_ref=base_ref,
        keep_worktrees=bool(getattr(args, "keep_worktrees", False)),
        cooldowns=_cooldowns(args),
        cooldown_seconds=config["routing"]["cooldown_seconds"],
    )


def _admit(args, log, config, goal: str, *, allow_live: bool) -> dict:
    candidates = select_candidates(config, extra_capabilities=getattr(args, "capability", None))
    return admit_goal(
        goal,
        candidates=candidates,
        allow_live=allow_live,
        retries=config["routing"]["retries"],
        backoff_seconds=config["routing"]["backoff_seconds"],
        timeout_seconds=_timeouts(config),
        log=log,
        open_adapter=None,
        cooldowns=_cooldowns(args),
        cooldown_seconds=config["routing"]["cooldown_seconds"],
    )


def _assign_candidates(candidates: list[str], planned: list[dict], config: dict) -> list[list[str]]:
    rotated = rotate_candidates(candidates, len(planned))
    capabilities = {item["name"]: set(item["capabilities"]) for item in config["providers"]}
    assigned = []
    for index, item in enumerate(planned):
        required = set(item.get("required_capabilities") or [])
        if not required:
            assigned.append(rotated[index])
            continue
        assigned.append([name for name in rotated[index] if required <= capabilities.get(name, set())])
    return assigned


def _goal_text(args: argparse.Namespace) -> tuple[str, bool]:
    has_task = bool(getattr(args, "task", None))
    has_goal = bool(getattr(args, "goal", None))
    if has_task == has_goal:
        raise HarnessError("pass one of --task or --goal")
    if has_task:
        return args.task, True
    split_goal(args.goal)
    return args.goal, False


def _timeouts(config: dict) -> dict[str, int]:
    return {item["name"]: item["timeout_seconds"] for item in config["providers"]}


def _state_dir(args: argparse.Namespace) -> Path:
    return args.state_dir if getattr(args, "state_dir", None) is not None else default_state_dir()


def _cooldowns(args: argparse.Namespace) -> CooldownStore:
    return CooldownStore(_store(args).root / "cooldowns.json")


def _store(args: argparse.Namespace) -> RunStore:
    return RunStore(_state_dir(args))


def _task_index(record: dict, task: str | None) -> int | None:
    if task is None:
        return None
    tasks = record.get("tasks") if isinstance(record.get("tasks"), list) else []
    if task.isdigit():
        index = int(task)
        if any(isinstance(item, dict) and item.get("index") == index for item in tasks):
            return index
    for item in tasks:
        if isinstance(item, dict) and item.get("id") == task and isinstance(item.get("index"), int):
            return item["index"]
    raise HarnessError(f"unknown task {task}")


def _route_view(route: dict, route_id: str) -> dict:
    return {
        "fixture_id": route["fixture_id"],
        "selected_route_id": route_id,
        "status": route["status"],
    }


def _days_arg(text: str) -> int:
    if not text.isdigit():
        raise argparse.ArgumentTypeError("older-than must be an integer >= 0")
    return int(text)


def _concurrency_arg(text: str) -> int:
    if not text.isdigit():
        raise argparse.ArgumentTypeError("concurrency must be an integer >= 1")
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("concurrency must be an integer >= 1")
    return value


def _stderr_is_tty() -> bool:
    isatty = getattr(sys.stderr, "isatty", None)
    if isatty is None:
        return False
    try:
        return bool(isatty())
    except Exception:
        return False


def _open_log(path: str | None, state_dir: Path, *, progress: bool) -> tuple[JsonLog, object | None]:
    json_streams: list = []
    progress_stream = None
    handle = None
    if progress or _stderr_is_tty():
        progress_stream = sys.stderr
    else:
        json_streams.append(sys.stderr)
    if path:
        handle = open(path, "a", encoding="utf-8")
        json_streams.append(handle)
    return JsonLog(json_streams, state_dir=state_dir, progress=progress_stream), handle


if __name__ == "__main__":
    raise SystemExit(main())

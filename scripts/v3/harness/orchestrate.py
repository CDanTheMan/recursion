"""Plan one goal into M1A tasks and run them in dependency order."""

from __future__ import annotations

import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from scripts.v3.harness.context import task_prompt
from scripts.v3.harness.dag import line_nodes
from scripts.v3.harness.errors import HarnessError, RunCancelled
from scripts.v3.harness.isolation import NullIsolator
from scripts.v3.harness.log import BoundLog, NullLog, utc_now
from scripts.v3.harness.planning import plan_task
from scripts.v3.harness.report import write_reports
from scripts.v3.harness.review import execute_and_review
from scripts.v3.harness.state import RunStore
from scripts.v3.harness.usage import BudgetGuard, empty_usage


_REOPEN = {"budget-exceeded", "cancelled", "conflict", "failed", "review-rejected", "running", "skipped", "unreviewed"}
_BLOCKED = {"budget-exceeded", "cancelled", "conflict", "failed", "review-rejected", "skipped", "unreviewed"}


def split_goal(goal: str) -> list[str]:
    """Return one task per non-empty line. Each line is admitted on its own."""

    if not isinstance(goal, str):
        raise HarnessError("goal text is empty")
    tasks = [line.strip() for line in goal.splitlines() if line.strip()]
    if not tasks:
        raise HarnessError("goal text is empty")
    return tasks


def plan_goal(goal: str, nodes: list[dict] | None = None, source: str = "lines", fallback: str | None = None) -> dict:
    """Admit each task through the M1A kernel. Projections stay separate."""

    chosen = nodes if nodes is not None else line_nodes(split_goal(goal))
    if not chosen:
        raise HarnessError("goal text is empty")
    tasks = []
    for node in chosen:
        admitted = plan_task(node["description"])
        admitted["depends_on"] = list(node["depends_on"])
        admitted["id"] = node["id"]
        admitted["required_capabilities"] = list(node["required_capabilities"])
        tasks.append(admitted)
    return {"fallback": fallback, "goal": goal.strip(), "source": source, "tasks": tasks}


def rotate_candidates(candidates: list[str], count: int) -> list[list[str]]:
    """Spread tasks across providers. Task ``i`` starts at the ``i``-th candidate."""

    if not candidates:
        raise HarnessError("no provider candidates")
    if count < 1:
        raise HarnessError("no tasks to assign")
    rotated = []
    for index in range(count):
        shift = index % len(candidates)
        rotated.append(candidates[shift:] + candidates[:shift])
    return rotated


def new_run_id() -> str:
    return "RUN-" + uuid.uuid4().hex[:16]


def create_run(
    store: RunStore,
    *,
    goal: str,
    planned: list[dict],
    candidates: list[list[str]],
    route: dict,
    concurrency: int,
    plan_source: str = "lines",
    plan_fallback: str | None = None,
) -> dict:
    run_id = new_run_id()
    record = {
        "base_ref": None,
        "cancel_requested": False,
        "concurrency": concurrency,
        "cooldowns": {},
        "created": utc_now(),
        "goal": goal,
        "plan_fallback": plan_fallback,
        "plan_source": plan_source,
        "route": route,
        "run_branch": None,
        "run_id": run_id,
        "status": "running",
        "stop_reason": None,
        "tasks": [
            {
                "attempts": [],
                "branch": None,
                "candidates": list(candidates[index]),
                "commit": None,
                "depends_on": list(item.get("depends_on") or []),
                "diff": "",
                "duration_seconds": None,
                "error": None,
                "execution": None,
                "id": item.get("id") or f"task-{index + 1}",
                "index": index,
                "merge_conflict": [],
                "merge_status": None,
                "packet_id": item["packet_id"],
                "projection_digest": item["projection_digest"],
                "provider": None,
                "required_capabilities": list(item.get("required_capabilities") or []),
                "reviews": [],
                "status": "pending",
                "task": item["intent_text"],
                "text": None,
                "usage": empty_usage(),
            }
            for index, item in enumerate(planned)
        ],
    }

    def create(current: dict) -> dict:
        current.clear()
        current.update(record)
        return current

    store.update(run_id, create)
    return store.load(run_id)


def drive_run(
    store: RunStore,
    run_id: str,
    *,
    allow_live: bool,
    retries: int,
    backoff_seconds: float,
    timeout_seconds: dict[str, int],
    route_id: str,
    log: object | None = None,
    open_adapter=None,
    sleep=None,
    max_rounds: int = 0,
    budgets: dict | None = None,
    isolator=None,
    accept_unreviewed: bool = False,
    base_ref: str = "HEAD",
    keep_worktrees: bool = False,
    cooldowns=None,
    cooldown_seconds: float = 60,
    now=None,
) -> dict:
    """Execute pending tasks whose dependencies have landed."""

    record = store.load(run_id)
    concurrency = record["concurrency"]
    if isinstance(concurrency, bool) or not isinstance(concurrency, int) or concurrency < 1:
        raise HarnessError("run concurrency must be an integer >= 1")
    sink = log if log is not None else NullLog()
    pause = time.sleep if sleep is None else sleep
    checkout = isolator if isolator is not None else NullIsolator()
    if open_adapter is None:
        from scripts.v3.harness.providers import open_provider

        open_adapter = open_provider
    guard = BudgetGuard(
        budgets
        or {"max_cost": None, "max_input_tokens": None, "max_output_tokens": None}
    )
    started = time.monotonic()
    run_branch = checkout.ensure_run_branch(run_id, base_ref)

    def remember(current: dict) -> None:
        current["base_ref"] = base_ref
        current["run_branch"] = run_branch

    store.update(run_id, remember)
    condition = threading.Condition()
    progress = {"done": 0, "inflight": 0}

    def stopped() -> bool:
        if guard.tripped:
            return True
        return store.load(run_id).get("cancel_requested") is True

    def claim_ready(current: dict) -> list[int]:
        if current.get("cancel_requested") or guard.tripped:
            return []
        _skip_blocked(current["tasks"])
        running = sum(task["status"] == "running" for task in current["tasks"])
        claimed = []
        for task in current["tasks"]:
            if running >= current["concurrency"]:
                break
            if task["status"] != "pending" or not _deps_met(task, current["tasks"]):
                continue
            task["error"] = None
            task["status"] = "running"
            running += 1
            claimed.append(task["index"])
        return claimed

    def work(index: int) -> None:
        task = store.load(run_id)["tasks"][index]
        if store.load(run_id).get("cancel_requested"):
            def cancel_early(current: dict) -> None:
                _cancel_task(current, index)
                _skip_blocked(current["tasks"])

            store.update(run_id, cancel_early)
            sink.event("task.cancelled", index=index, run_id=run_id)
            return
        sink.event("task.started", index=index, packet_id=task["packet_id"], run_id=run_id)
        iso = None
        outcome = None
        diff = ""
        commit = None
        begun = time.monotonic()
        keep_branch = keep_worktrees
        keep_tree = keep_worktrees
        try:
            if not task["candidates"]:
                raise HarnessError("no provider has the required capabilities")
            start_ref = store.load(run_id).get("run_branch")
            iso = checkout.acquire(run_id, index, start_ref)
            outcome = execute_and_review(
                task=task_prompt(task, store.load(run_id)["tasks"]),
                packet_id=task["packet_id"],
                route_id=route_id,
                candidates=list(task["candidates"]),
                allow_live=allow_live,
                retries=retries,
                backoff_seconds=backoff_seconds,
                timeout_seconds=timeout_seconds,
                max_rounds=max_rounds,
                cwd=None if iso.path is None else str(iso.path),
                diff_of=lambda: checkout.diff(iso),
                log=BoundLog(sink, index=index, packet_id=task["packet_id"], run_id=run_id),
                open_adapter=open_adapter,
                sleep=pause,
                should_stop=stopped,
                accept_unreviewed=accept_unreviewed,
                seal=lambda: checkout.commit_pending(iso, _land_message(task)),
                snapshot=lambda: checkout.snapshot(iso),
                restore=lambda head: checkout.restore(iso, head),
                cooldowns=cooldowns,
                cooldown_seconds=cooldown_seconds,
                now=now,
            )
            diff = checkout.diff(iso)
            keep_branch = keep_worktrees or outcome["disposition"] in {"completed", "unreviewed"}
            keep_tree = keep_worktrees and outcome["disposition"] not in {"completed", "unreviewed"}
            if keep_branch:
                commit = checkout.commit_pending(iso, _land_message(task))
        except RunCancelled:
            keep_branch = keep_worktrees
            keep_tree = keep_worktrees

            def cancel(current: dict) -> None:
                _cancel_task(current, index)
                current["tasks"][index]["branch"] = iso.branch if iso is not None and keep_branch else None
                current["tasks"][index]["duration_seconds"] = round(time.monotonic() - begun, 3)
                _skip_blocked(current["tasks"])

            store.update(run_id, cancel)
            sink.event("task.cancelled", index=index, run_id=run_id)
            return
        except HarnessError as exc:
            keep_branch = keep_worktrees
            keep_tree = keep_worktrees

            def fail(current: dict) -> None:
                item = current["tasks"][index]
                item["branch"] = iso.branch if iso is not None and keep_branch else None
                item["duration_seconds"] = round(time.monotonic() - begun, 3)
                item["error"] = str(exc)
                item["status"] = "failed"
                _skip_blocked(current["tasks"])

            store.update(run_id, fail)
            sink.event("task.failed", error=type(exc).__name__, index=index, run_id=run_id)
            return
        except Exception:
            keep_branch = keep_worktrees
            keep_tree = keep_worktrees

            def fail_unknown(current: dict) -> None:
                item = current["tasks"][index]
                item["branch"] = iso.branch if iso is not None and keep_branch else None
                item["duration_seconds"] = round(time.monotonic() - begun, 3)
                item["error"] = "task failed"
                item["status"] = "failed"
                _skip_blocked(current["tasks"])

            store.update(run_id, fail_unknown)
            sink.event("task.failed", error="Exception", index=index, run_id=run_id)
            return
        finally:
            if iso is not None:
                checkout.release(iso, keep_branch=keep_branch, keep_worktree=keep_tree)
        merge = {"commit": None, "paths": [], "status": "not-landed"}
        disposition = outcome["disposition"]
        if disposition == "completed" and commit is not None:
            try:
                merge = checkout.merge_into_run(run_branch, iso.branch)
            except HarnessError:
                merge = {"commit": None, "paths": [], "status": "conflict"}
            if merge["status"] == "conflict":
                disposition = "conflict"
        elif disposition == "completed":
            merge = {"commit": None, "paths": [], "status": "landed"}
        tripped = guard.add(outcome["usage"])
        if tripped:
            def mark_budget(current: dict) -> None:
                current["cancel_requested"] = True
                current["stop_reason"] = "budget"

            store.update(run_id, mark_budget)

        def succeed(current: dict) -> None:
            item = current["tasks"][index]
            item["attempts"] = outcome["attempts"]
            item["branch"] = iso.branch if iso is not None and keep_branch else None
            item["commit"] = commit
            item["diff"] = diff
            item["duration_seconds"] = round(time.monotonic() - begun, 3)
            item["execution"] = outcome["result"].to_dict()
            item["merge_conflict"] = list(merge["paths"])
            item["merge_status"] = merge["status"]
            item["provider"] = outcome["result"].provider
            item["reviews"] = outcome["reviews"]
            item["text"] = outcome["result"].text
            item["usage"] = outcome["usage"]
            if disposition == "conflict":
                item["error"] = _conflict_error(merge["paths"])
                item["status"] = "conflict"
            elif disposition == "unreviewed":
                item["error"] = "review did not complete"
                item["status"] = "unreviewed"
            elif disposition == "review-rejected":
                item["error"] = "review rejected"
                item["status"] = "review-rejected"
            else:
                item["error"] = None
                item["status"] = "completed"
            _skip_blocked(current["tasks"])

        store.update(run_id, succeed)
        event = {
            "completed": "task.completed",
            "conflict": "task.conflict",
            "review-rejected": "task.review_rejected",
            "unreviewed": "task.unreviewed",
        }[disposition]
        sink.event(event, index=index, provider=outcome["result"].provider, run_id=run_id)

    def wrapped(index: int) -> None:
        try:
            work(index)
        finally:
            with condition:
                progress["inflight"] -= 1
                progress["done"] += 1
                condition.notify_all()

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        while True:
            claimed = store.update(run_id, claim_ready) or []
            if not claimed:
                with condition:
                    if progress["inflight"] == 0:
                        break
                    condition.wait()
                continue
            seen = progress["done"]
            with condition:
                progress["inflight"] += len(claimed)
            for index in claimed:
                pool.submit(wrapped, index)
            with condition:
                while progress["inflight"] and progress["done"] == seen:
                    condition.wait()

    def finish(current: dict) -> None:
        current["duration_seconds"] = round(time.monotonic() - started, 3)
        for task in current["tasks"]:
            if task["status"] == "running":
                task["error"] = "task failed"
                task["status"] = "failed"
        _skip_blocked(current["tasks"])
        if current.get("stop_reason") == "budget":
            for task in current["tasks"]:
                if task["status"] in {"pending", "running", "cancelled"}:
                    task["error"] = "budget exceeded"
                    task["status"] = "budget-exceeded"
            current["status"] = "budget-exceeded"
        else:
            for task in current["tasks"]:
                if task["status"] == "pending":
                    task["error"] = "dependencies were not accepted"
                    task["status"] = "skipped"
            current["status"] = _run_status(current)
        if not keep_worktrees and not any(_keeps_run_branch(task) for task in current["tasks"]):
            if checkout.delete_run_branch(current.get("run_branch")):
                current["run_branch"] = None
        current["cooldowns"] = {} if cooldowns is None else cooldowns.snapshot()
        current["report"] = write_reports(store.root, current)

    store.update(run_id, finish)
    return store.load(run_id)


def reopen_run(store: RunStore, run_id: str) -> dict:
    """Mark unfinished tasks pending so a later drive can continue the run."""

    def reopen(current: dict) -> None:
        current["cancel_requested"] = False
        current["status"] = "running"
        current["stop_reason"] = None
        for task in current["tasks"]:
            if task["status"] in _REOPEN:
                task["error"] = None
                task["merge_conflict"] = []
                task["merge_status"] = None
                task["status"] = "pending"

    store.update(run_id, reopen)
    return store.load(run_id)


def cancel_run(store: RunStore, run_id: str) -> dict:
    """Ask a live driver to stop, and cancel tasks that are not already done."""

    def cancel(current: dict) -> None:
        current["cancel_requested"] = True
        for task in current["tasks"]:
            if task["status"] in {"pending", "running"}:
                _cancel_task(current, task["index"])
        current["status"] = _run_status(current) if not current["cancel_requested"] else "cancelled"
        if all(task["status"] == "completed" for task in current["tasks"]):
            current["status"] = "completed"
        else:
            current["status"] = "cancelled"

    store.update(run_id, cancel)
    return store.load(run_id)


def _cancel_task(record: dict, index: int) -> None:
    task = record["tasks"][index]
    task["error"] = "run cancelled"
    task["status"] = "cancelled"


def _deps_met(task: dict, tasks: list[dict]) -> bool:
    by_id = {item["id"]: item for item in tasks}
    for dep_id in task["depends_on"]:
        dep = by_id.get(dep_id)
        if dep is None or dep["status"] != "completed" or dep.get("merge_status") not in {None, "landed"}:
            return False
    return True


def _skip_blocked(tasks: list[dict]) -> None:
    by_id = {task["id"]: task for task in tasks}
    changed = True
    while changed:
        changed = False
        for task in tasks:
            if task["status"] != "pending":
                continue
            for dep_id in task["depends_on"]:
                dep = by_id.get(dep_id)
                if dep is None:
                    task["error"] = f"dependency {dep_id} is missing"
                    task["status"] = "skipped"
                    changed = True
                    break
                if dep["status"] in _BLOCKED:
                    task["error"] = f"dependency {dep_id} is {dep['status']}"
                    task["status"] = "skipped"
                    changed = True
                    break


def _run_status(current: dict) -> str:
    statuses = {task["status"] for task in current["tasks"]}
    if statuses <= {"completed"}:
        return "completed"
    if "failed" in statuses:
        return "failed"
    if "review-rejected" in statuses:
        return "review-rejected"
    if "conflict" in statuses:
        return "conflict"
    if "unreviewed" in statuses:
        return "unreviewed"
    if current.get("cancel_requested") or "cancelled" in statuses:
        return "cancelled"
    if "budget-exceeded" in statuses:
        return "budget-exceeded"
    if statuses <= {"completed", "skipped"}:
        return "skipped" if "skipped" in statuses and "completed" not in statuses else "failed"
    return "failed"


def _keeps_run_branch(task: dict) -> bool:
    """A run branch stays when accepted, unreviewed, or conflicted work is on it."""

    if task["status"] in {"completed", "conflict", "unreviewed"}:
        return True
    if task.get("merge_status") == "landed":
        return True
    return bool(task.get("branch"))


def _land_message(task: dict) -> str:
    label = str(task.get("id") or task["index"])
    return f"recursion: land {label}"[:72]


def _conflict_error(paths: list[str]) -> str:
    if not paths:
        return "merge conflict"
    shown = ", ".join(paths[:10])
    return f"merge conflict: {shown}"

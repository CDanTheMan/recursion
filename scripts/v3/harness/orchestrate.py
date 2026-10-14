"""Plan one goal into M1A tasks and run them in dependency order."""

from __future__ import annotations

import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from scripts.v3.harness.context import recovery_prompt, task_prompt
from scripts.v3.harness.dag import line_nodes
from scripts.v3.harness.errors import HarnessError, RunCancelled
from scripts.v3.harness.isolation import NullIsolator
from scripts.v3.harness.log import BoundLog, NullLog, utc_now
from scripts.v3.harness.planning import plan_task
from scripts.v3.harness.report import write_reports
from scripts.v3.harness.review import execute_and_review
from scripts.v3.harness.state import RunStore
from scripts.v3.harness.usage import BudgetGuard, add_usage, empty_usage


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
                "recovery": None,
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
    conflict_retries: int = 1,
) -> dict:
    """Execute pending tasks whose dependencies have landed."""

    record = store.load(run_id)
    concurrency = record["concurrency"]
    if isinstance(concurrency, bool) or not isinstance(concurrency, int) or concurrency < 1:
        raise HarnessError("run concurrency must be an integer >= 1")
    if isinstance(conflict_retries, bool) or not isinstance(conflict_retries, int) or conflict_retries < 0:
        raise HarnessError("landing.conflict_retries must be an integer >= 0")
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
        current["conflict_retries"] = conflict_retries
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
        if _recovery_active(task):
            if store.load(run_id).get("cancel_requested"):
                def cancel_recovery(current: dict) -> None:
                    _cancel_task(current, index)
                    recovery = current["tasks"][index].get("recovery")
                    if isinstance(recovery, dict):
                        recovery["active"] = False
                    _skip_blocked(current["tasks"])

                store.update(run_id, cancel_recovery)
                sink.event("task.cancelled", index=index, run_id=run_id)
                return
            sink.event("task.started", index=index, packet_id=task["packet_id"], run_id=run_id)
            _recover_landing(
                store=store,
                run_id=run_id,
                index=index,
                checkout=checkout,
                sink=sink,
                limit=int(task["recovery"]["limit"]),
                paths=list(task["recovery"].get("paths") or []),
                source_branch=task["recovery"].get("branch") or task.get("branch"),
                source_commit=task.get("commit"),
                source_diff=task.get("diff") or "",
                outcome=None,
                allow_live=allow_live,
                retries=retries,
                backoff_seconds=backoff_seconds,
                timeout_seconds=timeout_seconds,
                max_rounds=max_rounds,
                route_id=route_id,
                open_adapter=open_adapter,
                sleep=pause,
                should_stop=stopped,
                accept_unreviewed=accept_unreviewed,
                cooldowns=cooldowns,
                cooldown_seconds=cooldown_seconds,
                now=now,
                guard=guard,
                begun=time.monotonic(),
            )
            return
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
        if disposition == "conflict" and conflict_retries > 0 and not tripped and not stopped():
            _recover_landing(
                store=store,
                run_id=run_id,
                index=index,
                checkout=checkout,
                sink=sink,
                limit=conflict_retries,
                paths=list(merge["paths"]),
                source_branch=iso.branch if iso is not None else None,
                source_commit=commit,
                source_diff=diff,
                outcome=outcome,
                allow_live=allow_live,
                retries=retries,
                backoff_seconds=backoff_seconds,
                timeout_seconds=timeout_seconds,
                max_rounds=max_rounds,
                route_id=route_id,
                open_adapter=open_adapter,
                sleep=pause,
                should_stop=stopped,
                accept_unreviewed=accept_unreviewed,
                cooldowns=cooldowns,
                cooldown_seconds=cooldown_seconds,
                now=now,
                guard=guard,
                begun=begun,
            )
            return
        if disposition == "conflict" and stopped():
            def cancel_during_merge(current: dict) -> None:
                item = current["tasks"][index]
                item["branch"] = iso.branch if iso is not None else None
                item["commit"] = commit
                item["diff"] = diff
                item["duration_seconds"] = round(time.monotonic() - begun, 3)
                item["merge_conflict"] = list(merge["paths"])
                item["merge_status"] = "conflict"
                _cancel_task(current, index)
                _skip_blocked(current["tasks"])

            store.update(run_id, cancel_during_merge)
            sink.event("task.cancelled", index=index, run_id=run_id)
            return
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
        except Exception:
            raise
        except BaseException:
            # A provider interrupt leaves the task running. finish() records it.
            pass
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
                if _recovery_active(task):
                    task["error"] = "recovery interrupted"
                else:
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
                if _recovery_active(task):
                    task["error"] = None
                    task["status"] = "pending"
                    continue
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


def _recovery_active(task: dict) -> bool:
    recovery = task.get("recovery")
    return isinstance(recovery, dict) and recovery.get("active") is True


def _recover_landing(
    *,
    store: RunStore,
    run_id: str,
    index: int,
    checkout,
    sink,
    limit: int,
    paths: list[str],
    source_branch: str | None,
    source_commit: str | None,
    source_diff: str,
    outcome: dict | None,
    allow_live: bool,
    retries: int,
    backoff_seconds: float,
    timeout_seconds: dict[str, int],
    max_rounds: int,
    route_id: str,
    open_adapter,
    sleep,
    should_stop,
    accept_unreviewed: bool,
    cooldowns,
    cooldown_seconds: float,
    now,
    guard: BudgetGuard,
    begun: float,
) -> None:
    """Reconcile one conflicted task on a fresh worktree cut from the run branch."""

    if outcome is not None:
        def begin(current: dict) -> None:
            item = current["tasks"][index]
            item["attempts"] = outcome["attempts"]
            item["branch"] = source_branch
            item["commit"] = source_commit
            item["diff"] = source_diff
            item["execution"] = outcome["result"].to_dict()
            item["merge_conflict"] = list(paths)
            item["merge_status"] = "conflict"
            item["provider"] = outcome["result"].provider
            item["reviews"] = outcome["reviews"]
            item["status"] = "running"
            item["text"] = outcome["result"].text
            item["usage"] = outcome["usage"]
            item["recovery"] = {
                "active": True,
                "attempts": [],
                "branch": source_branch,
                "limit": limit,
                "paths": list(paths),
            }

        store.update(run_id, begin)

    def load_task() -> dict:
        return store.load(run_id)["tasks"][index]

    task = load_task()
    recovery = task.get("recovery") if isinstance(task.get("recovery"), dict) else {}
    attempts = list(recovery.get("attempts") or [])
    stored_limit = recovery.get("limit")
    if isinstance(stored_limit, int) and not isinstance(stored_limit, bool):
        limit = stored_limit
    source_branch = recovery.get("branch") or source_branch
    conflict_paths = list(recovery.get("paths") or paths)

    def remember_attempts(latest_paths: list[str]) -> None:
        def save(current: dict) -> None:
            item = current["tasks"][index]
            item_recovery = item.get("recovery")
            if not isinstance(item_recovery, dict):
                return
            item_recovery["attempts"] = list(attempts)
            item_recovery["paths"] = list(latest_paths)
            item["merge_conflict"] = list(latest_paths)

        store.update(run_id, save)

    landed = None
    while len(attempts) < limit:
        if should_stop is not None and should_stop():
            _cancel_open_recovery(store, run_id, index, source_branch, begun)
            sink.event("task.cancelled", index=index, run_id=run_id)
            return
        if guard.tripped:
            break
        attempt_no = len(attempts) + 1
        sink.event(
            "task.conflict_recovery",
            attempt=attempt_no,
            index=index,
            paths=list(conflict_paths),
            run_id=run_id,
        )
        attempt = _one_recovery_attempt(
            store=store,
            run_id=run_id,
            index=index,
            attempt_no=attempt_no,
            checkout=checkout,
            sink=sink,
            paths=conflict_paths,
            allow_live=allow_live,
            retries=retries,
            backoff_seconds=backoff_seconds,
            timeout_seconds=timeout_seconds,
            max_rounds=max_rounds,
            route_id=route_id,
            open_adapter=open_adapter,
            sleep=sleep,
            should_stop=should_stop,
            accept_unreviewed=accept_unreviewed,
            cooldowns=cooldowns,
            cooldown_seconds=cooldown_seconds,
            now=now,
            guard=guard,
            begun=begun,
        )
        if attempt.get("status") == "cancelled":
            return
        attempts.append(attempt)
        if attempt.get("merge_conflict"):
            conflict_paths = list(attempt["merge_conflict"])
        remember_attempts(conflict_paths)
        sink.event(
            "task.conflict_recovery",
            attempt=attempt_no,
            index=index,
            provider=attempt.get("provider"),
            run_id=run_id,
            status=attempt.get("status"),
        )
        if attempt.get("status") == "completed" and attempt.get("merge_status") == "landed":
            landed = attempt
            break

    _close_recovery(
        store=store,
        run_id=run_id,
        index=index,
        checkout=checkout,
        sink=sink,
        attempts=attempts,
        landed=landed,
        paths=conflict_paths,
        source_branch=source_branch,
        begun=begun,
    )


def _one_recovery_attempt(
    *,
    store: RunStore,
    run_id: str,
    index: int,
    attempt_no: int,
    checkout,
    sink,
    paths: list[str],
    allow_live: bool,
    retries: int,
    backoff_seconds: float,
    timeout_seconds: dict[str, int],
    max_rounds: int,
    route_id: str,
    open_adapter,
    sleep,
    should_stop,
    accept_unreviewed: bool,
    cooldowns,
    cooldown_seconds: float,
    now,
    guard: BudgetGuard,
    begun: float,
) -> dict:
    task = store.load(run_id)["tasks"][index]
    iso = None
    keep_branch = False
    try:
        if not task["candidates"]:
            raise HarnessError("no provider has the required capabilities")
        start_ref = store.load(run_id).get("run_branch")
        iso = checkout.acquire_recovery(run_id, index, attempt_no, start_ref)
        prompt = recovery_prompt(task, store.load(run_id)["tasks"], paths)
        outcome = execute_and_review(
            task=prompt,
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
            sleep=sleep,
            should_stop=should_stop,
            accept_unreviewed=accept_unreviewed,
            seal=lambda: checkout.commit_pending(iso, _land_message(task)),
            snapshot=lambda: checkout.snapshot(iso),
            restore=lambda head: checkout.restore(iso, head),
            cooldowns=cooldowns,
            cooldown_seconds=cooldown_seconds,
            now=now,
        )
        guard.add(outcome["usage"])
        diff = checkout.diff(iso)
        commit = None
        if outcome["disposition"] == "completed":
            commit = checkout.commit_pending(iso, _land_message(task))
        merge = {"commit": None, "paths": [], "status": "not-landed"}
        status = outcome["disposition"]
        error = None
        if outcome["disposition"] == "completed" and commit is not None:
            try:
                merge = checkout.merge_into_run(store.load(run_id).get("run_branch"), iso.branch)
            except HarnessError:
                merge = {"commit": None, "paths": [], "status": "conflict"}
            if merge["status"] == "conflict":
                status = "conflict"
                error = _conflict_error(merge["paths"])
            else:
                status = "completed"
        elif outcome["disposition"] == "completed":
            status = "failed"
            error = "recovery produced no commit"
        elif outcome["disposition"] == "review-rejected":
            error = "review rejected"
        elif outcome["disposition"] == "unreviewed":
            error = "review did not complete"
        keep_branch = status in {"completed", "conflict"} and bool(iso.branch)
        return {
            "attempt": attempt_no,
            "branch": iso.branch,
            "commit": commit,
            "diff": diff,
            "error": error,
            "execution": outcome["result"].to_dict(),
            "merge_conflict": list(merge["paths"]),
            "merge_status": merge["status"] if status == "completed" else merge["status"],
            "provider": outcome["result"].provider,
            "reviews": outcome["reviews"],
            "status": status,
            "text": outcome["result"].text,
            "usage": outcome["usage"],
            "worker_attempts": outcome["attempts"],
        }
    except RunCancelled:
        if iso is not None:
            checkout.release(iso, keep_branch=False, keep_worktree=False)
            iso = None
        _cancel_open_recovery(store, run_id, index, task.get("branch"), begun)
        sink.event("task.cancelled", index=index, run_id=run_id)
        return {"attempt": attempt_no, "branch": None, "error": "run cancelled", "status": "cancelled"}
    except HarnessError as exc:
        return {
            "attempt": attempt_no,
            "branch": None if iso is None else iso.branch,
            "commit": None,
            "diff": "",
            "error": str(exc),
            "execution": None,
            "merge_conflict": [],
            "merge_status": "not-landed",
            "provider": None,
            "reviews": [],
            "status": "failed",
            "text": None,
            "usage": empty_usage(),
            "worker_attempts": list(getattr(exc, "attempts", []) or []),
        }
    finally:
        if iso is not None:
            checkout.release(iso, keep_branch=keep_branch, keep_worktree=False)


def _cancel_open_recovery(store: RunStore, run_id: str, index: int, branch: str | None, begun: float) -> None:
    def cancel(current: dict) -> None:
        item = current["tasks"][index]
        recovery = item.get("recovery")
        if isinstance(recovery, dict):
            recovery["active"] = False
        if branch:
            item["branch"] = branch
        item["duration_seconds"] = round(time.monotonic() - begun, 3)
        _cancel_task(current, index)
        _skip_blocked(current["tasks"])

    store.update(run_id, cancel)


def _close_recovery(
    *,
    store: RunStore,
    run_id: str,
    index: int,
    checkout,
    sink,
    attempts: list[dict],
    landed: dict | None,
    paths: list[str],
    source_branch: str | None,
    begun: float,
) -> None:
    if landed is not None:
        for previous in attempts:
            branch = previous.get("branch")
            if branch and branch != landed.get("branch"):
                checkout.delete_branch(branch)
        if source_branch and source_branch != landed.get("branch"):
            checkout.delete_branch(source_branch)

    def close(current: dict) -> None:
        item = current["tasks"][index]
        recovery = item.get("recovery")
        if not isinstance(recovery, dict):
            recovery = {"attempts": [], "branch": source_branch, "limit": 0, "paths": list(paths)}
            item["recovery"] = recovery
        recovery["active"] = False
        recovery["attempts"] = [
            {key: value for key, value in attempt.items() if key not in {"diff", "execution", "worker_attempts"}}
            for attempt in attempts
        ]
        previous = item.get("duration_seconds")
        extra = time.monotonic() - begun
        base = float(previous) if isinstance(previous, (int, float)) and not isinstance(previous, bool) else 0.0
        item["duration_seconds"] = round(base + extra, 3)
        if not isinstance(item.get("usage"), dict):
            item["usage"] = empty_usage()
        extra_attempts = []
        extra_reviews = []
        for attempt in attempts:
            add_usage(item["usage"], attempt.get("usage") or empty_usage())
            extra_attempts.extend(attempt.get("worker_attempts") or [])
            extra_reviews.extend(attempt.get("reviews") or [])
        item["attempts"] = list(item.get("attempts") or []) + extra_attempts
        item["reviews"] = list(item.get("reviews") or []) + extra_reviews
        if landed is not None:
            item["branch"] = landed.get("branch")
            item["commit"] = landed.get("commit")
            item["diff"] = landed.get("diff") or ""
            item["error"] = None
            item["execution"] = landed.get("execution")
            item["merge_conflict"] = []
            item["merge_status"] = "landed"
            item["provider"] = landed.get("provider")
            item["status"] = "completed"
            item["text"] = landed.get("text")
        else:
            item["branch"] = source_branch or item.get("branch")
            item["error"] = _conflict_error(paths)
            item["merge_conflict"] = list(paths)
            item["merge_status"] = "conflict"
            item["status"] = "conflict"
        _skip_blocked(current["tasks"])

    store.update(run_id, close)
    if landed is not None:
        sink.event(
            "task.conflict_recovered",
            attempt=landed.get("attempt"),
            index=index,
            provider=landed.get("provider"),
            run_id=run_id,
        )
        sink.event("task.completed", index=index, provider=landed.get("provider"), run_id=run_id)
        return
    sink.event("task.conflict", index=index, provider=store.load(run_id)["tasks"][index].get("provider"), run_id=run_id)


def _conflict_error(paths: list[str]) -> str:
    if not paths:
        return "merge conflict"
    shown = ", ".join(paths[:10])
    return f"merge conflict: {shown}"

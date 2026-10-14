"""Plan one goal into M1A tasks and run the independent ones in parallel."""

from __future__ import annotations

import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from scripts.v3.harness.errors import HarnessError, RunCancelled
from scripts.v3.harness.isolation import NullIsolator
from scripts.v3.harness.log import NullLog, utc_now
from scripts.v3.harness.planning import plan_task
from scripts.v3.harness.report import write_reports
from scripts.v3.harness.review import execute_and_review
from scripts.v3.harness.state import RunStore
from scripts.v3.harness.usage import BudgetGuard, empty_usage


def split_goal(goal: str) -> list[str]:
    """Return one task per non-empty line. Each line is admitted on its own."""

    if not isinstance(goal, str):
        raise HarnessError("goal text is empty")
    tasks = [line.strip() for line in goal.splitlines() if line.strip()]
    if not tasks:
        raise HarnessError("goal text is empty")
    return tasks


def plan_goal(goal: str) -> dict:
    """Admit each task through the M1A kernel. Projections stay separate."""

    planned = [plan_task(task) for task in split_goal(goal)]
    return {"goal": goal.strip(), "tasks": planned}


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
) -> dict:
    run_id = new_run_id()
    record = {
        "cancel_requested": False,
        "concurrency": concurrency,
        "created": utc_now(),
        "goal": goal,
        "route": route,
        "run_id": run_id,
        "status": "running",
        "stop_reason": None,
        "tasks": [
            {
                "attempts": [],
                "branch": None,
                "candidates": list(candidates[index]),
                "diff": "",
                "duration_seconds": None,
                "error": None,
                "execution": None,
                "index": index,
                "packet_id": item["packet_id"],
                "projection_digest": item["projection_digest"],
                "provider": None,
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
) -> dict:
    """Execute tasks that are not completed, honoring the stored concurrency limit."""

    record = store.load(run_id)
    concurrency = record["concurrency"]
    if isinstance(concurrency, bool) or not isinstance(concurrency, int) or concurrency < 1:
        raise HarnessError("run concurrency must be an integer >= 1")
    indexes = [task["index"] for task in record["tasks"] if task["status"] != "completed"]
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

    def stopped() -> bool:
        if guard.tripped:
            return True
        return store.load(run_id).get("cancel_requested") is True

    def work(index: int) -> None:
        def claim(current: dict) -> bool:
            if current.get("cancel_requested"):
                _cancel_task(current, index)
                return False
            task = current["tasks"][index]
            if task["status"] == "completed":
                return False
            task["status"] = "running"
            task["error"] = None
            return True

        if not store.update(run_id, claim):
            return
        task = store.load(run_id)["tasks"][index]
        sink.event("task.started", index=index, packet_id=task["packet_id"], run_id=run_id)
        iso = None
        begun = time.monotonic()
        try:
            iso = checkout.acquire(run_id, index)
            outcome = execute_and_review(
                task=task["task"],
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
                log=sink,
                open_adapter=open_adapter,
                sleep=pause,
                should_stop=stopped,
            )
            diff = checkout.diff(iso)
        except RunCancelled:
            def cancel(current: dict) -> None:
                _cancel_task(current, index)
                current["tasks"][index]["duration_seconds"] = round(time.monotonic() - begun, 3)

            store.update(run_id, cancel)
            sink.event("task.cancelled", index=index, run_id=run_id)
            return
        except HarnessError as exc:
            def fail(current: dict) -> None:
                item = current["tasks"][index]
                item["duration_seconds"] = round(time.monotonic() - begun, 3)
                item["error"] = str(exc)
                item["status"] = "failed"

            store.update(run_id, fail)
            sink.event("task.failed", error=type(exc).__name__, index=index, run_id=run_id)
            return
        finally:
            if iso is not None:
                checkout.release(iso)
        tripped = guard.add(outcome["usage"])
        if tripped:
            def mark_budget(current: dict) -> None:
                current["cancel_requested"] = True
                current["stop_reason"] = "budget"

            store.update(run_id, mark_budget)

        def succeed(current: dict) -> None:
            item = current["tasks"][index]
            item["attempts"] = outcome["attempts"]
            item["branch"] = iso.branch if iso is not None else None
            item["diff"] = diff
            item["duration_seconds"] = round(time.monotonic() - begun, 3)
            item["error"] = None if outcome["accepted"] else "review rejected"
            item["execution"] = outcome["result"].to_dict()
            item["provider"] = outcome["result"].provider
            item["reviews"] = outcome["reviews"]
            item["status"] = "completed" if outcome["accepted"] else "review-rejected"
            item["text"] = outcome["result"].text
            item["usage"] = outcome["usage"]

        store.update(run_id, succeed)
        sink.event(
            "task.completed" if outcome["accepted"] else "task.review_rejected",
            index=index,
            provider=outcome["result"].provider,
            run_id=run_id,
        )

    if indexes:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(work, indexes))

    def finish(current: dict) -> None:
        current["duration_seconds"] = round(time.monotonic() - started, 3)
        if current.get("stop_reason") == "budget":
            for task in current["tasks"]:
                if task["status"] in {"pending", "running", "cancelled"}:
                    task["error"] = "budget exceeded"
                    task["status"] = "budget-exceeded"
            current["status"] = "budget-exceeded"
        elif all(task["status"] == "completed" for task in current["tasks"]):
            current["status"] = "completed"
        elif current.get("cancel_requested"):
            for task in current["tasks"]:
                if task["status"] in {"pending", "running"}:
                    _cancel_task(current, task["index"])
            current["status"] = "cancelled"
        elif any(task["status"] == "failed" for task in current["tasks"]):
            current["status"] = "failed"
        elif any(task["status"] == "review-rejected" for task in current["tasks"]):
            current["status"] = "review-rejected"
        else:
            current["status"] = "failed"
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
            if task["status"] in {"failed", "cancelled", "running", "budget-exceeded", "review-rejected"}:
                task["error"] = None
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
        if any(task["status"] == "completed" for task in current["tasks"]) and any(
            task["status"] != "completed" for task in current["tasks"]
        ):
            current["status"] = "cancelled"
        elif all(task["status"] == "completed" for task in current["tasks"]):
            current["status"] = "completed"
        else:
            current["status"] = "cancelled"

    store.update(run_id, cancel)
    return store.load(run_id)


def _cancel_task(record: dict, index: int) -> None:
    task = record["tasks"][index]
    task["error"] = "run cancelled"
    task["status"] = "cancelled"

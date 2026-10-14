"""Plan one goal into M1A tasks and run the independent ones in parallel."""

from __future__ import annotations

import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from scripts.v3.harness.dispatch import execute_with_policy
from scripts.v3.harness.errors import HarnessError, RunCancelled
from scripts.v3.harness.log import NullLog, utc_now
from scripts.v3.harness.planning import plan_task
from scripts.v3.harness.providers import ProviderRequest, open_provider
from scripts.v3.harness.state import RunStore


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
        "tasks": [
            {
                "attempts": [],
                "candidates": list(candidates[index]),
                "error": None,
                "execution": None,
                "index": index,
                "packet_id": item["packet_id"],
                "projection_digest": item["projection_digest"],
                "provider": None,
                "status": "pending",
                "task": item["intent_text"],
                "text": None,
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
    open_adapter=open_provider,
    sleep=None,
) -> dict:
    """Execute tasks that are not completed, honoring the stored concurrency limit."""

    record = store.load(run_id)
    concurrency = record["concurrency"]
    if isinstance(concurrency, bool) or not isinstance(concurrency, int) or concurrency < 1:
        raise HarnessError("run concurrency must be an integer >= 1")
    indexes = [task["index"] for task in record["tasks"] if task["status"] != "completed"]
    sink = log if log is not None else NullLog()
    pause = time.sleep if sleep is None else sleep

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
        request = ProviderRequest(task=task["task"], packet_id=task["packet_id"], route_id=route_id)
        attempts: list[dict] = []
        try:
            result, attempts = execute_with_policy(
                request,
                list(task["candidates"]),
                allow_live=allow_live,
                retries=retries,
                log=sink,
                open_adapter=open_adapter,
                backoff_seconds=backoff_seconds,
                sleep=pause,
                should_stop=lambda: store.load(run_id).get("cancel_requested") is True,
                timeout_seconds=timeout_seconds,
            )
        except RunCancelled:
            def cancel(current: dict) -> None:
                _cancel_task(current, index)

            store.update(run_id, cancel)
            sink.event("task.cancelled", index=index, run_id=run_id)
            return
        except HarnessError as exc:
            def fail(current: dict) -> None:
                item = current["tasks"][index]
                item["attempts"] = attempts
                item["error"] = str(exc)
                item["status"] = "failed"

            store.update(run_id, fail)
            sink.event("task.failed", error=type(exc).__name__, index=index, run_id=run_id)
            return

        def succeed(current: dict) -> None:
            item = current["tasks"][index]
            item["attempts"] = attempts
            item["error"] = None
            item["execution"] = result.to_dict()
            item["provider"] = result.provider
            item["status"] = "completed"
            item["text"] = result.text

        store.update(run_id, succeed)
        sink.event("task.completed", index=index, provider=result.provider, run_id=run_id)

    if indexes:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(work, indexes))

    def finish(current: dict) -> None:
        if all(task["status"] == "completed" for task in current["tasks"]):
            current["status"] = "completed"
            return
        if current.get("cancel_requested"):
            for task in current["tasks"]:
                if task["status"] in {"pending", "running"}:
                    _cancel_task(current, task["index"])
            current["status"] = "cancelled"
            return
        current["status"] = "failed"

    store.update(run_id, finish)
    return store.load(run_id)


def reopen_run(store: RunStore, run_id: str) -> dict:
    """Mark unfinished tasks pending so a later drive can continue the run."""

    def reopen(current: dict) -> None:
        current["cancel_requested"] = False
        current["status"] = "running"
        for task in current["tasks"]:
            if task["status"] in {"failed", "cancelled", "running"}:
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

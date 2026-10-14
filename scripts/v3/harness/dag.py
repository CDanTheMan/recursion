"""Validate a provider task graph and fall back to one task per line."""

from __future__ import annotations

import json
import re

from scripts.v3.harness.dispatch import execute_with_policy
from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.providers import ProviderRequest


_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
_CAPABILITY = re.compile(r"^[a-z0-9][a-z0-9+-]{0,63}$")
_TASK_KEYS = {"depends_on", "description", "id", "required_capabilities"}


def plan_prompt(goal: str) -> str:
    example = (
        '{"tasks":[{"id":"build","description":"Build the note","required_capabilities":[],'
        '"depends_on":[]},{"id":"test","description":"Test the note","required_capabilities":[],'
        '"depends_on":["build"]}]}'
    )
    return "\n".join(
        (
            "Break the goal into tasks.",
            "Reply with one JSON object and no other text.",
            "Independent tasks use an empty depends_on list.",
            "A task that needs another task lists that task's id in depends_on.",
            'Keys are exactly {"tasks":[{"id","description","required_capabilities","depends_on"}]}.',
            "Example:",
            example,
            "Each id is unique. depends_on lists ids from this object. required_capabilities is a list of strings.",
            "Goal:",
            goal,
        )
    )


def line_nodes(lines: list[str]) -> list[dict]:
    return [
        {
            "depends_on": [],
            "description": line,
            "id": f"task-{index}",
            "required_capabilities": [],
        }
        for index, line in enumerate(lines, start=1)
    ]


def parse_plan(text: str) -> list[dict]:
    """Accept one exact JSON plan. The raw body is not copied into errors."""

    try:
        payload = json.loads(text.strip())
    except json.JSONDecodeError as exc:
        raise HarnessError("planner returned invalid JSON") from exc
    if not isinstance(payload, dict) or set(payload) != {"tasks"}:
        raise HarnessError("planner JSON keys are not exactly tasks")
    tasks = payload["tasks"]
    if not isinstance(tasks, list) or not tasks:
        raise HarnessError("planner tasks must be a non-empty list")
    nodes = [_task(item) for item in tasks]
    _graph(nodes)
    return nodes


def admit_goal(
    goal: str,
    *,
    candidates: list[str],
    allow_live: bool,
    retries: int,
    backoff_seconds: float,
    timeout_seconds: dict[str, int] | None,
    log: object,
    open_adapter,
    sleep=None,
    cooldowns=None,
    cooldown_seconds: float = 60,
    now=None,
) -> dict:
    """Ask a provider for a task graph. Invalid output falls back to lines."""

    from scripts.v3.harness.orchestrate import plan_goal
    from scripts.v3.harness.providers import open_provider

    if open_adapter is None:
        open_adapter = open_provider
    if not candidates:
        reason = "no planning provider"
        log.event("plan.fallback", reason=reason)
        return plan_goal(goal, source="lines", fallback=reason)
    request = ProviderRequest(task=plan_prompt(goal), packet_id="PLAN", route_id="plan", kind="plan")
    try:
        result, _attempts = execute_with_policy(
            request,
            candidates,
            allow_live=allow_live,
            retries=retries,
            log=log,
            open_adapter=open_adapter,
            backoff_seconds=backoff_seconds,
            sleep=sleep,
            timeout_seconds=timeout_seconds,
            cooldowns=cooldowns,
            cooldown_seconds=cooldown_seconds,
            now=now,
        )
        nodes = parse_plan(result.text)
        planned = plan_goal(goal, nodes=nodes, source="provider")
    except HarnessError as exc:
        reason = str(exc)
        log.event("plan.fallback", reason=reason)
        return plan_goal(goal, source="lines", fallback=reason)
    log.event("plan.ready", provider=result.provider, source="provider", tasks=len(nodes))
    return planned


def _task(item: object) -> dict:
    if not isinstance(item, dict) or set(item) != _TASK_KEYS:
        raise HarnessError("planner task keys are not exact")
    task_id = item["id"]
    if not isinstance(task_id, str) or _ID.fullmatch(task_id) is None:
        raise HarnessError("planner task id is invalid")
    description = item["description"]
    if not isinstance(description, str) or description.strip() == "" or "\x00" in description or len(description) > 4096:
        raise HarnessError("planner task description is invalid")
    capabilities = _strings(item["required_capabilities"], _CAPABILITY, "planner capability is invalid")
    depends = _strings(item["depends_on"], _ID, "planner dependency id is invalid")
    if task_id in depends:
        raise HarnessError("planner task depends on itself")
    return {
        "depends_on": depends,
        "description": description.strip(),
        "id": task_id,
        "required_capabilities": capabilities,
    }


def _strings(value: object, pattern: re.Pattern[str], message: str) -> list[str]:
    if not isinstance(value, list):
        raise HarnessError(message)
    found = []
    for item in value:
        if not isinstance(item, str) or pattern.fullmatch(item) is None:
            raise HarnessError(message)
        if item in found:
            raise HarnessError(message)
        found.append(item)
    return found


def _graph(nodes: list[dict]) -> None:
    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        raise HarnessError("planner task id is duplicated")
    known = set(ids)
    by_id = {node["id"]: node for node in nodes}
    for node in nodes:
        for dep in node["depends_on"]:
            if dep not in known:
                raise HarnessError("planner dependency is unknown")
    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(task_id: str) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            raise HarnessError("planner tasks have a cycle")
        visiting.add(task_id)
        for dep in by_id[task_id]["depends_on"]:
            walk(dep)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        walk(task_id)

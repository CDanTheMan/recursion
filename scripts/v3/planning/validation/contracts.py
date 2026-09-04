"""Cross-record and admission validation for the closed M1A planning contract."""

from __future__ import annotations

import copy

from scripts.v3.planning.validation.canonical import digest, seal


PARENT_MUTATIONS = {"accept-goal-spec", "amend-goal-spec", "propose-plan-revision", "propose-replan"}
PAUSE_SENSITIVE = {
    "propose-plan-revision", "propose-replan", "derive-work-packet", "submit-worker-result",
    "record-effect-observation",
}
COMMAND_ROLES = {
    "record-owner-intent": "owner", "accept-goal-spec": "owner", "amend-goal-spec": "owner",
    "record-owner-verifier-exception": "owner", "apply-pause": "owner",
    "start-arm-run": "head", "replace-work-lease": "head",
    "replace-executive-lease": "head", "replace-route": "head",
    "propose-plan-revision": "arm", "derive-work-packet": "arm", "reserve-budget": "arm",
    "propose-retry": "arm", "propose-replan": "arm", "raise-blocker": "arm",
    "raise-escalation": "arm", "submit-worker-result": "worker",
    "submit-gate-result": "verifier", "submit-plan-verifier-decision": "verifier",
    "record-capacity-observation": "kernel-fixture-gate", "record-checkpoint": "kernel-fixture-gate",
    "record-effect-observation": "kernel-fixture-gate",
}
BUDGET_FIELDS = (
    "attempts", "cpu_ms", "memory_bytes", "model_turns", "money_minor", "output_bytes", "tokens",
)


def _find_record(state: dict, ref: dict | None, object_type: str | None = None) -> dict | None:
    if ref is None:
        return None
    expected_id = ref.get("id", ref.get("lease_id"))
    for record in state["records"]:
        if object_type and record["object_type"] != object_type:
            continue
        if record["id"] != expected_id:
            continue
        if "version" in ref and record["version"] != ref["version"]:
            continue
        if "content_digest" not in ref or record["content_digest"] == ref["content_digest"]:
            return record
    return None


def _object_state(state: dict, record: dict) -> str | None:
    target = {
        "object_type": record["object_type"], "id": record["id"], "version": record["version"],
        "content_digest": record["content_digest"],
    }
    return next((item["state"] for item in state["object_states"] if item["object_ref"] == target), None)


def _policy(policy_fixtures: list[dict], ref: dict | None, kind: str | None = None) -> dict | None:
    if ref is None:
        return None
    return next((p for p in policy_fixtures
                 if p["policy_id"] == ref.get("policy_id")
                 and p["policy_version"] == ref.get("policy_version")
                 and p["content_digest"] == ref.get("content_digest")
                 and (kind is None or p["policy_kind"] == kind)), None)


def _candidate_plan(command: dict) -> tuple[dict, list[dict]] | tuple[None, list]:
    payload = command["payload"]
    if command["command_type"] == "propose-plan-revision":
        return payload["plan_revision"], payload["task_nodes"]
    if command["command_type"] == "propose-replan":
        return payload["new_plan_revision"], payload["task_nodes"]
    if command["command_type"] == "amend-goal-spec":
        return payload["replacement_plan_revision"], payload["task_nodes"]
    return None, []


def _witness(code: str, *, object_ids=(), edges=(), fields=()) -> dict:
    return seal({
        "witness_schema_version": "m1a-error-witness-1", "error_code": code,
        "object_ids": sorted(object_ids),
        "dependency_edges": sorted(copy.deepcopy(list(edges)),
                                   key=lambda e: (e["from_node_id"], e["to_node_id"])),
        "field_paths": sorted(fields),
    })


def _path_overlaps(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def validate_dag(plan: dict, tasks: list[dict]) -> tuple[str | None, dict | None]:
    """Validate exact graph membership, acyclicity, and unordered ownership conflicts."""

    node_ids = {task["id"] for task in tasks}
    expected_refs = sorted(
        [{"object_type": t["object_type"], "id": t["id"], "version": t["version"],
          "content_digest": t["content_digest"]} for t in tasks], key=lambda item: item["id"]
    )
    if plan["payload"]["task_node_refs"] != expected_refs:
        missing = sorted({r["id"] for r in plan["payload"]["task_node_refs"]} ^ node_ids)
        return "E-DAG-DEPENDENCY", _witness("E-DAG-DEPENDENCY", object_ids=missing)
    plan_ref = {"object_type": plan["object_type"], "id": plan["id"],
                "version": plan["version"]}
    for task in tasks:
        if task["payload"]["plan_ref"] != plan_ref:
            return "E-DAG-DEPENDENCY", _witness("E-DAG-DEPENDENCY", object_ids=[task["id"]])
    edges = plan["payload"]["dependency_edges"]
    missing = sorted({endpoint for edge in edges
                      for endpoint in (edge["from_node_id"], edge["to_node_id"])
                      if endpoint not in node_ids})
    for task in tasks:
        missing.extend(dep for dep in task["payload"]["dependency_node_ids"] if dep not in node_ids)
    if missing:
        return "E-DAG-DEPENDENCY", _witness("E-DAG-DEPENDENCY", object_ids=sorted(set(missing)))
    graph = {node: [] for node in node_ids}
    for edge in edges:
        graph[edge["from_node_id"]].append(edge["to_node_id"])
    visiting, visited = set(), set()
    cycle_nodes: set[str] = set()

    def visit(node: str, trail: list[str]) -> bool:
        if node in visiting:
            cycle_nodes.update(trail[trail.index(node):])
            return True
        if node in visited:
            return False
        visiting.add(node)
        for child in sorted(graph[node]):
            if visit(child, [*trail, child]):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    for node in sorted(node_ids):
        if visit(node, [node]):
            return "E-DAG-CYCLE", _witness("E-DAG-CYCLE", object_ids=cycle_nodes, edges=edges)

    reach = {(a, b) for a in node_ids for b in graph[a]}
    for pivot in node_ids:
        for left in node_ids:
            for right in node_ids:
                if (left, pivot) in reach and (pivot, right) in reach:
                    reach.add((left, right))
    ordered = lambda a, b: (a, b) in reach or (b, a) in reach
    for index, left in enumerate(sorted(tasks, key=lambda t: t["id"])):
        for right in sorted(tasks, key=lambda t: t["id"])[index + 1:]:
            if ordered(left["id"], right["id"]):
                continue
            lp, rp = left["payload"], right["payload"]
            conflict = None
            if any(_path_overlaps(a, b) for a in lp["write_resource_paths"] for b in rp["write_resource_paths"]):
                conflict = "write-write"
            elif (any(_path_overlaps(a, b) for a in lp["read_resource_paths"] for b in rp["write_resource_paths"])
                  or any(_path_overlaps(a, b) for a in lp["write_resource_paths"] for b in rp["read_resource_paths"])):
                conflict = "read-write"
            elif set(lp["effect_keys"]) & set(rp["effect_keys"]):
                conflict = "same-effect"
            if conflict:
                return "E-DAG-CONFLICT", _witness(
                    "E-DAG-CONFLICT", object_ids=[left["id"], right["id"]], fields=[conflict]
                )
    return None, None


def _validate_scope(goal: dict, plan: dict, tasks: list[dict]) -> str | None:
    gp = goal["payload"]
    candidates = [plan["payload"], *(task["payload"] for task in tasks)]
    for candidate in candidates:
        limits = candidate.get("budget_limits", gp["budget_limits"])
        if any(limits[field] > gp["budget_limits"][field] for field in BUDGET_FIELDS):
            return "E-BUDGET-WIDEN"
    for item in candidates:
        subset_pairs = (
            ("authority_ids", "authority_ids"), ("capability_ids", "capability_ids"),
            ("allowed_action_ids", "allowed_action_ids"), ("route_ids", "allowed_route_ids"),
            ("account_class_ids", "allowed_account_class_ids"),
            ("capacity_pool_ids", "allowed_capacity_pool_ids"),
            ("effect_keys", "allowed_effect_keys"),
        )
        for child, parent in subset_pairs:
            if child in item and not set(item[child]).issubset(gp[parent]):
                return "E-SCOPE-WIDEN"
        for field in ("read_resource_paths", "write_resource_paths"):
            if field in item and any(not any(_path_overlaps(path, root) and
                                             (path == root or path.startswith(root + "/"))
                                             for root in gp["allowed_resource_paths"])
                                      for path in item[field]):
                return "E-SCOPE-WIDEN"
        if item.get("privacy_class_id") not in (None, gp["privacy_class_id"]):
            return "E-SCOPE-WIDEN"
        if item.get("egress_class_id") not in (None, gp["egress_class_id"]):
            return "E-SCOPE-WIDEN"
    return None


def _required_amendment_targets(state: dict) -> set[tuple[str, str, int]]:
    active_types = {"plan-revision", "task-node", "work-packet", "work-lease", "executive-lease", "effect-observation"}
    terminal = {"complete", "terminal-verified", "terminal-verified-downgraded"}
    targets = set()
    for item in state["object_states"]:
        ref = item["object_ref"]
        if ref["object_type"] in active_types and item["state"] not in terminal:
            targets.add((ref["object_type"], ref["id"], ref["version"]))
    return targets


def _validate_verifier(state: dict, command: dict) -> str | None:
    decision = command["payload"]
    plan = _find_record(state, decision["payload"]["plan_ref"], "plan-revision")
    if plan is None:
        return "E-STALE-PLAN"
    task_refs = plan["payload"]["task_node_refs"]
    passing = [r for r in state["records"] if r["object_type"] == "gate-result"
               and r["payload"]["plan_ref"] == decision["payload"]["plan_ref"]
               and r["payload"]["disposition"] == "pass"]
    passed_tasks = {r["payload"]["task_ref"]["id"] for r in passing}
    if any(ref["id"] not in passed_tasks for ref in task_refs):
        return "E-GATE-MISSING"
    assigned = plan["payload"]["assigned_plan_verifier_actor_id"]
    if assigned != command["actor_id"]:
        return "E-VERIFIER-MISSING"
    return None


def validate_admission(state: dict, command: dict, authority_fixtures: list[dict],
                       policy_fixtures: list[dict]) -> tuple[str | None, dict | None]:
    """Return the single deterministic primary error and optional canonical witness."""

    if digest(command, omit_content_digest=True) != command.get("content_digest"):
        return "E-DIGEST-MISMATCH", None
    if digest(command["payload"]) != command.get("payload_digest"):
        return "E-DIGEST-MISMATCH", None
    if command["candidate_digest"] != command["payload_digest"]:
        return "E-DIGEST-MISMATCH", None
    authority = next((a for a in authority_fixtures
                      if a["attestation_id"] == command["auth_ref"]), None)
    if authority is None:
        return "E-AUTH-MISSING", None
    if (digest(authority, omit_content_digest=True) != authority["content_digest"]
            or authority["candidate_digest"] != command["candidate_digest"]):
        return "E-AUTH-MISSING", None
    if (authority["actor_id"] != command["actor_id"]
            or command["command_type"] not in authority["allowed_command_types"]
            or not authority["valid_from_logical_time"] <= command["logical_time"] <= authority["expires_logical_time"]):
        return "E-AUTH-ROLE", None
    role = authority["actor_role"]
    if command["command_type"] in PARENT_MUTATIONS and role in ("worker", "verifier"):
        return "E-AUTH-PARENT-MUTATION", None
    if COMMAND_ROLES.get(command["command_type"]) != role:
        return "E-AUTH-ROLE", None
    if command["expected_state_version"] != state["state_version"]:
        return "E-DIGEST-MISMATCH", None

    if command["goal_ref"] is not None and command["goal_ref"] != state["operative_goal_ref"]:
        return "E-STALE-GOAL", None
    if command["plan_ref"] is not None and command["plan_ref"] != state["active_plan_ref"]:
        return "E-STALE-PLAN", None
    if command["lease_ref"] is not None:
        lease = _find_record(state, command["lease_ref"])
        if lease is None or _object_state(state, lease) != "active":
            return "E-STALE-LEASE", None

    if state["current_pause_epoch"] > 0 and command["command_type"] in PAUSE_SENSITIVE:
        pause_policy = _policy(policy_fixtures, state["current_pause_policy_ref"], "pause")
        if pause_policy is None or pause_policy["operative_pause_mode"] == "current-immediate":
            return "E-PAUSED", None
    if command["command_type"] == "apply-pause":
        directive = command["payload"]["payload"]
        pause_policy = _policy(policy_fixtures, directive["pause_policy_ref"], "pause")
        if pause_policy is None or directive["mode"] != pause_policy["operative_pause_mode"]:
            return "E-POLICY-UNKNOWN", None

    plan, tasks = _candidate_plan(command)
    if plan is not None:
        goal_ref = command["goal_ref"] or plan["payload"]["goal_ref"]
        goal = _find_record(state, goal_ref, "goal-spec")
        if goal is not None:
            error = _validate_scope(goal, plan, tasks)
            if error:
                return error, None
        error, witness = validate_dag(plan, tasks)
        if error:
            return error, witness

    if command["command_type"] == "propose-retry":
        retry = command["payload"]["payload"]
        prior_packet = _find_record(state, retry["prior_work_packet_ref"], "work-packet")
        if (retry["next_attempt"] > retry["retry_maximum"] and prior_packet is not None
                and _object_state(state, prior_packet) == "failed"):
            return "E-RETRY-EXHAUSTED", None
        if retry["novelty_delta_digest"] in state["consumed_novelty_delta_digests"]:
            return "E-RETRY-NONNOVEL", None
        if retry["next_attempt"] > retry["retry_maximum"]:
            return "E-RETRY-EXHAUSTED", None
        if state["ambiguous_effect_refs"]:
            return "E-EFFECT-AMBIGUOUS", None
    if command["command_type"] == "replace-route":
        route = command["payload"]["new_route"]["payload"]
        goal = _find_record(state, command["goal_ref"], "goal-spec")
        if (route["metered_spend_allowed"] or goal is None
                or route["route_id"] not in goal["payload"]["allowed_route_ids"]):
            return "E-ROUTE-SPEND", None
    if command["command_type"] == "submit-plan-verifier-decision":
        error = _validate_verifier(state, command)
        if error:
            return error, None
    if command["command_type"] == "amend-goal-spec":
        dispositions = command["payload"]["replacement_plan_revision"]["payload"]["dispositions"]
        covered = {(d["object_ref"]["object_type"], d["object_ref"]["id"], d["object_ref"]["version"])
                   for d in dispositions}
        if not _required_amendment_targets(state).issubset(covered):
            return "E-AMENDMENT-INCOMPLETE", None
    return None, None

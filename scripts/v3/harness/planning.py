"""Admit one task through the M1A planning kernel.

A run is one fresh stream and one task. Record ids match the closed single-task
vocabulary the kernel already accepts. Task bytes are bound into the owner
intent, the goal outcome, and the task semantic digest, so a different task
produces a different projection.
"""

from __future__ import annotations

import copy

from scripts.v3.harness.errors import HarnessError
from scripts.v3.planning.replay.kernel import (
    admit,
    derive_work_packet,
    genesis,
    lease_ref,
    object_ref,
)
from scripts.v3.planning.validation.canonical import (
    COMMAND_TYPES,
    digest,
    seal,
    validate_projection,
)


ACTORS = {
    "owner": "OWNER-LUCAS",
    "head": "HEAD-HERMES",
    "arm": "ARM-M1A",
    "worker": "WORKER-LUNA",
    "verifier": "VERIFIER-TERRA",
    "kernel-fixture-gate": "KERNEL-FIXTURE",
}
CORRELATION = "CORR-M1A"
STREAM_ID = "STREAM-HARNESS"
TEXT_BOUND = 4096

PLAN_COMMANDS = (
    "record-owner-intent",
    "accept-goal-spec",
    "start-arm-run",
    "propose-plan-revision",
    "record-capacity-observation",
    "reserve-budget",
    "derive-work-packet",
)


def check_task(task: str) -> str:
    """Return ``task`` when it fits the M1A text bound."""

    if not isinstance(task, str) or not task.strip():
        raise HarnessError("task text is empty")
    if "\x00" in task:
        raise HarnessError("task text contains a NUL")
    try:
        encoded = task.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise HarnessError("task text is not UTF-8") from exc
    if len(task) > TEXT_BOUND or len(encoded) > TEXT_BOUND:
        raise HarnessError("task text exceeds the M1A text bound")
    return task


def limit_budget() -> dict:
    return {
        "model_turns": 4,
        "attempts": 2,
        "tokens": 1000,
        "money_minor": 0,
        "cpu_ms": 10000,
        "memory_bytes": 1048576,
        "output_bytes": 65536,
    }


def zero_budget() -> dict:
    return {key: 0 for key in limit_budget()}


def policy_ref(policy: dict) -> dict:
    return {
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "content_digest": policy["content_digest"],
    }


def make_policies() -> list[dict]:
    """Closed policy envelope used by the M1A fixture corpus."""

    empty = {
        "allowed_roles": [],
        "allowed_command_types": [],
        "privacy_class_ids": [],
        "privacy_at_most_edges": [],
        "egress_class_ids": [],
        "egress_at_most_edges": [],
        "route_ids": [],
        "account_class_ids": [],
        "capacity_pool_ids": [],
        "allowed_spend_classes": [],
        "accepted_evidence_types": [],
        "failure_capability_requirements": [],
        "required_verifier_dimensions": [],
        "owner_verifier_exception_allowed": False,
        "operative_pause_mode": "current-immediate",
        "representable_future_pause_modes": [],
        "retry_maximum": 0,
    }

    def policy(policy_id: str, kind: str, **updates) -> dict:
        values = copy.deepcopy(empty)
        values.update(updates)
        return seal(
            {
                "policy_schema_version": "m1a-policy-fixture-1",
                "policy_id": policy_id,
                "policy_version": 1,
                "policy_kind": kind,
                **values,
            }
        )

    policies = [
        policy(
            "POLICY-AUTHORITY",
            "authority",
            allowed_roles=["arm", "head", "kernel-fixture-gate", "owner", "verifier", "worker"],
            allowed_command_types=sorted(COMMAND_TYPES),
        ),
        policy("POLICY-CONSTITUTION", "constitution", owner_verifier_exception_allowed=True),
        policy(
            "POLICY-NOVELTY",
            "novelty",
            route_ids=["ROUTE-INCLUDED", "ROUTE-ZERO"],
            account_class_ids=["ACCOUNT-INCLUDED"],
            capacity_pool_ids=["CAPACITY-INCLUDED"],
            allowed_spend_classes=["included", "none"],
            accepted_evidence_types=[
                {"failure_id": "FAIL-GATE", "evidence_types": ["fixture-observation", "gate-output"]}
            ],
            failure_capability_requirements=[
                {"failure_id": "FAIL-GATE", "capability_ids": ["CAPABILITY-REPAIR"]}
            ],
        ),
        policy(
            "POLICY-PAUSE",
            "pause",
            representable_future_pause_modes=["checkpoint", "drain", "interrupt"],
        ),
        policy(
            "POLICY-PRIVACY",
            "privacy-egress",
            privacy_class_ids=["PRIVACY-PUBLIC", "PRIVACY-SYNTHETIC"],
            privacy_at_most_edges=[
                {"less_or_equal_id": "PRIVACY-PUBLIC", "greater_or_equal_id": "PRIVACY-SYNTHETIC"}
            ],
            egress_class_ids=["EGRESS-NONE", "EGRESS-SYNTHETIC"],
            egress_at_most_edges=[
                {"less_or_equal_id": "EGRESS-NONE", "greater_or_equal_id": "EGRESS-SYNTHETIC"}
            ],
        ),
        policy("POLICY-RETRY", "retry", retry_maximum=2),
        policy(
            "POLICY-ROUTE",
            "route-envelope",
            route_ids=["ROUTE-INCLUDED", "ROUTE-ZERO"],
            account_class_ids=["ACCOUNT-INCLUDED"],
            capacity_pool_ids=["CAPACITY-INCLUDED"],
            allowed_spend_classes=["included", "none"],
        ),
        policy(
            "POLICY-VERIFIER",
            "verifier",
            required_verifier_dimensions=["actor", "evidence-store", "host", "model-family", "provider"],
            owner_verifier_exception_allowed=True,
        ),
    ]
    return sorted(policies, key=lambda item: (item["policy_id"], item["policy_version"]))


def domain_record(
    object_type: str,
    schema_version: str,
    record_id: str,
    payload: dict,
    command_id: str,
    actor_id: str,
    logical_time: int,
    *,
    under_lease: dict | None = None,
) -> dict:
    return seal(
        {
            "object_type": object_type,
            "schema_version": schema_version,
            "id": record_id,
            "version": 1,
            "created_by_actor_id": actor_id,
            "created_under_lease": under_lease,
            "causation_id": command_id,
            "correlation_id": CORRELATION,
            "created_logical_time": logical_time,
            "payload": payload,
        }
    )


def gate_requirement() -> dict:
    return {
        "gate_id": "GATE-M1A",
        "procedure_digest": digest("gate-procedure"),
        "evidence_schema_digest": digest("gate-evidence-schema"),
        "candidate_binding_digest": digest("candidate-binding"),
        "verifier_policy_digest": digest("verifier-policy"),
        "assigned_verifier_actor_id": ACTORS["verifier"],
    }


class PlanningSession:
    """Drive ``admit`` until one work packet exists."""

    def __init__(self) -> None:
        self.policies = make_policies()
        self.by_kind = {item["policy_kind"]: item for item in self.policies}
        pause = policy_ref(self.by_kind["pause"])
        self.state = genesis(
            {
                "genesis_schema_version": "m1a-genesis-1",
                "stream_id": STREAM_ID,
                "current_pause_policy_ref": pause,
                "current_pause_epoch": 0,
            }
        )
        self.journal: list[dict] = []
        self.authorities: list[dict] = []
        self.receipts: list[dict] = []
        self.ordinal = 0
        self.world: dict[str, dict] = {}

    def pref(self, kind: str) -> dict:
        return policy_ref(self.by_kind[kind])

    def _begin(self) -> tuple[str, int]:
        self.ordinal += 1
        return f"CMD-HARNESS-{self.ordinal:02d}", self.state["last_event_sequence"] + 1

    def _accept(
        self,
        command_type: str,
        role: str,
        payload: dict,
        *,
        lease: dict | None = None,
        goal: dict | None = None,
        plan: dict | None = None,
    ) -> None:
        command_id = f"CMD-HARNESS-{self.ordinal:02d}"
        payload_digest = digest(payload)
        suffix = command_id[4:]
        authority = seal(
            {
                "attestation_schema_version": "m1a-fixture-authority-1",
                "attestation_id": f"AUTH-{suffix}",
                "actor_id": ACTORS[role],
                "actor_role": role,
                "allowed_command_types": [command_type],
                "candidate_digest": payload_digest,
                "authority_policy_ref": self.pref("authority"),
                "constitution_policy_ref": self.pref("constitution"),
                "valid_from_logical_time": 0,
                "expires_logical_time": 10000,
            }
        )
        self.authorities.append(authority)
        command = seal(
            {
                "command_schema_version": "m1a-command-1",
                "command_id": command_id,
                "command_type": command_type,
                "actor_id": ACTORS[role],
                "auth_ref": authority["attestation_id"],
                "lease_ref": lease,
                "logical_time": self.state["last_event_sequence"] + 1,
                "expected_state_version": self.state["state_version"],
                "expected_state_digest": self.state["content_digest"],
                "goal_ref": goal,
                "plan_ref": plan,
                "payload": payload,
                "payload_digest": payload_digest,
                "candidate_digest": payload_digest,
            }
        )
        self.state, _events, receipt, self.journal = admit(
            self.state,
            self.state["content_digest"],
            command,
            self.authorities,
            self.policies,
            self.journal,
        )
        self.receipts.append(receipt)
        if receipt["disposition"] != "accepted":
            raise HarnessError(f"{command_type} refused: {receipt['primary_error']}")

    def plan(self, task: str) -> dict:
        task = check_task(task)
        bound = digest(task)
        budget = limit_budget()

        command_id, logical = self._begin()
        intent = domain_record(
            "owner-intent",
            "m1a-owner-intent-1",
            "INTENT-M1A",
            {
                "intent_text": task,
                "source_kind": "owner-prompt",
                "source_digest": bound,
                "privacy_policy_ref": self.pref("privacy-egress"),
                "supersedes_ref": None,
            },
            command_id,
            ACTORS["owner"],
            logical,
        )
        self.world["intent"] = intent
        self._accept("record-owner-intent", "owner", intent)

        command_id, logical = self._begin()
        goal = domain_record(
            "goal-spec",
            "m1a-goal-spec-1",
            "GOAL-M1A",
            {
                "owner_intent_ref": object_ref(intent),
                "outcome": task,
                "acceptance_gate_ids": ["GATE-M1A"],
                "allowed_resource_paths": ["workspace/input", "workspace/output"],
                "non_goals": ["no external effects", "no publication"],
                "authority_ids": ["AUTHORITY-M1A"],
                "capability_ids": ["CAPABILITY-BASE", "CAPABILITY-REPAIR"],
                "allowed_action_ids": ["ACTION-READ", "ACTION-WRITE"],
                "prohibition_ids": ["PROHIBIT-EGRESS"],
                "authority_policy_ref": self.pref("authority"),
                "privacy_class_id": "PRIVACY-SYNTHETIC",
                "egress_class_id": "EGRESS-NONE",
                "privacy_policy_ref": self.pref("privacy-egress"),
                "egress_policy_ref": self.pref("privacy-egress"),
                "route_policy_ref": self.pref("route-envelope"),
                "allowed_route_ids": ["ROUTE-INCLUDED", "ROUTE-ZERO"],
                "allowed_account_class_ids": ["ACCOUNT-INCLUDED"],
                "allowed_capacity_pool_ids": ["CAPACITY-INCLUDED"],
                "budget_limits": budget,
                "source_digests": [bound],
                "novelty_policy_ref": self.pref("novelty"),
                "retry_policy_ref": self.pref("retry"),
                "verifier_policy_ref": self.pref("verifier"),
                "constitution_policy_ref": self.pref("constitution"),
                "pause_policy_ref": self.pref("pause"),
                "allowed_effect_keys": ["EFFECT-SYNTHETIC"],
                "publication_allowed": False,
                "terminal_owner_seam_ids": ["SEAM-OWNER"],
                "fence_epoch": 1,
                "state": "accepted",
            },
            command_id,
            ACTORS["owner"],
            logical,
        )
        self.world["goal"] = goal
        self._accept("accept-goal-spec", "owner", goal)

        command_id, logical = self._begin()
        executive = domain_record(
            "executive-lease",
            "m1a-executive-lease-1",
            "LEASE-EXEC-1",
            {
                "subject_actor_id": ACTORS["arm"],
                "goal_ref": object_ref(goal),
                "plan_ref": None,
                "task_ref": None,
                "supersedes_lease_ref": None,
                "lease_epoch": 1,
                "nonce_digest": digest("executive-lease-one"),
                "issued_logical_time": logical,
                "expires_logical_time": 1000,
                "allowed_command_types": sorted(
                    [
                        "derive-work-packet",
                        "propose-plan-revision",
                        "propose-replan",
                        "propose-retry",
                        "reserve-budget",
                    ]
                ),
                "state": "active",
            },
            command_id,
            "KERNEL-M1A",
            logical,
        )
        arm = domain_record(
            "arm-run",
            "m1a-arm-run-1",
            "ARM-RUN-M1A",
            {
                "goal_ref": object_ref(goal),
                "logical_actor_id": ACTORS["arm"],
                "eligible_route_ids": ["ROUTE-INCLUDED", "ROUTE-ZERO"],
                "eligible_account_class_ids": ["ACCOUNT-INCLUDED"],
                "eligible_capacity_pool_ids": ["CAPACITY-INCLUDED"],
                "budget_limits": budget,
                "source_digests": [bound],
                "executive_lease_ref": lease_ref(executive),
                "verifier_policy_ref": self.pref("verifier"),
            },
            command_id,
            ACTORS["head"],
            logical,
        )
        self.world["executive"] = executive
        self.world["arm"] = arm
        self._accept(
            "start-arm-run",
            "head",
            {"executive_lease": executive, "arm_run": arm},
            goal=object_ref(goal),
        )

        command_id, logical = self._begin()
        executive_lease = lease_ref(executive)
        task_node = domain_record(
            "task-node",
            "m1a-task-node-1",
            "TASK-M1A-A",
            {
                "plan_ref": {"object_type": "plan-revision", "id": "PLAN-M1A", "version": 1},
                "semantic_definition_digest": bound,
                "output_schema_digest": digest("task-output-schema"),
                "dependency_node_ids": [],
                "input_digests": [bound],
                "source_digests": [bound],
                "read_resource_paths": ["workspace/input"],
                "write_resource_paths": ["workspace/output"],
                "effect_keys": ["EFFECT-SYNTHETIC"],
                "authority_ids": ["AUTHORITY-M1A"],
                "capability_ids": ["CAPABILITY-BASE"],
                "allowed_action_ids": ["ACTION-READ", "ACTION-WRITE"],
                "prohibition_ids": ["PROHIBIT-EGRESS"],
                "route_ids": ["ROUTE-INCLUDED", "ROUTE-ZERO"],
                "route_capability_ids": ["CAPABILITY-BASE"],
                "account_class_ids": ["ACCOUNT-INCLUDED"],
                "capacity_pool_ids": ["CAPACITY-INCLUDED"],
                "authority_policy_ref": self.pref("authority"),
                "privacy_class_id": "PRIVACY-SYNTHETIC",
                "egress_class_id": "EGRESS-NONE",
                "privacy_policy_ref": self.pref("privacy-egress"),
                "egress_policy_ref": self.pref("privacy-egress"),
                "budget_limits": budget,
                "gate_requirements": [gate_requirement()],
                "retry_policy_ref": self.pref("retry"),
                "verifier_policy_ref": self.pref("verifier"),
                "constitution_policy_ref": self.pref("constitution"),
                "terminal_contribution_digest": digest("terminal-contribution"),
                "retry_maximum": 2,
            },
            command_id,
            ACTORS["arm"],
            logical,
            under_lease=executive_lease,
        )
        task_refs = [object_ref(task_node)]
        edges: list[dict] = []
        plan = domain_record(
            "plan-revision",
            "m1a-plan-revision-1",
            "PLAN-M1A",
            {
                "goal_ref": object_ref(goal),
                "arm_run_ref": object_ref(arm),
                "prior_plan_ref": None,
                "trigger": "initial",
                "task_node_refs": task_refs,
                "dependency_edges": edges,
                "graph_digest": digest({"task_node_refs": task_refs, "dependency_edges": edges}),
                "acceptance_gate_ids": ["GATE-M1A"],
                "budget_limits": budget,
                "read_resource_paths": ["workspace/input"],
                "write_resource_paths": ["workspace/output"],
                "effect_keys": ["EFFECT-SYNTHETIC"],
                "source_digests": [bound],
                "verifier_policy_ref": self.pref("verifier"),
                "constitution_policy_ref": self.pref("constitution"),
                "assigned_plan_verifier_actor_id": ACTORS["verifier"],
                "change_rationale_digest": bound,
                "dispositions": [],
            },
            command_id,
            ACTORS["arm"],
            logical,
            under_lease=executive_lease,
        )
        transition = domain_record(
            "plan-transition",
            "m1a-plan-transition-1",
            "TRANSITION-M1A-1",
            {
                "from_plan_ref": None,
                "to_plan_ref": object_ref(plan),
                "trigger_evidence_digests": [bound],
                "dispositions": [],
                "executive_lease_ref": executive_lease,
                "expected_goal_fence_epoch": 1,
                "checkpoint_ref": None,
            },
            command_id,
            ACTORS["arm"],
            logical,
            under_lease=executive_lease,
        )
        self.world["task"] = task_node
        self.world["plan"] = plan
        self._accept(
            "propose-plan-revision",
            "arm",
            {
                "plan_revision": plan,
                "plan_transition": transition,
                "task_nodes": [task_node],
            },
            lease=executive_lease,
            goal=object_ref(goal),
        )

        command_id, logical = self._begin()
        capacity = domain_record(
            "capacity-observation",
            "m1a-capacity-observation-1",
            "CAPACITY-OBS-1",
            {
                "route_id": "ROUTE-INCLUDED",
                "account_class_id": "ACCOUNT-INCLUDED",
                "capacity_pool_id": "CAPACITY-INCLUDED",
                "spend_class": "included",
                "available": True,
                "remaining_units": 100,
                "observation_digest": digest("capacity-available"),
            },
            command_id,
            ACTORS["kernel-fixture-gate"],
            logical,
        )
        self.world["capacity"] = capacity
        self._accept(
            "record-capacity-observation",
            "kernel-fixture-gate",
            capacity,
            goal=object_ref(goal),
            plan=object_ref(plan),
        )

        command_id, logical = self._begin()
        reservation = domain_record(
            "budget-reservation",
            "m1a-budget-reservation-1",
            "BUDGET-RESERVATION-1",
            {
                "goal_ref": object_ref(goal),
                "plan_ref": object_ref(plan),
                "task_ref": object_ref(task_node),
                "limits": budget,
                "consumed": zero_budget(),
                "remaining": budget,
                "state": "reserved",
            },
            command_id,
            ACTORS["arm"],
            logical,
            under_lease=executive_lease,
        )
        self.world["budget"] = reservation
        self._accept(
            "reserve-budget",
            "arm",
            reservation,
            lease=executive_lease,
            goal=object_ref(goal),
            plan=object_ref(plan),
        )

        command_id, logical = self._begin()
        work_lease = domain_record(
            "work-lease",
            "m1a-work-lease-1",
            "LEASE-WORK-1",
            {
                "subject_actor_id": ACTORS["worker"],
                "goal_ref": object_ref(goal),
                "plan_ref": object_ref(plan),
                "task_ref": object_ref(task_node),
                "supersedes_lease_ref": None,
                "lease_epoch": 1,
                "nonce_digest": digest("work-lease-one"),
                "issued_logical_time": logical,
                "expires_logical_time": 900,
                "allowed_command_types": ["submit-worker-result"],
                "state": "active",
            },
            command_id,
            "KERNEL-M1A",
            logical,
            under_lease=executive_lease,
        )
        route = domain_record(
            "route-assignment",
            "m1a-route-assignment-1",
            "ROUTE-ASSIGNMENT-1",
            {
                "logical_actor_id": ACTORS["worker"],
                "route_id": "ROUTE-INCLUDED",
                "route_capability_ids": ["CAPABILITY-BASE"],
                "account_class_id": "ACCOUNT-INCLUDED",
                "capacity_pool_id": "CAPACITY-INCLUDED",
                "privacy_policy_ref": self.pref("privacy-egress"),
                "egress_policy_ref": self.pref("privacy-egress"),
                "route_policy_ref": self.pref("route-envelope"),
                "metered_spend_allowed": False,
                "capacity_observation_ref": object_ref(capacity),
                "supersedes_route_ref": None,
                "assigned_logical_time": logical,
                "expires_logical_time": 900,
                "state": "assigned",
            },
            command_id,
            "KERNEL-M1A",
            logical,
            under_lease=executive_lease,
        )
        packet = derive_work_packet(
            self.state,
            task_node["id"],
            {"command_id": command_id, "lease_ref": executive_lease, "logical_time": logical},
            work_lease=work_lease,
            route=route,
            budget_ref=object_ref(reservation),
            attempt=1,
        )
        self._accept(
            "derive-work-packet",
            "arm",
            {
                "task_ref": object_ref(task_node),
                "attempt": 1,
                "work_lease": work_lease,
                "route_assignment": route,
                "budget_reservation_ref": object_ref(reservation),
                "expected_work_packet_digest": packet["content_digest"],
            },
            lease=executive_lease,
            goal=object_ref(goal),
            plan=object_ref(plan),
        )
        validate_projection(self.state)
        admitted = next(
            record for record in self.state["records"] if record["object_type"] == "work-packet"
        )
        if admitted["content_digest"] != packet["content_digest"]:
            raise HarnessError("derived work packet digest was not admitted")
        if [item["disposition"] for item in self.receipts] != ["accepted"] * len(PLAN_COMMANDS):
            raise HarnessError("planning did not accept every command")
        return {
            "accepted": len(self.receipts),
            "commands": list(PLAN_COMMANDS),
            "goal_id": goal["id"],
            "intent_text": task,
            "outcome": task,
            "packet_id": admitted["id"],
            "projection_digest": self.state["content_digest"],
            "semantic_definition_digest": bound,
            "stream_id": STREAM_ID,
        }


def plan_task(task: str) -> dict:
    """Plan ``task`` and return the admitted projection summary."""

    return PlanningSession().plan(task)

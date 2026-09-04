#!/usr/bin/env python3
"""Materialize the literal M1A-02 red fixture corpus and SHA-256 manifest."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).with_name("fixtures")
SCHEMA_CANDIDATE = "ab9707480baf6ef7baff03b6bda444b890d78557"
GENESIS_DIGEST = "fb1168e6e4d1267c41ea3d7798ebb88963e6de7c05cc1500ed059ba4b2f75801"
ZERO_BUDGET = {
    "model_turns": 0,
    "attempts": 0,
    "tokens": 0,
    "money_minor": 0,
    "cpu_ms": 0,
    "memory_bytes": 0,
    "output_bytes": 0,
}
LIMIT_BUDGET = {
    "model_turns": 4,
    "attempts": 2,
    "tokens": 1000,
    "money_minor": 0,
    "cpu_ms": 10000,
    "memory_bytes": 1048576,
    "output_bytes": 65536,
}
COMMAND_TYPES = [
    "record-owner-intent",
    "accept-goal-spec",
    "amend-goal-spec",
    "record-owner-verifier-exception",
    "start-arm-run",
    "propose-plan-revision",
    "derive-work-packet",
    "replace-work-lease",
    "replace-executive-lease",
    "replace-route",
    "record-capacity-observation",
    "record-checkpoint",
    "reserve-budget",
    "submit-worker-result",
    "submit-gate-result",
    "propose-retry",
    "propose-replan",
    "raise-blocker",
    "raise-escalation",
    "submit-plan-verifier-decision",
    "apply-pause",
    "record-effect-observation",
]
ROLE_ACTORS = {
    "owner": "OWNER-LUCAS",
    "head": "HEAD-HERMES",
    "arm": "ARM-M1A",
    "worker": "WORKER-LUNA",
    "verifier": "VERIFIER-TERRA",
    "kernel-fixture-gate": "KERNEL-FIXTURE",
}


def utf16_key(value: str) -> bytes:
    return value.encode("utf-16be")


def canonical_bytes(value) -> bytes:
    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if isinstance(value, int) and not isinstance(value, bool):
        if value < 0 or value > 9_007_199_254_740_991:
            raise ValueError("integer outside M1A I-JSON range")
        return str(value).encode("ascii")
    if isinstance(value, str):
        value.encode("utf-8", errors="strict")
        return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if isinstance(value, list):
        return b"[" + b",".join(canonical_bytes(item) for item in value) + b"]"
    if isinstance(value, dict):
        keys = sorted(value, key=utf16_key)
        return b"{" + b",".join(
            canonical_bytes(key) + b":" + canonical_bytes(value[key]) for key in keys
        ) + b"}"
    raise TypeError(f"unsupported canonical value: {type(value)!r}")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(value, *, omit_content_digest: bool = False) -> str:
    operand = copy.deepcopy(value)
    if omit_content_digest and isinstance(operand, dict):
        operand.pop("content_digest", None)
    return sha_bytes(canonical_bytes(operand))


def sealed(value: dict) -> dict:
    result = copy.deepcopy(value)
    result.pop("content_digest", None)
    result["content_digest"] = digest(result)
    return result


def h(label: str) -> str:
    return sha_bytes(label.encode("utf-8"))


def object_ref(record: dict) -> dict:
    return {
        "object_type": record["object_type"],
        "id": record["id"],
        "version": record["version"],
        "content_digest": record["content_digest"],
    }


def lease_ref(record: dict) -> dict:
    return {
        "lease_id": record["id"],
        "lease_epoch": record["payload"]["lease_epoch"],
        "content_digest": record["content_digest"],
    }


def policy_ref(policy: dict) -> dict:
    return {
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "content_digest": policy["content_digest"],
    }


def domain_record(
    object_type: str,
    schema_version: str,
    record_id: str,
    payload: dict,
    command_id: str,
    actor_id: str,
    logical_time: int,
    *,
    version: int = 1,
    under_lease: dict | None = None,
) -> dict:
    return sealed(
        {
            "object_type": object_type,
            "schema_version": schema_version,
            "id": record_id,
            "version": version,
            "created_by_actor_id": actor_id,
            "created_under_lease": under_lease,
            "causation_id": command_id,
            "correlation_id": "CORR-M1A",
            "created_logical_time": logical_time,
            "payload": payload,
        }
    )


def make_policies() -> list[dict]:
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
        return sealed(
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
        policy(
            "POLICY-CONSTITUTION",
            "constitution",
            owner_verifier_exception_allowed=True,
        ),
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


def error_witness(error: str, *, object_ids=None, edges=None, fields=None) -> dict:
    return sealed(
        {
            "witness_schema_version": "m1a-error-witness-1",
            "error_code": error,
            "object_ids": sorted(object_ids or []),
            "dependency_edges": sorted(edges or [], key=lambda e: (e["from_node_id"], e["to_node_id"])),
            "field_paths": sorted(fields or []),
        }
    )


class Session:
    def __init__(self, fixture_id: str, case_id: str, description: str):
        self.fixture_id = fixture_id
        self.case_id = case_id
        self.description = description
        self.policies = make_policies()
        self.policy_by_kind = {item["policy_kind"]: item for item in self.policies}
        pause_ref = policy_ref(self.policy_by_kind["pause"])
        self.genesis = {
            "genesis_schema_version": "m1a-genesis-1",
            "stream_id": "STREAM-M1A",
            "current_pause_policy_ref": pause_ref,
            "current_pause_epoch": 0,
        }
        self.state = self._seal_state(
            {
                "projection_schema_version": "m1a-projection-1",
                "stream_id": "STREAM-M1A",
                "state_version": 0,
                "last_event_sequence": 0,
                "last_event_digest": GENESIS_DIGEST,
                "operative_goal_ref": None,
                "active_arm_run_ref": None,
                "active_plan_ref": None,
                "records": [],
                "object_states": [],
                "processed_command_receipts": [],
                "consumed_novelty_delta_digests": [],
                "open_blocker_refs": [],
                "open_escalation_refs": [],
                "ambiguous_effect_refs": [],
                "current_pause_policy_ref": pause_ref,
                "current_pause_epoch": 0,
                "terminal_status": "nonterminal",
            }
        )
        self.authorities: list[dict] = []
        self.initial_commands: list[dict] = []
        self.initial_receipts: list[dict] = []
        self.initial_events: list[dict] = []
        self.decode_inputs: list[str] = []
        self.decode_failures: list[dict] = []
        self.commands: list[dict] = []
        self.receipts: list[dict] = []
        self.events: list[dict] = []
        self.replay_cases: list[dict] = []
        self.command_ordinal = 0
        self.records: dict[str, dict] = {}

    def _seal_state(self, state: dict) -> dict:
        result = copy.deepcopy(state)
        result.pop("content_digest", None)
        result["records"] = sorted(
            result["records"], key=lambda r: (r["object_type"], r["id"], r["version"])
        )
        result["object_states"] = sorted(
            result["object_states"],
            key=lambda s: (
                s["object_ref"]["object_type"], s["object_ref"]["id"], s["object_ref"]["version"]
            ),
        )
        for field in (
            "processed_command_receipts",
            "open_blocker_refs",
            "open_escalation_refs",
            "ambiguous_effect_refs",
        ):
            key = "receipt_id" if field == "processed_command_receipts" else "id"
            result[field] = sorted(result[field], key=lambda item: item[key])
        result["consumed_novelty_delta_digests"] = sorted(
            result["consumed_novelty_delta_digests"]
        )
        return sealed(result)

    def policy_ref(self, kind: str) -> dict:
        return policy_ref(self.policy_by_kind[kind])

    def next_command_id(self) -> str:
        self.command_ordinal += 1
        return f"CMD-{self.fixture_id}-{self.case_id}-{self.command_ordinal:02d}"

    def _authority(self, command_id: str, command_type: str, role: str, candidate: str) -> dict:
        suffix = command_id[4:] if command_id.startswith("CMD-") else command_id
        result = sealed(
            {
                "attestation_schema_version": "m1a-fixture-authority-1",
                "attestation_id": f"AUTH-{suffix}",
                "actor_id": ROLE_ACTORS[role],
                "actor_role": role,
                "allowed_command_types": [command_type],
                "candidate_digest": candidate,
                "authority_policy_ref": self.policy_ref("authority"),
                "constitution_policy_ref": self.policy_ref("constitution"),
                "valid_from_logical_time": 0,
                "expires_logical_time": 10000,
            }
        )
        self.authorities.append(result)
        self.authorities.sort(key=lambda item: item["attestation_id"])
        return result

    def _command(
        self,
        command_id: str,
        command_type: str,
        role: str,
        payload: dict,
        *,
        lease: dict | None,
        goal: dict | None,
        plan: dict | None,
        include_authority: bool = True,
    ) -> dict:
        payload_digest = digest(payload)
        authority = self._authority(command_id, command_type, role, payload_digest) if include_authority else None
        return sealed(
            {
                "command_schema_version": "m1a-command-1",
                "command_id": command_id,
                "command_type": command_type,
                "actor_id": ROLE_ACTORS[role],
                "auth_ref": authority["attestation_id"] if authority else "AUTH-UNKNOWN",
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

    def _set_object_state(self, record: dict, state: str) -> None:
        target = object_ref(record)
        self.state["object_states"] = [
            item for item in self.state["object_states"]
            if not (
                item["object_ref"]["object_type"] == target["object_type"]
                and item["object_ref"]["id"] == target["id"]
                and item["object_ref"]["version"] == target["version"]
            )
        ]
        self.state["object_states"].append({"object_ref": target, "state": state})

    def _set_ref_state(self, target: dict | None, state: str) -> None:
        if target is None:
            return
        for record in self.state["records"]:
            if (
                record["object_type"] == target["object_type"]
                and record["id"] == target["id"]
                and record["version"] == target["version"]
            ):
                self._set_object_state(record, state)
                return

    def _insert_record(self, record: dict) -> None:
        key = f"{record['object_type']}:{record['id']}:{record['version']}"
        existing = self.records.get(key)
        if existing is not None and existing != record:
            raise ValueError(f"conflicting fixture record {key}")
        if existing is None:
            self.records[key] = record
            self.state["records"].append(record)
        default_state = {
            "owner-intent": "recorded",
            "goal-spec": "accepted",
            "goal-spec-amendment": "applied",
            "arm-run": "active",
            "plan-revision": "active",
            "plan-transition": "applied",
            "task-node": "ready",
            "work-packet": "leased",
            "worker-result": "submitted",
            "gate-result": "recorded",
            "retry-decision": record.get("payload", {}).get("disposition", "recorded"),
            "replan-decision": record.get("payload", {}).get("disposition", "recorded"),
            "blocker": record.get("payload", {}).get("state", "open"),
            "escalation": record.get("payload", {}).get("state", "raised"),
            "plan-verifier-decision": record.get("payload", {}).get("disposition", "recorded"),
            "owner-verifier-exception": "active",
            "executive-lease": record.get("payload", {}).get("state", "active"),
            "work-lease": record.get("payload", {}).get("state", "active"),
            "checkpoint": "recorded",
            "route-assignment": record.get("payload", {}).get("state", "assigned"),
            "capacity-observation": "recorded",
            "budget-reservation": record.get("payload", {}).get("state", "reserved"),
            "pause-directive": "applied",
            "effect-observation": record.get("payload", {}).get("observation", "recorded"),
            "disposition": record.get("payload", {}).get("disposition", "recorded"),
        }[record["object_type"]]
        self._set_object_state(record, default_state)

    def _apply_event(self, event: dict) -> None:
        records = [event["primary_record"], *event["related_records"]]
        for record in records:
            self._insert_record(record)
            payload = record["payload"]
            if record["object_type"] == "work-packet":
                self._set_ref_state(payload["supersedes_packet_ref"], "stale")
            elif record["object_type"] in ("work-lease", "executive-lease"):
                old = payload["supersedes_lease_ref"]
                if old:
                    for prior in self.state["records"]:
                        if prior["id"] == old["lease_id"]:
                            self._set_object_state(prior, "replaced")
            elif record["object_type"] == "route-assignment":
                self._set_ref_state(payload["supersedes_route_ref"], "released")

        primary = event["primary_record"]
        payload = primary["payload"]
        event_type = event["event_type"]
        if event_type == "GoalSpecAccepted":
            self.state["operative_goal_ref"] = object_ref(primary)
        elif event_type == "GoalSpecAmended":
            self._set_ref_state(payload["old_goal_ref"], "superseded")
            self.state["operative_goal_ref"] = object_ref(event["related_records"][0])
        elif event_type == "ArmRunStarted":
            self.state["active_arm_run_ref"] = object_ref(primary)
        elif event_type == "PlanRevisionAdmitted":
            if payload["prior_plan_ref"]:
                self._set_ref_state(payload["prior_plan_ref"], "superseded")
            self.state["active_plan_ref"] = object_ref(primary)
        elif event_type == "WorkerResultRecorded":
            packet_ref = payload["work_packet_ref"]
            self._set_ref_state(packet_ref, "result-submitted")
            for packet in self.state["records"]:
                if packet["object_type"] == "work-packet" and packet["id"] == packet_ref["id"]:
                    self._set_ref_state(packet["payload"]["task_ref"], "result-submitted")
        elif event_type == "GateResultRecorded":
            state = "verified" if payload["disposition"] == "pass" else "failed"
            self._set_ref_state(payload["task_ref"], state)
        elif event_type == "RetryAdmitted":
            self.state["consumed_novelty_delta_digests"].append(payload["novelty_delta_digest"])
            self._set_ref_state(payload["task_ref"], "ready")
        elif event_type == "BlockerRaised":
            self.state["open_blocker_refs"].append(object_ref(primary))
        elif event_type == "EscalationRaised":
            self.state["open_escalation_refs"].append(object_ref(primary))
        elif event_type == "PauseApplied":
            self.state["current_pause_epoch"] = payload["new_pause_epoch"]
        elif event_type == "EffectObservationRecorded" and payload["observation"] == "ambiguous":
            self.state["ambiguous_effect_refs"].append(object_ref(primary))
        elif event_type == "PlanVerifierDecisionRecorded":
            if payload["disposition"] == "pass":
                self.state["terminal_status"] = "terminal-verified"
                self._set_ref_state(payload["plan_ref"], "terminal-verified")
                for record in self.state["records"]:
                    if (
                        record["object_type"] == "task-node"
                        and record["payload"]["plan_ref"]["id"] == payload["plan_ref"]["id"]
                    ):
                        self._set_object_state(record, "complete")
            elif payload["disposition"] == "downgraded-pass":
                self.state["terminal_status"] = "terminal-verified-downgraded"
                self._set_ref_state(payload["plan_ref"], "terminal-verified-downgraded")
                for record in self.state["records"]:
                    if (
                        record["object_type"] == "task-node"
                        and record["payload"]["plan_ref"]["id"] == payload["plan_ref"]["id"]
                    ):
                        self._set_object_state(record, "complete")

        self.state["state_version"] += 1
        self.state["last_event_sequence"] = event["sequence"]
        self.state["last_event_digest"] = event["content_digest"]
        self.state = self._seal_state(self.state)

    def _event(self, command: dict, position: int, event_type: str, primary: dict, related: list[dict]) -> dict:
        suffix = command["command_id"][4:] if command["command_id"].startswith("CMD-") else command["command_id"]
        related = sorted(related, key=lambda r: (r["object_type"], r["id"], r["version"]))
        return sealed(
            {
                "event_schema_version": "m1a-event-1",
                "event_id": f"EV-{suffix}-{position:04d}",
                "stream_id": self.state["stream_id"],
                "sequence": self.state["last_event_sequence"] + 1,
                "previous_event_digest": self.state["last_event_digest"],
                "logical_time": command["logical_time"],
                "command_id": command["command_id"],
                "command_digest": command["content_digest"],
                "event_type": event_type,
                "primary_record": primary,
                "related_records": related,
                "state_delta_digest": digest(
                    {"event_type": event_type, "primary_record": primary, "related_records": related}
                ),
            }
        )

    def accept(
        self,
        command_type: str,
        role: str,
        payload_builder,
        event_builder,
        *,
        lease: dict | None = None,
        goal: dict | None = None,
        plan: dict | None = None,
    ) -> tuple[dict, dict]:
        command_id = self.next_command_id()
        payload = payload_builder(command_id)
        command = self._command(
            command_id, command_type, role, payload, lease=lease, goal=goal, plan=plan
        )
        before = self.state["content_digest"]
        emitted = []
        for position, (event_type, primary, related) in enumerate(
            event_builder(command_id, payload), start=1
        ):
            event = self._event(command, position, event_type, primary, related)
            emitted.append(event)
            self._apply_event(event)
        receipt_id = (
            "RCPT-" + command_id[4:] if command_id.startswith("CMD-") else "RCPT-" + command_id
        )
        identity = {
            "receipt_id": receipt_id,
            "command_id": command_id,
            "command_digest": command["content_digest"],
        }
        self.state["processed_command_receipts"].append(identity)
        self.state = self._seal_state(self.state)
        receipt = sealed(
            {
                "receipt_schema_version": "m1a-receipt-1",
                "receipt_id": receipt_id,
                "command_id": command_id,
                "command_digest": command["content_digest"],
                "disposition": "accepted",
                "primary_error": None,
                "related_errors": [],
                "witness": None,
                "state_before_digest": before,
                "state_after_digest": self.state["content_digest"],
                "event_ids": sorted(event["event_id"] for event in emitted),
                "first_event_sequence": emitted[0]["sequence"],
                "last_event_sequence": emitted[-1]["sequence"],
            }
        )
        self.commands.append(command)
        self.receipts.append(receipt)
        self.events.extend(emitted)
        return command, receipt

    def refuse(
        self,
        command_type: str,
        role: str,
        payload_builder,
        error: str,
        *,
        lease: dict | None = None,
        goal: dict | None = None,
        plan: dict | None = None,
        witness: dict | None = None,
        include_authority: bool = True,
        disposition: str = "refused",
        command_id: str | None = None,
    ) -> tuple[dict, dict]:
        command_id = command_id or self.next_command_id()
        payload = payload_builder(command_id)
        command = self._command(
            command_id,
            command_type,
            role,
            payload,
            lease=lease,
            goal=goal,
            plan=plan,
            include_authority=include_authority,
        )
        if disposition == "conflict":
            receipt_id = "RCPT-CONFLICT-" + digest(
                {"command_id": command_id, "command_digest": command["content_digest"]}
            )[:32]
        else:
            receipt_id = "RCPT-" + (command_id[4:] if command_id.startswith("CMD-") else command_id)
        receipt = sealed(
            {
                "receipt_schema_version": "m1a-receipt-1",
                "receipt_id": receipt_id,
                "command_id": command_id,
                "command_digest": command["content_digest"],
                "disposition": disposition,
                "primary_error": error,
                "related_errors": [],
                "witness": witness,
                "state_before_digest": self.state["content_digest"],
                "state_after_digest": self.state["content_digest"],
                "event_ids": [],
                "first_event_sequence": None,
                "last_event_sequence": None,
            }
        )
        self.commands.append(command)
        self.receipts.append(receipt)
        return command, receipt

    def add_decode_failure(self, raw: str, error: str) -> None:
        raw_bytes = raw.encode("utf-8")
        self.decode_inputs.append(raw)
        self.decode_failures.append(
            sealed(
                {
                    "decode_failure_schema_version": "m1a-decode-failure-1",
                    "schema_epoch": "m1a-1",
                    "raw_input_digest": sha_bytes(raw_bytes),
                    "primary_error": error,
                    "related_errors": [],
                }
            )
        )

    def promote_current_to_initial(self) -> None:
        self.initial_commands.extend(self.commands)
        self.initial_receipts.extend(self.receipts)
        self.initial_events.extend(self.events)
        self.commands = []
        self.receipts = []
        self.events = []

    def fixture_case(self) -> dict:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "genesis": self.genesis,
            "authority_fixtures": self.authorities,
            "policy_fixtures": self.policies,
            "initial_commands": self.initial_commands,
            "initial_receipts": self.initial_receipts,
            "initial_events": self.initial_events,
            "decode_inputs": self.decode_inputs,
            "expected_decode_failures": self.decode_failures,
            "commands": self.commands,
            "expected_receipts": self.receipts,
            "expected_events": self.events,
            "replay_cases": self.replay_cases,
            "expected_final_state": self.state,
            "expected_final_digest": self.state["content_digest"],
        }


def gate_requirement() -> dict:
    return {
        "gate_id": "GATE-M1A",
        "procedure_digest": h("gate-procedure"),
        "evidence_schema_digest": h("gate-evidence-schema"),
        "candidate_binding_digest": h("candidate-binding"),
        "verifier_policy_digest": h("verifier-policy"),
        "assigned_verifier_actor_id": ROLE_ACTORS["verifier"],
    }


def add_standard_setup(
    session: Session,
    through: str,
    *,
    gate_disposition: str = "pass",
    verifier_disposition: str = "pass",
    two_nodes: bool = False,
) -> dict[str, dict]:
    world: dict[str, dict] = {}
    stages = ["intent", "goal", "arm", "plan", "capacity", "budget", "packet", "worker", "gate", "verifier"]
    target = stages.index(through)

    def run(stage: str) -> bool:
        return stages.index(stage) <= target

    if run("intent"):
        def intent_payload(command_id):
            record = domain_record(
                "owner-intent",
                "m1a-owner-intent-1",
                "INTENT-M1A",
                {
                    "intent_text": "Complete the deterministic synthetic M1A contract.",
                    "source_kind": "owner-prompt",
                    "source_digest": h("owner-intent-source"),
                    "privacy_policy_ref": session.policy_ref("privacy-egress"),
                    "supersedes_ref": None,
                },
                command_id,
                ROLE_ACTORS["owner"],
                session.state["last_event_sequence"] + 1,
            )
            world["intent"] = record
            return record

        session.accept(
            "record-owner-intent",
            "owner",
            intent_payload,
            lambda cid, payload: [("OwnerIntentRecorded", payload, [])],
        )

    if run("goal"):
        def goal_payload(command_id):
            record = domain_record(
                "goal-spec",
                "m1a-goal-spec-1",
                "GOAL-M1A",
                {
                    "owner_intent_ref": object_ref(world["intent"]),
                    "outcome": "Reach the declared synthetic gate with deterministic replay.",
                    "acceptance_gate_ids": ["GATE-M1A"],
                    "allowed_resource_paths": ["workspace/input", "workspace/output"],
                    "non_goals": ["no external effects", "no publication"],
                    "authority_ids": ["AUTHORITY-M1A"],
                    "capability_ids": ["CAPABILITY-BASE", "CAPABILITY-REPAIR"],
                    "allowed_action_ids": ["ACTION-READ", "ACTION-WRITE"],
                    "prohibition_ids": ["PROHIBIT-EGRESS"],
                    "authority_policy_ref": session.policy_ref("authority"),
                    "privacy_class_id": "PRIVACY-SYNTHETIC",
                    "egress_class_id": "EGRESS-NONE",
                    "privacy_policy_ref": session.policy_ref("privacy-egress"),
                    "egress_policy_ref": session.policy_ref("privacy-egress"),
                    "route_policy_ref": session.policy_ref("route-envelope"),
                    "allowed_route_ids": ["ROUTE-INCLUDED", "ROUTE-ZERO"],
                    "allowed_account_class_ids": ["ACCOUNT-INCLUDED"],
                    "allowed_capacity_pool_ids": ["CAPACITY-INCLUDED"],
                    "budget_limits": LIMIT_BUDGET,
                    "source_digests": [h("source-one")],
                    "novelty_policy_ref": session.policy_ref("novelty"),
                    "retry_policy_ref": session.policy_ref("retry"),
                    "verifier_policy_ref": session.policy_ref("verifier"),
                    "constitution_policy_ref": session.policy_ref("constitution"),
                    "pause_policy_ref": session.policy_ref("pause"),
                    "allowed_effect_keys": ["EFFECT-SYNTHETIC"],
                    "publication_allowed": False,
                    "terminal_owner_seam_ids": ["SEAM-OWNER"],
                    "fence_epoch": 1,
                    "state": "accepted",
                },
                command_id,
                ROLE_ACTORS["owner"],
                session.state["last_event_sequence"] + 1,
            )
            world["goal"] = record
            return record

        session.accept(
            "accept-goal-spec",
            "owner",
            goal_payload,
            lambda cid, payload: [("GoalSpecAccepted", payload, [])],
        )

    if run("arm"):
        def arm_payload(command_id):
            logical_time = session.state["last_event_sequence"] + 1
            executive = domain_record(
                "executive-lease",
                "m1a-executive-lease-1",
                "LEASE-EXEC-1",
                {
                    "subject_actor_id": ROLE_ACTORS["arm"],
                    "goal_ref": object_ref(world["goal"]),
                    "plan_ref": None,
                    "task_ref": None,
                    "supersedes_lease_ref": None,
                    "lease_epoch": 1,
                    "nonce_digest": h("executive-lease-one"),
                    "issued_logical_time": logical_time,
                    "expires_logical_time": 1000,
                    "allowed_command_types": sorted(
                        ["derive-work-packet", "propose-plan-revision", "propose-replan", "propose-retry", "reserve-budget"]
                    ),
                    "state": "active",
                },
                command_id,
                "KERNEL-M1A",
                logical_time,
            )
            arm = domain_record(
                "arm-run",
                "m1a-arm-run-1",
                "ARM-RUN-M1A",
                {
                    "goal_ref": object_ref(world["goal"]),
                    "logical_actor_id": ROLE_ACTORS["arm"],
                    "eligible_route_ids": ["ROUTE-INCLUDED", "ROUTE-ZERO"],
                    "eligible_account_class_ids": ["ACCOUNT-INCLUDED"],
                    "eligible_capacity_pool_ids": ["CAPACITY-INCLUDED"],
                    "budget_limits": LIMIT_BUDGET,
                    "source_digests": [h("source-one")],
                    "executive_lease_ref": lease_ref(executive),
                    "verifier_policy_ref": session.policy_ref("verifier"),
                },
                command_id,
                ROLE_ACTORS["head"],
                logical_time,
            )
            world["executive_lease"] = executive
            world["arm"] = arm
            return {"executive_lease": executive, "arm_run": arm}

        session.accept(
            "start-arm-run",
            "head",
            arm_payload,
            lambda cid, payload: [("ArmRunStarted", payload["arm_run"], [payload["executive_lease"]])],
            goal=object_ref(world["goal"]),
        )

    if run("plan"):
        def plan_payload(command_id):
            logical_time = session.state["last_event_sequence"] + 1
            task = domain_record(
                "task-node",
                "m1a-task-node-1",
                "TASK-M1A-A",
                {
                    "plan_ref": {"object_type": "plan-revision", "id": "PLAN-M1A", "version": 1},
                    "semantic_definition_digest": h("task-semantics"),
                    "output_schema_digest": h("task-output-schema"),
                    "dependency_node_ids": [],
                    "input_digests": [h("task-input")],
                    "source_digests": [h("source-one")],
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
                    "authority_policy_ref": session.policy_ref("authority"),
                    "privacy_class_id": "PRIVACY-SYNTHETIC",
                    "egress_class_id": "EGRESS-NONE",
                    "privacy_policy_ref": session.policy_ref("privacy-egress"),
                    "egress_policy_ref": session.policy_ref("privacy-egress"),
                    "budget_limits": LIMIT_BUDGET,
                    "gate_requirements": [gate_requirement()],
                    "retry_policy_ref": session.policy_ref("retry"),
                    "verifier_policy_ref": session.policy_ref("verifier"),
                    "constitution_policy_ref": session.policy_ref("constitution"),
                    "terminal_contribution_digest": h("terminal-contribution"),
                    "retry_maximum": 2,
                },
                command_id,
                ROLE_ACTORS["arm"],
                logical_time,
                under_lease=lease_ref(world["executive_lease"]),
            )
            task_ref = object_ref(task)
            tasks = [task]
            edges = []
            if two_nodes:
                second_payload = copy.deepcopy(task["payload"])
                second_payload["plan_ref"] = {
                    "object_type": "plan-revision", "id": "PLAN-M1A", "version": 1
                }
                second_payload["semantic_definition_digest"] = h("task-semantics-b")
                second_payload["dependency_node_ids"] = ["TASK-M1A-A"]
                second_payload["effect_keys"] = []
                second_payload["write_resource_paths"] = ["workspace/output/b"]
                second = domain_record(
                    "task-node",
                    "m1a-task-node-1",
                    "TASK-M1A-B",
                    second_payload,
                    command_id,
                    ROLE_ACTORS["arm"],
                    logical_time,
                    under_lease=lease_ref(world["executive_lease"]),
                )
                tasks.append(second)
                edges.append({"from_node_id": "TASK-M1A-A", "to_node_id": "TASK-M1A-B"})
                world["task_b"] = second
            task_refs = sorted([object_ref(item) for item in tasks], key=lambda item: item["id"])
            plan = domain_record(
                "plan-revision",
                "m1a-plan-revision-1",
                "PLAN-M1A",
                {
                    "goal_ref": object_ref(world["goal"]),
                    "arm_run_ref": object_ref(world["arm"]),
                    "prior_plan_ref": None,
                    "trigger": "initial",
                    "task_node_refs": task_refs,
                    "dependency_edges": edges,
                    "graph_digest": digest({"task_node_refs": task_refs, "dependency_edges": edges}),
                    "acceptance_gate_ids": ["GATE-M1A"],
                    "budget_limits": LIMIT_BUDGET,
                    "read_resource_paths": ["workspace/input"],
                    "write_resource_paths": ["workspace/output"],
                    "effect_keys": ["EFFECT-SYNTHETIC"],
                    "source_digests": [h("source-one")],
                    "verifier_policy_ref": session.policy_ref("verifier"),
                    "constitution_policy_ref": session.policy_ref("constitution"),
                    "assigned_plan_verifier_actor_id": ROLE_ACTORS["verifier"],
                    "change_rationale_digest": h("initial-plan"),
                    "dispositions": [],
                },
                command_id,
                ROLE_ACTORS["arm"],
                logical_time,
                under_lease=lease_ref(world["executive_lease"]),
            )
            transition = domain_record(
                "plan-transition",
                "m1a-plan-transition-1",
                "TRANSITION-M1A-1",
                {
                    "from_plan_ref": None,
                    "to_plan_ref": object_ref(plan),
                    "trigger_evidence_digests": [h("owner-intent-source")],
                    "dispositions": [],
                    "executive_lease_ref": lease_ref(world["executive_lease"]),
                    "expected_goal_fence_epoch": 1,
                    "checkpoint_ref": None,
                },
                command_id,
                ROLE_ACTORS["arm"],
                logical_time,
                under_lease=lease_ref(world["executive_lease"]),
            )
            world["task"] = task
            world["plan"] = plan
            world["transition"] = transition
            return {"plan_revision": plan, "plan_transition": transition, "task_nodes": tasks}

        session.accept(
            "propose-plan-revision",
            "arm",
            plan_payload,
            lambda cid, payload: [
                ("PlanRevisionAdmitted", payload["plan_revision"], [payload["plan_transition"], *payload["task_nodes"]])
            ],
            lease=lease_ref(world["executive_lease"]),
            goal=object_ref(world["goal"]),
        )

    if run("capacity"):
        def capacity_payload(command_id):
            record = domain_record(
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
                    "observation_digest": h("capacity-available"),
                },
                command_id,
                ROLE_ACTORS["kernel-fixture-gate"],
                session.state["last_event_sequence"] + 1,
            )
            world["capacity"] = record
            return record

        session.accept(
            "record-capacity-observation",
            "kernel-fixture-gate",
            capacity_payload,
            lambda cid, payload: [("CapacityObservationRecorded", payload, [])],
            goal=object_ref(world["goal"]),
            plan=object_ref(world["plan"]),
        )

    if run("budget"):
        def budget_payload(command_id):
            record = domain_record(
                "budget-reservation",
                "m1a-budget-reservation-1",
                "BUDGET-RESERVATION-1",
                {
                    "goal_ref": object_ref(world["goal"]),
                    "plan_ref": object_ref(world["plan"]),
                    "task_ref": object_ref(world["task"]),
                    "limits": LIMIT_BUDGET,
                    "consumed": ZERO_BUDGET,
                    "remaining": LIMIT_BUDGET,
                    "state": "reserved",
                },
                command_id,
                ROLE_ACTORS["arm"],
                session.state["last_event_sequence"] + 1,
                under_lease=lease_ref(world["executive_lease"]),
            )
            world["budget"] = record
            return record

        session.accept(
            "reserve-budget",
            "arm",
            budget_payload,
            lambda cid, payload: [("BudgetReserved", payload, [])],
            lease=lease_ref(world["executive_lease"]),
            goal=object_ref(world["goal"]),
            plan=object_ref(world["plan"]),
        )

    if run("packet"):
        def packet_payload(command_id):
            logical_time = session.state["last_event_sequence"] + 1
            work_lease = domain_record(
                "work-lease",
                "m1a-work-lease-1",
                "LEASE-WORK-1",
                {
                    "subject_actor_id": ROLE_ACTORS["worker"],
                    "goal_ref": object_ref(world["goal"]),
                    "plan_ref": object_ref(world["plan"]),
                    "task_ref": object_ref(world["task"]),
                    "supersedes_lease_ref": None,
                    "lease_epoch": 1,
                    "nonce_digest": h("work-lease-one"),
                    "issued_logical_time": logical_time,
                    "expires_logical_time": 900,
                    "allowed_command_types": ["submit-worker-result"],
                    "state": "active",
                },
                command_id,
                "KERNEL-M1A",
                logical_time,
                under_lease=lease_ref(world["executive_lease"]),
            )
            route = domain_record(
                "route-assignment",
                "m1a-route-assignment-1",
                "ROUTE-ASSIGNMENT-1",
                {
                    "logical_actor_id": ROLE_ACTORS["worker"],
                    "route_id": "ROUTE-INCLUDED",
                    "route_capability_ids": ["CAPABILITY-BASE"],
                    "account_class_id": "ACCOUNT-INCLUDED",
                    "capacity_pool_id": "CAPACITY-INCLUDED",
                    "privacy_policy_ref": session.policy_ref("privacy-egress"),
                    "egress_policy_ref": session.policy_ref("privacy-egress"),
                    "route_policy_ref": session.policy_ref("route-envelope"),
                    "metered_spend_allowed": False,
                    "capacity_observation_ref": object_ref(world["capacity"]),
                    "supersedes_route_ref": None,
                    "assigned_logical_time": logical_time,
                    "expires_logical_time": 900,
                    "state": "assigned",
                },
                command_id,
                "KERNEL-M1A",
                logical_time,
                under_lease=lease_ref(world["executive_lease"]),
            )
            seed = {
                "command_id": command_id,
                "task_ref": object_ref(world["task"]),
                "attempt": 1,
                "work_lease_ref": lease_ref(work_lease),
                "route_assignment_ref": object_ref(route),
                "budget_reservation_ref": object_ref(world["budget"]),
                "checkpoint_ref": None,
            }
            packet = domain_record(
                "work-packet",
                "m1a-work-packet-1",
                "PACKET-" + digest(seed)[:32],
                {
                    "goal_ref": object_ref(world["goal"]),
                    "plan_ref": object_ref(world["plan"]),
                    "task_ref": object_ref(world["task"]),
                    "supersedes_packet_ref": None,
                    "logical_worker_actor_id": ROLE_ACTORS["worker"],
                    "attempt": 1,
                    "work_lease_ref": lease_ref(work_lease),
                    "expected_goal_fence_epoch": 1,
                    "expected_pause_epoch": 0,
                    "authority_ids": ["AUTHORITY-M1A"],
                    "capability_ids": ["CAPABILITY-BASE"],
                    "allowed_resource_paths": ["workspace/input", "workspace/output"],
                    "effect_keys": ["EFFECT-SYNTHETIC"],
                    "privacy_class_id": "PRIVACY-SYNTHETIC",
                    "egress_class_id": "EGRESS-NONE",
                    "authority_policy_ref": session.policy_ref("authority"),
                    "privacy_policy_ref": session.policy_ref("privacy-egress"),
                    "egress_policy_ref": session.policy_ref("privacy-egress"),
                    "route_assignment_ref": object_ref(route),
                    "budget_reservation_ref": object_ref(world["budget"]),
                    "budget_limits": LIMIT_BUDGET,
                    "source_digests": [h("source-one")],
                    "gate_requirements": [gate_requirement()],
                    "allowed_action_ids": ["ACTION-READ", "ACTION-WRITE"],
                    "prohibition_ids": ["PROHIBIT-EGRESS"],
                    "inherited_non_goals": ["no external effects", "no publication"],
                    "output_schema_digest": h("task-output-schema"),
                    "deadline_logical_time": 900,
                    "checkpoint_ref": None,
                },
                command_id,
                "KERNEL-M1A",
                logical_time,
                under_lease=lease_ref(world["executive_lease"]),
            )
            world["work_lease"] = work_lease
            world["route"] = route
            world["packet"] = packet
            return {
                "task_ref": object_ref(world["task"]),
                "attempt": 1,
                "work_lease": work_lease,
                "route_assignment": route,
                "budget_reservation_ref": object_ref(world["budget"]),
                "expected_work_packet_digest": packet["content_digest"],
            }

        session.accept(
            "derive-work-packet",
            "arm",
            packet_payload,
            lambda cid, payload: [("WorkPacketDerived", world["packet"], [payload["route_assignment"], payload["work_lease"]])],
            lease=lease_ref(world["executive_lease"]),
            goal=object_ref(world["goal"]),
            plan=object_ref(world["plan"]),
        )

    if run("worker"):
        def worker_payload(command_id):
            result = domain_record(
                "worker-result",
                "m1a-worker-result-1",
                "RESULT-M1A-1",
                {
                    "work_packet_ref": object_ref(world["packet"]),
                    "candidate_digest": h("candidate-one"),
                    "evidence_digests": [h("evidence-one")],
                    "output_digest": h("output-one"),
                    "observed_effect_ref": None,
                    "disposition": "submitted",
                },
                command_id,
                ROLE_ACTORS["worker"],
                session.state["last_event_sequence"] + 1,
                under_lease=lease_ref(world["work_lease"]),
            )
            world["worker_result"] = result
            return result

        session.accept(
            "submit-worker-result",
            "worker",
            worker_payload,
            lambda cid, payload: [("WorkerResultRecorded", payload, [])],
            lease=lease_ref(world["work_lease"]),
            goal=object_ref(world["goal"]),
            plan=object_ref(world["plan"]),
        )

    if run("gate"):
        def gate_payload(command_id):
            result = domain_record(
                "gate-result",
                "m1a-gate-result-1",
                "GATE-RESULT-M1A-1",
                {
                    "goal_ref": object_ref(world["goal"]),
                    "plan_ref": object_ref(world["plan"]),
                    "task_ref": object_ref(world["task"]),
                    "work_packet_ref": object_ref(world["packet"]),
                    "candidate_digest": h("candidate-one"),
                    "source_digests": [h("source-one")],
                    "evidence_digests": [h("evidence-one")],
                    "gate_requirement": gate_requirement(),
                    "procedure_version": 1,
                    "observation_digest": h("gate-observation"),
                    "expected_digest": h("expected-output"),
                    "actual_digest": h("actual-output" if gate_disposition != "pass" else "expected-output"),
                    "independence": {
                        "model_family": "gpt-family",
                        "provider": "openai",
                        "host": "local",
                        "session": "fixture",
                        "evidence_store": "fixture",
                        "implementation_actor_id": "ACTOR-IMPLEMENTER",
                        "verifier_actor_id": ROLE_ACTORS["verifier"],
                        "missing_dimensions": [],
                    },
                    "disposition": gate_disposition,
                    "limitation_digests": [],
                },
                command_id,
                ROLE_ACTORS["verifier"],
                session.state["last_event_sequence"] + 1,
            )
            world["gate_result"] = result
            return result

        session.accept(
            "submit-gate-result",
            "verifier",
            gate_payload,
            lambda cid, payload: [("GateResultRecorded", payload, [])],
            goal=object_ref(world["goal"]),
            plan=object_ref(world["plan"]),
        )

    if run("verifier"):
        def verifier_payload(command_id):
            exception_ref = object_ref(world["exception"]) if verifier_disposition == "downgraded-pass" else None
            decision = domain_record(
                "plan-verifier-decision",
                "m1a-plan-verifier-decision-1",
                "PLAN-VERIFIER-DECISION-1",
                {
                    "goal_ref": object_ref(world["goal"]),
                    "plan_ref": object_ref(world["plan"]),
                    "candidate_digest": h("candidate-one"),
                    "event_log_digest": digest([
                        {"sequence": event["sequence"], "event_id": event["event_id"], "content_digest": event["content_digest"]}
                        for event in [*session.initial_events, *session.events]
                    ]),
                    "gate_result_digests": [world["gate_result"]["content_digest"]],
                    "evidence_digests": [h("evidence-one")],
                    "verifier_policy_ref": session.policy_ref("verifier"),
                    "constitution_policy_ref": session.policy_ref("constitution"),
                    "independence": {
                        "model_family": "gpt-family",
                        "provider": "openai",
                        "host": "local",
                        "session": "fixture",
                        "evidence_store": "fixture",
                        "implementation_actor_id": "ACTOR-IMPLEMENTER",
                        "verifier_actor_id": ROLE_ACTORS["verifier"],
                        "missing_dimensions": ["account"] if verifier_disposition == "downgraded-pass" else [],
                    },
                    "disposition": verifier_disposition,
                    "assurance_grade": "downgraded" if verifier_disposition == "downgraded-pass" else "full",
                    "owner_exception_ref": exception_ref,
                    "dissent_digest": None,
                    "limitation_digests": [h("same-family-limit")] if verifier_disposition == "downgraded-pass" else [],
                },
                command_id,
                ROLE_ACTORS["verifier"],
                session.state["last_event_sequence"] + 1,
            )
            world["verifier"] = decision
            return decision

        session.accept(
            "submit-plan-verifier-decision",
            "verifier",
            verifier_payload,
            lambda cid, payload: [("PlanVerifierDecisionRecorded", payload, [])],
            goal=object_ref(world["goal"]),
            plan=object_ref(world["plan"]),
        )

    return world


def novelty_delta() -> dict:
    evidence = {
        "evidence_id": "evidence-new",
        "evidence_type": "fixture-observation",
        "locator": "fixture://evidence/evidence-new",
        "content_digest": h("evidence-new-content"),
        "schema_digest": h("evidence-schema"),
    }
    diff_entries = [
        {
            "path_segments": ["0"],
            "old_value": {"state": "absent", "digest": None},
            "new_value": {"state": "present", "digest": digest(evidence)},
        }
    ]
    delta = {
        "novelty_schema_version": "novelty-delta-1",
        "delta_id": "delta-evidence-new",
        "prior_attempt_digest": h("prior-attempt"),
        "addresses_failure_ids": ["FAIL-GATE"],
        "old_descriptor_digest": digest([]),
        "new_descriptor_digest": digest([evidence]),
        "canonical_diff": diff_entries,
        "canonical_diff_digest": digest(diff_entries),
        "kind": "evidence-added",
        "old_evidence_refs": [],
        "new_evidence_refs": [evidence],
    }
    delta["delta_digest"] = digest(delta)
    return delta


def checkpoint_payload(session: Session, world: dict, command_id: str) -> dict:
    packet_refs = [
        object_ref(record) for record in session.state["records"] if record["object_type"] == "work-packet"
    ]
    route_refs = [
        object_ref(record) for record in session.state["records"] if record["object_type"] == "route-assignment"
    ]
    budget_refs = [
        object_ref(record) for record in session.state["records"] if record["object_type"] == "budget-reservation"
    ]
    lease_refs = [
        lease_ref(record) for record in session.state["records"]
        if record["object_type"] in ("executive-lease", "work-lease")
    ]
    return domain_record(
        "checkpoint",
        "m1a-checkpoint-1",
        "CHECKPOINT-M1A-1",
        {
            "state_version": session.state["state_version"],
            "state_digest": session.state["content_digest"],
            "active_goal_ref": session.state["operative_goal_ref"],
            "active_plan_ref": session.state["active_plan_ref"],
            "open_packet_refs": sorted(packet_refs, key=lambda r: r["id"]),
            "ambiguous_effect_refs": session.state["ambiguous_effect_refs"],
            "budget_snapshot_digest": digest(sorted(budget_refs, key=lambda r: r["id"])),
            "route_snapshot_digest": digest(sorted(route_refs, key=lambda r: r["id"])),
            "pause_epoch": session.state["current_pause_epoch"],
            "lease_epoch_digest": digest(sorted(lease_refs, key=lambda r: r["lease_id"])),
        },
        command_id,
        ROLE_ACTORS["kernel-fixture-gate"],
        session.state["last_event_sequence"] + 1,
    )


def candidate_plan_payload(
    session: Session,
    world: dict,
    command_id: str,
    *,
    mutation: str = "none",
) -> dict:
    logical_time = session.state["last_event_sequence"] + 1
    task_payload = copy.deepcopy(world["task"]["payload"])
    task_payload["plan_ref"] = {
        "object_type": "plan-revision", "id": "PLAN-CANDIDATE", "version": 2
    }
    task_payload["dependency_node_ids"] = []
    if mutation == "capability-widen":
        task_payload["capability_ids"] = ["CAPABILITY-BASE", "CAPABILITY-EXTRA"]
    elif mutation == "path-widen":
        task_payload["write_resource_paths"] = ["outside/path"]
    elif mutation == "route-widen":
        task_payload["route_ids"] = ["ROUTE-INCLUDED", "ROUTE-METERED", "ROUTE-ZERO"]
    elif mutation == "egress-widen":
        task_payload["egress_class_id"] = "EGRESS-SYNTHETIC"
    elif mutation == "budget-widen":
        task_payload["budget_limits"] = {**LIMIT_BUDGET, "tokens": LIMIT_BUDGET["tokens"] + 1}
    elif mutation == "missing-dependency":
        task_payload["dependency_node_ids"] = ["TASK-MISSING"]
    task = domain_record(
        "task-node",
        "m1a-task-node-1",
        "TASK-CANDIDATE-A",
        task_payload,
        command_id,
        ROLE_ACTORS["arm"],
        logical_time,
        version=2,
        under_lease=lease_ref(world["executive_lease"]),
    )
    tasks = [task]
    edges = []
    if mutation == "cycle":
        second_payload = copy.deepcopy(task_payload)
        second_payload["dependency_node_ids"] = ["TASK-CANDIDATE-A"]
        second_payload["semantic_definition_digest"] = h("candidate-task-b")
        second = domain_record(
            "task-node",
            "m1a-task-node-1",
            "TASK-CANDIDATE-B",
            second_payload,
            command_id,
            ROLE_ACTORS["arm"],
            logical_time,
            version=2,
            under_lease=lease_ref(world["executive_lease"]),
        )
        task_payload = copy.deepcopy(task["payload"])
        task_payload["dependency_node_ids"] = ["TASK-CANDIDATE-B"]
        task = domain_record(
            "task-node",
            "m1a-task-node-1",
            "TASK-CANDIDATE-A",
            task_payload,
            command_id,
            ROLE_ACTORS["arm"],
            logical_time,
            version=2,
            under_lease=lease_ref(world["executive_lease"]),
        )
        tasks = [task, second]
        edges = [
            {"from_node_id": "TASK-CANDIDATE-A", "to_node_id": "TASK-CANDIDATE-B"},
            {"from_node_id": "TASK-CANDIDATE-B", "to_node_id": "TASK-CANDIDATE-A"},
        ]
    elif mutation == "write-conflict":
        second_payload = copy.deepcopy(task_payload)
        second_payload["semantic_definition_digest"] = h("conflicting-task")
        second = domain_record(
            "task-node",
            "m1a-task-node-1",
            "TASK-CANDIDATE-B",
            second_payload,
            command_id,
            ROLE_ACTORS["arm"],
            logical_time,
            version=2,
            under_lease=lease_ref(world["executive_lease"]),
        )
        tasks = [task, second]
    task_refs = sorted([object_ref(item) for item in tasks], key=lambda item: item["id"])
    edges = sorted(edges, key=lambda item: (item["from_node_id"], item["to_node_id"]))
    plan = domain_record(
        "plan-revision",
        "m1a-plan-revision-1",
        "PLAN-CANDIDATE",
        {
            **copy.deepcopy(world["plan"]["payload"]),
            "prior_plan_ref": object_ref(world["plan"]),
            "trigger": "replan",
            "task_node_refs": task_refs,
            "dependency_edges": edges,
            "graph_digest": digest({"task_node_refs": task_refs, "dependency_edges": edges}),
            "budget_limits": task_payload["budget_limits"],
            "write_resource_paths": task_payload["write_resource_paths"],
            "change_rationale_digest": h(f"candidate-{mutation}"),
        },
        command_id,
        ROLE_ACTORS["arm"],
        logical_time,
        version=2,
        under_lease=lease_ref(world["executive_lease"]),
    )
    transition = domain_record(
        "plan-transition",
        "m1a-plan-transition-1",
        "TRANSITION-CANDIDATE",
        {
            "from_plan_ref": object_ref(world["plan"]),
            "to_plan_ref": object_ref(plan),
            "trigger_evidence_digests": [h(f"trigger-{mutation}")],
            "dispositions": [],
            "executive_lease_ref": lease_ref(world["executive_lease"]),
            "expected_goal_fence_epoch": world["goal"]["payload"]["fence_epoch"],
            "checkpoint_ref": None,
        },
        command_id,
        ROLE_ACTORS["arm"],
        logical_time,
        version=2,
        under_lease=lease_ref(world["executive_lease"]),
    )
    return {"plan_revision": plan, "plan_transition": transition, "task_nodes": tasks}


def setup_case(
    fixture_id: str,
    case_id: str,
    description: str,
    through: str,
    *,
    gate_disposition: str = "pass",
    two_nodes: bool = False,
) -> tuple[Session, dict]:
    session = Session(fixture_id, case_id, description)
    world = add_standard_setup(
        session,
        through,
        gate_disposition=gate_disposition,
        two_nodes=two_nodes,
    )
    session.promote_current_to_initial()
    return session, world


def node_tuple(record: dict) -> dict:
    payload = record["payload"]
    return {
        "node_id": record["id"],
        "node_version": record["version"],
        "node_digest": record["content_digest"],
        "semantic_definition_digest": payload["semantic_definition_digest"],
        "output_schema_digest": payload["output_schema_digest"],
        "dependency_node_ids": payload["dependency_node_ids"],
        "input_digests": payload["input_digests"],
        "source_digests": payload["source_digests"],
        "read_resource_paths": payload["read_resource_paths"],
        "write_resource_paths": payload["write_resource_paths"],
        "effect_keys": payload["effect_keys"],
        "authority_ids": payload["authority_ids"],
        "capability_ids": payload["capability_ids"],
        "allowed_action_ids": payload["allowed_action_ids"],
        "prohibition_ids": payload["prohibition_ids"],
        "route_ids": payload["route_ids"],
        "route_capability_ids": payload["route_capability_ids"],
        "account_class_ids": payload["account_class_ids"],
        "capacity_pool_ids": payload["capacity_pool_ids"],
        "privacy_class_id": payload["privacy_class_id"],
        "egress_class_id": payload["egress_class_id"],
        "authority_policy_digest": payload["authority_policy_ref"]["content_digest"],
        "privacy_policy_digest": payload["privacy_policy_ref"]["content_digest"],
        "egress_policy_digest": payload["egress_policy_ref"]["content_digest"],
        "budget_limits": payload["budget_limits"],
        "gate_requirements": payload["gate_requirements"],
        "retry_policy_digest": payload["retry_policy_ref"]["content_digest"],
        "verifier_policy_digest": payload["verifier_policy_ref"]["content_digest"],
        "constitution_policy_digest": payload["constitution_policy_ref"]["content_digest"],
        "terminal_contribution_digest": payload["terminal_contribution_digest"],
        "retry_maximum": payload["retry_maximum"],
    }


def disposition_event_type(disposition: dict) -> str:
    object_type = disposition["object_ref"]["object_type"]
    if object_type == "work-packet":
        return "PacketFenced"
    if object_type in ("work-lease", "executive-lease"):
        return "LeaseFenced"
    if object_type == "effect-observation":
        return "EffectDisposed"
    if object_type == "evidence":
        return "EvidenceDisposed"
    return "PlanItemDisposed"


def disposition_domain(
    session: Session, world: dict, command_id: str, disposition: dict
) -> dict:
    return domain_record(
        "disposition",
        "m1a-disposition-1",
        "DISPOSITION-" + digest({"command_id": command_id, "disposition": disposition})[:32],
        disposition,
        command_id,
        "KERNEL-M1A",
        session.state["last_event_sequence"] + 1,
        under_lease=None,
    )


def plan_verifier_record(
    session: Session,
    world: dict,
    command_id: str,
    disposition: str,
    exception: dict | None,
    *,
    gate_digests: list[str] | None = None,
) -> dict:
    return domain_record(
        "plan-verifier-decision",
        "m1a-plan-verifier-decision-1",
        "PLAN-VERIFIER-DECISION-EXPLICIT",
        {
            "goal_ref": object_ref(world["goal"]),
            "plan_ref": object_ref(world["plan"]),
            "candidate_digest": h("candidate-one"),
            "event_log_digest": digest([
                {"sequence": event["sequence"], "event_id": event["event_id"], "content_digest": event["content_digest"]}
                for event in [*session.initial_events, *session.events]
            ]),
            "gate_result_digests": gate_digests if gate_digests is not None else [world["gate_result"]["content_digest"]],
            "evidence_digests": [h("evidence-one")],
            "verifier_policy_ref": session.policy_ref("verifier"),
            "constitution_policy_ref": session.policy_ref("constitution"),
            "independence": {
                "model_family": "gpt-family",
                "provider": "openai",
                "host": "local",
                "session": "fixture",
                "evidence_store": "fixture",
                "implementation_actor_id": "ACTOR-IMPLEMENTER",
                "verifier_actor_id": ROLE_ACTORS["verifier"],
                "missing_dimensions": ["account"] if disposition == "downgraded-pass" else [],
            },
            "disposition": disposition,
            "assurance_grade": "downgraded" if disposition == "downgraded-pass" else ("full" if disposition == "pass" else "none"),
            "owner_exception_ref": object_ref(exception) if exception else None,
            "dissent_digest": None,
            "limitation_digests": [h("same-family-limit")] if disposition == "downgraded-pass" else [],
        },
        command_id,
        ROLE_ACTORS["verifier"],
        session.state["last_event_sequence"] + 1,
    )


def blocker_record(session: Session, world: dict, command_id: str, *, kind="gate", deferred=False) -> dict:
    return domain_record(
        "blocker",
        "m1a-blocker-1",
        "BLOCKER-M1A-1",
        {
            "blocked_object_ref": object_ref(world["task"]),
            "kind": kind,
            "evidence_digests": [h("blocker-evidence")],
            "required_actor_id": ROLE_ACTORS["head"],
            "allowed_recovery_ids": ["RECOVERY-REPLAN"],
            "retry_after_observation_ref": object_ref(world["capacity"]) if deferred else None,
            "failure_fingerprint_digest": h("failure-fingerprint"),
            "state": "deferred" if deferred else "open",
        },
        command_id,
        ROLE_ACTORS["arm"],
        session.state["last_event_sequence"] + 1,
        under_lease=lease_ref(world["executive_lease"]),
    )


def escalation_record(session: Session, world: dict, blocker: dict, command_id: str) -> dict:
    return domain_record(
        "escalation",
        "m1a-escalation-1",
        "ESCALATION-M1A-1",
        {
            "source_blocker_ref": object_ref(blocker),
            "target_role": "head",
            "failure_history_digests": [h("failure-history")],
            "requested_decision": "Choose a bounded recovery or stop.",
            "option_digests": [h("option-stop")],
            "recommendation_digest": h("recommend-stop"),
            "frozen_scope_digest": h("frozen-scope"),
            "state": "raised",
        },
        command_id,
        ROLE_ACTORS["arm"],
        session.state["last_event_sequence"] + 1,
        under_lease=lease_ref(world["executive_lease"]),
    )


def retry_payload_and_packet(session: Session, world: dict, command_id: str, *, next_attempt: int = 2):
    delta = novelty_delta()
    remaining = {**LIMIT_BUDGET, "attempts": max(0, 2 - next_attempt)}
    decision = domain_record(
        "retry-decision",
        "m1a-retry-decision-1",
        f"RETRY-DECISION-{next_attempt}",
        {
            "goal_ref": object_ref(world["goal"]),
            "plan_ref": object_ref(world["plan"]),
            "task_ref": object_ref(world["task"]),
            "failed_gate_result_ref": object_ref(world["gate_result"]),
            "prior_work_packet_ref": object_ref(world["packet"]),
            "novelty_delta": delta,
            "novelty_delta_digest": delta["delta_digest"],
            "unchanged_binding_digest": h("unchanged-binding"),
            "next_attempt": next_attempt,
            "remaining_budget": remaining,
            "retry_maximum": 2,
            "disposition": "admitted" if next_attempt <= 2 else "exhausted",
        },
        command_id,
        ROLE_ACTORS["arm"],
        session.state["last_event_sequence"] + 1,
        under_lease=lease_ref(world["executive_lease"]),
    )
    packet_payload = copy.deepcopy(world["packet"]["payload"])
    packet_payload["supersedes_packet_ref"] = object_ref(world["packet"])
    packet_payload["attempt"] = next_attempt
    seed = {
        "command_id": command_id,
        "task_ref": object_ref(world["task"]),
        "attempt": next_attempt,
        "work_lease_ref": packet_payload["work_lease_ref"],
        "route_assignment_ref": packet_payload["route_assignment_ref"],
        "budget_reservation_ref": packet_payload["budget_reservation_ref"],
        "checkpoint_ref": packet_payload["checkpoint_ref"],
    }
    packet = domain_record(
        "work-packet",
        "m1a-work-packet-1",
        "PACKET-" + digest(seed)[:32],
        packet_payload,
        command_id,
        "KERNEL-M1A",
        session.state["last_event_sequence"] + 1,
        under_lease=lease_ref(world["executive_lease"]),
    )
    return decision, packet


def accept_retry(session: Session, world: dict) -> tuple[dict, dict]:
    box = {}

    def payload_builder(command_id):
        decision, packet = retry_payload_and_packet(session, world, command_id)
        box["decision"] = decision
        box["packet"] = packet
        return decision

    session.accept(
        "propose-retry",
        "arm",
        payload_builder,
        lambda cid, payload: [
            ("RetryAdmitted", box["decision"], []),
            ("WorkPacketDerived", box["packet"], []),
        ],
        lease=lease_ref(world["executive_lease"]),
        goal=object_ref(world["goal"]),
        plan=object_ref(world["plan"]),
    )
    world["packet"] = box["packet"]
    world["retry"] = box["decision"]
    return box["decision"], box["packet"]


def build_fixture_001() -> list[dict]:
    session = Session("F-M1A-001", "happy", "Complete deterministic planning path.")
    add_standard_setup(session, "verifier")
    return [session.fixture_case()]


def build_fixture_002() -> list[dict]:
    session = Session(
        "F-M1A-002", "decode",
        "Missing, duplicate, and bounded inputs decode-fail; invalid authority refuses.",
    )
    for raw in (
        '{"command_schema_version":"m1a-command-1"}',
        '{"object_type":"goal-spec"}',
        '{"acceptance_gate_ids":[]}',
        '{"policy_id":"POLICY-UNKNOWN"}',
    ):
        session.add_decode_failure(raw, "E-SCHEMA-MISSING-FIELD")
    session.add_decode_failure('{"duplicate":1,"duplicate":2}', "E-SCHEMA-DUPLICATE")
    session.add_decode_failure("[" * 18 + "0" + "]" * 18, "E-SCHEMA-BOUND")

    def payload(command_id):
        return domain_record(
            "owner-intent", "m1a-owner-intent-1", "INTENT-UNKNOWN-AUTH",
            {
                "intent_text": "Unknown authority must refuse.",
                "source_kind": "owner-prompt",
                "source_digest": h("unknown-auth-intent"),
                "privacy_policy_ref": session.policy_ref("privacy-egress"),
                "supersedes_ref": None,
            },
            command_id, ROLE_ACTORS["owner"], 1,
        )

    session.refuse(
        "record-owner-intent", "owner", payload, "E-AUTH-MISSING", include_authority=False
    )
    session.refuse(
        "record-owner-intent", "worker", payload, "E-AUTH-ROLE"
    )
    return [session.fixture_case()]


def build_fixture_003() -> list[dict]:
    cases = []
    for mutation, error in (
        ("capability-widen", "E-SCOPE-WIDEN"),
        ("path-widen", "E-SCOPE-WIDEN"),
        ("route-widen", "E-SCOPE-WIDEN"),
        ("egress-widen", "E-SCOPE-WIDEN"),
        ("budget-widen", "E-BUDGET-WIDEN"),
    ):
        session, world = setup_case(
            "F-M1A-003", mutation, f"Reject {mutation} descendant widening.", "plan"
        )
        session.refuse(
            "propose-plan-revision",
            "arm",
            lambda cid, m=mutation: candidate_plan_payload(session, world, cid, mutation=m),
            error,
            lease=lease_ref(world["executive_lease"]),
            goal=object_ref(world["goal"]),
            plan=object_ref(world["plan"]),
        )
        cases.append(session.fixture_case())
    return cases


def build_fixture_004() -> list[dict]:
    cases = []
    for mutation, error, ids, edges in (
        (
            "cycle", "E-DAG-CYCLE", ["TASK-CANDIDATE-A", "TASK-CANDIDATE-B"],
            [
                {"from_node_id": "TASK-CANDIDATE-A", "to_node_id": "TASK-CANDIDATE-B"},
                {"from_node_id": "TASK-CANDIDATE-B", "to_node_id": "TASK-CANDIDATE-A"},
            ],
        ),
        ("missing-dependency", "E-DAG-DEPENDENCY", ["TASK-MISSING"], []),
    ):
        session, world = setup_case(
            "F-M1A-004", mutation, f"Reject graph with {mutation}.", "plan"
        )
        session.refuse(
            "propose-plan-revision",
            "arm",
            lambda cid, m=mutation: candidate_plan_payload(session, world, cid, mutation=m),
            error,
            lease=lease_ref(world["executive_lease"]),
            goal=object_ref(world["goal"]),
            plan=object_ref(world["plan"]),
            witness=error_witness(error, object_ids=ids, edges=edges),
        )
        cases.append(session.fixture_case())
    return cases


def build_fixture_005() -> list[dict]:
    session, world = setup_case(
        "F-M1A-005", "amend", "Atomic amendment retains one node and invalidates another.",
        "verifier", two_nodes=True,
    )
    def prior_effect(command_id):
        record = domain_record(
            "effect-observation", "m1a-effect-observation-1", "EFFECT-OBS-AMENDMENT",
            {
                "effect_id": "EFFECT-ID-AMENDMENT", "effect_key": "EFFECT-SYNTHETIC",
                "work_packet_ref": object_ref(world["packet"]),
                "idempotency_key_digest": h("amendment-effect-idempotency"),
                "dispatch_state": "dispatched", "receipt_digest": h("effect-failure-receipt"),
                "provider_operation_id_digest": h("effect-operation"),
                "observation": "observed-failure", "quarantine": False,
            },
            command_id, ROLE_ACTORS["kernel-fixture-gate"],
            session.state["last_event_sequence"] + 1,
        )
        world["effect"] = record
        return record

    session.accept(
        "record-effect-observation", "kernel-fixture-gate", prior_effect,
        lambda cid, payload: [("EffectObservationRecorded", payload, [])],
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    session.promote_current_to_initial()
    box = {}

    def payload_builder(command_id):
        logical_time = session.state["last_event_sequence"] + 1
        new_goal_payload = copy.deepcopy(world["goal"]["payload"])
        new_goal_payload["fence_epoch"] = 2
        new_goal_payload["outcome"] = "Reach the amended deterministic synthetic gate."
        new_goal = domain_record(
            "goal-spec", "m1a-goal-spec-1", "GOAL-M1A", new_goal_payload, command_id,
            ROLE_ACTORS["owner"], logical_time, version=2,
        )
        tasks = []
        for key, disposition in (("task", "retain-terminal"), ("task_b", "invalidate")):
            old = world[key]
            task_payload = copy.deepcopy(old["payload"])
            task_payload["plan_ref"] = {
                "object_type": "plan-revision", "id": "PLAN-M1A", "version": 2
            }
            if key == "task_b":
                task_payload["semantic_definition_digest"] = h("amended-task-b")
            tasks.append(domain_record(
                "task-node", "m1a-task-node-1", old["id"], task_payload, command_id,
                ROLE_ACTORS["arm"], logical_time, version=2,
                under_lease=lease_ref(world["executive_lease"]),
            ))
        dispositions = [
            {
                "object_ref": object_ref(world["effect"]),
                "disposition": "cancel",
                "replacement_ref": None,
                "reason_digest": h("dispose-effect"),
            },
            {
                "object_ref": {
                    "object_type": "evidence", "id": "EVIDENCE-ONE", "version": 1,
                    "content_digest": h("evidence-one"),
                },
                "disposition": "invalidate",
                "replacement_ref": None,
                "reason_digest": h("dispose-evidence"),
            },
            {
                "object_ref": object_ref(world["executive_lease"]),
                "disposition": "fence",
                "replacement_ref": None,
                "reason_digest": h("fence-executive-lease"),
            },
            {
                "object_ref": object_ref(world["task"]),
                "disposition": "retain-terminal",
                "replacement_ref": object_ref(tasks[0]),
                "reason_digest": h("retain-compatible-a"),
            },
            {
                "object_ref": object_ref(world["task_b"]),
                "disposition": "invalidate",
                "replacement_ref": object_ref(tasks[1]),
                "reason_digest": h("invalidate-b"),
            },
            {
                "object_ref": object_ref(world["plan"]),
                "disposition": "supersede",
                "replacement_ref": None,
                "reason_digest": h("supersede-plan"),
            },
            {
                "object_ref": object_ref(world["work_lease"]),
                "disposition": "fence",
                "replacement_ref": None,
                "reason_digest": h("fence-work-lease"),
            },
            {
                "object_ref": object_ref(world["packet"]),
                "disposition": "fence",
                "replacement_ref": None,
                "reason_digest": h("fence-work-packet"),
            },
        ]
        dispositions.sort(key=lambda item: (
            item["object_ref"]["object_type"], item["object_ref"]["id"], item["object_ref"]["version"]
        ))
        task_refs = sorted([object_ref(item) for item in tasks], key=lambda item: item["id"])
        edges = [{"from_node_id": "TASK-M1A-A", "to_node_id": "TASK-M1A-B"}]
        plan_payload = copy.deepcopy(world["plan"]["payload"])
        plan_payload.update({
            "goal_ref": object_ref(new_goal),
            "prior_plan_ref": object_ref(world["plan"]),
            "trigger": "amendment",
            "task_node_refs": task_refs,
            "dependency_edges": edges,
            "graph_digest": digest({"task_node_refs": task_refs, "dependency_edges": edges}),
            "change_rationale_digest": h("owner-amendment"),
            "dispositions": dispositions,
        })
        plan = domain_record(
            "plan-revision", "m1a-plan-revision-1", "PLAN-M1A", plan_payload,
            command_id, ROLE_ACTORS["arm"], logical_time, version=2,
            under_lease=lease_ref(world["executive_lease"]),
        )
        transition = domain_record(
            "plan-transition", "m1a-plan-transition-1", "TRANSITION-M1A-2",
            {
                "from_plan_ref": object_ref(world["plan"]),
                "to_plan_ref": object_ref(plan),
                "trigger_evidence_digests": [h("owner-amendment")],
                "dispositions": dispositions,
                "executive_lease_ref": lease_ref(world["executive_lease"]),
                "expected_goal_fence_epoch": 2,
                "checkpoint_ref": None,
            },
            command_id, ROLE_ACTORS["arm"], logical_time, version=2,
            under_lease=lease_ref(world["executive_lease"]),
        )
        compat = {
            "compatibility_schema_version": "compatibility-input-1",
            "old_goal_ref": {
                "goal_id": world["goal"]["id"], "version": 1,
                "content_digest": world["goal"]["content_digest"], "fence_epoch": 1,
            },
            "new_goal_ref": {
                "goal_id": new_goal["id"], "version": 2,
                "content_digest": new_goal["content_digest"], "fence_epoch": 2,
            },
            "old_node": node_tuple(world["task"]),
            "new_node": node_tuple(tasks[0]),
            "replacement_node_id": tasks[0]["id"],
            "replacement_node_digest": tasks[0]["content_digest"],
            "prior_result": {
                "state": "complete", "candidate_digest": h("candidate-one"),
                "evidence_digests": [h("evidence-one")],
                "gate_result_digests": [world["gate_result"]["content_digest"]],
                "plan_verifier_decision_digest": world["verifier"]["content_digest"],
                "assurance_grade": "full",
            },
            "prior_effect": {
                "state": "none", "effect_id": None, "intent_digest": None, "receipt_digest": None,
            },
            "consumed_budget": ZERO_BUDGET,
        }
        arm_candidate = digest({
            "replacement_plan_revision": plan,
            "plan_transition": transition,
            "task_nodes": tasks,
        })
        arm_auth = session._authority(
            "CMD-ARM-ATTEST-M1A", "propose-plan-revision", "arm", arm_candidate
        )
        amendment = domain_record(
            "goal-spec-amendment", "m1a-goal-spec-amendment-1", "AMENDMENT-M1A-1",
            {
                "old_goal_ref": object_ref(world["goal"]),
                "new_goal_ref": object_ref(new_goal),
                "changed_field_paths": ["outcome"],
                "rationale_digest": h("owner-amendment"),
                "owner_authority_attestation_id": "AUTH-" + command_id[4:],
                "effective_fence_epoch": 2,
                "checkpoint_rule": "current-immediate",
                "compatibility_inputs": [compat],
                "dispositions": dispositions,
                "plan_transition_ref": object_ref(transition),
            },
            command_id, ROLE_ACTORS["owner"], logical_time, version=1,
        )
        box.update({"goal": new_goal, "tasks": tasks, "plan": plan, "transition": transition, "amendment": amendment})
        return {
            "new_goal_spec": new_goal,
            "amendment": amendment,
            "replacement_plan_revision": plan,
            "plan_transition": transition,
            "task_nodes": tasks,
            "arm_proposal_attestation_id": arm_auth["attestation_id"],
        }

    def event_builder(command_id, payload):
        events = [
            ("GoalSpecAmended", box["amendment"], [box["goal"]]),
            ("PlanRevisionAdmitted", box["plan"], [box["transition"], *box["tasks"]]),
        ]
        for disposition in box["amendment"]["payload"]["dispositions"]:
            record = disposition_domain(session, world, command_id, disposition)
            events.append((disposition_event_type(disposition), record, []))
        return events

    session.accept(
        "amend-goal-spec", "owner", payload_builder, event_builder,
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    return [session.fixture_case()]


def build_fixture_006() -> list[dict]:
    cases = []
    for case_id, error in (
        ("stale-goal", "E-STALE-GOAL"),
        ("stale-lease", "E-STALE-LEASE"),
        ("stale-plan", "E-STALE-PLAN"),
    ):
        session, world = setup_case("F-M1A-006", case_id, f"Reject {case_id} packet result.", "packet")
        original_work_lease = world["work_lease"]
        if error == "E-STALE-LEASE":
            def replace_lease(command_id):
                payload = copy.deepcopy(original_work_lease["payload"])
                payload.update({
                    "supersedes_lease_ref": lease_ref(original_work_lease),
                    "lease_epoch": 2,
                    "nonce_digest": h("work-lease-two"),
                })
                new_lease = domain_record(
                    "work-lease", "m1a-work-lease-1", "LEASE-WORK-2", payload,
                    command_id, "KERNEL-M1A", session.state["last_event_sequence"] + 1,
                )
                world["work_lease"] = new_lease
                return {"old_lease_ref": lease_ref(original_work_lease), "new_lease": new_lease}

            session.accept(
                "replace-work-lease", "head", replace_lease,
                lambda cid, payload: [("WorkLeaseReplaced", payload["new_lease"], [])],
                goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
            )

        def payload(command_id):
            return domain_record(
                "worker-result", "m1a-worker-result-1", f"RESULT-{case_id.upper()}",
                {
                    "work_packet_ref": object_ref(world["packet"]),
                    "candidate_digest": h(case_id), "evidence_digests": [h("evidence-stale")],
                    "output_digest": h("output-stale"), "observed_effect_ref": None,
                    "disposition": "submitted",
                },
                command_id, ROLE_ACTORS["worker"], session.state["last_event_sequence"] + 1,
            )

        goal_ref = object_ref(world["goal"])
        plan_ref = object_ref(world["plan"])
        lease = lease_ref(world["work_lease"])
        if error == "E-STALE-GOAL":
            goal_ref = {**goal_ref, "version": goal_ref["version"] + 1}
        elif error == "E-STALE-LEASE":
            lease = lease_ref(original_work_lease)
        else:
            plan_ref = {**plan_ref, "version": plan_ref["version"] + 1}
        session.refuse(
            "submit-worker-result", "worker", payload, error, lease=lease,
            goal=goal_ref, plan=plan_ref,
        )
        cases.append(session.fixture_case())
    return cases


def build_fixture_007() -> list[dict]:
    session, world = setup_case(
        "F-M1A-007", "novel", "Admit one typed novel retry at attempt two.", "gate",
        gate_disposition="fail",
    )
    accept_retry(session, world)
    return [session.fixture_case()]


def build_fixture_008() -> list[dict]:
    session, world = setup_case(
        "F-M1A-008", "repeated", "Reject a previously consumed novelty delta.", "gate",
        gate_disposition="fail",
    )
    accept_retry(session, world)
    session.promote_current_to_initial()
    session.refuse(
        "propose-retry", "arm",
        lambda cid: retry_payload_and_packet(session, world, cid)[0],
        "E-RETRY-NONNOVEL",
        lease=lease_ref(world["executive_lease"]), goal=object_ref(world["goal"]),
        plan=object_ref(world["plan"]),
    )
    return [session.fixture_case()]


def build_fixture_009() -> list[dict]:
    session, world = setup_case(
        "F-M1A-009", "exhausted", "Retry exhaustion raises a blocker and escalation.", "gate",
        gate_disposition="fail",
    )
    session.refuse(
        "propose-retry", "arm",
        lambda cid: retry_payload_and_packet(session, world, cid, next_attempt=3)[0],
        "E-RETRY-EXHAUSTED", lease=lease_ref(world["executive_lease"]),
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    box = {}
    session.accept(
        "raise-blocker", "arm",
        lambda cid: box.setdefault("blocker", blocker_record(session, world, cid)),
        lambda cid, payload: [("BlockerRaised", payload, [])],
        lease=lease_ref(world["executive_lease"]), goal=object_ref(world["goal"]),
        plan=object_ref(world["plan"]),
    )
    session.accept(
        "raise-escalation", "arm",
        lambda cid: escalation_record(session, world, box["blocker"], cid),
        lambda cid, payload: [("EscalationRaised", payload, [])],
        lease=lease_ref(world["executive_lease"]), goal=object_ref(world["goal"]),
        plan=object_ref(world["plan"]),
    )
    return [session.fixture_case()]


def build_fixture_010() -> list[dict]:
    cases = []
    for case_id, error in (
        ("gate-missing", "E-GATE-MISSING"),
        ("verifier-missing", "E-VERIFIER-MISSING"),
    ):
        session, world = setup_case(
            "F-M1A-010", case_id, f"{case_id} blocks terminal completion.", "worker"
        )

        def payload(command_id):
            return plan_verifier_record(session, world, command_id, "pass", None, gate_digests=[])

        session.refuse(
            "submit-plan-verifier-decision", "verifier", payload, error,
            goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
        )
        cases.append(session.fixture_case())
    return cases


def build_fixture_011() -> list[dict]:
    session, world = setup_case(
        "F-M1A-011", "downgrade", "Owner-bound verifier downgrade remains explicitly downgraded.",
        "gate",
    )
    box = {}

    def exception_payload(command_id):
        record = domain_record(
            "owner-verifier-exception",
            "m1a-owner-verifier-exception-1",
            "OWNER-VERIFIER-EXCEPTION-1",
            {
                "goal_ref": object_ref(world["goal"]),
                "plan_ref": object_ref(world["plan"]),
                "candidate_digest": h("candidate-one"),
                "verifier_policy_ref": session.policy_ref("verifier"),
                "constitution_policy_ref": session.policy_ref("constitution"),
                "missing_dimensions": ["account"],
                "reason_digest": h("risk-approved-same-family"),
                "owner_authority_attestation_id": "AUTH-" + command_id[4:],
                "issued_logical_time": session.state["last_event_sequence"] + 1,
                "expires_logical_time": 1000,
            },
            command_id,
            ROLE_ACTORS["owner"],
            session.state["last_event_sequence"] + 1,
        )
        box["exception"] = record
        return record

    session.accept(
        "record-owner-verifier-exception", "owner", exception_payload,
        lambda cid, payload: [("OwnerVerifierExceptionRecorded", payload, [])],
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    session.accept(
        "submit-plan-verifier-decision", "verifier",
        lambda cid: plan_verifier_record(session, world, cid, "downgraded-pass", box["exception"]),
        lambda cid, payload: [("PlanVerifierDecisionRecorded", payload, [])],
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    return [session.fixture_case()]


def build_fixture_012() -> list[dict]:
    session, world = setup_case(
        "F-M1A-012", "capacity", "Capacity exhaustion defers without spend widening.", "packet"
    )

    def unavailable(command_id):
        record = domain_record(
            "capacity-observation", "m1a-capacity-observation-1", "CAPACITY-OBS-2",
            {
                "route_id": "ROUTE-INCLUDED", "account_class_id": "ACCOUNT-INCLUDED",
                "capacity_pool_id": "CAPACITY-INCLUDED", "spend_class": "included",
                "available": False, "remaining_units": 0,
                "observation_digest": h("capacity-exhausted"),
            },
            command_id, ROLE_ACTORS["kernel-fixture-gate"],
            session.state["last_event_sequence"] + 1,
        )
        world["capacity"] = record
        return record

    session.accept(
        "record-capacity-observation", "kernel-fixture-gate", unavailable,
        lambda cid, payload: [("CapacityObservationRecorded", payload, [])],
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    box = {}
    session.accept(
        "raise-blocker", "arm",
        lambda cid: box.setdefault("blocker", blocker_record(session, world, cid, kind="capacity", deferred=True)),
        lambda cid, payload: [("BlockerRaised", payload, [])],
        lease=lease_ref(world["executive_lease"]), goal=object_ref(world["goal"]),
        plan=object_ref(world["plan"]),
    )

    def replacement(command_id):
        route_payload = copy.deepcopy(world["route"]["payload"])
        route_payload.update({
            "route_id": "ROUTE-METERED",
            "supersedes_route_ref": object_ref(world["route"]),
            "capacity_observation_ref": object_ref(world["capacity"]),
        })
        route = domain_record(
            "route-assignment", "m1a-route-assignment-1", "ROUTE-ASSIGNMENT-2",
            route_payload, command_id, "KERNEL-M1A",
            session.state["last_event_sequence"] + 1,
        )
        return {
            "old_route_ref": object_ref(world["route"]), "new_route": route,
            "checkpoint_ref": {
                "object_type": "checkpoint", "id": "CHECKPOINT-NOT-REACHED", "version": 1,
                "content_digest": h("checkpoint-not-reached"),
            },
            "expected_new_packet_digest": h("refused-metered-packet"),
        }

    session.refuse(
        "replace-route", "head", replacement, "E-ROUTE-SPEND",
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    return [session.fixture_case()]


def build_fixture_013() -> list[dict]:
    session, world = setup_case(
        "F-M1A-013", "replace", "Checkpointed route replacement fences the prior packet.", "packet"
    )
    snapshot = copy.deepcopy(session.state)
    box = {}

    def checkpoint_builder(command_id):
        record = checkpoint_payload(session, world, command_id)
        box["checkpoint"] = record
        return record

    session.accept(
        "record-checkpoint", "kernel-fixture-gate", checkpoint_builder,
        lambda cid, payload: [("CheckpointRecorded", payload, [])],
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )

    def replacement(command_id):
        logical_time = session.state["last_event_sequence"] + 1
        route_payload = copy.deepcopy(world["route"]["payload"])
        route_payload.update({
            "route_id": "ROUTE-ZERO",
            "supersedes_route_ref": object_ref(world["route"]),
            "assigned_logical_time": logical_time,
        })
        route = domain_record(
            "route-assignment", "m1a-route-assignment-1", "ROUTE-ASSIGNMENT-2",
            route_payload, command_id, "KERNEL-M1A", logical_time,
            under_lease=lease_ref(world["executive_lease"]),
        )
        packet_payload = copy.deepcopy(world["packet"]["payload"])
        packet_payload.update({
            "supersedes_packet_ref": object_ref(world["packet"]),
            "route_assignment_ref": object_ref(route),
            "checkpoint_ref": object_ref(box["checkpoint"]),
        })
        seed = {
            "command_id": command_id, "task_ref": object_ref(world["task"]),
            "attempt": packet_payload["attempt"], "work_lease_ref": packet_payload["work_lease_ref"],
            "route_assignment_ref": object_ref(route),
            "budget_reservation_ref": packet_payload["budget_reservation_ref"],
            "checkpoint_ref": object_ref(box["checkpoint"]),
        }
        packet = domain_record(
            "work-packet", "m1a-work-packet-1", "PACKET-" + digest(seed)[:32],
            packet_payload, command_id, "KERNEL-M1A", logical_time,
            under_lease=lease_ref(world["executive_lease"]),
        )
        box["new_route"] = route
        box["new_packet"] = packet
        return {
            "old_route_ref": object_ref(world["route"]), "new_route": route,
            "checkpoint_ref": object_ref(box["checkpoint"]),
            "expected_new_packet_digest": packet["content_digest"],
        }

    session.accept(
        "replace-route", "head", replacement,
        lambda cid, payload: [
            ("RouteAssignmentReplaced", box["new_route"], []),
            ("WorkPacketDerived", box["new_packet"], []),
        ],
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    session.replay_cases.append({
        "replay_id": "REPLAY-CHECKPOINT-ROUTE",
        "checkpoint": {"checkpoint_record": box["checkpoint"], "projection_snapshot": snapshot},
        "commands": session.commands,
        "receipts": session.receipts,
        "event_inputs": [canonical_bytes(event).decode("utf-8") for event in session.events],
        "expected_disposition": "accepted",
        "primary_error": None,
        "expected_projection_digest": session.state["content_digest"],
    })
    return [session.fixture_case()]


def build_fixture_014() -> list[dict]:
    session, world = setup_case(
        "F-M1A-014", "pause", "Current-immediate PAUSE refuses subsequent planning.", "packet"
    )

    def pause(command_id):
        return domain_record(
            "pause-directive", "m1a-pause-directive-1", "PAUSE-DIRECTIVE-1",
            {
                "pause_policy_ref": session.policy_ref("pause"), "mode": "current-immediate",
                "new_pause_epoch": 1, "reason_digest": h("owner-pause"),
            },
            command_id, ROLE_ACTORS["owner"], session.state["last_event_sequence"] + 1,
        )

    session.accept(
        "apply-pause", "owner", pause,
        lambda cid, payload: [("PauseApplied", payload, [])],
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    session.refuse(
        "propose-plan-revision", "arm",
        lambda cid: candidate_plan_payload(session, world, cid), "E-PAUSED",
        lease=lease_ref(world["executive_lease"]), goal=object_ref(world["goal"]),
        plan=object_ref(world["plan"]),
    )
    return [session.fixture_case()]


def build_fixture_015() -> list[dict]:
    session, world = setup_case(
        "F-M1A-015", "future", "Future PAUSE values round-trip but are not operative.", "goal"
    )

    def future_pause(command_id):
        return domain_record(
            "pause-directive", "m1a-pause-directive-1", "PAUSE-DIRECTIVE-FUTURE",
            {
                "pause_policy_ref": session.policy_ref("pause"), "mode": "checkpoint",
                "new_pause_epoch": 1, "reason_digest": h("future-pause"),
            },
            command_id, ROLE_ACTORS["owner"], session.state["last_event_sequence"] + 1,
        )

    session.refuse(
        "apply-pause", "owner", future_pause, "E-POLICY-UNKNOWN",
        goal=object_ref(world["goal"]),
    )
    return [session.fixture_case()]


def build_fixture_016() -> list[dict]:
    session, world = setup_case(
        "F-M1A-016", "ambiguous", "Ambiguous effect quarantines and blocks retry.", "gate",
        gate_disposition="fail",
    )
    box = {}

    def effect(command_id):
        record = domain_record(
            "effect-observation", "m1a-effect-observation-1", "EFFECT-OBS-1",
            {
                "effect_id": "EFFECT-ID-1", "effect_key": "EFFECT-SYNTHETIC",
                "work_packet_ref": object_ref(world["packet"]),
                "idempotency_key_digest": h("effect-idempotency"),
                "dispatch_state": "dispatched", "receipt_digest": None,
                "provider_operation_id_digest": None, "observation": "ambiguous",
                "quarantine": True,
            },
            command_id, ROLE_ACTORS["kernel-fixture-gate"],
            session.state["last_event_sequence"] + 1,
        )
        box["effect"] = record
        return record

    session.accept(
        "record-effect-observation", "kernel-fixture-gate", effect,
        lambda cid, payload: [("EffectObservationRecorded", payload, [])],
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    session.refuse(
        "propose-retry", "arm", lambda cid: retry_payload_and_packet(session, world, cid)[0],
        "E-EFFECT-AMBIGUOUS", lease=lease_ref(world["executive_lease"]),
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    return [session.fixture_case()]


def build_fixture_017() -> list[dict]:
    session = Session("F-M1A-017", "idempotency", "Duplicate is exact; conflicting payload refuses.")
    add_standard_setup(session, "intent")
    original_command = copy.deepcopy(session.commands[0])
    original_receipt = copy.deepcopy(session.receipts[0])
    session.commands.append(original_command)
    session.receipts.append(original_receipt)

    def conflict_payload(command_id):
        return domain_record(
            "owner-intent", "m1a-owner-intent-1", "INTENT-M1A-CONFLICT",
            {
                **copy.deepcopy(original_command["payload"]["payload"]),
                "intent_text": "Conflicting payload with reused command ID.",
            },
            command_id, ROLE_ACTORS["owner"], session.state["last_event_sequence"] + 1,
        )

    session.refuse(
        "record-owner-intent", "owner", conflict_payload, "E-IDEMPOTENCY-CONFLICT",
        include_authority=False, disposition="conflict", command_id=original_command["command_id"],
    )
    return [session.fixture_case()]


def build_fixture_018() -> list[dict]:
    session, world = setup_case(
        "F-M1A-018", "replay", "Genesis and checkpoint replay fail closed on corrupt variants.", "packet"
    )
    snapshot = copy.deepcopy(session.state)
    box = {}
    session.accept(
        "record-checkpoint", "kernel-fixture-gate",
        lambda cid: box.setdefault("checkpoint", checkpoint_payload(session, world, cid)),
        lambda cid, payload: [("CheckpointRecorded", payload, [])],
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    all_commands = [*session.initial_commands, *session.commands]
    all_receipts = [*session.initial_receipts, *session.receipts]
    all_events = [*session.initial_events, *session.events]
    valid_inputs = [canonical_bytes(event).decode("utf-8") for event in all_events]
    session.replay_cases.append({
        "replay_id": "REPLAY-GENESIS-VALID", "checkpoint": None,
        "commands": all_commands, "receipts": all_receipts, "event_inputs": valid_inputs,
        "expected_disposition": "accepted", "primary_error": None,
        "expected_projection_digest": session.state["content_digest"],
    })
    session.replay_cases.append({
        "replay_id": "REPLAY-CHECKPOINT-VALID",
        "checkpoint": {"checkpoint_record": box["checkpoint"], "projection_snapshot": snapshot},
        "commands": session.commands, "receipts": session.receipts,
        "event_inputs": [canonical_bytes(event).decode("utf-8") for event in session.events],
        "expected_disposition": "accepted", "primary_error": None,
        "expected_projection_digest": session.state["content_digest"],
    })
    corrupt = copy.deepcopy(all_events)
    corrupt[-1]["content_digest"] = "0" * 64
    gap = all_events[1:]
    unknown = copy.deepcopy(all_events)
    unknown[0]["event_schema_version"] = "m1a-event-2"
    for replay_id, events, error in (
        ("REPLAY-CORRUPT", corrupt, "E-DIGEST-MISMATCH"),
        ("REPLAY-GAP", gap, "E-DIGEST-MISMATCH"),
        ("REPLAY-UNKNOWN", unknown, "E-SCHEMA-UNKNOWN-VERSION"),
    ):
        session.replay_cases.append({
            "replay_id": replay_id, "checkpoint": None,
            "commands": all_commands, "receipts": all_receipts,
            "event_inputs": [canonical_bytes(event).decode("utf-8") for event in events],
            "expected_disposition": "refused", "primary_error": error,
            "expected_projection_digest": None,
        })
    return [session.fixture_case()]


def build_fixture_019() -> list[dict]:
    session, world = setup_case(
        "F-M1A-019", "executive", "Old executive lease cannot propose after replacement.", "plan"
    )
    old_lease = world["executive_lease"]

    def replace(command_id):
        payload = copy.deepcopy(old_lease["payload"])
        payload.update({
            "supersedes_lease_ref": lease_ref(old_lease), "lease_epoch": 2,
            "nonce_digest": h("executive-lease-two"),
        })
        new_lease = domain_record(
            "executive-lease", "m1a-executive-lease-1", "LEASE-EXEC-2", payload,
            command_id, "KERNEL-M1A", session.state["last_event_sequence"] + 1,
        )
        world["executive_lease"] = new_lease
        return {"old_lease_ref": lease_ref(old_lease), "new_lease": new_lease}

    session.accept(
        "replace-executive-lease", "head", replace,
        lambda cid, payload: [("ExecutiveLeaseReplaced", payload["new_lease"], [])],
        goal=object_ref(world["goal"]),
    )
    session.refuse(
        "propose-plan-revision", "arm",
        lambda cid: candidate_plan_payload(session, world, cid), "E-STALE-LEASE",
        lease=lease_ref(old_lease), goal=object_ref(world["goal"]),
    )
    return [session.fixture_case()]


def build_fixture_020() -> list[dict]:
    session, world = setup_case(
        "F-M1A-020", "mutation", "Worker and verifier cannot mutate parent planning records.", "plan"
    )

    def goal_payload(command_id):
        payload = copy.deepcopy(world["goal"]["payload"])
        payload["outcome"] = "Unauthorized worker mutation."
        return domain_record(
            "goal-spec", "m1a-goal-spec-1", "GOAL-M1A", payload,
            command_id, ROLE_ACTORS["worker"], session.state["last_event_sequence"] + 1,
            version=2,
        )

    session.refuse(
        "accept-goal-spec", "worker", goal_payload, "E-AUTH-PARENT-MUTATION",
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    session.refuse(
        "propose-plan-revision", "verifier",
        lambda cid: candidate_plan_payload(session, world, cid), "E-AUTH-PARENT-MUTATION",
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    return [session.fixture_case()]


def build_fixture_021() -> list[dict]:
    session, world = setup_case(
        "F-M1A-021", "strict", "Unknown field/version decode-fail; unknown policy refuses.", "goal"
    )
    session.add_decode_failure(
        '{"command_schema_version":"m1a-command-1","unknown":true}',
        "E-SCHEMA-UNKNOWN-FIELD",
    )
    session.add_decode_failure(
        '{"command_schema_version":"m1a-command-2"}',
        "E-SCHEMA-UNKNOWN-VERSION",
    )

    def unknown_policy(command_id):
        return domain_record(
            "pause-directive", "m1a-pause-directive-1", "PAUSE-UNKNOWN-POLICY",
            {
                "pause_policy_ref": {
                    "policy_id": "POLICY-UNKNOWN", "policy_version": 99,
                    "content_digest": h("unknown-policy"),
                },
                "mode": "current-immediate", "new_pause_epoch": 1,
                "reason_digest": h("unknown-policy-pause"),
            },
            command_id, ROLE_ACTORS["owner"], session.state["last_event_sequence"] + 1,
        )

    session.refuse(
        "apply-pause", "owner", unknown_policy, "E-POLICY-UNKNOWN",
        goal=object_ref(world["goal"]),
    )
    return [session.fixture_case()]


def build_fixture_022() -> list[dict]:
    cases = []
    for case_id in ("write-write", "read-write", "same-effect"):
        session, world = setup_case(
            "F-M1A-022", case_id, f"Reject unordered {case_id} ownership conflict.", "plan"
        )
        session.refuse(
            "propose-plan-revision", "arm",
            lambda cid: candidate_plan_payload(session, world, cid, mutation="write-conflict"),
            "E-DAG-CONFLICT", lease=lease_ref(world["executive_lease"]),
            goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
            witness=error_witness(
                "E-DAG-CONFLICT", object_ids=["TASK-CANDIDATE-A", "TASK-CANDIDATE-B"],
                fields=[case_id],
            ),
        )
        cases.append(session.fixture_case())

    session, world = setup_case(
        "F-M1A-022", "ordered", "Admit a deterministic conflict-free replan.", "plan"
    )
    box = {}

    def replan_payload(command_id):
        proposal = candidate_plan_payload(session, world, command_id)
        disposition = {
            "object_ref": object_ref(world["plan"]), "disposition": "supersede",
            # The transition carries the exact replacement plan ref. Keeping the
            # disposition replacement nullable avoids a self-digest cycle because
            # the disposition is itself embedded in the replacement PlanRevision.
            "replacement_ref": None,
            "reason_digest": h("ordered-replan"),
        }
        transition_payload = copy.deepcopy(proposal["plan_transition"]["payload"])
        transition_payload["dispositions"] = [disposition]
        transition = domain_record(
            "plan-transition", "m1a-plan-transition-1", "TRANSITION-CANDIDATE",
            transition_payload, command_id, ROLE_ACTORS["arm"],
            session.state["last_event_sequence"] + 1, version=2,
            under_lease=lease_ref(world["executive_lease"]),
        )
        plan_payload = copy.deepcopy(proposal["plan_revision"]["payload"])
        plan_payload["dispositions"] = [disposition]
        plan = domain_record(
            "plan-revision", "m1a-plan-revision-1", "PLAN-CANDIDATE", plan_payload,
            command_id, ROLE_ACTORS["arm"], session.state["last_event_sequence"] + 1,
            version=2, under_lease=lease_ref(world["executive_lease"]),
        )
        # Rebind the transition after the final plan digest.
        transition_payload["to_plan_ref"] = object_ref(plan)
        transition = domain_record(
            "plan-transition", "m1a-plan-transition-1", "TRANSITION-CANDIDATE",
            transition_payload, command_id, ROLE_ACTORS["arm"],
            session.state["last_event_sequence"] + 1, version=2,
            under_lease=lease_ref(world["executive_lease"]),
        )
        decision = domain_record(
            "replan-decision", "m1a-replan-decision-1", "REPLAN-DECISION-1",
            {
                "goal_ref": object_ref(world["goal"]), "old_plan_ref": object_ref(world["plan"]),
                "new_plan_ref": object_ref(plan), "trigger_evidence_digests": [h("ordered-replan")],
                "dispositions": [disposition], "narrowed_binding_digest": h("narrowed-binding"),
                "blocker_ref": None, "escalation_ref": None, "disposition": "admitted",
            },
            command_id, ROLE_ACTORS["arm"], session.state["last_event_sequence"] + 1,
            under_lease=lease_ref(world["executive_lease"]),
        )
        box.update({"decision": decision, "plan": plan, "transition": transition, "tasks": proposal["task_nodes"]})
        return {"decision": decision, "new_plan_revision": plan, "transition": transition, "task_nodes": proposal["task_nodes"]}

    session.accept(
        "propose-replan", "arm", replan_payload,
        lambda cid, payload: [
            ("ReplanAdmitted", box["decision"], []),
            ("PlanRevisionAdmitted", box["plan"], [box["transition"], *box["tasks"]]),
        ],
        lease=lease_ref(world["executive_lease"]), goal=object_ref(world["goal"]),
        plan=object_ref(world["plan"]),
    )
    cases.append(session.fixture_case())
    return cases


def build_fixture_023() -> list[dict]:
    session, world = setup_case(
        "F-M1A-023", "incomplete", "Incomplete amendment refuses atomically.", "packet"
    )

    def incomplete(command_id):
        proposal = candidate_plan_payload(session, world, command_id)
        new_goal_payload = copy.deepcopy(world["goal"]["payload"])
        new_goal_payload["fence_epoch"] = 2
        new_goal = domain_record(
            "goal-spec", "m1a-goal-spec-1", "GOAL-M1A", new_goal_payload,
            command_id, ROLE_ACTORS["owner"], session.state["last_event_sequence"] + 1,
            version=2,
        )
        plan_payload = copy.deepcopy(proposal["plan_revision"]["payload"])
        plan_payload["goal_ref"] = object_ref(new_goal)
        plan = domain_record(
            "plan-revision", "m1a-plan-revision-1", "PLAN-CANDIDATE", plan_payload,
            command_id, ROLE_ACTORS["arm"], session.state["last_event_sequence"] + 1,
            version=2, under_lease=lease_ref(world["executive_lease"]),
        )
        transition_payload = copy.deepcopy(proposal["plan_transition"]["payload"])
        transition_payload["to_plan_ref"] = object_ref(plan)
        transition = domain_record(
            "plan-transition", "m1a-plan-transition-1", "TRANSITION-CANDIDATE",
            transition_payload, command_id, ROLE_ACTORS["arm"],
            session.state["last_event_sequence"] + 1, version=2,
            under_lease=lease_ref(world["executive_lease"]),
        )
        amendment = domain_record(
            "goal-spec-amendment", "m1a-goal-spec-amendment-1", "AMENDMENT-INCOMPLETE",
            {
                "old_goal_ref": object_ref(world["goal"]), "new_goal_ref": object_ref(new_goal),
                "changed_field_paths": ["fence_epoch"], "rationale_digest": h("incomplete"),
                "owner_authority_attestation_id": "AUTH-" + command_id[4:],
                "effective_fence_epoch": 2, "checkpoint_rule": "current-immediate",
                "compatibility_inputs": [], "dispositions": [],
                "plan_transition_ref": object_ref(transition),
            },
            command_id, ROLE_ACTORS["owner"], session.state["last_event_sequence"] + 1,
        )
        arm_candidate = digest({
            "replacement_plan_revision": plan, "plan_transition": transition,
            "task_nodes": proposal["task_nodes"],
        })
        arm_auth = session._authority(
            "CMD-ARM-ATTEST-INCOMPLETE", "propose-plan-revision", "arm", arm_candidate
        )
        return {
            "new_goal_spec": new_goal, "amendment": amendment,
            "replacement_plan_revision": plan, "plan_transition": transition,
            "task_nodes": proposal["task_nodes"],
            "arm_proposal_attestation_id": arm_auth["attestation_id"],
        }

    session.refuse(
        "amend-goal-spec", "owner", incomplete, "E-AMENDMENT-INCOMPLETE",
        goal=object_ref(world["goal"]), plan=object_ref(world["plan"]),
    )
    return [session.fixture_case()]


BUILDERS = {
    1: build_fixture_001,
    2: build_fixture_002,
    3: build_fixture_003,
    4: build_fixture_004,
    5: build_fixture_005,
    6: build_fixture_006,
    7: build_fixture_007,
    8: build_fixture_008,
    9: build_fixture_009,
    10: build_fixture_010,
    11: build_fixture_011,
    12: build_fixture_012,
    13: build_fixture_013,
    14: build_fixture_014,
    15: build_fixture_015,
    16: build_fixture_016,
    17: build_fixture_017,
    18: build_fixture_018,
    19: build_fixture_019,
    20: build_fixture_020,
    21: build_fixture_021,
    22: build_fixture_022,
    23: build_fixture_023,
}


def bundle(number: int) -> dict:
    fixture_id = f"F-M1A-{number:03d}"
    return {
        "fixture_schema_version": "m1a-fixture-1",
        "fixture_id": fixture_id,
        "description": f"Literal deterministic oracle bundle {fixture_id}.",
        "cases": sorted(BUILDERS[number](), key=lambda case: case["case_id"]),
    }


def pretty_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build_outputs() -> dict[Path, bytes]:
    outputs: dict[Path, bytes] = {}
    manifest_rows = []
    schema = json.loads(
        (ROOT / "schemas" / "control-plane" / "v3" / "planning" / "schema.json").read_text(
            encoding="utf-8"
        )
    )
    for number in range(1, 24):
        value = bundle(number)
        path = FIXTURE_DIR / f"F-M1A-{number:03d}.json"
        data = pretty_bytes(value)
        outputs[path] = data
        cases = value["cases"]
        errors = sorted({
            error
            for case in cases
            for error in [
                *(item["primary_error"] for item in case["expected_decode_failures"]),
                *(item["primary_error"] for item in case["expected_receipts"] if item["primary_error"]),
                *(item["primary_error"] for item in case["replay_cases"] if item["primary_error"]),
            ]
        })
        manifest_rows.append({
            "fixture_id": value["fixture_id"],
            "path": path.name,
            "sha256": sha_bytes(data),
            "bytes": len(data),
            "case_count": len(cases),
            "command_count": sum(
                len(case["initial_commands"]) + len(case["commands"]) for case in cases
            ),
            "receipt_count": sum(
                len(case["initial_receipts"]) + len(case["expected_receipts"])
                for case in cases
            ),
            "event_count": sum(
                len(case["initial_events"]) + len(case["expected_events"])
                for case in cases
            ),
            "decode_failure_count": sum(
                len(case["expected_decode_failures"]) for case in cases
            ),
            "replay_case_count": sum(len(case["replay_cases"]) for case in cases),
            "error_codes": errors,
            "expected_final_digests": [case["expected_final_digest"] for case in cases],
        })
    manifest = {
        "manifest_schema_version": "m1a-red-manifest-1",
        "schema_candidate": SCHEMA_CANDIDATE,
        "schema_sha256": sha_bytes(
            (ROOT / "schemas" / "control-plane" / "v3" / "planning" / "schema.json").read_bytes()
        ),
        "schema_definitions": sorted(schema["$defs"]),
        "closed_command_types": schema["$defs"]["command_type"]["enum"],
        "closed_event_types": schema["$defs"]["event_type"]["enum"],
        "closed_error_codes": schema["$defs"]["error_code"]["enum"],
        "domain_record_types": sorted(
            schema["$defs"][branch["$ref"].split("/")[-1]]["properties"]["object_type"]["const"]
            for branch in schema["$defs"]["domain_record"]["oneOf"]
        ),
        "projection_terminal_states": schema["$defs"]["projection_state"]["properties"]
        ["terminal_status"]["enum"],
        "fixture_count": 23,
        "fixtures": manifest_rows,
    }
    outputs[FIXTURE_DIR / "manifest.json"] = pretty_bytes(manifest)
    return outputs


def main() -> None:
    outputs = build_outputs()
    if sys.argv[1:] == ["--write"]:
        FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
        expected = set(outputs)
        for existing in FIXTURE_DIR.glob("*.json"):
            if existing not in expected:
                raise SystemExit(f"unexpected existing fixture: {existing.name}")
        for path, data in outputs.items():
            path.write_bytes(data)
        return
    if sys.argv[1:] == ["--check"]:
        for path, data in outputs.items():
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"fixture is not byte-identical: {path.name}")
        print("M1A_FIXTURE_MATERIALIZATION_PASS")
        return
    raise SystemExit("usage: materialize_fixtures.py --write | --check")


if __name__ == "__main__":
    main()

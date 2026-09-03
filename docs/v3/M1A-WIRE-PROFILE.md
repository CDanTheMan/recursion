---
title: M1A closed JSON wire profile
status: normative-blueprint-for-future-build-not-executed
last-updated: 2026-09-03
---

# M1A closed JSON wire profile

This file owns the exact JSON encoding for the future M1A fixture and schema slice. The semantic
owner remains [AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md); the fixture sequences and expected
outcomes remain [M1A-FIXTURE-ORACLES.md](M1A-FIXTURE-ORACLES.md). A future implementation MUST
translate this profile mechanically into JSON Schema before choosing literal fixture values. It
MUST NOT rename, omit, add, flatten or re-nest a field. This is documentation-level specification,
not an executable schema or runtime result.

## Closed representation rules

Every field listed in this file is required. `T?` means the field value is either `T` or JSON
`null`; it never means the field may be omitted. Every record recursively has
`additionalProperties=false`. JSON object member order is irrelevant before canonicalization;
arrays marked `sorted` MUST already be in ascending Unicode-code-point order of their indicated
key and MUST contain no duplicate key. All other arrays preserve their stated semantic order.

| Alias | Exact representation and bound |
|---|---|
| `Id` | ASCII string matching `^[A-Z][A-Z0-9]*(?:-[A-Za-z0-9][A-Za-z0-9._-]*)+$`, 3–128 bytes |
| `Token` | ASCII string matching `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`, 1–64 bytes |
| `Digest` | lowercase hexadecimal SHA-256, exactly 64 characters |
| `Text` | UTF-8 string, 0–4,096 bytes; no NUL or unpaired surrogate |
| `NonemptyText` | `Text` with at least one Unicode scalar value |
| `UInt` | JSON integer from 0 through 9,007,199,254,740,991 |
| `PosInt` | JSON integer from 1 through 2,147,483,647 |
| `LogicalTime` | `UInt`, supplied by the fixture/event stream; never read from a clock |
| `IdSet` | sorted array of `Id`, maximum 256 |
| `DigestSet` | sorted array of `Digest`, maximum 256 |
| `TokenSet` | sorted array of `Token`, maximum 256 |
| `TextSet` | sorted array of `Text`, maximum 256 |
| `ResourcePathSet` | sorted array of the `ResourcePath` grammar in the fixture blueprint, maximum 256 |

An individual command, domain record, event or receipt is at most 262,144 canonical UTF-8 bytes;
a fixture bundle is at most 1,048,576 bytes; nesting depth is at most 16; commands/events/records
per bundle are each at most 2,048. Floats, negative zero, binary values and non-I-JSON numbers are
forbidden. `D(x)` is RFC 8785 canonical JSON followed by SHA-256. For every structure below,
`content_digest` is the only field omitted when computing that structure's `D(x)`; nested
structures retain their own digest fields. Fields named `*_digest` are never implicitly omitted.

## Reusable exact records

```text
ObjectRef@1 = {
  object_type: Token,
  id: Id,
  version: PosInt,
  content_digest: Digest
}

PolicyRef@1 = {
  policy_id: Id,
  policy_version: PosInt,
  content_digest: Digest
}

FixtureAuthorityAttestation@1 = {
  attestation_schema_version: "m1a-fixture-authority-1",
  attestation_id: Id,
  actor_id: Id,
  actor_role: owner or head or arm or worker or verifier or kernel-fixture-gate,
  allowed_command_types: TokenSet,
  candidate_digest: Digest,
  authority_policy_ref: PolicyRef@1,
  constitution_policy_ref: PolicyRef@1,
  valid_from_logical_time: LogicalTime,
  expires_logical_time: LogicalTime,
  content_digest: Digest
}

PolicyFixture@1 = {
  policy_schema_version: "m1a-policy-fixture-1",
  policy_id: Id,
  policy_version: PosInt,
  policy_kind: authority or privacy-egress or route-envelope or novelty or verifier or
               constitution or pause or retry,
  allowed_roles: TokenSet,
  allowed_command_types: TokenSet,
  privacy_class_ids: IdSet,
  privacy_at_most_edges: sorted array of {less_or_equal_id: Id, greater_or_equal_id: Id}
                         by (less_or_equal_id,greater_or_equal_id),
  egress_class_ids: IdSet,
  egress_at_most_edges: sorted array of {less_or_equal_id: Id, greater_or_equal_id: Id}
                        by (less_or_equal_id,greater_or_equal_id),
  route_ids: IdSet,
  account_class_ids: IdSet,
  capacity_pool_ids: IdSet,
  allowed_spend_classes: TokenSet restricted to none and included,
  accepted_evidence_types: sorted array of {failure_id: Id, evidence_types: TokenSet}
                           by failure_id,
  failure_capability_requirements: sorted array of {failure_id: Id, capability_ids: IdSet}
                                   by failure_id,
  required_verifier_dimensions: TokenSet,
  owner_verifier_exception_allowed: true or false,
  operative_pause_mode: current-immediate,
  representable_future_pause_modes: TokenSet restricted to checkpoint, interrupt and drain,
  retry_maximum: UInt,
  content_digest: Digest
}

LeaseRef@1 = {
  lease_id: Id,
  lease_epoch: UInt,
  content_digest: Digest
}

BudgetVector@1 = {
  model_turns: UInt,
  attempts: UInt,
  tokens: UInt,
  money_minor: UInt,
  cpu_ms: UInt,
  memory_bytes: UInt,
  output_bytes: UInt
}

GateRequirement@1 = {
  gate_id: Id,
  procedure_digest: Digest,
  evidence_schema_digest: Digest,
  candidate_binding_digest: Digest,
  verifier_policy_digest: Digest
}

IndependenceVector@1 = {
  model_family: Token,
  provider: Token,
  host: Token,
  session: Token,
  evidence_store: Token,
  implementation_actor_id: Id,
  verifier_actor_id: Id,
  missing_dimensions: TokenSet
}

Disposition@1 = {
  object_ref: ObjectRef@1,
  disposition: one of retain-definition, retain-terminal, invalidate, quarantine,
               supersede, cancel, fence,
  replacement_ref: ObjectRef@1?,
  reason_digest: Digest
}
```

`GateRequirement@1` arrays sort by `gate_id`; `Disposition@1` arrays sort by
`(object_ref.object_type, object_ref.id, object_ref.version)`. `CompatibilityInput@1`,
`NodeCompatibilityTuple@1`, `NoveltyDelta@1` and its seven kind payloads have exactly the fields,
enums and comparison rules in the correspondingly named closed-grammar sections of
[AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md). Those records are embedded as JSON objects, not
as opaque digests, whenever named below; their separately named digest fields are recomputed.
`PolicyRef@1` resolves only when every field matches one `PolicyFixture@1` in the same bundle;
there is no ambient registry. Fields irrelevant to a policy kind remain required and take their
empty-array/`false`/zero value. The reducer uses only the fields allowed for that kind and refuses
a nonempty irrelevant field with `E-POLICY-UNKNOWN`. A novelty policy uses exactly
`accepted_evidence_types`, `failure_capability_requirements`, `route_ids`, `account_class_ids`,
`capacity_pool_ids` and `allowed_spend_classes`. A verifier policy uses
`required_verifier_dimensions` and `owner_verifier_exception_allowed`. A constitution policy
uses `owner_verifier_exception_allowed`; a downgrade requires that boolean to be true in both
the exact GoalSpec-bound verifier and constitution fixtures.

An authority policy uses `allowed_roles` and `allowed_command_types`; a privacy-egress policy
uses only the two class sets and their two edge sets; a route-envelope policy uses the
route/account/pool/spend fields; a pause policy uses the operative/future pause fields; and a
retry policy uses only `retry_maximum`. Each policy kind MUST have exactly its named fields
nonempty/nonzero (booleans are excepted as stated); every other kind-specific array is empty and
every other numeric field is zero. The fixed common identity/version/digest fields are always
populated.

Every `PolicyRef@1` field has an exact kind constraint: OwnerIntent/GoalSpec privacy and egress
refs are `privacy-egress`; GoalSpec `route_policy_ref` is `route-envelope`,
`novelty_policy_ref` is `novelty`, `retry_policy_ref` is `retry`, `verifier_policy_ref` is
`verifier`, `constitution_policy_ref` is `constitution` and `pause_policy_ref` is `pause`.
TaskNode policy refs MUST equal the corresponding GoalSpec refs. An authority attestation's
authority ref is `authority` and its constitution ref MUST equal the GoalSpec-bound constitution
ref for a goal-scoped command. A route assignment's route-policy ref MUST equal the
GoalSpec-bound route-envelope ref. Any kind, equality or same-bundle lookup mismatch is
`E-POLICY-UNKNOWN` before semantic execution.

## Domain-record envelope

Every M1A domain record has exactly this shape:

```text
DomainRecord@1<P> = {
  object_type: registered Token,
  schema_version: registered Token,
  id: Id,
  version: PosInt,
  created_by_actor_id: Id,
  created_under_lease: LeaseRef@1?,
  causation_id: Id,
  correlation_id: Id,
  created_logical_time: LogicalTime,
  payload: P,
  content_digest: Digest
}
```

The pair `(object_type, schema_version)` selects exactly one payload below. Every array named
`*_refs`, `*_ids`, `*_digests` or `*_keys` is a duplicate-free sorted set. A `DomainRecord`
cannot contain another complete `DomainRecord`; it uses `ObjectRef@1` except where the command
mapping explicitly carries a proposed new record.

| `object_type` / `schema_version` | Exact payload fields |
|---|---|
| `owner-intent` / `m1a-owner-intent-1` | `{intent_text: NonemptyText, source_kind: owner-prompt or owner-amendment, source_digest: Digest, privacy_policy_ref: PolicyRef@1, supersedes_ref: ObjectRef@1?}` |
| `goal-spec` / `m1a-goal-spec-1` | `{owner_intent_ref: ObjectRef@1, outcome: NonemptyText, acceptance_gate_ids: IdSet, allowed_resource_paths: ResourcePathSet, non_goals: TextSet, authority_ids: IdSet, capability_ids: IdSet, privacy_class_id: Id, egress_class_id: Id, privacy_policy_ref: PolicyRef@1, egress_policy_ref: PolicyRef@1, route_policy_ref: PolicyRef@1, allowed_route_ids: IdSet, budget_limits: BudgetVector@1, source_digests: DigestSet, novelty_policy_ref: PolicyRef@1, retry_policy_ref: PolicyRef@1, verifier_policy_ref: PolicyRef@1, constitution_policy_ref: PolicyRef@1, pause_policy_ref: PolicyRef@1, allowed_effect_keys: IdSet, publication_allowed: false, terminal_owner_seam_ids: IdSet, fence_epoch: UInt, state: accepted}` |
| `goal-spec-amendment` / `m1a-goal-spec-amendment-1` | `{old_goal_ref: ObjectRef@1, new_goal_ref: ObjectRef@1, changed_field_paths: TextSet, rationale_digest: Digest, owner_authority_attestation_id: Id, effective_fence_epoch: UInt, checkpoint_rule: current-immediate or safe-checkpoint, compatibility_inputs: sorted CompatibilityInput@1 by old_node.node_id, dispositions: sorted Disposition@1, plan_transition_ref: ObjectRef@1}` |
| `arm-run` / `m1a-arm-run-1` | `{goal_ref: ObjectRef@1, logical_actor_id: Id, eligible_route_ids: IdSet, budget_limits: BudgetVector@1, source_digests: DigestSet, executive_lease_ref: LeaseRef@1, verifier_policy_ref: PolicyRef@1}` |
| `plan-revision` / `m1a-plan-revision-1` | `{goal_ref: ObjectRef@1, arm_run_ref: ObjectRef@1, prior_plan_ref: ObjectRef@1?, trigger: initial or retry or replan or amendment, task_node_refs: sorted ObjectRef@1 by id, dependency_edges: sorted array of `{from_node_id: Id, to_node_id: Id}` by `(from_node_id,to_node_id)`, graph_digest: Digest, acceptance_gate_ids: IdSet, budget_limits: BudgetVector@1, read_resource_paths: ResourcePathSet, write_resource_paths: ResourcePathSet, effect_keys: IdSet, source_digests: DigestSet, verifier_policy_ref: PolicyRef@1, constitution_policy_ref: PolicyRef@1, change_rationale_digest: Digest, dispositions: sorted Disposition@1}` |
| `plan-transition` / `m1a-plan-transition-1` | `{from_plan_ref: ObjectRef@1?, to_plan_ref: ObjectRef@1, trigger_evidence_digests: DigestSet, dispositions: sorted Disposition@1, executive_lease_ref: LeaseRef@1, expected_goal_fence_epoch: UInt, checkpoint_ref: ObjectRef@1?}` |
| `task-node` / `m1a-task-node-1` | `{plan_ref: ObjectRef@1, semantic_definition_digest: Digest, output_schema_digest: Digest, dependency_node_ids: IdSet, input_digests: DigestSet, source_digests: DigestSet, read_resource_paths: ResourcePathSet, write_resource_paths: ResourcePathSet, effect_keys: IdSet, authority_ids: IdSet, capability_ids: IdSet, route_ids: IdSet, route_capability_ids: IdSet, privacy_class_id: Id, egress_class_id: Id, privacy_policy_ref: PolicyRef@1, budget_limits: BudgetVector@1, gate_requirements: sorted GateRequirement@1 by gate_id, retry_policy_ref: PolicyRef@1, verifier_policy_ref: PolicyRef@1, constitution_policy_ref: PolicyRef@1, terminal_contribution_digest: Digest, retry_maximum: UInt}` |
| `work-packet` / `m1a-work-packet-1` | `{goal_ref: ObjectRef@1, plan_ref: ObjectRef@1, task_ref: ObjectRef@1, logical_worker_actor_id: Id, attempt: PosInt, work_lease_ref: LeaseRef@1, expected_goal_fence_epoch: UInt, expected_pause_epoch: UInt, authority_ids: IdSet, capability_ids: IdSet, allowed_resource_paths: ResourcePathSet, effect_keys: IdSet, privacy_class_id: Id, egress_class_id: Id, privacy_policy_ref: PolicyRef@1, route_assignment_ref: ObjectRef@1, budget_limits: BudgetVector@1, source_digests: DigestSet, gate_requirements: sorted GateRequirement@1 by gate_id, allowed_action_ids: IdSet, prohibition_ids: IdSet, output_schema_digest: Digest, deadline_logical_time: LogicalTime, checkpoint_ref: ObjectRef@1?}` |
| `worker-result` / `m1a-worker-result-1` | `{work_packet_ref: ObjectRef@1, candidate_digest: Digest, evidence_digests: DigestSet, output_digest: Digest, observed_effect_ref: ObjectRef@1?, disposition: submitted or failed}` |
| `gate-result` / `m1a-gate-result-1` | `{goal_ref: ObjectRef@1, plan_ref: ObjectRef@1, task_ref: ObjectRef@1, work_packet_ref: ObjectRef@1, candidate_digest: Digest, source_digests: DigestSet, evidence_digests: DigestSet, gate_requirement: GateRequirement@1, procedure_version: PosInt, observation_digest: Digest, expected_digest: Digest, actual_digest: Digest, independence: IndependenceVector@1, disposition: pass or fail or error or missing or ambiguous, limitation_digests: DigestSet}` |
| `retry-decision` / `m1a-retry-decision-1` | `{goal_ref: ObjectRef@1, plan_ref: ObjectRef@1, task_ref: ObjectRef@1, failed_gate_result_ref: ObjectRef@1, prior_work_packet_ref: ObjectRef@1, novelty_delta: NoveltyDelta@1, novelty_delta_digest: Digest, unchanged_binding_digest: Digest, next_attempt: PosInt, remaining_budget: BudgetVector@1, retry_maximum: UInt, disposition: admitted or refused or exhausted}` |
| `replan-decision` / `m1a-replan-decision-1` | `{goal_ref: ObjectRef@1, old_plan_ref: ObjectRef@1, new_plan_ref: ObjectRef@1, trigger_evidence_digests: DigestSet, dispositions: sorted Disposition@1, narrowed_binding_digest: Digest, blocker_ref: ObjectRef@1?, escalation_ref: ObjectRef@1?, disposition: admitted or refused}` |
| `blocker` / `m1a-blocker-1` | `{blocked_object_ref: ObjectRef@1, kind: authority or capacity or dependency or effect-ambiguity or gate or policy or provider-refusal or source or verifier, evidence_digests: DigestSet, required_actor_id: Id, allowed_recovery_ids: IdSet, retry_after_observation_ref: ObjectRef@1?, failure_fingerprint_digest: Digest, state: open or resolved or superseded or escalated}` |
| `escalation` / `m1a-escalation-1` | `{source_blocker_ref: ObjectRef@1, target_role: head or owner, failure_history_digests: DigestSet, requested_decision: NonemptyText, option_digests: DigestSet, recommendation_digest: Digest, frozen_scope_digest: Digest, state: raised or acknowledged or resolved or declined or superseded}` |
| `plan-verifier-decision` / `m1a-plan-verifier-decision-1` | `{goal_ref: ObjectRef@1, plan_ref: ObjectRef@1, candidate_digest: Digest, event_log_digest: Digest, gate_result_digests: DigestSet, evidence_digests: DigestSet, verifier_policy_ref: PolicyRef@1, constitution_policy_ref: PolicyRef@1, independence: IndependenceVector@1, disposition: pass or downgraded-pass or fail or blocked, assurance_grade: full or downgraded or none, owner_exception_ref: ObjectRef@1?, dissent_digest: Digest?, limitation_digests: DigestSet}` |
| `owner-verifier-exception` / `m1a-owner-verifier-exception-1` | `{goal_ref: ObjectRef@1, plan_ref: ObjectRef@1, candidate_digest: Digest, verifier_policy_ref: PolicyRef@1, constitution_policy_ref: PolicyRef@1, missing_dimensions: TokenSet, reason_digest: Digest, owner_authority_attestation_id: Id, issued_logical_time: LogicalTime, expires_logical_time: LogicalTime}` |
| `executive-lease` / `m1a-executive-lease-1`; `work-lease` / `m1a-work-lease-1` | `{subject_actor_id: Id, goal_ref: ObjectRef@1, plan_ref: ObjectRef@1?, task_ref: ObjectRef@1?, lease_epoch: UInt, nonce_digest: Digest, issued_logical_time: LogicalTime, expires_logical_time: LogicalTime, allowed_command_types: TokenSet, state: active or expired or revoked or replaced}` |
| `checkpoint` / `m1a-checkpoint-1` | `{state_version: UInt, state_digest: Digest, active_goal_ref: ObjectRef@1?, active_plan_ref: ObjectRef@1?, open_packet_refs: sorted ObjectRef@1 by id, ambiguous_effect_refs: sorted ObjectRef@1 by id, budget_snapshot_digest: Digest, route_snapshot_digest: Digest, pause_epoch: UInt, lease_epoch_digest: Digest}` |
| `route-assignment` / `m1a-route-assignment-1` | `{logical_actor_id: Id, route_id: Id, route_capability_ids: IdSet, account_class_id: Id, privacy_policy_ref: PolicyRef@1, route_policy_ref: PolicyRef@1, metered_spend_allowed: false, capacity_observation_digest: Digest, assigned_logical_time: LogicalTime, expires_logical_time: LogicalTime, state: assigned or deferred or released or expired}` |
| `effect-observation` / `m1a-effect-observation-1` | `{effect_id: Id, effect_key: Id, work_packet_ref: ObjectRef@1, idempotency_key_digest: Digest, dispatch_state: undispatched or dispatched, receipt_digest: Digest?, provider_operation_id_digest: Digest?, observation: observed-success or observed-failure or ambiguous, quarantine: true or false}` |
| `disposition` / `m1a-disposition-1` | the exact `Disposition@1` record |

For `plan-verifier-decision`, `pass` requires `full` and a null exception; `downgraded-pass`
requires `downgraded` and an exact `owner-verifier-exception` ref; `fail`/`blocked` require `none`.
For `effect-observation`, `quarantine` is `true` exactly when observation is `ambiguous`.

## Command, receipt, event and projection shapes

```text
CommandEnvelope@1 = {
  command_schema_version: "m1a-command-1",
  command_id: Id,
  command_type: one of the 17 registered command tokens,
  actor_id: Id,
  auth_ref: Id,
  lease_ref: LeaseRef@1?,
  logical_time: LogicalTime,
  expected_state_version: UInt,
  expected_state_digest: Digest,
  goal_ref: ObjectRef@1?,
  plan_ref: ObjectRef@1?,
  payload: the exact payload selected below,
  payload_digest: Digest,
  candidate_digest: Digest,
  content_digest: Digest
}

CommandReceipt@1 = {
  receipt_schema_version: "m1a-receipt-1",
  receipt_id: Id,
  command_id: Id,
  command_digest: Digest,
  disposition: accepted or refused or duplicate or conflict,
  primary_error: one registered error token or null,
  related_errors: TokenSet,
  state_before_digest: Digest,
  state_after_digest: Digest,
  event_ids: IdSet,
  first_event_sequence: UInt?,
  last_event_sequence: UInt?,
  content_digest: Digest
}

PlanningEvent@1 = {
  event_schema_version: "m1a-event-1",
  event_id: Id,
  stream_id: Id,
  sequence: PosInt,
  previous_event_digest: Digest,
  logical_time: LogicalTime,
  command_id: Id,
  command_digest: Digest,
  event_type: registered event Token,
  primary_record: DomainRecord@1,
  related_record_refs: sorted ObjectRef@1 by (object_type,id,version),
  state_delta_digest: Digest,
  content_digest: Digest
}

ProjectionState@1 = {
  projection_schema_version: "m1a-projection-1",
  stream_id: Id,
  state_version: UInt,
  last_event_sequence: UInt,
  last_event_digest: Digest,
  operative_goal_ref: ObjectRef@1?,
  active_arm_run_ref: ObjectRef@1?,
  active_plan_ref: ObjectRef@1?,
  records: sorted DomainRecord@1 by (object_type,id,version),
  object_states: sorted array of {object_ref: ObjectRef@1, state: Token} by
                 (object_ref.object_type,object_ref.id,object_ref.version),
  processed_command_receipt_refs: sorted ObjectRef@1 by id,
  consumed_novelty_delta_digests: DigestSet,
  open_blocker_refs: sorted ObjectRef@1 by id,
  open_escalation_refs: sorted ObjectRef@1 by id,
  ambiguous_effect_refs: sorted ObjectRef@1 by id,
  current_pause_policy_ref: PolicyRef@1,
  current_pause_epoch: UInt,
  terminal_status: nonterminal or terminal-verified or terminal-verified-downgraded or
                   terminal-failed,
  content_digest: Digest
}
```

In a receipt, both event-sequence fields are null exactly when `event_ids` is empty. Receipt
records are not domain records; `processed_command_receipt_refs` therefore uses
`object_type="command-receipt"`, the receipt ID, version 1 and its content digest.

Each command payload is exactly one proposed `DomainRecord@1` except these closed composites:

| Command | Exact `payload` |
|---|---|
| `record-owner-intent`, `accept-goal-spec`, `amend-goal-spec`, `start-arm-run`, `submit-worker-result`, `submit-gate-result`, `propose-retry`, `raise-blocker`, `raise-escalation`, `submit-plan-verifier-decision`, `record-effect-observation` | the correspondingly typed proposed `DomainRecord@1` |
| `propose-plan-revision` | `{plan_revision: DomainRecord@1<plan-revision>, plan_transition: DomainRecord@1<plan-transition>, task_nodes: sorted DomainRecord@1<task-node> by id}` |
| `derive-work-packet` | `{task_ref: ObjectRef@1, attempt: PosInt, work_lease_ref: LeaseRef@1, route_assignment_ref: ObjectRef@1, budget_snapshot_digest: Digest, expected_work_packet_digest: Digest}` |
| `replace-work-lease` | `{old_lease_ref: LeaseRef@1, new_lease: DomainRecord@1<work-lease>}` |
| `replace-route` | `{old_route_ref: ObjectRef@1, new_route: DomainRecord@1<route-assignment>, checkpoint_ref: ObjectRef@1, expected_new_packet_digest: Digest}` |
| `propose-replan` | `{decision: DomainRecord@1<replan-decision>, new_plan_revision: DomainRecord@1<plan-revision>, transition: DomainRecord@1<plan-transition>, task_nodes: sorted DomainRecord@1<task-node> by id}` |
| `apply-pause` | `{pause_policy_ref: PolicyRef@1, new_pause_epoch: UInt}` |

For every M1A command, `payload_digest=D(payload)` and `candidate_digest=payload_digest` exactly.
The matching `FixtureAuthorityAttestation@1.candidate_digest` MUST equal that command field. M1A
defines no other command-candidate selector. A GateResult or PlanVerifierDecision's separate
`candidate_digest` remains the task/output candidate it judges; it does not replace the command
candidate binding.

`amend-goal-spec` additionally requires that the referenced proposed `new_goal_ref` and
`plan_transition_ref` resolve to proposed records carried in the fixture's `initial_events` or
earlier accepted commands; forward references are forbidden. The Owner verifier-exception record
for a downgraded decision likewise MUST already exist as an accepted initial or command-carried
record and its exact ref is placed in the decision.

The event alphabet is the 17 admitted event types in the fixture blueprint plus
`PlanItemDisposed`, `PacketFenced`, `LeaseFenced`, `EffectDisposed` and `EvidenceDisposed`.
Disposition events sort by `(primary_record.payload.object_ref.object_type,
primary_record.payload.object_ref.id, primary_record.payload.object_ref.version)` after the
leading `GoalSpecAmended` or `ReplanAdmitted` event. An event's `primary_record.object_type` MUST
match its event: the natural created object for `*Recorded`, `*Started`, `*Admitted`, `*Derived`,
`*Replaced` or `*Applied`, and `disposition` for the five disposition events. No event carries an
unregistered union arm.

### Exact retry-policy calculation

For a retry command, the GoalSpec and TaskNode retry-policy refs MUST be byte-identical and
resolve the same `PolicyFixture@1(kind=retry)`. Define the total-attempt ceiling as:

`min(policy.retry_maximum, task.retry_maximum, goal.budget_limits.attempts,
task.budget_limits.attempts)`.

`next_attempt` MUST equal `prior_work_packet.payload.attempt + 1` and
`RetryDecision.payload.retry_maximum` MUST equal that ceiling. Admission requires
`next_attempt <= ceiling`; otherwise the primary error is `E-RETRY-EXHAUSTED`. The decision's
`remaining_budget.attempts` MUST equal `ceiling - next_attempt`; every other remaining-budget
field MUST equal the current replay projection after reserving the new packet and MUST be no
greater than both GoalSpec and TaskNode limits. F-M1A-007's “one remaining attempt” therefore
means prior attempt 1, ceiling 2, admitted next attempt 2 and remaining attempts 0. Novelty,
PAUSE, effect ambiguity and budget checks still run in the closed error-precedence order; no
policy maximum is inferred from prose or an ambient default.

## Construction ownership and falsifier

M1A-01 owns only a mechanical translation of this profile into strict JSON Schemas plus
meta-schema/load tests. M1A-02 then freezes literal sanitized bundles against those accepted
schemas and the separate oracle table, before reducer code. Neither node may change semantic
fields or expected transitions. Any ambiguity, schema/oracle mismatch or need for another union
arm stops for a new reviewed PlanRevision.

The decisive documentation falsifier is concrete: two implementers given these three canonical
documents must derive the same allowed field names, nesting, required/nullability rules, bounds,
digest omission profile, command payload union, receipt/event/projection shape and oracle
transition for F-M1A-005, F-M1A-007 and F-M1A-011. Literal synthetic values are deliberately
chosen and frozen once by M1A-02; different fixture prose or IDs before that freeze do not create
different contract semantics. M1A-02 must stop if it discovers a remaining semantic choice.

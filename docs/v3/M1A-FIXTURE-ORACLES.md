---
title: M1A deterministic fixture-oracle blueprint
status: owner-approved-construction-oracle
last-updated: 2026-09-03
---

# M1A deterministic fixture-oracle blueprint

This document closes the expected oracle for the future M1A build. It is a documentation
specification, not an executable fixture set or runtime result. The exact field names, nesting,
bounds, nullability and digest profile are owned by
[M1A-WIRE-PROFILE.md](M1A-WIRE-PROFILE.md). The authorized M1A campaign MUST first translate that
profile mechanically into strict schemas, then freeze literal sanitized JSON bundles and
their expected digests in a red-test commit, all before implementing a reducer. If either step
requires a choice outside the bounded delegation recorded in the campaign, construction stops for
Lucas; code must not guess.

The canonical planning meanings remain in
[AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md). The scope and construction DAG remain in
[M1A-AUTONOMOUS-PLANNING.md](M1A-AUTONOMOUS-PLANNING.md). This file owns only the M1A fixture
alphabet and oracle projection.

## Canonical bundle and digest rules

Every bundle is strict JSON with this closed top-level shape and exact types. There are exactly
23 bundles, one per F-M1A ID. A bundle contains one or more isolated cases so an oracle row can
exercise variants without sharing state or creating extra fixture IDs:

```text
fixture_schema_version: "m1a-fixture-1"
fixture_id: Id
description: NonemptyText
cases: nonempty sorted array by case_id of {
  case_id: Token,
  description: NonemptyText,
  genesis: GenesisConfig@1,
  authority_fixtures: sorted FixtureAuthorityAttestation@1 by attestation_id,
  policy_fixtures: sorted PolicyFixture@1 by (policy_id,policy_version),
  initial_commands: CommandEnvelope@1[] in declared execution order,
  initial_receipts: CommandReceipt@1[] in command order,
  initial_events: PlanningEvent@1[] in ascending contiguous sequence,
  decode_inputs: JsonInputText[] in declared order,
  expected_decode_failures: DecodeFailure@1[] in decode-input order,
  commands: CommandEnvelope@1[] in declared execution order,
  expected_receipts: CommandReceipt@1[] in command order,
  expected_events: PlanningEvent@1[] in ascending contiguous sequence,
  replay_cases: ReplayExpectation@1[] in declared order,
  expected_final_state: ProjectionState@1,
  expected_final_digest: Digest equal to expected_final_state.content_digest
}
```

Unknown or duplicate fields fail. Strings, arrays, maps, integers and nesting use explicit schema
limits. No float, non-I-JSON value, wall time, random value, environment value, filesystem
observation or unordered-map iteration participates.

`D(x)` means lowercase hexadecimal SHA-256 of RFC 8785 canonical JSON for `x` with its own
`content_digest` field omitted. Every future literal expected digest is computed by that rule and
committed in the red bundle; placeholders such as `D(x)` are forbidden in the executable bundle.
Fixture IDs and logical times are literal inputs. Commands use `CMD-<fixture>-<case>-<nn>`;
first-seen receipts replace that prefix with `RCPT-`; conflict receipts use the digest-derived
`RCPT-CONFLICT-*` form; admitted events replace it with `EV-` and append the one-based four-digit
position within the command, exactly as defined by the wire profile. Each case
starts from the exact genesis projection and fixed sequence-one previous-event digest defined by
the wire profile.

An exact duplicate command ID and digest returns the byte-identical original receipt and emits no
event. The same command ID with another digest returns `conflict/E-IDEMPOTENCY-CONFLICT` and emits
no event. Every structurally valid command receives one deterministic receipt. A refusal has
`state_before_digest`, unchanged `state_after_digest`, empty `event_ids`, and an error from the
closed registry below. Invalid JSON or a value that does not satisfy the selected schema epoch
returns `DecodeFailure@1` from `decode`; it has no CommandReceipt, event or state transition.

## Synthetic authority and policy fixtures

M1A does not implement or claim production authentication. Each bundle supplies the exact
`FixtureAuthorityAttestation@1` and `PolicyFixture@1` records defined by
[M1A-WIRE-PROFILE.md](M1A-WIRE-PROFILE.md). A command is fixture-authorized only when its exact
`auth_ref`, actor, type, logical time, `candidate_digest=payload_digest` and
authority/constitution policy references
match that supplied table. Missing, expired, unknown or mismatched references fail. No boolean
such as `trusted=true` is permitted.

The allowed roles are `owner`, `head`, `arm`, `worker`, `verifier`, `kernel-fixture-gate`. Only
`owner` may accept/amend GoalSpec or approve the fixture-only verifier exception; only `head` may
start/replace/stop ArmRun; only `arm` may propose PlanRevision/retry/replan; only `worker` may
submit the packet result; only the assigned verifier/gate may submit its gate/plan decision. The
kernel fixture is a pure decider, never an input actor.

`ResourcePath` is a platform-neutral logical key for M1A, not a filesystem path. Its grammar is
`^[a-z0-9][a-z0-9._-]*(/[a-z0-9][a-z0-9._-]*)*$`; `.`, `..`, empty/absolute paths, backslashes,
case folding, symlinks and platform paths are absent. Prefix-by-segment determines overlap.
Read/read is compatible; unordered read/write or write/write overlap fails. M1A has no effect
commutativity registry: equal synthetic `effect_key` values conflict, unequal keys are disjoint,
and a dependency may serialize but never merge ownership.

Privacy classes and route capabilities are finite identifiers supplied by an exact policy
fixture. The fixture provides the partial order and allowed set. Every policy reference obeys
the exact kind/equality lookup table in the wire profile. The GoalSpec binds exact route, novelty,
retry, verifier, constitution and PAUSE policy refs; `NoveltyDelta@1` admission uses only the
bound novelty fixture's accepted-evidence maps, failure-capability maps and route envelope.
Verifier downgrade requires both bound verifier and constitution fixtures to permit the Owner
exception plus a matching unexpired Owner attestation/exception record. Unknown, incomparable or
ambient values fail; the reducer performs set inclusion and exact integer comparison only.

## Closed command and event alphabets

| Command type | Fixture-authorized role | Admitted event type |
|---|---|---|
| `record-owner-intent` | `owner` | `OwnerIntentRecorded` |
| `accept-goal-spec` | `owner` | `GoalSpecAccepted` |
| `amend-goal-spec` | `owner` | `GoalSpecAmended`, then ordered disposition events |
| `record-owner-verifier-exception` | `owner` | `OwnerVerifierExceptionRecorded` |
| `start-arm-run` | `head` | `ArmRunStarted` |
| `propose-plan-revision` | `arm` | `PlanRevisionAdmitted` or no event on whole-plan refusal |
| `derive-work-packet` | `arm` request; kernel derives | `WorkPacketDerived` |
| `replace-work-lease` | `head` | `WorkLeaseReplaced` |
| `replace-executive-lease` | `head` | `ExecutiveLeaseReplaced` |
| `replace-route` | `head` | `RouteAssignmentReplaced` |
| `record-capacity-observation` | `kernel-fixture-gate` | `CapacityObservationRecorded` |
| `record-checkpoint` | `kernel-fixture-gate` | `CheckpointRecorded` |
| `reserve-budget` | `arm` | `BudgetReserved` |
| `submit-worker-result` | `worker` (the packet-assigned worker only) | `WorkerResultRecorded` |
| `submit-gate-result` | `verifier` or `kernel-fixture-gate` (the bound verifier assignment only) | `GateResultRecorded` |
| `propose-retry` | `arm` | `RetryAdmitted` or `RetryRefused` only as receipt |
| `propose-replan` | `arm` | `ReplanAdmitted`, `PlanRevisionAdmitted`, ordered disposition events |
| `raise-blocker` | `worker`, `verifier`, `arm` or `head` when assigned to the bound object | `BlockerRaised` |
| `raise-escalation` | `arm` or `head` | `EscalationRaised` |
| `submit-plan-verifier-decision` | `verifier` (the plan-assigned verifier only) | `PlanVerifierDecisionRecorded` |
| `apply-pause` | `owner` under operative fixture policy | `PauseApplied` |
| `record-effect-observation` | `kernel-fixture-gate` | `EffectObservationRecorded` |

No plugin, adapter, provider or free-form command type exists. Refused commands do not append an
authoritative planning event. The pure projection uses the exact object states enumerated in
`AUTONOMOUS-PLANNING.md`; `terminal-verified` additionally requires every current node complete,
all required gates passed, a full `pass` PlanVerifierDecision and no open blocker, escalation,
retry, stale packet or ambiguous effect. A valid `downgraded-pass` can produce only the distinct
`terminal-verified-downgraded` projection and must preserve its missing independence dimensions.

## Closed error registry

| Error | Mechanical condition |
|---|---|
| `E-SCHEMA-UNKNOWN-FIELD` | any field outside the exact schema |
| `E-SCHEMA-MISSING-FIELD` | a required field is absent after duplicate-key-safe JSON parsing |
| `E-SCHEMA-UNKNOWN-VERSION` | fixture/object/policy/novelty/event version not registered |
| `E-SCHEMA-INVALID` | malformed JSON, invalid UTF-8/surrogate, lexical negative zero, wrong JSON type/pattern/enum, or another schema violation not assigned a narrower schema code |
| `E-SCHEMA-DUPLICATE` | duplicate JSON key or stable object ID |
| `E-SCHEMA-BOUND` | configured size/count/depth/integer bound exceeded |
| `E-DIGEST-MISMATCH` | canonical digest or event chain mismatch |
| `E-AUTH-MISSING` | required synthetic authority reference absent/unknown |
| `E-AUTH-PARENT-MUTATION` | authenticated `worker` or `verifier` submits `accept-goal-spec`, `amend-goal-spec`, `propose-plan-revision` or `propose-replan`; this narrow classifier precedes generic role rejection |
| `E-AUTH-ROLE` | actor/command/assignment tuple unauthorized after the parent-mutation classifier |
| `E-SCOPE-WIDEN` | child capability/path/effect/privacy/egress/route set is not attenuated |
| `E-BUDGET-WIDEN` | child limit or consumed-plus-remaining amount exceeds parent |
| `E-DAG-CYCLE` | deterministic topological check leaves a cycle |
| `E-DAG-DEPENDENCY` | self, absent or unsatisfied dependency |
| `E-DAG-CONFLICT` | unordered logical resource/effect ownership conflict |
| `E-STALE-GOAL` | command/packet binds a noncurrent GoalSpec version/epoch |
| `E-STALE-PLAN` | command/packet binds a nonactive PlanRevision |
| `E-STALE-LEASE` | actor/packet binds expired/replaced lease epoch |
| `E-GATE-MISSING` | required GateResult absent, stale, ambiguous or nonpass |
| `E-VERIFIER-MISSING` | required assigned verifier/exception receipt absent or mismatched |
| `E-RETRY-NONNOVEL` | typed novelty delta is unknown, empty, repeated or does not address prior failure |
| `E-RETRY-EXHAUSTED` | attempt, task, goal or budget retry maximum reached |
| `E-ROUTE-SPEND` | replacement would add route/account/capability or metered authority |
| `E-PAUSED` | operative current-immediate PAUSE forbids transition |
| `E-EFFECT-AMBIGUOUS` | success/retry requested while effect observation is ambiguous |
| `E-IDEMPOTENCY-CONFLICT` | reused command ID has a different digest |
| `E-AMENDMENT-INCOMPLETE` | prior object lacks exactly one disposition |
| `E-POLICY-UNKNOWN` | required policy or comparison relation absent/incomparable |

Errors are stable oracle outputs, not exception strings. A command can return one primary error
plus a sorted `related_errors` list; the primary-error precedence is the table order above.

## Exact fixture-oracle sequences

The future red bundle expands each symbolic object below into literal strict JSON and replaces
every `D(...)` with its computed digest. `+EVENT` means exactly that ordered event type is emitted;
`NOEVENT` means none. Any additional event, receipt, state change or error code falsifies the
oracle.

| Fixture | Initial/command sequence | Exact receipt/event/final oracle |
|---|---|---|
| `F-M1A-001` | empty; owner records intent/accepts bounded goal; Head starts ARM with its executive lease; ARM proposes one-node DAG; gate records capacity; ARM reserves budget/derives the packet with its work lease and route assignment; worker result; deterministic gate pass; verifier pass | every command `accepted`; `+OwnerIntentRecorded,+GoalSpecAccepted,+ArmRunStarted,+PlanRevisionAdmitted,+CapacityObservationRecorded,+BudgetReserved,+WorkPacketDerived,+WorkerResultRecorded,+GateResultRecorded,+PlanVerifierDecisionRecorded`; node `complete`, plan `terminal-verified`; final `D(state)` repeats byte-identically |
| `F-M1A-002` | isolated decode cases omit command auth, GoalSpec outcome, acceptance gate or policy digest | each returns `DecodeFailure/E-SCHEMA-MISSING-FIELD`; `NOEVENT`; no receipt, ArmRun or plan; genesis state digest unchanged. A separate structurally valid command with unknown `auth_ref` returns `refused/E-AUTH-MISSING` |
| `F-M1A-003` | accepted parent; ARM proposes child with added capability/path/route/egress or higher integer budget | `refused/E-SCOPE-WIDEN` or `E-BUDGET-WIDEN`; `NOEVENT`; accepted parent/active-plan projection unchanged |
| `F-M1A-004` | accepted goal; propose separately a two-node cycle and a node with absent dependency | `refused/E-DAG-CYCLE` then `refused/E-DAG-DEPENDENCY`; `NOEVENT` for each; no partial node/plan admission; stable sorted witness |
| `F-M1A-005` | active two-node plan whose disjoint aggregate ownership is exact; both nodes execute, pass their gates and are consumed by an exact v1 plan-verifier pass; one node is exactly compatible and one is affected; Owner submits the closed atomic amendment composite with a separately attested ARM replacement plan and complete disposition | accepted amendment emits `+GoalSpecAmended,+PlanRevisionAdmitted` then sorted disposition events; compatible definition/result `retain-terminal`; affected node `invalidate`; old plan superseded; every old packet/lease stale; the newly active replacement plan is `nonterminal` until its own gates and verifier decision; genesis replay repeats the same `D(state)` |
| `F-M1A-006` | state from 005 and a separate state after `replace-work-lease`; submit result under old packet | each `refused/E-STALE-GOAL` or `E-STALE-LEASE` by variant; `NOEVENT`; no executing/result/effect state |
| `F-M1A-007` | exact failed GateResult at packet attempt 1; GoalSpec/TaskNode share retry policy with `retry_maximum=2` and both attempt budgets are 2; propose `evidence-added` delta with a new evidence digest allowed by the bound novelty map and addressing that gate | `accepted`; `+RetryAdmitted,+WorkPacketDerived`; next attempt exactly 2, decision ceiling 2 and remaining attempts 0; command candidate equals payload digest/attestation; delta digest recorded; old evidence/history unchanged |
| `F-M1A-008` | after admitted attempt 2, failure history already contains the same typed delta; propose attempt 3 with reworded prose but identical canonical delta fields | `refused/E-RETRY-NONNOVEL` before exhaustion; `NOEVENT`; no new packet, model-request marker, attempt or debit |
| `F-M1A-009` | failure at attempt 1; admit exact attempt 2, record its worker result and failed gate, then propose structurally valid attempt 3 beyond the exact ceiling | attempt 2 emits `+RetryAdmitted,+WorkPacketDerived`; attempt 3 is `refused/E-RETRY-EXHAUSTED`; then admitted `raise-blocker`/`raise-escalation` emits exactly `+BlockerRaised,+EscalationRaised`; plan not terminal-success |
| `F-M1A-010` | the PlanRevision names its required verifier actor, but the bundle has no matching current verifier attestation/result; attempt completion/verifier decision | `refused/E-VERIFIER-MISSING`; `NOEVENT`; node `gate-pending`/plan blocked, never verified/complete |
| `F-M1A-011` | exact candidate plus an earlier admitted Owner exception record bound to GoalSpec/PlanRevision/candidate/verifier-policy/operative-constitution digests, reason, expiry logical time and missing dimensions | `record-owner-verifier-exception` emits `+OwnerVerifierExceptionRecorded`; accepted decision emits `+PlanVerifierDecisionRecorded`; disposition `downgraded-pass`, assurance `downgraded`, terminal projection if otherwise complete is `terminal-verified-downgraded`, and independence vector preserves missing dimensions; any missing/mismatched/expired binding gives `E-AUTH-MISSING`/`E-VERIFIER-MISSING` and `NOEVENT`; `terminal-verified` is forbidden |
| `F-M1A-012` | active ready node plus a typed observed included-capacity exhaustion; request metered/unauthorized replacement | observation emits `+CapacityObservationRecorded`; blocker command records `+BlockerRaised` with `capacity/deferred`; replacement `refused/E-ROUTE-SPEND`, `NOEVENT`; no failure/success/debit |
| `F-M1A-013` | gate records a matching available observation for the exact nonmetered replacement route and then the exact pre-event checkpoint before a descriptor replacement within the same allowed set | observation emits `+CapacityObservationRecorded`; checkpoint emits `+CheckpointRecorded`; `replace-route` emits `+RouteAssignmentReplaced,+WorkPacketDerived`; logical actor/goal/policy/privacy/budget digests equal, new packet route/epoch differs, old packet stale |
| `F-M1A-014` | active state; Owner applies operative `current-immediate`; then submits one valid command in each transition class: plan revision, packet derivation, worker result and effect observation | pause accepted `+PauseApplied`; all four later commands are `refused/E-PAUSED`, `NOEVENT`; only status/receipt projection changes allowed |
| `F-M1A-015` | three isolated cases select checkpoint, interrupt and drain under a registry that represents all three while the operative ref remains `current-immediate`; each case also replays its accepted prefix | each future-mode record round-trips through schema; each selection is `refused/E-POLICY-UNKNOWN` with `NOEVENT`; its replay is accepted and byte-identically reconstructs the equivalent prefix/final digest |
| `F-M1A-016` | dispatched synthetic effect; gate records lost/contradictory receipt; attempt success and retry | observation accepted `+EffectObservationRecorded`, state `ambiguous/quarantined`; success/retry each `refused/E-EFFECT-AMBIGUOUS`, `NOEVENT`; plan cannot terminate verified |
| `F-M1A-017` | accepted command; resend same ID/payload, then same ID/different payload | exact duplicate returns byte-identical original receipt/`NOEVENT`; conflicting payload `conflict/E-IDEMPOTENCY-CONFLICT`/`NOEVENT`; event count unchanged after first command |
| `F-M1A-018` | canonical event fixture; replay from genesis and the typed pre-event checkpoint snapshot twice; corrupt/gap/unknown raw-event variants | valid runs have byte-identical expected events/state/`D(state)`; corrupt digest `E-DIGEST-MISMATCH`, gap `E-DIGEST-MISMATCH`, unknown version `E-SCHEMA-UNKNOWN-VERSION`; no best-effort final state |
| `F-M1A-019` | active ArmRun after admitted executive lease replacement; old ARM proposes revision | replacement emits `+ExecutiveLeaseReplaced`; old proposal is `refused/E-STALE-LEASE`; `NOEVENT`; plan digest/active revision unchanged |
| `F-M1A-020` | authenticated assigned worker submits `amend-goal-spec`; authenticated assigned verifier submits `propose-plan-revision` | each `refused/E-AUTH-PARENT-MUTATION` under the closed precedence; `NOEVENT`; GoalSpec/PlanRevision digests unchanged and verifier assignment unchanged |
| `F-M1A-021` | isolated unknown-field, unknown-schema-version and structurally valid unknown-policy-version inputs | the first two return `DecodeFailure/E-SCHEMA-UNKNOWN-FIELD` and `DecodeFailure/E-SCHEMA-UNKNOWN-VERSION`; the policy case returns `refused/E-POLICY-UNKNOWN`; `NOEVENT`; no permissive default or replay continuation |
| `F-M1A-022` | five genuinely distinct two-node graphs encode logical ancestor write/write, read/write, equal effect key, dependency-ordered disjoint ownership and unordered read/read; admitted replans carry a complete disposition set materialized as events | first three whole plans `refused/E-DAG-CONFLICT`, `NOEVENT`; ordered-disjoint and read/read variants emit `+ReplanAdmitted,+PlanRevisionAdmitted` and their sorted disposition events; all insertion permutations have identical witness/digest |
| `F-M1A-023` | Owner amendment omits one old node/effect/lease disposition | `refused/E-AMENDMENT-INCOMPLETE`; `NOEVENT`; old GoalSpec/plan/packets/leases remain current exactly; no partial fence increment |

## Schema and red-bundle freeze gate

Before reducer implementation begins, M1A-01 MUST materialize and review the strict schemas from
the wire profile without changing its shape. M1A-02 MUST then produce one manifest enumerating
exactly F-M1A-001–023, every literal input/expected file, its SHA-256, expected command/receipt/
event/error counts and expected final state digest. An independent red-runner must validate all
bundles against the accepted schemas, prove that every required object and error above appears,
and show every positive fixture fails only because the reducer is not yet implemented. After that
commit, any schema/profile/oracle change is a new reviewed PlanRevision with explicit invalidated
tests; implementation may not silently edit an expected result to make code pass.

Passing these fixtures would prove conformance only to the pure M1A contract. It would not prove
production authentication, durable replay, runtime planning quality, provider/process/plugin/
SQLite/Git behavior, external-effect safety, performance or Option 2 superiority.

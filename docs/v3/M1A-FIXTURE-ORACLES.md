---
title: M1A deterministic fixture-oracle blueprint
status: normative-blueprint-for-future-build-not-executed
last-updated: 2026-09-03
---

# M1A deterministic fixture-oracle blueprint

This document closes the machine grammar and expected oracle for the future M1A build. It is a
documentation specification, not an executable fixture set or runtime result. A separately
authorized M1A task MUST freeze the literal sanitized JSON bundles and their expected digests as
its first red-test commit before implementing a reducer. If a literal bundle cannot be derived
without another semantic choice, construction stops for Lucas; code must not guess.

The canonical planning meanings remain in
[AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md). The scope and construction DAG remain in
[M1A-AUTONOMOUS-PLANNING.md](M1A-AUTONOMOUS-PLANNING.md). This file owns only the M1A fixture
alphabet and oracle projection.

## Canonical bundle and digest rules

Every bundle is strict JSON with this closed top-level shape:

```text
fixture_schema_version = "m1a-fixture-1"
fixture_id
description
authority_fixtures[]
policy_fixtures[]
initial_events[]
commands[]
expected_receipts[]
expected_events[]
expected_final_state
expected_final_digest
```

Unknown or duplicate fields fail. Strings, arrays, maps, integers and nesting use explicit schema
limits. No float, non-I-JSON value, wall time, random value, environment value, filesystem
observation or unordered-map iteration participates.

`D(x)` means lowercase hexadecimal SHA-256 of RFC 8785 canonical JSON for `x` with its own
`content_digest` field omitted. Every future literal expected digest is computed by that rule and
committed in the red bundle; placeholders such as `D(x)` are forbidden in the executable bundle.
Fixture IDs and logical times are literal inputs. Commands use `CMD-<fixture>-<nn>`; receipts use
`RCPT-<fixture>-<nn>`; admitted events use `EV-<fixture>-<nn>`, where `nn` is the zero-padded
command or stream position. The event stream starts at sequence 1 and binds the previous event
digest, or a schema-defined genesis digest at sequence 1.

An exact duplicate command ID and digest returns the byte-identical original receipt and emits no
event. The same command ID with another digest returns `conflict/E-IDEMPOTENCY-CONFLICT` and emits
no event. Every refusal returns one deterministic receipt with `state_before_digest`, unchanged
`state_after_digest`, empty `event_ids`, and an error from the closed registry below.

## Synthetic authority and policy fixtures

M1A does not implement or claim production authentication. Each bundle supplies an immutable
`FixtureAuthorityAttestation` with `attestation_id`, `actor_id`, closed `actor_role`, sorted
`allowed_command_types`, `candidate_digest`, `authority_policy_digest` and
`constitution_policy_digest`. A command is fixture-authorized only when its exact `auth_ref`,
actor, type, candidate and policy digests match that supplied table. Missing, unknown or
mismatched references fail. No boolean such as `trusted=true` is permitted.

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

Privacy classes and route capabilities are finite identifiers supplied by a known policy fixture.
The fixture policy provides the partial order and allowed set. Unknown or incomparable values
fail; the reducer performs set inclusion and exact integer comparison only.

## Closed command and event alphabets

| Command type | Fixture-authorized role | Admitted event type |
|---|---|---|
| `record-owner-intent` | `owner` | `OwnerIntentRecorded` |
| `accept-goal-spec` | `owner` | `GoalSpecAccepted` |
| `amend-goal-spec` | `owner` | `GoalSpecAmended`, then ordered disposition events |
| `start-arm-run` | `head` | `ArmRunStarted` |
| `propose-plan-revision` | `arm` | `PlanRevisionAdmitted` or no event on whole-plan refusal |
| `derive-work-packet` | `arm` request; kernel derives | `WorkPacketDerived` |
| `replace-work-lease` | `head` | `WorkLeaseReplaced` |
| `replace-route` | `head` | `RouteAssignmentReplaced` |
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
all required gates passed, a passing plan-verifier decision and no open blocker, escalation,
retry, stale packet or ambiguous effect.

## Closed error registry

| Error | Mechanical condition |
|---|---|
| `E-SCHEMA-UNKNOWN-FIELD` | any field outside the exact schema |
| `E-SCHEMA-UNKNOWN-VERSION` | fixture/object/policy/novelty/event version not registered |
| `E-SCHEMA-DUPLICATE` | duplicate JSON key or stable object ID |
| `E-SCHEMA-BOUND` | configured size/count/depth/integer bound exceeded |
| `E-DIGEST-MISMATCH` | canonical digest or event chain mismatch |
| `E-AUTH-MISSING` | required synthetic authority reference absent/unknown |
| `E-AUTH-ROLE` | actor/command/assignment tuple unauthorized |
| `E-AUTH-PARENT-MUTATION` | worker/verifier attempts GoalSpec or PlanRevision mutation |
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
| `F-M1A-001` | empty; owner records intent/accepts bounded goal; Head starts ARM; ARM proposes one-node DAG/derives packet; worker result; deterministic gate pass; verifier pass | every command `accepted`; `+OwnerIntentRecorded,+GoalSpecAccepted,+ArmRunStarted,+PlanRevisionAdmitted,+WorkPacketDerived,+WorkerResultRecorded,+GateResultRecorded,+PlanVerifierDecisionRecorded`; node `complete`, plan `terminal-verified`; final `D(state)` repeats byte-identically |
| `F-M1A-002` | variants omit Owner auth, outcome, acceptance gate or policy digest; attempt `accept-goal-spec` | `refused/E-AUTH-MISSING` for auth variant, otherwise the applicable first schema error; `NOEVENT`; no ArmRun/plan; genesis state digest unchanged |
| `F-M1A-003` | accepted parent; ARM proposes child with added capability/path/route/egress or higher integer budget | `refused/E-SCOPE-WIDEN` or `E-BUDGET-WIDEN`; `NOEVENT`; accepted parent/active-plan projection unchanged |
| `F-M1A-004` | accepted goal; propose separately a two-node cycle and a node with absent dependency | `refused/E-DAG-CYCLE` then `refused/E-DAG-DEPENDENCY`; `NOEVENT` for each; no partial node/plan admission; stable sorted witness |
| `F-M1A-005` | active two-node plan with one exact compatible complete node and one affected node; Owner tightens goal with complete disposition | accepted amendment emits `+GoalSpecAmended` then sorted disposition events; compatible definition/result `retain-terminal`; affected node `invalidate`; old plan superseded; every old packet/lease stale; repeated replay same `D(state)` |
| `F-M1A-006` | state from 005 and a separate state after `replace-work-lease`; submit result under old packet | each `refused/E-STALE-GOAL` or `E-STALE-LEASE` by variant; `NOEVENT`; no executing/result/effect state |
| `F-M1A-007` | exact failed GateResult; propose `evidence-added` delta with a new evidence digest addressing that gate and one remaining attempt | `accepted`; `+RetryAdmitted,+WorkPacketDerived`; exactly next attempt; delta digest recorded; old evidence/history unchanged |
| `F-M1A-008` | failure history already contains same typed delta; propose reworded prose with identical canonical delta fields | `refused/E-RETRY-NONNOVEL`; `NOEVENT`; no new packet, model-request marker, attempt or debit |
| `F-M1A-009` | failure at exact attempt maximum; propose structurally valid new delta | `refused/E-RETRY-EXHAUSTED`; then admitted `raise-blocker`/`raise-escalation` emits exactly `+BlockerRaised,+EscalationRaised`; plan not terminal-success |
| `F-M1A-010` | all worker results/gates except required verifier assignment/result; attempt completion/verifier decision | `refused/E-VERIFIER-MISSING`; `NOEVENT`; node `gate-pending`/plan blocked, never verified/complete |
| `F-M1A-011` | exact candidate plus fixture Owner exception attestation bound to GoalSpec verifier-policy and operative constitution digests, reason, expiry logical time and missing dimensions | accepted `+PlanVerifierDecisionRecorded`; decision label `downgraded-pass`, independence vector preserves missing dimensions; any missing/mismatched binding gives `E-AUTH-MISSING`/`E-VERIFIER-MISSING` and `NOEVENT` |
| `F-M1A-012` | active ready node plus observed included-capacity exhaustion; request metered/unauthorized replacement | blocker command records `+BlockerRaised` with `capacity/deferred`; replacement `refused/E-ROUTE-SPEND`, `NOEVENT`; no failure/success/debit |
| `F-M1A-013` | checkpointed node and permitted nonmetered replacement descriptor within the same allowed set | `replace-route` accepted with `+RouteAssignmentReplaced,+WorkPacketDerived`; logical actor/goal/policy/privacy/budget digests equal, new packet route/epoch differs, old packet stale |
| `F-M1A-014` | active state; Owner applies operative `current-immediate`; then plan/packet/result/effect commands | pause accepted `+PauseApplied`; each later command `refused/E-PAUSED`, `NOEVENT`; only status/receipt projection changes allowed |
| `F-M1A-015` | fixture registry contains future checkpoint/interrupt/drain values but operative ref is `current-immediate`; round-trip/replay | schema accepts values as inert records; no behavior/event change; attempting to select one under current constitution is `refused/E-POLICY-UNKNOWN`; same final digest as equivalent state without selection attempt |
| `F-M1A-016` | dispatched synthetic effect; gate records lost/contradictory receipt; attempt success and retry | observation accepted `+EffectObservationRecorded`, state `ambiguous/quarantined`; success/retry each `refused/E-EFFECT-AMBIGUOUS`, `NOEVENT`; plan cannot terminate verified |
| `F-M1A-017` | accepted command; resend same ID/payload, then same ID/different payload | exact duplicate returns byte-identical original receipt/`NOEVENT`; conflicting payload `refused/E-IDEMPOTENCY-CONFLICT`/`NOEVENT`; event count unchanged after first command |
| `F-M1A-018` | canonical event fixture; replay from genesis and supplied checkpoint twice; corrupt/gap/unknown variants | valid runs have byte-identical expected events/state/`D(state)`; corrupt digest `E-DIGEST-MISMATCH`, gap `E-DIGEST-MISMATCH`, unknown version `E-SCHEMA-UNKNOWN-VERSION`; no best-effort final state |
| `F-M1A-019` | active ArmRun after executive lease replacement; old ARM proposes revision | `refused/E-STALE-LEASE`; `NOEVENT`; plan digest/active revision unchanged |
| `F-M1A-020` | worker then verifier use parent-mutation command types | each `refused/E-AUTH-PARENT-MUTATION`; `NOEVENT`; GoalSpec/PlanRevision digests unchanged and verifier assignment unchanged |
| `F-M1A-021` | separate unknown-field and unknown-policy-version inputs | `refused/E-SCHEMA-UNKNOWN-FIELD` and `refused/E-SCHEMA-UNKNOWN-VERSION`/`E-POLICY-UNKNOWN` by layer; `NOEVENT`; no permissive default or replay continuation |
| `F-M1A-022` | graphs for logical ancestor write/write, read/write, equal effect key, disjoint ordered paths and read/read | first three whole plans `refused/E-DAG-CONFLICT`, `NOEVENT`; disjoint ordered and read/read variants emit one `+PlanRevisionAdmitted`; all insertion permutations have identical witness/digest |
| `F-M1A-023` | Owner amendment omits one old node/effect/lease disposition | `refused/E-AMENDMENT-INCOMPLETE`; `NOEVENT`; old GoalSpec/plan/packets/leases remain current exactly; no partial fence increment |

## Red-bundle freeze gate

Before M1A reducer/schema implementation begins, M1A-01 MUST produce one manifest enumerating
exactly F-M1A-001–023, every literal input/expected file, its SHA-256, expected command/receipt/
event/error counts and expected final state digest. An independent red-runner must parse all
bundles, prove that every required object and error above appears, and show every positive fixture
fails only because the reducer is not yet implemented. After that commit, any oracle change is a
new reviewed PlanRevision with explicit invalidated tests; implementation may not silently edit
an expected result to make code pass.

Passing these fixtures would prove conformance only to the pure M1A contract. It would not prove
production authentication, durable replay, runtime planning quality, provider/process/plugin/
SQLite/Git behavior, external-effect safety, performance or Option 2 superiority.

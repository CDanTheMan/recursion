---
title: M1A — Autonomous Planning Contract and Replay Baseline
status: construction-ready-proposal-not-authorized
last-updated: 2026-09-03
---

# M1A — Autonomous Planning Contract and Replay Baseline

M1A is the smallest proposed construction slice that can demonstrate the autonomous-planning
contract in [AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md). It is pure schema, validation,
deterministic WorkPacket derivation and in-memory replay over sanitized fixtures. It does not
prove a v3 runtime, plan quality, external-effect safety or performance.

The standalone handoff prompt is
[prompts/m1a-autonomous-planning-contract.md](prompts/m1a-autonomous-planning-contract.md).
Neither this document nor that prompt authorizes execution.

## Parent goal and exact scope

**Parent goal:** demonstrate, with pure deterministic behavior, that an authenticated Owner intent
can become an accepted immutable GoalSpec, an ARM can propose a bounded task DAG and derived
WorkPacket, exact evidence can drive gate/retry/replan/escalation, and replay reaches the same
verified terminal plan without any external effect or authority widening.

**Allowed paths for a future separately authorized implementation:**

- `schemas/control-plane/v3/planning/**`
- `scripts/v3/planning/**`
- `scripts/tests/v3/planning/**`
- `docs/v3/**`

Everything else is denied. The future task may create its own bounded local implementation
commit only if its Owner prompt authorizes it. M1A code/tests MUST NOT invoke Git or modify
repository state themselves.

**Non-goals:** no provider/model calls; terminal or subprocess launch; plugin loading/execution;
SQLite or other database; v1/v2 migration; network; credential/account access; Git command or
ref/worktree mutation; publication, merge, deployment or service change; live PAUSE/config
change; external effect; performance or comparative-quality claim; native agent loop; UI;
scientific metadata adapter; production default or constitutional amendment.

Sanitized fixtures contain no repository-private product/business data, credentials, private
canary identity or real infrastructure identifiers.

## Included object and behavior floor

M1A includes only strict forms of `OwnerIntent`, `GoalSpec`, `GoalSpecAmendment`, `ArmRun`,
`PlanRevision`, `PlanTransition`, `TaskNode`, `WorkPacket`, `GateResult`, `RetryDecision`,
`ReplanDecision`, `Blocker`, `Escalation`, `PlanVerifierDecision`, command/receipt/event,
executive/work lease, policy/route/budget references, checkpoint and a synthetic effect-state
record. The last four are inert records used to validate binding/fencing/ambiguity; they do not
connect to providers, processes, stores or effectors.

Included pure behavior:

1. strict schema parse and RFC 8785 canonical digest;
2. cross-record owner/authority/privacy/egress/route/budget/source/policy/verifier attenuation;
3. GoalSpec acceptance/amendment and complete disposition validation;
4. DAG cycle, missing-dependency and path/effect-conflict admission;
5. pure TaskNode state transition and WorkPacket derivation;
6. GateResult, bounded novelty retry, replan, blocker and escalation decisions;
7. lease/epoch/PAUSE staleness checks;
8. append-only in-memory commands/events/receipts and deterministic replay; and
9. verified terminal-plan closure.

There is no clock, randomness, environment discovery or I/O in the reducer. Fixtures provide
logical time and immutable capacity/route/policy observations as data.

## Sequential construction DAG

| Node | Depends on | Exclusive output | Machine-checkable gate | Stop condition |
|---|---|---|---|---|
| M1A-01 freeze fixture vocabulary | accepted M1A prompt | `docs/v3/**` mapping plus red fixture manifests | every field maps to canonical planning contract; no second owner | two meanings for an authority/state term |
| M1A-02 strict schemas/canonicalization | M1A-01 | `schemas/control-plane/v3/planning/**` | meta-schema/load tests; unknown/unbounded/duplicate/non-I-JSON/version failures | current and future PAUSE cannot be separate values |
| M1A-03 cross-record validator/DAG admission | M1A-02 | `scripts/v3/planning/validation/**` | authority/budget/privacy/source/policy/DAG conflict fixtures pass | validation needs network, operational state or model judgment |
| M1A-04 pure decider/reducer/packet derivation | M1A-03 | `scripts/v3/planning/replay/**` | command idempotency, lease/fence, legal transition and replay digest fixtures pass | output depends on wall time, process, network or unordered iteration |
| M1A-05 complete conformance fixtures | M1A-04 | `scripts/tests/v3/planning/**` | F-M1A-001–023 pass twice from clean in-memory state | a required failure can only be asserted by prose |
| M1A-06 independent exact-candidate verification | M1A-05 | verifier receipt under `docs/v3/**` | fresh runner repeats exact commands/candidate digest and records dissent/limits | missing verifier, dirty/out-of-scope candidate or false independence claim |

The DAG is sequential because schema ownership and reducer semantics overlap. Parallel work is
not an acceptance objective. A future implementer may split read-only review but not concurrent
writes to a shared object family.

## Required fixtures, expected results and decisive falsifiers

Each fixture is a sanitized, content-addressed input bundle with expected ordered events,
receipts, final state/digest and error code. “No event” below permits only a typed refused command
receipt; it forbids the requested authoritative transition.

| ID | Fixture | Expected result | Decisive falsifier |
|---|---|---|---|
| F-M1A-001 | accepted bounded plan reaches verified completion | authenticated intent and accepted GoalSpec admit one plan/node/packet; exact passing gates and plan-verifier decision produce `terminal-verified` | terminal state without every required event/gate, or replay digest differs |
| F-M1A-002 | incomplete or unauthenticated GoalSpec | typed refusal before ArmRun/plan admission; no authoritative event | missing field/authentication receives accepted status or child work exists |
| F-M1A-003 | child authority or budget widening | typed subset/budget refusal; parent projection unchanged | any wider path, capability, route, egress or limit appears in descendant state |
| F-M1A-004 | cyclic or unsatisfied DAG variants | cycle and missing dependency each refuse the entire PlanRevision atomically | partial graph/node admits or topological result varies |
| F-M1A-005 | amendment retains unaffected and invalidates stale work | new GoalSpec/PlanRevision; complete old-node disposition; compatible evidence retained; affected node invalidated; all old packets/leases stale | an affected packet survives, an unaffected result changes nondeterministically, or a node is omitted |
| F-M1A-006 | stale packet after amendment or lease replacement | execute command refuses with stale goal/plan/lease epoch; no worker/effect transition | stale packet reaches `executing` or emits a success result |
| F-M1A-007 | gate failure with genuine novelty | exact failure plus typed material diff admits exactly one bounded RetryDecision and new packet | identical packet is reissued or more than the authorized attempt is created |
| F-M1A-008 | repetitive retry without novelty | refusal occurs before any sampler/model-turn request event; typed non-novel blocker | another attempt/model request is emitted or quota is debited |
| F-M1A-009 | retry exhaustion | task becomes failed/blocked and escalation targets the correct Head/Owner seam | implicit retry, silent terminal success or missing failure history |
| F-M1A-010 | missing required verifier | node/plan remains blocked; `missing` cannot satisfy a gate | `verified`, `complete` or terminal pass appears |
| F-M1A-011 | risk-approved verifier downgrade | exact-candidate exception receipt binds authenticated Lucas authority, GoalSpec verifier-policy and operative constitution digests, reason, expiry and missing dimensions; result label remains downgraded | output reports full/cross-family independence, lacks an authority/policy digest, or applies to another candidate |
| F-M1A-012 | quota exhaustion | typed capacity blocker/deferred state; no route or metered-spend widening | metered route is selected, task fails as semantic error, or state says success |
| F-M1A-013 | route replacement | new assignment/packet at checkpoint preserves logical actor, GoalSpec, policy, privacy and budget bindings | actor or authority changes, old packet remains live, or new account/spend appears |
| F-M1A-014 | operative current PAUSE | `current-immediate` epoch refuses planning, model, worker and effect transitions; awareness/status receipt only | any new plan/packet/action/effect transition admits |
| F-M1A-015 | future PAUSE policies represented but non-operative | checkpoint/interrupt/drain schemas round-trip under distinct future policy refs while operative selection stays `current-immediate` | serialized future value changes behavior without constitutional amendment |
| F-M1A-016 | ambiguous external-effect record | lost/contradictory synthetic receipt produces `ambiguous` and quarantine; never success/retry | replay, rollback or timeout converts it to success or admits duplicate dispatch |
| F-M1A-017 | duplicate command | same command id+digest returns original receipt with no new event; same id+different digest conflicts | event count/effect count increases or conflicting payload is accepted |
| F-M1A-018 | deterministic event replay | genesis and checkpoint replays produce byte-identical canonical projection and plan digest across repeated runs | digest/order changes or corrupt/gap/unknown event is best-effort accepted |
| F-M1A-019 | stale executive lease | proposal refuses before authoritative PlanTransition; current plan unchanged | stale holder creates/revises/adopts a plan |
| F-M1A-020 | worker/verifier parent mutation | command type/authority refusal; no GoalSpec/PlanRevision mutation | either actor amends goal/DAG or verifier assigns itself |
| F-M1A-021 | unknown fields or policy versions | strict parse/admission refusal before state change | field is ignored, permissive default selected or replay continues |
| F-M1A-022 | overlapping paths/effects | unordered write/write, write/read and same-effect-owner variants refuse; explicitly ordered disjoint ownership admits | concurrent conflicting owners admit or harmless ordered graph refuses nondeterministically |
| F-M1A-023 | incomplete amendment disposition | entire amendment/transition refuses atomically | unclassified old node/effect/lease remains live or amendment partially applies |

## Machine-checkable acceptance gates

M1A is ready to call complete only if a future exact candidate satisfies all of these:

1. a manifest enumerates every schema, command, event, state and fixture ID with no duplicates or
   unknown entries;
2. strict schema/meta-schema tests reject unknown fields, duplicate keys, non-I-JSON, malformed
   IDs/digests, unknown versions and configured size/depth/count overflow;
3. all F-M1A-001–023 expected receipt/event/state/digest fixtures pass twice;
4. property tests generate parent/child combinations and never admit authority, privacy, egress,
   path, route, budget or effect widening;
5. graph property tests reject cycles, missing dependencies and unordered ownership conflicts;
6. replay from genesis and each supplied checkpoint is byte/digest identical; corrupt, missing,
   duplicate-conflict and unknown-version events fail closed;
7. a static import/call scan proves the M1A package and tests have no network, provider/model,
   subprocess/terminal, plugin, SQLite/database, Git or publication/effect adapter dependency;
8. tests prove no wall-clock, random, environment or filesystem observation influences the
   reducer; sanitized fixture loading is the only test I/O;
9. legacy `scripts/tests/recursion-v2-mvp.test.py` passes unchanged; no v2 result is described as
   a v3 runtime/performance result;
10. `git diff --check`, relative-link, secret/private-data and changed-path checks pass;
11. the exact candidate begins and ends its gate clean except for authorized M1A paths; and
12. an assigned verifier independently reruns the exact candidate and records limitations; an
    unavailable verifier blocks instead of passing.

Suggested future command names may be frozen in the construction task after repository tooling
is inspected; the semantic gates above are canonical, not a dependency on one test runner.

## Explicit M1B and M1C boundaries

**M1B — Route, plugin and process requirement contracts:** may add inert schemas/fixtures for
route adapters, plugin manifests/grants and terminal/process broker messages. It still makes no
provider call, launches no process, executes no plugin and changes no runtime state. It begins
only after M1A passes and receives a separate GoalSpec.

**M1C — Source/effect and persistence requirement contracts:** may add inert scientific-source,
effect reconciliation, publication and persistence/migration schemas with synthetic fixtures.
SQLite/WAL implementation, live source/provider adapters, external effects, Git, publication and
migration remain later separately authorized milestones. This prevents research and state
machinery from bloating M1A's privileged planning slice.

## Readiness verdict

The documentation contract and fixture oracle are ready for a separately authorized M1A build,
subject to final same-family Terra adjudication and the campaign gates. Numeric production
budgets, future PAUSE ratification, provider behavior and broader architecture superiority are
not prerequisites because M1A encodes them only as strict inert references or explicit unknowns
that block.

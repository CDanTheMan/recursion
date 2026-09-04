---
title: Recursion v3 frontier harness research — tranche two campaign
status: active-documentation-demonstration
last-updated: 2026-09-03
campaign-id: FHAR2-20260903
parent-goal: ratified Option 2 construction architecture
---

# Frontier harness research — tranche two campaign

This is an inspectable documentation demonstration of proposed Recursion planning semantics. It is
not an operative `GoalSpec`, a constitutional amendment, a runtime, a benchmark result or
construction authorization. The current `CONTROL_PLANE.md` and immediate PAUSE behavior remain
operative throughout this docs-only campaign.

## OwnerIntent

`OI-FHAR2-20260903-01` records Lucas's 2026-09-03 direction:

1. Ratify Option 2: a small deterministic Recursion kernel with typed fail-closed adapters.
2. Canonize the versioned Recursion release as the sole canonical harness/control-plane dependency.
   External engines, models, providers, terminals, plugins, databases and a Hermes compatibility
   path may integrate only as non-authoritative adapters; ordinary pinned software dependencies are
   not prohibited.
3. Authorize a constitutional-amendment packet covering that ownership boundary, checkpoint-first
   future PAUSE behavior and risk-scaled verifier downgrade classes.
4. Launch a second docs-only research tranche covering formal kernel modeling, runtime/language
   experiments, durable storage/IPC, terminal/process fault matrices, plugin isolation and future
   surfaces, cache/context/token measurement, evaluation corpus science, and a lean versioned release
   boundary.

This intent authorizes public-source research and documentation edits under `docs/v3/**`. It does
not authorize editing the live constitution, runtime code, tests, configuration or state.

## Immutable campaign GoalSpec

| Field | Bound value |
|---|---|
| GoalSpec ID | `GS-FHAR2-20260903-01` |
| version | 1 |
| owner | Lucas |
| parent | `OR-018`, `OR-019`, `OR-020` |
| objective | Produce a source-pinned, falsifiable research and amendment-design baseline sufficient to authorize or reject the next pure Option 2 construction experiment. |
| allowed writes | `docs/v3/**` only |
| allowed reads | repository state and public primary sources needed for the assigned question |
| authority floor | Lucas remains final authority; current Hermes/current-PAUSE constitution governs live behavior until a later exact amendment is reviewed and applied. |
| privacy | no secrets, credentials, private canary, business data, unpublished raw artifacts or private repository content may leave the permitted local/public routes |
| egress | public primary-source retrieval only; any eligible external-family challenge receives a separately recorded public/synthetic packet |
| routes | Sol lead; at most eight `gpt-5.6-luna`/`xhigh` workers in two waves of at most four; then at most two `gpt-5.6-terra`/`xhigh` adjudicators |
| spending | no billing enablement, credits, metered fallback, provider/account/configuration change or guessed route alias |
| metrics | authority, safety and privacy are hard floors; accepted quality, reliability, token/cache efficiency, latency, CPU, memory, I/O, dependency/code surface and owner-review debt receive equal Pareto treatment |
| terminal result | complete only after every gate has an inspectable disposition, both Terra lanes review an exact candidate, all tests/checks pass and the committed tree is clean |

Immutable fields are identity, owner, objective, paths, non-goals, authority/privacy/egress/route/
spending boundaries, metric rule and acceptance gates. Status and append-only receipts are mutable.
Any scope or policy change requires a new `PlanRevision`; no original field is silently rewritten.

## Non-goals

- Do not edit `CONTROL_PLANE.md`, `ANCHOR.md`, `state/**`, implementation, tests, scripts,
  configuration, authentication, plugins, providers or environment variables.
- Do not execute M1A, prototypes, TLA+ models, benchmarks, process/terminal fault tests, migrations,
  canaries or external effects.
- Do not select Rust, Go, CPython, SQLite, JSONL, binary IPC, a terminal framework or numeric
  performance budget without comparative evidence.
- Do not claim that source inspection, model agreement or v2 regression tests prove v3 behavior.
- Do not push, publish, merge, deploy, open a PR, change PAUSE or spend money.

## Initial PlanRevision and task DAG

`PR-FHAR2-20260903-01` is the immutable initial plan.

| Task | Owner | Depends on | Deliverable |
|---|---|---|---|
| `TASK-FHAR2-000` | Sol | none | orientation, clean-tree/scope/ancestor verification |
| `TASK-FHAR2-010` | Sol | 000 | owner-decision, GoalSpec and campaign-plan checkpoint |
| `TASK-FHAR2-101` | Luna | 010 | formal kernel transition-system/model-checking packet |
| `TASK-FHAR2-102` | Luna | 010 | runtime/language/kernel-boundary experiment packet |
| `TASK-FHAR2-103` | Luna | 010 | durable log, projection, storage and IPC packet |
| `TASK-FHAR2-104` | Luna | 010 | Windows/Linux terminal and process fault-matrix packet |
| `TASK-FHAR2-105` | Luna | 010 | plugin isolation, capability and frontend-protocol packet |
| `TASK-FHAR2-106` | Luna | 010 | context, cache and token-measurement packet |
| `TASK-FHAR2-107` | Luna | 010 | benchmark corpus, statistics and owner-review packet |
| `TASK-FHAR2-108` | Luna | 010 | versioned release, adapter migration, license and adversarial-minimum packet |
| `TASK-FHAR2-200` | Sol | 101–108 | source reinspection, evidence matrix, experiment specifications and active-doc synthesis |
| `TASK-FHAR2-301` | Terra | 200 | authority, amendment, PAUSE and verifier-policy adjudication |
| `TASK-FHAR2-302` | Terra | 200 | evidence, performance-method and construction-readiness adjudication |
| `TASK-FHAR2-400` | Sol | 301–302 | dissent repair or explicit unresolved disposition |
| `TASK-FHAR2-500` | Sol | 400 | exact-candidate validation, commits and final clean-tree disposition |

Only nodes whose dependencies are complete may run. Luna discovery nodes are mutually independent.
Terra nodes are prohibited before the Sol synthesis candidate is committed. A failed gate returns to
`TASK-FHAR2-400`; it never silently becomes a pass.

## Worker WorkPackets

| Packet | Exact question |
|---|---|
| `WP-FHAR2-101` | What smallest transition system, invariants, refinement boundary and bounded model can falsify Option 2's command/event/lease/PAUSE/effect/replay contract before code? |
| `WP-FHAR2-102` | Which language/runtime and dependency-boundary mechanisms plausibly fit the privileged kernel, and what matched build/runtime/fault experiment could choose among CPython, Rust and Go without reputation-based selection? |
| `WP-FHAR2-103` | Which append, durability, projection, snapshot, IPC framing, backpressure and recovery mechanisms should JSONL/SQLite/content-addressed candidates expose, and what exact fault matrix decides among them? |
| `WP-FHAR2-104` | What native Windows/Linux process, PTY/ConPTY, job/cgroup, attach/detach, resize, rendering, accessibility and slow-client behavior must be tested for a polished multi-terminal harness? |
| `WP-FHAR2-105` | What digest, signature, manifest, capability, isolation, lifecycle, revocation and frontend bridge contract prevents plugins or views from becoming authority or imposing disabled-path cost? |
| `WP-FHAR2-106` | How should Recursion measure context fidelity, provider/local cache behavior, token accounting, compaction and privacy domains without assuming portable controls or counters? |
| `WP-FHAR2-107` | What sealed corpus, deterministic oracle, sampling, statistical and human-review design can attribute gains to harness components while controlling contamination, variance and judge bias? |
| `WP-FHAR2-108` | What is the smallest versioned Recursion release/boot/recovery contract that makes every external harness optional, defines Hermes migration/removal and license obligations, and resists architecture or dependency creep? |

Every worker returns: worker ID; exact model/effort; question; primary-source URL and immutable
revision/version/date/locator; claims and counterevidence; applicability/limits; confidence;
adopt/adapt/reject recommendation; decisive falsifier; unresolved question; and no hidden reasoning.
Workers are read-only, may not commit or edit, and may not spawn nested agents.

## Verifier assignments

- Sol personally opens every consequential primary source and owns all documentation changes.
- `WP-FHAR2-301` checks the exact amendment design, current/future constitutional separation,
  GoalSpec/actor authority, PAUSE/effects and verifier downgrade semantics.
- `WP-FHAR2-302` checks source sufficiency, licenses, competing options, experiment closure,
  performance claims, lean boundaries and exact validation.
- Both Terra routes are same-family review and must be labeled accordingly.

## Acceptance gates

| Gate | Required result |
|---|---|
| `GATE-FHAR2-01` | Every changed path is under `docs/v3/**`; starting and final trees are clean. |
| `GATE-FHAR2-02` | `OR-018`–`OR-020` and the immutable campaign GoalSpec are recorded before discovery. |
| `GATE-FHAR2-03` | Option 2 is consistently labeled ratified architecture, not measured superiority or construction authorization. |
| `GATE-FHAR2-04` | “Recursion sole dependency” is defined as canonical authority/recovery ownership and does not falsely ban ordinary libraries or optional adapters. |
| `GATE-FHAR2-05` | One exact proposed constitutional amendment packet separates current operative text, replacement text, migration, rollback and adoption evidence. |
| `GATE-FHAR2-06` | Future PAUSE has a complete per-operation/effect state-transition and ambiguity matrix; current immediate PAUSE stays operative. |
| `GATE-FHAR2-07` | Verifier risk classes, allowed downgrade dimensions, evidence labels, expiry and Lucas exception receipts are complete and fail closed. |
| `GATE-FHAR2-08` | A formal transition-system specification defines variables, initial state, next-state actions, invariants, liveness scope, environment assumptions and bounded counterexample plan. |
| `GATE-FHAR2-09` | Language/runtime selection remains a preregistered matched experiment with build, fault, performance, dependency and review measures. |
| `GATE-FHAR2-10` | Storage and IPC candidates have exact durability, framing, backpressure, crash, corruption, checkpoint and recovery comparisons. |
| `GATE-FHAR2-11` | Terminal/process research covers native Windows and Linux ownership, containment, detach/reconnect, resize, Unicode/control injection, slow clients and accessibility. |
| `GATE-FHAR2-12` | Plugin/frontend research covers artifact identity, signatures, grants, isolation, failure, reload/revocation, view protocols and zero-cost-disabled behavior. |
| `GATE-FHAR2-13` | Context/cache research separates canonical content from provider/local cache optimization and records unavailable controls/counters. |
| `GATE-FHAR2-14` | Evaluation research fixes corpus identity, contamination controls, deterministic oracles, repeated attempts, statistical rule, review debt and stop rule. |
| `GATE-FHAR2-15` | Every consequential factual claim has a primary source and version/revision/locator or is explicitly unverified. |
| `GATE-FHAR2-16` | Licenses and source applicability are recorded; copying/adaptation is not inferred from public visibility. |
| `GATE-FHAR2-17` | Every recommendation includes a competing option, failure mode and decisive experiment/falsifier. |
| `GATE-FHAR2-18` | Authority, safety and privacy remain hard floors; other metrics use declared Pareto comparison without hidden weights. |
| `GATE-FHAR2-19` | No source inspection, formal model, v2 test or same-family consensus is reported as v3 runtime/performance proof. |
| `GATE-FHAR2-20` | The claim registry, source register and relative-link checks remain deterministic and complete after additions. |
| `GATE-FHAR2-21` | The proposed release can boot/recover canonical state and refuse mutation with every optional engine/plugin/frontend absent. |
| `GATE-FHAR2-22` | Both targeted Terra adjudicators review the exact committed synthesis candidate; dissent is preserved and repaired or explicitly unresolved. |
| `GATE-FHAR2-23` | Full documentation validation and the unchanged v2 regression umbrella pass on an exact clean candidate. |
| `GATE-FHAR2-24` | Final worktree is clean; no unavailable route, counter, verifier, source or experiment is represented as a pass. |

## Stop conditions and Lucas seams

Continue unrelated ready tasks when one research lane is blocked. Stop rather than choose if work
would require editing the live constitution, exercising credentials/providers, enabling spending,
executing a prototype/benchmark/model, selecting a material non-dominated implementation default,
exposing private data, or widening the allowed path boundary. Any new owner instruction that changes
the objective, scope, policy or route envelope requires `PR-FHAR2-20260903-02`; append the trigger and
retained/invalidated/superseded nodes rather than rewriting PR01.

## PlanRevision history and receipts

| Revision | Trigger | Retained | Invalidated | Superseded | Disposition |
|---|---|---|---|---|---|
| `PR-FHAR2-20260903-01` | Lucas's 2026-09-03 ratification and tranche-two authorization | all initial tasks and boundaries | none | none | active |
| `PR-FHAR2-20260903-02` | `WP-FHAR2-107` showed the prior protocol confused 1,728 repeated attempts with 48 independent tasks and could not support its power guarantee. | GoalSpec, route/scope boundaries, task DAG and all completed work | none | prior `PROTO-FHAR-01` power/sample-size rule only | Active replacement: `PROTO-FHAR-01-R1`; no outcomes had been inspected. |
| `PR-FHAR2-20260903-03` | Both Terra adjudicators dissented on exact synthesis `af485e7401c2fb9d760c46cb8223c7365b952a4f`. | GoalSpec, task DAG, source matrix, all supported findings and passed gates | incomplete admission signature, duplicate verifier projection, ambiguous PAUSE awareness row, unregistered eager-loader assertion and stale storage/history wording | exact candidate `af485e7`; its dissent remains evidence | Repair every item, rerun validation and require both adjudicators to review the new exact candidate. |

Capacity admissions, worker results, failed gates, adjudications, validation and final disposition
append below. Earlier failures remain visible after repair.

| Receipt | Observation | Disposition |
|---|---|---|
| `PRE-FHAR2-001` | Clean `codex/v3-frontier-harness-research` at `b55a74fbcb70ce40e47f8e7809b5a15a3e7dcd87`; target `AGENTS.md` absent; effective instructions, `CONTROL_PLANE.md`, `ANCHOR.md` and active v3 campaign/evidence state reviewed. | Admit plan authoring only. No worker admitted before this checkpoint is committed. |
| `CAP-FHAR2-W1` | 2026-09-03T17:05:15-07:00; 32 logical CPUs; 30.44/63.12 GiB free memory; 644.12 GiB free system disk; 433 processes; clean plan commit `41e63d159d6948c903427824b3b422e6d253ce3b`; read-only Codex surface reported 25% used in its 10,080-minute primary window, no credit balance, no reset credits and no spend-control trip. Account identity is deliberately not retained. | Admit four Luna/xhigh workers. Point observation only; no credit is consumed or created and no metered fallback is permitted. |
| `WP-FHAR2-101-R` | `gpt-5.6-luna`/`xhigh`; bounded TLA+/PlusCal transition system, 17 safety invariants, limited liveness assumptions, refinement mapping, mutation tests and counterexample artifact contract. | Complete. Formal model design is falsification machinery, not runtime proof; TLC execution remains outside docs-only scope. |
| `WP-FHAR2-102-R` | `gpt-5.6-luna`/`xhigh`; implementation-neutral kernel API and matched CPython/Rust/Go build/runtime/fault/SBOM comparison. | Complete. No language winner selected; source mechanisms are evidence, performance remains unmeasured. |
| `WP-FHAR2-103-R` | `gpt-5.6-luna`/`xhigh`; JSONL/SQLite/CAS, framing, flush/replace, replay, backpressure and cross-platform crash/corruption matrix. | Complete. Storage serialization is not Recursion authority; JSONL-versus-SQLite remains a measured decision. |
| `WP-FHAR2-104-R` | `gpt-5.6-luna`/`xhigh`; after one bounded evidence-return for a partial first packet, closed Windows ConPTY/Job and Linux PTY/cgroup/pidfd ownership, reconnect/cursor/lease/fanout, rendering/control-injection, accessibility and terminal-matrix research. | Complete. PTY/ConPTY is transport, not process/effect authority; platform behavior remains an executable experiment. |
| `CAP-FHAR2-W2` | 2026-09-03T17:23:34-07:00; 32 logical CPUs; 30.13/63.12 GiB free memory; 644.08 GiB free system disk; 437 processes; clean wave-one commit `bf6d9caa59ff85b16048065cf253a8d21fe28d08`; read-only Codex surface still reported 25% used in its 10,080-minute primary window, no credits/reset credits and no spend-control trip. Account identity is deliberately not retained. | Admit four Luna/xhigh workers. Stable point observations support the same concurrency; no metered fallback is enabled. |
| `WP-FHAR2-105-R` | `gpt-5.6-luna`/`xhigh`; trust tiers, signed/isolated plugin lifecycle, capability intersection, fenced reload/revocation, zero-cost-disabled traps and source/origin/nonce-bound frontend bridge. | Complete. Signatures and WebAssembly isolation are bounded mechanisms, not behavioral safety or authority. Runtime/signing stack unselected. |
| `WP-FHAR2-106-R` | `gpt-5.6-luna`/`xhigh`; after one bounded supplement for source precision, defined canonical Context Capsule, route-local cache identity, observed/estimated/unknown counters and a cold/warm/fresh/cross-route experiment. | Complete. API controls do not prove CLI/OAuth behavior, subscription debit, portable cache reuse or savings. |
| `WP-FHAR2-107-R` | `gpt-5.6-luna`/`xhigh`; identified the independent-unit/power defect in `PROTO-FHAR-01` and supplied sealed-corpus, versioned-oracle, blinded-pilot, paired/hierarchical and human-review replacement `PROTO-FHAR-01-R1`. | Complete with material correction. No benchmark was run; the old power guarantee is rejected before outcome inspection. |
| `WP-FHAR2-108-R` | `gpt-5.6-luna`/`xhigh`; ReleaseId, BootReceipt, adapter-free core recovery, aggregate-scoped Hermes cutover/removal, provenance/license and dependency-admission minimum. | Complete. SemVer/signature/SBOM are insufficient alone; optional subsystems may not become boot or recovery dependencies. |
| `SYN-FHAR2-200-R` | Sol personally reinspected consequential primary sources, corrected the Cosign source pin, reconciled all eight lanes into the source/claim ledgers, drafted the exact amendment proposal and updated active specifications. | Complete candidate synthesis; commit and two exact-candidate Terra adjudications required before acceptance. |
| `WP-FHAR2-301-D1` | `gpt-5.6-terra`/`xhigh`; exact candidate `af485e7401c2fb9d760c46cb8223c7365b952a4f`; authority adjudication returned `DISSENT`. It found a competing Security/M1A independence-vector definition, stale accepted SQLite wording, a PAUSE row conflating read-only status with evidence append and one stale historical packet statement. | Material dissent accepted. Candidate cannot pass; repair under `PR-FHAR2-20260903-03` and re-review. Same-family only. |
| `WP-FHAR2-302-D1` | `gpt-5.6-terra`/`xhigh`; exact candidate `af485e7401c2fb9d760c46cb8223c7365b952a4f`; evidence/readiness adjudication returned `DISSENT`. It found two blank lines at EOF, an admission API supplied only an opaque state digest and an eager-Wasmtime-loader assertion lacked the registered source locator. | Dissent accepted. EOF defects were repaired and validation later passed on `71aa67d`; semantic/source defects are repaired under `PR-FHAR2-20260903-03`. Re-review required. Same-family only. |
| `WP-FHAR2-301-R2` | `gpt-5.6-terra`/`xhigh`; exact semantic repair candidate `adb0f02026744991402848da27761b5fdcb3e470`; authority re-adjudication returned `PASS`. All four D1 items were repaired; it identified only the non-blocking need to label M1A `session` as auxiliary rather than a canonical CA dimension. | Pass for semantic repair, same-family only. The wording seam is repaired before the final candidate; no runtime or constitutional-application proof. |
| `WP-FHAR2-302-R2` | `gpt-5.6-terra`/`xhigh`; exact semantic repair candidate `adb0f02026744991402848da27761b5fdcb3e470`; evidence/readiness re-adjudication returned `PASS`. EOF, pure admission, Wasmtime attribution, corrected evaluation and lean-boundary items passed. | Pass for semantic repair, same-family only. Exact final validation and candidate receipt still required. |
| `VAL-FHAR2-001` | Full [VALIDATION.md](VALIDATION.md) procedure passed on clean exact candidate `71aa67d9ebf42913b3ff7adf889104e3c96a9634`: path/diff, 110 claims, 17 R lanes, 8 tranche-two lanes, 106 sources, links, secret/private-path scan and unchanged v2 umbrella. | Superseded as final validation by semantic repair; retained as an intermediate pass, not proof of `adb0f02`. |
| `VAL-FHAR2-002` | Validation on `adb0f02` reached the tranche-two source-edge gate and stopped because a corrected explicit `SRC-V3-097` reference increased the set from 15 to 16. | Validator was too brittle: retain the evidence-coverage floor and unknown-ID rejection rather than forbid added registered evidence. Full rerun required on the next clean candidate. |

---
title: Recursion v3 ratified architecture target
status: owner-ratified-target-non-operative-until-amendment
last-updated: 2026-09-06
baseline-commit: 98113d6c6d3debe2a4d207c51bb1780f7356d714
---

# Recursion v3 ratified architecture target

## Mark 2 Owner direction — 2026-09-06

Persistent assistants spanning sessions/goals and configurable inter-assistant decision rights require an explicit mapping to Head, ARM, profiles and current GoalSpec amendment ownership. Compare the proposed identities, consultation/lifecycle, coherent forks, configuration propagation, Stop scopes and update/recovery accounting before formal-model freeze. OR-018/019 and immutable M1 remain unchanged; see the [Mark 2 contract obligations](foundation-research/mark2/handoff.md). No new manager tier, live process migration or universal memory-sharing default is selected.

## Platform execution requirement — 2026-09-06

OR-021/OR-022 require independently useful native and upstream execution in the first usable
release, plus combined workflows. A small native loop is required behind the existing typed
boundary; the privileged kernel remains small under OR-018. Reusing libraries is permitted.
An embedded upstream SDK that owns the agent loop is upstream execution in this taxonomy.

Every reasoning role resolves an explicit eligible execution/accounting path. The deterministic
runtime must boot, store, schedule, supervise processes, account and expose status without
continuous inference; an upstream-only workflow must not implicitly require a native planner,
reviewer, summarizer or recovery model. See the proposed
[ownership and interaction contract](foundation-research/platform-round/interaction-contract.md).
The current constitution and immutable M1 boundaries are unchanged.

## Foundation integration boundary — proposed 2026-09-05

OR-018/OR-019 remain accepted. Standalone recovery and a complete native sampling loop are
different commitments. Recursion owns canonical authority/recovery in both native and delegated
execution. An upstream engine may own sampling, native tools and session state through an optional
typed adapter. The [ownership matrix](foundation-research/compatibility.json) records each layer;
neither terminal attachment nor an SDK transfers canonical ownership. FND-004–FND-006.

Before formal-model freeze, make the M1A-to-M1C effect identity projection explicit; distinguish
work lease, writer fence, process/daemon and PAUSE/admission epochs; preserve one canonical writer,
current-immediate PAUSE and unresolved effects after partition/termination. Broker flow/replay is
either bounded model state or an explicit adapter obligation. See
`analysis.foundation.model` and `decision.foundation.model-boundary` in the
[foundation evidence](foundation-research/evidence.json) and [decisions](foundation-research/decisions.json).
These model-level mappings preserve immutable M1 contracts and the blocked OR-015 boundary.
A failed mapping requires a separately scoped repair proposal, not a silent schema change. FND-002/FND-003.

> **Ratified target, not operative authority.** `OR-018` and `OR-019` select the hierarchy and
> Recursion-owned Option 2 boundary below. The
> current `CONTROL_PLANE.md` still names Hermes as the automation-chain executive and remains
> controlling. The docs-only [amendment proposal](CONSTITUTIONAL-AMENDMENT-PROPOSAL.md) does not
> activate a replacement Head or transfer authority.

## Correct hierarchy

```text
Lucas — principal and final authority
  |
  v
Main Assistant / Recursion Head — portfolio executive
  |  model escalation, GoalSpecs, ARM lifecycle, monitoring, escalation
  |
  +--> ARM Executive — one approved parent goal
  |      implementation DAG, delegation, tactical replanning, checkpoints
  |        |
  |        +--> research / implementation / test / review / integration agents
  |                    |
  |                    +--> gates + independent verifier
  |
  +--> ARM Executive — another approved parent goal
  |
  v
Deterministic Recursion kernel
  authority | state | budgets | routing | leases | evidence | PAUSE | publication
  |
  v
Review candidate — Lucas reviews, merges, provisions, and deploys
```

The Recursion Head directly manages ARMs. An ARM is itself a bounded executive that carries an approved goal by delegating work. A worker implements one bounded task. A verifier independently evaluates evidence. The deterministic kernel validates and executes declared transitions but does not make semantic product decisions.

## Four planes

### Authority plane

Answers who may decide and how far authority extends. It contains owner identity, GoalSpecs, capability grants, budgets, amendments, approval receipts, project privacy policy, and publication authority. Child authority must be a subset of parent authority.

### Executive plane

Contains the durable logical actors: the Recursion-owned `Head` and `ArmRun` instances. Models are replaceable compute assigned to an actor. The actor's identity, goal, authority, and event history do not change merely because its model or provider changes.

### Execution plane

Contains native or external harness sessions, delegated agents, worktrees, nodes, sandbox scopes, gates, and integration. It consumes immutable work packets and returns normalized checkpoints, candidates, usage, and evidence.

### Evidence plane

Contains append-only events, receipts, exact source and candidate identifiers, gate results, independent verification, context artifact hashes, and publication provenance. Model narratives may explain evidence but cannot substitute for it.

## Interaction surfaces

The v3 product is a headless harness. The interactive CLI is its canonical local operator
surface, and Telegram is an optional interactive transport. Several terminal clients may attach
to Head, ARMs, workers, events or system state; closing a client does not own or end the
underlying process. The persistent daemon, canonical state and managed process broker provide
lifetime and recovery. The conceptual `#general` conversation belongs to the Recursion Head; a
dedicated topic may address an ARM directly. These are views over canonical actor/event state,
not additional supervisors or task registries. See
[TERMINAL-RUNTIME.md](TERMINAL-RUNTIME.md).

Shared multi-ARM conversations use a Head-routed room or an event-mediated workflow. A named ARM
may hold one bounded workflow-step coordination lease; Head retains overall goal, membership,
authority, conflicts, lifecycle and strategic escalation. A `supervisor` is a temporary role
held by Head or that named ARM inside a GoalSpec, never an additional AI ARM Manager. Transport
normalization and the bounded step lease now have requirements contracts; usefulness, conflict
resolution and delayed-message behavior remain experimental. See
[INTERACTION-SURFACES.md](INTERACTION-SURFACES.md).

## Core object model

| Object | Purpose |
|---|---|
| `OwnerIntent` | Exact owner directive plus scope, source, status, and superseding amendment |
| `GoalSpec` | Versioned execution contract: outcome, scope, non-goals, budget, privacy, routes, gates, falsifier |
| `ExecutiveProfile` | Reusable defaults for a Head or ARM without carrying active-goal state |
| `ArmRun` | Durable goal-scoped executive instance with lease, plan, policy, checkpoints, and status |
| `CoordinationLease` | Bounded Head-issued authority for one named ARM to coordinate one shared-room workflow step |
| `TaskNode` | Bounded unit in an ARM-owned DAG |
| `WorkPacket` | Immutable executable grant for a delegated worker or verifier |
| `Route` | Engine + provider + model + capacity pool + credential reference + host + sandbox |
| `CapacityPool` | Subscription, metered API, or local compute entitlement and observed availability |
| `PausePolicy` | Versioned `current-immediate` operative behavior plus separately labeled future/non-operative `checkpoint`, `interrupt`, `drain` or emergency behavior by effect class |
| `PermissionProfile` / `CapabilityGrant` | Configurable authority, including explicit maximum `sovereign` and optional `grant-admin` |
| `ActionAdmission` / `EffectReceipt` | Fenced before/after boundary for a typed effect, including explicit ambiguity and reconciliation |
| `GrantMutationReceipt` | Attributable before/after authority change with step-up and policy/epoch bindings |
| `ContextCapsule` | Model-independent, content-addressed handoff manifest |
| `SourceRecord` / `ResearchClaim` | Versioned source identity plus falsifiable claim, contradiction, applicability and revalidation edges |
| `ExperimentRecord` | Immutable workload, baseline/treatment, hard floors, measurements and result binding |
| `EvidenceBundle` | Exact source, diff, gates, observed behavior, and verifier receipt |
| `PublicationIntent` | Passed candidate proposed to the only approved publishing path |

The glossary normalizes names. Planning-object owners, fields, lifecycle and transitions are
canonical in [AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md); this table is only an architecture
projection. Schema field names remain provisional until M1A, and new documents must not create
competing owners or synonyms.

## One transition path

```text
authenticated command or model proposal
  -> schema validation
  -> authority and budget validation
  -> append durable event
  -> update transactionally derived projections
  -> enqueue an idempotent action
  -> deterministic actuator executes a fixed verb
  -> authenticated result/evidence event
  -> reconcile next state
```

The system should not maintain independent operational truths in Markdown, SQLite, JSONL, process tables, and chat sessions. Human-readable views and configuration may remain files, but active state needs one canonical event/projection boundary.

## Headless native harness and external integrations

Recursion v3 is its own harness at the orchestration and product-contract level. The
ratified construction architecture is a Recursion-owned deterministic contract/event kernel
with compatibility adapters around existing loops. Codex, Cursor, Claude Code, Gemini CLI,
OpenCode, Hermes, and future harnesses remain optional peer engines behind the same contracts.
A small Recursion-owned native agent turn loop is required for the first usable release under
OR-022. It need not precede the first bounded kernel prototype; its implementation and performance
must be measured independently from the upstream adapters.

Every engine adapter negotiates a versioned capability descriptor for thread/turn identities,
stream ordering, tool-intent and settlement boundaries, approval bridging, interrupt semantics,
process ownership, checkpoint/resume, native compaction, usage evidence and stale-notification
filtering. Unsupported invariants fail closed for that route. External engines may own provider
sampling, provider-specific wire/tool syntax and native retry/stream parsing; they do not own
Recursion actor/goal/task identity, authority, budgets, PAUSE epochs, process lifetime, evidence,
canonical events or publication.

The privileged kernel is intentionally smaller than the complete object catalog. Its ratified
implementation responsibilities are strict schema/canonicalization, authenticated command
admission, a pure reducer and event sequence, authority/budget/privacy/fence checks, deterministic
WorkPacket derivation, effect-intent/receipt classification, replay and publication gating.
Provider selection/sampling, context construction, plugin dependency resolution, source retrieval,
terminal rendering, telemetry and process implementation remain adapters that submit typed
proposals. The exact code-informed evidence and falsifiers are in
[FRONTIER-HARNESS-EVIDENCE.md](FRONTIER-HARNESS-EVIDENCE.md) and the second-tranche
[evidence packet](FRONTIER-HARNESS-RESEARCH-TRANCHE-2-EVIDENCE.md).

Expansion beyond the required small native loop must earn its scope by a required capability or
measured quality, continuity, security or resource improvement. See the compared options and falsifiers in
[ARCHITECTURE-OPTIONS.md](ARCHITECTURE-OPTIONS.md).

“Optimized” remains an objective, not a measured property. Implementing Option 2 is conditional
on the typed adapter contract and on a complete writer/migration boundary; a generic wrapper around
arbitrary opaque CLIs would not satisfy it. Matched neutral-API and minimal-native-loop spikes must show
a declared quality, continuity, security or resource benefit before the native loop expands.

## Scientific research capability

A research ARM is the same goal-scoped executive protocol applied to source discovery, claim
reconciliation and experiment design. Scholarly search, standards/source retrieval, PDF parsing,
citation checks and notebook execution are plugins; the kernel retains generic claim, source,
artifact, provenance, privacy and verification contracts. Research conclusions distinguish
external mechanism evidence, local structural applicability and empirical Recursion fit. See
[SCIENTIFIC-RESEARCH.md](SCIENTIFIC-RESEARCH.md).

## V2 inheritance

At `98113d6`, v2 already provides valuable substrate:

- immutable bounded task packets;
- explicit engine/provider/model/pool/host/sandbox separation;
- deterministic placement and rejection traces;
- durable leases, retries, restart recovery, and idempotency;
- aggregate child budgets;
- candidate/source/scope binding;
- independent authenticated verification;
- review intent separated from publication;
- provider egress and remote-execution contracts;
- PAUSE and protected publication boundaries.

V3 must preserve those invariants or deliberately supersede them with stronger tested equivalents.
The source trace verified that the MVP orchestrator has no non-test runtime caller in the
baseline tree, its supervisor schema fixes the executive identity to Hermes, and it does not
model an ARM as a first-class goal-scoped executive. Deployment state remains unknown. The
full trace and migration matrix are in
[CURRENT-AND-MIGRATION.md](CURRENT-AND-MIGRATION.md).

## Migration posture

The destination may be a re-foundation; construction should still use a strangler sequence:

1. Specify v3 contracts and prove adapters against fixtures.
2. Introduce the canonical event/state boundary alongside read-only projections of v2 state.
3. After Lucas ratifies ARM identity and Project Pilot compatibility semantics, represent the
   approved subset as first-class ARM runs without changing publication authority.
4. Rehearse the synthetic local execution-attempt/lease aggregate with no external effects,
   exact replay, complete writer fencing, crash recovery and rollback.
5. Compare results and rollback behavior against v2.
6. Move additional transitions only when their equivalence or improvement is proven.
7. Delete duplicated paths only after replay and migration gates pass.

The 2026-09-03 writer audit blocks step 4 at the broad aggregate boundary: task lifecycle,
assignment, run/evidence, accepted-result and fabric stores do not share a common fence epoch.
M1A uses planning-only in-memory fixtures and no fabric store. A later M1C may use an isolated
fabric-only synthetic requirement fixture, but that would be neither a cutover nor completion of
the owner-selected rehearsal. See
[ARCHITECTURE-PROOF.md](ARCHITECTURE-PROOF.md).

## Coordinator fit

The historical target is a 2-vCPU/4-GB-class coordinator; its current deployment was not
measured in this campaign. V3 is expected to fit only if it uses:

- one daemon per authority domain/OS account;
- event-driven scheduling instead of busy polling;
- one serialized canonical admission path; SQLite WAL is only an optional bounded metadata/
  projection candidate after a JSONL-plus-artifact comparison;
- content-addressed artifacts outside hot database pages;
- lazy plugin loading and isolated short-lived workers;
- adaptive admission with reserved OS/control-plane headroom;
- remote placement for heavy builds and model work;
- summaries and manifests rather than copying full transcripts between actors.

It does not fit if the coordinator becomes a universal build host, runs many resident CLI
trees, eagerly indexes every repository, or loads every plugin into one process. These are
hypotheses with workloads and failure rules in [PERFORMANCE-PLAN.md](PERFORMANCE-PLAN.md),
not measured conclusions.

No language is selected. CPython, Rust and Go are equal-entry post-M1A comparators on the same
reducer/replay/fault workload. JSON/JSONL is the inspectable initial local
protocol encoding; binary framing, SQLite and proposed native-loop optimizations must each
demonstrate a non-dominated improvement without a hard-floor regression before adoption.

## Constitutional reconciliation required

Lucas selected provider-neutral planning inside an explicit approved
model/provider/account/capacity-pool envelope. The current constitution still names ChatGPT via
Codex OAuth, so the product ruling requires a separately reviewed constitutional amendment
before private deployment configuration changes. OR-016 establishes the product principle that
the Recursion-owned `Head` remains the accountable logical actor, models and external harnesses
are authorized replaceable compute, deterministic code actuates, and Lucas retains authority.
Current Hermes-specific operative wording remains in force until the separate constitutional
amendment is applied. The exact proposed clauses and migration seam are recorded in
[CONSTITUTIONAL-AMENDMENT-PROPOSAL.md](CONSTITUTIONAL-AMENDMENT-PROPOSAL.md).

The proposed future `checkpoint` PAUSE default and a maximum `sovereign` profile capable of receiving
control-plane, credential, spending, publication, deployment and `grant-admin` authority
also differ from current constitutional defaults. V3 research must produce exact amendment
choices and preserve explicit receipts/audit boundaries; these docs do not authorize a live
policy or configuration change. See [DECISION-REGISTER.md](DECISION-REGISTER.md).

The first construction candidate is now the narrower planning-only
[M1A](M1A-AUTONOMOUS-PLANNING.md). It excludes SQLite, providers, terminals, plugins, Git,
publication and effects; the broader object table above remains a later architecture projection.

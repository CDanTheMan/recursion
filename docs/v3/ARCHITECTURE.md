---
title: Recursion v3 architecture recommendation
status: proposal-pending-owner-ratification
last-updated: 2026-09-03
baseline-commit: 98113d6c6d3debe2a4d207c51bb1780f7356d714
---

# Recursion v3 architecture recommendation

## Correct hierarchy

```text
Lucas — principal and final authority
  |
  v
Main Assistant / Head Hermes — portfolio executive
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

Head Hermes directly manages ARMs. An ARM is itself a bounded executive that carries an approved goal by delegating work. A worker implements one bounded task. A verifier independently evaluates evidence. The deterministic kernel validates and executes declared transitions but does not make semantic product decisions.

## Four planes

### Authority plane

Answers who may decide and how far authority extends. It contains owner identity, GoalSpecs, capability grants, budgets, amendments, approval receipts, project privacy policy, and publication authority. Child authority must be a subset of parent authority.

### Executive plane

Contains the durable logical actors: Head Hermes and `ArmRun` instances. Models are replaceable compute assigned to an actor. The actor's identity, goal, authority, and event history do not change merely because its model or provider changes.

### Execution plane

Contains native or external harness sessions, delegated agents, worktrees, nodes, sandbox scopes, gates, and integration. It consumes immutable work packets and returns normalized checkpoints, candidates, usage, and evidence.

### Evidence plane

Contains append-only events, receipts, exact source and candidate identifiers, gate results, independent verification, context artifact hashes, and publication provenance. Model narratives may explain evidence but cannot substitute for it.

## Core object model

| Object | Purpose |
|---|---|
| `OwnerIntent` | Exact owner directive plus scope, source, status, and superseding amendment |
| `GoalSpec` | Versioned execution contract: outcome, scope, non-goals, budget, privacy, routes, gates, falsifier |
| `ExecutiveProfile` | Reusable defaults for a Head or ARM without carrying active-goal state |
| `ArmRun` | Durable goal-scoped executive instance with lease, plan, policy, checkpoints, and status |
| `TaskNode` | Bounded unit in an ARM-owned DAG |
| `WorkPacket` | Immutable executable grant for a delegated worker or verifier |
| `Route` | Engine + provider + model + capacity pool + credential reference + host + sandbox |
| `CapacityPool` | Subscription, metered API, or local compute entitlement and observed availability |
| `ContextCapsule` | Model-independent, content-addressed handoff manifest |
| `EvidenceBundle` | Exact source, diff, gates, observed behavior, and verifier receipt |
| `PublicationIntent` | Passed candidate proposed to the only approved publishing path |

The normalized definitions and owners are in [GLOSSARY.md](GLOSSARY.md). Schema field names
remain provisional until the first contract milestone, but new documents should not create
competing actor/object synonyms.

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

## Native harness and external integrations

The recommended construction architecture is a Recursion-owned deterministic contract/event
kernel with compatibility adapters around existing loops. Codex, Cursor, Claude Code, Gemini
CLI, OpenCode, Hermes, and future harnesses remain optional peer engines behind the same
contracts. A Recursion-owned native agent turn loop is a separately measured capability, not a
prerequisite for the first kernel.

The product direction still permits a larger native harness later. It earns that scope only by
demonstrating a required quality, continuity, security or resource improvement that external
engines plus adapters cannot supply. See the compared options and falsifiers in
[ARCHITECTURE-OPTIONS.md](ARCHITECTURE-OPTIONS.md).

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
3. Represent Project Pilots as first-class ARM runs without changing publication authority.
4. Route one low-risk flow through the v3 kernel.
5. Compare results and rollback behavior against v2.
6. Move additional transitions only when their equivalence or improvement is proven.
7. Delete duplicated paths only after replay and migration gates pass.

## Coordinator fit

The historical target is a 2-vCPU/4-GB-class coordinator; its current deployment was not
measured in this campaign. V3 is expected to fit only if it uses:

- one daemon per authority domain/OS account;
- event-driven scheduling instead of busy polling;
- SQLite WAL with bounded projections;
- content-addressed artifacts outside hot database pages;
- lazy plugin loading and isolated short-lived workers;
- adaptive admission with reserved OS/control-plane headroom;
- remote placement for heavy builds and model work;
- summaries and manifests rather than copying full transcripts between actors.

It does not fit if the coordinator becomes a universal build host, runs many resident CLI
trees, eagerly indexes every repository, or loads every plugin into one process. These are
hypotheses with workloads and failure rules in [PERFORMANCE-PLAN.md](PERFORMANCE-PLAN.md),
not measured conclusions.

## Constitutional reconciliation required

The current constitution names ChatGPT via Codex OAuth as the planning model. V3's
provider-neutral executive model policy requires an explicit reviewed amendment before it can
become operative; a v3 document cannot make that change implicitly. The stable proposed
principle is that Hermes is the accountable logical actor, models are authorized replaceable
compute, deterministic code actuates, and Lucas retains authority. The exact proposed rulings
are in [ARCHITECTURE-OPTIONS.md](ARCHITECTURE-OPTIONS.md) and the prioritized owner queue is
in [DECISION-REGISTER.md](DECISION-REGISTER.md).

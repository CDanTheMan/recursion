---
title: Recursion v3 research and construction roadmap hypothesis
status: hypothesis
last-updated: 2026-09-02
---

# Recursion v3 research and construction roadmap hypothesis

## Delivery model

V3 is developed through small, independently verified milestones and released as one complete v3 product promise. `core`, `standard`, `remote`, `full`, and custom manifests control installation weight; they do not create incompatible products or closed feature tiers.

This roadmap is not implementation authorization. It orders the work that a later accepted GoalSpec should convert into bounded tasks.

## Milestone 0 — evidence-grounded specification

Deliver:

- current source/runtime architecture map at the merged v2 baseline;
- exact gap map between Project Pilot/Head Hermes and the v2 MVP fabric;
- primary-source reference matrix with license/provenance review;
- provider/CLI/context capability facts with verification dates;
- benchmark and experiment plan;
- reconciled decision register and constitutional amendment list;
- complete v3 spec with normative/hypothesis boundaries.

Gate: another agent can explain the product and create bounded implementation tasks without reading the archived chat or inventing an actor.

## Milestone 1 — v3 contract skeleton

Deliver versioned schemas and fixtures for OwnerIntent, GoalSpec, ExecutiveProfile, ArmRun, TaskNode/WorkPacket, Route, CapacityPool, ContextCapsule, EvidenceBundle, plugin manifest, and publication lineage.

Gate: cross-record, authority-subset, privacy, budget, source, lineage, and replay invariants fail closed; schema names and compatibility policy are frozen for initial implementation.

## Milestone 2 — canonical state and compatibility projection

Deliver the SQLite/WAL event writer, projections, migrations, artifact metadata, action/outbox path, backup/restore, and read-only imports/views for relevant v2 state.

Gate: crash, duplicate, stale lease, disk pressure, migration, backup, restore, and projection rebuild fixtures pass without two writable truths.

## Milestone 3 — plugin kernel and route fabric

Deliver compiled capability graph, plugin lifecycle, typed event bus, v2 adapter compatibility, route resolver, model-aware pools, billing boundary, credential references, and deterministic explanations.

Gate: supported routes negotiate from fixtures; disabled plugins are inert; failures quarantine only affected capabilities; no unauthorized billing/credential/egress transition is possible.

## Milestone 4 — Head and ARM executive runtime

Deliver first-class logical actors, executive leases, Project Pilot migration, model escalation, ARM-owned task DAGs, bounded delegation, checkpoint-driven route changes, quota-exhaustion behavior, and upward escalation.

Gate: Head directly manages multiple independent ARM runs; each survives model replacement and restart; the kernel never becomes a semantic ARM Manager; workers cannot redefine goals.

## Milestone 5 — context and evidence system

Deliver content-addressed repository evidence, context capsules, Owner Intent Ledger, Compaction Fidelity Contract, adapter capability descriptors, one compaction owner per route, rehydration, and proof-carrying verification.

Gate: repeated compaction/handoff benchmarks retain mandatory state and reduce measured repeated context without private cross-project reuse.

## Milestone 6 — planning and operator CLI

Deliver Grill Me modes, GoalSpec compiler/amendments, schema-driven setup/configuration, tiered doctor, route/queue/resource/context explanations, Observer Interface, and safe branch inventory/pruning.

Gate: a fresh owner can configure the first deployment and run a bounded synthetic goal without agent-assisted config editing or a model-powered setup call.

## Milestone 7 — authenticated node fabric

Deliver enrollment, trust root/operator credential separation, node roles, signed envelopes, replay protection, manifest-first hydration, disconnect spooling/reconciliation, capability quarantine, and cached lightweight preflight.

Gate: cross-node fault/security scenarios pass; local operation remains available without remote-node enrollment; coordinator stays within measured resource budgets.

## Milestone 8 — adaptive optimization

Deliver explainable local routing calibration, quota shadow prices, reservations, adaptive concurrency, cache-domain affinity, resource shedding, telemetry evidence providers, and optional `ccusage` reconciliation.

Gate: shadow-mode and controlled experiments show improvement for at least one declared profile without reducing quality floors or widening authority.

## Milestone 9 — integration, editions, and private soak

Deliver release manifests, dependency locks/SBOMs, official plugin combinations, migrations from v2, construction runbook, synthetic public conformance fixtures, private canary, long-session soak, and rollback.

Gate: [ACCEPTANCE.md](ACCEPTANCE.md) passes on the exact candidate; private evidence remains private; Lucas owns merge and production deployment.

## Parallelism rules

After a contract milestone freezes its interfaces, bounded agents may work concurrently on non-overlapping plugins and fixtures. Before that point, parallel research is encouraged but competing implementations of unstable core contracts are not.

- One integration owner per milestone.
- One exclusive worktree per implementation task.
- Machine-checkable gate and explicit allowed paths for every task.
- Different model family for meaningful independent review when practical.
- No more branch creation when the unique unreviewed limit is reached.
- Failed work returns evidence; retry requires novelty.
- Capacity is reserved for integration, verification, and recovery.

## Construction-system separation

The temporary tools used to build v3—an overnight Codex lead, Cursor implementation swarms, a Grok-powered watcher, or particular subscription arrangements—belong in a construction runbook. The product exposes generic engines, nodes, and observers; it does not hard-code the construction campaign into the release.

## First research blockers

1. Native Recursion agent-loop scope versus the retained Hermes base and external harness plugins.
2. Required constitutional amendment for provider-neutral Head/ARM model selection.
3. Canonical event/schema mapping from overlapping v1/v2/project-pilot stores.
4. Real subscription and cache observability for each intended CLI route.
5. Numeric coordinator performance budgets and representative task corpus.
6. Plugin isolation boundary on Linux and Windows without unacceptable overhead.
7. Public interoperability surface versus private implementation details.

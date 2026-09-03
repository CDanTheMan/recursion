---
title: Recursion v3 construction runbook
status: proposed-procedure-not-authorization
last-updated: 2026-09-03
---

# Recursion v3 construction runbook

This is temporary construction procedure, separate from the product specification. It does
not authorize implementation, provider changes, deployment or control-plane amendments.

The 2026-09-03 owner rulings added material terminal, interaction, PAUSE, Full Access,
verification and plugin-contract questions. Complete the focused
[RESEARCH-AGENDA.md](RESEARCH-AGENDA.md) campaign and obtain its contract-readiness verdict before
authorizing this milestone; this runbook remains the proposed first construction boundary, not
the next research task.

## Recommended first autonomous milestone

**Milestone:** v3 contract skeleton and replay/conformance harness.

**Parent goal:** prove that the proposed native kernel vocabulary can represent and reject
the v2 authority/evidence boundary before any runtime state writer, database or engine is
built.

**Allowed paths for a future owner-approved task:**

- `schemas/control-plane/v3/**`
- `scripts/v3/**`
- `scripts/tests/v3/**`
- `docs/v3/**`

**Explicit non-goals:** no edits to `CONTROL_PLANE.md`, `ANCHOR.md`, `state/DECISIONS.md`,
existing v1/v2 scripts or schemas, `.env`, auth/model/provider configuration, deployment,
services, cron, PAUSE, publication, VPS, live provider calls, SQLite runtime writer, migration
of live state, native agent loop or UI.

## Bounded task graph

| Task | Output | Gate | Stop condition |
|---|---|---|---|
| C1 vocabulary freeze | Schema names and object/event ownership ADR under `docs/v3/**` | Every name maps to [GLOSSARY.md](GLOSSARY.md); no second executive layer | Material term has two authority meanings |
| C2 strict schemas | Schemas for `OwnerIntent`, `GoalSpec`, `ArmRun`, `TaskNode`, `WorkPacket`, `Route`, `RouteLease`, `ContextCapsule`, `EvidenceBundle`, publication objects | Unknown fields, malformed identities, raw secrets, unbounded values and invalid versions fail closed | Required current invariant cannot be represented |
| C3 cross-record validator | Pure offline validator for parent/child authority, budget, source, route, verifier and publication bindings | Mutation/property fixtures prove child subset, distinct verifier and no implicit billing/egress widening | Validator needs operational state or network access |
| C4 compatibility fixtures | Sanitized synthetic fixtures shaped from v2 contracts plus explicit incompatibility results | Each fixture round-trips to a canonical digest or fails with one typed reason; no best-effort loss | Translation requires project/provider special cases in kernel |
| C5 replay model | In-memory command/event projector and deterministic replay test only | Duplicate command is idempotent; ordering/rebuild digest is stable; no external effect occurs | Replay depends on wall clock, process state or network |
| C6 independent verification | Separate reviewer re-runs gates and attacks authority, secret and dual-writer boundaries | Reviewer did not implement C2–C5; every objection is resolved or recorded | Same agent/model self-approves material claim without deterministic proof |

Only one task edits a schema/object family at a time. The integrator may resolve naming and
fixture conflicts but may not broaden the parent goal.

## Exact milestone acceptance gate

A future implementation passes only when all of the following are machine checked:

1. All v3 schemas reject unknown fields and bound string, collection, nesting and payload
   sizes.
2. The validator proves `Owner -> Head Hermes -> ARM executive -> worker/verifier` authority
   inheritance; no record or code path creates an AI ARM Manager.
3. Parent goal, source commit, allowed paths, non-goals, capabilities, privacy/egress, budget,
   route and gate cannot widen in a descendant.
4. Engine, provider, model, account reference, capacity pool, host and sandbox remain separate
   required route fields; subscription-to-metered fallback is impossible without a new owner
   grant.
5. Raw credential material and contributor-ineligible privacy combinations are rejected.
6. Implementer and verifier identities are distinct and both bind the exact task, source,
   candidate, gate and evidence digests.
7. Publication intent/receipt cannot mean merge or deploy and can be emitted only through the
   publisher role.
8. Duplicate commands replay one result; shuffled or corrupted events, stale leases and
   mismatched sequence/digest fail closed.
9. Every compatibility fixture either replays to the expected canonical digest or returns one
   stable typed incompatibility; no fixture mutates existing v1/v2 state.
10. The test suite performs no network call, provider invocation, Git push, runtime-state write
    or configuration change and leaves the repository clean except for intended allowed-path
    changes.
11. An independent verifier executes the exact gate on the exact candidate commit and records
    dissent plus any unproved property.
12. `git diff --check` and the repository's relevant tests pass; all changes stay inside the
    approved task paths.

## Handoff and rollback

Commit red tests before green implementation when the future task explicitly authorizes code.
Use synthetic fixtures containing no private project material. The milestone has no runtime
cutover, so rollback is removal of the unreferenced v3 skeleton branch; existing execution
must remain byte-for-byte behaviorally unchanged. If a required invariant cannot be expressed,
stop and return the smallest conflicting fixture and owner question.

## Later construction boundary

Only after this milestone passes may an owner-approved goal propose a SQLite/WAL writer,
shadow reader or one-aggregate cutover. A native inner agent loop remains a separate measured
spike. See [ARCHITECTURE-OPTIONS.md](ARCHITECTURE-OPTIONS.md) and
[CURRENT-AND-MIGRATION.md](CURRENT-AND-MIGRATION.md).

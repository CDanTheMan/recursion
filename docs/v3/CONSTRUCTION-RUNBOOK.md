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

**Milestone:** v3 pure contract skeleton and replay/conformance harness.

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
| C2 strict schemas | Schemas for `OwnerIntent`, `GoalSpec`, `ArmRun`, `CoordinationLease`, `TaskNode`, `WorkPacket`, `Route`, `RouteLease`, `RouteCapabilityDescriptor`, `CapacityPool`, `PausePolicy`, `PermissionProfile`, `CapabilityGrant`, `GrantMutationReceipt`, `VerifierPolicy`, `PluginManifest`, `ContextCapsule`, `SourceRecord`, `ResearchClaim`, `EvidenceBundle`, canonical command/event/effect and publication objects | Unknown fields, malformed identities, raw secrets, unbounded values and invalid versions fail closed | Required current invariant cannot be represented |
| C3 cross-record validator | Pure offline validator for parent/child authority, budget, source, route, verifier and publication bindings | Mutation/property fixtures prove child subset, distinct verifier and no implicit billing/egress widening | Validator needs operational state or network access |
| C4 compatibility fixtures | Sanitized synthetic fixtures shaped from v2 contracts plus explicit incompatibility results | Each fixture round-trips to a canonical digest or fails with one typed reason; no best-effort loss | Translation requires project/provider special cases in kernel |
| C5 replay model | In-memory command/event projector and deterministic replay test only | Duplicate command is idempotent; ordering/rebuild digest is stable; no external effect occurs | Replay depends on wall clock, process state or network |
| C6 independent verification | Separate reviewer re-runs gates and attacks authority, secret and dual-writer boundaries | Reviewer did not implement C2–C5; every objection is resolved or recorded | Same agent/model self-approves material claim without deterministic proof |

`CoordinationLease`, terminal client messages and the scientific records are requirements
contracts only in this milestone. Their presence proves that the generic vocabulary can express
and reject invalid states; it does not enable multi-ARM rooms, a terminal runtime or scholarly
adapters. Numeric limits, provider fields and platform behavior remain provisional or explicitly
`unknown` where evidence is unavailable.

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
5. `checkpoint` is the encoded ordinary PAUSE default; `interrupt`, `drain` and emergency stop
   are distinct values whose effect boundary and precedence cannot be conflated. A separate
   `current-immediate` compatibility policy represents the operative constitution and remains
   selected unless a later amendment receipt authorizes another policy.
6. Maximum `sovereign` authority can administer its own grants only when `grant-admin` is
   explicit; the mutation binds before/after digests and cannot silently alter audit history.
7. A plugin's code trust, digest, functional capabilities, subscription quota, metered spend,
   route/account use, update and revocation authorities are represented separately.
8. Raw credential material and contributor-ineligible privacy combinations are rejected.
9. Implementer and verifier identities are distinct and both bind the exact task, source,
   candidate, gate and evidence digests.
10. Routine verifier downgrade and high-risk owner exception are explicit typed evidence;
    missing verification cannot produce a pass.
11. Publication intent/receipt cannot mean merge or deploy and can be emitted only through the
   publisher role.
12. Duplicate commands replay one result; shuffled or corrupted events, stale leases and
   mismatched sequence/digest fail closed.
13. Every compatibility fixture either replays to the expected canonical digest or returns one
   stable typed incompatibility; no fixture mutates existing v1/v2 state.
14. The test suite performs no network call, provider invocation, Git push, runtime-state write
    or configuration change and leaves the repository clean except for intended allowed-path
    changes.
15. An independent verifier executes the exact gate on the exact candidate commit and records
    dissent plus any unproved property.
16. `git diff --check` and the repository's relevant tests pass; all changes stay inside the
    approved task paths.
17. The canonical experiment registry has one immutable mapping for `PERF-001` through
    `PERF-011`; an evidence result cannot bind to a mismatched experiment id or workload version.
18. `SourceRecord` and `ResearchClaim` distinguish discovered/identified/retrieved/verified,
    access/editorial status, source version, typed contradiction/applicability edges and
    revalidation; metadata-only or retracted-as-current evidence cannot pass.
19. Terminal protocol fixtures enforce epoch/cursor replay, one input/resize lease, bounded
    credit and reset-on-gap without launching a process or asserting OS compatibility.
20. The fabric-only state-contract fixture uses immutable assignment input and excludes every
    task/run/result/remote/Git/publication writer. Its report cannot claim OR-015 completion.

## Architecture-proof readiness verdict

The 2026-09-03 architecture proof gives a **conditional go** for this pure skeleton after the
PERF identifier reconciliation now recorded in the specification. It is not a go for SQLite,
runtime state, provider calls, terminal processes, plugin execution, migration or deployment.
The milestone freezes field meanings, authority subsets, event/replay refusal behavior and
synthetic fixtures; it preserves unresolved policy choices as explicit configuration/owner
questions instead of selecting them in code.

The fabric-only fixture is the smallest safe state proof inside C4/C5. The later owner-selected
local execution-attempt/lease rehearsal still requires a complete legacy-writer allowlist,
shared fence epoch, fault injection and rollback proof. If a future C1/C2 task cannot represent
current constitutional behavior and the proposed future profile without conflating them, the
conditional go is withdrawn and the conflicting fixture is returned to Lucas.

## Handoff and rollback

Commit red tests before green implementation when the future task explicitly authorizes code.
Use synthetic fixtures containing no private project material. The milestone has no runtime
cutover, so rollback is removal of the unreferenced v3 skeleton branch; existing execution
must remain byte-for-byte behaviorally unchanged. If a required invariant cannot be expressed,
stop and return the smallest conflicting fixture and owner question.

## Later construction boundary

Only after this milestone passes may an owner-approved goal propose a SQLite/WAL writer,
shadow reader or the ratified synthetic local execution-attempt/lease rehearsal. That rehearsal
has no external effects and must prove exact replay, full writer enumeration, fencing, crash
recovery and rollback with a deterministic zero-model gate. A native inner agent loop remains a separate measured
spike. See [ARCHITECTURE-OPTIONS.md](ARCHITECTURE-OPTIONS.md) and
[CURRENT-AND-MIGRATION.md](CURRENT-AND-MIGRATION.md).

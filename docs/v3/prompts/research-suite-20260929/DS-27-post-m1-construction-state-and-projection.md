---
title: DS-27 — Post-M1 construction state and projection
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-27 — Post-M1 construction state and projection

This is a bounded construction handoff, not a public Deep Research brief. Supplying this document is the invocation; it makes no repository or provider call on its own. This handoff is self-contained context for a repository-execution task; it is not a Deep Research session. It prepares the exact packet that would build the accepted Milestone 2 — canonical state and compatibility projection.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Hermes is the executive control plane. Workers are
bounded executors. An implementer's own PASS is never acceptance; independent review is
required, and missing verification is never a pass. `CONTROL_PLANE.md` is the operative
constitution; a research session may propose amendments but must never edit it. No research
session performs implementation, provider/model/authentication/configuration changes,
spending, deployment, publication or merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula,
captures and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs,
pinned source, licenses, peer-reviewed work). Classify every consequential claim as
source-documented, locally observed, inferred or unverified; keep `unknown` distinct from
zero. Model consensus and vendor marketing are not evidence. Every recommendation needs a
competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never
secrets, credentials, personal data, private repository content, local paths, or
account/infrastructure identifiers.

### Lane context

- Recursion v3 is the product being built. It has one canonical event/projection boundary plus content-addressed immutable artifacts. The physical event store is deliberately unselected: append-only canonical JSON/JSON Sequence plus content-addressed artifacts, versus single-writer SQLite WAL metadata plus the same artifacts, are the competing candidates. SQLite/WAL is a candidate only after it beats the JSONL baseline under a preregistered store/replay/fault comparison.
- The recorded state finding this packet addresses is that task, assignment, run/evidence, accepted-result and fabric stores do not form one fenced aggregate, a direct task-state fallback remains in the writer path, and no common monotonic fence epoch spans them. Until a machine-readable writer allowlist and common epoch cover the exact chosen boundary, the owner-selected rehearsal cannot begin.
- OR-015 is the recorded Owner decision that the first single-writer rehearsal targets the local execution-attempt/lease aggregate with synthetic work and no external effects, requiring exact replay parity, complete legacy-writer enumeration, fencing, crash recovery and proven rollback before ARM, remote-provider or publication aggregates. It stays blocked until the aggregate boundary, complete writer allowlist and fencing protocol are machine-checkable.
- Canonical write path: only deterministic controller code writes canonical state. For each aggregate exactly one fenced writer admits an event at a monotonically increasing sequence; cross-aggregate operations use an explicit saga/outbox boundary rather than a second writer. Each accepted event carries aggregate type/id, contiguous sequence, event and command id, idempotency key, causation/correlation ids, writer id, monotonic fence epoch, logical/controller time, previous/current event digest, schema version and typed payload.
- Durable lineage events are ordered, authenticated, replayable and schema-migrated. Projections (queues, status, budgets, lineage, routing history, artifact reachability, branch inventory, observer interfaces) must each be rebuildable from durable events plus immutable artifacts. Projection parity is not replay parity: equal rendered state does not prove equal event order, crash behavior or writer exclusion.
- Distributed effects are never assumed exactly once. The required posture is idempotency keys, prepare/execute/reconcile states, leases with expiry and fencing tokens, authenticated result receipts, exact repository/source bindings and a crash matrix for failure before prepare, after prepare, during the external call, after the effect but before receipt, and after receipt but before projection. The lease projection carries task/assignment/lease/attempt identities, status, recovery state, expiry, reservation, result digest, source digest and last event sequence/digest.
- Migration and import: versioned adapters record source digest and commit, deterministic identity mapping, duplicate/conflict reports, dry-run projection comparison, reversible backup, replay and crash injection, and refuse to fabricate missing or malformed state. The import/replay progression is UNIMPORTED -> SNAPSHOTTED -> VALIDATED -> LEGACY_WRITERS_QUIESCED -> FENCE_ESTABLISHED -> IMPORTED -> REPLAYED -> SHADOW_READ_VERIFIED -> V3_OWNER_ACTIVE -> CHECKPOINTED. Malformed, conflicting, torn, unauthenticated or stale input becomes `REFUSED` or `RECOVERY_REQUIRED`. Backup requires a consistent selected-store plus artifact snapshot, restore onto a fresh host, key/credential exclusion and forward/rollback migration proof. Dual writable sources of truth are forbidden.
- Frozen prior slices: M1A (planning schemas, validation, fixtures, in-memory replay), M1B (route, plugin and process requirement contracts) and M1C (source/effect/publication/persistence contracts) are merged frozen contracts; they must not be rebuilt, reopened or edited, and any mapping extension is a separately specified bridge, not a retrospective contract edit.
- This is a construction handoff, not a research lane: it requires repository execution (isolated worktree, branch, commits, machine-checkable gates) and independent exact-candidate verification, and it produces a proposed packet specification, not an executed result. The packet freezes a `TASK_BASE` (the exact reviewed predecessor commit), an isolated worktree and a branch before any edit. Prohibited: push, publication, merge, product language/store/framework selection, live provider or paid calls, real external effects or migration cutover, edits to protected paths, and reopening recorded Owner decisions OR-021 through OR-039.

## Purpose

Specify the first bounded construction packet for canonical state and compatibility projection: one fenced single-writer store, rebuildable projections, versioned migrations, an action/outbox path, backup/restore, and read-only legacy imports. This is blocking because the recorded state finding is that task, assignment, run/evidence, accepted-result and fabric stores do not yet form one fenced aggregate, so the owner-selected rehearsal cannot begin until its aggregate boundary, complete writer allowlist and fencing protocol are machine-checkable.

## Authority and boundaries

The shared authority constraints are in `## Baked context`. Preserve the current constitution; write proposed amendments, never edit it. M1A, M1B and M1C are already merged frozen at the recorded baseline and must not be rebuilt, reopened or edited; this packet extends them through a separately specified bridge if a mapping is needed. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication, push or merge is authorized. Do not select a product language, store or framework. Do not reopen recorded Owner decisions (OR-021 through OR-039). This is a construction task, not a public Deep Research session: it requires repository execution (isolated worktree, branch, commits) and independent exact-candidate verification. Public Deep Research receives only public or synthetic briefs; this construction packet may reference repository paths but must never export private content, transcripts, credentials or account identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Branch, worktree and task-binding discipline

1. What exact reviewed predecessor commit is the `TASK_BASE`, and what isolated worktree path and branch name does the packet freeze before any edit?
2. What is the full preflight sequence (ownership, cleanliness, remote state, PAUSE, capacity, source-commit verification) that must pass before inference or writes?
3. How is the parent goal, v3 objective, source commit, allowed paths, non-goals and acceptance commands bound into one machine-checkable GoalSpec before launch?

### Allowed paths and protected boundaries

4. Which exact new paths may this packet create, and how is every protected path (the operative constitution, the anchor/scope document, the state decision log, scripts, and environment/credential configuration) excluded by construction?
5. How does the packet prove it did not modify M1A/M1B/M1C fixtures, schemas, oracles or wire profiles?
6. Which existing read-only inputs are consumed as dependencies without being rewritten?

### Synthetic execution-attempt/lease aggregate rehearsal

7. What is the minimal synthetic execution-attempt/lease aggregate, with no task/run/result, remote or publication writes, and exactly what identities, statuses, expiry, reservation and result/source digests does its lease projection carry?
8. What aggregate type/id, contiguous sequence, event/command id, idempotency key, causation/correlation id, writer id, monotonic fence epoch, logical/controller time, previous/current event digest, schema version and typed payload does each event carry?
9. How does the rehearsal produce exact replay parity, and how is projection parity kept distinct from replay parity?
10. How is the complete legacy-writer enumeration and common fence epoch demonstrated before the rehearsal is admitted?

### Writer, projections, migrations and outbox

11. How does exactly one fenced writer admit an event per aggregate at a monotonically increasing sequence, and how are cross-aggregate operations expressed as an explicit saga/outbox boundary?
12. Which projections are transactionally synchronous and which are eventually rebuildable, and how is each rebuilt from durable events plus immutable artifacts?
13. What versioned migration and read-only legacy import adapters are specified, and how do they refuse to fabricate missing or malformed state?

### Backup, restore and failure gates

14. What consistent selected-event-store plus artifact snapshot, restore-onto-fresh-host, key/credential exclusion and forward/rollback migration proof is required?
15. How are the crash, duplicate, stale-lease, disk-full, migration, backup, restore and projection-rebuild gates each injected and observed?
16. Which malformed, conflicting, torn, unauthenticated or stale inputs must produce `REFUSED` or `RECOVERY_REQUIRED`, and how is the import/replay state machine preserved?
17. How does forward-only effect reconciliation handle failure before prepare, after prepare, during the external call, after the effect but before receipt, and after receipt but before projection?

### Independent review and publication boundary

18. What independent review is required for the exact candidate, and what evidence must the reviewer reproduce rather than accept from the implementer?
19. How does the packet end at a local candidate commit with no push, publication or merge, and what external attestation records the result?

## Deliverable

A machine-checkable construction packet specification: the frozen predecessor commit, worktree and branch; the exact allowed new paths and protected-path exclusions; the aggregate/event/lease field contract; the writer allowlist and fence protocol; the projection, migration, outbox, backup/restore and legacy-import requirements; the full failure-gate inventory with expected `REFUSED`/`RECOVERY_REQUIRED` outcomes; the forward-only reconciliation procedure; the acceptance command inventory; and the independent-review and no-push/no-merge boundary. It is a proposed packet, not an executed result.

## Non-goals

- No push, publication or merge to any branch.
- No rebuilding, editing or reopening M1A/M1B/M1C.
- No product language, store, framework or wire-format selection.
- No live provider, model, network or paid call.
- No real external effect, migration cutover or OR-015 rehearsal.
- No modification of protected paths or existing specifications.
- No SQLite migration or write outside the synthetic rehearsal boundary.
- No fabricated replay parity or projection parity claim.
- No self-review presented as independent verification.

## Completion gate

- The predecessor commit, worktree, branch and allowed paths are frozen and machine-checkable.
- The writer allowlist and common fence epoch cover the exact chosen aggregate boundary.
- The synthetic execution-attempt/lease aggregate is defined with no external effects.
- Event, lease-projection and idempotency field contracts are explicit and closed.
- Crash, duplicate, stale-lease, disk-full, migration, backup, restore and projection-rebuild gates each have an expected outcome.
- `REFUSED` and `RECOVERY_REQUIRED` semantics are stated for every malformed or stale input class.
- Forward-only effect reconciliation covers all five crash positions.
- The packet ends at a local candidate commit with no push, publication or merge.
- Independent review reproduces the exact-candidate gates and records any missing independence.
- Protected paths and M1 fixtures are untouched and the secret scan is clean.

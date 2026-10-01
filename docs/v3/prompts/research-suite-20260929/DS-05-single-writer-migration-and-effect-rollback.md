---
title: DS-05 — Single-writer migration and effect rollback
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-05 — Single-writer migration and effect rollback

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. Supplying this document is the invocation; it makes no repository or provider call on its own.

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

- **Focus.** This lane defines the exact checkpoint sufficient to fence a legacy writer and transfer one aggregate to v3, so the single-writer migration contract can be frozen. It is research lane R7 of the Recursion v3 agenda.
- **Accepted rehearsal.** `OR-015` ratifies the first single-writer rehearsal on the synthetic local execution-attempt/lease aggregate, using synthetic work and no external effects.
- **Current-state constraint.** Task lifecycle, assignment persistence, run/evidence, accepted-result ledger and fabric journal have separate writers, and no common monotonic writer epoch currently spans them. The design target is one fenced writer per aggregate admitting exactly one event per monotonically increasing sequence, with an explicit saga/outbox boundary for cross-aggregate operations.
- **Import/replay progression.** UNIMPORTED -> SNAPSHOTTED -> VALIDATED -> LEGACY_WRITERS_QUIESCED -> FENCE_ESTABLISHED -> IMPORTED -> REPLAYED -> SHADOW_READ_VERIFIED -> V3_OWNER_ACTIVE -> CHECKPOINTED. Malformed, conflicting, torn, unauthenticated or stale input becomes REFUSED or RECOVERY_REQUIRED.
- **Parity distinction.** Projection parity is not replay parity: equal rendered state does not prove equal event order, crash behavior or writer exclusion.
- **Crash matrix.** Every transition must pass with deterministic, zero-model reruns: before prepare, after prepare, during the effect, after the effect but before receipt, and after receipt but before projection.
- **Forward-only reconciliation.** Before the first externally accepted effect, rollback may restore the last verified checkpoint. Once a provider submission, pushed ref, sent message, credential operation, deployment or service change may have been accepted, state restoration cannot undo reality: retain the v3 record, block dependent effects and reconcile forward. Never claim rollback of an accepted effect or promise exactly-once semantics.
- **Fixture boundary.** A fabric-only state-contract fixture proves schema/replay/fault vocabulary only; it is not the full `OR-015` local execution-attempt/lease rehearsal. A separate bounded numeric recovery-reservation-ledger task covers integer recovery-reservation arithmetic and is explicitly out of scope here.
- **Ownership.** `OR-016` makes the versioned Recursion release the owner of canonical Head and orchestration semantics; Hermes is at most a removable compatibility/engine adapter.

## Purpose

This research informs the exact checkpoint sufficient to fence a legacy writer and transfer one aggregate to v3, so the single-writer migration contract can be frozen. It is blocking because `OR-015` ratifies a first rehearsal on the synthetic local execution-attempt/lease aggregate with no external effects, and no common monotonic writer epoch currently fences the task, assignment, run/evidence, accepted-result and fabric paths. It must also define forward-only reconciliation for effects that cannot be rolled back once externally accepted.

## Authority and boundaries

The authority, scope and privacy constraints are restated in `## Baked context`; read nothing else in preparation. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. This lane is design analysis over synthetic or copied fixtures only; it must not open a cutover, write canonical state, or run any external effect. It must not duplicate the separate bounded numeric recovery-reservation-ledger work; that ledger concerns integer recovery-reservation arithmetic and is explicitly out of scope here.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. What exact import/replay progression and checkpoint condition is sufficient to fence every legacy writer for one aggregate without a second writable truth?
2. How do event-sourced strangler, expand/contract, saga/outbox, fencing-token and shadow-read patterns compare for the synthetic local execution-attempt/lease aggregate with zero external effects?
3. What machine-checkable enumeration and allowlist catches a new or renamed legacy writer rather than relying on prose inventory?
4. What proves import and projection parity — equal rendered state, equal event order, equal crash behavior, or all three — and how are they distinguished?
5. What fencing epoch, stale-epoch refusal and duplicate-command rule make competing or replayed writes fail closed at admission and execution?
6. What crash matrix must pass at every transition (before prepare, after prepare, during effect, after effect before receipt, after receipt before projection) with deterministic, zero-model reruns?
7. What backup, reverse-reader and rollback proof permits returning to the frozen legacy writer without merging two histories or repeating work?
8. For provider submissions, pushed refs, sent messages, credential changes and deployments, what forward-only reconciliation proves reality once an effect may have been externally accepted?
9. How are ambiguous or partially applied cross-aggregate saga steps blocked and reconciled without relabeling an external effect as rolled back?
10. What distinguishes a fabric-only state-contract fixture from the full `OR-015` rehearsal, and why does the fixture not satisfy the broad gate?
11. Which design choices (concurrency, retry, fixture volume, resource limits, optional model assistance) must stay configurable while the default gate remains deterministic and quota-free?
12. What competing cutover boundary (smallest aggregate plus bounded broker refinement versus broker-inclusive model) is supported, and what decisive test separates them?

## Deliverable

- A source-pinned per-aggregate migration/cutover/rollback table with classification, confidence and expiry.
- An exact import/replay/fence/rollback proof outline and a crash matrix for the synthetic rehearsal aggregate.
- A forward-only reconciliation taxonomy for externally accepted effects, each with a decisive falsifier.
- A recommendation tied to a competing option, plus an explicit statement of the reservation-ledger boundary and open Owner questions.

## Non-goals

- Do not perform a cutover, open a shadow writer, or write any canonical or operational state.
- Do not duplicate the separate bounded numeric recovery-reservation-ledger work.
- Do not reopen `OR-015`/`OR-016` or promote a recommendation into an Owner decision.
- Do not claim rollback of an externally accepted effect or promise exactly-once semantics.
- Do not select a storage engine, language or persistence implementation.
- Do not edit constitution, auth, config or migration artifacts.
- Do not include private project identity, transcripts or local paths.

## Completion gate

- Every migration claim is pinned to a primary source or local read-only evidence, or marked unverified.
- The proof covers legacy-writer enumeration, fencing, replay parity, crash recovery, backup/restore and rollback.
- Forward-only reconciliation is defined for every externally accepted effect class.
- The reservation-ledger boundary is stated and no overlap with its assigned work is introduced.
- `OR-015`/`OR-016` are neither reopened nor promoted, and projection parity is not equated with replay parity.
- No cutover or protected path is touched and no runtime/provider/auth/spending effect occurs.
- The deliverable passes a privacy and secret scan; Owner questions are listed separately.

---
title: DS-01 — Pause, cancellation, and effect fencing
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-01 — Pause, cancellation, and effect fencing

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

- **Focus.** This lane defines the future per-effect-class pause, cancellation and effect-fencing semantics for the pause family plus an independent emergency stop, so the pause schema can be frozen. It is research lane R3 of the Recursion v3 agenda.
- **Pause modes.** `checkpoint` (selected future ordinary default: admit no new work and let the current bounded operation reach its next mechanically safe checkpoint, then pause), `interrupt` (cancel interruptible work, preserve atomic state, quarantine ambiguous effects), `drain` (admit no new work but let explicitly enumerated in-flight work classes finish), and emergency stop (separate break-glass behavior that blocks new effects immediately and may sacrifice in-flight work).
- **Effect classes.** The seven classes the questions enumerate are: model turn, local transaction, subprocess, remote/disconnected action, read-only gate, publication, and ambiguous external effect (an effect whose external acceptance cannot be proven).
- **Accepted direction and non-operative status.** `OR-004` is the Owner ruling that selects `checkpoint` as the future product PAUSE default but keeps it non-operative; the operative PAUSE is immediate halt. `OR-020` authorizes the future policy family and the exact docs-only constitutional amendment, which remains non-operative until applied.
- **Fencing and precedence.** The future pause uses a monotonically advancing admission epoch. Every action binds command, principal, GoalSpec/grant/policy digests, admission epoch, fencing token, effect class, idempotency key and deadline. Precedence is emergency, revocation, interrupt, then checkpoint. An action admitted before an epoch change but not yet executed is stale and fails closed.
- **Ambiguity and labels.** An already accepted external effect becomes ambiguous and is reconciled by provider identity/status; it is never blindly retried or described as rolled back. The terminal labels `ambiguous`, `quarantined` and `stale` distinguish unknown, quarantined and superseded work from completed work in owner-facing status.
- **Adapters versus kernel.** A typed adapter may declare a narrower disposition than the kernel, never a wider one.
- **Disconnect and reconnect.** A disconnected node may finish only the local bounded operation explicitly permitted by its last valid grant and spool signed evidence. After reconnection, the controller revalidates the GoalSpec version, fencing token, lease and PAUSE/revocation state before admitting that evidence or any derived action; it cannot widen scope or publish while disconnected.
- **Boundary.** This lane is analysis only: it never decides the PAUSE default, applies the amendment, or treats the future modes as operative, and it does not select a process-containment technology, language or runtime implementation.

## Purpose

This research informs the exact per-effect-class semantics of the future `checkpoint`, `interrupt` and `drain` pause family plus an independent emergency stop, so the pause schema can be frozen. It is blocking because R3's transition/crash matrix and constitutional reconciliation options are prerequisites named in the agenda, and because a wrong disposition either strands in-flight work or admits an undeclared post-pause effect. It must also state where the desired v3 product policy differs from the operative constitution.

## Authority and boundaries

The authority, scope and privacy constraints are restated in `## Baked context`; read nothing else in preparation. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. In this lane the operative PAUSE is immediate halt; `checkpoint` is a selected future default that stays non-operative under `OR-020` until the exact amendment is applied.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. For each effect class — model turn, local transaction, subprocess, remote/disconnected action, read-only gate, publication, and ambiguous external effect — what exactly may finish, must be cancelled, or must be quarantined under `checkpoint`, `interrupt`, `drain` and emergency stop?
2. Which OS, workflow-engine, job-scheduler and agent-harness cancellation/shutdown contracts provide enforceable process-tree termination and quiescence, pinned by version and license?
3. What admission-epoch and fencing rule makes "no undeclared post-pause effect" falsifiable, and where can a checkpoint policy still leak one?
4. How is a model-turn boundary detected when a harness exposes only process/session boundaries, and what is the conservative fallback when it is unobservable?
5. For an already-dispatched effect without a receipt, what provider-identity/status evidence proves reality without blind retry or a false rollback claim?
6. Which transition/crash cells (before prepare, after prepare, during call, after effect before receipt, after receipt before projection) differ across the four modes?
7. How do disconnect and reconnect change permitted local completion and signed evidence spooling, and when must spooled evidence be revalidated before admission?
8. What precedence ordering (emergency, revocation, interrupt, checkpoint) holds across every effect class, and where does it observably break?
9. Which dispositions are implementable by a typed adapter versus the kernel, given an adapter may declare a narrower but never a wider disposition?
10. What acknowledgement and terminal labels (`ambiguous`, `quarantined`, `stale`) distinguish stopped, unknown and completed effects in owner-facing status?
11. What deadline miss should deterministically escalate `checkpoint` or `drain` into containment, and how is that outcome tested?
12. What are the competing constitutional reconciliation options — keep immediate halt, adopt the full future family, or stage adoption — and what decisive test separates them?
13. Under what conditions, if any, may a final bounded turn reach a checkpoint on capacity exhaustion without creating a new-effect escape hatch?

## Deliverable

- A source-pinned claim table with classification, confidence and expiry for every per-effect and per-mode claim.
- A transition and crash matrix covering all seven effect classes and all four modes with no silent gaps.
- Options with tradeoffs, each tied to a competing option and its decisive falsifier.
- An explicit statement of where desired v3 policy differs from the operative constitution, plus open Owner questions.

## Non-goals

- Do not decide the PAUSE default, apply the amendment, or treat future modes as operative.
- Do not reopen `OR-004` or `OR-020`, and do not promote a research recommendation into an Owner decision.
- Do not select a process-containment technology, language, or runtime implementation.
- Do not design or edit control-plane, auth, config, cron, or autonomy state.
- Do not include private project identity, transcripts, or local paths in any public packet.
- Do not recommend a mode without a competing option and a decisive falsifier.

## Completion gate

- Every per-effect claim is pinned to a primary source or explicitly marked unverified.
- The matrix covers every listed effect class and mode with no silent gap.
- Every recommendation carries a competing option and a decisive falsifier.
- The current immediate-halt PAUSE and `OR-004`/`OR-020` status are neither reopened nor promoted.
- No protected path is edited and no runtime/provider/auth/cron/PAUSE/spending effect occurs.
- The deliverable passes a privacy and secret scan with no local paths or identifiers.
- Owner questions are listed separately and no model opinion is presented as an Owner decision.

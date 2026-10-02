---
title: R-Q — Durable memory and knowledge architecture
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-Q — Durable memory and knowledge architecture

This is a durable-memory and knowledge-architecture handoff for accepted Owner decisions D-018,
D-019, D-022, D-024 and D-031, with the gap register in
[GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-P](R-P-prompt-injection-and-untrusted-input-defense.md), the untrusted-input handoff, and on
[R-T](R-T-multimodal-io-and-attachments.md), the multimodal-I/O handoff: R-P governs what may be
trusted as it enters context and R-T governs non-text artifacts, while R-Q designs the *durable
memory layer* that outlives a session, a context window, a compaction and a harness change. It
extends the context, compaction and cache research recorded in
[CONTEXT.md](../../CONTEXT.md) and [SYNTHESIS.md](../../research-lane/SYNTHESIS.md) rather than
restating them: compaction decides what stays in the current window, memory decides what persists
across windows, sessions, goals and projects. It must extend, not restate, the provenance and
capability semantics those lanes share. It does not select a language, store, framework, database,
vector index, embedding model or vendor, does not qualify any route, and executes no provider call.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone agent harness and a harness
orchestrator that delegates through other harnesses. Hermes-led control was retired on
2026-09-28 (state/DECISIONS.md D-017); Hermes is an optional upstream integration, not the
executive control plane. Workers are bounded executors. An implementer's own PASS is never
acceptance; independent review is required, and missing verification is never a pass.
`CONTROL_PLANE.md` is the operative constitution; a research session may propose amendments
but must never edit it. No research session performs implementation,
provider/model/authentication/configuration changes, spending, deployment, publication or
merge.

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

- The object of study is **long-term memory beyond context and compaction**: the durable,
  queryable knowledge that survives across sessions, goals, projects, harness changes and lost
  machines, as distinct from the current context window and from provider-side conversational
  memory.
- Types under consideration: stable **facts** (what is true of the project or environment),
  **preferences** (how the user wants work done), **decisions** (accepted Owner choices and
  their rationale) and **lessons** (what failed or worked and why). Each type is a proposal with
  provenance, not an authority, and none may silently widen a capability grant.
- D-018 makes Recursion a first-class native harness *and* a first-class wrapper over the wider
  harness ecosystem. Memory must therefore be provider-neutral and portable across harnesses and
  providers, not captive to one vendor's memory feature, and must not require a route that cannot
  be exported.
- D-019 ships every capability as an **opt-in plugin or profile** rather than a default: memory
  capture, retrieval and background consolidation are off unless enabled, and the disabled path
  must be inert (zero extraction call, zero embedding call, zero network egress, zero stored
  artifact).
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain`. Memory writes must be tied to a defined point in that lifecycle:
  what a Stop does to an in-flight memory extraction, whether a `drain` flushes pending writes,
  and what "written" versus "durably committed" honestly means.
- D-024 makes **productive continuity** the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting. Durable memory is a continuity mechanism
  only if it preserves authority and provenance too; a remembered preference must never become an
  authority grant by repetition, and a memory derived from untrusted content must retain its taint
  (R-P).
- D-031 forbids marketing Recursion on a "vendors sabotage quota" claim: memory quality,
  retrieval accuracy and conflict rates are reported as measured facts, never as vendor-intent
  narratives.
- Non-negotiable direction this lane must respect: the canonical store is the source of truth and
  memory is a derived projection, not a second canonical writer; authority is computed at
  effect-admission from current canonical state, never from a memory; `unknown` is never collapsed
  to zero; and every recommendation carries a competing option, a decisive falsifier and an
  explicit non-proof.
- Prior comparison coverage to extend, not reinvent: the multi-project supervision memory of
  DS-30, the context/cache economics of DS-12, the retention and deletion evidence contract of
  DS-07, the scientific-ARM federation of DS-14, the authority model of DS-02 and the untrusted
  input model of R-P. Provider "memory" features and plain repository context files are prior art
  cited from public documentation, not endorsed or selected components.
- Evidence status: no memory schema, store, retriever, ranker, consolidation job, deletion
  drill or portability fixture has been implemented or measured by Recursion for this lane. Every
  recall, precision, conflict, portability and privacy statement below is to be established from
  public source, documented behavior and a synthetic provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **durable memory and knowledge-architecture design candidate** for
Recursion. The lane specifies a typed memory model (facts, preferences, decisions, lessons) with
provenance, confidence, expiry and revocation; the rule that memory never confers authority;
retrieval and ranking that keep an authoritative source ahead of a remembered summary; conflict
resolution when two memories disagree; forgetting, redaction and deletion with a verifiable
completion state; privacy scoping across projects and audiences; cross-provider and cross-harness
portability; an explicit prohibition on persisting hidden chain-of-thought; and a comparison with
simple context files and provider-native memory. It delivers a design candidate with competing
options, decisive falsifiers and an explicit statement of what it does not prove, plus
provider-free fixtures. It does not select a language, store, database, index, embedding model or
vendor, does not qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, database, vector index, embedding model, memory product,
framework or vendor.** Do not decide an Owner question recorded in D-018, D-019, D-022, D-024 or
D-031. Treat every named provider memory feature, retrieval system or embedding approach as prior
art cited from public documentation, not as an endorsed or selected component. No provider, model
or account call is made; no memory is written to or read from a live system; no credential or
account is touched. Do not claim that memory is a source of authority, that a remembered decision
is an accepted decision, or that recall accuracy is high without measurement. Do not assert
portability or deletion guarantees that were not demonstrated; record each as a bounded or
`unknown` claim with a falsifier. Hidden chain-of-thought is neither requested, persisted nor
displayed.

## Inputs to read

None from this repository: the rescope, the authority, retention/deletion, context/compaction and
multi-project supervision semantics are summarized in `## Baked context` above, and no repository,
connector or private-source access is assumed. The session must, however, retrieve the public
documentation it cites — the public literature and benchmarks on long-term agent memory and
knowledge updating (for example multi-session recall and knowledge-update evaluations), the
documented behavior of provider-native memory and personalization features, the public
specifications for content provenance, data minimization, retention and deletion, and the
accepted authority and pre-effect-mediation contracts summarized above — and pin each claim to a
URL and retrieval date.

## Research questions

### Memory types, schema and provenance

1. What is the typed memory model — facts, preferences, decisions and lessons — and what fields
   does each entry carry: source, author (human, model or imported), trust class and taint
   inherited from R-P, goal/project scope, creation and observation time, confidence, expiry,
   revocation state and the canonical reference it derives from?
2. How is memory kept a **derived projection** of canonical state rather than a second source of
   truth, so that a remembered decision, preference or fact can never override, contradict or
   substitute for the canonical Owner decision it summarized?
3. How is authority excluded from memory by construction: what prevents a remembered preference,
   repeated instruction or model-inferred fact from being read as a capability grant at
   effect-admission time?
4. How is hidden chain-of-thought excluded from persistence while still recording the recoverable
   state — decisions, evidence, actions, uncertainties and next steps — that D-024 requires, and
   what is the honest distinction between a stored rationale and an opaque reasoning trace?

### Retrieval, ranking and conflict

5. How is retrieval scoped by goal, project and audience, and how is ranking designed so that
   current authoritative sources, recent accepted decisions and high-confidence facts outrank
   stale summaries, low-confidence inferences and untrusted-derived content?
6. What signal set ranks a memory — recency, confidence, source trust, usage, goal relevance,
   direct user confirmation — and how is each signal kept from becoming a popularity or repetition
   loop that promotes a wrong memory because it was retrieved often?
7. How are conflicts between memories resolved and surfaced: when two entries disagree, when a
   newer fact supersedes an older one, when a remembered decision is revoked, and when the
   authoritative source and the memory diverge — and what is the competing option (auto-resolve
   versus escalate) and its falsifier?
8. How do retrieval and ranking avoid cross-project leakage and avoid exposing private content, raw
   digests or stable size/timing patterns that make equality or membership testable across a
   privacy boundary?

### Forgetting, redaction, deletion and privacy scoping

9. What are the mechanisms for forgetting, expiry, redaction and hard deletion, and how is
   deletion proven complete across every derived copy — index, cache, embedding, backup and
   downstream summary — rather than assumed from a primary-store delete (extending the DS-07
   deletion-evidence contract)?
10. How is revocation applied when a memory's source is revoked or its authority context changes,
    so that a preference learned under one goal does not silently persist into another goal or
    another project?
11. What privacy scopes are required — per-user, per-project, per-goal and per-audience — and how
    is a memory prevented from becoming visible to a broader audience than its strictest input?
12. How are memory extraction, consolidation and retrieval made inert when the capability is
    disabled under D-019, with a zero-effect predicate, and how is this tested?

### Portability, continuity and comparison

13. What makes the memory layer portable across providers and harnesses — a provider-neutral
    schema, exportable canonical entries, lossy-versus-lossless adaptation — and what semantic
    loss occurs when a memory is reconstructed on a different provider or harness?
14. How does durable memory support D-024 productive continuity when a machine is lost or a
    harness changes, and how is a memory safely rehydrated only after authority and provenance are
    revalidated rather than trusted on load?
15. Against **simple context files** (checked-in markdown, notes, repository docs) and
    **provider-native memory**, which cells are source-documented, inferred or `unknown`, and what
    genuine capability does a typed, provenance-carrying, revocable memory layer add that a flat
    context file or a vendor memory feature does not?
16. What is the decisive falsifier for each claimed advantage: for example a case where provider
    memory or a context file yields equal or better recall at lower cost, or where the typed layer
    loses a sanitization, deletion or portability property the simpler option had?

### Provider-free acceptance fixtures

17. What provider-free fixtures must accept or reject: a recall fixture across sessions, a
    knowledge-update fixture where a newer fact supersedes an older one, a conflict fixture, a
    revocation fixture, a deletion-completeness drill, a cross-project privacy isolation probe, a
    portability round-trip, and a disabled-path inertness soak — and what is the exact pass/fail
    predicate for each?
18. How do the fixtures prove that memory never confers authority, never overrides canonical state,
    never persists hidden chain-of-thought, never leaks across a privacy boundary, and never blocks
    the canonical writer, Stop or recovery — using synthetic entries and local processes only, with
    no provider call?
19. How is each result classified as source-documented, locally observed, inferred or `unknown`,
    and what does the suite not establish — for example no measured real-world recall accuracy, no
    coverage of an adaptive adversary and no claim about any specific provider's memory behavior?

## Deliverable

A durable memory and knowledge-architecture design candidate containing: a typed memory model
(facts, preferences, decisions, lessons) with a provenance, confidence, expiry and revocation
schema and an explicit prohibition on hidden chain-of-thought; a derived-projection rule that
memory is never a source of authority and never overrides canonical state; a retrieval, ranking
and conflict-resolution section scoped by goal, project and audience; a forgetting, redaction and
deletion section with a derived deletion-completeness predicate and privacy scoping; a portability
section covering cross-provider and cross-harness export, rehydration after revalidation and a
comparison with simple context files and provider-native memory; and a provider-free fixture suite
for recall, knowledge update, conflict, revocation, deletion completeness, privacy isolation,
portability and disabled-path inertness. Each recommendation names a competing option, a decisive
falsifier and what it does not prove. No language, store, database, index, embedding model or
vendor is selected.

## Non-goals

- No selection of a language, package manager, store, database, vector index, embedding model,
  memory product, framework or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that memory confers authority, that a remembered decision is an accepted decision,
  or that recall accuracy, conflict rate or portability are high where no measurement exists.
- No persisted or displayed hidden chain-of-thought; recoverable state is decisions, evidence,
  actions, uncertainties and next steps only.
- No provider, model, credential or account call; no live memory read or write; every fixture is
  synthetic and provider-free.
- No new executive tier, no separate AI "ARM manager", and no second canonical writer created by a
  memory store.
- No claim that a simple context file or a provider memory feature is sufficient or insufficient
  without a documented comparison and a falsifier.
- No reopening of D-018, D-019, D-022, D-024 or D-031, and no vendor-sabotage narrative (D-031).
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The memory model defines facts, preferences, decisions and lessons with provenance, confidence,
  expiry and revocation, and states that no memory entry carries or confers authority.
- The candidate states that memory is a derived projection of canonical state and can never
  override, substitute for or outrank the canonical Owner decision or acceptance gate.
- Retrieval and ranking are scoped by goal, project and audience, and conflict resolution is
  defined for supersession, revocation and source divergence with a competing option and a
  decisive falsifier.
- The forgetting, redaction and deletion section specifies a derived deletion-completeness
  predicate across index, cache, embedding, backup and downstream summary, and defines privacy
  scoping at the strictest input classification.
- The portability section defines cross-provider and cross-harness export and rehydration after
  authorization and provenance revalidation, and compares the layer with simple context files and
  provider-native memory with per-cell evidence classes.
- The candidate prohibits persistence and display of hidden chain-of-thought while preserving the
  recoverable decisions, evidence, actions, uncertainties and next steps D-024 requires.
- The provider-free fixture suite specifies predicates for recall, knowledge update, conflict,
  revocation, deletion completeness, privacy isolation, portability and disabled-path inertness,
  and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, database, index, embedding model or vendor is selected and no route is
  qualified.
- The candidate explicitly states what it does not establish: no measured real-world recall,
  conflict or portability result, no coverage of an adaptive adversary, no route qualification and
  no entitlement.
- Protected paths are untouched; privacy and secret scan are clean.

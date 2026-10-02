---
title: R-V — Observability, introspection and replay debugging
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-V — Observability, introspection and replay debugging

This is a model-free observability and debugging handoff for accepted Owner decisions D-018,
D-019, D-022, D-024 and D-031, with the gap register in
[GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-O](R-O-performance-and-configurability-engineering.md), the backend-performance handoff, and
on [R-K](R-K-terminal-multiplexer-and-tui.md), the terminal-multiplexer handoff, and must extend
rather than restate them: R-O specifies what to measure and R-K specifies the views that display
it, while R-V designs the **deterministic, model-free explanation and replay-debugging** layer
behind those views — how Recursion explains routing, admission, compaction and effects, and how a
human reproduces a run from canonical events without spending a model token.

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

- The object of study is **explainability and debuggability without inference**. Recursion must
  be able to answer "why did this task take this route, admit this worker, compact here, retry,
  spend this much, or produce this effect?" from its own canonical records, deterministically and
  cheaply, and a developer must be able to reproduce a run from recorded events without invoking
  a model.
- D-018 makes Recursion a first-class native harness *and* a unifying wrapper whose purpose is to
  remove lock-in and cut quota/usage burn. An observability layer that itself spends tokens, or
  that cannot compare routes without model calls, defeats that purpose; explanation must be a
  property of the kernel's records, not a second inference pass.
- D-019 ships every capability as an **opt-in plugin or profile** with no default spend. Tracing,
  timelines, graph views and telemetry export must therefore be opt-in and add no inference,
  indexing or activation by default; a view that is never opened must cost nothing.
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain`. The observability layer must show honestly what a Stop did and did not
  do, including a source interrupt, socket close or killed PID being **not** external rollback,
  and must not present "requested" as "observed".
- D-024 makes **productive continuity** the headline measurable differentiator across harness
  change, compaction, source fork and lost machine, preserving authority, evidence and honest
  accounting. Replay debugging is the mechanism that demonstrates continuity; the layer must
  reproduce a run's decisions and effects from canonical events, or state exactly where the
  record is insufficient.
- D-031 forbids a "vendors sabotage quota" claim: explanations of cost, retry and route choice
  are reported as recorded facts and honest counters, never as vendor-intent narratives or
  inferred motives.
- Honest counters are the substrate. DS-26 records that no telemetry adapter was exercised and
  that counters must keep `unknown` distinct from zero; DS-10 records replay verification as
  unmeasured; DS-25 records the recovery matrix as unmeasured. Every dashboard, timeline and
  explanation below must inherit those gaps rather than fill them with plausible numbers.
- Privacy is a hard constraint: telemetry is privacy-preserving by construction, content-free
  where possible, and a public session never receives private content, local paths, credentials
  or account identifiers. "Explain" the decision, not the private payload.
- Already accepted direction this lane must respect: the canonical event is appended before any
  presentation queue may coalesce or drop anything; command, lease, process-exit, termination and
  canonical-state events may not be dropped; the canonical writer defines the authoritative
  event order; and hidden chain-of-thought is neither required nor persisted — recoverable state
  consists of decisions, evidence, actions, uncertainties and next steps.
- Prior comparison coverage to extend, not reinvent: the rich command and compaction receipts
  already present in OpenCode, the projected-history forks and compaction receipts of OpenCode
  v2, the command/effect-state separation seen in T3 Code, and the usage/cost surfaces of the
  public upstream harnesses. These are version-specific comparison candidates cited from public
  documentation, not endorsed components.
- Evidence status: no tracing span, replay engine, timeline view, counter pipeline or telemetry
  exporter has been implemented or measured by Recursion for this lane. Every fidelity, cost,
  coverage and privacy statement below is to be established from public source and a synthetic
  provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **model-free observability, introspection and replay-debugging design
candidate** for Recursion. The lane specifies deterministic explain output for routing,
admission, compaction and effects; a causal tracing model over canonical events; replay
debugging that reconstructs a run from the canonical record without inference; timeline and graph
views that are truthful about gaps; honest-counter and unknown-preserving accounting; and a
privacy-preserving telemetry contract. It compares competing mechanisms (structured event log,
span/causal graph, deterministic re-derivation, sampled profiling) with a decisive falsifier for
each and selects none. It delivers a design candidate with provider-free acceptance fixtures and
an explicit statement of what explanation does **not** prove. It does not select a language,
store, framework, tracing library, telemetry backend or vendor, does not qualify any route, and
executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, tracing library, telemetry backend, query
language or vendor.** Do not decide an Owner question recorded in D-018, D-019, D-022, D-024 or
D-031. No provider, model or account call is made; no telemetry endpoint is contacted; no
credential or account is touched. Do not request or display hidden chain-of-thought; explain
decisions, evidence, actions, uncertainties and next steps, not private reasoning traces. Do not
claim that a replay proves semantic correctness or provider behavior; it proves reproduction of
recorded decisions and effects, and it must name what it cannot reconstruct. Do not present
`unknown` counters as zero, and do not attribute cost or retry behavior to vendor intent.

## Inputs to read

None from this repository: the rescope, the honest-counter and measurement contracts, the
pause/stop vocabulary and the continuity endpoints are summarized in `## Baked context` above,
and no repository, connector or private-source access is assumed. The session must, however,
retrieve the public documentation it cites — the OpenTelemetry specification and semantic
conventions, the W3C Trace Context and Event Logging recommendations, structured-logging and
audit-log guidance, causal-graph and deterministic-replay literature, the public OpenCode and T3
Code command/effect-state documentation, and the public company engineering documentation on
privacy-preserving telemetry and high-cardinality observability — and pin each claim to a URL
and retrieval date.

## Research questions

### Deterministic explanation of decisions

1. What is the deterministic **explain** contract for a routing decision: from recorded candidate
   descriptors, admission verdicts, budget and authority state, and the selection predicate,
   reconstruct why one route was chosen and every alternative refused — with no model call and no
   post-hoc narrative?
2. What is the explain contract for **admission** (why a worker, plugin or parallel step was
   admitted, queued, deferred or refused) and for **resource** decisions (water marks, reserves,
   concurrency limits), such that an operator can see the exact predicate and inputs?
3. What is the explain contract for **compaction**: which governor owned the transition, which
   artifacts were retained, transformed, dropped or rehydrated, what fidelity checks passed or
   failed, and why the epoch advanced — distinguished from a summary that merely narrates?
4. What is the explain contract for **effects**: what the task intended to do, what was actually
   attempted, what was observably applied, what is unverified, and what is pending — with the
   distinction between saved-locally, accepted, delivered/applied and observed outcome kept
   explicit and never collapsed into one success badge (D-024)?
5. How does the explain output remain honest about an **incomplete record** — a replay gap, a
   dropped presentation frame, a counter that was unavailable — by emitting a marker and an
   `unknown`, rather than inventing a step or a value?

### Causal tracing and views

6. What causal model links canonical events into a trace: which identifiers correlate a task, a
   step, a lease, a model call, an effect and a recovery across actors, nodes and harnesses, and
   how are parent/child and cause/effect edges recorded rather than inferred?
7. What is the minimal, stable, versioned trace schema that is model-free, store-neutral and
   safe to retain — what fields, what cardinality, what retention and what redaction — given that
   high-cardinality identifiers and content must not leak private data?
8. What timeline view makes a run skimmable (task phases, waits, retries, stops, compactions,
   effects) and what graph view makes causality navigable, without opening telemetry and evidence
   panes simultaneously by default (D-019) and without repainting the whole log on every event?
9. How are views bounded so a slow or absent viewer cannot block the canonical append, Stop or
   recovery, and so the explanation is derived from the canonical record rather than from a
   best-effort presentation stream?
10. How is an explanation kept **reproducible** — same canonical record yields the same explain
    output — including across schema versions, so a reviewer can independently re-derive it?

### Replay debugging from canonical events

11. What is the replay-debugging contract: starting from a checkpoint plus the canonical event
    suffix, reconstruct the run's decisions and state transitions deterministically, and stop
    exactly at the first event whose inputs are missing rather than guessing?
12. How does replay handle non-determinism — wall-clock time, entropy, scheduling, external
    effect outcomes, provider responses and floating-point — by injecting recorded inputs rather
    than re-sampling, and by distinguishing "replayed" from "re-executed"?
13. How is a replay **verified**: comparing re-derived state digests against the recorded
    canonical digest, and reporting divergence at the first differing event with the evidence
    needed to adjudicate — without claiming the replay proves the original was correct?
14. How does replay support debugging a failed or interrupted task after a crash, a lost node, a
    harness change or a source fork (D-024), and how does it mark the exact point where recovery
    began so the two segments are not conflated?
15. What is the **cost** model for replay debugging: tokens spent (expected zero), wall time,
    memory, disk read and CPU, and what does replay do that cannot be done cheaper by reading the
    event log directly?

### Honest counters and privacy-preserving telemetry

16. What counters must exist for explanation — decisions, admissions, refusals, retries, route
    switches, compactions, rehydrations, effects attempted/applied/failed, wasted work, recovered
    work, human corrections — and how is each labeled `unknown` when its source is unavailable,
    so no consumer reads `unknown` as zero?
17. What is the telemetry contract: opt-in by default, content-free or content-minimized,
    cardinality-bounded, locally retained first, and exporting only what a user explicitly
    authorizes — with a falsifier for any claim that telemetry is privacy-preserving?
18. How are local explanations separated from exportable telemetry so that a public or support
    export never includes private repository content, prompts, tool outputs, local paths,
    credentials or stable cross-project identifiers?
19. How does the layer route or alert on anomalies (retry storms, budget burn, replay gaps,
    containment refusals) **without** a model and without creating a standing autonomous
    executive or a self-activating agent (D-019, and no standing executive per ANCHOR)?
20. What does the observability layer explicitly **not** prove: that a decision was optimal, that
    a replay is semantically faithful to an external system, that counters are complete, that a
    trace explains model internals, or that absence of an anomaly means correctness?

### Provider-free acceptance fixtures

21. What provider-free fixtures must accept or reject: an explain-routing fixture with a known
    verdict and a refusal, a compaction-fidelity explanation, an effects-honesty fixture
    (intended vs applied vs observed), a replay-determinism fixture that reproduces a state
    digest, a replay-divergence fixture that stops at the first missing input, a counter
    `unknown`-preservation fixture, a slow-viewer isolation fixture, and a telemetry-redaction
    fixture — and what is the exact pass/fail predicate for each?
22. How do the fixtures prove that explanation and replay spend zero model tokens, that views
    cannot block the canonical writer or Stop, that a replay gap is shown as a marker rather than
    a fabricated step, and that no export leaks private content — using synthetic events only,
    with no provider call?

## Deliverable

A model-free observability, introspection and replay-debugging design candidate containing: a
deterministic-explanation section covering routing, admission, compaction and effects, with the
saved-locally / accepted / delivered / observed / pending distinctions and explicit `unknown`
markers for incomplete records; a causal-tracing and views section defining the trace schema,
correlation identifiers, retention and redaction, and bounded timeline and graph views that
cannot block the canonical writer or Stop; a replay-debugging section defining checkpoint-plus-
suffix re-derivation, non-determinism injection, digest-verified replay and divergence reporting
across crash, node loss, harness change and source fork; an honest-counter and privacy-preserving
telemetry section; and a provider-free fixture suite for every predicate above. Each
recommendation names a competing option, a decisive falsifier and what explanation does not
prove. No language, store, framework, runtime, tracing library, telemetry backend or vendor is
selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, tracing library,
  telemetry backend, query language or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No request for or display of hidden chain-of-thought; explanations use decisions, evidence,
  actions, uncertainties and next steps only.
- No claim that a replay proves semantic correctness, provider behavior or causal optimality, or
  that a missing anomaly proves correctness.
- No counter reported as a number when its source is unavailable; `unknown` is preserved, never
  zero.
- No telemetry that exports private repository content, prompts, tool outputs, local paths,
  credentials or stable cross-project identifiers.
- No provider, model, credential or account call; no telemetry endpoint contacted; every fixture
  is synthetic and provider-free.
- No new executive tier, no standing autonomous executive and no self-activating anomaly agent.
- No reopening of D-018, D-019, D-022, D-024 or D-031, and no reopening of the accepted
  performance requirements in `PERFORMANCE-PLAN.md` or the terminal requirements in
  `TERMINAL-RUNTIME.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The deterministic-explanation section defines model-free explain output for routing, admission,
  compaction and effects, and keeps saved-locally, accepted, delivered/applied, observed outcome
  and settled/pending distinct rather than collapsing them into one status.
- Explanation of effects and Stop reports honest boundaries: requested is not observed, a source
  interrupt, socket close or killed PID is not external rollback, and a replay gap is a marker
  rather than an invented step.
- The causal-tracing section defines correlation identifiers and a versioned, model-free,
  store-neutral trace schema with retention and redaction, and bounded timeline and graph views
  that cannot block canonical append, Stop or recovery.
- The replay-debugging section defines checkpoint-plus-canonical-suffix re-derivation, injected
  recorded inputs for non-determinism, digest-verified replay, and first-divergence reporting
  across crash, lost machine, harness change and source fork, distinguishing replayed from
  re-executed.
- The counters section defines the explanation counters and preserves `unknown` distinct from
  zero; the telemetry section is opt-in, content-minimized, cardinality-bounded and locally
  retained before any export, with a falsifier for the privacy-preserving claim.
- The provider-free fixture suite specifies predicates for routing/refusal explanation,
  compaction fidelity, effects honesty, replay determinism, replay divergence, counter
  `unknown`-preservation, slow-viewer isolation and telemetry redaction, and no fixture requires
  a provider call.
- The candidate states the cost of explanation and replay, expected zero model tokens, and what
  the layer does not prove: no optimal decision, no semantic fidelity to an external system, no
  counter completeness and no proof from absence.
- Every recommendation names a competing option, a decisive falsifier and what it does not
  prove; no language, store, framework, runtime, tracing library, telemetry backend or vendor is
  selected and no route is qualified.
- Protected paths are untouched; privacy and secret scan are clean.

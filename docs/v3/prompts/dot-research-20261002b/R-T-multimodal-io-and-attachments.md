---
title: R-T — Multimodal I/O and attachments
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-T — Multimodal I/O and attachments

This is a multimodal-input/output and attachments handoff for accepted Owner decisions D-018,
D-019, D-022, D-024 and D-031, with the gap register in
[GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-P](R-P-prompt-injection-and-untrusted-input-defense.md), the untrusted-input handoff, and on
[R-Q](R-Q-durable-memory-and-knowledge-architecture.md), the durable-memory handoff: R-P governs
the trust of untrusted bytes and R-Q governs what persists, while R-T designs how images,
screenshots, audio, video and documents enter and leave the system as context, evidence, budgeted
artifacts and rendered output. It extends the context and artifact model in
[CONTEXT.md](../../CONTEXT.md) and the provider-capability model in
[ROUTE-CAPABILITIES.md](../../ROUTE-CAPABILITIES.md) rather than restating them. It must extend,
not restate, the accounting, sandbox and terminal semantics those lanes share. It does not select
a language, store, framework, media codec, OCR/ASR engine, rendering library or vendor, does not
qualify any route, and executes no provider call.

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

- The object of study is **multimodal input and output**: images, screenshots, diagrams, audio,
  video, and documents (PDF, office documents, structured files) as *inputs*, and generated
  images, diagrams, audio or documents as *outputs*. The question is how each modality flows
  through the same context, evidence, budget, accounting, privacy and rendering contracts as text
  rather than becoming a parallel side channel.
- D-018 makes Recursion a first-class native harness *and* a first-class wrapper over the wider
  harness ecosystem; provider multimodal capability differs sharply by route and changes over
  time, so the design must be provider-neutral, describe capability via maintained descriptors,
  and never assume one vendor's multimodal API.
- D-019 ships every capability as **opt-in plugin or profile** rather than a default. Attachment
  ingestion, local OCR/ASR, media rendering and any cloud media call are off unless enabled, and
  the disabled path must be inert (zero decode, zero model call, zero upload, zero network egress,
  zero stored artifact).
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain`. A long decode, upload, stream or render must be interruptible, and the
  honest accounting of a partially received or partially sent attachment must be defined.
- D-024 makes **productive continuity** the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting. An attachment referenced by a task must
  remain resolvable and attributable after a harness change, and a re-derivation (for example
  re-OCR) must not fabricate content.
- D-031 forbids marketing Recursion on a "vendors sabotage quota" claim: modality coverage, cost,
  latency and quality differences are reported as measured facts, never as vendor-intent
  narratives.
- Non-negotiable direction this lane must respect: provider capability is described by a
  maintained, versioned route descriptor and a conflict degrades to the conservative bound;
  untrusted media is untrusted input under R-P and is parsed in the R-U boundary; every attached
  artifact carries provenance and an evidence class; `unknown` is never collapsed to zero; and
  every recommendation carries a competing option, a decisive falsifier and an explicit non-proof.
- Prior comparison coverage to extend, not reinvent: the context artifact model and privacy classes
  of [CONTEXT.md](../../CONTEXT.md), the route capability descriptor of
  [ROUTE-CAPABILITIES.md](../../ROUTE-CAPABILITIES.md), the two-ledger accounting of DS-26 and
  [TELEMETRY.md](../../TELEMETRY.md), the untrusted-input model of R-P, the sandbox boundary of
  R-U and the terminal rendering contract of [R-K](R-K-terminal-multiplexer-and-tui.md). Public
  multimodal APIs, local OCR/ASR engines and terminal image protocols are prior art cited from
  public documentation, not endorsed or selected components.
- Evidence status: no attachment pipeline, OCR/ASR integration, media accounting, provider
  capability probe or terminal media renderer has been implemented or measured by Recursion for
  this lane. Every fidelity, cost, latency, bandwidth and render statement below is to be
  established from public source, documented behavior and a synthetic provider-free fixture, or
  marked `unknown`.

## Purpose

Produce the decision-ready **multimodal-I/O and attachments design candidate** for Recursion. The
lane specifies how images, screenshots, audio, video and documents enter the system and flow
through context, evidence, budget and accounting; how provider capability differences and
resulting semantic loss are described and bounded; when local OCR/ASR is used versus a route
call; the privacy, egress and untrusted-media rules for derived and raw media; how rich media is
rendered or referenced in a terminal-first interface; and decisive falsifiers for each. It
delivers a design candidate with competing options, decisive falsifiers and an explicit statement
of what it does not prove, plus provider-free fixtures. It does not select a language, store,
framework, media codec, OCR/ASR engine, cloud service, rendering library or vendor, does not
qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, media codec, OCR/ASR engine, cloud media service,
rendering library, terminal image protocol or vendor.** Do not decide an Owner question recorded
in D-018, D-019, D-022, D-024 or D-031. Treat every named multimodal API, OCR/ASR engine and
terminal image protocol as prior art cited from public documentation, not as an endorsed or
selected component. No provider, model or account call is made; no media is uploaded, decoded from
a real private source or rendered live; no credential or account is touched. Do not claim that a
modality is universally supported, that OCR/ASR output is correct, or that semantic loss is
negligible without measurement; each is a bounded or `unknown` claim with a falsifier. Do not
claim that an attachment confers authority or becomes trusted evidence by arriving in context.
Hidden chain-of-thought is neither requested nor displayed.

## Inputs to read

None from this repository: the rescope, the context/artifact and privacy model, the route
capability descriptor, the accounting contract, the untrusted-input and sandbox boundaries and the
terminal rendering contract are summarized in `## Baked context` above, and no repository,
connector or private-source access is assumed. The session must, however, retrieve the public
documentation it cites — the official multimodal input/output documentation for the providers it
compares, the public specifications and documentation for OCR and speech-to-text engines, the
media container and accessibility guidance for terminal rendering and alt text, and the public
guidance on metadata, privacy and egress for uploaded media — and pin each claim to a URL and
retrieval date.

## Research questions

### Input modalities and ingestion

1. What input modalities must be supported as attached artifacts — images, screenshots, diagrams,
   audio, video and documents — and what does a unified attachment object carry: media type,
   origin, capture time, size, digest, provenance, trust class (R-P), privacy scope and the
   evidence class of any derived text?
2. How is each modality normalized into context without assuming a provider accepts it natively —
   pass-through, local transcription, local description, chunking of long documents or video,
   region cropping — and what is the competing option and its falsifier?
3. How is a document handled as structured content (text, tables, layout, page references) rather
   than a flat blob, and how are page or timestamp references preserved so evidence can be cited
   back to a location?
4. How does the pipeline handle an attachment a route cannot accept — refuse, degrade to a local
   derivation, or delegate to another route — without silently dropping content or inflating cost?

### Provider capability differences and semantic loss

5. How does the route capability descriptor express multimodal support — accepted media types,
   size and count limits, token or billing treatment, native versus transcribed handling, and the
   discovery method and evidence timestamp — so capability is provider-neutral and revalidated?
6. What semantic loss occurs when a modality is transcribed, summarized, downscaled, frame-sampled
   or re-derived, and how is that loss recorded on the artifact and surfaced rather than hidden?
7. How does a capability conflict (descriptor versus runtime discovery, or a changed provider
   limit) degrade to the conservative bound and alert, without silently widening what is sent or
   billed?
8. How are account, entitlement, cost and quota differences between routes for the same media
   reported as measured facts (D-031) rather than assumed or attributed to vendor intent?

### Local processing, privacy and egress

9. When is local OCR, ASR or media analysis preferred over a route call — privacy, cost, latency,
   offline operation, determinism — and what is the competing option and decisive falsifier for
   each choice?
10. How are derived artifacts (transcripts, OCR text, thumbnails, extracted metadata) classified,
    stored and expired under the same provenance, deletion and privacy-scoping rules as other
    memory and artifacts (R-Q), including metadata such as EXIF that may leak location or device?
11. What egress decision governs sending raw or derived media to a provider or upstream harness,
    how is the exact bytes-to-send compiled and authorized, and how is an upload blocked when
    privacy scope or capability does not permit it?
12. How is untrusted media treated as untrusted input (R-P) and parsed inside the sandbox boundary
    (R-U), so a hostile document, image or container cannot exploit a parser, run code or reach the
    network, and what is the fail-closed behavior on a parse failure?

### Context, evidence, budgets and accounting

13. How do media artifacts consume context budget — tokens, bytes, pixels, duration or frames —
    and how is that consumption counted per modality with `unknown` kept distinct from zero when a
    route cannot report a counter?
14. How do media artifacts participate in compaction and caching (D-024 and
    [CONTEXT.md](../../CONTEXT.md)): what is droppable, what is rehydratable by reference, and how
    is a rehydrated media artifact revalidated rather than assumed unchanged?
15. How are media cost and usage entered into the accounting ledgers (DS-26 and
    [TELEMETRY.md](../../TELEMETRY.md)), including provider-native tokenization of images or audio
    and local compute cost, so no modality becomes an unaccounted side channel?
16. How does a long decode, upload or stream map to the D-022 Stop vocabulary and to partial
    delivery, so that a Stop leaves an honest record of what was sent, received, billed or left
    incomplete?

### Terminal rendering and output modalities

17. How is rich media represented in a terminal-first interface — inline protocol, half-block or
    character rendering, a text description, or an explicit open-in-viewer reference — and what are
    the accessibility, plain-text, high-contrast and reduced-motion requirements for each?
18. What output modalities may be produced — images, diagrams, audio, documents — and how is a
    generated artifact attributed, versioned, budgeted and rendered or referenced without implying
    it is trusted evidence?
19. How is alt text, a caption or a description attached so a non-visual or low-bandwidth client
    can consume the content, and how is that description marked as a derived, possibly lossy
    artifact rather than the source?
20. What is the fallback when a terminal cannot render a modality — a stable text placeholder, a
    local path reference, or a deferred open — and how is the canonical record kept complete
    regardless of the view?

### Falsifiers and fixtures

21. What is the decisive falsifier for each recommendation — for example local OCR or ASR measured
    worse on accuracy or cost than a route call, a rendering approach that corrupts or blocks the
    interface, a modality whose accounting is unknowable, or a privacy case that must refuse
    upload?
22. What provider-free fixtures must accept or reject: an attachment ingestion and provenance
    round-trip, a capability-conflict degradation, a transcription-loss record, a local OCR/ASR
    path, a privacy-blocked egress, a hostile-document parse-failure, an accounting fixture for a
    modality with an unavailable counter, a long-upload Stop, a terminal rendering fallback and a
    disabled-path inertness soak — and what is the exact pass/fail predicate for each?
23. How do the fixtures prove that an attachment never confers authority or becomes trusted
    evidence by arrival, that a disabled multimodal path is inert, that media accounting never
    reads `unknown` as zero, and that no modality blocks the canonical writer, Stop or recovery —
    using synthetic media only, with no provider call?
24. How is each result classified as source-documented, locally observed, inferred or `unknown`,
    and what does the suite not establish — for example no measured accuracy, cost or latency
    advantage, no complete provider-modality coverage, no route qualification and no entitlement?

## Deliverable

A multimodal-I/O and attachments design candidate containing: an input-modality and ingestion
section defining a unified attachment object with provenance, trust and privacy scope; a
provider-capability section tying support to the route capability descriptor and recording
semantic loss; a local-processing, privacy and egress section covering OCR/ASR choice, metadata
handling, exact-bytes egress authorization and untrusted-media parsing; a context, evidence,
budget and accounting section covering per-modality counters, compaction/rehydration, ledger entry
and D-022 Stop interaction; a terminal-rendering and output-modality section covering inline,
character, description and reference fallbacks with accessibility; and a provider-free fixture
suite for ingestion, capability conflict, transcription loss, local OCR/ASR, privacy-blocked
egress, hostile-document parse failure, unavailable-counter accounting, long-upload Stop, terminal
fallback and disabled-path inertness. Each recommendation names a competing option, a decisive
falsifier and what it does not prove. No language, store, framework, media codec, OCR/ASR engine,
cloud service, rendering library or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, media codec, OCR/ASR engine,
  cloud media service, rendering library, terminal image protocol or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that a modality is universally supported, that OCR/ASR output is correct, or that
  semantic loss is negligible without measurement; those cells stay bounded or `unknown`.
- No assertion that an attachment, transcript or generated artifact confers authority or is
  trusted evidence by arriving in context.
- No upload or egress of private, sensitive or unclassified media without an explicit authorization
  and privacy-scope decision.
- No provider, model, credential or account call; no live media decode from a private source; every
  fixture is synthetic and provider-free.
- No vendor-sabotage narrative; every modality cost, quality and latency comparison is a measured
  fact with provenance and uncertainty (D-031).
- No new executive tier, no separate AI "ARM manager", and no media side channel that bypasses the
  canonical writer, accounting or Stop.
- No reopening of D-018, D-019, D-022, D-024 or D-031.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The ingestion section defines a unified attachment object (media type, origin, time, size,
  digest, provenance, trust class, privacy scope, derived-evidence class) and a normalization path
  for images, screenshots, audio, video and documents that does not assume native provider
  support.
- The provider-capability section describes multimodal support through the maintained route
  capability descriptor, records semantic loss on every derived artifact, and degrades to the
  conservative bound on a capability conflict.
- The privacy and egress section defines local-versus-route processing with a falsifier, metadata
  handling, exact-bytes egress authorization, and untrusted-media parsing inside the sandbox with
  a fail-closed behavior.
- The context, evidence, budget and accounting section defines per-modality counters that keep
  `unknown` distinct from zero, compaction and rehydration-by-reference with revalidation, ledger
  entry, and a D-022 Stop contract for partial decode, upload or stream.
- The terminal-rendering section defines inline, character, description and reference fallbacks
  with plain-text, high-contrast, reduced-motion and alt-text requirements, and keeps the canonical
  record complete regardless of the view.
- The provider-free fixture suite specifies predicates for ingestion and provenance, capability
  conflict, transcription loss, local OCR/ASR, privacy-blocked egress, hostile-document parse
  failure, unavailable-counter accounting, long-upload Stop, terminal fallback and disabled-path
  inertness, and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, framework, media codec, OCR/ASR engine, cloud service, rendering library or
  vendor is selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured accuracy, cost, latency
  or fidelity advantage, no complete provider-modality coverage, no route qualification and no
  entitlement.
- Protected paths are untouched; privacy and secret scan are clean.

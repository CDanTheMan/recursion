---
title: R-B — Delegating across harnesses without credential intermediation
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-B — Delegating across harnesses without credential intermediation

This is a rescope handoff for accepted Owner decisions D-021, D-023 and D-024, and the gap
register in [GAPS.md](../../research-lane/GAPS.md).

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

- D-021 accepts **delegation over credential intermediation**: Recursion must not hold, copy or
  relay provider credentials it was not explicitly granted; where possible it delegates a request
  to a user-authenticated local tool or harness rather than intermediating login, because driving
  the user's already-authenticated CLI is the preferred route over capturing OAuth tokens.
- D-023 qualifies Codex App Server end-to-end first (steering, correlated approvals/questions,
  resume, compaction, review) as the strongest structured interface; all other harnesses ship as
  plugins, and a deliberately different second adapter is an architecture stress test.
- D-024 makes **productive continuity** the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting.
- Prior public route research found interface breadth across ACP/HTTP/SSE/gateway surfaces but
  repeatedly warned that a documented interface is not proof of active steering, durable waiters,
  complete mediation, effect settlement or entitlement. Concrete gaps include in-memory pending
  question maps, unproven `prompt_async` steering, compaction helpers excluded from some usage
  counters, fail-open hooks, and redirect-to-background behavior. Several of these are
  source-documented seams, not observed exploits.
- No cross-harness continuity experiment has been run. Where a harness verb is not documented, the
  honest status is `unknown`, not assumed.

## Purpose

Produce the decision-ready evidence pack for delegating a Recursion request across multiple
harnesses without Recursion holding, copying or intermediating credentials, while preserving
authority, context and evidence. This is a research and design lane: it maps documented
delegation surfaces, classifies capability and loss, proposes a delegation architecture, and
specifies a falsifiable productive-continuity experiment. It does not call any provider, run any
harness, log in anywhere, or select a vendor.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Preserve the current Hermes constitution; propose amendments, never edit it. Public Deep
Research receives only public or synthetic briefs. **DO NOT select a language, store, framework,
protocol, transport or vendor as a product default.** No credential is collected, displayed,
copied or relayed; no OAuth flow is designed to capture tokens; no login is performed. Do not
claim that any harness interface guarantees steering, resume, fork, compaction or effect
settlement without a pinned public source. No provider, model, network or paid route call is
authorized. Do not decide an Owner question recorded in D-021, D-023 or D-024.

## Inputs to read

None. This handoff is self-contained; the rescope and prior conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Per-harness delegation surface map

1. For each named harness — Codex App Server, Claude Code, Cursor, Gemini/Google CLI, Grok Build,
   Hermes, OpenCode, Antigravity, and Pi — what documented programmatic, CLI, ACP or headless
   surfaces exist for (a) submitting a request, (b) steering or queuing a running request,
   (c) interrupt, cancel or stop, (d) resume, fork or rewind, and (e) observing completion,
   usage and evidence, and which of those are `unknown` from public sources?
2. Which surfaces genuinely require the harness to hold the credential itself (delegation) versus
   a surface that expects the caller to supply a token or key (intermediation), and what is the
   documented boundary?
3. Where a harness exposes both a local authenticated CLI and a hosted API, what is documented
   about which path Recursion would drive, and where is the choice Owner-gated or counsel-gated?

### Capability and loss taxonomy

4. What is a capability/loss taxonomy for cross-harness delegation that separates: continuity of
   authority; continuity of context or working state; continuity of evidence and accounting;
   capability present, degraded, or lost; and recoverable versus unrecoverable transitions?
5. Exactly where is continuity genuinely lost across a harness change — for example pending
   in-memory questions, unpersisted queue state, native compaction that discards a source
   boundary, fork that duplicates or diverges authority, session loss, or usage counters that
   exclude helpers — and what public source documents each loss?
6. How should a delegation record distinguish source-documented capability, locally observed
   behavior and `unknown`, so that a loss is never silently smoothed away by a summary?

### Delegation without intermediation

7. What is a delegation-without-intermediation design that keeps canonical authority, evidence
   and the non-droppable control kernel outside every upstream session, while upstream sessions
   remain acceleration state and never the sole copy of owner intent?
8. How does the design route a request to a user-authenticated local harness, hand off the
   minimum control kernel, rehydrate authorized artifacts, detect native compaction, and re-check
   authority before any effect, without Recursion seeing the credential?
9. What is the smallest Honest Accounting record — attempts, completions, interruptions,
   excluded helpers, unknown counters — that a delegated route must return, and how are missing
   counters recorded as `unknown` rather than zero?
10. What competing designs exist (native-only, single-harness, credential-intermediating router)
    and what decisive falsifier would reject the delegation design?

### Falsifiable productive-continuity experiment

11. What is a falsifiable experiment that switches an in-flight, currently authorized task from
    harness A to harness B across compaction, a source fork and a simulated lost machine, and
    measures authority preservation, evidence preservation and honest accounting against a
    strong single-harness baseline?
12. What are the measurable endpoints, the confounders, the hard floors (authority, safety,
    privacy, correctness, reproducibility) checked before any quality or cost trade-off, and the
    stop conditions that falsify productive continuity?

## Deliverable

A source-pinned report containing: a per-harness delegation surface map whose cells are
source-documented, inferred or `unknown`; a capability/loss taxonomy that names each
genuinely-lost transition and its source; a delegation-without-intermediation design that keeps
Recursion from holding or relaying credentials; a minimal Honest Accounting record; and a
falsifiable productive-continuity experiment with endpoints, confounders, hard floors and stop
conditions. Each recommendation names at least one competing option, a decisive falsifier and
what it does not prove. No vendor, transport or protocol is selected.

## Non-goals

- No selection of a language, store, framework, protocol, transport or vendor.
- No provider, model, network, login or paid route call; no OAuth or token capture.
- No credential collected, displayed, copied, relayed or persisted.
- No claim that any harness guarantees steering, resume, fork, compaction or effect settlement
  without a pinned public source.
- No harness run, adapter implemented or continuity experiment executed by this session.
- No legal conclusion about provider terms (that belongs to R-C and counsel).
- No reopening of D-021, D-023 or D-024.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- Every named harness has a delegation surface map, with each cell source-documented, inferred or
  explicitly `unknown`.
- The delegation/intermediation boundary is stated per harness from public sources.
- The capability/loss taxonomy names each genuinely-lost transition and its source.
- The delegation design keeps canonical authority, evidence and the control kernel outside every
  upstream session and never exposes a credential to Recursion.
- Missing usage or accounting is recorded as `unknown`, never zero.
- The continuity experiment is falsifiable with endpoints, confounders, hard floors and stop
  conditions, and names a strong baseline.
- Every recommendation names a competing option and what it does not prove.
- Protected paths are untouched; privacy and secret scan are clean.

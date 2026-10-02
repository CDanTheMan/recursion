---
title: R-F — Harness-native headless delegation and high-volume fan-out
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-F — Harness-native headless delegation and high-volume fan-out

This is a rescope handoff for accepted Owner decisions D-030 and D-022, with D-021 and D-023 as
constraints, and the gap register in [GAPS.md](../../research-lane/GAPS.md).

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

- D-030 accepts the delegation model: Recursion delegates through the user's own harness/CLI and
  its native headless/exec features (for example `codex exec`, `claude -p`, `cursor-agent`, ACP),
  owning the JSON stream of that output; it does not stand in for the provider. High-volume
  fan-out is authorized through the harness's own delegation features inside the user's
  subscription. D-030 is accepted subject to counsel and carries the falsifier that counsel finds
  it indistinguishable from credential intermediation on a required route, or a harness forbids
  third-party drivers.
- Locked delegation meaning for this lane: Recursion is a **caller** of the user's installed,
  user-authenticated CLI/headless tool and parses that tool's own stdout/JSON; it never proxies
  the provider API and never holds credentials. This is the operating definition the research must
  assume and test, not an open question.
- D-021 accepts delegation over credential intermediation and states that third-party credential
  intermediation is the specific thing provider terms restrict; per-route terms and automation
  limits remain counsel-gated (G-32 / D-027 / R-H).
- D-023 qualifies Codex App Server end-to-end first (steering, correlated approvals/questions,
  resume, compaction, review) as the strongest structured interface; all other harnesses ship as
  plugins, with a second deliberately different adapter as an architecture stress test.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — **Aggressive / Full / Lazy** — plus `checkpoint`, `interrupt` and `drain`. A
  source interrupt, socket close or killed PID is not external rollback. Every fan-out design must
  express spawn, steer, interrupt and settle in this vocabulary.
- D-024 makes productive continuity the headline measurable differentiator: a currently authorized
  task survives a harness change, compaction, a source fork or a lost machine while preserving
  authority, evidence and honest accounting.
- Named harnesses whose headless/exec surfaces are in scope: Codex (exec / app server), Claude
  Code (`claude -p`, Agent SDK), Cursor (`cursor-agent`), Gemini CLI, Grok Build, Hermes, OpenCode,
  Antigravity and Pi. Interface facts are mutable and must be re-pinned with retrieval dates.
- Evidence status: no cross-harness headless delegation or fan-out experiment has been run. Where
  a harness verb is not documented, the honest status is `unknown`, not assumed.

## Purpose

Produce the decision-ready evidence pack for harness-native headless delegation and high-volume
fan-out. The lane maps each named harness's documented headless/exec surface, locks the safe
delegation meaning (caller of the user's authenticated CLI; never a provider proxy; no credential
custody), analyzes an external session authorizing headless sub-agent spawns with authority
propagation and attenuation, assigns usage/accounting ownership, defines effect settlement, and
specifies stop/interrupt semantics in the D-022 vocabulary. It delivers a per-harness surface map,
delegation and accounting records, a fan-out design, a provider-free experiment design and
falsifiers. It does not select a language, store, framework, protocol or vendor, and it runs no
harness and calls no provider.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, store, framework, protocol, transport or vendor as a product default.** No credential is
collected, displayed, copied or relayed; no OAuth or token capture is designed; no login is
performed; no provider, model, network or paid route call is authorized. Do not claim any harness
guarantees steering, fan-out, resume, forking, compaction or effect settlement without a pinned
public source. Do not decide an Owner question recorded in D-021, D-022, D-023, D-024 or D-030.
Treat ACP, `codex exec`, the Codex App Server, `claude -p`, the Agent SDK and `cursor-agent` as
prior art to be cited from public sources, not as selected components.

## Inputs to read

None. This handoff is self-contained; the rescope and prior conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Per-harness headless/exec surface map

1. For each named harness — Codex (exec and app server), Claude Code (`claude -p` and Agent SDK),
   Cursor (`cursor-agent`), Gemini CLI, Grok Build, Hermes, OpenCode, Antigravity and Pi — what
   documented headless, exec, CLI or ACP surfaces exist for (a) submitting a request, (b) steering
   or queuing a running request, (c) interrupt, cancel or stop, (d) resume, fork or rewind, (e)
   emitting machine-readable stdout/JSON and (f) reporting usage/accounting, and which cells are
   `unknown` from public sources?
2. Which surfaces emit a documented JSON stream or structured event stream that Recursion can own
   and parse, and what is the documented schema stability, version negotiation and deprecation
   policy for each?
3. Which surfaces authenticate the user and hold the credential themselves (delegation), versus
   expecting the caller to supply a token or key (intermediation), and what is the documented
   boundary per harness?

### Safe delegation meaning and records

4. What is the precise test for "Recursion is a caller, not a proxy": which process owns the
   outbound provider connection, which process holds the credential, and what would have to be
   true for a design to cross into forbidden credential intermediation?
5. What is the minimal delegation record that names the invoked binary and version, the argument
   vector class, the inherited environment policy, the working directory and artifact scope, the
   credential owner, and the evidence class for each field?
6. What is the minimal Honest Accounting record for a delegated headless call — attempts,
   completions, interruptions, excluded helper calls, unknown counters — and how are missing
   counters recorded as `unknown` rather than zero?

### Fan-out, authority and settlement

7. For an external session (for example a Codex `/goal`) that authorizes headless sub-agent spawns
   (`codex exec`, `claude -p`, `cursor-agent`, ACP): how is authority propagated to each child, how
   is it attenuated so a child can never widen the parent goal, and how are capability, budget,
   egress and privacy bounds inherited or narrowed?
8. Who owns usage and accounting for a fan-out — the parent session, the child harness
   invocation, or the user's subscription — and how is per-child consumption attributed when a
   harness excludes helper calls from its counters or reports nothing?
9. What is effect settlement for fan-out: at what points are effects committed, how are partial or
   concurrent effects reconciled, and what makes a duplicate or lost spawn detectable rather than
   silently double-counted or dropped?
10. How do the D-022 vocabulary and Stop modes (Aggressive / Full / Lazy) plus `checkpoint`,
    `interrupt` and `drain` apply to a live fan-out — how are in-flight children checkpointed,
    interrupted and drained, and why is a killed child PID not external rollback?

### Convergence, experiment and falsifiers

11. How does fan-out converge or fan-in — result aggregation, conflict resolution, cancellation of
    redundant children, and bounded parallelism under quota and rate limits — without creating a
    second canonical authority?
12. What competing fan-out designs exist (single sequential delegate, harness-native fan-out,
    Recursion-orchestrated parallel spawns, queue-only) and what decisive falsifier rejects each?
13. What is a provider-free experiment design that exercises delegation and fan-out with synthetic
    fixtures and a stub harness (deterministic stdout/JSON, scripted delays, induced interrupts and
    failures) to test authority attenuation, accounting attribution, settlement and D-022 stop
    semantics, with endpoints, confounders, hard floors and stop conditions?

## Deliverable

A source-pinned report containing: a per-harness headless/exec surface map whose every cell is
source-documented, inferred or `unknown`; the locked caller-not-proxy test and a delegation
record; a minimal Honest Accounting record that uses `unknown` for unavailable counters; a
fan-out design covering authority propagation and attenuation, usage/accounting ownership, effect
settlement and D-022 stop/interrupt semantics; a convergence/fan-in design; and a provider-free,
deterministic experiment design with a stub harness, endpoints, confounders, hard floors, stop
conditions and decisive falsifiers. Each recommendation names at least one competing option, a
decisive falsifier and what it does not prove. No language, store, framework, protocol or vendor
is selected.

## Non-goals

- No selection of a language, store, framework, protocol, transport or vendor.
- No provider, model, network, login or paid route call; no quota consumed.
- No credential collected, displayed, copied, relayed or persisted; no OAuth or token capture.
- No claim that any harness guarantees steering, fan-out, resume, fork, compaction or settlement
  without a pinned public source.
- No harness executed, adapter implemented or fan-out experiment run by this session.
- No legal conclusion about whether calling a CLI is distinguishable from credentialed
  intermediation (that belongs to R-H and counsel).
- No reopening of D-021, D-022, D-023, D-024 or D-030.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- Every named harness has a headless/exec surface map with each cell source-documented, inferred
  or explicitly `unknown`.
- The caller-not-proxy test is stated so that ownership of the connection and the credential is
  unambiguous per harness.
- The delegation record and the Honest Accounting record are defined, and unavailable counters are
  `unknown`, never zero.
- The fan-out design states authority propagation and attenuation, usage/accounting ownership,
  effect settlement, and convergence/fan-in without creating a second canonical authority.
- Stop and interrupt semantics use the D-022 vocabulary (Aggressive / Full / Lazy, `checkpoint`,
  `interrupt`, `drain`), and no killed PID is described as external rollback.
- The experiment is provider-free and deterministic, with a stub harness, endpoints, confounders,
  hard floors, stop conditions and falsifiers.
- Every recommendation names a competing option and what it does not prove.
- Protected paths are untouched; privacy and secret scan are clean.

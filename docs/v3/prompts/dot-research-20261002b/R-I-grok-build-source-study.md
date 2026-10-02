---
title: R-I — Open-source Grok Build source study
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-I — Open-source Grok Build source study

This is a source-study handoff for accepted Owner decisions D-018, D-019, D-023, D-024 and D-033,
with D-022 as a constraint, and the gap register in [GAPS.md](../../research-lane/GAPS.md). It
builds directly on [R-G](R-G-plugin-import-and-cross-harness-reuse.md), the plugin import and
cross-harness reuse handoff, and must extend rather than restate it.

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

- D-018 repositions Recursion as both a first-class native harness and a first-class unifying
  wrapper over the wider harness ecosystem, whose purpose is to remove lock-in and cut quota/usage
  burn, with no ecosystem lock-in; adapter and porting work is a first-class path, and release of
  any credential-reliant route stays counsel-gated (G-32).
- D-019 builds the comprehensive capability and plugin surface but ships every capability as an
  opt-in plugin or profile rather than a default; a large fraction of that surface is
  port/optimize work ported from existing ecosystems, not new invention.
- D-033 treats "porting is cheap" strictly as a **hypothesis to validate, not assume**: porting
  savings are unmeasured, and an acceptable-port count of zero is possible. Its falsifier is that
  measured porting cost exceeds a native rewrite, or that no ecosystem imports cleanly.
- D-023 qualifies Codex App Server end-to-end first as the strongest structured interface; every
  other harness, Grok Build included, ships as a plugin, with a second deliberately different
  adapter prototyped only as an architecture stress test.
- D-024 makes productive continuity the headline measurable differentiator: a currently authorized
  task survives a harness change, compaction, a source fork or a lost machine while preserving
  authority, evidence and honest accounting.
- D-031 positions Recursion on its unrestrictive, customizable environment — one place to connect
  keys/subscriptions, routing through any harness or its own, with privacy and safety — not on a
  vendor-sabotage claim; savings are claimed only when measured.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — **Aggressive / Full / Lazy** — plus `checkpoint`, `interrupt` and `drain`. A
  source interrupt, socket close or killed PID is not external rollback.
- Study target: the open-source (Apache-2.0) Grok Build Rust codebase at
  https://github.com/xai-org/grok-build, pinned to an exact commit with a retrieval date. The
  prior register pin is `72a61251fcffb464bcc687aeb5a998e5a98ec0c9` (SOURCE-REGISTER.md SRC-V3-125);
  it is a starting baseline, not a guarantee that the upstream tree is unchanged, and every claim
  must be re-pinned.
- Prior Grok Build coverage exists as route evidence: SOURCE-REGISTER.md SRC-V3-125, SRC-V3-161,
  SRC-V3-162, SRC-V3-204 and SRC-V3-208 through SRC-V3-214; the route matrix in
  ROUTE-CAPABILITIES.md; and the current-strategy Grok Build section. Those establish behavior and
  route facts; this lane studies the source for reuse, port or avoidance, not route qualification.
- R-G is the plugin/capability-contract lane. This study must feed R-G's translation layer rather
  than duplicate it, and must respect R-G's finding that importability and porting savings are
  unproven.
- Evidence status: no Grok Build source was read by Recursion for this lane. Every reusability,
  portability and licensing statement below is to be established from pinned source, LICENSE,
  vendored notices and public documentation, or marked `unknown`.

## Purpose

Produce the decision-ready source study of the open-source Apache-2.0 Grok Build Rust codebase, so
the Owner can decide what Recursion should learn, adopt, port or avoid. The lane maps the
repository architecture, the UI/TUI interaction flow, and the extension/plugin model; establishes
the licensing and provenance position of the source and its vendored dependencies; and tests
whether the project's Rust experience bears on Recursion's open language question without
selecting a language. It delivers a source-pinned adoption/port/avoid ledger whose entries carry
competing options, decisive falsifiers and a statement of what each does not prove, plus an
explicit statement of what the study does not establish. It does not select a language, store,
framework, runtime, UI toolkit or vendor, does not qualify any route, and executes no Grok Build
binary.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, UI toolkit or vendor.** Reading an
Apache-2.0 source tree licenses study, not adoption: a permissive license does not certify quality,
stability, security, CVE-freedom or fitness, and does not grant account entitlement or route
eligibility. Do not claim any crate, protocol or pattern is reusable, portable or safe without a
pinned source locator and an evidence class. No binary is installed or run, no dependency is
fetched and executed, and no credential or account is touched. Do not decide an Owner question
recorded in D-018, D-019, D-022, D-023, D-024, D-031 or D-033. Treat the Rust crates, the
ACP/session implementation, the pager/TUI, the Agent Dashboard, worktree dispatch and the
extension hooks as prior art cited from pinned public source, not as endorsed or selected
components.

## Inputs to read

None from this repository: the rescope, R-G's contract summary and prior Grok Build route evidence
are summarized in `## Baked context` above, and no repository, connector or private-source access
is assumed. The session must, however, retrieve the public repository at
https://github.com/xai-org/grok-build pinned to one exact commit, together with its LICENSE, any
vendored notices, workspace manifests/lockfiles and the public documentation it carries; that
public source is the object of study.

## Research questions

### Repository architecture

1. For the pinned commit, what is the top-level workspace and crate layout (workspace members,
   crate boundaries, key dependencies), which crates own the agent loop, session/ACP server,
   process/terminal handling, and pager/TUI, and which cells are `unknown` from the public tree?
2. How is asynchronous execution and the runtime structured (runtime/tokio usage, task spawning,
   cancellation, channels/queues, actor or service boundaries), and which design choices are
   general Rust patterns a provider-neutral harness could reuse versus choices specific to Grok's
   product and vendor stack?
3. How does the session/ACP implementation model a turn, streaming updates, permission requests,
   questions, compaction and resume (for example the implemented `x.ai/*` extensions), and which
   of these are portable interface patterns versus Grok-specific internals that only a matching
   adapter could consume?
4. How are processes, terminals and shell/tool execution managed (spawn, attach, output capture,
   interrupts, worktrees), and where does the code draw the line between conversation continuity
   and filesystem or effect continuity? For each finding, classify it as source-documented,
   inferred or `unknown`.

### UI/TUI flow

5. How does the Agent Dashboard work as a TUI: what it shows for sessions, forks, state and
   subagents-under-parents, how navigation and scope are expressed, and why this is regarded as
   best-in-class, with source or documentation locators for each claim?
6. How are the distinct mid-turn operations implemented and surfaced — normal queueing, a
   configurable steer mode that injects at a safe gap, "send now" as cancel-and-send rather than
   active steering, peek/reply, and queue editing? What do these distinctions demonstrate about
   honest input disposition (accepted versus delivered versus adopted) that Recursion should
   preserve rather than normalize into a generic Send?
7. How is worktree dispatch presented and executed from the dashboard, and how do views being
   closed differ from session deletion? Compare the Grok Build flow with the Meta Muse Code
   interactive flow (active steer, next-turn queue, retract, interrupt) and the OpenCode flow
   (v1 and v2 steer/queue, pending cancellation, projected-history forks), naming where each
   comparison cell is source-documented, inferred or `unknown`.

### Extension and plugin model

8. What extension surfaces exist (agents, personas, subagents, skills, MCP, plugins and hooks):
   what each declares, how it is discovered and loaded, its lifecycle and permission model, and
   what its contribution points are?
9. Which of these map cleanly onto R-G's plugin/capability contract, which map only with a
   semantic translation, and which have no counterpart — and what would a Recursion translation
   layer have to add so that an imported Grok-style extension cannot widen authority, privacy,
   egress, credential visibility or billing?
10. How do hooks behave on timeout, crash or malformed output, and why can a fail-open hook not
    serve as a security or authority boundary? State what Recursion must enforce at its own
    admitted effect boundary instead, in terms that connect to D-022 stop/interrupt semantics.

### Licensing, provenance and dependency security

11. What exactly does the repository's Apache-2.0 LICENSE and any vendored notices permit and
    require for reuse (retention of notices, attribution, modification marking, patent grant,
    trademark limits), and what does a permissive source license explicitly not provide
    (account entitlement, route eligibility, service terms, warranty or security assurance)?
12. What dependency-security and provenance considerations attach to the tree: workspace
    dependency and lockfile inspection, transitive and dual licenses, vendored or encoded
    (including XOR/minified/obfuscated) artifacts, integrity metadata, update cadence and any
    documented supply-chain posture? Which of these can be checked deterministically from the
    pinned tree, and which remain `unknown` without executing anything?

### Language question, gaps and ledger

13. What does Grok Build's Rust experience demonstrate and not demonstrate about Rust as a
    candidate for Recursion's own implementation (FU-01 / DS-18) — regarding build/test
    ergonomics, async and concurrency, cross-platform Windows/Linux support at the D-028 floor,
    distribution and dependency management — stated as evidence about one project, never as a
    language selection?
14. What does this study explicitly NOT establish: no route qualification, no account or
    subscription entitlement, no UI conformance or accessibility certification, no measured
    porting cost, and no security audit. Which of these are out of scope versus merely unmeasured,
    and what would be required to establish each?
15. What competing options exist for each prospective adoption (adopt the pattern, port with an
    adapter, vendor a narrow piece, reimplement natively, or avoid), what is the decisive falsifier
    that would reject the recommendation, and what does each recommendation not prove?

## Deliverable

A source-pinned report containing: a repository architecture map (crate layout, async/runtime,
session/ACP, process/terminal) whose every cell is source-documented, inferred or `unknown`, with
each pattern labeled reusable, Grok-specific or `unknown`; a UI/TUI flow analysis of the Agent
Dashboard, steer versus queue versus "send now", peek/reply and worktree dispatch, compared against
Meta Muse Code and OpenCode with per-cell evidence classes; an extension/plugin model assessment
mapped onto R-G's contract, including an explicit statement that hooks fail open and are not a
security boundary; a licensing/provenance and dependency-security section distinguishing what
Apache-2.0 allows from what it does not, with no legal conclusion; a bounded statement of what the
project's Rust experience does and does not demonstrate about FU-01 / DS-18; an explicit gaps
section (no route qualification, no entitlement, no UI conformance); and a source-pinned
adoption/port/avoid ledger whose entries each name competing options, a decisive falsifier and what
the recommendation does not prove. "Porting is cheap" appears only as a hypothesis with a
falsifier. No language, store, framework, runtime, UI toolkit or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, UI toolkit or
  vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No UI conformance, accessibility certification or best-in-class ranking presented as measured.
- No Grok Build binary installed or run; no dependency fetched and executed; no network effect.
- No legal conclusion about license compatibility, redistribution or provider terms (that belongs
  to R-H and counsel).
- No security audit or CVE-clearance claim; unproven cells stay `unknown`.
- No assertion that porting is cheap; it remains a hypothesis with a falsifier (D-033).
- No measured porting-cost claim (that belongs to R-G's validation approach).
- No reopening of D-018, D-019, D-022, D-023, D-024, D-031 or D-033.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- Every architectural, UI, extension and licensing claim is tied to a pinned source locator and an
  evidence class (source-documented, locally observed, inferred or `unknown`).
- The repository architecture map covers crates, async/runtime, session/ACP and process/terminal
  handling, and labels each pattern reusable, Grok-specific or `unknown`.
- The UI/TUI flow covers the Agent Dashboard, steer versus queue versus "send now", peek/reply and
  worktree dispatch, and compares Grok Build against Meta Muse Code and OpenCode with per-cell
  evidence classes.
- The extension/plugin model is mapped onto R-G's contract, and hooks are explicitly treated as
  fail-open, not a security or authority boundary.
- Licensing and provenance findings state what Apache-2.0 does and does not permit, and
  dependency-security and provenance considerations are addressed without executing code or making
  a legal conclusion.
- The Rust question is treated strictly as evidence about one project for FU-01 / DS-18 — a
  candidate, never a selection — with what it demonstrates and does not.
- The study explicitly states what it does not establish: no route qualification, no entitlement,
  no UI conformance, no measured porting cost.
- The deliverable is a source-pinned adoption/port/avoid ledger in which each recommendation names
  a competing option, a decisive falsifier and what it does not prove; no language, store,
  framework, runtime, UI toolkit or vendor is selected.
- Protected paths are untouched; privacy and secret scan are clean.

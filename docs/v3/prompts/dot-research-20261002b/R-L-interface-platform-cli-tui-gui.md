---
title: R-L — Unified interface platform: one command-and-query model for CLI, TUI and GUI
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-L — Unified interface platform: one command-and-query model for CLI, TUI and GUI

This is an interface-platform handoff for accepted Owner decisions D-018, D-019, D-022, D-024
and D-031, with D-021 and D-033 as constraints, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-K](R-K-terminal-multiplexer-and-tui.md), the terminal multiplexer and transformative-TUI
handoff, and on [R-J](R-J-multi-agent-terminal-communication.md), the terminal multi-agent
interaction handoff, and must extend rather than restate them: R-K designs the multiplexer
substrate and the TUI on top of it, while R-L designs the **shared platform** every surface is a
client of. It consumes the already accepted direction in
[INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md), [TERMINAL-RUNTIME.md](../../TERMINAL-RUNTIME.md),
[CLI.md](../../CLI.md), [M1B-WIRE-PROFILE.md](../../M1B-WIRE-PROFILE.md) and
[PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md); it must not reopen their requirements.

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

- The exact thing to design: a **unified interface platform** — one versioned
  command-and-query model shared by the scriptable CLI, the interactive TUI and, later, the
  graphical client, so that a command or query has one meaning and one admission path on
  every surface. There are no divergent semantics between surfaces; a surface may present
  something differently, but it may not define a competing meaning.
- D-018 makes Recursion a first-class native harness and a first-class unifying wrapper over
  the wider harness ecosystem, whose purpose is to remove lock-in and cut quota/usage burn,
  with no ecosystem lock-in; the platform model must therefore be broker-neutral,
  route-neutral and renderer-neutral, not tied to one vendor's UI, transport or runtime.
- D-019 builds the comprehensive capability and plugin surface but ships every capability as an
  opt-in plugin or profile rather than a default; plugin-contributed views and commands may not
  appear, activate or spend by default, and opening, attaching or splitting a view must add no
  inference, indexing or plugin activation.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — **Aggressive / Full / Lazy** — plus `checkpoint`, `interrupt` and `drain`.
  The interface platform exposes exactly that vocabulary. A source interrupt, socket close or
  killed PID is not external rollback; closing a view or client is a detach, not a Stop, and
  must never be read as one.
- D-024 makes productive continuity the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting. The platform must present continuity
  state truthfully as facts — saved-locally versus accepted versus delivered/applied versus
  observed versus settled/unresolved — never as one optimistic badge, and a replay gap as a
  marker rather than an invented story.
- D-031 forbids a vendor-sabotage claim: no interface or platform wording may assert that
  vendors deliberately unoptimize quota, and no savings claim may be made without measurement.
- The backend services the interface depends on are already partially specified and this lane
  must define their **shared contract**, not re-invent them per surface: query projections over
  canonical records; event streaming with monotonic cursors, bounded credit and an explicit
  `RESET`/`GAP` resync; deterministic zero-model status; configuration resolution with effective
  value and provenance; and plugin-contributed views and commands with declared component and
  version.
- Already accepted wire direction from [M1B-WIRE-PROFILE.md](../../M1B-WIRE-PROFILE.md): the
  HELLO / WELCOME / SNAPSHOT / EVENT / ACK / CREDIT / INPUT / RESIZE / RESET messages; a cursor
  unit of `utf8-byte` or `event`; a replay floor and snapshot cursor; a `replay-gap` that
  requires RESET before any further same-stream message; credit bounded at 16,777,216 bytes and
  65,536 events; queue limits; lease values as opaque references; and refusal reasons including
  `replay-gap-continuation`, `credit-exhausted`, `stale-lease` and `passive-client-input`.
- Already accepted performance direction from [PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md):
  `PERF-010` uses 0, 1, 5, 10 and 20 passive views under idle and high-output loads and fails if
  views multiply model/worker calls, block canonical writes, cause unbounded memory, corrupt
  input, lose durable events or turn detach/reconnect into relaunch; it records p50/p95/p99 input
  and frame latency, CPU, RSS, wakeups, IPC bytes, queue high-water marks, coalesced presentation
  frames, process/handle counts and canonical append delay. The optimisation decision rule is
  `OR-024` in [DECISION-REGISTER.md](../../DECISION-REGISTER.md): responsiveness, subscription
  efficiency, then completion, subject to correctness, authorization, resource limits and
  recoverability, with full-vector reporting and no hidden scalar weights.
- Already accepted interface direction from [INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md):
  the interactive TUI owns live conversation, focused work views, keyboard-first
  steering/queueing, an attention inbox, split/attached views, task switching and compact
  inspect panels, and must not own actor/process lifetime, invoke a hidden model on attach or
  repaint the full log on every token; the five primary destinations are Work, Attention,
  Artifacts, Environment and Settings/recovery, with a command palette; the later GUI is a
  client of the same versioned observer/control protocols, not a rewrite of runtime state or
  actor semantics ([TERMINAL-RUNTIME.md](../../TERMINAL-RUNTIME.md)).
- Already accepted configuration direction from [CLI.md](../../CLI.md): one versioned
  configuration schema drives file, CLI and transport editors; a deterministic semantic
  validator resolves scope and emits effective value plus provenance for every field; edits carry
  expected current version/digest and fail stale rather than last-write-wins; canonical
  serialization (for example JSON Schema 2020-12 plus RFC 8785 canonical JSON) precedes
  digest/signature comparison; the TUI renders from the same schema and interactive editing never
  makes widget state canonical. The interface platform must unify this across all surfaces.
- Open gap this lane addresses: **G-09** in [GAPS.md](../../research-lane/GAPS.md) — the
  configuration architecture is frozen in design but has no cross-platform conformance corpus,
  no chosen human syntax and no agreed authority lattices for privacy exposure and publication.
  R-L must specify the conformance-corpus shape and the platform contract that consumes it; it
  must not select a syntax as a product decision.
- Integration surface named by the strategy and this lane: shell integration, editors
  (Neovim, VS Code), multiplexers (tmux, Zellij), OSC/shell integration, MCP, and notifications.
  Each is an adapter or client of the shared protocol; none may own authority or actor lifetime.
- Evidence status: no unified interface platform, configuration-conformance corpus, GUI or
  multi-surface session has been implemented or measured by Recursion for this lane. Every
  usability, differentiation, cost, latency, accessibility and performance statement below is to
  be established from public source, product documentation and a synthetic provider-free fixture,
  or marked `unknown`.

## Purpose

Produce the decision-ready **unified interface platform specification candidate** for Recursion.
The lane fixes one versioned command-and-query model shared by CLI, TUI and later GUI with no
divergent semantics; defines the backend services the platform depends on (query projections,
event streaming with monotonic cursors and bounded credit plus `RESET`/`GAP`, deterministic
zero-model status, configuration resolution, and plugin-contributed views and commands); states
the interface performance budgets per lifecycle phase (startup, idle, first-use, steady state and
recovery), frame and input latency, throughput under high output, resize behaviour and the
`PERF-010` 0/1/5/10/20-view matrix; specifies configurability (themes, keybindings, layouts,
profiles, human-readable plus machine-readable config, inspect/preview/apply/rollback and the
G-09 configuration conformance corpus); and fixes the integration contract for shell, editors,
multiplexers, OSC/shell integration, MCP and notifications, with the invariant that views never
own authority or actor lifetime. It delivers a spec candidate with competing options, decisive
falsifiers and an explicit statement of what it does not prove. It does not select a language,
store, framework, transport, UI toolkit, renderer, configuration syntax or vendor, does not
qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, UI toolkit, transport, renderer,
multiplexer, wire encoding, configuration syntax or vendor.** Do not decide an Owner question
recorded in D-018, D-019, D-021, D-022, D-024 or D-033. No provider, model or account call is
made; no credential or account is touched. Do not claim that a view, tab, command, plugin
contribution, layout or window geometry confers authority, owns an actor or owns process
lifetime. Do not assert that a unified model, a cache or "more surfaces" improves performance;
that is a hypothesis with a falsifier. Closing a view or client is a detach, never a Stop, and no
surface may widen credential visibility (D-021). No claim of measured platform superiority,
entitlement or UI conformance is authorized.

## Inputs to read

None from this repository: the rescope, the accepted terminal, interface, CLI, wire and
performance requirements and the `G-09`/`OR-024` context are summarized in `## Baked context`
above, and no repository, connector or private-source access is assumed. The session must,
however, retrieve the public standards and product documentation it cites — JSON Schema
2020-12, RFC 8785 canonical JSON, the WCAG 2.2 recommendation, the OpenAPI or equivalent
interface-description specifications it proposes to adopt, the tmux and Zellij documentation, the
Neovim API and VS Code extension APIs, the OSC 0/1/2/9/99/777 terminal-notification sequences,
the Model Context Protocol specification, and the public Claude Code plugin and mods
documentation that [R-M](R-M-claude-code-terminal-modding.md) pins — and pin each claim to a URL
and retrieval date.

## Research questions

### One versioned command-and-query model

1. How is a single command-and-query model defined so the CLI, TUI and later GUI share it with
   no divergent semantics: a versioned command schema, a query/projection schema, typed errors
   with code/precondition/effect-attempted/retryability, idempotent receipts with command IDs,
   explicit capability negotiation, and a mapping for arguments and results that cannot drift
   between surfaces?
2. How are deterministic, zero-model status and query projections defined (current goal,
   authority epoch, pending questions/approvals, queue state, budget, route, configuration) so
   that any surface can ask them without a model call and receive the same typed answer, and so
   that `unknown` stays distinct from zero?
3. How are plugin-contributed views and commands namespaced, versioned and capability-scoped so
   that a contribution declares its supplying component and version, cannot collide with a
   reserved command, cannot acquire authority from origin, and cannot act while disabled (D-019)?
4. How does the shared event streaming contract compose across surfaces: monotonic per-stream
   cursors, bounded credit, a replay floor and snapshot cursor, explicit `RESET`/`GAP` resync,
   and the non-droppable event classes (command, lease, process-exit, termination and canonical
   state) versus coalescible presentation frames — with the canonical append before any
   coalescing or drop?
5. How is configuration resolution shared across surfaces: the same versioned schema,
   effective value plus provenance for every field, lifecycle classification
   (`live`/`checkpoint-applied`/`restart-required`/new GoalSpec), before/after diff, and stale
   concurrent edits rejected as a typed conflict rather than last-write-wins?

### Performance budgets and regimes

6. What per-phase budgets should the interface carry — startup, idle, first-use, steady state
   and recovery — and how is each expressed so an idle surface (and an idle platform) provably
   performs no model call, no indexing and no plugin activation?
7. What frame and input latency budgets (p50/p95/p99), throughput-under-high-output budget,
   resize-storm behaviour and coalescing-versus-drop rules should the platform require, and how
   are they tied to the `PERF-010` 0/1/5/10/20-view matrix under idle and high-output regimes
   without a hidden scalar score?
8. What instrumentation, workload identity and freeze rules make a platform performance claim
   reproducible (OS, terminal, event rate, render workload, view count, configuration revision),
   and what exact observation falsifies a claimed budget?

### Configurability

9. How are themes, keybindings, layouts and profiles represented as configuration rather than
   code, and how are human-readable and machine-readable forms kept one deterministic compiled
   representation with a canonical serialization and digest (competing syntax options compared,
   none selected)?
10. What inspect/preview/apply/rollback contract does the platform expose, including affected
    actors, provenance, validation, application boundary and a reversible diff, and how do
    concurrent terminal/editor/CLI edits remain consistent?
11. What is the shape of the **G-09 configuration conformance corpus** — the cross-platform
    fixtures that must pass before the resolver is testable: round-trip, duplicate-key, type,
    normalization, invalid-combination classes, scope-subset proofs, migration/rollback, and a
    reported complexity vector — and which cells remain `unknown` without measurement?

### Integration

12. What integration contract do shell, editors (Neovim, VS Code), multiplexers (tmux, Zellij),
    OSC/shell integration, MCP and notifications share, such that each is a replaceable adapter
    or client of the shared protocol, none is mandatory, and none owns authority or actor
    lifetime?
13. How do OSC-based notifications, titles and shell integration remain safe (allowlisted
    sequences, no terminal-state corruption, no clipboard or credential exposure), and how do
    editor and MCP integrations map typed commands without smuggling in a second admission path?
14. How does the platform keep a slow, absent or hostile client from blocking canonical append,
    Stop or recovery, and how does every surface preserve the one pause/stop vocabulary
    (Aggressive/Full/Lazy plus `checkpoint`/`interrupt`/`drain`) with its scope visible?

### Open choices, differentiation and falsifiers

15. Which platform shapes are the live competing options to compare without selecting: an
    in-process library model, a daemon protocol with thin clients, or a hybrid; push versus pull
    query projections; one configuration document versus separated presentation-only
    configuration — and what is the decisive falsifier and non-proof for each?
16. What would falsify the headline claim of "one meaning on every surface" — for example a
    command that cannot be expressed identically, a projection that requires a surface-specific
    field, or a plugin view that can only work by bypassing admission — and what does this
    platform candidate explicitly not prove (no measured performance, no accessibility
    conformance, no security boundary between views, no porting cost, no route qualification)?
17. What provider-free acceptance fixtures accept or reject the model: identical query results
    across surfaces, a plugin-contributed view/command that cannot activate while disabled, a
    stale configuration edit rejection, a `RESET`/`GAP` resync, an OSC allowlist violation, and
    an N-view soak at 0/1/5/10/20 views — with an exact pass/fail predicate for each?

## Deliverable

A unified interface platform specification candidate containing: a **command-and-query model**
section defining the one versioned schema, typed errors, idempotent receipts, capability
negotiation and projection schema shared by CLI, TUI and GUI with no divergent semantics; a
**backend services** section defining query projections, event streaming (monotonic cursors plus
bounded credit and `RESET`/`GAP`), deterministic zero-model status, configuration resolution and
plugin-contributed views/commands, each with its authority boundary; a **performance budgets**
section with per-phase budgets (startup/idle/first-use/steady/recovery), p50/p95/p99 frame and
input latency, high-output throughput, resize behaviour and the `PERF-010` 0/1/5/10/20-view
matrix, plus freeze rules and an `unknown-until-measured` disposition; a **config schema shape**
section covering themes, keybindings, layouts and profiles, human and machine forms, canonical
serialization, inspect/preview/apply/rollback and the G-09 configuration conformance corpus; an
**integration contract** section for shell, editors, multiplexers, OSC/shell integration, MCP and
notifications; a **competing options** section comparing platform shapes without selecting one;
and a provider-free fixture suite. Every recommendation names a competing option, a decisive
falsifier and what it does not prove. No language, store, framework, runtime, transport, UI
toolkit, renderer, configuration syntax or vendor is selected, and views never own authority or
actor lifetime.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, transport, UI
  toolkit, renderer, multiplexer, wire encoding, configuration syntax or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that a view, command, plugin contribution, layout or window geometry confers
  authority or owns an actor; closing a view or client is a detach, never a Stop.
- No claim that a unified model, a cache or "more surfaces" improves performance without
  measurement; each such claim carries a competing option and a falsifier.
- No provider, model, credential or account call; no binary installed or run; every fixture is
  synthetic and provider-free.
- No assertion that porting an existing interface, plugin or CLI is cheap; it remains a
  hypothesis with a falsifier (D-033).
- No new executive tier, no separate AI "ARM manager", and no second portfolio executive created
  by a surface, command or view.
- No reopening of D-018, D-019, D-021, D-022, D-024 or D-033, and no reopening of the accepted
  requirements in `INTERFACE-STRATEGY.md`, `TERMINAL-RUNTIME.md`, `CLI.md`,
  `M1B-WIRE-PROFILE.md` or `PERFORMANCE-PLAN.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The command-and-query model defines one versioned schema, typed errors, idempotent receipts and
  capability negotiation shared by CLI, TUI and later GUI, with an explicit demonstration that no
  surface introduces a divergent meaning or a second admission path.
- The backend services section defines query projections, event streaming with monotonic cursors
  and bounded credit plus `RESET`/`GAP`, deterministic zero-model status, configuration
  resolution with provenance, and plugin-contributed views/commands — each with a stated
  authority boundary, and the canonical append precedes any coalescing or drop.
- The performance section states per-phase budgets (startup, idle, first-use, steady, recovery),
  p50/p95/p99 frame and input latency, throughput under high output, resize behaviour and the
  `PERF-010` 0/1/5/10/20-view matrix, with freeze rules and `unknown-until-measured` cells rather
  than invented numbers, and no single scalar score.
- The configurability section covers themes, keybindings, layouts and profiles, human-readable
  and machine-readable forms with one canonical compiled representation, inspect/preview/apply/
  rollback, stale-edit rejection and the G-09 configuration conformance-corpus shape; no syntax
  is selected.
- The integration section fixes a contract for shell, editors (Neovim, VS Code), multiplexers
  (tmux, Zellij), OSC/shell integration, MCP and notifications in which each is a replaceable
  adapter/client and none owns authority or actor lifetime, and no view widens credential
  visibility (D-021).
- The open-decision section compares platform shapes (in-process library, daemon protocol,
  hybrid; push/pull projections; unified/split configuration) with a competing option, decisive
  falsifier and non-proof for each, and selects none of them.
- The provider-free fixture suite specifies pass/fail predicates for cross-surface query
  equality, disabled-plugin inertness, stale-configuration rejection, `RESET`/`GAP` resync, an
  OSC-allowlist violation and the 0/1/5/10/20-view soak, and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, framework, runtime, transport, UI toolkit, renderer, configuration syntax
  or vendor is selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured performance advantage,
  no accessibility conformance, no route qualification, no entitlement, no security boundary
  between views and no measured porting cost.
- Protected paths are untouched; privacy and secret scan are clean.

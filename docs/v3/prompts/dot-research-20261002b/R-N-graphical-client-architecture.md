---
title: R-N — Graphical client architecture over the same command-and-query model
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-N — Graphical client architecture over the same command-and-query model

This is a graphical-client handoff for accepted Owner decisions D-018, D-019, D-022, D-024 and
D-031, with D-021 and D-033 as constraints, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It designs the **later graphical client** as a new client
of the same versioned observer/control protocols, and it builds directly on
[R-L](R-L-interface-platform-cli-tui-gui.md), the unified interface platform, and
[R-K](R-K-terminal-multiplexer-and-tui.md), the terminal multiplexer and transformative TUI. It
consumes the already accepted direction in
[INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md), [TERMINAL-RUNTIME.md](../../TERMINAL-RUNTIME.md),
[CLI.md](../../CLI.md) and [PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md); it must not reopen
their requirements.

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

- The exact thing to design: the **later graphical client** for Recursion — a desktop or rich
  client that reuses the same command-and-query model and the same presentation projections as
  the CLI and TUI, and adds spatial project/session navigation, artifact and diff review,
  visually clear lineage, context comparison, richer provenance inspection and accessible
  responsive views.
- D-019 builds the graphical client but ships it as an **opt-in** capability, not a default and
  not a mandatory always-on dashboard; the terminal remains the first surface. Nothing in this
  lane may make the GUI a prerequisite for core workflows or for v3 release.
- D-018 requires no ecosystem lock-in: the graphical client must be a replaceable presentation
  client, not a new source of truth, and must not bind Recursion's semantics, storage or
  transport to one platform, toolkit or vendor.
- D-022 fixes one pause/stop vocabulary (Aggressive/Full/Lazy plus
  `checkpoint`/`interrupt`/`drain`); the graphical client shows the same vocabulary, its scope
  and its boundary, and closing a window or detaching a client is a detach, never a Stop.
- D-024 makes productive continuity the headline measurable differentiator: the graphical client
  must present continuity state truthfully as facts — saved-locally versus accepted versus
  delivered/applied versus observed versus settled/unresolved — never as one optimistic badge,
  and must show a replay gap as a marker rather than an invented story.
- D-031 forbids a vendor-sabotage claim and any unmeasured savings claim; visual polish is never
  a performance or efficiency claim.
- Already accepted interface direction from [INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md):
  the later GUI owns spatial navigation, artifact/diff review, lineage, context comparison,
  richer provenance and accessible responsive views, and must not own different command meanings,
  must not bypass the common admission path and must not be a mandatory always-on dashboard.
- Already accepted runtime direction from [TERMINAL-RUNTIME.md](../../TERMINAL-RUNTIME.md): a
  later graphical frontend is a **new client of the same versioned observer/control protocols**,
  not a rewrite of runtime state or actor semantics; views are projections, not process owners;
  attaching a view must not launch another model or indexer; daemon/broker owns actor/process
  lifetime and canonical state.
- Already accepted model from [R-L](R-L-interface-platform-cli-tui-gui.md) and the wire profile
  in [M1B-WIRE-PROFILE.md](../../M1B-WIRE-PROFILE.md): one versioned command-and-query model,
  typed commands with idempotent receipts, monotonic per-stream cursors with bounded credit and
  `RESET`/`GAP` resync, deterministic zero-model status, configuration resolution with
  provenance, and plugin-contributed views/commands — all of which the GUI reuses unchanged.
- Already accepted performance direction from [PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md):
  `PERF-010` fixes the 0/1/5/10/20-view matrix under idle and high-output loads and forbids view
  cost from multiplying model/worker calls, blocking canonical writes, causing unbounded memory,
  corrupting input, losing durable events or turning detach/reconnect into relaunch; `OR-024`
  ranks responsiveness, subscription efficiency then completion with full-vector reporting and no
  hidden scalar score. The GUI adds frame rate, input latency, GPU and idle budgets that must be
  measured, not asserted.
- Requirement to state explicitly: a graphical client introduces desktop concerns absent from the
  terminal — rendering pipelines, GPU/driver variability, windowing and composition, DPI and
  scaling, input-method editors, animation and reduced-motion, offline/cached read views and OS
  accessibility bridges — each of which must be a budgeted, falsifiable requirement rather than
  a visual preference.
- Accessibility target set by this lane: **WCAG 2.2 Level AA** as the acceptance target, with
  keyboard-complete operation, visible focus, logical traversal, focus restoration, semantic
  status announcements, non-color-only encoding and reduced-motion support, all verified against
  the normative success criteria rather than a framework's claims.
- Offline and cached read views are permitted only with honesty: a cached projection shows its
  "last synchronized" boundary, a stale or disconnected state is visible, no cached read view
  grants control authority, and a gap is shown as a gap. Typed commands remain the only mutation
  path and require current authority.
- Security boundary: the graphical client has **no direct canonical-state authority**; it holds no
  credential custody and cannot widen credential visibility (D-021); it sends typed commands
  through the common admission path and receives authorized projections. A window, tab or local
  cache must never become a second writer or an authority source.
- Migration path: the GUI must be reachable as an incremental extension of the TUI's
  command-and-query usage, so existing TUI/CLI workflows, keybindings and layouts inform the GUI
  and a user can move between surfaces without relearning command meanings.
- Evidence status: no graphical client, rendering pipeline, accessibility conformance run or
  GUI performance measurement exists for Recursion. Every stack comparison, budget and
  accessibility statement below is to be established from public standards and product
  documentation, or marked `unknown`.

## Purpose

Produce the decision-ready **graphical client architecture candidate** for Recursion. The lane
states the requirements the GUI must satisfy; compares candidate stacks in a
**framework-agnostic** way (rendering model, accessibility bridge, platform reach, packaging,
idle and frame cost, offline behavior, testability) **without selecting one**; mandates reuse of
the same command-and-query model and projections with no divergent semantics; fixes an
accessibility contract at WCAG 2.2 AA; sets rendering, performance and idle budgets and a
provider-free measurement plan; defines offline/cached read views with "last synchronized"
honesty; defines detach/attach and the security boundary (typed commands only, no direct
canonical-state authority); and describes the migration path from the TUI. It delivers a
candidate with competing options, decisive falsifiers and an explicit statement of what it does
not prove. It does not select a language, UI framework, renderer, transport, store or vendor, does
not qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, UI toolkit, renderer, transport,
wire encoding or vendor.** Do not decide an Owner question recorded in D-018, D-019, D-021,
D-022, D-024 or D-033. No provider, model or account call is made; no credential or account is
touched. Do not claim that a window, panel, canvas, gesture or layout confers authority, owns an
actor or owns process lifetime; closing a window or detaching a client is a detach, never a Stop.
Do not assert that a graphical client, GPU rendering or animation improves performance,
productivity or accessibility without measurement; each is a hypothesis with a falsifier. No
claim of measured performance, entitlement, UI conformance, accessibility conformance or
security boundary between views is authorized.

## Inputs to read

None from this repository: the rescope, the accepted interface, terminal, CLI, wire and
performance requirements and the D-018/D-019/D-021/D-022/D-024/D-031 context are summarized in
`## Baked context` above, and no repository, connector or private-source access is assumed. The
session must, however, retrieve the public standards and product documentation it cites — the
WCAG 2.2 recommendation and its understanding documents, the platform accessibility APIs it
compares (for example the Microsoft UI Automation, Apple accessibility and Linux AT-SPI surfaces),
the relevant graphics and windowing API documentation, the reduced-motion and color-contrast
guidance it uses, and any interface-description or offline-sync specifications it proposes — and
pin each claim to a URL and retrieval date.

## Research questions

### Requirements and reuse of the common model

1. What is the complete requirement set for a Recursion graphical client: spatial
   project/session navigation, artifact and diff review, lineage and context comparison, richer
   provenance inspection, accessible responsive views, and truthful continuity/authority state —
   each traced to an accepted Owner decision or an accepted interface requirement?
2. How does the GUI reuse the R-L command-and-query model and presentation projections
   unchanged, so that a command or query has one meaning across CLI, TUI and GUI; which
   view-model operations are pure projections and which are typed commands; and what would
   falsify the claim of no divergent semantics?
3. How does the GUI keep the one pause/stop vocabulary, show scope and boundary, and treat
   window close or client detach as a detach rather than a Stop (D-022)?

### Candidate stacks, framework-agnostic

4. Which candidate approaches exist for a rich client — web/Electron-style, web-in-native-shell,
   native toolkit, declarative retained-mode, immediate-mode, or a browser-hosted client — and
   how are they compared on rendering model, accessibility bridge, platform reach and DPI,
   packaging and update, offline behavior, testability, dependency weight, idle and frame cost,
   and boot time? Compare without selecting.
5. What is the decisive falsifier for each candidate (accessibility bridge gaps, packaging or
   notarization constraints, unbounded idle cost, platform parity failure, or a missing typed
   input path), and what negative trace eliminates an option before any benchmark?
6. How are rendering performance and idle budgets defined per lifecycle phase (startup,
   first-use, steady, recovery, hidden/backgrounded) with p50/p95/p99 frame and input latency,
   memory and GPU/handle cost, and an explicit `unknown-until-measured` disposition rather than
   invented numbers?
7. How is the `PERF-010` 0/1/5/10/20-view cost contract preserved when the views are graphical,
   including that a GUI view never multiplies model/worker calls, blocks canonical append, or
   turns detach/reconnect into relaunch?

### Accessibility (WCAG 2.2 AA)

8. Which WCAG 2.2 Level AA success criteria apply to the GUI's core workflows (navigation,
   review, diff, conversation, stop/control, configuration), and how is each satisfied and
   verified by an independent check rather than a toolkit claim?
9. How are keyboard completeness, visible focus, logical traversal order, focus restoration
   after closing panels, non-color-only status encoding, sufficient contrast, text resizing,
   reduced-motion and semantic (rate-limited) screen-reader announcements ensured?
10. How does the accessibility contract interoperate with the plain-text and screen-reader
    surfaces the terminal already defines, so the GUI does not regress accessibility available
    in the TUI?

### Offline, detach/attach and security

11. How are offline and cached read views defined so a cached projection is honest: it shows its
    "last synchronized" boundary, marks stale or disconnected state, never grants control
    authority, and displays a replay gap as a gap?
12. How do detach and attach work across window close, host sleep, network loss and client crash,
    and how is reattachment proven to restore a projection without relaunching a process, model
    call or effect?
13. What is the security boundary: no direct canonical-state authority, no credential custody or
    widened credential visibility (D-021), typed commands only through the common admission path,
    and local caches that cannot become a second writer — and what negative fixture proves each?

### Migration path and falsifiers

14. What is the incremental migration path from the TUI, including shared command/query usage,
    keybinding and layout reuse, and a surface-switch that does not change command meanings or
    require parallel semantics?
15. What would falsify the claim that the GUI adds value over the TUI without raising cost or
    review burden — for example a workflow that cannot be expressed without a divergent command,
    an accessibility regression, or a frame/idle budget breach — and what does this candidate
    explicitly not prove?
16. What provider-free acceptance fixtures accept or reject the GUI's model: identical query
    results with the TUI, a typed-command-only mutation attempt, a cached-view staleness display,
    a keyboard-only traversal, a reduced-motion mode, a detach/attach round trip and an
    N-window soak — with an exact pass/fail predicate for each?

## Deliverable

A graphical client architecture candidate containing: a **requirements** section traced to
accepted decisions and interface requirements; a **framework-agnostic stack comparison** covering
rendering model, accessibility bridge, platform reach, packaging, offline behavior, testability,
dependency weight, and startup/idle/frame cost, with a competing option, decisive falsifier and
non-proof for each and **no selection**; a **common-model reuse** section that fixes mandatory use
of the same command-and-query model and projections with no divergent semantics; an
**accessibility** section targeting WCAG 2.2 Level AA with a criterion-to-workflow map and
independent verification; a **rendering, performance and idle budget** section per lifecycle
phase tied to `PERF-010`; an **offline/cached read view** section with "last synchronized"
honesty and no control authority; a **detach/attach and security** section (typed commands only,
no direct canonical-state authority, no credential custody); a **TUI migration path**; and a
provider-free fixture suite. Each recommendation names a competing option, a decisive falsifier
and what it does not prove. No language, UI framework, renderer, transport, store or vendor is
selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, UI toolkit,
  renderer, transport, wire encoding or vendor.
- No claim that the GUI is required for v3 or for any core workflow; it remains opt-in and later
  than the terminal (D-019).
- No assertion that a window, panel, canvas, gesture or layout confers authority or owns an
  actor; closing a window or client is a detach, never a Stop.
- No claim that a graphical client, GPU rendering or animation improves performance,
  productivity or accessibility without measurement; each carries a competing option and a
  falsifier.
- No provider, model, credential or account call; no toolkit installed or run; every fixture is
  synthetic and provider-free.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that porting an existing client, plugin or toolkit is cheap; it remains a
  hypothesis with a falsifier (D-033).
- No new executive tier, no separate AI "ARM manager", and no second portfolio executive created
  by a window, panel or cached view.
- No reopening of D-018, D-019, D-021, D-022, D-024 or D-033, and no reopening of the accepted
  requirements in `INTERFACE-STRATEGY.md`, `TERMINAL-RUNTIME.md`, `CLI.md`,
  `M1B-WIRE-PROFILE.md` or `PERFORMANCE-PLAN.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The requirements section traces every graphical-client requirement to an accepted Owner
  decision or accepted interface requirement, including spatial navigation, artifact/diff
  review, lineage, context comparison, provenance inspection and accessible responsive views.
- The stack comparison is framework-agnostic and compares at least the named candidate
  approaches on rendering model, accessibility bridge, platform reach/DPI, packaging, offline
  behavior, testability, dependency weight and startup/idle/frame cost, with a competing option,
  decisive falsifier and non-proof for each, and selects none.
- The common-model reuse section mandates the same command-and-query model and projections with
  no divergent semantics and names the demonstrable checks that would falsify that claim.
- The accessibility section targets WCAG 2.2 Level AA, maps the core workflows to the applicable
  success criteria, covers keyboard completeness, visible focus, traversal and focus restoration,
  contrast and non-color-only encoding, resize, reduced-motion and semantic announcements, and
  requires independent verification with an `unknown` disposition for unrun checks.
- The rendering/performance section defines per-phase p50/p95/p99 frame and input latency,
  memory/GPU/handle and idle budgets tied to the `PERF-010` 0/1/5/10/20-view matrix, with
  freeze rules and `unknown-until-measured` cells and no single scalar score.
- The offline section defines cached read views with a visible "last synchronized" boundary,
  stale/disconnected marking, no control authority and replay gaps shown as gaps; the
  detach/attach and security section states typed-commands-only, no direct canonical-state
  authority and no credential custody (D-021).
- The migration section describes an incremental path from the TUI without changing command
  meanings or creating parallel semantics.
- The provider-free fixture suite specifies pass/fail predicates for cross-surface query
  equality, typed-command-only mutation, cache staleness display, keyboard-only traversal,
  reduced motion, detach/attach and an N-window soak, and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, UI framework, renderer, transport, store or vendor is selected and no route is
  qualified.
- The candidate explicitly states what it does not establish: no measured performance, no
  accessibility conformance, no entitlement, no security boundary between views, no route
  qualification and no measured porting cost.
- Protected paths are untouched; privacy and secret scan are clean.

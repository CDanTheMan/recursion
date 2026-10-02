---
title: R-K — Terminal multiplexer and transformative TUI
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-K — Terminal multiplexer and transformative TUI

This is a terminal-experience handoff for accepted Owner decisions D-018, D-019, D-022 and
D-024, with D-021 and D-033 as constraints, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-J](R-J-multi-agent-terminal-communication.md), the terminal multi-agent interaction handoff,
and on [R-I](R-I-grok-build-source-study.md), the Grok Build source study, and must extend rather
than restate them: R-J designs the *interaction* between parallel agents, while R-K designs the
multiplexer substrate those views live in and the *transformative* TUI on top of it. It consumes
the already accepted direction in [TERMINAL-RUNTIME.md](../../TERMINAL-RUNTIME.md),
[INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md), [M1B-WIRE-PROFILE.md](../../M1B-WIRE-PROFILE.md)
and [PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md); it must not reopen their requirements.

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

- The exact user-perceivable experience to design: the terminal **multiplexer** — a
  server/daemon that owns attachable client views — plus a **transformative TUI** built on it
  that could define the category for a harness orchestrator. Views open, close, split and
  reattach without ever killing the actor behind them; the TUI is the composition layer over
  the interaction model R-J specifies.
- D-018 makes Recursion a first-class native harness and a first-class unifying wrapper over
  the wider harness ecosystem, whose purpose is to remove lock-in and cut quota/usage burn,
  with no ecosystem lock-in; the multiplexer and TUI must therefore be broker-neutral and
  route-neutral, not tied to one vendor's UI or one runtime.
- D-019 builds the comprehensive capability and plugin surface but ships every capability as an
  opt-in plugin or profile rather than a default; multiplexer layouts, graph views and parallel
  agents may not appear, activate or spend by default, and attaching or splitting a view must
  add no inference, indexing or plugin activation.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — **Aggressive / Full / Lazy** — plus `checkpoint`, `interrupt` and `drain`.
  A source interrupt, socket close or killed PID is not external rollback; closing a tab or pane
  is a detach, not a Stop, and closing a multiplexer client must never be read as a Stop.
- D-024 makes productive continuity the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting; the TUI must show continuity state
  truthfully rather than a fabricated live badge, and a reattached view must restore the same
  task without relaunching work.
- D-021 requires delegation over credential intermediation: driving the user's already
  authenticated harness is preferred, so the multiplexer must not become a credential relay and
  a view must never widen credential visibility.
- D-033 keeps porting strictly a hypothesis to validate: any claim that an existing multiplexer
  or TUI (tmux, Zellij, Grok Build, OpenCode, T3 Code) can be ported cheaply must carry a
  falsifier and measured cost, not an assumption.
- Already accepted, non-negotiable direction this lane must respect rather than relitigate: the
  daemon/broker owns actors and process trees; terminal windows are views, not process owners;
  one active lease owns input and resize while other clients are passive readers; a slow or
  absent view cannot block Stop, canonical append or recovery; a view is an authorized
  projection, not process ownership; multiple views of one actor and multiple actors in one view
  are both supported without merging contexts; the process broker drains PTY output with zero
  clients attached; presentation frames may be coalesced but command, lease, process-exit,
  termination and canonical state events may not be dropped; the canonical event is appended
  before a presentation queue may coalesce or drop anything; wire encoding and numeric limits
  remain experimental pending this research.
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
  frames, process/handle counts and canonical append delay.
- Already accepted interface direction from [INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md):
  the interactive TUI owns live conversation, focused work views, keyboard-first
  steering/queueing, an attention inbox, split/attached views, task switching and compact
  inspect panels, and must not own actor/process lifetime, invoke a hidden model on attach or
  repaint the full log on every token; the five primary destinations are Work, Attention,
  Artifacts, Environment and Settings/recovery, with a command palette.
- The open item this lane closes is recorded verbatim in
  [SYNTHESIS.md](../../research-lane/SYNTHESIS.md): the terminal lane left open the
  **"multiplexer role and wire encoding"**. This handoff is the research that answers it.
- Prior comparison coverage exists and is the reference for what is already known: the Grok
  Build Agent Dashboard (a TUI dashboard with top-level sessions, forks, subagents under
  parents, peek/reply, worktree dispatch, closed-view-versus-deletion) (R-I and R-J); the Meta
  Muse Code interactive terminal (active steer / next-turn queue / retract / interrupt,
  clarifying questions, task/subagent views, manual compaction); OpenCode v1/v2 TUI
  (steer/queue, pending cancellation, projected-history forks, rich compaction receipts); the
  Codex TUI (active instructions versus next-turn queueing, side conversations, visible
  subagents, worktrees, remote control, review); and T3 Code (web/desktop/mobile control over six
  integrations, a Working section that surfaces threads needing decisions, a composer that
  separates Queue and Steer, drafts and offline intent; its documented `t3` CLI is a
  server/service control entrypoint, not a TUI).
- Prior art that prevents claiming novelty: attention inboxes, persistence, task graphs, command
  receipts, worktrees and configurable workflows already exist elsewhere (D-024 and the
  2026-10-02 strategy). T3 Code's command/effect-state separation and Muse's session protocol are
  version- and maturity-specific comparison candidates, not endorsed components.
- Evidence status: no product multiplexer, N-view session, renderer comparison or TUI has been
  implemented or measured by Recursion for this lane. Every usability, differentiation, cost,
  latency and performance statement below is to be established from public source, product
  documentation and a synthetic provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **terminal multiplexer and transformative-TUI design candidate** for
Recursion. The lane specifies the multiplexer architecture (server/daemon plus attachable client
views; open/close/split without killing actors; one fenced input/resize lease; N concurrent
views; monotonic cursors; RESET/GAP resync; slow-client isolation; detach/reattach across
terminal loss), the rendering and responsiveness contract (non-flicker incremental/diff
rendering, frame pacing, stable scrollback, a follow-mode affordance, Unicode/IME safety and
high-throughput behavior under explicit latency and tail budgets tied to `PERF-010`), the
transformative TUI layout concepts, keyboard and accessibility requirements, a comparison
against Grok Build Agent Dashboard, Meta Muse Code, OpenCode, Codex TUI and T3 Code that
separates genuine novelty from existing affordances, the open multiplexer decision compared
without selecting it, and provider-free acceptance fixtures. It delivers a design candidate with
competing options, decisive falsifiers and an explicit statement of what it does not prove. It
does not select a language, store, framework, transport, UI toolkit, renderer, multiplexer or
vendor, does not qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, UI toolkit, transport, renderer,
multiplexer, wire encoding or vendor.** Do not decide an Owner question recorded in D-018, D-019,
D-021, D-022, D-024 or D-033. Treat the Grok Build Agent Dashboard, Muse Code, OpenCode, Codex
TUI and T3 Code as prior art cited from public documentation, not as endorsed or selected
components. No provider, model or account call is made; no live multiplexer session or room is
created; no credential or account is touched. Do not claim that a layout, tab, pane nesting,
focus or window geometry confers authority or owns an actor. Do not assert that the
multiplexer, a diff renderer or "more views" improves performance; that is a hypothesis with a
falsifier. Closing a view is a detach, never a Stop.

## Inputs to read

None from this repository: the rescope, the accepted terminal and interface requirements, the
M1B wire profile, the `PERF-010` matrix and the prior comparison coverage are summarized in
`## Baked context` above, and no repository, connector or private-source access is assumed. The
session must, however, retrieve the public product documentation it cites — the Meta Muse Code
interactive/terminal pages, the OpenCode TUI documentation, the pinned public Grok Build Agent
Dashboard and keyboard-shortcut documentation, the Codex terminal documentation, the T3 Code
README/composer/thread-sidebar documentation, the tmux and Zellij documentation for the external
multiplexer comparison, and the accepted terminal requirements summarized above — and pin each
claim to a URL and retrieval date.

## Research questions

### Multiplexer architecture: daemon, attachable views and lease

1. What is the server/daemon-plus-client architecture for a product multiplexer in which many
   client views attach to one runtime: how are views opened, closed and split without killing the
   actor behind them, and which process owns actors, PTYs, canonical state and view projection?
2. How is exactly one fenced input/resize **lease** defined so that one active client owns input
   and resize while N-1 clients remain passive readers; how does a passive reader request and
   receive control; and why must focus or attach alone never steal the lease?
3. What monotonic per-view cursor, snapshot and replay floor does each view carry; how does a
   late-joining or reconnecting view converge on the same state; and how do `RESET` and an
   explicit `GAP` resync a view when the requested cursor falls below the replay floor without
   inventing an event?
4. How is a slow, stalled or absent client isolated so it cannot block Stop, canonical append or
   recovery, and what bounded per-view credit, queue high-water and coalescing rule guarantees
   that, distinguishing presentation coalescing from the non-droppable command, lease,
   process-exit, termination and canonical-state events?
5. How does detach and reattach work across terminal loss (window closed, host sleep, SSH drop,
   terminal crash) including the zero-view state, and how is reattachment proven to restore a
   view without relaunching a process, model call or effect?

### Rendering and responsiveness

6. Which rendering approach best achieves non-flicker output — incremental/diff cell or region
   updates versus bounded full repaint — and under what measured conditions (near-total screen
   change, resize storms, very wide Unicode frames) is the competing approach cheaper; what is
   the decisive falsifier for each?
7. What frame pacing, event batching and input-priority policy keeps typed input responsive while
   high-throughput output streams, and how is "update only changed cells" reconciled with
   correctness under partial frames and resizes?
8. How are stable scrollback and a **follow-mode** affordance defined so that output does not
   drag a reading user to the bottom, a new-events indicator restores follow mode, and scrollback
   remains complete even when live presentation samples repetitive deltas?
9. What Unicode and IME safety contract is required: grapheme-cluster and display-width
   correctness, combining marks, wide/ambiguous characters, emoji, paste bracketing, IME
   composition preserved under streaming, and untrusted terminal control sequences kept from
   becoming UI commands?
10. What explicit latency and tail budgets should `PERF-010` require — p50/p95/p99 input latency,
    frame time, canonical-append delay and coalesced/dropped counts — and what numeric thresholds
    or "unknown until measured" disposition should each carry, given that no measured result
    exists for Recursion?

### The transformative TUI

11. What layout concepts make a best-in-class harness-orchestrator TUI: a focused task workspace,
    agent tabs and split panes, an attention inbox, and on-demand inspectors (Changes, Context,
    Route, Usage, Details) — and how do these compose over the R-J interaction model without
    opening graph, telemetry and evidence panes simultaneously by default?
12. Against the Grok Build Agent Dashboard, Meta Muse Code, OpenCode, Codex TUI and T3 Code, which
    cells are source-documented, inferred or `unknown`, and which affordances are already
    existing (attention inbox, persistence, task graph, receipts, worktrees, configurable
    workflows) rather than novel?
13. What, if anything, would make Recursion's TUI genuinely define the category — for example the
    combined contract of multiplexer-bounded views, truthful
    accepted/delivered/adopted and continuity state, one bounded step lease and
    `PERF-010`-bounded multi-view cost — and what would falsify each claimed differentiation?
14. How does the TUI present truthful state as a set of facts rather than one optimistic badge
    (saved-locally versus accepted versus delivered/applied versus observed outcome versus
    settled/unresolved; generated/tested/reviewed/accepted/published; compiled/validated/staged/
    effective), and how is a replay gap shown as a marker rather than an invented story?

### Keyboard and accessibility

15. What keybinding model gives full keyboard access with discoverable, named controls, visible
    non-obscured focus, logical traversal, focus restoration after closing inspectors, and
    customizable non-conflicting shortcuts?
16. How is a persistent, discoverable **Stop** affordance provided with its selected
    Aggressive/Full/Lazy mode and scope visible, without a mouse-only gesture or a
    timing-sensitive double keypress, and why must Escape not be globally overloaded with
    destructive cancellation?
17. What plain-text, high-contrast and reduced-motion modes are required, and how are status
    changes announced semantically and rate-limited so a screen reader hears important state
    without reading every streamed token or stealing focus?

### The open multiplexer decision

18. Compare the competing multiplexer approaches — an in-process renderer, a local daemon socket
    with thin clients, and an external multiplexer (tmux, Zellij or OS terminal panes) as the
    view host — on detach semantics, process-ownership independence, Windows/Linux parity,
    accessibility, testability and dependency cost. Do not select one.
19. Compare the wire and encoding choices — bounded framing, backpressure mechanism, cursor
    identity (`utf8-byte` versus `event`), snapshot format, and JSON/JSONL versus a binary
    encoding — against the frozen M1B message set. Do not select one.
20. How does each multiplexer and encoding option interact with the ratified daemon/broker
    ownership boundary, the one-lease rule and the Windows ConPTY/Job Object and Linux
    PTY/session/cgroup paths, and what negative trace would eliminate an option before any
    benchmark?
21. What is the decisive falsifier for the claim "an external multiplexer can simply be used as
    the runtime," and what cost or failure (parity, detach semantics, authority, porting effort
    under D-033) would reverse the preference for a product-owned view layer?

### Provider-free acceptance fixtures

22. What provider-free fixtures must accept or reject: an N-view soak at 0, 1, 5, 10 and 20
    passive views under idle and high-output loads; a slow or stalled client; a
    disconnect/reconnect; resize storms; huge output; Unicode and IME sequences; and detached
    actor lifetime — and what is the exact pass/fail predicate for each?
23. How do the fixtures prove that closing a view detaches rather than kills, that a split or
    second view adds no inference, indexing or plugin activation, that a slow client cannot
    block canonical state or Stop, that cursors stay monotonic and every `perf-010` view count
    respects the canonical-append and memory bounds, and that no view geometry creates a second
    portfolio executive — using synthetic events only, with no provider call?

## Deliverable

A terminal multiplexer and transformative-TUI design candidate containing: a multiplexer
architecture section that defines the server/daemon plus attachable client views, open/close/
split without killing actors, the single fenced input/resize lease, N concurrent views, monotonic
cursors, `RESET`/`GAP` resync and slow-client isolation, with detach/reattach across terminal
loss including the zero-view state; a rendering and responsiveness section fixing the non-flicker
incremental/diff approach with its bounded-full-repaint competing option, frame pacing, stable
scrollback, the follow-mode affordance, Unicode/IME safety and explicit p50/p95/p99 input, frame
and canonical-append budgets tied to the `PERF-010` N-view matrix; a transformative-TUI section
with layout concepts (focused task workspace, agent tabs/splits, attention inbox, on-demand
inspectors) and a per-cell comparison table against Grok Build Agent Dashboard, Meta Muse Code,
OpenCode, Codex TUI and T3 Code with an explicit differentiation ledger separating genuine
novelty from existing affordances; a keyboard and accessibility section covering full keyboard
access, a discoverable persistent Stop, no destructive Escape overload, a keybinding model,
plain-text/high-contrast/reduced-motion modes and rate-limited screen-reader status
announcements; an open-decision section comparing in-process renderer, local daemon socket and
external multiplexer approaches plus the bounded-framing, backpressure, cursor-identity and
encoding choices **without selecting any**; and a provider-free fixture suite for the N-view
soak, slow client, disconnect/reconnect, resize storms, huge output, Unicode/IME and detached
actor lifetime. Each recommendation names a competing option, a decisive falsifier and what it
does not prove. No language, store, framework, runtime, transport, UI toolkit, renderer,
multiplexer, wire encoding or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, transport, UI
  toolkit, renderer, multiplexer, wire encoding or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that a layout, tab, focus, pane nesting or view geometry confers authority or owns
  an actor; closing a view is a detach, never a Stop.
- No claim that a multiplexer, diff renderer, parallel agents or "more views" improve performance
  without measurement; each such claim carries a competing option and a falsifier.
- No provider, model, credential or account call; no binary installed or run; no live multiplexer
  session created; every fixture is synthetic and provider-free.
- No assertion that porting an existing multiplexer or TUI is cheap; it remains a hypothesis with
  a falsifier (D-033).
- No new executive tier, no separate AI "ARM manager", and no second portfolio executive created
  by a split or view.
- No reopening of D-018, D-019, D-021, D-022, D-024 or D-033, and no reopening of the accepted
  requirements in `TERMINAL-RUNTIME.md`, `INTERFACE-STRATEGY.md`, `M1B-WIRE-PROFILE.md` or
  `PERFORMANCE-PLAN.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The multiplexer architecture defines a server/daemon plus attachable client views, open/close/
  split without killing actors, exactly one fenced input/resize lease, N concurrent views with
  passive readers, monotonic per-view cursors, `RESET`/`GAP` resync, bounded slow-client
  isolation and detach/reattach across terminal loss including the zero-view state.
- Rendering commits to non-flicker incremental/diff updates with a named bounded-full-repaint
  competing option, frame pacing, stable scrollback, a follow-mode affordance, Unicode/IME safety
  and explicit p50/p95/p99 input, frame and canonical-append budgets tied to the `PERF-010`
  0/1/5/10/20-view matrix; the canonical append precedes any coalescing or drop.
- The TUI section defines the focused task workspace, agent tabs/splits, attention inbox and
  on-demand inspectors, and its comparison covers Grok Build Agent Dashboard, Meta Muse Code,
  OpenCode, Codex TUI and T3 Code with per-cell evidence classes (source-documented, inferred or
  `unknown`), separating genuine differentiation from already existing behavior.
- Keyboard and accessibility cover full keyboard access, a discoverable persistent Stop with its
  Aggressive/Full/Lazy mode visible, no globally destructive Escape, a keybinding model,
  plain-text/high-contrast/reduced-motion modes and rate-limited screen-reader status
  announcements.
- The open multiplexer decision compares an in-process renderer, a local daemon socket and an
  external multiplexer (tmux/Zellij/OS panes), and the bounded-framing, backpressure,
  cursor-identity and encoding choices, with a competing option, decisive falsifier and
  non-proof for each, and selects none of them.
- The provider-free fixture suite specifies pass/fail predicates for the N-view soak at 0, 1, 5,
  10 and 20 views, a slow client, disconnect/reconnect, resize storms, huge output, Unicode/IME
  and detached actor lifetime, and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, framework, runtime, transport, UI toolkit, renderer, multiplexer, wire
  encoding or vendor is selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured performance advantage,
  no route qualification, no entitlement, no UI conformance, no security boundary between views
  and no measured porting cost.
- Protected paths are untouched; privacy and secret scan are clean.

---
title: R-J — Terminal multi-agent communication and parallel-tab experience
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-J — Terminal multi-agent communication and parallel-tab experience

This is a terminal-experience handoff for accepted Owner decisions D-018, D-019, D-022, D-023,
D-024 and D-031, with D-021 and D-033 as constraints, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-I](R-I-grok-build-source-study.md), the Grok Build source study, and must extend rather than
restate it. It consumes the already accepted direction in
[INTERACTION-SURFACES.md](../../INTERACTION-SURFACES.md),
[TERMINAL-RUNTIME.md](../../TERMINAL-RUNTIME.md), [EXECUTIVES.md](../../EXECUTIVES.md) and
[INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md); it must not reopen their requirements.

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

- The exact user-perceivable experience to design: running several agents in parallel where the
  owner can open two (or N) agent tabs or split panes and **see them communicate with each
  other** — a sustained, attributable exchange, not merely two independent transcripts — in the
  spirit of the Meta Muse Code session-messaging flow, the OpenCode multi-session flow and the
  Grok Build Agent Dashboard multi-agent flow.
- D-018 makes Recursion a first-class native harness and a first-class unifying wrapper over the
  wider harness ecosystem, whose purpose is to remove lock-in and cut quota/usage burn, with no
  ecosystem lock-in; a multi-agent terminal must therefore be broker-neutral and route-neutral,
  not tied to one vendor's UI.
- D-019 builds the comprehensive capability and plugin surface but ships every capability as an
  opt-in plugin or profile rather than a default; multi-agent rooms, graph views and parallel
  agents may not appear, activate or spend by default, and attaching a view must add no
  inference, indexing or plugin activation.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — **Aggressive / Full / Lazy** — plus `checkpoint`, `interrupt` and `drain`.
  A source interrupt, socket close or killed PID is not external rollback; closing a tab is a
  detach, not a Stop.
- D-023 qualifies Codex App Server end-to-end first as the strongest structured interface; every
  other harness, Grok Build included, ships as a plugin. A parallel-tab model must therefore be
  an adapter contract that a mixed fleet of harness sessions can satisfy, not a Codex-only or
  Grok-only feature.
- D-024 makes productive continuity the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting; a multi-agent view must show continuity
  state truthfully rather than a fabricated live badge.
- D-031 positions Recursion on its unrestrictive, customizable environment — one place to connect
  keys/subscriptions, routing through any harness or its own, with privacy and safety — not on a
  vendor-sabotage claim; savings are claimed only when measured. Multi-agent rooms cross
  credential and subscription boundaries, so the design must not imply shared ambient
  credentials or a shared security boundary between agents.
- D-021 requires delegation over credential intermediation: driving the user's already
  authenticated harness is preferred, so a room transport must not become a credential relay.
- D-033 keeps porting strictly a hypothesis to validate: any claim that an existing multi-agent
  UI (Muse Code, OpenCode, Grok Build, Grok Bot) can be ported cheaply must carry a falsifier and
  measured cost, not an assumption.
- Already accepted, non-negotiable direction this lane must respect rather than relitigate:
  multiple terminal windows or panes attach to Head, an ARM, a worker, a verifier, a
  communication graph or system state; closing a terminal detaches the view without ending work;
  the daemon/broker owns actors and process trees; one active lease owns input and resize while
  other clients are passive readers; a slow or absent view cannot block Stop, canonical append or
  recovery; a view is an authorized projection, not process ownership; chat history, topic
  identity and provider sessions are never canonical task state; `PERF-010` uses 0, 1, 5, 10 and
  20 passive views under idle and high-output loads and fails if views multiply model/worker
  calls, block canonical writes, cause unbounded memory, corrupt input, lose durable events or
  turn detach/reconnect into relaunch.
- Prior comparison coverage exists and is the reference for what is already known: the Grok Build
  Agent Dashboard, steer versus queue versus "send now", peek/reply, worktree dispatch and the
  "closed view versus session deletion" distinction (R-I, and the strategy's Grok Build section);
  Muse Code active steer / next-turn queue / retract / interrupt, session messaging limited to
  same-user interactive sessions on one machine, and peer messages that do not convey approval
  authority; OpenCode v1/v2 steer/queue, pending cancellation and projected-history forks; and
  Grok Bot named persistent Bots, parallel work on a shared computer, explicit addressing,
  visible asynchronous handoffs, one owner per stage, and the explicit statement that separate
  Bots are not security boundaries.
- Evidence status: no multi-agent terminal room, shared-room transport or N-view soak has been
  implemented or measured by Recursion for this lane. Every usability, differentiation, cost and
  performance statement below is to be established from public source, product documentation and
  a synthetic provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **terminal multi-agent interaction specification** for running two or
more agents in parallel views and seeing them communicate. The lane specifies the interaction
model (tabs, split panes, a shared room or consultation view, peek/reply, the input/resize lease,
and detach-without-kill), the rendering of attributable agent-to-agent exchange (requester,
recipient, correlation, and adopted/declined/expired state), the authority separation that keeps
chat order and room membership from becoming command authority, the cost and backpressure
contract that keeps multiple views from multiplying worker/model cost, a comparison against Muse
Code, OpenCode, Grok Build and Grok Bot that separates genuine differentiation from already
existing behavior, and provider-free acceptance fixtures. It delivers a spec with competing
options, decisive falsifiers and an explicit statement of what it does not prove. It does not
select a language, store, framework, transport, UI toolkit or vendor, does not qualify any route,
and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, UI toolkit, transport or vendor.**
Do not decide an Owner question recorded in D-018, D-019, D-021, D-022, D-023, D-024, D-031 or
D-033. Treat Muse Code session messaging, OpenCode multi-session behavior, the Grok Build Agent
Dashboard and Grok Bot rooms as prior art cited from public documentation, not as endorsed or
selected components. No provider, model or account call is made; no live multi-agent room is
created; no credential or account is touched. Do not claim that Chat transcript order, window
nesting, tab focus or room membership confers authority. Do not assert that parallel agents
improve performance or that "more agents" is faster; that is a hypothesis with a falsifier.

## Inputs to read

None from this repository: the rescope, the accepted interaction requirements, R-I's Grok Build
findings and the prior comparison coverage are summarized in `## Baked context` above, and no
repository, connector or private-source access is assumed. The session must, however, retrieve
the public product documentation it cites — the Meta Muse Code interactive/session-messaging
pages, the OpenCode multi-session documentation, the pinned public Grok Build Agent Dashboard and
peek/reply documentation, the Grok Bot overview and collaboration pages, and the accepted
terminal requirements summarized above — and pin each claim to a URL and retrieval date.

## Research questions

### Interaction model: tabs, panes, rooms and detach

1. For a terminal that runs several agents in parallel, what is the interaction model that lets the
   owner open two (or N) agent tabs and split panes and see them communicate: per-actor views, a
   shared room / consultation view, or a hybrid — and which is the clearest default for the
   accepted Head -> ARM -> worker topology without inventing a new executive tier?
2. How should peek/reply be defined so a reader can inspect another agent's stream and reply
   without stealing focus, duplicating work or silently redirecting the target — and how does
   peek/reply differ from active steering, from a queued message and from a consultation request?
3. Who owns the input lease and the resize lease for a given view, how is a read-only viewer
   distinguished from a controller, how does a viewer request a control lease, and why must focus
   alone never steal a lease?
4. How does a closed tab or pane detach without killing the actor, how is a detach distinguished
   from session deletion and from a deliberate Stop, and how does a reconnect or a second view
   avoid relaunching work or duplicating execution?
5. What stable per-view cursor, snapshot and replay floor does a shared room need so that an
   attached, a late-joining and a reconnecting view converge on the same attributable exchange
   without a gap being invented?

### Visible inter-agent exchange and awareness

6. How should an agent-to-agent message be rendered so it is attributable and honest: requester,
   recipient, correlation identity, causation, goal/context revision, and the distinct states
   requested / accepted / delivered / answered / declined / adopted / expired / settled?
7. How should steering and queueing *between* agents be expressed — an addressed request, an
   injected steer at a safe gap, a next-turn queue, or a send-now — and how are `accepted`,
   `delivered` and `adopted` kept visibly distinct so a message never reads as a grant or an
   authoritative decision?
8. How can an owner stay aware of an N-agent exchange without reading every token: what summary,
   attention count, causal-ordering or "unseen activity" affordance is truthful, and how are
   slow, disconnected or high-output agents represented without a busy spinner pretending to be
   progress?
9. How are multiple views of the same actor and multiple actors in one view represented without
   merging their private contexts, and how does a shared room make the speaker's logical identity
   and GoalSpec visible without making its context canonical?

### Authority separation

10. How is "chat order is not authority" enforced in the design: what makes simultaneous or
    out-of-order proposals remain evidence until an authorized holder commits one transition,
    and why is transcript arrival order never the tie-breaker?
11. Why is a shared room not command authority, and how does the design prevent room membership,
    tab focus, addressing syntax or a peer recommendation from widening GoalSpec, privacy,
    egress, credential visibility, billing or tool grants?
12. Why does consultation not grant amendment rights, and how is a bounded, expiring
    `CoordinationLease` for one `workflow_step_id` structured so it cannot add members, transfer
    itself, settle cross-goal disputes or change the conflict policy — and what returns
    coordination to Head on expiry, revocation, PAUSE or conflict?
13. Which actor or lease holder may author an authoritative plan transition in a multi-agent
    room, and how does the design keep one writer per workflow step while several actors
    converse?

### Cost, backpressure and performance honesty

14. What bounded per-view credit and canonical-append-before-coalescing rules keep a slow or
    absent client from blocking canonical state, and how does the design guarantee that no view
    attach, tab switch, graph refresh or peek launches a model call, index build or plugin
    activation?
15. Why must multiple views of the same work not multiply worker/model cost, and how does the
    design satisfy `PERF-010`'s 0, 1, 5, 10 and 20 passive-view matrix under idle and high-output
    loads without multiplying model/worker calls, blocking canonical writes, causing unbounded
    memory, corrupting input, losing durable events or turning detach/reconnect into relaunch?
16. What is the decisive falsifier for the claim that "more parallel agents = more performance"?
    State the rejected claim, the competing option (fewer, better-coordinated agents at the same
    total budget) and the measurement that would reverse the recommendation, including retries,
    compaction and human review in the total.

### Comparison and genuine differentiation

17. Against the Meta Muse Code session-messaging flow (active steer, next-turn queue, retract,
    interrupt, sender attribution, same-user same-machine limits, peer messages not conveying
    approval authority), which cells are source-documented, inferred or `unknown`, and what does
    Recursion add or merely repeat?
18. Against the OpenCode multi-session flow (v1 and v2 steer/queue, pending cancellation,
    projected-history forks), which cells are source-documented, inferred or `unknown`, and what
    is genuinely differentiated?
19. Against the Grok Build Agent Dashboard (top-level sessions, forks, subagents under parents,
    peek/reply, worktree dispatch, closed view versus session deletion), which cells are
    source-documented, inferred or `unknown`, and what must Recursion preserve rather than
    normalize away?
20. Against Grok Bot multi-agent rooms (named persistent Bots, parallel work on a shared
    computer, explicit addressing, visible asynchronous handoffs, one owner per stage, Bots not
    being security boundaries), what is genuinely differentiated versus already existing, and
    where must Recursion explicitly reject the shared-computer-credential and chat-as-authority
    assumptions?
21. What, if anything, is genuinely differentiated once the comparison is complete — for
    example the combined contract of visible consultation, one bounded step lease, honest
    accepted/delivered/adopted states, continuity across a harness change and `PERF-010`-bounded
    multi-view cost — and what would falsify each claimed differentiation?

### Provider-free acceptance fixtures

22. What provider-free fixtures must accept or reject: duplicate, out-of-order, edited and deleted
    messages; a stale adoption against a changed lease or goal revision; simultaneous lease
    contention; disconnect and reconnect; and an N-view soak at 0, 1, 5, 10 and 20 passive views
    — and what is the exact pass/fail predicate for each?
23. How do the fixtures prove that closing a tab detaches rather than kills, that a second view
    adds no inference or indexing, that a slow client cannot block canonical state or Stop, and
    that no chat topology creates a second portfolio executive — using synthetic events only, with
    no provider call?

## Deliverable

A terminal multi-agent interaction specification containing: an interaction-model section that
compares per-actor tabs, split panes, a shared room / consultation view and a hybrid, and defines
peek/reply, the input and resize lease, detach-without-kill and per-view replay cursors; a
rendering section for attributable agent-to-agent exchange that fixes the requester, recipient,
correlation and adopted/declined/expired vocabulary and keeps accepted, delivered and adopted
distinct; an authority-separation section stating that chat order is not authority, a shared room
is not command authority, consultation does not grant amendment rights, and only one bounded
`workflow_step_id` lease permits a step transition; a cost/backpressure section with bounded
per-view credit, canonical-append-before-coalescing, no-view-launches-work and a `PERF-010`
N-view cost contract, with the "more parallel agents = more performance" claim rejected and
falsified; a comparison table against Muse Code, OpenCode, Grok Build and Grok Bot with per-cell
evidence classes and an explicit differentiation ledger; and a provider-free fixture suite for
duplicate/out-of-order/edited/deleted messages, stale adoption, lease contention,
disconnect/reconnect and an N-view soak. Each recommendation names a competing option, a
decisive falsifier and what it does not prove. No language, store, framework, runtime, transport,
UI toolkit or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, transport, UI
  toolkit or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that a chat, room, tab, focus or window nesting confers authority; chat order is
  never a tie-breaker.
- No claim that a peer message, consultation reply or persistent session is a grant, an approval
  or an authoritative decision.
- No new executive tier, no separate AI "ARM manager", and no second portfolio executive created
  by a shared room.
- No claim that parallel agents or "more agents" improve performance without measurement; that
  claim is rejected and carries a falsifier.
- No provider, model, credential or account call; no binary installed or run; no live multi-agent
  room created; every fixture is synthetic and provider-free.
- No assertion that porting an existing multi-agent UI is cheap; it remains a hypothesis with a
  falsifier (D-033).
- No reopening of D-018, D-019, D-021, D-022, D-023, D-024, D-031 or D-033, and no reopening of
  the accepted requirements in `INTERACTION-SURFACES.md`, `TERMINAL-RUNTIME.md`, `EXECUTIVES.md`
  or `INTERFACE-STRATEGY.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The interaction model compares per-actor tabs, split panes, a shared room / consultation view
  and a hybrid, defines peek/reply, names the input and resize lease holder, and specifies
  detach-without-kill and per-view replay cursors.
- Agent-to-agent messages are rendered with requester, recipient, correlation and
  adopted/declined/expired state, and `accepted`, `delivered` and `adopted` are visibly distinct.
- Authority separation is explicit: chat order is not authority, a shared room is not command
  authority, consultation grants no amendment rights, and one bounded `workflow_step_id` lease
  governs a step transition, with expiry, revocation, PAUSE and conflict returning coordination
  to Head.
- The cost section guarantees bounded per-view credit, canonical append before any coalescing or
  drop, and that no view attach, tab switch, graph refresh or peek launches model, index or plugin
  work; it commits to the `PERF-010` N-view matrix and rejects "more parallel agents = more
  performance" with a decisive falsifier.
- The comparison covers Muse Code, OpenCode, Grok Build (Agent Dashboard, peek/reply, worktrees)
  and Grok Bot multi-agent rooms with per-cell evidence classes (source-documented, inferred or
  `unknown`), and separates genuine differentiation from already existing behavior.
- The provider-free fixture suite specifies pass/fail predicates for duplicate, out-of-order,
  edited and deleted messages, stale adoption, lease contention, disconnect/reconnect and an
  N-view soak, and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, framework, runtime, transport, UI toolkit or vendor is selected and no route
  is qualified.
- The spec explicitly states what it does not establish: no measured performance advantage, no
  route qualification, no entitlement, no UI conformance, no security boundary between agents and
  no measured porting cost.
- Protected paths are untouched; privacy and secret scan are clean.

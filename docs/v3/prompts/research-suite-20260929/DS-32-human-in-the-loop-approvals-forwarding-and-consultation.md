---
title: DS-32 — Human-in-the-loop approvals, forwarding, and consultation
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-32 — Human-in-the-loop approvals, forwarding, and consultation

This is a self-contained Deep Research handoff. Supplying this document is the invocation; it makes no repository or provider call on its own. Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. It is a public/synthetic research lane and includes no private conversation content.

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

- Recursion v3 is a provider-neutral agent platform whose owner-facing surfaces are an interactive detachable CLI (canonical local configuration/control surface), optional Telegram (an interactive transport for conversation, commands and monitoring), and a read-only Observer Interface. No graphical client is required for v3. Terminals attach/detach, closing a terminal does not end work, and the daemon/process broker owns actors and process trees.
- The accepted interaction contract requires ten terminal controls, three Stop modes and preserved forks. The three Stop modes are Aggressive (forcefully interrupts the selected agent without waiting for its current operation), Full (includes subagents, shells and monitors), and Lazy (waits for an observable current-operation boundary). A preserved fork keeps the original unfinished work untouched, the derived version separate, and the parent allowance not duplicated.
- Direct Owner-to-ARM conversation is accepted: each active ARM may expose a dedicated addressable topic and the owner may talk to it without relaying every message through the Head. An accepted direct instruction becomes an attributable event under the ARM's existing GoalSpec and cannot silently create an unrelated goal or widen privacy, spending, credentials, publication or deployment authority. Head remains aware through canonical events.
- Consultation envelope (accepted direction): a consultation binds request/causation/correlation, requester and recipient logical identities and leases, goal/task version, permitted context/evidence revisions, response schema, expiry, depth/cycle limit, route/session/node and parent reservation. Durable states distinguish requested, accepted/rejected, delivered, answered/declined/blocked, and adopted/expired; effect settlement is a separate state.
- Advice versus adoption: only the current authorized lease holder may propose or accept an authoritative transition, and a changed lease can make a delayed answer ineligible for adoption while preserving it as attributable evidence. Owner answers remain distinct from advice and editorial synthesis. OR-037 is the recorded Owner decision that retains Owner-only actual GoalSpec amendments with substantial authorized routine delegation; a communication or a peer recommendation is not Owner approval.
- OR-038 is the recorded Owner decision requiring a questionnaire assistant to consult the Head and bring clarifications back while the Owner observes who requested, replied and adopted, and can participate, redirect or stop the exchange. OR-039 is the recorded Owner decision making configuration, compatibility and whole-system optimization central while preserving required communication, delegation and interaction; neither is reopened here.
- Notification, forwarding and truthful views: owner-facing notifications are projections over the same actor/event model. Presentation may coalesce only after durable append and must not delay a canonical control or PAUSE event; a revoked, replaced or unavailable transport affects one capability, not actor identity or canonical state. Owner views must distinguish engine activity from canonical acceptance, show provider reasoning only where returned, label opaque state and counters honestly, and never reconstruct hidden reasoning. A host-generated permission reply records its actual principal and must not imply human observation.
- Durability and ordering: deferred questions and waiters must survive crash/reconnect and must not target a replacement question or resurrect a stale one. A status question does not cancel an assignment; a queued follow-up is never confused with a steer into the current turn. Stale turn/lease answers and inputs receive typed conflicts, and a slow or absent view cannot block Stop, canonical append or recovery.
- Research constraints: this is a public/synthetic lane and includes no private conversation content, transcripts, local paths or credentials. It performs no runtime/transport/terminal/daemon/protocol implementation and selects no topology, transport or protocol as a product decision. It must not reopen OR-037, OR-038, OR-039 or the accepted interaction boundary; must not make provider/model/Telegram/paid-broadcast calls or run a live trial; and must not treat an acknowledgment, a protocol method name or a host-generated reply as human approval.

## Purpose

Decide the mechanisms by which a human stays meaningfully in the loop for approvals, steering and consultation, and how those mechanisms behave when work is unattended, remote or resumed. This is blocking because the accepted v3 interaction contract requires the ten terminal controls, three Stop modes, preserved forks, direct Owner-to-ARM conversation and a durable consultation envelope, and because an approval mechanism that merely appears to mediate an effect is a safety failure. The research must map concrete mechanisms onto the accepted interaction, executive and terminal-runtime boundaries without changing them.

## Authority and boundaries

The shared authority constraints are in `## Baked context`. Preserve the current constitution; write proposed reconciliation, never edit it. Public or synthetic briefs only — never private conversation content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. Do not reopen accepted Owner decisions (for example OR-037, OR-038, OR-039) or the accepted interaction boundary, and do not select a topology, transport or protocol as a product decision.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Approval and mediation mechanisms

1. How do approval callbacks, always-invoked hooks and pre-effect mediation differ in where the enforcing resource is, and which failure class does each fail to close when it is not the effecting resource?
2. Under what documented conditions can an approval reply be stale, replayed, re-targeted to a changed action, or answered by a host rather than a human, and how is each detected and rejected?
3. What does a pre-effect mediation boundary need to record — exact action, arguments, scope, current grant, principal, idempotency and receipt — to make "no undeclared effect" falsifiable?
4. Where do upstream harness approval and permission systems remain distinct from Recursion grants and resource containment, and what can be imported reliably?

### Steering, queued input, and question durability

5. How do active-turn steering, queued input and clarifying questions differ in target identity, delivery guarantee and effect on an in-flight turn, and what evidence proves actual delivery rather than acceptance?
6. How are deferred questions and waiters made durable so a crash, reconnect or delayed answer cannot target a replacement question or resurrect a stale one?
7. What is required so a status question does not cancel an assignment, and so a queued follow-up is never confused with a steer into the current turn?
8. How should multiple clients observe one conversation without an acknowledgment of presentation being mistaken for a semantic acknowledgment?

### Terminal controls, Stop modes, and preserved forks

9. How do the ten terminal controls translate to concrete observable contracts and decisive negative traces across local and remote work?
10. What distinguishes Aggressive, Full and Lazy Stop in scope, boundary and required evidence, and where does each still leave an effect ambiguous?
11. How is a preserved fork captured so original unfinished work is untouched, the derived version is separate, and the parent allowance is not duplicated?
12. How are conversation fork, worktree creation and filesystem snapshot kept as three distinct operations, and what binding must survive for recovery?

### Owner-to-ARM conversation and consultation

13. How is a direct Owner-to-ARM instruction represented as an attributable event under an existing GoalSpec without silently creating a goal or widening authority?
14. What does a consultation envelope need to bind (requester, recipient, leases, goal/task version, permitted context, response schema, expiry, depth bound, parent reservation) to keep advice, delivery and adoption as separate lifetimes?
15. How is an authoritative adoption decision kept distinct from a reply so that a late answer can remain attributable evidence while being ineligible under a changed lease?
16. What public multi-agent or assistant systems expose explicit advice-versus-adoption or lease semantics, and what do their documented failure modes show?

### Notification, forwarding, and recovery

17. How should owner-facing notifications be projected to remote surfaces with revoke, rate-limit, coalescing and recovery behavior, without presentation throttling delaying a canonical control event?
18. What recovery applies when a notification transport, bot token or remote view is revoked, replaced or unavailable, and how are duplicates and out-of-order delivery made harmless?

### Comprehension, accessibility, and truthful activity

19. How are comprehension, accessibility (including screen-reader and plain-text modes), input stability and rendering cost measured separately from raw responsiveness?
20. How are truthful activity views defined so engine activity, canonical acceptance, provider reasoning visibility and honest uncertainty are shown without fabricating progress, and which synthetic fixtures — stale steer, in-flight fork, interrupted question, duplicate and out-of-order messages, transport restart, PAUSE and revocation races — prove the mechanisms work?

## Deliverable

- A source-pinned claim table (claim, source, version/date, classification as fact/inference/hypothesis/proposal, confidence, expiry or falsifier trigger).
- A control-by-control and mode-by-mode matrix mapping each mechanism to an observable contract and a decisive negative trace, with unknown cells marked unknown.
- A consultation-envelope proposal that keeps advice, delivery and adoption as separate receipts, and a statement of where advice and authority must not be conflated.
- One recommendation tied to a named competing option and a decisive falsifier, plus open Owner questions.
- An accessible, truthful-view requirement list that does not rely on hidden reasoning.

## Non-goals

- No runtime, transport, terminal, daemon or protocol implementation.
- No language, store, framework, topology or transport selection as a product decision.
- No reopening of OR-037, OR-038, OR-039 or the accepted interaction boundary.
- No private conversation content, transcripts, local paths or credentials in any public packet.
- No provider, model, Telegram or paid-broadcast calls, and no live trial executed.
- No treating an acknowledgment, a protocol method name or a host-generated reply as human approval.
- No rate-limit bypass, paid-broadcast fallback or policy circumvention.
- No change to PAUSE, spending, deployment, publication or authority state.

## Completion gate

- Every consequential factual claim is pinned to official documentation or a primary source with version and date, or marked unverified.
- The control and Stop matrices cover every listed control and mode with no silent gap.
- Advice, delivery and adoption are represented as separate states with separate settlement.
- Approval mechanisms state where they are not the effecting resource and therefore cannot close the failure class.
- Accessibility and truthfulness requirements are stated as testable outcomes, not claims of achieved quality.
- Every recommendation names a competing option and a decisive falsifier.
- No Owner decision is reopened and no proposal is promoted into an Owner decision.
- A privacy and secret scan of the packet is clean and no protected path is edited.
- Remaining empirical unknowns and Owner questions are listed explicitly.

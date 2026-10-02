---
title: R-MOB — Mobile and remote control clients
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-MOB — Mobile and remote control clients

This is a mobile/remote-client handoff for accepted Owner decisions D-018, D-019, D-022, D-024,
D-031 and D-034, with D-021 and D-033 as constraints, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It is the third of three handoffs that make D-034's
"scales with your workflow" thesis falsifiable, alongside
[R-PC](R-PC-capability-driven-prompt-composition.md) and
[R-UI](R-UI-capability-driven-ui-projection.md). It builds directly on
[R-L](../dot-research-20261002b/R-L-interface-platform-cli-tui-gui.md), the unified interface
platform, [R-N](../dot-research-20261002b/R-N-graphical-client-architecture.md), the graphical
client, and [R-K](../dot-research-20261002b/R-K-terminal-multiplexer-and-tui.md), the terminal
multiplexer and transformative TUI, and it consumes the accepted remote-execution boundary in
[EXECUTION-FABRIC.md](../../EXECUTION-FABRIC.md) and
[R-X](../dot-research-20261002b/R-X-node-fabric-and-remote-execution-protocol.md). It consumes
the accepted direction in [INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md),
[TERMINAL-RUNTIME.md](../../TERMINAL-RUNTIME.md), [M1B-WIRE-PROFILE.md](../../M1B-WIRE-PROFILE.md)
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

- The exact thing to design: **iOS and Android control-surface clients** that attach to a
  remote-capable Recursion backend. They are additional clients of the same versioned
  observer/control protocols as the CLI, TUI and GUI: they receive authorized projections,
  issue typed commands through the common admission path, show truthful continuity and effect
  state, and hold no canonical-state authority and no credential custody. They are opt-in
  client plugins, never a prerequisite for core workflows.
- D-034 is the parent thesis: Recursion grows deterministically and without lock-in as the user
  adds subscriptions, BYOKs, plugins, configurations, nodes and modding. It states explicitly
  that "GUI and mobile are optional **client plugins** over a secure backend; remote/node fabric
  is a **backend capability**, never contingent on a client." A mobile client must therefore be
  an optional projection and control surface, not a new source of truth, not a reason the
  backend changes its semantics, and not a lock-in to one app store or platform.
- D-018 makes Recursion a first-class native harness and a first-class unifying wrapper over the
  wider harness ecosystem: the mobile client must be a replaceable presentation/control client,
  must not bind Recursion's semantics, storage or transport to one platform, toolkit or vendor,
  and must not become an ecosystem lock-in of its own.
- D-019 builds the comprehensive capability and plugin surface but ships every capability as an
  opt-in plugin or profile rather than a default. The mobile client is built but opt-in; it is
  never enabled by default, and a user without it loses no core capability. Nothing about the
  mobile client may activate a plugin, add a node or spend by backgrounding or notification.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — **Aggressive / Full / Lazy** — plus `checkpoint`, `interrupt` and `drain`.
  On mobile this must be explicit and persistent, never a swipe-only or timing-sensitive
  gesture. **Closing the last window or backgrounding the app is a detach, not a Stop**; a
  disconnected socket, killed app process or failed push delivery is not external rollback, and
  no client action may be silently read as an Aggressive/Full/Lazy Stop.
- D-024 makes productive continuity the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting. The mobile client must present
  continuity as facts — saved-locally versus accepted versus delivered/applied versus observed
  outcome versus settled/unresolved — show a replay gap as a marker, and reattach to the same
  task without relaunching work.
- D-031 forbids a vendor-sabotage claim and any unmeasured savings claim: mobile convenience or
  push notifications are never a performance, efficiency or savings claim.
- D-021 requires delegation over credential intermediation: the mobile client must never hold,
  request, copy, relay or widen provider credentials or account secrets; it must not become a
  credential vault or an intermediation shortcut, and pairing must not turn device possession
  into provider-credential custody.
- D-025 keeps continuing autonomous research optional, off by default and bounded; a notification
  or background wake on mobile must never activate it or reproduce a standing executive.
- D-027 and D-033 constrain distribution and porting: app-store distribution, store licensing,
  signing, review and platform policy are counsel-gated under **G-32**, and any claim that an
  existing mobile client or framework can be ported cheaply remains a hypothesis with a
  falsifier.
- Already accepted, non-negotiable direction this lane must respect rather than relitigate: the
  daemon/broker owns actors and process trees; the backend is remote-capable through the node
  fabric, and remote/node fabric is a backend capability never contingent on a client; views are
  authorized projections, not process owners; one active lease owns input while other clients
  are passive readers; a slow, absent or hostile client cannot block Stop, canonical append or
  recovery; the M1B message set uses opaque lease references and refusal reasons including
  `replay-gap-continuation`, `credit-exhausted`, `stale-lease` and `passive-client-input`; the
  canonical append precedes any coalescing or drop; typed commands are the only mutation path
  and require current authority; and `PERF-010`/`OR-024` govern view cost without a hidden
  scalar score.
- Already accepted client direction from [R-N](../dot-research-20261002b/R-N-graphical-client-architecture.md)
  and [INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md): a later client reuses the same
  versioned observer/control protocols and projections; offline/cached read views are permitted
  only with a visible "last synchronized" boundary and no control authority; the client has no
  direct canonical-state authority, holds no credential custody and sends typed commands through
  the common admission path; and accessibility, detach/attach and truthful `GAP`/continuity
  presentation are required rather than optional polish.
- Already accepted remote-execution direction from [EXECUTION-FABRIC.md](../../EXECUTION-FABRIC.md)
  and [R-X](../dot-research-20261002b/R-X-node-fabric-and-remote-execution-protocol.md):
  distinguish the user client, the authority coordinator, the execution host, the engine and the
  inference provider; node enrollment, authenticated transport, revocation and remote
  observation are backend capabilities; a client device is not an authority coordinator and
  cannot mint node enrollment or work authority.
- The delivered 2026-10-02c Prompt/Plugin/Skill architecture and shared-contract reconciliation
  companions (supplied research inputs, not repository paths) already establish the seven
  capability states and the `ArtifactRef`/`ContentEnvelope`/`authority_carried_none` provenance
  discipline. R-MOB consumes those and must add the mobile pairing/authentication, offline
  read-view honesty, push semantics, last-window-close and app-store/counsel questions rather
  than re-deriving shared fields.
- Evidence status: no Recursion mobile client, pairing scheme, push pipeline, offline cache,
  app-store submission or mobile performance measurement exists. Every pairing, security,
  notification, offline, latency, resource, distribution and licensing statement below is to be
  established from public platform documentation, primary standards and a synthetic
  provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **mobile and remote-control client specification candidate** for
Recursion. The lane defines the pairing and device-authentication model by which an iOS or
Android client enrolls with a remote-capable backend without holding provider credentials; the
remote session-control model (viewer versus controller roles, typed commands through the common
admission path, the single input lease, authority checked at dispatch); offline read views with
an honest "last synchronized" boundary, stale/disconnected marking and no control authority;
push and notification semantics that carry no authority, leak no content and never trigger work;
the explicit rule that last-window-close, backgrounding or socket loss is a detach and never a
Stop (D-022), together with a truthful stopped-with-unresolved-effects presentation; and an
app-store distribution/licensing analysis framed as **questions for counsel under G-32** rather
than a legal conclusion. It delivers a design candidate with competing options, decisive
falsifiers and an explicit statement of what it does not prove. It does not select a language,
mobile framework, store, transport, push provider, authentication mechanism or vendor, does not
qualify any route, and executes no provider or platform call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, mobile toolkit, transport, push
provider, authentication mechanism, wire encoding or vendor.** Do not decide an Owner question
recorded in D-018, D-019, D-021, D-022, D-024, D-025, D-027, D-031, D-033 or D-034. No
provider, model, account, store, device or push-service call is made; no credential or account
is touched; no app is built, signed, submitted or installed. Do not claim that device
possession, pairing, a push message, a notification tap, a deep link or a local cache confers
authority, owns an actor or process lifetime, or widens credential visibility. Closing the last
window, backgrounding the app, losing the network or killing the app process is a detach, never
a Stop, and no such event is external rollback. Do not assert that a mobile client, push
notification, offline cache or "more surfaces" improves performance, productivity, security or
review effort without a measured experiment; each carries a competing option and a falsifier. Do
not state a legal conclusion about app-store terms, distribution rights, export control,
trademarks or platform policy; those are questions for counsel (G-32). No claim of measured
performance, security, accessibility or distribution eligibility is authorized.

## Inputs to read

None from this repository: the rescope, the accepted interface, terminal, wire, client,
remote-execution, performance and plugin requirements and the D-018 through D-034 context are
summarized in `## Baked context` above, and no repository, connector or private-source access is
assumed. The session must, however, retrieve the public primary sources it cites — the current
Apple App Store Review Guidelines and Apple platform security, keychain/crypto and push
(APNs) documentation; the current Google Play policies, Android security, keystore and FCM
documentation; the OAuth 2.0 for Native Apps (RFC 8252) and OAuth 2.0 security best-current-
practice guidance; the current WebAuthn/passkeys specification and platform guidance; relevant
WCAG 2.2 and mobile platform accessibility documentation; and any device-pairing or remote-
session protocol specification it proposes — and pin each claim to a URL and retrieval date.
Treat every store, platform and push vendor as prior art cited from public documentation, not as
an endorsed or selected component. The delivered 2026-10-02c Prompt/Plugin/Skill architecture
and shared-contract reconciliation companions are inputs to build on, not repository links.

## Research questions

### Pairing and device authentication

1. What pairing model enrolls an iOS/Android client with a remote-capable backend without
   holding, copying or relaying provider credentials (D-021): what is shown/verified on the
   backend and the device, what is the trust root, and how is a device identity distinct from a
   provider account identity?
2. What device-authentication mechanism is defensible — short-lived scoped session tokens bound
   to a device key in platform secure storage, mutual authentication, certificate-bound or
   key-bound credentials, user-verified pairing, or a competing design — and what is the
   decisive falsifier (a stored long-lived provider credential, a bearer token that can be
   replayed, a pairing path that grants work authority, or a mechanism that cannot be revoked)?
3. How are authorization scope, audience, purpose and expiry bound to a device session so device
   possession alone never grants canonical-state authority, node enrollment, budget spend or
   credential visibility, and every protected action rechecks current authority at admission?
4. How are revocation and lost/stolen/compromised devices handled: immediate session fencing,
   remote deregistration, token/key revocation and cleanup, while preserving the rule that
   revocation does not assert a remote effect stopped?
5. How is the pairing flow resistant to phishing, relay and local attacker models, and what
   negative fixture proves that an unknown, cloned, downgraded or replayed device cannot enroll
   or act?

### Remote session control

6. What is the remote control model: viewer versus controller roles, how an active input lease is
   requested and granted, why focus/attach/pairing never steals the lease, and how a passive
   reader becomes an active controller without a second conflicting admission path?
7. How do typed mobile commands map to exactly the same versioned command-and-query model as
   CLI/TUI/GUI with no divergent semantics, idempotent receipts and typed errors, and how is a
   mobile-only gesture or affordance prevented from defining a competing action?
8. How is the one pause/stop vocabulary exposed on a small screen with mode and scope visible and
   a persistent, non-mouse-only, non-timing-sensitive affordance, and how is a full Stop
   presented truthfully when a node is unreachable or an effect is unresolved?
9. How does a mobile controller stay bounded: no hidden model invocation on attach, no added
   inference/indexing/plugin activation, no unbounded queue growth, and no ability to block
   canonical append, Stop or recovery when the mobile network is slow, absent or hostile?

### Offline read views and synchronization honesty

10. How are offline and cached read views defined so a cached projection is honest: it shows its
    "last synchronized" boundary, marks stale/disconnected state, never grants control authority,
    and displays a replay `GAP` as a gap rather than an invented story?
11. What is the exact cache key and invalidation discipline (principal, device, privacy domain,
    route/config revision, grants/fences, writer/cursor cut) so a cached view cannot serve data
    across a revoked grant, a changed privacy audience or a different principal, and so a cache
    hit never validates authority or freshness?
12. How is local persistence protected at rest and in backups (OS-provided protected storage,
    encryption boundaries, no secrets, no provider credentials, no raw private content beyond an
    authorized retention policy) and what is evicted on logout, revocation or device loss?
13. How does the client reconcile on reconnect without blind retry or duplicate effects, and how
    does it distinguish saved-locally / accepted / delivered / observed / settled with the
    honest unknown residual preserved?

### Push and notification semantics

14. What are the push/notification semantics: what may a push carry, what must it never carry
    (secrets, credentials, private content beyond an explicit disclosure policy, authority),
    and how is content minimized while remaining useful?
15. How is a notification or deep-link tap handled so it never becomes an admission, never
    triggers a model/plugin/capability activation, never reproduces a standing executive and
    never spends; and how is delivery success kept distinct from admission and effect?
16. How are notification rate-limiting, deduplication, quiet hours, per-device preferences,
    multiple-device fan-out and revocation handled, and how is the channel provider treated as an
    untrusted delivery path rather than an authority?
17. What privacy analysis is required of push payloads, timing and subscription patterns,
    recognizing that redacting obvious text is insufficient for a public observer?

### Detach, continuity and client lifetime

18. How is it proven that closing the last window, backgrounding the app, a lost socket, a
    failed push or a killed app process is a detach and never a Stop (D-022), that a reattached
    client restores the same task without relaunching work, and that a detached actor continues
    under backend ownership?
19. How does the mobile client coexist with other clients (CLI/TUI/GUI/other mobiles) without
    creating a second portfolio executive, a second writer, a competing control meaning or a
    view that owns actor/process lifetime?
20. What mobile-specific lifecycle budgets (cold start, resume from background, first-use, steady
    state, recovery, battery/wakeup, memory/handle, network bytes) must be measured rather than
    asserted, and how are they tied to `PERF-010`/`OR-024` with an `unknown-until-measured`
    disposition and no single scalar score?

### Distribution, licensing and counsel questions (G-32)

21. What questions must be put to counsel before distribution: app-store terms and review
    constraints on agentic/remote-control functionality, credentials and account handling,
    open-source (Apache-2.0) licensing and its interaction with store terms, code signing and
    notarization duties, export/encryption declarations, trademarks and branding, in-app
    purchase/subscription rules for BYOK and user subscriptions, and enterprise/MDM
    distribution — all stated as questions, not conclusions?
22. What competing distribution options exist (public store, enterprise/MDM, self-hosted or
    sideloaded/developer distribution, progressive web client) with their documented constraints,
    a decisive falsifier and what each does not prove, and how does the backend remain
    distribution-neutral so no client's availability is a backend prerequisite?
23. What provider-free acceptance fixtures accept or reject the mobile model: pairing with an
    unknown/cloned/replayed device, scope-limited action refusal, offline "last synchronized"
    display, revoked-grant cache invalidation, notification-no-authority, last-window-close !=
    Stop, detach/reattach without relaunch, an N-device/N-view soak, and a store-policy
    checklist marked as counsel input rather than a legal pass — each with an exact pass/fail
    predicate and no provider or store call?

## Deliverable

A mobile and remote-control client specification candidate containing: a **pairing and device
authentication** section defining the trust root, device identity, scoped short-lived session
credentials, revocation and the anti-phishing/anti-replay properties, with no provider-credential
custody; a **remote session control** section fixing viewer/controller roles, the single input
lease, typed-command mapping to the common model, the visible Stop vocabulary and the bounded
no-extra-work rule; an **offline read view** section fixing the "last synchronized" boundary,
stale/disconnected marking, cache key and invalidation discipline, at-rest protection, no control
authority and honest reconciliation/`GAP` display; a **push and notification** section fixing
content minimization, no-authority delivery, no activation/spend, rate-limiting and privacy
analysis; a **detach and continuity** section proving last-window-close/background/socket-loss
is a detach (D-022) and that reattach restores the same task under backend ownership; a **mobile
lifecycle budget** section tied to `PERF-010`/`OR-024` with measured-not-asserted disposition; a
**distribution and counsel** section listing G-32 questions and competing distribution options
without a legal conclusion; and a provider-free fixture suite. Each recommendation names a
competing option, a decisive falsifier and what it does not prove. No language, mobile
framework, store, transport, push provider, authentication mechanism or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, mobile
  toolkit, transport, push provider, authentication mechanism, wire encoding or vendor.
- No route qualification, account or subscription entitlement claim, eligibility finding or
  legal conclusion; app-store and licensing matters are questions for counsel under G-32.
- No provider, model, account, store, device or push-service call; no app built, signed,
  submitted or installed; no credential or account touched; every fixture is synthetic and
  provider-free.
- No credential custody and no widened credential visibility (D-021): pairing, push, cache or
  deep link never holds or relays a provider credential, and device possession never grants
  authority.
- No assertion that a window, app, notification, cache or gesture confers authority or owns an
  actor; closing the last window, backgrounding or losing the socket is a detach, never a Stop,
  and no such event is external rollback (D-022).
- No claim that a mobile client, push notification, offline cache or "more surfaces" improves
  performance, productivity, security or review effort without a measured experiment; each
  carries a competing option and a falsifier (D-031, D-034).
- No assertion that porting an existing mobile client or framework is cheap; it remains a
  hypothesis with a falsifier (D-033).
- No new executive tier, no separate AI "ARM manager", no second portfolio executive, and no
  reproduction of a standing executive through background wake or notification (D-025).
- No reopening of D-018, D-019, D-021, D-022, D-024, D-025, D-027, D-031, D-033 or D-034, and no
  reopening of the accepted requirements in `INTERFACE-STRATEGY.md`, `TERMINAL-RUNTIME.md`,
  `M1B-WIRE-PROFILE.md`, `PERFORMANCE-PLAN.md` or `EXECUTION-FABRIC.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The pairing section defines device identity, trust root, scoped short-lived session
  credentials, mutual/user-verified pairing, revocation and anti-phishing/anti-replay, and
  states explicitly that no provider credential is held, copied or relayed and that device
  possession grants no canonical-state, enrollment or spend authority.
- The remote-control section fixes viewer/controller roles, the single input lease, typed
  commands mapped to the one versioned model with idempotent receipts and typed errors, a
  visible persistent Stop with mode/scope, and boundedness against slow/absent/hostile clients.
- The offline section defines the "last synchronized" boundary, stale/disconnected marking, a
  cache key and invalidation discipline that cannot serve across revoked grants or changed
  audiences, at-rest protection with no secrets, no control authority and honest reconciliation
  with `GAP` shown as a gap.
- The push section fixes content minimization, no-authority delivery, no activation/spend, rate
  limiting, deduplication, multi-device and revocation handling, and a payload/timing privacy
  analysis, with delivery distinct from admission and effect.
- The detach/continuity section proves last-window-close, backgrounding, socket loss or killed
  app process is a detach and never a Stop (D-022), and that reattach restores the same task
  without relaunching work and without creating a second writer or portfolio executive.
- The lifecycle-budget section states cold-start, resume, first-use, steady, recovery,
  battery/wakeup, memory/handle and network budgets tied to `PERF-010`/`OR-024` with freeze
  rules, `unknown-until-measured` cells and no single scalar score.
- The distribution/counsel section lists G-32 questions and competing distribution options
  (public store, enterprise/MDM, self-hosted/sideloaded/developer, progressive web) with a
  decisive falsifier and non-proof for each, states no legal conclusion, and keeps the backend
  distribution-neutral.
- The provider-free fixture suite specifies pass/fail predicates for unknown/cloned/replayed
  pairing refusal, scope-limited action refusal, offline last-synchronized display, revoked-grant
  cache invalidation, notification-no-authority, last-window-close != Stop, detach/reattach
  without relaunch, an N-device soak and a counsel-input store-policy checklist, and no fixture
  requires a provider or store call.
- Every recommendation names a competing option, a decisive falsifier and what it does not
  prove; no language, mobile framework, store, transport, push provider, authentication
  mechanism or vendor is selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured performance, no
  security or accessibility conformance, no store eligibility, no route qualification, no
  entitlement, no legal conclusion and no measured porting cost.
- Protected paths are untouched; privacy and secret scan are clean.

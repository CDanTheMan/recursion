---
title: R-UI — Capability-driven UI projection contract
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-UI — Capability-driven UI projection contract

This is a UI-projection handoff for accepted Owner decisions D-018, D-019, D-022, D-024, D-031
and D-034, with D-021 and D-033 as constraints, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It is the second of three handoffs that make D-034's
"scales with your workflow" thesis falsifiable, alongside
[R-PC](R-PC-capability-driven-prompt-composition.md) and
[R-MOB](R-MOB-mobile-and-remote-control-clients.md). It builds directly on
[R-L](../dot-research-20261002b/R-L-interface-platform-cli-tui-gui.md), the unified interface
platform, [R-N](../dot-research-20261002b/R-N-graphical-client-architecture.md), the graphical
client, and [R-K](../dot-research-20261002b/R-K-terminal-multiplexer-and-tui.md), the terminal
multiplexer and transformative TUI, and it extends
[R-A](../dot-research-20261002/R-A-plugin-portability.md)'s capability graph with a typed UI
contribution surface. It consumes the accepted direction in
[INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md), [TERMINAL-RUNTIME.md](../../TERMINAL-RUNTIME.md),
[M1B-WIRE-PROFILE.md](../../M1B-WIRE-PROFILE.md) and [PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md);
it must not reopen their requirements.

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

- The exact thing to design: the **typed, versioned UI-contribution contract** by which any
  Recursion client (scriptable CLI, interactive TUI, later GUI, mobile/remote) deterministically
  materializes its user interface from the **effective capability set plus authorized
  projections**, rather than from hand-written per-client code. A plugin or first-party
  capability declares UI contributions against named, typed contribution points; the client
  resolves the effective set, fills only the points it supports, and refuses unknown
  capabilities fail-closed.
- D-034 is the parent thesis: Recursion grows deterministically and without lock-in as
  capabilities are added, "composing the effective system prompt and capabilities to fit the
  workflow." For the UI, the composed surface must be as deterministic and lock-in-free as the
  composed prompt: adding a plugin with UI contributions must not require a client rewrite, and
  removing or disabling one must leave no ghost, no spend and no ambient authority.
- D-018 makes Recursion a first-class native harness and a first-class unifying wrapper over
  the wider harness ecosystem: the contribution contract must be client-neutral and
  renderer-neutral, must not bind one toolkit, one vendor or one platform, and must let a
  replaceable client present the same underlying facts.
- D-019 builds the comprehensive capability and plugin surface but ships every capability as an
  opt-in plugin or profile rather than a default. A disabled capability contributes no UI
  element, no command, no badge, no model call, no index and no context/tool enumeration; its
  absence is genuinely inert, and a UI contribution can never itself activate a capability or
  spend.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — **Aggressive / Full / Lazy** — plus `checkpoint`, `interrupt` and `drain`.
  The UI must expose exactly that vocabulary with mode and scope visible, must never surface a
  destructive Stop as a timing-sensitive double gesture or a mouse-only affordance, and must
  treat closing a window, tab, pane or client as a detach, never a Stop.
- D-024 makes productive continuity the headline measurable differentiator: the UI must present
  continuity state truthfully as facts — saved-locally versus accepted versus delivered/applied
  versus observed outcome versus settled/unresolved — never as one optimistic badge, and must
  show a replay gap as a marker rather than inventing the missing story.
- D-031 forbids a vendor-sabotage claim and any unmeasured savings claim: visual richness,
  animation or "more surfaces" is never a performance or efficiency claim.
- D-021 requires delegation over credential intermediation: a UI contribution, badge, embedded
  view or plugin panel must never hold, request, relay or widen credential visibility, and no
  view, tab or geometry may confer authority.
- D-033 keeps porting strictly a hypothesis: any claim that an existing UI/extension contribution
  model can be ported cheaply carries a falsifier and measured cost.
- Already accepted, non-negotiable direction this lane must respect rather than relitigate:
  one versioned command-and-query model shared by CLI, TUI and later GUI with no divergent
  semantics and no second admission path; typed errors with code/precondition/effect-attempted/
  retryability; idempotent receipts with command IDs; deterministic zero-model status; monotonic
  per-stream cursors with bounded credit and explicit `RESET`/`GAP` resync; the canonical append
  before any coalescing or drop; non-droppable command, lease, process-exit, termination and
  canonical-state events; configuration resolution with effective value and provenance; and
  plugin-contributed views/commands that declare their supplying component and version and
  cannot acquire authority from origin.
- Already accepted interface direction from [INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md):
  the object graph users should understand (project/workspace, goal/task, assistant/role,
  run/attempt/session/turn, operation/effect, question/approval/queued input, checkpoint/context
  epoch, artifact/candidate/evidence, route, configuration/plugin/node, budget/reservation/meter
  segment); the ten controls (streaming output, questions, approvals, queued messages, active
  steering, interruption, resume, forks, compaction controls, commands/plugins); the three
  Stops (Aggressive/Full/Lazy) with their scope and required visible result; and the rule that an
  affordance must not claim a control is supported merely because it can be rendered — the exact
  route/interface/version/configuration combination must be checked and the precise loss shown.
- Already accepted runtime and wire direction: the daemon/broker owns actors and process trees;
  terminal windows are views, not process owners; one active lease owns input and resize while
  other clients are passive readers; a slow or absent view cannot block Stop, canonical append
  or recovery; a view is an authorized projection, not process ownership; the M1B message set
  uses opaque lease references and refusal reasons including `replay-gap-continuation`,
  `credit-exhausted`, `stale-lease` and `passive-client-input`; `PERF-010` fixes the 0/1/5/10/20
  view matrix and forbids view cost from multiplying model/worker calls, blocking canonical
  writes, causing unbounded memory, corrupting input, losing durable events or turning
  detach/reconnect into relaunch; and the optimisation rule `OR-024` ranks responsiveness,
  subscription efficiency then completion under correctness, authorization, resource and
  recoverability floors with no hidden scalar score.
- Already accepted plugin direction from [PLUGINS-AND-EDITIONS.md](../../PLUGINS-AND-EDITIONS.md)
  and [R-A](../dot-research-20261002/R-A-plugin-portability.md): plugins compose through a
  deterministic versioned capability graph and declare provided/required capabilities,
  exclusive resources and conflicts, configuration schema fragments, event subscriptions,
  process/isolation mode, filesystem/network/credential/model access, resource envelopes,
  lifecycle hooks and provenance; manifest resolution and policy checks occur before code import
  or installation; and disabled paths exclude code, network, model and context/tool enumeration.
- The delivered 2026-10-02c Prompt/Plugin/Skill architecture and shared-contract reconciliation
  companions (supplied research inputs, not repository paths) already establish the seven
  capability states, the `ArtifactRef`/`ContentEnvelope` provenance discipline and
  `authority_carried_none`. R-UI consumes that provenance discipline and must add the UI
  contribution-point taxonomy, deterministic materialization and fail-closed unknown-capability
  policy rather than re-deriving shared fields.
- Evidence status: no typed UI-contribution contract, capability-driven UI materializer,
  cross-client projection parity corpus or fail-closed unknown-capability path has been
  implemented or measured by Recursion for this lane. Every determinism, parity, security,
  accessibility, latency and resource statement below is to be established from public source,
  product documentation and a synthetic provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **capability-driven UI projection contract candidate** for Recursion.
The lane defines a typed, versioned UI-contribution surface attached to the accepted capability
graph; the contribution-point taxonomy (for example conversation/stream, work view, attention
inbox, artifact/inspector panel, command palette, status/continuity, notifications and settings)
with each point's contract and stability class; a deterministic materializer that turns the
effective capability set plus authorized projections into a client's UI tree; a fail-closed
unknown-capability and version-negotiation policy with typed loss reporting; the security
boundary for plugin-contributed UI (presentation only, no authority, no actor/process lifetime,
no credential custody, no second admission path, sandboxed and inert when disabled); and exact
parity with the ten controls and three Stops so every affordance is backed by a checked route/
interface/version/configuration combination rather than a rendered claim. It delivers a design
candidate with competing options, decisive falsifiers and an explicit statement of what it does
not prove. It does not select a language, store, framework, UI toolkit, renderer, transport or
vendor, does not qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, UI toolkit, renderer, transport,
wire encoding or vendor.** Do not decide an Owner question recorded in D-018, D-019, D-021,
D-022, D-024, D-031, D-033 or D-034. No provider, model or account call is made; no credential
or account is touched; no plugin is imported, installed or executed. Do not claim that a
contribution point, panel, badge, layout, tab or geometry confers authority, owns an actor or
process lifetime, or establishes that a control is supported. A rendered affordance is not
evidence of support; only a checked exact route/interface/version/configuration combination
with a declared loss is. Closing a view or client is a detach, never a Stop, and no
contribution may widen credential visibility (D-021). Do not assert that a capability-driven UI,
more contribution points or a richer layout improves performance, productivity, accessibility or
review effort without a measured experiment; each carries a competing option and a falsifier. No
claim of measured performance, accessibility conformance, UI conformance, security boundary
between views or porting cost is authorized.

## Inputs to read

None from this repository: the rescope, the accepted command-and-query, wire, interface,
terminal, performance, plugin and capability-graph requirements and the D-018 through D-034
context are summarized in `## Baked context` above, and no repository, connector or
private-source access is assumed. The session must, however, retrieve the public standards and
product documentation it cites — a JSON Schema 2020-12 reference and RFC 8785 canonical JSON for
the contribution schema and canonical identity; the current MCP tools/resources/prompts
specification for contribution-style capability declarations; the WCAG 2.2 recommendation and
its understanding documents for accessible contribution materialization; the platform
accessibility API documentation (for example Microsoft UI Automation, Apple accessibility and
Linux AT-SPI) where a GUI is compared; the WebView/embedded-content isolation documentation of
any candidate rich-view mechanism it cites; and any capability-negotiation or plugin-manifest
specification it proposes — and pin each claim to a URL and retrieval date. The delivered
2026-10-02c Prompt/Plugin/Skill architecture and shared-contract reconciliation companions are
inputs to build on, not repository links.

## Research questions

### Contribution-point taxonomy and schema

1. What is the exact set of typed UI contribution points a Recursion client recognizes, how is
   each named, versioned and namespaced, and which points are stable/normative versus
   client-local extension points that must not leak into the canonical contract?
2. What does each point's contract declare: required and optional inputs, the projection/query
   types it consumes, the commands it may invoke, its accessibility semantics, its resource
   envelope, its stability class and its degradation behavior when a client cannot render it?
3. How are contributions attached to the capability graph so a plugin declares UI
   contributions in its manifest with a supplying component and version, and so a contribution
   can never collide with a reserved first-party point or silently displace another provider?
4. How do contributions remain pure presentation: how is the boundary drawn so a contribution
   receives an authorized projection plus a typed command handle and never direct canonical-state
   access, a credential, a second admission path or actor/process ownership?

### Deterministic materialization

5. Given the same effective capability set and the same authorized projections, what makes a
   client's materialized UI tree deterministic and reproducible: canonical ordering, no
   model call on attach or render, no hidden indexing or plugin activation, and a declared
   materializer/schema revision?
6. How does the materializer resolve the effective set (installed, enabled, authorized,
   available, selected and supported-by-this-client) and reconcile it with the client's
   supported contribution points and versions without inventing semantics?
7. What is the effective-UI artifact (the resolved contribution set, the filled points, the
   omitted contributions with reasons, and the client capability profile) and how is it
   versioned, diffable and inspectable so a user or reviewer can see why the surface looks the
   way it does?
8. How does the materializer interact with the one versioned command-and-query model so a
   contribution's affordance and a CLI command have exactly one meaning and one admission path,
   and a contribution cannot define a competing action?

### Fail-closed unknown capabilities and degradation

9. What is the unknown-capability refusal policy: when a client encounters a contribution point,
   schema revision or capability it does not support, how does it fail closed (omit with a typed
   loss marker, refuse the protected action, or degrade to a documented fallback) rather than
   render a plausible but wrong affordance?
10. How is version negotiation conducted between a client capability profile and a contribution
    schema, and how are partial support, deprecated points and a required-but-unsupported
    contribution surfaced honestly?
11. How does the contract prevent a downgrade attack in which an unsupported or unknown
    contribution is silently ignored while its command remains reachable through another path,
    and what evidence proves that an omitted contribution is truly inert?
12. What accessibility and reduced-motion floor must survive degradation, so a client that cannot
    render a rich contribution still exposes the underlying fact or command through an
    accessible, non-color-only, keyboard-complete path?

### Plugin-contributed UI security

13. What sandbox/isolation boundary applies to a plugin-contributed UI contribution (rich view,
    embedded web content, native widget, terminal widget), such that a faulty or hostile
    contribution cannot read other projections, exfiltrate data, inject commands, spoof system
    status, steal focus destructively or corrupt terminal state?
14. How is the injection-safety discipline (`authority_carried_none`, untrusted content stays
    data, no authority from origin, no smuggled tool/agent/credential request through a UI
    manifest) enforced, and how are terminal-control sequences, OSC sequences, clipboard
    access, external URL opening and deep-link handling allowlisted?
15. How does a contribution prove it is inert when disabled: no code import, no process, no
    network, no credential access, no model turn, no indexing and no context/tool enumeration —
    and what provider-free fixture detects a violation rather than asserting inertness?
16. How are contribution lifecycle, capability revocation, stale contributions and cleanup
    handled so a revoked plugin's UI disappears immediately, its commands become unreachable and
    its cached view cannot act as a second writer?

### Parity with the ten controls and three Stops

17. How are each of the ten controls (streaming output, questions, approvals, queued messages,
    active steering, interruption, resume, forks, compaction controls, commands/plugins) exposed
    through the contribution contract with correct state semantics, exact target/scope and the
    precise loss when a route/interface/version lacks it?
18. How are the three Stops (Aggressive/Full/Lazy) and `checkpoint`/`interrupt`/`drain`
    represented with mode and scope visible, a persistent non-mouse-only affordance, no globally
    destructive Escape overload, and a truthful stopped-with-unresolved-effects disposition?
19. How does the UI present continuity and effect state as separate facts rather than one badge,
    show a replay `GAP` marker rather than an invented story, and keep a slow or absent client
    from blocking Stop, canonical append or recovery?
20. How is cross-client parity defined and checked — CLI, TUI, GUI and mobile resolving the same
    effective facts and the same command meanings with only declared presentation differences —
    and what would falsify the claim of no divergent semantics?

### Provider-free fixtures

21. What provider-free acceptance fixtures accept or reject the contract: identical materialized
    UI tree for frozen inputs; an unknown/unsupported contribution refused fail-closed; a
    disabled plugin contributing zero elements, commands and cost; a revoked contribution
    disappearing immediately; a contribution attempting direct canonical-state access refused;
    an injection/OSC/clipboard/deep-link violation rejected; parity of all ten controls and
    three Stops against the R-L model; and an N-contribution soak at 0/1/5/10/20 contributions
    under idle and high-output loads, with an exact pass/fail predicate for each?
22. How does the fixture suite prove that attaching, rendering or splitting a view adds no
    inference, indexing or plugin activation, that a slow client cannot block canonical state or
    Stop, and that cursor monotonicity and canonical-append/memory bounds hold at every
    contribution count?

## Deliverable

A capability-driven UI projection contract candidate containing: a **contribution-point
taxonomy** section with the typed, versioned, namespaced points and their stable versus
client-local classes; a **contribution schema** section defining the manifest attachment, the
declared inputs/projections/commands, the resource and accessibility envelopes and the
collision/reserved-point rules; a **deterministic materialization** section fixing the
effective-set resolution, canonical ordering, zero-model render, the versioned effective-UI
artifact and its diffability; a **fail-closed unknown-capability** section with version
negotiation, typed loss/omission, downgrade resistance and the accessibility floor under
degradation; a **plugin-contributed UI security** section with the sandbox/isolation boundary,
`authority_carried_none` enforcement, terminal/OSC/clipboard/deep-link allowlists and the
disabled-inertness properties; a **controls-and-Stops parity** section mapping all ten controls
and three Stops to inspected route/interface/version/configuration combinations with declared
losses and truthful continuity/`GAP` state; and a provider-free fixture suite with the
N-contribution soak. Each recommendation names a competing option, a decisive falsifier and what
it does not prove. No language, store, framework, UI toolkit, renderer, transport, wire encoding
or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, UI toolkit,
  renderer, transport, wire encoding or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that a contribution point, panel, badge, layout, tab or geometry confers
  authority, owns an actor or process lifetime, or proves a control is supported; a rendered
  affordance is not support, and closing a view or client is a detach, never a Stop.
- No new authority store, second admission path or prompt-only security boundary; no imported
  or plugin-contributed content acquires authority from its origin.
- No claim that a capability-driven UI, more contribution points, a richer layout or animation
  improves performance, productivity, accessibility or review effort without a measured
  experiment; each carries a competing option and a falsifier (D-031, D-034).
- No provider, model, credential or account call; no plugin imported, installed or executed; no
  toolkit installed or run; every fixture is synthetic and provider-free.
- No assertion that porting an existing UI/extension contribution model is cheap; it remains a
  hypothesis with a falsifier (D-033).
- No new executive tier, no separate AI "ARM manager", and no second portfolio executive created
  by a contribution, panel or client.
- No reopening of D-018, D-019, D-021, D-022, D-024, D-031, D-033 or D-034, and no reopening of
  the accepted requirements in `INTERFACE-STRATEGY.md`, `TERMINAL-RUNTIME.md`,
  `M1B-WIRE-PROFILE.md`, `PERFORMANCE-PLAN.md` or `PLUGINS-AND-EDITIONS.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The contribution-point taxonomy defines typed, versioned, namespaced points with stable versus
  client-local classes and a declared degradation behavior for each, and forbids collisions with
  reserved first-party points.
- The contribution schema attaches to the capability graph with supplying component and version,
  declares the consumed projections and permitted commands, and keeps contributions pure
  presentation with no direct canonical-state access, credential custody, second admission path
  or actor/process ownership.
- The deterministic-materialization section fixes effective-set resolution, canonical ordering,
  a zero-model render with no hidden indexing or plugin activation, and a versioned diffable
  effective-UI artifact naming filled and omitted contributions with reasons.
- The fail-closed section defines unknown-capability and version negotiation with typed
  loss/omission, downgrade resistance, inertness of omitted contributions and an accessible
  keyboard-complete non-color-only floor under degradation.
- The security section defines the plugin-UI sandbox/isolation boundary, enforces
  `authority_carried_none` for imported/contributed content, allowlists terminal/OSC/clipboard/
  deep-link behavior, and states disabled-inertness as checkable properties with a violation
  fixture.
- The controls-and-Stops parity section maps all ten controls and three Stops (plus
  `checkpoint`/`interrupt`/`drain`) to inspected route/interface/version/configuration
  combinations with visible scope and declared losses, presents continuity and effect state as
  facts, shows `GAP` as a marker, and keeps a slow client from blocking Stop, canonical append
  or recovery.
- The provider-free fixture suite specifies pass/fail predicates for deterministic
  materialization, fail-closed unknown capability, disabled/revoked contribution inertness,
  direct-access and injection violations, all-controls/all-Stops parity, and the
  0/1/5/10/20-contribution soak, and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not
  prove; no language, store, framework, UI toolkit, renderer, transport, wire encoding or vendor
  is selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured performance, no
  accessibility or UI conformance, no route qualification, no entitlement, no security boundary
  between views and no measured porting cost.
- Protected paths are untouched; privacy and secret scan are clean.

---
title: R-PC — Capability-driven prompt and context composition
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-PC — Capability-driven prompt and context composition

This is a composition-contract handoff for accepted Owner decisions D-018, D-019, D-022, D-024,
D-031 and D-034, with D-021 and D-033 as constraints, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It is the first of three handoffs that make D-034's
"scales with your workflow" thesis falsifiable: R-PC owns prompt/context composition, R-UI owns
UI projection, and R-MOB owns mobile/remote clients. It must extend, not restate, the delivered
2026-10-02c Prompt/Plugin/Skill architecture companion and the
[PLUGINS-AND-EDITIONS.md](../../PLUGINS-AND-EDITIONS.md) capability graph, consuming the accepted
[CONTEXT.md](../../CONTEXT.md) capsule, fidelity and governor contract and the effective-value
discipline in [CLI.md](../../CLI.md). It must not reopen accepted decisions or accepted
requirements.

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

- The exact thing to design: the **deterministic compiler that turns the installed capability
  set plus the GoalSpec into one versioned, inspectable effective prompt and context**. The
  "capability set" spans plugins, skills, configuration revision, route/execution profiles,
  node profiles and workspace/memory projections. The compiled output is the effective
  instruction/context artifact a route actually receives, with every segment attributable to
  an admitted source and every omission recorded.
- D-034 is the parent thesis: Recursion must grow **deterministically and without lock-in** as
  the user adds subscriptions, BYOKs, plugins, configurations, nodes and modding, "composing
  the effective system prompt and capabilities to fit the workflow." The thesis is claimed only
  if composition is reproducible, versioned, cache-aware and injection-safe, and if "scales" is
  measurable at fixed budget rather than "more is always better." D-034 names this exact
  research as commissioned, extending R-Q/R-L/R-O/R-A/R-W.
- D-018 makes Recursion a first-class native harness and a first-class unifying wrapper over
  the wider harness ecosystem; composition must therefore be broker-neutral and route-neutral,
  and must not encode one vendor's prompt, tool or cache semantics as the universal core.
- D-019 builds the comprehensive capability and plugin surface but ships every capability as an
  opt-in plugin or profile rather than a default. Installation, enablement, authorization,
  availability, selection, loading and execution are distinct facts; a capability present on
  disk is not automatically part of the prompt, and a disabled capability contributes no
  instruction, tool schema, resource or discovery cost, and performs no code import, network
  call, model turn or context/tool enumeration.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — **Aggressive / Full / Lazy** — plus `checkpoint`, `interrupt` and `drain`.
  Composition must respect this vocabulary: a `checkpoint` produces a validated durable
  manifest of the exact composed context and its bindings; a Stop fences new dispatch without
  silently rewriting the compiled context; and no interrupt, socket close or killed process is
  read as external rollback.
- D-024 makes productive continuity the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting. Composition must preserve canonical
  control references outside lossy summaries, recompile against current authority after
  compaction or route change, and present saved-locally / accepted / delivered / observed /
  settled as distinct facts rather than one optimistic badge.
- D-031 forbids a vendor-sabotage claim and any unmeasured savings claim. No composition,
  cache, retrieval or "smaller prompt" result may be presented as a saving without a measured
  per-workload resource vector.
- D-021 requires delegation over credential intermediation: the composed prompt and any
  discovery/selector step must never carry, copy, relay or widen credential visibility, and an
  upstream adapter may exercise only the prompt/tool/compaction controls its exact qualified
  profile supports.
- D-033 keeps porting strictly a hypothesis: any claim that an existing prompt/plugin/skill
  loader can be ported cheaply carries a falsifier and measured cost.
- Already accepted, non-negotiable direction this lane must respect rather than relitigate: the
  privileged kernel owns identity/authority verification, GoalSpec and Owner-intent integrity,
  event ordering and canonical writes, budget inheritance, leases, PAUSE/revocation, evidence
  admission, publication and plugin capability enforcement; plugins compose through a
  deterministic versioned capability graph, not by mutating global behavior; resolution
  produces a cached graph and a complete rejection explanation and fails cycles, incompatible
  ownership, ambiguous providers and missing dependencies before autonomous work starts;
  discovery is lazy and bounded, and task-specific tool schemas and context enter a WorkPacket
  only after admission and within explicit context/resource budgets.
- Already accepted context direction from [CONTEXT.md](../../CONTEXT.md): an Execution Context
  Capsule is a manifest with a non-droppable control kernel (actor lineage, exact GoalSpec and
  Owner Intent references, task and acceptance gate, authority/privacy/egress/budget bounds,
  exact source/candidate identifiers, current checkpoint and blockers, output/evidence
  contract) plus configurable tiers; one deterministic context governor owns the authoritative
  compaction transition per route epoch; the Compaction Fidelity Contract requires that every
  active directive remains represented by exact reference, identifiers/digests resolve, omitted
  evidence stays rehydratable, contradictions survive, and the old epoch remains available
  until the new one is accepted; provider-side prompt/KV caches and Recursion-owned semantic
  artifacts are different caches, and a cache hit can never validate a grant, freshness or
  subscription debit; cache-aware compilation keeps invariant instructions and schemas in
  stable prefixes, orders stable artifacts before volatile task state where provider semantics
  reward prefix reuse, uses canonical serialization, references unchanged artifacts by stable
  digest, isolates volatile timestamps/counters from reusable prefixes, and records observed
  cache evidence rather than estimating it as fact.
- Already accepted configuration direction from [CLI.md](../../CLI.md): requested, compiled and
  effective settings differ; preference propagation has two modes; immediate authority
  revocation cannot wait for a preference checkpoint; the deterministic semantic validator
  resolves scope and emits effective value plus provenance for every field; canonical
  serialization and digest precede comparison; and the TUI renders from the same schema, so
  widget state is never canonical.
- The delivered 2026-10-02c Prompt/Plugin/Skill architecture companion (a supplied research
  input, not a repository path) already establishes: seven independent capability states
  (installed, enabled, authorized, available, selected, loaded, executed); a small versioned
  behavioral core plus a task-scoped compiler; provenance-bearing references rather than a new
  global control object; discovery alternatives (eager admitted baseline, complete eligible
  metadata catalog, selective retrieval, explicit task profile) with their failure modes; three
  retention classes for compaction (exact canonical control, active procedure binding,
  compressible work evidence); and an invalidation matrix. R-PC consumes those candidate
  dimensions and instrumented resource vector; it must add the **effective-prompt artifact,
  deterministic versioning, cache-prefix contract, precedence rules and the falsifiable
  fixed-budget scaling experiment** rather than re-deriving them.
- Already accepted evaluation and performance direction this lane depends on: R-W owns
  independent verification, benchmark science and the disposition vocabulary; R-O owns the full
  resource vector, budgets, statistics and the complete-profile confirmation; R-Q owns the
  memory/knowledge projection boundary; R-A owns the plugin manifest and capability-graph
  portability contract. R-PC defines the composition-facing questions they must answer.
- Evidence status: no capability-driven prompt compiler, stable-prefix cache contract,
  precedence engine or fixed-budget scaling experiment has been implemented or measured by
  Recursion for this lane. Every determinism, quality, latency, resource, cache and review-effort
  statement below is to be established from public source, product documentation and a synthetic
  provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **capability-driven prompt and context composition specification
candidate** for Recursion. The lane defines the deterministic compiler from the effective
capability set (plugins, skills, configuration revision, route/execution profiles, node
profiles, workspace and memory projections) plus the GoalSpec to one versioned effective
prompt/context artifact; the exact inputs, passes, ordering and recompilation triggers; the
determinism and versioning discipline (canonical serialization, content-addressed digest,
reproducible reproduction, declared transform identity); the stable-prefix / append-only cache
contract and its provider-specific invalidation rules; a span-to-source provenance map that
keeps every segment attributable and marks imported or model-derived content
`authority_carried_none`; the conflict and precedence rules (authority conflict, procedural
conflict, evidence conflict) with a deterministic composition policy; injection-safety
boundaries between trusted control and untrusted content; and a **falsifiable fixed-budget
scaling experiment** that measures quality, latency, resources and review effort as
capabilities are added at a frozen budget. It delivers a design candidate with competing
options, decisive falsifiers and an explicit statement of what it does not prove. It does not
select a language, store, framework, serialization format, retrieval technology, model or
vendor, does not qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, serialization or schema format, retrieval
technology, transport, model or vendor.** Do not decide an Owner question recorded in D-018,
D-019, D-021, D-022, D-024, D-031, D-033 or D-034. No provider, model or account call is made;
no credential or account is touched; no plugin is imported, installed or executed. Do not claim
that a composed prompt, a stable prefix, a cache hit or "more capabilities" improves quality,
latency, cost or subscription efficiency without a measured fixed-budget experiment; each such
claim carries a competing option and a falsifier. Do not claim that a retrieval or catalog
result proves a capability is present, absent or safe. Do not let the compiler become a second
authority store: canonical rights, grants and fences resolve at admission and dispatch, and no
composed text, summary, cache entry or loaded skill body can authorize an effect. Imported
model output and imported content stay data or proposals regardless of wording. No claim of
measured determinism, cache savings or preference advantage is authorized.

## Inputs to read

None from this repository: the rescope, the accepted capability-graph, capsule, fidelity,
configuration, wire, performance, interface and evaluation requirements and the D-018 through
D-034 context are summarized in `## Baked context` above, and no repository, connector or
private-source access is assumed. The session must, however, retrieve the public primary sources
it cites — the current OpenAI, Anthropic and other provider prompt-caching, tool-definition,
tool-search/deferred-tool and compaction documentation; the Agent Skills specification and
client-integration guide; the MCP 2026-07-28 tool/resource/prompt specifications; RFC 8785
(JSON Canonicalization Scheme) and a JSON Schema 2020-12 reference for canonical serialization
candidates; and peer-reviewed context/retrieval evaluations such as the Lost in the Middle line
of work — and pin each claim to a URL and retrieval date. The delivered 2026-10-02c
Prompt/Plugin/Skill architecture companion is an input to build on, not a repository link.

## Research questions

### The deterministic composition pipeline

1. What is the exact input set for one composition pass — GoalSpec and task/gate references,
   accepted directives, current authority/privacy/egress/budget fences, effective configuration
   revision, route assignment and `RouteCapabilityDescriptor` identity, plugin/skill/
   dependency-lock identities, node/execution profile, workspace and memory projections, and
   context/resource allowance — and how is a coherent read cut captured and bound to those
   identities rather than a generic timestamp?
2. Which passes compose them in order (capture cut, resolve the eligible graph deterministically,
   determine the mandatory closure, retrieve optional candidates, admit exact content and tool
   disclosures, render the route-specific candidate, check fit and current applicability,
   dispatch through existing admission), and at which pass can a step be zero-model, bounded or
   refused rather than silently truncated?
3. How is the mandatory closure protected from budget pressure so a recommendation or ranking
   step can never remove an explicitly required instruction, skill or dependency, and how is an
   unfittable required context handled (preapproved narrower phase or typed blocker) instead of
   silent truncation?
4. What is the effective-prompt artifact itself: the serialized representation, its segments
   and roles, its declared ordering constraints, its segment-to-source map, its tool-binding
   set, its loss record and its content identity — and how is it kept immutable for its context
   epoch?

### Determinism and versioning

5. What makes composition deterministic and reproducible: the exact declared inputs, the
   pinned transform/compiler revision, canonical serialization, digest computation and the
   rule that generated summaries retain actual output identity rather than claiming seed-based
   reproducibility?
6. Which changes force a newly checked candidate or a typed hold rather than an in-place
   mutation (skill/dependency bytes, tool schema or endpoint, route/model/harness, source fork
   or workspace change, current grant/audience tightening, configuration revision, an omitted
   active reference), and how does the one authoritative context governor own the transition?
7. How are requested, compiled and effective states kept distinct and inspectable, and how does
   an immediate authority revocation fence affected reads/disclosures/effects without waiting
   for an ordinary preference checkpoint?
8. What does a `checkpoint` of the composed context contain, and how does it remain a validated
   durable manifest of directives, grants, epochs, interactions, queues, evidence, meters and
   unsettled effects rather than a transcript copy?

### Stable cache prefixes and cache-aware compilation

9. What stable-prefix contract can be specified without selecting a provider: invariant
   instruction and schema segments first, stable admitted artifacts ordered before volatile
   task state, canonical serialization and whitespace, digest-addressed references to unchanged
   artifacts, and isolation of timestamps/counters/route explanations from the reusable prefix?
10. For each provider class, what documented invalidation behavior constrains the prefix
    (tools-to-system-to-messages hierarchy, tool-definition ordering, append-only strategies,
    mid-conversation additions), how are provider session affinity and any explicit cache
    controls treated as provider-specific and continuously revalidated, and how is observed
    cache evidence recorded rather than estimated as fact?
11. How is the prefix contract reconciled with authority and correctness — never keeping a
    revoked tool callable to retain a prefix, never sorting conflicting procedural steps for
    cache convenience, never moving data into an instruction role for cache locality, and never
    preserving stale tool results merely for cache statistics?
12. What is the honest disposition when the same logical context recompiles to a changed prefix
    and forfeits a cache hit because an authoritative directive changed, and how is that cost
    reported as part of the full workflow rather than hidden?

### Provenance and injection safety

13. How is a span-to-source provenance map defined so every instruction, tool schema, resource
    or evidence segment is attributable to an admitted source, with its capability state,
    version/digest, recipient, purpose and loss?
14. How is `authority_carried_none` enforced for imported, model-derived and plugin-contributed
    content — descriptions, skills, `allowed-tools`, trust flags, system-looking tags and claims
    of prior approval remain data or requests until resolved against current canonical policy —
    and what separates the trusted control channel from the untrusted content channel?
15. How does the compiler avoid becoming an injection amplifier: least-privilege reads and
    outputs for selectors and compilers, sanitization for correct parsing that preserves
    original evidence rather than claiming text sanitation removes semantic influence, and a
    proposal-only path from any model-assisted selector into a more privileged consumer?
16. How is the injection defense evaluated against actual task correctness and disclosure as
    well as authority violations, and why is a prompt-only defense an intentionally inadequate
    negative control rather than a conforming alternative to canonical enforcement?

### Conflict and precedence rules

17. How are the three conflict classes resolved deterministically: **authority conflict** (a
    contribution requests a forbidden action or wider disclosure — denied independently of
    prompt obedience), **procedural conflict** (two valid contributions demand incompatible
    formats, step order or methods — resolved by explicit composition/precedence policy or a
    requested task decision, never last-loaded-wins), and **evidence conflict** (sources
    disagree — both provenance and uncertainty preserved, never smoothed into an accepted
    decision)?
18. What precedence order is defensible across sources (Owner directives and accepted
    decisions, the task control projection, the behavioral core, admitted workflow profiles,
    selected skills, imported content), how is it declared and versioned rather than inferred
    from filesystem order, and how are ambiguous providers or cycles refused before autonomous
    work?
19. How is composition policy made inspectable and reversible (why each segment was included or
    omitted, what a change would remove, how to preview a recompile), and how does this avoid a
    second settings database or hidden fallback?

### Falsifiable scaling at fixed budget

20. What exact experiment tests D-034's "scales with your workflow" claim: a frozen per-task
    budget with a preregistered capability-increment schedule (for example base, base+one
    plugin, base+one skill set, base+one node/profile, base+one route/config combination), the
    same accepted tasks, an independent quality oracle, and paired competing options (a
    complete eligible catalog; an eager admitted baseline; explicit workflow profiles)?
21. Which endpoints must the fixed-budget experiment report — qualified task success, wrong
    instruction/version, missed mandatory skill, forbidden disclosure, safe refusal, unresolved
    effects; latency p50/p95 (compile, first-event, verified outcome); context bytes and
    route-qualified tokens by segment; all reasoning roles including selectors, compactors,
    verifiers and retries; local CPU/memory/IO; observed cache reads/writes; and human
    corrections, missing-skill discovery and review effort — with resource per qualified success
    over the whole assigned cohort, zero successes undefined rather than zero, and unobserved
    counters null with reasons?
22. What is the decisive falsifier for the scaling thesis at each increment (quality or latency
    or authority degrades, or review effort grows super-linearly, or the composition is not
    reproducible, or integration tax exceeds the measured benefit), and how is NO_BENEFIT /
    HOLD_UNKNOWN / REGRESSION / CONDITIONAL_ADVANTAGE decided without a hidden scalar score?
23. What provider-free acceptance fixtures accept or reject the compiler: byte-identical
    reproduction for frozen inputs, a mandatory-closure item surviving budget pressure, a
    disabled capability contributing zero catalog/tool/context cost, a revoked capability
    fenced immediately while preferences await application, an `authority_carried_none`
    violation rejected, a procedural-conflict precedence case, a changed-directive cache-prefix
    forfeiture reported honestly, and an N-increment fixed-budget scaling run with an exact
    pass/fail predicate for each?

## Deliverable

A capability-driven prompt and context composition specification candidate containing: a
**composition pipeline** section defining the exact inputs, ordered passes, mandatory-closure
protection and fit/refusal behavior; a **determinism and versioning** section fixing canonical
serialization, content-addressed identity, declared transform revision, recompilation triggers,
requested/compiled/effective distinction and the immediate-revocation fence; a **stable cache
prefix** section fixing the invariant-prefix / stable-artifact / volatile-tail contract, its
provider-specific invalidation rules stated as continuously revalidated evidence, and honest
reporting of forfeited hits; a **provenance and injection safety** section defining the
span-to-source map, `authority_carried_none` enforcement, the trusted/untrusted channel split,
least-privilege selectors and the proposal-only path; a **conflict and precedence** section
resolving authority, procedural and evidence conflicts with a declared versioned precedence
order and inspectable/reversible policy; a **falsifiable fixed-budget scaling experiment**
section with a preregistered increment schedule, independent quality oracle, paired competing
options, the full resource vector, the disposition vocabulary and the per-increment decisive
falsifier; and a provider-free fixture suite. Each recommendation names a competing option, a
decisive falsifier and what it does not prove. No language, store, framework, serialization
format, retrieval technology, model or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox,
  serialization/schema format, retrieval or embedding technology, transport, model or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No new authority store and no prompt-only security boundary: a cache hit, summary, loaded
  skill body or model-assisted selection never authorizes a read, disclosure or effect, and no
  imported content acquires authority from its origin.
- No claim that a composed prompt, stable prefix, cache reuse, catalog strategy or "more
  capabilities" improves quality, latency, cost or subscription efficiency without a measured
  fixed-budget experiment; each carries a competing option and a falsifier (D-031, D-034).
- No provider, model, credential or account call; no plugin imported, installed or executed; no
  binary installed or run; every fixture is synthetic and provider-free.
- No assertion that porting an existing prompt/plugin/skill loader is cheap; it remains a
  hypothesis with a falsifier (D-033).
- No new executive tier, no separate AI "ARM manager", and no second portfolio executive created
  by a compiler, selector or profile.
- No reopening of D-018, D-019, D-021, D-022, D-024, D-031, D-033 or D-034, and no reopening of
  the accepted requirements in `CONTEXT.md`, `PLUGINS-AND-EDITIONS.md`, `CLI.md`,
  `M1B-WIRE-PROFILE.md` or `PERFORMANCE-PLAN.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The composition pipeline defines the exact input set, a coherent read cut, the ordered passes,
  zero-model/bounded/refused dispositions and mandatory-closure protection against budget
  pressure, with a typed blocker or preapproved narrower phase instead of silent truncation.
- The determinism and versioning section fixes declared inputs, pinned transform revision,
  canonical serialization, content-addressed identity, the rule that generated summaries retain
  actual output identity, recompilation triggers, the requested/compiled/effective distinction,
  the immediate-revocation fence and the validated `checkpoint` manifest.
- The stable-prefix section fixes the invariant/stable/volatile ordering and invalidation
  contract, treats provider cache controls as provider-specific evidence to revalidate, forbids
  authority- or correctness-eroding cache tactics and reports forfeited hits honestly within the
  full workflow.
- The provenance and injection-safety section defines a span-to-source map, enforces
  `authority_carried_none` for imported/model-derived content, separates trusted control from
  untrusted content, keeps selectors least-privilege and proposal-only, and evaluates actual
  task correctness and disclosure as well as authority violations.
- The conflict and precedence section resolves authority, procedural and evidence conflicts with
  a declared versioned precedence order, refuses ambiguous providers/cycles, and makes
  composition policy inspectable and reversible without creating a second settings database.
- The scaling section specifies a reproducible fixed-budget experiment over a preregistered
  capability-increment schedule with an independent quality oracle, competing options, the full
  resource vector (quality, latency, context/tokens, all reasoning roles, local resources,
  observed cache counters, review effort), resource per qualified success with zero undefined,
  and a per-increment decisive falsifier and disposition rule with no hidden scalar score.
- The provider-free fixture suite specifies pass/fail predicates for byte-identical
  reproduction, mandatory-closure survival, disabled-capability zero cost, immediate revocation
  fencing, an `authority_carried_none` violation, a procedural-conflict precedence case, a
  changed-directive prefix forfeiture, and an N-increment scaling run, and no fixture requires a
  provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not
  prove; no language, store, framework, serialization format, retrieval technology, model or
  vendor is selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured determinism, no
  measured quality/latency/resource/cache/subscription advantage, no route qualification, no
  entitlement, no security boundary and no measured porting cost.
- Protected paths are untouched; privacy and secret scan are clean.

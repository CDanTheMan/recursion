---
title: R-CS — Control-surface and competitor study
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-CS — Control-surface and competitor study

This handoff serves accepted Owner decisions D-018 (no ecosystem lock-in), D-023 (Codex App Server
is the first qualification priority), D-030 (harness-native driving plus headless fan-out), D-031
(no vendor-sabotage or unmeasured-savings claim), D-034 (the scaling thesis) and D-035 (plugins live
outside the core), with the gap register in [GAPS.md](../../research-lane/GAPS.md). It is paired
with [R-LANG](R-LANG-core-language-and-architecture-reconstruction.md), the core language and
architecture-reconstruction lane. It is a **competitive and prior-art study of agent-harness control
surfaces and orchestrators** — the category Recursion also occupies — so Recursion's differentiation
on D-034 stays honest. It is not a feature-copy list and it never states what a competitor intends.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a small
deterministic kernel with typed adapters; native and upstream execution; persistent, goal-scoped
assistants organized as Head -> executives -> bounded workers; configurable context and compaction;
plugins and editions; an interactive detachable terminal; and Windows/Linux operation and recovery.

Authority: Lucas is the final owner. Recursion is a standalone agent harness and a harness
orchestrator that delegates through other harnesses. Hermes-led control was retired on 2026-09-28
(state/DECISIONS.md D-017); Hermes is an optional upstream integration, not the executive control
plane. An implementer's own PASS is never acceptance; independent review is required, and missing
verification is never a pass. `CONTROL_PLANE.md` is the operative constitution; a research session
may propose amendments but must never edit it. No research session performs implementation,
provider/model/authentication/configuration changes, spending, deployment, publication or merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula, captures
and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (a project's own repository, release notes,
documentation, license and issue tracker; official platform/vendor documentation; peer-reviewed
work). Classify every consequential claim as source-documented, locally observed, inferred or
unverified; keep `unknown` distinct from zero. Model consensus, marketing and popularity metrics are
not evidence. Attribute every claim to a named source and a retrieval date. Every recommendation
needs a competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never secrets,
credentials, personal data, private repository content, local paths, or account/infrastructure
identifiers.

### Lane context

- The exact thing to design: a **systematic, evidence-classed comparison of agent-harness control
  surfaces and orchestrators** that drive other harnesses, anchored on **T3 Code** (the public
  project `pingdotgg/t3code`, whose v0.0.45 release is dated 2026-10-02) and covering its peers and
  predecessors in the same category. The output informs Recursion's differentiation and its
  qualification priorities; it is not an implementation plan.
- Why T3 Code anchors the study: it publicly describes itself as an "agent harness control surface"
  that controls agents on the user's machine from mobile, web and desktop clients and works with
  subscriptions on several harnesses. Its public release notes are a dated, citable primary source.
- D-034 is the parent thesis: Recursion grows deterministically and without lock-in as the user adds
  subscriptions, BYOKs, plugins, configurations, nodes and modding; the moat named in D-034 is
  **deterministic composition plus authority, continuity, accounting and portability** — not routing
  or a client surface, which are table stakes in this category.
- D-018 requires no ecosystem lock-in: Recursion must remain a first-class native harness and a
  first-class wrapper, so competitor analysis must identify lock-in patterns to avoid, not features
  to copy.
- D-023 makes the Codex App Server the first qualification priority; competitors' handling of
  upstream harness versions and protocol changes is directly relevant evidence.
- D-030 adopts harness-native driving plus headless fan-out, with Recursion owning the JSON stream
  subject to counsel; competitors' delegation and protocol strategies are relevant evidence.
- D-031 forbids any vendor-sabotage claim and any unmeasured savings/perf claim. This lane must
  explain a competitor's documented behavior and consequences for Recursion **without** imputing
  intent, without claiming a competitor degrades or sabotages anything, and without transferring any
  performance or cost advantage into a Recursion claim.
- D-035 makes plugins external artifacts referenced by digest; competitor plugin/skill lifecycle
  models are relevant to the boundary Recursion has chosen, not a reason to reopen it.
- Evidence status: this lane is **public-source only** — no competitor product is downloaded,
  installed, executed or measured; no account, store or provider call is made. Anything not
  documented publicly is `unknown`. An initial internal note on T3 Code v0.0.45 exists in the
  research lane's competitive-notes area; the lane must independently verify and extend it from
  primary sources rather than relying on that note.

## Purpose

Produce the decision-ready **control-surface and competitor study** for Recursion: a sourced
inventory of the category; a deep, cited analysis of T3 Code; a cross-competitor view of plugin and
skill lifecycle, continuity and notification semantics, delegation/protocol handling,
quota-by-credential accounting, mobile stack choices and licensing; and a differentiation analysis
that separates table stakes from Recursion's claimed moat under D-034. Every claim carries an
evidence class, a pinned source and a retrieval date, and every recommendation names a competing
option, a decisive falsifier and what it does not prove. It selects no technology and states no
legal conclusion.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, framework, runtime, store, transport, push provider, authentication mechanism or vendor,
and do not copy or propose copying any competitor's code, schema, assets or proprietary design.**
Do not decide an Owner question recorded in D-018, D-023, D-030, D-031, D-034 or D-035, and do not
reopen D-019, D-022, D-024, D-028, D-033 or D-039. No competitor product is downloaded, installed,
run, benchmarked or reverse-engineered; every observation is from public documentation, release
notes, repositories or licenses. **Make no vendor-intent or vendor-sabotage claim (D-031)** and
transfer no competitor performance or cost figure into a Recursion claim. Do not state a legal or
license conclusion; licensing and distribution matters are questions for counsel. Do not claim that
porting a competitor's plugin, client or design is cheap (D-033).

## Inputs to read

None from this repository: the D-018 through D-039 context and the category framing are summarized
in `## Baked context` above, and no repository, connector or private-source access is assumed. The
session must retrieve and cite the public primary sources it relies on and pin each claim to a URL
and retrieval date, including: the T3 Code public repository README, release notes (in particular
the v0.0.45 release dated 2026-10-02 and adjacent nightlies/previews), documentation and license;
the public documentation, repositories, release notes and licenses of a fair set of peer and
predecessor control surfaces and orchestrators, and of the upstream harnesses they drive; and any
published design notes the projects themselves provide. Treat every product as prior art cited from
public documentation, not as an endorsed or selected component. Where a project is only documented
by marketing or third parties, mark the claim inferred or unknown rather than source-documented.

## Research questions

### Landscape and definitions

1. How should the category "agent-harness control surface / orchestrator" be defined precisely, and
   which public projects occupy it, control which upstream harnesses, ship which client surfaces
   (CLI, TUI, web, desktop, mobile), and are open source under which license?
2. What architecture patterns recur across the category (local agent/server, per-machine runtime,
   control-plane over harness sessions, hub-and-spoke, peer/remote), and what does each pattern make
   easy or hard for authority, continuity and accounting?

### T3 Code deep dive

3. What is T3 Code's documented architecture — how a local server/service layer, clients and
   per-provider integrations are described publicly — and what does that imply about where session
   state, credentials and authority live?
4. How does T3 Code's documented plugin and skill lifecycle work, specifically the v0.0.45 change
   that restarts the agent session to load new skills and plugins; is it hot-reload or
   restart-based, and what are the consequences for disabled-inertness, trust and versioning?
5. How does T3 Code present continuity and notification state publicly — per-thread alerts, agent
   Live Activity staleness, Android subscription widgets — and how are "delivered" versus
   "completed" versus "needs you" distinguished, if at all?
6. What is documented about provider/version tracking and resilience (for example regenerating
   protocol bindings for a named Codex version, marking a provider CLI version broken, recovering
   from crashed provider sessions), and what does that reveal about maintaining route descriptors?
7. What is documented about quota and credential handling (for example merging a provider's limits
   by credential), and what does it imply for provider-neutral accounting and BYOK?
8. What client stack choices are documented (for example a cross-platform mobile stack and OS
   integrations), and what do the project's own notes say about tradeoffs, without copying them?

### Cross-competitor patterns

9. How do peers handle plugin/skill lifecycle (hot reload versus restart, manifest-before-import,
   disabled inertness, trust/signing) and what is the decisive falsifier for each pattern?
10. How do peers handle continuity, detach, reattach and Stop, and how do they present unresolved or
    uncertain outcomes — with sources and without imputing intent?
11. What mobile client stacks and OS integrations do peers use, and what evidence exists about
    native versus cross-platform choices (this informs, but does not decide, D-039)?
12. What licensing, governance and openness terms apply to each studied project, and what questions
    must go to counsel before any design could be reused, without stating a legal conclusion?

### Differentiation for Recursion

13. Which capabilities are table stakes in this category (routing, a client surface, plugins) versus
    Recursion's claimed moat under D-034 (deterministic reproducible composition, authority,
    productive continuity, honest accounting, portability), and where would Recursion be
    undifferentiated if it only matched peers?
14. What could Recursion learn **conceptually** from the category (patterns, failure modes, open
    problems) without copying code or design, each with a competing option, a decisive falsifier and
    what it does not prove?
15. What analysis method and threats to validity apply (marketing claims, popularity metrics,
    survivorship bias, version churn), and what public evidence would change a conclusion?

## Deliverable

A control-surface and competitor study containing: a **landscape inventory** with definitions,
covered harnesses, client surfaces and licenses, each sourced and dated; a **T3 Code deep dive**
covering architecture, plugin/skill lifecycle, continuity and notification semantics, provider
versioning/resilience, quota/credential handling and client stack choices, each pinned to a public
source; a **cross-competitor comparison matrix** for lifecycle, continuity/Stop, mobile stack and
licensing with an evidence class per cell and `unknown` where undocumented; a **differentiation
analysis** separating table stakes from Recursion's D-034 moat; a **learning list** of conceptual
patterns with rivals, falsifiers and non-proofs; and a **licensing/counsel questions** section stated
as questions. No technology is selected, no vendor intent is claimed, and no legal conclusion is
drawn.

## Non-goals

- No installation, execution, benchmarking, reverse-engineering or account/store/provider call for
  any competitor; observations are from public documentation only.
- No copying or proposing to copy any competitor's code, schema, assets or proprietary design.
- No vendor-intent or vendor-sabotage claim and no transfer of a competitor's performance, cost or
  savings figure into a Recursion claim (D-031).
- No selection of a language, framework, runtime, store, transport, push provider, authentication
  mechanism, license or vendor.
- No legal or license conclusion; licensing and distribution are counsel questions.
- No claim that porting a competitor's plugin, client or design is cheap (D-033).
- No reopening of D-018, D-019, D-022, D-023, D-024, D-028, D-030, D-031, D-033, D-034, D-035 or
  D-039.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The landscape inventory names the category's public projects, the harnesses they control, their
  client surfaces and their licenses, each with a source and retrieval date, and defines the
  category precisely.
- The T3 Code deep dive verifies against primary public sources, with citations and dates, the
  v0.0.45 (2026-10-02) specifics: the plugin/skill session-restart change, notification/continuity
  behavior, provider-version tracking/resilience, quota-by-credential handling and client stack
  choices; undocumented points are marked `unknown`.
- The cross-competitor matrix covers plugin/skill lifecycle, continuity/Stop, mobile stack and
  licensing, with an evidence class per cell and sources.
- The differentiation analysis separates category table stakes from Recursion's D-034 moat and
  states where Recursion would be undifferentiated by matching peers alone.
- The learning list gives conceptual patterns, each with a competing option, a decisive falsifier
  and what it does not prove; nothing is copied.
- Licensing/counsel matters are stated as questions, with no legal conclusion.
- Every consequential claim carries an evidence class and a pinned source, and `unknown` is kept
  distinct from zero; no vendor-intent or vendor-sabotage claim and no transferred performance or
  savings figure appears (D-031).
- No language, framework, store, transport, push provider, authentication mechanism or vendor is
  selected, and no competitor is installed, executed or benchmarked.
- The candidate explains what it does not establish: no measured competitor or Recursion
  performance, no security or eligibility finding, no legal conclusion and no porting cost.
- Protected paths are untouched; privacy and secret scan are clean.

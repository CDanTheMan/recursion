---
title: Recursion standalone harness foundation and GRILLME research handoff
status: ready-for-owner-invocation
last-updated: 2026-09-05
---

# Recursion standalone harness foundation and GRILLME research handoff

Run this prompt as GPT-6 Astra with Deep Research, private repository access, and local
Git read/write tools. This file prepares a future research campaign; creating or reading
it does not launch that campaign. Lucas's explicit instruction to execute this prompt
authorizes the bounded research, documentation synthesis, validation tooling, and local
commits below. It does not authorize product implementation or live-system changes.

## Objective and decision

Determine whether Recursion's current v3 contracts form a coherent, extensible foundation
for a standalone autonomous-development harness serving developers/power users, casual
users seeking plug-and-play operation, and eventually enterprise users. Reconcile the
Owner's ideas below with the actual repository, current upstream interfaces, scientific
evidence, and measurable limitations. Expand the repository into a durable reference
that supports a subsequent GRILLME session and bounded autonomous construction.

The decision is what must be clarified before formal-model freeze, what is already
specified adequately, what needs a later experiment, and what should be deferred or
rejected. Do not optimize for agreement with the Owner's technical assumptions, a large
report, a fashionable architecture, or a predetermined claim of industry leadership.
Ambitious product goals are welcome; factual claims and implementation choices must earn
their status through evidence.

Use existing research before opening new lanes. Preserve the recommended sequence:
focused integration-contract audit -> bounded formal model -> language-neutral vectors
and CPython/Rust/Go comparison -> JSONL/CAS versus SQLite-WAL/CAS fault comparison ->
canonical-state construction -> remaining accepted milestones. Recommend a different
dependency only with a concrete counterexample and an explicit Owner decision.

For each finding, distinguish a prerequisite for the existing formal-model experiment,
an adapter/interface accommodation, a later optimization experiment, and a deferred
product extension. Use the formal-model obligations in the existing tranche-two evidence
as the reference; flag any proposed change to their authority, replay, effect, lease,
pause, or liveness assumptions before recommending construction. Do not reopen completed
M1 work merely to restate its conclusions.

## Authority, environment, and campaign boundary

Lucas is principal and final authority. CONTROL_PLANE.md remains operative; Hermes
remains the executive control plane and portfolio owner. Astra is the research lead,
sole integrator, and sole writer for this campaign. The ratified future Recursion Head
and goal-scoped ARM design does not transfer current authority.

Before planning, read CONTROL_PLANE.md first, every effective CLAUDE.md and AGENTS.md
instruction, then ANCHOR.md.
Inspect the real repository and its WIP worktree. The prepared target is:

- repository: the existing Recursion Git repository;
- review/WIP branch: `codex/v3-formal-model-experiment`;
- worktree: the existing dedicated worktree registered for that branch;
- verified remote baseline on 2026-09-05: `a7cd9458d37f3090079930bf8d79ffd77c4f73e4`;
- parent goal: `goal-recursion-v2-execution-fabric`, specifically its provider-neutral
  control-plane outcome, under the already ratified v3 Option 2 direction;
- research GoalSpec identifier: `recursion.v3.foundation.research.20260905`.

The parent link scopes this research contribution. It does not change the parent's v2
acceptance suite, complete that goal, or create a new portfolio project. Confirm the
parent record remains applicable; a retired/conflicting parent requires an Owner/Hermes
binding before campaign admission.

Fetch origin/master, resolve the WIP branch through `git worktree list --porcelain`,
and record the full current invocation HEAD as `start_commit`. Check ancestry, branch
ownership, worktree cleanliness, PAUSE, disk/RAM/CPU responsiveness, available tools,
quota, and route eligibility. Preserve the older main checkout and unrelated files.
Do not reset, rebase, merge, clean, stash, prune, or switch another session's worktree.
A moved remote is an input to compatibility review, not permission to rewrite history.
If the target is occupied, dirty with unrelated work, or materially divergent, report
the exact blocker and request an exclusive compatible target. Never invent a replacement
WIP branch. Check any known operational PAUSE separately; absent local PAUSE does not
establish remote deployment state. Follow the operative PAUSE rules.

Create one concise campaign record before substantive research. Freeze Owner intent
provenance, parent, GoalSpec, `start_commit`, required ancestors, allowed paths, input
digests, expected outputs, budget, routes, gates, falsifiers, and non-goals. Record output
digests as artifacts become available. PlanRevisions are append-only
and identify retained, invalidated, quarantined, and superseded work. Do not silently
rewrite GoalSpec semantics through a PlanRevision; a material goal change needs Owner
acceptance of a new version. Treat this prompt and invocation as immutable inputs.

Initial execution envelope: one bounded six-hour research session, zero new metered
spend, existing included capacity only, at most four concurrent discovery workers,
30 minutes per discovery packet, and reserved time/capacity for synthesis and independent
review. Stop earlier when evidence converges. At the time limit, commit an explicitly
incomplete, resumable research checkpoint and report remaining gaps; do not inflate it
into a completed campaign. A tighter host/session/Owner limit wins.

Only these paths may change, relative to the verified worktree:

- `docs/v3/foundation-research/**`;
- `docs/v3/README.md`;
- `docs/v3/PRODUCT.md`, `ARCHITECTURE.md`, `EXECUTIVES.md`, `EXECUTION-FABRIC.md`;
- `docs/v3/PLANNING.md`, `CLI.md`, `TERMINAL-RUNTIME.md`, `INTERACTION-SURFACES.md`;
- `docs/v3/CONTEXT.md`, `PLUGINS-AND-EDITIONS.md`, `SECURITY.md`, `TELEMETRY.md`;
- `docs/v3/PERFORMANCE-PLAN.md`, `ACCEPTANCE.md`, `ROADMAP.md`, `CONSTRUCTION-RUNBOOK.md`;
- `docs/v3/DECISION-REGISTER.md`, `CLAIM-LEDGER.md`, `CLAIM-REGISTRY.json`;
- `docs/v3/SOURCE-REGISTER.md`, `ROUTE-CAPABILITIES.md`, `RESEARCH-HYPOTHESES.md`.

In the grouped entries, every filename is directly under `docs/v3/`. Everything else
is read-only, including this prompt, all M1A/M1B/M1C contracts, schemas, fixtures, tests,
receipts, existing production code, scripts, state, the constitution, ANCHOR, environment
files, configuration, credentials, auth, model/provider routing, services, and cron.
New code is permitted only as local documentation-validation tooling under the new
research directory. No runtime, prototype, benchmark implementation, live provider
probe, model-cache keepalive, node enrollment, source-account login, private canary,
migration, deployment, or external effect is authorized. Public research retrieval and
explicitly admitted research/reviewer routes are the only research egress exceptions.

Use repository-capable Astra for the complete workflow. If a Deep Research surface has
only web/read-only connectors, report that limit immediately, continue eligible public
research, and return a provenance-bearing handoff or patch for a repository-capable
session. Do not claim private inspection or commits that the tools cannot perform.
Do not create another task, enable a route, or change the selected model to work around
missing capabilities without the required Owner instruction.

## Verified repository starting facts and reading map

These facts were checked against the baseline above. Recheck them at invocation; Git
and executable artifacts outrank stale milestone prose.

| Slice | Reviewed implementation candidate | Terminal receipt commit | Evidence boundary |
|---|---|---|---|
| M1A | `fb0e04584a402b659560b64591706beb18082a72` | `0960481683e2b17ff213a824bbd4b4d559f1c91a` | Pure planning validation, packet derivation and in-memory replay; historical same-provider Terra review |
| M1B | `0f1bd5f9fd4f32acf9718930f67101983216c5a3` | `99a10f6c94f28305aa83d4444d8ebb32218a51ae` | Inert route/plugin/process/broker requirements and 24 literal cases; historical SOL review |
| M1C | `8cd1c8ef574b0e375000d7c68d133404928308cf` | `338ea91f4aab531c95b47d83bd74cf279ab3aa83` | Inert evidence/effect/publication/state/retention requirements and 24 literal cases; historical SOL review |

All six commits were ancestors of the merged M1C baseline. The three implementation/test
directories were unchanged from their reviewed candidates and their schema/fixture-manifest
hashes matched their receipts. This is historical source evidence, not a fresh test run,
production deployment, cross-provider verification, or a functioning v3 runtime.

Repository facts that the synthesis must preserve or challenge explicitly:

- OR-018 selects the small deterministic kernel with typed adapters. OR-019 gives the
  versioned Recursion release sole canonical authority/recovery ownership in the future
  product. An expanded native agent loop, language, and physical store remain unselected.
- CLI.md already requires schema-driven zero-model setup and configuration. An optional
  agent-assisted `/setup` must be researched as a compatible addition or a proposed change.
- TERMINAL-RUNTIME.md already specifies interactive detachable views, daemon-owned state,
  broker-owned processes, bounded streams, and native Windows/Linux acceptance.
- CONTEXT.md already specifies non-droppable control state, configurable context tiers,
  native/Recursion compaction coordination, fidelity checks, and project-scoped evidence.
  Treat proposed defaults as proposals; no comparative benefit is established.
- EXECUTIVES.md separates logical role, model escalation, provider failover, delegation,
  authority escalation, and lease-holder replacement. No extra AI ARM Manager exists.
- PLUGINS-AND-EDITIONS.md already specifies versioned manifests, independent grant
  dimensions, staged/fenced reload, disabled-path limits, and adapter-free core recovery.
- OR-015's broad execution-attempt/lease migration rehearsal remains blocked by the
  incomplete common writer fence. M1C's fabric-only fixtures do not remove that blocker.
- The three-audience ambition is research input, not evidence of product-market fit,
  enterprise demand, a new commercial tier policy, or changed near-term priorities.
- Current Hermes authority, immediate PAUSE, protected publication, and independent
  verification remain operative. Future sovereignty or PAUSE proposals do not activate them.

Read, in order, after the authority files:

1. [README](../README.md), [ROADMAP](../ROADMAP.md), and [CONSTRUCTION-RUNBOOK](../CONSTRUCTION-RUNBOOK.md).
2. [ARCHITECTURE](../ARCHITECTURE.md), [DECISION-REGISTER](../DECISION-REGISTER.md),
   [CLAIM-LEDGER](../CLAIM-LEDGER.md), [ACCEPTANCE](../ACCEPTANCE.md), and
   [CURRENT-AND-MIGRATION](../CURRENT-AND-MIGRATION.md).
3. The [M1A](../M1A-CONSTRUCTION-CAMPAIGN.md), [M1B](../M1B-CONSTRUCTION-CAMPAIGN.md),
   and [M1C](../M1C-CONSTRUCTION-CAMPAIGN.md) construction campaigns and terminal receipts.
4. Relevant sections of [FRONTIER-HARNESS-EVIDENCE](../FRONTIER-HARNESS-EVIDENCE.md),
   [tranche-two evidence](../FRONTIER-HARNESS-RESEARCH-TRANCHE-2-EVIDENCE.md),
   [SOURCE-REGISTER](../SOURCE-REGISTER.md), and [VALIDATION](../VALIDATION.md).
5. Route each research lane to its smallest canonical set: PRODUCT/PLUGINS for audiences;
   ARCHITECTURE/EXECUTION-FABRIC/M1B for engines; CONTEXT/TELEMETRY/PERFORMANCE-PLAN for
   compaction/cache; CLI/TERMINAL-RUNTIME/INTERACTION-SURFACES for UX;
   EXECUTIVES/AUTONOMOUS-PLANNING/PLANNING for delegation and GRILLME;
   STATE/SECURITY/CURRENT-AND-MIGRATION/M1C for nodes, recovery, and evidence.

Inspect the corresponding schemas, pure code, or test oracles when a claim depends on
behavior. Do not load the archived session transcript or every document indiscriminately.
Record exact source paths, symbols, candidate hashes, and decisive checks. Preserve failed
candidates and material dissent already recorded in the campaigns.

## Owner ideas to investigate, not assume

Preserve the motivation behind each idea and assign it a stable campaign-local ID such
as `thought.cache.heartbeat`. Track every idea to a finding, proposal, experiment, deferred
question, or explicit rejection. Retain exact Owner messages by authorized private reference;
the summary below is a research map, not a replacement for the Owner Intent Ledger.

### A. Audiences, standalone value, and product coherence

Investigate developers/power users, casual users seeking plug-and-play operation, and
enterprise customers separately. The ambition is one versioned, extensible Recursion
product that makes serious autonomous work usable across these audiences.

For each audience, identify concrete jobs, first successful workflow, required knowledge,
trust and intervention expectations, acceptable setup friction, cost visibility, failure
recovery, support burden, and measurable success. Enterprise willingness to spend and
viral adoption are hypotheses, not demand evidence. Distinguish a solo installation,
an organization running its own instance, and a hosted multi-tenant service; do not assume
that the current single-authority-domain design already supplies all three.

Assess one common integrity/runtime foundation with configurable profiles and optional
capabilities. Map advanced needs such as identity federation, roles, secrets, audit/export,
tenant isolation, data residency, private networks, procurement and reproducible updates
to actual requirements and later decisions. Do not claim compliance certification.
Recommend which audience leads v3.0 and which architecture accommodations must exist now,
without silently changing the current Lucas-first deployment scope or edition policy.

### B. Harness inspirations and capabilities beyond today's baseline

Investigate these exact inspirations, resolving product names, repositories, versions,
source availability, and licenses before comparing them:

- OpenCode: polished CLI, broad BYOK, cache handling, and the Owner's claim that it leads
  the Artificial Analysis Harness Index with Opus 4.7.
- DeepSeek Harness: configurable plugin infrastructure, open-source design, and visibility
  into reasoning when a model/API explicitly exposes it.
- T3 Code: remote control, interactive surface, and routing through Codex, Claude, or others.
  Verify whether the relevant surface is a TUI, GUI, web client, or another interface.
- Cursor: immediate visibility into agent actions, polished interaction, compaction, and
  understandable, shareable demonstrations of real work.
- Hermes Agent: sustained autonomous work and Telegram/other remote transports; investigate
  the Owner's negative cache/token-efficiency impression instead of treating it as measured.

Verify the benchmark's exact name, date, harness/model versions, task mix, methodology,
uncertainty, budget, and ranking. Separate model capability, harness contribution, evaluator
effects, and cost. Do not infer a universal best harness from one leaderboard result.
Use the repository's existing reference pins, then inspect consequential upstream changes.

Identify a small number of additional industry-defining mechanisms and original research
directions worth evaluating: replay-based adapter certification, capability-scoped command
bridges, evidence-carrying handoffs, compaction fidelity budgets, cache-aware scheduling,
recoverable multi-node sessions, or human-review-aware routing. For each, distinguish known
prior art, a Recursion adaptation, and an untested novel hypothesis. No invented novelty claim.
Rank by concrete user benefit, compatibility, measured or estimated cost, removal story,
and decisive falsifier. Do not turn this into an unbounded feature catalog.

### C. Interactive engines, BYOK, compatibility, and upstream change

Compare direct model APIs/BYOK, native Recursion loops, SDK/server-protocol integration,
structured headless CLI execution, and terminal passthrough. Explain which layer owns
sampling, tools, permissions, conversation state, compaction, lifetime, recovery, and billing.
BYOK may simplify authentication while requiring more loop implementation; determine the
actual tradeoff. Distinguish technical access, provider-permitted use, subscription
entitlement, and distribution rights.

Cover Codex, Claude Code/Agent SDK, Cursor, Gemini, OpenCode, and Hermes, plus the exact
products meant by Grok Build and Meta. Mark unresolved names unavailable/ambiguous and
continue independent lanes; do not invent an endpoint or substitute another product.

Produce a version-specific capability matrix for streaming, conversation turns, queued
input, active-turn steering, clarifying questions, approvals, pre-effect mediation,
custom tools/MCP, command discovery/import, subagents, resume/fork, interruption,
compaction controls, usage evidence, process ownership, and recovery. Classify each
cell as observed, documented, unsupported, unknown, or requiring a probe.

Separate engine adapters, provider adapters, and Recursion plugins. Investigate command
namespaces, collisions, argument schemas, upstream aliases, unavailable capabilities,
and translation fidelity. An imported slash command or upstream plugin must not gain
authority through its origin. Do not promise every native engine feature on every route.
Define a required base contract plus optional versioned capability extensions and an
explicit degraded interaction model.

Test the assumption that tool-event visibility implies control over every effect. Compare
approval callbacks, always-invoked hooks, sandbox controls, shell descendants, engine
retries, and independent network actions. A shell approval does not by itself identify
every downstream effect. Locate where Recursion's fences can actually be enforced and
where the route must be restricted or refused. Cancellation acknowledgement is not proof
that an external action never happened.

Define how upstream releases are discovered, diffed, pinned, staged, replay-tested,
quarantined, promoted, and rolled back without changing active work silently. Include
schema drift, new default tools, experimental surfaces, behavioral changes under an
unchanged protocol, support windows, and emergency security updates. Research the update
policy; do not install updates or create monitoring automations in this campaign.

### D. Tiered compaction, memory, and reasoning visibility

Investigate the proposed configurable layered compaction system using the existing
Context Capsule and Compaction Fidelity Contract. Separate context capacity, retained
conversation, durable goal state, retrieval memory, server-side caches, model quality,
and input-price thresholds.

Explicitly verify the Owner's claims about roughly 256k tokens triggering roughly double
pricing, applicability across models and subscriptions, Codex compaction operating through
milestones/checkpoints, Claude compaction quality, and observed Codex drift. Attribute
personal observations as anecdotes until replicated. Check current model, endpoint,
version, account, and date; API pricing cannot establish subscription debits.

Study long-context retrieval, selective forgetting, progressive summarization, memory
hierarchies, provenance, checkpointing, and loss under repeated compaction. Design tests
for negation, rare constraints, superseded decisions, unresolved dissent, stale tool
results, long-range dependencies, route changes, and reconstruction after native-session
loss. Specify one compaction owner per route epoch, rehydration checks, rejected-summary
recovery, and the cost of the compactor itself.

Distinguish provider-exposed reasoning text, reasoning summaries, opaque/encrypted state,
token counters, and ordinary action explanations. Verify each route's exposure contract.
Do not seek or reconstruct hidden chain of thought, or fabricate a reasoning display.
Recoverable decisions/evidence must not depend on private reasoning being accessible.

### E. Cache hits, token efficiency, and the heartbeat hypothesis

Investigate the claimed 90% discount, the role of stable tool schemas versus tool calls
and outputs, prefix ordering/serialization, invalidation, cache scope, minimum sizes,
write/read charges, retention, eviction, session affinity, compaction, and concurrency.
Reusing the same tool names alone is not evidence of a cache hit. Do not preserve stale
tool results or inject misleading context merely to increase a hit counter.

Evaluate the hypothesis that context/cache value drains after about 30 minutes and that
Head/ARM heartbeats keep caches warm and save quota. Distinguish an idle timeout, retention
policy, eviction, semantic forgetting, client reconnection, and an actual billed request.
Separate zero-model control-plane health checks from model calls intended to refresh a
provider cache. Determine whether a refresh mechanism exists and whether its total cost,
latency, quota, and load are lower than doing nothing or rehydrating later.

Use an explicit cost model and counterfactuals: no keepalive, event-triggered continuation,
provider-supported retention, periodic refresh if permitted, and a fresh capsule. Include
cache writes, hits/misses, compaction, retries, output tokens, background processes, and
quality failures. Keep API charges, observed subscription consumption, inferred capacity,
and unavailable counters separate. Never present null counters as zero or extrapolate
one provider's caching rules to another. No live keepalive is authorized here.

### F. Lightweight operation, setup, and visible work

Investigate low idle cost, responsiveness, lazy plugins, process reuse, bounded rendering,
watcher/indexer limits, wakeups, queues, logging, disk growth, and resource isolation.
The Owner reports serious desktop lag despite high-end hardware; treat that as motivation
for profiling, not proof of a cause or an automatic speedup from headless operation.
Separate UI, engine subprocesses, language servers, indexing, tool work, and inference.
Distinguish no GPU requirement for orchestration from GPU needs for optional local models.

Assess adaptive setup for a small coordinator, developer workstation, server, and enterprise
deployment. Propose dry-run inspection, explainable presets, measured admission, overrides,
rollback, and migration. Research `/setup` as an optional agent-assisted layer over the
existing deterministic zero-model wizard. Resolve first-auth bootstrap, unavailable agents,
credential entry, explicit change scopes, recovery, offline operation, and novice usability.
This product design never authorizes the research agent to edit its own configuration.

Explore visible work through event timelines, diffs, task graphs, state transitions,
progress, and truthful activity summaries. Test comprehension, accessibility, input
stability, privacy, and extra resource cost. Shareability is a product hypothesis; no
fake activity, invented progress, hidden-reasoning display, or automatic private export.
Preserve CLI-first v3 scope; graphical/media features remain proposals unless ratified.

### G. Remote interaction and node orchestration

Separate the interactive client host, authority coordinator, execution host, engine,
inference provider, and account/capacity pool. Investigate configurable harness selection,
machine selection, command surfaces, and node orchestration without collapsing them.

Verify the Owner's platform claims about controlling active Codex sessions from Windows,
macOS dependencies, and Cursor requiring desktop-initiated prompts before remote access.
Distinguish observing, attaching, resuming, steering, starting new work, approval handling,
and unattended boot. Resolve exact product/version and supported transport for each claim.

Assess authenticated coordination across desktops and servers using one canonical writer
per aggregate, leases/fencing, scheduling, enrollment/revocation, manifest-first artifact
transfer, locality, disconnect spooling, replay protection, quota aggregation, and recovery.
Study split brain, duplicate delivery, sleeping laptops, abandoned processes, offline
revocation, partitions, and remote effects with uncertain outcomes. Do not equate a process
kill with rollback. Preserve the blocked OR-015 boundary and distinguish future single-user
multi-node operation from enterprise multi-tenancy.

### H. Autonomous workflow, roles, escalation, and intelligence allocation

Evaluate the proposed configurable lifecycle `Propose -> Plan -> Research -> Synthesize ->
Develop`. Extend it with verification, integration, acceptance, checkpoint/recovery, and
stop decisions where needed. Determine which steps can be skipped for already bounded
tasks; a fixed ceremony for every task may waste resources. Preserve accepted GoalSpecs,
immutable PlanRevisions, task DAGs, bounded WorkPackets, novelty-based retries, and gates.

Investigate `Head -> ARM -> worker` as durable roles, with models replaceable independently.
Head is the strategic delegator and Owner interface; ARMs manage bounded goals and work;
workers execute bounded packets. Preserve direct Owner-to-ARM interaction. Reconcile the
Owner's illustrative Luna -> Terra -> Head chain with configurable model escalation and
the existing authority chain. A stronger model is not a new supervisor or an authority grant.

Compare an all-frontier fleet with mixed configurations, including the Owner's examples
of GPT-6 Astra xhigh leading GPT-5.6 Sol xhigh or Luna workers and public-only Muse Spark
Contributor work. Verify exact availability and costs. Treat these as proposed treatments,
not a permanent product hierarchy or a known efficiency win. Include a single-agent and
a simpler delegation baseline, same total budget, task complexity, retries, review burden,
failure probability, coordination overhead, and correlated errors. Never use model voting
as verification. Escalation should be evidence-triggered and bounded, not a mandatory tour
through every model tier.

Distinguish persistent logical actors from continuously running model calls. Evaluate
event-driven status, cheap deterministic heartbeats, semantic escalation, and useful
checkpoints separately from cache-refresh requests. Specify actual actor/run/lease state;
the user experience may feel continuous without pretending three models are always thinking.

## Scientific method, privacy, and research allocation

Start with a coverage/gap matrix mapping every Owner idea to current requirements and
available evidence. Separate: verified repository fact, verified external mechanism,
Owner preference, anecdote, inference, hypothesis, proposal, unavailable evidence, and
an Owner decision. A marketing claim or model answer does not become a verified mechanism.

Use official docs, pinned implementation paths, changelogs, licenses, standards, original
papers and datasets, and benchmark methodologies. Refresh volatile facts at execution
time. For each consequential source record title, publisher/authors, date/version,
retrieval date, exact URL or private locator, relevant section, source digest when
available, applicability, limitations, contradiction, and expiry/revalidation trigger.
Open the source; search snippets are insufficient. Do not fabricate paper identifiers,
benchmarks, product names, citations, unavailable data, or performance measurements.

Relevant theoretical foundations include distributed state machines and fencing,
capability security, queueing/admission control, cache economics, information retrieval,
lossy compression, human-computer interaction, software modularity, sequential decision
making, and causal evaluation. Explain assumptions and where transfer to Recursion may
fail. Mathematics should illuminate an implementation decision, with defined variables,
units, edge cases, and falsifiable predictions; do not decorate a preference with equations.

Pre-register at most eight decisive follow-up experiments. Each needs a question, current
contract, baseline/treatment, unit of analysis, matched budgets, hard floors, workload,
platform/route versions, metrics with denominators, failure cases, analysis/uncertainty,
stop rule, adoption/rejection rule, and required authorization. Include failures and review
cost. Repeated attempts on one task are not independent tasks. Use blinded power simulation
before making power claims; exploratory work stays labeled exploratory. These are experiment
designs, not permission to run performance trials or spend provider quota.

Maintain private/public boundaries. Never send raw private repository text, Owner messages,
local paths, infrastructure/account details, credentials, private hashes, or transcripts
to public search queries or Contributor routes. Use independently written generic questions
for public retrieval. Store exact sensitive intent through authorized private references;
commit only publication-safe summaries and synthetic examples. Contributor outputs remain
advisory until Astra verifies their sources. Do not assume Grok is private-data eligible
because it is cross-family; verify the exact route and input classification first.

Use the available Deep Research workflow for this research-only session. In a native Codex
construction environment, retain the Owner's explicit campaign topology: Astra integrates;
four bounded read-only Luna lanes at medium for inventories/extraction, high for focused
invariant/security work; admit more only if independent gaps and review capacity justify
them, never beyond eight. Use zero to two Terra high reviewers for private material or
unavailable Grok, with reduced provider diversity recorded. Use one bounded Cursor Grok
4.6 high/xhigh reviewer where the exact configured route, effort, privacy and included pool
are eligible. Muse Spark 1.3 Contributor is optional public/synthetic-only assistance,
never terminal architecture/security/authority verification. No nested agents or shared
worktree writes. When the surface cannot select these routes, report that and use only an
explicitly permitted fallback; never silently substitute a model or change configuration.

Each WorkPacket names goal/plan/task/dependencies, starting commit/ancestors, input digests,
allowed inputs and privacy, read-only ownership, route/tools, time/token budget, evidence
schema, non-goals, falsifiers, and stop conditions. Astra remains the result consumer and
does useful synthesis while workers run. Stop adding workers when outputs overlap, review
backlog grows, or resources/quota/responsiveness degrade. Preserve counterexamples and
dissent; resolve them with source evidence or a discriminating check.

## Durable synthesis, GRILLME, and completion

Create the following under `docs/v3/foundation-research/`, avoiding duplicate report copies:

- `campaign.md`: immutable GoalSpec, input provenance/digests, PlanRevisions, task DAG,
  routes/budgets, exact decisions, gate commands, review history, stop/resume state.
- `synthesis.md`: decision-first answer, at most 2,500 words, explaining the standalone
  product, audience tradeoffs, current foundation, supported changes, rejected assumptions,
  and what must happen now versus later. Link technical detail instead of duplicating it.
- `evidence.json`: thought/claim/source registry, repository anchors, classifications,
  contradictions, confidence, freshness, searches and stopping reasons. Every substantive
  Owner idea has a disposition. Keep private provenance out of publication-safe fields.
- `compatibility.json`: exact route/version/interface capabilities, auth/distribution and
  billing boundaries, evidence IDs, unknowns, required probes, and upgrade admission rules.
- `experiments.json`: at most eight preregistered comparisons/fault experiments, including
  compaction fidelity, total cache economics, mixed-tier delegation, resource/UI cost,
  adapter control/recovery, and remote/node behavior as justified by actual evidence gaps.
- `decisions.json`: proposed spec changes and Owner questions, each bound to sources,
  affected canonical paths, contract/fixture implications, dependency, and recommendation.
- `grillme.md`: the next interactive decision packet described below.
- `check.py`: deterministic, local, zero-model documentation gate with explicit base and
  candidate arguments and nonzero failure behavior. It must not implement runtime features.

Synthesize findings into the allowlisted canonical documents where warranted. Update
README with the reading route. Use the existing claim/source registries rather than
creating competing canonical truth. Register any new global claim IDs atomically; use
dotted IDs for campaign-local thoughts/tasks/sources to avoid namespace collisions.
Preserve superseded reasoning and failed evidence. Corrections to verifiable status may
be made from Git evidence; new product policy stays explicitly proposed pending GRILLME.
Do not rewrite immutable M1 contracts or receipts to fit new research. If their semantics
need change, record the exact conflict, impact, red fixture, and separately authorized
repair campaign needed. Do not mark roadmap milestones complete from research prose.

Follow [PLANNING.md](../PLANNING.md)'s GRILLME protocol. Prepare approximately 8-12
consequential questions, fewer if enough, ranked by dependency and expected decision value.
Do not ask questions already resolved by Owner rulings. Each question must contain:

1. one decision and why it affects the product or construction;
2. the current repository rule and whether the issue is new, contradictory, or unproved;
3. two or three materially different options with concrete tradeoffs;
4. one evidence-backed recommendation, separating default from configurable behavior;
5. relevant source/claim IDs, uncertainty, required experiments, and a falsifier;
6. affected docs/contracts/fixtures and what remains blocked pending the answer.

Cover only unresolved choices, potentially including the first audience, public subscription
promise, native versus delegated execution scope, optional agent-assisted setup, minimum
interactive engine guarantees, compaction/keepalive policy, advanced plugin compatibility,
remote authority-domain versus multi-tenant scope, escalation profiles, and upgrade support.
Leave answers pending. Do not conduct GRILLME or infer approval from silence in this run.
Describe how a later session records each exact Owner answer, updates its status and
affected documents, checks cross-decision consistency, and compiles an accepted versioned
GoalSpec and construction DAG. This research prepares that finalization; it cannot supply
Owner decisions or guarantee completion of all future development.

Use this dependency order: preflight/campaign freeze -> existing-evidence gap map ->
bounded independent discovery -> source verification/dissent resolution -> canonical
synthesis and GRILLME -> deterministic gates -> exact-candidate independent review ->
repairs/re-review -> terminal report. Every node has an inspectable output and gate.

The documentation gate must check these mechanically:

- exact branch, full source/candidate hashes, required M1 ancestry, clean candidate,
  complete start-to-candidate diff, allowlist, and unchanged protected/M1 bytes;
- required artifacts, valid JSON/closed record definitions, unique IDs, complete thought
  coverage, resolvable internal references, registered claim IDs, and relative file/anchors;
- every consequential claim has sources or explicit unknown status; every recommendation
  has a classification, affected contract, decision/experiment link and falsifier;
- compatibility rows separate observation from documentation and missing data from zero;
  experiments contain required controls; GRILLME entries link evidence and remain pending;
- canonical documentation/registry consistency, secret/private-identifier scanning, and
  recorded limitations. Automated checks cannot establish scientific truth or certify privacy
  alone: the lead and reviewer must inspect high-impact claims and the exact publication set.

Adapt the reusable checks in [VALIDATION.md](../VALIDATION.md) into the allowlisted new
gate, replacing its historical hard-coded branch/base with the frozen campaign values.
Do not edit the original validation procedure. Run the existing M1A/M1B/M1C and v2
regression commands read-only as listed in their receipts; record actual commands and
results. An unavailable environment or failing baseline is a disclosed blocker, not a pass.
Do not repair unrelated code or use a historical receipt as a current rerun.

Commit coherent local slices using explicit allowlisted paths: campaign, evidence,
synthesis/contracts, validation, and repairs as they become reviewable. Do not merely
recommend that someone commit the finished findings. Every terminal candidate must pass
the deterministic gate twice, for example:

```text
python -B docs/v3/foundation-research/check.py --base <frozen-start-commit> --candidate <full-candidate-sha>
```

Both runs and the independent review must bind the identical clean candidate. Record
commands, fixtures, outputs/digests, reviewer model/route/effort, independence dimensions,
findings and limitations. Any repair or later commit, including documentation or a
receipt-only change, creates a new candidate requiring revalidation and exact review.
Avoid self-referential receipts: commit the gate/evidence manifest before final checking;
keep the final review attestation bound to that hash in the review channel or an external
local evidence artifact. If that attestation is later committed, revalidate and re-review
the resulting candidate. No earlier verdict transfers automatically.

Do not push, publish, force-push, merge, deploy, or alter protected/default branches.
Lucas owns publication and merge. Missing external-family review may use the explicitly
authorized native Terra fallback with its limitations; an independence requirement that
neither satisfies remains blocked and requires an Owner exception, never a silent pass.

Finish with a concise, self-contained report: overall foundation verdict (`ready for
GRILLME`, `ready with named evidence gaps`, or `blocked`); most consequential corrections
to the Owner's assumptions; exact changed documents and local commit hashes; baseline,
branch/worktree, tests and review results; preserved dissent; and the first GRILLME
decision. Separate confidence in the research from runtime, performance, security,
market-adoption, or release claims. Leave an inspectable repository that the next Astra
session can use without reconstructing this conversation.

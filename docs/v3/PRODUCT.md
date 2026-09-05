---
title: Recursion v3 product specification direction
status: accepted-direction-with-open-research
last-updated: 2026-09-03
---

# Recursion v3 product hypothesis

## Audience and execution-mode findings — 2026-09-05

Lucas-first validation remains the accepted scope. A proposed next learning cohort is developers
performing bounded repository tasks with inspectable diffs and recoverable interruptions. Casual
users need unassisted setup, understandable permissions/cost and recoverable failures; organization
operators additionally need identity, audit, secret and support controls. Hosted tenancy is a
separate deferred authority/isolation design. Enterprise spending and viral adoption remain
hypotheses; no commercial tier policy or compliance claim follows. FND-008/FND-017.

One Recursion CLI can serve native and upstream-engine modes, with visible capability limits.
The product's stable promise is Recursion-owned goals, authority, evidence and recovery; universal
upstream feature parity and subscription portability are unproved. Proposed route-specific
authentication wording and the next external cohort remain pending in
[foundation decisions](foundation-research/decisions.json). See the
[audience job analysis](foundation-research/evidence.json), `analysis.foundation.audiences`.

## Thesis

Recursion is a self-hosted, headless harness for sustained, high-quality autonomous software development across models, subscriptions, APIs, CLIs, repositories, and machines. It turns an owner's intent into reviewable development while preserving authority, privacy, quota, machine responsiveness, and evidence.

Its distinguishing value is not another graphical chat UI or provider router. V3 owns the
durable orchestration harness: actor identity, goals, delegation, routing, state, context,
tools, evidence, policy and observation. It may delegate an individual turn to an optimized
external agent loop without becoming a thin wrapper around that loop:

- the owner retains sovereignty and final authority;
- one main assistant maintains strategic continuity;
- goal-scoped ARM executives plan and delegate implementation;
- external and native agent loops remain replaceable execution engines behind Recursion's
  contracts;
- deterministic infrastructure enforces authority, budget, state, and publication;
- context and evidence survive model, provider, session, and machine changes;
- results are measured by verified code quality, not output volume.

## Initial user and deployment

The first user is Lucas. The first deployment is a lightweight coordinator on the existing Hetzner VPS, with heavier work placed on subscriptions, cloud execution, or authenticated registered nodes. The interactive CLI is the canonical local configuration and operation surface; an agent is never required to edit settings. Multiple detachable terminal windows can observe and converse with Head, ARMs and executors without owning their processes. Telegram is an optional interactive surface for Head and ARM conversations. No web, desktop or mobile graphical client is required for v3.

Public usability remains an explicit design requirement. Users should be able to install a useful minimal edition, bring their own official subscriptions or API credentials, select more capable bundles, and retain complete access to human-readable configuration.

## Product promises

1. **Owner sovereignty.** Local operation, self-hosting, provider choice, portable configuration,
   custom builds and full-access modes remain available. Explicit maximum `sovereign` authority
   may include receipt-backed administration of its own grants.
2. **Provider neutrality.** A model, delivery route, billing pool, harness, and host are separate objects. Users can combine Codex, Cursor, Claude Code, Gemini CLI, OpenCode, Hermes, local models, APIs, and future adapters without rewriting goals.
   The versioned Recursion release is the sole canonical authority and recovery dependency;
   engines and providers are optional typed adapters, while ordinary pinned libraries remain
   permitted implementation dependencies.
3. **Durable autonomy.** Parent goals, ARM state, exact directives, checkpoints, evidence, and budgets survive process death and provider changes.
4. **Quality before activity.** Machine gates and independent verification determine progress. Branch count, agent count, and token consumption do not.
5. **Configurable optimization.** Users may optimize toward cost, quota conservation, quality, latency, privacy, local performance, or custom trade-offs.
6. **Explainability.** Routing, admission, compaction, escalation, and publication decisions are inspectable without spending model tokens.
7. **Privacy by construction.** Project data classification, egress policy, credential isolation, and local-only telemetry are explicit.
8. **Graceful scarcity.** Subscription exhaustion, provider refusal, node loss, and budget depletion checkpoint work instead of encouraging uncontrolled fallback.
9. **Evidence-grounded research.** Research ARMs can find papers, standards, datasets,
   documentation and source; reconcile contradiction; propose experiments; and preserve
   citations without treating model consensus as proof.
10. **Lean optionality.** Advanced capabilities remain physically optional and idle when
    disabled; capability growth must not make the privileged core opaque or the coordinator
    permanently heavy.
11. **Adapter-free recovery.** Core can verify its release identity, replay canonical state and
    expose owner status when every provider, external harness, plugin and frontend is absent.

## Primary workflows

- Configure providers, authenticated CLIs, API routes, capacity pools, models, nodes, and policies through files or the CLI.
- Use Grill Me to convert vague intent into a versioned, accepted GoalSpec.
- Let the Recursion Head start and monitor one or more bounded ARM executives.
- Talk directly to an ARM through its addressable topic without relaying every exchange through
  Head; Head remains aware through canonical state.
- Optionally place multiple named ARMs in a shared conversation or workflow. Head retains the
  overall goal, membership, authority, conflicts and lifecycle while one named ARM may hold a
  bounded workflow-step coordination lease.
- Allow each ARM to delegate research, implementation, testing, review, and integration within inherited authority.
- Move execution between approved models and pools at safe checkpoints while retaining logical identity and evidence.
- Observe progress, queue causes, budget state, route decisions, context health, and blockers from stable read-only interfaces.
- Open, close and rearrange terminal views without changing actor or process lifetime; terminate
  work only through explicit policy-aware commands.
- Produce a verified review branch for the owner; never merge or deploy autonomously by default.
- Run a research GoalSpec that discovers scholarly/technical evidence, builds a claim ledger,
  seeks disconfirmation and produces a reproducible cited decision packet.

## Optimization target

OR-017 requires v3 to consider the complete optimization vector equally behind non-tradeable
authority, safety, privacy, effect-correctness and quality floors. It includes verified quality,
recovery/replay, owner review, quota/tokens/money, context/cache efficiency, latency/throughput,
host resources, terminal interaction, portability/configurability, code/maintenance surface and
extensibility/idle cost. No scalar score hides a regression. Named profiles may select a Pareto
point only through explicit owner-visible policy. The canonical measurements and decision rule
are in [PERFORMANCE-PLAN.md](PERFORMANCE-PLAN.md#canonical-optimization-decision-rule).

## Non-goals for the initial v3 release

- Reselling inference or becoming a mandatory hosted gateway.
- Providing a mandatory central plugin marketplace or vendor-controlled authorization service.
- Shipping a graphical frontend as part of the initial v3 contract.
- Guaranteeing that unrelated providers share server-side prompt/KV caches.
- Persisting hidden chain of thought or treating it as required recovery state.
- Replacing Git, provider-native authentication, or every provider's optimized inner agent loop.
- Making protected-branch merge, production deployment, credential administration or authority
  expansion implicit/default consequences of ordinary autonomy. A future explicit Full Access
  grant may include supported high-impact capabilities only after constitutional reconciliation.
- Running every worker on the coordinator VPS.
- Exporting private prompts, source, telemetry, or project evidence by default.

## Release philosophy

V3 is one monumental product release built as independently testable internal milestones. A public `v3.0.0` tag should wait until the mandatory end-to-end contract passes, while core, standard, remote, full and custom release manifests control installed surface area. Future product defaults proposed after constitutional reconciliation include `checkpoint` PAUSE, trusted bounded autonomy, digest-aware plugin grants and detachable terminals; current immediate PAUSE remains operative. Installing `full` never implies maximum `sovereign` authority. This is an atomic product promise with incremental construction, not a big-bang implementation.

## What must be proven

- A strong ARM plus deliberate delegation produces better accepted code per quota unit than uncontrolled swarms.
- Semantic context artifacts and compaction reduce repeated input without losing owner intent, constraints, or evidence.
- The coordinator stays responsive on the target VPS under realistic event, SQLite, plugin, and monitoring load.
- Users can understand and change routing without reading source or invoking a model.
- Provider and node failures cannot silently widen spend, privacy exposure, or permissions.
- V3's additional machinery produces measurable benefit over the accepted v2 baseline.
- Direct ARM topics and multi-ARM collaboration reduce owner coordination effort without
  creating conflicting authority, instruction loss or an AI ARM Manager.
- Scientific Research ARM output withstands false-citation, outdated-source, contradiction,
  reproducibility, copyright, privacy and independent-source-verification gates.

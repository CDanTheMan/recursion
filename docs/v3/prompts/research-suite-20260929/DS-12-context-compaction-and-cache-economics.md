---
title: DS-12 — Context compaction and cache economics
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-12 — Context compaction and cache economics

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. Supplying this document is the invocation; it makes no repository or provider call on its own.

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

- Recursion owns a provider-neutral semantic evidence cache: stable, content-addressed artifacts (goal, repository, decisions, plan, checkpoints, diff, evidence, blockers) that adapters compile into each provider's preferred context shape. This is separate from provider-side prompt/KV caches, which are scoped to a provider, model family, account, endpoint, prefix or session and are not portable across vendors.
- The Execution Context Capsule is the standard handoff unit: a non-droppable control kernel (logical actor and lineage, exact GoalSpec version, current task and gate, authority/privacy/budget bounds, exact source/candidate identifiers, checkpoint and blockers, output contract) plus configurable context tiers. A compacted epoch is not authoritative unless deterministic validation confirms every active directive, gate, blocker and evidence reference is preserved or rehydratable.
- One deterministic context governor owns the single authoritative compaction transition for a route epoch. Native and session compactors return candidate artifacts only and cannot advance the authoritative epoch, so provider-native compaction is never the sole copy of Owner intent or execution state.
- Named compaction policies are `native`, `deterministic-only`, `hybrid`, `aggressive`, `manual` and `off`; no universal default is selected. A `RouteCapabilityDescriptor` is a versioned, maintainer-owned per-route descriptor covering context limits, native compaction, resumable-session semantics, cache observability and controllable fields, stable-prefix constraints, tool-output handling, token-accounting fidelity and discovery evidence/time.
- Units that must stay separate: provider prompt-cache behavior, Recursion-owned evidence reuse, and subscription debit. A cache hit or saving is asserted only from dated route evidence; unsupported savings claims carry an expiry trigger, and `unknown` is distinct from zero.
- Accepted direction: no periodic model keepalive; ordinary continuation is event-driven and deterministic health checks are separate. A preference/notification stream may coalesce, but revocation and tightening of identity, credentials, egress, privacy or resources advance a separate monotonic authority fence that cannot be coalesced away.
- Priming, refresh and retry costs belong in the full workflow cost, and the no-future-work and zero-miss edge cases must fail closed rather than being counted as savings.
- Evidence discipline: classify claims as source-documented, locally observed, inferred or unverified; provider cache flags or billing rules must not be copied between endpoints or routes without route evidence.

## Purpose

Decide which lawful, documented cache, session and context controls reduce repeated work without hidden coupling, privacy leakage or fidelity loss, and whether provider prompt caches and Recursion-owned evidence reuse can be kept honestly separate. This blocks the context governor, the execution-context capsule policy and the evidence-cache design. It is blocking because no local experiment yet measures compaction loss, priming cost, invalidations or cross-route continuation.

## Authority and boundaries

The authority, scope, privacy and evidence-discipline constraints for this lane are restated in `## Baked context` above and govern this work. This prompt authorizes a report only: no runtime, provider, model, authentication, configuration, spending, deployment, publication or merge action. "Cache manipulation" here means only supported prompt, layout, session and provider cache controls plus local evidence reuse; it never means bypassing provider policy or fabricating usage. Keep public/synthetic briefs free of private project content, transcripts, local paths, credentials or account/infrastructure identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. Which cache, session and context controls does each supported route actually expose at a dated version (endpoint, model class, explicit versus implicit, breakpoints, lifetime, retention), and which fields are documented, disabled or unknown?
2. Which cached-read, cache-write and billing semantics are documented per endpoint, and which cannot be transferred to an OAuth or harness route without route evidence?
3. Does a deterministic stable prefix plus content-addressed repository evidence reduce repeated input on same-route continuation when measured against a cold baseline that includes priming cost?
4. Does cross-route continuation reuse any provider cache, or only Recursion-owned semantic artifacts, and what quality loss appears after session reconstruction?
5. Which invalidation events (source change, configuration change, revoked instruction, changed tool or resource result) must force rehydration, and how accurately does a repository map invalidate by commit and configuration digest?
6. Does repeated compaction lose owner directives, gates, blockers or evidence references, and which deterministic checks detect each loss?
7. Can one compaction governor per route epoch be enforced, with native and session compactors returning candidate artifacts only and unable to advance the authoritative epoch?
8. Does session affinity beat fresh-session capsule reconstruction once priming, refresh and recovery cost are included?
9. What privacy leakage arises from cache keys, digests, size or timing patterns, or cross-project deduplication, and how is private-project isolation verified?
10. How complete is cold recovery from the non-droppable capsule plus content-addressed artifacts when no provider session survives?
11. How many cache writes and reads, and how many compactor, refresh, retry and output calls, occur per workflow, and how are unavailable counters kept unknown?
12. What is the total-cost counterfactual for keepalive or refresh, and does it ever repay priming under a no-future-work edge case?
13. Which cache-hit or savings claims are unsupported at current dates and must carry an expiry trigger?
14. What is the correct unit of account when provider cache, application evidence reuse and subscription debit are three different things?

## Deliverable

- A dated route-exposure table that separates provider cache controls from Recursion-owned evidence and context reuse, never conflating the two.
- A source-pinned claim table with classification, confidence and expiry, including explicit "unknown" rows.
- Options with tradeoffs for stable-prefix layout, session affinity, capsule hydration, evidence caching and compaction policy.
- A recommendation tied to a competing option and a decisive falsifier, plus open Owner questions.
- Explicit preservation of the non-droppable capsule and the one-compaction-governor-per-route-epoch requirement.

## Non-goals

- Bypassing provider policy or fabricating cache usage, cache hits or savings.
- Inferring a cache hit or subscription debit from a documented flag or a single observation.
- Adopting a paid explicit cache treatment, a default lifetime, or periodic model keepalive.
- Dropping the non-droppable capsule or allowing more than one compaction governor per route epoch.
- Sending private project content or raw content digests to a public route.
- Changing provider, auth or configuration, or running any cache experiment against a paid route.
- Reopening accepted Owner decisions or promoting a cache policy into a default.

## Completion gate

- Every provider exposure is pinned by endpoint, model class, source and retrieval date.
- Provider cache and Recursion-owned evidence reuse stay separate in every claim.
- Every recommendation names a competing option and a falsifier.
- No cache hit or saving is asserted without dated route evidence; unsupported claims carry expiry.
- The capsule and one-governor-per-epoch requirements are preserved explicitly.
- Unavailable counters stay unknown; no usage is fabricated.
- The privacy and secret scan is clean and no protected path is edited.
- Open Owner questions are listed and no decision is promoted.

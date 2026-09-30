---
title: DS-26 — Telemetry accounting and honest status
status: proposed-inert
last-updated: 2026-09-29
parent-goal: goal-recursion-v2-execution-fabric
invocation: only after Lucas explicitly invokes this file in a new session
---

# DS-26 — Telemetry accounting and honest status

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. This file is inert until Lucas invokes it in a new session; creating, reading or listing it launches nothing and authorizes no provider call, write, effect, spend or configuration change.

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

- Telemetry exists to improve verified development and preserve scarce capacity, not to maximize agent activity. Every execution segment carries stable correlation identifiers: `project_id`, `goal_id` plus GoalSpec version, `arm_run_id`, `task_id` and `segment_id`, `route_id` and resolved route digest, the provider-native session identifier when available, and source/checkpoint/candidate/evidence/verifier identifiers. Provider session ids are disposable; Recursion lineage is authoritative.
- Evidence providers are read-only usage sources: provider and CLI native usage events, official provider usage APIs, harness-specific collectors, local resource monitors and explicitly labeled deterministic token estimators. `ccusage` is an Owner-accepted candidate name for a possible future adapter only; it is not yet source/license reviewed and must be researched before admission. No collector may infer zero use because a CLI omits token counters.
- Cost classes are distinct: subscription capacity, metered/API spending, inferred quantity and `unavailable` are separate units, and null is not zero. Cached reads and writes must be normalized before summation, and human review minutes and host resource cost are reported separately from inference cost unless an explicit accepted valuation weight exists.
- Counter semantics: a counter is cumulative or per-request. Cumulative totals must be reconciled so a crash, reset, fork or session rotation neither double-charges nor erases consumption; helper, classifier, compaction and retry calls are counted exactly once at the parent segment; missing or unavailable counters stay `unknown`.
- The adaptive route scorer may reorder already-approved eligible routes by task class, but it may not add or authenticate a provider, enable metered billing or training, widen permissions or egress, lower required verification, rewrite GoalSpec or modify its own hard policy. Its state is versioned, explainable, resettable and exportable, and shadow/offline evaluation precedes automatic use.
- Privacy default is local and metadata-minimal: full prompts, raw tool output, source snippets and private artifact content are excluded from metrics tables and external exporters, and aggregation must resist revealing private repository membership.
- Profiles: `coordinator-small` is the small authority/scheduler/observer class and `interactive workstation` is the heavier development class; both are defined by measured CPU, memory, disk and latency, never by a vendor model.
- Milestone 8 (adaptive optimization) delivers explainable local routing calibration, quota shadow prices, reservations, adaptive concurrency, cache-domain affinity, resource shedding, telemetry evidence providers and an optional usage reconciler. Its gate is shadow-mode and controlled improvement for at least one declared profile without lowering quality floors or widening authority.
- Honest status: visible activity is an observation, never percent-complete; absence is never converted into a healthy or complete status; no optimization default is promoted without a baseline, an uncertainty statement and a falsifier. `M1A`/`M1B`/`M1C` are merged, inert contract milestones (planning/replay; route, plugin and process requirements; source, effect and persistence requirements) that make no provider call and launch no process. `OR-021`-`OR-039` are recorded Owner decisions: OR-021-OR-025 establish the standalone v3 architecture, native+upstream execution, the ten CLI controls, the optimization ranking and Windows/Linux placement; OR-026-OR-035 add critical integrations, persistent assistants, Stop/fork and compatibility semantics, continuity and truthful verification reporting, recovery budgets, six update modes, anti-superficial optimization and representative resource limits; OR-036-OR-039 accept the smallest aggregate plus broker refinement, Owner-only GoalSpec amendments with routine delegation, visible assistant-to-Head consultation, and deep whole-system optimization.

## Purpose

Decide how v3 qualifies telemetry evidence providers, normalizes provider counters, separates cost classes, and renders status without fabrication. This blocks the dashboards, budget reservations, route learning and optimization claims in the adaptive-optimization milestone and the canonical telemetry contract: without a falsifiable accounting contract, a visible activity stream becomes a fabricated percent-complete, and a missing counter becomes a false zero.

## Authority and boundaries

The authority, scope, privacy and evidence-discipline constraints for this lane are restated in `## Baked context` above and govern this work. This prompt authorizes a report only: no runtime, provider, authentication, configuration, spending, deployment, publication or merge action. Do not reopen the completed M1A/M1B/M1C contract work or the recorded Owner decisions OR-021 through OR-039, and do not select a product language, store or framework. Keep public/synthetic briefs free of private project content, transcripts, local paths, credentials or account/infrastructure identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Evidence providers and qualification

1. Which provider usage APIs (OpenAI, Anthropic, Google, Cursor) currently expose read-only, account-scoped usage, and what exact fields, windows, granularity and retention do their public documents specify?
2. Which CLI-native usage events exist for the supported harnesses, and which of them are cumulative totals versus per-request deltas?
3. What is the `ccusage` project's exact repository, pinned version, license and data model, and what does its license permit for a bundled or optional adapter?
4. For local resource monitors, which host counters (CPU, RSS, disk, I/O, process, handle, wakeup) are reliably available on the coordinator-small and workstation profiles?
5. How should deterministic token estimators be labeled so they are never mistaken for provider-reported usage?
6. What qualification receipt should each evidence provider produce before its numbers may enter a dashboard, and how is applicability bound to a route, model, endpoint and date?

### Counter semantics and normalization

7. Under current public documentation, do cached tokens count toward API tokens-per-minute, and where does Anthropic exclude cache reads from input tokens-per-minute; how do these rules differ from any subscription debit?
8. When is a counter cumulative versus per-request, and how must cumulative `model_usage` totals be reconciled so a crash, reset, fork or session rotation neither double-charges nor erases consumption?
9. Which helper, classifier, compaction and retry calls are excluded from a provider's headline counter, and how are they counted exactly once at the parent segment?
10. How are subscription, metered, inferred and unavailable quantities represented as distinct classes, with throttles and resets recorded as availability changes rather than task-budget changes?
11. What normalization is required before summing cache reads and cache writes, and which edge cases (no-future-work, zero-miss, partial final total) must fail closed?

### Cost separation, latency and identity

12. How are human review minutes and host resource cost reported separately from inference cost unless an explicit Owner-accepted valuation weight exists?
13. How is bridge/control latency measured separately from inference latency, and how are input stability and resource attribution kept distinct?
14. Which correlation identifiers (`project_id`, `goal_id`, `arm_run_id`, `task_id`, `segment_id`, `route_id`, route digest, provider session, source/checkpoint/candidate/evidence/verifier) must every usage record carry?

### Dashboards, honest status, learning and privacy

15. Which operator views are required (running, waiting, budget, backlog, regressions, compaction health, headroom, exact actions), and how does each avoid converting absence into a healthy or complete status?
16. What rule guarantees visible activity is an observation, never percent-complete, and what wording and data model prevent an inferred progress bar?
17. What constraints must the adaptive route scorer obey (no new providers, no widened authority, no lowered verification), and how are its state versioned, explained, reset and exported with shadow/offline evaluation before use?
18. What metadata-minimal privacy default excludes prompts, raw tool output, source snippets and private artifact content, and how does aggregation resist revealing project membership?

### Measurement families

19. For each family (quality, capacity/cost, context quality, system performance, research quality, continuity/safety), which counters are required, which are optional, and which are explicitly `unavailable` rather than zero?
20. What falsifier, baseline and uncertainty statement is required before any telemetry-derived optimization default is promoted?

## Deliverable

A source-pinned report containing: a claim table (claim, source, version/date, classification, confidence, expiry trigger); a provider-qualification matrix with explicit unknown cells; a counter-semantics table covering cached reads/writes, cumulative versus delta, helper exclusion, and subscription versus metered versus inferred versus unavailable; a normalization and exactly-once counting procedure; a cost-separation and latency-attribution model; a correlation-identifier schema; a dashboard and honest-status specification; a route-learning constraint list; a privacy-default statement; a measurement-family counter map; and a recommendation tied to a named competing approach and a decisive falsifier, plus open Owner questions.

## Non-goals

- No runtime, schema or dashboard implementation.
- No provider, model, network or paid API call.
- No provider/account credential or live usage query.
- No language, store, framework or dashboard-stack selection.
- No fabricated counter, percent-complete, confidence percentage or quota conversion.
- No reopening of M1A/M1B/M1C contracts or Owner decisions.
- No modification of protected paths or the canonical telemetry contract.
- No private repository content, paths, transcripts or account identifiers in any brief.
- No optimization default promoted without baseline, uncertainty and falsifier.

## Completion gate

- Every evidence provider has a pinned source, version/date and qualification receipt, or is marked `unavailable`.
- Every counter is classified as observed, modeled, inferred or `unavailable`, and no missing value is reported as zero.
- Cache reads and writes are normalized before summation, with the OpenAI/Anthropic/Google distinctions stated per endpoint.
- Cumulative totals, helper/compaction calls and retries are each counted exactly once with a stated reconciliation rule.
- Human review cost and host resource cost are separated from inference cost unless an accepted valuation weight exists.
- Bridge/control latency is separated from inference latency.
- Every usage record carries the full correlation-identifier set.
- The honest-status rule forbids fabricated percent-complete and requires unknown-as-unknown.
- The route-learning constraints and privacy defaults are stated with a falsifier.
- Protected paths are untouched and the secret scan is clean.

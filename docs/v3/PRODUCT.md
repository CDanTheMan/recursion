---
title: Recursion v3 product hypothesis
status: hypothesis
last-updated: 2026-09-02
---

# Recursion v3 product hypothesis

## Thesis

Recursion is a self-hosted control plane for sustained, high-quality autonomous software development across models, subscriptions, APIs, CLIs, harnesses, repositories, and machines. It turns an owner's intent into reviewable development while preserving authority, privacy, quota, machine responsiveness, and evidence.

Its distinguishing value is not another chat UI or another provider router. It is the durable outer loop around multiple agent runtimes:

- the owner retains sovereignty and final authority;
- one main assistant maintains strategic continuity;
- goal-scoped ARM executives plan and delegate implementation;
- external and native agent loops remain replaceable execution engines;
- deterministic infrastructure enforces authority, budget, state, and publication;
- context and evidence survive model, provider, session, and machine changes;
- results are measured by verified code quality, not output volume.

## Initial user and deployment

The first user is Lucas. The first deployment is a lightweight coordinator on the existing Hetzner VPS, with heavier work placed on subscriptions, cloud execution, or authenticated registered nodes. The first CLI prioritizes direct human configuration and operation; an agent is never required to edit settings.

Public usability remains an explicit design requirement. Users should be able to install a useful minimal edition, bring their own official subscriptions or API credentials, select more capable bundles, and retain complete access to human-readable configuration.

## Product promises

1. **Owner sovereignty.** Local operation, self-hosting, provider choice, portable configuration, custom builds, and full-access modes remain available to the owner.
2. **Provider neutrality.** A model, delivery route, billing pool, harness, and host are separate objects. Users can combine Codex, Cursor, Claude Code, Gemini CLI, OpenCode, Hermes, local models, APIs, and future adapters without rewriting goals.
3. **Durable autonomy.** Parent goals, ARM state, exact directives, checkpoints, evidence, and budgets survive process death and provider changes.
4. **Quality before activity.** Machine gates and independent verification determine progress. Branch count, agent count, and token consumption do not.
5. **Configurable optimization.** Users may optimize toward cost, quota conservation, quality, latency, privacy, local performance, or custom trade-offs.
6. **Explainability.** Routing, admission, compaction, escalation, and publication decisions are inspectable without spending model tokens.
7. **Privacy by construction.** Project data classification, egress policy, credential isolation, and local-only telemetry are explicit.
8. **Graceful scarcity.** Subscription exhaustion, provider refusal, node loss, and budget depletion checkpoint work instead of encouraging uncontrolled fallback.

## Primary workflows

- Configure providers, authenticated CLIs, API routes, capacity pools, models, nodes, and policies through files or the CLI.
- Use Grill Me to convert vague intent into a versioned, accepted GoalSpec.
- Let Head Hermes start and monitor one or more bounded ARM executives.
- Allow each ARM to delegate research, implementation, testing, review, and integration within inherited authority.
- Move execution between approved models and pools at safe checkpoints while retaining logical identity and evidence.
- Observe progress, queue causes, budget state, route decisions, context health, and blockers from stable read-only interfaces.
- Produce a verified review branch for the owner; never merge or deploy autonomously by default.

## Optimization target

V3 seeks the highest verified development quality per unit of:

- subscription quota;
- metered cost;
- CPU, memory, disk I/O, and interactive-machine impact;
- elapsed time;
- owner review attention.

No single scalar hides these dimensions. Named profiles select a Pareto point, and telemetry reports the underlying measurements.

## Non-goals for the initial v3 release

- Reselling inference or becoming a mandatory hosted gateway.
- Providing a mandatory central plugin marketplace or vendor-controlled authorization service.
- Guaranteeing that unrelated providers share server-side prompt/KV caches.
- Persisting hidden chain of thought or treating it as required recovery state.
- Replacing Git, provider-native authentication, or every provider's optimized inner agent loop.
- Autonomous protected-branch merge, production deployment, credential provisioning, or authority expansion.
- Running every worker on the coordinator VPS.
- Exporting private prompts, source, telemetry, or project evidence by default.

## Release philosophy

V3 is one monumental product release built as independently testable internal milestones. A public `v3.0.0` tag should wait until the mandatory end-to-end contract passes, while minimal, standard, and full release manifests control installed surface area. This is an atomic product promise with incremental construction, not a big-bang implementation.

## What must be proven

- A strong ARM plus deliberate delegation produces better accepted code per quota unit than uncontrolled swarms.
- Semantic context artifacts and compaction reduce repeated input without losing owner intent, constraints, or evidence.
- The coordinator stays responsive on the target VPS under realistic event, SQLite, plugin, and monitoring load.
- Users can understand and change routing without reading source or invoking a model.
- Provider and node failures cannot silently widen spend, privacy exposure, or permissions.
- V3's additional machinery produces measurable benefit over the accepted v2 baseline.

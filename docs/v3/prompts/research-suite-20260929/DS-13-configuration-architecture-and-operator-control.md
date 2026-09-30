---
title: DS-13 — Configuration architecture and operator control
status: proposed-inert
last-updated: 2026-09-29
parent-goal: goal-recursion-v2-execution-fabric
invocation: only after Lucas explicitly invokes this file in a new session
---

# DS-13 — Configuration architecture and operator control

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. This file is inert until Lucas invokes it; reading or creating it launches nothing and authorizes no provider call, write, or effect.

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

- Configuration is hierarchical and schema-driven: one versioned schema drives file, interactive CLI and transport editors. The resolution order is built-in defaults, edition preset, installation/authority-domain config, project config, parent-goal config, task override, then an explicit ephemeral operator override. The most specific valid value wins; child scopes may narrow, but widening authority, privacy exposure, credentials, network, spending or publication requires an explicit acknowledged operation at that scope.
- Merge operators: preferences merge by keyed override; hard authority, egress and budget ceilings intersect; plugin sets merge by stable identifier with conflict rejection; credentials require explicit authority and cannot be selected by a generic most-specific-wins rule. Effective value plus provenance (requested value, effective value, source scope/preset, merge operator, reason, application boundary, blocked status) is computed with zero model tokens.
- Field lifecycle classes are `goal-frozen` (snapshotted into GoalSpec, changed only by amendment), `checkpoint-applied`, `live` and `restart-required`. An edit carries schema version, scope/id, expected current version/digest, canonical before/after representations, principal, authority receipt, lifecycle and an idempotent command id; stale-version edits fail rather than using last-write-wins.
- Editions are `core`, `standard`, `remote`, `full` and `custom`. Installing `full` never enables maximum `sovereign` authority; `sovereign` is a separately enabled capability preset whose self-grant must be an attributable, schema-checked action. `Full Access` is a capability vector, not an ambient boolean.
- PAUSE direction: `checkpoint` is the selected future product default, with `interrupt`, `drain` and emergency stop as explicit alternatives; current immediate halt remains operative until a constitutional amendment is applied.
- Candidate schema techniques (none selected as final): JSON Schema 2020-12 for structural validation, RFC 8785 canonical JSON for a digest/signature representation, and TOML 1.0 or YAML as the human syntax only when round-trip, duplicate-key, type and normalization fixtures prove a deterministic compiled canonical form.
- Evidence discipline: configuration is never permission to weaken silent integrity, authority, privacy or verification invariants; unknown fields and invalid combinations fail before any side effect.

## Purpose

Decide whether one typed schema can make deep customization predictable and safe across files, the interactive CLI, Telegram, editions, goals, tasks, plugins, routes, nodes, PAUSE, Full Access and terminal layouts. This blocks the configuration freeze and the promise that settings are transactional, portable, explainable and rollback-safe. It is blocking because merge semantics, provenance, stale-version conflicts and migration behavior are still unproven.

## Authority and boundaries

The authority, scope, privacy and evidence-discipline constraints for this lane are restated in `## Baked context` above and govern this work. This prompt authorizes a report only: no runtime, provider, model, authentication, configuration, spending, deployment, publication or merge action. Configuration is never permission to weaken silent integrity, authority, privacy or verification invariants. Keep public/synthetic briefs free of private project content, transcripts, local paths, credentials or account/infrastructure identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. Which configuration encoding gives a deterministic canonical form and safe round-trip (typed structural validation, a canonical serialization for digests, and a human syntax only when duplicate-key, type and normalization fixtures pass)?
2. What is the smallest orthogonal setting set covering engines, tools, context, memory, routing, delegation, verification, scheduling, placement, resources, nodes, PAUSE and Full Access without untestable interactions?
3. How should merge operators behave: keyed override for preferences, intersection for authority, egress and budget ceilings, stable-identifier merge for plugin sets, and explicit authority for credentials?
4. How are effective value plus provenance (requested value, effective value, source scope or preset, merge operator, reason, application boundary, blocked status) computed and explained with zero model tokens?
5. How are narrowing and widening distinguished, and what authenticated acknowledgment and receipt are required before widening authority, privacy exposure, network access, spending or publication rights?
6. How do transactional edits handle stale-version conflicts, concurrent clients, partial failure and idempotent replay without last-write-wins?
7. Which fields are live, checkpoint-applied, goal-frozen or restart-required, and how are propagation and per-session application receipts proven?
8. How are migrations and rollback designed so an unknown field or invalid combination fails before any side effect?
9. How are credential references kept opaque and validated for presence without exposing secret values?
10. How do presets and feature flags compose across editions so a lean edition defers but never silently erases an accepted capability?
11. How do cross-platform paths and environment differences stay portable across Windows and Linux?
12. How do novice setup and expert file editing stay consistent because both compile from the same schema, and which pairwise or three-way fixtures prove it?
13. Which setting combinations cannot be explained or tested and must be rejected rather than shipped?
14. How is it guaranteed that no configuration combination weakens a silent integrity, authority, privacy or verification invariant?

## Deliverable

- A candidate versioned schema and the smallest orthogonal field set, with named gaps where a surface cannot yet be modeled.
- Written merge-operator semantics, provenance output, lifecycle and propagation table, and migration/rollback design.
- A configuration-complexity vector (field count, scope levels, cross-field constraints, lifecycle transitions, authority and billing edges, invalid-combination classes, round-trip and migration coverage).
- Options with tradeoffs and a recommendation tied to a competing option and a decisive falsifier, plus open Owner questions.

## Non-goals

- Selecting a language, parser, store, framework or file format as final.
- Editing configuration, credentials, auth, model selection, cron or autonomy flags.
- Implementing Full Access, PAUSE or sovereign authority.
- Reopening accepted Owner decisions or treating configuration as permission to weaken invariants.
- Designing hosted tenancy, edition commerce or a graphical client.
- Promising hot reload or last-write-wins conflict handling as a default.

## Completion gate

- One versioned schema covers every named surface, or every gap is named explicitly.
- Every merge operator and lifecycle transition is reviewer-checkable and testable.
- No combination ships that cannot be explained or tested.
- Every recommendation names a competing option and a falsifier.
- Stale-version, partial-failure and concurrent-client behavior is specified.
- Credential references are opaque, the secret scan is clean, and no protected path is edited.
- No configuration path can override a silent integrity invariant.
- Open Owner questions are listed and no decision is promoted.

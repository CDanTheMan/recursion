---
title: Recursion v3 context, cache, and compaction hypothesis
status: hypothesis
last-updated: 2026-09-03
---

# Recursion v3 context, cache, and compaction hypothesis

## Two different caches

Provider-side prompt/KV caches are normally scoped to provider, model family, account, endpoint, prefix, or session under rules Recursion may not control. V3 must not promise one physical cache shared by unrelated providers.

Recursion can own a provider-neutral **semantic evidence cache**: stable, content-addressed artifacts representing the goal, repository, decisions, plan, checkpoints, diff, evidence, and blockers. Adapters compile the same artifacts into each provider's preferred context shape. This creates cross-model reuse without pretending server-side caches are portable.

## Canonical context artifacts

Candidate artifact types:

- `OwnerIntentSlice`;
- `GoalBrief`;
- `PlanRevisionProjection`;
- `RepositoryMap`;
- `DecisionSlice`;
- `TaskBrief`;
- `CheckpointSummary`;
- `DiffSummary`;
- `EvidenceBundle`;
- `OpenBlockers`;
- `CapabilitySnapshot`.

Each artifact has a schema version, project/privacy classification, source identifiers, project-scoped content identity, dependencies, creation method, validity boundary, and rehydration locator. A context package references artifacts by an authorized opaque identifier rather than copying them repeatedly. Raw digests remain inside the project's trust domain; cross-domain handles are randomized or keyed so they do not expose equality or become membership oracles.

`PlanRevisionProjection` is a derived context view of the exact canonical `PlanRevision` digest in
[AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md), not a second plan object or writable snapshot.

## Execution Context Capsule

The capsule is the standard handoff unit between executives, engines, providers, and nodes. It is a manifest, not necessarily a monolithic prompt.

### Non-droppable control kernel

- logical actor and parent lineage;
- exact GoalSpec version and Owner Intent Ledger references;
- current task and acceptance gate;
- authority, permissions, privacy, egress, and budget bounds;
- exact repository/source/candidate identifiers;
- current checkpoint and open blockers;
- required output/evidence contract.

### Configurable context tiers

- hot working set;
- recent decisions and actions;
- relevant repository evidence;
- historical summaries;
- lazily rehydratable artifacts;
- optional raw session history.

Cross-node delivery sends the manifest and minimum control kernel first, then hydrates only required artifacts after authorization and digest validation.

## Compaction controller

V3 uses a dual-plane adaptive controller:

1. **Native plane:** allow Cursor, Codex, Claude Code, Gemini CLI, OpenCode, or another harness to use its own optimized compaction when the adapter can observe enough state and the owner enables it.
2. **Recursion plane:** maintain model-independent artifacts, non-droppable constraints, checkpoints, and deterministic validation outside the provider session.

Named policies:

- `native`;
- `deterministic-only`;
- `hybrid` (recommended default);
- `aggressive`;
- `manual`;
- `off`.

This avoids double-summarizing blindly while ensuring provider-native compaction never becomes the sole copy of owner intent or execution state.

## When to compact

Compaction is adaptive. Signals may include:

- provider-reported context usage or warning;
- token estimates with explicit uncertainty;
- semantic phase transition;
- checkpoint boundary;
- declining retrieval relevance;
- repeated context segments;
- expected route/provider switch;
- memory or latency pressure.

The deterministic context governor owns the one authoritative compaction transition for a route
epoch. It chooses whether to reuse the native session, request a route-native transform, start a
fresh session with a capsule, or call a specialist compactor. Native/session and plugin
compactors return candidate artifacts only; they cannot advance the authoritative epoch. The
governor must avoid needless churn that forfeits provider cache affinity.

## Compaction Fidelity Contract

No compacted epoch becomes authoritative unless deterministic validation confirms:

- every active owner directive remains represented by exact reference;
- GoalSpec, permissions, privacy, budgets, gates, source state, decisions, blockers, and next action are present;
- identifiers and digests resolve;
- omitted evidence remains rehydratable;
- contradictions and uncertainty are preserved rather than smoothed away;
- the old epoch remains available according to retention policy until the new one is accepted.

Independent model auditing is configurable for high-risk goals. Hidden chain of thought is neither required nor persisted; recoverable state consists of decisions, evidence, actions, uncertainties, and next steps.

## RouteCapabilityDescriptor

`RouteCapabilityDescriptor` is the canonical schema name for the maintainer-owned context
capability descriptor named in the owner ruling. Other prose labels are descriptive only.

Every engine/provider adapter publishes a maintained, versioned descriptor covering:

- supported context limits and known server-side restrictions;
- native compaction and summarization behavior;
- resumable session semantics;
- cache observability and controllable cache fields;
- stable-prefix constraints;
- tool-output handling;
- attachment/artifact behavior;
- token-accounting fidelity;
- discovery method and evidence timestamp.

Maintainers own signed descriptor updates. Local overrides are allowed and visible. Runtime discovery that conflicts with a descriptor degrades to the conservative bound and alerts the executive. An owner may override a performance or compatibility bound, but no descriptor override can widen GoalSpec authority, privacy, egress, credential visibility, billing, publication, or another constitutional boundary. Descriptor resolution must be zero-token.

## Cache-aware compilation

Provider adapters should maximize same-provider hits where documented by:

- keeping invariant instructions and schemas in stable prefixes;
- ordering stable artifacts before volatile task state when provider semantics reward prefix reuse;
- using canonical serialization and deterministic whitespace;
- referencing unchanged repository artifacts by stable digest;
- isolating volatile timestamps, counters, and route explanations from reusable prefixes;
- preserving provider session affinity when quality and capacity policy permit;
- recording observed cache evidence instead of estimating it as fact.

Exact strategies must be provider-specific and continuously revalidated against official documentation and empirical probes.

## Privacy

Context artifacts inherit the strictest classification of their inputs. Cross-project deduplication is forbidden for private content even when underlying bytes match. Public or cross-project interfaces expose neither raw content digests nor stable size/timing patterns that make equality or membership practical to test. Raw prompts and tool outputs are locally encrypted when retained, never automatically exported, and excluded from public telemetry.

## Required experiments

- Decision/constraint recall after repeated compaction cycles.
- Rehydration completeness after provider and node switches.
- Token and latency savings from stable artifact serialization.
- Native-only versus deterministic-only versus hybrid compaction.
- Session affinity benefits versus fresh-session capsule quality.
- Repository-map invalidation accuracy by commit and configuration digest.
- Cache-hit observability and billing behavior for every supported route.

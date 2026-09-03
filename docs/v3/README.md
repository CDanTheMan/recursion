---
title: Recursion v3 design workspace
status: hypothesis
last-updated: 2026-09-02
authority: non-normative until ratified
---

# Recursion v3 design workspace

Recursion v3 is hypothesized as a provider-neutral autonomous-development harness and integration system. It preserves the proven v2 execution and safety invariants while making the main assistant, ARM executives, provider routes, context flow, plugins, nodes, and operator experience first-class parts of one coherent product.

This directory is a research baseline, not an implementation authorization. Where it conflicts with Lucas's current instruction, `CONTROL_PLANE.md`, or a ratified decision in `state/DECISIONS.md`, the higher-authority source wins. Any v3 change to the constitutional model must be proposed and reviewed explicitly; these files do not silently amend it.

## Product shape

```text
Lucas
  -> Main Assistant / Head Hermes
       -> goal-scoped ARM executives
            -> delegated agents and external harness sessions
                 -> machine gates and independent verification
       -> deterministic Recursion kernel
            -> authority, state, budgets, routing, leases, evidence, publication
  -> review, merge, credentials, and production deployment
```

The main assistant directly creates and monitors ARM executives. There is no separate AI ARM Manager. The deterministic kernel is a privileged enforcement substrate, not another reasoning actor.

## Document map

| Document | Question it answers |
|---|---|
| [PRODUCT.md](PRODUCT.md) | What is v3, who is it for, and what is outside it? |
| [ARCHITECTURE.md](ARCHITECTURE.md) | How do Head Hermes, ARMs, workers, and the kernel fit together? |
| [EXECUTIVES.md](EXECUTIVES.md) | How do executive identity, escalation, delegation, and checkpoints work? |
| [PLANNING.md](PLANNING.md) | How does Grill Me turn intent into a durable GoalSpec and plan? |
| [EXECUTION-FABRIC.md](EXECUTION-FABRIC.md) | How are models, CLIs, subscriptions, hosts, and tasks resolved? |
| [CONTEXT.md](CONTEXT.md) | How does context reuse, caching, compaction, and rehydration work? |
| [STATE.md](STATE.md) | What is canonical, durable, replayable, and recoverable? |
| [SECURITY.md](SECURITY.md) | How are sovereignty, credentials, privacy, permissions, and nodes protected? |
| [PLUGINS-AND-EDITIONS.md](PLUGINS-AND-EDITIONS.md) | What belongs in the kernel, plugins, and release bundles? |
| [CLI.md](CLI.md) | How does an owner configure and operate Recursion without an agent? |
| [TELEMETRY.md](TELEMETRY.md) | How are quality, quota, cost, context, and resource use measured? |
| [ACCEPTANCE.md](ACCEPTANCE.md) | What evidence is required before v3 may ship? |
| [ROADMAP.md](ROADMAP.md) | In what order should research and construction proceed? |
| [DECISION-REGISTER.md](DECISION-REGISTER.md) | Which session conclusions are accepted, superseded, or unresolved? |
| [REFERENCE-MATRIX.md](REFERENCE-MATRIX.md) | What should be studied in the reference harnesses? |
| [RESEARCH-HYPOTHESES.md](RESEARCH-HYPOTHESES.md) | Which claims need experiments rather than confidence? |
| [prompts/overnight-architecture-research.md](prompts/overnight-architecture-research.md) | What should the next autonomous Codex research session do? |
| [prompts/overnight-adversarial-swarm-research.md](prompts/overnight-adversarial-swarm-research.md) | How should an eight-hour Luna, Muse, and conditional Grok research swarm ground and challenge the architecture? |
| [archive/session-transcript-2026-09-02.md](archive/session-transcript-2026-09-02.md) | What human-visible conversation produced this hypothesis? |

## Status vocabulary

- `accepted-direction`: Lucas agreed to the product direction in the archived session, but a formal constitutional or implementation decision may still be required.
- `hypothesis`: plausible design awaiting repository research, external-source validation, or experiment.
- `open`: requires a material owner decision.
- `superseded`: preserved because its reasoning remains useful, but it must not drive implementation.
- `verified-current`: directly supported by the source tree at `98113d6`.

## Working rules

1. The Owner Intent Ledger is non-lossy; summaries never replace exact directives.
2. Chat transcripts are provenance, not canonical runtime state.
3. Claims about provider behavior, model availability, pricing, cache semantics, or subscription access expire unless revalidated against primary sources.
4. V2 is the measured baseline and a source of proven invariants, not a ceiling on v3.
5. V3 may be ambitious in destination while remaining incremental, reversible, and independently gated in construction.
6. Configuration is a product feature, but integrity, attribution, privacy, budget authority, and publication provenance are not optional implementation details.
7. The public repository must never contain credentials or private-project content. The transcript archive is sanitized and must receive another privacy review before publication.

## Immediate next step

Run the adversarial swarm research prompt when the requested model routes pass its fail-closed preflight. Use the single-lead overnight prompt when cross-family routes are unavailable. Either run should replace weak assumptions with evidence, identify constitutional amendments that require Lucas's review, and refine these hypotheses without beginning implementation.

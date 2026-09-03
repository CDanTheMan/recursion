---
title: Recursion v3 evidence-grounded design workspace
status: evidence-reconciled-design-and-frontier-research-foundation
last-updated: 2026-09-03
authority: non-normative until ratified
---

# Recursion v3 evidence-grounded design workspace

Recursion v3 is hypothesized as a provider-neutral autonomous-development harness and integration system. It preserves the proven v2 execution and safety invariants while making the main assistant, ARM executives, provider routes, context flow, plugins, nodes, and operator experience first-class parts of one coherent product.

This directory is a research baseline, not an implementation authorization. Where it conflicts with Lucas's current instruction, `CONTROL_PLANE.md`, or a ratified decision in `state/DECISIONS.md`, the higher-authority source wins. Any v3 change to the constitutional model must be proposed and reviewed explicitly; these files do not silently amend it.

## Product shape

```text
Lucas
  -> Main Assistant / Recursion Head
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
| [ARCHITECTURE.md](ARCHITECTURE.md) | How do the Recursion Head, ARMs, workers, and the kernel fit together? |
| [ARCHITECTURE-PROOF.md](ARCHITECTURE-PROOF.md) | Which R1–R17 claims survived the focused campaign, what remains unproved, and is the contract skeleton ready? |
| [ARCHITECTURE-OPTIONS.md](ARCHITECTURE-OPTIONS.md) | Which runtime foundations were compared, what is recommended, and what would falsify it? |
| [CURRENT-AND-MIGRATION.md](CURRENT-AND-MIGRATION.md) | What v2 actually contains, what is source-only, and how can state move without two writers? |
| [GLOSSARY.md](GLOSSARY.md) | What do the canonical actors, objects, routes and events mean, and who owns them? |
| [EXECUTIVES.md](EXECUTIVES.md) | How do executive identity, escalation, delegation, and checkpoints work? |
| [PLANNING.md](PLANNING.md) | How does Grill Me turn intent into a durable GoalSpec and plan? |
| [AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md) | What are the canonical planning objects, owners, transitions, amendment/fencing rules and replay semantics? |
| [AUTONOMOUS-PLANNING-CAMPAIGN.md](AUTONOMOUS-PLANNING-CAMPAIGN.md) | How did this documentation campaign dogfood GoalSpec, PlanRevision, DAG, packets and gates? |
| [R1-R17-EVIDENCE.md](R1-R17-EVIDENCE.md) | What persistent reconstructed evidence, contradictions, confidence and falsifiers support every R1-R17 lane? |
| [FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md](FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md) | How did the follow-on source/code campaign dogfood a GoalSpec, two Luna waves, adjudication and gates? |
| [FRONTIER-HARNESS-EVIDENCE.md](FRONTIER-HARNESS-EVIDENCE.md) | Which harness, durable-runtime, context/cache, terminal, plugin/frontend, systems and evaluation mechanisms survived, and which experiments decide adoption? |
| [M1A-WIRE-PROFILE.md](M1A-WIRE-PROFILE.md) | What exact M1A JSON field, nesting, bound, nullability, command/receipt/event and digest profile must future schemas implement? |
| [M1A-FIXTURE-ORACLES.md](M1A-FIXTURE-ORACLES.md) | What closed command/event/error grammar and symbolic oracle must M1A freeze as literal red bundles after schemas and before reducer code? |
| [SOURCE-REGISTER.md](SOURCE-REGISTER.md) | Which consequential primary-source versions, revisions, locators, limits and expiry triggers ground the synthesis? |
| [VALIDATION.md](VALIDATION.md) | What exact candidate-bound command validates claim IDs, stable sequences, links, privacy, diff scope and v2 regression? |
| [EXECUTION-FABRIC.md](EXECUTION-FABRIC.md) | How are models, CLIs, subscriptions, hosts, and tasks resolved? |
| [CONTEXT.md](CONTEXT.md) | How does context reuse, caching, compaction, and rehydration work? |
| [STATE.md](STATE.md) | What is canonical, durable, replayable, and recoverable? |
| [SECURITY.md](SECURITY.md) | How are sovereignty, credentials, privacy, permissions, and nodes protected? |
| [PLUGINS-AND-EDITIONS.md](PLUGINS-AND-EDITIONS.md) | What belongs in the kernel, plugins, and release bundles? |
| [CLI.md](CLI.md) | How does an owner configure and operate Recursion without an agent? |
| [TERMINAL-RUNTIME.md](TERMINAL-RUNTIME.md) | How do interactive detachable terminal views, persistent actors, process ownership, non-flicker rendering and termination work? |
| [INTERACTION-SURFACES.md](INTERACTION-SURFACES.md) | How do `#general`, direct ARM topics and collaborative multi-ARM conversations map to authority? |
| [TELEMETRY.md](TELEMETRY.md) | How are quality, quota, cost, context, and resource use measured? |
| [ACCEPTANCE.md](ACCEPTANCE.md) | What evidence is required before v3 may ship? |
| [ROADMAP.md](ROADMAP.md) | In what order should research and construction proceed? |
| [DECISION-REGISTER.md](DECISION-REGISTER.md) | Which session conclusions are accepted, superseded, or unresolved? |
| [REFERENCE-MATRIX.md](REFERENCE-MATRIX.md) | What should be studied in the reference harnesses? |
| [CLAIM-LEDGER.md](CLAIM-LEDGER.md) | Which research claims are supported, challenged, disputed, or expired? |
| [ROUTE-CAPABILITIES.md](ROUTE-CAPABILITIES.md) | Which provider routes were actually observed and what remains unknown? |
| [PERFORMANCE-PLAN.md](PERFORMANCE-PLAN.md) | Which resource claims remain hypotheses, and what workloads will decide them? |
| [CONSTRUCTION-RUNBOOK.md](CONSTRUCTION-RUNBOOK.md) | What is the bounded first implementation milestone and exact gate, once authorized? |
| [M1A-AUTONOMOUS-PLANNING.md](M1A-AUTONOMOUS-PLANNING.md) | What exactly is the planning-only schema/validation/in-memory replay construction candidate? |
| [RESEARCH-HYPOTHESES.md](RESEARCH-HYPOTHESES.md) | Which claims need experiments rather than confidence? |
| [RESEARCH-AGENDA.md](RESEARCH-AGENDA.md) | Which architecture-proof research lanes should the next deep campaign execute? |
| [SCIENTIFIC-RESEARCH.md](SCIENTIFIC-RESEARCH.md) | How can a research ARM find papers, reconcile claims and produce reproducible evidence? |
| [prompts/overnight-architecture-research.md](prompts/overnight-architecture-research.md) | Which superseded research prompt is retained only as provenance? |
| [prompts/overnight-adversarial-swarm-research.md](prompts/overnight-adversarial-swarm-research.md) | Which superseded swarm prompt is retained only as provenance? |
| [prompts/architecture-proof-deep-research.md](prompts/architecture-proof-deep-research.md) | What should the next focused architecture-proof Deep Research session execute? |
| [prompts/m1a-autonomous-planning-contract.md](prompts/m1a-autonomous-planning-contract.md) | What standalone prompt may build M1A only after a separate Owner authorization? |
| [archive/session-transcript-2026-09-02.md](archive/session-transcript-2026-09-02.md) | What internal human-visible conversation produced this hypothesis? This file is excluded from public releases. |

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
4. V2 is the pinned source/test comparison baseline and a source of tested invariants, not a
   measured performance/deployment baseline or a ceiling on v3.
5. V3 may be ambitious in destination while remaining incremental, reversible, and independently gated in construction.
6. Configuration is a product feature, but integrity, attribution, privacy, budget authority, and publication provenance are not optional implementation details.
7. The public repository must never contain credentials or private-project content. The
   transcript archive is internal-review provenance and is excluded from public release
   artifacts; any public provenance is generated separately and reviewed after redaction.

## Immediate next step

The reconstructed [architecture proof](ARCHITECTURE-PROOF.md) and persistent
[R1-R17 matrix](R1-R17-EVIDENCE.md) use eight Luna discovery packets and two targeted
same-family Terra adjudications. No external-family packet was used or recovered. They give a
conditional go only for the planning schema/validator/synthetic-fixture/in-memory replay
[M1A](M1A-AUTONOMOUS-PLANNING.md). Its exact wire/profile/oracle candidate passed the campaign's
deterministic gates and targeted same-family Terra recheck; construction still requires a
separate Owner-approved task.
Current constitutional conflicts and remaining Lucas decisions are recorded in
[DECISION-REGISTER.md](DECISION-REGISTER.md). No runtime implementation, migration, provider
change, terminal process, private canary, publication or deployment is authorized by this suite.

The follow-on [frontier harness evidence](FRONTIER-HARNESS-EVIDENCE.md) narrows Option 2's
privileged kernel and freezes twelve comparison/fault experiments. It does not change M1A's
planning-only boundary or prove a runtime. The next authorized construction step remains M1A-01
strict schema materialization followed by M1A-02 literal red fixtures; language, store, binary IPC,
plugin isolation, renderer and native-loop choices remain later evidence gates.

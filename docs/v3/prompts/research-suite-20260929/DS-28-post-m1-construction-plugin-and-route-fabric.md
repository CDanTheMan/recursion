---
title: DS-28 — Post-M1 construction plugin and route fabric
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not stop at a plan, outline, scope sheet, or clarification request — execute the research now and return the final report.

# DS-28 — Post-M1 construction plugin and route fabric

This is a bounded construction handoff, not a public Deep Research brief. Supplying this document is the invocation; it makes no repository or provider call on its own. This handoff is self-contained context for a repository-execution task; it is not a Deep Research session. It prepares the exact packet that would build the accepted Milestone 3 — plugin kernel and route fabric.

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

- Recursion v3 is a provider-neutral agent platform with one small privileged kernel and lazy capability plugins. The kernel owns identity and authority verification, GoalSpec/Owner-intent integrity, event ordering and canonical state writes, parent/child budget inheritance, executive and worker leases, PAUSE and revocation, evidence/provenance admission, the publication boundary and plugin capability enforcement.
- Capability plugins may provide native/external agent engines, providers and model catalogs, capacity telemetry, routing heuristics, context sources and repository indexes, compaction strategies, gates and verifiers, node transports, sandboxes and permission mappings, notifications/observers/UIs/editors, scholarly discovery, artifact stores and optional telemetry exporters. One codebase produces versioned release manifests (`core`, `standard`, `remote`, `full`, `custom`); a `full` installation does not imply maximum `sovereign` authority.
- Manifest-first capability graph: each plugin manifest declares plugin and protocol version, full artifact digest and transitive dependency-lock digest, provided and required capabilities, exclusive resources and conflicts, a configuration schema fragment, durable and ephemeral event subscriptions, isolation mode, filesystem/network/credential/model access, a CPU/memory/disk/concurrency envelope, lifecycle hooks and health probes, and provenance/license/integrity/update-source. Resolution produces a cached graph and a complete rejection explanation; cycles, ownership conflicts, ambiguous providers and missing dependencies fail before autonomous work starts, and manifest resolution and policy checks occur before any code import or installation.
- Plugin lifecycle receipts are discovered -> verified -> admitted -> staged -> active, with quarantined/rejected branches and drain-and-fence -> retired/replaced; reload is a fenced transition that advances an epoch, so old WorkPackets, leases and subscriptions fail stale and ambiguous external effects enter reconciliation. A disabled plugin performs no code execution, import or installation; credential access; network call; subprocess, thread, timer or watcher; background callback; context/tool enumeration; model turn; quota reservation/debit; spend; or unbounded event subscription. Trust tiers are T0-kernel, T1-signed-built-in, T2-signed-isolated-third-party, T3-untrusted-view and T4-external-engine/provider; a tier is an isolation and review requirement, never an authority grant.
- Event bus: plugins coordinate through typed kernel events, not direct plugin-to-plugin calls. Durable lineage events are ordered, authenticated, replayable and schema-migrated; ephemeral operational events (progress ticks, streaming deltas, health samples, UI presence) are bounded, backpressured, sampled and disposable. Plugins receive only the event types and fields permitted by their manifest and project classification, and field values, identifiers, payload sizes, timing and subscription patterns are part of the disclosure analysis. One faulty plugin cannot block the durable writer indefinitely: circuit breakers, bounded queues, timeouts, restart budgets, quarantine and degraded modes keep the kernel, state writer, PAUSE and owner CLI usable.
- v2 adapter compatibility preserves the four inspectable incompatibility responses — state_incompatibility, recommend_combinations, no_action, and notify_and_recommend — each carrying a marker with requested capability, adapter/version, missing requirement, translation loss and effective config. A request reaching an incompatible route records `status=incompatible, attempted=false, effect=none` (no execution attempted, no import/process/auth/network/quota/spend). A semantic loss map covers tools, resources, prompts/skills, hooks, authentication, UI, memory, dependencies and lifecycle. A failure after an admitted effect instead reports failed/cancelled/uncertain and cannot reuse the no-effect status.
- Route resolution: a route is an eligible combination of engine, provider, model, capacity pool, credential reference and execution mode. Independent declarations (task requirements, executive policy, model capability, engine/harness capability, provider and transport, capacity pool and billing basis, credential reference, host/node capability, sandbox and network profile, project privacy and publication policy) resolve into one immutable route. Routing plugins may only score or reorder routes the kernel has already found eligible; the kernel revalidates every proposed route immediately before launch and rejects any authority, privacy, billing or capability expansion.
- Capacity pools and billing boundary: a model-aware, account-aware capacity pool tracks billing basis (subscription, metered, local, unknown), the models and reasoning modes actually exposed, concurrent-session and rate-limit observations, reset windows and uncertainty bounds, recent health/throttle/refusal/outage signals, observable cache evidence, reservations and aggregate parent-goal consumption, privacy/training constraints, and credential-reference status without storing credentials. Opaque flat subscriptions use confidence-aware shadow prices and must never be converted to fictional dollar prices; metered pools use real configured prices with hard budget authority. Switching from a subscription/OAuth route to a metered API route is a billing-authority transition, not ordinary failover, and requires existing parent-goal authorization.
- Frozen prior slices and construction nature: M1B froze the route, plugin, process and broker contracts; M1A and M1C are likewise merged frozen and must not be restarted, rebuilt or edited. This is a construction handoff requiring repository execution (isolated worktree, branch, commits, machine-checkable gates) and independent exact-candidate verification, not a research lane. Prohibited: provider launch, plugin installation/import/activation, credential storage/logging/retrieval, a billing-authority transition or metered fallback, product language/store/framework/sandbox selection, push/publication/merge, protected-path edits, and reopening recorded Owner decisions OR-021 through OR-039.

## Purpose

Specify the first bounded construction packet for the plugin kernel and route fabric: manifest-first capability graph, trusted built-in registry, bounded third-party plugin lifecycle, typed event bus, v2 adapter compatibility, route resolver, model-aware capacity pools, billing boundary and credential references. This is blocking because the Milestone 3 gate cannot be stated or falsified until the frozen contracts M1B froze are projected into a machine-checkable construction packet with a zero-cost disabled path and refuse-before-launch behavior.

## Authority and boundaries

The shared authority constraints are in `## Baked context`. Preserve the current constitution; write proposed amendments, never edit it. M1B already froze the route, plugin, process and broker contracts; do not restart, rebuild or edit it, and treat any required extension as a separately specified bridge. M1A and M1C are likewise merged frozen and must not be reopened. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication, push or merge is authorized. Do not select a product language, store, framework or plugin-sandbox implementation. Do not reopen recorded Owner decisions (OR-021 through OR-039). This is a construction task, not a public Deep Research session: it requires repository execution (isolated worktree, branch, commits) and independent exact-candidate verification. Public Deep Research receives only public or synthetic briefs; this construction packet may reference repository paths but must never export private content, transcripts, credentials or account identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Branch, worktree and task binding

1. What exact reviewed predecessor commit is the `TASK_BASE`, and what isolated worktree, branch name and preflight sequence does the packet freeze before any edit?
2. Which exact new paths may this packet create, and how are all protected paths and the frozen M1B contracts excluded by construction?
3. How does the packet prove it did not modify M1A/M1B/M1C schemas, fixtures, oracles or wire profiles?

### Manifests, registry and lifecycle receipts

4. What manifest fields are required (plugin and protocol version, full artifact digest, transitive dependency-lock digest, provided and required capabilities, exclusive resources, config schema fragment, durable and ephemeral subscriptions, isolation mode, filesystem/network/credential/model access, resource envelope, lifecycle hooks, provenance, license, update source)?
5. How does the trusted built-in registry admit, pin and explain a built-in versus a bounded isolated third-party plugin?
6. Which lifecycle receipts distinguish manifest known, dependency eligible, admitted, loaded/imported, activated, draining, deactivated, failed and unknown cleanup?
7. How is the fenced reload transition expressed so old WorkPackets, leases and subscriptions fail stale and ambiguous effects enter reconciliation?
8. How does the kernel keep manifest resolution and policy checks before any code import or installation?

### Event bus and v2 adapter

9. How are durable lineage events separated from bounded ephemeral operational events, and how is one faulty plugin prevented from blocking the durable writer?
10. How do plugins receive only the event types and fields permitted by their manifest and project classification?
11. What is the v2 adapter compatibility contract, including the four incompatibility responses and the semantic loss map for tools, resources, prompts, hooks, authentication, UI, memory, dependencies and lifecycle?

### Route resolver, capacity pools and billing boundary

12. What independent declarations (task requirements, executive policy, model capability, engine/harness capability, provider and transport, capacity pool and billing basis, credential reference, host/node capability, sandbox and network profile, project privacy and publication policy) resolve into one immutable route?
13. How does the route resolver reject any authority, privacy, billing or capability expansion proposed by a routing plugin?
14. What does a model-aware capacity pool track, and how are opaque flat subscriptions kept as confidence-aware shadow prices rather than fictional dollar prices?
15. How is the billing boundary enforced so switching from a subscription/OAuth route to a metered API route is a billing-authority transition, not ordinary failover?

### Credential references and disabled path

16. How are credential references stored and resolved without storing or logging credentials, and how is credential visibility bounded per route and project?
17. How does the zero-cost disabled path prove no code execution, import or installation, credential access, network call, subprocess, timer, watcher, callback, context/tool enumeration, model turn, quota reservation or spend?

### Refuse-before-provider-launch and denial receipts

18. What refuse-before-provider-launch check runs against the resolved route, and how does a denial receipt record the requested capability, missing requirement, translation loss and effective config?
19. How is the bounded tool-call budget enforced per job, and how does a disallowed tool call consume budget and produce a known completed failure only after model, transport, export and cleanup qualify?

### Independent review and publication boundary

20. What independent review reproduces the exact-candidate fixtures, and how does the packet end at a local candidate commit with no push, publication or merge?

## Deliverable

A machine-checkable construction packet specification: the frozen predecessor commit, worktree and branch; allowed new paths and protected-path exclusions; the manifest, registry and lifecycle-receipt contract; the event-bus and v2-adapter requirements; the route-resolver input and rejection rules; capacity-pool and billing-boundary requirements; credential-reference handling; the zero-cost disabled-path trap; the refuse-before-provider-launch check; the denial-receipt and tool-call-budget contract; the acceptance command inventory; and the independent-review and no-push/no-merge boundary. It is a proposed packet, not an executed result.

## Non-goals

- No push, publication or merge to any branch.
- No restarting, rebuilding or editing M1A/M1B/M1C.
- No provider, model, network or paid call, and no provider launch.
- No plugin installation, import or activation.
- No product language, store, framework or sandbox implementation selection.
- No credential storage, logging or retrieval.
- No billing-authority transition or metered fallback.
- No modification of protected paths or existing specifications.
- No self-review presented as independent verification.

## Completion gate

- The predecessor commit, worktree, branch and allowed paths are frozen and machine-checkable.
- Every required manifest field and lifecycle receipt is explicit and closed.
- The fenced reload transition and stale-lease behavior are stated with expected outcomes.
- Durable and ephemeral event-bus classes are separated, with fault containment for one faulty plugin.
- The v2 adapter preserves the four incompatibility responses and the semantic loss map.
- The route resolver rejects any authority, privacy, billing or capability expansion.
- Capacity pools distinguish billing bases and never invent dollar prices for opaque subscriptions.
- The zero-cost disabled path is a hard-failure test, not a timing tolerance.
- Refuse-before-provider-launch, denial receipts and the bounded tool-call budget are all specified.
- Protected paths and M1 contracts are untouched; independent review is recorded; no push or merge occurs.

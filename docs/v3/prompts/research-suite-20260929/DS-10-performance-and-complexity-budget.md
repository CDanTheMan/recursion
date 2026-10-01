---
title: DS-10 — Performance and complexity budget
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-10 — Performance and complexity budget

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

- Recursion v3 is built as Option 2: one small native deterministic kernel with typed fail-closed adapters. The kernel owns schema versions, authority/budget checks, command idempotency, event sequencing, action admission, PAUSE epoch, credential-reference policy, verification identity and publication provenance; agent inner loops stay replaceable through engines.
- Option 1 keeps the current file/Git runtime authoritative and extracts v3 incrementally. Option 2 is the ratified kernel-plus-adapters architecture. Option 3 is a complete native harness with external CLIs reduced to provider plugins.
- Lane `R12` (whole-system performance and lean codebase) establishes baselines for startup, idle CPU/RSS/wakeups, install/binary/dependency size, imported modules, daemon/process count, event/replay/WAL behavior, CLI latency and privileged-versus-optional lines; it maps every mandatory mechanism to exactly one owner and compares monolith, microservice and small-kernel/plugin packaging.
- Lane `R17` (comparative architecture benefit and complexity budget) runs matched end-to-end scenarios against v2 and Options 1/2/3 and requires an ablation that disables each major subsystem to see which accepted outcome degrades. Each disposition is adopt, simplify, defer or delete.
- `PERF-003` is the disabled-path test: compare the core manifest to 10 and 100 installed-but-disabled plugins across startup, RSS, handles, file reads and background tasks, with a budget set before implementation. Any disabled-path code execution, import, network call, worker process or periodic work is a hard failure rather than a timing tolerance.
- `v2` is the previous-generation Recursion runtime frozen at baseline commit `98113d6`; every claimed improvement is compared against it or a named simpler baseline, and numeric budgets are set only after a baseline exists.
- Profiles: `coordinator-small` is the small authority/event-writer/scheduler/observer class; `interactive workstation` is the heavier development class. Both are defined by measured CPU, memory, disk and latency, not by a vendor model.
- The optimization vector is reported dimension by dimension: authority/safety/privacy, verified quality, recovery/replay, owner/operator cost, quota/tokens/money, context/cache efficiency, latency/throughput, host resources, terminal interaction, portability/configurability, code and maintenance surface, and extensibility/idle cost. No scalar may hide a failed hard floor.
- Evidence discipline: missing counters are `unavailable`, never zero; every recommendation names a competing option, a decisive falsifier and what it does not prove.

## Purpose

Establish v2 and reference baselines across startup, idle resource use, install size, imported modules, process count, event/replay behavior, CLI latency and privileged versus optional code, then decide whether v3's added machinery is justified. Agenda lanes R12 and R17 block a lean core and any mandatory subsystem until every mechanism has one owner, a measured benefit and an ablation.

## Authority and boundaries

The authority, scope, privacy and evidence-discipline constraints for this lane are restated in `## Baked context` above and govern this work. This prompt authorizes a report only: no runtime, provider, authentication, configuration, cron, PAUSE, spending, deployment, publication or merge action. Option 2 is owner-ratified and is not reopened; this lane measures whether it and its mechanisms earn their cost. Keep public/synthetic briefs free of private project content, transcripts, local paths, credentials or account/infrastructure identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. What exact v2/reference baseline commit and command establish each dimension: startup, idle CPU/RSS/wakeups, install, binary and dependency size, imported modules, daemon and process count, event/replay/WAL behavior, CLI latency, and privileged versus optional lines or complexity?
2. Which counters are observable on the coordinator-small and workstation profiles, and which must be reported `unavailable` rather than zero?
3. How are the coordinate optimization dimensions reported separately so no scalar hides a failed quality, authority, privacy, resource or recovery floor?
4. How is every mandatory mechanism mapped to exactly one owner, and where do duplicate state, routing, process, context or plugin paths remain?
5. Which measured budgets may be set only after a baseline, and what falsifier invalidates each budget?
6. For monolith, microservice and small-kernel/plugin packaging, what matched end-to-end scenario, total resource cost and maintenance burden distinguish the options?
7. How does the ablation study work: disable each major subsystem and identify which accepted outcome degrades, with a named outcome and floor?
8. Which current mechanisms lack a user-visible, safety or measured efficiency benefit and therefore must not become mandatory core?
9. How do disabled paths (unselected engine, provider, node, plugin, indexer, contributor route) prove zero model or network call, zero plugin import, zero worker process and zero periodic work, per the Option 2 disabled-path commitments and PERF-003?
10. What is the per-mechanism and per-option disposition rule (adopt, simplify, defer, delete), and what evidence blocks promotion?
11. How are quality, owner review burden and maintenance cost included so an efficiency gain that shifts defects or review cost downstream is rejected?
12. Which Option 2 implementation-boundary falsifiers remain open, and which measurement would resolve each?
13. What is the minimum measurement set that could still change the Option 1, 2 or 3 choice, and what is already decisive without further spending?

## Deliverable

A source-pinned report with: a claim table (claim, source, version/date, classification, confidence, expiry trigger); the v2/reference baseline definition; an owner map for each mandatory mechanism; an ablation plan and results template; a monolith versus microservice versus small-kernel/plugin comparison; a recommendation tied to a named competing option and decisive falsifier; and open Owner questions.

## Non-goals

- No runtime implementation and no benchmark executed.
- No language, store, binary IPC or framework selection.
- No numeric product minimum, budget or threshold invented.
- No aggregate score hiding a failed hard floor.
- No reopening of the ratified Option 2 architecture.
- No personal hardware inventory treated as design data.
- No provider, model or route calls.
- No modification of the canonical performance plan or any protected path.

## Completion gate

- The v2 baseline commit and command are pinned for each dimension.
- Every claimed improvement is compared against v2 or a named simpler baseline.
- Each mandatory mechanism has one owner, one ablation and a user-visible, safety or measured-efficiency justification.
- Budgets are set only after measurement and carry a falsifier.
- Disabled-path cost has a hard-failure test rather than a timing tolerance alone.
- Every recommendation names adopt, simplify, defer or delete plus a decisive falsifier.
- Hard floors are reported before any trade-off or aggregate summary.
- Protected paths are untouched; privacy and secret scan are clean.

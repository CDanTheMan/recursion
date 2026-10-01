---
title: DS-06 — Capacity admission and review debt
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-06 — Capacity admission and review debt

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

- **Focus.** This lane defines which measured signals bound new branches, worktrees and concurrent ARM output, and how machine pressure is separated from human review debt so admission can adapt without inventing a constant. It is research lane R8 of the Recursion v3 agenda.
- **ARM.** A durable goal-scoped executive that plans and delegates bounded work inside one approved GoalSpec. Concurrency here means how many such executives and their branches/worktrees may be active at once.
- **Accepted direction.** `OR-008`: branch/worktree backlog limits are measured and configurable rather than fixed universally at 75, which is a historical unique-unreviewed-branch cap and not a v3 constant. Preserve an owner hard ceiling and human-review-capacity signals.
- **Admission shape.** Adaptive admission maintains independent machine, pool, queue and review credits: `admission = min(machine_headroom, pool_headroom, goal_budget, review_credit, owner_hard_ceiling)`.
- **Hysteresis.** Expansion requires a stable interval below measured low-water marks; contraction/refusal occurs at a high-water mark; emergency floors block admission immediately. Reserve synthesis, verification and recovery capacity before discovery.
- **Safety rule.** A large machine must not generate work faster than evidence can be reviewed: branch creation is cheap, so machine headroom alone must never be treated as protecting review capacity.
- **Pruning.** Automatic pruning touches only proven merged, superseded or content-identical branches and must never delete unpushed, referenced or review-only work; remote refs and published review branches need explicit care.
- **Observability honesty.** Counters that are not observable must remain `unavailable` rather than assumed zero.
- **Boundary.** This lane is measurement and policy research only; the owner-set hard ceiling and any numeric threshold remain Lucas's decision, and no threshold is presented as a default.

## Purpose

Decide which measured signals bound new branches, worktrees and concurrent ARM output, and how machine pressure is separated from human review debt so admission can adapt without inventing a constant. Agenda lane R8 blocks a construction contract for branch/worktree admission and safe pruning until this is evidence-backed.

## Authority and boundaries

The authority, scope and privacy constraints are restated in `## Baked context`; read nothing else in preparation. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. This lane is measurement and policy research only; the owner-set hard ceiling and any numeric threshold remain Lucas's decision.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. Which measured Git and worktree signals (status/index latency, changed bytes, disk and inode growth, process and handle counts) best bound concurrent branches and worktrees on the coordinator-small and workstation profiles?
2. What unreviewed-change volume and owner review service rate can be measured without exporting private code content, and how do they relate to branch age and integration-conflict frequency?
3. Which signal separates machine pressure (CPU, RAM, disk, I/O, pool quota) from human review debt, and what is the correct behavior when the two disagree?
4. How should admission combine machine headroom, pool headroom, goal budget, review credit and an owner hard ceiling, per the `admission = min(...)` shape restated in `## Baked context`?
5. What hysteresis, low/high-water marks and one-slot-at-a-time expansion or contraction prevent oscillation and reviewer whiplash?
6. How do stale-branch age, repeated integration conflicts and abandoned worktrees feed safe pruning rules that never delete unpushed, referenced or review-only work?
7. What is a safe pruning protocol for merged, superseded, stale or orphaned worktrees and branches, including remote refs and published review branches?
8. Which counters are observable per host and per route, and which must remain `unavailable` rather than assumed zero?
9. How can a review service-rate trace be modeled or controlled without exposing private content or transcripts?
10. How does the rule "a large machine must not generate work faster than evidence can be reviewed" become specific, testable refusal conditions?
11. How should refusal, queue age and inferred limits surface through CLI concepts such as `recursion branch inventory|explain|prune-safe` without writing canonical state from a view?
12. What falsifier shows adaptive admission genuinely outperforms a fixed limit, and what would show it merely hides a growing backlog?
13. What evidence would justify deleting the adaptive policy in favor of a simpler owner-set hard ceiling?

## Deliverable

A source-pinned report with: a claim table (claim, source, version/date, classification, confidence, expiry trigger); measurable machine and review signals with units and observability; candidate admission functions with hysteresis and refusal conditions; options with tradeoffs; a recommendation tied to a named competing option and decisive falsifier; and open Owner questions. No threshold is presented as a default.

## Non-goals

- No branch, worktree or Git implementation; no `git` command is run.
- No change to current capacity policy or the constitution.
- No owner hard-ceiling number selected; 75 is historical input, not a v3 constant.
- No private repository content, paths, transcripts, host names or account identifiers in any public or synthetic brief.
- No provider, model or route selection.
- No pruning, deletion or mutation of any real branch or worktree.
- No schema or CLI change.
- No claim that machine headroom alone protects review capacity.

## Completion gate

- Primary sources pinned by version/date; local structural claims separated from public evidence.
- Every machine and review signal traces to an observable measurement or is explicitly `unavailable`.
- Every recommendation names a competing option and a decisive falsifier.
- The adaptive-versus-fixed comparison has a baseline, workload and stopping rule.
- Owner decisions are not reopened and no number is promoted to a default.
- Protected paths are untouched; privacy and secret scan are clean.
- The report states which signals were measurable locally versus modeled.

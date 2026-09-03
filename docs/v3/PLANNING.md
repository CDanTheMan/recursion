---
title: Recursion v3 planning and Grill Me hypothesis
status: hypothesis
last-updated: 2026-09-03
---

# Recursion v3 planning and Grill Me hypothesis

## Purpose

Planning is a first-class, configurable phase of autonomous development. Its job is not to create an impressive document; it is to reduce semantic uncertainty, establish measurable success, expose trade-offs before implementation, and give ARM executives a stable contract they can execute without hallucinating product direction.

Planning may be disabled for already-bounded work. When enabled, it can range from seconds to hours.

`off` removes the interactive planning phase; it does not remove provenance or admission. Execution still requires an authenticated, complete GoalSpec with parent goal, authority, exact source, allowed paths, non-goals, budget, privacy/egress policy, and machine-checkable gates. If any field is absent or ambiguous, admission stops.

## Grill Me protocol

Grill Me is Recursion's interactive goal-compilation protocol. Each cycle:

1. Identifies one consequential ambiguity.
2. Explains why it affects architecture, quality, cost, privacy, or operation.
3. Presents materially different options and their trade-offs.
4. Makes one reasoned recommendation.
5. Separates the recommended default from what remains configurable.
6. Names failure modes, evidence needs, and a falsifier where possible.
7. Records the owner's exact answer in the Owner Intent Ledger.
8. Updates the decision register and affected specification immediately.
9. Generates the next highest-value unresolved question.
10. Periodically performs a cross-decision consistency audit.

The protocol must not ask a hundred questions and leave the answers trapped in chat. Durability after each answer is part of the feature.

## Modes

| Mode | Behavior |
|---|---|
| `off` | Accept an already complete GoalSpec or bounded task without interactive planning |
| `quick` | Ask only questions that block safe execution |
| `standard` | Resolve important product, acceptance, route, privacy, and budget choices |
| `deep` | Add reference research, alternatives, experiments, and consistency checks |
| `exhaustive` | Hours-long collaborative design with scientific hypotheses and repeated hardening |

Each mode has configurable time, subscription-capacity, token, and metered-cost sub-budgets. Planning remains inside the parent goal's aggregate authority. Default planning consumes included/subscription capacity only. Exhaustion returns a resumable draft; it does not silently lower quality or begin execution.

## Owner Intent Ledger

Every owner directive is stored losslessly with:

- exact text;
- source event and timestamp;
- intended scope;
- status: active, fulfilled, rejected, clarified, or superseded;
- link to any clarifying or superseding directive;
- affected GoalSpec and decision identifiers.

Summaries and compacted plans may reference this ledger but cannot replace it. When instructions conflict, the system surfaces the conflict and follows the established authority precedence; it never silently harmonizes them.

## GoalSpec

An accepted GoalSpec is an immutable, versioned execution contract. At minimum it contains:

- measurable outcome and acceptance suite;
- repository and exact starting source;
- scope, allowed paths, and explicit non-goals;
- privacy classification and egress policy;
- authority and permission profile;
- eligible providers, routes, models, nodes, and fallback rules;
- aggregate subscription and metered budget authority;
- resource and concurrency policy;
- required checkpoints and verification depth;
- branch, publication, merge, and deployment boundaries;
- falsifier, terminal conditions, and required human seams.

Execution receives a content-addressed snapshot. Later changes create an amendment linked to the old version. Restrictions may tighten immediately; widened permissions, privacy exposure, or spending require explicit authority and apply at a safe checkpoint.

## Planning ownership

The clean default boundary is:

- Lucas defines intent, values, acceptance, risk, spending, and final decisions.
- Head Hermes compiles the strategic GoalSpec, assigns the goal, and monitors outcomes.
- The ARM executive creates and maintains the implementation DAG and tactical plan.
- Workers execute one bounded node.
- Independent verifiers judge evidence against the GoalSpec.

Head-authored detailed implementation plans remain a configurable mode, not the only architecture.

## Plan verification

Plan verification is risk-scaled and resource-aware:

- low-risk bounded tasks: deterministic schema and repository checks;
- ordinary product work: an independent critique or targeted evidence review;
- security, authentication, control-plane, deployment, and migration work: multiple perspectives plus explicit human review where authority requires it.

Paid CI is never assumed. Local gates, remote-node gates, hosted CI, model review, and human validation are independent capabilities. A plan declares which evidence is required and which capabilities are unavailable. It must not report an unavailable gate as passed.

## Failure behavior

A task gate failure does not automatically PAUSE the entire system. It returns to its ARM with exact evidence. The ARM may retry only when it can name new information or a materially different action. Repeated failure, semantic ambiguity, exhausted authorized recovery, or conflicting evidence escalates to Head Hermes. If Lucas is the required actor, development under that affected authority stops until direction arrives.

Global PAUSE remains a separate operator/control-plane mechanism.

## Retry novelty contract

Every retry must identify at least one of:

- new evidence;
- corrected hypothesis;
- changed implementation strategy;
- changed eligible route justified by capability or continuity;
- narrowed task;
- repaired environment or dependency;
- explicit owner amendment.

Rephrasing the same attempt is not novelty. The scheduler should stop repetitive quota burn before another model turn is admitted.

## Planning outputs

A completed planning phase produces:

1. an accepted or explicitly draft GoalSpec;
2. an Owner Intent Ledger slice;
3. a decision register update;
4. a research/evidence appendix;
5. an initial ARM profile and execution policy;
6. a milestone DAG with machine-checkable gates;
7. unresolved questions and required human seams;
8. a construction prompt or task set that does not depend on the original chat.

## Learning without rewriting intent

Recursion may learn which question ordering, task size, plan form, and review pattern correlate with better outcomes. It may recommend defaults and reorder unasked questions. It may not silently alter accepted requirements, gates, privacy, permissions, budgets, or authority.

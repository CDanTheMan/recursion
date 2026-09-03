---
title: Recursion v3 acceptance hypothesis
status: hypothesis
last-updated: 2026-09-03
---

# Recursion v3 acceptance hypothesis

## Principle

Successful runs cannot prove the absence of failures. V3 release evidence must combine scenario coverage, invariant/property testing, fault injection, independent review, resource measurement, and private soak experience. A model's completion claim is never a release gate.

This document defines categories and provisional gates. Numeric performance budgets require baseline measurement before ratification; invented thresholds would create false confidence.

## Documentation gate

- Product, architecture, executive, planning, execution, context, state, security, plugin, CLI, telemetry, acceptance, roadmap, and decision documents agree on actor names and authority.
- Every mandatory feature maps to a schema, implementation owner, test, operational evidence, configuration surface, and documentation page.
- Every reference-derived behavior records source, license posture, adoption/change/rejection, and verification date.
- Accepted, superseded, hypothesized, and unresolved decisions are distinguishable.
- Public artifacts contain no private-project source, prompts, identifiers, credentials, or sensitive telemetry.

## Contract gate

- Schemas reject missing/unknown fields, invalid lineage, widened child authority, budget overflow, stale source, untrusted routes, and malformed artifacts.
- Logical actor identity is independent from model, provider session, and route.
- GoalSpec amendment, safe checkpoint, compaction epoch, executive replacement, and publication intent are content-addressed and replay-safe.
- The plugin capability graph resolves deterministically and fails with complete explanations.
- Event admission rejects unauthenticated principals, stale fencing tokens, duplicate command ids, non-monotonic sequences, and authority/GoalSpec mismatches.
- Each aggregate has one canonical writer; migration fixtures fail if legacy and v3 paths can both mutate the same transition or external effect.
- Version migrations are deterministic, reversible where promised, and tested against archived fixtures.

## Execution scenarios

At minimum, end-to-end fixtures cover:

- direct, reviewed, hierarchical, and adaptive execution depth;
- multiple tasks with independent worktrees and serialized integration;
- subscription exhaustion during a model turn and at a checkpoint;
- authorized and unauthorized metered fallback;
- provider refusal, throttle, outage, malformed output, and stale descriptor;
- same-route resume, cross-route handoff, executive replacement, and process restart;
- gate failure with novel repair and repeated non-novel retry rejection;
- verifier disagreement resolved through new evidence;
- unreviewed branch ceiling and safe-prune refusal;
- PAUSE/revocation races before dispatch, during work, before gates, and before publication;
- disk full, torn write, stale lease, duplicate result, node loss, and controller recovery;
- private project egress denied to an ineligible route;
- plugin crash/quarantine while unrelated work continues;
- privileged plugin digest/signature mismatch, dependency substitution, and rollback;
- planning mode `off` rejecting an incomplete or unauthenticated GoalSpec and preserving provenance for a complete one;
- full-access profile selected by the owner without leaking unrelated credentials or crossing control-plane, billing, privacy, publication, merge, or deployment seams not separately granted;
- contributor-route admission capturing the exact outbound byte set and rejecting private identifiers even when prompt scanning misses them;
- verifier collision where implementer and verifier share a family, provider, host, session, or evidence channel;
- review branch publication with no protected-branch merge or deployment.

## Context and compaction gate

- Active owner directives, GoalSpec, authority, privacy, budget, gates, source, blockers, and external effects survive every compaction cycle exactly or by verified immutable reference.
- Every omitted evidence item can be rehydrated by digest and authorization.
- Repeated compaction does not compound summary drift beyond the accepted benchmark.
- Exactly one active compaction owner exists per route.
- Native, deterministic, and hybrid modes have comparative recall, cost, latency, and cache-affinity measurements.
- A provider/model switch can resume from a capsule without hidden chain-of-thought state.

## Security and privacy gate

- Credentials never enter Git, canonical event payloads, model prompts, published evidence, support bundles, or telemetry exports.
- Remote work packets are authenticated, scoped, expiring, fenced, and replay protected.
- Controller, executor, observer, and verifier roles are independently grantable and revocable.
- Project data classification and deny-by-default egress are enforced before provider transmission.
- Plugin permission expansion and update trust changes require explicit owner action.
- Public observer/event output resists content, membership, size, and timing disclosure tests for private projects.
- The lightweight enrollment preflight completes within the measured startup budget and consumes zero model tokens.
- The full conformance suite is reproducible for official releases but is not an ordinary local startup gate.

## Performance and resource gate

Measure at minimum on the target coordinator class and one interactive workstation:

- disabled optional component footprint;
- idle daemon CPU/RSS/wakeups and disk writes;
- CLI startup and common read-command latency;
- SQLite transaction, projection, WAL, backup, and restore behavior;
- scheduler/admission latency under increasing queued work;
- worker/process cleanup and descriptor/plugin lazy load;
- adaptive concurrency response to CPU, RAM, disk I/O, and foreground pressure;
- context packaging, hydration, and compaction cost;
- node transfer volume and recovery;
- 10–12 hour bounded autonomous-session stability.

Thresholds are set from a measured v2/system baseline and documented owner expectations. Any optional subsystem failing its Resource Discipline Contract is disabled or excluded from the affected edition.

## Quality and efficiency gate

Compare v3 against v2 on representative scrubbed tasks:

- first-review acceptance;
- post-completion defect rate;
- repair iterations and false-green gates;
- subscription/metered use per accepted change;
- repeated repository scanning and context input;
- compaction recall and rehydration;
- human review minutes;
- plan churn and useful escalation rate;
- machine load and elapsed time.

V3 does not need to dominate every dimension. Each shipped profile must improve its declared objective without violating hard integrity and quality floors.

## Installation and CLI gate

- Fresh `core`, `standard`, `remote`, `full`, and representative `custom` installs are reproducible from one tagged source revision.
- Disabled components are physically absent or demonstrably idle.
- Schema-driven wizard, manual file editing, validation, migration, explanation, and rollback agree.
- Common local use works without remote enrollment or a full conformance run.
- Route, queue, capacity, resource, config, context, and capability explanations require no model call.
- Dangerous/full-access profiles remain available with exact, reviewable effects.
- The configured verifier-independence policy is displayed and enforced; the minimum acceptable separation is blocked on Lucas's decision rather than inferred.

## Private canary and publication

The first canary may use a private repository, but public release evidence must use synthetic or scrubbed fixtures. Private source, branch names, hashes, logs, prompts, and telemetry are not published.

The private canary demonstrates recovery and operational usability; it does not prove universal correctness. Publication provenance is mandatory in v3: every review branch traces to GoalSpec, source, routes, checkpoints, gates, verifier evidence, and publisher receipt.

## Release decision

One public v3 release is built incrementally and cut atomically only when:

- all mandatory scenarios pass on the exact candidate;
- supported edition combinations pass;
- no unresolved release-blocking security/privacy issue remains;
- performance budgets are met on the declared hardware classes;
- migration/rollback and backup/restore are proven;
- independent reviewers agree with evidence or disagreements are resolved empirically;
- Lucas accepts the review branch and performs the protected merge/deployment seams.

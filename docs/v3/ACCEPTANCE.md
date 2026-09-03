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
- Every command/action binds the operative constitution-policy reference, GoalSpec/grant/route
  digests, idempotency identity, PAUSE/revocation epochs and aggregate fence. The actuator
  revalidates immediately before an effect.
- A possible external acceptance followed by crash is `ambiguous`, blocks dependent effects and
  is reconciliation-only; state restoration never reports the effect undone.
- `PERF-001` through `PERF-011` have one immutable experiment-registry mapping, and a result
  cannot bind to another workload revision or unavailable denominator.
- A fabric-only state fixture is labeled as such and cannot pass the OR-015 broad rehearsal gate.

## M1A autonomous-planning gate

M1A is accepted only against the 23 fixture outcomes/falsifiers and twelve machine gates in
[M1A-AUTONOMOUS-PLANNING.md](M1A-AUTONOMOUS-PLANNING.md), after M1A-01 freezes the literal red
bundles required by the closed [M1A fixture-oracle blueprint](M1A-FIXTURE-ORACLES.md). The
canonical lifecycle and transition rules are
[AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md); this section does not redefine them.

The required closure is: authenticated OwnerIntent → Owner-accepted GoalSpec → admitted immutable
PlanRevision/DAG → ready TaskNode → deterministically derived bounded WorkPacket → exact
GateResult → bounded retry/replan/escalation → exact plan-verifier decision → terminal-verified
plan. Incomplete/authentication failures, widening, cycles/missing dependencies, ownership
conflicts, stale packets/leases, non-novel retries, exhaustion, missing/downgraded verification,
quota/provider blocks, route replacement, PAUSE epochs, ambiguous effects, duplicate commands,
replay corruption, unauthorized parent mutation and unknown fields/policies must all fail in the
specified way.

M1A performs no provider/model/network call, terminal/process launch, plugin execution, SQLite or
Git operation, publication or external effect. Inert records used in failure fixtures do not
prove those subsystems. The current immediate PAUSE is operative; future profiles must remain
representable but non-operative. A same-family Terra review is valuable adjudication but not
cross-family independence.

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
- measured/configurable branch admission, owner hard ceiling, review-backlog pressure and
  safe-prune refusal;
- every future-supported PAUSE policy and revocation race before dispatch, during work, on a
  disconnected node, before gates, and before publication;
- disk full, torn write, stale lease, duplicate result, node loss, and controller recovery;
- private project egress denied to an ineligible route;
- plugin crash/quarantine while unrelated work continues;
- privileged plugin digest/signature mismatch, dependency substitution, and rollback;
- unsigned local plugin installation, warning/acknowledgement, digest rotation, configured
  one-step or staged consent, and sensitive-capability refusal outside its digest-aware grant;
- plugin quota/route/spend declaration, attribution, configured ceilings and refusal of any
  unacknowledged metered transition;
- planning mode `off` rejecting an incomplete or unauthenticated GoalSpec and preserving provenance for a complete one;
- maximum Full Access selected by the owner with each control-plane, credential, billing,
  privacy, publication, merge, deployment, service and grant-administration capability exactly
  granted, bounded and attributed; self-grant is possible only when `grant-admin` was explicit,
  and every mutation produces a durable before/after receipt;
- contributor-route admission capturing the exact outbound byte set and rejecting private identifiers even when prompt scanning misses them;
- verifier collision where implementer and verifier share a family, provider, host, session, or evidence channel;
- review branch publication with no protected-branch merge or deployment;
- direct ARM and shared multi-ARM conversation with duplicate, out-of-order, edited and deleted
  transport messages without authority or actor identity changing; a named ARM's bounded step
  lease cannot change the overall goal, room membership, authority envelope, conflict policy,
  ARM lifecycle or Head-owned strategic escalation.

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
- Capability descendants cannot widen parent scope, limit, lifetime or delegation. Grant
  mutation requires explicit `grant-admin`, a current fence/epoch, single-use step-up where
  configured and exact before/after receipts; trust-root, constitution, audit retention and
  audit erasure remain distinct capabilities.
- Retention tests distinguish local deletion, key destruction, cache/replica/backup/disconnected
  propagation, legal hold and expiry-bound copies. No recoverable copy may coexist with a
  `verified-complete` disposition.

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

Each performance result binds its exact workload, host/route/config/source revisions, unit of
analysis, warm/cold policy, baseline/treatment, exclusion rule and hard quality/safety floor.
Unavailable provider/cache/subscription counters are null, not zero. No aggregate performance
score can hide failed authority, privacy, evidence, correctness, recovery or accessibility.

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

## Scientific research gate

- A research ARM creates a versioned question, decision target, gap matrix and falsifiable claim
  ledger before synthesis.
- Paper, standard, dataset, documentation and source records preserve title, author/publisher,
  date/version, persistent identifier, retrieval date, provenance and access/license boundary.
- Adversarial fixtures include fabricated citations, retracted/corrected papers, outdated
  versions, inaccessible/paywalled sources, contradictory findings and sources whose population
  or workload does not apply.
- Consequential sources are opened and independently checked; search snippets and model
  narratives are not evidence.
- External mechanism evidence, local structural applicability and empirical Recursion fit are
  classified separately.
- Experiments preregister baseline, treatment, controls, routes, metrics, quality floors,
  analysis and stop rules; raw observations and transformations are reproducible.
- Research stops on diminishing returns and can conclude `unknown`; it does not consume quota
  indefinitely to manufacture confidence.
- Private inputs, institutional credentials and copyrighted full text obey project egress,
  storage, quotation and export policy.
- `SourceRecord` separates discovery, identity, retrieval, verification, access and editorial
  state. `ResearchClaim` uses typed support, contradiction, qualification, update,
  metadata-only and inapplicability edges with exact locators and revalidation triggers.
- Accepting a fabricated identifier, retracted-as-current or stale version, metadata-only or
  inaccessible source, inapplicable transfer, unverifiable extraction, dropped contradiction or
  privacy/copyright violation is an automatic failure; the correct unresolved result is
  `unknown`.

## Installation and CLI gate

- Fresh `core`, `standard`, `remote`, `full`, and representative `custom` installs are reproducible from one tagged source revision.
- Disabled components are physically absent or demonstrably idle.
- Schema-driven wizard, manual file editing, validation, migration, explanation, and rollback agree.
- Common local use works without remote enrollment or a full conformance run.
- Route, queue, capacity, resource, config, context, and capability explanations require no model call.
- General, ARM, worker, graph, event and system terminal views can attach concurrently; closing
  a view never ends work, and explicit stop/kill controls terminate the complete owned process
  tree or report/quarantine what remains.
- Interactive rendering passes non-flicker, preserved-input, resize, Unicode, reconnect,
  high-output, slow-client, plain-text/accessibility and bounded-resource tests on supported
  Windows and Linux terminals.
- Protocol fixtures prove daemon epoch and per-stream cursor replay/reset, one input/resize
  lease, idempotent commands, bounded credit/queues and durable-event preservation before any
  wire ABI or client is called supported.
- The v3.0 matrix proves native Windows ConPTY/process ownership and native Linux
  PTY/process-group behavior. Git Bash, Neovim terminals and later compatibility targets are
  labeled tested, experimental or unsupported from evidence rather than aspiration.
- Future product defaults proposed for post-amendment conformance are `checkpoint` PAUSE, trusted bounded autonomy, digest-aware plugin grants
  and detachable multi-terminal operation. `full` installation does not imply `sovereign`.
- Dangerous/full-access profiles remain available with exact, reviewable effects. If explicit
  `grant-admin` is enabled, self-grant mutations are schema checked and receipt backed; they do
  not silently rewrite history.
- The configured verifier-independence policy is displayed and enforced. Routine downgrades are
  explicit; release, security-sensitive, control-plane and irreversible-effect work blocks on a
  missing verifier unless Lucas supplies an exception receipt. Missing verification never passes.

## Private canary and publication

The first canary may use a private repository, but public release evidence must use synthetic or scrubbed fixtures. Private source, branch names, hashes, logs, prompts, and telemetry are not published.

`CANARY-01` first performs test-only characterization of one stable, deterministic,
non-safety-critical business rule. Writes are limited to its tests and fixtures, every route is
private-approved, an independent verifier performs a clean rerun, and the only deliverable is a
local candidate commit. It does not publish, merge, deploy or touch an external effect.

The private canary demonstrates recovery and operational usability; it does not prove universal correctness. Publication provenance is mandatory in v3: every review branch traces to GoalSpec, source, routes, checkpoints, gates, verifier evidence, and publisher receipt.

## Release decision

One public v3 release is built incrementally and cut atomically only when:

- all mandatory scenarios pass on the exact candidate;
- supported edition combinations pass;
- no unresolved release-blocking security/privacy issue remains;
- performance budgets are met on the declared hardware classes;
- migration/rollback and backup/restore are proven;
- independent reviewers agree with evidence or disagreements are resolved empirically;
- for the initial private deployment, Lucas accepts the review branch and performs the protected
  merge/deployment seams unless a later explicit Full Access grant and operative constitutional
  amendment authorize a different reviewed profile.

---
title: Recursion v3 telemetry and optimization hypothesis
status: hypothesis
last-updated: 2026-09-07
---

# Recursion v3 telemetry and optimization hypothesis

## Mark 2 accounting observations — proposed 2026-09-07

A usage record binds scope/role/attempt, provider/account pool, executing harness/interface/build,
host, config revision, unit/quantum, observation source/time/window, cumulative-versus-delta
semantics and uncertainty. Normal and recovery consumption have separate monotonic ledgers;
shared-pool reservations prevent child/fork duplication. Provider resets affect availability,
not already-spent task allowance. MKR-016/MKR-020.

Claude `model_usage` is estimated query-pipeline usage, includes subagents/compaction, excludes
outside helpers such as the permission classifier/token counting, and is cumulative across
streaming turns (SRC-V3-220). Reconcile the latest total and crash/reset offsets; summing every
result double-charges. Other harness token/quota observations need their own adapters.
Missing data cannot support a claim of savings or a credible strict reservation.

Stop telemetry distinguishes request, acknowledgment, local settlement, remote enforcement and
external effect uncertainty. Update telemetry distinguishes available/staged/activated/per-host
landed, readable history, newest-work preservation and resumability. Evidence is attributable
without exporting private prompts, credentials, paths, account IDs or infrastructure details.

## Accounting and observation provenance

Record engine/build/model/effort, route and compaction epochs, tool-schema identity, auth/account
class (never credentials), counter origin and availability. Separate API charges, provider-reported
subscription debit, inferred capacity and unavailable values; null is not zero. Normalize whether
input totals include cache reads/writes before summing costs. Count refresh/compactor/retry calls
as ordinary requests exactly once. Report human review and host resource costs separately unless
explicit valuation weights are accepted. FND-010/FND-011.

Measure bridge/control latency, input stability and resource attribution separately from
inference latency. Visible activity is an observation, not percent-complete or an accepted result.
The accounting equation, units and no-future-work/zero-miss edge cases are in
`analysis.foundation.economics` of [evidence.json](foundation-research/evidence.json). FND-017.

## Objective

Telemetry exists to improve verified development and preserve scarce capacity, not to maximize agent activity. It must answer:

> Which authorized route, executive policy, context strategy, and delegation pattern produces the best accepted result for this class of task under the owner's quality, privacy, quota, cost, latency, and machine constraints?

## Correlation

Every execution segment carries stable identifiers:

- `project_id`;
- `goal_id` and GoalSpec version;
- `arm_run_id`;
- `task_id` and `segment_id`;
- `route_id` and resolved route digest;
- provider-native session identifier when available;
- source, checkpoint, candidate, evidence, and verifier identifiers.

Provider session IDs are disposable optimizations. Recursion lineage remains authoritative.

## Measurement families

### Quality

- first-review acceptance;
- machine-gate reliability and false-green rate;
- repair count and plan churn;
- defects found after ARM completion;
- verifier disagreement and resolution outcome;
- regression incidence after integration;
- human review minutes per accepted result.

### Capacity and cost

- route/model/pool requests and observed usage;
- subscription throttle and reset evidence;
- metered tokens and actual cost;
- capacity reservations, borrowing, and denied admissions;
- provider-reported cache reads/writes when available;
- estimated input avoided by semantic artifact reuse, labeled as estimate;
- compaction calls and their own pool usage.

### Context quality

- artifact reuse and invalidation;
- context-package bytes/tokens;
- decision, constraint, and blocker recall after compaction;
- rehydration misses;
- native-session reuse versus fresh-session outcome;
- context-related verifier findings.

### System performance

- controller CPU, RSS, database latency, WAL growth, disk I/O, and disk use;
- plugin idle/active footprint;
- scheduler/admission latency;
- node transfer volume and hydration latency;
- interactive foreground degradation;
- terminal-view count, render/input latency, wakeups, bounded-buffer pressure, coalesced or
  dropped presentation events and process-tree cleanup;
- privileged/core code and dependency size, install/binary footprint, startup imports and
  disabled-path work;
- queue wait and end-to-end elapsed time.

### Research quality

- primary versus secondary source coverage;
- persistent-identifier, version and retrieval completeness;
- fabricated, corrected/retracted and inapplicable-source detection;
- contradictory evidence preserved/resolved;
- experiment reproducibility and negative-result retention;
- human/source-verifier corrections per accepted research claim.

### Continuity and safety

- refusal, timeout, throttle, outage, and fallback causes;
- checkpoint and restart success;
- stale/duplicate/replay rejection;
- privacy/egress and permission denials;
- owner escalations, useful-alert rate, and unnecessary interruption rate.

## Evidence providers

Usage data comes through a read-only telemetry evidence-provider interface. Candidate adapters include:

- provider/CLI native usage events;
- a future, separately source/license-qualified `ccusage` adapter where its evidence proves applicable;
- official provider usage APIs;
- Cursor/OpenCode/Gemini-specific collectors;
- local resource monitors;
- deterministic token estimators as explicitly labeled fallback.

`ccusage` is preserved only as an owner-accepted name for a possible future adapter. This
campaign did not pin its repository, version, license, data model, or supported histories, so
it contributes no verified architecture claim and must be researched before admission. Any
future usage reconciler is an optional evidence source, not a canonical billing abstraction.
No collector may infer zero use merely because a CLI omits token counters.

## Route learning

The adaptive scorer may learn from local outcomes by task class. It can reorder eligible routes within an approved envelope. It cannot:

- add or authenticate a provider;
- enable metered billing or provider training;
- widen permissions or egress;
- lower required verification;
- rewrite GoalSpec;
- modify its own hard policy.

Learning state is versioned, explainable, resettable, and exportable. Shadow or offline evaluation precedes automatic use of a new scorer.

## Privacy

Default telemetry is local and metadata-minimal. Full prompts, raw tool output, source snippets, and private artifact content are excluded from metrics tables and external exporters. Project policy controls retention and opt-in export. Aggregation must resist revealing private repository membership through hashes or rare labels.

## Dashboards and reports

Operator views should prioritize:

- what is running and why;
- what is waiting and what capacity would unblock it;
- parent-goal budget and reserved final-phase capacity;
- accepted output versus unreviewed branch backlog;
- recent quality regressions or route failures;
- context compaction health;
- system headroom and predicted throttle risk;
- exact actions requiring Lucas.

The morning brief remains bounded. Detailed evidence is linked, not pasted.

## Evaluation discipline

Every claimed optimization needs a baseline, workload, controlled comparison, confidence/uncertainty statement, and falsifier. V2 at `98113d6` is the initial baseline. Optimization defaults should be promoted only when they improve the intended Pareto profile without degrading mandatory integrity or acceptance gates.

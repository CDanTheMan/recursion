---
title: Recursion v3 telemetry and optimization hypothesis
status: hypothesis
last-updated: 2026-09-02
---

# Recursion v3 telemetry and optimization hypothesis

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
- queue wait and end-to-end elapsed time.

### Continuity and safety

- refusal, timeout, throttle, outage, and fallback causes;
- checkpoint and restart success;
- stale/duplicate/replay rejection;
- privacy/egress and permission denials;
- owner escalations, useful-alert rate, and unnecessary interruption rate.

## Evidence providers

Usage data comes through a read-only telemetry evidence-provider interface. Candidate adapters include:

- provider/CLI native usage events;
- `ccusage` for supported Claude/Codex-compatible local histories where its evidence is applicable;
- official provider usage APIs;
- Cursor/OpenCode/Gemini-specific collectors;
- local resource monitors;
- deterministic token estimators as explicitly labeled fallback.

`ccusage` is useful as one optional evidence source, not a canonical billing abstraction. No collector may infer zero use merely because a CLI omits token counters.

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

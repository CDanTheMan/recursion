---
title: Recursion v3 performance and resource hypothesis plan
status: experiment-plan
last-updated: 2026-09-03
---

# Recursion v3 performance and resource hypothesis plan

No v3 performance improvement was measured in this campaign. This document defines workloads,
metrics and decision rules so later implementation cannot convert expectations into facts.

## Target profiles

| Profile | Evidence boundary | Intended role |
|---|---|---|
| Coordinator-small | Historical v2 design target: 2 vCPU/4 GB class; remeasure the actual host before a gate | Authority/event writer, scheduler, observer, light verification; not a universal build host |
| Interactive workstation | Campaign observation: 32 logical processors, 64 GB RAM, about 34 GB free before workers | Development, heavier tests, multiple external CLIs and optional local models while preserving interactivity |
| Registered worker | No fixed hardware assumption | Bounded build/test workload under a declared resource profile |

The named vendor/SKU is not the contract. A profile is accepted only by measured available
CPU, memory, disk, I/O and latency. Deployment state was not inspected.

## Hypotheses and decision rules

| ID | Hypothesis | Workload and metrics | Pass decision | Falsifier |
|---|---|---|---|---|
| PERF-001 | One SQLite WAL writer plus read projections fits coordinator-small | Replay 1M small events; 4 read observers; checkpoint and restart; measure p50/p95/p99 append, busy time, WAL size, RSS, rebuild time | Set numeric budget from baseline, then require p99 and restart within it with 25% RAM/disk headroom | Sustained lock contention, unbounded WAL, failed checkpoint or headroom loss |
| PERF-002 | Content-addressed artifacts keep hot database pages bounded | Store repeated and unique context/evidence payloads; measure DB growth, artifact dedupe, lookup latency, GC correctness | DB growth tracks metadata, duplicate payload is not copied, missing artifact fails closed | Payload duplication in DB or GC removes referenced evidence |
| PERF-003 | Disabled plugins have near-zero cost | Compare core manifest to 10/100 installed-but-disabled plugins; startup, RSS, handles, file reads and background tasks | Difference stays inside a budget established before implementation; zero plugin code executed | Discovery/import/network/background work occurs while disabled |
| PERF-004 | Event-driven admission preserves coordinator responsiveness | Burst 1k queued tasks plus heartbeats, no workers; measure CLI status latency, CPU, queue drain and fairness | Observer remains responsive and CPU returns near idle after burst | Busy polling, starvation or growing resident task objects |
| PERF-005 | Route/capacity changes only at checkpoints reduce churn | Synthetic quota/health oscillation; count route flips, lost work, repeated prompts and time to stable decision | No mid-effect switch; bounded flip count; each retry has novelty or backoff | Oscillation burns repeated quota or violates route affinity |
| PERF-006 | Context capsules reduce repeated provider input without fidelity loss | Fixed repository/task corpus across fresh, same-route and cross-route continuation; tokens, cache counters where exposed, answer/gate quality | Improvement only if measured input/resource falls and quality floor holds | Summary drift, intent loss, private cross-project reuse or unverifiable cache claim |
| PERF-007 | Coordinator can shed optional work before integrity work | Induce memory/disk/queue pressure; measure order of shedding and authority/PAUSE/status latency | Analytics/indexing stop first; authority/event writer and emergency control remain available | Integrity path is killed, blocked or silently drops a durable event |
| PERF-008 | External engines belong off coordinator when workload is heavy | Same bounded task on coordinator and worker; wall time, coordinator RSS/CPU/I/O, transfer volume, failure recovery | Placement rule is based on measured total resource and recovery cost, not wall time alone | Remote transfer/reconciliation costs exceed saved coordinator headroom |

## Required fault matrix

Every benchmark includes warm/cold start, clean/dirty shutdown, duplicate command, stale lease,
disk-full threshold, reader crash, writer crash and corrupted artifact reference. Remote tests
also include disconnect before send, ambiguous send, duplicate result and stale fencing epoch.
Performance success never overrides a failed safety result.

## Context and provider measurement rules

- Server-side prompt/cache controls are recorded only when the exact route exposes them. API
  controls are not assumed available through an OAuth CLI.
- Provider-native session state is an affinity hint, not a portable capsule.
- `ccusage` or reconstructed prices are reconciliation evidence, not live subscription
  capacity or billing truth.
- Contributor/training-eligible routes receive only public fixtures.
- Every result records engine, provider, model, account reference, pool, host, sandbox, source
  revision and descriptor revision so a route change cannot masquerade as an optimization.

## Workstation campaign observation

Three native Luna workers plus the lead and one bounded external Muse process were admitted
conservatively. No sustained local pressure was observed during the research campaign, but
that qualitative observation is not a benchmark and is not a v3 concurrency default. Future
tests reduce concurrency on sustained interactive latency, memory pressure, thermal pressure,
disk pressure or provider throttling.

## Reporting

Publish raw machine-readable samples, workload revision and confidence intervals beside a
one-page result. Report regressions and safety failures even when average throughput improves.
Do not compare models or providers unless prompt, task, route controls and quality gate are
comparable.

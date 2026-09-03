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
| PERF-009 | Branch/worktree admission can adapt to machine and human review capacity better than a universal count | Vary active worktrees, branch age, changed bytes, Git/index operations, integration conflicts and owner review service rate; measure disk/inodes, status latency, queue age and review debt | Policy uses measured signals plus hysteresis and an owner hard ceiling, protects review/integration capacity, and outperforms a fixed limit on declared profiles | Oscillation, hidden review backlog, excessive scanning, or a larger machine generates unreviewable output faster |
| PERF-010 | Several detachable terminal views can remain responsive without multiplying worker/model cost | Attach general, ARM, worker, event and system clients during idle and high-output runs; measure input/frame latency, CPU, RSS, wakeups, buffer growth, coalesced/dropped presentation events and daemon backpressure | Closing/reopening views preserves cursors and actors; added views stay within a preregistered UI budget, no view launches model/index work, and slow clients cannot block canonical state | Flicker/input corruption, unbounded buffers, canonical-writer delay, orphaned processes, or cost grows with each passive view |
| PERF-011 | A Sol director with up to eight bounded Luna researchers and two targeted Terra adjudicators improves verified research evidence per quota unit over Sol-heavy or uncontrolled parallelism | Freeze one public research corpus and compare bounded profiles such as Sol-only, Sol+4 Luna and the selected Sol+8 Luna+2 Terra ceiling; record exact model/effort, source validity, contradictory evidence, duplicate work, input/cache/output usage where exposed, account-window change, wall time and human review | The selected profile preserves preregistered quality/source floors, improves verified non-duplicate findings per observed quota unit, and leaves a declared synthesis/verification reserve | Coordination/context duplication erases savings, same-family agreement hides errors, quota exhausts before adjudication, or review debt grows faster than accepted evidence |

### Experiment controls identified by architecture proof

| ID | Control that must be frozen before measurement |
|---|---|
| Controls for PERF-001 | Event-size/distribution, SQLite version, filesystem, `synchronous` mode, page/checkpoint settings and hardware. Long-lived readers must test WAL checkpoint starvation. |
| Controls for PERF-002 | Count database and artifact-store bytes together; vary repeated/unique corpora and test reachability/GC. Moving bytes out of SQLite is not itself a storage win. |
| Controls for PERF-003 | Randomize cold/warm trials and separate manifest discovery from import/execute/network/background work. Disabled code execution is a hard failure even when timing noise is small. |
| Controls for PERF-004 | Define a matched polling baseline, poll interval, observer count and burst distribution. A historical implementation with no equivalent cannot be invented as the baseline. |
| Controls for PERF-005 | Separate route stability from provider-cache savings. Only directly exposed usage/cache counters may enter the latter result. |
| Controls for PERF-006 | Compare raw, native-only, deterministic-capsule and hybrid treatments over repeated compaction cycles; exact required-field recall is a hard floor. |
| Controls for PERF-007 | Record pressure source, process/cgroup/Job accounting and every shedding stage. A durable-event loss or unavailable PAUSE is an automatic failure. |
| Controls for PERF-008 | Use matched hardware/network or paired crossover and include transfer, hydration, recovery and total-system cost. |
| Controls for PERF-009 | Supply a measured or controlled owner-review service-rate trace; machine-only capacity cannot prove review protection. |
| Controls for PERF-010 | Fix OS, terminal, event rate and render workload and test 0/1/5/10/20 views, slow clients, restart and process escape. |
| Controls for PERF-011 | Freeze the corpus, rubric, finding key, blind review, observed quota denominator and stopping margin. Without a Sol-only baseline this campaign is architectural evidence, not a performance result. |

Quota efficiency is a vector, not a fabricated currency. Report verified non-duplicate findings
separately per directly observed input/output/reasoning token, account-window change when
available, human-review minute, adjudication turn and wall-clock/resource vector. Exact duplicates
use a canonical claim/source/version/locator key; semantic near-duplicates require adjudication.
An unavailable denominator is `null/unavailable`, never zero.

Adaptive admission maintains independent machine, pool, queue and review credits:

```text
admission = min(machine_headroom, pool_headroom, goal_budget,
                review_credit, owner_hard_ceiling)
```

Expansion requires a stable interval below measured low-water marks; contraction/refusal occurs
at a high-water mark; emergency floors block admission immediately. Reserve synthesis,
verification and recovery capacity before discovery. Thresholds, intervals and one-slot-at-a-time
hysteresis are derived from baselines and owner expectations rather than invented here.

## Required fault matrix

Every benchmark includes warm/cold start, clean/dirty shutdown, duplicate command, stale lease,
disk-full threshold, reader crash, writer crash and corrupted artifact reference. Remote tests
also include disconnect before send, ambiguous send, duplicate result and stale fencing epoch.
Performance success never overrides a failed safety result.

## Context and provider measurement rules

- Server-side prompt/cache controls are recorded only when the exact route exposes them. API
  controls are not assumed available through an OAuth CLI.
- Provider-native session state is an affinity hint, not a portable capsule.
- Any future `ccusage` adapter or reconstructed price is unverified reconciliation evidence,
  not live subscription capacity or billing truth; `ccusage` itself was not source/license
  reviewed in this campaign.
- Contributor/training-eligible routes receive only public fixtures.
- Every result records engine, provider, model, account reference, pool, host, sandbox, source
  revision and descriptor revision so a route change cannot masquerade as an optimization.
- The Sol+8 Luna+2 Terra research profile is a concurrency ceiling and experiment treatment,
  not a promise that all workers launch simultaneously or that Terra supplies cross-family
  independence. Run bounded waves when machine, provider, quota or review headroom is lower.

## Workstation campaign observation

Eight native Luna workers were admitted in two waves of four after a health check; the public-only
Muse review and two targeted Terra adjudicators ran after discovery. The initial workstation
observation was 32 logical processors, 63.12 GiB memory with about 34 GiB free and about 653 GiB
free disk. A later bounded check still showed about 33.6 GiB free memory and 652.7 GiB free disk.
No sustained local pressure was observed, but these point observations are not a benchmark,
provider-capacity proof or v3 concurrency default. Future tests reduce concurrency on sustained
interactive latency, memory, thermal, disk, provider, quota or review pressure.

## Reporting

Publish raw machine-readable samples, workload revision and confidence intervals beside a
one-page result. Report regressions and safety failures even when average throughput improves.
Do not compare models or providers unless prompt, task, route controls and quality gate are
comparable.

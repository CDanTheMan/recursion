---
title: Recursion v3 performance and resource hypothesis plan
status: experiment-plan
last-updated: 2026-09-06
---

# Recursion v3 performance and resource hypothesis plan

## Foundation follow-up designs — 2026-09-05

The [eight foundation designs](foundation-research/experiments.json) add explicit comparisons for
compaction, total cache economics, fleet allocation, resource/UI cost, native/upstream adapter
control, remote faults, setup and upgrade certification. All are preregistered exploratory
proposals, not executed trials. Preserve the earlier formal-model → language → storage priorities.

Match total budgets, count failures/retries/compaction and human review, and keep attempts nested
within independent tasks. Freeze route/OS/build/model/evaluator and workloads before execution;
run blinded power simulation before a powered claim. Stronger models or larger fleets are not
verification by voting. Historic benchmark rankings and developer/agent studies motivate controls
but do not establish current Recursion quality, performance or market effects. FND-015/FND-018.

The Owner's desktop-lag report motivates component attribution, including UI, engine subprocess,
language server, indexer, watchers, tools and inference. No headless speedup, GPU dependency or
cache-heartbeat savings is presumed. FND-011/FND-012.

No v3 performance improvement was measured in this campaign. This document defines workloads,
metrics and decision rules so later implementation cannot convert expectations into facts.

## Canonical optimization decision rule

OR-024 refines OR-017: the Owner's default ranking is responsiveness, subscription efficiency,
then task completion, subject to correctness, authorization, resource limits and recoverability.
Preserve the full vector below and the existing safety/privacy/effect/quality floors. Report
Pareto comparisons and explicit tradeoffs; no hidden scalar weights or invented thresholds.
A recommended default needs measured evidence and a disposition for every regression or
unavailable denominator. Material tradeoffs remain visible for Owner decision.

Compare each supported upstream engine directly with the same engine orchestrated by Recursion.
Include planning, failed attempts, verification, compaction, coordination and recovery. Keep
money, subscription allowance, machine resources and human review capacity distinct. Measure
session reuse, context/evidence reuse, delegation, placement/transfer, scheduling/reservations,
verification throughput, idle CPU/RSS, storage growth and disk writes, including interactions.
The [platform trials](foundation-research/platform-round/trials.json) define four scenarios,
including upstream-only role closure. These remain preregistered designs, not results.

| Dimension | Required observation |
|---|---|
| authority, safety, privacy, effects | violations, ambiguous outcomes, stale actions, isolation and policy-conformance results |
| verified quality | accepted gate quality, escaped defects, verifier disagreement and falsifier outcomes |
| recovery and replay | restart/reconciliation success, replay parity, bounded data loss and failure containment |
| owner/operator cost | review minutes, intervention count, comprehension/error probes and backlog age |
| quota, tokens and money | provider-reported counters where exposed, account-window change and metered receipts; unavailable is not zero |
| context/cache efficiency | directly observed reads/writes, reusable bytes/tokens, fidelity misses and invalidations |
| latency and throughput | p50/p95/p99 control, input, append, task and recovery latency plus accepted throughput |
| host resources | CPU, RSS, disk, I/O, network, wakeups, processes and handles |
| terminal interaction | frame/input latency, flicker/gap count, Unicode/input correctness and accessibility results |
| portability/configurability | supported platform/route matrices, fail-closed unknowns and owner-change cost |
| code and maintenance surface | privileged/total code, dependencies, binary/install size, upgrade work and defect density |
| extensibility/idle cost | plugin/frontend compatibility and disabled-path imports, reads, work, processes and calls |

This section is canonical for optimization comparisons. Product and campaign documents project
it rather than defining competing weights.

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

### Frontier harness comparison suite

The code-informed campaign adds the following preregistered comparisons without expanding the
M1A implementation scope. Their canonical detail is in
[FRONTIER-HARNESS-EVIDENCE.md](FRONTIER-HARNESS-EVIDENCE.md#preregistered-experiment-queue).

| Experiment | Required comparison and interpretation |
|---|---|
| `EXP-FHAR-01` | Minimal native loop versus typed adapters across two materially different engines; do not infer that owning the product contract requires rebuilding provider loops. |
| `EXP-FHAR-03` | Raw rescan, deterministic capsule, native compaction and hybrid under cold/warm and same/fresh sessions; only exact route counters support provider-cache results. |
| `EXP-FHAR-07` | Fixed-model component ladder for ACI, planner, DAG delegation, verifier and bounded novel retry; equal total budget and owner-review burden are mandatory. Unit of inference, pilot, power simulation, margins, analysis and stopping are frozen by [`PROTO-FHAR-01-R1`](FRONTIER-HARNESS-EVIDENCE.md#proto-fhar-01-r1--corrected-attribution-repetition-and-stopping-rule). Attempts are nested within unique tasks and never inflate the independent sample. |
| `EXP-FHAR-08` | Fresh/rotating held-outs, clean state, frozen evaluator/environment hashes, overlap audit and hierarchical family/task/attempt uncertainty under `PROTO-FHAR-01-R1`; contaminated or grading-incomparable benchmark versions are separate strata or excluded. |
| `EXP-FHAR-09` | 0/10/100 installed-but-disabled capabilities with import, credential, network, process/thread/watcher, context and quota traps. |
| `EXP-FHAR-10` | CPython/Rust/Go implementations of the same deterministic reducer/replay/fault workload on frozen Windows/Linux hosts. Language documentation is not a result. |
| `EXP-FHAR-11` | JSONL plus content-addressed artifacts versus single-writer SQLite WAL metadata plus the same artifacts, counting all bytes and recovery faults. |
| `EXP-FHAR-12` | Trusted built-in, isolated third-party plugin and sandboxed view through disable, crash, reload, stale fence and protocol mismatch. |

Every comparison reports the full canonical optimization vector, paired practical effect and
uncertainty, all attempts and all hard-floor failures. A result that improves quality but increases
review time, quota or resource use may be non-dominated; it is not silently declared optimal.

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
- As reverified 2026-09-03, OpenAI's API exposes model-dependent prefix caching,
  `prompt_cache_key`, retention controls and cached-token counters; Anthropic exposes
  automatic/explicit breakpoints, TTL choices and read/write counters; Gemini distinguishes
  implicit and explicit cached content and exposes cached-token metadata. These controls are not
  uniform or portable and expire on endpoint/model/account/SDK/CLI/provider-policy change.
- No API document establishes Codex OAuth CLI cache behavior, subscription debit or
  cross-provider cache reuse; those values remain `unknown` without exact route evidence.
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

## Workstation campaign observations

The earlier architecture-proof campaign admitted eight native Luna workers in two waves of four
after bounded checks. Before wave 1,
the point observation was 32 logical processors, 63.12 GiB memory with 33.17 GiB free and 650.72
GiB free disk. Between waves the host answered the combined check in 2.6 seconds, with 32.84 GiB
free memory and 650.63 GiB free disk; the localized CPU counter was unavailable and was not
guessed. The read-only usage surface showed 20% used in its visible 10,080-minute window at both
checks. No Contributor route was used. These observations are not a sustained benchmark,
provider-capacity, entitlement, billing, token-denominator, efficiency or v3 concurrency result.
The exact receipts are in
[AUTONOMOUS-PLANNING-CAMPAIGN.md](AUTONOMOUS-PLANNING-CAMPAIGN.md).

The frontier-harness campaign repeated the two-wave limit. Its point receipts were 32 logical
processors, 31.39/63.12 GiB free memory and 647.14 GiB free disk before wave one, then
30.85/63.12 GiB and 644.57 GiB before wave two. The read-only usage surface showed 23% used in
its visible 10,080-minute window; no credit or metered route was enabled. The observations do not
establish sustained throughput, worker efficiency or account economics. Exact receipts are in
[FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md](FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md).

## Reporting

Publish raw machine-readable samples, workload revision and confidence intervals beside a
one-page result. Report regressions and safety failures even when average throughput improves.
Do not compare models or providers unless prompt, task, route controls and quality gate are
comparable.

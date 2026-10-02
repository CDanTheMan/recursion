---
title: R-O — Backend performance and configurability engineering
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-O — Backend performance and configurability engineering

This is a backend-engineering handoff for accepted Owner decisions D-018, D-019, D-022, D-024 and
D-031, with D-021 and D-033 as constraints, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It treats backend performance and configurability as a
first-class concern and consolidates the optimization vector of `OR-024` in
[DECISION-REGISTER.md](../../DECISION-REGISTER.md) into one measurable program. It builds on the
preregistered workloads of [PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md), on the
platform/config lane [R-L](R-L-interface-platform-cli-tui-gui.md), and on the plugin-portability
findings in [R-A](../dot-research-20261002/R-A-plugin-portability.md); it must extend rather than
restate them and must not reopen their requirements.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone agent harness and a harness
orchestrator that delegates through other harnesses. Hermes-led control was retired on
2026-09-28 (state/DECISIONS.md D-017); Hermes is an optional upstream integration, not the
executive control plane. Workers are bounded executors. An implementer's own PASS is never
acceptance; independent review is required, and missing verification is never a pass.
`CONTROL_PLANE.md` is the operative constitution; a research session may propose amendments
but must never edit it. No research session performs implementation,
provider/model/authentication/configuration changes, spending, deployment, publication or
merge.

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

- The exact thing to design: a **backend performance and configurability engineering program** —
  the measurements, budgets and acceptance rules that decide how the deterministic backend
  behaves, not a set of implementation choices. It consolidates `OR-024`'s optimization vector
  and the `PERF-001`…`PERF-011` workloads already preregistered in
  [PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md) into one program with hard floors first.
- `OR-024` (in [DECISION-REGISTER.md](../../DECISION-REGISTER.md)) is canonical: the default
  ranking is **responsiveness, then subscription efficiency, then task completion**, subject to
  correctness, authorization, resource limits and recoverability. Preserve privacy/quality/
  effect floors, full-vector reporting, unavailable denominators and **no hidden scalar weights**.
  A regression or no-benefit outcome is a first-class result, not a failure to be smoothed away.
- The optimization dimensions that must be compared in one place, each with its source lane or
  preregistered experiment and its own competing option and falsifier:
  - **language/runtime** — `FU-01` / `DS-18` / `EXP-FHAR-10` (G-01); no runtime selected.
  - **canonical store** — `FU-02` / `DS-21` (`G-02`); segmented JSONL plus CAS versus SQLite WAL
    plus CAS; no store selected.
  - **broker/IPC** — `FU-05` / `DS-23` (`G-05`); the four freeze blockers and the native
    Windows/Linux chaos matrix; no protocol frozen.
  - **configuration and propagation** — `DS-13` and the `G-09` conformance gap; the shared
    resolver and effective-revision propagation; no syntax selected.
  - **plugin/route integration overhead and the integration tax** — R-A / `EXP-FHAR-09` /
    `DS-04` / the disabled-path zero-effect invariant; porting savings are an unmeasured
    hypothesis (D-033), never assumed.
  - **adaptive capacity** — `DS-06` (`G-21`) and `PERF-004`/`PERF-009`; admission, hysteresis and
    review-credit behaviour on measured signals, with a fixed-limit baseline.
  - **telemetry and honest accounting** — `DS-26` (`G-25`) and the canonical optimization vector;
    counters are `null/unavailable` unless directly observed, never zero, and no reconstructed
    price becomes billing truth.
- D-018 requires no ecosystem lock-in, so each dimension must be compared candidate-neutrally and
  none may hard-bind to a vendor, store or runtime. D-019 requires comprehensive capability but
  lean delivery: performance is measured for what is built and enabled, with disabled paths
  proven inert, and no capability activates or spends by default.
- D-022 fixes one pause/stop vocabulary (Aggressive/Full/Lazy plus
  `checkpoint`/`interrupt`/`drain`); every performance workload must preserve the integrity path,
  canonical append, Stop and recovery, and a durable-event loss or an unavailable PAUSE is an
  automatic safety failure regardless of throughput. D-024 requires honest continuity and
  accounting: an optimization claim must not hide a continuity break, and D-031 forbids any
  vendor-sabotage or unmeasured savings claim.
- Already accepted target profiles from [PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md):
  **coordinator-small** (historical 2 vCPU/4 GB class; remeasure before a gate) and
  **interactive workstation** (campaign-observed 32 logical processors / 64 GB class), plus a
  registered-worker profile without a fixed hardware assumption. The named vendor/SKU is not the
  contract; a profile is accepted only by measured available CPU, memory, disk, I/O and latency.
- Already accepted regimes and freeze rules: idle and high-output; cold/warm start; clean/dirty
  shutdown; the required fault matrix (duplicate command, stale lease, disk-full threshold,
  reader/writer crash, corrupted artifact reference, remote disconnect/ambiguous send/duplicate
  result/stale fencing epoch); and the freeze-before-outcome rule for OS, sink drain rate,
  logging/instrumentation mode, route/build/config/host/capacity and order.
- Already accepted reporting rules: unique task as the independent unit with attempts/messages
  nested; retain failed and censored attempts, all helpers, verification, recovery, human review
  and downstream corrections; report the full canonical vector with paired practical effect and
  uncertainty; never let performance success override a failed safety result.
- Evidence status: no language/store/broker decision, no capacity point and no optimization
  measurement exists for v3. `G-08` notes the coordinator-small profile is a target, not a
  demonstrated capacity point. Every numeric budget below is to be produced by measurement or
  explicitly marked `unknown`, never invented.

## Purpose

Produce the decision-ready **backend performance and configurability engineering program** for
Recursion. The lane consolidates the `OR-024` optimization vector across language/runtime,
canonical store, broker/IPC, configuration/propagation, plugin/route integration overhead and
the integration tax, adaptive capacity, and telemetry/honest accounting; defines measurable
budgets **per profile** (coordinator-small, interactive workstation, registered worker) and
**per regime** (idle, first-use, steady, high-output, recovery, fault); specifies a performance
conformance program that checks **hard floors first** and reports the full vector with **no
scalar score**; and fixes reproducible workload identities so a result can be independently
rerun. Every recommendation names a competing option, a decisive falsifier — including explicit
**no-benefit** and **regression** outcomes — and what it does not prove. It does not select a
language, store, broker, configuration syntax or vendor, does not qualify any route, and
executes no provider call or benchmark.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, broker, protocol, transport,
configuration syntax or vendor.** Do not decide an Owner question recorded in D-018, D-019,
D-021, D-022, D-024 or D-033. No provider, model or account call is made; no credential or
account is touched; no live benchmark, destructive trace or deployment is run. Do not invent
numeric thresholds; derive them from a measured baseline or mark them `unknown`. Do not let a
throughput or latency improvement override a failed safety, privacy, authority or effect result,
and do not smooth a regression or a no-benefit outcome into an apparent win. No claim of measured
advantage, entitlement or porting savings is authorized; `ccusage` and any reconstructed price
remain `unknown` and are not billing truth.

## Inputs to read

None from this repository: the `OR-024` vector, the `PERF-001`…`PERF-011` preregistered workloads
and profiles, the `G-01`/`G-02`/`G-05`/`G-08`/`G-09`/`G-21`/`G-25` gaps, the accepted interface and
terminal requirements and the D-018/D-019/D-021/D-022/D-024/D-031 context are summarized in
`## Baked context` above, and no repository, connector or private-source access is assumed. The
session must, however, retrieve the public sources it cites — the language/runtime, store and
broker comparison documentation, the relevant OS performance and power-management documentation
(CPU, memory, I/O, wakeups, cgroup v2 and Windows Job Object accounting), the configuration/
canonical-serialization specifications (for example JSON Schema 2020-12 and RFC 8785), and the
public plugin/extension and telemetry documentation — and pin each claim to a URL and retrieval
date. Prefer the candidate-neutral specifications already named by this packet over any vendor
benchmark.

## Research questions

### Consolidating the optimization vector

1. How is `OR-024` expressed as one measurement program with the full vector (authority/safety/
   privacy/effects; verified quality; recovery and replay; owner/operator cost; quota/tokens/
   money; context/cache efficiency; latency and throughput; host resources; terminal interaction;
   portability/configurability; code and maintenance surface; extensibility/idle cost), such that
   no hidden scalar weight is introduced and an unavailable denominator stays `null/unavailable`?
2. How are the dimensions jointly compared — language/runtime (`FU-01`), canonical store
   (`FU-02`), broker/IPC (`FU-05`), configuration/propagation (`DS-13`), plugin/route integration
   overhead and the integration tax (R-A), adaptive capacity (`DS-06`) and telemetry
   (`DS-26`) — without multiplying every fixture by every configuration, and what is the bounded
   screening order (deterministic dimensions first) and its falsifier?
3. How is the **integration tax** defined and measured: the added startup, idle, memory, file,
   process, network and quota cost of each installed-but-disabled and each enabled plugin or
   route, such that a disabled path provably executes no plugin/model work and a porting claim
   (D-033) is a measured cost rather than an assumption?

### Budgets per profile and regime

4. What measurable budgets should each profile carry — coordinator-small, interactive
   workstation, registered worker — for startup, idle wakeups/CPU/RSS/handles, first-use,
   steady-state latency and throughput, memory and disk growth, and recovery, including the
   headroom rule (for example a stated percentage of RAM/disk/WAL before a gate) and the
   requirement to remeasure the actual host before accepting a profile?
5. What measurable budgets should each regime carry — idle, first-use, steady, high-output,
   recovery and the fault matrix — and how are p50/p95/p99 control, input, append, task and
   recovery latencies, canonical-append delay, queue high-water marks and coalesced/dropped
   counts expressed without a single scalar score?
6. How do the deterministic-kernel invariants compose with performance: the one-writer fence and
   monotonic epoch, canonical append before any presentation coalescing, the integrity path
   surviving pressure (`PERF-007`), adaptive capacity with hysteresis and a fixed-limit baseline
   (`PERF-004`/`PERF-009`/`DS-06`) and the rule that a durable-event loss or unavailable PAUSE is
   an automatic failure?

### Performance conformance program

7. What is the **hard-floor-first** conformance order — correctness, authorization/privacy,
   resource and recovery floors qualify a candidate before any speed comparison — and how are
   floors written so they cannot be traded for throughput?
8. How is a performance claim made reproducible: the frozen OS, sink type/drain rate, logging and
   instrumentation mode, route/build/config/host/resource/capacity, cold/warm order, unique-task
   independent unit with nested attempts, retained failed/censored attempts, helpers,
   verification, recovery and human review, and a preregistered confirmatory size before held-out
   outcomes?
9. What **workload identities** are required so a result is independently rerunnable — a named,
   versioned workload revision with its fixture corpus, evaluator hash, environment hash and
   stopping rule — and what negative trace shows a result was contaminated, grading-incomparable
   or tuned after seeing the winner?
10. How are no-benefit and regression outcomes recorded and dispositioned, including a default for
    an unavailable denominator, a material non-dominated tradeoff escalated rather than silently
    chosen, and a regression in review time, quota or resources treated as a real result even
    when average throughput improves?

### Telemetry and honest accounting

11. How are counters kept honest: directly observed reads/writes and provider-reported counters
    only where the exact route exposes them; API money, subscription-window change and machine
    resources kept distinct; `null/unavailable` never zero; no reconstructed price (for example
    from an optional reconciliation adapter such as `ccusage`) treated as billing truth?
12. How does telemetry floor the design rather than decorate it — deterministic zero-model
    status, provider-free measurement, privacy-scoped artifacts only, and a stated
    `unknown-until-measured` set (local PSI-equivalent pressure, portable wakeup counts,
    route-level capacity metrics and host monetary cost) that no budget may pretend to have?

### Falsifiers and acceptance

13. For each consolidated dimension, language/runtime, store, broker/IPC, configuration,
    integration overhead, adaptive capacity and telemetry, what is the decisive falsifier,
    including the explicit no-benefit outcome, and what would eliminate the candidate before any
    benchmark?
14. What provider-free acceptance fixtures or evidence checks let an independent verifier accept
    the program's budgets and rules, and what would show the program merely restated `OR-024` or
    a vendor benchmark without measurement?

## Deliverable

A backend performance and configurability engineering program containing: a **consolidated
optimization vector** section that states the `OR-024` dimensions, their source lanes or
preregistered experiments (language/runtime `FU-01`/`DS-18`, canonical store `FU-02`, broker/IPC
`FU-05`, configuration/propagation `DS-13`/`G-09`, plugin/route integration overhead and the
integration tax R-A, adaptive capacity `DS-06`, telemetry/honest accounting `DS-26`) and the
no-scalar-score, unavailable-is-not-zero rule; a **budget** section with measurable budgets per
profile (coordinator-small, interactive workstation, registered worker) and per regime (idle,
first-use, steady, high-output, recovery, fault), each a named metric with a stated derivation or
an `unknown` disposition; a **hard-floor-first conformance program** that orders correctness,
authorization/privacy, resource and recovery floors before speed comparisons and forbids trading
a floor for throughput; a **reproducible workload-identity** section (versioned workload
revision, fixture corpus, evaluator/environment hashes, independent unit, freeze rules and
stopping rule); a **telemetry/honest-accounting** section; and a **falsifier/no-benefit/
regression** section with a provider-free acceptance check. Each recommendation names a competing
option, a decisive falsifier and what it does not prove. No language, store, broker,
configuration syntax or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, broker,
  protocol, transport, configuration syntax or vendor.
- No invented numeric threshold or budget; every number is derived from a measured baseline or
  marked `unknown`, and a profile is not accepted before its actual host is measured.
- No live benchmark, destructive trace, deployment or provider/model/account call; no credential
  or account is touched; every fixture is synthetic and provider-free.
- No hidden scalar weighting, no vendor-sabotage claim (D-031) and no savings claim without
  measurement; a reconstructed price is not billing truth.
- No performance success that overrides a failed safety, privacy, authority or effect result; a
  durable-event loss or unavailable PAUSE is an automatic failure.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that porting an existing plugin or runtime is cheap; the integration tax and any
  porting saving remain hypotheses with falsifiers (D-033).
- No new executive tier, no separate AI "ARM manager", and no second portfolio executive.
- No reopening of D-018, D-019, D-021, D-022, D-024 or D-033, and no reopening of the accepted
  requirements or preregistered workloads in `PERFORMANCE-PLAN.md`, `DECISION-REGISTER.md` or
  `GAPS.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The consolidated vector covers language/runtime (`FU-01`/`DS-18`), canonical store (`FU-02`),
  broker/IPC (`FU-05`), configuration/propagation (`DS-13`/`G-09`), plugin/route integration
  overhead and the integration tax (R-A), adaptive capacity (`DS-06`) and telemetry/honest
  accounting (`DS-26`), preserves the `OR-024` ranking and full vector, and introduces no scalar
  score; an unavailable denominator is `null/unavailable`.
- The budget section defines measurable budgets for coordinator-small, interactive workstation
  and registered-worker profiles and for idle, first-use, steady, high-output, recovery and fault
  regimes, each with a stated derivation or an `unknown` disposition, and states the headroom and
  remeasure-before-gate rules.
- The conformance program checks hard floors (correctness, authorization/privacy, resource and
  recovery) before any speed comparison, forbids trading a floor for throughput, and treats a
  durable-event loss or unavailable PAUSE as an automatic failure.
- The workload-identity section requires a named, versioned workload revision with fixture
  corpus, evaluator/environment hashes, a unique-task independent unit with nested attempts,
  retained failed/censored attempts, frozen environment and order, and a preregistered stopping
  rule.
- The integration-tax subsection proves the disabled path executes no plugin/model work and
  measures the added cost of each enabled plugin/route rather than assuming porting savings.
- The telemetry section keeps directly observed counters distinct from `null/unavailable`, keeps
  API money, subscription-window change and machine resources distinct, and does not treat a
  reconstructed price as billing truth.
- Every consolidated dimension names a competing option, a decisive falsifier including an
  explicit no-benefit outcome and a regression outcome, and what it does not prove; a material
  non-dominated tradeoff is escalated rather than silently chosen.
- A provider-free acceptance section specifies how an independent verifier reruns a workload and
  accepts the budgets and rules without a provider call.
- No language, store, broker, configuration syntax or vendor is selected and no route is
  qualified; the program explicitly states what it does not establish (no measured advantage, no
  capacity point, no entitlement, no porting saving).
- Protected paths are untouched; privacy and secret scan are clean.

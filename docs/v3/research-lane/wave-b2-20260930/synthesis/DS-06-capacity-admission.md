# DS-06 — capacity admission and review debt (synthesis)

## Provenance

- Raw: `raw/ds-DS-06-capacity-admission.md`.
- Handoff: `DS-06 — capacity admission and review debt` research directive supplied to the run.
- Session: Wave B Deep Research (self-contained handoff, run 2); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved from the report: **SD** = source-documented; **M** = inferred/modelled from source-documented facts; **Measured** = profiled on a pinned target under a preregistered fixture (the report contains **none**); **U** = unknown/unmeasured. All claims are attributed to "the report's sources"; no new facts or URLs are added.
- Scope: read-only. The report states it did not access a repository, execute Git, inspect private source, call a provider, or mutate any branch/worktree, and that no local profile was measured.
- Source base: the report cites current Git 2.56.0 documentation, Linux 6.18 kernel/cgroup-v2/PSI documentation, Microsoft Win32 Job Object and file/disk APIs, Little's 1961 queueing paper, Google's industrial code-review study, and merge-conflict research.

## The question

How should Recursion v3 bound new branches, linked worktrees and concurrent ARM output using measured capacity while keeping machine pressure distinct from human review debt? The report treats the supplied admission shape `min(machine_headroom, pool_headroom, goal_budget, review_credit, owner_hard_ceiling)`, the stable-low-water expansion rule, high-water refusal, the rule that review capacity cannot be inferred from machine size, the requirement that unobservable counters stay `unavailable`, and the ruling that the historical branch figure of 75 is not a v3 default as fixed inputs to implement, not reopen.

## Key findings

- **No single branch/worktree number is defensible (M).** Branch creation is cheap relative to the work and review obligations attached to it; Git exposes structural state (worktree state, merge reachability, churn, commit divergence, remote-tracking state) but not "safe concurrency" or "review capacity." The report prefers measured `status` latency over counting worktrees, citing Git's own documentation that untracked-file enumeration and index behavior drive cost.
- **Dual-domain min-credit controller (M).** The report recommends `A(t) = min(M, P, G, R, H)` with all terms integer slot credits evaluated independently; no weighted average, so a red review signal can stop admission when machine resources are abundant and vice versa.
- **Machine signals (SD/M).** Primary inputs are measured Git/worktree latency, free disk and filesystem-object capacity, memory headroom, process/handle headroom, and contention/pressure. Linux PSI reports CPU/memory/I/O stall time and supports per-cgroup accounting; cgroup v2 exposes memory usage, PID counts, I/O limits and pressure state. Windows exposes free storage and per-process handle counts, and Job Objects expose/limit process and memory usage when workers are actually assigned to jobs. Route-level metrics are marked `unavailable` — not inferred from host-wide data — when no accounting boundary exists.
- **Review debt is a first-class domain (M).** The first implementation should avoid invented "review points"; the privacy-preserving trace uses timestamps and aggregate counters only: obligations opened, independently closed, current queue count, queue-age distribution, aggregate changed files/insertions/deletions, commits ahead, a binary-change indicator and integration-conflict events. Git can produce aggregate churn without exporting diff text; path-bearing output stays local.
- **Service-rate trace (SD/M).** The report measures completed independent-review obligations per elapsed time, not identities or transcripts. Arrival rate, completion rate, queue size and queue age form the minimum defensible model. Little's Law (`L = λW`) is cited as a diagnostic relationship that should not be blindly assumed over a short, nonstationary window.
- **Gates versus credits (M).** Credits say how many additional slots a resource could support; gates say whether expansion is permissible at all. This prevents averaging severe I/O pressure with abundant RAM.
- **Asymmetric hysteresis (M).** Normal high-water stops new admission and drains naturally rather than killing existing work; expansion requires all required limiting signals to remain in low-water for an owner-configured dwell and should add at most one slot per epoch; emergency machine floors refuse admission immediately. The one-slot rule is framed as a small system-identification experiment.
- **`unavailable` is first-class (M).** Required stale or missing signals block automatic expansion without being falsified into numeric zero; unknown is not positive headroom and not an empty queue.
- **Pruning is stricter than "merged" (SD/M).** Git 2.56.0 can establish branch-tip reachability and provides worktree/upstream safeguards, and `git worktree prune` cleans administrative information for missing working trees, but neither proves that review, publication, reference or recovery obligations have ended. Remote-tracking state is not self-refreshing truth. The report frames staleness as triage, never deletion authority, and requires a proof ladder: worktree safety, content/ref disposition, remote/publication state, unpushed/recovery-only check, dry-run plan and independent verification — stopping at eligibility.
- **Read-only CLI concepts (M).** `branch inventory`, `branch explain`, and `branch prune-safe` are specified as read-only views over canonical facts and provenance, showing each credit, limiting term, water-mark/dwell state and every value's `observed / modeled / unavailable` status, and are forbidden from writing canonical state or deleting anything.
- **Adaptive-vs-fixed experiment (M).** The report pre-registers a baseline (a simple owner-set fixed ceiling), a treatment, two machine profiles, a content-free input trace, defined phases, machine/review/productivity endpoints, a hidden-backlog check, a stopping rule and a decision rule. The decisive falsifier: reject adaptive admission if it produces no preregistered meaningful improvement, or if the apparent improvement is explained by worse end-of-run backlog, queue age or drain time.
- **Profile measurements are absent (U).** The report explicitly did not profile coordinator-small or workstation, so per-slot marginal memory, disk, process, latency, pressure and review-arrival costs remain unverified.
- **Contraction is admission-only (M).** The report says ordinary contraction should reduce future permissible active concurrency, not terminate an ARM, delete a branch or destroy a worktree, because the lane authorizes admission-policy research but not destructive recovery behaviour.

## Recommendation and falsifier

The report recommends, at highest priority, validating the **dual-domain adaptive min-credit controller** with review credit as a service-rate/queue/age-aware domain, `unavailable` handled fail-closed for automatic expansion, and effectful state-changes kept read-only. Each recommendation names a competing option and decisive falsifier:

1. Adaptive min-credit controller vs a **fixed owner hard ceiling**; falsified if controlled testing shows no meaningful safety/review benefit, if apparent benefit is only hidden backlog, or if adaptive slot choice effectively collapses to the fixed cap across machine-rich/machine-poor and review-rich/review-poor regimes.
2. Review credit aware of arrivals, completions and age vs branch-count-only; falsified if service-rate/age signals add no incremental predictive value for review delay/conflict.
3. Fail-closed on `unavailable` vs substituting zero/defaults; falsified only by a formally bounded, independently verified conservative estimator that never understates risk.
4. Profile marginal per-slot cost on both profiles vs static per-profile caps; falsified if marginal-cost telemetry is nonpredictive and static limits are equivalent with less complexity.
5. Pressure as a gate alongside quantity vs totals/utilization only; falsified if pressure adds no predictive signal after controlling for totals.
6. Authoritative branch age only from a lifecycle event, else `unavailable` with Git tip age kept separate; falsified only if Git supplies an authoritative, matching creation primitive.
7. Conflict rate as a review/integration-debt gate, never deletion authority; falsified if conflict history adds no useful control information.
8. Layered proof before automatic pruning; falsified only if an authoritative system proves every protected obligation is fully represented by Git reachability, and still does not authorize any deletion.
9. Read-only views of canonical facts vs views that opportunistically repair/write; falsified only by a demonstrable consistency problem unsolvable transactionally.
10. Exit criterion: delete the adaptive policy and keep the simpler owner-set ceiling if it does not materially outperform after calibrated testing.

## What this does not prove

- No numeric ceiling, water mark, reserve, dwell interval, review-effort weight or concurrency count is selected; all such values remain for owner calibration.
- There are no measured claims; no repository-local resource, branch, worktree or review metric was measured.
- It does not prove Little's Law holds instantaneously in a bursty development queue, nor that every branch carries equal effort.
- It does not prove any Windows equivalent of PSI or any cross-platform attribution boundary.
- It does not authorize any deletion, recovery behaviour, CLI or schema change; pruning output stops at eligibility.
- Route-level and external publication/review state remain `unavailable` where no authoritative adapter exists.

## Open Owner decisions

- What is the hard ceiling H, given that the historical figure must not become a v3 default?
- What machine reserves must always be held for synthesis, verification and recovery?
- Which machine/review signals are mandatory versus advisory for automatic expansion?
- Which queue-age statistic and high/low boundaries represent unacceptable review debt?
- What dwell interval and experiment observation epoch are acceptable?
- Is content-free exact changed-byte aggregation worth adding beyond line/file churn?
- Which external publication/review systems must be authoritative prerequisites for pruning?
- When adaptive admission fails validation, should the fallback be one global owner ceiling or static per-profile ceilings?

## Relevance to later waves

This lane supplies the admission controller, telemetry contract and pruning safety ladder. Later waves should treat the proposed synthetic measurement protocol, the content-free review trace, the fixed-versus-adaptive crossover experiment, watermark calibration and the pruning proof ladder as validation activities to design and run on both target profiles — not as an implemented policy. Any implementation that adopts the shape must keep `unavailable` distinguishable from zero and must expose the limiting credit rather than an opaque score.

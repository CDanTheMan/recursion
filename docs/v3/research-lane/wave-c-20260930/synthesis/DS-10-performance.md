# DS-10 — performance and complexity budget (synthesis)

## Provenance

- Raw report: `raw/ds-DS-10-performance.md`.
- Source prompt: DS-10 — performance and complexity budget.
- Session: Wave C Deep Research (self-contained handoff); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved from the report: source-documented, locally observed, inferred, and unverified; missing measurements are `unavailable`, never zero.
- Scope: report-only. The report states it performed no implementation, benchmark, provider/model call, configuration change, deployment, publication, merge or repository/GitHub operation. The v2 baseline is pinned at commit `98113d6`; Option 2 (small deterministic kernel with typed fail-closed adapters) is treated as owner-ratified and is not reopened.
- The report treats the supplied DS-10 brief as the controlling scope rather than an unspecified general topic and considers evidence through September 30, 2026.
- "The report's sources" below means the public primary/official documents the report cites (Linux procfs/cgroup v2/ftrace, GNU `time`/`pidstat`, Microsoft WPR/reference-set docs, and the modularity/microkernel/microservice benchmarking literature). This synthesis adds no URLs and no new facts.

## The question

Define a rigorous measurement and decision protocol for Recursion v3's whole-system performance and complexity budget, comparing v2 against Options 1/2/3 under one identical end-to-end scenario, with hard floors reported before trade-offs and no invented numeric budgets. For each mechanism the operative question is whether it earns its existence — whether disabling it degrades a named accepted outcome.

## Key findings

- **DS-10 has enough information to define the protocol but not to claim the completion gate fully passed.** The v2 commit is pinned, but the brief supplies no canonical v2 executable, CLI syntax, startup/no-op/idle/replay command, source-tree ownership manifest or benchmark results. The correct state for those fields is `unavailable`, and the exact-command portion of the baseline gate remains open.
- **Measure the whole process tree or accounting group, not the apparent parent process.** Linux cgroup v2 accounts memory across processes in a group, while Windows documentation warns that a process working set is a momentary and incomplete view. An option that moves work into helpers must not appear leaner by shifting memory, CPU, I/O, network or wakeups into child processes or services.
- **Benchmark methodology is a hard requirement, not presentation.** It requires reproducible state, repeated trials, comparable warm/cold conditions, preserved raw environmental information, and reported uncertainty rather than a single-run point estimate. Interactive CLI performance is evaluated as a response-latency distribution, and cold and warm starts are separate experiments that must never be averaged into one "startup" number.
- **The architecture literature supports matched measurement, not architecture folklore.** Classic modularity research argues for decomposition around hidden design decisions; microkernel research shows a small kernel need not be intrinsically inefficient if genuinely minimal (an OS-kernel result with an explicit scope caveat); empirical microservice work shows decomposition changes networking, OS behavior, tail latency, resource management and failure modes, with no architecture-independent scalar winner. This does not prove Option 2 is faster.
- **The comparison produces a coordinate vector, not a score:** authority/safety/privacy, verified quality, recovery/replay, owner/operator cost, quota/tokens/money, context/cache efficiency, latency/throughput, host resources, terminal interaction, portability/configurability, code/maintenance surface, and extensibility/idle cost. Authority, privacy, recovery and disabled-path properties are hard floors; no startup or throughput gain can compensate for a floor failure.
- **No numeric product budget can responsibly be written today.** Each future budget follows the same sequence: measure v2 and a named simpler comparator → characterize variability → declare the acceptable regression/improvement envelope → independently review → freeze the budget with its benchmark fixture and expiry trigger. Every prospective budget names its prerequisite baseline and a decisive falsifier.
- **Each mandatory mechanism needs exactly one semantic owner plus a targeted ablation.** The one-owner map covers schema versions, authority/budget checks, command idempotency, event sequencing, action admission, PAUSE epoch, credential-reference policy, verification identity, publication provenance, plugin discovery/loading, and context/compaction. Adapters, engines and plugins may only perform bounded actions; adopt a mechanism only when its targeted ablation degrades a named accepted safety, quality, recovery, operator or measured-efficiency outcome.
- **Complexity is not one number.** Physical source size, structural/control-flow complexity (McCabe) and trust/ownership surface are separate views; "fewer lines" is not evidence of a leaner core or smaller trusted computing base.
- **PERF-003 disabled-path proof treats timing as secondary to semantic inactivity.** The 0/10/100 installed-but-disabled plugin matrix makes any disabled-path code import/execution, model/network action, worker process or periodic work a hard failure regardless of timing. Proof uses runtime module census, file/syscall/socket trace, process/lifetime events and scheduler `sched_wakeup` tracing on Linux and WPR/ETW on Windows, plus a proposed load-sentinel plugin whose initialization would be observable. This is a proposed test design, not an observation about the current implementation.
- **R17 ablation is stronger than unit testing.** Remove one mechanism while keeping the scenario otherwise matched, then identify the accepted outcome that degrades. Safety-critical ablations occur only in isolated synthetic/test builds with no external side effects; a mandatory mechanism that survives with no lost safety, quality, recovery, operator or measured-efficiency outcome has failed to justify its place and should be simplified, deferred or deleted. The report's ablation results table is entirely `unavailable` because no benchmark ran.
- **Packaging comparison retains three families** — integrated monolith, microservice/process decomposition, and small deterministic kernel plus plugins/adapters. Option 2 is the ratified target but its claimed performance advantage remains unmeasured; the primary risk of the small-kernel direction is that plugin loaders, adapters or alternate state paths quietly recreate a second kernel.
- **Evidence-backed dispositions:** Option 2 adopted as the target with its performance benefit explicitly unverified; mandatory microservice decomposition deferred; eager loading/scanning of disabled plugins simplified or deleted from the critical path; single-number complexity gating deleted.
- **The most important unresolved Owner input is the exact benchmark manifest**, not another architecture debate: the canonical v2 startup command, canonical idle/coordinator invocation, canonical CLI scenarios, canonical replay/recovery command, and the profile definitions against which the first measurements will be frozen.
- **Per-mechanism disposition rule:** adopt only with one semantic owner and a failing ablation; simplify when an outcome is real but the surface is larger or duplicated; defer when the benefit is plausible but no accepted scenario demonstrates it; delete when no accepted scenario degrades under removal and no safety requirement uniquely belongs to the mechanism. Every decision must also state what it does not prove.
- **Efficiency must include downstream cost.** A candidate that lowers startup but creates more regressions, independent-review work, recovery interventions or privileged-code touchpoints has not demonstrated net efficiency. Verified quality, owner/reviewer burden, change locality, maintenance surface and recovery/operator burden are tracked separately and must not be collapsed into a weighted score that could conceal a security or recovery failure.
- **The minimum experiment set likely to change an Owner decision** is: a hard-floor authority/recovery suite; the PERF-003 0/10/100 matrix; one matched real end-to-end workflow across v2 and Options 1–3; a crash/restart/replay fault-injection matrix; and one matched maintenance change crossing a provider/engine boundary.
- **What is already decisive without further spending** is narrow but important: no scalar may hide a hard-floor failure; no numeric product budget is valid before a baseline; installed-disabled plugins may not execute/import/network/spawn/periodically work; implementer PASS is not acceptance; and a mandatory mechanism needs one semantic owner plus an ablation-demonstrated outcome.
- **Completion-gate line statuses:** the exact-command baseline line is not complete, while the improvement-comparison, one-owner/ablation, budget-policy and disabled-path lines pass as research design or policy, with empirical ablation results and the private secret scan remaining `unavailable`.
- **Dispositions name a competing simpler mechanism:** adopt, simplify, defer and delete each state the evidence that would overturn the disposition, so no mechanism can be retained merely because its removal has not yet been tested.
- **The two hardware profiles stay abstract and versioned:** each profile record captures effective CPU allocation/affinity or quota, memory limit, storage behavior relevant to the scenario, OS version and background-load state, and the profile contract is held fixed across v2 and Options 1/2/3.
- **Source-pinned claims carry expiry:** the report's claim table marks the v2 pin and PERF-003 as source-documented/high confidence, treats the literature analogies as context-dependent, and marks Option 2's performance benefit as inferred/medium until matched measurements exist.

## Recommendation and falsifier

The report recommends keeping ratified Option 2 as the implementation target while treating every claimed performance or complexity advantage over v2/Option 1 as unverified until measured; adopting mechanisms whose removal demonstrably breaks an accepted safety/recovery invariant; simplifying their implementation surface aggressively; deferring machinery whose benefit can only be asserted; and deleting duplicate routing/state/context/plugin paths if an ablation shows no accepted outcome depends on them.

- The competing option is **Option 1, incremental extraction from the existing runtime**.
- **Decisive falsifier:** a matched pattern in which Option 2 fails to buy a unique accepted safety/recovery/quality benefit while simultaneously imposing persistent startup, idle resource, replay, code/review or operator cost beyond the budget derived from the v2/Option 1 baseline. That evidence should trigger Owner escalation, because the research lane is not authorized to reverse the ratified architecture.
- This recommendation does not prove a particular language, persistence mechanism, IPC choice, framework, storage layout or plugin technology.
- Sub-dispositions carry their own falsifiers: microservice decomposition is falsified if a matched experiment shows a necessary isolation/recovery/scalability/quality benefit unachievable with the simpler kernel/adapter arrangement without violating another floor; eager disabled-plugin activity is falsified if an alternative discovery implementation maintains zero disabled import/execution/network/worker/periodic work while meeting the eventual measured startup/file-I/O budget.

## What this does not prove

- No numeric ceiling, budget, threshold, water mark or concurrency count is selected; all await a baseline and Owner calibration.
- No measured claims exist: no Recursion benchmark was authorized or executed, so Option 2 is not shown to be faster and no language, storage engine, IPC format, framework or plugin framework is selected.
- It does not prove that duplicate paths currently exist or that disabled plugins currently run — those are criteria for a later source audit, and no repository was inspected.
- A startup improvement does not prove lower idle cost; lower RSS does not prove lower total memory impact; lower LOC does not prove lower control-flow or trust complexity; passing replay tests does not prove authority correctness; and zero provider calls in one scenario does not prove all disabled routes are inert.
- The private-repository secret scan remains `unavailable`, not "clean," because it was outside the supplied authorization.
- The report supplies no quantitative product chart, because no benchmark was authorized and the brief forbids inventing numeric budgets; producing one now would convert unknown measurements into fabricated evidence.

## Open Owner decisions

- The exact benchmark manifest: canonical v2 startup, idle/coordinator, CLI and replay/recovery commands and the profile definitions.
- Which accepted end-to-end scenario is the minimum representative workload for R17.
- What precise independent-review evidence is required for "verified quality."
- Which statistical uncertainty/reporting policy becomes canonical for performance budgets.
- Which outputs require publication provenance when publication itself is not active.
- Which source ownership labels define "privileged" code for the first v2 audit.

## Relevance to later waves

- Supplies the instrumentation layer (procfs/smaps, cgroup v2 and PSI, `pidstat`, tracefs `sched_wakeup`, GNU `time`; Windows WPR/ETW and reference sets), the versioned baseline artifact schema, the mechanism/ablation ownership map, the PERF-003 semantic-inactivity checks and the staged experiment sequence.
- Later waves should treat these as validation designs to run on both target profiles, not as implemented policy; the hard-floor-first ordering and typed `unavailable` must persist, and no scalar may hide a floor failure.

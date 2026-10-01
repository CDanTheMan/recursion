# Domain C — operations, capacity and evaluation (synthesis)

Status: research synthesis. Not a decision, not independently verified, not rerun. It aggregates six
per-lane syntheses from Wave B2 (DS-06, DS-09, DS-25, DS-26) and Wave C (DS-10, DS-11) without adding facts, URLs or selections. Every value a lane left unmeasured stays `unknown` or `unavailable`, never zero.

## Scope and lanes

Domain C covers the operating envelope of Recursion v3: how much concurrent work is admitted, how that work is measured and accounted for, how routes and delegation are evaluated, how terminal views relate to running processes, and how update, rollback and recovery make their claims falsifiable. The cluster answers "how do we know the system is behaving, and by what evidence do we let it do more" — not "which framework do we pick."

- **DS-06 — capacity admission and review debt.** Bounding branches, worktrees and concurrent ARM output by measured capacity, separating machine pressure from human review debt.
- **DS-09 — terminal and communication views.** Contracts for a daemon, process broker, detachable views and external actors before the terminal runtime is unblocked.
- **DS-10 — performance and complexity budget.** A measurement and ablation protocol comparing v2 against Options 1/2/3, with hard floors reported before trade-offs.
- **DS-11 — routing and delegation science.** Whether task-specific routing, orchestrator delegation, continuity and planning strength beat simpler alternatives, and how to measure it.
- **DS-25 — update, release, rollback and DR.** What contract keeps executable rollback, state recovery, history readability, newest-work preservation and task resumability distinct.
- **DS-26 — telemetry, accounting and honest status.** The evidence contract required before counters drive dashboards, budgets, route learning or optimization claims.

All six are report-only: none accessed a repository, executed Git, called a provider, ran a benchmark, performed a restore or deployed anything. Each lane treats its supplied directive (the admission shape, the authority model, the privacy boundary, the ratified Option 2 target) as a fixed input, so this synthesis reports what the research would require, not a ratified plan.

## Lane digests

### DS-06 — capacity admission and review debt

**Bottom line (inferred/modelled).** Adopt a dual-domain adaptive min-credit controller `A(t) = min(M, P, G, R, H)` evaluating machine headroom, pool headroom, goal budget, review credit and an Owner hard ceiling as independent integer slot credits — no weighted average, so a red review signal can stop admission while machine resources are abundant, and vice versa. Review credit is a service-rate/queue/age domain (obligations opened, independently closed, queue size and age, aggregate churn), not a branch-count proxy. Stale or missing signals are `unavailable` and fail closed for automatic expansion; contraction is admission-only and never terminates, deletes or destroys; pruning stops at eligibility after a layered proof ladder.

**Confidence / evidence class.** Mostly inferred/modelled from source-documented Git 2.56.0, Linux 6.18 cgroup v2/PSI and Windows Job Object/file APIs; the lane reports no measured claims.

**Does not prove.** No ceiling, water mark, reserve, dwell, review-effort weight or concurrency count is selected, and no repository-local resource, branch, worktree or review metric was measured.

### DS-09 — terminal and communication views

**Bottom line (inferred design over source-documented contracts).** Freeze semantic invariants before implementation: canonical event append isolated from presentation; daemon/broker ownership; OS-scoped containment (non-breakaway Job Object on Windows; non-threaded cgroup v2 scope with `cgroup.kill` on Linux); stable actor and lease identities; `SNAPSHOT`/`EVENT` replay with an explicit replay floor; bounded per-view credit; fail-closed capability negotiation; one active input/resize lease; plain-text accessibility as the degraded baseline. A view is a detachable projection; the PTY is transport, not the containment boundary.

**Confidence / evidence class.** Source-documented platform/standards contracts (Win32, Linux kernel, POSIX, RFC 4254, Unicode, W3C) with inferred protocol and ownership contracts; cross-platform containment is explicitly `unverified` pending adversarial tests.

**Does not prove.** No renderer, TUI library, multiplexer, IPC serialization or product default is selected, there are no locally observed runtime claims, and whole-descendant-tree termination on all target environments is unverified.

### DS-10 — performance and complexity budget

**Bottom line (design protocol; dispositions inferred).** Keep ratified Option 2 as the target while treating every claimed performance/complexity advantage over v2 and Option 1 as unverified until measured. Adopt a mechanism only when it has one semantic owner and a targeted ablation degrading a named accepted safety, quality, recovery, operator or measured-efficiency outcome; simplify aggressively; defer unproven machinery; delete duplicate routing/state/context/plugin paths. Hard floors (authority, privacy, recovery, disabled-path) precede any scalar and cannot be compensated by startup or throughput.

**Confidence / evidence class.** The v2 pin (`98113d6`) and PERF-003 are source-documented and high-confidence; the architecture literature is context-dependent analogy; Option 2's benefit is inferred/medium; ablation results are entirely `unavailable`.

**Does not prove.** No numeric budget, ceiling or concurrency count is chosen; no Recursion benchmark ran; no language, storage engine, IPC format, framework or plugin framework is selected.

### DS-11 — routing and delegation science

**Bottom line (provisional hypothesis, not an Owner decision).** Enter local measurement with task-specific route suites rather than a universal ladder; one strong ARM delegating only when decomposition value exceeds coordination cost; same-route continuity unless a checkpointed reason to switch exists; stronger planning only where it buys enough acceptance/repair reduction; and the existing risk-scaled verifier floor, with deterministic rule-based admission and event-triggered revalidation plus a small periodic canary. Primary endpoint: first-review acceptance at a pre-registered quality floor per unique task; false-green rate is first-class.

**Confidence / evidence class.** Source-documented public literature (an ICLR 2025 study of roughly 46,000 instances across 12 benchmarks; RouteLLM, Hybrid LLM, FrugalGPT, BEST-Route) with design inference. No local measurement; missing telemetry stays `unknown`.

**Does not prove.** No public source substitutes for local measurement; no named model is shown "best"; route eligibility/privacy/billing cannot be inferred; different-provider verification is not shown unbiased; no regulatory compliance is established.

### DS-25 — update, release, rollback and DR

**Bottom line (inferred starting disposition).** Prefer verified compatible executable rollback while retaining the newest canonical state/history, then verified task resume or an explicit hold, with `repair-forward` and noncanonical separate-instance restoration as competing options. Five propositions — working executable, readable history, preserved newest work, resumable tasks, reversed external effects — must never share one "recovered" bit. Release identity is multidimensional (SemVer covers declared public-API compatibility only); configuration publication is compare-and-set with separate `ConfigAcceptedReceipt`/`ConfigAppliedReceipt`; migration uses expand/contract with one canonical writer; backup requires a `SnapshotReceipt` binding state high-water, checkpoint digest, schema epoch and immutable artifact set.

**Confidence / evidence class.** Source-documented standards/security guidance (TUF-style properties, SLSA v1.2, SPDX 3.0.1, RFC 9110 `If-Match`, CISA backup posture) plus inferred specification. The six-mode by four-outcome matrix is deliberately `unknown` in every cell.

**Does not prove.** No implementation, migration, rollback or restore trial ran; no storage engine, packaging format, signing stack, update channel or SBOM tool is selected, so engine-specific snapshot and fencing behavior is unverified; no numeric RPO/RTO exists.

### DS-26 — telemetry, accounting and honest status

**Bottom line (inferred from source-documented rules).** Adopt provenance-qualified adapters feeding two ledgers — attribution/quantity and financial/capacity — reconciled after normalization, with no silent conversion between them. Authority is dimension-specific: invoices settle money, provider-native usage gives quantities, version-qualified harness events give task attribution, OS monitors give host resources, estimators stay modelled, subscription capacity stays in its native unit. Cache semantics are per-source and not summable; rate-limit charge is not billing. Every value carries `observed`/`modeled`/`inferred`/`unavailable`; a missing counter is `null` with a reason, never `0`. Honest status is an evidence viewer, not a progress story.

**Confidence / evidence class.** Source-documented provider/endpoint documentation; upstream-observed issue reports for Codex/Claude Code local streams (not a stable contract); design inference for the ledger split. No account, credential, billing endpoint or live adapter was exercised.

**Does not prove.** Findings are documentation-qualified, not runtime-qualified; documented query horizons are not proven retention; several retention cells, portable wakeup count, host monetary cost and subscription-to-dollar conversion remain `unknown`/`unavailable`.

## Cross-lane consistency and contradictions

**The shared thread.** Every lane converges on the same precondition before any policy may run: measure it, keep honest counters, preregister the experiment. DS-06 needs measured Git/worktree latency and a content-free review trace before adaptive admission; DS-09 preregisters the 0/1/5/10/20-view matrix with machine-readable negative traces; DS-10 refuses any numeric budget before a pinned baseline and reports hard floors before trade-offs; DS-11 freezes corpus hash, hypothesis, floors, margins and promotion rule before unblinding; DS-25 makes receipts non-skippable and leaves every recovery cell `unknown`; DS-26 makes `unavailable` first-class and forbids false equivalence between counters. All six reject the implementer's own PASS as acceptance.

**Consistent refusals.** No lane invents a measured value. Missing data is consistently `unknown`, `unavailable` or `null`, not zero or a default. The historical branch figure is explicitly barred as a v3 default (DS-06); DS-25 invents no RPO/RTO; DS-10 invents no budget; DS-11 invents no campaign size (its table is a sensitivity calculation); DS-09 treats numeric gates as provisional engineering thresholds, not SLAs.

**Tensions, not contradictions.**

- *Mechanisms depend on the numbers all lanes defer.* DS-06's water marks, DS-09's SLA, DS-10's budgets and DS-11's margins are all Owner inputs; until they exist the controllers and gates are shapes without calibration.
- *No scalar cost, but scalars are proposed.* DS-10 rejects single-number complexity gating and DS-26 forbids a scalar total; DS-06's min-credit `A(t)` is a scalar. DS-06 resolves this only by keeping each credit term independently inspectable.
- *Determinism vs model assistance.* DS-11 lets a model contribute a prediction if admission and reason codes stay deterministic; DS-10 requires one semantic owner. These reconcile only if the predictor never becomes the admission authority.
- *Contraction authority.* DS-06 allows admission-only contraction; DS-25 owns rollback/restore and demands receipts. The handoff between admission pressure and recovery action is unowned.
- *Selection avoidance is absolute.* DS-09, DS-10, DS-25 and DS-26 each select no renderer, language/store/framework, storage engine or provider, so the domain answers "how would we know," never "which."
- *Evaluation relies on a review process the cluster never measures.* DS-11's primary endpoint is first-review acceptance, but the reviewer behavior and independent-verification process that gate it are not measured anywhere in these lanes; DS-06 models review debt only as aggregate counters.
- *Recovery correctness is bounded by effects no lane can reverse.* DS-25 separates local software movement from external-effect reality, DS-09 provides no remote cancellation, and DS-26 leaves host cost unmonetized; together these bound what "recovered" can mean.
- *Freshness versus durability is unreconciled.* DS-26 wants metadata-minimal, local-first telemetry with retention `unknown`, while DS-25 wants durable receipts and audit-readable history; the two have not been merged into one retention policy.

## Cross-lane dependencies

- **Telemetry is upstream of everything evaluative.** DS-06 counters, DS-10 measurements, DS-11 endpoints and DS-25 receipts all consume the DS-26 typed, two-ledger contract; without it, each would read `unknown` as zero.
- **DS-06 depends on DS-10 baselines.** The min-credit controller needs the profile definitions and per-slot marginal-cost measurement DS-10 supplies as a protocol.
- **DS-06 review debt and DS-11 evaluation share endpoints.** Owner-review minutes, repair cycles and false-green rate serve both the review domain and the evaluation primary/secondary measures.
- **DS-09 reuses DS-10 instrumentation.** PERF-010 and containment tests reuse DS-10's profile records, trace tooling and uncertainty policy.
- **DS-25 depends on DS-10 and DS-26.** Activation/landing receipts and restore verification need counters and a pinned baseline; the open storage-engine decision blocks DS-10 replay verification.
- **DS-06 pruning depends on DS-25 authority.** The proof ladder stops at eligibility because review, publication and recovery obligations are DS-25's to discharge.
- **DS-11 route learning is subordinate to DS-26 and the fixed authority model.** Only runtime-qualified measurements may update production learning state.
- **Language, store and performance selection is a shared prerequisite.** DS-10's protocol presumes a selected implementation, DS-25's snapshot mechanism and DS-10's replay verification presume a storage engine, and DS-26's adapters presume a harness; none of these selections exists, so the dependency graph terminates in unselected components.
- **DS-09 containment and DS-25 fault injection overlap.** DS-25's process-death and torn-write dispositions exercise the same OS boundaries DS-09 must prove, so terminal containment results are partly a precondition for believable recovery trials.
- **Neither an evaluation corpus nor a benchmark workload is fixed.** The DS-10 benchmark manifest and the DS-11 corpus/difficulty mix are both open, so no evaluative campaign can be preregistered end-to-end.

## Consolidated open Owner decisions

Aggregated, unresolved, and deliberately not decided here.

**Capacity (DS-06):** hard ceiling H; machine reserves for synthesis, verification and recovery; mandatory vs advisory expansion signals; queue-age statistic and high/low boundaries; dwell interval and observation epoch; whether content-free exact changed-byte aggregation is worth adding; which external publication/review systems must be authoritative prerequisites for pruning; fallback (one global ceiling vs static per-profile ceilings).

**Terminal (DS-09):** minimum Windows build and Linux kernel/distribution and whether systemd is mandatory; what counts as an "external effect" outside the process tree; audit-durable history vs current projection; default geometry and lease-handoff rule; read authorization for shared rooms; the approved numeric PERF-010 SLA; supported accessibility technologies; snapshot cadence and replay floor; whether client capability survives a daemon restart; multiplexer role and wire encoding.

**Performance (DS-10):** the exact benchmark manifest (v2 startup, idle/coordinator, CLI, replay/recovery commands, profile definitions); the minimum representative end-to-end scenario; what counts as "verified quality"; canonical uncertainty/reporting policy; which outputs need publication provenance; which source-ownership labels define privileged code.

**Routing/delegation (DS-11):** minimum practically important acceptance difference and non-inferiority margin; value of one owner-review minute versus quota/latency; maximum experiment resource envelope; whether the peer-swarm control is worth its cost; acceptable corpus difficulty mix; deployment regions/use cases for legal classification; evidence threshold to promote a measured result into policy.

**Update/release/DR (DS-25):** storage engine; packaging format; signing/trust stack; update channel; SBOM tool; default configuration-propagation policy (`outstanding_sessions` vs `new_or_isolated_only`); Stop-mode semantics and scopes; release-promotion authorization/quorum; support windows; emergency update deadlines; retained-slot count/retention; numeric RPO/RTO after measurement.

**Telemetry/accounting (DS-26):** harness admission list and supported versions; whether organization-admin credentials are acceptable for read-only collectors; local retention; export cohort-suppression/differencing policy; whether provider session IDs may be stored raw locally; host-resource and human-review valuation; route-learning promotion metric, margin and uncertainty method; precedence for late billing corrections; whether document-qualified adapters may feed operator views before runtime qualification.

## Domain gaps and open unknowns

- **Nothing was executed anywhere in this cluster** — no implementation, benchmark, provider call, restore, rollback, fault injection or terminal run in any of the six lanes.
- **Unrun experiments.** DS-06: fixed-vs-adaptive crossover, per-slot marginal-cost profiling on both profiles, Little's Law validity over a bursty window. DS-09: PERF-010 view matrix, adversarial containment tests, separate compatibility/accessibility suites. DS-10: v2-vs-Options benchmark, PERF-003 0/10/100 disabled-plugin matrix, R17 ablation, crash/restart/replay fault injection, a matched maintenance change across a boundary. DS-11: five confirmatory campaigns, a pilot of 30 unique tasks per class with three repeats, an ARM-count sweep at 0/1/2/4/8. DS-25: the full six-mode by four-outcome matrix, fault-injection dispositions, a restore trial. DS-26: no adapter exercised, no conformance or shadow evaluation.
- **Unset numeric budgets.** Concurrency ceiling, reserves, water marks, dwell; terminal SLA; every performance/complexity budget; acceptance and non-inferiority margins; experiment resource envelope; support windows, emergency deadlines, retained slots; RPO/RTO; reconciliation tolerance and confidence threshold; host-resource and human-review valuation.
- **`unknown` or `unavailable` metrics.** Route-level capacity metrics; portable wakeup count; host monetary cost; subscription-to-dollar conversion; provider retention horizons; a Windows PSI equivalent; pure inference latency when only client RTT exists; full-descendant-tree termination; Option 2's performance benefit; DS-11's run variance, continuity direction and verifier-independence benefit.
- **Recovery and migration remain unproven even in design.** DS-25 classifies the Mode 2 vs Mode 6 distinction, expected-revision rejection and receipt model as proposals, not runtime-verified properties, so the operational recovery contract has no demonstrated cell.
- **Retention is not established by documented horizons.** DS-26 is explicit that provider query horizons and bucket limits do not prove guaranteed retention, so any budget or audit horizon built on them would rest on an inference.
- **Provider-effect cancellation is unowned.** DS-09 states Job Objects and cgroups govern local processes only; external/provider-side effects need their own cancellation and idempotency contracts, which DS-25's forward-only external-effect boundary also leaves open.
- **Provider counter coverage is unknown.** Which usage metadata is actually exposed for the accounts and routes Recursion may eligiblely use is not established, so parts of the DS-26 schema and DS-11 route learning rest on an unverified assumption.
- **No Windows equivalent of PSI is demonstrated.** DS-06 and DS-10 both need contention/pressure accounting; Linux has PSI and cgroup v2 pressure state, but the Windows mapping remains `unknown`.
- **Language, store and performance benchmarks are all unrun.** No v2-vs-Options measurement, no storage-engine comparison and no terminal or trace benchmark exists; DS-10 names the benchmark manifest as the most important unresolved Owner input.
- **Selection gaps block measurement.** No language, persistence mechanism, IPC choice, framework, storage layout, packaging format or plugin technology is selected; with no storage engine, DS-25's snapshot-with-active-writer mechanism and DS-10's replay verification remain unprovable.

## Evidence-quality notes

- **Provenance is uniform and weak by design.** All six are syntheses of self-contained handoffs; none was independently verified or rerun, and no new facts or URLs were added.
- **Evidence classes stay distinct.** Source-documented claims (platform contracts, provider documentation, standards) are strongest; inferred/design proposals (admission controller, terminal protocol, ledger split, rollback disposition) are marked; "locally observed" in DS-25 refers only to the supplied brief; DS-26's upstream-observed issue reports are version-specific, not contracts; several guarantees are explicitly `unverified`.
- **No measured numbers.** Every quantitative figure is either a source-documented external finding (DS-11's public benchmark study, DS-10's v2 pin), a sensitivity/feasibility calculation (DS-11's sample-size table), a provisional engineering threshold (DS-09), or a historical figure explicitly barred as a default (DS-06). None is a Recursion measurement.
- **Missing never becomes zero.** Every lane restates that absent counters are `unknown`, `unavailable` or `null` with a reason; DS-26 makes this a falsifier, and DS-10 forbids a scalar from hiding a hard-floor failure.
- **Expiry and drift.** DS-11 notes route rankings have finite shelf life under version drift; DS-26 requires version-pinned conformance; DS-10 requires baselines to carry expiry triggers. These conclusions should be revalidated, not treated as durable.
- **Acceptance rule carried through.** Implementer PASS is not acceptance; an independent verifier rerunning the exact candidate (preferably a different model family) is required before any of these designs becomes policy.
- **No independent verification exists for any lane.** Each synthesis was produced once from a self-contained handoff with no rerun and no cross-family verifier, so every recommendation in this domain is provisional by that same rule.
- **Briefs are controlling, not neutral.** DS-25 and DS-26 treat their supplied directives as controlling requirements and DS-10 treats Option 2 as ratified; this synthesis inherits those constraints and does not reopen them.
- **Upstream-observed is weaker than source-documented.** DS-26's Codex/Claude Code stream defects are issue history that later versions may fix, so none should be generalised into a permanent contract.
- **Sensitivity calculations are not measurements.** DS-11's sample-size table (illustrative acceptance rates, α and power) is explicitly a sensitivity calculation, not a predetermined campaign size, and is labelled as such here.

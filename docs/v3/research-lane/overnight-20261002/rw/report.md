# R-W — Harness evaluation and benchmark science

Evidence date: 2026-10-02. Repository basis: commit `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. Status: research design candidate; independent review pending. **No target evaluation, benchmark, model, provider, simulation, mutation campaign or local conformance test was executed for this report. All proposed runtime outcomes are UNEXECUTED / unknown.**

## Decision summary

Recursion needs three distinguishable verdicts: **conforms to the fixed contract**, **improves an explicitly named workload outcome**, and **reproduces independently**. A receipt parser passing, a mutant dying for an incidental reason, or a modeled activity counter reading zero supplies none of these verdicts automatically. Productive continuity should be judged by useful work completed after disruption with preserved authority, evidence and honest accounting, against a competent direct-harness/manual-transfer baseline and a minimal conforming orchestrator.

The design below makes first-review acceptance and independently established false greens primary, with workload-native allowance, full resource cost, latency and human effort alongside them. It retains task failures, abandoned runs, quota exhaustion, incomplete adjudication and delayed defects. Quality floors cannot be purchased with lower cost. Numeric margins, corpus allocation, sample size, power, qualification, and advantage are **unknown** pending accepted inputs and authorized local work.

The brief contains contradictory execution language: its authority, purpose and non-goals prohibit evaluations, while one later non-goal calls the provider-free layer “executed here.” The current explicit boundary prohibits target tests. This report resolves that conflict by defining the layer and delivering precise **unexecuted** handoffs, without claiming any PASS.

### Evidence and authority convention

- **Source-documented:** a primary public source or pinned repository specification states a fact; this is not implementation acceptance
- **Locally observed, static:** source bytes or committed receipts were read here; this is not an independent rerun of their underlying experiments
- **Inferred proposal:** every contract, analysis rule and recommendation below unless explicitly identified otherwise
- **Unknown:** unavailable target measurement, unresolved assumption, unqualified route, missing oracle or missing authorization; never numeric zero

D018–D033 remain fixed. Native loop ownership and independently useful upstream-only workflows both remain requirements. No hidden native/helper inference may be added to make an upstream-only arm work. D019 is comprehensive construction with lean opt-in installation; ablations compare conforming mechanisms or activated profiles, not whether accepted capabilities should exist. The current terminal-first/GUI-later instruction governs construction sequencing; D019's opt-in GUI release wording and older exclusion text need a release-timing interpretation, not an evaluator silently choosing a smaller release. D020's core fence plus optional takeover remains intact. D022 terms are Aggressive / Full / Lazy, checkpoint, interrupt and drain; process death never proves external rollback.

All eligible comparisons obey authority, privacy, credential, effect, quality, resource and recovery floors. A control violating a floor is an isolated **negative control**, never the rival that establishes benefit. Historical v2 or an unmediated shell can inform engineering history but is not an admissible product competitor until it meets the same task-relevant floors. No language, store, framework, runtime, statistical package, benchmark suite or vendor is selected.

## Source findings that change the design

These compact factual notes are the report's public-source summaries. Subsequent numbered sections are Recursion-specific proposals, not claims that these papers validate Recursion. Metadata and retrieval limitations appear in `source-register.json`; no raw source bodies are bundled.

1. **Minimal baseline counterpoint.** The [canonical paper note](../model-architecture/report.md#minimal-harness-paper-facts) retains the matched comparison, fixed-task inference and modeled-cost details. **I:** demand a strong simple comparator, without treating it as evidence about Recursion continuity, credentials, review labor or all task populations. Nonsignificance does not establish equivalence and cannot reopen D019.
<a id="w-capsule-2"></a>
2. **Coding-suite validity.** SWE-bench uses repository issues and executable verification; its evaluation guide separately describes runner completion and issue resolution. The Verified dataset card is a defined dataset release, not proof of exhaustive behavioral correctness. Agentless documents simple repair stages and problem-description/answer-leakage defects in public tasks. These are grounds for independently validating task and oracle quality before ranking harnesses. [W-S02](https://arxiv.org/abs/2310.06770v3), [W-S03](https://www.swebench.com/SWE-bench/guides/evaluation/), [W-S04](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified), [W-S05](https://arxiv.org/abs/2407.01489v2)
<a id="w-capsule-3"></a>
3. **Agent reliability and overfitting.** τ-bench evaluates goal-state outcomes and repeated-trial reliability; a successful retry is not the same endpoint as consistent first-attempt success. AI Agents That Matter criticizes accuracy-only comparison, weak holdouts and reproducibility gaps. LiveCodeBench's time-aware fresh-task approach is contamination-related prior art, not a guarantee that any Recursion model has never seen a task. [W-S06](https://arxiv.org/abs/2406.12045), [W-S07](https://arxiv.org/abs/2407.01502), [W-S08](https://arxiv.org/abs/2403.07974v2)
<a id="w-capsule-4"></a>
4. **Statistical discipline.** COS distinguishes confirmatory registration from exploratory work; Registered Reports review questions and methods before results. Lakens separates evidence of equivalence from failure to detect a difference and requires meaningful bounds. Sample-size justification must match the inferential objective. Use the [canonical confidence-sequence premise](../rs/report.md#s-s09-facts). These support the safeguards below, but select no package or numerical threshold. [W-S09](https://www.cos.io/initiatives/prereg), [W-S10](https://www.cos.io/initiatives/registered-reports), [W-S11](https://pure.tue.nl/ws/portalfiles/portal/80918653/lakeequi2017.pdf), [W-S12](https://doi.org/10.1525/collabra.33267), [W-S13](https://arxiv.org/abs/1810.08240)
<a id="w-capsule-5"></a>
5. **False-green and variance hazards.** Luo et al.'s original flaky-test study describes nondeterministic outcomes and the costs of rerun/ignore workarounds. Just et al. find mutation-detection association with real-fault detection in studied programs, with limitations; that is not universal fault coverage. Agarwal et al. show why few-run point estimates on RL benchmarks can mislead; Pineau et al. discuss reproducibility practices. These motivate separate oracle, task and stochastic-run uncertainty. [W-S14](https://mir.cs.uiuc.edu/~marinov/publications/LuoETAL14FlakyTestsAnalysis.pdf), [W-S15](https://homes.cs.washington.edu/~mernst/pubs/mutation-effectiveness-fse2014-abstract.html), [W-S16](https://proceedings.neurips.cc/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html), [W-S17](https://jmlr.org/papers/v22/20-303.html)
<a id="w-capsule-6"></a>
6. **Upstream practice, not qualification.** Anthropic's evaluation guidance separates transcript from environment outcome and code/model/human graders. Its infrastructure study reports resource-allocation effects and cautions about configuration comparability. mini-SWE-agent documents configurable benchmark runs, trajectories and resumable output handling; OpenHands documents benchmark infrastructure with a pinned SDK dependency. These are inspectable practices, not evidence any upstream route satisfies Recursion's floors. Their benchmark scores are not imported. [W-S18](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), [W-S19](https://www.anthropic.com/engineering/infrastructure-noise), [W-S20](https://mini-swe-agent.com/latest/usage/swebench/), [W-S21](https://github.com/OpenHands/benchmarks/blob/main/README.md)

For route-counter and provider facts use the [shared canonical evidence](../shared-evidence/source-facts.md), [R-F route/accounting findings](../rf/report.md), and the committed R-D endpoint dictionary. For backend instrumentation, profile manifests and budget calibration use [R-O](../ro/report.md). For MCP era-specific behavior use [protocol-edges](../protocol-edges/report.md). These companion reports are research, not qualified implementations; their review status must accompany reuse.

## Static repository findings

This section records static observations and their boundaries, with detailed source identities in `repository-source-manifest.json`.

- **No new end-to-end benchmark:** DS10 leaves its manifest and advantage unmeasured; DS11's route/corpus comparisons and independent-review benefit are unrun; DS12's context suite remains unrun; DS25 does not establish recovery outcomes; DS26's counters are not runtime qualified. G20/G22/G27 remain experimental gaps. Older proposals cannot restore retired executive authority or reopen D028 scope.
- **FU03:** current `RIntegrated.tla` has four fresh command IDs, six nominal events and capacity two, despite a stale header. Its baseline consumes a fresh ID per accepted transition, so the nominal event cap is not the exposed depth. Recorded five kills among seven instantiated diagnostics do not classify the full 36-row registry. M03's recorded TypeOK detection is useful but does not establish the named semantic monitor. M02/M03/M25 diagnostic edits differ from registered mutation meanings; surviving M25/M31 are not demonstrated equivalents. No fairness/liveness claim follows.
- **Candidate enlarged-bound witness:** GrantLease → Start → PrepareEffect → MarkDispatch → SubmitFail → ArmTimer → FireTimer could reach retryReady with an InFlight effect and violate the present NoBlindEffectReplay predicate after seven fresh IDs/events. This is an inferred source-level candidate outside the executed bound, not a reproduced counterexample or a full-spec defect. Resolve timer/effect semantics and exposure before increasing bounds; never weaken the oracle to improve a kill count. [Detailed static audit and candidate](../gaps/report.md#3-fu-03-what-the-committed-evidence-does-establish)
- **FU04:** retained rows are thirteen runs, twelve recorded pass and one unknown, spanning ten PF IDs; ten catalog cases remain not run and no full platform profile is qualified. Receipt checks accept observation/recovery booleans without proving the named fault or mechanism. Anonymous-pipe output is not ConPTY; size after a kill is not byte-exact durable replay; an out-of-lock-range write is not overlapping bypass; a directory/file sequence is not receiver-side epoch fencing. The WSL trace-end parser makes fault-trigger flags false despite possible physical activation. Preserve the observations, correct their claim scope, and independently witness fault activation. [Mechanism-level audit](../gaps/report.md#4-fu-04-raw-counts-actual-mechanisms-and-oracle-limits)
- **M1B:** `scripts/tests/v3/execution/reference_oracle.py`, `evaluate_disabled`, constructs its prohibited-activity counters as constant zeros. This specifies expected inactivity; it is not a runtime monitor of imports, processes, network, credentials or spend. Unknown runtime behavior cannot be converted to observed zero by copying that receipt.

The actionable finding is an **evidence-ladder gap**, not “all earlier work failed.” Record separately: source identity, registered semantic mutation, exposure/reachability, independent oracle, exact profile execution, repeatability, and full task outcome. Existing artifacts contribute only their supported rungs.

<a id="rw-q01"></a>
## Q01 — Task families, sampling and representativeness

The unit of substantive sampling is a **unique assigned task/goal episode**, clustered by source repository or family when tasks share code or solutions. An attempt, seed, retry, subagent, perturbation or repeated compaction is nested within that task. Ten repeats of one issue are not ten independent demonstrations of generalization.

Use the DS11 families (planning, architecture, security, backend, frontend, mechanical change, debugging, integration, documentation and research) as a proposed frame, not an instantiated corpus. Cross them with D024 continuity conditions, source state (clean/dirty, detached/forked, merge/conflict, stale/missing evidence), coupling (local change versus cross-component), oracle type, authority risk, context pressure and task duration. Difficulty is assigned before candidate results by independent rubric: dependency breadth, information needed, acceptance complexity and historical human effort where legitimately available. Avoid deriving difficulty from whether Recursion succeeded.

Maintain two manifests: a small stable regression core covering each mandatory invariant and a sampled empirical task panel for benefits. Stratify the latter by the declared intended population, sample reproducibly from an enumerated eligible frame, retain inclusion probabilities, record exclusions before treatment, and report both stratum results and prespecified population weights. Convenience samples support only claims about themselves. A maintenance quota should cover oracle review and retirement as well as task count; version retired/broken tasks instead of silently replacing difficult ones. Sample count, stratum weights and feasible review capacity are unknown.

Separate matched-harness attribution (same exact model route where possible) from full-product utility and release conformance. A behavior advantage when the model, prompt or tools differ is a package effect. The existing DS11 pilot numbers are prior design examples, not power evidence or a campaign authorization.

**Recommendation / admissible rival:** a stratified paired task panel plus stable conformance core versus a conforming fixed census of the explicitly bounded workflow portfolio. **Falsifier:** material population strata cannot be sampled or the panel omits failures seen in its reserved family set. **Non-proof:** representative coverage of all future work. Local handoffs W-H01/W-H08.

<a id="rw-q02"></a>
## Q02 — Objective acceptance and independent oracle

Define `Accept(task, final_artifacts, canonical_evidence, independent_environment_observations)` before implementation. It is true only when all required behavior predicates, no-regression predicates, authority/privacy/effect floors, provenance and accounting-completeness rules hold. A runner exit code, success string, matching filename, schema-valid receipt or candidate-authored test cannot alone satisfy it. A missing or undecidable predicate yields **inconclusive**, never pass; machine-checkable pass/fail applies only to complete valid evidence.

Each predicate identifies the intended behavior, precondition, authoritative observation surface, expected positive and negative behavior, independent author and review record. Tests run against immutable evaluator inputs; the candidate cannot alter tests, expected states, classifier rules, evaluator executable, environment instrumentation or the record of assignment. Candidate-added tests may contribute evidence but cannot replace the external acceptance gate. Keep oracle assets outside the candidate's writable/readable domain where secrecy is necessary; record any exposure.

Validate construct validity using paired controls: a known valid solution; a plausible format-only artifact; correct prose with absent effect; effect in the wrong workspace; replayed prior receipt; missing/forged evidence; test deletion or skip; leaked-answer-only patch; equal-size corruption; and a correct alternative implementation that does not resemble the reference. Positive controls guard against overstrict oracles; failures of known-invalid controls invalidate the gate. Metamorphic relations (renaming synthetic IDs, reordering independent observations, equivalent representation) supplement but do not replace a reference outcome.

**Recommendation / rival:** independently authored end-state plus causal-evidence oracle versus separately authored executable reference-state machine with independent black-box checks. Both preserve the same floors. **Falsifier:** any deliberately invalid outcome passes, or a valid alternative fails because of irrelevant formatting. **Non-proof:** complete semantic correctness outside the enumerated predicates. W-H02/W-H03.

<a id="rw-q03"></a>
## Q03 — Provider- and route-neutral gates

The invariant contract names logical goal, workspace, actor/grant epoch, operation/effect identity, authorized state transition and useful artifact. It does not require a vendor's session ID, tokenization, console wording or internal planning trace. Each adapter maps raw evidence to that contract with loss and unknown fields; the independently maintained mapping is tested separately from the candidate. Native, upstream and combined arms use the same required semantic predicates and equally scoped tool/credential access.

Use a preregistered capability manifest to identify eligible task-route pairs before seeing outcomes. If a route lacks a required capability, report “ineligible for this task” and the lost coverage. Do not quietly remove the task from the product release gate. A semantically equivalent human-mediated export/rehydration alternative can be a control if specified in advance; count its effort. Do not force every route through identical incidental mechanics or downgrade the task for one arm. Native-only and upstream-only cases are separate strata; helpers must use their declared eligible execution route, with no hidden API.

**Recommendation / rival:** one neutral semantic contract with independently validated evidence mappings versus task-specific black-box evaluators that share a common floor contract. **Falsifier:** an outcome changes solely because a vendor label or equivalent event encoding changes. **Non-proof:** identical capabilities, tokenizer units, legal eligibility or universal feature parity. W-H03.

<a id="rw-q04"></a>
## Q04 — Productive continuity and all six journeys

A continuity task has a useful pre-disruption objective, an externally scheduled disruption, an intact counterfactual baseline, and a post-disruption useful-work gate. Trigger at a declared logical boundary, not when one candidate happens to be succeeding. Register both expected and unexpected Stop separately from crash, disconnect, timeout and voluntary abandon. Injecting loss must not expand authority.

| D024 journey | Required accepted behavior and independent observation | Strong conforming comparison |
|---|---|---|
| 1. Native → upstream → native | Preserve logical goal, current grants, exact task/gate, evidence/artifact reachability, remaining reservation and unresolved effects; produce the same useful outcome. Report explicit loop/context losses, not portable-loop fiction | Direct native/upstream tools plus competent portable artifact transfer under the same launch/authority envelope |
| 2. Compaction and upstream-session loss | Reconstruct from non-droppable capsule and authorized artifacts; revoked directives stay revoked, citations retain source identity/freshness, all compaction/rebuild cost included | Same-route native compaction plus explicit cold reconstruction, with equal allowed information |
| 3. Full Stop, unreachable node, unresolved external operation | Close new admission; track local descendants, remote unknowns and fences; no repeat effect until reconciliation establishes its status. Useful completion resumes only within a fresh valid grant | Minimal conforming supervisor with explicit pending-effect ledger and operator reconciliation |
| 4. Fork dirty unfinished source | Distinct fork/workspace identity, preserved original dirty bytes and lineage, no accidental cross-write, task/gate/evidence references and split reservations explicit | Direct detached/worktree-style source copy with independently verified identity and manual ledger |
| 5. Worker disconnect, owner detach, reconnect | View loss does not kill or authorize work; late messages carry valid epoch/identity; duplicate completion cannot duplicate effects or cost; productive continuation or honest hold after reconnection | Direct harness resume/reconnect plus a deterministic fenced coordinator |
| 6. Honest subscription quality tradeoff | User-selected profile retained; resource units and unknowns shown; independent quality floor and first review applied; no undeclared routing/spend/helper call | Direct same-harness profile with native caches/helpers available and the same budget |

Authority survival means no widening and current revocation enforced, not merely identical serialized old grants. Evidence survival means references independently resolve and authenticate the intended revision, not just equal counts. Accounting survival means one parent allocation reconciles attempts, retries, cancellations, recovery, helpers and unresolved usage without recrediting unknown work. All three are conjunctions with useful completion, not substitutes for it.

For Aggressive, Full and Lazy treatments, bind scope, admission cutoff, checkpoint policy, interrupt request, drain allowlist, deadline/escalation and effect settlement. Observe completion of each requested control independently; a killed PID is a local event only. Lost-machine profiles include D020 optional writer takeover and core-only honest unavailability as distinct declared configurations, with receiver fences mandatory in both. D028 abrupt VM reset is the accepted durability boundary; physical power interruption is not added.

**Recommendation / rival:** paired disruption plus useful-work episodes versus the same conforming journey represented as a scripted operator study with external fault injection. **Falsifier:** preserved metadata coexists with stale authority, lost evidence, duplicate/unknown-erased consumption or failure to complete the useful objective. **Non-proof:** arbitrary session-state portability or reversal of external effects. W-H04/W-H05.

<a id="rw-q05"></a>
## Q05 — Regression detection, baseline and tolerance

Use the last independently accepted exact candidate/profile as the engineering baseline and a separately frozen direct/minimal comparator for benefit claims. Keep old raw artifacts when a baseline updates; a new version does not reset away regressions. Trigger affected conformance and empirical revalidation on candidate, adapter, model, context, tool, dependency, platform, oracle or resource-policy changes.

For each endpoint predeclare direction, practically important regression margin, uncertainty method and decision role. Hard invariants have a deterministic rejection rule; they do not receive a compensating statistical margin. For variable quality, cost, tail latency and review effort, numerical tolerances remain **unknown** until justified by the owner and calibration. Use paired task/time blocks and unchanged control-arm reruns to distinguish candidate change from shared service or infrastructure drift. A control chart can alert; it is not by itself causal attribution or release approval. Investigate benign drift, document its source and rerun affected blocks under the frozen analysis. Do not retrospectively expand resource limits for the losing arm.

If a confidence region still includes material harm, the result is inconclusive for non-inferiority. An observed floor violation blocks promotion even if average performance improves. Preserve raw latency for timeouts and error outcomes; use time-to-acceptance analysis and fixed-horizon completion rather than successful-only medians.

**Recommendation / rival:** paired fixed-release confirmation with event-triggered canaries versus a prespecified always-valid sequential monitor using the same eligible controls. **Falsifier:** seeded material regressions escape the registered detection rule at its declared sensitivity, or ordinary infrastructure drift produces unacceptable false alarms. **Non-proof:** reliable detection below the powered effect size or before the observation horizon. W-H06/W-H08.

<a id="rw-q06"></a>
## Q06 — False-green controls and mutation validity

Maintain separate layers: (1) artifact/schema validation, (2) fault exposure, (3) semantic oracle detection, (4) accepted task behavior, (5) independent reproduction. A single PASS field spanning these layers is prohibited.

A mutation registry records exact source revision, edit, intended violated rule, runnable preconditions, bounded exposure witness, equivalent/unreachable/inconclusive classification, expected independent detector and observed kill mechanism. Count reachable non-equivalent semantic faults separately from syntactic/TypeOK deaths. Every row must be classified; absent rows are not a small successful denominator. A baseline that fails invalidates that comparison before mutation scoring. Reachability must precede non-kill interpretation. Stronger bounds can uncover a baseline fault rather than prove mutation sensitivity, as the FU03 candidate illustrates.

Negative controls are intentionally invalid: stale grant, unknown usage set to zero, forged completion, missing scope, duplicate dispatch, hidden helper, weakened stop, altered test, reused result digest, constant-pass grader and corpus-label leakage. Their isolation is mandatory and they are excluded from efficiency competitors. Include historically observed bug patterns as well as one-site mutants; deliberately combine interacting faults after single-fault diagnostics. Calibrate an always-reject grader with known-good artifacts too, so “no false greens” cannot be purchased by accepting nothing.

Independence dimensions are recorded independently: human/agent author, model family if used, account/host, implementation/dependency sharing, specification lineage, evidence access, candidate-label blinding, held-out tasks and result custody. Different model names do not make two judges independent. Accepted V0–V3 floors remain; compare two conforming verifier arrangements, never remove required verification as the favorable cost baseline.

**Recommendation / rival:** spec-linked fault registry plus independently sourced historical faults versus independently generated property/metamorphic fault campaigns, both with exposure and good controls. **Falsifier:** constant-pass/receipt-forgery controls survive, or a claimed semantic kill is only an unrelated structural failure. **Non-proof:** every real defect is represented or all correlated verifier error is removed. W-H02/W-H07.

<a id="rw-q07"></a>
## Q07 — Primary endpoints and denominator contract

Freeze three distinct verdicts: runner-reported completion; first independent review; blinded specification audit. The last must not merely reread the same runner flag. Store original judgments and revisions append-only.

- **First-review acceptance (FRA):** independently accepted first submitted artifact at the frozen quality/floor criteria, without a correction cycle, per all assigned eligible task episodes. Episodes with no submission, abandonment or failure remain in the denominator. A reviewer correction followed by a pass is repaired acceptance, not FRA. Review not yet complete is unresolved and included in bounds, never an exclusion.
- **Spec-level false-green rate (FGR):** independent spec-audit rejects among first-gate greens, divided by all first-gate greens with complete audit; report the audit coverage denominator and unresolved count alongside. For a fully audited assigned cohort, this estimates `P(spec reject | gate green)` under that cohort's task distribution. If only a probability sample is audited, use its prespecified design weights and uncertainty. Convenience audit cannot estimate cohort FGR.
- **Conservative uncertainty:** with `g` greens, `f` confirmed false greens and `u` unresolved audits, report the identification interval `[f/g, (f+u)/g]` plus sampling uncertainty where applicable. If `g=0`, conditional FGR is undefined; do not report zero. For FRA use analogous lower/upper bounds across all assigned tasks when first review is unresolved.
- **Negative-control false acceptance:** invalid planted controls accepted / exposed invalid controls, per defect family. This is detection sensitivity evidence and not the natural-workload FGR prevalence.

Register a delayed-audit horizon and defect attribution rule. A later independently established defect can change final quality and escaped-defect endpoints while preserving the timestamped original first-review decision. Unmatured cohorts must be labelled; “no defects yet” is not final reliability. Reviewer disagreement is a separate observation, not automatically truth.

**Recommendation / rival:** full blind spec audit of gate greens versus a preregistered probability-sampled audit with honest bounds and mandatory high-risk coverage. Both meet fixed review floors. **Falsifier:** endpoint values change when the runner's success wording changes with artifacts fixed, or unaudited greens silently count as true. **Non-proof:** zero conditional errors when no greens exist or when observation is incomplete. W-H02/W-H08.

<a id="rw-q08"></a>
## Q08 — Flakiness, stochastic performance and quarantine

First rerun the **same frozen artifact through the same gate** to estimate evaluator instability. Separately repeat candidate generation on the same task to estimate model/agent variability. Separately vary controlled infrastructure, task order and independent reviewers. Do not call all three “model randomness.” Record task, repository, candidate run, oracle run, reviewer, seed availability, host and time block; variance decomposition follows these nesting/crossing relationships.

Before confirmatory admission, define per-gate stability criteria and a finite repeat protocol using known-good and known-bad controls. Numeric repeat counts/tolerances remain unknown. No rerun-until-pass rule. A deterministic safety gate with unexplained discordant outcomes is invalid pending diagnosis. Stochastic outcome endpoints can remain valid with repeated trials and uncertainty; they are not automatically quarantined because the agent sometimes fails.

Quarantine is versioned and approved blind to arm labels. Retain affected assignments, resource use, trigger and impact in the result ledger; the primary analysis reports invalid/missing outcome bounds, with a prespecified validated-subset sensitivity analysis. Fixing a gate creates a new oracle version and reruns all affected arms, including previously green results. Inconclusive or systematically one-sided flakiness blocks a comparative claim.

**Recommendation / rival:** artifact-level stability qualification plus nested task repeats versus dual independent gate implementations with adjudicated discordance and repeats. **Falsifier:** an unchanged known artifact alternates verdicts beyond the accepted tolerance, or quarantine preferentially removes one arm's failures. **Non-proof:** future infrastructure stability or repeat-independent errors. W-H06/W-H08.

<a id="rw-q09"></a>
## Q09 — Confirmatory preregistration contract

Before confirmatory assignments, freeze and independently review the following; the machine template is `preregistration-template.json`, deliberately not an accepted registration:

1. Decision to inform, claim scope, intended task population, estimand and directional hypotheses
2. Primary FRA/FGR and required floors; secondary quality, resource, latency, continuity, human-effort and maintenance endpoints; units, denominators and observation horizons
3. Exact task/suite/partition/oracle versions and digests; eligibility, sampling probabilities, difficulty rules, contamination checks and custody of held-out answers
4. All treatment configurations, strongest eligible controls, matched versus package-effect designation, capability toggles and semantic-loss declarations
5. Candidate/harness/adapter/model identity, model settings, tools, native context/caches/helpers, platform/profile/resource limits, allowed egress and authority envelope
6. Randomization and blocking, assignment sequence custody, repeated-trial structure, reviewer allocation and blinding
7. Minimum important effect, non-inferiority/equivalence margins, familywise error allocation, desired power or precision, sample-size method and justified nuisance assumptions
8. Analysis equations, dependence handling, weighting, interval method, planned contrasts, multiplicity and any interim looks/adaptation
9. Missingness, infrastructure failure, Stop/crash, timeout, quota exhaustion, human rescue, late events, abandonment, crossovers and exclusions; no post hoc successful-only denominator
10. Fault/oracle positive and negative controls, independent reproduction requirement, audit escalation and dispute procedure
11. Budget/resource/review ceilings, safety stops, futility rules, trial horizon and criteria for a new registration
12. Data minimization, local retention, release/redaction permissions, all-result ledger, author/conflict disclosures and exact promotion/withdrawal rule

Record registration digest and timestamp before collecting confirmatory outcomes; registration amendments preserve predecessor, reason, prior exposure and timestamp. A pilot used to tune thresholds is development data. A preregistered exploratory analysis is still exploratory if its question is not confirmatory. Use a results-blind protocol review patterned after Registered Reports without claiming journal acceptance.

**Recommendation / rival:** immutable local registration with independent custody versus an authorized embargoed external registration with the same contents. No external posting is authorized here. **Falsifier:** fields influencing decisions can change after unblinding without a declared amendment/new cohort. **Non-proof:** a scientifically valid design merely because its file was timestamped. W-H01/W-H08.

<a id="rw-q10"></a>
## Q10 — Power, sample size, effect size and uncertainty

Power is conditional on the selected estimand, minimum meaningful difference, paired-task discordance, task clustering, repeat variance, audit prevalence, allocation and multiplicity. None of these has a measured local value sufficient to fix a new campaign size. Derive the confirmatory size from a separately identified calibration/pilot and a sensitivity range for uncertain nuisance parameters; choose the size required by all co-primary decisions and mandatory strata. When budget cannot support it, report a precision-limited descriptive study, not “no difference.” No numerical power claim is made here.

For paired binary acceptance, retain the joint outcome table per unique task; a paired test/interval uses discordance rather than pretending two independent proportions. Repeated model trials inform each task's success distribution; dependence across shared repositories and source lineages must enter the analysis. Generalization to sampled tasks requires task-level or cluster-aware resampling/inference; seed-only intervals on a fixed suite answer a narrower question. Report these two uncertainty targets separately.

Use absolute acceptance-risk differences, absolute FGR and false-acceptance differences, resource/time/person-minute differences, plus compatible ratios with denominator checks. Choose interval procedures appropriate to bounded counts, rare events, heavy tails and clustering, with small-sample limitations declared. When no false greens are observed, report an upper uncertainty bound; do not assert a zero population rate. A quality non-inferiority claim requires its lower confidence bound above a justified negative margin; equivalence requires the entire accepted interval inside both bounds. Nonsignificance alone meets neither test. Bayesian alternatives require prespecified priors, sensitivity and decision loss rather than opportunistic switching after results.

**Recommendation / rival:** task-paired frequentist intervals and precision/power planning versus a prespecified hierarchical Bayesian model with prior sensitivity and the same hard floors. **Falsifier:** nominal coverage or decision sensitivity fails accepted calibration, or findings reverse under reasonable clustering/missingness assumptions. **Non-proof:** meaningful equivalence from wide overlapping intervals. W-H08.

<a id="rw-q11"></a>
## Q11 — Multiplicity and sequential/adaptive analysis

Define the confirmatory family before assignment: route/profile contrasts, task classes, primary endpoints, continuity conditions and time looks. A conjunction of all mandatory floors is not a contest to select the most favorable endpoint. Use a closed hierarchical gate: conformance and measurement validity first; quality/FGR requirements next; named efficiency/continuity benefit only thereafter. Preserve the entire vector regardless of which tests proceed.

One conforming option is fixed-horizon familywise control by preallocated Bonferroni bounds: choose per-test error budgets summing to no more than the family budget; the union bound controls any false rejection without requiring independent tests. Another is a prespecified step-down familywise method with its assumptions and exact algorithm independently reviewed; Holm's original paper is identified in W-S22, but its full text was not successfully retrieved here, so no implementation is certified from that citation. Exploratory subgroup discoveries require a new held-out confirmation, not retroactive expansion of the primary family.

For repeated looks choose in advance a valid alpha-spending/group-sequential design or an appropriate time-uniform confidence sequence. Do not repeatedly use fixed-sample intervals until they become favorable. Safety/floor violations stop immediately irrespective of statistical significance; a safety stop does not become an efficacy win. Response-adaptive allocation or route policy changes alter the sampling distribution; freeze them for confirmation or preregister valid estimators with logged assignment probabilities and positivity. Unknown assumptions block confirmatory interpretation. Calendar-based canaries are surveillance with a separate error budget, not accumulated evidence silently pooled into the original run.

**Recommendation / rival:** fixed-horizon familywise design versus preregistered sequential familywise monitoring with bounded resource/review expenditure. **Falsifier:** false-positive control is lost under the actual look/allocation rules, or analysts choose a family after seeing results. **Non-proof:** detection of arbitrary rare regressions or unrestricted adaptive validity. W-H08.

<a id="rw-q12"></a>
## Q12 — Held-out generalization and contamination

Split by substantive source lineage, repository, problem family and solution mechanism before tuning. A renamed or perturbed variant of the same issue is not an independent holdout. Maintain development, locked within-population confirmation, and explicitly out-of-distribution panels (new repository/domain, longer dependency horizon, unseen fault combination or platform/profile) with separate estimands. No proportion or sample count is selected here. A protocol may name population-level generalization only if its sampling and uncertainty support it.

Independent custodians hold task identities where feasible, test assets and answers. Freeze candidate, prompt/config and analysis before release of the held-out assignments. Log benchmark/task retrieval, cache/memory provenance, publicly available solutions, developer exposure and any prior evaluation contact. Training exposure is often unverifiable; report that limit. Freshness dates and network-denied tasks reduce some contamination routes but cannot prove absence of pretraining contamination. Do not send private corpus data to public decontamination searches.

If tasks leak, retain their assigned outcomes in the main ledger, mark exposure and apply the predeclared sensitivity/retirement rule. Repeated use consumes a holdout for tuning; replenishment needs a new version and new registration. OOD failure narrows the claim rather than disappearing from a leaderboard. Adapting on holdout responses means the final result is adaptive/development evidence unless a valid separate protocol reserved further unseen tasks.

**Recommendation / rival:** custodian-held source/family split versus prospective fresh-task enrollment under a frozen candidate, both with exposure tracking. **Falsifier:** the claimed unseen-family advantage disappears on reserved families or relies on answer exposure. **Non-proof:** universal transfer or contamination-free training. W-H01/W-H08.

<a id="rw-q13"></a>
## Q13 — Null, negative, stopped and abandoned results

Allocate immutable experiment and assignment IDs before dispatch. The registry contains every admitted and rejected-for-eligibility cohort, all attempts, no-output failures, cancellations, safety stops, human rescues, abandoned runs and final verdicts. Record stop reason and decision maker, elapsed resources, review debt, available outcome evidence and unresolved fields. A study that never starts is UNEXECUTED, not a null result. A stopped study with insufficient information is inconclusive; neither it nor a negative finding may be omitted because it weakens the product claim.

The result packet shows planned versus realized assignments; deviations; count flow by exclusion reason; confidence regions; unplanned analyses; missing data; and claim disposition (supported within scope, contradicted, equivalent within accepted bounds, inconclusive, or not identifiable). Corrected reports preserve prior versions and explain why conclusions changed. Publication is separately authorized; “retain a publication-ready all-result record” is not permission to publish private data or a report.

Use fixed task horizons for primary acceptance and separate delayed follow-up. Late improvements do not rewrite a timeout into an on-time success; delayed defects update mature quality. Dropout due to quota, crashes or difficult work is plausibly informative, so report conservative identification bounds/sensitivity rather than assuming missing at random. Statistical survival summaries require explicit censoring assumptions; otherwise show horizon completion and unresolved counts. R-D's estimand contract applies; ICH E9(R1) is methodological analogy, not a regulatory obligation. [W-S23](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)

**Recommendation / rival:** append-only all-assignment registry versus independently archived immutable cohort bundles with a complete index. **Falsifier:** an assigned failed/abandoned task vanishes or late outcomes overwrite original timing. **Non-proof:** absence of publication bias outside this controlled registry. W-H09.

<a id="rw-q14"></a>
## Q14 — Multi-endpoint standard and lineage

Every metric row must carry its source lineage, unit, numerator, denominator, observation horizon, route/profile key, evidence class, missing reason, collection coverage, uncertainty and raw-evidence reference. The endpoint appendix contains these contracts without invented observations.

| Endpoint group | Required report | Recorded basis |
|---|---|---|
| Verified quality | FRA, final accepted completion, spec FGR, planted false acceptance, escaped defects and severity; all-assigned denominator and audit maturity | DS11; R-D C1/C3/H4 |
| Continuity | Per-journey accepted transition; time to first independently verifiable useful action and final acceptance; authority/evidence preservation and explicit semantic loss | DS11/DS12/DS25; R-D C1–C3/L1/L2 |
| Native allowance and money | Attributable native allowance or randomized window debit with uncertainty; paid charges separately; no token-to-subscription conversion | DS26; R-D Q1–Q5 |
| Model/tool resources | All-role input/output/reasoning/cache/compaction, helpers, retries, tools and verification/repair; observed versus estimated fields distinct | DS12/DS26; R-D U1–U10 |
| Host and disabled-path cost | CPU, memory, storage, I/O, processes and orchestration; forbidden disabled activity separately from metadata enumeration overhead | DS10/DS26; R-D U11; R-O |
| Latency | Assignment to useful result/acceptance; queue, permission, execution, recovery and review components; tails, timeouts and unresolved outcomes | DS10/DS11/DS25; R-D C2/H1 |
| Reliability | Crashes, recovery failures, Stop/control failure, evaluator flakiness, repeated-task success and delayed outcome maturity | DS11/DS25; R-D C1–C3/U6/U12 |
| Human and review debt | Active person-minutes by role, corrections/rework, first/final review, queue age, unresolved obligations and eventual downstream repair | DS10/DS11; R-D H2–H4 |
| Instrumentation completeness | Attempt coverage, missing reports, clock/counter scope, duplicated observations and unallocated consumption | DS26; R-D U12 |
| Maintenance/port cost | Setup, integration, semantic mapping, test/review, update repair, abandoned ports; observed reuse versus hypothetical amortization | DS10; R-D L3/L4 |

Report all-assigned totals, per-assigned-task burdens and ratio-of-cohort-sums per independently accepted outcome. If no outcomes are accepted, cost per accepted outcome is undefined alongside total cost, not zero. Do not average only successful-run costs. Aggregation across incompatible tokenizers, subscription units or money/resource dimensions is prohibited. Pareto profiles and owner-visible tradeoffs can be discussed after floors; no scalar masks quality, privacy or review debt. Current values for every listed target endpoint are unknown.

**Recommendation / rival:** typed endpoint vector with floor-first decisions versus prespecified lexicographic decisions accompanied by the same complete vector. **Falsifier:** a reported improvement disappears when failed/helper/review work enters the denominator, or a floor regression is hidden by aggregation. **Non-proof:** a universal optimum or a monetary value for unpriced labor. W-H09/W-H10.

<a id="rw-q15"></a>
## Q15 — Fair treatments, strong controls and single-count accounting

Run distinct questions, not a single muddled leaderboard:

1. **Matched-route attribution:** same model revision, endpoint/account regime, reasoning setting, allowed tool capability, initial task/context, effective total budget, platform/resource envelope and review criteria. Same native cache/memory/resume/helper opportunities are available; don't weaken the direct harness. The candidate's added orchestration is the treatment. Record unavailable proprietary prompt/settings as residual confounders; exact model name equality alone is inadequate.
2. **Best-configured practical utility:** each conforming system receives equal disclosed tuning opportunity under the same useful-work requirements, floors and overall budget. This estimates whole-product utility, not an isolated harness mechanism.
3. **Capability/profile treatment:** installed-disabled, enabled-idle, and task-activated configurations are separately identified; task, acceptance and authority remain unchanged where a clean toggle exists. If disabling removes a required task capability, it is a coverage/refusal test, not a quality-matched efficiency rival. Compare two conforming implementations of that required capability instead.
4. **Release conformance:** all accepted capability/profile obligations remain, even when a lean configuration is the fastest empirical arm. A capability's null benefit in one workload does not remove it from D019.

Strong controls are (a) competent direct use of the exact eligible harness with native facilities, (b) a minimal single-agent loop under the same external authority/containment/receipt envelope, and (c) a minimal deterministic orchestrator with explicit artifacts, checkpoints, effect ledger and required review. Use Aider/mini-style simplicity only when its actual configured envelope satisfies the task floors; T3-style operator workflows are practical comparators only in eligible scopes. No public product is presumed qualified. Unsafe/no-review/no-fence/no-credential-boundary variants are negative controls only.

Block and randomize order by task, route, machine and time/quota window; prevent cross-arm caches, memory, worktrees and answer contamination except in explicitly shared-state treatments. Warm/cold states and no-future-work conditions are separate. Same budget means same full accounting boundary, not just equal main-model tokens or equal wall time while one arm hides helper spend. Do not force differing native unit regimes into a false matched claim.

Use one immutable operation ID with separate attempt IDs and external-effect IDs. Register an attempt before dispatch, including crash-before-receipt. A collector may receive duplicates; deduplicate observations by source and revision, not distinct genuine attempts. Parent aggregate counters and child itemized counters are reconciled representations, not summed twice. Compaction, retries, synthesis, failed work, verification, human corrections and settlement all remain chargeable. Late revisions replace/adjust the authoritative counter version with lineage, not a second charge. Unknown hidden attempts make denominator coverage unknown. Corroborate a zero only with complete independent activity coverage and calibrated tripwires.

**Recommendation / rival:** matched-route experiment plus separate practical-utility comparison versus a single carefully bounded best-configuration study labelled package effect. **Falsifier:** the estimated advantage depends on unequal model/tool/context/budget access or omitted baseline facilities. **Non-proof:** perfect control of proprietary service internals or all account regimes. W-H03/W-H09/W-H10.

<a id="rw-q16"></a>
## Q16 — Human effort and review throughput

Measure person-minutes, not just elapsed time: preparation, supervision, approvals, steering, review, dispute resolution, correction, reconstruction, tool repair and later defect work. Record activity boundaries with minimal content-free timers and role/category codes; self-reports can supplement, not silently replace missing measurements. One person's overlapping minute cannot be double counted; simultaneous work by two people legitimately sums to two person-minutes. Waiting is elapsed latency, not active labor.

Blind artifact review to arm and claimed success when possible; normalize presentation without removing behaviorally important evidence. Record accidental unblinding. Balance reviewers by expertise and task, randomize order, use fresh equivalent tasks or balanced groups to avoid the same reviewer learning the answer from one arm, and calibrate rubrics with independent reference artifacts. Intra-/inter-reviewer disagreement and audit time are measured. Correction count uses linked intervention events with severity and root cause, not changed-line count. Scripted task instructions are not counted as rescue.

Maintain outstanding review obligations, queue age, arrivals, independent closures, unresolved defects and rework minutes. Freeze a follow-up horizon to expose generated work whose debt was merely deferred. Report both workflow-operational effort and study-only instrumentation/audit overhead; also show their combined total. Measuring labor itself consumes labor and can change behavior. Calibrate that overhead on a separate authorized study; no current amount is known. Equal review staffing/capacity is part of the treatment envelope, and throughput is accepted useful work per review capacity, never token output.

**Recommendation / rival:** content-minimal time diary plus event-linked independent review versus consented structured observation/time sampling with equivalent privacy limits. **Falsifier:** savings reverse after deferred review/reconstruction or measurement overhead is included, or reviewer carryover determines the result. **Non-proof:** subjective cognitive burden, satisfaction or monetary labor value. W-H10.

<a id="rw-q17"></a>
## Q17 — Anti-lock-in and workload-specific savings

Separate two required claims. **Portability:** one authorized goal completes across more than one eligible harness/route, preserving current authority, evidence, source identity and honest accounting without ungranted credential custody. **Resource advantage:** for a named workload/account regime, the full cohort burden improves versus competent direct operation at accepted quality/FGR and recovery floors. Passing one does not establish the other.

D029 requires a trusted operator-provisioned launch domain outside Recursion's readable boundary; OS read denial alone does not block a credential-bearing CLI from exporting secrets through unconstrained tools or output. Require launch/tool/output/egress conformance for the exact profile before any strong credential non-access statement. A profile labelled policy-only cannot enter the strong-boundary comparison as if equivalent. Credentials, route terms and entitlement are eligibility gates, not performance endpoints; no account call or counsel contact occurred here.

Source→destination migration compares the best eligible direct export/resume/portable-artifact/manual reconstruction path plus a no-switch arm where useful. Count revalidation, mapping, lost-work reconstruction and all support/maintenance cost. Native allowance can be evaluated per isolated task only if attributable; otherwise randomize eligible windows/cohorts and preserve rounding, resets, concurrent use and delayed updates. If data identify only token activity, say so and withdraw a quota-savings claim. If accepted intervals show worse/no meaningful benefit, report that result; if inconclusive, withhold superiority. A legal/security ineligibility is not a performance loss. D031 prohibits vendor-intent inference regardless of result.

**Recommendation / rival:** joint portability-and-burden evaluation against direct and minimal conforming paths versus a narrower single-route workflow claim with explicit transition limitations. **Falsifier:** a required transition violates a floor or complete attributable burden does not meet the preregistered advantage criterion. **Non-proof:** universal portability, transferable subscriptions, route legality or malicious vendor intent. W-H04/W-H09/W-H11.

<a id="rw-q18"></a>
## Q18 — Provenance, custody, retention and independent rerun

A reportable cohort binds suite/task/source/oracle/configuration/assignment digests; candidate, native loop, adapter, binary and dependency revisions; model/service identity and capture time; exact OS/filesystem/resource profile; authority/privacy/capability profile; registered analysis; sampling/seed record; assessor identities and independence dimensions; collector versions; and immutable run/attempt/receipt IDs. Hash raw bytes or a declared canonical encoding, never call an excerpt hash a full-page hash. Mutable web pages in the source register are dated observations; unresolved revision/digest is explicitly null.

Keep bounded, access-controlled raw evidence sufficient for reconstruction: assigned inputs, authorized tool/action records, outcome artifacts, independent observations, counters, timing, verdicts and deviations. Do not collect hidden chain-of-thought or secrets. Store redacted public projections separately with an auditable transformation; a redaction may prevent public reproduction, which must be disclosed. Retention length, access roles and release audience require an accepted policy and remain unknown here. Deletion follows policy while preserving permitted aggregate/correction metadata; no promised universal raw retention.

An independent verifier first reruns the frozen analysis from retained data, then independently reruns the accepted protocol against the pinned candidate/profile and controls. These are different checks. Use fresh held-out tasks for extension claims; rerunning familiar tasks verifies repeatability, not generalization. Prefer genuinely separate oracle implementation/custody and author, with any shared dependencies declared. A different model family is useful diversity, not a sufficient independence proof. Agreement of two systems copying one faulty expected output is not corroboration.

No benchmark result has acceptance authority until the required independent rerun and owner acceptance. If a service revision cannot be reproduced, label the historical observation and limitation; do not silently update the baseline. A corrected oracle invalidates affected conclusions until affected comparisons are rerun. Public release additionally respects counsel/privacy/authorization gates; this report publishes nothing.

**Recommendation / rival:** immutable per-run evidence bundles plus independent execution versus a replicated read-only evidence archive and separately implemented external oracle under the same privacy contract. **Falsifier:** source-to-verdict reconstruction fails, or the independent run does not meet the registered outcome/uncertainty rule. **Non-proof:** correctness by hashing or unlimited reproducibility of proprietary services. W-H09/W-H12.

<a id="rw-q19"></a>
## Q19 — Provider-free versus human-gated layers

Exact D028 scope is Windows 11 25H2 build 26200 Home/Pro x64 plus separately qualified 24H2 build 26100 Enterprise x64, local NTFS; Linux 6.12 LTS primary and 6.6 LTS compatibility minimum with cgroup v2 and local ext4. WSL2-ext4 and WSL2 `/mnt/c` are distinct development/test cases only. Arm64 is a separate later case; SMB/NFS canonical state and ReFS/xfs/btrfs are outside the first-release scope. Every result is profile-keyed; no profile is qualified by this report.

| Layer | What a later authorized local session can establish | What it cannot establish | Current state |
|---|---|---|---|
| Static provenance/manifest review | File identity, schema completeness, declared dependency and predicate mapping | Runtime absence of effects or semantic success | Static observations only |
| Deterministic kernel/routing/admission/replay | Known-answer transitions, invariant preservation within explicit bounds, refusal behavior | Model task quality, arbitrary-depth correctness or live route behavior | UNEXECUTED here |
| Stub harness and synthetic fault layer | Stream/attempt/accounting semantics, Stop/checkpoint/drain ordering, duplicate/late events and loss mapping | Real binary/authentication/telemetry completeness | UNEXECUTED |
| Grader/negative-control/mutation layer | Detect specified invalid outcomes, validate known-good outcomes, classify exposed faults | Population false-green prevalence or exhaustive real faults | UNEXECUTED |
| Native platform/isolation layer | Exact-profile process, receiver-fence, storage and boundary behavior on approved disposable rigs | Different OS builds, uncontrolled CLIs, cloud provider cancellation | Human-approved local/host gate; UNEXECUTED |
| Statistical pipeline layer on synthetic records | Denominators, missingness, multiplicity/interval implementation and claim refusal; calibration under declared data-generating assumptions | Empirical task effects; simulations are not observations | UNEXECUTED, including simulation |
| Real installed binary without inference | A separately authorized offline/loopback profile's controls, where verified possible | Account entitlement or provider behavior | Human-gated, no entrypoint qualified here |
| Live model/provider/account regime | Empirical task quality, actual counters/allowance, helper behavior, service latency and real migration | Unmeasured future routes or vendor intent | Every run human-gated; UNEXECUTED |

Provider-free means no provider/model/account calls; it does not mean harmless, free of host effects, or automatically authorized. A local model is also a model call and is outside this session. A destructive containment or VM-reset test requires its own admitted disposable environment. Documentation of a headless route does not authorize running it.

**Recommendation / rival:** staged provider-free semantic and measurement qualification before live evaluation versus a smaller independently sufficient provider-free contract corpus with separate native-profile qualification. Both require the same mandatory predicates and authorization. **Falsifier:** a live run is admitted with a failed/unresolved prerequisite, or a claimed provider-free run actually calls inference/network outside its allowed fixture. **Non-proof:** live provider success from stubs. W-H02–W-H11.

<a id="rw-q20"></a>
## Q20 — Promotion contract and local handoff readiness

Promotion is a conjunction, not an average score:

1. Exact source/candidate/profile identity and complete accepted task/oracle manifest
2. Fixed authority, privacy, credential, containment, effect, recovery and disabled-path predicates independently qualified for required scope
3. Clean conforming baseline; all required positive/negative controls behave as specified; every mutation classified with exposure and exact semantics; no unclassified survivor interpreted as acceptance
4. Per-attempt provenance and accounting collectors independently calibrated; missingness and zeros handled honestly
5. Grader independence, stability, blindness, holdout custody and delayed-audit protocol accepted
6. Pre-data registration with justified margins, power/precision, full cost and review ceiling, valid analysis and stopping rules
7. Required eligible routes/profile evidence and fresh human authorization for live model/provider/account/host actions and spend
8. Independent confirmatory rerun and owner acceptance before promoting a measured claim or policy

The current candidate cannot enter a spent confirmatory run: no accepted corpus/thresholds, no complete independent runtime oracles, no route/platform qualifications, no measurement values and no live authorization have been supplied. Closed scope decisions are not qualification receipts. Codex App Server is the first qualification priority under D023, not an already qualified route.

`local-handoffs.json` gives twelve bounded handoffs with inputs, prerequisites, independent oracles, evidence, stopping conditions and non-proofs. No runnable command is fabricated. Known repository files are inspection anchors only; none is certified as an end-to-end entrypoint. A local session must first identify/review the actual target and collector entrypoints without changing the frozen scope.

**Recommendation / rival:** explicit evidence-ladder promotion versus an independently reviewed predicate dependency graph that enforces the same prerequisites. **Falsifier:** any synthetic forged PASS, stale receipt, missing oracle or unknown metric admits live promotion. **Non-proof:** release readiness beyond the accepted predicate set. W-H11/W-H12.

<a id="rw-q21"></a>
## Q21 — Claim limits and decision-ready unknowns

This candidate establishes no measured quality, cost, quota, latency, human-effort, porting or productive-continuity advantage. It supplies no universal superiority, no model-quality ranking, no vendor-intent claim, no route/legal/account entitlement, no production platform qualification and no selected technology or benchmark suite. A future result is conditional on task population, versions, model, tools, budgets, context, infrastructure, oracle, observation horizon and assessor process. Held-out evidence is required for the precise generalization stated; OOD evidence is required for a further OOD claim. Zero observed failures is not zero risk. Hash identity is not truthful evidence; independent rerun is necessary but not omniscient.

The next decision inputs are precise: accepted task portfolio and sampling weights; required per-task profile/capabilities; independently authored machine predicates and audit truth; practically important quality/false-green/latency/cost/review margins; repeat/horizon/retention policies; review budget; approved target environments and execution authority. The smallest discriminators are oracle/exposure reconciliation and telemetry qualification before scaling task volume. These are construction dependencies, not deferrals from D019.

**Recommendation / rival:** narrowly stated claim with explicit withdrawal conditions versus reporting only conformance and descriptive observations until benefit evidence matures. **Falsifier:** a proposed claim needs facts outside its registered scope or omits an unresolved floor. **Non-proof:** success of future implementation or even eventual positive benefit.

## Completion-gate disposition

The exact-text machine coverage register maps all 21 questions and all 10 gate bullets. G01–G09 are answered as research-design requirements; none is an empirical PASS. G10 is bounded to this work: repository/protected paths were not edited; output-only pattern/privacy review found no flagged secret/private capture content, subject to the documented heuristic limits. No repository-wide or runtime security scan is claimed.

The deliverables are the report, exact coverage, source and repository manifests, endpoint contract, preregistration template, local handoffs and artifact QA. All numeric target values remain null/unknown; all runtime handoffs remain UNEXECUTED. Independent review remains pending.

### Complete local procedure links

All procedures below remain UNEXECUTED and retain their independent oracles, prerequisites, stops, competitors and non-proofs.

- [W-H01: Freeze sampling and protocol identity](local-handoffs.json#/handoffs/0)
- [W-H02: Validate gate and fake-pass resistance](local-handoffs.json#/handoffs/1)
- [W-H03: Qualify neutral route evidence mapping](local-handoffs.json#/handoffs/2)
- [W-H04: Exercise all productive-continuity journeys](local-handoffs.json#/handoffs/3)
- [W-H05: Qualify actual platform fault oracles](local-handoffs.json#/handoffs/4)
- [W-H06: Calibrate regression and flakiness detection](local-handoffs.json#/handoffs/5)
- [W-H07: Reconcile FU03 mutations and exposure](local-handoffs.json#/handoffs/6)
- [W-H08: Validate statistical and holdout pipeline](local-handoffs.json#/handoffs/7)
- [W-H09: Reconcile complete cost and result ledger](local-handoffs.json#/handoffs/8)
- [W-H10: Measure review debt and disabled activity](local-handoffs.json#/handoffs/9)
- [W-H11: Audit live-promotion admission](local-handoffs.json#/handoffs/10)
- [W-H12: Reproduce and constrain claims](local-handoffs.json#/handoffs/11)

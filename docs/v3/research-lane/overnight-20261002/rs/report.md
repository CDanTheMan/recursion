# R-S — Adaptive optimization and outcome learning

**Design candidate, 2 October 2026. No adaptive runtime result.**

Repository authority: commit `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. This report answers R-S-Q01–Q22 and R-S-G01–G10. All product fixtures are **UNEXECUTED**. No provider/model/harness call, account action, installation, experiment, simulation, benchmark, repository edit or policy activation occurred.

## Decision-ready finding

Build the accepted opt-in adaptation capability as a **bounded proposal producer** over a conservative static baseline. Its output is a versioned candidate policy, never a grant, executive, effect approval, budget increase or acceptance verdict. A separate deterministic admission path recomputes current eligibility and resource reservations at each effect boundary. The learner cannot modify that path or promote itself.

The strongest practical blocker is evidence identification, not optimizer sophistication. A policy trained only on successful, cheap, promptly reviewed cases can look excellent while excluding difficult work, delayed defects, missing usage and human repair. Passive logs do not reveal the outcomes of unchosen alternatives. Consequently, offline fit, shadow agreement and synthetic safety fixtures are separate milestones; none establishes productive-continuity or subscription-efficiency superiority.

The candidate below compares static rules, periodically revised human rules, offline learned policies and bounded online bandits without selecting an algorithm, model, provider, language, store, runtime, framework or vendor. D-019 remains comprehensive-build/lean-opt-in; adaptation is built but off by default. D-031 forbids an intent narrative. Neither low usage nor a counter discrepancy establishes vendor sabotage.

<a id="rs-s0"></a>
## S0 — Evidence basis and inherited contracts

**Classification throughout:** **D** = source-documented public mechanism; **L** = locally observed static file/artifact fact; **I** = inferred Recursion design candidate; **U** = unknown/unexecuted. Normative Owner constraints are identified as constraints, not experimental evidence. Every proposal in S1–S22 belongs to recommendation S-R01–S-R12 in S23, which supplies its competitor, decisive falsifier and non-proof.

### Static observations and source precedence

- **L:** current governance makes Recursion a native harness and harness orchestrator; Hermes executive authority is retired. D-018–D-033, the active goal and current instructions constrain this report. D-023 is qualification priority, not qualification. D-029's trusted launch requirement is not satisfied merely by declining credential reads; the selected tool/output path must not export credentials either.
- **L:** `TELEMETRY.md` and DS-26 already distinguish attributed quantities from financial/capacity settlement, require missing values to remain null, and subordinate routing to current authority. R-S adds feedback provenance, outcome maturity, off-policy support and promotion controls instead of a competing ledger.
- **L:** the current-branch R-D report already fixes assigned-episode denominators, all-attempt costs, delayed-receipt windows and sequence/window clustering. S2/S18 extend those definitions. The frozen static baseline includes ordinary useful cache/resume/compaction and operator competence, not deliberately weakened functionality.
- **L:** static text search of the inspected `scripts/v3` Python/JSON subset found no adaptive/bandit/reward implementation under those terms. This is a bounded search result, not proof of absence everywhere. No verified executable entrypoint for the new R-S suite was found.
- **L:** FU-03 `RIntegrated.tla` declares reduced constants and explicitly lacks complete authority-dimension predicates and replay/projection state. Its checked-in result records report seven instantiated mutants, five killed. Those records are neither a newly run test nor evidence for this learner, all D-022 modes or the complete integrated gate. Some failures are type-related; they do not demonstrate the intended safety discriminator.
- **I:** R-O's whole-profile resource, collector-sensitivity and no-scalar-score discipline is the performance dependency; see [R-O S1–S3](../ro/report.md#ro-s1) and [handoff](../ro/report.md#ro-s14). R-R is an active companion lane; this report claims no completed R-R runtime evidence. Its sources/cadence/stopping/promotion envelope remains an input, not something adaptation can extend. R-Q's privacy-scoped memory and R-P's untrusted-data boundaries constrain any feedback ingestion.

The old copied brief says a graphical frontend is unnecessary; current instructions say TUI first/GUI later while D-019 includes opt-in GUI capability at first release. This is an exact release-timing interpretation to resolve, not permission to shrink the accepted scope. Adaptation configuration/explanation belongs to the common headless command/query backend and CLI/TUI first; no GUI dependence is introduced.

### Narrow primary-source findings

This is the canonical factual summary for these R-S-specific sources. Subsequent sections are original contract proposals, not additional performance claims from these publications. Versions, dates, retrieval scope and hash limitations are in `source-register.json`.

| Source | D: bounded finding and limit |
|---|---|
| <a id="s-s01-facts"></a>S-S01 — [Li et al., offline replay](https://arxiv.org/abs/1003.5956v2) | Contextual-bandit evaluation observes only chosen-action feedback; replay can be unbiased under its data-collection assumptions. This is a news-recommendation result, not evidence that arbitrary agent logs support counterfactual evaluation. |
| <a id="s-s02-facts"></a>S-S02 — [Dudík et al., doubly robust evaluation](https://arxiv.org/abs/1103.4601v2) | Combines an outcome estimate and a logging-policy estimate; bias and variance depend on their errors, and small action probabilities aggravate importance-weight variance. The method is not a repair for unsupported actions or arbitrary hidden selection. |
| <a id="s-s03-facts"></a>S-S03 — [Laroche et al., safe policy improvement](https://proceedings.mlr.press/v97/laroche19a.html) | Batch-RL baseline bootstrapping constrains changes where evidence is uncertain under its formal assumptions. A baseline-relative performance guarantee is not authorization, per-effect safety or universal robustness. |
| <a id="s-s04-facts"></a>S-S04 — [Kazerouni et al., conservative contextual bandits](https://arxiv.org/abs/1611.06426v2) | Studies a baseline-relative cumulative-performance constraint in a contextual linear setting. Cumulative reward safety does not forbid a single privacy breach or bound every individual effect. |
| <a id="s-s05-facts"></a>S-S05 — [Joulani et al., delayed feedback](https://proceedings.mlr.press/v28/joulani13.html) | Feedback delay affects online-learning regret; consequences differ across the examined stochastic and adversarial settings. No delay-independent local guarantee follows. |
| <a id="s-s06-facts"></a>S-S06 — [Garivier and Moulines, non-stationary bandits](https://arxiv.org/abs/0805.3415v1) | Studies discounted and sliding-window methods under changing reward distributions, including abrupt changes. It provides no provider-drift detector or universally correct freshness period. |
| <a id="s-s07-facts"></a>S-S07 — [Skalse et al., reward hacking](https://arxiv.org/abs/2209.13085v2) | Formalizes divergence between improving proxy reward and true reward; unhackability is a stringent property under the studied policy classes. More proxy optimization is not proof of better accepted work. |
| <a id="s-s08-facts"></a>S-S08 — [Dwork et al., adaptive data analysis](https://arxiv.org/abs/1411.2664v3) | Reusing information to choose later analyses can compromise ordinary statistical validity; controlled mechanisms are needed for adaptive reuse. A repeatedly consulted holdout is not automatically independent. |
| <a id="s-s09-facts"></a>S-S09 — [Howard et al., confidence sequences](https://arxiv.org/abs/1810.08240v9) | Time-uniform inference is possible under explicit assumptions. It does not make ordinary confidence intervals valid under repeated looks, remove confounding or fix missing outcomes. |
| <a id="s-s10-facts"></a>S-S10 — [Hyperband](https://www.jmlr.org/papers/v18/16-558.html) | Uses adaptive allocation and early stopping for hyperparameter search with predefined resources. Early short-run scores need not rank long-horizon task outcomes in Recursion. |
| <a id="s-s11-facts"></a>S-S11 — [RouteLLM](https://arxiv.org/abs/2406.18665v4) | Learns routing from preference data and evaluates quality/cost trade-offs on its chosen benchmarks. Preference labels, model pairs and evaluation setup do not establish this product's acceptance, full-workflow debit or account entitlement. |
| <a id="s-s12-facts"></a>S-S12 — [Harness Tokenomics v2](https://arxiv.org/abs/2609.28919v2) | D: [canonical paper note](../model-architecture/report.md#harness-tokenomics-facts). I: no headline saving is transplanted into this candidate; require observed whole-workflow evidence under the same acceptance contract. |
| <a id="s-s13-facts"></a>S-S13 — [Google SRE canarying](https://sre.google/workbook/canarying-releases/) | Describes limited rollout with attributed control comparisons; shared dependencies and before/after changes can confound evaluation. This is operational prior art, not permission to run live exploration here. |

Provider/protocol facts are deliberately centralized: [shared evidence navigation](../shared-evidence/source-facts.md), especially [Codex](../rf/report.md#codex-app-server-facts), [Claude accounting](../rf/report.md#claude-accounting-facts), and [MCP cancellation/tasks](../protocol-edges/report.md#cancellation-and-asynchronous-tasks). These supply version-specific counter/control facts; no vendor summary is duplicated here. API rate limits, subscription allowance, estimated cost and actual billing remain different dimensions.

<a id="rs-s1"></a>
## S1 — Q01: What may adapt and what stays fixed

**I / S-R01.** An adaptation surface is a bounded, typed choice inside a previously authorized envelope. A proposal may choose no change or abstain. Being available, installed, documented, authenticated and eligible are separate facts.

| Surface | Potentially adaptable proposal | Immutable boundary / application point |
|---|---|---|
| Route/provider/model | Rank exact eligible route descriptors for this task class; suggest an already permitted alternate | No new account, credential, model entitlement, pool, network destination or weaker control profile. Native and upstream loop owners remain explicit. Apply at new task/session or approved checkpoint handoff |
| Prompt/context shape | Select an approved template, order permitted evidence, tune optional context budget | Exact Owner directives, trust labels, task/gate identity, pending approvals, required evidence and privacy scope cannot be removed or rewritten. Template change is versioned, not arbitrary executable instructions |
| Tool/harness | Rank allowlisted equivalent tool/harness choices for the requested operation | Same effect class, recipient/data scope, required sandbox/launch boundary and current approval. An apparent equivalent with different side effects is a new admission question |
| Compaction/cache | Propose thresholds, approved transform and reuse strategy inside resource/fidelity bounds | One governor per route epoch; non-droppable references and source artifacts retained; no stale evidence for cache hits, cross-project hydration, automatic paid refresh or hidden helper inference |
| Fan-out | Propose fewer/more bounded workers for already authorized work | Existing parent reservation, fixed concurrency ceiling, review capacity, task ownership and stop scope; no new goals or autonomous executive |
| Retry | Select a lower retry limit/backoff or approved alternative for known-safe retries | Stable operation identity, one retry owner, reconciled effect state, deadline/attempt cap and idempotency. Ambiguous external effect is never a new reward opportunity |

Fixed objects include GoalSpec/plan amendments, grant lattice and fences, privacy/egress rules, trusted-launch guarantees, effect classifications, acceptance rubric/verifier requirements, pricing/debit observation semantics, retention consent, legal/entitlement gates, hard resource ceilings and who can promote. They may change only by their separate authorized processes. Learner feature extraction cannot be used to infer new consent. Prompt or tool adaptation is represented in the same proposal envelope as routing; “routing only” means no direct effect/control mutation, not that context policy escapes review.

<a id="rs-s2"></a>
## S2 — Q02: Outcome and counter contract

**I / S-R02.** Preserve the existing attribution/quantity ledger and financial/capacity ledger. Add an append-only outcome join, never a second authoritative cost table. Each record binds project/goal/task/assigned episode, parent/child lineage, route descriptor/build/model/settings, policy/config/context/authority epochs separately, attempt/operation IDs, source event identity, event time, observation time, capture window, unit, cumulative-or-delta semantics, counter reset epoch, value or null, availability reason, uncertainty/bounds, collector qualification and evidence reference.

| Signal | Definition and denominator | Qualifier / forbidden shortcut |
|---|---|---|
| Accepted completion | Independently accepted frozen goal outcomes / all assigned episodes, at declared horizon | Self-report, process exit and partial subtask count are not acceptance |
| First-review acceptance | First complete submitted candidate accepted by independent frozen gate / all assigned episodes; also show conditional submitted-candidate rate | Unsubmitted, abandoned, rejected and pending episodes stay visible; no dropping hard tasks |
| False green | Independent reject among gate-positive candidates / all gate-positive candidates examined under the prespecified audit design | Audit missingness and sampling probability explicit; no audited positives means unknown rate, not zero |
| Human correction/rework | Interventions, defect severity, repair attempts and person-minutes, all episodes | Review, reconstruction, reverted work and off-platform corrections included where observable; uncovered labor unknown |
| Tokens/helpers/retries | Endpoint-native input/output/cache/reasoning units and attempts, all roles | Existing inclusion algebra, deduplication and reset rules apply; no adding subsets twice or discarding failed calls |
| Latency/responsiveness | Admission/control/queue/round-trip/review/end-to-end durations and tail distributions | Observed clock domain, censoring, machine/load context; client RTT is not inferred provider inference time |
| Quota debit | Native bucket/window attributable debit or interval; window-level when task attribution is unidentified | Rounding, concurrent clients, resets, delayed updates and missing reports retained; tokens are not allowance |
| Monetary cost | Authoritative settled amount and currency; modeled price estimates separately | Fixed plan fees, actual metered charges and inferred price-sheet cost never collapsed |
| Review burden | Active reviewer minutes, queue age, incomplete review debt, dispute resolution | No cheap “success” by postponing review beyond the measurement horizon |
| Continuity/recoverability | Preserved control references, canonical parity, no duplicated unresolved effect, useful recovery and final acceptance | Resumed process, new session or clean replay alone is insufficient productive continuity |

Every registered episode exists **before selection/dispatch**. Record offered candidates, kernel-eligible set, policy-selected proposal, actual admitted action and reasons for any replacement/refusal. For randomized policies retain the **actual probability after eligibility filtering and fallback**, not a model confidence or pre-filter score. Bind any seed only as an audit aid, never as a substitute for probabilities. If a human override changes the action, retain both and mark the resulting off-policy identifiability limit.

Outcome maturity is `pending → provisional → mature`, with a separate `censored`, `disputed` or `unobserved` state and append-only corrections. Freeze horizons for first review, final acceptance, escaped defects and financial settlement separately. A fast proxy may inform a candidate forecast but cannot close a pending independent outcome. Late defects/debit corrections refer back to original episode/policy IDs, revise projections and trigger promotion reassessment; they do not overwrite the original verdict or history.

Report coverage by action, task difficulty/risk, route, outcome delay and policy arm. Missingness can be policy-dependent. The learner cannot optimize away required observers, stop expensive measurement on bad outcomes or label refusal as accepted completion. Correct refusal can satisfy a separately defined refusal task, but does not complete the original blocked goal. Costs of learning, shadow scoring, evaluation, promotion, rollback and human review remain charged to the experiment/parent workflow.

<a id="rs-s3"></a>
## S3 — Q03: Objective, baseline and genuine alternatives

**I / S-R03.** Apply correctness, authorization, privacy, recoverability, resource and acceptance floors first. Within feasible candidates, preserve the accepted order: responsiveness, then subscription efficiency, then completion, with the entire outcome vector visible. Do not invent weights translating human minutes, tokens, money and plan allowance into a universal reward. A material cross-metric trade-off goes to the Owner with its evidence. D-024's headline requires verified useful continuity and human-effort advantage against a strong baseline; a cost-only result is a narrower claim.

| Candidate class | What it can plausibly offer | Hidden cost and failure | Discriminating comparison |
|---|---|---|---|
| Conservative frozen static policy | Transparent, stable choice and zero learner overhead | May miss changing task/route fit; still requires independent qualification | Mandatory baseline with normal native features, same envelope and task mix |
| Human-revised decision rules/table | Explicit exceptions, small reviewable rule set | Maintenance delay, brittle interactions, human tuning time and implicit selection bias | Same update opportunities and full maintenance cost as learned policy |
| Offline learned ranking/template policy | Candidate patterns from mature qualified logs | Support gaps, train/eval leakage, stale patterns, training/inference/review overhead | Held-out future task families and full-workflow totals; unknown support abstains |
| Contextual bandit / online update | Sequential adaptation and explicit exploration trade-off | Nonstationarity, delayed outcomes, exploration regret, correlated samples, operational exposure | Separate sequence-level arms with frozen algorithm/update rules and hard external limits |
| Search/auto-tuning over configurations | Bounded search of approved policy packages | Many comparisons, early-stop selection of short-term proxies, candidate-generation cost | Compare fixed grid/random/manual search at equal authorized budget and final full-horizon evaluation |

These are alternatives to investigate, not a component selection. S-S03/S-S04 motivate conservative comparison but cannot replace per-effect hard gates. S-S10 motivates measuring all search expense; quick wins in proxy fidelity cannot justify eliminating a slow arm that would succeed by the final acceptance horizon.

<a id="rs-s4"></a>
## S4 — Q04: Candidate feedback architecture and authority separation

**I / S-R01.** Six logical objects fit inside existing canonical ownership:

1. **Observation envelope:** qualified immutable source receipts and explicit missingness, produced by authorized collectors
2. **Outcome episode:** append-only joins between assignment, actual action, mature independent outcomes and the existing two ledgers
3. **Policy artifact:** parent policy, complete content identity, approved feature/action schema, training data manifests and privacy scope, algorithm/config identity, uncertainty/support map, dependencies and expiry, static fallback identity
4. **Experiment permit:** allowed candidate space, data scope, assigned population, synthetic/non-live restriction, budget vector, horizons, stop/rollback rule, reviewer and promotion authority; issued outside the learner
5. **Promotion receipt:** independent review evidence plus Owner/explicitly delegated authorization bound to exact artifact, scope, stage, expiry and application boundary
6. **Decision receipt:** eligible candidates, chosen proposal/rejection, observed feature versions, binding policy, deterministic reason codes, separate grant/config/route/context epochs, reservation and actual admission outcome

Flow: authorized observations → scoped materialized training view → candidate artifact → independent evidence checks → authorized stage transition → immutable effective-policy pointer → proposal → **fresh kernel admission** → operation → qualified feedback. The learner cannot write grants, effective configuration, ledger settlements, independent labels or canonical events directly. It submits typed proposals through the same writer/admission path as other optional components.

Eligibility is computed before scoring for disclosure minimization and again immediately before dispatch. The permitted action set is an intersection, never a union: current grants, goal/plan, route controls, privacy, egress, entitlement/terms, hard caps, plugin capabilities and fence state. Stale rank inputs cannot recover a revoked route. `selected ≠ authorized`, `approved policy ≠ approved effect`, and `observed saving ≠ new budget`. The caller-not-provider-proxy boundary survives every route choice. A policy artifact containing unknown fields, executable commands, arbitrary URLs or modified acceptance predicates is rejected, not best-effort coerced.

<a id="rs-s5"></a>
## S5 — Q05: Offline, passive-online and exploratory-online are distinct

**I / S-R04.** Offline adaptation reads a sealed qualified dataset, produces a candidate and evaluates it before promotion. It performs no live action or hidden outcome collection. Passive-online observation can queue new evidence during authorized work, but the active policy stays frozen until the same promotion rules permit a new revision. Exploratory-online learning both chooses uncertain alternatives and updates from subsequent feedback; its update rule, scope and resource exposure must be explicitly permitted in advance. This lane allows only synthetic/provider-free fixture specifications, not live execution of any mode.

Offline competitor: independently reviewed human rules or static policy under the same gates and data scope. Hidden costs: extraction, labeling, support diagnostics, training, storage, private-data retention and independent review. Falsifier: a held-out gain disappears after selection/counter corrections or does not beat the static practical threshold after total overhead. Non-proof: useful logged predictions do not establish causal benefit for unchosen routes.

Online competitor: periodic offline updates with a frozen policy between promotions, under identical scope, ceilings, mature-outcome requirements and independent approval. Hidden costs: exploration loss, delayed feedback backlog, sequential inference complexity, and instability/operator burden. Falsifier: the externally enforced exposure cap fails, the mature outcome vector regresses, or update cost erases benefit. Non-proof: bounded synthetic exposure is not a provider-side quota or live-quality guarantee.

### Off-policy identification, selection and censoring

Use logged-policy evaluation only on a frozen target population with the relevant action support and valid conditional assignment information. A deterministic historical policy that always chose A supplies no direct evidence of B's counterfactual outcome in that context. Zero/unknown propensity is an explicit `NOT_IDENTIFIABLE` cell; assigning a made-up small probability or a learned confidence score is prohibited. A direct outcome model may extrapolate, but its output stays modeled and cannot close that evidence gap.

Candidate estimators include direct prediction, replay, inverse-propensity weighting, and doubly robust estimation. Choose none here. A later preregistration must state assumptions, target policy, support, propensity provenance, dependence, clipping/truncation bias, effective sample size, weight tails and uncertainty method. Cross-fitting must respect project/task-family/time boundaries. Stable feature availability before action is required; post-outcome review data cannot leak into selection-time features.

Selection can occur before logging, during route availability, at human override, at early trial termination and at reviewer sampling. Preserve the assigned population and every filter. Shared quota/window, task lineage, policy state and reviewer availability create interference; treat a whole adaptive sequence or independent state replica as the unit, not each turn. Pending acceptance is not failure and not success; prespecify horizon-based outcomes and separately report censoring. If censoring plausibly depends on policy/outcome, use prespecified sensitivity bounds or declare non-identification. No automatic missing-at-random assumption is adopted.

<a id="rs-s6"></a>
## S6 — Q06: Exploration costs and caps

**I / S-R05.** Exploration is spending scarce evidence-gathering opportunity on an uncertain allowed policy choice. It is not required to gather any particular live action: lack of safe informative support may simply make online learning inadmissible. No exploratory live, irreversible or human-gated action is admitted. A shadow score cannot quietly execute a second tool, send the same private prompt to another route or create a helper-model call.

The permit binds separate hard limits for total synthetic episodes, additional inference/tool attempts, native quota, money, elapsed/active time, host resources, reviewer minutes, concurrency and deadline. Applicable dimensions use native units. Cumulative experiment cost includes baseline plus challenger, failures, warmup, shadow/learning work, review, rollback and delayed liabilities. Extra-versus-baseline cost may be estimated separately, but admission cannot rely on a favorable counterfactual saving.

Before each admitted trial, require for every bounded dimension:

`settled debit + outstanding reservations + conservative bound for next work + protected recovery reserve ≤ approved cap`

The reservation terms are disjoint: outstanding reservations include all admitted unsettled work, including uncertain liabilities and already admitted recovery work. Protected recovery reserve means separately withheld, still-unallocated recovery headroom; it is not already counted in outstanding reservations. Admitting recovery atomically transfers the relevant amount from withheld headroom into an outstanding reservation, rather than charging both. If a shared ledger instead tags recovery inside total reservations, use that total once and omit a separate additive reserve term. This is a design predicate, not an executed calculation or proven provider bound. Atomic reservation ownership spans fork/retry/child lineage; resetting a provider window or rolling back a policy does not reset spent experiment allowance. Reconcile late receipts with the original reservation exactly once. Unknown upper cost means **deny the trial** when a hard bound is required; a time/token proxy cannot certify a strict native-quota cap. An externally enforced trustworthy maximum may bound exposure even while final debit is pending, but its availability is U for actual routes. No such mechanism was exercised here.

At cap, expiry, excessive pending liabilities or lost required observation: stop new exploration and promotion; preserve receipts; reconcile outstanding work. Do not refresh credentials, create an account, buy quota, change provider, lower review or borrow protected recovery budget. An attractive reward does not alter these rules.

<a id="rs-s7"></a>
## S7 — Q07: Promotion is an independently approved state machine

**I / S-R06.** Proposed states are `candidate → evidence_sealed → independently_reviewed → stage_authorized → effective`, with `rejected`, `expired`, `quarantined` and `superseded` branches. Each transition is idempotent and binds immutable artifact/evidence identities plus the current writer, configuration and authority revisions. Atomic compare-and-set of the effective pointer prevents racing promotions; a stale receipt cannot win after revocation or Stop.

1. **Candidate/schema screen:** permitted surfaces only, scoped data lineage, support/uncertainty, static fallback and expiry present
2. **Offline evidence gate:** frozen baseline, all-attempt ledgers, hard-floor fixtures, held-out task families/time, mature outcomes and valid identification
3. **Read-only shadow stage:** score authorized sanitized observations without affecting selection. Measure decision latency, abstention, disagreement and overhead. No counterfactual quality claim when the proposed action was not taken
4. **Synthetic canary/limited assignment:** separately authorized small cohort, rollback and independent witness. “Small” and duration are bounded in the permit; this report sets no production percentage
5. **Confirmatory A/B or equivalent justified design:** freeze policy state or randomize independent update sequences; hold acceptance/judge fixed; account for shared pools and all search/exploration costs
6. **Human-authorized effective policy:** independent verifier evidence plus Lucas's approval of exact artifact/scope, or a separately explicit bounded delegation whose receipt is current. Self-issued PASS is insufficient

Automatic rollback may execute an already authorized rollback rule; it cannot become automatic expansion of scope. Future promotion authority must be explicit, risk-bounded and outside the learner. No approval, signature or numerical score makes a real route qualified. Reusing a prior trial's authorization for a changed prompt, data scope, judge, model/build or budget is rejected.

<a id="rs-s8"></a>
## S8 — Q08: Stop, checkpoint, interrupt, drain and rollback

**I / S-R07**, aligned to the accepted D-022 semantics:

| Mode/operation | Experiment and pending update | What can honestly be reported |
|---|---|---|
| Aggressive Stop | Fence selected learner/experiment actor's new dispatch and promotion; interrupt without waiting. Revoke its unapplied proposals. Descendants are identified separately | Request, local interruption and any unresolved work separately. It does not silently stop every child |
| Full Stop | Fence selected scope plus owned evaluator/worker/shell/monitor/relauncher set; cancel pending scoped updates; collect local and separate remote receipts | Settled owned components versus unresolved/offline components; no quiescence claim without witness |
| Lazy Stop | Close new admission and promotion; stop at the declared observable current operation boundary/checkpoint with a deadline and authorized escalation rule | Named boundary and whether it was reached; not “finished thinking” |
| checkpoint | Persist policy/data cursor, outstanding trials/reservations, immature outcomes, current canonical references and proposed update status | A recoverable reference set, not effect settlement or permission renewal |
| interrupt | Deliver scoped cancellation/control and record adapter acknowledgment | Acknowledgment does not imply external rollback |
| drain | Admit no new work; settle or explicitly classify existing work and liabilities | Drained only when declared owned scope is settled; otherwise pending/unresolved |

A stopped experiment cannot publish a late promotion. If an experiment temporarily changed the effective policy, the **preauthorized rollback transaction** installs the last admissible baseline/previous artifact for future eligible boundaries, with a new monotonic policy revision and receipt. If no rollback authority was granted, Stop blocks continued experiment use and requests the authorized controller's decision; the learner does not grant itself write power. A previous artifact is revalidated against current grants, route availability and floors; if invalid, remain blocked rather than resurrect old authority.

`staged` means validated artifact awaiting authorization/application. `applied` requires a durable effective-pointer transaction and target-boundary adoption receipt. Offline targets remain pending. `reverted` means a new effective revision removed the candidate for the declared scope and boundaries, retaining history. It never means erased usage, undone external actions, restored prior permissions or deleted unfavorable observations. In-flight tasks retain their bound policy until a valid safe-boundary handoff or a safety fence blocks further effects. S-F09 exercises all modes and late results without conflating their scope.

<a id="rs-s9"></a>
## S9 — Q09: Drift and non-stationarity

**I / S-R08.** Separate **identity drift** from statistical suspicion. Changes in route build/model/settings, tool schema, prompt/template, context governor, acceptance rubric, counter semantics, pricing/debit window, trust boundary or permitted data scope invalidate affected compatibility keys immediately. A deprecated route cannot remain eligible because historical reward was high. Outage/error signals can shrink admissible choices but cannot authorize an unqualified fallback.

Task mix, reviewer mix, missingness, label delay and resource distributions need slice-level monitoring against frozen baselines and absolute guardrails. A “stable average” can conceal failure in rare critical tasks. Candidate drift detectors include deterministic schema/version checks, windowed distributions, change-point tests and independent spot-audits; compare them against simple expiry plus periodic review. No detector is selected and no delay/detection guarantee is asserted.

Drift response is freeze updates/promotions, invalidate affected evidence eligibility, fall back only to a currently admissible static policy, and request bounded revalidation. Preserve the original learned artifact, data manifests and adverse observations. Distinguish `known_changed`, `suspected_shift`, `insufficient_observation` and `no_detected_shift`; the last is not evidence of stationarity. Re-learning cannot proceed by silently enlarging source/cadence/budget allowances from R-R.

<a id="rs-s10"></a>
## S10 — Q10: Explicit staleness windows and expiry

**I / S-R08.** Every policy must contain adopted finite freshness parameters or be ineligible for effective use. Missing freshness configuration is not an infinite default. The candidate derives:

`valid_until = earliest(policy approval expiry, required route/control expiry, evidence_cutoff + adopted maximum evidence age, data-use consent expiry, counter-schema qualification expiry)`

Also enforce maximum mature-episode count since validation and dependency/event invalidation. Wall-clock age and sample count are separate: a million old similar episodes do not refresh a new rare task class. Replay uses the original validity decision for historical explanation but current time/epochs for new admissions.

| Window | Start, expiry and enforcement | Unknown/next decision |
|---|---|---|
| Admission freshness | Re-read current grants, pause/writer/route state at each effect; never cached beyond revocation | Concrete adapter enforcement remains to qualify |
| Availability/quota observation | Meter timestamp/window plus adopted maximum age and known reset; unknown or stale signal cannot authorize expansion | Numeric age depends on actual meter cadence/lag, U until qualified |
| Quality/policy evidence | Last independent mature evaluation cutoff plus adopted age and episode-count limit, scoped to task family | Owner and verifier choose age/count with drift risk and observable latency; no universal daily/monthly value assumed |
| Outcome maturity | Separate first-review, final/escaped-defect and settlement horizons fixed before assignment | Numeric horizons and delayed-outcome distributions U |
| Shadow/canary permit | Absolute expiry plus trial/exposure cap; no self-extension for incomplete results | If enough evidence cannot mature within permit, return inconclusive |
| Security/privacy/acceptance dependency | Immediate invalidation on relevant revision/revocation, regardless of timer | Never replaced by statistical grace period |

Synthetic fixtures use explicit example clocks/horizons solely to check expiry logic; they are not production defaults. The strongest safe behavior before adopted values exist is static-only/no learned promotion. This closes the design question while leaving calibration honestly blocked.

<a id="rs-s11"></a>
## S11 — Q11: Productive continuity and lossless rollback

**I / S-R07.** Bind each admitted execution segment to policy, route, context, goal/plan, effective configuration and authority identities. A rank update does not change an already authorized operation's destination, data, current context or approval. New policy application occurs at a permitted new-segment/checkpoint boundary after admission and continuity validation. Revocation still fences immediately; “finish the old policy” cannot override a narrowed grant.

For a handoff, preserve exact directives, source/candidate/evidence references, unresolved operations, pending interactions, ownership, budget reservations, independent verdicts and rollback lineage. A provider session is acceleration state, not canonical recovery authority. Compaction proposes artifacts; the sole governor commits a fidelity-checked transition. Rejected compactors and rehydration cost remain in the episode. Upstream-only work acquires no covert native helper model.

Rollback appends a supersession event and changes future effective selection; it does not rewrite prior decision receipts, counters, data splits or task assignment. Recovery loads the last valid pointer under the current fence and revalidates all dependencies. A fork shares historical evidence references only within scope; it gets distinct policy lineage and nonduplicated reservation ownership, not copied active grants. When a baseline is also invalid, a typed block is safer than a fabricated recovery success.

Hold out future task families and projects to test generalization without pooling private training data. Project-specific advantage stays project-specific. The D-024 six journeys remain acceptance targets; this report's synthetic continuity examples cannot establish real cross-harness productive work or human-effort superiority.

<a id="rs-s12"></a>
## S12 — Q12: Privacy and training scope

**I / S-R09.** Default policy and feedback stores are partitioned by user/project/goal privacy domain. Scope is checked **before** feature extraction, join, retrieval, training, scoring, explanation and export. Features must be allowlisted metadata necessary for the permitted decision; raw prompts, outputs, source snippets, private paths, credentials and account identifiers do not enter general metrics or shared training tables. Identifiers/hashes, rare task labels, timing and membership can disclose information even without text.

Cross-project learning is disabled unless explicit authorization names contributing data categories/domains, receiving policy/application scope, permitted recipients, retention and withdrawal behavior. Permission to run a task or show its result is not consent to train a shared policy. An aggregate model can leak membership or memorized content; minimum cohort size or removing names is not a proof. Differential privacy or federated learning would be separate candidates with explicit threat, utility, composition and access-budget evaluation, not a magic exemption or selected implementation.

Derived artifacts carry transitive data lineage and taint scope. Withdrawal/retention expiry blocks new use and invalidates affected policies; rebuild from admissible data or remain static. Preserve only authorized minimal audit tombstones/receipts, not an indefinite shadow copy of deleted private material. No machine-unlearning guarantee is claimed. Exporting a policy is data sharing and must respect the most restrictive training/input scope and explicit recipient permission. Candidate promotion cannot launder a private project feature into a public/global default.

<a id="rs-s13"></a>
## S13 — Q13: Hard floors cannot become reward terms

**I / S-R01/S-R05.** Evaluate hard predicates outside the learner, before scoring where possible and at effect admission. A reward of any magnitude cannot compensate for a failed predicate.

| Floor | Enforcement and failure disposition |
|---|---|
| Authority/security | Current grants, scope, effect identity, fence, launcher and adapter controls; any valid widening/stale effect counterexample rejects and quarantines affected policy |
| Privacy/egress | Permitted sources/features/recipients, scopes and export boundaries; one unauthorized disclosure stops affected work |
| Correctness/acceptance | Frozen per-task evidence and independent gate; ordinary task failure remains an outcome. Critical safety/canonical/acceptance-bypass failure is an immediate stop, not averaged away |
| Quality floor | Predeclared task-class/risk acceptance minimum and non-inferiority requirements; one rare critical slice cannot be offset by easy cases |
| Cost/quota/latency/resources | Existing hard ceilings plus independently reserved worst-case exposure; forecasts are not guarantees. If a strict cap cannot be enforced/identified, do not admit that trial |
| Recoverability/continuity | Exact mandatory references, current epoch, no duplicate ambiguous effects, canonical evidence retained; failure stops promotion even if speed improves |
| Control availability | Stop/admission fencing and evidence retention remain usable under learner failure or overload; optional scoring timeout falls back only within current bounds |
| Honest evidence | No missing-as-zero, mislabeled proxy, fabricated propensity, leaked evaluator data or self-acceptance; invalid evidence is not a passing floor |

Statistical quality floors and absolute safety invariants are different. Zero observed violations does not establish zero risk; finite-sample uncertainty is reported. A chance-constrained or baseline-relative optimizer cannot spend a privacy “error budget.” Human approval of a policy is necessary where required, but does not validate unsupported measurements or waive immutable floors.

<a id="rs-s14"></a>
## S14 — Q14: Reward-hacking attack and detection matrix

**I / S-R10.** Separate independent outcomes from optimization proxies. The feedback producer cannot change task denominators, acceptance criteria, evaluator identity, censoring rules, counter completeness or evidence retention.

| Attack | Detection/refusal candidate | Retained adverse evidence |
|---|---|---|
| Optimize first-review acceptance by submitting only easy cases | Assignment-before-selection ledger; submitted/assigned/mature/censored counts and risk/difficulty slices | Every suppressed/abandoned/pending episode and its resources |
| Choose a lenient judge or pass one's own output | Gate/judge identity bound outside policy; blinded independent adjudication and disagreement audit | Original judge result plus independent reversal, never overwritten |
| Split tasks or shrink scope to inflate completion | Frozen GoalSpec and parent outcome IDs; child completion cannot satisfy missing parent criteria | Full assigned-goal result, partial work and plan change history |
| Hide repair/retry/helper costs | Attempt-before-dispatch, full lineage and two-ledger reconciliation; uncovered role is unknown | Failed/crashed/threshold-crossing calls, rework and late liabilities |
| Stop before delayed defects/billing arrive | Maturity watermark and prespecified horizons; no promotion from immature-only cohort | Censoring reasons, late defects and reconciled amendments |
| Improve token/cache proxy while degrading semantics | Independent exact-reference/fidelity and task-quality checks; no-future-work/cold/loss controls | Lost intent, rehydration misses, review burden and total resource vector |
| Reward “safe refusal” by refusing all difficult tasks | Correct-refusal outcomes separate from original accepted completion; coverage and usefulness floors | Denied work and unmet original goal |
| Manipulate task classification or unavailable counters | Immutable pre-action classifier/version; audit feature shifts and unknown-rate differences | Disputed class, eligible-set changes and observation gaps |
| Poison feedback with tool text or synthetic verdicts | Typed trusted event provenance; low-trust strings cannot set outcome/approval fields | Rejected forged label and original source classification |
| Overfit held-out checks or stop on favorable interim view | Sealed evaluation bank, access log, candidate-count/multiplicity record and registered look schedule | Leaked/consulted tasks invalidated for confirmation, original failed analyses retained |

No tripwire establishes immunity. Silent channels, unobserved human labor, delayed harms, correlated judges and novel proxy failures remain U. Adversarial tests should include an attractive proxy score alongside a known unacceptable end state; an evaluator that rewards that case fails sensitivity before testing a learner.

<a id="rs-s15"></a>
## S15 — Q15: Honest-reward methods and their falsifiers

**I / S-R10/S-R11.** Each row is a candidate method; its benefit and limitations must be evaluated independently.

| Method | Competing option | Decisive falsifier / non-proof |
|---|---|---|
| Held-out task-family/time bank, sealed before tuning | Independently refreshed confirmatory bank inaccessible to the tuner, with a separate reusable regression bank | Discovery of shared task/solution/label lineage or feedback-informed selection invalidates independence. A clean split does not establish new-domain fit |
| Independently authored semantic-mutant acceptance/authority/ledger corpus | Property-based or metamorphic generation with the same required negative coverage; happy-path-only cases are a sensitivity negative control | Seeded critical corruption passes or expected refusal fails. Passing known probes does not cover unknown attacks |
| Blinded human spot checks with known selection probability | Full independent human review of the registered cohort under the same frozen acceptance gate | Independent reversal exceeds registered false-green/quality boundary, or biased sampling prevents population inference. Human review is fallible and costly |
| Shift/missingness/label-lag monitoring | Fixed expiry plus periodic manual review | Seeded dependency change not invalidated, or poor critical-slice outcome hidden by aggregates. No alert does not prove stationarity |
| Logged-policy/off-policy evaluation | Independent prospective assignment on safe synthetic tasks | Zero/unknown support, wrong actual propensity, unsupported dependence, excessive weight concentration, or sensitivity bounds change decision. A fitted estimate is not an observed counterfactual |
| Outcome/cost audit through original episode lineage | Independently reconciled periodic complete-cohort snapshots, retaining original receipts and all assigned attempts | Dropped assignment, double charge, erased repair, unknown converted to zero, late liability omitted. Ledger integrity does not prove provider completeness |
| Preregistered fixed-horizon analysis | Preregistered valid sequential analysis under the same endpoints, floors and exposure ceilings | Analysis differs from frozen stopping/multiplicity rules or method assumptions fail. Statistical validity does not establish causal comparability |

Candidate generation, tuning, calibration, threshold choice, confirmation and regression monitoring require separately identified data uses. Policy candidates that saw confirmatory results consume that evaluation opportunity; re-labeling the same bank “fresh” is forbidden. Holdouts belong to the independent evaluator, not learner-accessible prompts/tools. A changing learned policy must be evaluated as a **sequence-level procedure**, or frozen for the comparison; ordinary stationary per-call confidence claims do not follow from adaptive data.

<a id="rs-s16"></a>
## S16 — Q16: Zero-token explanation and reversible observation

**I / S-R06/S-R07.** Deterministic operator projections answer: what was requested, which options were eligible, what policy/version proposed, what evidence and uncertainty supported it, what was rejected by hard gates, what actually ran, which budget was reserved, when the policy expires and what rollback would affect. Use bounded stored reason codes and qualified scalar/vector fields; do not invoke a model to reconstruct an explanation.

A decision record distinguishes predicted outcome, observed outcome, current maturity and later correction. It displays route/config/policy/authority identities separately, dependency freshness, required unknowns and why fallback or abstention occurred. Numeric scores can explain a ranking but are not calibrated probabilities unless validated. No hidden chain-of-thought is requested or stored. Reproducing a stored decision uses pinned policy/features and an independently checked decoder; it need not rerun a model or repeat an external effect.

Operator views expose learner off/on, candidate/stage/effective states, pending promotion/rollback, scope/exposure, outstanding liabilities, review debt and stale/invalidated evidence. “Rollback complete” requires the receipts from S8; a button click or process exit is insufficient. Observability remains available when the learner crashes or is disabled. Display data follows the caller's privacy scope and does not publish training membership through arbitrary explain queries.

<a id="rs-s17"></a>
## S17 — Q17: Off-by-default inertness

**I / S-R12.** An absent or installed-disabled learner is not imported, initialized, scheduled, queried or subscribed. It performs zero attribution to adaptation of measurement calls, model/provider/tool calls, writes (policy/training/checkpoint/analytics), network attempts, processes/threads, timers/watchers, retries, quota reservations, egress or dynamic feature/context enumeration. No “helpful shadow scorer” remains running. Enabling adaptation requires an explicit permit/configuration transition.

The inertness predicate over a declared observation interval is:

`adaptation_enabled = false AND all independently witnessed adaptation-attributable activation/call/write/egress/reservation counts = 0 AND effective selection equals the approved static path AND Stop/status/replay remain available`

This does not promise literally zero global disk or metadata overhead. The core may read bounded inert manifest metadata needed to explain that the plugin is absent/disabled. Ordinary mandatory canonical evidence and safety/accounting for already authorized work remain part of the baseline; disabled adaptation cannot suppress them. Conversely, additional measurement undertaken solely for adaptation must cease.

A transition from enabled to off first fences future work, settles/stops owned activity and records the core-owned transition receipt. The quiescent disabled interval begins after that bounded transition; residual unresolved remote work is shown as such, never hidden in a zero claim. Retained policy/evidence artifacts are inert data subject to authorized retention. Malformed configuration, missing dependency, restart, task completion, late outcomes and UI attachment cannot self-enable the learner.

Test absent, installed-disabled, formerly-enabled-then-disabled and enabled-positive-control states. An independent observer needs sensitivity controls for imports, callbacks, file activity, IPC/network, spawning and reservations. A zero-filled fixture response is not measurement. Counts equal zero only within the declared instrumentation scope; unobserved channels yield U, not PASS.

<a id="rs-s18"></a>
## S18 — Q18: Preregistered no-benefit falsifier and margins

**I / S-R11.** No numerical production acceptance margin, practical-benefit threshold, exposure cap, horizon, confidence level or sample size is adopted by the source pin for this lane. Inventing one would silently decide risk and evidence requirements. `decision-contract.json` therefore requires explicit Owner/verifier-adopted values; missing entries make execution/promotion **BLOCKED**, not zero-tolerance by accident. Synthetic classifier examples use illustrative values only.

Before running, freeze target task families/risk slices, static and human-rule baselines, policy/update identity, independent assignment unit, source/build/control profiles, privacy scope, full overhead boundary, maturity horizons, primary metric vector, analysis/multiplicity/stopping rules and independent verifier. Adaptive state, shared quota windows and repeated related tasks require sequence/cluster-level design. Do not count helpers/turns/repeats as independent tasks. A pilot, if separately authorized, estimates variance/missingness and feasibility without selecting a confirmatory margin to fit observed gains.

Define `D_k = adapted burden − static burden` for each burden metric and `D_q = adapted quality − static quality`. Let `[L,U]` be the registered uncertainty interval using the correct dependence and look scheme. Required adoption fields include quality non-inferiority margin `δq ≥ 0`, burden practical improvement `b_k > 0`, burden non-inferiority tolerances `δk ≥ 0`, false-green and continuity margins, absolute floors and adverse reversal thresholds `r_k`. Critical authority/privacy/canonical/effect invariants retain zero permitted violations regardless of statistical margin.

- **Quality non-inferiority:** `L(D_q) > −δq` in every required quality/risk slice, plus the absolute acceptance floor. The margin must be justified by task consequence, independent of results
- **Burden non-inferiority:** `U(D_k) < δk` for every declared protected burden metric; equality/boundary contact is inconclusive under this conservative candidate rule
- **Meaningful benefit:** all hard floors, all required non-inferiority conditions and mature evidence pass, and `U(D_primary) < −b_primary` for the registered burden claim; other accepted-objective trade-offs need explicit Owner adjudication
- **Decisive no-practical-benefit:** a valid equivalence interval sits entirely inside the preregistered practical-equivalence band, or the interval excludes the necessary favorable threshold, under the frozen claim definition. This rejects the scoped improvement proposition
- **No established benefit:** superiority criterion not met but equivalence/harm not identified. Keep static policy; do not call this proof that all adaptation is useless
- **Inconclusive/not identifiable:** inadequate precision, unsupported actions, unbounded missing debit, unresolved dependent assignment or pending key outcomes. No promotion/claim

For example, when a registered claim requires a burden reduction of at least `b`, a valid lower bound greater than `−b` rules out that required magnitude; it need not show equality. The stronger statement of practical equivalence requires its own two-sided registered band and sufficient precision. D-024's broad continuity claim additionally requires preregistered verified-outcome and human-effort superiority; quality non-inferiority plus cheaper tokens alone does not meet it. No published bandit or router result fills these local cells.

<a id="rs-s19"></a>
## S19 — Q19: Regression, reversal and failed evidence

**I / S-R11.** There are three different reversal classes:

1. **Immediate safety/control reversal:** one independently witnessed authority/privacy/evidence-integrity breach, unsupported effect, failed Stop or corrupted canonical continuity stops affected admissions and invokes the preauthorized fallback/quarantine path. No statistical average is consulted
2. **Budget/operational reversal:** observed hard ceiling breach, insufficient safe reservation, lost required meter/witness, expired identity or unbounded pending liability freezes affected work. An unknown counter is an evidence block, not automatically evidence that cost increased
3. **Performance reversal:** for a burden, `L(D_k) > r_k` establishes registered adverse increase; for a quality/continuity benefit, `U(D_q) < −r_q` establishes registered adverse loss. False-green increase and review/rework debt have separately adopted thresholds. Use only valid prespecified looks or the declared sequential procedure

An absolute quality/resource floor failure can reverse preference even while comparative intervals are inconclusive. A precise practical no-benefit result reverses the case for enabling adaptation when static has lower complexity/overhead; it is not an authority failure. Investigate causal attribution, but stop the harmful exposure first under the permit. If canary and control both fail because of a shared dependency, neither is certified safe by their similarity.

Preserve every adverse result, repair identity and original preregistration. A bug fix/new policy gets a new artifact and relevant floor/held-out evaluation, not a replacement success for the same trial. Statistical rollback can protect future work; it does not guarantee recovered spent quota, elapsed time, private disclosure or external effects. Exact numeric reversal values remain Owner/verifier inputs; no operational threshold was tested here.

<a id="rs-s20"></a>
## S20 — Q20: Provider-free fixture suite

**I / U. All S-F01–S-F18 are UNEXECUTED specifications.** `fixtures.json` provides inputs, prerequisites, independent oracle, exact pass/fail predicates, evidence, stop conditions, competitor and non-proof per fixture. No runner entrypoint was verified; no runnable command is invented. A later separately authorized local implementation supplies reviewed source/runner identities and executes only synthetic inputs with provider/account/network denial tripwires. Do not execute repository scripts to make this research appear measured.

| ID | Required accept/reject oracle |
|---|---|
| [S-F01](fixtures.json#/fixtures/0) Offline promotion | Accept only exact sealed artifact with current independent verdict and authorized promotion; reject self-PASS, missing/mutated evidence, changed scope, stale receipt, expired or unsupported action |
| [S-F02](fixtures.json#/fixtures/1) Exploration cap | Reserve before admission; at/over each native cap reject next trial; delayed costs, fork/retry and replay cannot duplicate or release the same reservation twice; unknown bound blocks |
| [S-F03](fixtures.json#/fixtures/2) Floor-violation refusal | A high-reward candidate violating each fixed grant/privacy/gate/budget/control predicate is rejected before effect; low-reward valid candidate remains eligible |
| [S-F04](fixtures.json#/fixtures/3) Reward-hacking tripwires | Reject false improvement created by dropping hard tasks, selecting lenient judges, shrinking goals, hiding rework or treating immature labels as success |
| [S-F05](fixtures.json#/fixtures/4) Non-stationarity invalidation | At required dependency/version/freshness change invalidate affected learned policy before the next effect; unaffected scopes remain separate; no silent unqualified fallback |
| [S-F06](fixtures.json#/fixtures/5) Rollback and crash | New monotonic rollback revision restores only currently admissible prior policy; canonical evidence and ledgers remain append-only; stale writer/late promotion cannot reactivate candidate |
| [S-F07](fixtures.json#/fixtures/6) Privacy isolation | Foreign project/user/goal training/score/explain/export attempts denied before fetch; derived policy cannot exceed contributing scopes; consent expiry invalidates use |
| [S-F08](fixtures.json#/fixtures/7) Disabled inertness soak | All adaptation-specific watched counts zero in each disabled state; static decisions equal baseline; positive controls prove observer sensitivity; missing coverage is inconclusive |
| [S-F09](fixtures.json#/fixtures/8) Stop semantics | Aggressive, Full and Lazy match declared scope/boundary; no late promotion; rollback reports future-pointer effect only; remote unresolved remains unknown |
| [S-F10](fixtures.json#/fixtures/9) Continuity/checkpoint | No mid-effect reroute/context replacement; preserved non-droppable refs, approvals, unresolved operations and reservation identity after permitted handoff |
| [S-F11](fixtures.json#/fixtures/10) Delayed/censored outcomes | Pending and unreviewed outcomes never become zero-cost success; late defect/cost amendments invalidate stale claims without erasing initial records |
| [S-F12](fixtures.json#/fixtures/11) Off-policy support | Zero/unknown propensity yields not-identifiable; actual post-filter action probabilities required; unsupported modeled extrapolation cannot become observed gain |
| [S-F13](fixtures.json#/fixtures/12) Evaluation leakage | Shared task/solution lineage, outcome-derived features, accessed holdout or unregistered repeated looks invalidate confirmation |
| [S-F14](fixtures.json#/fixtures/13) Counter reconciliation | Explicit zero survives; missing/stale/reset/replayed counters preserve null/reason and no double charge; helper/failure residuals cannot disappear |
| [S-F15](fixtures.json#/fixtures/14) Zero-token explain | Stored receipt reconstructs selected/rejected/currently-ineligible distinctions with no model/network call; no unauthorized membership disclosure |
| [S-F16](fixtures.json#/fixtures/15) Result classifier | Synthetic interval/floor cases map exactly to benefit, equivalence/no-benefit, regression, inconclusive or blocked; no aggregate gain rescues a floor failure |
| [S-F17](fixtures.json#/fixtures/16) Allocation/interference | Whole sequence/quota cluster identity prevents call-level pseudo-replication and shared-state leakage; changed allocation invalidates comparison |
| [S-F18](fixtures.json#/fixtures/17) Feedback provenance | Forged tool-text acceptance, modified propensity or learner-written reviewer identity cannot become trusted outcome or promotion authority |

Every fixture has a clean control and a single discriminating mutant/adversarial input. Failure to detect the intended mutation is a failed oracle-sensitivity claim even if an unrelated parser/type error occurred. Scope includes new-session, checkpoint, crash/restart, duplicate delivery, stale epoch, fork and late-result schedules where relevant. These are enumerated inputs for a future runner, not simulations performed here.

<a id="rs-s21"></a>
## S21 — Q21: Invariant proof obligations and local handoff

**I / S-R01/S-R07/S-R12.** A synthetic suite can establish bounded conformance against an independently specified oracle after execution. It cannot prove an unbounded system property merely by returning PASS. The exact obligations are:

- **No authority widening:** S-F01/F03/F18 mutate every proposed permission/privacy/acceptance field; accepted effect set must remain a subset of independently calculated current eligibility. Admission trace must show revalidation after concurrent revocation. Reward and learned score never enter the authority oracle
- **Inert disabled path:** S-F08/F15 use independently placed activation/call/write/egress/reservation witnesses with positive controls. Any forbidden attributable activity fails. Incomplete observer coverage cannot prove zero
- **Stop and revert:** S-F06/F09 order Stop before/after candidate creation, review, authorized staging, pointer commit, boundary adoption and late feedback. No new scoped experiment dispatch/promotion after fencing; authorized rollback creates a new revision without pretending to reverse outside effects
- **Canonical continuity:** S-F06/F10/F11/F14 compare immutable required-reference sets, episode lineage, event-prefix preservation and ledger conservation through rollback/checkpoint/replay. No deleted or rewritten historic receipt; separate epochs remain separate

**Prerequisites for a later local session:** Owner-approved synthetic fixture corpus and independent expected decisions; separately reviewed implementation/runner and exact build identities; disposable local test profile at the applicable native D-028 floor; explicit no-provider/no-account/no-credential networking constraints; independent file/process/IPC/network/reservation witnesses; frozen policy/static baseline, scope and resource/margin/horizon values; trusted clocks and fault schedule; private evidence destination; independent verifier. A Windows/Linux compatibility claim needs each exact profile; WSL remains development-only. No actual OS fault injection is authorized by this report.

Expected evidence: input/candidate/oracle/source hashes; exact profile and dependency manifests; expected versus actual typed decisions; append-only promotion/rollback/Stop receipts; original and amended outcome/ledger projections; full counter/coverage manifest; witness sensitivity results; fault cutpoint and observation gap records; all negative traces; independent verdict and residual unknowns. Public-source page hashes remain null where no complete original-byte capture was obtained; an artifact hash is not a source-page hash.

Stop dependent execution on non-synthetic data, unexpected provider/credential/network access, lost independent witness, exceeded envelope, stale-writer dispatch, canonical divergence, uncontrolled external effect or unavailable Stop. Preserve records and report scope. Ordinary intentional synthetic refusal is an expected outcome; a broken test rig is inconclusive, not a product PASS. No repair-and-rerun may erase the original adverse trace.

<a id="rs-s22"></a>
## S22 — Q22: Result classes, bounded unknowns and non-results

**D:** S-S01–S-S13 document the scoped prior-art facts in S0; shared canonical notes hold vendor/protocol facts. **L:** this report inspected pinned text/receipts and generated/checked its own artifacts. **I:** policy objects, lifecycle, safeguards, comparisons, predicates and decision rules are candidates. **U:** all learner performance, local policy safety, exploration bounds, drift detection quality, runtime inertness, actual counter completeness, numeric deployment thresholds and productive-continuity benefits.

No measured improvement, quota saving, correct router ranking, reward-hacking immunity, non-stationarity guarantee, live exploration safety, route qualification, subscription entitlement, license/legal clearance or universal portability is established. A native token counter is not an allowance receipt; a paper's emulated list-price saving is not a local outcome. D-031 prohibits marketing unsupported vendor intent. D-033's porting-cost hypothesis remains unmeasured.

The immediate blockers to deployment are concrete: qualify required counters/control boundaries; bind Owner/verifier margins, ceilings and finite freshness/maturity windows; implement and independently execute the synthetic gate suite; collect separately authorized mature evidence with adequate action support; then seek exact scoped promotion approval. None requires reopening accepted D-018–D-033 or choosing a new executive.

<a id="rs-s23"></a>
## S23 — Recommendation, competitor, falsifier and non-proof register

All design imperatives in S1–S22 are scoped by the rows below; none chooses a final technology or authorizes execution. Every competitor is constrained by the same current authority, budget, privacy, evidence and quality floors. Self-PASS, missing-as-zero, success-only accounting, unlogged updates, automatic privilege growth and hidden shadow activity are rejection controls, not admissible contenders. Where a contender needs future explicit consent or qualification, it remains blocked until that prerequisite is met.

| ID / recommendation | Real competitor | Decisive falsifier | Passing does not prove |
|---|---|---|---|
| S-R01 Typed proposals plus independent current admission | Frozen static or hand-maintained eligible-choice table using the same current admission path | Any learned input widens eligibility, changes gate/privacy, bypasses current fence or writes authority | Complete kernel/security correctness or all adapter mediation |
| S-R02 Append-only mature outcome joins on two ledgers | Periodic immutable complete-cohort projections from the same canonical ledgers, with full maturity/lineage retained | Dropped assigned case, null→zero, double charge, missing helper/correction, misclassified pending label | Complete provider accounting or true causal counterfactual |
| S-R03 Vector/floor comparisons against static and human rules | Owner-adopted ordered decision table over the same feasible outcome vector and hard floors | Proxy improvement with worse required objective, floor, human effort or full overhead | Universal optimum or superiority of any model/algorithm |
| S-R04 Offline/passive/exploratory modes with support-aware evidence | Periodic independently approved offline updates versus bounded passive-online candidate batches, with identical support requirements | Unsupported action promoted, propensity invented, selection/censoring can reverse result | Safe/beneficial live exploration or no confounding |
| S-R05 Externally bounded reservations and no live exploratory effects | Reserve the whole permitted experiment worst-case envelope upfront rather than incrementally per trial, under identical ceilings | One new trial exceeds reservable cap, spends recovery reserve or explores prohibited effect | Provider internal spend/debit bound when unobservable |
| S-R06 Independent staged promotion and deterministic explanation | Independently approved offline-only promotion to new synthetic sessions versus extra shadow/canary stages at the same floors | Unreviewed/stale/mismatched artifact effective, shadow causes action, or explain calls a model | Live effectiveness, zero future regressions or entitlement |
| S-R07 Boundary-bound policy adoption and append-only rollback | New-session-only policy adoption versus explicitly approved checkpoint-boundary adoption, both with append-only supersession | Mid-effect route change, lost evidence, duplicated unresolved effect, old grants restored, false settled Stop | Undoing external effects, paid usage or all failures |
| S-R08 Dependency invalidation plus finite freshness windows | Mandatory identity invalidation plus conservative fixed-age re-review versus additional statistical drift monitoring | Changed identity/stale evidence survives next admission, missing window means infinite use | Detection of every hidden provider/task shift |
| S-R09 Domain-scoped features and explicit derived-policy scope | Explicitly consented, recipient-scoped cross-project aggregate learning with separately qualified privacy controls | Unauthorized cross-domain fetch, training, scoring, explanation, export or post-withdrawal use | Anonymity, machine unlearning or all side-channel resistance |
| S-R10 Independent audits, holdouts and gaming tripwires | Full independent review plus a fresh sealed confirmation bank, with the same acceptance and privacy gates | Seeded proxy exploit passes, test contamination is hidden or adverse case omitted | Reward-hacking immunity, unbiased human judgment or exhaustive attacks |
| S-R11 Frozen estimands/margins and exact result classifier | Preregistered fixed-horizon versus justified sequential inference with identical metrics, margins and hard ceilings | Outcome flips under prescribed missingness/overhead/dependence correction; regression threshold or floor met | Practical equivalence from nonsignificance or cross-route generalization |
| S-R12 Off-by-default inertness with independent witnesses | Absent optional payload versus installed inert payload with core-owned bounded metadata, both default-disabled | Any forbidden adaptation call/write/egress/reservation while disabled, or observer blind spot claimed zero | Literally zero package metadata/disk cost or infinite-time inertness |

<a id="rs-s24"></a>
## S24 — Completion gate and artifact-only QA

- **G01:** S1/S4 specify adaptable surfaces, immutable authority/privacy/acceptance boundaries and proposal-only application
- **G02:** S2 defines provenance-qualified outcomes, mature/delayed labels and null-versus-zero semantics
- **G03:** S5–S7 define modes, no-live exploration, hard caps and independent/Owner promotion
- **G04:** S9–S12 define finite-window schema, immediate invalidation, append-only rollback and privacy scope; numeric calibration remains U
- **G05:** S13–S15 define nontradeable floors, gaming attacks and honest-reward discriminators
- **G06:** S17 defines off-by-default zero-attributable-work predicate; runtime proof U
- **G07:** S18–S21 plus appendices define required non-inferiority margins, reversal rules and exact fixture predicates; numeric deployment values BLOCKED pending adoption; every runtime fixture UNEXECUTED
- **G08:** S23 covers every recommendation with competitor/falsifier/non-proof; no technology/model/provider/vendor selection or route qualification
- **G09:** S22 explicitly limits all conclusions, including no measured improvement or entitlement
- **G10:** `qa.json` records artifact-only structure/link/privacy-pattern checks and rehash of safe pinned governance inputs. No protected path was edited. A bounded pattern scan is not proof that every conceivable secret/side channel is absent; credential/authentication files were not read

Machine appendices: `coverage.json`, `fixtures.json`, `decision-contract.json`, `source-register.json`, `pinned-inputs.json`, `qa.json`. These are research artifacts, not installed policy, executable product tests or runtime acceptance receipts.

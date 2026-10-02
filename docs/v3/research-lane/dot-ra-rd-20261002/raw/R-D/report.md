# R-D — Falsifiable quota, usage and lock-in measurement

Research findings, endpoint contract and reusable preregistration

**Evidence date:** 2 October 2026  
**Experiment status:** All target outcomes are unrun and unknown. This report establishes no savings, cache advantage, quota advantage or lock-in reduction.  
**Decision posture:** D-018 and D-024 are accepted premises, not reopened decisions. Recursion is itself a harness and orchestrates other harnesses. Hermes is one candidate upstream harness; it is not the executive control plane.

## 1. Findings and claim boundary

The testable claim is narrower and more useful than an allegation about vendor motivation: **for a specified workload, route, account regime and continuity condition, does Recursion achieve independently accepted outcomes with lower native allowance consumption or other explicitly named resources, while reducing human effort and preserving authority, evidence and correctness?** An honest study must be able to answer yes, materially equivalent, worse, inconclusive, or not identifiable.

Five findings determine the measurement contract:

1. **Subscription allowance, rate-limit capacity, token activity and money are different endpoints.** Public Codex App Server documentation exposes usage-window percentages and reset information, as well as separate token-activity fields. Claude Code documentation distinguishes local cost estimates from authoritative billing and subscription usage. Neither establishes a universal conversion from tokens or API list prices into subscription allowance. [S1, S2]
2. **Even similarly named token counters have different accounting algebra.** Anthropic's documented input count excludes cache creation and cache read tokens; its total input combines the three. OpenAI exposes cache detail within input accounting and reasoning detail within output accounting. Normalization requires the exact endpoint/schema version, not a universal sum. [S3, S4, S5]
3. **A successful process exit or missing usage report cannot establish zero consumption or accepted completion.** Cursor explicitly documents failed runs that do not emit a well-formed final JSON result. OpenAI describes incomplete responses that can consume input and reasoning tokens without visible output. These are concrete reasons to register attempts before dispatch and preserve missing consumption. [S5, S6]
4. **Useful native functionality belongs in the baseline.** Native caches, memory, resume, compaction, helpers, indexing and ordinary operator competence must remain available wherever they would ordinarily be used. A wrapper-versus-disabled-harness comparison would test an artificially weakened competitor. The controlled comparison below holds the route constant; a separate practical comparison allows each system its best eligible configuration.
5. **No resource experiment identifies deliberate vendor intent.** Lower measured usage could arise from workload fit, context policy, service configuration, implementation trade-offs or other mechanisms. Equal or worse usage would reject the relevant Recursion advantage claim, but would not disprove a hidden intention either. The allegation that a vendor deliberately unoptimizes quota remains unsupported here. An intent study would require independent evidence about decisions, knowledge and alternatives, plus its own falsifiable predictions. No such evidence is supplied or collected.

### Coverage, authority and evidence classes

R-D itself names no route roster. For measurement coverage only, this report adopts the nine routes named in the same packet's R-B/R-C: Codex App Server/ChatGPT-backed Codex; Claude Code; Cursor; Gemini/Google CLI; Grok Build; Hermes; OpenCode; Antigravity; and Pi. This is an explicit within-packet coverage assumption, not a revived historical catalog or a decision that all nine are eligible to run.

The report uses four claim classes: **source-documented** (a cited source says it), **locally observed** (direct evidence from an authorized observation), **inferred** (a reasoned design recommendation), and **unverified/unknown**. All proposed experiment methods below are inferred recommendations. No route capability or target outcome was locally tested. A source-documented counter is a candidate observation surface, not evidence that it was collected, complete, or accurate in a future run.

For future data cells, use a separate epistemic field: **measured**, **modelled**, or **unknown**. A measured value can still have rounding, scope limitations or uncertain attribution. A modelled value must identify its model and assumptions. Unknown is represented by a null value plus a reason, never a numeric zero. “Not applicable” is a separate applicability state and needs a justification.

Credentials, entitlement, terms, automation permission and counsel clearance are **eligibility gates**, not performance metrics. A blocked route is “not eligible/unrun,” not “failed performance” and not zero cost. Eligibility does not establish safety or scientific comparability. No login, entitlement check, quota probe, provider call or account change was performed for this report.

## 2. Estimands, units and denominators

An **assigned episode** is a frozen goal with acceptance criteria and a prespecified observation horizon, including its preparation, execution, interruptions, recovery, verification and human repair. A continuity episode additionally identifies the source-to-destination transition and injected loss. A task family groups related goals sharing substantive structure. An attempt is an admitted or dispatch-intended execution, including failed, cancelled and helper attempts. An accepted outcome requires independent verification; a harness's own success message is insufficient.

Use three reporting layers together:

- **Assigned-episode layer:** verified-success fraction and resource totals per all assigned episodes. This is the principal protection against removing hard failures from the denominator.
- **Useful-output layer:** all resources consumed by the assigned cohort divided by independently accepted outcomes in that cohort. Failed attempts and repair stay in the numerator. If no outcome is accepted, this ratio is undefined and reported as such, alongside the total resources and zero accepted outcomes. It must never become zero cost per success.
- **Quota-window layer:** allowance consumption and interference measured over the actual shared account/bucket/reset window. A task-level allowance debit is reported only when attributable. A rounded or delayed shared meter does not become a precise per-task number by division.

For a compatible resource k and arm a: resource-per-assigned-episode is total resource k from every included attempt and human activity divided by the number of assigned episodes. Resource-per-accepted-outcome uses the same numerator and the accepted-outcome count. Ratios of cohort sums are primary summaries for these efficiency quantities; averaging successful-run ratios is not an equivalent estimator.

Compare Recursion minus direct harness within a prespecified route/condition. Lower is favorable for burden; higher is favorable for independently accepted outcomes. Report absolute differences before optional relative ratios. A ratio is undefined when the baseline denominator is zero. Do not pool different subscription units, tokenizer definitions or unknown counters into an “overall burn” scalar. Report a resource vector. Any workload aggregation requires an explicit target population and prespecified weighting, not weights chosen after results.

Failures, fallback to human work, model rerouting, loss of a session and quota exhaustion are part of the episode outcomes. They are not automatically exclusions. Specifying the target effect and treatment of such events before analysis follows the estimand principle in ICH E9(R1), applied here as a statistical analogy rather than a regulatory requirement. [S15]

### Comparison keys used in the endpoint dictionary

**D:** matched direct use of the same harness/route in Section 6.  
**X:** strongest eligible direct source-to-destination migration using native export/resume and ordinary portable artifacts/manual reconstruction; the source may continue natively as an additional “do not switch” comparator.  
**P:** direct ecosystem port of the same required capability with equivalent acceptance, including no-port outcomes.  
**N:** matched no-future-work condition in which reuse investment receives no hypothetical future credit.

Every endpoint below inherits the all-attempts boundary and measured/modelled/unknown classification. “Observable” means potentially obtainable under future authorization, not observed in this study. All current values are unknown. The comparator and “does not prove” columns apply to each named endpoint individually, including subcomponents.

## 3. Complete endpoint dictionary

### 3.1 Native allowance and service exposure

| ID / endpoint | Unit and denominator | Observability and evidence requirement | Comparator; does not prove |
|---|---|---|---|
| Q1 Plan allowance / limit | Provider-native requests, credits, percentage capacity or declared unit per named bucket/window; plan limit is a stock, not a task cost | Official account-specific limit with timestamp, tier, bucket and reset definition; undisclosed capacity stays unknown. A percentage does not reveal absolute tokens. [S1, S2, S8, S12] | D; does not prove consumption or permission to automate |
| Q2 Remaining / used allowance | Same native unit per bucket/window at timestamp; both before and after snapshots | Preserve raw value, precision, freshness, window ID and whether stale/cached. Never infer total allowance from price. | D; does not prove task attribution |
| Q3 Attributable allowance debit | Native units or percentage-point change per assigned episode only if isolated/attributable; otherwise per randomized window/cohort | Reconcile replenishment, reset, refunds, concurrent clients, delayed updates and bucket changes. Rounded meters yield intervals or unknown task debit. | D, X, N; does not prove monetary savings or vendor intent |
| Q4 Quota accessibility / wait | Throttle or exhaustion events per assigned episode/window; seconds blocked per episode; verified completions per observed window | Local time/event logs plus official limit error and reset evidence. Separate RPM/TPM from plan allowance. No forced exhaustion to find capacity. | D, X; does not prove a larger entitlement |
| Q5 Paid charges / credits actually debited | Invoice currency or provider credit units per assigned cohort and accepted outcome; fixed plan fee separately per billing period | Authoritative receipt/meter with scope, taxes/discounts/credits as applicable. Token-times-price is modelled, not a bill or subscription debit. No currency conversion without a frozen explicit method. | D, X, N; does not prove reduced native allowance |

### 3.2 Model and tool resource accounting

| ID / endpoint | Unit and denominator | Observability and evidence requirement | Comparator; does not prove |
|---|---|---|---|
| U1 Input tokens | Endpoint/tokenizer-native tokens per request, all attempts, assigned episode and accepted outcome | Preserve raw input field and documented inclusion algebra. Normalize only with an explicit mapping; multimodal units remain labelled. [S3, S4] | D, X, N; does not prove equal compute or quota |
| U2 Output tokens | Endpoint-native tokens per request and all-attempt episode/cohort | Preserve reported total and relationship to reasoning, visible and non-visible formatting tokens. Locally tokenized visible text is a modelled estimate only. [S5] | D, X, N; does not prove useful output quality |
| U3 Reasoning / thinking | Reported reasoning/thought tokens per attempt and episode; detail of output where specified | Count field only; do not request hidden reasoning. If not separately exposed, unknown, not zero. Do not add to output when already included. [S5, S7] | D, X, N; does not prove reasoning quality or disclose internal reasoning |
| U4 Cache reads | Reported read/cached input tokens per request and episode; token hit rate = compatible cached-input total / compatible input total | Exact endpoint's cache field, model, prefix regime and retention. Avoid summing request-hit rate with token-hit rate. [S3, S4] | D, X, N; does not prove grant validity, freshness, allowance benefit or owned reuse |
| U5 Cache writes / refreshes | Reported written input tokens by TTL class per attempt/episode; write/refresh request counts separately | Preserve whether writes are part of input, exclusive categories or separately charged dimensions. Unexposed write counters remain unknown. [S3, S4] | D, N; does not prove later amortization |
| U6 Inference requests / retries | Admitted requests and retries by cause per assigned episode; retry fraction per all identified inference attempts | Distinguish user turns, provider requests, transport retries and repeated business effects; include 429s, reconnects and failures. Unknown hidden retries require coverage flag. | D, X; does not prove provider compute count |
| U7 Helper / small-model calls | Attempts and full resource vector by helper role and actual model per assigned episode | Include planners, routers, background agents, subagents, title generation, safety/repair calls and post-run analytics when attributable. Record included/excluded/unknown coverage, not just named children. [S2, S9] | D, X, N; does not prove complete coverage without reconciliation |
| U8 Compaction / summary / refresh | Operations plus full resource vector per episode and per compaction/reconstruction; include failed operations | Separate native and Recursion compaction, evidence refresh, memory consolidation, branch summaries and rehydration. Reduction in context length is not saved billed work. [S7, S9, S13] | D, X, N; does not prove semantic or authority preservation |
| U9 Verification / repair | Model/tool resource vector, verification invocations and repair attempts per assigned episode; independently accepted outcomes as secondary denominator | Include first evaluation, reruns, failed checks, review model, human correction and final acceptance. Shared evaluator overhead is separately labelled in both arms, never erased. | D, X, P; does not prove unbiased acceptance without independent criteria |
| U10 Tools / external services | Calls, provider-native billable items, CPU seconds, network bytes, storage byte-time as available per episode | Report separate resources and service boundaries; local timers/process accounting may measure local work, not provider-internal compute. Tool fees can exist beyond token counts. | D, X, N; does not prove lower total cost if other costs are unknown |
| U11 Local orchestration overhead | CPU time, elapsed startup/coordination time, peak memory, storage and transfer units per episode; setup separately | Capture both Recursion and baseline instrumentation overhead with same method. No dollar value for unpaid hardware/labor without a prespecified model. | D, X, N; does not prove net system efficiency alone |
| U12 Missing-report coverage | Attempts with each required counter / all dispatch-intended attempts, by lifecycle; unallocated aggregate consumption per window | Missing ledger in Section 4. Hidden-attempt denominator may itself be unknown; state this rather than a false complete-coverage percentage. | D, X; does not prove missingness is random |

### 3.3 Productive continuity and human effort

| ID / endpoint | Unit and denominator | Observability and evidence requirement | Comparator; does not prove |
|---|---|---|---|
| C1 Independently accepted completion | Accepted goal outcomes / all assigned episodes; component outcomes separately | Frozen correctness/evidence gate and independent verdict; partial completion not full success. Record post-horizon completion separately. | D, X; does not prove safe authority use by itself |
| C2 Recovery to productive work | Seconds from loss/switch trigger to first independently verifiable useful action and to final acceptance, per assigned transition | Define useful action before run; report nonrecoveries and censoring, not successful-only median. End-to-end elapsed time accompanies incremental recovery time. | X; does not prove overall savings |
| C3 Authority and evidence preservation | Violations per assigned transition/effect; required evidence items preserved and validated / required items; missing items count explicitly | Independent checks of grant epoch/scope, pending approvals, revocation, provenance, source freshness and effect settlement. Critical failures trigger hard floors. | D, X; does not prove provider internals are fully mediated |
| H1 End-to-end wall-clock | Elapsed seconds from assigned-work start through accepted result or terminal horizon per episode | Includes setup, model/tool wait, permission wait, repair and review. Separately mark user-unavailable time and external outage; do not subtract them from primary elapsed time. | D, X, N; does not prove active human labor |
| H2 Active human labor | Person-minutes by preparation, supervision, approvals, re-prompting, correction, reconstruction and review per all assigned episodes and accepted outcome | Timestamped start/stop activity record; sum people, not just clock time. Attribute overlapping activities with an explicit rule; do not double-count one person's same minute. | D, X, P, N; does not prove cognitive ease or monetary cost |
| H3 Corrections and re-prompts | Correction interventions and re-prompts per assigned episode, with severity/cause; affected defects separately | A re-prompt changes/reissues instructions because current progress is insufficient. Corrections are distinct human intervention events with linked edits, not lines changed. Scripted task inputs are separately coded. | D, X; does not prove equal effort per intervention |
| H4 Reviewer effort / agreement | Reviewer person-minutes per assigned episode; agreement/disagreement counts per doubly reviewed outcome | Review failures and disputes count. Separate substantive product verification from study-only audit; show full operational and full study totals. | D, X, P; does not prove ground truth merely from agreement |

### 3.4 Lock-in and porting

| ID / endpoint | Unit and denominator | Observability and evidence requirement | Comparator; does not prove |
|---|---|---|---|
| L1 Accepted transition coverage | Accepted source→destination continuity episodes / all eligible assigned transitions; ineligible pairs separate | Predeclare required semantics, authority/evidence and useful work. Report by pair and loss class; no universe-wide percentage from selected pairs. | X; does not prove contractual permission or universal portability |
| L2 Migration / reconstruction burden | Person-minutes, elapsed seconds and resource vector per assigned transition and accepted transition | Include export, mapping, revalidation, relearning, lost-work rework and unsuccessful migration. Compare native export plus competent manual transfer. | X; does not prove lower vendor dependence if semantic losses remain |
| L3 Porting effort | Person-minutes by discovery/specification, implementation, authority/schema mapping, fixtures/independent verification, packaging/docs and repair per assigned port and accepted equivalent port | Count abandoned ports and failed conformance. Shared adapter/framework investment is separate and amortized only over observed accepted reuse, with raw total always shown. | P; does not prove long-term maintenance cost |
| L4 Port class / structural burden | Native reuse, mechanical adaptation, semantic adaptation, rewrite, no-port; handwritten/generated glue LOC, host API touchpoints and authority translations per required capability | Native reuse leaves artifact unchanged; mechanical changes manifest/schema; semantic adaptation shims behavior; rewrite reimplements it. Record tests and defects, not just LOC. | P; does not prove semantic equivalence or cheap effort |
| L5 Capability / permission / evidence loss | Accepted-equivalent required capabilities / all required capabilities; named degraded/lost items and extra permissions per assigned port/transition | No weighted score. Distinguish required unavailable semantics from optional features; any critical authority/evidence loss fails the floor. | P, X; does not prove absence of hidden coupling |
| L6 Maintenance and reversibility | Person-minutes and conformance defects per observed upstream-breaking release; accepted return migrations / assigned return migrations | Track real release exposure and abandonment; no extrapolated “annual savings” from no observed breaks. Both outward and return transitions have full costs. | P, X; does not prove future stability |

All dictionary rows use a competing direct route, migration or porting option. No row is sufficient alone to support the headline claim. A favorable endpoint is subordinate to the hard floors and the prespecified joint outcome/effort requirements.

## 4. Missing-report ledger and human-effort protocol

### Missing, cancelled and partial attempts

Before dispatch, allocate attempt and parent IDs and record the assigned episode, work unit, role and requested route. After dispatch, preserve admission uncertainty, request correlation if available, observed stream/exit, terminal status, cancellation request time, cancellation acknowledgment, last event and effect-settlement state. A cancellation request is not proof that computation stopped or that effects were rolled back.

Each missing-counter ledger row contains: attempt ID; expected counter; lifecycle state; observed lower bound, if any; unknown residual; missingness reason; raw source reference; aggregate/window reconciliation reference; recovery action allowed; and final reconciliation status. Reasons include no report, stream interrupted, timeout, crash, unknown admission, provider field absent, hidden helper, stale meter, schema mismatch and aggregate-only attribution.

- A failed-before-dispatch attempt may have proven zero provider consumption only when a local record establishes that no request escaped and no helper ran. Its local and human costs still count.
- A dispatched attempt with no usage report has unknown provider consumption, even if it produced no text.
- A partial stream can establish reported lower bounds; it cannot establish the final total. “Known subtotal + unknown residual” is the preferred display.
- A later cumulative total can reconcile missing requests only if scope, counter semantics and interval are compatible. Store the aggregate and its covered attempt set; do not allocate it arbitrarily or count both aggregate and children.
- Keep orphan helpers and asynchronous work open until settlement or the preregistered horizon. At the horizon, preserve unknown residual and unsettled status. Do not silently drop late receipts; append a dated reconciliation without changing the frozen primary analysis.
- Record exclusions with reason and timing, but retain every assigned episode and its resource ledger in the primary flow/accounting report. Counter failures can make a cost comparison non-identifiable even when correctness outcomes remain usable.

No complete-case analysis may be the sole efficiency result. Present missingness by arm, route, condition, helper role and lifecycle. Sensitivity analysis may bound missing usage using genuinely documented ceilings or independently justified externally measured ranges, labelled modelled. If there is no defensible upper bound, it remains unbounded/unknown; no numerical imputation is invented. A favorable result that depends on missing Recursion costs being zero is invalid.

### Human work cannot disappear

Use the same task brief, training material, operator competence criteria, permission policy and help availability in both arms. Log human activities as intervals and coded interventions. Record preparation before the first prompt and correction after the apparent final answer. Retrospective estimates are explicitly modelled and reported separately from timer records.

Two people working simultaneously contribute two person-minutes per minute of overlap. One person multitasking does not contribute more than their actual active interval total; use a prespecified allocation or shared-unallocated bucket. Idle provider wait is wall-clock, not active labor. Mandatory attention while waiting is supervision labor and must be recorded. Approval clicks, reading lengthy outputs, debugging failed resumptions and manually reconstructing evidence count.

Blind acceptance reviewers to arm where feasible by stripping branding without stripping evidence. If blinding is impossible, disclose it and use fixed rubrics plus independent adjudication. Operator learning is controlled through training before confirmatory runs, assignment rotation and order balance; the same person must not use remembered answers from an earlier arm. Use equivalent but disjoint task variants or isolated operators when carryover cannot be prevented. Human-effort recording burden is measured in both arms and distinguished from normal operational labor.

## 5. Confounder register

Randomization does not repair a deliberately unfair baseline or unobservable quota attribution. Blocking controls known nuisance variables, while randomization addresses residual imbalance; this is the core rationale of randomized block designs. [S14]

| Confounder | Control / randomization / recorded covariate | Residual limitation or stop trigger |
|---|---|---|
| Provider cache warmth, retention and prefix | Declare cold/warm/unknown strata; record last eligible activity, actual cache fields, TTL regime, key/prefix identity and cache-setting version; balance order | Session reuse is not proof of a cache hit. No claim of forced cold if the service cannot clear or verify cache state. |
| Cross-arm cache contamination | Disjoint synthetic prefixes/state where permitted; isolation or randomized window blocks; measure both arms' observed hits | Isolation itself may change behavior. If interference cannot be controlled, window-level policy comparison replaces per-task attribution. |
| Model, effort, routing and serving change | Same pinned requested model/effort/context/temperature where exposed; record actual served identity and reroutes; freeze routing policy | Hidden model/effort differences make this a system-level comparison, not a same-model causal estimate. |
| Account tier, subscription/API mode and resets | Same eligible plan regime, bucket and regional endpoint; record reset times, meter freshness and unrelated traffic; randomize independent windows where shared | Never switch accounts to bypass limits. A reset or unattributed shared usage breaks naive debit subtraction. |
| Helpers, tools and hidden system behavior | Retain useful native features; match allowed capabilities, helper policy and tool outputs; inventory visible helpers and unknown coverage | Unknown mandatory helper consumption can invalidate complete-resource superiority. Hidden system instructions cannot be claimed identical. |
| Task difficulty and repository size | Frozen revisions; task-family blocks; prespecified size/dependency/context bands and held-out equivalent variants | Post-hoc “easy” subsets cannot become the principal result. No extra hints for one arm. |
| State, memory, compaction and source fork | Freeze initial state and learning policy; assign whole adaptive sequences, not individual turns; record state/authority epochs and fork identity | A summary can alter evidence or authority. Shared adaptive state creates dependent outcomes. |
| Session / machine affinity | Cold, warm and loss strata; record host, process/session, region, time since activity and service affinity if exposed | Hidden provider placement is unknown; do not infer portable KV state from exported text. |
| Network, host load and local tooling | Matched host image/toolchain; monotonic timers; record latency, resource contention, outages; order/window blocks | Changed host begins a new experiment version; external incidents remain in the assigned-episode record. |
| Human work transfer | Matched operator training and assistance; time all roles; blind review where possible; rotate or isolate task exposure | Extra manual pre-processing in Recursion is a cost, not free input. |
| Censoring, failures and missing counters | Fixed horizon, full assigned cohort, missing ledger and sensitivity analysis | Do not stop timing at a convenient failure or omit cancelled jobs. |
| Acceptance leakage / evaluator bias | Frozen independently held criteria, concealed outcome labels and independent review | An implementer's PASS cannot substitute for acceptance; contaminated evaluation stops claims. |
| Instrumentation and meter latency | Same instrumentation regime, known schema map, record collection overhead/freshness; reconcile disjoint scopes | Telemetry can change timing and expose private data; unsafe collection stops the run. |
| Policy tuning / selective reporting | Freeze optimization on separate development data; register all route/condition cells and analysis | Tuning on confirmatory results creates a new experiment; all unfavorable cells remain reported. |

## 6. Explicit matched direct-harness baselines

### Two distinct comparisons

**Controlled route comparison:** Recursion orchestrating harness H versus direct use of that same harness H and the same eligible interface, version, model, effort, goal, repository revision, tools, capabilities, permission policy and acceptance criteria. The direct caller has no Recursion orchestration layer but retains ordinary harness functionality. Recursion-owned memory/evidence machinery is treatment, and its creation, maintenance and recovery costs count.

**Practical strong-baseline comparison:** Recursion's prespecified best eligible policy versus the best prespecified direct-harness workflow an informed operator would actually use. Both may use native memory, caching, helpers, indexing, resume, export, compaction and sensible prompting. Select and tune the baseline on separate development tasks before freezing it; report that tuning labor separately. This measures the whole workflow, not an isolated wrapper effect.

If Recursion's native harness runs directly against a provider rather than delegating to H, that is a separate native-harness arm. It cannot replace the delegated comparison or inherit the claim that only orchestration differs. If models or effort cannot truly match, retain the practical comparison with exact mismatch labels and withhold a controlled same-model claim.

Every route needs a signed match record: goal/fixture hash; source revision; required capabilities; upstream interface and binary/schema version; requested and served model IDs; effort and reasoning settings; context limits; tool/helper versions and policies; native memory/cache/compaction/export settings; operator/training allocation; account mode/tier/bucket/window; host/toolchain; acceptance gate; and a differences ledger. “Same model name” is insufficient where one route aliases, auto-routes or hides effort.

| Route | Direct baseline and features to preserve | Observable candidates / irreducible gap |
|---|---|---|
| Codex App Server / ChatGPT-backed Codex | Direct client of the same qualified App Server profile, with native thread resume/fork/compaction and approvals; a normal Codex workflow as practical comparator | Thread usage updates and account rate-limit fields documented. Native bucket percentages are not token-price conversions; exact counter completeness and actual entitlement require later qualification. [S1] |
| Claude Code | Direct user-authenticated Claude Code on the same execution surface; retain native compaction, cache, subagents and ordinarily useful tools | Token types and main/subagent/auxiliary labels are documented; local cost estimates are not the bill. Main-conversation cache statistics alone exclude subagents. [S2, S9] |
| Cursor | Direct same qualified CLI or SDK profile with native rules, tools, compression and resume; do not remove useful native interaction merely to simplify matching | CLI failures may lack final JSON. SDK live usage covers reporting turns and can be undefined; billed records are separate and costs may settle later. Plan-included chargedCents of zero does not establish zero quota burn. [S6, S19] |
| Gemini / Google CLI | Direct same Gemini CLI authentication class and route; retain native compression, routing and tools under the frozen policy | Telemetry documents input/output/thought/cache/tool tokens and request/compression counts; quota depends on authentication/pricing regime. Completeness and API-versus-subscription attribution remain to qualify. [S7, S8] |
| Grok Build | Direct same headless/ACP or interactive profile, with native helpers, memory and compaction left available in corresponding conditions | Official changelog records headless per-prompt/session token and cost output, and persisted per-turn usage. Exact schema, helper inclusion and allowance mapping need qualification; API docs cannot substitute for Build subscription accounting. [S10] |
| Hermes | Direct Hermes as an ordinary harness with the same selected provider profile, memory, skills, helpers and compression; no control-plane privilege | Native usage and context displays exist; some context breakdowns are explicitly estimates. Classify provider-reported and estimated fields separately; complete helper accounting is unverified. [S11] |
| OpenCode | Direct same run/serve/ACP profile, model variant, agents, tools, native resume/fork and compaction | Official CLI supports session stats and JSON export. A stats command's existence does not prove all helper/compaction usage or subscription attribution. [S13] |
| Antigravity | Direct same CLI or native surface and model policy; retain native task/workflow affordances and sanctioned recovery | Headless documentation exposes cumulative usage/duration/turn metadata, requiring before/after deltas or covered-attempt sets. Approval-required tools can be soft-denied while the process exits successfully; independent acceptance is essential. Quota UI and plan limits remain distinct from per-episode debit. [S12, S18] |
| Pi | Direct same RPC/CLI profile with native session/branching/compaction and configured extensions retained | RPC documentation includes assistant, reported tool, compaction and branch-summary usage in full-session totals. Custom compaction handlers may omit summary usage; post-compaction context usage can be null pending a fresh response. Qualify extensions and avoid cumulative double counting. [S16] |

Source availability is not route eligibility. Counsel/credential gates from R-C and mechanism qualification from R-B must be resolved separately before a future executable registration. No legal eligibility, provider permission or runtime support is asserted by this table.

## 7. Required counterfactuals and reuse separation

Each route comparison is stratified; a favorable warm result is never reported as a general result.

**Cold start:** Both arms receive the same original goal, source snapshot and allowed artifacts with no task-specific owned reuse. Include installation/setup if the estimand is first use; otherwise show that one-time cost separately and include ordinary episode startup. Provider cache state is independently recorded as verified cold, operationally cold with limitations, warm, or unknown. OpenAI says its cache cannot be manually cleared, so a new session is not by itself a guaranteed cold-cache intervention. [S4]

**Warm affinity:** Both arms receive equivalent prespecified prior work and retain their own useful native continuity. Include the cost of building that state in full-sequence results, plus separately labelled marginal continuation costs. Prespecify elapsed gaps and TTL regimes; do not discard inconvenient misses. A warm single-provider advantage is limited to that condition.

**Reconstruction after loss:** At a predetermined boundary, remove the designated acceleration state for both arms while preserving the same authorized external artifacts. Distinguish process/session loss, unavailable machine, cross-harness migration and source fork; these are different treatments. The direct comparator can use its strongest sanctioned backup/export/manual reconstruction. Check pending permissions, authority epoch, evidence freshness and effect settlement before resuming. Report full pre-loss investment plus recovery and completion; incremental recovery is secondary.

**No future work:** Assign a cohort that stops after the initial goal and a prespecified bounded observation horizon. Count all summary, indexing, cache-write, export and persistent-evidence investment, even when never reused. No assumed future tasks, lifetime amortization or hypothetical avoided calls are credited. If Recursion's investment makes this arm more expensive, report it as a real adverse result. Only observed follow-on work can amortize an investment in other cohorts.

**Source fork and changed evidence:** Use a controlled variant that invalidates selected evidence and another that preserves it. Both arms must revalidate source identity and freshness. Blindly reusing a stale answer is a correctness failure, not low burn. This is a separate continuity stratum inside cold/warm/loss designs, not an extra source of fabricated savings.

### Provider cache versus owned evidence reuse

Maintain two separate provenance ledgers:

- Provider cache ledger: provider/model/endpoint/account-region regime; prefix identity; retention settings; observed cache-read/write fields; reported hit/miss; unknown hidden behavior. It describes provider-managed acceleration.
- Owned reuse ledger: content-addressed evidence/artifact identity; source revision and freshness proof; creation and refresh costs; authority to reuse; transformation history; destination validation; consumed artifact IDs; actual downstream work avoided only when established by a paired counterfactual. It describes Recursion-controlled reusable information, not portable KV state.

A cross-route transition on the same provider might benefit from both, but a cross-provider transfer does not establish provider-cache portability. Cached tokens and reused artifacts have incompatible units and overlap causally; never add them as “total savings.” A future factorial ablation can vary owned reuse on/off and observed cache regime while retaining all safety features. Compare total compatible resources for each cell and their interaction; do not sum separate main-effect estimates when interactions exist. If cache state cannot be manipulated or verified, classify the ablation as observational/modelled and limit causal interpretation.

## 8. Statistical design, power and decisive interpretation

### Units and dependence

Randomize at the smallest level that does not share treatment state. Independent isolated episodes can be paired within task family and route. Repeats of one task are repeated measurements, not additional independent tasks. Turns and helper calls are accounting observations, not statistical replicates. A shared quota window with unrelated or cross-arm activity is a cluster; individual tasks within it cannot identify independent allowance effects. A persistent learning/memory policy is assigned to a whole sequence or independent state replica, with sequence as the experimental unit.

The registration names task-family, task-instance, repeat, operator, host, account/bucket/window and adaptive-sequence identifiers. Use blocking or whole-window assignment to avoid interference. If task-family and quota-window dependence are crossed, use a prespecified analysis supporting that structure or design genuinely independent blocks; a simple per-call t-test or ordinary bootstrap is invalid. Resampling/permutation must occur at the actual randomization unit, respecting matched blocks and carryover. Sparse independent clusters imply limited precision even if there are many calls.

Freeze the target task-family population and sampling rule before allocation. Include both continuation-rich and one-off work so the reusable-state hypothesis can fail. Register route-pair direction; A→B and B→A are not interchangeable. No route-wide claim follows from a single favorable task family. Use a blocked factorial or separate registered strata as feasible; do not choose a cell after seeing performance.

### Inputs that must be set before running

No numerical sample size, budget, effect threshold, confidence level, power target, endpoint weight or savings expectation is an accepted default in this report. An executable registration is blocked until its owner and independent reviewer set:

- A practically meaningful reduction for the claimed burden endpoint, meaningful human-effort superiority threshold, and verified productive-continuity superiority criterion for the D-024 headline; any narrower comparable-quality resource claim is labelled separately
- Equivalence bounds for “no meaningful difference,” with task-domain justification independent of observed arm differences
- Error-rate/confidence and multiplicity policy for the chosen primary endpoint family and confirmatory route/condition claims
- Independent-unit sample size and allocation, repeats, task-family coverage and window/sequence count, powered for the joint decision and equivalence/worse alternatives
- Maximum authorized usage/spend/human-time exposure, horizon, delayed-receipt window, retry policy and safety-stop actions

Set those using domain consequences and externally justified variance/correlation information, or a separately authorized pilot that is declared nonconfirmatory and frozen away from the confirmatory sample. A pilot may estimate variance, intracluster dependence, failure rate and missingness; it may not opportunistically redefine worthwhile benefit to fit its observed effect. Power calculations or simulations must mirror paired/clustered, repeated and adaptive-sequence structure, skewed resource distributions, binary acceptance and planned missingness sensitivity. If feasible authorized resources cannot support informative precision, preregister a descriptive feasibility study instead of relabelling it decisive.

### Analysis and interpretation

Report the assigned flow, all acceptance outcomes, all-attempt resource vectors, human effort, missing ledger, hard-floor events and uncertainty intervals by prespecified route and condition. Present both operational totals and total research instrumentation/audit overhead. No synthetic composite score is selected. The D-024 headline requires prespecified superiority over the strong baseline in verified productive-continuity outcomes and human effort, with all hard floors passed. A narrower resource-efficiency study may require comparable accepted quality, but non-inferiority on quality alone does not satisfy that headline. A cost-only improvement cannot rescue worse verified outcomes or unacceptable effort.

Use a predeclared inferential method compatible with the units above, such as block-respecting randomization inference and cluster-aware interval estimation, or a justified hierarchical model with explicit assumptions. The exact method and diagnostics must be frozen in the registration after design/power work, not chosen by favorable p-values. Equivalence requires predefined meaningful bounds and appropriate precision; a nonsignificant superiority test is not proof of no difference. [S17]

For a burden difference defined as Recursion minus direct:

- **Meaningful benefit:** its uncertainty interval clears the prespecified favorable threshold, all hard floors pass, resource coverage is adequate, and outcome/effort joint criteria pass
- **Practical no difference:** a prespecified equivalence analysis excludes differences outside the meaningful equivalence band; this falsifies the scoped claim of a meaningful advantage
- **Worse:** evidence establishes increased burden or human effort beyond the adverse threshold, or a required outcome/continuity criterion is worse; record the adverse result even if some token counter improves
- **No established benefit:** the favorable threshold is not met; this rejects deployment of the claim on current evidence but does not alone establish equivalence
- **Inconclusive/not identifiable:** intervals are too wide, missing consumption can change the decision, or attribution/matching is unresolved; do not convert this to either success or proof of no effect

### Decisive falsifiers

**Quota/burn claim:** For the registered route and workload, all-attempt native debit is materially equivalent or worse at acceptable outcome/effort criteria; or the claimed reduction disappears after helper, compaction, verification, failed attempts and human repair are included. If native debit is unknown, the quota claim is not identified even when token activity is lower. A cache-hit increase with equal or greater total burden is not a quota win.

**Productive continuity claim:** Recovery loses required authority/evidence, repeats an unsettled effect, fails independent acceptance, or requires more reconstruction labor without the prespecified verified-outcome/effort advantage. A hard-floor failure decisively rejects a safe-continuity claim for the tested condition.

**Lock-in reduction claim:** Accepted-equivalent migration/port coverage is no better and reconstruction/porting effort is practically equivalent or worse than the strong direct option; required semantics or evidence are lost; return migration cannot be completed within the registered conditions; or costs merely move into bespoke Recursion adapters/maintenance. Open-source availability alone does not falsify these adverse outcomes.

**Generalization claim:** Gains occur only with warm affinity, one direction or one task family and disappear or reverse in cold/loss/no-future-work strata. This rejects a broader unconditional claim, while allowing the narrower conditional observation to stand.

**Intent allegation:** None of these experiments establishes deliberate vendor unoptimization. A lower count is not evidence of intent; a worse Recursion result rejects its performance proposition. Intent remains unverified pending independent evidence and a separate research question.

## 9. Hard floors, stops and rerun policy

Hard floors precede cost, quota or speed comparisons. They are pass/fail requirements, not weighted preferences.

1. **Authority:** Current grant, scope, epoch, actor and permitted effects survive each transition. No copied credential, unauthorized provider/account route, silently expanded permission or resurrection of a revoked approval.
2. **Safety and effect settlement:** No dangerous real-world action; use inert/synthetic effects until specifically authorized. A stop/cancel must leave known settlement or a safe blocked state. An unresolved effect cannot be blindly retried.
3. **Privacy:** No secrets, credentials, private source content or unnecessary personal data in telemetry, public queries or exported artifacts. A hash does not automatically anonymize a sensitive short identifier.
4. **Correctness and evidence:** Frozen acceptance criteria, fresh source identity, required provenance and independent review. A failed task is recorded as failure; its cheap failure cannot enter an accepted-outcome savings claim.
5. **Reproducibility and honest accounting:** Known versions, immutable fixture/result identity, stable schema interpretation, raw receipts and no lost assigned attempts. Required unknowns must stay explicit; a fabricated zero or unverifiable success is a floor breach.

**A single authority, safety or privacy breach stops the affected comparison immediately.** A single critical correctness/evidence breach stops acceptance and savings claims for that affected episode/condition, retains all costs and triggers independent review; it does not justify deleting the observation. A broken accounting/reproducibility invariant suspends the affected metric or comparison until repaired. Ordinary correctly recorded task failure is an outcome, not grounds to erase the whole study. If the breached mechanism is shared, stop all affected arms/conditions; otherwise quarantine with an independently documented scope.

Additional prespecified stops: permission/eligibility revoked; usage/spend/time ceiling reached; ambiguous effect settlement; uncontrolled concurrent quota use; model or schema drift outside the frozen profile; failed privacy instrumentation; unresolvable clock/source identity; or registered statistical stopping boundary. Stop issuing new work, capture bounded safe evidence, record outstanding work and unknown residual consumption, and notify the responsible human. Do not switch identities, buy quota, raise a cap or silently use another paid route.

The default design recommendation is a fixed, powered independent-unit sample and fixed observation horizon, with only safety/authorization stops. This competes with a valid preregistered sequential design, which may be chosen before data and must account for repeated looks. Peeking until a win or adding runs after a disappointing interval is invalid.

A repaired instrumentation defect may justify a newly identified rerun under a logged amendment, with prior data retained. It cannot replace a legitimate bad result. Changed host image, provider model/schema, upstream harness, acceptance rubric, memory policy or data-generating workload starts a new experiment/version. Reanalysis of immutable data is labelled reanalysis, with original primary results preserved. A routine restart within the registered same-host recovery scenario is a measured event, not a new study; changed-host recovery has its own frozen host pair and loss condition.

## 10. Provider-free reproducibility and local execution handoff

No target benchmark, model, harness or test was run. Future work separates **provider-free qualification** from **authorized live measurement**. Provider-free fixtures can validate accounting algebra, lifecycle states, permissions/effects and analysis plumbing; they cannot establish live allowance efficiency, provider behavior or real model quality.

### Prerequisites before any future invocation

- Owner-signed scope, chosen route profiles and permitted synthetic/public fixture set; R-C eligibility/counsel decisions and R-B mechanism qualifications recorded as independent gates
- Completed preregistration in Appendix A, reviewed independently before allocation; all numerical inputs filled with justification and approval
- Frozen instrument/schema maps, analysis specification and acceptance rubric; independently held expected outcomes for fixtures
- Approved account/entitlement already available through a credential-preserving route; no key copying, authentication changes or new access implied by this handoff
- Explicit spending/usage/time authority and ceilings, approved observation sources, isolation/window plan, operator/reviewer availability, and safe stop/effect-settlement procedures

### Required records and conditions

Preserve content hashes and versions for goal/task-family manifests, repository fixtures, native/Recursion configurations, tool versions, adapter schema maps, dependencies, OS/host image, timezone/clock method, prompt/context templates, owned artifacts and evidence lineage. Use opaque local references for identities; keep credentials out. Save randomization assignment and seed when applicable, every attempt and human activity record, quota snapshots, raw usage receipts, independent verdicts, effect settlement, exclusions, amendments and missing-report ledger.

Before live measurement, a future authorized operator would qualify deterministic synthetic cases for: absent usage, interrupted stream, cancellation before/after admission, partial completion, duplicate delivery, cumulative counter reset, late receipt, nested helpers, custom compaction without usage, stale evidence, revoked authority, source fork and unknown effect settlement. Every case has expected accounting/authority outcomes. These are proposed required cases, not tests executed here.

The live experiment then follows the frozen allocation with no outcome-guided tuning. Capture baseline snapshots and match record, start all cost clocks, execute only the authorized condition, maintain every attempt including failed/retried work, settle effects, collect independent acceptance, and reconcile within the prespecified horizon. Verify the resource graph covers the cohort without overlap. Report unmeasured fields alongside known subtotals.

### Rerun and exit criteria

A future run exits as completed at the registered sample/horizon with every assigned episode accounted for, or as stopped with reason and unresolved ledger. Completion is not necessarily success. Independent review decides whether the prespecified claim is supported, falsified, inconclusive or ineligible. Reproduction on another host is a new identified replication with the original frozen protocol and any deviations explicitly compared. Live outcome status remains unrun until this process actually occurs.

## 11. Recommendation register

| Recommendation | Competing option | Decisive falsifier / rejection criterion | What it does not prove |
|---|---|---|---|
| Use native-unit resource vectors and full-cohort accounting | Single converted token/dollar score or successful-only cost | Claimed benefit disappears after complete counters/failed work, or endpoint mapping cannot reconcile | Vendor intention or universal allowance conversion |
| Require both matched and practical strong baselines | Minimal/disabled direct harness; native-only Recursion comparison | Advantage survives only a weakened baseline or unmatched model/effort | Isolation of hidden provider implementation differences |
| Separate cold/warm/loss/no-future-work | Warm-session average or hypothetical lifetime amortization | No benefit or worse in one-off/loss conditions rejects general claim | Future workload frequency without observation |
| Make useful outcomes and human effort joint acceptance requirements | Token savings alone | Lower tokens accompany worse accepted outcomes or more unacceptable labor | An arbitrary weighted “best product” ranking |
| Treat owned reuse and provider cache as distinct mechanisms | Sum their counts as combined savings | Factorial/paired comparisons show no total benefit or stale reuse failure | Cross-provider KV portability |
| Use family/window/sequence-aware randomization and analysis | Per-call independent samples; post-hoc test selection | Claimed precision vanishes with actual clusters or carryover correction | Absence of every unmeasured confounder |
| Count port/maintenance burden and capability loss | Count supported adapter names or changed LOC alone | Equivalent accepted coverage and labor are no better, or ongoing glue/repair offsets reduction | Legal permission or indefinite future stability |

## 12. Completion gate and remaining uncertainty

All twelve questions are addressed: endpoint definitions and observability (Sections 2–3); missing attempts (4); human effort (4); confounders (5); per-route matched baselines (6); counterfactuals and mechanism separation (7); preregistration (Appendix A); hard floors (9); reproducibility and execution handoff (10); falsifiers including equivalence and worse outcomes (8).

The deliverable is a completed evidence-backed measurement design, not an executed experiment. Unknown inputs are explicit run-admission blockers rather than invented defaults. No provider/internal allowance formula, target savings magnitude, numerical budget, sample size, metric weight or empirical benefit is established. Route eligibility is separate from measurement coverage. Source-documented behavior is not local verification. D-018/D-024 remain accepted; the outcome may honestly be no advantage or worse.

No protected project paths were edited. The only generated files are the report and document-production/QA artifacts. No private project text was used in public search queries. A final artifact-only privacy/secret check is recorded in the QA log; it is not a test of Recursion or a claim of scientific acceptance.

## Appendix A. Reusable preregistration form

This is a reusable form, intentionally containing unresolved fields. A future registration is not executable until every required field has a value or justified not-applicable state, and is signed and frozen. Do not substitute the report's examples for owner-approved inputs.

### A1 Identity, question and authority

- Registration ID/version/hash; date/time; owner; independent reviewer; source-document snapshot IDs
- Claim scope: route(s), direction(s), workload population, native/delegated/practical arm, continuity conditions and target observation horizon
- Hypothesis: named resource reduction plus named verified-outcome and human-effort requirement; explicit meaningful-benefit threshold and justification
- Falsifier: meaningful equivalence or worse rule, threshold and uncertainty criterion; hard-floor rejection rule
- Intent attribution: excluded from inference; any separate evidence question identified without claiming this experiment answers it
- Authorization references: synthetic/public inputs, route eligibility, counsel gate, permitted interfaces, already-provisioned entitlement, usage/spend/time ceilings and stop owner

### A2 Population, fixtures and matching

- Task-family sampling frame and selection rule; inclusion/exclusion criteria fixed before outcomes; instance/repeat identifiers and expected family coverage
- Source/fixture versions and hashes; required capability set; acceptance rubric and independent evaluator/version
- Each route's direct baseline and practical optimized baseline; development-tuning dataset separated from confirmatory dataset
- Match manifest from Section 6; unresolved differences and resulting limits on causal interpretation
- Cold/warm/loss/no-future-work allocation; source-fork variants; state-building horizon and observed-use amortization rule

### A3 Endpoints and records

- Primary endpoints selected from the dictionary, each with native unit, denominator, direction, minimum meaningful effect, uncertainty method and observability requirement
- Secondary/exploratory endpoints and multiplicity family; no silent promotion after outcomes
- Per-provider field algebra and inclusion/overlap graph; quota bucket/reset/rounding/freshness rules; conditions under which debit is unknown
- Human activity taxonomy, timing method, overlapping-work rule, reviewer blinding/adjudication and operator training
- Lifecycle/attempt/helper graph; source provenance; missing-report reasons; lower-bound and reconciliation policy
- Cell epistemic status: measured / modelled / unknown; modelled assumptions and sensitivity ranges; no unknown-to-zero coercion

### A4 Allocation, power and analysis

- Randomization unit and independent-unit definition; pairing/blocking; task-family, shared-window and adaptive-sequence dependencies
- Randomization generation, concealment, order balance, carryover prevention, seed/manifest and deviations policy
- Independent-unit sample size/allocation and repeats; power/precision objective; effect/margin rationale; variance/correlation/failure/missingness inputs and sources
- Exact estimator/test/interval method; clustering/crossed-effects treatment; distributional assumptions, diagnostics and prespecified fallback
- Assigned-cohort and accepted-output ratio estimands; failure/partial/cancellation treatment; no-success denominator handling
- Missingness analysis and defensible bounds; treatment of mixed modelled/measured totals; sensitivity condition that would reverse the decision
- Multiplicity/confidence policy; equivalence/worse criteria; heterogeneous route/condition claims and any prespecified population weights

### A5 Stops, exclusions, amendments and release

- Fixed sample/horizon or valid sequential rule; authorized ceilings; delayed-receipt deadline; early safety stops; no peeking-until-win
- Pre-dispatch exclusions versus post-assignment events; all exclusions retained in flow/resource ledger; independent adjudication
- Effect settlement and retry/recovery policy; no replay of unknown effects without resolution; outstanding work at stop
- Hard-floor checks and single-failure scope; reviewer required to resume; any eligibility/authentication change requires new approval
- Immutable output manifest; raw evidence retention/privacy rule; source/host/version drift; new experiment versus reanalysis rule
- Result categories and required reporting including unfavorable, null, missing and stopped cells; independent acceptance signature

## Appendix B. Reusable endpoint and accounting schemas

These are logical records, not a choice of language, database, transport or harness implementation. They align with the R-B minimal accounting contract and R-A porting-cost vocabulary.

### B1 Endpoint definition record

Required fields: endpoint_id; name; estimand; applicability; unit; denominator; aggregation_scope; favorable_direction; evidence_class; observability_surface; raw_field_names; inclusion_algebra; overlap_group; measurement_precision; freshness_requirement; missingness_rule; comparator_id; meaningful_threshold_ref; analysis_ref; does_not_prove; source_snapshot_ref.

### B2 Attempt/accounting record

Required fields: schema_version; experiment_id; block_id; task_family_id; task_id; episode_id; work_unit_id; attempt_id; parent_attempt_id; sequence_id; repeat_id; operator_ref; route_profile_id; binary/schema/docs_version; requested_model_ref; served_model_ref; effort_ref; account_window_ref; authority_grant_ref; authority_epoch; lifecycle_timestamps; admission_state; terminal_status; terminal_reason; helper_role; helper_coverage; cancellation_requested; cancellation_acknowledged; observed_completion; independently_accepted_completion; effect_settlement; raw_evidence_refs; resource_counters.

Each resource counter contains: endpoint_id/kind; value (number or null); unit; epistemic (measured/modelled/unknown); scope; source_ref; timestamp; precision; included_attempt_ids or aggregate_scope_ref; excluded_roles; coverage_state; missing_reason; inclusion_algebra_ref; overlap_group; lower_bound if justified; model_assumptions_ref when modelled. Unknown helper identities mean helper coverage unknown, not an empty list that implies none. Redacted public copies may use opaque IDs; the private linkage remains access-controlled.

### B3 Human activity and porting record

Human activity: activity_id; episode/port/attempt links; actor_role and opaque actor ID; start/end; active/elapsed classification; category; correction/re-prompt ID; shared-time allocation; evidence_ref; epistemic; reviewer verdict link. Porting adds source/destination profile; required capability set; port class; cost category; shared-investment pool; observed amortization count; handwritten/generated glue distinction; API touchpoints; authority translations; conformance defects; semantic/permission/evidence losses; maintenance release; abandoned reason.

### B4 Aggregate integrity rules

- Every assigned episode exists even if never admitted; every admitted request links to an attempt or an explicit orphan entry
- No parent-plus-child double counting: either reconcile component amounts into a total or preserve a cumulative total with covered IDs; do not sum both
- Native token algebra is versioned; output-plus-reasoning and input-plus-cache are not assumed disjoint
- Unknown cells cannot enter arithmetic as zero; report known subtotal and unknown residual
- Every accepted outcome links to an independent verdict and settled or explicitly safe-blocked effects
- Each quota delta links to compatible timestamped bucket snapshots and an interference assessment
- Native/provider cache and owned-reuse identities remain in separate ledgers; neither licenses or validates the other

## Appendix C. Primary-source register

All sources retrieved 2 October 2026. Public documentation is mutable; a future run must preserve its exact relevant schema/document snapshot and version. Retrieval establishes what the cited public page documented on the research date, not that a local installation conforms. No source below is empirical evidence of Recursion performance.

- **S1 — OpenAI, Codex App Server.** Thread token-usage notifications; account rate-limit buckets and reset fields; separate account usage fields. https://learn.chatgpt.com/docs/app-server
- **S2 — Anthropic, Manage costs effectively.** Estimated local costs versus billing, subscription usage and main-only cache statistics. https://code.claude.com/docs/en/costs
- **S3 — Anthropic, Prompt caching.** Explicit input/cache read/cache creation algebra. https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- **S4 — OpenAI, Prompt caching.** Cache scope/lifetime and counter semantics; cache clearing limitations. https://developers.openai.com/api/docs/guides/prompt-caching
- **S5 — OpenAI, Reasoning models.** Output/reasoning accounting and incomplete responses without visible output. https://developers.openai.com/api/docs/guides/reasoning
- **S6 — Cursor, Output format.** Structured CLI result/lifecycle and absent final JSON on failure. https://cursor.com/docs/cli/reference/output-format
- **S7 — Google, Gemini CLI observability.** Token types, API requests, compression and retry metrics. https://geminicli.com/docs/cli/telemetry/
- **S8 — Google, Gemini CLI quotas and pricing.** Authentication-dependent quota/pricing and session statistics. https://geminicli.com/docs/resources/quota-and-pricing/
- **S9 — Anthropic, Monitoring.** Token counter categories and main/subagent/auxiliary attribution. https://code.claude.com/docs/en/monitoring-usage
- **S10 — xAI, Grok Build changelog.** Versioned headless/persisted token and cost reporting, including 0.2.97 and 1.0.14 entries. https://x.ai/build/changelog
- **S11 — Nous Research, Hermes CLI interface.** Native usage/context displays and distinction between provider anchors and estimated breakdowns. https://hermes-agent.nousresearch.com/docs/user-guide/cli/
- **S12 — Google, Antigravity quota UI and plans.** Model quota display and workload-sensitive mutable limits. https://www.antigravity.google/docs/cli/commands/usage and https://antigravity.google/docs/plans
- **S13 — OpenCode, CLI reference.** Native session/run/fork, statistics and JSON export surfaces. https://opencode.ai/docs/cli/
- **S14 — NIST/SEMATECH, Randomized block designs.** Blocking known nuisance factors and randomization. https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm
- **S15 — ICH E9(R1), final guideline, 2019.** Advance specification of estimands, intercurrent events and sensitivity analysis. Applied here by analogy, not as clinical regulation. https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf
- **S16 — Pi, RPC command documentation.** Session-stat inclusion, custom compaction usage and context-estimate limitations. https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/rpc-commands.md
- **S17 — Lakens (2017), Equivalence Tests: A Practical Primer.** Prespecified equivalence bounds and why nonsignificance does not establish absence. Social Psychological and Personality Science, 8(4), 355–362. https://pure.tue.nl/ws/portalfiles/portal/80918653/lakeequi2017.pdf

- **S18 — Google, Antigravity headless mode.** Cumulative session metadata and soft-denial exit semantics. https://antigravity.google/docs/cli/headless/

- **S19 — Cursor, TypeScript SDK.** Reported-turn live usage versus billed agent records, delayed cost settlement and plan-included charge semantics. https://cursor.com/docs/sdk/typescript

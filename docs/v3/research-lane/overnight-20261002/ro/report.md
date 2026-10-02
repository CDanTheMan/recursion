# R-O — Backend performance and configurability engineering

Status: research proposal; no component selection, performance result, numeric acceptance budget or route qualification

Research date: 2026-10-02 UTC. Repository baseline: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. Parent goal: `goal-recursion-v3-harness-orchestrator`.

## Decision-ready findings

The useful output is a **falsifiable measurement contract**, not a fastest-language recommendation. Preserve the accepted comprehensive release and compare its complete enabled and disabled configurations. Residency, durability, language, presentation and isolation are independent design axes; a fast isolated component cannot establish that the assembled product is responsive, economical or recoverable.

The proposed program has four decision artifacts beyond OR-024: a profile/regime budget register with explicit unknowns; an immutable workload and comparison identity; a complete-profile/integration-tax matrix; and an independently checked result classifier. All target fixtures are **UNEXECUTED**. Numeric performance cells are `null`, including capacity, porting savings and observer overhead. No hidden weighting produces an overall score.

The most discriminating early work is: validate counter/oracle sensitivity; prove installed-disabled paths inert; compare complete demand-activated and bounded-resident profiles under the same durability and authority contract; then test persistence, configuration propagation, slow observers and review-limited admission together. Freeze winners only after a held-out whole-profile confirmation. A result favoring a cheaper default does not remove a D-019 capability.

The literal R-O-G05 requirement to **prove** inertness and **measure** integration cost cannot be closed by this research-only task. It receives a bounded-unknown answer and exact fixtures O-F03/O-F04/O-F14. Likewise no profile budget is numerically accepted. All 14 questions and 10 gates are mapped in `coverage.json`; coverage is not implementation acceptance.

<a id="ro-s0"></a>

## S0 — Authority, evidence and current-source reconciliation

Evidence classes used throughout:

- **SD-public:** the cited primary public source documents a mechanism, not Recursion behavior
- **SD-repository:** the pinned repository states a requirement, design or recorded result
- **LO-record:** static inspection of existing implementation or evidence bytes; no rerun
- **Proposal:** original Recursion design or experimental inference in this report
- **Unknown:** no qualifying measurement or accepted decision exists

D-018/D-019/D-020/D-022/D-024/D-028–D-033 control the scope. Native-loop ownership remains first-class; an upstream SDK loop is not the native harness. Upstream-only execution must account for every reasoning role without a hidden native planner, compactor or recovery model. Core has a fenced single writer and availability seam; automatic takeover is an opt-in first-party remote/full capability. It is not default consensus. Hermes executive authority is retired.

The current instruction is TUI first, GUI later. D-019 also requires GUI among built opt-in first-release capabilities, while older PRODUCT/INTERFACE-STRATEGY prose excludes it from the initial contract. This report uses TUI-first construction, a common backend and GUI-off measurement arms; the exact release-timing interpretation remains explicitly flagged for the Owner. It does not choose a smaller release or reopen D-019.

### S0.1 — What static inspection actually establishes

| Pinned evidence | Observation of records | Limit on use here |
|---|---|---|
| `scripts/v3/planning/replay/kernel.py`: `_record`, `_sealed_state`, `genesis` | The inspected pure M1A implementation searches record lists and copies/sorts projection state | Candidate sensitivity dimensions are history length, active objects, copying and serialization; this is not a bottleneck measurement or a reason to replace Python |
| `scripts/v3/planning/validation/canonical.py`: `canonical_bytes`, `decode`, `validate_policy_fixture` | The implementation has a bounded integer-only canonical subset and an M1A-specific current-immediate policy contract | Do not equate it with a complete new configuration resolver, complete RFC-8785 numeric implementation or D-022 qualification; do not change frozen M1A to make a benchmark easier |
| M1B `reference_oracle.py::evaluate_disabled`, `replay_broker`; fixture `F-M1B-015`; adversarial test `test_output_that_spells_command_remains_untrusted_data` | Disabled activity fields are constructed as zeros; the broker oracle checks and returns supplied activity counters. The command-looking payload test is an inert fixture transformation | Schema/oracle conformance, not observed runtime inertness. PERF-003 must use independent import/process/network/timer and other tripwires; constant fixture zeros cannot become measured counters |
| FU-03 `results/summary.json`, `results/mutants.json` | Reduced-bound baseline receipt and seven instantiated mutant records exist; five are recorded killed and two not killed within bound | Not the complete 36-mutant or full integrated gate; incidental type failures do not prove intended safety sensitivity |
| FU-04 `traces/traces_results.json` | Thirteen recorded runs contain twelve pass and one unknown; the unknown PF11 is a WSL dev/test pressure case | No native production profile qualification; unrun catalog cells stay unrun; this report executed none |
| `PERFORMANCE-PLAN.md`, `GAPS.md`, FU-01/02/05 syntheses | Workloads and designs exist; current GAPS prose partly predates bounded FU-03/FU-04 receipts | Preserve those receipts without turning them into language, persistence, broker or capacity wins |

D-028 platforms are the native Windows 11 25H2/build 26200 Home/Pro floor plus 24H2/build 26100 Enterprise qualification, x64 primary; Linux 6.12 LTS primary and 6.6 LTS compatibility minimum with cgroup v2, local ext4; local NTFS for Windows canonical state. WSL2-ext4 and WSL2 `/mnt/c` are separate dev/test cells, not production evidence. SMB/NFS canonical storage and physical-platter power interruption remain out of scope. The accepted abrupt-VM-reset promise still requires an authorized disposable rig and matching replay evidence.

### S0.2 — Narrow public-source findings

These are the only concentrated public-source summaries in this report. Later sections apply original Recursion proposals to these mechanisms, rather than repeating vendor documentation. Exact URLs, source identities, retrieval date and hash limitations are in `source-register.json`.

| ID | Source-documented fact and resulting measurement obligation |
|---|---|
| <a id="python-free-threading-facts"></a>O-S01 | CPython's free-threaded documentation describes different threading behavior and memory reclamation, including delayed release. Treat GIL/free-threaded and extension topology as separate arms; infer no local winner. [Python documentation](https://docs.python.org/3/howto/free-threading-python.html) |
| O-S02 | Go's GC guide describes a soft runtime memory limit and memory outside runtime accounting. A runtime heap limit is not a whole-process or process-tree hard ceiling. [Go GC guide](https://go.dev/doc/gc-guide) |
| O-S03 | Rust documents ownership-based memory management. This does not provide a Recursion tail-latency, cancellation, allocation or packaging result. [Rust ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) |
| O-S04 | SQLite WAL has checkpoint/read-lifetime interactions, auxiliary persistent state and durability-sensitive synchronization choices. Pin these, include all bytes and test reader starvation; WAL does not establish authority fencing. [SQLite WAL](https://www.sqlite.org/wal.html) |
| O-S05 | RFC 7464 specifies JSON text-sequence framing and parsing behavior. It does not supply transactions, commit acknowledgements or crash durability for a segmented log. [RFC 7464](https://www.rfc-editor.org/rfc/rfc7464) |
| O-S06 | Source premises: [R-E’s cgroup note](../re/report.md#linux-cgroup-facts). CPU, memory and I/O observations need an identified membership boundary and collector semantics before workload attribution. |
| O-S07 | Linux PSI measures resource-stall pressure, including per-cgroup interfaces. A supported kernel interface is not evidence that a particular deployment exposes usable pressure observations. [Linux 6.12 PSI](https://docs.kernel.org/6.12/accounting/psi.html) |
| <a id="job-query-facts"></a>O-S08 | [Job Object premises](../re/report.md#windows-job-facts). QueryInformationJobObject exposes class-specific records. Establish membership and class semantics before attributing resource use. [Query API](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject) |
| O-S09 | Linux CPUFreq makes power/performance policy a real environmental variable. Requested frequency need not equal actual frequency. [Linux 6.12 CPU performance scaling](https://docs.kernel.org/6.12/admin-guide/pm/cpufreq.html) |
| O-S10 | Windows timer-resolution requests can affect scheduling and power saving; visibility affects their guarantees on Windows 11. Capture timer policy and foreground/occluded state, rather than assuming identical idle conditions. [timeBeginPeriod](https://learn.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timebeginperiod) |
| O-S11 | Source premises: [JCS](../rl/report.md#jcs-facts) and [JSON Schema](../rl/report.md#json-schema-facts). Neither decides Recursion’s merge, authority or propagation semantics. Reuse R-L Q05/Q11’s canonical configuration discussion. |
| <a id="otel-bounds-facts"></a>O-S12 | OpenTelemetry metrics specifies cardinality/overflow handling; its trace batch processor may drop spans after its bounded queue fills. Optional telemetry is therefore not the durable evidence oracle. [Metrics SDK](https://opentelemetry.io/docs/specs/otel/metrics/sdk/), [Tracing SDK](https://opentelemetry.io/docs/specs/otel/trace/sdk/) |
| O-S13 | Use [R-G’s activation and lifecycle premises](../rg/report.md#vscode-activation-facts). They do not establish installed-disabled Recursion inertness; qualify that invariant independently. |
| O-S14 | Named pipes provide buffered communication and security checks; locally intended pipes require attention to remote accessibility. A transport alone supplies neither the broker protocol nor bounded control latency. [Windows named pipes](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipes) |
| O-S15 | NIST distinguishes screening from comparative and response-surface designs. Screening can reduce an experiment, but it does not certify untested interactions. [NIST experimental design](https://www.itl.nist.gov/div898/handbook/pri/section3/pri33.htm) |

R-E owns credential-boundary comparisons; R-F owns route mechanics/counters; R-G owns import semantics and port-cost definitions; R-K/R-L own terminal/interface contracts; protocol-edges owns MCP revision-specific semantics. They are research companions, not qualified implementations. Cross-references use semantic question/fixture IDs because those drafts can be edited.

<a id="ro-s1"></a>

## S1 — Q01: One full optimization vector

Proposal: each comparison is an array of separately typed outcomes below, plus floor verdicts. Default preference order is **responsiveness, then subscription efficiency, then task completion**, subject to correctness, authorization, privacy, effects, quality, resource and recovery floors. This is an ordered decision discussion, not a license to hide costs or choose a material tradeoff automatically.

| Vector component | Required measurements/observations | Denominator and interpretation |
|---|---|---|
| Authority/safety/privacy/effects | Violations, stale dispatch, ambiguous effects, forbidden disclosures, isolation/refusal sensitivity | Exact admitted operation and fault corpus; one valid hard-floor counterexample rejects the arm |
| Verified quality | Accepted gates, escaped defects, disagreement, downstream correction, evidence validity | Unique tasks; failed, abandoned and censored tasks retained |
| Recovery/replay | Canonical parity, acknowledged-data preservation, reconciliation, productive continuation | Fault instance and unique task; an open database is not recovered useful work |
| Owner/operator cost | Active review time, intervention count, error/comprehension probes, backlog age, correction time | Review obligation and unique task; waiting and active review separately |
| Quota/tokens/money | Native observed quantity, explicit subscription-window delta, metered receipts | Separate units and sources; no currency conversion across these columns |
| Context/cache | Local reads/writes, reused content, invalidation, required-field fidelity, exposed route counters | Cache tier, access scope and route epoch; no provider benefit inferred from a local hit |
| Latency/throughput | Control/input/append/task/recovery distributions and accepted throughput | Wall-clock experiment exposure and scheduled unique tasks, not only successful completions |
| Host resources | CPU time, residency/commit, disk logical/allocated, I/O, network, wakeups, processes, handles | Whole declared workload tree plus separate host/co-tenant observation |
| Terminal interaction | Frame/input tails, gaps/flicker, Unicode/input/accessibility errors | Sink profile, view count, drain rate and focus state |
| Portability/configurability | Required platform cells, typed refusals, edit/migration errors, explainability, owner change cost | Complete configuration/profile identity and user task |
| Code/maintenance | Privileged and total code, dependency closure, artifact/install size, upgrade effort, defect evidence | Same required capability contract; source lines alone are not maintainability |
| Extensibility/idle | Disabled execution traps, metadata cost, plugin lifecycle/residency, optional observer cost | Absent/installed-disabled/enabled-idle/active/retired states separated |

Every metric includes value, unit, semantic definition, source class, scope, interval/clock, collector revision, availability reason, uncertainty and evidence reference. Unknown numerator or denominator yields a null ratio with the reason. An observed zero denominator makes the rate undefined, not infinite efficiency. Explicitly observed zero events is a value only when observation coverage and sensitivity are demonstrated.

A passing candidate must remain within every adopted ceiling and floor. A non-dominated candidate that improves response time but raises review debt or resource use is escalated with both vectors. More accepted features, higher activity and more parallel tasks are not proxy wins.

<a id="ro-s2"></a>

## S2 — Q02: Bounded screening and complete architectures

### S2.1 — Screening order and mandatory interaction closure

Proposal O-R01: compare in layers against a fixed semantic corpus instead of a Cartesian product. Competitor: full-factorial testing of every setting. The staged design spends less evaluation work only if held-out complete profiles reproduce its conclusions; missed adverse interactions falsify that claim.

1. **Evidence readiness:** settle exact corpus/refusal/Stop identities, current pins, collector sensitivity, privacy scope, hardware identity and unexecuted-versus-recorded evidence. Missing required semantics blocks affected arms.
2. **Deterministic floor screen:** canonical bytes, admission/replay, config accept/reject, plugin inertness, fence and accounting fixtures. Do this before timing and without a provider.
3. **Controlled component contrasts:** FU-01 runtime arms; FU-02 store arms with common artifact corpus; FU-05 broker choices; configuration resolver arms; plugin lifecycle; fixed/adaptive admission; telemetry modes. Each comparison changes only declared factors.
4. **Risk-based interactions:** always include runtime×serializer, store×reader age×checkpoint, broker×sink drain×control reserve, config propagation×Stop×reconnect, plugin reload×epoch, observer×storage pressure, adaptive admission×review service rate, and accounting×retry/fork/recovery. These are required, not omitted by pairwise generation.
5. **Complete profile confirmation:** evaluate lean, installed-disabled, native-only, upstream-only stand-ins, combined, remote and presentation arms below on independently frozen held-out tasks. Re-run all applicable floors after stress and recovery.
6. **Later authorized real-route stage:** only a separately admitted route-qualified trial can establish subscription/cache/quality economics. This report supplies no authorization or executable live-route recipe.

A screen excludes invalid candidates, not inconvenient failures. Keep an excluded-arm ledger with the violated floor, witness and scope. An unmeasured interaction stays uncovered; no covering-array count means safety completeness. New high-order failure expands the interaction set and requires a new freeze, rather than silently discarding the failed cell. Screening sample sizes and confirmatory sizes remain unknown until a blinded pilot/power or precision design is approved.

### S2.2 — Residency and persistence are orthogonal

Compare these architectural arrangements under the same canonical owner, accepted features, authority/recovery semantics and workload:

| Arrangement | Potential benefit to test | Complete costs and failure modes to retain | Decisive discriminator |
|---|---|---|---|
| A: demand-activated optional services | Lower residency while quiet | Spawn/handshake/cold-cache latency, retry/recovery rehydration, churn, launch-boundary cost | First-use bursts and intermittent workloads including time until productive task continuation |
| B: bounded resident session hub/warm pools | Lower repeated first-use latency | Baseline residency, timers, stale sessions, peak co-residency, eviction, pool ownership | Same intermittent trace with identical session affinity and cold-loss recovery |
| C: A or B plus durable workflow assistance | Less bespoke timer/retry/recovery coordination | Journal writes, extra schema/state, process and dependency closure, duplicated retry ownership, replay/upgrade costs | Hold residency fixed; inject ambiguous delivery, crash, update and stale epoch; compare useful recovery and maintenance work |

The canonical writer, authority and durable receipts are common to all arms. C's auxiliary journal is not a second authority or a replacement for the native loop. Any two independent retry owners or re-created authority after recovery eliminates an arm before speed comparison. No-benefit: confidence does not establish a practical gain or the supposed benefit is already provided by the baseline. Regression: a warm profile increases idle residency or a journal increases recovery complexity beyond an adopted ceiling, even if one tail metric improves. A pass proves only the frozen workloads and profiles, not universal topology superiority.

### S2.3 — Complete enabled/disabled configurations

Each row names an entire locked release/configuration, not a feature flag applied to an unknown installation. Synthetic route/process stand-ins carry no provider authentication.

| Profile ID | Complete arm and contrast | Required proof/cost |
|---|---|---|
| O-P0 | Lean core with no optional payloads present | Adapter-free boot, status, canonical replay and Stop; full core install and recovery cost |
| O-P1 | Same core plus full first-party payload bundle installed, all optional capabilities disabled | Bounded core-owned catalog metadata delta; no plugin imports, payload scanning, credentials, processes, watchers, network, context enumeration or model work |
| O-P2 | Upstream-only supported workflow stand-ins | All reasoning-role bindings explicit; no native helper inference; launch, parsing, steering, Stop, continuity and ledger costs |
| O-P3 | Native-only workflow stand-ins | Recursion-owned native loop control path and all helper role accounting; no required upstream SDK loop |
| O-P4 | Combined rich profile with each required compatible capability enabled | Same useful workflow/gates; cumulative startup, idle, active, persistence, operator and maintenance costs; conflicts produce typed refusal |
| O-P5 | Remote execution with availability plugin off versus explicitly on | Transport/hydration/reconciliation and replication/election overhead separate; core fence remains; no consensus dependency in O-P0 |
| O-P6 | O-P0/P2/P3/P4 with passive TUI views, then optional GUI closed/open/occluded | Common backend identity, view overhead, cold detach/reattach, bounded buffers and no observer-triggered model or index work |
| O-P7 | Custom constrained profile with plugin conflict, unsupported route field and pending update | Requested/effective discrepancy explainable; no silent feature activation, fallback, authority expansion or swallowed configuration |

O-P4 means all **compatible declared** capabilities of that manifest, not an impossible union of mutually exclusive plugins. Every incompatible combination remains an explicit supported refusal. Measurement crosses these semantic arms with the three target hardware classes, applicable platform floors and declared regimes; risk screening reduces tuning permutations, never removes a required release capability.

<a id="ro-s3"></a>

## S3 — Q03: Integration tax, lifecycle and release packaging

Proposal O-R02: maintain a vector-valued marginal cost ledger for each plugin/route and for the complete bundle. Admissible competitor: independently measured whole-profile totals with attribution, rather than a paired lifecycle-delta ledger; both retain the full dependency and work closure. Startup-only and lean-only accounting are negative controls, not eligible competing evidence designs. Falsifier: an included dependency, background worker, helper inference call, install byte or review hour disappears from attribution.

Lifecycle contrasts are **absent → catalog-known → payload-installed-disabled → admitted/enabled-idle → active → drained/retired-with-evidence**. The core may read bounded release metadata needed to explain absence/compatibility. That is attributable metadata cost, not literal zero global overhead. Disabled plugin code and its dynamic schema/tool/context enumeration must not run. Installing a full bundle must not make a disabled heavy dependency an implicit boot dependency.

For each contrast record startup distribution; CPU time and wakeups over the declared idle window; current/peak residency and commit; handles/processes/threads/timers/watchers; files opened/read/written; logical and allocated disk bytes; network attempts/bytes; context injected; model/helper invocations; native quota reservations and observed debit; shutdown/reload/recovery; explanation/edit/review/upgrade effort. Subtract paired comparable observations only, preserve uncertainty, and retain the absolute totals beside deltas. Negative deltas are observations, not free capability.

For plugins i and j, compare observed combined cost against the individually measured deltas as an **interaction diagnostic**, not an additive budget guarantee. Dependency sharing, cache reuse and contention can make the interaction positive or negative. Plugin count is a workload parameter, not a predictor of cost. PERF-003/EXP-FHAR-09's 0/10/100 installed-disabled arms remain historical workload cardinalities, not performance thresholds; include a shared-dependency bundle and malformed/oversized metadata case.

Static evidence warning: M1B’s `evaluate_disabled` supplies expected zeros rather than collecting runtime activity; `M1B-EXECUTION-CONTRACTS.md` explicitly bounds acceptance to sanitized in-memory fixtures. This is a useful contract oracle, not a product observation. O-F03 must not accept those zeros as measurements.

The disabled-path fixture uses independent traps for code import/entrypoint, dynamic enumeration, subprocess/thread/timer/watcher, credential reads, model-call requests, quota reservations, egress attempts and event subscription growth. Synthetic positive controls deliberately activate one trap at a time. A trap that cannot observe its positive control makes the result inconclusive. No model is invoked even in a positive control: it records an attempted call at a synthetic denying endpoint. Inspect the package/dependency closure as well as the trace. A clean dynamic window cannot prove universal inertness under every input.

### S3.1 — Porting and maintenance economics

Reuse R-G Q09's import-versus-native-rewrite cost accounting. Add this backend comparison: same independently accepted behavior/loss contract, initial implementation and translation effort, review, test/negative-control effort, dependency/license handling, two declared upgrade/revalidation scenarios, support/diagnosis effort, runtime lifecycle cost and rejection/rework. Unit is an independently accepted port or equivalent rewrite, not lines changed or imported packages. Failed ports and unacceptable losses remain in the denominator. If no port is acceptable, porting benefit is unknown/absent for that corpus; the accepted-count observation can be zero without turning missing effort data into zero. D-033 cheap porting remains a hypothesis.

### S3.2 — Distribution is not activation

Compare a lean signed closure with opt-in payloads, a full offline first-party bundle with disabled payloads, and custom locked closures. A single executable and a multi-artifact self-contained closure remain competing packaging options, not selections. Report transfer bytes, unpacked/allocated bytes, installation time, required runtime/native dependencies, privilege needs, offline boot/recovery, upgrade/rollback retained bytes, antivirus/signature-check conditions, support matrix and reproducibility evidence. Count both a tiny launcher and everything it requires to work.

All D-019 capabilities must have built artifacts, manifests, documentation, conformance evidence or an explicit unresolved release blocker. Cost concerns can motivate better activation, placement or defaults; they cannot silently become missing features. Installing full does not grant sovereign authority. Availability, research, GUI, indexing and telemetry exporters remain separately activated. A packaging pass cannot establish license clearance, security, route entitlement or runtime resource benefit.

<a id="ro-s4"></a>

## S4 — Q04: Profile budgets and headroom

`budget-register.json` contains the complete cross-product of three target profiles, six regimes and the metric families below. Each numerical ceiling, measured baseline, practical margin and accepted result is null. The register is a contract to fill from evidence, not a claim that numbers were measured.

### S4.1 — Three profile contracts

| Profile | Current identity | Required measurement before accepting it |
|---|---|---|
| Coordinator-small | Historical 2-vCPU/4-GB class target, not a capacity point | Actually available CPU entitlement/competition, memory/commit, disk/free allocation, I/O and control/recovery latency; reserve writer, authority, Stop, observer and recovery capacity before admitting optional work |
| Interactive workstation | Historical 32-logical-processor/64-GB class observation, not a requirement or guarantee | Actual occupancy, foreground/occluded interactions, competing build/index/harness processes, input/render tails, total process-tree resources and review service rate |
| Registered worker | No fixed hardware assumption | Declared job envelope, available resources, sandbox/membership, transfer/hydration, result/reconciliation and loss recovery; coordinator cost measured separately and in total |

A hardware label, SKU, logical-CPU count, memory total or historical free-memory receipt cannot qualify a current profile. Re-measure after material host/build/runtime/configuration/accounting changes, before a gate, and when drift invalidates the frozen envelope. Rechecking means read-only measurement in a later authorized local session, not a current host action.

### S4.2 — Derivation rule, not an invented number

A budget entry binds: profile and regime; metric/unit; exact start/end and process/artifact boundary; baseline evidence; Owner ceiling; practical improvement/noninferiority margins; uncertainty method; derived reserve; safety reason; reviewer; expiry/requalification trigger. Baseline performance does not automatically become an acceptable product ceiling. First establish admissible floors, measure baseline and stress/recovery demand, then ask the Owner to adopt the ceiling and practical margins before confirmatory outcomes.

For a resource r, proposed admission arithmetic is: usable envelope = measured available capacity minus separately reserved integrity, recovery, co-tenant and uncertainty allowances. Each allowance needs non-overlapping accounting or a documented shared-reserve rule. Admission is refused when projected marginal demand exceeds this envelope; an unknown required term blocks automatic expansion. CPU, memory, disk, process handles and review are separate constraints, not summed.

Headroom must cover both steady use and worst declared transient overlap: checkpoint + active writes, snapshot + old release + new release, replay + projections, artifact hydration + bounded queues, or failover + reconciliation. A disk/WAL gate must reserve bytes to commit refusal/checkpoint/recovery evidence before admitting more growth. A free-disk percentage alone cannot protect against a single artifact larger than that reserve. Count reserved quota and competing filesystem users where visible; missing visibility is an uncertainty reason.

PERF-001 contains a **25% RAM/disk headroom preregistration clause**. Preserve its provenance; it is neither new R-O advice nor a measured/independently accepted value. Its denominator, applicable resource pool, transient demand and relationship to current Owner ceilings must be revalidated before it becomes a gate. No percentage for RAM, disk, WAL, CPU or review is selected here. A baseline that cannot leave the adopted integrity/recovery reserve is inadmissible, even if it is the fastest observed arm.

<a id="ro-s5"></a>

## S5 — Q05: Regimes, metrics and latency meanings

All regimes collect the full applicable vector. Non-applicable is explicit with reason; unknown is not non-applicable.

| Regime | Exposure and distinguishing observations | Budget derivation / failure signal |
|---|---|---|
| Idle | Booted quiescent core; enabled-idle separately; zero then passive views; bounded metadata changes | CPU time per wall interval, wakeups if observable, memory slope, process/handle/timer count, disk/network growth; optional surprise work violates inertness regardless of small cost |
| First-use | Cold process/start plus first admitted feature; warm process separately; explicit cache-state label | Start-to-model-free-control, first-use activation, ready-to-input, first durable receipt and useful-work latency; cold/warm never silently pooled |
| Steady | Frozen open-loop arrival schedule and corpus after declared warm-up | Accepted throughput, p50/p95/p99 defined below, queues and resource slopes; no saturation knee or safe load claimed without measurement |
| High-output | Fast stream, slow/stalled sink, fan-out/views, large bounded artifacts | Writer/control isolation, queue bytes/count/age high water, coalesced presentation counts and gaps; durable loss is categorical failure |
| Recovery | Clean/dirty stop, restart, detached view, lost session and restoration | Detection → safe admission readiness → reconciled authority → first useful verified continuation; all recovery work and backlog drain counted |
| Fault | Frozen required fault matrix and paired no-fault controls | Oracles first; fault-triggered evidence, data/authority parity, Stop availability, containment and bounded resource behavior; no performance ranking for floor-failing arm |

Define timestamps before collection:

- **Control:** authorized command issued → durable acceptance/refusal; also acceptance → receiver observation, and observation → settled/unresolved disposition. Report these separately, especially for Stop
- **Input:** user/synthetic input available at ingress → backend command acceptance and separately rendered feedback; include waiting behind output
- **Append:** canonical append request → committed/durable acknowledgement under the declared durability promise; distinguish queue wait from service/flush time
- **Task:** scheduled arrival → independent verified useful result; queue, helpers, retries, review and downstream correction remain visible. Report abandoned/censored exposure and outcome separately
- **Recovery:** injected fault → detection, replay readiness, safe authority, reconciled effect state and productive continuity; report each stage rather than just process-start time

For each latency record empirical p50/p95/p99, sample count, independent-task count, exposure, uncertainty, timeout/censoring count and quantile estimator. Quantiles that cannot be resolved at the frozen exposure stay null or explicitly interval-censored; a success-only p99 is not an all-task guarantee. Attempts/messages are nested measurements. Throughput is independently accepted unique tasks per full observation time; report generated and reviewed output separately.

Every queue has a named owner, count **and byte** limits, oldest age, outstanding credits, high-water observation, rejection/block/reset behavior and a reserved control route. Canonical event loss must remain distinct from presentation coalescing, optional trace drop, intentional retention expiry and disconnected replay gaps. None can be relabeled “dropped logs” to obscure canonical loss.

Required fault cases retain the preregistered duplicate command, stale lease, disk-full threshold, reader crash, writer crash and corrupted artifact reference, plus cold/warm starts and clean/dirty shutdowns. Remote arms add disconnect-before-send, ambiguous send, duplicate result and stale fencing epoch. Add pressure during config propagation, telemetry failure, slow observers and review pause because they expose interaction failures, not because every knob needs full factorial testing.

<a id="ro-s6"></a>

## S6 — Q06: Integrity, capacity and review debt under pressure

Proposal O-R03: emergency control and canonical integrity have separately bounded admission/queue/resource paths. Admissible competitor: one bounded transport/queue with enforced logical control reservation and independent bounded scheduling, rather than physically separate control paths. An unreserved common saturation policy is a negative control. The discriminator is pressure with a slow reader and concurrent Stop, not unloaded throughput.

Canonical intent and receipts commit through one fenced writer before dependent dispatch/presentation. Coalescing is allowed only on projections after canonical admission; it cannot skip an append. Keep writer, work, process, configuration, release and pause epochs distinct and validate the appropriate current fence at each irreversible boundary. A writer lock is not an authority lease. Receipt delivery is not external settlement.

Aggressive Stop fences further selected-agent dispatch and requests immediate interruption; Full includes owned descendants/monitors/relaunchers; Lazy closes admission and reaches the named observable boundary with its declared deadline/escalation. `checkpoint`, `interrupt` and `drain` remain distinct operations under D-022. A stopped PID or socket does not roll back an external effect. Unreachable nodes and ambiguous sends remain unresolved, with reservations retained according to the recovery ledger. Optional telemetry and presentation may shed work; authority, Stop, required evidence and canonical append must survive the admitted pressure profile. Durable-event loss or unavailable PAUSE is an automatic failure.

### S6.1 — Adaptive admission includes a human queue

Proposal O-R04 compares DS-06's independently derived integer credits M/P/G/R/H against an Owner-set fixed-limit policy using identical input and review-service traces. All policies preserve resource, authority and quality floors. `admission = min(machine, pool, goal, review, Owner ceiling)` is meaningful only after each unlike quantity is converted into a **conservatively calibrated slot credit**. Do not take the numerical minimum of bytes, tokens and minutes.

Maintain queue openings, independently closed review obligations, outstanding count, age distribution, active review time, rejected/reworked outputs, changed-byte/file/binary indicators and integration conflicts. Machine size never creates review credit. Reserve synthesis, verification and recovery before discovery. A pause in reviewer service, vacation-like gap or downstream correction burst must reduce expansion even on an idle machine. Routine contraction blocks new admission and drains according to the task contract; it is not authority to destroy worktrees or terminate tasks.

High-water contraction and emergency refusal are separate from low-water expansion. Expansion requires valid fresh limiting signals for a calibrated dwell interval; dwell, watermarks, per-slot demand and ceiling stay unknown. Stale/missing required signals refuse expansion with a typed reason. Existing bounded work follows its current safe contract; lack of telemetry is not an excuse to invent pressure or kill it.

Count ending backlog, age, rework and drain time, not just output completed before the cutoff. A policy producing more unreviewed artifacts is a regression even when generation throughput improves. Queueing identities such as Little's Law may be diagnostics only after checking population closure, stationarity and matched intervals; never infer human review capacity from a short burst. Fixed and adaptive policies are both candidates. If adaptation adds no practical benefit, retain the simpler calibrated policy as a comparison candidate; D-019's adaptive capability remains built/opt-in unless the Owner changes scope.

<a id="ro-s7"></a>

## S7 — Q07: Hard-floor-first conformance

Proposed gate sequence O-R05 compares staged floor screening before timing with interleaved floor/performance characterization. Both enforce the identical mandatory floors and forbid ranking until those floors pass. “Benchmark first, fix correctness later” is only a negative control:

1. **F0 evidence validity:** exact artifact/corpus/oracle identity, permissions, synthetic-data scope, clocks, counters and positive/negative controls. Invalid fixture yields invalid/inconclusive, not a candidate pass or fail
2. **F1 correctness/effects:** canonical bytes/refusals, replay, idempotence, one writer, monotonic applicable epochs, complete artifact closure, no blind retry after ambiguity
3. **F2 authorization/privacy:** current grants, non-widening config, disabled-path traps, boundary-scoped data, no hidden credential/model/egress access; upstream-only role closure
4. **F3 resource/control:** bounded allocations, backpressure, current host envelope, integrity/control reserve, no hidden process or resident subsystem; durable-event loss/unavailable PAUSE rejects immediately
5. **F4 recovery/continuity:** declared crash/reset/reconnect cases, independent acknowledgement witness, useful authorized continuation, unresolved effects preserved, accounting conservation
6. **F5 product-quality/operability:** required gates, review/error burden, required configuration/platform behavior and release closure; no feature deletion used to improve a measurement
7. **F6 performance comparison:** only independently reviewed F0–F5 passers with adopted budgets/margins; retain all floor failures in the public result record

Each floor is a predicate with an independent witness, exact scope and invalid-trace rule. Unknown required floor means **HOLD**, not eligible. Floors run before timing and again on the actual measured build after pressure/recovery; a different optimized build cannot inherit them. Failure cannot be offset by throughput, quota savings or a scalar score. A proposal-level review may accept these rules while execution remains blocked; that is not runtime conformance.

<a id="ro-s8"></a>

## S8 — Q08: Reproducible comparisons and inference

Proposal O-R06 requires preregistration before held-out outcomes. Admissible competitor: blocked versus paired/randomized preregistered confirmation designs with held-out outcomes. Exploratory tuning on the reported confirmatory benchmark is a negative control. Freeze:

- OS edition/build/kernel/architecture; NTFS/ext4 profile; mount/VFS and durability/flush settings; virtualization and reset domain; qualified collector permissions
- Actual available CPU/affinity/quota, memory/commit/disk, co-tenants, thermal/power/governor policy, foreground state, storage/cache conditions; known unknowns retained
- Source and release/build/toolchain/dependency digests, runtime flags/GC/allocator/FFI, process topology, plugin lock/capability graph, route descriptor, enabled state and effective config revision
- Sink kind, terminal/view count, source event rate, exact drain schedule, backpressure/reset policy, instrumentation/export mode and collector sampling
- Unique-task corpus, history/event-size distribution, artifacts, queue/review-service trace, arrival schedule, seeds, failure cutpoints, cache/session state and cold/warm order
- Primary endpoints, floors, product ceilings, practical margins, independent-unit definition, planned exclusions, precision/power design, confirmatory sample size and stopping/censoring rules

Use paired/block-randomized order across equivalent host states; deterministic seeded orders become part of the manifest. Measure scheduled arrival delay, not only service time after acceptance, so overload cannot disappear when a blocked load generator emits fewer requests. If an open-loop generator misses schedule, retain the offered-load and missed-arrival trace; classify it rather than pretending the system saw intended load. Terminal-input and control arrival use independent stimulus schedules.

Use unique tasks as the independent inferential unit with attempts/messages nested and repeated task versions/families identified. A process launch is a replication unit for startup, not an additional independently solved task. Estimate uncertainty with a method respecting task/family/block clustering; do not claim a powered p99 from many correlated messages. The pilot, effect margin, variance estimate and confirmatory size are unknown until chosen prospectively. No invented 30-run or million-event inference guarantee is adopted here; historical workload sizes stay provenance-bound.

Retain failures, timeouts, censored tasks, helpers, coordination, verification, recovery, active human review and later corrections. Record exclusion reasons before seeing comparative outcomes. Interim stopping for safety is always allowed and retained as failure evidence; optional stopping on an attractive winner invalidates confirmatory claims. Collection failures remain visible, with analysis populations and incomplete denominators.

<a id="ro-s9"></a>

## S9 — Q09: Workload identity, corpus and contamination

`workload-manifest-template.json` is an **unfilled, non-runnable contract**. `status=UNEXECUTED`, numeric budgets and target digests remain null. It requires a named workload revision, semantic contract, source/artifact identity, fixture-corpus digest and privacy classification, generator and evaluator hashes, independent oracle hash, environment/configuration hashes, trial order, exposure/stopping rule, collector identities, sample-unit hierarchy and review identity.

Define a comparison ID over the workload identity plus every candidate arm's manifest and common acceptance rules. The manifest digest detects change; it does not prove environment completeness or authorize execution. Public release evidence uses synthetic fixture locators and privacy-scoped aliases; local content/environment attestations stay in their authorized scope. Never publish private raw paths, stable private content hashes or account identifiers merely to make a benchmark “reproducible.”

### S9.1 — Workload registry extending PERF-001…011

| Existing identity | O-lane binding and decisive extension | In-scope provider-free evidence |
|---|---|---|
| PERF-001 | O-F05: matched log/store durability and all-byte accounting; include long reader/checkpoint pressure | Local append/replay/resource fixtures only; no store selected |
| PERF-002 | O-F06: repeated/unique artifacts, reachability/GC, missing references, privacy scope | Synthetic content and closure oracle; no private cross-project dedup |
| PERF-003 | O-F03: installed-disabled integration traps and lifecycle delta | 0/10/100 inherited catalog arms; exact payload/metadata distinction |
| PERF-004 | O-F08: burst admission plus independent control schedule | Deterministic fake jobs; no inference |
| PERF-005 | O-F09: oscillating synthetic quota/health and configuration epochs | Stable affinity and no mid-effect switch; no provider-cache saving claim |
| PERF-006 | O-F10: raw/capsule reuse and invalidation/required-field fidelity | Deterministic corpus/counter replay; actual model quality/cache economics remain unknown |
| PERF-007 | O-F07: memory/disk/queue pressure, slow observer, Stop and append witnesses | Authorized disposable fixture only; not executed here |
| PERF-008 | O-F11: coordinator/worker placement, hydration, transfer and recovery | Synthetic remote endpoint/process; real-node/route benefit unknown |
| PERF-009 | O-F08: fixed/adaptive matched traces with reviewer outage and drain tail | Machine/review/control outcomes; no human-effort benefit from simulated review alone |
| PERF-010 | O-F12: detachable views including stalled/closed/occluded clients | Existing 0/1/5/10/20 view counts are inherited test arms, not ceilings |
| PERF-011 | O-F13: finding/task deduplication, helper accounting and reserve bookkeeping | Synthetic recorded evidence only; named-model research advantage is out of scope/unmeasured |
| EXP-FHAR-10/FU-01 | O-F02: canonical/refusal/kernel arms and runtime identity | Full proof prerequisites, not a shortcut from M1A microbenchmarks |
| EXP-FHAR-11/FU-02 | O-F05/O-F06: common CAS and crash/replay contract | Same fault/durability/ack witness across stores |
| FU-05/DS-13 | O-F04/O-F12/O-F15: config/broker interactions and observer isolation | Four broker freeze blockers remain blockers |

### S9.2 — Negative traces that invalidate a claim

- Change the evaluator or a practical margin after reading arm labels; independent manifest comparison must flag a new, exploratory comparison
- Reuse held-out task content for optimization, or overlap near-duplicate family instances across pilot/confirmation; quarantine affected results, retain the overlap audit and do not quietly delete failures
- Compare different quality rubrics, route semantics or durability promises under one score; split into non-comparable strata
- Warm only the favored arm, exclude a cold failure, tune checkpoint/GC settings mid-run, or change sink rate without a new identity; classify affected trials as invalid
- Count attempts, repeated messages or provider responses as independent tasks; reject the inference denominator
- Stop before the slower arm's review/recovery tail drains, or discard censored failures; report remaining liabilities and withhold victory
- Let both implementation and oracle share the same erroneous serializer or canonical-state code; require independently authored oracle and mutation controls, not agreement alone

O-F16 exercises these as synthetic evidence mutations without running a candidate. Detection proves bookkeeping sensitivity for the seeded defects, not absence of undiscovered contamination.

<a id="ro-s10"></a>

## S10 — Q10: No-benefit, regression and tradeoff disposition

Proposal O-R07: every arm receives one scoped disposition, with all vector outcomes still visible:

| Disposition | Rule | Next action |
|---|---|---|
| INVALID_EVIDENCE | Manifest, clock, stimulus, oracle or denominator cannot support the claim | Repair evidence design and refreeze; retain invalid record |
| REJECT_FLOOR | A valid counterexample violates a non-tradeable floor | Reject exact artifact/profile; preserve witness; no speed ranking |
| HOLD_UNKNOWN | Required floor, metric, baseline, numeric ceiling or denominator missing | Name exact missing evidence/decision; do not infer safety or advantage |
| NO_BENEFIT | No preregistered practical improvement is established, including equivalence/no detectable useful gain within the planned precision | Report plainly; retain simpler comparison or optional alternative, without deleting accepted capabilities |
| REGRESSION | Adopted ceiling/noninferiority margin breached in any required endpoint, including review/quota/resources | Identify endpoint and uncertainty; reject that default claim or ask for a permitted explicit tradeoff if no floor is affected |
| NON_DOMINATED_TRADEOFF | Some outcomes improve and others materially worsen, without floor failure | Owner receives the full vectors and intended workload; no silent default choice |
| CONDITIONAL_ADVANTAGE | Floors/budgets pass, comparison is valid and preregistered practical benefit survives uncertainty and held-out confirmation | Limited to exact profile/workload/revision; independent acceptance and Owner selection still required |

Unknown subscription debit prevents a subscription-efficiency conclusion even if CPU and input-byte costs improve. It need not erase a valid CPU-only observation. No-benefit is different from inadequate power or unavailable accounting. If confidence spans benefit and harm beyond the declared margins, classify inconclusive/HOLD rather than asserting a tie. Average throughput cannot cancel a worse control p99, peak residency, review backlog or recovery endpoint.

<a id="ro-s11"></a>

## S11 — Q11: Honest counters, cache and accounting boundaries

Proposal O-R08 keeps DS-26's attribution/quantity ledger separate from financial/capacity evidence. Admissible competitor: event-level versus periodically reconciled native-unit ledgers, both preserving complete raw units and observation coverage. A single normalized cost field is a negative control if it replaces those records; an explicitly assumption-bound modeled valuation may only supplement them. Quantities are reconciled only under an explicit semantic map and exact route version; R-F Q06 and the committed R-D/DS-26 source ledgers own provider facts. This report adds no new provider-counter promise.

Each observation carries collector/source version, evidence class, task/operation/attempt/role/route/session or meter epoch, unit, interval, cumulative-or-delta semantics, coverage, freshness, availability reason and deduplication identity. Provider-reported counters are eligible only where the exact qualified route emits them. Explicit zero is retained; absent, redacted, stale, reset-ambiguous or unqualified evidence produces null. Counter decreases require a proved epoch transition; a “last usage” snapshot must not be summed on every replay.

Count planner, compactor, router, verifier, retry, recovery and external-harness helpers once. A role without a known denominator remains a coverage hole, not an exclusion. Synthetic tests provide known ledger conservation cases, but cannot prove the live provider charges the same way. API billed money, subscription-window change, provider token classes, rate-limit charge, local CPU and human review remain separate. Reconstructed prices, including an optional `ccusage` reconciliation estimate, remain modeled evidence, never billing truth or subscription capacity.

### S11.1 — Cache boundaries

Maintain separate records for local source/index cache, canonical-artifact cache, context capsule, harness session and provider-native cache. Each has its own owner, privacy scope, key/version, invalidation reason, creation/lookup/write/retention/revalidation cost and observed hit/miss. A local hit does not prove provider tokens were cached or a subscription debit fell. A source digest alone neither grants access nor permits equality leakage across private projects.

Compare cold/no future reuse, warm same route, fresh session, cross-route continuation, changed instructions/config/source, expired/missing artifact and privacy-scope mismatch. Include compaction/rehydration and failed cache work in totals. Fidelity requires exact retained directives/approvals and the declared task gate, not merely fewer bytes. Compare total system disk and I/O; moving payloads from database pages into CAS is not automatically a storage saving. Count invalidation and correction cost after the attractive initial cache hit.

### S11.2 — Host and tree attribution

Collect the declared process tree plus externally owned services separately. Linux cgroup accounting and Windows Job accounting are candidate observation boundaries (O-S06/O-S08), not credential/security boundaries. Verify descendants, breakaway, shared helpers and collector privilege before attributing totals; uncontained or shared work is a coverage gap. Do not sum per-process peak memory into a fictitious simultaneous group peak. Keep Linux RSS, cgroup memory, Windows working set and commit as distinct metrics unless a defensible common semantic exists. I/O counters do not automatically mean physical-media writes, and clock resolution does not imply clock accuracy. Where only round-trip time is observed, provider inference latency stays unknown.

<a id="ro-s12"></a>

## S12 — Q12: Telemetry is part of the floor

Proposal O-R09: minimal deterministic local evidence remains available with optional exporters, rich traces and every model disabled. Admissible competitor: richer deterministic local metrics and optional export under the same no-hidden-model and declared resource/egress rules. An always-on model-dependent status path is a negative control, not a compliant alternative. Any model/credential/egress attempt during status, config explain, queue diagnosis or replay rejects zero-model status.

Measure telemetry itself with **required evidence only**, **local operational metrics**, and **explicit rich trace/export enabled** arms. The baseline still retains the independent witness and mandatory accounting; a completely unobserved run cannot prove its own correctness. Compare separately calibrated collector overhead, data-volume/cardinality pressure, slow exporter, full telemetry disk, exporter crash/restart, serialization and retention/compaction. Preserve absolute measured results; do not subtract overhead to invent an unobserved latency. Unknown collector perturbation makes the affected performance claim provisional.

Status reads a bounded authorized projection, including freshness and explicit incomplete scopes. It must not walk all history, import every plugin or reconstruct progress with a model. High-cardinality identities and raw event bodies belong only in scoped evidence artifacts, not unconstrained metric labels. Telemetry loss is counted as such and cannot delete canonical acknowledgements. An exporter cannot block the writer or Stop; throttling optional telemetry still leaves a bounded loss indicator. O-S12 motivates testing this distinction, not selecting OpenTelemetry.

Local pressure availability, Windows PSI-equivalent semantics, portable wakeup counts, route-level capacity attribution, exact provider debit, host monetary cost and energy remain **unknown until measured or explicitly supported**. A Windows memory counter is not a PSI substitute. Idle CPU percentage is not a portable energy measurement. Electricity price or machine rental valuation requires an explicit authoritative rate/interval, and stays outside resource observations. No budget may pretend these inputs are known.

Privacy: allowlisted synthetic/aggregate fields, audience-bound artifacts, opaque project/task aliases, bounded retention, no prompt/output/source text, raw private paths, credentials or unscoped private digests in general telemetry. Test membership/timing/size leakage as well as obvious strings. Default export remains off. This contract is not proof against every side channel.

<a id="ro-s13"></a>

## S13 — Q13: Dimension comparison and recommendation/falsifier register

All recommendations are proposals for evidence or contract structure, not technology choices. Every row has a credible competitor, pre-benchmark elimination, explicit no-benefit/regression and a non-proof. O-R01…O-R09 above inherit the indicated row's local discriminators.

| Dimension / source lane | Competing candidates and measured trade | Eliminate before speed; decisive falsifier | No-benefit / regression / non-proof |
|---|---|---|---|
| **O-D1 language/runtime:** FU-01/DS-18/EXP-FHAR-10 | Pinned CPython GIL/FT, Rust, Go; hybrid FFI topology separately. Same kernel/replay and whole release closure; O-S01–03 inform controls only | Missing approved corpus/host identity; byte/refusal/epoch mismatch, orphan after claimed quiescence, unbounded allocation or broken offline closure | No practical whole-profile gain after equal semantics = no-benefit. Worse cold/tail/RSS/FFI/upgrade cost = regression. Passing synthetic reducer does not prove real-route/UI performance or universal memory safety |
| **O-D2 store:** FU-02/DS-21/EXP-FHAR-11 | Segmented JSONL+CAS versus SQLite WAL+same CAS; per-command/group commit are separately authorized semantic arms. Equal acknowledgement promise | Acknowledged canonical group lost/altered, dangling artifact, stale writer admitted, unreviewed fault domain or absent independent witness | Metadata-only speed without total-byte/recovery gain = no-benefit. Reader starvation, checkpoint tail or recovery reserve breach = regression. A process-kill pass is not abrupt-VM-reset durability or physical-power evidence |
| **O-D3 broker/IPC:** FU-05/DS-23 | Existing exact-version bounded protocol versus a separately approved negotiated-major candidate; demand-activated versus resident broker; OS transport implementations are separate profiles | Four blockers unresolved: version admission, snapshot materialization, cursor incarnation/rollover, ACK-release/credit semantics. Duplicate release, stale delivery, unbounded decoding or unavailable Stop rejects | No useful control/whole-profile benefit = no-benefit. Faster output but worse append/control tail or buffer cost = regression. Transport delivery does not prove effect settlement; no MCP or broker freeze follows |
| **O-D4 config/propagation:** DS-13/G-09, R-L | Shared typed schema/resolver plus immutable whole-effective-revision receipts versus declarative constraint challenger (e.g. CUE) preserving same command contract; indexed incremental recomputation versus full deterministic resolve | Different canonical semantic configuration bytes, effective values, refusal classes or logical field/scope provenance; stale authority expansion, half-applied revision, hidden activation or missing propagation acknowledgement semantics | Faster parse with unchanged human/update/propagation cost = no-benefit. Recompute thrash, ambiguous explanation, stale resume or migration loss = regression. Schema/JCS conformity does not establish policy correctness or choose syntax |
| **O-D5 integration tax:** R-A/R-G, DS-04, EXP-FHAR-09 | Lean optional payloads versus full installed-disabled bundle; native rewrite versus import/translation with same accepted losses; isolated versus trusted built-in where permitted | Disabled execution/credential/network/model work, silent semantic loss, authority widening or absent dependency/license closure | No measured accepted-port saving = no-benefit. Hidden startup, idle, review, upgrade or resource cost = regression. A compatible example is not universal importability, entitlement or low porting cost |
| **O-D6 adaptive capacity:** DS-06/G-21/PERF-004/009 | Calibrated min-credit/hysteresis policy versus fixed Owner ceiling; same review service trace and permitted workload | Missing required signals/ceilings; authority floor violation; unbounded queue, stale-signal expansion, oscillation or unavailable control | Same useful outcomes/backlog within precision = no-benefit. End debt, review age, scan cost or tail latency increases = regression. Synthetic reviews do not prove human capacity, nor host metrics provider quota |
| **O-D7 telemetry:** DS-26/G-25 | Minimal mandatory local evidence versus optional richer metrics/traces/export; event-level versus periodically reconciled native-unit ledgers retaining complete raw units; a blended estimator is only supplementary modeled valuation, never an evidence replacement | Null→zero, replay double charge, omitted helper, private-field export, collector blind spot or telemetry-dependent authority | Richer telemetry changes no actionable diagnosis/admission outcome = no-benefit. Observer tax, cardinality growth, stale status or blocked Stop = regression. A dashboard/SDK does not prove billing truth or a complete observation boundary |

### S13.1 — Configuration complexity and propagation cost in detail

Proposal O-R10 extends R-L Q05/Q09/Q10/Q11 without selecting human syntax. Admissible competitor: independently implemented frontend/adapter resolvers that pass the same semantic corpus, versus one shared resolver implementation. Full deterministic resolution versus indexed incremental resolution is a second admissible contrast. Uncoordinated per-surface meanings are a negative control. Freeze one effective-revision object per target and cache key including schema, resolver, scope inputs, plugin-lock/capability graph, authority and relevant route descriptor identities. For equivalent frozen inputs, compare canonical semantic configuration bytes, effective values, refusal classes and logical field/scope provenance. Record compiler/resolver/build digests and cache keys separately for each arm; these implementation identities may differ and must remain in the evidence manifest. Do not use equality of a full provenance/implementation digest as the semantic-equivalence oracle, and do not erase authority or policy differences through post-outcome normalization. Cache validity must not outlive a narrowed grant or changed dependency. Re-resolve on the declared invalidation edge, not on every token; measure against full-resolution baseline.

Record compile/validate/commit/effective timings separately; fan-out bytes, pending-target count/age, re-resolve work, duplicate-edit receipts, conflict retries, restart-required downtime and recoverable migration cost. Include both accepted propagation choices: update outstanding sessions at their permitted application boundaries, or apply only to new sessions. In both, authority revocation fences new effects immediately. Existing active, queued, idle, suspended and descendant sessions retain their own application receipts; new roots/children compile the activated revision within parent scope. Do not turn a pending revision into “applied” for disconnected work. A resumed target acknowledges the complete current revision or refuses; it cannot combine fields from different revisions. Goal-frozen changes require their accepted amendment path. A rollback is a new authorized configuration transaction and does not rewind external effects.

Complexity is evaluated with a measurement vector whose current observed values remain unknown: persisted fields and distinct concepts, scope interactions, merge operators, explanation completeness, inconsistent defaults, migration branches, duplicated resolver logic, contributor onboarding work, edit/error/recovery task time, review burden, tests and dependency closure. DS-13's 18 domains/55 leaves are a design inventory, not a target or measurement of simplicity. Fewer settings can conceal policy and become harder to operate; a comprehensive control surface need not be resident code. Add a setting only with its scope, default, lifecycle, provenance, authority class, resource effect and failing fixture documented.

Falsifier: identical user changes across CLI/TUI/GUI/adapter yield different effective configuration or cannot explain every limiting contributor. No-benefit: incremental resolution offers no practical gain over bounded full resolve. Regression: cache invalidation or propagation adds stale grants, unbounded state, confusing pending status or more operator corrections. Passing the corpus does not prove every future plugin schema safe, every configuration combination performant or GUI timing resolved.

<a id="ro-s14"></a>

## S14 — Q14: Provider-free acceptance and local handoff

### S14.1 — Exact scope and prerequisites

The verifier may review this program now. Running it is a later, separately authorized local task. All O-F fixtures below are UNEXECUTED; no runnable entrypoint for this new integrated suite was verified, so no command is invented. Existing repository scripts were inspected as text only and are not implicitly authorized to run. The local implementer must provide reviewed fixture/runner source identities before the verifier can execute.

Required package: Owner-approved semantic corpus and refusal/Stop contract; exact candidate/build/package/dependency identities; measured native D-028 host manifest; independent oracle and durable-ACK witness; bounded synthetic artifacts and route/model-denial stand-ins; per-profile budgets/margins/reserves and exposure/stopping plan; private evidence destination; explicit disposable fault-rig authorization for pressure/crash/reset cases; and an independent verifier. For broker-dependent fixtures, unresolved FU-05 blockers produce BLOCKED, not a guessed protocol. Counters with unsupported semantics stay unavailable.

`fixtures.json` gives inputs, prerequisites, independent oracle, expected evidence, stopping conditions, competitor, falsifier and non-proofs for every fixture. The concise index follows.

| Fixture | Discriminating local handoff and exact oracle |
|---|---|
| [O-F01](fixtures.json#/fixtures/0) Counter/oracle sensitivity | Seed explicit zero, missing, stale, reset and duplicate counters; independent expected ledger rejects null→zero, double charge and missed helper; positive-control failure makes results inconclusive |
| [O-F02](fixtures.json#/fixtures/1) Deterministic runtime gate | Independent candidate outputs equal the approved corpus for decode/admit/reduce/derive/replay and refusals; compare each with oracle, not only each other |
| [O-F03](fixtures.json#/fixtures/2) Disabled-path zero-work | Absent/full-installed-disabled arms plus one-trigger positive controls; any forbidden attributable activation fails; metadata bytes/resources reported separately |
| [O-F04](fixtures.json#/fixtures/3) Complete configuration propagation | Same typed edit through every surface; compare effective digest/reasons/authority and whole-revision receipts under disconnect/Stop/restart; stale/partial adoption fails |
| [O-F05](fixtures.json#/fixtures/4) Writer/store crash and pressure | Paired stores, common CAS, durable external acknowledgement witness, crash cutpoints/long reader; missing acknowledged state, stale writer or unavailable Stop fails |
| [O-F06](fixtures.json#/fixtures/5) Artifact/cache closure | Synthetic duplicate/unique/privacy-scoped artifacts, invalidation and referenced-GC race; dangling acknowledged reference or unauthorized cross-scope hit fails |
| [O-F07](fixtures.json#/fixtures/6) Integrity reserve under overload | Independent control stimulus plus queue/memory/disk pressure and slow sink; lost durable event or unavailable PAUSE fails even if aggregate throughput rises |
| [O-F08](fixtures.json#/fixtures/7) Admission/review crossover | Fixed/adaptive input plus controlled reviewer pause/rework; compare ending debt, drain tail and responsiveness with identical arrivals; hidden backlog defeats benefit |
| [O-F09](fixtures.json#/fixtures/8) Oscillation and checkpoints | Synthetic health/quota/config signals around cutpoints; witness must show no mid-effect switch, no stale expansion, bounded declared retries and explicit unknown inputs |
| [O-F10](fixtures.json#/fixtures/9) Cache/continuity accounting | Fresh/warm/expired/cross-route stand-ins with exact retained directives and counter replays; ledger/required-field drift fails; no actual provider economics inferred |
| [O-F11](fixtures.json#/fixtures/10) Placement and remote ambiguity | Local/remote stand-ins including disconnect-before-send/ambiguous send/duplicate result/stale epoch; stable operation/reservation identity and total transfer/recovery evidence required |
| [O-F12](fixtures.json#/fixtures/11) Observer isolation | Detach/reconnect, inherited view counts, stalled/occluded/small-buffer sinks, cursor/reset cases; canonical parity, bounded queues and responsive control required |
| [O-F13](fixtures.json#/fixtures/12) Full-role evidence accounting | Synthetic helper/research/fork/recovery attempts; independent finding keys and role ledger conserve obligations/counters without double attribution |
| [O-F14](fixtures.json#/fixtures/13) Whole-release closure | Lean/full-disabled/native/upstream/combined/remote locked artifacts; offline core boot/recovery and declared dependency closure; missing accepted capability remains a release blocker |
| [O-F15](fixtures.json#/fixtures/14) Instrumentation tax | Required-evidence/local-metrics/rich-trace arms, cardinality flood and failing exporter; optional telemetry cannot block writer/control or become authoritative |
| [O-F16](fixtures.json#/fixtures/15) Contamination/refreeze rejection | Mutate a copy of synthetic result manifests, evaluator, corpus overlap, order and sample hierarchy; independent classifier must invalidate the tainted comparison |
| [O-F17](fixtures.json#/fixtures/16) Budget/result classifier | Synthetic floor failure with attractive speed, null denominator, true no-benefit, resource/review regression and non-dominated vectors; exact dispositions in S10 required |
| [O-F18](fixtures.json#/fixtures/17) Complete-architecture confirmation | Paired A/B plus C at fixed residency across O-P profiles; full workload vector and recovery/review tail; component winners that fail whole-profile floors/budgets cannot be promoted |

Stop all dependent execution upon non-synthetic data, unexpected credential/provider/network access, unauthorized host action, exceeded approved fault envelope, lost witness, invalid clock/collector scope, canonical divergence, stale admission or unavailable control. Preserve evidence; distinguish a candidate failure from an invalid injector. No repair-and-rerun hides the original result. New repairs/configuration changes receive new identities and the relevant floor suite again.

### S14.2 — What independent acceptance means

**Program acceptance** can establish that every required decision has a named metric, independent oracle, baseline competitor, unknown treatment, budget derivation, workload identity, failure disposition and stopping rule. It cannot fill numeric ceilings or claim runtime passes. O-F17 is the machine-checkable decision contract; O-F16 guards comparability. The new appendices make this report more than a restatement of OR-024: each profile/regime cell is explicit; lifecycle and complete-profile contrasts are enumerated; fixtures have observable reject predicates; and the classifier refuses synthetic fast-but-unsafe, fast-but-unreviewable and unknown-debit “wins.”

**Measured budget acceptance** later requires immutable raw samples and host/collector identity, validated sensitivity controls, all applicable floor evidence, calibrated reserves, Owner-adopted ceilings/margins, held-out confirmation and an independent rerun. A vendor benchmark or a transplanted headline percentage cannot satisfy those joins. Reviewing the JSON files is not running the product.

### S14.3 — Completion gates and non-results

- G01: vector, dimension mapping and OR-024 ranking specified in S1/S2/S13; no scalar score
- G02: all profiles/regimes/metric derivations specified in S4/S5 and budget register; **numeric budgets and accepted capacity remain unknown**
- G03: non-tradeable floors and immediate loss/PAUSE failures specified in S6/S7
- G04: named workload/corpus/evaluator/environment identity and statistical/stopping requirements in S8/S9
- G05: **bounded unknown; not operationally satisfied**. Disabled-path proof and integration measurements require O-F03/O-F14/O-F18; no clean dynamic receipt exists here
- G06: native-unit accounting, cache boundaries and null semantics in S11/S12
- G07: all seven dimensions have competitor, pre-benchmark elimination, decisive falsifier, no-benefit/regression and non-proof in S13; material tradeoffs escalate under S10
- G08: provider-free independent acceptance handoffs specified in S14 and fixtures; **not executed**
- G09: no language, runtime, package manager, store, framework, broker, protocol, transport, human syntax, toolkit, sandbox, vendor or route selected/qualified; no measured advantage, capacity point, entitlement or porting saving
- G10: artifact-only QA and protected-governance byte checks are recorded in `qa.json`. Scope is generated R-O outputs and selected pinned safe inputs, not secret-bearing files or runtime observation; pattern scanning does not prove absence of every secret or side channel

There is no benchmark result, live provider/model/account call, credential inspection, installation, configuration change, repository edit, deployment, publication, merge, spend or counsel engagement in this lane. All implementation, operating-system and route qualification remains explicitly separate from this research deliverable.

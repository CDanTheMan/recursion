# R-R — Long-horizon autonomy and scheduling

Decision-ready design candidate · 2026-10-02 UTC  
Repository basis: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
Status: researched design; every runtime handoff **UNEXECUTED**

## Decision summary

A durable scheduler should remember **when to ask for admission**, never remember that an effect is forever approved. Put one bounded campaign beneath an exact accepted GoalSpec; retain cumulative expenditure, outstanding reservations, evidence and unresolved effects across every timer, retry, plan revision, session and recovery. On each wake, resolve current canonical authority before creating work. On every effect, recheck it again. These are candidate mechanics, not evidence of implementation.

The proposed autonomy plugin is **off by default, explicitly enabled, goal-scoped and bounded**. It cannot activate itself, create a standing executive, acquire portfolio authority, approve its outputs, relax a gate, renew its own horizon, or expand its sources, routes, privileges or spending. A schedule, deadline, retry or installed-plugin flag supplies none of those powers. D019 still requires the comprehensive accepted capability surface to be built and shipped opt-in. This report neither proposes a smaller first release nor selects a language, store, framework, workflow engine, scheduler, runtime or vendor.

The useful candidate advance is D024 productive continuity: after a bounded failure, preserve enough trustworthy state to complete the same currently authorized goal with fewer errors and less human reconstruction than a strong simple baseline. Uptime, token generation, process survival and a green workflow status are insufficient. Recursion's productivity advantage, stopping latency, unattended safety and route fitness remain **unknown**.

### Evidence legend and authority

- **D — source-documented:** a retrieved public primary source describes its own system or study; transfer is limited
- **O — locally observed:** this report inspected committed source or receipt bytes; no target code was executed
- **I — inferred/design:** all proposed Recursion contracts, recommendations and fixture oracles below
- **U — unknown:** runtime behavior or measurement not established here; a missing counter is not zero

The controlling documents are the current `CONTROL_PLANE.md`, `ANCHOR.md`, active v3 goal and D017–D033 [L01–L04]. `PLANNING.md` and `AUTONOMOUS-PLANNING.md` contribute immutable goal/plan/packet, attenuation, novelty and gate semantics [L05–L06]. Their retired Hermes-constitution and standing-role wording is not current authority. Product roles may participate in an explicitly admitted goal; they cannot become a permanent repository or portfolio executive. No second planner, queue database or workflow journal becomes canonical authority.

D022's vocabulary is accepted. Some committed planning code still enforces `current-immediate`; the new mapping is a qualification target, not a claim that implementation already conforms. D020 requires a user-toggleable automatic writer-takeover plugin in remote/full, while the core remains single-node with a fence and availability seam. The requirement survives; unconditional zero downtime, partition availability and remote rollback do not follow. D028 platform floors remain fixed. TUI-first/later-GUI sequencing shares one backend; the precise timing of D019's built-opt-in GUI versus older exclusion wording remains an Owner interpretation, not a scheduling decision.

## Public evidence capsules

These compact capsules are the only substantive public-source summaries in this lane. Later sections apply Recursion-specific reasoning rather than repeat vendor descriptions. Retrieved 2026-10-02; versions and hash limitations are in [source-register.json](source-register.json). Sources are prior art, not selected dependencies.

<a id="rr-s01-facts"></a>
- **RR-S01, Temporal execution (D):** workflow replay checks generated commands against recorded history; workflow/run identity and an execution chain are distinct. This motivates separating a durable campaign from a restarted attempt, without importing Temporal's authority model. [Documentation](https://docs.temporal.io/workflow-execution)
<a id="rr-s02-facts"></a>
- **RR-S02, Temporal retries (D):** activity retry defaults differ from workflow retry defaults, and some default limits are unlimited. A workflow-assisted candidate therefore needs explicit bounded policies rather than library defaults. [Documentation](https://docs.temporal.io/encyclopedia/retry-policies)
<a id="rr-s03-facts"></a>
- **RR-S03, Temporal scheduling (D):** schedule pause does not stop already-started executions; overlap and catch-up are separate policies. Manual trigger/backfill differ from ordinary catch-up. Recursion must mediate every path. [Documentation](https://docs.temporal.io/schedule)
<a id="rr-s04-facts"></a>
- **RR-S04, Temporal cancellation (D):** cooperative cancellation and forceful termination differ; activity cancellation depends on heartbeats, and termination does not run workflow cleanup. A terminal workflow record cannot establish external-effect rollback. [Documentation](https://docs.temporal.io/encyclopedia/workflow/cancellation-and-termination)
<a id="rr-s05-facts"></a>
- **RR-S05, Kubernetes CronJob (D):** scheduling may create duplicate or missing jobs; concurrency policy is per CronJob, and suspending scheduling leaves existing jobs unaffected. These are concrete counterexamples to treating a timer as global execution ownership. [Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
<a id="rr-s06-facts"></a>
- **RR-S06, systemd v257 timer source (D):** timers can activate services, retain missed calendar-trigger state and randomize delay; an already-active target is not restarted. Demand activation therefore has useful primitives but needs a separate canonical wake ledger. This Linux example says nothing about Windows qualification. [Versioned source](https://github.com/systemd/systemd/blob/v257/man/systemd.timer.xml)
<a id="rr-s07-facts"></a>
- **RR-S07, AWS retry guidance (D):** retries can aggravate load; idempotency and non-transient failure handling matter alongside backoff. Jitter or increasing waits alone cannot make an unsafe effect safe. [Documentation](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html)
<a id="rr-s08-facts"></a>
- **RR-S08, LangGraph interrupts (D):** resuming an interrupted node re-executes its earlier code; side effects before the interrupt need idempotency or relocation. A human-in-the-loop API is not automatically a pre-effect boundary. [Documentation](https://docs.langchain.com/oss/python/langgraph/interrupts)
<a id="rr-s09-facts"></a>
- **RR-S09, long-task measurement (D):** the paper defines a human-calibrated completion horizon at a stated success probability, with domain and external-validity limits. It measures task success, not how long a daemon stays alive. No current model ranking or Recursion horizon is inferred. [Paper v4](https://arxiv.org/html/2503.14499v4)
<a id="rr-s10-facts"></a>
- **RR-S10, proxy objectives (D):** *Concrete Problems in AI Safety* distinguishes reward hacking, side effects and scalable supervision among accident risks. It motivates testing the objective and verifier, not rewarding activity counters. [Paper v2](https://arxiv.org/abs/1606.06565v2)
<a id="rr-s11-facts"></a>
- **RR-S11, controlled reward-hacking study (D):** a 2026 preprint reports a gap between observed reward and hidden safety objectives in adapted text gridworlds. The abstract-level evidence supports a negative-test concern, not an estimate of Recursion or production-agent prevalence. [Paper v1](https://arxiv.org/abs/2606.15385v1)
<a id="rr-s12-facts"></a>
- **RR-S12, minimal-harness counterpoint:** The [canonical paper note](../model-architecture/report.md#minimal-harness-paper-facts) retains its documentary finding and scope limits. **I:** compare a strong simple competitor under the same acceptance conditions; do not remove D019 capabilities. See Q04 for the matched Recursion comparison.
<a id="rr-s13-facts"></a>
- **RR-S13, provider limits (D):** Claude's API documentation separates rate and spend limits and documents distinct error behavior, including cases without a retry-after value. An error code alone cannot establish when another attempt is admissible. This is one API's documentation, not subscription or automation qualification. [Documentation](https://platform.claude.com/docs/en/api/rate-limits)
<a id="rr-s14-facts"></a>
- **RR-S14, usage scope (D):** Claude's organization usage/cost interface is an administrative historical reporting surface with access requirements. It does not establish per-attempt subscription debit or permission to obtain credentials. Existing route-accounting facts remain in [R-F's canonical note](../rf/report.md#claude-accounting-facts). [Documentation](https://platform.claude.com/docs/en/manage-claude/usage-cost-api)

## R-R-Q01 Bounded decomposition

**I; recommendation RR-R01.** Extend the existing immutable `GoalSpec → PlanRevision → TaskNode → WorkPacket` relationship with a **CampaignBinding**, not another goal authority. A campaign is a bounded execution envelope for an already accepted goal. Its version binds goal and plan digests, plugin/configuration revision, authorized source set, scheduling policy, total budget ledger, progress contract, expiration, stop policy, notification policy and promotion actor. Kernel admission records it; the plugin may only propose it. Enabling the plugin is distinct from admitting a campaign, a wake, a step and an effect.

The work structure has two relations: a bounded parent/child decomposition tree for accountability, and an acyclic dependency graph for ordering. Each node has one parent goal and one accountable step owner; shared evidence is referenced rather than charged as duplicated completion. A task has exact inputs/source revisions, allowed outputs and paths, read/effect scope, gate procedure and assigned verifier, lease maximum, retry maximum and terminal contribution. Depth, total nodes, active leaves, unresolved leaves and proposal bytes all have finite GoalSpec-bound ceilings. Adding a child consumes capacity before dispatch; neither renaming nor creating a fresh run resets that ceiling.

Plan admission rejects cycles, dangling dependencies, duplicate semantic obligations, unowned effects, conflicting writers, unbounded fields, relaxed gates and scope outside the parent. A ready node requires satisfied dependencies, current bindings, reserved resource/review capacity, no Stop and no unresolved effect conflict. The kernel derives the immutable attenuated packet; a worker does not create children or mint packets. A lease permits only its named work and expires even if the worker reports activity. Expiry fences future work but does not prove the worker or a remote effect stopped.

A bounded planner may propose a decomposition only while executing an admitted planning step inside the goal. It does not continuously invent projects. If no complete goal/gate or bounded planning mandate exists, the result is a draft or blocker, never executable work. This preserves accepted product roles without reviving the retired executive.

## R-R-Q02 Bounded and auditable replanning

**I; RR-R02.** Keep the canonical seven-kind `NoveltyDelta` grammar [L06]: evidence-added, hypothesis-replaced, strategy-changed, route-capability-changed, task-narrowed, dependency-repaired and owner-amended. Typed difference is necessary but not evidence of semantic value. Track all revision and retry expenditure at campaign level.

A retry repeats one stable logical operation after a classified failure, with one retry owner and a new attempt identity. A replan changes dependencies, node contracts, source validity or strategy across nodes and requires a new immutable PlanRevision. The proposal binds old/new digests, trigger evidence and a complete disposition of every old node: retained-compatible, invalidated, quarantined, superseded, cancelled or terminal-compatible. Compare-and-admit on the expected active revision prevents two planners from silently replacing one another. New authority requires Owner amendment, not replan.

Bound both: per-node attempt count; per-failure novelty allowance; per-plan and campaign revision limits; planning CPU/model/tool allowance; proposal bytes; wall deadline; and a finite recovery allowance. Repeated failure fingerprints and already-consumed novelty digests prevent rephrasing from becoming progress. Identical or cosmetically renamed goals cannot evade canonical semantic lineage. Since semantic equivalence is not generally decidable, mechanically reject exact repetition, require failure-addressing structured deltas, then let the declared independent gate assess usefulness; unresolved ambiguity blocks rather than relying on a model similarity score.

Replan budget is not a reward for producing a new plan. At the declared no-progress window, block further generative work, checkpoint and escalate with retained work. A long valid experiment can declare intermediate independently observable milestones in advance; it cannot retroactively lengthen the window because it is busy. The stopping thresholds are policy inputs awaiting calibration, not values selected here.

## R-R-Q03 Canonical plan versus remembered plan

**I; RR-R03.** Canonical accepted GoalSpec and active PlanRevision remain owned by the existing fenced writer. A remembered plan, context capsule, scratchpad or workflow memo is a derived artifact with its source digests, read cut, provenance, missing fields, transformations and age. It may help find candidates; it may not grant authority, choose the active revision, prove a gate or answer a pending approval.

At wake/resume: load authenticated canonical head; verify replay/checkpoint; resolve current goal/plan/source/configuration/policy refs; compare remembered refs; discard or quarantine stale derived claims; rehydrate exact accepted directives, gate definitions and pending questions separately. Missing canonical data yields `recovery_blocked`, not reconstruction of authority from plausible prose. A recalled prior PASS remains evidence for that candidate only and requires a compatibility check before reuse. An accepted decision can be superseded only by its authorized immutable amendment; a summary cannot overwrite it.

R-P's [trust/provenance boundary](../rp/report.md) applies before retrieval and again before effect admission. R-Q's [recovery candidate](../rq/report.md#q14) owns detailed durable-memory mechanics; this lane's required interface is the digest-bound canonical/derived split above. Both reports are draft integration dependencies, not accepted runtime behavior. No additional model inference is required just to inspect status, validate references or decide a deterministic refusal; an upstream-only path must not silently invoke a native planner or compactor.

## R-R-Q04 Decomposition competitors and decisive comparison

**I; RR-R01.** Compare: (A) a hierarchical bounded DAG with workers; (B) a flat queue of independently gated packets; (C) one admitted agent/session with a scratchpad and the same effect, accounting and verification controls. A is plausible for independently verifiable subproblems and failure isolation; B avoids manager overhead when dependencies are shallow; C is a serious baseline when one coherent context dominates.

The requested [minimal-harness paper note](../model-architecture/report.md#minimal-harness-paper-facts) is a counterpoint to assuming more orchestration improves task scores, not a conformance test of Recursion's authority or recovery contract. The comparative endpoint here is verified useful completion after interruption and source/route changes, with the same source inputs, model/route conditions, authority, total allowances, reviewer availability and deadline. Charge every planning, consultation, replay, verifier and failed attempt; include failures and censored runs rather than report only successes. Preserve optional features in every build and vary enabled profiles.

Decisive falsifier: the flat or single-session baseline meets the same continuity/safety gates with equal or better verified outcomes and lower human review/reconstruction effort at matched expenditure, or hierarchy introduces more stale/duplicated work. Then change the default decomposition profile, not accepted capability availability. Passing a synthetic structural test does not show semantic decomposition is worthwhile; an eventual benchmark win does not show superiority across tasks or models.

## R-R-Q05 What unattended means and what may wake it

**I; RR-R04.** Unattended means no human is presently participating; it does not mean ongoing approval. Eligible wake classes are an admitted timer occurrence, an authenticated user-requested signal, a bounded queued-work notification, a canonical dependency-completion event, or a previously admitted capacity recheck. Public source change is an untrusted observation until provenance and relevance checks pass. A worker's “please continue,” a remembered deadline, a heartbeat and an external webhook do not by themselves authorize a turn.

Within an enabled campaign, a wake may perform already admitted deterministic bookkeeping, compare permitted cached evidence, verify a pure predicate, prepare a proposal or conduct specifically authorized read-only source retrieval with its own egress/privacy checks. Live provider/model dispatch, operational host actions, spend, publication and merge remain human-gated; the unattended path reaches `waiting_for_human` and dispatches none of them without the required fresh reviewed admission. It cannot infer consent from the user's absence, a past session or an elapsed deadline. This report authorizes no such action and starts no unattended run.

Separate lifetimes:

1. `CampaignBinding`: `proposed → admitted → enabled → suspended/expired/closed/revoked`; no plugin-authored enable/renew transition
2. `WakeIntent`: `registered → due-observed → claimed → admitted/refused/expired/superseded`; a durable claim is not authority to execute
3. `RunAttempt`: `admission-pending → ready → running → waiting_dependency/waiting_human/waiting_capacity/gate_pending → verified_complete/stopped/failed/quarantined`
4. `EffectIntent`: existing prepare/dispatch/observation/reconciliation lifecycle, independently tracked even after a run ends

Waiting states release their execution slot where safe, but retain ownership of unresolved effects and reservations. `sleeping` is a scheduling projection, not a live worker lease. A calendar occurrence contains nominal due time and policy revision; effective start, admission time and observed action time remain separate.

## R-R-Q06 Bounded self-scheduling and candidate architectures

**I; RR-R04/RR-R05.** A proposed `ScheduleSpec` binds exact campaign/goal/plugin/configuration revisions; allowed event sources; cadence with IANA time zone and calendar-rule version where relevant; start/expiry; earliest/latest eligible times; missed-run policy; overlap limit; queue and notification bounds; quiet hours; backoff/jitter policy; maximum wakes, active runs and attempts; and cumulative resource limits. Required unknowns block admission. The plugin may request a later wake within this envelope; it cannot advance cadence, renew expiry, add triggers or use a new account.

A wake key is `(schedule_id, schedule_revision, nominal_occurrence_id)`. Persist it and its disposition canonically before an executor is eligible. Duplicate delivery resolves to the same intent/receipt; changed payload under the same key is a conflict. Concurrency is checked across the relevant goal/account/resource scopes, not merely per timer. Eligible queues use an explicit fair-service policy with bounded aging and per-scope admission ceilings; urgent control and revocation retain a separate service reserve. Aging changes priority only, never grants. Unknown prerequisite or capacity cannot be solved by bypassing another scope’s limit. A dependency wait must not occupy the sole executor needed to resolve that dependency. Queued duplicates coalesce by declared event semantics. A policy may skip or coalesce stale occurrences; catch-up/backfill is bounded, visible and admitted explicitly. Resume cannot produce an unbounded burst.

Civil-time schedules resolve daylight-saving gaps/folds by an explicit skip/earlier/later policy; retain the chosen occurrence identity. Monotonic elapsed time controls local timeouts. Wall-clock changes, suspend/resume and clock uncertainty are recorded observations. A backward clock must not extend an expired lease or restore a consumed budget. If cross-restart elapsed time cannot be bounded, deadline validity is unknown and admission blocks pending trustworthy time evidence. Quiet hours can defer ordinary work/notifications, but cannot delay Stop, revocation or containment fencing.

Backoff computes a bounded next-eligible time from classified failure, attempt ordinal and current policy. Jitter is recorded once as a bounded observation so replay does not resample it. Respect a valid route-specific retry-after as a minimum where applicable; cap by campaign expiry. Missing retry-after does not mean immediate retry. Capacity reset is evidence to reconsider admission, not automatic fresh money or permission.

| Candidate | Mechanism and useful fit | Principal cost/failure | Required falsification |
|---|---|---|---|
| Resident deterministic dispatcher | One enabled service watches canonical due work; no resident model needed; low-latency event handling | Idle footprint, restart races and a temptation to let the daemon become an executive | Saturation/Stop responsiveness, bounded idle cost, crash claim races and zero disabled activation |
| Demand-activated dispatcher | OS/event facility starts a bounded admission pass; exits when done; explicit wake ledger remains canonical | Startup latency, missed/duplicate events, boot catch-up and platform differences | Same event corpus and deadlines, cold-start budget, duplicate suppression and reboot recovery |
| Workflow-assisted dispatcher | External workflow execution supplies timers/retries/history behind an adapter | Competing history/authority, default retries, version migration and hidden child lifecycle | Canonical state remains sole authority, every replay/trigger re-admitted, no hidden retry or budget reset |

An owner-invoked batch using the same checks is a useful bounded comparison baseline, not a substitute for the accepted opt-in scheduling capability. None is selected. RR-S01–S08 supply concrete prior-art contrasts; comparison measures all three against the same neutral contract. A workflow engine may store delivery state and receipt references, never independently decide an accepted goal or effect. A resident non-inference dispatcher is not intrinsically a standing executive; authority and ability to generate/assign unbounded work are the decisive distinctions.

**Disabled path:** installed metadata may be bounded and inspectable, but executable plugin code is not imported, initialized or installed; no timers/watchers/subscriptions, model calls, subprocesses, credential reads, network/egress, reservations or effects are attributable to the disabled feature. Remove/fence its scheduler registrations and external trigger activation, not merely suppress its final callback. Record residual externally delivered events as discarded through the existing core ingress, without loading the plugin; distinguish unavoidable shared ingress/metadata cost from plugin activity. Disabling an active plugin first fences admission and settles or quarantines owned work. Only observed quiescence permits a fully disabled claim; unresolved remote work remains visible.

## R-R-Q07 D022 Stop and sleeping work

**I; RR-R06.** Stop is a command with authenticated actor, exact target/rooted ownership set, expected state/configuration, mode, pause policy, unique ID and new stop fence. Commit the local admission fence before acknowledging local acceptance. Then remove/reap in-scope scheduled wake/retry registrations and fence relaunch sources. Retain tombstones and receipts; do not erase history. Repeated delivery of an old timer fails its captured schedule/stop generation, even after restart. A manually requested resume is a new command and new admission, never a callback from the stopped timer.

| D022 mode | Sleeping timer and pending retry | In-flight step and worker | Honest completion |
|---|---|---|---|
| **Aggressive** | Fence/reap the selected actor's owned future work immediately; enumerate descendant schedules separately | Interrupt selected actor/operation without waiting for its normal boundary; do not silently include unrelated descendants | Local interruption/termination and owned-schedule receipts; unresolved effects stay unknown |
| **Full** | Fence/reap the root and all owned subagents, shells, monitors, retry sources and relaunchers; include later-discovered descendants linked to the pre-fence ownership root | Stop the rooted owned set; shared/borrowed operations are scoped so unrelated persistent work survives | Per-member settlement or explicit unresolved status plus remote receipts; no auto-respawn |
| **Lazy** | Close new admission immediately; sleeping has no running-operation boundary to wait for, so its wake/retry is reaped now | Name the exact already-admitted observable current-operation boundary and finite deadline; allow only permitted existing operation to reach it; then no next operation | Boundary receipt, remaining-effect status and observed local quiescence; timeout is not success |

The configured **mechanics are orthogonal**, not aliases for these modes:

- `checkpoint`: after fencing new work, record a validated checkpoint at an allowed current-operation boundary; an attempt to save requires no new model turn or forbidden effect
- `interrupt`: deliver the supported interruption/termination operation within the selected scope; transport ACK is not termination or effect settlement
- `drain`: allow only a finite captured allowlist of already-admitted operations to settle within existing grants/budgets/deadlines; no new dependencies, retries, model turns, publication or promotion are implied

A policy compiler rejects contradictory combinations. In particular Aggressive cannot wait for checkpoint/drain; it may retain an already-safe snapshot and interrupt. Lazy may checkpoint at its named boundary; its escalation behavior must be explicit and separately within the authorized target scope. Full determines ownership closure, then applies the approved interrupt/checkpoint/drain mechanics with a finite termination bound. Revocation or privacy/containment failure overrides a permissive drain: no fresh affected effect may dispatch. Current literal M1A immediate PAUSE behavior must not be relaxed during construction merely to implement this candidate.

Report a vector: `requested`, `locally_accepted`, `local_fence_installed`, `remote_fence_observed`, `schedules_reaped`, `interrupt_delivered`, `owned_processes_quiescent`, `external_effects_settled`, `independently_verified`; each has true/false/unknown, scope and timestamp. “Asked to stop” can be true while observed stopped is unknown. A disconnected machine remains unknown. No mode undoes a pre-fence external effect. A bounded control/cleanup reserve must survive ordinary budget exhaustion and saturated presentation queues; it cannot finance more research.

## R-R-Q08 Cross-harness and credential boundaries

**I; RR-R07.** The scheduler talks to one route-neutral admission interface and names the logical goal/step/operation, never a provider token. A route descriptor carries harness/interface/build, model/provider when relevant, account/capacity reference, execution host/profile, capabilities and losses. Its credentials remain behind the operator-provisioned trusted-launch boundary required by D029. D021/D030 favor user-authenticated harness-native delegation; no credential extraction, refresh workaround, automatic login, account switching or provider proxy is supplied by scheduling.

R-E's [boundary research](../re/report.md) controls launch isolation; filesystem denial alone does not exclude credential export through an unconstrained CLI or returned output. R-F's [route and fan-out contracts](../rf/report.md) control source-loop ownership and attempt accounting. A native loop remains native; an upstream-only workflow does not acquire a hidden native planner, reviewer, compactor or recovery model. Missing control capability is a declared loss or refusal, not a simulated success badge.

On route change, checkpoint/reconcile first, recheck current grants/source/configuration, preserve logical operation IDs and all expenditure, then issue a new route assignment/packet. An existing ambiguous effect cannot be resubmitted via a different harness. A provider session resume proves neither Recursion authority nor continued entitlement. D023 remains Codex App Server first qualification priority, not qualification already achieved. Legal/automation eligibility stays with R-H and the existing counsel gate; this lane makes no entitlement finding.

## R-R-Q09 Cumulative budgets and honest counters

**I; RR-R08.** The canonical ledger uses **disjoint settled consumption and outstanding reservations**. For each resource dimension, admission requires `settled_consumption + outstanding_reserved_upper_bound + proposed_new_reservation <= approved_limit`. Uncertain liabilities are an **annotation/subset of outstanding reservations**, never an extra amount added again. Settlement atomically moves the corresponding reserved amount to measured consumption and releases only demonstrably unused remainder. A missing trustworthy upper bound for an unresolved liability blocks further admission against that pool. The estimate is not reported as measured consumption.

| Dimension | Required counter and reservation | Unknown behavior |
|---|---|---|
| Wall-clock and active compute | Absolute campaign expiry; elapsed admission-to-outcome time including waits; separate active CPU/time and retry delay | Uncertain clock continuity blocks deadline-sensitive admissions; waiting time never silently disappears |
| Model/token | Parent and child turns; input/output/cache categories when exposed; planner/reviewer/compactor/tool-helper use; bounded launch reservation | Missing provider count is null with reason, route and interval; no “zero-token” inference from absent telemetry |
| Monetary | Currency and minor units, approved spending class, exact reserved maximum including authorized overhead | No price-derived subscription debit; no unpriced spend; capacity exhaustion cannot select metered fallback |
| Quota/capacity | Account/pool/window, observed counter semantics and timestamp, known allocations and uncertain consumption | A rate limit, token count and subscription debit are separate; no counter means quota remaining unknown |
| Tool/network | Logical operations, dispatch attempts including retries, read bytes/egress requests and bounded subprocess/resource use | Uninstrumented hidden operations make coverage incomplete; required hard ceiling then blocks |
| Effects | Prepared/dispatched/settled/ambiguous identities and per-class ceilings | Timeout retains liability and effect ownership; cancellation is not refund or settlement |
| Artifacts/storage | Produced bytes/count, retained bytes, quarantined output, logs, candidate versions and retention costs | No deletion of required evidence to manufacture headroom; deletion needs its own authority |
| Review | Reserved verifier slots/time allowance, backlog count/bytes/age and high-risk review capacity | Unavailable reviewer is `waiting_review`; no unreviewed PASS and no presumed infinite human capacity |
| Recovery/control | Reserved replay, reconciliation, checkpoint, Stop, evidence preservation and notification allowance | Ring-fenced control cannot be borrowed for generation; exhaustion yields bounded safe state and explicit unknowns |

Parent limits dominate child sums; transfer is a canonical atomic reservation reassignment, not minting new allowance. Record expenditure before, during and after failure as observable; a failed attempt is not free. Retrying, replanning, forking, moving machines, new provider sessions, calendar-day rollover, workflow continue-as-new and changing plugin versions do not reset the campaign ledger. A separately authorized periodic allowance can renew only according to its exact window; lifecycle restart cannot trigger renewal. Shared usage not attributable to one child is retained as parent overhead or unknown, not silently distributed to make savings attractive.

RR-S13/RR-S14 and the [shared accounting note](../rf/report.md#claude-accounting-facts) illustrate why API limits/reporting cannot be generalized to subscription usage. Any future pricing or counter comparison must pin workload, route/build, account class, measurement interval, coverage and units. No vendor-intent story follows from measured burden (D031).

## R-R-Q10 Stopping conditions and declaring authority

**I; RR-R09.** Stopping is a finite state decision under the accepted policy, not a model's feeling that enough work occurred. Terminal execution state and unresolved effects remain independent.

| Condition | Declarer/evidence | Required disposition |
|---|---|---|
| Goal met | Assigned independent verifier passes exact candidate/gates; kernel confirms acceptance closure and required Owner seam | `verified_complete`; scheduled future work reaped; promotion still separate |
| Budget exhausted | Kernel ledger/reservation test against accepted limit | Stop new work; checkpoint/control reserve only; `stopped_budget` |
| No progress | Deterministic monitor applies accepted progress window to verified receipts; disputed semantics go to named reviewer | `stopped_no_progress` or bounded `waiting_review`; no automatic extension |
| Safety floor tripped | Admission/egress/containment/refusal-storm monitor records violation or required evidence absent | Immediate affected admission fence; quarantine/Stop; scoped escalation |
| Authority revoked/expired | Authenticated Owner/policy revocation or lease/goal-expiry predicate | No further affected dispatch; reconcile previously dispatched effects |
| Dependency blocked | Canonical missing/invalid dependency or observed outage with named resolution actor | `waiting_dependency` with bound and condition; expiry becomes stopped-blocked, not success |
| Human interrupt | Authenticated Stop command under D022 | Exact scope/mode applied; observations reported independently |
| Inconclusive effect | Missing/conflicting acceptance receipt | `quarantined`/`paused_with_ambiguity`; only admitted reconciliation/remediation |

A schedule may recur while a goal remains authorized, but each campaign has a finite horizon/action allowance and a decidable local predicate for when no further autonomous work is admitted. Open-ended discovery is divided into explicitly bounded campaigns; renewal is an Owner-controlled decision. This does not claim arbitrary research goals have a decidable success predicate. When success cannot be mechanically judged, a named independent review decision is a required terminal gate; until then completion is unknown.

## R-R-Q11 Escalation without silent drift or alert loops

**I; RR-R10.** One durable `Escalation` binds campaign/goal/plan/step, blocker kind, failure fingerprint, current source/authority refs, relevant evidence, attempts/expenditure/remaining bounds, unresolved effects, exact decision needed, authorized options and the next permissible action. Route it to the authority named by the accepted goal: the Owner for intent, scope, spending, irreversible ambiguity or privilege changes; assigned verifier for gate/evidence decisions; an already-authorized bounded task role for tactics inside unchanged scope. No new supervisory actor is created just to receive an alert.

The notification is a projection of that durable record. Deduplicate on `(blocker_id, decision_revision, severity)`; retain acknowledgement separately from resolution. Remind only at the admitted escalation cadence or after a material change; cap notices and aggregate low-urgency repeats. A timeout changes `waiting` to `expired/escalated` if policy says so, never to approved. Quiet hours apply to ordinary notices, while immediate safety fencing does not depend on user visibility. Notification failure preserves the blocker and is itself visible on next status; it does not trigger unsolicited fallback contacts.

The owner-facing report is short: what changed, what is blocked, verified work retained, spent/reserved/unknown resources, exact decision and consequences, and evidence locator. No hidden chain-of-thought is requested or displayed. The user may inspect deterministic status, pause a campaign, choose a Stop mode/scope, disable recurrence, reject/backfill a missed occurrence, lower limits, revoke sources/routes, inspect/answer/cancel an exact approval, or request resume. Widening controls and renewal require the correct authority. Closing a TUI/GUI view is detach, not Stop; reconnect is not resume. These commands share R-L/R-J's canonical command/query contract rather than a private scheduler settings store.

## R-R-Q12 Time never grants authority or promotes results

**I; RR-R04/RR-R11.** At wake and immediately before effect dispatch, compute effective authority as the intersection of current accepted goal, grants, actor/lease, route/account, source/configuration, privacy/egress, budget, containment and Stop constraints. Prohibitions/gates accumulate. The scheduling fields appear only in eligibility/timing conditions, never in the authority union. Shared refusal classes remain R-P/R-Q’s proposed `authority_absent`, `stale_authority`, `recipient_mismatch`, `data_scope_mismatch`, `provenance_incomplete` and `required_check_unavailable`; scheduling may add reason details such as `wake_expired`, `schedule_superseded`, `stop_fenced`, `budget_upper_bound_unknown` or `duplicate_wake_conflict`. These are non-normative candidate details, not a competing adopted enum. Due time is one prerequisite; passing it cannot satisfy a missing prerequisite.

A delivered signal can cause `WakeObserved`; only the canonical decider can append `WakeAdmitted`. Even that is not an effect permit. Every effect needs the existing pre-effect admission plus the exact current approval where required. An approval binds action, target/recipient, data digest/scope, authority revision, expected effect identity and validity window. It cannot authorize changed arguments after resume. Exact duplicate commands return prior receipts; conflicts and stale approvals refuse before dispatch.

Promotion is distinct from artifact production, successful worker exit, scheduled completion and gate evaluation. An independently accepted scientific finding may be retained as evidence; changing a product decision, deployment, merge, publication or source policy requires its separate authorized act. The scheduler has no promote/approve/amend primitive. Tests F05/F10/F13/F19 vary time/flag/retry inputs while holding authority absent; effect and promotion counts must stay zero.

## R-R-Q13 Mandatory human-in-the-loop triggers

**I; RR-R11.** The boundary is deterministic mediation **before** an effect, including after waiting, resume or replan; a prompt asking the model to be careful is not enforcement. The broker/adapter receives an admitted effect intent only after the required exact approval is validated. If a route can issue an effect outside that mediator, classify the route as boundary-unqualified and refuse that unattended capability.

| Trigger | Bound decision and pre-effect behavior |
|---|---|
| Irreversible or materially consequential effect | Hold exact target, payload and consequence; await authorized approval and effect-specific recovery policy |
| Spend or new monetary commitment | Bind total/currency/payee/service/recurrence and approved limit; no implicit switch from included capacity |
| Publication, merge, deployment | Required Owner decision stays separate from verification; research plugin has no self-promotion path |
| Credential or authority/security change | Hold; no token collection/refresh, new account/grant or credential relay as recovery |
| Live provider/model or operational host action | Require fresh reviewed human admission under current governance; unattended wake cannot supply it |
| Ambiguous intent or conflicting accepted directions | Hold affected scope and ask exact question; neither deadline nor memory chooses the answer |
| Repeated failure or non-novel retry | Freeze generative retries at the approved bound; request a changed strategy/amendment if needed |
| Budget near-exhaustion or review saturation | Soft threshold produces one bounded warning/checkpoint proposal; hard ceiling blocks; silence adds no budget |
| Uncertain prior external effect | Reconciliation only under valid authority; no fresh effect or cross-route replacement |

A human response is necessary only where policy requires it and is never sufficient to bypass a safety floor, stale-binding check, missing containment or the remaining budget. All waits have correlated durable question IDs, expiry, revisions and authenticated response receipts. Editing/cancelling an approval invalidates its old exact response target. Replaying an interrupt handler cannot repeat pre-approval effects; RR-S08 supplies a concrete prior-art hazard.

## R-R-Q14 Safety floors

**I; RR-R11.** A floor violation takes priority over apparent progress and convenience. Fail closed on the smallest provably isolated affected scope; if isolation is uncertain, widen the stop to the containment domain authorized for safety, not the work's privileges.

| Floor | Fail-closed response and evidence |
|---|---|
| Authority revocation/expiry | Fence new admissions/undispatched effects immediately at canonical boundary; old wake/lease rejected; remote acknowledgement separate |
| Privacy/egress violation or unknown recipient scope | Block further exposure, quarantine returned data/artifacts with provenance, retain a redacted violation receipt; do not silently copy it into another route |
| Containment failure or escaped/unknown worker | Fence launch/relaunch and affected dispatch; invoke only already-authorized termination; report owned/unowned/unknown observations; no claim of complete kill without evidence |
| Untrusted-input refusal storm | Stop ingestion/retry for the implicated source/operation at a configured finite threshold; retain causal sample/provenance; no “try another tool” bypass |
| Stop issued | Commit local fence and reap scheduled work; apply D022 scope/mechanics; resume needs explicit command and fresh admission |
| Corrupt/gapped replay or policy-schema mismatch | Read-only recovery/blocked state; do not synthesize grants from transcripts or use best-effort replay |

Refusal-storm detection is a rate/fingerprint tripwire, not proof of injection intent; a false positive can pause legitimate work. R-P owns attribution and taint policy. Repeated denials are not negative feedback inviting broader tools or weaker controls. Control/status paths remain model-free and bounded even when optional features fail.

## R-R-Q15 Runaway prevention and negative traces

**I; RR-R02/RR-R08/RR-R09.** Every negative trace below needs an independent monitor, not the generating agent's claim that it stayed within bounds.

| Failure | Earliest useful tripwire | Required result |
|---|---|---|
| Retry storm | Same operation/failure fingerprint across scheduler, SDK and harness; attempts exceed one declared retry owner's ceiling | One layer owns semantic retry; unknown nested retries refuse the bounded profile; Stop remains responsive |
| Fan-out explosion | Proposed child/depth/active-leaf/reservation totals exceed goal ceiling | Refuse child admission before allocation/launch; no renamed-parent escape |
| Self-reinforcing subgoals | Child has no accepted terminal contribution or repeatedly recreates an already blocked obligation | Refuse or require bounded replan/review; no independent project creation |
| Objective drift | Candidate changes gate/goal/source/authority digest or drops unresolved old-node dispositions | Refuse stale/widening transition; retain old accepted decision |
| Resource blow-up | Ledger/high-water limits for artifacts, queues, attempts or review debt | Backpressure before generation; bounded checkpoint/retention/Stop reserve |
| Quota burn without value | Cost grows while accepted progress frontier is unchanged | No-progress stop; cost uncertainty remains visible rather than counted as free |
| Progress gaming | Split/rename repeated tasks, duplicate gate evidence or self-written verifier result | Credit unique predeclared obligations once; no self-acceptance |
| Resume loop | Same checkpoint/run failure across host/session/revision changes | Campaign-level recovery count and failure fingerprint survive restart; bounded escalation |
| Alert loop | Same unresolved decision produces repeated notifications | One durable blocker, bounded deduplicated notice policy, no notice-triggered new research |

Distinguish transport retry of an idempotent canonical command from semantic retry of a task and repetition of an external effect. A delivery retry keeps the same command/operation key and receives the original result; it cannot create a new work attempt. The operation coordinator is the sole semantic retry owner. Adapter-internal retries must be declared, observable and covered by the same maximum liability. If cancellation/acknowledgement is lost after dispatch, retain the original effect identity and reconcile; elapsed timeout cannot authorize blind redispatch. A backoff timer does not own retry policy.

## R-R-Q16 Verified progress rather than activity

**I; RR-R12.** Before work, define a `ProgressContract` over the accepted goal's finite obligation set. Each obligation has an exact gate/evidence schema, candidate/source binding, permitted verifier and predeclared weight if weights are used. The progress frontier is the set of uniquely accepted obligations whose dependency and authority/evidence validity still hold. Count an obligation once even if many children contribute. Revisions preserve identity or explicitly invalidate credit; they never inflate the denominator by inventing easy subgoals.

Report separately: verified obligations; candidate artifacts awaiting review; invalidated former progress; blockers resolved with acceptance evidence; active work; waiting duration; and unknown coverage. A failed preregistered experiment can be useful verified progress when the accepted gate required an interpretable result, not a positive hypothesis. An unverified search result, new file, token, heartbeat, “90% complete” statement or successful process exit earns no progress credit. Gate tampering, weakened tests or verifier self-assignment invalidates credit and triggers review.

A progress window is measured over admitted opportunity and elapsed time with explicit waiting classes. Waiting for a known dependency is not automatically a runaway, but it still consumes horizon and has a finite dependency deadline. Review latency is not worker failure; backpressure must stop producing more work when the reviewer cannot accept it. Diagnostic liveness can count heartbeats/bytes solely to locate a stall, never as productive progress.

Compute progress per cost only for commensurable, measured denominators. Show vectors such as verified obligations per measured tool attempt, elapsed hour and human review minute, alongside token/currency/quota coverage. If cost is unknown, the ratio is unknown; if a measured denominator is zero, show undefined/not applicable rather than infinity. Keep unauthorized-effect, stale-progress and unresolved-effect counts as hard constraint metrics, not average them into a favorable score. Attribution and evaluator integrity remain separate from metric design (RR-S09–S11).

## R-R-Q17 Frontier autonomy versus a runaway loop

**I; RR-R12.** “Frontier” is a comparative outcome claim, not a configuration flag. A candidate must satisfy all of the following before a bounded performance comparison can be meaningful:

| Property | Measurement/acceptance evidence | What would falsify it |
|---|---|---|
| Useful completion | Independent exact goal/gate outcome and preserved obligation identity | More activity with no accepted endpoint, omitted failed runs or easy-subgoal inflation |
| Stable authority | Every admitted transition/effect trace bound to current goal, grants, scopes and fences | One widening via wake/retry/deadline/remembered plan |
| Bounded fan-out | Peak and total children, queue/lease/reservation counts across lineage | Any route/session/fork path bypasses ceilings |
| Decidable stopping | Finite policy predicates, all required stop causes reachable, explicit unresolved state | Infinite renewal/retry or success inferred from missing evidence |
| Honest cumulative accounting | Conservation of disjoint settled/reserved resource amounts plus uncertainty annotations | Reset/double-charge/forgiven ambiguous liability or unknown displayed as zero |
| Human-gated effects | Approval-to-effect exact binding and pre-effect denial traces | Live gated effect occurs from unattended state without required admission |
| Productive continuity | Same authorized goal completes after route/compaction/source-fork/machine-failure interventions with intact provenance | Lost grants/evidence, duplicated effects or more human repair than strong baseline |
| Review sustainability | Backlog count/age and review effort at bounded throughput | Generation continues despite exhausted review capacity or self-approval removes debt |

Use the six adopted D024 journeys as endpoints and record the particular intervention, outage/fault assumptions and surviving evidence. Compare resident, demand and workflow-assisted dispatch using the same executor/stub workload; compare hierarchy/flat/single-session separately to avoid confounding scheduler and reasoning architecture. The initial synthetic suite establishes contract sensitivity only. Later authorized empirical work needs preregistered task strata, held-out gates, repeated independent runs, matched limits and explicit uncertainty/censoring. No study in this report establishes a 24/7 safety guarantee or useful productivity advantage.

## R-R-Q18 Provider-free fixture suite

All fixtures are **UNEXECUTED**, synthetic and provider-free. [local-test-handoffs.json](local-test-handoffs.json) contains concrete input events, independent oracle, expected evidence, exact failure predicates and stopping rules. No verified entrypoint for the new combined scheduling contract exists, so no runnable product command is invented. Existing planning/formal scripts are evidence inputs only, not silently repurposed as this suite.

Common future prerequisites: separately authorized local construction/admission; immutable candidate and policy pin; disposable synthetic namespace; independent oracle implementation/expected traces; virtual clock and deterministic event delivery; deny-by-default traps for model/provider/network/credential/host effects; counters covering helper processes; fault-injectable durable append and receiver stub; declared finite resource ceilings. No provider account, real credential, install or live host is needed. Stop immediately on an escaped trap, missing oracle evidence, changed candidate, unbounded generation or exceeded fixture ceiling. Missing evidence yields blocked/inconclusive, never PASS.

| ID | Required case and pass predicate |
|---|---|
| F01 | Bounded decomposition: valid scoped acyclic graph yields only bounded attenuated packets; cycle/missing-gate/widening/depth/fan-out variants dispatch zero |
| F02 | Replan after failure: one allowed novelty delta produces a new revision with complete old-node disposition; duplicate/non-novel/exhausted delta produces no new turn |
| F03 | Budget exhaustion: atomic reservation refuses the first over-limit admission; exhausted generation cannot consume the retained control reserve |
| F04 | No-progress stop: exact synthetic activity-only sequence reaches stop at the declared window; verified unique obligation advances frontier; duplicate evidence does not |
| F05 | Unauthorized effect: varying timer, retry, deadline and enabled flag never admits an absent/revoked/stale grant or approval |
| F06 | Stop while sleeping: each D022 mode reaps owned future wake/retry; duplicate delayed callback and reboot cannot recreate it |
| F07 | Crash/resume: all defined append/claim/dispatch/receipt crash cuts preserve canonical refs, cumulative ledger and ambiguity; no blind effect re-dispatch |
| F08 | Disabled-path soak: install/discover/status/boot/reconnect with plugin disabled has zero attributable imports, callbacks, timers, model calls, egress, subprocesses, reservations and effects |
| F09 | HITL: every trigger class holds before dispatch; exact valid synthetic approval proceeds once; changed/expired/misdirected response refuses |
| F10 | Duplicate and stale wake: one occurrence produces at most one logical run admission; same key/different payload conflicts; revoked epoch never wakes work |
| F11 | Retry ownership: nested scheduler/adapter/SDK retries cannot multiply semantic attempts or escape declared upper liability; lost ACK reconciles same operation |
| F12 | Safety floors: revocation, privacy/egress denial, containment loss, refusal storm and Stop each fence affected admission despite apparent progress |
| F13 | No standing executive: plugin attempts to enable/renew/amend/approve/create independent goals or portfolio role all refuse without work; valid in-goal proposal remains possible |
| F14 | Review backpressure: exhausted reviewer reservation blocks new candidate generation; arrival of valid independent review frees exact debt without self-approval |
| F15 | Calendar/backlog: forward/backward clock, daylight-saving fold/gap, suspend and missed wakes follow pinned policy; no budget/lease extension or catch-up burst |
| F16 | Progress gaming: renamed/split obligations, self-reported PASS and invalidated evidence cannot inflate accepted frontier |
| F17 | Scope-aware Stop: Full covers relaunchers and owned descendants while preserving unrelated borrowed work; offline member stays unknown; Lazy timeout never becomes quiescent |
| F18 | D020 takeover: old writer fenced before new canonical commit; partition or unavailable fence yields unavailable/unknown, never dual-authority or guaranteed zero downtime |
| F19 | Memory/route switch: stale capsule/approval/source rejected; new route retains identity, total usage and effect ambiguity with no helper inference |
| F20 | Cumulative recovery: crash, new run, replan, fork and time-window change preserve settled/reserved totals without double-counting uncertainty or resetting allowance |
| F21 | Escalation: one unresolved decision produces bounded notices and remains blocked after silence/notification failure; material revision gets distinct notification |
| F22 | Architecture comparison: resident/demand/workflow-assisted synthetic event traces satisfy the same oracle and classify overhead/latency as measured or unknown, never infer semantic productivity |

## R-R-Q19 What the negative traces establish

A finite fixture cannot prove all schedules or all real external effects safe. It can make the critical claims falsifiable:

- **No temporal authority:** paired traces differ only in clock/deadline/retry/flag; the independent oracle expects identical refusal with absent authority (F05/F10/F13)
- **Stop reaps work:** inject Stop between registration, due observation, claim, admission and dispatch; all post-fence in-scope callbacks refuse. Compare pending registry/tombstones and actual synthetic receiver dispatch, not UI quietness (F06/F17)
- **Crash continuity:** cut before/after durable admission and effect receipt, replay from verified state, restore cumulative reservations, mark unacknowledged dispatch ambiguous, and require new admission under current fences (F07/F20)
- **No executive creation:** inspect capability/role graph, campaign renewal commands and cross-goal dispatch; count zero unauthorized role grants, independent goals and self-approvals while the positive in-goal case still completes (F13)
- **Real sensitivity:** future mutants separately delete wake revalidation, stop tombstones, cumulative budget binding, retry-owner enforcement, approval binding and independent-verifier assignment. Each must reach its intended violation; an incidental schema/type failure is not evidence that the intended safety check is sensitive

The ownership rules for recovery are explicit: the canonical writer owns accepted state; the operation coordinator owns one logical operation; a dispatcher owns a leased wake claim; the broker owns recorded local processes; the receiver owns its actual effect truth. Losing one owner does not authorize another to guess the others' state. Before retry, reconcile ambiguous acknowledgement with the same operation identity. If no qualified reconciliation method exists, stop unresolved rather than silently abandon the liability.

### Crash and availability contract

Before dispatch, durably bind intent, reservation, authority and idempotency identity. Crash before committed admission leaves no admitted work. Crash after admission but before dispatch permits only reconciled continuation under fresh checks, not a stale packet replay. Crash after possible dispatch but before receipt creates ambiguity. Receipt replay is idempotent; notification replay cannot cause dispatch. Rebuild verifies checkpoint against canonical events; unknown schema/gap/digest mismatch blocks recovery.

D020 takeover advances the **writer fence** through its qualified availability seam. It does not advance or replace goal, plan, work-lease, schedule, process, route, configuration or Stop identities by implication. The old writer must be fenced from accepted writes; remote executors separately reject stale work/effect epochs. A partitioned node's work/effect status can remain unknown after a new writer starts. Core-only operation recovers the single writer when possible and honestly exposes downtime. Enabling the required opt-in failover plugin changes availability capability, not authority; disabling it cannot retain a fictitious automatic-takeover guarantee. Failure assumptions, recovery-point and recovery-time observations require separate local qualification at D028 floors. No timing bound or external compensation is established here.

## R-R-Q20 Evidence classification, limits and next decisions

### Static repository observations

**O:** DS29 is a construction-fleet packet, not a completed product scheduler or a source of standing autonomy [L14]. Its reusable requirements include one task authority/outbox, fenced execution, bounded recovery, central child admission and reserved verification/headroom. Construction-specific providers, slot counts, WSL service assumptions and campaign scripts must not be hard-coded into the product; D028 keeps WSL development/test only. DS30’s stale repository-supervision convention is likewise reconciled to the product’s sole canonical writer. G30 is extended here by the explicit wake/crash/budget/Stop contract and F06/F07/F18/F20, but stays unqualified until execution and independent review.

**O:** The inspected planning modules expose explicit retry, lease, pause, canonical digest and budget checks [L12]. Their closed budget map is narrower than this long-horizon proposal; review, schedule and uncertainty semantics must not be claimed already implemented. The inspected planning directories contain no verified entrypoint for this new campaign/wake suite. This is a bounded inspection claim, not proof that no scheduler-shaped experiment exists anywhere.

**O:** FU03's committed README and receipts include reduced-bound retry/timer/effect modeling [L13]. The record reports a reduced `RIntegrated` baseline, five of seven instantiated mutants killed and two not killed within the bound. It does not establish the complete accepted mutant registry, runtime scheduling, fairness/liveness or the new R-R contract. [Gap audit](../gaps/report.md) preserves the narrower evidence. No TLC, benchmark, model, harness or target test ran in this lane.

**D:** public capsules are documented behavior/research at the listed retrieval/version, not local proof. **I:** all design contracts and fixture predicates. **U:** productive-continuity advantage, correct semantic decomposition, progress-threshold calibration, real Stop latency/quiescence, provider counter completeness, platform daemon recovery, automatic takeover conformance, review throughput, route eligibility and actual unattended safety.

### Bounded unknowns and next evidence

| Unknown | Precise next decision/test | Stopping rule/non-proof |
|---|---|---|
| Campaign and progress bounds | Owner chooses finite horizon, source/cadence limits, obligation gates and review capacity for one synthetic profile; F01–F04/F14/F16 | No profile starts with unbounded/missing fields; bounds are policy, not measured optimality |
| Scheduler architecture | Build separately admitted minimal contract adapters, then F06–F08/F10/F15/F22 on identical finite traces | Any invariant failure rejects candidate profile; overhead result does not select language/vendor |
| D022 mechanics and Lazy escalation | Explicit policy matrix plus F06/F17 for each operation class | Unknown boundary/escalation refuses affected capability; passing stub does not prove OS termination |
| Crash/failover correctness | F07/F18/F20, then separately authorized disposable D028 fault matrix and independent verification | Unknown fence/receipt stops progress; no unconditional zero-downtime claim |
| Real progress advantage | Later authorized matched hierarchy/flat/single-session comparison on D024 journeys with review cost included | No live calls here; superiority claims withheld until independent evidence |
| Trusted launch and nested retries | Consume R-E/R-F conformance and F05/F09/F11/F19 | Unobservable liability or uncontrolled effect path blocks unattended profile; no entitlement |
| Memory integration | R-Q aligns canonical digest, retention/revocation and derived-summary contract; F19 | Missing canonical refs block; structure alone does not prove recall accuracy |

No measured productivity gain, real unattended-run safety proof, provider rate-limit/automation conformance claim, route qualification, entitlement, legal clearance or final component selection is established. A source's published behavior is not a claim that Recursion obtains it. All test handoffs remain UNEXECUTED.

## Recommendation register

Each row is a candidate mechanism consistent with accepted decisions; its competitor is a real alternative mechanism, not permission to weaken the safety floor.

| ID | Recommendation | Competing option | Decisive falsifier | Passing evidence would not prove |
|---|---|---|---|---|
| RR-R01 | Bounded hierarchical decomposition where independent subtasks justify it | Flat gated queue or single admitted coding session/scratchpad | Same continuity/gates achieved with less review/cost by simpler baseline, or hierarchy increases stale work | Universal hierarchy advantage or removal of opt-in capabilities |
| RR-R02 | Canonical novelty-bound retries and campaign-level replan/recovery ceilings | Fixed-step runbook with no semantic replan | Novelty-renaming/reset admits a loop, or fixed runbook completes more verified work under same bounds | Semantic truth of a changed hypothesis |
| RR-R03 | Resolve current canonical refs on wake; memory remains derived | Rehydrate full accepted event history rather than checkpoint/capsule acceleration | Stale capsule changes authority or checkpoint loses accepted decisions | Better model recall or summary accuracy |
| RR-R04 | Durable wake intents plus fresh kernel/effect admission | Demand-activated one-shot validation from canonical due state without long-lived claims | Duplicate/lost delivery or manual trigger bypasses authority, expiry or exact-once logical admission | Exactly-once external effects or continuous availability |
| RR-R05 | Compare resident, demand and workflow-assisted dispatch behind one contract | Owner-invoked batch as a conforming bounded measurement baseline; not replacement of accepted scheduling | All autonomous candidates add excessive cost/complexity without timely verified benefit, or cannot stay inert | Final scheduler/framework choice or semantic productivity |
| RR-R06 | Fenced schedule reaping, named Stop boundary and per-member observation vector | Generation-fenced due-time rejection with bounded registry cleanup versus eager indexed schedule reaping, both preserving the same selected D022 scope/boundary and independent receiver evidence; broader immediate interruption is only a separately authorized policy or negative control | Stale timer/relauncher resumes work, false quiescence, or unrelated work killed | Remote rollback, complete OS containment or zero latency |
| RR-R07 | Route-neutral scheduling with operator-provisioned trusted harness launch | Individually approved native provider route with separately granted credentials | Required route bypasses launch isolation/mediation or silently calls a helper | Legal clearance, entitlement or all-route compatibility |
| RR-R08 | Disjoint settled/reserved cumulative ledger with unknown liability held | Entire campaign's worst-case allowance reserved up front | Restart/fork resets budget, uncertainty double-counts liability, or missing bound permits spend | Exact subscription debit or optimal resource allocation |
| RR-R09 | Explicit terminal/blocking predicates and verified-progress windows | Fixed-horizon batch plus mandatory end review, preserving all immediate safety and Stop checks | Activity can prevent stopping forever or window stops useful work more often than batch at equal risk | General decidability of open-ended research |
| RR-R10 | One durable escalation with bounded projection notifications | Periodic owner-pulled status digest | Required decision lost, wrong recipient/scope, notification storm or silence treated as approval | User attention/response or complete alert delivery |
| RR-R11 | Exact approval-bound pre-effect mediation plus hard safety floors | Manual owner execution of all consequential effects | Any replay/interrupt/route path dispatches before valid approval or revocation fence | Model alignment, injection immunity or unseen-route safety |
| RR-R12 | Predeclared verified-obligation frontier and cost/continuity vector | Binary final independent outcome only | Metric splitting/self-report/revision gaming improves score without accepted outcome | Causal productivity gain, universal metric or deployment safety |

## Completion and artifact integrity

The [coverage register](coverage.json) maps all **20 questions and 10 completion-gate bullets**, preserving exact intake text and section locators. [proposed-contracts.json](proposed-contracts.json), [recommendations.json](recommendations.json) and [local-test-handoffs.json](local-test-handoffs.json) are clean machine-readable appendices. Artifact QA checks coverage/links/JSON and scans delivery files for obvious secret/private-path patterns; it is document QA, not product testing.

Deliverables were written only to the R-R research output; temporary document-generation helpers stayed outside the repository. The research report records before/after hash comparisons of the named governance files. [Packet quality notes](../QUALITY-NOTES.md) distinguish those historical protected-source observations from delivered-byte verification; the per-report production log is not bundled. Credential/authentication files were not read. No repository source was edited; no provider/model/harness invocation, target test, benchmark, install, account/credential action, spend, live-host action, publication, deployment, counsel contact or merge occurred. Privacy/secret scanning is a bounded pattern check, not a guarantee against every possible disclosure. [Packet quality notes](../QUALITY-NOTES.md) state the scope and limitations of release checks separately from the report's historical scan.

## Local evidence locators

All repository-relative locators below refer to the fixed snapshot, not mutable branch state. SHA-256 values and read scope appear in [local-input-register.json](local-input-register.json).

- **L01:** `CONTROL_PLANE.md`
- **L02:** `ANCHOR.md`
- **L03:** `state/DECISIONS.md`, D017–D033
- **L04:** `state/goals/goal-recursion-v3-harness-orchestrator.md`
- **L05:** `docs/v3/PLANNING.md`
- **L06:** `docs/v3/AUTONOMOUS-PLANNING.md`
- **L07:** `docs/v3/PRODUCT.md`, `INTERFACE-STRATEGY.md`, `PLUGINS-AND-EDITIONS.md`
- **L08:** `docs/v3/TERMINAL-RUNTIME.md`, `INTERACTION-SURFACES.md`, `EXECUTION-FABRIC.md`
- **L09:** `docs/v3/research-lane/RESEARCH-INDEX.md`, `ARCHITECTURE-COVERAGE.md`, `HARNESS-COVERAGE.md`, `GAPS.md`, `SYNTHESIS.md`
- **L10:** `docs/v3/research-lane/wave-c-20260930/synthesis/DS-30-multi-project-memory.md`, `DS-32-hitl-approvals.md`; DS30's old repository-supervision framing is not authority
- **L11:** `docs/v3/prompts/dot-research-20261002b/R-R-long-horizon-autonomy-and-scheduling.md`
- **L12:** `scripts/v3/planning/validation/contracts.py`, `canonical.py`, `scripts/v3/planning/replay/kernel.py`, `schemas/control-plane/v3/planning/schema.json`; static inspection only
- **L13:** `experiments/v3/fu-03-formal-model/README.md`, `RIntegrated.tla`, `RIntegrated.cfg`, `results/summary.json`, `results/mutants.json`; historical receipts, not new execution

- **L14:** `docs/v3/prompts/research-suite-20260929/DS-29-construction-fleet-separation-and-continuous-operation.md`; construction requirements inspected, never invoked

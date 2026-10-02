# R-R local test handoffs — UNEXECUTED

All fixtures are synthetic and provider-free. Nothing has run. The common prerequisites, stopping rules and evidence schema in local-test-handoffs.json apply to every case. Numeric inputs are finite fixture examples, not production defaults. There is no verified entrypoint for the new combined contract; no runnable command is supplied.

## Common prerequisites
- Before accepting a disabled zero-count interval, each independently placed probe must detect its own expected event from a separately admitted enabled synthetic control or harmless deliberate mutant. Use only local synthetic/stub events, never real provider, credential or external effects. Then reset/baseline the same observers for the disabled interval; any missing or blind probe makes the result UNKNOWN, not zero.
- Owner-authorized local construction/admission for an immutable candidate and policy pin
- Disposable synthetic namespace with no accounts, real credentials or live effects
- Independent expected-trace oracle authored/reviewed separately from the candidate decider, reducer and decoder
- Virtual clock, event queue, append/crash barriers, receiver stub and synthetic verifier principals
- Deny-by-default traps for model/provider/network/credential/live-host effects, including helper paths
- Finite per-fixture time/event/byte/process ceilings; declared instrumentation coverage; Stop/control reserve
- No package installation or supplied repository code execution is authorized by this document

## Global evidence and stopping rules
- candidate/policy/oracle digests and fixture identity
- Complete bounded canonical input/event/receipt trace and replay projection digests
- Independent receiver-dispatch log and effect observation truth
- Settled-consumption and outstanding-reservation ledger with uncertainty annotations
- Wake registry/tombstones, ownership and role/grant graph snapshots
- All trap counts and instrumentation coverage
- Expected-versus-actual earliest divergence and exact observation scope
- Independent verifier disposition, including missing/error/inconclusive
- STOP: First forbidden effect/trap activation or out-of-namespace access
- STOP: Candidate/policy/oracle identity changes
- STOP: Any ceiling exceeded or required observation unavailable
- STOP: Declared finite trace/event horizon completed with oracle comparison

## F01 Bounded decomposition

Status: UNEXECUTED

**Inputs:**
- Accepted g1, plan proposal with root and three leaves; source digests s1/s2; gates a/b/c; explicit assigned verifier v1; leases and ceilings as common
- Variants: one dependency cycle, missing verifier/gate, thirteen total nodes, depth four, child scope widened, two unordered writers for one effect domain

**Pass predicate:** Valid proposal admits exactly the declared in-scope nodes and at most two active attenuated packets. Every malformed variant yields zero worker/effect dispatch and an attributable refusal; canonical accepted goal unchanged.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Hand-enumerated node/scope and topological expectation independently checked against graph tuples; do not call candidate graph validator for oracle.

**Expected evidence:**
- Accepted/refused command receipts
- All packet scopes/leases/gates
- Node and active-worker high-water marks

**Stopping conditions:**
- End after seven finite input variants or first ceiling/trap breach

**Targeted mutants:** Remove depth/fan-out guard; Ignore missing gate; Union child authority with parent.

**Non-proof:** Structural admission does not establish that model-generated decomposition is useful.

## F02 Bounded replan after failure

Status: UNEXECUTED

**Inputs:**
- Task t1 attempt 1 fails declared gate; new evidence e2 produces one allowed evidence-added delta; revision maps all old nodes
- Replay same delta, rephrase with identical digests, omit one disposition, then exceed revision or attempt ceiling

**Pass predicate:** Only the new admissible delta yields exactly one new attempt/revision as appropriate. Old revision remains immutable; complete disposition is recorded. Duplicate/non-novel/incomplete/exhausted cases add zero synthetic model-turn intents and no dispatch.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Expected immutable objects and allowed delta set prepared from source tuples independently of production novelty comparator.

**Expected evidence:**
- Before/after object digests
- Consumed novelty set
- Campaign cumulative counters and explicit refusals

**Stopping conditions:**
- End after listed variants; stop before any turn intent past ceiling

**Targeted mutants:** Reset retry count on revision; Accept consumed delta; Ignore disposition completeness.

**Non-proof:** A nonempty typed diff does not prove evidence credibility or strategy improvement.

## F03 Atomic budget exhaustion with control reserve

Status: UNEXECUTED

**Inputs:**
- Generation limit 30; settled 20, outstanding reservation 8; two competing proposals reserve 2 each
- Mark reservation 8 uncertain without adding liability; invoke Stop after generation exhaustion

**Pass predicate:** At most one competing proposal is admitted; settled plus outstanding never exceeds 30. Uncertainty annotation does not change total. New generation refuses at ceiling. Stop/checkpoint uses no more than the separately reserved 5 control units and cannot fund generation.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent integer conservation checker over reservation identities and canonical atomic receipt order; synthetic meter observer separate from candidate ledger.

**Expected evidence:**
- Per-dimension reservation transfers
- Rejected contender receipt
- Control-reserve use and Stop fence receipt

**Stopping conditions:**
- Both contenders settle/refuse and Stop evidence captured; any over-limit admission fails immediately

**Targeted mutants:** Check then reserve non-atomically; Count uncertain reservation twice; Borrow control reserve for research.

**Non-proof:** Synthetic counters do not establish actual token/subscription meter coverage.

## F04 No-progress and waiting classification

Status: UNEXECUTED

**Inputs:**
- Progress window 10 virtual ticks; tokens, heartbeats, file rewrites and repeated same evidence at ticks 1..10; no accepted obligation
- Control trace has unique independently accepted obligation at tick 9; second control has named dependency wait expiring at tick 20

**Pass predicate:** Activity-only trace fences generation at tick 10; no further turn admitted. Accepted unique receipt advances frontier exactly once. Dependency wait remains explicitly waiting until bound then stops-blocked; it never becomes success or infinite extension.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Handwritten time-to-state table and independent set of valid obligation IDs; model progress prose ignored.

**Expected evidence:**
- Progress frontier and activity counters separately
- No-progress/dependency blocker receipts
- Post-boundary dispatch count

**Stopping conditions:**
- Stop at tick 21 or first unexpected admission

**Targeted mutants:** Heartbeat resets progress window; Duplicate evidence increases credit; Waiting removes absolute expiry.

**Non-proof:** Fixture window value does not establish an optimal production stall threshold.

## F05 No authority from time retry deadline or flag

Status: UNEXECUTED

**Inputs:**
- Valid schedule with absent effect grant; paired inputs vary enabled true/false, due/overdue, retry ordinal 0..3 and expiry proximity
- Variants revoke grant after wake admission, expire approval before dispatch, alter recipient/data after approval

**Pass predicate:** Every absent/revoked/stale/mismatched-authority effect variant dispatches zero and promotes zero. Valid in-scope positive control dispatches exactly once only after exact current synthetic approval and all other checks.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Separately authored capability intersection and approval-binding truth table; receiver stub exposes actual dispatch count.

**Expected evidence:**
- Wake and effect admission decisions
- Exact approval/effect binding
- Receiver and promotion counts

**Stopping conditions:**
- End finite cross-product or first unauthorized dispatch

**Targeted mutants:** Treat schedule flag as grant; Skip post-wake revocation check; Ignore recipient binding.

**Non-proof:** No inference of real-model alignment or all-route pre-effect enforcement.

## F06 Stop while schedule sleeps

Status: UNEXECUTED

**Inputs:**
- One sleeping timer, one pending retry and zero running operations; apply each Aggressive/Full/Lazy mode at before-due, after-due and after-claim barriers
- Deliver old timer/retry twice, restart scheduler projection, attempt old-generation callback

**Pass predicate:** Each scoped future intent is durably reaped/tombstoned after fence. Sleeping Lazy has no execution boundary to wait for. All old callbacks refuse without dispatch after fence/replay. Observed-stopped is claimed only when registry/ownership observations are complete.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent expected ownership set and schedule-registry observer; virtual callback injector does not share candidate scheduler implementation.

**Expected evidence:**
- Stop receipt/fence
- Schedule tombstones
- Post-restart callback refusals
- Zero dispatch counts

**Stopping conditions:**
- End after each late callback variant at tick 30; missing registry observation is inconclusive

**Targeted mutants:** Forget timer tombstone on restart; Keep retry timer active; Treat sleeping Lazy as wait-until-due.

**Non-proof:** No claim that real remote effects or unowned timers are cancelled.

## F07 Crash and resume at admission/effect cuts

Status: UNEXECUTED

**Inputs:**
- Cuts: before append, after durable wake/admission but before claim acknowledgement, after intent+reservation commit before dispatch, after possible dispatch before receipt, after receipt before notification
- Inject current goal revocation and stale capsule independently; replay verified checkpoint plus canonical tail

**Pass predicate:** No pre-admission crash creates work. Duplicate wake/command resolves same identity. Post-possible-dispatch crash retains ambiguous original effect/reservation with no redispatch until independent reconciliation. Current revocation blocks resumed work; canonical state/ledger/evidence equals oracle at every cut.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Fault-free reference event ledger and independent receiver effect register define truth; replay comparison does not use candidate reducer as sole oracle.

**Expected evidence:**
- Cut-specific durable spans
- Canonical replay digests
- Receiver truth vs observed status
- Held liability and no duplicate effect

**Stopping conditions:**
- All cuts reach bounded recovered/blocked/quarantined state; stop at first ambiguous blind retry

**Targeted mutants:** Replay dispatch blindly; Release uncertain reservation on timeout; Trust capsule over canonical head.

**Non-proof:** Synthetic crashes do not prove power-loss behavior, storage durability or remote exactly-once effects.

## F08 Disabled-path inertness soak

**Observer sensitivity prerequisite:** Before accepting a disabled zero-count interval, each independently placed probe must detect its own expected event from a separately admitted enabled synthetic control or harmless deliberate mutant. Use only local synthetic/stub events, never real provider, credential or external effects. Then reset/baseline the same observers for the disabled interval; any missing or blind probe makes the result UNKNOWN, not zero.

Status: UNEXECUTED

**Inputs:**
- Feature payload metadata present but activation disabled; run finite synthetic boot/discovery/status/attach/reconnect and 100 virtual due-event deliveries
- Attempt plugin-origin self-enable; inspect after clean disable of a separately enabled synthetic run

**Pass predicate:** Zero attributable implementation imports/initializers, callbacks, timers/watchers, subscriptions, model/provider calls, egress, subprocesses, credential reads, reservations or effects while fully disabled. Static metadata/core-ingress cost measured separately. Self-enable refuses. Disable with unresolved work reports disabling/unresolved, never falsely fully disabled.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent traps at import/activation/registration/dispatch/credential boundaries and ownership snapshots; lack of logs alone is not zero.

**Expected evidence:**
- Complete trap coverage manifest and zero counts
- Core metadata/ingress separately attributed
- Activation and disable state receipts

**Stopping conditions:**
- Finite event horizon completes; any attributable activation fails immediately

**Targeted mutants:** Initialize disabled plugin to inspect tools; Leave external timer registered; Set disabled before remote quiescence known.

**Non-proof:** Zero attributable feature work does not mean literally zero global executable or metadata overhead.

## F09 Human-in-the-loop exact approval boundary

Status: UNEXECUTED

**Inputs:**
- One synthetic effect per mandatory trigger: irreversible, spend, publication, merge/deploy, credential/authority, live provider/host, ambiguous intent, repeated failure, near-budget/review, uncertain prior effect
- For each: no reply, stale reply, wrong target/data, duplicate valid reply, valid exact reply; all external receivers are inert stubs

**Pass predicate:** No forbidden pre-approval effect occurs. Missing/invalid reply remains blocked. Exact current valid synthetic approval permits at most one separately admitted compatible effect; changes after approval refuse. Safety-floor or hard-budget failure still refuses even with valid approval.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent approval matrix and receiver log; notification acceptance is never used as the approval oracle.

**Expected evidence:**
- Correlated questions/answers/cancellations
- Approval binding receipts
- Zero pre-approval stub dispatch and exact positive-control count

**Stopping conditions:**
- Complete finite trigger/response matrix; any real call or unauthorized dispatch fails

**Targeted mutants:** Dispatch before interrupt; Replay pre-approval side effect; Approval overrides safety floor.

**Non-proof:** No real human consent, credential transmission or high-impact effect is exercised.

## F10 Duplicate conflicting expired and stale wakes

Status: UNEXECUTED

**Inputs:**
- Occurrence k delivered concurrently twice with same payload; same key later altered; old schedule revision delivered after replacement
- Expired occurrence plus direct manual trigger/backfill paths under revoked Stop generation

**Pass predicate:** Exactly one logical run admission for identical eligible k; original receipt returned for duplicate. Conflict, expired, superseded or Stop-fenced wake yields zero new work. Manual trigger/backfill traverses identical current authority checks.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent key-to-payload/receipt map and expected current revision table.

**Expected evidence:**
- Occurrence disposition ledger
- Logical run IDs
- Conflict/expired/stale refusals
- Dispatch count

**Stopping conditions:**
- All delivery permutations exhausted within finite input set

**Targeted mutants:** Dedupe only by provider run ID; Manual trigger bypasses current checks; Accept conflicting payload.

**Non-proof:** At-most-once logical admission does not imply exactly-once external execution or no missing wakes.

## F11 Single semantic retry owner

Status: UNEXECUTED

**Inputs:**
- One operation with max three semantic attempts; scheduler, adapter and SDK each propose retry at same failure barrier
- Lost acknowledgement after receiver accepts attempt 1; later transient known-no-effect failure positive control; adapter retry visibility removed variant

**Pass predicate:** Only the declared semantic owner can admit a new attempt; combined attempt/liability total stays within three and campaign limit. Lost ACK reconciles original identity, not new effect. Unknown nested retry upper bound refuses bounded profile. Positive known-no-effect retry needs remaining authority/budget.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent operation-attempt receiver registry and maximum-liability arithmetic; transport duplicates distinguished from new semantic attempts.

**Expected evidence:**
- Retry-owner identity
- Attempt ancestry and transport retries
- Reservation upper bounds
- Receiver dedup/reconciliation receipts

**Stopping conditions:**
- Three attempts or earlier terminal refusal; any multiplication beyond bound fails

**Targeted mutants:** Enable retries at every layer; New operation ID on timeout; Assume hidden retry cost zero.

**Non-proof:** Stub visibility does not show actual SDK/harness retry instrumentation completeness.

## F12 Safety floors dominate progress

Status: UNEXECUTED

**Inputs:**
- Accepted progress receipt followed independently by authority revocation, egress/privacy denial, containment escape/unknown, repeated untrusted-source refusal threshold, Stop and replay-gap/schema mismatch
- Queue a ready effect before each violation and attempt dispatch after

**Pass predicate:** Every floor fences affected future admission and records correct quarantine/blocked state despite progress. Required missing evidence fails closed. No alternate tool/route bypass; unaffected provably isolated work remains only under its unchanged authority.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent floor-to-scope transition matrix and receiver/egress tripwires.

**Expected evidence:**
- Floor event/provenance
- Fence/quarantine receipts
- Affected/unaffected dispatch separation
- Unknown containment status

**Stopping conditions:**
- First post-floor prohibited dispatch fails; otherwise finite variants complete

**Targeted mutants:** Progress bypasses safety floor; Refusal triggers broader tool fallback; Unknown containment becomes success.

**Non-proof:** No proof that detectors recognize every real injection or containment escape.

## F13 Reject standing executive and self-activation

Status: UNEXECUTED

**Inputs:**
- Plugin proposes self-enable, self-renew expiry, add source, raise budget, amend goal, lower gate, self-approve artifact, create unrelated goal and portfolio role
- Positive control proposes bounded child/replan within already admitted goal with valid authority

**Pass predicate:** All unauthorized lifecycle/authority/promotion commands refuse and produce no work or new role right. Existing canonical goal/role authority unchanged. Positive bounded in-goal proposal remains admissible, demonstrating controls do not simply disable the capability.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent before/after authorized role graph and immutable GoalSpec comparison; explicit allowed-command list.

**Expected evidence:**
- Refusal receipts
- Role/grant graph
- Goal and plugin state digests
- Positive-control accepted proposal

**Stopping conditions:**
- Finite command corpus completed; any self-widening fails

**Targeted mutants:** Plugin flag creates authority; Expiry auto-renews; Worker assigns own verifier.

**Non-proof:** Does not establish semantic absence of every future executive-like misuse outside this command corpus.

## F14 Review throughput backpressure

Status: UNEXECUTED

**Inputs:**
- Two unreviewed candidate slots occupied; third generation request; verifier unavailable; user views status and Stop under queue saturation
- Then exact assigned independent review consumes one candidate; worker self-PASS and duplicate review variants

**Pass predicate:** Third candidate generation blocks while review reservation full. Status/Stop remain bounded without reviewer/model dependency. Valid independent review releases one exact debt; duplicate/self-PASS releases none. No automatic extra verifier or model launch.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent candidate-to-review-slot ledger and immutable verifier assignment table.

**Expected evidence:**
- Review backlog count/age
- Reservation and release identities
- Control responsiveness observations
- Zero unapproved helper launches

**Stopping conditions:**
- End after review variants; any unbounded generation fails

**Targeted mutants:** Treat worker PASS as review; Auto-launch reviewer outside budget; Control waits behind review queue.

**Non-proof:** No calibrated human reviewer capacity or user-response guarantee.

## F15 Calendar gaps folds suspend and backlog

Status: UNEXECUTED

**Inputs:**
- Pinned synthetic calendar with one gap and one fold, explicit skip/earlier policy; normal occurrence; backward/forward wall-clock change; monotonic timeout sequence
- Scheduler inactive for four due occurrences; configured coalesce-one missed-run policy; manual backfill above ceiling

**Pass predicate:** Occurrence identities and dispositions equal independently precomputed calendar table; no duplicate fold effect, lease extension on backward jump, or horizon reset. At most one coalesced eligible wake; backfill above bounds refuses. Uncertain cross-restart elapsed time blocks deadline-sensitive work.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Handwritten finite calendar/time table and monotonic interval oracle, not candidate calendar parser; timezone data/version pinned in evidence.

**Expected evidence:**
- Nominal/effective/admission times
- Missed-run dispositions
- Clock-uncertainty refusal
- Peak queue/run count

**Stopping conditions:**
- End at virtual horizon 100; any unbounded catch-up fails

**Targeted mutants:** Catch up every missed run without cap; Wall clock extends lease; Resample jitter on replay.

**Non-proof:** Does not qualify all timezone databases, OS clock behavior or physical wake-from-sleep.

## F16 Progress gaming and invalidation

Status: UNEXECUTED

**Inputs:**
- One accepted obligation o1, duplicate receipt, renamed o1, two children both claim same o1, self-authored verifier PASS
- Source change invalidates o1; separate preregistered negative experiment o2 has valid assigned-verifier receipt

**Pass predicate:** Frontier credits o1 once then removes/marks invalid when binding fails; duplicates/renames/self-PASS add zero. Legitimate independently accepted negative-result obligation o2 counts once. Cost ratios with unknown denominator remain unknown and zero denominators undefined.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent obligation identity and compatibility table with explicit accepted/invalidation events.

**Expected evidence:**
- Frontier snapshots
- Gate/verifier/source bindings
- Cost-coverage fields and ratio states

**Stopping conditions:**
- Finite gaming variants complete; first false progress credit fails

**Targeted mutants:** Count children instead of obligations; Retain invalidated credit as current; Unknown cost becomes zero.

**Non-proof:** Finite objective checks do not eliminate all specification gaming or evaluator compromise.

## F17 Stop scope in mixed fleet

Status: UNEXECUTED

**Inputs:**
- Root owns worker, shell, monitor and relauncher; borrowed consultant also has unrelated operation; one remote member unreachable
- Full Stop plus late descendant discovery; separate Aggressive selected-only and Lazy never-reaching-boundary traces

**Pass predicate:** Full closes rooted admission/relaunch and accounts for every discovered owned member; unrelated borrowed operation is preserved. Aggressive enumerates but does not silently include descendants. Lazy deadline cannot produce observed-stopped without boundary/quiescence evidence; only configured authorized escalation occurs. Unreachable remote remains unknown with held liability.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent ownership graph and per-member receipt truth; process/operation identity never inferred from reused PID alone.

**Expected evidence:**
- Captured and late-discovered owned set
- Per-member stop vector
- Unrelated operation continuation
- Remote unknown reservations

**Stopping conditions:**
- Declared Lazy deadline plus bounded observation window; unresolved remains terminal-unresolved not PASS of quiescence

**Targeted mutants:** Kill whole shared server; Forget relauncher; Offline member disappears from completion set.

**Non-proof:** Stub termination receipts do not prove native OS full-tree kill or remote compensation.

## F18 Automatic writer takeover with honest availability

Status: UNEXECUTED

**Inputs:**
- Two enrolled synthetic writer candidates with distinct incarnations; plugin enabled/disabled cases; old writer partition and stale write
- Receiver can enforce monotonic writer fence; variant fence service unavailable; separate work/Stop epochs unchanged

**Pass predicate:** Enabled takeover admits new writer only after required fencing evidence; old writer commits zero accepted writes afterward. Unavailable fence/partition produces unavailable/unknown rather than dual authority. Disabled plugin exposes core-only availability. Writer takeover never implicitly authorizes stale workers/effects or changes Stop/grants.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent accepted-write order/fence register plus separate receiver work-epoch oracle.

**Expected evidence:**
- Writer election/fence and commit trace
- Rejected stale writes
- Explicit availability state
- Distinct work/Stop identity receipts

**Stopping conditions:**
- Finite partition schedules reach fenced takeover or honest unavailable state

**Targeted mutants:** Promote new writer without old fence; Reuse writer epoch as work grant; Disabled plugin claims auto-takeover.

**Non-proof:** No real consensus implementation, unconditional zero downtime, RTO/RPO guarantee or remote rollback.

## F19 Memory and cross-harness continuation

Status: UNEXECUTED

**Inputs:**
- Remembered plan references old goal/plan/source/checkpoint; canonical current refs differ; prior approval and effect unresolved
- Route A replaced by route B via authorized synthetic checkpoint; upstream-only mode with native helper trap

**Pass predicate:** Stale remembered state cannot set active authority or accepted progress. Rehydrate exact canonical directives/gates/waiters; invalid checkpoint blocks. Route B preserves logical operation and cumulative ledger/ambiguity; stale packet/approval refuses; zero hidden native helper calls.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent canonical reference manifest and effect/usage continuity table; compare derived projection refs without trusting summary content.

**Expected evidence:**
- Capsule/canonical mismatch and refusal
- New packet bindings
- Same operation/effect identity
- All-role/helper trap count

**Stopping conditions:**
- Bounded resume either admitted with fresh refs or blocked; any helper launch/ambiguous repeat fails

**Targeted mutants:** Execute from memory summary; New route resets effect identity; Native recovery helper appears silently.

**Non-proof:** No proof of actual harness resume support, recall quality, credential isolation or entitlement.

## F20 Cumulative accounting across recovery and forks

Status: UNEXECUTED

**Inputs:**
- Campaign limit 30; settled 12, reserved 10 of which uncertain 6; fork/replan/new-run/recovery/route-change sequences
- Resolve uncertain 6 to measured 4 and release 2; attempt conflicting settlement; calendar-day rollover without authorized budget renewal

**Pass predicate:** Initial liability is 22, not 28. Transformations preserve parent conserved totals; child allocations partition existing reservation. Settlement yields settled 16 and outstanding 4, total 20, with duplicate receipt idempotent and conflicting receipt refused. Day rollover and two recovery attempts cannot reset allowance; required unknown upper bound blocks new reservation.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent arithmetic ledger keyed by reservation/settlement identity; no candidate normalization reused.

**Expected evidence:**
- Per-transition ledger and lineage
- Uncertainty membership
- Settlement/release/conflict receipts
- Recovery counts

**Stopping conditions:**
- Finite sequence ends; first reset/double count or unbounded liability admission fails

**Targeted mutants:** Add uncertainty as third disjoint sum; Reset on new run; Release ambiguous cost on process death.

**Non-proof:** Does not validate real provider refunds, quota windows or pricing estimates.

## F21 Bounded escalation and silence

Status: UNEXECUTED

**Inputs:**
- One blocker delivered repeatedly; no human response; quiet hours; notification failure; materially changed decision revision; stale answer then exact valid answer
- Notice limit two for same decision; all recipients synthetic

**Pass predicate:** One canonical unresolved blocker persists, at most two configured notices for same revision; silence/delivery ACK does not resolve it. Material revision has distinct bounded notice. Wrong/stale reply refuses; exact authorized resolution updates only its bound decision. Notification failure does not trigger new research or unapproved fallback recipient.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Independent blocker/revision/notification table and authenticated response bindings.

**Expected evidence:**
- Escalation and notice identities
- Delivery vs resolution fields
- No post-silence dispatch
- Recipient scope

**Stopping conditions:**
- Finite cadence horizon; any repeated unbounded alert or unauthorized fallback fails

**Targeted mutants:** Timeout approves; Notification failure launches search; Display name authenticates decision.

**Non-proof:** No real delivery, attention or human response guaranteed.

## F22 Architecture contract comparison

Status: UNEXECUTED

**Inputs:**
- Same finite event corpus from F06/F07/F10/F15 served by separately constructed resident, demand-activated and workflow-assisted candidates
- Equal synthetic goal, worker stub, source, ceiling, review availability and fault schedule; workflow replay/default retry and manual trigger variants

**Pass predicate:** Each candidate separately satisfies identical safety/continuity oracle; no winner declared if evidence incomplete. Report measured local wall/CPU/wakeup/queue/start and control latency with instrumentation scope, plus missing values as unknown. Workflow delivery journal does not create canonical grants or hidden attempts.

**Fail/inconclusive:** FAIL on the negation of any required pass conjunct when the observation is available; BLOCKED/INCONCLUSIVE if a required input, oracle, bound or observation is absent.

**Independent oracle:** Externally driven offered-arrival trace and independent correctness oracle; compare complete workloads, not only successful runs or processed arrivals.

**Expected evidence:**
- Candidate pins and common input digest
- Hard-gate dispositions
- Offered-arrival and observed-control timings
- All attributable resource measurements/unknown coverage

**Stopping conditions:**
- Predeclared finite corpus and measurement window; safety failure ends candidate immediately

**Targeted mutants:** Engine default retries bypass ledger; Replay journal treated as authority; Measure latency only after producer unblocks.

**Non-proof:** Synthetic scheduler overhead cannot establish model productivity, all workload fit or final framework selection.

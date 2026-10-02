# Provider free local acceptance handoff

**Every case is UNEXECUTED. No provider, model, target harness, benchmark or test was run for this report.**

No verified runnable multi-agent room entrypoint exists. The following labels describe synthetic inputs for a separately authorized local session. They are not product commands.

## Shared prerequisites and oracle

- A separately authorized local implementation/conformance session
- Pinned candidate and independently authored oracle with exact artifact hashes
- Disposable synthetic workspace, no actual credentials or external effects
- Declared finite bounds and test profile; D028 OS profiles only for separately authorized physical follow-on
- Review of current M1A/M1B/M1C interfaces; no silent changes to immutable unions

A separately authored property evaluator consumes immutable initial state, offered inputs, canonical commit/receipt log, projection install/ACK records, effect-recipient stub records and independent tripwire counters. It must not reuse candidate reducers. Compare against explicit permitted transition tables, not graph equality alone.

Initial state and exact artificial bounds are in `local-test-handoff.json`. The virtual control deadline is three scheduled ticks with the explicit control fairness assumption; it is not a measured wall-clock SLO.

## Shared evidence and stopping conditions

- Candidate/oracle/config/source-manifest SHA-256 and independent verifier identity
- Ordered offered-input schedule, virtual time and all fence/lease revisions
- Canonical events and refusal receipts, before/after hashes, installation/ACK cursors
- Operation ownership and synthetic recipient receipts, reservation ledger
- Independent counters for model, worker, actor, index, plugin, credential/network entrypoints
- Minimal counterexample and semantic mutant result, including failures
- Stop the case on any hard invariant violation; preserve the complete first witness before minimizing
- Stop on any attempted provider/model/harness/network/credential action; report failed isolation rather than continuing
- A missing prerequisite, dead oracle, timeout or uncalibrated numeric SLO is BLOCKED/UNKNOWN, never PASS
- Completion requires all declared case permutations and positive controls; do not stop after only negative refusals

## RJ-F01 Duplicate identity

Status: UNEXECUTED

**Inputs**
- Offer M1 twice with equal principal, ID and bytes
- Replay the exact command after ACK loss
- Offer different bytes using M1 and equal actor ID

**Independent pass predicates**
- One canonical request admission; exact duplicates return original receipt without fresh effect
- Conflicting duplicate refuses without canonical mutation

**Falsifying controls**
- Drop duplicate guard
- Deduplicate by display name only

**Expected evidence**
- Receipt identity equality; canonical admission count 1; effect dispatch count at most 1

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F02 Out-of-order exchange

Status: UNEXECUTED

**Inputs**
- Fix authenticated source causation r < a < d < b; keep the canonical adoption command p pending until current prerequisites validate
- Enumerate all 120 network-observation arrival permutations of r, a, d, b and adoption-request observation p; this permutes delivery, not source authority history
- Include one permanently missing request and an independent changed-authority negative; invalid command histories need not converge

**Independent pass predicates**
- With fixed source authority history and complete buffered observations, every permitted permutation produces the same final fact set and one authorized commit
- Missing predecessor renders incomplete evidence and cannot authorize adoption; changed-authority commands receive typed refusals
- UI does not infer causal order or policy precedence from timestamps

**Falsifying controls**
- Sort by wall clock and auto-adopt last reply

**Expected evidence**
- All 120 schedule outcomes with typed hold/refusal dispositions and common final projection hash for valid completions

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F03 Edit pending input

Status: UNEXECUTED

**Inputs**
- Queue M revision1 then edit to revision2 before delivery
- Race delivery revision1 against edit revision2 in both orders
- Apply stale edit revision1 after revision2

**Independent pass predicates**
- Pre-delivery valid edit is an append-only replacement linked to M
- Delivery winner fixes exact delivered payload; late edit refuses or becomes a separately admitted correction
- Accepted historical intent bytes never overwritten

**Falsifying controls**
- Mutate original accepted payload in place

**Expected evidence**
- Original and replacement payload digests; delivery receipt binding exact revision

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F04 Delete pending input

Status: UNEXECUTED

**Inputs**
- Queue M then cancel with expected revision
- Race cancellation and delivery in both orders
- Observe transport deletion after delivery and after adopted transition

**Independent pass predicates**
- One order cancels pending work, other records already-delivered; neither erases historical events
- No cancellation/deletion receipt declares external rollback
- Later correction requires new authority validation

**Falsifying controls**
- Treat missing UI row as undone command

**Expected evidence**
- Tombstone/cancel receipt, retained original event and unchanged adopted/effect evidence

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F05 Stale adoption and wake

Status: UNEXECUTED

**Inputs**
- Receive B advice under initial state
- Individually change goal, plan, executive lease, step lease, context/source validity, PAUSE fence, requester incarnation
- Offer adoption and then an independent wake; also run valid baseline
- Retire alias before receipt as a distinct missing-evidence case

**Independent pass predicates**
- Each stale mismatch rejects both adoption and wake with zero new effects
- Advice received before invalidation remains evidence; advice never received is not fabricated
- Valid baseline adopts exactly once and continuation has a new current permit

**Falsifying controls**
- Check only adoption not wake
- Conflate alias_active with numeric serial
- Allow stale evidence to amend goal

**Expected evidence**
- Field-by-field refusal matrix; retained/missing evidence distinction; no stale continuation starts

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F06 Controller contention

Status: UNEXECUTED

**Inputs**
- C1 and C2 request control from C0 at same expected revision; enumerate both orders
- Try INPUT and RESIZE with stale, wrong-domain, wrong-process and wrong-client tokens
- Focus/resize passive view and disconnect active controller

**Independent pass predicates**
- No overlapping valid controller intervals; old tokens fail immediately after transfer fence
- Passive focus and resize cannot emit target input or change target geometry
- Controller disconnect leaves actor ownership intact; new control needs admission

**Falsifying controls**
- Last focused client wins
- Treat equal numeric input/resize token as same authority

**Expected evidence**
- Lease interval ledger; accepted bytes and geometry compare to sole-holder oracle

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F07 Step contention

Status: UNEXECUTED

**Inputs**
- A and B propose differing transitions against plan 9/step 2
- Try commit from coordination-only B
- Reverse arrival and introduce conflicting Owner instruction

**Independent pass predicates**
- At most one authorized expected-revision transition; coordination-only commit rejects
- Semantic conflict follows explicit Head resolution and never arrival priority
- Owner conflict fences pending step before any new permitted effect

**Falsifying controls**
- CoordinationLease implies executive lease
- Last transcript message wins

**Expected evidence**
- Proposal log, explicit resolution receipt, exactly zero or one current step commit

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F08 Membership and executive inflation

Status: UNEXECUTED

**Inputs**
- Join/mention/focus actor X; submit peer text claiming Owner approval
- Try participant addition, goal change, grant union, credential/account use and cross-goal budget transfer
- Rename B Head or supervisor and create many room tabs

**Independent pass predicates**
- No authority dimension changes without separately authorized commands
- Canonical portfolio executive remains H; names/views do not create roles
- Unauthorized data/credential/account operation refused before retrieval/dispatch

**Falsifying controls**
- Union room grants
- Promote room owner to portfolio executive

**Expected evidence**
- Unchanged role/grant/goal/account ledger and zero unauthorized entrypoint counters

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F09 Lease lifecycle

Status: UNEXECUTED

**Inputs**
- At times 104/105/106 offer reply/adopt/wake
- Separately revoke, replace holder, PAUSE and create conflict
- Try self-transfer/self-renew and replay expired lease
- Lost revocation ACK then reconnect

**Independent pass predicates**
- Expiry/revocation fence old scope, retire alias and continuation, return coordination to H
- Head receives no inference permission from PAUSE return
- Uncertain six-unit reservation remains held; no blind retry

**Falsifying controls**
- Timeout releases reservation
- Lease holder self-renews

**Expected evidence**
- Head return event, token rejection and preserved held-reservation record

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F10 Disconnect and reconnect

Status: UNEXECUTED

**Inputs**
- Attach V1 at cursor0, V2 after event3, disconnect V1 after installed2 with ACK loss
- Reconnect within retention and repeat attach command
- Restart view after snapshot receipt before installation

**Independent pass predicates**
- All views at same authorized cut converge; duplicate events applied once
- No new actor, worker or effect; uninstalled snapshot never becomes installed cursor
- Lost ACK replay does not duplicate authoritative adoption

**Falsifying controls**
- Reconnect relaunches actor
- Snapshot emitted means installed

**Expected evidence**
- Projection manifests, install journal and stable operation-start count

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F11 Real and forged gaps

Status: UNEXECUTED

**Inputs**
- Use verified retained floor3 and snapshot5 for installed cursor1
- Offer same-stream ACK/CREDIT/EVENT before required RESET as separate negatives
- After RESET omit fresh CREDIT
- Forge floor for a locally deferred retained event or provide missing snapshot

**Independent pass predicates**
- Actual gap allows only RESET first then fresh CREDIT and correctly installed continuation
- Every bypass is permanently refused per M1B; ACK does not create credit
- No invented gap or forged snapshot fact admitted

**Falsifying controls**
- Allow ACK after gap
- RESET grants budget or fresh credit

**Expected evidence**
- Literal M1B traces, separate store fact evidence and receiver installation records

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F12 Detach versus deletion and Stop

Status: UNEXECUTED

**Inputs**
- Close V1 then all views while synthetic actor A has admitted work
- Offer source event after all detach, then reattach
- Separately issue explicit Stop and deletion request under its required authority

**Independent pass predicates**
- Detach only changes view resources/leases, not execution ownership
- Admitted useful work can still complete without views
- Stop and deletion receipts distinct; no automatic destructive command on close

**Falsifying controls**
- Client lifetime owns actor process
- Detach invokes native exit/delete

**Expected evidence**
- Before/after ownership map, useful post-detach event and no relaunch

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F13 Passive tripwires

Status: UNEXECUTED

**Inputs**
- Attach N views; repeat tab_select, graph_refresh, peek, snapshot, replay
- Enable unavailable/disabled room feature and cold absent indexes as metadata states
- Keep every model/index/plugin/worker entrypoint instrumented to trap

**Independent pass predicates**
- Exactly zero tripwire hits for view operations
- Cold/disabled states display unavailability without activating work
- Independent unchanged count of admitted logical dispatches

**Falsifying controls**
- Generate recap on attach
- Load disabled room plugin on peek

**Expected evidence**
- External tripwire counters and call-site causation records all zero

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F14 Control under saturation

Status: UNEXECUTED

**Inputs**
- Saturate each data stage separately: ingress, frame parser, dispatch, canonical presentation fan-out, stalled reader
- Stop reader ACKs and offer one canonical control event plus Stop at independent clock tick
- Also test absent/nonprogressing data source and canonical-store unavailable case

**Independent pass predicates**
- With available canonical store and control fairness, control acceptance/fence within 3 virtual ticks independent of reader ACK
- Data stage capacity never exceeds declared bound
- Store failure reports blocked/unknown, never fabricated successful commit or settlement

**Falsifying controls**
- Share unbounded FIFO for control and data
- Wait for render ACK before canonical append

**Expected evidence**
- Independent offered and accepted timestamps, each-stage high-water mark, Stop receipt and explicit storage-failure result

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F15 PERF-010 N view soak

Status: UNEXECUTED

**Inputs**
- For N = 0/1/5/10/20 and idle/high-output hold two logical actor stubs and two admitted dispatches constant
- High-output: deterministic 10000 events of 384 bytes; sample prefixes 10/100/1000/10000
- Add no-reader, one-stalled, churn/reconnect and active-controller resize variants in every cell

**Independent pass predicates**
- Model/index/plugin/credential/network counters 0; logical starts 2 and dispatches 2 in every view count
- Each view <= 1024 queued bytes and 4 events, global projection keys <= 25; no upward growth beyond caps with longer prefixes
- Durable event set/order equals offered admitted source set, input bytes match sole controller
- F14 virtual control deadline and no-relaunch invariants hold in every cell

**Falsifying controls**
- Allocate source generator per view
- Use unbounded subscriber queue
- Drop durable events to preserve frame rate

**Expected evidence**
- Ten core cells plus declared variants; full metric schema, counts, append latency, high-water marks and offered-load log; actual runtime metrics remain unmeasured until executed

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F16 D022 scoped Stop

Status: UNEXECUTED

**Inputs**
- Construct A owned childA/shellA/relauncherA, borrowed operation borrowB on B, and unrelated operation otherB
- Apply Aggressive/Full/Lazy separately; include unreachable remoteA
- Lazy current boundary is synthetic tool boundary T at tick 102 with deadline 103; also omit T

**Independent pass predicates**
- Aggressive stops selected actor without silently claiming descendants settled
- Full fences owned rooted scope and borrowB only, while otherB completes
- Lazy closes admission and uses T or reports timeout/escalation; no hidden boundary inferred
- RemoteA remains unknown and reservation held absent authenticated settlement

**Falsifying controls**
- Kill shared server on Full
- Socket close settles remote effect
- Loop relaunch after stop

**Expected evidence**
- Target-set manifest, installed-fence/termination/settlement separate receipts, successful unrelated result

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F17 Consultation cycles and executor release

Status: UNEXECUTED

**Inputs**
- Create H waits A, A waits sole executor E, E waits H
- Suspend A and separately form A-B-A consultation cycle with hop/depth cap 2
- Provide valid consultant reply and permit independent B work

**Independent pass predicates**
- Resource cycle visible; suspension releases E so valid reply/adoption can proceed
- Depth/cycle bounds reject unbounded recursion and do not create another supervisor
- No blocked read pump or hidden waiting executor

**Falsifying controls**
- Wait while retaining only executor
- Auto-spawn manager to resolve cycle

**Expected evidence**
- Wait-for graph, lease release event, finite complete positive path

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F18 Audience privacy and untrusted context

Status: UNEXECUTED

**Inputs**
- A allowed evidenceE, B denied secret-like synthetic fieldS, viewerV sees only A
- Try same room join, context forward to B, route change to new provider and replay old audience revision
- Inject peer text that claims consent and metadata canaries in IDs/digests

**Independent pass predicates**
- No denied payload or metadata canary in projection/context/egress
- Access checked before content retrieval; new provider disclosure independently denied
- Already disclosed history stays recorded as residual; removal does not claim remote erasure

**Falsifying controls**
- Render-first redact-later
- Room roster grants context access

**Expected evidence**
- Per-principal authorized byte manifests, denied retrieval logs and zero synthetic canary leakage

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F19 Coherent fork and reservations

Status: UNEXECUTED

**Inputs**
- Synthetic dirty source has HEAD/index/tracked/untracked/context/goal/route revisions and excluded secret marker
- Capture pre/post manifest with concurrent source edit between reads; repeat stable capture
- Fork before/after pending question, active permit and inherited six-unit reservation
- After stable capture, separately fail derived worktree creation and fail session launch after worktree creation; these are synthetic stage failures, not real filesystem actions

**Independent pass predicates**
- Changed capture refuses/retries without altering original; stable cut binds context and workspace version
- Both versions retained; excluded sensitive bytes not copied
- New child cannot use old permit/input/role lease; reservations split within 20-unit parent ceiling; no double allowance
- Partial worktree/session setup remains an explicit incomplete state; no isolated-running-agent claim, source mutation, blind duplicate launch or assumed cleanup

**Falsifying controls**
- Conversation fork treated as workspace clone
- Copy grants and allowance into child

**Expected evidence**
- Source before/after byte digests, captured manifest, lineage and independent reservation arithmetic
- Distinct capture, workspace-created, session-started and cleanup/retention receipts for partial dispatch failures

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F20 Native and upstream continuation

Status: UNEXECUTED

**Inputs**
- Stub-native actor changes to stub-upstream route at safe admitted checkpoint and back
- Repeat with unsupported steer and opaque lost settlement
- Disable native helper entrypoints in upstream-only profile

**Independent pass predicates**
- Logical goal/evidence/accounting persists with new route/session binding and revalidated rights
- Unsupported control displays typed loss/blocker; ambiguous effect is not replayed
- No hidden native planning/compaction/review/recovery inference

**Falsifying controls**
- Resume copies current grants from provider history
- Hidden helper on route switch

**Expected evidence**
- Continuity manifest, helper tripwires, authority refusals and unchanged uncertain operation identity

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F21 Terminal injection and target spoofing

Status: UNEXECUTED

**Inputs**
- Synthetic peer/tool bytes contain ANSI title/control sequences, fake Head prefix, embedded action-looking payload and bidirectional text
- Render in normal/plain-text and paste into reply composer without sending

**Independent pass predicates**
- Display sanitization preserves attribution and cannot invoke command path
- No control/input/tool/approval generated by source text; stable target labels remain inspectable
- Original untrusted evidence preserved separately under policy

**Falsifying controls**
- Parse terminal output as command
- Trust visual Head prefix

**Expected evidence**
- Raw versus rendered reference hashes, zero action-entrypoint hits and target identity log

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F22 Accounting semantics

Status: UNEXECUTED

**Inputs**
- Known parent meter includes child subtotal, child meter separate; duplicate replay totals
- Missing interrupted final usage and unknown remote receipt
- Attach 20 views and fork with budget split

**Independent pass predicates**
- Sum inclusive/exclusive scopes once; unchanged work totals across views
- Missing values remain null with reason; reservations held until reconciled
- Fork/restart/route change does not renew parent allowance

**Falsifying controls**
- Zero-fill unknown
- Sum parent inclusive and child
- Reset allowance on session restart

**Expected evidence**
- Per-meter scope/unit/provenance ledger and reservation conservation evidence

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F23 All ten controls

Status: UNEXECUTED

**Inputs**
- One valid and one stale/wrong-scope vector for each of streaming questions approvals queued_messages active_steering interruption resume forks compaction commands_plugins
- Repeat under route capability unknown and revoked lease
- Approval for actionX followed by changed actionY

**Independent pass predicates**
- All 20 minimum vectors retain exact command/interaction/action identity and truthful requested/accepted/delivered/adopted/settled distinctions
- Unknown capability never becomes supported; changed action approval refuses
- Compaction and resume preserve authoritative records outside summaries

**Falsifying controls**
- Reuse approval across changed action
- Treat renderable control as supported

**Expected evidence**
- Ten-control coverage grid, per-vector expected/actual typed receipts and capability-loss records

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## RJ-F24 Useful positive completion

Status: UNEXECUTED

**Inputs**
- A requests permitted B review with reservation 6; B answers exact artifact question
- Current authorized A adopts through step 2/plan 9 and canonical writer commits one transition
- Independent synthetic artifact verifier accepts known-good artifact; detach/reattach during exchange

**Independent pass predicates**
- Exactly one useful authorized transition and accepted synthetic artifact, no duplicate effect
- Correct actor/correlation/goal/evidence lineage visible from either view
- All bounds hold; independent unrelated work remains possible

**Falsifying controls**
- Deny every message
- Discard answer to avoid stale risk

**Expected evidence**
- End-to-end synthetic positive witness, independent artifact oracle and role/receipt lineage

Any pass predicate violated, any unexpected authority/effect change, or missing mandatory positive completion is FAIL; missing infrastructure/observation is BLOCKED or UNKNOWN, not PASS.

Use the shared independent oracle, prerequisite gate, stopping conditions and non-proofs; no exception is implied by this case.

## Non proofs

- No live route entitlement or account qualification
- No real external rollback, security boundary, production durability or OS containment
- No measured human comprehension, accessibility, UI conformance, model quality, quota savings or port cost
- Finite schedules are not unbounded proofs; source-documented behavior is not executed behavior

## Physical and human follow on

- Matched hybrid/per-actor/Head-relay comprehension and wrong-target tests with accessibility/plain-text participation
- D028 Windows 11 25H2 build 26200 x64 and 24H2 build 26100 Enterprise; Linux 6.12 LTS primary/6.6 LTS compatibility with cgroup v2 and local NTFS/ext4
- WSL2 ext4 and /mnt/c development-only cases kept separate; no production qualification inferred
- Calibrated offered-load latency, actual process/handle/RSS/CPU/wakeup observations and durable crash/replay tests
- Equal-total-budget larger/fewer-agent workload evaluation including retries compaction and human review

# Unexecuted local qualification handoffs

Every fixture is UNEXECUTED. No runnable product fixture entrypoint was found. These records specify implementation/qualification evidence, not permission to execute. The source-verified supplemental wire command at the end is narrower than product acceptance.

## RK-F01 N-view resource and continuity soak

**Inputs**
- Idle workload and fixed-rate high-output source; 120x40 primary plus 80x24 and 240x80 variants
- Synthetic source event sequence, hashes, burst distribution and finite duration fixed before run
- Run both N passive +1 active and N total-client conventions; separate zero-view case

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Independent event generator manifest and canonical reducer, external invocation hooks, OS resource sampler; same zero-view workload baseline

**Pass predicates**
- canonical_state_digest == expected_digest at every checkpoint
- delta(model_calls, actor_creates, effects, indexer_entries, disabled_plugin_activations) attributable to view operations == 0
- every sampled queue_bytes <= adopted Qbytes and queue_events <= adopted Qevents
- for every N: adopted daemon/client/global memory envelope holds; no sustained post-warm-up growth outside declared cache bound
- each applicable latency quantile meets adopted threshold; zero-view render/input is NOT_APPLICABLE, never 0

**Expected evidence**
- Per-N raw timestamps and independent run IDs, all latencies/timeouts/maxima
- CPU/RSS/wakeups/IPC/process/handle counts; source and canonical digests
- Queue high-water, dropped/coalesced classes, traps, exact thresholds and environment manifest

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Bounded synthetic workload only, not provider cost, all hosts or infinite soak

## RK-F02 Close split and zero-view lifetime

**Inputs**
- One already-admitted synthetic actor emitting numbered records
- Open one view, split, close each, close last, allow no-view interval, reattach same task
- Natural actor completion is a separate expected case

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Independent process birth identity and canonical operation manifest before view operations

**Pass predicates**
- actor_id, process_birth_identity and attempt_id unchanged while source is expected alive
- no extra model/index/plugin/effect dispatch on open/split/reattach
- source continues to drain with 0 clients and retained records match manifest
- close/detach creates no Stop/session-close/EOF signal in adapter trace

**Expected evidence**
- Process creation/exit observer; adapter stdin/PTY endpoint lifecycle
- Canonical before/after roots, view lifecycle records, zero-view output trace

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Does not establish survival of broker or machine loss

## RK-F03 Disconnect reconnect and incarnation recovery

**Inputs**
- Disconnect before/after delivery and ACK; duplicate attach; client crash; sleep/wake
- Broker restart represented as new incarnation with retained canonical facts; no live host fault in research

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Independent operation ID list and snapshot-plus-suffix reducer with fixed expected state

**Pass predicates**
- no new operation/actor/model dispatch caused by reconnect
- each stale daemon/process/lease message refused
- installed state equals expected snapshot+suffix or control disabled with explicit gap/recovery status
- local unsent drafts remain saved-locally and no ambiguous effect blindly retried

**Expected evidence**
- Per-client requested/received/installed/acknowledged positions
- Incarnation/fence records and exact rejection receipts
- State digest and view freshness labels

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Synthetic connection loss does not qualify real power loss or remote takeover

## RK-F04 Input resize and takeover races

**Inputs**
- Two controllers race to acquire same target; 20 passive readers
- Old holder input/resize after transfer; focus/attach; duplicate identical/conflicting command IDs
- Authorized Stop from a client without terminal input lease

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Separate lease-state model and ordered input sink with command IDs

**Pass predicates**
- valid_holder_count(target,instant) <= 1
- accepted INPUT and RESIZE bind authenticated holder plus exact daemon/process/lease generation
- passive INPUT/RESIZE and stale references refused
- identical command retry has one semantic execution; conflicting reuse refused
- focus/attach/split never change holder; separately authorized Stop does not require input lease

**Expected evidence**
- Lease transition journal and independent sink bytes
- Concurrent command schedule and all decisions
- Control-capability versus view/input/step-authority matrix

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Does not establish authentication secrecy or application authority

## RK-F05 Replay gaps snapshots and literal M1B conformance

**Inputs**
- Below-floor HELLO then WELCOME RESET fresh CREDIT EVENT
- Interpose ACK/CREDIT/SNAPSHOT after detected gap; missing/corrupt/unauthorized snapshot
- ACK ahead/backwards; ACK without renewed credit; real retention gap versus deferred local event

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Literal expected M1B outcomes plus independent materialized snapshot digest/state; do not reuse implementation fold

**Pass predicates**
- gap followed by any non-RESET same-stream message => refused replay-gap-continuation
- RESET clears credits; EVENT before fresh CREDIT => refusal
- ACK releases only entries at/below acknowledged cursor and grants no credit
- recovered UI only after verified snapshot and suffix state match; accepted-reset alone insufficient
- local deferral cannot claim retention loss; GAP is not added to closed message union

**Expected evidence**
- Input traces and expected/actual decisions
- Snapshot identity/hash/authorization and source retention evidence
- Installed state digest and UI gap/freshness capture

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Wire acceptance does not authenticate snapshot/store facts or physical delivery

## RK-F06 Framing cursor bounds and credit arithmetic

**Inputs**
- Event and UTF-8-byte cursors; multibyte payload; Count near 2147483647
- Duplicate keys, invalid UTF-8, BOM, floats, depth65, object262145 bytes, excessive decoded payload
- Slow partial frame, oversized length/line, repeated maximum CREDIT

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Independent strict parser/schema checker and arbitrary-precision expected cursor/credit calculations

**Pass predicates**
- no wrap or silent unit/stream/incarnation change
- event increment exactly1; byte increment equals decoded payload bytes
- frozen malformed object cases rejected before semantic effects
- framing/partial buffers bounded at every byte; oversized request cannot block control
- production cumulative outstanding grant never exceeds adopted allocation; mapping differences from existing oracle explicitly recorded

**Expected evidence**
- Malformed corpus IDs and bounded allocation samples
- All parser refusals, input byte counts and cursor arithmetic
- Version-negotiation/rollover mapping record

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Does not select encoding or prove freedom from parser vulnerabilities

## RK-F07 Stalled client and end-to-end Stop reserve

**Inputs**
- One client grants no further credit/ACK and stops reading
- Saturate render/output/history queues, incomplete frame buffer, and bounded writer pressure
- Offer authorized Stop while canonical source continues; separately test storage unavailable

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Independent monotonic timestamp observer, source ledger, actual admission-fence/effect dispatch observer

**Pass predicates**
- slow client cannot hold canonical append or Stop scheduling path
- adopted offer->accepted and accepted->fence bounds hold under declared available-storage profile
- zero post-fence selected-scope admissions; unrelated task continues
- zero canonical/command/lease/exit/termination event loss
- storage failure is explicitly persistence-unavailable/unresolved, not a fabricated durable acceptance

**Expected evidence**
- Each pipeline stage timestamp and queue high-water
- Fence receipts, dispatched effect IDs, event conservation ledger
- Storage-state and excluded/stalled-client latency flags

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: No bounded liveness claim under failed kernel/disk or settled remote effects

## RK-F08 Huge output scroll anchors and retention

**Inputs**
- At least100x visible viewport; repeated progress deltas and immutable unique records
- Reader scrolls away/selects/searches while output continues; retention boundary crossed
- Compare complete retained history and exact byte-transcript mode separately

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Source corpus digest plus expected anchor event/grapheme coordinates

**Pass predicates**
- reading anchor/selection unchanged by append, reflow preserves semantic anchor
- follow resumes only by user action with correct unread event count
- retained history export exactly matches declared source recording policy
- presentation coalescing does not remove canonical facts
- cache/disk envelope respected and actual unavailable retention range marked

**Expected evidence**
- Export digest, retained range manifest, anchors before/after
- Coalescing range records and memory/queue samples

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Cannot prove infinite or unconfigured raw-byte retention

## RK-F09 Diff repaint resize and partial writes

**Inputs**
- 1%,50%,100% dirty screens; full-width emojis/combining marks; sparse streaming
- Synthetic100 resizes/s, final valid holder geometry, passive resize attempts
- Short writes/failures; maximal admitted1..1000 geometry; compare diff and bounded repaint

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Separately implemented reference framebuffer and captured terminal output replay under exact width profile

**Pass predicates**
- every committed frame equals reference for its state+geometry generation
- never commit unsent/stale partial-frame baseline
- no wide-cell residue or torn attributes at final frame
- final holder resize applied; passive geometry cannot change PTY
- all applicable adopted input/frame/memory thresholds met; full-log repaint absent

**Expected evidence**
- Golden cell grids, output-byte traces and geometry generations
- Dirty ratios, bytes, CPU, tail distributions, screenshots/manual tearing notes

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Emulator agreement is not proof of real terminal perception or renderer selection

## RK-F10 Unicode IME paste and untrusted controls

**Inputs**
- Pinned grapheme corpus including combining marks,CJK,ambiguous width,ZWJ emoji,flags,variation selectors
- Split each UTF-8 sequence at each byte boundary; invalid sequences; backspace/select/wrap
- Bracketed multiline paste with control strings; OSC52/title/hyperlink/device controls; approval-shaped text
- Later native IME composition/candidate selection/cancel with streaming+resize

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Pinned Unicode expected segmentation and exact committed input corpus; independent command/clipboard/approval traps; human IME observer

**Pass predicates**
- committed text and editing outcomes exactly match declared profile
- paste never submits without explicit action
- composition/caret preserved where supported; unavailable preedit marked unsupported/unknown
- untrusted output creates zero UI command/clipboard/approval/authority changes
- buffers and long grapheme handling bounded

**Expected evidence**
- Corpus IDs, byte traces, clipboard/command traps
- Terminal/font/IME build and locale; manual composition recordings without personal data

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Does not prove all-font width parity, credential isolation or general injection resistance

## RK-F11 Contained actor lifetime and three Stop scopes

**Inputs**
- Provider-free synthetic actor tree with children,monitor,relauncher and unrelated sibling
- Full/Aggressive/Lazy at named operation boundary; detached views
- Native approved Job/cgroup test with deliberate escape/containment failure; unreachable-node fixture

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Independent native process membership/birth observer plus rooted ownership manifest and effect ledger

**Pass predicates**
- detach alone leaves expected actor tree alive
- Full fences relauncher and accounts for each owned process as settled or unresolved; unrelated work not killed
- Aggressive target/descendant distinction preserved
- Lazy closes admission and stops only at named observable boundary or explicit configured timeout/escalation
- process exit,PTY EOF,ClosePseudoConsole return never imply external rollback

**Expected evidence**
- Native OS profile and containment receipts; escape/remaining-process list
- Admission and restart-fence trace; local versus remote settlement states

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Synthetic containment result does not qualify hostile credentials, outside effects or all process launchers

## RK-F12 Shared backend facts and no extra executive

**Inputs**
- Same commands via deterministic headless client and TUI; future GUI contract simulator
- Delayed/out-of-order/stale accepted/delivered/adopted/effect receipts
- Multiple actors in one view,one actor in many,split room with bounded step coordinator

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Independent canonical reducer and authority/role/step-lease graph; literal receipt truth table

**Pass predicates**
- identical valid commands yield identical canonical transitions across surfaces
- saved-locally not labeled accepted; delivered not adopted; generated not reviewed/accepted/published
- gap/offline/unknown counts remain explicit
- view operations add no Head/ARM/worker identity,step permit,budget grant or actor
- contexts remain separately keyed; addressed-message authority distinct from raw terminal lease

**Expected evidence**
- Cross-surface trace diff and authority graph digests
- Truth-table results and stale-action refusals
- Unresolved effect and usage-null projections

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Does not prove live source assertions, model compliance or actual GUI accessibility

## RK-F13 Keyboard accessibility and semantic announcements

**Inputs**
- All workflows keyboard only; narrow/high-contrast/plain-text/reduced-motion profiles
- Focus inspector open/close,question expiry,streaming,IME,disconnect
- Separately admitted actual Windows and Linux terminal/screen-reader combinations

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: Independent task script and human accessibility review with named action/role/focus expectations

**Pass predicates**
- all controls reachable by named keyboard path; current focus visible and not obscured
- focus restoration correct; streaming never steals focus
- Stop mode/target persistent and reachable without timed double press
- Escape never globally stops/deletes; draft recoverable
- semantic important-state announcements present,deduplicated,rate-limited; no token speech flood or urgent-state loss

**Expected evidence**
- Per-action reachability/focus log and assistive-technology profile
- Announcement event/history transcript; user error/comprehension measures
- Untested combinations listed NOT_RUN

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: No general WCAG or all-assistive-technology conformance from a finite matrix

## RK-F14 Host encoding and port-cost comparison

**Inputs**
- Eligible in-process/daemon/external-host candidates with same semantics and workload
- JSON framing versus explicitly versioned binary mapping; semantic and cell snapshot variants
- Preregister implementation/update/support effort accounting and licensing/dependency review

**Prerequisites**
- Separately admitted local implementation session and pinned candidate commit
- Exact D028 OS build, terminal build, font/Unicode/IME profile and permissions recorded
- Synthetic-only adapter; outbound provider/auth/network denied and invocation traps independently observed
- Independent verifier and frozen expected outputs; proposed numeric/resource thresholds adopted or replaced before run

**Independent oracle**: All hard-gate results independently accepted first; reversible encoding mapping and matched workload hashes

**Pass predicates**
- no candidate compared as viable if any authority/lifetime/accessibility hard gate fails
- encoding preserves exact null/missing/integer/schema/digest domains and event order
- reported cost includes integration,port parity,tests,upgrades,support; unknown cost not0
- no component selected from an incomplete or unmeasured cell

**Expected evidence**
- Candidate/build/source/license manifests; total-system metrics
- Engineering effort ledger and unsupported cases
- Versioned wire crosswalk with literal positive/negative cases

**Stopping conditions**
- Stop immediately on a provider/auth call attempt, credential access, unrelated process impact or authority-floor failure
- Stop on declared memory/disk/process/elapsed-time envelope; retain failure trace and mark incomplete cells NOT_RUN
- Never infer pass from missing observations or an unresponsive client

**Failure rule**: Any false pass predicate is FAIL. Missing prerequisite/evidence is BLOCKED or NOT_RUN, not PASS.

**Does not prove**: Does not prove cheap porting, superiority or future vendor compatibility

## RK-H01 Existing supplemental wire entrypoint

Verified source command: `python3 -B experiments/v3/external-20260914/broker_wire_tests.py`

Source basis: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`

**Prerequisites**
- Separately authorized local session and exact snapshot
- Python3 and existing reference_oracle/fixture files present; no installation implied
- Independent verifier reviews literal expected values against frozen M1B before execution

**Inputs**
- Frozen F-M1B-020 fixture baseline and hand-built trace mutations in inspected test source

**Independent Oracle**
Literal expected trace outcomes independently reviewed against the profile; existing test invokes the reference oracle and therefore is not independent of that oracle implementation

**Expected Evidence**
- Full stdout/stderr,exit status,candidate hash,test-source hash and verifier notes
- Expected program success marker V3_BROKER_WIRE_PASS only if every included case passes

**Stopping Conditions**
- Any unexpected provider/network/process effect stops the run
- Any fixture/import mismatch or exception blocks acceptance

**Non Proof**
No snapshot materialization, physical IPC, N-client exclusion, product Stop, host recovery or route qualification; this entrypoint alone cannot pass RK-F01..F14.

# R-L unexecuted local handoffs

All 15 fixtures are UNEXECUTED. No unified implementation entrypoint is verified. No command in this packet is authority to run target code.

## Common prerequisites

- Pinned candidate source/build/config/protocol profile and independent oracle
- Synthetic fixtures only; no real providers, accounts, credentials, personal data or operational hosts
- External egress/provider entrypoints disabled by admitted test setup; complete call/activation/credential tripwires
- Frozen finite time, memory, disk, frame, queue and teardown limits
- Canonical writer/effect sink/terminal sink observations independent of candidate status; observer loss detectable
- Positive controls and deliberate negative mutants; verifier independent of candidate author

## Stop conditions

- Unexpected external provider/network/account/credential/production-path access: abort and preserve evidence
- Any authority widening, unrelated process impact or inadequate teardown: abort
- Observer/oracle failure or failed positive control: halt campaign
- Hard time/resource/queue cap crossed: fail boundedness and stop safely; never count timeout as pass
- Finish only at frozen finite trace or observation-window end with synthetic teardown; preserve every failure/censored row

## F01 Cross-surface query and command parity

Additional namespace cases: Same domain/canonical ID with changed principal/grant or payload; same client-local ID under two principals with explicit injective canonical mapping; cross-domain and revoked-reader receipt lookup; allowed historical receipt after effect revocation. Required result: one canonical (authority domain, command ID) key with immutable principal/grant binding; mapped client IDs stay distinct, unauthorized readers receive no existence disclosure, and old receipts never redispatch. Preserve the identity-map and current-reader authorization evidence.

Inputs:
- One synthetic goal with two tasks, two principals/audiences and pinned cut 40
- Queue, steer, status, Stop, config preview and interaction answer catalogs
- CLI, TUI, GUI-stub and editor codec inputs with deliberately conflicting focus/selected target
- Same-ID identical retry and same-ID changed-argument retry

Independent oracle:
- Canonical bytes from independently authored golden target/argument/query records
- Separate synthetic effect counter; not candidate self-report

Pass: At equal cut/audience/version, query canonical bytes match; equivalent command semantic bytes and errors match; same-ID retry causes exactly one effect; changed bytes conflict.

Fail: A hidden default, focus retargeting, unknown-to-zero coercion, second effect or second admission path fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Independently authored codecs against same corpus.

Non-proof: Does not prove visual usability, real GUI correctness or route semantics.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F02 Disabled contribution inertness

Inputs:
- 0/10/100 inert synthetic manifests and a malicious disabled implementation marker
- Layouts that reference absent/disabled views; catalog lookup, attach/split/focus/idle
- Explicitly enabled positive control in separate authorized phase

Independent oracle:
- Independent import/process/thread/watcher/timer/network/index/model/credential/subscription/registration/reservation probes
- Frozen metadata read budget and event inventory

Pass: Disabled fields are all zero after bounded metadata inventory; missing view is core placeholder; enabled positive control proves probes fire.

Fail: Any executable activation or omitted probe coverage fails or makes unknown; metadata cost is reported rather than hidden.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Precompiled inert registry.

Non-proof: Does not prove host plugin sandbox or malicious supply-chain isolation.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F03 Configuration race and rollback

Inputs:
- R7 config; concurrent CLI and editor edits with expected R7; two orderings
- R8 revokes an effect; unrelated R9 preference coalesces notification
- Rollback request to old config and lost apply acknowledgment

Independent oracle:
- Independent compare-and-swap expected sequence and finite grant-set oracle
- Effect sink records whether revoked work dispatched

Pass: At most one same-base edit succeeds; loser conflict has no mutation; receipt lookup deduplicates; rollback is new revision and cannot restore revoked authority without current grant.

Fail: Last-write-wins, stale dispatch or decremented authority fence fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Serialized single-editor lease.

Non-proof: Does not define unresolved privacy/publication lattice or undo external effects.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F04 M1B resync and snapshot fact binding

Inputs:
- Exact frozen m1b-broker/1 traces for event and utf8-byte units
- Genuine retained prefix loss with requested<floor<=snapshot; verified synthetic snapshot
- Every non-RESET message after gap; RESET then new CREDIT; byte/event credit edges
- Forged floor/missing snapshot, local deferred frame without retention loss, Count maximum

Independent oracle:
- Frozen M1B expected refusal vectors plus independent source-retention and snapshot-byte ledger
- Separate cursor-unit arithmetic with multibyte payload

Pass: True gap immediately RESETs with no forbidden continuation; fresh credit required; exact refusal classes; snapshot installs atomically; forged facts rejected by fact layer; no cursor wrap.

Fail: Gap invention, invented snapshot, same-stream bypass, ack-ahead or loss disguised as frame coalescing fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Direct pull reconstruction at canonical cut.

Non-proof: Does not prove physical crash durability, infinite cursor lifetime or new production rollover protocol.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F05 OSC boundary and reply safety

Inputs:
- Allowed title/notify forms; OSC52, unknown OSC9/777 forms and command links
- Every split point in introducer/payload/terminator, C0/C1 injection, malformed UTF-8, overlong/unterminated input
- Notification reply colliding with apparent approval/input data; synthetic secret marker

Independent oracle:
- Independent fake terminal state/clipboard/command sink and escape grammar oracle
- Authorized display-body goldens

Pass: Forbidden sequence has no forbidden effect; parser recovers; allowed data is correctly encoded/scoped; reply cannot become input/approval; no marker leakage.

Fail: Any clipboard/command side effect, corrupted parser ground state or disclosure fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Suppress all OSC; separate native notifications.

Non-proof: Does not qualify every terminal or guarantee against screen/timing side channels.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F06 PERF-010 passive-view soak

Inputs:
- N=0,1,5,10,20 times idle/high-output; fixed offered event distribution/rate/burst
- Slow/no-read/disconnected view, resize storm and snapshot recovery variants
- Frozen startup/idle/first-use/steady/recovery caps and preregistered tail budgets

Independent oracle:
- Independent canonical event count/hash and process/actor/effect sink
- External offered-load timestamps and resource samplers independent of renderer

Pass: Every required cell meets frozen resource/tail bounds, preserves mandatory events, adds zero model/index/activation, preserves actor/process lifetime and drains backlog; N0 frame metric is not-applicable.

Fail: Any durable loss, hidden work, misrouted input, cap violation, relaunch or missing required metric rejects or blocks pass.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Sequential human workflow measurement with same workload.

Non-proof: Does not measure subscription savings or certify all hardware/terminal profiles.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F07 Composed control reserve

Inputs:
- Separate and combined saturation at ingress, incomplete frame, window, read pump, callback scheduler, writer, projection and slow output sink
- Owner Stop on selected scope with one offline synthetic remote and one unresolved effect
- Disk reserve exhaustion negative control under disposable test harness only

Independent oracle:
- Independent offered/admitted/fence-installed trace and effect dispatch log
- Frozen per-stage and end-to-end control deadline; offline effect oracle

Pass: Authorized Stop fences within bound while unrelated authorized work remains possible; required evidence retained; offline/unsettled state remains unknown; failed persistence blocks new effects and reports inability honestly.

Fail: UI-only ACK treated as fence, indefinite head-of-line delay, new dispatch after fence, or fake remote settlement fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Shared transport with proven reserved logical slots versus separate channel.

Non-proof: Does not guarantee progress through arbitrary OS/storage failure or remote compliance.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F08 Durable interaction race

Inputs:
- Interaction i1 generation1; two clients answer simultaneously; reconnect
- Replace with generation2 with same visible wording; replay old answer
- Approval action changes recipient/data/args; expire respondent grant

Independent oracle:
- Independent waiter-consumption log keyed by interaction/generation/digest
- Frozen answer/expiry schedule and exact action goldens

Pass: One current answer consumes one waiter; duplicate is idempotent; stale/expired/changed-action response refused; no privilege change from dialog origin.

Fail: Duplicate adoption, generation retarget or reused broader approval fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Reconstruct interaction state directly from canonical events.

Non-proof: Does not prove upstream callback lifetime or durable provider approval retention.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F09 Input and resize ownership

Inputs:
- Two observers; one current input and resize owner; wrong and stale leases/epochs
- Rapid focus/resize and reconnect; valid current-owner input
- Owner Stop without input lease but with proper authority

Independent oracle:
- Independent typed lease/epoch table and byte-target sink
- Frozen expected geometry revisions and Stop fence

Pass: Only matching input/resize lease and epochs mutate target; focus never steals; valid control completes; authorized Stop succeeds via its separate path.

Fail: Raw input from observer, conflated writer/input lease, stale resize overwrite or Stop blocked by view ownership fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Explicit controller handoff versus fixed designated input client.

Non-proof: Does not prove OS input capture safety or effect authorization beyond fixture.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F10 Configuration conformance corpus

Inputs:
- All nine corpus classes from report, all five edition profiles, pairwise/three-way plus targeted bounds
- Native Windows accepted-floor profiles and Linux primary/compatibility; separate WSL dev profiles
- Golden normalized/no-normalization distinctions and finite grant-subset examples

Independent oracle:
- Independent canonical byte/digest/provenance/error goldens
- Independent reference subset evaluator, no candidate parser reused

Pass: All defined cases match exact bytes/errors/receipts across applicable profiles; deny-all fails positives; undefined privacy/publication relation stays blocked-definition.

Fail: Parser-specific duplicate/type coercion, stale mutation, unauthorized widening or fabricated lattice success fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Two independent resolvers with targeted goldens.

Non-proof: Does not select syntax or exhaust all combinations; migration usability remains unmeasured.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F11 Capability-driven controls

Inputs:
- Route supports queue but not steer; other route steer unknown
- Enabled plugin replaced with new artifact/schema; view retains old catalog
- Grant revocation between affordance display and submit

Independent oracle:
- Independent capability/grant/revision table at each canonical sequence
- Effect sink distinguishes queue from steer

Pass: Current admission rechecks all dimensions; exact loss/reason shown; stale command rejected; no unsupported steer silently queued; rendering feature alone confers nothing.

Fail: Visibility-only enforcement, unknown-as-supported or semantic fallback fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Fixed operation surface with typed unavailable responses.

Non-proof: Does not qualify upstream documented capability or build stability.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F12 Detach versus adapter lifetime

Inputs:
- Synthetic adapter with stdin-close terminates-host behavior
- Close all CLI/TUI/GUI-stub observers, reattach, then explicit Stop
- Pending question and accepted command survive detached interval

Independent oracle:
- Independent launch/exit/actor/model counters and adapter connection owner log
- Canonical interaction/receipt IDs before and after

Pass: Detach closes subscriptions only, not owned adapter control connection; no launch/model/actor multiplication on reconnect; explicit Stop remains separate.

Fail: Per-view adapter ownership closes work or reconnect relaunches it without command fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Runtime-owned proxy connection versus shared durable server adapter.

Non-proof: Does not prove any actual harness can restore after host loss.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F13 Audience-bound projections

Inputs:
- Two audiences with disjoint private synthetic records and shared public fact
- Revocation while one client is slow/offline with snapshot cached
- Attempt reuse of continuation/snapshot handle in other scope

Independent oracle:
- Independent allowed-disclosure sets and byte sink
- Audience/filter/source-cut identity ledger

Pass: Queries/snapshots/continuations are bound to current audience; no new denied bytes disclose after revocation; stale cache disposition truthful; prior disclosure not claimed erased.

Fail: Cross-audience handle reuse, identifier/sequence leak beyond declared policy or new revoked disclosure fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Direct authorized reads without persistent client cache.

Non-proof: Does not prove deletion from hostile client memory or eliminate timing side channels.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F14 Crash and honest effect state

Inputs:
- Crash points before acceptance, after acceptance, after dispatch, after synthetic effect before reply
- Resume with new view/connection and changed writer/config generation
- Missing final usage observation

Independent oracle:
- Independent synthetic effect count and canonical receipt history
- Frozen state table for each cut; unknown usage goldens

Pass: Stable operation identity, correct receipt/ambiguity per cut, no duplicate effect, no hidden helper inference; usage remains unknown when unavailable.

Fail: New-ID forced retry, vanished operation treated as zero or response absence treated as rollback fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Durable receiver records versus query-only reconciliation.

Non-proof: Does not establish external remote idempotency, power-loss durability or receipt retention bounds.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

## F15 Accessibility semantic screening

Inputs:
- Keyboard-only navigation/control corpus for five destinations and command palette
- Status/error/focus/unknown state mappings for CLI/TUI/GUI-stub
- Theme with color ambiguity and missing semantic labels

Independent oracle:
- Independent requirement-to-action/status/focus map, not visual snapshot alone

Pass: All required controls have explicit semantic names/status and reachable declared keyboard paths; missing labels/focus/status alternatives fail screening.

Fail: Critical action accessible only through unlabelled color or mouse-only undisclosed path fails.

Expected evidence: fixture and oracle hashes; offered/send/accepted/appended/applied/observed monotonic timestamps with clock domains; canonical records and stable command/operation/interaction IDs; bounded raw input/output traces and typed refusals; authority/process/daemon/config/route/audience generations; model/index/activation/credential/egress tripwire coverage and counters; queue/resource high-water and exceeded-limit records; teardown receipts and missing-observation reasons.

Competing option: Surface-specific accessible forms over same typed command schema.

Non-proof: Does not establish WCAG or actual screen-reader/terminal accessibility; real human/assistive-tech work remains required.

Stop: common conditions apply; conclude only after the frozen trace/window and safe synthetic teardown.

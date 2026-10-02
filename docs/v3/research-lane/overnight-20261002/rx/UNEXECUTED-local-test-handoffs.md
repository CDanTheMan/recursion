# R-X UNEXECUTED local test handoffs

Every fixture below is UNEXECUTED. These are test specifications, not runnable product commands. No fabric entrypoint was verified. A separately authorized engineering session must supply a pinned implementation, independent runner/oracle and approved disposable environment before execution. No fixture requires a provider/model/account or real credential.

## Common execution contract

### Prerequisites
- Pin candidate commit/build, exact configuration, protocol/schema, OS profile, permission and fault model
- Adopt finite resource/time/freshness/replay thresholds before running; keep unknown values null
- Use independent oracle code/evidence not authored as a wrapper around candidate success status
- Record every positive and negative case; refusing everything is failure
- Keep control/writer and receiver observations separate; incomplete instrumentation is inconclusive
- No install, network setup, destructive reset, security setting, live credential or account action follows from this handoff
- Any zero-activity claim needs a per-probe enabled synthetic sensitivity control using the same observer configuration, reset procedure and defined baseline, with retained expected/detected receipts. Blind/failed/uncalibrated probes are UNKNOWN; ordinary task acceptance is not detector calibration. Controls are inert/local and never call a provider or external network.

### Evidence
- fixture and candidate identities/hashes
- input manifest and fault schedule
- source/receiver/canonical observation records with separate cursors
- oracle identity and verdict per exact predicate
- unknowns/refusals and observation coverage
- independent reviewer acceptance remains separate from author result

### Stopping Conditions
- Stop immediately on unsafe mutation/disclosure, unexpected live dependency, privilege or resource ceiling breach
- Stop at the predeclared finite case corpus/deadline; timeout is failure or inconclusive according to named predicate, never success
- Preserve synthetic evidence; do not retry a hazardous action under a new logical effect ID

### Nonproofs
- No model/provider/route qualification
- No cryptographic or native OS conformance from typed-message mocks
- No unbounded proof, exactly-once arbitrary external effects, instant remote Stop or unconditional availability

## RX-F01 — Enrollment and revocation

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Synthetic domain D, node N and public-key identifiers K1/K2
- Owner approval A binds D/N/K1, role executor and expiry
- Single-use bootstrap proof B and one private artifact handle

### Prerequisites
- Canonical enrollment command schema and independent policy evaluator
- No actual key provisioning or account access

### Procedure
1. Enroll exact approved binding; request artifact/task/effect with no task grant
2. Replay B; change key/role/domain under A; then issue a valid exact task grant
3. Revoke generation while a session remains open; attempt renew/read/rejoin using old generation

### Independent oracle
Independent canonical membership/approval ledger and artifact/effect access counters

### Exact pass predicate
Exactly one membership creation for B; altered/replayed binding rejected; enrolled-without-grant access count is zero; only positive exact grant succeeds; old revoked generation cannot renew or rejoin

### Exact failure predicate
Any membership-only task/effect/disclosure, changed enrollment acceptance or stale-generation access

### Expected evidence
- Approval binding and before/after canonical revision
- Typed refusals, session revocation receipts, byte/effect counters

### Stopping conditions
Finish all explicit variants or stop at first unsafe state transition; observer loss makes affected result inconclusive

### Passing does not prove
Correct physical identity, secret-key protection, real cryptography or entitlement

## RX-F02 — Mutual authentication and downgrade refusal

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Synthetic peer credential/status fixtures, valid and revoked trust revisions
- Version/capability offers with required fence and Stop features
- Fresh and replayed transcript IDs; below-floor and stripped offers

### Prerequisites
- Selected semantic handshake schema with declared floor and exact required capabilities
- Later crypto testing requires a separately authorized implementation and disposable local endpoints

### Procedure
1. Run positive mutual-authentication transcript and exact-version competitor
2. Remove each authentication direction; mismatch audience/domain; revoke/expire trust; replay old transcript
3. Strip version/capability; offer replayable early control; report proxy-terminated identity as end-to-end

### Independent oracle
Independent transcript acceptance matrix; content release and dispatch counters outside the candidate

### Exact pass predicate
Only both-current-peer, correct-audience, floor-compliant transcript succeeds; every negative releases zero protected content and starts zero work; no automatic security downgrade

### Exact failure predicate
Any unilateral or stale authentication accepted, stripped feature silently tolerated or mutating early data admitted

### Expected evidence
- Offered/selected versions and capability differences
- Transcript-binding checks and refusal codes
- No-content/no-dispatch observations

### Stopping conditions
Stop on first forbidden release; otherwise exhaust finite transcript matrix; lack of crypto implementation is unknown rather than simulated crypto PASS

### Passing does not prove
Forward secrecy, cryptographic library security, native transport compatibility or production latency

## RX-F03 — Clone and incarnation recovery

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- N incarnation 4 current; old disk snapshot incarnation 3
- N2 identity and message addressed to N2
- Two simulated endpoints with the same software-key identity

### Prerequisites
- Canonical incarnation issuer and session-binding contract
- Explicit profile statement about copied-key indistinguishability

### Procedure
1. Present old snapshot/incarnation and replay N2 envelope as N
2. Request a new incarnation from non-authoritative node-local counter
3. Present observable conflicting live incarnations; separately present indistinguishable copied-key case

### Independent oracle
Independent current-incarnation registry and audience-check oracle

### Exact pass predicate
Old/cross-node/self-issued incarnation refuses; observable conflict quarantines dependent admission; indistinguishable copied-key case is labeled unknown and cannot receive hardware-unique qualification

### Exact failure predicate
Old snapshot gets a current permit, local counter mints authority, or copied-key case reported physically unique

### Expected evidence
- Incarnation issuance provenance
- Conflict/quarantine receipts
- Explicit unknown assurance field

### Stopping conditions
Complete finite identity cases; stop if metadata exposes real host identity or observer cannot distinguish sessions

### Passing does not prove
Actual hardware identity, non-exportable key properties or administrator resistance

## RX-F04 — Control-first and integrity-bounded hydration

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Synthetic control capsule with exact goal/Stop/effect refs
- Two artifact entries, one valid and one forbidden
- Chunks with missing, corrupted, oversize and re-ordered content; traversal/redirect locators
- ExposureIntent referencing expected CopyRecord, full lineage and existing reservation, with no copy-presence assertion
- Crash cuts before/after intent registration, quarantine verification, protected publication and independent publication observation; deletion-inventory-cut race

### Prerequisites
- Q ArtifactRef/ContentEnvelope base and scoped resolver
- Independent fixture digest/length and rights catalog
- Durable canonical intent registration and independent publication/copy observation; Q CopyRecord status vocabulary unchanged

### Procedure
1. Offer protected metadata/content before exact recipient authorization or registered exposure intent; refuse release Include a private manifest and remote-quarantine chunk as actual recipient disclosures; authorized local private staging is the separate no-disclosure positive case.
2. Authorize exact scope and durably register exposure intent, expected CopyRecord reference, lineage and existing reservation without marking a copy present; validate minimum control manifest before artifact hydration
3. Transfer only approved chunks into quarantine; corrupt body/reference, omit chunk, widen range/embedded object, redirect destination and substitute traversal path
4. Verify integrity and lineage; inject revocation/deletion-inventory cut before publication and require fresh rights/fence/cut checks at the protected publication gate
5. Crash at each registration/verification/publication/observation seam; restart and refuse publication without recovered durable intent; preserve operation/transfer identity and reservation
6. For publication_unknown, reconcile independently without guessing absence or blindly redispatching; positive valid publication receives independent observation before settlement

### Independent oracle
Independent expected bytes, durable canonical intent/lineage/reservation ledger, deletion-inventory-cut evaluator and externally observed publication/copy log; candidate status is not truth Sender egress is independently observed separately from remote quarantine arrival and task-visible publication.

### Exact pass predicate
Authorization and durable separate exposure intent precede protected transfer; task-visible bytes require validated minimum control/artifact, recovered durable intent and fresh rights/fence/inventory-cut checks. Expected CopyRecord is not labeled present until observed; Q statuses unchanged. Every crash preserves one operation/transfer identity and reservation; publication_unknown reconciles without assumed absence or blind retry. Valid positive publication is independently observed; malformed/widened/revoked cases refuse. Remote quarantine counts as node disclosure: before sender release of every relevant private manifest metadata/chunk, the scoped durable exposure intent and potential-copy inventory obligation, lineage and reservation already exist. Intent asserts neither present nor delivered; later verified task publication has a separate current-rights/fence gate.

### Exact failure predicate
Unregistered transfer/publication, invented planned/staged CopyRecord status, intent treated as observed/present copy, restart without intent, stale-cut publication, premature settlement, guessed absent publication or new blind transfer identity

### Expected evidence
- Authorization and durable exposure-intent registration receipt before transfer/publication Include independent sender-release ordering, potential-copy inventory obligation and distinct remote-arrival versus task-publication observations.
- Expected CopyRecord reference, lineage registration and unchanged reservation binding; no presence claim from intent
- Manifest/chunk/whole-object verification and protected-gate current rights/fence/cut receipts
- Independent publication/copy observations or explicit publication_unknown
- Per-crash recovery trace with same operation/transfer identity and reservation; reconciliation/refusal decisions

### Stopping conditions
Stop immediately on forbidden exposure or allocation ceiling breach; missing source blocks rather than fabricate bytes

### Passing does not prove
Authentic origin from digest alone, universal parser safety or semantic fidelity

## RX-F05 — Placement and egress refusal

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Three synthetic nodes: approved, forbidden region/operator and unknown residency
- Task with private metadata, allowed purpose and exact source revision
- Stale descriptor, false self-asserted capability and cost null cases

### Prerequisites
- Hard eligibility policy with evidence freshness and authoritative descriptor sources
- Independent outbound metadata/content sink

### Procedure
1. Evaluate all candidates under identical policy
2. Attempt forbidden and unknown destination before manifest disclosure
3. Change policy after placement but before transfer/dispatch; attempt stale receipt use
4. Admit approved destination with all facts/reservations and inspect explanation

### Independent oracle
Independent policy evaluator and per-recipient observed byte/metadata counters

### Exact pass predicate
Forbidden/unknown hard-bound destinations receive zero protected metadata/content; stale placement cannot dispatch; allowed placement has exact evidence/refusal/tradeoff receipt

### Exact failure predicate
Urgency/score/cheapness overrides a hard floor, unknown becomes verified or prefilter metadata leaks

### Expected evidence
- PlacementReceipt and fact versions
- Zero-release observations for negatives
- Allowed positive output and capacity reservation

### Stopping conditions
Stop on first unauthorized byte or unbounded policy lookup; finite candidates then conclude

### Passing does not prove
Truth of an asserted physical region, optimal placement or cost advantage

## RX-F06 — Exclusive admitted lease and replacement hold

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- One task/step, holders A/B and work epochs 7/8
- Renewal conflict, expiry, sleep/wake and unknown old-process variants
- Receiver barrier complete and incomplete variants

### Prerequisites
- Canonical compare-and-admit lease semantics
- Profile flag requiring physical non-overlap where applicable

### Procedure
1. Race grant/renew/replace against expected work revision
2. Expire/suspend A without a quiescence observation
3. Try B while sink install barrier/effect reconciliation is incomplete
4. Allow B only after applicable fencing/effect/quiescence predicates become evidenced

### Independent oracle
Independent state-machine oracle counts current admitted holders and unsafe conflicting dispatches

### Exact pass predicate
Current admitted holder count never exceeds one; renewal is not heartbeat side effect; replacement blocks on missing required barrier or physical quiescence; positive safe replacement succeeds

### Exact failure predicate
Two current grants, renewed expired grant or B dispatches despite unresolved required non-overlap

### Expected evidence
- Ordered grant/close/install/start receipts
- Process/effect unknown vector
- Independent holder-count trace

### Stopping conditions
Stop at duplicate grant or unsafe replacement; no wait timeout is interpreted as dead process

### Passing does not prove
One physically running process on an unreachable/malicious host or real-clock accuracy

## RX-F07 — Receiver fence installation race

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Receiver R floor 7 and delayed A request with work epoch 7
- Authorized floor-8 installation and forged high-number installation
- Crash cuts before persistence, after persistence, before/after effect gate and ACK

### Prerequisites
- Durable receiver floor with independently observable irreversible gate
- Defined source of current writer/work/Stop authority

### Procedure
1. Delay A before gate; commit canonical revocation; keep installation pending and inspect status
2. Persist floor 8 and acknowledge installation; attempt stale A and valid B
3. Crash/restart at each cut; retry both request and install with stable IDs
4. Try lower/fabricated higher floor and stale config/pause vector

### Independent oracle
Independent sink mutation ledger plus separately tracked durable floor and linearization order

### Exact pass predicate
After floor-8 gate installation no epoch-7 mutation occurs, including restart; pre-install exposure remains pending/unknown; invalid issuer/high token refuses; no check-to-effect race

### Exact failure predicate
Stale mutation after install, floor regression, fabricated high token accepted or pending remote revocation reported complete

### Expected evidence
- Gate order trace
- Persisted floor before/after restart
- Sink mutation and installation receipts

### Stopping conditions
Stop on first stale mutation or false quiescence; missing receiver instrumentation is inconclusive

### Passing does not prove
Instant offline Stop, rollback, malicious-sink cooperation or general distributed linearizability

## RX-F08 — Lost acknowledgements and crash boundaries

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- One admitted effect with stable operation/body and one retry owner
- Crashes before intent, after admission, after send, after sink commit and before canonical receipt
- Transport/local-spool/record/effect ACK variants

### Prerequisites
- Independent canonical and receiver ledgers
- Defined durable-admission and receipt meanings

### Procedure
1. Inject each boundary crash and lose each ACK independently
2. Restart/reconnect under current fences; query the same operation
3. Replay duplicate ACK and same-ID altered payload; retain unknown dispatch variant
4. Reconcile a late receiver receipt and accounting without executing again

### Independent oracle
Independent event-order oracle and actual synthetic sink count; implementation status ignored

### Exact pass predicate
Admission/reservation precedes permit; lost ACK never means success or known no-effect; same operation reconciles once; no duplicate effect and no premature liability release

### Exact failure predicate
New effect ID on retry, transport ACK treated as settlement, missing evidence converted to zero or duplicate execution

### Expected evidence
- Crash cut and last-known boundary
- Operation-query/disposition records
- Sink count and reservation history

### Stopping conditions
Stop at first duplicate/false-success; unsupported crash injection is blocked, not pass

### Passing does not prove
Exactly-once external APIs or unseen upstream retry behavior

## RX-F09 — Partition and stale spool replay

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Writer C, worker A, replacement B and partitioned message queues
- Signed synthetic observation spool containing duplicates, old grants and conflicting body IDs
- Current revocation/Stop state changes while partitioned

### Prerequisites
- Fault scheduler capable of delay/reorder/drop without external network
- Historical-observation admission separate from work dispatch

### Procedure
1. Partition A, permit only pre-admitted bounded local computation and spool
2. Attempt new offline work/renewal/child/effect
3. Advance current authority; reconnect and submit old observations/requests
4. Reconcile duplicate/conflicting observations with exact provenance

### Independent oracle
Independent canonical authority trace and scoped synthetic receiver dispatch log

### Exact pass predicate
No new offline admission or authority; old evidence remains historical and deduplicated; stale work refuses after reconnect; conflicts quarantine rather than overwrite

### Exact failure predicate
Spool turns into canonical grants, reconnect revives stale permits or missing observations are fabricated

### Expected evidence
- Partition schedule
- Observed/recorded-at and cursor bindings
- Historical evidence/refusal dispositions

### Stopping conditions
Stop at safety violation or spool limit; lost mandatory evidence yields explicit gap/hold

### Passing does not prove
Availability during every partition, honest remote reports or no physical offline computation

## RX-F10 — Lost-machine productive resume

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Checkpoint H, complete canonical suffix through K, exact source artifacts and a known-output transformation task
- Pending approval, Stop change, revoked artifact and one unknown external effect
- Corrupt/missing checkpoint/suffix variants

### Prerequisites
- Independent expected-state replay and hidden task-output oracle
- Fresh admitted destination with no copied authority or credentials

### Procedure
1. Remove source machine from available evidence; rehydrate successor from verified retained material
2. Replay and verify current goal/policy/Stop/accounting state
3. Classify every step as re-executable/resumable/settled/unknown; hold unsafe effect
4. Complete positive deterministic task under current instructions and check exact output/provenance

### Independent oracle
Independent replay reducer, fixture output key and effect/reservation ledgers

### Exact pass predicate
Recovered canonical state equals authoritative prefix/suffix; useful permitted task completes with correct current output; corrupt/missing state blocks; unknown effects and liabilities stay unresolved

### Exact failure predicate
Boot/status-only success, old instruction wins, missing event fabricated, effect retried or cumulative allowance reset

### Expected evidence
- Checkpoint/suffix/digest verification
- Recovery classification and hold reasons
- Exact output plus independent acceptance and attribution map

### Stopping conditions
Stop on any parity/privacy/effect mismatch; if required material absent, record precise blocked result

### Passing does not prove
General model reasoning continuity, human effort advantage, zero data loss or measured RTO

## RX-F11 — Sink idempotency and expiry

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Stable effect E/body X scoped to receiver R
- Identical duplicates, E/body Y conflict, out-of-order attempts and stale fences
- Durable dedup record available and expired variants

### Prerequisites
- Toy sink whose atomic mutation+idempotency ledger is independently controlled
- Declared retry/recovery retention horizon
- Canonical sink key is (receiver_scope,effect_id); immutable exact_body_digest is an equality/conflict check under that same key, never an extra namespace component

### Procedure
1. Commit E/X and lose reply; retry after process/node/writer change
2. Send E/Y and replay stale fenced request
3. Expire dedup evidence; ask recovery to retry without postcondition evidence
4. Provide authoritative postcondition reconciliation positive variant

### Independent oracle
Independent immutable sink mutation counter and exact body ledger

### Exact pass predicate
E/X causes one mutation; E/Y and stale request cause no mutation; expired dedup without truth holds; reconciliation settles existing effect rather than repeats it

### Exact failure predicate
Second mutation, altered-body acceptance or expired ledger interpreted as never executed

### Expected evidence
- Effect-key/body mapping
- Actual mutation counts
- Expiry/hold/reconciliation evidence

### Stopping conditions
Stop at duplicate effect; finish all finite variants; uncertainty remains unknown, never assumed no-effect

### Passing does not prove
Arbitrary provider idempotency, atomicity across unrelated services or rollback

## RX-F12 — Drain with in-flight work and D022 Stops

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Node A with selected actor, owned child/shell/monitor/relauncher and unrelated task
- Aggressive, Full and Lazy with named boundary/deadline
- In-flight effect, half-sent artifact and unacknowledged durable evidence

### Prerequisites
- Frozen D022 ownership/scope and authorized drain allowlist
- Independent local process and receiver observers; unknown remote member variant

### Procedure
1. Close placement/renewals and snapshot owned inventory with concurrent-child coverage
2. Inject each Stop mode before/after start/spawn/dispatch/flush/release
3. Attempt late relaunch, new publication/inference and unauthorized compensation
4. Drain positive known-settled case; timeout/partition negative case

### Independent oracle
Independent per-member process/effect/fence observation vector and durable evidence store

### Exact pass predicate
Exact mode scope/boundary is preserved; no new prohibited work/relaunch; unrelated task is unaffected; required evidence survives; unreachable/effect-unknown members prevent false drained/quiescent

### Exact failure predicate
Wrong scope, implicit rollback, evidence deleted on send ACK, publication during drain or offline member marked stopped

### Expected evidence
- Owned inventory cut
- Boundary/deadline/escalation receipts
- Per-member facts and retained evidence map

### Stopping conditions
At deadline record drain_incomplete unless predicate evidenced; stop immediately on escaped dispatch or lost mandatory evidence

### Passing does not prove
Instant remote halt, whole native process-tree containment or external compensation

## RX-F13 — Cross-OS normalization matrix

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Synthetic manifests with case/Unicode collisions, reserved names, long names, drive-relative/UNC/device names and symlink/reparse swaps
- CRLF/LF payloads and argument/environment fixtures
- Windows 26200 Home/Pro, 26100 Enterprise; Linux 6.12 and 6.6; WSL ext4 and /mnt/c distinct cells

### Prerequisites
- Exact native profile fingerprints and supported mapping policy
- Later process/filesystem probes require separately authorized disposable local targets

### Procedure
1. Evaluate portable subset and profile-specific materialization competitors
2. Reject traversal/collisions/unknown sandbox mapping before exposure
3. Preserve bytes unless explicit derivative admitted; verify source and derivative identities
4. For native stage, observe creation-time containment, exit identity, locks and commit behavior per cell

### Independent oracle
Independent expected path/byte map plus OS observers outside candidate containment

### Exact pass predicate
Every supported positive maps exactly; unsafe/ambiguous names refuse; normalization never alters approval/source identity silently; unrun/unsupported cells remain unknown with reasons

### Exact failure predicate
Silent overwrite/traversal, PID-only settlement, WSL credited as native production or process-kill credited as reset

### Expected evidence
- Per-cell exact profile and expected/observed mapping
- Byte hashes and loss reports
- Native observation receipts when separately run

### Stopping conditions
Stop on out-of-scope filesystem, secret path, privileged step or destructive action absent fresh approval; no inferred native pass

### Passing does not prove
Universal application portability, cross-OS filesystem equivalence or production support

## RX-F14 — Compromised node authority attacks

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Valid enrolled node with bounded task grant
- Forged goal/writer/event ordinal, other-node replay, self-minted fence and changed approval payload
- Resource-flood descriptors and dishonest completion report

### Prerequisites
- Independent canonical admission reference and final receiver instrumentation
- No exploit binaries; attacks are typed synthetic envelopes

### Procedure
1. Submit each forbidden command at actual admission/receiver gate
2. Try current valid command as positive control
3. Replay altered audience/body/configuration and fake completion
4. Run paired negative control with one check omitted to verify the oracle sees the intended violation

### Independent oracle
Independent canonical writer/permit ledger, receiver postcondition ledger and provenance classifier

### Exact pass predicate
All authority/recipient/fence forgeries refuse; false completion remains attributable unverified evidence; positive allowed operation succeeds; negative-control sensitivity reaches intended gate

### Exact failure predicate
Worker-selected ordinal accepted, receipt treated as truth, self-grant accepted or oracle only sees a type error

### Expected evidence
- Gate-reached markers
- Typed refusal and positive-control receipts
- Independent invariant evaluation

### Stopping conditions
Stop on first unauthorized mutation/release; no generic harness exception counts as security rejection

### Passing does not prove
Security against host-admin/kernel compromise, parser exploitation or a determined adversary

## RX-F15 — No second writer or portfolio executive

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Enrolled no-grant node N and active bounded worker W
- Requests to append canonical state, grant lease, spawn ungranted child, change goal and schedule new portfolio task
- Properly authorized canonical positive controls

### Prerequisites
- Complete canonical append/admission ownership inventory
- Independent enumeration of all issuer identities

### Procedure
1. Attempt every control action from N and W
2. Attempt to repackage them as result/event/heartbeat messages
3. Perform bounded proposal and proper canonical positive control
4. Inspect all resulting writers/leases/children and parent-goal lineage

### Independent oracle
Independent writer-fence and grant-issuer audit, not process names

### Exact pass predicate
Zero unauthorized canonical append/lease/portfolio rights; bounded proposal is inert; only current kernel admission creates authorized work; one accepted writer at each commit

### Exact failure predicate
Node origin, membership or lease turns proposal into authority; hidden executive or second append path appears

### Expected evidence
- Issuer inventory
- Accepted/refused commands with canonical ordinals
- Parent and lease lineage

### Stopping conditions
Stop at any second-authority path; incomplete writer inventory blocks qualification

### Passing does not prove
No undiscovered backdoor, whole-product correctness or future topology safety

## RX-F16 — Gaps, rollover and resource pressure

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Stream S cursor range with removed interval and replay floor
- Snapshot locator/digest and available suffix; corrupt/missing snapshot variants
- Cursor-near-limit, backward/duplicate ACK and stalled bulk/view queues

### Prerequisites
- Declared finite credit, queue and control-resource budgets
- Independent expected event log and reserved control scheduler oracle

### Procedure
1. Reconnect below replay floor; require GAP/RESET and materialize authorized snapshot
2. Attempt to fill timeline from guesses or worker timestamps
3. Exercise rollover into linked new stream and ACK cases
4. Flood bulk transfer/view path while submitting Stop/fence/current status

### Independent oracle
Independent source event set, cursor/credit arithmetic and control completion observation

### Exact pass predicate
Every real gap marked; no fabricated event; valid snapshot reconstructs only evidenced state; no wrap/backward release; duplicate ACK no-op; bounded control path progresses within adopted bound

### Exact failure predicate
Gap hidden, snapshot digest with no bytes treated restored, resource cap exceeded or control starved without failure

### Expected evidence
- Gap/reset/snapshot chain
- Credit/queue high-water and control progress
- Reconstructed versus source event set

### Stopping conditions
Stop at safety/cap breach; absent adopted timing bound is unknown, not a guessed pass

### Passing does not prove
Production throughput, unlimited retention, complete physical timeline or real-time scheduling

## RX-F17 — Lean core and idle execution node

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Core absent, installed-disabled, enabled-idle executor and active remote/full manifests
- Dependency/import/startup declarations; synthetic provider-dispatch trap
- Health budget and separate availability-coordination budget
- Per-probe enabled inert synthetic controls for provider-attempt detection, helper/descendant activation and work-lease activity, with expected detections and defined reset/baseline

### Prerequisites
- Independently reviewable build/runtime closure of chosen candidate
- Full descendant/helper observation; no actual provider endpoint configured
- Each required absence detector independently demonstrates expected sensitivity under the identical observer configuration and reset/baseline used for idle observations; retain detection receipts. Task acceptance is not probe calibration.

### Procedure
1. Inspect core build closure and launch only in a later authorized local fixture
2. For every provider-attempt, helper/descendant activation and work-lease probe, run an enabled inert local synthetic positive control through its actual observation path with the same observer configuration; compare expected and detected events and retain receipts; no real provider/network call
3. Apply the documented same reset procedure and baseline to each control and absence observation; verify reset/baseline identity and complete observer coverage
4. Observe each lifecycle state with no work admitted; report a per-probe zero only if its matching sensitivity control passed. Blind, failed or uncalibrated probes remain UNKNOWN
5. Attempt hidden wake/helper/model/election activation in disabled path and evaluate with the already calibrated observers; ordinary accepted tasks do not substitute for sensitivity evidence
6. Activate the required availability plugin separately and attribute its declared coordination overhead

### Independent oracle
Independent dependency/runtime inventory, process/helper counters, lease table and inert provider-attempt trap; each probe has its own expected-versus-detected enabled synthetic sensitivity receipt under the same observer/reset/baseline as its absence observation

### Exact pass predicate
Default core has no consensus/fabric activation; idle executor has zero work leases/provider attempts/helper inference and only bounded allowed health activity, with all metadata/coordination footprint attributed separately. Every zero claim is supported by a matching retained per-probe enabled synthetic detection receipt and identical observer/reset/baseline identity. No blind, failed, missing or uncalibrated probe is reported as zero; ordinary task acceptance is not calibration.

### Exact failure predicate
Consensus required by core, hidden helper inference, heartbeat renews lease, detector misses its enabled synthetic control, control/absence observer or reset/baseline differs, ordinary task acceptance used as probe calibration, or unobserved activity reported zero. A failed/blind probe makes the associated absence result UNKNOWN rather than evidence of inactivity.

### Expected evidence
- Edition/dependency and observer/configuration identities
- Per-probe expected/detected enabled synthetic sensitivity receipts for provider attempts, helpers/descendants and work leases
- Matching reset procedure/baseline receipts for sensitivity and absence observations
- Provider-attempt/helper/lease/health observations with coverage and per-probe UNKNOWN reasons where needed
- Separate active-availability overhead

### Stopping conditions
Stop if any external endpoint/account is requested; blind/failed/missing probes or incomplete observer graph produce UNKNOWN, not zero. Fix and recalibrate the probe before drawing an absence conclusion.

### Passing does not prove
Subscription billing zero, literally zero installed overhead or achieved resource targets

## RX-F18 — Placement tradeoff comparison

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Same bounded workload manifest and node fact versions for both candidates
- Hard constraints, rule priority policy and Pareto preference policy
- Observed, estimated and null cost/latency/resource dimensions

### Prerequisites
- Adopted thresholds and tradeoff authority before evaluation
- Independent measurement definitions per R-O; no fabricated numeric scoring

### Procedure
1. Apply identical eligibility filter to both arms
2. Record complete candidate/refusal evidence and preference path
3. Inject unknown/stale cost/load and policy changes
4. Compare accepted outcome vectors and expose non-dominated tradeoffs

### Independent oracle
Independent eligibility oracle plus blinded evaluation of retained measurement inputs

### Exact pass predicate
Both arms obey every floor; unknown stays null; preference never silently widens egress/spend; decisions can be reconstructed from recorded facts; no winner without sufficient observed evidence

### Exact failure predicate
Opaque score hides violation, null becomes zero, unequal floors or after-the-fact threshold tuning

### Expected evidence
- Workload/policy/fact manifest
- Per-arm receipt and full vector
- Blocked comparison reasons

### Stopping conditions
Stop on floor violation; if observations insufficient, return bounded unknown rather than rank

### Passing does not prove
Best scheduler, savings, general latency or productive-continuity superiority

## RX-F19 — Privacy, copy accounting and credential exclusion

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Synthetic ContentEnvelope with project_and_audience/privacy_domain_id and scoped handles
- Sentinel credential-like strings only in forbidden synthetic boundary fixtures
- Revoked source, metadata/equality probes, partial transfer and lost-node copy
- Durable exposure intents registered before and after a deletion-inventory cut, with copy observation UNKNOWN
- Crash after publication but before observation; partial transfer and missing publication ACK variants

### Prerequisites
- Complete permitted output/log/dead-letter channel inventory
- Q CopyRecord and R-T representation lineage; independent egress observer
- Independent inventory oracle includes unresolved exposure intents/possible copies; no inherited CopyRecord planned/staged status

### Procedure
1. Request metadata under wrong audience and probe raw digest equality; require current authorization before durable intent/transfer Include a private manifest and remote-quarantine chunk as actual recipient disclosures; authorized local private staging is the separate no-disclosure positive case.
2. Place synthetic sentinel in each prohibited capsule/output/log field and test rejection without diagnostic echo
3. Register separate exposure intent with expected CopyRecord, lineage and reservation; verify it does not assert copy presence
4. Race deletion-inventory cut/revocation against intent registration, chunk transfer and protected publication; include unresolved pre-cut intents/possible copies and reject stale post-cut publication
5. Crash before/after publication and before independent observation; restart with recovered intent and same operation/transfer identity/reservation; reconcile publication_unknown without assumed absence or blind retry
6. Account independently observed copies, prior/partial disclosures, unknown publication and lost node; do not claim erasure or settle/release unknown obligations

### Independent oracle
Independent exposure-channel recorder plus canonical intent/lineage/reservation and copy-inventory-cut oracle; synthetic sentinel observations are separate from copy-presence/settlement truth Sender egress is independently observed separately from remote quarantine arrival and task-visible publication.

### Exact pass predicate
No unauthorized metadata/content/sentinel release; base scope fields match Q/T. Durable separate intent precedes transfer/publication without inventing Q CopyRecord statuses or asserting presence. Deletion cuts include unresolved intents/possible copies; fresh rights/fence/cut check rejects revoked or stale publication, including restart. Publication_unknown preserves the same operation/transfer identity and reservation until independent reconciliation. Prior disclosures remain accounted and lost-node erasure stays unknown. Remote quarantine counts as node disclosure: before sender release of every relevant private manifest metadata/chunk, the scoped durable exposure intent and potential-copy inventory obligation, lineage and reservation already exist. Intent asserts neither present nor delivered; later verified task publication has a separate current-rights/fence gate.

### Exact failure predicate
Secret in capsule/log, scope alias error, unregistered exposure, expected copy called present, invented CopyRecord status, deletion-cut omission, cache bypass, stale rights publication, unknown publication guessed absent/retried or false deletion/settlement

### Expected evidence
- Q/T base-field correspondence and per-channel synthetic sentinel/exposure results Include independent sender-release ordering, potential-copy inventory obligation and distinct remote-arrival versus task-publication observations.
- Durable exposure-intent/lineage/reservation registration and expected CopyRecord references
- Deletion-inventory cut with unresolved intent/possible-copy membership and fresh publication-gate decisions
- Crash/restart trace retaining same operation/transfer identity and reservation
- Independent publication/copy observations or explicit UNKNOWN/publication_unknown, residual-retention and reconciliation receipts

### Stopping conditions
Stop on first forbidden disclosure; absent channel coverage prevents clean-leak claim

### Passing does not prove
Universal covert-channel noninterference, physical erasure or trusted-launch qualification

## RX-F20 — Broker and fabric semantic correspondence

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Synthetic broker command/receipt corpus with four G05 blocker cases
- Fabric wrappers carrying exact original command identity
- Reconnect, UI attach, approval replay and snapshot materialization variants

### Prerequisites
- Ratified/explicitly candidate version contracts on both sides
- Independent mapping oracle and loss report; no inferred wider cursor type

### Procedure
1. Map command through fabric-to-broker adapter and back
2. Negotiate incompatible version and missing required capability
3. Exercise digest-only snapshot, cursor exhaustion and duplicate/backward ACK
4. Reconnect/reattach views and replay exact approval receipts

### Independent oracle
Independent schema/cursor/receipt correspondence checker and synthetic effect ledger

### Exact pass predicate
Mapped identity/authority/receipt semantics preserved or explicitly refused; snapshot bytes resolvable only with current scope; ACK releases only declared pending state; view reattach causes zero effect dispatch

### Exact failure predicate
Silent semantic downgrade, approval broadened, cursor coerced/wrapped or ACK settles an effect

### Expected evidence
- Input/output mapping plus explicit loss report
- Four-blocker dispositions
- No-effect reattachment observation

### Stopping conditions
Stop at unresolved version/mapping ambiguity; G05 remains open until native implementation evidence exists

### Passing does not prove
Frozen broker/fabric wire protocol, chosen encoding or platform conformance

## RX-F21 — Automatic takeover behind availability seam

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Synthetic current writer W1, candidate W2 and plugin membership/commit witness
- Old writer delayed append, quorum loss and membership-change cuts
- Availability toggle enabled and disabled; old-backup restore

### Prerequisites
- Separately qualified candidate plugin contract with explicit sufficient fault assumptions
- Independent canonical-store commit/fence oracle; no consensus library selected here

### Procedure
1. Under declared sufficient conditions, lose W1 and let plugin acquire fresh writer fence and committed prefix
2. Submit old writer and current writer appends across all takeover cuts
3. Remove required availability condition and attempt both sides
4. Restore old backup/membership and toggle off plugin; inspect safe core-only status

### Independent oracle
Independent accepted canonical event sequence and writer-fence/membership history

### Exact pass predicate
Automatic plugin takeover proceeds under its declared sufficient model with exactly one accepted writer; stale appends and unsafe partition commits reject; old restore cannot lower floor; disabled core shows availability loss honestly

### Exact failure predicate
Two accepted writers, guessed fence on lost authority, new writer discards committed suffix or consensus needed in core

### Expected evidence
- Membership/commit/fence proof
- Old/new writer append outcomes
- Toggle and blocked-availability evidence

### Stopping conditions
Stop at double commit or lost committed state; absence of qualified plugin is blocked, not a simulated product pass

### Passing does not prove
Unconditional zero downtime, Byzantine coordinator tolerance, numeric RPO/RTO or every-partition availability

## RX-F22 — Unknown effects and reservation conservation

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Cumulative normal/recovery ledger with one settled effect and one uncertain liability
- Outstanding reservation carrying uncertainty annotation
- New node/attempt/writer, late receipt, cancellation and duplicate cumulative meter updates

### Prerequisites
- R-R existing canonical ledger semantics and independent arithmetic oracle
- Exact native units, observation source and horizon

### Procedure
1. Recover and replay ledger without resetting cumulative normal/recovery allowance
2. Lose effect ACK, replace node and try release/new reservation for same liability
3. Ingest late authoritative settlement and replay duplicate cumulative meter
4. Try to count uncertainty as both reservation and separate liability total

### Independent oracle
Independent typed-unit ledger arithmetic and effect-state oracle

### Exact pass predicate
Existing unresolved liability remains attached exactly once; recovery allowance never resets; only supported authoritative settlement changes status; unknown quantities remain null with reason; duplicates do not double count

### Exact failure predicate
Possible liability released, cancelled treated free, double-counted uncertainty or new run erases spent budget

### Expected evidence
- Before/after typed ledgers
- Source receipt identity and dedup trace
- Reservation/uncertainty linkage

### Stopping conditions
Stop at conservation or unit mismatch; unavailable counter blocks bound-dependent admission

### Passing does not prove
Exact provider bills, subscription portability or zero-cost cancellation

## RX-F23 — Native durability and supervisor races

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Qualified candidate build/profile manifest plus synthetic committed events/fence state
- Fault cuts at floor persist, canonical append, artifact expose and ACK
- Separate native Windows/Linux and WSL development fixtures

### Prerequisites
- Fresh separate Owner authorization for each disposable native/reset target and elevated/destructive step
- Independent external checkpoint/fence/effect oracle; instrumentation proves requested fault actually happened

### Procedure
1. In later local session, execute bounded non-destructive race cases first
2. Only with fresh approved reset authority, cut at declared commit boundaries using abrupt VM reset
3. Replay retained committed prefix and receiver floors; compare exact canonical state
4. Observe spawn/Stop/relauncher containment separately on every native profile

### Independent oracle
Independent pre-fault committed-state/fence ledger and post-reset replay observer

### Exact pass predicate
Acknowledged committed state and monotonic fences survive the declared fault model; replay identical; fault_triggered evidence true; native process races meet exact profile contract; no substitute fault earns pass

### Exact failure predicate
Committed prefix lost, floor regresses, trace says pass when fault not triggered, or WSL/process kill substituted for native reset

### Expected evidence
- Exact OS/build/filesystem/security profile
- Fault-trigger receipt and cut identity
- Pre/post canonical-state and receiver-floor evidence

### Stopping conditions
Do not start until authorization/instrumentation exists; abort on target mismatch/unexpected privilege/host impact; stop at first destructive anomaly

### Passing does not prove
Physical disk power-loss survival, all hardware, production safety or broader system certification

## RX-F24 — Schema evolution and aggregate resource limits

Status: **UNEXECUTED**. Entry point: none verified. Result: unknown.

### Inputs
- Class-specific valid messages plus unsupported critical fields and version sets
- Oversized claimed lengths, nesting, credit increments and unfinished transfer counts
- Reconnect/stream rollover with existing resource debt

### Prerequisites
- Finite adopted message/aggregate limits and exact schema negotiation policy
- Independent allocation/credit ledger; no parser exploit payloads

### Procedure
1. Accept supported bounded positive corpus
2. Reject unsupported critical fields, missing dependencies and invalid numeric domains before allocation/dispatch
3. Accumulate many individually valid credits/transfers until aggregate ceiling
4. Reconnect/rollover and verify resource debt remains attributed instead of resetting

### Independent oracle
Independent bounded arithmetic and class/identity schema oracle

### Exact pass predicate
Unsupported/oversized messages refuse before effect/unbounded allocation; individual and aggregate ceilings hold; reconnect/rollover cannot reset debt; valid compatible positives succeed

### Exact failure predicate
Per-message cap mistaken for total cap, unknown critical field ignored, scope broadened or reconnect creates free credit

### Expected evidence
- Class/version decisions
- Allocation and credit high-water receipts
- Positive compatibility and refusal cases

### Stopping conditions
Stop at bound violation; absent finite bound blocks eligibility rather than invented threshold

### Passing does not prove
Parser memory safety, chosen serialization, real traffic latency or denial-of-service immunity

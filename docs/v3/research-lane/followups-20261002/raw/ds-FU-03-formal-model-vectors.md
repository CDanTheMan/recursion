---
title: Formal model and byte conformance specification
source-prompt: FU-03 — formal model and byte conformance
session: Codex Dot follow-up research — specification only, target experiments NOT run
retrieved: 2026-10-02
status: research-evidence-not-a-decision
verification: not independently verified by Recursion; target experiments not run
---

# Formal model and byte conformance specification

FU03 research report for the Recursion v3 Owner and local validation agents

Evidence cutoff 1 October 2026 • Scope clarification incorporated 2 October 2026 • Candidate specification CAND RCV1 20261001

## 1 Findings and acceptance status

The kernel freeze remains conditional. The Owner has clarified that Hermes is retired and v3 is a standalone harness that also wraps and orchestrates other harnesses. All authority statements here use that current scope; H below is only a synthetic authorized control principal. The supplied handoff fixes the model bounds, the seventeen invariant names, TLA plus TLC as the primary instrument, Alloy 6.2.0 as the cross check, and the 36 of 36 mutant classification threshold. It does not supply the earlier invariant formulas, the complete mutant list, the six authority dimensions, the interior refusal names or their allocation to codes 1 through 16, or the exact historical binary layouts. Those details cannot honestly be recovered from public sources.

This report therefore makes a precise candidate completion of those missing details. The candidate fixes proposed semantic choices for local module and fixture transcription. It is not compiled source or a claim that its definitions were previously accepted; a transcription audit must expose any remaining ambiguity before execution. The original source definitions, if available locally, take precedence after an explicit reconciliation record. Any incompatible difference is an Owner decision, not a license to silently change an accepted rule. The local execution handoff in section 14 lists the work still needed.

The consequential findings are:

- The safety run must contain independent committed history, replay state, projection state, and effect dispatch observations. An assertion that compares a reducer to another call to itself cannot kill a shared reducer defect.
- Exact duplicate commands must be separated from fresh authority. Reusing an immutable committed receipt may remain valid after an epoch change; dispatching a new effect using that old receipt is forbidden. An uncertain commit is reconciled by command identity before any retry.
- The RCV1 record is test interchange. Its CBOR payload may carry arbitrary test input as an opaque byte string, including malformed CBOR and JCS floats. Neither its framing nor its integer only semantic profile chooses the broker wire format.
- A symbolic injective DigestOf deliberately rules out collisions. TLC state fingerprints, real SHA-256, and application authentication are three different things. None may be conflated with the symbolic abstraction.
- A passing finite baseline, an untriggered mutant, identical output from two related stacks, and a trace accepted after silently dropping fields are insufficient evidence.
- The primary instrument is falsified for this purpose if it cannot expose the preregistered reachable guard faults using independent monitors, or cannot explore the required three lease epoch, PAUSE and effect interaction within the preregistered resource envelope. Smaller models remain useful diagnostic evidence, not substitutes for the accepted integrated bound.

No checker, reducer, benchmark, target runtime, external effect, crash fixture or implementation was run. No mutant was killed. No binary corpus was generated or reproduced. No checker or container digest was measured. Report generation and document checks are the only local computations used for this deliverable. Product language, store, broker transport, renderer, availability contract and kernel freeze remain unselected.

### Evidence labels

SD means source documented in a primary public source. LO means locally observed in this session, limited to the supplied brief and document artifact checks. I means an inference or proposed design. U means unverified. High, medium and low describe confidence in the stated bounded claim, never confidence in an unperformed test. All numbered specification requirements below are I with medium confidence until reconciliation and independent validation; they are normative only within the candidate profile. All run, kill, equivalence, byte parity and performance outcomes are U.

## 2 What the public evidence establishes

TLA specifications distinguish state predicates, actions, temporal behavior and refinement; finite model results do not establish an unbounded implementation proof. TLC provides explicit state exploration, while fairness and liveness require separate treatment. The current official tool repository identifies a moving 1.8.0 prerelease, so a friendly release name or mutable download is not an immutable experiment identity. The official 1.7.4 release is a suitable research reference pin, but the actual JAR and runtime bytes remain to be pinned locally. [S1–S4]

Alloy 6 adds mutable relations and temporal operators. Bounded temporal checks explore a finite time scope, while complete checking uses an appropriate backend with finite object scopes. The older statement that Alloy has no native state machine idiom is unsuitable as a description of Alloy 6. The named independent cross check remains Alloy 6.2.0, whose official release identifies 9 January 2025. [S5–S7]

RFC 8949 supplies CBOR encodings and deterministic encoding rules; an application must still choose a data model, reject duplicate keys and define additional restrictions. RFC 8785 supplies JCS, including ECMAScript number serialization, UTF-16 property ordering and no Unicode normalization. They are different formats. RFC 8610 can document a data schema but is not, by itself, a strict deterministic byte validator. [S8–S10]

FIPS 180-4 defines SHA-256. A trailing unkeyed digest detects changes relative to the digest supplied; it authenticates no author. The use of distinct preimages for distinct digest purposes is a design choice here, with domain separation an established construction pattern exemplified by RFC 9162. It does not prove collision impossibility. [S11–S12]

| Claim | Pin and source | Class and confidence | Expiry or invalidation trigger |
|---|---|---|---|
| Finite checking is bounded by modeled state and assumptions | Specifying Systems, 18 June 2002 text, 4 July 2021 PDF, chapters 8, 10 and 14; S1 | SD high | Different semantics or claimed generalization beyond scope |
| A trace witness is weaker than a proved refinement | Lamport, Refinement in State-Based Formalisms, 18 December 1996; S2 | SD high | New proof obligations or a machine checked mapping supplied |
| TLC CLI and runtime are separately pin worthy | Official TLC CLI documentation accessed 1 October 2026; S3 | SD high | Tool, JDK, options or documentation changes |
| Version 1.7.4 release reference exists | Official release, commit abbreviation 5a47802; S4 | SD high; downloaded binary identity U | Any artifact byte, full commit or package change |
| Alloy 6.2.0 is the named cross check | Official release 9 January 2025, 59ba203; S5 | SD high | Artifact, solver, options or syntax change |
| Alloy time and object bounds are separate | Alloy 6 documentation and language reference; S6, S7 | SD high | Different backend or temporal scope |
| CBOR deterministic profile needs application constraints | RFC 8949 December 2020, sections 4.2 and 5; S8 | SD high | Relevant erratum or profile/schema change |
| JCS cannot be substituted for CBOR | RFC 8785 June 2020, sections 3.1 and 3.2; S9 | SD high | Relevant erratum or explicit mapping epoch change |
| CDDL is schema notation, not this whole byte contract | RFC 8610 June 2019; S10 | SD high | Additional byte validation layer proved |
| SHA-256 is not authentication or an injective function | FIPS 180-4 August 2015; S11 | SD high for algorithm; security implication I high | Cryptanalytic change or updated algorithm policy |
| Typed digest domains avoid accidental cross purpose equality of identical encodings | Proposed rule, informed by S12 section 2.1 | I medium | Preimage ambiguity, collision or domain omission found |
| All original 36 mutations and refusal names are recoverable here | No such evidence supplied | U, not asserted | Local historical definitions supplied and reconciled |
| Raw negative zero parsing has a security erratum distinct from serialization | RFC 8785 erratum 7920, verified 15 May 2024; S14 | SD high; secure profile allocation I medium | Erratum status or accepted input policy changes |
| Current candidate passes model or byte checks | No run artifacts | U, not asserted | Valid retained receipts and independent review |

The report pins references, not a claim that retrieved mutable web pages have immutable content digests. Local agents must archive relevant source documents and record their hashes in the run bundle. Research access date is not a release date. A prerelease stream must never be described as the immutable baseline. [S3, S4]

## 3 Candidate model modules and constants

### Module boundaries

The exact proposed module set is RTypes, RDecode, RAdmit, RReduce, RPacket, RReplay, RProject, RReference, RMonitors, REnvironment, RIntegrated and RMutants. Each is a TLA module; RTypes extends Naturals, Integers, Sequences and FiniteSets. No Java operator override, generated implementation source, external function, random oracle, wall clock or host I/O is part of the model. The local translation must record the SHA-256 of every module and configuration.

RTypes owns finite domains, record shapes and total helper operators. RDecode maps finite input classes to commands or structured refusals. RAdmit is a total deterministic function of canonical state and a decoded command. RReduce folds a validated event batch into canonical state. RPacket derives a packet or a structured refusal from state and a worker identifier. RReplay and RProject are the target replay and projection paths, separately authored from the live reducer. RReference is the immutable relational history oracle and may not import RReduce, RAdmit, RPacket, RReplay or RProject. Mutations may alter a target path, never RReference or its assertions. RMonitors uses RReference plus observations. REnvironment supplies finite queue, delivery, pause, crash and effect schedules. RIntegrated defines Init and Next. RMutants changes exactly the named operator or action site for one mutant at a time; no monitor is mutated.

The abstraction has two levels. AbstractKernel has only a committed canonical state, committed event sequence, immutable command receipts and declared packet result. Integrated adds pending admission, append preparation, delivery, volatile observations, crash and independent monitors. Its proposed mapping is the committed boundary tuple, hiding preparation and diagnostic steps as stuttering. This mapping is a stated obligation, not a proved theorem. The trace bridge in section 12 checks finite instances of it.

### Fixed constants

| Constant | Exact candidate value | Provenance and role |
|---|---|---|
| Aggregates, Tasks, Effects, Timers, Verifiers | Each singleton, represented by 1 in its own typed domain | Given bounds; do not identify different domains merely because all use 1 |
| Workers | {1, 2} | Given bound |
| GoalEpochs, PlanRevisions | {1, 2}, {1, 2} | Given bounds |
| LeaseEpochs | {1, 2, 3} | Given bound; no wraparound |
| Attempts | {1, 2} plus 0 only as not started sentinel | Given bound |
| PauseEpochs | {0, 1} | Candidate interpretation of two epochs; exactly one PAUSE increment can be represented |
| QueueCapacity, MaxCommittedEvents | 2, 20 | Given bounds; event count, not command count |
| CommandIds | 1..20 | Candidate completion; identifiers may repeat, first accepted use is immutable |
| WriterEpochs | {1, 2} | Additional candidate adapter fencing dimension; not claimed as a given DS22 bound |
| Principals | {H, W1, W2, X} | H control authority, X unauthorized; workers are W1 and W2 |
| VerifierPrincipal | W2 | One verifier role; W2 may also produce, so self verification is reachable |
| ResultValues | {None, R1, R2} | Distinct opaque payload atoms |
| EffectOutcomes | {Success, KnownNoEffect, Unknown} | No outcome inferred from missing acknowledgment |
| WireClasses | canonical command records plus 7 malformed classes | Truncated, duplicate key, nonshortest, bad UTF-8, tag, float, unknown schema |
| MutantId | Baseline or exactly one integer 1..36 | Baseline has all guards enabled |
| Symmetry, view reduction, state constraints | None, none, none | First authoritative run; no pruning that hides a guard witness |

Any reduced debugging bound has a distinct configuration identity and cannot satisfy the integrated gate. The event cap is an explicit transition guard, not a TLC state constraint. At the cap, observational and rejection transitions can still occur; no successful new event batch can be appended. The cap itself does not mean production overload or success. Queues contain at most two entries unless a mutation deliberately violates that property.

### State and initial values

The canonical state K has schema epoch 1; aggregate 1; ordinal 0; tail Genesis; goal 1; plan 1; lease 1; writer 1; pause epoch 0; paused FALSE; task status Ready; owner W1; attempt 0; no result; result producer None; verifier result None; effect None; timer Disarmed; retry ready FALSE; cancelled FALSE; empty command receipt map; and empty durable outbox. Genesis is a distinct symbolic digest atom. Integer enums in the byte schema are given in section 8.

Effect is a record with status in {None, Prepared, InFlight, Unknown, Succeeded, KnownNoEffect}, effect id 1, producing attempt, captured goal, plan, lease and pause epochs, issuing command id, and token. Fields not yet assigned have the unique None value. Result contains value and producer. Timer contains status {Disarmed, Armed, Fired}, attempt and captured goal/plan/pause epochs. A command receipt contains the complete command digest, event ordinal interval, final event digest, result class and result bytes; it contains no pointer back to the state digest. Result class is 0 for committed. Result bytes are C({0:command id, 1:first ordinal, 2:last ordinal, 3:last event digest}), never a serialized state or post state digest. Cached reuse returns the same class and bytes. This avoids a recursive state digest definition.

Integrated variables are K, Log, Inbox, Pending, VolatileReply, DeliveryQueue, Issued, Crashed, RecoveryNeeded, DispatchPermit, ReplayInput, ReplayCursor, ReplayState, ReplayStatus, ProjectionState, ProjectionCursor, and Obs. Pending is None or a record of command, admission snapshot, admitted batch and prepared candidate state. Issued is a sequence of actual dispatch observations with token and all fencing fields. Obs is a bounded record of the latest transition, prestate, poststate, old/new log, command, packet and externally observed result. It replaces its prior value each step; it is not an unbounded trace. Inbox and DeliveryQueue are sequences. Log contains at most 20 events. Issued contains at most 20 observations in the baseline; attempting a twenty first dispatch is disabled independently of successful safety. ReplayInput is a sequence of at most 21 records, allowing one extra corrupt or duplicate record to be tested.

Initially all queues and logs are empty, Pending is None, Crashed FALSE, RecoveryNeeded FALSE, DispatchPermit None, all replay/projection cursors are 0, both independent states are the canonical genesis state, and replay status is Idle. The environment may choose future inputs but cannot directly alter K, Log or monitor state except through the actions below.

### Total helper definitions

Prefix(s, n) is s[1..n], including the empty sequence at n=0. Append concatenates sequences. Replace replaces exactly one record field. Any guard referencing a missing field is FALSE, never an evaluator error. All functions return a tagged Ok(value) or Refuse(code, detail); no implicit exceptions are results. Body(e) removes only its self digest field. DigestOf(tag, x) is the symbolic pair <<tag, x>>, so equality implies equality of tag and value. Nested terms remain finite because event and command histories are bounded. It is explicitly stronger than SHA-256.

Expected(K, c) means c.expectedOrdinal=K.ordinal and c.expectedStateDigest=DigestOf(state, CanonicalState(K)). Command digest binds every command field including expected state and all authority tokens. Receipt lookup is by command id, with equality checked against the complete command digest. These choices create exact duplicate semantics and prevent a same id changed payload from being mistaken for a retry.

### Finite input enumeration and operator closure

The environment enumerates typed command records with schema in {1,2}, id in 1..20, kind in {0..17,255}, aggregate/task target in {1,2}, principal in {H,W1,W2,X}, capability in 0..17, goal/plan/writer in {1,2}, lease in {1,2,3}, pause in {0,1}, attempt in {0,1,2,3}, and expected ordinal in 0..21. State carrying identifiers remain the singleton1; target2 is foreign. Attempt3 and ordinal21 are input boundary values, not valid canonical state values. Payload uses the section 8 maps plus BadPayload, which refuses FIELD_INVALID. Token values are DigestOf(effecttoken, <<1,1,a,c>>) for a in Attempts and c in CommandIds, plus WrongToken; retained old tokens are in this same finite set. Unknown kind 255 carries {}. Seven opaque malformed tokens cover the WireClasses row; they do not attempt to model raw arbitrary bytes.

For each current committed log L, the permitted symbolic expected digest inputs are WrongDigest plus DigestOf(state,RefState(Prefix(L,n))) for every complete batch prefix n in 0..Len(L). WrongDigest is a distinct atom. This gives current, stale and wrong digest cases without an unbounded environment hash universe. It is an abstraction of equality classes, not a cryptographic claim. Event corruption inputs are exactly: identity, one wrong predecessor, one wrong self digest, one ordinal gap, one foreign aggregate, one unknown schema, one unknown kind, omission of one record, duplication of one record or swap of two adjacent records of a committed log, retaining the21 record input bound. BeginReplay chooses from this finite set. Repeated corruption composition is outside the first model and remains a byte/trace negative control extension.

Pending.stage is one of Decoded, Admitted or Prepared. An Ok tagged value contains the complete result; a Refuse tagged value contains only code/detail. Lookup returns None or exactly one receipt. CompleteBatchPrefix recognizes only boundaries identified by the command batch envelope. Body removes key 8 from an event and no other field. RefState is defined only on RefValid complete batch prefixes; every caller checks that guard before evaluation. Decode, Admit, Reduce and DeriveWorkPacket are total by a final catch all FIELD_INVALID/BAD_TRANSITION case; the reference relation may be false but never contains an undefined lookup. An invalid preparation yields a refusal observation and clears Pending without publication. RTypes must implement guarded record access with nested IF, not assume that a missing field in a conjunction is safe in every evaluator.

All record fields not assigned in an update retain their old values. Inbox enqueue choices come from the finite command/token set above. QueueDelivery may enqueue only the packet in the immediately preceding successful Derive observation; older packets survive only in the bounded delivery queue. External outcomes are the three fixed atoms and never supply new identifiers. These definitions close the candidate enumeration; the local transcription audit must reject any extra unconstrained constant, free choice, implicit default or use of the implementation under test as an expected value oracle.

## 4 Pure function semantics and integrated transitions

### Decode and admission order

Decode operates on the finite input classes in the model. The byte corpus, not TLC, tests real parsers. Decode rejects malformed structure before canonicality; it then checks schema epoch, command kind, exact field set and field domains. Success returns the full typed command, preserving every authority, epoch and expected state field. It may not silently normalize, ignore unknown fields, collapse duplicate keys or substitute defaults.

Admit(K, c) applies the following ordered checks. This order is also the refusal precedence rule. The first failed check wins; secondary diagnostics are excluded from normative bytes.

1. If the command id already exists, equal command digest returns the exact cached receipt with no events; unequal digest returns COMMAND_CONFLICT. This does not produce or dispatch a new packet.
2. Require Expected(K, c), otherwise EXPECTED_STATE_MISMATCH.
3. Require exact aggregate and task targets, authorized principal for the command kind and exact capability token, otherwise AUTHORITY_DENIED. Authority is the conjunction of six dimensions: aggregate, task, goal, plan, principal and capability. Goal and plan get their more specific codes at steps 4 and 5.
4. Require c.goal=K.goal, otherwise GOAL_EPOCH_STALE.
5. Require c.plan=K.plan, otherwise PLAN_REVISION_STALE.
6. Require c.writer=K.writer. A mismatch uses AUTHORITY_DENIED with WRITER_EPOCH detail. This is separate from the worker lease.
7. Worker commands are exactly Start, Submit, Retry, PrepareEffect and MarkDispatch. For these require c.lease=K.lease and c.principal=K.owner, otherwise LEASE_EPOCH_STALE or AUTHORITY_DENIED respectively. Verify is not a worker command: it requires the current numeric lease but no owner equality, and independently requires the designated verifier, current goal/plan/writer/pause/attempt and exact submitted result binding. Its actor/verification failures use VERIFIER_INVALID. Control commands do not acquire worker ownership by carrying a lease field.
8. Require c.pauseEpoch=K.pauseEpoch for every fresh command. If unequal return PAUSE_EPOCH_STALE. If paused, forbid Start, Submit, Retry, PrepareEffect, MarkDispatch, ArmTimer and FireTimer with PAUSED. Pause, Resume, Cancel, epoch/lease changes, ObserveEffect and ReconcileEffect remain available subject to their own guards.
9. If cancelled, forbid every new task progress, retry, result acceptance, effect preparation or dispatch with CANCELLED. Cancel itself is idempotent only by command id; a new Cancel command in cancelled state is FIELD_INVALID with BAD_TRANSITION. Effect observation and reconciliation may still record external truth without reviving the task.
10. Check attempt, task transition, effect, verifier, timer and capacity rules below, in that order. Invalid capacity is FIELD_INVALID with CAPACITY. A new batch whose length would exceed 20 is not admitted in the finite environment; it yields OUT_OF_SCOPE at the harness boundary rather than a production refusal.

H alone may grant/revoke leases, change goal/plan/writer, pause/resume/cancel, arm/fire timers and reconcile effects. The lease owner may Start, Submit, Retry, PrepareEffect and MarkDispatch. ObserveEffect is supplied by H as an adapter observation, not as independently established truth. Verify is permitted only to VerifierPrincipal with verification capability, and must be different from the stored producer. Capabilities are kind specific atoms, so possession of one never implies another. The six authority dimensions are candidate completions, not historical facts recovered from DS22.

### Event generation and reduction

Except for PrepareEffect, every admitted fresh command produces one event of the same kind. PrepareEffect produces two events in order: EffectPrepared and OutboxEnqueued. Those two events are an indivisible batch at the committed boundary. Payloads include the complete command digest, command id, principal, relevant epochs and the named arguments. Every event carries the next ordinal, previous event digest and writer epoch. The first event of a batch follows the existing tail; the second follows the first.

Reduce validates schema, event kind, aggregate, writer epoch, ordinal and previous digest before applying the corresponding equation below. It returns a candidate state only if the whole batch validates. Partial valid prefixes are not externally published as the result of an atomic batch. The receipt and outbox join the same committed transaction as the canonical state and events. A separate public replay operation can report a valid prefix cursor after a corrupt log, but may not resume command admission from it as if the complete store were healthy.

| Command or event | Guard beyond common admission | Exact semantic update |
|---|---|---|
| GrantLease(worker) | H, worker in Workers, lease<3 | lease:=lease+1; owner:=worker; leave task/result/effect untouched |
| RevokeLease | H, lease<3 | lease:=lease+1; owner:=None; leave outstanding effects explicit |
| AmendPlan | H, plan=1 | plan:=2; clear retry ready; disarm timer; no task resurrection |
| AdvanceGoal | H, goal=1 | goal:=2; clear retry ready; disarm timer; no task resurrection |
| AdvanceWriter | H, writer=1 | writer:=2; pending old writer proposals become stale at commit |
| Pause | H, not paused, pauseEpoch=0 | pauseEpoch:=1; paused:=TRUE; no new dispatch after commit |
| Resume | H, paused | paused:=FALSE; pauseEpoch remains 1; old epoch packets remain invalid |
| Start | owner present, status Ready, attempt=0 | status:=Running; attempt:=1 |
| Submit(value, outcome) | current owner, status Running, c.attempt=attempt | success: status:=Submitted, result:=value, producer:=principal, result scope:=current attempt/goal/plan/lease; failure: status:=Failed, result:=None; value in {R1, R2}, outcome in {success, failure} |
| Verify(value) | status Submitted, value=result, principal=W2, principal differs from producer, matching current attempt and stored result goal/plan; no owner equality | status:=Done; verifier result:=value; no effect issuance |
| ArmTimer | H, status Failed, timer Disarmed, attempt<2 | timer:=Armed with current attempt/goal/plan/pause; retry ready:=FALSE |
| FireTimer | H, timer Armed and captured fields current | timer:=Fired; retry ready:=TRUE; firing is an explicit input, not wall time |
| Retry | status Failed, retry ready, attempt<2, effect None or KnownNoEffect | attempt:=attempt+1; status:=Running; result/producer/verifier result:=None; timer:=Disarmed; retry ready:=FALSE; effect:=None |
| Cancel | H, not cancelled | cancelled:=TRUE; status:=Cancelled; clear retry ready; disarm timer; retain effect state and reconciliation obligations |
| PrepareEffect | status Running, matching attempt, effect None, durable outbox has space | effect:=Prepared with captured fence and stable token; second event enqueues that token exactly once |
| MarkDispatch | effect Prepared, matching captured fields and current owner; token is sole matching outbox item | effect:=InFlight; remove matching outbox item; permits one subsequent external dispatch observation |
| ObserveEffect(outcome) | effect InFlight or Unknown, matching token | Success sets Succeeded; KnownNoEffect sets KnownNoEffect; Unknown sets Unknown; never changes cancelled flag |
| ReconcileEffect(outcome) | H, effect Unknown or InFlight, evidence token exact; outcome Success or KnownNoEffect | set corresponding effect state; no automatic resend, no task resurrection |

For every successful event, ordinal and tail are advanced exactly once. Other canonical fields are unchanged unless listed. Every accepted fresh command adds one immutable receipt after its complete batch. Rejected commands change none of K, Log, outbox or command index. In this finite candidate, MarkDispatch records intent before the modeled external action. A crash between intent and the external action becomes epistemically unresolved; canonical InFlight remains until an explicit observation or reconciliation event changes it. It is never safe permission to retry. Exactly once external execution is not claimed.

### Derive work packet

DeriveWorkPacket(K, w) returns a refusal if w is not the current owner, the task is not Running, the state is paused or cancelled, or an effect is unresolved for a request to execute that effect. Otherwise it returns the exact map of schema epoch, aggregate, task, worker, goal, plan, lease, writer, pause epoch, attempt, expected ordinal, expected state digest, permitted capability, and effect token or None. It contains no clock, random value, provider identity, host path or renderer state. Packet digest is over every field except the digest itself. Derivation does not enqueue, commit or dispatch anything. Packet validity is rechecked at use; being derivable once is not a perpetual authorization.

### Exact integrated action relation

Next is the disjunction of the following named actions. Every action assigns every variable, using UNCHANGED for unmentioned fields. Baseline safety is Init /\ [][Next]_vars; bracketed stuttering is intentional. The environment may indefinitely stop supplying input, delay a reply, lose an acknowledgment or crash, so safety requires no fairness.

| Action | Enabling condition | Update and observable boundary |
|---|---|---|
| Enqueue(c) | Inbox length<2 and finite c domain | Append c to Inbox only |
| DecodeHead | not crashed, not RecoveryNeeded, Pending=None, Inbox nonempty | Remove head; decode; refusal updates VolatileReply and Obs only; success stores decoded pending record |
| AdmitPending | pending decoded, not RecoveryNeeded | Compute Admit; refusal/cached success yields reply and clears Pending; fresh success stores batch, prestate ordinal/digest and writer epoch |
| PrepareAppend | pending admitted | Compute full Reduce result and receipt in private Pending; no committed change |
| CommitAppend | pending prepared; snapshot ordinal/digest/writer still current; batch fits cap | Atomically append full batch, publish K plus receipt and outbox, clear Pending, publish success receipt; only a fresh MarkDispatch commit creates volatile DispatchPermit=current token; record full pre/post boundary in Obs |
| CommitRejectStale | pending prepared; snapshot or writer no longer current | Clear Pending; publish expected state or writer fence refusal; no committed change |
| ControlCommit(c) | not crashed, not RecoveryNeeded; H control command admissible and batch fits | Same atomic append rule immediately, independent of a worker Pending; lets PAUSE or amendment win a race |
| Derive(w) | not crashed, not RecoveryNeeded | Publish pure packet/refusal observation; canonical state unchanged |
| QueueDelivery(packet) | delivery queue length<2 | Append an already observed packet; canonical state unchanged |
| Deliver(i) | delivery queue nonempty | Remove arbitrary indexed packet to permit reordering; record delivery only; use still needs current fences |
| Dispatch(token) | not crashed, not RecoveryNeeded, DispatchPermit equals matching current InFlight token, token not previously dispatched; all captured fences still equal, not paused/cancelled | Consume DispatchPermit to None before the modeled external boundary and append actual dispatch observation to Issued and Obs; no invented external result |
| ObserveExternal(outcome) | current token was dispatched | Enqueue corresponding observation command or drop observation; external outcome remains an assumption |
| Crash | not crashed | Set Crashed and RecoveryNeeded TRUE; clear DispatchPermit; discard Inbox, Pending, VolatileReply and DeliveryQueue; retain committed K/Log/outbox/receipts; unresolved InFlight does not become Prepared |
| Recover | crashed | Set not crashed; start target replay from Log; RecoveryNeeded stays TRUE and DispatchPermit stays None; replay never recreates a permit |
| BeginReplay(input) | replay Idle or Done or Refused | Snapshot finite input, set cursor 0 and independent genesis, status Running |
| ReplayOne | replay Running and more input | Target RReplay validates/applies next record; the immutable reference monitor checks that result; if invalid set Refused and keep last valid replay state/cursor; otherwise advance cursor |
| FinishReplay | replay Running and cursor=input length | Set Done; clear RecoveryNeeded only for exact full committed Log with reference validity/canonical parity; never recreate DispatchPermit |
| ProjectOne | ProjectionCursor<Len(Log) | Target RProject interprets one event's public semantic fields; immutable reference projection checks the result; advance projection cursor |
| ObserveMonitor | always | Recompute current independent history assertions and latest boundary obligations; does not modify canonical state |

The independent monitors are updated on every committed or externally observed action, not merely on a schedulable ObserveMonitor action. ObserveMonitor is redundant diagnostic exposure, so a scheduler cannot hide a violation by never selecting it. Replay and projection can lag; parity is asserted only when their cursor equals the committed ordinal and their input identity equals that log. Latest boundary evidence is latched until its predicate has been evaluated within the same state transition.

Pending snapshot revalidation is essential. Rechecking only at AdmitPending allows a PAUSE or lease replacement between admission and commit. A storage writer lock is not an authority grant. The modeling of ControlCommit supplies that interleaving without pretending there are two authorized durable writers.

## 5 Seventeen invariants and independent monitors

The formulas below are the candidate invariant expressions. They are evaluated as state predicates over the current canonical variables and latched boundary observations. For action properties, Obs contains the old and new values from the just completed transition. Initially its action is Init and action specific implications are vacuously true. This conversion must not discard intermediate visible states. AtomicAppend is checked at every published boundary, including any boundary introduced by a mutant.

RefState(L) is the unique state satisfying the independently authored reference event equations over L, including the command receipt and outbox rules. RefValid(L) means every event, transaction boundary, schema, command binding, ordinal, digest and semantic precondition is valid. RefProject(L) interprets only the declared projection fields, independently of the implementation projection. FenceEqual(p, K) compares aggregate, task, goal, plan, worker owner, lease, writer and pause epoch; it also requires a valid attempt and not paused or cancelled. Canon(K) excludes digest caches and projections but retains all canonical authority, task, command and effect data.

| Invariant | Candidate expression | Required independent evidence |
|---|---|---|
| TypeOK | K in StateDomain /\ Log in BoundedEventSeq /\ Inbox and DeliveryQueue in bounded sequences /\ all cursors and tagged results in declared domains | Structural validator over every variable; do not use implementation decoder as the validator |
| ChainIntegrity | For each i in 1..Len(Log): Log[i].ordinal=i, aggregate=1, prev=Genesis if i=1 else digest(Log[i-1]), and digest=DigestOf(event, Body(Log[i])) | Full committed event bytes/abstract bodies; independent digest preimage constructor |
| AtomicAppend | On each visible mutation, there exists one admitted whole batch B with newLog=oldLog concatenated B, newK=RefState(newLog), and receipt/outbox changes exactly those of B; otherwise all four are unchanged | Latched publication snapshots of log, state, receipts and outbox; split append cannot be hidden as stuttering |
| CommandIdempotence | Each accepted id binds one command digest and one receipt; equal repeated id/digest yields that receipt and no log delta; unequal digest is refused with code 5 and no canonical delta | Independent command ledger keyed by id, retained old receipt and old/new ordinal |
| AuthorityScope | Every fresh accepted command satisfies all six authority dimensions and the writer fence in its admission and commit contexts | Original command and actual caller, capability, full contexts; no reducer generated authorization Boolean accepted as evidence |
| LeaseFence | Every committed worker mutation and actual dispatch has lease=current lease and actor=current owner at the corresponding boundary | Captured packet, admission context, commit context and dispatch observation, not just current state |
| AmendmentFence | Each worker mutation or dispatch uses current goal and plan; a change invalidates older outstanding work without reviving a cancelled task | History of goal/plan amendments and packet fields before hiding |
| PauseSafety | Once a Pause event commits, no fresh Start/Submit/Retry/PrepareEffect/MarkDispatch or external Dispatch occurs until Resume; all subsequently used work has current pause epoch | Pause/Resume committed ordinals plus actual dispatch observations; process stop is not inferred |
| RetrySafety | Every increment of attempt is exactly +1, at most 2, follows Failed plus matching Fired timer, and begins with no unresolved effect; all attempt scoped values are reset | Prior task, timer and effect state independently reconstructed |
| CancelNoResurrection | Once cancelled TRUE, it remains TRUE and status remains Cancelled; no new work/effect/result acceptance follows; effect truth recording is permitted | Monotone cancellation history and event kind specific allowed updates |
| EffectSafety | Every actual dispatch has one prior committed preparation and dispatch intent, a fresh volatile permit, exact token and current fences; a token appears at most once in Issued; a canonical known outcome requires a matching observed/reconciled outcome for that token | Durable preparation/outbox history and adapter dispatch observations; not provider claims alone |
| VerifierSafety | Done implies a matching submitted value/attempt and accepted designated verifier distinct from producer | Original producer identity, verifier identity, result binding and attempt; never a precomputed passed flag |
| ReplayDeterminism | If replay is Done over the committed Log, Canon(ReplayState)=Canon(K)=Canon(RefState(Log)); replay result is a function only of genesis and exact ordered input | Separate ReplayState and ReplayCursor, independent reference equations, a second invocation or functional determinism check for code |
| ReplayFailClosed | If next input is invalid, replay status=Refused at first bad index, cursor and state stay at the valid prefix, and no recovery admission or dispatch is enabled | Corrupted input retained; independent first error index; explicit recovery readiness latch |
| ProjectionParity | If ProjectionCursor=Len(Log), ProjectionState=RefProject(Log); projection identity binds the same aggregate, cursor and event tail | Independent projection state and cursor; UI/rendered equality does not count |
| FlowBound | Len(Inbox)<=2 /\ Len(DeliveryQueue)<=2 /\ Len(K.outbox)<=2 and all reservations count before enqueue | Actual queues plus pending capacity reservations; never count only delivered entries |
| NoBlindEffectReplay | Recovery/replay produces no external Dispatch; Unknown or InFlight effects cannot return to Prepared or be retried without matching reconciliation proving KnownNoEffect | Issued sequence, recovery latch, effect transitions and explicit evidence token |

Reference state and projection monitors must have observably distinct storage. Defining ReplayState to be K or RefProject to be the implementation projector is an immediate specification rejection. However, independently authored monitors can still share a mistaken requirement. This report requires cross review against the invariant statements, structural Alloy cases and byte vectors; it does not claim that authorship independence eliminates common specification error.

RefProject is fixed for this candidate as the tuple (aggregate, ordinal, tail, task status, goal, plan, lease, owner, attempt, paused, pause epoch, cancelled, result value, verifier result, effect status, timer status). This is a test projection, not a chosen user interface or production materialized view. Projection digest binds this tuple under the separate projection domain. An omitted status or epoch must fail parity even if a rendered screen would look the same.

### Fairness scope

Safety configuration has no WF or SF condition. Enqueue, crash, control commands, delivery, external completion and reconciliation are unfair adversarial environment choices. Do not assume eventual provider response, eventual Resume, eventual disk recovery, eventual verification, or timely human action merely to obtain a liveness pass.

A separate diagnostic LiveDrain configuration permits the explicitly stated assumptions: after a designated stable suffix, no Crash occurs; no further control command invalidates the active work; a bounded input queue receives no further entries; a recovery input is valid; and enough event capacity remains. Under those assumptions only, add WF_vars(DecodeHead), WF_vars(AdmitPending), WF_vars(PrepareAppend), WF_vars(CommitAppend \/ CommitRejectStale), WF_vars(ReplayOne \/ FinishReplay), and WF_vars(ProjectOne). The property is that each already enqueued command receives a success, cached receipt or refusal, and each begun finite valid replay terminates. No strong fairness is proposed. WF cannot require an action disabled by the event cap to occur. Liveness claims are not kernel admission hard floors until independently approved and exercised under their explicit environmental premises. [S1, S3]

Every liveness run disables symmetry and records all fairness formulas. The first safety run also disables symmetry. Any later state reduction needs a separate soundness argument and an unreduced cross check; TLC does not certify the soundness of a user supplied symmetry declaration. [S13]

### Recovery readiness and dispatch token clarification

RecoveryNeeded is the Boolean already included in Init and the action inventory, initially FALSE, set TRUE by Crash and cleared only by FinishReplay when input equals the complete committed Log, reference validation succeeds and canonical state parity holds. AdmitPending, ControlCommit, Derive and Dispatch require not RecoveryNeeded. Effect reconciliation remains available after healthy replay, but Unknown and InFlight are not resend permission. DispatchPermit is a volatile one shot token created only by a fresh MarkDispatch commit, consumed by Dispatch and erased by Crash. Cached receipt reuse and replay never create it. Consequently a crash before actual dispatch conservatively loses permission even if the durable intent is InFlight; reconciliation is required. This intentionally sacrifices availability rather than infer that an effect did not occur. A token is DigestOf(effecttoken, (aggregate, effect id, attempt, issuing command id)); the byte profile gives effecttoken its own domain. The dispatch observation guard also checks that this token has not previously appeared in Issued. Issued is an environment observation and is not itself assumed durable; recovery safety must therefore rest on canonical effect uncertainty, not only on a remembered Issued set.

## 6 Thirty six candidate mutations

These are thirty six exact proposed fault sites, not a recovered historical list and not classifications produced by a run. The names explicitly supplied in the handoff are preserved. If the local DS22 registry uses different sites, reconcile it before assigning historical IDs. A mutation is one controlled semantic edit; deleting a named predicate at its single definition may affect its callers, but cannot secretly change a monitor, scope or environment.

R means a baseline reachable prefix reaches the mutated decision point. A distinguishing suffix may then take a mutant only transition. NE means a witness distinguishes observable behavior or a declared invariant; it is not inferred from different syntax. A prospective trigger in the table is a search target, not a demonstrated reachable state. Each row currently has classification PENDING and no receipt. Mandatory means the registry requires a disposition for that row. It does not mean an unreachable or equivalent mutation is counted as killed.

| ID and mutation | Exact changed behavior | Prospective distinguishing trigger and checked obligation |
|---|---|---|
| M01 ATOMIC_SPLIT | Replace one CommitAppend publication for a two event PrepareEffect batch with publication of first event/state, then second event/outbox/receipt | Observe after first publication; AtomicAppend must reject missing second event and outbox/receipt |
| M02 CHAIN_PREV_DELETE | Remove previous digest equality from Reduce event validation | Valid prefix plus next event with wrong predecessor; ChainIntegrity or ReplayFailClosed |
| M03 CHAIN_ORDINAL_WEAKEN | Replace next ordinal=old+1 with next ordinal>=old+1 | Gap from 1 to 3 with otherwise valid body; ChainIntegrity |
| M04 COMMAND_DEDUP_DELETE | Skip existing command id lookup in Admit | Reissue exact accepted command with its original expected state; either duplicate append or different refusal distinguishes CommandIdempotence |
| M05 COMMAND_BODY_HIDE | Compare only command id, not its digest, on receipt reuse | Same id, changed kind or payload; code 5 required; CommandIdempotence |
| M06 EXPECTED_STATE_DELETE | Remove complete ordinal/digest Expected predicate at fresh admission | Fresh id with stale expected state and current fences; atomic stale admission must be refused |
| M07 AUTH_DIM_DELETE aggregate | Remove aggregate target equality only from authorization predicate | H control command directed at different aggregate atom; AuthorityScope; out of domain target is a decoder valid foreign id, not a second modeled aggregate |
| M08 AUTH_DIM_DELETE task | Remove task target equality only | Worker command with foreign task id, otherwise current; AuthorityScope |
| M09 AUTH_DIM_DELETE goal | Remove current goal equality at fresh admission | Fresh H command with previous goal, current expected state; AuthorityScope and AmendmentFence |
| M10 AUTH_DIM_DELETE plan | Remove current plan equality at fresh admission | Fresh H command with previous plan, current expected state; AuthorityScope and AmendmentFence |
| M11 AUTH_DIM_DELETE principal | Remove command kind principal role check only | X issues control command with otherwise correct scope/capability; AuthorityScope |
| M12 AUTH_DIM_DELETE capability | Remove exact command capability check only | Authorized principal uses another kind capability; AuthorityScope |
| M13 LEASE_EPOCH_WEAKEN | Replace command lease=current by command lease<=current | Old worker epoch with current expected state after replacement; LeaseFence |
| M14 LEASE_OWNER_DELETE | Remove actor=current owner, retaining actor in Workers | Nonowner worker supplies current numeric epoch; LeaseFence |
| M15 AMENDMENT_FENCE_DELETE | Remove goal and plan comparison at actual Dispatch only | Prepare/intent, then AmendPlan or AdvanceGoal, then dispatch; AmendmentFence |
| M16 PAUSE_GUARD_DELETE | Remove paused rejection from fresh worker admission only | Current pause epoch supplied while paused; PauseSafety |
| M17 PAUSE_REORDER | Publish successful Pause receipt before publishing paused/epoch state, exposing an intermediate boundary | Attempt fresh dispatch after receipt and before state update; AtomicAppend and PauseSafety |
| M18 PAUSE_EPOCH_HIDE | Exclude pause epoch from packet use validation while retaining paused check | Packet from before Pause used after Resume; PauseSafety |
| M19 RETRY_ATTEMPT_WEAKEN | Replace attempt<2 by attempt<=2 and permit next value 3 | Failed attempt 2 with fired matching timer; RetrySafety and TypeOK |
| M20 RETRY_TIMER_DELETE | Remove fired matching timer prerequisite from Retry | Failed attempt 1 with disarmed timer; RetrySafety |
| M21 CANCEL_RESURRECT | Retry writes cancelled FALSE and Running even when cancelled | Cancelled failed work with previously fired timer; CancelNoResurrection; reachability must account for timer clearing |
| M22 EFFECT_TOKEN_HIDE | Match dispatch intent by effect id only, omitting attempt/command token binding | Reconcile KnownNoEffect, retry, use prior attempt token for current effect; EffectSafety |
| M23 EFFECT_UNKNOWN_SUCCESS | Map Unknown observation to Succeeded | Lost or uncertain acknowledgment; independent observed outcome disagrees with canonical effect truth |
| M24 EFFECT_PREPARE_OMIT | Allow MarkDispatch from effect None and synthesize intent without preparation | Running task issues MarkDispatch directly; EffectSafety |
| M25 BLIND_EFFECT_REPLAY | Recovery changes InFlight or Unknown to Prepared and requeues the token | Crash after intent/dispatch before known outcome; NoBlindEffectReplay |
| M26 VERIFIER_SELF_ALLOW | Remove verifier principal differs from producer | W2 produces and then verifies same result; VerifierSafety |
| M27 VERIFIER_RESULT_UNBOUND | Remove submitted value and attempt equality from Verify | W2 verifies R2 after W1 submits R1, or stale attempt; VerifierSafety |
| M28 REPLAY_UNKNOWN_SKIP | Treat unknown event schema/kind as a successful no op and advance cursor | Known valid prefix, unknown event, valid successor; ReplayFailClosed |
| M29 REPLAY_CHAIN_SKIP | Replay path ignores predecessor and ordinal checks, while live Reduce keeps them | Reordered or omitted committed event; ReplayFailClosed and ReplayDeterminism |
| M30 PROJECTION_FIELD_HIDE | Implementation projector omits paused and pause epoch from its result | Pause commit with projection caught up; ProjectionParity; independent projector unchanged |
| M31 FLOW_OFF_BY_ONE | Replace queue length<2 with length<=2 at Enqueue | Two occupied slots followed by third input; FlowBound |
| M32 PACKET_LEASE_HIDE | DeriveWorkPacket omits lease field from emitted packet | Running owner derives packet; exact schema and LeaseFence packet contract fail |
| M33 DIGEST_DOMAIN_OMIT | Remove tag from DigestOf or type string from concrete preimage | Equal canonical value used under command and packet domains; domain vector must differ |
| M34 COMMIT_SNAPSHOT_DELETE | Remove ordinal/digest snapshot revalidation at CommitAppend | Admit/prepare worker command, commit Pause or amendment, then old proposal commits; AtomicAppend, PauseSafety |
| M35 WRITER_FENCE_DELETE | Remove writer epoch revalidation at durable mutation boundary, leaving other snapshot validation intact | Requires separately modeled authority epoch advance without ordinary log snapshot change or an independent adapter boundary; may be equivalent in this candidate; must be justified rather than claimed killed |
| M36 REDUCE_BATCH_REORDER | Reverse a two event batch before applying semantic updates while retaining original log order | PrepareEffect then OutboxEnqueued; independent RefState disagrees or invalid semantic prefix is accepted; ReplayDeterminism and AtomicAppend |

The finite external identifier domain adds ForeignAggregate and ForeignTask only as command target atoms. They are not state carrying aggregates/tasks and therefore do not expand the given integrated entity bound. Parser schemas accept syntactically valid foreign identifiers so an authorization fault can actually be reached. If a decoder rejects all foreign identifiers before authorization, M07/M08 are unreachable under that decoder partition and require explicit justification, not a coverage claim.

M21 is intentionally a potentially overguarded mutation: Cancel clears the timer and retry ready state, so deleting only a cancellation guard may not expose a retry. The local agent must either produce a real trigger for the specified semantic edit, prove it observationally equivalent within the bounds, or propose a replacement with Owner approval. It may not quietly weaken unrelated guards to make the mutation killable. M35 similarly exposes a modeling seam: writer changes are canonical events here, so ordinal/digest revalidation may subsume a writer only deletion. The correct answer can be bounded equivalence, followed by a separate adapter mutation whose independent authority epoch is explicitly modeled. The handoff's requirement for reachable non equivalent faults cannot be met by pretending all candidate rows already satisfy it.

### Classification algorithm and receipts

Each mutant has exactly one final disposition: KILLED, SURVIVED_REACHABLE_NONEQUIVALENT, EQUIVALENT_WITHIN_BOUND, UNREACHABLE_WITHIN_BOUND, or INCONCLUSIVE. PENDING is a pre execution state only. A syntax error, evaluator exception, resource exhaustion, missing invariant, missing field, aborted run, unreviewed scope reduction or failed artifact capture is INCONCLUSIVE, not a kill.

Reachability is shown with a baseline prefix and a guard exposure predicate that names the altered site and gives the operands. To establish NE, supply either an observation difference between baseline and mutant from a common prefix, or a mutant trace violating an independently stated invariant while the baseline continuation refuses or preserves it. Equivalent means equality of the declared observation relation for all reachable states/transitions within the exact finite model, supported by a checked product construction or a reviewed exhaustive relation proof. Unreachable means a complete baseline reachability check cannot reach the site with its activation condition, supported by a named exposure property and explored scope. Neither claim generalizes outside the bound.

A kill receipt is a canonical structured record containing: receipt schema epoch; mutant id; baseline and mutant source digests; exact one site semantic diff; model/config/monitor/checker/runtime/container digests; source citation snapshot digests; complete constants and fairness; invariant id; first divergence index; baseline prefix; full mutant counterexample; baseline response to the same external sequence; minimized counterexample; minimization method; guard exposure state; event and command ordinal mapping; interpreter version; original TLC output and exit status; independent reviewer identity and decision. Artifact identity fields may not be null in an accepted receipt. Unavailable evidence makes it incomplete.

Minimize first by number of committed events, then external input actions, then other modeled steps, then lexicographic input encoding, preserving guard activation, divergence and invariant failure. This is a deterministic minimization objective, not a claim to have found a globally minimal trace unless exhaustive minimality evidence is supplied. Keep the unminimized trace as well. A delta debugging local minimum is labeled as such.

The acceptance denominator is 36 of 36 mandatory rows classified with retained evidence. Separately report K/RNE, where RNE is the number proved reachable and non equivalent and K is those killed. Acceptance requires K=RNE, no survivor and no inconclusive row. Equivalent/unreachable rows contribute to the classification denominator only, never the kill numerator. If the intended historical requirement is 36 reachable non equivalent mutants, candidate substitutions need explicit acceptance until RNE=36; relabeling an equivalent row does not satisfy it. A passing baseline is not coverage.

## 7 Binary test record and canonical profile

CAND RCV1 20261001 is the candidate corpus/schema name. A released literal corpus must add a content digest and immutable revision. The name alone identifies no reviewed bytes. RCV1 is a test container, never a negotiated broker protocol, storage log format or product default.

### Frame layout

| Offset | Width | Value and rule |
|---|---|---|
| 0 | 4 bytes | ASCII RCV1, hex 52 43 56 31 |
| 4 | 2 bytes | Unsigned big endian frame version 1, hex 00 01 |
| 6 | 2 bytes | Flags 0, hex 00 00; unknown flags rejected |
| 8 | 4 bytes | Unsigned big endian payload length N |
| 12 | N bytes | Exactly one deterministic CBOR map under the profile below |
| 12+N | 32 bytes | SHA-256 of all 12+N preceding bytes, raw digest bytes |

Total size is 44+N. The harness safety cap is N<=16, 777, 216, nesting depth<=64, and at most 1, 048, 576 total decoded items, with map keys and values each counted. These are proposed test harness protection limits, not production capacity choices. The frame length must be checked without integer overflow before allocation. End of file mid header, payload or digest is truncation. A file contains a sequence of complete records; parsing advances by exact frame length, never by scanning for magic inside a damaged payload. A corrupt record fails the corpus load and does not resynchronize to a later magic byte.

Frame errors are FRAME_BAD_MAGIC, FRAME_VERSION, FRAME_FLAGS, FRAME_LENGTH, FRAME_TRUNCATED, FRAME_CHECKSUM and FRAME_PAYLOAD. They are harness failures separate from the eighteen kernel refusal codes. A deliberately malformed tested frame is embedded as raw bytes inside an otherwise valid vector record. It must not corrupt the container that delivers the test.

For an empty map payload, the exact prechecksum prefix is 52 43 56 31 00 01 00 00 00 00 00 01 a0. The trailing 32 bytes are defined by SHA-256 of that thirteen byte string. This is an illustrative frame primitive, not a valid full vector record because required record fields are absent. No evaluated checksum is claimed in this report.

### Deterministic CBOR profile

Permitted semantic types are unsigned integers 0..2^64−1, negative integers−2^63..−1, byte strings, valid UTF-8 text strings, arrays, maps with unsigned integer keys only, FALSE, TRUE and null. Schema specific ranges may be narrower. No floats, tags, undefined, other simple values, indefinite lengths or duplicate keys are permitted. All lengths and integers use the shortest legal CBOR head. For these unsigned integer map keys, ascending numeric order also supplies deterministic encoded byte order; do not generalize that equivalence to arbitrary key types. [S8]

Text is strictly valid UTF-8 with no surrogate scalar values and no normalization. A text field containing precomposed e acute differs from one containing e plus combining acute unless the application schema explicitly states an equivalence; this profile states none. Byte strings are opaque and may contain any octets, including malformed nested inputs. The profile requires exact end of item: trailing bytes are invalid. Before object/map collapse, detect repeated keys. A reencode comparison can supplement structural validation but cannot recover duplicates already discarded by a generic decoder.

The profile gives one canonical byte representation per permitted typed value. It does not identify integers with floats, text with byte strings, absent fields with null, or booleans with integers. A finite input cap is enforced before recursing into nested data. CDDL may document these shapes, but custom ordered byte validation is still required. [S10]

### Corpus record map

Every record has exactly keys 0 through 8. Key 0 is corpus schema epoch 1. Key 1 is a positive integer vector id. Key 2 is layer:0 CBOR primitives, 1 semantic kernel test representation, 2 replay, 3 JCS compatibility, 4 frame. Key 3 is operation:0 decode, 1 admit, 2 reduce, 3derive_work_packet, 4 replay harness, 5 canonicalizer, 6 frame parser. Key 4 is raw input bytes. Key 5 is prestate bytes or null. Key 6 is an ordered array of auxiliary byte strings. Key 7 is the expected result map. Key 8 is a stable purpose string, excluded from normative semantic output comparison but included in the frame checksum.

Expected result has exactly keys 0 status (0 success or 1 refusal), 1 ordered array of exact output byte strings, and 2 refusal map or null. The distinction between no output [] and one empty byte string [h''] is significant. Success requires refusal=null. Refusal requires outputs=[] unless the operation is replay, where a separately typed valid prefix checkpoint is an auxiliary expected observation; it is never an admitted success state. The normative local corpus must make that checkpoint an explicit auxiliary field of its replay input/result schema and bump the schema if adding a new field; this report's baseline refusal output remains [].

A manifest gives profile name, schema epoch, exact vector count, sorted vector ids, SHA-256 of each complete framed record, SHA-256 of ordered concatenated record bytes, SHA-256 of this candidate specification revision, and independence/review attestations. Duplicate or missing ids, unexpected files or changed bytes fail loading. The manifest itself uses the same deterministic CBOR profile and a separately domain tagged manifest digest. Cryptographic signing is optional separate provenance; the checksum is not a signature.

## 8 Logical schemas and typed digest domains

These schemas are a language neutral conformance representation of logical values. They do not select production serialization. A production JCS implementation must supply an explicitly approved mapping from its fields and bytes to this representation, while retaining separate JCS vectors for its actual byte contract. Never compare a JCS byte string to a CBOR byte string as though different encodings were an implementation failure. Byte equality is required within the same declared profile and schema identity.

### Canonical object fields

Command map keys are:0 schema epoch; 1 command id; 2 kind; 3 aggregate; 4 task; 5principal; 6 capability; 7 goal epoch; 8 plan revision; 9 lease epoch; 10 writer epoch; 11 pause epoch; 12 attempt; 13 expected ordinal; 14 expected state digest; 15 payload. All keys are present. A nonapplicable value is explicitly null, never omitted. Control commands still bind all current scope and epoch fields; their lease owner restriction is inapplicable, not their schema. Payload is a kind specific unsigned key map with no unknown keys.

Kinds 0..17 are GrantLease, RevokeLease, AmendPlan, AdvanceGoal, AdvanceWriter, Pause, Resume, Start, Submit, Verify, ArmTimer, FireTimer, Retry, Cancel, PrepareEffect, MarkDispatch, ObserveEffect, ReconcileEffect. Payload is {} except: GrantLease {0 worker}; Submit {0 result value, 1 outcome success 0/failure 1}; Verify {0 result value}; PrepareEffect {0 effect id}; MarkDispatch {0 effect token}; ObserveEffect/ReconcileEffect {0 effect token, 1 outcome Success0/KnownNoEffect 1/Unknown 2}. Reconcile rejects outcome 2. Event kinds use command kinds except PrepareEffect emits event kind 18 EffectPrepared and 19 OutboxEnqueued. This distinction is encoded, not inferred from array position.

State map keys are:0 schema epoch; 1 aggregate; 2 ordinal; 3 event tail digest; 4 goal; 5 plan; 6 lease; 7 writer; 8 pause epoch; 9 paused; 10 task status; 11 owner; 12 attempt; 13 effect record; 14 timer record; 15 result record; 16 cancelled; 17 command receipt array; 18 outbox array; 19 retry ready. Task status codes 0..6 are Ready, Running, Submitted, Failed, Done, Cancelled and ReservedInvalid; code 6 is decoder rejected in this epoch. Principals are H = 0, W1 = 1, W2 = 2, X = 3, None=null. Values R1 and R2 are byte strings h'01' and h'02'. Capability code equals authorized command kind; capability equality is exact, not an ordering.

Effect record keys 0 status (None 0, Prepared 1, InFlight 2, Unknown 3, Succeeded 4, KnownNoEffect 5), 1 effect id, 2 attempt, 3 goal, 4 plan, 5 lease, 6 pause epoch, 7 issuing command id, 8 token, 9 writer. For None all fields 1..9 are null. Timer record keys 0 status (Disarmed 0, Armed 1, Fired 2), 1 attempt, 2 goal, 3 plan, 4 pause epoch; Disarmed uses null for 1..4. Result record keys 0 value, 1 producer, 2 verified value, 3 attempt, 4 goal, 5 plan, 6 producer lease, all initially null. Submit success captures 3..6; Retry resets all fields. Verify requires stored attempt/goal/plan to match current state and supplied result; producer lease is retained as provenance, while verifier authorization uses current numeric lease without requiring verifier=owner. Receipt entries are ordered ascending command id, with keys 0 id, 1 command digest, 2 first ordinal, 3 last ordinal, 4 last event digest, 5 result class, 6 result bytes. Outbox entries are ordered by first enqueue ordinal and contain effect token and full captured fence. Semantic set membership never licenses unordered bytes.

Event body keys 0 schema epoch, 1 aggregate, 2 ordinal, 3 previous event digest, 4 command digest, 5 event kind, 6 payload, 7 writer epoch. Stored event adds key 8 event digest. Payload wraps the original command map at key 0 and event specific data at key 1; for OutboxEnqueued the data is the complete token/fence record. Every replay validator checks that wrapped command digest equals key 4 and that batch events share the same command binding. Transaction batch metadata is kept in a separate candidate batch map {0 command id, 1 ordered events, 2 receipt}; the atomic store oracle must retain that boundary even if its physical format uses separate rows.

Packet map keys 0 schema epoch, 1 aggregate, 2 task, 3 worker, 4 goal, 5 plan, 6 lease, 7 writer, 8 pause epoch, 9 attempt, 10 expected ordinal, 11 expected state digest, 12 capability, 13 effect token or null, 14 packet digest. Fields 0..13 define the packet digest preimage. Projection map uses the exact sixteen field tuple declared in section 5, encoded as keys 0..15 in that order. Different projection schemas require different epochs or profile identity.

### Digest preimages

Let C(x) be exact deterministic CBOR bytes for x. Let U16/U64 be unsigned big endian fixed width integer encodings. For type t and schema epoch e, define:

D(t, e, x) = SHA-256(ASCII("RCV1/") || ASCII(t) || 00 || U16(e) || U64(length(C(x))) || C(x))

The complete permitted domain strings are state, event, packet, command, projection, effecttoken and manifest. They are lowercase ASCII with no terminator inside the string; the single 00 delimiter follows the type. Epoch is 1 for this candidate. Output is raw 32 bytes; textual display is lowercase 64 digit hex only in reports/manifests that explicitly request text. Domain and length are included, avoiding ambiguous concatenation. A stored digest field is removed only from its own object preimage. No other data may be excluded without a schema change.

State excludes cached state/projection digests and volatile queues but includes the command receipt index, durable outbox, complete authority state and effect uncertainty. Event hashes its body excluding key 8. Command hashes all sixteen command fields. Packet hashes keys 0..13. Projection has a distinct projection domain and binds aggregate, ordinal and event tail. Effecttoken hashes [aggregate, effect id, attempt, issuing command id]. Manifest hashes its complete content excluding its own digest field. Genesis previous event digest is 32 zero bytes; the first event ordinal is 1. The state genesis digest is D(state, 1, genesis state), not 32 zero bytes.

These are exact proposed preimage rules, not measured digest values and not a production hashing decision. Cross profile digests are not equal merely because logical meaning agrees. If JCS becomes the accepted semantic byte profile, it needs a differently named digest profile or domain/version and its own vectors; silently replacing C(x) by JCS is forbidden. Hash algorithm conformance must include trusted SHA-256 known answer tests before application vectors, but passing those tests is not a proof of collision resistance. [S11]

## 9 Stable refusal taxonomy

All code allocations here are candidate completions because only endpoint names and the range0..17 were supplied. Reconcile historical code assignments before public or persistent use. Codes never change meaning within schema epoch 1. A new refusal needs a new code/epoch policy; reusing an old code for an unrelated condition is forbidden.

A refusal is (code, structured_detail), encoded as {0:code, 1:detail}. Detail is exactly {0:schema_epoch, 1:field_path, 2:stable_detail_enum, 3:expected, 4:observed}. Schema epoch is 1. Field path is an array of unsigned map keys, integer array indices or explicitly standardized text labels; [] denotes the entire input. Expected and observed are null or a scalar allowed by the profile. In synthetic fixtures they must be exact. In a real protocol, sensitive details may require redaction by a separately approved disclosure schema; exception strings, locale and stack traces never enter the refusal bytes.

| Code | Name | Required use and primary detail |
|---|---|---|
| 0 | MALFORMED | Truncated CBOR/JSON, impossible head, invalid UTF-8, trailing bytes; first structural error |
| 1 | NONCANONICAL | Valid typed value with nonshortest encoding, map order violation or duplicate key rejected before collapse |
| 2 | UNSUPPORTED_SCHEMA | Unknown schema epoch; no permissive forward interpretation |
| 3 | UNKNOWN_KIND | Valid schema with unknown command/event kind |
| 4 | FIELD_INVALID | Missing/extra field, type/range violation, forbidden CBOR type, invalid transition or capacity |
| 5 | COMMAND_CONFLICT | Existing command id with different complete command digest |
| 6 | EXPECTED_STATE_MISMATCH | Fresh command's expected ordinal or state digest differs |
| 7 | AUTHORITY_DENIED | Aggregate/task/principal/capability/owner or writer epoch mismatch |
| 8 | GOAL_EPOCH_STALE | Fresh command goal does not equal current goal, including unsupported future value within syntax |
| 9 | PLAN_REVISION_STALE | Fresh command plan does not equal current plan |
| 10 | LEASE_EPOCH_STALE | Worker command lease differs from current lease |
| 11 | PAUSED | Fresh forbidden work while paused and pause epoch otherwise current |
| 12 | PAUSE_EPOCH_STALE | Command or packet carries another pause epoch |
| 13 | ATTEMPT_INVALID | Attempt mismatch, out of range or forbidden retry increment |
| 14 | CANCELLED | Fresh work would progress a cancelled task |
| 15 | EFFECT_UNSAFE | Missing preparation, unknown outcome, token mismatch, unsafe replay or blind retry |
| 16 | VERIFIER_INVALID | Self verification, wrong designated verifier or result/attempt binding failure at verification |
| 17 | CHAIN_MISMATCH | Event ordinal, predecessor digest, self digest, aggregate chain or transaction continuity mismatch |

Field paths for command inputs start directly with the command key. Paths for state conditions start with the literal text "state", followed by state keys; replay paths start with "events", a zero based event index and event key. These are the only standardized text path labels. Detail enums are fixed as follows.

| Code | Stable detail | Code | Stable detail |
|---|---|---|---|
| 0 | NONE | 21 | LEASE |
| 1 | TRUNCATED | 22 | OWNER |
| 2 | DUPLICATE_KEY | 23 | WRITER_EPOCH |
| 3 | NONSHORTEST | 24 | PAUSED |
| 4 | MAP_ORDER | 25 | PAUSE_EPOCH |
| 5 | BAD_UTF-8 | 26 | ATTEMPT |
| 6 | FORBIDDEN_TYPE | 27 | BAD_TRANSITION |
| 7 | MISSING_FIELD | 28 | TIMER |
| 8 | UNKNOWN_FIELD | 29 | CAPACITY |
| 9 | RANGE | 30 | CANCELLED |
| 10 | SCHEMA | 31 | EFFECT_STATE |
| 11 | KIND | 32 | EFFECT_TOKEN |
| 12 | COMMAND_DIGEST | 33 | EFFECT_OUTCOME |
| 13 | EXPECTED_ORDINAL | 34 | SELF_VERIFY |
| 14 | EXPECTED_DIGEST | 35 | RESULT_BINDING |
| 15 | AGGREGATE | 36 | CHAIN_ORDINAL |
| 16 | TASK | 37 | CHAIN_PREVIOUS |
| 17 | PRINCIPAL | 38 | CHAIN_DIGEST |
| 18 | CAPABILITY | 39 | TRAILING_BYTES |
| 19 | GOAL | 40 | DEPTH_LIMIT |
| 20 | PLAN | 41 | ITEM_LIMIT |

Unknown detail enums are rejected under epoch 1.

MALFORMED covers lexical invalidity. Duplicate keys are assigned NONCANONICAL/DUPLICATE_KEY by this application even though RFC 8949 discusses them as a validity issue; this classification is a protocol choice, not a claim about the RFC terminology. Forbidden but well formed CBOR floats/tags use FIELD_INVALID/FORBIDDEN_TYPE. JCS canonicalizer invalid NaN/Infinity input uses MALFORMED for raw JSON tokens, whereas nonfinite in memory values presented to its typed API use FIELD_INVALID/FORBIDDEN_TYPE. These two input types have different vector ids.

For multidefect inputs, structural decoding completes before admission. Within structure choose the first byte offset error; within a schema choose the lowest unsigned missing/invalid field key; within admission follow section 4. Expected ordinal mismatch precedes expected digest mismatch. Authorization aggregate, task, principal and capability are checked in that order; specific epoch checks follow. For verification, the designated verifier check is handled under VERIFIER_INVALID rather than generic principal rejection, so code 16 remains stable. Field path names the earliest decisive field. These tie breakers make refusal equality mechanical.

## 10 Minimum coverage complete vector catalog

This catalog is a proposed minimum by required coverage obligations, not a theorem that no smaller suite could work. It contains 88 named rows plus finite expansions explicitly stated below. A vector is mandatory if it is listed, and expansions are distinct manifest entries. Positive and negative controls travel together. It is language neutral because inputs, exact expected semantic values, ordered outputs and refusal tuples are fixed independently of either implementation. The literal binary corpus and evaluated digest manifest remain local execution deliverables; this report must not be represented as an already reproduced byte corpus.

### Deterministic fixture construction

Each semantic row starts from genesis unless a prefix is named. Fresh(kind, S, payload) means the command map in section 8 with the next unused positive command id, kind and payload given, all scopes/epochs/attempt and expected state taken from the named S, exact kind capability, and the actor prescribed for that kind. H is a synthetic authorized control principal, not the retired Hermes system. Worker commands use the current owner; Verify uses W2. A row saying replace(field, value) changes only that field after Fresh construction. Foreign aggregate/task are syntactically valid identifier2. Other wrong scalar is the smallest different member of its syntactic domain. Unknown schema is 2; unknown kind is 255; unknown field is 255.

Prefix G is genesis. A is Start by W1 from G. B is A followed by Submit(R1, success) by W1. F is A followed by Submit(R1, failure). T is F followed by ArmTimer then FireTimer. P is A followed by Pause. Q is P followed by Resume. L is A followed by GrantLease(W2). V is G followed by GrantLease(W2), Start and Submit(R1, success) by W2. E is A followed by PrepareEffect(1). I is E followed by MarkDispatch(current token). U is I, actual Dispatch, ObserveEffect(Unknown). N is I, actual Dispatch, ObserveEffect(KnownNoEffect), Submit(R1, failure), ArmTimer, FireTimer. These are mathematical fixture prefixes; no such trace was run here.

For accepted commands, the expected event sequence is exactly the ordered batch in section 4 with independently computed canonical bodies and digests; the expected state equals the listed field update with all other fields unchanged plus ordinal/tail/receipt changes. All outputs must be materialized as literal bytes during corpus preparation and separately reviewed. A/B stacks are prohibited from generating expected outputs. The candidate reference equations define what must be materialized; successful execution of a generator alone does not certify those bytes.

For refusal rows, canonical state, event sequence, command index, outbox and dispatch observations remain unchanged. The refusal code/detail/path must match exactly. Unless otherwise stated expected/observed contain the actual scalar operands; structural errors that have no scalar use null/null. Paths are actual map keys or [] for whole input. The detail enum table in section 9 supplies numeric values, never diagnostic prose.

### Canonical byte primitives

Rows 1..30 use layer 0 operation 5. Valid input yields exactly the same bytes, not a normalized alternative. Invalid input yields the stated refusal.

| Id | Exact bytes or finite construction | Expected result |
|---|---|---|
| 1 | 00 | Success unsigned 0 |
| 2 | 17 | Success unsigned 23 |
| 3 | 18 18 | Success unsigned 24 |
| 4 | 18 ff | Success unsigned 255 |
| 5 | 19 01 00 | Success unsigned 256 |
| 6 | 19 ff ff | Success unsigned 65535 |
| 7 | 1a 00 01 00 00 | Success unsigned 65536 |
| 8 | 1a ff ff ff ff | Success unsigned 4294967295 |
| 9 | 1b 00 00 00 01 00 00 00 00 | Success unsigned 4294967296 |
| 10 | 1b ff ff ff ff ff ff ff ff | Success unsigned maximum |
| 11 | 20 | Success negative1 |
| 12 | 3b 7f ff ff ff ff ff ff ff | Success minimum signed64 |
| 13 | 83 f4 f5 f6 | Success [FALSE, TRUE, null] |
| 14 | 42 00 ff | Success two byte string |
| 15 | 62 c3 a9 | Success precomposed text; not equal to row 16 |
| 16 | 63 65 cc 81 | Success decomposed text; no normalization |
| 17 | a2 00 01 18 18 02 | Success map {0:1, 24:2}, exact order |
| 18 | 18 00 | Refuse 1/NONSHORTEST, [] |
| 19 | a2 01 00 00 00 | Refuse 1/MAP_ORDER, [] |
| 20 | a2 00 00 00 01 | Refuse 1/DUPLICATE_KEY, [0] |
| 21 | c0 00 | Refuse 4/FORBIDDEN_TYPE, [] |
| 22 | f9 00 00; f9 80 00; f9 7c 00; f9 7e 00 | Four entries, refuse4/FORBIDDEN_TYPE, [] for float0, negative0, infinity and NaN |
| 23 | 9f ff; bf ff; 5f ff; 7f ff | Four entries, refuse4/FORBIDDEN_TYPE, [] for indefinite array/map/bytes/text |
| 24 | 61 ff | Refuse 0/BAD_UTF-8, [] |
| 25 | 1a 00 00 | Refuse 0/TRUNCATED, [] |
| 26 | 00 00 | Refuse 0/TRAILING_BYTES, [] |
| 27 | f7 | Refuse 4/FORBIDDEN_TYPE, [] for undefined |
| 28 | 65 nested one element arrays, each head81, then00 | Refuse 4/DEPTH_LIMIT at65th container; root depth1 |
| 29 | a1 61 61 00 | Refuse 4/FORBIDDEN_TYPE, [] because text map key forbidden |
| 30 | 3b ff ff ff ff ff ff ff ff | Refuse 4/RANGE, [] because negative value below signed64 minimum |

The item limit also receives two generated boundary entries: an array with1, 048, 575 zero elements (root plus elements totals1, 048, 576) succeeds if frame size cap permits; one more element refuses4/ITEM_LIMIT. These are fixtures, not permission to allocate uncontrolled memory. The producer must stream their construction and independently verify declared lengths. For depth28, sixty four containers plus the scalar are permitted; sixty five containers are rejected. Array item index paths are zero based in the byte vector profile, unlike TLA sequence indices; the trace mapper must convert explicitly.

### Semantic and trace fixtures

Rows 31..74 use layer 1 unless replay or projection is named, then layer 2. Operation is the named pure function or replay harness. Admission rows also assert subsequent reduce/packet results for accepted batches; a failure cannot be masked by skipping later outputs.

| Id | Input and prefix | Required exact assertion |
|---|---|---|
| 31 | Fresh Start at G, schema 2 | decode refuses2/SCHEMA at[0] |
| 32 | Fresh Start at G, kind 255 | decode refuses3/KIND at[2] |
| 33 | Fresh Start with field 14 removed | decode refuses4/MISSING_FIELD at[14] |
| 34 | Fresh Start with key 255:null added | decode refuses4/UNKNOWN_FIELD at[255] |
| 35 | Encode genesis canonical state | Exact canonical state bytes and D(state, 1, G); this digest is not Genesis event tail |
| 36 | Fresh Start at G | One Start event; Running/attempt 1; full receipt and derivable W1 packet |
| 37 | Replay identical accepted Start command at A | Exact cached receipt, zero events, unchanged state, no new dispatch |
| 38 | Same id as Start, payload or kind changed | Refuse5/COMMAND_DIGEST at[1] |
| 39 | Fresh Submit at A with expected ordinal0 | Refuse6/EXPECTED_ORDINAL at[13] |
| 40 | Fresh Submit at A with expected digest 32 zero bytes | Refuse6/EXPECTED_DIGEST at[14] |
| 41 | Fresh Pause at A with aggregate2 | Refuse7/AGGREGATE at[3] |
| 42 | Fresh Submit at A with task2 | Refuse7/TASK at[4] |
| 43 | Fresh Pause at A with actorX | Refuse7/PRINCIPAL at[5] |
| 44 | Fresh Pause at A with Start capability | Refuse7/CAPABILITY at[6] |
| 45 | AdvanceGoal after A; fresh Pause with goal1 | Refuse8/GOAL at[7] |
| 46 | AmendPlan after A; fresh Pause with plan1 | Refuse9/PLAN at[8] |
| 47 | Fresh Submit at L from W2 but lease 1 | Refuse10/LEASE at[9] |
| 48 | AdvanceWriter after A; fresh Pause with writer1 | Refuse7/WRITER_EPOCH at[10] |
| 49 | Fresh Submit at L from W1 with current lease 2 | Refuse7/OWNER at[5] |
| 50 | Fresh Submit at P with current pause epoch 1 | Refuse11/PAUSED at["state", 9] |
| 51 | Fresh Submit at Q with old pause epoch 0 | Refuse12/PAUSE_EPOCH at[11] |
| 52 | Admit/prepare Submit at A; ControlCommit Pause; commit old pending | Refuse6/EXPECTED_ORDINAL; no late Submit event, no post pause packet dispatch |
| 53 | A, PrepareEffect, Pause, GrantLease(W2), GrantLease(W1), Resume | Reach lease 3, pause epoch 1 and outstanding Prepared effect; old effect cannot dispatch; retain full witness |
| 54 | Fresh Retry at F before timer firing | Refuse 4/TIMER at["state", 14, 0]; unchanged attempt 1 |
| 55 | Retry from T, fail attempt 2, attempt retry again | Refuse13/ATTEMPT; no attempt 3; do not require a timer that cannot legally arm |
| 56 | Cancel at A then fresh Submit | Refuse14/CANCELLED, status remains Cancelled |
| 57 | Fresh PrepareEffect at A | Exactly EffectPrepared then OutboxEnqueued, one receipt, atomic visibility; derive never dispatches |
| 58 | MarkDispatch at E with other token | Refuse15/EFFECT_TOKEN; no intent and no dispatch |
| 59 | Fresh Retry or resend at U | Refuse15/EFFECT_STATE, preserve Unknown; test request constructed to reach effect guard after earlier checks pass |
| 60 | Crash after I/actual Dispatch; replay and recover | No new dispatch; intent remains unresolved until explicit reconciliation |
| 61 | Retry from N | New attempt 2, result/timer reset; any new effect gets a different token; old token refused |
| 62 | Verify by W2 at V | Refuse16/SELF_VERIFY; W2 is producer and designated verifier |
| 63 | Verify R1 by W2 at B | Done and verified R1; accepted once, exact duplicate returns receipt |
| 64 | Verify R2 at B | Refuse16/RESULT_BINDING, no Done |
| 65 | Replay exact Log of B then Verify | Same canonical state/receipts/outbox as live path; no side effects |
| 66 | Next event with wrong predecessor but internally recomputed self digest | Refuse17/CHAIN_PREVIOUS at[3]; valid prefix retained diagnostically |
| 67 | Next event ordinal skips one, self digest recomputed | Refuse17/CHAIN_ORDINAL at[2] |
| 68 | Valid replay prefix then event schema 2 | Refuse2/SCHEMA at first bad record, no skip or admission from partial recovery |
| 69 | Valid replay prefix then kind 255 | Refuse3/KIND; same fail closed requirement |
| 70 | Project exact Q log, then compare against projection with pause epoch removed | Correct projection bytes/digest pass; hidden field candidate fails exact parity |
| 71 | Enqueue two distinct inputs then a third | First two fit; third refuses4/CAPACITY or backpressures at the harness queue API as explicitly selected, with no third slot. Candidate selects refusal4/CAPACITY |
| 72 | Derive at A; compare full packet then packet lacking lease | Full exact bytes pass; missing lease rejected4/MISSING_FIELD before use |
| 73 | Same typed value{} under all seven digest domains | Seven distinct specified preimages and reviewed expected digests; also same domain with schema 1 versus2 |
| 74 | Reverse semantic application order of PrepareEffect two event batch | Refuse 4/BAD_TRANSITION or reference parity failure; baseline ordered batch succeeds |

For59, use U followed by Submit(failure), ArmTimer and FireTimer, then Retry, so the timer/task checks do not mask the intended effect refusal. A direct MarkDispatch from Unknown also refuses15/EFFECT_STATE independently. For55, a raw attempt 3 is a schema/attempt boundary probe; an actual legal retry command at attempt 2 must fail the attempt bound before timer validation. These precedence details prevent accidentally measuring an unrelated guard.

Exact record ids use id=1000*row+variant. A single case uses variant 1. Semicolon alternatives and listed input alternatives use variants 1..n in written order. Row73 uses domains in the section 8 order, schema 1 then2 for each domain, giving variants 1..14. Row79 uses every incomplete prefix length0..L-1 of the row 75 input frame, variant=prefix length+1. Row85 uses the 26 published Appendix B table rows in order, variants 1..26, with binary64 bit patterns carried as an8 byte input byte string under the typed JCS number probe subtype. The two item limit boundary cases are row 28 variants 100 and 101. No base record is added when a row already expands into its enumerated variants.

The following additional semantic variants are mandatory and have fixed inputs and outcomes. They are not optional coverage suggestions.

| Row and variant | Exact added construction | Required observation |
|---|---|---|
| 37 variant 100 | Reuse original Start command after P | Cached original receipt, no event or permit |
| 37 variant 101 | Reuse original Start command after L | Same cached receipt despite lease change, no new authority |
| 38 variant 100 | Original Start id with only pause token changed to 1 | Code5 COMMAND_CONFLICT before current state checks |
| 52 variant 100 | Commit Submit before ControlCommit Pause | Submit accepted before pause; no subsequent dispatch |
| 52 variant 101 | ControlCommit Pause before AdmitPending Submit | Refuse6 expected ordinal from stale command, no Submit event |
| 53 variant 100 | Prepare/MarkDispatch, AmendPlan, then Dispatch | No dispatch with captured old plan; permit does not override fence |
| 53 variant 101 | Prepare/MarkDispatch, AdvanceGoal, then Dispatch | No dispatch with captured old goal |
| 59 variant 100 | U then ReconcileEffect Success with exact token | Succeeded, no second dispatch |
| 59 variant 101 | U then ReconcileEffect KnownNoEffect with exact token | KnownNoEffect, no automatic retry or dispatch |
| 59 variant 102 | U then ReconcileEffect KnownNoEffect with wrong token | Code15 EFFECT_TOKEN, Unknown retained |
| 60 variant 100 | Crash after MarkDispatch before actual Dispatch | Permit lost; replay never creates permission to send |
| 60 variant 101 | Crash after Dispatch before observation | Same conservative uncertainty; no blind replay |
| 62 variant 100 | W1 producer prefix B, W1 attempts Verify | Code16 VERIFIER_INVALID, no Done |
| 65 variant 100 | Exact accepted log from N followed by Retry | Replay state and receipt index equal live path |
| 66 variant 100 | Correct next event except one self digest bit flipped | Code17 CHAIN_DIGEST at event key 8 |
| 66 variant 101 | Remove middle event from a three event valid log | Code17 at first broken ordinal/predecessor, no skip |
| 66 variant 102 | Duplicate first event in a valid log | Code17 at repeated ordinal |
| 66 variant 103 | Swap first two events in a valid log | Code17 at first unexpected ordinal |
| 68 variant 100 | Replay refuses unknown schema then attempt fresh Start | RecoveryNeeded remains TRUE; admission disabled, never successful |
| 70 variant 100 | Independently materialize every prefix of Q | Equal typed projections at matched cursor/tail only |
| 74 variants 100 through 104 | PrepareEffect batch: before publication, after first event only, after both events without receipt, after receipt without outbox, after all four parts | Only before and complete publication are valid atomic states; the three partial states are invalid trace controls |

All fields not deliberately changed follow Fresh and the exact prefix definitions. At a nonadmission boundary such as Dispatch, refusal is represented as a disabled action plus an INVALID_TRACE control if an implementation nevertheless dispatches; it is not a fabricated kernel refusal event.

### Frame and JCS compatibility fixtures

Rows 75..79 use layer 4 and operation 6. Rows 80..88 use layer 3 operation 5; their input and expected output are opaque UTF-8 JSON byte strings inside the CBOR container. The JCS adapter profile has its own schema id. It does not introduce floats into CBOR.

| Id | Exact case | Expected result |
|---|---|---|
| 75 | Well formed frame containing complete record row 1 variant 1 | Exact frame length and checksum accepted; no extra byte consumed |
| 76 | In the row 75 input frame, change first magic byte52 to 53 | FRAME_BAD_MAGIC, no payload evaluation |
| 77 | In the row 75 input frame, flip low bit of final checksum byte | FRAME_CHECKSUM, no tested operation invoked |
| 78 | Length field 16, 777, 217 with no allocation of that payload | FRAME_LENGTH before allocation |
| 79 | Truncate the row 75 input frame at every incomplete byte prefix | FRAME_TRUNCATED for every incomplete prefix; full frame succeeds |
| 80 | JSON bytes -0, -0.0 and 0.0 | Each JCS output is ASCII0; separate entries |
| 81 | JSON bytes NaN, Infinity and -Infinity | MALFORMED; typed in memory nonfinite probes separately FIELD_INVALID |
| 82 | JSON bytes {"a":1,"a":2} | Reject duplicate before object collapse; NONCANONICAL/DUPLICATE_KEY |
| 83 | Object keys U+E000 and U+1F600 with values1 and 2 | JCS sorts U+1F600 before U+E000 by UTF-16 code units; output UTF-8, no normalization |
| 84 | JSON string precomposed e acute versus decomposed e plus acute | Distinct canonical UTF-8 JSON outputs |
| 85 | RFC 8785 Appendix B binary64 cases, all rows of the published table | Exact RFC expected number text; rejected nonfinite cases retained; no host pretty printer |
| 86 | JSON bytes { "b" : 2, "a" : 1 } | Exact ASCII {"a":1,"b":2} |
| 87 | JSON object key escape \u0061 versus literal a in separate valid objects | Same canonical key a; combined two key object rejected as duplicate after escape decoding |
| 88 | JSON string containing unpaired escaped high surrogate \ud800 | Reject invalid Unicode; MALFORMED/BAD_UTF-8 label is replaced by FIELD_INVALID/FORBIDDEN_TYPE for typed string API, with distinct vector id |

Two JCS profiles must be kept separate. JCS-CANON-2020 tests the canonicalizer behavior requested by FU01, including row 80 negative zero becoming ASCII 0. It is not a secure broker input admission rule. Verified technical erratum 7920, dated 15 May 2024, recommends that a parser reject raw negative zero to avoid attacks on data before parsing. JCS-INPUT-7920 rejects every lexically valid JSON number token whose correctly rounded binary64 value is negative zero before canonicalization. Row 80 variants 100 through 106 are, in order, -0, -0.0, -0e0, -0.00E+2, -0e-7, -0.0000 and -1e-9999; each is refused 4/FORBIDDEN_TYPE under this candidate secure input profile. Variant 107 is the positive zero control 0, accepted as ASCII 0. Rejecting the underflow form is an explicit candidate extension of the defensive input rule; no loss of sign during parsing may bypass it. Programmatically supplied binary64 negative zero remains a canonicalizer case. The profile id must be bound in the auxiliary input and manifest; release is blocked until the Owner reconciles secure broker admission with the baseline canonicalizer tests. No requested -0 to 0 vector is silently changed. [S14]

JCS row 85 must pin the RFC table bytes rather than paraphrase a few conveniently passing values. It is a finite imported normative subcorpus, with each original table row separately identified. Nothing in this report certifies any runtime's number formatter. Ordinary map iteration order is not JCS sorting. UTF-8 byte order is not UTF-16 key order. [S9]

### Coverage and release gate

Rows 1..30 cover canonical primitive and rejection bytes; 31..40 schema, expected state and idempotence; 41..53 authority, lease, goal, plan and pause races; 54..64 retry, cancellation, effects and verification; 65..74 replay, projection, queues, packets and digests; 75..79 framing; 80..88 JCS compatibility. Every refusal0..17 has at least one explicit target case. A generated coverage matrix must map every mutation, invariant and refusal to its input fixtures and observable assertions. Missing one edge fails corpus release even if every executed row passed.

The released corpus must contain complete literal input/output bytes, not expressions such as Fresh or D. This report supplies exact construction rules and expected semantics but does not pretend that unevaluated formulas are already bit for bit receipts. Corpus release is blocked until independent authors materialize/review every expansion, publish the immutable manifest to the Owner's local workflow and retain A/B receipts. FU01 must not begin resource ranking while this prerequisite is incomplete. FU02 may use the semantic event identity and uncertainty oracle now for specification, but its executable persistence comparison must pin the same accepted schema and literal corpus.

## 11 Immutable run identity and independent Alloy protocol

### Identity before execution

Both checker binary and execution environment must be pinned. A container digest alone does not identify a mounted replacement JAR; a JAR digest alone does not identify JVM behavior or native libraries. Bare metal runs use a complete environment manifest instead of pretending a container was used. The immutable RunId is D(manifest, 1, RunManifest), with all output artifact digests collected in a separately signed or reviewed result manifest to avoid self reference.

RunManifest requires: full model module hashes; config and monitor hashes; mutant patch hash or Baseline; constants; schema/corpus digest; TLC JAR SHA-256; full source commit and release reference; Java vendor/version/build and distribution digest; JVM flags; container OCI digest if used, otherwise OS/architecture/runtime manifest digest; command line; environment variables affecting execution; locale/timezone; worker count; fingerprint polynomial; memory/disk/time limits; symmetry/view/state/action constraints; fairness; checker exit semantics; trace export format; source archive hashes; and reviewer identity. No field may be silently inherited from a workstation default.

Research reference is TLC 1.7.4, not the moving 1.8.0 prerelease. Downloaded JAR hash, full commit, JDK artifact, OCI image and run environment are all U in this report. Local agents must obtain official artifacts, compute their digests, retain license and provenance, inspect that pinned binary's help/version output, and lock the supported CLI. A changed tool, module, flag, source archive, host profile or corpus creates a new RunId. Never claim that a retrieved tag proves the binary digest. [S3, S4]

The intended safety invocation is Java with the explicitly recorded heap cap, the pinned TLC JAR, one worker, the RIntegratedSafety configuration and RIntegrated module. The configuration sets SPECIFICATION SafetySpec and all seventeen INVARIANT names. It sets no symmetry, view, state constraint, action constraint, or fairness. The first run records an explicit fingerprint polynomial selection. A second validation run uses a different recorded fingerprint polynomial; agreement reduces one practical risk but does not prove the absence of collisions. The exact accepted options are taken from the pinned binary, not copied blindly from a later documentation page. Optional JSON/TLA trace export is enabled only if the pinned binary supports it. [S3]

No state fingerprint is an event digest. No TLC hash probability estimate is a security claim. Retain explored/distinct states, transition count, maximum depth, completed versus interrupted status, warnings, errors and collision estimates if the binary reports them. A timeout or out of memory is INCONCLUSIVE. Before execution, the Owner/local operator fills the resource envelope (wall time, resident memory, disk and worker cap) and the stopping policy; those values are experiment constraints, not product performance budgets. Unfilled resource limits block the run identity, not a reason to invent benchmark results.

### Alloy cross check

Alloy 6.2.0 is the named independent instrument. Pin its exact JAR, source commit, Java distribution, chosen SAT or temporal backend and native solver bytes. Its6.2.0 release documents CLI availability; local agents must capture that pinned binary's help rather than assume a current example applies. [S5]

The independent Alloy author receives this semantic specification and fixture catalog, not the TLA modules, generated transition code or minimized TLC results. They independently encode Command, Principal, Event, Batch, Lease, Packet, Effect and State as relations. Use explicit event order and full frame conditions. A changed event relation must not leave unrelated state unconstrained. Use dedicated epoch atoms or an integer bit width that can represent every used count; record the width. For these bounds, six signed bits can represent0..20, but field sums and derived indices must also be checked for overflow. Avoid silently interpreting an overflowing cardinality as a valid result.

Structural cases check: unique ordinal and predecessor; batch completeness; one command id to one digest/receipt; all six authority dimensions; unique current lease; packet fence equality; verifier distinctness; projection cursor/tail identity; and preparation/intent/token linkage. Enumerate exact one aggregate/task/effect/timer/verifier and exactly two workers. For targeted structural counterexamples, event scope 0..6 is diagnostic only. Temporal cross checks use exactly the full named epoch sets and bounded traces long enough for each published witness; include stuttering and last state loop semantics explicitly. A trace bound is not a committed event bound. [S6, S7]

Cross check protocol:

1. Independently produce positive existence witnesses for genesis, legal Start/Submit/Verify, exact duplicate, legal retry, and the seven event lease 3/PAUSE/effect prefix in row 53. A safety assertion that holds only because Init or Next is unsatisfiable fails immediately.
2. Check the selected structural assertions and small traces in each tool under aligned domains. Preserve Alloy model, solver settings, all SAT witnesses/UNSAT outcomes, scope and overflow settings.
3. Export each discovered counterexample as the common typed trace schema. Recheck the trace against the other tool's relation with inputs fixed; compare observable states and first differing predicate, not tool specific state numbering.
4. Seed M01, M05, M13, M17, M26, M28 and M31 as mandatory cross tool negative controls. They span atomicity, idempotence, fencing, pause, verification, replay and flow. A missing witness is investigated for scope/mapping/vacuity before blaming a checker.
5. Resolve every discrepancy by identifying a translation, scope, semantic or tool issue, retaining both originals. Do not vote between tools. Unresolved disagreement blocks acceptance.

A complete Alloy temporal check over finite atoms may be an additional check if an independently pinned supported backend is available. It is not required to pretend a bounded SAT backend supports unbounded time. Alloy object scopes remain finite either way. [S6]

The decisive Alloy falsifier is an inability to reproduce a hand checked reachable structural/short trace counterexample under aligned scope, or an unresolved result disagreement with the common reference relation. Competing option is independently authored relational checks plus a different finite state tool, but substituting that option needs Owner review because Alloy 6.2.0 is the named cross check. Neither option proves the production implementation.

## 12 Trace validity and two stack differential contract

### Trace evidence schema

A trace bundle binds run id, schema profile, corpus revision, initial canonical bytes/digest, ordered observations and final state. Each observation records index, boundary kind, command input bytes/digest, actor and authority context, prestate ordinal/digest, admitted batch or refusal, ordered committed event bodies/digests, poststate bytes/digest, receipt, packet fields/digest, durable outbox delta, effect dispatch token and captured fence, replay/projection cursor and tail, and crash/recovery markers. Fields absent by boundary type are explicitly null. Unknown is a distinct tagged observation, not zero, empty bytes or a false Boolean.

Boundary kinds are Decode, Admission, Prepare, Commit, Refusal, ReceiptReuse, Derive, Delivery, ExternalDispatch, EffectObservation, Crash, RecoveryStart, ReplayStep, ReplayRefusal, RecoveryReady and ProjectionStep. Internal trace fields and final event projections use the same profile/schema identity and typed field definitions. Extra implementation details may be retained in a nonnormative extension but cannot replace a required field. A final event projection is not a sufficient record of a prior admission or dispatch fence check.

The checker first validates frame/schema/corpus identity; verifies all concrete digest preimages and event continuity; checks index and commit ordering; reconstructs abstract state using independent reference equations; then checks each adjacent observation against a named modeled action or permitted stutter. It checks refused operations for no canonical mutation and no external dispatch. It preserves crash ambiguity and checks that recovery did not manufacture success. It maps implementation identifiers to typed finite atoms using one injective mapping per trace; it never merges three concrete workers into two to fit a bound. Epochs preserve equality and strict order. The third distinct lease epoch maps to 3, not back to 1. A fourth distinct lease is OUT_OF_SCOPE for this model.

Preparation may map to stuttering only while none of its effects is externally visible. A returned success, durable partial append, changed outbox or actual effect dispatch is not hidden. An operation with missing before/after evidence is INCONCLUSIVE. If the implementation has more internal steps than the model, the checker may match a finite declared sequence of hidden actions, but must emit that witness sequence and preserve the observation order. It may not invent missing external actions or reorder committed events to make the trace fit.

Verdicts are VALID_BOUNDED, INVALID_TRACE, OUT_OF_SCOPE and INCONCLUSIVE. VALID_BOUNDED requires a concrete abstract witness for every observed step and all applicable invariants. INVALID_TRACE gives the first violated rule plus exact operands. OUT_OF_SCOPE means a declared model bound or absent adapter semantics is exceeded, not a product safety verdict. INCONCLUSIVE means necessary evidence, mapping, digest or computation is missing. A refusal can be an entirely valid bounded trace; conversely a success reply can be an invalid trace.

The checker establishes consistency of a finite observed behavior with the declared abstraction, assuming the observations are faithful and complete. It does not quantify over all implementation executions, prove fairness, establish external effect truth, prove OS containment, certify storage durability, verify compiler correctness or provide a machine checked refinement map. A machine checked refinement would require universal initial/step simulation obligations and any needed auxiliary/history variables; checking a finite trace is weaker. [S2]

### Independent stacks

The acceptance equation is exact: A output bytes and structured result = B output bytes and structured result = reviewed normative vector, for every required vector and expansion. Equal digests without retained bytes are insufficient. A and B must also produce independently valid trace receipts for the semantic cases. If both disagree with the normative vector in the same way, they fail; the corpus is not changed just to make them pass.

The stacks share the written contract, literal corpus and approved type definitions as documentation. They share no serializer implementation, decoder registry, reducer implementation, generated source, code generator templates or expected output generator. Prefer distinct maintainers and independent dependency families. They may use a standard SHA-256 primitive, but this shared dependency must be disclosed and each must pass independently sourced known answer tests; a second hash implementation is the stronger competitor. Sharing an OS, compiler, crypto library or upstream harness creates residual common mode risk, not automatic disqualification unless it crosses the prohibited components.

Each team freezes its code/dependency hashes and submits results before seeing the other's outputs or the hidden adversarial corpus partition. A separate reviewer controls expected bytes. Changes after a discrepancy receive new stack/corpus identities and rerun the entire affected suite. Provenance attests author, code origin, dependency lock, generated files, imported snippets and reuse review. Different programming languages alone do not establish independence; two wrappers around the same library fail it. Separate implementations in one language can be independent if the prohibited sharing is absent.

This gate applies equally to v3 native execution and its wrapper/orchestrator adapters for other harnesses. An upstream harness's success event is input evidence, not authority or an independent verifier. The adapter must retain the original identity and epoch fields, classify uncertainty, and show the trace mapping; truncating an upstream result to a convenient success string is not conformance. No runtime or provider is selected by these requirements.

## 13 Explicit seams and recommendation tests

| Unproved seam | What remains open | Required visible evidence boundary |
|---|---|---|
| Unbounded state | One aggregate/task/effect does not establish behavior for arbitrary counts or unbounded history | Exact constants in every receipt; separate larger scope or inductive proof required |
| Digest abstraction | Injective DigestOf is stronger than SHA-256 | Symbolic versus concrete digest labels; byte preimage tests and security review separate |
| Kernel implementation | Model semantics may not match code, compiler or runtime | Literal vectors, independent stacks, trace bridge and later refinement work |
| Storage adapter | Atomic model append does not establish disk durability or stale writer exclusion | FU02 crash/replay receipts and durable boundary fence evidence |
| Broker delivery | Modeled loss/reordering does not certify a real transport | FU05 framing/chaos receipts; explicit uncertainty and cursor identity |
| OS containment | A stopped modeled worker does not prove process tree termination | FU04 native OS fixture evidence |
| External effect truth | A received success may be false; a lost reply may follow a real effect | Provenance/evidence token and reconciliation, never automatic replay |
| Fairness and liveness | Scheduler/provider/human progress is not guaranteed | Separate conditional formulas and named assumptions |
| Projection parity | Same rendering can hide different canonical order or authority | Independent cursor/tail keyed projection bytes and reference reconstruction |
| Model checker itself | Parser, engine, solver, JVM and state fingerprint bugs remain possible | Immutable binaries, negative controls, second fingerprint run, independent Alloy checks |

| Recommendation | Competing option | Decisive falsifier | What it does not prove |
|---|---|---|---|
| Keep TLA/TLC primary at fixed integrated bounds | Alloy primary or another finite state instrument, only after Owner review | Hand checked reachable mandatory fault not found under matching semantics, or incomplete integrated exploration inside agreed resource envelope | Unbounded correctness, code correctness or practical product performance |
| Require independent history/replay/projection monitors | Reuse reducer/projector for convenience | A seeded reducer or hidden field mutation passes because both sides share its logic | Reference requirements themselves are correct |
| Use candidate RCV1 test framing with strict CBOR | Another language neutral deterministic fixture container | Two conforming independent decoders disagree, ambiguous preimage, or a malformed input is normalized away | Production wire format or broker choice |
| Require typed digest domains and exact preimages | One undifferentiated hash function namespace | Distinct object purposes share an unintended preimage or excluded security field | Authentication or collision impossibility |
| Keep receipt reuse separate from fresh dispatch | Reject all duplicates after epoch changes | Replay of an accepted command produces new events/effects, or exact cached receipt becomes nondeterministic | Exactly once effects under arbitrary providers |
| Classify every mutant and kill every reachable non equivalent one | Baseline only or percentage mutation score | Survivor, missing reachability proof, mislabeled equivalent fault or absent minimized receipt | Completeness of the mutant list |
| Require two genuinely independent stacks | One implementation plus a model generated oracle | Shared prohibited code or both stacks agree on output that contradicts normative bytes | Absence of common specification or platform defects |
| Use bounded trace validation before FU01/FU02 admission | Immediate machine checked refinement project | Validator accepts a deliberately invalid trace or drops fields to fit a bound | Universal refinement or liveness |
| Keep Alloy independent and scope aligned | Same source translated automatically into a second syntax | Unresolved disagreement or vacuous positive/negative control | Full integrated exhaustive equivalence |
| Hold adoption until local receipts and independent review | Provisional freeze based on design prose | Any unverified hard floor presented as pass | Owner acceptance or a language/store/transport selection |

There are two separate TLC falsifiers. F1 is semantic sensitivity: failure to distinguish a known reachable non equivalent mutation with the independent monitor and matched scope, after translation errors are eliminated. F2 is adequacy at the agreed bound: failure to reach and retain row 53's lease 3/PAUSE/effect witness and to finish the authoritative safety exploration at all fixed bounds within the predeclared resource envelope. F2 may indicate a poor abstraction or an impractical instrument configuration; it does not show that the product is unsafe. Reducing lease epochs to 2, removing effect uncertainty or PAUSE, or pruning the exposing transition cannot turn F2 into acceptance.

## 14 Local execution handoff

The Owner has said local agent sessions will execute the remaining tests. The following tasks are deliberately left for those sessions. This research session has not done them. Execution authorization and environment selection are local responsibilities; this document does not start a session, install a tool, run a checker, configure a provider, spend money, deploy, publish or merge anything.

The Owner's latest scope correction supersedes the handoff's historical governance description: Hermes is retired. Recursion v3 is a standalone harness and a wrapper/orchestrator of other harnesses, as well as a native harness. H in the synthetic model denotes an authorized local control principal only. It does not reinstate Hermes or assume that any upstream harness has authority. The Owner remains the final decision maker. Local agents must reconcile any older documents against that current scope before using them as acceptance authority.

| Local task | Exact remaining work and evidence | Pass requirement | Fail or stop condition |
|---|---|---|---|
| L01 Reconcile original definitions | Compare locally available DS22 invariant formulas, 36 mutation sites, six authority dimensions, refusal0..17 allocation, API schemas and accepted decisions to candidate report; retain a field by field disposition | Owner accepts a single versioned specification or identifies precisely which candidate details remain proposals | Missing historical source remains unknown; incompatible accepted rule blocks silent adoption |
| L02 Complete mechanical model transcription | Write the named modules and configs, including all guards, UNCHANGED clauses, RecoveryNeeded, target replay/projector versus immutable reference monitors; record a symbol inventory and parse/type output | No undefined operators, incomplete assignments, hidden defaults or missing action/monitor; independent review matches equations | Parse/evaluator errors, accidental circular state digest, unconstrained state or absent action field blocks checker run |
| L03 Pin execution artifacts | Obtain official TLC/Alloy/JDK artifacts, compute digests, archive exact help/version output and licenses; populate RunManifest and resource envelope | Every required field nonnull and full binary/source identity retained | Mutable latest link, unpinned native solver or missing limit makes run inadmissible |
| L04 Validate baseline and vacuity controls | Check Init existence, each action reachability, positive trace fixtures, all 17 invariants and exact integrated bounds; capture complete exploration and any diagnostic reductions separately | Baseline completes without violations; explicit row 53 witness reaches lease 3/pause 1/effect; no pruned required behavior | Violation is a defect to resolve; timeout/OOM is inconclusive; a smaller passing model is not the integrated pass |
| L05 Run all 36 mutations | Apply exactly one registered mutation at a time; prove exposure and NE/equivalence/unreachability; retain original/minimized traces and baseline replay |36/36 classified with receipts; every reachable non equivalent mutation killed; no survivor/inconclusive; historical mandatory count reconciled | Do not count syntax failure, timeout, equivalent or unreachable as killed; do not weaken extra guards to manufacture a kill |
| L06 Run independent Alloy cases | Independent relational author, aligned scope, positive witnesses, selected structural checks and seven seeded faults; exchange only frozen outputs afterward | Each selected witness and result agrees after explicit mapping; discrepancy resolved with evidence | Vacuity, unsupported backend, overflow or unresolved disagreement blocks cross check |
| L07 Materialize literal corpus | Build every primitive, semantic prefix, frame case, JCS case and mandatory expansion as reviewed literal input/output bytes; compute exact preimages/digests and manifest | Complete immutable corpus; full coverage matrix; independent review of every normative byte record | Fresh/D expressions, missing expansion, generated expected results from A/B, unknown digest or unreviewed code allocation blocks corpus release |
| L08 Implement A and B independently | Separate serializer, decoder registry, reducer and generated source; disclose dependencies/code origin; run exact same released corpus | A=B=normative bytes and structured results for every entry, retained outputs and independent review | Any mismatch, shared prohibited component or undocumented normalization rejects conformance |
| L09 Validate trace checker | Feed valid fixtures plus wrong epoch, split append, duplicate effect, hidden field, out of scope fourth lease and incomplete evidence traces | Correct four way verdicts with concrete witnesses and first bad step; invalid controls rejected | Dropped fields, reordered visible events, invented observations or false VALID_BOUNDED blocks all consumers |
| L10 Admit dependent experiments | Give FU01 and FU02 accepted schema/corpus digest, refusal registry, trace checker identity and receipts; require their corresponding hard floors | Consumers bind identical profile/version and pass before resource comparisons | No language/store ranking may substitute for failed byte/safety gate |
| L11 Independent acceptance review | Reviewer other than implementer checks all manifests, classified mutants, byte outputs, assumptions and outstanding seams | Explicit review disposition supplied to Owner | Implementer's own PASS is not acceptance; missing verification stays open |
| L12 Owner decision | Owner separately decides API freeze and any implementation/runtime/store/broker adoption | Explicit accepted decision referencing evidence scope | Validation success alone never selects or freezes anything |

Local agents may fix recoverable transcription or fixture defects within their authorized scope, but every semantic change creates a new candidate revision and requires a comparison to the accepted requirements. They should preserve failing receipts, not overwrite them with a clean rerun. Each discrepancy gets a root cause, changed artifact hashes, rerun scope and independent review. Provider/model/authentication/configuration changes, privileged OS changes, paid routes, deployment and private data sharing remain outside this handoff.

### Required evidence bundle

Return the accepted specification revision; complete source/config/monitor hashes; run environment identities; baseline result and positive reachability witnesses; 36 row classification ledger; all kill/equivalence/unreachability receipts; Alloy results; literal RCV1/JCS corpus and manifest; full byte coverage matrix; A/B origin/dependency attestations and per vector results; trace validator negative controls; FU01/FU02 consumer acknowledgments; unresolved seams; and independent review disposition. Unknown fields remain explicitly null with a blocker reason in draft bundles and cannot be accepted as complete.

The bounded local sequence is reconciliation, transcription and pinning, baseline/positive controls, mutation and independent cross check, literal corpus review, independent stacks, trace checker adversarial controls, dependent experiment admission, independent review, then Owner decision. No duration or measured result is promised. Stop dependent work on a failed safety gate, unresolved semantic conflict or missing authorization; continue unrelated authorized documentation only.

## 15 Completion gate and research question map

| Gate or question | Report coverage | Honest status |
|---|---|---|
| Q1 exact modules/constants/transitions/fairness | Sections3–5 and local transcription contract | Candidate semantic module plan specified; source compilation and historical reconciliation pending |
| Q2 all 17 invariants and monitor independence | Section 5 | All named, expressed and tied to observations; no invariant checked |
| Q3 explicit unproved seams | Section 13 | All ten required seams visible |
| Q4 immutable identity and Alloy protocol | Section 11 | Identity schema/protocol fixed; actual artifact hashes and outcomes unknown |
| Q5 exact36 mutation instantiations | Section 6 | Candidate list complete; original registry and reachability/NE classifications pending |
| Q6 classifications and receipts | Section 6 | Rules/formats complete; no fabricated kill/equivalence/unreachability result |
| Q7 frame/CBOR/digest profile | Sections7–8 | Candidate framing and preimages fixed; not production format or evaluated corpus |
| Q8 minimum coverage corpus | Section 10 |88 rows plus specified expansions; literal materialization/review pending |
| Q9 refusal taxonomy0..17 | Section 9 | Candidate allocation and details fixed; historical reconciliation required |
| Q10 trace bridge | Section 12 | Four verdicts and bounded guarantees defined; checker not implemented or tested |
| Q11 independent A/B differential rule | Section 12 | Prohibited shared components and exact comparison stated; no stacks run |
| Q12 decisive primary/secondary falsifiers | Sections11 and 13 | Semantic sensitivity, integrated bound and Alloy discrepancy falsifiers stated |
| Dependency to FU01 and FU02 | Sections10 and 14 | Blocking artifact identities and order explicit |
| No freeze or selection | Sections1, 13–14 | Preserved |
| Privacy and protected paths | Document artifact review | Only authorized uploaded brief/public research and report artifacts used; no target repository/protected path changed |

A research specification can close a design question while leaving an execution acceptance gate open. In particular, the brief simultaneously forbids running the model and asks for classified mutants and byte reproduction. The honest deliverable is the complete proposed registry, classification obligations and local execution handoff; classified run results and reproduced bytes remain unverified. This distinction is part of the acceptance record.

## 16 Primary source register

All public references were read during research begun 1 October 2026. Source access continued into 2 October 2026 UTC; no post cutoff release is used to change the candidate pins. Reference dates below describe the source itself where available, not the date a search engine crawled it. Short commit abbreviations are discovery references only; the local execution bundle must resolve and retain full commit hashes and binary digests. No private repository source or GitHub connector was used.

S1. Leslie Lamport, Specifying Systems. First printing text 18 June 2002; PDF recreated 4 July 2021. Chapters 8, 10 and 14 for fairness, refinement and finite checking. https://lamport.azurewebsites.net/tla/book-21-07-04.pdf

S2. Leslie Lamport, Refinement in State-Based Formalisms, SRC Technical Note 1996 001, 18 December 1996, author hosted paper. Used for the distinction between behavior refinement obligations and finite trace witnesses. https://lamport.azurewebsites.net/pubs/refinement.pdf

S3. TLA Foundation documentation, TLC Model Checker command line reference. Mutable documentation, accessed 1–2 October 2026. CLI syntax must be checked against the pinned binary. https://docs.tlapl.us/using:tlc:start

S4. TLA tools official Xenophanes release 1.7.4, commit abbreviation 5a47802; full artifact hash not downloaded or measured. https://github.com/tlaplus/tlaplus/releases/tag/v1.7.4

S5. AlloyTools official Alloy 6.2.0 release, 9 January 2025, commit abbreviation 59ba203. CLI and solver capability release notes. https://github.com/AlloyTools/org.alloytools.alloy/releases/tag/v6.2.0

S6. AlloyTools, Alloy 6 language and temporal model checking overview. Mutable official documentation. https://alloytools.org/alloy6.html

S7. Alloy language reference, temporal relational semantics, scopes and lasso traces. Mutable official specification. https://alloytools.org/spec.html

S8. C. Bormann and P. Hoffman, RFC 8949, Concise Binary Object Representation. December 2020, STD 94, sections 4.2 and 5. https://www.rfc-editor.org/rfc/rfc8949.html

S9. A. Rundgren, B. Jordan and S. Erdtman, RFC 8785, JSON Canonicalization Scheme. June 2020, sections 3.1–3.2 and Appendix B. https://www.rfc-editor.org/rfc/rfc8785.html

S10. H. Birkholz, C. Vigano and C. Bormann, RFC 8610, Concise Data Definition Language. June 2019. https://www.rfc-editor.org/rfc/rfc8610.html

S11. NIST, FIPS 180-4, Secure Hash Standard. 4 August 2015, with revision planning note on current publication page. https://csrc.nist.gov/pubs/fips/180-4/upd1/final

S12. B. Laurie, E. Messeri and R. Stradling, RFC 9162, Certificate Transparency Version 2.0. December 2021, section 2.1, cited only as a primary example of domain separated hash preimages, not a Recursion protocol recommendation. https://www.rfc-editor.org/rfc/rfc9162.html

S13. Leslie Lamport, Symmetry and Liveness, 28 May 2015, author explanation of symmetry assumptions and TLC checks. https://discuss.tlapl.us/msg00134.html

S14. RFC Editor, RFC 8785 verified technical erratum 7920, reported 2 May 2024 and verified 15 May 2024. Secure negative zero input parsing guidance. https://www.rfc-editor.org/errata/rfc8785

The uploaded FU03 handoff and README establish the lane requirements; public sources establish technical facts. The Owner's 2 October scope clarification supersedes the handoff's historical governance description.

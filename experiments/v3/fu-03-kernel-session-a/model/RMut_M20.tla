------------------------- MODULE RMut_M20 -------------------------
(***************************************************************************)
(* FU-03 kernel Session A: enlarged diagnostic model with the reconciled    *)
(* guard applied.                                                           *)
(*                                                                          *)
(* NOT the accepted integrated gate. Same boundary as RBig, but the         *)
(* witness-step guard FireTimerEffectOK is FIXED:                           *)
(*                                                                          *)
(*     the timer cannot set retryReady while an effect is unresolved         *)
(*     (eff.status must be None or KnownNoEffect).                          *)
(*                                                                          *)
(* This is the selected half of the reconciliation: RetryEffectOK already   *)
(* blocks Retry over an unresolved effect; FireTimerEffectOK now blocks the *)
(* timer from arming a replay before recovery proves KnownNoEffect.         *)
(* M25 removes exactly this guard. M31 removes the outbox bound.            *)
(***************************************************************************)
EXTENDS Naturals, Sequences, FiniteSets

CmdIds == 1..10
MaxEvents == 12
Cap == 3
GENESIS == <<"genesis">>

DigestOf(tag, x) == <<tag, x>>

WorkerProgress == {"Start", "Submit", "SubmitFail", "Retry", "PrepareEffect", "MarkDispatch"}

VARIABLES
  ordinal, log, tail, receipts, order,
  goal, plan, lease, pauseEpoch, paused, writer,
  status, owner, attempt, result, producer, verifierResult,
  eff, timer, retryReady, cancelled, outbox, ref

vars == <<ordinal, log, tail, receipts, order, goal, plan, lease, pauseEpoch, paused,
          writer, status, owner, attempt, result, producer, verifierResult, eff, timer,
          retryReady, cancelled, outbox, ref>>

(***************************************************************************)
(* Isolated guard sites (single-site mutation targets).                     *)
(***************************************************************************)
Fresh(id) == receipts[id].used = FALSE
WorkerProgressGuard == ~paused /\ ~cancelled
VerifierOK == producer # "w2"
RetryEffectOK == eff.status \in {"None", "KnownNoEffect"}
OutboxOK == Len(outbox) < Cap
ResultAcceptanceOK == attempt \in 1..2
AttemptBoundOK == attempt < 2
RetryTimerOK == TRUE
DispatchPreparedOK == eff.status = "Prepared"
AcceptedVerifierResult == result
FireTimerEffectOK == eff.status \in {"None", "KnownNoEffect"}   \* reconciled witness-step guard

(***************************************************************************)
(* Sound symmetry-breaking constraint. CmdIds are interchangeable in every  *)
(* action and invariant, so restrict to the canonical representative where  *)
(* the ids ever used form an initial segment {1..k} (ids are consumed in     *)
(* order of first use). Applied via CONSTRAINT in the .cfg; it does not      *)
(* change the specification, only selects one representative per orbit.      *)
(***************************************************************************)
CanonicalIds == \A i \in CmdIds : i > 1 => (receipts[i].used => receipts[i - 1].used)

(***************************************************************************)
(* Independent, log-folding reference monitor.                              *)
(***************************************************************************)
RefReduce(L) ==
  LET chainOK == \A i \in DOMAIN L :
                   /\ L[i].prev = (IF i = 1 THEN GENESIS ELSE L[i - 1].digest)
                   /\ L[i].digest =
                        DigestOf("event", <<i, L[i].body.kind, L[i].body.id, L[i].prev>>)
      dispatches == SelectSeq(L, LAMBDA e: e.body.kind = "MarkDispatch")
      retries == SelectSeq(L, LAMBDA e: e.body.kind = "Retry")
  IN [chainOK |-> chainOK, dispatched |-> Len(dispatches), retries |-> Len(retries)]

Event(kind, id) ==
  LET n == ordinal + 1
      p == IF ordinal = 0 THEN GENESIS ELSE log[ordinal].digest
      d == DigestOf("event", <<n, kind, id, p>>)
  IN [ordinal |-> n, prev |-> p,
      body |-> [kind |-> kind, id |-> id, paused |-> paused, cancelled |-> cancelled],
      digest |-> d]

NextLog(kind, id) == Append(log, Event(kind, id))

AppendEvent(kind, id) ==
  /\ ordinal < MaxEvents
  /\ log' = NextLog(kind, id)
  /\ ordinal' = ordinal + 1
  /\ tail' = Event(kind, id).digest
  /\ receipts' = [receipts EXCEPT ![id] = [used |-> TRUE, kind |-> kind, ord |-> ordinal + 1]]
  /\ order' = Append(order, id)
  /\ ref' = RefReduce(NextLog(kind, id))

Init ==
  /\ ordinal = 0 /\ log = <<>> /\ tail = GENESIS
  /\ receipts = [i \in CmdIds |-> [used |-> FALSE, kind |-> "Start", ord |-> 0]]
  /\ order = <<>>
  /\ goal = 1 /\ plan = 1 /\ lease = 1 /\ pauseEpoch = 0 /\ paused = FALSE /\ writer = 1
  /\ status = "Ready" /\ owner = "none" /\ attempt = 0
  /\ result = "none" /\ producer = "none" /\ verifierResult = "none"
  /\ eff = [status |-> "None", attempt |-> 0]
  /\ timer = [status |-> "Disarmed", attempt |-> 0]
  /\ retryReady = FALSE /\ cancelled = FALSE /\ outbox = <<>>
  /\ ref = RefReduce(<<>>)

GrantLease ==
  \E w \in {"w1", "w2"} : \E id \in CmdIds :
    /\ Fresh(id) /\ lease < 3
    /\ AppendEvent("GrantLease", id)
    /\ lease' = lease + 1 /\ owner' = w
    /\ UNCHANGED <<goal, plan, pauseEpoch, paused, writer, status, attempt, result,
                   producer, verifierResult, eff, timer, retryReady, cancelled, outbox>>

RevokeLease ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ lease < 3
    /\ AppendEvent("RevokeLease", id)
    /\ lease' = lease + 1 /\ owner' = "none"
    /\ UNCHANGED <<goal, plan, pauseEpoch, paused, writer, status, attempt, result,
                   producer, verifierResult, eff, timer, retryReady, cancelled, outbox>>

AdvanceGoal ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ goal = 1
    /\ AppendEvent("AdvanceGoal", id)
    /\ goal' = 2
    /\ UNCHANGED <<plan, lease, pauseEpoch, paused, writer, status, owner, attempt, result,
                   producer, verifierResult, eff, timer, retryReady, cancelled, outbox>>

AmendPlan ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ plan = 1
    /\ AppendEvent("AmendPlan", id)
    /\ plan' = 2
    /\ UNCHANGED <<goal, lease, pauseEpoch, paused, writer, status, owner, attempt, result,
                   producer, verifierResult, eff, timer, retryReady, cancelled, outbox>>

Pause ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ ~paused /\ pauseEpoch = 0
    /\ AppendEvent("Pause", id)
    /\ paused' = TRUE /\ pauseEpoch' = 1
    /\ UNCHANGED <<goal, plan, lease, writer, status, owner, attempt, result,
                   producer, verifierResult, eff, timer, retryReady, cancelled, outbox>>

Resume ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ paused
    /\ AppendEvent("Resume", id)
    /\ paused' = FALSE
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, writer, status, owner, attempt, result,
                   producer, verifierResult, eff, timer, retryReady, cancelled, outbox>>

Start ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ WorkerProgressGuard
    /\ owner # "none" /\ status = "Ready" /\ attempt = 0
    /\ AppendEvent("Start", id)
    /\ status' = "Running" /\ attempt' = 1
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, result, producer,
                   verifierResult, eff, timer, retryReady, cancelled, outbox>>

Submit ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ WorkerProgressGuard
    /\ owner # "none" /\ status = "Running" /\ ResultAcceptanceOK
    /\ AppendEvent("Submit", id)
    /\ status' = "Submitted" /\ result' = "R1" /\ producer' = owner
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, attempt, verifierResult,
                   eff, timer, retryReady, cancelled, outbox>>

SubmitFail ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ WorkerProgressGuard
    /\ owner # "none" /\ status = "Running" /\ ResultAcceptanceOK
    /\ AppendEvent("SubmitFail", id)
    /\ status' = "Failed" /\ result' = "none"
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, attempt, producer,
                   verifierResult, eff, timer, retryReady, cancelled, outbox>>

Verify ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ status = "Submitted" /\ result # "none" /\ VerifierOK /\ verifierResult = "none"
    /\ AppendEvent("Verify", id)
    /\ verifierResult' = AcceptedVerifierResult /\ status' = "Done"
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, attempt, result,
                   producer, eff, timer, retryReady, cancelled, outbox>>

ArmTimer ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ status = "Failed" /\ timer.status = "Disarmed" /\ AttemptBoundOK
    /\ AppendEvent("ArmTimer", id)
    /\ timer' = [status |-> "Armed", attempt |-> attempt]
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, status, attempt,
                   result, producer, verifierResult, eff, retryReady, cancelled, outbox>>

FireTimer ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ timer.status = "Armed" /\ FireTimerEffectOK
    /\ AppendEvent("FireTimer", id)
    /\ timer' = [status |-> "Fired", attempt |-> timer.attempt] /\ retryReady' = TRUE
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, status, owner, attempt,
                   result, producer, verifierResult, eff, cancelled, outbox>>

Retry ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ WorkerProgressGuard
    /\ status = "Failed" /\ RetryTimerOK /\ AttemptBoundOK /\ RetryEffectOK
    /\ AppendEvent("Retry", id)
    /\ attempt' = attempt + 1 /\ status' = "Running"
    /\ result' = "none" /\ producer' = "none" /\ verifierResult' = "none"
    /\ timer' = [status |-> "Disarmed", attempt |-> attempt + 1] /\ retryReady' = FALSE
    /\ eff' = [status |-> "None", attempt |-> attempt + 1]
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, cancelled, outbox>>

Cancel ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ ~cancelled
    /\ AppendEvent("Cancel", id)
    /\ cancelled' = TRUE /\ status' = "Cancelled" /\ retryReady' = FALSE
    /\ timer' = [status |-> "Disarmed", attempt |-> timer.attempt]
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, attempt, result,
                   producer, verifierResult, eff, outbox>>

PrepareEffect ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ WorkerProgressGuard
    /\ status = "Running" /\ eff.status = "None"
    /\ AppendEvent("PrepareEffect", id)
    /\ eff' = [status |-> "Prepared", attempt |-> attempt]
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, status, attempt,
                   result, producer, verifierResult, timer, retryReady, cancelled, outbox>>

MarkDispatch ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ WorkerProgressGuard
    /\ DispatchPreparedOK /\ OutboxOK
    /\ AppendEvent("MarkDispatch", id)
    /\ eff' = [status |-> "InFlight", attempt |-> eff.attempt]
    /\ outbox' = Append(outbox, <<"token", eff.attempt, id>>)
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, status, attempt,
                   result, producer, verifierResult, timer, retryReady, cancelled>>

ObserveEffect ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ eff.status \in {"InFlight", "Unknown"}
    /\ AppendEvent("ObserveEffect", id)
    /\ eff' = [status |-> "Succeeded", attempt |-> eff.attempt]
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, status, attempt,
                   result, producer, verifierResult, timer, retryReady, cancelled, outbox>>

ReconcileEffect ==
  \E id \in CmdIds :
    /\ Fresh(id) /\ eff.status \in {"InFlight", "Unknown"}
    /\ AppendEvent("ReconcileEffect", id)
    /\ eff' = [status |-> "KnownNoEffect", attempt |-> eff.attempt]
    /\ UNCHANGED <<goal, plan, lease, pauseEpoch, paused, writer, owner, status, attempt,
                   result, producer, verifierResult, timer, retryReady, cancelled, outbox>>

Next ==
  \/ GrantLease \/ RevokeLease \/ AdvanceGoal \/ AmendPlan
  \/ Pause \/ Resume \/ Start \/ Submit \/ SubmitFail \/ Verify
  \/ ArmTimer \/ FireTimer \/ Retry \/ Cancel
  \/ PrepareEffect \/ MarkDispatch \/ ObserveEffect \/ ReconcileEffect

Spec == Init /\ [][Next]_vars

(***************************************************************************)
(* Invariants                                                               *)
(***************************************************************************)
TypeOK ==
  /\ ordinal \in 0..MaxEvents
  /\ ordinal = Len(log)
  /\ \A i \in DOMAIN log : log[i].ordinal = i
  /\ goal \in {1, 2} /\ plan \in {1, 2} /\ lease \in 1..3
  /\ pauseEpoch \in {0, 1} /\ paused \in BOOLEAN /\ writer \in {1, 2}
  /\ status \in {"Ready", "Running", "Submitted", "Failed", "Done", "Cancelled"}
  /\ owner \in {"none", "w1", "w2"}
  /\ attempt \in 0..MaxEvents   \* structural bound; RetryBound owns the semantic limit
  /\ eff.status \in {"None", "Prepared", "InFlight", "Unknown", "Succeeded", "KnownNoEffect"}
  /\ timer.status \in {"Disarmed", "Armed", "Fired"}
  /\ ref \in [chainOK : BOOLEAN, dispatched : 0..MaxEvents, retries : 0..MaxEvents]

ChainIntegrity ==
  \A i \in DOMAIN log :
    /\ log[i].ordinal = i
    /\ log[i].prev = (IF i = 1 THEN GENESIS ELSE log[i - 1].digest)
    /\ log[i].digest =
         DigestOf("event", <<i, log[i].body.kind, log[i].body.id, log[i].prev>>)

OrdinalConsistent == ordinal = Len(log)

NoDuplicateIds ==
  \A i, j \in DOMAIN order : i # j => order[i] # order[j]

PauseNoProgress ==
  \A i \in DOMAIN log : log[i].body.kind \in WorkerProgress => log[i].body.paused = FALSE

CancelNoResurrect ==
  \A i, j \in DOMAIN log :
    (log[i].body.kind = "Cancel" /\ j > i) => log[j].body.kind \notin WorkerProgress

VerifierSafety ==
  status = "Done" => verifierResult # "none" /\ verifierResult = result /\ producer # "w2"

RetryBound == attempt <= 2

NoBlindEffectReplay ==
  eff.status \in {"InFlight", "Unknown"} => retryReady = FALSE

FlowBound == Len(outbox) <= Cap

EffectSafety ==
  \A i \in DOMAIN log :
    log[i].body.kind = "MarkDispatch" =>
      \E j \in DOMAIN log : j < i /\ log[j].body.kind = "PrepareEffect"

RetrySafety ==
  \A i \in DOMAIN log :
    log[i].body.kind = "Retry" =>
      \E j \in DOMAIN log : j < i /\ log[j].body.kind = "FireTimer"

ProjectionParity ==
  ref.dispatched = Len(outbox)

=============================================================================

------------------------- MODULE RKernel -------------------------
(***************************************************************************)
(* Reduced-bound first cut of the Recursion v3 four-function kernel model.  *)
(*                                                                          *)
(* Evidence class: inference/design, NOT the accepted integrated bound.     *)
(* This model deliberately reduces CmdIds and MaxEvents to keep the first   *)
(* TLC run mechanical. The strategy (ds-FU-03) states that a reduced bound  *)
(* has a distinct configuration identity and cannot satisfy the integrated  *)
(* gate; this run is diagnostic only.                                       *)
(*                                                                          *)
(* Modelled here: canonical event log with ordinal + predecessor chain,      *)
(* atomic append of one event per command, command receipts with idempotent  *)
(* ids, lease grant/revoke, goal/plan amendment, pause/resume, start/submit. *)
(* Not modelled here: derived packets, effect dispatch, replay/projection    *)
(* monitors, the 36 mutants, CBOR byte vectors. See README.md.               *)
(***************************************************************************)
EXTENDS Naturals, Sequences, FiniteSets

CmdIds == 1..3
MaxEvents == 6

GENESIS == <<"genesis">>

(***************************************************************************)
(* Symbolic injective digest abstraction. Explicitly stronger than SHA-256. *)
(***************************************************************************)
DigestOf(tag, x) == <<tag, x>>

Kinds == {"GrantLease", "RevokeLease", "AdvanceGoal", "AmendPlan",
          "Pause", "Resume", "Start", "Submit"}

VARIABLES
  ordinal, log, receipts, order,
  lease, owner, paused, pauseEpoch, goal, plan, status, attempt, cancelled

vars == <<ordinal, log, receipts, order, lease, owner, paused, pauseEpoch,
          goal, plan, status, attempt, cancelled>>

(***************************************************************************)
(* The event appended for (kind, id) at the next ordinal.                   *)
(***************************************************************************)
Event(kind, id) ==
  LET n == ordinal + 1
      p == IF ordinal = 0 THEN GENESIS ELSE log[ordinal].digest
      d == DigestOf("event", <<n, kind, id, p>>)
  IN [ordinal |-> n, prev |-> p,
      body |-> [kind |-> kind, id |-> id], digest |-> d]

(***************************************************************************)
(* Atomic append: one event, one receipt, one order entry, one ordinal step. *)
(***************************************************************************)
AppendEvent(kind, id) ==
  /\ ordinal < MaxEvents
  /\ log' = Append(log, Event(kind, id))
  /\ ordinal' = ordinal + 1
  /\ receipts' = [receipts EXCEPT ![id] = [used |-> TRUE, kind |-> kind, ord |-> ordinal + 1]]
  /\ order' = Append(order, id)

Init ==
  /\ ordinal = 0
  /\ log = <<>>
  /\ receipts = [i \in CmdIds |-> [used |-> FALSE, kind |-> "Start", ord |-> 0]]
  /\ order = <<>>
  /\ lease = 1
  /\ owner = "none"
  /\ paused = FALSE
  /\ pauseEpoch = 0
  /\ goal = 1
  /\ plan = 1
  /\ status = "Ready"
  /\ attempt = 0
  /\ cancelled = FALSE

GrantLease ==
  \E w \in {"w1", "w2"} : \E id \in CmdIds :
    /\ receipts[id].used = FALSE
    /\ lease < 2
    /\ AppendEvent("GrantLease", id)
    /\ lease' = lease + 1
    /\ owner' = w
    /\ UNCHANGED <<paused, pauseEpoch, goal, plan, status, attempt, cancelled>>

RevokeLease ==
  \E id \in CmdIds :
    /\ receipts[id].used = FALSE
    /\ lease < 2
    /\ AppendEvent("RevokeLease", id)
    /\ lease' = lease + 1
    /\ owner' = "none"
    /\ UNCHANGED <<paused, pauseEpoch, goal, plan, status, attempt, cancelled>>

AdvanceGoal ==
  \E id \in CmdIds :
    /\ receipts[id].used = FALSE
    /\ goal = 1
    /\ AppendEvent("AdvanceGoal", id)
    /\ goal' = 2
    /\ UNCHANGED <<lease, owner, paused, pauseEpoch, plan, status, attempt, cancelled>>

AmendPlan ==
  \E id \in CmdIds :
    /\ receipts[id].used = FALSE
    /\ plan = 1
    /\ AppendEvent("AmendPlan", id)
    /\ plan' = 2
    /\ UNCHANGED <<lease, owner, paused, pauseEpoch, goal, status, attempt, cancelled>>

Pause ==
  \E id \in CmdIds :
    /\ receipts[id].used = FALSE
    /\ ~paused /\ pauseEpoch = 0
    /\ AppendEvent("Pause", id)
    /\ paused' = TRUE
    /\ pauseEpoch' = 1
    /\ UNCHANGED <<lease, owner, goal, plan, status, attempt, cancelled>>

Resume ==
  \E id \in CmdIds :
    /\ receipts[id].used = FALSE
    /\ paused
    /\ AppendEvent("Resume", id)
    /\ paused' = FALSE
    /\ UNCHANGED <<lease, owner, pauseEpoch, goal, plan, status, attempt, cancelled>>

Start ==
  \E id \in CmdIds :
    /\ receipts[id].used = FALSE
    /\ owner # "none" /\ status = "Ready" /\ attempt = 0
    /\ ~paused /\ ~cancelled
    /\ AppendEvent("Start", id)
    /\ status' = "Running"
    /\ attempt' = 1
    /\ UNCHANGED <<lease, owner, paused, pauseEpoch, goal, plan, cancelled>>

Submit ==
  \E id \in CmdIds :
    /\ receipts[id].used = FALSE
    /\ owner # "none" /\ status = "Running"
    /\ ~paused /\ ~cancelled
    /\ AppendEvent("Submit", id)
    /\ status' = "Submitted"
    /\ UNCHANGED <<lease, owner, paused, pauseEpoch, goal, plan, attempt, cancelled>>

Next ==
  \/ GrantLease \/ RevokeLease \/ AdvanceGoal \/ AmendPlan
  \/ Pause \/ Resume \/ Start \/ Submit

Spec == Init /\ [][Next]_vars

(***************************************************************************)
(* Invariants                                                               *)
(***************************************************************************)
TypeOK ==
  /\ ordinal \in 0..MaxEvents
  /\ ordinal = Len(log)
  /\ \A i \in DOMAIN log : log[i].ordinal = i
  /\ receipts \in [CmdIds -> [used : BOOLEAN, kind : Kinds, ord : 0..MaxEvents]]
  /\ lease \in 1..2
  /\ owner \in {"none", "w1", "w2"}
  /\ paused \in BOOLEAN
  /\ pauseEpoch \in {0, 1}
  /\ goal \in {1, 2}
  /\ plan \in {1, 2}
  /\ status \in {"Ready", "Running", "Submitted"}
  /\ attempt \in {0, 1}
  /\ cancelled \in BOOLEAN

ChainIntegrity ==
  \A i \in DOMAIN log :
    /\ log[i].ordinal = i
    /\ log[i].prev = (IF i = 1 THEN GENESIS ELSE log[i - 1].digest)
    /\ log[i].digest =
         DigestOf("event", <<i, log[i].body.kind, log[i].body.id, log[i].prev>>)

OrdinalConsistent == ordinal = Len(log)

NoDuplicateIds ==
  \A i, j \in DOMAIN order : i # j => order[i] # order[j]

=============================================================================

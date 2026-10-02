------------------------- MODULE RMutant -------------------------
(***************************************************************************)
(* Mutant M02 CHAIN_PREV_DELETE (ds-FU-03 section 6).                       *)
(*                                                                          *)
(* Single controlled semantic edit: the event predecessor field is always   *)
(* GENESIS, i.e. the previous-digest chain link is deleted. Everything else *)
(* is identical to RKernel. Expected: TLC finds a counterexample to         *)
(* ChainIntegrity at the second event.                                      *)
(***************************************************************************)
EXTENDS Naturals, Sequences, FiniteSets

CmdIds == 1..3
MaxEvents == 6

GENESIS == <<"genesis">>

DigestOf(tag, x) == <<tag, x>>

Kinds == {"GrantLease", "RevokeLease", "AdvanceGoal", "AmendPlan",
          "Pause", "Resume", "Start", "Submit"}

VARIABLES
  ordinal, log, receipts, order,
  lease, owner, paused, pauseEpoch, goal, plan, status, attempt, cancelled

vars == <<ordinal, log, receipts, order, lease, owner, paused, pauseEpoch,
          goal, plan, status, attempt, cancelled>>

(***************************************************************************)
(* MUTATION: prev is always GENESIS; the chain link is deleted.             *)
(***************************************************************************)
Event(kind, id) ==
  LET n == ordinal + 1
      d == DigestOf("event", <<n, kind, id, GENESIS>>)
  IN [ordinal |-> n, prev |-> GENESIS,
      body |-> [kind |-> kind, id |-> id], digest |-> d]

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

TypeOK ==
  /\ ordinal \in 0..MaxEvents
  /\ ordinal = Len(log)

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

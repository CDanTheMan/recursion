# Counterexample derivations — 2026-09-09

These are manual arguments about the stated reducers, independently challenged by
counterexample_reasoning. They are not proofs of source validity or execution results.
The new committed packet must reproduce the concrete original N=3 and N=4 examples.

Before the first C action, neither policy has an active seal, so both service exactly
the same appends. Their first capture size k is therefore the same. Each policy's
capture sizes strictly increase: failure means visible count advanced, while a
successful check forbids reopening until it advances. At a joint completed endpoint
both final captures have size N, with no unfinished capture. Read work is the sum of
capture sizes, since every capture finishes before another can open.

For positive N<=2, those constraints force identical capture histories, so there is
no completed sealed-read advantage. At N=3, common first capture 3 forces {3}; first
capture 2 forces {2,3}; first capture 1 permits {1,3} or {1,2,3}. The only reversal
is optimistic {1,2,3} versus sealed {1,3}, costing 6 versus 4 reads.

For every N>=3, any completed sealed-read advantage requires at least three
optimistic captures. With at most two, its common first and final sizes give the
minimum work any sealed history can have. Three or more increasing optimistic
captures cost at least 1+2+N reads and three openings plus three checks: N+9 C
actions. All N-1 noninitial records must be offered. Sealed must service N-1 appends,
and divergence requires at least one postponed A: without a postponed append,
visibility and both reducers' evolution coincide. Thus there are at least N A
actions and N-1 O actions, giving a lower bound of 3N+8 total actions.

The word `COACCC O^(N-2) A^(N-1) C^(N+5)` attains that bound. `COACC` opens/reads
capture 1 in both policies; optimistic appends during it and invalidates, while
sealed checks 1. The next C opens optimistic capture 2 while sealed idles. The
offers and service burst bring both to N before sealed opens another capture.
The final C burst finishes optimistic's stale size-2 capture, then its size-N
capture; sealed only captures N. Histories are {1,2,N} and {1,N}, costing N+3 and
N+1 reads. N=3 gives 17 actions and 6 versus 4 reads; N=4 gives 20 and 7 versus 5.
The earlier N=4 22-action 8-versus-7 example stays valid but is not shortest.

This is shortestness for completed endpoints in the exact unit-action contract,
starting with one visible original record and no active collector. It is not a
shortest wall-clock execution, an intermediate-state comparison, or a claim that
all possible capture-history pairs are reachable. The finite necessary-history
certificate intentionally overapproximates reachable pairs. The general symbolic
construction does not create or execute larger original source inventories.

The unchanged-count idling guard is also needed for the earlier progress and read
bounds. Remove it only from sealed collection; offer all N=3 records, then repeat
CCAC. At each cycle: C opens at visible 1; C reads ordinal 0; A is postponed because
the seal is active; C checks 1 and releases it. The next cycle immediately reseals
before its A. At every cycle boundary, visible remains 1, checked=1, the collector
is inactive, two appends remain pending, and reads/captures/checks/postponements
each increase by one. Offer and completed-wait fields remain unchanged.

Induction on this recurrence supplies an infinite extension with infinitely many
A and C opportunities but no further sealed append service. Seven cycles give a
finite read count 7, exceeding the original N=3 bound 6. The finite run alone does
not prove the infinite statement. Fair occurrence of opportunity symbols is weaker
than fairness of an enabled append transition; the recurrence does not satisfy
every stronger fairness definition. The original guard prevents this resealing
schedule and is part of its sufficient opportunity-based completion argument.

Matched-record waiting dominance uses different premises: identical FIFO records,
arrival steps and action word, unit append service, optimistic always accepting
pending A service, and sealed only suppressing it. It is a logical scheduling-step
claim, not physical-time dominance or a comparison of independent schedulers.
Q1-Q6, source metadata changes, crashes and real runtime selection remain outside
these derivations. Only the explicitly declared idling guard varies in this packet.

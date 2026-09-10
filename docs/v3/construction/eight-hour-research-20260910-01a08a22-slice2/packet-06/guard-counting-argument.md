2026-09-10 — conditional guard classification for the original scale profile

This packet checks a source argument about all 40,320 core orders of the original scale-eight-action-race profile. It does not execute the model histories or establish their intermediate response, journal, strict-relation or accepted-relation comparisons. It adds no successful-attestation witness. The earlier model packets remain the execution evidence.

The hypotheses are the original successful fixed setup (valid registration, attempt 1, three append records and no pause), unchanged profile dependencies and successful delivery, the success cut's attempt-1-only mapping, outcome 1, either original unit, and non-mutant source and adapter semantics. Source files are pinned in the specification. These are explicit hypotheses of the combinatorial certificate, supported by source review; the order-only checker does not prove setup correctness by executing it.

Write O for collect-open, R for restart, A2/A3/A4 for the attempt calls, and C0/C1/C2 for the three collections. The eight core occurrences are freely ordered between the unchanged setup and suffix. Inequalities below mean chronological occurrence order, not numeric occurrence suffixes.

Attempt 2 always succeeds: before it executes, attempts 3 and 4 cannot satisfy the sequential-number guard. Attempt 3 succeeds exactly when A2 < A3. Attempt 4 succeeds exactly when A2 < A3 < A4. Successful attempts increase source_revision; refused attempts do not. Restart changes incarnation and preserves the registry. Each collection succeeds exactly when O precedes it; the append inventory has already been fixed by setup.

A current capture requires O to follow restart and every successful attempt. This freshness predicate F has two disjoint forms:

1. All of A2, A3, A4 and R precede O.
2. A3 < A2 < O < A4, with R < O.

The exceptional second form is necessary. Attempt 3 has already gap-refused, so the later attempt 4 also gap-refuses and does not invalidate capture. Requiring every attempted registration before O would incorrectly discard these fresh captures.

Let I mean that O precedes C0, C1 and C2. The attestation at chronological prefix 22 encounters guards in this order:

| Condition | First refusing attestation guard | Predicted orders per unit |
|---|---|---:|
| not F | stale-collection | 31,248 |
| F and not I | incomplete-inventory | 8,856 |
| F and I | incomplete-registry | 216 |
| successful attestation | impossible under these hypotheses | 0 |

Registration, capture and delivered cut exist, excluding no-captured-source. A fresh capture contains attempt 2; its registry cannot equal the fixed cut's attempt-1-only mapping. This proves the last refusal without examining later publication behavior. The first refusing attestation guard is not necessarily the history's earliest visible refusal or first relation failure.

The first freshness class has 8!/5 = 8,064 orders. The second has three allowed relative positions of R among its five distinguished actions, giving 3(8!/5!) = 1,008. Thus 9,072 captures are fresh. Adding I yields 4!3! = 144 orders in the first class and 3(4!) = 72 in the exceptional class, for 216 fresh complete inventories. Subtracting gives the table.

Each of the six relative attempt orders occurs in 6,720 full orders. Five have 1,344 fresh and 24 fresh-complete orders. The exceptional A3 < A2 < A4 order has 2,352 fresh and 96 fresh-complete orders. These independent subtotals supplement aggregate equality.

A discriminating witness is R, A3, A2, O, A4, C0, C1, C2. Its capture is fresh and complete, and its first refusing attestation guard is incomplete-registry. Treating A4's failed call as a revision change would misclassify it as stale.

The new checker generates literal order records from successful-attempt predicates and compares every record with the disjoint partial-order characterization. A separately owned retained audit verifies every serialized record and proves complete membership using a factorial-rank bijection over all eight-occurrence permutations. Both jobs use finite checked symbolic-work counters. The campaign conservatively charges their full reservations to the existing cumulative ledger while reporting zero model-state visits for this packet. These records are symbolic certificates, not model replay certificates.

The primary source grounding is s_domain.py:40–41,141–149; s_inclusive.py:21–35,55–69; q_inclusive.py:13; p_literal.py:24; c_domain.py:27–30; and batch-06/guard_a.py:22–35,56–71. The ten exact source pins include the corresponding adapter implementations and existing experiment assertions. Two independent same-model reviews checked the conditional derivation before any enumeration.

No unrestricted refinement, original-Q-profile reachability, source truth/Q1–Q6, composition, fairness, physical recovery or runtime integration follows. The selected48-history and small60-history prefix-sharing tools passed their actual local checks and owned receipt audit in this slice; their separate final gates and publication status belong to the current increment. This symbolic certificate does not extend their full-history coverage. Under the selected constraint, C0/C1/A3/A4 precede O/C2/A2/R. Only A2 succeeds; freshness requires A2 and R before O, yielding eight fresh and sixteen stale orders per unit. Inventory is never complete because C0/C1 precede O. Thus the conditional projection predicts32 stale and16 incomplete-inventory refusals across both units, consistent with the independently executed selected subset. This agreement does not execute the other40,296 orders per unit.

# Append handoff comparison — 2026-09-09

Neither servicing one append before resealing nor dynamically draining the offered
backlog universally wins on ordinal reads or matched-record waiting. This rules out
choosing either policy from a single favorable schedule. It does not choose a runtime
architecture or settle source validity. Both policies retain a finite read-work bound
and eventual completion under the specified finite-offer scheduling premises.

The admitted paired model completed 77,841 states and 78,300 edges per representation,
with exact state/edge/parent/terminal equality, independent all-field checks and zero
frontier. The preserved earlier progress and counterexample packets reproduced in full.
Five negative controls were detected, including a structurally valid drain capture
started while a record remained pending. The owned run took 6.83 seconds and peaked
at 135,028,736 bytes, with exit zero and no owned processes after cleanup.

| Original stream | N | States | Terminals | one fewer / equal / drain fewer reads |
|---|---:|---:|---:|---|
| success | 3 | 15,735 | 356 | 2 / 96 / 258 |
| ambiguous | 2 | 3,962 | 133 | 0 / 73 / 60 |
| prior-unresolved | 4 | 29,072 | 452 | 0 / 41 / 411 |
| later-start-only | 4 | 29,072 | 452 | 0 / 41 / 411 |

These are distinct completed-state counts, not probabilities or performance estimates.
The two N4 rows share a count-domain graph. Exhaustiveness covers length-six O/A/C
prefixes followed by one declared quiet suffix, not every possible schedule.

Three preregistered manual words independently reproduce the mechanisms: N2 reads
3 versus 2; N3 reads 4 versus 5; and N3 waiting vectors (0,5,1) versus (0,2,4).
The second case reverses the read ordering; the third reverses the waiting ordering
between two individual records. Their full traces are in results.json. Derivations
separate general finite-inventory arguments from these finite observations.

A practical architecture decision still needs an owner-selected objective and arrival
assumptions. Aggregating fewer reads across this artificial domain is not sufficient.
No additional campaign, objective, product/framework, runtime or provider is selected.
Q1-Q6, source validity, full composition and runtime integration remain unresolved.
All original sources, six obligations, 27 trace rows and A6/B6 pool10 data are preserved.

This document records the accepted local packet. Publication requires two subsequent
full 44-item validations on the same clean candidate and two independent exact reviews.
Their receipts and final publication status belong in the external candidate completion
record, avoiding a circular candidate hash or rewriting historical evidence.

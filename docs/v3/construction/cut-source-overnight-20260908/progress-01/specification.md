# Conditional collection progress — 2026-09-09

Parent goal-recursion-v2-execution-fabric; same SC-CUT-SOURCE-01 campaign. This is
an independent source-authority subquestion under the existing approved scope,
identified by read-only primary-source review after conservative resumption.
It does not resume the interrupted Q1–Q6 work or advance the dependent coupled or
scaling queue. Original activation03:40:33UTC, discovery cutoff12:30UTC and hard
deadline15:30UTC on2026-09-09 remain unchanged. Preserve Astra High Standard.

The documentation candidate 8f457c546e4d85fada73913efb900f921eaf6b1a remains frozen
in its own worktree for two complete gates and review publication. Add this work
only under the nested progress-01 documentation/experiment directories. No earlier
source, evidence, checker, M1, canonical contract or operational setting may change.

Question: given already accepted immutable valid records, how does optimistic
collection trade repeated collection work against the append waiting introduced
by a sealed collection window? Correct registration, input validity, ordering and
boundary association are explicit premises, not claims established by this model.

This comparison may establish finite traversal work, local unchanged-boundary
checks, and postponed append accounting. It cannot establish independently proven
source completeness, accepted attestation, publication currentness, allowance
release, physical recovery or any deferred Q1–Q6 conclusion. No production store,
language, framework, runtime migration or authority policy is selected.

Use only the original valid source streams named success, ambiguous,
prior-unresolved and later-start-only, constructed by the unchanged ee_cases.unsigned
factory. Retain their full original record bytes, intent/admission and provenance
hashes. No record mutation, foreign caller, identifier substitution, type alteration,
credential operation or external target belongs to this domain. Original attempts
remain1–2 and record inventories2–4; no larger original admission is invented.

The original A6/B6 requests against pool10 and wire event lengths1,2,1,2 remain
immutable inputs. All A6 stays held in this progress relation; it grants no allowance.
The unchanged historical gates continue to exercise the complete original event
flow and both cursor units. This new record-traversal metric supplies no additional
wire-flow or full-composition coverage. Preserve all six obligations and27 rows.

Conceptual service actions, identical for both alternatives:

- O offers the next original valid record, once, in its original order. The offered
  cursor is independent of visible length. The record stays pending until serviced;
  once all records are offered, O is idle. Record0 starts both offered and serviced.
- A services at most one oldest pending append when that alternative's window is open.
  A closed sealed window postpones the request without deleting or rejecting it.
- C services collection: open a capture; read one record ordinal; then perform a
  local unchanged-count check. This local check is not an attestation/publication.
  Each C opportunity performs exactly one of those transitions.

Optimistic collection leaves append service enabled. A completed traversal whose
captured count differs from the visible count incurs a recollection. A successful
local check records that count and idles until visible state advances.

Sealed collection holds its current window while reading/checking. Completing that
window reopens append service. An idle collector must not immediately reseal the
same already checked count; it starts another window only when visible state changes.
Seal ownership and crash recovery are premises/residuals, not implemented protocols.

State and measurements must retain visible prefix length, ordered pending requests
and their offer steps, captured length, next read ordinal, window/collector phase,
last locally checked count, per-original-record read counts, completed traversals,
invalidated traversals, actual retry starts and append waiting in scheduling steps.
Both alternatives see the same offered records and service opportunities. Differences
in how many appends have been serviced are measured, not normalized away.

Increment one shared logical action clock on every O/A/C action, including idle
actions and postponed append service. An O action stamps its newly offered record
with the incremented clock. Completed waiting is service_step minus offer_step;
outstanding waiting is current_step minus offer_step. Count postponed A opportunities
separately. This clock measures scheduling steps, not physical time or network latency.

Count a completed traversal at its final check. A failed local count check increments
invalidated_traversals and marks a retry needed; only a later C that opens a new
capture increments retry_starts. A new capture after a successful earlier check is
a capture start, not a failed-check retry. Retain every per-record read count so
repeated work remains observable under either reason for a new capture.

For each alternative require visible_count + pending_count = offered_count, with
the exact original visible FIFO prefix and pending suffix. Sum of per-record read
counts equals read work. The quiet-suffix endpoint must have all N original records
serviced, no pending work and last locally checked count N. These are conditional
bookkeeping properties, never source validity or accepted publication conclusions.

Initial preregistration: four valid streams, initially one visible record, every
word of length6 over O/A/C, then a deterministic quiet suffix. In that suffix offer
any remaining valid records, then provide R=(N+1)(N+2)+1 rounds of A followed by C,
where N is the original record count. Do not call the arbitrary prefix fair.
The suffix explicitly supplies collector and append service after all offers finish.

Proposed suffix bound, to challenge independently before execution: at most N+1
collection cycles remain, each needing at most N+2 collector opportunities; after
a sealed cycle opens, the next A opportunity can service a pending append. The
extra round covers final service/idle accounting. Whether this bound is sufficient
is a research question until the independent relation and finite results establish
it for the declared domain. It is not an unbounded or wall-clock liveness proof.
The independent conceptual challenge found this bound conservative: successive
captures have strictly increasing counts, since a failed check requires source
advancement and a successful check idles until advancement. This bounds collection
cycles over the stipulated finite input, without asserting correctness of an
implementation. The suffix is one deterministic bounded service continuation;
it is not a claim about every fair continuation.

Use independently implemented unified and separated representations of the paired
optimistic/sealed state, plus an independent full transition relation. Shared code
may supply only immutable inputs, encodings and schedules. Compare exact reachable
graphs and all terminal metrics, not only summary hashes. A simple exploration upper
bound is four times the full ternary prefix tree plus729 quiet tails of at most
66 actions per stream, below200000 states per representation before optional checker
controls. Actual state/edge counts and any remaining frontier must be recorded.

Positive witnesses must show an optimistic recollection, a postponed sealed append,
and quiet-suffix completion with every offered original record retained and serviced.
Four accounting controls distinguish an omitted read count, omitted completed
append-wait measurement, incorrect nonnegative wait arithmetic, and a discarded
pending offer. The independent relation also checks exact initial values and every
field of the reporting projection;
they test this measurement relation, not any deferred admission/attestation predicate.
Retain failed and superseded attempts, including an insufficient suffix bound or
resource exhaustion. No finite unfinished prefix establishes unbounded starvation.

Sources must be committed before admitted execution. Construct a versioned explicit
source/input manifest and resource runner first:500000 states/representation,
600seconds,2GiB,256MiB artifacts, no model network, one owned model process. The
currently running historical gate has priority; no new model may run concurrently.
At most four read-only workers, ten active agents, twenty minutes/packet, no nested
delegation or worker writes. Check usage every15minutes, checkpoint every20minutes,
and preserve the existing single-reset authorization/ledger without new spend.

Two complete final gates and two independent exact-candidate reviews remain required
before normal non-force draft review publication against verified master. The gate
pg_check.py --candidate FULL_HASH verifies all18 frozen predecessors and25 unchanged
regressions, regenerates exact original input bytes, and reproduces the complete
results and graphs. No model run or result is admitted by this document alone.

The full gate always enforces the original amended deadline. It has no implicit
historical mode that revives expired campaign authority. A future expressly
authorized enclosing gate can reproduce this slice's prepare/explore commands
under its own recorded context and containment, retaining fresh replay evidence;
it must not recursively call this full wrapper or change this slice's recorded clock.

Primary-source basis: Kung–Robinson §§1,3.3–4 distinguish reading, final validation
and repeated validation failure; Chandy–Lamport §§2,3.3 state delivery/scheduling
assumptions for snapshot termination. Applying these to this finite work comparison
is a conditional design inference, not a correctness theorem from those papers.
[Kung–Robinson](https://www.eecs.harvard.edu/~htk/publication/1981-tods-kung-robinson.pdf),
[Chandy–Lamport](https://lamport.azurewebsites.net/pubs/chandy.pdf).

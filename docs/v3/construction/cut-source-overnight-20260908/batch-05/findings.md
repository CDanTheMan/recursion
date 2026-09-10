# Semantic signed-record findings — 2026-09-09

The semantic relation repairs the retained initialized publication prefixes and
some lifecycle examples without rewriting either model's records. It does not
establish full visible correspondence. Source freshness and the public action
surface remain separate obstacles, now isolated by initialized certificates.

| Selected trace family | Cases | Every paired transition related | Complete visible correspondence |
|---|---:|---:|---:|
| Original success/failure prefixes through first reconcile, both units | 4 | 4 | 0 |
| Canonical source traces with explicitly declared Q schedules | 104 | 62 | 0 |
| Combined retained evidence | 108 | 66 | 0 |

The original prefixes contain 80 paired operations with related prestates,
successors and visible responses, plus 32 unmatched source events. Original Q
suffixes, including the second reconcile, are listed and not claimed covered.

Across all 108 traces there are 2700 source-event occurrences: 1772 paired and
928 unmatched. Of the paired occurrences, 1610 have related prestates, successors
and responses; 1612 have related successors and responses alone. There are 114
prestate gaps, 152 successor-state gaps and 124 response gaps; these categories
overlap. Forty-two response gaps occur at related prestates, including eight with
related successors too. The other 82 occur after the histories already diverged.
Each of the 42 negative cases has a retained first literal-decision obstruction.

These are selected, overlapping trace occurrences in two units, not a full graph
exploration, runtime frequencies or independent defect counts. Of the 66 wholly
paired matches, 26 establish no incarnation pair and 38 contain successful
publication. The headline count is not a publication success rate. All source-only
operations retain their actual responses; they have not been hidden as stutters.

## What the record relation establishes

Each original signed envelope validates over its own full body. Incarnation pairs
are scoped, injective and established by earlier paired attestation/restart events.
Each receipt keeps the digest of its own actual envelope. All other identity,
content, lineage, revision and receipt fields remain exact. The differently signed
records and receipt digests remain present in the evidence.

In restart-recollect, all 15 paired transitions match in each unit. S0/Q1 becomes
S1/Q2 on restart; recollection, staging and publication succeed. Thirteen source
events per case remain unmatched.

In publication-duplicate-retired, all 27 paired transitions match in each unit.
After two publications, retirement, source/authority restart and permit revocation,
duplicate retry returns the first retired generation's durable receipt. It increments
the receipt-read count without changing selected publication, revision, store or
receipt journal. The following conflicting retry returns E-IDEMPOTENCY-CONFLICT.
Both original receipt digests validate; 16 source events per case remain unmatched.
These checked histories are examples, not general lifecycle theorems.

## The remaining freshness distinction

The twin-publication certificate compares pending-success with
append-between-collect-and-publish in both units. Their complete Q prestates are
identical before the same pub-commit@10 call. Common S data is also identical,
but source revisions are 5 and 7 while both attestations/staged bindings retain 5.
S returns pub-commit:ok in the first history and source-boundary-stale in the second;
Q returns pub-commit:ok in both.

The overall target profile dictionaries have different later suffixes. The certificate
checks equal current action ordinal, unit and outcome and anchors a scoped AST/source
argument: the original publication branch does not read that suffix. This is a
source-backed necessity argument plus checked retained facts, not arbitrary-program
noninterference or an unrestricted refinement impossibility proof.

A record relation alone cannot make this fixed target decision equal both literal
source decisions. A richer target interface or justified translation would need to
carry the freshness distinction. It would also need to retain all source responses.

The reconciliation certificate similarly retains S's stale selected-source rejection
after a new attempt while Q settles. In the publication-source-race certificate,
both prestates and successors are related, yet S returns source-boundary-stale and
Q returns E-PAUSED. Exact rejection precedence remains visible. The oracle-bypass
trace has no unmatched source events, but source:success is rejected by S and accepted
by Q; declaring the action surface remains necessary.

## Validation boundary

The supplemented focused C run passed all 108 cases as checked comparisons and
detected 17 checker-corruption controls, using 4688 combined state visits per
representation against a nonrefundable 10000 reservation. Certificates add no model
steps. Both original inclusive/split reducers and independent auditors check every
replayed step from each side's own initialization. Normalized and recursive record
comparisons have separate structure and share signature/receipt predicates.

Three successful focused runs and their separately owned receipt audits remain
retained. No owned execution failure or automatic safeguard rejection occurred
before acceptance. Prospective review corrected causal binding, type checks,
prestate accounting, precharged visits, module closure and auxiliary ledger checks;
these corrections are recorded, not represented as runtime test failures.

Publication requires two complete 48-command gates on one clean final candidate,
two successful receipt audits and two independent final reviews. Until external
completion records those outcomes, they are pending. Historical models, inputs,
graphs, clocks and closing evidence remain unchanged. The parent goal, full visible
refinement, original-Q-profile reachability for translated schedules, whole-path
composition, fairness, source truth, physical recovery, Q1-Q6 and runtime integration
remain open. No runtime, language, store or provider is selected.

# Campaign B: conditional workload bounds — 2026-09-09

The admitted workload study passes 184482 states per representation across nine domains:
N=2,3,4 crossed with AC,AAC,ACC. Equal-count original N4 streams share a scheduling
domain. All original AC graph hashes reproduce exactly, both reducers agree, all edges
and metrics pass the independent relation, five controls are detected and frontier is 0.

Every original H6 word is paired across service families. Results retain 729 matched
prefixes per comparison and explicit witnesses. Counts are descriptive, not probabilities.
A/C/O each cost one modeled tick; AC periods cost 2 while AAC/ACC cost 3. These are
conditional service schedules, not physical throughput measurements.

| N | Period | Maximum joint completion ticks after suffix start | Proven conservative bound | one read range | drain read range |
|---|---|---:|---:|---|---|
| 2 | AC | 12 | 16 | [2, 3] | [2, 3] |
| 2 | AAC | 18 | 24 | [2, 3] | [2, 3] |
| 2 | ACC | 9 | 24 | [2, 3] | [2, 3] |
| 3 | AC | 22 | 28 | [3, 6] | [3, 6] |
| 3 | AAC | 24 | 42 | [3, 6] | [3, 6] |
| 3 | ACC | 17 | 42 | [3, 6] | [3, 6] |
| 4 | AC | 34 | 42 | [4, 10] | [4, 7] |
| 4 | AAC | 39 | 63 | [4, 8] | [4, 7] |
| 4 | ACC | 27 | 63 | [4, 10] | [4, 7] |

For each policy, strictly increasing captures give at most N starts, N checks and
N(N+1)/2 reads. At most N-1 append services remain. Every incomplete full period
containing A and C performs at least one useful operation, giving U=(N-1)+2N+N(N+1)/2.
With S=max(6,last-offer tick), completion is bounded by S+len(period)*U and record i
waiting by S-offer_tick[i]+len(period)*U. The registered R exceeds U for all three N.

Observed per-record maxima and attaining traces are in B-results.json. For N4, one
has maximum record waits [0,12,18,26] under AC, [0,14,15,25] under AAC, and
[0,11,15,22] under ACC. More append opportunities can increase some waits while
decreasing others; collector opportunities also matter because they release seals.
These different-prefix maxima alone do not prove pairwise dominance; the separate
matched-prefix comparisons supply the corresponding actual shared-prefix evidence.

All offers are finite, source data are stipulated valid, seals retain unchanged-count
idling, and service follows the declared suffix. Arbitrarily long scheduling gaps,
infinite arrivals, physical latency and source truth do not inherit these guarantees.

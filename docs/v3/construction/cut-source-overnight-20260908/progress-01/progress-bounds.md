# Conditional progress bounds and work comparison — 2026-09-09

These are independently reasoned claims about the reachable reducers at
candidate a8fda63a9c1ce7db4827748e1f8734d4e5b5e9f1. They are distinct from
finite enumeration. Inputs are stipulated accepted immutable records; visibility
only grows, collection cannot restart midway, and actions perform their specified
transitions without crashes or resets. They establish no source-validity result.
The admitted original inventories remain N=2,3,4.

For either policy, capture sizes strictly increase. After a failed capture of k
records, visibility exceeds k and never decreases. After a successful capture,
checked=k and the opening guard prevents another capture until visibility exceeds
k. Retry bookkeeping does not bypass that guard. Consequently at most N captures
start, including any unfinished capture. Each capture reads each of its ordinals
at most once, so total read work is at most N(N+1)/2 on every finite action word.
No fairness assumption is required for this work bound.

The bound is attainable. Complete a capture at each successive visible size k,
using C^(k+2), and place OA between successive captures. At N=4, the action sequence
`CCC OA CCCC OA CCCCC OA CCCCCC` makes both policies read exactly10 records in
captures of sizes1,2,3,4. This is a manually derived construction, not a new run.

Suppose all finite offers eventually occur and future A and C opportunities each
occur infinitely often. Optimistic append service eventually drains the finite
inventory; after its last change, collector service completes any stale capture
and a capture at N. Each sealed capture also finishes after finitely many C
opportunities. Its final check releases the seal; intervening C actions idle at the
already checked size, so the window stays open until pending A service advances it.
Repeating this finitely many times services and checks N. These sufficient
assumptions imply eventual completion, but provide no uniform scheduling-step or
wall-clock latency bound and are not necessary conditions.

A separate manually derived N=4 trace shows why optimistic collection has no
universal advantage in total reads. Use `COACCOACOACCCAAC`, followed by six C actions.
This16-action prefix is outside the preregistered H6 enumeration.

| Steps | Optimistic | Sealed |
|---|---|---|
|1–5, COACC|Read capture1; invalidate at visible2|Postpone append; read and check1|
|6–8, OAC|Advance to3 and capture3|Advance to2 and capture2|
|9–13, OACCC|Advance to4 and read3 records|Postpone append, read2 and check2|
|14–16, AAC|Invalidate capture3|Service through4 and capture4|
|17–22, CCCCCC|Open, read and check4|Read and check4, then idle|

Both end with every record serviced and checked. Optimistic capture sizes1,3,4
cost8 reads, two invalidations and two actual retries. Sealed sizes1,2,4 cost7 reads
and two postponed append opportunities. This refutes universal optimistic read-work
superiority; it supplies no average-case comparison or reverse universal dominance.

The read-only coupled_scaling_challenge reviewer independently checked both proofs,
the trace and the tight-bound construction without model execution. Exact final
reviews must still assess these claims with the final candidate. No additional
finite profiles, source-completeness claims, general protocol proof, architecture
selection, formal freeze or Q1–Q6 resolution follows from this reasoning.

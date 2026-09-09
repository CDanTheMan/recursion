# Campaign C: two-service handoff — 2026-09-09

The new policy passes all declared finite checks, but it offers no read-work or
matched-record waiting advantage over drain in the original N<=4 inventory. This is
an informative conditional result, not an instruction to select a runtime policy.

Both independent three-policy implementations agree across 184482 states per
representation. Their node and edge projections reproduce all B graphs exactly.
All fields, metrics, schedule choices, projected predecessor transitions, conditional
bounds and nine negative controls pass. A/B reproduce unchanged first; combined B/C
state count is 368964 per representation. The owned run took 33.703 seconds, peaked at
542314496 bytes and cleaned up all owned processes without errors.

| N | Period | Distinct complete states | drain fewer reads / equal / two fewer |
|---|---|---:|---|
| 2 | AC | 133 | 0 / 133 / 0 |
| 2 | AAC | 133 | 0 / 133 / 0 |
| 2 | ACC | 98 | 0 / 98 / 0 |
| 3 | AC | 356 | 0 / 356 / 0 |
| 3 | AAC | 356 | 0 / 356 / 0 |
| 3 | ACC | 301 | 0 / 301 / 0 |
| 4 | AC | 452 | 314 / 138 / 0 |
| 4 | AAC | 452 | 171 / 281 / 0 |
| 4 | ACC | 411 | 279 / 132 / 0 |

Counts refer to distinct complete states, not probabilities. The full per-record
maxima and attaining traces are retained in results.json. For N4, two's last-record
maximum wait is 19 under AC,24 under AAC and 18 under ACC; drain's corresponding
maxima are 11,13 and 12. These maxima alone are not the dominance proof: every modeled
state also checks matched-record waiting, and the following separate argument explains
why the restriction on inventory matters.

For N<=3, after any release at visible>=1 at most two records remain unserved. If
two-service exhausts its two-unit budget, no original record can remain pending.
Its extra opening condition therefore never permits a capture that drain would refuse.
Their original policy projections agree on every word under the stated semantics.

For N4, their first projected difference can only be two-service opening at visible 3,
offered 4,budget 0 while drain idles. The prefix OOOAAC reaches precisely that case.
Before the difference, capture histories and serviced-record waits are identical.
All four records have now been offered; no future arrival can reverse their phases.
Drain serves the final record no later. Two-service must finish capture 3 before that
record can be serviced, then capture 4; drain's only subsequent capture is 4. At joint
completed endpoints, two therefore costs exactly three extra reads after divergence,
or zero if no divergence occurs. Drain's matched-record waits are no greater throughout.

Initial/refill budget 2, unit FIFO service, dynamic backlog testing, N<=4, seals and
unchanged-count idling are essential premises. Budget 0 never blocks further A service;
it permits resealing at a C opportunity. This is not a hard cap on append throughput.
Partial read counts can have a different ordering, and larger inventories or infinite
arrivals are outside the proof. No such domain is added here.

One and two remain incomparable in general completed read work and individual waiting:
for N3, two equals drain, so the previously established one/drain counterexamples
transfer by that equivalence. This is a proof consequence, not a new unregistered run.

# Counterexample and assumptions findings — 2026-09-09

The older 22-action example is valid but not shortest. Under the exact original
unit-action, one-initial-record and joint-completed-endpoint contract, the reviewed
manual proof gives no completed reversal for positive N<=2 and shortest length
3N+8 for N>=3. The general claim is a symbolic argument with an attaining construction,
not exhaustive exploration or a machine-checked general theorem.

| Original records | Actions | Optimistic / sealed reads | Capture histories |
|---|---:|---:|---|
|4, older example|22|8 / 7|1,3,4 / 1,2,4|
|3, new shortest example|17|6 / 4|1,2,3 / 1,3|
|4, new shortest example|20|7 / 5|1,2,4 / 1,4|

The mechanism is batching: sealed collection delays append service, then services
its backlog before opening another capture. It skips an intermediate capture that
optimistic collection has already started. Both policies' completed read work must
be compared; an unfinished collector cannot win by omitting remaining work.

The proof uses a common first capture and strictly increasing completed capture
sizes. An optimistic read disadvantage needs at least three captures, hence at least
N+9 collector opportunities, N-1 offers and N append opportunities. The constructed
word attains their sum. See derivations.md for every premise and the construction.

One guard matters for more than work accounting: the sealed collector's requirement
to idle at an unchanged already checked count. Removing only that guard lets
`OO+(CCAC)^7` hold N=3 visibility at 1 with two pending appends and seven reads,
exceeding the original bound 6. The unchanged collector completes on that same word.
The full cycle-state equations were checked at each repetition. A separate induction
extends the recurrence indefinitely; a finite trace alone cannot establish starvation.

Fairness must name the action whose progress is required. Our recurrence supplies
infinitely many A and C opportunities, yet the actual sealed append is enabled only
between check and reseal. Weak fairness does not force a step that is repeatedly
disabled; strong fairness of that append step would exclude this recurrence. This
applies Lamport's distinction to our explicitly defined transition; it does not claim
a TLA+ verification. [Lamport, PlusCal tutorial session 9, section 5](https://lamport.azurewebsites.net/tla/tutorial/session 9.html).

Validation: the admitted run reproduced the predecessor's complete original input
bytes, accepted result and all four graph hashes. Every new original-policy witness
agreed between both reducers and the independent transition/metric relation. Necessary
capture-history certificates cover original N=2,3,4; they deliberately overapproximate
reachable histories and do not enumerate longer schedules. The new run used 4.109
seconds and 135,368,704-byte job peak with successful owned cleanup. All 247 retained
file hashes and 236 source snapshots were verified. Two earlier adapter failures are
retained: Windows snapshot path length, then Python tuple versus JSON-list comparison.

Astra High Standard remains unchanged. No reset, new metered spend, operational
configuration, publisher script, source-validity predicate or original source record
changed. Q1–Q6 remain deferred. Original history, M1, A6/B6 pool10, four-event flow,
six obligations and 27 rows remain intact. This local packet is not a full historical
publication gate. The branch remains local pending the separate complete publication
requirements; no old interrupted or expired full-pass receipt is promoted to success.

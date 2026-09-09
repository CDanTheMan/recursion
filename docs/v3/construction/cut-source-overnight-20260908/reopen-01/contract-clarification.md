# Collection and publication contracts — 2026-09-09

This is a specification clarification supported by primary-source reading, not a
new implementation result or production architecture choice. Existing modeled
support remains confined to the first slice's declared finite profiles. Q1–Q6 in
work-inventory.json remain deferred; this document does not resolve them.

| Claim | Required campaign obligation | What it does not establish |
|---|---|---|
| Complete at boundary B | The collection contains every registered original input and every admitted record through the declared authoritative boundary, with its required mapping. | Events never registered or admitted; currentness after B. |
| Consistent snapshot | Recorded state satisfies the relevant causal and channel-state assumptions. | A latest source boundary or necessarily a state that physically occurred during collection. |
| Current at publication P | Validation of B and selection of the publication preserve their relationship at one defined atomic point. | Currency when the response is received or when a reader later uses it. |
| Current at later use U | The existing use/reconciliation rule independently relates the installed publication to the then-current source boundary. | Physical truth, recovery or permission to release an uncertain reservation merely because data were once current. |

Chandy–Lamport §4, Theorem1 places a recorded snapshot in an equivalent reordered
computation. Its consistency result does not promise the most recent state.
Section2 assumes ordered, error-free channels with finite message delays; §3.3
states conditions for snapshot termination. These are assumptions of that paper,
not guarantees supplied by this campaign's local model.
[Original paper](https://lamport.azurewebsites.net/pubs/chandy.pdf).

Herlihy–Wing §2.2 defines linearizability through a legal sequential history that
respects real-time precedence of nonoverlapping operations. Applied here as a
design inference, "current at publication" needs an identified atomic publication
point and a declared set of source updates ordered against it. A concurrent update
may be ordered before or after publication; an update completed before publication
begins must precede it. This does not imply newest-at-response data.
[Original paper](https://www.cs.cmu.edu/~wing/publications/HerlihyWing90.pdf).

The authority boundary must cover registration changes as well as record appends.
This is a campaign-specific obligation: an unchanged record inventory alone says
nothing about whether the registered attempt set has grown. The original source
revision, source incarnation, literal fixture version, publication revision, reader
pin, quota, worker lifetime and uncertain-effect reservation remain separate state.
The exact object bound by attestation is still Q1; none of these definitions silently
settles its deferred implementation question.

| Ordinary concurrency condition | Optimistic collection | Sealed collection window |
|---|---|---|
| Source advances during collection | Collectors can finish reading a historical boundary; current publication may require recollection. | The sealed window stays fixed if later appends are excluded from it. |
| Continuing benign appends | Repeated validation failure can prevent publication without violating safety. | Holding the relevant source fixed shifts waiting to writers; progress needs a closing/reopening rule. |
| Appends accepted into a later window | A later boundary supersedes the captured boundary under the declared currentness contract. | Earlier-window completeness remains historical; a seal alone cannot authorize globally current publication. |
| Collector interruption | No progress claim without scheduling and retained-state assumptions. | A seal requires specified ownership, recovery and eventual reopening; these remain unimplemented here. |

Kung–Robinson separates optimistic reading, validation and writing (§1), discusses
repeated validation failure and starvation (§3.3), and keeps final validation and
writing indivisible in its concurrent-validation construction (§4). Its discussion
of excluding writes supports the progress tradeoff above, not the details of our
proposed sealed-window alternative. Consequently neither alternative earns an
unbounded liveness claim from the present finite evidence.
[Original paper](https://www.eecs.harvard.edu/~htk/publication/1981-tods-kung-robinson.pdf).

As a concrete published API distinction, etcd's KV guarantees specify atomic
ordering consistent with real time, while watch delivery may lag and is expressly
not linearizable. A notification boundary can describe delivered historical
coverage without establishing an atomic current-state selection. This is a semantic
example, not a recommendation to select or install etcd.
[API guarantees](https://etcd.io/docs/v3.7/learning/api_guarantees/).

The consequence for the six original obligations and27 trace rows is no new
coverage. Actual A6/B6 each request6 from pool10; original attempts1–2 and event
lengths1,2,1,2 remain unchanged. Receipt replay, source currentness, literal
classification and reservation release remain separate responsibilities. Source
truth outside admitted events, physical durability/recovery, orphan reclamation,
unbounded progress and runtime/common-writer integration remain residuals.

Sources consulted2026-09-09. Independent read-only primary-source packet completed
by source_protocol_research; integration into this candidate still needs review.

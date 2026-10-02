---
title: Broker protocol freeze blockers and native chaos specification
source-prompt: FU-05 — broker protocol and native chaos
session: Codex Dot follow-up research — specification only, target experiments NOT run
retrieved: 2026-10-02
status: research-evidence-not-a-decision
verification: not independently verified by Recursion; target experiments not run
---

# Broker protocol freeze blockers and native chaos specification

FU05 research report for the Recursion Owner and independent reviewer

Research cutoff 1 October 2026 UTC • Prepared 2 October 2026 UTC • Decision status HOLD • Revision 1

## 1 Decision and scope

The broker protocol is not ready to freeze. This report narrows all four blockers to named decisions and falsifiable fixtures, supplies proposed normative wording, and preregisters the Windows and Linux chaos campaign. None of those fixtures was executed. The report is decision evidence, not implementation acceptance.

The most important unresolved dependency is snapshot materialization. The supplied handoff does not identify an already-ratified contract that turns SNAPSHOT.snapshot_digest into verifiable bytes at a specific cursor. Public protocol standards cannot establish an internal ratification. A digest alone does not define a projection, its serialization, its cursor binding or how to retrieve its bytes. The named missing input is SM-01, defined in section 4. Until it is supplied and independently checked, snapshot recovery remains unverified.

The other blockers are narrowed as follows. V-01 requires the Owner to choose an exact-only compatibility envelope or authorize a new negotiated major. C-01 requires a durable stream-incarnation and rollover contract, including its mapping to canonical event identity. A-01 offers exact ACK, credit and RESET wording for ratification, with duplicate, backward, ahead-of-send, reconnect and reset races made explicit. Completing these documents alone will not close the freeze: two independent implementations must pass the same reviewed corpus and the native platform campaign must pass within its declared threat model.

A current-source correction matters at the separate tool boundary. The current MCP core revision found in official sources is 2026-07-28, not 2025-11-25. It uses per-request version and capabilities, with modern and legacy interoperability rules. SDK major version 2 is not a protocol revision. Numerical buffer ceilings below are local policy proposals, not values mandated by MCP. [S01–S07]

The latest Owner clarification takes precedence over the inherited brief: Hermes is retired. Recursion v3 is an Owner-controlled standalone harness and a wrapper/orchestrator of other harnesses, supporting native, upstream-only and combined execution. The protocol evidence must therefore cover both native process management and upstream harness boundaries without promoting an adapter or upstream result into authority. This clarification changes the product framing; it does not authorize runtime tests or implementation in this research.

This report selects no renderer, multiplexer, GUI toolkit, IPC library, serialization library, cursor store, snapshot format or retention engine. It does not select a default language or runtime. The fixed detachable-terminal ruling remains intact: terminal bytes are data, attaching a view creates no actor or effect, and a view or adapter never gains authority. No target process, socket, model checker, native fixture or broker implementation was launched or operated for this research. Document construction and document-quality checks are separate from the prohibited target experiments.

### Reading and decision map

Sections 3–6 contain the four freeze blockers and proposed wire semantics. Sections 7–9 cover framing, bounded buffers and exact recovery. Sections 10–12 preregister containment chaos and the limit of the containment claim. Sections 13–15 define the separate MCP boundary, command receipts and Stop. Sections 16–19 provide recommendations, Owner decisions, local execution handoff and the completion gate. Section 20 is the source and freshness register.

## 2 Evidence discipline and inherited facts

This is ordinary public-source research and specification work. No target or local Work/Codex execution session was used, and no native test result was generated here.

Use these labels throughout: SD means source-documented in the cited primary source; LO means locally observed with retained raw evidence; IN means an inference or a proposed design/policy; UV means unverified or evidence absent. Confidence measures support for the stated claim, not probability that an unrun implementation will pass. High confidence in a documented API does not confer platform qualification.

All proposed MUST, MUST NOT and SHOULD clauses are a candidate specification called BP-CAND-20261001. They are not quotations from DS23, an adopted broker major, or a ratified product contract. Unless a paragraph explicitly says SD or identifies the supplied handoff, its proposed behavior is IN. Its implementation status is UV. The word PASS is reserved for a future independently reviewed result with its evidence bundle.

The supplied handoff reports one prior bounded Windows observation: a child escaped during a create-suspended-then-associate gap, while creation-time Job listing closed the tested gap. Classification here is handoff-reported LO, raw artifacts unavailable, independently unverified in this report. It does not prove a current build, full descendant capture, Linux behavior, slow-view isolation or operational framing. The experiment's process-creation details and fixture identity are missing, so it must not be generalized into a claim that every suspended-creation pattern necessarily allows execution before resume.

No content of CONTROL_PLANE.md, GAPS.md, the source-lane reports, private repositories or alleged ratification records was available beyond the self-contained handoff. Their names establish dependencies, not that their unseen contents were checked. No claims of repository cleanliness, original lane reproduction or acceptance are made. The local document privacy scan covers the new deliverables only.

### Cross lane interface boundaries

FU03's proposed RCV1 deterministic-CBOR container is a test interchange candidate. Its bytes are not the broker's JCS JSON wire bytes. Kernel semantic bytes, RCV1 envelope bytes and broker frame bytes must have distinct layer labels, schemas, expected results and digests. A JCS test case can be an opaque byte string inside the test container without converting JCS numeric semantics into CBOR numeric semantics.

FU03 proposes event identity as aggregate_id plus ordinal plus event_digest, with separately domain-tagged state, event, packet, command and projection digests. FU05 consumes that as a candidate interface only. Rendered equality, database row IDs, log byte offsets and terminal positions must not become canonical event identity. The approved mapping from a broker cursor to a projection cut and canonical event identity remains part of SM-01 and C-01.

FU04's candidate platform result key is profile_key, fixture_id, fixture_version, variant_id, cutpoint, failure_domain and contract_digest. Its qualification values are qualified, rejected and unknown; unknown is displayed as Unqualified. FU05 records transport_closed, client_disconnected, process_exited, containment_empty and execution_settled independently, including unknown. A missing notification is not a negative observation. Neither candidate interface is represented as already ratified.

## 3 Blocker one version admission

### V01 decision input and costs

Exact-only m1b-broker/1 can safely reject versions it does not implement if rejection occurs before command admission, state allocation beyond the bounded handshake, or effects. A clean refusal is a safe failure, not an interoperability success. Its costs are operational: detached clients left behind by daemon upgrades cannot reconnect; old views cannot discover a mutually supported subset; rolling upgrades need a coordinated compatibility window; unknown future fields cannot be safely interpreted by guesswork. A common version string also cannot protect against two implementations silently using different schemas or semantics.

V-01 is a signed Owner decision record containing the permitted client/server support matrix, whether mixed versions must interoperate, allowed outage during upgrades, exact schema identity rules, minimum refusal semantics, downgrade policy, and which deployed clients are supported. If the Owner requires exact-only /1, preserve the existing approved envelope unchanged. Do not silently add fields that strict /1 decoders reject. Publish the exact accepted wire/schema package with a content digest and require every /1 build to conform to it. If that package is absent, exact-only remains a HOLD too.

A new negotiated major is a competing option, not selected here. It needs a bounded bootstrap grammar that is independently versioned or immutable; there is otherwise a circular dependency in negotiating the grammar needed to parse negotiation. The new major must not be advertised as /1 and must not reinterpret bytes from an old /1 client.

### Proposed negotiated major requirements

HELLO declares an explicit supported-major set, supported minor intervals within each major, schema epoch and digest combinations, required capabilities, optional capabilities, maximum record and window ceilings, and a client nonce. WELCOME selects one actual major/minor/schema tuple, returns the selected capability set and ceilings, binds the nonce to a fresh delivery epoch, and identifies the stream. An interval means every listed revision is implemented; gaps require separate intervals or an explicit set. Capabilities do not authorize effects. An unknown required capability, nonintersecting version, incompatible schema, or inability to support an atomic minimum record produces typed refusal.

The canonical schema digest must cover the semantic rules and referenced schemas as a content-closed package. A JSON schema file digest alone cannot distinguish changed ACK semantics or changed digest preimages. Use an approved schema registry or an exact shared digest; do not equate the same epoch integer with semantic compatibility. Optional unknown fields are ignorable only where the chosen schema explicitly permits them. Required features may not be silently dropped to gain admission.

Typed pre-admission refusal has the closed fields kind=REFUSE, bootstrap_version, code, retryable, supported_versions, supported_schema_ids, missing_required_capabilities and bounded diagnostic_code. The proposed codes are UNSUPPORTED_VERSION, UNSUPPORTED_SCHEMA, REQUIRED_CAPABILITY_MISSING, LIMIT_INCOMPATIBLE, MALFORMED_HELLO, ADMISSION_UNAVAILABLE and PEER_NOT_ALLOWED. Values absent by policy are represented explicitly as empty lists or null as the schema defines; refusal must not expose process IDs, account names, file paths or credentials. Refusal grants no command ID, execution lease or actor identity. The refusal record is bounded and then the connection closes. Before a valid bootstrap can be parsed, malformed bytes may yield close-only refusal evidence.

Negotiation must bind the transport's verified peer context and fresh nonce. A handshake transcript digest detects accidental disagreement; it is not authentication unless an approved authenticated mechanism binds it. These proposals do not add credentials or change security configuration.

### V01 decisive interoperability fixture

Run V-FIX-01 against two independently authored clients and two servers, using the reviewed version/schema matrix. Cover exact match, major mismatch, intervals with and without intersection, same version but incompatible schema, capability deletion, unknown optional field, unknown required field, malformed lengths, duplicate HELLO, WELCOME replay, refusal truncation and downgrade retry. Capture exact bytes, selected tuple, state allocations, command ledger and external-effect counter.

The decisive safety falsifier is any pair admitted under a shared version name that then disagrees on a command, receipt, ACK, reset or snapshot interpretation, or any side effect before admission. An unsupported pair cleanly refusing does not falsify safety. It falsifies adequacy only if V-01 requires that pair to interoperate or recover within its approved outage objective. A server crash or unbounded allocation while rejecting an unknown version also falsifies safe exact-only rejection. The negotiated-major option fails if it selects an unimplemented tuple, silently loses a required capability or allows stale WELCOME replay.

Status: narrowed to V-01 and V-FIX-01; neither an Owner decision nor a run result exists here. Confidence: high in this limitation, medium in the proposed design until interoperability evidence exists.

## 4 Blocker two snapshot materialization

### SM01 evidence that must be supplied

No already-ratified materialization contract can be named from the supplied evidence. Do not substitute RFC 8785, a store checkpoint, a renderer screenshot, a CBOR corpus convention or a newly invented schema. Those can contribute mechanics but cannot establish the product's approved meaning of SNAPSHOT.snapshot_digest.

SM-01 is the required ratification and byte-evidence package. It must include the contract identifier and immutable revision, Owner acceptance evidence, exact projection identifier and schema, cursor semantics, domain-separated digest preimage, serialization/encoding rules, and how bytes are retrieved or transferred without exposing storage internals. It must specify whether the digest commits to canonical bytes, transported bytes, chunk manifest or a root over chunks. It must define digest algorithm and encoding, empty-view behavior, duplicate/unknown fields, integer rules, compression boundaries, normalization policy, maximum materialized size, and behavior when that size is exceeded.

It must also define exact-cut consistency: which canonical event frontier the view represents; how multiple aggregates form that cut; how a snapshot is pinned while the writer advances; the lease or validity of bytes and replay tail; the mapping to canonical event identities; projection rebuild/version changes; disposal; and who independently verifies bytes. A returned URL or opaque handle needs a content-binding, permission, expiry and retrieval contract. The reference is data, not authority to fetch an arbitrary URI.

A storage-neutral contract can specify these semantic inputs and outputs without naming a store, snapshot format or retention engine. It still needs concrete bytes before a digest can be checked. If no contract was ratified, SM-01 must explicitly record that fact and seek an Owner contract decision; it must not be represented as recovered historical agreement.

### Proposed recovery state machine

The states are PRE_ADMISSION, READY_TO_RESUME, RESET_REQUIRED, SNAPSHOT_LOADING, SNAPSHOT_ACK_PENDING and STREAMING. Every connection has a fresh delivery_epoch. Within that connection every recovery attempt has a monotonically increasing reset_epoch. All data, ACK and credit messages bind both epochs; all stream positions bind stream_id, incarnation_id and sequence. Epochs identify protocol state and never confer effect authority.

HELLO carries the last locally verified cursor and associated materialization/schema identity or explicitly says none. WELCOME identifies the admitted contract and actual stream. If the server can prove a contiguous replay interval from the supplied cursor to a known frontier, it may offer that replay under credit. If it cannot prove continuity, including retention gap, unknown incarnation or schema mismatch, it MUST enter RESET_REQUIRED before any later EVENT is applied.

RESET contains a stable reason, reset_epoch, current stream identity, the earliest replayable cursor if known, and the proposed snapshot cut. Unknown retention floor remains null. RESET invalidates the old delivery's pending ACK and credit state. It does not erase canonical events, authorize a command retry or declare execution stopped. Once queued bytes cannot be retracted, client epoch validation prevents them being applied after reset. If the reserved control channel cannot deliver RESET, close the connection; reconnect must still discover the gap rather than infer it healed.

SNAPSHOT, possibly through an approved bounded chunk transfer, binds snapshot_id, materialization_contract_id, projection_schema_id, cursor, digest specification, total byte count and final verification evidence. The candidate deliberately does not define a snapshot format. The client stages bytes separately, verifies length and digest using SM-01, validates exact cursor and projection identity, and replaces the projection atomically only after every required check succeeds. No partial projection is acknowledged or rendered as current.

The client then sends ACK with ack_kind=SNAPSHOT, exact snapshot_id, digest, cut cursor and epochs. The server accepts it only against the offered snapshot and current recovery epoch, then opens the event frontier at that cut. A snapshot ACK is not an EVENT ACK and does not acknowledge unsent events. The client sends a separate initial CREDIT grant for event streaming. The first EVENT must be the immediate defined successor of the snapshot cut, with a canonical identity matching the approved mapping. A missing or altered event forces a new RESET.

If the replay tail vanishes while a snapshot is transferred, the server may finish the transfer but MUST NOT attach an unverifiable tail. It must issue a newer RESET and snapshot or refuse recovery under bounded retry policy. Holding the writer until a view catches up is prohibited. Repeated reset without progress must produce an explicit recovery-unavailable result and bounded retry/backoff; it must not spin or allocate unbounded snapshots.

### SM01 decisive recovery oracle

SM-FIX-01 starts with a literal reviewed snapshot and canonical event corpus. Execute HELLO → WELCOME → replay-gap detection → RESET → SNAPSHOT → SNAPSHOT ACK → CREDIT → EVENT. Two independent materializers must produce the approved bytes and digest for the identical cut; two independent consumers must reconstruct the same projection after replay. Neither implementation may serve as the other's oracle.

Inject a wrong digest, wrong cursor, valid digest for another projection, modified chunk, missing/duplicate/out-of-order chunk, truncated final chunk, decompression bomb if compression is approved, late ACK from the prior reset, changed schema, snapshot eviction, tail eviction, unknown incarnation and broker crash at each transition. A false snapshot ACK, event applied across a gap, digest accepted for the wrong cut, or writer blocked by snapshot retention is a hard failure. Correct rejection is not snapshot success. Without SM-01's literal bytes, the fixture is BLOCKED, not PASS.

Status: HOLD on missing ratification and materialization bytes. This is an evidence limitation, not a recommendation to select a new snapshot format.

## 5 Blocker three cursor incarnation and rollover

### C01 candidate identity contract

A bare integer cursor is insufficient to distinguish a new stream from an old process restart or wraparound. The proposed cursor is the tuple stream_id, incarnation_id, sequence. stream_id names the logical projection stream; incarnation_id is an opaque, durable unique identifier for one sequence namespace. sequence is a JSON integer in 0 through 2147483646. Zero denotes the approved initial snapshot cut, never an event. All cursors additionally bind the projection schema and materialization contract through the admitted stream contract.

This candidate reserves 2147483647 and never emits it as an event sequence. Before the next event would exceed 2147483646, the authority for stream metadata must durably establish the next incarnation and its predecessor link. Rotate at that boundary or earlier according to an approved threshold. Do not perform signed wraparound, modulo ordering or numeric comparison across incarnations. The logical canonical event ordinal is not forced to wrap with this projection sequence.

The transition record binds old incarnation, old final cursor, new incarnation, new starting snapshot cut, canonical cut identity and predecessor-transition digest. Establishing that record and the new namespace must be crash-consistent under a contract still to be ratified. A random identifier alone does not prove the incarnation is legitimate. The broker must resolve it through authoritative persisted stream metadata, and the client must verify the transition or take an authenticated RESET and a verified snapshot. A connection nonce prevents replay into the current delivery; it does not replace durable lineage.

Ordinary broker restart preserves incarnation if stream metadata and sequence continuity can be verified. If continuity cannot be proved, the broker must allocate a durably recorded new incarnation and require RESET, or refuse service. It must not reset sequence to zero under an old incarnation. State restoration from backup must not reuse a previously live incarnation/sequence pair for different data. A forked or split-brain lineage is a HOLD requiring canonical reconciliation, not last-writer-wins cursor selection.

Disconnected clients reconnecting with old incarnations receive either a verified retained transition chain plus an approved recovery path, or mandatory RESET. Old ACK, credit and command receipts cannot be reinterpreted as current merely because their sequence matches. A change of projection schema likewise requires explicit contract handling, never automatic cursor reuse.

### C01 decisive rollover fixture

C-FIX-01 uses a synthetic stream seeded at 2147483644, then records events through the boundary. This is a test-state injection specification; no billions-of-events run is required. Expected old-incarnation events stop at 2147483646, followed by a durable rotation/recovery path before any further delivery. The next incarnation may have a zero snapshot cut and event sequence 1, only if the approved mapping says so.

Crash before transition persistence, after persistence but before exposure, after exposure but before client ACK, during snapshot install, and after old state restoration. Reconnect a client holding the old final ACK; replay a stale WELCOME and ACK; simulate duplicate incarnation IDs; expose competing transition records. Any reuse of one cursor for different logical bytes, comparison of sequence alone, accepted stale ACK, event emitted at the reserved maximum, or allocation beyond the range is a failure. Unknown persistence durability means INCONCLUSIVE and HOLD.

C-01 must decide identifier creation/uniqueness evidence, the durable lineage authority, rollover threshold, canonical-cut mapping, backup recovery and the compatibility treatment for /1 clients that lack incarnation. Extending /1 in place is not assumed permitted. This does not select a cursor store. Status: candidate contract provided; ratification and native/crash validation pending.

## 6 Blocker four ACK credit and RESET wording

### Proposed normative ACK release

For the current stream incarnation, delivery_epoch and reset_epoch, let A be the highest contiguous EVENT sequence already acknowledged, H the highest contiguous EVENT sequence fully handed to the view's transport, and P the ledger of sent but not acknowledged events with their encoded byte charges. An EVENT ACK(n) MUST be evaluated atomically against that state.

If A < n ≤ H and every event in (A,n] was emitted contiguously in this delivery, the ACK is forward and valid. The broker MUST advance A to n exactly once and release only the newly acknowledged pending entries in (A,n], including their event-count reservations and encoded-byte reservations. It MUST NOT release an event outside that interval or any canonical log retention obligation not separately authorized by retention policy.

If n = A, the ACK is a duplicate. It MUST be a no-op: no cursor movement, no pending release, no credit increment, no repeated command receipt, no effect. If n < A, the ACK is backward and MUST be refused as ACK_BACKWARD with unchanged state. If n > H, continuity is missing, the message has the wrong identity/epoch, or the ACK references an unoffered snapshot, it MUST be refused as ACK_AHEAD, ACK_NONCONTIGUOUS, STALE_DELIVERY or SNAPSHOT_ACK_MISMATCH as applicable. Refusal must never silently clamp the value. Repeated malformed/refused traffic may close that view under the stated bounded control policy.

A cumulative ACK does not prove that a user saw the data, that a renderer is safe, that a process exited, that the canonical writer committed an effect, or that a tool's claim is true. The candidate semantic meaning is only that the client asserts it verified and accepted a contiguous protocol prefix into its bounded view state. A malicious client may lie; canonical retention and authority cannot rely solely on its assertion.

### Independent byte and event credit

Credit is independent of acknowledgment. The candidate CREDIT message contains credit_seq, grant_events_total and grant_bytes_total for the current delivery/reset epochs. These are cumulative authorized transmission totals, not additive deltas. The sender tracks sent_events_total and sent_bytes_total. Remaining event credit is grant_events_total minus sent_events_total; remaining byte credit is grant_bytes_total minus sent_bytes_total. Every EVENT requires both at least one event credit and at least its exact encoded record charge in byte credit. Debit both once before enqueue, and refund neither for an ACK.

An accepted forward ACK releases pending ledger capacity. It does not mint transmission credit. Only a valid CREDIT can increase the cumulative grants. The receiver checks that new grants do not permit outstanding transmissions above negotiated event or byte windows and that the pending ledger can represent the permitted window. Grant counters use bounded nonnegative integers with rollover tied to delivery renewal before their agreed maximum; no floating-point rounding or overflow is permitted. For the proposed stress profile, cap each cumulative counter at 2147483646 and renew/reset earlier if necessary.

credit_seq is monotonically increasing. The same credit_seq with identical totals is a no-op; the same sequence with different totals is CREDIT_CONFLICT. Older credit_seq is refused. New totals below previous totals are refused. Cumulative totals are not re-applied after reconnect. Credit for another view, stream, incarnation or recovery epoch is refused. At zero grant, a client can still exchange the separately bounded control records needed for ACK, CREDIT, RESET and refusal.

Byte charge is the exact number of bytes in the selected EVENT record on this connection, including the fixed length prefix or RS/LF framing and all encoded envelope fields. Do not charge Unicode code points, decoded object size, terminal cells or uncompressed size as wire bytes. Separately cap decoded memory and decompression; a wire-byte budget is insufficient for those layers. Snapshot transfer uses a separate approved bounded budget and does not borrow EVENT credit.

### Credit exhaustion is reset requiring

This candidate preserves a strict reset-requiring exhaustion policy. Exhaustion occurs when an eligible next EVENT is ready for delivery but cannot be enqueued because either remaining credit or pending-state capacity is insufficient. Merely reaching zero exactly after a valid final event, while no next event is ready, is not by itself a reset. When exhaustion occurs, the broker MUST stop EVENT delivery for that view, enter RESET_REQUIRED, invalidate that delivery's grants and pending ledger, and request a fresh snapshot recovery. It MUST NOT drop an event and continue at a later cursor or silently resume the same delivery when late credit arrives.

The alternative is a PAUSED_FOR_CREDIT state that resumes from a provably retained contiguous cursor without RESET; it can reduce recovery churn. Adopting it would be a deliberate contract change requiring retention and race fixtures. This report does not silently take that alternative. The Owner must ratify the strict exhaustion policy or explicitly authorize the alternative in A-01. Credit exhaustion is a view-level condition; it never pauses canonical writing.

RESET is always mandatory on a replay gap even if credit is abundant. For reset delivery, reserve an independent small control budget with rate limiting. A wedged transport may make RESET undeliverable; closing that connection and requiring recovery on its replacement is the terminal action. Closing does not prove the client saw RESET. Old bytes remaining in kernel or library buffers must remain distinguishable by epochs.

### Arithmetic and race oracle

A-FIX-01 starts with A=4 and H=7 and ledger byte charges for EVENT5=120, EVENT6=200 and EVENT7=80. ACK6 releases exactly two entries and 320 bytes; ACK6 again releases zero; ACK5 is refused unchanged; ACK8 is refused unchanged. ACK7 later releases one entry and 80 bytes. Credit remains unchanged by every ACK. The exact charges are a synthetic arithmetic vector; actual literal frame bytes must independently produce those lengths or use their own recorded charges.

A second vector gives one event credit and 100 byte credits for a 101-byte frame: no event is sent, neither counter is partially decremented, and RESET_REQUIRED follows. With two event credits and 101 byte credits, one 101-byte record may be sent; a ready second record triggers exhaustion. With bytes but zero events, a ready event likewise triggers reset. Concurrent ACK and CREDIT must serialize to an outcome consistent with these rules, with no double release or counter underflow.

Additional cases cover ACK before the corresponding write completes, partial transport write, torn ACK, reset crossing a queued ACK, old connection ACK after reconnect, duplicate CREDIT, conflicting CREDIT, cumulative-counter boundary, event ceiling without byte ceiling and vice versa, oversized single record, and a view that ACKs then stops rendering. Any negative count, silently accepted backward ACK, reissued credit from a duplicate, gap skipping, canonical-writer dependency or stale-epoch mutation is a failure. A-01 must approve the wording, arithmetic basis and exhaustion semantics before these are acceptance tests.

## 7 Framing decision and falsifiers

### The two candidates answer different questions

JCS specifies canonical JSON representation; it does not supply record framing, bounded allocation, corruption recovery or semantic authority. RFC 8785 constrains JSON values and deterministic property ordering. Duplicate property names and invalid Unicode must be rejected; numeric handling must follow the approved profile. Its verified errata include a security recommendation concerning negative zero. A broker profile must pin the RFC and errata treatment and must not quietly substitute a library's default JSON formatter. SD, high confidence. [S08, S09]

RFC 7464 provides UTF-8 JSON Text Sequences with record-separator and line-feed delimiters and recovery opportunities at a following record separator. It permits a parser to continue after malformed or truncated elements. Resynchronization does not prove that skipped semantic events are harmless or that the recovered bytes are authentic. A broker consumer still needs cursor continuity, schema and size checks. SD for sequence mechanics, IN for broker consequences. [S10]

Candidate LP-JCS uses a four-byte unsigned big-endian byte length N followed by exactly N bytes of the selected JCS record. N must be nonzero and within the negotiated cap before allocation; the prefix is not part of the JCS payload digest unless a separate frame digest explicitly includes it. EOF inside the prefix or payload, invalid UTF-8, invalid/noncanonical JSON, a length mismatch or corrupted structure is connection failure. No scanning for a plausible next length is allowed. Reconnect uses the last accepted cursor and either contiguous replay or RESET. This is proposed framing, not a selection or an existing /1 fact.

Candidate RS-JCS uses RFC 7464 delimiters with the same semantic JSON/JCS schema. It may locate a following RS after bad input, but cannot apply an EVENT beyond a missing predecessor. On a skipped event or unprovable continuity, it enters RESET_REQUIRED; successful scan is not success of the lost operation. Restricting broker records to top-level objects avoids some scalar ambiguity but does not remove the RFC's truncation and parser concerns. A maximum record size, maximum scan budget and timeout are required even when no valid delimiter appears.

### Decision rule

LP-JCS is the candidate to evaluate first if transport corruption is connection-fatal by policy, reliable reconnect and cursor recovery meet the product's outage objective, and measured allocation bounds are more valuable than keeping a damaged connection alive. Choose RS-JCS only through an Owner decision showing that in-stream recovery provides a required and measured advantage, while the parser still enforces gaps, caps and authority boundaries. Neither preference selects a serialization library.

The decisive comparison uses the same literal corpus, traffic segmentation and fault schedule, recording accepted event identities, recovered cursor, bytes scanned, peak memory, CPU, reconnect time, reset count and healthy-view/writer impact. A shorter recovered-byte sequence is not a win if it concealed a missing event. A protocol that depends on RS resynchronization but resets for every corruption may not gain enough to justify the added parser surface; that is an empirical question, not a blanket rejection of RFC 7464.

### FR01 torn and corrupt stream corpus

FR-FIX-01 includes every split of the four-byte length prefix, splits at each UTF-8 boundary, zero and maximum lengths, cap plus one, 0xffffffff, payload shorter/longer than declared, EOF after each prefix byte, EOF at payload boundaries, concatenated valid records, a valid suffix after a torn record, and conflicting length embedded in attacker-controlled JSON. LP-JCS must never allocate from an unchecked declaration or resume by scanning after a corrupt length.

FR-FIX-02 includes missing initial RS, repeated RS, empty record, truncated string, embedded escaped newline, raw control characters, missing LF, valid scalar prefix followed by truncation, malformed UTF-8, a valid record after noise, an RS appearing in corrupted bytes, and an infinite delimiter-free stream truncated by the test harness. RS-JCS must remain bounded and must not convert resynchronization into sequence-gap acceptance.

Both candidates receive duplicate object keys, unordered keys, lone surrogates, alternate valid escape forms, nonfinite values, 2^53 boundary numeric cases, negative zero per the approved errata policy, excessive nesting, huge property counts, deeply nested arrays, and records with syntactically valid but wrong cursor/schema. Reject/noncanonical outcomes must be literal corpus expectations rather than inherited parser behavior. Silent parser repair or normalization is a failure.

Framing is falsified by an admitted unbounded allocation, lost or duplicated event applied as contiguous, different canonical bytes across independent implementations, a corrupted record admitted as a command, or healthy writers/views delayed beyond the declared isolation envelope. Correctly closing a torn LP-JCS stream is expected behavior, not a failure. Passing the corpus does not establish arbitrary parser safety or prove a library implementation correct for all inputs.

## 8 Bounded flow and canonical writer isolation

### Architecture constraints

The canonical writer must publish only bounded immutable event references or approved copies into a nonblocking handoff. It must not perform view transport writes, wait for view ACK, await rendering, hold a canonical mutation lock while projecting, or call a per-view allocator whose exhaustion blocks commit. A view that exceeds its capacity is reset or disconnected. A bounded projection worker can read canonical history under its own limits; no slow view may hold an indefinite canonical snapshot/retention lease.

A per-view queue is insufficient by itself. Audit transport buffers, partial-frame accumulator, parser and schema-validation work, decoded objects, projection state, pending ACK ledger, renderer/sink queue, logs, metrics labels, snapshot staging and any library's implicit queue. Shared queues must have global limits and fairness. A fixed per-view cap multiplied by unlimited connections is still unbounded. Retention volume and writer admission capacity must be independently bounded by their own Owner-approved policies; a view cannot force them to grow.

Detach is a view operation. Input is a command through the separately authorized broker path, not arbitrary bytes reinterpreted as authority. Reattach must not launch a process, create a model or replay an unacknowledged input command blindly. A view claiming it has rendered data does not become a verifier for effect completion.

### Candidate bounded qualification profile

These are proposed test ceilings for BP-CAND-20261001, not production defaults, measured capacities or standards requirements. The Owner may choose different values before execution, but a run must pin all values and its contract digest. MiB and KiB mean binary units. Raising a ceiling after a failing run creates a new profile, not a corrected PASS.

| Layer | Candidate ceiling | Overflow action and evidence |
| --- | --- | --- |
| Broker data record | 256 KiB including framing | Refuse oversized outbound record before enqueue; close malformed inbound record; preserve reason |
| Handshake or control record | 16 KiB per record | Refuse or close; no admission/effect |
| Frame accumulator | One maximum data record plus prefix | Never allocate declared excess; partial-frame timer 5 s |
| Decode and validation | 2 MiB live decoded data per view; depth 64; 4096 fields | Reject on budget; validate elapsed work against a 50 ms per-record test budget |
| EVENT window and pending ledger | 256 events and 1 MiB wire bytes per view | Both limits apply; strict RESET on an eligible event that cannot fit |
| Projection state | 8 MiB per view | RESET or refuse projection; do not trim semantically required state silently |
| Render sink queue | 1 MiB per view | Detach/reset sink; never wait on canonical writer |
| Snapshot staging | 16 MiB transferred snapshot; 2 MiB memory staging | Refuse larger materialization unless another approved profile exists; streamed/chunked format remains undecided |
| Control reserve | 16 records and 64 KiB per view | Close on reserve exhaustion; rate limit repeated ACK/refusal/reset traffic |
| Active views | 16 per broker in this profile | Typed pre-admission refusal for the seventeenth |
| Per-view application memory | 16 MiB hard accounted cap | Close/reset offending view; include metadata/copies, not just payload |
| Global view application memory | 256 MiB hard cap | Refuse new views or reset selected views without canonical mutation lock |
| OS transport buffers | Requested ceiling 256 KiB per direction | Record effective values; if unenforceable or unmeasurable, qualification is unknown rather than claiming the requested cap |
| Reset recovery | At most 3 attempts in 30 s per view | End with recovery-unavailable and bounded backoff; no endless snapshot churn |

These caps are intentionally separate. A 1 MiB wire queue plus an 8 MiB projection does not account for kernel buffers, allocator overhead or duplicate copies; the overall 16 MiB accounting cap still applies. A single legitimate event larger than 256 KiB must use a separately ratified representation or receive a typed refusal; it may not be secretly split into semantically different events. A snapshot larger than 16 MiB is a profile failure or refusal, not proof of corrupt state. A 50 ms parser limit is a qualification objective, not an ability to safely preempt any runtime; implementation must show a bounded-work mechanism.

### ISO01 measurable no wait oracle

ISO-FIX-01 runs a pinned workload with zero views, one healthy view, and one healthy plus the allowed number of stalled/adversarial views. Inject stalling separately at the transport read, partial-record sender, decode/validation, projection, ACK generation and render sink. Include a view that consumes/ACKs at full rate while its sink blocks, and one that sends control frames at the allowed maximum. Baseline and fault runs must use the same event corpus, rates, CPU/memory limits, storage profile and schedule seeds.

A hard architectural pass requires independent inspection and trace evidence that no canonical commit's wait chain depends on a view stage. A bounded synthetic test cannot prove that property for all schedules; include instrumentation for waits, lock hold times and queue dependencies. Performance must also meet a preregistered candidate threshold: fault-run commit p99 may not exceed baseline p99 by more than max(10 percent of baseline p99, 1 ms), healthy-view p99 lag by more than max(20 percent, 20 ms), with no cap violation and no committed event lost. Those are proposed qualification thresholds, not measured results.

Capture per-stage high-water bytes and counts, process RSS with baseline separation, OS effective buffers, event-loop or worker scheduling delay, writer commit latency, reset/disconnect decisions, CPU time and live allocations after detach. A mean below threshold cannot hide p99 failure. Report sample size and confidence intervals; a noisy baseline is INCONCLUSIVE. Stop immediately on an effect-authority violation, canonical corruption or unbounded growth. A failed performance threshold calls for diagnosis and a new explicitly versioned run, never a lowered hidden workload.

## 9 Exact end to end recovery and command identity

REC-FIX-01 exercises the complete recovery path across both native platforms. Its oracle is a reviewed canonical event chain plus SM-01 snapshot bytes; the observable view must equal the approved projection of precisely that cut and subsequent contiguous events. Record the last accepted EVENT ACK, not simply the last frame read. Disconnect before write completion, after full write but before ACK, after ACK transmission but before server processing, and during new CREDIT. Repeat at RESET and snapshot transitions.

At-least-once delivery is compatible with exactly-once application only if the consumer recognizes duplicate canonical event identity and applies the approved idempotent rule. An identical sequence with different digest is a corruption/conflict, not a duplicate. Event replay is not command retry. The view must never cause a new effect merely because an old output frame is replayed.

A command ID binds the complete approved canonical command bytes/digest. Same ID and same digest yields the recorded committed receipt, with no new canonical event or dispatch. Same ID with a different digest is COMMAND_CONFLICT. On uncertain commit, reconcile against the authoritative command ledger and event chain before deciding whether a retry is allowed. A previously admitted receipt does not grant a fresh dispatch lease: current goal, plan, lease and pause epochs must be checked at the effect boundary. This aligns with the FU03 candidate semantics and still needs the actual approved contract.

A broker-only deduplication ledger cannot guarantee exactly-once external effects. If an external service committed but the receipt was lost, the state is effect_unknown until an approved idempotency key or external reconciliation can establish the result. A retry after unknown effect must not be automatic merely because the socket closed. Stop also does not resolve that uncertainty.

## 10 Native chaos campaign preregistration

### Common execution contract

The following CH cases are preregistered specifications. Every case is UNRUN. Required native cells are Windows and Linux under FU04's exact profile records. WSL2 ext4, WSL2 mounted Windows filesystems, MSYS2/Git Bash, embedded terminals, SMB and NFS are distinct profiles, not substitutes for either native platform. BSD behavior is not inferred from Linux. Windows pre-build-26100 and build-26100-or-later must be separate cells if both are in the Owner's support envelope.

Before a local session runs any case, it needs approved fixture code and digest, exact OS/build/kernel and architecture, privilege and namespace model, Job or cgroup hierarchy, transport/PTY versions and settings, canonical contract digest, fresh disposable test scope, synthetic command/event corpus, and an independent observer outside that scope. No current configuration is changed by this report. Privileged migrations and external service cases require separately authorized isolated local test setup; their inclusion is not permission to alter a production host.

Use stable process identity rather than PID alone: process handle or pidfd where supported, creation time, boot identity and scope identity. The observer records creation, membership changes, exit, transport state, kill request, termination verification and any external-service effect. Retain raw traces and observer health. If the observer loses coverage, the relevant verdict becomes unknown even if cleanup later succeeds.

The candidate test timing is 5 s for cooperative stop, another 5 s for authorized forced-scope termination, and up to 20 s for verification/reaping, with a 30 s safety deadline from stop request. These are local qualification ceilings, not OS or MCP promises. Case-specific long-running effects need a reviewed different profile. The independent watchdog uses an outer disposable safety boundary; it must not be the same mechanism whose effectiveness is being tested.

PASS requires the case's positive and negative controls, intended fault injection confirmed, all required observations and recovered invariant. REJECTED means a demonstrated contract violation. INCONCLUSIVE means missing injection/coverage or environmental failure. BLOCKED means a required contract, privilege or profile is absent. Only PASS can qualify a case; a skipped row cannot.

### CH01 birth time membership

Platforms: native Windows and Linux. Inject the documented post-creation-association pattern as a negative control and creation-time membership as the candidate, with maximal early child activity and repeated broker termination at the relevant creation cutpoints. On Windows test PROC_THREAD_ATTRIBUTE_JOB_LIST with an explicit handle-inheritance list; on Linux test an approved creation-in-cgroup path, such as CLONE_INTO_CGROUP where available, or a separately qualified manager-mediated birth path. API availability is documented; host capability is unverified. [S11, S13]

Observe membership before the first fixture user-code marker and the lifetime of every fixture-created process under the independent observer. Recovery requires that candidate creation either fails before runnable work or begins inside the intended scope; the negative control must show the harness can detect the unsafe gap if it occurs. Stop on an uncontained fixture process, observer loss or 30 s deadline. Never generalize one passing birth path into complete descendant capture.

### CH02 Windows explicit and silent breakaway

Inject child creation with breakaway flags, permissive versus restrictive Job limits, and the same cases under an ancestor Job. Observe the actual Job hierarchy and membership of each created process, including rejected creation. The restrictive profile must refuse or retain the child; the deliberately permissive profile must reveal the escape without a false containment-complete claim. Recovery closes admission, kills only the approved managed scope and reconciles the escaped test process through the independent safety boundary. Stop on escape beyond that boundary or unknown process identity. [S12]

### CH03 Linux privileged and unprivileged migration

Inject writes attempting to move a member outside its delegated cgroup subtree, first as the intended unprivileged principal and then, only in an authorized disposable test, through a privileged helper. Observe cgroup identity at each cutpoint and the helper's credentials/capabilities. The unprivileged denied-migration control and the privileged escape control must be distinguishable. Killing the original scope may leave already escaped work alive; record that limit. Recovery forbids new effects, invokes approved cleanup and marks effect_unknown when external work cannot be reconciled. Stop on observer gaps, migration outside the outer test boundary or cleanup deadline. [S14]

### CH04 nested and alternate Windows Jobs

Inject launch from a process already inside an ancestor Job, assignment to a nested Job, incompatible limits, alternate Job use, reordered creation-time Job lists and assignment failure. Observe exact API errors and actual membership rather than assuming the requested list took effect. Candidate recovery either achieves the declared supported hierarchy or refuses admission before effect. No fallback to uncontained launch is allowed. Stop on a process running after containment setup failed or a mismatch between requested and observed membership. [S11, S12]

### CH05 external service created work

Platforms: both. Inject a fixture requesting an external service/daemon to create work outside the broker's process ancestry or scope. Use only a separately authorized synthetic service. Windows management-service creation and Linux manager-created jobs are distinct variants. Add upstream-only and combined harness routes, pinning upstream product, version, configuration digest and delegated-work boundary; a local wrapper process cannot inherit capture of work delegated to a remote service or host. Observe the service's own work identity and lifecycle separately from the requester. Recovery must show that requester death is not reported as service-work completion; use an approved service cancellation/reconciliation API or preserve unknown effects. Stop on non-synthetic service access, unbounded work or inability to contain cleanup. This case is a required counterexample to unconditional full-tree claims.

### CH06 abrupt broker death

Platforms: both. Kill the broker without graceful cleanup at pre-admission, post-admission, pre-dispatch, post-dispatch and post-receipt cutpoints. Observe which supervisor survives, actual scope ownership and durable command/effect state. On Windows vary whether the last Job handle really closes; on Linux verify the independent supervisor's policy because cgroup membership alone is not an automatic kill-on-broker-death contract. Recovery must reconcile existing command IDs and effects before new admission. Stop at the safety deadline or any duplicate effect. [S12, S14]

### CH07 leaked handles and descriptors

Inject a duplicated/inherited Job handle held outside the dying broker, open pipe handles held by a child, and extra PTY file descriptors. Observe all test-owned references through the fixture manifest, actual last-close timing, EOF and process exit separately. Windows KILL_ON_JOB_CLOSE depends on the last Job handle closing, not one arbitrary handle. Recovery uses explicit approved scope termination and reconciles the leak. The expected negative control may keep the scope alive; it must not be labelled settled. Stop on unknown reference owner, broader host handles in the test, or verification timeout. [S12]

### CH08 ConPTY teardown and blocked output

Windows only. Inject saturated output, no reader, a separate drainer, closure on the draining thread and closure from a separate lifecycle worker. Execute supported pre-26100 and 26100-plus profiles separately. Observe ClosePseudoConsole return, output EOF, connected-client state, process handles and Job membership independently. Microsoft documents immediate return from Windows 11 24H2 build 26100, and older-build deadlock risk if output is not closed/drained. Recovery must avoid waiting on the same blocked path and then verify scope termination separately. Stop on watchdog deadline or canonical-writer coupling. [S15]

### CH09 Linux PTY teardown

Inject closing the master while children retain slave descriptors, a child ignoring cooperative hangup/termination, a detached session and an independently retained PTY reference. Observe transport EOF/error, process identity and cgroup membership separately. Recovery must use the approved scope path and independently verify live-process absence; no inference from terminal closure is accepted. Stop on escaped fixture work, uncertain observer coverage or timeout. PTY API behavior is platform-specific; the fixture does not assume ConPTY-equivalent return or signal semantics. [S16]

### CH10 duplicate input and reconnect

Platforms: both. Inject the identical command before and after acknowledgement loss, reconnect, broker crash and durable receipt recovery; then reuse the ID with different bytes. Observe the canonical command ledger, external test-effect counter and exact receipt bytes. Recovery must return the recorded result for the identical command and refuse the conflicting body, never duplicate dispatch. Stop on the first duplicate side effect, receipt inconsistency or ambiguous external result. A transport ACK is not the oracle.

### CH11 VT and terminal injection

Platforms: both. Inject synthetic OSC and CSI sequences, hyperlinks, clipboard requests, title changes, cursor movement, control characters, bracketed-paste delimiters and text that imitates prompts or broker status. Test malformed and oversized sequences. Observe that only terminal/view data changes within the authorized presentation policy; no input command, URL fetch, clipboard write, file access or effect admission is generated from output bytes. Recovery resets the affected bounded parser/view and preserves canonical state. Stop on any cross-boundary effect or uncontrolled host action. This is an authority-boundary test, not a renderer selection.

### CH12 daemon restart and stale endpoint

Platforms: both. Restart while a client holds an old cursor, old connection, old endpoint path/pipe name and in-flight ACK/CREDIT. Add stale endpoint ownership and an unauthorized synthetic peer. Observe actual peer admission, delivery epoch, incarnation lineage and state recovery. Recovery must refuse stale identity, avoid killing unrelated processes or deleting another owner's endpoint, and produce replay or RESET as required. Stop on mistaken peer admission, unsafe cleanup or cursor reuse. Native permissions and credentials differ; a pathname or pipe name alone is not sufficient identity. [S17, S18]

### CH13 slow view at every layer

Platforms: both. Execute ISO-FIX-01, blocking each transport/decode/projection/render stage independently and together. Observe every high-water mark, healthy-view lag and canonical wait chain. Recovery resets/disconnects the offender with bounded residual buffers, then returns memory to the recorded baseline tolerance. Stop on a global memory cap, writer wait dependency or isolation threshold failure. This case cannot be passed by demonstrating only a bounded application queue.

### CH14 replay retention gap

Platforms: both. Evict required history before HELLO, after WELCOME, during snapshot transfer and just before first post-snapshot EVENT. Observe retention proof, RESET reason, snapshot cut and accepted event chain. Recovery requires a complete verified snapshot and fresh contiguous tail, or explicit recovery-unavailable. Stop on event application over a gap, infinite reset churn or writer blocking for retention. The test uses an approved synthetic retention fixture, not a chosen retention engine.

### CH15 framing corruption and partial send

Platforms: both. Execute FR-FIX-01 and FR-FIX-02 with identical segment schedules and a healthy concurrent view. Observe parser budget, cursor, refused/admitted commands and reconnection state. Recover by the candidate's declared failure/reset rule, with no allocation from an unchecked length. Stop on unbounded scan/allocation, admitted corrupted command, cross-view impact or false contiguous delivery.

### CH16 cancellation ignored and boundary absent

Platforms: both. Run a synthetic effect that ignores cooperative cancellation, one that emits endless progress without a safe boundary, and one that finishes concurrently with cancellation. Observe Stop's durable fence, per-effect deadline, cancellation request, scope termination and external-effect reconciliation. Recovery must reach either independently verified settlement or an explicit stopped-with-unknown-effects state; no green completion from timeout alone. Stop on a new effect admitted after the Stop fence or the independent safety deadline. See section 15.

### CH17 writer commit and receipt crash windows

Platforms: both. Crash before and after command admission, event persistence, receipt persistence and external dispatch boundary, using the approved store's cutpoints supplied by FU02. Observe authoritative events, command receipt and outbox/dispatch state. Recovery must preserve the accepted atomicity contract and report ambiguous effects honestly. Stop on a committed receipt without its required state, duplicate dispatch, or lost acknowledged canonical commitment. No storage atomicity is presumed from this report.

### CH18 rollover and restored old state

Platforms: both. Execute C-FIX-01, add a backup restored from before rotation and a client reconnecting from an old incarnation. Observe persistent lineage, exact canonical cut and rejected stale ACK/CREDIT. Recovery requires a verified current lineage or mandatory reset/refusal. Stop on same-cursor different-bytes reuse, sequence overflow or reconciliation uncertainty.

### CH19 scope kill racing with creation

Platforms: both. Race kill with bounded fixture child creation inside the declared scope; separately attempt pre-kill privileged migration in the authorized negative control. Observe all births through an independent observer and record the kill linearization interval as an interval, not a guessed instant. Recovery must establish scope empty and individual known exits under the approved platform oracle. Stop on residual managed live work at deadline or missing coverage. Passing does not recapture work that left the scope before kill. [S12, S14]

### CH20 observer failure and false green

Platforms: both. Stop the observer, drop a completion notification, reuse a PID, corrupt an observation record, and feed a forged tool success result. Observe whether the broker retains distinct unknown values and refuses to infer settlement from channel closure or absent events. Recovery re-establishes a trusted observer and reconciles state, or remains unknown. Stop on any completion claim based solely on a transport ACK, tool text or missing notification. This negative control is required for every containment campaign.

## 11 The defensible containment claim

The strongest supported design claim is membership-limited: after the approved termination operation and independent verification, all live processes remaining inside the identified managed scope have been terminated. Scope identity, observation time, OS profile, kill operation and verification evidence must be stated. An API return alone is insufficient. Until the native fixture is run, even this is a proposed acceptance claim, not an observed product capability.

Windows documentation describes terminating processes associated with a Job and the dependence of kill-on-close on the last handle. It also documents breakaway behavior and exceptions to normal child membership. Linux cgroup v2 documents killing processes in the affected cgroup tree, with concurrent-fork handling and migration protection during that operation. Neither statement captures work that was created outside, escaped earlier, was created by an external service, or resides on a different host. SD, high confidence within the cited APIs. [S12, S14]

The verification must distinguish known process exit from no live process in the scope, and both from effect settlement. A Linux zombie can have no live execution while still awaiting reap. A closed terminal can coexist with live detached work. A terminated local requester can leave a remote operation running. Unknown external state remains unknown rather than zero work remaining.

To strengthen capture completeness, a future claim needs a defined closed-world threat model, an inventory of every process-creation and external-service path, creation-time membership for each supported path, inability of the threat principal to break away or migrate, restricted access to out-of-scope service creation, complete independent birth/membership observation, supervisor survival and handle ownership guarantees, and validation across every supported native build. It also needs negative controls demonstrating that escape is detected. Observation coverage must include the interval before kill, not just a final process enumeration.

Even that package supports completeness only under its explicit assumptions and tested profiles. Administrator/root intervention, compromised kernel, unavailable remote-service evidence, observational blind spots and arbitrary new launch mechanisms remain outside the claim. This report makes no full descendant-tree termination claim. Adding a broader claim is an Owner security decision plus new evidence, not a wording change after a convenient PASS.

## 12 Chaos evidence record and acceptance

Each local run must emit a content-addressed manifest linking the raw trace, exact fixture source/binary identity, environment profile, approved contracts, corpus identity and independent review. Use synthetic identifiers in public exports. Keep private host paths, usernames and credential-bearing arguments out of the report; retain sensitive diagnostic evidence only in an authorized private evidence store.

The candidate broker-specific supplemental evidence record, linked to but not substituted for FU04's platform result, has these required fields: result_schema, run_id, profile_key, fixture_id, fixture_version, variant_id, cutpoint, failure_domain, contract_digest, corpus_digest, injection_confirmed, observer_coverage, observations, recovery_result, stop_reason, verdict, qualification, evidence_manifest_digest and reviewer. Strings and enums must have explicit size caps in the approved fixture schema; absence is not equivalent to an empty string. Unknown digest/profile values are null with a missing-input reason, never fabricated hashes.

observations contains independent tri-state values for transport_closed, client_disconnected, process_exited, containment_empty and execution_settled. Each includes observed_true, observed_false or unknown; observer_id; monotonic time plus clock domain; source artifact reference; and coverage interval. Multiple process-exited observations are indexed by stable process identity. A wall-clock timestamp is useful for correlation but cannot order concurrent state transitions reliably by itself.

The FU04 platform result remains a separate closed-schema object. It records execution_epoch and observer_epoch separately and uses the string tri-state values true, false and unknown, each with evidence_refs and reason. The receipt vocabulary maps observed_true to the string true, observed_false to the string false and unknown to unknown; no unknown value maps to false or zero. FU04 also requires scope_membership_complete and descendant_capture_complete. Those completeness predicates remain unknown unless independently established under a bounded claim; containment_empty never sets either automatically. Its qualification is qualified, rejected or unknown, and its independent_review is pending, accepted or rejected. A missing required platform result prevents qualification even if the broker supplement is complete.

The evidence bundle also contains commanded and observed membership, effect IDs, exact receipt bytes, ACK/credit counters, high-water buffers and counts, canonical event frontier, timeout deadlines and actual elapsed time, observer health, and successful cleanup verification. For a timing distribution, retain the samples, workload identity and analysis recipe, not only percentiles.

Reviewers must be independent of the implementer and must inspect the negative controls, false-green cases and missing data. The implementer's own PASS never accepts the platform. A fixture that fails to inject its intended fault is INCONCLUSIVE. A missing supported OS/build cell leaves that profile Unqualified. A paper contract can close a wording question but cannot turn an unrun native matrix green.

## 13 Separate MCP tool broker boundary

### Current protocol pin and actual documented behavior

The research pin is MCP core 2026-07-28. The official stable release points to commit 5f5440bb26a62e2cf3440b92da5a667efa03b267. That is a reproducible release baseline, not a claim that all later documentation is byte-identical to it. Current version-qualified documentation was read on 1 October 2026, and the source register identifies separately the immutable commit evidence and mutable dated pages. Before a local qualification run, archive the exact schema and documentation package and record its digest. Do not use a floating latest or main reference as the test oracle. [S01, S02, S07]

Modern requests carry version and declared client capabilities per request; unsupported versions receive a typed error with the server's supported versions. The inspected current page and schema use error code -32022. Legacy initialization-based revisions through 2025-11-25 require an explicitly tested compatibility path. Do not send a modern request without its required metadata or infer capabilities from an earlier connection. SD, high confidence in inspected sources. [S02, S03, S07]

For stdio, messages are UTF-8 JSON-RPC, one newline-delimited message per line; stdout is protocol-only and stderr is separate logging. The subprocess lifecycle is specific to this binding. All notifications and responses share stdout, so subscription demultiplexing does not create separate physical channels or independent OS backpressure. SD for binding mechanics; IN for the flow-control implication. [S04]

The modern subscriptions/listen stream begins with an acknowledgment scoped to its subscription ID, and notifications are restricted to subscribed types. Reconnection requires resubscription. The inspected sources do not define the broker's event/byte CREDIT or durable replay cursor contract for MCP notifications. The broker must not assume its own event protocol is supplied by MCP or that a subscription acknowledgment proves an effect completed. [S05]

### A live source discrepancy to resolve

The inspected cancellation page requires a server cancellation notification when tearing down a subscription, while the subscriptions page describes a successful completion response for graceful closure. These are directly conflicting descriptions of the same path. The discrepancy is also recorded in issue 3348, with both pages pinned at e76e9c572c6f2bfcb730357101acc90f2f802e02. The report relies on the primary page contents for the conflict; the issue's claims about SDK implementation are not treated as observed behavior. [S05, S06, S21]

MCP-01 must choose a pinned schema/documentation interpretation and test the actual server/SDK combinations before qualifying subscription teardown. A tolerant receiver can record either recognized closure form as a protocol observation, without deriving effect settlement. A sender still needs an explicit interoperable behavior; tolerating both cannot settle which normative rule it implements. An upstream clarification is useful but does not replace local compatibility evidence. No issue was posted, no SDK installed and no server contacted for this report.

### Numerical bounds are local policy proposals

No universal numeric maximum for a stdio line, partial line, tool result, stderr queue or per-subscription queue was found in the inspected MCP core binding, subscription pages and schema. The specification gives qualitative timeout/resource guidance and transport rules. A chosen SDK or server may impose its own defaults; those are unknown until the exact implementation and configuration are pinned. Absence of a universal maximum is not permission to allocate without a cap. [S03–S07]

The following proposed TOOL-LIMITS-01 profile is distinct from the broker EVENT profile. It is deliberately explicit so local agents can test it. Every value requires Owner ratification or a revised profile before production adoption.

| Boundary | Proposed ceiling | Enforced behavior |
| --- | --- | --- |
| MCP wire message | 1 MiB UTF-8 bytes excluding delimiter LF | Reject/close at cap plus one; no allocation from an untrusted declared size |
| Partial stdio line | 1 MiB plus one delimiter byte; 5 s no-completion timer | End offending server channel and reconcile in-flight effects |
| Decoded message | 4 MiB live decoded data; depth 64; 16384 nodes | Fail validation within bounded work; never forward partially decoded result |
| Declared maximum record | Local adapter profile field max_record_bytes=1048576 | No standard MCP max-record negotiation is invented; incompatible server is refused or gets an approved alternate profile |
| stdout dispatch queue | 64 records and 4 MiB per server | Dedicated bounded reader; overload is channel fault, not silent result loss |
| stderr drainer | Dedicated read path; 64 KiB partial line; 256 KiB retained ring | Continue draining with discard counters when retention fills; do not stop reading because logs are full |
| Tool result retained payload | 8 MiB aggregate per effect; no inline output in receipt | Mark truncation and observed length; oversized protocol message still fails earlier |
| Binary or encoded content | 8 MiB decoded aggregate per effect | Count encoded and decoded sizes separately; reject a decompression/decoding bomb |
| Concurrent in-flight requests | 8 per server in this profile | Queue or refuse before dispatch under bounded admission |
| Active subscriptions | 4 per server; 128 queued notifications and 1 MiB total | Close/reconcile overloaded subscription/channel; never imply durable replay |
| Default finite tool request | 60 s absolute maximum, independent of progress | Cancellation and effect-aware escalation at deadline |
| Tool-broker process/application memory | 128 MiB incremental budget for this profile | Stop admission, fault offending server and reconcile rather than unbounded growth |

stdio has no separate length header to trust. The partial-line limit must apply incrementally before a newline arrives. A 1 MiB encoded cap still permits memory expansion during JSON decoding, base64 decoding, schema evaluation or nested content handling, hence the separate budgets. Dedicated stderr draining is a local robustness requirement: ordinary pipes are finite, and a writer can block when a pipe is full. Dropping retained logs is different from ceasing to drain. SD for finite-pipe behavior, IN for this proposed design. [S19]

Tool outputs are untrusted evidence. Validate the declared output schema where applicable, sanitize presentation, cap content, and never treat instructions embedded in a result as authority. Tool annotations are not an authorization mechanism. The accepted Recursion command and current authority guards determine effects; a tool result cannot promote itself into a command, change the model/provider, reopen a stopped goal or create a new credential. [S20]

### MCP01 interoperability and overload fixture

Use two independent adapters and approved synthetic servers for the pinned modern revision and each explicitly supported legacy revision. Test per-request metadata, supported-version refusal, required capabilities, malformed responses, result IDs, modern/legacy mismatch, interleaved subscriptions, unsupported filters, acknowledgment ordering, resubscription, both observed subscription-closure forms, and late notifications after cancellation.

Inject a delimiter-free stdout stream, 1 MiB-minus-one and cap-plus-one records, mixed log text on stdout, saturated stderr, huge decoded content, excessive schema depth, a notification flood while a tool response is pending, a server that ignores cancellation and a server that continually reports progress. Oracle: no authority promotion, bounded per-layer and total allocation, correct request/subscription correlation, no false success, and explicit unknown effects after forced channel failure. Stop on any authorization breach, cap violation, wrong-request delivery or the independent safety deadline. A standard conformance-suite PASS alone cannot establish these local limits or effect semantics.

## 14 Command receipt event payload

### Scope and exact candidate type rules

TOOL-RECEIPT-01 is a proposed closed payload schema for the separate tool broker, not an MCP message schema and not an already-ratified Recursion event. The canonical event envelope supplies stable event identity and integrity according to the approved kernel contract; the payload below references that identity but does not define the store or serialization library. A transport envelope may mark a delivery as replayed without changing the cached canonical receipt bytes.

Every listed field is required. Nullable means an explicit JSON null; omitted fields are invalid. Additional properties are forbidden at every object level. All strings use valid Unicode; free text is restricted to bounded diagnostic text and must be redacted before persistence. The envelope is limited to 16 KiB; larger evidence is an opaque, policy-approved artifact reference. No raw stdout/stderr, command-line secret, credential, host path or arbitrary network URL belongs in the receipt.

Primitive definitions: Id is 1–128 ASCII characters from letters, digits, dot, underscore, colon and hyphen. Counter is an integer in 0 through 2147483646. DecimalOrdinal is a decimal string of 1–20 digits with no leading zero except the single digit zero; its precise semantic maximum comes from the approved canonical event contract. Digest is a closed object with algorithm equal to sha256, value equal to 64 lowercase hexadecimal characters, and preimage_contract_id of type Id. SHA-256 here is a receipt-candidate convention and must be reconciled with the approved kernel digest contract; it is not a snapshot format decision. TriState is observed_true, observed_false or unknown.

| Field | Exact type | Meaning and constraint |
| --- | --- | --- |
| receipt_schema | Constant tool-command-receipt/1-candidate | Must change if interpretation changes |
| receipt_id | Id | Stable unique identity of this canonical receipt transition |
| command_id | Id | Durable idempotency identity, never a connection ID |
| command_digest | Digest | Binds the complete approved canonical command bytes |
| authority_decision_ref | Id or null | Reference to a recorded authorization/admission decision, never a grant by itself |
| effect_id | Id or null | Stable external effect identity if assigned |
| attempt | Counter | Zero before dispatch; positive for a recorded authorized dispatch attempt |
| phase | Closed enum below | One canonical lifecycle transition, not a claim inferred from socket state |
| cause | Closed enum below | Stable machine-readable reason |
| source_event | EventRef or null | Already committed causative event; never the digest of this receipt event |
| broker_instance_id | Id | Diagnostic instance identity, not stream or effect authority |
| scope_ref | Id or null | Opaque managed-scope reference |
| mcp | McpRef or null | Transport/request correlation, never effect identity |
| limits_profile_id | Id | Exact applied numerical and deadline policy |
| deadline | Deadline or null | Deadline evidence for this attempt |
| output | OutputEvidence | Length, truncation and approved evidence references |
| observations | ObservationSet | Five independent truth-valued evidence observations |
| settlement | Closed enum below | Effect-level outcome with unknown kept explicit |
| evidence_refs | Array of 0–16 Id values | Approved retained evidence identifiers |
| diagnostic_code | Id or null | No runtime-generated unbounded diagnostic text |

phase is one of admitted, dispatch_started, protocol_observed, tool_result_received, stop_requested, cancellation_requested, scope_termination_requested, settled, rejected or effect_unknown. cause is one of accepted, completed, policy_refused, schema_refused, command_conflict, user_stop, deadline, transport_fault, limit_exceeded, containment_fault, observer_lost or reconciliation. settlement is one of not_started, pending, succeeded, failed, cancelled_verified or unknown.

source_event refers only to an already committed event; the receipt event's own digest belongs in its outer canonical envelope and is excluded from its own preimage as that contract requires. This prevents a circular self-hash. EventRef is the closed object {aggregate_id: Id, ordinal: DecimalOrdinal, event_digest: Digest}. McpRef is {protocol_version: Id, transport: stdio or streamable_http, request_id: Id, server_profile_id: Id}; adapters normalize a JSON-RPC numeric ID to a lossless local correlation string and retain its original type in the approved request-evidence artifact. It must not become a command idempotency key. A retry for additional MCP input has a new JSON-RPC ID while remaining linked to the authorized effect and command.

Deadline is {clock_domain: Id, started_tick_ns: DecimalOrdinal, absolute_deadline_tick_ns: DecimalOrdinal, budget_ms: Counter, escalation_profile_id: Id}. Monotonic ticks compare only inside the recorded clock domain. After restart, remaining budget must come from an approved durable deadline contract; if it cannot be established, do not silently reset the full timeout or pretend it expired precisely. Record uncertainty and reconcile before dispatch.

OutputEvidence is {artifact_ref: Id or null, digest: Digest or null, bytes_observed: Counter or null, bytes_retained: Counter, truncated: boolean, complete: boolean, validation: valid or invalid or unknown}. Null bytes_observed means not known; zero means observed empty. A complete output may still describe a failed tool operation. If truncated is true, complete must be false; bytes_retained cannot exceed bytes_observed when that value is known. A digest identifies retained bytes according to its preimage contract and must not imply a digest of unobserved output.

ObservationSet is {transport_closed: Observation, client_disconnected: Observation, process_exited: Observation, containment_empty: Observation, execution_settled: Observation}. Observation is {value: TriState, observer_id: Id or null, clock_domain: Id or null, tick_ns: DecimalOrdinal or null, evidence_ref: Id or null}. observed_true or observed_false requires all four evidence/observer fields non-null. unknown permits nulls and must not be promoted by default. Aggregate process-exited truth refers to an explicitly identified process set in the evidence artifact, never an unstated universal set.

### Required semantic validation beyond shape

A receipt with phase=admitted has settlement=not_started or pending, and cannot alone prove dispatch. A receipt with phase=dispatch_started requires effect_id, attempt greater than zero and recorded current authority checks. A rejected command has settlement=not_started, no new effect dispatch, and a stable refusal cause. A tool_result_received receipt may still have settlement=pending or unknown; a tool's claimed success is insufficient to set succeeded.

phase=settled requires a permitted terminal settlement, independently supported execution_settled=observed_true and evidence appropriate to the effect's contract. Process/scope exit alone cannot settle a remote effect. phase=effect_unknown requires settlement=unknown and an explicit reason. A failed/cancelled result must not be rewritten as not_started after dispatch. Settlement corrections are new canonical transitions with evidence, never edits to an old receipt.

For exact duplicate commands, return the original committed receipt bytes. Do not emit a new canonical transition merely to acknowledge transport replay. A transport-level replay indicator is outside this immutable payload. Same ID with changed bytes yields a separate refused request observation without mutating the original command's committed receipt. This distinction prevents a replay counter from changing a supposedly byte-exact idempotent result.

RCPT-FIX-01 validates every allowed phase/settlement pair, each missing/extra field, wrong nullable type, oversized identifier, integer overflow, false digest domain, request-ID type collision, unknown-to-true coercion, truncated-as-complete output, invalid observation evidence and late result after Stop. It also crashes at receipt persistence cutpoints and replays identical commands. Any receipt that implies more than the retained evidence proves is a failure, even if the JSON shape is valid.

## 15 Lazy Stop observable boundary and escalation

### What Stop changes immediately

Lazy Stop is a durable request to reach a defined safe boundary without admitting new effects in the stopped scope. The canonical authority must record a Stop fence or pause epoch before reporting the request accepted. Dispatchers must recheck it immediately before each effect boundary, including after a command was previously admitted. Merely displaying stopping in a terminal is not a fence.

A qualifying boundary is effect-specific and independently observable: for example, a tool call has returned and its result/side effects are reconciled; a transaction is known committed or aborted; a child has exited and scoped/external work is reconciled; or a cooperative executor has reached a declared checkpoint before another effect. Output newline, progress notification, token generation, transport ACK, terminal detachment and silence are not safe boundaries by themselves.

Stop must separately expose request accepted, boundary reached, cancellation requested, forced termination requested, local scope verified empty and execution settled. The final user-facing status may be stopped with unknown effects when no stronger result is justified. That status is terminal for dispatch admission but not a claim that every effect was undone. Never label timeout or successful kill request as effect success, verified cancellation or full-tree termination.

### Proposed deadline and escalation defaults

STOP-01 is a proposed policy for Owner ratification. There is no universal safe forced-kill deadline across all effect types. Every effect adapter must declare its boundary, normal maximum duration, cancellation mechanism, forced-termination permission, irreversible/remote behavior and reconciliation query. If those are missing, new dispatch is refused as an undeclared effect policy. A pre-existing unknown effect is fenced and escalated for decision, not assigned an invented cancellation guarantee.

For a declared finite local read-only computation, the candidate default absolute request budget is 60 s. On Lazy Stop, allow up to 5 s to reach its declared cooperative boundary, then send its supported cancellation. Allow 5 s additional grace, then use the already approved managed-scope termination mechanism. Allow 20 s for independent verification. Report unknown if verification fails. These values match the qualification campaign and are proposals, not OS or MCP mandates.

For a local mutating operation, use the same stop fence immediately, but forced termination is allowed only if the adapter's approved crash/recovery contract defines how to recover its partial effects. Without that contract, stop new dispatch, request cancellation and expose the unresolved effect; do not invent a safe timeout-to-kill transition. For a remote or externally serviced operation, a local timeout cancels waiting and invokes an approved remote cancellation/reconciliation route, if one exists. Killing the requester never proves remote cancellation. Do not retry an unknown remote effect without approved idempotency or reconciliation.

For human-input-required operations, stop further dispatch immediately and cancel the pending interaction where supported. Do not leave a receipt implying a tool is still running simply because a UI waits. If a user later supplies input, it must pass the current Stop/authority guards; stale elicitation cannot resume a stopped effect. Long-lived subscriptions use a declared subscription lifecycle and heartbeat/idle policy, not a 60 s fiction that treats them as ordinary finite tools.

Progress notifications may update visible progress or a soft idle timer, but they must not extend the absolute effect deadline indefinitely. MCP recommends configurable timeouts and a maximum even when progress resets a timeout. Cancellation can race with completion and may not stop work that cannot be cancelled. SD, high confidence in the protocol guidance; the numeric and effect-class policy remains IN. [S06]

### STOP01 boundary absent oracle

STOP-FIX-01 uses synthetic effects for each declared class. One reaches a boundary just before the soft deadline; one just after; one emits endless progress; one ignores cancellation; one completes concurrently; one leaves a known remote operation active; one crashes before receipt persistence; one receives stale user input after the Stop fence. Observe the fence order, attempted dispatches, monotonic deadlines, cancellation and kill requests, process/scope state and reconciled effect outcome.

PASS requires no fresh effect dispatch after the fence, bounded escalation for the classes where it is approved, and truthful unknown status otherwise. Late evidence can settle an effect through a new verified canonical transition; it must not be discarded merely because the transport wait ended. Stop immediately on an unauthorized post-fence dispatch, premature succeeded/cancelled_verified receipt, or a test effect escaping its disposable safety boundary. No Stop fixture was run here.

## 16 Recommendations with competitors and falsifiers

Each item is IN, a decision recommendation rather than an adoption. Confidence in the need for the gate is high; confidence in the unrun implementation is unknown. The candidate numerical values have low-to-medium confidence until measured against an approved workload.

### R01 Keep the protocol on HOLD

Recommendation: retain conditional adoption and do not freeze until the four blockers and supported native cells pass independent review. Competitor: freeze a deliberately smaller exact-only profile with unsupported behavior expressly excluded. Decisive falsifier of HOLD necessity: a complete already-ratified contract package and independently reviewed evidence satisfying every required gate. Non-claim: a research report does not prove product failure or reopen previously accepted decisions.

### R02 Treat exact only as a support envelope decision

Recommendation: preserve exact-only /1 unless V-01 demonstrates that mixed-version interoperability is required and authorizes a new major. Competitor: new-major negotiation with explicit schema/capability agreement. Falsifier: the exact-only fleet cannot meet the approved supported-pair recovery/outage requirement, or two /1 peers accept but disagree semantically. Non-claim: refusal safety is not rolling-upgrade availability or semantic equality.

### R03 Require the real materialization contract

Recommendation: block snapshot acceptance until SM-01 identifies ratification, exact bytes and cut binding. Competitor: seek a new Owner-approved storage-neutral materialization contract if none exists. Falsifier: a proposed contract cannot yield identical verified bytes at the same approved cut across independent materializers, or mismatched-cut bytes pass verification. Non-claim: a digest or JCS standard does not identify an approved snapshot format.

### R04 Use durable incarnation before sequence reuse

Recommendation: ratify the tuple/lineage rule in C-01, with no sequence reuse under an old incarnation. Competitor: a new major using a larger unbounded-in-practice monotone cursor, while still retaining stream identity and restart semantics. Falsifier: crash/backup recovery reuses one cursor for different bytes or accepts a stale delivery. Non-claim: unique incarnation identifiers do not establish authority, durable storage or complete replay history.

### R05 Separate ACK release from credit grants

Recommendation: ratify section 6's forward/duplicate/backward contract and cumulative independent event/byte grants. Competitor: ACK-returned windows or additive CREDIT with a separately proven deduplication mechanism. Falsifier: any replay/race double-releases state or overgrants transmission, or independent implementations disagree on byte charge. Non-claim: a valid ACK proves no effect, persistence, rendering or user observation.

### R06 Preserve strict exhaustion RESET until changed

Recommendation: retain reset-requiring inability to enqueue an eligible EVENT, with control reserve and closure fallback. Competitor: explicit pause/resume under provably retained contiguous history. Falsifier: strict reset churn makes the approved healthy workload unrecoverable within its objective, or late credit resumes an invalidated delivery. Non-claim: this is a proposed compatibility-preserving interpretation, not evidence that unseen /1 text already contains it.

### R07 Decide framing by recovery semantics

Recommendation: evaluate bounded LP-JCS first for fail-connection/reconnect semantics and compare RS-JCS only against a stated in-stream recovery requirement. Competitor: RFC 7464 resynchronizing frames with the same semantic gap rules. Falsifier: FR fixtures show unchecked allocation, accepted corruption, divergent bytes or a failed recovery objective. Non-claim: neither wire choice selects a JSON library or proves parser correctness universally.

### R08 Bound and instrument every layer

Recommendation: use the explicit per-layer/global qualification profile and no-wait dependency checks. Competitor: a smaller set of views or a shared projection cache with independently bounded references. Falsifier: a stalled layer blocks canonical progress, violates a cap or leaks retained memory after detach. Non-claim: per-view queue bounds alone do not bound OS buffers, process memory or retention.

### R09 Claim only verified scope membership termination

Recommendation: creation-time containment plus independent membership/exit observation under FU04 profiles. Competitor: a separately qualified supervisor-mediated launch path or a deliberately weaker supported workload class. Falsifier: a supposedly contained birth escapes, scope kill leaves managed live work beyond the approved deadline, or an observer gap is called PASS. Non-claim: no complete descendant-tree or remote-work termination guarantee.

### R10 Pin modern MCP and enforce local caps

Recommendation: pin core 2026-07-28 with exact source/implementation profile; resolve closure ambiguity; independently test TOOL-LIMITS-01. Competitor: an explicitly bounded legacy-only adapter profile with its own support decision. Falsifier: wrong request/subscription correlation, source-profile mismatch, failure of required modern behavior, or overflow under malicious output. Non-claim: SDK v2, a standard conformance badge or subscription ACK does not supply product backpressure or safety.

### R11 Make receipts evidence typed

Recommendation: ratify the closed receipt schema and semantic validation, preserving unknown separately from zero/false. Competitor: reference only a canonical effect ledger and expose a smaller presentation receipt. Falsifier: a validly shaped receipt conveys a stronger effect outcome than its evidence, changes under exact replay or has self-referential digest semantics. Non-claim: schema validity is not truthful external observation or authorization.

### R12 Make Stop effect specific

Recommendation: immediate durable Stop fence, a declared observable boundary, absolute deadline and approved escalation/reconciliation. Competitor: immediate cancellation/kill for a narrowly proven safe workload class, or cooperative-only stop with explicit unbounded/unknown completion risk. Falsifier: a new effect is dispatched after the fence, progress extends the hard deadline indefinitely, or requester death is reported as remote cancellation. Non-claim: a timeout cannot undo irreversible work, and a kill cannot prove every effect settled.

## 17 Open Owner decisions

These are newly named decision inputs inferred from the handoff's open questions. They are not claims about the unseen contents of GAPS.md, and do not replace its recorded Owner questions.

1. V-01: exact-only /1 or a newly numbered negotiated major; supported version pairs, outage tolerance, schema package identity and downgrade policy.
2. SM-01: identify the already-ratified materialization contract with immutable acceptance evidence, or explicitly confirm a new contract decision is needed. Approve exact-cut semantics, digest domain and retrieval/size behavior without selecting a store here.
3. C-01: incarnation durability, uniqueness, rollover threshold before 2147483647, lineage and restoration behavior, and compatibility with clients lacking incarnation fields.
4. A-01: ratify exact ACK release, cumulative credit accounting, byte-charge basis, control reserve and strict credit-exhaustion RESET or authorize a separately specified pause/resume alternative.
5. FR-01: choose framing based on approved recovery objectives and the comparative corpus, without choosing a library.
6. LIMITS-01: ratify or revise the broker and tool numerical ceilings, workload rates, supported concurrency and performance thresholds before measurement.
7. PLATFORM-01: define native Windows/Linux support floors, supported privilege and Job/cgroup profiles, ConPTY build split, external-service exclusions and acceptable observer coverage.
8. MCP-01: choose exact revision/schema/adapter versions and explicitly resolve subscription teardown interoperability; enumerate any supported legacy revisions.
9. RCPT-01: ratify the closed receipt type/semantic contract, kernel-envelope mapping, evidence retention and redaction rules.
10. STOP-01: approve effect classes, deadline budgets, cancellation/kill permissions, crash recovery and reconciliation policy; unknown classes remain undeclared and inadmissible.
11. REVIEW-01: name the independent acceptance reviewer and evidence location; specify which matrix cells must pass for a bounded freeze and how exceptions are documented.

None of these decisions is silently taken by this report. No protected constitution or project configuration was changed.

## 18 Local execution handoff

The user plans to execute necessary tests with local agent sessions. This section is the concrete remaining work. It separates contract decisions from executable validation so agents do not fabricate missing specifications or treat an unapproved candidate as production authority.

### First obtain inputs without running target experiments

The local session must obtain V-01, SM-01, C-01, A-01, FR-01, LIMITS-01, PLATFORM-01, MCP-01, RCPT-01 and STOP-01, including approval status and immutable revision. It should reconcile these with the actual repository constitution and existing accepted decisions. If the real contract differs from BP-CAND-20261001, preserve the accepted contract and record the exact delta; do not overwrite it with this report.

Obtain FU03's approved byte corpus, manifest digest and independent implementations; FU04's exact platform fixture profiles and result schema; FU02's approved storage crash cutpoints and atomicity contract where needed. The preliminary cross-lane candidates described here are not substitutes for those approved artifacts. Archive exact public standards/specification sources and implementation versions, including current MCP closure interpretation.

Deliverable from this input stage: an approval and dependency manifest identifying present, missing, superseded and incompatible inputs. Stop dependent work when a required input is absent. A blocked input is not an excuse to invent a schema, weaken a guard or run privileged experiments without authorization.

### Local session A checks protocol interoperability

Execute V-FIX-01, A-FIX-01, FR-FIX-01, FR-FIX-02 and RCPT-FIX-01 with two independently authored implementations, reviewed literal input/output bytes and negative controls. Inputs are the approved version/schema matrix, framing and receipt contracts, exact byte corpus and limits profile. Evidence is the full request/response trace, expected-versus-actual byte comparison, refusal code, counters, allocations and absence/presence of dispatch.

Pass only when both independent implementations match the reviewed oracle, all rejection cases remain effect-free, and the duplicate/backward/overflow cases have the exact prescribed outcomes. Stop on admitted malformed commands, double effects, cap violations or contract ambiguity. Return the first counterexample with minimal reproducer bytes and all run identities; never patch the oracle to match one implementation without a new reviewed contract revision.

### Local session B checks snapshot and recovery

Execute SM-FIX-01, C-FIX-01 and REC-FIX-01, then CH14, CH17 and CH18. Inputs include SM-01's actual literal snapshot bytes, canonical event cuts, approved lineage durability and FU02 crash evidence. Evidence is each transition, materialized byte digest, accepted view cut, canonical event identity, durable command receipt and post-crash lineage.

Pass only with identical independent materialization, strict continuity, no stale-epoch acceptance and no same-cursor different-bytes reuse. Stop on missing ratification, missing literal bytes, unresolved durability, accepted wrong-cut snapshot, duplicate dispatch or effect ambiguity that is labelled success. Report unknown external effects explicitly. This session cannot qualify store behavior that FU02 has not established for the same profile.

### Local session C checks native platform containment

On each required native Windows and Linux profile, execute CH01 through CH09, CH12, CH19 and CH20 with positive/negative controls. Include both ConPTY build families if supported. Inputs are exact FU04 profiles, reviewed fixture code, disposable scope and separately authorized privilege/service setup. Evidence is independent birth/membership/exit traces, handle/descriptor manifest, API returns, scope-empty observations and cleanup receipts.

Pass each case only under its stated membership-limited claim and complete observation coverage. Stop immediately on escaped work outside the outer safety boundary, observer loss, unauthorized host changes or the safety deadline. A Windows PASS cannot qualify Linux, and WSL cannot substitute for native Linux. Record rejected or unknown cells instead of omitting them.

### Local session D checks isolation and overload

Execute ISO-FIX-01, CH13 and CH15 across every target transport/profile, plus MCP-01 overload variants. Inputs are the pinned workload, expected record sizes/rates, effective OS buffer measurements and numerical ceiling profile. Evidence includes raw latency samples, wait/lock dependency traces, all-layer high-water counts/bytes, process RSS, healthy-view lag, reset/closure traces and post-detach residual memory.

Pass only if both structural no-wait checks and quantitative thresholds pass. Stop on unbounded allocation, cap crossing, canonical-writer dependency, lost committed event or an unhealthy independent observer. If effective kernel buffers cannot be measured or enforced as assumed, mark that profile unknown and revise the profile explicitly before rerunning.

### Local session E checks tool and Stop semantics

Execute MCP-01, CH10, CH11, CH16 and STOP-FIX-01 using approved synthetic tool servers and effect classes. Inputs are exact modern/legacy protocol pins, declared request/cancellation policies, receipt schema and no-real-effect synthetic service. Evidence is interleaved MCP wire traces, independent effect counters, Stop fence order, deadlines, cancellation/termination/reconciliation and receipt truth predicates.

Pass only with bounded stderr/stdout handling, correct correlation, no output-to-authority promotion, no post-fence dispatch and truthful outcome classification. Stop on a real unapproved external target, authority promotion, incorrect request correlation or false settled status. Verify the subscription closure interpretation against actual pinned adapters; do not report the source discrepancy resolved merely because one adapter tolerated it.

### Independent review and bounded freeze decision

A different reviewer must inspect the manifest, all counterexamples and unresolved/unknown cells, not just a green summary. The freeze record must enumerate the exact supported contracts, versions, OS profiles and limits, and explicitly exclude unqualified cells. Every required blocker and matrix case must be accepted; otherwise the outcome remains HOLD with named residual inputs. A review cannot establish a product-wide claim from a narrower tested profile.

The local sessions should return: approved-contract manifest; corpus and fixture source/binary digests; exact environment profiles; raw traces and measurement samples; counterexample files; effect/command reconciliation ledger; cleanup evidence; per-case verdicts; independent review decision; and a concise list of remaining Owner decisions. No target executable command is invented in this report because no fixture implementation or repository entrypoint was supplied.

## 19 Completion gate and remaining status

| Handoff requirement | Research deliverable | Execution or decision status |
| --- | --- | --- |
| Four freeze blockers resolved or narrowed | V-01, SM-01, C-01, A-01 and decisive fixtures in sections 3–6 | Narrowed; contract approval and runs pending |
| Framing competitor and corrupt-stream falsifier | LP-JCS versus RFC 7464; FR-FIX-01 and 02 | No framing/library selected; unrun |
| Normative ACK credit RESET contract | Exact release/no-op/refusal; independent counters; strict exhaustion behavior | Candidate only; A-01 required |
| Every named containment escape path | CH01–CH20 each has injection, observation, recovery and stop | Explicit preregistration; all unrun |
| Membership-limited containment | Sections 10–12 | No full-tree claim; host qualification unknown |
| MCP version and numeric bounds | Core 2026-07-28 with immutable release baseline; local caps separately labelled | Actual adapters/configuration unknown; closure discrepancy remains |
| Command receipt schema | Closed types, fields, enums, null semantics and semantic checks | Candidate schema; RCPT-FIX-01 unrun |
| Lazy Stop and false-green rule | Section 15 and CH20 | Effect policy requires approval and tests |
| Conditional freeze and no selection | HOLD throughout; restricted choices preserved | Owner decision and independent acceptance absent |
| Protected paths and privacy | New report only; deliverable scan recorded separately | No target/protected path edits; not a repository-wide audit |
| Local session leftovers | Five executable validation work packages plus input/review stages | Exact inputs, evidence, pass/fail and stop supplied |

Research completion means that the requested decision materials are provided and missing evidence is named. It does not mean the protocol is frozen, fixtures passed, a platform was qualified or an unseen ratified contract was recovered. The final acceptance decision remains with the Owner after independent review.

## 20 Primary source and freshness register

Sources were read on 1 October 2026 UTC unless otherwise stated. The immutable MCP schema baseline and RFC errata were rechecked on 2 October 2026 UTC while finishing the report. Version-qualified URLs and named document revisions are used below; mutable documentation is explicitly identified. An expiry means revalidate before relying on the claim, not that the old source becomes false on that date. All implementation applicability remains unverified until the local runs.

### S01 MCP stable release

[Official MCP 2026-07-28 release](https://github.com/modelcontextprotocol/modelcontextprotocol/releases/tag/2026-07-28) and [release commit 5f5440bb26a62e2cf3440b92da5a667efa03b267](https://github.com/modelcontextprotocol/modelcontextprotocol/commit/5f5440bb26a62e2cf3440b92da5a667efa03b267). Pin: stable dated release plus immutable commit. Supports the release identity, not installed adapter conformance. Classification SD; confidence high. Current-version freshness expires 1 November 2026 or sooner on a new release; immutable historical identity does not expire.

### S02 MCP versioning

[Versioning and Compatibility for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning). Pin: protocol revision and access date; mutable official page. Supports per-request version, modern/legacy distinction, supported-version refusal and -32022. Classification SD; confidence high for inspected content. Recheck before the first local run or by 1 November 2026, whichever occurs first. Does not select the broker version strategy.

### S03 MCP base protocol

[Basic protocol for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic). Pin: protocol revision and access date; mutable page. Supports stateless per-request metadata, schema source of truth and qualitative validation resource guidance. Classification SD; confidence high. Expiry: first local qualification or 1 November 2026. Does not supply the report's numerical ceilings.

### S04 MCP stdio

[stdio binding for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio). Pin: revision and access date; mutable page. Supports newline framing, protocol-only stdout, stderr separation, shared response/notification channel and shutdown guidance. Classification SD; confidence high. Expiry: first local qualification or 1 November 2026. SDK buffer defaults remain unknown.

### S05 MCP subscriptions

[Subscriptions for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions) and [immutable subscription text at e76e9c572c6f2bfcb730357101acc90f2f802e02](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/e76e9c572c6f2bfcb730357101acc90f2f802e02/docs/specification/2026-07-28/basic/patterns/subscriptions.mdx). Supports subscription acknowledgment, filtering, correlation, reconnection and graceful completion-response wording. SD; high confidence that the words appear, reduced interoperability confidence because S06 differs. Recheck immediately before local qualification; historical text remains fixed.

### S06 MCP cancellation

[Cancellation for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/cancellation) and [immutable cancellation text at e76e9c572c6f2bfcb730357101acc90f2f802e02](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/e76e9c572c6f2bfcb730357101acc90f2f802e02/docs/specification/2026-07-28/basic/patterns/cancellation.mdx). Supports transport-specific cancellation, timeout guidance, races and the conflicting subscription-teardown wording. SD; high confidence in inspected text, unresolved normative alignment. Expiry: before any MCP teardown acceptance run.

### S07 MCP schema

[Immutable schema at stable release commit](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/5f5440bb26a62e2cf3440b92da5a667efa03b267/schema/2026-07-28/schema.ts) and [current dated schema on main](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2026-07-28/schema.ts). The first is the reproducible baseline; the second was inspected for current declarations and must not be treated as immutable. SD; high confidence for the inspected definitions. Recheck source drift before local qualification. No full schema-diff or SDK compatibility run was performed.

### S08 JCS

[RFC 8785 JSON Canonicalization Scheme](https://www.rfc-editor.org/info/rfc8785/). Pin: June 2020 RFC, especially sections 3.1 and 3.2. Supports canonical JSON mechanics and input constraints, not broker framing or snapshot semantics. SD; high confidence. Historical RFC text is stable; check errata before corpus freeze. This RFC is Informational, not an Internet Standards Track protocol.

### S09 JCS errata

[RFC 8785 verified errata](https://www.rfc-editor.org/errata/rfc8785). Pins: technical erratum 7920 verified 15 May 2024 and editorial erratum 6292 verified 22 September 2020, as inspected. Supports the negative-zero security recommendation and corrected ECMAScript section reference. SD; high confidence. Recheck before byte-corpus ratification and at most 90 days after this report. The broker's acceptance policy for affected inputs must be explicit.

### S10 JSON Text Sequences

[RFC 7464 JSON Text Sequences](https://www.rfc-editor.org/info/rfc7464/). Pin: February 2015 Standards Track RFC, sections 2 and 3. Supports RS/LF framing, truncation and resynchronization considerations. SD; high confidence. RFC text is stable; recheck errata before corpus freeze. It does not authorize skipping broker semantic events.

### S11 Windows creation attributes

[UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute). Pin: official API page accessed 1 October 2026, specifically JOB_LIST, HANDLE_LIST and PARENT_PROCESS attributes. Supports creation-time Job-list availability on documented Windows generations. SD; high confidence in API documentation, host availability unverified. Recheck for the exact supported Windows build and SDK at each qualification change; maximum freshness 90 days.

### S12 Windows Job behavior

[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects). Pin: page last updated 14 July 2025, accessed 1 October 2026. Supports association, child/breakaway exceptions, nested behavior, termination scope, nonguaranteed completion messages and last-handle kill-on-close. SD; high confidence in documented scope, not an implementation result. Revalidate per Windows build/Job policy change or within 90 days.

### S13 Linux creation in cgroup

[clone and clone3 Linux manual](https://www.man7.org/linux/man-pages/man2/clone.2.html). Pin: accessed manual edition and CLONE_INTO_CGROUP section; feature documented since Linux 5.7. Supports creation directly in a cgroup v2 under applicable restrictions. SD; high confidence in documented API; actual kernel configuration/seccomp/privilege availability unknown. Recheck on kernel or launch-path changes, before the first native run.

### S14 Linux cgroup v2

[Linux 6.12 cgroup v2 documentation](https://docs.kernel.org/6.12/admin-guide/cgroup-v2.html). Pin: version-qualified kernel documentation, delegation containment, populated state and cgroup.kill sections. Supports membership and kill scope, permissions and live-process observation semantics. SD; high confidence for that documented version. It is a source baseline, not a selected minimum kernel. Revalidate against the actual target kernel and patchset; no cross-version qualification is inferred.

### S15 Windows pseudoconsole closure

[ClosePseudoConsole](https://learn.microsoft.com/en-us/windows/console/closepseudoconsole). Pin: page updated 9 July 2025, accessed 1 October 2026. Supports the Windows 11 24H2 build 26100 behavior seam, continued output and older-build deadlock warning. SD; high confidence. Recheck for each Windows/ConPTY profile change or within 90 days. Return/EOF is not Job-empty evidence.

### S16 Linux PTY

[Linux pty manual](https://man7.org/linux/man-pages/man7/pty.7.html). Pin: accessed Linux man-pages source on 1 October 2026. Supports PTY master/slave context, not a guarantee of process-tree death when a terminal closes. SD; high confidence for the described interface. The report's teardown cases and oracles are IN. Revalidate on kernel/terminal stack changes before qualification.

### S17 Linux local socket semantics

[Linux unix manual](https://www.man7.org/linux/man-pages/man7/unix.7.html). Pin: accessed source on 1 October 2026, pathname/abstract namespaces and permissions sections. Supports local transport distinctions and nonportable abstract namespace behavior. SD; high confidence for Linux, no BSD equivalence asserted. Revalidate on platform/security-profile changes; endpoint-admission implementation remains unverified.

### S18 Windows named pipe endpoint

[CreateNamedPipeA](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea). Pin: official API page accessed 1 October 2026. Supports remote-client rejection option and transport configuration distinctions. SD; high confidence for API meaning, actual ACL/peer verification not observed. Revalidate on Windows build or endpoint-policy change, before qualification. A pipe name does not prove identity.

### S19 Pipe buffering

[Linux pipe manual](https://man7.org/linux/man-pages/man7/pipe.7.html). Pin: official Linux man-pages source accessed 1 October 2026. Supports finite pipe capacity and blocking behavior; no cross-platform numeric buffer value is imported. SD; high confidence. Dedicated stderr draining and proposed ceilings are IN. Revalidate actual transport buffers on every target profile.

### S20 MCP tools

[Tools for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/server/tools). Pin: dated official specification page accessed 1 October 2026. Supports output schema context, untrusted tool annotations, tool results and multi-round-trip request ID behavior. SD; high confidence for inspected text. Broader result-to-authority separation is the handoff's fixed constraint and this report's proposed enforcement. Recheck before local compatibility runs or by 1 November 2026.

### S21 MCP closure discrepancy report

[Official repository issue 3348](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/3348). Pin: opened 6 September 2026; displayed open when inspected. This is a primary report of a specification discrepancy, not normative authority. The report independently checked the two linked official texts. SD for existence/status at inspection; confidence high for the discrepancy, unknown for unseen SDK behavior. Issue status expires immediately for future decisions; recheck before resolving MCP-01.

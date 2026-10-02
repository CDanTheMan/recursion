# FU-05 — broker protocol and native chaos (synthesis)

## Provenance

This synthesis summarizes `raw/ds-FU-05-broker-chaos.md` (its own title: "Broker protocol
freeze blockers and native chaos specification"). The underlying work is research and
specification only; the report's sources are public primary sources (mutable specification
pages plus immutable release/commit pins) read around 1–2 October 2026 UTC, and no target
process, socket, model checker, native fixture or broker implementation was launched. The
proposal is labeled candidate specification BP-CAND-20261001, not a ratified contract; all
fixtures below are unrun, and this synthesis adds no verification of its own.

## The question

Is the Recursion v3 broker protocol ready to freeze, and if not, what exact decisions and
falsifiable fixtures would close the gaps? The report answers no: it narrows four freeze blockers
to named Owner decisions and preregisters a native Windows/Linux chaos campaign. A secondary
question is how the separate MCP tool-broker boundary, command receipts and Lazy Stop semantics
should be pinned and bounded without promoting an adapter or upstream result into authority.

## Key findings

**Four freeze blockers, narrowed but unresolved.**

1. **V-01 — version admission.** Exact-only `m1b-broker/1` can safely refuse unimplemented
   versions if refusal happens before command admission, state allocation beyond the bounded
   handshake, or effects. Its costs are operational (stranded detached clients after upgrades,
   no mutual discovery of a supported subset, coordinated rolling upgrades, risky interpretation
   of unknown future fields). The Owner must choose an exact-only compatibility envelope with an
   exact accepted wire/schema package, or authorize a new negotiated major. The report proposes
   HELLO/WELCOME negotiation with typed pre-admission refusal codes and warns that a shared
   version string cannot protect against implementations with different schemas or semantics.
2. **SM-01 — snapshot materialization.** Named as the most important unresolved dependency. The
   supplied handoff identifies no already-ratified contract that turns `SNAPSHOT.snapshot_digest`
   into verifiable bytes at a specific cursor. A digest alone does not define a projection, its
   serialization, its cursor binding or byte retrieval. The report refuses to substitute RFC
   8785, a store checkpoint, a renderer screenshot or a new schema, and requires SM-01 to supply
   the ratification and byte-evidence package. Until then snapshot recovery is unverified and
   the fixture is BLOCKED, not PASS.
3. **C-01 — cursor incarnation and rollover.** A bare integer cursor cannot distinguish a new
   stream from a restart or wraparound. The candidate cursor is `stream_id, incarnation_id,
   sequence`, with `sequence` bounded in 0..2147483646; zero denotes the approved initial
   snapshot cut and 2147483647 is reserved. Rollover needs a durably crash-consistent transition
   record linking old incarnation, old final cursor, new incarnation, new starting cut and a
   predecessor-transition digest. Durable lineage authority, backup/restore behavior, split-brain
   reconciliation and `/1` compatibility without incarnation remain to be ratified.
4. **A-01 — ACK, credit and RESET wording.** Proposed wording defines forward, duplicate (no-op)
   and backward/refused ACK outcomes evaluated atomically against the current `delivery_epoch`/
   `reset_epoch`, separating ACK release from credit grants. CREDIT carries cumulative
   `credit_seq`, `grant_events_total` and `grant_bytes_total`; every EVENT debits event and exact
   encoded-byte charge once before enqueue, with no refund on ACK. The candidate preserves
   strict reset-requiring exhaustion: an eligible next EVENT that cannot be enqueued sends the
   view to RESET_REQUIRED rather than skipping or silently resuming. A PAUSED_FOR_CREDIT
   alternative is named as a deliberate contract change, not silently adopted.

**Proposed protocol revision (BP-CAND-20261001).** Beyond the four blockers the report proposes:
JCS canonical JSON (RFC 8785 with errata/normalization policy) and a framing choice between
LP-JCS (four-byte big-endian length prefix) and RS-JCS (RFC 7464 RS/LF resynchronizing frames);
an explicit per-layer bounded qualification profile (record, accumulator, decode, EVENT window,
projection, render sink, snapshot staging, control reserve, active views, per-view and global
memory, OS buffers, reset recovery); a recovery state machine (PRE_ADMISSION, READY_TO_RESUME,
RESET_REQUIRED, SNAPSHOT_LOADING, SNAPSHOT_ACK_PENDING, STREAMING) with bound `delivery_epoch`/
`reset_epoch`; a closed command-receipt schema TOOL-RECEIPT-01; and Lazy Stop semantics (STOP-01)
with an effect-specific safe boundary, absolute deadline and approved escalation/reconciliation.
It also corrects the MCP core pin to 2026-07-28 (not 2025-11-25) and notes a live
subscription-teardown discrepancy between the cancellation and subscriptions pages. All of the
above are **proposed**; none is measured or ratified here, and the report selects no renderer,
multiplexer, GUI toolkit, IPC library, serialization library, cursor store, snapshot format,
retention engine, default language or runtime.

## Recommendation and falsifier

The report recommends keeping the protocol on HOLD (R01) and retaining conditional adoption
until the four blockers and the supported native cells pass independent review. Exact-only `/1`
should be preserved unless V-01 demonstrates that mixed-version interoperability is required
and authorizes a new major (R02). Snapshot acceptance should be blocked until SM-01 identifies
ratification, exact bytes and cut binding (R03). Incarnation lineage should be ratified with no
sequence reuse under an old incarnation (R04). ACK release should be separated from credit
grants (R05), and strict exhaustion RESET retained until deliberately changed (R06).

The decisive falsifier of the necessity of HOLD is a complete, already-ratified contract package
plus independently reviewed evidence satisfying every required gate. Per blocker: two peers
admitted under a shared version name that then disagree semantically, or any side effect before
admission, falsifies version safety; materializers that cannot produce identical verified bytes
at the same approved cut falsify materialization; same-cursor/different-bytes reuse or accepted
stale delivery falsifies incarnation; a replay/race double-release or byte-charge disagreement
between independent implementations falsifies the ACK/credit contract; unchecked allocation,
admitted corruption or divergent bytes falsify the framing preference. Correct rejection is not
success.

## Local execution handoff

The report separates contract decisions from executable validation. Key fixtures to run:

- **Version/interoperability:** V-FIX-01 — two independently authored clients and two servers
  over the reviewed version/schema matrix (exact match, major mismatch, interval intersection,
  incompatible schema, capability deletion, unknown fields, malformed lengths, duplicate HELLO,
  WELCOME replay, refusal truncation, downgrade retry).
- **Snapshot/recovery:** SM-FIX-01 — HELLO → WELCOME → replay-gap detection → RESET → SNAPSHOT
  → SNAPSHOT ACK → CREDIT → EVENT, with wrong digest, wrong cursor, wrong projection, modified/
  missing/duplicate/out-of-order/truncated chunks, eviction, unknown incarnation and crash at
  each transition. REC-FIX-01 covers exact end-to-end recovery and command identity.
- **ACK/credit edge cases:** A-FIX-01 — forward/duplicate/backward ACK vectors, exact byte
  charges, credit-vs-ACK independence, exhaustion with one event credit and 100 byte credits for
  a 101-byte frame, concurrent ACK/CREDIT serialization, torn ACK, stale-epoch ACK, duplicate
  and conflicting CREDIT.
- **Rollover/incarnation:** C-FIX-01 — synthetic stream seeded at 2147483644 through the
  boundary, crash before/after transition persistence and exposure, snapshot install, stale
  WELCOME/ACK, duplicate incarnation IDs, restored old state.
- **Framing:** FR-FIX-01 (LP-JCS torn/corrupt corpus) and FR-FIX-02 (RS-JCS delimiter corpus).
- **Slow readers/isolation:** ISO-FIX-01 and CH13 — stalled views at every layer with no-wait
  dependency traces and preregistered performance thresholds.
- **Replay gaps:** CH14 (retention eviction at every transition) and CH17 (writer commit and
  receipt crash windows).
- **Containment escapes:** CH01–CH09 and CH19–CH20 — birth-time membership, Windows breakaway,
  Linux migration, nested Jobs, external-service work, abrupt broker death, leaked handles,
  ConPTY and Linux PTY teardown, scope-kill races and observer-failure/false-green controls.
- **Tool/Stop boundary:** MCP-01 (two adapters, modern and legacy pins, overload), RCPT-FIX-01
  (receipt shape and semantics) and STOP-FIX-01 (boundary-absent effects).

The report maps sessions A–E: A protocol interoperability, B snapshot and recovery, C native
platform containment, D isolation and overload, E tool and Stop semantics, followed by
independent review. No fixture implementation or repository entrypoint was supplied, so no
executable command is invented; **implementation is not done**.

## What this does not prove

This is decision evidence, not implementation acceptance: no target experiment was run, so no
PASS exists, and public protocol standards cannot establish an internal ratification. A digest
does not define a projection, and the report makes no full descendant-tree termination claim;
the strongest defensible claim is membership-limited termination of live processes inside an
identified managed scope after an approved termination operation and independent verification.
The MCP standard does not supply the broker's CREDIT/replay contract, SDK v2 is not a protocol
revision, and numerical ceilings are local policy proposals, not mandated values. A transport
ACK does not prove an effect settled, a renderer is safe, a process exited or a tool claim true;
the report selects no language, store, renderer, framing, snapshot format or retention engine,
and does not recover unseen ratified contracts from CONTROL_PLANE.md, GAPS.md or private records.

## Open Owner decisions

V-01 (support matrix, outage tolerance, schema package identity, downgrade policy); SM-01
(ratification/byte-evidence package, exact-cut semantics, digest domain, retrieval/size
behavior); C-01 (incarnation durability, uniqueness, rollover threshold, lineage, restoration,
`/1` compatibility); A-01 (ACK release, cumulative credit accounting, byte-charge basis,
control reserve, strict exhaustion or a specified pause/resume alternative); FR-01 (framing by
recovery objective); LIMITS-01 (broker and tool ceilings and thresholds); PLATFORM-01 (native
support floors, Job/cgroup profiles, ConPTY build split, service exclusions, observer coverage);
MCP-01 (exact revision/schema/adapter pins and subscription-teardown resolution); RCPT-01
(receipt type/semantic contract, kernel-envelope mapping, retention, redaction); STOP-01 (effect
classes, deadline budgets, cancellation/kill permissions, reconciliation); REVIEW-01 (named independent reviewer, evidence location, required cells).

## Relevance to later waves

FU-05 consumes FU-03's candidate byte corpus, event-identity vocabulary and conformance automata
as test-interchange interfaces only, and consumes FU-04's candidate `profile_key`/platform
result schema for its native chaos cells. It depends on FU-02 for approved storage crash
cutpoints and atomicity evidence where recovery and receipt fixtures cross the writer boundary.
The inventory/corpus/dependency manifest from this report is the input gate for any later broker
implementation wave; the HOLD means later waves may build fixtures and ratify contracts, but
must not claim a frozen protocol, qualified platform or settled effect semantics until the named decisions and independent runs exist.

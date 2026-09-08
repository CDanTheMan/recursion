# SC-WIRE-02 findings — 2026-09-08

Parent goal-recursion-v2-execution-fabric. The declared16 synthetic configurations
close at4,480 states and10,240 edges per representation, including304 distinct
literal wire histories summed across configurations. Counts include repeated
states between configurations. Both independently written reducers agree on every
enabled edge; a third complete initial/action/postcondition relation checks each.
Every distinct emitted history passes immutable strict schema and oracle checks
with the expected intermediate refused-gap or recovered accepted-reset disposition.

WELCOME establishes GAP and advances wire cursor; RESET clears old credit and
receiver pending. Fresh CREDIT may arrive before installation, but EVENT waits
for independent application installation. Source future entries survive that
installation. Byte and event credit and receiver queue limits are checked
separately. Lost ACK emits nothing and holds pending; retry releases pending once
without creating credit. Receiver restart before installation or with pending EVENT
preserves intact ownership. It does not model daemon epoch change or power loss.

The immutable snapshot records zero reservations at its older cursor. Its installed
cursor is separate from wire/ACK cursors. Current authoritative owner/op remains
six reserved and four free through install, restart, quota and control. This is
an explicit boundary assumption/noninterference check. The original two6-unit
requests from10 are preserved in unchanged SC-WR-01, not reconstructed by this
constant boundary. The coupled shared-reservation/wire product remains required.

Six reachable local guard removals expose installation bypass, reservation release
on install/restart/quota, false pending release on lost ACK and future source loss.
Thirteen literal cases include positive recovery and the wire-only limitation,
plus unexpected RESET, GAP continuation, missing/reused credit, stale epoch, stream,
unit, byte advancement, queue and ACK violations. Ten strict decoder/type controls
include valid oversized JSON so byte-ceiling removal cannot hide behind invalid
syntax. Five checker calibrations reject wrong reservation/view initialization,
omitted edges, no-op effects and truncation. These are local synthetic experiments,
not observed transport/SDK/parser integration or proof of arbitrary histories.

Independent challenge caused three prospective strengthening slices. Run01 failed
counterexample recording after normal graphs closed; run02 through04 are superseded
passing attempts with their actual sources; run05 is accepted. All remain hash-bound
externally. Full final readiness still requires two exact clean full gates and two
independent exact reviews, outside this candidate. Original6 obligations,27 rows,
eight experiment families, six cross-area cases and all integration routes remain.
No full formal freeze, authenticated snapshot, physical durability, production
integration, common-writer migration or liveness claim. No new Owner decision.

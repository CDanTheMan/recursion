# SC-WIRE-02 prospective specification — 2026-09-08

Parent goal-recursion-v2-execution-fabric. goal.json freezes baseline, allowlist,
resources, four-hour deadline and90-minute final reserve before execution.

Compare independently implemented split producer/receiver/application ownership and
inclusive records against independent enabledness and per-edge postconditions.
GAP is a modeled retention fact conveyed by WELCOME, never an invented wire message.
HELLO0, WELCOME floor1/snapshot1 establishes a gap; only RESET may next cross the
wire. RESET clears receiver pending and old credit. A fresh CREDIT is required for
EVENT, and local application installation must precede EVENT separately. WELCOME
and RESET wire cursors do not establish installation or authenticate snapshot facts.
All emitted messages use immutable M1B schema and replay oracle, unmodified.

Declare16 configurations: cursor units event/utf8-byte; payload sizes1/2; receiver
queue event limits1/2 and byte capacities1/2 payloads. Each has two source events
strictly newer than immutable snapshot1, two fresh credit grants, one local receiver
restart, one failed ACK, one independent Owner control and one quota reset. The
initial old credit is explicitly emitted before WELCOME gap. Every enabled finite
interleaving is enumerated including distinct wire histories; no schedule sampling.
Restart is local receiver recovery under intact persistent state and unchanged daemon
epoch, never a claim that a daemon restart can reuse its old epoch. Restart is
available after RESET and before installation, or after first EVENT before its ACK;
retain both witnesses. Lost ACK emits no wire message and cannot release pending.
Application installation is separate from transport reset and from immutable snapshot
capture; source queue and receiver pending are never aliases. Snapshot content says
zero reservations; an outstanding fixed owner/op reservation holds six of ten with
four free. This is a boundary assumption and noninterference check, not the complete
SC-WR-01 product. Original two6-unit requests from10 remain frozen in that gate.

No EVENT may overrun either credit dimension or receiver pending limit. ACK releases
pending only and does not replenish credit. Install, restart, quota reset, failed ACK
and control cannot change reservation ownership. No trace launches work. Retain
original full flow/ingress bounds through the unchanged flow-recovery predecessor;
add literal malformed framing/type controls through the immutable strict decoder.
Synthetic wire vectors are modeled, never observed upstream. No transport, physical
crash, SDK, authenticated snapshot or full common-writer integration claim.

Negative controls distinguish unexpected RESET, stale daemon epoch, EVENT before
RESET, EVENT before fresh credit, reused exhausted credit, ACK without fresh grant,
queue overflow, byte exhaustion, wrong cursor unit and byte cursor. Independent
local mutants must expose early installation bypass, false pending release on lost
ACK, source-tail erasure and reservation release on install/restart/quota. The wire
oracle can accept early application delivery; that limitation is an explicit positive
control for the need for local obligations. Checker calibrations must detect omitted
edges, wrong initial ownership, no-op effects and truncation. A bound hit is incomplete.

Keep6 original obligations and27 trace rows with partial flow/replay and uncertainty
support only. SC-EPOCH-03 follows as its own campaign. A coupled reservation/wire
product remains required before aggregate promotion, followed by remaining original
coverage; no language/store/framework selection or operational change.

Prospective revision2: retain the actual immutable (cursor,zero-reservations) snapshot
record and separate installed snapshot cursor, including byte-unit cursor2. This
cursor records snapshot installation, not subsequent incremental renderer progress.
Run01 failed while recording a guard-removal enabledness witness; no semantic pass
was admitted. Run02 passed the earlier equivalent fixed snapshot boundary and is
superseded by this explicit cursor representation before final evidence.

Prospective revision3 after independent challenge: add correctly typed UTF-8 byte
cursor with wrong advancement and a syntactically valid oversized JSON object.
Require the exact byte-ceiling error so malformed syntax cannot make that negative
control pass vacuously. Earlier run03 remains superseded before admitted rerun.

Prospective revision4: independent review found initial flags/view/ACK/wire fields
underconstrained. The independent audit now requires every initial field and exact
initial HELLO/CREDIT bytes; add wrong-initial-view calibration. Run04 is retained
superseded. This strengthens the independent obligation without reducing the model.

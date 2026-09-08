# SC-WR-01 findings — 2026-09-08

Parent: goal-recursion-v2-execution-fabric. This campaign constructs the missing
shared-pool and uncertain-effect reservation slice. It does not complete the
original formal comparison, establish production integration or release the
common-writer migration blocker.

| Design | Complete declared exploration per representation | Consequence |
| --- | --- | --- |
| Serialized central admission | 78,066 states;517,813 edges across19 environments | One atomic current-pool admission serves six and leaves four; competing6-unit request refuses. |
| Two holders with one durable transfer | 64,084 states;417,008 edges across the same19 environments | Initial5/5 cannot serve six; a committed1-unit transfer enables its destination. |

Counts sum environments and include repeated states; these are not unique full
original core/cross product counts. Every frontier closes. Both independently
implemented representations match exactly within each design, with complete
independent initial, enabledness, per-edge postcondition and invariant checks.
No fields affecting authority or resource ownership are hidden. Across designs,
safety obligations match but admission availability differs; no graph equivalence,
latency advantage or fairness theorem is claimed. The free core supplies unordered
interleavings; constrained profiles supply exact ordered boundary witnesses.

The conserved quantity is free+in-flight+reserved+consumed=10. Successful settlement
moves six reserved to six consumed and leaves only four available. A verified
terminal nonexecution releases six exactly once, while the request tombstone
prevents a duplicate from receiving a fresh grant. In the rights design, that
release returns rights to the original holder; it does not automatically rebalance
the other holder. Neither worker lifetime nor provider-window reset changes this
cumulative effect allowance.

A reservation stores its fixed pool/goal/operation/attempt/payload/owner/amount
tuple. Incoming owner, payload, goal, amount and attempt conflicts are refused by
actual tuple comparisons. Intent append and send are separate from reservation
commit. Restart after each of reserve, intent and send preserves the durable
binding; send-before-remote-outcome already carries uncertainty. Remote acceptance,
lost receipt, restart, envelope replay, matching duplicate request and blocked
resend leave the same operation unknown with six held. Local exit/wait, a new
incarnation, two lifetime compute units and quota reset preserve that reservation.

Receipt arrival, pure classification and accounting reconciliation are separate.
A successful classification with conflicting evidence still holds the reservation.
Canonical quarantine persists. The classifier is a restricted symbolic relation;
it is not a new literal M1C implementation or a runtime evidence bridge. Existing
literal M1 gates remain unchanged and are revalidated separately.

Old copied presentation content can show zero reservations while current durable
state holds six. Its installed cursor differs from the envelope replay cursor.
Replay observes the intact durable envelope revision; it does not rebuild a full
JSONL event log. Generation/reader-pin release changes reader ownership, not effect
reservation ownership. Complete broker/receiver credit, queues, framing and wire
correspondence remain SC-WIRE-02.

The rights relation commits a source debit before a separate destination
application; in-flight counts the right between those commits. A durable applied
marker makes duplicate installation a stutter, including installation -> restart
without ACK -> duplicate installation. Timeout never reclaims unknown rights.
Restoring an old presentation snapshot cannot roll back that ledger. These are
explicit finite durable-state transitions under intact persistent-memory and
serialized authenticated-holder premises, not physical crash/power-loss tests.

Nineteen guard mutations fail independent obligations. Central stale reads admit
reserved(6,6), exposing the original twelve-from-ten fault. Removing uncertainty
retention loses backing after restart, replay, exit, quota reset or old snapshot
installation. Removing duplicate credit/debit/timeout guards manufactures rights.
The snapshot-rights control fails a forbidden-authority-rollback postcondition;
it is not reported as12-unit oversubscription. One transfer can expose minted
rights but cannot exercise the two-opposite-transfer12-unit schedule. Five checker
calibrations reject wrong initialization, omitted edges, changed status, a present
but no-op admission, and truncated exploration.

Independent preliminary review exposed concrete gaps in early attempts. Run01
lacked the free core; run02 lacked concrete identity comparisons and explicit
replay/terminal-duplicate/crash-cut/lost-ACK witnesses. Both remain retained as
superseded passing experiments, not admitted final evidence. Run03 contains the
repaired model, about51.8 seconds and227,835,904 observed peak bytes on the admitted
Windows/Python host. This is resource admission evidence, not comparative runtime
performance. Source/command/host/raw hashes and dispositions are in evidence.json.

Canonical dispositions: retain central serialized admission as the mandatory
baseline; retain the rights design as a scoped optional comparator under its
stated durable-transfer premises. Reuse immutable M1 oracles and prior gates;
adapt the reservation and ownership boundaries in subsequent composition. New
Python is local experiment code, not a product language or store decision. No
upstream code, dependency installation, provider trial or new metered spend was
introduced. Account allowance was read; no reset credit was consumed.

All six original obligations and27 rows remain with exact historical evidence and
scoped new support. SC-WIRE-02 then SC-EPOCH-03 remain successors, with a coupled
check before aggregate promotion. General identity/ownership changes, multi-transfer
recovery, receiver relocation/record retirement, physical persistence, authenticated
writers, full core/cross closure and unbounded liveness remain unproved. No new
Owner decision is needed. Final readiness requires the two exact-candidate full
gates and two independent reviews recorded externally; this file alone is no
completion attestation.

# SC-WR-01 shared admission and reservations — 2026-09-08

Parent: goal-recursion-v2-execution-fabric. Frozen start, allowed paths, four-hour
envelope and90-minute synthesis reserve are in goal.json; prospective resources
are in plan.json/preflight.json. This specification precedes model execution.

## Designs and independently checked boundaries

Two goals A/B each request SIX integer effect-budget units from a fixed TEN-unit
parent pool. This is cumulative allowance, not a reusable concurrency semaphore.
Maintain free rights F, unresolved reservations R and settled consumption C.
Central admission serializes the check and durable reservation across both goals.
Its competing conserved-rights design starts holders at(5,5), admits locally only
from owned rights, and permits one transfer of ONE right from B to A. Mirror the
holder identities in a second environment. Neither design resets parent allowance.

Each design has an independently implemented inclusive record and authority/broker
record pair. Check both against a third complete transition relation, per-edge
invariants, enabledness and field ownership. Flattening preserves every field;
exact graph correspondence applies BETWEEN representations of the SAME design.
It is not claimed between central and rights admission. Central can serve six
immediately; rights may reject until transfer. Compare their safety and visible
admission behavior separately, with a concrete distinguishing availability trace.
No fairness, remote response or eventual transfer delivery is assumed.

## Durable pool and effect relation

Each request is bound to a fixed pool, goal, logical operation, attempt, six-unit
amount, payload and authorized owner. Owner/changed-payload probes reject; a
matching duplicate returns the durable disposition, including after a release.
A reservation commit precedes a separate dispatch-intent append; a separate send
marks the attempt ambiguous BEFORE remote acceptance. External success/refusal,
receipt loss, receipt arrival/query, pure classification and canonical accounting
reconciliation are different transitions. No resend of an ambiguous attempt is
admitted, including after process exit, replay and restart. Recipient behavior is
uncooperative: the receipt may remain lost permanently. A successful remote effect
is an environmental fact and does not itself settle local accounting.

A trusted exact successful receipt moves six R to six C through explicit
reconciliation. An exact terminal nonexecution receipt releases six R to free
rights through explicit reconciliation. Settlement is idempotent. Classification,
conflicting evidence hold and canonical quarantine are separate; classification
alone cannot release R, and a conflict blocks reconciliation. Quarantine is never
silently cleared by this model. Receipt authenticity/completeness and the fixed
identity mapping are declared environment premises, not production authentication.

Conservation is sum(F)+in_flight+sum(R)+sum(C)=10; separately sum(R)+sum(C)<=10.
R backs every sent operation without a committed terminal disposition. Local
worker lifetime, quota epoch/current-window usage, generation and reader pin,
classification/hold, copied presentation snapshot and installed cursor are distinct
fields. None can manufacture effect allowance. Unknown outcomes do not become zero.

## Durable transfer relation and crash boundary

One fixed immutable transfer ID binds source, destination, amount1 and pool.
Debit atomically subtracts1 from source free rights and retains that record.
Installation requires the durable debit and atomically adds1 at the destination
with a retained applied marker. A duplicate installation is a stutter. In-flight
counts1 only after debit and before durable application; lack of sender ACK after
application does not count another right. ACK changes transport metadata only.
Timeout cannot reclaim rights. Restart preserves debit, application, reservations,
consumption and request tombstones. Stale presentation/snapshot restoration cannot
roll back the durable ledger. Lost authoritative durable history is outside the
intact-persistent-memory premise and must block future admission in production.

The two durable commits and intervening interruption are explicit. Atomic local
commit/persistence and authenticated cooperating holders are premises; this is a
finite protocol construction, not an OS power-loss durability experiment. One
transfer suffices for an independent minted-rights counterexample on duplicate
credit. It cannot witness the two-opposite-transfer schedule that admits twelve;
central stale-read admission supplies the original12-unit counterexample.

## Finite environment

Two fixed goals, operations, attempts and owners; one request plus one duplicate
probe each, one first send each, and a second send only in the ambiguity mutant.
One receipt per goal with success/refusal alternatives; one conflict extension;
one restart, one quota reset, two local worker incarnations, two lifetime compute
units, two generations and one copied snapshot/reader pin. No identity symmetry
reduction. Rights transfer source is an explicit environment parameter(0 or1).

Named prospective profiles in wr_domain.py specify one-shot environment actions
and prerequisite edges. Every enabled interleaving of each profile is explored;
status is always enabled. A free admission profile imposes no scheduling order
beyond actual transition guards. Other profiles compose contention, receipt loss,
restart, snapshot installation, pin release, quota reset and reconciliation.
Counts summed across profiles include repeated states; they are not the full
original core/cross Cartesian product. A nonempty frontier, timeout or bound hit
means incomplete. All declared enabled edges, including refusals, are checked.
Ordered witness paths and per-action pre/post states establish the claimed orders.

## Acceptance and mutations

Original trace21: both goals observe ten, first reservation accepts six, other
rejects; removing serialized current-balance check admits twelve. Trace03: reserve,
append intent, send, remote accept, lose receipt, restart, duplicate request and
blocked resend preserve same unknown operation and six reserved. Rights trace22:
debit, restart before install, install, duplicate install, stale snapshot, timeout
and lost-ACK restart preserve conservation. Apply the same environments to both
representations. Explicit positive refusal and successful settlement witnesses
ensure conservative holding is not a vacuous always-deny design.

Remove serialization, reservation-on-exit/reset/replay retention, ambiguity,
identity/owner bindings, settlement idempotence, classification/reconciliation
separation, durable debit, duplicate credit, timeout ownership and snapshot rollback
guards. Each must expose an independently stated invariant or transition failure.
Calibrate the checker with wrong initialization, missing edges, changed/no-op
effects and truncated exploration. Exact graph equality alone is insufficient.

The gate preserves unchanged25 regressions and ten frozen historical gates,
including shared-composition at68d50fc. Sources are committed before admitted
executions; all attempts are retained externally with source/host/command hashes.
Two complete gates on an identical clean final candidate and two independent
exact-candidate reviews precede normal review publication. Historical evidence is
revalidated under its unchanged --working gate, not rerun as a past campaign.

## Limits and successors

Keep every original obligation and27 trace rows, eight experiment families, six
cross-area cases and native/upstream-only/combined integration requirements.
SC-WIRE-02 and SC-EPOCH-03 remain successors; this does not import the full prior
broker/epoch product. Full formal freeze, common-writer migration, runtime
integration, recipient relocation/retirement, general ownership reassignment,
physical persistence and unbounded liveness remain unproved. No language/store/
framework selection, installations, providers, spend/reset credits, operational
configuration changes, deployment or merge.

Prospective revision2 after run-01: add free-reservation-core with14 unordered one-shot actions spanning admission, intent, send, acceptance, loss, restart, quota, snapshot and transfer. Run-01 remains retained preliminary evidence; this additional profile is declared before its run. Only actual guards restrict its interleavings. It does not import the original complete core/cross product.

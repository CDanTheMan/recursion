# Batch 04 prospective contract — 2026-09-09

Parent goal-recursion-v2-execution-fabric. Lucas approved the bounded successor
proposal verbatim: "Yes, I approve the bounded successor proposal." The historical
proposal is preserved in approved-proposal.md; its pending language records the
pre-approval checkpoint, superseded only by this approval and goal.json.

Base is freshly verified master 84056423be31617b49841b87ccd2e17bab491a09, merged
PR115. Astra High/Standard remains sole writer/integrator. Work is additive under
the two Batch04 paths in goal.json. No predecessor source, record, identity,
encoding, signature, receipt, schedule, control-plane path or setting may change.

The existing envelope remains 2026-09-09T20:26:30Z through 2026-09-10T02:26:30Z;
discovery ends 2026-09-10T00:26:30Z. This successor does not restart its clock.
At most four read-only workers and ten total active agents; worker packets last
at most 1200 seconds, with no writes or nested delegation. Stop on convergence,
capacity or a binding scope boundary. Independent eligible work continues while
another workstream awaits an owner decision; completed packets do not close the
broader parent goal. No automatic resumption or new metered spend is authorized.

Freeze two local relations. Identity preserves all Q fields. First-attestation-floor
changes only the top-level source_generation serial to max(serial,1) if source_name
is nonempty; otherwise it preserves the serial. Namespace components and every
nested signed envelope, receipt, digest, raw byte string and other Q field remain
exact. This is a candidate relation, not an assertion of equivalent generations.
Source incarnation, restart, stale rejection, attestation, publication and
reconciliation remain observable obligations even when the candidate fails them.

State observation excludes only scheduling done and last-transition decision.
Decision is instead an exact observable transition response for every modeled
action; append operations also expose append_reply. Source-only register, attempt,
atomic, append and collection operations have no Q translation. They are explicit
unmapped operations, with their responses retained; no private action hiding or
response-erasing stutter fallback is selected. This conservative finite-model
contract selects no production interface or runtime response vocabulary.

For shared operations, invoke both unchanged Q reducers and the independent Q
relation at the projected S prestate, retaining original S scheduling bookkeeping.
This establishes only local transition correspondence. It supplies neither a
schedule translation nor original-Q reachability. Classify every source edge under
each relation as matching-step, state-gap, response-gap, state-and-response-gap or
unmapped-operation. Preserve independent state-field and response differences,
source edge and projected target prestate/successor hashes, plus full source
prefixes for first-discovered representative witnesses. No cross-profile shortest
witness claim is made.

Reproduce every original graph hash for 51 profiles and 104 environments: 17966
states and 31140 edges per original representation, zero frontier and exact
terminal counts. Both source reducers and their independent relation must agree.
Check initialization for both relations, finite rank on every edge and full terminal
masks. Reproduce Batch03's unchanged 10292/20794/54 baseline classification.
Retain the known successful first-attestation endpoint, lifted restart obstruction,
signed staging mismatch and omitted-record response mismatch in both encodings;
also retain publication, reconciliation, stale retry and durable duplicate examples.
Passing classification does not require a satisfying global relation.

New negative controls corrupt only certificates, projection fields, responses and
coverage: promoted gap, erased response, misbound source edge, missing generation,
renamed namespace, changed signed envelope, misbound target prestate, omitted
classification and hidden source-only operation. Original protocol inputs and guards
are unchanged. Frozen historical gates still reproduce their original mutants,
traces and truncated calibration; those are reported as historical activity.

After the first complete comparison, use the already retained consecutive
pending-success attestation/stage edges for a restricted contradiction certificate.
With one shared target intermediate state, same actions and exact preservation of
all other fields including staged, first successful Q attestation requires its
generation to be token 1. Normal Q staging copies that generation into the envelope,
while exact preservation of the S envelope requires token 0. Verify source-edge
adjacency/prefixes, both successful responses, guard facts, typed tokens, the shared
target intermediate state and exact source/function anchors. Record the inconsistent
necessary equalities in both original encodings. Controls erase the contradiction,
erase exact staged preservation or misbind the shared source middle state.
This checks retained facts plus an equality contradiction; the source-backed argument
explains necessity. It is not an unrestricted proof about arbitrary Python programs
or relations that change nested observations, action translation or intermediate steps.

The two read-only prospective reviews corrected the inherited accounting estimate:
three Batch03 mapping traversals cost 53898 states; its two frozen source gates
also traverse 35932 states plus four conservatively charged calibration states.
Inherited source-family charge is therefore 89834 per representation. Reserve
17966 before each Batch03/04 invocation and 17968 before each frozen source gate.
Durable reservations never refund failures. The cumulative ceiling is 500000 per
source representation; relation variants reuse one S traversal, and Q kernel calls
are not target graph searches. Other historical graph families preserve their own
original domains/caps and remain separately reported. Finite trace replay is not
silently counted as new graph exploration or omitted from activity descriptions.

Every owned command uses the unchanged Windows OwnedJob helper, suspended launch
before assignment/resume, no breakaway and kill-on-close. Cap commands at 600 seconds
and 2GiB committed process/job memory; cap retained runs at 256MiB. Use shared
heavy-gate/model locks; require >3GiB available physical memory and >1GiB free disk.
Require capacity evidence younger than 15 minutes. Stop discovery at 10%, new
workers at 6%, expensive work at 3% remaining. Keep actual reset use at zero.

Before first execution, require two read-only reviews of the exact preregistered
candidate. Final publication requires two complete 47-command gates on one clean
candidate: the unchanged 18 frozen checks, 25 regressions, append-handoff, Batch02,
Batch03 and Batch04. Require two independent exact-candidate final reviews, fresh
publication admission and verified master. Normal non-force codex push and draft
PR are authorized; Lucas merges. Publisher scripts and upstream/config are unchanged.

Snapshot the complete inherited manifest plus every new source; bind compressed
snapshot hashes, decompressed working bytes and original Git blobs. Preserve all
prior closure receipts and add Batch03's 1336-file completion closure. Retain failures,
superseded candidates and accurate omitted-test descriptions. Q1-Q6 source-admission
questions remain deferred-safeguard, with empty evidence and unchanged dependencies.
No interrupted source-admission experiment is resumed. Source truth, physical
recovery, fairness, whole-path composition, full formal freeze, runtime integration
and language/store/provider selection remain unproved and outside this packet.

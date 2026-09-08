# Shared generation, evidence and replay model — 2026-09-08

Preregistered before execution; parent `goal-recursion-v2-execution-fabric`.
The frozen starting commit, allowed paths and resource bounds are in goal.json,
manifest.json and plan.json. This is a new coupled finite subsystem, not a claim
that multiplying prior separate passes proves their composition.

## Competing constructions

Compare a minimal authoritative aggregate plus independently checked broker state
with an inclusive state record. Implement their transitions separately and check
both against independent invariants, per-action authority/ownership footprints,
enabledness and ordered witnesses. Compare normalized reachable state/edge digests
as additional implementation cross-checks. Do not hide any field whose change
affects authority, settlement, resource ownership or the installed view.

The decisive implementation choices are: independent evidence and replay cuts
versus treating cursor recovery as settlement; exact writer term AND same-term
serial versus term-only publication; an invocation pin AND separate reader pin
versus a single lifetime flag; copied immutable snapshot bytes versus retaining
their source generation until a slow viewer finishes. Construct the guarded
relations and explicit guard-removal counterexamples. Existing M1 contracts,
schemas, validators, oracles and prior experiments remain unchanged.

## Declared environment and bounds

One operation O and payload P; one initially issued epoch1 recipient permit;
two generations G1/G2 and at most two residents; one preserved G1 history capsule;
one invocation pin; one independently owned snapshot reader; one snapshot with at
most three presentation entries; one replay gap; two queued entries and one EVENT
credit; one task Stop; one operational-PAUSE state; one recipient fence install;
one writer boot change and one same-term serial replacement; two worker
incarnations, one provider-quota reset and two lifetime compute units.

Effect evidence has a first started attempt, then either a valid terminal receipt
or a valid refusal receipt. After a success, the next inventory extension may be a
second effect-attempt start or a conflicting verified receipt. The second effect
attempt has no subsequent execution/settlement transition in this bounded profile:
permanent uncertainty is allowed. It is distinct from the second local worker
incarnation, which is an already-scoped deterministic query and may finish without
settling that effect attempt. No second remote execution or fresh permit is issued.

The initial observation is canonically quarantined; no model action clears it.
Literal M1C status and conservative settlement hold are distinct. Refusal at the
recipient does not resolve local uncertainty until its exact retained receipt is
classified. Identity/authentication/completeness of accepted evidence is an
explicit environment premise bound to the frozen literal adapter controls, not a
new production authentication proof. PAUSE forbids a fresh modeled M1A observation
write; pure retained-evidence classification remains separate.

## Coupled presentation and lifetime rules

Publication and accepted evidence extensions append immutable **presentation
facts** `(selected_generation, evidence_cut)` to a finite view journal. This is not
the M1A canonical command/event ledger. It conveys established read-side facts and
never grants authority. Stop/status use an independent control path and do not
wait for presentation credit, queues or snapshot negotiation.

Separate source ingestion, bounded broker queue, deliberate pre-ingress/queued
loss, snapshot capture, immutable byte-copy completion, advertisement, emitted
RESET and installed content/cursor. One loss establishes a floor; EVENT cannot
skip a gap or run while emitted RESET awaits installation. A snapshot binds its
exact source generation, journal cursor and historical evidence cut. New journal
entries remain owned across RESET and are eligible for later delivery. Installation
changes the view only, never the current evidence inventory or authority fields.

Snapshot capture owns a generation-specific reader pin. Copied bytes are not enough
to release that pin: the reader must explicitly finish and be waited. Once copied
bytes are independently retained and the reader is waited, installation may happen
after the original generation is reclaimed. Invocation return/kill/wait and release
are separate. Generation reclamation requires both applicable pins released and
the preserved history capsule. Evidence settlement neither releases pins nor
deletes history. Snapshot installation neither releases an unsettled attempt nor
clears canonical quarantine.

Writer publication stages a candidate and checks its complete modeled ticket
`(term, serial, parent generation, target generation)`. A same-term replacement
invalidates the old ticket even when parent/target/content remain unchanged. A
boot change invalidates the term independently. Generation selection changes at
publication commit and survives lost acknowledgment/restart. This tuple is a
restricted abstraction of the prior full issuer/owner/nonce/directory/manifest
ticket, not a substitute for those runtime bindings.

## Required checks

Before the first execution, the concrete domain narrows the environment to the
initial13 named schedule profiles in `sc_domain.py`. Every profile starts at the same
initial state. Its named external actions are one-shot, with explicit prerequisite
edges; all their enabled interleavings are explored. Status, applicable Stop,
PAUSE and recipient installation remain independently enabled in every profile.
The 500000-state bound applies to the sum of profiles for each representation.
These are coupled finite interaction slices, not closure of an unrestricted
Cartesian product of all capabilities. The restricted schedules, including two
writer denial/retry sequences, are applicability limits; arbitrary extra retries,
multiple snapshots, multiple readers and general scheduling remain unproven.
No schedule is chosen from a successful run after the fact.

Prospective revision2, after retained run01 and independent static challenge:
add a fourteenth `free-shared-core` profile with16 externally unordered one-shot
actions across generation, evidence, replay and lifetime. Only actual transition
guards constrain their interleavings. Strengthen the serial-denial profile to
stage before submitting the old ticket, so missing staging cannot explain denial.
Require complete independent postconditions and edge-based Stop/exposure witnesses.
Run01 remains superseded evidence; its state-only witnesses did not establish those
orders. This revision is committed before its own run and does not promote the
original broad comparison to complete coverage.

Prospective revision3, after retained run02 and a second contract challenge:
require explicit gap detection before recovery emission, clear receiver EVENT
credit on emission, allow one fresh grant after emission (possibly before content
installation), and prove retained future delivery after installation and that grant.
Add a fifteenth recovery-trigger negative profile. The queue here owns broker-side
undelivered source entries; it is NOT M1B's receiver pending/unacknowledged queue.
Advertisement/copy/install are internal implementation phases. Gap detection is an
abstract environment assertion of a missing suffix, not a tested HELLO/WELCOME
exchange. The inherited M1B wire oracle remains unchanged; full wire identity,
byte-credit, ACK, framing and restart handshake correspondence remain unproved.
Thus these internal phase graphs must not be reported as observed M1B integration.
Require single edge-milestone paths for pinned publication → refused reclaim →
copy/wait → reclaim → install and prequeued future entry → install → fresh grant →
delivery. Run02 remains superseded, with its source and outcomes retained.

The modeled reply is an acknowledgment received after committed publication;
publish → writer restart → acknowledgment is tested, but a lost-reply transport is
not represented. Full goal/lease/issuer epoch namespaces and the outstanding
external-effect reservation remain inherited assumptions/residuals. Settlement
hold and lifetime compute are not a substitute for that reservation variable.

Exhaustively enumerate every reachable state and transition of the declared
profile in both representations; a nonempty frontier or resource limit is
incomplete. Require per-edge independent authority/evidence/pin write footprints,
invariants, initial correspondence, state/edge equality and always-enabled status
and applicable Stop. Hidden broker stages also need independent edge checks.
Check explicit finite progress paths, not a fairness/eventual-delivery theorem.

Ordered witnesses must combine: settled cut1 → capture snapshot1 → start attempt2
→ RESET/install old cut1 with hold preserved; snapshot reader on G1 → G2 publish →
invocation release → blocked reclamation → copied/waited reader → reclaim → install;
writer serial ABA and writer restart; saturated queue with Stop; local Stop before
recipient installation versus installed-fence refusal; unknown effect across local
kill/wait and replay; conflict with no pending IDs yet a settlement hold; emitted
RESET interrupted before application install; later output survives RESET; and
old ACK versus new incarnation completion/lifetime accounting.

Remove guards independently for replay clearing newer evidence, status-only or
pending-only settlement, premature reader/invocation release, stale term/serial,
un-staged publication, generation reclamation, gap/RESET ordering, future-output
ownership, control backpressure, recipient fencing, local-death settlement,
canonical quarantine clearing, ACK/incarnation conflation and reset accounting.
Each must yield a reachable counterexample to an independent obligation, not
merely a different output. Checker calibrations must reject wrong initial state,
missing edge, changed edge and truncated frontier.

Freeze seven literal mapping controls from the predecessor: success, late-receipt,
later-start-only, later-unresolved, prior-unresolved, conflict and stale-paused.
Compare exact hand-stated literal status, pending IDs, hold and permission=false.
Retain actual literal PAUSE/quarantine controls separately. These mappings do not
turn the abstract graph into literal runtime execution.

## Coverage and limits

Preserve all six obligations and27 rows. No two-goal serialized pool, complete
original core/cross profiles, process-at-birth containment, remote relocation,
receiver-record retirement, consultation/adoption, full configuration closure or
fairness theorem is supplied here. The prior complete ingress/framing model is
preserved evidence but its entire state space is not imported into this reduced
composition. Full formal freeze and the common-writer migration blocker remain
open unless their original complete gates are independently established.

No language, store, framework or product crypto selection; no live provider,
installation, deployment, auth/model/PAUSE configuration change or reset credit.
Sources are committed before every admitted run. Preserve all failed/superseded
runs externally. Two full exact-candidate gates include unchanged25 regressions
and nine frozen historical gates; two independent exact reviews precede normal
publication. PR101 remains the base while open; only the Owner merges.

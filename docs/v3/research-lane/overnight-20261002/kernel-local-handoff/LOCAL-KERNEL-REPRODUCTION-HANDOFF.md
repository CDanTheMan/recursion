# Local kernel reproduction handoff

Source pin: **73d70505b8c266fbb08d820d304ebd2e68ac7f1b**  
Prepared: **2026-10-02**  
Status: **static synthesis of 13 independently source-reviewed findings; all proposed reproduction cases UNEXECUTED**

## Decision and order

First establish the independent packet oracle (SG03), then the short arithmetic, exception and lease cases. Continue through authority joins and the stale-packet/terminal sequences. Keep the reduced RIntegrated adequacy questions and full candidate LiveDrain premise decision separate from pure M1A admission candidates. Packet-dependent rows are presently diagnostic-only under the historical source/fixture regime; the pre-packet SK01 and SG07 cases avoid this particular blocker. Priority is qualitative leverage and dependency, not measured cost or severity. A dependency means a valid control or semantic decision, never that a candidate fix must land before another baseline case can run.

This handoff documents leftover local tasks; it does **not** authorize execution. Preparation here was static document synthesis only. No target code, runner, checker or target import was executed. The frozen delivered main archive remains untouched. These findings are candidates, not runtime failures, accepted fixes or a deterministic-core freeze verdict.

| Rank | Case | Layer | Reason to do it here |
|---|---|---|---|
| 1 | SG03 Preserve task effects in derived packet | pure M1A | independent packet oracle; whole-wire control setup pending |
| 2 | SK01 Enforce reservation component conservation | pure M1A | Short independent discriminator |
| 3 | SG05 Resolve exact admitted downgrade exception | pure M1A | Short independent discriminator; whole-wire control setup pending |
| 4 | SG01 Require replacement lease epoch increment | pure M1A | Short independent discriminator; whole-wire control setup pending |
| 5 | SG07 Resolve attestation authority policy reference | pure M1A | Short independent discriminator |
| 6 | SG06 Resolve separate ARM amendment approval | pure M1A | Short independent discriminator; whole-wire control setup pending |
| 7 | SG04 Enforce assigned gate verifier identity | pure M1A | Short independent discriminator; whole-wire control setup pending |
| 8 | SG02 Reject stale packet under fresh lease | pure M1A | valid SG01 control shape, not its fix; whole-wire control setup pending |
| 9 | SK02 Decide zero Pause epoch semantics | pure M1A | explicit zero/nonmonotone epoch contract decision; whole-wire control setup pending |
| 10 | SG08 Block terminal success while effects remain ambiguous | pure M1A | valid assigned-gate and full-plan controls; independent SG03 packet oracle; whole-wire control setup pending |
| 11 | SK03 Expose missing second attempt completion | reduced RIntegrated adequacy | Short independent discriminator |
| 12 | SK04 Classify reduced M31 exposure structurally | reduced RIntegrated adequacy | SK03 attempt ceiling understood; no repair dependency |
| 13 | SK05 Specify LiveDrain recovery progress premise | full candidate LiveDrain semantics | explicit premise interpretation before any liveness claim |

## Known prefix and control qualification

W:583–587 requires packet correlation_id = GoalSpec ID. In the inspected F-M1A-001/005/006/011/014/016 packets, stored correlation_id is CORR-M1A while GoalSpec ID is GOAL-M1A; R:288 hardcodes CORR-M1A. This is a source-observed metadata discrepancy, not a runtime result or another counted case. It affects SG03’s derived packet/control and packet-bearing prefixes for SG01/02/04/05/06/08 and SK02. The first F-M1A-005 packet also carries SG03’s broad-effects mismatch; its second packet agrees on effects. SK01’s first-five-command reservation prefix and SG07’s first-three-command policy prefix are pre-packet and unaffected by this particular discrepancy. Effect-set agreement elsewhere is one-axis consistency, not whole-prefix certification.

Independently validate every reused active-state prefix and each positive control against the chosen whole wire contract. Admission/replay acceptance of a structurally valid but wire-inconsistent prefix is producer-diagnostic only, not an otherwise-valid isolated semantic counterexample. Any regenerated fixture needs a distinct source/seed regime, exact hashes, transitive resealing and independent verification of every prefix step. Preserve all historical bytes and guards; if target code changes, separate baseline and revision evidence and show that the tested missing-guard relation was not repaired or masked.

A fresh GoalSpec ID literally CORR-M1A is statically eligible under W:29 and V:217,415–419,1174; no GOAL-prefix restriction was found in the inspected V/A/R. A separately authored single-goal seed could avoid this correlation mismatch without changing target code, but no complete seed/control has been constructed or whole-prefix validated. It is not ready evidence or a general metadata fix. Rebuild every reference, packet seed, digest and synthetic attestation; retain the original-ID correlation discriminator so the narrow seed does not hide it. A separately reviewed valid projection or corrected candidate is also only a proposed distinct regime, not a substitute for independent validation.

## Before a future authorized run

1. Verify the exact pin and relevant source hashes. Read the precise public boundary and separately approve a provider-free local execution profile. The visible fixture runner invokes `R.admit` directly (T/conformance.test.py:24–56; R:517–599); this is an entrypoint identification, not a verified runner command. This document deliberately supplies no runner command.
2. Preregister each case’s independent expected semantics, raw observables, control, earliest unrelated guard, stop rule and exact source/config identity. Implement expected values from W/O/P or the explicitly chosen formal contract, not by asking the target implementation what it would emit.
3. Build each negative and control from the same pinned baseline in isolated state. Fix transitive digests and bindings necessary to isolate one semantic relation; do not remove unrelated safety checks. Every failed control blocks interpretation of its paired negative.
4. Capture raw outputs and input immutability; identify atomic refusal versus accepted state transition. A passing fixture runner, matching frozen digest, or replay success alone is insufficient semantic evidence.
5. If a real mandatory guard defeats the construction, narrow or withdraw that candidate. If a patch is proposed, record a new revision and review it independently. Keep baseline receipts immutable; rerun each relevant case separately on the new revision. One fix must not mask another case, silently update a historic receipt or migrate an old mutation name to a different site.

No measured runtime, cost or exhaustive bound is asserted. Any finite exploration bound is proposed and must retain capacity for the discriminating probe; exhaustion is not a pass. Establish the short witnesses and model scope before enlarging bounds.

## Shared case contracts

### Pure M1A

Every M1A case inherits: fresh command identity; fresh record identity unless the cited upcoming ID is unused; exact current projection version/digest; valid closed/sorted shapes; independent canonical record, payload, candidate and command digests and matching synthetic authority attestation. Keep exact goal/plan/task/packet refs and current actor/role/allowed-command/lease/time/policy bindings except the isolated relation. Advance logical time only as needed within half-open lease and authority windows. Resolve dependencies and reseal transitively; never change already admitted immutable bytes. Identify the precise earliest failing guard. No real credential or authority is involved.

Refusals require no emitted event, unchanged projection and no partial record/state transition, assessed from raw artifacts. Do not assume a specific error code where the profile has not pinned one. Require the intended semantic guard or an independently justified earlier mandatory guard, not merely any refusal.

**Expected evidence for every M1A case:** source commit and per-file hashes; exact prefix and independently authored mutated/control inputs plus resealing/reference ledger; preregistered semantic oracle and error-code decision where needed; raw receipts/events/full before-and-after projections and unchanged caller inputs; first-failing-guard trace and atomicity comparison; case verdict with reviewer and limitations. These are future evidence obligations, not files claiming completed runs.

### Formal cases

Keep exact baseline text/config/one-site mutation and explicit bounds in separate artifacts. Independently derive action preconditions, transition effects, invariants and temporal obligations from the cited contract. Expected semantics cannot be generated by the target as its own oracle. Capacity truncation, deadlock-check suppression and omitted fairness must be visible. No checker or target import occurred in this drafting task.

**Expected evidence for every formal case:** source/config hashes and exact site identity; independent transcription and property/premise/observation definitions; bounds and guard/capacity ledger; raw trace or proof/checker report if later authorized; positive control and falsifier classification; revision-specific receipt with limitations. Any full-candidate transcription is a newly reviewed artifact, not the pinned reduced model or a previously executed result.

## SG03 frozen positive oracle warning

The source-reviewed literal witness is in T/fixtures/F-M1A-005.json, case `amend`: `initial_events[3].related_records` includes TASK-M1A-A with `effect_keys=[]` and digest `0b5bed6c6f30f395b7b3a387b3dafbd1960b5ce57adc369b903f19db83301ba2`. `initial_events[6].primary_record` is PACKET-b4eb25dd79a41ba8692a4b4354af95f6, binding that exact task digest, but with effects `[EFFECT-SYNTHETIC]` and digest `cc53dcc8b141453c293a08b509c1418d8dc85e78f11fb434d69d072fcf82f5b0`.

These are observed **stored fixture bytes**, not a runtime trace. Reproducing the frozen positive oracle can therefore preserve the wrong broad packet. W:569–576’s task-copy rule and P:57–63,262–272’s attenuation rule must independently determine the expected empty set. Preserve the old bytes as historical evidence; author a separately identified expectation and record all metadata discrepancies. Never use R’s packet-generation function as its own semantic oracle.

## Case specifications

### 1 SG03 Preserve task effects in derived packet

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient. Equal task/goal effect sets do not make the original-ID positive packet whole-wire valid; do not normalize expected correlation metadata to R output.
- **Exact fixture or prefix:** T/fixtures/F-M1A-001.json, happy: commands 1–6 through reserve-budget, with the single task narrowed at plan construction; probe command 7 derive-work-packet. Literal cross-check: T/fixtures/F-M1A-005.json, amend, initial_events[3].related_records and initial_events[6].primary_record.
- **Contract and source guard:** W:569–576;P:57–63,262–272;A:256–278;R:324–340,428–429 (R:327 copies goal effects).
- **One isolated change:** Only semantic change: task effect_keys [EFFECT-SYNTHETIC] → []; goal allowed_effect_keys stays unchanged. Rebinding consequences are not additional mutations.
- **Keep unrelated guards valid:** M1A common discipline; recompute task, plan graph/transition, downstream reservation/lease/route refs and command bindings. Keep the one-node DAG, actor, active leases, policies and logical times valid. Construct expected packet independently from W, not R’s derivation.
- **Independent oracle:** A valid derived packet must copy the empty task effect set; independently construct its whole expected record/digest. An inconsistent derivation request may refuse, but must not be treated as successful broad derivation. Separately document a semantic-digest refusal if the independently correct packet is rejected.
- **Positive control:** Same construction and bindings with task effects equal to goal effects; derive the independently specified matching packet. If separately probing broad expected digest, label that a diagnostic, not the semantic positive control. Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient. Equal task/goal effect sets do not make the original-ID positive packet whole-wire valid; do not normalize expected correlation metadata to R output.
- **Decisive falsifier and rival:** An emitted packet with EFFECT-SYNTHETIC against the empty task disproves attenuation at this boundary. A semantic expected-digest refusal plus a broad packet accepted under a broad expected digest distinguishes the derivation mismatch. A demonstrated mandatory independent guard or correctly empty packet refutes/narrows the predicted acceptance.
- **What this does not prove:** Stored fixture bytes are not execution. Existing broad expected-packet equality is not a valid attenuation oracle; no effect dispatch or beyond-goal authority follows.
- **Allowed future scope:** Provider-free independent fixture construction and pure admission/derivation only, after authorization.
- **Stop or inconclusive:** Stop for any unrelated stale/digest/policy/auth failure or unexplained frozen metadata discrepancy; preserve it rather than editing history. Do not derive the expected packet by calling the implementation under test. Strict conformance interpretation is blocked by the historical packet prefix/control discrepancy; an unchanged historical pair may be retained only as a labeled producer diagnostic.
- **Additional evidence:** Common M1A artifacts plus independently assembled packet, field-by-field derivation ledger, expected and returned packet digests, literal SG03 witness extract.

### 2 SK01 Enforce reservation component conservation

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Pre-packet prefix: unaffected by the specific known packet correlation/effect discrepancies; still requires independent whole-prefix validation and a valid paired control before conformance interpretation.
- **Exact fixture or prefix:** T/fixtures/F-M1A-001.json, happy, first five commands; mutate sixth reserve-budget only.
- **Contract and source guard:** W:335–338;O:155;V:548–552,1008–1009,1041–1072,1156–1186,1351–1410;A:340–528;R:176–181,389,413–416,517–599.
- **One isolated change:** Reservation tokens triple becomes limits=1, consumed=1, remaining=1; every other component remains valid.
- **Keep unrelated guards valid:** M1A common discipline; upcoming BUDGET-RESERVATION-1 is fresh in the five-command prefix and may stay. Preserve goal/plan/task refs and current unexpired ARM lease; no packet exists in this suffix. Both malformed and control limits must remain within parent limits.
- **Independent oracle:** Independently calculate consumed+remaining=limits per component with no overflow. Malformed reservation must refuse atomically: no event, unchanged projection and reservation totals.
- **Positive control:** Identical command construction with consumed.tokens=0, remaining.tokens=1, limits.tokens=1. A separate parent-limit probe is optional and must not be folded into this mutation.
- **Decisive falsifier and rival:** Admission of 1+1!=1 falsifies the equation. A demonstrated mandatory equation check at the same public boundary that refuses while the control admits refutes the inferred acceptance.
- **What this does not prove:** No aggregate sibling conservation, debit correctness, external spend or live-meter conclusion.
- **Allowed future scope:** One-command provider-free pure admission pair after authorization.
- **Stop or inconclusive:** Unrelated refusal or invalid control is inconclusive; do not remove digest/auth/parent guards to obtain arithmetic exposure.
- **Additional evidence:** Common M1A artifacts plus independent component equation and before/after reservation totals.

### 3 SG05 Resolve exact admitted downgrade exception

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Exact fixture or prefix:** T/fixtures/F-M1A-011.json, downgrade: initial nine-command prefix plus admitted record-owner-verifier-exception; probe following downgraded-pass decision.
- **Contract and source guard:** W:250–255,490–496;O:97–104;V:1046–1058;A:322–337,507–510;R:236–264.
- **One isolated change:** Change only owner_exception_ref.id to OWNER-VERIFIER-EXCEPTION-ABSENT, retaining original ref version/digest.
- **Keep unrelated guards valid:** M1A common discipline; keep original exception in state, exact passing gate, assigned plan verifier, both downgrade policy permissions, current state/event-log bindings, valid time and otherwise unexpired real referenced control exception. Reseal decision/command/verifier candidate attestation.
- **Independent oracle:** Resolve the exact reference independently against admitted records; an absent referenced exception cannot justify downgraded terminal state. Require atomic refusal, no terminal transition.
- **Positive control:** Identical decision with original exact admitted unexpired exception ref. Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Decisive falsifier and rival:** Terminal-verified-downgraded with the absent ref is decisive. Exact-resolution refusal with valid control refutes this minimal case.
- **What this does not prove:** Does not establish full assurance or actual Owner risk approval. Expired/wrong-candidate cases are separate follow-ons, not tested by absence.
- **Allowed future scope:** Provider-free single-suffix admission pair after authorization.
- **Stop or inconclusive:** Stop if gate, policy permission, verifier assignment, state/event-log or candidate binding fails before reference resolution. Strict conformance interpretation is blocked by the historical packet prefix/control discrepancy; an unchanged historical pair may be retained only as a labeled producer diagnostic.
- **Additional evidence:** Common M1A artifacts plus admitted-record membership ledger and exact exception-ref comparison.

### 4 SG01 Require replacement lease epoch increment

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Exact fixture or prefix:** T/fixtures/F-M1A-006.json, stale-lease, seven-command initial prefix immediately before first replacement command.
- **Contract and source guard:** W:332–334,592–595;V:1034–1036;A:384–397,399–528;R:185–190,442–445.
- **One isolated change:** Fresh LEASE-WORK-2 payload epoch 2 → 1; old_lease_ref and supersedes_lease_ref stay exact current epoch-1 lease.
- **Keep unrelated guards valid:** M1A common discipline; Head-authored replacement keeps null envelope lease as supplied, valid ordered issue/expiry interval, same goal/plan/task/worker and permitted command; fresh record ID and matching resealed Head attestation.
- **Independent oracle:** Independently compare new epoch with old+1 and exact supersession ref. Equal epoch must refuse without changing either lease. Pin the refusal code before running if unspecified.
- **Positive control:** Otherwise-identical 1→2 replacement. No worker probe is needed. Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Decisive falsifier and rival:** Accepted 1→1 replacement disproves the increment obligation. A mandatory +1 check at this same boundary and accepted control refutes predicted admission.
- **What this does not prove:** No two-live-writer, process-fence, takeover or dispatch claim.
- **Allowed future scope:** Provider-free one-command replacement pair after authorization.
- **Stop or inconclusive:** Stop if freshness, exact old ref, interval, Head binding or control admission is invalid. Strict conformance interpretation is blocked by the historical packet prefix/control discrepancy; an unchanged historical pair may be retained only as a labeled producer diagnostic.
- **Additional evidence:** Common M1A artifacts plus old/new lease states, epochs and exact supersession refs.

### 5 SG07 Resolve attestation authority policy reference

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Pre-packet prefix: unaffected by the specific known packet correlation/effect discrepancies; still requires independent whole-prefix validation and a valid paired control before conformance interpretation.
- **Exact fixture or prefix:** T/fixtures/F-M1A-001.json, happy, first three commands; probe fourth propose-plan-revision.
- **Contract and source guard:** W:246–254,264–273;O:76–82;V:1423–1445;A:348–352,365–376,280–307.
- **One isolated change:** In only the matching synthetic attestation, change authority_policy_ref to a well-shaped absent policy ID/version/digest and reseal attestation.
- **Keep unrelated guards valid:** Keep command candidate byte-identical, actor/role, allowed command, times and command auth identity valid. Goal/plan/task policy records and refs remain valid and unchanged. Confirm the unknown tuple is absent from the exact policy bundle.
- **Independent oracle:** Independent exact policy-table lookup must fail; expect E-POLICY-UNKNOWN, no events and unchanged projection.
- **Positive control:** Same command and attestation except valid original authority_policy_ref and its resulting attestation digest.
- **Decisive falsifier and rival:** Acceptance despite absent authority policy falsifies resolution. Genuine lookup refusal with accepted control refutes the minimal prediction.
- **What this does not prove:** No credential authenticity or task-policy equality failure; constitution mismatch is a separate mutation.
- **Allowed future scope:** Provider-free synthetic authority-table pair after authorization.
- **Stop or inconclusive:** Stop for attestation shape/self-digest/candidate/time failure. Do not alter task policies to force the same error.
- **Additional evidence:** Common M1A artifacts plus policy-table membership proof and unchanged command-candidate digest.

### 6 SG06 Resolve separate ARM amendment approval

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient. F-M1A-005 additionally includes SG03’s inconsistent first packet effects. Independently revalidate all 15 prefix steps, co-authority and dispositions in any regenerated setup.
- **Exact fixture or prefix:** T/fixtures/F-M1A-005.json, amend, all 15 initial commands; probe its single amendment.
- **Contract and source guard:** W:490–495;V:1292–1293;A:361–376,409–432,511–521;R:446–455.
- **One isolated change:** Only payload.arm_proposal_attestation_id becomes a valid-format absent authority-table ID.
- **Keep unrelated guards valid:** M1A common discipline; reseal full command candidate and matching Owner attestation. Keep replacement records, complete dispositions, policies and original ARM entries unchanged; retain current ARM proposal context and times for control. The separate ARM candidate is D({replacement_plan_revision,plan_transition,task_nodes}), distinct from the Owner’s full-command candidate (W:490–495). Independent literal JSON hashing of the original control matches ARM candidate b485f11703ad8d85f871e9ecbdf620c36de291a426e6b78ec25554f1299d3b05; the original ARM attestation is present. Any regenerated setup must independently reseal/reverify both distinct bindings.
- **Independent oracle:** Independently resolve the separately required candidate-bound current ARM attestation. Missing co-authority requires atomic refusal of entire composite; no partial amendment/replacement/dispositions.
- **Positive control:** Identical complete composite with original valid ARM attestation ID. Independently verify its candidate binding rather than assuming the frozen positive proves it. Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient. F-M1A-005 additionally includes SG03’s inconsistent first packet effects. Independently revalidate all 15 prefix steps, co-authority and dispositions in any regenerated setup.
- **Decisive falsifier and rival:** Accepted amendment with absent ARM reference falsifies the co-authority requirement. A valid mandatory resolution rejection with positive control refutes prediction.
- **What this does not prove:** No principal escalation in a deployed service or complete compatibility/disposition correctness claim.
- **Allowed future scope:** Provider-free atomic-composite pair after authorization.
- **Stop or inconclusive:** If the purported positive’s separate ARM candidate binding cannot be established, stop and report unresolved control. Do not weaken co-authority or incomplete-disposition checks. Strict conformance interpretation is blocked by the historical packet prefix/control discrepancy; an unchanged historical pair may be retained only as a labeled producer diagnostic.
- **Additional evidence:** Common M1A artifacts plus Owner/ARM candidate-binding ledger and composite atomicity diff.

### 7 SG04 Enforce assigned gate verifier identity

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Exact fixture or prefix:** T/fixtures/F-M1A-001.json, happy, first eight commands through submit-worker-result; probe ninth gate result.
- **Contract and source guard:** W:238–239;O:84–88,124;P:268–272;V:593–609;A:361–376,334–336;R:215–218,389–390,413–416.
- **One isolated change:** Use a different synthetically attested verifier actor; consistently change command actor, creator and independence verifier identity, but never GateRequirement.assigned_verifier_actor_id.
- **Keep unrelated guards valid:** M1A common discipline; both actors have equally valid verifier-role/candidate/time authorization. Keep gate requirement, packet/task/evidence refs, policies and expected gate disposition identical. No assignment-change event occurs.
- **Independent oracle:** Independent exact assigned-actor comparison must reject the alternate actor without task advancement; self-reported independence is not assignment. Pin unspecified refusal code beforehand.
- **Positive control:** Same gate pass by the assigned verifier with consistent creator/independence identity and equally valid attestation. Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Decisive falsifier and rival:** Alternate actor advances gate/task state: decisive assignment violation. Assignment-specific refusal plus accepted assigned control refutes predicted admission.
- **What this does not prove:** No unauthenticated caller or production authentication claim; does not test every required gate.
- **Allowed future scope:** Provider-free two-actor synthetic admission pair after authorization.
- **Stop or inconclusive:** Stop if alternate role/candidate attestation is invalid or another evidence/ref guard blocks; do not disable role checks. Strict conformance interpretation is blocked by the historical packet prefix/control discrepancy; an unchanged historical pair may be retained only as a labeled producer diagnostic.
- **Additional evidence:** Common M1A artifacts plus assigned-versus-actual identity ledger.

### 8 SG02 Reject stale packet under fresh lease

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Exact fixture or prefix:** T/fixtures/F-M1A-006.json, stale-lease, seven-command initial prefix plus valid 1→2 replacement; probe following worker result.
- **Contract and source guard:** W:570–579;P:274–277;O:F-M1A-006;A:380–397;R:209–214,389–390,413–416.
- **One isolated change:** Keep old work_packet_ref but switch result envelope to new active lease; update result creation-lease metadata consistently. This isolates packet-versus-current-lease relation.
- **Keep unrelated guards valid:** M1A common discipline; same authorized worker, goal/plan/task and permitted submit-worker-result. New lease issue=7, expiry=900 exclusive; choose probe within interval and attestation window. Reseal affected records and attestation. Do not use malformed SG01 lease.
- **Independent oracle:** Independently compare packet’s captured lease with current active lease. Require stale refusal and no current task/packet progress; inert historical observation is only acceptable after an explicit reviewed contract decision.
- **Positive control:** Otherwise-equivalent result for a newly reissued packet captured under the new active lease, with all resulting exact refs resealed. Also retain the frozen old-envelope refusal as a masking-guard check. Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Decisive falsifier and rival:** Fresh-envelope acceptance advancing old packet/task disproves stale-packet obligation. Independent freshness refusal with new-packet control accepted refutes prediction.
- **What this does not prove:** No unauthorized actor, physical work, source-freshness or deployed acceptance proof.
- **Allowed future scope:** Provider-free replacement and result-binding pairs after authorization.
- **Stop or inconclusive:** If a valid newly reissued packet/control cannot be authored under pinned semantics, report control construction blocked. Unrelated stale state/lease/time refusal is inconclusive. Strict conformance interpretation is blocked by the historical packet prefix/control discrepancy; an unchanged historical pair may be retained only as a labeled producer diagnostic.
- **Additional evidence:** Common M1A artifacts plus captured/envelope/current lease comparison and packet/task state transitions.

### 9 SK02 Decide zero Pause epoch semantics

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Exact fixture or prefix:** T/fixtures/F-M1A-014.json, pause, seven-command active prefix at epoch 0; first apply-pause then fresh submit-worker-result probe. Separate rollback variant: accept epoch-1 Pause, then fresh zero Pause, then probe.
- **Contract and source guard:** W:323;O:198;V:434–439,1034–1036;A:14–18,399–407;R:228–229.
- **One isolated change:** Primary pair changes new_pause_epoch 1 → 0 only. Keep mode current-immediate. Rollback is separately identified fresh 1→0 control action, never a duplicate receipt.
- **Keep unrelated guards valid:** M1A common discipline; Owner-attested Pause; original packet captured epoch 0; WORKER-LUNA active work lease epoch 1, issue 7, expiry 900 exclusive. Primary worker probe can use logical time 9 with newly current state/version and resealed authority. Rollback requires a later in-window time and distinct directive ID.
- **Independent oracle:** Precommit one contract: reject zero/nonmonotone inputs atomically, or explicitly approved strictly advancing normalization. Every accepted operative Pause must make otherwise-valid progress refuse E-PAUSED; zero may not silently mean Resume.
- **Positive control:** Identical epoch-1 Pause followed by the same valid fresh worker probe must enforce E-PAUSED; unpaused equivalent probe establishes the probe is otherwise admissible. Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Decisive falsifier and rival:** Accepted current-immediate zero Pause followed by progress is decisive against operative-Pause semantics. Rejection/approved advancing normalization and paused refusal narrows or refutes the candidate.
- **What this does not prove:** No actual process continuation, receiver fencing or D-022 Full/Aggressive/Lazy Stop implementation conclusion.
- **Allowed future scope:** Provider-free Pause/progress pairs after explicit profile decision and authorization; preserve historical epoch-1 oracle.
- **Stop or inconclusive:** Undecided zero contract, stale probe, duplicate identity or lease/attestation expiry makes outcome inconclusive. Do not call a stale-input refusal successful Pause enforcement. Strict conformance interpretation is blocked by the historical packet prefix/control discrepancy; an unchanged historical pair may be retained only as a labeled producer diagnostic.
- **Additional evidence:** Common M1A artifacts plus selected epoch contract, directive IDs, epoch trajectory and paired progress receipts.

### 10 SG08 Block terminal success while effects remain ambiguous

**Layer:** pure M1A. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Exact fixture or prefix:** T/fixtures/F-M1A-001.json, happy, first eight commands; add fresh ambiguous observation using T/fixtures/F-M1A-016.json shape, then assigned gate pass and full plan decision.
- **Contract and source guard:** O:135–137,200;W:443–444;A:322–337,472–473;R:215–218,230–264.
- **One isolated change:** Single semantic change to happy completion path: insert one valid ambiguous-effect observation on the packet; no reconciliation/disposition. Rebind subsequent completion commands to changed states.
- **Keep unrelated guards valid:** M1A common discipline; fresh observation/command IDs, increasing in-window times; valid assigned gate actor and assigned full plan verifier; exact current event-log and gate digests; unchanged valid policies/leases and full-assurance inputs.
- **Independent oracle:** Independently test terminal-verified ⇒ no unresolved ambiguous effect for this completion. Gate pass alone can remain meaningful; plan must remain nonterminal while ambiguity persists.
- **Positive control:** Otherwise-identical successful completion with no ambiguous observation, recomputing only resulting state/event-log bindings. Preserve honest gate output independently of terminal allowance. Historical source/fixture regime is producer-diagnostic only because of the known packet correlation mismatch (W:583–587;R:288). A whole-wire conformance claim is blocked until a separately identified, independently whole-prefix-valid setup/control is constructed and reviewed; unchanged-source acceptance is not sufficient.
- **Decisive falsifier and rival:** Terminal-verified plus same nonempty ambiguous_effect_refs and no reconciliation is decisive. Nonterminal outcome under ambiguity with successful no-ambiguity control refutes predicted terminal transition.
- **What this does not prove:** No external effect success, duplicate dispatch, rollback or runtime safety conclusion.
- **Allowed future scope:** Provider-free observation/gate/plan sequence pair after authorization.
- **Stop or inconclusive:** Stop for wrong verifier, broken event-log/gate digest or invalid control. A blocked gate alone is not evidence that every terminal path checks ambiguity. Strict conformance interpretation is blocked by the historical packet prefix/control discrepancy; an unchanged historical pair may be retained only as a labeled producer diagnostic.
- **Additional evidence:** Common M1A artifacts plus ambiguity-set snapshots after each step and terminal/task/packet state diff.

### 11 SK03 Expose missing second attempt completion

**Layer:** reduced RIntegrated adequacy. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Formal-model case; M1A packet-prefix discrepancies do not apply. Retain exact model/config/premise scope.
- **Exact fixture or prefix:** K Init → GrantLease(w1) → Start → SubmitFail → ArmTimer → FireTimer → Retry. Six fresh IDs/events reach Running attempt 2; propose at least seven IDs/events so the completion probe has capacity.
- **Contract and source guard:** K:70–76,118–143,153–178;KC CHECK_DEADLOCK FALSE;F:162–166 is a different fuller contract.
- **One isolated change:** No implementation mutation. Isolate attempt value via reachable retry prefix and probe Submit and SubmitFail separately at attempt 2; compare reachable attempt-1 controls.
- **Keep unrelated guards valid:** Model-only common discipline; owner=w1, lease starts 1<3 and becomes 2, unpaused/uncancelled; retain fresh ID/event for probe. No synthetic authority/policy digest, wall-clock lease, credential or provider exists in this reduced model. Do not claim those dimensions were validated.
- **Independent oracle:** Independent action-enablement ledger: after legitimate retry, useful retry-completion scope needs a result path. Exact K guards require attempt=1 for both result actions. Require a scope decision, not an invented invariant failure.
- **Positive control:** Otherwise-equivalent Running state reached by GrantLease→Start at attempt 1, with fresh capacity; each result action should be enabled. A later fuller revision must separately show attempt-2 success and failure.
- **Decisive falsifier and rival:** Enabled valid attempt-2 Submit or SubmitFail in the unchanged pinned reduced model refutes the missing-path claim. Disabled probes with capacity support inadequacy only if useful completion was claimed.
- **What this does not prove:** Not global deadlock (Cancel/control may remain possible), invariant violation, unfairness, production liveness failure or defect in full candidate.
- **Allowed future scope:** Provider-free independent model transcription/enablement check after authorization and scope declaration.
- **Stop or inconclusive:** Stop if capacity is exhausted, prefix not reachable, or model intentionally claims only bounded increment; label diagnostic scope rather than force a fix. Do not weaken guards for mutation score.
- **Additional evidence:** Common formal artifacts plus six-action trace, action-enabledness matrix and remaining-capacity ledger.

### 12 SK04 Classify reduced M31 exposure structurally

**Layer:** reduced RIntegrated adequacy. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Formal-model case; M1A packet-prefix discrepancies do not apply. Retain exact model/config/premise scope.
- **Exact fixture or prefix:** K: GrantLease→Start→PrepareEffect→MarkDispatch→ReconcileEffect(KnownNoEffect)→SubmitFail→ArmTimer→FireTimer→Retry→PrepareEffect→MarkDispatch. At least 11 fresh IDs/events reach full outbox. Extra capacity is needed for later probes, not a cure for structural exposure.
- **Contract and source guard:** MG:43–45;K:17,169–178,189–222;F:185,289 names a different Enqueue mutation.
- **One isolated change:** Exact diagnostic mutant only: OutboxOK Len(outbox)<Cap → <=Cap, with Cap=2; leave transition system/attempt ceiling unchanged.
- **Keep unrelated guards valid:** Model-only common discipline; isolate baseline and one-site mutant; preserve reconciliation before timer/retry, fresh IDs/events and Cap=2. No authority, policy, digest or logical-time fields apply. Do not add retry attempts or new enqueue paths.
- **Independent oracle:** Independently establish MarkDispatch count ≤ attempt ≤2 and that effect=Prepared ∧ Len(outbox)=2 cannot be exposed. Exact mutant equivalence requires a declared observation relation and separate formal classification.
- **Positive control:** Same reachable prefix: at second dispatch old length=1, so both <2 and <=2 admit. This is positive reachability control, not a mutant kill. Full candidate’s separate two-enqueues/third-input control must retain its own identity.
- **Decisive falsifier and rival:** A reachable third append or Prepared∧length2 with all other dispatch guards true falsifies structural argument. No difference at finite sampled bounds alone does not establish equivalence.
- **What this does not prove:** No full-candidate queue bug, production flow-control guarantee, or all-mutants-unreachable claim. Shared M31 label is not a shared site.
- **Allowed future scope:** Provider-free unchanged reduced baseline/mutant classification after authorization; optional full Enqueue exercise is separate evidence, never reused kill receipt.
- **Stop or inconclusive:** Stop if an altered model introduces a new reset/attempt or if full candidate site is substituted. Bounds-only failure to find a witness remains inconclusive absent proof.
- **Additional evidence:** Common formal artifacts plus exact mutant diff, exposure predicate, invariant argument/proof and declared observation relation.

### 13 SK05 Specify LiveDrain recovery progress premise

**Layer:** full candidate LiveDrain semantics. **Status:** UNEXECUTED.

- **Prefix and control qualification:** Formal-model case; M1A packet-prefix discrepancies do not apply. Retain exact model/config/premise scope.
- **Exact fixture or prefix:** F Init → Crash → Enqueue(c) → stutter forever. One valid finite command identity, zero committed events, one queue slot, no effect; ample event capacity and valid exact recovery input.
- **Contract and source guard:** F:185–186,197–198,243; Recover omitted from listed weakly fair actions.
- **One isolated change:** No target mutation. Isolate premise interpretation: valid recovery input merely exists versus stable suffix starts healthy after Recover/replay, or explicitly forces eventual recovery.
- **Keep unrelated guards valid:** Full-model common discipline; retain Crashed/RecoveryNeeded, finite input domain, queue<2, no later arrivals/crashes/invalidating controls and sufficient event capacity. Use a valid recovery input and well-formed command under the full specification. Do not import M1A attestations or reduced-model caps as substitutes.
- **Independent oracle:** Independently transcribe exact temporal premise and listed fairness. Under literal existence-only recovery premise, check lasso is admissible while receipt never appears. Under healthy-suffix premise prove Crashed∨RecoveryNeeded excluded; under progress premise identify the exact eventual recovery/healthy replay obligation.
- **Positive control:** Same queued command with successful Recover and valid complete replay before stable suffix, fair processing and ample capacity; require eventual receipt/drain. The added recovery condition must be explicit, not assumed.
- **Decisive falsifier and rival:** An existing exact premise/fairness obligation that excludes the lasso refutes that interpretation’s counterexample. A fair admitted lasso without receipt falsifies literal LiveDrain, not safety.
- **What this does not prove:** No runtime hang, unavailable-disk/provider liveness, safety violation or impossibility of a stronger complete formalization.
- **Allowed future scope:** Provider-free independent transcription and lasso/premise check after authorization; no real recovery service.
- **Stop or inconclusive:** Stop if prose cannot be transcribed unambiguously, command/recovery input validity cannot be established, or bounds run out. Do not silently add fairness or smuggle premises into safety.
- **Additional evidence:** Common formal artifacts plus alternative premise formulas, enabledness/fairness ledger, lasso and healthy drain control trace.

## Residuals that remain outside these 13 cases

The coverage matrix’s all-gates/evidence completeness, admission-equivalent replay, aggregate sibling resource conservation, route/budget/observation tuples and other revision/fence/logical-time axes remain residual questions, not additional proven bugs (A:256–263,328–333; R:308–310,608–720; P:223–234,401–405; W:220–224,338–341). These small cases do not qualify those broader obligations.

The reduced model never writes Unknown even though it names that value in its type/guard sets (K:65,177,194,203,212,220); raising IDs/events cannot manufacture absent semantics. The known InFlight/retryReady witness is not duplicated here. Full-candidate captured-fence checks and platform broker/receiver/process ownership still need their own evidence; no new stale-authority bypass or wall-clock Stop guarantee is asserted.

No language, store, framework or vendor selection is reopened. D018–33 remain closed for this handoff; pure M1A Pause is not retrofitted into all accepted Stop modes. No live targets, models, providers, Work sessions, credentials, accounts, live hosts, installs, spending or counsel are within this drafting or proposed provider-free reproduction scope.

## Repository relative citation key

All source citations resolve at the pin above. T fixture and test suffixes are relative to the T directory. The source-review inputs were the supplemental kernel audit (SK01–SK05), semantic guard coverage report (SG01–SG08) and its 24-row coverage matrix. Their classifications are retained; this synthesis is not another independent source reread. The JSON companion preserves the union of matrix and supplemental manifest source hashes, exact input-report artifact hashes and complete per-case stop/evidence fields. Source pin attribution is by declared commit plus matched file hashes; the exported source tree does not independently establish Git HEAD.

- **W:** `docs/v3/M1A-WIRE-PROFILE.md`
- **O:** `docs/v3/M1A-FIXTURE-ORACLES.md`
- **P:** `docs/v3/AUTONOMOUS-PLANNING.md`
- **V:** `scripts/v3/planning/validation/canonical.py`
- **A:** `scripts/v3/planning/validation/contracts.py`
- **R:** `scripts/v3/planning/replay/kernel.py`
- **T:** `scripts/tests/v3/planning`
- **K:** `experiments/v3/fu-03-formal-model/RIntegrated.tla`
- **KC:** `experiments/v3/fu-03-formal-model/RIntegrated.cfg`
- **MG:** `experiments/v3/fu-03-formal-model/mutants.py`
- **F:** `docs/v3/research-lane/followups-20261002/raw/ds-FU-03-formal-model-vectors.md`

Authority and scope: `CONTROL_PLANE.md`; `ANCHOR.md`; `docs/v3/START-HERE.md`; `state/DECISIONS.md`; `docs/v3/M1A-CONSTRUCTION-CAMPAIGN.md:9–11,48–52`; O:74–82,220–222. Product specifications outrank experiment PASS results; synthetic authority and bounded local evidence do not establish production safety.

## Input artifact provenance

These are report-package-relative artifact identifiers, not private filesystem paths or repository source citations. Exact final input bytes used for this correction:

- `additional-kernel-research/SUPPLEMENTAL-KERNEL-AUDIT.md`: `eae6444e59169e5908d2f0a8a058930b98d28054c0d0fb27e7cd95cd3e0a9b56`
- `additional-kernel-research/SOURCE-MANIFEST.json`: `a4f0999126284e46b4a9d513c0963668345a4f0900df5c27058d167d80719b68`
- `semantic-guard-research/SEMANTIC-GUARD-COVERAGE.md`: `bce322e7917c4223f8ece5aa2e78b4a03d4ff8f6853f59ddcaf05e18b6feb426`
- `semantic-guard-research/coverage-matrix.json`: `5d574b79d6bade26b7e267177d41bd11657374a157a6452085dc90b37e5d579a`

Repository source hashes now cover all 42 union entries, including K, KC, MG, F and the M1A construction campaign. Source hash matching and literal JSON inspection do not constitute target execution.

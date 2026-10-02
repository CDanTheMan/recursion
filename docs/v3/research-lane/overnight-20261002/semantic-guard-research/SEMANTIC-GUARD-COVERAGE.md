# M1A semantic guard coverage

Source commit: **73d70505b8c266fbb08d820d304ebd2e68ac7f1b**  
Date: **2026-10-02**  
Status: **independently reread static/inferred audit; synthetic candidates UNEXECUTED**

## Result and scope

Eight additional small discriminators deserve independent local review: replacement lease epochs, stale packets under fresh envelope leases, task-to-packet effect attenuation, gate-assignee identity, missing downgrade exceptions, missing amendment co-authority, authority-policy resolution, and terminal success while effect ambiguity remains. They are source-level candidates, not observed failures or accepted fixes.

The useful negative result is equally important: the visible implementation does enforce command digest/authority-candidate binding, role separation for parent mutations, exact current envelope goal/plan/lease checks, DAG membership and conflicts, plan/task upper budget bounds, retry ceilings, immutable record content, receipt-journal idempotency, event-chain continuity and checkpoint binding. Those checks do not automatically establish the finer semantic joins below.

Only static text reading, JSON fixture parsing, hashes and this separate deliverable were used. No repository code was imported or executed; no tests, model checker, provider, harness, installation, account, credentials or live host actions were used. The source and frozen main packet were not edited. This covers the three pure planning implementation files and their visible fixture runner; it does not claim a repository-wide runtime audit.

The separate supplemental audit's reservation equation/parent-bound family and zero/nonmonotone Pause candidate are **not new findings here**. Formal-model candidates from that report are also excluded. No result here authorizes replacing frozen oracle values.

## Citation key and authority

Every source citation is repository-relative at the commit above:

- **W** — `docs/v3/M1A-WIRE-PROFILE.md`
- **O** — `docs/v3/M1A-FIXTURE-ORACLES.md`
- **P** — `docs/v3/AUTONOMOUS-PLANNING.md`
- **V** — `scripts/v3/planning/validation/canonical.py`
- **A** — `scripts/v3/planning/validation/contracts.py`
- **R** — `scripts/v3/planning/replay/kernel.py`
- **T** — `scripts/tests/v3/planning/`; fixture pointers are below `T/fixtures/`

`CONTROL_PLANE.md`, `ANCHOR.md`, `docs/v3/START-HERE.md` and decisions D-017–D-033 were read. D-017's heading still says OPEN while its chosen greenfield direction is reflected in the higher-precedence control plane; this audit does not reinterpret that status. Accepted product/platform/Stop/credential decisions do not turn frozen pure M1A fixtures into production guarantees. O:76–82 explicitly makes authority synthetic; O:220–222 limits fixture conclusions. P's broader semantics inform the audit, while W/O provide the exact M1A encoding and oracle obligations.

**Evidence classes:** quoted obligations and visible comparisons are source-documented. Predictions about a newly constructed command's result are inferred and unexecuted. End-to-end runtime behavior, independent reproduction and any additional mandatory caller layer are unknown. `coverage-matrix.json` records these distinctions and source hashes.

## Shared call path and test discipline

The visible fixture runner calls `R.admit` directly (`T/conformance.test.py:24–56`). Admission validates the input projection and receipt journal, checks schema/self-digests and duplicate identity, then invokes `A.validate_admission` (R:517–580). Accepted proposals reach `_event_specs`, `_make_event` and `reduce` (R:588–599). The reducer validates records/digests and event continuity, inserts immutable records, and performs event-specific state changes (R:152–276). V's record/projection validation validates shapes, scalar ranges and selected local conditionals, not every cross-record predicate (V:936–1072,1156–1186,1351–1410).

Each proposed test below must use fresh command/record identities where needed, current state version/digest, valid sorted closed records, recomputed record/payload/candidate/command digests and matching **synthetic** candidate attestations. Preserve valid actor/lease/time/policy bindings except the one being discriminated. The repository itself uses this resealing pattern (`T/adversarial.test.py:38–54`). No credential or real grant is involved. A refusal caused by a stale state hash or broken candidate digest is inconclusive for the intended semantic guard.

**Known shared setup limitation:** W:583–587 requires a derived packet's `correlation_id` to equal its GoalSpec ID. Stored packet events in F-M1A-001/005, every F-M1A-006 case, and F-M1A-011/014/016 instead use `CORR-M1A` while binding `GOAL-M1A`; R:282–289 hardcodes that correlation metadata. This is a source-observed setup inconsistency, not an executed result or an additional promoted finding. All packet-dependent recipes below are therefore diagnostic against those unchanged historical prefixes, including their nominal positive controls. F-M1A-005 additionally has SG03's effect mismatch. A strictly wire-valid isolated test requires a separately identified, reviewed fixture/source regime and full-prefix revalidation; digest resealing alone cannot repair the original target's hardcoded metadata. Preserve historical bytes and name any separately authorized changes explicitly. Descriptions below of otherwise-valid fields or controls are conditional on this preflight, not certifications of whole-prefix validity.

Before claiming any isolated conformance failure, independently validate the entire setup prefix and positive control against the whole applicable contract, not merely the target implementation or its stored expected digests. Acceptance of an inconsistent setup is diagnostic only. Later authorized tests should assert raw receipt, event list, whole projection and preserved input values. Pair every negative with an otherwise-identical valid control. Refusals must be atomic. Never repair a test by removing an unrelated safety check or updating a frozen expected value silently.

## SG01 — Replacement lease epoch need not advance by one

**Required:** W:332–334 requires an active lease's ordered interval and replacement epoch exactly old+1; W:592–595 requires the exact current supersession target. O's F-M1A-006 and 019 exercise stale-holder rejection after valid replacement.

**Discriminator:** take `F-M1A-006.json`, case `stale-lease`, immediately before its first command. Change only the proposed fresh `LEASE-WORK-2` payload epoch from 2 to 1, keeping `old_lease_ref` and `supersedes_lease_ref` exactly bound to the current epoch-1 lease. Reseal the proposal and matching Head attestation. One replacement command is sufficient; no worker probe is necessary to observe an invalid epoch transition.

**Visible path:** V:1034–1036 validates epochs as UInt. A:384–397 checks an envelope lease when present, but the fixture replacement is Head-authored with null envelope lease. The rest of A:399–528 has no replacement-epoch branch. R:442–445 emits the new lease directly; R:185–190 marks the superseded lease replaced, without comparing epochs. R:120–149 inserts the fresh identity and declared active state. The predicted result is an accepted replacement with equal epochs, not a bypass of old-lease digest/state checking.

**Coverage:** the literal replacement uses 1→2; the stale worker then submits the old lease. That tests the old lease's projected state, not arithmetic on the replacement. The existing adversarial expiry probe tests use at the half-open expiry boundary, not creation of a malformed lease interval.

**Conforming rival and decisive test:** a mandatory pre-admission layer could enforce +1, but it must be shown on the actual direct fixture/public call path. Independently call the same boundary with 1→1 and 1→2 controls; require the former to refuse without changing either lease. The exact error choice should be pinned before execution if not already specified.

**Does not prove:** two live writers, process fencing, takeover safety, or an external-effect replay. Goal fence/revision monotonicity is separately mapped, not claimed proven by this lease case.

## SG02 — A fresh lease envelope can carry a result for the old packet

**Required:** W:570–579 and P:274–277 bind the packet to its current lease; a lease replacement makes the old binding stale before the next action. O's F-M1A-006 promises stale old-packet results refuse.

**Discriminator:** use the same case after its valid lease replacement. In its subsequent worker-result command, retain the old `work_packet_ref` and valid worker actor, but replace only the envelope lease ref with the new active lease. Keep the worker-result's own creation-lease metadata consistent with the new envelope for isolation. Reseal all affected records and candidate attestation. The replacement lease has the same goal, plan, task, worker and permitted command, with issue 7/expiry 900; the probe is inside that interval.

**Visible path:** A:380–397 validates current envelope goal/plan and the new lease's actor/time/goal/plan. It does not compare that lease to the payload packet's captured lease or resolve the packet for `submit-worker-result`. R:389–390,413–416 emits the simple record; R:209–214 marks the referenced old packet `result-submitted` and its task `gate-pending`. No packet-freshness join intervenes.

**Coverage:** the frozen stale-lease probe submits the old envelope lease and is caught by A:386. It does not isolate a stale payload reference under a current envelope. Null-lease variants are deliberately unnecessary here.

**Conforming rival and decisive test:** a design could allow observations from stale work for history, but the admitted transition must not advance the old packet/task into the current completion path and must be explicitly distinguished from this oracle's refusal. Run old-envelope and new-envelope variants against the same old packet; require stale refusal/no progress, or an explicitly approved inert-observation contract. Include a newly reissued packet/current-lease positive control.

**Does not prove:** an unauthorized actor, physical execution, source freshness, or real stale results being accepted by a deployed service.

## SG03 — Packet effects widen back from the task to the goal

**Required:** W:569–576 says the packet copies TaskNode effect fields; P:57–63,262–272 requires descendant intersection/attenuation.

**Discriminator:** in the F-M1A-001 planning prefix, narrow the one task's `effect_keys` from `[EFFECT-SYNTHETIC]` to `[]`, leaving the goal's allowed set unchanged. Recompute task/plan graph/transition and downstream reservation/lease/route refs and command bindings. Derive the packet. This is a valid narrowing, not a widened parent or two-node conflict.

**Visible path:** A:256–278 accepts the subset, and the one-node DAG has no competing owner. R:324–340 copies most fields from the task, but **R:327 explicitly copies `goal.payload.allowed_effect_keys`**. Thus the predicted packet restores `EFFECT-SYNTHETIC` despite the task allowing none. R:428–429 compares the caller's expected digest to the generated record, not to a second semantic attenuation oracle.

**Stronger literal-source observation:** no mutation is needed to see this mismatch in the stored positive oracle. In `F-M1A-005.json`, case `amend`, `initial_events[3].related_records` contains `TASK-M1A-A` with `effect_keys=[]` and digest `0b5bed6c6f30f395b7b3a387b3dafbd1960b5ce57adc369b903f19db83301ba2`. `initial_events[6].primary_record` is packet `PACKET-b4eb25dd79a41ba8692a4b4354af95f6`, whose task ref binds that exact digest but whose effects are `[EFFECT-SYNTHETIC]`; its digest is `cc53dcc8b141453c293a08b509c1418d8dc85e78f11fb434d69d072fcf82f5b0`. This is observed **fixture data**, not observed execution. It means that positive oracle equality alone would preserve this particular wire mismatch.

**Coverage:** literal F-M1A-001 uses the same effect set in goal and task, so either source expression agrees there. `T/property.test.py:84–100` tests a task effect outside the goal; it does not test a task strictly narrower than the goal. F-M1A-005 supplies the stricter-subset literal witness above, but its stored expected packet is already broad.

**Conforming rival and decisive test:** no union interpretation satisfies the cited exact copy rule. A rival implementation that refuses inconsistent derivation inputs or emits the attenuated empty set conforms. Use an independently assembled expected packet with empty effects; the present path is predicted to reject its expected digest or emit the broad packet when supplied the implementation-derived digest. Record both observables, including unrelated frozen metadata discrepancies rather than silently correcting them.

**Does not prove:** any real effect is dispatched or that the widened key adds authority beyond the GoalSpec. It specifically loses the narrower TaskNode boundary.

## SG04 — Gate actor role is checked; the gate's assigned actor is not

**Required:** W:238–239 and O:84–88,124 allow only the assigned gate verifier to submit its gate. Assignment cannot be created by self-reported independence (P:268–272).

**Discriminator:** after F-M1A-001's worker result, submit its gate result from a different synthetically attested verifier actor. Keep the task/packet's actual `GateRequirement.assigned_verifier_actor_id` unchanged. Make record creator and synthetic independence verifier identity consistently name the alternate actor; keep the declared gate requirement unchanged. This isolates the difference between having verifier role and having this gate assignment.

**Visible path:** A:361–376 verifies candidate, actor, allowed command and verifier role. There is no `submit-gate-result` branch comparing task requirements to command actor. V:593–609 validates the requirement/independence fields structurally. R:389–390,413–416 emits `GateResultRecorded`; R:215–218 immediately sets task verified on pass. The plan-assignee comparison at A:334–336 applies only to plan decisions.

**Coverage:** F-M1A-010 `verifier-missing` tests the plan-assignee comparison; it is not a gate-assignee negative. F-M1A-020 tests worker/verifier parent mutation, a different role boundary.

**Conforming rival and decisive test:** an authoritative assignment-change event could permit a new verifier, but none is introduced here. Test the assigned and alternate actor with equally valid synthetic role/candidate attestations; only the assigned actor should advance gate state. Pin the intended refusal error before execution.

**Does not prove:** production authentication failure or that an unauthenticated caller can create a fixture attestation. It tests the documented semantics after synthetic role authorization.

## SG05 — Downgrade can refer to an exception that was never admitted

**Required:** W:250–255,490–496 and O:97–104 require both policy permissions plus an exact previously admitted unexpired Owner exception. O's F-M1A-011 explicitly demands missing/mismatched/expired bindings refuse.

**Discriminator:** keep F-M1A-011's valid prefix including its admitted Owner exception. In the following `downgraded-pass` decision change only `owner_exception_ref.id` to `OWNER-VERIFIER-EXCEPTION-ABSENT`, which has no record in that state. Preserve the original ref's version/digest and every other field, then reseal the decision, command and matching verifier attestation. The original exception still exists, but the decision does not reference it. This isolates exact-ref resolution without altering the event-log binding or state history.

**Visible path:** V:1046–1058 checks downgraded disposition/assurance and a non-null ref, without resolving it. A:322–337 checks existence of a passing gate per task ID and the plan-assigned actor; A:507–510 calls only that verifier helper. It never resolves the decision's exception. R:236–264 can therefore mark the plan `terminal-verified-downgraded` once its task remains verified. The distinct downgraded suffix is preserved, which is a useful enforced negative.

**Coverage:** literal F-M1A-011 has only the positive `downgrade` case with exception then decision. Its missing/expired variants described by the prose oracle are not literal cases there. This is a fixture inventory observation, not a newly executed failure.

**Conforming rival and decisive test:** treating a non-null ref as trusted ambient authority conflicts with the same-bundle/prior-admission requirements. A mandatory external resolver would need demonstration. Compare the exact valid exception ref against absent, expired and wrong-candidate variants, one mutation at a time; the absent one-command suffix is smallest. Require refusal and no terminal transition.

**Does not prove:** a full-assurance claim, constitutional release assurance, or any actual Owner risk approval. M1A independence remains synthetic and deliberately incomplete.

## SG06 — Amendment's separate ARM attestation is parsed but not resolved

**Required:** W:490–495 makes the Owner's full-command approval and separately candidate-bound current ARM proposal both mandatory for the atomic amendment bootstrap.

**Diagnostic recipe and setup prerequisite:** F-M1A-005 supplies a stored amendment composite and prefix, but its original prefix contains SG03's known TaskNode/packet effect mismatch. It is not an independently valid whole-contract prefix or positive control. An unknown `payload.arm_proposal_attestation_id` under that unchanged historical prefix can probe the visible missing lookup, but any acceptance is diagnostic only. Before claiming an isolated conformance failure, use a separately identified synthetic fixture whose complete prefix and positive amendment control have been independently resealed and revalidated against the whole applicable contract. Preserve the original historical fixture bytes; do not silently repair its expected oracle. In that independently valid setup, change only `payload.arm_proposal_attestation_id` to a valid-format ID absent from its authority table, recompute the full command candidate and matching Owner attestation, and leave the valid replacement records, dispositions and ARM table entries unchanged.

**Visible path:** V:1292–1293 validates only the ID syntax. A:361–376 resolves `command.auth_ref` (the Owner), while A:409–432 validates replacement goal/policy/scope/DAG and A:511–521 checks matching disposition sets and target coverage. No lookup uses `arm_proposal_attestation_id`. R:446–455 emits amendment/replacement/dispositions.

**Coverage:** F-M1A-005 is the stored positive amendment composite, with the setup qualification above; F-M1A-023 and the adversarial mutation exercise missing dispositions, not missing ARM approval. Good disposition coverage is not co-authority coverage.

**Conforming rival and decisive test:** the accepted M1A wire profile explicitly requires this second attestation; an Owner-only amendment design needs a reviewed contract change. After independent whole-prefix/control validation, compare the valid composite with the unknown ARM ID under equally valid exact Owner candidate bindings. Require atomic refusal of the unknown reference; a prior schema/digest failure is inconclusive. A reproduction using only the original inconsistent F-M1A-005 prefix cannot establish an isolated semantic conformance failure. The source-supported absence of the ARM lookup does not depend on that prefix being valid.

**Does not prove:** an Owner cannot authorize product changes, a deployed principal escalation, or that the complete compatibility/disposition algorithm is correct.

## SG07 — Authority attestation policy references are not resolved in admission

**Required:** W:246–254,264–273 and O:76–82 require exact same-bundle policy resolution, authority kind and GoalSpec-bound constitution equality.

**Discriminator:** keep F-M1A-001's otherwise valid plan command after its first three commands. In only the matched synthetic authority attestation, replace `authority_policy_ref` with a well-shaped unknown policy ID/version/digest and recompute the attestation digest. Do not change actor, candidate digest, command type or time, nor the actual goal/task policies.

**Visible path:** V:1423–1445 validates ref shape. A:348–352 validates each supplied fixture; A:365–376 verifies the attestation digest/candidate/actor/role/time, but never resolves its policy refs. A:280–307 resolves the goal/plan/task policies, not the attestation's. All graph and scope guards can still pass.

**Coverage:** the unknown-policy command in F-M1A-021 is `apply-pause`; the adversarial unknown-policy mutation changes a TaskNode authority policy. Both reach other exact policy lookups. They do not discriminate this authority-attestation reference.

**Conforming rival and decisive test:** an independently mandatory policy-table admission boundary could enforce it, but the visible direct entrypoint does not call one. Test present versus unknown authority ref while leaving the command candidate identical; require `E-POLICY-UNKNOWN` and unchanged projection. Constitution mismatch is a separate follow-on mutation, not necessary for this smallest case.

**Does not prove:** possession of credentials, the authenticity of real attestations, or failure of the task-policy equality guard.

## SG08 — Terminal verification can coexist with unresolved M1A effect ambiguity

**Required:** O:135–137 explicitly prohibits `terminal-verified` with ambiguous effects; O:200 (F-M1A-016) says the plan cannot terminate verified. This is the decisive boundary: output-gate verification alone may be meaningful even when effect settlement remains unresolved. W:443–444 quarantines the packet and task.

**Discriminator:** start with F-M1A-001's first eight commands (through worker result). Record a valid fresh synthetic ambiguous effect on that packet using the F-M1A-016 observation shape. Then submit the otherwise valid assigned gate pass and assigned full plan decision, freshly bound to each new state and the actual event-log/gate digests. This is an observation plus two completion commands; use fresh IDs and monotonically increasing times.

**Visible path:** R:230–235 appends the effect to `ambiguous_effect_refs` and quarantines packet/task. A's explicit ambiguity guard at 472–473 is inside `propose-retry` only. Gate admission has no object-state/ambiguity check; R:215–218 changes the same task to verified. A:322–337 sees a passing gate and correct assigned plan verifier. R:236–264 tests exact active plan and all task states verified, but not the nonempty ambiguity set, so predicts `terminal-verified`, a completed task and consumed packet while the same unresolved effect remains in `ambiguous_effect_refs`, with no reconciliation or disposition. Gate-state overwrite is the mechanism; this terminal invariant is the finding.

**Coverage:** literal F-M1A-016 contains only `record-effect-observation` then `propose-retry`. It has no success/completion probe, although the prose row specifies one. The source-enforced retry refusal therefore does not establish the success half.

**Conforming rival and decisive test:** stale/ambiguous observations could be historical after an explicit reconciliation/disposition, but this sequence adds none. Require the plan to remain nonterminal while ambiguity remains; the implementation may preserve an honest separate output-gate result, but may not use it to bypass the terminal guard; pair with the no-ambiguity successful path. An accepted terminal result with a nonempty ambiguity set is the decisive local counterexample, if independently reproduced.

**Does not prove:** external effect success, actual duplicate dispatch, rollback, or runtime safety. It concerns only the synthetic terminal projection.

## Coverage ledger and useful negatives

The machine matrix is a map of visible checks and selected coverage, not an exhaustive proof. In particular:

- **Resource conservation:** A:256–263 enforces each plan/task component against GoalSpec. Reservation equations, reservation parent bounds and positivity have no equivalent branch in the inspected path; those belong to existing supplemental SK01, not a new claim here. Aggregate sibling conservation remains unproven.
- **Revision/fence/time monotonicity:** W:332–334 and P:77,120 require more than UInt. A/R compare current envelope refs, but no monotone revision/goal-fence/logical-time predicate was located in these files. SG01 gives one fully traced lease discriminator. Other axes remain bounded static gaps without additional reported counterexamples; Pause is already SK02.
- **Identity/duplicates:** R:120–128 refuses unequal content at an existing immutable key; R:554–576 checks content before exact duplicate return and ID conflict. O's F-M1A-017 and adversarial duplicate/conflict probes directly target this. Equal immutable content can be reused; no claim of record-level exactly-once semantics follows from command deduplication. Derived collision error mapping in W:589–590 versus R:125 also deserves explicit future reconciliation rather than being called an executed failure.
- **Goal/plan/task graph:** A:99–180 validates exact task refs, identity plan refs, edge agreement, acyclicity and unordered ownership. A:409–432 checks plan GoalSpec equality and graph digest. Positive/discriminating F-M1A-003/004/022 and property permutations exist. These are genuine guards.
- **Route/budget-to-packet joins:** derivation resolves a reservation (R:308–310), but existence alone is not equality of its goal/plan/task. W:338–341's route/account/pool/observation tuple has no complete check in A:434–440; route replacement at A:502–506 checks route allowlist and nonmetered status only. These are mapped static coverage limitations, not additional fully constructed candidates in this bounded pass.
- **All gates and evidence:** A:328–333 counts passing task IDs, not every GateRequirement or exact task digest. R:215–218 marks verified on each individual pass. Candidate/source/event-log digest and full required-dimension joins are not supplied by the few structural conditionals. This audit's small assigned-actor/exception/ambiguity cases do not purport to test every evidence relation.
- **Replay:** R:152–175 and 659–720 enforce schema, chain, stream, state and receipt/event boundaries; R:608–654 checks checkpoint snapshot bindings. Replay does not call `validate_admission`, receive authority/policy fixtures, or regenerate `_event_specs` from the paired command. Therefore replay's success is not independent evidence that all admission semantics were enforced. A trusted previously admitted journal is a possible narrower design; P:401–405 and W:220–224 require its precise trust boundary to be reconciled. No forged-log runtime claim is made.
- **No live dispatcher:** `_event_specs` is pure command-to-event construction; it is not a broker, receiver, process launcher or external effect dispatcher. Missing later platform guarantees are not counted as M1A defects.

## Suggested next action

Independently review SG03's explicit field source, SG05's absent-record case and SG01's one-field epoch mutation first; they offer short discriminators with strong literal clauses. Then check SG02/04/06/07's cross-record authority joins and SG08's terminal path. Any execution or repair needs a separately authorized exact candidate, independent oracle and no silent changes to historical receipts. Finding one earlier guard that legitimately refuses the constructed case should narrow or withdraw that case, not be worked around outside its documented scope.

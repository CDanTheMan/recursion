# Supplemental deterministic-kernel audit

Status: **independently reread static/inferred candidates; UNEXECUTED; no runtime qualification**  
Source commit: **73d70505b8c266fbb08d820d304ebd2e68ac7f1b**  
Prepared: 2026-10-02

## Result

Five useful additional discriminators emerged: an M1A reservation-conservation candidate, an M1A zero-epoch Pause candidate, an absent second-attempt completion path in the reduced formal model, a structural reason enlarging bounds cannot expose that model's M31 mutation, and an underspecified recovery premise in the full candidate's liveness claim.

An independent static reread supported all five findings at their stated inferred level and found no blocking semantic correction. That review checked the initial draft and all 14 then-listed source hashes; the revised clarification delta and final artifact identity remain separately checkable. None is an executed counterexample, runtime failure, accepted fix or production-safety verdict. The first two concern the inspected pure M1A admission/reduction source. The next two concern only the simplified `RIntegrated.tla` experiment. The last concerns the written full FU03 candidate, which is a different model. These distinctions are essential.

The known seven-step enlarged-bound `InFlight`/`retryReady` witness is not repeated here. No repository files or frozen research packet were changed. No target code was imported or executed; no checker, tests, benchmarks, external provider or live host was used. Source reading, JSON fixture parsing and artifact writing were the only activities.

## Post-delivery setup clarification — 2026-10-02 10:31 UTC

A continued independent handoff review found a shared setup limitation in stored packet-bearing fixture prefixes. W:583–590 requires each derived WorkPacket's correlation ID to be the GoalSpec ID. R:282–290 instead constructs records with `correlation_id="CORR-M1A"`; the inspected F-M1A-014 stored packet has that value while its goal is `GOAL-M1A`. Therefore SK02's unchanged seven-command stored prefix is a **producer-diagnostic seed, not an independently whole-contract-valid conformance seed**.

The static zero-epoch guard/assignment argument remains intact. Before claiming an isolated SK02 conformance violation, a later authorized session must separately identify, construct/reseal and independently revalidate a whole-contract-valid seed and its complete packet/reference/digest/expected-state dependencies. Preserve and report the stored-seed diagnostic separately. Merely editing and resealing packet bytes does not change the target's hardcoded constructor: identify the exact unchanged-source/fixture regime or separately authorized changed-source regime. An earlier packet or digest refusal is not evidence that the Pause epoch guard works. If the unchanged producer cannot construct the required valid seed, classify that setup blockage explicitly; do not silently change the historical fixture, implementation or oracle to force the Pause test through. This is a post-delivery setup qualification, not another guard finding or an executed runtime failure.

SK01's five-command prefix and reservation probe precede packet creation and are unaffected **on this correlation-ID axis**; that is not blanket certification of all other seed constraints. Historical source fixtures and the already delivered ZIP remain unchanged. This current supplemental source revision is for the next checkpoint.

## Citation key and authority

All references below are repository-relative at the pinned commit:

- **K**: `experiments/v3/fu-03-formal-model/RIntegrated.tla`
- **KC**: `experiments/v3/fu-03-formal-model/RIntegrated.cfg`
- **MG**: `experiments/v3/fu-03-formal-model/mutants.py`
- **F**: `docs/v3/research-lane/followups-20261002/raw/ds-FU-03-formal-model-vectors.md`
- **V**: `scripts/v3/planning/validation/canonical.py`
- **A**: `scripts/v3/planning/validation/contracts.py`
- **R**: `scripts/v3/planning/replay/kernel.py`
- **W**: `docs/v3/M1A-WIRE-PROFILE.md`
- **O**: `docs/v3/M1A-FIXTURE-ORACLES.md`

`CONTROL_PLANE.md` establishes that product specifications outrank experiment evidence and that independent verification, not the implementer's PASS, controls acceptance. `ANCHOR.md` requires a proven deterministic core and honest bounded evidence. D-017–D-033 were reviewed; notably D-022 adopts shared Aggressive/Full/Lazy Stop vocabulary and requires reconciliation with the formal model and broker. This supplement does not reinterpret that accepted product scope, retrofit the frozen M1A profile, or treat its `apply-pause` command as an implementation of all three Stop modes.

M1A itself is local construction only and does not create an operative runtime (`docs/v3/M1A-CONSTRUCTION-CAMPAIGN.md:9–11,48–52`). Its authority fixtures are explicit synthetic candidate bindings, not production authentication (O:74–82). The existing adversarial test helper already reseals the matching synthetic authority candidate when changing a proposal (`scripts/tests/v3/planning/adversarial.test.py:47–54`). Citing that helper does not report executing it or authorize changing any real credentials, grants or production state.

## SK01. M1A: an individually nonconserving reservation appears admissible

**Class:** unexecuted source-level candidate contract violation. High confidence in the missing comparison; actual end-to-end admission remains unverified.

**Required contract.** W:335–338 requires, for every reservation component, `consumed + remaining = limits` without overflow and limits no greater than the referenced goal/task. O:155 identifies budget widening as a refusal class. This is stronger than checking that all three vectors contain nonnegative integers.

**Smallest discriminating suffix.** Start from the valid F-M1A-001 prefix immediately before its sixth command (`reserve-budget`). Retain its valid goal, task, plan, actor, authority and current-state bindings. In a newly authored synthetic reservation set only the tokens triple to:

- `limits.tokens = 1`
- `consumed.tokens = 1`
- `remaining.tokens = 1`

Keep every other component valid, preserve `state=reserved`, and use a fresh reservation/command identity with correctly recomputed record, payload, candidate, command and matching synthetic authority-attestation digests. The upcoming fixture identity `BUDGET-RESERVATION-1` is already fresh: it occurs zero times in the first five commands. Keeping it avoids unnecessary ID changes. Preserve its exact goal/plan/task refs and the current unexpired ARM lease; those parent records do not contain reservation-ref fields needing replacement. No packet is derived in this one-command suffix, so no packet digest/reference needs to be manufactured. This is one fresh admission and one proposed `BudgetReserved` event beyond the five-command fixture prefix. The triple is a minimal positive-component arithmetic witness: 1 + 1 != 1. No sibling, fork, external spend or runtime meter is needed.

**Why the inspected path appears to accept it.** V:548–552 checks each vector's closed fields and UInt values. V:1008–1009 routes each of `limits`, `consumed`, `remaining` separately through that check. The object-specific tail at V:1041–1072 has blocker/verifier/effect checks, but no reservation equation. `validate_domain_record` invokes those validators without consulting ambient schemas (V:1156–1186). A:340–528 checks fresh command identity/authority/current state, policies and command-specific cases; its plan-only scope checks do not apply to this simple reservation command, and it has no reservation-conservation branch. R:389 maps the command to `BudgetReserved`; R:413–416 emits the simple event; R:176–181 inserts its validated record; R:120–149 preserves its payload/state. R:517–599 contains the public admission path and final projection/receipt construction. Projection validation at V:1351–1410 repeats structural/record validation, not the missing equation.

**Conforming rival.** A separate, mandatory independently specified admission layer might enforce the equation before this function. That would falsify a claim about the complete public entrypoint only if the caller boundary is demonstrated and cannot be bypassed. Alternatively, enforce the equation in the pure semantic admission layer and independently in replay validation. Both conform to W; mere trust in the fixture author's arithmetic does not.

**Decisive later local test.** Independently construct/reseal that one malformed command; call the exact admitted public M1A boundary in a separately authorized session. Require refusal with no event, unchanged projection and unchanged reservation totals. Pair it with a conserving `0 + 1 = 1` control and a parent-limit control. Check raw returned state/events, not only a producer verdict. An earlier digest or authority refusal makes the arithmetic test inconclusive and must be corrected without removing those guards.

**Does not prove:** cumulative sibling conservation, debit accuracy, external overspend, an exploit without synthetic authority, or any live resource claim. The aggregate ledger question remains separate; this smaller equation is enough to discriminate the local implementation from the written contract. The inspected property test targets plan/task budget widening (`scripts/tests/v3/planning/property.test.py:84–100`), not this reservation equation. That is a source-level coverage distinction, not a newly observed test result.

## SK02. M1A: an epoch-zero Pause can be applied without enforcing Pause

**Class:** unexecuted source-level candidate and contract decision. High confidence in the numeric path; whether zero must refuse or be translated to a strictly increasing epoch needs an explicit profile decision.

**Intended observable.** O:198 requires an operative `current-immediate` Pause to make subsequent otherwise-valid plan/packet/worker/effect commands refuse `E-PAUSED`. W:323 gives `new_pause_epoch` type UInt, so it does not itself exclude zero. No explicit resume command is part of this M1A command vocabulary.

**Smallest discriminating suffix.** For a producer-diagnostic trace, use F-M1A-014's stored seven-command active-state prefix, whose epoch is zero. Its packet correlation metadata has the setup limitation stated above; an isolated conformance trace instead requires a separately identified, resealed and independently whole-contract-revalidated seed. Replace the Pause proposal's `new_pause_epoch=1` with zero in a fresh, fully resealed, Owner-attested synthetic command. It still says mode `current-immediate`. Follow it with an independently otherwise-valid worker-result command bound to the new current state. This is one Pause plus one progress probe; it does not require any live effect or new control policy.

A second, stronger variant begins after a valid epoch-1 Pause, then submits a distinct freshly attested Pause with epoch zero before the progress probe. It tests rollback of an established pause, not replay of the old command. Exact duplicate receipts are not fresh control actions.

**Concrete stored-fixture bindings, not whole-contract seed certification.** The F-M1A-014 producer-diagnostic prefix has a packet captured at pause epoch 0 and an active WORKER-LUNA work lease at lease epoch 1, issued at logical time 7 and expiring at 900 (exclusive). That lease permits `submit-worker-result` and binds the same goal/plan as the probe. Pause changes none of those object/lease bindings. The first variant can use the existing worker probe at time 9 with newly current state/version and resealed command/authority; the rollback variant needs a suitably later time still inside both lease and attestation windows. Use a distinct directive identity for the second Pause, never different contents under an already accepted record ID. These checks address freshness, digest, actor and lease requirements, but do not resolve the separate packet-correlation seed limitation. Preserve their counterparts when independently validating a conforming seed.

**Guard/transition reasoning.** V:1034–1036 validates any `_epoch` field as UInt; V:434–439 permits zero. A:403–407 checks the directive's policy and mode but not positive/monotonic epoch advancement. `apply-pause` is absent from A:14–18's PAUSE_SENSITIVE set, so a second Pause is not rejected merely because the state is paused. R:228–229 assigns the supplied epoch directly. A:399–402 enforces Pause only when `current_pause_epoch > 0`. Thus an accepted zero-valued directive leaves that guard inactive; a 1→0 assignment would make it inactive again. Fresh identities prevent immutable-record collision and command-dedup checks from masking the test.

**Conforming rival.** UInt could be only a wire type with an intended but separately enforced semantic precondition `new_pause_epoch > current_pause_epoch`. Show that actual mandatory check if it exists. A second conforming design has the kernel derive the next epoch and rejects incompatible caller values. If Owner-authored zero is intended to mean Resume, that needs an explicit separately accepted semantic rule: neither the `current-immediate` name nor its current oracle expresses such a meaning. Do not silently reinterpret a Stop request as resume.

**Decisive later local test.** First satisfy the separately recorded whole-contract seed prerequisite above, or label the result producer-diagnostic/setup-blocked. Then run the two variants with independently generated exact digests/attestations and a positive epoch-1 control. Require invalid epoch inputs to refuse atomically, or an explicitly accepted monotone-epoch normalization contract. After every accepted Pause, the fresh progress probe must refuse. Preserve the historical epoch-1 F-M1A-014 expectations.

**Does not prove:** unauthorized command admission, actual process continuation, receiver fence failure, or implementation of D-022's Full/Aggressive/Lazy Stop. These remain synthetic pure-kernel semantics.

## SK03. Reduced RIntegrated: retry enters attempt 2, but neither result path can complete it

**Class:** model-adequacy/positive-reachability gap, not a checked invariant violation or production liveness failure.

**Shortest inferred prefix.** With six fresh IDs and at least six events:

1. `GrantLease(w1)` — fresh ID, lease 1<3; owner becomes w1, lease 2 (K:70–76)
2. `Start` — unpaused/uncancelled, owner present, Ready, attempt 0; Running/1 (K:118–125)
3. `SubmitFail` — Running, owner present, attempt 1; Failed (K:136–143)
4. `ArmTimer` — Failed, Disarmed, attempt 1<2; Armed (K:153–159)
5. `FireTimer` — Armed; Fired and retryReady true (K:161–167)
6. `Retry` — Failed, ready, attempt 1<2, effect None; Running/2, timer reset, effect None (K:169–178)

No shorter genesis prefix reaches Retry: each of ownership, Start, failure, timer arm and timer fire is required by a separate action. To discriminate the completion guard from resource exhaustion, use **at least seven IDs and seven events**, leaving a fresh command/event for a Submit or SubmitFail probe. Both remain disabled because K:130 and K:139 require `attempt=1`. No action decreases attempt. Verify needs Submitted, so it cannot rescue this second attempt. Cancel and control actions can remain possible: this is not necessarily global deadlock.

The historical four-ID/six-event baseline cannot reach step 6. KC checks safety invariants and sets `CHECK_DEADLOCK FALSE`; it does not assert eventual useful retry completion. Raising only IDs/events cannot remove the attempt equality.

**Conforming rival.** This may be an intentionally one-shot diagnostic abstraction whose only retry claim is a bounded increment. In that interpretation it is not a model defect, but it cannot support useful-retry completion evidence. The full F:162–166 semantics uses matching current attempt for Submit and permits the two-attempt retry contract. That full model must be reviewed on its own terms.

**Decisive later local test.** Record the exact six-step positive prefix and expose each completion guard with remaining capacity. Require an explicit scope decision: keep the reduced model diagnostic and label this missing behavior, or separately author/review the fuller semantics with an attempt-2 success/failure positive control. Do not weaken a guard just to improve a mutation score.

**Does not prove:** an invariant failure, an implementation bug, unfair scheduling, or that the full candidate lacks second-attempt completion.

## SK04. Reduced M31: third enqueue is structurally unreachable, not merely beyond four IDs

**Class:** static equivalence argument for this exact one-site diagnostic mutation; independent formal classification still pending.

MG:43–45 changes only `OutboxOK: Len(outbox)<Cap` to `<=Cap`. K:17 fixes Cap=2. Only MarkDispatch appends to outbox (K:198–206). It requires Prepared, then changes effect to InFlight. PrepareEffect requires None (K:189–196). The only post-genesis reset to None is Retry, which increments attempt and is allowed only below 2 (K:169–178). Observation/reconciliation never restore Prepared/None (K:208–222). Therefore there are at most two preparations/dispatches over the whole task, one per attempt, and at most two outbox appends.

A shortest inferred prefix reaching a full outbox is:

`GrantLease → Start → PrepareEffect → MarkDispatch → ReconcileEffect(KnownNoEffect) → SubmitFail → ArmTimer → FireTimer → Retry → PrepareEffect → MarkDispatch`

It needs 11 fresh IDs/events. Reconciliation before timer firing also avoids the already-known `NoBlindEffectReplay` witness. At the second MarkDispatch, old length is 1, so both `<2` and `<=2` are true. Afterwards length is 2 and effect InFlight at attempt 2. No further Retry can reset it. Even allowing second-attempt SubmitFail would not bypass `attempt<2`.

Thus the changed predicate is never reached with all other MarkDispatch guards true and length 2. Merely enlarging IDs/events, even beyond the full-outbox prefix, cannot expose M31. This is a source argument about all traces of the unchanged transition system; it is not a newly executed exhaustive proof or a final mutant receipt.

**Conforming rival.** Keep the toy model and formally classify M31 as equivalent within its declared observation relation; alternatively instantiate the full candidate's actual queue mutation. F:289 names M31 at input Enqueue, and F:185 lets arbitrary finite inputs fill a two-slot Inbox. A third enqueue there does not require a third task attempt. These are different sites and cannot share a kill claim by name alone.

**Decisive later local test.** Independently check the invariant “number of MarkDispatch events ≤ attempt ≤2” and the impossible exposure predicate `effect=Prepared ∧ Len(outbox)=2` in the unchanged simplified baseline and mutant. Then separately expose the full candidate's Enqueue guard with two entries and a third proposed input. Classify each exact site, not the shared label.

**Does not prove:** production flow control, a bug in the full queue model, or that every other mutation is unreachable. A safe toy trace space can still be too narrow to qualify a required safety mechanism.

## SK05. Full candidate LiveDrain: valid recovery input is not the same as eventual recovery

**Class:** unexecuted candidate liveness-premise ambiguity in F, not a safety counterexample and not a statement about the reduced executed model.

**Smallest literal lasso.** From full-model Init:

1. `Crash` sets Crashed and RecoveryNeeded true and empties queues (F:197)
2. `Enqueue(c)` appends one valid finite command while still crashed; its listed guard is only queue length<2 and finite command domain (F:185)
3. Stutter forever from the resulting one-command queue state

This uses one command identity, zero committed events, one queue slot, no effect and no exhausted bound. At the stable suffix there are no further crashes, input arrivals or invalidating control commands; event capacity is plentiful and an exact valid recovery input can exist. DecodeHead is disabled by Crashed/RecoveryNeeded (F:186); other listed fair processing actions have no enabled pending work or replay. Recover is enabled (F:198) but **not among the weakly fair actions** listed at F:243. The lasso therefore satisfies those listed fairness formulas under a literal reading while the queued command never receives a receipt.

**Conforming rival.** If “a recovery input is valid” means the stable suffix starts only after successful Recover and healthy replay, the lasso is outside the intended premise. State that temporal/initial condition explicitly. Another conforming diagnostic adds eventual recovery and valid complete replay as environment premises, or explicitly approved fairness for recovery. Neither premise should be smuggled into the safety model or claimed for an unavailable disk/provider.

**Decisive later local test.** Transcribe both interpretations independently and check this two-action lasso before expensive exploration. In the healthy-suffix interpretation, prove that the premise actually excludes `Crashed ∨ RecoveryNeeded`; in a recovery-progress interpretation, state exactly what forces Recover/healthy replay. Include a queue-drain positive control under those premises.

**Does not prove:** a safety violation, a runtime hang, provider liveness, or that no fair complete formalization can satisfy LiveDrain. It identifies one short discriminating obligation in prose awaiting transcription.

## Negative findings and residual limits

- **Unknown-effect coverage is absent from the simplified transition system.** K:65 initializes effect None; its complete updates at K:177,194,203,212,220 write None, Prepared, InFlight, Succeeded or KnownNoEffect, never Unknown. Unknown is present in TypeOK and guard sets only. Enlarging IDs/events cannot produce an Unknown observation without adding semantics. This does not negate the existing InFlight witness, and it is not a failure of the full candidate, which explicitly models Unknown outcomes (F:170–171).
- **No new stale-authority runtime witness is claimed.** K's own header explicitly excludes principals and authority-dimension predicates; many missing fences there are admitted abstraction gaps. The full candidate rechecks snapshot/writer at commit and captured fences at Dispatch (F:189–195). Static reading did not establish a new trace bypassing those complete guards. A receiver implementation/refinement and independent observations remain necessary.
- **The models do not establish bounded wall-clock Stop.** Pure safety, finite event caps and absence of fairness cannot by themselves promise a response time under saturation or disconnected receivers. D-022 still needs the broker/receiver and process-ownership joins already specified in the main handoff. No speculative new Stop race is asserted here.
- **No resource-exhaustion safety conclusion follows from the formal cap.** In K, all successful actions consume a fresh ID/event. Four IDs truncate the model before many interactions; reaching the cap is not production overload or successful task completion. In F the event cap instead yields an explicit out-of-scope boundary, and its diagnostic liveness premises must leave sufficient capacity.

## Recommended next review order

1. Independently reread and reproduce/refute the one-command reservation arithmetic candidate
2. Decide and test epoch-zero/nonmonotone Pause semantics without modifying the frozen positive oracle silently
3. Record positive attempt-2 completion scope and M31's exact structural exposure argument before raising bounds
4. Clarify LiveDrain's healthy/recovery premise before claiming liveness

Any later execution requires its own exact target/profile, independent inputs/oracles and authorization. Retain refusals that reveal an unrelated guard as inconclusive for the intended test. Do not update historical receipts, rename a different mutation as the old one, or use these unexecuted findings to declare the deterministic kernel frozen.

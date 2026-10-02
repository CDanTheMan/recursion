# FU-03 kernel Session A reconciliation

Date: 2026-10-02
Status: source-documented and locally-observed reconciliation; no checker run, no kill, not acceptance
Sources: `mutants-registry.json`; `RIntegrated.tla`; ds-FU-03 sections 5-6; `gaps/report.md` section 3; `fu03-static-evidence.json`; `fu03-candidate-witness.json`; SK01-SK05.

## Invariant set and independent monitor need

Intended (ds-FU-03 section 5): TypeOK, ChainIntegrity, AtomicAppend, CommandIdempotence, AuthorityScope, LeaseFence, AmendmentFence, PauseSafety, RetrySafety, CancelNoResurrection, EffectSafety, VerifierSafety, ReplayDeterminism, ReplayFailClosed, ProjectionParity, FlowBound, NoBlindEffectReplay.

TypeOK is structural (not the decoder); FlowBound must count reservations. The other 15 need distinct state or latched boundary evidence (source-documented): ChainIntegrity an independent digest preimage; AtomicAppend latched pre/post log/state/receipts/outbox; CommandIdempotence a ledger; AuthorityScope and fences command plus admission/commit/dispatch context; PauseSafety pause ordinals plus dispatch; RetrySafety reconstructed task/timer/effect; CancelNoResurrection monotone history; EffectSafety and NoBlindEffectReplay durable outbox, an Issued sequence and recovery latch; VerifierSafety original identities; ReplayDeterminism and ReplayFailClosed separate cursor/state and reference; ProjectionParity a separate projector. The reduced model supplies none (`RIntegrated.tla:8-11`).

## Registry-versus-code mismatches

**M02.** Registry: delete previous-digest equality in Reduce validation. Battery: set `Event` prev to `GENESIS` (`mutants.py:26-28`). Chosen: predecessor integrity is a validation obligation (ChainIntegrity/ReplayFailClosed); a wrong-predecessor event with recomputed self-digest distinguishes it (ds section 6; row 66). The battery edit corrupts construction, is caught trivially, and is an analogue only.

**M03.** Registry: weaken `ordinal = old+1` to `>=`. Battery: `ordinal + 2` (`mutants.py:29-30`). Chosen: keep construction `+1` and weaken acceptance to `>=`; only then does a gap 1 to 3 test ChainIntegrity. The +2 variant is killed by TypeOK at 2 states, i.e. ill-typing, not accepted-gap. The row needs a separate replay/Reduce ordinal check.

**M25.** Registry: recovery maps InFlight/Unknown to Prepared and requeues the token. Battery: `RetryEffectOK == TRUE` (`mutants.py:37-39`). Chosen: split the faults. NoBlindEffectReplay forbids both recovery/replay manufacturing a permit over unresolved uncertainty and retry without reconciliation proving KnownNoEffect. Registry M25 needs a `Recover`/replay action the model lacks; the battery edit is a retry-guard fault adjacent to M20. The recorded M25 classification matches neither.

## SK03 and SK04 reconciliation

SK03 (inferred): `Submit`/`SubmitFail` require `attempt = 1` (`RIntegrated.tla:130,139`), no action decreases attempt, and Retry needs at least six fresh IDs. Retry-dependent rows (M19, M20, M21, plus the M25 analogue) are unreachable at four IDs, matching `NEEDS_LARGER_BOUND`. The inferred seven-step effect/timer witness (`fu03-candidate-witness.json`) needs seven IDs/events, is unexecuted, and must be reproduced or refuted before any guard, invariant or M25 change.

SK04 (inferred): reduced `M31` edits `OutboxOK` (`mutants.py:43-45`), but only `MarkDispatch` appends to outbox, `PrepareEffect` requires None, and only `Retry` resets to None (attempt<2). At most two appends occur, so `Len(outbox)=2` never meets `Prepared`; enlarging bounds cannot expose it. The real M31 is an `Enqueue`/Inbox `length<=2` site; the analogue is equivalent-within-bound, not a kill.

## Dispositions

Larger bound: M19, M20, M21. Instantiable: M02, M03, M04, M16, M26 (battery) plus M24, M27. Not implemented (26): M01, M05-M15, M17, M18, M22, M23, M25, M28-M36. Evidence classes: invariant set, mutant definitions and receipt fields are source-documented; reduced bound, sites and outcomes locally observed; SK03/SK04 and reachability labels inferred; no checker or kill result asserted.

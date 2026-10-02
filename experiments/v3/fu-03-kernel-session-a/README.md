# FU-03 Session A — kernel proof/evidence reconciliation

Status: **diagnostic / reconciliation**, not the integrated acceptance gate and not a kernel
freeze. Evidence classes: specification = source-documented; runs = locally observed; reachability
and setup qualifications = inferred; unrun = unknown. Authorized locally by the Owner on
2026-10-02.

Session A answers the packet's Stage A: reconcile the intended kernel invariants and mutation
definitions, build an **independent** oracle, resolve the fixture setup qualification, and classify
the 36 mutants.

## Deliverables

| Path | What |
|---|---|
| `mutants-registry.json` | all 36 ds-FU-03 mutants with exact semantic edit, model site, expected invariant, reachability and disposition |
| `RECONCILIATION.md` | invariant set + independent-monitor needs; M02/M03/M25 registry-vs-code resolution; SK03/SK04 |
| `FIXTURE-QUALIFICATION.md` | the `CORR-M1A`/`GOAL-M1A` setup qualification; producer diagnostics vs valid controls |
| `oracle/` | independently authored Python reference oracle (`RefState`/`RefValid`/`RefProject`), trace-validity bridge, 51-vector corpus, gate |
| `model/` | enlarged TLA+/TLC model (`RBig` unfixed, `RFixed` reconciled), mutant battery, receipts, gate |

## Results

- **Packet witness confirmed.** On the enlarged, *unfixed* `RBig` model TLC reaches the 7-step
  witness and **violates `NoBlindEffectReplay`** (`eff = InFlight`, `retryReady = TRUE`); recorded
  in `model/results/baseline-witness.json`. TLC's shortest trace places `MarkDispatch` last rather
  than the packet's inferred position — the condition is the same, the ordering differs.
- **Reconciled model clean.** `RFixed` adds the guard "the timer cannot set `retryReady` while an
  effect is unresolved"; baseline = exit 0, no error.
- **Battery:** 11 instantiated, **10 KILLED** including **M25** (`NoBlindEffectReplay`);
  **M31** = `NOT_KILLED_WITHIN_BOUND` (a third outbox enqueue is unreachable because `Retry`
  allows at most two attempts → at most two `MarkDispatch` appends, so `Len(outbox) ≤ 2 < Cap`).
  All 36 registry rows carry a disposition (24 `NOT_YET_IMPLEMENTED`, 1 `NEEDS_LARGER_BOUND`). The
  36-row acceptance metric is **not** met — this is a diagnostic subset, not 36/36.
- **Oracle:** 51 language-neutral vectors + the trace bridge pass; `RefState` is deterministic and
  `RefProject` binds aggregate/ordinal/tail.

## Gate

```text
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/check_session_a.py
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/oracle/check_oracle.py
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/model/check_model.py
```

## Recorded assumptions and non-proofs

- The enlarged model is still a **reduced/diagnostic bound**, not the accepted integrated bound.
- `model/` adds a **symmetry-breaking constraint** (`CanonicalIds`: used ids form an initial
  segment). ds-FU-03 requires a separate soundness argument for any state reduction; here the ids
  are interchangeable, so the constraint selects one representative per orbit. This is an
  **assumption**, not a proven equivalence.
- The reference oracle is independently authored but a **bounded bridge**, not a machine-checked
  refinement; and independent authorship does not eliminate a shared specification error.
- No implementation, byte-vector reproduction, Alloy cross-check, or independent verifier rerun
  has occurred. `M03` in the older `experiments/v3/fu-03-formal-model/README.md` remains fixed to
  `TypeOK`; here the registry keeps construction `+1` and tests acceptance weakening.

# FU-03 experiment — reduced-bound kernel model (TLA+/TLC)

Status: **first cut / diagnostic run.** Evidence class: model = inference/design; run output =
locally observed. This is **not** the integrated-bound acceptance gate and **not** a kernel freeze.

Source specification: `docs/v3/research-lane/followups-20261002/raw/ds-FU-03-formal-model-vectors.md`
(candidate `CAND-RCV1-20261001`). Prompt: `docs/v3/prompts/followups-20261001/FU-03-formal-model-and-conformance-vectors.md`.

## What ran

| Item | Value |
|---|---|
| Checker | TLC 2.19 (tla2tools.jar v1.7.4) |
| JAR SHA-256 | `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88` |
| Java | Temurin 21.0.12.1 (recorded per run in `results/summary.json`) |
| Baseline `RKernel` | 727 states generated, 727 distinct, **no error** (exit 0) |
| Mutant `M02 CHAIN_PREV_DELETE` | `ChainIntegrity` violated at the first divergence (2nd event), 20 states (exit 12) → **KILLED** |

Raw output: `results/RKernel.out`, `results/RMutant.out`, `results/summary.json`.

## Reduced bound (deliberate)

`CmdIds = 1..3`, `MaxEvents = 6`, two workers, one aggregate/task/effect. The integrated bound
(1 aggregate, 2 workers, 3 lease epochs, 2 goal/plan epochs, queue capacity 2, up to 20 committed
events, command ids 1..20) is **not** run here. Per `ds-FU-03`, a reduced bound has a distinct
configuration identity and cannot satisfy the integrated gate; this run is diagnostic only.

## Modelled

- canonical event log with ordinal and predecessor chain (symbolic injective `DigestOf`);
- atomic single-event append — one event, one receipt, one order entry per command;
- command receipts with idempotent command ids;
- `GrantLease`, `RevokeLease`, `AdvanceGoal`, `AmendPlan`, `Pause`, `Resume`, `Start`, `Submit`;
- invariants `TypeOK`, `ChainIntegrity`, `OrdinalConsistent`, `NoDuplicateIds`.

## Not modelled

`derive_work_packet`; effect dispatch/outbox; independent reference and replay/projection
monitors; the other 35 mutants; RCV1 CBOR byte vectors; the Alloy cross-check; fairness/liveness.
The model has no independent monitor, so it deliberately does **not** claim to catch shared
reducer defects.

## Gate

```text
python -X utf8 -B experiments/v3/fu-03-formal-model/run_tlc.py
python -X utf8 -B experiments/v3/fu-03-formal-model/check_fu03.py
```

`run_tlc.py` refuses to run if the pinned JAR digest changes.

## What this does not prove

No integrated bound, no 36/36 mutant coverage, no byte-vector reproduction, no implementation,
no kernel freeze. One reachable mutant site was killed; that is not coverage. A passing finite
baseline is not evidence of coverage.

## Increment 2 — `RIntegrated` + mutant battery (reduced bound)

`RIntegrated.tla` extends the model with effect/outbox/dispatch/observe/reconcile, retry/timer,
verifier, cancel, lease epochs and guard indirection so ds-FU-03 mutants are one-site edits.
Baseline `RIntegrated`: **38,837 states generated, 34,625 distinct, no error**.

`mutants.py` generates each mutant as exactly one textual semantic edit (refusing non-unique
sites), renames the module, runs TLC, and writes `results/mutants.json` plus a receipt per row.

| Mutant | Name | Disposition | Violated |
|---|---|---|---|
| M02 | CHAIN_PREV_DELETE | KILLED | ChainIntegrity |
| M03 | CHAIN_ORDINAL_WEAKEN | KILLED | TypeOK |
| M04 | COMMAND_DEDUP_DELETE | KILLED | NoDuplicateIds |
| M16 | PAUSE_GUARD_DELETE | KILLED | PauseNoProgress |
| M26 | VERIFIER_SELF_ALLOW | KILLED | VerifierSafety |
| M25 | BLIND_EFFECT_REPLAY | NOT_KILLED_WITHIN_BOUND | — |
| M31 | FLOW_OFF_BY_ONE | NOT_KILLED_WITHIN_BOUND | — |

**5/7 instantiated mutants killed.** M25/M31 are recorded as not-killed within this bound
(reachability/equivalence), not as coverage. This is a **reduced bound** (`CmdIds = 1..4`,
`MaxEvents = 6`), so it is not the 36/36 acceptance metric; the remaining 29 ds-FU-03 rows are
not yet instantiated and require the integrated model (independent reference/replay monitors,
packet derivation, authority dimensions).

> **Erratum (2026-10-02 overnight audit).** (a) M03 is killed by `TypeOK`, not `ChainIntegrity`.
> (b) The 4-command-ID bound cannot exceed four accepted transitions, so 5/7 is emphatically
> **not 5/36**. (c) M25/M31 are `NOT_KILLED_WITHIN_BOUND` and must not be read as equivalence or
> reachability proofs. (d) The proposed 7-step `NoBlindEffectReplay` witness in the packet is
> source-level inference **outside** the executed bound, and `SK03` reports that second-attempt
> completion is unreachable (both result guards require `attempt = 1`). See
> `docs/v3/research-lane/overnight-20261002/gaps/`.

Battery gate: `python -X utf8 -B experiments/v3/fu-03-formal-model/check_fu03_mutants.py`.

## Next increments (dependency-ordered)

1. Raise constants to the integrated bound and add the independent reference monitor (`RefState`).
2. Add packet/effect/outbox and replay/projection invariants with the remaining monitor state.
3. Instantiate all 36 mutants with reachability, equivalence/unreachable justification and kill
   receipts (`ds-FU-03` section 6).
4. Build the RCV1 deterministic-CBOR vector corpus and the two-stack differential harness.
5. Independent verifier reruns the exact candidate; implementer PASS is not acceptance.

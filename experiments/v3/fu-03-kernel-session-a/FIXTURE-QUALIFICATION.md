# FU-03 Session A fixture qualification

Date: 2026-10-02
Status: source-observed and inferred setup qualification; no runtime execution, no conformance verdict
Sources: `SEMANTIC-GUARD-COVERAGE.md` SG01-SG08 and shared-setup section; `SUPPLEMENTAL-KERNEL-AUDIT.md` SK02 and post-delivery clarification; `scripts/v3/planning/replay/kernel.py:282-290`.

## CORR-M1A vs GOAL-M1A mismatch

`kernel.py:282-290` (`_domain_record`) hardcodes `"correlation_id": "CORR-M1A"`, but the wire profile requires a derived WorkPacket's `correlation_id` to equal its GoalSpec ID (SG citation W:583-587, W:590). Stored packet events bind `GOAL-M1A` while carrying `CORR-M1A` (source-observed, SG shared-setup: F-M1A-001/005, all F-M1A-006 cases, F-M1A-011/014/016). This is a setup inconsistency, not an executed failure: tests on those prefixes are not whole-contract valid, so an early digest or packet refusal is inconclusive for the intended guard. Resealing digests cannot repair it because the constructor still emits `CORR-M1A`.

## F005 effect mismatch

In `F-M1A-005.json` case `amend`, `initial_events[3]` binds task `TASK-M1A-A` with `effect_keys=[]` and digest `0b5bed6c...01ba2`, while packet `PACKET-b4eb25dd...f5b0` binds that task digest but carries `[EFFECT-SYNTHETIC]` (SG03). The mechanism is `kernel.py:327`, copying `goal.payload.allowed_effect_keys` rather than the task's narrowed fields. This is observed fixture data, not observed execution; positive-oracle equality alone preserves the mismatch.

## Producer diagnostics versus valid controls

Producer diagnostics (not whole-contract-valid seeds or positive controls): SK02's stored F-M1A-014 seven-command prefix (epoch zero, CORR-M1A limited); SG06's F-M1A-005 amendment prefix and SG03's F-M1A-005 (the explicit effect mismatch); and the packet-dependent SG01/SG02 (F-M1A-006), SG04 (F-M1A-001), SG05 (F-M1A-011), SG06 (F-M1A-005), SG08 (F-M1A-001) prefixes, diagnostic against unchanged historical bytes including nominal positive controls.

SK01's five-command reservation prefix precedes packet creation, unaffected on the correlation-ID axis only, not blanket-certified.

Valid controls: no historical prefix qualifies. A fixture is whole-contract-valid only if an independent oracle validates its entire setup prefix against the written contract, not the target implementation or stored digests: all record/candidate/command digests and matching synthetic attestations recomputed; packet `correlation_id` equal to the GoalSpec ID; packet effects equal to the task's fields (task-to-goal intersection, never a widened parent); and all reference/digest/expected-state dependencies revalidated end to end. The negative must differ from an otherwise-identical valid control in exactly one field, refusals must be atomic, and frozen bytes preserved. Until then, a refusal from an earlier setup defect is inconclusive.

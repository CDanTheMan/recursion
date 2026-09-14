# Sol: implement the v3 recovery reservation ledger experiment

Parent: goal-recursion-v2-execution-fabric. Apply COMMON.md. Suggested independent reviewer: Astra. This product assignment can run alongside the external service work and does not require live providers or the old scientific campaign.

Read accepted OR-032, ARCHITECTURE.md's Relative recovery ledger section, STATE.md's uncertain-effect posture, and the external-20260914 recovery calculator/review. The calculator is an arithmetic component only. Build the missing inert event/replay contract using integer counters in explicitly declared units and quanta; using Python as an experimental vehicle does not select the product implementation language or store.

For each explicit task/goal/unit/window binding, freeze pre-shutdown verified normal use N and configured exact fraction p/q, with B=floor(p*N/q). Model cumulative committed recovery C and outstanding reservations R. Admit credible upper-bound x only when C+R+x<=B and every parent/pool/resource component ceiling permits it. No unit conversion, floating-point percentages, universal fraction or inferred allowance identity.

Require idempotent actual charging, release of only reconciled unused reservation, duplicate/conflicting-event handling, and unknown reservation retention. Restart, repeated recovery and provider-window reset do not reset C or R. Recovery spending cannot enlarge N; only separately verified additional normal use can change a later boundary. Unknown prior use or counter-reset identity blocks new consumption. Keep deterministic observation/replay available without consumption admission.

Allowed new paths only:
- experiments/v3/recovery-ledger-20260914/ledger.py
- experiments/v3/recovery-ledger-20260914/test_ledger.py
- experiments/v3/recovery-ledger-20260914/check.py
- docs/v3/construction/recovery-ledger-20260914/SPEC.md
- docs/v3/construction/recovery-ledger-20260914/PROGRESS.md

NEW acceptance commands to implement:

```text
python -X utf8 -B experiments/v3/recovery-ledger-20260914/test_ledger.py
python -X utf8 -B experiments/v3/recovery-ledger-20260914/check.py --candidate FULL_SHA
```

Freeze literal outcomes before implementation. Required cases: floor a non-integral allowance; reserve and partially settle; two competing reservations; unknown effect survives serialize/reopen; duplicate settlement charges once; conflicting duplicate refuses; cumulative retries respect cap; provider reset and daemon restart preserve C/R; recovery cost cannot enlarge N; verified additional normal work is separately attributed; unknown baseline/window blocks admission; bool/negative/invalid fraction/quantum refuses; componentwise parent/pool caps; two unlike units never combine. Positive authorized reservation/settlement must work, so blanket refusal cannot pass.

An independent model or literal audit checks every selected event prefix rather than deriving expected results from the implementation. Include controls that erase R on restart, erase C on quota reset, charge duplicate settlement, use a ceiling without flooring, count recovery as normal use and mix units. The check must reject missing controls, skipped cases and changed candidate/source. Preserve original failed gates.

Inert construction/test budget: zero provider calls, at most 1,024 declared event sequences of at most 32 events each,60 seconds per gate,32 MiB artifacts; no OS process crashes, services or live canonical state. Serialization/replay is not physical durability. A real crash/persistence successor needs its own packet.

Done means the new experiment's exact candidate passes literal/replay/mutation gates and independent review. Do not use the experiment to admit real consumption or represent it as the entire v3 kernel. Leave existing arithmetic fixtures, product specs, schemas and prior experiments unchanged.

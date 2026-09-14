# Recovery reservation-ledger progress

## Binding

- Date: 2026-09-14
- Parent: `goal-recursion-v2-execution-fabric`
- Product: Recursion v3
- Branch: `codex/v3-recovery-reservation-ledger-20260914`
- Worktree: `C:\\r3p3`
- `TASK_BASE`: `0c908f6833e715af0eaa01b6f6788120eb577efd`
- Allowed paths: the five new packet-03 paths only
- Provider calls / real consumption: zero

## Inputs read

- `CONTROL_PLANE.md`, `ANCHOR.md`, `AGENTS.md`
- `docs/v3/START-HERE.md`, `docs/v3/PRODUCT.md`
- accepted `OR-021` through `OR-039` rows in `docs/v3/DECISION-REGISTER.md`
- `docs/v3/construction/next-work-20260914/COMMON.md`
- `docs/v3/construction/next-work-20260914/03-sol-recovery-ledger.md`
- `docs/v3/ARCHITECTURE.md`, Relative recovery ledger and recovery mechanics
- `docs/v3/STATE.md`, event/projection and uncertain-effect posture
- prior `experiments/v3/external-20260914/recovery_allowance.py` and tests
- independent prior review at
  `docs/v3/construction/external-rdt-20260914/reviews/recovery-allowance.json`

The prior arithmetic review says that prototype has no integer-quantum floor or explicit
outstanding reservation input and must not admit recovery. This experiment does not modify
or import it.

## Source preservation before implementation

Command:

```text
python -X utf8 -B docs/v3/construction/next-work-20260914/check_handoff.py
```

Result: exit 0, `HANDOFF_SOURCE_PASS`, candidate
`0c908f6833e715af0eaa01b6f6788120eb577efd`, 49 unchanged top-level v3
specifications, zero provider calls, no scientific execution or service activation.

## Frozen-before-implementation state

`SPEC.md` and `test_ledger.py` were authored before `ledger.py`. The literal prefix table,
required case names and six mutation-control names are input expectations, not values
computed from the implementation.

## Results

Intentional pre-implementation red gate, run after freezing `SPEC.md` and
`test_ledger.py` but before creating `ledger.py`:

```text
python -X utf8 -B experiments/v3/recovery-ledger-20260914/test_ledger.py
exit 1
ModuleNotFoundError: No module named 'ledger'
```

This is the expected missing-implementation failure, not a passing result. Implementation,
exact-candidate gates and independent Astra review remain pending. This failed attempt will
not be deleted or relabeled after a later pass.

## Limits and negative evidence

- Inert Python event/replay prototype only; no product language or store selected.
- No provider, service, worker, canonical-state, publication or merge action.
- Serialization/reopen is modeled replay, not physical crash durability.
- No unit conversion, provider counter precision, external-effect reconciliation or real
  consumption is claimed.

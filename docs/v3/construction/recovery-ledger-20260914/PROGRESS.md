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

First implementation run:

```text
python -X utf8 -B experiments/v3/recovery-ledger-20260914/test_ledger.py
exit 1; 14 errors
TypeError: _same_binding() missing 1 required positional argument: 'name'
```

The binding validator was repaired by supplying a stable default diagnostic label. The next
run passed all 16 test methods, 15 required behavior cases, 21 frozen prefixes and six
mutation controls.

First committed candidate: `0b8f20d6465eea89d47db4b28886747f052627b6`.

- Handoff source check: exit 0, `HANDOFF_SOURCE_PASS`, 49 unchanged top-level specs.
- Test command: exit 0, `RECOVERY_LEDGER_TEST_PASS`.
- Exact-candidate check: exit 1. `git diff --check` found a new blank line at EOF in
  `SPEC.md` and `check.py`.

That candidate is retained as failed. The trailing blank lines were removed; no oracle,
case or acceptance requirement was weakened.

Second committed candidate: `0a9be03314d11f3208b9db6bf95f6abbe40f2ab5`.

- Handoff source check: exit 0, `HANDOFF_SOURCE_PASS`, 49 unchanged top-level specs.
- Test command: exit 0, 16 methods / 15 cases / 21 prefixes / six controls.
- Exact-candidate gate: exit 0, `RECOVERY_LEDGER_GATE_PASS`, 13 input bindings and
  73,389 artifact bytes.

Independent Astra review reran all three commands successfully on that clean exact
candidate but returned `repair`. Its in-memory counterexamples found:

- a second root or successor boundary reset cumulative `C/R` and reset uncertainty;
- a reservation could omit configured parent/pool/resource components;
- a semantic duplicate under a new event id left that id available for conflicting reuse;
- disabling parent/pool guards survived the original tests, and the six controls changed
  projected output rather than faulty transition behavior.

Remediation keeps one cumulative account per task/goal/unit/quantum lineage, makes only the
current successor admissible, carries `C/R` and unknown identity across later boundaries,
and rejects a second root. Each boundary now freezes the complete required component-id
inventory. Semantic duplicate deliveries retain their new event ids in serialized evidence.
Parent, pool and resource each have a decisive exhaustion probe, and both the test program
and exact-candidate gate run independent faulty-transition subclasses for all six required
mutations. The original reviewed candidate and `repair` verdict remain recorded above.

Third committed candidate: `e8b78b22a8c9cc88f49fb379066c446a23257c11`.

- Handoff source check: exit 0, `HANDOFF_SOURCE_PASS`.
- Test command: exit 0, all 16 methods and required inventories.
- Exact-candidate gate: exit 0, three component guards, six behavioral mutations,
  21 prefixes, 13 source bindings and 92,952 artifact bytes.

Astra confirmed the four prior counterexamples were repaired, including settlement of an old
reservation into the current cumulative account and reopen preservation. Its fresh review
still returned `repair`: one account-wide reset blocker did not retain reset identity. A
reconciliation against old window W1 could clear newer unknown reset W2.

The second remediation gives every reset an explicit `reset_id` and exact boundary/window
scope. Unknown reset records remain independently outstanding; a reconciliation clears only
the matching id and scope, conflicting scope reuse refuses, and observation lists unresolved
reset bindings. The seven-event W1/W2 counterexample is now a positive refusal check in both
the unit program and independent gate. Same-unit component claims also cannot understate the
boundary upper bound or settled actual.

## Limits and negative evidence

- Inert Python event/replay prototype only; no product language or store selected.
- No provider, service, worker, canonical-state, publication or merge action.
- Serialization/reopen is modeled replay, not physical crash durability.
- No unit conversion, provider counter precision, external-effect reconciliation or real
  consumption is claimed.

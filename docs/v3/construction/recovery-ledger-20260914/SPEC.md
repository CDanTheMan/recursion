# Recovery reservation-ledger experiment

Status: inert construction contract. Parent: `goal-recursion-v2-execution-fabric`.
Product target: Recursion v3. This experiment implements no service, provider call,
canonical writer, physical store, or crash-durability claim.

## Binding and arithmetic

Each recovery boundary is identified by `boundary_id` and carries a complete literal
binding:

- `task_id` and `goal_id`;
- `unit` and positive integer `quantum`;
- `window_id`, or `null` only to preserve an explicitly unknown window;
- verified pre-shutdown normal-use count `N`, or `null` only to preserve an explicitly
  unknown baseline;
- an operator-configured exact fraction `p/q`, with integer `0 <= p <= q` and `q > 0`.

All amounts are non-negative Python `int` values measured in counts of the declared
quantum. Booleans are not integers at this boundary. Floats, conversion, inferred
window identity, implicit percentages and a default fraction are refused.

For a known binding, the frozen recovery ceiling is:

```text
B = floor(p * N / q)
```

For each boundary, replay projects cumulative committed recovery `C` and the sum of
outstanding credible-upper-bound reservations `R`. A reservation of `x > 0` is admitted
only when `C + R + x <= B`. Unknown baseline, unknown/reset window identity, or exhausted
headroom refuses new reservations without disabling deterministic replay and observation.

## Componentwise limits

Parent, pool and resource caps are configured as separate components. Each component has
its own `component_id`, kind, scope, unit, quantum, window, exact ceiling, verified prior
use and identity status. A reservation names every component claim explicitly, including
unit, quantum and window. Admission independently requires:

```text
used_component + C_component + R_component + x_component <= ceiling_component
```

No component amount is converted or summed with another component. A claim whose literal
unit, quantum or window differs from its configured component is refused. Two recovery
boundaries with unlike units remain distinct even when their integer counts happen to be
equal.

## Events and replay

The accepted event types are:

- `boundary_frozen` — establishes the immutable binding, `N`, fraction and derived `B`;
- `cap_configured` — establishes one immutable parent/pool/resource component;
- `reservation_created` — admits a positive credible upper bound under the boundary and
  all named components;
- `effect_unknown` — records ambiguity and retains the full reservation;
- `reservation_settled` — after reconciliation, charges actual amounts once and releases
  only the verified unused remainder;
- `normal_use_verified` — separately attributes additional normal work for a later
  boundary and does not change the current `N` or `B`;
- `provider_counter_reset` — records a reconciled or unknown provider reset without
  clearing `C` or `R`; unknown identity blocks later admission;
- `process_restarted` — an audit event with no counter-reset semantics.

Every event has a non-empty `event_id`. Exact duplicate events are replay no-ops;
different content under an existing event id is a conflict. Reservation, settlement and
normal-use attribution identities are independently idempotent. An identical settlement
identity charges once even if delivery uses a new event id; changed actuals or bindings
under that identity conflict. Once reconciled, a reservation cannot be settled again under
a new identity.

Serialization is canonical UTF-8 JSON containing the accepted event sequence. Reopening
replays that sequence from zero and must reproduce the projection. Serialization does not
claim atomic writes, fsync, process-crash behavior, corruption recovery or physical
durability.

## Later boundaries and normal work

Recovery charges never change `N`. `normal_use_verified` records an amount and source id
against one boundary. A later `boundary_frozen` may cite those source ids and must declare
exactly `N_previous + sum(cited additions)` with the same task, goal, unit and quantum.
The later window is still supplied literally. Each attribution may be consumed by at most
one successor boundary.

## Frozen literal audit

`test_ledger.py` freezes literal outcomes before `ledger.py` exists. Its selected sequences
audit every prefix for:

1. non-integral floor (`N=10`, `p/q=1/3`, `B=3`);
2. reserve eight and reconcile actual three (`C=3`, `R=0`, `B=10`);
3. unknown effect across provider reset, serialize/reopen and process restart;
4. separately attributed additional normal work creating a later `N=150`, `B=15`;
5. simultaneous parent, pool and resource component ceilings;
6. independent token and currency-minor-unit boundaries.

The test inventory also fixes positive settlement, competing reservations, cumulative
retries, duplicate/conflicting delivery, unknown baseline/window refusal, invalid numeric
inputs, and component binding refusal. The final gate independently requires the full case
inventory and all selected prefixes.

Six required mutation controls alter otherwise valid projected outcomes: erase `R` at
restart, erase `C` at provider reset, charge a duplicate settlement, use a mathematical
ceiling instead of floor, add recovery cost to `N`, and combine unlike units. Every altered
outcome must disagree with its frozen literal expectation.

## Acceptance and limits

```text
python -X utf8 -B experiments/v3/recovery-ledger-20260914/test_ledger.py
python -X utf8 -B experiments/v3/recovery-ledger-20260914/check.py --candidate FULL_SHA
```

The gate binds the exact candidate, base commit, clean checkout, allowed paths, required
case/prefix/control inventory, source preservation and a fresh subprocess test result. It
allows at most 1,024 declared event sequences, 32 events per sequence, 60 seconds per gate,
32 MiB of experiment artifacts and zero provider calls.

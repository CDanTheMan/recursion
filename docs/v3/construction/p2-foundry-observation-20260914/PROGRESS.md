# P2 foundry observation progress

## Binding

- Date: 2026-09-14
- Parent: `goal-recursion-v2-execution-fabric`
- Product target: Recursion v3
- Branch: `codex/v3-p2-foundry-observation-20260914`
- Worktree: `C:\\r3fo`
- `TASK_BASE`: `e627cd93bac473094bc99e8fa29c8d62bae526a2`
- Allowed changes: the four new files in this packet only
- Providers, inference, schedulers, workers and service activation: zero

## Inputs read

- `CONTROL_PLANE.md`, then `ANCHOR.md`, `AGENTS.md` and `docs/v3/START-HERE.md`
- `docs/v3/construction/integration-20260914/NEXT.md` and `README.md`
- `docs/v3/construction/next-work-20260914/COMMON.md`
- `tools/construction_swarm/foundry.py`, especially `report`, `run_one` and run layout
- `tools/construction_swarm/ledger.py`, `runner.py`, `contracts.py`
- `tools/construction_swarm/p2_access.py` `AccessService`, adapter response, artifact,
  grant and `serve` interfaces, plus the existing P2 tests

The adapter contract pins the five exact dependency blobs from `TASK_BASE`. The foundry
ledger is observation evidence, not a second canonical Hermes registry. A returned worker
filing is not independently accepted unless the existing ledger has both the accepted job
state and matching `head-decision` event.

## Source preservation before implementation

```text
python -X utf8 -B docs/v3/construction/next-work-20260914/check_handoff.py
```

Exit 0 at exact `TASK_BASE`: `HANDOFF_SOURCE_PASS`, 49 unchanged v3 top-level
specifications, three packets, zero provider calls, no scientific execution or service
activation.

## Frozen acceptance state

`SPEC.md` and the focused acceptance test were written before the adapter. The required
facts, refusal cases, source/blob pins and input-byte invariance checks are frozen. The
first focused run is intentionally expected to fail because the adapter module does not
yet exist; that evidence will remain recorded after implementation.

## Results

Intentional pre-implementation red gate after freezing the contract and tests:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_foundry_observation
exit 1
ModuleNotFoundError: No module named 'tools.construction_swarm.p2_foundry_observation'
```

This is retained missing-implementation evidence, not a passing result. Implementation,
regressions, exact scope gate and independent Astra review remain pending.

## Limits and negative evidence

- Temporary fixture bytes are capped below 32 MiB; child commands use 15-second timeouts
  and the focused gate has a 120-second ceiling.
- No live completed-run smoke has been performed (`unrun`).
- No canonical state/acceptance integration, product-runtime agent, product store,
  physical lifecycle durability, provider telemetry or real fleet readiness is claimed.
- No production service/fleet activation, provider call, configuration/auth/model/cron/
  autonomy change, publication or merge is authorized.

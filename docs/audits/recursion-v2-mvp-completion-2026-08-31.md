# Recursion v2 MVP — source-only completion

Date: 2026-08-31
Status: source gate passed; review publication pending

## Exact source

- Authorized baseline: `907e66cc9ba6ee45256615f2726fa03a3315e9ea`
- Accepted orchestration/provenance candidate: `4d9cc06c3265b401184cc54cd3580501d6926077`
- Integrated orchestration commit: `2a9e12dc6a8ef677314a047cbedb8b153ddc5790`
- Python 3.11 fabric compatibility: `8d124c71faf55eb49641a423bfa426416f234024`
- Independently reviewed adapter/kernel compatibility: `d78a967daef886089b38b8edf25fa33e19af83a4`
- Temporary diagnostic `2175561a2fc3c17e88193aab8d6004fa47e42f73` is not in the branch history.

## Acceptance evidence

The implementation-head command `python3 -u scripts/tests/recursion-v2-mvp.test.py`
returned `recursion-v2-mvp.test: ALL PASS`. The gate executes these source-only checks:

| Gate | Result |
|---|---:|
| MVP contracts | 15 passed |
| task-packet kernel | 25 passed |
| provider adapters | 54 passed |
| bounded orchestration | 22 passed |
| Telegram/control surface and watchdog | 17 passed |
| durable execution fabric | 42 passed |
| cumulative v2 contracts | 16 passed |
| cross-engine contract | all checks passed |
| Cursor Cloud fake transport | all checks passed |
| completion probes | 3 passed |
| `compileall`, `git diff --check`, clean-run invariant | passed |

The completion probes prove that Codex and Cursor hermetic tasks use the same exact
packet, assignment, budget, grant, receipt, checkpoint, evidence, usage, and duplicate
delivery contract with zero cost. They also inject `ENOSPC`, verify no journal or temporary
state survives the failed write, restart from disk, retry, and confirm the lease is durable.
Independent adversarial review additionally reproduced global/closure authority poisoning:
both fabric and orchestration remained typed reject-only.

No provider, production Telegram transport, credential, live controller, deployment,
restart, PAUSE mutation, on-demand billing, or metered spend was used.

## Chiron and quota

Canonical Chiron `origin/main@7525af525ab538f31c2e5b6f117a83fe8e4ac6d2`
passes its 39-slice ledger validation, TypeScript check, and production source build. The v6
study pilot is not ready: H2 browser smoke is next, B0 requires Lucas, and B10 remains behind
B2, B4, B5, B6, S5, and S6. `npm audit` reported three high-severity dependency findings.
No account quota was consumed; all provider evidence was hermetic or fake transport.

## Remaining human seams

This is not production completion. Lucas still owns the approved publisher enablement and
key, review-branch push, PR/merge, production credentials, Telegram transport, second-box
heartbeat transport/key provisioning, deployment, restart, and any broader autonomy. Python
same-process code is reflectively mutable; the tested graph poisoning fails closed, while a
production boundary still requires process isolation. Live provider and outage behavior must
be validated only after those human-controlled seams are provisioned.

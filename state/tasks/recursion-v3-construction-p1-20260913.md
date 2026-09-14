schema_version: 1
id: recursion-v3-construction-p1-20260913
goal_id: goal-recursion-v2-execution-fabric
project_id: recursion
status: active
product_target: v3

Bounded P1 implementation packet for the continuous WSL construction-service
specification. This implements only the fake-worker, fake-Hermes fenced task/attempt core
needed to exercise S01, S02 and S05 without activating a service.

Exact implementation baseline: `8568b8a4e95171803cf126ce417cdfd775a71eb4`
(`origin/master`, merged 2026-09-13 WSL-autonomy specification).
Requirements source: `docs/v3/construction-swarm/CONTINUOUS-OPERATION.md`, CW-01, CW-02
and CW-05; acceptance contract:
`docs/v3/construction-swarm/continuous-operation-contract.json`, P1/S01/S02/S05.
Parent goal: `goal-recursion-v2-execution-fabric`.

Deliverable: durable local fake-Hermes and fake-worker task/attempt core that proves the
following bounded properties with SQLite-backed test state: exactly-once outbox delivery
across reopen, canonical revision conflict preservation, process-contended leader election
with monotonically fenced effects, reserve-before-launch crash uncertainty with retained
charges, old-fence refusal, transport-bound identity, project/capability enforcement,
idempotency-body conflict, and grant revocation at the launch boundary.

Allowed paths:
- `tools/construction_swarm/p1_core.py`
- `tools/construction_swarm/p1_fixture_worker.py`
- `tools/construction_swarm/test_p1_core.py`
- `state/tasks/recursion-v3-construction-p1-20260913.md`

Non-goals: any live WSL service, Windows lifecycle, sockets/MCP/CLI integration, real
provider, live Hermes integration, live worker or route qualification, spending, task
admission beyond P1's fake boundary, scheduler activation, configuration/auth/cron/autonomy
changes, changes to historical evidence or contracts, publication, merge or push. The fake
transport is a test harness only and is not evidence of live transport qualification.

Acceptance commands, run from this worktree after each checkpoint and on the exact candidate:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p1_core
git diff --check 8568b8a4e95171803cf126ce417cdfd775a71eb4 HEAD
powershell -NoProfile -Command "$changed = git diff --name-only 8568b8a4e95171803cf126ce417cdfd775a71eb4 HEAD; $allowed = 'tools/construction_swarm/p1_core.py','tools/construction_swarm/p1_fixture_worker.py','tools/construction_swarm/test_p1_core.py','state/tasks/recursion-v3-construction-p1-20260913.md'; $bad = $changed | Where-Object { $_ -notin $allowed }; if ($bad) { $bad; exit 1 }"
```

The unittest command must include actual abrupt child-process exit/reopen and independently
started competing-process leader-election cases; thread-only and mock-only evidence does not
meet this packet. Preserve the resulting command output in checkpoint notes below. An
independent reviewer must inspect the exact candidate and rerun the command before this task
may be called complete.

Checkpoint 0 (2026-09-13): packet recorded before implementation. Fresh clean worktree at
`8568b8a4e95171803cf126ce417cdfd775a71eb4`; no service or provider was launched.

Checkpoint 1 (2026-09-13): P1 implementation candidate expanded after independent Luna
adversarial audits identified stale idempotent/fence paths, caller-controlled result revision,
launch-intent crash ambiguity, and missing envelope bindings. The revised fake-only suite ran
seven tests successfully, including abrupt child-process reserve/launch-intent loss and a
synchronized two-process election. No live qualification or activation occurred. Exact
candidate review remains required before this packet can pass.

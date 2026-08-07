---
title: Hermes Project Pilot Phase 6 Handoff
type: handoff
status: ready-for-review
last-verified: 2026-08-07
related:
  - CONTROL_PLANE.md
  - docs/architecture.md
  - docs/delegation-design.md
  - docs/autonomous-loops-architecture-and-roadmap.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
  - docs/plans/hermes-project-pilot-phase5-handoff.md
---
# Hermes project pilot Phase 6 handoff

## Current state

- Phase 5 merge gate passed before authoring: implementation
  `719ca2453f8e1a85f684611b0cd0fe175524992b` and final published handoff tip
  `529d15e6438035b4ed62369459307af8a642fde3` are ancestors of merged
  `origin/master` at `10bca6cfe1df81a4f03592a49868e70f89fd43f3` (PR #26).
- Phase 6 red-control commit: `50d354c758f002ef64db57dc78c549f178b1e00e`.
- Phase 6 core implementation commit: `b00d7debb1c3cabecd3c75d9fc41e19b94d59dff`.
- Phase 6 final implementation OID: `b4b2924664793f4c7b60d507269e2bcdafd7d413`; this adds the
  exit-zero-but-mutating final-gate refusal and its control.
- Local review branch: `review/hermes-phase6-controls` in the clean worktree
  `C:\Users\drfoo\github\recursion-hermes-phase6`.
- Publication state: Lucas separately authorized the branch push after Phase 6 completed. The
  review branch is published; no PR was opened, and nothing was merged or deployed.
- Exact implementation proof: 17/17 baseline; every Phase 1-5 control and positive audit; all 18
  Phase 6 behavioral controls; and the Phase 6 positive architecture audit are green.
- Production remained PAUSE-gated throughout this work and had zero transient worker units at the
  final snapshot. No live pilot or production Phase 1-6 deployment was run by this work.

The exact merge gate, pre-change matrix, red failures, exact-commit green matrix, implementation
OID, and live evidence are appended to
`docs/plans/hermes-project-pilot-phase0-evidence.md`.

## Implemented Phase 6 loop

Phase 6 adds a deterministic per-goal reconciler inside the existing supervised actuator. It is
not another scheduler, state store, publisher, executor, worker launcher, or model-to-shell path.
The only path remains:

```text
canonical truth -> schema-v1 decision -> durable action -> existing actuator
```

Each supervised actuator pass first asks `project-reconcile.py schedule` to observe canonical
project/goal/task/run/git/event/delivery truth and enqueue idempotent `reconcile-goal` decisions.
Those decisions then travel through the same action queue and actuator as every prior phase. The
reconciler advances this bounded lifecycle:

```text
observe -> plan ready work -> capacity admission -> dispatch existing work action
        -> collect -> Phase 5 scope/machine/independent-verifier evidence
        -> pass/retry/block -> unlock dependencies -> exact-commit goal verify -> stop/report
```

The implementation adds:

- compare-and-swap task and goal transitions with append-only transition and recovery events;
- complete recovery projection across canonical task files, live processes, worktrees, local and
  remote refs, events, and delivery records, deduplicated by observed-state digest;
- ready-task admission by dependency order, exact fresh base, configured per-goal concurrency,
  token, cost, wall-clock, task-attempt, retry, failure, publish-attempt, and review-queue budgets;
- reuse of the Phase 5 `work` action, envelopes, human-owned aliases, process evidence, complete
  scope gate, non-vacuous result/gate rules, timeout handling, and distinct exact-OID verifier;
- bounded publication through the existing `publish.sh` boundary and proof of the exact remote
  review ref before a published task can pass;
- an exact candidate goal verification worktree, interruptible acceptance gate, dependency-commit
  ancestry proof, immutable verification evidence, and evidence-required `verifying -> active`
  reopen;
- deterministic terminal states for `achieved`, `blocked`, `abandoned`, `budget-exhausted`, and
  `paused`, with terminal goals closed to new work and repeated achieved ticks dispatching zero;
- PAUSE checks at scheduling, reconciliation, publication, and interruptible goal verification so
  PAUSE prevents new dispatch/gates/publication and cancels an in-flight verification gate.

A model's prose or `done` claim is never a completion signal. Task progress is accepted only from
the linked Phase 5 evidence at one exact commit; a goal becomes achieved only after its independent
goal acceptance evidence passes at the exact final candidate.

## Red-to-green proof

On untouched merged base `10bca6c`, the new control exited `1` with exactly 18 intended failures:
successful exact-commit reconciliation, bounded gate retry, ambiguity deduplication, failure-budget
exhaustion, PAUSE, crash/reboot recovery, stale base, publisher failure, verifier disagreement,
five capacity/budget limits, deterministic terminals, six-source recovery, verifying closure, and
zero post-achievement launch. The red suite was committed separately before implementation.

At exact final implementation OID `b4b2924`, the same 18 cases all passed. The successful-goal case
also proves that a final gate which exits zero after dirtying the detached exact-commit worktree is
recorded as failed and cannot achieve or relaunch the goal. A fresh named Linux clone from a Git
bundle passed the baseline and every historical control/audit. The precise commands and results are
in the Phase 0 evidence file.

## Production boundary and observed drift

The pre-change live snapshot at `2026-08-07T17:15:18Z` found production on `loop/auto` at
`c6332c191501c47a9c9b82c50cb81f82f5678528`, PAUSE present, and zero worker units. The final
read-only snapshot at `2026-08-07T18:18:10Z` found `loop/auto` had independently advanced to
`9c70a860df2a2b68f4359cdbfeb9fdca1c877ad3` (`loop: board 2026-08-07 18:16Z`). That commit descends
from the earlier deployed commit and was not authored, deployed, or invoked by this Phase 6 work.

The final read-only recheck at `2026-08-07T18:46:33Z` found that ref unchanged. PAUSE remained
present before and after the final audit with SHA-256
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`; `hermes-gateway` was active,
`recursion-hermes-gateway` and `recursion-supervisor.timer` were inactive, and zero
`recursion-worker-*` units existed. The audit retained exactly two deployment-gated failures: the
unrestricted/root installed gateway and advisories in installed `aiohttp==3.14.1` and
`cryptography==48.0.1`.

The initial published remote tip was `f8996fe545a7faf59883b1b4d50be8d10a721f1d`, exactly matching
the then-current local tip. Publication did not open a PR, merge, deploy, lift PAUSE, raise live
project concurrency, run a live pilot, or begin Phase 7. Those actions still require separate
authorization from Lucas.

The dirty user-owned `master` remains at `20c1fa77042f3aa9f5d8978352792f3b058bc0d1`; it was not an
authoring or test source and its tracked and untracked changes remain user-owned.

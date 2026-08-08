---
title: Hermes Project Pilot Phase 8 Handoff
type: handoff
status: ready-for-review
last-verified: 2026-08-08
related:
  - CONTROL_PLANE.md
  - docs/architecture.md
  - docs/delegation-design.md
  - docs/autonomous-loops-architecture-and-roadmap.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
  - docs/plans/hermes-project-pilot-phase7-handoff.md
---
# Hermes project pilot Phase 8 handoff

## Current state

- The Phase 7 merge gate passed before Phase 8 authoring. Phase 7 implementation
  `b4d3a30317e7d11f8e31b5e2578eb53aaeb5155c` is an ancestor of merged
  `origin/master` at `7aa6e0f44ffd5145d15c38dfad893ed46389308b` (PR #28), and the Phase 7
  handoff/evidence artifacts are present.
- Phase 8 red-control commit: `234d49b46197b7e120ca96b7efdfdc904ba87ec0`.
- Phase 8 implementation commit: `7d0dc10fcb5914f98353be1f73deb15498e71b7c`.
- Local review branch: `review/hermes-phase8-pilot` in the clean worktree
  `C:\Users\drfoo\github\recursion-hermes-phase8`, based on merged `origin/master`.
- Publication state: Lucas separately authorized a push after local implementation, verification,
  and evidence were complete. The branch was published with initial remote tip
  `a411e1cdcc999c9606f35879d0ad3a1d3d58f438`; no PR was opened, and no merge or deployment occurred.
- Exact Linux proof: 17/17 historical baseline; every Phase 1-7 behavioral control and positive
  audit; all six Phase 8 plan/window/assist controls; the real Linux parallel-capacity control; and
  the Phase 8 positive architecture audit are green at the exact implementation OID.
- No live pilot or soak window has started. Production flags, model routing, concurrency, services,
  notification state, product repositories, and PAUSE were not changed by Phase 8 work.

The exact commands, OIDs, results, live snapshot, GitHub inventory, rollback gates, and raw-log
hashes are appended to `docs/plans/hermes-project-pilot-phase0-evidence.md`.

## Why the previous Chiron plan is not executable

The production Chiron registry still contains the pre-Phase-8 goal
`goal-chiron-learning-shell` and legacy tasks `chiron-001` through `chiron-003`. That state predates
the Hermes plan-synthesis contract and is not a valid autonomous Phase 8 plan. Phase 8 therefore
does not reopen, reinterpret, or silently upgrade it.

A Chiron pilot can begin only from a fresh Lucas instruction that produces a new, schema-complete
plan with new plan, goal, and task identities. The plan must contain:

- a bounded Phase 6 budget and complete Phase 5 worker/verifier task envelopes;
- an acyclic dependency graph, exact allowed paths, and explicit non-goals;
- non-vacuous task and terminal gates;
- review-branch-only publication, with credentials, merge, and deployment excluded; and
- one deterministic stop condition and bounded prose fields.

The proposal is stored at `state/plans/<project>/<plan>.json`. Head Hermes cannot materialize its
goal or tasks until a separate authenticated Lucas instruction names the exact plan ID and SHA-256
digest. Replaying the approval is idempotent. A collision, stale digest, malformed plan, reused
identity, missing field, cycle, vacuous gate, or partial materialization fails closed.

## Implemented Phase 8 path

Phase 8 uses the existing hierarchy and adds no parallel scheduler, executor, publisher, store,
sender, or worker launcher:

```text
Lucas instruction
  -> authenticated intake record
  -> logical project pilot or Head Hermes planning invocation
  -> schema-validated decision
  -> existing durable decision queue
  -> existing conduct-hermes.sh sole actuator
  -> fresh immutable plan proposal
  -> separate Lucas exact-digest approval
  -> Phase 6 goal + Phase 5 task DAG materialization
  -> separate Lucas exact-goal bounded window authorization
  -> scheduler/actuator admission recheck
  -> Phase 5 bounded worker + independent verifier
  -> Phase 6 reconciliation and review-branch publication
  -> Phase 7 outbox -> existing notify.sh -> exact delivery acknowledgement
  -> deterministic terminal closure
```

The implementation provides:

- event-invoked logical GPT project pilots with a project-scoped live brief; `RECURSION_PILOT_MODEL`
  is required and fails closed when no human-owned model alias is configured;
- Head-Hermes-only plan approval, window approval/closure, and assist-answer routing;
- durable pilot windows that are armed while PAUSE is present, activate only on the first unpaused
  scheduler observation, admit exactly one named goal for a bounded duration, and are rechecked at
  scheduler and final worker/action boundaries;
- automatic closure of every open pilot window when PAUSE is observed, so a later resume cannot
  replay stale authority;
- compare-and-swap assist resumption of the same blocked goal and task exactly once, with failed
  actuator actions reopening rather than losing their originating instruction;
- direct pilot notification suppression so Phase 7 remains the only human-visible outbox path;
- global worker capacity through `RECURSION_PILOT_GLOBAL_CONCURRENCY` plus one active worker per
  project, implemented as filtered claims in the existing decision queue and sole actuator;
- PAUSE-safe draining only for inert plan/approval/window/assist state transitions, never worker,
  gate, publication, or delivery work; and
- backup coverage for plans, windows, decisions, actions, goals, tasks, assists, runs, events,
  reports, and delivery state.

The checked-in Chiron and golden-stallion-client pilot records gain only
`"window_required": true`. Their production concurrency remains zero. No model alias or global
concurrency value was configured.

## Red-to-green and exact-commit proof

On untouched merged base `7aa6e0f`, the Phase 8 falsifier overlay reported `0/6 controls passed`.
The red suite was preserved in its own commit before implementation. It covers fresh plan shape,
atomic rejection, exact-digest approval, exact-goal bounded admission, PAUSE revocation, and
same-task assist resumption.

At exact implementation OID `7d0dc10`, those six controls pass. The independent Linux parallel
test also proves two projects overlap when global capacity is two while a second task from either
project remains blocked by per-project capacity one. The complete 17-command Linux matrix ended:

```text
MATRIX_TOTAL=17 MATRIX_FAILED=0
```

Every individual command log ended `RC=0`; `matrix2.err` was empty. The disposable Linux bundle and
archive fixtures were removed after the logs were copied and hashed locally. No test used the live
production tree, transport, credentials, project worktrees, or product repositories.

## Read-only production preflight

The final snapshot at `2026-08-08T17:18:24Z` found:

| Gate | Observed state |
|---|---|
| deployed checkout | `loop/auto` at `87189cd6e43ecc3d91f78881b82fb2186c7b2ebe`; Phase 7 merge and implementation are ancestors |
| tracked production changes after Phase 7 merge | awareness-only board/brief/event/inbox/escalation files |
| untracked production file | `.env.bak.1786014440`; pre-existing/user-owned, not read or changed |
| PAUSE | present, `root:root`, mode `0644`, 189 bytes, SHA-256 `919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db` before and after |
| services | `hermes-gateway=active`; hardened `recursion-hermes-gateway=inactive`; supervisor timer/service inactive |
| workers | zero `recursion-worker-*` units; zero active project-worktree processes |
| delivery state | zero notification events and zero deliveries for all nine registered projects |
| pending execution | no decision/action/run/lease directories and no pending/running decision or action files |
| pilot capacity | Chiron and GSC `concurrency_limit=0`, `max_inflight_workers=0`, publication false |
| runtime routing | `RECURSION_PILOT_MODEL`, `RECURSION_DECIDE_MODEL`, and `RECURSION_PILOT_GLOBAL_CONCURRENCY` unset |
| live Phase 1 audit | return `1` with exactly the two known deployment gates: unrestricted/root gateway and advisories in `aiohttp==3.14.1` plus `cryptography==48.0.1` |
| branch protection | authenticated protection endpoint returned HTTP 403 for every registered repository; none is verifiably protected |
| backup/restore | exact fixture backup/restore and crash recovery green; production script present and PAUSE/lock-gated; no production snapshot/restore drill yet authorized or demonstrated |

The deployed OID differs from the Phase 7 handoff's earlier snapshot because the PAUSE-safe
awareness cadence created board/morning commits after merging `origin/master`. Phase 8 did not
create them. The production `origin` cannot currently authenticate with its default recursion key;
that observation was read-only and was not repaired or bypassed.

The two live Phase 1 findings, unverified default-branch protection, absent production
backup/restore drill, unset pilot model alias, zero configured capacity, and unpublished/unmerged
Phase 8 implementation are deployment and pilot gates, not waivers.

## Santa Clara repository evidence

GitHub reports `NotSkittlz/santa-clara-construction` as a private, unarchived repository with
default branch `main`, size zero, and this account holding admin/push access. Its deploy-key endpoint
contains one verified writable key titled `gs-recursion`, created `2026-08-06T08:00:05Z`.

On `gs-recursion`, `/root/.ssh/santa-clara-construction_deploy` is readable, has ED25519 fingerprint
`SHA256:AioH/xSd+WQNtGNqvSjKLJQwbWf74Dgo5lNOFqyp4lk`, and authenticates to GitHub specifically as
`NotSkittlz/santa-clara-construction`. No key bytes were printed. The remote is empty, and the
project has no topic, goal, or actionable charter, so it correctly remains pending with concurrency
zero. Phase 8 did not clone or activate it.

## Rollback gates for future authorized actions

Every item below is a runbook, not current authorization. Before each action, recapture the exact
deployed OID, PAUSE hash, service state, queue/outbox counts, and a manifest-hashed runtime snapshot
outside the checkout. If the deployed OID moves from the value above, that newly observed OID
becomes the rollback OID only after the same read-only checks pass.

1. **Phase 8 deployment.** Keep PAUSE asserted; quiesce writers; take and verify the runtime
   snapshot; deploy only Lucas-reviewed merged code. On any mismatch, keep/reassert PAUSE, stop the
   supervisor and all worker units, restore the pre-deploy snapshot into staging and verify its
   manifest, then deploy a reviewed inverse commit returning the code to the captured pre-deploy
   OID/tree. Never reset, force-push, or use the dirty local master.
2. **Chiron success window.** PAUSE is removed only after the new plan digest and exact goal/window
   instruction are recorded. Rollback is to restore the same 189-byte PAUSE file and verify its
   SHA-256, observe automatic window closure, terminate/verify zero worker units, leave any review
   branch unmerged, and reconcile the goal to a deterministic stopped state. Restore the pre-window
   runtime snapshot if any chain object is missing or duplicated.
3. **Chiron assist window.** Use a distinct exact-goal window. Rollback is identical, plus prove the
   assist and instruction remain durably correlated and the task has not resumed more than once.
   Never fabricate an answer or create a replacement task.
4. **GSC offline window.** Capture the product HEAD plus hashes of the conformance/native-diff gate,
   tests, fixtures, oracle, baseline, and corpus manifest first. On any hash change or live-game
   dependency, reassert PAUSE, close the window, terminate the worker, leave the review branch
   unmerged, restore runtime state if required, and reject the result. Do not rewrite a baseline to
   make the task pass.
5. **Parallel window.** Authorize exactly two named goals and the reviewed global/per-project
   capacity values for that window only. On overlap, isolation, reporting, or capacity mismatch,
   reassert PAUSE, close both windows, terminate all worker units, verify no queued work or sends,
   and restore the pre-window snapshot before any retry.
6. **Soak fault windows.** Record each gateway restart, host reboot, PAUSE interruption, and
   notification-failure injection as a separately observed sub-window. Each sub-window rolls back
   to PAUSE plus the captured service/configuration state; delivery retry uses only the Phase 7
   outbox and exact transport evidence. Any lost/duplicate action, event, report, or delivery ends
   the soak and prevents promotion.

After every future window: PAUSE must be present with the expected hash, all pilot windows closed,
worker/worktree process counts zero, no unintended sends, and the exact
instruction/plan/goal/task/run/commit/gate/verifier/review/report/delivery chain complete. Partial
evidence is a no-go for the next window.

## Authorization boundary and next action

Lucas approved the Phase 8 implementation plan and the requirement to replace the old Chiron plan
shape. That approval authorized local Phase 8 authoring and read-only preflight. Lucas later
authorized the review-branch push, which is the only remote mutation completed. Neither approval
authorized a PR, merge, production repair, deployment, configuration change, PAUSE removal,
human-visible notification, backup/restore drill, or pilot window.

The next action belongs to Lucas's GitHub review workflow: review and merge the published branch,
then prune it when satisfied. Deployment cannot be proposed as go until the two Phase 1 findings,
branch-protection gate, and production backup/restore demonstration are resolved through reviewed
actions. The first Chiron window additionally requires the merged/deployed Phase 8 code, a
configured human-owned pilot model alias and bounded capacity, a fresh Lucas goal instruction,
exact plan-digest approval, and exact window authorization.

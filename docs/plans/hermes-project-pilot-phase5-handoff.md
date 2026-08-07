---
title: Hermes Project Pilot Phase 5 Handoff
type: handoff
status: ready-for-review
last-verified: 2026-08-07
related:
  - CONTROL_PLANE.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
  - docs/plans/hermes-project-pilot-phase1-handoff.md
  - docs/plans/hermes-project-pilot-phase1-deployment.md
  - docs/plans/hermes-project-pilot-phase2-handoff.md
  - docs/plans/hermes-project-pilot-phase3-handoff.md
  - docs/plans/hermes-project-pilot-phase4-handoff.md
---
# Hermes project pilot Phase 5 handoff

## Current state

- Phase 5 red-control commit: `c5e60eb53508cfe557673522eb4d4334f33b3c6f`.
- Phase 5 implementation commit: `719ca2453f8e1a85f684611b0cd0fe175524992b`.
- Local review branch: `review/hermes-phase5-controls` in the clean worktree
  `C:\Users\drfoo\github\recursion-hermes-phase5`.
- Publication state: local only. The branch was not pushed and no PR was opened.
- Authoring base: merged Phase 4 `origin/master` at
  `2d631c4df36edec96d9d69013f8b8afedb28a79e` (PR #25 merge).
- Phase 4 implementation commit `537749193abcd6e8a9ce0aa9c3a8da73c679b42d` and published
  handoff tip `679b12d3b353f95b418dc1f5a45f79872416dc6f` are ancestors of that base.
- Existing baseline: 17/17 green at the exact Phase 5 implementation commit.
- Phase 1 controls: 8/8 green; positive artifact/sandbox/publication/dependency audit green.
- Phase 2 controls: 6/6 green; positive schema/action-coupling/rotation/backup audit green.
- Phase 3 controls: 6/6 green; positive intake/decision/queue/coupling/supervision audit green.
- Phase 4 controls: 4/4 green; positive metadata/topic/forwarding/bounded-read/verb/registration
  audit green.
- Phase 5 controls: 9/9 green; positive alias/gate/scope/envelope/process/verifier audit green.
- Production: still paused and undeployed on `loop/auto` at
  `c6332c191501c47a9c9b82c50cb81f82f5678528`, with zero transient workers.
- Live Phase 1 audit: exactly two deployment-gated findings remain—the unrestricted/root gateway
  and advisories in the old installed dependency environment.

The exact merge gate, pre-change matrix, nine red failures, exact-commit green matrix,
implementation OID, and final read-only live evidence are appended to
`docs/plans/hermes-project-pilot-phase0-evidence.md`.

## Implemented Phase 5 controls

Phase 5 extends the existing `work` action and proven executor; it does not add a second planner,
dispatcher, state store, publisher, or actuator. Pilot-created tasks remain proposals until the
existing decision/action/actuator path admits a `work` action. The configured pilot concurrency
remains zero, so this implementation does not begin the Phase 6 autonomous reconcile loop.

The implementation adds:

- strict worker envelopes carrying project/goal/task identity, exact base commit, allowed paths,
  non-goals, acceptance, evidence contract, deadline, network policy, ambiguity-stop behavior,
  distinct implementer/verifier aliases, and required-change policy;
- versionless `sonnet-routine`, `opus-complex`, and `opus-review` role aliases whose actual model
  values exist only in human-owned environment mappings; a worker cannot select or rewrite them;
- PID and process-group identity, heartbeat/lease timestamps, deadline, log, usage, result, scope,
  changed-file, machine-gate, and verifier evidence in atomic ignored `state/runs/*.json` records;
- complete scope comparison across `base..HEAD`, staged, unstaged, untracked, renamed, copied, and
  deleted paths, with both rename sides checked and worker commits unable to hide protected or
  out-of-scope mutations;
- fail-closed gate and result rules: empty/`true`/structurally vacuous gates, result-dependent gates,
  worker-modifiable gate programs without declared fingerprints, missing or inconsistent result
  JSON, and no-op output for a required-change task cannot pass;
- supervised deadline handling that terminates the process group, records timeout evidence, clears
  the task lease, blocks the task, and deduplicates the one actionable escalation by run ID;
- candidate commit creation before the machine gate, proof that the gate did not mutate tracked
  candidate state, and a second read-only verifier worktree at that exact candidate OID;
- verifier output limited to its evidence mount, checked for source/HEAD mutation, schema-validated
  against the implementer run and exact OID, and linked back to the machine-gate evidence before a
  task can pass.

## Required controls proved

The Phase 5 falsifier failed nine times on untouched merged base `2d631c4`: committed protected
changes and a committed combined test/fixture/rename/delete/out-of-scope mutation passed; missing
result, required-change no-op, literal `true`, and worker-rewritten gate all passed; a hung worker
finished rather than timing out; no independent exact-commit verifier evidence existed; and a
verifier mutation could not be distinguished from success.

At `719ca245`, the same suite proves the inverse: each scope/result/gate violation terminates as
`escalated` before its gate, the hung worker terminates as `blocked` with lease `0`, a dead recorded
PGID, and one timeout escalation, a clean independent verifier produces a distinct PID/run bound to
the machine-gated OID, and a mutating verifier is rejected while the implementer branch retains its
original bytes.

## Review and publication boundary

No publication was authorized. The branch has not been pushed, no PR exists, and nothing was
merged or deployed. Phase 1's paused deployment runbook remains unexecuted; Phases 2 through 5 are
also undeployed. Keep `/opt/recursion/state/PAUSE` present and treat the two live Phase 1 findings
as deployment gates rather than waived criteria.

The dirty user-owned `master` remains at `20c1fa77042f3aa9f5d8978352792f3b058bc0d1`; it was not an
authoring or test source and none of its tracked or untracked files were changed.

## Phase 6 boundary

Phase 6 is not authorized by this handoff. Do not start the autonomous measurable-goal loop until
Lucas reviews Phase 5, separately authorizes publication, merges it, and the implementation commit
is independently confirmed in current `origin/master`.

Phase 6 owns event-driven observation, capacity admission, dispatch/retry/reconciliation, goal-stop
semantics, and scenario testing across process crash, reboot, PAUSE, stale base, publisher failure,
and verifier disagreement. Phase 5 provides the bounded worker/verifier mechanism only. Do not run
a live pilot, raise project concurrency, lift PAUSE, deploy, merge, push, or open a PR without the
separate authorization applicable to that action.

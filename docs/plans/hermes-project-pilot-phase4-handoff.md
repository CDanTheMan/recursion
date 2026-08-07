---
title: Hermes Project Pilot Phase 4 Handoff
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
---
# Hermes project pilot Phase 4 handoff

## Current state

- Phase 4 implementation commit: `537749193abcd6e8a9ce0aa9c3a8da73c679b42d`.
- Review branch: `review/hermes-phase4-controls` in the clean worktree
  `C:\Users\drfoo\github\recursion-hermes-phase4`.
- Publication state: Lucas authorized a branch-only publication for review on 2026-08-07. The
  branch is published as `origin/review/hermes-phase4-controls`; no PR was authorized or opened.
- Authoring base: merged Phase 3 `origin/master` at
  `f120566a49a8d9a371e8b03d42d7e2aaf13dd7fc` (PR #24 merge).
- Phase 3 implementation commit `06a7422b6b51b9e2db6f7ca3e86b76da3cab2953` and its published
  handoff commit are ancestors of the authoring base; the Phase 3 controls/artifacts are present.
- Existing baseline: 17/17 green at the Phase 4 implementation commit.
- Phase 1 controls: 8/8 green; positive artifact/sandbox/publication/dependency audit green.
- Phase 2 controls: 6/6 green; positive schema/action-coupling/rotation/backup audit green.
- Phase 3 controls: 6/6 green; positive intake/decision/queue/coupling/supervision audit green.
- Phase 4 controls: 4/4 green; positive metadata/topic/forwarding/bounded-read/verb/registration
  audit green.
- Production: still paused and undeployed on `loop/auto` at
  `c6332c191501c47a9c9b82c50cb81f82f5678528`, with both Hermes units inactive and zero transient
  workers.
- Live Phase 1 audit: exactly two deployment-gated findings remain—the old unrestricted/root
  gateway and advisories in its old installed dependency environment.

The exact merge gate, pre-change matrix, four red failures, exact-commit green matrix,
implementation OID, and live PAUSE evidence are appended to
`docs/plans/hermes-project-pilot-phase0-evidence.md`.

## Implemented Phase 4 controls

Phase 4 preserves the file/event architecture and Phase 2/3 queue and actuator. It adds:

- durable project and pilot companion records for every registered project, including topic,
  charter, model alias, concurrency/budget, notification targets, goal source, memory key, and
  worktree namespace;
- one unique logical pilot per active Telegram topic; topic intake records its pilot identity and
  memory namespace, while Head Hermes receives portfolio, policy, cross-project, credential, and
  production requests;
- bounded read APIs for charter/scoped context, live task/run/git status, charter-allowed tracked
  repo text, and project-owned evidence/log tails; status never reads pilot memory;
- Phase 4 verbs for plan proposals, dependency-linked tasks under an approved goal's existing
  gate, worker/verifier requests, block/escalation, and goal-verification requests, all behind the
  existing instruction/decision/action/actuator path;
- two-step pending preparation and activation, with an explicit pending-topic bind and activation
  only after complete charter/gate/pilot metadata, deploy-key-backed remote proof, correct clean
  clone/default branch, and exact remote-head freshness;
- project-pilot runtime requests/runs added to ignored backup/restore coverage.

The configured project-pilot worker concurrency remains zero. The implementation creates only
proposed tasks or durable requests; it does not invoke a model worker, verifier, publisher, merge,
or deployment. Existing active rows received tracked metadata but were not reactivated on the box.

## Review and publication boundary

Lucas authorized committing and pushing the Phase 4 review branch on 2026-08-07. That authorization
does not include opening a PR, merging, deploying, running a live pilot, or changing PAUSE. Phase
1's paused deployment runbook remains unexecuted; Phase 2, Phase 3, and Phase 4 are also undeployed.
Keep `/opt/recursion/state/PAUSE` present and treat the two live Phase 1 findings as deployment
gates rather than waived criteria.

The dirty local `master` remains user-owned at `20c1fa7`; do not use or clean it. Lucas's normal
review path is this clean Phase 4 worktree/branch, followed by his GitHub merge only after he
separately authorizes publication.

## Phase 5 boundary

Phase 5 is not authorized by this handoff. It owns GPT project-pilot orientation/decomposition and
the Claude worker/verifier hierarchy: complete worker envelopes, model aliases, process evidence,
full diff scope checks, non-vacuous gates/results, timeout/lease handling, and independent verifier
evidence at the exact commit. Phase 4 deliberately launches none of that hierarchy.

Do not begin Phase 5 until Phase 4 is reviewed and merged by Lucas and
`537749193abcd6e8a9ce0aa9c3a8da73c679b42d` is independently confirmed as an ancestor of current
`origin/master`.

## Copy/paste prompt for the next implementation session

```text
Continue the Hermes Project Pilot with Phase 5 only.

First read:
- C:\Users\drfoo\github\AGENTS.md
- Recursion's CLAUDE.md and ANCHOR.md
- the live /opt/recursion/CONTROL_PLANE.md on gs-recursion
- docs/plans/hermes-project-pilot-production-plan.md
- docs/plans/hermes-project-pilot-phase0-evidence.md
- docs/plans/hermes-project-pilot-phase1-handoff.md
- docs/plans/hermes-project-pilot-phase1-deployment.md
- docs/plans/hermes-project-pilot-phase2-handoff.md
- docs/plans/hermes-project-pilot-phase3-handoff.md
- docs/plans/hermes-project-pilot-phase4-handoff.md

The Phase 4 implementation is commit 537749193abcd6e8a9ce0aa9c3a8da73c679b42d on the published
review branch origin/review/hermes-phase4-controls recorded in the Phase 4 handoff. Before
implementation, confirm Lucas reviewed and merged the branch and that the implementation commit is
an ancestor of current origin/master. Confirm all Phase 4 controls and artifacts are present. If it
is not merged, stop and report the blocker.

Keep remote state/PAUSE enabled. Do not deploy Phases 1-4 unless Lucas separately authorizes a
paused deployment. Leave the dirty local master at 20c1fa7 and all user-owned changes untouched.
Fetch origin and create a new clean Phase 5 authoring worktree/review branch from merged
origin/master; do not reuse any prior worktree or base Phase 5 on an unmerged branch.

Before changing code, reproduce and record the 17/17 baseline; all Phase 1-4 control suites; all
Phase 1-4 positive audits; the Phase 5 red controls; and the live Phase 1/PAUSE evidence. Treat live
findings as deployment-gated and do not change production.

Present an implementation plan before non-trivial code. Execute Phase 5 only. Preserve the
file/event architecture, the sole decision/action/actuator path, and all Phase 1-4 controls. Before
implementation, author and prove red controls that show: a worker committing a protected-file
change is rejected; test/fixture/out-of-scope mutation, missing result, and a no-op against a
non-vacuous task cannot pass; a hung worker times out, loses its lease, is terminated, and creates
one actionable escalation; and implementer/verifier runs are independent and cannot mutate each
other's output. Implement the Phase 5 worker envelopes, human-owned model aliases, PID/process
evidence, complete base..HEAD plus staged/unstaged/untracked/rename/delete scope checks,
non-vacuous gate/result rules, timeout handling, and exact-commit independent verification. Do not
run a live pilot or begin the Phase 6 autonomous loop.

Create/update the Phase 5 handoff and append exact red-to-green commands, results, implementation
OID, and final live PAUSE evidence to the project-pilot evidence. Do not run pilots, enable
autonomous execution, lift PAUSE, deploy, merge, push the Phase 5 branch, or open its PR unless
Lucas separately authorizes publication.
```

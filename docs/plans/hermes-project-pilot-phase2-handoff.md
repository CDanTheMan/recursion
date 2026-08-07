---
title: Hermes Project Pilot Phase 2 Handoff
type: handoff
status: ready-for-review
last-verified: 2026-08-07
related:
  - CONTROL_PLANE.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
  - docs/plans/hermes-project-pilot-phase1-handoff.md
  - docs/plans/hermes-project-pilot-phase1-deployment.md
---
# Hermes project pilot Phase 2 handoff

## Current state

- Phase 2 implementation commit: `9a4778fa794158c32e5f1381fb7b24c930202542`.
- Published review branch: `review/hermes-phase2-controls`.
- Draft PR: `https://github.com/NotSkittlz/recursion/pull/23`, targeting `master`.
- Authoring base: merged Phase 1 `origin/master` at
  `b25b3294dcbd320f92cd104718d795648fd57449`.
- PR #22 was merged by Lucas; Phase 1 implementation commit
  `0da2e1c8b0bea07849166aae58f80d9ed8191a49` is an ancestor of the authoring base.
- Existing baseline: 17/17 green at the Phase 2 implementation commit.
- Phase 1 controls: 8/8 green; positive sandbox/publication/dependency audit green.
- Phase 2 controls: 6/6 green; positive schema/action-coupling/rotation/backup audit green.
- Phase 3 controls: exactly six intended failures; Phase 3 was not implemented.
- Production: still paused and undeployed on `loop/auto` at
  `987fcfe08793b9fb5a452edf288a4fe9fc367ea1`, with zero transient workers.
- Live Phase 1 audit: exactly two deployment-gated findings remain: the old unrestricted/root
  gateway unit and advisories in its old installed dependency environment.

The exact pre-change red evidence, final green commands/results, implementation OID, harness
repair proof, and live PAUSE evidence are appended to
`docs/plans/hermes-project-pilot-phase0-evidence.md`.

## Implemented Phase 2 controls

Phase 2 preserves Recursion's canonical file/event architecture. It adds:

- versioned schemas and a dependency-free validator for projects, pilots, goals, tasks, runs,
  decisions, escalations, deliveries, instructions, and actions;
- atomic temp-write/fsync/rename state transitions, serialized planners, durable event appends,
  and state locks that fail closed;
- canonical goal and dependency validation before a task can start;
- deterministic action IDs and an append-only action journal with lifecycle state, leases,
  attempts, result evidence, replay suppression, and crash reconciliation;
- instruction consumption and acknowledgement coupled to the exact durable, succeeded action;
- PAUSE-gated event rotation and manifest-hashed backup/restore with ownership and mode checks.

## Review and publication boundary

Lucas authorized publication on 2026-08-07. The clean local worktree at
`C:\Users\drfoo\github\recursion-hermes-phase2` was pushed as
`review/hermes-phase2-controls`, and draft PR #23 was opened against `master`. Lucas will review
the branch and PR and perform the merge. Publication did not authorize deployment or any live
control-plane change.

Phase 1's paused deployment proposal remains documented but unexecuted. Its two live findings are
deployment gates, not waived acceptance criteria. Keep `/opt/recursion/state/PAUSE` present and do
not change live services while reviewing Phase 2.

## Phase 3 boundary

Phase 3 remains at its six falsifiers. Do not begin it until Phase 2 has been authorized for
publication, reviewed, merged, and independently confirmed in `origin/master`. Phase 3, not this
handoff—owns gateway narrowing to intake only, validated authoring preservation, richer
decision/usage evidence, lossless planner projections, and replacement of singleton decision
pointers with a durable queue.

No pilot, autonomous execution, PAUSE removal, deployment, or merge was performed. The only newly
authorized external actions were pushing the Phase 2 review branch and opening draft PR #23.

## Copy/paste prompt for the next session

```text
Continue the Hermes Project Pilot with Phase 3 only.

First read:
- C:\Users\drfoo\github\AGENTS.md
- Recursion's CLAUDE.md and ANCHOR.md
- the live /opt/recursion/CONTROL_PLANE.md on gs-recursion
- docs/plans/hermes-project-pilot-production-plan.md
- docs/plans/hermes-project-pilot-phase0-evidence.md
- docs/plans/hermes-project-pilot-phase1-handoff.md
- docs/plans/hermes-project-pilot-phase1-deployment.md
- docs/plans/hermes-project-pilot-phase2-handoff.md

The Phase 2 PR is recorded in docs/plans/hermes-project-pilot-phase2-handoff.md. Before
implementation, confirm that Lucas reviewed and merged it and that its Phase 2 controls are present
in current origin/master. Confirm the Phase 2 implementation commit
9a4778fa794158c32e5f1381fb7b24c930202542 is an ancestor of origin/master. If the PR is not
merged, stop and report the blocker.

Keep remote state/PAUSE enabled. Do not deploy Phase 1 or Phase 2 unless Lucas separately
authorizes a paused deployment. Leave the dirty local master at 20c1fa7 and all of its user-owned
changes untouched. Fetch origin and create a new clean Phase 3 authoring worktree and review branch
from the merged origin/master. Do not reuse the dirty master or base Phase 3 on an unmerged branch.

Before changing code, reproduce and record:
- the existing baseline: 17/17 green;
- the Phase 1 control suite: 8/8 green;
- the Phase 1 positive artifact/sandbox/publication audit: green;
- the Phase 2 control suite: 6/6 green;
- the Phase 2 positive schema/action-coupling/rotation/backup audit: green;
- the Phase 3 red suite: 6 intended failures;
- the live Phase 1 audit and PAUSE evidence. Treat remaining live findings as deployment-gated;
  do not silently waive or fix them on production.

Present an implementation plan before non-trivial code. Execute Phase 3 only, preserving the
existing file/event architecture and all Phase 1 and Phase 2 controls. Make all six Phase 3
controls pass without weakening them while keeping the 17/17 baseline, all eight Phase 1 controls,
all six Phase 2 controls, and both positive audits green.

Create or update a Phase 3 handoff and append exact red-to-green commands, results, commit OID, and
final live PAUSE evidence to the project-pilot evidence. Do not run pilots, enable autonomous
execution, lift PAUSE, deploy, merge, push the Phase 3 branch, or open its PR unless Lucas
separately authorizes publication.
```

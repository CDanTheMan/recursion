---
title: Hermes Project Pilot Phase 3 Handoff
type: handoff
status: published-for-review
last-verified: 2026-08-07
related:
  - CONTROL_PLANE.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
  - docs/plans/hermes-project-pilot-phase1-handoff.md
  - docs/plans/hermes-project-pilot-phase1-deployment.md
  - docs/plans/hermes-project-pilot-phase2-handoff.md
---
# Hermes project pilot Phase 3 handoff

## Current state

- Phase 3 implementation commit: `06a7422b6b51b9e2db6f7ca3e86b76da3cab2953`.
- Review branch: `review/hermes-phase3-controls` in the clean worktree
  `C:\Users\drfoo\github\recursion-hermes-phase3`.
- Authoring base: merged Phase 2 `origin/master` at
  `6adb1ba5b297c92d47c3d5c561ef7267dd7f3e3a`.
- PR #23 was merged by Lucas; Phase 2 implementation commit
  `9a4778fa794158c32e5f1381fb7b24c930202542` is an ancestor of the authoring base.
- Existing baseline: 17/17 green at the Phase 3 implementation commit.
- Phase 1 controls: 8/8 green; positive artifact/sandbox/publication audit green.
- Phase 2 controls: 6/6 green; positive schema/action-coupling/rotation/backup audit green.
- Phase 3 controls: 6/6 green; positive intake/decision/queue/coupling/supervision audit green.
- Production: still paused and undeployed on `loop/auto` at
  `b51bfff09fdc8f51cb8313ceb7267dbe0f701c69`, with zero transient workers.
- Live Phase 1 audit: exactly two deployment-gated findings remain: the old unrestricted/root
  gateway unit and advisories in its old installed dependency environment.

The exact pre-change red evidence, final green commands/results, implementation OID, and final
live PAUSE evidence are appended to
`docs/plans/hermes-project-pilot-phase0-evidence.md`.

## Implemented Phase 3 controls

Phase 3 preserves the file/event architecture and the Phase 2 action lifecycle. It adds:

- a Telegram gateway skill that is intake/status only and cannot directly invoke control-plane
  operations;
- durable instruction metadata for authenticated principal, topic, project, reply correlation,
  and deduplication identity, with no direct assist or handled shortcut;
- complete precedence-ordered authority/scope/decision projections and mandatory, fresh
  provider/usage evidence for every planning turn;
- schema-v1 normalized Head Hermes decisions in an append-only journal plus atomic
  `pending/running/succeeded/failed` projections, replacing the singleton latest pointer;
- a single supervised actuator that drains the durable queue through the existing Phase 2 action
  claim, automatically consumes and acknowledges an originating instruction only after the exact
  linked action succeeds, and never double-launches recovery work;
- one fail-closed control lock shared by planning-time resync and action-time git mutation, with
  no actuator cron entry competing with the supervised service;
- strict inertness for malformed Markdown, shell-shaped text, traversal, unknown verbs, unsafe
  arguments, and oversized/control-character prose.

## Review and publication boundary

Lucas explicitly authorized committing and pushing the Phase 3 review branch on 2026-08-07 so he
can review the diff and merge it in GitHub. The branch is published as
`origin/review/hermes-phase3-controls`. No PR was opened by the authoring session, and no live
service or cron entry was changed.

Publication does not authorize deployment. Phase 1's paused deployment proposal remains
unexecuted, Phase 2 and Phase 3 are undeployed, and the two live Phase 1 findings remain deployment
gates rather than waived acceptance criteria. Keep `/opt/recursion/state/PAUSE` present.

## Next-phase boundary

Phase 4 is not authorized by this handoff. Do not begin persistent project pilots until Phase 3 is
published, reviewed, merged, and independently confirmed in current `origin/master`. Do not run a
pilot, enable autonomous execution, remove PAUSE, deploy, or publish Phase 4 without Lucas's
separate explicit authorization for the relevant action.

Phases 4 through 8 remain in the production plan. The next implementation session must execute
Phase 4 only.

## Copy/paste prompt for the next session

```text
Continue the Hermes Project Pilot with Phase 4 only.

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

The Phase 3 review branch is recorded in docs/plans/hermes-project-pilot-phase3-handoff.md. Before
implementation, confirm that Lucas reviewed and merged it and that its Phase 3 controls are present
in current origin/master. Confirm the Phase 3 implementation commit
06a7422b6b51b9e2db6f7ca3e86b76da3cab2953 is an ancestor of origin/master. If the branch is not
merged, stop and report the blocker.

Keep remote state/PAUSE enabled. Do not deploy Phase 1, Phase 2, or Phase 3 unless Lucas separately
authorizes a paused deployment. Leave the dirty local master at 20c1fa7 and all of its user-owned
changes untouched. Fetch origin and create a new clean Phase 4 authoring worktree and review branch
from the merged origin/master. Do not reuse the dirty master or base Phase 4 on an unmerged branch.

Before changing code, reproduce and record:
- the existing baseline: 17/17 green;
- the Phase 1 control suite: 8/8 green;
- the Phase 1 positive artifact/sandbox/publication audit: green;
- the Phase 2 control suite: 6/6 green;
- the Phase 2 positive schema/action-coupling/rotation/backup audit: green;
- the Phase 3 control suite: 6/6 green;
- the Phase 3 positive intake/decision/queue/coupling/supervision audit: green;
- the Phase 4 red suite for all required controls;
- the live Phase 1 audit and PAUSE evidence. Treat remaining live findings as deployment-gated;
  do not silently waive or fix them on production.

Present an implementation plan before non-trivial code. Execute Phase 4 only: persistent project
pilots in Telegram topics. Preserve the existing file/event architecture and all Phase 1 through
Phase 3 controls. Before implementation, author and prove red controls that demonstrate:
- messages in two topics never share project state, tasks, worktrees, or pilot memory;
- a pilot refuses work outside its charter and cannot modify another project's priority;
- a direct status question returns live task/run/git evidence rather than remembered prose;
- a project with an absent key, stale clone, missing gate, or missing charter cannot activate.

Implement the Phase 4 deliverables from the production plan: durable pilot/topic/charter/model,
budget, notification, and goal-source metadata; one logical project pilot per active topic;
bounded read APIs and project-pilot verbs; forwarding of portfolio/policy requests to Head Hermes;
and two-step project registration with clone/auth/freshness proof before activation. Make the Phase
4 controls pass without weakening them while keeping the baseline and all Phase 1 through Phase 3
control and positive-audit suites green.

Create or update a Phase 4 handoff and append exact red-to-green commands, results, commit OID, and
final live PAUSE evidence to the project-pilot evidence. Do not run pilots, enable autonomous
execution, lift PAUSE, deploy, merge, push the Phase 4 branch, or open its PR unless Lucas separately
authorizes publication.
```

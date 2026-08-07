---
title: Hermes Project Pilot Phase 1 Handoff
type: handoff
status: ready-for-review
last-verified: 2026-08-06
related:
  - CONTROL_PLANE.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
  - docs/plans/hermes-project-pilot-phase1-deployment.md
---
# Hermes project pilot Phase 1 handoff

## Current state

- Phase 1 implementation commit: `0da2e1c8b0bea07849166aae58f80d9ed8191a49`.
- Evidence commit before this handoff: `aef8a7cfeb7de6e8eb413f250c3386c8a332a75b`.
- Review branch: `review/hermes-phase1-controls`.
- Phase 1 PR: pending publication in this session.
- Authoring base: merged Phase 0 `origin/master` at
  `aadf7b301c9bd3e73b94c6cf5a47e6b5de893146`.
- Local Phase 1 controls: 8/8 green; positive sandbox/publication/dependency audit green.
- Existing baseline: 17/17 green at the Phase 1 implementation commit.
- Phase 2 and Phase 3 controls: six intended failures each; neither phase was implemented.
- Production: still paused on `loop/auto` at
  `58b912c46b0bbba8f420fdda685e05b958279daa`.
- Live Phase 1 audit: two expected deployment-gated findings remain because Phase 1 was not
  deployed. The gateway is still the old unrestricted service and the live environment still has
  the old dependency versions.

The exact commands and results are in
`docs/plans/hermes-project-pilot-phase0-evidence.md`. The proposed Phase 1 paused deployment and
rollback procedure is in `docs/plans/hermes-project-pilot-phase1-deployment.md` and has not been
executed.

## Phase 2 boundary

Phase 2 strengthens the existing file/event architecture; it does not replace it. Its scope is:

- versioned schemas for projects, pilots, goals, tasks, runs, decisions, escalations, and
  deliveries;
- atomic temp-write-plus-rename updates and locks that fail closed;
- an append-only action queue with lifecycle state, leases, attempts, result evidence, and
  idempotency keys;
- validator-enforced goal and task dependency IDs;
- instruction acknowledgement coupled to the resulting action IDs;
- tested event-log rotation, backup, and restore for ignored runtime state.

The six existing Phase 2 red controls are the starting falsifiers. Phase 2 must make them green
without weakening the test and while keeping the 17-suite baseline and all Phase 1 controls green.
Do not begin Phase 3, run a pilot, enable autonomous execution, lift PAUSE, deploy, merge, push the
Phase 2 branch, or open its PR without separate authorization.

## Copy/paste prompt for the next session

```text
Continue the Hermes Project Pilot with Phase 2 only.

First read:
- C:\Users\drfoo\github\AGENTS.md
- Recursion's CLAUDE.md and ANCHOR.md
- the live /opt/recursion/CONTROL_PLANE.md on gs-recursion
- docs/plans/hermes-project-pilot-production-plan.md
- docs/plans/hermes-project-pilot-phase0-evidence.md
- docs/plans/hermes-project-pilot-phase1-handoff.md
- docs/plans/hermes-project-pilot-phase1-deployment.md

The Phase 1 PR is recorded in docs/plans/hermes-project-pilot-phase1-handoff.md.
Before implementation, confirm that Lucas reviewed and merged it and that its Phase 1 controls are
present in current origin/master. Confirm the Phase 1 implementation commit
0da2e1c8b0bea07849166aae58f80d9ed8191a49 is an ancestor of origin/master. If the PR is not merged,
stop and report the blocker.

Keep remote state/PAUSE enabled. Do not deploy Phase 1 unless Lucas separately authorizes the
paused deployment. Leave the dirty local master at 20c1fa7 and all of its user-owned changes
untouched. Fetch origin and create a new clean Phase 2 authoring worktree and review branch from
the merged origin/master. Do not reuse the dirty master or base Phase 2 on an unmerged branch.

Before changing code, reproduce and record:
- the existing baseline: 17/17 green;
- the Phase 1 control suite: 8/8 green;
- the Phase 1 positive artifact/sandbox/publication audit: green;
- the Phase 2 red suite: 6 intended failures;
- the Phase 3 red suite: 6 intended failures;
- the live Phase 1 audit and PAUSE evidence. Treat any remaining live findings as deployment-gated;
  do not silently waive or fix them on production.

Present an implementation plan before non-trivial code. Execute Phase 2 only, preserving the
existing file/event architecture. Make all six Phase 2 controls pass without weakening them, while
keeping the 17/17 baseline and all Phase 1 controls green. Keep Phase 3 at its six intended red
failures.

Create or update a Phase 2 handoff and append exact red-to-green commands, results, commit OID, and
final live PAUSE evidence to the project-pilot evidence. Do not begin Phase 3, run pilots, enable
autonomous execution, lift PAUSE, deploy, merge, push the Phase 2 branch, or open its PR unless
Lucas separately authorizes publication.
```

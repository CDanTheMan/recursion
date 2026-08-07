---
title: Hermes Project Pilot Phase 2 Handoff
type: handoff
status: ready-for-review
last-verified: 2026-08-06
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
- Local review branch: `review/hermes-phase2-controls` (not pushed or published).
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

The branch exists only in the clean local worktree
`C:\Users\drfoo\github\recursion-hermes-phase2`. Lucas must review the local changes and separately
authorize publication before anyone pushes the branch or opens a PR. Do not merge or deploy it as
part of publication unless separately authorized for those actions.

Phase 1's paused deployment proposal remains documented but unexecuted. Its two live findings are
deployment gates, not waived acceptance criteria. Keep `/opt/recursion/state/PAUSE` present and do
not change live services while reviewing Phase 2.

## Phase 3 boundary

Phase 3 remains at its six falsifiers. Do not begin it until Phase 2 has been authorized for
publication, reviewed, merged, and independently confirmed in `origin/master`. Phase 3, not this
handoff—owns gateway narrowing to intake only, validated authoring preservation, richer
decision/usage evidence, lossless planner projections, and replacement of singleton decision
pointers with a durable queue.

No pilot, autonomous execution, PAUSE removal, deployment, merge, push, or PR is authorized by
this handoff.

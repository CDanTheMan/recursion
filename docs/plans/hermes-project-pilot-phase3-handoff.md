---
title: Hermes Project Pilot Phase 3 Handoff
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
---
# Hermes project pilot Phase 3 handoff

## Current state

- Phase 3 implementation commit: `06a7422b6b51b9e2db6f7ca3e86b76da3cab2953`.
- Local review branch: `review/hermes-phase3-controls` in the clean worktree
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

The Phase 3 branch is local only. It was not pushed, no PR was opened, and no live service or cron
entry was changed. Lucas must review the local branch and separately authorize publication before
it may be pushed or a draft PR may be opened.

Publication would still not authorize deployment. Phase 1's paused deployment proposal remains
unexecuted, Phase 2 and Phase 3 are undeployed, and the two live Phase 1 findings remain deployment
gates rather than waived acceptance criteria. Keep `/opt/recursion/state/PAUSE` present.

## Next-phase boundary

Phase 4 is not authorized by this handoff. Do not begin persistent project pilots until Phase 3 is
published, reviewed, merged, and independently confirmed in current `origin/master`. Do not run a
pilot, enable autonomous execution, remove PAUSE, deploy, merge, push, or open a PR without Lucas's
separate explicit authorization for the relevant action.

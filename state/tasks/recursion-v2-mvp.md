schema_version: 1
id: recursion-v2-mvp
workstream: recursion
goal_id: goal-recursion-v2-execution-fabric
dependencies: recursion-v2-execution-fabric-wip
goal: Deliver the source-only Recursion MVP authorized by Lucas on 2026-08-31, ending at an independently verified review branch and PR.
engine: codex
worker_class: control-plane-authoring
repo: /opt/recursion
acceptance: python3 scripts/tests/recursion-v2-mvp.test.py
workdir: .
allowed_paths: config,schemas,scripts,state/tasks/recursion-v2-mvp.md,docs/architecture.md,docs/plans/recursion-v2-execution-fabric.md,docs/audits
non_goals: production deployment or restart,PAUSE removal,credentials or auth,cron,routing policy,firewall,autonomy flags,on-demand billing,metered spend,protected or default branch merge,CONTROL_PLANE.md modification
autonomy: human-authored
status: passed

Lucas explicitly authorized this source-only control-plane authoring and MVP implementation
session on 2026-08-31. The acceptance program is the one machine-checkable source gate for the
MVP completion criteria in the authorization. Platform controls that cannot execute in a source
worktree must return a typed pending result and must not be reported as passing.

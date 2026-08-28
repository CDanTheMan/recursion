schema_version: 1
id: recursion-v2-execution-fabric-wip
workstream: recursion
goal_id: goal-recursion-v2-execution-fabric
dependencies:
goal: Record the audited Recursion v2 target architecture and autonomous execution handoff on a review branch.
engine: none
worker_class: control-plane-authoring
repo: /opt/recursion
sshkey: ~/.ssh/id_deploy
acceptance: git diff --check origin/master...HEAD
workdir: .
allowed_paths: docs/architecture.md,docs/audits/recursion-v2-infrastructure-audit-2026-08-28.md,docs/plans/recursion-v2-execution-fabric.md,state/DECISIONS.md,state/goals/goal-recursion-v2-execution-fabric.md,state/tasks/recursion-v2-execution-fabric-wip.md
non_goals: implementation, deployment, credentials, routing flags, cron, PAUSE removal, default-branch merge
autonomy: human-authored
status: passed

Lucas explicitly authorized this documentation-only control-plane authoring session on 2026-08-28.
The task records the plan for a separate Codex session; it performs no plan phase itself.

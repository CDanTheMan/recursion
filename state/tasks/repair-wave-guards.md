schema_version: 1
id: repair-wave-guards
workstream: recursion
goal_id: goal-recursion-v2-execution-fabric
dependencies:
goal: Record General Manager pass verdict for foundry repair-wave guards on test evidence.
engine: none
worker_class: control-plane-authoring
repo: /opt/recursion
sshkey: ~/.ssh/id_deploy
acceptance: python -m pytest tools/construction_swarm/test_provider_output_guard.py tools/construction_swarm/test_tool_receipt_inventory.py
workdir: .
allowed_paths: state/tasks/repair-wave-guards.md,tools/construction_swarm
non_goals: default-branch merge,credentials,autonomy flags
autonomy: human-authored
status: passed

General Manager verdict: repair-wave-guards is passed on test evidence.
Test totals 18 plus 25 passing.
Commits 427c265 and 69dd124.
Merge review stays with the General Manager.

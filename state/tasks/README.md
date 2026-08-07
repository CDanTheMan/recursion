# task queue — one file per build-loop task (delegation-design.md task model).
# Schema v1: every canonical task names an active state/goals/<goal_id>.md parent and explicit
# dependency ids; scripts/taskctl.sh enforces both before leasing the task.
# Executor: scripts/work.sh. List: recursion tasks. Run: recursion work <id>.

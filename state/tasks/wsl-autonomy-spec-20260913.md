schema_version: 1
id: wsl-autonomy-spec-20260913
goal_id: goal-recursion-v2-execution-fabric
project_id: recursion
status: in_review

Lucas requested a specification for continuous research/testing/development on the D: WSL
sandbox, with Cursor/Codex participation, additional contributed agents, model diversity,
quality/depth preservation and GrokBot access as an operator capability.

Baseline: `ba6720c262a1293bd132b5c83504fd6a52e9de72` (the local orientation repair).
Branch: `loop/work/wsl-autonomy-spec-20260913`.
Allowed paths: docs/v3/START-HERE.md,
docs/v3/construction-swarm/CONTINUOUS-OPERATION.md,
docs/v3/construction-swarm/continuous-operation-contract.json,
state/tasks/wsl-autonomy-spec-20260913.md, tools/check_wsl_autonomy_spec.py.

Gate: `python -X utf8 -B tools/check_wsl_autonomy_spec.py --candidate FULL_COMMIT`.
Require clean exact candidate, bounded changed paths, retained original specifications,
all requirement/scenario/phase references resolved, source links present and proposed
activation explicitly false. The runtime scenarios remain specified, not executed.

Non-goals: running or installing the service; starting WSL or agent campaigns; changing
authority, auth, model/provider configuration, cron, power policy, secrets or autonomy;
purchasing credits; modifying historical contracts/evidence; production deployment;
autonomous merge. Routine proposed design parameters are labelled for later ratification.
The current request authorizes specification work, not operational activation.

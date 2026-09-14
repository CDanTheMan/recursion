schema_version: 1
id: wsl-autonomy-spec-20260913
goal_id: goal-recursion-v2-execution-fabric
project_id: recursion
status: passed

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

## Independent review and publication follow-up

Lucas requested an independent Muse Spark 1.3 Contributor review via OpenCode Go,
then explicitly requested a commit and PR for his merge. The complete review of
`59fed9628fa19da5d1762462f1aae7e1531d250e` returned
`READY_FOR_BOUNDED_IMPLEMENTATION`, with no blocker to P1 fake-worker implementation.
OpenCode 1.18.30's export verified `opencode-go/muse-spark-1.3-contributor`, zero
tool calls and normal scoped-process cleanup. Complete CW-01–18, S01–26 and P1–8
coverage was confirmed; a prior attachment-truncated review is superseded.

Complete review SHA-256:
`e7e051861486088d7a19168b3322b2f70b7764e7b0e9a36c9e730101fe7e29ef`.
Session export SHA-256:
`4a24b8b04a869aa9323f9835a3b6daa004ef9bba7d0986e6c0b65d3309cb1ae8`.
Local full evidence: git common directory,
`research-handoffs/wsl-autonomy-spec-20260913/muse-review-03/`.
Evidence is not a runtime qualification or a review of later changed bytes.

All five findings are addressed in this follow-up: concurrent controller starts
in S03; canonical revision conflicts in CW-01/S01/S06; contributed-child isolation
in CW-06/S06; exact review-backlog refusal in S11; off-VHDX restore provenance and
digest binding in S26. These are specification refinements, not implemented tests.
Final scope/traceability checking binds the subsequent committed candidate.
This task status denotes authoring-gate completion only, not runtime qualification.

Next suggested execution packet: P1 only, parent goal as above, exact new source
commit, explicit implementation/test paths and executable race/replay/permission/
crash gates established before coding. An eight-hour work window is a ceiling,
not a reason to keep generating after completion. P2 can follow in its own packet;
live fleet activation still waits for P3–P7 and fresh Owner provisioning.

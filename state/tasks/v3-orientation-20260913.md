schema_version: 1
id: v3-orientation-20260913
goal_id: goal-recursion-v2-execution-fabric
project_id: recursion
status: in_review

Lucas requested repository repair and verification of the intact v3 specifications on
2026-09-13. This task repairs development orientation and checks source integrity.
The legacy parent identifier records lineage; the development target is Recursion v3.

Baseline: `797be4f18edf3f9e0f2dbac9432f190dbe1ed969`.
Branch: `loop/work/v3-orientation-20260913`.
Allowed paths: README.md, AGENTS.md, CLAUDE.md, docs/v3/README.md,
docs/v3/VALIDATION.md, docs/v3/ROADMAP.md, docs/v3/START-HERE.md,
state/tasks/v3-orientation-20260913.md, tools/check_v3_orientation.py.

Acceptance: `python -X utf8 -B tools/check_v3_orientation.py --contracts --candidate FULL_COMMIT`.
The candidate must be clean, remain within the exact allowlist and preserve every
other baseline path. Verify the canonical document links, claim/Owner decision
registries, all 71 M1 fixtures, schema/fixture reproducibility and all 17 M1 test programs.
Record the exact candidate and command results; independent review and Lucas's merge
remain separate from the executor's successful local checks.

Non-goals: modifying product requirements or historical evidence; choosing a runtime,
language, store or model; enabling a scheduler or launching paid/provider workers;
changing the constitution, auth, config, cron, autonomy, operational state or deployment;
merging to master. No inference credit purchase or reset is authorized by this task.

Stop on a missing accepted specification, failed frozen contract, out-of-scope required
repair or a consequential Owner decision. Record the exact finding without rewriting
sealed evidence or silently weakening its gate.

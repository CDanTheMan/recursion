# Recursion — self-improvement proposals (human-review queue)

Reflect.sh appends; a human applies or rejects. NOTHING here is auto-applied (CLAUDE.md rule 3).
[APPLY-SAFE] = low-risk, likely-approve. [NEEDS-APPROVAL] = touches config/auth/model/cron/gate/spend/mining.

## 2026-08-05 20:28 — [NEEDS-APPROVAL] Add a native-diff numeric acceptance gate for GSC frontier tasks
status: DONE 2026-08-05 — built as scripts/gsc-nativediff-gate.sh (commit 8a6755f); baseline state/gsc/nativediff-baseline.tsv; roadmap state/roadmaps/gsc-renderer.md

[NEEDS-APPROVAL] Add a native-diff numeric acceptance gate for GSC frontier tasks
**Evidence:** “GSC corpus deployed; conformance is COMPLETE” says 211 tests yield 206 pass, 0 FAIL, 5 skip and explicitly identifies native-diff quality as the frontier requiring “a NUMERIC acceptance gate (error must strictly decrease + a control reproducing the old golden).”
**Change:** Human to design and approve a native-mesh error baseline/control and strict-decrease gate, then add its task-planner integration under the GSC overnight workflow.
**Fitness:** Reduces GSC native-diff error and restores productive build-loop work without re-running already-green conformance tasks.
**Risk:** Changes acceptance gates and task selection; baseline design could reward misleading aggregate improvements, so it requires human approval.

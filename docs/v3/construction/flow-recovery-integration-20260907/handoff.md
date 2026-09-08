# Flow and recovery integration checkpoint

Read CONTROL_PLANE.md first, applicable CLAUDE/AGENTS, then ANCHOR.md.

Parent goal: goal-recursion-v2-execution-fabric.
Goal: recursion.v3.flow-recovery-integration.20260907.
Worktree: recursion-v3-flow-recovery-integration-20260907.
Branch: codex/v3-flow-recovery-integration-20260907.
Frozen start: f86f169c61ca6db4a3d7870353f270e35ef954d6.
Started 2026-09-08T01:09:17Z. Outer deadline 04:39:28Z, discovery cutoff 03:09:28Z.

This is an incomplete checkpoint. The Owner's stop condition occurred: at 01:25:29Z
(18:25 Pacific on 2026-09-07), the live usage feed changed from 85% used with reset
timestamp1789355738 to 0% used with reset timestamp1789435401. Both banked credits
remained unused. No manual reset, paid fallback or operational configuration change occurred.
The monitoring heartbeat watch-automatic-codex-reset was paused. No new construction was
started after observing the reset; only checkpoint and validation bookkeeping followed.

The prior completed review stack is PR94 interface probes, PR95 formal subsystem, and
PR96 RESET mapping. Their exact candidates are a497bae, c87f492 and f86f169, respectively.
Those worktrees and the original research worktree at 51733c4 must remain frozen because
historical working gates depend on them. Do not rewrite or reset any branch.

The present semantic source is 846e02aa6ee649a8668fa33e62f6263acefbc24b. One prospective
local run completed successfully at 01:22:21Z. Source snapshots, admission, stdout, result and
execution receipt are under Git common research-attestations/flow-recovery-integration/
discovery/20260908T012125403181/. evidence.json hashes those files; results.json preserves
the actual output. Two independent read-only design challenges found no blocking transition
or audit error within this finite scope. They did not review the final gate or exact checkpoint
as a publication candidate; their extra in-memory controls are not adopted raw measurements.

Canonical findings are FRI-001 in ARCHITECTURE, FRI-002 in EXECUTION-FABRIC and FRI-003
in TERMINAL-RUNTIME. There are 97,500 reachable split/audit states and 603,827 transitions
per cursor profile, zero frontier, maximum explored depth32 without a depth cutoff, nine
semantic mutation counterexamples, 45,240 finite audit controls, twelve long controls,
four special controls, eleven witnesses per profile and two 32-action combined witnesses.
The independent inclusive definition is checked through exact local correspondence over
every reachable split/audit state; these are not separate execution performance comparisons.

Preserve the important limits: retention loss and snapshot availability are separately modeled
facts; WELCOME audit advancement precedes application RESET installation; future candidates
remain owned; historical requires_reset is not current recovery. Stop establishes logical
control progress only and does not fence later offers/emissions. Framing quarantine blocks
new offers only, and no parser oversize rejection is implemented. Event-count queue saturation
is not independently exercised by this byte-capacity2 profile. FIFO ordering is maintained by
the current transitions but no separate reorder mutant or data-progress theorem is present.
Actual emitted-exhaustion recovery remains in literal controls, outside the normal-source
product. Shared domain/cursor encoding and finite bounds remain assumptions.

Full formal comparison and freeze remain false. Preserve all six obligations and 27 corpus
rows: earlier01/02/26 are partial,22 unselected, others unimplemented. No language/store choice,
M1 contract change or common-writer migration clearance is authorized by this result.

Resume by inspecting checkpoint.json and external checkpoint receipts. Then review the new
gate and domain claims, run --working if needed, repair any defect, stage exact artifacts and
regenerate inventory with experiments/v3/flow-recovery-integration/inventory.py. The intended
complete gate is python -X utf8 -B experiments/v3/flow-recovery-integration/check.py --candidate
FULL_HASH. It reproduces the model in an isolated process, preserves the unchanged25 commands,
and invokes four frozen historical working gates. It has not yet been accepted as a final gate.

Before publication, run that complete gate twice on the identical clean candidate and obtain
two independent exact-commit reviews. Any repair requires both gates and both reviews again.
Normal-push only this review branch and create a draft PR stacked on the current predecessor
after rechecking remote state. No publication has been performed for this packet. External
final attestations belong under research-attestations/flow-recovery-integration/<candidate>/.

Next bounded requests are recorded in ROADMAP: real local retention/snapshot evidence,
complementary event-queue pressure, actual emitted-exhaustion product, then physical control
transport/fencing and remaining full formal obligations. The current invocation ended on the
automatic reset; a continuation must establish its new time/capacity envelope before launching
more work. No new consequential Owner decision. First new GRILLME decision: none.

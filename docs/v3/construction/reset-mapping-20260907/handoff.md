# RESET mapping continuation

Read CONTROL_PLANE.md, applicable CLAUDE/AGENTS and ANCHOR.md first.

Parent goal: goal-recursion-v2-execution-fabric. Goal: recursion.v3.reset-mapping.20260907.
Branch: codex/v3-reset-mapping-20260907. Frozen start: c87f492780087772e3bcb06249ef14d89e812a25.
Owner approved included-capacity work until 18:00 Los Angeles on 2026-09-07: 2026-09-08T01:00:00Z.
Started 2026-09-08T00:44:36Z. Prior outer deadline remains 04:39:28Z; this burst stops earlier.
No metered spend, reset credits, active-assistant config/auth/model/routing changes or deployment.

Canonical findings live in EXECUTION-FABRIC, TERMINAL-RUNTIME, ACCEPTANCE and ROADMAP.
This packet owns manifest.json, goal.json, plan.json, evidence.json and results.json.
The immutable M1 contracts and historical records remain untouched.

The new mapper defers an un-emitted candidate until credit AND queue capacity permit delivery.
It does not force RESET for local deferral. Actual emitted exhaustion still requires RESET.
A real replay-store gap permits the existing HELLO/WELCOME/RESET/fresh-CREDIT sequence, conditional
on genuine retention and snapshot facts. The wire oracle alone cannot establish those facts.
M1B requires_reset is historical recovery evidence, not a current imperative to RESET.

Separate split/inclusive mapper transitions enumerate every bounded schedule prefix for 16
configurations: 2,576 prefixes and 544 complete schedules. Two offers and two CREDIT grants bound
the environment, not a general transition-depth theorem. All terminal schedules complete both
events; no scheduler fairness or unbounded producer theorem is claimed. Twelve literal controls
and five fact-guard failures preserve edge cases. All payloads and store facts are synthetic.

An initial attempt failed because an empty wire prefix violates the schema. The accepted revision
starts with HELLO/WELCOME and the selected cursor unit. Failed source and a truthful failure
record are retained; the original full terminal log was not retained. Successful development
source/results are snapshotted after execution. Exact-candidate final gates independently
reproduce those results from committed source.

Use python -X utf8 -B experiments/v3/reset-mapping/check.py --working for scoped checks.
Use --candidate FULL_HASH on the clean candidate for the complete gate, twice, followed by two
independent exact-candidate approvals before normal review-branch publication.
The gate preserves the unchanged25 inventory and original working gates on frozen c87f492,
a497bae and 51733c4 worktrees. Do not alter those worktrees.
Final receipts are external under Git common research-attestations/reset-mapping/<candidate>/.
Raw failures and successful snapshots are under research-attestations/reset-mapping/discovery/.
If final receipts or publication completion are absent, this is a resumable incomplete checkpoint.

Next: integrate explicit deferred admission and current recovery state into both prior full
broker models, preserving their old RESET counterexample. Establish replay-store evidence and
physical control/loss/recovery behavior separately. All six obligations and 27 corpus rows stay
required; prior 01/02/26 coverage remains partial,22 unselected,othersunimplemented.
Full formal freeze remains false; language then storage comparison follow the complete gate.
No new consequential Owner decision. First new GRILLME decision: none.

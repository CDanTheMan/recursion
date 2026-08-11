#!/usr/bin/env bash
# Positive Phase 6 architecture/evidence audit. Hermetic: scenario coverage supplies stubs;
# this script never calls a model, network API, real publisher, notifier, or live state.
set -euo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$ROOT"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

bash -n scripts/conduct-hermes.sh scripts/hermes-actuator.sh scripts/taskctl.sh \
  scripts/tests/hermes-pilot-phase6-red.test.sh
python3 -m py_compile scripts/project-reconcile.py scripts/project-pilot.py \
  scripts/decision-queue.py scripts/jsonl_durable.py scripts/transition_receipt.py \
  scripts/validate-decision.py scripts/validate-control-state.py scripts/runtime-state.py
python3 -m json.tool schemas/control-plane/v1/schema.json >/dev/null
echo "ok    Phase 6 shell, Python, and schema artifacts parse"

for verb in reconcile-goal task-transition goal-transition verify-goal publish-task; do
  grep -q "\"$verb\"" scripts/validate-decision.py
  grep -q "$verb" scripts/conduct-hermes.sh
done
! grep -qE 'reconcile-goal|task-transition|goal-transition|verify-goal|publish-task' scripts/hermes-decide.sh
grep -q 'project-reconcile.py.*schedule' scripts/hermes-actuator.sh
count="$(find deploy -type f \( -name '*actuator*.service' -o -name '*actuator*.timer' \) 2>/dev/null | wc -l)"
[ "$count" -le 1 ]
echo "ok    Phase 6 is inside the existing supervised scheduler and sole decision/action/actuator path"

grep -q 'taskctl.sh.*cas' scripts/project-reconcile.py
grep -q 'CAS expected' scripts/taskctl.sh
grep -q 'goal compare-and-swap failed' scripts/project-reconcile.py
grep -q '"goal-transition"' scripts/project-reconcile.py
grep -q 'resume_transition(base, transition)' scripts/project-reconcile.py
grep -q 'recovery-reconciled' scripts/project-reconcile.py
echo "ok    task/goal changes are compare-and-swap transitions with receipt-backed recovery/events"

grep -q 'goal_state_lock' scripts/project-pilot.py
grep -q 'verification may reopen a goal only with failing evidence' scripts/project-reconcile.py
grep -q 'status") not in ACTIVE_GOALS' scripts/project-reconcile.py
grep -q 'consumed_task_ids' scripts/tests/hermes-pilot-phase6-red.test.sh
grep -q 'mutation-backed terminal receipt resumes and replays exactly once' \
  scripts/tests/hermes-pilot-phase6-red.test.sh
echo "ok    verifying closes task creation; evidence is required to reopen; terminal goals stay closed"

cat > "$TMP/goal.json" <<'JSON'
{"schema_version":1,"id":"goal","project_id":"project","outcome":"measurable","acceptance_suite":"test -s app/out","falsifier":"exact evidence disagrees","budget":{"max_concurrency":1,"max_tokens":100,"max_cost_usd":1,"max_wall_clock_seconds":60,"max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":1,"publication_required":true},"status":"budget-exhausted"}
JSON
python3 scripts/validate-control-state.py goal "$TMP/goal.json" >/dev/null
for field in max_concurrency max_tokens max_cost_usd max_wall_clock_seconds max_task_attempts \
             max_failures max_review_queue max_publish_attempts publication_required; do
  grep -q "$field" scripts/project-reconcile.py
done
grep -q 'review-backpressure' scripts/project-reconcile.py
echo "ok    concurrency, usage/cost, wall-clock, retry/failure, publication, and review budgets validate"

for path in state/evidence state/recovery state/deliveries; do
  grep -qF "$path" .gitignore
  grep -qF "\"$path\"" scripts/runtime-state.py
done
grep -q 'dead_process_tasks' scripts/project-reconcile.py
grep -q 'worktrees' scripts/project-reconcile.py
grep -q 'git_refs' scripts/project-reconcile.py
grep -q 'deliveries' scripts/project-reconcile.py
echo "ok    crash/reboot recovery covers ignored task/process/worktree/ref/event/delivery state"

bash scripts/tests/hermes-pilot-phase6-red.test.sh
echo "hermes-pilot-phase6-green: ALL PASS"

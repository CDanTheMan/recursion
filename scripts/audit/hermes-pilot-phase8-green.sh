#!/usr/bin/env bash
# Positive architecture audit for Phase 8 observed project pilots.
set -euo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$ROOT"

bash -n scripts/conduct-hermes.sh scripts/hermes-actuator.sh scripts/hermes-decide.sh \
  scripts/assist.sh scripts/taskctl.sh scripts/work.sh scripts/tests/hermes-pilot-phase8-red.test.sh
python3 -m py_compile scripts/project-pilot.py scripts/project-reconcile.py scripts/decision-queue.py \
  scripts/notification-outbox.py scripts/validate-decision.py scripts/validate-control-state.py \
  scripts/runtime-state.py scripts/tests/hermes-pilot-phase8-red.py \
  scripts/tests/hermes-pilot-phase8-parallel.py \
  scripts/tests/hermes-pilot-phase8-legacy-journal-red.py
python3 - <<'PY'
import json
json.load(open('schemas/control-plane/v1/schema.json',encoding='utf-8'))
PY
echo "ok    Phase 8 shell, Python, and schema artifacts parse"

for verb in pilot-plan-propose pilot-plan-approve pilot-window-open pilot-window-close; do
  grep -q "$verb" scripts/hermes-decide.sh
  grep -q "$verb" scripts/validate-decision.py
  grep -q "$verb" scripts/conduct-hermes.sh
done
grep -q 'canonical_digest(plan)' scripts/project-pilot.py
grep -q 'fresh pilot plan reuses an existing goal id' scripts/project-pilot.py
grep -q 'Lucas instruction does not name the exact Phase 8 object' scripts/project-pilot.py
echo "ok    fresh synthesis, schema bounds, collision refusal, and exact Lucas digest/window approval are mechanical"

grep -q 'build_pilot_brief' scripts/hermes-decide.sh
grep -q 'RECURSION_PILOT_MODEL' scripts/hermes-decide.sh
grep -q 'DECIDER_ACTOR="$route"' scripts/hermes-decide.sh
grep -q 'approve.*plan' scripts/intake.sh
echo "ok    event-invoked logical GPT pilots receive a scoped brief and approval/assist authority routes to Head Hermes"

grep -q 'a pilot window may be authorized only while PAUSE is observed' scripts/project-pilot.py
grep -q 'exact open pilot window authority is absent' scripts/project-reconcile.py
grep -q 'close-paused-windows' scripts/hermes-actuator.sh
grep -q 'admit-work' scripts/conduct-hermes.sh
echo "ok    exact-goal admission is rechecked at actuation and PAUSE revokes stale authority"

grep -q 'claim-pending --kind work' scripts/conduct-hermes.sh
grep -q 'RECURSION_PILOT_GLOBAL_CONCURRENCY' scripts/conduct-hermes.sh
grep -q -- '--exclude-project' scripts/conduct-hermes.sh
grep -q 'concurrency_limit' scripts/project-reconcile.py
grep -q 'max_inflight_workers' scripts/project-reconcile.py
echo "ok    the sole actuator enforces global and per-project worker capacity without a second executor"

grep -q 'resume-assist' scripts/assist.sh
grep -q 'resume_assist' scripts/project-reconcile.py
grep -q 'resume_event_id' scripts/project-reconcile.py
grep -q 'DURABLE_REPORTING' scripts/assist.sh
grep -q 'PILOT_ID' scripts/work.sh
grep -q 'assist-open' scripts/notification-outbox.py
grep -q 'assist-answer' scripts/notification-outbox.py
echo "ok    one answered assist reopens the same goal/task and all pilot notices use the Phase 7 outbox"

for state_path in state/decisions.jsonl state/decision-queue state/goals state/tasks state/assists \
  state/plans state/pilot-windows; do
  grep -qF "\"$state_path\"" scripts/runtime-state.py
done
for ignored in state/plans state/pilot-windows; do grep -qF "$ignored/" .gitignore; done
echo "ok    plan/window/queue/goal/task/assist state is backup-covered and runtime projections stay untracked"

for event in plan-proposed plan-approved pilot-window-armed pilot-window-opened pilot-window-closed \
  lucas-attention-required human-answer-received; do
  grep -q "$event" scripts/notification-outbox.py
done
grep -q 'source-plan-proposed-' scripts/project-pilot.py
grep -q 'source-assist-' scripts/project-reconcile.py
echo "ok    stable source-event identities feed exact-once Phase 7 delivery policy"

grep -q 'LEGACY_PRE_SCHEMA_NOOP_SHA256' scripts/decision-queue.py
grep -q 'reviewed-pre-schema-noop' scripts/decision-queue.py
grep -q 'decision journal import failed rc=' scripts/conduct-hermes.sh
grep -q 'PAUSE-safe queue pass failed rc=' scripts/hermes-actuator.sh
echo "ok    exact reviewed legacy noops are non-executable and journal failures are observable"

bash scripts/tests/hermes-pilot-phase8-red.test.sh
echo "hermes-pilot-phase8-green: ALL PASS"

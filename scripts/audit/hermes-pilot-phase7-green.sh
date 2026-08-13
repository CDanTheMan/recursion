#!/usr/bin/env bash
# Positive architecture audit for Phase 7 reporting and notification fan-out.
set -euo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$ROOT"

bash -n scripts/notify.sh scripts/conduct-hermes.sh scripts/hermes-actuator.sh \
  scripts/tests/hermes-pilot-phase7-red.test.sh
python3 -m py_compile scripts/notification-outbox.py scripts/jsonl_durable.py \
  scripts/transition_receipt.py scripts/validate-decision.py \
  scripts/validate-control-state.py scripts/runtime-state.py \
  scripts/tests/hermes-pilot-phase7-red.py scripts/tests/notification-transition-receipt.test.py \
  scripts/tests/invalid-task-contract-notification.test.py
python3 - <<'PY'
import json
json.load(open('schemas/control-plane/v1/schema.json',encoding='utf-8'))
PY
echo "ok    Phase 7 shell, Python, and schema artifacts parse"

grep -q 'notification-outbox.py.*schedule' scripts/hermes-actuator.sh
for verb in notification-reconcile notification-deliver notification-portfolio notification-audit notification-recover; do
  grep -q "$verb" scripts/conduct-hermes.sh
  grep -q "\"$verb\"" scripts/validate-decision.py
done
grep -q 'RECURSION_QUEUE_ACTUATION' scripts/notification-outbox.py
grep -q 'scripts/notify.sh' scripts/notification-outbox.py
! grep -Eq 'api\.telegram\.org|hermes send' scripts/notification-outbox.py
echo "ok    one supervised scheduler, durable decision queue, sole actuator, and existing sender remain the only path"

for token in project-topic head-hermes lucas-direct portfolio-account portfolio-channel; do
  grep -q "$token" scripts/notification-outbox.py
done
for event in goal-accepted plan-approved worker-launched task-passed task-failed task-blocked \
  human-answer-received review-branch-published goal-verifying goal-achieved goal-stopped; do
  grep -q "$event" scripts/notification-outbox.py
done
grep -q 'stable_id("delivery", event\["id"\], destination)' scripts/notification-outbox.py
echo "ok    strict destination policies and exact event/destination delivery identity are explicit"

for state_path in notification-events delivery-events transport-evidence reports; do
  grep -q "$state_path" scripts/runtime-state.py
  grep -q "$state_path" .gitignore
done
grep -q 'os\.fsync' scripts/notification-outbox.py
grep -q 'acknowledged-from-durable-transport-evidence' scripts/notification-outbox.py
grep -q 'transport returned no valid acceptance evidence' scripts/notification-outbox.py
echo "ok    outbox, receipts, reports, lifecycle history, and recovery state are durable and backup-covered"

grep -q 'RECURSION_DELIVERY_MAX_ATTEMPTS' scripts/notification-outbox.py
grep -q 'RECURSION_DELIVERY_BACKOFF_MAX_S' scripts/notification-outbox.py
grep -q 'dead-letter' scripts/notification-outbox.py
grep -q 'delivery-dead-letter:' scripts/notification-outbox.py
grep -q 'state/PAUSE' scripts/notification-outbox.py
echo "ok    bounded retry/backoff, dead-letter escalation, and PAUSE refusal are mechanical"

grep -q 'pilot-terminal-report' scripts/notification-outbox.py
grep -q 'portfolio-result' scripts/notification-outbox.py
grep -q 'delivery_acknowledgements' scripts/notification-outbox.py
grep -q 'goal_id}-audit.json' scripts/notification-outbox.py
echo "ok    pilot-to-Head ordering, one portfolio result, and complete terminal correlation are explicit"

bash scripts/tests/hermes-pilot-phase7-red.test.sh
python3 scripts/tests/notification-transition-receipt.test.py
python3 scripts/tests/invalid-task-contract-notification.test.py
echo "hermes-pilot-phase7-green: ALL PASS"

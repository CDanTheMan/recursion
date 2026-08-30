#!/usr/bin/env bash
# Phase 0 control: reproduce the Phase 2 durability/idempotency defects before fixing them.
# This suite is EXPECTED TO FAIL on the pre-change commit recorded in the production plan.
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }
stage_controller_closure(){
  local root="$1"
  for helper in assignment.py assist.sh author.sh board.sh branch-review.sh capacity.sh conduct-hermes.sh conduct.sh \
      decision-queue.py engine_contract.py git-scope.py hermes-decide.sh instruction_routing.py intake.sh \
      jsonl_durable.py notification-outbox.py notify.sh pilot_instruction.py plan.sh project-pilot.py \
      project-reconcile.py project_authority.py provider-connect-proxy.py provider_contract.py provider-network.sh provider-egress.py publish.sh \
      remote_evidence.py resolve-engine.py resolve-model-alias.py resync.sh run_contract.py runtime-state.py \
      seed_contract.py taskctl.sh transition_receipt.py validate-assignment-result.py validate-control-state.py \
      validate-decision.py validate-gate.py validate-verifier-result.py validate-worker-result.py work.sh assignment-token.py \
      worker-evidence.py worker-sandbox.sh; do
    cp "$SRC/scripts/$helper" "$root/scripts/"
  done
}
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# 1. Replaying the same durable decision ten times must execute one action, not ten.
R="$TMP/replay"; mkdir -p "$R/scripts" "$R/state/tasks" "$R/loop/logs"
cp "$SRC/scripts/conduct-hermes.sh" "$R/scripts/"
cp "$SRC/scripts/taskctl.sh" "$R/scripts/"
cp "$SRC/scripts/jsonl_durable.py" "$SRC/scripts/transition_receipt.py" \
  "$SRC/scripts/runtime-state.py" "$R/scripts/"
cp "$SRC/scripts/decision-queue.py" "$SRC/scripts/validate-control-state.py" \
  "$SRC/scripts/validate-decision.py" "$SRC/scripts/engine_contract.py" \
  "$SRC/scripts/assignment.py" "$R/scripts/"
stage_controller_closure "$R"
normalize_head_decision(){
  local file="$1" temporary="$1.normalized"
  python3 - "$file" <<'PY' | RECURSION_ROOT="$R" python3 "$R/scripts/decision-queue.py" normalize > "$temporary"
import json,sys
row=json.load(open(sys.argv[1],encoding='utf-8'))
row.setdefault('actor','head-hermes')
row.setdefault('decision_source','hermes-model')
row.setdefault('routed_decider','head-hermes')
row.setdefault('why',row.get('reason') or 'Phase 2 red control')
print(json.dumps(row,separators=(',',':')))
PY
  mv -f "$temporary" "$file"
}
cat > "$R/scripts/work.sh" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$1" >> "$ACTION_LOG"
STUB
chmod +x "$R/scripts/"*.sh
python3 "$SRC/scripts/tests/staged-dependency-guard.py" "$SRC/scripts" "$R/scripts" \
  || { no "replay fixture is missing a staged first-party dependency"; }
cat > "$R/state/tasks/replay-task.md" <<'T'
id: replay-task
goal_id: goal-1
acceptance: true
status: queued
T
cat > "$TMP/replay.json" <<'J'
{"id":"decision-replay","idempotency_key":"same-key","verb":"work","args":["replay-task"],"goal":"goal-1","wrong_if":"more than once"}
J
normalize_head_decision "$TMP/replay.json"
: > "$TMP/replay.log"
for _ in $(seq 1 10); do
  ( cd "$R" && ACTION_LOG="$TMP/replay.log" RECURSION_ROOT="$R" \
      bash scripts/conduct-hermes.sh --file "$TMP/replay.json" ) >/dev/null 2>&1 || true
done
n="$(wc -l < "$TMP/replay.log" | tr -d ' ')"
[ "$n" = 1 ] && ok "ten replays executed one idempotent action" \
             || no "ten replays executed $n actions (no durable idempotency claim)"

# 2. Crash after dispatch/before acknowledgement must reconcile without launching twice.
cat > "$R/state/tasks/crash-task.md" <<'T'
id: crash-task
goal_id: goal-1
acceptance: true
status: queued
T
cat > "$TMP/crash.json" <<'J'
{"id":"decision-crash","idempotency_key":"crash-key","verb":"work","args":["crash-task"],"goal":"goal-1","wrong_if":"double launch"}
J
normalize_head_decision "$TMP/crash.json"
cat > "$R/scripts/work.sh" <<'STUB'
#!/usr/bin/env bash
printf 'launch\n' >> "$CRASH_LOG"
if [ ! -f "$CRASH_ONCE" ]; then
  : > "$CRASH_ONCE"
  kill -KILL "$PPID"
fi
STUB
chmod +x "$R/scripts/work.sh"; : > "$TMP/crash.log"
( cd "$R" && CRASH_LOG="$TMP/crash.log" CRASH_ONCE="$TMP/crashed" RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --file "$TMP/crash.json" ) >/dev/null 2>&1 || true
( cd "$R" && CRASH_LOG="$TMP/crash.log" CRASH_ONCE="$TMP/crashed" RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --file "$TMP/crash.json" ) >/dev/null 2>&1 || true
n="$(wc -l < "$TMP/crash.log" | tr -d ' ')"
[ "$n" = 1 ] && ok "post-dispatch crash recovery did not double-launch" \
             || no "post-dispatch crash recovery launched $n times"

# 3. Two simultaneous planners must reserve different task IDs and roadmap items atomically.
P="$TMP/planners"; mkdir -p "$P/scripts" "$P/state/tasks" "$P/state/roadmaps" "$TMP/plan-bin" "$TMP/arrivals"
cp "$SRC/scripts/plan.sh" "$P/scripts/"
cp "$SRC/scripts/repository_contract.py" "$P/scripts/"
cp "$SRC/scripts/runtime-state.py" "$P/scripts/"
cat > "$P/state/roadmaps/race.md" <<'RMAP'
engine: none
repo: /tmp/repo
workdir: .
acceptance: true

- [ ] first item
- [ ] second item
RMAP
REAL_LS="$(command -v ls)"
REAL_MKDIR="$(command -v mkdir)"
# Align fixed implementations immediately BEFORE lock acquisition. The old ls-only barrier ran
# after one planner already held the lock, so its peer could not arrive until the holder's
# arbitrary two-second timeout expired. Under post-baseline load that produced false one-task
# failures even though the serialized planner was correct.
cat > "$TMP/plan-bin/mkdir" <<STUB
#!/usr/bin/env bash
case "\$*" in *state/.locks/planner-race.lock)
  : > "$TMP/arrivals/lock-\$\$"
  for _ in \$(seq 1 100); do [ "\$(find '$TMP/arrivals' -name 'lock-*' -type f | wc -l)" -ge 2 ] && break; sleep 0.02; done ;;
esac
exec "$REAL_MKDIR" "\$@"
STUB
# Preserve the original vulnerable-read barrier for the pre-Phase 2 implementation, which has no
# planner lock. With the fixed implementation the lock directory exists, so this second barrier
# deliberately does not wait while the peer is correctly excluded.
cat > "$TMP/plan-bin/ls" <<STUB
#!/usr/bin/env bash
case "\$*" in *state/tasks/race-*)
  if [ ! -d "$P/state/.locks/planner-race.lock" ]; then
    : > "$TMP/arrivals/read-\$\$"
    for _ in \$(seq 1 100); do [ "\$(find '$TMP/arrivals' -name 'read-*' -type f | wc -l)" -ge 2 ] && break; sleep 0.02; done
  fi ;;
esac
exec "$REAL_LS" "\$@"
STUB
chmod +x "$TMP/plan-bin/ls" "$TMP/plan-bin/mkdir"
( cd "$P" && PATH="$TMP/plan-bin:$PATH" RECURSION_ROOT="$P" bash scripts/plan.sh race ) >"$TMP/p1" 2>&1 & p1=$!
( cd "$P" && PATH="$TMP/plan-bin:$PATH" RECURSION_ROOT="$P" bash scripts/plan.sh race ) >"$TMP/p2" 2>&1 & p2=$!
wait "$p1" 2>/dev/null || true; wait "$p2" 2>/dev/null || true
task_count="$(find "$P/state/tasks" -maxdepth 1 -name 'race-*.md' -type f | wc -l | tr -d ' ')"
reserved_count="$(grep -c '^- \[~\] ' "$P/state/roadmaps/race.md" || true)"
if [ "$task_count" = 2 ] && [ "$reserved_count" = 2 ]; then
  ok "simultaneous planners reserved two unique tasks and items"
else
  no "planner CAS missing (task_files=$task_count reserved_items=$reserved_count)"
fi

# 4. Task start must enforce an active parent goal and passed dependencies.
TROOT="$TMP/taskctl"; mkdir -p "$TROOT/scripts" "$TROOT/state/tasks" "$TROOT/state/goals"
cp "$SRC/scripts/taskctl.sh" "$TROOT/scripts/"
cp "$SRC/scripts/jsonl_durable.py" "$SRC/scripts/transition_receipt.py" "$SRC/scripts/assignment.py" \
  "$SRC/scripts/runtime-state.py" "$TROOT/scripts/"
stage_controller_closure "$TROOT"
python3 "$SRC/scripts/tests/staged-dependency-guard.py" "$SRC/scripts" "$TROOT/scripts" \
  || { no "taskctl fixture is missing a staged first-party dependency"; }
printf 'id: active\nstatus: active\n' > "$TROOT/state/goals/active.md"
printf 'id: blocked\nstatus: blocked\n' > "$TROOT/state/goals/blocked.md"
cat > "$TROOT/state/tasks/dep.md" <<'T'
id: dep
goal_id: active
status: queued
T
cat > "$TROOT/state/tasks/no-goal.md" <<'T'
id: no-goal
status: queued
T
cat > "$TROOT/state/tasks/bad-goal.md" <<'T'
id: bad-goal
goal_id: blocked
status: queued
T
cat > "$TROOT/state/tasks/unmet.md" <<'T'
id: unmet
goal_id: active
dependencies: dep
status: queued
T
invalid_started=0
for id in no-goal bad-goal unmet; do
  RECURSION_ROOT="$TROOT" bash "$TROOT/scripts/taskctl.sh" start "$id" test >/dev/null 2>&1
  rc=$?; st="$(sed -n 's/^status: *//p' "$TROOT/state/tasks/$id.md" | head -1)"
  [ "$rc" -eq 0 ] || [ "$st" = running ] && invalid_started=$((invalid_started+1))
done
[ "$invalid_started" = 0 ] && ok "task start enforced parent goal and dependencies" \
                           || no "$invalid_started invalid tasks entered running"

# 5. A contended state lock must fail closed, never time out and write unlocked.
LROOT="$TMP/lock"; mkdir -p "$LROOT/scripts" "$LROOT/state/.locks"
cp "$SRC/scripts/taskctl.sh" "$SRC/scripts/assignment.py" "$SRC/scripts/jsonl_durable.py" "$SRC/scripts/transition_receipt.py" \
  "$SRC/scripts/runtime-state.py" "$LROOT/scripts/"; mkdir "$LROOT/state/.locks/taskctl.lock"
stage_controller_closure "$LROOT"
python3 "$SRC/scripts/tests/staged-dependency-guard.py" "$SRC/scripts" "$LROOT/scripts" \
  || { no "lock fixture is missing a staged first-party dependency"; }
set +e
RECURSION_ROOT="$LROOT" timeout 20s bash "$LROOT/scripts/taskctl.sh" event probe '' locked \
  >"$TMP/lock.out" 2>&1; lock_rc=$?
set -e
if [ "$lock_rc" -ne 0 ] && [ ! -s "$LROOT/state/events.jsonl" ]; then
  ok "contended task-state lock failed closed"
else
  no "contended task-state lock proceeded unlocked (rc=$lock_rc event_written=$([ -s "$LROOT/state/events.jsonl" ] && echo yes || echo no))"
fi

# 6. A crash after the atomic state write must leave a complete task and one repairable event,
# never a torn projection or a second state transition.
AROOT="$TMP/atomic"; mkdir -p "$AROOT/scripts" "$AROOT/state/tasks" "$AROOT/state/goals"
cp "$SRC/scripts/taskctl.sh" "$AROOT/scripts/"
cp "$SRC/scripts/jsonl_durable.py" "$SRC/scripts/transition_receipt.py" "$SRC/scripts/assignment.py" \
  "$SRC/scripts/runtime-state.py" "$AROOT/scripts/"
stage_controller_closure "$AROOT"
python3 "$SRC/scripts/tests/staged-dependency-guard.py" "$SRC/scripts" "$AROOT/scripts" \
  || { no "atomic fixture is missing a staged first-party dependency"; }
printf 'id: g\nstatus: active\n' > "$AROOT/state/goals/g.md"
cat > "$AROOT/state/tasks/a.md" <<'T'
id: a
goal_id: g
status: queued

body that must survive
T
set +e
RECURSION_TRANSITION_FAILPOINT=state-write RECURSION_ROOT="$AROOT" \
  bash "$AROOT/scripts/taskctl.sh" start a test \
  >/dev/null 2>&1; atomic_rc=$?
set -e
RECURSION_ROOT="$AROOT" bash "$AROOT/scripts/taskctl.sh" event recovery-probe a repaired \
  >/dev/null 2>&1; repair_rc=$?
start_events="$(grep -c '"event":"start"' "$AROOT/state/events.jsonl" 2>/dev/null || true)"
if [ "$atomic_rc" -ne 0 ] && [ "$repair_rc" -eq 0 ] \
   && grep -q '^id: a$' "$AROOT/state/tasks/a.md" \
   && grep -q '^status: running$' "$AROOT/state/tasks/a.md" \
   && grep -q '^body that must survive$' "$AROOT/state/tasks/a.md" \
   && [ "$start_events" = 1 ]; then
  ok "interrupted state/event projection preserved one complete state and repaired one event"
else
  no "interrupted state/event projection was partial or unrecoverable (rc=$atomic_rc repair=$repair_rc starts=$start_events)"
fi

echo
[ "$fails" -eq 0 ] && { echo "hermes-pilot-phase2-red: ALL PASS"; exit 0; }
echo "hermes-pilot-phase2-red: $fails FAILED (expected on the Phase 0 pre-fix commit)"; exit 1

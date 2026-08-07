#!/usr/bin/env bash
# Phase 6 falsifiers: one event-driven measurable-goal loop, admitted and recovered through
# the existing durable decision/action/actuator path. Hermetic: no model, network, real
# publisher, notification, or live control-plane state.
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"
cleanup(){
  if [ "${PHASE6_KEEP_TMP:-0}" = 1 ]; then echo "PHASE6_TMP=$TMP" >&2
  else rm -rf "$TMP"; fi
}
trap cleanup EXIT

copy_controller(){
  local r="$1"
  mkdir -p "$r/scripts" "$r/state/tasks" "$r/state/goals" "$r/state/runs" \
    "$r/state/actions" "$r/state/deliveries" "$r/state/instructions" "$r/state/project-config" "$r/state/pilots" \
    "$r/state/decision-queue/pending" "$r/state/decision-queue/running" \
    "$r/state/decision-queue/succeeded" "$r/state/decision-queue/failed" \
    "$r/state/.locks" "$r/state/evidence" "$r/loop/logs"
  for s in conduct-hermes.sh decision-queue.py validate-decision.py validate-control-state.py \
           project-pilot.py project-reconcile.py taskctl.sh; do
    [ ! -f "$SRC/scripts/$s" ] || cp "$SRC/scripts/$s" "$r/scripts/"
  done
  chmod +x "$r/scripts/"* 2>/dev/null || true
  : > "$r/.env"; : > "$r/state/events.jsonl"; : > "$r/state/action-events.jsonl"
  : > "$r/state/decisions.jsonl"; : > "$r/state/INBOX.md"
}

make_repo(){
  local p="$1" origin="$2"
  mkdir -p "$p/app"
  git -c init.defaultBranch=main init -q --bare "$origin"
  git -c init.defaultBranch=main init -q "$p"
  printf 'seed\n' > "$p/app/seed.txt"
  git -C "$p" add -A
  git -C "$p" -c user.name=t -c user.email=t@t commit -qm base
  git -C "$p" remote add origin "$origin"
  git -C "$p" push -q -u origin main
}

write_registry(){
  local r="$1" p="$2" origin="$3" concurrency="${4:-1}"
  printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > "$r/state/portfolio.tsv"
  printf 'phase6\t%s\t%s\tmain\t-\t-\t61\tactive\n' "$p" "$origin" >> "$r/state/portfolio.tsv"
  cat > "$r/state/project-config/phase6.json" <<JSON
{"schema_version":1,"id":"phase6","repo":"$p","remote":"$origin","default_branch":"main","deploy_key_ref":"-","charter":"Bounded Phase 6 fixture only.","allowed_paths":["app"],"topic":61,"pilot_id":"pilot-phase6","activation_gate":"clone-auth-freshness-v1","notification_targets":["test"],"goal_source":"state/goals/phase6-goal.md","status":"active"}
JSON
  cat > "$r/state/pilots/pilot-phase6.json" <<JSON
{"schema_version":1,"id":"pilot-phase6","project_id":"phase6","topic":61,"charter":"Bounded Phase 6 fixture only.","model_policy":"project-pilot","concurrency_limit":$concurrency,"budget":{"max_inflight_workers":$concurrency},"notification_targets":["test"],"goal_source":"state/goals/phase6-goal.md","memory_key":"test:61","worktree_root":".worktrees/phase6","status":"active"}
JSON
}

write_goal(){ # root status budget-json
  local r="$1" status="$2" budget="$3"
  cat > "$r/state/goals/phase6-goal.md" <<G
schema_version: 1
version: 1
id: phase6-goal
project_id: phase6
status: $status
outcome: Produce the exact verified Phase 6 fixture.
acceptance_suite: test -s app/result.txt
falsifier: Exact commit evidence is absent or disagrees.
budget: $budget
started_at_epoch: $(date +%s)
terminal_reported: 0
G
}

write_task(){ # root id status attempts deps
  local r="$1" id="$2" status="$3" attempts="${4:-0}" deps="${5:-}"
  cat > "$r/state/tasks/$id.md" <<T
schema_version: 1
version: 1
id: $id
project_id: phase6
pilot_id: pilot-phase6
workstream: phase6
goal_id: phase6-goal
dependencies: $deps
goal: Produce the bounded Phase 6 fixture for $id.
engine: claude
repo: $(sed -n 's/^phase6\t\([^\t]*\).*/\1/p' "$r/state/portfolio.tsv")
acceptance: test -s app/result.txt
workdir: .
allowed_paths: app
non_goals: tests,fixtures,control-plane,merge,deploy
worker_class: claude
model_alias: sonnet-routine
verifier_model_alias: opus-review
deadline_seconds: 10
verifier_deadline_seconds: 10
network_policy: provider-only
evidence_contract: worker-result-v1
verification: independent
expected_change: required
gate_files:
autonomy: auto
status: $status
attempts: $attempts
lease_expires: 0
T
}

field(){ sed -n "s/^$2: *//p" "$1" | head -1 | tr -d '\r'; }
goal_status(){ field "$1/state/goals/phase6-goal.md" status; }
task_status(){ field "$1/state/tasks/$2.md" status; }
set_field(){
  local file="$1" key="$2" value="$3"
  if grep -q "^$key:" "$file"; then sed -i "s#^$key:.*#$key: $value#" "$file"
  else printf '%s: %s\n' "$key" "$value" >> "$file"; fi
}

install_stubs(){
  local r="$1"
  cat > "$r/scripts/capacity.sh" <<'SH'
#!/usr/bin/env bash
[ ! -f "$RECURSION_ROOT/state/test-capacity-deny" ]
SH
  cat > "$r/scripts/notify.sh" <<'SH'
#!/usr/bin/env bash
exit 0
SH
  cat > "$r/scripts/intake.sh" <<'SH'
#!/usr/bin/env bash
exit 0
SH
  cat > "$r/scripts/publish.sh" <<'SH'
#!/usr/bin/env bash
set -u
root="${RECURSION_ROOT:?}"; repo=""; branch=""
while [ $# -gt 0 ]; do case "$1" in --repo) repo="$2"; shift 2;; --branch) branch="$2"; shift 2;; *) shift;; esac; done
printf '%s\n' "$branch" >> "$root/state/publish-attempts"
[ ! -f "$root/state/test-publisher-fail" ] || exit 41
git -C "$repo" push -q origin "$branch:$branch"
SH
  cat > "$r/scripts/work.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root="${RECURSION_ROOT:?}"; id="${1:?}"; task="$root/state/tasks/$id.md"
printf '%s\n' "$id" >> "$root/state/worker-launches"
get(){ sed -n "s/^$1: *//p" "$task" | head -1; }
setv(){ if grep -q "^$1:" "$task"; then sed -i "s#^$1:.*#$1: $2#" "$task"; else printf '%s: %s\n' "$1" "$2" >> "$task"; fi; }
attempts="$(( ${RECURSION_STUB_ATTEMPTS:-$(get attempts)} + 1 ))"; setv attempts "$attempts"
if [ -f "$root/state/test-ambiguity" ]; then
  setv status blocked
  printf '{"schema_version":1,"id":"assist-%s","task_id":"%s","status":"open"}\n' "$id" "$id" > "$root/state/assist-$id.json"
  exit 0
fi
if [ -f "$root/state/test-gate-fail" ]; then setv status failed; exit 0; fi
repo="$(get repo)"; wt="$(mktemp -d)"; git -C "$repo" worktree add -q -b "loop/work/$id" "$wt" main
printf 'verified\n' > "$wt/app/result.txt"
git -C "$wt" add -A; git -C "$wt" -c user.name=t -c user.email=t@t commit -qm "$id"
oid="$(git -C "$wt" rev-parse HEAD)"; git -C "$repo" worktree remove --force "$wt"
setv candidate_commit "$oid"; setv review_status local; setv status passed
mkdir -p "$root/state/runs"
cat > "$root/state/runs/$id-impl.json" <<JSON
{"schema_version":1,"id":"$id-impl","task_id":"$id","worker":"implementer:test","role":"implementer","worktree":"fixture","base_commit":"$(git -C "$repo" rev-parse main)","pid":1,"process_group":1,"lease_expires":"0","deadline":"0","usage":{"tokens":10,"cost_usd":0.01},"result":{"status":"done"},"machine_gate":{"commit_oid":"$oid","exit_code":0},"verification":{"verifier_run_id":"$id-verify","commit_oid":"$oid","verdict":"pass"},"status":"succeeded"}
JSON
cat > "$root/state/runs/$id-verify.json" <<JSON
{"schema_version":1,"id":"$id-verify","task_id":"$id","worker":"verifier:test","role":"verifier","worktree":"fixture","base_commit":"$(git -C "$repo" rev-parse main)","pid":2,"process_group":2,"lease_expires":"0","deadline":"0","usage":{"tokens":5,"cost_usd":0.01},"result":{"verdict":"pass"},"verification":{"commit_oid":"$oid","implementer_run_id":"$id-impl","verdict":"pass"},"status":"succeeded"}
JSON
SH
  chmod +x "$r/scripts/"*.sh 2>/dev/null || true
}

setup(){ # name goal-status budget concurrency
  local name="$1" status="${2:-active}" budget="${3:-}" concurrency="${4:-1}"
  local r="$TMP/$name/controller" p="$TMP/$name/project" o="$TMP/$name/origin.git"
  copy_controller "$r"; make_repo "$p" "$o"; write_registry "$r" "$p" "$o" "$concurrency"
  [ -n "$budget" ] || budget='{"max_concurrency":1,"max_tokens":1000,"max_cost_usd":5,"max_wall_clock_seconds":3600,"max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":1,"publication_required":false}'
  write_goal "$r" "$status" "$budget"; install_stubs "$r"
  printf '%s\n' "$r"
}

schedule(){
  local r="$1"
  [ -x "$r/scripts/project-reconcile.py" ] || return 127
  RECURSION_ROOT="$r" python3 "$r/scripts/project-reconcile.py" schedule --project phase6 --goal phase6-goal >/dev/null 2>&1
}
drain(){ RECURSION_ROOT="$1" RECURSION_NO_NOTIFY=1 bash "$1/scripts/conduct-hermes.sh" >/dev/null 2>&1; }
tick(){ local r="$1"; schedule "$r" || return $?; drain "$r" || true; }
ticks(){ local r="$1" n="$2" i; for i in $(seq 1 "$n"); do tick "$r" || true; done; }
action_count(){
  local r="$1" verb="$2"
  python3 - "$r/state/actions" "$verb" <<'PY'
import glob,json,sys
n=0
for path in glob.glob(sys.argv[1]+'/*.json'):
    try: row=json.load(open(path))
    except Exception: continue
    n += row.get('verb') == sys.argv[2]
print(n)
PY
}
launch_count(){ [ -f "$1/state/worker-launches" ] && wc -l < "$1/state/worker-launches" || echo 0; }

# 1. Full success: proposed -> ready -> work -> exact-commit goal verification -> achieved.
R="$(setup success)"; write_task "$R" success-task proposed 0
ticks "$R" 8
loop_live=0; [ "$(action_count "$R" work)" -gt 0 ] && loop_live=1
if [ "$(goal_status "$R")" = achieved ] && [ "$(task_status "$R" success-task)" = passed ] \
   && [ "$(action_count "$R" work)" = 1 ] \
   && python3 - "$R/state/evidence/phase6-goal.json" <<'PY'
import json,sys
try: row=json.load(open(sys.argv[1]))
except Exception: raise SystemExit(1)
raise SystemExit(0 if row.get('verdict')=='pass' and row.get('commit_oid') and row.get('independent_verifier') else 1)
PY
then ok "successful goal reconciled through exact-commit acceptance and independent verification"
else no "successful goal did not reach achieved through the exact evidence chain"; fi

# 2. Machine-gate failure gets one durable retry and no unbounded third launch.
R="$(setup gate-failure)"; write_task "$R" gate-task ready 0; touch "$R/state/test-gate-fail"
ticks "$R" 8
launches="$(launch_count "$R")"
if [ "$loop_live" = 1 ] && [ "$launches" = 2 ] && [ "$(goal_status "$R")" = budget-exhausted ]; then
  ok "machine-gate failure retried only within the configured bound"
else no "machine-gate failure was not bounded (launches=$launches goal=$(goal_status "$R"))"; fi

# 3. An ambiguity/assist stops the goal and repeated ticks do not execute it twice.
R="$(setup ambiguity)"; write_task "$R" assist-task ready 0; touch "$R/state/test-ambiguity"
ticks "$R" 8; before="$(launch_count "$R")"; ticks "$R" 3
after="$(launch_count "$R")"
if [ "$loop_live" = 1 ] && [ "$before" = 1 ] && [ "$after" = 1 ] && [ "$(task_status "$R" assist-task)" = blocked ] \
   && [ -f "$R/state/assist-assist-task.json" ]; then
  ok "ambiguity opened one assist without duplicate execution"
else no "ambiguity/assist duplicated or disappeared (before=$before after=$after)"; fi

# 4. A goal-wide failure budget is distinct from one task's retry bound.
B='{"max_concurrency":2,"max_tokens":1000,"max_cost_usd":5,"max_wall_clock_seconds":3600,"max_task_attempts":3,"max_failures":1,"max_review_queue":2,"max_publish_attempts":1,"publication_required":false}'
R="$(setup failure-budget active "$B" 2)"; write_task "$R" fail-a failed 1; write_task "$R" fail-b failed 1
ticks "$R" 3
[ "$loop_live" = 1 ] && [ "$(goal_status "$R")" = budget-exhausted ] \
  && ok "retry and failure-budget exhaustion stop the goal deterministically" \
  || no "failure budget did not stop the goal (status=$(goal_status "$R"))"

# 5. PAUSE admits no reconcile/dispatch; Phase 1 already supplies the in-flight kill proof.
R="$(setup paused)"; write_task "$R" pause-task ready 0; touch "$R/state/PAUSE"; ticks "$R" 3
if [ "$loop_live" = 1 ] && [ "$(action_count "$R" work)" = 0 ] && [ ! -s "$R/state/publish-attempts" ]; then
  ok "PAUSE prevents gates, publication, and new Phase 6 dispatch"
else no "PAUSE allowed Phase 6 execution or publication"; fi

# 6. Crash/reboot recovery reconciles a dead lease once before any relaunch.
R="$(setup recovery)"; write_task "$R" crash-task running 1
set_field "$R/state/tasks/crash-task.md" lease_expires 1
cat > "$R/state/runs/crash-task-impl.json" <<'JSON'
{"schema_version":1,"id":"crash-task-impl","task_id":"crash-task","worker":"implementer:test","role":"implementer","worktree":"missing","base_commit":"0000000000000000000000000000000000000000","pid":999999,"process_group":999999,"lease_expires":"1","deadline":"1","usage":{},"result":{},"status":"running"}
JSON
ticks "$R" 8
launches="$(launch_count "$R")"
if [ "$loop_live" = 1 ] && [ "$launches" -le 1 ] && grep -q 'recovery' "$R/state/events.jsonl" 2>/dev/null; then
  ok "process crash and host-reboot recovery do not duplicate launches"
else no "crash/reboot recovery duplicated or lacked evidence (launches=$launches)"; fi

# 7. A stale default base is blocked before work.
R="$(setup stale-base)"; write_task "$R" stale-task ready 0
P="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["repo"])' "$R/state/project-config/phase6.json")"
O="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["remote"])' "$R/state/project-config/phase6.json")"
W="$TMP/stale-writer"; git clone -q "$O" "$W"; printf later > "$W/app/later.txt"; git -C "$W" add -A
git -C "$W" -c user.name=t -c user.email=t@t commit -qm later; git -C "$W" push -q origin main
ticks "$R" 4
if [ "$loop_live" = 1 ] && [ "$(action_count "$R" work)" = 0 ] && [ "$(goal_status "$R")" = blocked ]; then
  ok "stale base blocks dispatch with terminal evidence"
else no "stale base reached a worker or stayed ambiguous"; fi

# 8. Publisher failure is durable, bounded, and cannot be mistaken for achievement.
B='{"max_concurrency":1,"max_tokens":1000,"max_cost_usd":5,"max_wall_clock_seconds":3600,"max_task_attempts":2,"max_failures":1,"max_review_queue":2,"max_publish_attempts":1,"publication_required":true}'
R="$(setup publisher-failure active "$B")"; write_task "$R" pub-task ready 0; touch "$R/state/test-publisher-fail"
ticks "$R" 10
if [ "$loop_live" = 1 ] && [ "$(action_count "$R" publish-task)" = 1 ] && [ "$(goal_status "$R")" != achieved ]; then
  ok "publisher failure is bounded and prevents goal achievement"
else no "publisher failure was lost or retried without bound"; fi

# 9. A verifier disagreement on the exact candidate blocks the goal.
R="$(setup verifier-disagreement)"; write_task "$R" disagree-task ready 0; ticks "$R" 3
[ ! -f "$R/state/runs/disagree-task-verify.json" ] || python3 - "$R/state/runs/disagree-task-verify.json" <<'PY'
import json,sys
p=sys.argv[1]; row=json.load(open(p)); row['verification']['verdict']='fail'; row['result']['verdict']='fail';
open(p,'w').write(json.dumps(row)+'\n')
PY
ticks "$R" 5
if [ "$loop_live" = 1 ] && [ "$(goal_status "$R")" = blocked ]; then ok "verifier disagreement fails closed"
else no "verifier disagreement did not block the goal"; fi

# 10. Every admission budget is enforced before another work action is queued.
budget_case(){
  local name="$1" budget="$2" setup_hook="$3"
  local r; r="$(setup "budget-$name" active "$budget" 2)"; write_task "$r" "$name-task" ready 0
  eval "$setup_hook"; ticks "$r" 4
  [ "$loop_live" = 1 ] && [ "$(action_count "$r" work)" = 0 ]
}
B0='{"max_concurrency":0,"max_tokens":1000,"max_cost_usd":5,"max_wall_clock_seconds":3600,"max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":1,"publication_required":false}'
budget_case concurrency "$B0" ':' && ok "per-goal concurrency budget is enforced" || no "concurrency budget admitted work"
B1='{"max_concurrency":1,"max_tokens":5,"max_cost_usd":5,"max_wall_clock_seconds":3600,"max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":1,"publication_required":false}'
budget_case tokens "$B1" 'mkdir -p "$r/state/runs"; printf "{\"schema_version\":1,\"id\":\"used\",\"task_id\":\"tokens-task\",\"worker\":\"x\",\"worktree\":\"x\",\"base_commit\":\"0000000000000000000000000000000000000000\",\"pid\":1,\"lease_expires\":\"0\",\"deadline\":\"0\",\"usage\":{\"tokens\":6},\"result\":{},\"status\":\"succeeded\"}\n" > "$r/state/runs/used.json"' \
  && ok "per-goal token budget is enforced" || no "token budget admitted work"
B2='{"max_concurrency":1,"max_tokens":1000,"max_cost_usd":0.01,"max_wall_clock_seconds":3600,"max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":1,"publication_required":false}'
budget_case cost "$B2" 'mkdir -p "$r/state/runs"; printf "{\"schema_version\":1,\"id\":\"used\",\"task_id\":\"cost-task\",\"worker\":\"x\",\"worktree\":\"x\",\"base_commit\":\"0000000000000000000000000000000000000000\",\"pid\":1,\"lease_expires\":\"0\",\"deadline\":\"0\",\"usage\":{\"cost_usd\":0.02},\"result\":{},\"status\":\"succeeded\"}\n" > "$r/state/runs/used.json"' \
  && ok "per-goal cost budget is enforced" || no "cost budget admitted work"
B3='{"max_concurrency":1,"max_tokens":1000,"max_cost_usd":5,"max_wall_clock_seconds":1,"max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":1,"publication_required":false}'
budget_case wall "$B3" 'set_field "$r/state/goals/phase6-goal.md" started_at_epoch 1' \
  && ok "per-goal wall-clock budget is enforced" || no "wall-clock budget admitted work"

# 11. Review-queue backpressure blocks unlimited new generation.
B='{"max_concurrency":2,"max_tokens":1000,"max_cost_usd":5,"max_wall_clock_seconds":3600,"max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":1,"publication_required":true}'
R="$(setup review-pressure active "$B" 2)"; write_task "$R" review-one passed 1; set_field "$R/state/tasks/review-one.md" review_status published
write_task "$R" review-two ready 0; ticks "$R" 4
[ "$loop_live" = 1 ] && [ "$(action_count "$R" work)" = 0 ] \
  && ok "review-queue backpressure prevents unlimited new work" \
  || no "review backlog did not stop new work"

# 12. All terminal/paused goal states are stable and dispatch-closed.
terminal_ok=1
for st in achieved blocked abandoned budget-exhausted paused; do
  R="$(setup "terminal-$st" "$st")"; write_task "$R" "$st-task" ready 0; ticks "$R" 3
  [ "$(goal_status "$R")" = "$st" ] && [ "$(action_count "$R" work)" = 0 ] || terminal_ok=0
done
[ "$loop_live" = 1 ] && [ "$terminal_ok" = 1 ] && ok "achieved, blocked, abandoned, budget-exhausted, and paused are deterministic" \
  || no "one or more terminal goal states reopened or dispatched"

# 13. Recovery reconciles every named truth source and does not redeliver.
R="$(setup recovery-sources)"; write_task "$R" recovery-task stale 1
mkdir -p "$R/state/deliveries"; printf '{"schema_version":1,"id":"delivery-1","event_id":"event-1","destination":"test","attempt":1,"acknowledgement":"ok","status":"succeeded"}\n' > "$R/state/deliveries/delivery-1.json"
mkdir -p "$R/.worktrees/orphan"; git -C "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["repo"])' "$R/state/project-config/phase6.json")" branch loop/work/orphan >/dev/null
ticks "$R" 4
deliveries="$(find "$R/state/deliveries" -type f | wc -l)"
if [ "$loop_live" = 1 ] && grep -q 'recovery-reconciled' "$R/state/events.jsonl" 2>/dev/null && [ "$deliveries" = 1 ]; then
  ok "recovery reconciles task/process/worktree/ref/event/delivery truth without duplicate delivery"
else no "recovery reconciliation omitted a truth source or duplicated delivery"; fi

# 14. A real pilot-task-create action loses once verifying begins, then succeeds only after
# failed exact-commit verification evidence reopens the goal.
pilot_task_decision(){ # root instruction-id task-id file
  local r="$1" iid="$2" tid="$3" file="$4"
  printf 'schema_version: 1\nid: %s\nprincipal: test\ntopic: 61\nproject_id: phase6\npilot_id: pilot-phase6\nstatus: open\n' "$iid" > "$r/state/instructions/$(printf '%08d' "$iid").md"
  cat > "$file" <<JSON
{"schema_version":1,"id":"decision-$iid","actor":"pilot-phase6","verb":"pilot-task-create","args":["phase6","phase6-goal","$tid","app"],"project":"phase6","goal":"phase6-goal","why":"bounded task creation control","wrong_if":"goal state changed","text":"Create one bounded verification follow-up.","instruction_id":"$iid","idempotency_key":"phase6-create-$iid"}
JSON
}
R="$(setup verifying)"; write_task "$R" verify-task ready 0; ticks "$R" 2
before="$(find "$R/state/tasks" -type f | wc -l)"
pilot_task_decision "$R" 14 forbidden-task "$R/forbidden.json"
RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 bash "$R/scripts/conduct-hermes.sh" --file "$R/forbidden.json" >/dev/null 2>&1 || true
mid="$(find "$R/state/tasks" -type f | wc -l)"
cat > "$R/state/evidence/phase6-goal.json" <<'JSON'
{"schema_version":1,"id":"goal-evidence-phase6-goal","project_id":"phase6","goal_id":"phase6-goal","verdict":"fail","reason":"controlled falsifier","commit_oid":"0000000000000000000000000000000000000000"}
JSON
ticks "$R" 1
pilot_task_decision "$R" 15 reopened-task "$R/reopened.json"
RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 bash "$R/scripts/conduct-hermes.sh" --file "$R/reopened.json" >/dev/null 2>&1 || true
after="$(find "$R/state/tasks" -type f | wc -l)"
if [ "$loop_live" = 1 ] && [ "$before" = "$mid" ] && [ "$after" = "$((before + 1))" ] \
   && [ "$(goal_status "$R")" = active ] && [ -f "$R/state/tasks/reopened-task.md" ]; then
  ok "verifying refuses task creation until failed verification evidence reopens the goal"
else no "task creation crossed verifying or failed to require reopen evidence (before=$before mid=$mid after=$after goal=$(goal_status "$R"))"; fi

# 15. Non-vacuous stop proof: active launches once, then achieved ticks launch zero.
R="$(setup achieved-stop)"; write_task "$R" stop-task ready 0; ticks "$R" 8
before="$(action_count "$R" work)"; ticks "$R" 5; after="$(action_count "$R" work)"
if [ "$before" = 1 ] && [ "$after" = 1 ] && [ "$(goal_status "$R")" = achieved ]; then
  ok "repeated scheduler ticks launch zero workers after achieved"
else no "achieved was vacuous or relaunched work (before=$before after=$after)"; fi

echo
[ "$fails" -eq 0 ] && { echo "hermes-pilot-phase6-red: ALL PASS"; exit 0; }
echo "hermes-pilot-phase6-red: $fails FAILED (expected on the pre-Phase 6 base)"; exit 1

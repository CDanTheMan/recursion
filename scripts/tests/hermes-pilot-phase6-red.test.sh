#!/usr/bin/env bash
# Phase 6 falsifiers: one event-driven measurable-goal loop, admitted and recovered through
# the existing durable decision/action/actuator path. Hermetic: no model, network, real
# publisher, notification, or live control-plane state.
set -uo pipefail
export LC_ALL=C
export RECURSION_TEST_WORKER=logical
export RECURSION_TEST_PROVIDER_NETWORK=logical
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
    "$r/state/actions" "$r/state/deliveries" "$r/state/instructions" "$r/state/assists" "$r/state/project-config" "$r/state/pilots" \
    "$r/state/decision-queue/pending" "$r/state/decision-queue/running" \
    "$r/state/decision-queue/succeeded" "$r/state/decision-queue/failed" \
    "$r/state/.locks" "$r/state/evidence" "$r/loop/logs"
  for s in assignment.py assist.sh author.sh board.sh branch-review.sh capacity.sh conduct-hermes.sh conduct.sh \
           decision-queue.py engine_contract.py git-scope.py hermes-decide.sh instruction_routing.py intake.sh \
           jsonl_durable.py notification-outbox.py notify.sh pilot_instruction.py plan.sh project-pilot.py \
           project-reconcile.py project_authority.py provider-connect-proxy.py provider_contract.py provider-network.sh provider-egress.py publish.sh \
           remote_evidence.py resolve-engine.py resolve-model-alias.py resync.sh run_contract.py runtime-state.py \
           seed_contract.py taskctl.sh transition_receipt.py validate-assignment-result.py validate-control-state.py \
           validate-decision.py validate-gate.py validate-verifier-result.py validate-worker-result.py work.sh assignment-token.py \
           worker-evidence.py worker-sandbox.sh; do
    [ ! -f "$SRC/scripts/$s" ] || cp "$SRC/scripts/$s" "$r/scripts/"
  done
  [ ! -f "$SRC/scripts/seed_contract.py" ] || cp "$SRC/scripts/seed_contract.py" "$r/scripts/"
  python3 "$SRC/scripts/tests/staged-dependency-guard.py" "$SRC/scripts" "$r/scripts" \
    || { no "phase 6 controller fixture is missing a staged first-party dependency"; }
  chmod +x "$r/scripts/"* 2>/dev/null || true
  if ! python3 -c 'import fcntl' >/dev/null 2>&1; then
    cat > "$r/scripts/fcntl.py" <<'PY'
LOCK_EX=2
LOCK_NB=4
def flock(_file, _flags):
    return None
PY
  fi
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
  python3 - "$file" "$key" "$value" <<'PY'
import sys
from pathlib import Path

path, key, value = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
lines = path.read_text(encoding="utf-8").splitlines()
replacement = f"{key}: {value}"
for index, line in enumerate(lines):
    if line.startswith(f"{key}:"):
        lines[index] = replacement
        break
else:
    lines.append(replacement)
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
}

install_stubs(){
  local r="$1"
  cat > "$r/scripts/capacity.sh" <<'SH'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$RECURSION_ROOT/state/capacity-calls"
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
printf '%s\n' "$id" > "$wt/app/result.txt"
git -C "$wt" add -A; git -C "$wt" -c user.name=t -c user.email=t@t commit -qm "$id"
oid="$(git -C "$wt" rev-parse HEAD)"; git -C "$repo" worktree remove --force "$wt"
setv candidate_commit "$oid"; setv review_status local; setv status passed
mkdir -p "$root/state/runs"
cat > "$root/state/runs/$id-impl.json" <<JSON
{"schema_version":1,"id":"$id-impl","task_id":"$id","worker":"implementer:test","role":"implementer","worktree":"fixture","base_commit":"$(git -C "$repo" rev-parse main)","pid":1,"process_group":1,"lease_expires":"0","deadline":"0","usage":{"tokens":10,"cost_usd":0.01},"result":{"status":"done"},"seed_evidence":{"manifest_sha256":"$(get seed_manifest_sha256)","content_sha256":"$(get seed_digest)","verified_before":true,"verified_after":true},"machine_gate":{"commit_oid":"$oid","exit_code":0},"verification":{"verifier_run_id":"$id-verify","commit_oid":"$oid","verdict":"pass"},"status":"succeeded"}
JSON
cat > "$root/state/runs/$id-verify.json" <<JSON
{"schema_version":1,"id":"$id-verify","task_id":"$id","worker":"verifier:test","role":"verifier","worktree":"fixture","base_commit":"$(git -C "$repo" rev-parse main)","pid":2,"process_group":2,"lease_expires":"0","deadline":"0","usage":{"tokens":5,"cost_usd":0.01},"result":{"verdict":"pass"},"seed_evidence":{"manifest_sha256":"$(get seed_manifest_sha256)","content_sha256":"$(get seed_digest)","verified_before":true,"verified_after":true},"verification":{"commit_oid":"$oid","implementer_run_id":"$id-impl","verdict":"pass"},"status":"succeeded"}
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
install_seed(){ # controller-root task-id
  local r="$1" task="$2" repo contract manifest digest
  repo="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["repo"])' "$r/state/project-config/phase6.json")"
  mkdir -p "$repo/data/corpus"
  printf 'immutable goal oracle\n' > "$repo/data/corpus/oracle.bin"
  printf '/data/corpus/\n' > "$repo/.gitignore"
  printf 'data/corpus\n' > "$repo/.seedlist"
  git -C "$repo" add .gitignore .seedlist
  git -C "$repo" -c user.name=t -c user.email=t@t commit -qm 'seed contract'
  git -C "$repo" push -q origin main
  contract="$(python3 "$r/scripts/seed_contract.py" inspect --repo "$repo")"
  manifest="$(python3 -c 'import json,sys;print(json.loads(sys.argv[1])["manifest_sha256"])' "$contract")"
  digest="$(python3 -c 'import json,sys;print(json.loads(sys.argv[1])["content_sha256"])' "$contract")"
  for file in "$r/state/goals/phase6-goal.md" "$r/state/tasks/$task.md"; do
    set_field "$file" seed_manifest .seedlist
    set_field "$file" seed_manifest_sha256 "$manifest"
    set_field "$file" seed data/corpus
    set_field "$file" seed_digest "$digest"
  done
  printf '%s\n' "$digest"
}

# 1. Full success: proposed -> ready -> work -> exact-commit goal verification -> achieved.
R="$(setup success)"; write_task "$R" success-task proposed 0
ticks "$R" 8
loop_live=0; [ "$(action_count "$R" work)" -gt 0 ] && loop_live=1
M="$(setup success-mutating-gate)"; write_task "$M" mutation-task proposed 0
set_field "$M/state/goals/phase6-goal.md" acceptance_suite "printf mutation > app/gate-mutation.txt"
ticks "$M" 8
mutation_closed=0
if [ "$(goal_status "$M")" = active ] && [ "$(launch_count "$M")" = 1 ] \
   && python3 - "$M/state/evidence/phase6-goal.json" "$M/state/evidence/history" <<'PY'
import glob,json,sys
try: current=json.load(open(sys.argv[1]))
except Exception: raise SystemExit(1)
rows=[]
for path in glob.glob(sys.argv[2]+'/phase6-goal-reopen-v*-fail.json'):
    try: rows.append(json.load(open(path)))
    except Exception: pass
ok=(current.get('verdict')=='consumed' and current.get('source_verdict')=='fail'
    and current.get('consumed_task_ids')==['mutation-task'] and len(rows)==1
    and rows[0].get('verdict')=='fail' and rows[0].get('exit_code') != 0)
raise SystemExit(0 if ok else 1)
PY
then mutation_closed=1; fi

# A consumed verdict must hold this exact task graph open for remediation rather than bounce.
# Once one stacked follow-up changes that graph, a clean exact-commit gate may close the goal.
mutation_oid="$(field "$M/state/tasks/mutation-task.md" candidate_commit)"
mutation_repo="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["repo"])' "$M/state/project-config/phase6.json")"
mutation_origin="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["remote"])' "$M/state/project-config/phase6.json")"
git -C "$mutation_repo" checkout -q main
git -C "$mutation_repo" merge -q --ff-only "$mutation_oid"
git -C "$mutation_repo" push -q "$mutation_origin" main
mutation_review_rc=0
RECURSION_ROOT="$M" python3 "$M/scripts/project-reconcile.py" accept-review \
  phase6 phase6-goal mutation-task "$mutation_oid" lucas \
  >"$M/state/mutation-review.out" 2>&1 || mutation_review_rc=$?
set_field "$M/state/goals/phase6-goal.md" acceptance_suite "test -s app/result.txt"
write_task "$M" remediation-task proposed 0 mutation-task
ticks "$M" 8
remediation_clean=0
if [ "$mutation_review_rc" = 0 ] \
   && [ "$(field "$M/state/tasks/mutation-task.md" review_status)" = accepted ] \
   && [ "$(goal_status "$M")" = achieved ] && [ "$(launch_count "$M")" = 2 ] \
   && [ "$(grep -c '"event":"goal-transition"' "$M/state/events.jsonl" 2>/dev/null || true)" = 4 ] \
   && [ "$(grep -c '"event":"goal-terminal"' "$M/state/events.jsonl" 2>/dev/null || true)" = 1 ]; then
  remediation_clean=1
fi
if [ "$(goal_status "$R")" = achieved ] && [ "$(task_status "$R" success-task)" = passed ] \
   && [ "$(action_count "$R" work)" = 1 ] \
   && [ "$mutation_closed" = 1 ] && [ "$remediation_clean" = 1 ] \
   && python3 - "$R/state/evidence/phase6-goal.json" <<'PY'
import json,sys
try: row=json.load(open(sys.argv[1]))
except Exception: raise SystemExit(1)
raise SystemExit(0 if row.get('verdict')=='pass' and row.get('commit_oid') and row.get('independent_verifier') else 1)
PY
then ok "dirty verification reopens once and a stacked clean remediation closes exactly"
else
  printf '      mutation_closed=%s review_rc=%s review_status=%s remediation_status=%s goal_status=%s launches=%s\n' \
    "$mutation_closed" "$mutation_review_rc" \
    "$(field "$M/state/tasks/mutation-task.md" review_status)" \
    "$(task_status "$M" remediation-task)" "$(goal_status "$M")" "$(launch_count "$M")" >&2
  if [ -s "$M/state/mutation-review.out" ]; then
    sed 's/^/      accept-review: /' "$M/state/mutation-review.out" >&2
  fi
  no "exact goal verification accepted failure or rejected clean success"
fi

# 1b. Exact-commit goal verification receives the same approved ignored corpus, protects it,
# records before/after digest evidence, and serializes a declared heavy gate.
R="$(setup seeded-goal)"; write_task "$R" seeded-task proposed 0
SEED_DIGEST="$(install_seed "$R" seeded-task)"
set_field "$R/state/goals/phase6-goal.md" acceptance_suite \
  "test -s app/result.txt && test -s data/corpus/oracle.bin"
set_field "$R/state/goals/phase6-goal.md" gate_class heavy
set_field "$R/state/tasks/seeded-task.md" gate_class heavy
ticks "$R" 8
if [ "$(goal_status "$R")" = achieved ] \
   && grep -q '^heavy acquire goal-phase6-goal$' "$R/state/capacity-calls" \
   && grep -q '^heavy release$' "$R/state/capacity-calls" \
   && python3 - "$R/state/evidence/phase6-goal.json" "$SEED_DIGEST" <<'PY'
import json,sys
row=json.load(open(sys.argv[1])); seed=row.get('seed_evidence',{})
valid=(row.get('verdict')=='pass' and row.get('gate_class')=='heavy'
       and seed.get('content_sha256')==sys.argv[2]
       and seed.get('verified_before') is True and seed.get('verified_after') is True)
raise SystemExit(0 if valid else 1)
PY
then
  ok "heavy exact-commit goal gate receives and records the approved ignored seed"
else
  no "goal verification omitted seed evidence, post-gate integrity, or heavy exclusivity"
fi

# Source drift after work passed is not silently re-baselined by exact-commit verification.
R="$(setup seed-drift)"; write_task "$R" drift-task proposed 0
install_seed "$R" drift-task >/dev/null
set_field "$R/state/goals/phase6-goal.md" acceptance_suite \
  "test -s app/result.txt && test -s data/corpus/oracle.bin"
for _ in $(seq 1 12); do
  tick "$R" || true
  [ "$(goal_status "$R")" != verifying ] || break
done
repo="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["repo"])' "$R/state/project-config/phase6.json")"
printf 'drifted after task pass\n' > "$repo/data/corpus/oracle.bin"
tick "$R" || true
if python3 - "$R/state/evidence/phase6-goal.json" <<'PY'
import json,sys
row=json.load(open(sys.argv[1]))
raise SystemExit(0 if row.get('verdict')=='fail' and str(row.get('reason','')).startswith('seed-contract:') else 1)
PY
then
  ok "goal verification refuses seed drift instead of deriving a new trusted digest"
else
  no "changed seed bytes were silently accepted or left no durable goal evidence"
fi

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

# 11b. Only Lucas's local exact-commit acceptance releases that backpressure.
B='{"max_concurrency":2,"max_tokens":1000,"max_cost_usd":5,"max_wall_clock_seconds":3600,"max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":1,"publication_required":false}'
R="$(setup review-release active "$B" 2)"; write_task "$R" review-a ready 0; write_task "$R" review-b ready 0
ticks "$R" 5
oid="$(field "$R/state/tasks/review-a.md" candidate_commit)"
wrong=0; exact=0
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" accept-review \
  phase6 phase6-goal review-a "$oid" automation >/dev/null 2>&1 || wrong=$?
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" accept-review \
  phase6 phase6-goal review-a "$oid" lucas >/dev/null 2>&1 || exact=$?
ticks "$R" 5
if [ "$loop_live" = 1 ] && [ "$wrong" != 0 ] && [ "$exact" = 0 ] \
   && [ "$(field "$R/state/tasks/review-a.md" review_status)" = accepted ] \
   && [ -f "$R/state/evidence/review-review-a.json" ] \
   && [ "$(action_count "$R" work)" = 2 ]; then
  ok "Lucas exact-commit acceptance durably releases review backpressure"
else
  no "review acceptance authority/evidence did not release exactly one bounded slot"
fi

# 12. All terminal/paused goal states are stable and dispatch-closed.
terminal_ok=1
for st in achieved blocked abandoned budget-exhausted paused; do
  R="$(setup "terminal-$st" "$st")"; write_task "$R" "$st-task" ready 0; ticks "$R" 3
  [ "$(goal_status "$R")" = "$st" ] && [ "$(action_count "$R" work)" = 0 ] || terminal_ok=0
done
[ "$loop_live" = 1 ] && [ "$terminal_ok" = 1 ] && ok "achieved, blocked, abandoned, budget-exhausted, and paused are deterministic" \
  || no "one or more terminal goal states reopened or dispatched"

# 12b. Explicit review acceptance survives the normal merge-then-prune remote workflow.
B='{"max_concurrency":1,"max_tokens":1000,"max_cost_usd":5,"max_wall_clock_seconds":3600,"max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":2,"publication_required":true}'
R="$(setup review-merge-prune active "$B")"; write_task "$R" merged-review ready 0; ticks "$R" 8
repo="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["repo"])' "$R/state/project-config/phase6.json")"
origin="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["remote"])' "$R/state/project-config/phase6.json")"
oid="$(field "$R/state/tasks/merged-review.md" candidate_commit)"
git -C "$repo" checkout -q main
git -C "$repo" merge -q --ff-only "loop/work/merged-review"
git -C "$repo" push -q "$origin" main
git -C "$repo" push -q "$origin" :"loop/work/merged-review"
git -C "$repo" branch -D "loop/work/merged-review" >/dev/null
hostile_cwd="$TMP/review-merge-prune-hostile-cwd"
mkdir -p "$hostile_cwd"
printf 'gitdir: /definitely/absent/ambient-gitdir\n' > "$hostile_cwd/.git"
merged_accept_rc=0
( cd "$hostile_cwd" && RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" accept-review \
  phase6 phase6-goal merged-review "$oid" lucas >/dev/null 2>&1 ) || merged_accept_rc=$?
proof_kind="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["review_proof"]["kind"])' "$R/state/evidence/review-merged-review.json" 2>/dev/null)"
if [ "$merged_accept_rc" = 0 ] && [ "$proof_kind" = remote-default-ancestor ] \
   && [ "$(field "$R/state/tasks/merged-review.md" review_status)" = accepted ]; then
  ok "explicit exact-commit review accepts a fetched merge proof after review-ref pruning"
else
  no "merge-then-prune workflow could not release explicit human review backpressure"
fi

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
{"schema_version":1,"id":"decision-$iid","actor":"pilot-phase6","verb":"pilot-task-create","args":["phase6","phase6-goal","$tid","app"],"project":"phase6","goal":"phase6-goal","why":"bounded task creation control","wrong_if":"goal state changed","text":"Create one bounded verification follow-up.","instruction_id":"$iid","idempotency_key":"phase6-create-$iid","decision_source":"hermes-model","routed_decider":"pilot-phase6"}
JSON
  RECURSION_ROOT="$r" python3 "$r/scripts/decision-queue.py" normalize < "$file" > "$file.normalized"
  mv -f "$file.normalized" "$file"
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

# 16. A mutation-backed terminal receipt committed before its event append is resumed, not
# re-created as a colliding pure event. The exact operation and its replay both return success.
R="$(setup terminal-event-repair verifying)"
terminal_crash_rc=0; terminal_resume_rc=0; terminal_replay_rc=0
RECURSION_ROOT="$R" RECURSION_TRANSITION_FAILPOINT=state-write \
  python3 "$R/scripts/project-reconcile.py" transition-goal \
  phase6 phase6-goal verifying achieved exact-commit-verified >/dev/null 2>&1 || terminal_crash_rc=$?
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" transition-goal \
  phase6 phase6-goal verifying achieved exact-commit-verified >/dev/null 2>&1 || terminal_resume_rc=$?
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" transition-goal \
  phase6 phase6-goal verifying achieved exact-commit-verified >/dev/null 2>&1 || terminal_replay_rc=$?
terminal_transition_count="$(grep -c '"event":"goal-transition"' "$R/state/events.jsonl" 2>/dev/null || true)"
terminal_event_count="$(grep -c '"event":"goal-terminal"' "$R/state/events.jsonl" 2>/dev/null || true)"
if [ "$terminal_crash_rc" != 0 ] && [ "$terminal_resume_rc" = 0 ] && [ "$terminal_replay_rc" = 0 ] \
   && [ "$(goal_status "$R")" = achieved ] \
   && [ "$terminal_transition_count" = 1 ] && [ "$terminal_event_count" = 1 ]; then
  ok "mutation-backed terminal receipt resumes and replays exactly once"
else
  no "terminal receipt collided, failed replay, or lost/duplicated report events"
fi

# 17. PAUSE evidence is a controlled reopen verdict, not a permanent verifying wedge.
R="$(setup paused-verification verifying)"
cat > "$R/state/evidence/phase6-goal.json" <<'JSON'
{"schema_version":1,"id":"goal-evidence-phase6-goal","project_id":"phase6","goal_id":"phase6-goal","verdict":"paused"}
JSON
paused_rc=0
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" transition-goal \
  phase6 phase6-goal verifying active verification-reopened >/dev/null 2>&1 || paused_rc=$?
if [ "$paused_rc" = 0 ] && [ "$(goal_status "$R")" = active ] \
   && [ "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("verdict",""))' "$R/state/evidence/phase6-goal.json")" = consumed ] \
   && find "$R/state/evidence/history" -name 'phase6-goal-reopen-*-paused.json' -print -quit | grep -q .; then
  ok "paused verification evidence reopens the goal after resume"
else
  no "paused verification evidence wedged the goal in verifying"
fi

# 18. A queued blocked transition must re-check that its triggering task is still blocked.
R="$(setup stale-block-cause active)"; write_task "$R" repaired-task queued 1
stale_rc=0
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" transition-goal \
  phase6 phase6-goal active blocked task-blocked >/dev/null 2>&1 || stale_rc=$?
if [ "$stale_rc" != 0 ] && [ "$(goal_status "$R")" = active ] \
   && [ "$(task_status "$R" repaired-task)" = queued ]; then
  ok "stale task-blocked transition is refused after assist recovery"
else
  no "stale task-blocked transition stranded an already repaired task"
fi

# 19. The durable answer may remain open across resume CAS; replay remains idempotent.
R="$(setup assist-open-answer blocked)"; write_task "$R" assisted-task blocked 1
cat > "$R/state/assists/assisted-task.md" <<'ASSIST'
task: assisted-task
kind: decision
status: open
asked: 2026-08-10T00:00:00Z
asked_by: worker
answered: 2026-08-10T00:01:00Z
answered_by: lucas

## QUESTION
Which marker?

## ANSWER
Use the marker after the canonical header.
ASSIST
assist_crash=0; assist_first=0; assist_second=0
# Crash after the non-authoritative task/goal writes but before the assist commit marker/event.
RECURSION_ROOT="$R" RECURSION_TRANSITION_FAILPOINT=state-write-2 \
  python3 "$R/scripts/project-reconcile.py" resume-assist \
  assisted-task 88 >/dev/null 2>&1 || assist_crash=$?
crash_guidance="$(RECURSION_ROOT="$R" bash "$SRC/scripts/assist.sh" guidance assisted-task)"
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" resume-assist \
  assisted-task 88 >/dev/null 2>&1 || assist_first=$?
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" resume-assist \
  assisted-task 88 >/dev/null 2>&1 || assist_second=$?
assist_events="$(grep -c '"event":"assist-answer"' "$R/state/events.jsonl" 2>/dev/null || true)"
if [ "$assist_crash" != 0 ] && [ "$assist_first" = 0 ] && [ "$assist_second" = 0 ] \
   && [ "$(goal_status "$R")" = active ] && [ "$(task_status "$R" assisted-task)" = queued ] \
   && [ "$(field "$R/state/assists/assisted-task.md" status)" = answered ] \
   && printf '%s' "$crash_guidance" | grep -q 'Use the marker after the canonical header' \
   && [ "$assist_events" = 1 ]; then
  ok "open durable assist answer survives the resume crash seam and replays idempotently"
else
  no "assist answer/CAS ordering remained lossy or non-idempotent"
fi

# 20. Project event appenders share taskctl's rotation boundary and never append mid-archive.
R="$(setup event-rotation active)"; mkdir -p "$R/state/.locks/runtime-state.lock"
RECURSION_ROOT="$R" RECURSION_LOCK_ATTEMPTS=1 RECURSION_LOCK_DELAY_S=0 python3 - <<'PY'
import importlib.util, os, pathlib, sys
root = pathlib.Path(os.environ["RECURSION_ROOT"])
sys.path.insert(0, str(root / "scripts"))
for name in ("project-reconcile.py", "project-pilot.py"):
    spec = importlib.util.spec_from_file_location("control", root / "scripts" / name)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    try:
        module.append_event(root, "must-not-append", "phase6", "phase6-goal")
    except (RuntimeError, SystemExit):
        continue
    raise SystemExit(f"{name} appended through runtime-state.lock")
PY
rotation_rc=$?
if [ "$rotation_rc" = 0 ] && ! grep -q 'must-not-append' "$R/state/events.jsonl"; then
  ok "project appenders refuse runtime-state rotation races"
else
  no "a project appender crossed the runtime-state/taskctl serialization boundary"
fi

# 21. A structurally invalid pilot gate is a controller rejection, not a successful worker
# action.  Task+goal close under one receipt before attempts/worktrees/runs exist; exact replay
# (including recovery after PAUSE lands between the two state writes) cannot duplicate evidence.
R="$(setup invalid-task-contract active)"; write_task "$R" contract-task ready 0
set_field "$R/state/tasks/contract-task.md" acceptance true
cp "$SRC/scripts/work.sh" "$SRC/scripts/validate-gate.py" "$SRC/scripts/resolve-model-alias.py" "$R/scripts/"
chmod +x "$R/scripts/work.sh" "$R/scripts/validate-gate.py" "$R/scripts/resolve-model-alias.py"
RECURSION_MODEL_ALIAS_SONNET_ROUTINE=stub-sonnet RECURSION_MODEL_ALIAS_OPUS_REVIEW=stub-opus \
  ticks "$R" 4
first_work_rc=0
RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 RECURSION_GIT_FETCH=0 \
  RECURSION_MODEL_ALIAS_SONNET_ROUTINE=stub-sonnet RECURSION_MODEL_ALIAS_OPUS_REVIEW=stub-opus \
  bash "$R/scripts/work.sh" contract-task >/dev/null 2>&1 || first_work_rc=$?
contract_events="$(grep -c '"event":"task-contract-invalid"' "$R/state/events.jsonl" 2>/dev/null || true)"
terminal_events="$(grep -c '"event":"goal-terminal"' "$R/state/events.jsonl" 2>/dev/null || true)"
failed_work_actions="$(python3 - "$R/state/actions" <<'PY'
import glob,json,sys
rows=[]
for path in glob.glob(sys.argv[1]+'/*.json'):
    try: row=json.load(open(path))
    except Exception: continue
    if row.get('verb')=='work': rows.append(row)
print(sum(row.get('status')=='failed' for row in rows))
PY
)"
if [ "$first_work_rc" = 78 ] && [ "$(task_status "$R" contract-task)" = blocked ] \
   && [ "$(goal_status "$R")" = blocked ] \
   && [ "$(field "$R/state/tasks/contract-task.md" attempts)" = 0 ] \
   && [ "$failed_work_actions" = 1 ] && [ "$contract_events" = 1 ] && [ "$terminal_events" = 1 ] \
   && ! find "$R/state/runs" -type f -print -quit | grep -q . \
   && [ ! -d "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["repo"])' "$R/state/project-config/phase6.json")/.worktrees/contract-task" ]; then
  ok "invalid pilot gate atomically blocks task+goal, fails work action, and launches nothing"
else
  no "invalid pilot gate succeeded, stranded the goal, incremented attempts, or launched execution"
fi

C="$(setup invalid-contract-crash active)"; write_task "$C" crash-contract ready 0
DIGEST="$(printf contract | sha256sum | cut -d' ' -f1)"
crash_rc=0; paused_replay_rc=0
RECURSION_ROOT="$C" RECURSION_TRANSITION_FAILPOINT=state-write-1 \
  python3 "$C/scripts/project-reconcile.py" reject-task-contract crash-contract acceptance-invalid "$DIGEST" \
  >/dev/null 2>&1 || crash_rc=$?
touch "$C/state/PAUSE"
RECURSION_ROOT="$C" python3 "$C/scripts/project-reconcile.py" reject-task-contract crash-contract acceptance-invalid "$DIGEST" \
  >/dev/null 2>&1 || paused_replay_rc=$?
crash_events="$(grep -c '"event":"task-contract-invalid"' "$C/state/events.jsonl" 2>/dev/null || true)"
task_receipt="$(field "$C/state/tasks/crash-contract.md" last_transition_id)"
goal_receipt="$(field "$C/state/goals/phase6-goal.md" last_transition_id)"
if [ "$crash_rc" != 0 ] && [ "$paused_replay_rc" = 0 ] \
   && [ "$(task_status "$C" crash-contract)" = blocked ] && [ "$(goal_status "$C")" = blocked ] \
   && [ "$(field "$C/state/tasks/crash-contract.md" attempts)" = 0 ] \
   && [ -n "$task_receipt" ] && [ "$task_receipt" = "$goal_receipt" ] && [ "$crash_events" = 1 ]; then
  ok "PAUSE-time exact replay completes one partial task-contract rejection receipt"
else
  no "partial contract rejection was not safely recoverable after PAUSE"
fi

P="$(setup invalid-contract-pause-race active)"; write_task "$P" pause-contract ready 0
pause_race_rc=0
RECURSION_ROOT="$P" RECURSION_TEST_PAUSE_BEFORE_CONTRACT_COMMIT=1 \
  python3 "$P/scripts/project-reconcile.py" reject-task-contract pause-contract acceptance-invalid "$DIGEST" \
  >/dev/null 2>&1 || pause_race_rc=$?
if [ "$pause_race_rc" = 75 ] && [ "$(task_status "$P" pause-contract)" = ready ] \
   && [ "$(goal_status "$P")" = active ] \
   && ! grep -q '"event":"task-contract-invalid"' "$P/state/events.jsonl"; then
  ok "PAUSE at the receipt commit boundary prevents a new contract rejection"
else
  no "PAUSE/window authority change was not a typed deferral or mutated state (rc=$pause_race_rc)"
fi

# Every deterministic pre-worker metadata refusal shares the same attempts-zero lifecycle.
preworker_case(){ # name category mutation
  local name="$1" category="$2" mutation="$3" r rc=0 observed
  r="$(setup "preworker-$name" active)"; write_task "$r" "$name-task" ready 0
  cp "$SRC/scripts/work.sh" "$SRC/scripts/validate-gate.py" "$SRC/scripts/resolve-model-alias.py" "$r/scripts/"
  chmod +x "$r/scripts/work.sh" "$r/scripts/validate-gate.py" "$r/scripts/resolve-model-alias.py"
  eval "$mutation"
  RECURSION_ROOT="$r" RECURSION_NO_NOTIFY=1 RECURSION_GIT_FETCH=0 \
    RECURSION_MODEL_ALIAS_SONNET_ROUTINE=stub-sonnet RECURSION_MODEL_ALIAS_OPUS_REVIEW=stub-opus \
    bash "$r/scripts/work.sh" "$name-task" >/dev/null 2>&1 || rc=$?
  observed="$(field "$r/state/tasks/$name-task.md" contract_rejection_category)"
  [ "$rc" = 78 ] && [ "$observed" = "$category" ] \
    && [ "$(task_status "$r" "$name-task")" = blocked ] && [ "$(goal_status "$r")" = blocked ] \
    && [ "$(field "$r/state/tasks/$name-task.md" attempts)" = 0 ] \
    && [ -n "$(field "$r/state/tasks/$name-task.md" contract_digest)" ] \
    && ! find "$r/state/runs" -type f -print -quit | grep -q .
}

preworker_case missing acceptance-missing 'set_field "$r/state/tasks/$name-task.md" acceptance ""' \
  && ok "missing acceptance uses the atomic pre-worker rejection" \
  || no "missing acceptance retained the stranded legacy lifecycle"
preworker_case deadline deadline-invalid 'set_field "$r/state/tasks/$name-task.md" deadline_seconds nope' \
  && ok "invalid deadline uses the atomic pre-worker rejection" || no "invalid deadline stranded state"
preworker_case network network-policy-invalid 'set_field "$r/state/tasks/$name-task.md" network_policy live' \
  && ok "invalid network policy uses the atomic pre-worker rejection" || no "invalid network policy stranded state"
preworker_case verification verification-policy-invalid 'set_field "$r/state/tasks/$name-task.md" verification self' \
  && ok "invalid verifier policy uses the atomic pre-worker rejection" || no "invalid verifier policy stranded state"
preworker_case engine worker-engine-invalid 'set_field "$r/state/tasks/$name-task.md" engine hermes' \
  && ok "invalid worker engine uses the atomic pre-worker rejection" || no "invalid worker engine stranded state"
preworker_case verifier-engine worker-engine-invalid 'sed -i "1a verifier_engine: hermes" "$r/state/tasks/$name-task.md"' \
  && ok "invalid verifier engine uses the atomic pre-worker rejection" || no "invalid verifier engine stranded state"
preworker_case model model-alias-invalid 'set_field "$r/state/tasks/$name-task.md" model_alias unknown-model' \
  && ok "invalid implementer model uses the atomic pre-worker rejection" || no "invalid implementer model stranded state"
preworker_case verifier-model verifier-model-alias-invalid 'set_field "$r/state/tasks/$name-task.md" verifier_model_alias unknown-model' \
  && ok "invalid verifier model uses the atomic pre-worker rejection" || no "invalid verifier model stranded state"
preworker_case same-model model-separation-invalid 'set_field "$r/state/tasks/$name-task.md" verifier_model_alias sonnet-routine' \
  && ok "non-independent model aliases use the atomic pre-worker rejection" || no "same models stranded state"

T="$(setup preworker-transient active)"; write_task "$T" transient-task ready 0
cp "$SRC/scripts/work.sh" "$SRC/scripts/resolve-model-alias.py" "$T/scripts/"
chmod +x "$T/scripts/work.sh" "$T/scripts/resolve-model-alias.py"
cat > "$T/scripts/validate-gate.py" <<'PY'
#!/usr/bin/env python3
raise SystemExit(74)
PY
chmod +x "$T/scripts/validate-gate.py"
transient_rc=0
RECURSION_ROOT="$T" RECURSION_NO_NOTIFY=1 RECURSION_GIT_FETCH=0 \
  RECURSION_MODEL_ALIAS_SONNET_ROUTINE=stub-sonnet RECURSION_MODEL_ALIAS_OPUS_REVIEW=stub-opus \
  bash "$T/scripts/work.sh" transient-task >/dev/null 2>&1 || transient_rc=$?
if [ "$transient_rc" = 74 ] && [ "$(task_status "$T" transient-task)" = ready ] \
   && [ "$(goal_status "$T")" = active ] && ! grep -q 'task-contract-invalid' "$T/state/events.jsonl"; then
  ok "transient validator I/O fails closed without falsely terminalizing metadata"
else
  no "transient controller failure was mislabeled as invalid task metadata"
fi

# 22. Terminal goal grading runs against an OS read-only exact-commit worktree. A conformance
# that reversibly tampers with its own declared gate file (write + restore inside one command)
# cannot write it, so the gate fails and the goal reopens instead of silently achieving.
R="$(setup toctou)"; write_task "$R" toctou-task proposed 0
toctou_repo="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["repo"])' "$R/state/project-config/phase6.json")"
printf '#!/usr/bin/env bash\nexit 1\n' > "$toctou_repo/app/gate.sh"
git -C "$toctou_repo" add app/gate.sh
git -C "$toctou_repo" -c user.name=t -c user.email=t@t commit -qm 'declared gate file'
git -C "$toctou_repo" push -q origin main
set_field "$R/state/goals/phase6-goal.md" acceptance_suite \
  "printf 'exit 0\n' > app/gate.sh && git checkout -- app/gate.sh && test -s app/result.txt"
set_field "$R/state/goals/phase6-goal.md" gate_files app/gate.sh
# This falsifier is specifically about the OS mount boundary.  The suite-wide logical mode
# intentionally bypasses that boundary and therefore cannot be authority for this one control.
sandbox_proven=0
if RECURSION_ROOT="$R" RECURSION_TEST_WORKER=sandbox \
     bash "$R/scripts/worker-sandbox.sh" --engine gate --role gate \
       --worktree "$toctou_repo" --workdir . --network-policy none --read-only-worktree \
       --gate-command '[ "$(id -u)" -ne 0 ] && ! touch .recursion-ro-probe' \
       >/dev/null 2>&1 \
   && [ ! -e "$toctou_repo/.recursion-ro-probe" ]; then
  sandbox_proven=1
fi
prior_test_worker="$RECURSION_TEST_WORKER"
export RECURSION_TEST_WORKER=sandbox
ticks "$R" 12
export RECURSION_TEST_WORKER="$prior_test_worker"
toctou_closed=0
if [ "$sandbox_proven" = 1 ] && [ "$(goal_status "$R")" = active ] \
   && [ "$(launch_count "$R")" = 1 ] \
   && python3 - "$R/state/evidence/history" <<'PY'
import glob,json,sys
rows=[]
for path in glob.glob(sys.argv[1] + '/phase6-goal-reopen-v*-fail.json'):
    try: rows.append(json.load(open(path)))
    except Exception: pass
raise SystemExit(0 if len(rows)==1 and rows[0].get('verdict')=='fail'
                 and rows[0].get('exit_code') != 0 else 1)
PY
then toctou_closed=1; fi
if [ "$toctou_closed" = 1 ]; then
  ok "reversible gate-file tampering fails against the OS read-only grading worktree"
else
  no "reversible gate-file tampering escaped the terminal gate (status=$(goal_status "$R") launches=$(launch_count "$R"))"
fi

# 23. A Phase-8 goal is terminal-graded only against its exact approved plan projection: the
# materialized goal/task immutable contract is re-proven before any worktree or gate runs, so
# tampering with the materialized projection fails closed, while the restored projection
# revalidates cleanly and grades pass.
R="$(setup phase8-projection)"; write_task "$R" phase8-task proposed 0
phase8_repo="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["repo"])' "$R/state/project-config/phase6.json")"
printf ok > "$phase8_repo/app/result.txt"
git -C "$phase8_repo" add app/result.txt
git -C "$phase8_repo" -c user.name=t -c user.email=t@t commit -qm result
git -C "$phase8_repo" push -q origin main
source_head="$(git -C "$phase8_repo" rev-parse HEAD)"
python3 - "$R" "$phase8_repo" "$source_head" <<'PY'
import hashlib, json, subprocess, sys, time
from pathlib import Path
root, repo = Path(sys.argv[1]), Path(sys.argv[2])
source_head = sys.argv[3]
contract = json.loads(subprocess.run(
    [sys.executable, str(root / "scripts/validate-gate.py"), "--acceptance",
     "test -s app/result.txt", "--allowed-paths", "app", "--gate-files", "",
     "--repo", str(repo), "--controller-root", str(root),
     "--controller-gate-files", "", "--strict-direct"],
    text=True, capture_output=True, check=True).stdout.strip())
budget = {"max_concurrency":1,"max_tokens":1000,"max_cost_usd":5,"max_wall_clock_seconds":3600,
          "max_task_attempts":2,"max_failures":1,"max_review_queue":1,"max_publish_attempts":1,
          "publication_required":False}
charter = hashlib.sha256(b"Bounded Phase 6 fixture only.").hexdigest()
authority = {"source_head":source_head,"remote_head":source_head,"default_branch":"main",
             "charter_sha256":charter,
             "required_non_goals":["credentials","merge","deploy"]}
plan = {"schema_version":1,"id":"plan-phase8-projection","project_id":"phase6",
        "authority_contract":authority,
        "goal":{"id":"phase6-goal","outcome":"Projection fixture.","acceptance_suite":"test -s app/result.txt",
                "falsifier":"The projection disagrees.","gate_class":"light","gate_files":[],
                "controller_gate_files":[],"gate_contract":contract,"budget":budget},
        "tasks":[{"id":"phase8-task","intent":"Produce the projection fixture.","dependencies":[],
                  "allowed_paths":["app"],"non_goals":["credentials","merge","deploy"],
                  "worker_class":"claude","engine":"claude","model_alias":"sonnet-routine",
                  "verifier_model_alias":"opus-review","deadline_seconds":60,
                  "verifier_deadline_seconds":60,"network_policy":"provider-only",
                  "evidence_contract":"worker-result-v1","verification":"independent",
                  "expected_change":"required","gate_class":"light","gate_files":[],
                  "controller_gate_files":[],"gate_contract":contract,
                  "acceptance":"test -s app/result.txt"}]}
def raw(value): return json.dumps(value, sort_keys=True, separators=(",", ":"))
digest = hashlib.sha256(raw(plan).encode()).hexdigest()
(root / "state/plans/phase6").mkdir(parents=True, exist_ok=True)
(root / "state/plans/phase6/plan-phase8-projection.json").write_text(raw({
    "schema_version":1,"id":"plan-phase8-projection","project_id":"phase6","instruction_id":"101",
    "plan_digest":digest,"plan":plan,"status":"approved"}) + "\n", encoding="utf-8")
(root / "state/goals/phase6-goal.md").write_text(
    "schema_version: 1\nversion: 1\nid: phase6-goal\nproject_id: phase6\npilot_id: pilot-phase6\n"
    f"plan_id: plan-phase8-projection\nplan_digest: {digest}\ninstruction_id: 101\nstatus: verifying\n"
    "outcome: Projection fixture.\nacceptance_suite: test -s app/result.txt\n"
    "falsifier: The projection disagrees.\ngate_class: light\ngate_files: \ncontroller_gate_files: \n"
    f"gate_contract: {raw(contract)}\nsource_head: {source_head}\nsource_branch: main\n"
    f"charter_sha256: {charter}\nbudget: {raw(budget)}\nstarted_at_epoch: {int(time.time())}\n"
    "terminal_reported: 0\n", encoding="utf-8")
task = {"schema_version":"1","version":"1","id":"phase8-task","project_id":"phase6","project":"phase6",
        "workstream":"phase6","pilot_id":"pilot-phase6","goal_id":"phase6-goal",
        "plan_id":"plan-phase8-projection","plan_digest":digest,"dependencies":"",
        "goal":"Produce the projection fixture.","allowed_paths":"app",
        "non_goals":"credentials,merge,deploy","worker_class":"claude","engine":"claude",
        "model_alias":"sonnet-routine","verifier_model_alias":"opus-review","deadline_seconds":"60",
        "verifier_deadline_seconds":"60","network_policy":"provider-only",
        "evidence_contract":"worker-result-v1","verification":"independent","expected_change":"required",
        "gate_class":"light","gate_contract":raw(contract),"gate_files":"",
        "acceptance":"test -s app/result.txt","controller_gate_files":"","source_head":source_head,
        "source_branch":"main","charter_sha256":charter,"repo":str(repo),"workdir":".","autonomy":"auto",
        "status":"passed","candidate_commit":source_head}
(root / "state/tasks/phase8-task.md").write_text(
    "".join(f"{key}: {value}\n" for key, value in task.items()), encoding="utf-8")
def run_record(rid, role):
    return {"schema_version":1,"id":rid,"task_id":"phase8-task","worker":f"{role}:test","role":role,
            "worktree":"fixture","base_commit":source_head,"pid":1,"process_group":1,
            "lease_expires":"0","deadline":"0","usage":{"tokens":10,"cost_usd":0.01},
            "result":{"status":"done"},"seed_evidence":{},
            "machine_gate":{"commit_oid":source_head,"exit_code":0},
            "verification":{"verifier_run_id":"phase8-task-verify","commit_oid":source_head,"verdict":"pass"},
            "status":"succeeded"}
(root / "state/runs/phase8-task-impl.json").write_text(raw(run_record("phase8-task-impl","implementer")) + "\n")
verifier = run_record("phase8-task-verify","verifier")
verifier["verification"] = {"commit_oid":source_head,"implementer_run_id":"phase8-task-impl","verdict":"pass"}
(root / "state/runs/phase8-task-verify.json").write_text(raw(verifier) + "\n")
PY
git -C "$phase8_repo" branch loop/work/phase8-task "$source_head"
nonterminal_rc=0
RECURSION_ROOT="$R" python3 "$R/scripts/project-pilot.py" \
  verify-approved-goal phase6 phase6-goal >/dev/null 2>&1 || nonterminal_rc=$?
sed -i 's#^acceptance: test -s app/result.txt#acceptance: true#' "$R/state/tasks/phase8-task.md"
first_rc=0
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" verify-goal phase6 phase6-goal \
  >/dev/null 2>&1 || first_rc=$?
first_ok=0
if [ "$first_rc" = 0 ] && python3 - "$R/state/evidence/phase6-goal.json" "$phase8_repo" <<'PY'
import json,sys
from pathlib import Path
row=json.load(open(sys.argv[1],encoding="utf-8"))
verify_root=Path(sys.argv[2],".worktrees")
worktrees=list(verify_root.glob("goal-phase6-goal-verify-*")) if verify_root.is_dir() else []
raise SystemExit(0 if row.get('verdict')=='fail'
                 and str(row.get('reason','')).startswith('phase8-contract') and not worktrees else 1)
PY
then first_ok=1; fi
sed -i 's#^acceptance: true#acceptance: test -s app/result.txt#' "$R/state/tasks/phase8-task.md"
second_rc=0
RECURSION_ROOT="$R" python3 "$R/scripts/project-reconcile.py" verify-goal phase6 phase6-goal \
  >/dev/null 2>&1 || second_rc=$?
second_ok=0
if [ "$second_rc" = 0 ] && python3 - "$R/state/evidence/phase6-goal.json" <<'PY'
import json,sys
row=json.load(open(sys.argv[1],encoding="utf-8"))
raise SystemExit(0 if row.get('verdict')=='pass' and not str(row.get('reason','')).startswith('phase8-contract') else 1)
PY
then second_ok=1; fi
if [ "$nonterminal_rc" != 0 ] && [ "$first_ok" = 1 ] && [ "$second_ok" = 1 ]; then
  ok "Phase-8 goal grading revalidates the approved plan projection before the gate"
else
  no "Phase-8 projection tampering was not caught or restore did not revalidate (first=$first_ok second=$second_ok rc=$first_rc/$second_rc)"
fi

echo
[ "$fails" -eq 0 ] && { echo "hermes-pilot-phase6-red: ALL PASS"; exit 0; }
echo "hermes-pilot-phase6-red: $fails FAILED (expected on the pre-Phase 6 base)"; exit 1

#!/usr/bin/env bash
# Phase 4 controls: topic/project isolation, charter authority, live status, and activation proof.
set -uo pipefail
export LC_ALL=C RECURSION_NO_NOTIFY=1
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"
trap 'if [ "${RECURSION_KEEP_TEST_TMP:-0}" = 1 ]; then echo "PHASE4_TEST_TMP=$TMP" >&2; else rm -rf "$TMP"; fi' EXIT
R="$TMP/root"
mkdir -p "$R/scripts" "$R/state/project-config" "$R/state/pilots" "$R/state/goals" \
  "$R/state/tasks" "$R/state/runs" "$R/state/instructions" "$R/state/.locks" \
  "$R/loop/logs" "$R/.worktrees"
for s in project-pilot.py intake.sh author.sh resync.sh taskctl.sh jsonl_durable.py transition_receipt.py runtime-state.py notify.sh validate-control-state.py; do
  [ -f "$SRC/scripts/$s" ] && cp "$SRC/scripts/$s" "$R/scripts/$s"
done
chmod +x "$R/scripts/"* 2>/dev/null || true
: > "$R/.env"
PILOT="$R/scripts/project-pilot.py"
GIT="git -c user.name=t -c user.email=t@t -c init.defaultBranch=main"

mk_repo(){ # name -> prints clone path and creates matching .git origin
  local name origin clone
  name="$1"; origin="$TMP/$name.git"; clone="$TMP/$name"
  $GIT init -q --bare "$origin"
  $GIT init -q "$clone"
  ( cd "$clone" && printf '%s\n' "$name" > README.md && $GIT add README.md \
    && $GIT commit -qm init && $GIT branch -M main && $GIT remote add origin "$origin" \
    && $GIT push -q origin main )
  $GIT -C "$clone" fetch -q origin
  printf '%s\n' "$clone"
}

ALPHA="$(mk_repo alpha)"; BETA="$(mk_repo beta)"
KEY="$TMP/fake-key"; : > "$KEY"; chmod 600 "$KEY"
{
  printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n'
  printf 'alpha\t%s\t%s\tmain\t%s\t-\t11\tactive\n' "$ALPHA" "$TMP/alpha.git" "$KEY"
  printf 'beta\t%s\t%s\tmain\t%s\t-\t22\tactive\n' "$BETA" "$TMP/beta.git" "$KEY"
} > "$R/state/portfolio.tsv"

python3 - "$R" "$ALPHA" "$BETA" "$KEY" <<'PY'
import json,os,sys
root,alpha,beta,key=sys.argv[1:]
for project,topic,repo,scope in (("alpha",11,alpha,"alpha-src"),("beta",22,beta,"beta-src")):
    charter=f"Work only in {project} under approved goals and {scope}; no portfolio or policy authority."
    project_record={"schema_version":1,"id":project,"repo":repo,"remote":repo+".git",
      "default_branch":"main","deploy_key_ref":key,"charter":charter,"allowed_paths":[scope],
      "topic":topic,"pilot_id":"pilot-"+project,"activation_gate":"clone-auth-freshness-v1",
      "notification_targets":[f"topic:{topic}","head-hermes","lucas-direct"],
      "goal_source":"state/goals","status":"active"}
    pilot_record={"schema_version":1,"id":"pilot-"+project,"project_id":project,
      "topic":topic,"charter":charter,"model_policy":"project-pilot","concurrency_limit":0,
      "budget":{"max_inflight_workers":0,"max_decisions_per_turn":1},
      "notification_targets":project_record["notification_targets"],"goal_source":"state/goals",
      "memory_key":f"telegram-topic:{topic}","worktree_root":f".worktrees/{project}","status":"active"}
    for directory,value in (("project-config",project_record),("pilots",pilot_record)):
        path=os.path.join(root,"state",directory,value["id"]+".json")
        with open(path,"w",encoding="utf-8") as out: json.dump(value,out); out.write("\n")
PY

for project in alpha beta; do
  cat > "$R/state/goals/goal-$project.md" <<EOF
schema_version: 1
id: goal-$project
project_id: $project
status: active
outcome: complete bounded $project work
acceptance_suite: test -f README.md
falsifier: work escapes $project
budget: phase4 fixture
EOF
  cat > "$R/state/tasks/$project-task.md" <<EOF
id: $project-task
project_id: $project
goal_id: goal-$project
dependencies:
allowed_paths: ${project}-src
acceptance: test -f README.md
status: queued
EOF
  printf '{"schema_version":1,"id":"%s-run","task_id":"%s-task","project_id":"%s","worktree":".worktrees/%s/%s-task","status":"running"}\n' \
    "$project" "$project" "$project" "$project" "$project" > "$R/state/runs/$project-run.json"
done

# 1. Two Telegram topics must resolve to distinct durable pilots and expose only scoped state.
DB="$TMP/gateway.db"
python3 - "$DB" <<'PY'
import sqlite3,sys
c=sqlite3.connect(sys.argv[1])
c.execute('create table sessions(id text primary key,source text,user_id text,chat_id text,thread_id text)')
c.execute('create table messages(id integer primary key,session_id text,role text,content text,timestamp real)')
c.executemany('insert into sessions values(?,?,?,?,?)',[
 ('a','telegram','8913126684','-1001','11'),('b','telegram','8913126684','-1001','22')])
c.executemany('insert into messages values(?,?,?,?,?)',[
 (101,'a','user','status alpha',1.0),(102,'b','user','status beta',2.0)])
c.commit()
PY
( cd "$R" && RECURSION_ROOT="$R" RECURSION_HERMES_DB="$DB" RECURSION_INTAKE_ALLOW=8913126684 \
    bash scripts/intake.sh poll --backfill ) >/dev/null 2>&1
isolation=0
if [ -f "$PILOT" ]; then
  RECURSION_ROOT="$R" python3 "$PILOT" verify-registry >/dev/null 2>&1 || isolation=1
  RECURSION_ROOT="$R" python3 "$PILOT" context alpha > "$TMP/alpha-context.json" 2>/dev/null || isolation=1
  RECURSION_ROOT="$R" python3 "$PILOT" context beta > "$TMP/beta-context.json" 2>/dev/null || isolation=1
else isolation=1
fi
if [ "$isolation" = 0 ] \
  && grep -q '^pilot_id: pilot-alpha$' "$R/state/instructions/00000101.md" \
  && grep -q '^pilot_memory_key: telegram-topic:11$' "$R/state/instructions/00000101.md" \
  && grep -q '^pilot_id: pilot-beta$' "$R/state/instructions/00000102.md" \
  && grep -q '^pilot_memory_key: telegram-topic:22$' "$R/state/instructions/00000102.md" \
  && grep -q 'alpha-task' "$TMP/alpha-context.json" && ! grep -q 'beta-task\|beta-run' "$TMP/alpha-context.json" \
  && grep -q 'beta-task' "$TMP/beta-context.json" && ! grep -q 'alpha-task\|alpha-run' "$TMP/beta-context.json" \
  && grep -q '"worktree_root":".worktrees/alpha"' "$TMP/alpha-context.json" \
  && grep -q '"worktree_root":".worktrees/beta"' "$TMP/beta-context.json"; then
  ok "two topics have isolated project state, tasks, worktrees, and pilot memory"
else
  no "topic messages lack a durable, isolated project-pilot binding"
fi

# 2. A project pilot cannot escape its charter or change another project's priority.
cp "$R/state/project-config/beta.json" "$TMP/beta-before.json"
route_rc=1; scope_rc=0
if [ -f "$PILOT" ]; then
  RECURSION_ROOT="$R" python3 "$PILOT" route alpha priority-set beta > "$TMP/route.json" 2>/dev/null; route_rc=$?
  RECURSION_ROOT="$R" python3 "$PILOT" authorize alpha pilot-task-create beta-src beta > "$TMP/scope.out" 2>&1; scope_rc=$?
else
  printf '{}\n' > "$TMP/route.json"; scope_rc=0
fi
if [ "$route_rc" = 0 ] && grep -q '"target":"head-hermes"' "$TMP/route.json" \
  && [ "$scope_rc" -ne 0 ] && cmp -s "$TMP/beta-before.json" "$R/state/project-config/beta.json"; then
  ok "pilot refuses out-of-charter work and forwards cross-project priority to Head Hermes"
else
  no "pilot scope/priority authority is not mechanically bounded"
fi

# 3. Status must ignore remembered prose and return current task/run/git evidence.
printf 'remembered old prose that must never be status truth\n' > "$R/state/pilots/pilot-alpha.memory"
( cd "$ALPHA" && printf 'live\n' >> README.md && $GIT add README.md && $GIT commit -qm live-status )
sed -i 's/^status: queued/status: blocked/' "$R/state/tasks/alpha-task.md"
live_head="$(git -C "$ALPHA" rev-parse HEAD)"; status_rc=1
if [ -f "$PILOT" ]; then
  RECURSION_ROOT="$R" python3 "$PILOT" status alpha > "$TMP/status.json" 2>/dev/null; status_rc=$?
else printf '{}\n' > "$TMP/status.json"; fi
if [ "$status_rc" = 0 ] && grep -q "$live_head" "$TMP/status.json" \
  && grep -q '"status":"blocked"' "$TMP/status.json" && grep -q 'alpha-run' "$TMP/status.json" \
  && grep -q '"source":"live-control-state"' "$TMP/status.json" \
  && ! grep -q 'remembered old prose' "$TMP/status.json"; then
  ok "direct status returns current task/run/git evidence, never remembered prose"
else
  no "direct status is not a bounded live-evidence read"
fi

# 4. Activation must fail closed for absent key, stale clone, missing gate, or missing charter.
ACT="$TMP/activation"; mkdir -p "$ACT"
add_pending(){
  local p path remote key charter gate topic
  p="$1"; path="$2"; remote="$3"; key="$4"; charter="$5"; gate="$6"; topic="$7"
  printf '%s\t%s\t%s\tmain\t%s\t-\t%s\tpending\n' "$p" "$path" "$remote" "$key" "$topic" >> "$R/state/portfolio.tsv"
  python3 - "$R" "$p" "$path" "$remote" "$key" "$charter" "$gate" "$topic" <<'PY'
import json,sys
root,p,repo,remote,key,charter,gate,topic=sys.argv[1:]
d={"schema_version":1,"id":p,"repo":repo,"remote":remote,"default_branch":"main",
   "deploy_key_ref":key,"charter":charter,"allowed_paths":["src"],"topic":int(topic),
   "pilot_id":"pilot-"+p,"activation_gate":gate,"notification_targets":["topic:"+topic,"head-hermes"],
   "goal_source":"state/goals","status":"pending"}
pilot={"schema_version":1,"id":"pilot-"+p,"project_id":p,"topic":int(topic),"charter":charter,
 "model_policy":"project-pilot","concurrency_limit":0,
 "budget":{"max_inflight_workers":0,"max_decisions_per_turn":1},
 "notification_targets":["topic:"+topic,"head-hermes"],"goal_source":"state/goals",
 "memory_key":"telegram-topic:"+topic,"worktree_root":".worktrees/"+p,"status":"pending"}
for directory,value in (("project-config",d),("pilots",pilot)):
    path=root+"/state/"+directory+"/"+value["id"]+".json"
    with open(path,"w",encoding="utf-8") as out: json.dump(value,out); out.write("\n")
PY
}
mk_pending_remote(){
  local p origin seed
  p="$1"; origin="$ACT/$p.git"; seed="$ACT/$p-seed"
  $GIT init -q --bare "$origin"; $GIT init -q "$seed"
  ( cd "$seed" && printf x > f && $GIT add f && $GIT commit -qm init && $GIT branch -M main \
    && $GIT remote add origin "$origin" && $GIT push -q origin main )
  printf '%s\n' "$origin"
}
GOOD_GATE=clone-auth-freshness-v1
NO_KEY_REMOTE="$(mk_pending_remote no-key)"
add_pending no-key "$ACT/no-key" "$NO_KEY_REMOTE" "$ACT/absent-key" "bounded charter" "$GOOD_GATE" 31

STALE_REMOTE="$(mk_pending_remote stale)"; git clone -q "$STALE_REMOTE" "$ACT/stale"
( cd "$ACT/stale-seed" && printf y >> f && $GIT add f && $GIT commit -qm newer && $GIT push -q origin main )
add_pending stale "$ACT/stale" "$STALE_REMOTE" "$KEY" "bounded charter" "$GOOD_GATE" 32

NO_GATE_REMOTE="$(mk_pending_remote no-gate)"
add_pending no-gate "$ACT/no-gate" "$NO_GATE_REMOTE" "$KEY" "bounded charter" "" 33
NO_CHARTER_REMOTE="$(mk_pending_remote no-charter)"
add_pending no-charter "$ACT/no-charter" "$NO_CHARTER_REMOTE" "$KEY" "" "$GOOD_GATE" 34

activation_ok=1
for p in no-key stale no-gate no-charter; do
  ( cd "$R" && RECURSION_ROOT="$R" bash scripts/author.sh register "$p" ) > "$TMP/register-$p.out" 2>&1
  rc=$?; row="$(awk -F'\t' -v p="$p" '$1==p{print $8}' "$R/state/portfolio.tsv")"
  [ "$rc" -ne 0 ] && [ "$row" = pending ] || activation_ok=0
done
if [ "$activation_ok" = 1 ]; then
  ok "activation refuses absent key, stale clone, missing gate, and missing charter"
else
  no "registration activated a project without every key/clone/freshness/gate/charter proof"
fi

echo
[ "$fails" -eq 0 ] && { echo "hermes-pilot-phase4-red: ALL PASS"; exit 0; }
echo "hermes-pilot-phase4-red: $fails FAILED"; exit 1

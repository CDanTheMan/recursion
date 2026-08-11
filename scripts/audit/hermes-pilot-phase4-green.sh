#!/usr/bin/env bash
# Positive Phase 4 audit: hermetic fixtures only; no model, Telegram API, worker, or publication.
set -euo pipefail
export LC_ALL=C RECURSION_NO_NOTIFY=1
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# Every tracked active project has one complete, unique topic pilot, and both record kinds remain
# valid v1 control-state objects with additive Phase 4 metadata.
RECURSION_ROOT="$SRC" python3 "$SRC/scripts/project-pilot.py" verify-registry >/dev/null
for file in "$SRC"/state/project-config/*.json; do
  python3 "$SRC/scripts/validate-control-state.py" project "$file" >/dev/null
done
for file in "$SRC"/state/pilots/*.json; do
  python3 "$SRC/scripts/validate-control-state.py" pilot "$file" >/dev/null
done
echo "ok    durable project/pilot metadata validates and active topics are one-to-one"

# One direct topic message stays with its pilot; a cross-project priority request in the same
# topic is forwarded to Head Hermes. Both remain inert durable instructions.
I="$TMP/intake"; mkdir -p "$I/scripts" "$I/state/project-config" "$I/state/pilots" "$I/state/instructions"
cp "$SRC/scripts/intake.sh" "$SRC/scripts/runtime-state.py" "$I/scripts/"
printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > "$I/state/portfolio.tsv"
printf 'alpha\t/tmp/alpha\tgit@example/alpha\tmain\t/tmp/key\t-\t11\tactive\n' >> "$I/state/portfolio.tsv"
printf 'beta\t/tmp/beta\tgit@example/beta\tmain\t/tmp/key\t-\t22\tactive\n' >> "$I/state/portfolio.tsv"
python3 - "$I" <<'PY'
import json,os,sys
root=sys.argv[1]
for project,topic in (("alpha",11),("beta",22)):
    charter=f"only {project} src"
    cfg={"schema_version":1,"id":project,"repo":"/tmp/"+project,"remote":"git@example/"+project,
      "default_branch":"main","deploy_key_ref":"/tmp/key","charter":charter,"allowed_paths":["src"],
      "topic":topic,"pilot_id":"pilot-"+project,"activation_gate":"clone-auth-freshness-v1",
      "notification_targets":[f"topic:{topic}","head-hermes"],"goal_source":"state/goals","status":"active"}
    pilot={"schema_version":1,"id":"pilot-"+project,"project_id":project,"topic":topic,
      "charter":charter,"model_policy":"project-pilot","concurrency_limit":0,
      "budget":{"max_inflight_workers":0,"max_decisions_per_turn":1},
      "notification_targets":cfg["notification_targets"],"goal_source":"state/goals",
      "memory_key":f"telegram-topic:{topic}","worktree_root":".worktrees/"+project,"status":"active"}
    for directory,value in (("project-config",cfg),("pilots",pilot)):
        with open(os.path.join(root,"state",directory,value["id"]+".json"),"w",encoding="utf-8") as out:
            json.dump(value,out); out.write("\n")
PY
DB="$TMP/gateway.db"
python3 - "$DB" <<'PY'
import sqlite3,sys
c=sqlite3.connect(sys.argv[1])
c.execute('create table sessions(id text primary key,source text,user_id text,chat_id text,thread_id text)')
c.execute('create table messages(id integer primary key,session_id text,role text,content text,timestamp real)')
c.execute('insert into sessions values(?,?,?,?,?)',('a','telegram','8913126684','-1001','11'))
c.executemany('insert into messages values(?,?,?,?,?)',[
 (1,'a','user','show alpha status',1.0),(2,'a','user','make beta the higher portfolio priority',2.0)])
c.commit()
PY
( cd "$I" && RECURSION_ROOT="$I" RECURSION_HERMES_DB="$DB" RECURSION_INTAKE_ALLOW=8913126684 \
  bash scripts/intake.sh poll --backfill ) >/dev/null 2>&1
grep -q '^routing_target: pilot-alpha$' "$I/state/instructions/00000001.md"
grep -q '^pilot_memory_key: telegram-topic:11$' "$I/state/instructions/00000001.md"
grep -q '^routing_target: head-hermes$' "$I/state/instructions/00000002.md"
echo "ok    project-topic intake binds its pilot and forwards portfolio/cross-project authority"

# The deterministic pilot verb boundary creates one scoped, dependency-linked proposed task from
# its approved goal gate, while worker/verifier/verification requests remain requests (Phase 5+).
P="$TMP/pilot"; mkdir -p "$P/scripts" "$P/state/project-config" "$P/state/pilots" \
  "$P/state/goals" "$P/state/tasks" "$P/state/runs" "$P/state/instructions" "$P/state/actions" \
  "$P/state/.locks" "$P/loop/logs"
for script in project-pilot.py conduct-hermes.sh validate-decision.py validate-control-state.py \
              decision-queue.py taskctl.sh jsonl_durable.py transition_receipt.py intake.sh \
              runtime-state.py; do
  cp "$SRC/scripts/$script" "$P/scripts/"
done
printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > "$P/state/portfolio.tsv"
printf 'alpha\t%s\t%s\tmain\t%s\t-\t11\tactive\n' "$TMP/alpha" "$TMP/alpha.git" "$TMP/key" >> "$P/state/portfolio.tsv"
python3 - "$P" "$TMP" <<'PY'
import json,os,sys
root,tmp=sys.argv[1:]
charter="alpha src only; no portfolio authority"
cfg={"schema_version":1,"id":"alpha","repo":tmp+"/alpha","remote":tmp+"/alpha.git",
 "default_branch":"main","deploy_key_ref":tmp+"/key","charter":charter,"allowed_paths":["src"],
 "topic":11,"pilot_id":"pilot-alpha","activation_gate":"clone-auth-freshness-v1",
 "notification_targets":["topic:11","head-hermes"],"goal_source":"state/goals","status":"active"}
pilot={"schema_version":1,"id":"pilot-alpha","project_id":"alpha","topic":11,"charter":charter,
 "model_policy":"project-pilot","concurrency_limit":0,"budget":{"max_inflight_workers":0},
 "notification_targets":cfg["notification_targets"],"goal_source":"state/goals",
 "memory_key":"telegram-topic:11","worktree_root":".worktrees/alpha","status":"active"}
for directory,value in (("project-config",cfg),("pilots",pilot)):
    with open(os.path.join(root,"state",directory,value["id"]+".json"),"w",encoding="utf-8") as out:
        json.dump(value,out); out.write("\n")
PY
cat > "$P/state/goals/goal-alpha.md" <<'T'
schema_version: 1
id: goal-alpha
project_id: alpha
status: active
outcome: bounded alpha change
acceptance_suite: test -f src/result.txt
falsifier: work escapes alpha
budget: phase4 fixture
T
cat > "$P/state/tasks/alpha-base.md" <<'T'
id: alpha-base
project_id: alpha
goal_id: goal-alpha
status: passed
T
cat > "$P/state/instructions/00000042.md" <<'T'
schema_version: 1
id: 42
project_id: alpha
pilot_id: pilot-alpha
pilot_memory_key: telegram-topic:11
routing_target: pilot-alpha
status: open
T
cat > "$TMP/task-decision.json" <<'J'
{"schema_version":1,"id":"decision-alpha-task","actor":"pilot-alpha","decision_source":"hermes-model","routed_decider":"pilot-alpha","verb":"pilot-task-create","args":["alpha","goal-alpha","alpha-next","src","alpha-base"],"project":"alpha","goal":"goal-alpha","text":"produce the bounded alpha result","instruction_id":"42","idempotency_key":"alpha-task","why":"materialize one bounded pilot task","wrong_if":"scope escapes"}
J
RECURSION_ROOT="$P" python3 "$P/scripts/decision-queue.py" normalize \
  < "$TMP/task-decision.json" > "$TMP/task-decision.normalized.json"
mv -f "$TMP/task-decision.normalized.json" "$TMP/task-decision.json"
set +e
( cd "$P" && RECURSION_ROOT="$P" RECURSION_QUEUE_ACTUATION=1 \
  bash scripts/conduct-hermes.sh --file "$TMP/task-decision.json" ) \
  >"$TMP/pilot-conductor.out" 2>&1
pilot_rc=$?
set -e
if [ "$pilot_rc" -ne 0 ]; then
  echo "FAIL  pilot task actuation fixture rc=$pilot_rc" >&2
  sed 's/^/      /' "$TMP/pilot-conductor.out" >&2
  exit "$pilot_rc"
fi
grep -q '^project_id: alpha$' "$P/state/tasks/alpha-next.md"
grep -q '^dependencies: alpha-base$' "$P/state/tasks/alpha-next.md"
grep -q '^allowed_paths: src$' "$P/state/tasks/alpha-next.md"
grep -q '^acceptance: test -f src/result.txt$' "$P/state/tasks/alpha-next.md"
grep -q '^status: proposed$' "$P/state/tasks/alpha-next.md"
grep -q '^status: acknowledged$' "$P/state/instructions/00000042.md"
python3 - "$P/state/actions" <<'PY'
import json,sys
from pathlib import Path
rows=[json.load(open(path,encoding='utf-8')) for path in Path(sys.argv[1]).glob('*.json')]
assert len(rows)==1 and rows[0]['status']=='succeeded' and rows[0]['verb']=='pilot-task-create'
PY
echo "ok    pilot task verb is charter-, goal-, dependency-, gate-, and action-coupled without dispatch"

# Registration's positive direction proves the gate is usable: a complete pending record plus a
# key, clean clone, and exact remote OID becomes active and records the proof.
A="$TMP/activation"; mkdir -p "$A/scripts" "$A/state/project-config" "$A/state/pilots" "$A/state/.locks"
cp "$SRC/scripts/project-pilot.py" "$SRC/scripts/jsonl_durable.py" \
   "$SRC/scripts/transition_receipt.py" "$SRC/scripts/runtime-state.py" "$A/scripts/"
KEY="$TMP/activation-key"; : > "$KEY"; chmod 600 "$KEY"
ORIGIN="$TMP/activation.git"; SEED="$TMP/activation-seed"; CLONE="$TMP/activation-clone"
git -c init.defaultBranch=main init -q --bare "$ORIGIN"
git -c init.defaultBranch=main init -q "$SEED"
( cd "$SEED" && mkdir src && printf x > src/f && git add src/f && git -c user.name=t -c user.email=t@t commit -qm init \
  && git branch -M main && git remote add origin "$ORIGIN" && git push -q origin main )
printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > "$A/state/portfolio.tsv"
printf 'new-project\t%s\t%s\tmain\t%s\t-\t33\tpending\n' "$CLONE" "$ORIGIN" "$KEY" >> "$A/state/portfolio.tsv"
python3 - "$A" "$CLONE" "$ORIGIN" "$KEY" <<'PY'
import json,os,sys
root,repo,remote,key=sys.argv[1:]
charter="new project src only"
cfg={"schema_version":1,"id":"new-project","repo":repo,"remote":remote,"default_branch":"main",
 "deploy_key_ref":key,"charter":charter,"allowed_paths":["src"],"topic":33,
 "pilot_id":"pilot-new-project","activation_gate":"clone-auth-freshness-v1",
 "notification_targets":["head-hermes"],"goal_source":"state/goals","status":"pending"}
pilot={"schema_version":1,"id":"pilot-new-project","project_id":"new-project","topic":33,
 "charter":charter,"model_policy":"project-pilot","concurrency_limit":0,
 "budget":{"max_inflight_workers":0},"notification_targets":["head-hermes"],
 "goal_source":"state/goals","memory_key":"telegram-topic:33",
 "worktree_root":".worktrees/new-project","status":"pending"}
for directory,value in (("project-config",cfg),("pilots",pilot)):
    with open(os.path.join(root,"state",directory,value["id"]+".json"),"w",encoding="utf-8") as out:
        json.dump(value,out); out.write("\n")
PY
RECURSION_ROOT="$A" python3 "$A/scripts/project-pilot.py" activate new-project > "$TMP/proof.json"
grep -q $'new-project\t.*\tactive$' "$A/state/portfolio.tsv"
grep -q '"gate":"clone-auth-freshness-v1"' "$TMP/proof.json"
head="$(git -C "$CLONE" rev-parse HEAD)"; grep -q "$head" "$TMP/proof.json"
RECURSION_ROOT="$A" python3 "$A/scripts/project-pilot.py" repo new-project src/f > "$TMP/repo-read.json"
grep -q '"path":"src/f"' "$TMP/repo-read.json"; grep -q '"content":"x"' "$TMP/repo-read.json"
echo "ok    two-step registration activates only after clone/auth/freshness proof"

echo "hermes-pilot-phase4-green: ALL PASS"

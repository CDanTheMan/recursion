#!/usr/bin/env bash
# Positive Phase 2 artifact/recovery audit. Hermetic: no model, network, production, or publication.
set -euo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# The schema bundle must name every Phase 2 object and the dependency-free validator must accept
# one complete v1 record of each type.
python3 - "$SRC" "$TMP" <<'PY'
import json,os,sys
root,tmp=sys.argv[1:3]
schema=json.load(open(os.path.join(root,'schemas/control-plane/v1/schema.json'),encoding='utf-8'))
kinds=('project','pilot','goal','task','run','decision','escalation','delivery','instruction','action')
assert set(kinds) <= set(schema.get('$defs',{}))
samples={
'project':{'schema_version':1,'id':'p','repo':'git@example/p','default_branch':'main','deploy_key_ref':'key','charter':'c','topic':1,'pilot_id':'pilot','status':'active'},
'pilot':{'schema_version':1,'id':'pilot','project_id':'p','charter':'c','model_policy':'human alias','status':'active'},
'goal':{'schema_version':1,'id':'g','project_id':'p','outcome':'o','acceptance_suite':'true','falsifier':'false green','budget':{},'status':'active'},
'task':{'schema_version':1,'id':'t','goal_id':'g','dependencies':[],'allowed_paths':['app'],'non_goals':['tests'],'worker_class':'claude','acceptance':'true','status':'ready'},
'run':{'schema_version':1,'id':'r','task_id':'t','worker':'w','worktree':'/tmp/w','base_commit':'0'*40,'pid':1,'lease_expires':'later','deadline':'later','usage':{},'result':{},'status':'pending'},
'decision':{'schema_version':1,'id':'d','actor':'head-hermes','verb':'work','arguments':['t'],'reason':'r','goal_id':'g','idempotency_key':'k','status':'accepted'},
'escalation':{'schema_version':1,'id':'e','goal_id':'g','required_actor':'Lucas','question':'q','evidence':{},'status':'open'},
'delivery':{'schema_version':1,'id':'delivery','event_id':'event','destination':'topic:1','attempt':0,'acknowledgement':None,'status':'pending'},
'instruction':{'schema_version':1,'id':'i','principal':'Lucas','topic':1,'project_id':'p','deduplication_key':'k','status':'open','action_ids':[]},
'action':{'schema_version':1,'id':'action-a','idempotency_key':'k','verb':'work','arguments':['t'],'goal_id':'g','status':'pending','lease_expires':None,'attempts':0,'result_evidence':None},
}
for kind,value in samples.items():
    with open(os.path.join(tmp,kind+'.json'),'w',encoding='utf-8') as out: json.dump(value,out)
PY
for kind in project pilot goal task run decision escalation delivery instruction action; do
  python3 "$SRC/scripts/validate-control-state.py" "$kind" "$TMP/$kind.json" >/dev/null
done
echo "ok    versioned schemas and validator cover all ten control-state objects"

# One decision with an instruction correlation creates one durable action. Consumption records
# exactly that action id; acknowledgement is refused until/if every coupled action succeeded.
R="$TMP/control"; mkdir -p "$R/scripts" "$R/state/tasks" "$R/state/goals" \
  "$R/state/instructions" "$R/loop/logs"
cp "$SRC/scripts/conduct-hermes.sh" "$SRC/scripts/taskctl.sh" "$SRC/scripts/intake.sh" "$R/scripts/"
cat > "$R/scripts/work.sh" <<'STUB'
#!/usr/bin/env bash
printf 'launch\n' >> "$ACTION_LOG"
STUB
chmod +x "$R/scripts/"*.sh
cat > "$R/state/goals/g.md" <<'T'
id: g
status: active
T
cat > "$R/state/tasks/t.md" <<'T'
id: t
goal_id: g
dependencies:
acceptance: true
status: queued
T
cat > "$R/state/instructions/00000042.md" <<'T'
schema_version: 1
id: 42
status: open
action_ids:

## INSTRUCTION
work t
T
cat > "$TMP/decision.json" <<'J'
{"id":"d","idempotency_key":"instruction-42-work-t","instruction_id":"42","verb":"work","args":["t"],"goal":"g","wrong_if":"duplicate"}
J
: > "$TMP/action.log"
( cd "$R" && ACTION_LOG="$TMP/action.log" RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --file "$TMP/decision.json" ) >/dev/null 2>&1
ACTION_FILE="$(find "$R/state/actions" -maxdepth 1 -name 'action-*.json' -type f)"
ACTION_ID="$(basename "$ACTION_FILE" .json)"
[ "$(wc -l < "$TMP/action.log" | tr -d ' ')" = 1 ]
python3 "$SRC/scripts/validate-control-state.py" action "$ACTION_FILE" >/dev/null
( cd "$R" && RECURSION_ROOT="$R" bash scripts/intake.sh consume 42 "$ACTION_ID" ) >/dev/null
grep -q '^status: consumed$' "$R/state/instructions/00000042.md"
grep -q "^action_ids: $ACTION_ID$" "$R/state/instructions/00000042.md"
( cd "$R" && RECURSION_ROOT="$R" bash scripts/intake.sh acknowledge 42 "$ACTION_ID" ) >/dev/null
grep -q '^status: acknowledged$' "$R/state/instructions/00000042.md"
if ( cd "$R" && RECURSION_ROOT="$R" bash scripts/intake.sh consume 42 action-000000000000000000000000 ) >/dev/null 2>&1; then
  echo "FAIL  uncoupled action was accepted"; exit 1
fi
echo "ok    instruction consumption/acknowledgement is coupled to the exact succeeded action"

# Rotation plus manifest-hashed backup/restore of ignored runtime state. The fixture PAUSE is
# never removed; production is not addressed by this audit.
RR="$TMP/runtime"; SNAP="$TMP/runtime-snapshot"
mkdir -p "$RR/state/actions" "$RR/state/instructions"
printf 'PAUSED test\n' > "$RR/state/PAUSE"
printf '{"event":"one"}\n{"event":"two"}\n' > "$RR/state/events.jsonl"
printf '{"schema_version":1,"id":"action-a"}\n' > "$RR/state/actions/action-a.json"
printf 'id: 1\nstatus: open\n' > "$RR/state/instructions/00000001.md"
RECURSION_ROOT="$RR" python3 "$SRC/scripts/runtime-state.py" rotate-events --max-bytes 1 >/dev/null
[ ! -s "$RR/state/events.jsonl" ]
[ "$(find "$RR/state/event-archive" -name 'events-*.jsonl' -type f | wc -l | tr -d ' ')" = 1 ]
RECURSION_ROOT="$RR" python3 "$SRC/scripts/runtime-state.py" backup "$SNAP" >/dev/null
printf 'corrupt\n' > "$RR/state/events.jsonl"
printf 'corrupt\n' > "$RR/state/actions/action-a.json"
RECURSION_ROOT="$RR" python3 "$SRC/scripts/runtime-state.py" restore "$SNAP" >/dev/null
[ ! -s "$RR/state/events.jsonl" ]
python3 - "$SNAP" "$RR" <<'PY'
import hashlib,json,os,sys
snap,root=sys.argv[1:3]
m=json.load(open(os.path.join(snap,'manifest.json')))
for row in m['files']:
    p=os.path.join(root,*row['path'].split('/'))
    assert hashlib.sha256(open(p,'rb').read()).hexdigest()==row['sha256']
assert os.path.isfile(os.path.join(root,'state/PAUSE'))
PY
echo "ok    PAUSE-gated event rotation and manifest-hashed backup/restore passed"

echo "hermes-pilot-phase2-green: ALL PASS"

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
'run':{'schema_version':1,'id':'r','task_id':'t','worker':'w','worktree':'/tmp/w','base_commit':'0'*40,'pid':1,'process_group':1,'lease_expires':'later','deadline':'later','usage':{},'result':{},'status':'pending'},
'decision':{'schema_version':1,'id':'d','actor':'head-hermes','verb':'work','arguments':['t'],'reason':'r','goal_id':'g','idempotency_key':'k','status':'accepted','decision_source':'hermes-model'},
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
cp "$SRC/scripts/conduct-hermes.sh" "$SRC/scripts/taskctl.sh" "$SRC/scripts/intake.sh" \
  "$SRC/scripts/jsonl_durable.py" "$SRC/scripts/transition_receipt.py" \
  "$SRC/scripts/decision-queue.py" "$SRC/scripts/validate-control-state.py" \
  "$SRC/scripts/engine_contract.py" \
  "$SRC/scripts/validate-decision.py" "$SRC/scripts/assignment.py" \
  "$SRC/scripts/phase5_safety.py" "$SRC/scripts/runtime-state.py" "$R/scripts/"
normalize_head_decision(){
  local file="$1" temporary="$1.normalized"
  python3 - "$file" <<'PY' | RECURSION_ROOT="$R" python3 "$R/scripts/decision-queue.py" normalize > "$temporary"
import json,sys
path=sys.argv[1]
row=json.load(open(path,encoding='utf-8'))
row.setdefault('actor','head-hermes')
row.setdefault('decision_source','hermes-model')
row.setdefault('routed_decider','head-hermes')
row.setdefault('why',row.get('reason') or 'Phase 2 control')
print(json.dumps(row,separators=(',',':')))
PY
  mv -f "$temporary" "$file"
}
cat > "$R/scripts/work.sh" <<'STUB'
#!/usr/bin/env bash
printf 'launch\n' >> "$ACTION_LOG"
exit "${WORK_RC:-0}"
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
normalize_head_decision "$TMP/decision.json"
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

# An explicit idempotency-key collision must not let a different decision/instruction reuse the
# first action record or dispatch different argv under its identity.
cat > "$TMP/collision.json" <<'J'
{"id":"d-collision","idempotency_key":"instruction-42-work-t","instruction_id":"99","verb":"work","args":["different-task"],"goal":"different-goal","wrong_if":"key collision suppresses distinct authority"}
J
normalize_head_decision "$TMP/collision.json"
collision_before="$(sha256sum "$ACTION_FILE" | awk '{print $1}')"
collision_launches="$(wc -l < "$TMP/action.log" | tr -d ' ')"
set +e
( cd "$R" && ACTION_LOG="$TMP/action.log" RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --file "$TMP/collision.json" ) >"$TMP/collision.out" 2>&1
collision_rc=$?
set -e
[ "$collision_rc" -eq 74 ]
[ "$(sha256sum "$ACTION_FILE" | awk '{print $1}')" = "$collision_before" ]
[ "$(wc -l < "$TMP/action.log" | tr -d ' ')" = "$collision_launches" ]
grep -q 'identity collision' "$TMP/collision.out"
echo "ok    idempotency-key collision cannot change authority, evidence, or dispatch argv"

# A noop can terminalize an authenticated instruction, so it is an action, not an opinion. The
# only admitted case is the poisoned-topic escape hatch: two distinct failed pilot actions for
# THIS instruction, both visible in OPEN annotations and both carrying the exact durable refusal.
# Three guard failures must not manufacture their own proof and eventually acknowledge the input.
cat > "$R/state/instructions/00000048.md" <<'T'
schema_version: 1
id: 48
status: open
action_ids:

## INSTRUCTION
Approve the exact plan.
T
for attempt in 1 2 3; do
  cat > "$TMP/unsupported-noop-$attempt.json" <<J
{"id":"d-unsupported-noop-$attempt","idempotency_key":"unsupported-noop-$attempt","instruction_id":"48","verb":"noop","args":[],"text":"Instruction cannot bind as posted.","goal":"g","wrong_if":"the approval can bind"}
J
  normalize_head_decision "$TMP/unsupported-noop-$attempt.json"
  set +e
  ( cd "$R" && RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$R" \
      bash scripts/conduct-hermes.sh --file "$TMP/unsupported-noop-$attempt.json" ) \
    >"$TMP/unsupported-noop-$attempt.out" 2>&1
  unsupported_rc=$?
  set -e
  [ "$unsupported_rc" -eq 4 ]
  UNSUPPORTED_ID="action-$(printf '%s' "unsupported-noop-$attempt" | sha256sum | cut -c1-24)"
  [ "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' \
      "$R/state/actions/$UNSUPPORTED_ID.json")" = failed ]
  grep -q '^status: open$' "$R/state/instructions/00000048.md"
done
[ "$(grep -c 'cannot-bind noop evidence is absent' "$R/state/instructions/00000048.md")" = 3 ]
! grep -q 'project-pilot: instruction is not owned by this project pilot' \
  "$R/state/instructions/00000048.md"
echo "ok    unsupported instruction noop fails and repeated guard failures cannot self-authorize"

REFUSAL='project-pilot: instruction is not owned by this project pilot'
for aid in action-aaaaaaaaaaaaaaaaaaaaaaaa action-bbbbbbbbbbbbbbbbbbbbbbbb; do
  cat > "$R/state/actions/$aid.json" <<J
{"schema_version":1,"id":"$aid","decision_id":"prior-$aid","instruction_id":"49","idempotency_key":"prior-$aid","verb":"pilot-plan-approve","arguments":[],"goal_id":"g","action_payload_sha256":"$(printf '%064d' 0)","status":"failed","lease_owner":null,"lease_expires":null,"attempts":1,"result_evidence":"log=fixture rc=4 | $REFUSAL","created_at":"2026-01-01T00:00:00Z","updated_at":"2026-01-01T00:00:01Z"}
J
done
cat > "$R/state/instructions/00000049.md" <<T
schema_version: 1
id: 49
status: open
action_ids: action-bbbbbbbbbbbbbbbbbbbbbbbb

## INSTRUCTION
Approve the exact plan.

## OPEN 2026-01-01T00:00:01Z
deferred/failed actions reopened instruction: action-aaaaaaaaaaaaaaaaaaaaaaaa | last failure: log=fixture rc=4 | $REFUSAL

## OPEN 2026-01-01T00:00:02Z
deferred/failed actions reopened instruction: action-bbbbbbbbbbbbbbbbbbbbbbbb | last failure: log=fixture rc=4 | $REFUSAL
T
cat > "$TMP/supported-noop.json" <<'J'
{"id":"d-supported-noop","idempotency_key":"supported-noop","instruction_id":"49","verb":"noop","args":[],"text":"Instruction cannot bind as posted.","goal":"g","wrong_if":"the ownership refusal changes"}
J
normalize_head_decision "$TMP/supported-noop.json"
( cd "$R" && RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --file "$TMP/supported-noop.json" ) >/dev/null 2>&1
SUPPORTED_ID="action-$(printf '%s' supported-noop | sha256sum | cut -c1-24)"
[ "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' \
    "$R/state/actions/$SUPPORTED_ID.json")" = succeeded ]
grep -q '^status: acknowledged$' "$R/state/instructions/00000049.md"
echo "ok    two annotated same-instruction pilot ownership refusals admit the closing noop"

cat > "$R/state/instructions/00000050.md" <<T
schema_version: 1
id: 50
status: open
action_ids:

## INSTRUCTION
Approve another exact plan.

## OPEN 2026-01-01T00:00:01Z
deferred/failed actions reopened instruction: action-aaaaaaaaaaaaaaaaaaaaaaaa | last failure: log=fixture rc=4 | $REFUSAL

## OPEN 2026-01-01T00:00:02Z
deferred/failed actions reopened instruction: action-bbbbbbbbbbbbbbbbbbbbbbbb | last failure: log=fixture rc=4 | $REFUSAL
T
cat > "$TMP/foreign-noop.json" <<'J'
{"id":"d-foreign-noop","idempotency_key":"foreign-noop","instruction_id":"50","verb":"noop","args":[],"text":"Instruction cannot bind as posted.","goal":"g","wrong_if":"another instruction's evidence is borrowed"}
J
normalize_head_decision "$TMP/foreign-noop.json"
set +e
( cd "$R" && RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --file "$TMP/foreign-noop.json" ) >/dev/null 2>&1
foreign_rc=$?
set -e
[ "$foreign_rc" -eq 4 ]
FOREIGN_ID="action-$(printf '%s' foreign-noop | sha256sum | cut -c1-24)"
[ "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' \
    "$R/state/actions/$FOREIGN_ID.json")" = failed ]
grep -q '^status: open$' "$R/state/instructions/00000050.md"
echo "ok    one instruction cannot borrow another instruction's ownership failures"

# Freeze the validator-approved JSON. The validator shim swaps the on-disk projection after it
# returns OK; the actuator must still execute/record the original noop, never the replacement work.
cp "$R/scripts/validate-decision.py" "$R/scripts/validate-decision-real.py"
cat > "$R/scripts/validate-decision.py" <<'STUB'
#!/usr/bin/env python3
import os, subprocess, sys
from pathlib import Path

real = Path(__file__).with_name("validate-decision-real.py")
result = subprocess.run(
    [sys.executable, str(real), *sys.argv[1:]], text=True, capture_output=True, check=False,
)
Path(os.environ["SWAP_FILE"]).write_text(os.environ["SWAP_REPLACEMENT"] + "\n", encoding="utf-8")
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
raise SystemExit(result.returncode)
STUB
chmod +x "$R/scripts/validate-decision.py"
cat > "$TMP/frozen.json" <<'J'
{"id":"d-frozen","idempotency_key":"frozen-decision","verb":"noop","args":[],"goal":"g","wrong_if":"mutable projection changes authority"}
J
normalize_head_decision "$TMP/frozen.json"
SWAP_REPLACEMENT='{"id":"d-swapped","idempotency_key":"frozen-decision","verb":"work","args":["t"],"goal":"g","wrong_if":"swap executes"}'
frozen_launches="$(wc -l < "$TMP/action.log" | tr -d ' ')"
( cd "$R" && ACTION_LOG="$TMP/action.log" SWAP_FILE="$TMP/frozen.json" \
    SWAP_REPLACEMENT="$SWAP_REPLACEMENT" RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --file "$TMP/frozen.json" ) >/dev/null
FROZEN_ID="action-$(printf '%s' frozen-decision | sha256sum | cut -c1-24)"
[ "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["verb"])' \
      "$R/state/actions/$FROZEN_ID.json")" = noop ]
[ "$(wc -l < "$TMP/action.log" | tr -d ' ')" = "$frozen_launches" ]
mv "$R/scripts/validate-decision-real.py" "$R/scripts/validate-decision.py"
chmod +x "$R/scripts/validate-decision.py"
echo "ok    actuator freezes one validated decision across a concurrent projection replacement"

cat > "$R/state/instructions/00000043.md" <<'T'
schema_version: 1
id: 43
status: open
action_ids:

## INSTRUCTION
work t
T
cat > "$TMP/deferred-decision.json" <<'J'
{"id":"d-deferred","idempotency_key":"instruction-43-work-t","instruction_id":"43","verb":"work","args":["t"],"goal":"g","wrong_if":"deferred work is terminalized"}
J
normalize_head_decision "$TMP/deferred-decision.json"
set +e
( cd "$R" && ACTION_LOG="$TMP/action.log" WORK_RC=75 RECURSION_QUEUE_ACTUATION=1 \
    RECURSION_ROOT="$R" bash scripts/conduct-hermes.sh --file "$TMP/deferred-decision.json" ) \
  >"$TMP/deferred.out" 2>&1
deferred_rc=$?
set -e
DEFERRED_ID="action-$(printf '%s' instruction-43-work-t | sha256sum | cut -c1-24)"
[ "$deferred_rc" -eq 75 ]
[ "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' \
      "$R/state/actions/$DEFERRED_ID.json")" = pending ]
grep -q '^status: open$' "$R/state/instructions/00000043.md"
echo "ok    rc=75 defers the action and reopens its exact consumed instruction"

# A refusal after the durable claim must not strand an action in running forever. That state is
# inspected before every later queue admission, so one missing task would otherwise wedge the
# sole actuator until a human found and replayed the exact file.
cat > "$TMP/refused-decision.json" <<'J'
{"id":"d-refused","idempotency_key":"refused-missing-task","verb":"work","args":["missing-task"],"goal":"g","wrong_if":"missing task is dispatched"}
J
normalize_head_decision "$TMP/refused-decision.json"
set +e
( cd "$R" && RECURSION_ROOT="$R" bash scripts/conduct-hermes.sh --file "$TMP/refused-decision.json" ) \
  >"$TMP/refused.out" 2>&1
refused_rc=$?
set -e
REFUSED_ID="action-$(printf '%s' refused-missing-task | sha256sum | cut -c1-24)"
[ "$refused_rc" -ne 0 ]
[ "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' \
      "$R/state/actions/$REFUSED_ID.json")" = failed ]
echo "ok    post-claim actuator refusal reaches a durable failed action instead of wedging running"

cat > "$TMP/recover-decision.json" <<'J'
{"id":"d-recover","idempotency_key":"recover-expired","verb":"work","args":["t"],"goal":"g","wrong_if":"recovery launches work"}
J
normalize_head_decision "$TMP/recover-decision.json"
RECOVER_ID="action-$(printf '%s' recover-expired | sha256sum | cut -c1-24)"
RECOVER_PAYLOAD="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["decision_payload_sha256"])' "$TMP/recover-decision.json")"
cat > "$R/state/actions/$RECOVER_ID.json" <<J
{"schema_version":1,"id":"$RECOVER_ID","decision_id":"d-recover","instruction_id":null,"idempotency_key":"recover-expired","verb":"work","arguments":["t"],"goal_id":"g","action_payload_sha256":"$RECOVER_PAYLOAD","status":"running","lease_owner":"dead@fixture","lease_expires":1,"attempts":1,"result_evidence":null,"created_at":"2026-01-01T00:00:00Z","updated_at":"2026-01-01T00:00:00Z"}
J
before_launches="$(wc -l < "$TMP/action.log" | tr -d ' ')"
set +e
( cd "$R" && ACTION_LOG="$TMP/action.log" RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --recover-only --file "$TMP/recover-decision.json" ) \
  >"$TMP/recover.out" 2>&1
recover_rc=$?
set -e
[ "$recover_rc" -ne 0 ]
[ "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' \
      "$R/state/actions/$RECOVER_ID.json")" = failed ]
[ "$(wc -l < "$TMP/action.log" | tr -d ' ')" = "$before_launches" ]
echo "ok    expired-action recovery terminalizes without relaunching worker code"

# A crash after the terminal action write but before instruction projection recovery must not
# strand authenticated input in consumed forever. Recovery is idempotent and never dispatches.
cat > "$R/state/instructions/00000044.md" <<'T'
schema_version: 1
id: 44
status: consumed
action_ids: action-placeholder

## INSTRUCTION
work t
T
cat > "$TMP/recover-succeeded.json" <<'J'
{"id":"d-recover-succeeded","idempotency_key":"recover-succeeded","instruction_id":"44","verb":"work","args":["t"],"goal":"g","wrong_if":"terminal recovery relaunches"}
J
normalize_head_decision "$TMP/recover-succeeded.json"
RECOVER_SUCCEEDED_ID="action-$(printf '%s' recover-succeeded | sha256sum | cut -c1-24)"
RECOVER_SUCCEEDED_PAYLOAD="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["decision_payload_sha256"])' "$TMP/recover-succeeded.json")"
sed -i "s/action-placeholder/$RECOVER_SUCCEEDED_ID/" "$R/state/instructions/00000044.md"
cat > "$R/state/actions/$RECOVER_SUCCEEDED_ID.json" <<J
{"schema_version":1,"id":"$RECOVER_SUCCEEDED_ID","decision_id":"d-recover-succeeded","instruction_id":"44","idempotency_key":"recover-succeeded","verb":"work","arguments":["t"],"goal_id":"g","action_payload_sha256":"$RECOVER_SUCCEEDED_PAYLOAD","status":"succeeded","lease_owner":null,"lease_expires":null,"attempts":1,"result_evidence":"work complete","created_at":"2026-01-01T00:00:00Z","updated_at":"2026-01-01T00:00:01Z"}
J
before_launches="$(wc -l < "$TMP/action.log" | tr -d ' ')"
( cd "$R" && ACTION_LOG="$TMP/action.log" RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --recover-only --file "$TMP/recover-succeeded.json" ) >/dev/null
( cd "$R" && ACTION_LOG="$TMP/action.log" RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --recover-only --file "$TMP/recover-succeeded.json" ) >/dev/null
[ "$(sed -n 's/^status: *//p' "$R/state/instructions/00000044.md" | head -1)" = acknowledged ]
[ "$(wc -l < "$TMP/action.log" | tr -d ' ')" = "$before_launches" ]
echo "ok    succeeded-action recovery acknowledges its exact instruction once without relaunch"

# The corresponding rc75 crash seam leaves a pending action plus consumed instruction. Recovery
# completes the defer handshake: instruction open, action pending, no worker launch.
cat > "$R/state/instructions/00000045.md" <<'T'
schema_version: 1
id: 45
status: consumed
action_ids: action-placeholder

## INSTRUCTION
work t
T
cat > "$TMP/recover-pending.json" <<'J'
{"id":"d-recover-pending","idempotency_key":"recover-pending","instruction_id":"45","verb":"work","args":["t"],"goal":"g","wrong_if":"defer recovery terminalizes or relaunches"}
J
normalize_head_decision "$TMP/recover-pending.json"
RECOVER_PENDING_ID="action-$(printf '%s' recover-pending | sha256sum | cut -c1-24)"
RECOVER_PENDING_PAYLOAD="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["decision_payload_sha256"])' "$TMP/recover-pending.json")"
sed -i "s/action-placeholder/$RECOVER_PENDING_ID/" "$R/state/instructions/00000045.md"
cat > "$R/state/actions/$RECOVER_PENDING_ID.json" <<J
{"schema_version":1,"id":"$RECOVER_PENDING_ID","decision_id":"d-recover-pending","instruction_id":"45","idempotency_key":"recover-pending","verb":"work","arguments":["t"],"goal_id":"g","action_payload_sha256":"$RECOVER_PENDING_PAYLOAD","status":"pending","lease_owner":null,"lease_expires":null,"attempts":1,"result_evidence":"deferred rc=75","created_at":"2026-01-01T00:00:00Z","updated_at":"2026-01-01T00:00:01Z"}
J
set +e
( cd "$R" && ACTION_LOG="$TMP/action.log" RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$R" \
    bash scripts/conduct-hermes.sh --recover-only --file "$TMP/recover-pending.json" ) >/dev/null 2>&1
recover_pending_rc=$?
set -e
[ "$recover_pending_rc" -eq 75 ]
[ "$(sed -n 's/^status: *//p' "$R/state/instructions/00000045.md" | head -1)" = open ]
[ "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' \
      "$R/state/actions/$RECOVER_PENDING_ID.json")" = pending ]
[ "$(wc -l < "$TMP/action.log" | tr -d ' ')" = "$before_launches" ]
echo "ok    pending-action recovery completes the PAUSE defer handshake without relaunch"

# Interleave runtime maintenance immediately after the witnessed action lock's atomic publish.
# The writer's post-publish check must remove its own complete lock and refuse the mutation.
python3 - "$SRC/scripts/runtime-state.py" "$R" <<'PY'
import importlib.util,os,shutil,subprocess,sys
from pathlib import Path

source,root=Path(sys.argv[1]),Path(sys.argv[2])
spec=importlib.util.spec_from_file_location("phase2_runtime_state",source)
module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
locks=root/"state/.locks"; locks.mkdir(parents=True,exist_ok=True)
action=locks/"action-action-race.lock"; runtime=locks/"runtime-state.lock"
sleeper=subprocess.Popen(["sleep","30"])
real_rename=module._rename_noreplace
def interleave(candidate,target):
    real_rename(candidate,target)
    if target == action:
        runtime.mkdir()
        module.atomic_bytes(runtime/"pid",f"{sleeper.pid}\n".encode("ascii"))
        module.atomic_bytes(runtime/"start",(module.process_start(sleeper.pid)+"\n").encode("ascii"))
        module.fsync_dir(runtime)
module._rename_noreplace=interleave
try:
    try:
        module.acquire_witnessed_directory_lock(action,"action",os.getpid())
    except RuntimeError as exc:
        assert "runtime-state maintenance is active" in str(exc),exc
    else:
        raise AssertionError("writer crossed post-publish maintenance interleave")
    assert not action.exists()
finally:
    sleeper.terminate(); sleeper.wait(timeout=5)
    shutil.rmtree(runtime,ignore_errors=True)
PY
echo "ok    action/maintenance lock handshake closes the post-publish interleaving"

# Rotation plus manifest-hashed backup/restore of ignored runtime state. The fixture PAUSE is
# never removed; production is not addressed by this audit.
RR="$TMP/runtime"; SNAP="$TMP/runtime-snapshot"
mkdir -p "$RR/state/actions" "$RR/state/instructions" "$RR/state/tasks" "$RR/state/assists"
printf 'PAUSED test\n' > "$RR/state/PAUSE"
printf '' > "$RR/state/events.jsonl"
cat > "$RR/state/tasks/t.md" <<'J'
id: t
project_id: p
pilot_id: pilot-p
goal_id: g
status: blocked
J
cat > "$RR/state/assists/t.md" <<'J'
task: t
kind: decision
status: open
asked: 2026-08-10T00:00:00Z
asked_by: test
answered:
answered_by:

## QUESTION
needs Lucas

## WHAT WOULD SATISFY THIS
A reviewed answer.

## ANSWER
_(unanswered)_
J
printf '{"schema_version":1,"id":"action-a"}\n' > "$RR/state/actions/action-a.json"
printf 'id: 1\nstatus: open\n' > "$RR/state/instructions/00000001.md"
python3 - "$SRC/scripts" "$RR" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from transition_receipt import commit_event
commit_event(Path(sys.argv[2]), {
    "schema_version":1,"id":"source-assist-rotation","ts":"2026-08-10T00:00:00Z",
    "event":"assist-open","task":"t","project":"p","goal":"g","pid":1,
    "detail":"decision: needs Lucas",
})
PY
before_rotation="$(sha256sum "$RR/state/events.jsonl" | awk '{print $1}')"
if RECURSION_ROOT="$RR" python3 "$SRC/scripts/runtime-state.py" rotate-events --max-bytes 1 \
     >"$TMP/rotation-refusal.out" 2>&1; then
  echo "FAIL  event rotation archived an unreconciled mapped source event"; exit 1
fi
[ "$(sha256sum "$RR/state/events.jsonl" | awk '{print $1}')" = "$before_rotation" ]
mkdir -p "$RR/state/project-config" "$RR/state/pilots"
cat > "$RR/state/project-config/p.json" <<'J'
{"id":"p","pilot_id":"pilot-p","status":"active","notification_targets":["project-topic:telegram:-100:11","head-hermes:telegram:-100:12","lucas-direct:telegram:123"]}
J
cat > "$RR/state/pilots/pilot-p.json" <<'J'
{"id":"pilot-p","project_id":"p","status":"active","notification_targets":["project-topic:telegram:-100:11","head-hermes:telegram:-100:12","lucas-direct:telegram:123"]}
J
python3 - "$SRC/scripts/notification-outbox.py" "$RR" <<'PY'
import importlib.util,json,sys
from pathlib import Path
source=Path(sys.argv[1]); root=Path(sys.argv[2])
sys.path.insert(0,str(source.parent))
spec=importlib.util.spec_from_file_location('phase2_notification_outbox',source)
module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
event=module.all_mapped(root)[0]
projection=module.create_event(root,event)
deliveries=[row for _,row in module.delivery_records(root,'p') if row.get('event_id') == event['id']]
assert projection['source_event_id'] == event['source_event_id']
assert len(deliveries) == 1 and deliveries[0]['destination'] == 'lucas-direct:telegram:123'
assert projection['message_digest'] == deliveries[0]['message_digest']
PY
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
echo "ok    PAUSE-gated rotation preserves unreconciled events and backup/restore remains manifest-hashed"

echo "hermes-pilot-phase2-green: ALL PASS"

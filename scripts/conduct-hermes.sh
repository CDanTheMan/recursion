#!/usr/bin/env bash
# conduct-hermes.sh — execute ONE validated Hermes decision through existing tooling.
#
# This is the actuator half of the split in hermes-decide.sh. Hermes decides in text and
# cannot act; this script acts and cannot decide. Neither half can do the other's job, which
# is what keeps the executive on the flat subscription and out of the implementer's seat.
#
# ★ THE MODEL'S OUTPUT BECOMES PROCESS ARGUMENTS. That is an injection surface, so:
#   - every verb is matched against a fixed case list — there is no computed dispatch;
#   - every argument is re-validated HERE, not trusted from the decision file, because the
#     file can be edited between decide and conduct;
#   - execution uses argv arrays, never eval, never a constructed shell string.
# A decision this script does not recognise does nothing at all.
#
#   conduct-hermes.sh                 drain every durable pending decision
#   conduct-hermes.sh --file <path>   execute a specific decision file
#   conduct-hermes.sh --dry-run       print what would run, execute nothing
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a
# .env pins RECURSION_ROOT for the deployed checkout. Sourcing it must never RETARGET a
# caller who passed a different root: that silently made a "sandbox" enqueue ten decisions
# into production on 2026-08-12. ROOT and RECURSION_ROOT agree from here on.
RECURSION_ROOT="$ROOT"; export RECURSION_ROOT

FILE=""; DRY=0; PAUSED_SAFE=0; RECOVER_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --file) FILE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --paused-safe) PAUSED_SAFE=1; shift ;;
    --recover-only) RECOVER_ONLY=1; shift ;;
    *) shift ;;
  esac
done
DATE="$(date +%F)"
LOG="$ROOT/loop/logs/$DATE-conduct-hermes.log"; mkdir -p "$(dirname "$LOG")"
log(){ echo "[$(date -Is)] conduct-hermes: $*" | tee -a "$LOG" >&2; }
ev(){ bash scripts/taskctl.sh event "$1" "" "$2" >/dev/null 2>&1 || true; }

drain_queue(){
  local queue_file claim_rc child_rc action_state aggregate=0 project global first i
  local import_error import_rc
  local -a pids=() files=() projects=() claim_args=()
  [ "$DRY" = 0 ] || { log "--dry-run requires an explicit --file"; return 2; }
  [ -x "$ROOT/scripts/decision-queue.py" ] \
    || { log "durable decision queue helper is absent"; return 74; }
  mkdir -p "$ROOT/state/.locks" || return 70
  # WAIT, do not give up. hermes-decide.sh holds this same lock for its entire model call
  # (~40s observed). An actuator that returns 73 during that window still leaves a claimed
  # action behind, and its instruction coupling then fails before dispatch -- which is how a
  # decision wedged in production on 2026-08-12. Skipping a poll is free; failing an action
  # is not.
  CONTROL_LOCK_WAIT_S="${RECURSION_CONTROL_LOCK_WAIT_S:-120}"
  exec 8>>"$ROOT/state/.locks/hermes-control.lock"
  flock -w "$CONTROL_LOCK_WAIT_S" 8 \
    || { log "control lock still held after ${CONTROL_LOCK_WAIT_S}s; refusing overlapping actuation"; return 73; }
  import_error="$(python3 "$ROOT/scripts/decision-queue.py" import-journal 2>&1 >/dev/null)"
  import_rc=$?
  if [ "$import_rc" -ne 0 ]; then
    log "decision journal import failed rc=$import_rc; pending state was preserved: ${import_error:0:240}"
    return 74
  fi
  for quarantine_record in "$ROOT/state/decision-queue/quarantine"/*.json; do
    [ -f "$quarantine_record" ] || continue
    quarantine_sha="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("tail_sha256", ""))' \
      "$quarantine_record" 2>/dev/null || true)"
    [ -n "$quarantine_sha" ] || continue
    RECURSION_ROOT="$ROOT" bash "$ROOT/scripts/taskctl.sh" esc-record \
      "decision-journal-tail-$quarantine_sha" \
      "A torn decision-journal tail was quarantined; review crash evidence" \
      infra "${quarantine_record#$ROOT/}" >/dev/null 2>&1 || true
  done

  finalize_claim(){
    local claimed="$1" result_rc="$2" state reconcile_rc=0
    state="$(python3 "$ROOT/scripts/decision-queue.py" action-status "$claimed")" || return $?
    case "$state" in
      succeeded|failed|cancelled|pending)
        # The child can die after writing its terminal/deferred action but before projecting the
        # coupled instruction. Reconcile that handshake idempotently before moving the decision;
        # otherwise the parent would hide the only projection capable of recovery.
        RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$ROOT" \
          bash "$ROOT/scripts/conduct-hermes.sh" --recover-only --file "$claimed" 8>&- \
          >/dev/null 2>&1 || reconcile_rc=$?
        case "$state:$reconcile_rc" in
          succeeded:0|failed:1|cancelled:1|pending:75) : ;;
          *) log "instruction/action recovery failed state=$state rc=$reconcile_rc; preserving $claimed"; return 74 ;;
        esac
        state="$(python3 "$ROOT/scripts/decision-queue.py" action-status "$claimed")" || return $?
        case "$state" in
          succeeded) python3 "$ROOT/scripts/decision-queue.py" succeed "$claimed" "action succeeded" >/dev/null ;;
          failed|cancelled)
        python3 "$ROOT/scripts/decision-queue.py" fail "$claimed" "action $state rc=$result_rc" >/dev/null
            aggregate=1 ;;
          pending)
            python3 "$ROOT/scripts/decision-queue.py" defer "$claimed" "action deferred rc=$result_rc" >/dev/null
            return 75 ;;
          *) log "action changed unexpectedly during recovery: $state"; return 74 ;;
        esac
        ;;
      running) log "decision remains coupled to a running action"; return 75 ;;
      absent)
        if [ "$result_rc" -eq 75 ]; then
          python3 "$ROOT/scripts/decision-queue.py" defer "$claimed" "execution deferred" >/dev/null
          return 75
        fi
        if [ -f "$ROOT/state/PAUSE" ]; then
          # PAUSE preserves pending state, but it must not RELABEL a refusal as a deferral.
          # A genuine PAUSE decline returns 75 above; any other rc here means the child refused
          # (bad provenance, inconsistent digest, unsafe argument...). Masking those as
          # deferrals is how an undrainable record spins forever while the actuator reports
          # healthy -- observed 2026-08-12. Disposition is unchanged; visibility is not.
          log "REFUSED under PAUSE - child rc=$result_rc for ${claimed#$ROOT/}; pending preserved, NOT a deferral"
          python3 "$ROOT/scripts/decision-queue.py" defer "$claimed" "refused under pause rc=$result_rc" >/dev/null
          return 76
        fi
        python3 "$ROOT/scripts/decision-queue.py" fail "$claimed" "no action record rc=$result_rc" >/dev/null
        aggregate=1 ;;
      *) log "corrupt action state '$state'; preserving $claimed"; return 74 ;;
    esac
  }

  # Reconcile projections left running by a prior actuator process before claiming anything
  # new. A genuinely running action is never double-launched and blocks new admissions until
  # its own durable action reaches terminal state.
  for queue_file in "$ROOT/state/decision-queue/running"/*.json; do
    [ -f "$queue_file" ] || continue
    action_state="$(python3 "$ROOT/scripts/decision-queue.py" action-status "$queue_file")" || return $?
    case "$action_state" in
      absent) python3 "$ROOT/scripts/decision-queue.py" defer "$queue_file" "recovered claim had no action" >/dev/null || return $? ;;
      succeeded|failed|cancelled|running|pending)
        # Re-enter only the recovery path so the coupled instruction is acknowledged/released
        # before the decision projection becomes terminal. No verb is dispatched here.
        RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$ROOT" \
          bash "$ROOT/scripts/conduct-hermes.sh" --recover-only --file "$queue_file" 8>&-
        child_rc=$?
        finalize_claim "$queue_file" "$child_rc" || return $?
        ;;
      *) log "corrupt recovered action state '$action_state'"; return 74 ;;
    esac
  done

  # Deterministic state transitions run serially. They may enqueue more transitions, which this
  # same loop drains before any worker dispatch, preserving the goal/task CAS order.
  while :; do
    if [ "$PAUSED_SAFE" = 1 ]; then
      queue_file="$(python3 "$ROOT/scripts/decision-queue.py" claim-pending --kind non-work \
        --verb noop --verb pilot-plan-propose --verb pilot-plan-approve --verb pilot-window-open \
        --verb pilot-window-close --verb assist-answer --verb routing-refuse)"
    else
      queue_file="$(python3 "$ROOT/scripts/decision-queue.py" claim-pending --kind non-work)"
    fi
    claim_rc=$?
    [ "$claim_rc" -ne 4 ] || break
    [ "$claim_rc" -eq 0 ] || return "$claim_rc"
    RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$ROOT" \
      bash "$ROOT/scripts/conduct-hermes.sh" --file "$queue_file" 8>&-
    child_rc=$?
    finalize_claim "$queue_file" "$child_rc" || return $?
  done

  [ "$PAUSED_SAFE" = 0 ] || return "$aggregate"

  # Work decisions remain ordinary actions through this same actuator. The only difference is
  # that independent projects may occupy separate bounded slots. One slot per project plus the
  # global ceiling proves isolation; project/goal/window admission is rechecked in --file.
  global="${RECURSION_PILOT_GLOBAL_CONCURRENCY:-1}"
  case "$global" in ''|*[!0-9]*) log "invalid global pilot concurrency '$global'"; return 4 ;; esac
  [ "$global" -ge 1 ] && [ "$global" -le 16 ] || { log "global pilot concurrency must be 1..16"; return 4; }
  while :; do
    while [ "${#pids[@]}" -lt "$global" ]; do
      claim_args=(claim-pending --kind work)
      for project in "${projects[@]}"; do claim_args+=(--exclude-project "$project"); done
      queue_file="$(python3 "$ROOT/scripts/decision-queue.py" "${claim_args[@]}")"
      claim_rc=$?
      [ "$claim_rc" -ne 4 ] || break
      [ "$claim_rc" -eq 0 ] || return "$claim_rc"
      project="$(python3 - "$queue_file" "$ROOT" <<'PY'
import json,sys
from pathlib import Path
decision=Path(sys.argv[1]); root=Path(sys.argv[2])
row=json.loads(decision.read_text(encoding='utf-8'))
args=row.get('arguments') or row.get('args') or []
project=''
if args:
    task=root/'state/tasks'/f'{args[0]}.md'
    try:
        for line in task.read_text(encoding='utf-8').splitlines():
            key,sep,value=line.partition(':')
            if sep and key.strip() in {'project_id','project','workstream'} and value.strip():
                project=value.strip(); break
    except OSError:
        pass
print(project or row.get('project') or '')
PY
)"
      [ -n "$project" ] || project="unknown-$(basename "$queue_file")"
      RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$ROOT" \
        bash "$ROOT/scripts/conduct-hermes.sh" --file "$queue_file" 8>&- &
      pids+=("$!"); files+=("$queue_file"); projects+=("$project")
    done
    [ "${#pids[@]}" -gt 0 ] || break
    first="${pids[0]}"; queue_file="${files[0]}"
    wait "$first"; child_rc=$?
    finalize_claim "$queue_file" "$child_rc" || return $?
    pids=("${pids[@]:1}"); files=("${files[@]:1}"); projects=("${projects[@]:1}")
    if [ -f "$ROOT/state/PAUSE" ]; then
      for ((i=0; i<${#pids[@]}; i++)); do
        wait "${pids[$i]}"; child_rc=$?
        finalize_claim "${files[$i]}" "$child_rc" || true
      done
      return 75
    fi
  done
  return "$aggregate"
}

if [ -z "$FILE" ]; then
  drain_queue
  exit $?
fi

[ -f "$FILE" ] || { log "no decision file at $FILE"; exit 2; }

VERBS="noop plan work conduct publish escalate resolve-esc reap roadmap-add roadmap-new portfolio-add project-topic-bind register note assist-answer pilot-plan-propose pilot-plan-approve pilot-window-open pilot-window-close pilot-task-create pilot-worker-request pilot-verifier-request pilot-block pilot-escalate pilot-goal-verify reconcile-goal task-transition goal-transition verify-goal publish-task notification-reconcile notification-deliver notification-portfolio notification-audit notification-recover routing-refuse"
RAW_DECISION="$(cat "$FILE" 2>/dev/null || true)"
VALID="$(python3 "$ROOT/scripts/validate-decision.py" "$VERBS" "$RAW_DECISION" 2>&1)"
case "$VALID" in
  OK\ *) DECISION_JSON="${VALID#OK }" ;;
  *) log "REFUSED - ${VALID:-decision validation produced no output}"; exit 5 ;;
esac

read_field(){ python3 -c 'import json,sys;print(json.loads(sys.argv[1]).get(sys.argv[2],"") or "")' "$DECISION_JSON" "$1" 2>/dev/null; }
VERB="$(read_field verb)"; WHY="$(read_field why)"; GOAL="$(read_field goal)"
ACTOR="$(read_field actor)"
DECISION_PROJECT="$(read_field project)"
DECISION_SOURCE="$(read_field decision_source)"
ROUTED_DECIDER="$(read_field routed_decider)"
DECISION_ID="$(read_field id)"; IDEMPOTENCY_KEY="$(read_field idempotency_key)"
INSTRUCTION_ID="$(read_field instruction_id)"
ARGS_JSON="$(python3 -c 'import json,sys;print(json.dumps(json.loads(sys.argv[1]).get("args") or [],separators=(",",":")))' "$DECISION_JSON")" \
  || { log "REFUSED - could not freeze decision arguments"; exit 5; }
ACTION_PAYLOAD_SHA256="$(python3 - "$DECISION_JSON" <<'PY'
import hashlib,json,sys
row=json.loads(sys.argv[1])
payload={
    'actor':row.get('actor') or '', 'verb':row.get('verb') or '',
    'args':row.get('args',row.get('arguments',[])) or [], 'text':row.get('text') or '',
    'plan':row.get('plan') or None, 'instruction_id':row.get('instruction_id') or None,
    'project':row.get('project') or '', 'goal':row.get('goal',row.get('goal_id','')) or '',
    'decision_source':row.get('decision_source') or '',
    'routed_decider':row.get('routed_decider') or '',
}
raw=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
print(hashlib.sha256(raw).hexdigest())
PY
)" || { log "REFUSED - could not freeze complete action payload"; exit 5; }
DECISION_PAYLOAD_SHA256="$(read_field decision_payload_sha256)"
[ -n "$DECISION_PAYLOAD_SHA256" ] && [ "$DECISION_PAYLOAD_SHA256" = "$ACTION_PAYLOAD_SHA256" ] \
  || { log "REFUSED - decision authority/effect digest is absent or inconsistent"; exit 5; }
mapfile -t ARGS < <(python3 -c 'import json,sys
for a in json.loads(sys.argv[1]): sys.stdout.buffer.write(a.encode()+b"\n")' "$ARGS_JSON" 2>/dev/null)

[ -n "$VERB" ] || { log "decision has no verb"; exit 2; }

# --- re-validate args HERE. The decision file is on disk between decide and conduct, so
# validating only at decide time trusts a file anything could have rewritten. -------------
for a in ${ARGS+"${ARGS[@]}"}; do
  if ! printf '%s' "$a" | grep -qE '^[A-Za-z0-9][A-Za-z0-9._/-]{0,80}$'; then
    log "REFUSED — unsafe argument: $(printf '%s' "$a" | head -c 60)"
    ev decision-refused "unsafe arg for verb=$VERB"; exit 5
  fi
  case "$a" in
    *..*) log "REFUSED — path traversal in argument: $a"; ev decision-refused "traversal"; exit 5 ;;
  esac
done

case "$DECISION_SOURCE" in
  hermes-model)
    [ -n "$ROUTED_DECIDER" ] && [ "$ACTOR" = "$ROUTED_DECIDER" ] \
      || { log "REFUSED - model decision actor does not match its routed authority"; exit 5; }
    case "$ROUTED_DECIDER" in
      pilot-*)
        case "$VERB" in
          noop|pilot-plan-propose|pilot-task-create|pilot-worker-request|pilot-verifier-request|pilot-block|pilot-escalate|pilot-goal-verify) : ;;
          *) log "REFUSED - project-pilot model cannot emit Head-Hermes verb '$VERB'"; exit 5 ;;
        esac ;;
      head-hermes) : ;;
      *) log "REFUSED - unknown routed model authority '$ROUTED_DECIDER'"; exit 5 ;;
    esac ;;
  project-reconciler)
    [ -n "$ROUTED_DECIDER" ] && [ "$ACTOR" = "$ROUTED_DECIDER" ] \
      || { log "REFUSED - reconciler decision actor does not match routed authority"; exit 5; }
    case "$ACTOR:$VERB" in
      pilot-*:reconcile-goal|pilot-*:task-transition|pilot-*:goal-transition|pilot-*:verify-goal|pilot-*:publish-task|pilot-*:work) : ;;
      *) log "REFUSED - project reconciler cannot emit '$VERB' as '$ACTOR'"; exit 5 ;;
    esac ;;
  notification-reconciler)
    [ -n "$ROUTED_DECIDER" ] && [ "$ACTOR" = "$ROUTED_DECIDER" ] \
      || { log "REFUSED - notification reconciler actor does not match routed authority"; exit 5; }
    case "$ACTOR:$VERB" in
      pilot-*:notification-reconcile|pilot-*:notification-deliver|pilot-*:notification-audit|pilot-*:notification-recover|head-hermes:notification-portfolio) : ;;
      *) log "REFUSED - notification reconciler cannot emit '$VERB' as '$ACTOR'"; exit 5 ;;
    esac ;;
  routing-reconciler)
    [ -n "$ROUTED_DECIDER" ] && [ "$ACTOR" = "$ROUTED_DECIDER" ] \
      || { log "REFUSED - routing reconciler actor does not match routed authority"; exit 5; }
    case "$ACTOR:$VERB" in
      head-hermes:routing-refuse|pilot-*:routing-refuse) : ;;
      *) log "REFUSED - routing reconciler cannot emit '$VERB' as '$ACTOR'"; exit 5 ;;
    esac ;;
  instruction-reconciler)
    [ "$ACTOR" = head-hermes ] && [ "$ROUTED_DECIDER" = head-hermes ] \
      || { log "REFUSED - instruction reconciler lacks exact Head-Hermes authority"; exit 5; }
    [ "$VERB" = pilot-window-open ] \
      || { log "REFUSED - instruction reconciler cannot emit '$VERB'"; exit 5; } ;;
  *) log "REFUSED - missing or unknown decision provenance '$DECISION_SOURCE'"; exit 5 ;;
esac

# Capacity and authority derive from the canonical task, never a model-authored project label.
if [ "$VERB" = work ] && [ -n "${ARGS[0]:-}" ] && [ -f "state/tasks/${ARGS[0]}.md" ]; then
  TASK_PROJECT="$(sed -n -E 's/^(project_id|project|workstream):[[:space:]]*//p' \
    "state/tasks/${ARGS[0]}.md" | head -1 | tr -d '\r')"
  if [ -n "$DECISION_PROJECT" ] && [ -n "$TASK_PROJECT" ] \
     && [ "$DECISION_PROJECT" != "$TASK_PROJECT" ]; then
    log "REFUSED - decision project '$DECISION_PROJECT' does not match canonical task project '$TASK_PROJECT'"
    ev decision-refused "project mismatch for task ${ARGS[0]}"
    exit 5
  fi
fi

# --- PAUSE: deciding is awareness, acting is not (D-012). --------------------------------
if [ "$RECOVER_ONLY" = 0 ] && [ -f "$ROOT/state/PAUSE" ]; then
  case "$VERB" in
    noop|pilot-plan-propose|pilot-plan-approve|pilot-window-open|pilot-window-close|assist-answer|routing-refuse) : ;;
    *)
  log "PAUSED — refusing to execute '$VERB'. The decision is recorded; it will not run until resume."
  ev decision-deferred "paused: $VERB"
      exit 75 ;;
  esac
fi

# --- durable action claim. The decision file may be replayed after a crash or scheduler retry.
# A deterministic action id plus an append-only lifecycle journal makes that replay observe the
# prior claim instead of dispatching again. This strengthens the existing actuator; it does not
# introduce a second execution path.
ACTION_LOCK=""; ACTION_LOCK_HELD=0; ACTION_FILE=""; ACTION_ID=""
ACTION_CLAIMED=0; ACTION_TERMINAL=0; INSTRUCTION_CONSUMED=0
action_unlock(){
  [ "$ACTION_LOCK_HELD" = 1 ] || return 0
  python3 "$ROOT/scripts/runtime-state.py" lock-release "$ACTION_LOCK" "$$" \
    >/dev/null 2>&1 || return 74
  ACTION_LOCK_HELD=0
}
action_lock(){
  mkdir -p "$ROOT/state/actions" "$ROOT/state/.locks" || return 70
  ACTION_LOCK="$ROOT/state/.locks/action-$ACTION_ID.lock"
  [ -x "$ROOT/scripts/runtime-state.py" ] \
    || { log "witnessed action lock helper is absent"; return 73; }
  python3 "$ROOT/scripts/runtime-state.py" lock-acquire "$ACTION_LOCK" "$$" \
    >/dev/null 2>&1 \
    || { log "action lock contended; refusing duplicate/unlocked dispatch"; return 73; }
  ACTION_LOCK_HELD=1
  if ! RECURSION_ROOT="$ROOT" python3 "$ROOT/scripts/transition_receipt.py" \
       --root "$ROOT" recover >/dev/null; then
    action_unlock || true
    log "transition receipt recovery failed closed before action claim"
    return 74
  fi
  return 0
}
action_field(){
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get(sys.argv[2],"") or "")' \
    "$ACTION_FILE" "$1" 2>/dev/null
}
action_owned_running(){
  ACTION_EXPECTED_OWNER="$$@$(hostname)" python3 - "$ACTION_FILE" <<'PY' 2>/dev/null
import json,os,sys
try:
    row=json.load(open(sys.argv[1],encoding='utf-8'))
except (OSError,json.JSONDecodeError):
    raise SystemExit(1)
raise SystemExit(0 if row.get('status') == 'running' and
                 row.get('lease_owner') == os.environ['ACTION_EXPECTED_OWNER'] else 1)
PY
}
action_identity_matches(){
  ACTION_EXPECTED_ID="$ACTION_ID" ACTION_EXPECTED_KEY="$IDEMPOTENCY_KEY" \
  ACTION_EXPECTED_DECISION="$DECISION_ID" ACTION_EXPECTED_INSTRUCTION="$INSTRUCTION_ID" \
  ACTION_EXPECTED_VERB="$VERB" ACTION_EXPECTED_GOAL="$GOAL" ACTION_EXPECTED_ARGS="$ARGS_JSON" \
  ACTION_EXPECTED_PAYLOAD="$ACTION_PAYLOAD_SHA256" \
    python3 - "$ACTION_FILE" <<'PY' 2>/dev/null
import json,os,sys
try:
    row=json.load(open(sys.argv[1],encoding='utf-8'))
except (OSError,json.JSONDecodeError):
    raise SystemExit(1)
expected={
    'id':os.environ['ACTION_EXPECTED_ID'],
    'idempotency_key':os.environ['ACTION_EXPECTED_KEY'],
    'decision_id':os.environ.get('ACTION_EXPECTED_DECISION') or None,
    'instruction_id':os.environ.get('ACTION_EXPECTED_INSTRUCTION') or None,
    'verb':os.environ['ACTION_EXPECTED_VERB'],
    'arguments':json.loads(os.environ['ACTION_EXPECTED_ARGS']),
    'goal_id':os.environ.get('ACTION_EXPECTED_GOAL') or None,
    'action_payload_sha256':os.environ['ACTION_EXPECTED_PAYLOAD'],
}
raise SystemExit(0 if all(row.get(key)==value for key,value in expected.items()) else 1)
PY
}
action_transition(){ # status evidence
  local status="$1" evidence="${2:-}" rc
  ACTION_STATUS="$status" ACTION_EVIDENCE="$evidence" ACTION_ID="$ACTION_ID" \
  ACTION_KEY="$IDEMPOTENCY_KEY" ACTION_DECISION="$DECISION_ID" \
  ACTION_INSTRUCTION="$INSTRUCTION_ID" ACTION_VERB="$VERB" ACTION_GOAL="$GOAL" \
  ACTION_SOURCE="$FILE" ACTION_ARGS="$ARGS_JSON" ACTION_OWNER="$$@$(hostname)" \
  ACTION_PAYLOAD_SHA256="$ACTION_PAYLOAD_SHA256" ACTION_ACTOR="$ACTOR" \
  ACTION_PROJECT="$DECISION_PROJECT" ACTION_DECISION_SOURCE="$DECISION_SOURCE" \
  ACTION_ROUTED_DECIDER="$ROUTED_DECIDER" \
  python3 - "$ACTION_FILE" "$ROOT/state/action-events.jsonl" "$ROOT/scripts" <<'PY'
import json,os,sys,time
sys.path.insert(0,sys.argv[3])
from transition_receipt import commit_transition,json_mutation
path,journal=sys.argv[1:3]
now=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
status=os.environ['ACTION_STATUS']
try:
    with open(path,encoding='utf-8') as src: record=json.load(src)
except FileNotFoundError:
    record={
      'schema_version':1,'id':os.environ['ACTION_ID'],
      'decision_id':os.environ.get('ACTION_DECISION') or None,
      'instruction_id':os.environ.get('ACTION_INSTRUCTION') or None,
      'idempotency_key':os.environ['ACTION_KEY'],'verb':os.environ['ACTION_VERB'],
      'arguments':json.loads(os.environ['ACTION_ARGS']),
      'goal_id':os.environ.get('ACTION_GOAL') or None,'status':'pending',
      'actor':os.environ.get('ACTION_ACTOR') or None,
      'project':os.environ.get('ACTION_PROJECT') or None,
      'decision_source':os.environ.get('ACTION_DECISION_SOURCE') or None,
      'routed_decider':os.environ.get('ACTION_ROUTED_DECIDER') or None,
      'action_payload_sha256':os.environ['ACTION_PAYLOAD_SHA256'],
      'lease_owner':None,'lease_expires':None,'attempts':0,'result_evidence':None,
      'created_at':now,'updated_at':now,
    }
if status=='running':
    record['attempts']=int(record.get('attempts') or 0)+1
    record['lease_owner']=os.environ['ACTION_OWNER']
    record['lease_expires']=int(time.time())+int(os.environ.get('RECURSION_ACTION_LEASE_S','3600'))
elif status in ('pending','succeeded','failed','cancelled'):
    record['lease_owner']=None; record['lease_expires']=None
record['status']=status
record['result_evidence']=os.environ.get('ACTION_EVIDENCE') or None
record['updated_at']=now
event={'schema_version':1,'ts':now,'action_id':record['id'],'status':status,
       'attempt':record['attempts'],'idempotency_key':record['idempotency_key'],
       'evidence':record['result_evidence']}
commit_transition(__import__('pathlib').Path(sys.argv[3]).parent,
                  [json_mutation(__import__('pathlib').Path(path),record)],event,
                  journal='state/action-events.jsonl')
PY
  rc=$?
  [ "$rc" -eq 0 ] || log "failed durable action transition status=$status rc=$rc"
  return "$rc"
}
release_consumed_instruction(){
  [ "${RECURSION_QUEUE_ACTUATION:-0}" = 1 ] && [ -n "$INSTRUCTION_ID" ] || return 0
  if ! RECURSION_ROOT="$ROOT" bash scripts/intake.sh release "$INSTRUCTION_ID" "$ACTION_ID"; then
    log "action $ACTION_ID could not reopen instruction $INSTRUCTION_ID"
    return 74
  fi
}
reconcile_terminal_instruction(){ # succeeded|failed
  local disposition="$1"
  [ "${RECURSION_QUEUE_ACTUATION:-0}" = 1 ] && [ -n "$INSTRUCTION_ID" ] || return 0
  case "$disposition" in
    succeeded)
      if [ "$VERB" = routing-refuse ]; then
        RECURSION_ROOT="$ROOT" python3 scripts/instruction_routing.py --root "$ROOT" \
          record "$DECISION_JSON" || return $?
      fi
      # Receipt first, acknowledgement second: a failed refusal-event commit must leave the
      # instruction recoverably consumed, never silently terminal with zero attention evidence.
      RECURSION_ROOT="$ROOT" bash scripts/intake.sh acknowledge "$INSTRUCTION_ID" "$ACTION_ID" ;;
    failed)
      RECURSION_ROOT="$ROOT" bash scripts/intake.sh release "$INSTRUCTION_ID" "$ACTION_ID" ;;
    *) return 2 ;;
  esac
}
action_cleanup(){
  local exit_rc=$?
  trap - EXIT INT TERM HUP
  if [ "$ACTION_CLAIMED" = 1 ] && [ "$ACTION_TERMINAL" = 0 ] && action_owned_running; then
    if [ "$exit_rc" -eq 75 ]; then
      action_transition pending "actuator deferred before terminal transition rc=$exit_rc" || true
    else
      action_transition failed "actuator exited before terminal transition rc=$exit_rc" || true
    fi
    if [ "$INSTRUCTION_CONSUMED" != 0 ] && ! release_consumed_instruction; then
      exit_rc=74
    fi
  fi
  action_unlock
  exit "$exit_rc"
}

if [ "$DRY" = 0 ]; then
  if [ -z "$IDEMPOTENCY_KEY" ]; then
    IDEMPOTENCY_KEY="decision:${DECISION_ID:-$(printf '%s' "$DECISION_JSON" | sha256sum | awk '{print $1}')}"
  fi
  [ "${#IDEMPOTENCY_KEY}" -le 256 ] \
    || { log "REFUSED — idempotency key exceeds 256 characters"; exit 5; }
  ACTION_ID="action-$(printf '%s' "$IDEMPOTENCY_KEY" | sha256sum | cut -c1-24)"
  ACTION_FILE="$ROOT/state/actions/$ACTION_ID.json"
  action_lock || exit $?
  trap 'action_unlock' EXIT
  if [ -f "$ACTION_FILE" ] && ! action_identity_matches; then
    log "REFUSED - action identity collision for $ACTION_ID; immutable decision fields disagree"
    action_unlock; trap - EXIT; exit 74
  fi
  if [ "$RECOVER_ONLY" = 1 ]; then
    if [ ! -f "$ACTION_FILE" ]; then
      log "recovery: $ACTION_ID disappeared before inspection; refusing dispatch"
      action_unlock; trap - EXIT; exit 4
    fi
    prior="$(action_field status)"
    case "$prior" in
      succeeded)
        reconcile_terminal_instruction succeeded || { action_unlock; trap - EXIT; exit 74; }
        action_unlock; trap - EXIT; exit 0 ;;
      failed|cancelled)
        reconcile_terminal_instruction failed || { action_unlock; trap - EXIT; exit 74; }
        action_unlock; trap - EXIT; exit 1 ;;
      running)
        if [ "$VERB" = routing-refuse ]; then
          # routing-refuse validates only immutable evidence before terminal action state. It is
          # therefore the one verb a fresh actuator may finish after a crash without relaunching
          # an external effect or creating a second action.
          RECURSION_ROOT="$ROOT" python3 scripts/instruction_routing.py --root "$ROOT" \
            perform "$DECISION_JSON" >/dev/null || {
              action_unlock; trap - EXIT; exit 4;
            }
          action_transition succeeded "routing refusal recovered after interrupted dispatch" || {
            action_unlock; trap - EXIT; exit 74;
          }
          reconcile_terminal_instruction succeeded || { action_unlock; trap - EXIT; exit 75; }
          action_unlock; trap - EXIT; exit 0
        fi
        lease="$(action_field lease_expires)"
        if printf '%s' "$lease" | grep -qE '^[0-9]+$' && [ "$lease" -le "$(date +%s)" ]; then
          action_transition failed "stale dispatch lease expired; recovery refused relaunch" || {
            action_unlock; trap - EXIT; exit 74;
          }
          reconcile_terminal_instruction failed || { action_unlock; trap - EXIT; exit 74; }
          log "recovery: $ACTION_ID lease expired; marked failed without dispatch"
          action_unlock; trap - EXIT; exit 1
        fi
        log "recovery: $ACTION_ID still owns a live lease; refusing duplicate dispatch"
        action_unlock; trap - EXIT; exit 75
        ;;
      pending)
        if [ "$VERB" = routing-refuse ]; then
          action_transition running "routing refusal recovery claimed" || {
            action_unlock; trap - EXIT; exit 74;
          }
          RECURSION_ROOT="$ROOT" python3 scripts/instruction_routing.py --root "$ROOT" \
            perform "$DECISION_JSON" >/dev/null || {
              action_transition failed "routing refusal recovery validation failed" || true
              action_unlock; trap - EXIT; exit 1;
            }
          action_transition succeeded "routing refusal recovered from pending state" || {
            action_unlock; trap - EXIT; exit 74;
          }
          reconcile_terminal_instruction succeeded || { action_unlock; trap - EXIT; exit 75; }
          action_unlock; trap - EXIT; exit 0
        fi
        # rc=75 intentionally restores pending before the decision claim is deferred. A crash in
        # that narrow interval must finish the defer/reopen handshake, not terminalize the action.
        reconcile_terminal_instruction failed || { action_unlock; trap - EXIT; exit 74; }
        action_unlock; trap - EXIT; exit 75
        ;;
      *) log "REFUSED - corrupt/unknown recovery action status '$prior'"; action_unlock; trap - EXIT; exit 74 ;;
    esac
  fi
  if [ -f "$ACTION_FILE" ]; then
    prior="$(action_field status)"
    case "$prior" in
      succeeded)
        reconcile_terminal_instruction succeeded || { action_unlock; trap - EXIT; exit 74; }
        log "idempotent replay: $ACTION_ID already succeeded; no dispatch"
        action_unlock; trap - EXIT; exit 0 ;;
      failed|cancelled)
        reconcile_terminal_instruction failed || { action_unlock; trap - EXIT; exit 74; }
        log "idempotent replay: $ACTION_ID is terminal ($prior); explicit retry required"
        action_unlock; trap - EXIT; exit 1 ;;
      running)
        lease="$(action_field lease_expires)"
        if printf '%s' "$lease" | grep -qE '^[0-9]+$' && [ "$lease" -le "$(date +%s)" ]; then
          action_transition failed "stale dispatch lease expired; reconciliation refused relaunch" || true
          log "recovery: $ACTION_ID lease expired; marked failed for explicit reconciliation, not relaunched"
          action_unlock; trap - EXIT; exit 1
        fi
        log "recovery: $ACTION_ID was already dispatched; refusing a double launch"
        action_unlock; trap - EXIT; exit 75 ;;
      pending)
        reconcile_terminal_instruction failed || { action_unlock; trap - EXIT; exit 74; }
        : ;;
      *) log "REFUSED — corrupt/unknown action status '$prior'"; action_unlock; trap - EXIT; exit 74 ;;
    esac
  else
    action_transition pending "decision accepted" || { action_unlock; trap - EXIT; exit 74; }
  fi
  action_transition running "dispatch claimed" || { action_unlock; trap - EXIT; exit 74; }
  ACTION_CLAIMED=1
  trap 'action_cleanup' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  trap 'exit 129' HUP
  if [ "${RECURSION_QUEUE_ACTUATION:-0}" = 1 ] && [ -n "$INSTRUCTION_ID" ]; then
    if ! RECURSION_ROOT="$ROOT" bash scripts/intake.sh consume "$INSTRUCTION_ID" "$ACTION_ID"; then
      action_transition failed "instruction coupling failed before dispatch" || true
      action_unlock; trap - EXIT
      exit 74
    fi
    INSTRUCTION_CONSUMED=1
  fi
fi

log "verb=$VERB args=[${ARGS[*]-}] goal=${GOAL:0:60}"
[ -n "$WHY" ] && log "why: ${WHY:0:160}"

run(){ # execute an argv array, or print it under --dry-run
  if [ "$DRY" = "1" ]; then printf '  WOULD RUN:'; printf ' %q' "$@"; printf '\n'; return 0; fi
  "$@"
}

instruction_noop_bind_evidence(){
  python3 - "$ROOT" "$INSTRUCTION_ID" <<'PY'
import json,re,sys
from pathlib import Path

root,iid=Path(sys.argv[1]),sys.argv[2]
name=f"{int(iid):08d}.md" if iid.isdigit() else f"{iid}.md"
path=root/'state/instructions'/name
try:
    lines=path.read_text(encoding='utf-8',errors='surrogateescape').splitlines()
except OSError:
    raise SystemExit(1)
refusal='project-pilot: instruction is not owned by this project pilot'
annotated=set()
for i,line in enumerate(lines[:-1]):
    if not re.fullmatch(r'## OPEN \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',line.strip()):
        continue
    note=lines[i+1].strip()
    if note.startswith('deferred/failed actions reopened instruction:') and refusal in note:
        annotated.update(re.findall(r'action-[0-9a-f]{24}',note))
proven=[]
for aid in sorted(annotated):
    action_path=root/'state/actions'/f'{aid}.json'
    try:
        action=json.loads(action_path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError):
        continue
    if (action.get('id') == aid and str(action.get('instruction_id') or '') == iid
            and action.get('status') == 'failed'
            and str(action.get('verb') or '').startswith('pilot-')
            and refusal in str(action.get('result_evidence') or '')):
        proven.append(aid)
if len(proven) < 2:
    raise SystemExit(1)
print(','.join(proven))
PY
}

# --- the whitelist. A fixed case list: there is no path from an unrecognised verb to
# execution, and nothing here reaches auth, cron, .env, flags, merges, or deploys. --------
rc=0
VERB_STDERR_TAIL=""
# Prose for the authoring verbs. Held to the same rules validate-decision.py applied, because
# this file is a separate boundary and the decision sat on disk in between.
TEXT="$(read_field text)"
if [ -n "$TEXT" ] && { [ "${#TEXT}" -gt 500 ] || printf '%s' "$TEXT" | grep -q '[[:cntrl:]]' \
  || printf '%s' "$TEXT" | grep -qE '^[[:space:]]*-'; }; then
  log "REFUSED - invalid authoring text at actuator boundary"
  exit 5
fi

case "$VERB" in
  # AUTHORING. These WRITE, so they go through scripts/author.sh — one writer, append-only,
  # state/ only — for the same reason execution goes through the proven scripts rather than
  # through whatever the model felt like running. author.sh validates its own arguments again:
  # the decision file sits on disk between deciding and acting, so this is a separate boundary.
  roadmap-add|note)
    A0="${ARGS[0]:-}"; [ -n "$A0" ] || { log "$VERB needs a target"; exit 2; }
    [ -n "$TEXT" ] || { log "REFUSED — $VERB needs prose in the \"text\" field"; exit 2; }
    run bash scripts/author.sh "$VERB" "$A0" "$TEXT"; rc=$? ;;

  roadmap-new|register|project-topic-bind)
    A0="${ARGS[0]:-}"; [ -n "$A0" ] || { log "$VERB needs an argument"; exit 2; }
    run bash scripts/author.sh "$VERB" "$A0" "${ARGS[1]:-}"; rc=$? ;;

  portfolio-add)
    A0="${ARGS[0]:-}"; A1="${ARGS[1]:-}"
    [ -n "$A0" ] && [ -n "$A1" ] && [ -n "$TEXT" ] \
      || { log "portfolio-add needs project, remote, and charter text"; exit 2; }
    run bash scripts/author.sh portfolio-add "$A0" "$A1" "$TEXT"; rc=$? ;;

  pilot-plan-propose|pilot-plan-approve|pilot-window-open|pilot-window-close|pilot-task-create|pilot-worker-request|pilot-verifier-request|pilot-block|pilot-escalate|pilot-goal-verify)
    # Project-pilot authority is rechecked against the durable topic/pilot/charter records here.
    # The helper may create scoped proposal/task state; it never launches a worker or publishes.
    # Keep the stderr tail: the refusal reason must reach the action record and the instruction
    # annotation, or a refused verb presents as a bare rc and gets re-decided identically
    # forever. Three rc=4 refusals were debugged blind this way on 2026-08-12 because the
    # actuator discards child streams.
    _pilot_err="$(mktemp "${TMPDIR:-/tmp}/pilot-stderr.XXXXXX")"
    run python3 scripts/project-pilot.py execute-json "$DECISION_JSON" 2>"$_pilot_err"; rc=$?
    VERB_STDERR_TAIL="$(tail -c 240 "$_pilot_err" | tr '
' ' ' | sed 's/  */ /g')"
    cat "$_pilot_err" >&2; rm -f "$_pilot_err"
    [ "$rc" -eq 0 ] || log "pilot verb refused: ${VERB_STDERR_TAIL:-<no stderr>}" ;;

  routing-refuse)
    # This verb is never model-callable. The deterministic helper re-authenticates the current
    # instruction, exact historical recovery witnesses (707/732), and the actor/verb mismatch,
    # then emits one receipt-backed refusal event. Generic action coupling performs the only
    # instruction state transition.
    _routing_err="$(mktemp "${TMPDIR:-/tmp}/routing-stderr.XXXXXX")"
    run python3 scripts/instruction_routing.py --root "$ROOT" perform "$DECISION_JSON" \
      2>"$_routing_err"; rc=$?
    VERB_STDERR_TAIL="$(tail -c 240 "$_routing_err" | tr '\n' ' ' | sed 's/  */ /g')"
    cat "$_routing_err" >&2; rm -f "$_routing_err"
    [ "$rc" -eq 0 ] || log "routing refusal deferred/refused: ${VERB_STDERR_TAIL:-<no stderr>}" ;;

  reconcile-goal|task-transition|goal-transition|verify-goal|publish-task)
    # These are not model-callable verbs: project-reconcile.py emits them from canonical
    # truth, and the pilot identity is rechecked at this final actuator boundary.
    P0="${ARGS[0]:-}"; [ -n "$P0" ] || { log "$VERB needs a project"; exit 2; }
    EXPECTED_ACTOR="$(python3 - "$ROOT/state/project-config/$P0.json" <<'PY' 2>/dev/null
import json,sys
print(json.load(open(sys.argv[1],encoding='utf-8')).get('pilot_id',''))
PY
)"
    [ -n "$EXPECTED_ACTOR" ] && [ "$ACTOR" = "$EXPECTED_ACTOR" ] \
      || { log "REFUSED - Phase 6 decision actor is not the bound project pilot"; exit 5; }
    case "$VERB" in
      reconcile-goal) run python3 scripts/project-reconcile.py reconcile "${ARGS[0]}" "${ARGS[1]}" ;;
      task-transition) run python3 scripts/project-reconcile.py transition-task \
        "${ARGS[0]}" "${ARGS[1]}" "${ARGS[2]}" "${ARGS[3]}" "${ARGS[4]}" "${ARGS[5]}" ;;
      goal-transition) run python3 scripts/project-reconcile.py transition-goal \
        "${ARGS[0]}" "${ARGS[1]}" "${ARGS[2]}" "${ARGS[3]}" "${ARGS[4]}" ;;
      verify-goal) run python3 scripts/project-reconcile.py verify-goal "${ARGS[0]}" "${ARGS[1]}" ;;
      publish-task) run python3 scripts/project-reconcile.py publish-task "${ARGS[0]}" "${ARGS[1]}" "${ARGS[2]}" ;;
    esac
    rc=$? ;;

  notification-reconcile|notification-deliver|notification-portfolio|notification-audit|notification-recover)
    # Phase 7 is another deterministic consumer of canonical truth, not another sender or
    # actuator. Project actions are bound to their pilot; only the portfolio-result action is
    # attributed to Head Hermes. notification-outbox.py independently rechecks destination policy.
    P0="${ARGS[0]:-}"; A1="${ARGS[1]:-}"
    [ -n "$P0" ] && [ -n "$A1" ] || { log "$VERB needs project and object identity"; exit 2; }
    EXPECTED_ACTOR="$(python3 - "$ROOT/state/project-config/$P0.json" <<'PY' 2>/dev/null
import json,sys
print(json.load(open(sys.argv[1],encoding='utf-8')).get('pilot_id',''))
PY
)"
    if [ "$VERB" = notification-portfolio ]; then
      [ "$ACTOR" = head-hermes ] || { log "REFUSED - portfolio result actor is not Head Hermes"; exit 5; }
    else
      [ -n "$EXPECTED_ACTOR" ] && [ "$ACTOR" = "$EXPECTED_ACTOR" ] \
        || { log "REFUSED - Phase 7 action actor is not the bound project pilot"; exit 5; }
    fi
    case "$VERB" in
      notification-reconcile) run python3 scripts/notification-outbox.py reconcile-event "$P0" "$A1" ;;
      notification-deliver) run python3 scripts/notification-outbox.py deliver "$P0" "$A1" ;;
      notification-portfolio) run python3 scripts/notification-outbox.py portfolio-report "$P0" "$A1" ;;
      notification-audit) run python3 scripts/notification-outbox.py audit "$P0" "$A1" ;;
      notification-recover) run python3 scripts/notification-outbox.py recover "$P0" "$A1" ;;
    esac
    rc=$? ;;

  assist-answer)
    A0="${ARGS[0]:-}"; [ -n "$A0" ] || { log "assist-answer needs a task id"; exit 2; }
    [ -n "$TEXT" ] || { log "REFUSED - assist-answer needs prose in the text field"; exit 2; }
    RECURSION_INSTRUCTION_ID="$INSTRUCTION_ID" run bash scripts/assist.sh answer "$A0" "$TEXT"; rc=$? ;;

  noop)
    if [ "$DRY" = 0 ] && [ "${RECURSION_QUEUE_ACTUATION:-0}" = 1 ] && [ -n "$INSTRUCTION_ID" ]; then
      NOOP_BIND_EVIDENCE="$(instruction_noop_bind_evidence)"
      if [ "$?" -ne 0 ]; then
        VERB_STDERR_TAIL="cannot-bind noop evidence is absent"
        log "REFUSED - instruction-coupled noop lacks two corroborated prior ownership refusals"
        rc=4
      else
        log "noop — cannot-bind evidence=$NOOP_BIND_EVIDENCE${WHY:+ ($WHY)}"
      fi
    else
      log "noop — nothing to run${WHY:+ ($WHY)}"
    fi ;;

  reap)
    run bash scripts/taskctl.sh reap; rc=$? ;;

  plan)
    WS="${ARGS[0]:-}"; [ -n "$WS" ] || { log "plan needs a workstream"; exit 2; }
    [ -f "state/roadmaps/$WS.md" ] || { log "REFUSED — no roadmap for workstream '$WS'"; exit 5; }
    run bash scripts/plan.sh "$WS"; rc=$? ;;

  work)
    ID="${ARGS[0]:-}"; [ -n "$ID" ] || { log "work needs a task id"; exit 2; }
    [ -f "state/tasks/$ID.md" ] || { log "REFUSED — no such task: $ID"; exit 5; }
    # The gate is the contract (delegation-design.md): no acceptance command, no autonomy.
    if [ -z "$(sed -n 's/^acceptance: *//p' "state/tasks/$ID.md" | head -1)" ] \
       && ! grep -q '^pilot_id: ' "state/tasks/$ID.md"; then
      log "REFUSED — task $ID has no acceptance gate; it must escalate, not run"; exit 5
    fi
    if grep -q '^pilot_id: ' "state/tasks/$ID.md" && [ -x scripts/project-reconcile.py ]; then
      authority_rc=0
      RECURSION_ROOT="$ROOT" python3 scripts/project-reconcile.py \
        check-work-authority "$ID" >/dev/null || authority_rc=$?
      if [ "$authority_rc" -ne 0 ]; then
        log "REFUSED - task $ID lacks exact open pilot-window authority rc=$authority_rc"
        case "$authority_rc" in 74|75) exit 75 ;; *) exit 5 ;; esac
      fi
    fi
    run bash scripts/work.sh "$ID"; rc=$? ;;

  conduct)
    run bash scripts/conduct.sh; rc=$? ;;

  publish)
    BR="${ARGS[0]:-}"; [ -n "$BR" ] || { log "publish needs a branch"; exit 2; }
    # publish.sh --branch never pushes to a default branch, but refuse obvious defaults here
    # too: two independent checks, because this one is driven by model output.
    case "$BR" in
      main|master|HEAD) log "REFUSED — '$BR' is a default branch; the loop never pushes to it"; exit 5 ;;
    esac
    run bash scripts/publish.sh --branch "$BR"; rc=$? ;;

  escalate)
    KEY="${ARGS[0]:-}"; TITLE="${TEXT:-${ARGS[1]:-$KEY}}"
    [ -n "$KEY" ] || { log "escalate needs a key"; exit 2; }
    run bash scripts/taskctl.sh esc-record "$KEY" "$TITLE" "${ARGS[2]:-}" "hermes-decision"; rc=$? ;;

  resolve-esc)
    EID="${ARGS[0]:-}"; [ -n "$EID" ] || { log "resolve-esc needs an escalation id"; exit 2; }
    case "$EID" in esc-*) ;; *) log "REFUSED — '$EID' is not an escalation id"; exit 5 ;; esac
    run bash scripts/taskctl.sh esc-resolve "$EID" "closed by Hermes decision: ${WHY:0:120}"; rc=$? ;;

  *)
    log "REFUSED — '$VERB' is not a whitelisted verb. Nothing was executed."
    ev decision-refused "unknown verb: $VERB"
    exit 5 ;;
esac

[ "$DRY" = "1" ] || {
  if [ "$rc" -eq 0 ]; then
    action_transition succeeded "log=$LOG rc=0"
    if [ "$?" -eq 0 ] && [ "${RECURSION_QUEUE_ACTUATION:-0}" = 1 ] && [ -n "$INSTRUCTION_ID" ]; then
      reconcile_terminal_instruction succeeded \
        || { rc=74; INSTRUCTION_CONSUMED=0; log "instruction acknowledgement failed after durable success"; }
    fi
  elif [ "$rc" -eq 75 ]; then
    action_transition pending "log=$LOG deferred rc=75"
  else action_transition failed "log=$LOG rc=$rc${VERB_STDERR_TAIL:+ | $VERB_STDERR_TAIL}"
  fi || rc=74
  if [ "$rc" -ne 0 ] && [ "$INSTRUCTION_CONSUMED" = 1 ]; then
    if release_consumed_instruction; then
      INSTRUCTION_CONSUMED=0
    else
      rc=74
    fi
  fi
  ev decision-executed "$VERB rc=$rc"
  if action_owned_running; then
    rc=74
  else
    ACTION_TERMINAL=1
    action_unlock; trap - EXIT INT TERM HUP
  fi
}
log "done (verb=$VERB rc=$rc)"
exit "$rc"

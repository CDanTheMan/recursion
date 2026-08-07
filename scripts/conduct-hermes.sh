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

FILE=""; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --file) FILE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    *) shift ;;
  esac
done
DATE="$(date +%F)"
LOG="$ROOT/loop/logs/$DATE-conduct-hermes.log"; mkdir -p "$(dirname "$LOG")"
log(){ echo "[$(date -Is)] conduct-hermes: $*" | tee -a "$LOG" >&2; }
ev(){ bash scripts/taskctl.sh event "$1" "" "$2" >/dev/null 2>&1 || true; }

drain_queue(){
  local queue_file claim_rc child_rc action_state aggregate=0
  [ "$DRY" = 0 ] || { log "--dry-run requires an explicit --file"; return 2; }
  [ -x "$ROOT/scripts/decision-queue.py" ] \
    || { log "durable decision queue helper is absent"; return 74; }
  mkdir -p "$ROOT/state/.locks" || return 70
  exec 8>>"$ROOT/state/.locks/hermes-control.lock"
  flock -n 8 || { log "control lock contended; refusing overlapping actuation"; return 73; }
  python3 "$ROOT/scripts/decision-queue.py" import-journal >/dev/null || return $?
  while :; do
    queue_file="$(python3 "$ROOT/scripts/decision-queue.py" claim)"
    claim_rc=$?
    [ "$claim_rc" -ne 4 ] || break
    [ "$claim_rc" -eq 0 ] || return "$claim_rc"
    RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$ROOT" \
      bash "$ROOT/scripts/conduct-hermes.sh" --file "$queue_file"
    child_rc=$?
    action_state="$(python3 "$ROOT/scripts/decision-queue.py" action-status "$queue_file")" \
      || return $?
    case "$action_state" in
      succeeded)
        python3 "$ROOT/scripts/decision-queue.py" succeed "$queue_file" "action succeeded" >/dev/null \
          || return $? ;;
      failed|cancelled)
        python3 "$ROOT/scripts/decision-queue.py" fail "$queue_file" "action $action_state rc=$child_rc" >/dev/null \
          || return $?
        aggregate=1 ;;
      running)
        # A live or unreconciled Phase 2 action claim must never be launched again. Leave its
        # decision in running so a later lease reconciliation can make the terminal call.
        log "decision remains coupled to a running action; stopping this queue pass"
        return 75 ;;
      absent)
        if [ "$child_rc" -eq 75 ] || [ -f "$ROOT/state/PAUSE" ]; then
          python3 "$ROOT/scripts/decision-queue.py" defer "$queue_file" "execution deferred" >/dev/null \
            || return $?
          return 75
        fi
        python3 "$ROOT/scripts/decision-queue.py" fail "$queue_file" "no action record rc=$child_rc" >/dev/null \
          || return $?
        aggregate=1 ;;
      *)
        log "corrupt action state '$action_state'; preserving the running decision"
        return 74 ;;
    esac
  done
  return "$aggregate"
}

if [ -z "$FILE" ]; then
  drain_queue
  exit $?
fi

[ -f "$FILE" ] || { log "no decision file at $FILE"; exit 2; }

VERBS="noop plan work conduct publish escalate resolve-esc reap roadmap-add roadmap-new portfolio-add project-topic-bind register note assist-answer pilot-plan-propose pilot-task-create pilot-worker-request pilot-verifier-request pilot-block pilot-escalate pilot-goal-verify"
RAW_DECISION="$(cat "$FILE" 2>/dev/null || true)"
VALID="$(python3 "$ROOT/scripts/validate-decision.py" "$VERBS" "$RAW_DECISION" 2>&1)"
case "$VALID" in
  OK\ *) : ;;
  *) log "REFUSED - ${VALID:-decision validation produced no output}"; exit 5 ;;
esac

read_field(){ python3 -c 'import json,sys;print(json.load(open(sys.argv[1],encoding="utf-8")).get(sys.argv[2],"") or "")' "$FILE" "$1" 2>/dev/null; }
VERB="$(read_field verb)"; WHY="$(read_field why)"; GOAL="$(read_field goal)"
DECISION_ID="$(read_field id)"; IDEMPOTENCY_KEY="$(read_field idempotency_key)"
INSTRUCTION_ID="$(read_field instruction_id)"
mapfile -t ARGS < <(python3 -c 'import json,sys
d=json.load(open(sys.argv[1],encoding="utf-8"))
for a in (d.get("args") or []): print(a)' "$FILE" 2>/dev/null)

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

# --- PAUSE: deciding is awareness, acting is not (D-012). --------------------------------
if [ -f "$ROOT/state/PAUSE" ] && [ "$VERB" != "noop" ]; then
  log "PAUSED — refusing to execute '$VERB'. The decision is recorded; it will not run until resume."
  ev decision-deferred "paused: $VERB"
  exit 75
fi

# --- durable action claim. The decision file may be replayed after a crash or scheduler retry.
# A deterministic action id plus an append-only lifecycle journal makes that replay observe the
# prior claim instead of dispatching again. This strengthens the existing actuator; it does not
# introduce a second execution path.
ACTION_LOCK=""; ACTION_LOCK_HELD=0; ACTION_FILE=""; ACTION_ID=""
action_unlock(){
  [ "$ACTION_LOCK_HELD" = 1 ] || return 0
  rm -f -- "$ACTION_LOCK/pid" 2>/dev/null || true
  rmdir "$ACTION_LOCK" 2>/dev/null || true
  ACTION_LOCK_HELD=0
}
action_lock(){
  local i=0 holder
  mkdir -p "$ROOT/state/actions" "$ROOT/state/.locks" || return 70
  ACTION_LOCK="$ROOT/state/.locks/action-$ACTION_ID.lock"
  while :; do
    if [ ! -d "$ROOT/state/.locks/runtime-state.lock" ] && mkdir "$ACTION_LOCK" 2>/dev/null; then
      break
    fi
    holder="$(cat "$ACTION_LOCK/pid" 2>/dev/null || true)"
    case "$holder" in
      ''|*[!0-9]*) : ;;
      *) if ! kill -0 "$holder" 2>/dev/null; then
           rm -f -- "$ACTION_LOCK/pid" 2>/dev/null || true
           rmdir "$ACTION_LOCK" 2>/dev/null || true
           continue
         fi ;;
    esac
    i=$((i+1))
    [ "$i" -lt "${RECURSION_LOCK_ATTEMPTS:-100}" ] \
      || { log "action lock contended; refusing duplicate/unlocked dispatch"; return 73; }
    sleep "${RECURSION_LOCK_DELAY_S:-0.1}"
  done
  printf '%s\n' "$$" > "$ACTION_LOCK/pid"
  ACTION_LOCK_HELD=1
}
action_field(){
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get(sys.argv[2],"") or "")' \
    "$ACTION_FILE" "$1" 2>/dev/null
}
action_transition(){ # status evidence
  local status="$1" evidence="${2:-}" rc
  ACTION_STATUS="$status" ACTION_EVIDENCE="$evidence" ACTION_ID="$ACTION_ID" \
  ACTION_KEY="$IDEMPOTENCY_KEY" ACTION_DECISION="$DECISION_ID" \
  ACTION_INSTRUCTION="$INSTRUCTION_ID" ACTION_VERB="$VERB" ACTION_GOAL="$GOAL" \
  ACTION_SOURCE="$FILE" ACTION_OWNER="$$@$(hostname)" \
  python3 - "$ACTION_FILE" "$ROOT/state/action-events.jsonl" <<'PY'
import json,os,sys,tempfile,time
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
      'arguments':json.load(open(os.environ['ACTION_SOURCE'],encoding='utf-8')).get('args') or [],
      'goal_id':os.environ.get('ACTION_GOAL') or None,'status':'pending',
      'lease_owner':None,'lease_expires':None,'attempts':0,'result_evidence':None,
      'created_at':now,'updated_at':now,
    }
if status=='running':
    record['attempts']=int(record.get('attempts') or 0)+1
    record['lease_owner']=os.environ['ACTION_OWNER']
    record['lease_expires']=int(time.time())+int(os.environ.get('RECURSION_ACTION_LEASE_S','3600'))
elif status in ('succeeded','failed','cancelled'):
    record['lease_owner']=None; record['lease_expires']=None
record['status']=status
record['result_evidence']=os.environ.get('ACTION_EVIDENCE') or None
record['updated_at']=now
directory=os.path.dirname(path); os.makedirs(directory,exist_ok=True)
fd,tmp=tempfile.mkstemp(prefix='.'+os.path.basename(path)+'.tmp.',dir=directory)
try:
    with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as out:
        json.dump(record,out,sort_keys=True,separators=(',',':')); out.write('\n')
        out.flush(); os.fsync(out.fileno())
    os.replace(tmp,path)
    dfd=os.open(directory,os.O_RDONLY)
    try: os.fsync(dfd)
    finally: os.close(dfd)
except BaseException:
    try: os.unlink(tmp)
    except FileNotFoundError: pass
    raise
event={'schema_version':1,'ts':now,'action_id':record['id'],'status':status,
       'attempt':record['attempts'],'idempotency_key':record['idempotency_key'],
       'evidence':record['result_evidence']}
jfd=os.open(journal,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
try:
    os.write(jfd,(json.dumps(event,sort_keys=True,separators=(',',':'))+'\n').encode())
    os.fsync(jfd)
finally: os.close(jfd)
PY
  rc=$?
  [ "$rc" -eq 0 ] || log "failed durable action transition status=$status rc=$rc"
  return "$rc"
}

if [ "$DRY" = 0 ]; then
  if [ -z "$IDEMPOTENCY_KEY" ]; then
    IDEMPOTENCY_KEY="decision:${DECISION_ID:-$(sha256sum "$FILE" | awk '{print $1}')}"
  fi
  [ "${#IDEMPOTENCY_KEY}" -le 256 ] \
    || { log "REFUSED — idempotency key exceeds 256 characters"; exit 5; }
  ACTION_ID="action-$(printf '%s' "$IDEMPOTENCY_KEY" | sha256sum | cut -c1-24)"
  ACTION_FILE="$ROOT/state/actions/$ACTION_ID.json"
  action_lock || exit $?
  trap 'action_unlock' EXIT
  if [ -f "$ACTION_FILE" ]; then
    prior="$(action_field status)"
    case "$prior" in
      succeeded) log "idempotent replay: $ACTION_ID already succeeded; no dispatch"; action_unlock; trap - EXIT; exit 0 ;;
      failed|cancelled) log "idempotent replay: $ACTION_ID is terminal ($prior); explicit retry required"; action_unlock; trap - EXIT; exit 1 ;;
      running)
        lease="$(action_field lease_expires)"
        if printf '%s' "$lease" | grep -qE '^[0-9]+$' && [ "$lease" -le "$(date +%s)" ]; then
          action_transition failed "stale dispatch lease expired; reconciliation refused relaunch" || true
          log "recovery: $ACTION_ID lease expired; marked failed for explicit reconciliation, not relaunched"
          action_unlock; trap - EXIT; exit 1
        fi
        log "recovery: $ACTION_ID was already dispatched; refusing a double launch"
        action_unlock; trap - EXIT; exit 75 ;;
      pending) : ;;
      *) log "REFUSED — corrupt/unknown action status '$prior'"; action_unlock; trap - EXIT; exit 74 ;;
    esac
  else
    action_transition pending "decision accepted" || { action_unlock; trap - EXIT; exit 74; }
  fi
  action_transition running "dispatch claimed" || { action_unlock; trap - EXIT; exit 74; }
  if [ "${RECURSION_QUEUE_ACTUATION:-0}" = 1 ] && [ -n "$INSTRUCTION_ID" ]; then
    if ! RECURSION_ROOT="$ROOT" bash scripts/intake.sh consume "$INSTRUCTION_ID" "$ACTION_ID"; then
      action_transition failed "instruction coupling failed before dispatch" || true
      action_unlock; trap - EXIT
      exit 74
    fi
  fi
fi

log "verb=$VERB args=[${ARGS[*]-}] goal=${GOAL:0:60}"
[ -n "$WHY" ] && log "why: ${WHY:0:160}"

run(){ # execute an argv array, or print it under --dry-run
  if [ "$DRY" = "1" ]; then printf '  WOULD RUN:'; printf ' %q' "$@"; printf '\n'; return 0; fi
  "$@"
}

# --- the whitelist. A fixed case list: there is no path from an unrecognised verb to
# execution, and nothing here reaches auth, cron, .env, flags, merges, or deploys. --------
rc=0
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

  pilot-plan-propose|pilot-task-create|pilot-worker-request|pilot-verifier-request|pilot-block|pilot-escalate|pilot-goal-verify)
    # Project-pilot authority is rechecked against the durable topic/pilot/charter records here.
    # The helper may create scoped proposal/task state; it never launches a worker or publishes.
    run python3 scripts/project-pilot.py execute "$FILE"; rc=$? ;;

  assist-answer)
    A0="${ARGS[0]:-}"; [ -n "$A0" ] || { log "assist-answer needs a task id"; exit 2; }
    [ -n "$TEXT" ] || { log "REFUSED - assist-answer needs prose in the text field"; exit 2; }
    run bash scripts/assist.sh answer "$A0" "$TEXT"; rc=$? ;;

  noop)
    log "noop — nothing to run${WHY:+ ($WHY)}" ;;

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
    if [ -z "$(sed -n 's/^acceptance: *//p' "state/tasks/$ID.md" | head -1)" ]; then
      log "REFUSED — task $ID has no acceptance gate; it must escalate, not run"; exit 5
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
    KEY="${ARGS[0]:-}"; TITLE="${ARGS[1]:-$KEY}"
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
      RECURSION_ROOT="$ROOT" bash scripts/intake.sh acknowledge "$INSTRUCTION_ID" "$ACTION_ID" \
        || { rc=74; action_transition failed "instruction acknowledgement failed" || true; }
    fi
  else action_transition failed "log=$LOG rc=$rc"
  fi || rc=74
  ev decision-executed "$VERB rc=$rc"
  action_unlock; trap - EXIT
}
log "done (verb=$VERB rc=$rc)"
exit "$rc"

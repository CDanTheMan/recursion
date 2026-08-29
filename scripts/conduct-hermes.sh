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
#   conduct-hermes.sh --non-work-only drain only state/approval decisions
#   conduct-hermes.sh --work-only     drain only worker decisions
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT" 2>/dev/null || exit 2
[ -f .env ] && set -a && . ./.env && set +a
# .env pins RECURSION_ROOT for the deployed checkout. Sourcing it must never RETARGET a
# caller who passed a different root: that silently made a "sandbox" enqueue ten decisions
# into production on 2026-08-12. ROOT and RECURSION_ROOT agree from here on.
RECURSION_ROOT="$ROOT"; export RECURSION_ROOT

FILE=""; DRY=0; PAUSED_SAFE=0; RECOVER_ONLY=0; NON_WORK_ONLY=0; WORK_ONLY=0
CLI_ERROR=0
# A queue claim supplies these immutable bytes through the child environment. Direct --file
# invocation captures them below. The child never re-reads a path as its decision authority.
DECISION_SNAPSHOT_B64="${RECURSION_DECISION_SNAPSHOT_B64:-}"
DECISION_FILE_DIGEST="${RECURSION_DECISION_FILE_DIGEST:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --file)
      if [ "$#" -lt 2 ]; then CLI_ERROR=1; shift; continue; fi
      [ -z "$FILE" ] || CLI_ERROR=1
      FILE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --paused-safe) PAUSED_SAFE=1; shift ;;
    --recover-only) RECOVER_ONLY=1; shift ;;
    --non-work-only) NON_WORK_ONLY=1; shift ;;
    --work-only) WORK_ONLY=1; shift ;;
    *) CLI_ERROR=1; shift ;;
  esac
done
RECOVERY_SCOPE_ARGS=()
[ "$NON_WORK_ONLY" = 1 ] && RECOVERY_SCOPE_ARGS+=(--non-work-only)
[ "$WORK_ONLY" = 1 ] && RECOVERY_SCOPE_ARGS+=(--work-only)
CHILD_SCOPE_ARGS=("${RECOVERY_SCOPE_ARGS[@]}")

# Scope is an admission boundary, not merely a queue preference.  It must run before action
# recovery because recovery can acknowledge or release the instruction coupled to an action.
# A state-only actuator may therefore never touch a work decision (and vice versa), including a
# directly supplied --file or a claim left in running/ after a crash.
scope_allows_file(){
  local path="$1" verb
  if [ "$NON_WORK_ONLY" = 0 ] && [ "$WORK_ONLY" = 0 ]; then return 0; fi
  verb="$(python3 - "$path" "${DECISION_SNAPSHOT_B64:-}" <<'PY' 2>/dev/null
import base64,binascii,json,sys
try:
    if sys.argv[2]:
        value=base64.b64decode(sys.argv[2], validate=True).decode("utf-8")
    else:
        value=open(sys.argv[1], encoding="utf-8").read(2 * 1024 * 1024 + 1)
    if len(value) > 2 * 1024 * 1024: raise ValueError("decision is too large")
    row=json.loads(value, parse_constant=lambda name: (_ for _ in ()).throw(ValueError(name)))
    print(row.get("verb", "") if isinstance(row, dict) else "")
except (OSError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError,
        json.JSONDecodeError,binascii.Error):
    raise SystemExit(2)
PY
)" || return 2
  if [ "$WORK_ONLY" = 1 ]; then
    [ "$verb" = work ]
  else
    [ "$verb" != work ]
  fi
}
scope_guard(){
  local scope_rc current_digest
  [ -n "${DECISION_SNAPSHOT_B64:-}" ] || { log "REFUSED - immutable decision snapshot is absent"; return 74; }
  current_digest="$(python3 - "${DECISION_SNAPSHOT_B64}" <<'PY' 2>/dev/null
import base64,binascii,hashlib,sys
try:
    raw=base64.b64decode(sys.argv[1], validate=True)
    if len(raw) > 2 * 1024 * 1024: raise ValueError("decision is too large")
except (ValueError,TypeError,binascii.Error): raise SystemExit(2)
print(hashlib.sha256(raw).hexdigest())
PY
)" || return 74
  [ "$current_digest" = "$DECISION_FILE_DIGEST" ] || { log "REFUSED - immutable decision snapshot digest changed"; return 74; }
  # The queue projection is checked against the snapshotted bytes before each action.  The action
  # itself always consumes DECISION_JSON from that same immutable stream, so a swap after this
  # observation cannot redirect the validated verb or arguments.
  local source_digest
  source_digest="$(python3 - "$FILE" <<'PY' 2>/dev/null
import hashlib,sys
try:
    with open(sys.argv[1], "rb") as source: raw=source.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024: raise ValueError("decision is too large")
    print(hashlib.sha256(raw).hexdigest())
except (OSError,ValueError): raise SystemExit(2)
PY
)" || { log "REFUSED - decision disappeared before child action"; return 74; }
  [ "$source_digest" = "$DECISION_FILE_DIGEST" ] || { log "REFUSED - decision projection changed before child action"; return 74; }
  scope_allows_file "$FILE"; scope_rc=$?
  [ "$scope_rc" -eq 0 ] && return 0
  [ "$scope_rc" -eq 1 ] && log "REFUSED - decision scope changed before child action" \
    || log "REFUSED - decision scope could not be authenticated before child action"
  return 74
}
DATE="$(date +%F)"
LOG="$ROOT/loop/logs/$DATE-conduct-hermes.log"; mkdir -p "$(dirname "$LOG")"
log(){ echo "[$(date -Is)] conduct-hermes: $*" | tee -a "$LOG" >&2; }
[ "$CLI_ERROR" = 0 ] || { log "REFUSED - invalid command-line parameters"; exit 2; }
[ "$NON_WORK_ONLY" = 0 ] || [ "$WORK_ONLY" = 0 ] \
  || { log "REFUSED - --non-work-only and --work-only are mutually exclusive"; exit 2; }
ev(){ bash scripts/taskctl.sh event "$1" "" "$2" >/dev/null 2>&1 || true; }

claim_from_queue(){
  local output; local -a fields
  CLAIMED_FILE=""; CLAIMED_DIGEST=""; CLAIMED_SNAPSHOT=""
  output="$(python3 "$ROOT/scripts/decision-queue.py" claim-pending "$@" --with-snapshot)"
  CLAIM_RC=$?
  [ "$CLAIM_RC" -eq 0 ] || return "$CLAIM_RC"
  mapfile -t fields <<< "$output"
  [ "${#fields[@]}" -eq 3 ] && [ -n "${fields[0]}" ] \
    && [[ "${fields[1]}" =~ ^[0-9a-f]{64}$ ]] && [ -n "${fields[2]}" ] \
    || { log "REFUSED - queue claim returned an invalid immutable snapshot"; return 74; }
  CLAIMED_FILE="${fields[0]}"; CLAIMED_DIGEST="${fields[1]}"; CLAIMED_SNAPSHOT="${fields[2]}"
}

snapshot_running(){
  local output; local -a fields
  output="$(python3 "$ROOT/scripts/decision-queue.py" snapshot "$1")" || return 74
  mapfile -t fields <<< "$output"
  [ "${#fields[@]}" -eq 2 ] && [[ "${fields[0]}" =~ ^[0-9a-f]{64}$ ]] && [ -n "${fields[1]}" ] \
    || { log "REFUSED - running decision snapshot is invalid"; return 74; }
  CLAIMED_DIGEST="${fields[0]}"; CLAIMED_SNAPSHOT="${fields[1]}"
}

run_claimed_child(){
  local path="$1" digest="$2" snapshot="$3"; shift 3
  RECURSION_DECISION_FILE_DIGEST="$digest" RECURSION_DECISION_SNAPSHOT_B64="$snapshot" \
    RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="$ROOT" \
    bash "$ROOT/scripts/conduct-hermes.sh" "$@" --file "$path" 8>&-
}

drain_queue(){
  local queue_file claim_rc child_rc action_state aggregate=0 project global first i claimed_digest
  local import_error import_rc
  local -a pids=() files=() projects=() digests=() snapshots=() claim_args=()
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
    quarantine_sha="$(python3 -c 'import json,sys
try:
    with open(sys.argv[1],"rb") as source: raw=source.read(65537)
    if len(raw)>65536: raise ValueError("quarantine metadata is too large")
    value=json.loads(raw.decode("utf-8","strict"),parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
    print(value.get("tail_sha256","") if isinstance(value,dict) else "")
except (OSError,json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    raise SystemExit(2)' \
      "$quarantine_record" 2>/dev/null || true)"
    [ -n "$quarantine_sha" ] || continue
    RECURSION_ROOT="$ROOT" bash "$ROOT/scripts/taskctl.sh" esc-record \
      "decision-journal-tail-$quarantine_sha" \
      "A torn decision-journal tail was quarantined; review crash evidence" \
      infra "${quarantine_record#$ROOT/}" >/dev/null 2>&1 || true
  done

  finalize_claim(){
    local claimed="$1" result_rc="$2" queue_sha="$3" queue_snapshot="$4" state reconcile_rc=0
    # queue_sha is captured immediately after claim and retained across child execution.  Never
    # hash the post-action path here: that would let a swapped projection become the authority
    # used by terminalization after the immutable child snapshot has completed.
    [[ "$queue_sha" =~ ^[0-9a-f]{64}$ ]] || { log "original claimed decision digest is absent"; return 74; }
    state="$(python3 "$ROOT/scripts/decision-queue.py" action-status "$claimed" --expected-sha256 "$queue_sha")" || return $?
    case "$state" in
      succeeded|failed|cancelled|pending)
        # The child can die after writing its terminal/deferred action but before projecting the
        # coupled instruction. Reconcile that handshake idempotently before moving the decision;
        # otherwise the parent would hide the only projection capable of recovery.
        run_claimed_child "$claimed" "$queue_sha" "$queue_snapshot" \
          --recover-only "${CHILD_SCOPE_ARGS[@]}" 8>&- \
          >/dev/null 2>&1 || reconcile_rc=$?
        case "$state:$reconcile_rc" in
          succeeded:0|failed:1|cancelled:1|pending:75) : ;;
          *) log "instruction/action recovery failed state=$state rc=$reconcile_rc; preserving $claimed"; return 74 ;;
        esac
        state="$(python3 "$ROOT/scripts/decision-queue.py" action-status "$claimed" --expected-sha256 "$queue_sha")" || return $?
        case "$state" in
          succeeded) python3 "$ROOT/scripts/decision-queue.py" succeed "$claimed" "action succeeded" --expected-sha256 "$queue_sha" >/dev/null ;;
          failed|cancelled)
        python3 "$ROOT/scripts/decision-queue.py" fail "$claimed" "action $state rc=$result_rc" --expected-sha256 "$queue_sha" >/dev/null
            aggregate=1 ;;
          pending)
            python3 "$ROOT/scripts/decision-queue.py" defer "$claimed" "action deferred rc=$result_rc" --expected-sha256 "$queue_sha" >/dev/null
            return 75 ;;
          *) log "action changed unexpectedly during recovery: $state"; return 74 ;;
        esac
        ;;
      running) log "decision remains coupled to a running action"; return 75 ;;
      absent)
        if [ "$result_rc" -eq 75 ]; then
          python3 "$ROOT/scripts/decision-queue.py" defer "$claimed" "execution deferred" --expected-sha256 "$queue_sha" >/dev/null
          return 75
        fi
        if [ -f "$ROOT/state/PAUSE" ]; then
          # PAUSE preserves pending state, but it must not RELABEL a refusal as a deferral.
          # A genuine PAUSE decline returns 75 above; any other rc here means the child refused
          # (bad provenance, inconsistent digest, unsafe argument...). Masking those as
          # deferrals is how an undrainable record spins forever while the actuator reports
          # healthy -- observed 2026-08-12. Disposition is unchanged; visibility is not.
          log "REFUSED under PAUSE - child rc=$result_rc for ${claimed#$ROOT/}; pending preserved, NOT a deferral"
          python3 "$ROOT/scripts/decision-queue.py" defer "$claimed" "refused under pause rc=$result_rc" --expected-sha256 "$queue_sha" >/dev/null
          return 76
        fi
        python3 "$ROOT/scripts/decision-queue.py" fail "$claimed" "no action record rc=$result_rc" --expected-sha256 "$queue_sha" >/dev/null
        aggregate=1 ;;
      *) log "corrupt action state '$state'; preserving $claimed"; return 74 ;;
    esac
  }

  # Reconcile projections left running by a prior actuator process before claiming anything
  # new. A genuinely running action is never double-launched and blocks new admissions until
  # its own durable action reaches terminal state.
  for queue_file in "$ROOT/state/decision-queue/running"/*.json; do
    [ -f "$queue_file" ] || continue
    snapshot_running "$queue_file" || return 74
    DECISION_SNAPSHOT_B64="$CLAIMED_SNAPSHOT"; DECISION_FILE_DIGEST="$CLAIMED_DIGEST"
    scope_allows_file "$queue_file"; scope_rc=$?
    if [ "$scope_rc" -ne 0 ]; then
      [ "$scope_rc" -eq 1 ] || { log "recovery scope could not inspect $queue_file; preserving it"; return 74; }
      continue
    fi
    action_state="$(python3 "$ROOT/scripts/decision-queue.py" action-status "$queue_file" --expected-sha256 "$CLAIMED_DIGEST")" || return $?
    case "$action_state" in
      absent) python3 "$ROOT/scripts/decision-queue.py" defer "$queue_file" "recovered claim had no action" \
        --expected-sha256 "$CLAIMED_DIGEST" >/dev/null || return $? ;;
      succeeded|failed|cancelled|running|pending)
        # Re-enter only the recovery path so the coupled instruction is acknowledged/released
        # before the decision projection becomes terminal. No verb is dispatched here.
        run_claimed_child "$queue_file" "$CLAIMED_DIGEST" "$CLAIMED_SNAPSHOT" \
          --recover-only "${CHILD_SCOPE_ARGS[@]}"
        child_rc=$?
        finalize_claim "$queue_file" "$child_rc" "$CLAIMED_DIGEST" "$CLAIMED_SNAPSHOT" || return $?
        ;;
      *) log "corrupt recovered action state '$action_state'"; return 74 ;;
    esac
  done

  # Deterministic state transitions run serially. They may enqueue more transitions, which this
  # same loop drains before any worker dispatch, preserving the goal/task CAS order.
  while [ "$WORK_ONLY" = 0 ]; do
    if [ "$PAUSED_SAFE" = 1 ]; then
      claim_from_queue --kind non-work \
        --verb noop --verb pilot-plan-propose --verb pilot-plan-approve --verb pilot-window-open \
        --verb pilot-window-close --verb assist-answer --verb routing-refuse
      claim_rc=$?
    else
      claim_from_queue --kind non-work
      claim_rc=$?
    fi
    [ "$claim_rc" -ne 4 ] || break
    [ "$claim_rc" -eq 0 ] || return "$claim_rc"
    queue_file="$CLAIMED_FILE"; claimed_digest="$CLAIMED_DIGEST"; claimed_snapshot="$CLAIMED_SNAPSHOT"
    run_claimed_child "$queue_file" "$claimed_digest" "$claimed_snapshot" "${CHILD_SCOPE_ARGS[@]}"
    child_rc=$?
    finalize_claim "$queue_file" "$child_rc" "$claimed_digest" "$claimed_snapshot" || return $?
  done

  [ "$PAUSED_SAFE" = 0 ] || return "$aggregate"
  [ "$NON_WORK_ONLY" = 0 ] || return "$aggregate"

  # Work decisions remain ordinary actions through this same actuator. The only difference is
  # that independent projects may occupy separate bounded slots. One slot per project plus the
  # global ceiling proves isolation; project/goal/window admission is rechecked in --file.
  global="${RECURSION_PILOT_GLOBAL_CONCURRENCY:-1}"
  case "$global" in ''|*[!0-9]*) log "invalid global pilot concurrency '$global'"; return 4 ;; esac
  [ "${#global}" -le 3 ] || { log "global pilot concurrency is too large"; return 4; }
  global=$((10#$global))
  [ "$global" -ge 1 ] && [ "$global" -le 16 ] || { log "global pilot concurrency must be 1..16"; return 4; }
  while :; do
    while [ "${#pids[@]}" -lt "$global" ]; do
      claim_args=(claim-pending --kind work)
      for project in "${projects[@]}"; do claim_args+=(--exclude-project "$project"); done
      claim_from_queue "${claim_args[@]:1}"
      claim_rc=$?
      [ "$claim_rc" -ne 4 ] || break
      [ "$claim_rc" -eq 0 ] || return "$claim_rc"
      queue_file="$CLAIMED_FILE"; claimed_digest="$CLAIMED_DIGEST"; claimed_snapshot="$CLAIMED_SNAPSHOT"
      project="$(python3 - "$claimed_snapshot" <<'PY'
import base64,binascii,json,sys
try:
    raw=base64.b64decode(sys.argv[1], validate=True)
    if len(raw) > 2 * 1024 * 1024: raise ValueError("decision is too large")
    row=json.loads(raw.decode("utf-8"), parse_constant=lambda name: (_ for _ in ()).throw(ValueError(name)))
except (OSError,ValueError,TypeError,UnicodeError,binascii.Error,OverflowError,
        RecursionError,json.JSONDecodeError):
    raise SystemExit(2)
print(row.get('project') if isinstance(row, dict) else '')
PY
)"
      [ -n "$project" ] || project="unknown-$(basename "$queue_file")"
      run_claimed_child "$queue_file" "$claimed_digest" "$claimed_snapshot" "${CHILD_SCOPE_ARGS[@]}" &
      pids+=("$!"); files+=("$queue_file"); projects+=("$project"); digests+=("$claimed_digest"); snapshots+=("$claimed_snapshot")
    done
    [ "${#pids[@]}" -gt 0 ] || break
    first="${pids[0]}"; queue_file="${files[0]}"
    wait "$first"; child_rc=$?
    finalize_claim "$queue_file" "$child_rc" "${digests[0]}" "${snapshots[0]}" || return $?
    pids=("${pids[@]:1}"); files=("${files[@]:1}"); projects=("${projects[@]:1}"); digests=("${digests[@]:1}"); snapshots=("${snapshots[@]:1}")
    if [ -f "$ROOT/state/PAUSE" ]; then
      for ((i=0; i<${#pids[@]}; i++)); do
        wait "${pids[$i]}"; child_rc=$?
        finalize_claim "${files[$i]}" "$child_rc" "${digests[$i]}" "${snapshots[$i]}" || true
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

python3 - "$FILE" <<'PY' || { log "REFUSED - decision file path is unsafe or unavailable"; exit 2; }
import os,re,stat,sys
from pathlib import Path
try:
    raw=sys.argv[1]
    if not isinstance(raw,str) or not raw or len(raw.encode("utf-8")) > 4096:
        raise ValueError("decision file path is invalid")
    normalized=raw.replace("\\", "/")
    if ("\x00" in raw or any(ord(char) < 32 for char in raw)
            or raw.startswith(("\\\\", "//", "~")) or "%" in raw
            or re.match(r"^[A-Za-z]:[^\\/].*", raw)
            or any(part in {".", ".."} for part in normalized.split("/"))
            or "//" in normalized[1:]):
        raise ValueError("decision file path is not canonical")
    path=Path(raw)
    if not path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise ValueError("decision file must be a canonical absolute path")
    current=Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        info=current.lstat()
        if (stat.S_ISLNK(info.st_mode) or getattr(info,"st_reparse_tag",0)
                or bool(getattr(info,"st_file_attributes",0) & 0x400)):
            raise ValueError("reparse path")
    flags=os.O_RDONLY|getattr(os,"O_BINARY",0)|getattr(os,"O_NOFOLLOW",0)
    descriptor=os.open(path,flags)
    try:
        info=os.fstat(descriptor)
        if (stat.S_ISLNK(info.st_mode) or getattr(info,"st_reparse_tag",0)
                or bool(getattr(info,"st_file_attributes",0) & 0x400)
                or not stat.S_ISREG(info.st_mode)):
            raise ValueError("not regular")
    finally:
        os.close(descriptor)
except OSError:
    print("boundary=decision-path-unavailable", file=sys.stderr)
    raise SystemExit(2)
except (ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    print("boundary=decision-path-invalid", file=sys.stderr)
    raise SystemExit(2)
PY
if [ -z "$DECISION_SNAPSHOT_B64" ] || [ -z "$DECISION_FILE_DIGEST" ]; then
SNAPSHOT_BUNDLE="$(python3 - "$FILE" <<'PY'
import base64,hashlib,sys
try:
    with open(sys.argv[1], "rb") as source: raw=source.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024: raise ValueError("decision is too large")
except OSError:
    print("boundary=decision-snapshot-unavailable", file=sys.stderr)
    raise SystemExit(2)
except (ValueError, TypeError):
    print("boundary=decision-size", file=sys.stderr)
    raise SystemExit(2)
print(hashlib.sha256(raw).hexdigest())
print(base64.b64encode(raw).decode("ascii"))
PY
)" || { log "REFUSED - decision snapshot could not be captured"; exit 74; }
DECISION_FILE_DIGEST="${SNAPSHOT_BUNDLE%%$'\n'*}"
DECISION_SNAPSHOT_B64="${SNAPSHOT_BUNDLE#*$'\n'}"
unset SNAPSHOT_BUNDLE
else
  [[ "$DECISION_FILE_DIGEST" =~ ^[0-9a-f]{64}$ ]] && [ -n "$DECISION_SNAPSHOT_B64" ] \
    || { log "REFUSED - supplied decision snapshot is malformed"; exit 74; }
fi
# Do this before validation, action identity, consume, acknowledge, or release.  An out-of-scope
# file remains untouched so its owning actuator can recover it.
scope_allows_file "$FILE"; scope_rc=$?
[ "$scope_rc" -eq 0 ] || {
  [ "$scope_rc" -eq 1 ] && { log "REFUSED - decision is outside actuator scope"; exit 74; }
  log "REFUSED - decision scope could not be authenticated"; exit 74
}

VERBS="noop plan work conduct publish escalate resolve-esc reap roadmap-add roadmap-new portfolio-add project-topic-bind register note assist-answer pilot-plan-propose pilot-plan-approve pilot-window-open pilot-window-close pilot-task-create pilot-worker-request pilot-verifier-request pilot-block pilot-escalate pilot-goal-verify reconcile-goal task-transition goal-transition verify-goal publish-task notification-reconcile notification-deliver notification-portfolio notification-audit notification-recover routing-refuse"
RAW_DECISION="$(python3 - "$DECISION_SNAPSHOT_B64" <<'PY'
import base64,binascii,sys
try:
    raw=base64.b64decode(sys.argv[1], validate=True)
    if len(raw) > 2 * 1024 * 1024: raise ValueError("decision is too large")
    sys.stdout.write(raw.decode("utf-8", "strict"))
except (OSError,ValueError,TypeError,UnicodeError,binascii.Error,OverflowError,
        RecursionError):
    raise SystemExit(2)
PY
)" || { log "REFUSED - decision snapshot could not be decoded: boundary=utf8-strict"; exit 74; }

# CLASS B: the snapshot is caller-controlled bytes until this local boundary has proved that it
# is bounded JSON with a typed object shape.  The external validator below checks decision
# semantics; it is not the input boundary and must never be the first code to touch hostile JSON.
class_b_decision_json(){
  python3 - "$1" <<'PY'
import json,math,re,sys

MAX_BYTES=2 * 1024 * 1024
MAX_INTEGER=2**63 - 1
MAX_STRING=4096
MAX_ITEMS=256
MAX_DEPTH=64
INTEGER_FIELDS={
    "schema_version", "max_concurrency", "max_tokens", "max_wall_clock_seconds",
    "max_task_attempts", "max_failures", "max_review_queue", "max_publish_attempts",
    "deadline_seconds", "verifier_deadline_seconds",
}
REAL_FIELDS={"cost_usd", "max_cost_usd", "estimated_cost_usd"}
PATH_FIELDS={
    "path", "file", "directory", "root", "runtime_root", "runtime_directory",
    "snapshot_directory", "recipient_file", "signature_file",
}

def bounded_int(raw):
    digits=raw[1:] if raw.startswith("-") else raw
    if len(digits) > 19:
        raise ValueError("decision integer is out of range")
    value=int(raw)
    if not -MAX_INTEGER - 1 <= value <= MAX_INTEGER:
        raise ValueError("decision integer is out of range")
    return value

def bounded_float(raw):
    value=float(raw)
    if not math.isfinite(value) or abs(value) > 1e308:
        raise ValueError("decision number is non-finite or out of range")
    return value

def check_path(value):
    normalized=value.replace("\\", "/")
    if (not value or value.startswith(("\\\\", "//", "~")) or "%" in value
            or re.match(r"^[A-Za-z]:[^\\/].*", value)
            or any(part in {".", ".."} for part in normalized.split("/"))
            or "//" in normalized[1:]):
        raise ValueError("decision path is unsafe")

def check_value(value, depth=0, key=None):
    if depth > MAX_DEPTH:
        raise ValueError("decision nesting is too deep")
    if key in INTEGER_FIELDS and type(value) is not int:
        raise TypeError("decision integer field has the wrong type")
    if key in REAL_FIELDS and value is not None \
            and (isinstance(value, bool) or not isinstance(value, (int, float))):
        raise TypeError("decision numeric field has the wrong type")
    if key in PATH_FIELDS:
        if value is not None and not isinstance(value, str):
            raise TypeError("decision path field has the wrong type")
        if isinstance(value, str):
            check_path(value)
    if isinstance(value, str):
        if len(value) > MAX_STRING or any(ord(char) < 32 for char in value):
            raise ValueError("decision string is invalid")
        return
    if type(value) is int:
        if not -MAX_INTEGER - 1 <= value <= MAX_INTEGER:
            raise ValueError("decision integer is out of range")
        return
    if isinstance(value, float):
        if not math.isfinite(value) or abs(value) > 1e308:
            raise ValueError("decision number is non-finite or out of range")
        return
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, list):
        if len(value) > MAX_ITEMS:
            raise ValueError("decision array is too large")
        for item in value:
            check_value(item, depth + 1, key)
        return
    if isinstance(value, dict):
        if len(value) > MAX_ITEMS:
            raise ValueError("decision object is too large")
        for key, item in value.items():
            if (not isinstance(key, str) or len(key) > MAX_STRING
                    or any(ord(char) < 32 for char in key)):
                raise ValueError("decision object key is invalid")
            check_value(item, depth + 1, key)
        return
    raise TypeError("decision contains an unsupported value")

try:
    raw=sys.argv[1]
    if not isinstance(raw,str) or len(raw.encode("utf-8")) > MAX_BYTES:
        raise ValueError("decision exceeds the bounded input size")
    value=json.loads(raw, parse_int=bounded_int, parse_float=bounded_float,
                     parse_constant=lambda name: (_ for _ in ()).throw(ValueError(
                         "decision JSON constant is forbidden")))
    if not isinstance(value, dict):
        raise ValueError("decision is not an object")
    check_value(value)
    if "schema_version" in value and (type(value["schema_version"]) is not int
                                       or value["schema_version"] != 1):
        raise ValueError("decision schema_version must be the integer 1")
    string_fields={
        "actor", "confidence", "decision_source", "goal", "goal_id", "id",
        "idempotency_key", "instruction_id", "project", "provider", "reason",
        "routed_decider", "status", "text", "ts", "verb", "why", "wrong_if",
        "decision_payload_sha256",
    }
    list_fields={"args", "arguments"}
    for field, item in value.items():
        if field in string_fields and item is not None and not isinstance(item,str):
            raise TypeError("decision field has the wrong type")
        if field in list_fields:
            if not isinstance(item,list) or any(not isinstance(arg,str) for arg in item):
                raise TypeError("decision arguments have the wrong type")
        if field == "cost_usd":
            if item is not None and (isinstance(item,bool) or not isinstance(item,(int,float))):
                raise TypeError("decision cost has the wrong type")
        if field in {"schema_version"} and isinstance(item,bool):
            raise TypeError("decision integer field is boolean")
    print(json.dumps(value, sort_keys=True, separators=(",",":"),
                     ensure_ascii=False, allow_nan=False))
except json.JSONDecodeError:
    print("boundary=malformed-json", file=sys.stderr)
    raise SystemExit(2)
except TypeError as exc:
    message=str(exc)
    if "integer field" in message:
        marker="integer-type"
    elif "numeric field" in message:
        marker="real-type"
    elif "path field" in message:
        marker="path-type"
    elif "arguments" in message:
        marker="arguments-type"
    else:
        marker="value-type"
    print("boundary=" + marker, file=sys.stderr)
    raise SystemExit(2)
except ValueError as exc:
    message=str(exc)
    if "JSON constant" in message:
        marker="json-constant"
    elif "not an object" in message:
        marker="non-object-root"
    elif "nesting" in message:
        marker="depth"
    elif "string" in message:
        marker="string"
    elif "path" in message:
        marker="path-unsafe"
    elif "non-finite" in message:
        marker="non-finite-number"
    elif "integer" in message:
        marker="integer-range"
    elif "exceeds" in message or "too large" in message:
        marker="decision-size"
    else:
        marker="value-invalid"
    print("boundary=" + marker, file=sys.stderr)
    raise SystemExit(2)
except RecursionError:
    print("boundary=depth", file=sys.stderr)
    raise SystemExit(2)
except (OverflowError,UnicodeDecodeError,UnicodeError,OSError):
    print("boundary=controlled-input-failure", file=sys.stderr)
    raise SystemExit(2)
PY
}
# PHASE4_CLASS_B_DECISION_BOUNDARY_CALL
DECISION_JSON="$(class_b_decision_json "$RAW_DECISION")" \
  || { log "REFUSED - decision input boundary rejected"; exit 5; }
VALID="$(python3 "$ROOT/scripts/validate-decision.py" "$VERBS" "$DECISION_JSON" 2>&1)"
VALID_RC=$?
if [ "$VALID_RC" -ne 0 ]; then
  case "$VALID" in
    ERR\ *) log "REFUSED - decision validation rejected the input: boundary=semantic-validation" ;;
    *) log "REFUSED - decision validator is unavailable" ;;
  esac
  exit 74
fi
case "$VALID" in
  OK\ *) DECISION_JSON="${VALID#OK }" ;;
  *) log "REFUSED - decision validation rejected the input: boundary=semantic-validation"; exit 5 ;;
esac

read_field(){ python3 -c 'import json,sys
try:
    value=json.loads(sys.argv[1],parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
    print(value.get(sys.argv[2],"") or "" if isinstance(value,dict) else "")
except (json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,
        RecursionError,OSError):
    raise SystemExit(2)' "$DECISION_JSON" "$1" 2>/dev/null; }
VERB="$(read_field verb)"; WHY="$(read_field why)"; GOAL="$(read_field goal)"
ACTOR="$(read_field actor)"
DECISION_PROJECT="$(read_field project)"
DECISION_SOURCE="$(read_field decision_source)"
ROUTED_DECIDER="$(read_field routed_decider)"
DECISION_ID="$(read_field id)"; IDEMPOTENCY_KEY="$(read_field idempotency_key)"
INSTRUCTION_ID="$(read_field instruction_id)"
ARGS_JSON="$(python3 -c 'import json,sys
try:
    value=json.loads(sys.argv[1],parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
    if not isinstance(value,dict): raise ValueError("decision is not an object")
    print(json.dumps(value.get("args") or [],separators=(",",":"),allow_nan=False))
except (json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,
        RecursionError,OSError):
    raise SystemExit(2)' "$DECISION_JSON")" \
  || { log "REFUSED - could not freeze decision arguments"; exit 5; }
ACTION_PAYLOAD_SHA256="$(python3 - "$DECISION_JSON" <<'PY'
import hashlib,json,sys
try:
 row=json.loads(sys.argv[1],parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
except (json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,
        RecursionError,OSError):
 raise SystemExit(2)
if not isinstance(row,dict):
 raise SystemExit(2)
payload={
    'actor':row.get('actor') or '', 'verb':row.get('verb') or '',
    'args':row.get('args',row.get('arguments',[])) or [], 'text':row.get('text') or '',
    'plan':row.get('plan') or None, 'instruction_id':row.get('instruction_id') or None,
    'project':row.get('project') or '', 'goal':row.get('goal',row.get('goal_id','')) or '',
    'decision_source':row.get('decision_source') or '',
    'routed_decider':row.get('routed_decider') or '',
}
raw=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
print(hashlib.sha256(raw).hexdigest())
PY
)" || { log "REFUSED - could not freeze complete action payload"; exit 5; }
DECISION_PAYLOAD_SHA256="$(read_field decision_payload_sha256)"
[ -n "$DECISION_PAYLOAD_SHA256" ] && [ "$DECISION_PAYLOAD_SHA256" = "$ACTION_PAYLOAD_SHA256" ] \
  || { log "REFUSED - decision authority/effect digest is absent or inconsistent"; exit 5; }
ARGS_LINES="$(python3 -c 'import json,sys
try:
    value=json.loads(sys.argv[1],parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
    if not isinstance(value,list) or any(not isinstance(a,str) for a in value): raise ValueError("args are invalid")
    for a in value: sys.stdout.buffer.write(a.encode()+b"\n")
except (json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,
        RecursionError,OSError):
    raise SystemExit(2)' "$ARGS_JSON" 2>/dev/null)" \
  || { log "REFUSED - could not materialize decision arguments"; exit 5; }
ARGS=()
[ -n "$ARGS_LINES" ] && mapfile -t ARGS <<< "$ARGS_LINES"
unset ARGS_LINES

[ -n "$VERB" ] || { log "decision has no verb"; exit 2; }

# --- re-validate args HERE. The decision file is on disk between decide and conduct, so
# validating only at decide time trusts a file anything could have rewritten. -------------
for a in ${ARGS+"${ARGS[@]}"}; do
  if ! printf '%s' "$a" | grep -qE '^[A-Za-z0-9][A-Za-z0-9._/-]{0,80}$'; then
    log "REFUSED - unsafe decision argument"
    ev decision-refused "unsafe arg for verb=$VERB"; exit 5
  fi
  case "$a" in
    *..*) log "REFUSED - path traversal in decision argument"; ev decision-refused "traversal"; exit 5 ;;
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
  scope_guard || return 74
  mkdir -p "$ROOT/state/actions" "$ROOT/state/.locks" || return 70
  ACTION_LOCK="$ROOT/state/.locks/action-$ACTION_ID.lock"
  [ -x "$ROOT/scripts/runtime-state.py" ] \
    || { log "witnessed action lock helper is absent"; return 73; }
  python3 "$ROOT/scripts/runtime-state.py" lock-acquire "$ACTION_LOCK" "$$" \
    >/dev/null 2>&1 \
    || { log "action lock contended; refusing duplicate/unlocked dispatch"; return 73; }
  ACTION_LOCK_HELD=1
  scope_guard || { action_unlock || true; return 74; }
  if ! RECURSION_ROOT="$ROOT" python3 "$ROOT/scripts/transition_receipt.py" \
       --root "$ROOT" recover >/dev/null; then
    action_unlock || true
    log "transition receipt recovery failed closed before action claim"
    return 74
  fi
  return 0
}
action_field(){
  python3 -c 'import json,sys
try:
    with open(sys.argv[1],"rb") as source: raw=source.read(2*1024*1024+1)
    if len(raw)>2*1024*1024: raise ValueError("action is too large")
    value=json.loads(raw.decode("utf-8","strict"),parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
    print(value.get(sys.argv[2],"") or "" if isinstance(value,dict) else "")
except (OSError,json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    raise SystemExit(2)' "$ACTION_FILE" "$1" 2>/dev/null
}
action_owned_running(){
  ACTION_EXPECTED_OWNER="$$@$(hostname)" python3 - "$ACTION_FILE" <<'PY' 2>/dev/null
import json,os,sys
try:
    with open(sys.argv[1],"rb") as source: raw=source.read(2*1024*1024+1)
    if len(raw)>2*1024*1024: raise ValueError("action is too large")
    row=json.loads(raw.decode("utf-8","strict"),parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
except (OSError,json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    raise SystemExit(1)
if not isinstance(row,dict):
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
    with open(sys.argv[1],"rb") as source: raw=source.read(2*1024*1024+1)
    if len(raw)>2*1024*1024: raise ValueError("action is too large")
    row=json.loads(raw.decode("utf-8","strict"),parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
except (OSError,json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    raise SystemExit(1)
if not isinstance(row,dict):
    raise SystemExit(1)
try:
    expected_args=json.loads(os.environ['ACTION_EXPECTED_ARGS'],parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
except (json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError,OSError):
    raise SystemExit(1)
if not isinstance(expected_args,list) or any(not isinstance(item,str) for item in expected_args):
    raise SystemExit(1)
expected={
    'id':os.environ['ACTION_EXPECTED_ID'],
    'idempotency_key':os.environ['ACTION_EXPECTED_KEY'],
    'decision_id':os.environ.get('ACTION_EXPECTED_DECISION') or None,
    'instruction_id':os.environ.get('ACTION_EXPECTED_INSTRUCTION') or None,
    'verb':os.environ['ACTION_EXPECTED_VERB'],
    'arguments':expected_args,
    'goal_id':os.environ.get('ACTION_EXPECTED_GOAL') or None,
    'action_payload_sha256':os.environ['ACTION_EXPECTED_PAYLOAD'],
}
raise SystemExit(0 if all(row.get(key)==value for key,value in expected.items()) else 1)
PY
}
action_transition(){ # status evidence
  local status="$1" evidence="${2:-}" rc
  scope_guard || return 74
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
    with open(path,'rb') as src:
        raw=src.read(2*1024*1024+1)
    if len(raw)>2*1024*1024: raise ValueError('action is too large')
    record=json.loads(raw.decode('utf-8','strict'),parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
except FileNotFoundError:
    try:
      arguments=json.loads(os.environ['ACTION_ARGS'],parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
      if not isinstance(arguments,list) or any(not isinstance(a,str) for a in arguments): raise ValueError('action arguments invalid')
    except (json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError,OSError):
      raise SystemExit(2)
    record={
      'schema_version':1,'id':os.environ['ACTION_ID'],
      'decision_id':os.environ.get('ACTION_DECISION') or None,
      'instruction_id':os.environ.get('ACTION_INSTRUCTION') or None,
      'idempotency_key':os.environ['ACTION_KEY'],'verb':os.environ['ACTION_VERB'],
      'arguments':arguments,
      'goal_id':os.environ.get('ACTION_GOAL') or None,'status':'pending',
      'actor':os.environ.get('ACTION_ACTOR') or None,
      'project':os.environ.get('ACTION_PROJECT') or None,
      'decision_source':os.environ.get('ACTION_DECISION_SOURCE') or None,
      'routed_decider':os.environ.get('ACTION_ROUTED_DECIDER') or None,
      'action_payload_sha256':os.environ['ACTION_PAYLOAD_SHA256'],
      'lease_owner':None,'lease_expires':None,'attempts':0,'result_evidence':None,
      'created_at':now,'updated_at':now,
    }
except (OSError,json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    raise SystemExit(2)
if not isinstance(record,dict):
    raise SystemExit(2)
attempts=record.get('attempts')
if type(attempts) is not int or attempts < 0:
    raise SystemExit(2)
if status=='running':
    try:
      lease=int(os.environ.get('RECURSION_ACTION_LEASE_S','3600'),10)
    except (TypeError,ValueError,OverflowError):
      raise SystemExit(2)
    if not 1 <= lease <= 86400: raise SystemExit(2)
    record['attempts']=attempts+1
    record['lease_owner']=os.environ['ACTION_OWNER']
    record['lease_expires']=int(time.time())+lease
elif status in ('pending','succeeded','failed','cancelled'):
    record['lease_owner']=None; record['lease_expires']=None
record['status']=status
record['result_evidence']=os.environ.get('ACTION_EVIDENCE') or None
record['updated_at']=now
event={'schema_version':1,'ts':now,'action_id':record['id'],'status':status,
       'attempt':record['attempts'],'idempotency_key':record['idempotency_key'],
       'evidence':record['result_evidence']}
try:
    commit_transition(__import__('pathlib').Path(sys.argv[3]).parent,
                      [json_mutation(__import__('pathlib').Path(path),record)],event,
                      journal='state/action-events.jsonl')
except (OSError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    raise SystemExit(2)
PY
  rc=$?
  [ "$rc" -eq 0 ] || log "failed durable action transition status=$status rc=$rc"
  return "$rc"
}
release_consumed_instruction(){
  [ "${RECURSION_QUEUE_ACTUATION:-0}" = 1 ] && [ -n "$INSTRUCTION_ID" ] || return 0
  scope_guard || return 74
  if ! RECURSION_ROOT="$ROOT" bash scripts/intake.sh release "$INSTRUCTION_ID" "$ACTION_ID"; then
    log "action $ACTION_ID could not reopen instruction $INSTRUCTION_ID"
    return 74
  fi
}
reconcile_terminal_instruction(){ # succeeded|failed
  local disposition="$1"
  [ "${RECURSION_QUEUE_ACTUATION:-0}" = 1 ] && [ -n "$INSTRUCTION_ID" ] || return 0
  scope_guard || return 74
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
    scope_guard || { action_transition failed "decision scope changed before instruction consume" || true
      action_unlock; trap - EXIT; exit 74; }
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
        raw=action_path.read_bytes()
        if len(raw)>2*1024*1024: raise ValueError('action is too large')
        action=json.loads(raw.decode('utf-8','strict'),parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
    except (OSError,json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
        continue
    if not isinstance(action,dict):
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
try:
    with open(sys.argv[1],'rb') as source: raw=source.read(2*1024*1024+1)
    if len(raw)>2*1024*1024: raise ValueError('project config is too large')
    value=json.loads(raw.decode('utf-8','strict'),parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
    print(value.get('pilot_id','') if isinstance(value,dict) else '')
except (OSError,json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    raise SystemExit(2)
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
try:
    with open(sys.argv[1],'rb') as source: raw=source.read(2*1024*1024+1)
    if len(raw)>2*1024*1024: raise ValueError('project config is too large')
    value=json.loads(raw.decode('utf-8','strict'),parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
    print(value.get('pilot_id','') if isinstance(value,dict) else '')
except (OSError,json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    raise SystemExit(2)
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

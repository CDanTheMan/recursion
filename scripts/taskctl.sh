#!/usr/bin/env bash
# taskctl.sh — the ONE writer for task state, the event log, and escalation identity.
#
# WHY THIS EXISTS. Task status lived in state/tasks/*.md (edited by ad-hoc `sed` from two
# scripts), queue direction in state/roadmaps/, blockers in state/INBOX.md, and a render in
# state/BOARD.md — four stores, one of which called itself "the single source of truth".
# Two concrete failures came out of that:
#
#   1. NO LEASE. A killed worker left `status: running` forever. It happened (the 0x68 arm
#      auto-retried, the orphan had to be found and killed by hand) and nothing detected it.
#   2. NO ESCALATION IDENTITY. run.sh appended whatever the brief emitted, with no id and no
#      dedup, while the heartbeat signalled `brief` for as long as the INBOX had an unanswered
#      item. The same ask was appended FOUR times in nine hours (21:15, 00:15, 03:15, 06:15).
#      A queue that regenerates its own contents cannot be worked down.
#
# This does not replace the task files — they are what the proven executor consumes, and
# swapping the store while moving authority would risk the working machinery to fix a layer
# above it. It makes them CANONICAL and gives them the missing properties: exactly one status
# per task, an append-only event log, leases that expire, and escalations with identity.
#
# All state writes go through here so there is one place that takes the lock and one place
# that emits events.
#
#   taskctl.sh start <id> [owner]      lease the task and mark it running
#   taskctl.sh heartbeat <id>          extend the lease
#   taskctl.sh finish <id> <status> [note]
#   taskctl.sh block <id> <reason>     mark blocked (see esc-record for the escalation)
#   taskctl.sh cas <id> <from> <to> <reason>  Phase 6 compare-and-swap transition
#   taskctl.sh get <id> [field]        canonical status, or one field
#   taskctl.sh reap                    expire dead leases -> stale + event (safe, idempotent)
#   taskctl.sh event <kind> <task> <detail...>
#   taskctl.sh esc-record <key> <title> [workstream] [pointer]
#                                      -> "NEW <id>" | "DUP <id> <count>"
#   taskctl.sh esc-resolve <id> [note]
#   taskctl.sh esc-list [open|all]
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT" 2>/dev/null || { echo "taskctl: no RECURSION_ROOT" >&2; exit 3; }

TASKDIR="state/tasks"
EVENTS="state/events.jsonl"
ESCIDX="state/escalations.tsv"
LOCKDIR="state/.locks"
LEASE_TTL="${RECURSION_LEASE_TTL_S:-5400}"   # 90 min; a GSC arm run is ~60 min

mkdir -p "$TASKDIR" "$LOCKDIR" "$(dirname "$EVENTS")" 2>/dev/null

# --- lock: mkdir is atomic. Bounded spin, then proceed — a stuck lock must not wedge the
# loop, and every writer here is append-or-rewrite-single-file, so worst case is interleaving,
# never corruption of a half-written record. ------------------------------------------------
_LOCK_HELD=0
_lock(){
  local i=0 limit="${RECURSION_LOCK_ATTEMPTS:-100}" delay="${RECURSION_LOCK_DELAY_S:-0.1}"
  while :; do
    if [ ! -d "$LOCKDIR/runtime-state.lock" ] && mkdir "$LOCKDIR/taskctl.lock" 2>/dev/null; then
      _LOCK_HELD=1
      return 0
    fi
    i=$((i+1))
    if [ "$i" -ge "$limit" ]; then
      echo "taskctl: state lock is contended; refusing to write unlocked" >&2
      return 73
    fi
    sleep "$delay"
  done
}
_unlock(){
  [ "$_LOCK_HELD" = 1 ] || return 0
  rmdir "$LOCKDIR/taskctl.lock" 2>/dev/null || return 74
  _LOCK_HELD=0
}

_now(){ date -u +%FT%TZ; }
_epoch(){ date +%s; }
# Resolve a task to a file. work.sh accepts an id OR an arbitrary task-file path, so taskctl
# must too — otherwise a path-invoked task looks like "no such task" and the caller silently
# does nothing. (Caught by work.selftest.sh, which invokes work.sh with an absolute path.)
# TASKCTL_FILE lets a caller that already resolved the file say so explicitly.
_taskfile(){
  if   [ -n "${TASKCTL_FILE:-}" ] && [ -f "$TASKCTL_FILE" ]; then printf '%s' "$TASKCTL_FILE"
  elif [ -f "$1" ];                                          then printf '%s' "$1"
  else printf '%s/%s.md' "$TASKDIR" "$1"; fi
}
_field(){ sed -n "s/^$2: *//p" "$1" 2>/dev/null | head -1 | tr -d '\r'; }

# JSON string escape — a goal line containing a quote or backslash must not produce a
# malformed event. jq is not guaranteed on the box, so do it here.
_esc(){ printf '%s' "$1" | python3 -c 'import json,sys;sys.stdout.write(json.dumps(sys.stdin.read())[1:-1])' 2>/dev/null \
        || printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n'; }

# Apply a whole transition to a same-directory temporary copy, fsync it, then rename it over
# the projection. Passing the temp path as Python's first argument is intentional: a killed or
# failed writer can damage only the temp file, never the canonical record.
_set_fields(){ # file key value [key value ...]
  local f="$1" d b tmp rc; shift
  [ $(( $# % 2 )) -eq 0 ] || { echo "taskctl: internal odd field list" >&2; return 2; }
  d="$(dirname "$f")"; b="$(basename "$f")"
  tmp="$(mktemp "$d/.${b}.tmp.XXXXXX")" || return 70
  if ! cp -p -- "$f" "$tmp"; then rm -f -- "$tmp"; return 70; fi
  python3 - "$tmp" "$f" "$@" <<'PY'
import os,sys
tmp=sys.argv[1]
pairs=sys.argv[3:]
lines=open(tmp,encoding='utf-8',errors='surrogateescape').read().split('\n')
for n in range(0,len(pairs),2):
    key,value=pairs[n],pairs[n+1]
    hit=False
    for i,line in enumerate(lines):
        if not hit and line.startswith(key+': '):
            lines[i]=key+': '+value; hit=True
    if not hit:
        for i,line in enumerate(lines):
            if line.strip()=='':
                lines.insert(i,key+': '+value); hit=True; break
    if not hit:
        lines.append(key+': '+value)
with open(tmp,'w',encoding='utf-8',errors='surrogateescape',newline='\n') as out:
    out.write('\n'.join(lines)); out.flush(); os.fsync(out.fileno())
PY
  rc=$?
  if [ "$rc" -ne 0 ]; then rm -f -- "$tmp"; return "$rc"; fi
  if ! mv -f -- "$tmp" "$f"; then rm -f -- "$tmp"; return 71; fi
  python3 - "$d" <<'PY' >/dev/null 2>&1 || return 72
import os,sys
fd=os.open(sys.argv[1],os.O_RDONLY)
try: os.fsync(fd)
finally: os.close(fd)
PY
}

_set_field(){ _set_fields "$@"; }

_canonical_task(){
  case "$1" in "$ROOT/$TASKDIR/"*|"$TASKDIR/"*) return 0 ;; *) return 1 ;; esac
}

_validate_task_start(){
  local f="$1" gid gf deps dep df st
  # Temporary/external task files remain supported for the existing gate self-test. Canonical
  # tasks are schema-enforced once a goal registry exists.
  _canonical_task "$f" || return 0
  { [ -f schemas/control-plane/v1/schema.json ] || [ -d state/goals ]; } || return 0
  gid="$(_field "$f" goal_id)"
  printf '%s' "$gid" | grep -qE '^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$' \
    || { echo "taskctl: task requires a canonical goal_id" >&2; return 6; }
  gf="state/goals/$gid.md"
  [ -f "$gf" ] || { echo "taskctl: parent goal does not exist: $gid" >&2; return 6; }
  [ "$(_field "$gf" id)" = "$gid" ] \
    || { echo "taskctl: goal file/id mismatch: $gid" >&2; return 6; }
  [ "$(_field "$gf" status)" = active ] \
    || { echo "taskctl: parent goal is not active: $gid" >&2; return 6; }
  deps="$(_field "$f" dependencies)"; deps="${deps//,/ }"
  for dep in $deps; do
    printf '%s' "$dep" | grep -qE '^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$' \
      || { echo "taskctl: invalid dependency id: $dep" >&2; return 6; }
    df="$TASKDIR/$dep.md"; [ -f "$df" ] \
      || { echo "taskctl: dependency does not exist: $dep" >&2; return 6; }
    st="$(_field "$df" status)"; [ "$st" = passed ] \
      || { echo "taskctl: dependency has not passed: $dep ($st)" >&2; return 6; }
  done
}

_atomic_esc(){ # mode [arguments...]
  local mode="$1" d b tmp rc; shift
  d="$(dirname "$ESCIDX")"; b="$(basename "$ESCIDX")"
  tmp="$(mktemp "$d/.${b}.tmp.XXXXXX")" || return 70
  if [ -f "$ESCIDX" ]; then cp -p -- "$ESCIDX" "$tmp" || { rm -f -- "$tmp"; return 70; }
  else printf '#id\tkey\tstatus\tfirst_seen\tlast_seen\tcount\tworkstream\tpointer\ttitle\n' > "$tmp"; fi
  python3 - "$tmp" "$mode" "$@" <<'PY'
import os,sys
path,mode=sys.argv[1:3]
args=sys.argv[3:]
lines=open(path,encoding='utf-8').read().splitlines()
result=''
if mode=='init':
    pass
elif mode=='bump':
    eid,now=args; hit=False
    for i,line in enumerate(lines):
        cells=line.split('\t')
        if len(cells)>=9 and cells[0]==eid:
            cells[4]=now; cells[5]=str(int(cells[5])+1); lines[i]='\t'.join(cells)
            result=cells[5]; hit=True; break
    if not hit: raise SystemExit(2)
elif mode=='add':
    lines.append('\t'.join(args))
elif mode=='resolve':
    eid=args[0]; hit=False
    for i,line in enumerate(lines):
        cells=line.split('\t')
        if len(cells)>=9 and cells[0]==eid and cells[2]=='open':
            cells[2]='resolved'; lines[i]='\t'.join(cells); hit=True; break
    if not hit: raise SystemExit(2)
else:
    raise SystemExit(2)
with open(path,'w',encoding='utf-8',newline='\n') as out:
    out.write('\n'.join(lines)+'\n'); out.flush(); os.fsync(out.fileno())
if result: print(result)
PY
  rc=$?
  if [ "$rc" -ne 0 ]; then rm -f -- "$tmp"; return "$rc"; fi
  if ! mv -f -- "$tmp" "$ESCIDX"; then rm -f -- "$tmp"; return 71; fi
  python3 - "$d" <<'PY' >/dev/null 2>&1 || return 72
import os,sys
fd=os.open(sys.argv[1],os.O_RDONLY)
try: os.fsync(fd)
finally: os.close(fd)
PY
}

emit_event(){ # kind task detail
  local kind="$1" task="${2:-}" detail="${3:-}" f proj goal line
  f="$(_taskfile "$task")"
  proj=""; goal=""
  if [ -f "$f" ]; then proj="$(_field "$f" project)"; [ -z "$proj" ] && proj="$(_field "$f" workstream)"; goal="$(_field "$f" goal_id)"; fi
  line="$(printf '{"schema_version":1,"ts":"%s","event":"%s","task":"%s","project":"%s","goal":"%s","pid":%s,"detail":"%s"}' \
    "$(_now)" "$(_esc "$kind")" "$(_esc "$task")" "$(_esc "$proj")" "$(_esc "$goal")" "$$" "$(_esc "$detail")")"
  EVENT_LINE="$line" python3 - "$EVENTS" <<'PY'
import os,sys
path=sys.argv[1]
fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
try:
    os.write(fd,(os.environ['EVENT_LINE']+'\n').encode())
    os.fsync(fd)
finally:
    os.close(fd)
PY
}

cmd="${1:-}"; shift 2>/dev/null || true

case "$cmd" in

start)
  ID="${1:?usage: taskctl start <id> [owner]}"; OWNER="${2:-$$@$(hostname)}"
  F="$(_taskfile "$ID")"; [ -f "$F" ] || { echo "taskctl: no such task: $ID" >&2; exit 2; }
  _validate_task_start "$F" || exit $?
  _lock || exit $?
  cur="$(_field "$F" status)"
  # Refuse to steal a LIVE lease. A second worker on one task is the failure that produced a
  # redundant hour-long arm run; the reaper — not a racing writer — is what frees a dead one.
  exp="$(_field "$F" lease_expires)"
  if [ "$cur" = "running" ] && [ -n "$exp" ] && [ "$exp" -gt "$(_epoch)" ] 2>/dev/null; then
    _unlock; echo "taskctl: $ID already leased by $(_field "$F" lease_owner) until $exp" >&2; exit 4
  fi
  case "$cur" in
    ready|queued|stale) : ;;
    *) _unlock; echo "taskctl: $ID is status=$cur, not dispatchable" >&2; exit 4 ;;
  esac
  att="$(_field "$F" attempts)"; att="$(( ${att:-0} + 1 ))"
  _set_fields "$F" status running lease_owner "$OWNER" \
    lease_expires "$(( $(_epoch) + LEASE_TTL ))" attempts "$att" started_at "$(_now)" \
    || { rc=$?; _unlock; exit "$rc"; }
  emit_event start "$ID" "owner=$OWNER attempt=$att" || { rc=$?; _unlock; exit "$rc"; }
  _unlock; echo "started $ID (attempt $att)" ;;

heartbeat)
  ID="${1:?usage: taskctl heartbeat <id>}"; F="$(_taskfile "$ID")"; [ -f "$F" ] || exit 2
  _lock || exit $?
  _set_fields "$F" lease_expires "$(( $(_epoch) + LEASE_TTL ))" \
    || { rc=$?; _unlock; exit "$rc"; }
  emit_event heartbeat "$ID" "" || { rc=$?; _unlock; exit "$rc"; }
  _unlock ;;

finish)
  ID="${1:?usage: taskctl finish <id> <status> [note]}"; ST="${2:?status}"; NOTE="${3:-}"
  F="$(_taskfile "$ID")"; [ -f "$F" ] || exit 2
  _lock || exit $?
  if [ -n "$NOTE" ]; then
    _set_fields "$F" status "$ST" lease_expires 0 finished_at "$(_now)" evidence "$NOTE"
  else
    _set_fields "$F" status "$ST" lease_expires 0 finished_at "$(_now)"
  fi || { rc=$?; _unlock; exit "$rc"; }
  emit_event finish "$ID" "status=$ST $NOTE" || { rc=$?; _unlock; exit "$rc"; }
  _unlock; echo "finished $ID -> $ST" ;;

block)
  ID="${1:?usage: taskctl block <id> <reason>}"; REASON="${2:-blocked}"
  F="$(_taskfile "$ID")"; [ -f "$F" ] || exit 2
  _lock || exit $?
  _set_fields "$F" status blocked lease_expires 0 blocker_actor "${BLOCKER_ACTOR:-human}" \
    || { rc=$?; _unlock; exit "$rc"; }
  emit_event block "$ID" "$REASON" || { rc=$?; _unlock; exit "$rc"; }
  _unlock; echo "blocked $ID" ;;

cas)
  ID="${1:?usage: taskctl cas <id> <from> <to> <reason>}"
  FROM="${2:?from}"; TO="${3:?to}"; REASON="${4:?reason}"
  F="$(_taskfile "$ID")"; [ -f "$F" ] || { echo "taskctl: no such task: $ID" >&2; exit 2; }
  case "$FROM:$TO" in
    proposed:ready|failed:ready|stale:ready|running:stale|leased:stale|ready:blocked|queued:blocked) : ;;
    *) echo "taskctl: refused transition $FROM -> $TO" >&2; exit 6 ;;
  esac
  _lock || exit $?
  CUR="$(_field "$F" status)"
  [ "$CUR" = "$FROM" ] || { _unlock; echo "taskctl: CAS expected $FROM, found $CUR" >&2; exit 73; }
  VER="$(_field "$F" version)"; VER="$(( ${VER:-1} + 1 ))"
  _set_fields "$F" status "$TO" version "$VER" lease_expires 0 transition_reason "$REASON" \
    transition_at "$(_now)" || { rc=$?; _unlock; exit "$rc"; }
  emit_event task-transition "$ID" "from=$FROM to=$TO reason=$REASON version=$VER" \
    || { rc=$?; _unlock; exit "$rc"; }
  _unlock; echo "transitioned $ID $FROM -> $TO" ;;

get)
  ID="${1:?usage: taskctl get <id> [field]}"; FLD="${2:-status}"
  F="$(_taskfile "$ID")"; [ -f "$F" ] || exit 2
  _field "$F" "$FLD" ;;

reap)
  # A task is STALE when it claims to be running, its lease has expired, and nothing is
  # holding it. That is the "no board row may remain running after its worker exits" rule,
  # made mechanical. Idempotent: a task already reaped is not reaped twice.
  now="$(_epoch)"; n=0
  _lock || exit $?
  for F in "$TASKDIR"/*.md; do
    [ -f "$F" ] || continue
    [ "$(_field "$F" status)" = "running" ] || continue
    exp="$(_field "$F" lease_expires)"; [ -n "$exp" ] || continue
    case "$exp" in (*[!0-9]*) continue ;; esac
    [ "$exp" -gt "$now" ] && continue
    ID="$(_field "$F" id)"; [ -n "$ID" ] || ID="$(basename "$F" .md)"
    _set_fields "$F" status stale lease_expires 0 \
      || { rc=$?; _unlock; exit "$rc"; }
    emit_event stale "$ID" "lease expired at $exp (owner $(_field "$F" lease_owner)); worker gone" \
      || { rc=$?; _unlock; exit "$rc"; }
    echo "reaped $ID (stale lease)"
    n=$((n+1))
  done
  _unlock
  [ "$n" -eq 0 ] && echo "reap: nothing stale"
  exit 0 ;;

event)
  K="${1:?usage: taskctl event <kind> <task> [detail]}"; T="${2:-}"; D="${3:-}"
  _lock || exit $?
  emit_event "$K" "$T" "$D" || { rc=$?; _unlock; exit "$rc"; }
  _unlock ;;

# --- escalation identity ---------------------------------------------------------------
# Index columns: id  key  status  first_seen  last_seen  count  workstream  pointer  title
esc-record)
  KEY="${1:?usage: taskctl esc-record <key> <title> [workstream] [pointer]}"
  TITLE="${2:-}"; WS="${3:-}"; PTR="${4:-}"
  _lock || exit $?
  _atomic_esc init || { rc=$?; _unlock; exit "$rc"; }
  # An OPEN escalation with this key already exists -> it is the SAME ask. Bump and report
  # DUP; the caller must not append or re-notify. This is the fix for the four-times bug.
  existing="$(awk -F'\t' -v k="$KEY" '$2==k && $3=="open" {print $1; exit}' "$ESCIDX")"
  if [ -n "$existing" ]; then
    cnt="$(_atomic_esc bump "$existing" "$(_now)")" \
      || { rc=$?; _unlock; exit "$rc"; }
    _unlock; echo "DUP $existing ${cnt:-?}"; exit 0
  fi
  n="$(awk -F'\t' '$1 ~ /^esc-/ {c++} END{print c+0}' "$ESCIDX")"
  EID="$(printf 'esc-%04d' "$(( n + 1 ))")"
  SEEN="$(_now)"
  _atomic_esc add "$EID" "$KEY" open "$SEEN" "$SEEN" 1 "$WS" "$PTR" "$TITLE" \
    || { rc=$?; _unlock; exit "$rc"; }
  emit_event escalation-open "" "$EID $WS $TITLE" || { rc=$?; _unlock; exit "$rc"; }
  _unlock; echo "NEW $EID" ;;

esc-resolve)
  EID="${1:?usage: taskctl esc-resolve <id> [note]}"; NOTE="${2:-}"
  _lock || exit $?
  [ -f "$ESCIDX" ] || { _unlock; echo "taskctl: no escalation index" >&2; exit 2; }
  _atomic_esc resolve "$EID"; rc=$?
  [ "$rc" -eq 0 ] && emit_event escalation-resolve "" "$EID $NOTE" || rc=$?
  _unlock
  [ "$rc" -eq 0 ] && echo "resolved $EID" || { echo "taskctl: no OPEN escalation $EID" >&2; exit 2; }
  ;;

esc-list)
  W="${1:-open}"
  [ -f "$ESCIDX" ] || { echo "(no escalations)"; exit 0; }
  if [ "$W" = "all" ]; then awk -F'\t' 'NR>1 && NF>=9' "$ESCIDX"
  else awk -F'\t' 'NR>1 && $3=="open"' "$ESCIDX"; fi ;;

*) sed -n '/^#   taskctl.sh/,/^set -uo/p' "$0" | sed '$d'; exit 2 ;;
esac

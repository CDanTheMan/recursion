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
_lock(){ local i=0; while ! mkdir "$LOCKDIR/taskctl.lock" 2>/dev/null; do i=$((i+1)); [ "$i" -ge 100 ] && return 0; sleep 0.1; done; }
_unlock(){ rmdir "$LOCKDIR/taskctl.lock" 2>/dev/null || true; }

_now(){ date -u +%FT%TZ; }
_epoch(){ date +%s; }
_taskfile(){ printf '%s/%s.md' "$TASKDIR" "$1"; }
_field(){ sed -n "s/^$2: *//p" "$1" 2>/dev/null | head -1 | tr -d '\r'; }

# JSON string escape — a goal line containing a quote or backslash must not produce a
# malformed event. jq is not guaranteed on the box, so do it here.
_esc(){ printf '%s' "$1" | python3 -c 'import json,sys;sys.stdout.write(json.dumps(sys.stdin.read())[1:-1])' 2>/dev/null \
        || printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n'; }

# set-or-append a `key: value` field, preserving the rest of the file byte-for-byte.
_set_field(){ # $1=file $2=key $3=value
  local f="$1" k="$2" v="$3"
  if grep -q "^$k: " "$f" 2>/dev/null; then
    python3 - "$f" "$k" "$v" <<'PY' 2>/dev/null && return 0
import sys,io
f,k,v=sys.argv[1],sys.argv[2],sys.argv[3]
lines=open(f,encoding='utf-8',errors='surrogateescape').read().split('\n')
done=False
for i,l in enumerate(lines):
    if not done and l.startswith(k+': '):
        lines[i]=f'{k}: {v}'; done=True
open(f,'w',encoding='utf-8',errors='surrogateescape',newline='\n').write('\n'.join(lines))
PY
    sed -i "0,/^$k: .*/s##$k: $v#" "$f" 2>/dev/null
  else
    # insert before the first blank line (end of the header block), else append
    python3 - "$f" "$k" "$v" <<'PY' 2>/dev/null && return 0
import sys
f,k,v=sys.argv[1],sys.argv[2],sys.argv[3]
s=open(f,encoding='utf-8',errors='surrogateescape').read().split('\n')
for i,l in enumerate(s):
    if l.strip()=='':
        s.insert(i,f'{k}: {v}'); break
else:
    s.append(f'{k}: {v}')
open(f,'w',encoding='utf-8',errors='surrogateescape',newline='\n').write('\n'.join(s))
PY
    printf '%s: %s\n' "$k" "$v" >> "$f"
  fi
}

emit_event(){ # kind task detail
  local kind="$1" task="${2:-}" detail="${3:-}" f proj goal
  f="$(_taskfile "$task")"
  proj=""; goal=""
  if [ -f "$f" ]; then proj="$(_field "$f" project)"; [ -z "$proj" ] && proj="$(_field "$f" workstream)"; goal="$(_field "$f" goal_id)"; fi
  printf '{"ts":"%s","event":"%s","task":"%s","project":"%s","goal":"%s","pid":%s,"detail":"%s"}\n' \
    "$(_now)" "$(_esc "$kind")" "$(_esc "$task")" "$(_esc "$proj")" "$(_esc "$goal")" "$$" "$(_esc "$detail")" >> "$EVENTS"
}

cmd="${1:-}"; shift 2>/dev/null || true

case "$cmd" in

start)
  ID="${1:?usage: taskctl start <id> [owner]}"; OWNER="${2:-$$@$(hostname)}"
  F="$(_taskfile "$ID")"; [ -f "$F" ] || { echo "taskctl: no such task: $ID" >&2; exit 2; }
  _lock
  cur="$(_field "$F" status)"
  # Refuse to steal a LIVE lease. A second worker on one task is the failure that produced a
  # redundant hour-long arm run; the reaper — not a racing writer — is what frees a dead one.
  exp="$(_field "$F" lease_expires)"
  if [ "$cur" = "running" ] && [ -n "$exp" ] && [ "$exp" -gt "$(_epoch)" ] 2>/dev/null; then
    _unlock; echo "taskctl: $ID already leased by $(_field "$F" lease_owner) until $exp" >&2; exit 4
  fi
  att="$(_field "$F" attempts)"; att="$(( ${att:-0} + 1 ))"
  _set_field "$F" status running
  _set_field "$F" lease_owner "$OWNER"
  _set_field "$F" lease_expires "$(( $(_epoch) + LEASE_TTL ))"
  _set_field "$F" attempts "$att"
  _set_field "$F" started_at "$(_now)"
  emit_event start "$ID" "owner=$OWNER attempt=$att"
  _unlock; echo "started $ID (attempt $att)" ;;

heartbeat)
  ID="${1:?usage: taskctl heartbeat <id>}"; F="$(_taskfile "$ID")"; [ -f "$F" ] || exit 2
  _lock; _set_field "$F" lease_expires "$(( $(_epoch) + LEASE_TTL ))"; emit_event heartbeat "$ID" ""; _unlock ;;

finish)
  ID="${1:?usage: taskctl finish <id> <status> [note]}"; ST="${2:?status}"; NOTE="${3:-}"
  F="$(_taskfile "$ID")"; [ -f "$F" ] || exit 2
  _lock
  _set_field "$F" status "$ST"
  _set_field "$F" lease_expires 0
  _set_field "$F" finished_at "$(_now)"
  [ -n "$NOTE" ] && _set_field "$F" evidence "$NOTE"
  emit_event finish "$ID" "status=$ST $NOTE"
  _unlock; echo "finished $ID -> $ST" ;;

block)
  ID="${1:?usage: taskctl block <id> <reason>}"; REASON="${2:-blocked}"
  F="$(_taskfile "$ID")"; [ -f "$F" ] || exit 2
  _lock
  _set_field "$F" status blocked
  _set_field "$F" lease_expires 0
  _set_field "$F" blocker_actor "${BLOCKER_ACTOR:-human}"
  emit_event block "$ID" "$REASON"
  _unlock; echo "blocked $ID" ;;

get)
  ID="${1:?usage: taskctl get <id> [field]}"; FLD="${2:-status}"
  F="$(_taskfile "$ID")"; [ -f "$F" ] || exit 2
  _field "$F" "$FLD" ;;

reap)
  # A task is STALE when it claims to be running, its lease has expired, and nothing is
  # holding it. That is the "no board row may remain running after its worker exits" rule,
  # made mechanical. Idempotent: a task already reaped is not reaped twice.
  now="$(_epoch)"; n=0
  _lock
  for F in "$TASKDIR"/*.md; do
    [ -f "$F" ] || continue
    [ "$(_field "$F" status)" = "running" ] || continue
    exp="$(_field "$F" lease_expires)"; [ -n "$exp" ] || continue
    case "$exp" in (*[!0-9]*) continue ;; esac
    [ "$exp" -gt "$now" ] && continue
    ID="$(_field "$F" id)"; [ -n "$ID" ] || ID="$(basename "$F" .md)"
    _set_field "$F" status stale
    _set_field "$F" lease_expires 0
    emit_event stale "$ID" "lease expired at $exp (owner $(_field "$F" lease_owner)); worker gone"
    echo "reaped $ID (stale lease)"
    n=$((n+1))
  done
  _unlock
  [ "$n" -eq 0 ] && echo "reap: nothing stale"
  exit 0 ;;

event)
  K="${1:?usage: taskctl event <kind> <task> [detail]}"; T="${2:-}"; D="${3:-}"
  _lock; emit_event "$K" "$T" "$D"; _unlock ;;

# --- escalation identity ---------------------------------------------------------------
# Index columns: id  key  status  first_seen  last_seen  count  workstream  pointer  title
esc-record)
  KEY="${1:?usage: taskctl esc-record <key> <title> [workstream] [pointer]}"
  TITLE="${2:-}"; WS="${3:-}"; PTR="${4:-}"
  _lock
  [ -f "$ESCIDX" ] || printf '#id\tkey\tstatus\tfirst_seen\tlast_seen\tcount\tworkstream\tpointer\ttitle\n' > "$ESCIDX"
  # An OPEN escalation with this key already exists -> it is the SAME ask. Bump and report
  # DUP; the caller must not append or re-notify. This is the fix for the four-times bug.
  existing="$(awk -F'\t' -v k="$KEY" '$2==k && $3=="open" {print $1; exit}' "$ESCIDX")"
  if [ -n "$existing" ]; then
    python3 - "$ESCIDX" "$existing" "$(_now)" <<'PY'
import sys
idx,eid,now=sys.argv[1],sys.argv[2],sys.argv[3]
out=[]
for line in open(idx,encoding='utf-8').read().split('\n'):
    c=line.split('\t')
    if len(c)>=9 and c[0]==eid:
        c[4]=now; c[5]=str(int(c[5])+1); line='\t'.join(c)
    out.append(line)
open(idx,'w',encoding='utf-8',newline='\n').write('\n'.join(out))
PY
    cnt="$(awk -F'\t' -v e="$existing" '$1==e {print $6; exit}' "$ESCIDX")"
    _unlock; echo "DUP $existing ${cnt:-?}"; exit 0
  fi
  n="$(awk -F'\t' '$1 ~ /^esc-/ {c++} END{print c+0}' "$ESCIDX")"
  EID="$(printf 'esc-%04d' "$(( n + 1 ))")"
  printf '%s\t%s\topen\t%s\t%s\t1\t%s\t%s\t%s\n' \
    "$EID" "$KEY" "$(_now)" "$(_now)" "$WS" "$PTR" "$TITLE" >> "$ESCIDX"
  emit_event escalation-open "" "$EID $WS $TITLE"
  _unlock; echo "NEW $EID" ;;

esc-resolve)
  EID="${1:?usage: taskctl esc-resolve <id> [note]}"; NOTE="${2:-}"
  _lock
  [ -f "$ESCIDX" ] || { _unlock; echo "taskctl: no escalation index" >&2; exit 2; }
  python3 - "$ESCIDX" "$EID" <<'PY'
import sys
idx,eid=sys.argv[1],sys.argv[2]
out=[];hit=False
for line in open(idx,encoding='utf-8').read().split('\n'):
    c=line.split('\t')
    if len(c)>=9 and c[0]==eid and c[2]=='open':
        c[2]='resolved'; line='\t'.join(c); hit=True
    out.append(line)
open(idx,'w',encoding='utf-8',newline='\n').write('\n'.join(out))
sys.exit(0 if hit else 1)
PY
  rc=$?
  [ "$rc" -eq 0 ] && emit_event escalation-resolve "" "$EID $NOTE"
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

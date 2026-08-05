#!/usr/bin/env bash
# conduct.sh — the PARALLEL continuation engine (parallel-loops.md). Where drain.sh runs queued
# tasks strictly one at a time, conduct.sh runs up to N at once — at most ONE build per workstream
# (work.sh's per-workstream lock is the backstop), so chiron / gsc / future workstreams build
# concurrently. Same bounds as drain so it can never run away or grind the Max quota.
#
# Bounds (env, human-set):
#   RECURSION_CONDUCT_CONCURRENCY  max concurrent builds        (default 2)
#   RECURSION_DRAIN_MAX            max tasks total this run      (default 6)
#   RECURSION_DRAIN_FAILSTOP       stop launching after N non-passes (default 2; total, not consec.)
#   RECURSION_DRAIN_DEADLINE_MIN   wall-clock cap in minutes     (default 360)
#   RECURSION_CONDUCT_POLL_S       poll interval seconds         (default 5)
#   state/PAUSE                    hard stop (checked every poll; work.sh checks it too)
#
#   conduct.sh          drain the queue IN PARALLEL under the bounds above
set -uo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"; cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a
CONC="${RECURSION_CONDUCT_CONCURRENCY:-2}"
MAX="${RECURSION_DRAIN_MAX:-6}"
FAILSTOP="${RECURSION_DRAIN_FAILSTOP:-2}"
DEADLINE="${RECURSION_DRAIN_DEADLINE_MIN:-360}"
POLL="${RECURSION_CONDUCT_POLL_S:-5}"
LOCK="$ROOT/state/.conduct.lock"
LOG="$ROOT/loop/logs/$(date +%F)-conduct.log"
log(){ echo "[$(date -Is)] conduct: $*" | tee -a "$LOG"; }

# single-instance, and never double-drive the queue against a serial drainer.
if ! mkdir "$LOCK" 2>/dev/null; then log "another conductor holds $LOCK — exiting"; exit 0; fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT
if [ -d "$ROOT/state/.drain.lock" ]; then log "a serial drain holds .drain.lock — exiting"; exit 0; fi

START="$(date +%s)"; launched=0; done_n=0; nonpass=0
declare -A PID2ID PID2WS RUNNING_WS

status_of(){ sed -n 's/^status: *//p' "state/tasks/$1.md" 2>/dev/null | head -1 | tr -d '\r'; }

# next queued task whose workstream is NOT already running under this conductor.
# emits "<id>\t<ws>" and returns 0, or returns 1 when nothing is launchable.
next_launchable(){
  local f id ws
  for f in $(grep -l '^status: *queued' state/tasks/*.md 2>/dev/null | sort); do
    id="$(sed -n 's/^id: *//p' "$f" | head -1 | tr -d '\r')"
    ws="$(sed -n 's/^workstream: *//p' "$f" | head -1 | tr -d '\r')"; ws="${ws:-none}"
    [ -n "${RUNNING_WS[$ws]:-}" ] && continue
    printf '%s\t%s\n' "$id" "$ws"; return 0
  done
  return 1
}

# reap finished children: update counters, free the workstream slot.
reap(){
  local pid id ws st
  for pid in "${!PID2ID[@]}"; do
    if ! kill -0 "$pid" 2>/dev/null; then
      id="${PID2ID[$pid]}"; ws="${PID2WS[$pid]}"
      wait "$pid" 2>/dev/null || true
      st="$(status_of "$id")"
      log "$id ($ws) -> ${st:-?}"
      [ "$st" = "passed" ] || nonpass=$((nonpass+1))
      done_n=$((done_n+1))
      unset "PID2ID[$pid]" "PID2WS[$pid]" "RUNNING_WS[$ws]"
    fi
  done
}

log "start (concurrency=$CONC max=$MAX failstop=$FAILSTOP deadline=${DEADLINE}m poll=${POLL}s)"
while :; do
  [ -f "$ROOT/state/PAUSE" ] && { log "PAUSED — stop launching"; break; }
  emin=$(( ( $(date +%s) - START ) / 60 ))
  [ "$emin" -ge "$DEADLINE" ] && { log "deadline reached (${emin}m) — stop launching"; break; }
  [ "$nonpass" -ge "$FAILSTOP" ] && { log "$FAILSTOP non-passes — stop launching (approach not landing)"; break; }

  # launch while we have a free slot, budget left, and an idle workstream with queued work.
  while [ "${#PID2ID[@]}" -lt "$CONC" ] && [ "$launched" -lt "$MAX" ]; do
    line="$(next_launchable)" || break
    id="${line%%$'\t'*}"; ws="${line##*$'\t'}"
    log "launch $id (ws=$ws) [#$((launched+1))/$MAX, running $(( ${#PID2ID[@]} + 1 ))/$CONC]"
    nohup bash scripts/work.sh "$id" >>"$LOG" 2>&1 &
    pid=$!
    PID2ID[$pid]="$id"; PID2WS[$pid]="$ws"; RUNNING_WS[$ws]=1
    launched=$((launched+1))
  done

  # nothing running and nothing launchable -> the queue is drained.
  [ "${#PID2ID[@]}" -eq 0 ] && { log "queue empty / no idle workstream with work — done ($done_n ran)"; break; }

  sleep "$POLL"
  reap
done

# let in-flight builds finish (bounded by their own logic), then reap.
if [ "${#PID2ID[@]}" -gt 0 ]; then
  log "draining ${#PID2ID[@]} in-flight build(s) to completion"
  while [ "${#PID2ID[@]}" -gt 0 ]; do sleep "$POLL"; reap; done
fi
log "done ($done_n tasks, $nonpass non-pass)"

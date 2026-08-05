#!/usr/bin/env bash
# gsc-overnight.sh — bounded overnight driver for cubic-castles build tasks.
#
# Runs queued cubic-castles tasks one at a time (work.sh enforces concurrency=1), each
# gate-verified. Guards so it can NEVER grind the Max quota all night:
#   - stops at a wall-clock deadline (GSC_DEADLINE_MIN, default 360 = 6h)
#   - stops after 2 CONSECUTIVE non-passes (the blind approach isn't landing -> save quota)
#   - respects state/PAUSE (checked every iteration; work.sh checks it too)
# Outcomes land on the BOARD + each task's status; escalations hit INBOX + Telegram as usual.
set -uo pipefail
ROOT="${RECURSION_ROOT:-/opt/recursion}"; cd "$ROOT"
DEADLINE_MIN="${GSC_DEADLINE_MIN:-360}"
LOG="$ROOT/loop/logs/$(date +%F)-gsc-overnight.log"
log(){ echo "[$(date -Is)] gsc-overnight: $*" | tee -a "$LOG"; }
START="$(date +%s)"
consec_fail=0
log "start (deadline ${DEADLINE_MIN}m)"

next_task(){
  # first queued cubic-castles task, alpha order (000 control sorts first)
  for f in $(ls state/tasks/cubic-castles-*.md 2>/dev/null | sort); do
    grep -q '^workstream: cubic-castles' "$f" || continue
    grep -q '^status: *queued' "$f" || continue
    sed -n 's/^id: *//p' "$f" | head -1; return 0
  done
  return 1
}

while :; do
  if [ -f "$ROOT/state/PAUSE" ]; then log "PAUSED — stopping"; break; fi
  elapsed_min=$(( ( $(date +%s) - START ) / 60 ))
  if [ "$elapsed_min" -ge "$DEADLINE_MIN" ]; then log "deadline reached (${elapsed_min}m) — stopping"; break; fi

  ID="$(next_task || true)"
  if [ -z "${ID:-}" ]; then log "no queued cubic-castles tasks — done"; break; fi

  log "running $ID (elapsed ${elapsed_min}m)"
  bash scripts/work.sh "$ID" || true
  ST="$(sed -n 's/^status: *//p' "state/tasks/$ID.md" | head -1)"
  log "$ID -> $ST"

  if [ "$ST" = "passed" ]; then
    consec_fail=0
  else
    consec_fail=$((consec_fail+1))
    if [ "$consec_fail" -ge 2 ]; then
      log "2 consecutive non-passes — stopping (approach not landing; saving Max quota)"; break
    fi
  fi
done
log "done"

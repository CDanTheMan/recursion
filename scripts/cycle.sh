#!/usr/bin/env bash
# One supervised tick (architecture.md flow):
#   cron -> Lua heartbeat -> (signal) Terra brief -> results to ledger -> Telegram
# The heartbeat is cheap and silent; the brief fires only when the heartbeat signals
# (or when forced, for the guaranteed daily digest). Every arm is recorded on the BOARD.
#
#   cycle.sh          # heartbeat; brief only if signalled
#   cycle.sh force    # always run the brief (the daily-digest cron uses this)
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a

FORCE="${1:-}"
DATE="$(date +%F)"
LOG_DIR="$ROOT/loop/logs"; mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$DATE-cycle.log"
log(){ echo "[$(date -Is)] $*" | tee -a "$LOG"; }

# Kill switch: a hard stop for v1 (heartbeat-under-pause is a v2 refinement). ------
if [ -f "$ROOT/state/PAUSE" ]; then
  log "PAUSED (state/PAUSE) — cycle idle. resume.sh to lift."
  exit 0
fi

log "cycle start (force=${FORCE:-no})"
bash scripts/board.sh begin

# --- 1) Heartbeat (Lua/luna). --------------------------------------------------------
bash scripts/board.sh add hb supervision heartbeat gpt-5.6-luna running "scanning ledger" >/dev/null
HB_USAGE="$LOG_DIR/$DATE-heartbeat.usage.json"
HB_OUT="$LOG_DIR/$DATE-heartbeat.out"
if bash loop/supervisor/run.sh heartbeat; then
  SIG_LINE="$(grep -E '===HEARTBEAT:' "$HB_OUT" 2>/dev/null | tail -1 || true)"
else
  log "heartbeat FAILED (run.sh alerts separately) — treating as quiet"
  SIG_LINE=""
fi

if printf '%s' "$SIG_LINE" | grep -q 'brief'; then SIGNAL="brief"; else SIGNAL="quiet"; fi
REASON="$(printf '%s' "$SIG_LINE" | sed -E 's/.*brief===[[:space:]]*//' | tr -d '\r')"
[ "$SIGNAL" = "quiet" ] && REASON="quiet"
bash scripts/board.sh finish hb done "$HB_USAGE" "$SIGNAL: ${REASON:-}" >/dev/null
log "heartbeat signal=$SIGNAL reason=${REASON:-}"

# --- 2) Brief (Terra) — only on a signal, or when forced. ----------------------------
if [ "$SIGNAL" = "brief" ] || [ "$FORCE" = "force" ]; then
  # Forced (daily) brief pushes the full digest; intra-day briefs stay silent (escalations
  # still ping via run.sh). This is what keeps a 3-hourly heartbeat from spamming Telegram.
  if [ "$FORCE" = "force" ]; then DELIVER=1; LBL="daily brief (pushed)"; else DELIVER=0; LBL="intra-day refresh (silent)"; fi
  bash scripts/board.sh add br supervision brief gpt-5.6-terra running "$LBL" >/dev/null
  BR_USAGE="$LOG_DIR/$DATE-morning.usage.json"
  if DELIVER_BRIEF=$DELIVER bash loop/supervisor/run.sh morning; then
    bash scripts/board.sh finish br done "$BR_USAGE" "$LBL" >/dev/null
    log "brief done (deliver=$DELIVER)"
  else
    bash scripts/board.sh finish br blocked "$BR_USAGE" "run failed" >/dev/null
    log "brief FAILED (run.sh alerts separately)"
  fi
else
  log "quiet tick — no brief"
fi

# --- 3) Commit the BOARD to loop/auto (run.sh already put us on that branch). ---------
# History of what ran, tick by tick. Never main (CLAUDE.md rule 2); non-fatal.
if git rev-parse --abbrev-ref HEAD 2>/dev/null | grep -q '^loop/auto$'; then
  git add -A state/BOARD.md 2>/dev/null || true
  git diff --cached --quiet 2>/dev/null || git commit -q -m "loop: board $DATE $(date -u +%H:%MZ)" 2>/dev/null || true
fi

# --- 3.5) Daily reflection (opt-in). --------------------------------------------------
# Once a day (on the forced/daily tick), the box reviews ITSELF and queues at most one
# improvement to state/PROPOSALS.md + one durable lesson to state/LESSONS.md/hermes memory.
# It never applies anything (CLAUDE.md rule 3) — the next brief surfaces the queue. $0 codex
# arm; default OFF (the human enables autonomy in .env; the loop can't self-enable, rule 3).
if [ "${RECURSION_AUTO_REFLECT:-0}" = "1" ] && [ "$FORCE" = "force" ] && [ ! -f "$ROOT/state/PAUSE" ]; then
  log "auto-reflect: daily self-review"
  bash scripts/reflect.sh >>"$LOG" 2>&1 || log "reflect FAILED (non-fatal)"
fi

# --- 4) Autonomous continuation (opt-in). ---------------------------------------------
# On the existing 3h cadence, if enabled and there is queued work, kick the drainer in the
# BACKGROUND (non-blocking, lock-guarded) so a heavy build never stalls the heartbeat. With
# RECURSION_AUTO_PLAN=1 it first refills the queue from the roadmaps. Both default OFF — the
# human enables autonomy in .env; the loop can't self-enable it (CLAUDE.md rule 3).
if [ "${RECURSION_AUTO_DRAIN:-0}" = "1" ] && [ ! -f "$ROOT/state/PAUSE" ]; then
  if [ "${RECURSION_AUTO_PLAN:-0}" = "1" ]; then
    for ws in ${RECURSION_PLAN_WORKSTREAMS:-}; do bash scripts/plan.sh "$ws" >>"$LOG" 2>&1 || true; done
  fi
  if grep -lq '^status: *queued' state/tasks/*.md 2>/dev/null; then
    if [ "${RECURSION_CONDUCT:-0}" = "1" ]; then
      log "auto-drain: queued work — kicking PARALLEL conductor in background"
      nohup bash scripts/conduct.sh >>"$LOG_DIR/$DATE-conduct.log" 2>&1 &
    else
      log "auto-drain: queued work present — kicking drainer in background"
      nohup bash scripts/drain.sh >>"$LOG_DIR/$DATE-drain.log" 2>&1 &
    fi
  fi
fi

log "cycle done (signal=$SIGNAL)"

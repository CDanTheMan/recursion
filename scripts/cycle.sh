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
  bash scripts/board.sh add br supervision brief gpt-5.6-terra running "daily brief" >/dev/null
  BR_USAGE="$LOG_DIR/$DATE-morning.usage.json"
  if bash loop/supervisor/run.sh morning; then
    bash scripts/board.sh finish br done "$BR_USAGE" "delivered" >/dev/null
    log "brief delivered"
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

log "cycle done (signal=$SIGNAL)"

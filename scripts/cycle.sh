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

# Kill switch (D-012): PAUSE halts EXECUTION and preserves AWARENESS. -----------------
# Heartbeat, brief, and escalation delivery keep running; arms, planning, drain/conduct and
# reflection do not. The old behaviour exited here, before the heartbeat — which contradicted
# docs/access.md, docs/architecture.md and pause.sh's own message, and meant that the moment
# you most needed to see what the box thought was the one moment it went silent. A paused box
# that cannot tell you it is paused is a blind spot, not a safety feature.
PAUSED=0
if [ -f "$ROOT/state/PAUSE" ]; then
  PAUSED=1
  log "PAUSED (state/PAUSE) — monitoring only: heartbeat + brief + escalations run; no arms, no planning, no drain. resume.sh to lift."
fi
export RECURSION_PAUSED="$PAUSED"   # run.sh labels the brief from this

log "cycle start (force=${FORCE:-no}, paused=$PAUSED)"
bash scripts/board.sh begin

# --- 0) Reap dead leases. MONITORING, so it runs even while paused. --------------------
# A worker that dies leaves `status: running` forever, and the board renders it as live work
# — that happened (an orphaned arm had to be found and killed by hand) and nothing detected
# it. Reaping is a state correction, not execution: it only ever moves running -> stale on a
# task whose lease has already expired. Doing it under PAUSE is the point — a paused box
# should still be able to tell you that a row is a corpse.
if [ -x scripts/taskctl.sh ]; then
  REAPED="$(bash scripts/taskctl.sh reap 2>/dev/null | grep -c '^reaped ' || true)"
  [ "${REAPED:-0}" -gt 0 ] && log "reaped ${REAPED} stale task lease(s)"
fi

# --- 0.5) Observe/resync the portfolio. ---------------------------------------------------
# Lucas reviews and merges on GitHub, so origin moves while this box sleeps. Anything built on
# a base older than origin's default silently reverts what he just merged, which is the one
# failure he asked for by name. So every cycle fast-forwards each registered repo BEFORE any
# dispatch can happen, and turns what a fast-forward cannot fix — divergence, unpushed work, a
# dirty tree, an unreachable remote — into an escalation instead of a log line.
#
# Under PAUSE only read-only awareness runs: fetch remote-tracking refs, report drift, and escalate,
# but never checkout, fast-forward, merge, or move a local branch/checked-out executable tree. The
# 2026-08-10 production incident proved that treating fast-forward as awareness let a paused cycle
# change deployed code. When resumed, the ordinary sync path still fast-forwards before dispatch.
if [ -x scripts/resync.sh ]; then
  if [ "$PAUSED" = "1" ]; then
    if bash scripts/resync.sh observe >>"$LOG" 2>&1; then
      log "portfolio observed (PAUSE: fetch/status only; no branch maintenance)"
    else
      log "portfolio observation reported drift a human must settle — see state/INBOX.md"
    fi
  elif bash scripts/resync.sh sync >>"$LOG" 2>&1; then
    log "portfolio resynced"
  else
    log "portfolio resync reported drift a human must settle — see state/INBOX.md"
  fi
fi

# --- 0.6) Intake. AWARENESS, so it runs even while paused. ---------------------------------
# Reads what Lucas said in the cockpit out of the gateway's own store and files it as durable
# instructions. It does NOT poll Telegram — the hermes gateway already long-polls getUpdates on
# this token, and two pollers steal updates from each other, losing messages silently.
#
# Hearing is not acting: an instruction is data for Hermes to decide on, and the actuator
# whitelist still governs what runs. That is exactly why this is safe under PAUSE — a paused box
# that cannot even hear you is a box you have to SSH into to talk to.
if [ -x scripts/intake.sh ]; then
  bash scripts/intake.sh poll >>"$LOG" 2>&1 || log "intake failed — see $LOG"
fi

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

# --- 2.5) Per-project digests, on the daily cycle only. ------------------------------------
# One message per active project, into that project's own topic. This is what gives each topic a
# pilot's memory: the gateway already keys a conversational session per (chat, thread), so the
# digest puts that project's facts into the session Lucas talks to when he opens the thread.
# Daily only — a digest every three hours is noise, and noise is how a real alert gets missed.
if [ "$FORCE" = "force" ] && [ -x scripts/digest.sh ]; then
  bash scripts/digest.sh --all >>"$LOG" 2>&1 || log "per-project digests failed — see $LOG"
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
# Reflection spawns an arm, so it is EXECUTION and stays halted under PAUSE (D-012).
if [ "${RECURSION_AUTO_REFLECT:-0}" = "1" ] && [ "$FORCE" = "force" ] && [ "$PAUSED" = "0" ]; then
  log "auto-reflect: daily self-review"
  bash scripts/reflect.sh >>"$LOG" 2>&1 || log "reflect FAILED (non-fatal)"
elif [ "$PAUSED" = "1" ] && [ "${RECURSION_AUTO_REFLECT:-0}" = "1" ] && [ "$FORCE" = "force" ]; then
  log "paused: skipping reflect (spawns an arm = execution)"
fi

# --- 4) Autonomous continuation (opt-in). ---------------------------------------------
# On the existing 3h cadence, if enabled and there is queued work, kick the drainer in the
# BACKGROUND (non-blocking, lock-guarded) so a heavy build never stalls the heartbeat. With
# RECURSION_AUTO_PLAN=1 it first refills the queue from the roadmaps. Both default OFF — the
# human enables autonomy in .env; the loop can't self-enable it (CLAUDE.md rule 3).
# Planning and draining are EXECUTION — halted under PAUSE (D-012). conduct.sh and work.sh
# each re-check state/PAUSE themselves; this is the outer gate, not the only one.
if [ "${RECURSION_AUTO_DRAIN:-0}" = "1" ] && [ "$PAUSED" = "1" ]; then
  log "paused: skipping plan/drain/conduct (execution)"
elif [ "${RECURSION_AUTO_DRAIN:-0}" = "1" ]; then
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

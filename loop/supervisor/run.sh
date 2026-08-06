#!/usr/bin/env bash
# Recursion supervisor. Headless Hermes (ChatGPT Pro via Codex OAuth) on a schedule.
# Runs on the $200 sub, NOT `claude -p` — see state/DECISIONS.md D-006/D-008.
#
# Design: this script is a pure text transform. It re-derives the ledger from disk
# every run (carry no state — memory: handoff-prompts-must-carry-no-state), feeds it
# into the prompt, and Hermes returns the brief on stdout. The agent needs no tools;
# run.sh owns file writes, escalation extraction, git, and delivery.
#
# Usage: run.sh <job>    e.g. run.sh morning
set -euo pipefail

ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
JOB="${1:-morning}"
LOG_DIR="$ROOT/loop/logs"; mkdir -p "$LOG_DIR"
DATE="$(date +%F)"
LOG="$LOG_DIR/$DATE-$JOB.log"
OUT="$LOG_DIR/$DATE-$JOB.out"
USAGE="$LOG_DIR/$DATE-$JOB.usage.json"
BRANCH="loop/auto"

cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a

log(){ echo "[$(date -Is)] $*" | tee -a "$LOG"; }

# --- Kill switch (architecture.md): state/PAUSE halts all autonomous action. ------
if [ -f "$ROOT/state/PAUSE" ]; then
  log "PAUSED (state/PAUSE present) — skipping $JOB. Remove it or run scripts/resume.sh."
  exit 0
fi

# --- Per-tier model (realizes Lua/Terra/Sol routing via --model). -----------------
# Decisions/brief = terra; cheap heartbeat = luna. See loop/config/routing.yaml.
case "$JOB" in
  morning)   PROMPT_FILE="loop/supervisor/morning-brief.md"; MODEL="gpt-5.6-terra"; MODE="brief" ;;
  heartbeat) PROMPT_FILE="loop/supervisor/heartbeat.md";     MODEL="gpt-5.6-luna";  MODE="signal" ;;
  *) echo "unknown job: $JOB" >&2; exit 2 ;;
esac

# --- Work on the auto branch. Never the default branch (CLAUDE.md hard rule 2). ----
DEFAULT_BRANCH="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-master}"
git rev-parse --verify "$BRANCH" >/dev/null 2>&1 \
  && git checkout -q "$BRANCH" \
  || git checkout -q -b "$BRANCH"
git merge -q --ff-only "$DEFAULT_BRANCH" 2>/dev/null || true

mkdir -p state/briefs
log "start $JOB (model=$MODEL)"

# --- Assemble the ledger (re-derived fresh every run). ----------------------------
SNAP="$ROOT/state/.recursion-snapshot.txt"
CTX="$(
  echo "===== ANCHOR (scope + success criteria) ====="; sed -n '1,90p' ANCHOR.md 2>/dev/null || true
  echo; echo "===== OPEN DECISIONS ====="; cat state/DECISIONS.md 2>/dev/null || true
  echo; echo "===== PROJECT STATUS (pushed from repos) ====="; cat state/projects/*.md 2>/dev/null || true
  echo; bash scripts/board-summary.sh --ledger 2>/dev/null || true
  echo; echo "===== DURABLE LESSONS (the box's own memory) ====="; cat state/LESSONS.md 2>/dev/null || true
  echo; echo "===== OPEN SELF-IMPROVEMENT PROPOSALS (surface, don't apply) ====="; tail -n 40 state/PROPOSALS.md 2>/dev/null || true
  echo; echo "===== PHYSICS GAP MAP ====="; cat state/gap-map.json 2>/dev/null || true
  echo; echo "===== SYLLABUS LEAD ====="; cat curriculum/syllabus-map.md 2>/dev/null || true
  echo; echo "===== CURRENT INBOX ====="; cat state/INBOX.md 2>/dev/null || true
  echo; echo "===== YESTERDAY'S SNAPSHOT (for the 'changed since' diff) ====="; cat "$SNAP" 2>/dev/null || true
)" || true

PROMPT="$(cat "$PROMPT_FILE")
=================== LEDGER (ground truth, re-derived this run) ===================
$CTX"

# --- Engine: one-shot Hermes on the sub. -----------------------------------------
if ! hermes -z "$PROMPT" -m "$MODEL" --usage-file "$USAGE" >"$OUT" 2>>"$LOG"; then
  log "FAILED $JOB — see $LOG"
  bash "$ROOT/scripts/notify.sh" "⚠ Recursion: $JOB failed. See $LOG" || true
  exit 1
fi
cat "$OUT" >> "$LOG"

if [ "${MODE:-brief}" = "brief" ]; then   # signal-mode (heartbeat) stops here — no brief/deliver/commit
# --- Write the brief (everything before the escalation block). --------------------
BRIEF="state/briefs/$DATE.md"
awk 'BEGIN{p=1} /^===INBOX-START===/{p=0} p{print} /^===INBOX-END===/{p=1}' "$OUT" > "$BRIEF"

# --- Extract escalations → durable INBOX queue + a distinct Telegram ping. ---------
ESC="$(awk '/^===INBOX-START===/{f=1;next} /^===INBOX-END===/{f=0} f' "$OUT")"
if [ -n "${ESC//[[:space:]]/}" ]; then
  { echo; echo "$ESC"; } >> state/INBOX.md
  log "escalation(s) appended to state/INBOX.md"
  bash "$ROOT/scripts/notify.sh" "🔔 Recursion needs a decision:
$ESC" || true
fi

# --- Save today's snapshot for tomorrow's diff. -----------------------------------
cat state/projects/*.md 2>/dev/null > "$SNAP" || true

# --- Commit any state changes (agent output). Never main. -------------------------
if ! git diff --quiet || ! git diff --cached --quiet; then
  git add -A state/ || true
  if git commit -q -m "loop: $JOB $DATE"; then
    log "committed to $BRANCH"
  else
    log "commit FAILED (non-fatal — check git identity on the box); continuing to delivery"
  fi
else
  log "no changes"
fi

# --- Deliver the brief to Telegram (daily digest only). ---------------------------
# Intra-day heartbeat-triggered briefs set DELIVER_BRIEF=0: they still write the brief,
# update the board, and fire escalation pings above — but don't push a full digest every
# few hours. Escalations always reach you; routine intra-day briefs stay silent.
if [ "${DELIVER_BRIEF:-1}" = "1" ] && [ -f "$BRIEF" ]; then
  # Append the review-branch tracker VERBATIM so the digest always carries the exact branch list,
  # merge status, and review order (the loop pushes branches; you merge on GitHub).
  { echo; echo; bash "$ROOT/scripts/branch-review.sh" 2>/dev/null; } >> "$BRIEF"
  bash "$ROOT/scripts/notify.sh" -f "$BRIEF" || true
fi
fi   # end brief-mode block

# --- Per-job fallback check: did this run drop off the sub onto metered billing? ---
PROV="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("provider",""))' "$USAGE" 2>/dev/null || true)"
COST="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("estimated_cost_usd",0))' "$USAGE" 2>/dev/null || true)"
if [ -n "$PROV" ] && [ "$PROV" != "openai-codex" ]; then
  bash "$ROOT/scripts/notify.sh" "⚠ Recursion $JOB ran on FALLBACK (provider=$PROV, cost=\$$COST) — not the ChatGPT sub. Check quota/gateway." || true
fi

log "done $JOB"

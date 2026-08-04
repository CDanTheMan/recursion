#!/usr/bin/env bash
# Recursion supervisor. Headless Claude Code on a schedule.
# Usage: run.sh <job>    e.g. run.sh morning
set -euo pipefail

ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
JOB="${1:-morning}"
LOG_DIR="$ROOT/loop/logs"; mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%F)-$JOB.log"
BRANCH="loop/auto"

cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a

case "$JOB" in
  morning) PROMPT_FILE="loop/supervisor/morning-brief.md" ;;
  *) echo "unknown job: $JOB" >&2; exit 2 ;;
esac

# Work on the auto branch. Never main.
git rev-parse --verify "$BRANCH" >/dev/null 2>&1 \
  && git checkout -q "$BRANCH" \
  || git checkout -q -b "$BRANCH"
git merge -q --ff-only main 2>/dev/null || true

mkdir -p state/briefs

echo "[$(date -Is)] start $JOB" | tee -a "$LOG"

if ! claude -p "$(cat "$PROMPT_FILE")" \
      --allowedTools "Read,Write,Bash(git *)" \
      >>"$LOG" 2>&1; then
  echo "[$(date -Is)] FAILED $JOB — see $LOG" | tee -a "$LOG"
  bash "$ROOT/scripts/notify.sh" "Recursion: $JOB failed. See $LOG" || true
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  git add -A state/
  git commit -q -m "loop: $JOB $(date +%F)"
  echo "[$(date -Is)] committed to $BRANCH" | tee -a "$LOG"
else
  echo "[$(date -Is)] no changes" | tee -a "$LOG"
fi

BRIEF="state/briefs/$(date +%F).md"
[ -f "$BRIEF" ] && bash "$ROOT/scripts/notify.sh" "$(head -c 3000 "$BRIEF")" || true

echo "[$(date -Is)] done $JOB" | tee -a "$LOG"

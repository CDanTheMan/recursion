#!/usr/bin/env bash
# reflect.sh — the box looks at ITSELF and proposes one improvement (bounded self-improvement).
#
# This is the reflection tier. Where run.sh briefs Lucas on the WORK, reflect.sh briefs the box
# on the MACHINE: build-loop outcomes, arm logs, escalation precision, cost. It is a pure text
# transform in the run.sh mould — re-derive a REFLECTION LEDGER from disk, feed it to a tool-less
# Hermes arm ($0 codex sub), and reflect.sh owns every write. The arm proposes; it never applies.
#
# Two durable outputs (append-only, committed to loop/auto — never main, CLAUDE.md rule 2):
#   state/PROPOSALS.md  the human-review queue. NOTHING here is auto-applied (CLAUDE.md rule 3);
#                       the daily brief surfaces it, a human decides.
#   state/LESSONS.md    the box's own memory — one durable line per cycle, re-fed into every
#                       future arm (via run.sh's ledger) so lessons compound.
# And one hermes-native bridge (fenced, $0, non-fatal): the lesson is also written to hermes
# built-in memory (MEMORY.md), which is auto-injected into every future arm and shows up in the
# memory-graph / journey / curator substrate. This is the "leverage hermes capabilities" leg.
#
# Usage: reflect.sh
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a

DATE="$(date +%F)"; STAMP="$(date '+%Y-%m-%d %H:%M')"
LOG_DIR="$ROOT/loop/logs"; mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$DATE-reflect.log"
OUT="$LOG_DIR/$DATE-reflect.out"
USAGE="$LOG_DIR/$DATE-reflect.usage.json"
BRANCH="loop/auto"
MODEL="${RECURSION_REFLECT_MODEL:-gpt-5.6-terra}"   # a reasoning task -> brief tier, not luna
PROMPT_FILE="loop/supervisor/reflect.md"
PROPOSALS="state/PROPOSALS.md"
LESSONS="state/LESSONS.md"

log(){ echo "[$(date -Is)] $*" | tee -a "$LOG"; }

# --- Kill switch (architecture.md): state/PAUSE halts all autonomous action. -----------
if [ -f "$ROOT/state/PAUSE" ]; then
  log "PAUSED (state/PAUSE present) — skipping reflect."
  exit 0
fi

# --- Work on the auto branch. Never the default branch (CLAUDE.md hard rule 2). ---------
DEFAULT_BRANCH="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-master}"
git rev-parse --verify "$BRANCH" >/dev/null 2>&1 && git checkout -q "$BRANCH" || git checkout -q -b "$BRANCH"
git merge -q --ff-only "$DEFAULT_BRANCH" 2>/dev/null || true

log "start reflect (model=$MODEL)"

# --- Assemble the REFLECTION LEDGER (re-derived fresh every run; carry no state). -------
# Everything the reflector needs to judge the machine: what built, what escalated, what it
# cost, what it already knows, and what is already proposed (so it does not repeat itself).
LEDGER="$(
  echo "===== BUILD-LOOP OUTCOMES ====="; bash scripts/board-summary.sh 2>/dev/null || true
  echo; echo "===== ESCALATION HISTORY (state/INBOX.md) ====="; tail -n 80 state/INBOX.md 2>/dev/null || true
  echo; echo "===== RECENT ARM LOGS (last lines of the newest work/drain logs) ====="
  for f in $(ls -t loop/logs/*-drain.log loop/logs/*-cycle.log 2>/dev/null | head -3); do
    echo "--- $f ---"; tail -n 15 "$f" 2>/dev/null || true
  done
  echo; echo "===== COST / USAGE TELEMETRY (hermes insights, 7d) ====="
  hermes insights --days 7 2>/dev/null | sed -n '1,40p' || echo "(insights unavailable)"
  echo; echo "===== LESSONS ALREADY LEARNED (do not repeat) ====="; cat "$LESSONS" 2>/dev/null || echo "(none yet)"
  echo; echo "===== PROPOSALS ALREADY OPEN (do not repeat) ====="; tail -n 60 "$PROPOSALS" 2>/dev/null || echo "(none yet)"
)" || true

PROMPT="$(cat "$PROMPT_FILE")
=================== REFLECTION LEDGER (ground truth, re-derived this run) ===================
$LEDGER"

# --- Engine: one-shot tool-less Hermes on the sub (stdout = final message; tools off). --
if ! hermes -z "$PROMPT" -m "$MODEL" --usage-file "$USAGE" >"$OUT" 2>>"$LOG"; then
  log "reflect arm FAILED — see $LOG"
  bash "$ROOT/scripts/notify.sh" "⚠ Recursion: reflect arm failed. See $LOG" || true
  exit 1
fi
cat "$OUT" >> "$LOG"

# --- Fallback check: did we drop off the $0 sub onto metered billing? -------------------
PROV="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("provider",""))' "$USAGE" 2>/dev/null || true)"
COST="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("estimated_cost_usd",0))' "$USAGE" 2>/dev/null || true)"
if [ -n "$PROV" ] && [ "$PROV" != "openai-codex" ]; then
  bash "$ROOT/scripts/notify.sh" "⚠ Recursion reflect ran on FALLBACK (provider=$PROV, cost=\$$COST) — not the ChatGPT sub." || true
fi

# --- Extract the two blocks (mirror run.sh's INBOX extraction). -------------------------
LESSON="$(awk '/^===LESSON-START===/{f=1;next} /^===LESSON-END===/{f=0} f' "$OUT" | sed '/^[[:space:]]*$/d')"
PROPOSAL="$(awk '/^===PROPOSAL-START===/{f=1;next} /^===PROPOSAL-END===/{f=0} f' "$OUT")"

# --- Durable lesson -> the box's own versioned memory (dedup on the line text). ---------
if [ -n "${LESSON//[[:space:]]/}" ]; then
  [ -f "$LESSONS" ] || printf '# Recursion — durable operational lessons\n\nOne line per cycle. Re-fed into every arm so lessons compound. Reflect.sh appends; humans prune.\n' > "$LESSONS"
  if ! grep -qxF "- $LESSON" "$LESSONS" 2>/dev/null; then
    printf -- '- %s\n' "$LESSON" >> "$LESSONS"
    log "lesson recorded: $LESSON"
    # --- hermes-native bridge: also persist to built-in memory (auto-injected into future
    # arms; visible in memory-graph/journey/curator). $0, fenced, non-fatal. Writes hermes's
    # OWN memory store — NOT loop config/auth/model/cron, so it is within CLAUDE.md rule 3.
    if [ "${RECURSION_REFLECT_HERMES_MEMORY:-1}" = "1" ]; then
      MEMMODEL="${RECURSION_REFLECT_MEM_MODEL:-gpt-5.6-luna}"
      MPROMPT="Use your memory tool to durably record this single operational lesson about the Recursion control-plane box, so future sessions recall it. Record ONLY this, verbatim, then stop:
$LESSON"
      if hermes -z "$MPROMPT" -m "$MEMMODEL" -t memory >>"$LOG" 2>>"$LOG"; then
        log "lesson mirrored to hermes memory"
      else
        log "hermes-memory bridge failed (non-fatal)"
      fi
    fi
  else
    log "lesson already known — not re-recording"
  fi
else
  log "no new lesson this cycle"
fi

# --- Proposal -> the human-review queue. Append-only. NOTHING is applied here. ----------
if [ -n "${PROPOSAL//[[:space:]]/}" ]; then
  [ -f "$PROPOSALS" ] || printf '# Recursion — self-improvement proposals (human-review queue)\n\nReflect.sh appends; a human applies or rejects. NOTHING here is auto-applied (CLAUDE.md rule 3).\n[APPLY-SAFE] = low-risk, likely-approve. [NEEDS-APPROVAL] = touches config/auth/model/cron/gate/spend/mining.\n' > "$PROPOSALS"
  TITLE="$(printf '%s' "$PROPOSAL" | sed -n '1p' | tr -d '\r')"
  { echo; echo "## $STAMP — ${TITLE}"; echo "status: open"; echo; printf '%s\n' "$PROPOSAL"; } >> "$PROPOSALS"
  log "proposal queued: $TITLE"
else
  log "no proposal this cycle (honest 'nothing worth changing')"
fi

# --- Commit the queue + memory to loop/auto (never main; non-fatal). --------------------
# Scope the add+commit to ONLY our two files (loop/auto carries other uncommitted work we must
# not sweep in), and STAGE FIRST so newly-created (untracked) files are detected — git diff on
# an untracked path reports no change, which silently skipped the first commit.
git add -- "$PROPOSALS" "$LESSONS" 2>/dev/null || true
if ! git diff --cached --quiet -- "$PROPOSALS" "$LESSONS" 2>/dev/null; then
  git commit -q -m "loop: reflect $DATE" -- "$PROPOSALS" "$LESSONS" 2>/dev/null && log "committed to $BRANCH" || log "commit skipped/failed (non-fatal)"
else
  log "no queue changes to commit"
fi

log "done reflect"

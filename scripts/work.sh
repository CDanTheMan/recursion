#!/usr/bin/env bash
# work.sh — the build-loop executor (delegation-design.md "The pipeline", Plane 2).
#
#   queued task -> dispatch an arm to GENERATE -> run the ACCEPTANCE test (the gate) ->
#   on green: auto-commit output to loop/work/<id> (never main, never merge)
#   on red:   retry the arm once, then ESCALATE (INBOX + Telegram)
#
# The load-bearing rule (delegation-design.md): autonomy rests on the acceptance test, not
# trust. A task with no machine-checkable acceptance command is NEVER auto-integrated — it
# escalates. The generator is never trusted; only a green gate earns an auto-commit.
#
# Build output lives on a per-task branch in an isolated git WORKTREE, so it never collides
# with the main tree (which cron keeps on loop/auto). Every arm lands on the BOARD.
#
#   work.sh <id|path>   run a specific task (state/tasks/<id>.md, or a file path)
#   work.sh             pull the first queued task in state/tasks/ (alpha order)
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a

DATE="$(date +%F)"; STAMP="$(date +%H%M%S)"
LOG_DIR="$ROOT/loop/logs"; mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$DATE-work.log"
log(){ echo "[$(date -Is)] work: $*" | tee -a "$LOG" >&2; }
board(){ bash scripts/board.sh "$@" >/dev/null 2>&1 || true; }
notify(){ [ "${RECURSION_NO_NOTIFY:-0}" = "1" ] && return 0; bash "$ROOT/scripts/notify.sh" "$@" >/dev/null 2>&1 || true; }

# --- kill switch (architecture.md): state/PAUSE halts the executor like every job. ------
if [ -f "$ROOT/state/PAUSE" ]; then log "PAUSED (state/PAUSE) — executor idle."; exit 0; fi

# --- concurrency = 1 (first-slice default). mkdir is atomic. ---------------------------
LOCK="$ROOT/state/.work.lock"
if ! mkdir "$LOCK" 2>/dev/null; then log "another executor holds $LOCK — exiting."; exit 0; fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

# --- resolve the task -----------------------------------------------------------------
ARG="${1:-}"
if   [ -n "$ARG" ] && [ -f "$ARG" ];                  then TASK="$ARG"
elif [ -n "$ARG" ] && [ -f "state/tasks/$ARG.md" ];   then TASK="state/tasks/$ARG.md"
elif [ -z "$ARG" ]; then
  TASK="$(grep -l '^status: *queued' state/tasks/*.md 2>/dev/null | sort | head -1 || true)"
  [ -n "$TASK" ] || { log "no queued tasks in state/tasks/."; exit 0; }
else
  log "no such task: $ARG"; exit 2
fi

field(){ sed -n "s/^$1: *//p" "$TASK" | head -1 | tr -d '\r'; }
ID="$(field id)"; WORKSTREAM="$(field workstream)"; GOAL="$(field goal)"
ENGINE="$(field engine)"; ACCEPTANCE="$(field acceptance)"; WORKDIR="$(field workdir)"
AUTONOMY="$(field autonomy)"; MODEL="$(field model)"
WORKDIR="${WORKDIR:-.}"; AUTONOMY="${AUTONOMY:-auto}"; ENGINE="${ENGINE:-claude}"
[ -n "$ID" ] || { log "task $TASK missing 'id:'"; exit 2; }
BRANCH="loop/work/$ID"
ARMLOG="$LOG_DIR/$DATE-arm-$ID-$STAMP.out"
# body = the detailed spec (everything after the first blank line)
BODY="$(awk 'f{print} /^[[:space:]]*$/{f=1}' "$TASK")"

log "task=$ID ws=${WORKSTREAM:-?} engine=$ENGINE workdir=$WORKDIR"
log "acceptance: ${ACCEPTANCE:-<none>}"

set_status(){ sed -i "s#^status: .*#status: $1#" "$TASK" 2>/dev/null || true; }

# ledger writes (task status + BOARD) go to loop/auto, like every other loop write.
commit_state(){
  if git rev-parse --abbrev-ref HEAD 2>/dev/null | grep -q '^loop/auto$'; then
    git add -A state/ 2>/dev/null || true
    git diff --cached --quiet 2>/dev/null || \
      git -c user.name="recursion-loop" -c user.email="loop@recursion.local" \
        commit -q -m "loop: task $ID -> $(field status)" 2>/dev/null || true
  fi
}

# escalation carries the context handle (Workstream + Pointer) — morning-brief.md format.
escalate(){
  local reason="$1" rc="${2:-}"
  { echo
    echo "## build escalation — $ID  ($(date -u +%FT%TZ))"
    echo "**Workstream:** ${WORKSTREAM:-unknown}"
    echo "**Pointer:** state/tasks/$ID.md · branch $BRANCH · arm log ${ARMLOG#$ROOT/}"
    echo "Blocked on: $reason"
    [ -n "$rc" ] && echo "Acceptance: \`$ACCEPTANCE\` exited $rc"
    echo "Options: inspect the worktree/branch, fix the task or its acceptance, then \`recursion work $ID\`."
  } >> state/INBOX.md
  log "escalated: $reason"
  notify "🔔 Recursion build blocked: $ID — $reason"
}

# --- acceptance is the contract: no test -> no autonomy (delegation-design.md) ----------
if [ -z "$ACCEPTANCE" ]; then
  board add "$ID" "${WORKSTREAM:-?}" "$ENGINE" "${MODEL:-$ENGINE}" blocked "no acceptance test"
  set_status escalated
  escalate "no machine-checkable acceptance test (autonomy requires one)"
  commit_state
  exit 0
fi

# --- create the isolated worktree on loop/work/<id> (never touches the main tree) -------
mk_worktree(){
  local wt="$ROOT/.worktrees/$ID" base
  git worktree remove --force "$wt" 2>/dev/null || true
  rm -rf "$wt" 2>/dev/null || true
  git worktree prune 2>/dev/null || true
  base="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)"
  base="${base:-master}"
  git rev-parse --verify "$base" >/dev/null 2>&1 || base="$(git rev-parse --abbrev-ref HEAD)"
  git worktree add -B "$BRANCH" "$wt" "$base" >>"$LOG" 2>&1 || return 1
  printf '%s\n' "$wt"
}

# --- the arm: GENERATE files into the worktree. Exit code is advisory — the gate decides. -
BUILD_PROMPT="You are a build arm for the Recursion system. Produce working source files.

TASK: $GOAL
Write your output into the directory: $WORKDIR (relative to the current working directory).

Constraints:
- WRITE FILES ONLY. Do NOT run npm, builds, servers, git, or any shell command — a separate
  verifier runs the acceptance test after you finish.
- Your work is gated by this exact command (make it exit 0): $ACCEPTANCE
- Keep it minimal and CORRECT. A minimal thing that builds beats a rich thing that does not.

$BODY"

ARM_USAGE="${ARMLOG%.out}.usage.json"
run_arm(){
  local wt="$1"
  case "$ENGINE" in
    none) return 0 ;;   # verify-only: gate whatever is already in the worktree
    claude)
      command -v claude >/dev/null 2>&1 || return 90
      # claude may print "Not logged in" yet still exit 0 (writing nothing) — the gate
      # catches a no-op arm and escalates. This arm is ~flat on Claude Max once logged in.
      ( cd "$wt" && claude -p "$BUILD_PROMPT" --permission-mode acceptEdits ${MODEL:+--model "$MODEL"} ) \
        >"$ARMLOG" 2>&1 || true
      return 0 ;;
    hermes)
      # hermes has native file/terminal tools — BUT tool-calling turns fall off the Codex
      # sub onto metered OpenRouter (measured 2026-08-05), so this arm is FENCED like every
      # metered leg. Its cost lands on the BOARD via --usage-file.
      [ "${RECURSION_ALLOW_METERED:-0}" = "1" ] || return 93
      command -v hermes >/dev/null 2>&1 || return 94
      ( cd "$wt" && hermes -z "$BUILD_PROMPT" -m "${MODEL:-gpt-5.6-sol}" -t file,terminal --yolo \
          --usage-file "$ARM_USAGE" ) >"$ARMLOG" 2>&1 || true
      return 0 ;;
    deepseek|openrouter)
      return 91 ;;   # raw chat-completion has no file tools — needs a file-emission protocol (design: later)
    *) return 92 ;;
  esac
}

# --- the gate: run the acceptance command in the app dir; its exit code is the verdict. --
verify(){
  local wt="$1" adir="$1/$WORKDIR"
  [ -d "$adir" ] || adir="$wt"
  ( cd "$adir" && bash -c "$ACCEPTANCE" ) >>"$ARMLOG" 2>&1
}

# ============================ pipeline ============================
board add "$ID" "${WORKSTREAM:-?}" "$ENGINE" "${MODEL:-$ENGINE}" running "${GOAL:0:40}"
set_status running; commit_state

if ! WT="$(mk_worktree)"; then
  board finish "$ID" blocked - "worktree create failed"
  set_status escalated; escalate "could not create git worktree $BRANCH"; commit_state
  exit 0
fi
log "worktree: $WT (branch $BRANCH)"

# --- EXECUTE (attempt 1) --------------------------------------------------------------
if run_arm "$WT"; then arc=0; else arc=$?; fi
if [ "$arc" -ne 0 ]; then
  case "$arc" in
    90) msg="claude CLI not logged in / unavailable (run: claude /login on the box)" ;;
    91) msg="engine=$ENGINE has no file-writing tool yet (needs a file-emission protocol)" ;;
    93) msg="engine=hermes is metered (tool-calls route to OpenRouter) — set RECURSION_ALLOW_METERED=1 to allow" ;;
    94) msg="hermes CLI unavailable" ;;
    *)  msg="arm dispatch error (code $arc)" ;;
  esac
  board finish "$ID" blocked - "$msg"
  set_status escalated; escalate "$msg"; commit_state
  git worktree remove --force "$WT" 2>/dev/null || true
  exit 0
fi

# --- VERIFY (+ retry the arm once on red, per design) ---------------------------------
PASS=0; rc=0
if verify "$WT"; then
  PASS=1
else
  rc=$?
  log "acceptance FAILED (exit $rc), attempt 1"
  if [ "$ENGINE" != "none" ]; then
    log "retry once (design: retry once then escalate)"
    run_arm "$WT" || true
    if verify "$WT"; then PASS=1; else rc=$?; fi
  fi
fi

# --- INTEGRATE ------------------------------------------------------------------------
if [ "$PASS" = "1" ]; then
  git -C "$WT" add -A 2>>"$LOG" || true
  if git -C "$WT" diff --cached --quiet 2>/dev/null; then
    NOTE="passed (no file changes)"; log "acceptance green; nothing to commit (verify-only)"
  else
    git -C "$WT" -c user.name="recursion-loop" -c user.email="loop@recursion.local" \
      commit -q -m "build($ID): $GOAL

acceptance: $ACCEPTANCE (green)
engine: $ENGINE" 2>>"$LOG" || true
    NOTE="passed -> $BRANCH"; log "committed build output to $BRANCH"
  fi
  if [ -f "$ARM_USAGE" ]; then board finish "$ID" done "$ARM_USAGE" "$NOTE"; else board finish "$ID" done - "$NOTE"; fi
  set_status passed; commit_state
  notify "✅ Recursion build passed: $ID -> $BRANCH (acceptance green). Review/merge at your pace."
  git worktree remove --force "$WT" 2>/dev/null || true   # branch persists for review
  log "DONE $ID passed"
else
  board finish "$ID" blocked - "acceptance failed (exit $rc)"
  set_status failed; escalate "acceptance test failed after retry" "$rc"; commit_state
  log "left worktree for inspection: $WT (branch $BRANCH)"
fi

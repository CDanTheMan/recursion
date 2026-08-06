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
# repo: which git repo the arm builds in. Default = this repo ($ROOT). An external repo
# (e.g. /opt/golden-stallion-client) lets the loop build another codebase; its build output
# and loop/work/<id> branch live in THAT repo, gated by whatever acceptance the task names.
REPO_DIR="$(field repo)"; REPO_DIR="${REPO_DIR:-$ROOT}"
# seed: gitignored paths (space/comma separated, relative to REPO_DIR) to COPY into each fresh
# worktree. git worktree does NOT inherit gitignored files, so a required-but-untracked data
# corpus (e.g. the GSC block-model corpus user-client/render/data/models) is absent in a new
# worktree and every test that needs it fails. Declaring it here makes the dependency explicit.
SEED="$(field seed)"; SEED="${SEED//,/ }"
# git authority (all default-safe). sshkey = the deploy key for THIS repo (fetch, and push IF the
# key has write). automerge/automerge_scope opt a task into PATH-SCOPED auto-merge. Push and merge
# are ALSO globally fenced by env flags (RECURSION_ALLOW_PUSH / RECURSION_ALLOW_AUTOMERGE) set only
# in .env by the human — the loop can never self-enable them (CLAUDE.md rule 3).
SSHKEY="$(field sshkey)"; AUTOMERGE="$(field automerge)"; AUTOMERGE_SCOPE="$(field automerge_scope)"
PLANNED_FROM="$(field planned_from)"   # <roadmap>:<line> — flipped [~]->[x] when this task passes
GSSH=""; [ -n "$SSHKEY" ] && GSSH="ssh -i ${SSHKEY/#\~/$HOME} -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=12"
gitr(){ if [ -n "$GSSH" ]; then GIT_SSH_COMMAND="$GSSH" git -C "$REPO_DIR" "$@"; else git -C "$REPO_DIR" "$@"; fi; }
[ -n "$ID" ] || { log "task $TASK missing 'id:'"; exit 2; }
BRANCH="loop/work/$ID"

# --- per-workstream lock (parallel-loops.md): at most one build per workstream; different
# workstreams run concurrently. mkdir is atomic. Replaces the old global state/.work.lock so
# conduct.sh can drive several at once. Serial callers (drain/manual/cycle) run one work.sh, so
# this behaves exactly like the old global lock for them. -------------------------------
mkdir -p "$ROOT/state/.locks" 2>/dev/null || true
WSLOCK="$ROOT/state/.locks/ws-${WORKSTREAM:-none}.lock"
if ! mkdir "$WSLOCK" 2>/dev/null; then log "workstream ${WORKSTREAM:-none} already building (held $WSLOCK) — exiting."; exit 0; fi
trap 'rmdir "$WSLOCK" 2>/dev/null || true' EXIT
ARMLOG="$LOG_DIR/$DATE-arm-$ID-$STAMP.out"
# body = the detailed spec (everything after the first blank line)
BODY="$(awk 'f{print} /^[[:space:]]*$/{f=1}' "$TASK")"

log "task=$ID ws=${WORKSTREAM:-?} engine=$ENGINE repo=$REPO_DIR workdir=$WORKDIR"
log "acceptance: ${ACCEPTANCE:-<none>}"

set_status(){ sed -i "s#^status: .*#status: $1#" "$TASK" 2>/dev/null || true; }

# ledger writes (task status + BOARD) go to loop/auto, like every other loop write.
# Under parallel loops several work.sh share this one $ROOT tree/index, so serialize the ledger
# commit behind a short lock (spin <=30s, then proceed). Serial callers acquire it instantly.
ledger_lock(){ local i=0; mkdir -p "$ROOT/state/.locks" 2>/dev/null || true; while ! mkdir "$ROOT/state/.locks/ledger.lock" 2>/dev/null; do i=$((i+1)); [ "$i" -ge 60 ] && return 0; sleep 0.5; done; return 0; }
ledger_unlock(){ rmdir "$ROOT/state/.locks/ledger.lock" 2>/dev/null || true; }
commit_state(){
  if git rev-parse --abbrev-ref HEAD 2>/dev/null | grep -q '^loop/auto$'; then
    ledger_lock
    git add -A state/ 2>/dev/null || true
    git diff --cached --quiet 2>/dev/null || \
      git -c user.name="recursion-loop" -c user.email="loop@recursion.local" \
        commit -q -m "loop: task $ID -> $(field status)" 2>/dev/null || true
    ledger_unlock
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
    echo "Options: inspect the worktree/branch, fix the task or its acceptance, then \`recursion work $ID\` (or \`recursion requeue $ID\`)."
    echo "Close it with: \`recursion resolve $ID \"<what you decided>\"\`."
  } >> state/INBOX.md
  log "escalated: $reason"
  # Lead the ping with a [id] tag: there is no reply<->item correlation, so referencing the tag
  # (in a reply or a `recursion resolve <id>`) is how a decision reaches the right escalation.
  notify "🔔 [$ID] build blocked — $reason
Reply referencing [$ID], or on the box: recursion resolve $ID \"...\""
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
  local wt="$REPO_DIR/.worktrees/$ID" base def
  # per-repo worktree lock (parallel-loops.md): serialize git worktree ops so two workstreams
  # sharing a repo do not race git ref/index locks. Cross-repo streams never contend.
  local rk wtlock wi=0; rk="$(printf '%s' "$REPO_DIR" | md5sum | cut -c1-12)"
  wtlock="$ROOT/state/.locks/wt-$rk.lock"; mkdir -p "$ROOT/state/.locks" 2>/dev/null || true
  while ! mkdir "$wtlock" 2>/dev/null; do wi=$((wi+1)); [ "$wi" -ge 120 ] && break; sleep 0.5; done
  git -C "$REPO_DIR" worktree remove --force "$wt" 2>/dev/null || true
  rm -rf "$wt" 2>/dev/null || true
  git -C "$REPO_DIR" worktree prune 2>/dev/null || true
  # Fetch latest so the task builds on the FRESHEST merged base — this is what makes work
  # ACCUMULATE across tasks (once you merge task N, task N+1 builds on top). Non-fatal: offline
  # or no cred just falls back to the local base. Disable with RECURSION_GIT_FETCH=0.
  if [ "${RECURSION_GIT_FETCH:-1}" = "1" ]; then
    gitr fetch --prune --quiet origin >>"$LOG" 2>&1 && log "fetched origin" || log "fetch skipped/failed — building on local base"
  fi
  def="$(git -C "$REPO_DIR" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)"; def="${def:-master}"
  # prefer the remote-tracking tip (freshest merged main); fall back to local, then current HEAD.
  if git -C "$REPO_DIR" rev-parse --verify "origin/$def" >/dev/null 2>&1; then base="origin/$def"
  elif git -C "$REPO_DIR" rev-parse --verify "$def" >/dev/null 2>&1; then base="$def"
  else base="$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)"; fi
  git -C "$REPO_DIR" worktree add -B "$BRANCH" "$wt" "$base" >>"$LOG" 2>&1; local addrc=$?
  rmdir "$wtlock" 2>/dev/null || true
  [ "$addrc" -eq 0 ] || return 1
  # seed gitignored data the tests need but the worktree did not inherit (see SEED note above).
  local p
  for p in $SEED; do
    if [ -e "$REPO_DIR/$p" ]; then
      mkdir -p "$wt/$(dirname "$p")"
      cp -a "$REPO_DIR/$p" "$wt/$p"
      log "seeded $p into worktree ($(find "$wt/$p" -type f 2>/dev/null | wc -l | tr -d ' ') files)"
    else
      log "WARN seed path missing in repo: $REPO_DIR/$p (task may fail on absent data)"
    fi
  done
  printf '%s\n' "$wt"
}

# --- the arm: GENERATE files into the worktree. Exit code is advisory — the gate decides. -
BUILD_PROMPT="You are a build arm for the Recursion system. Produce working source files.

TASK: $GOAL
The target repo is already checked out at the current directory; your output goes here.
Output/work subdir for this task: $WORKDIR

Rules:
- Your work is gated by this exact command, which MUST exit 0: $ACCEPTANCE
- You MAY read the codebase and run \`node\` (e.g. \`node --test <file>\`) to check your work as
  you go. You may NOT run installers, servers, git, or any other shell command.
- Do NOT modify test files (*.test.cjs), truth fixtures, or golden data to force a pass — that
  is tampering and the gate rejects it. Fix the IMPLEMENTATION, not the test.
- Keep changes minimal and CORRECT. Minimal-and-correct beats broad-and-broken.

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
      # acceptEdits auto-approves file writes; --allowedTools adds ONLY `node` (so the arm can
      # run tests to iterate) — never arbitrary bash, on a root box.
      ( cd "$wt" && claude -p "$BUILD_PROMPT" --permission-mode acceptEdits \
          --allowedTools 'Bash(node:*)' ${MODEL:+--model "$MODEL"} ) >"$ARMLOG" 2>&1 || true
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

# --- after a GREEN build: optionally PUBLISH the review branch, and optionally AUTO-MERGE. -----
# Layers of defense, all off by default:
#   publish  : RECURSION_ALLOW_PUSH=1 (env, human-set). Pushes loop/work/<id> only. Never force.
#   automerge: RECURSION_ALLOW_AUTOMERGE=1 (env) AND task `automerge: yes` AND the branch diff
#              touches ONLY automerge_scope/  AND the merge is fast-forward. ff-only push to the
#              default branch = safest merge (no merge commit; auto-rejects if main moved). Any
#              file outside scope -> BLOCK + escalate (a chiron lane can't smuggle a control change).
integrate_remote(){
  local def; def="$(git -C "$REPO_DIR" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)"; def="${def:-master}"
  if [ "${RECURSION_ALLOW_PUSH:-0}" = "1" ]; then
    if gitr push origin "$BRANCH" >>"$LOG" 2>&1; then
      log "published $BRANCH to origin"; notify "📤 [$ID] published $BRANCH for review"
    else
      log "publish failed (read-only key or non-ff) — branch stays local on the box"
    fi
  fi
  [ "${RECURSION_ALLOW_AUTOMERGE:-0}" = "1" ] && [ "$AUTOMERGE" = "yes" ] || return 0
  local scope="${AUTOMERGE_SCOPE:-$WORKDIR}"; scope="${scope%/}"
  local outside; outside="$(git -C "$REPO_DIR" diff --name-only "origin/$def..$BRANCH" 2>/dev/null | grep -v "^$scope/" || true)"
  if [ -n "$outside" ]; then
    log "auto-merge BLOCKED — branch touches files outside $scope/:"; printf '%s\n' "$outside" >>"$LOG"
    notify "🛑 [$ID] auto-merge blocked — touched files outside $scope/. Left on $BRANCH for your review."
    escalate "auto-merge blocked: branch changed files outside automerge_scope=$scope/ — needs human review"
    return 0
  fi
  if gitr push origin "$BRANCH:$def" >>"$LOG" 2>&1; then
    log "AUTO-MERGED $BRANCH -> $def (ff-only, scope=$scope/)"; notify "🚀 [$ID] auto-merged to $def (chiron, scope-checked, ff-only)"
  else
    log "auto-merge push rejected (non-ff: $def advanced) — needs your merge"
    notify "⚠ [$ID] auto-merge needs you ($def moved since base). Review $BRANCH."
  fi
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
  git -C "$REPO_DIR" worktree remove --force "$WT" 2>/dev/null || true
  exit 0
fi

# --- VERIFY (+ retry the arm once on red, per design) ---------------------------------
PASS=0; rc=0
if verify "$WT"; then
  PASS=1
else
  rc=$?
  log "acceptance FAILED (exit $rc), attempt 1"
  # A deliberate NO-OP (rc=2 no-progress with NO implementation change) will not benefit from a
  # retry — the arm chose not to ship (0x68, overlay-0x6c both did this). Retry only a genuine
  # "tried but failed": impl files changed, or a non-no-progress failure. Saves a wasted ~1h run.
  impl_changed=$(git -C "$WT" status --porcelain -- . ":(exclude)docs" 2>/dev/null | grep -c . || true)
  if [ "$ENGINE" != "none" ] && { [ "$rc" != "2" ] || [ "${impl_changed:-0}" -gt 0 ]; }; then
    log "retry once (design: retry once then escalate)"
    run_arm "$WT" || true
    if verify "$WT"; then PASS=1; else rc=$?; fi
  else
    log "no retry: deliberate no-op (rc=$rc, impl-files-changed=${impl_changed:-0})"
  fi
fi

# --- INTEGRATE ------------------------------------------------------------------------
if [ "$PASS" = "1" ]; then
  COMMITTED=0
  git -C "$WT" add -A 2>>"$LOG" || true
  if git -C "$WT" diff --cached --quiet 2>/dev/null; then
    NOTE="passed (no file changes)"; log "acceptance green; nothing to commit (verify-only)"
  else
    git -C "$WT" -c user.name="recursion-loop" -c user.email="loop@recursion.local" \
      commit -q -m "build($ID): $GOAL

acceptance: $ACCEPTANCE (green)
engine: $ENGINE" 2>>"$LOG" || true
    NOTE="passed -> $BRANCH"; COMMITTED=1; log "committed build output to $BRANCH"
  fi
  if [ -f "$ARM_USAGE" ]; then board finish "$ID" done "$ARM_USAGE" "$NOTE"; else board finish "$ID" done - "$NOTE"; fi
  set_status passed; commit_state
  notify "✅ Recursion build passed: $ID -> $BRANCH (acceptance green). Review/merge at your pace."
  [ "$COMMITTED" = "1" ] && integrate_remote   # publish / path-scoped auto-merge (both env-fenced, off by default)
  # close the plan->build->done loop: a passed planned task flips its roadmap item [~] -> [x].
  if [ -n "$PLANNED_FROM" ]; then
    rf="${PLANNED_FROM%%:*}"; rl="${PLANNED_FROM##*:}"
    [ -f "$rf" ] && sed -i "${rl}s/^- \[~\] /- [x] /" "$rf" 2>/dev/null && log "roadmap $rf:$rl -> done"
  fi
  git -C "$REPO_DIR" worktree remove --force "$WT" 2>/dev/null || true   # branch persists for review
  log "DONE $ID passed"
else
  board finish "$ID" blocked - "acceptance failed (exit $rc)"
  set_status failed; escalate "acceptance test failed after retry" "$rc"; commit_state
  log "left worktree for inspection: $WT (branch $BRANCH)"
fi

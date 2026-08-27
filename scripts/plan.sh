#!/usr/bin/env bash
# plan.sh — turn the next roadmap item into a runnable task. The human sets DIRECTION (an ordered
# feature list); the loop mechanizes turning the next item into a task file the drainer can run.
# This keeps scope in human hands while the execution is autonomous.
#
#   plan.sh <workstream>        emit a task for the first unchecked roadmap item
#
# Roadmap file: state/roadmaps/<workstream>.md — a header of `key: value` task defaults, a blank
# line, then a checklist. Example:
#     engine: claude
#     repo: /opt/recursion
#     sshkey: ~/.ssh/id_deploy
#     workdir: apps/chiron
#     acceptance: cd apps/chiron && npm install && npm run build
#
# `automerge:` / `automerge_scope:` are NOT roadmap-grantable (esc-0001). A roadmap says what to
# build; it does not hand out default-branch write authority. Headers carrying them are dropped
# with a warning — see below.
#
#     - [x] Scaffold a minimal Next.js shell
#     - [ ] Add a landing page with a hero + CTA        <- plan.sh emits THIS, marks it [~]
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"; cd "$ROOT"
fsync_dir(){ python3 - "$1" <<'PY' >/dev/null 2>&1
import os,sys
fd=os.open(sys.argv[1],os.O_RDONLY)
try: os.fsync(fd)
finally: os.close(fd)
PY
}
PLANNER_LOCK_HELD=0; PLANNER_LOCK=""
planner_lock_acquire(){
  PLANNER_LOCK="$1"
  [ -x "$ROOT/scripts/runtime-state.py" ] \
    || { echo "plan: witnessed planner lock helper is absent" >&2; return 73; }
  python3 "$ROOT/scripts/runtime-state.py" lock-acquire "$PLANNER_LOCK" "$$" >/dev/null
}
planner_lock_release(){
  [ "$PLANNER_LOCK_HELD" = 1 ] || return 0
  if python3 "$ROOT/scripts/runtime-state.py" lock-release "$PLANNER_LOCK" "$$" >/dev/null; then
    PLANNER_LOCK_HELD=0
    return 0
  fi
  echo "plan: planner lock release failed closed: $PLANNER_LOCK" >&2
  return 74
}

if [ "${1:-}" = --complete ]; then
  PLANNED="${2:?usage: plan.sh --complete state/roadmaps/<workstream>.md:<line>}"
  case "$PLANNED" in state/roadmaps/*.md:[0-9]*) ;; *) echo "plan: invalid planned_from pointer" >&2; exit 2 ;; esac
  RM="${PLANNED%:*}"; LN="${PLANNED##*:}"; WS="$(basename "$RM" .md)"
  printf '%s' "$WS" | grep -qE '^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$' || exit 2
  [ -f "$RM" ] || { echo "plan: no roadmap for completion: $RM" >&2; exit 2; }
  mkdir -p state/.locks
  LOCK="state/.locks/planner-$WS.lock"
  planner_lock_acquire "$LOCK" \
    || { echo "plan: planner lock contended; refusing unlocked completion" >&2; exit 73; }
  PLANNER_LOCK_HELD=1
  trap 'planner_lock_release || true' EXIT
  current="$(sed -n "${LN}p" "$RM")"
  case "$current" in '- [x] '*) echo "roadmap already complete: $PLANNED"; exit 0 ;; '- [~] '*) : ;; *) echo "plan: roadmap row is not reserved: $PLANNED" >&2; exit 75 ;; esac
  tmp_rm="$(mktemp "$(dirname "$RM")/.$(basename "$RM").tmp.XXXXXX")"
  cp -p -- "$RM" "$tmp_rm"
  sed -i "${LN}s/^- \[~\] /- [x] /" "$tmp_rm"
  python3 - "$tmp_rm" <<'PY'
import os,sys
with open(sys.argv[1],'rb') as source: os.fsync(source.fileno())
PY
  mv -f -- "$tmp_rm" "$RM"
  fsync_dir "$(dirname "$RM")"
  echo "roadmap complete: $PLANNED"
  exit 0
fi

WS="${1:?usage: plan.sh <workstream>}"
printf '%s' "$WS" | grep -qE '^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$' \
  || { echo "plan: invalid workstream id" >&2; exit 2; }
RM="state/roadmaps/$WS.md"
[ -f "$RM" ] || { echo "no roadmap: $RM (create it: header of task defaults + a '- [ ]' checklist)"; exit 2; }
TASKDIR="state/tasks"; mkdir -p "$TASKDIR"

# Allocation and roadmap reservation are one critical section. The old read/allocate/write/sed
# sequence let two planners choose the same ID and checklist row. A contended lock never degrades
# to an unlocked write.
LOCKDIR="state/.locks"; mkdir -p "$LOCKDIR"
LOCK="$LOCKDIR/planner-$WS.lock"
planner_lock_acquire "$LOCK" \
  || { echo "plan: planner lock contended; refusing unlocked allocation" >&2; exit 73; }
PLANNER_LOCK_HELD=1
trap 'planner_lock_release || true' EXIT

# header defaults: read a key's value from the key:value lines above the first checklist item
hget(){ awk -v k="$1" -F': *' '/^- \[/{exit} $1==k{sub(/^[^:]+: */,"");print;exit}' "$RM"; }

# first UNCHECKED roadmap item (the goal)
GOAL_LINE="$(grep -nE '^- \[ \] ' "$RM" | head -1 || true)"
[ -n "$GOAL_LINE" ] || { echo "roadmap $WS: nothing unchecked — queue not refilled (all planned)."; exit 3; }
LN="${GOAL_LINE%%:*}"
GOAL="$(printf '%s' "$GOAL_LINE" | sed -E 's/^[0-9]+:- \[ \] //')"

# next id: <ws>-NNN (zero-padded, max existing + 1)
last="$(ls state/tasks/$WS-*.md 2>/dev/null | sed -E "s#.*/$WS-0*([0-9]+)\.md#\1#" | sort -n | tail -1 || true)"
next="$(printf '%03d' $(( ${last:-0} + 1 )))"
ID="$WS-$next"; TASK="state/tasks/$ID.md"

ENGINE="$(hget engine)";   REPO="$(hget repo)";     SSHKEY="$(hget sshkey)"
WORKDIR="$(hget workdir)"; ACC="$(hget acceptance)"; SEED="$(hget seed)"
AM="$(hget automerge)";    AMS="$(hget automerge_scope)"; MODEL="$(hget model)"
GOAL_ID="$(hget goal_id)"; DEPS="$(hget dependencies)"; ALLOWED="$(hget allowed_paths)"
NON_GOALS="$(hget non_goals)"; WORKER_CLASS="$(hget worker_class)"
GOAL_ID="${GOAL_ID:-goal-$WS}"
# The planner does not grant automerge (esc-0001). Copying the header through is how chiron-001
# and chiron-003 acquired `automerge: yes` from a roadmap edit rather than a human decision. The
# fields are read only so the drop can be announced: a header that is silently ignored looks
# exactly like a header that was honored.
if [ -n "$AM" ] || [ -n "$AMS" ]; then
  echo "plan: REFUSED automerge from $RM (automerge='$AM' automerge_scope='$AMS') — not copied into $ID; publication stays review-branch-only. Remove it from the roadmap header." >&2
fi
printf '%s' "$GOAL_ID" | grep -qE '^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$' \
  || { echo "plan: roadmap has an invalid goal_id" >&2; exit 2; }
if [ -f schemas/control-plane/v1/schema.json ] || [ -d state/goals ]; then
  [ -f "state/goals/$GOAL_ID.md" ] \
    || { echo "plan: parent goal does not exist: $GOAL_ID" >&2; exit 6; }
  [ "$(sed -n 's/^status: *//p' "state/goals/$GOAL_ID.md" | head -1)" = active ] \
    || { echo "plan: parent goal is not active: $GOAL_ID" >&2; exit 6; }
fi

tmp_task="$(mktemp "$TASKDIR/.${ID}.tmp.XXXXXX")"
{
  echo "schema_version: 1"
  echo "id: $ID"
  echo "workstream: $WS"
  echo "goal_id: $GOAL_ID"
  echo "dependencies: $DEPS"
  echo "goal: $GOAL"
  echo "engine: ${ENGINE:-claude}"
  echo "worker_class: ${WORKER_CLASS:-${ENGINE:-claude}}"
  [ -n "$REPO" ]    && echo "repo: $REPO"
  [ -n "$SSHKEY" ]  && echo "sshkey: $SSHKEY"
  [ -n "$SEED" ]    && echo "seed: $SEED"
  [ -n "$MODEL" ]   && echo "model: $MODEL"
  echo "acceptance: ${ACC:?roadmap $WS is missing an 'acceptance:' default (no gate => no autonomy)}"
  echo "workdir: ${WORKDIR:-.}"
  echo "allowed_paths: ${ALLOWED:-${WORKDIR:-.}}"
  echo "non_goals: $NON_GOALS"
  echo "autonomy: auto"
  echo "status: queued"
  echo "planned_from: $RM:$LN"
  echo
  echo "$GOAL"
  echo
  echo "(Auto-planned from the $WS roadmap. Fix the IMPLEMENTATION, not the test/fixtures. The gate"
  echo "is the acceptance command above; keep every currently-passing check green.)"
} > "$tmp_task"
python3 - "$tmp_task" <<'PY'
import os,sys
with open(sys.argv[1],'rb') as f: os.fsync(f.fileno())
PY
mv -f -- "$tmp_task" "$TASK"
fsync_dir "$TASKDIR"

# mark the roadmap item as queued ([~]) so it is not re-emitted; it flips to [x] when the task passes.
tmp_rm="$(mktemp "$(dirname "$RM")/.$(basename "$RM").tmp.XXXXXX")"
cp -p -- "$RM" "$tmp_rm"
line="$(sed -n "${LN}p" "$tmp_rm")"
case "$line" in '- [ ] '*) ;; *) rm -f -- "$tmp_rm" "$TASK"; echo "plan: roadmap row changed during reservation" >&2; exit 75 ;; esac
sed -i "${LN}s/^- \[ \] /- [~] /" "$tmp_rm"
python3 - "$tmp_rm" <<'PY'
import os,sys
with open(sys.argv[1],'rb') as f: os.fsync(f.fileno())
PY
mv -f -- "$tmp_rm" "$RM"
fsync_dir "$(dirname "$RM")"
echo "planned $ID -> $TASK"
echo "  goal: $GOAL"

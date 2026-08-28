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
GATE_COMMANDS="$(hget gate_commands)"
GOAL_ID="${GOAL_ID:-goal-$WS}"
# Phase 2 repository boundary. The frozen in-repository Chiron tree is historical residue, not a
# destination for new work. A canonical Chiron project may still be planned from /opt/chiron;
# only the legacy apps/chiron path is refused.
contains_legacy_chiron(){
  # Normalize separators, redundant ./ and trailing slashes before matching every command/path
  # field. This catches shell, Windows, and comma-separated roadmap spellings alike.
  printf '%s\n' "$1" | tr '\\' '/' | sed -E 's#/{2,}#/#g; s#(^|[[:space:]])\./#\1#g; s#/$##' \
    | grep -qiE "(^|[[:space:]\"'=/:])apps/chiron([/[:space:]\"'=,:]|$)"
}
for generated_field in "$WORKDIR" "$ALLOWED" "$ACC" "$GATE_COMMANDS" "$SEED" "$REPO" "$GOAL" "$NON_GOALS" "$ENGINE" "$MODEL" "$WORKER_CLASS" "$DEPS"; do
  if contains_legacy_chiron "$generated_field"; then
    echo "plan: REFUSED new task targeting historical apps/chiron; use the canonical Chiron project repository" >&2
    exit 6
  fi
done
# Registered projects must bind the task to the exact current source tip. Disposable planner
# fixtures intentionally have no descriptor/checkout and retain their v1 compatibility path.
SOURCE_BRANCH=""; SOURCE_SHA=""; PROJECT_CONFIG=""; REPO_CANONICAL="$REPO"
for candidate_config in state/project-config/*.json; do
  [ -f "$candidate_config" ] || continue
  project_match="$(python3 - "$candidate_config" "$REPO" <<'PY'
import json,sys
from pathlib import Path
try:
    value=json.load(open(sys.argv[1],encoding='utf-8'))
    configured_raw=value.get('repo')
    if not isinstance(configured_raw,str) or not configured_raw.strip():
        print('invalid')
    else:
        configured=Path(configured_raw).expanduser().resolve(strict=False)
        requested=Path(str(sys.argv[2] or '')).expanduser().resolve(strict=False)
        print(value.get('status','invalid') if configured == requested else 'no')
except (OSError,ValueError):
    print('invalid')
PY
)"
  case "$project_match" in active) PROJECT_CONFIG="$candidate_config"; break;; esac
done
if [ -n "$PROJECT_CONFIG" ]; then
  [ -d "${REPO:-}/.git" ] || { echo "plan: registered project checkout is unavailable; exact source SHA cannot be admitted" >&2; exit 74; }
  observed_root="$(git -C "$REPO" rev-parse --show-toplevel 2>/dev/null || true)"
  canonical_root="$(python3 - "$REPO" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
)"
  [ -n "$observed_root" ] && [ "$canonical_root" = "$observed_root" ] \
    || { echo "plan: registered project path is not the exact Git worktree root" >&2; exit 74; }
  REPO_CANONICAL="$canonical_root"
  SOURCE_BRANCH="$(python3 - "$PROJECT_CONFIG" <<'PY'
import json,sys
print(json.load(open(sys.argv[1],encoding='utf-8')).get('default_branch',''))
PY
)"
  SOURCE_SHA="$(git -C "$REPO" rev-parse --verify "refs/heads/$SOURCE_BRANCH^{commit}" 2>/dev/null || true)"
  printf '%s' "$SOURCE_SHA" | grep -qE '^[0-9a-f]{40,64}$' \
    || { echo "plan: registered project source branch is unavailable; exact source SHA cannot be admitted" >&2; exit 74; }
fi
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
  [ -n "$REPO" ]    && echo "repo: ${REPO_CANONICAL:-$REPO}"
  [ -n "$SSHKEY" ]  && echo "sshkey: $SSHKEY"
  [ -n "$SEED" ]    && echo "seed: $SEED"
  [ -n "$SOURCE_BRANCH" ] && echo "source_branch: $SOURCE_BRANCH"
  [ -n "$SOURCE_SHA" ] && echo "source_sha: $SOURCE_SHA"
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

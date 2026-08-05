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
#     automerge: yes
#     automerge_scope: apps/chiron
#
#     - [x] Scaffold a minimal Next.js shell
#     - [ ] Add a landing page with a hero + CTA        <- plan.sh emits THIS, marks it [~]
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"; cd "$ROOT"
WS="${1:?usage: plan.sh <workstream>}"
RM="state/roadmaps/$WS.md"
[ -f "$RM" ] || { echo "no roadmap: $RM (create it: header of task defaults + a '- [ ]' checklist)"; exit 2; }

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

{
  echo "id: $ID"
  echo "workstream: $WS"
  echo "goal: $GOAL"
  echo "engine: ${ENGINE:-claude}"
  [ -n "$REPO" ]    && echo "repo: $REPO"
  [ -n "$SSHKEY" ]  && echo "sshkey: $SSHKEY"
  [ -n "$SEED" ]    && echo "seed: $SEED"
  [ -n "$MODEL" ]   && echo "model: $MODEL"
  echo "acceptance: ${ACC:?roadmap $WS is missing an 'acceptance:' default (no gate => no autonomy)}"
  echo "workdir: ${WORKDIR:-.}"
  echo "autonomy: auto"
  [ -n "$AM" ]  && echo "automerge: $AM"
  [ -n "$AMS" ] && echo "automerge_scope: $AMS"
  echo "status: queued"
  echo "planned_from: $RM:$LN"
  echo
  echo "$GOAL"
  echo
  echo "(Auto-planned from the $WS roadmap. Fix the IMPLEMENTATION, not the test/fixtures. The gate"
  echo "is the acceptance command above; keep every currently-passing check green.)"
} > "$TASK"

# mark the roadmap item as queued ([~]) so it is not re-emitted; it flips to [x] when the task passes.
sed -i "${LN}s/^- \[ \] /- [~] /" "$RM"
echo "planned $ID -> $TASK"
echo "  goal: $GOAL"

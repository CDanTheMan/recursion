#!/usr/bin/env bash
# publish.sh — push the box's local branches to origin, gated by the same flags as the autonomous
# flow. This is the "enable the box to push" surface: the box pushes with its own deploy key, never
# the operator's shell. Two things:
#   1. loop/auto  -> origin  (the infra REVIEW branch; a human merges it to the default branch)
#   2. each PASSED task branch whose diff is within its automerge_scope -> ff-merged to default
#      (this discharges the pre-existing chiron-001 scaffold, which predates work.sh's
#      integrate_remote; FUTURE task work auto-merges via work.sh itself).
#
# All pushing is gated: RECURSION_ALLOW_PUSH for the branch push, RECURSION_ALLOW_AUTOMERGE for the
# ff-merge to default. Scope-checked + ff-only, exactly like work.sh integrate_remote. Never --force.
set -uo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"; cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a
KEY="${RECURSION_DEPLOY_KEY:-$HOME/.ssh/id_deploy}"
GSSH="ssh -i ${KEY/#\~/$HOME} -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"
gitp(){ GIT_SSH_COMMAND="$GSSH" git "$@"; }
field(){ sed -n "s/^$1: *//p" "$2" 2>/dev/null | head -1 | tr -d '\r'; }

[ "${RECURSION_ALLOW_PUSH:-0}" = "1" ] || { echo "publish: RECURSION_ALLOW_PUSH!=1 — nothing pushed (set it in .env)"; exit 0; }

# --branch <name> [--repo <path>] [--key <keyfile>]: push one named local branch to origin as a
# REVIEW branch, NEVER to the default branch. Optional --repo/--key push a branch in another repo
# (e.g. golden-stallion-client with its deploy key) — the universal review-branch pusher for every
# repo the loop drives. Never --force, never to default; main stays yours to merge on GitHub.
if [ "${1:-}" = "--branch" ] && [ -n "${2:-}" ]; then
  BR="$2"; RREPO="$ROOT"; RKEY="${KEY/#\~/$HOME}"; shift 2
  while [ $# -gt 0 ]; do case "$1" in
    --repo) RREPO="$2"; shift 2;;
    --key)  RKEY="${2/#\~/$HOME}"; shift 2;;
    *) shift;;
  esac; done
  RGSSH="ssh -i $RKEY -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"
  git -C "$RREPO" rev-parse --verify "$BR" >/dev/null 2>&1 || { echo "publish: no such local branch: $BR in $RREPO"; exit 2; }
  if GIT_SSH_COMMAND="$RGSSH" git -C "$RREPO" push origin "$BR:$BR" 2>&1 | tail -2; then echo "  -> pushed $BR to origin (review branch, repo=$RREPO)"; fi
  exit 0
fi

def="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')"; def="${def:-master}"
gitp fetch --prune --quiet origin 2>/dev/null || echo "publish: fetch failed (continuing on local refs)"

# 1) infra review branch --------------------------------------------------------------
if git rev-parse --verify loop/auto >/dev/null 2>&1; then
  if gitp push origin loop/auto 2>&1 | tail -1; then echo "  -> pushed loop/auto (infra review branch); merge it to $def at your pace"; fi
fi

# 2) passed, in-scope task branches -> ff-merge to default ------------------------------
shopt -s nullglob
for tf in state/tasks/*.md; do
  [ "$(field status "$tf")" = "passed" ] || continue
  [ "$(field automerge "$tf")" = "yes" ] || continue
  id="$(field id "$tf")"; br="loop/work/$id"
  git rev-parse --verify "$br" >/dev/null 2>&1 || continue
  scope="$(field automerge_scope "$tf")"; scope="${scope%/}"
  echo "task $id ($br):"
  gitp push origin "$br" 2>&1 | tail -1 && echo "  pushed $br for review"
  if [ "${RECURSION_ALLOW_AUTOMERGE:-0}" != "1" ] || [ -z "$scope" ]; then
    echo "  (automerge off or no scope — left for manual merge)"; continue
  fi
  outside="$(git diff --name-only "origin/$def..$br" 2>/dev/null | grep -v "^$scope/" || true)"
  if [ -n "$outside" ]; then
    echo "  BLOCKED — $br touches files outside $scope/:"; printf '    %s\n' $outside | head; continue
  fi
  if gitp push origin "$br:$def" 2>&1 | tail -1; then
    echo "  ✅ AUTO-MERGED $br -> $def (ff-only, scope=$scope/)"
  else
    echo "  ff-merge rejected ($def advanced since base) — needs a manual merge"
  fi
done
echo "publish: done"

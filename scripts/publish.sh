#!/usr/bin/env bash
# Review-only publisher. This is the sole push path for worker output.
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a

refuse(){ echo "publish: REFUSED — $*" >&2; exit 2; }
unpaused(){ [ ! -f "$ROOT/state/PAUSE" ] || refuse "state/PAUSE blocks publication"; }
unpaused
[ "${RECURSION_ALLOW_PUSH:-0}" = 1 ] \
  || { echo "publish: RECURSION_ALLOW_PUSH!=1 — nothing pushed (set it in .env)"; exit 0; }

canonical_branch(){
  local branch="$1"
  [[ "$branch" =~ ^loop/work/[A-Za-z0-9][A-Za-z0-9._-]{0,127}$ ]] \
    || refuse "only canonical loop/work/<task-id> review refs are accepted: $branch"
  git check-ref-format "refs/heads/$branch" >/dev/null 2>&1 \
    || refuse "invalid branch ref: $branch"
}

registry_row(){
  local repo="$1" want path
  want="$(realpath -e "$repo" 2>/dev/null)" || return 1
  while IFS=$'\t' read -r project path remote branch key roadmap topic status rest; do
    case "$project" in ""|'#'*) continue;; esac
    [ "$status" = active ] || continue
    [ "$(realpath -e "$path" 2>/dev/null || true)" = "$want" ] || continue
    printf '%s\t%s\t%s\n' "$branch" "$key" "$project"
    return 0
  done < "$ROOT/state/portfolio.tsv"
  return 1
}

publish_one(){
  local branch="$1" repo="$2" key="${3:-}" row def registry_key project
  local src_ref dst_ref id status remote_def
  canonical_branch "$branch"
  repo="$(realpath -e "$repo" 2>/dev/null)" || refuse "repository does not exist: $repo"
  row="$(registry_row "$repo")" || refuse "repository is not active in state/portfolio.tsv: $repo"
  IFS=$'\t' read -r def registry_key project <<<"$row"
  [ -n "$def" ] || refuse "registered default branch is empty for $project"
  src_ref="refs/heads/$branch"; dst_ref="$src_ref"
  [ "$dst_ref" != "refs/heads/$def" ] \
    || refuse "resolved destination is the registered default branch: $def"
  git -C "$repo" show-ref --verify --quiet "$src_ref" \
    || refuse "no direct local branch $src_ref in $repo"
  ! git -C "$repo" symbolic-ref -q "$src_ref" >/dev/null 2>&1 \
    || refuse "symbolic branch refs are not publishable: $branch"

  remote_def="$(git -C "$repo" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)"
  [ -z "$remote_def" ] || [ "$remote_def" = "$def" ] \
    || refuse "registry default $def disagrees with origin/HEAD $remote_def"

  id="${branch#loop/work/}"
  [ -f "$ROOT/state/tasks/$id.md" ] || refuse "no canonical task for branch $branch"
  status="$(sed -n 's/^status: *//p' "$ROOT/state/tasks/$id.md" | head -1 | tr -d '\r')"
  [ "$status" = passed ] || refuse "task $id is not passed (status=${status:-missing})"

  [ -n "$key" ] || key="$registry_key"
  case "$key" in ""|-) refuse "publisher key is not configured for $project";; esac
  key="${key/#\~/$HOME}"
  [ -f "$key" ] || refuse "publisher key file is missing for $project"
  unpaused
  local gssh="ssh -i $key -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"
  if GIT_SSH_COMMAND="$gssh" git -C "$repo" push origin "$src_ref:$dst_ref"; then
    echo "publish: pushed $branch for review (project=$project); default $def unchanged"
  else
    refuse "review-branch push failed for $branch"
  fi
}

if [ "${1:-}" = --branch ]; then
  [ $# -ge 2 ] || refuse "--branch requires a value"
  BRANCH="$2"; REPO="$ROOT"; KEY=""; shift 2
  while [ $# -gt 0 ]; do
    case "$1" in
      --repo) [ $# -ge 2 ] || refuse "--repo requires a value"; REPO="$2"; shift 2;;
      --key) [ $# -ge 2 ] || refuse "--key requires a value"; KEY="$2"; shift 2;;
      *) refuse "unknown option: $1";;
    esac
  done
  publish_one "$BRANCH" "$REPO" "$KEY"
  exit 0
fi
[ $# -eq 0 ] || refuse "use --branch loop/work/<task-id> [--repo path] [--key path]"

# Bulk publication is still review-only. There is intentionally no default-branch merge path.
shopt -s nullglob
for task in state/tasks/*.md; do
  [ "$(sed -n 's/^status: *//p' "$task" | head -1)" = passed ] || continue
  id="$(sed -n 's/^id: *//p' "$task" | head -1)"
  repo="$(sed -n 's/^repo: *//p' "$task" | head -1)"; repo="${repo:-$ROOT}"
  branch="loop/work/$id"
  git -C "$repo" show-ref --verify --quiet "refs/heads/$branch" || continue
  unpaused
  publish_one "$branch" "$repo" ""
done
echo "publish: review branches complete"

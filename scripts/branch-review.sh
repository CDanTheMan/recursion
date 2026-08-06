#!/usr/bin/env bash
# branch-review.sh — the "what's waiting for your review" section of the daily digest.
# Enumerates the loop's review branches across every tracked repo, their merge status against the
# protected default branch, whether they are PUSHED (reviewable on GitHub) or still local, and a
# recommended review+merge order. The loop pushes branches; it NEVER merges main — you do, on GitHub.
#
# Read-only: fetch + inspect only. Emits markdown to stdout for the brief to include.
set -uo pipefail
HOME="${HOME:-/root}"

# repo rows: name|path|sshkey  (empty sshkey => default key). GSC needs its deploy key to fetch.
REPOS=(
  "recursion|/opt/recursion|"
  "golden-stallion-client|/opt/golden-stallion-client|$HOME/.ssh/gsc_deploy"
)

gitfetch(){ # $1=path $2=key
  if [ -n "$2" ]; then
    GIT_SSH_COMMAND="ssh -i $2 -o IdentitiesOnly=yes -o BatchMode=yes" git -C "$1" fetch -q --prune origin 2>/dev/null || true
  else
    git -C "$1" fetch -q --prune origin 2>/dev/null || true
  fi
}

echo "## 🔀 Review branches — you merge on GitHub (the loop only pushes)"
echo ""
GRAND_OPEN=0
for entry in "${REPOS[@]}"; do
  IFS='|' read -r name path key <<<"$entry"
  [ -d "$path/.git" ] || continue
  gitfetch "$path" "$key"
  def="$(git -C "$path" symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"; def="${def:-main}"
  # all loop/* refs, remote (reviewable) and local (not yet pushed), deduped to branch names
  mapfile -t brs < <(git -C "$path" for-each-ref --format='%(refname:short)' \
      'refs/remotes/origin/loop' 'refs/heads/loop' 2>/dev/null | sed 's#^origin/##' | sort -u)
  [ "${#brs[@]}" -eq 0 ] && continue

  # build sortable rows: <sortkey>\t<line>   (open first, then oldest-first within each group)
  rows=()
  for br in "${brs[@]}"; do
    onorigin=0; git -C "$path" rev-parse --verify -q "origin/$br" >/dev/null 2>&1 && onorigin=1
    ref="origin/$br"; [ "$onorigin" -eq 1 ] || ref="$br"
    tip="$(git -C "$path" rev-parse --short "$ref" 2>/dev/null)"
    subj="$(git -C "$path" log -1 --format='%s' "$ref" 2>/dev/null | cut -c1-72)"
    ts="$(git -C "$path" log -1 --format='%ct' "$ref" 2>/dev/null || echo 0)"
    ago="$(git -C "$path" log -1 --format='%cr' "$ref" 2>/dev/null)"
    if git -C "$path" merge-base --is-ancestor "$ref" "origin/$def" 2>/dev/null; then
      grp=2; tag="✅ merged (prunable)"
    elif [ "$onorigin" -eq 1 ]; then
      grp=0; tag="🟡 OPEN — review on GitHub"; GRAND_OPEN=$((GRAND_OPEN+1))
    else
      grp=1; tag="⚪ local only (not pushed yet — grant write key)"; GRAND_OPEN=$((GRAND_OPEN+1))
    fi
    rows+=("${grp} ${ts}	- [$tag] \`$br\` ($tip, $ago) — $subj")
  done
  echo "### $name"
  printf '%s\n' "${rows[@]}" | sort -k1,1n -k2,2n | cut -f2-
  echo ""
done
if [ "$GRAND_OPEN" -eq 0 ]; then
  echo "_Nothing waiting — no open review branches._"
else
  echo "**$GRAND_OPEN branch(es) awaiting your review.** Recommended order: top-to-bottom within each repo (oldest-first; a dep lands before what builds on it)."
fi

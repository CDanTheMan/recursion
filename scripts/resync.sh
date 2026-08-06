#!/usr/bin/env bash
# resync.sh — prove the portfolio is CURRENT before anything builds on it.
#
# WHY THIS EXISTS. Every repo the loop touches is reached over git with a per-repo deploy key,
# and until now that key was known only to whoever typed the command. Two failures follow, and
# both were observed on this box rather than imagined:
#
#  1. A git remote command run WITHOUT a usable key does not fail in a way callers notice.
#     `git ls-remote` prints NOTHING, and the caller reads that as "this repo has no branches".
#     An auth failure is indistinguishable from a true empty result unless someone decides, in
#     advance, that empty is a FAULT. This script decides that. (Observed 2026-08-06: an
#     ls-remote run with the wrong key name made five merged review branches look pruned-and-lost.)
#
#  2. work.sh fetched origin before creating a worktree and, on failure, logged
#     "fetch skipped/failed — building on local base" and carried on. That is the expensive one.
#     The arm then builds on a STALE base, the acceptance gate passes (it is testing the old
#     tree), the branch is published, and merging it REVERTS whatever Lucas fixed upstream in the
#     meantime. Silent staleness is how reviewed fixes get un-fixed — which is exactly the risk
#     Lucas named: "in case I resolve any bugs that are lost in previously shipped code".
#
# So freshness is a PRECONDITION, not best effort. If this cannot PROVE a repo is current with
# origin, the task does not start — it escalates to a human.
#
#   resync.sh status [--all]        one line per repo: auth, drift, dirt, unpushed work
#   resync.sh sync [project ...]    fetch + fast-forward the default branch; escalate the rest
#   resync.sh check <project|path>  dispatch precondition. 0 fresh · 3 cannot prove · 4 needs a human
#   resync.sh key <project|path>    the deploy key for this repo (single source of truth)
#   resync.sh list [--all]          registry rows
#
# EXIT CODES ARE THE INTERFACE. 3 means "the answer is unknown" and 4 means "the answer is no".
# Collapsing those two is what produced failure (1) above: an unknown that reads as a clean no.
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
REG="${RECURSION_PORTFOLIO:-$ROOT/state/portfolio.tsv}"
TASKCTL="$ROOT/scripts/taskctl.sh"
NOTIFY="$ROOT/scripts/notify.sh"
CMD="${1:-status}"; shift 2>/dev/null || true

# --- registry ---------------------------------------------------------------------------
# TSV, not JSON: the whole control plane is shell, and a registry you can awk/grep/diff without
# a parser is a registry that still works when python is the thing that is broken.
# columns: project  path  remote  branch  sshkey  roadmap  topic  status
reg_rows(){ [ -f "$REG" ] || return 0; awk -F'\t' 'NF>=8 && $1 !~ /^#/ && $1 != ""' "$REG"; }
reg_active(){ reg_rows | awk -F'\t' '$8=="active"'; }
reg_find(){ reg_rows | awk -F'\t' -v q="$1" '$1==q || $2==q {print; exit}'; }

# Every field read goes through here so a short/ragged row cannot silently yield "".
fld(){ printf '%s' "$1" | cut -f"$2"; }

# --- git with the right key, always -------------------------------------------------------
gitk(){ # gitk <path> <key> <git args...>
  local p="$1" k="${2:-}"; shift 2
  k="${k/#\~/$HOME}"
  if [ -n "$k" ] && [ "$k" != "-" ] && [ -f "$k" ]; then
    GIT_SSH_COMMAND="ssh -i $k -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15" \
      git -C "$p" "$@"
  else
    git -C "$p" "$@"
  fi
}

# --- escalation: a drift a human must settle is an ITEM, not a log line --------------------
# Keys are stable and carry no timestamp, so the same drift seen ten times is one escalation
# with a sighting count — the dedup contract from the task-graph branch.
esc(){ # esc <key> <title> [pointer] [project]
  [ -x "$TASKCTL" ] || return 0
  local out
  out="$(RECURSION_ROOT="$ROOT" bash "$TASKCTL" esc-record "$1" "$2" portfolio "${3:-}" 2>/dev/null)"
  case "$out" in
    NEW*) [ -x "$NOTIFY" ] && bash "$NOTIFY" --project "${4:-}" "🔔 portfolio: $2" >/dev/null 2>&1 || true ;;
    *) : ;;   # DUP — already open. Do not re-notify; that was the four-times bug.
  esac
}

# --- inspect one repo ---------------------------------------------------------------------
# Sets: R_AUTH R_REFS R_BEHIND R_AHEAD R_DIRTY R_UNPUSHED R_VERDICT R_WHY
inspect(){ # inspect <path> <key> <default-branch>
  local p="$1" k="$2" d="$3" out rc counts
  R_AUTH=no R_REFS=0 R_BEHIND=0 R_AHEAD=0 R_DIRTY=0 R_UNPUSHED=0 R_VERDICT=FAULT R_WHY=""

  if [ ! -d "$p/.git" ]; then R_WHY="not a git repo: $p"; return 3; fi

  # ★ THE PROBE. Two independent ways to be wrong, both checked:
  #   a non-zero exit (obvious), and a ZERO-length ref list (the silent one).
  out="$(gitk "$p" "$k" ls-remote --heads origin 2>/dev/null)"; rc=$?
  if [ "$rc" -ne 0 ]; then
    R_WHY="cannot reach origin (git exited $rc) — wrong/absent deploy key, or the remote is down"
    return 3
  fi
  if [ -z "${out//[[:space:]]/}" ]; then
    # A repo that HAS a remote and answers with no heads at all is not an empty repo, it is a
    # failed probe wearing an empty result's clothes. Refusing to call this "clean" is the point.
    R_WHY="origin answered with ZERO refs — treating as a failed probe, not as an empty remote"
    return 3
  fi
  R_AUTH=yes; R_REFS="$(printf '%s\n' "$out" | wc -l | tr -d ' ')"

  # Fetch, so every comparison below is against the REAL remote tip and not a stale
  # remote-tracking ref. Comparing to a stale origin/<def> is the same bug in a nicer suit.
  if ! gitk "$p" "$k" fetch --prune --quiet origin >/dev/null 2>&1; then
    R_WHY="ls-remote succeeded but fetch failed — the remote-tracking refs are stale"
    return 3
  fi
  if ! git -C "$p" rev-parse --verify --quiet "origin/$d" >/dev/null 2>&1; then
    R_WHY="origin/$d does not exist (is '$d' really the default branch?)"
    return 3
  fi

  [ -n "$(git -C "$p" status --porcelain 2>/dev/null)" ] && R_DIRTY=1

  if git -C "$p" rev-parse --verify --quiet "$d" >/dev/null 2>&1; then
    counts="$(git -C "$p" rev-list --left-right --count "origin/$d...$d" 2>/dev/null)"
    R_BEHIND="$(printf '%s' "$counts" | cut -f1)"; R_AHEAD="$(printf '%s' "$counts" | cut -f2)"
    R_BEHIND="${R_BEHIND:-0}"; R_AHEAD="${R_AHEAD:-0}"
  fi

  # Local branches holding commits that exist on no remote branch at all. This is the
  # "it existed only on one disk" class — the delegation-design.md near-miss.
  R_UNPUSHED="$(git -C "$p" for-each-ref --format='%(refname:short)' refs/heads \
                 | while read -r b; do
                     [ -n "$(git -C "$p" rev-list --count "$b" --not --remotes 2>/dev/null | grep -v '^0$')" ] && echo "$b"
                   done | wc -l | tr -d ' ')"
  R_UNPUSHED="${R_UNPUSHED:-0}"

  if   [ "$R_AHEAD" -gt 0 ] && [ "$R_BEHIND" -gt 0 ]; then
    R_VERDICT=DIVERGED; R_WHY="$d has diverged from origin/$d (+$R_AHEAD local, -$R_BEHIND remote) — a human must reconcile"; return 4
  elif [ "$R_BEHIND" -gt 0 ]; then
    R_VERDICT=BEHIND;   R_WHY="$d is $R_BEHIND behind origin/$d (fast-forwardable)"; return 0
  elif [ "$R_AHEAD" -gt 0 ]; then
    R_VERDICT=UNPUSHED; R_WHY="$d has $R_AHEAD commit(s) that exist only on this box"; return 0
  else
    R_VERDICT=OK;       R_WHY="current with origin/$d"; return 0
  fi
}

# --- fast-forward the default branch ------------------------------------------------------
# Never a merge commit, never a rebase, never a force. If it is not a fast-forward we stop and
# escalate: reconciling divergence is a human's call, and guessing at it destroys work.
ff_default(){ # ff_default <path> <def> <behind> <ahead>
  local p="$1" d="$2" beh="$3" ah="$4" cur old new
  [ "$beh" -gt 0 ] && [ "$ah" -eq 0 ] || return 0
  cur="$(git -C "$p" rev-parse --abbrev-ref HEAD 2>/dev/null)"
  if [ "$cur" = "$d" ]; then
    git -C "$p" merge --ff-only "origin/$d" >/dev/null 2>&1 || return 1
  else
    # compare-and-swap: refuses if $d moved under us between inspect and now.
    old="$(git -C "$p" rev-parse "$d")"; new="$(git -C "$p" rev-parse "origin/$d")"
    git -C "$p" update-ref "refs/heads/$d" "$new" "$old" >/dev/null 2>&1 || return 1
  fi
  return 0
}

row_for(){ # row_for <query> -> echoes the row, or fails
  local row; row="$(reg_find "$1")"
  [ -n "$row" ] || { echo "resync: '$1' is not in $REG" >&2; return 1; }
  printf '%s' "$row"
}

case "$CMD" in

list)
  if [ "${1:-}" = "--all" ]; then reg_rows; else reg_active; fi ;;

key)
  Q="${1:?usage: resync.sh key <project|path>}"
  row="$(row_for "$Q")" || exit 2
  k="$(fld "$row" 5)"; [ -n "$k" ] && [ "$k" != "-" ] || exit 2
  printf '%s\n' "${k/#\~/$HOME}" ;;

status)
  ALL=0; [ "${1:-}" = "--all" ] && ALL=1
  printf '%-26s %-6s %-8s %-22s %-6s %-7s %s\n' PROJECT AUTH BRANCH DRIFT DIRTY UNPUSH NOTE
  bad=0
  while IFS= read -r row; do
    [ -n "$row" ] || continue
    pr="$(fld "$row" 1)"; p="$(fld "$row" 2)"; d="$(fld "$row" 4)"; k="$(fld "$row" 5)"
    inspect "$p" "$k" "$d"; rc=$?
    [ "$rc" -ne 0 ] && bad=$((bad+1))
    drift="$R_VERDICT"
    if [ "$R_BEHIND" != "0" ] || [ "$R_AHEAD" != "0" ]; then drift="$R_VERDICT(-$R_BEHIND/+$R_AHEAD)"; fi
    # UNPUSH is the third thing that must never be silent (with drift and dirt): local
    # branches holding commits that exist on no remote — the "it lived on one disk" class.
    printf '%-26s %-6s %-8s %-22s %-6s %-7s %s\n' \
      "$pr" "$R_AUTH" "$d" "$drift" "$([ "$R_DIRTY" = 1 ] && echo yes || echo no)" "$R_UNPUSHED" "$R_WHY"
  done < <(if [ "$ALL" = 1 ]; then reg_rows; else reg_active; fi)
  [ "$bad" -eq 0 ] || exit 1 ;;

sync)
  # Bring every registered repo (or the named ones) up to origin, and turn everything that a
  # fast-forward CANNOT fix into an escalation. A silent "couldn't sync" is the whole problem.
  if [ "$#" -gt 0 ]; then
    rows=""; for q in "$@"; do r="$(row_for "$q")" || exit 2; rows="$rows$r"$'\n'; done
  else rows="$(reg_active)"; fi
  fails=0
  while IFS= read -r row; do
    [ -n "$row" ] || continue
    pr="$(fld "$row" 1)"; p="$(fld "$row" 2)"; d="$(fld "$row" 4)"; k="$(fld "$row" 5)"
    inspect "$p" "$k" "$d"; rc=$?
    case "$rc" in
      3) echo "FAULT     $pr — $R_WHY"; fails=$((fails+1))
         esc "resync-auth-$pr" "$pr: cannot prove it is current with origin — $R_WHY" "$p" "$pr"; continue ;;
      4) echo "DIVERGED  $pr — $R_WHY"; fails=$((fails+1))
         esc "resync-diverged-$pr" "$pr: $d has diverged from origin — reconcile before more work lands on it" "$p" "$pr"; continue ;;
    esac
    if [ "$R_BEHIND" -gt 0 ]; then
      if ff_default "$p" "$d" "$R_BEHIND" "$R_AHEAD"; then echo "FF        $pr — $d +$R_BEHIND"
      else echo "FF-FAILED $pr — $d could not fast-forward"; fails=$((fails+1))
           esc "resync-ff-$pr" "$pr: $d is behind origin but would not fast-forward" "$p" "$pr"; continue; fi
    else echo "OK        $pr — $R_WHY"; fi
    # These do not block a build (the arm works in an isolated worktree off origin/<def>), but
    # they are work that exists in exactly one place, so they are never left silent.
    [ "$R_AHEAD"    -gt 0 ] && esc "resync-unpushed-$pr" "$pr: $R_AHEAD commit(s) on $d exist only on this box" "$p" "$pr"
    [ "$R_UNPUSHED" -gt 0 ] && esc "resync-localonly-$pr" "$pr: $R_UNPUSHED local branch(es) hold commits on no remote" "$p" "$pr"
    [ "$R_DIRTY"    = 1   ] && esc "resync-dirty-$pr" "$pr: uncommitted changes in the working tree" "$p" "$pr"
  done <<< "$rows"
  [ "$fails" -eq 0 ] || exit 1 ;;

check)
  # THE DISPATCH PRECONDITION. work.sh calls this before it builds anything.
  Q="${1:?usage: resync.sh check <project|path>}"
  row="$(reg_find "$Q")"
  if [ -z "$row" ]; then
    # An unregistered repo is not a pass. Nothing knows its key or its default branch, so
    # nothing can prove it is current — which is the definition of exit 3 here.
    echo "unregistered repo '$Q' — add it to ${REG#$ROOT/} before dispatching work at it"; exit 3
  fi
  pr="$(fld "$row" 1)"; p="$(fld "$row" 2)"; d="$(fld "$row" 4)"; k="$(fld "$row" 5)"
  st="$(fld "$row" 8)"
  [ "$st" = "active" ] || { echo "$pr is status=$st in the registry — not dispatchable"; exit 4; }
  inspect "$p" "$k" "$d"; rc=$?
  case "$rc" in
    3) echo "CANNOT PROVE FRESH: $R_WHY"; exit 3 ;;
    4) echo "NEEDS A HUMAN: $R_WHY"; exit 4 ;;
  esac
  echo "$pr fresh: origin/$d @ $(git -C "$p" rev-parse --short "origin/$d") ($R_REFS refs, $R_VERDICT)" ;;

*) sed -n '24,30p' "$0"; exit 2 ;;
esac

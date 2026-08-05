#!/usr/bin/env bash
# board-summary.sh — a COMPACT, re-derived view of the build-loop (delegation brain) for
# the supervisor's ledger and the operator CLI. This is what closes the self-awareness gap:
# loop/supervisor/run.sh feeds ANCHOR/DECISIONS/projects/INBOX but was BLIND to the task
# queue, so the brief/heartbeat could not say "what's building". This adds that, summarized.
#
# Design rule (CLAUDE.md "Bounded output"): counts + the tasks that NEED A HUMAN (running now,
# escalated, awaiting review) — NOT a full dump of every queued body. Ground truth is
# re-derived from state/tasks/*.md and the loop/work/* branches every call (carry no state).
#
#   board-summary.sh            human/CLI view (same content, plain)
#   board-summary.sh --ledger   same, framed for the supervisor prompt
set -uo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
field(){ sed -n "s/^$1: *//p" "$2" 2>/dev/null | head -1 | tr -d '\r'; }

shopt -s nullglob
FILES=(state/tasks/*.md)

# --- tally + bucket in one pass ----------------------------------------------------
declare -A CNT
running=(); escalated=(); failed=(); passed=(); queued=(); blocked=(); moot=(); repos=()
total=0
for f in "${FILES[@]}"; do
  id="$(field id "$f")"; [ -n "$id" ] || continue      # a task file has an id: line
  st="$(field status "$f")"; ws="$(field workstream "$f")"; en="$(field engine "$f")"
  goal="$(field goal "$f")"; repo="$(field repo "$f")"; repo="${repo:-$ROOT}"
  total=$((total+1)); CNT["$st"]=$(( ${CNT["$st"]:-0} + 1 ))
  line="$(printf '%-18s [%s] %s' "$id" "${en:-?}" "${goal:-$ws}")"
  case "$st" in
    running)   running+=("$line") ;;
    escalated) escalated+=("$line") ;;
    failed)    failed+=("$line") ;;
    passed)    passed+=("$id") ;;
    queued)    queued+=("$id") ;;
    blocked)   blocked+=("$(printf '%-18s %s' "$id" "$(field blocked_on "$f")")") ;;
    moot)      moot+=("$id") ;;
    resolved)  moot+=("$id (resolved)") ;;
  esac
  # remember distinct repos so we can list built (loop/work) branches awaiting review
  case " ${repos[*]-} " in *" $repo "*) : ;; *) repos+=("$repo") ;; esac
done

emit(){
  echo "BUILD-LOOP (delegation brain) — re-derived $(date -u +%FT%TZ)"
  if [ "$total" -eq 0 ]; then echo "  (no tasks in state/tasks/)"; return; fi
  local parts="$total total"
  for k in queued running passed escalated failed blocked moot resolved; do
    [ -n "${CNT[$k]:-}" ] && parts="$parts · ${CNT[$k]} $k"
  done
  echo "  tasks: $parts"

  if [ "${#running[@]}" -gt 0 ]; then
    echo "  RUNNING NOW:"; printf '    %s\n' "${running[@]}"
  fi
  if [ "$(( ${#escalated[@]} + ${#failed[@]} ))" -gt 0 ]; then
    echo "  NEEDS A DECISION (escalated/failed — see INBOX):"
    [ "${#escalated[@]}" -gt 0 ] && printf '    %s\n' "${escalated[@]}"
    [ "${#failed[@]}" -gt 0 ]    && printf '    %s\n' "${failed[@]}"
  fi
  if [ "${#blocked[@]}" -gt 0 ]; then
    echo "  BLOCKED (waiting on a prerequisite — will not run):"; printf '    %s\n' "${blocked[@]}"
  fi

  # awaiting review = a loop/work/<id> branch that actually CARRIES A BUILD (commits ahead of
  # base). Reading git directly (not task status) catches drift; the ahead>0 test excludes a
  # failed/running task's empty base-only branch, which status alone would not.
  local shown=0
  for r in ${repos[*]-}; do
    base="$(git -C "$r" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
    [ -n "$base" ] || base="$(git -C "$r" rev-parse --abbrev-ref HEAD 2>/dev/null)"
    br=""
    while read -r ref; do
      [ -n "$ref" ] || continue
      ahead="$(git -C "$r" rev-list --count "${base}..${ref}" 2>/dev/null || echo 0)"
      [ "${ahead:-0}" -gt 0 ] || continue          # base-only branch = nothing built yet
      br="${br:+$br }${ref#loop/work/} (+$ahead)"
    done < <(git -C "$r" for-each-ref --format='%(refname:short)' refs/heads/loop/work 2>/dev/null)
    [ -n "$br" ] || continue
    [ "$shown" -eq 0 ] && { echo "  AWAITING REVIEW (built on loop/work/*, NOT merged — box has read-only key):"; shown=1; }
    printf '    %s: %s\n' "$r" "$br"
  done
  [ "$shown" -eq 1 ] && echo "    review: git fetch <repo>; git log loop/work/<id>"

  [ "${#queued[@]}" -gt 0 ] && echo "  queued: ${queued[*]}"
  [ "${#passed[@]}" -gt 0 ] && echo "  passed: ${passed[*]}"
  [ "${#moot[@]}" -gt 0 ]   && echo "  moot (already implemented, no work): ${moot[*]}"
}

if [ "${1:-}" = "--ledger" ]; then
  echo "===== BUILD-LOOP STATUS (what the loop is building — re-derived this run) ====="
  emit
else
  emit
fi
exit 0

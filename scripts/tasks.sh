#!/usr/bin/env bash
# tasks.sh — list the build-loop task queue (delegation-design.md task model).
#   tasks.sh            all tasks
#   tasks.sh queued     only tasks in a given status
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
FILTER="${1:-}"
field(){ sed -n "s/^$1: *//p" "$2" | head -1 | tr -d '\r'; }

shopt -s nullglob
FILES=(state/tasks/*.md)
# drop README/non-task files (a task has an 'id:' line)
printf '%-16s %-14s %-9s %-10s %s\n' ID WORKSTREAM ENGINE STATUS GOAL
printf '%-16s %-14s %-9s %-10s %s\n' "----------------" "--------------" "---------" "----------" "----"
n=0
for f in "${FILES[@]}"; do
  id="$(field id "$f")"; [ -n "$id" ] || continue
  st="$(field status "$f")"
  [ -n "$FILTER" ] && [ "$st" != "$FILTER" ] && continue
  printf '%-16s %-14s %-9s %-10s %s\n' \
    "$id" "$(field workstream "$f")" "$(field engine "$f")" "$st" "$(field goal "$f")"
  n=$((n+1))
done
[ "$n" -eq 0 ] && echo "(no tasks${FILTER:+ with status=$FILTER})"
exit 0

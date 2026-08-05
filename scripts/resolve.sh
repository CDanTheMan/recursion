#!/usr/bin/env bash
# resolve.sh — close/annotate a build-loop escalation from the operator side. This is the missing
# half of the escalation loop: pings were one-way and INBOX items never closed, so a Telegram
# reply had nowhere to land (there is no reply<->item correlation — one DM stream). Now:
#   recursion resolve <id> ["note"]     -> stamp a dated RESOLVED note into INBOX, set the task
#                                          status to `resolved`, and confirm on Telegram.
#   recursion requeue <id> ["note"]     -> re-open a task for another run (status -> queued).
# Both are HUMAN-driven (you, or the gateway agent acting on your explicit instruction). They do
# not run an arm; the queue-drainer / `recursion work <id>` does that.
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

MODE="resolve"
case "${1:-}" in
  --requeue) MODE="requeue"; shift ;;
esac
ID="${1:?usage: resolve.sh [--requeue] <task-id> [note]}"; shift || true
NOTE="${*:-}"
TASK="state/tasks/$ID.md"
TS="$(date -u +%FT%TZ)"
notify(){ [ "${RECURSION_NO_NOTIFY:-0}" = "1" ] && return 0; bash "$ROOT/scripts/notify.sh" "$@" >/dev/null 2>&1 || true; }

if [ "$MODE" = "requeue" ]; then
  [ -f "$TASK" ] || { echo "no such task: $TASK"; exit 2; }
  sed -i 's/^status: .*/status: queued/' "$TASK"
  sed -i '/^resolved:/d;/^blocked_on:/d' "$TASK"
  { echo; echo "## REQUEUED $TS — $ID"; [ -n "$NOTE" ] && echo "$NOTE"; } >> state/INBOX.md
  echo "requeued $ID (status -> queued). Next drainer / \`recursion work $ID\` will run it."
  notify "♻ requeued $ID${NOTE:+: $NOTE}"
  exit 0
fi

# resolve
{ echo; echo "## RESOLVED $TS — $ID"; echo "${NOTE:-resolved by operator}"; } >> state/INBOX.md
if [ -f "$TASK" ]; then
  sed -i 's/^status: .*/status: resolved/' "$TASK"
  grep -q '^blocked_on:' "$TASK" && sed -i '/^blocked_on:/d' "$TASK" || true
  echo "resolved $ID (task status -> resolved; note appended to INBOX)."
else
  echo "resolved $ID (no task file; note appended to INBOX — escalation closed)."
fi
notify "✅ resolved $ID${NOTE:+: $NOTE}"

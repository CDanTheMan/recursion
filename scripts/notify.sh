#!/usr/bin/env bash
# notify.sh — send to Telegram, into the RIGHT forum topic.
#
# Everything used to land in one stream, so a GSC gate result, a chiron build and a portfolio
# escalation were interleaved in the order they happened and had to be told apart by reading
# them. The Cockpit (-100…) is a forum, so each project gets a topic and each message goes to
# the topic that owns it. Routing is the whole feature: a cockpit whose messages all arrive in
# one channel is the thing it replaces.
#
# Usage:
#   notify.sh "message"                      -> home topic
#   notify.sh --project <name|repo-path> "…" -> that project's topic (registry lookup)
#   notify.sh --thread <id> "…"              -> an explicit thread
#   notify.sh [--project …] -f /path/to/file -> body from a file
#
# ★ THE TOKEN NEVER LEAVES THIS FILE. It is only ever interpolated into a URL held in a local
# variable, never echoed, never logged, never put in an error message, and no `set -x` may run
# with it in scope. curl's own errors can include the URL it was given, so stderr from the token
# path is discarded and a redacted line is printed instead. scripts/tests/telegram-routing.test.sh
# runs this file with a sentinel token and greps EVERYTHING it emits for it.
set -euo pipefail

# ★ THE FIXTURE-LEAK GUARD, and it is load-bearing. Tests run the REAL notify.sh against
# disposable roots, and `hermes send` uses the GATEWAY's credentials (~/.hermes), not this repo's
# .env — so a fixture with an empty .env does NOT stop delivery. Every escalation a test fixture
# raised went to Lucas for real. Observed 2026-08-06: two live pings about repos named "diverged"
# and "unreachable", which are resync.test.sh fixtures, indistinguishable in the notification
# from a genuine portfolio failure. work.sh honoured RECURSION_NO_NOTIFY in its own wrapper;
# every script that calls notify.sh directly (resync.sh, assist.sh, taskctl.sh) did not, and the
# guard has to live HERE because this is the one place they all pass through.
[ "${RECURSION_NO_NOTIFY:-0}" = "1" ] && exit 0

ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
[ -f "$ROOT/.env" ] && { set -a; . "$ROOT/.env"; set +a; }

PROJECT=""; THREAD=""; FILE=""; MSG=""
while [ $# -gt 0 ]; do
  case "$1" in
    --project) PROJECT="${2:-}"; shift 2 ;;
    --thread)  THREAD="${2:-}";  shift 2 ;;
    -f)        FILE="${2:-}";    shift 2 ;;
    *)         MSG="$1";         shift   ;;
  esac
done

# The cockpit chat. RECURSION_TELEGRAM_CHAT is the forum supergroup; TELEGRAM_CHAT_ID stays the
# fallback so nothing that worked before this change stops working.
CHAT="${RECURSION_TELEGRAM_CHAT:-${TELEGRAM_CHAT_ID:-}}"
HOME_THREAD="${RECURSION_TELEGRAM_HOME_THREAD:-}"
REG="${RECURSION_PORTFOLIO:-$ROOT/state/portfolio.tsv}"

# --- resolve the topic --------------------------------------------------------------------
# A project with no topic yet routes HOME rather than to a malformed target. Silently dropping
# the message would be the worst option available: the alert exists to be seen.
if [ -z "$THREAD" ] && [ -n "$PROJECT" ] && [ -f "$REG" ]; then
  THREAD="$(awk -F'\t' -v q="$PROJECT" '$1 !~ /^#/ && NF>=8 && ($1==q || $2==q) {print $7; exit}' "$REG")"
  [ "$THREAD" = "-" ] && THREAD=""
fi
[ -z "$THREAD" ] && THREAD="$HOME_THREAD"

# --- preferred path: hermes send (reuses the gateway's creds; no LLM, no token here at all) ---
if command -v hermes >/dev/null 2>&1; then
  TARGET="telegram"
  if [ -n "$CHAT" ]; then
    TARGET="telegram:$CHAT"
    [ -n "$THREAD" ] && TARGET="telegram:$CHAT:$THREAD"
  fi
  if [ -n "$FILE" ]; then
    hermes send -t "$TARGET" -f "$FILE" -q && exit 0 || true
  else
    hermes send -t "$TARGET" "$MSG" -q && exit 0 || true
  fi
fi

# --- fallback: raw Telegram API ---------------------------------------------------------------
[ -z "${TELEGRAM_BOT_TOKEN:-}" ] && exit 0
[ -z "$CHAT" ] && exit 0
if [ -n "$FILE" ]; then MSG="$(head -c 3800 "$FILE")"; fi

# message_thread_id is what puts a message in a forum topic; without it every message lands in
# the group's General topic, which is the un-routed behaviour this file exists to replace.
set +x
if ! curl -sS -o /dev/null \
      -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="$CHAT" \
      ${THREAD:+-d message_thread_id="$THREAD"} \
      --data-urlencode text="$MSG" 2>/dev/null; then
  # Never print curl's error: it echoes the URL it was handed, and the URL carries the token.
  echo "notify: telegram send failed (chat=$CHAT thread=${THREAD:-home})" >&2
fi
exit 0

#!/usr/bin/env bash
# Send to Telegram. Prefers `hermes send` (reuses the gateway's platform creds);
# falls back to the raw Telegram API if hermes is unavailable.
# Usage:
#   notify.sh "message text"
#   notify.sh -f /path/to/file
set -euo pipefail

# Load .env if present (for the curl fallback path).
if [ -f "${RECURSION_ROOT:-.}/.env" ]; then set -a; . "${RECURSION_ROOT:-.}/.env"; set +a; fi

# --- Preferred path: hermes send (no LLM, reuses ~/.hermes creds). ----------------
if command -v hermes >/dev/null 2>&1; then
  if [ "${1:-}" = "-f" ] && [ -n "${2:-}" ]; then
    hermes send -t telegram -f "$2" -q && exit 0 || true
  else
    hermes send -t telegram "${1:-}" -q && exit 0 || true
  fi
fi

# --- Fallback: raw Telegram API. --------------------------------------------------
[ -z "${TELEGRAM_BOT_TOKEN:-}" ] && exit 0
[ -z "${TELEGRAM_CHAT_ID:-}" ]   && exit 0
if [ "${1:-}" = "-f" ] && [ -n "${2:-}" ]; then
  MSG="$(head -c 3800 "$2")"
else
  MSG="${1:-}"
fi
curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  --data-urlencode text="${MSG}" >/dev/null || true

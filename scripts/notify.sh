#!/usr/bin/env bash
# Send a message to Telegram. Silent no-op if unconfigured.
set -euo pipefail
MSG="${1:-}"
[ -z "${TELEGRAM_BOT_TOKEN:-}" ] && exit 0
[ -z "${TELEGRAM_CHAT_ID:-}" ] && exit 0
curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  --data-urlencode text="${MSG}" >/dev/null

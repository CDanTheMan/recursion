#!/usr/bin/env bash
# Spawn an execution arm and record it on the BOARD (architecture.md "Plane 2").
# The supervisor REASONS; when something needs DOING it dispatches an arm here.
#
#   dispatch.sh <workstream> <engine> <prompt_file> [model] [label]
#
# engine:
#   hermes      — GPT 5.6 on the ChatGPT Pro sub (Codex OAuth). Flat, ~$0. DEFAULT-safe.
#   claude      — Opus via `claude -p` (Claude Max sub, flat). Deep single-focus work.
#                 OFF the 24/7 path by policy; runs only if the CLI is installed+authed.
#   openrouter  — Deepseek-class bulk, price-sorted. The ONLY metered leg — FENCED:
#                 fires only with RECURSION_ALLOW_METERED=1 (else recorded blocked).
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a
# .env pins RECURSION_ROOT for the deployed checkout. Sourcing it must never RETARGET a
# caller who passed a different root: that silently made a "sandbox" enqueue ten decisions
# into production on 2026-08-12. ROOT and RECURSION_ROOT agree from here on.
RECURSION_ROOT="$ROOT"; export RECURSION_ROOT

WS="${1:?workstream}"; ENGINE="${2:?engine}"; PROMPT_FILE="${3:?prompt_file}"
MODEL="${4:-}"; LABEL="${5:-$ENGINE arm}"
[ -f "$PROMPT_FILE" ] || { echo "no prompt file: $PROMPT_FILE" >&2; exit 2; }
PROMPT="$(cat "$PROMPT_FILE")"

DATE="$(date +%F)"; STAMP="$(date +%H%M%S)"
LOG_DIR="$ROOT/loop/logs"; mkdir -p "$LOG_DIR"
ID="${ENGINE}-${STAMP}"
OUT="$LOG_DIR/$DATE-arm-$ID.out"
USAGE="$LOG_DIR/$DATE-arm-$ID.usage.json"

board(){ bash scripts/board.sh "$@" >/dev/null 2>&1 || true; }
board add "$ID" "$WS" "$ENGINE" "${MODEL:-$ENGINE}" running "$LABEL"

fail(){ board finish "$ID" blocked - "$1"; echo "BLOCKED: $1" >&2; exit 1; }

case "$ENGINE" in
  hermes)
    MODEL="${MODEL:-gpt-5.6-terra}"
    if hermes -z "$PROMPT" -m "$MODEL" --usage-file "$USAGE" >"$OUT" 2>>"$LOG_DIR/$DATE-cycle.log"; then
      board finish "$ID" done "$USAGE" "$LABEL"
    else
      fail "hermes run failed"
    fi ;;

  claude)
    command -v claude >/dev/null 2>&1 || fail "claude CLI not on box (Opus arm unavailable)"
    # Flat Max sub — no metered usage json; note the sub on the board.
    if claude -p "$PROMPT" ${MODEL:+--model "$MODEL"} >"$OUT" 2>>"$LOG_DIR/$DATE-cycle.log"; then
      board finish "$ID" done - "$LABEL (Max sub)"
    else
      fail "claude -p failed (installed but errored — check auth)"
    fi ;;

  openrouter)
    [ "${RECURSION_ALLOW_METERED:-0}" = "1" ] || fail "metered leg fenced — set RECURSION_ALLOW_METERED=1 to dispatch bulk"
    [ -n "${OPENROUTER_API_KEY:-}" ] || fail "no OPENROUTER_API_KEY"
    MODEL="${MODEL:-deepseek/deepseek-chat-v3.1}"
    REQ="$(python3 - "$MODEL" "$PROMPT" <<'PY'
import json,sys
print(json.dumps({"model":sys.argv[1],
  "messages":[{"role":"user","content":sys.argv[2]}],
  "provider":{"sort":"price"}}))
PY
)"
    RESP="$(curl -sS https://openrouter.ai/api/v1/chat/completions \
      -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" \
      -d "$REQ" 2>/dev/null || true)"
    printf '%s' "$RESP" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["choices"][0]["message"]["content"])' >"$OUT" 2>/dev/null \
      || fail "openrouter call failed/empty"
    board finish "$ID" done - "$LABEL (metered:openrouter)" ;;

  *) fail "unknown engine: $ENGINE (hermes|claude|openrouter)" ;;
esac

echo "arm $ID ($ENGINE) done -> $OUT"

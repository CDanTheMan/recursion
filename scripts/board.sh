#!/usr/bin/env bash
# state/BOARD.md — the live registry (architecture.md "Observability").
# One row per in-flight arm: workstream, tier/model, state, started, tokens, $ metered.
# Backed by a TSV sidecar (state/.board.tsv) so rows can flip running->done; BOARD.md is
# re-rendered from it each change. Single source of truth — nothing else invents status.
#
#   board.sh begin                                  # start a fresh tick (clears rows)
#   board.sh add    <id> <ws> <tier> <model> <state> [note]     # add/replace a row
#   board.sh finish <id> <state> <usage_json|-> [note]          # close a row (+tokens/$)
#   board.sh render                                 # print BOARD.md
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
TSV="state/.board.tsv"
MD="state/BOARD.md"
CMD="${1:-render}"; shift || true

clean(){ printf '%s' "${1:-}" | tr '\t\n' '  '; }   # no tabs/newlines inside a field

render(){
  {
    echo "# Recursion board — live registry"
    echo
    echo "Tick: $(cat state/.board-tick 2>/dev/null || echo '(none)')  ·  rendered $(date -u +%FT%TZ)"
    echo
    echo "| Workstream | Tier | Model | State | Started | Tokens | \$ metered | Note |"
    echo "|---|---|---|---|---|---|---|---|"
    if [ -s "$TSV" ]; then
      awk -F'\t' '{printf "| %s | %s | %s | %s | %s | %s | %s | %s |\n",$2,$3,$4,$5,$6,$7,$8,$9}' "$TSV"
    else
      echo "| _(idle — no arms this tick)_ |  |  |  |  |  |  |  |"
    fi
  } > "$MD"
}

case "$CMD" in
  begin)
    : > "$TSV"
    date -u +%FT%TZ > state/.board-tick
    render ;;
  add)
    ID="$(clean "${1:-}")"; WS="$(clean "${2:-}")"; TIER="$(clean "${3:-}")"
    MODEL="$(clean "${4:-}")"; STATE="$(clean "${5:-running}")"; NOTE="$(clean "${6:-}")"
    STARTED="$(date -u +%H:%M:%SZ)"
    grep -v -P "^${ID}\t" "$TSV" 2>/dev/null > "$TSV.tmp" || true; mv -f "$TSV.tmp" "$TSV" 2>/dev/null || true
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ID" "$WS" "$TIER" "$MODEL" "$STATE" "$STARTED" "-" "-" "$NOTE" >> "$TSV"
    render ;;
  finish)
    ID="$(clean "${1:-}")"; STATE="$(clean "${2:-done}")"; USAGE="${3:--}"; NOTE="$(clean "${4:-}")"
    TOK="-"; COST="0.0000"
    if [ -f "$USAGE" ]; then
      TOK="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("total_tokens","-"))' "$USAGE" 2>/dev/null || echo '-')"
      PROV="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("provider",""))' "$USAGE" 2>/dev/null || echo '')"
      C="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("estimated_cost_usd",0))' "$USAGE" 2>/dev/null || echo 0)"
      COST="$(python3 -c "print(f'{float('$C'):.4f}')" 2>/dev/null || echo "$C")"
      [ -n "$PROV" ] && [ "$PROV" != "openai-codex" ] && NOTE="$(clean "$NOTE metered:$PROV")"
    fi
    # carry the existing row's ws/tier/model/started; just update state/tokens/cost/note.
    LINE="$(grep -P "^${ID}\t" "$TSV" 2>/dev/null | head -1 || true)"
    if [ -n "$LINE" ]; then
      WS="$(printf '%s' "$LINE" | cut -f2)"; TIER="$(printf '%s' "$LINE" | cut -f3)"
      MODEL="$(printf '%s' "$LINE" | cut -f4)"; STARTED="$(printf '%s' "$LINE" | cut -f6)"
      [ -z "$NOTE" ] && NOTE="$(printf '%s' "$LINE" | cut -f9)"
      grep -v -P "^${ID}\t" "$TSV" > "$TSV.tmp" || true; mv -f "$TSV.tmp" "$TSV"
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ID" "$WS" "$TIER" "$MODEL" "$STATE" "$STARTED" "$TOK" "$COST" "$NOTE" >> "$TSV"
    fi
    render ;;
  render) render; cat "$MD" ;;
  *) echo "usage: board.sh begin|add|finish|render" >&2; exit 2 ;;
esac

#!/usr/bin/env bash
# Fallback-spend watchdog (the D-006/D-008 guard). Snapshots OpenRouter's cumulative
# metered spend and alerts Telegram if it rose since the last check — i.e. the loop
# silently fell back off the ChatGPT Pro sub onto metered billing. A DIRECT measure of
# money spent, not a log heuristic. Also warns when the prepaid balance runs low.
# Run from cron. Empty output on the happy path (silent watchdog).
set -euo pipefail

ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a
[ -z "${OPENROUTER_API_KEY:-}" ] && exit 0

SNAP="state/.openrouter-usage.json"
LOW_BALANCE_FLOOR="${OR_LOW_BALANCE_FLOOR:-5}"   # USD remaining before we warn
SPEND_EPSILON="${OR_SPEND_EPSILON:-0.01}"        # USD delta that counts as "fell back"

RESP="$(curl -sS -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        https://openrouter.ai/api/v1/credits 2>/dev/null || true)"

read_field(){ printf '%s' "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['$1'])" 2>/dev/null || true; }
USAGE="$(read_field total_usage)"
CREDITS="$(read_field total_credits)"
[ -z "$USAGE" ] && exit 0   # API hiccup — silent, retry next tick

PREV=""
[ -f "$SNAP" ] && PREV="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("total_usage",""))' "$SNAP" 2>/dev/null || true)"

write_snapshot(){
  SNAP_USAGE="$USAGE" SNAP_CREDITS="${CREDITS:-0}" SNAP_AT="$(date -Is)" \
    python3 - "$SNAP" <<'PY'
import json,os,pathlib,sys,tempfile
path=pathlib.Path(sys.argv[1])
path.parent.mkdir(parents=True,exist_ok=True)
fd,tmp=tempfile.mkstemp(prefix=f'.{path.name}.tmp.',dir=path.parent)
try:
    with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as out:
        json.dump({'total_usage':float(os.environ['SNAP_USAGE']),
                   'total_credits':float(os.environ['SNAP_CREDITS']),
                   'at':os.environ['SNAP_AT']},out,separators=(',',':'))
        out.write('\n'); out.flush(); os.fsync(out.fileno())
    os.replace(tmp,path)
    try:
        directory=os.open(path.parent,os.O_RDONLY)
    except OSError:
        directory=None
    if directory is not None:
        try: os.fsync(directory)
        finally: os.close(directory)
finally:
    try: os.unlink(tmp)
    except FileNotFoundError: pass
PY
}

# First run just seeds the snapshot -- no prior to diff against.
if [ -z "$PREV" ]; then
  write_snapshot
else
  OVER="$(python3 -c "print(1 if (float('$USAGE')-float('$PREV'))>float('$SPEND_EPSILON') else 0)" 2>/dev/null || echo 0)"
  if [ "$OVER" = "1" ]; then
    DELTA="$(python3 -c "print(round(float('$USAGE')-float('$PREV'),4))" 2>/dev/null || echo '?')"
    ALERT="⚠ Recursion FALLBACK FIRED: OpenRouter metered spend +\$$DELTA since last check (cumulative \$$USAGE). The loop dropped off the ChatGPT Pro sub — check quota/gateway logs (journalctl -u hermes-gateway)."

    # Record the occurrence before consulting PAUSE. Escalation identity is stable, so repeated
    # paused ticks remain one durable ask while the unconsumed usage delta stays in the snapshot.
    if ! bash "$ROOT/scripts/taskctl.sh" esc-record fallback-spend:openrouter \
      "$ALERT" recursion "$SNAP" >/dev/null; then
      echo "fallback-watch: durable spend escalation could not be recorded" >&2
      exit 73
    fi
    [ ! -f "$ROOT/state/PAUSE" ] || exit 0

    # notify.sh is the sole transport boundary. Advance the baseline only once it accepts the
    # notification; rc=75 (including a PAUSE race) and all other failures preserve the delta.
    bash "$ROOT/scripts/notify.sh" "$ALERT"
    write_snapshot
    exit 0
  fi
  write_snapshot
fi

# Low-balance warning (independent of fallback).
if [ -n "$CREDITS" ]; then
  LOW="$(python3 -c "print(1 if (float('$CREDITS')-float('$USAGE'))<float('$LOW_BALANCE_FLOOR') else 0)" 2>/dev/null || echo 0)"
  if [ "$LOW" = "1" ]; then
    REMAIN="$(python3 -c "print(round(float('$CREDITS')-float('$USAGE'),2))" 2>/dev/null || echo '?')"
    bash "$ROOT/scripts/notify.sh" "⚠ Recursion: OpenRouter balance low — \$$REMAIN left. Top up so the fallback leg stays available." || true
  fi
fi
exit 0

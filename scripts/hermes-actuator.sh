#!/usr/bin/env bash
# Continuously supervised consumer for the durable Head Hermes decision queue.
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
INTERVAL="${RECURSION_ACTUATOR_INTERVAL_S:-2}"
STOP=0
trap 'STOP=1' INT TERM
log(){ echo "[$(date -Is)] hermes-actuator: $*" >&2; }

cd "$ROOT" || exit 3
log "started; durable queue consumer is supervised"
while [ "$STOP" = 0 ]; do
  if [ -f "$ROOT/state/PAUSE" ]; then
    # PAUSE halts execution, not awareness.  Stay supervised without consuming or dropping work.
    sleep "$INTERVAL" & wait $! 2>/dev/null || true
    continue
  fi
  set +e
  RECURSION_ROOT="$ROOT" bash "$ROOT/scripts/conduct-hermes.sh"
  rc=$?
  set -e
  case "$rc" in
    0|4|73|75) : ;;
    *) log "queue pass failed rc=$rc; pending state was preserved" ;;
  esac
  sleep "$INTERVAL" & wait $! 2>/dev/null || true
done
log "stopped"

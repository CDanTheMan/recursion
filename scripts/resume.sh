#!/usr/bin/env bash
# Kill switch OFF. Removes state/PAUSE so scheduled jobs run again.
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
if [ -f "$ROOT/state/PAUSE" ]; then
  python3 "$ROOT/scripts/remote-pause.py" clear --base "$ROOT"
  echo "resumed (state/PAUSE removed)"
  bash "$ROOT/scripts/notify.sh" "▶ Recursion RESUMED. Scheduled jobs active." || true
else
  echo "not paused (no state/PAUSE)"
fi

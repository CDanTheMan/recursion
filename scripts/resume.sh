#!/usr/bin/env bash
# Kill switch OFF. Removes state/PAUSE so scheduled jobs run again.
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
if [ -f "$ROOT/state/PAUSE" ]; then
  python3 - "$ROOT" <<'PY'
import importlib.util
import sys
from pathlib import Path

root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("recursion_runtime_state", root / "scripts/runtime-state.py")
if spec is None or spec.loader is None:
    raise SystemExit("resume: runtime-state helper is absent")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with module.DirectoryLock(root / "state/.locks/pause-transfer.lock", "pause-transfer"):
    try:
        (root / "state/PAUSE").unlink()
    except FileNotFoundError:
        pass
PY
  echo "resumed (state/PAUSE removed)"
  bash "$ROOT/scripts/notify.sh" "▶ Recursion RESUMED. Scheduled jobs active." || true
else
  echo "not paused (no state/PAUSE)"
fi

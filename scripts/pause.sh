#!/usr/bin/env bash
# Kill switch ON. Every supervisor job checks state/PAUSE first and halts autonomous
# action while it is present (architecture.md). Heartbeat and durable escalation recording
# continue locally; D-014 interlocks all external notification delivery.
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
REASON="${*:-manual pause}"
python3 - "$ROOT" "$REASON" <<'PY'
import importlib.util
import sys
from pathlib import Path

root, reason = Path(sys.argv[1]), sys.argv[2]
spec = importlib.util.spec_from_file_location("recursion_runtime_state", root / "scripts/runtime-state.py")
if spec is None or spec.loader is None:
    raise SystemExit("pause: runtime-state helper is absent")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
pause = root / "state/PAUSE"
pause.parent.mkdir(parents=True, exist_ok=True)
with module.DirectoryLock(root / "state/.locks/pause-transfer.lock", "pause-transfer"):
    module.atomic_bytes(pause, f"PAUSED {module.time.strftime('%Y-%m-%dT%H:%M:%S%z')}\nreason: {reason}\n".encode())
PY
echo "paused: $ROOT/state/PAUSE"
bash "$ROOT/scripts/notify.sh" "⏸ Recursion PAUSED ($REASON). Autonomous action halted. resume.sh to lift." || true

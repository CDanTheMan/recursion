#!/usr/bin/env bash
# Kill switch ON. Every supervisor job checks state/PAUSE first and halts autonomous
# action while it is present (architecture.md). Heartbeat and durable escalation recording
# continue locally; D-014 interlocks all external notification delivery.
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
REASON="${*:-manual pause}"
python3 "$ROOT/scripts/remote-pause.py" set --base "$ROOT" --reason "$REASON"
echo "paused: $ROOT/state/PAUSE"
bash "$ROOT/scripts/notify.sh" "⏸ Recursion PAUSED ($REASON). Autonomous action halted. resume.sh to lift." || true

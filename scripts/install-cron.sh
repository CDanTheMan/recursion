#!/usr/bin/env bash
# Install the supervisor schedule. Idempotent.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENTRY="30 6 * * * cd $ROOT && RECURSION_ROOT=$ROOT bash loop/supervisor/run.sh morning"

( crontab -l 2>/dev/null | grep -v "recursion/loop/supervisor/run.sh" ; echo "$ENTRY" ) | crontab -
echo "installed:"
crontab -l | grep supervisor

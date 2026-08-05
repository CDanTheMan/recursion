#!/usr/bin/env bash
# Install the supervisor schedule. Idempotent — safe to re-run.
#   Job 1: daily one-page brief   (runs on the ChatGPT Pro sub via Hermes)
#   Job 2: fallback-spend watchdog (every 3h; silent unless something's wrong)
#
# Override the schedules with env vars, e.g. to fire the brief at your local morning:
#   BRIEF_CRON="0 12 * * *" bash scripts/install-cron.sh    # 12:00 box-time (UTC)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# cron runs with a minimal PATH; make sure it can find `hermes`.
HERMES_DIR="$(dirname "$(command -v hermes 2>/dev/null || echo /usr/local/bin/hermes)")"

BRIEF_CRON="${BRIEF_CRON:-30 6 * * *}"     # guaranteed daily digest (box time = UTC)
CYCLE_CRON="${CYCLE_CRON:-15 */3 * * *}"   # cheap heartbeat every 3h; brief fires only on a signal
WATCH_CRON="${WATCH_CRON:-0 */3 * * *}"

PATHLINE="PATH=$HERMES_DIR:/usr/local/bin:/usr/bin:/bin # recursion-path"
BRIEF="$BRIEF_CRON cd $ROOT && RECURSION_ROOT=$ROOT bash scripts/cycle.sh force # recursion-brief"
CYCLE="$CYCLE_CRON cd $ROOT && RECURSION_ROOT=$ROOT bash scripts/cycle.sh # recursion-cycle"
WATCH="$WATCH_CRON cd $ROOT && RECURSION_ROOT=$ROOT bash scripts/fallback-watch.sh # recursion-watch"

# Robust against a box with no existing crontab (crontab -l exits non-zero the first time).
CUR="$(crontab -l 2>/dev/null || true)"
KEEP="$(printf '%s\n' "$CUR" | grep -vE '# recursion-(brief|cycle|watch|path)$' | grep -v '^$' || true)"
printf '%s\n%s\n%s\n%s\n%s\n' "$KEEP" "$PATHLINE" "$BRIEF" "$CYCLE" "$WATCH" | grep -v '^$' | crontab -

# Make sure the cron daemon is actually running + enabled at boot.
for svc in cron crond; do
  if systemctl list-unit-files 2>/dev/null | grep -q "^$svc"; then
    systemctl enable --now "$svc" >/dev/null 2>&1 || true
    break
  fi
done

echo "installed:"
crontab -l | grep -E '# recursion-'

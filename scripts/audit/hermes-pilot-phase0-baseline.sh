#!/usr/bin/env bash
# Reproduce the pre-change Recursion baseline without running the intentionally-red pilot controls.
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
LIVE_ROOT="${RECURSION_LIVE_ROOT:-/opt/recursion}"
cd "$ROOT"

branch="$(git branch --show-current 2>/dev/null)"
[ -n "$branch" ] || { echo "BASELINE HARNESS: use a named branch, not detached HEAD" >&2; exit 3; }
ROOT_PHYSICAL="$(pwd -P)"
LIVE_ROOT_PHYSICAL="$(cd "$LIVE_ROOT" 2>/dev/null && pwd -P)" \
  || { echo "BASELINE HARNESS: live root is absent" >&2; exit 90; }
[ "$ROOT_PHYSICAL" != "$LIVE_ROOT_PHYSICAL" ] || {
  echo "BASELINE HARNESS: use a fresh reviewed clone separate from the deployed checkout" >&2
  exit 3
}
[ -f "$LIVE_ROOT/state/PAUSE" ] || { echo "BASELINE HARNESS: live PAUSE missing" >&2; exit 90; }
echo "BASELINE_COMMIT=$(git rev-parse HEAD)"
echo "BASELINE_BRANCH=$branch"
echo "DEPLOYED_COMMIT=$(git -C "$LIVE_ROOT" rev-parse HEAD)"

failed=0; count=0
for test_file in scripts/tests/*.sh; do
  case "$test_file" in *hermes-pilot-phase*-red.test.sh) continue ;; esac
  count=$((count+1)); echo "===== $test_file ====="
  timeout "${RECURSION_BASELINE_TEST_TIMEOUT_S:-180}" bash "$test_file"
  rc=$?; echo "RESULT $test_file rc=$rc"
  [ "$rc" -eq 0 ] || failed=$((failed+1))
done
count=$((count+1)); echo "===== scripts/work.selftest.sh ====="
timeout "${RECURSION_BASELINE_TEST_TIMEOUT_S:-180}" bash scripts/work.selftest.sh
rc=$?; echo "RESULT scripts/work.selftest.sh rc=$rc"
[ "$rc" -eq 0 ] || failed=$((failed+1))

[ -f "$LIVE_ROOT/state/PAUSE" ] || { echo "BASELINE HARNESS: live PAUSE disappeared" >&2; exit 91; }
echo "BASELINE_SUITES=$count"
echo "BASELINE_FAILED_SUITES=$failed"
[ "$failed" -eq 0 ]

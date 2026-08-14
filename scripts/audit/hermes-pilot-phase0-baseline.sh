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
ROOT_ID="$(stat -Lc '%d:%i' -- "$ROOT_PHYSICAL" 2>/dev/null)" \
  || { echo "BASELINE HARNESS: reviewed root identity is unreadable" >&2; exit 3; }
LIVE_ROOT_ID="$(stat -Lc '%d:%i' -- "$LIVE_ROOT_PHYSICAL" 2>/dev/null)" \
  || { echo "BASELINE HARNESS: live root identity is unreadable" >&2; exit 90; }
refuse_shared_checkout(){
  echo "BASELINE HARNESS: use a fresh independent reviewed clone separate from the deployed checkout" >&2
  exit 3
}
[ "$ROOT_PHYSICAL" != "$LIVE_ROOT_PHYSICAL" ] || refuse_shared_checkout
[ "$ROOT_ID" != "$LIVE_ROOT_ID" ] || refuse_shared_checkout

# Freeze symlink resolution before later PAUSE and Git reads, and refuse linked worktrees that
# have distinct directories but share the deployed checkout's refs and object authority.
ROOT="$ROOT_PHYSICAL"
LIVE_ROOT="$LIVE_ROOT_PHYSICAL"
git_common_physical(){
  local repo="$1" common
  common="$(git -C "$repo" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" \
    || return 1
  (cd "$common" 2>/dev/null && pwd -P)
}
ROOT_GIT_COMMON="$(git_common_physical "$ROOT")" \
  || { echo "BASELINE HARNESS: reviewed root is not a Git checkout" >&2; exit 3; }
LIVE_ROOT_GIT_COMMON="$(git_common_physical "$LIVE_ROOT")" \
  || { echo "BASELINE HARNESS: live root is not a Git checkout" >&2; exit 90; }
[ "$ROOT_GIT_COMMON" != "$LIVE_ROOT_GIT_COMMON" ] || refuse_shared_checkout

[ -f "$LIVE_ROOT/state/PAUSE" ] || { echo "BASELINE HARNESS: live PAUSE missing" >&2; exit 90; }
BASELINE_COMMIT="$(git -C "$ROOT" rev-parse --verify HEAD 2>/dev/null)" \
  || { echo "BASELINE HARNESS: reviewed commit evidence is unavailable" >&2; exit 3; }
DEPLOYED_COMMIT="$(git -C "$LIVE_ROOT" rev-parse --verify HEAD 2>/dev/null)" \
  || { echo "BASELINE HARNESS: deployed commit evidence is unavailable" >&2; exit 90; }
echo "BASELINE_COMMIT=$BASELINE_COMMIT"
echo "BASELINE_BRANCH=$branch"
echo "DEPLOYED_COMMIT=$DEPLOYED_COMMIT"

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

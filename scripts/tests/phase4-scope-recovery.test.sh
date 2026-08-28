#!/usr/bin/env bash
# A scoped actuator must refuse an out-of-scope recovery before action identity or instruction
# coupling can acknowledge/release anything. This fixture does not need a live queue or systemd.
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/loop/logs" "$TMP/state/actions" "$TMP/state/instructions" "$TMP/state/.locks"
cp "$ROOT/scripts/conduct-hermes.sh" "$TMP/conduct-hermes.sh"
cat > "$TMP/work.json" <<'JSON'
{"verb":"work","args":[],"status":"queued"}
JSON
cat > "$TMP/state-action.json" <<'JSON'
{"verb":"noop","args":[],"status":"queued"}
JSON
before_work="$(sha256sum "$TMP/work.json" | awk '{print $1}')"
before_state="$(sha256sum "$TMP/state-action.json" | awk '{print $1}')"

set +e
( cd "$TMP" && RECURSION_ROOT="$TMP" bash conduct-hermes.sh --recover-only --non-work-only --file "$TMP/work.json" ) \
  >"$TMP/non-work.out" 2>&1
non_work_rc=$?
( cd "$TMP" && RECURSION_ROOT="$TMP" bash conduct-hermes.sh --recover-only --work-only --file "$TMP/state-action.json" ) \
  >"$TMP/work.out" 2>&1
work_rc=$?
set -e

test "$non_work_rc" = 74
test "$work_rc" = 74
test "$(sha256sum "$TMP/work.json" | awk '{print $1}')" = "$before_work"
test "$(sha256sum "$TMP/state-action.json" | awk '{print $1}')" = "$before_state"
test ! -e "$TMP/state/instructions/00000001.md"
grep -q 'REFUSED' "$TMP/non-work.out"
grep -q 'REFUSED' "$TMP/work.out"
grep -q 'CHILD_SCOPE_ARGS' "$TMP/conduct-hermes.sh"
grep -q 'DECISION_FILE_DIGEST' "$TMP/conduct-hermes.sh"
grep -q 'DECISION_SNAPSHOT_B64' "$TMP/conduct-hermes.sh"
grep -q 'decision projection changed before child action' "$TMP/conduct-hermes.sh"
grep -q 'scope_guard' "$TMP/conduct-hermes.sh"
echo "phase4-scope-recovery: ALL PASS"

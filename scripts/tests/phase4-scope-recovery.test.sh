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
grep -q 'original claimed decision digest is absent' "$TMP/conduct-hermes.sh"
grep -q 'finalize_claim "$queue_file" "$child_rc" "$claimed_digest"' "$TMP/conduct-hermes.sh"
! grep -q 'queue_sha="$(python3 - "$claimed"' "$TMP/conduct-hermes.sh"
# The parallel claim path must retain the digest before starting its child; otherwise a swap in
# this former pre-capture window can turn the swapped projection into the terminal-CAS authority.
python3 - "$TMP/conduct-hermes.sh" <<'PY'
import re,sys
text=open(sys.argv[1],encoding='utf-8').read()
start=text.index('while [ "${#pids[@]}"')
end=text.index('    done\n    [ "${#pids[@]}"',start)
parallel=text[start:end]
pattern=(r'claimed_digest="\$\(sha256sum "\$queue_file".*?\n'
         r'\s*RECURSION_QUEUE_ACTUATION=1 RECURSION_ROOT="\$ROOT" \\\n'
         r'\s*bash "\$ROOT/scripts/conduct-hermes\.sh".*?&')
if not re.search(pattern,parallel,re.S):
    raise SystemExit('parallel claim does not capture the original digest before child launch')
PY
grep -q 'scope_guard' "$TMP/conduct-hermes.sh"
mkdir -p "$TMP/state/decision-queue/running" "$TMP/state/decision-queue/failed"
if python3 -c 'import fcntl' 2>/dev/null; then
printf '{"id":"swap","status":"running","verb":"noop"}\n' > "$TMP/state/decision-queue/running/swap.json"
post_action_digest="$(sha256sum "$TMP/state/decision-queue/running/swap.json" | awk '{print $1}')"
printf '{"id":"swap","status":"running","verb":"work"}\n' > "$TMP/state/decision-queue/running/swap.json"
set +e
RECURSION_ROOT="$TMP" python3 "$ROOT/scripts/decision-queue.py" fail "$TMP/state/decision-queue/running/swap.json" swapped --expected-sha256 "$post_action_digest" >/dev/null 2>&1
swap_rc=$?
set -e
test "$swap_rc" = 73
test -f "$TMP/state/decision-queue/running/swap.json"
echo "ok    post-action queue projection swap fails the retained original digest CAS"
else
 echo "skip  post-action queue projection swap CAS (fcntl unavailable on this host)"
fi
echo "phase4-scope-recovery: ALL PASS"

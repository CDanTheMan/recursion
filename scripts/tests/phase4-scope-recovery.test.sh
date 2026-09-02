#!/usr/bin/env bash
# A scoped actuator must refuse an out-of-scope recovery before action identity or instruction
# coupling can acknowledge/release anything. This fixture does not need a live queue or systemd.
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TMP="$(mktemp -d)"

scope_failure_report() {
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    printf 'phase4-scope-recovery: assertion failed (rc=%s)\n' "$rc" >&2
    for log in "$TMP/non-work.out" "$TMP/work.out"; do
      if [ -f "$log" ]; then
        printf '%s: %s\n' "$(basename "$log")" "$(tr '\n' ' ' < "$log")" >&2
      fi
    done
  fi
  rm -rf "$TMP"
  return "$rc"
}
trap scope_failure_report EXIT

assert_equal() {
  local label="$1" expected="$2" actual="$3"
  if [ "$actual" != "$expected" ]; then
    printf 'phase4-scope-recovery: assertion=%s expected=%q got=%q\n' \
      "$label" "$expected" "$actual" >&2
    return 1
  fi
}

assert_file_state() {
  local label="$1" expected="$2" path="$3" actual=absent
  if [ -e "$path" ]; then actual=present; fi
  assert_equal "$label" "$expected" "$actual"
}

assert_contains() {
  local label="$1" pattern="$2" path="$3"
  if grep -q -- "$pattern" "$path"; then return 0; fi
  assert_equal "$label" "pattern-present" "pattern-absent"
}

assert_absent() {
  local label="$1" pattern="$2" path="$3"
  if ! grep -q -- "$pattern" "$path"; then return 0; fi
  assert_equal "$label" "pattern-absent" "pattern-present"
}

sha256_or_missing() {
  if [ -f "$1" ]; then
    sha256sum "$1" | awk '{print $1}'
  else
    printf '<missing>\n'
  fi
}

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

assert_equal "non-work scope refusal exit" 74 "$non_work_rc"
assert_equal "work scope refusal exit" 74 "$work_rc"
assert_equal "work input remains byte-exact" "$before_work" "$(sha256_or_missing "$TMP/work.json")"
assert_equal "state input remains byte-exact" "$before_state" "$(sha256_or_missing "$TMP/state-action.json")"
assert_file_state "scope refusal does not write an instruction" absent "$TMP/state/instructions/00000001.md"
assert_contains "non-work refusal is visible" 'REFUSED' "$TMP/non-work.out"
assert_contains "work refusal is visible" 'REFUSED' "$TMP/work.out"
assert_contains "child scope arguments are wired" 'CHILD_SCOPE_ARGS' "$TMP/conduct-hermes.sh"
assert_contains "decision file digest is wired" 'DECISION_FILE_DIGEST' "$TMP/conduct-hermes.sh"
assert_contains "immutable snapshot is wired" 'DECISION_SNAPSHOT_B64' "$TMP/conduct-hermes.sh"
assert_contains "swap refusal message is wired" 'decision projection changed before child action' "$TMP/conduct-hermes.sh"
assert_contains "missing claimed digest is refused" 'original claimed decision digest is absent' "$TMP/conduct-hermes.sh"
assert_contains "finalize uses retained digest" 'finalize_claim "$queue_file" "$child_rc" "$claimed_digest"' "$TMP/conduct-hermes.sh"
assert_absent "parallel claim does not rehash mutable path" 'queue_sha="$(python3 - "$claimed"' "$TMP/conduct-hermes.sh"
# Every claim path must receive the immutable bytes and digest while the queue lock is held;
# otherwise a swap in the former pre-capture window can turn the swapped projection into the
# child authority.
if ! parallel_check_output="$(python3 - "$TMP/conduct-hermes.sh" 2>&1 <<'PY'
import re,sys
text=open(sys.argv[1],encoding='utf-8').read()
start=text.index('while [ "${#pids[@]}"')
end=text.index('    done\n    [ "${#pids[@]}"',start)
parallel=text[start:end]
if 'claim_from_queue "${claim_args[@]:1}"' not in parallel:
    raise SystemExit('parallel claim does not use the snapshotting claim helper')
if 'run_claimed_child "$queue_file" "$claimed_digest" "$claimed_snapshot"' not in parallel:
    raise SystemExit('parallel claim does not launch from the immutable snapshot')
if 'sha256sum "$queue_file"' in parallel:
    raise SystemExit('parallel claim hashes the mutable path after claim')
PY
)"; then
  assert_equal "parallel claim snapshot structure" "all required immutable snapshot hooks" "$parallel_check_output"
fi
assert_contains "scope guard is wired" 'scope_guard' "$TMP/conduct-hermes.sh"
assert_contains "claim helper receives snapshot" 'claim-pending "\$@" --with-snapshot' "$TMP/conduct-hermes.sh"
assert_contains "transition receives retained digest" '--expected-sha256 "\$CLAIMED_DIGEST"' "$TMP/conduct-hermes.sh"
mkdir -p "$TMP/state/decision-queue/running" "$TMP/state/decision-queue/failed"
if python3 -c 'import fcntl' 2>/dev/null; then
printf '{"id":"swap","status":"running","verb":"noop"}\n' > "$TMP/state/decision-queue/running/swap.json"
post_action_digest="$(sha256sum "$TMP/state/decision-queue/running/swap.json" | awk '{print $1}')"
printf '{"id":"swap","status":"running","verb":"work"}\n' > "$TMP/state/decision-queue/running/swap.json"
set +e
RECURSION_ROOT="$TMP" python3 "$ROOT/scripts/decision-queue.py" fail "$TMP/state/decision-queue/running/swap.json" swapped --expected-sha256 "$post_action_digest" >/dev/null 2>&1
swap_rc=$?
set -e
assert_equal "swapped projection returns typed refusal" 73 "$swap_rc"
assert_file_state "swapped projection remains in running queue" present "$TMP/state/decision-queue/running/swap.json"
echo "ok    post-action queue projection swap fails the retained original digest CAS"

printf '{"id":"steady","status":"running","verb":"noop"}\n' \
  > "$TMP/state/decision-queue/running/steady.json"
steady_digest="$(sha256sum "$TMP/state/decision-queue/running/steady.json" | awk '{print $1}')"
set +e
RECURSION_ROOT="$TMP" python3 "$ROOT/scripts/decision-queue.py" fail \
  "$TMP/state/decision-queue/running/steady.json" steady --expected-sha256 "$steady_digest" \
  >"$TMP/steady.out" 2>&1
steady_rc=$?
set -e
assert_equal "well-formed queue transition succeeds" 0 "$steady_rc"
assert_file_state "successful transition removes running projection" absent \
  "$TMP/state/decision-queue/running/steady.json"
assert_file_state "successful transition publishes failed projection" present \
  "$TMP/state/decision-queue/failed/steady.json"
echo "ok    well-formed queue projection transition succeeds with the retained digest"
else
 echo "skip  post-action queue projection swap CAS (fcntl unavailable on this host)"
fi
echo "phase4-scope-recovery: ALL PASS"

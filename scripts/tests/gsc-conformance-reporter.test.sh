#!/usr/bin/env bash
# Guards the machine-readable reporter contract used by gsc-conformance-gate-v2.sh.
set -uo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
GATE="$ROOT/scripts/gsc-conformance-gate-v2.sh"
fails=0
ok() { printf 'ok    %s\n' "$1"; }
no() { printf 'FAIL  %s\n' "$1"; fails=$((fails + 1)); }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
REPO="$TMP/repo"
mkdir -p "$REPO/user-client/render" "$TMP/bin"
printf '%s\n' "'use strict';" > "$REPO/user-client/render/reporter.test.cjs"
printf '%s\n' 'baseline reporter title' > "$TMP/baseline-pass.txt"
git -C "$REPO" init -q
git -C "$REPO" add user-client/render/reporter.test.cjs
git -C "$REPO" -c user.name=fixture -c user.email=fixture@example.invalid \
  commit -qm 'reporter fixture'

cat > "$TMP/bin/node" <<'NODE'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$NODE_ARGS_LOG"
if [ "$#" -ne 3 ] || [ "$1" != "--test" ] || [ "$2" != "--test-reporter=tap" ] \
    || [ "$3" != "user-client/render/reporter.test.cjs" ]; then
  printf '%s\n' 'fake node: unexpected test reporter invocation' >&2
  exit 96
fi
case "${FAKE_NODE_MODE:-pass}" in
  pass)
    printf '%s\n' 'TAP version 13' '# Subtest: baseline reporter title' \
      'ok 1 - baseline reporter title' '1..1' '# pass 1' '# fail 0'
    ;;
  regression)
    printf '%s\n' 'TAP version 13' '# Subtest: replacement title' \
      'ok 1 - replacement title' '1..1' '# pass 1' '# fail 0'
    ;;
  skip)
    printf '%s\n' 'TAP version 13' '# Subtest: baseline reporter title' \
      'ok 1 - baseline reporter title # SKIP unavailable' '1..1' '# pass 0' '# fail 0'
    ;;
  *) exit 97 ;;
esac
NODE
chmod 0755 "$TMP/bin/node"

run_gate() {
  local gate="${2:-$GATE}"
  NODE_ARGS_LOG="$TMP/node-args" PATH="$TMP/bin:$PATH" FAKE_NODE_MODE="$1" \
    GSC_BASELINE="$TMP/baseline-pass.txt" bash "$gate" --no-progress 2>&1
}

set +e
OUT="$(cd "$REPO" && run_gate pass "$GATE")"; rc=$?
set -e
mapfile -t node_args < "$TMP/node-args"
if [ "$rc" = 0 ] && [ "${#node_args[@]}" -eq 3 ] \
    && [ "${node_args[0]}" = "--test" ] \
    && [ "${node_args[1]}" = "--test-reporter=tap" ] \
    && [ "${node_args[2]}" = "user-client/render/reporter.test.cjs" ]; then
  ok "gate requests TAP explicitly and parses its passing title"
else
  no "expected explicit TAP reporter and pass; got rc=$rc: $(printf '%s' "$OUT" | head -1)"
fi

set +e
OUT="$(cd "$REPO" && TMPDIR="$TMP/missing-scratch" run_gate pass "$GATE")"; rc=$?
set -e
if [ "$rc" = 3 ] && printf '%s' "$OUT" | grep -q 'HARNESS — cannot allocate TAP scratch space'; then
  ok "an unavailable scratch directory fails closed"
else
  no "unavailable scratch directory escaped; rc=$rc: $(printf '%s' "$OUT" | head -1)"
fi

MISSING_REPORTER_GATE="$TMP/missing-reporter-gate.sh"
sed 's/node --test --test-reporter=tap /node --test /' "$GATE" > "$MISSING_REPORTER_GATE"
set +e
OUT="$(cd "$REPO" && run_gate pass "$MISSING_REPORTER_GATE")"; rc=$?
set -e
if [ "$rc" = 3 ] && ! grep -qx -- '--test-reporter=tap' "$TMP/node-args" \
    && printf '%s' "$OUT" | grep -q 'zero passing tests parsed'; then
  ok "mutation detected: removing the explicit TAP reporter fails closed"
else
  no "missing-reporter mutation escaped; rc=$rc: $(printf '%s' "$OUT" | head -1)"
fi

REORDERED_REPORTER_GATE="$TMP/reordered-reporter-gate.sh"
sed 's/--test --test-reporter=tap user-client\/render\/\*\.test\.cjs/--test user-client\/render\/\*\.test\.cjs --test-reporter=tap/' \
  "$GATE" > "$REORDERED_REPORTER_GATE"
set +e
OUT="$(cd "$REPO" && run_gate pass "$REORDERED_REPORTER_GATE")"; rc=$?
set -e
if [ "$rc" = 3 ] && printf '%s' "$OUT" | grep -q 'zero passing tests parsed'; then
  ok "mutation detected: an unexpected reporter invocation shape fails closed"
else
  no "unexpected reporter shape escaped; rc=$rc: $(printf '%s' "$OUT" | head -1)"
fi

set +e
OUT="$(cd "$REPO" && run_gate regression)"; rc=$?
set -e
if [ "$rc" = 1 ] && printf '%s' "$OUT" | grep -q 'baseline reporter title'; then
  ok "mutation detected: a missing baseline title remains a regression"
else
  no "missing baseline title escaped; rc=$rc: $(printf '%s' "$OUT" | head -1)"
fi

set +e
OUT="$(cd "$REPO" && run_gate skip)"; rc=$?
set -e
if [ "$rc" = 3 ] && printf '%s' "$OUT" | grep -q 'HARNESS'; then
  ok "a skipped title cannot satisfy the baseline"
else
  no "skipped baseline title was not rejected as a harness fault; rc=$rc"
fi

echo
if [ "$fails" -eq 0 ]; then
  echo "gsc-conformance-reporter: ALL PASS"
  exit 0
fi
echo "gsc-conformance-reporter: $fails FAILED"
exit 1

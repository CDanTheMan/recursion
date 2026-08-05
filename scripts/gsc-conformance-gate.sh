#!/usr/bin/env bash
# gsc-conformance-gate.sh — acceptance gate for cubic-castles (golden-stallion-client) build
# tasks. Enforces the renderer discipline as a machine-checkable contract. Run from the
# worktree repo root (work.sh sets cwd). A green here means the change moved the spec forward
# WITHOUT breaking anything and WITHOUT cheating:
#
#   (0) NO TAMPERING — the arm may not edit tests, truth fixtures, or golden data.
#   (1) NO REGRESSION — every genuine baseline pass still passes.
#   (2) PROGRESS      — at least one previously-failing test now passes (unless --no-progress).
#
# Hard to game: can't fake the target by editing a test (0), can't pass it by breaking a
# sibling (1), can't no-op (2).  exit 0=pass · 1=regression · 2=no progress · 3=harness · 4=tamper
set -uo pipefail
BASELINE="${GSC_BASELINE:-/opt/recursion/state/gsc/baseline-pass.txt}"
NOPROG=0; [ "${1:-}" = "--no-progress" ] && NOPROG=1
[ -f "$BASELINE" ] || { echo "GATE: no baseline at $BASELINE"; exit 3; }

# (0) anti-gaming: no changes to any *.test.cjs or anything under render/data (fixtures/golden).
TAMPER="$(git status --porcelain -- '*.test.cjs' user-client/render/data 2>/dev/null || true)"
if [ -n "$TAMPER" ]; then
  echo "GATE: TAMPERING — arm modified protected test/fixture files (forbidden):"
  printf '%s\n' "$TAMPER" | head -20
  exit 4
fi

TAP="$(mktemp)"; PASS="$(mktemp)"; trap 'rm -f "$TAP" "$PASS"' EXIT
node --test user-client/render/*.test.cjs > "$TAP" 2>&1 || true   # node exits 1 on any fail; score from TAP
grep -E '^ok ' "$TAP" | grep -v '# SKIP' | sed -E 's/^ok [0-9]+ - //' | sort -u > "$PASS"
CUR="$(wc -l < "$PASS")"; BASE="$(wc -l < "$BASELINE")"

# (1) regression: any baseline-pass title missing from current passes
MISSING="$(comm -23 "$BASELINE" "$PASS")"
if [ -n "$MISSING" ]; then
  echo "GATE: REGRESSION — these baseline-passing tests no longer pass:"
  printf '%s\n' "$MISSING" | head -20
  exit 1
fi

# (2) progress
if [ "$NOPROG" = "0" ] && [ "$CUR" -le "$BASE" ]; then
  echo "GATE: NO PROGRESS — genuine passes $CUR <= baseline $BASE (nothing flipped green)"
  exit 2
fi

echo "GATE: PASS — no regression; genuine passes $BASE -> $CUR (+$((CUR-BASE)))"
comm -13 "$BASELINE" "$PASS" | sed 's/^/  now passing: /' | head -20
exit 0

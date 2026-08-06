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
#
# ⚠ LC_ALL=C IS LOAD-BEARING — DO NOT REMOVE (fixed 2026-08-06).
# `sort` and `comm` must agree on collation or the set comparison is meaningless. Under
# en_US.UTF-8 they do NOT agree: GNU sort applies locale collation (which folds case and
# ignores punctuation/leading symbols), while comm's sortedness check compares differently.
# The observable bug: comparing the baseline against a strict SUPERSET of itself reported a
# title as "missing" — a mathematically impossible result — accompanied by
# "comm: file N is not in sorted order". Reproduced parameter-free by appending 6 titles to
# the baseline and diffing it against itself.
#   - False REGRESSION blocks correct work (how this was found).
#   - False PASS is the dangerous direction: the same mis-collation can skip a genuinely
#     absent title, so a real regression would be blessed as green.
# Forcing C collation everywhere makes sort and comm byte-consistent. The baseline is
# re-pinned under C collation in the same commit; both sides must be produced identically.
# Guarded by scripts/tests/gate-collation.test.sh, which includes a MUTATION test proving the
# gate still catches a genuinely removed title (a "fix" that never fails is not a fix).
set -uo pipefail
export LC_ALL=C
BASELINE="${GSC_BASELINE:-/opt/recursion/state/gsc/baseline-pass.txt}"
NOPROG=0; [ "${1:-}" = "--no-progress" ] && NOPROG=1
[ -f "$BASELINE" ] || { echo "GATE: no baseline at $BASELINE"; exit 3; }

# The baseline must be C-collated or every comparison below is unsound. A baseline pinned
# under a different locale is a harness fault, not a test result — fail loudly (exit 3)
# rather than emit a verdict from an invalid comparison.
if ! sort -c -u "$BASELINE" 2>/dev/null; then
  echo "GATE: HARNESS — baseline is not C-collated/unique: $BASELINE"
  echo "  re-pin it with:  LC_ALL=C sort -u <in> > $BASELINE"
  exit 3
fi

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

# A harness fault (node crash, wrong cwd, absent corpus) yields a tiny/empty pass set, which
# reads as a catastrophic regression. Name it as a harness fault instead of a code verdict.
if [ "$CUR" -eq 0 ]; then
  echo "GATE: HARNESS — zero passing tests parsed; the suite did not run (cwd? corpus? node?)"
  sed -n '1,15p' "$TAP"
  exit 3
fi

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

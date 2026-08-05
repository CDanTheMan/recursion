#!/usr/bin/env bash
# work.selftest.sh — the CONTROL for the build-loop gate.
#
# Lucas's rule, learned the hard way: a green accept-rate is NOT a sound harness. A gate is
# only trustworthy if a KNOWN-BAD task actually fails and escalates. So this runs two
# deterministic engine=none tasks (no AI, no cost, seconds):
#   selftest-green : acceptance `test -f ANCHOR.md`      -> MUST pass  (green path + integrate)
#   selftest-red   : acceptance `test -f __no_such__`    -> MUST fail  (retry->escalate path)
# and asserts each landed in the right terminal state. If the red one "passes", the gate is
# broken and the whole autonomy model is unsafe — so this exits nonzero and shouts.
#
# Self-cleaning: snapshots INBOX, uses temp task files, removes the test branches/worktrees.
set -uo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
TMP="$ROOT/state/.selftest"; rm -rf "$TMP"; mkdir -p "$TMP"
INBOX="$ROOT/state/INBOX.md"; INBOX_BAK="$TMP/INBOX.bak"; cp -f "$INBOX" "$INBOX_BAK" 2>/dev/null || : > "$INBOX_BAK"
fails=0
say(){ echo "[selftest] $*"; }
assert(){ if [ "$2" = "$3" ]; then say "PASS  $1 ($2)"; else say "FAIL  $1: expected '$3' got '$2'"; fails=$((fails+1)); fi; }

mktask(){ # id acceptance
  cat > "$TMP/$1.md" <<EOF
id: $1
workstream: selftest
goal: control task $1
engine: none
acceptance: $2
workdir: .
autonomy: auto
status: queued
EOF
}

status_of(){ sed -n 's/^status: *//p' "$1" | head -1 | tr -d '\r'; }
inbox_grew(){ ! diff -q "$INBOX" "$INBOX_BAK" >/dev/null 2>&1 && echo yes || echo no; }
branch_exists(){ git rev-parse --verify "$1" >/dev/null 2>&1 && echo yes || echo no; }

# --- GREEN: engine=none, acceptance true against a fresh worktree checkout --------------
mktask selftest-green "test -f ANCHOR.md"
RECURSION_NO_NOTIFY=1 bash scripts/work.sh "$TMP/selftest-green.md" >/dev/null 2>&1 || true
assert "green -> passed"        "$(status_of "$TMP/selftest-green.md")" "passed"
assert "green branch created"   "$(branch_exists loop/work/selftest-green)" "yes"

# --- RED: engine=none, acceptance can never pass -> must fail + escalate ----------------
cp -f "$INBOX" "$INBOX_BAK"   # reset the diff baseline before the red run
mktask selftest-red "test -f __definitely_absent_$$__"
RECURSION_NO_NOTIFY=1 bash scripts/work.sh "$TMP/selftest-red.md" >/dev/null 2>&1 || true
assert "red -> failed"          "$(status_of "$TMP/selftest-red.md")" "failed"
assert "red escalated to INBOX" "$(inbox_grew)" "yes"

# --- cleanup: restore INBOX, drop test branches + worktrees ----------------------------
cp -f "$INBOX_BAK" "$INBOX" 2>/dev/null || true
for b in selftest-green selftest-red; do
  git worktree remove --force "$ROOT/.worktrees/$b" >/dev/null 2>&1 || true
  git branch -D "loop/work/$b" >/dev/null 2>&1 || true
done
git worktree prune >/dev/null 2>&1 || true
rm -rf "$TMP"

echo
if [ "$fails" -eq 0 ]; then echo "[selftest] ALL PASS — the gate gates (green integrates, red escalates)."; exit 0
else echo "[selftest] $fails ASSERTION(S) FAILED — the gate is NOT sound. Do not trust auto-commit."; exit 1; fi

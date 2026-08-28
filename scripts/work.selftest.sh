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

# This is the CONTROL for the build-loop gate itself (flock, procfs, POSIX lock semantics) —
# off-box it cannot certify anything, so it reports an explicit SKIP instead of a false signal.
if [ "$(uname -s)" != "Linux" ]; then
  echo "[selftest] SKIP (Linux loop runtime required — the gate can only be certified on the box)"
  exit 0
fi

SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# ★ RUN IN A CLONE, NOT IN THE LIVE REPO. work.sh exits the moment it sees state/PAUSE, so on a
# correctly PAUSED box this test — the control that certifies the acceptance gate — could not run
# at all and reported FAILED. It passed all day on 2026-08-06 only because PAUSE had been
# accidentally deleted by a branch checkout; restoring the kill switch turned it red. A test that
# silently requires the safety system to be OFF is not a test of the gate.
#
# The clone also stops this leaking selftest branches, INBOX entries and board rows into the live
# repo on every run — the same fixture-leak pattern that had other tests fetching real repos and
# paging Lucas earlier the same day.
CLONE="$(mktemp -d)/selftest-repo"
git clone -q --local --no-hardlinks "$SRC" "$CLONE" 2>/dev/null || { echo "[selftest] could not clone $SRC"; exit 3; }
ROOT="$CLONE"
cd "$ROOT"
rm -f state/PAUSE                      # the clone is a sandbox; the live box stays exactly as it is
git checkout -q -b selftest-run 2>/dev/null || true
# The clone's origin is the live repo, so freshness checks resolve offline against a real remote.
printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > state/portfolio.tsv
printf 'selftest\t%s\t%s\t%s\t-\t-\t-\tactive\n' "$ROOT" "$SRC" \
  "$(git -C "$SRC" rev-parse --abbrev-ref HEAD)" >> state/portfolio.tsv
export RECURSION_ROOT="$ROOT" RECURSION_NO_NOTIFY=1
trap 'rm -rf "$(dirname "$CLONE")"' EXIT

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
# Nothing to unpick: the whole clone is deleted by the EXIT trap. The live repo was never
# touched, so there are no selftest branches, worktrees or INBOX entries to clean out of it.

echo
if [ "$fails" -eq 0 ]; then echo "[selftest] ALL PASS — the gate gates (green integrates, red escalates)."; exit 0
else echo "[selftest] $fails ASSERTION(S) FAILED — the gate is NOT sound. Do not trust auto-commit."; exit 1; fi

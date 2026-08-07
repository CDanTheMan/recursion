#!/usr/bin/env bash
# killswitch.test.sh — PAUSE must survive the ordinary operation of git, and the runtime branch
# must carry the code that was reviewed.
#
# WHY. All three of these were live failures on 2026-08-06, from ONE `git checkout master` run to
# fast-forward master during review:
#   - PAUSE was a TRACKED file present on loop/auto and absent on master, so the checkout deleted
#     it and the box went live with RECURSION_AUTO_DRAIN=1. Nothing ran only because the queue was
#     empty. A safety control whose presence depends on the current branch is not one.
#   - state/BOARD.md is RENDERED and tracked, so it is dirty nearly always, and a dirty tracked
#     file makes `git checkout` refuse — run.sh could not get back to its own branch, and the
#     heartbeat and the daily brief failed on every cycle for fourteen hours while the per-project
#     digests kept arriving. The visible half of the system looked fine.
#   - run.sh's way of staying current was `git merge --ff-only`, which CANNOT succeed on a branch
#     that accumulates its own ledger commits. It had been failing silently under `|| true` since
#     the first one, and the runtime branch was 21 commits behind master.
#
# ★ Each test therefore checks a property of the SYSTEM under ordinary git use, not a unit.
#
#   run: bash scripts/tests/killswitch.test.sh
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

export RECURSION_NO_NOTIFY=1
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
R="$TMP/repo"; mkdir -p "$R/state" "$R/scripts"
GIT="git -c user.name=t -c user.email=t@t -c init.defaultBranch=master"

# A repo shaped like the real one: a default branch, a ledger branch that gains its own commits,
# a tracked rendered board, and the project's .gitignore.
cp "$SRC/.gitignore" "$R/.gitignore"
( cd "$R" && $GIT init -q .
  printf 'board v1\n' > state/BOARD.md
  printf 'code v1\n'  > scripts/thing.sh
  $GIT add -A && $GIT commit -qm "base"
  $GIT checkout -qb loop/auto
  printf 'PAUSED\nreason: test\n' > state/PAUSE
  # The ledger branch also re-renders the board, so BOARD.md DIFFERS between the branches.
  # That difference is what makes git refuse a checkout when the working copy is dirty too —
  # with identical content on both sides git just carries the local edit across and nothing
  # blocks, which is why the first version of this test could not reproduce the bug.
  printf 'board v1-ledger\n' > state/BOARD.md
  $GIT add -A && $GIT commit -qm "loop: ledger commit with PAUSE"
  $GIT checkout -q master
  printf 'code v2 (reviewed)\n' > scripts/thing.sh
  $GIT add -A && $GIT commit -qm "reviewed change"
  $GIT checkout -q loop/auto ) >/dev/null 2>&1

# --- 1) ★ THE KILL SWITCH SURVIVES A BRANCH SWITCH -----------------------------------------
# This is the whole branch. Switching to the default branch and back must not disarm the box.
[ -f "$R/state/PAUSE" ] || no "fixture is wrong: PAUSE missing before the test"
( cd "$R" && $GIT checkout -q master ) >/dev/null 2>&1
if [ -f "$R/state/PAUSE" ]; then
  ok "★ PAUSE survives \`git checkout master\` (the kill switch is not branch-dependent)"
else
  no "★ THE KILL SWITCH IS BRANCH-DEPENDENT — checkout deleted state/PAUSE and the box went live"
fi
( cd "$R" && $GIT checkout -q loop/auto ) >/dev/null 2>&1

# ★ CONTROL: PAUSE must still be REMOVABLE, or "it survives" is satisfied by a file nothing can
# clear — which would be a box that can never be resumed.
rm -f "$R/state/PAUSE"
[ ! -f "$R/state/PAUSE" ] && ok "★ CONTROL — PAUSE can still be cleared (resume.sh still works)" \
                          || no "★ PAUSE could not be removed — the box could never resume"
printf 'PAUSED\nreason: test\n' > "$R/state/PAUSE"

# --- 2) a RENDERED tracked file must not block the branch switch ------------------------------
# The board is re-rendered constantly, so it is dirty nearly always. If that blocks checkout, the
# supervisor cannot reach its own branch and every model-driven job dies while the rest looks fine.
( cd "$R" && $GIT checkout -q master ) >/dev/null 2>&1
printf 'board v2 (rendered since)\n' > "$R/state/BOARD.md"
out="$( cd "$R" && $GIT checkout -q loop/auto 2>&1 )"; rc=$?
if [ "$rc" != "0" ] && printf '%s' "$out" | grep -q 'would be overwritten'; then
  ok "reproduced: a dirty rendered board DOES block the switch (this is the bug run.sh must handle)"
else
  no "could not reproduce the blocking checkout — the rest of this test proves nothing"
fi
# run.sh's fix: discard the rendered file first, because it is regenerated every run.
( cd "$R" && $GIT checkout -q -- state/BOARD.md && $GIT checkout -q loop/auto ) >/dev/null 2>&1
cur="$( cd "$R" && $GIT rev-parse --abbrev-ref HEAD )"
[ "$cur" = "loop/auto" ] && ok "discarding the rendered board lets the supervisor reach its branch" \
                         || no "still stuck on $cur"

# --- 3) ★ --ff-only CANNOT keep the runtime branch current ---------------------------------------
# The property that made the drift silent: loop/auto has its own commits, so it is never a strict
# ancestor of master, so --ff-only always fails — and it was wrapped in `|| true`.
( cd "$R" && $GIT merge -q --ff-only master ) >/dev/null 2>&1; ffrc=$?
behind="$( cd "$R" && $GIT rev-list --count loop/auto..master )"
if [ "$ffrc" != "0" ] && [ "$behind" -gt 0 ]; then
  ok "★ --ff-only cannot merge the default branch into a ledger branch (why the drift was silent)"
else
  no "★ the premise is wrong: ff-only returned $ffrc, behind=$behind"
fi

# --- 4) ★ a real merge DOES carry the reviewed code into the runtime branch ---------------------
( cd "$R" && $GIT merge -q --no-edit master ) >/dev/null 2>&1
behind="$( cd "$R" && $GIT rev-list --count loop/auto..master )"
code="$(cat "$R/scripts/thing.sh")"
if [ "$behind" = "0" ] && [ "$code" = "code v2 (reviewed)" ]; then
  ok "★ a real merge brings the REVIEWED code into the runtime branch (0 behind, v2 on disk)"
else
  no "★ the runtime branch still lags: behind=$behind code='$code'"
fi
[ -f "$R/state/PAUSE" ] && ok "and the merge did not disturb PAUSE" || no "the merge cleared PAUSE"

# --- 5) the real repo: PAUSE is ignored, not tracked ---------------------------------------------
if git -C "$SRC" check-ignore -q state/PAUSE 2>/dev/null; then
  ok "the live repo ignores state/PAUSE"
else
  no "state/PAUSE is still tracked in the live repo — a checkout can still disarm the box"
fi

echo
[ "$fails" -eq 0 ] && { echo "killswitch: ALL PASS"; exit 0; }
echo "killswitch: $fails FAILED"; exit 1

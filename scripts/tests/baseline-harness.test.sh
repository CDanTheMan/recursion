#!/usr/bin/env bash
# The Gate-6 baseline is evidence from a fresh reviewed clone, never the deployed runtime tree.
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }
sk(){ printf 'SKIP  %s\n' "$1"; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
R="$TMP/reviewed"; LIVE="$TMP/live"; NONGIT="$TMP/non-git-live"; LINKED="$TMP/linked"
mkdir -p "$R/scripts/tests" "$R/state" "$LIVE/state" "$NONGIT/state"
printf '#!/usr/bin/env bash\nexit 0\n' > "$R/scripts/tests/control.test.sh"
printf '#!/usr/bin/env bash\nexit 0\n' > "$R/scripts/work.selftest.sh"
chmod +x "$R/scripts/tests/control.test.sh" "$R/scripts/work.selftest.sh"
git -C "$R" init -q
# Fixture-local only: a Windows dev box has core.autocrlf=true globally, and these throwaway
# clones would otherwise be rewritten to CRLF on checkout (plus a warning per file). The Linux
# box already has autocrlf off, so this pins the behaviour it already has.
git -C "$R" config core.autocrlf false; git -C "$R" config core.eol lf
git -C "$R" add scripts
git -C "$R" -c user.name=t -c user.email=t@t commit -qm fixture
git -C "$R" checkout -qb reviewed
git -C "$LIVE" init -q
git -C "$LIVE" config core.autocrlf false; git -C "$LIVE" config core.eol lf
printf 'deployed fixture\n' > "$LIVE/deployed.txt"
git -C "$LIVE" add deployed.txt
git -C "$LIVE" -c user.name=t -c user.email=t@t commit -qm deployed
git -C "$LIVE" checkout -qb deployed
printf 'fixture pause\n' > "$R/state/PAUSE"

same_out="$(RECURSION_ROOT="$R" RECURSION_LIVE_ROOT="$R" \
  bash "$SRC/scripts/audit/hermes-pilot-phase0-baseline.sh" 2>&1)"
same_rc=$?
if [ "$same_rc" = 3 ] && printf '%s' "$same_out" | grep -q 'independent reviewed clone'; then
  ok "baseline refuses to audit the deployed runtime checkout as its reviewed source"
else
  no "baseline accepted the deployed runtime checkout (rc=$same_rc): $same_out"
fi

# PLATFORM-BOUND (verified 2026-08-27): this one check is skipped off Linux, and only this one.
# On Windows Git Bash, `git rev-parse --git-common-dir` answers from inside a LINKED worktree with
# a Windows-form absolute path ("C:/…/reviewed/.git"). The audited script treats a common-dir as
# absolute only when it begins with "/", so it appends that answer to the worktree path, the
# subsequent `cd` fails, and git_common_physical returns 1. The refusal DOES still fire — rc=3 —
# but through "reviewed root is not a Git checkout", not the shared-Git-authority comparison this
# check exists to pin. Asserting on the wrong refusal would prove nothing, and loosening the grep
# to any rc=3 would let a real regression in the common-dir comparison pass. The audited script is
# read-only here; the production fix is recorded rather than applied. On Linux the check is
# unchanged and still runs.
if [ "$(uname -s)" = Linux ]; then
  git -C "$R" worktree add -qb linked "$LINKED"
  linked_out="$(RECURSION_ROOT="$LINKED" RECURSION_LIVE_ROOT="$R" \
    bash "$SRC/scripts/audit/hermes-pilot-phase0-baseline.sh" 2>&1)"
  linked_rc=$?
  if [ "$linked_rc" = 3 ] && printf '%s' "$linked_out" | grep -q 'independent reviewed clone'; then
    ok "baseline refuses a linked worktree that shares deployed Git authority"
  else
    no "baseline accepted a linked deployed worktree (rc=$linked_rc): $linked_out"
  fi
else
  sk "linked-worktree shared-Git-authority refusal on $(uname -s): git rev-parse --git-common-dir returns a Windows-form path (C:/...) that hermes-pilot-phase0-baseline.sh classifies as relative, so the refusal arrives as 'reviewed root is not a Git checkout' instead of 'independent reviewed clone'. The other three checks below still run."
fi

rm -f -- "$R/state/PAUSE"
printf 'fixture pause\n' > "$LIVE/state/PAUSE"
separate_out="$(GIT_DIR="$R/.git" GIT_COMMON_DIR="$R/.git" GIT_WORK_TREE="$R" \
  RECURSION_ROOT="$R" RECURSION_LIVE_ROOT="$LIVE" \
  bash "$SRC/scripts/audit/hermes-pilot-phase0-baseline.sh" 2>&1)"
separate_rc=$?
live_head="$(git -C "$LIVE" rev-parse HEAD)"
if [ "$separate_rc" = 0 ] \
  && printf '%s' "$separate_out" | grep -q "DEPLOYED_COMMIT=$live_head" \
  && printf '%s' "$separate_out" | grep -q 'BASELINE_FAILED_SUITES=0'; then
  ok "control: a separate named reviewed clone ignores inherited Git overrides"
else
  no "baseline rejected a separate reviewed clone (rc=$separate_rc): $separate_out"
fi

printf 'fixture pause\n' > "$NONGIT/state/PAUSE"
nongit_out="$(RECURSION_ROOT="$R" RECURSION_LIVE_ROOT="$NONGIT" \
  bash "$SRC/scripts/audit/hermes-pilot-phase0-baseline.sh" 2>&1)"
nongit_rc=$?
if [ "$nongit_rc" = 90 ] && printf '%s' "$nongit_out" | grep -q 'live root is not a Git checkout'; then
  ok "baseline fails closed when deployed commit evidence is unavailable"
else
  no "baseline accepted a non-Git deployed root (rc=$nongit_rc): $nongit_out"
fi

printf '\nbaseline-harness: %s\n' "$([ "$fails" -eq 0 ] && echo 'ALL PASS' || echo "$fails FAILED")"
[ "$fails" -eq 0 ]

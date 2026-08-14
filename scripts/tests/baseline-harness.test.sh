#!/usr/bin/env bash
# The Gate-6 baseline is evidence from a fresh reviewed clone, never the deployed runtime tree.
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
R="$TMP/reviewed"; LIVE="$TMP/live"
mkdir -p "$R/scripts/tests" "$R/state" "$LIVE/state"
printf '#!/usr/bin/env bash\nexit 0\n' > "$R/scripts/tests/control.test.sh"
printf '#!/usr/bin/env bash\nexit 0\n' > "$R/scripts/work.selftest.sh"
chmod +x "$R/scripts/tests/control.test.sh" "$R/scripts/work.selftest.sh"
git -C "$R" init -q
git -C "$R" add scripts
git -C "$R" -c user.name=t -c user.email=t@t commit -qm fixture
git -C "$R" checkout -qb reviewed
printf 'fixture pause\n' > "$R/state/PAUSE"

same_out="$(RECURSION_ROOT="$R" RECURSION_LIVE_ROOT="$R" \
  bash "$SRC/scripts/audit/hermes-pilot-phase0-baseline.sh" 2>&1)"
same_rc=$?
if [ "$same_rc" = 3 ] && printf '%s' "$same_out" | grep -q 'fresh reviewed clone'; then
  ok "baseline refuses to audit the deployed runtime checkout as its reviewed source"
else
  no "baseline accepted the deployed runtime checkout (rc=$same_rc): $same_out"
fi

rm -f -- "$R/state/PAUSE"
printf 'fixture pause\n' > "$LIVE/state/PAUSE"
separate_out="$(RECURSION_ROOT="$R" RECURSION_LIVE_ROOT="$LIVE" \
  bash "$SRC/scripts/audit/hermes-pilot-phase0-baseline.sh" 2>&1)"
separate_rc=$?
if [ "$separate_rc" = 0 ] && printf '%s' "$separate_out" | grep -q 'BASELINE_FAILED_SUITES=0'; then
  ok "control: a separate named reviewed clone runs the baseline"
else
  no "baseline rejected a separate reviewed clone (rc=$separate_rc): $separate_out"
fi

printf '\nbaseline-harness: %s\n' "$([ "$fails" -eq 0 ] && echo 'ALL PASS' || echo "$fails FAILED")"
[ "$fails" -eq 0 ]

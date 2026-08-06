#!/usr/bin/env bash
# resync.test.sh — freshness must be PROVEN, and "I could not check" must never read as "fine".
#
# WHY THESE TESTS. Two failures on this box motivated the whole branch, and both are the same
# shape: an operation that could not answer, answering "clean" anyway.
#   - `git ls-remote` with no usable key prints nothing and exits 0-ish; the caller reads that as
#     "this repo has no branches". Test 6 is that exact case and it must come back as a FAULT.
#   - work.sh fetched, failed, logged "building on local base", and built anyway — so the arm
#     built on a stale tree, the gate passed (it was testing the old tree), and merging the
#     result would revert whatever had been fixed upstream. Test 11 is that case.
#
# ★ Tests 1, 3b and 10 are CONTROLS. Without them every refusal here would also pass on a
#   resync.sh that refuses everything and a work.sh that builds nothing — which is the way this
#   suite would be worthless while scoring full marks.
#
# Hermetic: local bare repos as origins (file:// needs no credential), a temp registry, no
# network, no keys, no spend.
#
#   run: bash scripts/tests/resync.test.sh
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

command -v git >/dev/null 2>&1 || { echo "resync.test: git is required"; exit 3; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
R="$TMP/root"; mkdir -p "$R/scripts/tests" "$R/state/tasks" "$R/state/roadmaps" "$R/loop/logs" "$TMP/origins"
for s in resync.sh taskctl.sh notify.sh work.sh board.sh publish.sh; do
  cp "$SRC/scripts/$s" "$R/scripts/" 2>/dev/null || true
done
chmod +x "$R"/scripts/*.sh 2>/dev/null
: > "$R/.env"; : > "$R/state/INBOX.md"; echo "anchor" > "$R/ANCHOR.md"
export RECURSION_NO_NOTIFY=1
GIT="git -c user.name=t -c user.email=t@t -c init.defaultBranch=main -c advice.detachedHead=false"

# --- fixtures: <name> gets an origin bare repo and a clone --------------------------------
mkrepo(){ # mkrepo <name>
  local n="$1" o="$TMP/origins/$n.git" c="$TMP/$n"
  $GIT init -q --bare "$o"
  $GIT init -q "$c"; ( cd "$c" && echo one > f.txt && $GIT add -A && $GIT commit -qm one \
    && $GIT branch -M main && $GIT remote add origin "$o" && $GIT push -q origin main \
    && $GIT branch --set-upstream-to=origin/main main ) >/dev/null 2>&1
  $GIT -C "$c" fetch -q origin
}
# advance the ORIGIN without the clone knowing (the normal "someone merged a PR" case)
advance_origin(){ # advance_origin <name> <msg>
  local n="$1" w="$TMP/.adv-$n"; rm -rf "$w"
  $GIT clone -q "$TMP/origins/$n.git" "$w" >/dev/null 2>&1
  ( cd "$w" && echo "$2" >> f.txt && $GIT add -A && $GIT commit -qm "$2" && $GIT push -q origin main ) >/dev/null 2>&1
  rm -rf "$w"
}
for n in insync behind diverged unreachable emptyremote; do mkrepo "$n"; done

# 'emptyremote' authenticates perfectly and simply answers with no heads. This is the trap:
# it is indistinguishable from a successful probe of a repo that has branches, unless someone
# decides in advance that zero refs means the probe failed.
$GIT init -q --bare "$TMP/origins/empty.git"
$GIT -C "$TMP/emptyremote" remote set-url origin "$TMP/origins/empty.git"
$GIT -C "$TMP/unreachable" remote set-url origin "$TMP/origins/does-not-exist.git"

reg(){ printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$TMP/$1" "file://$TMP/origins/$1.git" main - - - "$2"; }
{ printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n'
  reg insync active; reg behind active; reg diverged active
  reg unreachable active; reg emptyremote active
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' notyet "$TMP/notyet" "file://$TMP/origins/notyet.git" main - - - pending
} > "$R/state/portfolio.tsv"

rs(){ ( cd "$R" && RECURSION_ROOT="$R" bash scripts/resync.sh "$@" ) >"$TMP/out" 2>&1; echo $?; }

# --- 1) ★ CONTROL: a repo that IS current reports fresh -------------------------------------
# The refusal text ("CANNOT PROVE FRESH") contains the word 'fresh', so every assertion about
# freshness matches the SUCCESS line's shape ("<project> fresh: origin/<branch> @ <sha>") rather
# than the bare word — an assertion that both outcomes satisfy is not an assertion.
rc=$(rs check insync)
if [ "$rc" = "0" ] && grep -q 'fresh: origin/' "$TMP/out"; then
  ok "★ CONTROL — an in-sync repo checks fresh (resync is not just refusing everything)"
else
  no "★ CONTROL FAILED — an in-sync repo did not check fresh (rc=$rc): $(cat "$TMP/out")"
fi

# --- 2) the registry is the single source of truth for repo -> deploy key -------------------
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' keyed "$TMP/insync" x main "$TMP/fake.key" - - active >> "$R/state/portfolio.tsv"
rc=$(rs key keyed)
[ "$rc" = "0" ] && grep -q 'fake.key' "$TMP/out" && ok "key: the registry answers repo -> deploy key" \
  || no "key: registry lookup failed (rc=$rc): $(cat "$TMP/out")"
rc=$(rs key nosuchproject)
[ "$rc" != "0" ] && ok "key: an unregistered repo has no key (and says so)" || no "key: invented a key for an unknown repo"

# --- 3) BEHIND: visible, non-blocking, and fast-forwardable ---------------------------------
advance_origin behind two
rc=$(rs check behind)
[ "$rc" = "0" ] && ok "a repo merely BEHIND still checks fresh (the build bases on origin/main)" \
  || no "a fast-forwardable repo was treated as unfit (rc=$rc)"
rc=$(rs status)
grep -q 'BEHIND' "$TMP/out" && ok "status names the drift instead of hiding it" || no "status did not report BEHIND"

# 3b) ★ CONTROL: sync must actually fast-forward, or 'refuses to sync' below proves nothing.
before="$($GIT -C "$TMP/behind" rev-parse main)"
rc=$(rs sync behind)
after="$($GIT -C "$TMP/behind" rev-parse main)"
if [ "$before" != "$after" ] && [ "$($GIT -C "$TMP/behind" rev-parse main)" = "$($GIT -C "$TMP/behind" rev-parse origin/main)" ]; then
  ok "★ CONTROL — sync fast-forwards a behind repo onto origin/main"
else
  no "★ CONTROL FAILED — sync did not fast-forward (before=$before after=$after)"
fi

# --- 4) DIVERGED needs a human, and sync must not "fix" it by rewriting anything -------------
advance_origin diverged remote-side
( cd "$TMP/diverged" && echo local-side >> f.txt && $GIT add -A && $GIT commit -qm local-side ) >/dev/null 2>&1
$GIT -C "$TMP/diverged" fetch -q origin
localtip="$($GIT -C "$TMP/diverged" rev-parse main)"
rc=$(rs check diverged)
[ "$rc" = "4" ] && ok "a DIVERGED repo needs a human (exit 4, distinct from 'cannot prove')" \
  || no "diverged repo returned $rc, expected 4"
rc=$(rs sync diverged)
if [ "$($GIT -C "$TMP/diverged" rev-parse main)" = "$localtip" ] && [ "$rc" != "0" ]; then
  ok "sync REFUSES to reconcile divergence and leaves local history untouched"
else
  no "sync altered a diverged branch (tip moved) or reported success"
fi

# --- 5) an unreachable remote cannot prove anything -----------------------------------------
rc=$(rs check unreachable)
if [ "$rc" = "3" ] && ! grep -q 'fresh: origin/' "$TMP/out"; then
  ok "an unreachable origin is 'cannot prove' (exit 3) and is never called fresh"
else
  no "unreachable origin returned $rc: $(cat "$TMP/out")"
fi

# --- 6) ★ THE TRAP: a remote that answers with ZERO refs is a failed probe, not an empty repo -
rc=$(rs check emptyremote)
if [ "$rc" = "3" ]; then
  ok "★ zero refs from origin is a FAULT, not a clean 'no branches' (the ls-remote trap)"
else
  no "★ TRAP OPEN — a zero-ref probe returned $rc; an auth failure will read as a clean result"
fi

# --- 7) an unregistered repo is not a pass ---------------------------------------------------
rc=$(rs check "$TMP/insync-unregistered")
[ "$rc" = "3" ] && ok "an unregistered repo cannot be proven fresh (exit 3, not 0)" \
  || no "an unregistered repo returned $rc"

# --- 8) status=pending is registered but not dispatchable ------------------------------------
rc=$(rs check notyet)
[ "$rc" = "4" ] && ok "a pending (not yet cloned) repo is refused for dispatch" || no "pending repo returned $rc"

# --- 9) repeated faults are ONE escalation with a sighting count, not a new item each run -----
rs sync unreachable >/dev/null 2>&1; rs sync unreachable >/dev/null 2>&1
n="$( ( cd "$R" && RECURSION_ROOT="$R" bash scripts/taskctl.sh esc-list open 2>/dev/null ) | grep -c 'resync-auth-unreachable' )"
c="$( ( cd "$R" && RECURSION_ROOT="$R" bash scripts/taskctl.sh esc-list open 2>/dev/null ) | awk -F'\t' '/resync-auth-unreachable/{print $6; exit}' )"
if [ "$n" = "1" ] && [ "${c:-0}" -ge 2 ]; then
  ok "a fault seen twice is ONE escalation with count=$c (dedup holds)"
else
  no "escalation dedup broke: $n item(s), count=${c:-?}"
fi

# ============================================================================================
# work.sh integration — the actual defect this branch closes.
# ============================================================================================
mktask(){ # mktask <id> <repo-path>
  cat > "$R/state/tasks/$1.md" <<EOF
id: $1
workstream: resynctest
goal: prove the freshness precondition
engine: none
acceptance: true
repo: $2
workdir: .
autonomy: auto
status: queued
EOF
}
run_work(){ ( cd "$R" && RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 bash scripts/work.sh "$1" ) >"$TMP/w.out" 2>&1; }
st(){ sed -n 's/^status: *//p' "$R/state/tasks/$1.md" | head -1 | tr -d '\r'; }

# --- 10) ★ CONTROL: against a FRESH repo the build proceeds normally --------------------------
mktask fresh-ok "$TMP/insync"
run_work fresh-ok
# work.sh removes the worktree when it finishes but keeps loop/work/<id> "for review", so the
# BRANCH is the durable evidence that a build ran — the directory is not.
built(){ $GIT -C "$1" rev-parse --verify --quiet "refs/heads/loop/work/$2" >/dev/null 2>&1 && echo yes || echo no; }
if [ "$(st fresh-ok)" = "passed" ] && [ "$(built "$TMP/insync" fresh-ok)" = "yes" ]; then
  ok "★ CONTROL — a task against a fresh repo builds (status=passed, worktree created)"
else
  no "★ CONTROL FAILED — a fresh repo did not build (status=$(st fresh-ok)); test 11 proves nothing"
  tail -5 "$TMP/w.out" | sed 's/^/        /'
fi

# --- 11) ★ the defect: a repo whose freshness cannot be proven must NOT be built on -----------
# Pre-change work.sh logged "fetch skipped/failed — building on local base" and carried on: the
# worktree was created and the arm ran against a stale tree. The two observable differences are
# that no worktree exists and the escalation names the BASE rather than the arm.
mktask stale-block "$TMP/unreachable"
run_work stale-block
wt_made="$(built "$TMP/unreachable" stale-block)"
if [ "$wt_made" = "no" ] && [ "$(st stale-block)" = "blocked" ]; then
  ok "★ a task against an unprovable base is BLOCKED before any build happens"
else
  no "★ THE DEFECT IS OPEN — built=$wt_made status=$(st stale-block); pre-change this task PASSED while its origin was unreachable"
fi
grep -qi 'current with origin\|cannot prove' "$R/state/INBOX.md" \
  && ok "the escalation names the base, not a downstream symptom" \
  || no "the escalation does not explain that the base could not be proven"

# --- 12) the off-switch is explicit, and says so ---------------------------------------------
mktask override "$TMP/unreachable"
( cd "$R" && RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 RECURSION_REQUIRE_FRESH_BASE=0 \
    bash scripts/work.sh override ) >"$TMP/w2.out" 2>&1
if [ "$(st override)" != "blocked" ] && grep -q 'FRESH-BASE CHECK DISABLED' "$R/loop/logs/"*.log 2>/dev/null; then
  ok "RECURSION_REQUIRE_FRESH_BASE=0 overrides the gate and LOGS that it did"
else
  no "the documented override did not work, or did not announce itself"
fi

echo
[ "$fails" -eq 0 ] && { echo "resync: ALL PASS"; exit 0; }
echo "resync: $fails FAILED"; exit 1

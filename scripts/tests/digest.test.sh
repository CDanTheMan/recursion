#!/usr/bin/env bash
# digest.test.sh — a project's status must be true, and must say so when it cannot be.
#
# WHY. The digest is what makes a topic into a pilot: the gateway already keys a conversational
# session per (chat, thread), so posting a project's facts into its topic is what gives the
# session Lucas talks to any idea which project it belongs to. That only works if the facts are
# facts — a digest that states a confident repo status it could not actually verify is worse than
# no digest, because it will be believed and then quoted back.
#
# ★ Test 1 is the CONTROL: a healthy project must produce a real digest naming real state.
#
#   run: bash scripts/tests/digest.test.sh
set -uo pipefail
export LC_ALL=C

# This suite drives the live loop arms (flock, procfs, POSIX lock semantics) — off-box it can only
# produce noise, so it reports an explicit SKIP. The box baseline runs it for real.
if [ "$(uname -s)" != "Linux" ]; then
  echo "digest: SKIP (Linux loop runtime required — flock/procfs/POSIX lock semantics; certified in the box suite)"
  exit 0
fi

SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

export RECURSION_NO_NOTIFY=1
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
R="$TMP/root"; mkdir -p "$R/scripts" "$R/state/tasks" "$R/state/roadmaps" "$R/state/assists" "$R/loop/logs"
for s in assignment.py assist.sh author.sh board.sh capacity.sh conduct.sh digest.sh engine_contract.py git-scope.py \
  instruction_routing.py intake.sh jsonl_durable.py notify.sh pilot_instruction.py plan.sh project-pilot.py \
  project-reconcile.py project_authority.py provider-connect-proxy.py provider_contract.py provider-network.sh provider-egress.py publish.sh \
  remote_evidence.py resolve-engine.py resolve-model-alias.py resync.sh run_contract.py runtime-state.py \
  seed_contract.py taskctl.sh transition_receipt.py validate-assignment-result.py validate-control-state.py \
  validate-decision.py validate-gate.py validate-verifier-result.py validate-worker-result.py work.sh assignment-token.py \
  worker-evidence.py worker-sandbox.sh; do
  cp "$SRC/scripts/$s" "$R/scripts/"
done
chmod +x "$R"/scripts/*.sh 2>/dev/null
: > "$R/.env"

GIT="git -c user.name=t -c user.email=t@t -c init.defaultBranch=main"
mk(){ local n o c
  n="$1"; o="$TMP/$n.git"; c="$TMP/$n"   # separate statements: a `local a=$1 b=$a` chain is not reliably left-to-right under set -u
  $GIT init -q --bare "$o"
  $GIT init -q "$c"; ( cd "$c" && echo x > f.txt && $GIT add -A && $GIT commit -qm init \
    && $GIT branch -M main && $GIT remote add origin "$o" && $GIT push -q origin main \
    && $GIT checkout -qb review/some-work && echo y >> f.txt && $GIT add -A \
    && $GIT commit -qm work && $GIT push -q origin review/some-work \
    && $GIT checkout -q main ) >/dev/null 2>&1
  $GIT -C "$c" fetch -q origin; $GIT -C "$c" remote set-head origin -a >/dev/null 2>&1
}
mk good; mk broken
$GIT -C "$TMP/broken" remote set-url origin "$TMP/gone.git"

{ printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n'
  printf 'good\t%s\t%s\tmain\t-\tstate/roadmaps/goodws.md\t7\tactive\n'  "$TMP/good" "$TMP/good.git"
  printf 'broken\t%s\t%s\tmain\t-\t-\t8\tactive\n' "$TMP/broken" "$TMP/gone.git"
  printf 'later\t/opt/later\tgit@github.com:x/l.git\tmain\t-\t-\t-\tpending\n'
} > "$R/state/portfolio.tsv"
cat > "$R/state/roadmaps/goodws.md" <<'T'
engine: claude
acceptance: true

- [x] something finished
- [ ] the very next thing
T
cat > "$R/state/tasks/g1.md" <<'T'
id: g1
workstream: goodws
status: queued
T
cat > "$R/state/tasks/g2.md" <<'T'
id: g2
workstream: goodws
status: blocked
T

dg(){ ( cd "$R" && RECURSION_ROOT="$R" bash scripts/digest.sh "$@" ) >"$TMP/out" 2>&1; echo $?; }

# --- 1) ★ CONTROL: a healthy project renders real state ---------------------------------------
rc=$(dg good --print)
if [ "$rc" = "0" ] && grep -q '📋 good' "$TMP/out" && grep -q 'origin/main @' "$TMP/out"; then
  ok "★ CONTROL — a healthy project renders a digest naming its real repo state"
else
  no "★ CONTROL FAILED — no usable digest (rc=$rc): $(cat "$TMP/out")"
fi
grep -q 'the very next thing' "$TMP/out" && ok "the digest shows the next unchecked roadmap items" \
                                         || no "roadmap next-items missing"
grep -q '1 queued' "$TMP/out" && grep -q '1 blocked' "$TMP/out" \
  && ok "task counts are per-workstream, from the task files" || no "task counts wrong: $(grep tasks: "$TMP/out")"

# --- 2) ★ a repo it cannot reach is NOT reported as fine ----------------------------------------
rc=$(dg broken --print)
if grep -q 'CANNOT VERIFY\|NEEDS YOU' "$TMP/out"; then
  ok "★ an unreachable repo is reported as unverified, never as a confident status"
else
  no "★ a broken repo produced a confident claim: $(grep '^repo:' "$TMP/out")"
fi

# --- 3) the review-branch list is REVIEW branches ------------------------------------------------
# origin/HEAD shortens to a bare "origin", which the first version listed as a branch awaiting
# review. A digest that invents work items is a digest that gets ignored.
dg good --print >/dev/null
if grep -q 'review/some-work' "$TMP/out" && ! grep -qE '^  · (origin|HEAD|main)$' "$TMP/out"; then
  ok "review branches are listed; origin/HEAD, main and HEAD are not"
else
  no "review-branch list is wrong: $(sed -n '/awaiting/,$p' "$TMP/out")"
fi

# --- 4) --all covers every ACTIVE project and skips pending ones ---------------------------------
rc=$(dg --all)
if grep -q 'good' "$TMP/out" && grep -q 'broken' "$TMP/out" && ! grep -q 'later' "$TMP/out"; then
  ok "--all digests every active project and skips pending ones (they have no clone)"
else
  no "--all covered the wrong set: $(cat "$TMP/out")"
fi

# --- 5) an unknown project fails closed -----------------------------------------------------------
rc=$(dg no-such-project --print)
[ "$rc" != "0" ] && ok "an unregistered project produces no digest" || no "a digest was invented"

echo
[ "$fails" -eq 0 ] && { echo "digest: ALL PASS"; exit 0; }
echo "digest: $fails FAILED"; exit 1

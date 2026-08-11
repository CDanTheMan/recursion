#!/usr/bin/env bash
# Positive controls: the hardened worker can perform bounded work and the publisher can publish
# a canonical review ref without changing the registered default branch.
set -euo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/bin"; R="$TMP/controller"; ORIGIN="$TMP/origin.git"
mkdir -p "$BIN" "$R/scripts" "$R/state/tasks" "$R/loop/logs" "$R/app"
for s in work.sh worker-sandbox.sh publish.sh taskctl.sh jsonl_durable.py transition_receipt.py \
         runtime-state.py board.sh notify.sh resync.sh capacity.sh; do
  cp "$SRC/scripts/$s" "$R/scripts/"
done
chmod +x "$R/scripts/"*.sh
cat > "$BIN/claude" <<'STUB'
#!/usr/bin/env bash
bash -c "${STUB_ARM_SCRIPT:-:}"
STUB
chmod +x "$BIN/claude"
: > "$R/.env"; echo seed > "$R/app/seed.txt"
git -c init.defaultBranch=main init -q --bare "$ORIGIN"
git -c init.defaultBranch=main init -q "$R"
git -C "$R" add -A
git -C "$R" -c user.name=t -c user.email=t@t commit -qm init
git -C "$R" branch -M main; git -C "$R" remote add origin "$ORIGIN"
git -C "$R" push -q origin main; git -C "$R" fetch -q origin
printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > "$R/state/portfolio.tsv"
printf 'phase1\t%s\t%s\tmain\t%s\t-\t-\tactive\n' "$R" "$ORIGIN" "$TMP/publisher-key" >> "$R/state/portfolio.tsv"

cat > "$R/state/tasks/sandbox-ok.md" <<T
id: sandbox-ok
workstream: phase1
goal_id: phase1-goal
goal: prove the unprivileged sandbox can write only its worktree
engine: claude
repo: $R
acceptance: test -f app/ok.txt && test -s app/uid.txt
workdir: .
allowed_paths: app
autonomy: auto
network_policy: none
status: queued
T
(
  umask 0077
  STUB_ARM_SCRIPT='mkdir -p app; id -u > app/uid.txt; echo ok > app/ok.txt' \
  PATH="$BIN:$PATH" RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 RECURSION_GIT_FETCH=0 \
  RECURSION_REQUIRE_FRESH_BASE=0 RECURSION_TEST_WORKER=sandbox \
  bash "$R/scripts/work.sh" sandbox-ok
) >"$TMP/sandbox-work.out" 2>&1
status="$(sed -n 's/^status: *//p' "$R/state/tasks/sandbox-ok.md" | head -1)"
[ "$status" = passed ] || {
  echo "FAIL strict sandbox task status=$status"; tail -30 "$TMP/sandbox-work.out"
  tail -30 "$R"/loop/logs/*-arm-sandbox-ok-*.out 2>/dev/null || true
  exit 1
}
worker_uid="$(git -C "$R" show loop/work/sandbox-ok:app/uid.txt | tr -d '[:space:]')"
[ "$status" = passed ] && [ -n "$worker_uid" ] && [ "$worker_uid" != "$(id -u)" ]
echo "ok    strict sandbox completed bounded work as uid=$worker_uid (controller uid=$(id -u))"

# Canonical review publication positive control.
git -C "$R" checkout -q main
git -C "$R" checkout -q -b loop/work/publish-ok
echo review > "$R/app/review.txt"; git -C "$R" add app/review.txt
git -C "$R" -c user.name=t -c user.email=t@t commit -qm review
git -C "$R" checkout -q main
cat > "$R/state/tasks/publish-ok.md" <<'T'
id: publish-ok
goal_id: phase1-goal
status: passed
T
: > "$TMP/publisher-key"; chmod 600 "$TMP/publisher-key"
before="$(git --git-dir="$ORIGIN" rev-parse refs/heads/main)"
RECURSION_ROOT="$R" RECURSION_ALLOW_PUSH=1 bash "$R/scripts/publish.sh" \
  --branch loop/work/publish-ok --repo "$R" --key "$TMP/publisher-key" >/dev/null
after="$(git --git-dir="$ORIGIN" rev-parse refs/heads/main)"
review="$(git --git-dir="$ORIGIN" rev-parse refs/heads/loop/work/publish-ok)"
[ "$before" = "$after" ] && [ -n "$review" ]
echo "ok    canonical review ref published and registered default remained unchanged"

RECURSION_ROOT="$SRC" bash "$SRC/scripts/audit/hermes-pilot-phase1-artifacts.sh"
echo "hermes-pilot-phase1-green: ALL PASS"

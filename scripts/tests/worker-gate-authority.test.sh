#!/usr/bin/env bash
# Focused hermetic controls for canonical worker admission and deny-first gate scope.
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

# Project contention is a retryable defer, never a successful no-op.
R="$TMP/controller"; mkdir -p "$R/scripts" "$R/state/tasks" "$R/state/.locks/project-alpha.lock" "$R/loop/logs"
cp "$SRC/scripts/work.sh" "$R/scripts/"
cp "$SRC/scripts/runtime-state.py" "$R/scripts/"
: > "$R/.env"
cat > "$R/state/tasks/task-a.md" <<'TASK'
id: task-a
project_id: alpha
workstream: ignored-worker-label
goal: bounded fixture
engine: claude
acceptance: test -s result
status: queued
TASK
RECURSION_ROOT="$R" bash "$R/scripts/work.sh" task-a >/dev/null 2>&1; rc=$?
if [ "$rc" = 75 ] && grep -q '^status: queued' "$R/state/tasks/task-a.md"; then
  ok "canonical project lock contention defers without false success"
else
  no "project contention returned rc=$rc or mutated the task"
fi

# provider-only cannot degrade to the host network when the operator capability is absent.
N="$TMP/network-controller"; mkdir -p "$N/scripts" "$N/worktree"
cp "$SRC/scripts/worker-sandbox.sh" "$N/scripts/"
cp "$SRC/scripts/phase5_safety.py" "$N/scripts/"
network_rc=0
RECURSION_ROOT="$N" RECURSION_TEST_WORKER=logical \
  bash "$N/scripts/worker-sandbox.sh" --engine claude --role implementer \
  --worktree "$N/worktree" --network-policy provider-only --prompt fixture \
  >/dev/null 2>&1 || network_rc=$?
if [ "$network_rc" = 96 ] && grep -q 'NetworkNamespacePath=' "$SRC/scripts/worker-sandbox.sh"; then
  ok "provider-only refuses execution without a controller-owned network capability"
else
  no "provider-only silently retained host egress or lacks a namespace boundary"
fi

# The logical test bypass is permitted only for a disposable platform-temp controller.  The
# checked-out repository is a deliberately non-temp controller on this host and must be refused.
non_temp_rc=0
RECURSION_ROOT="$SRC" RECURSION_TEST_WORKER=logical \
  bash "$N/scripts/worker-sandbox.sh" --engine claude --role implementer \
  --worktree "$N/worktree" --network-policy provider-only --prompt fixture \
  >/dev/null 2>&1 || non_temp_rc=$?
if [ "$non_temp_rc" = 95 ]; then
  ok "logical test bypass refuses a non-temp controller root"
else
  no "logical test bypass accepted a non-temp controller root (rc=$non_temp_rc)"
fi

if grep -q 'commit_event(base, value)' "$SRC/scripts/project-reconcile.py" \
   && grep -q 'commit_event(base, value)' "$SRC/scripts/project-pilot.py" \
   && grep -q 'append_jsonl(journal_path, event' "$SRC/scripts/transition_receipt.py" \
   && grep -q 'while view:' "$SRC/scripts/jsonl_durable.py"; then
  ok "project event appenders complete every write under the shared journal lock"
else
  no "a project event appender can commit a short JSONL write"
fi

# Nested renderer truth/tools and the deployed actuator definition are protected base..HEAD.
P="$TMP/project"; git -c init.defaultBranch=main init -q "$P"
mkdir -p "$P/user-client/render/data/models" "$P/user-client/render/tools" "$P/deploy/systemd"
printf 'base\n' > "$P/user-client/render/data/models/oracle.json"
printf 'base\n' > "$P/user-client/render/tools/native-diff.cjs"
printf 'base\n' > "$P/deploy/systemd/hermes-actuator.service"
git -C "$P" add -A; git -C "$P" -c user.name=t -c user.email=t@t commit -qm base
base="$(git -C "$P" rev-parse HEAD)"
printf 'tamper\n' >> "$P/user-client/render/data/models/oracle.json"
printf 'tamper\n' >> "$P/user-client/render/tools/native-diff.cjs"
printf 'tamper\n' >> "$P/deploy/systemd/hermes-actuator.service"
evidence="$TMP/scope.json"
python3 "$SRC/scripts/git-scope.py" --repo "$P" --base "$base" --allowed-paths . --check \
  >"$evidence" 2>/dev/null; scope_rc=$?
if [ "$scope_rc" = 1 ] && python3 - "$evidence" <<'PY'
import json,sys
paths=set(json.load(open(sys.argv[1],encoding='utf-8')).get('protected_paths',[]))
expected={'user-client/render/data/models/oracle.json',
          'user-client/render/tools/native-diff.cjs',
          'deploy/systemd/hermes-actuator.service'}
raise SystemExit(0 if expected <= paths else 1)
PY
then
  ok "nested oracle/tools and deploy/systemd are deny-first protected"
else
  no "nested protected paths escaped the complete Git scope gate"
fi

# Gates that only prove a shell constant or host invariant cannot grade a candidate.
vacuous_ok=1
for gate in 'echo ok' '[ 1 -eq 1 ]' 'test -e /' \
  'true || test -s app/result.txt' '[ 1 = 1 ] || test -s app/result.txt' \
  'test -s app/result.txt || true' 'test -s app/result.txt || [ 1 = 1 ]'; do
  python3 "$SRC/scripts/validate-gate.py" --acceptance "$gate" --allowed-paths app \
    >/dev/null 2>&1 && vacuous_ok=0
done
python3 "$SRC/scripts/validate-gate.py" --acceptance 'test -s app/result.txt' \
  --allowed-paths app >/dev/null 2>&1 || vacuous_ok=0
if [ "$vacuous_ok" = 1 ]; then
  ok "constant-output, constant-comparison, and host-root gates are refused"
else
  no "a structurally vacuous gate was admitted or a real file gate was refused"
fi

# Both task and goal acceptance are routed through the non-root gate role.
if grep -q -- '--engine gate' "$SRC/scripts/work.sh" \
   && grep -q 'worker-sandbox.sh.*--engine.*gate' "$SRC/scripts/project-reconcile.py" \
   && grep -q -- '--uid "$RUNNER_USER"' "$SRC/scripts/worker-sandbox.sh" \
   && grep -q 'ReadOnlyPaths=-/workspace/.git' "$SRC/scripts/worker-sandbox.sh" \
   && ! grep -q 'Popen(\["bash", "-c", command\]' "$SRC/scripts/project-reconcile.py"; then
  ok "task and goal gates share the non-root boundary with read-only git authority"
else
  no "a machine gate still has a direct root bash execution path"
fi

# Where transient systemd services are available, prove build outputs stay writable while the
# linked-worktree authority pointer cannot be rewritten by the acceptance command.
if [ "$(id -u 2>/dev/null || echo 1)" = 0 ] && command -v systemd-run >/dev/null 2>&1 \
   && id recursion-runner >/dev/null 2>&1 && systemctl is-system-running >/dev/null 2>&1; then
  M="$TMP/sandbox-main"; S="$TMP/sandbox-project"; git -c init.defaultBranch=main init -q "$M"
  printf 'seed\n' > "$M/source.txt"; git -C "$M" add -A
  git -C "$M" -c user.name=t -c user.email=t@t commit -qm base
  git -C "$M" worktree add -q -b sandbox-gate "$S" main
  pointer_before="$(sha256sum "$S/.git" 2>/dev/null | awk '{print $1}')"
  RECURSION_ROOT="$SRC" bash "$SRC/scripts/worker-sandbox.sh" --engine gate --role gate \
    --worktree "$S" --network-policy none --gate-command 'printf built > build.out' \
    >/dev/null 2>&1; build_rc=$?
  RECURSION_ROOT="$SRC" bash "$SRC/scripts/worker-sandbox.sh" --engine gate --role gate \
    --worktree "$S" --network-policy none --gate-command 'printf forged > .git' \
    >/dev/null 2>&1; git_rc=$?
  pointer_after="$(sha256sum "$S/.git" 2>/dev/null | awk '{print $1}')"
  if [ "$build_rc" = 0 ] && [ -s "$S/build.out" ] && [ "$git_rc" != 0 ] \
     && [ "$pointer_before" = "$pointer_after" ]; then
    ok "gate may emit build output but cannot rewrite linked-worktree git authority"
  else
    no "gate write boundary did not separate build output from git authority"
  fi
else
  ok "gate git-write runtime control skipped (transient systemd unavailable)"
fi

echo
[ "$fails" -eq 0 ] && { echo "worker-gate-authority: ALL PASS"; exit 0; }
echo "worker-gate-authority: $fails FAILED"; exit 1

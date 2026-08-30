#!/usr/bin/env bash
# Hermetic controls for PAUSE-safe self-repo monitoring, cycle serialization, and date identity.
set -uo pipefail
export LC_ALL=C

# This suite drives the live loop arms (flock, procfs, POSIX lock semantics) — off-box it can only
# produce noise, so it reports an explicit SKIP. The box baseline runs it for real.
if [ "$(uname -s)" != "Linux" ]; then
  echo "cycle-control: SKIP (Linux loop runtime required — flock/procfs/POSIX lock semantics; certified in the box suite)"
  exit 0
fi

SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"
DRAIN_PID=""
FIRST_PID=""
cleanup(){
  [ -z "$FIRST_PID" ] || kill "$FIRST_PID" 2>/dev/null || true
  [ -z "$DRAIN_PID" ] || kill "$DRAIN_PID" 2>/dev/null || true
  rm -rf "$TMP"
}
trap cleanup EXIT
GIT="git -c user.name=t -c user.email=t@t"

# --- run.sh: PAUSE preserves the exact self-repo Git projection ----------------------------
R="$TMP/run-repo"
mkdir -p "$R/bin" "$R/loop/supervisor" "$R/loop/logs" "$R/state/briefs" "$R/state/projects"
cp "$SRC/loop/supervisor/run.sh" "$R/loop/supervisor/run.sh"
cat > "$R/bin/hermes" <<'STUB'
#!/usr/bin/env bash
usage=""; prompt=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    -z) prompt="$2"; shift 2 ;;
    --usage-file) usage="$2"; shift 2 ;;
    *) shift ;;
  esac
done
[ -n "$usage" ] && printf '%s\n' '{"provider":"openai-codex","estimated_cost_usd":0,"total_tokens":1}' > "$usage"
if printf '%s' "$prompt" | grep -q HEARTBEAT; then
  printf '%s\n' '===HEARTBEAT: quiet==='
else
  printf '%s\n' '# monitored brief' 'nothing to report'
fi
STUB
chmod +x "$R/bin/hermes" "$R/loop/supervisor/run.sh"
printf '%s\n' HEARTBEAT > "$R/loop/supervisor/heartbeat.md"
printf '%s\n' MORNING > "$R/loop/supervisor/morning-brief.md"
printf '%s\n' '# anchor' > "$R/ANCHOR.md"
printf '%s\n' '# board committed' > "$R/state/BOARD.md"
printf '%s\n' '# inbox' > "$R/state/INBOX.md"
printf '%s\n' '#!/usr/bin/env bash' 'echo one' > "$R/probe.sh"
cat > "$R/.gitignore" <<'EOF'
state/PAUSE
state/.recursion-snapshot.txt
loop/logs/
EOF
( cd "$R" && git init -q -b master && git config user.name t && git config user.email t@t \
  && git add -A && git commit -qm initial )

# No loop/auto exists. A paused morning still generates a local brief, but may not discard the
# operator's BOARD edit, create/switch a branch, commit it, or touch HEAD/reflog.
printf '%s\n' '# operator board must survive' > "$R/state/BOARD.md"
printf '%s\n' 'PAUSED fixture' 'reason: cycle-control' > "$R/state/PAUSE"
branch_before="$(git -C "$R" branch --show-current)"
head_before="$(git -C "$R" rev-parse HEAD)"
board_before="$(sha256sum "$R/state/BOARD.md" | awk '{print $1}')"
reflog_before="$(git -C "$R" reflog --format=%H | wc -l)"
( cd "$R" && PATH="$R/bin:$PATH" RECURSION_ROOT="$R" RECURSION_CYCLE_DATE=2099-01-02 DELIVER_BRIEF=0 \
    bash loop/supervisor/run.sh morning ) >"$TMP/paused-morning.out" 2>&1
rc=$?
branch_after="$(git -C "$R" branch --show-current)"
head_after="$(git -C "$R" rev-parse HEAD)"
board_after="$(sha256sum "$R/state/BOARD.md" | awk '{print $1}')"
reflog_after="$(git -C "$R" reflog --format=%H | wc -l)"
if [ "$rc" -eq 0 ] && [ "$branch_before" = "$branch_after" ] && [ "$head_before" = "$head_after" ] \
    && [ "$board_before" = "$board_after" ] && [ "$reflog_before" = "$reflog_after" ] \
    && ! git -C "$R" show-ref --verify --quiet refs/heads/loop/auto \
    && grep -q 'PAUSED' "$R/state/briefs/2099-01-02.md"; then
  ok "paused morning monitors without changing branch, HEAD, BOARD, reflog, or creating loop/auto"
else
  no "paused morning mutated self-repo Git state or failed monitoring (rc=$rc branch=$branch_before/$branch_after head=$head_before/$head_after board=$board_before/$board_after reflog=$reflog_before/$reflog_after loop=$([ -n "$(git -C "$R" show-ref refs/heads/loop/auto)" ] && echo present || echo absent) brief=$([ -f "$R/state/briefs/2099-01-02.md" ] && echo present || echo absent))"
  sed 's/^/      /' "$TMP/paused-morning.out" >&2
fi

# With a real divergent ledger branch and a newer reviewed default, heartbeat mode must likewise
# leave the executable tree and reflog exact while paused.
git -C "$R" checkout -q -- state/BOARD.md
git -C "$R" checkout -qb loop/auto
printf '%s\n' ledger > "$R/state/ledger.txt"
( cd "$R" && $GIT add state/ledger.txt && $GIT commit -qm ledger )
git -C "$R" checkout -q master
printf '%s\n' '#!/usr/bin/env bash' 'echo two' > "$R/probe.sh"
( cd "$R" && $GIT add probe.sh && $GIT commit -qm reviewed-v2 )
git -C "$R" checkout -q loop/auto
printf '%s\n' '# second operator board' > "$R/state/BOARD.md"
head_before="$(git -C "$R" rev-parse HEAD)"
board_before="$(sha256sum "$R/state/BOARD.md" | awk '{print $1}')"
reflog_before="$(git -C "$R" reflog --format=%H | wc -l)"
( cd "$R" && PATH="$R/bin:$PATH" RECURSION_ROOT="$R" RECURSION_CYCLE_DATE=2099-01-03 \
    bash loop/supervisor/run.sh heartbeat ) >"$TMP/paused-heartbeat.out" 2>&1
rc=$?
if [ "$rc" -eq 0 ] && [ "$(git -C "$R" rev-parse HEAD)" = "$head_before" ] \
    && [ "$(sha256sum "$R/state/BOARD.md" | awk '{print $1}')" = "$board_before" ] \
    && [ "$(git -C "$R" reflog --format=%H | wc -l)" = "$reflog_before" ] \
    && [ "$(bash "$R/probe.sh")" = one ] \
    && grep -q 'done heartbeat' "$TMP/paused-heartbeat.out"; then
  ok "paused heartbeat does not merge a newer default into the runtime branch"
else
  no "paused heartbeat changed the runtime branch/tree or stopped monitoring"
fi

# Resume keeps the proven path: clean BOARD, reach loop/auto, and merge the reviewed default.
rm -f "$R/state/PAUSE"
( cd "$R" && PATH="$R/bin:$PATH" RECURSION_ROOT="$R" RECURSION_CYCLE_DATE=2099-01-04 \
    bash loop/supervisor/run.sh heartbeat ) >"$TMP/resumed-heartbeat.out" 2>&1
rc=$?
if [ "$rc" -eq 0 ] && [ "$(git -C "$R" branch --show-current)" = loop/auto ] \
    && git -C "$R" merge-base --is-ancestor master loop/auto \
    && [ "$(bash "$R/probe.sh")" = two ]; then
  ok "resumed heartbeat retains the reviewed default-to-loop/auto merge path"
else
  no "resumed heartbeat failed to update the runtime branch"
fi

# Defense in depth: if anything changes branches after the initial checkout, state output must
# remain uncommitted on that non-loop branch. The engine stub simulates the branch race here.
( cd "$R" && $GIT add -A && $GIT commit -qm clean-ledger )
cat > "$R/bin/hermes" <<'STUB'
#!/usr/bin/env bash
usage=""; prompt=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    -z) prompt="$2"; shift 2 ;;
    --usage-file) usage="$2"; shift 2 ;;
    *) shift ;;
  esac
done
[ -n "$usage" ] && printf '%s\n' '{"provider":"openai-codex","estimated_cost_usd":0,"total_tokens":1}' > "$usage"
git checkout -q master
mkdir -p state/briefs
printf '%s\n' '# monitored after branch race'
STUB
chmod +x "$R/bin/hermes"
master_before="$(git -C "$R" rev-parse master)"
( cd "$R" && PATH="$R/bin:$PATH" RECURSION_ROOT="$R" RECURSION_CYCLE_DATE=2099-01-05 DELIVER_BRIEF=0 \
    bash loop/supervisor/run.sh morning ) >"$TMP/non-loop-commit.out" 2>&1
rc=$?
if [ "$rc" -eq 0 ] && [ "$(git -C "$R" branch --show-current)" = master ] \
    && [ "$(git -C "$R" rev-parse master)" = "$master_before" ] \
    && grep -q 'REFUSED state commit on branch' "$TMP/non-loop-commit.out"; then
  ok "supervisor refuses to commit monitoring state after a non-loop branch race"
else
  no "supervisor committed or failed after a non-loop branch race (rc=$rc branch=$(git -C "$R" branch --show-current) master=$master_before/$(git -C "$R" rev-parse master))"
  sed 's/^/      /' "$TMP/non-loop-commit.out" >&2
fi

if [ "${CYCLE_CONTROL_RUN_ONLY:-}" = "run" ]; then
  echo
  [ "$fails" -eq 0 ] && { echo "cycle-control (run only): ALL PASS"; exit 0; }
  echo "cycle-control (run only): $fails FAILED"; exit 1
fi

# --- cycle.sh: one date, one owner, and no lock inherited by background continuations --------
C="$TMP/cycle-root"
mkdir -p "$C/scripts" "$C/loop/supervisor" "$C/loop/logs" "$C/state/tasks" "$C/state/.locks"
for s in assignment.py assignment_contract.py phase5_safety.py assist.sh author.sh board.sh capacity.sh conduct.sh cycle.sh digest.sh engine_contract.py \
  git-scope.py instruction_routing.py intake.sh jsonl_durable.py notify.sh pilot_instruction.py plan.sh \
  board-summary.sh \
  project-pilot.py project-reconcile.py project_authority.py provider-connect-proxy.py provider_contract.py provider-network.sh provider-egress.py \
  publish.sh remote_evidence.py resolve-engine.py resolve-model-alias.py resync.sh reflect.sh resume.sh \
  remote-pause.py remote_backend.py remote_assignment.py \
  drain.sh run_contract.py runtime-state.py seed_contract.py taskctl.sh transition_receipt.py \
  validate-assignment-result.py validate-control-state.py validate-decision.py validate-gate.py \
  validate-verifier-result.py validate-worker-result.py work.sh assignment-token.py worker-evidence.py worker-sandbox.sh; do
  cp "$SRC/scripts/$s" "$C/scripts/"
done
cat > "$C/scripts/board.sh" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
cat > "$C/scripts/taskctl.sh" <<'STUB'
#!/usr/bin/env bash
case "${1:-}" in
  reap) echo 'reap: nothing stale' ;;
  esc-record) printf '%s\n' "$*" >> "${STUB_ESC_LOG:?}"; echo 'NEW esc-test' ;;
esac
STUB
cat > "$C/scripts/resync.sh" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
cat > "$C/scripts/intake.sh" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
cat > "$C/loop/supervisor/run.sh" <<'STUB'
#!/usr/bin/env bash
job="${1:-heartbeat}"; date="${RECURSION_CYCLE_DATE:?}"
printf '%s\t%s\n' "$date" "$job" >> "${STUB_DATE_LOG:?}"
if [ "$job" = heartbeat ]; then
  printf '%s\n' '===HEARTBEAT: quiet===' > "$RECURSION_ROOT/loop/logs/$date-heartbeat.out"
  printf '%s\n' '{"provider":"openai-codex","estimated_cost_usd":0,"total_tokens":1}' > "$RECURSION_ROOT/loop/logs/$date-heartbeat.usage.json"
  if [ -n "${STUB_HEARTBEAT_STARTED:-}" ]; then
    : > "$STUB_HEARTBEAT_STARTED"
    while [ ! -f "${STUB_HEARTBEAT_RELEASE:?}" ]; do sleep 0.05; done
  fi
fi
STUB
cat > "$C/scripts/drain.sh" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$$" > "${STUB_DRAIN_PID:?}"
: > "${STUB_DRAIN_STARTED:?}"
while [ ! -f "${STUB_DRAIN_RELEASE:?}" ]; do sleep 0.05; done
STUB
chmod +x "$C/scripts/"*.sh "$C/loop/supervisor/run.sh"
: > "$TMP/date.log"; : > "$TMP/escalation.log"

# Hold one real cycle inside its heartbeat, then prove a second cron tick refuses immediately and
# records both a dated log and a canonical local escalation.
STUB_DATE_LOG="$TMP/date.log" STUB_ESC_LOG="$TMP/escalation.log" \
STUB_HEARTBEAT_STARTED="$TMP/heartbeat.started" STUB_HEARTBEAT_RELEASE="$TMP/heartbeat.release" \
RECURSION_ROOT="$C" RECURSION_CYCLE_DATE=2099-12-31 \
  bash "$C/scripts/cycle.sh" >"$TMP/cycle-first.out" 2>&1 &
first_pid=$!
FIRST_PID="$first_pid"
for _ in $(seq 1 200); do [ -f "$TMP/heartbeat.started" ] && break; sleep 0.05; done
if [ ! -f "$TMP/heartbeat.started" ]; then
  no "first cycle did not reach its held heartbeat"
fi
set +e
STUB_DATE_LOG="$TMP/date.log" STUB_ESC_LOG="$TMP/escalation.log" \
RECURSION_ROOT="$C" RECURSION_CYCLE_DATE=2099-12-31 \
  bash "$C/scripts/cycle.sh" >"$TMP/cycle-overlap.out" 2>&1
overlap_rc=$?
: > "$TMP/heartbeat.release"
wait "$first_pid"; first_rc=$?
FIRST_PID=""
if [ "$first_rc" -eq 0 ] && [ "$overlap_rc" -eq 73 ] \
    && grep -q 'cycle overlap refused' "$TMP/cycle-overlap.out" \
    && grep -q 'cycle-overlap' "$TMP/escalation.log" \
    && grep -q '^2099-12-31[[:space:]]heartbeat$' "$TMP/date.log" \
    && [ -f "$C/loop/logs/2099-12-31-cycle.log" ]; then
  ok "overlapping cycle is refused durably and one exported date reaches the heartbeat"
else
  no "cycle overlap/date control failed (first=$first_rc overlap=$overlap_rc)"
fi

# A detached drainer may outlive cycle.sh, but it must not keep fd 9's flock alive. The next cycle
# must acquire immediately while that child is still running.
printf '%s\n' 'status: queued' > "$C/state/tasks/fd-test.md"
: > "$TMP/date-fd.log"
STUB_DATE_LOG="$TMP/date-fd.log" STUB_ESC_LOG="$TMP/escalation.log" \
STUB_DRAIN_PID="$TMP/drain.pid" STUB_DRAIN_STARTED="$TMP/drain.started" \
STUB_DRAIN_RELEASE="$TMP/drain.release" RECURSION_AUTO_DRAIN=1 RECURSION_CONDUCT=0 \
RECURSION_ROOT="$C" RECURSION_CYCLE_DATE=2099-12-30 \
  bash "$C/scripts/cycle.sh" >"$TMP/cycle-fd-first.out" 2>&1
fd_first_rc=$?
for _ in $(seq 1 200); do [ -f "$TMP/drain.started" ] && break; sleep 0.05; done
[ -f "$TMP/drain.pid" ] && DRAIN_PID="$(cat "$TMP/drain.pid")"
set +e
STUB_DATE_LOG="$TMP/date-fd.log" STUB_ESC_LOG="$TMP/escalation.log" \
RECURSION_AUTO_DRAIN=0 RECURSION_ROOT="$C" RECURSION_CYCLE_DATE=2099-12-29 \
  bash "$C/scripts/cycle.sh" >"$TMP/cycle-fd-second.out" 2>&1
fd_second_rc=$?
drain_alive=0
[ -n "$DRAIN_PID" ] && kill -0 "$DRAIN_PID" 2>/dev/null && drain_alive=1
: > "$TMP/drain.release"
if [ "$fd_first_rc" -eq 0 ] && [ "$fd_second_rc" -eq 0 ] \
    && [ "$drain_alive" -eq 1 ] \
    && grep -q '^2099-12-30[[:space:]]heartbeat$' "$TMP/date-fd.log" \
    && grep -q '^2099-12-29[[:space:]]heartbeat$' "$TMP/date-fd.log"; then
  ok "background drainer outlives its cycle without inheriting the singleton lock fd"
else
  no "background child retained the cycle lock or date identity was inconsistent"
fi
for _ in $(seq 1 100); do kill -0 "$DRAIN_PID" 2>/dev/null || break; sleep 0.05; done
DRAIN_PID=""

echo
[ "$fails" -eq 0 ] && { echo "cycle-control: ALL PASS"; exit 0; }
echo "cycle-control: $fails FAILED"; exit 1

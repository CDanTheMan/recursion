#!/usr/bin/env bash
# capacity.test.sh — the governor must refuse when the box is full, ADMIT when it is not, and
# never mistake "I could not measure" for "there is room".
#
# WHY. conduct.sh bounded parallelism with a fixed count, which assumes every task costs the same
# and cannot see anything else running on the box. On 2 cores with 3.8G, two heavy gates do not
# fail loudly — they thrash, every gate gets slower, and the timeouts that fire read as flaky
# tests rather than as a starved machine. That is a diagnosis you can chase for days.
#
# ★ Test 1 is the CONTROL. A governor that defers everything satisfies every "it defers"
#   assertion below and stops all work forever, so healthy metrics MUST admit.
# ★ Test 6 is the trap-shaped one: an unreadable metric must be "cannot tell" (exit 3), never
#   an admit. A governor that fails open is decorative exactly when the box is in the state it
#   exists to catch.
#
# The decision function is driven DIRECTLY (`capacity.sh decide`), so this exercises the code
# that runs rather than a restatement of its thresholds — and one assertion pins the real
# collector to the real box, so the pure function cannot drift away from reality.
#
#   run: bash scripts/tests/capacity.test.sh
set -uo pipefail
export LC_ALL=C

# This suite drives the live loop arms (flock, procfs, POSIX lock semantics) — off-box it can only
# produce noise, so it reports an explicit SKIP. The box baseline runs it for real.
if [ "$(uname -s)" != "Linux" ]; then
  echo "capacity: SKIP (Linux loop runtime required — flock/procfs/POSIX lock semantics; certified in the box suite)"
  exit 0
fi

SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
R="$TMP/root"; mkdir -p "$R/scripts" "$R/state/tasks" "$R/state/.locks" "$R/loop/logs"
for s in assignment.py assignment_contract.py phase5_safety.py assist.sh author.sh board.sh capacity.sh conduct.sh engine_contract.py git-scope.py \
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
HEAVY_TEST_OWNER_PID="$$"
# capacity.sh scales its load caps by the HOST's core count (nproc). The fixture metrics
# below were chosen against the 2-core box; on a many-core machine a load of 9.00 would
# legitimately ADMIT and the deferral assertions would go vacuous. Pin the fixture to 2.
mkdir -p "$TMP/bin"
printf '#!/usr/bin/env bash\necho 2\n' > "$TMP/bin/nproc"
chmod +x "$TMP/bin/nproc"
cap(){ ( cd "$R" && PATH="$TMP/bin:$PATH" RECURSION_ROOT="$R" RECURSION_HEAVY_PID="$HEAVY_TEST_OWNER_PID" \
  bash scripts/capacity.sh "$@" ) >"$TMP/out" 2>&1; echo $?; }

# mem_mb load1 disk_mb swap_mb — a comfortable box and several kinds of full one.
HEALTHY="2900 0.30 25000 0"

# --- 1) ★ CONTROL: a healthy box admits BOTH classes -------------------------------------------
a=$(cap decide arm  $HEALTHY);  ao="$(cat "$TMP/out")"
g=$(cap decide gate $HEALTHY);  go="$(cat "$TMP/out")"
if [ "$a" = "0" ] && [ "$g" = "0" ]; then
  ok "★ CONTROL — a healthy box admits both an arm and a gate (the governor is not refusing everything)"
else
  no "★ CONTROL FAILED — healthy metrics were refused (arm=$a '$ao' gate=$g '$go'); every deferral below is meaningless"
fi

# --- 2) memory: the gate is refused before the arm is ------------------------------------------
# This asymmetry IS the design: an arm is an LLM call and costs nothing locally, a gate is
# node --test over a corpus. Treating them alike is what a fixed concurrency count does.
g=$(cap decide gate 600 0.30 25000 0)
a=$(cap decide arm  600 0.30 25000 0)
if [ "$g" = "4" ] && [ "$a" = "0" ]; then
  ok "at 600MB free a GATE defers while an ARM still runs (they do not cost the same)"
else
  no "class asymmetry lost: gate=$g arm=$a at 600MB"
fi
a=$(cap decide arm 200 0.30 25000 0)
[ "$a" = "4" ] && ok "at 200MB even an arm defers" || no "an arm was admitted at 200MB free (rc=$a)"

# --- 3) load, disk and swap each defer on their own ---------------------------------------------
rc=$(cap decide gate 2900 9.00 25000 0)
[ "$rc" = "4" ] && ok "high load defers (load is scaled by core count)" || no "load ignored (rc=$rc)"
rc=$(cap decide gate 2900 0.30 500 0)
[ "$rc" = "4" ] && ok "a nearly-full disk defers" || no "disk ignored (rc=$rc)"
rc=$(cap decide gate 2900 0.30 25000 900)
[ "$rc" = "4" ] && ok "swap already in use defers — the box is thrashing before the gate starts" \
                || no "swap ignored (rc=$rc)"

# --- 4) thresholds are configurable, not baked in ------------------------------------------------
rc=$( ( cd "$R" && RECURSION_ROOT="$R" RECURSION_CAP_GATE_MEM_MB=100 \
        bash scripts/capacity.sh decide gate 600 0.30 25000 0 ) >/dev/null 2>&1; echo $? )
[ "$rc" = "0" ] && ok "a bigger box needs an env var, not a code change" || no "threshold override ignored (rc=$rc)"

# --- 5) an unknown class is an error, not an admit ------------------------------------------------
rc=$(cap decide teleport $HEALTHY)
[ "$rc" != "0" ] && ok "an unknown work class is refused rather than waved through" || no "unknown class admitted"

# --- 6) ★ THE TRAP: an unreadable metric is "cannot tell", never "fine" ----------------------------
# Simulated by pointing the collector at a root whose df cannot resolve. The distinction matters
# most when the box is sick, which is exactly when /proc reads are likeliest to misbehave.
rc=$( ( cd "$R" && RECURSION_ROOT="$R/definitely/not/here" bash scripts/capacity.sh check gate ) >"$TMP/out" 2>&1; echo $? )
if [ "$rc" = "3" ] && grep -q 'CANNOT TELL' "$TMP/out"; then
  ok "★ an unreadable metric is CANNOT TELL (exit 3), never an admit"
else
  no "★ FAILS OPEN — unmeasurable box returned rc=$rc: $(cat "$TMP/out")"
fi

# --- 7) the heavy-gate lock is exclusive, and it OPENS again ---------------------------------------
rc=$(cap heavy acquire first)
[ "$rc" = "0" ] && ok "the heavy-gate lock can be taken" || no "could not acquire the heavy lock: $(cat "$TMP/out")"
rc=$(cap heavy acquire second)
[ "$rc" = "4" ] && grep -q '^BUSY' "$TMP/out" && ok "a second heavy gate is refused while the first holds" \
  || no "two heavy gates ran at once (rc=$rc)"
cap heavy release >/dev/null
rc=$(cap heavy acquire third)
if [ "$rc" = "0" ]; then
  ok "★ CONTROL — the lock OPENS after release (it is a mutex, not a one-way door)"
else
  no "★ CONTROL FAILED — the lock never reopened; one gate would wedge every future gate"
fi
cap heavy release >/dev/null

# --- 8) ★ a dead holder is reclaimed, not honoured forever -------------------------------------
# A crashed gate leaves the lock directory behind. Without reclaiming, one crash disables heavy
# gates permanently and the symptom is "gates stopped running", with nothing pointing at why.
mkdir -p "$R/state/.locks/heavy-gate.lock"
echo 999999 > "$R/state/.locks/heavy-gate.lock/pid"        # a pid that cannot be alive
echo 'ghost (pid 999999)' > "$R/state/.locks/heavy-gate.lock/holder"
# Aged past the grace window. The grace exists because the recorded pid may belong to a
# short-lived CLI process that exited the instant it acquired — judging liveness alone made
# every holder look dead immediately, and the mutex excluded nobody while appearing to work.
touch -d '30 minutes ago' "$R/state/.locks/heavy-gate.lock"
rc=$(cap heavy acquire after-crash)
if [ "$rc" = "0" ]; then
  ok "★ a lock held by a DEAD process is reclaimed (a crashed gate does not wedge the box)"
else
  no "★ DEADLOCK — a dead holder still owns the heavy lock (rc=$rc): $(cat "$TMP/out")"
fi
cap heavy release >/dev/null

# --- 9) the real collector agrees with the real box ------------------------------------------------
# Ties the pure function to reality: without this the thresholds could drift into fantasy and
# every test above would still pass, because they all supply their own numbers.
rc=$(cap check arm)
if [ "$rc" = "0" ] || [ "$rc" = "4" ]; then
  ok "the live collector produces a real verdict on this box ($(head -1 "$TMP/out"))"
else
  no "the live collector could not measure this box (rc=$rc): $(cat "$TMP/out")"
fi

# --- 10) ★ the conductor HOLDS instead of reporting an empty queue ---------------------------------
# The dangerous failure is not refusing to launch — it is refusing to launch and then logging
# "queue empty", which reads as success on work that never ran.
cat > "$R/state/tasks/cap-001.md" <<'T'
id: cap-001
workstream: captest
goal: should not launch while the box is full
engine: none
acceptance: true
status: queued
T
cat > "$R/scripts/capacity.sh" <<'DENY'
#!/usr/bin/env bash
[ "${1:-}" = "check" ] && { echo "DEFER arm: synthetic full box"; exit 4; }
exit 0
DENY
chmod +x "$R/scripts/capacity.sh"
( cd "$R" && RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 RECURSION_CONDUCT_POLL_S=1 \
    RECURSION_CONDUCT_CAP_WAIT_S=2 bash scripts/conduct.sh ) >"$TMP/c.out" 2>&1
st="$(sed -n 's/^status: *//p' "$R/state/tasks/cap-001.md" | head -1)"
if [ "$st" = "queued" ] && grep -q 'holding:' "$TMP/c.out" && ! grep -q 'queue empty' "$TMP/c.out"; then
  ok "★ a full box makes the conductor HOLD and say so — never 'queue empty' on unrun work"
else
  no "★ the conductor mis-reported a full box (task=$st): $(tail -3 "$TMP/c.out")"
fi

# ★ ...and the hold is BOUNDED. This hung for real while being written: waiting forever holds the
# single-instance state/.conduct.lock forever, and a held lock makes every LATER conduct run exit
# immediately — one full box wedging all future conducting, with silence as the only symptom.
if grep -q 'gave up after' "$TMP/c.out" && [ ! -d "$R/state/.conduct.lock" ]; then
  ok "★ the hold is BOUNDED and the lock is released (a full box cannot wedge conducting forever)"
else
  no "★ UNBOUNDED WAIT — the conductor never gave up; .conduct.lock would be held indefinitely"
fi

# ★ CONTROL: with capacity admitting, the same conductor DOES launch — or test 10 passes on a
# conductor that never launches anything.
cp "$SRC/scripts/capacity.sh" "$R/scripts/capacity.sh"; chmod +x "$R/scripts/capacity.sh"
# The disk floor is lowered for this run because the FIXTURE lives under /tmp, a ~1.9G
# tmpfs on this box, so the REAL collector defers on disk for a reason that has nothing to
# do with the conductor. Lowering a documented threshold keeps this a test of the real
# governor; stubbing the governor out would make it a test of the stub.
( cd "$R" && RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 RECURSION_CONDUCT_POLL_S=1 \
    RECURSION_CAP_ARM_DISK_MB=64 RECURSION_CONDUCT_CAP_WAIT_S=5 \
    bash scripts/conduct.sh ) >"$TMP/c2.out" 2>&1
grep -q 'launch cap-001' "$TMP/c2.out" \
  && ok "★ CONTROL — with capacity available the conductor DOES launch (test 10 is not vacuous)" \
  || no "★ CONTROL FAILED — the conductor never launches: $(tail -5 "$TMP/c2.out")"

# --- 11) ★ a HEAVY task still releases its workstream lock ----------------------------------
# The heavy-gate release was added as `trap 'release_heavy' EXIT`, which REPLACED work.sh's
# existing EXIT trap instead of adding to it — so every run leaked its per-workstream lock and
# the NEXT run of that workstream exited at "already building" with the task left queued. The
# first run always looked fine, which is exactly why it needed a second run to surface. Four
# suites went red from that one line.
mkheavy(){ cat > "$R/state/tasks/$1.md" <<T
id: $1
workstream: heavytest
goal: a heavy-gated task
engine: none
acceptance: true
gate_class: heavy
repo: $R
workdir: .
status: queued
T
}
runw(){ ( cd "$R" && RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 RECURSION_REQUIRE_FRESH_BASE=0 \
    bash scripts/work.sh "$1" ) >"$TMP/hw.out" 2>&1; }
( cd "$R" && git -c init.defaultBranch=main init -q . && git add -A >/dev/null 2>&1 \
    && git -c user.name=t -c user.email=t@t commit -qm init >/dev/null 2>&1 ) >/dev/null 2>&1
mkheavy heavy-a; mkheavy heavy-b
runw heavy-a
runw heavy-b
sa="$(sed -n 's/^status: *//p' "$R/state/tasks/heavy-a.md" | head -1)"
sb="$(sed -n 's/^status: *//p' "$R/state/tasks/heavy-b.md" | head -1)"
if [ "$sa" != "queued" ] && [ "$sb" != "queued" ]; then
  ok "★ two sequential HEAVY tasks in one workstream both ran (a=$sa b=$sb) — no lock leaked"
else
  no "★ LOCK LEAKED — the second heavy task never ran (a=$sa b=$sb); an EXIT trap was clobbered"
fi
[ ! -d "$R/state/.locks/ws-heavytest.lock" ] \
  && ok "the workstream lock is released after a heavy-gated run" \
  || no "ws-heavytest.lock survived the run"
[ ! -d "$R/state/.locks/heavy-gate.lock" ] \
  && ok "the heavy-gate lock is released after the gate" \
  || no "heavy-gate.lock survived the run"

echo
[ "$fails" -eq 0 ] && { echo "capacity: ALL PASS"; exit 0; }
echo "capacity: $fails FAILED"; exit 1

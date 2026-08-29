#!/usr/bin/env bash
# worker-envelope.test.sh — the arm must stay inside its boundary, and the boundary must be
# enforced by code rather than by the prompt asking nicely.
#
# WHY. The envelope tells the arm its allowed paths, its non-goals, and to stop on ambiguity.
# A prompt is a request. These tests drive a STUB arm that deliberately misbehaves — writes a
# control-plane file, edits a test, wanders outside allowed_paths — and assert work.sh refuses
# the result. The acceptance gate structurally cannot catch any of it: the gate scores the
# OUTCOME, so a diff that quietly edits a fixture to reach that outcome still exits 0.
#
# ★ ORDER IS A PROPERTY UNDER TEST. The scope check must run BEFORE the acceptance gate. If it
# ran after, a tampered pass would already have been declared. Test 5 pins that by making the
# acceptance command leave a marker and asserting the marker is absent.
#
# ★ The CONTROL (test 1) proves the gate is not simply refusing everything.
#
#   run: bash scripts/tests/worker-envelope.test.sh
set -uo pipefail
export LC_ALL=C

# This suite drives the live loop arms (flock, procfs, POSIX lock semantics) — off-box it can only
# produce noise, so it reports an explicit SKIP. The box baseline runs it for real.
if [ "$(uname -s)" != "Linux" ]; then
  echo "worker-envelope: SKIP (Linux loop runtime required — flock/procfs/POSIX lock semantics; certified in the box suite)"
  exit 0
fi

SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/bin"; mkdir -p "$BIN"

# stub arm: runs $STUB_ARM_SCRIPT inside the worktree (cwd), i.e. it writes whatever the case
# under test needs. Stands in for `claude -p` with no model call and no spend.
cat > "$BIN/claude" <<'STUB'
#!/usr/bin/env bash
[ -n "${STUB_ARM_SCRIPT:-}" ] && bash -c "$STUB_ARM_SCRIPT"
exit 0
STUB
chmod +x "$BIN/claude"

# disposable repo with a realistic shape (a protected tree and a product tree)
R="$TMP/repo"; mkdir -p "$R/scripts/tests" "$R/apps/chiron" "$R/other" "$R/state/tasks" "$R/loop/logs"
cp "$SRC/scripts/work.sh" "$R/scripts/"
cp "$SRC/scripts/worker-sandbox.sh" "$R/scripts/"
cp "$SRC/scripts/phase5_safety.py" "$R/scripts/"
chmod +x "$R/scripts/worker-sandbox.sh"
cp "$SRC/scripts/board.sh" "$R/scripts/" 2>/dev/null || true
cp "$SRC/scripts/notify.sh" "$R/scripts/" 2>/dev/null || true
cp "$SRC/scripts/taskctl.sh" "$R/scripts/" 2>/dev/null || true
cp "$SRC/scripts/jsonl_durable.py" "$R/scripts/" 2>/dev/null || true
cp "$SRC/scripts/transition_receipt.py" "$R/scripts/" 2>/dev/null || true
cp "$SRC/scripts/runtime-state.py" "$R/scripts/" 2>/dev/null || true
cp "$SRC/scripts/resync.sh" "$R/scripts/" 2>/dev/null || true
# resync's freshness gate shells the typed source-pin controller; without it (and its full
# import closure) every task blocks at CANNOT PROVE FRESH before the envelope is ever
# exercised. Hard cp: a silent skip here would reproduce exactly the failure this stages
# against.
cp "$SRC/scripts/project-pilot.py" "$R/scripts/"
cp "$SRC/scripts/engine_contract.py" "$R/scripts/"
cp "$SRC/scripts/pilot_instruction.py" "$R/scripts/"
cp "$SRC/scripts/seed_contract.py" "$R/scripts/"
cp "$SRC/scripts/project_authority.py" "$R/scripts/"
printf 'seed\n' > "$R/apps/chiron/seed.txt"
printf 'protected fixture\n' > "$R/scripts/tests/existing.test.cjs"
: > "$R/.env"
# The repo gets a real (local, bare) origin and a registry row, because work.sh will not build
# on a base whose freshness it cannot prove — see scripts/resync.sh. Giving the fixture a real
# upstream keeps these tests on the REAL dispatch path; setting RECURSION_REQUIRE_FRESH_BASE=0
# would have been one line shorter and would have quietly stopped testing what actually runs.
ORIGIN="$TMP/origin.git"
git -c init.defaultBranch=main init -q --bare "$ORIGIN"
( cd "$R" \
  && git -c init.defaultBranch=main init -q . \
  && git add -A >/dev/null 2>&1 \
  && git -c user.name=t -c user.email=t@t commit -qm init >/dev/null 2>&1 \
  && git branch -M main >/dev/null 2>&1 \
  && git remote add origin "$ORIGIN" \
  && git push -q origin main >/dev/null 2>&1 \
  && git fetch -q origin >/dev/null 2>&1 ) || true
printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > "$R/state/portfolio.tsv"
printf 'wtest\t%s\t%s\tmain\t-\t-\t-\tactive\n' "$R" "$ORIGIN" >> "$R/state/portfolio.tsv"

MARKER="$TMP/acceptance-ran"

mktask(){ # id allowed_paths acceptance
  cat > "$R/state/tasks/$1.md" <<T
id: $1
workstream: wtest
goal: a bounded change
engine: claude
network_policy: none
repo: $R
acceptance: $3
workdir: .
allowed_paths: $2
autonomy: auto
status: queued

body
T
}

run_case(){ # id script
  rm -f "$MARKER"
  ( cd "$R" && PATH="$BIN:$PATH" RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 \
      RECURSION_GIT_FETCH=0 RECURSION_TEST_WORKER=logical STUB_ARM_SCRIPT="$2" \
      bash scripts/work.sh "$1" ) >"$TMP/out-$1" 2>&1
}
status_of(){ sed -n 's/^status: *//p' "$R/state/tasks/$1.md" | head -1 | tr -d '\r'; }
inbox_tail(){ tail -25 "$R/state/INBOX.md" 2>/dev/null; }

# --- 1) ★ CONTROL: an in-scope change with a green gate must PASS ---------------------------
mktask t-ok "apps/chiron" "test -s apps/chiron/new.txt"
run_case t-ok 'mkdir -p apps/chiron && echo hello > apps/chiron/new.txt'
if [ "$(status_of t-ok)" = "passed" ]; then
  ok "★ CONTROL — an in-scope change with a green gate PASSES (the gate is not refusing everything)"
else
  no "★ CONTROL FAILED — an in-scope change was rejected (status=$(status_of t-ok)); every result below is meaningless"
  sed 's/^/        /' "$TMP/out-t-ok" | tail -6
fi

# --- 2) writing a CONTROL-PLANE file is refused --------------------------------------------
mktask t-cp "apps/chiron" "test -s apps/chiron/a.txt"
run_case t-cp 'mkdir -p apps/chiron && echo x > apps/chiron/a.txt && echo "evil" > scripts/pwn.sh'
if [ "$(status_of t-cp)" != "passed" ] && inbox_tail | grep -q 'SCOPE VIOLATION'; then
  ok "control-plane write (scripts/) is REFUSED and escalated"
else
  no "control-plane write was accepted (status=$(status_of t-cp))"
fi

# --- 3) editing a TEST file is refused (the gate cannot see this) ---------------------------
mktask t-test "apps/chiron" "test -s apps/chiron/b.txt"
run_case t-test 'mkdir -p apps/chiron && echo x > apps/chiron/b.txt && echo "assert(true)" >> scripts/tests/existing.test.cjs'
if [ "$(status_of t-test)" != "passed" ]; then
  ok "editing a *.test.cjs is REFUSED (tamper path the acceptance gate cannot detect)"
else
  no "a test-file edit reached 'passed'"
fi

# --- 4) wandering outside allowed_paths is refused ------------------------------------------
mktask t-out "apps/chiron" "test -s apps/chiron/c.txt"
run_case t-out 'mkdir -p apps/chiron other && echo x > apps/chiron/c.txt && echo y > other/stray.txt'
if [ "$(status_of t-out)" != "passed" ] && inbox_tail | grep -qi 'outside allowed_paths'; then
  ok "a write outside allowed_paths is REFUSED and names the offending path"
else
  no "an out-of-scope write was accepted (status=$(status_of t-out))"
fi

# --- 5) ★ ORDER: the scope check runs BEFORE the acceptance gate ----------------------------
# The acceptance command leaves a marker. On a scope violation it must never have run.
mktask t-order "apps/chiron" "touch $MARKER"
run_case t-order 'mkdir -p apps/chiron && echo x > apps/chiron/d.txt && echo evil > scripts/pwn2.sh'
if [ ! -f "$MARKER" ] && [ "$(status_of t-order)" != "passed" ]; then
  ok "★ the scope check runs BEFORE the gate (acceptance never executed on a violating diff)"
else
  no "★ the acceptance gate RAN on a scope-violating diff — a tampered pass would be declared first"
fi

# --- 6) a `blocked` result escalates the arm's QUESTION and skips the gate -------------------
mktask t-blocked "apps/chiron" "touch $MARKER"
run_case t-blocked 'printf "{\"status\":\"blocked\",\"summary\":\"two readings\",\"blocker\":\"Which realm is the target?\"}" > .recursion-result.json'
if [ "$(status_of t-blocked)" = "blocked" ] && inbox_tail | grep -q 'Which realm is the target'; then
  ok "an ambiguity STOP is recorded as blocked and carries the arm's own question"
else
  no "a blocked result was not handled (status=$(status_of t-blocked))"
fi
[ ! -f "$MARKER" ] && ok "blocked: the acceptance gate was not run (it would certainly fail)" \
                   || no "blocked: the gate ran anyway"

# --- 7) the envelope actually reaches the arm -----------------------------------------------
# Capture the prompt the arm receives and assert the boundary is stated in it. A gate that
# enforces silently, with a prompt that never mentions the rule, teaches the arm nothing.
cat > "$BIN/claude" <<'STUB'
#!/usr/bin/env bash
prev=""
for a in "$@"; do
  [ "$prev" = "-p" ] && { printf '%s' "$a" > "$STUB_PROMPT_OUT"; break; }
  prev="$a"
done
exit 0
STUB
chmod +x "$BIN/claude"
mktask t-prompt "apps/chiron" "test -s apps/chiron/seed.txt"
export STUB_PROMPT_OUT="$TMP/prompt.txt"
( cd "$R" && PATH="$BIN:$PATH" RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 RECURSION_GIT_FETCH=0 \
    RECURSION_TEST_WORKER=logical STUB_PROMPT_OUT="$TMP/prompt.txt" bash scripts/work.sh t-prompt ) >/dev/null 2>&1
miss=""
for phrase in "bounded executor" "ALLOWED PATHS" "PROTECTED" "ON AMBIGUITY" "recursion-result.json" "Hermes owns planning"; do
  grep -qF "$phrase" "$TMP/prompt.txt" 2>/dev/null || miss="$miss '$phrase'"
done
[ -z "$miss" ] && ok "the envelope reaches the arm (authority, paths, protections, stop rule, schema)" \
               || no "the arm prompt is missing:$miss"

echo
[ "$fails" -eq 0 ] && { echo "worker-envelope: ALL PASS"; exit 0; }
echo "worker-envelope: $fails FAILED"; exit 1

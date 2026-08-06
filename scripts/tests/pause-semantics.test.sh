#!/usr/bin/env bash
# pause-semantics.test.sh — PAUSE halts EXECUTION and preserves AWARENESS (D-012).
#
# WHY. Three documents and pause.sh's own message promised "heartbeat + escalation still
# reach you" while cycle.sh and run.sh both exited before the heartbeat. Docs and code
# disagreed for as long as the kill switch existed, and nothing could catch it because
# nothing tested the paused path. This is that test.
#
# HOW. It runs the REAL cycle.sh against a disposable copy of the repo, with a stub `hermes`
# earlier on PATH. No model is called, no Telegram message is sent, no spend. The stub also
# absorbs `hermes send`, which is notify.sh's preferred delivery path.
#
# ★ Test 2 is the one that matters: it asserts NO EXECUTION happened. Asserting only that the
# heartbeat ran would pass on a build that also launched arms while paused.
#
#   run: bash scripts/tests/pause-semantics.test.sh
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/bin"; mkdir -p "$BIN"

# --- stub engine: answers the heartbeat, the brief, and notify.sh's `hermes send` ----------
cat > "$BIN/hermes" <<'STUB'
#!/usr/bin/env bash
# `hermes send ...` -> notify.sh delivery path. Record it; never contact Telegram.
if [ "${1:-}" = "send" ]; then
  shift; printf '%s\n' "NOTIFY $*" >> "${STUB_NOTIFY_LOG:-/dev/null}"; exit 0
fi
# `hermes -z <prompt> -m <model> --usage-file <f>` -> one-shot completion.
usage=""; prompt=""
while [ $# -gt 0 ]; do
  case "$1" in
    -z) prompt="$2"; shift 2 ;;
    --usage-file) usage="$2"; shift 2 ;;
    *) shift ;;
  esac
done
[ -n "$usage" ] && printf '{"provider":"openai-codex","estimated_cost_usd":0.0,"total_tokens":1}\n' > "$usage"
# Heartbeat prompts ask for the ===HEARTBEAT:=== sentinel; briefs want prose.
if printf '%s' "$prompt" | grep -q 'HEARTBEAT'; then
  echo "stub heartbeat"; echo "===HEARTBEAT: quiet==="
else
  echo "# stub brief"; echo "nothing to report"
fi
exit 0
STUB
chmod +x "$BIN/hermes"

# claude must NOT be reachable: if anything tries to run an arm while paused, we want a loud
# artifact rather than a silent success.
cat > "$BIN/claude" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "ARM LAUNCHED WHILE PAUSED" >> "${STUB_ARM_LOG:-/dev/null}"
exit 0
STUB
chmod +x "$BIN/claude"

# --- disposable repo copy (never touch the live tree) --------------------------------------
R="$TMP/repo"; mkdir -p "$R"
tar -C "$SRC" -cf - scripts loop state ANCHOR.md CLAUDE.md 2>/dev/null | tar -C "$R" -xf - 2>/dev/null
mkdir -p "$R/state/briefs" "$R/loop/logs" "$R/state/tasks"
: > "$R/.env"
( cd "$R" && git init -q . && git add -A >/dev/null 2>&1 \
  && git -c user.name=t -c user.email=t@t commit -qm init >/dev/null 2>&1 \
  && git checkout -qb loop/auto ) || true

export STUB_NOTIFY_LOG="$TMP/notify.log"; : > "$STUB_NOTIFY_LOG"
export STUB_ARM_LOG="$TMP/arm.log";       : > "$STUB_ARM_LOG"

B="$R/state/briefs/$(date +%F).md"

run_cycle(){ # $1=force|""
  # ★ Clear the artifacts this run is judged on. The repo ships COMMITTED briefs and a
  # populated INBOX, so without this a test could "pass" on a file the archive supplied and
  # the run never wrote — asserting on history instead of behaviour. (Caught by running the
  # suite against the pre-fix scripts: it reported a brief written by a run that exits first.)
  rm -f "$R"/state/briefs/*.md
  printf '# Inbox\n\n_(empty)_\n' > "$R/state/INBOX.md"
  ( cd "$R" && PATH="$BIN:$PATH" RECURSION_ROOT="$R" \
      RECURSION_AUTO_DRAIN=1 RECURSION_AUTO_PLAN=1 RECURSION_AUTO_REFLECT=1 \
      RECURSION_PLAN_WORKSTREAMS="" \
      bash scripts/cycle.sh "${1:-}" ) >"$TMP/cycle.out" 2>&1
}

# =========================== PAUSED ===========================
printf 'PAUSED test\nreason: pause-semantics test\n' > "$R/state/PAUSE"
# a queued task so the drainer WOULD have something to do if it wrongly ran
cat > "$R/state/tasks/ptest-pause.md" <<'T'
id: ptest-pause
workstream: ptest
goal: must never run while paused
engine: claude
acceptance: true
status: queued
T
run_cycle force

# --- 1) AWARENESS: the heartbeat ran -------------------------------------------------------
if grep -q 'heartbeat signal=' "$TMP/cycle.out"; then
  ok "paused: heartbeat RAN (awareness preserved)"
else
  no "paused: heartbeat did not run — the box is blind while paused"
  sed 's/^/        /' "$TMP/cycle.out" | head -5
fi

# --- 2) ★ NO EXECUTION: no arm, no drain, no reflect, task untouched -----------------------
exec_faults=""
[ -s "$STUB_ARM_LOG" ] && exec_faults="$exec_faults arm-launched"
grep -q 'auto-drain: queued work' "$TMP/cycle.out" && exec_faults="$exec_faults drain-kicked"
grep -q 'auto-reflect: daily self-review' "$TMP/cycle.out" && exec_faults="$exec_faults reflect-ran"
[ "$(sed -n 's/^status: *//p' "$R/state/tasks/ptest-pause.md" | head -1)" = "queued" ] \
  || exec_faults="$exec_faults task-status-changed"
if [ -z "$exec_faults" ]; then
  ok "paused: NO execution (no arm, no drain, no reflect, task still queued)"
else
  no "paused: EXECUTION LEAKED —$exec_faults"
fi

# --- 3) the brief exists and is labelled PAUSED --------------------------------------------
if [ -f "$B" ] && head -3 "$B" | grep -q 'PAUSED'; then
  ok "paused: brief written and labelled PAUSED"
elif [ -f "$B" ]; then
  no "paused: brief written but NOT labelled — reads like a normal brief"
else
  no "paused: no brief written (escalations ride in the brief path)"
fi

# --- 4) escalation delivery still works while paused ---------------------------------------
# Feed the stub an escalation block by making the brief prompt emit one.
cat > "$BIN/hermes" <<'STUB'
#!/usr/bin/env bash
if [ "${1:-}" = "send" ]; then shift; printf '%s\n' "NOTIFY $*" >> "${STUB_NOTIFY_LOG:-/dev/null}"; exit 0; fi
usage=""; prompt=""
while [ $# -gt 0 ]; do case "$1" in -z) prompt="$2"; shift 2;; --usage-file) usage="$2"; shift 2;; *) shift;; esac; done
[ -n "$usage" ] && printf '{"provider":"openai-codex","estimated_cost_usd":0.0,"total_tokens":1}\n' > "$usage"
if printf '%s' "$prompt" | grep -q 'HEARTBEAT'; then echo "===HEARTBEAT: brief=== test"; else
  echo "# stub brief"; echo "===INBOX-START==="; echo "## test — a decision is needed"; echo "===INBOX-END==="
fi
exit 0
STUB
chmod +x "$BIN/hermes"
: > "$STUB_NOTIFY_LOG"
run_cycle force
if grep -q 'a decision is needed' "$R/state/INBOX.md" 2>/dev/null && [ -s "$STUB_NOTIFY_LOG" ]; then
  ok "paused: escalation reached BOTH the durable INBOX and the notifier"
else
  no "paused: escalation did not reach INBOX and/or notifier while paused"
fi

# --- 5) the paused ping is tagged so it cannot be mistaken for actionable ------------------
if grep -q 'PAUSED' "$STUB_NOTIFY_LOG"; then
  ok "paused: escalation ping is tagged PAUSED"
else
  no "paused: escalation ping is untagged — reads as though the box will act on it"
fi

# =========================== RESUMED (the control) ===========================
# Without this, every assertion above would also pass on a build that simply never executes.
rm -f "$R/state/PAUSE"
: > "$STUB_ARM_LOG"
run_cycle force
if grep -q 'auto-drain: queued work' "$TMP/cycle.out"; then
  ok "CONTROL — resumed: the drainer DOES run (the gates above are not vacuous)"
else
  no "CONTROL FAILED — resumed and the drainer still did not run; the paused assertions prove nothing"
  sed 's/^/        /' "$TMP/cycle.out" | tail -5
fi

echo
[ "$fails" -eq 0 ] && { echo "pause-semantics: ALL PASS"; exit 0; }
echo "pause-semantics: $fails FAILED"; exit 1

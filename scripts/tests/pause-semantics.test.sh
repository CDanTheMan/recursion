#!/usr/bin/env bash
# pause-semantics.test.sh — PAUSE halts EXECUTION and preserves AWARENESS (D-012).
#
# WHY. PAUSE preserves local awareness but must prohibit every human-visible send. The 2026-08-10
# 06:30Z forced cycle proved that setting DELIVER_BRIEF=1 and invoking digest.sh under PAUSE could
# bypass the Phase 7 outbox, make nine legacy transport calls, and leave the brief tracked dirty.
#
# HOW. It runs the REAL cycle.sh against a disposable copy of the repo, with a stub `hermes`
# earlier on PATH. No model is called, no Telegram message is sent, no spend. The stub also
# absorbs `hermes send`, which is notify.sh's preferred delivery path.
#
# ★ Tests 1b and 2 are the ones that matter. Test 1b proves awareness without allowing the
# checked-out executable tree to move; test 2 proves no worker execution happened. Asserting only
# that the heartbeat ran would pass on a build that also changed code or launched arms while paused.
#
#   run: bash scripts/tests/pause-semantics.test.sh
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

# PLATFORM-BOUND (measured 2026-08-27 on Windows Git Bash; this suite passes on Linux). This test
# runs the REAL cycle.sh, and cycle.sh is gated on two Linux-only runtime facilities that no stub
# can honestly stand in for:
#
#   1. `flock` (util-linux) — cycle.sh takes the whole-cycle lock on fd 9 before anything else.
#      Git Bash ships no flock, so `flock -n 9` fails, every invocation logs "cycle overlap
#      refused" and exits 73, and all twelve checks below judge a cycle that never started.
#   2. the witnessed directory lock — taskctl.sh hands `$$` to scripts/runtime-state.py
#      lock-acquire, which witnesses the owner by reading that PID's process start time. Under Git
#      Bash `$$` is the MSYS process id, not the Windows process id (the latter is readable at
#      /proc/$$/winpid), so the witness fails and durable escalation writes are refused with
#      "cannot witness lock owner process start".
#
# Both were confirmed by experiment: stubbing flock alone turns the first six checks green and
# then check 5 and all three RESUMED ★ CONTROLs still fail on (2) — i.e. exactly the controls that
# keep the paused assertions from being vacuous. A suite that reports six passes and cannot run
# its own controls is worse than one that says it did not run, so it says it did not run.
if [ "$(uname -s)" != Linux ]; then
  echo "pause-semantics: SKIP on $(uname -s) — cycle.sh needs flock (absent in Git Bash: every cycle exits 73 at the whole-cycle lock) and taskctl.sh's witnessed lock needs a Linux PID witness (Git Bash \$\$ is the MSYS pid, not the Windows pid)."
  echo "pause-semantics: NOT RUN — awareness/heartbeat, portfolio fetch-without-maintenance, no-execution, PAUSED brief labelling, transport silence, self-repo Git preservation, durable escalation, and all three resumed ★ CONTROLs."
  exit 0
fi

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
# Earlier suites may have populated ignored derived caches in SRC. They are not fixture input:
# copying them before this fixture's git init would accidentally make them tracked authority.
tar -C "$SRC" --exclude='scripts/__pycache__' --exclude='loop/logs/*' \
  --exclude='state/jsonl-index' --exclude='state/recovery/transition-archive' \
  --exclude='state/recovery/transition-event-index' \
  -cf - scripts loop state ANCHOR.md CLAUDE.md .gitignore 2>/dev/null \
  | tar -C "$R" -xf - 2>/dev/null
mkdir -p "$R/state/briefs" "$R/loop/logs" "$R/state/tasks"
rm -f "$R"/loop/logs/*
: > "$R/.env"
# Replace the copied production registry with one disposable active repo. Its origin advances by
# one executable-file commit while its checked-out main stays behind. A paused cycle must fetch
# that remote tip and report BEHIND, but must not move main or the checked-out executable file.
GIT="git -c user.name=t -c user.email=t@t -c init.defaultBranch=main"
PORT_ORIGIN="$TMP/portfolio-origin.git"
PORT_SEED="$TMP/portfolio-seed"
PORT_REPO="$TMP/portfolio-repo"
$GIT init -q --bare "$PORT_ORIGIN"
$GIT init -q "$PORT_SEED"
mkdir -p "$PORT_SEED/scripts"
printf '#!/usr/bin/env bash\necho one\n' > "$PORT_SEED/scripts/pause-probe.sh"
chmod +x "$PORT_SEED/scripts/pause-probe.sh"
( cd "$PORT_SEED" && $GIT add -A && $GIT commit -qm one && $GIT branch -M main \
  && $GIT remote add origin "$PORT_ORIGIN" && $GIT push -q origin main )
$GIT --git-dir="$PORT_ORIGIN" symbolic-ref HEAD refs/heads/main
$GIT clone -q "$PORT_ORIGIN" "$PORT_REPO"
printf '#!/usr/bin/env bash\necho two\n' > "$PORT_SEED/scripts/pause-probe.sh"
( cd "$PORT_SEED" && $GIT add -A && $GIT commit -qm two && $GIT push -q origin main )
PORT_BEFORE="$($GIT -C "$PORT_REPO" rev-parse main)"
PORT_TREE_BEFORE="$(sha256sum "$PORT_REPO/scripts/pause-probe.sh" | awk '{print $1}')"
PORT_REMOTE="$($GIT -C "$PORT_SEED" rev-parse main)"
{
  printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n'
  printf 'pause-probe\t%s\t%s\tmain\t-\t-\t-\tactive\n' "$PORT_REPO" "$PORT_ORIGIN"
} > "$R/state/portfolio.tsv"
# The disposable clone is configured, not just initialised, because the REAL scripts commit inside
# it and inherit whatever this machine happens to provide:
#
#   * user.name/user.email — cycle.sh (`git commit -q -m "loop: board ..." 2>/dev/null || true`)
#     and work.sh both stage state and swallow a failed commit. This fixture supplied an identity
#     to its OWN commit via `git -c`, but never wrote one into the clone, so those commits used
#     the ambient identity. Under root git derives one from the passwd entry and they succeed;
#     under an ordinary account with an empty gecos name git refuses with "empty ident name", the
#     commit is silently dropped, and everything the cycle wrote stays STAGED — which the final
#     ★ CONTROL then reports as "resumed forced cycle left tracked state dirty". That is the
#     runner's account leaking into a PAUSE assertion, not a state leak. (Reproduced 2026-08-27:
#     identical suite, same machine, passes as root and fails as a non-root user.)
#   * core.autocrlf — a per-clone setting inherited from the developer's global config. If it is
#     on, tracked text is checked out CRLF, every file the cycle rewrites comes back LF, and the
#     same ★ CONTROL reports "M state/INBOX.md" for a line-ending artefact.
#
# Both are no-ops on the deploy box, which already has an identity and autocrlf off.
( cd "$R" && git init -q . \
  && git config user.name t && git config user.email t@t \
  && git config core.autocrlf false && git config core.eol lf \
  && git add -A >/dev/null 2>&1 \
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
  rm -f "$R"/loop/logs/*
  printf '# Inbox\n\n_(empty)_\n' > "$R/state/INBOX.md"
  if [ -f "$R/state/PAUSE" ]; then
    PAUSED_SELF_BRANCH="$($GIT -C "$R" branch --show-current)"
    PAUSED_SELF_HEAD="$($GIT -C "$R" rev-parse HEAD)"
    PAUSED_SELF_BOARD="$(sha256sum "$R/state/BOARD.md" | awk '{print $1}')"
    PAUSED_SELF_REFLOG="$($GIT -C "$R" reflog --format=%H | sha256sum | awk '{print $1}')"
  fi
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

# --- 1b) AWARENESS WITHOUT MAINTENANCE: fetch/status runs, executable tree stays exact -------
# The production defect this guards was observed at 2026-08-10T03:15Z: paused cycle -> sync
# fast-forwarded master and then merged it into the checked-out loop/auto tree. Remote-tracking
# refs are awareness; moving a local branch or checked-out file is branch-changing maintenance.
PORT_AFTER="$($GIT -C "$PORT_REPO" rev-parse main)"
PORT_TREE_AFTER="$(sha256sum "$PORT_REPO/scripts/pause-probe.sh" | awk '{print $1}')"
PORT_FETCHED="$($GIT -C "$PORT_REPO" rev-parse origin/main)"
if [ "$PORT_AFTER" = "$PORT_BEFORE" ] \
    && [ "$PORT_TREE_AFTER" = "$PORT_TREE_BEFORE" ] \
    && [ "$PORT_FETCHED" = "$PORT_REMOTE" ] \
    && grep -q 'BEHIND.*pause-probe\|pause-probe.*BEHIND' "$R"/loop/logs/*-cycle.log; then
  ok "paused: fetch/status reports BEHIND without changing local main or its executable tree"
else
  no "paused: portfolio awareness changed a branch/tree or failed to fetch/report (main $PORT_BEFORE -> $PORT_AFTER; tree $PORT_TREE_BEFORE -> $PORT_TREE_AFTER; fetched=$PORT_FETCHED remote=$PORT_REMOTE)"
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

# --- 4) ★ PAUSE produces no transport call and leaves the tracked tree clean ----------------
if [ ! -s "$STUB_NOTIFY_LOG" ]; then
  ok "paused: no brief, digest, escalation, or fallback transport was invoked"
else
  no "paused: HUMAN-VISIBLE SEND LEAKED — $(cat "$STUB_NOTIFY_LOG")"
fi
if [ "$($GIT -C "$R" branch --show-current)" = "$PAUSED_SELF_BRANCH" ] \
    && [ "$($GIT -C "$R" rev-parse HEAD)" = "$PAUSED_SELF_HEAD" ] \
    && [ "$(sha256sum "$R/state/BOARD.md" | awk '{print $1}')" = "$PAUSED_SELF_BOARD" ] \
    && [ "$($GIT -C "$R" reflog --format=%H | sha256sum | awk '{print $1}')" = "$PAUSED_SELF_REFLOG" ]; then
  ok "paused: forced monitoring preserves self-repo branch, HEAD, BOARD, and reflog"
else
  no "paused: forced monitoring mutated self-repo Git state (branch=$($GIT -C "$R" branch --show-current), HEAD=$($GIT -C "$R" rev-parse --short HEAD))"
fi

# --- 5) escalation remains durable locally but is not sent while paused --------------------
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
if grep -q 'a decision is needed' "$R/state/INBOX.md" 2>/dev/null && [ ! -s "$STUB_NOTIFY_LOG" ]; then
  ok "paused: escalation reached durable INBOX without invoking a transport"
else
  no "paused: escalation was not durable or leaked to transport: $(cat "$STUB_NOTIFY_LOG")"
  sed 's/^/        /' "$TMP/cycle.out" | tail -20
fi

# --- 6) no stale brief/digest delivery is queued during PAUSE ------------------------------
if ! grep -Eq '"event":"(portfolio-brief|project-digest)"' "$R/state/events.jsonl" 2>/dev/null; then
  ok "paused: no stale brief or digest source event is queued for a later window"
else
  no "paused: a brief/digest event was queued for replay after PAUSE"
fi

# =========================== RESUMED (the control) ===========================
# Without this, every assertion above would also pass on a build that simply never executes.
rm -f "$R/state/PAUSE"
: > "$STUB_ARM_LOG"
: > "$STUB_NOTIFY_LOG"
run_cycle force
if grep -q 'auto-drain: queued work' "$TMP/cycle.out"; then
  ok "CONTROL — resumed: the drainer DOES run (the gates above are not vacuous)"
else
  no "CONTROL FAILED — resumed and the drainer still did not run; the paused assertions prove nothing"
  sed 's/^/        /' "$TMP/cycle.out" | tail -5
fi
if [ "$($GIT -C "$PORT_REPO" rev-parse main)" = "$PORT_REMOTE" ] \
    && [ "$(sha256sum "$PORT_REPO/scripts/pause-probe.sh" | awk '{print $1}')" != "$PORT_TREE_BEFORE" ]; then
  ok "CONTROL — resumed: portfolio sync DOES fast-forward the branch and executable tree"
else
  no "CONTROL FAILED — resumed portfolio sync did not fast-forward; the paused no-change assertion is vacuous"
fi
if grep -q '"event":"portfolio-brief"' "$R/state/events.jsonl" 2>/dev/null \
    && grep -q '"event":"project-digest"' "$R/state/events.jsonl" 2>/dev/null \
    && [ ! -s "$STUB_NOTIFY_LOG" ]; then
  ok "CONTROL — resumed: brief and digest enter the canonical event/outbox path with no direct send"
else
  no "CONTROL FAILED — resumed brief/digest did not use the canonical event path or called notify directly"
fi
if $GIT -C "$R" diff --quiet && $GIT -C "$R" diff --cached --quiet; then
  ok "CONTROL — resumed forced cycle also leaves tracked state clean"
else
  no "CONTROL FAILED — resumed forced cycle left tracked state dirty: $($GIT -C "$R" status --short)"
fi

echo
[ "$fails" -eq 0 ] && { echo "pause-semantics: ALL PASS"; exit 0; }
echo "pause-semantics: $fails FAILED"; exit 1

#!/usr/bin/env bash
# hermes-decide.sh — Hermes DECIDES what runs next. It does not act.
#
# WHY THE SPLIT. CONTROL_PLANE.md makes Hermes the executive: it owns the portfolio and
# chooses the next work. But Hermes' tool-calling turns fall off the Codex subscription onto
# metered OpenRouter (measured 2026-08-05, and why work.sh fences the hermes arm behind
# RECURSION_ALLOW_METERED). An executive that ACTS through tool calls would quietly convert a
# flat subscription into a metered bill, and would also become a second implementer.
#
# So: this script assembles ground truth, asks a TEXT-ONLY model for one decision, validates
# it, and records it. conduct-hermes.sh is the only thing that executes, and it executes only
# through the existing proven scripts. Authority moves; actuation does not.
#
# Carries no state: the brief is re-derived from disk every run (a state block baked into a
# prompt rots in days and reads as working).
#
#   hermes-decide.sh              decide, print the decision, record it
#   hermes-decide.sh --brief      print the assembled state brief and exit (no model call)
#   hermes-decide.sh --dry-run    decide and validate, but do not record
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a

MODE="${1:-}"
DATE="$(date +%F)"; STAMP="$(date -u +%FT%TZ)"
LOG_DIR="$ROOT/loop/logs"; mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$DATE-decide.log"
OUT="$LOG_DIR/$DATE-decide.out"
USAGE="$LOG_DIR/$DATE-decide.usage.json"
DECISIONS="$ROOT/state/decisions.jsonl"
LATEST="$ROOT/state/.decision-latest.json"
MODEL="${RECURSION_DECIDE_MODEL:-gpt-5.6-terra}"
log(){ echo "[$(date -Is)] decide: $*" | tee -a "$LOG" >&2; }

# The verbs Hermes may choose. This list is the contract: conduct-hermes.sh refuses anything
# else, so adding a verb here without adding it there is inert, and vice versa.
VERBS="noop plan work conduct publish escalate resolve-esc reap"

# --- the state brief: ground truth, re-derived every run ---------------------------------
build_brief(){
  echo "===== AUTHORITY (you are bound by this) ====="
  sed -n '1,60p' CONTROL_PLANE.md 2>/dev/null || echo "(CONTROL_PLANE.md absent)"
  echo; echo "===== INSTRUCTIONS FROM LUCAS (highest priority — he is the principal) ====="
  # What he actually said, in his words, from the cockpit. These outrank the roadmaps: a roadmap
  # is what was planned, an open instruction is what he wants now.
  bash scripts/intake.sh open 2>/dev/null || echo "(none)"
  echo; echo "===== SCOPE (ANCHOR) ====="
  sed -n '1,60p' ANCHOR.md 2>/dev/null
  echo; echo "===== DECISIONS (open calls you must honour) ====="
  grep -E '^## D-|^\*\*Chose:|^\*\*Falsifier:|^Date:' state/DECISIONS.md 2>/dev/null | tail -60
  echo; echo "===== RUNTIME: PAUSE ====="
  if [ -f state/PAUSE ]; then echo "PAUSED — execution is halted. You may still decide; the only"
    echo "executable verb while paused is 'noop'. Say what you WOULD do and why."
    cat state/PAUSE; else echo "not paused"; fi
  echo; echo "===== TASKS (canonical state) ====="
  for f in state/tasks/*.md; do
    [ -f "$f" ] || continue
    printf '%-26s status=%-10s ws=%-16s attempts=%-3s lease_expires=%-12s goal=%s\n' \
      "$(sed -n 's/^id: *//p' "$f"|head -1)" "$(sed -n 's/^status: *//p' "$f"|head -1)" \
      "$(sed -n 's/^workstream: *//p' "$f"|head -1)" "$(sed -n 's/^attempts: *//p' "$f"|head -1)" \
      "$(sed -n 's/^lease_expires: *//p' "$f"|head -1)" "$(sed -n 's/^goal: *//p' "$f"|head -1)"
  done
  echo; echo "===== OPEN ESCALATIONS (blockers — who owns each?) ====="
  bash scripts/taskctl.sh esc-list open 2>/dev/null | awk -F'\t' '{printf "%s  [%s seen %sx]  %s\n",$1,$7,$6,$9}' || echo "(none)"
  echo; echo "===== ASSISTS (tasks waiting on a HUMAN — you cannot unblock these) ====="
  # A task with an open assist is not queued work: re-dispatching it burns an arm to produce the
  # same question. Only Lucas can close these.
  bash scripts/assist.sh list open 2>/dev/null || echo "(none)"
  echo; echo "===== RECENT EVENTS ====="
  tail -25 state/events.jsonl 2>/dev/null || echo "(no events)"
  echo; echo "===== ROADMAPS (human-set direction) ====="
  for r in state/roadmaps/*.md; do [ -f "$r" ] || continue
    echo "--- $r"; grep -nE '^- \[' "$r" | head -12; done
  echo; echo "===== REVIEW BRANCHES (what awaits Lucas) ====="
  bash scripts/branch-review.sh 2>/dev/null | head -40
  echo; echo "===== PORTFOLIO (git-native truth; a repo whose freshness cannot be PROVEN is not dispatchable) ====="
  # This fetches every registered repo, so the brief reports the real remote, not a stale
  # remote-tracking ref. A repo in FAULT or DIVERGED must not be dispatched at — choose escalate.
  bash scripts/resync.sh status 2>/dev/null || echo "(some repos are not provably current — see above)"
  echo; echo "===== CAPACITY (do not queue work this box cannot run) ====="
  # scripts/capacity.sh is the decider, so the brief shows exactly what the conductor will act
  # on. A brief that computes its own numbers can disagree with the gate that enforces them.
  bash scripts/capacity.sh report 2>/dev/null || echo "(capacity unreadable — treat the box as full)"
  echo; echo "===== PROPOSALS (human-gated; you may not apply these) ====="
  tail -25 state/PROPOSALS.md 2>/dev/null
}

if [ "$MODE" = "--brief" ]; then build_brief; exit 0; fi

PROMPT="You are HERMES, the executive control plane for the Recursion system.

Lucas is the principal. You own the portfolio, choose what runs next, and monitor it. You are
NOT an implementer: you never write code and never edit files. You emit ONE decision; a
deterministic script executes it through already-proven tooling.

Choose exactly one verb:
  noop        nothing should run right now — ALWAYS valid, and correct more often than not
  plan <ws>   turn the next roadmap item for workstream <ws> into a task
  work <id>   run a specific queued task through the build loop
  conduct     drain the queue in parallel, under existing bounds
  publish <branch>  push a review branch for Lucas
  escalate <key> <title>   raise a blocker that needs a human
  resolve-esc <esc-id>     close an escalation that is demonstrably settled
  reap        reclaim dead task leases

HARD RULES
- If the box is PAUSED, the only executable verb is 'noop'. Decide anyway and explain.
- Never choose work that has no machine-checkable acceptance gate.
- Never choose anything that merges, deploys, spends money, or touches auth/cron/.env/flags.
  Those are Lucas's. If one is needed, choose 'escalate'.
- Prefer 'noop' over inventing work. Generation that outruns review is a liability, not
  progress; an idle box with a clear reason is a good outcome.
- Every decision must serve a goal that already exists in the roadmaps or DECISIONS. If the
  most valuable next step is not written down anywhere, choose 'escalate' and say so.
- Never dispatch work at a repo the PORTFOLIO section reports as FAULT or DIVERGED. A repo whose
  freshness cannot be proven will silently build on a stale base and revert merged fixes.
- Never dispatch a task that has an OPEN assist. It is waiting on Lucas, and running it again
  produces the same question at the cost of an arm.
- If CAPACITY reports DEFER, do not choose 'conduct' or 'work'. The box cannot take the load, and
  queueing into a full box produces timeouts that look like failing tests. 'noop' is correct.
- An OPEN INSTRUCTION from Lucas is the highest-priority input you have. Act on it through the
  verbs you are given, or 'escalate' saying precisely what you cannot do — but never ignore one
  and never silently reinterpret it. If it asks for something outside your verbs (a new project, a
  new roadmap, a flag change), 'escalate' is the correct answer, not a workaround.

Reply with reasoning first, then EXACTLY this block and nothing after it:

===DECISION-START===
{\"verb\":\"...\",\"args\":[\"...\"],\"project\":\"...\",\"goal\":\"the existing goal this serves\",\"why\":\"one or two sentences\",\"confidence\":\"high|medium|low\",\"wrong_if\":\"the specific observable that would mean this was the wrong call\"}
===DECISION-END===

'goal' and 'wrong_if' are mandatory. A decision that cannot name the goal it serves, or what
would make it wrong, is a guess — choose 'escalate' instead of writing one.

=================== STATE (ground truth, re-derived this run) ===================
$(build_brief)"

log "deciding (model=$MODEL)"
if ! hermes -z "$PROMPT" -m "$MODEL" --usage-file "$USAGE" >"$OUT" 2>>"$LOG"; then
  log "FAILED — hermes returned non-zero; see $LOG"
  exit 1
fi

# --- COST FENCE: the whole design rests on this staying free. ----------------------------
# A silent fallback to metered OpenRouter is the failure D-008 warned about, and it would make
# an always-on executive quietly expensive. Refuse the decision rather than act on a billed one.
PROV="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("provider",""))' "$USAGE" 2>/dev/null || true)"
COST="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("estimated_cost_usd",0))' "$USAGE" 2>/dev/null || echo 0)"
if [ -n "$PROV" ] && [ "$PROV" != "openai-codex" ]; then
  log "REFUSED — decision ran on '$PROV' (cost=\$$COST), not the flat sub."
  bash scripts/notify.sh "⚠ Recursion: a Hermes DECISION fell back to $PROV (\$$COST). Decision discarded — the executive must stay on the flat sub." || true
  exit 3
fi

# --- extract + validate the decision ------------------------------------------------------
BLOCK="$(awk '/^===DECISION-START===/{f=1;next} /^===DECISION-END===/{f=0} f' "$OUT")"
if [ -z "${BLOCK//[[:space:]]/}" ]; then
  log "REFUSED — no decision block in the reply"; exit 4
fi

# Validation lives in scripts/validate-decision.py — one definition, exercised directly by
# the test suite. It was inlined here as a heredoc-fed snippet and was SILENTLY BROKEN:
# `python3 - <<PY` consumes stdin for the script, so the piped JSON never arrived and every
# decision was rejected. Passing the payload as an argument removes the stdin ambiguity.
VALID="$(python3 "$ROOT/scripts/validate-decision.py" "$VERBS" "$BLOCK" 2>&1)"

case "$VALID" in
  OK\ *) DECISION="${VALID#OK }" ;;
  *) log "REFUSED — ${VALID:-validation produced no output}"; printf '%s\n' "$BLOCK" >>"$LOG"; exit 5 ;;
esac

VERB="$(printf '%s' "$DECISION" | python3 -c 'import json,sys;print(json.load(sys.stdin)["verb"])')"
log "decision: $VERB — $(printf '%s' "$DECISION" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("why",""))' | cut -c1-120)"

[ "$MODE" = "--dry-run" ] && { printf '%s\n' "$DECISION"; exit 0; }

# --- record: the decision is durable state, not a chat message ---------------------------
python3 - "$DECISIONS" "$LATEST" "$STAMP" "$PROV" "$COST" <<PY
import json,sys
d=json.loads('''$DECISION''')
d['ts']=sys.argv[3]; d['provider']=sys.argv[4]; d['cost_usd']=sys.argv[5]
open(sys.argv[1],'a',encoding='utf-8').write(json.dumps(d,sort_keys=True)+"\n")
open(sys.argv[2],'w',encoding='utf-8').write(json.dumps(d,sort_keys=True)+"\n")
PY
bash scripts/taskctl.sh event decision "" "$VERB $(printf '%s' "$DECISION" | python3 -c 'import json,sys;print(" ".join(json.load(sys.stdin).get("args",[])))')" >/dev/null 2>&1 || true
printf '%s\n' "$DECISION"

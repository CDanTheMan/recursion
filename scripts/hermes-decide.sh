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
# .env pins RECURSION_ROOT for the deployed checkout. Sourcing it must never RETARGET a
# caller who passed a different root: that silently made a "sandbox" enqueue ten decisions
# into production on 2026-08-12. ROOT and RECURSION_ROOT agree from here on.
RECURSION_ROOT="$ROOT"; export RECURSION_ROOT

MODE="${1:-}"
DATE="$(date +%F)"; STAMP="$(date -u +%FT%TZ)"; RUN_TAG="$(date -u +%Y%m%dT%H%M%SZ)-$$"
LOG_DIR="$ROOT/loop/logs"; mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$DATE-decide.log"
OUT="$LOG_DIR/$DATE-decide-$RUN_TAG.out"
USAGE="$LOG_DIR/$DATE-decide-$RUN_TAG.usage.json"
DECISIONS="$ROOT/state/decisions.jsonl"
MODEL="${RECURSION_DECIDE_MODEL:-gpt-5.6-terra}"
log(){ echo "[$(date -Is)] decide: $*" | tee -a "$LOG" >&2; }

# Decision-time resync reads and fetches git truth. The actuator may mutate the same repos, so
# both halves take one fail-closed lock instead of colliding through independent schedules.
#
# WAIT for it, do not try once. conduct-hermes.sh takes this same lock on fd 8, and since the
# Phase 8 actuator became a persistent service it runs on a 2s poll: production measured the
# lock held for 18 of 60 half-second samples, a ~30% duty cycle. With `flock -n` that lost
# roughly a third of all scheduled decision turns outright, silently, one log line each.
# The actuator holds it for well under a second; cycle.sh's longest observed hold is ~32s.
# A timeout still fails closed here, on the same path and the same exit code.
mkdir -p "$ROOT/state/.locks" || exit 70
CONTROL_LOCK_WAIT_S="${RECURSION_CONTROL_LOCK_WAIT_S:-120}"
exec 9>>"$ROOT/state/.locks/hermes-control.lock"
flock -w "$CONTROL_LOCK_WAIT_S" 9 \
  || { log "control lock still held after ${CONTROL_LOCK_WAIT_S}s; refusing overlapping planner/sync work"; exit 73; }

# The verbs Hermes may choose. This list is the contract: conduct-hermes.sh refuses anything
# else, so adding a verb here without adding it there is inert, and vice versa.
VERBS="noop plan work conduct publish escalate resolve-esc reap roadmap-add roadmap-new portfolio-add project-topic-bind register note assist-answer pilot-plan-propose pilot-plan-approve pilot-window-open pilot-window-close pilot-task-create pilot-worker-request pilot-verifier-request pilot-block pilot-escalate pilot-goal-verify"

# Invoke the durable identity that owns the oldest open instruction. There is still one planner
# process and one queue; this selects a scoped prompt, not another scheduler or executor.
SELECTED_INSTRUCTION=""; DECIDER_ACTOR="head-hermes"; PILOT_PROJECT=""
for instruction_file in "$ROOT/state/instructions"/*.md; do
  [ -f "$instruction_file" ] || continue
  [ "$(sed -n 's/^status: *//p' "$instruction_file" | head -1)" = open ] || continue
  SELECTED_INSTRUCTION="$instruction_file"
  route="$(sed -n 's/^routing_target: *//p' "$instruction_file" | head -1)"
  case "$route" in
    pilot-*)
      PILOT_PROJECT="$(sed -n 's/^project_id: *//p' "$instruction_file" | head -1)"
      expected="$(python3 - "$ROOT/state/project-config/$PILOT_PROJECT.json" <<'PY' 2>/dev/null
import json,sys
try: print(json.load(open(sys.argv[1],encoding='utf-8')).get('pilot_id',''))
except Exception: print('')
PY
)"
      [ -n "$PILOT_PROJECT" ] && [ "$route" = "$expected" ] \
        || { log "REFUSED - open instruction has an invalid project-pilot binding"; exit 5; }
      DECIDER_ACTOR="$route" ;;
    *) DECIDER_ACTOR="head-hermes" ;;
  esac
  break
done

build_pilot_brief(){
  echo "===== AUTHORITY (project pilot $DECIDER_ACTOR; project $PILOT_PROJECT) ====="
  cat CONTROL_PLANE.md 2>/dev/null || echo "(CONTROL_PLANE.md absent)"
  echo; echo "===== EXACT AUTHENTICATED INSTRUCTION (highest priority) ====="
  [ -n "$SELECTED_INSTRUCTION" ] && head -c 8192 "$SELECTED_INSTRUCTION" || echo "(none)"
  echo; echo "===== PROJECT CHARTER AND LIVE SCOPED STATE ====="
  python3 scripts/project-pilot.py status "$PILOT_PROJECT" 2>/dev/null \
    || echo "(project state is not provable - choose pilot-escalate)"
  echo; echo "===== RUNTIME: PAUSE ====="
  if [ -f state/PAUSE ]; then echo "PAUSED - no worker may run"; cat state/PAUSE
  else echo "not paused"; fi
  echo; echo "===== CAPACITY ====="
  bash scripts/capacity.sh report 2>/dev/null || echo "(capacity unreadable - do not request work)"
}

# --- the state brief: ground truth, re-derived every run ---------------------------------
build_brief(){
  if [ "$DECIDER_ACTOR" != head-hermes ]; then build_pilot_brief; return; fi
  echo "===== AUTHORITY (you are bound by this) ====="
  cat CONTROL_PLANE.md 2>/dev/null || echo "(CONTROL_PLANE.md absent)"
  echo; echo "===== INSTRUCTIONS FROM LUCAS (highest priority — he is the principal) ====="
  # What he actually said, in his words, from the cockpit. These outrank the roadmaps: a roadmap
  # is what was planned, an open instruction is what he wants now.
  # Project-topic instructions are owned by their durable project pilot. Head Hermes sees only
  # explicit head routing (portfolio/policy/cross-project/credentials/production) here.
  if [ -n "$SELECTED_INSTRUCTION" ] && [ "$DECIDER_ACTOR" = head-hermes ]; then
    head -c 8192 "$SELECTED_INSTRUCTION"
  else
    bash scripts/intake.sh open head-hermes 2>/dev/null || echo "(none)"
  fi
  echo; echo "===== SCOPE (ANCHOR) ====="
  cat ANCHOR.md 2>/dev/null || echo "(ANCHOR.md absent)"
  echo; echo "===== DECISIONS (open calls you must honour) ====="
  cat state/DECISIONS.md 2>/dev/null || echo "(DECISIONS.md absent)"
  echo; echo "===== RUNTIME: PAUSE ====="
  if [ -f state/PAUSE ]; then echo "PAUSED — worker dispatch, gates, publication and every"
    echo "other execution verb are halted. Deciding is awareness and continues. These six verbs"
    echo "REMAIN EXECUTABLE while paused and are the only ones that are:"
    echo "  noop  pilot-plan-propose  pilot-plan-approve  pilot-window-open  pilot-window-close"
    echo "  assist-answer"
    echo "So an open Lucas instruction asking for a bounded pilot plan is ANSWERABLE right now:"
    echo "propose the plan. Opening a window while paused arms it; it does not lift PAUSE, and"
    echo "pilot-window-open REQUIRES PAUSE to still be present. For anything else, say what you"
    echo "WOULD do and why, and choose noop."
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

if [ "$DECIDER_ACTOR" = head-hermes ]; then
  ROLE_PROMPT="You are HEAD HERMES, the executive control plane for the Recursion system.
Lucas is the principal. You own portfolio decisions and delegate bounded project work."
else
  MODEL="${RECURSION_PILOT_MODEL:-}"
  [ -n "$MODEL" ] || { log "REFUSED - RECURSION_PILOT_MODEL alias is not configured"; exit 3; }
  ROLE_PROMPT="You are $DECIDER_ACTOR, the persistent logical GPT project pilot for $PILOT_PROJECT.
You may orient, synthesize bounded plans, monitor, and escalate only inside the scoped charter in
your brief. You do not own portfolio policy and you never implement. Emit only noop or a pilot-*
verb, with actor=$DECIDER_ACTOR."
fi

PROMPT="$ROLE_PROMPT

You are NOT an implementer: you never write code and never edit files. You emit ONE decision; a
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

AUTHORING — how an instruction from Lucas becomes work the loop can actually do. These WRITE, so
they are deliberately small: append-only, into state/ only, never code and never a gate. Prose
goes in the "text" field, not in args.
  roadmap-add <ws>              + text: append one plannable checklist item to a roadmap
  roadmap-new <ws> <project>    create a roadmap wired to a registered repo
  portfolio-add <project> <remote>   + text: prepare a PENDING row and bounded charter
  project-topic-bind <project> <topic>   bind an existing Telegram topic while pending
  register <project>            clone + activate a pending row — ONLY if its deploy key exists
  note <project>                + text: append to a project's state file
  assist-answer <task-id>       + text: answer one open assist through the actuator

PROJECT-PILOT PLAN SYNTHESIS - a fresh project instruction becomes a new bounded plan; never
reuse a historical goal merely because it already exists.
  pilot-plan-propose <project> <plan-id> + text and a top-level \"plan\" object.
    THE SCHEMA BELOW IS EXACT. Every key is required, and where alternatives are listed those are
    the ONLY accepted values. Validation happens later, in the actuator, and rejects the plan
    WHOLE -- a near-miss produces nothing anyone will see, so copy the key names literally.

    plan: {\"schema_version\":1, \"id\":\"<the plan-id in your args>\", \"project_id\":\"<project>\",
           \"goal\":{...}, \"tasks\":[ 1..16 of them ]}        serialized under 64 KiB

    goal: {\"id\":\"<a NEW goal id, never one that already exists>\",
           \"outcome\":\"<one line>\", \"falsifier\":\"<one line>\",
           \"acceptance_suite\":\"<a real command; true, :, exit 0 are refused as vacuous>\",
           \"budget\":{\"max_concurrency\":0+, \"max_tokens\":0+, \"max_cost_usd\":0+,
                     \"max_wall_clock_seconds\":0+, \"max_task_attempts\":0+, \"max_failures\":0+,
                     \"max_review_queue\":1+, \"max_publish_attempts\":0+,
                     \"publication_required\":true or false}}
      ALL NINE budget keys are required and are NUMBERS; publication_required is a boolean.
      They are not phase descriptions -- narrative belongs in \"text\".

    task: {\"id\":\"<NEW>\", \"intent\":\"<one line>\",
           \"dependencies\":[ids of OTHER tasks in this plan; may be empty],
           \"allowed_paths\":[paths inside the project charter],
           \"non_goals\":[must contain the literal strings credentials, merge, deploy],
           \"acceptance\":\"<a real command>\",
           \"worker_class\":\"<string>\",
           \"engine\":\"claude\",
           \"model_alias\":\"sonnet-routine\" or \"opus-complex\",
           \"verifier_model_alias\":\"opus-review\" or \"opus-complex\",
           \"deadline_seconds\":1+, \"verifier_deadline_seconds\":1+,
           \"network_policy\":\"provider-only\" or \"none\",
           \"evidence_contract\":\"worker-result-v1\",
           \"verification\":\"independent\",
           \"expected_change\":\"required\" or \"optional\",
           \"gate_files\":[unique paths]}
      The keys are deadline_seconds and verifier_deadline_seconds, NOT \"deadlines\".
      The key is verification with the value \"independent\", NOT \"independent_verification\".
      \"deployment\" is not \"deploy\". model_alias and verifier_model_alias name the ROLE ALIAS,
      never an underlying model: \"claude\", \"codex\", \"sonnet\", \"opus\" are all invalid there.
  pilot-plan-approve <project> <plan-id> <sha256>  materialize only when Lucas's correlated
    instruction itself names that exact plan id and digest.
  pilot-window-open <project> <goal-id> <window-id> <seconds>  admit that exact approved goal;
    Lucas's correlated instruction must name every bound, and PAUSE must still be present.
  pilot-window-close <project> <window-id>  revoke one window. Observing PAUSE also revokes it.
Set "actor" to the project's bound pilot id for pilot-plan-propose and other project-pilot
verbs. Set it to "head-hermes" for approval/window verbs; those additionally require a separate
authenticated Lucas instruction that names the exact object.

You CANNOT provision a deploy key; only Lucas can, on GitHub. 'portfolio-add' prepares a repo and
'register' completes it, and when the key is missing the honest answer is 'escalate' asking him
for one. Never report a repo as ready because you wrote a row about it.

HARD RULES
- If the box is PAUSED, workers, gates, publication, and execution stay forbidden. Safe plan
  proposal, exact approval/window state, assist answers, and noop remain available through their
  explicit verbs; opening a window while PAUSED does not lift PAUSE.
- Never choose work that has no machine-checkable acceptance gate.
- Never choose anything that merges, deploys, spends money, or touches auth/cron/.env/flags.
  Those are Lucas's. If one is needed, choose 'escalate'.
- Prefer 'noop' over inventing work. Generation that outruns review is a liability, not
  progress; an idle box with a clear reason is a good outcome.
- Every execution decision must serve an existing goal. A fresh project objective is the one
  exception: synthesize it with pilot-plan-propose, then wait for a separate exact-digest Lucas
  approval. Never reinterpret or attach it to a historical goal/task shell.
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
- When a decision answers an OPEN INSTRUCTION, copy its exact id into "instruction_id". The
  actuator couples that instruction to the resulting durable action and acknowledges it only
  after success. Never emit a separate "handled" decision.

Reply with reasoning first, then EXACTLY this block and nothing after it:

===DECISION-START===
{\"actor\":\"head-hermes or the exact bound pilot id\",\"verb\":\"...\",\"args\":[\"...\"],\"text\":\"prose, for the authoring verbs only\",\"plan\":\"complete object for pilot-plan-propose only; omit otherwise\",\"instruction_id\":\"exact open instruction id, or omit\",\"project\":\"...\",\"goal\":\"goal-slug-like-this\",\"why\":\"one or two sentences\",\"confidence\":\"high|medium|low\",\"wrong_if\":\"the specific observable that would mean this was the wrong call\"}
===DECISION-END===


'text' is REQUIRED and must be NON-EMPTY for every authoring verb, pilot-plan-propose included.
Omitting it refuses the decision just as surely as malforming it. It is handed to those verbs as
an argument, so it is filtered like a command line. All of the following are enforced:
  - required and non-empty for authoring verbs, at most 500 characters
  - ONE line: no newlines, no control characters
  - may not begin with a '-'
  - none of these characters ANYWHERE:  ;  &  |  <  >
  - no backticks, and no dollar sign immediately followed by an open parenthesis or open brace
  - no Markdown: no leading #, no **bold**, no __underline__, no [label](link)
The character rule catches ordinary punctuation. A semicolon joining two clauses, or a pipe in a
metric name like Sum|per-slot error|, refuses the ENTIRE decision, not just the field. Write
\"and\" instead of a semicolon and name the metric in words. Only 'text' is filtered this way --
'why', 'wrong_if' and the plan object are not.

'goal' and 'wrong_if' are mandatory. A decision that cannot name the goal it serves, or what
would make it wrong, is a guess — choose 'escalate' instead of writing one.

'goal' MUST BE AN IDENTIFIER, never a sentence. It has to match ^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$
- no spaces, no colons, no punctuation beyond . _ and -. Name the existing goal id, or the new
goal id you are proposing. A purpose statement in this field is rejected at normalization and
the whole decision is DISCARDED, silently, so the run reads as if you never decided.
  good: architecture-rebase   goal-gsc-client-reconstruction   goal-pause-safety
  bad:  PAUSE safety: preserve operational awareness while execution remains halted

=================== STATE (ground truth, re-derived this run) ===================
$(build_brief)"

# A malformed reply is retried; nothing else is. Roughly one run in four emitted an unbalanced
# brace in the nested plan object, and with no retry the whole turn was discarded until the next
# cron six hours later. The COST FENCE below stays inside the loop deliberately: each attempt
# proves its own provider and cost, so a metered fallback still refuses on the attempt that
# caused it and is never retried into a second billed call.
DECIDE_ATTEMPTS="${RECURSION_DECIDE_ATTEMPTS:-3}"
case "$DECIDE_ATTEMPTS" in ''|*[!0-9]*) log "invalid RECURSION_DECIDE_ATTEMPTS"; exit 4 ;; esac
[ "$DECIDE_ATTEMPTS" -ge 1 ] || { log "RECURSION_DECIDE_ATTEMPTS must be at least 1"; exit 4; }
DECIDE_ATTEMPT=0
while :; do
DECIDE_ATTEMPT=$((DECIDE_ATTEMPT+1))

log "deciding (model=$MODEL, attempt $DECIDE_ATTEMPT/$DECIDE_ATTEMPTS)"
if ! hermes -z "$PROMPT" -m "$MODEL" --usage-file "$USAGE" >"$OUT" 2>>"$LOG"; then
  log "FAILED — hermes returned non-zero; see $LOG"
  exit 1
fi

# --- COST FENCE: the whole design rests on this staying free. ----------------------------
# A silent fallback to metered OpenRouter is the failure D-008 warned about, and it would make
# an always-on executive quietly expensive. Refuse the decision rather than act on a billed one.
USAGE_FIELDS="$(python3 - "$USAGE" <<'PY'
import json,sys
try:
    value=json.load(open(sys.argv[1],encoding='utf-8'))
    provider=value['provider']
    cost=value['estimated_cost_usd']
    if not isinstance(provider,str) or not provider.strip(): raise ValueError('provider absent')
    if isinstance(cost,bool) or not isinstance(cost,(int,float)) or cost < 0:
        raise ValueError('usage cost absent')
    print(provider+'\t'+str(cost))
except Exception as exc:
    print('usage evidence absent or invalid: '+str(exc),file=sys.stderr)
    raise SystemExit(1)
PY
)"
if [ "$?" -ne 0 ] || [ -z "$USAGE_FIELDS" ]; then
  log "REFUSED - provider/usage evidence is absent or invalid"
  exit 3
fi
PROV="${USAGE_FIELDS%%$'\t'*}"
COST="${USAGE_FIELDS#*$'\t'}"
if [ -n "$PROV" ] && [ "$PROV" != "openai-codex" ]; then
  log "REFUSED — decision ran on '$PROV' (cost=\$$COST), not the flat sub."
  bash scripts/notify.sh "⚠ Recursion: a Hermes DECISION fell back to $PROV (\$$COST). Decision discarded — the executive must stay on the flat sub." || true
  exit 3
fi

# --- extract + validate the decision ------------------------------------------------------
BLOCK="$(awk '/^===DECISION-START===/{f=1;next} /^===DECISION-END===/{f=0} f' "$OUT")"
if [ -z "${BLOCK//[[:space:]]/}" ]; then
  if [ "$DECIDE_ATTEMPT" -lt "$DECIDE_ATTEMPTS" ]; then
    log "no decision block in the reply; retrying"
    continue
  fi
  log "REFUSED — no decision block in the reply after $DECIDE_ATTEMPT attempts"; exit 4
fi

# Validation lives in scripts/validate-decision.py — one definition, exercised directly by
# the test suite. It was inlined here as a heredoc-fed snippet and was SILENTLY BROKEN:
# `python3 - <<PY` consumes stdin for the script, so the piped JSON never arrived and every
# decision was rejected. Passing the payload as an argument removes the stdin ambiguity.
VALID="$(python3 "$ROOT/scripts/validate-decision.py" "$VERBS" "$BLOCK" "$DECIDER_ACTOR" 2>&1)"

case "$VALID" in
  OK\ *) DECISION="${VALID#OK }"; break ;;
esac
# Only a MALFORMED reply is the model's slip to retake. A decision that parsed and was refused on
# its content is a real refusal and must stay terminal, or a retry loop would grind against the
# same objection until the budget runs out.
case "$VALID" in
  *"malformed JSON"*|*"is not an object"*|*"produced no output"*)
    if [ "$DECIDE_ATTEMPT" -lt "$DECIDE_ATTEMPTS" ]; then
      log "malformed decision (${VALID:-no output}); retrying"
      printf '%s\n' "$BLOCK" >>"$LOG"
      continue
    fi
    log "REFUSED — ${VALID:-validation produced no output} after $DECIDE_ATTEMPT attempts"
    printf '%s\n' "$BLOCK" >>"$LOG"; exit 5 ;;
esac
log "REFUSED — ${VALID:-validation produced no output}"; printf '%s\n' "$BLOCK" >>"$LOG"; exit 5
done

# Bind model provenance and the routed authority into the durable record. Deterministic internal
# reconcilers do not carry this marker; the actuator uses it to distinguish a scoped model
# decision from a pilot-attributed internal transition.
DECISION="$(python3 - "$DECISION" "$DECIDER_ACTOR" <<'PY'
import json,sys
row=json.loads(sys.argv[1])
row['decision_source']='hermes-model'
row['routed_decider']=sys.argv[2]
print(json.dumps(row,sort_keys=True,separators=(',',':')))
PY
)" || { log "REFUSED - could not bind routed decision authority"; exit 5; }

VERB="$(printf '%s' "$DECISION" | python3 -c 'import json,sys;print(json.load(sys.stdin)["verb"])')"
log "decision: $VERB — $(printf '%s' "$DECISION" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("why",""))' | cut -c1-120)"

CANONICAL="$(printf '%s' "$DECISION" | python3 "$ROOT/scripts/decision-queue.py" normalize \
  --stamp "$STAMP" --provider "$PROV" --usage-file "$USAGE")" \
  || { log "REFUSED - decision could not be normalized to schema v1"; exit 5; }

[ "$MODE" = "--dry-run" ] && { printf '%s\n' "$CANONICAL"; exit 0; }

# --- record: append-only journal plus durable pending projection; no latest singleton ----
QUEUE_PATH="$(printf '%s' "$CANONICAL" | python3 "$ROOT/scripts/decision-queue.py" enqueue)" \
  || { log "REFUSED - durable decision enqueue failed"; exit 73; }
bash scripts/taskctl.sh event decision "" "$VERB $(printf '%s' "$DECISION" | python3 -c 'import json,sys;print(" ".join(json.load(sys.stdin).get("args",[])))')" >/dev/null 2>&1 || true
# Post the decision where Lucas can see it. This is the ONLY thing scheduling this script does
# to the world: hermes-decide decides and records, and conduct-hermes.sh is the only thing that
# executes. So a cron entry for this file is safe by construction — the supervisor thinks out
# loud, on a schedule, and nothing moves until a human turns actuation on.
if [ -x scripts/notify.sh ] && [ "${RECURSION_DECIDE_QUIET:-0}" != "1" ] \
    && [ "$DECIDER_ACTOR" = head-hermes ] && [[ "$VERB" != pilot-* ]] && [ "$VERB" != assist-answer ]; then
  bash scripts/notify.sh "🧭 Hermes decided: $VERB $(printf '%s' "$DECISION" | python3 -c 'import json,sys;print(" ".join(json.load(sys.stdin).get("args",[])))' 2>/dev/null)
why: $(printf '%s' "$DECISION" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("why",""))' 2>/dev/null)
wrong if: $(printf '%s' "$DECISION" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("wrong_if",""))' 2>/dev/null)
(queued at $QUEUE_PATH; the supervised actuator is the sole execution path)" || true
fi
printf '%s\n' "$CANONICAL"

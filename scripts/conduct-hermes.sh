#!/usr/bin/env bash
# conduct-hermes.sh — execute ONE validated Hermes decision through existing tooling.
#
# This is the actuator half of the split in hermes-decide.sh. Hermes decides in text and
# cannot act; this script acts and cannot decide. Neither half can do the other's job, which
# is what keeps the executive on the flat subscription and out of the implementer's seat.
#
# ★ THE MODEL'S OUTPUT BECOMES PROCESS ARGUMENTS. That is an injection surface, so:
#   - every verb is matched against a fixed case list — there is no computed dispatch;
#   - every argument is re-validated HERE, not trusted from the decision file, because the
#     file can be edited between decide and conduct;
#   - execution uses argv arrays, never eval, never a constructed shell string.
# A decision this script does not recognise does nothing at all.
#
#   conduct-hermes.sh                 execute state/.decision-latest.json
#   conduct-hermes.sh --file <path>   execute a specific decision file
#   conduct-hermes.sh --dry-run       print what would run, execute nothing
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
[ -f .env ] && set -a && . ./.env && set +a

FILE="$ROOT/state/.decision-latest.json"; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --file) FILE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    *) shift ;;
  esac
done
DATE="$(date +%F)"
LOG="$ROOT/loop/logs/$DATE-conduct-hermes.log"; mkdir -p "$(dirname "$LOG")"
log(){ echo "[$(date -Is)] conduct-hermes: $*" | tee -a "$LOG" >&2; }
ev(){ bash scripts/taskctl.sh event "$1" "" "$2" >/dev/null 2>&1 || true; }

[ -f "$FILE" ] || { log "no decision file at $FILE"; exit 2; }

read_field(){ python3 -c 'import json,sys;print(json.load(open(sys.argv[1],encoding="utf-8")).get(sys.argv[2],"") or "")' "$FILE" "$1" 2>/dev/null; }
VERB="$(read_field verb)"; WHY="$(read_field why)"; GOAL="$(read_field goal)"
mapfile -t ARGS < <(python3 -c 'import json,sys
d=json.load(open(sys.argv[1],encoding="utf-8"))
for a in (d.get("args") or []): print(a)' "$FILE" 2>/dev/null)

[ -n "$VERB" ] || { log "decision has no verb"; exit 2; }

# --- re-validate args HERE. The decision file is on disk between decide and conduct, so
# validating only at decide time trusts a file anything could have rewritten. -------------
for a in ${ARGS+"${ARGS[@]}"}; do
  if ! printf '%s' "$a" | grep -qE '^[A-Za-z0-9][A-Za-z0-9._/-]{0,80}$'; then
    log "REFUSED — unsafe argument: $(printf '%s' "$a" | head -c 60)"
    ev decision-refused "unsafe arg for verb=$VERB"; exit 5
  fi
  case "$a" in
    *..*) log "REFUSED — path traversal in argument: $a"; ev decision-refused "traversal"; exit 5 ;;
  esac
done

# --- PAUSE: deciding is awareness, acting is not (D-012). --------------------------------
if [ -f "$ROOT/state/PAUSE" ] && [ "$VERB" != "noop" ]; then
  log "PAUSED — refusing to execute '$VERB'. The decision is recorded; it will not run until resume."
  ev decision-deferred "paused: $VERB"
  exit 0
fi

log "verb=$VERB args=[${ARGS[*]-}] goal=${GOAL:0:60}"
[ -n "$WHY" ] && log "why: ${WHY:0:160}"

run(){ # execute an argv array, or print it under --dry-run
  if [ "$DRY" = "1" ]; then printf '  WOULD RUN:'; printf ' %q' "$@"; printf '\n'; return 0; fi
  "$@"
}

# --- the whitelist. A fixed case list: there is no path from an unrecognised verb to
# execution, and nothing here reaches auth, cron, .env, flags, merges, or deploys. --------
rc=0
case "$VERB" in
  noop)
    log "noop — nothing to run${WHY:+ ($WHY)}" ;;

  reap)
    run bash scripts/taskctl.sh reap; rc=$? ;;

  plan)
    WS="${ARGS[0]:-}"; [ -n "$WS" ] || { log "plan needs a workstream"; exit 2; }
    [ -f "state/roadmaps/$WS.md" ] || { log "REFUSED — no roadmap for workstream '$WS'"; exit 5; }
    run bash scripts/plan.sh "$WS"; rc=$? ;;

  work)
    ID="${ARGS[0]:-}"; [ -n "$ID" ] || { log "work needs a task id"; exit 2; }
    [ -f "state/tasks/$ID.md" ] || { log "REFUSED — no such task: $ID"; exit 5; }
    # The gate is the contract (delegation-design.md): no acceptance command, no autonomy.
    if [ -z "$(sed -n 's/^acceptance: *//p' "state/tasks/$ID.md" | head -1)" ]; then
      log "REFUSED — task $ID has no acceptance gate; it must escalate, not run"; exit 5
    fi
    run bash scripts/work.sh "$ID"; rc=$? ;;

  conduct)
    run bash scripts/conduct.sh; rc=$? ;;

  publish)
    BR="${ARGS[0]:-}"; [ -n "$BR" ] || { log "publish needs a branch"; exit 2; }
    # publish.sh --branch never pushes to a default branch, but refuse obvious defaults here
    # too: two independent checks, because this one is driven by model output.
    case "$BR" in
      main|master|HEAD) log "REFUSED — '$BR' is a default branch; the loop never pushes to it"; exit 5 ;;
    esac
    run bash scripts/publish.sh --branch "$BR"; rc=$? ;;

  escalate)
    KEY="${ARGS[0]:-}"; TITLE="${ARGS[1]:-$KEY}"
    [ -n "$KEY" ] || { log "escalate needs a key"; exit 2; }
    run bash scripts/taskctl.sh esc-record "$KEY" "$TITLE" "${ARGS[2]:-}" "hermes-decision"; rc=$? ;;

  resolve-esc)
    EID="${ARGS[0]:-}"; [ -n "$EID" ] || { log "resolve-esc needs an escalation id"; exit 2; }
    case "$EID" in esc-*) ;; *) log "REFUSED — '$EID' is not an escalation id"; exit 5 ;; esac
    run bash scripts/taskctl.sh esc-resolve "$EID" "closed by Hermes decision: ${WHY:0:120}"; rc=$? ;;

  *)
    log "REFUSED — '$VERB' is not a whitelisted verb. Nothing was executed."
    ev decision-refused "unknown verb: $VERB"
    exit 5 ;;
esac

[ "$DRY" = "1" ] || ev decision-executed "$VERB rc=$rc"
log "done (verb=$VERB rc=$rc)"
exit "$rc"

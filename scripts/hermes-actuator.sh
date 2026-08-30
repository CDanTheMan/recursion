#!/usr/bin/env bash
# Continuously supervised consumer for the durable Head Hermes decision queue.
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
INTERVAL="${RECURSION_ACTUATOR_INTERVAL_S:-2}"
ACTUATOR_SCOPE="${RECURSION_ACTUATOR_SCOPE:-all}"
case "$ACTUATOR_SCOPE" in state|work|all) ;; *) echo "hermes-actuator: invalid scope '$ACTUATOR_SCOPE'" >&2; exit 2;; esac
STOP=0
trap 'STOP=1' INT TERM
log(){ echo "[$(date -Is)] hermes-actuator: $*" >&2; }
refusal_seen=0

cd "$ROOT" || exit 3
log "started; durable queue consumer is supervised"
while [ "$STOP" = 0 ]; do
  if [ -f "$ROOT/state/PAUSE" ]; then
    # PAUSE halts execution, not awareness. It also revokes every Phase 8 window so a later
    # resume cannot replay old human authority. This closes state only; it dispatches nothing.
    if [ "$ACTUATOR_SCOPE" != work ] && [ -x "$ROOT/scripts/project-reconcile.py" ]; then
      RECURSION_ROOT="$ROOT" python3 "$ROOT/scripts/project-reconcile.py" close-paused-windows >/dev/null \
        || log "PAUSE window revocation failed; execution remains paused"
    fi
    # Drain only state-authoring/approval actions that are explicitly safe under PAUSE. Worker,
    # gate, publisher, and notification-delivery decisions remain pending and untouched.
    paused_rc=0
    if [ "$ACTUATOR_SCOPE" != work ]; then
      set +e
      RECURSION_ROOT="$ROOT" bash "$ROOT/scripts/conduct-hermes.sh" --paused-safe --non-work-only >/dev/null 2>&1
      paused_rc=$?
      set -e
    fi
    [ "$paused_rc" = 76 ] || refusal_seen=0
    case "$paused_rc" in
      0|4|75) : ;;
      76)
        # A decision was REFUSED, not deferred. Pending state is intact, but this record will
        # never drain on its own, so the loop must say so instead of looking healthy forever.
        # conduct-hermes tees the specific reason to loop/logs/<date>-conduct-hermes.log.
        if [ "$refusal_seen" = 0 ]; then
          refusal_seen=1
          log "PAUSE-safe queue pass REFUSED a decision (rc=76); pending preserved and NOT draining. Reason: loop/logs/$(date -u +%Y-%m-%d)-conduct-hermes.log"
        fi ;;
      *) refusal_seen=0; log "PAUSE-safe queue pass failed rc=$paused_rc; pending state was preserved" ;;
    esac
    sleep "$INTERVAL" & wait $! 2>/dev/null || true
    continue
  fi
  set +e
  # Phase 6 adds no scheduler process. The existing supervised actuator asks the deterministic
  # reconciler to enqueue at most one idempotent reconcile decision per eligible goal, then
  # drains those decisions through the same queue/action path it already owns.
  if [ "$ACTUATOR_SCOPE" != work ] && [ -x "$ROOT/scripts/project-reconcile.py" ]; then
    RECURSION_ROOT="$ROOT" python3 "$ROOT/scripts/project-reconcile.py" schedule >/dev/null
    schedule_rc=$?
    case "$schedule_rc" in
      0) : ;;
      *) log "goal reconciliation scheduling failed rc=$schedule_rc; no direct execution occurred" ;;
    esac
  fi
  # Phase 7 uses this same supervised loop. The notification scheduler observes append-only
  # events/outbox truth and emits decisions only; delivery and reporting still occur below through
  # the durable queue and sole actuator.
  if [ "$ACTUATOR_SCOPE" != work ] && [ -x "$ROOT/scripts/notification-outbox.py" ]; then
    RECURSION_ROOT="$ROOT" python3 "$ROOT/scripts/notification-outbox.py" schedule >/dev/null
    notification_rc=$?
    case "$notification_rc" in
      0) : ;;
      *) log "notification reconciliation scheduling failed rc=$notification_rc; no direct send occurred" ;;
    esac
  fi
  conduct_args=()
  [ "$ACTUATOR_SCOPE" != state ] || conduct_args+=(--non-work-only)
  [ "$ACTUATOR_SCOPE" != work ] || conduct_args+=(--work-only)
  RECURSION_ROOT="$ROOT" bash "$ROOT/scripts/conduct-hermes.sh" "${conduct_args[@]}"
  rc=$?
  set -e
  case "$rc" in
    0|4|73|75) : ;;
    *) log "queue pass failed rc=$rc; pending state was preserved" ;;
  esac
  sleep "$INTERVAL" & wait $! 2>/dev/null || true
done
log "stopped"

#!/usr/bin/env bash
# notify.sh — send to Telegram, into the RIGHT forum topic.
#
# Everything used to land in one stream, so a GSC gate result, a chiron build and a portfolio
# escalation were interleaved in the order they happened and had to be told apart by reading
# them. The Cockpit (-100…) is a forum, so each project gets a topic and each message goes to
# the topic that owns it. Routing is the whole feature: a cockpit whose messages all arrive in
# one channel is the thing it replaces.
#
# Usage:
#   notify.sh "message"                      -> home topic
#   notify.sh --project <name|repo-path> "…" -> that project's topic (registry lookup)
#   notify.sh --thread <id> "…"              -> an explicit thread
#   notify.sh [--project …] -f /path/to/file -> body from a file
#
# ★ THE TOKEN NEVER LEAVES THIS FILE. It is only ever interpolated into a URL held in a local
# variable, never echoed, never logged, never put in an error message, and no `set -x` may run
# with it in scope. curl's own errors can include the URL it was given, so stderr from the token
# path is discarded and a redacted line is printed instead. scripts/tests/telegram-routing.test.sh
# runs this file with a sentinel token and greps EVERYTHING it emits for it.
set -euo pipefail

# ★ THE FIXTURE-LEAK GUARD, and it is load-bearing. Tests run the REAL notify.sh against
# disposable roots, and `hermes send` uses the GATEWAY's credentials (~/.hermes), not this repo's
# .env — so a fixture with an empty .env does NOT stop delivery. Every escalation a test fixture
# raised went to Lucas for real. Observed 2026-08-06: two live pings about repos named "diverged"
# and "unreachable", which are resync.test.sh fixtures, indistinguishable in the notification
# from a genuine portfolio failure. work.sh honoured RECURSION_NO_NOTIFY in its own wrapper;
# every script that calls notify.sh directly (resync.sh, assist.sh, taskctl.sh) did not, and the
# guard has to live HERE because this is the one place they all pass through.
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
[ -f "$ROOT/.env" ] && { set -a; . "$ROOT/.env"; set +a; }

PROJECT=""; THREAD=""; FILE=""; MSG=""; DESTINATION=""; DELIVERY_ID=""; EVENT_ID=""
ATTEMPT_TOKEN=""; MESSAGE_DIGEST=""; EVIDENCE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --project) PROJECT="${2:-}"; shift 2 ;;
    --thread)  THREAD="${2:-}";  shift 2 ;;
    --destination) DESTINATION="${2:-}"; shift 2 ;;
    --delivery-id) DELIVERY_ID="${2:-}"; shift 2 ;;
    --event-id) EVENT_ID="${2:-}"; shift 2 ;;
    --attempt-token) ATTEMPT_TOKEN="${2:-}"; shift 2 ;;
    --message-digest) MESSAGE_DIGEST="${2:-}"; shift 2 ;;
    --evidence) EVIDENCE="${2:-}"; shift 2 ;;
    -f)        FILE="${2:-}";    shift 2 ;;
    *)         MSG="$1";         shift   ;;
  esac
done

# Phase 7 durable mode. This is still the sole sender: the outbox calls notify.sh with an exact
# configured destination and requires a transport acknowledgement carrying a Telegram message id.
# A zero exit from a process, prose saying "sent", or a model claim is not delivery evidence.
if [ -n "$DESTINATION" ]; then
  [ "${RECURSION_NO_NOTIFY:-0}" != "1" ] || exit 12
  [ -n "$DELIVERY_ID" ] && [ -n "$EVENT_ID" ] && [ -n "$ATTEMPT_TOKEN" ] \
    && [ -n "$MESSAGE_DIGEST" ] && [ -n "$EVIDENCE" ] || exit 12
  case "$DELIVERY_ID:$EVENT_ID:$ATTEMPT_TOKEN" in
    *[!A-Za-z0-9._:-]*|*..*) exit 12 ;;
  esac
  if [ -n "$FILE" ]; then MSG="$(head -c 3800 "$FILE")"; fi
  MSG="$(printf '%s' "$MSG" | head -c 3800)"
  IFS=: read -r DEST_KIND DEST_TRANSPORT DEST_CHAT DEST_THREAD DEST_EXTRA <<EOF
$DESTINATION
EOF
  case "$DEST_KIND:$DEST_TRANSPORT" in
    project-topic:telegram|head-hermes:telegram|lucas-direct:telegram|portfolio-account:telegram|portfolio-channel:telegram) : ;;
    *) exit 12 ;;
  esac
  printf '%s' "$DEST_CHAT" | grep -qE '^-?[1-9][0-9]*$' || exit 12
  [ -z "${DEST_EXTRA:-}" ] || exit 12
  case "$DEST_KIND" in
    project-topic|head-hermes|portfolio-channel)
      printf '%s' "${DEST_THREAD:-}" | grep -qE '^[1-9][0-9]*$' || exit 12 ;;
    lucas-direct|portfolio-account)
      [ -z "${DEST_THREAD:-}" ] || exit 12 ;;
  esac
  [ "$DEST_KIND" != lucas-direct ] || case "$DEST_CHAT" in -*) exit 12 ;; esac

  RESPONSE=""; TRANSPORT_RC=0
  if [ -n "${RECURSION_NOTIFY_TRANSPORT:-}" ]; then
    set +e
    RESPONSE="$("$RECURSION_NOTIFY_TRANSPORT" "$DESTINATION" "$MSG" "$DELIVERY_ID" "$EVENT_ID" 2>/dev/null)"
    TRANSPORT_RC=$?
    set -e
    [ "$TRANSPORT_RC" -eq 0 ] || exit 12
  else
    [ -n "${TELEGRAM_BOT_TOKEN:-}" ] || exit 11
    set +x
    set +e
    RESPONSE="$(curl -sS --max-time "${RECURSION_NOTIFY_TIMEOUT_S:-20}" \
      -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="$DEST_CHAT" ${DEST_THREAD:+-d message_thread_id="$DEST_THREAD"} \
      --data-urlencode text="$MSG" 2>/dev/null)"
    TRANSPORT_RC=$?
    set -e
    [ "$TRANSPORT_RC" -eq 0 ] || exit 12
  fi

  TRANSPORT_RESPONSE="$RESPONSE" DESTINATION="$DESTINATION" DEST_CHAT="$DEST_CHAT" \
  DEST_THREAD="${DEST_THREAD:-}" DELIVERY_ID="$DELIVERY_ID" EVENT_ID="$EVENT_ID" \
  ATTEMPT_TOKEN="$ATTEMPT_TOKEN" MESSAGE_DIGEST="$MESSAGE_DIGEST" \
  python3 - "$EVIDENCE" <<'PY'
import hashlib,json,os,sys,tempfile,time
path=sys.argv[1]
try: raw=json.loads(os.environ.get('TRANSPORT_RESPONSE',''))
except Exception: raise SystemExit(12)
if not isinstance(raw,dict): raise SystemExit(12)
if raw.get('accepted') is False or raw.get('ok') is False:
    raise SystemExit(10 if raw.get('retryable') is True else 11)
result=raw.get('result') if isinstance(raw.get('result'),dict) else raw
chat=result.get('chat') if isinstance(result.get('chat'),dict) else {}
message_id=result.get('message_id')
chat_id=result.get('chat_id',chat.get('id'))
thread_id=result.get('thread_id',result.get('message_thread_id'))
transport=result.get('transport',raw.get('transport','telegram'))
expected_chat=os.environ['DEST_CHAT']; expected_thread=os.environ.get('DEST_THREAD') or None
if raw.get('ok') is not True or raw.get('accepted',True) is not True or transport!='telegram' or message_id in (None,''):
    raise SystemExit(12)
if str(chat_id)!=expected_chat or (str(thread_id) if thread_id not in (None,'') else None)!=expected_thread:
    raise SystemExit(12)
value={'schema_version':1,'delivery_id':os.environ['DELIVERY_ID'],'event_id':os.environ['EVENT_ID'],
       'destination':os.environ['DESTINATION'],'attempt_token':os.environ['ATTEMPT_TOKEN'],
       'message_digest':os.environ['MESSAGE_DIGEST'],'transport':'telegram','accepted':True,
       'message_id':str(message_id),'chat_id':str(chat_id),'thread_id':expected_thread,
       'acknowledged_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
       'transport_response_digest':hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
directory=os.path.dirname(path); os.makedirs(directory,exist_ok=True)
fd,tmp=tempfile.mkstemp(prefix='.'+os.path.basename(path)+'.tmp.',dir=directory)
try:
    os.fchmod(fd,0o600)
    with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as out:
        json.dump(value,out,sort_keys=True,separators=(',',':')); out.write('\n'); out.flush(); os.fsync(out.fileno())
    os.replace(tmp,path)
    dfd=os.open(directory,os.O_RDONLY)
    try: os.fsync(dfd)
    finally: os.close(dfd)
except BaseException:
    try: os.unlink(tmp)
    except FileNotFoundError: pass
    raise
PY
  exit $?
fi

[ "${RECURSION_NO_NOTIFY:-0}" = "1" ] && exit 0

# The cockpit chat. RECURSION_TELEGRAM_CHAT is the forum supergroup; TELEGRAM_CHAT_ID stays the
# fallback so nothing that worked before this change stops working.
CHAT="${RECURSION_TELEGRAM_CHAT:-${TELEGRAM_CHAT_ID:-}}"
HOME_THREAD="${RECURSION_TELEGRAM_HOME_THREAD:-}"
REG="${RECURSION_PORTFOLIO:-$ROOT/state/portfolio.tsv}"

# --- resolve the topic --------------------------------------------------------------------
# A project with no topic yet routes HOME rather than to a malformed target. Silently dropping
# the message would be the worst option available: the alert exists to be seen.
if [ -z "$THREAD" ] && [ -n "$PROJECT" ] && [ -f "$REG" ]; then
  THREAD="$(awk -F'\t' -v q="$PROJECT" '$1 !~ /^#/ && NF>=8 && ($1==q || $2==q) {print $7; exit}' "$REG")"
  [ "$THREAD" = "-" ] && THREAD=""
fi
[ -z "$THREAD" ] && THREAD="$HOME_THREAD"

# --- preferred path: hermes send (reuses the gateway's creds; no LLM, no token here at all) ---
if command -v hermes >/dev/null 2>&1; then
  TARGET="telegram"
  if [ -n "$CHAT" ]; then
    TARGET="telegram:$CHAT"
    [ -n "$THREAD" ] && TARGET="telegram:$CHAT:$THREAD"
  fi
  if [ -n "$FILE" ]; then
    hermes send -t "$TARGET" -f "$FILE" -q && exit 0 || true
  else
    hermes send -t "$TARGET" "$MSG" -q && exit 0 || true
  fi
fi

# --- fallback: raw Telegram API ---------------------------------------------------------------
[ -z "${TELEGRAM_BOT_TOKEN:-}" ] && exit 0
[ -z "$CHAT" ] && exit 0
if [ -n "$FILE" ]; then MSG="$(head -c 3800 "$FILE")"; fi

# message_thread_id is what puts a message in a forum topic; without it every message lands in
# the group's General topic, which is the un-routed behaviour this file exists to replace.
set +x
if ! curl -sS -o /dev/null \
      -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="$CHAT" \
      ${THREAD:+-d message_thread_id="$THREAD"} \
      --data-urlencode text="$MSG" 2>/dev/null; then
  # Never print curl's error: it echoes the URL it was handed, and the URL carries the token.
  echo "notify: telegram send failed (chat=$CHAT thread=${THREAD:-home})" >&2
fi
exit 0

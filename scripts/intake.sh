#!/usr/bin/env bash
# intake.sh — the inbound half of the cockpit: what Lucas SAYS becomes durable state.
#
# Until now Telegram was one-directional. notify.sh could page him; nothing could hear him back.
# So every instruction — "set up this project", "deprioritise that", "yes, do it" — had to be
# typed into a session like this one, which makes the human the transport and means Hermes can
# only ever choose among work someone else wrote down.
#
# ★ WHY IT DOES NOT POLL TELEGRAM. A hermes gateway is already running `gateway run` and
# long-polling getUpdates on this bot token. Telegram deletes an update once a consumer confirms
# it, so TWO pollers steal from each other: some messages would reach the gateway, some would
# reach us, nondeterministically, and the rest would vanish. That is unrecoverable and silent —
# the worst shape of bug this system has. Verified before building: our own getUpdates returned
# 0 updates with pending=0, because the gateway had already taken them.
#
# The gateway persists what it receives, so intake READS that store instead of competing for it:
#   ~/.hermes/state.db  messages(role,content,timestamp) JOIN sessions(source,chat_id,thread_id,user_id)
# Read-only, no second bot, no metered call, nothing taken away from the gateway.
#
# ★ AND THE TRAP INSIDE THAT TABLE: most role='user' rows are NOT from a human. The heartbeat,
# the daily brief and hermes-decide all write their prompts there with source='cli', and
# subagents with source='subagent'. Ingesting those would feed the system its own output back as
# instructions from Lucas — a loop that reads as him becoming very talkative. Only
# source='telegram' from an ALLOWED user id is intake.
#
# ★ INTAKE IS NOT A COMMAND CHANNEL. A message becomes a durable INSTRUCTION that Hermes reads
# in its brief and must act on or escalate; the actuator whitelist still governs what may run.
# There is no executable shortcut, including for assist answers. Every authenticated message is
# durable input; only a schema-checked Head Hermes decision and the sole actuator may change state.
#
#   intake.sh poll [--dry-run] [--backfill]   ingest new messages; advance the watermark
#                                (a first run SEEDS the watermark; --backfill takes history too)
#   intake.sh list [n]           the most recent instructions
#   intake.sh open               instructions not yet acknowledged
#   intake.sh consume <id> <action-id>...      couple consumption to durable actions
#   intake.sh acknowledge <id> <action-id>...  close only when those actions succeeded
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT" 2>/dev/null || { echo "intake: RECURSION_ROOT '$ROOT' is not a directory" >&2; exit 3; }
[ -f .env ] && { set -a; . ./.env; set +a; }

DB="${RECURSION_HERMES_DB:-$HOME/.hermes/state.db}"
DIR="$ROOT/state/instructions"; mkdir -p "$DIR"
MARK="$ROOT/state/.intake-watermark"
REG="${RECURSION_PORTFOLIO:-$ROOT/state/portfolio.tsv}"
ALLOW="${RECURSION_INTAKE_ALLOW:-8913126684}"     # Lucas. A chat is not an authorisation.
CMD="${1:-poll}"; shift 2>/dev/null || true
now(){ date -u +%FT%TZ; }

atomic_instruction_transition(){ # file status action_csv note
  local file="$1" status="$2" actions="$3" note="$4" d b tmp rc
  [ ! -d "$ROOT/state/.locks/runtime-state.lock" ] \
    || { echo "intake: runtime-state maintenance in progress; refusing concurrent update" >&2; return 73; }
  d="$(dirname "$file")"; b="$(basename "$file")"
  tmp="$(mktemp "$d/.${b}.tmp.XXXXXX")" || return 70
  cp -p -- "$file" "$tmp" || { rm -f -- "$tmp"; return 70; }
  python3 - "$tmp" "$status" "$actions" "$note" "$(now)" <<'PY'
import os,sys
path,status,actions,note,stamp=sys.argv[1:6]
lines=open(path,encoding='utf-8',errors='surrogateescape').read().split('\n')
updates={'schema_version':'1','status':status,'action_ids':actions}
for key,value in updates.items():
    hit=False
    for i,line in enumerate(lines):
        if line.startswith(key+':'): lines[i]=key+': '+value; hit=True; break
    if not hit:
        for i,line in enumerate(lines):
            if line.strip()=='': lines.insert(i,key+': '+value); hit=True; break
    if not hit: lines.append(key+': '+value)
lines.extend(['','## '+status.upper()+' '+stamp,note])
with open(path,'w',encoding='utf-8',errors='surrogateescape',newline='\n') as out:
    out.write('\n'.join(lines)); out.flush(); os.fsync(out.fileno())
PY
  rc=$?
  if [ "$rc" -ne 0 ]; then rm -f -- "$tmp"; return "$rc"; fi
  mv -f -- "$tmp" "$file" || { rm -f -- "$tmp"; return 71; }
  python3 - "$d" <<'PY' >/dev/null 2>&1 || return 72
import os,sys
fd=os.open(sys.argv[1],os.O_RDONLY)
try: os.fsync(fd)
finally: os.close(fd)
PY
}

coupled_actions(){ # instruction id required_status action ids...
  local iid="$1" required="$2" aid file owner status csv=""
  shift 2
  [ "$#" -gt 0 ] || { echo "intake: at least one resulting action id is required" >&2; return 2; }
  for aid in "$@"; do
    printf '%s' "$aid" | grep -qE '^action-[0-9a-f]{24}$' \
      || { echo "intake: invalid action id: $aid" >&2; return 2; }
    file="$ROOT/state/actions/$aid.json"; [ -f "$file" ] \
      || { echo "intake: no durable action $aid" >&2; return 2; }
    read -r owner status < <(python3 - "$file" <<'PY'
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
print(d.get('instruction_id') or '-',d.get('status') or '-')
PY
)
    [ "$owner" = "$iid" ] \
      || { echo "intake: action $aid is not coupled to instruction $iid" >&2; return 2; }
    if [ "$required" = succeeded ] && [ "$status" != succeeded ]; then
      echo "intake: action $aid is $status, not succeeded" >&2; return 2
    fi
    csv="${csv:+$csv,}$aid"
  done
  printf '%s' "$csv"
}

case "$CMD" in

poll)
  DRY=0; BACKFILL=0
  for a in "$@"; do case "$a" in --dry-run) DRY=1 ;; --backfill) BACKFILL=1 ;; esac; done
  [ -f "$DB" ] || { echo "intake: no gateway store at $DB — nothing to read"; exit 0; }
  [ -f "$MARK" ] || echo 0 > "$MARK"
  LAST="$(cat "$MARK" 2>/dev/null || echo 0)"; case "$LAST" in ''|*[!0-9]*) LAST=0 ;; esac

  # The watermark advances only over messages actually written out, so a crash mid-batch
  # re-reads rather than skips. Losing an instruction silently is the failure that matters;
  # seeing one twice is merely untidy, and the filename is keyed by message id so a repeat
  # overwrites rather than duplicates.
  TMPOUT="$(mktemp)"; trap 'rm -f "$TMPOUT"' EXIT
  python3 - "$DB" "$LAST" "$ALLOW" "$DIR" "$REG" "$DRY" "$(now)" "$BACKFILL" >"$TMPOUT" <<'PY'
import io, json, os, re, sqlite3, sys, shutil, tempfile

db, last, allow, outdir, reg, dry, stamp, backfill = sys.argv[1:9]
last = int(last); dry = dry == "1"; backfill = backfill == "1"
allowed = set(x for x in allow.replace(",", " ").split() if x)

def connect(path):
    # The gateway holds this in WAL mode. Read-only is enough and never blocks it; if the
    # reader cannot attach (a -shm it may not create), fall back to a snapshot copy rather
    # than opening read-write and risking the gateway's own state.
    try:
        c = sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=5)
        c.execute("select count(*) from sqlite_master").fetchone()
        return c, None
    except Exception:
        tmp = tempfile.mkdtemp(prefix="intake-")
        for suf in ("", "-wal", "-shm"):
            if os.path.exists(path + suf):
                shutil.copy2(path + suf, os.path.join(tmp, os.path.basename(path) + suf))
        return sqlite3.connect(os.path.join(tmp, os.path.basename(path)), timeout=5), tmp

conn, tmp = connect(db)

# Thread id -> durable project pilot. The Telegram session history is a cache; these files are
# the authority for which logical pilot, memory namespace, and project own a topic.
topics = {}
project_ids = []
try:
    for line in io.open(reg, encoding="utf-8", newline="").read().split("\n"):
        c = line.split("\t")
        if len(c) >= 8 and not c[0].startswith("#") and c[6] not in ("-", ""):
            project_ids.append(c[0])
            binding = {"project": c[0], "pilot_id": "", "memory_key": ""}
            try:
                state = os.path.dirname(outdir)
                cfg = json.load(io.open(os.path.join(state, "project-config", c[0]+".json"), encoding="utf-8"))
                pilot = json.load(io.open(os.path.join(state, "pilots", cfg["pilot_id"]+".json"), encoding="utf-8"))
                if (c[7] == "active" and cfg.get("status") == "active" and pilot.get("status") == "active"
                        and str(cfg.get("topic")) == c[6] and str(pilot.get("topic")) == c[6]):
                    binding.update(pilot_id=pilot["id"], memory_key=pilot["memory_key"])
            except Exception:
                pass
            topics[c[6]] = binding
except Exception:
    pass

def route_for(body, binding):
    if not binding or not binding.get("pilot_id"):
        return "head-hermes"
    # Project pilots do not own portfolio/policy, credentials, production, PAUSE, model routing,
    # or another project's priority. Conservative forwarding is safer than a local guess.
    if re.search(r"\b(portfolio|priorit\w*|policy|spend\w*|credential\w*|deploy\w*|merge\w*|pause|resume|cron|model\s+policy|control\s+plane|deploy\s+key)\b", body, re.I):
        return "head-hermes"
    current = binding["project"]
    for other in project_ids:
        if other != current and re.search(r"(?<![A-Za-z0-9_-])"+re.escape(other)+r"(?![A-Za-z0-9_-])", body, re.I):
            return "head-hermes"
    return binding["pilot_id"]

rows = list(conn.execute("""
    select m.id, m.content, m.timestamp, s.chat_id, s.thread_id, s.user_id, s.source
      from messages m join sessions s on s.id = m.session_id
     where m.role = 'user' and s.source = 'telegram' and m.id > ?
     order by m.id asc
""", (last,)))

# ★ FIRST RUN SEEDS, IT DOES NOT BACKFILL. The gateway store predates intake by days, and
# ingesting that history would place stale DMs in front of Hermes as instructions to act on now —
# old context wearing a current timestamp. Seed the watermark to the present and say what was
# skipped; `--backfill` is there when the history is actually wanted.
if last == 0 and not backfill:
    high = max([r[0] for r in rows], default=0)
    sys.stderr.write("intake: FIRST RUN — seeding the watermark at %d, skipping %d historical "
                     "message(s). Use --backfill to ingest them.\n" % (high, len(rows)))
    print("__WATERMARK__%d" % high)
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    raise SystemExit(0)

written, skipped, high = 0, 0, last
for mid, content, ts, chat, thread, uid, source in rows:
    high = max(high, mid)
    if str(uid) not in allowed:
        skipped += 1
        continue
    text = (content or "").strip()
    if not text:
        skipped += 1
        continue
    # ★ ORDER MATTERS HERE. The gateway's own async-delivery notices arrive as user messages
    # shaped "[ASYNC DELEGATION BATCH COMPLETE - deleg_x]\n...", and the display-name strip below
    # happily ate that bracket, after which the marker check found nothing. Message 275 sailed
    # straight through the dry run. So: system markers are tested on the RAW text, first.
    if re.match(r"^\[(ASYNC|SYSTEM|AUTO)\b", text):
        skipped += 1
        continue
    # Only strip a leading bracket that actually looks like a sender name: a few words, no
    # SHOUTING marker. A greedy strip is what caused the bug above.
    body = re.sub(r"^\[[A-Za-z][A-Za-z .'-]{0,40}\]\s*", "", text)
    binding = topics.get(str(thread or ""), {})
    project = binding.get("project", "")
    pilot_id = binding.get("pilot_id", "")
    memory_key = binding.get("memory_key", "")
    routing_target = route_for(body, binding)
    if dry:
        print("WOULD ingest %s thread=%s project=%s %r" % (mid, thread, project or "-", body[:70]))
        written += 1
        continue
    path = os.path.join(outdir, "%08d.md" % mid)
    tmppath = path + ".tmp.%d" % os.getpid()
    with io.open(tmppath, "w", encoding="utf-8", newline="\n") as output:
        correlation = "telegram:%s:%s:%s" % (chat, thread or "root", mid)
        output.write(
            "schema_version: 1\nid: %d\nreceived: %s\nprincipal: %s\ntopic: %s\n"
            "project_id: %s\npilot_id: %s\npilot_memory_key: %s\nrouting_target: %s\n"
            "reply_correlation: %s\ndeduplication_key: %s\n"
            "from: %s\nchat: %s\nthread: %s\nproject: %s\nstatus: open\n"
            "action_ids: \n\n## INSTRUCTION\n%s\n" %
            (mid, stamp, uid, thread or "-", project or "", pilot_id, memory_key, routing_target,
             correlation, correlation,
             uid, chat, thread or "-", project or "-", body))
        output.flush(); os.fsync(output.fileno())
    os.replace(tmppath, path)
    dfd = os.open(outdir, os.O_RDONLY)
    try: os.fsync(dfd)
    finally: os.close(dfd)
    print("INGESTED %d project=%s %r" % (mid, project or "-", body[:70]))
    written += 1

if tmp:
    shutil.rmtree(tmp, ignore_errors=True)
sys.stderr.write("intake: %d ingested, %d skipped, watermark %d -> %d\n" % (written, skipped, last, high))
print("__WATERMARK__%d" % high)
PY
  rc=$?
  [ "$rc" -eq 0 ] || { echo "intake: reader failed (rc=$rc)" >&2; exit "$rc"; }

  # The reader's last line carries the high-water mark; everything else is the report.
  WM="$(grep '^__WATERMARK__' "$TMPOUT" | tail -1 | sed 's/^__WATERMARK__//')"
  grep -v '^__WATERMARK__' "$TMPOUT" || true
  if [ "$DRY" = "0" ] && [ -n "$WM" ]; then
    mark_tmp="$(mktemp "$(dirname "$MARK")/.$(basename "$MARK").tmp.XXXXXX")" || exit 70
    printf '%s\n' "$WM" > "$mark_tmp" && mv -f -- "$mark_tmp" "$MARK" || exit 71
    python3 - "$(dirname "$MARK")" <<'PY' >/dev/null 2>&1 || exit 72
import os,sys
fd=os.open(sys.argv[1],os.O_RDONLY)
try: os.fsync(fd)
finally: os.close(fd)
PY
  fi

  # Message text never executes here. An assist answer is another durable instruction; the
  # planner may emit assist-answer and the actuator will couple it to the resulting action.
  # A quiet poll is a SUCCESS. Without this the trailing grep-for-ingested-lines finds nothing,
  # its exit status becomes the script's, and cycle.sh logs "intake failed" on every normal
  # cycle — an error message that means "nothing happened", which is how real errors get ignored.
  true
  ;;

list) n="${1:-10}"; ls -1 "$DIR"/*.md 2>/dev/null | tail -"$n" | while read -r f; do
        project="$(sed -n 's/^project_id: *//p' "$f" | head -1)"; [ -n "$project" ] || project="$(sed -n 's/^project: *//p' "$f" | head -1)"
        printf '%-10s %-26s %s\n' "$(sed -n 's/^id: *//p' "$f")" "$project" \
          "$(awk '/^## INSTRUCTION/{f=1;next} f' "$f" | tr '\n' ' ' | cut -c1-80)"; done
      [ -n "$(ls -A "$DIR" 2>/dev/null)" ] || echo "(no instructions yet)" ;;

open) found=0; TARGET="${1:-}"
      for f in "$DIR"/*.md; do [ -f "$f" ] || continue
        [ "$(sed -n 's/^status: *//p' "$f" | head -1)" = "open" ] || continue
        if [ -n "$TARGET" ]; then
          route="$(sed -n 's/^routing_target: *//p' "$f" | head -1)"
          [ "${route:-head-hermes}" = "$TARGET" ] || continue
        fi
        found=1
        project="$(sed -n 's/^project_id: *//p' "$f" | head -1)"; [ -n "$project" ] || project="$(sed -n 's/^project: *//p' "$f" | head -1)"
        printf '%-10s %-26s %s\n' "$(sed -n 's/^id: *//p' "$f")" "$project" \
          "$(awk '/^## INSTRUCTION/{f=1;next} f' "$f" | tr '\n' ' ' | cut -c1-80)"; done
      [ "$found" = "1" ] || echo "(no open instructions)" ;;

handled) echo "intake: handled is forbidden; acknowledge a coupled succeeded action" >&2; exit 2 ;;

consume) ID="${1:?usage: intake.sh consume <id> <action-id>...}"; shift
      F="$DIR/$(printf '%08d' "$ID").md"
      [ -f "$F" ] || { echo "intake: no instruction $ID" >&2; exit 2; }
      ACTIONS="$(coupled_actions "$ID" any "$@")" || exit $?
      atomic_instruction_transition "$F" consumed "$ACTIONS" "resulting actions: $ACTIONS" || exit $?
      echo "consumed $ID -> $ACTIONS" ;;

acknowledge) ID="${1:?usage: intake.sh acknowledge <id> <action-id>...}"; shift
      F="$DIR/$(printf '%08d' "$ID").md"
      [ -f "$F" ] || { echo "intake: no instruction $ID" >&2; exit 2; }
      [ "$(sed -n 's/^status: *//p' "$F" | head -1)" = consumed ] \
        || { echo "intake: instruction $ID is not consumed" >&2; exit 2; }
      ACTIONS="$(coupled_actions "$ID" succeeded "$@")" || exit $?
      atomic_instruction_transition "$F" acknowledged "$ACTIONS" "succeeded actions: $ACTIONS" || exit $?
      echo "acknowledged $ID -> $ACTIONS" ;;

*) sed -n '30,34p' "$0"; exit 2 ;;
esac

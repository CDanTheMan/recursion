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
# The single exception is answering an assist, because that is Lucas answering a question the
# system asked him, and it can only requeue one task (see scripts/assist.sh).
#
#   intake.sh poll [--dry-run] [--backfill]   ingest new messages; advance the watermark
#                                (a first run SEEDS the watermark; --backfill takes history too)
#   intake.sh list [n]           the most recent instructions
#   intake.sh open               instructions not yet marked handled
#   intake.sh handled <id> [why] mark one handled (Hermes acts through the actuator, then this)
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
import io, os, re, sqlite3, sys, shutil, tempfile

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

# thread id -> project, so an instruction typed in a project's topic is ABOUT that project.
topics = {}
try:
    for line in io.open(reg, encoding="utf-8", newline="").read().split("\n"):
        c = line.split("\t")
        if len(c) >= 8 and not c[0].startswith("#") and c[6] not in ("-", ""):
            topics[c[6]] = c[0]
except Exception:
    pass

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
    project = topics.get(str(thread or ""), "")
    if dry:
        print("WOULD ingest %s thread=%s project=%s %r" % (mid, thread, project or "-", body[:70]))
        written += 1
        continue
    path = os.path.join(outdir, "%08d.md" % mid)
    io.open(path, "w", encoding="utf-8", newline="\n").write(
        "id: %d\nreceived: %s\nfrom: %s\nchat: %s\nthread: %s\nproject: %s\nstatus: open\n\n"
        "## INSTRUCTION\n%s\n" % (mid, stamp, uid, chat, thread or "-", project or "-", body))
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
  if [ "$DRY" = "0" ] && [ -n "$WM" ]; then printf '%s\n' "$WM" > "$MARK"; fi

  # ONE executable shortcut, and only one: Lucas answering a question the system asked him.
  # `assist <task-id> <text>` is the human half of scripts/assist.sh — it can requeue exactly the
  # task that asked, and nothing else. Every other message stays inert until Hermes decides on it
  # through the actuator whitelist, because a chat line must never become a command.
  if [ "$DRY" = "0" ] && [ -x "$ROOT/scripts/assist.sh" ]; then
    grep '^INGESTED ' "$TMPOUT" | sed 's/^INGESTED \([0-9]*\) .*/\1/' | while read -r mid; do
      f="$DIR/$(printf '%08d' "$mid").md"
      [ -f "$f" ] || continue
      body="$(awk '/^## INSTRUCTION/{f=1;next} f' "$f" | head -1)"
      case "$body" in
        assist\ *)
          tid="$(printf '%s' "$body" | awk '{print $2}')"
          ans="$(printf '%s' "$body" | cut -d' ' -f3-)"
          if [ -n "$tid" ] && [ -n "${ans//[[:space:]]/}" ]; then
            if RECURSION_ROOT="$ROOT" bash "$ROOT/scripts/assist.sh" answer "$tid" "$ans" >/dev/null 2>&1; then
              RECURSION_ROOT="$ROOT" bash "$0" handled "$mid" "answered assist $tid" >/dev/null
              echo "  -> answered assist $tid from instruction $mid"
            fi
          fi ;;
      esac
    done
  fi
  # A quiet poll is a SUCCESS. Without this the trailing grep-for-ingested-lines finds nothing,
  # its exit status becomes the script's, and cycle.sh logs "intake failed" on every normal
  # cycle — an error message that means "nothing happened", which is how real errors get ignored.
  true
  ;;

list) n="${1:-10}"; ls -1 "$DIR"/*.md 2>/dev/null | tail -"$n" | while read -r f; do
        printf '%-10s %-26s %s\n' "$(sed -n 's/^id: *//p' "$f")" "$(sed -n 's/^project: *//p' "$f")" \
          "$(awk '/^## INSTRUCTION/{f=1;next} f' "$f" | tr '\n' ' ' | cut -c1-80)"; done
      [ -n "$(ls -A "$DIR" 2>/dev/null)" ] || echo "(no instructions yet)" ;;

open) found=0
      for f in "$DIR"/*.md; do [ -f "$f" ] || continue
        [ "$(sed -n 's/^status: *//p' "$f" | head -1)" = "open" ] || continue
        found=1
        printf '%-10s %-26s %s\n' "$(sed -n 's/^id: *//p' "$f")" "$(sed -n 's/^project: *//p' "$f")" \
          "$(awk '/^## INSTRUCTION/{f=1;next} f' "$f" | tr '\n' ' ' | cut -c1-80)"; done
      [ "$found" = "1" ] || echo "(no open instructions)" ;;

handled) ID="${1:?usage: intake.sh handled <id> [why]}"; shift; WHY="${*:-handled}"
      F="$DIR/$(printf '%08d' "$ID").md"
      [ -f "$F" ] || { echo "intake: no instruction $ID" >&2; exit 2; }
      sed -i "s/^status: .*/status: handled/" "$F"
      { echo; echo "## HANDLED $(now)"; printf '%s\n' "$WHY"; } >> "$F"
      echo "marked $ID handled" ;;

*) sed -n '30,34p' "$0"; exit 2 ;;
esac

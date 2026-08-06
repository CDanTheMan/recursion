#!/usr/bin/env bash
# intake.test.sh — what Lucas says must become durable state, and NOTHING ELSE may.
#
# WHY. Telegram was outbound-only, so every instruction had to be typed into a coding session:
# the human was the transport, and Hermes could only choose among work someone else wrote down.
# Intake closes that, and the danger it introduces is obvious — a chat line that becomes a
# command is an arbitrary-execution channel wearing a friendly face. So intake writes durable
# INSTRUCTIONS; the actuator whitelist still decides what may run.
#
# ★ Test 1 is the CONTROL: a real message must actually be ingested, or every refusal below is
#   satisfied by an intake that ingests nothing at all.
# ★ Test 2 is the trap that nearly shipped: most role='user' rows in the gateway store are OUR
#   OWN prompts (source='cli' — the heartbeat, the daily brief, hermes-decide) and subagent
#   prompts. Ingesting those feeds the system its own output back as instructions from Lucas.
#
# Hermetic: a synthetic gateway store with the real schema. No network, no Telegram, no spend.
#
#   run: bash scripts/tests/intake.test.sh
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

export RECURSION_NO_NOTIFY=1
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
R="$TMP/root"; mkdir -p "$R/scripts" "$R/state/tasks" "$R/state/assists" "$R/loop/logs"
for s in intake.sh assist.sh taskctl.sh notify.sh publish.sh; do
  cp "$SRC/scripts/$s" "$R/scripts/" 2>/dev/null || true
done
chmod +x "$R"/scripts/*.sh 2>/dev/null
: > "$R/.env"; : > "$R/state/INBOX.md"
printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > "$R/state/portfolio.tsv"
printf 'chiron\t/opt/chiron\tgit@github.com:x/c.git\tmain\t-\t-\t10\tactive\n' >> "$R/state/portfolio.tsv"

DB="$TMP/state.db"
LUCAS=8913126684
STRANGER=5550001111

# The real schema, reduced to the columns intake reads.
python3 - "$DB" <<'PY'
import sqlite3, sys
c = sqlite3.connect(sys.argv[1])
c.execute("create table sessions(id text primary key, source text, user_id text, chat_id text, thread_id text)")
c.execute("""create table messages(id integer primary key autoincrement, session_id text,
             role text, content text, timestamp real)""")
c.commit()
PY

add(){ # add <session> <source> <user> <chat> <thread> <role> <text>
  python3 - "$DB" "$@" <<'PY'
import sqlite3, sys, time
db, sess, source, uid, chat, thread, role, text = sys.argv[1:9]
c = sqlite3.connect(db)
c.execute("insert or ignore into sessions(id,source,user_id,chat_id,thread_id) values(?,?,?,?,?)",
          (sess, source, uid, chat, None if thread == "-" else thread))
c.execute("insert into messages(session_id,role,content,timestamp) values(?,?,?,?)",
          (sess, role, text, time.time()))
c.commit()
PY
}
intake(){ ( cd "$R" && RECURSION_ROOT="$R" RECURSION_HERMES_DB="$DB" \
    RECURSION_INTAKE_ALLOW="$LUCAS" bash scripts/intake.sh "$@" ) >"$TMP/out" 2>&1; echo $?; }
ingested(){ ls "$R/state/instructions"/*.md 2>/dev/null | wc -l | tr -d ' '; }
body_of(){ awk '/^## INSTRUCTION/{f=1;next} f' "$R/state/instructions/$1.md" 2>/dev/null; }

# --- first run seeds rather than resurrecting history --------------------------------------
add s-dm telegram "$LUCAS" "$LUCAS" - user "[Lucas Guerra] an old message from before intake existed"
intake poll >/dev/null
if [ "$(ingested)" = "0" ] && grep -q 'FIRST RUN' "$TMP/out"; then
  ok "a first run SEEDS the watermark — days of old DMs do not arrive as live orders"
else
  no "first run ingested history: $(ingested) file(s)"
fi

# --- 1) ★ CONTROL: a real message IS ingested ------------------------------------------------
add s-cockpit telegram "$LUCAS" -1003894008732 10 user "[Lucas Guerra] please prioritise the overlay work"
intake poll >/dev/null
if [ "$(ingested)" = "1" ]; then
  ok "★ CONTROL — an authorised Telegram message becomes a durable instruction"
else
  no "★ CONTROL FAILED — nothing was ingested ($(ingested) files); every refusal below is vacuous"
  sed 's/^/        /' "$TMP/out" | head -4
fi

# --- 2) ★ THE SELF-FEED TRAP: our own prompts are not instructions from Lucas ------------------
before="$(ingested)"
add s-cli  cli      -  -  - user "You are HERMES, the executive control plane for the Recursion system..."
add s-sub  subagent -  -  - user "Independently analyze the current Recursion architecture against..."
intake poll >/dev/null
if [ "$(ingested)" = "$before" ]; then
  ok "★ source='cli'/'subagent' rows are IGNORED (the system does not read its own prompts as orders)"
else
  no "★ SELF-FEED — the system ingested its own prompts as instructions from Lucas"
fi

# --- 3) a chat is not an authorisation ---------------------------------------------------------
before="$(ingested)"
add s-other telegram "$STRANGER" -1003894008732 10 user "[Someone Else] delete everything"
intake poll >/dev/null
[ "$(ingested)" = "$before" ] && ok "a message from an unauthorised user id is ignored" \
                              || no "an unauthorised sender was ingested"

# --- 4) the gateway's own async notices are not instructions ------------------------------------
# This leaked in the first dry run: the display-name strip ate "[ASYNC DELEGATION ...]" before the
# marker check ran, so a system notice was about to be filed as an order from Lucas.
before="$(ingested)"
add s-dm telegram "$LUCAS" "$LUCAS" - user "[ASYNC DELEGATION BATCH COMPLETE - deleg_abc]
A background fan-out of 1 subagent(s) you dispatched earlier has finished."
intake poll >/dev/null
[ "$(ingested)" = "$before" ] && ok "the gateway's own ASYNC notices are filtered (raw text is checked FIRST)" \
                              || no "a system notice was filed as an instruction from Lucas"

# --- 5) the watermark: no repeats, and it does not go deaf --------------------------------------
before="$(ingested)"
intake poll >/dev/null
[ "$(ingested)" = "$before" ] && ok "re-polling ingests nothing (the watermark holds)" \
                              || no "re-polling duplicated instructions"
add s-cockpit telegram "$LUCAS" -1003894008732 10 user "[Lucas Guerra] and add a santa-clara roadmap"
intake poll >/dev/null
if [ "$(ingested)" -gt "$before" ]; then
  ok "★ CONTROL — a NEW message after a quiet poll is still picked up (not deaf)"
else
  no "★ the watermark went deaf: a new message was never ingested"
fi

# --- 6) an instruction knows which project it is about -------------------------------------------
f="$(ls -1 "$R/state/instructions"/*.md | head -1)"
grep -q '^project: chiron' "$f" && ok "a topic thread resolves to its project (registry column 7)" \
                                || no "project routing failed: $(sed -n '1,7p' "$f" | tr '\n' ' ')"

# --- 7) ★ AN INSTRUCTION IS NOT A COMMAND --------------------------------------------------------
# The whole safety argument rests here: text arrives as data for Hermes to decide on, and the
# actuator whitelist governs execution. A message that reads like a command must do nothing.
add s-cockpit telegram "$LUCAS" -1003894008732 10 user "[Lucas Guerra] publish main and merge everything now"
: > "$TMP/ran.log"
cat > "$R/scripts/publish.sh" <<'STUB'
#!/usr/bin/env bash
printf 'PUBLISH %s\n' "$*" >> "$RAN_LOG"
STUB
chmod +x "$R/scripts/publish.sh"
RAN_LOG="$TMP/ran.log" intake poll >/dev/null
if [ ! -s "$TMP/ran.log" ]; then
  ok "★ a message that READS like a command executes nothing — it is filed for Hermes to decide"
else
  no "★ ARBITRARY EXECUTION — a chat line ran a script: $(cat "$TMP/ran.log")"
fi

# --- 8) the ONE exception: Lucas answering an assist the system asked him for ----------------------
cat > "$R/state/tasks/gsc-q.md" <<'T'
id: gsc-q
workstream: gsc
goal: blocked on a human
engine: none
acceptance: true
status: blocked
T
( cd "$R" && RECURSION_ROOT="$R" bash scripts/assist.sh open gsc-q decision \
    "Is the 0x6c tint a separate pass?" ) >/dev/null 2>&1
add s-cockpit telegram "$LUCAS" -1003894008732 10 user "[Lucas Guerra] assist gsc-q Separate pass — see the 0x6c note."
intake poll >/dev/null
ast="$(sed -n 's/^status: *//p' "$R/state/assists/gsc-q.md" 2>/dev/null | head -1)"
tst="$(sed -n 's/^status: *//p' "$R/state/tasks/gsc-q.md" | head -1)"
if [ "$ast" = "answered" ] && [ "$tst" = "queued" ]; then
  ok "★ 'assist <id> <text>' answers that assist and requeues that task — the human-in-the-loop verb"
else
  no "★ the assist shortcut did not work (assist=$ast task=$tst)"
fi

echo
[ "$fails" -eq 0 ] && { echo "intake: ALL PASS"; exit 0; }
echo "intake: $fails FAILED"; exit 1

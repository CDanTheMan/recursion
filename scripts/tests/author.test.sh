#!/usr/bin/env bash
# author.test.sh — Hermes may now WRITE. This is where that authority is bounded.
#
# WHY. Every verb before this one operated on work somebody else had already written down, so
# "set up santa-clara" could only ever come back as `escalate`. Authoring closes that gap, and it
# is the largest expansion of authority in the rebase — so the tests are about what it CANNOT do
# at least as much as what it can.
#
# ★ Test 1 is the CONTROL: a legitimate authoring call must actually work, or every refusal
#   below is satisfied by an author.sh that refuses everything and the loop simply stops.
# ★ Test 4 is the load-bearing one: APPEND-ONLY. A model that can rewrite a roadmap can delete
#   the plan, and the deletion would look exactly like a plan.
# ★ Test 6 is the human gate: no deploy key, no repo — and a key is a fact about GitHub, not a
#   flag anything here can flip.
#
#   run: bash scripts/tests/author.test.sh
set -uo pipefail
if [ "$(uname -s)" != "Linux" ]; then
  echo "author: SKIP (Linux loop runtime required; certified in the box suite)"
  exit 0
fi
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

export RECURSION_NO_NOTIFY=1
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
R="$TMP/root"; mkdir -p "$R/scripts" "$R/state/roadmaps" "$R/state/projects" "$R/state/project-config" \
  "$R/state/pilots" "$R/state/instructions" "$R/state/.locks" "$R/loop/logs"
for s in author.sh project-pilot.py remote_evidence.py engine_contract.py project_authority.py pilot_instruction.py instruction_routing.py seed_contract.py taskctl.sh jsonl_durable.py transition_receipt.py runtime-state.py notify.sh resync.sh intake.sh conduct-hermes.sh validate-decision.py; do
  cp "$SRC/scripts/$s" "$R/scripts/" 2>/dev/null || true
done
chmod +x "$R"/scripts/*.sh 2>/dev/null
: > "$R/.env"
GIT="git -c user.name=t -c user.email=t@t -c init.defaultBranch=main"
ORIGIN="$TMP/origin.git"; $GIT init -q --bare "$ORIGIN"
W="$TMP/seed"; $GIT init -q "$W"; ( cd "$W" && echo x > f.txt && $GIT add -A && $GIT commit -qm init \
  && $GIT branch -M main && $GIT remote add origin "$ORIGIN" && $GIT push -q origin main ) >/dev/null 2>&1

printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > "$R/state/portfolio.tsv"
printf 'chiron\t/opt/chiron\tgit@github.com:x/c.git\tmain\t-\t-\t10\tactive\n' >> "$R/state/portfolio.tsv"
cat > "$R/state/roadmaps/chiron.md" <<'T'
engine: claude
repo: /opt/chiron
acceptance: npm run build

- [x] an item already done
- [ ] an item already planned
T
ORIG_HASH="$(md5sum < "$R/state/roadmaps/chiron.md")"

au(){ ( cd "$R" && RECURSION_ROOT="$R" bash scripts/author.sh "$@" ) >"$TMP/out" 2>&1; echo $?; }

# --- 1) ★ CONTROL: a legitimate roadmap item is added and is plannable -----------------------
rc=$(au roadmap-add chiron "add a nav bar with links to each unit")
if [ "$rc" = "0" ] && grep -q '^- \[ \] add a nav bar' "$R/state/roadmaps/chiron.md"; then
  ok "★ CONTROL — an instruction becomes a plannable roadmap item (authoring actually works)"
else
  no "★ CONTROL FAILED — a valid roadmap-add did nothing (rc=$rc): $(cat "$TMP/out")"
fi

# --- 2) names are filenames, so they are an injection boundary --------------------------------
for bad in "../../etc/passwd" ".hidden" "has space" "UPPER"; do
  rc=$(au roadmap-add "$bad" "some item")
  [ "$rc" = "0" ] && { no "a dangerous workstream name was accepted: '$bad'"; break; }
done
[ "$rc" != "0" ] && ok "traversal / hidden / spaced / uppercase names are refused"
[ ! -f "$TMP/root/../../etc/passwd.md" ] && ok "no file was created outside state/roadmaps" \
  || no "a write escaped the roadmap directory"

# --- 3) an unknown roadmap is refused rather than invented -------------------------------------
rc=$(au roadmap-add never-heard-of-it "do a thing")
[ "$rc" != "0" ] && [ ! -f "$R/state/roadmaps/never-heard-of-it.md" ] \
  && ok "adding to a nonexistent roadmap is refused (roadmap-new is explicit, with a repo)" \
  || no "an unknown roadmap was invented by roadmap-add"

# --- 4) ★ APPEND-ONLY: nothing that was already there may change --------------------------------
head -n 6 "$R/state/roadmaps/chiron.md" > "$TMP/head6"
if [ "$(md5sum < "$TMP/head6")" = "$ORIG_HASH" ]; then
  ok "★ every pre-existing line survives byte-for-byte (a plan cannot be quietly deleted)"
else
  no "★ APPEND-ONLY VIOLATED — existing roadmap content changed"
  diff <(head -6 "$R/state/roadmaps/chiron.md") <(printf '%s' "$(cat "$TMP/head6")") | head -5
fi
rc=$(au roadmap-add chiron "   ")
[ "$rc" != "0" ] && ok "an empty roadmap item is refused" || no "an empty item was appended"
rc=$(au roadmap-add chiron "line one
line two")
[ "$rc" != "0" ] && ok "a multi-line item is refused (it would forge extra checklist lines)" \
                 || no "a multi-line item was appended"

# --- 5) portfolio-add can only ever create a PENDING row ----------------------------------------
rc=$(au portfolio-add santa-clara git@github.com:NotSkittlz/santa-clara.git \
  "Build only within santa-clara under approved goals; no portfolio or policy authority")
row="$(grep '^santa-clara' "$R/state/portfolio.tsv" || true)"
if [ "$rc" = "0" ] && printf '%s' "$row" | grep -q 'pending$'; then
  ok "portfolio-add creates a PENDING row — never an active one"
else
  no "portfolio-add produced: $row"
fi
projection="$(python3 - "$R/state/project-config/santa-clara.json" \
  "$R/state/pilots/pilot-santa-clara.json" <<'PY'
import json,sys
project=json.load(open(sys.argv[1],encoding='utf-8')).get('required_non_goals')
pilot=json.load(open(sys.argv[2],encoding='utf-8')).get('required_non_goals')
print('match' if project == pilot == ['credentials','merge','deploy'] else 'mismatch')
PY
)"
[ "$projection" = match ] \
  && ok "pending project and pilot share the exact default non-goal projection" \
  || no "pending project/pilot default non-goals differ"
rc=$(au project-topic-bind santa-clara 33)
[ "$rc" = "0" ] && grep '^santa-clara' "$R/state/portfolio.tsv" | cut -f7 | grep -qx 33 \
  && ok "pending project binds one explicit Telegram topic before activation" \
  || no "pending project topic binding failed (rc=$rc): $(cat "$TMP/out")"
rc=$(au portfolio-add evil "http://not-github.example/x.git" "bounded fixture charter")
[ "$rc" != "0" ] && ok "a non-GitHub remote is refused" || no "an arbitrary remote was added"

# --- 6) ★ THE HUMAN GATE: no deploy key, no repo -------------------------------------------------
rc=$(au register santa-clara)
if [ "$rc" = "4" ] && grep -q 'deploy key' "$TMP/out"; then
  ok "★ register REFUSES without a deploy key — only Lucas can provision one on GitHub"
else
  no "★ THE GATE IS OPEN — register returned $rc without a key: $(cat "$TMP/out")"
fi
still="$(grep '^santa-clara' "$R/state/portfolio.tsv")"
printf '%s' "$still" | grep -q 'pending$' && ok "the refused row is still pending (no half-registration)" \
                                          || no "a refused register left the row active"

# ★ CONTROL for the gate: WITH a key, the same call succeeds — or "it refuses" is satisfied by a
# register that can never work at all.
KEY="$TMP/fake_deploy"; : > "$KEY"
python3 - "$R/state/portfolio.tsv" "$R/state/project-config/santa-clara.json" "$KEY" "$ORIGIN" <<'PY'
import io,json,sys
reg,config,key,remote=sys.argv[1:]
out=[]
for line in io.open(reg,encoding='utf-8',newline='').read().split('\n'):
    c=line.split('\t')
    if len(c)>=8 and c[0]=='santa-clara':
        c[2]=remote; c[4]=key; c[1]=key+'-clone'; line='\t'.join(c)
    out.append(line)
io.open(reg,'w',encoding='utf-8',newline='\n').write('\n'.join(out))
d=json.load(open(config,encoding='utf-8')); d.update(repo=key+'-clone',remote=remote,deploy_key_ref=key)
with open(config,'w',encoding='utf-8') as out: json.dump(d,out); out.write('\n')
PY
rc=$(au register santa-clara)
if [ "$rc" = "0" ] && grep '^santa-clara' "$R/state/portfolio.tsv" | grep -q 'active$'; then
  ok "★ CONTROL — with a key present, register clones and activates (the gate is a gate, not a wall)"
else
  no "★ CONTROL FAILED — register never works even with a key (rc=$rc): $(cat "$TMP/out")"
fi

# --- 7) roadmap-new derives its header from the registry, not from prose --------------------------
rc=$(au roadmap-new santaclara santa-clara)
if [ "$rc" = "0" ] && grep -q "^repo: $KEY-clone" "$R/state/roadmaps/santaclara.md"; then
  ok "roadmap-new stamps repo/key FROM THE REGISTRY (a wrong repo builds in the wrong place)"
else
  no "roadmap-new header is wrong (rc=$rc): $(sed -n '1,4p' "$R/state/roadmaps/santaclara.md" 2>/dev/null)"
fi
rc=$(au roadmap-new dupe santa-clara)
rc2=$(au roadmap-new santaclara santa-clara)
[ "$rc2" != "0" ] && ok "roadmap-new refuses to overwrite an existing roadmap" || no "a roadmap was overwritten"

# --- 8) ★ the actuator carries prose in `text`, and validates it separately ------------------------
# args are held to an identifier pattern because they are process arguments; prose could never
# pass that, so it travels in its own field with its own rules. Both boundaries are checked.
val(){ python3 "$R/scripts/validate-decision.py" \
        "noop roadmap-add note register" "$1" 2>&1 | cut -d' ' -f1; }
[ "$(val '{"verb":"roadmap-add","args":["chiron"],"text":"add a nav bar","goal":"g","wrong_if":"w"}')" = "OK" ] \
  && ok "a decision carrying prose in text validates" || no "prose in text was rejected"
[ "$(val '{"verb":"roadmap-add","args":["chiron"],"text":"a\nb","goal":"g","wrong_if":"w"}')" = "ERR" ] \
  && ok "★ text with a newline is refused (it would forge extra lines in an append-only file)" \
  || no "a newline survived into text"
[ "$(val '{"verb":"roadmap-add","args":["chiron"],"text":"--force something","goal":"g","wrong_if":"w"}')" = "ERR" ] \
  && ok "text may not start with '-' (it would be read as a flag)" || no "a flag-shaped text was accepted"
[ "$(val '{"verb":"roadmap-add","args":["../etc"],"text":"x","goal":"g","wrong_if":"w"}')" = "ERR" ] \
  && ok "args stay strict — traversal is still refused with text present" || no "args validation weakened"

echo
[ "$fails" -eq 0 ] && { echo "author: ALL PASS"; exit 0; }
echo "author: $fails FAILED"; exit 1

#!/usr/bin/env bash
# Phase 0 control: reproduce the Phase 1 security-boundary defects before fixing them.
# This suite is EXPECTED TO FAIL on the pre-change commit recorded in the production plan.
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/bin"; mkdir -p "$BIN"

# A deterministic stand-in for the model worker. It runs the requested script with the exact
# identity and environment work.sh gave it; no model, network, credential, or spend is involved.
cat > "$BIN/claude" <<'STUB'
#!/usr/bin/env bash
bash -c "${STUB_ARM_SCRIPT:-:}"
STUB
chmod +x "$BIN/claude"

R="$TMP/controller"
mkdir -p "$R/scripts" "$R/state/tasks" "$R/loop/logs" "$R/app"
for s in work.sh assignment-token.py worker-sandbox.sh phase5_safety.py taskctl.sh assignment.py assignment_contract.py jsonl_durable.py transition_receipt.py runtime-state.py board.sh notify.sh resync.sh capacity.sh \
  assist.sh conduct.sh engine_contract.py git-scope.py pilot_instruction.py plan.sh project-pilot.py \
  project-reconcile.py project_authority.py provider-connect-proxy.py provider_contract.py provider-network.sh provider-egress.py publish.sh \
  remote_evidence.py resolve-engine.py resolve-model-alias.py run_contract.py seed_contract.py \
  validate-assignment-result.py validate-gate.py validate-verifier-result.py validate-worker-result.py \
  worker-evidence.py; do
  cp "$SRC/scripts/$s" "$R/scripts/" 2>/dev/null || true
done
python3 "$SRC/scripts/tests/staged-dependency-guard.py" "$SRC/scripts" "$R/scripts" \
  || { no "phase 1 fixture is missing a staged first-party dependency"; }
chmod +x "$R/scripts/worker-sandbox.sh" 2>/dev/null || true
: > "$R/.env"
printf 'seed\n' > "$R/app/seed.txt"
git -c init.defaultBranch=main init -q "$R"
git -C "$R" add -A
git -C "$R" -c user.name=t -c user.email=t@t commit -qm init
git -C "$R" branch -M main

mktask(){ # id acceptance
  cat > "$R/state/tasks/$1.md" <<T
id: $1
workstream: phase1
goal_id: phase1-goal
goal: exercise a security boundary
engine: claude
repo: $R
acceptance: $2
workdir: .
allowed_paths: app
network_policy: none
autonomy: auto
status: queued

control fixture
T
}
status_of(){ sed -n 's/^status: *//p' "$R/state/tasks/$1.md" | head -1; }

# 1. PAUSE must interrupt an already-running worker and prevent every later gate/publication step.
STARTED="$TMP/arm-started"; GATE="$TMP/gate-ran"
mktask pause-midrun "touch '$GATE'"
STUB_ARM_SCRIPT='touch "$STUB_STARTED"; sleep 3; mkdir -p app; echo done > app/result.txt' \
STUB_STARTED="$STARTED" PATH="$BIN:$PATH" RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 \
RECURSION_REQUIRE_FRESH_BASE=0 RECURSION_TEST_WORKER=sandbox \
bash "$R/scripts/work.sh" pause-midrun >"$TMP/pause.out" 2>&1 &
wpid=$!
for _ in $(seq 1 50); do [ -f "$STARTED" ] && break; sleep 0.1; done
printf 'PAUSED test\nreason: Phase 0 mid-run control\n' > "$R/state/PAUSE"
wait "$wpid" 2>/dev/null || true
if [ ! -f "$GATE" ] && [ "$(status_of pause-midrun)" != "passed" ]; then
  ok "PAUSE terminated the in-flight worker before its gate"
else
  no "PAUSE was noticed only at startup; the in-flight worker reached status=$(status_of pause-midrun) and gate=$([ -f "$GATE" ] && echo ran || echo blocked)"
fi
rm -f "$R/state/PAUSE"

# 2. A worker must not share the controller identity, read controller-only data, write outside
# its worktree, or invoke the publisher. The current prompt/scope gate cannot enforce OS boundaries.
SECRET="$TMP/controller-secret"; LEAK="$TMP/leaked-secret"; OUTSIDE="$TMP/outside-write"
PUBLOG="$TMP/publisher-called"; UIDLOG="$TMP/worker-uid"
printf 'sentinel-secret\n' > "$SECRET"; chmod 600 "$SECRET"
cat > "$TMP/publisher" <<'STUB'
#!/usr/bin/env bash
printf 'called\n' > "$STUB_PUBLOG"
STUB
chmod 700 "$TMP/publisher"
mktask worker-sandbox "test -f app/ok.txt"
STUB_ARM_SCRIPT='set -e; cat "$STUB_SECRET" > "$STUB_LEAK"; echo outside > "$STUB_OUTSIDE"; id -u > "$STUB_UIDLOG"; "$STUB_PUBLISHER"; mkdir -p app; echo ok > app/ok.txt' \
STUB_SECRET="$SECRET" STUB_LEAK="$LEAK" STUB_OUTSIDE="$OUTSIDE" STUB_UIDLOG="$UIDLOG" \
STUB_PUBLISHER="$TMP/publisher" STUB_PUBLOG="$PUBLOG" PATH="$BIN:$PATH" RECURSION_ROOT="$R" \
RECURSION_NO_NOTIFY=1 RECURSION_REQUIRE_FRESH_BASE=0 RECURSION_TEST_WORKER=sandbox \
bash "$R/scripts/work.sh" worker-sandbox \
  >"$TMP/sandbox.out" 2>&1 || true
if [ ! -e "$LEAK" ] && [ ! -e "$OUTSIDE" ] && [ ! -e "$PUBLOG" ] \
   && { [ ! -e "$UIDLOG" ] || [ "$(cat "$UIDLOG")" != "$(id -u)" ]; } \
   && [ "$(status_of worker-sandbox)" != "passed" ]; then
  ok "worker OS boundary denied controller data, outside writes, publisher access, and shared identity"
else
  no "worker inherited controller authority (status=$(status_of worker-sandbox), secret=$([ -e "$LEAK" ] && echo read || echo denied), outside=$([ -e "$OUTSIDE" ] && echo wrote || echo denied), publisher=$([ -e "$PUBLOG" ] && echo called || echo denied))"
fi

# 3. The copied model executable must remain reachable by the dedicated runner when the
# hardened controller/unit umask is 0077. The directory and executable stay outside allowed_paths
# and are removed before the controller evaluates the worker diff.
mktask worker-sandbox-umask "test -f app/ok.txt && test -s app/uid.txt"
(
  umask 0077
  STUB_ARM_SCRIPT='mkdir -p app; id -u > app/uid.txt; echo ok > app/ok.txt' \
  PATH="$BIN:$PATH" RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 RECURSION_GIT_FETCH=0 \
  RECURSION_REQUIRE_FRESH_BASE=0 RECURSION_TEST_WORKER=sandbox \
  bash "$R/scripts/work.sh" worker-sandbox-umask
) >"$TMP/umask.out" 2>&1
umask_uid="$(git -C "$R" show loop/work/worker-sandbox-umask:app/uid.txt 2>/dev/null | tr -d '[:space:]')"
if [ "$(status_of worker-sandbox-umask)" = passed ] \
   && [ -n "$umask_uid" ] && [ "$umask_uid" != "$(id -u)" ]; then
  ok "copied worker executable remained reachable under hardened controller umask"
else
  no "copied worker executable was inaccessible under hardened controller umask (status=$(status_of worker-sandbox-umask))"
fi

# 4. The publisher itself must reject protected spellings, symbolic refs, and revision/refspec
# expressions. Each case gets a fresh local bare origin, so this cannot touch a real repository.
probe_ref(){ # label default-branch candidate
  local label="$1" def="$2" candidate="$3" d="$TMP/pub-$1" before after out rc
  mkdir -p "$d/repo"; git -c init.defaultBranch="$def" init -q --bare "$d/origin.git"
  git -c init.defaultBranch="$def" init -q "$d/repo"
  printf 'one\n' > "$d/repo/file"; git -C "$d/repo" add file
  git -C "$d/repo" -c user.name=t -c user.email=t@t commit -qm one
  git -C "$d/repo" branch -M "$def"; git -C "$d/repo" remote add origin "$d/origin.git"
  git -C "$d/repo" push -q origin "$def"
  before="$(git --git-dir="$d/origin.git" rev-parse "refs/heads/$def")"
  printf 'two\n' >> "$d/repo/file"; git -C "$d/repo" add file
  git -C "$d/repo" -c user.name=t -c user.email=t@t commit -qm two
  [ "$candidate" = alias ] && git -C "$d/repo" symbolic-ref refs/heads/alias "refs/heads/$def"
  set +e
  out="$(RECURSION_ROOT="$SRC" RECURSION_ALLOW_PUSH=1 bash "$SRC/scripts/publish.sh" \
    --branch "$candidate" --repo "$d/repo" --key "$d/no-key" 2>&1)"; rc=$?
  set -e
  after="$(git --git-dir="$d/origin.git" rev-parse "refs/heads/$def")"
  if [ "$rc" -ne 0 ] && [ "$before" = "$after" ] && printf '%s' "$out" | grep -qi 'refus'; then
    ok "publisher refused $label"
  else
    no "publisher did not fail closed for $label (rc=$rc default_changed=$([ "$before" != "$after" ] && echo yes || echo no))"
  fi
}
probe_ref main main main
probe_ref master master master
probe_ref HEAD main HEAD
probe_ref full-ref main refs/heads/main
probe_ref symbolic-ref main alias
probe_ref revision-expression main 'main^0'

echo
[ "$fails" -eq 0 ] && { echo "hermes-pilot-phase1-red: ALL PASS"; exit 0; }
echo "hermes-pilot-phase1-red: $fails FAILED (expected on the Phase 0 pre-fix commit)"; exit 1

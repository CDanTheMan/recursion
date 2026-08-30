#!/usr/bin/env bash
# Phase 5 falsifiers: strict worker envelopes, complete scope evidence, timeout/lease handling,
# and exact-commit independent verification. Hermetic: no model, network, publisher, or live state.
set -uo pipefail
export LC_ALL=C
export RECURSION_TEST_PROVIDER_NETWORK=logical
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"
cleanup(){
  if [ "${PHASE5_KEEP_TMP:-0}" = 1 ]; then echo "PHASE5_TMP=$TMP" >&2
  else rm -rf "$TMP"; fi
}
trap cleanup EXIT
BIN="$TMP/bin"; R="$TMP/controller"; ORIGIN="$TMP/origin.git"
mkdir -p "$BIN" "$R/scripts/tests" "$R/state/tasks" "$R/state/runs" \
  "$R/loop/logs" "$R/app" "$R/fixtures" "$R/other" \
  "$R/user-client/render/data/models"
for s in work.sh worker-sandbox.sh taskctl.sh jsonl_durable.py transition_receipt.py runtime-state.py board.sh notify.sh resync.sh capacity.sh \
         git-scope.py validate-gate.py validate-worker-result.py validate-verifier-result.py \
         resolve-model-alias.py worker-evidence.py seed_contract.py project-pilot.py engine_contract.py \
         pilot_instruction.py project_authority.py; do
  [ ! -f "$SRC/scripts/$s" ] || cp "$SRC/scripts/$s" "$R/scripts/"
done
chmod +x "$R/scripts/"* 2>/dev/null || true
printf 'protected\n' > "$R/scripts/protected.sh"
printf 'test\n' > "$R/scripts/tests/existing.test.cjs"
printf '{"truth":1}\n' > "$R/fixtures/truth.json"
printf 'seed\n' > "$R/app/seed.txt"
printf 'immutable oracle\n' > "$R/user-client/render/data/models/oracle.json"
printf '/user-client/render/data/models/\n' > "$R/.gitignore"
printf 'user-client/render/data/models\n' > "$R/.seedlist"
printf '#!/usr/bin/env bash\nexit 1\n' > "$R/app/gate.sh"; chmod +x "$R/app/gate.sh"
: > "$R/.env"; : > "$R/state/INBOX.md"

cat > "$BIN/claude" <<'STUB'
#!/usr/bin/env bash
if [ "${RECURSION_WORKER_ROLE:-implementer}" = verifier ]; then
  bash -c "${STUB_VERIFIER_SCRIPT:-:}"
else
  bash -c "${STUB_ARM_SCRIPT:-:}"
fi
STUB
chmod +x "$BIN/claude"

git -c init.defaultBranch=main init -q --bare "$ORIGIN"
git -c init.defaultBranch=main init -q "$R"
git -C "$R" add -A
git -C "$R" -c user.name=t -c user.email=t@t commit -qm init
git -C "$R" branch -M main; git -C "$R" remote add origin "$ORIGIN"
git -C "$R" push -q origin main; git -C "$R" fetch -q origin
printf '#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n' > "$R/state/portfolio.tsv"
printf 'phase5\t%s\t%s\tmain\t-\t-\t31\tactive\n' "$R" "$ORIGIN" >> "$R/state/portfolio.tsv"

mktask(){ # id acceptance [expected-change] [gate-files]
  cat > "$R/state/tasks/$1.md" <<T
schema_version: 1
id: $1
project_id: phase5
workstream: phase5
goal_id: phase5-goal
goal: produce the bounded Phase 5 fixture for $1
engine: claude
repo: $R
acceptance: $2
workdir: .
allowed_paths: app
non_goals: tests,fixtures,control-plane,merge,deploy
worker_class: claude
model_alias: sonnet-routine
verifier_model_alias: opus-review
deadline_seconds: 1
verifier_deadline_seconds: 2
network_policy: provider-only
evidence_contract: worker-result-v1
verification: independent
expected_change: ${3:-required}
gate_files: ${4:-}
autonomy: auto
status: queued

Implement only this non-vacuous fixture.
T
}
status_of(){ sed -n 's/^status: *//p' "$R/state/tasks/$1.md" | head -1 | tr -d '\r'; }
run_case(){ # id implementer-script [verifier-script]
  ( cd "$R" && PATH="$BIN:$PATH" RECURSION_ROOT="$R" \
      RECURSION_NO_NOTIFY="${RECURSION_TEST_NO_NOTIFY:-1}" \
      RECURSION_ALLOW_PUSH="${RECURSION_TEST_ALLOW_PUSH:-0}" \
      RECURSION_GIT_FETCH=0 RECURSION_TEST_WORKER=logical \
      RECURSION_MODEL_ALIAS_SONNET_ROUTINE=stub-sonnet \
      RECURSION_MODEL_ALIAS_OPUS_REVIEW=stub-opus \
      STUB_ARM_SCRIPT="$2" STUB_VERIFIER_SCRIPT="${3:-:}" \
      bash scripts/work.sh "$1" ) >"$TMP/out-$1" 2>&1
}
done_result(){ # summary files-json
  printf '{"status":"done","summary":"%s","files_changed":%s,"tests_run":"fixture gate","risks":[],"blocker":""}' "$1" "$2"
}
verdict_script='mkdir -p "$RECURSION_EVIDENCE_DIR"; printf "{\"verdict\":\"pass\",\"commit_oid\":\"%s\",\"implementer_run_id\":\"%s\",\"summary\":\"independent review passed\",\"evidence\":[\"diff and machine gate inspected\"],\"risks\":[]}" "$RECURSION_VERIFICATION_COMMIT" "$RECURSION_IMPLEMENTER_RUN_ID" > "$RECURSION_EVIDENCE_DIR/verdict.json"'

if [ "${PHASE5_HARDENING_ONLY:-0}" != 1 ]; then
# 1. A worker-created commit must not hide a protected-file change from scope verification.
MARKER1="$TMP/gate-committed-protected"
mktask committed-protected "test -s app/committed.txt && touch $MARKER1"
result="$(done_result committed '["app/committed.txt","scripts/protected.sh"]')"
run_case committed-protected "printf ok > app/committed.txt; printf evil > scripts/protected.sh; printf '%s' '$result' > .recursion-result.json; git add -A; git -c user.name=arm -c user.email=arm@t commit -qm hidden"
if [ "$(status_of committed-protected)" = escalated ] && [ ! -e "$MARKER1" ]; then
  ok "committed protected-file mutation is rejected before its gate"
else
  no "a committed protected-file mutation was hidden (status=$(status_of committed-protected) gate=$([ -e "$MARKER1" ] && echo ran || echo blocked))"
fi

# 1b. A declared ignored oracle is read-only/checksummed and cannot invisibly grade itself.
MARKER_SEED="$TMP/gate-seed-tamper"
mktask seed-tamper "test -s app/seed-safe.txt && touch $MARKER_SEED"
sed -i '/^workdir:/i seed: user-client/render/data/models' "$R/state/tasks/seed-tamper.md"
result="$(done_result seed '[]')"
run_case seed-tamper "printf corrupt > user-client/render/data/models/oracle.json; printf '%s' '$result' > .recursion-result.json"
if [ "$(status_of seed-tamper)" = escalated ] && [ ! -e "$MARKER_SEED" ]; then
  ok "ignored seed/oracle mutation is rejected before its gate"
else
  no "an ignored worker-writable oracle reached its gate (status=$(status_of seed-tamper))"
fi

# 1c. Phase-8 seeds are compared to the approved manifest/content digest, copied into the
# verifier checkout too, and represented in both run records without corpus bytes.
SEED_CONTRACT="$(python3 "$R/scripts/seed_contract.py" inspect --repo "$R")"
eval "$(python3 - "$SEED_CONTRACT" <<'PY'
import json,shlex,sys
row=json.loads(sys.argv[1])
for key,name in [('manifest_sha256','BOUND_MANIFEST'),('content_sha256','BOUND_SEED')]:
    print(f'{name}={shlex.quote(row[key])}')
PY
)"
mktask seed-bound-pass "test -s app/seed-bound.txt && test -s user-client/render/data/models/oracle.json"
sed -i "/^workdir:/i seed_manifest: .seedlist\nseed_manifest_sha256: $BOUND_MANIFEST\nseed: user-client/render/data/models\nseed_digest: $BOUND_SEED" \
  "$R/state/tasks/seed-bound-pass.md"
result="$(done_result seed-bound '["app/seed-bound.txt"]')"
seeded_verdict='test "$(cat user-client/render/data/models/oracle.json)" = "immutable oracle" || exit 42; '"$verdict_script"
run_case seed-bound-pass "printf ok > app/seed-bound.txt; printf '%s' '$result' > .recursion-result.json" "$seeded_verdict"
if [ "$(status_of seed-bound-pass)" = passed ] && python3 - "$R/state/runs" "$BOUND_SEED" <<'PY'
import glob,json,sys
rows=[]
for path in glob.glob(sys.argv[1]+'/*.json'):
    try: row=json.load(open(path))
    except Exception: continue
    if row.get('task_id')=='seed-bound-pass': rows.append(row)
roles={row.get('role') for row in rows}
valid=(roles=={'implementer','verifier'} and all(
    row.get('seed_evidence',{}).get('content_sha256')==sys.argv[2]
    and row.get('seed_evidence',{}).get('verified_before') is True
    and row.get('seed_evidence',{}).get('verified_after') is True for row in rows))
raise SystemExit(0 if valid else 1)
PY
then
  ok "approved seed digest reaches implementer and independent verifier evidence"
else
  no "approved seed was absent, self-derived, or missing from verifier evidence"
fi

mktask seed-wrong-digest "test -s app/never-seeded.txt"
WRONG_SEED="0${BOUND_SEED#?}"
[ "$WRONG_SEED" != "$BOUND_SEED" ] || WRONG_SEED="1${BOUND_SEED#?}"
sed -i "/^workdir:/i seed_manifest: .seedlist\nseed_manifest_sha256: $BOUND_MANIFEST\nseed: user-client/render/data/models\nseed_digest: $WRONG_SEED" \
  "$R/state/tasks/seed-wrong-digest.md"
result="$(done_result wrong '["app/never-seeded.txt"]')"
run_case seed-wrong-digest "printf reached > app/never-seeded.txt; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
[ "$(status_of seed-wrong-digest)" = escalated ] \
  && ok "copied seed is compared with the approved digest before worker launch" \
  || no "a task ran against seed bytes that disagreed with its approved digest"

mktask verifier-seed-tamper "test -s app/verifier-seed.txt"
sed -i "/^workdir:/i seed_manifest: .seedlist\nseed_manifest_sha256: $BOUND_MANIFEST\nseed: user-client/render/data/models\nseed_digest: $BOUND_SEED" \
  "$R/state/tasks/verifier-seed-tamper.md"
result="$(done_result verifier-seed '["app/verifier-seed.txt"]')"
run_case verifier-seed-tamper \
  "printf original > app/verifier-seed.txt; printf '%s' '$result' > .recursion-result.json" \
  'printf corrupt > user-client/render/data/models/oracle.json; '"$verdict_script"
[ "$(status_of verifier-seed-tamper)" = escalated ] \
  && ok "independent verifier cannot mutate an ignored seeded oracle" \
  || no "verifier seed mutation escaped integrity enforcement"

# 2. One committed change set exercises test, fixture rename/delete, and out-of-scope paths.
MARKER2="$TMP/gate-committed-mutations"
mktask committed-mutations "test -s app/mutations.txt && touch $MARKER2"
result="$(done_result mutations '["app/mutations.txt","scripts/tests/existing.test.cjs","fixtures/truth.json","app/truth-moved.json","other/stray.txt"]')"
run_case committed-mutations "printf ok > app/mutations.txt; printf evil >> scripts/tests/existing.test.cjs; git mv fixtures/truth.json app/truth-moved.json; printf stray > other/stray.txt; printf '%s' '$result' > .recursion-result.json; git add -A; git -c user.name=arm -c user.email=arm@t commit -qm hidden"
if [ "$(status_of committed-mutations)" = escalated ] && [ ! -e "$MARKER2" ]; then
  ok "committed test/fixture/rename/delete/out-of-scope mutations are rejected"
else
  no "committed mutation set passed or reached its gate (status=$(status_of committed-mutations))"
fi

# 3. Generated work without the required result contract must fail closed.
mktask missing-result "test -s app/missing-result.txt"
run_case missing-result 'printf ok > app/missing-result.txt' "$verdict_script"
[ "$(status_of missing-result)" = escalated ] \
  && ok "missing worker result cannot pass" \
  || no "generated work passed without a result report"

# 4. A no-op cannot satisfy an explicitly non-vacuous implementation task.
mktask nonvacuous-noop "test -s app/seed.txt"
noop='{"status":"no-op","summary":"nothing changed","files_changed":[],"tests_run":"fixture gate","risks":[],"blocker":""}'
run_case nonvacuous-noop "printf '%s' '$noop' > .recursion-result.json" "$verdict_script"
[ "$(status_of nonvacuous-noop)" = escalated ] \
  && ok "no-op is rejected for a task that requires a change" \
  || no "a no-op passed a non-vacuous implementation task"

# 5. Structurally vacuous and worker-modifiable gates must both fail closed.
mktask vacuous-gate true
result="$(done_result vacuous '["app/vacuous.txt"]')"
run_case vacuous-gate "printf ok > app/vacuous.txt; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
[ "$(status_of vacuous-gate)" = escalated ] \
  && ok "literal true gate is rejected as structurally vacuous" \
  || no "literal true was accepted as an autonomy gate"

mktask self-modified-gate "bash app/gate.sh" required app/gate.sh
result="$(done_result selfgate '["app/gate.sh"]')"
run_case self-modified-gate "printf '#!/usr/bin/env bash\nexit 0\n' > app/gate.sh; chmod +x app/gate.sh; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
[ "$(status_of self-modified-gate)" = escalated ] \
  && ok "worker-modified gate file is rejected" \
  || no "the worker rewrote its own gate and passed"

# 6. Deadline expiry must terminate the process group, clear the lease, and open one ask.
mktask hung-worker "test -s app/hung.txt"
result="$(done_result late '["app/hung.txt"]')"
run_case hung-worker "sleep 4; printf late > app/hung.txt; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
lease="$(sed -n 's/^lease_expires: *//p' "$R/state/tasks/hung-worker.md" | head -1)"
timeout_count="$(grep -c 'WORKER TIMEOUT.*hung-worker' "$R/state/INBOX.md" 2>/dev/null || true)"
timeout_run="$(grep -l '"outcome": "timeout"' "$R/state/runs/"*.json 2>/dev/null | head -1 || true)"
pgid=""; [ -z "$timeout_run" ] || pgid="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("process_group",""))' "$timeout_run")"
dead=1; [ -z "$pgid" ] || { kill -0 -- "-$pgid" 2>/dev/null && dead=0 || dead=1; }
if [ "$(status_of hung-worker)" = blocked ] && [ "$lease" = 0 ] && [ "$timeout_count" = 1 ] \
   && [ -n "$timeout_run" ] && [ "$dead" = 1 ]; then
  ok "hung worker timed out, lost its lease, terminated, and opened one actionable escalation"
else
  no "hung-worker control incomplete (status=$(status_of hung-worker) lease=${lease:-missing} escalations=$timeout_count evidence=$([ -n "$timeout_run" ] && echo yes || echo no) dead=$dead)"
fi

# 7. A clean independent verifier must be a distinct run bound to the machine-gated OID.
mktask independent-pass "test -s app/independent.txt"
result="$(done_result independent '["app/independent.txt"]')"
run_case independent-pass "printf original > app/independent.txt; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
if [ "$(status_of independent-pass)" = passed ] && python3 - "$R/state/runs" <<'PY'
import glob,json,sys
rows=[json.load(open(p)) for p in glob.glob(sys.argv[1]+'/*.json') if 'independent-pass' in open(p).read()]
impl=[r for r in rows if r.get('role')=='implementer']; ver=[r for r in rows if r.get('role')=='verifier']
valid=(len(impl)==1 and len(ver)==1 and impl[0]['id']!=ver[0]['id'] and impl[0]['pid']!=ver[0]['pid'])
if valid:
    valid=(impl[0].get('machine_gate',{}).get('commit_oid')==ver[0].get('verification',{}).get('commit_oid')
           and ver[0].get('verification',{}).get('implementer_run_id')==impl[0]['id']
           and ver[0].get('verification',{}).get('verdict')=='pass'
           and all(r.get('usage',{}).get('tokens')==0 and r.get('usage',{}).get('cost_usd')==0
                   and r.get('usage',{}).get('evidence_source')=='controller-engine-policy-v1'
                   for r in (impl[0],ver[0])))
raise SystemExit(0 if valid else 1)
PY
then
  ok "independent exact-commit runs carry controller-owned flat-sub usage evidence"
else
  no "independent exact-commit verification evidence is absent or inconsistent"
fi

# 8. A verifier that mutates its isolated checkout cannot silently certify the implementation.
mktask verifier-mutation "test -s app/verifier-mutation.txt"
result="$(done_result verifier '["app/verifier-mutation.txt"]')"
mutating_verifier='printf evil > app/verifier-mutation.txt; '"$verdict_script"
run_case verifier-mutation "printf original > app/verifier-mutation.txt; printf '%s' '$result' > .recursion-result.json" "$mutating_verifier"
branch_value="$(git -C "$R" show loop/work/verifier-mutation:app/verifier-mutation.txt 2>/dev/null || true)"
if [ "$(status_of verifier-mutation)" = escalated ] && [ "$branch_value" = original ]; then
  ok "verifier mutation is rejected and cannot alter implementer output"
else
  no "verifier mutation was silent (status=$(status_of verifier-mutation) implementer_output=${branch_value:-missing})"
fi
fi

# 9. A durable gate-evidence failure must stop before terminal success, publication,
# notification, or cleanup. The running lease/worktree make the interrupted task recoverable.
NOTIFY_MARKER="$TMP/notify-called"; PUBLISH_MARKER="$TMP/publish-called"
cp "$R/scripts/notify.sh" "$R/scripts/notify.real.sh"
cat > "$R/scripts/notify.sh" <<'SH'
#!/usr/bin/env bash
printf 'notify\n' >> "${TEST_NOTIFY_MARKER:?}"
SH
cat > "$R/scripts/publish.sh" <<'SH'
#!/usr/bin/env bash
printf 'publish\n' >> "${TEST_PUBLISH_MARKER:?}"
SH
chmod +x "$R/scripts/notify.sh" "$R/scripts/publish.sh"

mv "$R/scripts/worker-evidence.py" "$R/scripts/worker-evidence.real.py"
cat > "$R/scripts/worker-evidence.py" <<'PY'
#!/usr/bin/env python3
import os, sys
if len(sys.argv) > 1 and sys.argv[1] == "gate":
    raise SystemExit(87)
real = os.path.join(os.path.dirname(__file__), "worker-evidence.real.py")
os.execv(sys.executable, [sys.executable, real, *sys.argv[1:]])
PY
chmod +x "$R/scripts/worker-evidence.py"
mktask gate-evidence-failure "test -s app/gate-evidence.txt"
result="$(done_result gate-evidence '["app/gate-evidence.txt"]')"
RECURSION_TEST_NO_NOTIFY=0 RECURSION_TEST_ALLOW_PUSH=1 \
  TEST_NOTIFY_MARKER="$NOTIFY_MARKER" TEST_PUBLISH_MARKER="$PUBLISH_MARKER" \
  run_case gate-evidence-failure \
    "printf ok > app/gate-evidence.txt; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
evidence_rc=$?
evidence_lease="$(sed -n 's/^lease_expires: *//p' "$R/state/tasks/gate-evidence-failure.md" | head -1)"
if [ "$evidence_rc" = 87 ] && [ "$(status_of gate-evidence-failure)" = running ] \
   && printf '%s' "$evidence_lease" | grep -qE '^[1-9][0-9]*$' \
   && [ -d "$R/.worktrees/gate-evidence-failure" ] \
   && [ ! -e "$NOTIFY_MARKER" ] && [ ! -e "$PUBLISH_MARKER" ]; then
  ok "gate-evidence failure retains recoverable running state and blocks success side effects"
else
  no "gate-evidence failure escaped fail-closed handling (rc=$evidence_rc status=$(status_of gate-evidence-failure) lease=${evidence_lease:-missing})"
fi
mv "$R/scripts/worker-evidence.real.py" "$R/scripts/worker-evidence.py"

# 10. Even after every build/verifier gate is green, a failed canonical passed transition
# is authoritative: the caller sees failure and nothing publishes, notifies, or cleans up.
mv "$R/scripts/taskctl.sh" "$R/scripts/taskctl.real.sh"
cat > "$R/scripts/taskctl.sh" <<'SH'
#!/usr/bin/env bash
if [ "${1:-}" = esc-record ] && [ "${FAIL_ESC_RECORD:-0}" = 1 ]; then
  exit 85
fi
if [ "${1:-}" = finish ] && [ "${3:-}" = "${FAIL_TASKCTL_STATUS:-}" ]; then
  exit 86
fi
exec bash "$(dirname "$0")/taskctl.real.sh" "$@"
SH
chmod +x "$R/scripts/taskctl.sh"
rm -f "$NOTIFY_MARKER" "$PUBLISH_MARKER"
mktask terminal-state-failure "test -s app/terminal-state.txt"
result="$(done_result terminal-state '["app/terminal-state.txt"]')"
RECURSION_TEST_NO_NOTIFY=0 RECURSION_TEST_ALLOW_PUSH=1 FAIL_TASKCTL_STATUS=passed \
  TEST_NOTIFY_MARKER="$NOTIFY_MARKER" TEST_PUBLISH_MARKER="$PUBLISH_MARKER" \
  run_case terminal-state-failure \
    "printf ok > app/terminal-state.txt; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
terminal_rc=$?
terminal_lease="$(sed -n 's/^lease_expires: *//p' "$R/state/tasks/terminal-state-failure.md" | head -1)"
if [ "$terminal_rc" = 86 ] && [ "$(status_of terminal-state-failure)" = running ] \
   && printf '%s' "$terminal_lease" | grep -qE '^[1-9][0-9]*$' \
   && [ -d "$R/.worktrees/terminal-state-failure" ] \
   && [ ! -e "$NOTIFY_MARKER" ] && [ ! -e "$PUBLISH_MARKER" ]; then
  ok "failed canonical passed transition propagates and blocks publish/notify/cleanup"
else
  no "failed canonical passed transition was hidden (rc=$terminal_rc status=$(status_of terminal-state-failure) lease=${terminal_lease:-missing})"
fi

# 10b. A verifier rejection may terminalize only after its canonical escalation record is
# durable. An esc-record failure leaves the running task/worktree recoverable and sends nothing.
rm -f "$NOTIFY_MARKER" "$PUBLISH_MARKER"
mktask escalation-record-failure "test -s app/escalation-record.txt"
result="$(done_result escalation-record '["app/escalation-record.txt"]')"
rejecting_verifier='mkdir -p "$RECURSION_EVIDENCE_DIR"; printf "{\"verdict\":\"fail\",\"commit_oid\":\"%s\",\"implementer_run_id\":\"%s\",\"summary\":\"controlled rejection\",\"evidence\":[\"falsifier\"],\"risks\":[]}" "$RECURSION_VERIFICATION_COMMIT" "$RECURSION_IMPLEMENTER_RUN_ID" > "$RECURSION_EVIDENCE_DIR/verdict.json"'
RECURSION_TEST_NO_NOTIFY=0 RECURSION_TEST_ALLOW_PUSH=1 FAIL_ESC_RECORD=1 \
  TEST_NOTIFY_MARKER="$NOTIFY_MARKER" TEST_PUBLISH_MARKER="$PUBLISH_MARKER" \
  run_case escalation-record-failure \
    "printf ok > app/escalation-record.txt; printf '%s' '$result' > .recursion-result.json" "$rejecting_verifier"
escalation_rc=$?
if [ "$escalation_rc" = 85 ] && [ "$(status_of escalation-record-failure)" = running ] \
   && [ -d "$R/.worktrees/escalation-record-failure" ] \
   && [ ! -e "$NOTIFY_MARKER" ] && [ ! -e "$PUBLISH_MARKER" ]; then
  ok "failed canonical escalation record blocks terminal action success and notification"
else
  no "failed canonical escalation record was hidden (rc=$escalation_rc status=$(status_of escalation-record-failure))"
fi

# 10c. Once passed is durable it is the point of no return. PAUSE arriving at that exact seam
# suppresses sends/publication/cleanup but does not turn the completed action into a deferral;
# a subsequent invocation cannot launch the worker again.
rm -f "$NOTIFY_MARKER" "$PUBLISH_MARKER" "$R/state/PAUSE"
AFTER_TERMINAL_WORKER="$TMP/after-terminal-worker"
mktask pause-after-terminal "test -s app/pause-after-terminal.txt"
result="$(done_result pause-after-terminal '["app/pause-after-terminal.txt"]')"
RECURSION_TEST_NO_NOTIFY=0 RECURSION_TEST_ALLOW_PUSH=1 RECURSION_TEST_PAUSE_AFTER_TERMINAL=1 \
  TEST_NOTIFY_MARKER="$NOTIFY_MARKER" TEST_PUBLISH_MARKER="$PUBLISH_MARKER" \
  run_case pause-after-terminal \
    "printf 'run\\n' >> '$AFTER_TERMINAL_WORKER'; printf ok > app/pause-after-terminal.txt; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
after_terminal_rc=$?
RECURSION_TEST_NO_NOTIFY=0 TEST_NOTIFY_MARKER="$NOTIFY_MARKER" \
  run_case pause-after-terminal \
    "printf 'replay\\n' >> '$AFTER_TERMINAL_WORKER'" "$verdict_script"
after_terminal_replay_rc=$?
worker_launches="$(wc -l < "$AFTER_TERMINAL_WORKER" 2>/dev/null || echo 0)"
if [ "$after_terminal_rc" = 0 ] && [ "$after_terminal_replay_rc" = 75 ] \
   && [ "$(status_of pause-after-terminal)" = passed ] && [ "$worker_launches" = 1 ] \
   && [ -d "$R/.worktrees/pause-after-terminal" ] \
   && [ ! -e "$NOTIFY_MARKER" ] && [ ! -e "$PUBLISH_MARKER" ]; then
  ok "PAUSE after terminal pass preserves one success and suppresses send/publish/replay"
else
  no "post-terminal PAUSE changed outcome or leaked side effects (rc=$after_terminal_rc replay=$after_terminal_replay_rc status=$(status_of pause-after-terminal) launches=$worker_launches)"
fi
rm -f "$R/state/PAUSE"
mv "$R/scripts/taskctl.real.sh" "$R/scripts/taskctl.sh"

# 11. A heavy gate that cannot acquire the singleton capacity lock defers with rc75 and
# never executes its acceptance command without exclusivity.
mv "$R/scripts/capacity.sh" "$R/scripts/capacity.real.sh"
cat > "$R/scripts/capacity.sh" <<'SH'
#!/usr/bin/env bash
echo 'BUSY fixture-holder'
exit 75
SH
chmod +x "$R/scripts/capacity.sh"
mktask heavy-contention "test -s app/heavy.txt"
sed -i '/^gate_files:/i gate_class: heavy' "$R/state/tasks/heavy-contention.md"
result="$(done_result heavy '["app/heavy.txt"]')"
RECURSION_HEAVY_WAIT_S=0 run_case heavy-contention \
  "printf ok > app/heavy.txt; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
heavy_rc=$?
heavy_gate_evidence="$(grep -l '"machine_gate"' "$R/state/runs"/heavy-contention-impl-*.json 2>/dev/null || true)"
if [ "$heavy_rc" = 75 ] && [ "$(status_of heavy-contention)" = running ] \
   && [ -d "$R/.worktrees/heavy-contention" ] && [ -z "$heavy_gate_evidence" ]; then
  ok "contended heavy gate defers without executing unlocked"
else
  no "contended heavy gate did not fail closed (rc=$heavy_rc status=$(status_of heavy-contention) gate_evidence=$([ -n "$heavy_gate_evidence" ] && echo recorded || echo absent))"
fi
mv "$R/scripts/capacity.real.sh" "$R/scripts/capacity.sh"
mv "$R/scripts/notify.real.sh" "$R/scripts/notify.sh"
rm -f "$R/scripts/publish.sh"

# 12. The heavy-gate lock is exclusive for the GATE only. Every verify() releases it in all
# outcomes, so a passing heavy gate runs its independent verifier with the box-wide lock FREE,
# and a failing heavy gate can re-acquire for the one bounded retry instead of spinning on a
# lock this same process still holds.
export RECURSION_HEAVY_WAIT_S=0
LOCK_FREE_MARKER="$TMP/heavy-lock-free"
mktask heavy-pass "test -s app/heavy-pass.txt"
sed -i '/^gate_files:/i gate_class: heavy' "$R/state/tasks/heavy-pass.md"
result="$(done_result heavy-pass '["app/heavy-pass.txt"]')"
verifier_lock_check='h="$(RECURSION_ROOT="$RECURSION_ROOT" bash "$RECURSION_ROOT/scripts/capacity.sh" heavy status)"; [ "$h" = FREE ] && : > "$HEAVY_LOCK_FREE_MARKER"; '"$verdict_script"
HEAVY_LOCK_FREE_MARKER="$LOCK_FREE_MARKER" run_case heavy-pass \
  "printf ok > app/heavy-pass.txt; printf '%s' '$result' > .recursion-result.json" "$verifier_lock_check"
if [ "$(status_of heavy-pass)" = passed ] && [ -e "$LOCK_FREE_MARKER" ]; then
  ok "heavy gate releases the box-wide lock before the independent verifier"
else
  no "heavy lock was still held across the independent verifier (status=$(status_of heavy-pass) lock_free=$([ -e "$LOCK_FREE_MARKER" ] && echo yes || echo no))"
fi

RETRY_LAUNCHES="$TMP/heavy-retry-launches"
mktask heavy-retry "if [ -e app/retry-second.txt ]; then exit 0; else exit 1; fi"
sed -i '/^gate_files:/i gate_class: heavy' "$R/state/tasks/heavy-retry.md"
first_result='{"status":"done","summary":"first heavy attempt","files_changed":["app/heavy-retry.txt"],"tests_run":"fixture gate","risks":[],"blocker":""}'
second_result='{"status":"done","summary":"second heavy attempt","files_changed":["app/heavy-retry.txt","app/retry-second.txt"],"tests_run":"fixture gate","risks":[],"blocker":""}'
RETRY_LAUNCHES="$RETRY_LAUNCHES" run_case heavy-retry "n=\$(wc -l < \"\$RETRY_LAUNCHES\" 2>/dev/null || echo 0); n=\$((n+1)); echo \"launch \$n\" >> \"\$RETRY_LAUNCHES\"; if [ \"\$n\" = 1 ]; then printf ok > app/heavy-retry.txt; printf '%s' '$first_result' > .recursion-result.json; else printf ok > app/heavy-retry.txt; printf ok > app/retry-second.txt; printf '%s' '$second_result' > .recursion-result.json; fi" "$verdict_script"
heavy_retry_launches="$(wc -l < "$RETRY_LAUNCHES" 2>/dev/null || echo 0)"
if [ "$(status_of heavy-retry)" = passed ] && [ "$heavy_retry_launches" = 2 ]; then
  ok "a failed heavy gate releases its lock so the one bounded retry reruns"
else
  no "heavy retry could not re-acquire after the failed gate (status=$(status_of heavy-retry) launches=$heavy_retry_launches)"
fi

mv "$R/scripts/capacity.sh" "$R/scripts/capacity.release-real.sh"
cat > "$R/scripts/capacity.sh" <<'SH'
#!/usr/bin/env bash
case "${1:-}:${2:-}" in
  heavy:acquire) echo 'ACQUIRED release-failure-fixture'; exit 0 ;;
  heavy:release) exit 76 ;;
  heavy:status) echo 'HELD release-failure-fixture'; exit 0 ;;
esac
exit 4
SH
chmod +x "$R/scripts/capacity.sh"
RELEASE_FAIL_LAUNCHES="$TMP/heavy-release-fail-launches"
mktask heavy-release-fail "test -s app/heavy-release-fail.txt"
sed -i '/^gate_files:/i gate_class: heavy' "$R/state/tasks/heavy-release-fail.md"
result="$(done_result heavy-release-fail '["app/heavy-release-fail.txt"]')"
RELEASE_FAIL_LAUNCHES="$RELEASE_FAIL_LAUNCHES" run_case heavy-release-fail \
  "printf 'launch\n' >> '$RELEASE_FAIL_LAUNCHES'; printf ok > app/heavy-release-fail.txt; printf '%s' '$result' > .recursion-result.json" \
  "$verdict_script"
heavy_release_rc=$?
heavy_release_launches="$(wc -l < "$RELEASE_FAIL_LAUNCHES" 2>/dev/null || echo 0)"
if [ "$heavy_release_rc" = 76 ] && [ "$(status_of heavy-release-fail)" = running ] \
   && [ "$heavy_release_launches" = 1 ]; then
  ok "heavy lock release failure stops before retry/verifier/later actuation"
else
  no "heavy lock release failure was hidden or retried (rc=$heavy_release_rc status=$(status_of heavy-release-fail) launches=$heavy_release_launches)"
fi
mv "$R/scripts/capacity.release-real.sh" "$R/scripts/capacity.sh"
unset RECURSION_HEAVY_WAIT_S LOCK_FREE_MARKER RETRY_LAUNCHES

# 13. Gate rc=2 is treated as unchanged no-progress ONLY when BASE_COMMIT == CANDIDATE_OID.
# A changed rc2 candidate (the arm committed something) is "tried but failed" and gets the one
# bounded retry; a genuinely unchanged rc2 candidate is a deliberate no-op and does not.
RC2_LAUNCHES="$TMP/rc2-changed-launches"
mktask rc2-changed "if [ -e app/rc2-second.txt ]; then exit 0; else exit 2; fi"
first_rc2='{"status":"done","summary":"changed rc2 attempt","files_changed":["app/rc2-changed.txt"],"tests_run":"fixture gate","risks":[],"blocker":""}'
second_rc2='{"status":"done","summary":"changed rc2 second","files_changed":["app/rc2-changed.txt","app/rc2-second.txt"],"tests_run":"fixture gate","risks":[],"blocker":""}'
RC2_LAUNCHES="$RC2_LAUNCHES" run_case rc2-changed "n=\$(wc -l < \"\$RC2_LAUNCHES\" 2>/dev/null || echo 0); n=\$((n+1)); echo \"launch \$n\" >> \"\$RC2_LAUNCHES\"; if [ \"\$n\" = 1 ]; then printf ok > app/rc2-changed.txt; printf '%s' '$first_rc2' > .recursion-result.json; else printf ok > app/rc2-changed.txt; printf ok > app/rc2-second.txt; printf '%s' '$second_rc2' > .recursion-result.json; fi" "$verdict_script"
rc2_launches="$(wc -l < "$RC2_LAUNCHES" 2>/dev/null || echo 0)"
if [ "$(status_of rc2-changed)" = passed ] && [ "$rc2_launches" = 2 ]; then
  ok "a changed rc2 candidate receives the one bounded retry"
else
  no "a changed rc2 candidate was misread as no-progress (status=$(status_of rc2-changed) launches=$rc2_launches)"
fi

NOOP_LAUNCHES="$TMP/rc2-noop-launches"
mktask rc2-noop "if [ -e app/rc2-noop.txt ]; then exit 0; else exit 2; fi" optional
noop_result='{"status":"no-op","summary":"deliberate no progress","files_changed":[],"tests_run":"fixture gate","risks":[],"blocker":""}'
NOOP_LAUNCHES="$NOOP_LAUNCHES" run_case rc2-noop "n=\$(wc -l < \"\$NOOP_LAUNCHES\" 2>/dev/null || echo 0); n=\$((n+1)); echo \"launch \$n\" >> \"\$NOOP_LAUNCHES\"; printf '%s' '$noop_result' > .recursion-result.json"
rc2_noop_launches="$(wc -l < "$NOOP_LAUNCHES" 2>/dev/null || echo 0)"
if [ "$(status_of rc2-noop)" = failed ] && [ "$rc2_noop_launches" = 1 ]; then
  ok "an unchanged rc2 candidate (base==candidate) is a deliberate no-op with no retry"
else
  no "an unchanged rc2 no-progress was retried (status=$(status_of rc2-noop) launches=$rc2_noop_launches)"
fi
unset RC2_LAUNCHES NOOP_LAUNCHES

echo
[ "$fails" -eq 0 ] && { echo "hermes-pilot-phase5-red: ALL PASS"; exit 0; }
echo "hermes-pilot-phase5-red: $fails FAILED (expected on the pre-Phase 5 base)"; exit 1

#!/usr/bin/env bash
# Phase 5 falsifiers: strict worker envelopes, complete scope evidence, timeout/lease handling,
# and exact-commit independent verification. Hermetic: no model, network, publisher, or live state.
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/bin"; R="$TMP/controller"; ORIGIN="$TMP/origin.git"
mkdir -p "$BIN" "$R/scripts/tests" "$R/state/tasks" "$R/state/runs" \
  "$R/loop/logs" "$R/app" "$R/fixtures" "$R/other"
for s in work.sh worker-sandbox.sh taskctl.sh board.sh notify.sh resync.sh capacity.sh \
         git-scope.py validate-gate.py validate-worker-result.py worker-evidence.py; do
  [ ! -f "$SRC/scripts/$s" ] || cp "$SRC/scripts/$s" "$R/scripts/"
done
chmod +x "$R/scripts/"* 2>/dev/null || true
printf 'protected\n' > "$R/scripts/protected.sh"
printf 'test\n' > "$R/scripts/tests/existing.test.cjs"
printf '{"truth":1}\n' > "$R/fixtures/truth.json"
printf 'seed\n' > "$R/app/seed.txt"
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
pilot_id: pilot-phase5
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
  ( cd "$R" && PATH="$BIN:$PATH" RECURSION_ROOT="$R" RECURSION_NO_NOTIFY=1 \
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

# 1. A worker-created commit must not hide a protected-file change from scope verification.
MARKER1="$TMP/gate-committed-protected"
mktask committed-protected "test -s app/committed.txt && touch $MARKER1"
result="$(done_result committed '["app/committed.txt","scripts/protected.sh"]')"
run_case committed-protected "printf ok > app/committed.txt; printf evil > scripts/protected.sh; printf '%s' '$result' > .recursion-result.json; git add -A; git -c user.name=arm -c user.email=arm@t commit -qm hidden"
if [ "$(status_of committed-protected)" != passed ] && [ ! -e "$MARKER1" ]; then
  ok "committed protected-file mutation is rejected before its gate"
else
  no "a committed protected-file mutation was hidden (status=$(status_of committed-protected) gate=$([ -e "$MARKER1" ] && echo ran || echo blocked))"
fi

# 2. One committed change set exercises test, fixture rename/delete, and out-of-scope paths.
MARKER2="$TMP/gate-committed-mutations"
mktask committed-mutations "test -s app/mutations.txt && touch $MARKER2"
result="$(done_result mutations '["app/mutations.txt","scripts/tests/existing.test.cjs","fixtures/truth.json","app/truth-moved.json","other/stray.txt"]')"
run_case committed-mutations "printf ok > app/mutations.txt; printf evil >> scripts/tests/existing.test.cjs; git mv fixtures/truth.json app/truth-moved.json; printf stray > other/stray.txt; printf '%s' '$result' > .recursion-result.json; git add -A; git -c user.name=arm -c user.email=arm@t commit -qm hidden"
if [ "$(status_of committed-mutations)" != passed ] && [ ! -e "$MARKER2" ]; then
  ok "committed test/fixture/rename/delete/out-of-scope mutations are rejected"
else
  no "committed mutation set passed or reached its gate (status=$(status_of committed-mutations))"
fi

# 3. Generated work without the required result contract must fail closed.
mktask missing-result "test -s app/missing-result.txt"
run_case missing-result 'printf ok > app/missing-result.txt' "$verdict_script"
[ "$(status_of missing-result)" != passed ] \
  && ok "missing worker result cannot pass" \
  || no "generated work passed without a result report"

# 4. A no-op cannot satisfy an explicitly non-vacuous implementation task.
mktask nonvacuous-noop "test -s app/seed.txt"
noop='{"status":"no-op","summary":"nothing changed","files_changed":[],"tests_run":"fixture gate","risks":[],"blocker":""}'
run_case nonvacuous-noop "printf '%s' '$noop' > .recursion-result.json" "$verdict_script"
[ "$(status_of nonvacuous-noop)" != passed ] \
  && ok "no-op is rejected for a task that requires a change" \
  || no "a no-op passed a non-vacuous implementation task"

# 5. Structurally vacuous and worker-modifiable gates must both fail closed.
mktask vacuous-gate true
result="$(done_result vacuous '["app/vacuous.txt"]')"
run_case vacuous-gate "printf ok > app/vacuous.txt; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
[ "$(status_of vacuous-gate)" != passed ] \
  && ok "literal true gate is rejected as structurally vacuous" \
  || no "literal true was accepted as an autonomy gate"

mktask self-modified-gate "bash app/gate.sh" required app/gate.sh
result="$(done_result selfgate '["app/gate.sh"]')"
run_case self-modified-gate "printf '#!/usr/bin/env bash\nexit 0\n' > app/gate.sh; chmod +x app/gate.sh; printf '%s' '$result' > .recursion-result.json" "$verdict_script"
[ "$(status_of self-modified-gate)" != passed ] \
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
if [ "$(status_of hung-worker)" != passed ] && [ "$lease" = 0 ] && [ "$timeout_count" = 1 ] \
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
           and ver[0].get('verification',{}).get('verdict')=='pass')
raise SystemExit(0 if valid else 1)
PY
then
  ok "implementer and verifier are independent runs bound to one exact commit"
else
  no "independent exact-commit verification evidence is absent or inconsistent"
fi

# 8. A verifier that mutates its isolated checkout cannot silently certify the implementation.
mktask verifier-mutation "test -s app/verifier-mutation.txt"
result="$(done_result verifier '["app/verifier-mutation.txt"]')"
mutating_verifier='printf evil > app/verifier-mutation.txt; '"$verdict_script"
run_case verifier-mutation "printf original > app/verifier-mutation.txt; printf '%s' '$result' > .recursion-result.json" "$mutating_verifier"
branch_value="$(git -C "$R" show loop/work/verifier-mutation:app/verifier-mutation.txt 2>/dev/null || true)"
if [ "$(status_of verifier-mutation)" != passed ] && [ "$branch_value" = original ]; then
  ok "verifier mutation is rejected and cannot alter implementer output"
else
  no "verifier mutation was silent (status=$(status_of verifier-mutation) implementer_output=${branch_value:-missing})"
fi

echo
[ "$fails" -eq 0 ] && { echo "hermes-pilot-phase5-red: ALL PASS"; exit 0; }
echo "hermes-pilot-phase5-red: $fails FAILED (expected on the pre-Phase 5 base)"; exit 1

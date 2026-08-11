#!/usr/bin/env bash
# Positive Phase 5 artifact/evidence audit. Hermetic: no model, network, publisher, or live state.
set -euo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$ROOT"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

bash -n scripts/work.sh scripts/worker-sandbox.sh scripts/tests/hermes-pilot-phase5-red.test.sh \
  scripts/tests/worker-gate-authority.test.sh
python3 -m py_compile scripts/resolve-model-alias.py scripts/validate-gate.py scripts/git-scope.py \
  scripts/validate-worker-result.py scripts/validate-verifier-result.py scripts/worker-evidence.py \
  scripts/validate-control-state.py scripts/project-pilot.py scripts/jsonl_durable.py scripts/transition_receipt.py
echo "ok    Phase 5 shell and Python artifacts parse"

if python3 scripts/resolve-model-alias.py sonnet-routine implementer >/dev/null 2>&1; then
  echo "FAIL model alias resolved without a human-owned mapping"; exit 1
fi
[ "$(RECURSION_MODEL_ALIAS_SONNET_ROUTINE=reviewed-sonnet \
  python3 scripts/resolve-model-alias.py sonnet-routine implementer)" = reviewed-sonnet ]
if RECURSION_MODEL_ALIAS_SONNET_ROUTINE=reviewed-sonnet \
    python3 scripts/resolve-model-alias.py sonnet-routine verifier >/dev/null 2>&1; then
  echo "FAIL implementer alias was accepted for verifier"; exit 1
fi
! rg -n --glob '*.py' --glob '*.sh' 'claude-(sonnet|opus)-[0-9]' scripts >/dev/null
echo "ok    model aliases resolve only through human-owned role mappings; no version is hardcoded"

G="$TMP/gate"; mkdir -p "$G/app"; git -c init.defaultBranch=main init -q "$G"
printf '#!/usr/bin/env bash\nexit 0\n' > "$G/app/gate.sh"; chmod +x "$G/app/gate.sh"
git -C "$G" add -A; git -C "$G" -c user.name=t -c user.email=t@t commit -qm init
if python3 scripts/validate-gate.py --acceptance true --allowed-paths app --repo "$G" >/dev/null 2>&1; then
  echo "FAIL literal true gate passed"; exit 1
fi
python3 scripts/validate-gate.py --acceptance 'test -s app/output.txt' --allowed-paths app --repo "$G" >/dev/null
python3 scripts/validate-gate.py --acceptance 'bash app/gate.sh' --allowed-paths app \
  --gate-files app/gate.sh --repo "$G" > "$TMP/gate-contract.json"
python3 - "$TMP/gate-contract.json" <<'PY'
import json,sys
value=json.load(open(sys.argv[1])); assert len(value['acceptance_sha256'])==64
assert len(value['gate_files']['app/gate.sh'])==64
PY
echo "ok    non-vacuous gates and immutable gate-file fingerprints validate"

S="$TMP/scope"; mkdir -p "$S/app"; git -c init.defaultBranch=main init -q "$S"
printf base > "$S/app/base"; printf rename > "$S/app/rename"; printf delete > "$S/app/delete"
git -C "$S" add -A; git -C "$S" -c user.name=t -c user.email=t@t commit -qm base
base="$(git -C "$S" rev-parse HEAD)"
printf committed > "$S/app/committed"; git -C "$S" add app/committed
git -C "$S" -c user.name=t -c user.email=t@t commit -qm committed
git -C "$S" mv app/rename app/renamed; git -C "$S" rm -q app/delete
printf staged > "$S/app/staged"; git -C "$S" add app/staged
printf changed >> "$S/app/base"; printf untracked > "$S/app/untracked"
python3 scripts/git-scope.py --repo "$S" --base "$base" --allowed-paths app --check > "$TMP/scope.json"
python3 - "$TMP/scope.json" <<'PY'
import json,sys
value=json.load(open(sys.argv[1])); sources={entry['source'] for entry in value['entries']}
assert {'base..HEAD','staged','unstaged','untracked'} <= sources
statuses={entry['status'][0] for entry in value['entries']}; assert {'A','M','R','D'} <= statuses
assert value['protected_paths']==[] and value['outside_paths']==[]
PY
echo "ok    scope evidence covers base..HEAD, staged, unstaged, untracked, rename, and delete state"

python3 - "$TMP/task.json" "$TMP/run.json" <<'PY'
import json,sys
task={'schema_version':1,'id':'t','goal_id':'g','dependencies':[],'allowed_paths':['app'],
      'non_goals':['tests'],'worker_class':'claude','acceptance':'test -s app/out','status':'ready',
      'model_alias':'sonnet-routine','verifier_model_alias':'opus-review','deadline_seconds':60,
      'verifier_deadline_seconds':60,'network_policy':'provider-only','evidence_contract':'worker-result-v1',
      'verification':'independent','expected_change':'required','gate_files':[]}
run={'schema_version':1,'id':'r','task_id':'t','worker':'implementer:sonnet-routine','role':'implementer',
     'model_alias':'sonnet-routine','network_policy':'provider-only','worktree':'/tmp/w',
     'base_commit':'0'*40,'pid':1,'process_group':1,'lease_expires':'later','deadline':'later',
     'usage':{},'result':{},'status':'running'}
json.dump(task,open(sys.argv[1],'w')); json.dump(run,open(sys.argv[2],'w'))
PY
python3 scripts/validate-control-state.py task "$TMP/task.json" >/dev/null
python3 scripts/validate-control-state.py run "$TMP/run.json" >/dev/null
for phrase in 'model_alias: sonnet-routine' 'verifier_model_alias: opus-review' \
  'evidence_contract: worker-result-v1' 'verification: independent'; do
  grep -qF "$phrase" scripts/project-pilot.py
done
grep -q 'BindReadOnlyPaths=.*:/workspace' scripts/worker-sandbox.sh
grep -q 'PrivateNetwork=yes' scripts/worker-sandbox.sh
echo "ok    pilot tasks, run schemas, read-only verification, and network policy are explicit"

bash scripts/tests/hermes-pilot-phase5-red.test.sh
bash scripts/tests/worker-gate-authority.test.sh
echo "hermes-pilot-phase5-green: ALL PASS"

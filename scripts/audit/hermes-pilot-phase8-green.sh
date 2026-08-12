#!/usr/bin/env bash
# Positive architecture audit for Phase 8 observed project pilots.
set -euo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$ROOT"

bash -n scripts/conduct-hermes.sh scripts/hermes-actuator.sh scripts/hermes-decide.sh \
  scripts/assist.sh scripts/taskctl.sh scripts/work.sh scripts/notify.sh scripts/digest.sh \
  scripts/cycle.sh loop/supervisor/run.sh scripts/tests/hermes-pilot-phase8-red.test.sh
python3 -m py_compile scripts/project-pilot.py scripts/project-reconcile.py scripts/decision-queue.py \
  scripts/notification-outbox.py scripts/jsonl_durable.py scripts/transition_receipt.py scripts/validate-decision.py scripts/validate-control-state.py \
  scripts/runtime-state.py scripts/tests/hermes-pilot-phase8-red.py \
  scripts/tests/hermes-pilot-phase8-parallel.py \
  scripts/tests/hermes-pilot-phase8-legacy-journal-red.py \
  scripts/tests/hermes-pilot-phase8-notification-red.py scripts/tests/jsonl-durability.test.py \
  scripts/tests/decision-identity.test.py scripts/tests/runtime-state-locks.test.py \
  scripts/tests/runtime-state-recovery.test.py scripts/tests/reconcile-liveness.test.py \
  scripts/tests/transition-receipt.test.py scripts/tests/notification-transition-receipt.test.py
python3 - <<'PY'
import json
json.load(open('schemas/control-plane/v1/schema.json',encoding='utf-8'))
PY
echo "ok    Phase 8 shell, Python, and schema artifacts parse"

for verb in pilot-plan-propose pilot-plan-approve pilot-window-open pilot-window-close; do
  grep -q "$verb" scripts/hermes-decide.sh
  grep -q "$verb" scripts/validate-decision.py
  grep -q "$verb" scripts/conduct-hermes.sh
done
grep -q 'canonical_digest(plan)' scripts/project-pilot.py
grep -q 'fresh pilot plan reuses an existing goal id' scripts/project-pilot.py
grep -q 'Lucas instruction does not name the exact Phase 8 object' scripts/project-pilot.py
echo "ok    fresh synthesis, schema bounds, collision refusal, and exact Lucas digest/window approval are mechanical"

grep -q 'build_pilot_brief' scripts/hermes-decide.sh
grep -q 'RECURSION_PILOT_MODEL' scripts/hermes-decide.sh
grep -q 'DECIDER_ACTOR="$route"' scripts/hermes-decide.sh
grep -q 'approve.*plan' scripts/intake.sh
echo "ok    event-invoked logical GPT pilots receive a scoped brief and approval/assist authority routes to Head Hermes"

grep -q 'a pilot window may be authorized only while PAUSE is observed' scripts/project-pilot.py
grep -q 'exact open pilot window authority is absent' scripts/project-reconcile.py
grep -q 'close-paused-windows' scripts/hermes-actuator.sh
grep -q 'admit-work' scripts/conduct-hermes.sh
echo "ok    exact-goal admission is rechecked at actuation and PAUSE revokes stale authority"

# The machinery admitting six verbs under PAUSE is worthless if the prompt tells the model only
# one of them exists. It did, for four days: every decide run chose noop citing "no
# execution-capable verb is permitted", which is the RUNTIME/PAUSE block quoted back verbatim.
# A paused box must still be able to PROPOSE a plan -- that is the whole of gate 5.
# NOTE: there are two RUNTIME/PAUSE blocks. The first belongs to build_pilot_brief and is
# correct as written ("no worker may run"); this asserts only the Head Hermes one, anchored on
# text unique to it.
PAUSE_BLOCK="$(awk '/REMAIN EXECUTABLE while paused/{f=1} f{print} f&&/cat state\/PAUSE/{exit}' \
  scripts/hermes-decide.sh)"
[ -n "$PAUSE_BLOCK" ]
for verb in noop pilot-plan-propose pilot-plan-approve pilot-window-open pilot-window-close assist-answer; do
  printf '%s\n' "$PAUSE_BLOCK" | grep -q -- "$verb"
done
# Matched against the pre-fix bytes: the stale claim wrapped across two echo lines, so a grep
# spanning "the only executable verb" could never match and would have passed vacuously.
! grep -q "executable verb while paused is 'noop'" scripts/hermes-decide.sh
echo "ok    the paused Head Hermes prompt names every PAUSE-safe verb and claims no others"

# 'goal' is normalized into goal_id, which must be a canonical identifier. Every decision from
# 2026-08-07 to 2026-08-10 was discarded at normalize with "goal_id is not a canonical
# identifier" because the model wrote a purpose sentence there. The rejection is silent from the
# operator's side -- the run simply produces nothing -- so the constraint must be in the prompt.
grep -q 'goal.\+MUST BE AN IDENTIFIER, never a sentence' scripts/hermes-decide.sh
grep -qF '^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$' scripts/hermes-decide.sh
echo "ok    the decision prompt states the goal identifier constraint that normalization enforces"

# The prompt is one double-quoted shell string, so anything the shell expands inside it is
# deleted from what the model reads. Backticks around two verb names silently emptied them:
# the model received "only Lucas can, on GitHub.  prepares a repo and  completes it". Guard the
# CLASS, not those two words -- the only substitution the prompt may contain is $(build_brief).
python3 - <<'PY'
import re, sys
lines = open('scripts/hermes-decide.sh', encoding='utf-8').read().split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('PROMPT="'))
end = next(i for i, l in enumerate(lines) if l.strip() == '$(build_brief)"')
body = lines[start:end + 1]
bad = [(start + i + 1, l) for i, l in enumerate(body) if '`' in l]
subs = [(start + i + 1, m) for i, l in enumerate(body) for m in re.findall(r'\$\([^)]*\)', l)]
unexpected = [(n, m) for n, m in subs if m != '$(build_brief)']
if bad or unexpected:
    for n, l in bad:
        print('FAIL backtick in prompt line %d: %s' % (n, l.strip()[:90]), file=sys.stderr)
    for n, m in unexpected:
        print('FAIL unexpected substitution in prompt line %d: %s' % (n, m), file=sys.stderr)
    raise SystemExit(1)
PY
echo "ok    the prompt string contains no shell expansion that would delete its own text"

# conduct-hermes.sh takes this same lock on fd 8 and the actuator runs it on a 2s poll, so a
# single non-blocking attempt loses roughly a third of all scheduled decision turns. Production
# measured the lock held for 18 of 60 half-second samples.
grep -qE '^flock -w "\$CONTROL_LOCK_WAIT_S" 9' scripts/hermes-decide.sh
! grep -qE '^flock -n 9' scripts/hermes-decide.sh
grep -q 'RECURSION_CONTROL_LOCK_WAIT_S' scripts/hermes-decide.sh
echo "ok    the decision turn waits for the shared control lock instead of failing on first contention"

# A systemd service inherits no HOME. Under `set -u` an unguarded $HOME is a fatal error on the
# FIRST line that mentions it, before any subcommand runs -- so the script is not "degraded", it
# is entirely dead, and only under systemd. intake.sh was dead this way for the whole life of
# hermes-actuator.service while every suite stayed green, because no test ran without HOME.
# Guard the class: branch-review.sh had already been fixed for this once, and resync.sh carried
# the same latent defect, which is the signature of something that comes back.
python3 - <<'PY'
import glob, re, sys
bad = []
# ONE glob: scripts/*.sh and scripts/**/*.sh overlap and reported every top-level script twice.
for path in sorted(set(glob.glob('scripts/**/*.sh', recursive=True))):
    text = open(path, encoding='utf-8', errors='replace').read()
    if not re.search(r'(?m)^set -[a-z]*u', text):
        continue
    uses = [n for n, line in enumerate(text.split('\n'), 1)
            if re.search(r'\$\{?HOME\b', line) and not line.lstrip().startswith('#')]
    if not uses:
        continue
    if not re.search(r'HOME="\$\{HOME:-', text):
        bad.append((path, uses[:3]))
for path, lines in bad:
    print('FAIL unguarded HOME under set -u: %s lines %s' % (path, lines), file=sys.stderr)
if bad:
    raise SystemExit(1)
PY
echo "ok    no set -u script dereferences HOME unguarded (systemd services have none)"

# THE PROMPT MUST TEACH WHAT THE VALIDATOR ENFORCES. Rehearsed against the live model: every
# rejected plan failed on a literal the prompt never stated. "complete Phase 6 budget" did not
# name the nine budget keys, so the model wrote prose. The prompt said "deadlines" and
# "independent verification" -- not the key names -- and the model copied them. Six fields are
# enum-constrained and the prompt listed no values, so the model guessed plausibly and wrongly
# every time (model_alias "claude", verifier_model_alias "codex", network_policy "offline-deny").
#
# Read the contract out of validate_plan's AST rather than spot-checking today's strings, so a
# field added to the validator fails this audit until the prompt teaches it.
python3 - <<'PY'
import ast, sys

src = open('scripts/project-pilot.py', encoding='utf-8').read()
fn = next(n for n in ast.walk(ast.parse(src))
          if isinstance(n, ast.FunctionDef) and n.name == 'validate_plan')

def strings(node):
    if isinstance(node, ast.Set):
        return {e.value for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)}
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    return set()

required = set()
for node in ast.walk(fn):
    # required = {...} and required_budget = {...}
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in ('required', 'required_budget'):
                required |= strings(node.value)
    # task.get("field") != "value"   /   task.get("field") not in {"a", "b"}
    if isinstance(node, ast.Compare):
        left = node.left
        if (isinstance(left, ast.Call) and isinstance(left.func, ast.Attribute)
                and left.func.attr == 'get'
                and isinstance(left.func.value, ast.Name) and left.func.value.id == 'task'
                and left.args and isinstance(left.args[0], ast.Constant)):
            required.add(left.args[0].value)
            for comparator in node.comparators:
                required |= strings(comparator)

prompt = open('scripts/hermes-decide.sh', encoding='utf-8').read()
missing = sorted(term for term in required if term not in prompt)
if missing:
    print('FAIL the plan prompt never states %d enforced literal(s): %s'
          % (len(missing), ', '.join(missing)), file=sys.stderr)
    raise SystemExit(1)
print('    (%d enforced literals, all present in the prompt)' % len(required))
PY
echo "ok    the plan prompt states every key and enum value that validate_plan enforces"

# A caller-supplied RECURSION_ROOT must survive .env. These scripts compute ROOT from
# ${RECURSION_ROOT:-<script dir>} and THEN source .env with `set -a`; production's .env pins
# RECURSION_ROOT=/opt/recursion, so from that line on the shell's ROOT and the exported
# RECURSION_ROOT disagree, and every python child reads the environment. On 2026-08-12 that made
# rehearsals run against a copy enqueue TEN decisions into production, with nothing to warn:
# the parent's own file writes went to the copy, so the split was invisible until the live queue
# was inspected. ROOT and RECURSION_ROOT must agree after .env is sourced.
python3 - <<'PY'
import glob, re, sys
# Assembled, not spelled: a checker that writes out its own pattern matches itself.
ENV_SRC = re.compile(r'^\[ -f \.env \]', re.M)
ROOT_FROM_ENV = '{RECURSION_ROOT:-'
REASSERT = 'RECURSION_ROOT="' + '$ROOT"; export RECURSION_ROOT'
bad = []
for path in sorted(set(glob.glob('scripts/**/*.sh', recursive=True))):
    text = open(path, encoding='utf-8', errors='replace').read()
    m = ENV_SRC.search(text)
    if not m or ROOT_FROM_ENV not in text:
        continue
    tail = text[m.end():]
    if REASSERT not in tail:
        bad.append(path)
for path in bad:
    print('FAIL %s sources .env without re-asserting the caller root after it' % path,
          file=sys.stderr)
if bad:
    raise SystemExit(1)
print('    (every .env-sourcing script re-asserts the caller root)')
PY
echo "ok    sourcing .env cannot retarget a caller-supplied root"

grep -q 'claim-pending --kind work' scripts/conduct-hermes.sh
grep -q 'RECURSION_PILOT_GLOBAL_CONCURRENCY' scripts/conduct-hermes.sh
grep -q -- '--exclude-project' scripts/conduct-hermes.sh
grep -q 'concurrency_limit' scripts/project-reconcile.py
grep -q 'max_inflight_workers' scripts/project-reconcile.py
echo "ok    the sole actuator enforces global and per-project worker capacity without a second executor"

grep -q 'resume-assist' scripts/assist.sh
grep -q 'resume_assist' scripts/project-reconcile.py
grep -q 'resume_event_id' scripts/project-reconcile.py
grep -q 'DURABLE_REPORTING' scripts/assist.sh
grep -q 'PILOT_ID' scripts/work.sh
grep -q 'assist-open' scripts/notification-outbox.py
grep -q 'assist-answer' scripts/notification-outbox.py
echo "ok    one answered assist reopens the same goal/task and all pilot notices use the Phase 7 outbox"

for state_path in state/decisions.jsonl state/decision-queue state/goals state/tasks state/assists \
  state/plans state/pilot-windows state/jsonl-quarantine; do
  grep -qF "\"$state_path\"" scripts/runtime-state.py
done
for ignored in state/plans state/pilot-windows state/jsonl-quarantine state/jsonl-index; do grep -qF "$ignored/" .gitignore; done
echo "ok    plan/window/queue/goal/task/assist state is backup-covered and runtime projections stay untracked"

grep -q 'read_jsonl_since' scripts/decision-queue.py
grep -q 'validate_projection_authority' scripts/decision-queue.py
grep -q 'INDEX_AUTHORITY = "jsonl-verification-index-v1"' scripts/jsonl_durable.py
echo "ok    decision/event journals use durable tail verification and claims rebind to journal authority"

for event in plan-proposed plan-approved pilot-window-armed pilot-window-opened pilot-window-closed \
  lucas-attention-required human-answer-received; do
  grep -q "$event" scripts/notification-outbox.py
done
grep -q 'source-plan-proposed-' scripts/project-pilot.py
grep -q 'source-assist-' scripts/project-reconcile.py
echo "ok    stable source-event identities feed exact-once Phase 7 delivery policy"

grep -q 'LEGACY_PRE_SCHEMA_NOOP_SHA256' scripts/decision-queue.py
grep -q 'reviewed-pre-schema-noop' scripts/decision-queue.py
grep -q 'decision journal import failed rc=' scripts/conduct-hermes.sh
grep -q 'PAUSE-safe queue pass failed rc=' scripts/hermes-actuator.sh
echo "ok    exact reviewed legacy noops are non-executable and journal failures are observable"

grep -q 'PAUSE asserted; transport refused' scripts/notify.sh
grep -q 'notify-event portfolio-brief' loop/supervisor/run.sh
grep -q 'notify-event project-digest' scripts/digest.sh
! grep -q 'notify.sh' scripts/digest.sh
grep -q 'paused: skipping per-project notification enqueue' scripts/cycle.sh
grep -q 'state/.board.tsv state/events.jsonl' scripts/cycle.sh
for event in portfolio-brief project-digest; do grep -q "$event" scripts/notification-outbox.py; done
echo "ok    PAUSE interlocks the sole sender and resumed brief/digest delivery enters the Phase 7 outbox"

bash scripts/tests/hermes-pilot-phase8-red.test.sh
python3 scripts/tests/hermes-pilot-phase8-notification-red.py
python3 scripts/tests/decision-identity.test.py
python3 scripts/tests/jsonl-durability.test.py
python3 scripts/tests/runtime-state-locks.test.py
python3 scripts/tests/runtime-state-recovery.test.py
python3 scripts/tests/reconcile-liveness.test.py
python3 scripts/tests/transition-receipt.test.py
python3 scripts/tests/notification-transition-receipt.test.py
echo "hermes-pilot-phase8-green: ALL PASS"

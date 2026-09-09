"""Freeze Owner activation and baseline inputs; no model execution."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / 'docs/v3/construction/cut-source-overnight-20260908'
PREP = ROOT.parent / 'recursion-v3-overnight-handoff-20260908/docs/v3/construction/overnight-research-20260908'
BASE = 'ec4232e95722d58dc0eff03289fb629b58d29247'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')

def main():
    common = Path(git('rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip())
    external = common / 'research-attestations/cut-source-overnight'
    activation = external / 'activation.json'
    if activation.exists():
        raise SystemExit('Activation exists: reuse original clock, never overwrite or restart it')
    assert git('rev-parse', 'HEAD').decode().strip() == BASE
    assert not (ROOT / 'state/PAUSE').exists() and not (common.parent / 'state/PAUSE').exists()
    assert 'status: active' in (ROOT / 'state/goals/goal-recursion-v2-execution-fabric.md').read_text()
    proposal = read(PREP / 'goal-proposal.json')
    goal = dict(proposal, status='active-preflight-in-progress', start_commit=BASE,
                activation_start_commit=BASE, started_at='2026-09-09T03:40:33Z',
                deadline_utc='2026-09-09T15:40:33Z', discovery_cutoff_utc='2026-09-09T12:40:33Z',
                owner_approval='Explicit Lucas activation in task 01a0843f-abd7-79c3-bc3c-c1cba4c7b4c3; 2026-09-09T03:40:33Z initial clock',
                branch='codex/v3-cut-source-overnight-20260908', worktree=str(ROOT),
                preparation_commit='ab9fbd7525849a75ac13443ed5a37683a4d570b6')
    receipt = dict(goal=goal, recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   approved_packet={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in PREP.iterdir() if p.is_file()},
                   usage={'used_percent':31, 'remaining_percent':69, 'shared_account':True, 'resets_used':0, 'new_metered_spend':0},
                   publication_method='Previously approved normal non-force codex review publication; legacy loop publisher/config unchanged; draft PR master; Lucas merges')
    write(activation, receipt)
    write(DOC / 'goal.json', goal)
    write(DOC / 'activation.json', {'external_path':str(activation), 'sha256':hashlib.sha256(activation.read_bytes()).hexdigest(), **receipt})
    write(DOC / 'research-queue.json', read(PREP / 'research-queue.json'))
    prior = ROOT / 'docs/v3/construction/cut-publication-20260908'
    inputs = {x['path'] for x in read(prior / 'manifest.json')['inputs']}
    inputs.update(git('diff','--name-only',read(prior/'goal.json')['start_commit'],BASE).decode().splitlines())
    write(DOC / 'manifest.json', {'parent_goal':goal['parent_goal'],'start_commit':BASE,'inputs':[
        {'path':p,'git_blob_sha256':hashlib.sha256(git('show',BASE+':'+p)).hexdigest()} for p in sorted(inputs)]})
    context = read(PREP / 'context.json')
    write(DOC / 'validation-inventory.json', {'start_commit':BASE,'frozen_gates':context['frozen_gates'],'regression_commands':context['regression_commands'],'artifacts':{}})
    write(DOC / 'checkpoint.json', {'status':'incomplete-preflight','started_at':goal['started_at'],'deadline_utc':goal['deadline_utc'],'discovery_cutoff_utc':goal['discovery_cutoff_utc'],'head':BASE,'queue_item':'source_authority','admitted_runs':[],'owned_processes':[],'publication':'not-ready','next_command':'Finish original contract and input review; build and commit admission/gate before model execution'})
    print(json.dumps({'activation':str(activation),'deadline':goal['deadline_utc'],'inputs':len(inputs)}))

if __name__ == '__main__':
    main()

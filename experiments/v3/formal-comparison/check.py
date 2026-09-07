"""Bounded formal construction gate; never launches a harness or model provider."""
import argparse,hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
AREA=ROOT/'docs/v3/construction/formal-comparison-20260907'
BASE='a497bae10dddc3adf176242aed878f83b4519316'
BRANCH='codex/v3-formal-comparison-20260907'

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT).decode().strip()
def require(value,message):
    if not value:raise ValueError(message)
def load(path):return json.loads(path.read_text(encoding='utf8'))
def preflight():
    goal=load(AREA/'goal.json')
    require(goal['start_commit']==BASE and goal['branch']==BRANCH and goal['parent_goal']=='goal-recursion-v2-execution-fabric','goal lineage')
    require(git('branch','--show-current')==BRANCH,'actual branch')
    git('merge-base','--is-ancestor',BASE,'HEAD')
    owners=[e for e in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+BRANCH in e.splitlines()]
    require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree ownership')
    common=pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'))
    prior=common/'research-attestations/interface-probes'/BASE
    completion=load(prior/'completion.json')
    require(completion['candidate']==BASE and completion['status']=='published-scoped-campaign-complete','predecessor accepted')
    receipts=[load(prior/name) for name,digest in completion['receipts'].items() if require(hashlib.sha256((prior/name).read_bytes()).hexdigest()==digest,'predecessor receipt hash') is None]
    require(sum(r.get('status')=='INTERFACE_PROBE_GATE_PASS' for r in receipts)==2 and sum(r.get('verdict')=='approve' for r in receipts)==2,'predecessor gates/reviews')
    require(goal['new_metered_spend']==0 and goal['usage_resets_allowed'] is False,'spend boundary')
    return goal

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');parser.add_argument('--candidate');args=parser.parse_args()
    try:
        preflight()
        require(args.preflight,'Final gate is not constructed: campaign incomplete')
        print('FORMAL_CONSTRUCTION_PREFLIGHT_PASS_NOT_FINAL')
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as exc:print('FORMAL_CONSTRUCTION_GATE_FAIL '+str(exc),file=sys.stderr);sys.exit(1)

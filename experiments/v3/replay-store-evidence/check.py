"""Construction admission only; final acceptance is not implemented yet."""
import argparse,json,pathlib,subprocess,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='03fd11014a5be99006d637ad5eb692faa0557f8f'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def require(value,message):
    if not value:raise ValueError(message)
def preflight():
    goal=json.loads((ROOT/'docs/v3/construction/replay-store-evidence-20260907/goal.json').read_text())
    require(goal['start_commit']==BASE and goal['parent_goal']=='goal-recursion-v2-execution-fabric','goal lineage')
    require(goal['new_metered_spend']==0 and goal['usage_resets_allowed'] is False,'spend/reset boundary')
    require(git('branch','--show-current')==goal['branch'],'branch')
    for ancestor in [BASE,'a7cd9458d37f3090079930bf8d79ffd77c4f73e4']:git('merge-base','--is-ancestor',ancestor,'HEAD')
    owners=[r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+goal['branch'] in r.splitlines()]
    require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree')
    common=pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'));require(not (ROOT/'state/PAUSE').exists() and not (common.parent/'state/PAUSE').exists(),'PAUSE')
    prior=common/'research-attestations/flow-recovery-integration'/BASE;receipt=json.loads((prior/'completion.json').read_text());require(receipt['candidate']==BASE and receipt['status']=='published-scoped-campaign-complete','accepted predecessor')
    records=[]
    for name,digest in receipt['receipts'].items():
        raw=(prior/name).read_bytes();require(hashlib.sha256(raw).hexdigest()==digest,'predecessor receipt digest');records.append(json.loads(raw))
    require(all(r['candidate']==BASE for r in records) and sum(r.get('status')=='FLOW_RECOVERY_GATE_PASS' for r in records)==2 and len({r['reviewer'] for r in records if r.get('verdict')=='approve'})==2,'two exact predecessor gates/reviews')
    print('REPLAY_STORE_CONSTRUCTION_PREFLIGHT_PASS_NOT_FINAL')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preflight',action='store_true');args=p.parse_args()
    if not args.preflight:raise SystemExit('Final gate is not implemented; construction remains incomplete.')
    preflight()

"""Generation authority construction preflight; final gate follows evidence."""
import argparse,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='04b664c58bddb72674d297f4bcf4bef5435bda0f'
AREA=ROOT/'docs/v3/construction/generation-authority-20260907'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def require(ok,message):
    if not ok:raise ValueError(message)
def preflight():
    g=json.loads((AREA/'goal.json').read_text());require(g['start_commit']==BASE and g['parent_goal']=='goal-recursion-v2-execution-fabric','goal lineage')
    require(g['new_metered_spend']==0 and g['usage_resets_allowed'] is False,'capacity boundary');require(git('branch','--show-current')==g['branch'],'branch')
    for a in [BASE,'a7cd9458d37f3090079930bf8d79ffd77c4f73e4']:git('merge-base','--is-ancestor',a,'HEAD')
    owners=[r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+g['branch'] in r.splitlines()];require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive ownership')
    common=pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'));require(not (ROOT/'state/PAUSE').exists() and not (common.parent/'state/PAUSE').exists(),'PAUSE')
    p=common/'research-attestations/replay-store-evidence'/BASE;c=json.loads((p/'completion.json').read_text());require(c['status']=='published-scoped-campaign-complete' and c['candidate']==BASE,'predecessor')
    rs=[]
    for n,h in c['receipts'].items():
        raw=(p/n).read_bytes();require(hashlib.sha256(raw).hexdigest()==h,'receipt hash');rs.append(json.loads(raw))
    require(all(r['candidate']==BASE for r in rs) and sum(r.get('status')=='REPLAY_STORE_GATE_PASS' for r in rs)==2 and len({r['reviewer'] for r in rs if r.get('verdict')=='approve'})==2,'two exact predecessor gates/reviews')
    print('GENERATION_AUTHORITY_PREFLIGHT_PASS_NOT_FINAL')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preflight',action='store_true');args=p.parse_args()
    if not args.preflight:raise SystemExit('Final gate not implemented. Construction incomplete.')
    preflight()

"""Construction preflight; final publication gate is not yet implemented."""
import argparse,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='f86f169c61ca6db4a3d7870353f270e35ef954d6'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def preflight():
    g=json.loads((ROOT/'docs/v3/construction/flow-recovery-integration-20260907/goal.json').read_text())
    assert g['start_commit']==BASE and g['parent_goal']=='goal-recursion-v2-execution-fabric'
    assert g['new_metered_spend']==0 and g['usage_resets_allowed'] is False
    assert git('branch','--show-current')==g['branch']
    git('merge-base','--is-ancestor',BASE,'HEAD')
    assert len([r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+g['branch'] in r.splitlines()])==1
    common=pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'))
    receipt=json.loads((common/'research-attestations/reset-mapping'/BASE/'completion.json').read_text())
    assert receipt['candidate']==BASE and receipt['status']=='published-scoped-campaign-complete'
    print('FLOW_RECOVERY_CONSTRUCTION_PREFLIGHT_PASS_NOT_FINAL')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preflight',action='store_true');args=p.parse_args()
    if not args.preflight:raise SystemExit('Final gate is not implemented; this remains construction in progress.')
    preflight()

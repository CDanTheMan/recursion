"""Bind staged publication artifacts without a circular self digest."""
import hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='f86f169c61ca6db4a3d7870353f270e35ef954d6';PREFIX='docs/v3/construction/flow-recovery-integration-20260907/'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
if __name__=='__main__':
    prior=json.loads((ROOT/'docs/v3/foundation-research/mark2-research/mark3-comparison/validation-inventory.json').read_text())
    changed=git('diff','--cached','--name-only',BASE).decode().splitlines()
    result={'schema_version':1,'start_commit':BASE,'regression_commands':prior['regression_commands'],'artifacts':{p:hashlib.sha256(git('show',':'+p)).hexdigest() for p in changed if p!=PREFIX+'validation-inventory.json'}}
    (ROOT/PREFIX/'validation-inventory.json').write_text(json.dumps(result,indent=2)+'\n')

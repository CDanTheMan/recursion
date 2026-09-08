"""Bind publication artifacts to staged Git blobs, independent of checkout EOLs."""
import hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
PREFIX='docs/v3/construction/formal-comparison-20260907/'
BASE='a497bae10dddc3adf176242aed878f83b4519316'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
if __name__=='__main__':
    changed=git('diff','--cached','--name-only',BASE).decode().splitlines()
    prior=json.loads((ROOT/'docs/v3/foundation-research/mark2-research/mark3-comparison/validation-inventory.json').read_text())
    result={'schema_version':1,'start_commit':BASE,'regression_commands':prior['regression_commands'],
        'artifacts':{p:hashlib.sha256(git('show',':'+p)).hexdigest() for p in changed if p!=PREFIX+'validation-inventory.json'},
        'scope':'Current exact candidate: retained evidence checks, model/calibration reproduction, unchanged25 regressions. Frozen predecessor and research worktrees: original working gates.',
        'limitations':['Inventory excludes its own digest; the final receipt hashes every changed artifact.','Pass certifies only the named finite preventive slice, not full formal comparison, wire refinement, live provider behavior or product readiness.']}
    (ROOT/PREFIX/'validation-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    print('INVENTORY_WRITTEN_FROM_STAGED_BLOBS '+str(len(result['artifacts'])))

"""Materialize final candidate inventory from the staged Git blobs, not checkout EOLs."""
import hashlib
import json
import pathlib
import subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
PREFIX='docs/v3/construction/interface-probes-20260907/'
BASE='840599ae60a7dadacc8b6ac2eac29ca0734c2a1d'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
if __name__=='__main__':
    changed=git('diff','--cached','--name-only',BASE).decode().splitlines()
    prior=json.loads((ROOT/'docs/v3/foundation-research/mark2-research/mark3-comparison/validation-inventory.json').read_text())
    result={'schema_version':1,'start_commit':BASE,'regression_commands':prior['regression_commands'],
            'artifacts':{p:hashlib.sha256(git('show',':'+p)).hexdigest() for p in changed if p!=PREFIX+'validation-inventory.json'},
            'scope':'Current candidate: new checks and unchanged25 regressions. Historical campaign positives/adversarial checks: unchanged frozen research worktree. Raw run/source evidence remains external.',
            'limitations':['Inventory excludes its own digest; final gate receipt hashes every changed artifact.','No live provider, formal-refinement or product certification from validation.']}
    (ROOT/PREFIX/'validation-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    print('INVENTORY_WRITTEN_FROM_STAGED_BLOBS '+str(len(result['artifacts'])))

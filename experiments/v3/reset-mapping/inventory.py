import hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='c87f492780087772e3bcb06249ef14d89e812a25';PREFIX='docs/v3/construction/reset-mapping-20260907/'
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
if __name__=='__main__':
    prior=json.loads((ROOT/'docs/v3/foundation-research/mark2-research/mark3-comparison/validation-inventory.json').read_text())
    changed=git('diff','--cached','--name-only',BASE).decode().splitlines()
    result={'schema_version':1,'start_commit':BASE,'regression_commands':prior['regression_commands'],'artifacts':{p:hashlib.sha256(git('show',':'+p)).hexdigest() for p in changed if p!=PREFIX+'validation-inventory.json'}}
    (ROOT/PREFIX/'validation-inventory.json').write_text(json.dumps(result,indent=2)+'\n')

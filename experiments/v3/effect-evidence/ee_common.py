"""Frozen literal codecs and validators; no runtime effects."""
import copy, hashlib, importlib.util, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.v3.planning.validation import canonical as m1a
from scripts.v3.planning.replay import kernel
from scripts.v3.planning.validation import contracts

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

schema = module('ee_literal_schema', 'scripts/tests/v3/integrity/schema.test.py')
oracle = module('ee_literal_oracle', 'scripts/tests/v3/integrity/reference_oracle.py')
def rawhash(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return oracle.canonical_bytes(value)
def dh(value): return 'sha256:' + rawhash(canonical(value))
def ref(record): return {k:record[k] for k in ('object_type','id','version','content_digest')}
def pref(digest): return 'sha256:' + digest
def tid(kind, value): return kind + ':' + value
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path,value): path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def require(condition,label):
    if not condition: raise ValueError(label)
def classify(value):
    schema.validate(value,'EffectTraceInput')
    result=oracle.classify_effect_trace(value)
    schema.validate(result,'EffectDecision')
    return result
def running():
    fixture=load(ROOT/'scripts/tests/v3/planning/fixtures/F-M1A-014.json')['cases'][0]
    state=kernel.genesis(fixture['genesis']); journal=[]
    for command in fixture['initial_commands']:
        state,events,receipt,journal=kernel.admit(state,state['content_digest'],command,fixture['authority_fixtures'],fixture['policy_fixtures'],journal)
        require(receipt['disposition']=='accepted','literal setup admission')
    return fixture,state,journal
def rebind(command,state):
    result=copy.deepcopy(command)
    result.update(expected_state_digest=state['content_digest'],expected_state_version=state['state_version'])
    return m1a.seal(result)

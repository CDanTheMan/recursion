"""Shared transport/fixture utilities; no product runtime."""
import hashlib,json,pathlib,runpy,os
ROOT=pathlib.Path(__file__).resolve().parents[3]
F=runpy.run_path(str(ROOT/'experiments/v3/replay-store-evidence/fixture.py'))
PARSE=runpy.run_path(str(ROOT/'experiments/v3/replay-store-evidence/reader.py'))['parse']
def encode(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode('ascii')
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return PARSE(pathlib.Path(p).read_bytes())
def save(p,v):
    with pathlib.Path(p).open('wb') as f:f.write(encode(v));f.flush();os.fsync(f.fileno())
def require(ok,message):
    if not ok:raise ValueError(message)
def emit(v):print(json.dumps(v,sort_keys=True),flush=True)
def phase(name):
    emit({'phase':name});require(input()=='continue','phase-aborted')
def scope(root,path):
    root=pathlib.Path(root).resolve();p=pathlib.Path(path);require(p.resolve().is_relative_to(root),'path-escape');return p
def bootstrap(root,unit,policy,instance):
    root.mkdir();(root/'store').mkdir();d=root/'store/g1';d.mkdir()
    files=F['artifacts'](1,unit)
    for n,b in files.items():(d/n).write_bytes(b)
    (root/'authority.lock').write_bytes(b'0')
    state={'version':1,'instance':instance,'unit':unit,'policy':policy,'boot':0,'revision':0,'selected':1,'writer_seq':0,'writer':None,'pin_seq':0,'pins':{},'draining':False,'generations':{'1':{'status':'current','directory':'g1','manifest_sha256':sha(files['manifest.json'])},'2':{'status':'unpublished','directory':None,'manifest_sha256':None}}};save(root/'authority.json',state)

"""Independent fixed-generation byte verifier; does not import producer fixture."""
import base64,hashlib,json,pathlib,stat
def require(ok,message):
    if not ok:raise ValueError(message)
def digest(b):return hashlib.sha256(b).hexdigest()
def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode('ascii')
def verify(store,ticket,after_manifest=None):
    root=pathlib.Path(store).resolve();directory=root/ticket['directory'];require(directory.resolve().is_relative_to(root),'generation-path');s=directory.lstat();require(stat.S_ISDIR(s.st_mode) and not getattr(s,'st_file_attributes',0)&0x400,'generation-type')
    reads={}
    def read(name):
        p=directory/name;s=p.lstat();require(stat.S_ISREG(s.st_mode) and not getattr(s,'st_file_attributes',0)&0x400,'artifact-type');b=p.read_bytes();require(len(b)<65536,'artifact-size');reads[name]=digest(b);return b
    g=ticket['generation'];unit=ticket['unit'];require(type(g)is int and g in (1,2) and unit in ('event','utf8-byte'),'ticket-profile')
    names=sorted(p.name for p in directory.iterdir());expected=['event1.json','event2.json','event3.json','manifest.json','snapshot.json'] if g==1 else ['event3.json','manifest.json','snapshot.json'];require(names==expected,'generation-membership')
    mraw=read('manifest.json');require(digest(mraw)==ticket['manifest_sha256'],'manifest-pin');m=json.loads(mraw)
    if after_manifest:after_manifest()
    payloads=[b'A',b'\xc3\xa9',b'B'];catalog=[{'version':1,'stream':'stream-a','epoch':2,'id':n,'event_cursor':n,'byte_cursor':sum(map(len,payloads[:n])),'payload':base64.b64encode(payloads[n-1]).decode()} for n in (1,2,3)]
    floor=0 if g==1 else 2;sn=1 if g==1 else 2;content=b''.join(payloads[:sn]);snap={'version':1,'stream':'stream-a','epoch':2,'generation':g,'cursor_unit':unit,'event_cursor':sn,'byte_cursor':len(content),'state_base64':base64.b64encode(content).decode(),'state_sha256':digest(content),'prefix_event_hashes':[digest(encoded(e)) for e in catalog[:sn]]}
    blobs={f'event{n}.json':encoded(catalog[n-1]) for n in ((1,2,3) if g==1 else (3,))};blobs['snapshot.json']=encoded(snap)
    wanted={'version':1,'stream':'stream-a','epoch':2,'generation':g,'cursor_unit':unit,'tip_event':3,'tip_byte':4,'replay_floor_event':floor,'replay_floor_byte':0 if g==1 else 3,'files':{n:digest(b) for n,b in blobs.items()}}
    require(m==wanted,'generation-manifest')
    for n,b in blobs.items():require(read(n)==b,'generation-content')
    return {'generation':g,'unit':unit,'directory':ticket['directory'],'files':reads,'snapshot_event_cursor':sn,'snapshot_byte_cursor':len(content),'snapshot_state_base64':snap['state_base64'],'retained_event_ids':[1,2,3] if g==1 else [3]}

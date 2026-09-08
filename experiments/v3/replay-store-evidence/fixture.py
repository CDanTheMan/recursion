"""Synthetic producer/controller fixture. No product storage implementation."""
import base64,hashlib,json,pathlib,os
PAYLOADS=[b'A','é'.encode('utf8'),b'B']
def encode(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def b64(raw):return base64.b64encode(raw).decode('ascii')
def event(n):return {'version':1,'stream':'stream-a','epoch':2,'id':n,'event_cursor':n,'byte_cursor':sum(map(len,PAYLOADS[:n])),'payload':b64(PAYLOADS[n-1])}
def snapshot(g,n,unit):
    raw=b''.join(PAYLOADS[:n]);return {'version':1,'stream':'stream-a','epoch':2,'generation':g,'cursor_unit':unit,'event_cursor':n,'byte_cursor':len(raw),'state_base64':b64(raw),'state_sha256':digest(raw),'prefix_event_hashes':[digest(encode(event(k))) for k in range(1,n+1)]}
def artifacts(g,unit,ids=None,snap=None,floor=None):
    ids=([1,2,3] if g==1 else [3]) if ids is None else ids;snap=(1 if g==1 else 2) if snap is None else snap
    missing=set(range(1,4))-set(ids);floor=max(missing,default=0) if floor is None else floor
    files={f'event{k}.json':encode(event(k)) for k in ids};files['snapshot.json']=encode(snapshot(g,snap,unit))
    manifest={'version':1,'stream':'stream-a','epoch':2,'generation':g,'cursor_unit':unit,'tip_event':3,'tip_byte':4,'replay_floor_event':floor,'replay_floor_byte':sum(map(len,PAYLOADS[:floor])),'files':{n:digest(raw) for n,raw in files.items()}}
    files['manifest.json']=encode(manifest);return files
def current(layout,g,files):return {'version':1,'generation':g,'directory':'active' if layout=='in-place' else f'g{g}','manifest_sha256':digest(files['manifest.json'])}
def trust(layout,g,unit,attempt,nonce,files=None,request_event=1):
    files=files or artifacts(g,unit);pointer=current(layout,g,files)
    return {'version':1,'attempt':attempt,'nonce':nonce,'layout':layout,'expected_generation':g,'current_sha256':digest(encode(pointer)),'manifest_sha256':digest(files['manifest.json']),'stream':'stream-a','epoch':2,'cursor_unit':unit,'request_cursor':request_event if unit=='event' else sum(map(len,PAYLOADS[:request_event])),'catalog':[event(k) for k in range(1,4)]}
def flush_write(path,raw):
    with pathlib.Path(path).open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def initial_app():return {'version':1,'stream':'stream-a','epoch':2,'generation':1,'event_cursor':1,'byte_cursor':1,'state_base64':b64(b'A')}

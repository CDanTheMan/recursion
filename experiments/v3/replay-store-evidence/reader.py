"""Independent byte/namespace verifier; imports no producer fixture reducer."""
import base64,hashlib,json,pathlib,os,stat
class Refused(ValueError):pass
def require(value,reason):
    if not value:raise Refused(reason)
def parse(raw):
    def pairs(items):
        value={}
        for key,item in items:
            require(key not in value,'duplicate-json-key');value[key]=item
        return value
    return json.loads(raw.decode('utf8'),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(Refused('non-json-constant')))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def payload(value):return base64.b64decode(value,validate=True)
def shape(value,keys):require(type(value)is dict and set(value)==set(keys.split()),'object-shape')
def integer(n):return type(n)is int and 0<=n<=2147483647
def regular(path):
    s=path.lstat();require(stat.S_ISREG(s.st_mode) and not getattr(s,'st_file_attributes',0)&0x400,'nonregular-artifact')
def observe(store,trust):
    root=pathlib.Path(store).resolve();reads={};names=[]
    def read(path):
        require(path.resolve().is_relative_to(root),'artifact-path');regular(path);raw=path.read_bytes();require(len(raw)<=65536,'artifact-size');reads[path.relative_to(root).as_posix()]=sha(raw);return raw
    result={'attempt':trust['attempt'],'nonce':trust['nonce'],'reader_pid':os.getpid(),'status':'blocked','reason':None,'reads':reads,'selected_files':names}
    try:
        shape(trust,'version attempt nonce layout expected_generation current_sha256 manifest_sha256 stream epoch cursor_unit request_cursor catalog')
        require(trust['version']==1 and trust['layout'] in ('in-place','staged-generation') and trust['cursor_unit'] in ('event','utf8-byte'),'trust-profile')
        require(trust['stream']=='stream-a' and trust['epoch']==2 and integer(trust['expected_generation']) and trust['expected_generation'] in (1,2),'trust-identity')
        cat=trust['catalog'];require(type(cat)is list and len(cat)==3,'bounded-catalog');data=[];boundaries=[0];hashes=[]
        for n,e in enumerate(cat,1):
            shape(e,'version stream epoch id event_cursor byte_cursor payload');raw=payload(e['payload']);data.append(raw);boundaries.append(boundaries[-1]+len(raw));hashes.append(sha(canonical(e)))
            require(e['version']==1 and e['stream']==trust['stream'] and e['epoch']==trust['epoch'] and type(e['id'])is int and e['id']==n and type(e['event_cursor'])is int and e['event_cursor']==n and type(e['byte_cursor'])is int and e['byte_cursor']==boundaries[n],'catalog-identity')
        require(data==[b'A',b'\xc3\xa9',b'B'],'fixture-catalog')
        unit=trust['cursor_unit'];request=trust['request_cursor'];require(integer(request),'request-type')
        legal=list(range(4)) if unit=='event' else boundaries;require(request in legal,'cursor-inside-payload-or-outside-catalog');request_id=legal.index(request)
        current_raw=read(root/'CURRENT.json');require(sha(current_raw)==trust['current_sha256'],'current-pin-mismatch');pointer=parse(current_raw)
        shape(pointer,'version generation directory manifest_sha256');g=trust['expected_generation'];expected_dir='active' if trust['layout']=='in-place' else f'g{g}'
        require(pointer['version']==1 and type(pointer['generation'])is int and pointer['generation']==g and pointer['directory']==expected_dir and pointer['manifest_sha256']==trust['manifest_sha256'],'selected-generation-mismatch')
        directory=root/expected_dir;s=directory.lstat();require(stat.S_ISDIR(s.st_mode) and not getattr(s,'st_file_attributes',0)&0x400,'nonregular-namespace')
        # All members are enumerated after writer exit. Enumeration errors block.
        names.extend(sorted(p.name for p in directory.iterdir()));require(set(names)<=set(['manifest.json','snapshot.json','event1.json','event2.json','event3.json']),'unexpected-namespace-member')
        mraw=read(directory/'manifest.json');require(sha(mraw)==pointer['manifest_sha256'],'manifest-pin-mismatch');m=parse(mraw)
        shape(m,'version stream epoch generation cursor_unit tip_event tip_byte replay_floor_event replay_floor_byte files')
        require(m['version']==1 and m['stream']==trust['stream'] and m['epoch']==trust['epoch'] and type(m['generation'])is int and m['generation']==g and m['cursor_unit']==unit and type(m['tip_event'])is int and m['tip_event']==3 and type(m['tip_byte'])is int and m['tip_byte']==4,'manifest-identity')
        require(type(m['files'])is dict and set(m['files'])==set(names)-{'manifest.json'} and 'snapshot.json' in m['files'],'namespace-membership-mismatch')
        blobs={}
        for name,expected in m['files'].items():
            raw=read(directory/name);require(sha(raw)==expected,'member-digest-mismatch');blobs[name]=raw
        ids=[]
        for n,e in enumerate(cat,1):
            name=f'event{n}.json'
            if name in blobs:require(blobs[name]==canonical(e),'event-catalog-mismatch');ids.append(n)
        floor=max(set(range(1,4))-set(ids),default=0)
        require(integer(m['replay_floor_event']) and integer(m['replay_floor_byte']) and m['replay_floor_event']==floor and m['replay_floor_byte']==boundaries[floor],'declared-floor-not-observed-suffix')
        snap=parse(blobs['snapshot.json']);shape(snap,'version stream epoch generation cursor_unit event_cursor byte_cursor state_base64 state_sha256 prefix_event_hashes');sn=snap['event_cursor']
        require(integer(sn) and sn<=3 and snap['version']==1 and snap['stream']==trust['stream'] and snap['epoch']==trust['epoch'] and type(snap['generation'])is int and snap['generation']==g and snap['cursor_unit']==unit,'snapshot-identity')
        rawstate=payload(snap['state_base64']);require(type(snap['byte_cursor'])is int and snap['byte_cursor']==boundaries[sn] and rawstate==b''.join(data[:sn]) and snap['state_sha256']==sha(rawstate) and snap['prefix_event_hashes']==hashes[:sn],'snapshot-content-or-cursor')
        require(sn>=floor,'snapshot-below-replay-floor')
        require(read(root/'CURRENT.json')==current_raw,'selection-changed-during-read')
        gap=request_id<floor;resume=sn if gap else request_id;require(all(n in ids for n in range(resume+1,4)),'incomplete-replay-suffix')
        result.update(status='gap' if gap else 'replay',reason=None,generation=g,cursor_unit=unit,request_event_cursor=request_id,derived_floor_event=floor,derived_floor_cursor=legal[floor],snapshot_event_cursor=sn,snapshot_cursor=legal[sn],snapshot=snap,replay_events=[cat[n-1] for n in range(resume+1,4)],current_sha256=sha(current_raw),manifest_sha256=sha(mraw))
    except (Refused,OSError,ValueError,KeyError,TypeError,IndexError) as exc:result['reason']=str(exc) if isinstance(exc,Refused) else type(exc).__name__
    return result

"""Finite local producer/reader/receiver helper; admits no network or child work."""
import argparse,base64,json,os,pathlib,sys
import fixture as F
from reader import observe,parse,require
def output(value):print(json.dumps(value,sort_keys=True),flush=True)
def phase(name,**extra):
    output({'phase':name,**extra});require(sys.stdin.readline().strip()=='continue','phase-admission-ended')
def network_guard(event,args):
    if event.startswith('socket.') or event in ('subprocess.Popen','os.system'):raise RuntimeError('helper-external-operation-blocked')
def initialize(root,layout,unit):
    files=F.artifacts(1,unit);directory=root/('active' if layout=='in-place' else 'g1');directory.mkdir()
    for name,raw in files.items():F.flush_write(directory/name,raw)
    F.flush_write(root/'CURRENT.json',F.encode(F.current(layout,1,files)));output({'status':'initialized','pid':os.getpid()})
def update(root,layout,unit):
    files=F.artifacts(2,unit);directory=root/('active' if layout=='in-place' else 'g2');directory.mkdir(exist_ok=True)
    raw=files['snapshot.json'];half=len(raw)//2
    with (directory/'snapshot.json').open('wb') as stream:
        stream.write(raw[:half]);stream.flush();os.fsync(stream.fileno());phase('snapshot_partial')
        stream.write(raw[half:]);stream.flush();os.fsync(stream.fileno())
    phase('snapshot_ready')
    if layout=='in-place':
        for n in (1,2):(directory/f'event{n}.json').unlink()
    else:
        # Copy the actually retained baseline bytes; the reader verifies their identity.
        F.flush_write(directory/'event3.json',(root/'g1/event3.json').read_bytes())
    phase('retention_changed')
    F.flush_write(directory/'manifest.json',files['manifest.json']);F.flush_write(root/'CURRENT.tmp',F.encode(F.current(layout,2,files)));phase('manifest_staged')
    os.replace(root/'CURRENT.tmp',root/'CURRENT.json');phase('commit_published');output({'status':'updated','pid':os.getpid()})
def application(path,catalog):
    a=parse(path.read_bytes());require(set(a)==set('version stream epoch generation event_cursor byte_cursor state_base64'.split()),'application-shape');n=a['event_cursor']
    require(type(n)is int and 0<=n<=3 and a['version']==1 and a['stream']=='stream-a' and a['epoch']==2 and type(a['generation'])is int and a['generation'] in (1,2),'application-identity')
    raw=b''.join(base64.b64decode(e['payload'],validate=True) for e in catalog[:n]);require(a['state_base64']==F.b64(raw) and type(a['byte_cursor'])is int and a['byte_cursor']==len(raw),'application-content-cursor');return a
def receive(root,trust,proof,app):
    require(proof['attempt']==trust['attempt'] and proof['nonce']==trust['nonce'],'transplanted-observation')
    fresh=observe(root,trust);require(fresh['status'] in ('gap','replay'),'store-evidence-blocked')
    for key in ['status','generation','current_sha256','manifest_sha256','request_event_cursor','derived_floor_cursor','snapshot_cursor','replay_events','snapshot','reads']:
        require(proof[key]==fresh[key],'stale-observation')
    a=application(app,trust['catalog']);require(a['event_cursor']==fresh['request_event_cursor'],'request-application-mismatch');unit=trust['cursor_unit']
    def cursor(state):return state['event_cursor'] if unit=='event' else state['byte_cursor']
    def emit(kind,**fields):output({'wire':{'type':kind,'protocol_version':'m1b-broker/1','stream_id':'stream-a','daemon_epoch':2,**fields}})
    emit('HELLO',client_id='client-a',last_cursor=cursor(a),cursor_unit=unit,columns=80,rows=24,capabilities=['attach'])
    emit('WELCOME',client_id='client-a',replay_floor=fresh['derived_floor_cursor'],snapshot_cursor=fresh['snapshot_cursor'] if fresh['status']=='gap' else cursor(a),cursor_unit=unit,input_lease=None,resize_lease=None,capabilities=[])
    if fresh['status']=='gap':
        emit('RESET',client_id='client-a',reason='gap',snapshot_cursor=fresh['snapshot_cursor'],cursor_unit=unit);phase('RESET_emitted')
        s=fresh['snapshot'];a={'version':1,'stream':'stream-a','epoch':2,'generation':s['generation'],'event_cursor':s['event_cursor'],'byte_cursor':s['byte_cursor'],'state_base64':s['state_base64']}
        F.flush_write(app.with_suffix('.tmp'),F.encode(a));phase('snapshot_staged');os.replace(app.with_suffix('.tmp'),app);phase('reset_committed')
    for e in fresh['replay_events']:
        raw=base64.b64decode(e['payload'],validate=True);require(e['event_cursor']==a['event_cursor']+1,'nonconsecutive-application')
        emit('CREDIT',client_id='client-a',bytes=len(raw),events=1)
        emit('EVENT',cursor=e['event_cursor'] if unit=='event' else e['byte_cursor'],cursor_unit=unit,payload_base64=e['payload'],event_class='output',process_id='process-a',payload_untrusted=True)
        a.update(event_cursor=e['event_cursor'],byte_cursor=e['byte_cursor'],state_base64=F.b64(base64.b64decode(a['state_base64'])+raw))
        F.flush_write(app.with_suffix('.tmp'),F.encode(a));os.replace(app.with_suffix('.tmp'),app)
        emit('ACK',client_id='client-a',cursor=cursor(a),cursor_unit=unit)
    output({'status':'receiver-complete','application':application(app,trust['catalog']),'pid':os.getpid()})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('role',choices=['init','update','read','receive']);p.add_argument('--store',required=True);p.add_argument('--layout',choices=['in-place','staged-generation']);p.add_argument('--unit',choices=['event','utf8-byte']);p.add_argument('--trust');p.add_argument('--proof');p.add_argument('--app');args=p.parse_args();root=pathlib.Path(args.store).resolve();sys.addaudithook(network_guard)
    try:
        if args.role=='init':initialize(root,args.layout,args.unit)
        elif args.role=='update':update(root,args.layout,args.unit)
        elif args.role=='read':output(observe(root,parse(pathlib.Path(args.trust).read_bytes())))
        else:receive(root,parse(pathlib.Path(args.trust).read_bytes()),parse(pathlib.Path(args.proof).read_bytes()),pathlib.Path(args.app))
    except Exception as exc:output({'status':'helper-refused','reason':type(exc).__name__+': '+str(exc),'pid':os.getpid()});raise SystemExit(2)

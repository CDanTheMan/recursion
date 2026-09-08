"""Named-cut local process experiment. Raw case receipts and files are retained."""
import argparse,copy,datetime,json,os,pathlib,queue,runpy,subprocess,sys,threading,time,uuid
from jsonschema import Draft202012Validator
import fixture as F
ROOT=pathlib.Path(__file__).resolve().parents[3]
HELPER=pathlib.Path(__file__).with_name('worker.py')
ORACLE=runpy.run_path(str(ROOT/'scripts/tests/v3/execution/reference_oracle.py'))['replay_broker']
VALIDATOR=Draft202012Validator(json.loads((ROOT/'schemas/control-plane/v3/execution/schema.json').read_text()))
BASE_INPUT=json.loads((ROOT/'scripts/tests/v3/execution/fixtures/F-M1B-020.json').read_text())['input']
WRITER_CUTS=['snapshot_partial','snapshot_ready','retention_changed','manifest_staged','commit_published']
RECEIVER_CUTS=['RESET_emitted','snapshot_staged','reset_committed']
LIMITS={'child_seconds':10,'kill_wait_seconds':5,'whole_seconds':600,'artifact_bytes':67108864,'repetitions':2}
def require(ok,message):
    if not ok:raise ValueError(message)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,value):path.write_bytes(F.encode(value))
def load(path):return json.loads(path.read_bytes())
def inventory(root):return {p.relative_to(root).as_posix():F.digest(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}
def semantic_report(proof):return {k:v for k,v in proof.items() if k not in ('attempt','nonce','reader_pid')}
class Campaign:
    def __init__(self,output):
        self.output=output.resolve();self.output.mkdir(parents=True,exist_ok=False);self.started=time.monotonic();self.children=0;self.rows=[]
    def case(self,name):
        require(time.monotonic()-self.started<LIMITS['whole_seconds'],'whole-experiment-timeout');root=self.output/name;root.mkdir();(root/'store').mkdir();return root
    def child(self,root,role,*,cut=None,**kwargs):
        command=[sys.executable,'-X','utf8','-B',str(HELPER),role,'--store',str(root/'store')]
        for k,v in kwargs.items():command += ['--'+k,str(v)]
        self.children+=1;tag=f'{self.children:04d}-{role}';q=queue.Queue();records=[];started=now();killed=False;phase_seen=False
        p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        def drain():
            try:
                for line in p.stdout:q.put(line)
            finally:q.put(None)
        thread=threading.Thread(target=drain,daemon=True);thread.start();deadline=time.monotonic()+LIMITS['child_seconds'];error=None
        try:
            while True:
                require(time.monotonic()<deadline,'child-deadline')
                line=q.get(timeout=max(.001,deadline-time.monotonic()))
                if line is None:break
                obj=json.loads(line);records.append(obj)
                if 'phase' in obj:
                    if obj['phase']==cut:p.kill();killed=True;phase_seen=True
                    else:p.stdin.write('continue\n');p.stdin.flush()
            p.wait(timeout=LIMITS['kill_wait_seconds'])
        except Exception as exc:
            error=repr(exc)
        finally:
            if p.poll() is None:p.kill();killed=True
            p.wait(timeout=LIMITS['kill_wait_seconds']);thread.join(timeout=1)
            p.stdin.close();p.stdout.close()
            receipt={'command':command,'started_at':started,'finished_at':now(),'pid':p.pid,'exit_code':p.returncode,'requested_cut':cut,'cut_observed':phase_seen,'terminated_by_controller':killed,'wait_completed':True,'error':error,'records':records}
            save(root/(tag+'.json'),receipt)
        require(error is None,'child-error '+str(error));require(cut is None or (phase_seen and p.returncode!=0),'named-cut-not-reached');receipt['_file']=tag+'.json';return receipt
    def init(self,root,layout,unit):
        r=self.child(root,'init',layout=layout,unit=unit);require(r['exit_code']==0,'init-refused');save(root/'application.json',F.initial_app())
    def read(self,root,layout,unit,g,*,files=None,request=1,mutate=None):
        trust=F.trust(layout,g,unit,root.name,uuid.uuid4().hex,files=files,request_event=request)
        if mutate:mutate(trust)
        t=root/f'trust-{self.children}.json';save(t,trust);r=self.child(root,'read',trust=t);require(r['exit_code']==0 and len(r['records'])==1,'reader-process-failed');proof=r['records'][0]
        require(proof['attempt']==trust['attempt'] and proof['nonce']==trust['nonce'] and proof['reader_pid']==r['pid'],'reader-provenance')
        snapshot=root/f'read-snapshot-{self.children}';snapshot.mkdir()
        for path in (root/'store').rglob('*'):
            if path.is_file():dest=snapshot/path.relative_to(root/'store');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
        proof['_reader_receipt']=r['_file'];proof['_read_snapshot']=snapshot.name;p=root/f'proof-{self.children}.json';save(p,proof);return t,p,proof
    def receive(self,root,t,p,cut=None,refused=False):
        r=self.child(root,'receive',trust=t,proof=p,app=root/'application.json',cut=cut)
        wire=[v['wire'] for v in r['records'] if 'wire' in v];decision=None
        if wire:
            value=copy.deepcopy(BASE_INPUT);value.update(messages=wire,queue_limit_bytes=2,queue_limit_events=2);VALIDATOR.validate(value);decision=ORACLE(value)
            require(decision['status'] in ('accepted','accepted-reset'),'wire-refused '+str(decision))
        if refused:require(r['exit_code']==2 and not wire,'unsafe-receiver-emission')
        elif cut is None:require(r['exit_code']==0,'receiver-failed')
        app=load(root/'application.json');appfile=f'application-observation-{self.children}.json';save(root/appfile,app)
        return {'wire':wire,'decision':decision,'application':app,'refused':refused,'receipt':r['_file'],'application_file':appfile}
    def finish_row(self,root,row):
        row['case']=root.name;self.rows.append(row);save(root/'observation.json',row);save(root/'inventory.json',inventory(root))
    def ordinary(self,rep,layout,unit,mode):
        root=self.case(f'r{rep}-{layout}-{unit}-{mode}');self.init(root,layout,unit)
        g=1
        if mode!='baseline':
            cut=mode if mode in WRITER_CUTS else None;writer=self.child(root,'update',layout=layout,unit=unit,cut=cut)
            if cut is None:require(writer['exit_code']==0,'update-refused')
            g=2 if cut in (None,'commit_published') else 1
        t,p,proof=self.read(root,layout,unit,g)
        expected='blocked' if layout=='in-place' and mode in WRITER_CUTS[:-1] else ('replay' if g==1 else 'gap')
        require(proof['status']==expected,'publication-disposition '+root.name+str(proof));row={'kind':'writer-or-baseline','store':semantic_report(proof),'expected':expected}
        if expected!='blocked':
            received=self.receive(root,t,p);require(received['application']['event_cursor']==3 and received['application']['state_base64']==F.b64(b'A\xc3\xa9B'),'final-content');require(sum(m['type']=='RESET' for m in received['wire'])==(g==2),'reset-choice');row['receiver']=received
        self.finish_row(root,row)
    def receiver_cut(self,rep,layout,unit,cut):
        root=self.case(f'r{rep}-{layout}-{unit}-receiver-{cut}');self.init(root,layout,unit);r=self.child(root,'update',layout=layout,unit=unit);require(r['exit_code']==0,'update');t,p,proof=self.read(root,layout,unit,2)
        before=self.receive(root,t,p,cut=cut);cursor=2 if cut=='reset_committed' else 1
        require(before['application']['event_cursor']==cursor and before['application']['state_base64']==F.b64(b''.join(F.PAYLOADS[:cursor])),'interrupted-app-content')
        require(before['decision']['status']=='accepted-reset','literal-reset-control')
        t,p,reopened=self.read(root,layout,unit,2,request=cursor);after=self.receive(root,t,p);require(after['application']['event_cursor']==3 and after['application']['state_base64']==F.b64(b'A\xc3\xa9B'),'recovered-content')
        t,p,_=self.read(root,layout,unit,2,request=3);again=self.receive(root,t,p);require(not any(m['type']=='EVENT' for m in again['wire']) and again['application']==after['application'],'duplicate-application')
        self.finish_row(root,{'kind':'receiver-cut','cut':cut,'store':semantic_report(proof),'at_cut':before,'application_recovery_at_cut':cursor==2,'reopened':semantic_report(reopened),'recovery':after,'repeat_attach':again})
    def control(self,unit,name):
        root=self.case('control-'+unit+'-'+name);layout='staged-generation';g=2;files=F.artifacts(g,unit);expected='blocked';request=1;mutate=None
        if name=='hole-prefix':files=F.artifacts(g,unit,ids=[1,3]);expected='gap'
        elif name=='retained-suffix':files=F.artifacts(g,unit,ids=[2,3],snap=1);expected='replay'
        elif name=='trailing-hole':files=F.artifacts(g,unit,ids=[1,2],floor=3)
        elif name=='false-floor':files=F.artifacts(g,unit,ids=[1,2,3],floor=2)
        elif name.startswith('snapshot-'):
            s=json.loads(files['snapshot.json']);field,value={'snapshot-stream':('stream','other'),'snapshot-generation':('generation',1),'snapshot-unit':('cursor_unit','utf8-byte' if unit=='event' else 'event'),'snapshot-cursor':('event_cursor',1),'snapshot-content':('state_base64',F.b64(b'xx'))}[name];s[field]=value;files['snapshot.json']=F.encode(s)
            m=json.loads(files['manifest.json']);m['files']['snapshot.json']=F.digest(files['snapshot.json']);files['manifest.json']=F.encode(m)
        elif name=='inside-byte':mutate=lambda t:t.update(request_cursor=2)
        directory=root/'store/g2';directory.mkdir()
        for n,raw in files.items():F.flush_write(directory/n,raw)
        F.flush_write(root/'store/CURRENT.json',F.encode(F.current(layout,g,files)));save(root/'application.json',F.initial_app())
        if name=='missing-snapshot':(directory/'snapshot.json').unlink()
        elif name=='tampered-snapshot':F.flush_write(directory/'snapshot.json',b'{}')
        elif name=='unknown-member':F.flush_write(directory/'unexpected.json',b'{}')
        elif name=='missing-event':(directory/'event3.json').unlink()
        elif name=='rollback':
            old=F.artifacts(1,unit);d=root/'store/g1';d.mkdir()
            for n,raw in old.items():F.flush_write(d/n,raw)
            F.flush_write(root/'store/CURRENT.json',F.encode(F.current(layout,1,old)))
        elif name=='duplicate-json':
            raw=F.encode(F.current(layout,g,files)).replace(b'"version":1',b'"version":1,"version":1');F.flush_write(root/'store/CURRENT.json',raw);mutate=lambda t:t.update(current_sha256=F.digest(raw))
        t,p,proof=self.read(root,layout,unit,g,files=files,request=request,mutate=mutate)
        if name in ('transplanted-proof','stale-proof'):
            require(proof['status']=='gap','negative-baseline')
            if name=='transplanted-proof':bad=load(p);bad['nonce']='other';save(p,bad)
            else:F.flush_write(directory/'snapshot.json',b'{}')
            received=self.receive(root,t,p,refused=True);row={'kind':'receiver-negative','control':name,'store':semantic_report(proof),'receiver':received}
        else:
            require(proof['status']==expected,'control '+name+str(proof))
            reasons={'trailing-hole':'snapshot-below-replay-floor','false-floor':'declared-floor-not-observed-suffix','snapshot-stream':'snapshot-identity','snapshot-generation':'snapshot-identity','snapshot-unit':'snapshot-identity','snapshot-cursor':'snapshot-content-or-cursor','snapshot-content':'snapshot-content-or-cursor','missing-snapshot':'namespace-membership-mismatch','tampered-snapshot':'member-digest-mismatch','unknown-member':'unexpected-namespace-member','missing-event':'namespace-membership-mismatch','rollback':'current-pin-mismatch','duplicate-json':'duplicate-json-key','inside-byte':'cursor-inside-payload-or-outside-catalog'}
            if expected=='blocked':require(proof['reason']==reasons[name],'wrong-negative-reason '+name+str(proof))
            row={'kind':'namespace-control','control':name,'store':semantic_report(proof),'expected':expected}
            if expected!='blocked':row['receiver']=self.receive(root,t,p)
        self.finish_row(root,row)
    def run(self):
        for rep in range(LIMITS['repetitions']):
            for layout in ('in-place','staged-generation'):
                for unit in ('event','utf8-byte'):
                    for mode in ['baseline','complete',*WRITER_CUTS]:self.ordinary(rep,layout,unit,mode)
                    for cut in RECEIVER_CUTS:self.receiver_cut(rep,layout,unit,cut)
        names=['hole-prefix','retained-suffix','trailing-hole','false-floor','snapshot-stream','snapshot-generation','snapshot-unit','snapshot-cursor','snapshot-content','missing-snapshot','tampered-snapshot','unknown-member','missing-event','rollback','duplicate-json','transplanted-proof','stale-proof']
        for unit in ('event','utf8-byte'):
            for name in names+(['inside-byte'] if unit=='utf8-byte' else []):self.control(unit,name)
        require(sum(p.stat().st_size for p in self.output.rglob('*') if p.is_file())<=LIMITS['artifact_bytes'],'artifact-budget')
        return {'status':'local-named-cut-pass','case_count':len(self.rows),'helper_process_count':self.children,'live_provider_calls':0,'formal_freeze':False,'power_loss_durability_established':False,'rows':self.rows,'cleanup':'All owned helper handles waited and pipes closed; isolated fixture artifacts retained for forensics.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=pathlib.Path(args.output);campaign=Campaign(out)
    try:result=campaign.run();save(out/'result.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
    except Exception as exc:save(out/'failure.json',{'error':repr(exc),'completed_cases':len(campaign.rows),'helper_process_count':campaign.children});raise

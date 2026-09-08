"""Preregistered real-process schedules; retains content-addressed raw observations."""
import argparse,copy,datetime,json,os,pathlib,queue,subprocess,sys,threading,time,uuid
from support import F,bootstrap,encode,sha,load,require
CODE=pathlib.Path(__file__).resolve().parent
CASES=['overlap_pin','overlap_manifest','two_pins','stale_writer_cancel','restart_live_pin','pin_staged_loss','pin_reply_loss','publish_staged_loss','publish_reply_loss','retire_intent_loss','retire_partial_loss','reader_death','publisher_death','lock_exclusion','acquisition_race','negative_tokens']
LIMITS={'whole_seconds':600,'command_seconds':10,'kill_wait_seconds':5,'artifact_bytes':67108864,'maximum_children_alive':5}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
class Child:
    def __init__(self,campaign,case,role,args):
        self.c=campaign;self.case=case;self.role=role;self.id=f'child{len(campaign.children)+1}';self.q=queue.Queue();self.held=None;self.waited=False
        command=[sys.executable,'-X','utf8','-B',str(CODE/('authority.py' if role=='authority' else 'actor.py')),*args]
        self.p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));campaign.children.append(self);campaign.event(case,{'kind':'spawn','child':self.id,'role':role,'pid':self.p.pid,'command':command})
        require(sum(p.p.poll() is None for p in campaign.children)<=5,'live-child-cap')
        def drain():
            try:
                for line in self.p.stdout:self.q.put(line)
            finally:self.q.put(None)
        self.thread=threading.Thread(target=drain,daemon=True);self.thread.start()
    def send(self,value):
        require(time.monotonic()<self.c.deadline,'whole-timeout');self.c.event(self.case,{'kind':'send','child':self.id,'value':value});self.p.stdin.write((value if isinstance(value,str) else json.dumps(value))+'\n');self.p.stdin.flush();self.held=None
    def until(self,*,phase=None,response=None,ready=False,cut=None):
        deadline=min(time.monotonic()+10,self.c.deadline)
        while True:
            require(time.monotonic()<deadline,'command-timeout');line=self.q.get(timeout=max(.001,deadline-time.monotonic()))
            if line is None:self.wait();return None
            try:v=json.loads(line)
            except ValueError:self.c.event(self.case,{'kind':'unparsed-output','child':self.id,'text':line});raise
            self.c.event(self.case,{'kind':'receive','child':self.id,'value':v})
            if 'phase' in v:
                self.held=v['phase'];self.c.snapshot(self.case,self.id+'/'+self.held)
                if self.held==cut:self.stop(kill=True);return None
                if self.held==phase:return v
                self.send('continue')
            elif ready and v.get('ready'):return v
            elif response is not None and v.get('request_id')==response:return v['response']
    def resume(self,phase=None):self.send('continue');return self.until(phase=phase)
    def wait(self,killed=False):
        if self.waited:return
        self.p.wait(timeout=5);self.thread.join(timeout=1);self.p.stdin.close();self.p.stdout.close();self.waited=True;self.c.event(self.case,{'kind':'wait','child':self.id,'pid':self.p.pid,'exit_code':self.p.returncode,'killed':killed})
    def stop(self,kill=False):
        if self.waited:return
        if self.p.poll() is None:
            if kill:self.p.kill();self.wait(killed=True);return
            if self.held:self.send('continue')
            elif self.role=='authority':self.send({'op':'exit'})
            self.until()
        self.wait()
class Campaign:
    def __init__(self,out):
        self.out=out.resolve();self.out.mkdir(parents=True,exist_ok=False);(self.out/'blobs').mkdir();self.children=[];self.rows=[];self.request=0;self.snap=0;self.deadline=time.monotonic()+600;self.journals={}
    def event(self,case,value):
        value=dict(value,at=now());self.journals[case.name].append(value)
        with (case/'journal.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(value,sort_keys=True)+'\n')
    def snapshot(self,case,label):
        self.snap+=1;files={}
        for p in sorted((case/'fixture').rglob('*')):
            if p.is_file():
                if p.name=='authority.lock':continue
                b=p.read_bytes();h=sha(b);dest=self.out/'blobs'/h
                if not dest.exists():dest.write_bytes(b)
                files[p.relative_to(case/'fixture').as_posix()]=h
        lock=(case/'fixture/authority.lock').stat();self.event(case,{'kind':'snapshot','snapshot':self.snap,'label':label,'files':files,'lock_identity':{'device':lock.st_dev,'inode':lock.st_ino,'size':lock.st_size}});return files
    def note(self,case,name,actual,expected):
        require(actual==expected,name+': '+repr(actual));self.event(case,{'kind':'assertion','name':name,'actual':actual,'expected':expected});return actual
    def start_authority(self,case,instance,**kw):
        args=['--root',str(case/'fixture'),'--instance',instance]
        if kw.get('offset') is not None:args+=['--lock-offset',str(kw['offset'])]
        if kw.get('lock_only'):args+=['--lock-only']
        a=Child(self,case,'authority',args);a.until(ready=not kw.get('lock_only'),phase='lock:held' if kw.get('lock_only') else None);return a
    def rpc(self,case,a,op,cut=None,**fields):
        self.request+=1;r={'op':op,'request_id':self.request,**fields};self.snapshot(case,'before/'+op);a.send(r);reply=a.until(response=self.request,cut=cut);self.snapshot(case,'after/'+op);return reply
    def state(self,case):return load(case/'fixture/authority.json')
    def claim(self,case,a,owner='writer-a'):
        nonce=uuid.uuid4().hex;r=self.rpc(case,a,'claim',owner=owner,actor_nonce=nonce,expected_revision=self.state(case)['revision'],manifest_sha256=sha(F['artifacts'](2,self.state(case)['unit'])['manifest.json']));self.note(case,'claim-admitted',r['status'],'ok');return r['writer']
    def writer(self,case,t):
        p=case/(t['owner']+'-'+str(t['serial'])+'.json');p.write_bytes(encode(dict(t,unit=self.state(case)['unit'])));a=Child(self,case,'writer',['writer','--root',str(case/'fixture'),'--ticket',str(p)]);a.until(phase='writer:staged');return a
    def pin(self,case,a,owner='reader-a',cut=None):
        s=self.state(case);return self.rpc(case,a,'pin',generation=s['selected'],expected_revision=s['revision'],owner=owner,actor_nonce=uuid.uuid4().hex,cut=cut)
    def reader(self,case,t,point='reader:pinned'):
        p=case/(t['owner']+'-'+t['pin']+'.json');p.write_bytes(encode(t));a=Child(self,case,'reader',['reader','--root',str(case/'fixture'),'--ticket',str(p)]);a.until(phase=point);return a
    def finish_reader(self,case,a,t):
        a.resume(phase='reader:read');a.stop();self.note(case,'reader-exit',a.p.returncode,0)
        messages=[e['value'] for e in self.journals[case.name] if e['kind']=='receive' and e['child']==a.id];proof=next(v['observation'] for v in messages if 'observation' in v);self.note(case,'read-fixed-generation',proof['generation'],t['generation']);return proof
    def release(self,case,a,t,actor=None,reason='reader-complete'):
        if actor is not None and not actor.waited:
            self.event(case,{'kind':'lifetime-refusal','actor':actor.id,'pin':t,'reason':'owned-reader-not-waited'});return {'status':'refused','reason':'owned-reader-not-waited'}
        return self.rpc(case,a,'release_pin',pin=t,reason=reason)
    def publish(self,case,a,w):return self.rpc(case,a,'publish',writer=w)
    def case(self,rep,policy,unit,name):
        case=self.out/f'r{rep}-{policy}-{unit}-{name}';case.mkdir();self.journals[case.name]=[];instance=uuid.uuid4().hex;bootstrap(case/'fixture',unit,policy,instance);self.snapshot(case,'initial');a=self.start_authority(case,instance);self.note(case,'authority-ready',a.p.poll(),None)
        try:
            if name in ('overlap_pin','overlap_manifest','two_pins','restart_live_pin','reader_death','acquisition_race'):
                w=self.claim(case,a);writer=self.writer(case,w);t=self.pin(case,a)['pin'];reader=self.reader(case,t,'reader:manifest' if name=='overlap_manifest' else 'reader:pinned');t2=None
                if name=='two_pins':
                    t2=self.pin(case,a,'reader-b')['pin'];self.note(case,'third-pin-capacity',self.pin(case,a,'reader-c')['reason'],'pin-capacity')
                if name=='restart_live_pin':
                    a.stop(kill=True);a=self.start_authority(case,instance);self.note(case,'old-writer-after-restart',self.publish(case,a,w)['reason'],'stale-writer');self.note(case,'old-pin-after-restart',self.rpc(case,a,'validate_pin',pin=t)['status'],'ok');w=self.claim(case,a,'writer-b');newwriter=self.writer(case,w);newwriter.stop()
                r=self.publish(case,a,w);self.note(case,'publication-with-pins',r['status'],'busy' if policy=='drain-before-publish' else 'ok')
                if policy=='drain-before-publish':self.note(case,'drain-closes-new-admission',self.pin(case,a,'late-reader')['reason'],'drain-admission-closed')
                else:
                    self.note(case,'new-old-selection-refused',self.rpc(case,a,'pin',generation=1,expected_revision=0,owner='late-reader',actor_nonce=uuid.uuid4().hex)['reason'],'not-current-selection');self.note(case,'live-pin-blocks-reclaim',self.rpc(case,a,'reclaim')['reason'],'generation-pinned')
                if name=='acquisition_race':self.note(case,'stale-selection-between-select-and-pin',self.rpc(case,a,'pin',generation=1,expected_revision=0,owner='racing-reader',actor_nonce=uuid.uuid4().hex)['status'],'refused')
                if name=='reader_death':
                    self.note(case,'premature-reader-cleanup',self.release(case,a,t,reader)['status'],'refused');reader.stop(kill=True);self.note(case,'dead-pin-still-durable',self.rpc(case,a,'validate_pin',pin=t)['status'],'ok');self.release(case,a,t,reader,'controller-observed-death')
                else:self.finish_reader(case,reader,t);self.release(case,a,t,reader)
                if t2:
                    if policy=='pinned-generation':self.note(case,'second-pin-still-blocks',self.rpc(case,a,'reclaim')['reason'],'generation-pinned')
                    else:self.note(case,'second-pin-still-drains',self.publish(case,a,w)['status'],'busy')
                    reader2=self.reader(case,t2);self.finish_reader(case,reader2,t2);self.release(case,a,t2,reader2)
                if policy=='drain-before-publish':self.note(case,'publish-after-drain',self.publish(case,a,w)['status'],'ok')
                writer.stop();self.note(case,'reclaim-after-release',self.rpc(case,a,'reclaim')['status'],'ok');self.note(case,'old-files-removed',(case/'fixture/store/g1').exists(),False)
            elif name in ('stale_writer_cancel','publisher_death'):
                w=self.claim(case,a);writer=self.writer(case,w)
                if name=='publisher_death':writer.stop(kill=True)
                self.rpc(case,a,'revoke_writer',writer=w,reason='controller-observed-death' if name=='publisher_death' else 'owner-cancel');w2=self.claim(case,a,'writer-b');writer2=self.writer(case,w2);self.note(case,'same-term-stale-permit',self.publish(case,a,w)['reason'],'stale-writer');self.note(case,'replacement-publisher',self.publish(case,a,w2)['status'],'ok');writer.stop();writer2.stop()
            elif name in ('pin_staged_loss','pin_reply_loss'):
                self.pin(case,a,cut='pin:staged' if name=='pin_staged_loss' else 'pin:committed');a=self.start_authority(case,instance);expected=0 if name=='pin_staged_loss' else 1;self.note(case,'pin-survives-only-commit',len(self.state(case)['pins']),expected)
                if expected:
                    t=next(iter(self.state(case)['pins'].values()));self.note(case,'orphan-pin-valid',self.rpc(case,a,'validate_pin',pin=t)['status'],'ok');self.release(case,a,t,reason='owner-cancel')
            elif name in ('publish_staged_loss','publish_reply_loss','retire_intent_loss','retire_partial_loss'):
                w=self.claim(case,a);writer=self.writer(case,w)
                if name.startswith('publish_'):
                    self.rpc(case,a,'publish',writer=w,cut='publish:staged' if name=='publish_staged_loss' else 'publish:committed');a=self.start_authority(case,instance);self.note(case,'publication-commit-survives',self.state(case)['selected'],1 if name=='publish_staged_loss' else 2);self.note(case,'old-publish-retry-refused',self.publish(case,a,w)['reason'],'stale-writer')
                else:
                    self.publish(case,a,w);self.rpc(case,a,'reclaim',cut='retire:committed' if name=='retire_intent_loss' else 'reclaim:first_deleted');self.note(case,'reclaim-intent-survives',self.state(case)['generations']['1']['status'],'retiring');a=self.start_authority(case,instance);self.note(case,'reclamation-recovered',self.state(case)['generations']['1']['status'],'removed');self.note(case,'recovery-deleted-only-old',(case/'fixture/store/g1').exists(),False);self.note(case,'repeat-reclaim-idempotent',self.rpc(case,a,'reclaim')['already_removed'],True)
                writer.stop()
            elif name=='lock_exclusion':
                other=self.start_authority(case,instance);self.note(case,'second-authority-lock-refused',other.p.returncode,3);control=self.start_authority(case,instance,offset=1,lock_only=True);self.note(case,'wrong-offset-is-ineffective',control.held,'lock:held');control.stop();before=self.state(case)['boot'];a.stop(kill=True);a=self.start_authority(case,instance);self.note(case,'lock-reacquired-after-wait',self.state(case)['boot'],before+1)
            elif name=='negative_tokens':
                t=self.pin(case,a)['pin'];bad=dict(t,owner='other');self.note(case,'wrong-holder-refused',self.rpc(case,a,'release_pin',pin=bad,reason='reader-complete')['reason'],'invalid-pin');bad=dict(t,instance='other');self.note(case,'transplanted-pin-refused',self.rpc(case,a,'validate_pin',pin=bad)['reason'],'invalid-pin');self.note(case,'duplicate-holder-refused',self.pin(case,a)['reason'],'duplicate-reader');self.release(case,a,t,reason='owner-cancel');self.note(case,'released-pin-refused',self.rpc(case,a,'validate_pin',pin=t)['reason'],'invalid-pin');w=self.claim(case,a);writer=self.writer(case,w);bad=dict(w,manifest_sha256='0'*64);self.note(case,'substituted-publisher-digest',self.publish(case,a,bad)['reason'],'stale-writer');bad=dict(w,parent_revision=99);self.note(case,'substituted-parent',self.publish(case,a,bad)['reason'],'stale-writer');self.note(case,'valid-publication',self.publish(case,a,w)['status'],'ok');writer.stop();self.note(case,'two-generation-backpressure',self.rpc(case,a,'claim',owner='extra',actor_nonce=uuid.uuid4().hex,expected_revision=1,manifest_sha256='0'*64)['reason'],'domain-generation-limit')
            a.stop();self.snapshot(case,'final');row={'case':case.name,'policy':policy,'unit':unit,'schedule':name,'checks':[{'name':e['name'],'value':e['actual']} for e in self.journals[case.name] if e['kind']=='assertion'],'final_selected':self.state(case)['selected'],'final_old_status':self.state(case)['generations']['1']['status']};self.rows.append(row);(case/'result.json').write_bytes(encode(row))
        finally:
            for child in self.children:
                if child.case==case and not child.waited:child.stop(kill=True)
    def run(self):
        try:
            for rep in range(2):
                for policy in ('drain-before-publish','pinned-generation'):
                    for unit in ('event','utf8-byte'):
                        for name in CASES:self.case(rep,policy,unit,name)
            require(time.monotonic()<self.deadline,'whole-timeout');require(sum(p.stat().st_size for p in self.out.rglob('*') if p.is_file())<67108864,'artifact-limit')
            return {'status':'named-concurrent-schedules-pass','case_count':len(self.rows),'helper_process_count':len(self.children),'all_helpers_waited':all(p.waited for p in self.children),'live_provider_calls':0,'formal_freeze':False,'production_authentication_established':False,'power_loss_durability_established':False,'rows':self.rows}
        finally:
            for child in self.children:
                if not child.waited:child.stop(kill=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();c=Campaign(pathlib.Path(a.output))
    try:r=c.run();(c.out/'result.json').write_bytes(encode(r));print(json.dumps({k:v for k,v in r.items() if k!='rows'}))
    except Exception as exc:(c.out/'failure.json').write_bytes(encode({'error':repr(exc),'completed_cases':len(c.rows)}));raise

"""Single cooperating-process fixture authority; private IPC is the trust boundary."""
import argparse,copy,errno,msvcrt,os,pathlib,sys,time
from support import load,save,sha,require,emit,phase,scope
from verify import verify
class Authority:
    def __init__(self,root,instance):self.root=root;self.instance=instance;self.state=load(root/'authority.json');self.validate()
    def validate(self):
        s=self.state;require(set(s)==set('version instance unit policy boot revision selected writer_seq writer pin_seq pins draining generations'.split()),'state-shape');require(s['version']==1 and s['instance']==self.instance and s['unit'] in ('event','utf8-byte') and s['policy'] in ('drain-before-publish','pinned-generation'),'state-identity')
        require(type(s['boot'])is int and s['boot']>=0 and s['selected'] in (1,2) and s['revision']==s['selected']-1 and len(s['pins'])<=2,'state-bounds')
        require(s['generations'][str(s['selected'])]['status']=='current','selected-state')
        for key,p in s['pins'].items():require(p['pin']==key and p['instance']==self.instance and s['generations'][str(p['generation'])]['status'] in ('current','retained'),'persisted-pin')
        if s['generations']['1']['status'] in ('retiring','removed'):require(not any(p['generation']==1 for p in s['pins'].values()),'retiring-with-pins')
    def commit(self,s,op):
        save(self.root/'authority.tmp',s);phase(op+':staged');os.replace(self.root/'authority.tmp',self.root/'authority.json');self.state=s;phase(op+':committed')
    def boot(self):
        s=copy.deepcopy(self.state);s['boot']+=1;s['writer']=None;s['draining']=False;self.commit(s,'boot')
        if self.state['generations']['1']['status']=='retiring':self.delete_retiring()
        emit({'ready':True,'pid':os.getpid(),'state':self.state})
    def ticket(self,g):
        d=self.state['generations'][str(g)];return {'generation':g,'unit':self.state['unit'],'directory':d['directory'],'manifest_sha256':d['manifest_sha256']}
    def delete_retiring(self):
        require(self.state['generations']['1']['status']=='retiring' and not any(p['generation']==1 for p in self.state['pins'].values()),'reclaim-state')
        directory=scope(self.root/'store',self.root/'store'/self.state['generations']['1']['directory']);require(directory.name=='g1','reclaim-directory')
        names=['event1.json','event2.json','event3.json','manifest.json','snapshot.json']
        if directory.exists():
            require(not directory.is_symlink() and not directory.stat().st_file_attributes&0x400,'reclaim-reparse');require(set(p.name for p in directory.iterdir())<=set(names),'unexpected-reclaim-member')
            phase('reclaim:before_delete')
            for i,n in enumerate(names):
                p=scope(directory,directory/n)
                if p.exists():require(p.is_file() and not p.is_symlink() and not p.stat().st_file_attributes&0x400,'reclaim-member');p.unlink()
                if i==0:phase('reclaim:first_deleted')
            directory.rmdir()
        s=copy.deepcopy(self.state);s['generations']['1']['status']='removed';self.commit(s,'reclaim')
    def command(self,r):
        op=r['op'];s=copy.deepcopy(self.state)
        if op=='status':return {'status':'ok','state':s}
        if op=='claim':
            require(s['selected']==1,'domain-generation-limit');require(s['writer'] is None,'writer-busy');require(r['expected_revision']==s['revision'],'stale-parent')
            s['writer_seq']+=1;w={'instance':self.instance,'boot':s['boot'],'serial':s['writer_seq'],'owner':r['owner'],'actor_nonce':r['actor_nonce'],'parent_revision':s['revision'],'generation':2,'directory':f'g2-t{s["boot"]}-w{s["writer_seq"]}','manifest_sha256':r['manifest_sha256']};s['writer']=w;self.commit(s,'claim');return {'status':'ok','writer':w}
        if op in ('publish','revoke_writer'):
            require(s['writer'] is not None and r['writer']==s['writer'],'stale-writer')
            if op=='revoke_writer':
                require(r['reason'] in ('owner-cancel','controller-observed-death'),'revocation-reason');s['writer']=None;s['draining']=False;self.commit(s,'revoke_writer');return {'status':'ok'}
            require(s['writer']['parent_revision']==s['revision'] and s['writer']['boot']==s['boot'],'stale-parent')
            verify(self.root/'store',dict(s['writer'],unit=s['unit']))
            if s['policy']=='drain-before-publish' and s['pins']:
                s['draining']=True;self.commit(s,'drain');return {'status':'busy','reason':'reader-pins','state':s}
            w=s['writer'];s.update(selected=2,revision=1,writer=None,draining=False);s['generations']['1']['status']='retained';s['generations']['2']={'status':'current','directory':w['directory'],'manifest_sha256':w['manifest_sha256']};self.commit(s,'publish');return {'status':'ok','state':s}
        if op=='pin':
            require(not s['draining'],'drain-admission-closed');require(r['generation']==s['selected'] and r['expected_revision']==s['revision'],'not-current-selection');require(len(s['pins'])<2,'pin-capacity');require(not any(p['owner']==r['owner'] for p in s['pins'].values()),'duplicate-reader')
            s['pin_seq']+=1;p=dict(self.ticket(s['selected']),instance=self.instance,pin=f'p{s["pin_seq"]}',owner=r['owner'],actor_nonce=r['actor_nonce']);s['pins'][p['pin']]=p;self.commit(s,'pin');return {'status':'ok','pin':p}
        if op in ('validate_pin','release_pin'):
            p=r['pin'];require(s['pins'].get(p.get('pin'))==p,'invalid-pin')
            if op=='validate_pin':return {'status':'ok','pin':p}
            require(r['reason'] in ('reader-complete','owner-cancel','controller-observed-death'),'release-reason');del s['pins'][p['pin']];self.commit(s,'release_pin');return {'status':'ok'}
        if op=='reclaim':
            require(s['selected']==2,'cannot-reclaim-current');require(not any(p['generation']==1 for p in s['pins'].values()),'generation-pinned')
            if s['generations']['1']['status']=='removed':return {'status':'ok','already_removed':True}
            s['generations']['1']['status']='retiring';self.commit(s,'retire');self.delete_retiring();return {'status':'ok','state':self.state}
        raise ValueError('unknown-command')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--instance',required=True);p.add_argument('--lock-offset',type=int,default=0);p.add_argument('--lock-only',action='store_true');a=p.parse_args();root=pathlib.Path(a.root).resolve();fd=os.open(root/'authority.lock',os.O_RDWR|os.O_BINARY);locked=False;attempts=[];began=time.monotonic()
    try:
        while True:
            os.lseek(fd,a.lock_offset,os.SEEK_SET)
            try:msvcrt.locking(fd,msvcrt.LK_NBLCK,1);locked=True;break
            except OSError as exc:
                attempts.append({'errno':exc.errno,'winerror':getattr(exc,'winerror',None)})
                if exc.errno!=errno.EACCES or time.monotonic()-began>=.5:emit({'status':'lock-refused','errors':attempts,'pid':os.getpid()});return 3
                time.sleep(.01)
        emit({'lock_acquired':True,'offset':a.lock_offset,'attempts':len(attempts)+1,'errors':attempts,'elapsed_seconds':time.monotonic()-began,'pid':os.getpid()})
        if a.lock_only:phase('lock:held');return 0
        authority=Authority(root,a.instance);authority.boot()
        for line in sys.stdin:
            request=__import__('json').loads(line)
            if request['op']=='exit':emit({'status':'exited'});return 0
            try:reply=authority.command(request)
            except (ValueError,OSError,KeyError,TypeError) as exc:reply={'status':'refused','reason':str(exc)}
            emit({'response':reply,'request_id':request['request_id']})
    finally:
        if locked:os.lseek(fd,a.lock_offset,os.SEEK_SET);msvcrt.locking(fd,msvcrt.LK_UNLCK,1)
        os.close(fd)
if __name__=='__main__':raise SystemExit(main())

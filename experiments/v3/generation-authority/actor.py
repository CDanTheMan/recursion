"""Owned staging writer or pinned reader; scheduled through private stdin phases."""
import argparse,json,os,pathlib,sys
from support import F,load,emit,phase,require,scope
from verify import verify
def main():
    p=argparse.ArgumentParser();p.add_argument('role',choices=['writer','reader']);p.add_argument('--root',required=True);p.add_argument('--ticket',required=True);a=p.parse_args();root=pathlib.Path(a.root).resolve();t=load(a.ticket);emit({'started':True,'role':a.role,'pid':os.getpid(),'ticket':t})
    if a.role=='writer':
        directory=scope(root/'store',root/'store'/t['directory']);directory.mkdir();files=F['artifacts'](2,t['unit'])
        for name,b in files.items():
            with (directory/name).open('wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
        emit({'proposal':{k:v for k,v in t.items() if k!='unit'}});phase('writer:staged')
    else:
        phase('reader:pinned');proof=verify(root/'store',t,after_manifest=lambda:phase('reader:manifest'));emit({'observation':proof,'ticket':t});phase('reader:read')
    emit({'finished':True,'pid':os.getpid()})
if __name__=='__main__':
    try:main()
    except Exception as exc:emit({'status':'actor-refused','reason':str(exc),'pid':os.getpid()});raise SystemExit(2)

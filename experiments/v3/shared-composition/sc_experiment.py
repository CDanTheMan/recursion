"""Provider-free bounded composition and literal mapping experiment."""
import argparse,ctypes,datetime,gc,json,pathlib,sys,time
from dataclasses import asdict
import sc_domain as d,sc_explore as ex

ROOT=pathlib.Path(__file__).resolve().parents[3]
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def peak_bytes():
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
    c=Counters();c.cb=ctypes.sizeof(c)
    ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(-1),ctypes.byref(c),c.cb)
    return c.PeakWorkingSetSize

WITNESSES={
 'old-cut-new-attempt':lambda s:s.phase==5 and s.snapshot[2]==1 and s.cut==2 and s.hold,
 'reader-reclaim-install':lambda s:s.phase==5 and s.snapshot[0]==1 and s.residents==2 and s.waited,
 'writer-serial-and-boot':lambda s:s.g==2 and s.term==2 and s.serial==2 and s.reply,
 'writer-stale-boot':lambda s:s.g==2 and s.term==2,
 'writer-unstaged':lambda s:s.g==2,
 'queue-gap-stop':lambda s:s.phase==5 and s.loss>0 and s.stopped,
 'late-evidence-local-death':lambda s:s.cut==1 and s.phase==5 and s.snapshot[2]==0 and s.actor==2 and not s.pin,
 'conflict-pause':lambda s:s.cut==3 and s.phase==5 and s.paused and s.write_result==2,
 'reset-restart-future-output':lambda s:s.phase==5 and s.restarted and s.cut==2 and s.snapshot[2]==1 and s.queue==(2,),
 'reset-incarnation-accounting':lambda s:s.phase==5 and s.closed2 and s.spent==2 and s.reset and s.ack==1,
 'pre-ingress-gap':lambda s:s.phase==5 and s.loss>0,
 'ownership-probes':lambda s:s.residents==2 and not s.pin and s.capsule,
 'recipient-refusal':lambda s:s.cut==4 and s.remote==3 and not s.hold,
}
MUTANTS={
 'replay-settlement':'old-cut-new-attempt','status-only-hold':'old-cut-new-attempt',
 'pending-only-hold':'conflict-pause','invocation-release':'ownership-probes',
 'other-reader-release':'reader-reclaim-install','copy-release':'reader-reclaim-install',
 'reclaim-reader':'reader-reclaim-install','reclaim-history':'ownership-probes',
 'reclaim-invocation':'ownership-probes','stale-term':'writer-stale-boot',
 'stale-serial':'writer-serial-and-boot','unstaged':'writer-unstaged',
 'gap-order':'queue-gap-stop','reset-order':'reset-restart-future-output',
 'future-loss':'reset-restart-future-output','control-pressure':'queue-gap-stop',
 'recipient-fence':'recipient-refusal','local-death':'late-evidence-local-death',
 'quarantine-clear':'conflict-pause','ack-completion':'reset-incarnation-accounting',
 'reset-spend':'reset-incarnation-accounting','emission-install':'reset-restart-future-output'
}

def literal():
    sys.path.insert(0,str(ROOT/'experiments/v3/effect-evidence'))
    import ee_cases,ee_join,ee_experiment
    # Public deterministic fixture bytes, not credentials or production keys.
    keys={role:bytes([i])*32 for i,role in enumerate(('collector','dispatcher','observer'),1)}
    expected={
      'success':('succeeded',[],False),'late-receipt':('succeeded',[],False),
      'later-start-only':('succeeded',['attempt:2'],True),
      'later-unresolved':('ambiguous',['attempt:2'],True),
      'prior-unresolved':('ambiguous',['attempt:1'],True),
      'conflict':('ambiguous',[],True),'stale-paused':('succeeded',[],False)
    };actual={}
    for name,(status,pending,hold) in expected.items():
        original=ee_cases.unsigned(name);result=ee_join.join(ee_cases.package(original,keys),keys)
        ex.audit.need((result['current']['status'],result['unsettled_attempt_ids'],result['runtime_settlement_hold'])==(status,pending,hold),'frozen literal mapping '+name)
        ex.audit.need(result['runtime_permission'] is False and result['canonical_write_count']==0,'classification never runtime permission')
        actual[name]={'status':status,'pending':pending,'hold':hold,'runtime_permission':False,'canonical_writes':0}
    return {'mappings':actual,'actual_m1a_controls':ee_experiment.literal_controls()}

def run(directory,limits):
    profiles={};total=0;began=time.monotonic()
    for name in d.PROFILES:
        av,ag,parents=ex.explore(name,'inclusive',limit=limits['states_per_boundary'],seconds=limits['seconds_per_experiment'])
        bv,bg,_=ex.explore(name,'split',limit=limits['states_per_boundary'],seconds=limits['seconds_per_experiment'])
        ex.audit.need(av==bv and ag==bg,'exact state AND edge correspondence '+name)
        witnesses=[]
        for i,s in enumerate(av):
            if WITNESSES[name](s):
                witnesses.append({'name':name,'trace':ex.path(parents,i),'state':asdict(s)});break
        ex.audit.need(witnesses,'required composed ordered witness '+name)
        if name=='reader-reclaim-install':
            found=None
            for i,s in enumerate(av):
                if s.reader==1 and s.g==2 and not s.pin and s.capsule:
                    for action,j in ag[i]:
                        if action=='reclaim_early' and av[j].residents==s.residents:
                            found={'name':'reclaim-blocked-by-independent-reader','trace':ex.path(parents,i)+[action],'state':asdict(av[j])};break
                if found:break
            ex.audit.need(found,'blocked reader reclaim witness');witnesses.append(found)
        if name=='queue-gap-stop':
            index=next((i for i,s in enumerate(av) if len(s.queue)==2 and s.stopped),None)
            ex.audit.need(index is not None,'Stop with saturated queue');witnesses.append({'name':'saturated-queue-Stop','trace':ex.path(parents,index),'state':asdict(av[index])})
        if name=='recipient-refusal':
            index=next((i for i,s in enumerate(av) if s.stopped and s.fence==1 and s.remote==1),None)
            ex.audit.need(index is not None,'Stop before recipient installation exposure');witnesses.append({'name':'Stop-before-recipient-install','trace':ex.path(parents,index),'state':asdict(av[index])})
        profiles[name]={'inclusive':ex.graph_receipt(av,ag),'split':ex.graph_receipt(bv,bg),'exact_graph_equal':True,'witnesses':witnesses}
        total+=len(av)
        ex.audit.need(total<=limits['states_per_boundary'],'total declared profile state admission')
        ex.audit.need(peak_bytes()<=limits['memory_bytes'] and time.monotonic()-began<=limits['seconds_per_experiment'],'profile resource bounds')
        write(directory/'progress.json',profiles);print(name+' '+str(len(av))+' states',flush=True)
        del av,ag,bv,bg,parents;gc.collect()
    mutants=[]
    for guard,profile in MUTANTS.items():
        mutants.append(ex.explore(profile,'inclusive',mutant=guard,limit=limits['states_per_boundary'],seconds=limits['seconds_per_experiment']))
        write(directory/'mutants.json',mutants)
    return {'status':'shared-composition-pass','classification':'modeled','profiles':profiles,'states_per_boundary':total,
      'mutants':mutants,'calibrations':ex.calibrate(),'literal':literal(),'formal_freeze':False,
      'full_comparison_complete':False,'runtime_integration_support':False,'live_provider_calls':0,'new_owner_questions':[]}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=pathlib.Path);a=parser.parse_args()
    if a.output.exists():raise ValueError('fresh output required')
    limits=json.loads((ROOT/'docs/v3/construction/shared-composition-20260908/plan.json').read_text())['limits']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();code=0
    try:result=run(a.output.parent,limits)
    except Exception as e:result={'status':'incomplete-or-checker-failure','detail':type(e).__name__+': '+str(e),'formal_freeze':False};code=1
    write(a.output,{'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-t,'peak_bytes':peak_bytes(),'result':result})
    print(json.dumps({'status':result['status'],'detail':result.get('detail'),'seconds':time.monotonic()-t}),flush=True)
    return code
if __name__=='__main__':raise SystemExit(main())

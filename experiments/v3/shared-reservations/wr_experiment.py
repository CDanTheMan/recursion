"""Admitted provider-free experiment. Its output is modeled evidence only."""
import argparse,ctypes,datetime,gc,json,pathlib,time
import wr_domain as d,wr_explore as ex,wr_audit as audit

ROOT=pathlib.Path(__file__).resolve().parents[3]
MUTANTS={
 'serialization':('stale-read-race','central'),
 'ambiguity':('lost-receipt-restart','central'),
 'restart-release':('lost-receipt-restart','central'),
 'exit-reservation':('local-lifetime','central'),
 'quota-reservation':('local-lifetime','central'),
 'quota-lifetime':('local-lifetime','central'),
 'snapshot-reservation':('snapshot-uncertainty','central'),
 'snapshot-rights':('transfer-interruption','rights'),
 'foreign-release':('owner-and-identity','central'),
 'owner-binding':('owner-and-identity','central'),
 'payload-binding':('owner-and-identity','central'),
 'classification-release':('success-consumption','central'),
 'conflict-hold':('classification-hold','central'),
 'settlement-idempotence':('lost-receipt-refusal','central'),
 'durable-debit':('transfer-interruption','rights'),
 'duplicate-credit':('transfer-interruption','rights'),
 'timeout-reclaim':('transfer-free','rights'),
}

def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def peak_bytes():
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ('peak','working','pp','p','np','n','page','peakpage')]
    c=Counters();c.cb=ctypes.sizeof(c)
    if not ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(-1),ctypes.byref(c),c.cb):raise OSError('cannot measure process memory')
    return c.peak

def witness_check(name,design,w):
    s=w['final'];events={e['label'].split('=')[0]:e for e in w['events']}
    if name in ('free-admission','stale-read-race'):
        if design=='central':audit.require(s['reserved']==(6,0) and events['reserve1']['label']=='reserve1=denied','original central6+6 schedule')
        else:audit.require(s['reserved']==(0,0),'initial5/5 rights cannot serve six')
    elif name in ('free-reservation-core','lost-receipt-restart','owner-and-identity','snapshot-uncertainty','local-lifetime','pin-and-reservation'):
        audit.require(s['reserved']==(6,0) and s['sent']==(1,0) and s['receipt']==(0,0) and s['classification']==(0,0),'same unknown operation reservation survives')
        if 'resend0' in events:audit.require(events['resend0']['label']=='resend0=blocked','no blind resend')
        if name=='snapshot-uncertainty':audit.require(s['installed'][2]==(0,0) and s['reserved']==(6,0),'old snapshot distinct from current reservation')
        if name=='local-lifetime':audit.require(s['lifetime']==(1,1) and s['quota_epoch']==1 and s['boot']==1,'independent lifetime/reset/restart')
        if name=='pin-and-reservation':audit.require(s['generation']==2 and not s['reader_pin'] and s['reserved']==(6,0),'pin release is not reservation release')
    elif name=='success-consumption':audit.require(s['consumed']==(6,0) and s['reserved']==(0,0) and sum(s['free'])==4,'success consumes budget once')
    elif name=='lost-receipt-refusal':
        audit.require(s['consumed']==(0,0) and s['reserved'][0]==0 and s['issued']&1,'terminal nonexecution releases with tombstone')
        audit.require(events['settle_again0']['label']=='settle_again0=duplicate','settlement idempotent')
    elif name=='classification-hold':audit.require(s['reserved']==(6,0) and s['classification']==(1,0) and s['conflict']==1,'classification success and conflict hold differ')
    elif name.startswith('transfer'):
        if design=='rights':audit.require(s['transfer']==2 and sum(s['reserved'])==6,'durable transfer enables six exactly once')
    elif name=='receipt-and-local-interleavings':audit.require(s['consumed']==(6,0),'receipt settlement despite local restart')
    else:raise ValueError('uncovered witness '+name)

def run(directory,limits):
    profiles={};totals={x:0 for x in ('central','rights')};began=time.monotonic()
    for name in d.PROFILES:
        profiles[name]={}
        for design in ('central','rights'):
            av,ag=ex.explore(name,design,'inclusive',limit=limits['states_per_boundary'],seconds=limits['seconds_per_experiment'])
            bv,bg=ex.explore(name,design,'split',limit=limits['states_per_boundary'],seconds=limits['seconds_per_experiment'])
            audit.require(av==bv and ag==bg,'complete representation graph correspondence')
            w=ex.witness(name,design);witness_check(name,design,w)
            profiles[name][design]={'inclusive':ex.receipt(av,ag),'split':ex.receipt(bv,bg),'exact_graph_equal':True,'witness':w}
            totals[design]+=len(av);audit.require(totals[design]<=limits['states_per_boundary'],'sum of declared profiles exceeds admission')
            audit.require(time.monotonic()-began<=limits['seconds_per_experiment'] and peak_bytes()<=limits['memory_bytes'],'admitted experiment resources')
            print(name+'/'+design+' '+str(len(av))+' states',flush=True)
            del av,ag,bv,bg;gc.collect()
        write(directory/'progress.json',profiles)
    mutants=[]
    for guard,(profile,design) in MUTANTS.items():
        mutants.append(ex.explore(profile,design,'inclusive',mutant=guard));write(directory/'mutants.json',mutants)
    comparison={'central_initial_six':'admitted','rights_initial_six':'denied','rights_after_one_durable_transfer':'admitted at destination','relation':'exact correspondence between representations within each design; different admission availability across designs','fairness_assumed':False,'one_transfer_duplicate_control':'conservation failure; not the two-transfer12-unit oversubscription schedule'}
    return {'status':'shared-reservations-pass','classification':'modeled','profiles':profiles,'states_per_design_per_boundary':totals,'mutants':mutants,'calibrations':ex.calibrate(),'comparison':comparison,'formal_freeze':False,'full_comparison_complete':False,'runtime_integration_support':False,'live_provider_calls':0,'new_owner_questions':[]}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=pathlib.Path);a=parser.parse_args()
    if a.output.exists():raise ValueError('fresh output required')
    limits=json.loads((ROOT/'docs/v3/construction/shared-reservations-20260908/plan.json').read_text())['limits']
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();code=0
    try:result=run(a.output.parent,limits)
    except Exception as e:result={'status':'incomplete-or-checker-failure','detail':type(e).__name__+': '+str(e),'formal_freeze':False};code=1
    write(a.output,{'started_at':start,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-t,'peak_bytes':peak_bytes(),'result':result})
    print(json.dumps({'status':result['status'],'detail':result.get('detail'),'seconds':time.monotonic()-t}),flush=True);return code
if __name__=='__main__':raise SystemExit(main())

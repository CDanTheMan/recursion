"""Admitted finite computation; no provider/network or child process operations."""
import argparse,datetime,json,pathlib,time
import cm_explore

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=pathlib.Path);a=parser.parse_args()
    if a.output.exists():raise ValueError('result already exists')
    plan=json.loads((pathlib.Path(__file__).resolve().parents[3]/'docs/v3/construction/composition-model-20260908/plan.json').read_text())
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter();code=0
    try:result=cm_explore.run(plan['limits'])
    except cm_explore.Limit as e:result={'status':'exploration-limit','detail':str(e),'formal_freeze':False};code=2
    except Exception as e:result={'status':'checker-error','detail':type(e).__name__+': '+str(e),'formal_freeze':False};code=1
    receipt={'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.perf_counter()-t,'peak_bytes':cm_explore.peak_bytes(),'result':result}
    a.output.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':result['status'],'seconds':receipt['seconds'],'peak_bytes':receipt['peak_bytes']}),flush=True)
    return code
if __name__=='__main__':raise SystemExit(main())

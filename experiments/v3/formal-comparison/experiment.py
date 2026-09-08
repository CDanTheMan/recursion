"""Run finite models and proof-method controls; output goes to an admitted external path."""
import argparse,datetime,json,pathlib,sys,time
import calibrations,explore

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args()
    if args.output.exists():raise ValueError('Refuse to overwrite a prior run result')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();clock=time.perf_counter()
    result={'started_at':started,'kind':'finite-subsystem-model-experiment','live_provider_calls':0,'formal_freeze':False}
    code=0
    try:
        result['calibrations']=calibrations.run()
        result['models']=explore.run()
        result['status']=result['models']['status']
        if result['status']!='conditional-subsystem-pass':code=1
    except explore.ExplorationLimit as exc:result.update(status='exploration-limit',detail=str(exc));code=2
    except Exception as exc:result.update(status='checker-error',detail=type(exc).__name__+': '+str(exc));code=1
    result['ended_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();result['elapsed_seconds']=round(time.perf_counter()-clock,6)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print('FORMAL_MODEL_EXPERIMENT '+json.dumps({'status':result['status'],'seconds':result['elapsed_seconds'],'output':str(args.output)}),flush=True)
    return code

if __name__=='__main__':raise SystemExit(main())

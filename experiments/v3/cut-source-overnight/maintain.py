"""Sole-integrator metadata maintenance; never invokes model work or publication."""
import argparse
import json
from pathlib import Path
import run_packet as r

def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=('initialize','inventory','usage','checkpoint'));p.add_argument('--used',type=int);a=p.parse_args()
    root=r.ROOT; area=root/r.PREFIX
    if a.operation=='usage':
        assert a.used is not None and 0<=a.used<=100
        r.write(r.cache()/'usage.json',{'checked_at':r.now().isoformat(),'used_percent':a.used,'remaining_percent':100-a.used,'shared_account':True,'binding_windows':'one reported codex weekly window; secondary unavailable','new_metered_spend':0,'reset_credits_used':0})
    elif a.operation=='initialize':
        prior=r.read(root/'docs/v3/construction/cut-publication-20260908/coverage.json')
        coverage={'predecessor_coverage':prior,'formal_freeze':False,'full_comparison_complete':False,
                  'slice_obligations':[dict(x,status='no-new-coverage',support='Pending new evidence; preserve complete predecessor support.',result=None,profiles=[]) for x in prior['slice_obligations']],
                  'slice_traces':[dict(x,status='no-new-coverage',support='Pending new evidence; preserve complete predecessor support.',result=None,profiles=[]) for x in prior['slice_traces']]}
        r.write(area/'coverage.json',coverage)
        r.write(area/'preflight.json',{'status':'passed-scope-and-resource-preflight','baseline':'ec4232e95722d58dc0eff03289fb629b58d29247',
            'pr109':'MERGED; head e4b844b1af6c309263812c6961ccb50b3e5b8a82; master ec4232e95722d58dc0eff03289fb629b58d29247 verified via fetch and gh',
            'preparation_candidate':'ab9fbd7525849a75ac13443ed5a37683a4d570b6','predecessor_hashes_verified':245,
            'parent_active':True,'operational_pause_absent':True,'free_physical_kib':33982248,'total_physical_kib':66187496,
            'free_disk_bytes':657777278976,'used_percent':31,'remaining_percent':69,'new_metered_spend':0,'reset_credits_used':0,
            'readiness':'new gate and model sources must be committed before any admitted experiment','input_files':371,
            'original_comparison':'six obligations,27 traces,eight families,six cross-area and native/upstream-only/combined preserved; no full comparison claim',
            'reading':'CONTROL_PLANE, CLAUDE/AGENTS, ANCHOR, active parent, full predecessor packet parsed including losslessly unpacked results and preserved coverage; original comparison and affected canonical contracts reviewed'})
        r.write(area/'plan.json',{'parent_goal':'goal-recursion-v2-execution-fabric','status':'preregistered-before-first-model-run',
            'limits':r.read(area/'goal.json')['experiment_limits'],'queue_order':['source_authority','coupled_adversarial','bounded_scaling'],
            'profiles':'s_domain.PROFILES literal schedules, policies, outcomes and queue labels; commit identity in each admission',
            'domains':{'source_incarnations':[0,1],'original_attempts':[1,2],'record_inventory_lengths':[2,3,4],'reader_slots':2,'pool':10,'requests':[6,6],'cursor_units':['event','utf8-byte'],'event_lengths':[1,2,1,2]},
            'orders':'Every topological ordering of declared six-action cores; ordered prefixes retain all actions. No full original Cartesian claim.',
            'coverage':'complete finite declared domain only; all inherited support preserved separately','historical_command_timeout_seconds':600})
        r.write(area/'method-review.json',{'status':'primary-source-read-only-packet-complete; construction challenge and final exact reviews pending',
            'worker':'source_protocol_research','writes':False,'nested_delegation':False,'conclusions':['registration participates in currentness','pending attempt requires explicit hold or atomic start','source truth beyond admission remains a premise']})
    elif a.operation=='inventory':
        inv=r.read(area/'validation-inventory.json')
        paths=set(r.git('diff','--name-only',inv['start_commit']).decode().splitlines())
        paths.update(r.git('ls-files','--others','--exclude-standard').decode().splitlines())
        paths.discard(r.PREFIX+'validation-inventory.json')
        inv['artifacts']={path:r.sha((root/path).read_bytes().replace(b'\r\n',b'\n')) for path in sorted(paths)}
        r.write(area/'validation-inventory.json',inv)
    else:
        r.scope(expensive=False,final=True)
        r.write(area/'checkpoint.json',{'status':'incomplete-construction','at':r.now().isoformat(),'head':r.git('rev-parse','HEAD').decode().strip(),
            'dirty':r.git('status','--porcelain').decode().splitlines(),'started_at':'2026-09-09T03:40:33Z','discovery_cutoff_utc':'2026-09-09T12:40:33Z','deadline_utc':'2026-09-09T15:40:33Z',
            'queue_item':'source_authority','admitted_runs':[p.name for p in (r.cache()/'discovery').glob('*')] if (r.cache()/'discovery').exists() else [],
            'owned_processes':[],'workers':'source_protocol_research finished read-only; none running','hypothesis':'registration+append revision and exact ordinal/registry coverage establish bounded complete current source','residuals':'all nonmodeled source truth and original comparison remain open',
            'publication':'not-ready','next_command':'Run committed source_authority packet after gate preflight and fresh usage; retain any failures'})

if __name__=='__main__': main()

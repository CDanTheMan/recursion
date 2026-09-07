"""Exact-candidate gate. Validation replays evidence, never a live model/harness."""
import argparse,copy,datetime,json,os,pathlib,re,runpy,subprocess,sys,time,tomllib
from urllib.parse import urlsplit
from evidence_tools import project,require,sha,codex_projection,hermes_projection,ownership_projection,stderr_json
from contract_vectors import campaign as vectors
from release import validate as validate_release
ROOT=pathlib.Path(__file__).resolve().parents[3]
PREFIX='docs/v3/construction/interface-probes-20260907/'
CODE='experiments/v3/interface-probes/'
AREA=ROOT/PREFIX
START='840599ae60a7dadacc8b6ac2eac29ca0734c2a1d'
RESEARCH='51733c48537d91ad17774b0c05c48ec289a75517'
BRANCH='codex/v3-interface-probes-20260907'
CANONICAL={'docs/v3/'+n for n in 'ARCHITECTURE.md EXECUTION-FABRIC.md INTERACTION-SURFACES.md TERMINAL-RUNTIME.md PLUGINS-AND-EDITIONS.md ROUTE-CAPABILITIES.md ACCEPTANCE.md ROADMAP.md CONSTRUCTION-RUNBOOK.md README.md CLAIM-REGISTRY.json CLAIM-LEDGER.md SOURCE-REGISTER.md'.split()}
OLD_PATH='docs/v3/foundation-research/mark2-research/mark3-comparison/'
HIST=runpy.run_path(str(ROOT/OLD_PATH/'check.py'));strict=HIST['strict']

def git(*args,root=ROOT,binary=False):
    raw=subprocess.check_output(['git',*args],cwd=root)
    return raw if binary else raw.decode('utf8').strip()
def read(name):return strict((AREA/name).read_text(encoding='utf8'))
def text(name):return (ROOT/name).read_text(encoding='utf8')
def common():
    p=pathlib.Path(git('rev-parse','--git-common-dir'))
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()
def cache():return common()/'research-attestations/interface-probes/discovery'

def goal_check(g):
    require(g['id']=='recursion.v3.interface-probes.20260907' and g['parent_goal']=='goal-recursion-v2-execution-fabric','goal/parent')
    require(g['start_commit']==START and g['required_research_ancestor']==RESEARCH and g['branch']==BRANCH,'goal lineage')
    require(set(g['allowed_paths'])==CANONICAL|{PREFIX+'**',CODE+'**'},'goal scope')
    require(type(g['new_metered_spend'])is int and g['new_metered_spend']==0 and g['usage_resets_allowed'] is False,'goal spend')
    require(g['max_concurrent_read_only_workers']==4 and g['synthesis_review_reserve_minutes']>=90,'goal bounds')
    start=datetime.datetime.fromisoformat(g['start_utc'].replace('Z','+00:00'));deadline=datetime.datetime.fromisoformat(g['agent_chosen_deadline_utc'].replace('Z','+00:00'))
    require(start.isoformat()=='2026-09-07T22:39:28+00:00' and (deadline-start).total_seconds()==21600,'campaign envelope')
def scope_check(changed):
    require(changed and all(p in CANONICAL or p.startswith(PREFIX) or p.startswith(CODE) for p in changed),'out-of-scope change')
    require(not git('diff','--name-only','--diff-filter=D',START),'deleted baseline file')
def candidate_check(candidate,actual,dirty):
    require(isinstance(candidate,str) and re.fullmatch('[0-9a-f]{40}',candidate) and candidate==actual and not dirty,'clean exact candidate')
def preflight():
    g=read('goal.json');goal_check(g)
    require(git('branch','--show-current')==BRANCH,'actual branch')
    for ancestor in [START,RESEARCH,'a7cd9458d37f3090079930bf8d79ffd77c4f73e4']:git('merge-base','--is-ancestor',ancestor,'HEAD')
    owners=[x for x in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+BRANCH in x.splitlines()]
    require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree ownership')
    require('status: active' in text('state/goals/goal-recursion-v2-execution-fabric.md'),'active parent')
    return g

def canonical_preservation(overrides=None):
    overrides=overrides or {}
    for path in CANONICAL:
        old=git('show',START+':'+path);current=overrides.get(path,text(path))
        if path.endswith('.json'):
            a,b=strict(old),strict(current)
            require({k:v for k,v in a.items() if k!='ranges'}=={k:v for k,v in b.items() if k!='ranges'},'registry shape changed')
            require(a['ranges']==[x for x in b['ranges'] if x['prefix']!='IPR'],'historical registry range changed')
        else:
            lines=iter(current.splitlines())
            for line in old.splitlines():require(any(x==line for x in lines),'historical canonical text changed: '+path)

def claim_bindings(e,ledger=None,registry=None,source=None):
    ledger=text('docs/v3/CLAIM-LEDGER.md') if ledger is None else ledger
    registry=strict(text('docs/v3/CLAIM-REGISTRY.json')) if registry is None else registry
    source=text('docs/v3/SOURCE-REGISTER.md') if source is None else source
    HIST['OLD']['registry_shape'](registry,ledger)
    rows=re.findall(r'^\| (IPR-\d{3}) \| ([^|]*)\| ([^|]*)\| ([^|]*)\|',ledger,re.M)
    require(len(rows)==7 and {r[0] for r in rows}=={f'IPR-{i:03}' for i in range(1,8)},'new ledger coverage')
    mapped={r[0]:r for r in rows};run_ids={r['id'] for r in e['runs']}
    def family(r):
        f=r['facts']
        return 'ownership' if 'executions' in f else 'codex' if 'server_launches' in f else 'hermes-real' if f['agent']=='real' else 'hermes-synthetic'
    accepted={family(r):r['id'] for r in e['runs'] if r['use']=='accepted-scoped-evidence'}
    require(set(accepted)=={'ownership','codex','hermes-real','hermes-synthetic'},'accepted fact families')
    failed_synthetic={r['id'] for r in e['runs'] if family(r)=='hermes-synthetic' and r['recorded_failure']}
    require(len(failed_synthetic)==1,'retained synthetic failure identity')
    expected_runs={1:{accepted['ownership']},2:{accepted['codex']},3:{accepted['codex']},
                   4:failed_synthetic|{accepted['hermes-synthetic'],accepted['hermes-real']},5:{accepted['hermes-real']},6:{accepted['hermes-real']},7:set()}
    expected_sources={1:{'SRC-V3-231','SRC-V3-260'},2:{'SRC-V3-273'},3:{'SRC-V3-273'},4:{'SRC-V3-275'},5:{'SRC-V3-274'},6:{'SRC-V3-274','SRC-V3-275'},7:set()}
    require(len(e['claims'])==7 and {c['id'] for c in e['claims']}==set(mapped),'claim identity set')
    for c in e['claims']:
        row=mapped[c['id']]
        number=int(c['id'].split('-')[1])
        require(set(c['run_ids'])==expected_runs[number] and len(c['run_ids'])==len(expected_runs[number]),'claim requires exact accepted fact family and retained failure')
        require(set(c['source_ids'])==expected_sources[number] and len(c['source_ids'])==len(expected_sources[number]),'claim primary source family')
        require(row[1].strip()==c['statement'] and row[2].strip()==c['state'],'claim statement/state drift')
        require(set(re.findall(r'SRC-V3-\d{3}',row[3]))==set(c['source_ids']),'claim source drift')
        require(c['canonical'] in CANONICAL and c['id'] in text(c['canonical']),'canonical claim owner')
        require(c['state'] in {'locally-observed','modeled'} and set(c['run_ids'])<=run_ids,'claim state/joins')
        require((c['state']=='modeled')==(not c['run_ids']),'modeled/observed boundary')
    smap=dict(re.findall(r'^\| `(SRC-V3-\d{3})` \| ([^|]*)\|',source,re.M))
    for s in e['sources']:require('('+s['url']+')' in smap[s['id']],'new source URL binding')
    require(e['measured_provider_results']==[] and e['formal_refinement_results']==[],'unestablished provider/formal result')

def evidence_check(e):
    require(type(e['schema_version'])is int and e['schema_version']==1 and e['start_commit']==START,'evidence identity')
    index=strict((cache()/'index.json').read_text(encoding='utf8'))
    audit_raw=(cache()/'build-audit.json').read_bytes();audit=strict(audit_raw.decode())
    require(sha(audit_raw)==e['post_run_build_audit']['sha256'] and audit['hermes']['mismatches']==[] and audit['hermes']['regular_members_checked']==11939,'post-run source audit')
    build_hashes={name:sha((cache()/'builds'/file).read_bytes()) for name,file in [('codex','codex-0.149.0-windows-x64.exe'),('python','windows-python.exe'),('hermes','hermes-source.tar.gz')]}
    require(build_hashes=={'codex':audit['codex_executable_sha256'],'python':audit['windows_python_sha256'],'hermes':audit['retained_archive_sha256']},'retained build bytes')
    require(len(index['runs'])==len(e['runs']) and len({x['id'] for x in index['runs']})==len(index['runs']),'run inventory')
    leases=strict((cache()/'packet-04-leases.json').read_text());used=0
    closure=read('packet-04-closure.json')
    require(sha((cache()/'packet-04-leases.json').read_bytes())==closure['lease_receipt_sha256'],'packet lease receipt digest')
    for ordinal,rel in enumerate(leases['reservations'],1):
        validate_release(rel['packet'],rel['case'],rel['launches'],used,datetime.datetime.fromisoformat(rel['reserved_at']))
        require(rel['ordinal']==ordinal and rel['packet_sha256']==leases['packet_sha256'],'lease order/packet binding');used+=rel['launches']
    require(used==closure['reserved_harness_launches']==closure['actual_harness_launches']==3 and closure['status']=='closed','packet closure accounting')
    released=[]
    for entry,public in zip(index['runs'],e['runs']):
        directory=pathlib.Path(entry['directory']).resolve()
        require(directory.is_relative_to((cache()/'runs').resolve()),'external run path escape')
        require(project(entry)==public,'public projection or retained bytes changed: '+entry['id'])
        if entry['use']=='accepted-scoped-evidence':
            a=strict((directory/'admission.json').read_text())
            r=strict((directory/'result.json').read_text())
            if 'codex' in entry['id']:
                require(a['executable_sha256']==build_hashes['codex'] and a['config_sha256']==sha((directory/'home/config.toml').read_bytes()),'Codex admitted build/config bytes')
                config=tomllib.loads((directory/'home/config.toml').read_text())
                require(config['model_provider']=='fixture' and config['model_providers']['fixture']['requires_openai_auth'] is False and config['model_providers']['fixture']['base_url']==a['provider_destination'],'Codex configured provider')
                route=urlsplit(a['provider_destination']);require(route.scheme=='http' and route.hostname=='127.0.0.1' and route.path=='/v1' and route.port and not route.username and not route.password,'Codex loopback route')
            elif 'ownership' in entry['id']:require(a['python_sha256']==build_hashes['python'],'ownership admitted Python build')
            else:
                require(a['source_pin']=='693641aa8b4359c602283bdbbc14041e03bc47bc' and a['source_archive_sha256']==build_hashes['hermes'],'Hermes admitted archive/pin')
                require(a['dependencies_sha256']==sha((directory/'dependencies.txt').read_bytes()),'Hermes installed dependency receipt')
                if a.get('mode')=='real':
                    routes=stderr_json(r,'effective_fixture_route');require(len(routes)==1,'Hermes effective config receipt')
                    route=routes[0];require(route['config_sha256']==sha((directory/'effective-config.yaml').read_bytes()),'Hermes effective config bytes')
                    before=strict(a['configuration']);before['model']['base_url']=route['url']
                    require(before==route['configuration'] and route['inference'] is False,'Hermes effective config transformation')
                    endpoint=urlsplit(route['url']);require(endpoint.scheme=='http' and endpoint.hostname=='127.0.0.1' and endpoint.path=='/v1' and endpoint.port,'Hermes loopback route')
                else:require((directory/'effective-config.yaml').read_bytes()==a['configuration'].encode(),'Hermes synthetic configuration bytes')
            if 'packet_release' in a:
                rel=a['packet_release'];packet=rel['packet']
                validate_release(packet,rel['case'],rel['launches'],0,datetime.datetime.fromisoformat(rel['reserved_at']))
                require(datetime.datetime.fromisoformat(rel['reserved_at'])<=datetime.datetime.fromisoformat(a['at']),'release after admission')
                require(sha((AREA/'packet-04.json').read_bytes())==rel['packet_sha256'],'release packet drift')
                require(rel in leases['reservations'],'unretained packet reservation')
                actual=public['facts'].get('server_launches',1)
                require(actual==rel['launches'],'observed launch count differs from reservation')
                released.append((entry['id'],rel['ordinal'],actual))
            if 'codex' in entry['id'] or 'hermes-real' in entry['id']:require('packet_release' in a,'final harness evidence lacks prospective release')
    require(len(released)==len(leases['reservations']) and len({r[1] for r in released})==len(released),'reservation reused or unrepresented')
    require({r[0] for r in released}==set(closure['runs']) and len(closure['runs'])==len(released) and sum(r[2] for r in released)==used,'closure actual runs/launches')
    accepted=[x for x in e['runs'] if x['use']=='accepted-scoped-evidence']
    require(len(accepted)==4 and all(not r['recorded_failure'] for r in accepted),'accepted subset')
    sources=strict((cache()/'source-index.json').read_text());verified=set()
    for r in sources:
        p=pathlib.Path(r['file']).resolve();require(p.is_relative_to((cache()/'sources').resolve()),'source path escape')
        raw=p.read_bytes();require(sha(raw)==r['sha256'] and len(raw)==r['bytes'],'source bytes')
        verified.add((r['url'],r['sha256'],r['bytes']))
    require(len(e['sources'])==3 and {s['id'] for s in e['sources']}=={'SRC-V3-273','SRC-V3-274','SRC-V3-275'},'new source identities')
    claimed=set()
    for s in e['sources']:
        require(re.fullmatch('[0-9a-f]{40}',s['version']) and '/'+s['version']+'/' in s['url'],'pinned new source')
        require(s['receipts'] and s['url'] in [r['url'] for r in s['receipts']],'source primary receipt missing')
        prefix=s['url'].split(s['version'])[0]+s['version']+'/'
        for r in s['receipts']:
            require(r['url'].startswith(prefix) and type(r['bytes'])is int and r['bytes']>0 and (r['url'],r['sha256'],r['bytes']) in verified,'unretained or wrong-version source')
            claimed.add((r['url'],r['sha256'],r['bytes']))
    claim_bindings(e);return len(index['runs']),len(claimed)

def manifest_check():
    m=read('manifest.json');require(m['start_commit']==START and m['required_research_ancestor']==RESEARCH and m['branch']==BRANCH,'manifest lineage')
    expected={x['path'] for x in HIST['read']('manifest.json')['inputs']}
    expected|={str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/OLD_PATH).iterdir() if p.is_file()}
    require({x['path'] for x in m['inputs']}==expected and len(m['inputs'])==len(expected),'complete frozen inputs')
    for x in m['inputs']:require(sha(git('show',START+':'+x['path'],binary=True))==x['git_blob_sha256'],'frozen input hash')
    p=read('next-packets.json');old=HIST['read']('coverage.json');spec=HIST['read']('comparison-contract.json')
    require(p['preserved_experiment_families']==old['experiment_families'] and p['preserved_cross_area_cases']==old['cross_area_cases'],'preserved experiment coverage')
    require(p['shared_formal_obligations']==spec['obligations'] and p['formal_boundary_names']==spec['boundaries'] and p['formal_traces']==27,'full formal contract')
    require(p['owner_questions']==[] and p['first_grillme'] is None,'no manufactured Owner decisions')

def reject(fn,value,label):
    try:fn(value)
    except (ValueError,KeyError,TypeError,AssertionError):return label
    raise ValueError('accepted adversarial mutation: '+label)
def adversarial(e):
    rejected=[]
    for field,value in [('start_commit','0'*40),('new_metered_spend',1),('usage_resets_allowed',True),('allowed_paths',['CONTROL_PLANE.md'])]:
        g=copy.deepcopy(read('goal.json'));g[field]=value;rejected.append(reject(goal_check,g,'goal/'+field))
    rejected.append(reject(scope_check,['CONTROL_PLANE.md'],'protected path'))
    rejected.append(reject(lambda c:candidate_check(c,git('rev-parse','HEAD'),False),'0'*40,'wrong candidate'))
    rejected.append(reject(lambda d:candidate_check(git('rev-parse','HEAD'),git('rev-parse','HEAD'),d),True,'dirty candidate'))
    for field,value in [('statement','unsupported changed statement'),('state','measured'),('run_ids',['invented']),('source_ids',[])]:
        bad=copy.deepcopy(e);bad['claims'][0][field]=value;rejected.append(reject(claim_bindings,bad,'claim/'+field))
    bad=copy.deepcopy(e);bad['claims'][1]['run_ids']=e['claims'][0]['run_ids'];rejected.append(reject(claim_bindings,bad,'claim unrelated observed run'))
    bad=copy.deepcopy(e)
    for s in bad['sources']:s['receipts']=[]
    rejected.append(reject(evidence_check,bad,'all source receipts removed'))
    ledger=text('docs/v3/CLAIM-LEDGER.md');line=next(x for x in ledger.splitlines() if x.startswith('| IPR-001 |'))
    for label,bad in [('missing ledger row',ledger.replace(line,'')),('duplicate ledger row',ledger+'\n'+line)]:rejected.append(reject(lambda s:claim_bindings(e,ledger=s),bad,label))
    reg=strict(text('docs/v3/CLAIM-REGISTRY.json'))
    for field,value in [('start',True),('end',8)]:
        bad=copy.deepcopy(reg);bad['ranges'][-1][field]=value;rejected.append(reject(lambda s:claim_bindings(e,registry=s),bad,'registry/'+field))
    bad=copy.deepcopy(reg);bad['ranges'].append(copy.deepcopy(bad['ranges'][-1]));rejected.append(reject(lambda s:claim_bindings(e,registry=s),bad,'overlapping range'))
    source=text('docs/v3/SOURCE-REGISTER.md').replace(e['sources'][0]['url'],'https://example.com/unrelated');rejected.append(reject(lambda s:claim_bindings(e,source=s),source,'source URL drift'))
    baseline=text('docs/v3/EXECUTION-FABRIC.md');anchor='No upstream-only helper may silently require a direct API key.';require(anchor in baseline,'canonical mutant anchor')
    rejected.append(reject(canonical_preservation,{'docs/v3/EXECUTION-FABRIC.md':baseline.replace(anchor,'A separate paid helper is required.')},'historical contract mutation'))
    index=strict((cache()/'index.json').read_text())
    for entry in index['runs']:
        if entry['use']!='accepted-scoped-evidence':continue
        d=pathlib.Path(entry['directory']);a=strict((d/'admission.json').read_text());r=strict((d/'result.json').read_text())
        if 'codex' in entry['id']:
            fn=lambda x:codex_projection(a,x,True);bad=copy.deepcopy(r);bad['scripted_endpoint_requests'][0]['credential_header_present']=True;rejected.append(reject(fn,bad,'Codex inherited credential'))
            bad=copy.deepcopy(r);bad['trace']['reader_threads_alive']=1;rejected.append(reject(fn,bad,'Codex unended observer'))
            bad=copy.deepcopy(r)
            for request in bad['scripted_endpoint_requests']:request['body']['tools']=[{'name':'PUBLIC_UNEXPECTED_TOOL'}]
            rejected.append(reject(fn,bad,'Codex unexpected enabled tool'))
            bad=copy.deepcopy(r);bad['outcomes']=[o for o in bad['outcomes'] if o['check']!='fork_boundary_history'];rejected.append(reject(fn,bad,'Codex missing claimed behavior'))
        elif 'hermes-real' in entry['id']:
            fn=lambda x:hermes_projection(a,x,True);bad=copy.deepcopy(r)
            for o in bad['outcomes']:
                if o['check'] in ('postinterrupt_durable_history','same_process_resumed_history'):o['result']['result']['messages']=o['result']['result']['messages'][2:]
            rejected.append(reject(fn,bad,'Hermes lost earlier history'))
            bad=copy.deepcopy(r);bad['namespace_owner_exit_code']=None;rejected.append(reject(fn,bad,'Hermes Linux cleanup unknown'))
        elif 'ownership' in entry['id']:
            fn=lambda x:ownership_projection(a,x,True);bad=copy.deepcopy(r);bad['results'][0]['live_immediately_before_crash']=[False];rejected.append(reject(fn,bad,'ownership vacuous death'))
            bad=copy.deepcopy(r);bad['results'][3]['survived_broker_death']=[True];rejected.append(reject(fn,bad,'birth containment survivor'))
            bad=copy.deepcopy(r)
            for row in bad['results']:
                for field in ['identities','live_immediately_before_crash','survived_broker_death','target_membership_before_crash']:row[field]=[]
                row['barrier']['identities']=[]
            rejected.append(reject(fn,bad,'ownership empty observation arrays'))
    return rejected

def working_checks():
    preflight();manifest_check();canonical_preservation();e=read('evidence.json');counts=evidence_check(e)
    HIST['bindings'](HIST['read']('evidence.json'));HIST['bindings'](HIST['M']['read']('evidence.json'))
    changed=sorted(set(git('diff','--name-only',START).splitlines()+git('ls-files','--others','--exclude-standard').splitlines()))
    scope_check(changed);HIST['PRIOR']['document_gate'](changed)
    modeled=read('contract-vectors.json');modeled.pop('observed_at');require(modeled==json.loads(json.dumps(vectors())),'model vector output drift')
    return changed,counts,adversarial(e)
def command_env():
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1');bash=pathlib.Path(os.environ.get('ProgramFiles',''))/'Git/bin'
    if os.name=='nt' and (bash/'bash.exe').exists():env['PATH']=str(bash)+os.pathsep+env.get('PATH','')
    return env
def run_command(command,root,out,name):
    before=time.monotonic();result=subprocess.run(command,cwd=root,env=command_env(),capture_output=True,timeout=240)
    raw=result.stdout+result.stderr;(out/(name+'.log')).write_bytes(raw)
    receipt={'command':command,'exit_code':result.returncode,'seconds':round(time.monotonic()-before,3),'output_sha256':sha(raw)}
    print(json.dumps(receipt),flush=True);require(result.returncode==0,'command failed: '+name);return receipt
def frozen_root():
    matches=[]
    for entry in git('worktree','list','--porcelain').split('\n\n'):
        lines=entry.splitlines()
        if 'HEAD '+RESEARCH in lines and 'branch refs/heads/codex/v3-formal-model-experiment' in lines:matches.append(pathlib.Path(lines[0][9:]))
    require(len(matches)==1,'frozen research worktree unavailable; reconstitute exact authorized evidence')
    p=matches[0];require(not git('status','--porcelain=v1','--untracked-files=all',root=p),'frozen worktree dirty');return p
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preflight',action='store_true');ap.add_argument('--working',action='store_true');ap.add_argument('--candidate');args=ap.parse_args();preflight()
    if args.preflight:print('CAMPAIGN_PREFLIGHT_PASS_NOT_FINAL');return
    if not args.working:candidate_check(args.candidate,git('rev-parse','HEAD'),git('status','--porcelain=v1','--untracked-files=all'))
    changed,counts,mutants=working_checks()
    if args.working:print(json.dumps({'status':'WORKING_EVIDENCE_PASS_NOT_FINAL','retained_runs':counts[0],'source_receipts':counts[1],'adversarial_checks':len(mutants)}));return
    git('diff','--check',START,args.candidate);inventory=read('validation-inventory.json');prior=HIST['read']('validation-inventory.json')
    require(inventory['regression_commands']==prior['regression_commands']==HIST['OLD']['regression_commands']() and len(inventory['regression_commands'])==25,'unchanged regression inventory')
    for x in prior['regression_entrypoints']:
        raw=git('show',args.candidate+':'+x['path'],binary=True);require(sha(raw)==x['sha256'] and raw==git('show',START+':'+x['path'],binary=True),'historical executable changed')
    require(set(inventory['artifacts'])==set(changed)-{PREFIX+'validation-inventory.json'},'artifact coverage')
    for p,digest in inventory['artifacts'].items():require(sha(git('show',args.candidate+':'+p,binary=True))==digest,'artifact digest: '+p)
    out=common()/'research-attestations/interface-probes'/args.candidate;out.mkdir(parents=True,exist_ok=True);runid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+str(time.time_ns())[-6:]
    observer=run_command([sys.executable,'-X','utf8','-B',CODE+'observer_tests.py'],ROOT,out,runid+'-observer')
    frozen=frozen_root();frozen_receipt=run_command([sys.executable,'-X','utf8','-B',OLD_PATH+'check.py','--working'],frozen,out,runid+'-frozen')
    require(git('rev-parse','HEAD',root=frozen)==RESEARCH and not git('status','--porcelain=v1','--untracked-files=all',root=frozen),'frozen source changed')
    regressions=[]
    for i,cmd in enumerate(inventory['regression_commands']):
        row=run_command([sys.executable,*cmd[1:]],ROOT,out,runid+f'-regression-{i:02}');row['command']=cmd;regressions.append(row)
    candidate_check(args.candidate,git('rev-parse','HEAD'),git('status','--porcelain=v1','--untracked-files=all'))
    receipt={'status':'INTERFACE_PROBE_GATE_PASS','candidate':args.candidate,'base':START,'run_id':runid,'retained_runs':counts[0],'source_receipts':counts[1],'adversarial_checks':mutants,'observer':observer,'frozen_source_commit':RESEARCH,'frozen_validation':frozen_receipt,'current_candidate_regressions':regressions,'artifacts':{p:sha(git('show',args.candidate+':'+p,binary=True)) for p in changed},'live_provider_inference_validated':False,'formal_refinement_checked':False,'product_acceptance':False}
    raw=(json.dumps(receipt,indent=2)+'\n').encode();(out/(runid+'.json')).write_bytes(raw);print('INTERFACE_PROBE_GATE_PASS '+json.dumps({'candidate':args.candidate,'run_id':runid,'regressions':25,'receipt_sha256':sha(raw)}),flush=True)
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:print('INTERFACE_PROBE_GATE_FAIL '+str(exc),file=sys.stderr);sys.exit(1)

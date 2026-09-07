"""Local documentation/evidence gate; no provider, benchmark or formal-model execution."""
from __future__ import annotations
import argparse, copy, json, os, re, runpy, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
AREA=Path(__file__).resolve().parent
ROOT=AREA.parents[4]
START="6d24f93741ccfd05d6f473e1d50123d7c6e20a8a"
BRANCH="codex/v3-formal-model-experiment"
PREFIX="docs/v3/foundation-research/mark2-research/mark3-comparison/"
FILES=set("campaign.md manifest.json goal.json plan.json architectures.md formal-boundaries.md comparison-contract.json evidence.json coverage.json probes.json probe-admission-schema.json route-deltas.json research-log.json handoff.md check.py validation-inventory.json".split())
PRIOR=runpy.run_path(str(AREA.parent/'mark3/check.py'))
M=PRIOR['M']; OLD=M['OLD']
need,closed,strings,rows,git,sha,strict=[M[n] for n in ('need','closed','strings','rows','git','sha','strict')]
AREAS=PRIOR['AREAS']; FAMILIES=M['FAMILIES']
ROLES="Head ARM worker reviewer questionnaire-assistant consultant summarizer compactor recovery-assistant classifier title-helper token-count-helper MCP-sampling next-speaker-checker loop-detector model-router edit-repair".split()
ROUTE_SOURCES=dict.fromkeys('chatgpt-codex codex-server'.split(),'SRC-V3-252')
for _paths,_source in [('grok-acp grok-headless',267),('cursor-sdk-local cursor-sdk-cloud cursor-acp-third',268),('hermes-tui hermes-http hermes-acp',269),('gemini-acp gemini-headless gemini-core-adaptation',270),('opencode-server opencode-acp',271),('claude-sdk claude-cli',272)]:
    ROUTE_SOURCES.update(dict.fromkeys(_paths.split(),'SRC-V3-'+str(_source)))
def read(n): return strict((AREA/n).read_text(encoding='utf8'))
def text(n): return (ROOT/n).read_text(encoding='utf8')
def shape(x,keys):
    closed(x,keys,'record')
    if 'schema_version' in x: need(type(x['schema_version']) is int and x['schema_version']==1,'schema version')
def nonempty(x,keys):
    for k in keys.split(): need(isinstance(x[k],str) and bool(x[k].strip()),'empty '+k)

def common_dir():
    p=Path(git('rev-parse','--git-common-dir'))
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()

def retrieval_audit(e):
    """Verify declared receipts against retained external bytes, not just a hash-shaped string.

    The cache is outside the candidate. Missing evidence requires exact public re-retrieval
    and review; this gate neither fetches sources nor equates their hashes with claim truth.
    """
    cache=common_dir()/'research-attestations/mark3-comparison/discovery'
    found={}
    for index in cache.glob('*receipts.json'):
        records=strict(index.read_text(encoding='utf8'))
        need(isinstance(records,list),'external retrieval index')
        for r in records:
            if not isinstance(r,dict) or 'sha256' not in r: continue
            path=(cache/'sources'/r['file']).resolve()
            need(path.is_relative_to((cache/'sources').resolve()),'source cache path escape')
            raw=path.read_bytes()
            need(sha(raw)==r['sha256'] and len(raw)==r['bytes'],'retained source bytes changed')
            found[(r['url'],r['sha256'],r['bytes'])]=True
    for s in e['sources']:
        for r in s['receipts']:
            need((r['url'],r['sha256'],r['bytes']) in found,'unverified source receipt: '+r['url'])
    return sum(len(s['receipts']) for s in e['sources'])
def preflight(m=None):
    m=read('manifest.json') if m is None else m
    shape(m,'schema_version goal parent predecessor start_commit branch required_ancestors allowed_canonical_paths allowed_new_directory inputs started_utc deadline_utc review_reserve_start_utc maximum_concurrent_readonly_workers maximum_discovery_minutes new_metered_spend provider_trials_authorized product_implementation_authorized')
    need(m['start_commit']==START and m['branch']==BRANCH and m['parent']=='goal-recursion-v2-execution-fabric','start lineage')
    need(m['goal']=='recursion.v3.foundation.mark3.comparison.20260907' and m['predecessor']=='recursion.v3.foundation.mark3.integration.20260907','goal lineage')
    need(m['maximum_concurrent_readonly_workers']==4 and m['maximum_discovery_minutes']==30,'Owner-expanded worker bounds')
    need(type(m['new_metered_spend']) is int and m['new_metered_spend']==0 and m['provider_trials_authorized'] is False and m['product_implementation_authorized'] is False,'research-only')
    ts=[datetime.fromisoformat(m[k].replace('Z','+00:00')) for k in ['started_utc','deadline_utc','review_reserve_start_utc']]
    need(ts[0].isoformat()=='2026-09-07T21:16:24+00:00' and (ts[1]-ts[0]).total_seconds()==21600 and ts[0]<=ts[2]<ts[1] and (ts[1]-ts[2]).total_seconds()>=5400,'six-hour envelope/reserve')
    names='ACCEPTANCE ARCHITECTURE CLAIM-LEDGER CLI CONSTRUCTION-RUNBOOK CONTEXT DECISION-REGISTER EXECUTION-FABRIC EXECUTIVES INTERACTION-SURFACES PERFORMANCE-PLAN PLANNING PLUGINS-AND-EDITIONS PRODUCT README RESEARCH-HYPOTHESES ROADMAP ROUTE-CAPABILITIES SECURITY SOURCE-REGISTER TELEMETRY TERMINAL-RUNTIME'.split()
    allowed={'docs/v3/'+n+'.md' for n in names}|{'docs/v3/CLAIM-REGISTRY.json'}
    need(set(m['allowed_canonical_paths'])==allowed and len(m['allowed_canonical_paths'])==len(allowed) and m['allowed_new_directory']==PREFIX,'allowlist')
    need(git('branch','--show-current')==BRANCH,'actual branch')
    need(m['required_ancestors']==['ec9c3d1632193e8509e7baf41fa8810165f93c05','a7cd9458d37f3090079930bf8d79ffd77c4f73e4'],'required ancestors')
    for h in [START,*m['required_ancestors']]: git('merge-base','--is-ancestor',h,'HEAD')
    owners=[x for x in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+BRANCH in x.splitlines()]
    need(len(owners)==1 and Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree')
    expected_inputs=allowed|{'ANCHOR.md','CLAUDE.md','CONTROL_PLANE.md','docs/v3/prompts/standalone-harness-foundation-deep-research.md','state/goals/goal-recursion-v2-execution-fabric.md','scripts/v3/planning/validation/contracts.py'}
    expected_inputs|={'docs/v3/'+n+'.md' for n in ['M1A-WIRE-PROFILE','M1B-WIRE-PROFILE','M1C-WIRE-PROFILE','M1B-EXECUTION-CONTRACTS','M1C-INTEGRITY-CONTRACTS']}
    expected_inputs|={'docs/v3/foundation-research/platform-round/'+n+'.md' for n in ['repository-map','interaction-contract']}
    expected_inputs|={'docs/v3/foundation-research/mark2-research/'+n for n in 'campaign.md check.py compatibility.json decisions.json evidence.json experiments.json grillme.md manifest.json report-source.md validation-inventory.json'.split()}
    expected_inputs|={'docs/v3/foundation-research/mark2-research/mark3/'+n for n in 'campaign.md check.py companion-review.json directions.json handoff.md owner-answers.md research-plan.json validation-inventory.json'.split()}
    need(rows(m['inputs'],'inputs','path')==expected_inputs and len(expected_inputs)==54,'complete frozen input set')
    for x in m['inputs']:
        shape(x,'path git_blob_sha256'); need(sha(git('show',START+':'+x['path'],binary=True))==x['git_blob_sha256'],'frozen input digest')
    return m,allowed

def bindings(ev):
    sr=re.findall(r'^\| `(SRC-V3-\d{3})` \| ([^|]*)\|',text('docs/v3/SOURCE-REGISTER.md'),re.M)
    need([x[0] for x in sr]==[f'SRC-V3-{n:03}' for n in range(1,len(sr)+1)],'source sequence')
    smap={k:re.findall(r'\[[^\]]*\]\((https://[^)]+)\)',v) for k,v in sr}
    for s in ev['sources']: need(s['url'] in smap[s['id']],'source ID/URL drift')
    ledger=text('docs/v3/CLAIM-LEDGER.md'); reg=strict(text('docs/v3/CLAIM-REGISTRY.json')); registered=OLD['registry_shape'](reg,ledger)
    cm=dict(re.findall(r'^\| ((?:MKR|CMP)-\d{3}) \| ([^|]*)\|',ledger,re.M))
    for c in ev['claims']: need(cm.get(c['id'],'').strip()==c['statement'],'claim statement drift')
    owner=text('docs/v3/DECISION-REGISTER.md'); oids=set(re.findall(r'^\| (OR-\d{3}) \|',owner,re.M))
    need(oids=={f'OR-{i:03}' for i in range(1,40)},'no new Owner answer')
    for i in oids: need(owner.count('| '+i+' |')==1,'Owner uniqueness')
    for p in (ROOT/'docs/v3').rglob('*'):
        if p.suffix not in {'.md','.json'} or 'archive' in p.relative_to(ROOT/'docs/v3').parts: continue
        prose=p.read_text(encoding='utf8')
        for match in re.finditer(reg['referencePattern'],prose):
            v=match[1]; need(v in registered or v in oids or v=='SHA-256' or re.fullmatch('H-[0-9]{3}',v),'unregistered claim '+v)
        need(set(re.findall(r'SRC-V3-\d{3}',prose))<=set(smap),'unregistered source')
    for path,pat in [('docs/v3/SOURCE-REGISTER.md',r'^\| `SRC-V3-\d{3}` \|.*$'),('docs/v3/CLAIM-LEDGER.md',r'^\| [A-Z][A-Z0-9]*-\d{3} \|.*$'),('docs/v3/DECISION-REGISTER.md',r'^\| OR-\d{3} \|.*$')]:
        for row in re.findall(pat,git('show',START+':'+path),re.M): need(row in text(path),'historical registry changed')
    return set(smap),registered

def evidence_gate(e):
    shape(e,'schema_version start_commit status sources claims claim_states observed_runtime_runs measured_results source_failures contradictions')
    need(e['start_commit']==START and e['status']=='source-researched-probes-unrun','evidence identity')
    need(e['claim_states']=='source-documented inferred modeled locally-observed measured unsupported unknown'.split() and e['observed_runtime_runs']==[] and e['measured_results']==[],'honest states')
    ids=rows(e['sources'],'sources'); need(ids=={f'SRC-V3-{n:03}' for n in range(229,229+len(ids))},'new source IDs')
    for s in e['sources']:
        shape(s,'id title url publisher version retrieved license applicability receipts unretrieved'); nonempty(s,'title url publisher version license applicability')
        need(s['retrieved']=='2026-09-07' and (s['receipts'] or s['unretrieved']),'source retrieval')
        urls=[s['url']]
        for x in s['receipts']:
            shape(x,'url sha256 bytes'); need(re.fullmatch('[0-9a-f]{64}',x['sha256']) and type(x['bytes']) is int and x['bytes']>0,'raw receipt'); urls.append(x['url'])
        need(s['url'] in [r['url'] for r in s['receipts']] or bool(s['unretrieved']),'source primary URL retrieval or explicit failure')
        for url in urls:
            u=urlsplit(url); need(u.scheme=='https' and u.hostname and not u.username and not u.password,'public URL')
            if u.hostname=='raw.githubusercontent.com': need(re.fullmatch('[0-9a-f]{40}',u.path.split('/')[3]),'pinned code')
    cids=rows(e['claims'],'claims'); need(cids=={f'CMP-{n:03}' for n in range(1,len(cids)+1)},'new claims')
    ledger=text('docs/v3/CLAIM-LEDGER.md')
    for c in e['claims']:
        shape(c,'id statement state source_ids applicability canonical next_test observations disposition'); nonempty(c,'statement applicability canonical next_test disposition')
        need(c['state'] in {'source-documented','inferred','unsupported','unknown'} and c['observations']==[],'unrun claim promoted')
        need(c['source_ids'] and set(c['source_ids'])<=ids and c['next_test'] in {'experiment.mark2.'+x for x in FAMILIES},'claim source/test')
        need(c['canonical'] in read('manifest.json')['allowed_canonical_paths'] and c['canonical'] not in {'docs/v3/CLAIM-LEDGER.md','docs/v3/SOURCE-REGISTER.md','docs/v3/CLAIM-REGISTRY.json'} and c['id'] in text(c['canonical']),'canonical owner/claim occurrence')
        line=next((l for l in ledger.splitlines() if l.startswith('| '+c['id']+' |')),'')
        need(c['statement'] in line and '| '+c['state']+' |' in line and set(re.findall('SRC-V3-[0-9]{3}',line))==set(c['source_ids']),'claim ledger source binding')
    strings(e['source_failures'],'failures'); strings(e['contradictions'],'contradictions'); bindings(e); retrieval_audit(e)

def coverage_gate(c,e):
    shape(c,'schema_version areas architecture_ids design_axes experiment_families cross_area_cases required_capabilities_removable_by_benchmark ranking hard_floors human_outcomes')
    old=PRIOR['read']('research-plan.json'); trials=M['read']('experiments.json')
    need([x['id'] for x in c['areas']]==AREAS and c['architecture_ids']==['A','B','C'],'twelve areas/three configurations')
    need(c['design_axes']==old['design_axes'] and c['experiment_families']==FAMILIES and c['cross_area_cases']==old['cross_area_cases'],'axes/families/six cases')
    need(c['required_capabilities_removable_by_benchmark'] is False and c['ranking']==trials['priorities'] and c['hard_floors']==trials['hard_floors'] and c['human_outcomes']==old['comparison_protocol']['required_human_outcomes'],'accepted outcomes')
    for x in c['areas']:
        shape(x,'id approaches claim_ids disposition decisive_test unresolved status'); strings(x['approaches'],'approaches'); nonempty(x,'disposition decisive_test unresolved')
        need(len(set(x['approaches']))>=3 and x['claim_ids'] and set(x['claim_ids'])<={c['id'] for c in e['claims']} and x['status']=='researched-probes-unrun','area depth/evidence boundary')

def route_gate(r,e=None):
    e=read('evidence.json') if e is None else e
    sources={s['id']:s for s in e['sources']}
    shape(r,'schema_version baseline baseline_git_blob_sha256 entry_names path_ids critical_names controls deltas role_paths observed_runs')
    baseline='docs/v3/foundation-research/mark2-research/compatibility.json'; old=M['read']('compatibility.json'); paths={p['id']:p for e in old['entries'] for p in e['paths']}
    need(r['baseline']==baseline and r['baseline_git_blob_sha256']==sha(git('show',START+':'+baseline,binary=True)),'matrix baseline')
    need(r['entry_names']==[e['requested_name'] for e in old['entries']] and len(r['entry_names'])==13 and r['path_ids']==list(paths) and len(paths)==23,'all integrations/paths')
    need(r['critical_names']==old['launch_critical_names'] and r['controls']==old['feature_inventory'] and r['observed_runs']==[],'critical names/ten controls/unrun')
    need(rows(r['deltas'],'deltas','path_id')==set(ROUTE_SOURCES),'reviewed route overlay set')
    for d in r['deltas']:
        shape(d,'path_id binding source_ids state tested_build observed_runs supersedes limit next_test'); fields='provider executing_harness supported_interface authentication billing_source host version intended_distribution'; shape(d['binding'],fields); nonempty(d['binding'],fields)
        need(d['path_id'] in paths and d['state']=='source-documented' and d['tested_build'] is None and d['observed_runs']==[],'route promotion'); nonempty(d,'supersedes limit next_test')
        strings(d['source_ids'],'route sources')
        need(set(d['source_ids'])<=set(sources) and d['next_test'] in {'experiment.mark2.'+x for x in FAMILIES},'route source/test join')
        need(d['source_ids']==[ROUTE_SOURCES[d['path_id']]],'route to source binding')
        need(all(d['binding'][k]==paths[d['path_id']][k] for k in ['provider','executing_harness']),'preserved route identity')
        sid=d['source_ids'][0]
        token=('1.0.31' if d['path_id'] in ['cursor-sdk-local','cursor-sdk-cloud'] else '1.0.28') if sid=='SRC-V3-268' else '2026-09-07' if sid=='SRC-V3-272' else re.findall(r'[0-9a-f]{40}',sources[sid]['version'])[0]
        need(token in d['binding']['version'],'source-located route version')
    need(set(r['role_paths'])==set(ROLES),'all reasoning roles')
    for x in r['role_paths'].values():
        shape(x,'native upstream_only combined accounting status'); nonempty(x,'native upstream_only combined accounting'); need(x['status']=='design-unrun' and 'no direct API credential dependency' in x['upstream_only'],'upstream-only helper closure')

def probe_gate(p,e=None):
    e=read('evidence.json') if e is None else e
    sources={s['id']:s for s in e['sources']}
    shape(p,'schema_version status execution_authorized baseline preserved_families probes results_available')
    need(p['status']=='preregistered-unrun' and p['execution_authorized'] is False and p['results_available'] is False,'unrun probe authority')
    need(p['baseline']=='docs/v3/foundation-research/mark2-research/experiments.json' and p['preserved_families']==FAMILIES and [x['id'] for x in p['probes']]==['experiment.mark2.'+x for x in FAMILIES],'eight probe families')
    old={t['id']:t for t in M['read']('experiments.json')['trials']}
    fields='status admission actual_host installed_build_digest fixture_digest included_capacity_lease deadline_utc new_metered_spend maximum_concurrent_cases privacy forbidden_effects cleanup stop_conditions result id family baseline treatments scenarios maximum_minutes source_builds route host_design configuration fixture_specification allowed_effects steps counters acceptance_gate analysis full_workflow_costs release_admission_fields cell_plan'
    for x in p['probes']:
        shape(x,fields); need(x['status']=='preregistered-unrun' and x['admission']=='blocked-unavailable-build-host-fixture-and-capacity' and x['result'] is None,'probe state')
        need(x['scenarios']==old[x['id']]['scenarios'] and x['release_admission_fields']==['actual_host','installed_build_digest','fixture_digest','included_capacity_lease','deadline_utc'],'scenarios/admission')
        need(all(x[k] is None for k in x['release_admission_fields']),'invented probe admission')
        need(type(x['new_metered_spend']) is int and x['new_metered_spend']==0 and x['maximum_concurrent_cases']==2 and type(x['maximum_minutes']) is int and 0<x['maximum_minutes']<=90,'probe bounds')
        nonempty(x,'privacy cleanup route host_design configuration fixture_specification acceptance_gate analysis baseline family')
        need(x['id']=='experiment.mark2.'+x['family'],'probe family identity'); strings(x['treatments'],'treatments')
        for k in 'forbidden_effects stop_conditions allowed_effects steps counters'.split(): strings(x[k],k)
        need(x['full_workflow_costs']==['initial work','failed attempts','retry','helpers','verification','recovery','human review'],'fullworkflow denominator')
        need(x['source_builds'],'build candidates')
        for b in x['source_builds']:
            shape(b,'source_id source_version source_url installed_build'); nonempty(b,'source_id source_version source_url'); need(b['installed_build'] is None,'source pin is not tested build')
            need(b['source_id'] in sources,'unknown build source')
            s=sources[b['source_id']]
            need(b['source_version']==s['version'] and b['source_url']==s['url'],'exact source/version/build join')
        cp=x['cell_plan']
        shape(cp,'status maximum_cells maximum_executions selection exact_cell_manifest offered_load_schedule sampler_build_and_overhead cache_state subscription_attribution human_evaluator_admission confirmation_sample_plan unfinished_tasks admission_schema')
        need(cp['status']=='unadmitted' and type(cp['maximum_cells']) is int and cp['maximum_cells']==2 and type(cp['maximum_executions']) is int and cp['maximum_executions']==6,'bounded cell/execution count')
        need(all(cp[k] is None for k in ['exact_cell_manifest','offered_load_schedule','sampler_build_and_overhead','subscription_attribution','human_evaluator_admission','confirmation_sample_plan']),'unavailable cell admissions')
        need(cp['cache_state']=='unknown-until-observed-or-documented-disabled','cache observation boundary'); nonempty(cp,'selection unfinished_tasks')
        need(cp['admission_schema']=='probe-admission-schema.json','typed future admission')
        if x['family']=='simulation':
            need('twenty-seven' in x['fixture_specification'] and 'comparison-contract.json' in x['fixture_specification'] and 'trace IDs' in x['fixture_specification'],'simulation corpus binding')

def research_log_gate(log):
    shape(log,'schema_version status integrator routes limits observed_integration_runs review_results')
    need(log['status']=='research-synthesis-complete-final-gates-pending' and log['integrator']=='native Astra sole writer','research status')
    need(log['observed_integration_runs']==[] and log['review_results']==[],'no in-candidate invented observations/reviews')
    need(log['limits']==dict(maximum_concurrent_workers=4,nested_delegation=False,writer_count=1,new_metered_spend=0,usage_resets=False),'research limits')
    need(isinstance(log['routes'],list) and len(log['routes'])>=6,'research route receipts')
    for r in log['routes']:
        shape(r,'role model effort read_only privacy included_capacity timing findings')
        nonempty(r,'role privacy included_capacity timing findings')
        need(r['read_only'] is True and (r['model'],r['effort']) in {('gpt-5.6-luna','high'),('gpt-6-astra','xhigh')},'recorded native route')

def comparison_gate(c):
    shape(c,'schema_version status start_commit boundaries equal_environment model_implemented model_results obligations core_bounds cross_area_bounds fairness mapping_checks result_categories traces calibrations freeze_gate bound_resolution')
    need(c['start_commit']==START and c['status']=='preregistered-not-model-checked' and c['model_implemented'] is False and c['model_results']==[],'no model result')
    need(c['boundaries']==['aggregate-plus-bounded-broker-refinement','broker-inclusive'] and c['equal_environment'] is True,'both equal-environment boundaries')
    need([x['id'] for x in c['obligations']]==['effect-join','epoch-types','writer-pool','pause','uncertainty','flow-replay'],'six M1 obligations')
    for x in c['obligations']: shape(x,'id input required forbidden'); nonempty(x,'input required forbidden')
    need(c['core_bounds']==dict(aggregates=1,tasks=1,effects=1,timers=1,verifiers=1,workers=2,goal_epochs=2,plan_revisions=2,attempts=2,lease_epochs=3,events=20),'unchanged original bounds')
    need(c['cross_area_bounds']==dict(goals=2,assistants=2,tasks=2,hosts=2,queue_capacity=2,configuration_epochs=2,unresolved_effects=1,update_candidates=1,pool_owners=1,permits_per_host=1,recipient_fence_epochs=2,retired_records=1,stale_requests=1),'cross-area equal bounds')
    need(all(type(v) is int for b in ['core_bounds','cross_area_bounds'] for v in c[b].values()),'integer model bounds')
    need(c['fairness']==dict(safety_eventual_delivery=False,local='weak fairness for continuously enabled kernel/broker actions',lazy_stop='named bounded operation boundary',provider_response_assumed=False,owner_response_assumed=False,partition_recovery_assumed=False),'fairness/uncertainty')
    need(c['mapping_checks']==['initialization','step preservation or visible-state stutter','invariant implication','composition','liveness compatibility','auxiliary behavior preservation after hiding'],'composition checks')
    need(c['result_categories']==['semantic-counterexample','unenforceable-mapping-assumption','inadequate-proof-technique','exploration-limit','conditional-pass'],'failure taxonomy')
    need([x['id'] for x in c['traces']]==['comparison.trace.'+str(i).zfill(2) for i in range(1,28)],'complete trace corpus')
    formal=text(PREFIX+'formal-boundaries.md')
    for t in c['traces']:
        shape(t,'id schedule required_outcome_and_mutant status result'); nonempty(t,'schedule required_outcome_and_mutant')
        need(t['status']=='constructed-unrun' and t['result'] is None and '| '+t['schedule']+' | '+t['required_outcome_and_mutant']+' |' in formal,'trace prose/boundary join')
    need(len(c['calibrations'])==2,'proof calibration'); strings(c['calibrations'],'calibrations'); nonempty(c,'freeze_gate')
    b=c['bound_resolution']
    shape(b,'profile_composition preference_revision_identities cross_area_aggregates optional_rights_holders optional_transfers_in_flight unresolved_dimensions resolved_configuration_digests per_trace_gate readiness')
    need(b['preference_revision_identities']==['R1','R2','R3'] and b['cross_area_aggregates']==2 and b['optional_rights_holders']==2 and b['optional_transfers_in_flight']==1,'profile cardinality separation')
    need(b['resolved_configuration_digests'] is None and len(b['unresolved_dimensions'])==5,'unresolved formal domains')
    strings(b['unresolved_dimensions'],'unresolved bounds'); nonempty(b,'profile_composition per_trace_gate readiness')

def admission_schema_gate():
    """Positive/adversarial synthetic data only; no run admission or integration result."""
    from jsonschema import Draft202012Validator, ValidationError
    schema=read('probe-admission-schema.json'); Draft202012Validator.check_schema(schema)
    need(schema['additionalProperties'] is False and set(schema['required'])==set(schema['properties']) and len(schema['required'])==30,'closed admission root')
    def fixture(s):
        if 'const' in s: return s['const']
        if 'enum' in s: return s['enum'][0]
        if s['type']=='object': return {k:fixture(v) for k,v in s['properties'].items()}
        if s['type']=='array': return [fixture(s['items']) for _ in range(s.get('minItems',0))]
        if s['type']=='boolean': return False
        if s['type']=='integer': return s['minimum']
        if s.get('pattern')=='^[0-9a-f]{64}$': return 'a'*64
        if 'pattern' in s: return '2026-09-07T22:00:00Z'
        return 'SYNTHETIC_ONLY_NOT_ADMITTED'
    f=fixture(schema); validator=Draft202012Validator(schema)
    def validate(v):
        validator.validate(v)
        datetime.fromisoformat(v['deadline_utc'].replace('Z','+00:00'))
        datetime.fromisoformat(v['included_capacity']['observed_at_utc'].replace('Z','+00:00'))
        need(v['resources']['control_reserved_events']<=v['resources']['max_queue_events'],'control reserve exceeds total')
        need(v['resources']['mrtr_deadline_seconds']<=60*v['maximum_minutes'],'MRTR exceeds packet duration')
    validate(f)
    paths=[['resources',k] for k in 'max_decoded_frame_bytes max_stdio_line_bytes max_http_header_bytes max_mrtr_total_bytes max_mrtr_rounds mrtr_deadline_seconds max_queue_events max_queue_bytes control_reserved_events max_spool_bytes max_cache_bytes max_global_pool_keys max_owned_processes'.split()]
    paths += [['privacy',k] for k in 'allowed_destinations capture_body capture_headers capture_request_state capture_urls capture_telemetry redaction_rules retention_seconds deletion_and_access_policy mcp_name_and_param_header_policy third_party_authorization_token_policy'.split()]
    paths += [['binding',k] for k in 'provider executing_harness supported_interface authentication billing_source host version intended_distribution'.split()]
    paths += [['included_capacity'],['fixture'],['executable'],['authorization_reference'],['measurement'],['cleanup'],['stop_conditions']]
    rejected=0
    for path in paths:
        bad=copy.deepcopy(f);node=bad
        for k in path[:-1]: node=node[k]
        del node[path[-1]]
        try: validate(bad)
        except (ValidationError,ValueError): rejected+=1;continue
        raise ValueError('admission schema accepts missing '+str(path))
    for path,value in [(['new_metered_spend'],1),(['usage_resets_allowed'],True),(['privacy','private_repository_payload_allowed'],True),(['privacy','real_credentials_in_fixture_allowed'],True),(['resources','max_mrtr_rounds'],0),(['resources','max_http_header_bytes'],True),(['maximum_cells'],3),(['maximum_executions'],7),(['executable','sha256'],'unverified'),(['deadline_utc'],'2026-02-31T22:00:00Z'),(['resources','control_reserved_events'],2),(['resources','mrtr_deadline_seconds'],61)]:
        bad=copy.deepcopy(f);node=bad
        for k in path[:-1]:node=node[k]
        node[path[-1]]=value
        try:validate(bad)
        except (ValidationError,ValueError):rejected+=1;continue
        raise ValueError('admission schema accepts weakening '+str(path))
    return rejected

def canonical_preservation(overrides=None):
    """Preserve baseline contracts; exact source-justified updates are enumerated below.

    This catches removal/replacement, not semantic contradiction in new prose: reviewers
    must still assess additions and source applicability.
    """
    overrides={} if overrides is None else overrides
    replacements={'docs/v3/ROUTE-CAPABILITIES.md':{
        '[The current machine-readable matrix](foundation-research/mark2-research/compatibility.json)':'[The preserved Mark 2 matrix](foundation-research/mark2-research/compatibility.json)',
        '| Codex | App Server has rich turn/thread controls; command/WebSocket transport is experimental and documented unsuitable for production use |':'| Codex | Current stdio App Server integration is distinct from experimental WebSocket/methods; exact build, sandbox-sensitive commands and helper accounting require probes |'},
        'docs/v3/ARCHITECTURE.md':{
        'Canonical event order resolves Stop/update races. Stop accepted first fences later work; an':'Canonical event order resolves admission order; Stop fences new permits. A previously issued',
        'update already past an external activation boundary cannot claim cancellation reversed it.':'permit may activate after local Stop until the recipient fence is installed; cancellation is not rollback.'}}
    for path in read('manifest.json')['allowed_canonical_paths']:
        old=git('show',START+':'+path); current=overrides.get(path,text(path))
        if path.endswith('.json'):
            a=strict(old);b=strict(current)
            need({k:v for k,v in a.items() if k!='ranges'}=={k:v for k,v in b.items() if k!='ranges'},'registry baseline keys')
            need(a['ranges']==[r for r in b['ranges'] if r['prefix']!='CMP'],'registry baseline ranges')
            continue
        sequence=iter(current.splitlines())
        for line in old.splitlines():
            target=replacements.get(path,{}).get(line,line)
            need(any(s==target for s in sequence),'canonical baseline changed: '+path+' '+line[:90])

def goal_gate(g,p,m):
    shape(g,'schema_version id parent predecessor authorization status source_commit branch objective allowed_paths allowed_new_directory non_goals start_utc deadline_utc synthesis_review_reserve_minutes max_concurrent_read_only_workers max_discovery_packet_minutes writer new_metered_spend usage_resets_allowed acceptance_gate acceptance checkpoint_rule')
    need(g['id']==m['goal'] and g['parent']==m['parent'] and g['predecessor']==m['predecessor'] and g['source_commit']==START and g['branch']==BRANCH,'GoalSpec identity')
    need(g['allowed_paths']==m['allowed_canonical_paths'] and g['allowed_new_directory']==PREFIX and g['status']=='authorized-research-only' and g['writer']=='Astra sole integrator','GoalSpec scope')
    need(g['max_concurrent_read_only_workers']==4 and g['max_discovery_packet_minutes']==30 and g['synthesis_review_reserve_minutes']>=90 and g['usage_resets_allowed'] is False and g['new_metered_spend']==0,'GoalSpec resources')
    need(g['start_utc']==m['started_utc'] and g['deadline_utc']==m['deadline_utc'] and START in g['acceptance_gate'] and 'check.py' in g['acceptance_gate'],'GoalSpec clock/gate')
    strings(g['non_goals'],'non-goals'); strings(g['acceptance'],'acceptance')
    shape(p,'schema_version goal start_commit revisions phases new_owner_decisions first_grillme remaining_experiments')
    need(p['goal']==m['goal'] and p['start_commit']==START and p['new_owner_decisions']==[] and p['first_grillme'] is None and p['revisions'] and p['phases'] and p['remaining_experiments'],'resumable plan/no manufactured queue')

def adversarial(e,c,r,p,g,plan,m):
    validators=[lambda d:evidence_gate(d),lambda d:coverage_gate(d,e),lambda d:route_gate(d,e),lambda d:probe_gate(d,e),lambda d:goal_gate(d,plan,m),comparison_gate,research_log_gate,preflight]
    originals=[e,c,r,p,g,read('comparison-contract.json'),read('research-log.json'),m]
    for fn,d in zip(validators,originals): fn(d)
    cases=[(0,['schema_version'],True),(0,['observed_runtime_runs'],['synthetic']),(0,['measured_results'],[1]),(0,['sources',0,'url'],'https://example.com/wrong'),(0,['sources',0,'receipts',0,'sha256'],'bad'),(0,['claims',0,'statement'],'Changed.'),(0,['claims',0,'source_ids'],[]),(0,['claims',0,'state'],'measured'),(1,['areas'],[]),(1,['areas',0,'approaches'],['one']),(1,['cross_area_cases'],[]),(1,['required_capabilities_removable_by_benchmark'],True),(1,['ranking'],['completion']),(1,['human_outcomes'],[]),(2,['entry_names'],[]),(2,['path_ids'],r['path_ids'][:-1]),(2,['critical_names'],[]),(2,['controls'],[]),(2,['deltas',0,'binding','authentication'],''),(2,['deltas',0,'tested_build'],'synthetic'),(2,['role_paths'],{}),(2,['role_paths','reviewer','upstream_only'],'Extra API key required'),(3,['execution_authorized'],True),(3,['probes',0,'actual_host'],'invented'),(3,['probes',0,'fixture_digest'],'invented'),(3,['probes',0,'included_capacity_lease'],'invented'),(3,['probes',0,'result'],'pass'),(3,['probes',0,'full_workflow_costs'],['initial work']),(3,['probes',0,'new_metered_spend'],1),(3,['probes',0,'cleanup'],''),(3,['probes',0,'source_builds',0,'installed_build'],'tested'),(4,['usage_resets_allowed'],True),(4,['source_commit'],'0'*40),(4,['max_concurrent_read_only_workers'],5)]
    cases += [(0,['sources',0,'receipts',0,'sha256'],'0'*64),(0,['sources',0,'receipts',0,'bytes'],1),(0,['sources',0,'receipts',0,'url'],'https://example.com/unrelated'),(0,['claims',0,'canonical'],'CONTROL_PLANE.md'),(2,['deltas',0,'source_ids'],[]),(2,['deltas',0,'source_ids'],['SRC-V3-001']),(2,['deltas',0,'next_test'],'missing-family'),(3,['probes',0,'family'],'performance'),(3,['probes',0,'baseline'],[]),(3,['probes',0,'treatments'],[]),(3,['probes',0,'source_builds',0,'source_id'],'SRC-V3-001'),(3,['probes',0,'source_builds',0,'source_version'],'main'),(3,['probes',0,'source_builds',0,'source_url'],'javascript:alert(1)'),(3,['probes',0,'cell_plan','maximum_cells'],100),(3,['probes',0,'cell_plan','exact_cell_manifest'],'invented'),(3,['probes',0,'cell_plan','subscription_attribution'],'assumed'),(3,['probes',0,'cell_plan','cache_state'],'cold-after-30-minutes'),(5,['model_implemented'],True),(5,['model_results'],['pass']),(5,['boundaries'],['broker-inclusive']),(5,['equal_environment'],False),(5,['obligations'],[]),(5,['obligations',0,'required'],''),(5,['core_bounds','events'],21),(5,['core_bounds','aggregates'],True),(5,['cross_area_bounds','goals'],1),(5,['cross_area_bounds','pool_owners'],2),(5,['fairness','provider_response_assumed'],True),(5,['mapping_checks'],['initialization']),(5,['result_categories'],['conditional-pass']),(5,['traces'],[]),(5,['traces',0,'result'],'observed'),(5,['traces',0,'schedule'],'unbound'),(5,['calibrations'],[]),(6,['observed_integration_runs'],[{'status':'measured-pass'}]),(6,['review_results'],[{'candidate':'invented','verdict':'approved'}]),(6,['limits','nested_delegation'],True),(6,['routes',0,'read_only'],False),(6,['routes',0,'model'],'unapproved'),(7,['inputs'],m['inputs'][:1]),(7,['review_reserve_start_utc'],'2026-09-01T00:00:00Z')]
    cases += [(3,['probes',0,'cell_plan','admission_schema'],'missing.json'),(5,['bound_resolution','preference_revision_identities'],['R1','R3']),(5,['bound_resolution','resolved_configuration_digests'],['invented']),(5,['bound_resolution','unresolved_dimensions'],[]),(0,['sources',0,'receipts'],e['sources'][1]['receipts']),(2,['deltas',0,'source_ids'],['SRC-V3-229']),(2,['deltas',0,'binding','provider'],'UnrelatedProvider'),(2,['deltas',0,'binding','version'],'main'),(3,['probes',5,'fixture_specification'],'Twelve constructed traces')]
    cases += [(0,['claims',0,'canonical'],'docs/v3/CLAIM-LEDGER.md')]
    rejected=[]
    for i,path,value in cases:
        d=copy.deepcopy(originals[i]); node=d
        for k in path[:-1]: node=node[k]
        node[path[-1]]=value
        try: validators[i](d)
        except (ValueError,KeyError,TypeError): rejected.append('/'.join(map(str,path))); continue
        raise ValueError('accepted mutant '+str(path))
    canonical_preservation()
    for path,before,after in [('docs/v3/CLAIM-LEDGER.md','with no AI ARM Manager','with an AI ARM Manager'),('docs/v3/EXECUTIVES.md','immediate halt is the only operative profile','immediate halt may be replaced by drain without Owner approval')]:
        original=text(path); need(before in original,'meaningful canonical mutant anchor')
        try: canonical_preservation({path:original.replace(before,after)})
        except ValueError: rejected.append('canonical-preservation/'+path); continue
        raise ValueError('accepted canonical weakening '+path)
    return rejected

def docs_gate(changed):
    PRIOR['document_gate'](changed)
    canonical_preservation(); comparison_gate(read('comparison-contract.json')); research_log_gate(read('research-log.json'))
    f=text(PREFIX+'formal-boundaries.md')
    for v in ['effect_observation_record','writer fence','current-immediate','OR-015','RESET','weak fairness','twenty events','three lease epochs','composition','unknown','language','storage','not a formal model or proof','No M1 schema or contract is edited']: need(v in f,'formal comparison missing '+v)
    a=text(PREFIX+'architectures.md')
    for v in ['A: demand-activated','B: resident','C: durable','upstream-only','license','No new route is marked observed']: need(v in a,'dossier missing '+v)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base'); ap.add_argument('--candidate'); ap.add_argument('--preflight',action='store_true')
    ap.add_argument('--working',action='store_true',help='Documentation development checks; not final acceptance')
    args=ap.parse_args(); m,allowed=preflight()
    if args.preflight: print('PREFLIGHT_PASS; final acceptance not asserted'); return
    e,c,r,p,g,plan=[read(n) for n in ['evidence.json','coverage.json','route-deltas.json','probes.json','goal.json','plan.json']]
    mutants=adversarial(e,c,r,p,g,plan,m)
    admission_mutants=admission_schema_gate(); source_receipts=retrieval_audit(e)
    ev,matrix,trials,decisions=[M['read'](n) for n in ['evidence.json','compatibility.json','experiments.json','decisions.json']]
    M['data_gate'](ev,matrix,trials,decisions)
    sources,claims=bindings(ev); historical=M['historical_gate'](sources,claims)
    oi=M['read']('validation-inventory.json'); arithmetic=M['arithmetic_gate'](oi)
    # Historical URL/statement mutants must exercise the extended positive binding guard.
    M['adversarial'].__globals__['bindings']=bindings
    old_mutants=M['adversarial'](ev,matrix,trials,decisions,oi)
    d,pp,cc,ii=[PRIOR['read'](n) for n in ['directions.json','research-plan.json','companion-review.json','validation-inventory.json']]
    PRIOR['direction_gate'](d,ii); PRIOR['plan_gate'](pp); PRIOR['companion_gate'](cc)
    mark3_mutants=PRIOR['adversarial'](d,pp,cc,ii)
    if args.working:
        changed=git('diff','--name-only',START).splitlines()+git('ls-files','--others','--exclude-standard').splitlines()
        need(all(x in allowed or x.startswith(PREFIX) for x in changed),'working scope'); docs_gate(sorted(set(changed)))
        print(json.dumps(dict(status='WORKING_DOCUMENTATION_PASS_NOT_FINAL',new_mutants=len(mutants),admission_schema_mutants=admission_mutants,verified_source_receipts=source_receipts,mark2_mutants=old_mutants,mark3_mutants=mark3_mutants,arithmetic=arithmetic,historical=historical)))
        return
    need(args.base==START and isinstance(args.candidate,str) and re.fullmatch('[0-9a-f]{40}',args.candidate),'full frozen hashes')
    need(git('rev-parse','HEAD')==args.candidate and not git('status','--porcelain=v1','--untracked-files=all'),'clean exact candidate')
    changed=git('diff','--name-only','--no-renames',START,args.candidate).splitlines()
    need(changed and all(x in allowed or x.startswith(PREFIX) for x in changed),'bounded diff')
    need(not git('diff','--name-only','--diff-filter=D',START,args.candidate),'no deleted artifact')
    need({x.name for x in AREA.iterdir()}==FILES,'closed campaign files'); git('diff','--check',START,args.candidate); docs_gate(changed)
    inv=read('validation-inventory.json'); shape(inv,'schema_version start_commit regression_commands regression_entrypoints artifacts limitations')
    need(inv['start_commit']==START,'inventory start')
    commands=OLD['regression_commands']()
    need(inv['regression_commands']==commands==ii['regression_commands'] and len(commands)==25,'unchanged 25-command inventory')
    expected={next(s for s in cmd if s.endswith('.py')) for cmd in commands}
    need(rows(inv['regression_entrypoints'],'entrypoints','path')==expected,'entrypoint set')
    for x in inv['regression_entrypoints']:
        shape(x,'path sha256'); raw=git('show',START+':'+x['path'],binary=True)
        need(sha(raw)==x['sha256'] and raw==git('show',args.candidate+':'+x['path'],binary=True),'unchanged historical code')
    need(rows(inv['artifacts'],'artifacts','path')==set(changed)-{PREFIX+'validation-inventory.json'},'artifact coverage')
    for x in inv['artifacts']:
        shape(x,'path git_blob_sha256')
        need(sha(git('show',args.candidate+':'+x['path'],binary=True))==x['git_blob_sha256'],'artifact digest '+x['path'])
    common=Path(git('rev-parse','--git-common-dir'))
    if not common.is_absolute(): common=(ROOT/common).resolve()
    out=common/'research-attestations'/'mark3-comparison'/args.candidate; out.mkdir(parents=True,exist_ok=True)
    runid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+str(time.time_ns())[-6:]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
    if os.name=='nt':
        bash=Path(os.environ.get('ProgramFiles',''))/'Git/bin'
        if (bash/'bash.exe').is_file(): env['PATH']=str(bash)+os.pathsep+env.get('PATH','')
    receipts=[]
    for i,cmd in enumerate(commands):
        before=time.monotonic()
        result=subprocess.run([sys.executable,*cmd[1:]],cwd=ROOT,env=env,capture_output=True,timeout=240)
        raw=result.stdout+result.stderr; (out/f'{runid}-{i:02}.log').write_bytes(raw)
        row=dict(command=cmd,exit_code=result.returncode,seconds=round(time.monotonic()-before,3),output_sha256=sha(raw))
        receipts.append(row); print(json.dumps(row),flush=True); need(result.returncode==0,'regression failed: '+' '.join(cmd))
    need(git('rev-parse','HEAD')==args.candidate and not git('status','--porcelain=v1','--untracked-files=all'),'candidate changed during gate')
    receipt=dict(base=START,candidate=args.candidate,run_id=runid,new_mutants=mutants,admission_schema_mutants=admission_mutants,verified_source_receipts=source_receipts,mark2_mutants=old_mutants,mark3_mutants=mark3_mutants,arithmetic_cases=arithmetic,historical=historical,regressions=receipts,artifacts={x:sha(git('show',args.candidate+':'+x,binary=True)) for x in changed},runtime_integration_observed=False,formal_model_checked=False,privacy_certified=False)
    raw=(json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode(); (out/(runid+'.json')).write_bytes(raw)
    print('MARK3_COMPARISON_GATE_PASS '+json.dumps(dict(candidate=args.candidate,run_id=runid,regressions=len(receipts),new_mutants=len(mutants),receipt_sha256=sha(raw))),flush=True)

if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.TimeoutExpired) as e:
        print('MARK3_COMPARISON_GATE_FAIL '+str(e),file=sys.stderr); sys.exit(1)

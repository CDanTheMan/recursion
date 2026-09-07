"""Allowlisted projections of retained private fixture receipts; never copy raw prose."""
import hashlib
import json
import pathlib
from rpc import validate_trace


def require(value, message):
    if not value: raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def read(path):return json.loads(pathlib.Path(path).read_text(encoding='utf8'))


def outcomes(result):
    rows=result.get('outcomes',[]);mapped={r['check']:r for r in rows}
    require(len(mapped)==len(rows),'duplicate outcome identity')
    return mapped


def stderr_json(result, kind):
    found=[]
    for e in result['trace']['events']:
        if e['direction']!='stderr' or not e['payload'].startswith('{'):continue
        try:item=json.loads(e['payload'])
        except ValueError:continue
        if item.get('type')==kind:found.append(item)
    return found


def codex_projection(a,r,accepted):
    os=outcomes(r)
    traces=[o['trace'] for o in r['outcomes'] if o['check']=='crash_process_settlement']+[r['trace']]
    if accepted:
        expected={'initialize','effective_config','thread_start','stale_steer_rejected','inflight_fork_result','active_steer','steer_reached_same_turn_provider_input','blocking_question_interrupt','late_old_answer_did_not_release_current_waiter','current_question_answer_completed','fork_boundary_history','crash_process_settlement','post_crash_history_resume'}
        require(set(os)==expected,'Codex complete outcome set')
        require(r['failure'] is None and r['watchdog_fired'] is False,'Codex failure or timeout')
        for trace in traces:validate_trace(trace)
        require(len(r['scripted_endpoint_requests'])==5,'Codex scripted call count')
        require(all(not q['credential_header_present'] and q['path']=='/v1/responses' for q in r['scripted_endpoint_requests']),'Codex route/auth drift')
        for q in r['scripted_endpoint_requests']:
            require(q['body']['model']=='gpt-6-astra' and {t.get('name',t.get('type')) for t in q['body']['tools']}=={'update_plan','request_user_input','skills','fixture_barrier'},'Codex model/tool inventory')
        require(r['actual_model_calls']==0 and r['simulated_usage'] is True,'Codex simulated boundary')
        require(os['blocking_question_interrupt']['terminal']['params']['turn']['status']=='interrupted','Codex interruption')
        require(os['current_question_answer_completed']['terminal']['params']['turn']['status']=='completed','Codex current reply')
        require('error' in os['stale_steer_rejected']['result'] and 'error' in os['inflight_fork_result']['result'],'Codex negative guards')
        require(r['cleanup_job_accounting']['ActiveProcesses']==0 and os['crash_process_settlement']['job']['ActiveProcesses']==0,'Codex owned cleanup')
        thread=os['thread_start']['result']['result']['thread']['id']
        first=os['steer_reached_same_turn_provider_input']['result']['params']['turn']['id']
        interrupted=os['blocking_question_interrupt']['terminal']['params']['turn']['id']
        current=os['current_question_answer_completed']['terminal']['params']['turn']['id']
        require(len({first,interrupted,current})==3,'Codex distinct turn identities')
        require('PUBLIC_OWNER_STEER_B' in json.dumps(r['scripted_endpoint_requests'][1]['body']) and 'PUBLIC_STALE_MUST_NOT_APPEAR' not in json.dumps(r['scripted_endpoint_requests']),'Codex actual steer input')
        oldq=os['blocking_question_interrupt']['request']
        require(oldq['params']['isBlocking'] is True and oldq['params']['threadId']==thread and oldq['params']['turnId']==interrupted,'Codex blocking question identity')
        questions=[e['payload'] for e in traces[0]['events'] if e['direction']=='receive' and isinstance(e['payload'],dict) and e['payload'].get('method')=='item/tool/requestUserInput']
        require(len(questions)==2 and questions[0]==oldq and questions[1]['id']!=oldq['id'] and questions[1]['params']['threadId']==thread and questions[1]['params']['turnId']==current,'Codex question generations')
        late=os['late_old_answer_did_not_release_current_waiter']
        require(late['provider_requests_before']==late['provider_requests_after']==4 and late['observation_window_s']==.3,'Codex late answer observation')
        outputs={x.get('call_id'):x.get('output') for x in r['scripted_endpoint_requests'][-1]['body']['input'] if x.get('type')=='function_call_output'}
        require(json.loads(outputs[questions[1]['params']['itemId']])['answers']['public_color']['answers']==['blue'],'Codex current answer reached provider input')
        fork=os['fork_boundary_history']['result']['result']['thread']
        require(fork['id']!=thread and fork['forkedFromId']==thread and [t['id'] for t in fork['turns']]==[first] and 'PUBLIC_OWNER_STEER_B' in json.dumps(fork) and 'PUBLIC_BLUE_CONFIRMED' not in json.dumps(fork),'Codex fork boundary')
        resumed=os['post_crash_history_resume']['result']['result']['thread']
        require(resumed['id']==thread and [(t['id'],t['status']) for t in resumed['turns']]==[(first,'completed'),(interrupted,'interrupted'),(current,'completed')] and 'PUBLIC_BLUE_CONFIRMED' in json.dumps(resumed),'Codex resumed history')
    counters=[]
    original=os['thread_start']['result']['result']['thread']['id']
    for trace_index,trace in enumerate(traces):
        for e in trace['events']:
            p=e['payload']
            if e['direction']=='receive' and isinstance(p,dict) and p.get('method')=='thread/tokenUsage/updated':
                usage=p['params']['tokenUsage'];counters.append({'server_instance':trace_index+1,'lineage':'original' if p['params']['threadId']==original else 'fork','usage':usage})
    if accepted:
        require([(c['server_instance'],c['lineage'],c['usage']['total']['totalTokens']) for c in counters]==[(1,'original',15),(1,'original',30),(1,'original',45),(1,'original',60),(1,'original',75),(1,'fork',30),(2,'original',75)],'Codex counter lineage/replay')
    return {'scripted_http_posts':len(r['scripted_endpoint_requests']),'actual_model_calls':r['actual_model_calls'],
            'simulated_usage':r['simulated_usage'],'observed_checks':list(os),'usage_notifications':counters,
            'owned_processes_at_cleanup':r['cleanup_job_accounting']['ActiveProcesses'],
            'watchdog_fired':r.get('watchdog_fired'),'server_launches':len(traces),
            'elapsed_seconds':r['elapsed_s'],'recovery_boundary':'idle server crash; read/resume only, no new inference after restart'}


def hermes_projection(a,r,accepted):
    os=outcomes(r);real=a.get('mode')=='real'
    if accepted:
        require(r['failure'] is None and r['watchdog_fired'] is False,'Hermes failure or timeout')
        validate_trace(r['trace'])
        require(r['namespace_owner_exit_code']==0 and r['cleanup_job']['ActiveProcesses']==0,'Hermes namespace cleanup')
        require(r['actual_model_calls']==0,'Hermes actual inference')
        canary=stderr_json(r,'namespace_admission');require(len(canary)==1 and canary[0]['network_canary_errno']==101,'Hermes network canary')
        turn=os['interrupt_after_delta']
        require(turn['second_start']['params']['seq']<turn['delta']['params']['seq']<turn['terminal']['params']['seq'],'Hermes event correlation')
    projection={'agent':'real' if real else 'upstream synthetic','actual_model_calls':r['actual_model_calls'],
                'simulated_usage':True,'observed_checks':list(os),'namespace_owner_exit_code':r.get('namespace_owner_exit_code'),
                'owned_windows_processes_at_cleanup':r['cleanup_job']['ActiveProcesses'],'watchdog_fired':r.get('watchdog_fired')}
    if real:
        receipts=stderr_json(r,'scripted_chat_receipt');require(len(receipts)==1,'missing mock receipt')
        receipt=receipts[0];requests=receipt['requests']
        projection['http_requests']=[{'method':x['method'],'path':x['path'],'status':x.get('status',200),'rejected':x.get('rejected',False)} for x in requests]
        projection['metadata_detection_errors']=len(receipt['errors'])
        projection['scripted_http_posts']=sum(x['method']=='POST' for x in requests)
        if 'postinterrupt_active' in os:
            info=os['postinterrupt_active']['result']['result']['info']
            projection['postinterrupt_reported_usage']={k:v for k,v in info['usage'].items() if k in {'input','output','total','calls'}}
            projection['outgoing_tool_counts']=[len(x['body'].get('tools',[])) for x in requests if x['method']=='POST']
        if 'history' in os:
            projection['normal_durable_messages']=len(os['history']['result']['result']['messages'])
        if 'postinterrupt_durable_history' in os:
            before=os['postinterrupt_durable_history']['result']['result']['messages']
            after=os['same_process_resumed_history']['result']['result']['messages']
            projection['interrupt_durable_messages']=len(before)
            projection['same_process_resume_preserved_rows']=before==after
        if accepted:
            require(not receipt['errors'] and receipt['active']==0,'Hermes scripted route errors')
            require(projection['scripted_http_posts']==2 and projection['outgoing_tool_counts']==[0,0],'Hermes calls/tools')
            require({(x['method'],x['path']) for x in requests}=={('POST','/v1/chat/completions'),('GET','/v1/models'),*[('GET',p) for p in ['/api/v1/models','/api/tags','/v1/props','/props','/version']]},'Hermes exact metadata route set')
            require(len(requests)==8 and all(x.get('status')==404 for x in requests if x.get('purpose')=='pinned local-server detection negative'),'Hermes metadata count/negative responses')
            require(projection['postinterrupt_reported_usage']=={'input':11,'output':7,'total':18,'calls':1},'Hermes incomplete reported usage boundary')
            require(os['normal_terminal']['result']['params']['payload']['status']=='complete','Hermes normal completion')
            require(os['interrupt_after_delta']['terminal']['params']['payload']['status']=='interrupted','Hermes interrupted terminal')
            require(os['postinterrupt_active']['result']['result']['running'] is False,'Hermes session not settled')
            require(projection['same_process_resume_preserved_rows'],'Hermes durable history changed')
            rows=os['postinterrupt_durable_history']['result']['result']['messages']
            first=os['history']['result']['result']['messages']
            require(rows[:len(first)]==first,'Hermes prior durable rows lost during interruption')
            require([x['role'] for x in rows]==['user','assistant','user','assistant'],'Hermes history roles')
            require([x['text'] for x in rows]==['PUBLIC_PERSISTENCE_PROMPT','PUBLIC_HISTORY_COMPLETE','PUBLIC_INTERRUPT_PROMPT','PUBLIC_INTERRUPT_PARTIAL'],'Hermes history text')
            ids=[x['row_id'] for x in rows];require(len(set(ids))==4 and all(type(x)is int and x>0 for x in ids),'Hermes durable row identities')
            resume=os['same_process_stored_session_resume']['result']['result']
            stored=os['postinterrupt_active']['result']['result']['session_key']
            live=os['session_create']['result']['result']['session_id']
            require(os['session_close']['result']['result']['closed'] is True and resume['session_id']!=live and resume['resumed']==stored and resume['session_key']==stored,'Hermes close/resume identity')
            final_canary=stderr_json(r,'post_loopback_network_canary');require(len(final_canary)==1 and final_canary[0]['errno']==101,'Hermes loopback external-route canary')
    return projection


def ownership_projection(a,r,accepted):
    rows=[]
    for x in r['results']:
        gap=x['mode']=='post_create' and x['boundary']=='created'
        if accepted:
            cardinality=2 if x['boundary']=='descendant' else 1
            fields=['identities','live_immediately_before_crash','survived_broker_death','target_membership_before_crash']
            require(all(len(x[k])==cardinality for k in fields) and len(x['barrier']['identities'])==cardinality and len(x['barrier']['pids'])==cardinality,'ownership nonvacuous observation cardinality')
            require(len(set(x['barrier']['pids']))==cardinality and all(type(p)is int and p>0 for p in x['barrier']['pids']),'ownership process identity set')
            require(all(type(i['creation_filetime'])is int and i['creation_filetime']>0 and isinstance(i['image'],str) and i['image'] for i in x['identities']),'ownership creation identities')
            require(x['observer_job_handle_closed_before_crash'] is True and x['outer_safety_job'] is True and x['broker_exit']==125,'ownership observer/termination boundary')
            require(not x['errors'] and not x['watchdog_fired'],'ownership observer failed')
            require(x['cleanup']['ActiveProcesses']==0 and x['broker_live_before_crash'],'ownership cleanup or live broker')
            require(all(x['live_immediately_before_crash']) and x['identities']==x['barrier']['identities'],'ownership child identity/liveness')
            require(all(v==gap for v in x['survived_broker_death']),'ownership survival mismatch')
            require(all(v!=gap for v in x['target_membership_before_crash']),'ownership membership mismatch')
        rows.append({k:x[k] for k in ['mode','boundary','survived_broker_death','target_membership_before_crash','oracle','watchdog_fired'] if k in x})
        rows[-1]['owned_processes_at_cleanup']=x['cleanup']['ActiveProcesses']
        rows[-1]['precrash_liveness_recorded']='live_immediately_before_crash' in x
    if accepted:
        require([(x['mode'],x['boundary']) for x in rows]==[(m,b) for m in ['post_create','at_birth'] for b in ['created','associated','descendant']],'ownership full treatment set')
    return {'executions':rows,'actual_model_calls':r['model_calls'],'timing_scope':'ordinary descendants and post-return barriers; no hostile escape or crash inside CreateProcess'}


def project(index_entry):
    directory=pathlib.Path(index_entry['directory']);rpath=directory/'result.json';apath=directory/'admission.json'
    a=read(apath);r=read(rpath);accepted=index_entry['use']=='accepted-scoped-evidence'
    require(sha(apath.read_bytes())==r['admission_sha256'],'admission/result digest mismatch')
    if accepted:
        required={'win_process.py'}
        if 'codex' in index_entry['id']:required|={'codex_probe.py','rpc.py','mock_responses.py','release.py'}
        elif 'ownership' in index_entry['id']:required|={'ownership_probe.py'}
        else:
            required|={'hermes_probe.py','hermes_fixture_entry.py','rpc.py'}
            if a.get('mode')=='real':required|={'mock_chat.py','release.py'}
        require(required<=set(a['tooling']),'incomplete executed tooling inventory')
        for name,digest in a['tooling'].items():
            require(pathlib.Path(name).name==name,'tooling path traversal')
            require(sha((directory/'tooling'/name).read_bytes())==digest,'missing/changed executed tooling')
    if a['kind']=='native-windows-owned-process-fault-probe':result=ownership_projection(a,r,accepted)
    elif 'codex' in index_entry['id']:result=codex_projection(a,r,accepted)
    elif 'hermes' in index_entry['id']:result=hermes_projection(a,r,accepted)
    else:raise ValueError('unrecognized retained run kind')
    failed=bool(r.get('failure')) or any(x.get('errors') for x in r.get('results',[]))
    build={k:a[k] for k in ['executable_sha256','config_sha256','source_pin','source_archive_sha256','dependencies_sha256','python_sha256'] if k in a}
    return {'id':index_entry['id'],'use':index_entry['use'],'recorded_failure':failed,'admitted_build':build,
            'admission_sha256':sha(apath.read_bytes()),'result_sha256':sha(rpath.read_bytes()),
            'tooling_sha256':a['tooling'],'started_at':a['at'],
            'ended_at':r.get('ended_at',r.get('results',[{}])[-1].get('ended_at')),
            'facts':result,'limitation':index_entry['limitation']}

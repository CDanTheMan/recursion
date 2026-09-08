"""Independent finite trace auditor. Does not import authority, actors or producer."""
import base64,copy,datetime,hashlib,json,pathlib,re,sys

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode('ascii')
def strict(raw):
    def pairs(items):
        d={}
        for k,v in items:need(k not in d,'duplicate JSON key');d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=pairs)
def load(p):return strict(p.read_bytes())

SCHEDULES='overlap_pin overlap_manifest two_pins stale_writer_cancel restart_live_pin pin_staged_loss pin_reply_loss publish_staged_loss publish_reply_loss retire_intent_loss retire_partial_loss reader_death publisher_death lock_exclusion acquisition_race negative_tokens'.split()

def artifacts(g,unit):
    # Independent byte specification, including the multibyte boundary.
    payload=[b'A',bytes([195,169]),b'B'];events={}
    for n in range(1,4):events[n]=encode(dict(version=1,stream='stream-a',epoch=2,id=n,event_cursor=n,byte_cursor=[1,3,4][n-1],payload=base64.b64encode(payload[n-1]).decode()))
    sn=1 if g==1 else 2;content=b''.join(payload[:sn])
    snap=dict(version=1,stream='stream-a',epoch=2,generation=g,cursor_unit=unit,event_cursor=sn,byte_cursor=len(content),state_base64=base64.b64encode(content).decode(),state_sha256=sha(content),prefix_event_hashes=[sha(events[n]) for n in range(1,sn+1)])
    files={f'event{n}.json':events[n] for n in ([1,2,3] if g==1 else [3])};files['snapshot.json']=encode(snap)
    files['manifest.json']=encode(dict(version=1,stream='stream-a',epoch=2,generation=g,cursor_unit=unit,tip_event=3,tip_byte=4,replay_floor_event=0 if g==1 else 2,replay_floor_byte=0 if g==1 else 3,files={n:sha(b) for n,b in files.items()}))
    return files

def content_reason(files,t,unit):
    prefix='store/'+t['directory']+'/';actual={p[len(prefix):]:h for p,h in files.items() if p.startswith(prefix)};wanted={n:sha(b) for n,b in artifacts(t['generation'],unit).items()}
    if set(actual)!=set(wanted):return 'generation-membership'
    if actual['manifest.json']!=t['manifest_sha256']:return 'manifest-pin'
    if actual['manifest.json']!=wanted['manifest.json']:return 'generation-manifest'
    if actual!=wanted:return 'generation-content'
    return None

def reason(s,r,files):
    op=r['op']
    if op=='claim':
        if s['selected']!=1:return 'domain-generation-limit'
        if s['writer'] is not None:return 'writer-busy'
        if r['expected_revision']!=s['revision']:return 'stale-parent'
    elif op in ('publish','revoke_writer'):
        if s['writer'] is None or r['writer']!=s['writer']:return 'stale-writer'
        if op=='revoke_writer':
            if r['reason'] not in ('controller-cancel','controller-observed-death'):return 'revocation-reason'
        else:
            if s['writer']['parent_revision']!=s['revision'] or s['writer']['boot']!=s['boot']:return 'stale-parent'
            return content_reason(files,s['writer'],s['unit'])
    elif op=='pin':
        if s['draining']:return 'drain-admission-closed'
        if (r['generation'],r['expected_revision'])!=(s['selected'],s['revision']):return 'not-current-selection'
        if len(s['pins'])>=2:return 'pin-capacity'
        if any(p['owner']==r['owner'] for p in s['pins'].values()):return 'duplicate-reader'
    elif op in ('validate_pin','release_pin'):
        if s['pins'].get(r['pin'].get('pin'))!=r['pin']:return 'invalid-pin'
        if op=='release_pin' and r['reason'] not in ('reader-complete','controller-cancel','controller-observed-death'):return 'release-reason'
    elif op=='reclaim':
        if s['selected']!=2:return 'cannot-reclaim-current'
        if any(p['generation']==1 for p in s['pins'].values()):return 'generation-pinned'
    else:need(op=='status','unknown audited command')
    return None

def transition(s,r,op,files,children):
    n=copy.deepcopy(s)
    if op=='boot':n.update(boot=s['boot']+1,writer=None,draining=False);return n
    if op=='reclaim':
        need(s['generations']['1']['status']=='retiring' and s['selected']==2 and not any(p['generation']==1 for p in s['pins'].values()),'reclaim precondition')
        need(not any(p.startswith('store/g1/') for p in files),'reclaim before physical deletion');n['generations']['1']['status']='removed';return n
    need(r is not None and reason(s,r,files) is None,'transition on refused request')
    expected={'retire':'reclaim','drain':'publish'}.get(op,op);need(r['op']==expected,'operation/request mismatch')
    if op=='claim':
        seq=s['writer_seq']+1;n['writer_seq']=seq;n['writer']=dict(instance=s['instance'],boot=s['boot'],serial=seq,owner=r['owner'],actor_nonce=r['actor_nonce'],parent_revision=s['revision'],generation=2,directory=f'g2-t{s["boot"]}-w{seq}',manifest_sha256=r['manifest_sha256'])
    elif op=='pin':
        seq=s['pin_seq']+1;g=s['selected'];d=s['generations'][str(g)];n['pin_seq']=seq;n['pins'][f'p{seq}']=dict(generation=g,unit=s['unit'],directory=d['directory'],manifest_sha256=d['manifest_sha256'],instance=s['instance'],pin=f'p{seq}',owner=r['owner'],actor_nonce=r['actor_nonce'])
    elif op in ('publish','drain'):
        busy=s['policy']=='drain-before-publish' and bool(s['pins']);need((op=='drain')==busy,'policy publication ordering')
        if busy:n['draining']=True
        else:
            w=s['writer'];n.update(selected=2,revision=1,writer=None,draining=False);n['generations']['1']['status']='retained';n['generations']['2']=dict(status='current',directory=w['directory'],manifest_sha256=w['manifest_sha256'])
    elif op=='release_pin':
        matching=[c for c in children.values() if c['role']=='reader' and c.get('ticket')==r['pin']]
        need(all(c.get('wait') for c in matching),'release before owned reader wait')
        if r['reason']=='reader-complete':need(matching and all(c.get('observation') and c['wait']['exit_code']==0 for c in matching),'completion without observed read')
        if r['reason']=='controller-observed-death':need(matching and all(c['wait']['killed'] for c in matching),'death without owned kill/wait')
        del n['pins'][r['pin']['pin']]
    elif op=='revoke_writer':
        if r['reason']=='controller-observed-death':need(any(c['role']=='writer' and c.get('ticket')==dict(r['writer'],unit=s['unit']) and c.get('wait',{}).get('killed') for c in children.values()),'publisher death without wait')
        n.update(writer=None,draining=False)
    elif op=='retire':n['generations']['1']['status']='retiring'
    else:raise ValueError('unknown transition '+op)
    return n

def audit(directory,result,journal_overrides=None,blob_overrides=None,row_overrides=None):
    cases=directory/'cases';expected={f'r{rep}-{policy}-{unit}-{name}' for rep in range(2) for policy in ('drain-before-publish','pinned-generation') for unit in ('event','utf8-byte') for name in SCHEDULES}
    need(len(result['rows'])==128 and {r['case'] for r in result['rows']}==expected,'closed schedule coverage')
    need({p.name for p in cases.iterdir() if p.is_dir()}==expected|{'blobs'},'raw directory coverage')
    blobs={p.name:p.read_bytes() for p in (cases/'blobs').iterdir()};need(all(sha(b)==h for h,b in blobs.items()),'content addressed bytes');blobs.update(blob_overrides or {})
    totals=dict(case_count=128,helpers=0,commits=0,completed_reads=0,killed_helpers=0,overlap_publications=0,reclaimed_with_current_reader=0)
    all_ids=[];all_nonces=set();all_instances=set();snapids=[]
    for row in result['rows']:
        case=cases/row['case'];need((row_overrides or {}).get(row['case'],load(case/'result.json'))==row,'raw row binding')
        events=(journal_overrides or {}).get(row['case'],[strict(line) for line in (case/'journal.jsonl').read_bytes().splitlines()]);need(events and events[0]['label']=='initial' and events[-1]['label']=='final','trace endpoints')
        dates=[datetime.datetime.fromisoformat(e['at']) for e in events];need(all(t.tzinfo for t in dates) and dates==sorted(dates),'trace time order')
        s=None;files={};children={};staged={};requests={};checks=[];lock=None;pending_phase=None
        for e in events:
            kind=e['kind']
            if pending_phase:need(kind=='snapshot' and e['label']==pending_phase,'phase snapshot adjacency');pending_phase=None
            if kind=='snapshot':
                snapids.append(e['snapshot']);nf=e['files'];need(all(h in blobs for h in nf.values()),'missing observed bytes');ns=strict(blobs[nf['authority.json']]);label=e['label']
                if s is None:
                    need(ns['boot']==ns['revision']==ns['writer_seq']==ns['pin_seq']==0 and ns['selected']==1 and ns['writer'] is None and ns['pins']=={} and ns['draining'] is False,'initial authority state')
                    need(ns['version']==1 and ns['unit']==row['unit'] and ns['policy']==row['policy'] and re.fullmatch('[0-9a-f]{32}',ns['instance']) and ns['instance'] not in all_instances,'fixture identity');all_instances.add(ns['instance']);lock=e['lock_identity'];need(lock['size']==1,'stable lock size')
                    need(ns['generations']=={'1':dict(status='current',directory='g1',manifest_sha256=sha(artifacts(1,row['unit'])['manifest.json'])),'2':dict(status='unpublished',directory=None,manifest_sha256=None)},'initial generation metadata');need(content_reason(nf,dict(generation=1,directory='g1',manifest_sha256=ns['generations']['1']['manifest_sha256']),row['unit']) is None,'initial generation bytes');s=ns
                need(e['lock_identity']==lock,'lock identity replacement')
                if label.endswith(':staged') and not label.endswith('/writer:staged'):
                    child,phase=label.split('/');op=phase.split(':')[0];need(children[child].get('lock')==0 and not children[child].get('wait'),'mutation outside authority lock');need(ns==s,'staging changed canonical state')
                    wanted=transition(s,requests.get(child,{}).get('request'),op,nf,children);need(strict(blobs[nf['authority.tmp']])==wanted,'staged transition differs');staged[child]=(op,wanted,nf['authority.tmp'])
                elif label.endswith(':committed'):
                    child,phase=label.split('/');op=phase.split(':')[0];need(child in staged and staged[child]==(op,ns,nf['authority.json']) and 'authority.tmp' not in nf,'commit differs from staged transition');s=ns;del staged[child];totals['commits']+=1
                    if op=='publish' and any(c['role']=='reader' and not c.get('wait') for c in children.values()):totals['overlap_publications']+=1
                    if op=='reclaim' and any(c['role']=='reader' and c.get('ticket',{}).get('generation')==2 and not c.get('wait') for c in children.values()):totals['reclaimed_with_current_reader']+=1
                else:need(ns==s,'unannounced canonical mutation')
                removed={p for p in files if p.startswith('store/g1/') and p not in nf}
                if removed:need(s['selected']==2 and s['generations']['1']['status'] in ('retiring','removed') and not any(p['generation']==1 for p in s['pins'].values()),'physical removal without retiring unpinned generation')
                for pin in s['pins'].values():need(content_reason(nf,pin,s['unit']) is None,'live pin bytes changed')
                if s['selected']==2:need(content_reason(nf,dict(generation=2,**{k:s['generations']['2'][k] for k in ('directory','manifest_sha256')}),s['unit']) is None,'selected generation bytes changed')
                files=nf
            elif kind=='spawn':
                cid=e['child'];need(cid not in children and type(e['pid'])is int and e['pid']>0,'child identity');need(not any(c['pid']==e['pid'] and not c.get('wait') for c in children.values()),'live PID reuse');need(sum(not c.get('wait') for c in children.values())<5,'child capacity');c=dict(e);children[cid]=c;all_ids.append(cid);totals['helpers']+=1
                command=e['command'];need(command[:4]==[sys.executable,'-X','utf8','-B'],'helper runtime');need(pathlib.Path(command[4]).resolve()==pathlib.Path(__file__).resolve().parent/('authority.py' if e['role']=='authority' else 'actor.py'),'helper source');need(command[command.index('--root')+1]==str(case/'fixture'),'helper fixture')
                if e['role']!='authority':
                    need(command[5]==e['role'] and e['role'] in ('writer','reader'),'actor role');p=pathlib.Path(command[command.index('--ticket')+1]);need(p.resolve().is_relative_to(case.resolve()),'ticket path');t=load(p);c['ticket']=t;need(t['actor_nonce'] not in all_nonces,'actor nonce reuse');all_nonces.add(t['actor_nonce'])
                    if e['role']=='reader':need(s['pins'].get(t['pin'])==t,'actor launch without durable pin')
                    else:need(t==dict(s['writer'],unit=s['unit']),'actor launch without publisher permit')
            elif kind=='send':
                c=children[e['child']];need(not c.get('wait'),'send after wait');v=e['value']
                if isinstance(v,dict) and v['op']!='exit':
                    need(c.get('lock')==0 and c['role']=='authority','request outside authority');requests[e['child']]=dict(request=v,state=copy.deepcopy(s),files=files.copy(),reason=reason(s,v,files))
            elif kind=='receive':
                c=children[e['child']];need(not c.get('wait'),'receive after wait');v=e['value']
                if 'pid' in v:need(v['pid']==c['pid'],'receipt PID binding')
                if v.get('lock_acquired'):
                    offset=v['offset'];need(not any(x.get('lock')==offset and not x.get('wait') for x in children.values()),'overlapping same-range authority');need(offset in (0,1) and (offset==0 or '--lock-only' in c['command']),'lock route');need(v['attempts']==len(v['errors'])+1 and all(err['errno']==13 for err in v['errors']),'lock retry classification');c['lock']=offset
                if v.get('status')=='lock-refused':need(c['role']=='authority' and any(x.get('lock')==0 and not x.get('wait') for x in children.values()) and v['errors'] and all(x['errno']==13 for x in v['errors']),'lock contention evidence');c['refused']=True
                if 'phase' in v:pending_phase=e['child']+'/'+v['phase'];c['phase']=v['phase']
                if v.get('ready'):need(v['state']==s and c.get('lock')==0,'ready state')
                if 'ticket' in v:need(v['ticket']==c.get('ticket'),'actor ticket receipt')
                if 'response' in v:
                    q=requests[e['child']];r=q['request'];reply=v['response'];need(v['request_id']==r['request_id'],'request reply identity')
                    if q['reason'] is not None:need(reply==dict(status='refused',reason=q['reason']) and s==q['state'],'refusal mutation/reason')
                    else:
                        op=r['op'];busy=op=='publish' and q['state']['policy']=='drain-before-publish' and bool(q['state']['pins']);need(reply['status']==('busy' if busy else 'ok'),'admitted reply status')
                        if 'state' in reply:need(reply['state']==s,'reply canonical state')
                        if op=='claim':need(reply['writer']==s['writer'] and s!=q['state'],'claim reply before commit')
                        if op in ('pin','validate_pin'):need(reply['pin']==s['pins'].get(reply['pin']['pin']),'pin reply before commit')
                        if op=='publish' and not busy:need(s['selected']==2 and s['revision']==1,'publication reply before commit')
                        if op=='release_pin':need(r['pin']['pin'] not in s['pins'],'release reply before commit')
                if 'observation' in v:
                    t=c['ticket'];o=v['observation'];need(c['role']=='reader' and s['pins'].get(t['pin'])==t,'read without durable rights');need(content_reason(files,t,s['unit']) is None,'read byte profile');g=t['generation'];sn=1 if g==1 else 2
                    expected_o=dict(generation=g,unit=s['unit'],directory=t['directory'],files={n:sha(b) for n,b in artifacts(g,s['unit']).items()},snapshot_event_cursor=sn,snapshot_byte_cursor=1 if g==1 else 3,snapshot_state_base64=base64.b64encode(b'A' if g==1 else b'A\xc3\xa9').decode(),retained_event_ids=[1,2,3] if g==1 else [3]);need(o==expected_o,'independent reader reconstruction');c['observation']=o;totals['completed_reads']+=1
            elif kind=='wait':
                c=children[e['child']];need(not c.get('wait') and e['pid']==c['pid'],'unique owned wait');need(type(e['killed'])is bool and type(e['exit_code'])is int,'wait shape');need(e['exit_code']!=0 if e['killed'] else e['exit_code']==(3 if c.get('refused') else 0),'wait outcome');c['wait']=e;totals['killed_helpers']+=int(e['killed'])
                if c['role']=='reader' and not e['killed']:need(c.get('observation'),'reader success without observation')
            elif kind=='assertion':need(e['actual']==e['expected'],'failed journal assertion');checks.append(dict(name=e['name'],value=e['actual']))
            elif kind=='lifetime-refusal':need(e['actor'] in children and not children[e['actor']].get('wait') and children[e['actor']]['ticket']==e['pin'],'lifetime refusal provenance')
            elif kind=='reader-admission-refusal':need(s['pins'].get(e['pin']['pin'])!=e['pin'],'reader refusal provenance')
            else:need(kind in ('injected-stage-fault','restored-stage-fault'),'unknown trace event')
        cuts={'pin_staged_loss':'pin:staged','pin_reply_loss':'pin:committed','publish_staged_loss':'publish:staged','publish_reply_loss':'publish:committed','retire_intent_loss':'retire:committed','retire_partial_loss':'reclaim:first_deleted'}
        if row['schedule'] in cuts:
            phase=cuts[row['schedule']];hits=[i for i,e in enumerate(events) if e['kind']=='receive' and e['value'].get('phase')==phase]
            need(any(i+2<len(events) and events[i+1]['kind']=='snapshot' and events[i+2]['kind']=='wait' and events[i+2]['child']==events[i]['child'] and events[i+2]['killed'] is True for i in hits),'named cut termination ordering')
        need(not pending_phase and all(c.get('wait') for c in children.values()),'unwaited helper or missing snapshot');need(checks==row['checks'] and s['selected']==row['final_selected'] and s['generations']['1']['status']==row['final_old_status'],'derived row')
        actual={p.relative_to(case/'fixture').as_posix():sha(p.read_bytes()) for p in (case/'fixture').rglob('*') if p.is_file() and p.name!='authority.lock'};need(actual==files,'final filesystem observation')
    need(sorted(int(c[5:]) for c in all_ids)==list(range(1,len(all_ids)+1)) and len(set(snapids))==len(snapids),'global receipt identity');need(totals['helpers']==result['helper_process_count'] and result['all_helpers_waited'] is True,'helper summary');need(totals['overlap_publications']>0 and totals['reclaimed_with_current_reader']==8,'required physical overlaps')
    return totals

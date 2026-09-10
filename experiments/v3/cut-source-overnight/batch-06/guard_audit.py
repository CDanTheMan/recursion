"""Adapter guard audit, transcribed from frozen S direct-byte relation.
Does not import implementation reducers or their guard functions.
"""
import json,hashlib
import s_domain as d

def encoded(value): return json.dumps(value,sort_keys=True,separators=(',',':'))

def expected(s,a,p):
    k=a.partition('@')[0]; patch={}; reason='ok'; delegate=False
    pub = k in ('pub-commit','pub-rival','pub-retry','pub-retry-conflict','pub-retry-foreign')
    request = d.q.incoming(s,k)[0].request if pub and (s['staged'] or s['publication_receipts']) else None
    duplicate_id = request in {r[0].request for r in s['publication_receipts']}
    if k.startswith('register:'):
        f=d.q.lit.fixture(k.partition(':')[2]); header=f['original']['cut']['trace_header']
        value=encoded([header['intent'],header['admission'],f['binding']['body']['reservation']])
        expected_fields=set(d.q.lit.fixture('success')['original']['cut']['trace_header']['intent'])
        if set(header['intent'])!=expected_fields: reason='incomplete-registration'
        elif s['remote']==0 or f['binding']['body']['reservation']!=list(s['bindings'][0]): reason='foreign-registration'
        elif s['registration'] and s['registration']!=value: reason='registration-conflict'
        elif not s['registration']: patch={'registration':value,'source_revision':s['source_revision']+1}
    elif k.startswith(('attempt:','atomic:')):
        atomic=k.startswith('atomic:')
        if atomic:
            _,name,offset=k.split(':'); offset=int(offset); record=d.q.lit.fixture(name)['original']['records'][offset]; number=record['attempt_number']
        else: number=int(k.partition(':')[2])
        pair=('attemptA' if number==1 else 'retained-attemptA'+str(number),'attempt:'+str(number))
        if not s['registration']: reason='no-registration'
        elif s['paused']: reason='E-PAUSED'
        elif pair in s['attempts']: reason='duplicate-attempt'
        elif number!=len(s['attempts'])+1: reason='attempt-gap'
        elif atomic and (p['policy']!='atomic-start' or offset!=len(s['append_log'])): reason='atomic-position'
        elif atomic and (record['type']!='AttemptStarted@1' or record['attempt_id']!=pair[1] or any(record[f]!=json.loads(s['registration'])[0][f] for f in ('effect_id','idempotency_key','payload_digest','target_ref','admission_epoch','fence_epoch'))): reason='invalid-atomic-start'
        else:
            patch.update(attempts=s['attempts']+(pair,),source_revision=s['source_revision']+1)
            if atomic: patch['append_log']=s['append_log']+(encoded(record),)
    elif k.startswith('append:'):
        # Independently decode the offered record and mutations; do not call append_request.
        _,name,index,variant=k.split(':'); index=int(index)
        record=dict(d.q.lit.fixture(name)['original']['records'][index]); request='append-'+str(index)
        caller='collectorB' if variant=='foreign' else 'collectorA'
        incarnation=('cut-source','collectorA','effectA',1 if variant=='new-boot' else 0)
        if variant=='wrong-attempt': record['attempt_id']='attempt:foreign'
        if variant=='wrong-body': record['payload_digest']='sha256:'+'9'*64
        if variant=='fresh': request+='-fresh'
        raw=encoded(record); body=(caller,incarnation,index,raw)
        rows=[r for r in s['append_receipts'] if r[0]==request]
        if caller!='collectorA': reason='wrong-append-owner'
        elif rows:
            if rows[0][1]!=body: reason='append-id-conflict'
            else: reason='duplicate'; patch['append_reply']=rows[0][2]
        elif incarnation!=s['source_generation']: reason='stale-append-incarnation'
        elif s['paused']: reason='E-PAUSED'
        elif not s['registration']: reason='no-registration'
        elif index!=len(s['append_log']): reason='append-gap-or-fork'
        elif all(pair[1]!=record['attempt_id'] for pair in s['attempts']): reason='unregistered-attempt'
        elif any(record[field]!=json.loads(s['registration'])[0][field] for field in ('effect_id','idempotency_key','payload_digest','target_ref','admission_epoch','fence_epoch')): reason='foreign-record-scope'
        else:
            revision=s['source_revision']+1; receipt=(request,revision,index,hashlib.sha256(encoded(raw).encode()).hexdigest())
            patch.update(append_log=s['append_log']+(raw,),source_revision=revision,append_receipts=s['append_receipts']+((request,body,receipt),),append_reply=receipt)
    elif k=='append-lose-reply': patch['append_reply']=()
    elif k=='collect-open':
        if not s['registration']: reason='no-registration'
        else: patch.update(collection=(s['source_generation'],s['source_revision'],s['registration'],s['attempts'],len(s['append_log'])),collected=())
    elif k.startswith('collect:'):
        index=int(k[8:])
        if not s['collection'] or not 0<=index<min(s['collection'][4],len(s['append_log'])): reason='outside-captured-cut'
        elif index in [x[0] for x in s['collected']]: reason='duplicate-collection'
        else: patch['collected']=tuple(sorted(s['collected']+((index,s['append_log'][index]),)))
    elif k=='source-attest':
        c=s['collection']; name=s['cut_delivery']
        if not c or not name: reason='no-captured-source'
        else:
            f=d.q.lit.fixture(name); original=f['original']; header=original['cut']['trace_header']
            expected=tuple((i,encoded(record)) for i,record in enumerate(original['records']))
            registry=encoded((header['intent'],header['admission'],f['binding']['body']['reservation']))
            attempt_map=tuple(tuple(pair) for pair in f['binding']['body']['attempt_mapping'])
            if c[0]!=s['source_generation'] or c[1]!=s['source_revision']: reason='stale-collection'
            elif len(expected)!=c[4] or s['collected']!=expected: reason='incomplete-inventory'
            elif c[2]!=registry or c[3]!=attempt_map: reason='incomplete-registry'
            else:
                patch['attestation']=(c[0],c[1],name); delegate=True
    elif k.startswith('source:'): reason='registered-protocol-required'
    elif pub and not duplicate_id and (s['attestation']==() or s['attestation'][:2]!=(s['source_generation'],s['source_revision']) or s['staged_source']!=s['attestation']): reason='source-boundary-stale'
    elif k=='reconcile' and (s['selected_source']==() or s['selected_source'][:2]!=(s['source_generation'],s['source_revision'])): reason='source-boundary-stale'
    else: delegate=True
    return {key:patch.get(key,s[key]) for key in d.EXTRA}, k+':'+reason, delegate

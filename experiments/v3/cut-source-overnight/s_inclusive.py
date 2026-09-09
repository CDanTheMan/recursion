"""Inclusive registered source authority. Delegates only unchanged publication actions."""
import copy
import json
import s_domain as d
import q_inclusive as old

def step(s, a, p, u, outcome, mutant=None):
    k = a.split('@')[0]
    n = copy.deepcopy(s)
    n.update(done=s['done'] | (1 << p['actions'].index(a)), decision=k+':ok')
    publication = k in ('pub-commit','pub-rival','pub-retry','pub-retry-conflict','pub-retry-foreign')
    retained = publication and bool(s['staged'] or s['publication_receipts']) and any(row[0].request == d.q.incoming(s,k)[0].request for row in s['publication_receipts'])
    def deny(reason): n['decision'] = k+':'+reason
    if k.startswith('register:'):
        name = k.split(':')[1]; raw = d.registration(name)
        required = set(d.q.lit.fixture('success')['original']['cut']['trace_header']['intent'])
        if set(json.loads(raw)[0]) != required and mutant != 'registration-complete': deny('incomplete-registration')
        elif not s['remote'] or tuple(json.loads(raw)[2]) != s['bindings'][0]: deny('foreign-registration')
        elif s['registration'] and s['registration'] != raw: deny('registration-conflict')
        elif not s['registration']: n.update(registration=raw, source_revision=s['source_revision']+1)
    elif k.startswith('attempt:') or k.startswith('atomic:'):
        atomic = k.startswith('atomic:')
        if atomic:
            _, name, index = k.split(':'); raw = d.records(name)[int(index)]; record = json.loads(raw); number = record['attempt_number']
        else: number = int(k.split(':')[1])
        pair = ('attemptA' if number == 1 else 'retained-attemptA'+str(number), 'attempt:'+str(number))
        if not s['registration']: deny('no-registration')
        elif s['paused']: deny('E-PAUSED')
        elif pair in s['attempts']: deny('duplicate-attempt')
        elif number != len(s['attempts'])+1: deny('attempt-gap')
        elif atomic and (p['policy'] != 'atomic-start' or int(index) != len(s['append_log'])): deny('atomic-position')
        elif atomic and (record['type'] != 'AttemptStarted@1' or record['attempt_id'] != pair[1] or any(record[field] != json.loads(s['registration'])[0][field] for field in ('effect_id','idempotency_key','payload_digest','target_ref','admission_epoch','fence_epoch'))) and mutant != 'atomic-start-record': deny('invalid-atomic-start')
        else:
            n.update(attempts=s['attempts']+(pair,), source_revision=s['source_revision']+1)
            if atomic: n['append_log'] = s['append_log']+(raw,)
    elif k.startswith('append:'):
        request, caller, boot, index, raw = d.append_request(k)
        body = (caller, boot, index, raw); existing = next((r for r in s['append_receipts'] if r[0] == request), None)
        record = json.loads(raw)
        if caller != 'collectorA' and mutant != 'append-owner': deny('wrong-append-owner')
        elif existing:
            if existing[1] != body and mutant != 'append-conflict': deny('append-id-conflict')
            else: n['append_reply'] = existing[2]; deny('duplicate')
        elif boot != s['source_generation'] and mutant != 'append-incarnation': deny('stale-append-incarnation')
        elif s['paused'] and mutant != 'append-pause': deny('E-PAUSED')
        elif not s['registration']: deny('no-registration')
        elif index != len(s['append_log']) and mutant != 'append-position': deny('append-gap-or-fork')
        elif record['attempt_id'] not in dict(s['attempts']).values() and mutant != 'append-attempt': deny('unregistered-attempt')
        elif any(record[f] != json.loads(s['registration'])[0][f] for f in ('effect_id','idempotency_key','payload_digest','target_ref','admission_epoch','fence_epoch')) and mutant != 'append-scope': deny('foreign-record-scope')
        else:
            revision=s['source_revision']+1; receipt=(request,revision,index,d.q.digest(raw))
            n.update(append_log=s['append_log']+(raw,),source_revision=revision,
                     append_receipts=s['append_receipts']+((request,body,receipt),),append_reply=receipt)
    elif k == 'append-lose-reply': n['append_reply'] = ()
    elif k == 'collect-open':
        if not s['registration']: deny('no-registration')
        else: n.update(collection=(s['source_generation'],s['source_revision'],s['registration'],s['attempts'],len(s['append_log'])),collected=())
    elif k.startswith('collect:'):
        index=int(k.split(':')[1])
        if not s['collection'] or (index < 0 and mutant != 'collection-lower-bound') or index >= s['collection'][4] or index >= len(s['append_log']): deny('outside-captured-cut')
        elif any(i == index for i,raw in s['collected']): deny('duplicate-collection')
        else: n['collected'] = tuple(sorted(s['collected']+((index,s['append_log'][index]),)))
    elif k == 'source-attest':
        name=s['cut_delivery']; capture=s['collection']; expected=d.records(name) if name else ()
        if not capture or not name: deny('no-captured-source')
        elif (capture[0] != s['source_generation'] or capture[1] != s['source_revision']) and mutant != 'capture-current': deny('stale-collection')
        elif (tuple(i for i,raw in s['collected']) != tuple(range(capture[4])) or tuple(raw for i,raw in s['collected']) != expected) and mutant != 'complete-collection': deny('incomplete-inventory')
        elif (capture[2] != d.registration(name) or capture[3] != d.mapping(name)) and mutant != 'complete-registry': deny('incomplete-registry')
        else: n.update(attestation=(capture[0],capture[1],name),source_name=name,source_head=d.q.head(name),source_version=max(s['source_version'],d.q.lit.fixture(name)['binding']['body']['source_version']))
    elif k.startswith('source:'): deny('registered-protocol-required')
    elif publication and not retained and (not s['attestation'] or s['attestation'][:2] != (s['source_generation'],s['source_revision']) or s['staged_source'] != s['attestation']) and mutant != 'publication-source-current': deny('source-boundary-stale')
    elif k == 'reconcile' and (not s['selected_source'] or s['selected_source'][:2] != (s['source_generation'],s['source_revision'])) and mutant != 'reconcile-source-current': deny('source-boundary-stale')
    else:
        n.update(old.step(d.project(s),a,p,u,outcome))
        if k == 'stage' or k.startswith('stage-'): n['staged_source'] = s['attestation']
        if n['publication_revision'] > s['publication_revision']: n['selected_source'] = s['staged_source']
    return n

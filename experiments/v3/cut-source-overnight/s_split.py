"""Separated authority, transport and presentation implementation."""
import copy
import json
import s_domain as d
import q_split as old

def step(state, action, profile, unit, outcome):
    authority, flow, view = copy.deepcopy(state)
    s = d.flatten(state)
    verb = action.partition('@')[0]
    why = 'ok'
    delegate = False
    if verb.startswith('register:'):
        value = d.registration(verb[9:])
        if s['remote'] == 0 or json.loads(value)[2] != list(s['bindings'][0]): why = 'foreign-registration'
        elif s['registration'] not in ('', value): why = 'registration-conflict'
        elif s['registration'] == '': authority.update(registration=value, source_revision=s['source_revision']+1)
    elif verb.startswith(('attempt:', 'atomic:')):
        immediate = verb.startswith('atomic:')
        if immediate:
            _, name, offset = verb.split(':'); offset = int(offset)
            payload = d.records(name)[offset]; number = json.loads(payload)['attempt_number']
        else: number = int(verb[8:])
        identity = ('attemptA' if number == 1 else 'retained-attemptA'+str(number), 'attempt:'+str(number))
        checks = [(bool(s['registration']), 'no-registration'), (not s['paused'], 'E-PAUSED'),
                  (identity not in s['attempts'], 'duplicate-attempt'), (number == len(s['attempts'])+1, 'attempt-gap')]
        if immediate: checks.append((profile['policy']=='atomic-start' and offset==len(s['append_log']), 'atomic-position'))
        why = next((reason for ok, reason in checks if not ok), 'ok')
        if why == 'ok':
            authority['attempts'] = (*s['attempts'], identity)
            authority['source_revision'] = s['source_revision']+1
            if immediate: authority['append_log'] = (*s['append_log'], payload)
    elif verb.startswith('append:'):
        identity, caller, incarnation, ordinal, payload = d.append_request(verb)
        request_body = (caller, incarnation, ordinal, payload)
        saved = {r[0]:r for r in s['append_receipts']}.get(identity)
        if caller != 'collectorA': why = 'wrong-append-owner'
        elif saved is not None:
            if saved[1] != request_body: why = 'append-id-conflict'
            else: why = 'duplicate'; authority['append_reply'] = saved[2]
        elif incarnation != s['source_generation']: why = 'stale-append-incarnation'
        elif s['paused']: why = 'E-PAUSED'
        elif s['registration'] == '': why = 'no-registration'
        elif ordinal != len(s['append_log']): why = 'append-gap-or-fork'
        elif json.loads(payload)['attempt_id'] not in [r[1] for r in s['attempts']]: why = 'unregistered-attempt'
        else:
            original = json.loads(s['registration'])[0]; record = json.loads(payload)
            keys = ('effect_id','idempotency_key','payload_digest','target_ref','admission_epoch','fence_epoch')
            if {k:record[k] for k in keys} != {k:original[k] for k in keys}: why = 'foreign-record-scope'
            else:
                revision = s['source_revision']+1
                reply = (identity,revision,ordinal,d.q.digest(payload))
                authority.update(append_log=(*s['append_log'],payload),source_revision=revision,
                                 append_receipts=(*s['append_receipts'],(identity,request_body,reply)),append_reply=reply)
    elif verb == 'append-lose-reply': authority['append_reply'] = ()
    elif verb == 'collect-open':
        if s['registration'] == '': why = 'no-registration'
        else:
            authority['collection'] = (s['source_generation'],s['source_revision'],s['registration'],s['attempts'],len(s['append_log']))
            authority['collected'] = ()
    elif verb.startswith('collect:'):
        ordinal = int(verb[8:])
        if not s['collection'] or ordinal >= s['collection'][4] or ordinal >= len(s['append_log']): why = 'outside-captured-cut'
        elif ordinal in dict(s['collected']): why = 'duplicate-collection'
        else: authority['collected'] = tuple(sorted((*s['collected'],(ordinal,s['append_log'][ordinal]))))
    elif verb == 'source-attest':
        captured = s['collection']; cut = s['cut_delivery']
        if not captured or not cut: why = 'no-captured-source'
        elif captured[:2] != (s['source_generation'],s['source_revision']): why = 'stale-collection'
        elif [i for i,v in s['collected']] != list(range(captured[4])) or tuple(v for i,v in s['collected']) != d.records(cut): why = 'incomplete-inventory'
        elif captured[2:] != (d.registration(cut),d.mapping(cut),captured[4]): why = 'incomplete-registry'
        else: authority.update(attestation=(*captured[:2],cut),source_name=cut,source_head=d.q.head(cut),source_version=max(s['source_version'],d.q.lit.fixture(cut)['binding']['body']['source_version']))
    elif verb.startswith('source:'): why = 'registered-protocol-required'
    elif verb in ('pub-commit','pub-rival'):
        valid = bool(s['attestation']) and s['attestation'][:2] == (s['source_generation'],s['source_revision']) and s['staged_source'] == s['attestation']
        if not valid: why = 'source-boundary-stale'
        else: delegate = True
    elif verb == 'reconcile':
        if not s['selected_source'] or s['selected_source'][:2] != (s['source_generation'],s['source_revision']): why = 'source-boundary-stale'
        else: delegate = True
    else: delegate = True
    if delegate:
        baseline = d.q.split(d.project(d.flatten(state)))
        next_state = old.step(baseline,action,profile,unit,outcome)
        authority.update(next_state.authority); flow.update(next_state.flow); view.update(next_state.view)
        if verb == 'stage' or verb.startswith('stage-'): authority['staged_source'] = s['attestation']
        if authority['publication_revision'] > s['publication_revision']: authority['selected_source'] = s['staged_source']
    else:
        view.update(done=s['done'] | (1 << profile['actions'].index(action)),decision=verb+':'+why)
    return d.q.Split(authority,flow,view)

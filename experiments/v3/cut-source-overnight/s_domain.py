"""Immutable input encodings and finite schedules; no transition predicates."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-publication'))
import q_domain as q
from q_domain import canonical, require, UNITS, OUTCOMES, sequence, ready_actions

EXTRA = ('registration', 'attempts', 'append_log', 'append_receipts', 'append_reply',
         'source_revision', 'collection', 'collected', 'attestation', 'staged_source', 'selected_source')
DEFAULTS = dict(registration='', attempts=(), append_log=(), append_receipts=(), append_reply=(),
                source_revision=0, collection=(), collected=(), attestation=(), staged_source=(), selected_source=())
AUTH = q.AUTH + EXTRA
FLOW, VIEW = q.FLOW, q.VIEW
PROFILES = {}

def initial(unit):
    return dict(q.initial(unit), **copy.deepcopy(DEFAULTS))

def project(state):
    return {k: state[k] for k in q.AUTH + q.FLOW + q.VIEW}

def split(state):
    return q.Split(*({k: state[k] for k in names} for names in (AUTH, FLOW, VIEW)))

def flatten(state):
    return dict(**state.authority, **state.flow, **state.view)

def registration(name):
    f = q.lit.fixture(name)
    return canonical((f['original']['cut']['trace_header']['intent'],
                      f['original']['cut']['trace_header']['admission'], f['binding']['body']['reservation']))

def records(name):
    return tuple(canonical(r) for r in q.lit.fixture(name)['original']['records'])

def mapping(name):
    return tuple(tuple(r) for r in q.lit.fixture(name)['binding']['body']['attempt_mapping'])

def append_request(action):
    # Explicit request identity, full bytes, position and typed source incarnation.
    _, name, index, variant = action.split(':')
    index = int(index)
    raw = records(name)[index]
    request = 'append-' + str(index)
    boot = ('cut-source', 'collectorA', 'effectA', 0)
    caller = 'collectorA'
    if variant == 'foreign': caller = 'collectorB'
    if variant == 'wrong-attempt':
        body = json.loads(raw); body['attempt_id'] = 'attempt:foreign'; raw = canonical(body)
    if variant == 'wrong-body':
        body = json.loads(raw); body['payload_digest'] = 'sha256:' + '9' * 64; raw = canonical(body)
    if variant == 'fresh': request += '-fresh'
    if variant == 'new-boot': boot = boot[:-1] + (1,)
    return request, caller, boot, index, raw

def append(name, index, variant='normal'):
    return 'append:' + name + ':' + str(index) + ':' + variant

def setup(name, policy='pending'):
    steps = list(q.SETUP) + ['register:' + name]
    for i, raw in enumerate(records(name)):
        r = json.loads(raw)
        if r['type'] == 'AttemptStarted@1':
            steps.append(('atomic:' + name + ':' + str(i)) if policy == 'atomic-start' else 'attempt:' + str(r['attempt_number']))
            if policy == 'atomic-start': continue
        steps.append(append(name, i))
    return steps

def collect(name, omit=(), reverse=False):
    indexes = list(range(len(records(name))))
    if reverse: indexes.reverse()
    return ['collect-open'] + ['collect:' + str(i) for i in indexes if i not in omit] + q.deliver(name) + ['source-attest']

def publish(name):
    return collect(name) + ['stage', 'pub-commit']

def add(name, steps, core=(), outcomes=OUTCOMES, policy='pending', queue='source_authority'):
    p = sequence(steps, core); p.update(outcomes=outcomes, policy=policy, queue=queue)
    PROFILES[name] = p

for policy in ('pending', 'atomic-start'):
    for name, outcome in (('success', 1), ('failure', 2), ('later-start-only', 1), ('ambiguous', 1)):
        add(policy + '-' + name, setup(name, policy) + publish(name) + q.reader() + ['reconcile', 'admitB'], outcomes=(outcome,), policy=policy)
add('omitted-record', setup('success') + collect('success', (1,)) + ['stage','pub-commit'], outcomes=(1,))
add('omitted-tail-current-head', setup('success') + collect('success', (2,)) + ['stage','pub-commit'], outcomes=(1,))
add('reverse-collection', setup('success') + collect('success', reverse=True) + ['stage','pub-commit'], outcomes=(1,))
add('delayed-record', setup('success') + collect('success',(1,)) + ['collect:1','source-attest','stage','pub-commit'], outcomes=(1,))
add('pending-attempt-before-collect', setup('success') + ['attempt:2'] + publish('success') + ['admitB'], outcomes=(1,))
add('new-attempt-during-collection', setup('success') + ['collect-open','collect:0','attempt:2','collect:1','collect:2'] + q.deliver('success') + ['source-attest','stage','pub-commit'], outcomes=(1,))
add('append-between-collect-and-publish', setup('success') + collect('success') + ['stage','attempt:2',append('later-start-only',3),'pub-commit'], outcomes=(1,))
add('pending-after-selected', setup('failure') + publish('failure') + q.reader() + ['attempt:2','reconcile','admitB'], outcomes=(2,), queue='coupled_adversarial')
add('append-after-selected', setup('success') + publish('success') + q.reader() + ['attempt:2',append('later-start-only',3),'reconcile','admitB'], outcomes=(1,), queue='coupled_adversarial')
add('same-version-real-append', setup('late-receipt') + publish('late-receipt') + ['attempt:2',append('later-start-only',3)] + publish('later-start-only') + q.reader() + ['reconcile','admitB'], outcomes=(1,), queue='coupled_adversarial')
add('equal-position-fork', setup('later-start-only') + [append('conflict',3)], outcomes=(1,))
add('foreign-registration', list(q.SETUP) + ['register:foreign','attempt:1',append('success',0)] + publish('foreign'))
for variant in ('foreign','wrong-attempt','wrong-body'):
    add('append-' + variant, list(q.SETUP)+['register:success','attempt:1',append('success',0,variant)], outcomes=(1,))
add('unregistered-append', list(q.SETUP)+['register:success',append('success',0)], outcomes=(1,))
add('append-gap', list(q.SETUP)+['register:success','attempt:1',append('success',1)], outcomes=(1,))
add('append-duplicate-lost-reply', setup('success') + ['append-lose-reply','source-restart',append('success',2),append('success',2)], outcomes=(1,))
add('append-fresh-old-boot', setup('ambiguous') + ['source-restart',append('success',2,'fresh')], outcomes=(1,))
add('collection-old-incarnation', setup('success') + collect('success') + ['source-restart','stage','pub-commit'], outcomes=(1,))
add('restart-recollect', setup('success') + collect('success') + ['source-restart'] + publish('success'), outcomes=(1,))
add('source-oracle-bypass', list(q.SETUP)+q.deliver('success')+['source:success','stage','pub-commit'], outcomes=(1,))
add('source-collection-race', setup('success'), ('collect-open','collect:0','collect:1','collect:2','attempt:2','source-restart'), outcomes=(1,))
add('pause-append', setup('ambiguous') + ['pause',append('success',2)] + publish('success'), outcomes=(1,), queue='coupled_adversarial')
add('pause-publication', setup('failure') + collect('failure') + ['stage','pause','pub-commit'], outcomes=(2,), queue='coupled_adversarial')
add('quota-worker-independent', setup('failure') + publish('failure') + q.reader() + ['quota','restart','replay','duplicateA','admitB','reconcile','admitB'], outcomes=(2,), queue='coupled_adversarial')
add('publication-duplicate-retired', setup('success') + publish('success') + ['reader-request:0','reader-pin:0','reader-copy:0','attempt:2',append('later-start-only',3)] + publish('later-start-only') + ['reader-wait:0','reader-release:0','reclaim','source-restart','authority-restart','publisher-revoke','pub-retry','pub-retry-conflict'], outcomes=(1,), queue='coupled_adversarial')
add('copy-not-wait', setup('success') + publish('success') + ['reader-request:0','reader-pin:0','reader-copy:0','attempt:2',append('later-start-only',3)] + publish('later-start-only') + ['reader-release:0','reclaim','reader-wait:0','reader-release:0','reclaim','reader-install:0','join-cut','classify','reconcile','admitB'], outcomes=(1,), queue='coupled_adversarial')
add('publication-source-race', setup('success') + collect('success') + ['stage'], ('pub-commit','attempt:2',append('later-start-only',3),'source-restart','pause','quota'), outcomes=(1,), queue='coupled_adversarial')
# Preserve full inherited literal event and typed consultation prefixes; install source at classification.
for label, prefix in [('four-event', q.base.base.PROFILES['four-literal-events']['actions']), ('typed-consultation', q.base.base.PROFILES['transported-stale-advice']['actions'])]:
    steps = []
    for action in prefix:
        k = action.split('@')[0]
        if k == 'classify': steps += setup('success')[6:] + publish('success') + q.reader()
        else: steps.append(k)
    if label == 'typed-consultation': steps += ['query'] + setup('success')[6:] + publish('success') + q.reader()
    add(label, steps + ['reconcile','admitB'], outcomes=(1,), queue='coupled_adversarial')


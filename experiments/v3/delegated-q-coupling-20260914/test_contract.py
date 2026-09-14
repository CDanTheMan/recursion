"""Inert contract controls. No inherited scientific module may be imported."""
import copy
import hashlib
import hmac
import importlib.abc
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import NamedTuple

import audit
import check
import relation


class BlockInherited(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition('.')[0] in {'identity', 'identity_audit', 'adapter_traces',
                's_domain', 's_inclusive', 's_split', 's_audit', 'q_domain', 'q_inclusive',
                'q_split', 'q_audit', 'a_domain', 'a_inclusive', 'a_split', 'a_audit',
                'semantic', 'p_domain', 'c_domain'}:
            raise ValueError('inherited scientific import forbidden in fake gate: ' + fullname)
        return None


class Envelope(NamedTuple):
    request: str
    source_generation: tuple
    content: str
    signature: str


KEY = b'public-inert-certificate-fixture-only'
PAYLOAD = '{"fixture":"inert","records":["literal-original"]}'
BINDING = dict(candidate='a' * 40, task_base=check.BASE, plan_sha256='b' * 64,
               source_digest='c' * 64, source_files=1632)
ACTIONS = ('attempt:2@0', 'source-restart@1', 'source-attest@2', 'stage@3', 'pub-commit@4')
PROFILE = dict(actions=ACTIONS, requires={a: () if i == 0 else (ACTIONS[i - 1],) for i, a in enumerate(ACTIONS)},
               outcomes=(1,), policy='pending', queue='inert-only')
ENTRY = dict(id='inert-restart-refusal/event/1', unit='event', actions=list(ACTIONS))


def signed_fixture():
    body = ('fixture-publication-1', ('cut-source', 'collectorA', 'effectA', 1), hashlib.sha256(PAYLOAD.encode()).hexdigest())
    mac = hmac.new(KEY, json.dumps(body, separators=(',', ':')).encode(), hashlib.sha256).hexdigest()
    return Envelope(*body, mac), PAYLOAD


class FakeKernel:
    """Tiny literal fixture protocol, not an implementation of S/Q semantics."""
    Envelope = Envelope

    def __init__(self):
        inventory = check.field_inventory()
        self.fields, self.journal = inventory['common'], inventory['journal']

    def initial(self, unit):
        core = dict.fromkeys(self.fields, ())
        core.update(done=0, decision='initial', source_name='',
                    source_generation=('cut-source', 'collectorA', 'effectA', 0), stage_serial=0, publisher_boot=1)
        ledger = dict.fromkeys(self.journal, ())
        ledger.update(source_generation=core['source_generation'], source_revision=0)
        return dict(core, **ledger), dict(core=core, journal=ledger, done=0, decision='initial', invocations=())

    def initial_audit(self, source, adapter, unit):
        # Independent initial expectations, checking even fields unused by the toy actions.
        for state in (source, adapter['core']):
            for key in self.fields:
                expected = {'source_name': '', 'source_generation': ('cut-source', 'collectorA', 'effectA', 0), 'stage_serial': 0, 'publisher_boot': 1}.get(key, ())
                audit.demand(audit.same(state[key], expected), 'inert initial common field ' + key)
            audit.demand(state['done'] == 0 and state['decision'] == 'initial', 'initial bookkeeping')
        for key in self.journal:
            expected = 0 if key == 'source_revision' else ('cut-source', 'collectorA', 'effectA', 0) if key == 'source_generation' else ()
            audit.demand(audit.same(source[key], expected) and audit.same(adapter['journal'][key], expected), 'inert initial journal')
        audit.demand(adapter['done'] == 0 and adapter['decision'] == 'initial' and adapter['invocations'] == (), 'inert adapter initialization')

    def step(self, source, adapter, action, profile, unit, outcome):
        ns, na = copy.deepcopy(source), copy.deepcopy(adapter)
        verb = action.partition('@')[0]
        ns['done'] |= 1 << profile['actions'].index(action)
        na['done'] = ns['done']
        reasons = {'source-attest': 'stale-collection', 'pub-commit': 'source-boundary-stale'}
        ns['decision'] = na['decision'] = verb + ':' + reasons.get(verb, 'ok')
        if verb == 'attempt:2':
            ns['source_revision'] += 1
            na['journal']['source_revision'] += 1
            ns['attempts'] = na['journal']['attempts'] = (('retained-attemptA2', 'attempt:2'),)
        if verb == 'source-restart':
            token = ('cut-source', 'collectorA', 'effectA', 1)
            ns['source_generation'] = na['journal']['source_generation'] = na['core']['source_generation'] = token
        if verb == 'stage':
            ns['staged'] = na['core']['staged'] = signed_fixture()
            ns['stage_serial'] = na['core']['stage_serial'] = 1
        if verb in ('source-restart', 'stage'):
            potential = profile['actions'][1:]
            na['core']['done'] |= 1 << potential.index(action)
            na['core']['decision'] = na['decision']
            na['invocations'] += (action,)
        return ns, na

    def transition(self, source, adapter, ns, na, action, profile, unit, outcome):
        # Table-driven independent postconditions; does not call step or fixture builder.
        verb = action.partition('@')[0]
        called = verb in ('source-restart', 'stage')
        reason = {'attempt:2': 'attempt:2:ok', 'source-restart': 'source-restart:ok',
                  'source-attest': 'source-attest:stale-collection', 'stage': 'stage:ok',
                  'pub-commit': 'pub-commit:source-boundary-stale'}[verb]
        audit.demand(ns['decision'] == na['decision'] == reason, 'independent refused outer response')
        changed = {'attempt:2': {'attempts', 'source_revision'}, 'source-restart': {'source_generation'},
                   'stage': {'staged', 'stage_serial'}}.get(verb, set())
        for key in (set(self.fields) | set(self.journal)) - changed:
            audit.demand(audit.same(source[key], ns[key]), 'complete source frame ' + key)
        for key in set(self.fields) - changed:
            audit.demand(audit.same(adapter['core'][key], na['core'][key]), 'complete Q frame ' + key)
        for key in set(self.journal) - changed:
            audit.demand(audit.same(adapter['journal'][key], na['journal'][key]), 'complete journal frame ' + key)
        if verb == 'attempt:2':
            audit.demand(ns['source_revision'] == source['source_revision'] + 1 == na['journal']['source_revision'], 'journal revision')
            expected = (('retained-attemptA2', 'attempt:2'),)
            audit.demand(audit.same(ns['attempts'], expected) and audit.same(na['journal']['attempts'], expected), 'typed attempts')
        if verb == 'source-restart':
            expected = ('cut-source', 'collectorA', 'effectA', source['source_generation'][-1] + 1)
            audit.demand(all(audit.same(x, expected) for x in (ns['source_generation'], na['journal']['source_generation'], na['core']['source_generation'])), 'actual live Q generation')
        if verb == 'stage':
            audit.demand(ns['stage_serial'] == na['core']['stage_serial'] == 1, 'stage serial')
            for staged in (ns['staged'], na['core']['staged']):
                self.audit_object(staged)
        audit.demand(na['core']['decision'] == (reason if called else adapter['core']['decision']), 'Q decision on call/noncall')
        return called

    @staticmethod
    def audit_object(staged):
        audit.demand(type(staged) is tuple and len(staged) == 2 and type(staged[0]) is Envelope, 'original tuple and Envelope types')
        envelope, payload = staged
        body = json.dumps([envelope.request, envelope.source_generation, envelope.content], separators=(',', ':')).encode()
        audit.demand(hmac.compare_digest(envelope.signature, hmac.digest(KEY, body, 'sha256').hex()), 'original signature')
        audit.demand(payload == PAYLOAD and envelope.content == hashlib.sha256(payload.encode()).hexdigest(), 'original payload and digest')
        audit.demand(envelope.request == 'fixture-publication-1' and envelope.source_generation == ('cut-source', 'collectorA', 'effectA', 1), 'fixture original object')

    def advance(self, pairs, *args):
        audit.demand(pairs == [], 'no fabricated incarnation pairing')

    def compare(self, case, ss, aa, prefix, pairs):
        source, adapter = ss[prefix], aa[prefix]
        common = [k for k in self.fields if not relation.exact(source[k], adapter['core'][k]) or (k == 'staged' and bool(source[k]))]
        journal = [k for k in self.journal if not relation.exact(source[k], adapter['journal'][k])]
        staged = source['staged']
        origin = None
        if staged and relation.exact(staged, adapter['core']['staged']) and relation.exact(staged, signed_fixture()):
            for i in range(prefix - 1, -1, -1):
                if not relation.exact(ss[i + 1]['staged'], staged) or not relation.exact(aa[i + 1]['core']['staged'], staged):
                    break
                if case['source']['events'][i]['action'] == 'stage@3':
                    origin = dict(case=case['case'], prefix=prefix, event=i,
                                  source=relation.digest(ss[i + 1]), adapter=relation.digest(aa[i + 1]),
                                  source_prefix=relation.digest(case['source']['events'][:prefix]),
                                  adapter_prefix=relation.digest(case['adapter']['events'][:prefix]))
                    break
        accepted = [k for k in common if k != 'staged' or origin is None]
        return dict(strict_related=not (common or journal), related=not (accepted or journal),
                    strict_differing_common_fields=common, differing_common_fields=accepted,
                    differing_journal_fields=journal, identity_proof=origin)

    def audit_row(self, row, case, ss, aa, prefix, pairs):
        left, right = ss[prefix], aa[prefix]
        bad = []
        for key in self.fields:
            l, r = left[key], right['core'][key]
            if not audit.same(l, r) or key == 'staged' and l:
                bad.append(key)
        journal = [key for key in self.journal if not audit.same(left[key], right['journal'][key])]
        proof = None
        candidates = [i for i in range(prefix) if case['source']['events'][i]['action'].partition('@')[0] == 'stage']
        if candidates and left['staged'] and audit.same(left['staged'], right['core']['staged']):
            self.audit_object(left['staged'])
            self.audit_object(right['core']['staged'])
            i = candidates[-1]
            persistent = all(audit.same(ss[j]['staged'], left['staged']) and audit.same(aa[j]['core']['staged'], left['staged']) for j in range(i + 1, prefix + 1))
            if persistent and ss[i + 1]['decision'] == aa[i + 1]['decision'] == 'stage:ok':
                proof = dict(case=case['case'], prefix=prefix, event=i,
                             source=audit.sha(ss[i + 1]), adapter=audit.sha(aa[i + 1]),
                             source_prefix=audit.sha(case['source']['events'][:prefix]),
                             adapter_prefix=audit.sha(case['adapter']['events'][:prefix]))
        extended = [key for key in bad if key != 'staged' or proof is None]
        expected = dict(strict_related=not bad and not journal, related=not extended and not journal,
                        strict_differing_common_fields=bad, differing_common_fields=extended,
                        differing_journal_fields=journal, identity_proof=proof)
        audit.demand(audit.same(row, expected), 'independent complete relation and stage/case proof')

    def response(self, source, adapter, action, pairs):
        return relation.exact(source['decision'], adapter['decision'])

    def audit_response(self, source, adapter, action, pairs):
        return type(source['decision']) is str and source['decision'] == adapter['decision']


def run():
    started = time.monotonic()
    blocker = BlockInherited()
    sys.meta_path.insert(0, blocker)
    controls = []
    attempts = 0
    try:
        kernel = FakeKernel()
        source, adapter = kernel.initial('event')
        ss, aa = [source], [adapter]
        for action in ACTIONS:
            source, adapter = kernel.step(source, adapter, action, PROFILE, 'event', 1)
            ss.append(source)
            aa.append(adapter)
        def make(left=ss, right=aa):
            return relation.certificate(ENTRY['id'], PROFILE, ACTIONS, 'event', 1, left, right, kernel, BINDING)
        def inspect(cert):
            nonlocal attempts
            attempts += 1
            check.require(attempts <= 1024, 'fake certificate reservation')
            return audit.inspect(cert, BINDING, ENTRY, PROFILE, kernel)
        good = make()
        restored = audit.decode(json.loads(json.dumps(relation.typed(good))), Envelope)
        check.require(relation.exact(restored, good), 'lossless typed text roundtrip')
        result = inspect(restored)
        check.require(result['staged_identity_complete'] and not result['strict_complete'] and not result['inductive_proof'], 'meaningful strict/staged split witness')
        def reject(name, operation):
            try:
                operation()
            except (ValueError, KeyError, TypeError, IndexError) as error:
                controls.append(dict(control=name, detected=True, reason=str(error)))
            else:
                raise ValueError('UNDETECTED CONTROL: ' + name)
        for field in ('candidate', 'plan_sha256', 'source_digest'):
            bad = copy.deepcopy(good)
            bad['binding'][field] = '0' * len(bad['binding'][field])
            reject('stale-' + field, lambda b=bad: inspect(b))
        for name, mutate in (
            ('refused-response', lambda c: c['rows'][3].update(response=False)),
            ('refused-Q-bit', lambda c: c['rows'][3].update(q_invoked=True)),
            ('missing-prefix', lambda c: c['rows'].pop(1)),
            ('missing-suffix', lambda c: c['case']['source']['events'].pop()),
            ('case-binding', lambda c: c['case'].update(case='different-case')),
            ('stage-origin', lambda c: c['rows'][4]['comparison']['identity_proof'].update(event=4)),
            ('origin-case', lambda c: c['rows'][4]['comparison']['identity_proof'].update(case='other')),
            ('origin-prefix', lambda c: c['rows'][4]['comparison']['identity_proof'].update(source_prefix='0' * 64)),
            ('fabricated-pair', lambda c: c['pairs'].append({'source': 'invented'})),
            ('dependency-loss', lambda c: c['case']['source']['profile']['requires'].update({'stage@3': ()})),
        ):
            bad = copy.deepcopy(good)
            mutate(bad)
            reject(name, lambda b=bad: inspect(b))
        # Rebuild every row and hash after mutation. These must fail semantically,
        # not merely because an artifact digest was left stale.
        for name, mutate in (
            ('rehash-initial-outer-bool', lambda l, r: (l[0].update(done=False), r[0].update(done=False))),
            ('rehash-initial-Q-bool', lambda l, r: r[0]['core'].update(done=False)),
            ('rehash-initial-shared-scalar', lambda l, r: (l[0].update(stage_serial=False), r[0]['core'].update(stage_serial=False))),
            ('rehash-both-sides-poststate-type-alias', lambda l, r: [(l[i].update(publisher_boot=True), r[i]['core'].update(publisher_boot=True)) for i in range(1, len(l))]),
            ('rehash-live-Q-generation', lambda l, r: r[2]['core'].update(source_generation=('cut-source', 'collectorA', 'effectA', 9))),
            ('rehash-refused-outer-response', lambda l, r: r[3].update(decision='source-attest:ok')),
            ('rehash-refused-Q-mask', lambda l, r: r[3]['core'].update(done=3)),
            ('rehash-journal-revision', lambda l, r: r[1]['journal'].update(source_revision=7)),
            ('rehash-tuple-type', lambda l, r: r[1]['journal'].update(attempts=list(r[1]['journal']['attempts']))),
            ('rehash-original-signature', lambda l, r: r[4]['core'].update(staged=(r[4]['core']['staged'][0]._replace(signature='0' * 64), PAYLOAD))),
            ('rehash-original-payload', lambda l, r: r[4]['core'].update(staged=(r[4]['core']['staged'][0], PAYLOAD + 'bad'))),
            ('rehash-Q-old-decision', lambda l, r: r[3]['core'].update(decision='source-attest:stale-collection')),
            ('rehash-earlier-field-terminal-restored', lambda l, r: r[2]['core'].update(free=999)),
        ):
            left, right = copy.deepcopy(ss), copy.deepcopy(aa)
            mutate(left, right)
            reject(name, lambda l=left, r=right: inspect(make(l, r)))
        # Positive initial/strict prefix, separately bound as a complete tiny domain.
        empty_profile = dict(PROFILE, actions=(), requires={})
        empty_entry = dict(ENTRY, actions=[])
        initial = relation.certificate(ENTRY['id'], empty_profile, (), 'event', 1, ss[:1], aa[:1], kernel, BINDING)
        attempts += 1
        check.require(audit.inspect(initial, BINDING, empty_entry, empty_profile, kernel)['strict_complete'], 'valid strict fixture')
        # Exercise the same candidate experiment body through the inert backend.
        emitted = []
        fake_plan = dict(profile=PROFILE, cases=[ENTRY])
        outcome = relation.experiment(fake_plan, BINDING, kernel, lambda name, cert: emitted.append(cert))
        check.require(len(emitted) == 1 and outcome[0]['status'] == 'finite-domain-pass', 'executable candidate fake path')
        inspect(emitted[0])
        plan = check.expected_plan()
        check.validate_plan(plan)
        for name, mutate in (
            ('outcome-bool', lambda p: p['profile'].update(outcomes=[True])),
            ('bundle-float', lambda p: p['accounting'].update(scientific_bundles=3.0)),
            ('provider-bool', lambda p: p['construction_limits'].update(provider_calls=False)),
        ):
            bad = copy.deepcopy(plan)
            mutate(bad)
            reject('typed-plan-' + name, lambda b=bad: check.validate_plan(b))
        for key in ('cases', 'fields', 'accounting', 'admission', 'input_closure'):
            bad = copy.deepcopy(plan)
            if key == 'cases': bad[key].pop()
            elif key == 'fields': bad[key]['common'].remove('source_generation')
            elif key == 'accounting': bad[key]['scientific_bundles'] = 1
            elif key == 'admission': bad[key]['status'] = 'approved'
            else: bad[key]['git_tree'] = '0' * 40
            reject('plan-' + key, lambda b=bad: check.validate_plan(b))
        reject('scientific-admission-unavailable', lambda: check.refuse_scientific_admission('execute'))
        reject('receipt-self-attestation-unavailable', lambda: check.refuse_scientific_admission('audit', 'forged-approved.json'))
        reject('inherited-import-firewall', lambda: __import__('s_domain'))
        # A short owned inert timeout, not a scientific/resource campaign. Retain
        # the failing child's evidence and verify its actual exit before PASS.
        timeout_output = Path(tempfile.mkdtemp(prefix='dq-fake-deadline-'))
        program = "import sys,time; from pathlib import Path; sys.path.insert(0,sys.argv[1]); import check; check.arm_fake_deadline(Path(sys.argv[2]),0.1); time.sleep(2)"
        child = subprocess.run([sys.executable, '-X', 'utf8', '-B', '-c', program, str(Path(__file__).parent), str(timeout_output)],
                               capture_output=True, text=True, timeout=4)
        check.require(child.returncode in (124, -9), 'owned fake timeout must terminate the child')
        failure = json.loads((timeout_output / 'deadline-failure.json').read_text(encoding='utf8'))
        check.require(failure['status'] == 'FAKE_GATE_TIMEOUT', 'durable owned timeout evidence')
        controls.append(dict(control='owned-deadline-termination', detected=True, reason='child terminated and failure receipt retained'))
        check.require(len(controls) == 38, 'complete mandatory negative control inventory')
        check.require(time.monotonic() - started < 60, 'fake command time bound')
        return dict(status='FAKE_CONTRACT_PASS', fake_certificates=attempts, valid_fixtures=3,
                    controls=controls, provider_calls=0, inherited_state_visits=0,
                    owned_timeout_evidence=str(timeout_output / 'deadline-failure.json'),
                    scientific_proposition='unexecuted', elapsed_seconds=round(time.monotonic() - started, 3))
    finally:
        sys.meta_path.remove(blocker)


if __name__ == '__main__':
    deadline = check.arm_fake_deadline(Path(tempfile.mkdtemp(prefix='dq-fake-command-')))
    try:
        print(json.dumps(run(), sort_keys=True))
    finally:
        deadline.cancel()

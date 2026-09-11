"""Owned negative controls for the boundary-01 inventory and retained shard.

The module imports only the Python standard library.  Admitted execution must
pass four already-bound callables to ``run_controls`` or ``main``:

``durable_precharge(plan_bytes)``
    Durably reserves the exact canonical plan before any audit call and returns
    ``status``, ``plan_sha256`` and a nonempty ``receipt_id``.  The in-module
    counter is only a local cross-check and is never represented as durable.

``outer_binding(inventory_bytes, result_bytes, expected_indices)``
    Accepts the exact admitted bytes and rejects byte drift with an exception
    whose text contains ``outer-binding``.

``inventory_audit(frozen, symbolic_limit, expected_producer_limit)``
    The public callable from inventory_audit.py.

``retained_audit(frozen, result, expected_indices, charge, inventory_sha256)``
    The public callable from boundary_audit.py. ``charge`` has ``take`` and
    ``visits`` and is fresh for every invocation.

Every callable invocation has a positive baseline at its layer.  The runner
precharges the full declared reservation for the baseline and each mutation
before calling the auditor.  It also reports the retained auditor's actual
counter delta, including partial deltas on rejection.  The inventory auditor's
private failure-path counter is not externally observable, so its actual
runner precharge is reported separately from its success-only returned count.

Controls mutate deep copies of the admitted inventory/shard or bounded copies
of actual certificate bytes.  Producer-emitted control assertions are ignored.
No original model, boundary generator, reducer, provider or ledger is imported
or invoked by this source module itself.
"""
import argparse
import base64
import copy
import gzip
import hashlib
import json
import math
import zlib
from pathlib import Path


MAX_INPUT = 1048576
MAX_B64 = 1048576
MAX_GZIP = 1048576
MAX_JSON = 8388608
WRAPPER_FIXTURES = 4096
INVENTORY_UNITS = 40512
SELECTED = 192
PREFIXES = 35
HISTORIES = 384
EXPECTED_EXCEPTIONS = (ValueError, KeyError, IndexError, TypeError)

OUTER_LABELS = (
    'outer-inventory-byte-binding',
    'outer-shard-byte-binding',
)
INVENTORY_LABELS = (
    'inventory-whole-digest-drift',
    'inventory-hash-encoding-drift',
    'inventory-count-drift',
    'inventory-producer-limit-drift',
    'inventory-membership-drift',
    'inventory-exact-type-drift',
)
RETAINED_LABELS = (
    'certificate-digest-drift',
    'certificate-gzip-overflow',
    'certificate-gzip-truncated',
    'certificate-gzip-trailing-data',
    'certificate-duplicate-json-key',
    'missing-case',
    'duplicate-case',
    'cross-unit-case',
    'wrong-ordinal-filename',
    'shard-history-count-drift',
    'extra-case-row',
    'typed-action-tuple-loss',
    'typed-profile-drift',
    'altered-summary',
    'altered-prefix-census',
    'false-representation-visit-count',
    'changed-actual-q-generation',
    'journal-only-generation-disagreement',
    'altered-attestation-observation',
    'false-q-invocation-on-refused-attestation',
    'dropped-refusal-event-structural',
    'cross-case-stage-proof',
    'staged-identity-misused-as-authority',
    'selected-member-omission',
    'selected-member-duplicate',
    'retained-global-index-drift',
    'retained-subclass-drift',
)
CONTROL_LABELS = OUTER_LABELS + INVENTORY_LABELS + RETAINED_LABELS


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(raw):
    """Decode one finite JSON value while rejecting duplicate keys."""
    require(type(raw) is bytes and len(raw) <= MAX_JSON, 'bounded JSON bytes')

    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError('duplicate JSON key')
            value[key] = item
        return value

    def nonfinite(value):
        raise ValueError('nonfinite JSON constant: ' + value)

    def finite(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError('nonfinite JSON number')
        return result

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite,
                      parse_float=finite)


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


class Counter:
    """Fresh retained-auditor counter with an exact per-call limit."""

    def __init__(self, limit):
        require(type(limit) is int and limit >= 0, 'finite exact counter limit')
        self.limit = limit
        self.visits = 0

    def take(self, amount):
        require(type(amount) is int and amount >= 0,
                'exact nonnegative counter increment')
        require(self.visits + amount <= self.limit,
                'control callable exceeded precharged reservation')
        self.visits += amount


class LocalControlCounter:
    """Local precharge cross-check; controller durability is a separate gate."""

    def __init__(self, limits):
        require(type(limits) is dict and all(type(v) is int and v >= 0
                                             for v in limits.values()),
                'finite reservation plan')
        self.limits = dict(limits)
        self.used = {key: 0 for key in limits}

    def take(self, unit, amount):
        require(unit in self.used and type(amount) is int and amount >= 0,
                'known exact reservation unit')
        before = self.used[unit]
        require(before + amount <= self.limits[unit],
                'precharged control plan exceeded: ' + unit)
        self.used[unit] += amount
        return dict(unit=unit, before=before, after=self.used[unit], delta=amount)


def _reason(error):
    text = str(error)
    return text if text else type(error).__name__


def _call(book, unit, reservation, function, *, baseline, reason_fragments,
          callable_counter=None, callable_delta=None):
    """Precharge one call, run it once and retain its actual rejection facts."""
    precharge = book.take(unit, reservation)
    before = callable_counter.visits if callable_counter is not None else None
    value = None
    error = None
    try:
        value = function()
    except Exception as caught:  # The exact type is classified below.
        error = caught
    after = callable_counter.visits if callable_counter is not None else None
    actual = (after - before) if before is not None else callable_delta(value, error)
    if baseline:
        if error is not None:
            raise ValueError('positive baseline rejected by ' + unit + ': ' + _reason(error))
        return dict(outcome='baseline-pass', detected=True, reason=None,
                    exception_type=None, precharge=precharge,
                    callable_counter_delta=actual)
    if error is None:
        return dict(outcome='undetected-control', detected=False,
                    reason='mutated artifact was accepted', exception_type=None,
                    precharge=precharge, callable_counter_delta=actual)
    text = _reason(error)
    exact_exception = type(error) in EXPECTED_EXCEPTIONS
    attributed = any(fragment in text for fragment in reason_fragments)
    return dict(outcome=unit if exact_exception and attributed else
                        'misattributed-rejection',
                detected=bool(exact_exception and attributed), reason=text,
                exception_type=type(error).__name__, precharge=precharge,
                callable_counter_delta=actual)


def _inventory_call(book, auditor, frozen, expected_producer_limit, *,
                    baseline=False, reasons=()):
    def invoke():
        report = auditor(copy.deepcopy(frozen), INVENTORY_UNITS,
                         expected_producer_limit)
        require(type(report) is dict and report.get('symbolic_units') == INVENTORY_UNITS,
                'inventory auditor did not report exact successful counter')
        return report

    def delta(report, error):
        if error is not None:
            return None
        return report['symbolic_units']

    return _call(book, 'inventory-auditor', INVENTORY_UNITS, invoke,
                 baseline=baseline, reason_fragments=reasons,
                 callable_delta=delta)


def _retained_call(book, auditor, frozen, result, indices, inventory_sha256, *,
                   baseline=False, reasons=()):
    reservation = SELECTED + PREFIXES * len(indices)
    counter = Counter(reservation)

    def invoke():
        report = auditor(copy.deepcopy(frozen), copy.deepcopy(result),
                         list(indices), counter, inventory_sha256)
        require(type(report) is dict and report.get('charged_units') == counter.visits,
                'retained auditor did not echo its actual counter delta')
        return report

    return _call(book, 'retained-auditor', reservation, invoke,
                 baseline=baseline, reason_fragments=reasons,
                 callable_counter=counter)


def _outer_call(book, binder, inventory_raw, result_raw, indices, *,
                baseline=False):
    return _call(book, 'outer-binding', 1,
                 lambda: binder(inventory_raw, result_raw, list(indices)),
                 baseline=baseline, reason_fragments=('outer-binding',),
                 callable_delta=lambda value, error: None)


def _flip_hex(value):
    require(type(value) is str and len(value) == 64,
            'reachable 64-character digest witness')
    return ('1' if value[0] != '1' else '0') + value[1:]


def _drift(value):
    """One JSON-safe, exact-type-preserving drift where possible."""
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is float:
        return value + 1.0
    if type(value) is str:
        return value + ':control-drift'
    if value is None:
        return 'control-drift'
    if type(value) is list:
        return copy.deepcopy(value) + ['control-drift']
    if type(value) is dict:
        result = copy.deepcopy(value)
        result['__control_drift__'] = True
        return result
    raise ValueError('no JSON-safe drift for witness type')


def _certificate_raw(info):
    require(type(info) is dict and type(info.get('certificate_gzip_base64')) is str
            and len(info['certificate_gzip_base64']) <= MAX_B64,
            'reachable bounded certificate witness')
    raw = base64.b64decode(info['certificate_gzip_base64'], validate=True)
    require(len(raw) <= MAX_GZIP, 'reachable bounded gzip witness')
    return raw


def _replace_certificate(info, raw):
    require(type(raw) is bytes and len(raw) <= MAX_GZIP,
            'bounded replacement certificate')
    info['certificate_gzip_base64'] = base64.b64encode(raw).decode('ascii')
    info['artifact_sha256'] = hashlib.sha256(raw).hexdigest()


def _inflate(raw):
    stream = zlib.decompressobj(31)
    body = stream.decompress(raw, MAX_JSON + 1)
    require(len(body) <= MAX_JSON and not stream.unconsumed_tail and stream.eof
            and stream.unused_data == b'', 'reachable complete certificate JSON')
    return body


def _typed_entries(node):
    require(type(node) is list and len(node) == 2 and node[0] == 'dict'
            and type(node[1]) is list, 'reachable typed dictionary witness')
    entries = node[1]
    require(all(type(item) is list and len(item) == 2 and type(item[0]) is str
                for item in entries), 'reachable typed dictionary entries')
    return entries


def _typed_get(node, key):
    matches = [value for name, value in _typed_entries(node) if name == key]
    require(len(matches) == 1, 'reachable typed key witness: ' + key)
    return matches[0]


def _typed_set(node, key, value):
    entries = _typed_entries(node)
    matches = [index for index, item in enumerate(entries) if item[0] == key]
    require(len(matches) == 1, 'reachable typed key witness: ' + key)
    entries[matches[0]][1] = copy.deepcopy(value)


def _typed_update(node, patch):
    for key, value in _typed_entries(patch):
        _typed_set(node, key, value)


def _typed_sequence(node, tag=None):
    require(type(node) is list and len(node) == 2 and type(node[0]) is str
            and type(node[1]) is list and (tag is None or node[0] == tag),
            'reachable typed sequence witness' + (': ' + tag if tag else ''))
    return node[1]


def _typed_scalar(node, tag=None):
    require(type(node) is list and len(node) == 2
            and (tag is None or node[0] == tag),
            'reachable typed scalar witness' + (': ' + tag if tag else ''))
    return node[1]


def _typed_strings(node):
    return [_typed_scalar(item, 'str') for item in _typed_sequence(node)]


def _bump_generation(node):
    values = _typed_sequence(node, 'tuple')
    require(values and type(values[-1]) is list and len(values[-1]) == 2
            and values[-1][0] == 'int' and type(values[-1][1]) is int,
            'reachable typed source-generation serial')
    values[-1][1] += 1


def _packed_value(value, objects):
    if type(value) is dict and set(value) == {'$text_sha256'}:
        key = value['$text_sha256']
        require(type(key) is str and key in objects and type(objects[key]) is str
                and hashlib.sha256(objects[key].encode('utf-8')).hexdigest() == key,
                'bound packed text reference')
        return objects[key]
    return value


def _typed_plain(node, objects):
    require(type(node) is list and len(node) == 2 and type(node[0]) is str,
            'reachable typed evidence node')
    tag, body = node
    if tag == 'dict':
        return {key: _typed_plain(value, objects)
                for key, value in _typed_entries(node)}
    if tag in ('list', 'tuple', 'Envelope'):
        return [_typed_plain(value, objects) for value in _typed_sequence(node)]
    require(tag in ('str', 'int', 'bool', 'float', 'NoneType'),
            'reachable typed scalar tag')
    return _packed_value(body, objects)


def _typed_digest(node, objects):
    raw = json.dumps(_typed_plain(node, objects), sort_keys=True,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def _rebind_adapter_trace(adapter, objects):
    """Rebuild exact trace hashes after a typed journal patch mutation."""
    current = copy.deepcopy(_typed_get(adapter, 'initial'))
    events = _typed_sequence(_typed_get(adapter, 'events'), 'list')
    for event in events:
        before = _typed_get(event, 'before_sha256')
        require(before[0] == 'str', 'typed trace before hash')
        before[1] = _typed_digest(current, objects)
        patch = _typed_get(event, 'patch')
        for key, value in _typed_entries(patch):
            if key in ('core', 'journal'):
                _typed_update(_typed_get(current, key), value)
            else:
                _typed_set(current, key, value)
        after = _typed_get(event, 'after_sha256')
        require(after[0] == 'str', 'typed trace after hash')
        after[1] = _typed_digest(current, objects)


def _used_texts(value, used):
    if type(value) is dict:
        if set(value) == {'$text_sha256'} and type(value['$text_sha256']) is str:
            used.add(value['$text_sha256'])
        else:
            for item in value.values():
                _used_texts(item, used)
    elif type(value) is list:
        for item in value:
            _used_texts(item, used)


def _edit_certificate(result, position, edit):
    info = result['cases'][position]
    packed = strict_json(_inflate(_certificate_raw(info)))
    require(type(packed) is dict and set(packed) == {'format', 'objects', 'result'}
            and packed['format'] == 'text-interning/1'
            and type(packed['objects']) is dict,
            'reachable packed certificate envelope')
    rebind_adapter = edit(packed['result'])
    if rebind_adapter:
        _rebind_adapter_trace(_typed_get(packed['result'], 'adapter'),
                              packed['objects'])
    used = set()
    _used_texts(packed['result'], used)
    packed['objects'] = {key: value for key, value in packed['objects'].items()
                         if key in used}
    raw = gzip.compress(canonical_bytes(packed), compresslevel=6, mtime=0)
    _replace_certificate(info, raw)


def _read_typed_case(result, position):
    packed = strict_json(_inflate(_certificate_raw(result['cases'][position])))
    require(type(packed) is dict and set(packed) == {'format', 'objects', 'result'},
            'reachable packed case witness')
    return packed['result']


def _case_name(result, position):
    return _typed_scalar(_typed_get(_read_typed_case(result, position), 'case'), 'str')


def _mutated_inventory(frozen, change):
    result = copy.deepcopy(frozen)
    change(result)
    return result


def _mutated_result(result, change):
    value = copy.deepcopy(result)
    change(value)
    return value


def _candidate(label, target, mutation, reasons, *, scope='result', witness=None,
               unavailable=None):
    return dict(label=label, target=target, mutation=mutation, reasons=tuple(reasons),
                scope=scope, witness=witness or {}, unavailable=unavailable)


def _inventory_controls(frozen):
    controls = []
    controls.append(_candidate(
        INVENTORY_LABELS[0], 'inventory-auditor',
        _mutated_inventory(frozen, lambda x: x.update(
            whole_inventory_sha256=_flip_hex(x['whole_inventory_sha256']))),
        ('changed whole inventory digest rejected',),
        witness={'path': 'whole_inventory_sha256', 'operation': 'single-hex drift'}))
    controls.append(_candidate(
        INVENTORY_LABELS[1], 'inventory-auditor',
        _mutated_inventory(frozen, lambda x: x.update(
            inventory_hash_encoding=_drift(x['inventory_hash_encoding']))),
        ('declared digest encoding matches audited encoding',),
        witness={'path': 'inventory_hash_encoding', 'operation': 'string drift'}))
    controls.append(_candidate(
        INVENTORY_LABELS[2], 'inventory-auditor',
        _mutated_inventory(frozen, lambda x: x['subclass_counts'].__setitem__(
            'fresh-incomplete', x['subclass_counts']['fresh-incomplete'] + 1)),
        ('frozen declared counts',),
        witness={'path': 'subclass_counts.fresh-incomplete', 'operation': '+1'}))
    controls.append(_candidate(
        INVENTORY_LABELS[3], 'inventory-auditor',
        _mutated_inventory(frozen, lambda x: x.update(
            symbolic_limit=x['symbolic_limit'] + 1)),
        ('frozen charged-work provenance',),
        witness={'path': 'symbolic_limit', 'operation': '+1'}))

    def member(change):
        schedule = change['selected'][0]['schedule']
        require(type(schedule) is list and len(schedule) >= 14,
                'reachable selected schedule witness')
        schedule[12], schedule[13] = schedule[13], schedule[12]

    controls.append(_candidate(
        INVENTORY_LABELS[4], 'inventory-auditor',
        _mutated_inventory(frozen, member),
        ('exact frozen membership, subclass and global rank',),
        witness={'path': 'selected[0].schedule[12:14]',
                 'operation': 'swap two valid core occurrences without changing claimed rank'}))
    controls.append(_candidate(
        INVENTORY_LABELS[5], 'inventory-auditor',
        _mutated_inventory(frozen, lambda x: x['selected'][0].__setitem__(
            'global_index', str(x['selected'][0]['global_index']))),
        ('exact frozen membership, subclass and global rank',),
        witness={'path': 'selected[0].global_index', 'operation': 'int-to-str drift'}))
    return controls


def _retained_controls(frozen, result, indices):
    controls = []

    def cert_result(change):
        return _mutated_result(result, change)

    def certificate_digest(value):
        raw = _certificate_raw(value['cases'][0])
        require(raw, 'nonempty certificate witness')
        changed = raw[:-1] + bytes((raw[-1] ^ 1,))
        value['cases'][0]['certificate_gzip_base64'] = base64.b64encode(changed).decode('ascii')

    controls.append(_candidate(
        RETAINED_LABELS[0], 'retained-auditor', cert_result(certificate_digest),
        ('exact certificate bytes and sha256 binding',),
        witness={'position': 0, 'operation': 'one gzip byte drift with retained digest'}))

    def overflow(value):
        raw = gzip.compress(b' ' * (MAX_JSON + 1), compresslevel=6, mtime=0)
        _replace_certificate(value['cases'][0], raw)

    controls.append(_candidate(
        RETAINED_LABELS[1], 'retained-auditor', cert_result(overflow),
        ('certificate expansion exceeds bound',),
        witness={'position': 0, 'expanded_bytes': MAX_JSON + 1}))

    def truncated(value):
        raw = _certificate_raw(value['cases'][0])
        require(len(raw) > 1, 'truncatable certificate witness')
        _replace_certificate(value['cases'][0], raw[:-1])

    controls.append(_candidate(
        RETAINED_LABELS[2], 'retained-auditor', cert_result(truncated),
        ('certificate gzip decode', 'bounded complete certificate stream'),
        witness={'position': 0, 'operation': 'remove final gzip byte and rebind digest'}))

    def trailing(value):
        raw = _certificate_raw(value['cases'][0]) + b'\x00'
        _replace_certificate(value['cases'][0], raw)

    controls.append(_candidate(
        RETAINED_LABELS[3], 'retained-auditor', cert_result(trailing),
        ('bounded complete certificate stream',),
        witness={'position': 0, 'operation': 'append trailing byte and rebind digest'}))

    def duplicate_json(value):
        body = _inflate(_certificate_raw(value['cases'][0]))
        offset = len(body) - len(body.lstrip())
        require(body[offset:offset + 1] == b'{', 'certificate root JSON object witness')
        duplicate = b'"__control_duplicate__":0,"__control_duplicate__":1,'
        raw = gzip.compress(body[:offset + 1] + duplicate + body[offset + 1:],
                            compresslevel=6, mtime=0)
        _replace_certificate(value['cases'][0], raw)

    controls.append(_candidate(
        RETAINED_LABELS[4], 'retained-auditor', cert_result(duplicate_json),
        ('duplicate JSON key',),
        witness={'position': 0, 'operation': 'duplicate root JSON key and rebind digest'}))

    controls.append(_candidate(
        RETAINED_LABELS[5], 'retained-auditor',
        cert_result(lambda x: x['cases'].pop(0)),
        ('exact per-history result sections',),
        witness={'path': 'cases[0]', 'operation': 'remove'}))

    if len(indices) >= 2:
        controls.append(_candidate(
            RETAINED_LABELS[6], 'retained-auditor',
            cert_result(lambda x: x['cases'].__setitem__(1, copy.deepcopy(x['cases'][0]))),
            ('exact ordinal artifact filename', 'decoded case identity, schedule and original profile'),
            witness={'source_position': 0, 'target_position': 1,
                     'operation': 'duplicate actual case over another position'}))
    else:
        controls.append(_candidate(
            RETAINED_LABELS[6], 'retained-auditor', None, (),
            unavailable='requires at least two admitted cases',
            witness={'required': 'two result case positions'}))

    pair = next(((left, right) for left, a in enumerate(indices)
                 for right, b in enumerate(indices)
                 if left != right and a // 2 == b // 2 and a % 2 != b % 2), None)
    if pair is None:
        controls.append(_candidate(
            RETAINED_LABELS[7], 'retained-auditor', None, (),
            unavailable='requires both unit certificates for one selected schedule',
            witness={'required': 'admitted ordinal pair (2k,2k+1)'}))
    else:
        target, donor = pair

        def cross_unit(value):
            value['cases'][target]['certificate_gzip_base64'] = copy.deepcopy(
                value['cases'][donor]['certificate_gzip_base64'])
            value['cases'][target]['artifact_sha256'] = value['cases'][donor]['artifact_sha256']

        controls.append(_candidate(
            RETAINED_LABELS[7], 'retained-auditor', cert_result(cross_unit),
            ('decoded case identity, schedule and original profile',),
            witness={'target_position': target, 'donor_position': donor,
                     'target_ordinal': indices[target], 'donor_ordinal': indices[donor],
                     'operation': 'substitute opposite-unit certificate under target filename'}))

    controls.append(_candidate(
        RETAINED_LABELS[8], 'retained-auditor',
        cert_result(lambda x: x['cases'][0].__setitem__('artifact', 'wrong.json.gz')),
        ('exact ordinal artifact filename',),
        witness={'path': 'cases[0].artifact', 'operation': 'wrong ordinal name'}))
    controls.append(_candidate(
        RETAINED_LABELS[9], 'retained-auditor',
        cert_result(lambda x: x.update(histories=x['histories'] + 1)),
        ('exact shard cardinalities',),
        witness={'path': 'histories', 'operation': '+1'}))

    def extra_row(value):
        def edit(root):
            rows = _typed_sequence(_typed_get(root, 'rows'), 'list')
            require(rows, 'reachable typed comparison-row witness')
            rows.append(copy.deepcopy(rows[-1]))
        _edit_certificate(value, 0, edit)

    controls.append(_candidate(
        RETAINED_LABELS[10], 'retained-auditor', cert_result(extra_row),
        ('exact visible events, comparison rows and prefixes',),
        witness={'certificate_position': 0, 'path': 'case.rows',
                 'operation': 'append duplicate actual row'}))

    def tuple_loss(value):
        def edit(root):
            actions = _typed_get(_typed_get(root, 'source'), 'actions')
            require(actions[0] == 'tuple', 'reachable source action tuple witness')
            actions[0] = 'list'
        _edit_certificate(value, 0, edit)

    controls.append(_candidate(
        RETAINED_LABELS[11], 'retained-auditor', cert_result(tuple_loss),
        ('decoded case identity, schedule and original profile',),
        witness={'certificate_position': 0, 'path': 'case.source.actions.type',
                 'operation': 'tuple-to-list'}))

    def profile_drift(value):
        def edit(root):
            profile = _typed_get(_typed_get(root, 'source'), 'profile')
            actions = _typed_sequence(_typed_get(profile, 'actions'))
            require(actions and actions[0][0] == 'str', 'reachable profile action witness')
            actions[0][1] = _drift(actions[0][1])
        _edit_certificate(value, 0, edit)

    controls.append(_candidate(
        RETAINED_LABELS[12], 'retained-auditor', cert_result(profile_drift),
        ('decoded case identity, schedule and original profile',),
        witness={'certificate_position': 0, 'path': 'case.source.profile.actions[0]',
                 'operation': 'literal action drift'}))

    controls.append(_candidate(
        RETAINED_LABELS[13], 'retained-auditor',
        cert_result(lambda x: x['summaries'][0].__setitem__(
            'visible_events', x['summaries'][0]['visible_events'] + 1)),
        ('independently reconstructed summary',),
        witness={'path': 'summaries[0].visible_events', 'operation': '+1'}))
    controls.append(_candidate(
        RETAINED_LABELS[14], 'retained-auditor',
        cert_result(lambda x: x['prefix_censuses'][0][0].__setitem__(
            'decision', _drift(x['prefix_censuses'][0][0]['decision']))),
        ('independently reconstructed prefix census',),
        witness={'path': 'prefix_censuses[0][0].decision', 'operation': 'scalar drift'}))
    controls.append(_candidate(
        RETAINED_LABELS[15], 'retained-auditor',
        cert_result(lambda x: x.update(state_visits=x['state_visits'] + 1)),
        ('exact actual representation visits and reservation',),
        witness={'path': 'state_visits', 'operation': '+1'}))

    def q_generation(value):
        def edit(root):
            initial = _typed_get(_typed_get(root, 'adapter'), 'initial')
            core = _typed_get(initial, 'core')
            _bump_generation(_typed_get(core, 'source_generation'))
        _edit_certificate(value, 0, edit)

    controls.append(_candidate(
        RETAINED_LABELS[16], 'retained-auditor', cert_result(q_generation),
        ('complete adapter initialization',),
        witness={'certificate_position': 0,
                 'path': 'case.adapter.initial.core.source_generation[-1]',
                 'operation': '+1'}))

    def journal_generation(value):
        def edit(root):
            adapter = _typed_get(root, 'adapter')
            actions = _typed_strings(_typed_get(adapter, 'actions'))
            index = next(i for i, action in enumerate(actions)
                         if action.split('@')[0] == 'source-restart')
            event = _typed_sequence(_typed_get(adapter, 'events'), 'list')[index]
            patch = _typed_get(event, 'patch')
            journal = _typed_get(patch, 'journal')
            _bump_generation(_typed_get(journal, 'source_generation'))
            return True
        _edit_certificate(value, 0, edit)

    try:
        journal_value = cert_result(journal_generation)
        controls.append(_candidate(
            RETAINED_LABELS[17], 'retained-auditor', journal_value,
            ('complete independent adapter ledger postcondition source-restart',),
            witness={'certificate_position': 0,
                     'path': 'case.adapter.events[source-restart].patch.journal.source_generation[-1]',
                     'operation': '+1 without Q-core change; rebuild every adapter trace hash'}))
    except (ValueError, KeyError, IndexError, TypeError, StopIteration) as error:
        controls.append(_candidate(
            RETAINED_LABELS[17], 'retained-auditor', None, (),
            unavailable='actual source-restart journal patch not reachable: ' + _reason(error),
            witness={'required': 'adapter source-restart event with journal generation patch'}))

    controls.append(_candidate(
        RETAINED_LABELS[18], 'retained-auditor',
        cert_result(lambda x: x['attestation_observations'][0].__setitem__(
            'source_decision', _drift(x['attestation_observations'][0]['source_decision']))),
        ('independently reconstructed attestation observation',),
        witness={'path': 'attestation_observations[0].source_decision',
                 'operation': 'decision drift'}))

    def refused_invocation(value):
        def edit(root):
            actions = _typed_strings(_typed_get(_typed_get(root, 'source'), 'actions'))
            index = next(i for i, action in enumerate(actions)
                         if action.split('@')[0] == 'source-attest')
            row = _typed_sequence(_typed_get(root, 'rows'), 'list')[index]
            invoked = _typed_get(row, 'q_invoked')
            require(invoked == ['bool', False], 'reachable refused-attestation witness')
            invoked[1] = True
        _edit_certificate(value, 0, edit)

    try:
        refusal_value = cert_result(refused_invocation)
        controls.append(_candidate(
            RETAINED_LABELS[19], 'retained-auditor', refusal_value,
            ('actual Q invocation and translation retained',),
            witness={'certificate_position': 0,
                     'path': 'case.rows[source-attest].q_invoked',
                     'operation': 'false-to-true on actual refusal'}))
    except (ValueError, KeyError, IndexError, TypeError, StopIteration) as error:
        controls.append(_candidate(
            RETAINED_LABELS[19], 'retained-auditor', None, (),
            unavailable='refused source-attest row not reachable: ' + _reason(error),
            witness={'required': 'actual source-attest row with q_invoked false'}))

    def dropped_refusal(value):
        def edit(root):
            source = _typed_get(root, 'source')
            actions = _typed_strings(_typed_get(source, 'actions'))
            index = next(i for i, action in enumerate(actions)
                         if action.split('@')[0] == 'source-attest')
            rows = _typed_sequence(_typed_get(root, 'rows'), 'list')
            require(_typed_get(rows[index], 'q_invoked') == ['bool', False],
                    'reachable refused-attestation event witness')
            _typed_sequence(_typed_get(source, 'events'), 'list').pop(index)
        _edit_certificate(value, 0, edit)

    try:
        dropped_value = cert_result(dropped_refusal)
        controls.append(_candidate(
            RETAINED_LABELS[20], 'retained-auditor', dropped_value,
            ('exact visible events, comparison rows and prefixes',
             'complete visible event inventory'),
            witness={'certificate_position': 0,
                     'path': 'case.source.events[source-attest]',
                     'operation': 'drop actual refused event'}))
    except (ValueError, KeyError, IndexError, TypeError, StopIteration) as error:
        controls.append(_candidate(
            RETAINED_LABELS[20], 'retained-auditor', None, (),
            unavailable='refused source-attest event not reachable: ' + _reason(error),
            witness={'required': 'actual refused source-attest event'}))

    identity_position = None
    identity_prefix = None
    for position in range(len(indices)):
        try:
            root = _read_typed_case(result, position)
            prefixes = _typed_sequence(_typed_get(root, 'prefixes'), 'list')
            identity_prefix = next(i for i, row in enumerate(prefixes)
                if _typed_get(row, 'identity_proof')[0] != 'NoneType')
            identity_position = position
            break
        except (ValueError, KeyError, IndexError, TypeError, StopIteration):
            continue

    donor_position = next((i for i in range(len(indices)) if i != identity_position), None)
    if identity_position is None or donor_position is None:
        controls.append(_candidate(
            RETAINED_LABELS[21], 'retained-auditor', None, (),
            unavailable='requires an actual identity-proof prefix and a distinct admitted case',
            witness={'required': 'identity proof plus second case'}))
    else:
        donor_name = _case_name(result, donor_position)

        def cross_proof(value):
            def edit(root):
                prefixes = _typed_sequence(_typed_get(root, 'prefixes'), 'list')
                proof = _typed_get(prefixes[identity_prefix], 'identity_proof')
                case = _typed_get(proof, 'case')
                require(case[0] == 'str', 'typed identity proof case witness')
                case[1] = donor_name
            _edit_certificate(value, identity_position, edit)

        controls.append(_candidate(
            RETAINED_LABELS[21], 'retained-auditor', cert_result(cross_proof),
            ('independent typed replay of every prefix',),
            witness={'certificate_position': identity_position, 'prefix': identity_prefix,
                     'donor_position': donor_position, 'donor_case': donor_name,
                     'operation': 'bind proof to distinct admitted case'}))

    authority_position = None
    authority_prefix = None
    for position in range(len(indices)):
        try:
            root = _read_typed_case(result, position)
            prefixes = _typed_sequence(_typed_get(root, 'prefixes'), 'list')
            authority_prefix = next(i for i, row in enumerate(prefixes)
                if _typed_scalar(_typed_get(row, 'staged_rule'), 'str') ==
                   'original-object-identity')
            authority_position = position
            break
        except (ValueError, KeyError, IndexError, TypeError, StopIteration):
            continue

    if authority_position is None:
        controls.append(_candidate(
            RETAINED_LABELS[22], 'retained-auditor', None, (),
            unavailable='requires an actual original-object-identity prefix',
            witness={'required': 'staged_rule original-object-identity'}))
    else:
        def identity_authority(value):
            def edit(root):
                prefixes = _typed_sequence(_typed_get(root, 'prefixes'), 'list')
                row = prefixes[authority_prefix]
                authority = _typed_get(row, 'incarnation_pair_established_by_identity')
                require(authority == ['bool', False], 'non-authoritative identity witness')
                authority[1] = True
            _edit_certificate(value, authority_position, edit)

        controls.append(_candidate(
            RETAINED_LABELS[22], 'retained-auditor', cert_result(identity_authority),
            ('independent typed replay of every prefix',),
            witness={'certificate_position': authority_position, 'prefix': authority_prefix,
                     'path': 'incarnation_pair_established_by_identity',
                     'operation': 'false-to-true'}))

    controls.append(_candidate(
        RETAINED_LABELS[23], 'retained-auditor',
        _mutated_inventory(frozen, lambda x: x['selected'].pop()),
        ('declared inventory shape and budget',), scope='inventory',
        witness={'path': 'selected[-1]', 'operation': 'omit actual selected member'}))
    controls.append(_candidate(
        RETAINED_LABELS[24], 'retained-auditor',
        _mutated_inventory(frozen, lambda x: x['selected'].__setitem__(
            1, copy.deepcopy(x['selected'][0]))),
        ('exact unique rank and literal subclass membership',), scope='inventory',
        witness={'source': 'selected[0]', 'target': 'selected[1]',
                 'operation': 'duplicate actual member at fixed cardinality'}))
    controls.append(_candidate(
        RETAINED_LABELS[25], 'retained-auditor',
        _mutated_inventory(frozen, lambda x: x['selected'][0].__setitem__(
            'global_index', x['selected'][0]['global_index'] + 1)),
        ('exact unique rank and literal subclass membership',), scope='inventory',
        witness={'path': 'selected[0].global_index', 'operation': 'numeric +1'}))

    def subclass_drift(value):
        item = value['selected'][0]
        item['subclass'] = ('fresh-incomplete' if item['subclass'] != 'fresh-incomplete'
                            else 'stale-complete')

    controls.append(_candidate(
        RETAINED_LABELS[26], 'retained-auditor',
        _mutated_inventory(frozen, subclass_drift),
        ('exact unique rank and literal subclass membership',), scope='inventory',
        witness={'path': 'selected[0].subclass',
                 'operation': 'swap to the other admitted subclass label'}))

    require(tuple(item['label'] for item in controls) == RETAINED_LABELS,
            'complete fixed retained-control inventory')
    return controls


def _execute_control(book, control, inventory_audit, retained_audit, frozen,
                     result, indices, inventory_sha256, expected_producer_limit):
    if control['unavailable'] is not None:
        return dict(control=control['label'], target=control['target'],
                    outcome='unavailable-reachable-witness', detected=False,
                    reason=control['unavailable'], exception_type=None,
                    precharge=None, callable_counter_delta=None,
                    witness=control['witness'])
    if control['target'] == 'inventory-auditor':
        execution = _inventory_call(book, inventory_audit, control['mutation'],
                                    expected_producer_limit,
                                    reasons=control['reasons'])
    else:
        controlled_frozen = (control['mutation'] if control['scope'] == 'inventory'
                             else frozen)
        controlled_result = (control['mutation'] if control['scope'] == 'result'
                             else result)
        execution = _retained_call(book, retained_audit, controlled_frozen,
                                   controlled_result, indices, inventory_sha256,
                                   reasons=control['reasons'])
    return dict(control=control['label'], target=control['target'],
                witness=control['witness'], **execution)


def run_controls(inventory_raw, result_raw, expected_indices, *,
                 durable_precharge, outer_binding, inventory_audit, retained_audit,
                 expected_producer_limit=INVENTORY_UNITS):
    """Run the fixed owned suite over exact admitted bytes and passed callables."""
    require(callable(durable_precharge) and callable(outer_binding)
            and callable(inventory_audit) and callable(retained_audit),
            'durable precharge and three passed audit callables required')
    require(type(inventory_raw) is bytes and 0 < len(inventory_raw) <= MAX_INPUT
            and type(result_raw) is bytes and 0 < len(result_raw) <= MAX_INPUT,
            'bounded nonempty admitted inventory and shard bytes')
    require(type(expected_indices) is list and 0 < len(expected_indices) <= 24
            and all(type(value) is int and 0 <= value < HISTORIES
                    for value in expected_indices)
            and len(set(expected_indices)) == len(expected_indices),
            'finite distinct expected shard ordinals')
    require(type(expected_producer_limit) is int
            and expected_producer_limit == INVENTORY_UNITS,
            'exact admitted producer limit')
    frozen = strict_json(inventory_raw)
    result = strict_json(result_raw)
    require(type(frozen) is dict and type(result) is dict,
            'admitted JSON objects')

    inventory_controls = _inventory_controls(frozen)
    retained_controls = _retained_controls(frozen, result, expected_indices)
    inventory_sha256 = hashlib.sha256(inventory_raw).hexdigest()
    available_retained = sum(item['unavailable'] is None
                             for item in retained_controls)
    retained_reservation = SELECTED + PREFIXES * len(expected_indices)
    limits = {
        'outer-binding': 1 + len(OUTER_LABELS),
        'inventory-auditor': INVENTORY_UNITS * (1 + len(inventory_controls)),
        'retained-auditor': retained_reservation * (1 + available_retained),
    }
    durable_plan = {
        'version': 1,
        'packet': 'boundary-01',
        'inventory_input_sha256': inventory_sha256,
        'result_input_sha256': hashlib.sha256(result_raw).hexdigest(),
        'expected_indices': list(expected_indices),
        'fixed_control_labels': list(CONTROL_LABELS),
        'local_control_limits': dict(limits),
        'wrapper_fixture_kernel_calls': WRAPPER_FIXTURES,
    }
    plan_bytes = canonical_bytes(durable_plan)
    plan_sha256 = hashlib.sha256(plan_bytes).hexdigest()
    receipt = durable_precharge(plan_bytes)
    require(type(receipt) is dict and set(receipt) ==
            {'status', 'plan_sha256', 'receipt_id'}
            and receipt['status'] == 'DURABLY_PRECHARGED'
            and receipt['plan_sha256'] == plan_sha256
            and type(receipt['receipt_id']) is str and receipt['receipt_id'],
            'exact controller durable precharge receipt')
    receipt = strict_json(canonical_bytes(receipt))
    book = LocalControlCounter(limits)

    baselines = {
        'outer-binding': _outer_call(book, outer_binding, inventory_raw, result_raw,
                                     expected_indices, baseline=True),
        'inventory-auditor': _inventory_call(
            book, inventory_audit, frozen, expected_producer_limit, baseline=True),
        'retained-auditor': _retained_call(
            book, retained_audit, frozen, result, expected_indices,
            inventory_sha256, baseline=True),
    }

    controls = []
    outer_mutations = (
        (OUTER_LABELS[0], inventory_raw + b' ', result_raw,
         {'artifact': 'inventory', 'operation': 'append semantically inert byte'}),
        (OUTER_LABELS[1], inventory_raw, result_raw + b' ',
         {'artifact': 'shard', 'operation': 'append semantically inert byte'}),
    )
    for label, changed_inventory, changed_result, witness in outer_mutations:
        execution = _outer_call(book, outer_binding, changed_inventory,
                                changed_result, expected_indices)
        controls.append(dict(control=label, target='outer-binding', witness=witness,
                             **execution))
    for control in inventory_controls + retained_controls:
        controls.append(_execute_control(
            book, control, inventory_audit, retained_audit, frozen, result,
            expected_indices, inventory_sha256, expected_producer_limit))

    require(tuple(item['control'] for item in controls) == CONTROL_LABELS,
            'complete fixed owned control inventory')
    require(book.used == book.limits, 'every planned baseline/repetition precharged exactly')
    unavailable = [item['control'] for item in controls
                   if item['outcome'] == 'unavailable-reachable-witness']
    failed = [item['control'] for item in controls
              if item['outcome'] not in (item['target'],
                                         'unavailable-reachable-witness')]
    detected = [item['control'] for item in controls
                if item['outcome'] == item['target'] and item['detected']]
    return {
        'packet': 'boundary-01',
        'runner': 'owned-boundary-mutation-controls',
        'status': ('COMPLETE_FIXED_CONTROL_SUITE' if not unavailable and not failed
                   else 'INCOMPLETE_FIXED_CONTROL_SUITE'),
        'inventory_input_sha256': hashlib.sha256(inventory_raw).hexdigest(),
        'result_input_sha256': hashlib.sha256(result_raw).hexdigest(),
        'expected_indices': list(expected_indices),
        'expected_producer_limit': expected_producer_limit,
        'fixed_control_labels': list(CONTROL_LABELS),
        'baselines': baselines,
        'controls': controls,
        'detected_controls': detected,
        'unavailable_reachable_witnesses': unavailable,
        'failed_controls': failed,
        'all_available_controls_detected': not failed,
        'all_required_controls_detected': not unavailable and not failed,
        'durable_precharge_plan_sha256': plan_sha256,
        'durable_precharge_receipt': receipt,
        'local_control_limits': dict(book.limits),
        'actual_local_control_precharges': dict(book.used),
        'wrapper_fixture_kernel_calls_in_durable_plan': WRAPPER_FIXTURES,
        'reservation_units_are_not_additive': True,
        'producer_asserted_controls_accepted': False,
        'outer_binding_bypassed_for_semantic_controls': True,
        'original_model_or_reducer_execution_by_runner': False,
        'limitations': [
            'Outer byte binding is tested separately; semantic mutations are sent directly '
            'to the responsible independent auditor so an outer hash rejection cannot be '
            'misreported as semantic discrimination.',
            'The inventory auditor owns a private Symbolic counter. Its successful report '
            'exposes the actual 40512-unit delta; rejection paths expose only this runner\'s '
            'actual full precharge, not the private partial counter.',
            'Controls establish discrimination over mutations of retained admitted artifacts. '
            'They do not establish that each corrupted state is reachable in the model domain.',
            'The dropped-refusal control is structural: it proves the exact trace cardinality '
            'gate rejects removal. A semantic refusal control with preserved cardinality is the '
            'separate false-q-invocation mutation.',
        ],
    }


def main(argv=None, *, durable_precharge=None, outer_binding=None, inventory_audit=None,
         retained_audit=None):
    """CLI-shaped entry used by the admitted wrapper after callable injection."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--indices', required=True)
    parser.add_argument('--expected-producer-limit', type=int, required=True)
    parser.add_argument('--stdout-limit', type=int, default=MAX_INPUT)
    args = parser.parse_args(argv)
    require(callable(durable_precharge) and callable(outer_binding)
            and callable(inventory_audit) and callable(retained_audit),
            'admitted wrapper must inject durable precharge and bound audit callables')
    require(1 <= args.stdout_limit <= MAX_INPUT, 'bounded stdout limit')
    inventory_raw = args.inventory.read_bytes()
    result_raw = args.result.read_bytes()
    indices = [int(value) for value in args.indices.split(',')]
    report = run_controls(
        inventory_raw, result_raw, indices, durable_precharge=durable_precharge,
        outer_binding=outer_binding,
        inventory_audit=inventory_audit, retained_audit=retained_audit,
        expected_producer_limit=args.expected_producer_limit)
    report['runner_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    payload = canonical_bytes(report)
    require(len(payload) <= args.stdout_limit, 'bounded control report stdout object')
    print(payload.decode('utf-8'))


if __name__ == '__main__':
    raise SystemExit(
        'REFUSED: import this source in the admitted wrapper and call main with '
        'durable_precharge, outer_binding, inventory_audit and retained_audit callables')

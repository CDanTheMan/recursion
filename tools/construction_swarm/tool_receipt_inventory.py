"""Independent verifier for a complete retained native-v3 attempt bundle.

The bundle is an explicit mapping of canonical relative POSIX paths to the
retained bytes of a single attempt: packet.json, receipt.json, transport.json,
filing.json, client-output/export.json, config/config.json,
config/tool-presentation.json and the contiguous tools/<n>/ directories.
Controller artifacts must be canonical strict JSON; the provider export must
be strict JSON. Retained bytes and prose are untrusted data, never authority:
every 'accepted' flag must be false, the attempt must be a returned native-v3
attempt, and every claimed binding is recomputed from the supplied bytes.
"""
from __future__ import annotations

import re

from .contracts import (
    JOB_TOOLS,
    Refused,
    digest,
    encoded,
    identifier,
    integer,
    keys,
    path,
    require,
    strict_json,
    validate_allowed_tools,
    validate_filing,
)

PERMISSION_DIGEST_FIELD = 'permission_presentation_sha256'
TOOL_DIGEST_FIELD = 'tool_presentation_sha256'
PRESENTATION_VERSION = 'foundry-mcp/v3-paged-read-1'
MCP_PROTOCOL_VERSION = '2024-11-05'
MCP_SERVER_NAME = 'recursion-foundry'
MCP_PAGED_SERVER_VERSION = '2'
READ_FILE_MAX_BYTES = 4096
READ_FILE_MAX_VALUE_BYTES = 3072
READ_FILE_MAX_MCP_RESPONSE_BYTES = 8192
MAX_REQUEST_BYTES = 1024 * 1024
MAX_RECEIPT_BYTES = 3 * 1024 * 1024
WORKSPACE_CAP_BYTES = 2 * 1024 * 1024
MAX_FILE_BYTES = 262144
MAX_PROPOSED_FILES = 30
MAX_RETAINED_BYTES = 64 * 1024 * 1024
MAX_TOOL_CALLS = 64
MODEL_NAME = 'SWE-2 Max'
ROUTE_BACKEND = 'devin-tools'
ROUTE_MODEL = 'swe-2-max'

FIXED_FILES = frozenset({
    'packet.json',
    'receipt.json',
    'transport.json',
    'filing.json',
    'client-output/export.json',
    'config/config.json',
    'config/tool-presentation.json',
})
TOOL_ENTRY = re.compile(
    r'tools/([1-9][0-9]*)/(request\.json|receipt\.json|oversize-result\.json)')
RESULT_FIELDS = frozenset(
    {'ok', 'value', 'error', 'uncertain', 'observation', 'retained_sha256'})

# Re-derived, never imported: an independent verifier must not trust the
# producer's own constants. Drift here must fail verification loudly.
NATIVE_DENY = [
    'read', 'write', 'edit', 'apply_patch', 'notebook_read', 'notebook_edit',
    'grep', 'glob', 'exec', 'get_output', 'write_to_process', 'kill_shell',
    'webfetch', 'fetch', 'web_search', 'skill', 'request_scope',
    'run_subagent', 'read_subagent', 'mcp_read_resource', 'Read(/**)',
    'Write(/**)', 'Exec(*)', 'Fetch(*)',
]

TOOL_PROPERTIES = {
    'list_files': {},
    'read_file': {
        'path': {'type': 'string'},
        'offset': {'type': 'integer', 'minimum': 0},
        'limit': {'type': 'integer', 'minimum': 1, 'maximum': READ_FILE_MAX_BYTES},
    },
    'search': {'text': {'type': 'string'}},
    'write_file': {
        'path': {'type': 'string'},
        'content': {'type': 'string'},
        'expected_sha256': {'type': ['string', 'null']},
    },
    'run_command': {
        'argv': {'type': 'array', 'items': {'type': 'string'}},
        'seconds': {'type': 'integer', 'minimum': 1, 'maximum': 60},
    },
    'fetch_source': {'url': {'type': 'string'}},
}
TOOL_DESCRIPTIONS = {
    'list_files': 'List frozen workspace files, exact writable paths, and reviewed research source URLs.',
    'read_file': 'Read a bounded UTF-8 byte page from the current broker virtual workspace, including accepted write_file updates. The response includes the full-file SHA256 and byte length plus next_offset; continue only with foundry read_file.',
    'search': 'Search literal text in workspace files, returning at most 100 numbered matches.',
    'write_file': 'Persist complete text to an allowed path. Supply current SHA256, or null for a new file.',
    'run_command': 'Run argv in a disposable offline Linux copy of the current workspace. Python3, shell, git and system tools are available. Commands cannot persist edits; use write_file. No host mounts or credentials. Returns actual exit/stdout/stderr and cleanup evidence.',
    'fetch_source': 'Retrieve a reviewed, frozen public source by exact URL, including content digest. Available URLs come from list_files.',
}


def expected_permission_presentation(allowed_tools):
    """Re-derive the exact provider-facing permission bytes for a tool policy."""
    return {
        'permissions': {
            'deny': list(NATIVE_DENY),
            'allow': [f'mcp__foundry__{name}' for name in allowed_tools],
            'ask': [],
        },
        'subagents_enabled': False,
        'auto_update': False,
        'notify': 'never',
        'read_config_from': {name: False for name in ('cursor', 'windsurf', 'claude')},
    }


def expected_tool_presentation(allowed_tools):
    """Re-derive the exact bound v3 permission + MCP tool presentation."""
    tools = [{
        'name': name,
        'description': TOOL_DESCRIPTIONS[name],
        'inputSchema': {
            'type': 'object',
            'properties': TOOL_PROPERTIES[name],
            'required': (['path'] if name == 'read_file'
                         else list(TOOL_PROPERTIES[name])),
            'additionalProperties': False,
        },
    } for name in JOB_TOOLS if name in allowed_tools]
    return {
        'permission': expected_permission_presentation(allowed_tools),
        'mcp': {
            'version': PRESENTATION_VERSION,
            'protocol_version': MCP_PROTOCOL_VERSION,
            'server_info': {'name': MCP_SERVER_NAME,
                            'version': MCP_PAGED_SERVER_VERSION},
            'read_file_policy': {
                'max_content_bytes': READ_FILE_MAX_BYTES,
                'max_encoded_value_bytes': READ_FILE_MAX_VALUE_BYTES,
                'max_mcp_response_bytes': READ_FILE_MAX_MCP_RESPONSE_BYTES,
                'offset_unit': 'utf-8-bytes',
                'continuation_field': 'next_offset',
                'full_file_fields': ['file_bytes', 'sha256'],
                'workspace': 'current-broker-virtual-state',
            },
            'tools': tools,
        },
    }


def _digest64(value):
    require(type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value),
            'sha256 digest required')
    return value


def _canonical(raw, name):
    value = strict_json(raw)
    require(raw == encoded(value), f'{name}: retained JSON is not canonical')
    return value


def _paged_read(content, args):
    """Exact replica of the broker's bounded UTF-8 page computation."""
    data = content.encode()
    offset = args.get('offset', 0)
    limit = args.get('limit', READ_FILE_MAX_BYTES)
    integer(offset, 0, len(data))
    integer(limit, 1, READ_FILE_MAX_BYTES)
    try:
        data[:offset].decode('utf-8')
    except UnicodeDecodeError as exc:
        raise Refused('read_file offset must be a UTF-8 boundary') from exc
    end = min(len(data), offset + limit)
    while True:
        try:
            page = data[offset:end].decode('utf-8')
        except UnicodeDecodeError:
            end -= 1
            continue
        require(end > offset or offset == len(data),
                'read_file limit ends before next UTF-8 code point')
        value = {
            'content': page,
            'content_bytes': end - offset,
            'file_bytes': len(data),
            'next_offset': end if end < len(data) else None,
            'offset': offset,
            'sha256': digest(data),
        }
        if len(encoded(value)) <= READ_FILE_MAX_VALUE_BYTES:
            return value
        require(end > offset, 'read_file page cannot fit bounded response')
        end = offset + max(1, (end - offset) // 2)


def _read_expected(current, args):
    require(type(args) is dict and 'path' in args and
            set(args) <= {'path', 'offset', 'limit'}, 'read_file fields invalid')
    target = path(args['path'])
    require(target in current, 'file outside frozen workspace')
    return _paged_read(current[target], args)


def _search_value(current, text):
    matches = []
    for target, content in sorted(current.items()):
        for number, line in enumerate(content.splitlines(), 1):
            if text in line:
                matches.append({'path': target, 'line': number, 'text': line[:2000]})
                if len(matches) == 100:
                    return {'matches': matches, 'truncated': True}
    return {'matches': matches, 'truncated': False}


def _write_target(current, initial, writable, args):
    """Replicate every deterministic write_file precondition; None on refusal."""
    try:
        require(set(args) == {'path', 'content', 'expected_sha256'}, 'write fields')
        target = path(args['path'])
        require(target in writable, 'write outside exact allowed paths')
        require(type(args['content']) is str and
                len(args['content'].encode()) <= MAX_FILE_BYTES,
                'bounded text file required')
        old = digest(current[target].encode()) if target in current else None
        require(args['expected_sha256'] == old, 'stale write')
        candidate = {**current, target: args['content']}
        require(len(encoded(candidate)) <= WORKSPACE_CAP_BYTES,
                'workspace size exhausted')
        require(sum(initial.get(p) != content for p, content in candidate.items()
                    if p in writable) <= MAX_PROPOSED_FILES, 'proposal cap')
    except Refused:
        return None
    return target


def _command_args_valid(args):
    argv = args.get('argv')
    return (set(args) == {'argv', 'seconds'} and type(argv) is list and
            1 <= len(argv) <= 64 and
            all(type(x) is str and 0 < len(x) <= 16384 and '\0' not in x
                for x in argv) and
            type(args['seconds']) is int and 1 <= args['seconds'] <= 60)


def _answer_json(message):
    try:
        return strict_json(message.encode())
    except Refused:
        pass
    blocks = re.findall(r'```(?:json)?[ \t]*\n(.*?)```', message, re.S)
    require(len(blocks) == 1, 'ambiguous final worker answer')
    return strict_json(blocks[0].encode())


def _check_discovery(call, step, tools):
    """A retained mcp_list_tools payload must contain the bound tool list."""
    found = []
    payloads = 0

    def walk(node, depth):
        require(depth <= 8, 'discovery payload too deep')
        if type(node) is str:
            try:
                node = strict_json(node.encode())
            except Refused:
                return
        if type(node) is list:
            for item in node:
                walk(item, depth + 1)
            return
        if type(node) is not dict:
            return
        if 'tools' in node:
            require(type(node['tools']) is list,
                    'malformed discovery tools payload')
            found.append(node['tools'])
        for field in ('content', 'result', 'text', 'tool_results'):
            if field in node:
                walk(node[field], depth + 1)

    for field in ('result', 'output', 'response'):
        if field in call:
            payloads += 1
            walk(call[field], 0)
    for field in ('tool_result', 'tool_results'):
        if field in step:
            payloads += 1
            walk(step[field], 0)
    require(found or not payloads, 'discovery result missing tools')
    for value in found:
        require(value == tools,
                'mcp_list_tools discovery differs from retained presentation')


def _partition(files):
    require(type(files) is dict and files,
            'a nonempty retained file mapping is required')
    fixed = {}
    tool_dirs = {}
    for name, data in files.items():
        require(type(name) is str, 'retained file names must be strings')
        path(name)
        require(type(data) is bytes, f'{name}: retained bytes required')
        require(len(data) <= MAX_RETAINED_BYTES, f'{name}: retained file too large')
        match = TOOL_ENTRY.fullmatch(name)
        if match:
            tool_dirs.setdefault(int(match.group(1)), {})[match.group(2)] = name
        else:
            require(name in FIXED_FILES, f'extra retained file: {name}')
            fixed[name] = data
    missing = sorted(FIXED_FILES - set(fixed))
    require(not missing, 'missing retained file: ' + ','.join(missing))
    numbers = sorted(tool_dirs)
    require(numbers == list(range(1, len(numbers) + 1)),
            'tool directories must be contiguous 1..N')
    require(len(numbers) <= MAX_TOOL_CALLS, 'cumulative tool budget exceeded')
    return fixed, tool_dirs, numbers


def verify_attempt_inventory(files, expect):
    """Recompute every binding of one retained native-v3 attempt bundle.

    files maps canonical relative POSIX paths to retained bytes; expect pins
    the exact source/job/attempt/route/model identities. Raises Refused on any
    omission, reordering, duplication, drift, snapshot break, foreign/native
    tool, unknown/failed state, or authority claim. Returns a small summary.
    """
    require(type(expect) is dict, 'expected identities required')
    keys(expect, ['source_commit', 'job_id', 'attempt', 'route', 'model'])
    require(type(expect['source_commit']) is str and
            re.fullmatch(r'[0-9a-f]{40}', expect['source_commit']),
            'full source commit required')
    identifier(expect['job_id'])
    integer(expect['attempt'], 1, 10 ** 6)
    route = expect['route']
    require(type(route) is dict, 'route object required')
    require(route.get('backend') == ROUTE_BACKEND, 'exact native-v3 route required')
    require(route.get('model') == ROUTE_MODEL, 'exact route model required')
    require(type(route.get('executable')) is str and bool(route['executable']),
            'route executable required')
    _digest64(route.get('sha256'))
    require(expect['model'] == MODEL_NAME, 'SWE-2 Max identity required')

    fixed, tool_dirs, numbers = _partition(files)

    packet = _canonical(fixed['packet.json'], 'packet.json')
    keys(packet, ['job', 'plan_version', 'source_commit', 'source_inputs',
                  'dependencies', 'citation_ids',
                  PERMISSION_DIGEST_FIELD, TOOL_DIGEST_FIELD])
    require(packet['plan_version'] == 3, 'native v3 packet required')
    require(packet['source_commit'] == expect['source_commit'],
            'packet source identity')
    job = packet['job']
    keys(job, ['id', 'domain', 'kind', 'brief', 'inputs', 'depends_on',
               'allowed_paths', 'allowed_tools'])
    require(job['id'] == expect['job_id'], 'packet job identity')
    allowed = validate_allowed_tools(job)
    allowed_set = frozenset(allowed)
    writable = frozenset(job['allowed_paths'])
    for value in job['allowed_paths']:
        path(value)

    inputs = packet['source_inputs']
    require(type(inputs) is dict and set(inputs) == set(job['inputs']) and
            len(set(job['inputs'])) == len(job['inputs']),
            'source inputs differ from job inputs')
    for name, item in inputs.items():
        path(name)
        require(type(item) is dict, 'source input malformed')
        keys(item, ['content', 'sha256'])
        require(type(item['content']) is str and
                digest(item['content'].encode()) == item['sha256'],
                'source input digest')
    dependencies = packet['dependencies']
    require(type(dependencies) is dict and
            set(dependencies) == set(job['depends_on']) and
            len(set(job['depends_on'])) == len(job['depends_on']),
            'dependency set differs from job')
    for dep_id, dep in dependencies.items():
        identifier(dep_id)
        require(type(dep) is dict, 'dependency malformed')
        keys(dep, ['sha256', 'filing'])
        _digest64(dep['sha256'])
        require(type(dep['filing']) is dict and
                type(dep['filing'].get('files')) is list,
                'dependency filing files required')
        for item in dep['filing']['files']:
            require(type(item) is dict, 'dependency file malformed')
            keys(item, ['path', 'content'])
            require(type(item['content']) is str, 'dependency content required')
    expected_refs = [f'source:{name}@{inputs[name]["sha256"]}'
                     for name in job['inputs']]
    expected_refs += [f'filing:{dep}@{dependencies[dep]["sha256"]}'
                      for dep in job['depends_on']]
    require(packet['citation_ids'] == expected_refs, 'citation identity drift')

    permission_raw = fixed['config/config.json']
    presentation_raw = fixed['config/tool-presentation.json']
    permission = _canonical(permission_raw, 'config/config.json')
    presentation = _canonical(presentation_raw, 'config/tool-presentation.json')
    require(permission == expected_permission_presentation(allowed),
            'permission presentation differs from job policy')
    require(presentation == expected_tool_presentation(allowed),
            'MCP tool presentation differs from job policy')
    permission_sha256 = digest(permission_raw)
    presentation_sha256 = digest(presentation_raw)
    require(packet[PERMISSION_DIGEST_FIELD] == permission_sha256 and
            packet[TOOL_DIGEST_FIELD] == presentation_sha256,
            'packet presentation binding')

    receipt = _canonical(fixed['receipt.json'], 'receipt.json')
    transport = _canonical(fixed['transport.json'], 'transport.json')
    export_raw = fixed['client-output/export.json']
    export = strict_json(export_raw)
    filing_raw = fixed['filing.json']
    for holder_name, holder in (('receipt', receipt), ('transport', transport)):
        require(holder.get(PERMISSION_DIGEST_FIELD) == permission_sha256 and
                holder.get(TOOL_DIGEST_FIELD) == presentation_sha256,
                f'{holder_name}: retained presentation digest drift')
        require(holder.get('exit_code') == 0 and not holder.get('reason'),
                f'{holder_name}: client did not complete normally')
        require(holder.get('local_quiescent') is True,
                f'{holder_name}: local quiescence not established')
        require(holder.get('broker_errors') == [],
                f'{holder_name}: broker errors retained')
        scope = holder.get('scope')
        require(type(scope) is dict and scope.get('quiescent') is True,
                f'{holder_name}: model scope not quiescent')
        require(holder.get('export_sha256') == digest(export_raw),
                f'{holder_name}: export binding')
        require(holder.get('usage') == export.get('final_metrics'),
                f'{holder_name}: usage binding')

    initial = {name: item['content'] for name, item in inputs.items()}
    proposals = {}
    for dep in dependencies.values():
        for item in dep['filing']['files']:
            target = path(item['path'])
            require(target.startswith(('tools/', 'docs/', 'experiments/')),
                    'dependency proposal outside construction scope')
            require(target not in proposals or proposals[target] == item['content'],
                    'conflicting dependency proposals require review')
            proposals[target] = item['content']
    initial.update(proposals)
    current = dict(initial)
    expected_rows = []
    request_seq = []
    for number in numbers:
        entry = tool_dirs[number]
        require({'request.json', 'receipt.json'} <= set(entry) <=
                {'request.json', 'receipt.json', 'oversize-result.json'},
                f'tools/{number}: request/receipt required, no extras')
        request_raw = files[entry['request.json']]
        receipt_raw = files[entry['receipt.json']]
        require(len(receipt_raw) <= MAX_RECEIPT_BYTES, 'oversized tool receipt')
        request = _canonical(request_raw, entry['request.json'])
        keys(request, ['name', 'arguments', 'number', 'snapshot_sha256'])
        require(request['number'] == number,
                f'tools/{number}: request number drift')
        name = request['name']
        require(name in JOB_TOOLS, 'unknown broker tool')
        args = request['arguments']
        require(type(args) is dict and len(encoded(args)) <= MAX_REQUEST_BYTES,
                'tool arguments invalid')
        _digest64(request['snapshot_sha256'])
        require(request['snapshot_sha256'] == digest(encoded(current)),
                f'tools/{number}: pre-state snapshot drift')
        record = _canonical(receipt_raw, entry['receipt.json'])
        keys(record, ['request_sha256', 'result', 'snapshot_sha256', 'accepted'])
        require(record['request_sha256'] == digest(request_raw),
                f'tools/{number}: request binding')
        require(record['accepted'] is False, 'tool receipt claims acceptance')
        result = record['result']
        require(type(result) is dict and type(result.get('ok')) is bool and
                set(result) <= RESULT_FIELDS, 'tool result malformed')
        oversize = 'retained_sha256' in result
        if oversize:
            _digest64(result['retained_sha256'])
            require(result['ok'] is False and 'oversize-result.json' in entry and
                    digest(files[entry['oversize-result.json']]) ==
                    result['retained_sha256'], 'oversize result binding')
        else:
            require('oversize-result.json' not in entry,
                    'unreferenced oversize result')
        if name not in allowed_set:
            require(result['ok'] is False and
                    result.get('error') == 'tool not permitted for this job',
                    'denied tool receipt drift')
        elif result['ok']:
            require(set(result) == {'ok', 'value'}, 'tool result shape')
            value = result['value']
            if name == 'list_files':
                require(set(args) == set(), 'list_files arguments')
                require(type(value) is dict, 'list_files value')
                keys(value, ['files', 'writable', 'sources'])
                require(value['files'] == sorted(current) and
                        value['writable'] == sorted(writable), 'list_files drift')
                require(type(value['sources']) is list and
                        all(type(u) is str for u in value['sources']) and
                        value['sources'] == sorted(set(value['sources'])),
                        'sources shape')
            elif name == 'read_file':
                require(value == _read_expected(current, args),
                        'read_file page drift')
            elif name == 'search':
                require(set(args) == {'text'} and type(args['text']) is str and
                        1 <= len(args['text']) <= 256, 'search arguments')
                require(value == _search_value(current, args['text']),
                        'search result drift')
            elif name == 'write_file':
                target = _write_target(current, initial, writable, args)
                require(target is not None,
                        'successful write violates broker preconditions')
                require(value == {'path': target,
                                  'sha256': digest(args['content'].encode())},
                        'write_file value drift')
                current[target] = args['content']
            elif name == 'run_command':
                require(_command_args_valid(args), 'run_command arguments')
                require(type(value) is dict and
                        value.get('local_quiescent') is True and
                        type(value.get('isolation')) is dict and
                        value['isolation'].get('quiescent') is True,
                        'run_command quiescence')
                require(value.get('exit_code') is None or
                        type(value['exit_code']) is int, 'exit code shape')
                require(type(value.get('stdout')) is str and
                        type(value.get('stderr')) is str, 'output shape')
            elif name == 'fetch_source':
                require(set(args) == {'url'} and type(args['url']) is str,
                        'fetch_source arguments')
                require(type(value) is dict, 'fetch_source value')
                keys(value, ['content', 'sha256', 'retrieved_utc'])
                require(type(value['content']) is str and
                        digest(value['content'].encode()) == value['sha256'],
                        'source digest')
            else:
                require(False, 'unsupported tool')
        else:
            require(type(result.get('error')) is str and result['error'],
                    'tool error required')
            if not oversize:
                if name == 'write_file':
                    require(_write_target(current, initial, writable, args) is None,
                            'failed write had valid preconditions')
                elif name == 'read_file':
                    try:
                        _read_expected(current, args)
                    except Refused:
                        pass
                    else:
                        require(False,
                                'failed read_file had valid preconditions')
                elif name == 'list_files':
                    require(set(args) != set(), 'list_files cannot fail')
                elif name == 'search':
                    require(not (set(args) == {'text'} and
                                 type(args['text']) is str and
                                 1 <= len(args['text']) <= 256),
                            'search cannot fail')
        require(result.get('uncertain') in (None, False),
                'uncertain tool outcome cannot verify a returned attempt')
        _digest64(record['snapshot_sha256'])
        require(record['snapshot_sha256'] == digest(encoded(current)),
                f'tools/{number}: post-state snapshot drift')
        expected_rows.append({'number': number, 'sha256': digest(receipt_raw),
                              'name': name})
        request_seq.append(encoded({'name': name, 'arguments': args}))

    require(receipt.get('tool_receipts') == expected_rows and
            transport.get('tool_receipts') == expected_rows,
            'receipt/transport tool inventory drift')
    for holder_name, holder in (('receipt', receipt), ('transport', transport)):
        require(holder.get('tools_used') == [r['name'] for r in expected_rows],
                f'{holder_name}: tools_used drift')
    require(receipt.get('job') == job['id'] and
            receipt.get('attempt') == expect['attempt'], 'receipt identity')
    require(receipt.get('state') == 'returned', 'attempt is not returned')
    require(receipt.get('accepted') is False, 'receipt claims acceptance')
    require(receipt.get('launch_entered') is True, 'launch not entered')
    require(receipt.get('route') == route, 'receipt route drift')
    require(not receipt.get('error'), 'attempt error retained')
    require(receipt.get('packet_sha256') == digest(fixed['packet.json']),
            'packet binding')
    require(receipt.get('transport_sha256') == digest(fixed['transport.json']),
            'transport binding')
    require(receipt.get('filing_sha256') == digest(filing_raw), 'filing binding')
    require(type(receipt.get('started')) is str and
            type(receipt.get('ended')) is str, 'attempt times required')

    require(type(export) is dict and type(export.get('agent')) is dict,
            'export object required')
    require(export['agent'].get('model_name') == expect['model'],
            'provider model identity')
    steps = export.get('steps')
    require(type(steps) is list, 'export steps required')
    calls = []
    answers = []
    presentation_tools = presentation['mcp']['tools']
    for step in steps:
        require(type(step) is dict, 'export step malformed')
        if step.get('source') == 'agent':
            require(step.get('model_name') in {'swe-2-max', MODEL_NAME},
                    'worker step model changed')
            if step.get('message'):
                require(type(step['message']) is str, 'worker message malformed')
                answers.append(step['message'])
        tool_calls = step.get('tool_calls')
        require(tool_calls is None or type(tool_calls) is list,
                'tool_calls malformed')
        for call in tool_calls or []:
            require(type(call) is dict, 'tool call malformed')
            cargs = call.get('arguments')
            require(type(cargs) is dict and cargs.get('server_name') == 'foundry',
                    'foreign/native tool attempted')
            function = call.get('function_name')
            if function == 'mcp_list_tools':
                require(set(cargs) == {'server_name'}, 'unexpected discovery scope')
                _check_discovery(call, step, presentation_tools)
                continue
            require(function == 'mcp_call_tool' and
                    set(cargs) == {'server_name', 'tool_name', 'arguments'} and
                    cargs['tool_name'] in JOB_TOOLS and
                    type(cargs['arguments']) is dict,
                    'unqualified tool attempted')
            calls.append(encoded({'name': cargs['tool_name'],
                                  'arguments': cargs['arguments']}))
    require(calls == request_seq,
            'ordered provider tool calls differ from broker requests')

    require(answers, 'missing final worker answer')
    answer = _answer_json(answers[-1])
    require(type(answer) is dict and answer.get('files') == [],
            'worker files channel must be empty')
    proposed = [{'path': name, 'content': content}
                for name, content in sorted(current.items())
                if name in writable and initial.get(name) != content]
    candidate = dict(answer, files=proposed)
    require(encoded(candidate) == filing_raw,
            'filing differs from independently collected proposals')
    refs = list(packet['citation_ids']) + [
        f"tool:{row['number']}@{row['sha256']}" for row in expected_rows]
    validate_filing(candidate, job, refs)
    return {'job': job['id'], 'attempt': expect['attempt'],
            'tool_calls': len(expected_rows),
            'proposed_files': [item['path'] for item in proposed],
            'filing_sha256': digest(filing_raw)}

"""Credential-free construction tools. Model arguments never select host paths."""
from __future__ import annotations

import contextlib
import sys
import tempfile
import time
from pathlib import Path

from .contracts import (
    Refused,
    digest,
    encoded,
    integer,
    keys,
    path,
    require,
    strict_json,
)
from .ledger import controller_lock
from .process import execute
from .runner import put
from .sandbox import bwrap_argv

TOOL_NAMES = ('list_files', 'read_file', 'search', 'write_file', 'run_command', 'fetch_source')
MAX_BYTES = 1024 * 1024


class ToolUncertain(Refused):
    def __init__(self, observation):
        super().__init__('tool cleanup unknown; reservation retained')
        self.observation = observation


@contextlib.contextmanager
def tool_scope(stop, seconds):
    """Four machine-wide slots. An abandoned cgroup retains its particular slot."""
    require(sys.platform == 'linux', 'tool execution requires Linux')
    pool = Path('/run/recursion-foundry-tools')
    pool.mkdir(exist_ok=True, mode=0o700)
    end = time.monotonic() + seconds
    stack = contextlib.ExitStack()
    group = None
    while group is None:
        require(not stop() and time.monotonic() < end, 'tool queue cancelled/expired')
        for index in range(4):
            slot = pool / str(index)
            slot.mkdir(exist_ok=True)
            candidate = Path('/sys/fs/cgroup') / f'recursion-foundry-tool-{index}'
            try:
                stack.enter_context(controller_lock(slot))
            except Refused:
                continue
            if candidate.exists():
                stack.close()
                continue
            group = candidate
            break
        if group is None:
            time.sleep(.05)
    observation = {'path': str(group), 'quiescent': False, 'cleanup_error': None,
                   'started_unix': time.time()}
    try:
        group.mkdir()
        for name, value in [('memory.max', '2147483648'), ('memory.swap.max', '0'),
                            ('pids.max', '64'), ('cpu.max', '200000 100000')]:
            (group / name).write_text(value)
            require((group / name).read_text().strip() == value, 'tool resource limit not enforced')
        require((group / 'cgroup.kill').exists(), 'cgroup kill unavailable')
        yield group, observation
    finally:
        try:
            (group / 'cgroup.kill').write_text('1')
            until = time.monotonic() + 5
            while 'populated 1' in (group / 'cgroup.events').read_text() and time.monotonic() < until:
                time.sleep(.025)
            require('populated 0' in (group / 'cgroup.events').read_text(), 'tool descendants remain')
            observation['memory_peak'] = int((group / 'memory.peak').read_text())
            group.rmdir()
            observation['quiescent'] = True
        except (OSError, Refused) as exc:
            observation['cleanup_error'] = str(exc)
        observation['ended_unix'] = time.time()
        stack.close()


def run_command(files, argv, seconds, stop=lambda: False):
    require(type(argv) is list and 1 <= len(argv) <= 64 and
            all(type(x) is str and 0 < len(x) <= 16384 and '\0' not in x for x in argv), 'bounded argv required')
    integer(seconds, 1, 60)
    # Tools have ephemeral scratch. Persistent source changes use write_file so
    # arbitrary commands cannot forge the trusted workspace or its receipts.
    with tempfile.TemporaryDirectory(prefix='recursion-foundry-source-') as temporary:
        source = Path(temporary)
        for name, content in files.items():
            target = source / path(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            put(target, content.encode())
        entry = 'foundry_command_gate.py'
        require(entry not in files, 'reserved gate path')
        script = ('import os,shutil,subprocess,sys\n'
                  'shutil.copytree("/src", "/work/repo")\n'
                  'os.chdir("/work/repo")\n'
                  f'raise SystemExit(subprocess.call({argv!r}))\n')
        put(source / entry, script.encode())
        with tool_scope(stop, seconds + 120) as (group, observation):
            wrapper = ('import os,sys; from pathlib import Path; '
                       'Path(sys.argv[1]).write_text(str(os.getpid())); '
                       'os.execv(sys.argv[2],sys.argv[2:])')
            command = ['/usr/bin/python3', '-I', '-c', wrapper, str(group / 'cgroup.procs'),
                       *bwrap_argv(source, entry, seconds, MAX_BYTES)]
            try:
                result = execute(command, source, {}, seconds, MAX_BYTES, stop)
            except Exception as exc:  # noqa: BLE001 -- retain scope cleanup on every transport failure
                result = {'exit_code': None, 'reason': 'transport-exception',
                          'error': f'{type(exc).__name__}: {exc}', 'stdout': b'', 'stderr': b'',
                          'direct_process_exited': False, 'local_quiescent': False}
        result['isolation'] = observation
        result['local_quiescent'] = observation['quiescent'] and result['direct_process_exited']
        for name in ['stdout', 'stderr']:
            result[name] = result[name].decode('utf-8', errors='replace')
        if not result['local_quiescent']:
            raise ToolUncertain(result)
        return result


class Broker:
    def __init__(self, root, files, allowed_paths, sources, max_calls=64, seconds=60, stop=lambda: False):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=False)
        self.files = dict(files)
        self.allowed = set(allowed_paths)
        self.sources = sources  # Frozen, already fetched source bytes, no model-selected network access.
        self.max_calls = max_calls
        self.seconds = seconds
        self.stop = stop
        self.count = 0
        self.uncertain = False
        self.receipts = []
        self.initial = dict(files)

    def call(self, name, args):
        require(not self.stop(), 'worker stopped')
        require(not self.uncertain, 'previous tool outcome uncertain')
        require(self.count < self.max_calls, 'cumulative tool budget exhausted')
        require(name in TOOL_NAMES, 'unknown tool')
        require(type(args) is dict, 'tool arguments must be a JSON object')
        require(len(encoded(args)) <= MAX_BYTES, 'oversized tool request')
        self.count += 1
        directory = self.root / str(self.count)
        directory.mkdir()
        request = {'name': name, 'arguments': args, 'number': self.count,
                   'snapshot_sha256': digest(encoded(self.files))}
        put(directory / 'request.json', encoded(request))
        self.uncertain = True
        try:
            value = self._dispatch(name, args)
            result = {'ok': True, 'value': value}
        except ToolUncertain as exc:
            result = {'ok': False, 'error': str(exc), 'uncertain': True, 'observation': exc.observation}
        except (Refused, OSError, ValueError) as exc:
            result = {'ok': False, 'error': str(exc)[:2000]}
        if len(encoded(result)) > 2 * MAX_BYTES:
            # UTF-8 -> escaped JSON can expand stdout by 6x. This is a known
            # output-limit failure, not lost execution/cleanup evidence.
            raw = encoded(result)
            put(directory / 'oversize-result.json', raw)
            result = {'ok': False, 'error': 'encoded tool output exceeds response cap; request smaller output',
                      'retained_sha256': digest(raw), 'uncertain': result.get('uncertain', False)}
        receipt = {'request_sha256': digest(encoded(request)), 'result': result,
                   'snapshot_sha256': digest(encoded(self.files)), 'accepted': False}
        data = encoded(receipt)
        require(len(data) <= 3 * MAX_BYTES, 'oversized tool receipt')
        put(directory / 'receipt.json', data)
        self.receipts.append({'number': self.count, 'sha256': digest(data), 'name': name})
        self.uncertain = result.get('uncertain', False)
        return {**result, 'receipt': f'tool:{self.count}@{digest(data)}'}

    def _dispatch(self, name, args):
        if name == 'list_files':
            keys(args, [])
            return {'files': sorted(self.files), 'writable': sorted(self.allowed), 'sources': sorted(self.sources)}
        if name == 'read_file':
            keys(args, ['path'])
            target = path(args['path'])
            require(target in self.files, 'file outside frozen workspace')
            return {'content': self.files[target], 'sha256': digest(self.files[target].encode())}
        if name == 'search':
            keys(args, ['text'])
            require(type(args['text']) is str and 1 <= len(args['text']) <= 256, 'bounded literal search')
            matches = []
            for target, content in sorted(self.files.items()):
                for number, line in enumerate(content.splitlines(), 1):
                    if args['text'] in line:
                        matches.append({'path': target, 'line': number, 'text': line[:2000]})
                        if len(matches) == 100:
                            return {'matches': matches, 'truncated': True}
            return {'matches': matches, 'truncated': False}
        if name == 'write_file':
            keys(args, ['path', 'content', 'expected_sha256'])
            target = path(args['path'])
            require(target in self.allowed, 'write outside exact allowed paths')
            require(type(args['content']) is str and len(args['content'].encode()) <= 262144, 'bounded text file required')
            old = digest(self.files[target].encode()) if target in self.files else None
            require(args['expected_sha256'] == old, 'stale write: read latest file first')
            candidate = {**self.files, target: args['content']}
            require(len(encoded(candidate)) <= 2 * MAX_BYTES, 'workspace size exhausted')
            require(sum(self.initial.get(p) != content for p, content in candidate.items() if p in self.allowed) <= 30,
                    'at most 30 changed files can be proposed')
            self.files = candidate
            return {'path': target, 'sha256': digest(args['content'].encode())}
        if name == 'run_command':
            keys(args, ['argv', 'seconds'])
            integer(args['seconds'], 1, self.seconds)
            return run_command(self.files, args['argv'], args['seconds'], self.stop)
        if name == 'fetch_source':
            keys(args, ['url'])
            require(type(args['url']) is str and args['url'] in self.sources, 'source URL not in reviewed corpus')
            return self.sources[args['url']]
        raise Refused('unsupported tool')

    def proposed_files(self):
        return [{'path': name, 'content': content} for name, content in sorted(self.files.items())
                if name in self.allowed and self.initial.get(name) != content]


def definitions():
    properties = {
        'list_files': {}, 'read_file': {'path': {'type': 'string'}},
        'search': {'text': {'type': 'string'}},
        'write_file': {'path': {'type': 'string'}, 'content': {'type': 'string'},
                       'expected_sha256': {'type': ['string', 'null']}},
        'run_command': {'argv': {'type': 'array', 'items': {'type': 'string'}},
                        'seconds': {'type': 'integer', 'minimum': 1, 'maximum': 60}},
        'fetch_source': {'url': {'type': 'string'}},
    }
    descriptions = {
        'list_files': 'List frozen workspace files, exact writable paths, and reviewed research source URLs.',
        'read_file': 'Read a workspace text file and its SHA256.',
        'search': 'Search literal text in workspace files, returning at most 100 numbered matches.',
        'write_file': 'Persist complete text to an allowed path. Supply current SHA256, or null for a new file.',
        'run_command': 'Run argv in a disposable offline Linux copy of the current workspace. Python3, shell, git and system tools are available. Commands cannot persist edits; use write_file. No host mounts or credentials. Returns actual exit/stdout/stderr and cleanup evidence.',
        'fetch_source': 'Retrieve a reviewed, frozen public source by exact URL, including content digest. Available URLs come from list_files.',
    }
    return [{'name': name, 'description': descriptions[name], 'inputSchema': {
        'type': 'object', 'properties': properties[name], 'required': list(properties[name]),
        'additionalProperties': False}} for name in TOOL_NAMES]


def serve_connection(connection, broker):
    """MCP newline JSON-RPC; one owner/connection, no HTTP or discovery beyond tools."""
    with connection.makefile('rwb', buffering=0) as stream:
        while line := stream.readline(MAX_BYTES + 1):
            require(len(line) <= MAX_BYTES and line.endswith(b'\n'), 'oversized MCP frame')
            message = strict_json(line)
            if 'id' not in message:
                continue
            response = {'jsonrpc': '2.0', 'id': message['id']}
            method = message.get('method')
            if method == 'initialize':
                response['result'] = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}},
                                      'serverInfo': {'name': 'recursion-foundry', 'version': '1'}}
            elif method == 'ping':
                response['result'] = {}
            elif method == 'tools/list':
                response['result'] = {'tools': definitions()}
            elif method == 'tools/call':
                try:
                    params = message['params']
                    value = broker.call(params['name'], params.get('arguments', {}))
                except (Refused, KeyError, TypeError) as exc:
                    value = {'ok': False, 'error': str(exc)}
                response['result'] = {'content': [{'type': 'text', 'text': encoded(value).decode()}],
                                      'isError': not value['ok']}
            else:
                response['error'] = {'code': -32601, 'message': 'Method unavailable'}
            connection.sendall(encoded(response) + b'\n')

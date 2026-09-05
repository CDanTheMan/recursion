"""Local documentation gate. No model, provider, network, or runtime implementation.

Run twice on the same clean commit. Receipts are stdout, never self-committed.
Only the existing inert regression entrypoints are executed. Python bytecode is disabled.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
AREA = ROOT / 'docs/v3/foundation-research'
START = 'f28f620644115b7d14eeab32f3f2d192034dd8ea'
MERGED = 'a7cd9458d37f3090079930bf8d79ffd77c4f73e4'
BRANCH = 'codex/v3-formal-model-experiment'
CAMPAIGN = 'recursion.v3.foundation.research.20260905'
CANONICAL = set(('README PRODUCT ARCHITECTURE EXECUTIVES EXECUTION-FABRIC PLANNING CLI '
                 'TERMINAL-RUNTIME INTERACTION-SURFACES CONTEXT PLUGINS-AND-EDITIONS SECURITY '
                 'TELEMETRY PERFORMANCE-PLAN ACCEPTANCE ROADMAP CONSTRUCTION-RUNBOOK '
                 'DECISION-REGISTER CLAIM-LEDGER SOURCE-REGISTER ROUTE-CAPABILITIES '
                 'RESEARCH-HYPOTHESES').split())
ALLOWED = {'docs/v3/' + n + '.md' for n in CANONICAL} | {'docs/v3/CLAIM-REGISTRY.json'}
REQUIRED = {'campaign.md', 'synthesis.md', 'evidence.json', 'compatibility.json',
            'experiments.json', 'decisions.json', 'grillme.md', 'check.py', 'validation-manifest.json'}
CLASSIFICATIONS = {'prerequisite', 'accommodation', 'later-experiment', 'deferred', 'rejected', 'already-specified'}
KINDS = {'repository-fact', 'verified-external-mechanism', 'Owner-preference', 'anecdote',
         'inference', 'hypothesis', 'proposal', 'unavailable-evidence', 'Owner-decision'}
CAPS = ('streaming turns queued_input active_steering questions approvals pre_effect tools '
        'commands subagents resume fork interrupt compaction usage process_ownership recovery').split()
THOUGHTS = {
    'a': 'developer casual enterprise adoption one-product deployment-domains enterprise-needs lucas-first',
    'b': 'opencode ranking deepseek t3 cursor hermes-efficiency original-directions grok meta',
    'c': 'modes claude-layer billing matrix namespaces adapter-types degraded effect-control cancel updates defaults-drift',
    'd': 'tiers capacity capsule coordination rejection reasoning',
    'e': 'discount prefix ttl heartbeat counterfactuals total-cost counters stale-results',
    'f': 'lag resources attribution gpu presets setup credentials visible',
    'g': 'hosts windows cursor-start operations orchestration transfer partitions migration',
    'h': 'lifecycle roles escalation fleet baselines review triggers actors',
}
EXPECTED_THOUGHTS = {'thought.' + group + '.' + name for group, names in THOUGHTS.items() for name in names.split()}
DECISIONS = ('model-boundary engine-floor authentication setup context-policy remote-scope '
             'escalation updates plugin-bridge audience-validation').split()
EXPERIMENTS = 'compaction cache delegation resources adapter remote setup updates'.split()
ROUTES = 'native codex claude-sdk claude-binary gemini opencode hermes cursor-local cursor-cloud cursor-remote cursor-machines grok meta terminal'.split()
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def closed(obj, fields, label):
    require(type(obj) is dict and set(obj) == set(fields.split()), label + ': closed fields differ')


def record(obj, fields, label, lists='', nullable='', numbers='', booleans=''):
    closed(obj, fields, label)
    for key, value in obj.items():
        if key in nullable.split() and value is None:
            continue
        if key in lists.split():
            require(type(value) is list and all(type(x) is str and x.strip() for x in value), label + ': string list ' + key)
        elif key in numbers.split():
            require(type(value) in (int, float) and math.isfinite(value) and value >= 0, label + ': number ' + key)
        elif key in booleans.split():
            require(type(value) is bool, label + ': boolean ' + key)
        else:
            require(type(value) is str and bool(value.strip()), label + ': nonempty string ' + key)


def unique(rows, label, key='id'):
    require(type(rows) is list and rows, label + ': nonempty list')
    ids = [r[key] for r in rows]
    require(len(ids) == len(set(ids)), label + ': duplicate ID')
    return set(ids)


def strict_json(text):
    def pairs(items):
        result = {}
        for k, v in items:
            require(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    def constant(value):
        raise ValueError('nonfinite JSON value: ' + value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def read(name):
    return strict_json((AREA / name).read_text(encoding='utf-8'))


def git(*args, binary=False):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    require(result.returncode == 0, 'git command failed: ' + ' '.join(args))
    return result.stdout if binary else result.stdout.decode('utf-8').strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def allowed(path):
    return path in ALLOWED or path.startswith('docs/v3/foundation-research/')


def slug_set(path):
    counts, result = {}, set()
    for line in path.read_text(encoding='utf-8').splitlines():
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not match:
            continue
        title = re.sub(r'<[^>]+>', '', match[1].lower())
        title = ''.join(c for c in title if c.isalnum() or c.isspace() or c in '_-')
        title = re.sub(r'\s', '-', title)
        count = counts.get(title, 0)
        result.add(title + ('-' + str(count) if count else ''))
        counts[title] = count + 1
    return result


def path_ref(ref, origin=ROOT):
    path, _, fragment = ref.partition('#')
    require(not re.match(r'^[A-Za-z]:|^[/\\]', path), 'absolute repository reference')
    target = (origin / unquote(path)).resolve() if path else origin
    require(target.is_relative_to(ROOT) and target.is_file(), 'missing/outside repository reference: ' + ref)
    if fragment and target.suffix == '.md':
        require(unquote(fragment) in slug_set(target), 'missing anchor: ' + ref)


def source_refs(refs, known):
    require(set(refs) <= known, 'unregistered source reference')


def data_gate(ev, co, ex, de, sources, claims):
    closed(ev, 'schema_version campaign as_of start_commit sources claims thoughts repository_records analyses fixtures benchmark searches dissent limitations', 'evidence')
    closed(co, 'schema_version campaign as_of capability_names core_contract command_bridge modes routes upgrade_policy limitations', 'compatibility')
    closed(ex, 'schema_version campaign experiments limitations', 'experiments')
    closed(de, 'schema_version campaign decisions finalization', 'decisions')
    for item in (ev, co, ex, de):
        require(type(item['schema_version']) is int and item['schema_version'] == 1, 'schema version')
        require(item['campaign'] == CAMPAIGN, 'campaign identity')
    require(ev['start_commit'] == START and ev['as_of'] == co['as_of'] == '2026-09-05', 'frozen evidence identity')
    require(set(co['capability_names']) == set(CAPS) and len(co['capability_names']) == 17, 'capability inventory')
    for root, key in ((ev, 'limitations'), (co, 'limitations'), (co, 'core_contract'), (co, 'command_bridge'), (ex, 'limitations')):
        require(type(root[key]) is list and root[key] and all(type(x) is str and x.strip() for x in root[key]), 'missing limitations/contract')
    require(type(de['finalization']) is str and 'Owner' in de['finalization'], 'finalization procedure')
    unique(ev['sources'], 'sources')
    require(unique(ev['sources'], 'source registry', 'registry_id') == {f'SRC-V3-{n:03}' for n in range(107, 139)}, 'source refresh inventory')
    for r in ev['sources']:
        record(r, 'id registry_id publisher title url version_date retrieved section sha256 status applicability contradiction revalidate', 'source', nullable='sha256')
        require(r['id'].startswith('source.foundation.') and r['status'] == 'opened', 'source provenance')
        require(r['url'].startswith('https://') and r['retrieved'] == '2026-09-05', 'source locator/date')
        require(r['sha256'] is None or HEX64.fullmatch(r['sha256']), 'source digest')
        source_refs([r['registry_id']], sources)
    dids = unique(de['decisions'], 'decisions')
    eids = unique(ex['experiments'], 'experiments')
    cids = unique(ev['claims'], 'claims')
    fids = unique(ev['fixtures'], 'fixtures')
    require(dids == {'decision.foundation.' + x for x in DECISIONS}, 'decision inventory')
    require(eids == {'experiment.foundation.' + x for x in EXPERIMENTS} and len(eids) <= 8, 'experiment inventory')
    require(cids == {f'FND-{n:03}' for n in range(1, 19)} and cids <= claims, 'claim inventory')
    require(unique(ev['thoughts'], 'thoughts') == EXPECTED_THOUGHTS, 'Owner thought coverage')
    for r in ev['claims']:
        record(r, 'id statement kind confidence classification sources repository_anchors decision experiment falsifier evidence_status contradiction recommendation', 'claim', lists='sources repository_anchors', nullable='experiment')
        require(r['kind'] in KINDS and r['classification'] in CLASSIFICATIONS, 'claim classification')
        require(r['confidence'] in {'high', 'medium', 'low'}, 'claim confidence')
        require(r['evidence_status'] in {'supported-with-limits', 'repository-verified', 'explicit-unknown'}, 'claim evidence status')
        require(r['sources'] or r['evidence_status'] in {'repository-verified', 'explicit-unknown'}, 'unsupported claim')
        require(r['decision'] in dids and (r['experiment'] is None or r['experiment'] in eids), 'claim decision/experiment edge')
        source_refs(r['sources'], sources)
        require(r['repository_anchors'], 'recommendation lacks affected contract')
        for p in r['repository_anchors']:
            path_ref(p)
    for r in ev['thoughts']:
        record(r, 'id handoff_section summary kind disposition claim decision experiment contract finding falsifier', 'thought', nullable='experiment')
        require(r['kind'] in KINDS and r['disposition'] in CLASSIFICATIONS, 'thought classification')
        require(r['handoff_section'].lower() == r['id'].split('.')[1], 'thought section')
        require(r['claim'] in cids and r['decision'] in dids and (r['experiment'] is None or r['experiment'] in eids), 'thought edges')
        path_ref(r['contract'])
    for rank, r in enumerate(de['decisions'], 1):
        record(r, 'id rank status owner_answer classification question current_rule options recommendation default_vs_configuration sources claims contracts experiments dependency red_fixtures falsifier blocked uncertainty', 'decision', lists='options sources claims contracts experiments red_fixtures', nullable='owner_answer', numbers='rank')
        require(type(r['rank']) is int and r['rank'] == rank and r['status'] == 'pending' and r['owner_answer'] is None, 'pending Owner decision/rank')
        require(r['classification'] in CLASSIFICATIONS and 2 <= len(r['options']) <= 3, 'decision options/classification')
        require(r['contracts'] and r['red_fixtures'] and r['sources'] and r['claims'], 'decision support missing')
        require(set(r['claims']) <= cids and set(r['experiments']) <= eids and set(r['red_fixtures']) <= fids, 'decision edges')
        source_refs(r['sources'], sources)
        for p in r['contracts']:
            path_ref(p)
    for r in ex['experiments']:
        record(r, 'id status question current_contract baseline_treatment unit_of_analysis matched_budgets hard_floors workload versions metrics failure_cases analysis_uncertainty stop_rule adoption_rejection required_authorization claims red_fixtures', 'experiment', lists='hard_floors claims red_fixtures')
        require(r['status'] == 'preregistered-not-run' and len(r['hard_floors']) >= 3, 'experiment status/floors')
        require(set(r['claims']) <= cids and set(r['red_fixtures']) <= fids, 'experiment edges')
        require('Exploratory' in r['analysis_uncertainty'] and 'power' in r['analysis_uncertainty'] and 'Separate Owner' in r['required_authorization'], 'experiment controls/authorization')
        path_ref(r['current_contract'])
    for r in ev['fixtures']:
        record(r, 'id status trigger expected contracts decisions experiments', 'fixture', lists='contracts decisions experiments')
        require(r['status'] == 'design-not-executed' and r['contracts'], 'fixture evidence boundary')
        require(set(r['decisions']) <= dids and set(r['experiments']) <= eids, 'fixture edges')
        for p in r['contracts']:
            path_ref(p)
    for r in ev['repository_records']:
        record(r, 'id path symbol candidate receipt schema_sha256 fixture_manifest_sha256 status', 'repository record')
        require(HEX40.fullmatch(r['candidate']) and HEX40.fullmatch(r['receipt']), 'repository commit')
        require(HEX64.fullmatch(r['schema_sha256']) and HEX64.fullmatch(r['fixture_manifest_sha256']), 'repository digest')
        path_ref(r['path'])
    for r in ev['analyses']:
        record(r, 'id sources contracts text', 'analysis', lists='sources contracts')
        source_refs(r['sources'], sources)
        for p in r['contracts']:
            path_ref(p)
    for r in ev['searches']:
        record(r, 'id queries result stop_reason', 'search', lists='queries')
    for r in ev['dissent']:
        record(r, 'id initial resolution remaining', 'dissent')
    for key in ('repository_records', 'analyses', 'searches', 'dissent'):
        unique(ev[key], key)
    b = ev['benchmark']
    closed(b, 'source methodology name version retrieved tasks aggregation rows uncertainty', 'benchmark')
    source_refs([b['source'], b['methodology']], sources)
    closed(b['tasks'], 'deep_swe terminal_bench_2_1 swe_atlas_qna total_unique attempts_per_task', 'benchmark tasks')
    require(b['tasks'] == dict(deep_swe=113, terminal_bench_2_1=89, swe_atlas_qna=124, total_unique=326, attempts_per_task=3), 'benchmark denominator')
    require(len(b['rows']) == 4 and b['uncertainty'], 'benchmark missing uncertainty')
    for r in b['rows']:
        record(r, 'harness model index reported_mean_usd version_span', 'benchmark row', numbers='index reported_mean_usd')
        require(r['index'] <= 1, 'benchmark score bound')
    require(unique(co['routes'], 'routes') == {'route.foundation.' + x for x in ROUTES}, 'route inventory')
    for r in co['routes']:
        closed(r, 'id name version interface sources auth distribution billing observation capabilities limitations admission experiment', 'route')
        for k in ('id', 'name', 'version', 'interface', 'auth', 'distribution', 'billing', 'limitations', 'admission'):
            require(type(r[k]) is str and r[k].strip(), 'route metadata ' + k)
        require(type(r['sources']) is list and r['sources'] and r['experiment'] in eids, 'route support/probe')
        source_refs(r['sources'], sources)
        if r['observation'] is not None:
            record(r['observation'], 'kind version date runtime_capabilities_observed', 'observation', booleans='runtime_capabilities_observed')
            require(r['observation']['kind'] == 'version-help-only' and r['observation']['runtime_capabilities_observed'] is False, 'forged runtime observation')
        closed(r['capabilities'], ' '.join(CAPS), 'capability row')
        for cell in r['capabilities'].values():
            record(cell, 'status detail probe', 'capability cell')
            require(cell['status'] in {'documented', 'unsupported', 'unknown', 'requiring-probe'}, 'runtime observation not admitted in this campaign')
    require(len(co['modes']) == 4, 'ownership modes')
    for r in co['modes']:
        record(r, 'mode sampling tools permissions conversation compaction lifetime recovery billing', 'ownership mode')
    return dids | eids | fids | {r['id'] for k in ('sources', 'thoughts', 'repository_records', 'analyses', 'searches', 'dissent') for r in ev[k]} | {r['id'] for r in co['routes']}


def regression_commands():
    result = []
    for lane in ('planning', 'execution', 'integrity'):
        result += [['python', '-B', f'schemas/control-plane/v3/{lane}/materialize.py', '--check'],
                   ['python', '-B', f'scripts/tests/v3/{lane}/materialize_fixtures.py', '--check']]
        if lane == 'planning':
            result.append(['python', '-B', 'scripts/tests/v3/planning/red_fixture.test.py', '--validate-only'])
        result += [['python', '-B', p.relative_to(ROOT).as_posix()] for p in sorted((ROOT / f'scripts/tests/v3/{lane}').glob('*.test.py'))]
    result.append(['python', '-B', '-u', 'scripts/tests/recursion-v2-mvp.test.py'])
    return result


def publication_gate(changed):
    patterns = {
        'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'aws': r'(?<![A-Z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])',
        'github': r'(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})',
        'slack': r'xox[baprs]-[A-Za-z0-9-]{10,}',
        'api_token': r'(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}',
        'bearer': r'(?i)\bBearer\s+[A-Za-z0-9._~+/-]{20,}={0,2}',
        'credential_assignment': r'''(?i)\b(?:api[_-]?key|client[_-]?secret|password|access[_-]?token)\s*[:=]\s*["'][^"']{8,}["']''',
        'credential_url': r'(?i)https?://[^/\s:@]+:[^/\s@]+@',
        'windows_user_path': r'(?i)\b[A-Z]:[\\/]+Users[\\/]+[^\\/\s]+',
        'unix_user_path': r'''(?i)(?:^|[\s"'])(?:/home/|/Users/)[^/\s"']+''',
        'private_canary': r'''(?i)\bprivate[-_ ]canary[-_ ](?:id|name|identity)\s*[:=]\s*["']?[^"'\s|]{3,}''',
        'private_network': r'(?<![\d.])(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?![\d.])',
    }
    for name in changed:
        text = (ROOT / name).read_text(encoding='utf-8')
        for label, pattern in patterns.items():
            require(not re.search(pattern, text), 'publication scan ' + label + ' in ' + name)


def registry_gate():
    root = ROOT / 'docs/v3'
    registry = strict_json((root / 'CLAIM-REGISTRY.json').read_text(encoding='utf-8'))
    ledger = (root / registry['canonicalLedger']).read_text(encoding='utf-8')
    rows = re.findall(r'^\| ([A-Z][A-Z0-9]*-\d{3}) \|', ledger, re.M)
    require(len(rows) == len(set(rows)), 'duplicate canonical claim row')
    expected = {f"{r['prefix']}-{n:03}" for r in registry['ranges'] for n in range(r['start'], r['end'] + 1) if n not in r['reserved']}
    require(set(rows) == expected, 'canonical claim ranges')
    source_text = (root / 'SOURCE-REGISTER.md').read_text(encoding='utf-8')
    source_rows = re.findall(r'^\| `(SRC-V3-\d{3})` \|', source_text, re.M)
    require(source_rows == [f'SRC-V3-{n:03}' for n in range(1, 139)], 'canonical source sequence')
    sources = set(source_rows)
    active = [p for p in root.rglob('*') if p.suffix in {'.md', '.json'} and 'archive' not in p.relative_to(root).parts]
    exclusions = {r['value'] for r in registry['literalExclusions']}
    for path in active:
        text = path.read_text(encoding='utf-8')
        for match in re.finditer(registry['referencePattern'], text):
            value = match[1]
            require(value in expected or value in exclusions or any(re.fullmatch(r['idPattern'], value) for r in registry['foreignRegistries']), 'unregistered claim ' + value + ' in ' + path.name)
        source_refs(re.findall(r'SRC-V3-\d{3}', text), sources)
        if path.suffix == '.md':
            prose = re.sub(r'(?ms)^```.*?^```[ \t]*\r?$', '', text)
            for ref in re.findall(r'\[[^\]]*\]\(([^)]+)\)', prose):
                ref = ref.strip().strip('<>')
                if re.match(r'^(https?|mailto|data):', ref):
                    continue
                path_ref(ref.split(' "', 1)[0], path.parent if not ref.startswith('#') else path)
    sequences = [
        ('R1-R17-EVIDENCE.md', r'^## (R\d+) —', 'R', 1, 17, 0),
        ('AUTONOMOUS-PLANNING.md', r'^\| (APQ-\d{2}) \|', 'APQ-', 1, 18, 2),
        ('M1A-AUTONOMOUS-PLANNING.md', r'^\| (F-M1A-\d{3}) \|', 'F-M1A-', 1, 23, 3),
        ('M1A-AUTONOMOUS-PLANNING.md', r'^\| (M1A-\d{2}) [^|]*\|', 'M1A-', 1, 7, 2),
        ('M1A-FIXTURE-ORACLES.md', r'^\| `(F-M1A-\d{3})` \|', 'F-M1A-', 1, 23, 3),
        ('AUTONOMOUS-PLANNING-CAMPAIGN.md', r'^\| (GATE-V3DF-\d{2}) \|', 'GATE-V3DF-', 1, 24, 2),
        ('FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md', r'^\| `(GATE-FHAR-\d{2})` \|', 'GATE-FHAR-', 1, 24, 2),
        ('FRONTIER-HARNESS-RESEARCH-TRANCHE-2.md', r'^\| `(GATE-FHAR2-\d{2})` \|', 'GATE-FHAR2-', 1, 24, 2),
        ('FRONTIER-HARNESS-RESEARCH-TRANCHE-2-EVIDENCE.md', r'^## (E-FHAR2-\d{3}) —', 'E-FHAR2-', 101, 108, 3),
        ('SOURCE-REGISTER.md', r'^\| (R\d+) \| `SRC-V3-', 'R', 1, 17, 0),
    ]
    for name, pattern, prefix, start, end, width in sequences:
        ids = re.findall(pattern, (root / name).read_text(encoding='utf-8'), re.M)
        require(ids == [prefix + str(n).zfill(width) for n in range(start, end + 1)], 'historical sequence ' + name + ' ' + prefix)
    oracle = (root / 'M1A-FIXTURE-ORACLES.md').read_text(encoding='utf-8')
    for pattern, count in [(r'^\| `([a-z][a-z0-9-]+)` \| `(?:owner|head|arm|worker|verifier|kernel-fixture-gate)', 22), (r'^\| `(E-[A-Z0-9-]+)` \|', 28)]:
        ids = re.findall(pattern, oracle, re.M)
        require(len(ids) == len(set(ids)) == count, 'M1A closed alphabet')
    frontier = (root / 'FRONTIER-HARNESS-EVIDENCE.md').read_text(encoding='utf-8')
    for title, count in [('Harness corpus and code paths', 8), ('Durable execution findings', 6), ('Context, token and cache findings', 7), ('Terminal, TUI and multi-view findings', 6)]:
        section = frontier.split('## ' + title, 1)[1].split('\n## ', 1)[0]
        rows = [line for line in section.splitlines() if line.startswith('|') and not line.startswith('|---')][1:]
        require(len(rows) == count and all(re.search(r'SRC-V3-\d{3}', r) for r in rows), 'historical source edges')
    tranche = (root / 'FRONTIER-HARNESS-RESEARCH-TRANCHE-2-EVIDENCE.md').read_text(encoding='utf-8')
    require(len(set(re.findall(r'SRC-V3-\d{3}', tranche))) >= 15, 'tranche source coverage')
    return sources, expected


def adversarial_gate(ev, co, ex, de, sources, claims):
    def rejects(fn, label):
        try:
            fn()
        except (ValueError, TypeError, KeyError):
            return
        raise ValueError('gate accepted adversarial mutation: ' + label)
    rejects(lambda: strict_json('{"a":1,"a":2}'), 'duplicate JSON')
    rejects(lambda: strict_json('{"a":NaN}'), 'nonfinite JSON')
    cases = []
    x = copy.deepcopy(ev); x['thoughts'].pop(); cases.append((x, co, ex, de, 'missing thought'))
    x = copy.deepcopy(ev); x['claims'][0]['extra'] = True; cases.append((x, co, ex, de, 'unknown claim field'))
    x = copy.deepcopy(ev); x['claims'][0]['decision'] = 'decision.foundation.missing'; cases.append((x, co, ex, de, 'missing edge'))
    x = copy.deepcopy(ev); x['claims'][0]['repository_anchors'] = []; cases.append((x, co, ex, de, 'missing contract'))
    x = copy.deepcopy(co); x['routes'][0]['capabilities']['usage']['status'] = 'observed'; cases.append((ev, x, ex, de, 'false observation'))
    x = copy.deepcopy(de); x['decisions'][0]['owner_answer'] = 'inferred'; cases.append((ev, co, ex, x, 'invented Owner answer'))
    x = copy.deepcopy(ex); x['experiments'][0]['hard_floors'] = []; cases.append((ev, co, x, de, 'missing experiment floor'))
    for a, b, c, d, label in cases:
        rejects(lambda: data_gate(a, b, c, d, sources, claims), label)
    print('ADVERSARIAL_GATE_PASS mutations=9', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    require(args.base == START and HEX40.fullmatch(args.candidate), 'full frozen base/candidate required')
    require(ROOT.name == 'recursion-v3-formal-model-20260904', 'wrong dedicated worktree')
    require(git('branch', '--show-current') == BRANCH, 'wrong branch')
    require(git('rev-parse', 'HEAD') == args.candidate, 'candidate differs from HEAD')
    require(not git('status', '--porcelain'), 'candidate worktree is dirty')
    git('merge-base', '--is-ancestor', START, args.candidate)
    git('merge-base', '--is-ancestor', MERGED, args.candidate)
    entries = git('worktree', 'list', '--porcelain').split('\n\n')
    owners = [e for e in entries if 'branch refs/heads/' + BRANCH in e.splitlines()]
    require(len(owners) == 1 and Path(owners[0].splitlines()[0][9:]).resolve() == ROOT, 'worktree registration/ownership')
    changed = git('diff', '--name-only', '--no-renames', START, args.candidate).splitlines()
    require(changed and all(allowed(p) for p in changed), 'complete diff outside allowlist')
    require(all(line[0] in 'AM' for line in git('diff', '--name-status', '--no-renames', START, args.candidate).splitlines()), 'unexpected deletion/rename/type change')
    git('diff', '--check', START, args.candidate)
    require(all((AREA / n).is_file() for n in REQUIRED), 'required artifact missing')
    print('candidate=' + args.candidate, flush=True)
    sources, claims = registry_gate()
    ev, co, ex, de = (read(n) for n in ('evidence.json', 'compatibility.json', 'experiments.json', 'decisions.json'))
    ids = data_gate(ev, co, ex, de, sources, claims)
    for lane, r in zip(('planning', 'execution', 'integrity'), ev['repository_records']):
        for commit in (r['candidate'], r['receipt']):
            git('merge-base', '--is-ancestor', commit, args.candidate)
        for prefix in ('schemas/control-plane/v3/', 'scripts/v3/', 'scripts/tests/v3/'):
            require(not git('diff', '--name-only', r['candidate'], args.candidate, '--', prefix + lane), 'M1 candidate bytes changed')
        for path, key in [(ROOT / 'schemas/control-plane/v3' / lane / 'schema.json', 'schema_sha256'),
                          (ROOT / 'scripts/tests/v3' / lane / 'fixtures/manifest.json', 'fixture_manifest_sha256')]:
            require(sha(path.read_bytes()) == r[key], 'M1 schema/fixture manifest byte digest changed')
    grill = (AREA / 'grillme.md').read_text(encoding='utf-8')
    require(len(re.findall(r'^## \d+\.', grill, re.M)) == 10 and grill.count('Owner answer: **pending**') == 10, 'GRILLME pending count')
    require(len((AREA / 'synthesis.md').read_text(encoding='utf-8').split()) <= 2500, 'synthesis word cap')
    for name in changed:
        if name.endswith(('.md', '.json')):
            text = (ROOT / name).read_text(encoding='utf-8')
            for ref in re.findall(r'\b(?:decision|experiment|thought|source|analysis|fixture|route|repository|search|dissent)\.(?:foundation|[a-h])\.[a-z0-9]+(?:[.-][a-z0-9]+)*', text):
                require(ref in ids, 'unresolved campaign reference: ' + ref)
    for r in ev['sources']:
        require(r['url'] in (ROOT / 'docs/v3/SOURCE-REGISTER.md').read_text(encoding='utf-8'), 'source URL registry drift')
    for r in ev['claims']:
        require(r['statement'] in (ROOT / 'docs/v3/CLAIM-LEDGER.md').read_text(encoding='utf-8'), 'claim statement registry drift')
    publication_gate(changed)
    adversarial_gate(ev, co, ex, de, sources, claims)
    manifest = read('validation-manifest.json')
    closed(manifest, 'schema_version campaign base baseline_runs artifacts limitations', 'manifest')
    require(manifest['schema_version'] == 1 and manifest['campaign'] == CAMPAIGN and manifest['base'] == START and manifest['limitations'], 'manifest identity/limits')
    artifact_rows = manifest['artifacts']
    require(unique(artifact_rows, 'artifact manifest', 'path') == set(changed) - {'docs/v3/foundation-research/validation-manifest.json'}, 'manifest complete candidate diff')
    for r in artifact_rows:
        record(r, 'path git_blob_sha256', 'artifact manifest row')
        require(HEX64.fullmatch(r['git_blob_sha256']) and sha(git('show', args.candidate + ':' + r['path'], binary=True)) == r['git_blob_sha256'], 'artifact digest mismatch: ' + r['path'])
    commands = regression_commands()
    expected_baseline = {tuple(c) for c in commands if '--validate-only' not in c}
    require({tuple(r['command']) for r in manifest['baseline_runs']} == expected_baseline and len(manifest['baseline_runs']) == len(expected_baseline), 'fresh baseline command inventory')
    for r in manifest['baseline_runs']:
        record(r, 'candidate command exit_code seconds output_sha256', 'baseline run', lists='command', numbers='exit_code seconds')
        require(r['candidate'] == 'c2c84fa62aa5ce682c3e701c47380c5f167d20de' and r['exit_code'] == 0 and HEX64.fullmatch(r['output_sha256']), 'baseline receipt')
    print('DOCUMENT_GATE_PASS paths=' + str(len(changed)) + ' thoughts=66 claims=18 sources=32 routes=14 cells=238 experiments=8 decisions=10', flush=True)
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONUTF8'] = '1'
    bash = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/bin'
    if os.name == 'nt' and bash.is_dir():
        env['PATH'] = str(bash) + os.pathsep + env.get('PATH', '')
    receipts = []
    for command in commands:
        result = subprocess.run([sys.executable, *command[1:]], cwd=ROOT, env=env, capture_output=True, timeout=300)
        receipt = dict(candidate=args.candidate, command=command, exit_code=result.returncode, output_sha256=sha(result.stdout + result.stderr))
        receipts.append(receipt)
        print(json.dumps(receipt, sort_keys=True), flush=True)
        require(result.returncode == 0, 'regression failure; output digest above, rerun named command for diagnostics')
    require(git('rev-parse', 'HEAD') == args.candidate and not git('status', '--porcelain'), 'candidate changed during gate')
    print('FOUNDATION_GATE_PASS candidate=' + args.candidate + ' regressions=' + str(len(receipts)) + ' receipt_sha256=' + sha(json.dumps(receipts, sort_keys=True).encode()), flush=True)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, IndexError, subprocess.TimeoutExpired) as error:
        print('FOUNDATION_GATE_FAIL: ' + str(error), file=sys.stderr, flush=True)
        sys.exit(1)

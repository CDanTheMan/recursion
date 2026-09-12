"""Version 3 campaign admission and evidence-bound live advisory snapshots.

Worker lifetime is the remaining campaign work window, not an inactivity guess.
Advisors cannot accept evidence, launch workers, or change the frozen plan.
"""
import threading
import time
from pathlib import Path, PurePosixPath

from .contracts import digest, encoded, integer, keys, require, strict_json, timestamp

MAX_SLOTS = 200
MAX_WORKER_SECONDS = 8 * 3600


def ceiling(plan):
    return MAX_SLOTS if plan['version'] == 3 else 100


def validate_campaign(value):
    keys(value, ['start_utc', 'hard_deadline_utc', 'closeout_reserve_seconds',
                 'quota_path', 'quota_max_age_seconds', 'quota_reserve_percent',
                 'max_supervision_dispatches', 'pause_paths', 'quota_reset_identities'])
    start, end = timestamp(value['start_utc']), timestamp(value['hard_deadline_utc'])
    require(0 < end - start <= MAX_WORKER_SECONDS, 'one finite campaign window')
    integer(value['closeout_reserve_seconds'], 600, MAX_WORKER_SECONDS - 1)
    require(start < end - value['closeout_reserve_seconds'], 'nonempty work window')
    integer(value['quota_max_age_seconds'], 60, 1800)
    integer(value['quota_reserve_percent'], 1, 99)
    integer(value['max_supervision_dispatches'], 1, 1000)
    resets = value['quota_reset_identities']
    require(type(resets) is dict and 1 <= len(resets) <= 10
            and all(type(k) is str and 1 <= len(k) <= 100 and type(v) is int and v > end
                    for k, v in resets.items()), 'fixed named included quota reset identities')
    require(type(value['quota_path']) is str and value['quota_path'].startswith(
        '/var/lib/recursion-foundry/campaigns/') and '..' not in Path(value['quota_path']).parts,
        'native campaign quota evidence path')
    require(type(value['pause_paths']) is list and 1 <= len(value['pause_paths']) <= 10
            and all(type(p) is str and PurePosixPath(p).is_absolute() and '..' not in PurePosixPath(p).parts
                    for p in value['pause_paths']), 'explicit absolute owner stop paths')
    return value


def campaign_live(plan, *, at=None):
    """Fresh checks also run in transport stop predicates; any uncertainty stops."""
    if plan['version'] != 3:
        return True
    try:
        c = validate_campaign(plan['campaign'])
        current = time.time() if at is None else at
        end = min(timestamp(plan['deadline_utc']),
                  timestamp(c['hard_deadline_utc']) - c['closeout_reserve_seconds'])
        if not timestamp(c['start_utc']) <= current < end:
            return False
        if any(Path(p).exists() for p in c['pause_paths']):
            return False
        usage = strict_json(Path(c['quota_path']).read_bytes())
        age = current - timestamp(usage['checked_utc'])
        if not 0 <= age <= c['quota_max_age_seconds']:
            return False
        windows = usage['binding_windows']
        identities = {w['name']: w['resets_at'] for w in windows}
        return (bool(windows) and len(identities) == len(windows)
                and identities == c['quota_reset_identities']
                and usage['remaining_percent'] == min(w['remaining_percent'] for w in windows)
                and all(
            type(w['used_percent']) in (int, float) and 0 <= w['used_percent'] <= 100
            and w['remaining_percent'] == 100 - w['used_percent']
            and w['remaining_percent'] > c['quota_reserve_percent']
            and current < w['resets_at'] for w in windows
        ) and usage['reset_credits_used'] == usage['new_metered_spend'] == 0)
    except (OSError, ValueError, KeyError, TypeError):
        return False


def campaign_monitor(plan):
    """One shared observation per second per controller; false is never extended."""
    mutex = threading.Lock()
    checked, value = -float('inf'), False

    def observe():
        nonlocal checked, value
        with mutex:
            current = time.monotonic()
            if not value or current - checked >= 1 or current < checked:
                value, checked = campaign_live(plan), current
            return value
    return observe


def progress_packet(root, packet):
    """Capture only complete bounded broker records; partial files remain unknown.

    This does not take the worker controller lock. Ledger report is a read-only
    transaction. Hashes bind the exact observation, not a claim of useful progress.
    """
    root = Path(root)
    packet = dict(packet, observed_unix=time.time(), advisory_only=True)
    records = []
    for row in packet['records']:
        row = dict(row)
        directory = root / 'attempts' / row['id'] / str(row['attempts']) / 'tools'
        completed, pending, excerpt, uncertain = [], 0, '', False
        paths = sorted(directory.glob('*/request.json'), key=lambda p: int(p.parent.name))
        for request in paths[:128]:
            receipt = request.with_name('receipt.json')
            try:
                require(request.stat().st_size <= 2 * 1024**2 and receipt.stat().st_size <= 2 * 1024**2,
                        'bounded progress source')
                raw_request, raw = request.read_bytes(), receipt.read_bytes()
                value = strict_json(raw)
                require(value['request_sha256'] == digest(raw_request), 'progress request binding')
                require(raw == receipt.read_bytes(), 'receipt changed during observation')
                completed.append({'number': int(request.parent.name), 'sha256': digest(raw),
                                  'tool': strict_json(raw_request)['name'],
                                  'observed_mtime_unix': receipt.stat().st_mtime})
                uncertain = uncertain or value.get('result', {}).get('uncertain') is True
                excerpt = encoded(value.get('result', {})).decode()[:1200]
            except (OSError, ValueError, KeyError, TypeError):
                pending += 1
        progress = {'completed_tools': len(completed), 'pending_or_unreadable': pending,
                    'last_receipts': completed[-3:], 'last_result_excerpt': excerpt,
                    'tool_uncertainty_observed': uncertain,
                    'liveness_is_not_scientific_progress': True}
        attempt = directory.parent
        try:
            raw = (attempt/'packet.json').read_bytes()
            require(len(raw) <= 4*1024**2, 'bounded task context')
            task = strict_json(raw)
            progress['objective'] = task['job']['brief'][:2400]
            progress['packet_sha256'] = digest(raw)
            progress['observed_elapsed_seconds'] = max(0, time.time() - (attempt/'packet.json').stat().st_mtime)
        except (OSError, ValueError, KeyError, TypeError):
            progress['task_context_unavailable'] = True
        row['progress'] = progress
        row['progress_ref'] = 'progress:' + row['id'] + '@' + digest(encoded(progress))
        records.append(row)
    packet['records'] = records
    require(len(encoded(packet)) <= 96000, 'bounded live coordinator packet')
    return packet


def validate_advice(value, packet):
    keys(value, ['summary', 'assessments'])
    require(type(value['summary']) is str and 1 <= len(value['summary']) <= 8000,
            'bounded live summary')
    require(type(value['assessments']) is list, 'live assessments')
    expected = {r['id']: r for r in packet['records']}
    seen = set()
    for item in value['assessments']:
        keys(item, ['id', 'disposition', 'reason', 'evidence'])
        require(item['id'] in expected and item['id'] not in seen, 'exact live worker coverage')
        seen.add(item['id'])
        require(item['disposition'] in {'continue', 'inspect', 'stop_for_review'},
                'advisory only, no acceptance or dispatch')
        require(type(item['reason']) is str and 1 <= len(item['reason']) <= 4000,
                'bounded live reason')
        row = expected[item['id']]
        refs = [row['progress_ref']] + ([row['filing_ref']] if 'filing_ref' in row else [])
        require(item['evidence'] == refs, 'exact snapshot and filing references')
        if (row['state'] in {'unknown', 'failed', 'blocked'} or 'artifact_error' in row
                or row['progress']['tool_uncertainty_observed']):
            require(item['disposition'] == 'stop_for_review', 'uncertainty cannot advance')
    require(seen == set(expected), 'complete live coverage')
    return value

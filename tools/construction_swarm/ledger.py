"""Single trusted controller; durable reservations precede launch.

SQLite is temporary construction tooling, not a Recursion product-store decision.
All commands take an OS lock. Workers never receive this database or its directory.
"""
from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path
import sqlite3
import time

from .contracts import Refused, digest, encoded, now, require, strict_json, timestamp


@contextlib.contextmanager
def controller_lock(root):
    root = Path(root).resolve(strict=True)
    filename = root / "controller.lock"
    require(not filename.is_symlink(), "symlink lock")
    with filename.open("a+b") as handle:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            if filename.stat().st_size == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise Refused("another controller owns this run") from exc
        else:
            import fcntl
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise Refused("another controller owns this run") from exc
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


class Ledger:
    def __init__(self, root):
        self.root = Path(root).resolve(strict=True)
        require(not (self.root / 'ledger.sqlite').is_symlink(), 'symlink database')
        self.db = sqlite3.connect(self.root / "ledger.sqlite", timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, spec TEXT NOT NULL, state TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0, result_hash TEXT);
            CREATE TABLE IF NOT EXISTS attempts (
                job TEXT NOT NULL, number INTEGER NOT NULL, state TEXT NOT NULL,
                started TEXT NOT NULL, ended TEXT, receipt TEXT,
                PRIMARY KEY(job, number));
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY, at TEXT NOT NULL, event TEXT NOT NULL,
                detail TEXT NOT NULL);
        ''')

    def close(self):
        self.db.close()

    @classmethod
    def readonly(cls, root):
        self = cls.__new__(cls)
        self.root = Path(root).resolve(strict=True)
        require((self.root / 'ledger.sqlite').is_file(), 'run missing')
        self.db = sqlite3.connect((self.root / 'ledger.sqlite').as_uri() + '?mode=ro', uri=True)
        self.db.row_factory = sqlite3.Row
        self.db.execute('BEGIN')
        return self

    def event(self, event, detail):
        self.db.execute("INSERT INTO events(at,event,detail) VALUES(?,?,?)",
                        (now(), event, encoded(detail).decode()))

    def initialize(self, plan):
        require(not self.db.execute("SELECT 1 FROM meta").fetchone(), "run already initialized")
        with self.db:
            self.db.execute("INSERT INTO meta VALUES('plan',?)", (encoded(plan).decode(),))
            self.db.execute("INSERT INTO meta VALUES('plan_hash',?)", (digest(encoded(plan)),))
            for job in plan['jobs']:
                self.db.execute("INSERT INTO jobs(id,spec,state) VALUES(?,?,'queued')",
                                (job['id'], encoded(job).decode()))
            self.event('initialized', {'run_id': plan['run_id'], 'plan_hash': digest(encoded(plan))})

    @property
    def plan(self):
        row = self.db.execute("SELECT value FROM meta WHERE key='plan'").fetchone()
        require(row is not None, 'run not initialized')
        plan = strict_json(row[0].encode())
        expected = self.db.execute("SELECT value FROM meta WHERE key='plan_hash'").fetchone()[0]
        require(digest(encoded(plan)) == expected, 'plan digest mismatch')
        return plan

    def rows(self):
        return [dict(r) for r in self.db.execute('SELECT * FROM jobs ORDER BY id')]

    def recover(self):
        # The caller owns the controller lock. Nothing is re-launched or refunded.
        with self.db:
            running = [r[0] for r in self.db.execute("SELECT id FROM jobs WHERE state='running'")]
            self.db.execute("UPDATE jobs SET state='unknown' WHERE state='running'")
            self.db.execute("UPDATE attempts SET state='unknown' WHERE state='running'")
            if running:
                self.event('controller-loss', {'unknown_jobs': running,
                                              'reservations_retained': True})

    def reserve(self, job_id):
        plan = self.plan
        self.db.execute('BEGIN IMMEDIATE')
        try:
            require(time.time() < timestamp(plan['deadline_utc']), 'campaign deadline reached')
            require(not (self.root / 'STOP').exists(), 'STOP requested')
            rows = {r['id']: r for r in self.rows()}
            require(job_id in rows, 'unknown job')
            row = rows[job_id]
            require(row['state'] == 'queued', 'job not queued')
            spec = json.loads(row['spec'])
            require(all(rows[d]['state'] in {'returned', 'accepted'} for d in spec['depends_on']),
                    'dependency not returned')
            # Unknown outcomes retain slots and cumulative dispatch charges.
            active = [r for r in rows.values() if r['state'] in {'running', 'unknown'}]
            limits = plan['limits']
            require(len(active) < limits['model_slots'], 'model slots reserved')
            require(sum(json.loads(r['spec'])['domain'] == spec['domain'] for r in active)
                    < limits['domain_slots'], 'domain slots reserved')
            used = self.db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]
            require(used < limits['max_dispatches'], 'cumulative dispatch budget exhausted')
            number = row['attempts'] + 1
            require(number <= limits['max_attempts'], 'attempt budget exhausted')
            self.db.execute("INSERT INTO attempts VALUES(?,?,'running',?,NULL,NULL)",
                            (job_id, number, now()))
            self.db.execute("UPDATE jobs SET state='running',attempts=? WHERE id=?", (number, job_id))
            self.event('reserved', {'job': job_id, 'attempt': number})
            self.db.commit()
            return number
        except BaseException:
            self.db.rollback()
            raise

    def finish(self, job_id, number, state, receipt, result_hash=None):
        require(state in {'returned', 'failed', 'unknown', 'cancelled'}, 'invalid terminal state')
        with self.db:
            row = self.db.execute('SELECT state,attempts FROM jobs WHERE id=?', (job_id,)).fetchone()
            require(row and row['state'] == 'running' and row['attempts'] == number,
                    'stale/double settlement')
            self.db.execute('UPDATE attempts SET state=?,ended=?,receipt=? WHERE job=? AND number=?',
                            (state, now(), encoded(receipt).decode(), job_id, number))
            self.db.execute('UPDATE jobs SET state=?,result_hash=? WHERE id=?',
                            (state, result_hash, job_id))
            self.event('finished', {'job': job_id, 'attempt': number, 'state': state})

    def retry(self, job_id, reason):
        require(type(reason) is str and len(reason) >= 10, 'retry reason required')
        with self.db:
            row = self.db.execute('SELECT state,attempts FROM jobs WHERE id=?', (job_id,)).fetchone()
            require(row and row['state'] == 'failed', 'only known failed jobs can retry; unknown stays held')
            require(row['attempts'] < self.plan['limits']['max_attempts'], 'attempt budget exhausted')
            dependents = [json.loads(r['spec']) for r in self.rows()
                          if r['state'] != 'queued' and job_id in json.loads(r['spec'])['depends_on']]
            require(not dependents, 'dependent evidence already dispatched')
            self.db.execute("UPDATE jobs SET state='queued' WHERE id=?", (job_id,))
            self.event('retry-authorized', {'job': job_id, 'reason': reason})

    def decision(self, job_id, accepted, reason):
        require(type(reason) is str and len(reason) >= 10, 'independent review reference required')
        with self.db:
            row = self.db.execute('SELECT state FROM jobs WHERE id=?', (job_id,)).fetchone()
            require(row and row['state'] == 'returned', 'only returned work can be reviewed')
            self.db.execute('UPDATE jobs SET state=? WHERE id=?',
                            ('accepted' if accepted else 'rejected', job_id))
            self.event('head-decision', {'job': job_id, 'accepted': accepted, 'reference': reason,
                                         'automatic_empirical_pass': False})

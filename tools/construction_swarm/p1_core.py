"""P1 fake-only, durable fenced task/attempt core.

No socket, provider, WSL service, or live Hermes integration is present here. The two
SQLite files deliberately give fixtures independent canonical/execution durability seams.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

SOURCE_COMMIT = "8568b8a4e95171803cf126ce417cdfd775a71eb4"
GOAL_ID = "goal-recursion-v2-execution-fabric"
REQUIREMENTS_DIGEST = hashlib.sha256(b"CW-01,CW-02,CW-05;S01,S02,S05").hexdigest()


class P1Refused(RuntimeError):
    pass


class RevisionConflict(P1Refused):
    pass


class IdempotencyConflict(P1Refused):
    pass


class FenceRejected(P1Refused):
    pass


class PermissionDenied(P1Refused):
    pass


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value):
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def request_digest(request):
    return _digest({key: value for key, value in request.items() if key != "content_digest"})


def _connection(filename):
    db = sqlite3.connect(filename, timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    try:
        deadline = time.monotonic() + 10
        while True:
            try:
                mode = db.execute("PRAGMA journal_mode=WAL").fetchone()[0]
                _require(mode.lower() == "wal", "WAL durability mode unavailable")
                break
            except sqlite3.OperationalError as exc:
                # Concurrent first opens can fail the journal-mode lock upgrade
                # immediately despite busy_timeout. Retry only this setup step;
                # no task, provider or outbox effect has occurred yet.
                code = getattr(exc, "sqlite_errorcode", 0)
                if code & 0xff != sqlite3.SQLITE_BUSY or time.monotonic() >= deadline:
                    raise
                time.sleep(.01)
        db.execute("PRAGMA synchronous=FULL")
        db.execute("PRAGMA foreign_keys=ON")
        return db
    except BaseException:
        db.close()
        raise


def _require(value, reason):
    if not value:
        raise P1Refused(reason)


@dataclass(frozen=True)
class FakeTransport:
    """Test-only authenticated identity; every body-provided actor is untrusted."""

    identity: str


class FakeHermes:
    """Separate fake canonical authority. It is not an execution task registry."""

    def __init__(self, filename):
        self.db = _connection(filename)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY, project TEXT NOT NULL, revision INTEGER NOT NULL,
                goal_id TEXT NOT NULL, source_commit TEXT NOT NULL, requirements_digest TEXT NOT NULL,
                state TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS receipts (
                receipt TEXT PRIMARY KEY, body TEXT NOT NULL, delivery_fence INTEGER NOT NULL,
                delivery_identity TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS transitions (
                receipt TEXT PRIMARY KEY, task_id TEXT NOT NULL, event TEXT NOT NULL);
        """)

    def close(self):
        self.db.close()

    def create_task(self, task_id, project, revision=1, goal_id=GOAL_ID,
                    source_commit=SOURCE_COMMIT, requirements_digest=REQUIREMENTS_DIGEST):
        with self.db:
            self.db.execute("INSERT INTO tasks VALUES(?,?,?,?,?,?,?)",
                            (task_id, project, revision, goal_id, source_commit, requirements_digest, "open"))

    def task(self, task_id):
        row = self.db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if not row:
            raise P1Refused("unknown canonical task")
        return dict(row)

    def assert_binding(self, body):
        task = self.task(body["task_id"])
        for field in ("project", "goal_id", "source_commit", "requirements_digest"):
            if task[field] != body[field]:
                raise PermissionDenied("canonical task binding mismatch")
        if task["revision"] != body["expected_revision"]:
            raise RevisionConflict("canonical task revision changed")
        return task

    def amend(self, task_id):
        with self.db:
            self.db.execute("UPDATE tasks SET revision=revision+1,state='open' WHERE task_id=?", (task_id,))

    def deliver(self, receipt, body, delivery_fence, delivery_identity):
        """Idempotent canonical transition receipt, called only from an effect boundary."""
        self.db.execute("BEGIN IMMEDIATE")
        try:
            prior = self.db.execute("SELECT body FROM receipts WHERE receipt=?", (receipt,)).fetchone()
            if prior:
                if prior["body"] != _json(body):
                    raise IdempotencyConflict("canonical receipt body changed")
                self.db.commit()
                return {"receipt": receipt, "duplicate": True}
            self.assert_binding(body)
            self.db.execute("INSERT INTO receipts VALUES(?,?,?,?)",
                            (receipt, _json(body), delivery_fence, delivery_identity))
            self.db.execute("INSERT INTO transitions VALUES(?,?,?)", (receipt, body["task_id"], body["event"]))
            state = "attempt_accepted" if body["event"] == "attempt_accepted" else "result_received"
            self.db.execute("UPDATE tasks SET state=? WHERE task_id=?", (state, body["task_id"]))
            self.db.commit()
            return {"receipt": receipt, "duplicate": False}
        except BaseException:
            self.db.rollback()
            raise

    def receipt_count(self, task_id, event=None):
        rows = [json.loads(row[0]) for row in self.db.execute("SELECT body FROM receipts")]
        return sum(body["task_id"] == task_id and (event is None or body["event"] == event) for body in rows)

    def receipt(self, receipt):
        row = self.db.execute("SELECT * FROM receipts WHERE receipt=?", (receipt,)).fetchone()
        return dict(row) if row else None


class FakeWorker:
    """In-memory fake effect endpoint with a guard evaluated at the effect boundary."""

    def __init__(self, before_effect=None, after_authorize=None, after_effect=None):
        self.launches = []
        self.before_effect = before_effect
        self.after_authorize = after_authorize
        self.after_effect = after_effect

    def launch(self, attempt_id, fence, authorize):
        if self.before_effect:
            self.before_effect()
        finish = authorize()
        failed = True
        try:
            if self.after_authorize:
                self.after_authorize()
            self.launches.append({"attempt_id": attempt_id, "fence": fence})
            if self.after_effect:
                self.after_effect()
            failed = False
        finally:
            finish(not failed)
        return "fake-launch:" + attempt_id + ":" + str(fence)


class P1Store:
    """Durable execution facts; Hermes remains the only logical task authority."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = _connection(self.root / "p1.sqlite")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS leader (
                singleton INTEGER PRIMARY KEY CHECK(singleton=1), owner TEXT NOT NULL, fence INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS grants (
                grant_id TEXT PRIMARY KEY, identity TEXT NOT NULL, project TEXT NOT NULL,
                capability TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS attempts (
                attempt_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, project TEXT NOT NULL,
                task_revision INTEGER NOT NULL, goal_id TEXT NOT NULL, source_commit TEXT NOT NULL,
                requirements_digest TEXT NOT NULL, content_digest TEXT NOT NULL, identity TEXT NOT NULL,
                grant_id TEXT NOT NULL, fence INTEGER NOT NULL, state TEXT NOT NULL, charge_state TEXT NOT NULL,
                launch_identity TEXT, launch_receipt TEXT);
            CREATE TABLE IF NOT EXISTS outbox (
                receipt TEXT PRIMARY KEY, attempt_id TEXT NOT NULL, delivery_fence INTEGER NOT NULL,
                identity TEXT NOT NULL, grant_id TEXT NOT NULL, body TEXT NOT NULL,
                delivery TEXT NOT NULL DEFAULT 'pending');
            CREATE TABLE IF NOT EXISTS idempotency (
                identity TEXT NOT NULL, project TEXT NOT NULL, key TEXT NOT NULL, body_digest TEXT NOT NULL,
                fence INTEGER NOT NULL, response TEXT NOT NULL, PRIMARY KEY(identity, project, key));
            CREATE TABLE IF NOT EXISTS results (
                attempt_id TEXT PRIMARY KEY, expected_revision INTEGER NOT NULL, idempotency_key TEXT NOT NULL,
                body_digest TEXT NOT NULL, receipt TEXT, state TEXT NOT NULL, detail TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS recoveries (
                crashed_fence INTEGER PRIMARY KEY, recovery_fence INTEGER NOT NULL, recovery_owner TEXT NOT NULL);
        """)

    def close(self):
        self.db.close()

    def grant(self, grant_id, identity, project, capability="mutate"):
        with self.db:
            self.db.execute("INSERT INTO grants VALUES(?,?,?,?,0)", (grant_id, identity, project, capability))

    def revoke(self, grant_id):
        with self.db:
            self.db.execute("UPDATE grants SET revoked=1 WHERE grant_id=?", (grant_id,))

    def leader(self):
        row = self.db.execute("SELECT owner,fence FROM leader WHERE singleton=1").fetchone()
        return dict(row) if row else None

    def acquire_leader(self, owner, takeover=False):
        """Every new controller incarnation must explicitly advance the persisted fence."""
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT owner,fence FROM leader WHERE singleton=1").fetchone()
            if row is None:
                fence = 1
                self.db.execute("INSERT INTO leader VALUES(1,?,?)", (owner, fence))
            else:
                if not takeover:
                    raise FenceRejected("leader already exists; new incarnation must take over")
                fence = row["fence"] + 1
                self.db.execute("UPDATE leader SET owner=?,fence=? WHERE singleton=1", (owner, fence))
            self.db.commit()
            return fence
        except BaseException:
            self.db.rollback()
            raise

    def _fence(self, owner, fence):
        row = self.db.execute("SELECT owner,fence FROM leader WHERE singleton=1").fetchone()
        if not row or row["owner"] != owner or row["fence"] != fence:
            raise FenceRejected("stale leader fence")

    def _grant(self, grant_id, identity, project):
        row = self.db.execute("SELECT * FROM grants WHERE grant_id=?", (grant_id,)).fetchone()
        if not row or row["revoked"] or row["identity"] != identity or row["project"] != project or row["capability"] != "mutate":
            raise PermissionDenied("current transport-bound mutation grant required")

    @staticmethod
    def _request_fields(request):
        required = {"protocol_version", "goal_id", "task_id", "project", "expected_revision", "source_commit",
                    "requirements_digest", "content_digest", "grant_id", "idempotency_key", "claimed_actor"}
        _require(set(request) == required, "malformed mutation envelope")
        _require(request["protocol_version"] == 1, "unsupported protocol version")
        _require(request["goal_id"] == GOAL_ID and request["source_commit"] == SOURCE_COMMIT,
                 "unbound goal/source")
        _require(request["requirements_digest"] == REQUIREMENTS_DIGEST, "unbound requirements")
        _require(type(request["expected_revision"]) is int and request["expected_revision"] > 0,
                 "invalid expected revision")
        _require(type(request["idempotency_key"]) is str and request["idempotency_key"], "missing idempotency key")
        _require(re.fullmatch(r"[0-9a-f]{64}", request["content_digest"]) is not None and
                 request["content_digest"] == request_digest(request), "content digest mismatch")

    def _attempt_authorized(self, attempt, transport, owner, fence):
        self._fence(owner, fence)
        if attempt["fence"] != fence:
            raise FenceRejected("attempt belongs to a retired fence")
        if transport.identity != attempt["identity"]:
            raise PermissionDenied("transport identity differs from leased contributor")
        self._grant(attempt["grant_id"], attempt["identity"], attempt["project"])

    def accept(self, hermes, transport, request, owner, fence):
        """Atomically reserve capacity and create a fence/grant-bound canonical outbox intent."""
        self._request_fields(request)
        identity, project = transport.identity, request["project"]
        digest = request_digest(request)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self._fence(owner, fence)
            self._grant(request["grant_id"], identity, project)
            hermes.assert_binding(request)
            prior = self.db.execute("SELECT body_digest,fence,response FROM idempotency WHERE identity=? AND project=? AND key=?",
                                    (identity, project, request["idempotency_key"])).fetchone()
            if prior:
                if prior["body_digest"] != digest:
                    raise IdempotencyConflict("idempotency key reused with different body")
                if prior["fence"] != fence:
                    raise FenceRejected("idempotent request belongs to a retired fence")
                prior_attempt = self.db.execute("SELECT fence,state FROM attempts WHERE attempt_id=?",
                                                (json.loads(prior["response"])["attempt_id"],)).fetchone()
                if prior_attempt and prior_attempt["state"] == "revision_conflict":
                    raise RevisionConflict("prior attempt has a canonical revision conflict")
                self.db.commit()
                response = json.loads(prior["response"])
                if prior_attempt:
                    # The receipt is immutable, but recovery must never return stale authority.
                    response.update(fence=prior_attempt["fence"], state=prior_attempt["state"])
                return response
            attempt_id = "attempt-%08d" % (self.db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] + 1)
            receipt = "attempt-accepted:" + attempt_id
            self.db.execute("INSERT INTO attempts VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                attempt_id, request["task_id"], project, request["expected_revision"], request["goal_id"],
                request["source_commit"], request["requirements_digest"], request["content_digest"], identity,
                request["grant_id"], fence, "reserved", "held", None, None))
            event = {"event": "attempt_accepted", "task_id": request["task_id"], "project": project,
                     "expected_revision": request["expected_revision"], "attempt_id": attempt_id,
                     "goal_id": request["goal_id"], "source_commit": request["source_commit"],
                     "requirements_digest": request["requirements_digest"], "content_digest": request["content_digest"],
                     "origin_fence": fence, "identity": identity, "grant_id": request["grant_id"]}
            self.db.execute("INSERT INTO outbox(receipt,attempt_id,delivery_fence,identity,grant_id,body) VALUES(?,?,?,?,?,?)",
                            (receipt, attempt_id, fence, identity, request["grant_id"], _json(event)))
            response = {"attempt_id": attempt_id, "receipt": receipt, "fence": fence, "state": "reserved"}
            self.db.execute("INSERT INTO idempotency VALUES(?,?,?,?,?,?)",
                            (identity, project, request["idempotency_key"], digest, fence, _json(response)))
            self.db.commit()
            return response
        except BaseException:
            self.db.rollback()
            raise

    def replay_outbox(self, hermes, transport, owner, fence):
        """Deliver pending effects only under their exact current fence and current grant."""
        delivered = []
        receipts = [row[0] for row in self.db.execute("SELECT receipt FROM outbox WHERE delivery='pending' ORDER BY receipt")]
        for receipt in receipts:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                row = self.db.execute("SELECT * FROM outbox WHERE receipt=?", (receipt,)).fetchone()
                if not row or row["delivery"] != "pending":
                    self.db.commit()
                    continue
                self._fence(owner, fence)
                if row["delivery_fence"] != fence:
                    # A current leader cannot publish an unrecovered old-fence intent, but
                    # that retained evidence must not starve independent current work.
                    self.db.commit()
                    continue
                body = json.loads(row["body"])
                if transport.identity != row["identity"]:
                    self.db.commit()
                    continue
                try:
                    self._grant(row["grant_id"], row["identity"], body["project"])
                except PermissionDenied:
                    self.db.execute("UPDATE outbox SET delivery='grant_revoked' WHERE receipt=?", (receipt,))
                    self.db.commit()
                    continue
                attempt = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (row["attempt_id"],)).fetchone()
                _require(attempt is not None, "outbox attempt missing")
                expected = {"attempt_id": attempt["attempt_id"], "task_id": attempt["task_id"],
                            "project": attempt["project"], "expected_revision": attempt["task_revision"],
                            "goal_id": attempt["goal_id"], "source_commit": attempt["source_commit"],
                            "requirements_digest": attempt["requirements_digest"], "content_digest": attempt["content_digest"],
                            "identity": attempt["identity"], "grant_id": attempt["grant_id"],
                            "origin_fence": attempt["fence"]}
                expected["event"] = ("attempt_accepted" if receipt == "attempt-accepted:" + attempt["attempt_id"]
                                     else "attempt_result" if receipt == "attempt-result:" + attempt["attempt_id"] else None)
                if expected["event"] is None or body != expected:
                    self.db.execute("UPDATE outbox SET delivery='envelope_refused' WHERE receipt=?", (receipt,))
                    self.db.commit()
                    continue
                try:
                    hermes.deliver(receipt, body, row["delivery_fence"], transport.identity)
                except RevisionConflict:
                    self.db.execute("UPDATE outbox SET delivery='revision_conflict' WHERE receipt=?", (receipt,))
                    self.db.execute("UPDATE attempts SET state='revision_conflict' WHERE attempt_id=?", (attempt["attempt_id"],))
                    self.db.execute("UPDATE results SET state='revision_conflict',detail='canonical task revision changed' WHERE attempt_id=?",
                                    (attempt["attempt_id"],))
                    self.db.commit()
                    continue
                self.db.execute("UPDATE outbox SET delivery='delivered' WHERE receipt=?", (receipt,))
                self.db.commit()
                delivered.append(receipt)
            except BaseException:
                if self.db.in_transaction:
                    self.db.rollback()
                raise
        return delivered

    def begin_launch(self, transport, attempt_id, owner, fence):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            attempt = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
            if not attempt or attempt["state"] != "reserved":
                raise P1Refused("only a reserved attempt can launch")
            self._attempt_authorized(attempt, transport, owner, fence)
            launch_identity = "launch:" + attempt_id + ":" + str(fence)
            self.db.execute("UPDATE attempts SET state='launch_intent',launch_identity=? WHERE attempt_id=?",
                            (launch_identity, attempt_id))
            self.db.commit()
            return launch_identity
        except BaseException:
            self.db.rollback()
            raise

    def launch(self, worker, transport, attempt_id, owner, fence):
        launch_identity = self.begin_launch(transport, attempt_id, owner, fence)

        def authorize():
            self.db.execute("BEGIN IMMEDIATE")
            try:
                attempt = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
                self._attempt_authorized(attempt, transport, owner, fence)
            except BaseException:
                self.db.rollback()
                raise

            def finish(success):
                if success:
                    self.db.commit()
                else:
                    self.db.rollback()
            return finish

        receipt = worker.launch(attempt_id, fence, authorize)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            attempt = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
            self._attempt_authorized(attempt, transport, owner, fence)
            row = self.db.execute("SELECT state,launch_identity FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
            if not row or row["state"] != "launch_intent" or row["launch_identity"] != launch_identity:
                raise P1Refused("launch intent changed before receipt")
            self.db.execute("UPDATE attempts SET state='launched',launch_receipt=? WHERE attempt_id=?", (receipt, attempt_id))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        return receipt

    def recover_after_crash(self, crashed_fence, owner, fence):
        """A replacement incarnation retains every unreceipted old-fence launch as unknown/held."""
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self._fence(owner, fence)
            _require(fence != crashed_fence, "recovery requires a replacement fence")
            _require(fence > crashed_fence, "recovery fence must advance")
            prior = self.db.execute("SELECT 1 FROM recoveries WHERE crashed_fence=?", (crashed_fence,)).fetchone()
            _require(prior is None, "fence already recovered")
            owned = self.db.execute("SELECT COUNT(*) FROM attempts WHERE fence=? AND state IN ('reserved','launch_intent','launched')",
                                    (crashed_fence,)).fetchone()[0]
            pending = self.db.execute("SELECT COUNT(*) FROM outbox WHERE delivery_fence=? AND delivery='pending'",
                                      (crashed_fence,)).fetchone()[0]
            # Recovery can crash after adopting another incarnation's receipts.
            # Their immutable attempt origin stays old; current delivery ownership
            # is sufficient to adopt them again, without granting launch authority.
            _require(owned > 0 or pending > 0, "no recoverable crashed-fence attempt or receipt")
            self.db.execute("UPDATE attempts SET state='unknown' WHERE fence=? AND state IN ('reserved','launch_intent','launched')",
                            (crashed_fence,))
            self.db.execute("UPDATE outbox SET delivery_fence=? WHERE delivery_fence=? AND delivery='pending'", (fence, crashed_fence))
            self.db.execute("UPDATE idempotency SET fence=? WHERE fence=?", (fence, crashed_fence))
            self.db.execute("INSERT INTO recoveries VALUES(?,?,?)", (crashed_fence, fence, owner))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise

    def submit_result(self, hermes, transport, attempt_id, expected_revision, idempotency_key, owner, fence):
        """Queue one result receipt only if the submitted revision is the lease's revision."""
        body = {"attempt_id": attempt_id, "expected_revision": expected_revision, "idempotency_key": idempotency_key}
        digest = _digest(body)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            attempt = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
            if not attempt or attempt["state"] != "launched":
                raise P1Refused("only launched attempts can submit")
            self._attempt_authorized(attempt, transport, owner, fence)
            prior = self.db.execute("SELECT * FROM results WHERE attempt_id=?", (attempt_id,)).fetchone()
            if prior:
                if prior["body_digest"] != digest or prior["idempotency_key"] != idempotency_key:
                    raise IdempotencyConflict("result idempotency body changed")
                if prior["state"] == "revision_conflict":
                    raise RevisionConflict(prior["detail"])
                binding = {key: attempt[key] for key in
                           ("task_id", "project", "goal_id", "source_commit", "requirements_digest")}
                binding["expected_revision"] = attempt["task_revision"]
                try:
                    hermes.assert_binding(binding)
                except RevisionConflict:
                    # Preserve the original receipt, including any delivered history,
                    # while preventing an old success from authorizing new progress.
                    self.db.execute("UPDATE results SET state='revision_conflict',detail='canonical task revision changed' WHERE attempt_id=?",
                                    (attempt_id,))
                    self.db.execute("UPDATE outbox SET delivery='revision_conflict' WHERE attempt_id=? AND delivery='pending'",
                                    (attempt_id,))
                    self.db.commit()
                    raise
                self.db.commit()
                return prior["receipt"]
            if expected_revision != attempt["task_revision"]:
                self.db.execute("INSERT INTO results VALUES(?,?,?,?,?,?,?)", (
                    attempt_id, expected_revision, idempotency_key, digest, None, "revision_conflict",
                    "attempt is bound to another canonical revision"))
                self.db.commit()
                raise RevisionConflict("attempt is bound to another canonical revision")
            event = {"event": "attempt_result", "task_id": attempt["task_id"], "project": attempt["project"],
                     "expected_revision": attempt["task_revision"], "attempt_id": attempt_id,
                     "goal_id": attempt["goal_id"], "source_commit": attempt["source_commit"],
                     "requirements_digest": attempt["requirements_digest"], "content_digest": attempt["content_digest"],
                     "origin_fence": attempt["fence"], "identity": attempt["identity"], "grant_id": attempt["grant_id"]}
            try:
                hermes.assert_binding(event)
            except RevisionConflict:
                self.db.execute("INSERT INTO results VALUES(?,?,?,?,?,?,?)", (
                    attempt_id, expected_revision, idempotency_key, digest, None, "revision_conflict",
                    "canonical task revision changed"))
                self.db.commit()
                raise
            receipt = "attempt-result:" + attempt_id
            self.db.execute("INSERT INTO outbox(receipt,attempt_id,delivery_fence,identity,grant_id,body) VALUES(?,?,?,?,?,?)",
                            (receipt, attempt_id, fence, attempt["identity"], attempt["grant_id"], _json(event)))
            self.db.execute("INSERT INTO results VALUES(?,?,?,?,?,?,?)",
                            (attempt_id, expected_revision, idempotency_key, digest, receipt, "pending", "outbox queued"))
            self.db.commit()
            return receipt
        except BaseException:
            if self.db.in_transaction:
                self.db.rollback()
            raise

    def attempt(self, attempt_id):
        row = self.db.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        return dict(row) if row else None

    def attempts_count(self):
        return self.db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]

    def outbox_delivery(self, receipt):
        row = self.db.execute("SELECT delivery FROM outbox WHERE receipt=?", (receipt,)).fetchone()
        return row["delivery"] if row else None

    def result(self, attempt_id):
        row = self.db.execute("SELECT * FROM results WHERE attempt_id=?", (attempt_id,)).fetchone()
        return dict(row) if row else None

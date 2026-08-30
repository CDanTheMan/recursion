#!/usr/bin/env python3
"""Phase 7 Grok Bot outbound signed-routine dispatcher. INERT AND DISABLED BY DEFAULT.

docs/plans/recursion-v2-execution-fabric.md, "Grok Bot adapter" and "Phase 7". Grok Bot is a
SUPERVISORY backend: a persistent project principal, planning critic, reviewer, triage arm and
browser-QA preparer. It is not an engine manifest, not a Cursor model alias, and not a fleet of
isolated workers.

The single fact that shapes every decision in this file (audit 2026-08-28, "Grok Bot"): **all
Bots on an account share one cloud computer** -- one filesystem, one browser session, one set
of application logins, one command line. Separate screens are not separate security
boundaries. Therefore:

  * the Bot receives an immutable, redacted envelope and non-secret repository references --
    never a deploy key, a controller token, ``.env``, or SSH access to gs-recursion;
  * concurrency is leased at the ACCOUNT level, not per Bot, because two Bots editing code
    are one writer with two screens;
  * results come back as a PROPOSAL, or on a review branch that Recursion fetches and verifies
    itself. A Bot transcript, screenshot or self-reported test is advisory evidence.

Transport is one outbound POST to a human-created, narrowly scoped signed routine webhook. The
URL and the sender key live in the box .env behind references; neither ever enters a tracked
file, a durable record, or a log line. There is no inbound listener and this phase does not
require one (plan Phase 4 gate).

Everything here is gated: ``RECURSION_REMOTE_ADAPTERS=1`` plus
``RECURSION_REMOTE_<NAME>_ENABLED=1``, a valid manifest, a resolvable webhook URL and sender
key, and -- for the live transport -- ``RECURSION_REMOTE_LIVE=1``. The loop writes none of
them (CLAUDE.md rule 3).
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from remote_assignment import (
    EXIT_OK,
    RemoteError,
    assignment_digest,
    canonical_bytes,
    canonical_digest,
    assignment_reference,
    screen_for_secret_material,
    validate_assignment,
)
from remote_backend import (
    AccountLease,
    AMBIGUOUS_MUTATION_ERRORS,
    RefusingTransport,
    Transport,
    atomic_json,
    assert_not_paused,
    backend_endpoint,
    begin_attempt,
    classify_status,
    is_paused,
    lookup_attempt,
    now_iso,
    outbound_admission,
    open_attempts,
    read_session,
    reconcile_attempt,
    remote_root,
    resolve_backend,
    resolve_secret,
    validate_directory,
    validate_secret_ref,
    write_session,
)

PROG = "grok-bot-dispatcher"
SCHEMA_VERSION = 1
BACKEND_KIND = "grok-routine"
ENVELOPE_KIND = "recursion-grok-routine-assignment"
SIGNATURE_VERSION = "v1"

# Supervisory roles only. Implementation on a shared computer stays exceptional and is not
# expressible here: there is no "implementer" role in this list, deliberately.
ROLES = frozenset({"project-lead", "planner-critic", "reviewer", "triage", "browser-qa",
                   "status-synthesis"})

# The Bot's only result channel. A proposal is reviewed by Hermes and Lucas; it is never
# applied, merged, deployed, or published by anything in this file.
RESULT_CHANNEL = "proposal-review-only"

# Stated in the envelope so the boundary travels with the assignment rather than living only
# in a design document the Bot never reads.
CAPABILITIES_WITHHELD = (
    "controller-credentials",
    "deploy-keys",
    "recursion-state-write",
    "branch-merge",
    "production-deployment",
    "pause-control",
    "routing-and-autonomy-policy",
    "external-communication",
)

# A proposal that tries to be an instruction. These are refused on ingest rather than filtered,
# because a partially-obeyed instruction is worse than a rejected one.
FORBIDDEN_PROPOSAL_KEYS = frozenset({
    "merge", "deploy", "publish", "push", "force_push", "delete_branch", "pause", "unpause",
    "credentials", "autonomy", "cron", "approve", "execute",
})

DISPATCH_ATTEMPT_OPERATION = "dispatch"


def imperative_keys(value: object, path: str = "proposal") -> list[str]:
    """Find imperative keys anywhere in a proposal, not just at the top level.

    Nested is where they would actually appear: ``{"recommendations": [{"deploy": ...}]}``
    reads as advice until something walks it.
    """
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            here = f"{path}.{key}"
            if str(key).strip().lower().replace("-", "_") in FORBIDDEN_PROPOSAL_KEYS:
                found.append(here)
            found.extend(imperative_keys(item, here))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(imperative_keys(item, f"{path}[{index}]"))
    return found


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def validate_role(role: object) -> str:
    if role not in ROLES:
        raise RemoteError("request-invalid",
                          "role must be one of " + ", ".join(sorted(ROLES))
                          + "; implementation on the account-shared computer is not a role "
                            "this dispatcher can request")
    return str(role)


def build_envelope(assignment: dict, *, role: str, instructions: str, non_goals: list[str],
                   dispatch_id: str, issued_at: str) -> dict:
    """The immutable, redacted envelope.

    Redaction is not a filter that strips secrets -- it is a screen that REFUSES. A field that
    should not be here does not get quietly removed and sent anyway; the dispatch fails and a
    human finds out why.

    The envelope carries only ``assignment_reference``: task, project, repository URL, branch,
    exact sha, publication policy and the assignment digest. Sandbox profile, network profile
    and allowed paths are withheld -- an external executor has no need to learn the shape of
    the containment it is being run under.
    """
    normalised = validate_assignment(assignment)
    validate_role(role)
    if not isinstance(instructions, str) or not instructions.strip():
        raise RemoteError("request-invalid", "instructions must be a nonempty string")
    if not isinstance(non_goals, list) or not all(
            isinstance(item, str) and item.strip() for item in non_goals):
        raise RemoteError("request-invalid", "non_goals must be a list of nonempty strings")

    envelope = {
        "schema_version": SCHEMA_VERSION,
        "envelope_kind": ENVELOPE_KIND,
        "dispatch_id": dispatch_id,
        "issued_at": issued_at,
        "role": role,
        "result_channel": RESULT_CHANNEL,
        "assignment": assignment_reference(normalised),
        "assignment_digest": assignment_digest(normalised),
        "instructions": instructions,
        "non_goals": list(non_goals),
        "capabilities_withheld": list(CAPABILITIES_WITHHELD),
        "verification_note": (
            "Transcripts, screenshots and self-reported tests are advisory evidence. Code is "
            "returned on a review branch and independently fetched, gated and verified on the "
            "coordinator before it can become a candidate."
        ),
    }
    screen_for_secret_material(envelope, "envelope")
    return envelope


def envelope_digest(envelope: dict) -> str:
    return canonical_digest(envelope)


def envelope_identity_digest(envelope: dict) -> str:
    """The digest of WHAT is being asked, excluding WHEN it was asked.

    ``issued_at`` is inside the signed envelope so a captured body cannot be replayed with a
    fresh timestamp. But it must stay out of the idempotency key: otherwise the same logical
    dispatch, retried one second later, is a different key and gets sent twice. Idempotency is
    a property of the request's content, not of the clock.
    """
    return canonical_digest({key: value for key, value in envelope.items()
                             if key != "issued_at"})


def sign_envelope(body: bytes, timestamp: str, secret: str) -> str:
    """``HMAC-SHA256(key, "<version>:<timestamp>:" || body)`` -> ``<version>=<hex>``.

    The timestamp is inside the signed material so a captured body cannot be replayed with a
    fresh header, and the version prefix is inside it so a future scheme change cannot be
    downgraded by rewriting one header.
    """
    if not isinstance(secret, str) or not secret:
        raise RemoteError("credential-absent", "signing key is empty")
    material = f"{SIGNATURE_VERSION}:{timestamp}:".encode("utf-8") + body
    digest = hmac.new(secret.encode("utf-8"), material, hashlib.sha256).hexdigest()
    return f"{SIGNATURE_VERSION}={digest}"


class GrokBotDispatcher:
    """Outbound-only signed-routine dispatcher. Construct with an injected transport."""

    def __init__(self, base: Path, manifest: dict, transport: Transport | None = None,
                 clock=None) -> None:
        if manifest.get("kind") != BACKEND_KIND:
            raise RemoteError("manifest-invalid",
                              f"backend kind {manifest.get('kind')!r} is not {BACKEND_KIND!r}")
        self.base = Path(base)
        self.manifest = manifest
        self.name = manifest["name"]
        self.transport = transport if transport is not None else RefusingTransport()
        self.clock = clock

    def _now(self) -> str:
        return now_iso(self.clock)

    def _signing_key(self) -> str:
        env_name = validate_secret_ref(self.manifest["signing_key_ref"], "signing_key_ref")
        return resolve_secret(env_name, "signing_key_ref")

    def _sender_credential(self) -> str:
        env_name = validate_secret_ref(self.manifest["credential_ref"], "credential_ref")
        return resolve_secret(env_name, "credential_ref")

    # -- dispatch ---------------------------------------------------------------------------

    def dispatch(self, assignment: dict, *, role: str, instructions: str,
                 non_goals: list[str], dispatch_id: str) -> dict:
        """Send exactly one immutable envelope, at most once, and record what happened.

        Order is the contract:
          1. PAUSE is checked FIRST. Under PAUSE nothing leaves the box -- not a retry, not a
             "harmless" status ping.
          2. The envelope is built, digested and signed, and the endpoint is resolved. All of
             this is local and can fail (redaction, bad role, absent credential); those
             failures cost nothing and consume no attempt, because nothing has been committed
             or sent.
          3. The attempt is committed durably BEFORE the request. A process that dies mid-POST
             leaves an open attempt, which is a question, not a licence to re-send.
          4. The account-shared lease is taken.
          5. The request goes out. Then, and only then, the attempt closes.
        """
        assert_not_paused(self.base, "a Grok Bot routine dispatch")
        normalised = validate_assignment(assignment)
        self._assert_assignment_binding(normalised)
        digest = assignment_digest(normalised)
        issued_at = self._now()
        envelope = build_envelope(normalised, role=role, instructions=instructions,
                                  non_goals=non_goals, dispatch_id=dispatch_id,
                                  issued_at=issued_at)
        body = canonical_bytes(envelope)
        body_digest = hashlib.sha256(body).hexdigest()
        env_digest = envelope_digest(envelope)
        identity_digest = envelope_identity_digest(envelope)

        # The admission lock orders the PAUSE decision, reservation, POST and close.  The
        # idempotency key is also sent to providers that support it, so a crash after the
        # provider accepts the request can be reconciled without blind duplicate creation.
        with outbound_admission(self.base, self.name, "a Grok Bot routine dispatch"):
            prior = lookup_attempt(
                self.base, self.name, dispatch_id=dispatch_id,
                operation=DISPATCH_ATTEMPT_OPERATION, assignment_digest=digest,
                request_digest=identity_digest, lock_held=True)
            if prior is not None:
                if prior.replayed:
                    try:
                        return read_session(self.base, self.name, dispatch_id, lock_held=True)
                    except RemoteError as exc:
                        if exc.code != "not-found":
                            raise
                        raise RemoteError("unreconciled-attempt",
                                          f"dispatch {dispatch_id} is recorded as landed but has no "
                                          "local dispatch record; import the result rather than "
                                          "re-dispatching") from exc
                raise RemoteError("unreconciled-attempt",
                                  f"dispatch attempt {prior.attempt_id} was left open by an "
                                  "earlier process. The routine may already be running. Reconcile "
                                  "it with observed evidence before dispatching again.")

            # Resolve credentials only for new work. A completed idempotent replay must remain
            # readable even after a human rotates/removes the old credential.
            url = backend_endpoint(self.manifest)
            headers = {
                "Content-Type": "application/json",
                "X-Recursion-Dispatch-Id": dispatch_id,
                "X-Recursion-Assignment-Digest": digest,
                "X-Recursion-Envelope-Digest": env_digest,
                "X-Recursion-Timestamp": issued_at,
                "X-Recursion-Signature": sign_envelope(body, issued_at, self._signing_key()),
                "X-Recursion-Sender": self._sender_credential(),
                "Idempotency-Key": identity_digest,
            }
            attempt = begin_attempt(
                self.base, self.name, dispatch_id=dispatch_id,
                operation=DISPATCH_ATTEMPT_OPERATION, assignment_digest=digest,
                request_digest=identity_digest, max_attempts=self.manifest["max_attempts"],
                clock=self.clock, lock_held=True)
            if attempt.replayed or attempt.unreconciled:
                raise RemoteError("unreconciled-attempt", "reservation changed unexpectedly")
            admission_snapshot, admission_snapshot_digest = self._admission_snapshot(
                normalised, digest)

            try:
                with AccountLease(self.base, self.manifest["capacity_pool"],
                                  self.manifest["concurrency_lease"]):
                    assert_not_paused(self.base, "a Grok Bot routine dispatch")
                    response = self.transport.request(
                        "POST", url, headers, body, self.manifest["timeout_seconds"])
                    classify_status(response.status, response.body)
                    payload = response.json()
            except RemoteError as exc:
                if exc.code in AMBIGUOUS_MUTATION_ERRORS:
                    # A retryable-looking provider failure can still follow an accepted
                    # mutation.  Reconcile before allowing another dispatch.
                    pass
                elif exc.exit_code == 75:
                    attempt.defer(exc, clock=self.clock, lock_held=True)
                else:
                    attempt.fail(exc, clock=self.clock, lock_held=True)
                # A transport/ambiguous response leaves the fire-and-forget dispatch OPEN.
                # The caller must observe the Bot externally before retrying.
                raise

            accepted = payload.get("accepted")
            if accepted is not True:
                error = RemoteError("malformed-response",
                                    "routine did not acknowledge the envelope with accepted=true")
                attempt.fail(error, clock=self.clock, lock_held=True)
                raise error
            routine_run_id = payload.get("routine_run_id")
            if routine_run_id is not None and not isinstance(routine_run_id, str):
                error = RemoteError("malformed-response", "routine_run_id is not a string")
                raise error

            record = {
                "schema_version": SCHEMA_VERSION,
                "kind": "grok-routine-dispatch",
                "backend": self.name,
                "dispatch_id": dispatch_id,
                "assignment_digest": digest,
                "envelope_digest": env_digest,
                "envelope_identity_digest": identity_digest,
                "body_sha256": body_digest,
                "role": role,
                "task_id": normalised["task_id"],
                "project_id": normalised["project_id"],
                "capacity_pool": self.manifest["capacity_pool"],
                "host_id": self.manifest["host_id"],
                # The URL is bearer-grade; the REFERENCE is what is durable, never the value.
                "endpoint_ref": self.manifest["endpoint_ref"],
                "signing_key_ref": self.manifest["signing_key_ref"],
                "result_channel": RESULT_CHANNEL,
                "routine_run_id": routine_run_id or "",
                "state": "dispatched",
                "envelope": envelope,
                "issued_at": issued_at,
                "updated_at": self._now(),
                "billing_basis": self.manifest["billing_basis"],
                "on_demand": self.manifest["on_demand"],
                "provider": normalised["provider"],
                "admission_snapshot": admission_snapshot,
                "admission_snapshot_digest": admission_snapshot_digest,
            }
            write_session(self.base, self.name, dispatch_id, record, lock_held=True)
            attempt.succeed("dispatched", {"envelope_digest": env_digest},
                            clock=self.clock, lock_held=True)
            return record

    def _assert_assignment_binding(self, assignment: dict) -> None:
        if assignment["capacity_pool"] != self.manifest["capacity_pool"]:
            raise RemoteError("assignment-invalid",
                              "assignment capacity_pool is not the authorized backend pool")
        if assignment["host"] != self.manifest["host_id"]:
            raise RemoteError("assignment-invalid",
                              "assignment host is not the authorized backend host")

    def _admission_snapshot(self, assignment: dict, digest: str) -> tuple[dict, str]:
        """Capture the admitted assignment/manifest attribution before dispatch."""
        snapshot = {
            "schema_version": SCHEMA_VERSION,
            "backend": self.name,
            "manifest_digest": canonical_digest(self.manifest),
            "assignment_digest": digest,
            "provider": assignment["provider"],
            "capacity_pool": self.manifest["capacity_pool"],
            "host_id": self.manifest["host_id"],
            "billing_basis": self.manifest["billing_basis"],
            "on_demand": self.manifest["on_demand"],
        }
        return snapshot, canonical_digest(snapshot)

    def read_dispatch(self, dispatch_id: str) -> dict:
        return read_session(self.base, self.name, dispatch_id)

    # -- retry reconciliation ---------------------------------------------------------------

    def reconcile(self, attempt_id: str, *, observed: str, observer: str,
                  evidence: dict | None = None) -> dict:
        """Close an open dispatch attempt against evidence observed OUTSIDE this dispatcher.

        A signed routine webhook is fire-and-forget: there is no vendor endpoint that will
        tell us whether a lost POST landed. So reconciliation consumes an observation --
        a routine run visible in the Bot app, a branch that appeared on the remote, or a human
        confirming neither happened -- and records who observed it.

        ``unknown`` is terminal, not a retry: it becomes ``unreconciled`` and needs a human.
        Deciding "probably didn't land" is exactly how a duplicate dispatch happens.
        """
        detail = dict(evidence or {})
        screen_for_secret_material(detail, "reconciliation evidence")
        return reconcile_attempt(self.base, self.name, attempt_id, observed=observed,
                                 observer=observer, detail=detail, clock=self.clock)

    def recover(self) -> dict:
        """Restart recovery. Pure local awareness -- available under PAUSE, by design."""
        pending = open_attempts(self.base, self.name)
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "grok-routine-recovery",
            "backend": self.name,
            "paused": is_paused(self.base),
            "open_attempts": [
                {"attempt_id": row["attempt_id"], "dispatch_id": row.get("dispatch_id", ""),
                 "assignment_digest": row.get("assignment_digest", ""),
                 "opened_at": row.get("opened_at", "")}
                for row in pending
            ],
            "next_action": (
                "For each open attempt, establish independently whether the routine ran, then "
                "call reconcile with landed / not-landed / unknown. Do not re-dispatch first."
            ),
            "observed_at": self._now(),
        }

    # -- result channel ----------------------------------------------------------------------

    def record_proposal(self, dispatch_id: str, proposal: dict) -> dict:
        """Ingest a Bot result as a PROPOSAL. Advisory, reviewed, never applied.

        This writes to ``state/remote/<backend>/proposals/`` and nowhere else. It does not
        touch tasks, the board, the ledger, ``state/DECISIONS.md``, or any branch. A proposal
        carrying an imperative key (merge, deploy, publish, pause, credentials, ...) is
        refused whole: a partially-obeyed instruction is worse than a rejected one.
        """
        if not isinstance(proposal, dict) or not proposal:
            raise RemoteError("request-invalid", "proposal must be a nonempty JSON object")
        dispatch = self.read_dispatch(dispatch_id)
        offending = sorted(imperative_keys(proposal))
        if offending:
            raise RemoteError("result-channel-violation",
                              "proposal carries imperative key(s) "
                              + ", ".join(offending)
                              + f"; the {RESULT_CHANNEL} channel accepts findings and "
                                "recommendations, not actions")
        screen_for_secret_material(proposal, "proposal")
        record = {
            "schema_version": SCHEMA_VERSION,
            "kind": "grok-routine-proposal",
            "backend": self.name,
            "dispatch_id": dispatch_id,
            "assignment_digest": dispatch["assignment_digest"],
            "envelope_digest": dispatch["envelope_digest"],
            "role": dispatch["role"],
            "result_channel": RESULT_CHANNEL,
            "authority": "advisory",
            "requires_human_review": True,
            "self_reported_evidence_is_advisory": True,
            "proposal": proposal,
            "proposal_digest": canonical_digest(proposal),
            "received_at": self._now(),
        }
        path = remote_root(self.base, self.name) / "proposals" / f"{dispatch_id}.json"
        atomic_json(path, record)
        return record


# --- CLI -------------------------------------------------------------------------------------

def build_dispatcher(base: Path, name: str) -> GrokBotDispatcher:
    manifest = resolve_backend(name, kind=BACKEND_KIND)
    from remote_backend import HttpsTransport  # late import keeps import-time side-effect free

    transport: Transport = RefusingTransport()
    try:
        transport = HttpsTransport()
    except RemoteError:
        pass
    return GrokBotDispatcher(base, manifest, transport)


def main() -> int:
    parser = argparse.ArgumentParser(prog=PROG, description=__doc__.splitlines()[0])
    parser.add_argument("--base", default=".", help="repository root (default: .)")
    parser.add_argument("--backend", default="grok-bot", help="manifest name")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("validate", help="validate every remote backend manifest")
    sub.add_parser("recover", help="list dispatch attempts left open by a prior process")
    show = sub.add_parser("show", help="print one durable dispatch record")
    show.add_argument("dispatch_id")
    reconcile = sub.add_parser("reconcile", help="close an open attempt against evidence")
    reconcile.add_argument("attempt_id")
    reconcile.add_argument("--observed", required=True,
                           choices=("landed", "not-landed", "unknown"))
    reconcile.add_argument("--observer", required=True,
                           help="who established this, e.g. 'lucas:grok-bot-app'")
    args = parser.parse_args()

    if args.command is None:
        parser.print_help(sys.stderr)
        return 2
    if args.command == "validate":
        return validate_directory()

    base = Path(args.base).resolve()
    try:
        dispatcher = build_dispatcher(base, args.backend)
        if args.command == "recover":
            result: object = dispatcher.recover()
        elif args.command == "show":
            result = dispatcher.read_dispatch(args.dispatch_id)
        else:
            result = dispatcher.reconcile(args.attempt_id, observed=args.observed,
                                          observer=args.observer)
    except RemoteError as exc:
        diag(str(exc))
        return exc.exit_code
    print(json.dumps(result, indent=2, sort_keys=True))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())

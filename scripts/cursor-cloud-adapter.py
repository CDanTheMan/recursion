#!/usr/bin/env python3
"""Phase 6 Cursor Cloud client contract. INERT AND DISABLED BY DEFAULT.

docs/plans/recursion-v2-execution-fabric.md, "Cursor Cloud adapter" and "Phase 6". Cursor
Cloud is an isolated execution HOST and a capacity POOL -- not a local engine, not a model
alias, and not Grok Bot.

This file implements the client contract and nothing else. It performs no network I/O of its
own: every byte goes through an injected ``Transport`` (scripts/remote_backend.py), the
production transport refuses to be constructed without ``RECURSION_REMOTE_LIVE=1``, and the
controls inject a fake. The adapter refuses to resolve at all until a human sets
``RECURSION_REMOTE_ADAPTERS=1`` and ``RECURSION_REMOTE_<NAME>_ENABLED=1`` in the box .env.

The four properties this file exists to make structural:

  * **Exact source.** Every run is bound to a full 40-hex ``source_sha``. A branch name, a
    tag, an abbreviated sha or ``HEAD`` is refused at request construction. A run bound to a
    moving ref cannot be reconciled against what it actually built.
  * **Isolated branch.** ``workOnCurrentBranch`` is forced false, ``autoCreatePr`` is forced
    false, and the target branch is checked against the project's default and integration
    branches -- twice: once while building the request, and once as a post-check over the
    finished body. Construction and post-check are separate on purpose; the plan's Phase 6
    gate asks for both.
  * **Independent verification.** Nothing the vendor reports can mark a candidate verified.
    ``reconciliation_input`` emits ``verification_state = requires-independent-verification``
    and has no code path that emits anything else. Vendor test claims are recorded as an
    advisory digest, not ingested as gate evidence.
  * **Quota is not permission to spend.** HTTP 402 maps to ``quota-exhausted``, which is a
    DEFER (exit 75). No handler in this file can set ``on_demand``; only a human editing the
    manifest and setting ``RECURSION_ALLOW_METERED=1`` can admit metered work at all.

The exact request/response field names below are PROVISIONAL, in the same sense as the
engine manifests shipped under D-015: they follow the vocabulary recorded in
docs/audits/recursion-v2-infrastructure-audit-2026-08-28.md ("Cursor Cloud Agents") and must
be verified against the live API during the human-gated deployment step. Shipping provisional
field names is safe precisely because the adapter is inert -- measure, don't assume.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from remote_assignment import (
    EXIT_OK,
    RemoteError,
    SHA_RE,
    assignment_digest,
    canonical_bytes,
    canonical_digest,
    screen_for_secret_material,
    validate_assignment,
    validate_branch_name,
    validate_repository_url,
)
from remote_backend import (
    AccountLease,
    AMBIGUOUS_MUTATION_ERRORS,
    RefusingTransport,
    Transport,
    assert_not_paused,
    backend_endpoint,
    begin_attempt,
    classify_status,
    is_paused,
    lookup_attempt,
    list_sessions,
    now_iso,
    open_attempts,
    outbound_admission,
    read_session,
    reconcile_attempt,
    resolve_backend,
    resolve_secret,
    validate_directory,
    write_usage,
    validate_secret_ref,
    write_session,
)

PROG = "cursor-cloud-adapter"
SCHEMA_VERSION = 1
BACKEND_KIND = "cursor-cloud"
EVIDENCE_SOURCE = "cursor-cloud-api-v0"

# The only value this module will ever write into a verification_state field. There is no
# branch, no flag and no vendor payload that produces "verified" here; that word belongs to
# the independent gate on Hetzner (CONTROL_PLANE.md invariant 7, plan invariant 12).
VERIFICATION_STATE = "requires-independent-verification"

REQUIRED_INDEPENDENT_CHECKS = (
    "fetch-returned-branch-and-commit-from-the-registered-remote",
    "verify-the-candidate-commit-descends-from-source_sha",
    "verify-the-diff-touches-only-allowed_paths",
    "run-the-project-gate-commands-on-hetzner",
    "verify-the-assignment-digest-matches-the-launched-assignment",
)

# Mutating operations get a durable attempt; reads do not. A durable row per status poll
# would drown the journal that exists to answer one question -- "did a request that may have
# changed remote state actually land?" -- and a poll cannot change remote state. Reads update
# the session projection instead, which is where "what did we last observe" belongs.
MUTATING_OPERATIONS = frozenset({"create", "cancel"})

SESSION_ACTIVE_STATES = frozenset({"created", "running"})
SESSION_TERMINAL_STATES = frozenset({"completed", "cancelled", "failed", "unreconciled"})

# Fail closed on an unrecognised vendor state. Guessing that an unknown string means
# "finished" is how a half-built candidate gets imported.
VENDOR_STATE_MAP = {
    "CREATING": "created", "PENDING": "created", "QUEUED": "created",
    "RUNNING": "running", "IN_PROGRESS": "running",
    "FINISHED": "completed", "COMPLETED": "completed", "SUCCEEDED": "completed",
    "CANCELLED": "cancelled", "CANCELED": "cancelled",
    "ERROR": "failed", "FAILED": "failed", "EXPIRED": "failed",
}


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def map_vendor_state(raw: object) -> str:
    if not isinstance(raw, str) or not raw:
        raise RemoteError("malformed-response", "vendor status is missing or not a string")
    mapped = VENDOR_STATE_MAP.get(raw.strip().upper())
    if mapped is None:
        raise RemoteError("malformed-response",
                          f"vendor reported an unrecognised state {raw!r}; refusing to guess "
                          "whether the run is terminal")
    return mapped


def branch_is_allowed(branch: str, publication: dict) -> bool:
    validate_branch_name(branch, "returned branch")
    if branch in (publication["default_branch"], publication["integration_branch"]):
        return False
    return any(fnmatch.fnmatchcase(branch, pattern)
               for pattern in publication["allowed_result_branch_patterns"])


def task_branch_for(assignment: dict, publication: dict) -> str:
    branch = publication["task_branch_pattern"].replace("<task-id>", assignment["task_id"])
    validate_branch_name(branch, "target branch")
    if not branch_is_allowed(branch, publication):
        raise RemoteError("request-invalid",
                          f"derived target branch {branch!r} is the default/integration branch "
                          "or does not match publication.allowed_result_branch_patterns")
    return branch


def assert_isolated_branch_request(body: dict, publication: dict) -> None:
    """Post-check the finished request body.

    Separate from construction deliberately. Construction can be reasoned about; a post-check
    over the exact bytes about to be sent is what survives a future edit to construction.
    """
    if body.get("workOnCurrentBranch") is not False:
        raise RemoteError("request-invalid",
                          "workOnCurrentBranch must be exactly false; a vendor run may never "
                          "write the branch it started from")
    target = body.get("target")
    if not isinstance(target, dict):
        raise RemoteError("request-invalid", "request target block is missing")
    if target.get("autoCreatePr") is not False:
        raise RemoteError("request-invalid",
                          "autoCreatePr must be exactly false; Recursion is the sole publisher")
    branch = target.get("branchName")
    if not isinstance(branch, str) or not branch_is_allowed(branch, publication):
        raise RemoteError("request-invalid",
                          f"target branch {branch!r} is not an isolated, allowed result branch")
    source = body.get("source")
    if not isinstance(source, dict):
        raise RemoteError("request-invalid", "request source block is missing")
    ref = source.get("startingRef")
    if not isinstance(ref, str) or not SHA_RE.fullmatch(ref):
        raise RemoteError("request-invalid",
                          "startingRef must be a full 40-hex commit sha; a branch, tag, short "
                          "sha or HEAD is refused")


class CursorCloudAdapter:
    """The Cursor Cloud client contract. Construct with an injected transport."""

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
        self.endpoint = backend_endpoint(manifest).rstrip("/")

    # -- plumbing -------------------------------------------------------------------------

    def _headers(self) -> dict:
        """Resolved per request and never stored on the instance, so no repr, traceback or
        pickled adapter can carry the credential."""
        env_name = validate_secret_ref(self.manifest["credential_ref"], "credential_ref")
        return {
            "Authorization": "Bearer " + resolve_secret(env_name, "credential_ref"),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _assert_credential(self) -> None:
        """Force credential resolution BEFORE any durable commit.

        Otherwise an unset API key would be discovered inside the request path, after the
        attempt was already committed, and a configuration error would consume an attempt
        from the budget it has no business spending.
        """
        env_name = validate_secret_ref(self.manifest["credential_ref"], "credential_ref")
        resolve_secret(env_name, "credential_ref")

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            raise RemoteError("request-invalid", "adapter paths are absolute within the API")
        return self.endpoint + path

    def _call(self, method: str, path: str, body: dict | None = None,
              extra_headers: dict | None = None) -> dict:
        payload = canonical_bytes(body) if body is not None else None
        headers = self._headers()
        headers.update(extra_headers or {})
        assert_not_paused(self.base, f"{method} {path}")
        response = self.transport.request(method, self._url(path), headers, payload,
                                          self.manifest["timeout_seconds"])
        classify_status(response.status, response.body)
        return response.json()

    def _now(self) -> str:
        return now_iso(self.clock)

    def _begin(self, dispatch_id: str, operation: str, digest: str, request_digest: str,
               *, lock_held: bool = False):
        if operation not in MUTATING_OPERATIONS:
            raise RemoteError("request-invalid",
                              f"{operation!r} is a read; reads update the session projection "
                              "and do not consume a durable attempt")
        return begin_attempt(
            self.base, self.name, dispatch_id=dispatch_id, operation=operation,
            assignment_digest=digest, request_digest=request_digest,
            max_attempts=self.manifest["max_attempts"], clock=self.clock, lock_held=lock_held)

    def _assert_assignment_binding(self, assignment: dict) -> None:
        if assignment["capacity_pool"] != self.manifest["capacity_pool"]:
            raise RemoteError("assignment-invalid",
                              "assignment capacity_pool is not the authorized backend pool")
        if assignment["host"] != self.manifest["host_id"]:
            raise RemoteError("assignment-invalid",
                              "assignment host is not the authorized backend host")

    # -- models ---------------------------------------------------------------------------

    def list_models(self) -> list[str]:
        with outbound_admission(self.base, self.name, "a Cursor Cloud model listing"):
            payload = self._call("GET", "/v0/models")
            models = payload.get("models")
            if not isinstance(models, list) or not all(isinstance(item, str) for item in models):
                raise RemoteError("malformed-response", "models response is not a list of strings")
            return models

    def validate_model(self, model_id: str) -> str:
        """Configured model IDs are validated against the provider, not assumed."""
        if not isinstance(model_id, str) or not model_id:
            raise RemoteError("request-invalid", "model id must be a nonempty string")
        available = self.list_models()
        if model_id not in available:
            raise RemoteError("request-invalid",
                              f"model {model_id!r} is not offered by this Cursor Cloud account")
        return model_id

    # -- create ---------------------------------------------------------------------------

    def build_create_request(self, assignment: dict, prompt: str) -> dict:
        """Pure request construction -- no transport, no credential, fully testable."""
        normalised = validate_assignment(assignment)
        if not isinstance(prompt, str) or not prompt.strip():
            raise RemoteError("request-invalid", "prompt must be a nonempty string")
        screen_for_secret_material({"prompt": prompt}, "create request")
        publication = self.manifest["publication"]
        target_branch = task_branch_for(normalised, publication)
        body: dict = {
            "prompt": {"text": prompt},
            "source": {
                "repository": normalised["source_repository"],
                # The exact commit, always. This is the field the whole phase turns on.
                "startingRef": normalised["source_sha"],
            },
            "target": {
                "branchName": target_branch,
                # Recursion is the sole publisher; a vendor-opened PR would be a second one.
                "autoCreatePr": False,
            },
            "workOnCurrentBranch": False,
        }
        if normalised["model"]:
            body["model"] = normalised["model"]
        assert_isolated_branch_request(body, publication)
        return body

    def create_run(self, assignment: dict, prompt: str, dispatch_id: str) -> dict:
        assert_not_paused(self.base, "a Cursor Cloud run creation")
        normalised = validate_assignment(assignment)
        self._assert_assignment_binding(normalised)
        digest = assignment_digest(normalised)
        body = self.build_create_request(normalised, prompt)
        with outbound_admission(self.base, self.name, "a Cursor Cloud run creation"):
            request_digest = canonical_digest(body)
            prior = lookup_attempt(
                self.base, self.name, dispatch_id=dispatch_id, operation="create",
                assignment_digest=digest, request_digest=request_digest, lock_held=True)
            if prior is not None:
                if prior.replayed:
                    try:
                        return read_session(self.base, self.name, dispatch_id, lock_held=True)
                    except RemoteError as exc:
                        if exc.code != "not-found":
                            raise
                        raise RemoteError("unreconciled-attempt",
                                          f"dispatch {dispatch_id} is recorded as landed but has no "
                                          "local session record; recover the vendor run rather than "
                                          "creating a second one") from exc
                raise RemoteError("unreconciled-attempt",
                                  f"attempt {prior.attempt_id} was left open by an earlier "
                                  "process; reconcile it against observed provider state before "
                                  "dispatching again")
            self._assert_credential()
            attempt = self._begin(dispatch_id, "create", digest, canonical_digest(body),
                                  lock_held=True)
            if attempt.replayed or attempt.unreconciled:
                raise RemoteError("unreconciled-attempt", "reservation changed unexpectedly")
            try:
                with AccountLease(self.base, self.manifest["capacity_pool"],
                                  self.manifest["concurrency_lease"]):
                    payload = self._call(
                        "POST", "/v0/agents", body,
                        {"Idempotency-Key": attempt.record["idempotency_key"]})
            except RemoteError as exc:
                if exc.code in AMBIGUOUS_MUTATION_ERRORS:
                    # Even a retryable-looking 503 is ambiguous after a mutation was sent.
                    # Keep the reservation OPEN until reconciliation proves the outcome.
                    pass
                elif exc.exit_code == 75:
                    attempt.defer(exc, clock=self.clock, lock_held=True)
                else:
                    attempt.fail(exc, clock=self.clock, lock_held=True)
                # An ambiguous create intentionally remains OPEN.  Recovery/reconciliation
                # must establish whether the provider accepted it before any retry.
                raise
            run_id = payload.get("id")
            if not isinstance(run_id, str) or not run_id.strip():
                error = RemoteError("malformed-response", "create response carries no run id")
                raise error
            record = {
                "schema_version": SCHEMA_VERSION,
                "kind": "cursor-cloud-session",
                "backend": self.name,
                "dispatch_id": dispatch_id,
                "run_id": run_id,
                "assignment_digest": digest,
                "task_id": normalised["task_id"],
                "project_id": normalised["project_id"],
                "source_repository": normalised["source_repository"],
                "source_branch": normalised["source_branch"],
                "source_sha": normalised["source_sha"],
                "target_branch": body["target"]["branchName"],
                "capacity_pool": self.manifest["capacity_pool"],
                "host_id": self.manifest["host_id"],
                "state": "created",
                "vendor_state": str(payload.get("status") or "CREATING"),
                "artifacts": [],
                "reconciliation": None,
                "created_at": self._now(),
                "updated_at": self._now(),
                "billing_basis": self.manifest["billing_basis"],
                "on_demand": self.manifest["on_demand"],
                "provider": normalised["provider"],
                "authorized_repositories": ([{
                    "repository": normalised["source_repository"],
                    "source_branch": normalised["source_branch"],
                    "source_sha": normalised["source_sha"],
                }] + normalised["authorized_repositories"]),
            }
            write_session(self.base, self.name, dispatch_id, record, lock_held=True)
            attempt.succeed("created", {"run_id": run_id}, clock=self.clock, lock_held=True)
            return record

    # -- status / stream ------------------------------------------------------------------

    def get_status(self, dispatch_id: str) -> dict:
        with outbound_admission(self.base, self.name, "a Cursor Cloud status query"):
            session = read_session(self.base, self.name, dispatch_id, lock_held=True)
            payload = self._call("GET", f"/v0/agents/{session['run_id']}")
            state = map_vendor_state(payload.get("status"))
            session["state"] = state
            session["vendor_state"] = str(payload.get("status"))
            session["updated_at"] = self._now()
            write_session(self.base, self.name, dispatch_id, session, lock_held=True)
            return session

    def poll_status(self, dispatch_id: str, *, max_polls: int = 5, base_delay: int = 2,
                    max_delay: int = 60, sleeper=None) -> dict:
        """Status with bounded exponential backoff. ``sleeper`` is injected so the controls
        exercise the schedule without spending wall-clock."""
        if max_polls < 1:
            raise RemoteError("request-invalid", "max_polls must be at least 1")
        sleep = sleeper if sleeper is not None else time.sleep
        session = None
        for poll in range(max_polls):
            session = self.get_status(dispatch_id)
            if session["state"] in SESSION_TERMINAL_STATES:
                return session
            if poll + 1 < max_polls:
                sleep(min(max_delay, base_delay * (2 ** poll)))
        return session

    def stream_events(self, dispatch_id: str):
        """Yield decoded run events. Server-sent-event framing is tolerated; a malformed
        payload is a typed error, never a skipped line."""
        with outbound_admission(self.base, self.name, "a Cursor Cloud status stream"):
            session = read_session(self.base, self.name, dispatch_id, lock_held=True)
            url = self._url(f"/v0/agents/{session['run_id']}/events")
            assert_not_paused(self.base, "a Cursor Cloud status stream")
            for line in self.transport.stream_lines("GET", url, self._headers(), None,
                                                    self.manifest["timeout_seconds"]):
                text = line.strip()
                if not text or text.startswith(":"):
                    continue
                if text.startswith("data:"):
                    text = text[len("data:"):].strip()
                if text == "[DONE]":
                    return
                try:
                    event = json.loads(text)
                except json.JSONDecodeError as exc:
                    raise RemoteError("malformed-response",
                                      f"stream carried a line that is not JSON: {exc}") from exc
                if not isinstance(event, dict):
                    raise RemoteError("malformed-response", "stream event is not a JSON object")
                yield event

    # -- cancel ---------------------------------------------------------------------------

    def cancel(self, dispatch_id: str) -> dict:
        assert_not_paused(self.base, "a Cursor Cloud cancellation")
        with outbound_admission(self.base, self.name, "a Cursor Cloud cancellation"):
            self._assert_credential()
            session = read_session(self.base, self.name, dispatch_id, lock_held=True)
            attempt = self._begin(dispatch_id, "cancel", session["assignment_digest"],
                                  canonical_digest({"run_id": session["run_id"]}),
                                  lock_held=True)
            if attempt.replayed:
                return read_session(self.base, self.name, dispatch_id, lock_held=True)
            if attempt.unreconciled:
                raise RemoteError("unreconciled-attempt",
                                  f"cancel attempt {attempt.attempt_id} was left open; reconcile "
                                  "the run's observed state before cancelling again")
            try:
                payload = self._call("POST", f"/v0/agents/{session['run_id']}/cancel")
            except RemoteError as exc:
                if exc.code in AMBIGUOUS_MUTATION_ERRORS:
                    # A cancel transport failure is also ambiguous: the provider may have
                    # accepted the request even when the client did not receive a response.
                    pass
                elif exc.exit_code == 75:
                    attempt.defer(exc, clock=self.clock, lock_held=True)
                else:
                    attempt.fail(exc, clock=self.clock, lock_held=True)
                raise
            # Only the provider's terminal CANCELLED state is cancellation success.  Missing,
            # active, completed, and unknown states leave the attempt OPEN for reconciliation;
            # callers must never infer success from the fact that a cancel was requested.
            raw_status = payload.get("status")
            if raw_status is None:
                raise RemoteError("malformed-response",
                                  "cancel response has no provider status; cancellation is "
                                  "unknown and remains reconcilable")
            state = map_vendor_state(raw_status)
            session["state"] = state
            session["vendor_state"] = str(raw_status)
            session["updated_at"] = self._now()
            write_session(self.base, self.name, dispatch_id, session, lock_held=True)
            if state != "cancelled":
                raise RemoteError("unreconciled-attempt",
                                  f"provider reported {raw_status!r}, not terminal CANCELLED; "
                                  "cancellation remains reconcilable")
            attempt.succeed("cancelled", {"run_id": session["run_id"]},
                            clock=self.clock, lock_held=True)
            return session

    # -- artifacts ------------------------------------------------------------------------

    def list_artifacts(self, dispatch_id: str) -> list[dict]:
        with outbound_admission(self.base, self.name, "a Cursor Cloud artifact listing"):
            session = read_session(self.base, self.name, dispatch_id, lock_held=True)
            payload = self._call("GET", f"/v0/agents/{session['run_id']}/artifacts")
            artifacts = payload.get("artifacts")
            if not isinstance(artifacts, list):
                raise RemoteError("malformed-response", "artifacts response is not a list")
            out: list[dict] = []
            for item in artifacts:
                if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                    raise RemoteError("malformed-response", "artifact entry has no string id")
                out.append({"id": item["id"], "name": str(item.get("name") or ""),
                            "bytes": int(item.get("bytes") or 0)})
            return out

    def download_artifact(self, dispatch_id: str, artifact_id: str) -> tuple[bytes, dict]:
        """Return the bytes and an evidence row. Artifacts are ADVISORY: a vendor-produced
        file is an input to verification, never the verification."""
        if not isinstance(artifact_id, str) or not artifact_id.strip():
            raise RemoteError("request-invalid", "artifact id must be a nonempty string")
        with outbound_admission(self.base, self.name, "a Cursor Cloud artifact download"):
            session = read_session(self.base, self.name, dispatch_id, lock_held=True)
            assert_not_paused(self.base, "a Cursor Cloud artifact download")
            response = self.transport.request(
                "GET", self._url(f"/v0/agents/{session['run_id']}/artifacts/{artifact_id}"),
                self._headers(), None, self.manifest["timeout_seconds"])
            classify_status(response.status, response.body)
            row = {
                "id": artifact_id,
                "sha256": hashlib.sha256(response.body).hexdigest(),
                "bytes": len(response.body),
                "evidence_class": "advisory",
                "observed_at": self._now(),
            }
            session["artifacts"] = [entry for entry in session.get("artifacts", [])
                                    if entry.get("id") != artifact_id] + [row]
            session["updated_at"] = self._now()
            write_session(self.base, self.name, dispatch_id, session, lock_held=True)
            return response.body, row

    # -- usage ----------------------------------------------------------------------------

    def get_usage(self, dispatch_id: str) -> dict:
        """Token usage attributed to the capacity POOL that paid for it.

        ``spend_state`` is derived from the manifest's billing basis and never from the
        vendor payload: an unreconciled metered run must not be able to report itself as
        included usage (plan Phase 3 gate).
        """
        with outbound_admission(self.base, self.name, "a Cursor Cloud usage query"):
            session = read_session(self.base, self.name, dispatch_id, lock_held=True)
            payload = self._call("GET", f"/v0/agents/{session['run_id']}/usage")
            tokens = payload.get("usage") if isinstance(payload.get("usage"), dict) else payload
            counts: dict[str, int] = {}
            for field in ("input_tokens", "output_tokens", "cache_read_tokens", "total_tokens"):
                value = tokens.get(field)
                if value is None:
                    continue
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise RemoteError("malformed-response",
                                      f"usage.{field} is not a non-negative integer")
                counts[field] = value
            # These values were captured from the validated assignment and selected manifest at
            # admission. Provider response fields such as ``billing`` and ``included`` are not
            # authorization data and are intentionally ignored.
            basis = session.get("billing_basis")
            on_demand = session.get("on_demand")
            provider = session.get("provider")
            if basis not in ("included", "metered", "local") or not isinstance(on_demand, bool):
                raise RemoteError("malformed-response",
                                  "session lacks authorized billing attribution")
            if not isinstance(provider, str) or not provider:
                raise RemoteError("malformed-response", "session lacks authorized provider")
            spend_state = ("included" if basis == "included" and not on_demand
                           else "local" if basis == "local" and not on_demand
                           else "metered-unreconciled")
            record = {
                "schema_version": SCHEMA_VERSION,
                "kind": "cursor-cloud-usage",
                "backend": self.name,
                "dispatch_id": dispatch_id,
                "run_id": session["run_id"],
                "assignment_digest": session["assignment_digest"],
                "provider": provider,
                "capacity_pool": self.manifest["capacity_pool"],
                "host_id": self.manifest["host_id"],
                "billing_basis": basis,
                "on_demand": on_demand,
                "spend_state": spend_state,
                "tokens": counts,
                "observed_at": self._now(),
            }
            write_usage(self.base, self.name, dispatch_id, record, lock_held=True)
            return record

    # -- returned ref / commit reconciliation ----------------------------------------------

    @staticmethod
    def _authorized_scope(session: dict,
                          requested: list[str] | list[dict] | None) -> dict[str, dict]:
        authoritative = session.get("authorized_repositories")
        if not isinstance(authoritative, list) or not authoritative:
            raise RemoteError("malformed-response",
                              "session lacks the immutable authorized repository scope")
        by_repo = {}
        for item in authoritative:
            if not isinstance(item, dict) or set(item) != {
                    "repository", "source_branch", "source_sha"}:
                raise RemoteError("malformed-response", "session repository scope is malformed")
            by_repo[item["repository"]] = item
        if requested is None:
            return by_repo
        selected: dict[str, dict] = {}
        for item in requested:
            if isinstance(item, str):
                repository = item
                expected = by_repo.get(repository)
            elif isinstance(item, dict):
                repository = item.get("repository")
                expected = by_repo.get(repository)
                if expected is None or item != expected:
                    expected = None
            else:
                expected = None
                repository = item
            if expected is None:
                raise RemoteError("unauthorized-result",
                                  f"requested repository {repository!r} is outside the "
                                  "immutable assignment scope or lacks its pinned source")
            selected[repository] = expected
        if not selected:
            raise RemoteError("unauthorized-result", "authorized repository selection is empty")
        return selected

    def reconciliation_input(self, dispatch_id: str, vendor_result: dict,
                             authorized_repositories: list[str] | list[dict] | None = None) -> dict:
        """Turn a vendor result into the INPUT to independent verification.

        Every returned branch and commit is recorded per repository, because a run that
        touched three repositories produced three candidates and each needs its own source
        sha, result commit, diff and gate (plan, "Cursor Cloud adapter").

        This function cannot approve anything. Its output always carries
        ``verification_state = requires-independent-verification`` and
        ``vendor_self_report_is_evidence = false``.
        """
        session = read_session(self.base, self.name, dispatch_id)
        publication = self.manifest["publication"]
        if not isinstance(vendor_result, dict):
            raise RemoteError("malformed-response", "vendor result must be a JSON object")

        entries = vendor_result.get("repositories")
        if entries is None:
            target = vendor_result.get("target")
            if not isinstance(target, dict):
                raise RemoteError("malformed-response",
                                  "vendor result carries neither a repositories list nor a "
                                  "target block")
            entries = [{
                "repository": target.get("repository", session["source_repository"]),
                "branch": target.get("branchName"),
                "commit": target.get("commit"),
            }]
        if not isinstance(entries, list) or not entries:
            raise RemoteError("malformed-response",
                              "vendor result repositories must be a nonempty list")

        authorized = self._authorized_scope(session, authorized_repositories)
        rows: list[dict] = []
        seen_repositories: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise RemoteError("malformed-response", "repository result is not an object")
            repository = entry.get("repository")
            branch = entry.get("branch")
            commit = entry.get("commit")
            if not isinstance(repository, str):
                raise RemoteError("malformed-response", "returned repository is not a string")
            try:
                validate_repository_url(repository, "returned repository")
            except RemoteError as exc:
                raise RemoteError("unauthorized-result",
                                  "vendor returned a repository outside the URL contract") from exc
            if repository not in authorized:
                raise RemoteError("unauthorized-result",
                                  f"vendor returned a result for repository {repository!r}, "
                                  "which this assignment did not authorise")
            if not isinstance(commit, str) or not SHA_RE.fullmatch(commit):
                raise RemoteError("malformed-response",
                                  f"returned commit for {repository} is not a 40-hex sha")
            if not isinstance(branch, str):
                raise RemoteError("malformed-response",
                                  f"returned branch for {repository} is not a string")
            try:
                valid_branch = branch_is_allowed(branch, publication)
            except RemoteError as exc:
                raise RemoteError("unauthorized-result",
                                  f"vendor returned an invalid branch for {repository}; "
                                  "the result is outside the assignment confinement") from exc
            if not valid_branch:
                raise RemoteError("unauthorized-result",
                                  f"vendor returned branch {branch!r} for {repository}: it is "
                                  "the default or integration branch, or does not match "
                                  "publication.allowed_result_branch_patterns")
            if repository in seen_repositories:
                raise RemoteError("unauthorized-result",
                                  f"vendor returned duplicate results for {repository}")
            seen_repositories.add(repository)
            pinned = authorized[repository]
            if commit == pinned["source_sha"]:
                raise RemoteError("unauthorized-result",
                                  f"returned commit for {repository} equals source_sha; the "
                                  "run produced no candidate to verify")
            rows.append({
                "repository": repository,
                "source_branch": pinned["source_branch"],
                "source_sha": pinned["source_sha"],
                "result_branch": branch,
                "result_commit": commit,
                "verification_state": VERIFICATION_STATE,
            })

        vendor_status = vendor_result.get("status")
        record = {
            "schema_version": SCHEMA_VERSION,
            "kind": "cursor-cloud-reconciliation-input",
            "backend": self.name,
            "dispatch_id": dispatch_id,
            "run_id": session["run_id"],
            "assignment_digest": session["assignment_digest"],
            "repositories": rows,
            "verification_state": VERIFICATION_STATE,
            "vendor_self_report_is_evidence": False,
            "gate_evidence": None,
            "required_independent_checks": list(REQUIRED_INDEPENDENT_CHECKS),
            # The vendor's own claims are kept as a digest and a key inventory, not ingested.
            # Recording them verbatim would put unvetted vendor text into canonical evidence;
            # recording nothing would lose attributability when the two later disagree.
            "advisory_only": {
                "vendor_reported_state": str(vendor_status) if vendor_status is not None else "",
                "vendor_report_digest": canonical_digest(vendor_result),
                "vendor_claim_keys": sorted(str(key) for key in vendor_result),
            },
            "observed_at": self._now(),
        }
        session["reconciliation"] = record
        session["updated_at"] = self._now()
        write_session(self.base, self.name, dispatch_id, session)
        return record

    # -- restart recovery ------------------------------------------------------------------

    def recover(self, *, query_provider: bool = True) -> dict:
        """Reconstruct in-flight vendor state after a controller restart.

        The local half always runs: enumerating open attempts and non-terminal sessions is
        awareness, and awareness survives PAUSE. The provider half is an external effect and
        is skipped while PAUSE is present -- the report says so rather than pretending the
        state is known.
        """
        pending_attempts = open_attempts(self.base, self.name)
        active = [session for session in list_sessions(self.base, self.name)
                  if session.get("state") in SESSION_ACTIVE_STATES]
        paused = is_paused(self.base)
        report = {
            "schema_version": SCHEMA_VERSION,
            "kind": "cursor-cloud-recovery",
            "backend": self.name,
            "paused": paused,
            "provider_queried": bool(query_provider and not paused),
            "open_attempts": [row["attempt_id"] for row in pending_attempts],
            "active_sessions": [row["dispatch_id"] for row in active],
            "reconciled": [],
            "unreconciled": [],
            "ambiguous_create_attempts": [],
            "observed_at": self._now(),
        }
        if paused or not query_provider:
            report["unreconciled"] = [row["attempt_id"] for row in pending_attempts]
            return report
        for row in pending_attempts:
            dispatch_id = row.get("dispatch_id", "")
            try:
                session = self.get_status(dispatch_id)
            except RemoteError as exc:
                # An attempt whose outcome cannot be established stays a question. It is never
                # reopened for re-sending; a human closes it.
                reconcile_attempt(self.base, self.name, row["attempt_id"], observed="unknown",
                                  observer=f"{PROG}:recover", detail={
                                      "error": exc.code,
                                      "ambiguity": "create-outcome-unknown"
                                      if row.get("operation") == "create" else "provider-state-unknown",
                                  },
                                  clock=self.clock)
                report["unreconciled"].append(row["attempt_id"])
                if row.get("operation") == "create":
                    report["ambiguous_create_attempts"].append(row["attempt_id"])
                continue
            if row.get("operation") == "cancel":
                observed = "landed" if session.get("state") == "cancelled" else "unknown"
            else:
                observed = "landed" if session.get("run_id") else "unknown"
            reconcile_attempt(self.base, self.name, row["attempt_id"], observed=observed,
                              observer=f"{PROG}:recover",
                              detail={
                                  "vendor_state": session.get("vendor_state", ""),
                                  "ambiguity": "create-outcome-unknown"
                                  if observed == "unknown" and row.get("operation") == "create"
                                  else "provider-state-nonterminal"
                                  if observed == "unknown" else "",
                              },
                              clock=self.clock)
            if observed == "unknown":
                report["unreconciled"].append(row["attempt_id"])
                if row.get("operation") == "create":
                    report["ambiguous_create_attempts"].append(row["attempt_id"])
            else:
                report["reconciled"].append(row["attempt_id"])
        return report


# --- CLI -----------------------------------------------------------------------------------

def build_adapter(base: Path, name: str) -> CursorCloudAdapter:
    manifest = resolve_backend(name, kind=BACKEND_KIND)
    # No transport is constructed here beyond the refusing one unless the human-owned live
    # flag is set; HttpsTransport enforces that itself.
    from remote_backend import HttpsTransport  # imported late so import-time is side-effect free

    transport: Transport = RefusingTransport()
    try:
        transport = HttpsTransport()
    except RemoteError:
        pass
    return CursorCloudAdapter(base, manifest, transport)


def main() -> int:
    parser = argparse.ArgumentParser(prog=PROG, description=__doc__.splitlines()[0])
    parser.add_argument("--base", default=".", help="repository root (default: .)")
    parser.add_argument("--backend", default="cursor-cloud", help="manifest name")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("validate", help="validate every remote backend manifest")
    sub.add_parser("models", help="list models offered to this account")
    recover = sub.add_parser("recover", help="reconstruct in-flight vendor state")
    recover.add_argument("--local-only", action="store_true",
                         help="skip the provider query; report local awareness only")
    status = sub.add_parser("status", help="query one dispatch")
    status.add_argument("dispatch_id")
    cancel = sub.add_parser("cancel", help="cancel one dispatch")
    cancel.add_argument("dispatch_id")
    usage = sub.add_parser("usage", help="token usage for one dispatch")
    usage.add_argument("dispatch_id")
    args = parser.parse_args()

    if args.command is None:
        parser.print_help(sys.stderr)
        return 2
    if args.command == "validate":
        return validate_directory()

    base = Path(args.base).resolve()
    try:
        adapter = build_adapter(base, args.backend)
        if args.command == "models":
            result: object = adapter.list_models()
        elif args.command == "recover":
            result = adapter.recover(query_provider=not args.local_only)
        elif args.command == "status":
            result = adapter.get_status(args.dispatch_id)
        elif args.command == "cancel":
            result = adapter.cancel(args.dispatch_id)
        else:
            result = adapter.get_usage(args.dispatch_id)
    except RemoteError as exc:
        diag(str(exc))
        return exc.exit_code
    print(json.dumps(result, indent=2, sort_keys=True))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())

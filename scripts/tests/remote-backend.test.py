#!/usr/bin/env python3
"""Control: remote backend manifests, transport gating, durable attempts, lease, PAUSE.

Frozen contract: scripts/remote_backend.py, scripts/remote/README.md, and
schemas/control-plane/v1/remote-backend.schema.json.

Exit-code roles under test: 3 = absent or disabled (nothing to run, and that is not an
error), 2 = present but invalid, 4 = refused by policy, 10 = retryable, 75 = defer.

The load-bearing checks:
  * validation happens BEFORE enablement, so a broken manifest reports as broken rather than
    hiding behind a disabled flag until the day someone flips it;
  * HttpsTransport cannot be constructed without RECURSION_REMOTE_LIVE=1 -- which is how this
    suite proves it never opens a socket;
  * an attempt is committed before I/O, a duplicate is replayed rather than re-sent, and one
    left open by a dead process is a question rather than a retry.

Hermetic: tempdirs only, no network, no box environment.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SOURCE / "scripts"))

import remote_backend as rb  # noqa: E402
from remote_assignment import RemoteError  # noqa: E402

failures: list[str] = []
TEMPDIRS: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def raises(code: str, fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except RemoteError as exc:
        if exc.code == code:
            return True
        print(f"     (got {exc.code}, wanted {code}: {exc})")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"     (got {type(exc).__name__}: {exc})")
        return False
    return False


def tempdir() -> Path:
    path = tempfile.mkdtemp(prefix="recursion-remote-test-")
    TEMPDIRS.append(path)
    return Path(path)


def clear_flags() -> None:
    for name in list(os.environ):
        if name.startswith("RECURSION_REMOTE") or name == "RECURSION_ALLOW_METERED":
            os.environ.pop(name, None)


CURSOR_MANIFEST = {
    "schema_version": 1,
    "name": "cursor-cloud",
    "kind": "cursor-cloud",
    "description": "control fixture",
    "endpoint": "https://api.cursor.com",
    "endpoint_ref": None,
    "credential_ref": "secret:CURSOR_CLOUD_API_KEY",
    "signing_key_ref": None,
    "capacity_pool": "cursor-cloud-pool",
    "host_id": "cursor-cloud",
    "billing_basis": "included",
    "on_demand": False,
    "timeout_seconds": 60,
    "max_attempts": 3,
    "concurrency_lease": 2,
    "publication": {
        "default_branch": "main",
        "integration_branch": "recursion/integration",
        "task_branch_pattern": "recursion/extern/<task-id>",
        "allowed_result_branch_patterns": ["recursion/extern/*", "cursor/*"],
    },
}

GROK_MANIFEST = {
    "schema_version": 1,
    "name": "grok-bot",
    "kind": "grok-routine",
    "description": "control fixture",
    "endpoint": None,
    "endpoint_ref": "secret:GROK_ROUTINE_WEBHOOK_URL",
    "credential_ref": "secret:GROK_ROUTINE_SENDER_ID",
    "signing_key_ref": "secret:GROK_ROUTINE_SIGNING_SECRET",
    "capacity_pool": "grok-bot-weekly",
    "host_id": "grok-bot-account-cloud",
    "billing_basis": "included",
    "on_demand": False,
    "timeout_seconds": 30,
    "max_attempts": 3,
    "concurrency_lease": 1,
    "publication": {
        "default_branch": "main",
        "integration_branch": "recursion/integration",
        "task_branch_pattern": "recursion/extern/grok/<task-id>",
        "allowed_result_branch_patterns": ["recursion/extern/grok/*"],
    },
}


def copy(manifest: dict) -> dict:
    return json.loads(json.dumps(manifest))


def mutated(manifest: dict, **overrides) -> dict:
    out = copy(manifest)
    out.update(overrides)
    return out


def with_publication(manifest: dict, **overrides) -> dict:
    out = copy(manifest)
    out["publication"].update(overrides)
    return out


def write_manifest(directory: Path, manifest: dict, stem: str | None = None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{stem or manifest['name']}.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


# --- the shipped examples -------------------------------------------------------------------

EXAMPLES = SOURCE / "scripts" / "remote" / "examples"
example_paths = sorted(EXAMPLES.glob("*.json.example"))
check(len(example_paths) == 2, "both remote backend examples ship")
for example in example_paths:
    stem = example.name[: -len(".json.example")]
    payload = json.loads(example.read_text(encoding="utf-8"))
    try:
        rb.validate_manifest(payload, stem)
        valid = True
    except RemoteError as exc:
        valid = False
        print(f"     ({example.name}: {exc})")
    check(valid, f"the shipped example {example.name} satisfies the manifest contract")

check(not sorted((SOURCE / "scripts" / "remote").glob("*.json")),
      "scripts/remote/ ships no loadable manifest -- an example cannot resolve by accident")

# --- manifest validation ----------------------------------------------------------------------

check(rb.validate_manifest(CURSOR_MANIFEST, "cursor-cloud")["name"] == "cursor-cloud",
      "a well-formed cursor-cloud manifest validates")
check(rb.validate_manifest(GROK_MANIFEST, "grok-bot")["kind"] == "grok-routine",
      "a well-formed grok-routine manifest validates")

check(raises("manifest-invalid", rb.validate_manifest, CURSOR_MANIFEST, "other-name"),
      "name must equal the filename stem")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, schema_version=2), "cursor-cloud"),
      "an unknown schema_version is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, kind="something-else"), "cursor-cloud"),
      "an unknown backend kind is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, extra_field=1), "cursor-cloud"),
      "an unknown manifest key is refused")
missing = copy(CURSOR_MANIFEST)
del missing["host_id"]
check(raises("manifest-invalid", rb.validate_manifest, missing, "cursor-cloud"),
      "a missing manifest key is refused")

check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, endpoint_ref="secret:SOMEWHERE"), "cursor-cloud"),
      "setting both endpoint and endpoint_ref is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, endpoint=None), "cursor-cloud"),
      "setting neither endpoint nor endpoint_ref is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, endpoint="http://api.cursor.com"), "cursor-cloud"),
      "a plain http endpoint is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, endpoint=None, endpoint_ref="secret:CURSOR_ENDPOINT"),
                    "cursor-cloud"),
      "cursor-cloud requires its public endpoint form")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(GROK_MANIFEST, endpoint="https://api.cursor.com", endpoint_ref=None), "grok-bot"),
      "grok-routine requires its bearer-grade endpoint reference form")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, endpoint="https://u:p@api.cursor.com"), "cursor-cloud"),
      "an endpoint carrying userinfo is refused")

check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, credential_ref="cur-live-abcdef"), "cursor-cloud"),
      "a literal credential where a reference belongs is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, credential_ref="secret:GITHUB_TOKEN"), "cursor-cloud"),
      "a reference to a controller/deploy credential is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, signing_key_ref="secret:SOME_SIGNING_SECRET"),
             "cursor-cloud"),
      "a non-grok backend may not declare a signing key")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(GROK_MANIFEST, signing_key_ref=None), "grok-bot"),
      "a grok-routine backend without a signing key is refused -- unsigned is unauthenticated")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(GROK_MANIFEST, signing_key_ref=GROK_MANIFEST["credential_ref"]),
             "grok-bot"),
      "the signing key and the sender credential must differ")

check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, billing_basis="free"), "cursor-cloud"),
      "an unknown billing basis is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, concurrency_lease=0), "cursor-cloud"),
      "a zero-width lease is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, max_attempts=99), "cursor-cloud"),
      "an unbounded attempt budget is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, timeout_seconds=True), "cursor-cloud"),
      "a boolean where an integer belongs is refused")

check(raises("manifest-invalid", rb.validate_manifest,
             with_publication(CURSOR_MANIFEST, integration_branch="main"), "cursor-cloud"),
      "the integration branch may not be the default branch")
check(raises("manifest-invalid", rb.validate_manifest,
             with_publication(CURSOR_MANIFEST, task_branch_pattern="recursion/extern/fixed"),
             "cursor-cloud"),
      "a task branch pattern without <task-id> is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             with_publication(CURSOR_MANIFEST, allowed_result_branch_patterns=["*"]),
             "cursor-cloud"),
      "an unrestricted result-branch wildcard is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             with_publication(CURSOR_MANIFEST, allowed_result_branch_patterns=[]),
             "cursor-cloud"),
      "an empty result-branch pattern list is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, description="token is sk-" + "a" * 32), "cursor-cloud"),
      "a credential pasted into a manifest field is refused by the secret screen")

# --- resolution and the enablement chain -------------------------------------------------------

clear_flags()
directory = tempdir()
write_manifest(directory, CURSOR_MANIFEST)
write_manifest(directory, GROK_MANIFEST)
os.environ["RECURSION_REMOTE_DIR"] = str(directory)

check(raises("manifest-absent", rb.resolve_backend, "not-configured"),
      "an absent manifest is absent (3), not an error")
check(raises("request-invalid", rb.resolve_backend, "Not A Name"),
      "a malformed backend name is a request error")
check(raises("adapter-disabled", rb.resolve_backend, "cursor-cloud"),
      "with RECURSION_REMOTE_ADAPTERS unset, a valid backend is disabled (3)")

os.environ["RECURSION_REMOTE_ADAPTERS"] = "1"
check(raises("adapter-disabled", rb.resolve_backend, "cursor-cloud"),
      "the master switch alone does not enable a backend")
os.environ["RECURSION_REMOTE_CURSOR_CLOUD_ENABLED"] = "1"
resolved = rb.resolve_backend("cursor-cloud")
check(resolved["capacity_pool"] == "cursor-cloud-pool",
      "both flags plus a valid manifest resolve the backend")
check(raises("manifest-invalid", rb.resolve_backend, "cursor-cloud", "grok-routine"),
      "resolving with the wrong expected kind is refused")

broken = copy(CURSOR_MANIFEST)
del broken["publication"]
broken["name"] = "broken"
write_manifest(directory, broken)
clear_flags()
os.environ["RECURSION_REMOTE_DIR"] = str(directory)
check(raises("manifest-invalid", rb.resolve_backend, "broken"),
      "a BROKEN manifest reports invalid (2) even while the flags are off -- validation "
      "precedes enablement so a latent break is not hidden until someone flips a flag")

metered = mutated(CURSOR_MANIFEST, name="metered-one", billing_basis="metered")
write_manifest(directory, metered)
os.environ["RECURSION_REMOTE_ADAPTERS"] = "1"
os.environ["RECURSION_REMOTE_METERED_ONE_ENABLED"] = "1"
check(raises("adapter-disabled", rb.resolve_backend, "metered-one"),
      "a metered backend without RECURSION_ALLOW_METERED is disabled, not admitted")
os.environ["RECURSION_ALLOW_METERED"] = "1"
check(rb.resolve_backend("metered-one")["billing_basis"] == "metered",
      "a metered backend is admitted only once a human sets the metered flag")
os.environ.pop("RECURSION_ALLOW_METERED", None)
ondemand = mutated(CURSOR_MANIFEST, name="ondemand-one", on_demand=True)
write_manifest(directory, ondemand)
os.environ["RECURSION_REMOTE_ONDEMAND_ONE_ENABLED"] = "1"
check(raises("adapter-disabled", rb.resolve_backend, "ondemand-one"),
      "an on-demand backend without the metered flag is disabled")

check(rb.validate_directory() == 2,
      "--validate reports 2 when the directory holds an invalid manifest")
(directory / "broken.json").unlink()
check(rb.validate_directory() == 0,
      "--validate reports 0 once every manifest in the directory is valid")

# --- endpoint resolution -----------------------------------------------------------------------

check(rb.backend_endpoint(CURSOR_MANIFEST) == "https://api.cursor.com",
      "a literal endpoint resolves without touching the environment")
os.environ.pop("GROK_ROUTINE_WEBHOOK_URL", None)
check(raises("credential-absent", rb.backend_endpoint, GROK_MANIFEST),
      "an endpoint_ref with no env value is absent, not empty")
os.environ["GROK_ROUTINE_WEBHOOK_URL"] = "not a url"
check(raises("credential-absent", rb.backend_endpoint, GROK_MANIFEST),
      "a malformed webhook URL is refused")
try:
    rb.backend_endpoint(GROK_MANIFEST)
    leak_message = ""
except RemoteError as exc:
    leak_message = str(exc)
check("not a url" not in leak_message,
      "the refusal does not echo the bearer-grade webhook value")
os.environ["GROK_ROUTINE_WEBHOOK_URL"] = "https://hooks.example.com/routines/abc?v=1"
check(rb.backend_endpoint(GROK_MANIFEST).endswith("?v=1"),
      "a webhook URL with a query string resolves")

# --- transport gating ---------------------------------------------------------------------------

os.environ.pop("RECURSION_REMOTE_LIVE", None)
check(raises("live-transport-disabled", rb.HttpsTransport),
      "the live transport refuses to be CONSTRUCTED without RECURSION_REMOTE_LIVE=1 -- this "
      "suite therefore cannot open a socket")
os.environ["RECURSION_REMOTE_LIVE"] = "1"
live = rb.HttpsTransport()
check(isinstance(live, rb.Transport),
      "with the human-owned live flag set, the transport constructs (and only then)")
os.environ.pop("RECURSION_REMOTE_LIVE", None)

refusing = rb.RefusingTransport()
check(raises("live-transport-disabled", refusing.request, "GET", "https://x/y", {}, None, 5),
      "the default transport refuses every request")
check(raises("live-transport-disabled", lambda: list(
    refusing.stream_lines("GET", "https://x/y", {}, None, 5))),
      "the default transport refuses every stream")

check(rb.TransportResponse(200, {"X-A": "b"}, b'{"a":1}').json() == {"a": 1},
      "a JSON body parses")
check(raises("malformed-response", rb.TransportResponse(200, {}, b"not json").json),
      "a non-JSON body is a typed malformed-response")
check(raises("malformed-response", rb.TransportResponse(200, {}, b"[1,2]").json),
      "a JSON array where an object belongs is a malformed-response")

# --- status classification -------------------------------------------------------------------------

rb.classify_status(200, b"")
rb.classify_status(204, b"")
for status, code in ((401, "auth-failed"), (403, "auth-failed"), (404, "not-found"),
                     (402, "quota-exhausted"), (429, "rate-limited"),
                     (503, "provider-unavailable"), (500, "provider-error"),
                     (502, "provider-error"), (400, "request-invalid")):
    check(raises(code, rb.classify_status, status, b"body"),
          f"HTTP {status} classifies as {code}")
try:
    rb.classify_status(500, b"ghp_" + b"a" * 36)
    status_message = ""
except RemoteError as exc:
    status_message = str(exc)
check("ghp_" not in status_message and "body" not in status_message,
      "HTTP response bodies never enter durable error text")
check(RemoteError("quota-exhausted", "x").exit_code == 75,
      "quota exhaustion DEFERS (75); it is never an argument for spending")
check(RemoteError("rate-limited", "x").exit_code == 10,
      "a rate limit is retryable (10), distinct from quota exhaustion")

# --- PAUSE ------------------------------------------------------------------------------------------

base = tempdir()
(base / "state").mkdir(parents=True, exist_ok=True)
check(rb.is_paused(base) is False, "an unpaused base reports unpaused")
rb.assert_not_paused(base, "a probe")
(base / "state" / "PAUSE").write_text("held\n", encoding="utf-8")
check(rb.is_paused(base) is True, "a PAUSE file is observed")
check(raises("paused", rb.assert_not_paused, base, "a probe"),
      "PAUSE refuses an external effect with a policy refusal (4)")
(base / "state" / "PAUSE").unlink()

# --- durable attempts ----------------------------------------------------------------------------------

DIGEST = "d" * 64
REQUEST = "r" * 64


def begin(base_dir: Path, *, dispatch_id="dispatch-0001", operation="dispatch",
          digest=DIGEST, request=REQUEST, max_attempts=3):
    return rb.begin_attempt(base_dir, "grok-bot", dispatch_id=dispatch_id,
                            operation=operation, assignment_digest=digest,
                            request_digest=request, max_attempts=max_attempts)


attempts_base = tempdir()
(attempts_base / "state").mkdir(parents=True, exist_ok=True)

check(raises("request-invalid", begin, attempts_base, dispatch_id="short"),
      "a malformed dispatch id is refused before anything is committed")

first = begin(attempts_base)
check(first.record["state"] == "open" and first.record["attempt_number"] == 1,
      "the first attempt is committed OPEN before any I/O")
check(rb.attempts_journal(attempts_base, "grok-bot").is_file(),
      "the durable attempt journal exists on disk")
check(rb.attempt_projection(attempts_base, "grok-bot", first.attempt_id).is_file(),
      "the attempt projection exists beside the journal")

crashed = begin(attempts_base)
check(crashed.unreconciled and crashed.attempt_id == first.attempt_id,
      "a second call while the first is OPEN returns it as unreconciled -- an open attempt is "
      "a question, not a licence to re-send")
check(rb.open_attempts(attempts_base, "grok-bot")[0]["attempt_id"] == first.attempt_id,
      "restart recovery finds the open attempt")

first.succeed("dispatched", {"routine_run_id": "r-1"})
replay = begin(attempts_base)
check(replay.replayed and replay.record["state"] == "succeeded",
      "once the attempt has succeeded, an identical call REPLAYS instead of re-sending")
check(raises("request-invalid", replay.succeed),
      "a replayed handle cannot be closed again")
check(not rb.open_attempts(attempts_base, "grok-bot"),
      "no attempt remains open after success")

different = begin(attempts_base, request="s" * 64)
check(not different.replayed and different.record["attempt_number"] == 1,
      "a different request body is a different idempotency key, not a replay of the first")

check(rb.idempotency_key("b", "op", DIGEST, "dispatch-0001", REQUEST)
      != rb.idempotency_key("b", "op", "e" * 64, "dispatch-0001", REQUEST),
      "rebinding the assignment changes the idempotency key, so a rebound retry cannot "
      "deduplicate against the original run")

budget_base = tempdir()
(budget_base / "state").mkdir(parents=True, exist_ok=True)
one = begin(budget_base, max_attempts=2)
one.fail(RemoteError("transport-error", "host loss"))
two = begin(budget_base, max_attempts=2)
check(two.record["attempt_number"] == 2, "a failed attempt frees the key for one more attempt")
two.fail(RemoteError("transport-error", "host loss again"))
check(raises("attempts-exhausted", begin, budget_base, max_attempts=2),
      "the attempt budget is enforced (4), not retried forever")

# --- reconciliation -------------------------------------------------------------------------------------

recon_base = tempdir()
(recon_base / "state").mkdir(parents=True, exist_ok=True)
landed = begin(recon_base, dispatch_id="dispatch-land")
closed = rb.reconcile_attempt(recon_base, "grok-bot", landed.attempt_id,
                              observed="landed", observer="lucas:grok-bot-app")
check(closed["state"] == "succeeded" and closed["detail"]["observer"] == "lucas:grok-bot-app",
      "an observation of 'landed' closes the attempt as succeeded and records the observer")
check(raises("request-invalid", rb.reconcile_attempt, recon_base, "grok-bot",
             landed.attempt_id, observed="landed", observer="lucas"),
      "an already-closed attempt cannot be reconciled twice")

missed = begin(recon_base, dispatch_id="dispatch-miss")
check(rb.reconcile_attempt(recon_base, "grok-bot", missed.attempt_id,
                           observed="not-landed", observer="lucas")["state"] == "failed",
      "an observation of 'not-landed' closes the attempt as failed, freeing a retry")

unknown = begin(recon_base, dispatch_id="dispatch-unkn")
result = rb.reconcile_attempt(recon_base, "grok-bot", unknown.attempt_id,
                              observed="unknown", observer="lucas")
check(result["state"] == "unreconciled",
      "'unknown' is TERMINAL -- guessing 'probably did not land' is how a duplicate happens")
check(not any(row["attempt_id"] == unknown.attempt_id
              for row in rb.open_attempts(recon_base, "grok-bot")),
      "an unreconciled attempt is no longer open, so recovery does not loop on it")
check(raises("request-invalid", rb.reconcile_attempt, recon_base, "grok-bot",
             unknown.attempt_id, observed="maybe", observer="lucas"),
      "an unknown observation vocabulary is refused")
check(raises("request-invalid", rb.reconcile_attempt, recon_base, "grok-bot",
             unknown.attempt_id, observed="landed", observer="  "),
      "reconciliation must record WHO observed it")
check(raises("not-found", rb.reconcile_attempt, recon_base, "grok-bot", "0" * 16 + "-1",
             observed="landed", observer="lucas"),
      "reconciling an attempt that does not exist is not-found")

# --- sessions -------------------------------------------------------------------------------------------

session_base = tempdir()
(session_base / "state").mkdir(parents=True, exist_ok=True)
rb.write_session(session_base, "grok-bot", "dispatch-0001", {"kind": "probe", "a": 1})
check(rb.read_session(session_base, "grok-bot", "dispatch-0001")["a"] == 1,
      "a session record round-trips")
check(len(rb.list_sessions(session_base, "grok-bot")) == 1, "sessions enumerate")
check(raises("not-found", rb.read_session, session_base, "grok-bot", "dispatch-absent"),
      "an absent session is not-found")
check(raises("redaction-violation", rb.write_session, session_base, "grok-bot",
             "dispatch-0002", {"note": "ghp_" + "a" * 36}),
      "a credential cannot be written into a durable session record")
check(raises("request-invalid", rb.write_session, session_base, "grok-bot", "bad id!",
             {"a": 1}),
      "a malformed dispatch id cannot name a session file")
check(raises("request-invalid", rb.write_session, session_base, "../escape", "dispatch-0002",
             {"a": 1}),
      "a backend traversal cannot escape runtime storage")

# --- the account-shared lease ------------------------------------------------------------------------------

lease_base = tempdir()
(lease_base / "state").mkdir(parents=True, exist_ok=True)
with rb.AccountLease(lease_base, "grok-bot-weekly", 1) as held:
    check(held.slot == 0 and held.path is not None, "the first lease takes slot 0")

    def take_second():
        with rb.AccountLease(lease_base, "grok-bot-weekly", 1):
            pass

    check(raises("lease-unavailable", take_second),
          "a single-slot pool refuses a second holder with a DEFER (75), not a failure -- two "
          "Bots on one account computer are one writer with two screens")

    def take_wider():
        with rb.AccountLease(lease_base, "grok-bot-weekly", 2) as second:
            return second.slot

    check(take_wider() == 1, "widening the pool to two slots admits the second holder")

with rb.AccountLease(lease_base, "grok-bot-weekly", 1) as reacquired:
    check(reacquired.slot == 0, "slot 0 is free again once the first holder released it")
check(not (lease_base / "state" / ".locks" / "remote-grok-bot-weekly-slot-0.lock").exists(),
      "the lease directory is removed on release")
check(raises("request-invalid", rb.AccountLease, lease_base, "Bad Pool", 1),
      "a malformed pool id cannot name a lease")
check(raises("request-invalid", rb.AccountLease, lease_base, "grok-bot-weekly", 0),
      "a zero-width lease is refused")

# --- cleanup -------------------------------------------------------------------------------------------------

clear_flags()
os.environ.pop("RECURSION_REMOTE_DIR", None)
os.environ.pop("GROK_ROUTINE_WEBHOOK_URL", None)
for path in TEMPDIRS:
    shutil.rmtree(path, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} check(s) failed:")
    for item in failures:
        print(f"  - {item}")
    raise SystemExit(1)
print("all checks passed")

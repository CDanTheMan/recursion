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
import math
import os
import re
import shutil
import socket
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from jsonschema import Draft7Validator, validators

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

# Manifest boundary errors use the symbolic backend name only.  A caller-controlled manifest
# directory and parser input must not put an absolute path or JSON parser/OS text into stderr.
unreadable_manifest = tempdir()
try:
    rb.load_manifest(unreadable_manifest, "cursor-cloud")
except RemoteError as exc:
    unreadable_message = str(exc)
else:
    unreadable_message = ""
check(unreadable_message == "manifest-invalid: could not read manifest cursor-cloud",
      "an unreadable manifest has a stable symbolic refusal")

malformed_manifest = tempdir() / "cursor-cloud.json"
malformed_manifest.write_text("{not-json", encoding="utf-8")
try:
    rb.load_manifest(malformed_manifest, "cursor-cloud")
except RemoteError as exc:
    malformed_message = str(exc)
else:
    malformed_message = ""
check(malformed_message == "manifest-invalid: manifest cursor-cloud is not valid JSON",
      "malformed manifest JSON hides its path and parser details")

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
for invalid_pattern in ("foo/.", "foo/.bar", "foo@{bar}"):
    check(raises("manifest-invalid", rb.validate_manifest,
                 with_publication(CURSOR_MANIFEST,
                                  allowed_result_branch_patterns=[invalid_pattern]),
                 "cursor-cloud"),
          f"a git-invalid result pattern {invalid_pattern!r} is refused before fnmatch")
check(raises("manifest-invalid", rb.validate_manifest,
             with_publication(CURSOR_MANIFEST, allowed_result_branch_patterns=[]),
             "cursor-cloud"),
      "an empty result-branch pattern list is refused")
check(raises("manifest-invalid", rb.validate_manifest,
             mutated(CURSOR_MANIFEST, description="token is sk-" + "a" * 32), "cursor-cloud"),
      "a credential pasted into a manifest field is refused by the secret screen")

# --- schema/runtime branch parity -----------------------------------------------------------

REMOTE_SCHEMA = json.loads(
    (SOURCE / "schemas" / "control-plane" / "v1" / "remote-backend.schema.json")
    .read_text(encoding="utf-8")
)
def strict_schema_validator(schema: dict) -> Draft7Validator:
    """Use the runtime's exact Python integer policy while retaining Draft-7 semantics.

    JSON Schema's default Python type checker deliberately treats 1.0 as an integer,
    while the runtime contract requires an actual int and rejects bool.  The sibling
    phase controls use this same Draft-7 TypeChecker refinement for Python-object parity.
    """
    checker = Draft7Validator.TYPE_CHECKER.redefine_many({
        "integer": lambda _checker, value: type(value) is int,
        "number": lambda _checker, value: (
            type(value) is int or (type(value) is float and math.isfinite(value))
        ),
    })
    strict_class = validators.extend(Draft7Validator, type_checker=checker)
    return strict_class(schema)


SCHEMA_VALIDATOR = strict_schema_validator(REMOTE_SCHEMA)
SCHEMA_VALIDATOR.check_schema(REMOTE_SCHEMA)
PUBLICATION_SCHEMA = REMOTE_SCHEMA["properties"]["publication"]["properties"]


def schema_accepts_manifest(value: object) -> bool:
    return SCHEMA_VALIDATOR.is_valid(value)


def runtime_accepts_manifest(value: dict, name: str) -> bool:
    try:
        rb.validate_manifest(value, name)
        return True
    except RemoteError:
        return False


def schema_accepts_definition(definition: dict, value: object) -> bool:
    return (isinstance(value, str)
            and len(value) >= definition.get("minLength", 0)
            and re.search(definition["pattern"], value) is not None)


def schema_accepts_property(field: str, value: object) -> bool:
    definition = PUBLICATION_SCHEMA[field]
    if "allOf" in definition:
        return all(
            schema_accepts_definition(
                REMOTE_SCHEMA["definitions"][clause["$ref"].split("/")[-1]]
                if "$ref" in clause else clause,
                value,
            )
            for clause in definition["allOf"]
        )
    if "$ref" in definition:
        definition = REMOTE_SCHEMA["definitions"][definition["$ref"].split("/")[-1]]
    return schema_accepts_definition(definition, value)


def schema_accepts_result_pattern(value: object) -> bool:
    item = PUBLICATION_SCHEMA["allowed_result_branch_patterns"]["items"]
    definition = REMOTE_SCHEMA["definitions"][item["allOf"][0]["$ref"].split("/")[-1]]
    return (schema_accepts_definition(definition, value)
            and value not in item["allOf"][1]["not"]["enum"])


def runtime_accepts_branch(value: str) -> bool:
    try:
        rb.validate_branch_name(value, "branch")
        return True
    except RemoteError:
        return False


branch_parity_cases = [
    ("@", True),
    ("x" * 256, True),
    (".", False),
    ("foo.", False),
    ("foo@{bar}", False),
    ("foo/.bar", False),
    ("foo/bar.lock", False),
    ("foo/.lock", False),
    ("foo\x00bar", False),
    ("foo\x1fbar", False),
    ("foo\x7fbar", False),
    ("foo./bar", True),
    ("foo/@", True),
]
for candidate, expected in branch_parity_cases:
    runtime = runtime_accepts_branch(candidate)
    schema = schema_accepts_property("default_branch", candidate)
    check(runtime == expected and schema == expected and runtime == schema,
          f"schema/runtime default_branch parity for {candidate!r}")

task_pattern_parity_cases = [
    ("recursion/extern/<task-id>", True),
    ("@/<task-id>", True),
    (".", False),
    ("foo/.bar/<task-id>", False),
    ("foo@{bar}/<task-id>", False),
    ("foo/<task-id>?", False),
]
for candidate, expected in task_pattern_parity_cases:
    try:
        rb.validate_manifest(
            with_publication(CURSOR_MANIFEST, task_branch_pattern=candidate),
            "cursor-cloud",
        )
        runtime = True
    except RemoteError:
        runtime = False
    schema = schema_accepts_property("task_branch_pattern", candidate)
    check(runtime == expected and schema == expected and runtime == schema,
          f"schema/runtime task_branch_pattern parity for {candidate!r}")

pattern_parity_cases = [
    ("@", True),
    ("x" * 256, True),
    ("foo/*", True),
    ("foo/?bar", True),
    ("foo./*", True),
    ("?", True),
    ("*", False),
    ("**", False),
    ("/*", False),
    (".", False),
    ("foo.", False),
    ("foo/.bar", False),
    ("foo/bar.lock", False),
    ("foo@{bar}", False),
    ("foo\x00*", False),
    ("foo\x1f*", False),
    ("foo[ab]", False),
]
for candidate, expected in pattern_parity_cases:
    try:
        rb.validate_manifest(
            with_publication(CURSOR_MANIFEST,
                             allowed_result_branch_patterns=[candidate]),
            "cursor-cloud",
        )
        runtime = True
    except RemoteError:
        runtime = False
    schema = schema_accepts_result_pattern(candidate)
    check(runtime == expected and schema == expected and runtime == schema,
          f"schema/runtime allowed_result_branch_patterns parity for {candidate!r}")

# --- direct Draft7 endpoint/runtime differentials --------------------------------------------

check(schema_accepts_manifest(CURSOR_MANIFEST)
      and runtime_accepts_manifest(CURSOR_MANIFEST, "cursor-cloud"),
      "the cursor-cloud manifest is accepted by both Draft7 and authoritative runtime validation")
check(schema_accepts_manifest(GROK_MANIFEST)
      and runtime_accepts_manifest(GROK_MANIFEST, "grok-bot"),
      "the grok-routine endpoint_ref form is accepted by both Draft7 and runtime validation")

public_endpoint_cases = [
    ("https://api.cursor.com", True),
    ("https://api.cursor.com/base/path", True),
    ("https://api.cursor.com:443", True),
    ("https:///x", False),
    ("https://:443", False),
    ("https://user:pass@api.cursor.com", False),
    ("https://api.cursor.com?token=1", False),
    ("https://api.cursor.com#fragment", False),
    ("https://[::1", False),
    ("http://api.cursor.com", False),
]
for candidate, expected in public_endpoint_cases:
    candidate_manifest = mutated(CURSOR_MANIFEST, endpoint=candidate)
    schema = schema_accepts_manifest(candidate_manifest)
    runtime = runtime_accepts_manifest(candidate_manifest, "cursor-cloud")
    check(schema == expected and runtime == expected and schema == runtime,
          f"direct schema/runtime public endpoint parity for {candidate!r}")

# endpoint_ref is deliberately opaque to Draft7: it carries a secret reference, not the URL
# value. The resolved value is tested through backend_endpoint, where the runtime applies the
# same https/authority/userinfo/query/fragment/path policy with a webhook-appropriate query rule.
check(schema_accepts_manifest(mutated(GROK_MANIFEST,
                                      endpoint_ref="secret:GROK_ROUTINE_WEBHOOK_URL")),
      "Draft7 accepts the grok endpoint_ref reference form without seeing its secret value")
resolved_endpoint_cases = [
    ("https://hooks.example.com/routines/abc", True),
    ("https://hooks.example.com/routines/abc?v=1", True),
    ("https://hooks.example.com?route=1", True),
    ("https:///x", False),
    ("https://:443", False),
    ("https://[::1", False),
    ("https://user:pass@hooks.example.com/routines/abc", False),
    ("https://hooks.example.com/routines/abc#fragment", False),
    ("http://hooks.example.com/routines/abc", False),
]
for candidate, expected in resolved_endpoint_cases:
    os.environ["GROK_ROUTINE_WEBHOOK_URL"] = candidate
    try:
        rb.backend_endpoint(GROK_MANIFEST)
        runtime = True
    except RemoteError:
        runtime = False
    check(schema_accepts_manifest(GROK_MANIFEST) and runtime == expected,
          f"endpoint_ref schema/runtime differential for resolved value {candidate!r}")
os.environ.pop("GROK_ROUTINE_WEBHOOK_URL", None)

# Generated boundary corpus: Python runtime values that specifically exercise Draft-7's
# permissive numeric semantics and its pre-newline `$` behavior.  The strict TypeChecker above
# is still Draft7Validator 4.26.0, but uses the same exact-int policy as the runtime.
parity_corpus = [
    ("timeout_seconds", 1.0),
    ("max_attempts", 1.0),
    ("concurrency_lease", 1.0),
    ("name", "cursor-cloud\n"),
    ("capacity_pool", "cursor-cloud-pool\n"),
    ("host_id", "cursor-cloud\n"),
    ("endpoint", "https://api.cursor.com\n"),
    ("credential_ref", "secret:CURSOR_CLOUD_API_KEY\n"),
    ("publication", with_publication(CURSOR_MANIFEST, default_branch="main\n")["publication"]),
]
parity_results = []
for field, value in parity_corpus:
    candidate_manifest = (mutated(CURSOR_MANIFEST, **{field: value})
                          if field != "publication" else mutated(CURSOR_MANIFEST, publication=value))
    schema = schema_accepts_manifest(candidate_manifest)
    runtime = runtime_accepts_manifest(candidate_manifest, "cursor-cloud")
    parity_results.append((field, schema, runtime))
schema_only = sum(schema and not runtime for _, schema, runtime in parity_results)
runtime_only = sum(runtime and not schema for _, schema, runtime in parity_results)
check(schema_only == 0 and runtime_only == 0,
      f"generated schema/runtime parity corpus has schema-only={schema_only}, "
      f"runtime-only={runtime_only} across {len(parity_results)} cases")

# Draft7 validates each branch independently but cannot generically compare two sibling values.
# Keep the equality case accepted by the schema as an explicit semantic boundary, while the
# authoritative runtime check remains mandatory and refuses it.
equal_branches = with_publication(CURSOR_MANIFEST, integration_branch="main")
check(schema_accepts_manifest(equal_branches)
      and not runtime_accepts_manifest(equal_branches, "cursor-cloud"),
      "Draft7 documents but does not pretend to enforce integration_branch != default_branch; "
      "runtime validation remains mandatory")

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

class BrokenResponse:
    status = 200
    headers = {}

    def __init__(self, failure):
        self.failure = failure

    def read(self):
        raise self.failure

    def close(self):
        return None


class BrokenStream:
    headers = {}

    def __iter__(self):
        raise self.failure

    def __init__(self, failure):
        self.failure = failure

    def close(self):
        return None


original_urlopen = urllib.request.urlopen
try:
    urllib.request.urlopen = lambda *args, **kwargs: BrokenResponse(
        TimeoutError("Bearer ghp_" + "q" * 36))
    try:
        live.request("POST", "https://provider.example/run", {}, b"{}", 5)
    except RemoteError as exc:
        read_timeout = exc.code == "transport-timeout" and "ghp_" not in str(exc)
    else:
        read_timeout = False
    check(read_timeout,
          "a response read timeout is a typed timeout without response or credential text")

    urllib.request.urlopen = lambda *args, **kwargs: BrokenResponse(
        urllib.error.URLError("https://provider.example/?token=secret"))
    try:
        live.request("POST", "https://provider.example/run", {}, b"{}", 5)
    except RemoteError as exc:
        open_failure = exc.code == "transport-error" and "token=secret" not in str(exc)
    else:
        open_failure = False
    check(open_failure,
          "a urllib request failure is normalized without copying exception details")

    urllib.request.urlopen = lambda *args, **kwargs: BrokenStream(socket.timeout(
        "Bearer ghp_" + "r" * 36))
    try:
        list(live.stream_lines("GET", "https://provider.example/events", {}, None, 5))
    except RemoteError as exc:
        stream_timeout = exc.code == "transport-timeout" and "ghp_" not in str(exc)
    else:
        stream_timeout = False
    check(stream_timeout,
          "a stream iterator timeout is a typed timeout without response or credential text")
finally:
    urllib.request.urlopen = original_urlopen
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
provider_secret = "Bearer ghp_" + "z" * 36
try:
    rb.TransportResponse(200, {}, (b'{"token":"' + provider_secret.encode() + b'')).json()
except RemoteError as exc:
    provider_json_error = str(exc)
else:
    provider_json_error = ""
check("JSONDecodeError" not in provider_json_error and provider_secret not in provider_json_error,
      "malformed provider JSON exposes neither parser text nor credential-shaped material")

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

cancel_digest = "c" * 64
cancel = begin(recon_base, dispatch_id="dispatch-cancel", operation="cancel",
               digest=cancel_digest, request="k" * 64)
rb.write_session(recon_base, "grok-bot", "dispatch-cancel", {
    "dispatch_id": "dispatch-cancel", "assignment_digest": cancel_digest,
    "run_id": "provider-run-1", "state": "cancelled",
    "vendor_state": "CANCELED",
})
check(raises("unreconciled-attempt", rb.reconcile_attempt, recon_base, "grok-bot",
             cancel.attempt_id, observed="landed", observer="lucas",
             detail={"provider_status": "RUNNING", "attempt_id": cancel.attempt_id,
                     "dispatch_id": "dispatch-cancel", "run_id": "provider-run-1"}),
      "generic landed evidence cannot mark a cancel successful from a running provider")
check(rb.open_attempts(recon_base, "grok-bot")[0]["attempt_id"] == cancel.attempt_id,
      "invalid cancel evidence leaves the cancellation attempt open")
closed_cancel = rb.reconcile_attempt(
    recon_base, "grok-bot", cancel.attempt_id, observed="landed", observer="lucas",
    detail={"provider_status": "CANCELED", "attempt_id": cancel.attempt_id,
            "dispatch_id": "dispatch-cancel", "run_id": "provider-run-1"})
check(closed_cancel["state"] == "succeeded",
      "only bound provider-terminal CANCELED evidence can close a cancel successfully")

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
check(raises("redaction-violation", rb.write_session, session_base, "grok-bot",
             "dispatch-0003", {"credential_ref": "secret:GITHUB_TOKEN"}),
      "write_session cannot use credential_ref as a broad exemption for a controller secret")
check(raises("redaction-violation", rb.write_session, session_base, "grok-bot",
             "dispatch-0004", {"kind": "probe",
                                "endpoint_ref": "secret:BACKEND_WEBHOOK_URL"}),
      "an arbitrary session kind cannot borrow the Grok endpoint_ref exemption")
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

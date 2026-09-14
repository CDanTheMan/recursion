# P2 read-only construction-service access

This slice implements the read-only part of continuous-operation P2. It is infrastructure for
external agents constructing Recursion v3, not a Recursion kernel, live Hermes integration,
scheduler, provider launcher, publication path or 24/7 service claim.

## Delivered boundary

`tools/construction_swarm/p2_access.py` is an explicitly started foreground service. It exposes
protocol version 1 over a mode-0600 Unix-domain socket. A first authentication frame maps a
presented token digest to server-side identity, project set, read capability and optional expiry;
that identity remains bound to the connection. Later request bodies cannot select an actor.

The only operations are `status`, `tasks`, `task`, `events` and `artifact`. Every service response,
including refusals, carries source commit, service instance, service fence or an explicit
unavailable marker, observation time, canonical observation/revision, freshness, last event cursor
and unavailable fields. Pages, requests, responses and artifact reads are bounded. Event history
gaps return `replay_gap` with `snapshot_required=true`. Artifact handles are project-scoped and
absolute paths, `..`, symlinks, non-files and files beyond the configured limit are refused.
Artifact roots are pinned as directory descriptors; every path component is opened relative to a
pinned descriptor with no-follow flags. Size, manifest SHA-256, returned bytes and pagination all
come from one size-capped capture of the same nonblocking file descriptor, so pathname replacement,
in-place writes and special files cannot redirect, version-mix or permanently block a read.

Status has a separate two-slot bounded path from the bounded general read slots. Accepted
connections and handshake/read lifetimes are also bounded. A disconnected client can return only
the same-operation cached snapshot when explicitly enabled; the cache key also binds the credential
digest and absolute service endpoint. Authentication refusal clears that complete credential and
endpoint scope; project refusal clears every cached operation for the affected project. The result
is relabelled `stale_disconnected` and adds `service.connection` to unavailable fields. Reconnection
always asks the service again and replaces the cache.

There is deliberately no real canonical adapter in this packet. Starting without the test fixture
adapter returns `None`, never zero/healthy, for unknown canonical fields and identifies both
`canonical.adapter` and `canonical.ledger` as unavailable. `FixtureCanonicalAdapter` and
`--fixture-canonical` are test-only seams; they must not be described as Hermes integration.

`p2_cli.py` is the native connecting CLI. `p2_mcp.py` is a newline-delimited JSON-RPC stdio MCP
bridge exposing the same five read tools. Neither starts or owns the service. Closing either client
does not signal, cancel or stop the service.

## Protocol frames

One connection authenticates, receives an authentication response, sends one read, receives one
read response and closes. Frames are single bounded UTF-8 JSON lines.

```json
{"op":"authenticate","protocol_version":1,"request_id":"auth-1","token":"presented-secret"}
{"op":"status","params":{"project":"recursion-v3"},"protocol_version":1,"request_id":"read-1"}
```

Grant files contain token SHA-256 digests, not plaintext tokens:

```json
[
  {
    "token_sha256": "64-lowercase-hex-characters",
    "identity": "codex-reader",
    "projects": ["recursion-v3"],
    "capabilities": ["read"],
    "expires_at": "2026-09-15T00:00:00Z"
  }
]
```

Plaintext tokens belong in separately permissioned, untracked files. Do not place them in argv,
tracked configuration, logs or this repository.

## Native commands

The normal service currently has no canonical adapter, so this exact foreground command is useful
only for verifying honest-unavailable behavior. It does not daemonize or activate a fleet.

```text
python3 -X utf8 -B -m tools.construction_swarm.p2_access serve --socket /run/user/1000/recursion-construction-read.sock --source-commit FULL_40_CHARACTER_COMMIT --grants /var/lib/recursion-foundry/access/read-grants.json
```

From a second WSL shell:

```text
python3 -X utf8 -B -m tools.construction_swarm.p2_cli --socket /run/user/1000/recursion-construction-read.sock --token-file /var/lib/recursion-foundry/access/clients/native.token status --project recursion-v3
```

`--allow-stale` requires `--cache PATH`; without a same-operation, same-credential, same-endpoint
cached response, service loss is `service_unavailable`. Artifact content is base64 and must be paged
using `next_offset`; every artifact manifest record must bind the handle to its expected SHA-256.

## Separately enabled client smoke commands — unrun

These are exact process-level smoke commands for the present worktree and the proposed socket/token
locations. They were not run because no real grants, canonical adapter, service installation or
Cursor/Codex MCP configuration was provisioned by this packet.

Windows-to-WSL native CLI, **UNRUN**:

```text
wsl.exe -d Ubuntu-24.04 --cd /mnt/c/r3p1 python3 -X utf8 -B -m tools.construction_swarm.p2_cli --socket /run/user/1000/recursion-construction-read.sock --token-file /var/lib/recursion-foundry/access/clients/windows-cli.token status --project recursion-v3
```

Codex stdio bridge process, **UNRUN**:

```text
wsl.exe -d Ubuntu-24.04 --cd /mnt/c/r3p1 python3 -X utf8 -B -m tools.construction_swarm.p2_mcp --socket /run/user/1000/recursion-construction-read.sock --token-file /var/lib/recursion-foundry/access/clients/codex.token --cache /var/lib/recursion-foundry/access/clients/codex-cache.json
```

Cursor stdio bridge process, **UNRUN**:

```text
wsl.exe -d Ubuntu-24.04 --cd /mnt/c/r3p1 python3 -X utf8 -B -m tools.construction_swarm.p2_mcp --socket /run/user/1000/recursion-construction-read.sock --token-file /var/lib/recursion-foundry/access/clients/cursor.token --cache /var/lib/recursion-foundry/access/clients/cursor-cache.json
```

An operator must separately provision those files and configure each client to invoke its bridge.
This packet does not edit installed Codex/Cursor configuration. A process-level stdio test is not
evidence that either actual application interoperates.

## Acceptance

Run from the reviewed repository root:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_access
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p1_core
```

On the qualified Windows host, the first command uses `wsl.exe` to run the nineteen real Unix-socket
cases under WSL2. Each service, CLI and MCP child has a bounded timeout and is cleaned by its owning
test. On a native Linux host the same command runs those cases directly.

## Remaining P2 limits

- No real canonical Hermes adapter, canonical ledger reader or live artifact manifest exists.
- Native Windows CPython on the tested host has no `AF_UNIX`; the intended Windows path is a
  `wsl.exe` stdio bridge. No actual Codex or Cursor application connection was configured or run.
- Remote encrypted transport, grant provisioning/revocation distribution and credential rotation
  are outside this slice.
- Boot, sign-out, lock, editor closure, WSL shutdown, sleep/wake, Linux service restart, Windows
  watchdog behavior, duplicate host launch/fencing and recovery timing remain unimplemented/unrun.
- This does not activate the fleet, establish continuous operation, qualify S03/S04 as a whole,
  launch a provider, mutate canonical state, publish, merge or deploy.

## Draft next bounded packet: P2 host lifecycle

Parent: `goal-recursion-v2-execution-fabric`. Product target: Recursion v3. Input binding: the
reviewed commit containing this access slice, supplied explicitly to the executor as `TASK_BASE`.
Apply `docs/v3/construction/next-work-20260914/COMMON.md`; reread CW-03/04 and S03/S04. This is a
build-and-local-fault packet, not permission to install startup policy or claim 24/7 operation.

Objective: implement inert, operator-invoked lifecycle components that own the existing foreground
`p2_access serve` process independently of CLI/MCP clients. Define persisted service incarnation
and fencing, deterministic duplicate-watchdog refusal, stale-socket/PID reconciliation, bounded
restart/backoff and explicit outage observations. Preserve the current access protocol and its
honest unavailable behavior. A losing lifecycle controller must not start or signal the service;
neither controller may start a scheduler/provider or acquire P1 mutation authority.

Proposed allowed new paths only:

- `tools/construction_swarm/p2_host_lifecycle.py`
- `tools/construction_swarm/p2_windows_watchdog.ps1`
- `tools/construction_swarm/test_p2_host_lifecycle.py`
- `docs/v3/construction/p2-host-lifecycle-20260914/README.md`
- `docs/v3/construction/p2-host-lifecycle-20260914/PROGRESS.md`

Non-goals: no Task Scheduler/systemd installation or edits, no registry/config/auth/cron/autonomy
changes, no reboot/sign-out/sleep/WSL shutdown, no scheduler/provider/worker activation, no
publication, no second writer and no claim that a read-service fence is a Hermes/P1 leader fence.
Lifecycle tests use only an inert fixture child and temporary state. Each child deadline is 15
seconds; focused suite ceiling is 120 seconds; temporary data ceiling is 32 MiB.

Required local cases: two concurrent watchdog processes elect exactly one persisted incarnation;
the loser starts/signals nothing; service remains after CLI/MCP exit; unexpected fixture-child exit
is observed and restarted within a bounded backoff; a stale PID/socket is reconciled without
signalling an unrelated PID; old-incarnation health cannot overwrite current health; repeated
failures become explicit unavailable/outage state and stop at the restart cap; an operator Stop
quiesces only the owned fixture tree; Windows command construction is injection-safe and never
contains plaintext credentials; PAUSE/disabled input refuses start without changing it.

NEW acceptance command to implement:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_host_lifecycle
```

Also rerun both access and P1 commands above, source/scope checks and independent Astra review of
the exact final commit. Record Windows and Linux/WSL coverage separately. Produce, but do not apply,
an operator qualification runbook for boot, sign-out, lock, closing every editor, WSL shutdown,
sleep/wake and forced concurrent launch. Actual S03 host qualification requires a fresh finite plan,
human provisioning and receipts from the named Windows account; until then every such row remains
`specified_not_run`.

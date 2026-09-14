# P2 operator-invoked host lifecycle

Parent goal: `goal-recursion-v2-execution-fabric`. Product target: Recursion v3. Task base:
`e627cd93bac473094bc99e8fa29c8d62bae526a2`.

This packet adds an operator-invoked controller for the existing foreground `p2_access serve`
process. It supports external Devin/SWE-2 contributors who research, develop and test on Recursion
v3. It does not put those agents inside the Recursion product and does not activate a fleet.

## Delivered boundary

`p2_host_lifecycle.py` runs on native Linux or WSL. It takes a strict, size-bounded JSON
configuration, refuses a disabled input or an existing regular `PAUSE` file, takes a nonblocking
exclusive watchdog lock and only then reconciles prior state. A competing controller exits
`watchdog_busy` before it reads, starts or signals any service process.

Each service launch gets a monotonically increasing persisted incarnation. The same integer is
passed to `p2_access` as its read-service fence and is recorded with the service PID, Linux boot ID,
`/proc` start ticks, process group and command-line digest. The controller then binds each verified
identity to a Linux pidfd before any signal; it never signals a numeric PID or process group. A
bounded set of discovered descendants is persisted and kernel-pinned. Cleanup freezes the pinned
tree before a final descendant scan, then signals only those handles. A read-service fence is only an access
service incarnation: state always records `canonical_writer_authority=false`; it is not a Hermes or
P1 leader fence and grants no mutation authority.

The service starts in a new process session, so native CLI and MCP client exit do not signal it.
Unexpected child exit advances the incarnation and uses
bounded exponential backoff. After the configured restart cap, the controller exits and persists
`health=outage`, `unavailable=true` and `outage_reason=restart_exhausted`. `starting`, `backoff`,
`stopping`, `stopped` and every outage are also unavailable; only `running` is available. Every
transition carries an observation timestamp. This is transition freshness, not a continuous
application-level probe.

An operator stop first binds and proves the recorded controller pidfd before signaling it. It
returns success only after the same controller records stopped, unavailable and a quiescent cleanup
receipt for the service incarnation. The controller never searches by process name. An inactive
Unix socket is removed only after two inode checks, including before every restart; an
active socket, non-socket path or uncertain probe is refused. An old service incarnation cannot
publish health over the current one.

`p2_windows_watchdog.ps1` is a thin Windows launcher. It constructs a `wsl.exe` argument array and
never evaluates a command string. It accepts only distro, Linux repository and config paths; there
is no credential parameter. The grant file contains digests and is named by path in the lifecycle
configuration. Plaintext client tokens remain in separately permissioned, untracked token files
used by clients, never this wrapper or service argv.

The existing five-operation read protocol, canonical-unavailable behavior, bounded artifact
access, client cache binding and CLI/MCP ownership remain unchanged.

## Configuration and manual operation

Configuration is operator-provisioned outside this repository. The controller accepts exactly
these fields:

```json
{
  "version": 1,
  "enabled": true,
  "source_commit": "FULL_40_CHARACTER_REVIEWED_COMMIT",
  "repository_root": "/opt/recursion-foundry/repos/recursion-qualified",
  "python_executable": "/usr/bin/python3",
  "socket_path": "/run/user/1000/recursion-construction-read.sock",
  "grants_file": "/var/lib/recursion-foundry/access/read-grants.json",
  "state_root": "/var/lib/recursion-foundry/run/p2-read-lifecycle",
  "pause_path": "/var/lib/recursion-foundry/run/PAUSE",
  "restart_cap": 3,
  "backoff_initial_seconds": 1.0,
  "backoff_max_seconds": 8.0,
  "startup_timeout_seconds": 10.0,
  "shutdown_timeout_seconds": 10.0
}
```

`source_commit` must be lowercase 40-character hex and must equal `repository_root` HEAD. Linux
pidfd support is required. A discovered service tree is capped at 256 members. The
repository must contain `p2_access.py`; all paths must be absolute. Timeouts are individually
bounded to 15 seconds and the restart cap to ten. The config and grants paths must be regular,
non-symlink files. This packet does not create those files or choose their production locations.

Manual Linux/WSL start:

```text
python3 -X utf8 -B -m tools.construction_swarm.p2_host_lifecycle run --config /ABSOLUTE/UNTRACKED/lifecycle.json
```

Manual Windows-to-WSL start:

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/construction_swarm/p2_windows_watchdog.ps1 -Distro Ubuntu-24.04 -LinuxRepository /opt/recursion-foundry/repos/recursion-qualified -Config /ABSOLUTE/UNTRACKED/lifecycle.json
```

Manual bounded stop from Linux/WSL:

```text
python3 -X utf8 -B -m tools.construction_swarm.p2_host_lifecycle stop --state-root /var/lib/recursion-foundry/run/p2-read-lifecycle --timeout 15
```

State is in `state.json` beneath the configured state root. Operators must treat missing state,
non-`running` health, a stale `observation_time`, an identity mismatch or a failed read as
unavailable—not infer health from a PID alone. `PAUSE`/disabled inputs prevent a new controller
start and are not changed by the controller.

## Acceptance

Run from the reviewed native Linux repository root:

```text
python3 -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_host_lifecycle
python3 -X utf8 -B -m unittest -v tools.construction_swarm.test_p1_core
python3 -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_access
python3 -X utf8 -B -m tools.construction_swarm.p2_host_lifecycle source-scope --repository "$PWD" --candidate FULL_40_CHARACTER_FINAL_COMMIT
git diff --check e627cd93bac473094bc99e8fa29c8d62bae526a2 FULL_40_CHARACTER_FINAL_COMMIT
```

The focused tests use only temporary fixture children. Each subprocess deadline is at most 15
seconds, the suite has an internal 120-second alarm and is also externally bounded to 120 seconds
during qualification, and fixture JSON
is capped at 32 MiB. The frozen predecessor integration gate remains frozen and intentionally
rejects successor files; it is not an acceptance gate for this additive packet.

## Draft host qualification runbook — all trials specified, not run

This runbook is a proposal for a separately approved, human-provisioned finite trial on the named
Windows account. It does not authorize installing Task Scheduler/systemd services, editing startup
policy, changing auth/config/model/cron/autonomy settings, rebooting, signing out, sleeping,
shutting down WSL or activating providers. Every row below is `specified_not_run`.

Before a future trial, the operator must record the reviewed commit, Windows account, WSL distro
and kernel, Python and PowerShell versions, absolute native-Linux checkout/config/state/socket
paths, the approved time window and rollback owner. Use a disposable read-only grant and an inert
or explicitly approved unavailable canonical adapter. Capture timestamps, controller/service
identity tuples, incarnation/fence, state transitions, client response freshness, restart count,
exit codes and process-tree observations. Do not capture token contents or environment secrets.

| Trial | Future operator procedure | Required receipt | Current status |
| --- | --- | --- | --- |
| Baseline/manual boot start | After normal account login and WSL availability, invoke the wrapper once; do not install it. Read status through native CLI and MCP separately, then close both. | One controller, one service, unchanged incarnation after client exit, read response with truthful freshness/unavailable fields. | `specified_not_run` |
| Forced concurrent launch | Invoke two wrappers concurrently against one state root. | Exactly one running controller/service; loser `watchdog_busy`; launch count and fence advance once; no signal from loser. | `specified_not_run` |
| Close every editor | With service running, close Codex, Cursor, terminals and other clients, then inspect from a newly opened shell. | Same controller/service identity and incarnation, or explicit unavailable/outage evidence. | `specified_not_run` |
| Windows lock/unlock | Lock and unlock the session within the approved window. | Same identity/incarnation or bounded recovery with a new fence; no false healthy state. | `specified_not_run` |
| Sign out/in | Operator performs the approved sign-out and signs back in, then invokes the wrapper manually if no process remains. | Exact observed termination/persistence behavior; manual recovery time and resulting incarnation. No automatic-start claim. | `specified_not_run` |
| WSL shutdown/reopen | Operator performs the approved distro/WSL shutdown, reopens it and manually invokes the wrapper. | Old boot-ID identity rejected, stale PID/socket reconciliation, new incarnation, recovery timing. | `specified_not_run` |
| Sleep/wake | Operator performs approved host sleep/wake and probes immediately after wake. | Persistence or bounded manual recovery, clock/freshness observations and no unrelated signals. | `specified_not_run` |
| Reboot | Operator performs the approved reboot, signs in and manually invokes the wrapper. | Old boot-ID identity rejected, stale state reconciled, new incarnation and manual recovery timing. No boot-service claim. | `specified_not_run` |
| Crash/restart cap | Kill only the recorded fixture/approved service process repeatedly, never by name. | Bounded backoff sequence, monotonically increasing fence, explicit outage at cap and no further child. | `specified_not_run` |
| Stop/tree isolation | Start an unrelated canary process, use the lifecycle stop command and inspect both trees. | Owned tree quiescent, unrelated canary unchanged, stopped state unavailable. | `specified_not_run` |

Abort the future trial on source mismatch, unsafe config/state/socket path, unexpected provider or
writer activity, any signal to an unrelated process, missing receipt, secret exposure or an
unbounded child. Preserve the failed state and logs, place `PAUSE` through the separately approved
operator procedure, stop only through identity-bound lifecycle stop when safe, and escalate. Do not
repair by weakening a gate or deleting evidence.

## Remaining limits

- No startup service, scheduled task, automatic login start, WSL keepalive or 24/7 operation is
  installed or claimed.
- No real canonical Hermes adapter, canonical ledger reader or live artifact manifest exists.
- The controller records transition health; it does not perform semantic read-protocol liveness
  probes while the child remains running.
- Tree discovery is bounded to 256 processes and relies on Linux `/proc` plus pidfds; unsupported
  kernels refuse rather than falling back to numeric PID signaling.
- Remote transport, grant provisioning/revocation and credential rotation remain outside scope.
- All disruptive Windows/WSL lifecycle qualification rows above remain `specified_not_run`.
- This packet does not qualify S03/S04 as a whole, launch providers/workers, mutate canonical
  state, publish, merge or deploy.

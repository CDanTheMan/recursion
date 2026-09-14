# P2 read-only access progress

Date: 2026-09-14

## Binding

- Parent: `goal-recursion-v2-execution-fabric`
- Product target: Recursion v3 external construction service
- Branch: `codex/p1-readonly-service-20260914`
- Worktree: `C:\r3p1`
- `TASK_BASE`: `0c908f6833e715af0eaa01b6f6788120eb577efd`
- Allowed paths: the six paths in packet 01; no other path changed
- Provider inference: none
- Service/fleet activation: none
- Publication/deployment/config/auth/cron/autonomy changes: none

## Source preservation before editing

Command:

```text
python -X utf8 -B docs/v3/construction/next-work-20260914/check_handoff.py
```

Observed before implementation: exit 0 in 11.4 seconds with
`status=HANDOFF_SOURCE_PASS`, candidate
`0c908f6833e715af0eaa01b6f6788120eb577efd`, 3 packets, 49 unchanged top-level v3
specifications, 0 provider calls, no scientific execution and no service activation.

## Implementation

- Commit `d261d61` adds the foreground version-1 authenticated Unix-socket service, native CLI,
  read-only stdio MCP bridge and acceptance tests.
- Authentication maps a token SHA-256 to server-side identity/project/read grants and binds it to
  the connection. Actor/identity fields in operation bodies are refused.
- `status`, `tasks`, `task`, `events` and `artifact` are the complete operation/tool set. Mutation
  verbs are refused. No implementation module imports or invokes a provider, scheduler or P1
  mutation surface.
- Default canonical state is explicitly unavailable. The JSON canonical adapter is named and
  exposed as fixture-only for tests; it is not a live Hermes adapter.
- Status and general reads use separate bounded slots. Pages, requests, responses, event replay and
  artifact chunks/sizes are bounded. Project/handle/path/symlink checks precede artifact reads.
- Client caches are optional and operation/parameter-specific. Only explicit stale reads return a
  cached response after connection loss, relabelled stale and unavailable.

## Gate evidence before independent review

Exact focused command from Windows PowerShell:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_access
```

Observed: exit 0 in 5.6 seconds. The outer Windows test invoked the same module under WSL2; all 11
native cases passed in 2.499 seconds. The cases used real foreground service processes, Unix-domain
sockets, separate CLI/MCP processes and temporary artifact fixtures. They covered both clients and
bounded snapshot identity, isolation/spoofing, mutation denial, missing adapter/ledger, disconnect
staleness, replay gap, malformed/oversize input, artifact escapes, bridge independence/reconnect and
reserved status response under two saturated general read slots.

Exact P1 regression:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p1_core
```

Observed: exit 0; all 18 cases passed in 1.776 seconds.

## Actual platform coverage

- Windows host orchestration: Microsoft Windows 11 Pro, version 10.0.26200 build 26200, 64-bit;
  CPython 3.12.10. Native Windows CPython reported no `socket.AF_UNIX`, so no native-Windows socket
  behavior is claimed.
- WSL transport/runtime: WSL 2.7.3.0, Ubuntu 24.04.4 LTS, kernel
  6.6.114.1-microsoft-standard-WSL2, Python 3.12.3. All eleven service cases ran here.
- Native non-WSL Linux, macOS, actual Codex MCP and actual Cursor MCP were not run.
- Boot, sign-out, lock, editor closure, `wsl --shutdown`, sleep/wake and reboot were not run.

## Negative evidence and limitations

- With no adapter, canonical revision/cursor/active leases/counts and all CW-17 status dimensions
  are `None` plus named unavailable fields; the service does not report zero work or health.
- The fixture adapter proves the boundary behavior only. It is neither canonical acceptance nor
  live Hermes/foundry integration.
- S03 remains entirely unrun. S04 is covered only at process/socket protocol level; simultaneous
  actual Cursor/Codex application attachment is unrun.
- No remote encrypted transport, credential provisioning/rotation, host lifecycle/watchdog,
  canonical adapter, scheduler, provider, worker, publication or persistent startup policy exists.
- P2 and 24/7 continuous operation are not complete or activated.

## Independent review

Pending exact-candidate Astra review. Final candidate SHA, review evidence, findings/remediation and
post-review reruns will be appended before handoff.

# P2 host lifecycle progress

Date: 2026-09-14

Parent goal: `goal-recursion-v2-execution-fabric`

Product target: Recursion v3

TASK_BASE: `e627cd93bac473094bc99e8fa29c8d62bae526a2`

Source branch: `codex/v3-integration-20260914`

Work branch: `codex/p2-host-lifecycle-20260914`

Native WSL worktree:
`/opt/recursion-foundry/worktrees/recursion-host-lifecycle-20260914`

Windows reference worktree `C:\r3i` was read only. The older checkout
`C:\Users\Lucas\Documents\GitHub\recursion` was not used for task writes.

## Source and preservation

- Remote `refs/heads/codex/v3-integration-20260914` resolved to TASK_BASE before construction.
- The native Linux worktree was created at TASK_BASE. Its `.git` pointer is Linux-native under
  `/opt/recursion-foundry`; no Windows worktree Git pointer is used from Linux.
- Before editing, the handoff-preservation check passed in the native worktree with candidate
  `e627cd93bac473094bc99e8fa29c8d62bae526a2`: `HANDOFF_SOURCE_PASS`, three packets, zero provider
  calls, no scientific result, no construction service and 49 unchanged specification files.
- The frozen integration gate was not edited or weakened. This successor packet has an additive
  exact-base/exact-path source-scope checker.

## Implementation

The first coherent code/test slice is `d1f6083` (`Add bounded P2 host lifecycle controller`). It
adds nonblocking watchdog election, persisted incarnation/fence and process identity, safe stale
PID/socket reconciliation, bounded restart/backoff/cap, honest outage state, identity-bound tree
stop, strict PAUSE/disabled refusal, a literal-argv Windows wrapper and bounded fixture coverage.

Documentation and exact final review evidence are recorded in later commits on the same branch.

## Coverage so far

Native Linux under WSL Ubuntu-24.04:

- Focused lifecycle suite after correction: 11 tests, pass, 2.691 seconds.
- A subsequent quiet pre-commit run: 11 tests, pass, 2.742 seconds.
- Real fixture processes covered competing watchdogs, client disconnect, crash/restart, restart
  exhaustion, stale and active socket handling, stale unrelated PID preservation, old-incarnation
  health rejection, owned-tree cleanup and PAUSE/disabled refusal.

Windows host surface from the WSL suite:

- Windows PowerShell 5 wrapper executed in `-DryRun` mode through `powershell.exe`.
- Adversarial config text containing command syntax remained one literal argv element and created
  no marker; no credential parameter appeared.
- The wrapper did not start WSL/service processes in that test. Native Windows does not run the
  Unix-socket controller.

Not run:

- Provider, worker, scheduler, live Hermes/canonical adapter or external-agent calls.
- Installed/scheduled startup, deployment, publication or fleet activation.
- Boot, reboot, sign-out, lock/unlock, closing editors, WSL shutdown and sleep/wake qualification.

## Retained failed evidence

- A direct GitHub fetch in a new WSL-native clone exceeded the 30-second command window. The three
  exact task-owned Git process chains were inspected and terminated; no other process was
  signaled. A bundle made from the separately verified source branch was then used to create the
  native clone, and its origin was reset to the GitHub URL.
- The first preservation invocation used WSL while its current directory was `C:\r3i`; Git rejected
  the Windows worktree pointer as not a Linux repository. The check was rerun from the native
  `/opt/recursion-foundry` worktree and passed before editing.
- One intermediate inspection command had invalid nested shell quoting and did not execute the
  intended AST read. A direct Python compile check then passed.
- The first focused suite run completed 11 tests in 2.603 seconds with one error: the client-exit
  test passed a `Path` instead of `str` to `socket.connect`. The implementation cases had run; the
  test was corrected, pipe cleanup was tightened, and the complete suite passed twice afterward.

## Pending final evidence

- Commit this runbook/progress slice.
- Run focused P2 host lifecycle, frozen P1 and P2 access regressions, source/scope, handoff
  preservation and `git diff --check` on a committed candidate.
- Obtain independent Astra review of the exact candidate, resolve actionable findings, rerun
  affected gates and record the exact reviewed final commit.

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

Documentation began in `2b28a59` (`Document P2 lifecycle qualification boundary`). Independent
Astra review of exact candidate `2b28a596978845dce2b732d74bbd93cfea578a4b` required changes:
restart-time stale sockets exhausted the cap, a dead leader could orphan an unrecorded descendant,
numeric PID/group signaling had a reuse race, Stop did not require a cleanup receipt, health
publication could contradict availability, and the source/scope gate was not bound to current HEAD
and cleanliness.

The remediation replaces numeric signals with verified kernel pidfds, persists bounded discovered
tree members, freezes and rescans before cleanup, reconciles sockets before restart, binds Stop
success to a quiescent receipt, updates availability with health, and binds source/scope to exact
clean HEAD plus five additions. Focused regressions reproduce the review failures. Exact final
review evidence is recorded in the final documentation commit on this branch.

Astra review of exact remediation candidate `22f90f705c0274160b6b59fb5a428de5399be9a9`
closed the six prior findings but found three related ownership-domain failures: a child forked
after discovery could survive a quiescent receipt, numeric ancestry discovery could adopt an
unrelated reused PID, and the discovery-limit error could leak a pidfd while leaving processes
frozen. That candidate is also retained as failed review evidence. The second remediation removes
numeric descendant discovery entirely. The service enters a dedicated cgroup-v2 domain before
`exec`; all forks inherit it, `pids.max=256` bounds it, and atomic `cgroup.kill` defines quiescence.
Pidfds remain only for the verified controller Stop signal.

Astra review of exact cgroup candidate `67b65434419331fcc901628b25b1f69724e675fc`
confirmed pre-exec membership, inherited fork containment, atomic domain cleanup, unrelated-process
isolation and replacement-controller recovery. It still failed the candidate because the fixture
delegation did not enable `pids`, making the advertised process bound absent, and because cleanup
was armed from the derived cgroup pathname before prior source/state ownership validation. The
third remediation requires and reads back `pids.max=256`, adds an undelegated-controller refusal
case, and arms domain cleanup only after matching prior source/domain state (or a proven-empty new
domain). Its negative canary test verifies rejected prior state causes no signal. Cleanup also does
not let membership-count or process-limit observations block an already-authorized `cgroup.kill`.

Astra review of exact candidate `02e8aa50c50817f321fd1a842505769e929c2a07` closed those
findings but found two remaining admission effects: `pids.max` was still rewritten before a
mismatched prior state was refused, and an injected authorized takeover-cleanup failure left the
dead controller's stale `running` state intact. The fourth remediation performs a non-mutating
existing-domain inspection, authorizes exact prior source/domain state before any control write,
and persists a current-controller unavailable/non-quiescent outage when authorized cleanup fails.
Both actual-canary boundaries now have focused regressions.

Astra review of exact candidate `ceec469c05eea83feb3c80ab342f4ff1e58135dc` closed both
counterexamples but injected one adjacent matched-takeover failure: an unreadable `cgroup.events`
observation occurred before the durable uncertainty path and left the prior controller's stale
available state. The fifth remediation authorizes the exact recorded source/domain before fallible
inspection, then publishes current-controller unavailable/non-quiescent state for inspection or
population-read failure without touching mismatched domains.

## Coverage so far

Native Linux under WSL Ubuntu-24.04:

- Focused lifecycle suite after the first correction: 11 tests, pass, 2.691 seconds.
- A subsequent quiet pre-commit run: 11 tests, pass, 2.742 seconds.
- First independently reviewed committed candidate: 11 tests passed in 2.622 seconds; Astra's own
  rerun passed 11 in 2.746 seconds, but independent process probes found the six issues above.
- First remediation suite run: 15 tests in 3.403 seconds with one test error because the assertion
  looked for the prior cleanup receipt under the wrong state key. The persisted `last_cleanup`
  receipt and assertion were aligned.
- Remediation suite: 15 tests, pass, 3.351 seconds; affected-gate rerun: 15 pass in 3.423 seconds.
- Affected frozen regressions after remediation: P1 18 pass in 2.113 seconds; P2 access 19 pass in
  5.577 seconds.
- Clean first-remediation candidate: lifecycle 15 pass in 3.495 seconds, P1 18 pass in 2.115
  seconds, P2 access 19 pass in 5.581 seconds, with preservation/scope/diff passing. Astra reran 15
  in 3.625 seconds, 18 in 2.168 seconds and 19 in 5.598 seconds before its adversarial tree probes
  failed the candidate.
- First cgroup-domain suite: 15 tests, pass, 3.561 seconds. An added unobserved-fork regression then
  expanded the suite to 16 tests, pass, 4.035 seconds.
- Clean cgroup candidate: lifecycle 16 pass in 4.332 seconds, P1 18 pass in 2.072 seconds and P2
  access 19 pass in 5.581 seconds, with preservation/scope/diff passing. Astra reran 16 in 4.392
  seconds, 18 in 3.346 seconds and 19 in 5.586 seconds before its admission probes failed it.
- First delegation/authorization remediation suite: 18 tests, pass, 4.076 seconds.
- Exact clean admission candidate then passed 18 lifecycle tests in 4.305 seconds, 18 P1 tests in
  2.113 seconds and 19 P2 access tests in 5.600 seconds; preservation/scope/diff also passed.
- A final local audit made cleanup-control errors persist explicit non-quiescent uncertainty rather
  than leave the last transition apparently healthy. Its focused regression expanded the suite to
  19 tests, pass, 4.028 seconds.
- Clean preauthorization candidate: lifecycle 19 pass in 4.161 seconds, P1 18 pass in 2.107 seconds,
  P2 access 19 pass in 5.603 seconds, with preservation/scope/diff passing. Astra reran 19 in 4.222
  seconds, 18 in 2.121 seconds and 19 in 5.596 seconds before its admission probes failed it.
- First non-mutating-admission suite: 20 tests, pass, 4.043 seconds.
- Clean non-mutating candidate: lifecycle 20 pass in 4.668 seconds, P1 18 pass in 3.386 seconds and
  P2 access 19 pass in 5.615 seconds, with preservation/scope/diff passing. Astra reran 20 in 4.250
  seconds, 18 in 2.118 seconds and 19 in 5.641 seconds before its control-read probe failed it.
- First matched-inspection uncertainty suite: 21 tests, pass, 4.230 seconds.
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
- Astra review of `2b28a596978845dce2b732d74bbd93cfea578a4b` returned six actionable findings despite
  all 48 supplied tests passing. That failed review receipt is retained above; the exact candidate
  was not treated as final.
- Astra review of `22f90f705c0274160b6b59fb5a428de5399be9a9` returned three actionable tree-domain
  findings despite all 52 supplied tests passing. Its two surviving-child probes and modeled stale
  discovery probe were cleaned by the reviewer; the candidate was not treated as final.
- Astra review of `67b65434419331fcc901628b25b1f69724e675fc` returned two actionable admission
  findings despite all 53 supplied tests passing. The reviewer's disposable canaries and cgroups
  were cleaned; the candidate was not treated as final.
- Astra review of `02e8aa50c50817f321fd1a842505769e929c2a07` returned two actionable admission-side
  findings despite all 56 supplied tests passing. Its canaries, fixture processes and cgroups were
  cleaned; the candidate was not treated as final.
- Astra review of `ceec469c05eea83feb3c80ab342f4ff1e58135dc` returned one actionable matched-domain
  inspection finding despite all 57 supplied tests passing. Its canaries, fixtures and cgroups
  were cleaned; the candidate was not treated as final.
- The first expanded remediation suite completed 15 tests in 3.403 seconds with one error: the
  restart receipt assertion expected `cleanup` in the new running state. The implementation now
  intentionally carries the most recent verified receipt as `last_cleanup`; the corrected suite
  passed.
- An initial Windows version probe was malformed by outer-shell variable expansion and returned a
  parser error. Direct probes then recorded PowerShell 7.6.5 on the host and Windows PowerShell
  5.1.26100.9444 for the wrapper path.
- Windows denied the first attempt to remove the task-owned 13,407,032-byte temporary source
  bundle. Its exact path was revalidated and the file was removed from WSL; absence was verified.

## Pending final evidence

- Commit the remediation and evidence slices.
- Run focused P2 host lifecycle, frozen P1 and P2 access regressions, source/scope, handoff
  preservation and `git diff --check` on a committed candidate.
- Obtain independent Astra review of the exact candidate, resolve actionable findings, rerun
  affected gates and record the exact reviewed final commit.

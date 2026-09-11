# Construction swarm validation — 2026-09-10

Parent: `goal-recursion-v2-execution-fabric`. Baseline: merged PR121, `d9f27d2`.
Implementation reviewed after remediation: `2344cdc2828de983c7d16ab551f0532909649ecf`.
This records construction-tool evidence, not a Recursion formal-model gate or
production deployment qualification. The original checkout was not changed.

## Checks

| Check | Observed result |
| --- | --- |
| `python -B -m unittest tools.construction_swarm.tests.test_swarm -q` on Windows Python 3.12 | 30 tests, 27 passed, 3 platform skips |
| Same module under WSL Ubuntu 24.04 Python 3.12 | 30 tests, 29 passed, 1 Windows pool skip |
| `python -m ruff check tools/construction_swarm` | Passed |
| `git diff --check` | Passed |
| Fifty fixture leaves plus dependent synthesis | Peak 50 reservations, all 51 returned once; rerun did not dispatch again |
| Actual Bubblewrap/cgroup probes | Read-only source, absent host drives/home, isolated network, 64-process ceiling and detached-child cleanup verified |
| Documented prepare/init/run/manifest commands | All three example fixture jobs returned; no provider inference |
| Failure regressions | Packet errors isolated; rejected dependencies blocked; unknown reservations retained across campaigns; archived completed campaign admitted safely; forged staging manifest refused; injected cleanup failure retained |

Fixture concurrency is not evidence of 50 concurrent live Devin workers. The two
focused live reviews below overlapped. Host admission can reduce requested slots.
Windows skips Linux sandbox and symlink checks; Linux skips Windows shared-pool
coverage. Cross-platform tests do not establish support for every host setup.

WSL2 Ubuntu 24.04 booted using the registered `D:\WSL\ext4.vhdx`. The Linux tests
used installed Bubblewrap 0.9.0 and existing delegated cgroup controllers. No
parent controllers, assistant settings, provider authentication or autonomy flags
were changed. Windows Devin remains a trusted, tool-denied CLI transport; only
proposed-code tests execute inside Linux isolation.

## Actual SWE-2 Max review

Installed Devin CLI: `3000.10.21`; executable SHA-256:
`baca16c8d4930d2708458bd685c9092e07f8a59d73e59564835f7082532df9ab`.
Each successful export identified `SWE-2 Max`, contained no tool calls, exited
normally and yielded a schema-valid filing bound to frozen source hashes.
These are static model reviews, not executed tests or acceptance decisions.

| Attempt | Source | Result |
| --- | --- | --- |
| Initial whole-framework review | `5004e5c` | 600-second timeout; no filing; unknown reservation retained |
| `review-queue` | `2ea9bca` | Returned; 2026-09-11 00:37:13–00:39:38 UTC |
| `review-containment` | `2ea9bca` | Returned; 2026-09-11 00:37:13–00:41:49 UTC |

Raw packets, exports, receipts and dissent remain external under
`D:/RecursionSwarm/framework-review-20260910/run` and
`D:/RecursionSwarm/framework-review-parts-20260910/run`, in
`attempts/<job>/1/`. Raw CLI exports contain local context and are not committed.

Receipt SHA-256:

- Initial timeout: `97f6400d04853eb7f700535e8a036cbc12bbf92578f4028e352d13d0695432a0`.
- Queue: `5e2b2177fa215b58658c16794aa86a71e9a8e43c28374f5ddfa7980d010753e4`.
- Containment: `aecf64ba886e8a72fe88dcaa1af2f934615b648ece9ec2e33b141e78008ed1f2`.

The initial timeout confirmed local Job quiescence, not remote completion.
Its dispatch remains charged and its shared-pool reservation remains unknown.
Reported usage for successful queue/containment reviews was respectively
20,736/20,375 prompt tokens and 10,489/21,117 completion tokens. These are provider
observations, not a complete campaign cost ledger. The initial attempt lacks usage.

A separate tool-denial smoke probe attempted `exec`; Devin denied it. Its queued
read attempt was cancelled with the denied execution, so it does not independently
prove read denial. The packet reviews themselves made no tool attempts.

## Findings disposition

| Finding | Disposition |
| --- | --- |
| Packet construction exception aborts dispatch and strands other results | Fixed; bad packet becomes blocked while other futures settle. Reproduction test passes. |
| Rejected dependency leaves a silent queued job | Fixed; unresolved admission becomes an explicit blocked state with retained reason. |
| Historical pool claims depend forever on all old databases | Completed, non-retryable runs now retain compact zero-hold records. Unknown/retryable roots still require evidence; missing or corrupt evidence deliberately prevents admission. |
| Unknown outcomes retain capacity indefinitely | Intentional conservative boundary. Reconciliation exists in the CLI and requires positive normal completion evidence. No expiry, fabricated completion or automatic refund added. Blocked downstream work is now visible. |
| POSIX process groups can miss detached descendants | Fixed evidence claim: transport reports only direct exit; Linux model launch remains refused. Actual sandbox cgroups supply descendant cleanup proof. |
| Caller manifest can detach tests from a returned filing or expose controller state | Fixed; exact manifest registered by stage, current filing checked, source outside canonical controller root required. |
| Noncanonical stage root weakens destination guard | Fixed; resolve root and require agreement with ledger root before staging. |
| Cleanup failure loses observations and leaves unexplained scopes | Fixed; preserve result and cleanup observation, report failure, retain scope, refuse new tests with unreconciled scopes. Fault injection and actual normal cleanup are distinct tests. |

Some reviewer reasoning exceeded the supplied packet: the queue reviewer did not
receive the CLI containing `reconcile`, and SIGSTOP alone is not an unkillable
cgroup reproducer. Those assertions are not treated as observed facts. The valid
boundary concerns were independently assessed and addressed as listed above.

An independent Astra static review of `2344cdc` found no additional merge-blocking
issue in the changed files. It did not run tests or qualify provider behavior.

## Remaining limits

This increment supports frozen research/review/synthesis packets and proposed
complete code files; it does not grant Devin an interactive shell. Automatic
Cursor, Terra/Sol and Linux model adapters remain unqualified. Coordinators can
prepare plans through their existing authorized sessions. The lead selects the
next bounded packet and integrates reviewed code; Lucas merges.

CLI launch counts do not bound internal provider retries, tokens or remote cost.
The CLI's global session history is outside the export byte cap. Startup imports
on another host need qualification. There is no live 30–50-worker load claim,
automatic model substitution, operational deployment or new eight-hour campaign.

# P2 foundry observation progress

## Binding

- Date: 2026-09-14
- Parent: `goal-recursion-v2-execution-fabric`
- Product target: Recursion v3
- Branch: `codex/v3-p2-foundry-observation-20260914`
- Worktree: `C:\\r3fo`
- `TASK_BASE`: `e627cd93bac473094bc99e8fa29c8d62bae526a2`
- Allowed changes: the four new files in this packet only
- Providers, inference, schedulers, workers and service activation: zero

## Inputs read

- `CONTROL_PLANE.md`, then `ANCHOR.md`, `AGENTS.md` and `docs/v3/START-HERE.md`
- `docs/v3/construction/integration-20260914/NEXT.md` and `README.md`
- `docs/v3/construction/next-work-20260914/COMMON.md`
- `tools/construction_swarm/foundry.py`, especially `report`, `run_one` and run layout
- `tools/construction_swarm/ledger.py`, `runner.py`, `contracts.py`
- `tools/construction_swarm/p2_access.py` `AccessService`, adapter response, artifact,
  grant and `serve` interfaces, plus the existing P2 tests

The adapter contract pins the five exact dependency blobs from `TASK_BASE`. The foundry
ledger is observation evidence, not a second canonical Hermes registry. A returned worker
filing is not independently accepted unless the existing ledger has both the accepted job
state and matching `head-decision` event.

## Source preservation before implementation

```text
python -X utf8 -B docs/v3/construction/next-work-20260914/check_handoff.py
```

Exit 0 at exact `TASK_BASE`: `HANDOFF_SOURCE_PASS`, 49 unchanged v3 top-level
specifications, three packets, zero provider calls, no scientific execution or service
activation.

## Frozen acceptance state

`SPEC.md` and the focused acceptance test were written before the adapter. The required
facts, refusal cases, source/blob pins and input-byte invariance checks are frozen. The
first focused run is intentionally expected to fail because the adapter module does not
yet exist; that evidence will remain recorded after implementation.

## Results

Intentional pre-implementation red gate after freezing the contract and tests:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_foundry_observation
exit 1
ModuleNotFoundError: No module named 'tools.construction_swarm.p2_foundry_observation'
```

This is retained missing-implementation evidence, not a passing result. Implementation,
regressions, exact scope gate and independent Astra review remain pending.

The first implementation run retained two independent failures. Ten of 12 tests failed:

- the evidence verifier called nonexistent `hashlib.compare_digest`; and
- `Ledger.readonly` created empty SQLite WAL/SHM sidecars, violating the input-directory
  byte-invariance oracle.

The implementation now uses `hmac.compare_digest` and copies a stable, bounded database
plus any WAL into a temporary observation snapshot before opening SQLite. A second local
run passed all behavior cases; only the deliberately dirty-tree scope check failed because
the new adapter was not yet committed. That failure was not reclassified.

Candidate `c4af7b454b7d914296bda411524bcbf48a9dd62d` passed the clean 12-case
focused gate. A native Ubuntu-24.04 clone was created at
`<repo>-foundry/p2-foundry-observation-20260914` rather than using Windows
worktree Git pointers. On that candidate:

- focused observation gate: exit 0, 12 tests;
- P1 regression: exit 0, 18 tests; and
- P2 regression: exit 0, 19 tests.

The snapshot copy was then hardened with whole database/WAL-set pre/post signatures and a
live committed-WAL control. Candidate `072ebf448055e979a4fa54fbb1ca76c770ee3800`
passed from the clean native clone:

- focused observation gate: exit 0, 13 tests in 1.034 seconds;
- P1 regression: exit 0, 18 tests in 1.872 seconds;
- P2 regression: exit 0, 19 tests in 5.588 seconds.

The live-WAL case observed its committed event without changing database, WAL, SHM or any
attempt bytes. All fixture trees remained below 32 MiB and no provider, scheduler, worker
or service path ran.

On the same exact candidate, the existing handoff-preservation check exited 0 with
`HANDOFF_SOURCE_PASS`, 49 unchanged v3 specifications and zero provider calls. The
additive focused source check confirmed exact `TASK_BASE`, the dependency blobs, a
clean branch and exactly the four allowed new paths. `git diff --check TASK_BASE HEAD`
also exited 0.

Candidate `9b25a10aeb9281e3961ea7df8ed3b2772fe760cf` was not approved. During
self-audit, before its Astra review completed, the actual `foundry_tools.py` producer was
rechecked and showed that every tool-manifest row has `number`, `sha256`, and `name`. The
candidate verifier required only the first two fields, so real returned work using tools
would have been reported unavailable despite the synthetic fixture passing. The obsolete
review was interrupted and produced no verdict.

The repair uses the exact three-field row, binds `name` and `number` back to the verified
request, requires receipt outcome identity, and makes contradictory head decisions
unavailable instead of accepted. Its fixture now has the actual tool row/request shape and
an injected contradictory-decision control. The evidence file ceiling was also aligned to
the actual foundry's 32 MiB export ceiling while preserving a finite 64 MiB aggregate
verification ceiling.

Repaired candidate `1218ec7d891fd912dda5e19c108edfdc34032420` passed from the
clean native clone:

- focused observation gate: exit 0, 13 tests in 1.056 seconds;
- P1 regression: exit 0, 18 tests in 1.911 seconds;
- P2 regression: exit 0, 19 tests in 5.623 seconds.

Independent Astra review of successor candidate
`3219ec98cb71e7e44f82807b2686b5c4ac4aebd3` reran every gate successfully but
returned `repair`. Its bounded probes found five counterexamples retained as failed
evidence:

- hostile billion-sized attempt/event integers caused unbounded `range` allocation;
- regular-file-to-FIFO replacement could block both database and artifact opens;
- same-inode growth between `lstat` and `open` bypassed the file/budget charge;
- a valid 1,126,707-byte producer-generated tool receipt exceeded an accidental 1 MiB
  verifier default; and
- an integer cursor from one run could be silently reused after adapter restart for a
  different run.

The reviewer used fixtures below 1.2 MiB, two-second bounded children and a 192 MiB
address-space cap. It changed no files and made no provider or service call.

The remediation bounds stored counters before comparison without allocating from them,
opens source records nonblocking, rechecks descriptor size before charging/reading, uses
the producer's 3 MiB tool-receipt ceiling, and adds producer-generated and adversarial
controls. Because unchanged P2 cursor parameters contain only an integer and no durable
run binding, all foundry `events` replay now refuses with `snapshot_required`; the latest
durable event remains a status observation, not a replay cursor. `foundry_tools.py` and
`foundry_client.py` source blobs are now also pinned.

Remediated candidate `0d6e324c6e4d82cfe9c0f9ee7692d35ed704e1c8` passed from the
clean native clone:

- focused observation gate: exit 0, 16 tests in 1.385 seconds;
- P1 regression: exit 0, 18 tests in 1.862 seconds;
- P2 regression: exit 0, 19 tests in 5.586 seconds;
- handoff preservation: exit 0, `HANDOFF_SOURCE_PASS`, 49 unchanged specifications;
- source/scope and `git diff --check`: exit 0, exact four paths and seven pinned
  dependency blobs.

Documentation candidate `d2837b59c2063788c5aaf417ea88331714f7332d` repeated those
gates in the clean native clone: focused 16 in 2.161 seconds, P1 18 in 2.690 seconds,
P2 19 in 5.597 seconds, handoff `HANDOFF_SOURCE_PASS` with 49 specifications, and an
empty `git diff --check`. Independent Astra review reproduced every prior repair and 15
digest/identity mutations, but returned `repair` after finding another malformed-ledger
counterexample:

- an `accepted` job whose current attempt was changed to `unknown` still asserted
  `independently_accepted=true`; and
- an `unknown` job whose current attempt was changed to `failed` exposed a known effect
  and released its observation hold even though the source ledger retains capacity by
  job state.

Both source fixture trees remained byte-identical. The reviewer also verified bounded
refusal during a committed-WAL copy race, followed by a stable successful observation.
The newly frozen state-coherence control then failed exactly those two contradiction
cases while the missing-current-attempt control already refused as an incomplete prefix;
that local red run executed one test with two failures and exit 1.

The repair binds every job state to the source-supported current-attempt state before any
projection. Contradictory pairs now refuse the complete snapshot, so they can neither
assert acceptance nor release a hold. Added positive controls preserve a failed-attempt
retry, recovery of its second running attempt to retained `unknown`, and explicit
reconciliation to `cancelled`. The 17 behavioral tests passed locally after the repair
(one POSIX-only FIFO control skipped on Windows). Candidate
`200e8cccc1e7701f6f199ec1c8e9176181176857` then passed from the clean native clone:

- focused observation gate: exit 0, 18 tests in 2.780 seconds;
- P1 regression: exit 0, 18 tests in 2.939 seconds;
- P2 regression: exit 0, 19 tests in 5.584 seconds; and
- handoff preservation: exit 0, `HANDOFF_SOURCE_PASS`, 49 unchanged specifications.

The documentation-only successor requires one final exact-commit gate run and Astra
verdict.

## Limits and negative evidence

- Temporary fixture bytes are capped below 32 MiB; child commands use 15-second timeouts
  and the focused gate has a 120-second ceiling.
- No live completed-run smoke has been performed (`unrun`).
- No canonical state/acceptance integration, product-runtime agent, product store,
  physical lifecycle durability, provider telemetry or real fleet readiness is claimed.
- No production service/fleet activation, provider call, configuration/auth/model/cron/
  autonomy change, publication or merge is authorized.

# Using the Session A oracle for Stage B (design)

Status: **DESIGN ONLY / UNEXECUTED.** This note plans how Stage B would consume
`experiments/v3/fu-03-kernel-session-a/oracle` as its independent expectation source. It does
not run the oracle, and reading the plan is not a Stage B result. The oracle itself remains a
candidate reference implementation; its own `README.md` records the non-proofs.

## What the oracle provides

`experiments/v3/fu-03-kernel-session-a/oracle/` is pure-Python, deterministic and provider-free.
It supplies three surfaces Stage B would use:

| Surface | Role in Stage B |
|---|---|
| `refstate.RefValid(log)` | structural validity of a finite committed prefix: schema, aggregate, writer epoch, ordinal, predecessor chain, digest binding, command binding and semantic preconditions |
| `refstate.RefState(log)` | deterministic fold of the committed event log into canonical state (schema, aggregate, ordinal, tail, goal, plan, lease, writer, pause epoch, paused, status, owner, attempt, effect, timer, result, cancelled, receipts, outbox, retry-ready) |
| `refstate.RefProject(log)` | the fixed 16-field projection tuple; Stage B reads status `[3]`, attempt `[8]`, paused `[9]`, result value `[12]`, effect status `[14]` and timer status `[15]` |
| `trace_checker.check_trace(trace)` | bounded bridge: replays a finite trace of events, admissions and observed digests/projections, reporting the first divergence index |

`refstate.py` does not import, call or consult any model, live reducer, provider or host action.
That independence is exactly why Stage B uses it as the expectation side rather than the
candidate reducer.

## Independence rule

Stage B's safe claim is "stale or ambiguous work never becomes a new authorized effect". The
candidate's own reducer is not a valid oracle for that claim: it would share a bug with itself.
The design therefore fixes the comparison direction:

- **Expectation side:** the Session A oracle, fed the canonical committed log.
- **Observation side:** the independently observed receiver mutation ledger, durable installed
  floor and receipt cut.
- **Never the reverse:** the candidate reducer's output is not used to generate the expected
  reference state. The folded expected state is compared against the candidate's claimed state,
  not the other way round.

For each fixture in `fixtures.json` the design names which projection is compared:
`RefValid` only, `RefState` fields, or the full `RefProject` tuple. A fixture whose oracle
cannot be named is blocked, not passed.

## Trace-validity bridge limits

`trace_checker.check_trace` is a **bounded observed-consistency check of one finite behaviour**,
assuming the supplied observations are faithful and complete. It is not a refinement proof.
Stage B would therefore use it for:

- Confirming that the supplied committed prefix is internally valid and binds to the observed
  state digest / projection.
- Localizing the first divergence index between the expected fold and the observations.

It would **not** use it to claim:

- Quantification over all executions, fairness, liveness or exactly-once external effect.
- That the candidate produced the events or that the observations are faithful.
- Durable storage, OS containment, provider trust or physical quiescence.
- That the reference equations themselves are correct. The oracle is independently authored but
  not proven; a shared specification error with the candidate is not excluded by authorship.
- Any behaviour beyond the declared bounds (one aggregate and task, at most 20 committed events,
  lease epochs at most 3, attempts at most 2, outbox and queue capacity 2).

## How a Stage B run would be wired (later, under separate authorization)

1. Freeze the candidate cut, profile and the exact oracle revision; record both hashes.
2. For each fixture, construct the finite committed log and the independent observations from
   the fixture's schedule. The observation side is authored outside the candidate.
3. Bind expectations: call `RefValid` for structural validity and `RefState`/`RefProject` for
   the named projection. Where the fixture compares observed state, build a trace for
   `trace_checker` with `observed_state_digest` or `observed_projection`.
4. Compare at the declared cut only. Do not promote a result because the candidate exits zero,
   the fold parses or the oracle agrees without an independent observation.
5. Classify each fixture as bounded-consistent, divergent at a named index, invalid,
   out-of-scope, unsupported, not-run or blocked. Preserve failures and unknowns.
6. Retain the raw logs, the observation ledger and the first-divergence index as evidence.

## Additions Stage B needs beyond the Session A oracle

The Session A oracle models the kernel's canonical state and admission, not the receiver fence,
Stop modes or resource conservation as first-class objects. Stage B must therefore add
independent observers (not oracle imports) for:

- The receiver's durable installed floor, install acknowledgement and mutation ledger.
- Per-mode Stop target sets and lifecycle fact vectors (requested / accepted / fenced /
  acknowledged / local-exited / remote-observed).
- Reservation and liability conservation across replacement and recovery.

These additions are the observation side. Where they are absent, the corresponding fixture is
`blocked` or `unknown`, never a pass.

## Non-proofs carried forward

- The oracle is a bounded bridge, not the integrated-bound TLC gate and not a kernel freeze.
- Session A results are diagnostic; Stage B reuses the artifact, not its authority. Stage B
  still awaits independent verification of Session A.
- A simulated receiver checked by this oracle does not qualify an external service, native
  process containment or real automatic takeover.

# FU-03 Stage B — canonical commit, dispatch, receiver fences and Stop

Status: **EXECUTED** for the provider-free synthetic run recorded in `results/` at candidate
commit `e21cd75` (Session A admitted). This directory still grants no execution authority,
proves nothing beyond the bounded corpus and remains an experiment: a finite crash-cut matrix, an
oracle-reuse plan, a synthetic harness plus observation side, and two gates. Stage B remains
non-normative.

Authoring boundary: local design and synthetic execution on 2026-10-02, provider-free, no
network, no store or framework selection, no live provider/game/host action, no change outside
`experiments/v3/fu-03-stage-b/`. The execution used only the Session A reference oracle as the
expectation side and independently authored observers as the observation side.

Earlier design-only status (preserved): before this run the directory ran nothing and granted no
authority. The design artifacts below are unchanged; `fixtures.json` remains `unexecuted` because
results live in `results/stage_b_results.json`, not in the matrix.

## Parent goal and anchor

Primary joined case: `synthesis/INTEGRATION-TEST-HANDOFF.md` IT-02 (canonical commit receiver
fencing and Stop crash cuts). Section source: `LOCAL-SESSION-HANDOFF.md` section B.

Goal (verbatim from the packet, restated as the acceptance object):

> stale or ambiguous work never becomes a new authorized effect through retry, crash or takeover.

## Scope

In scope:

- A finite, data-described crash-cut matrix across six cut points and three receiver-fence
  states, under the three Stop modes.
- The named lane-case references preserved as claims, each mapped to at least one fixture.
- A plan for reusing the Session A reference oracle as an independent expectation source.
- A deterministic gate over the design (parse, required fields, reference coverage, no
  execution claim).

Out of scope (non-goals):

- Any live/provider/host action, TLC/TLC-like invocation, container, VM or native fault
  injection. The executed run is a pure-Python synthetic harness only.
- Selecting a language, store, framework, sandbox or final actuator design.
- Claiming 36/36, kernel freeze, integrated-bound coverage or IT-02 acceptance.
- Re-opening Session A findings or the frozen M1A/M1B/M1C contracts.
- Touching protected paths or any path outside `experiments/v3/fu-03-stage-b/`.

## Prerequisites (all must be recorded before any Stage B run is admitted)

1. **Exact operation/attempt and epoch domains.** Command delivery identity
   (`command_id`), semantic effect identity (`logical_operation_id`) and dispatch attempt
   (`attempt_id`) are separate. Writer, work, pause, lease, goal and plan epochs are named with
   their domain and issuer; numbers from different domains are never compared
   (`OWNERSHIP-AND-FIELD-MAP.md`, "Identity domains and explicit adapters").
2. **Independently observed receiver installation and mutation boundary.** The receiver's
   durable installed floor, its linearization order and each mutation must come from an
   observer that is not the candidate reducer. Canonical revocation alone does not establish
   remote installation.
3. **Idempotency and reconciliation rules.** For each stable logical operation: at most one
   effect; duplicate old receipts are historical acceptance, never fresh authority; changed
   bytes under the same ID conflict; reconciliation settles an existing effect rather than
   repeating it.
4. **Durable intent and canonical acceptance contract.** The exact store/profile that makes a
   commit acknowledged and durable, and the exact boundary at which an intent becomes a
   dispatchable effect. Acknowledged state must recover within the declared durability profile.
5. **Finite crash schedules.** A bounded set of injected cuts and stop points, fixed before
   execution, with each cut's expected disposition written down.
6. **Known control reserve.** The resource contract declares gross versus net limits, the
   reserved control allowance, and that recovery moves withheld allowance into outstanding
   without changing the conserved total. Uncertain liabilities are annotated once and never
   double-counted (`OWNERSHIP-AND-FIELD-MAP.md`, "Resource compatibility").

## Required evidence (per admitted run)

- The same logical operation traced across commit, dispatch and response-loss cuts.
- Independent receiver-fence observation: durable floor, install acknowledgement and mutation
  ledger, separate from the candidate.
- Stale receiver rejection after the installed-current fence, with a pre-install exposure
  interval recorded as pending/unknown rather than complete.
- No blind duplicate effect: exactly one effect for a stable operation, zero for a
  pre-dispatch refused/revoked one.
- Scope-correct Aggressive/Full/Lazy receipts; requested/accepted/fenced/acknowledged/
  local-exited/remote-observed remain distinct.
- Conservation of settled usage, outstanding reservations and uncertain liabilities across
  every cut.
- A positive control that produces the intended single effect, plus a negative control that
  refuses stale work; an observer that sees nothing cannot pass.

## Results (2026-10-02, candidate commit e21cd75)

Provider-free synthetic run over the 26-fixture matrix. Expectation side: the Session A oracle
(`refstate.RefValid` / `RefState` / `RefProject`, `trace_checker.check_trace`) folded over the
materialized committed log. Observation side: independently authored observers
(`run/observers.py`) for the receiver fence, Stop lifecycle, receipt binding and reservation
liability. The oracle is never used to generate the observation and the observation is never used
to generate the expectation.

Disposition counts (`results/stage_b_results.json`):

| Disposition | Count | Meaning |
|---|---|---|
| bounded_consistent | 16 | oracle expectation and independent observation agree at the declared cut |
| unknown | 3 | outcome cannot be bounded; preserved as unknown, never promoted |
| unsupported | 5 | fixture needs a mechanism the synthetic kernel does not model |
| blocked | 2 | required native observer/authorization genuinely absent |
| divergent / invalid / out_of_scope | 0 | none |

Controls:

- Positive control `SB-05`: exactly one committed effect, independent receiver mutation count 1,
  liability settled once.
- Negative controls `SB-07` (stale epoch-7 and unqualified-issuer mutations refused; floor 8
  monotonic across restart) and `SB-14` (identical duplicate cached, changed bytes
  `COMMAND_CONFLICT`, stale lease refused). Neither is a pass without a rejection.
- Trace control `SB-03`: `check_trace` accepts the retained prefix and rejects a corrupt
  duplicate append at the first divergence index.

Conservation holds for every fixture that carries a resource ledger; uncertain liabilities are
annotated once and recovery preserves the conserved total.

Fixtures preserved `unknown`/`unsupported`/`blocked` (never a promoted pass):

| Fixture | Disposition | Reason |
|---|---|---|
| SB-09 | unknown | pre-install exposure interval cannot be resolved; effect stays pending/unknown |
| SB-11 | unknown | a rooted member is unreachable; stop unresolved with held liability |
| SB-12 | unknown | Lazy deadline reached with no boundary/quiescence evidence |
| SB-15 | unsupported | transport/apply stages have no provider-free independent observer |
| SB-20 | unsupported | writer-takeover availability/plugin/restore semantics not modeled |
| SB-21 | blocked | needs an authorized native abrupt reset and durable store |
| SB-22 | blocked | needs a real process launch and incarnation register |
| SB-24 | unsupported | native abort / queued follow-up / approval reconnect not modeled |
| SB-25 | unsupported | offline spool and reconnect need an external authority trace |
| SB-26 | unsupported | TTL and externally observable effect need an external service clock |

This result is bounded safety evidence for the synthetic corpus only and is unchanged in kind by
having executed: the stop conditions and non-proofs below still apply.

## Stop and non-proofs

Stop and record `invalid`/`unknown`/`blocked` (never a promoted pass) when:

- A required observer, fence floor or durable boundary is missing.
- A timeout is taken as physical quiescence.
- A cancellation acknowledgement is read as rollback.
- A missing or unavailable counter is read as released liability or zero usage.
- A simulated receiver is offered as qualification of an external service, native process
  containment or real automatic takeover.

Explicit non-proofs:

- Passing a finite synthetic matrix is bounded safety evidence for this corpus. It is not
  unbounded liveness, exactly-once external effect, physical non-overlap or provider trust.
- No inferred physical quiescence from timeout.
- No canceled-equals-rolled-back claim.
- No released liability from missing counters.
- A simulated receiver does not qualify an external service.
- Historical FU04 lock-directory/fsync/file-size observations do not satisfy the IT-02 oracle.
- Abrupt-VM-reset replay and native platform cells are separate from a pure synthetic receiver
  test and require their own authorization.

## Files

| Path | Role |
|---|---|
| `README.md` | this scope, status, prerequisites, evidence and stop/non-proofs |
| `fixtures.json` | the crash-cut matrix as data; every fixture `unexecuted` |
| `USING-SESSION-A-ORACLE.md` | how the Session A oracle is the independent expectation source, and its limits |
| `check_stage_b.py` | deterministic design gate over this directory only |
| `run/harness.py` | materializes each fixture's schedule into a canonical committed log and a separate observation side |
| `run/observers.py` | independent receiver-fence, Stop-lifecycle, receipt-binding and reservation/liability observers (no oracle import) |
| `run/run_stage_b.py` | runs all 26 fixtures; oracle expectation vs observer observation; writes results |
| `run/check_stage_b_run.py` | run gate over the results, with vacuity probes |
| `results/stage_b_results.json` | per-fixture disposition, reason, expectation, observation and check evidence |
| `results/logs/SB-*.json` | raw committed logs, admissions and observations per fixture |

## Gate

```text
python -X utf8 -B experiments/v3/fu-03-stage-b/run/run_stage_b.py
python -X utf8 -B experiments/v3/fu-03-stage-b/run/check_stage_b_run.py
python -X utf8 -B experiments/v3/fu-03-stage-b/check_stage_b.py
python -X utf8 -B tools/check_public_scope.py
```

`check_stage_b.py` is the design-only gate: a pass certifies that the matrix parses, every fixture
carries the required fields with valid enum values, every named lane case is referenced, no
fixture claims execution, and no field claims a run result. `fixtures.json` stays `unexecuted`;
run evidence is separate.

`run_stage_b.py` executes the 26 synthetic schedules and writes
`results/stage_b_results.json` and `results/logs/`. `check_stage_b_run.py` certifies that all 26
fixtures carry a disposition, that no `bounded_consistent` fixture lacks either an oracle
expectation or an independent observation (or a two-sided comparison), that the positive control
produced one effect, that the negative controls and the trace control rejected stale/duplicate
work, that conservation holds, and that the simulated receiver is recorded as not being
qualification. It runs vacuity probes (strip observation, flip a check, zero a negative control,
mark an unbacked pass) and fails if it cannot reject them. None of this is IT-02 acceptance.

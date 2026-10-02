# FU-03 Stage B — canonical commit, dispatch, receiver fences and Stop

Status: **DESIGN ONLY / UNEXECUTED.** This directory scopes the packet's Stage B; it runs
nothing, proves nothing and grants no execution authority. Stage B awaits independent
verification of Session A before any target is admitted. Every artifact here is a fixture and
handoff design: a finite crash-cut matrix, an oracle-reuse plan and a design gate. There is no
entrypoint to execute beyond the design checker.

Authoring boundary: local design work on 2026-10-02, provider-free, no network, no store or
framework selection, no change outside `experiments/v3/fu-03-stage-b/`.

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

- Any run, replay, TLC/TLC-like invocation, container, VM, host or provider action.
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

## Required evidence (per admitted run, later)

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

## Gate

```text
python -X utf8 -B experiments/v3/fu-03-stage-b/check_stage_b.py
python -X utf8 -B tools/check_public_scope.py
```

The first command is a design-only gate. A pass certifies that the matrix parses, every fixture
carries the required fields with valid enum values, every named lane case is referenced, no
fixture claims execution, and no field claims a run result. It is not a Stage B pass and not
IT-02 acceptance.

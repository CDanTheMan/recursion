# FU-03 Stage B — independent verification handoff

Status: **awaiting independent verification.** An implementer's PASS is not acceptance
(`CONTROL_PLANE.md` invariant 3). Run this in a separate session on a **different model family**
(e.g. Muse) and record the model + version.

## Candidate

- Repository: `https://github.com/NotSkittlz/recursion`
- Commit: **`d56cc44`** (PR #150 merged): `experiments/v3/fu-03-stage-b/` (design + `run/` + results)
  and `experiments/v3/fu-03-kernel-session-a/oracle/` (the verified expectation oracle).
- Snapshot Session A acceptance first: `experiments/v3/fu-03-kernel-session-a/verification/`.

## Fresh checkout

```text
git clone https://github.com/NotSkittlz/recursion.git recursion-verify-b
cd recursion-verify-b
git checkout d56cc44
```

## Run

```text
python -X utf8 -B experiments/v3/fu-03-stage-b/run/run_stage_b.py
python -X utf8 -B experiments/v3/fu-03-stage-b/run/check_stage_b_run.py
python -X utf8 -B experiments/v3/fu-03-stage-b/check_stage_b.py
python -X utf8 -B tools/check_public_scope.py
```

Expected: `STAGE_B_RUN` 26 fixtures with `16 bounded_consistent / 5 unsupported / 3 unknown /
2 blocked / 0 divergent`; `STAGE_B_RUN_GATE_PASS`; design gate `STAGE_B_DESIGN_PASS`; public scope
`PASS`.

## Checks beyond rerunning

1. **Direction of comparison:** the Session A oracle is the **expectation** side and the
   harness/observers are the **observation** side — confirm the runner never generates expected
   state from the candidate it is testing. Confirm `run/observers.py` does not import the oracle.
2. **Honesty of non-passes:** confirm the 5 `unsupported`, 3 `unknown` and 2 `blocked` fixtures are
   genuinely unresolved (missing observer / no provider-free independent observation), not
   downgraded to inflate a pass count.
3. **Controls:** confirm the positive control yields exactly one effect and the negative controls
   reject stale/duplicate work; confirm conservation of settled/outstanding/withheld.
4. **Gate honesty (vacuity):** confirm `check_stage_b_run.py` **fails** when a pass-equivalent is
   stripped of its observation, when a check is flipped, when a negative control is zeroed, and on
   an unbacked pass. (The gate exercises these probes every run; reproduce one manually.)
5. **Non-proofs preserved:** a simulated receiver is **not** qualification of an external service,
   native containment or real takeover; no timeout-as-quiescence; no canceled-equals-rolled-back;
   no released liability from missing counters.

## Falsifiers (verification fails if)

- A fixture is a pass-equivalent without **both** an oracle expectation and an independent
  observation.
- The runner derives expectations from the candidate rather than the oracle.
- A vacuity probe fails to be rejected by the gate.
- `unsupported`/`unknown`/`blocked` are relabelled as passes.
- Any claim of IT-02 acceptance, qualification or 26/26 safety beyond the bounded synthetic corpus.

## Result

Copy `verification/RESULT-TEMPLATE.md` to
`experiments/v3/fu-03-stage-b/verification/results/<sha>-<model-slug>.md`, fill it in, commit on a
review branch, and return it. Record model + version, candidate SHA, commands + raw outputs,
per-check PASS/FAIL, residual unknowns, reviewer identity, and the decision.

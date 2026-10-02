# Session A verification result — clean-checkout reproducibility (same family)

- Verifier model + version: `opencode/deepseek-v4.1-flash` — **same family as the implementer; this
  is NOT model-independent.**
- Session / operator: automated local session, 2026-10-02
- Candidate repository + commit SHA: `https://github.com/NotSkittlz/recursion` @ `6fcaaba`
- Fresh checkout? **yes** (`git worktree add --detach <path> 6fcaaba`)
- TLA+ jar SHA-256 observed: `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`
  (matches the pin; jar copied from the main checkout)

## Commands and raw outputs

```text
$ python -X utf8 -B experiments/v3/fu-03-kernel-session-a/check_session_a.py
SESSION_A_PASS registry=36 model_dispositioned=36 killed=10 M25=KILLED M31=NOT_KILLED_WITHIN_BOUND witness=NoBlindEffectReplay oracle_exit=0

$ python -X utf8 -B experiments/v3/fu-03-kernel-session-a/oracle/check_oracle.py
... ORACLE_PASS (bounded OBSERVED-consistency check, not a machine-checked refinement)

$ python -X utf8 -B experiments/v3/fu-03-kernel-session-a/model/check_model.py
MODEL_PASS RBig baseline recorded (witness); RFixed clean; M25=KILLED M31=NOT_KILLED_WITHIN_BOUND; 10 killed; all 36 registry ids dispositioned

$ python -X utf8 -B tools/check_public_scope.py
PASS: no other-project identifiers found in repository text files
```

## Per-check disposition

| Check | Disposition | Note |
|---|---|---|
| 36-row registry, each dispositioned | PASS | verified by `check_session_a.py` on the fresh tree |
| Witness is `NoBlindEffectReplay` | PASS | `check_session_a.py` asserts it |
| `RFixed` guard removes the witness | NEEDS-EVIDENCE | not re-derived from scratch in this run |
| Oracle independent of model/live reducer | NEEDS-EVIDENCE | not inspected by this run |
| Gate-honesty probe (gate fails when result removed) | NEEDS-EVIDENCE | not performed |
| Symmetry assumption accepted/rejected | NEEDS-EVIDENCE | deferred to the independent verifier |
| `CORR/GOAL` fixture qualification spot-check | NEEDS-EVIDENCE | deferred |
| No claim upgraded to verified/qualified | PASS | artifact set unchanged |

## Residual unknowns

The checks marked NEEDS-EVIDENCE require a verifier who reads the artifacts critically; a rerun of
our own gates on a clean tree proves reproducibility only, not correctness or independence.

## Reviewer identity and decision

- Decision: **REPRODUCIBLE (same-family), NOT independent verification.**
- Rationale: the candidate is self-contained and reproduces on a fresh checkout, but model-family
  independence and the gate-honesty/oracle-independence probes remain outstanding. Session A is
  **not yet accepted**; Stage B stays design-only until the independent verifier signs off.

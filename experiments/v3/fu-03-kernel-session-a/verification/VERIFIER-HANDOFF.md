# FU-03 Session A — verifier handoff

Purpose: independent verification of Session A (`CONTROL_PLANE.md` invariant 3 — an implementer's
PASS is not acceptance). Run this in a **separate session on a different model family** (e.g. Muse
1.3 Contributor) and record the model + version in the result.

Do **not** reuse the implementer's working tree, this repo's uncommitted state, or the implementer's
summary as evidence.

## Candidate

- Repository: `https://github.com/NotSkittlz/recursion`
- Branch: `loop/work/overnight-intake-20261002`
- Candidate commit: **`6fcaaba`** (tip containing Session A + this handoff). Session A itself was
  `b1f42c2`; if the branch has merged, use the merge commit on `master` — record the exact SHA.
- Artifacts: `experiments/v3/fu-03-kernel-session-a/{mutants-registry.json, RECONCILIATION.md,
  FIXTURE-QUALIFICATION.md, oracle/, model/}`.

## Fresh checkout

```text
git clone https://github.com/NotSkittlz/recursion.git recursion-verify
cd recursion-verify
git checkout <CANDIDATE_SHA>
```

## Toolchain

- Python 3.12+, Java 21 (Temurin).
- The TLA+ tools JAR is **not tracked** (gitignored). Fetch it and verify the digest:

```text
New-Item -ItemType Directory -Force -Path tools/tlaplus | Out-Null
Invoke-WebRequest -Uri https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar -OutFile tools/tlaplus/tla2tools.jar
(Get-FileHash -Algorithm SHA256 tools/tlaplus/tla2tools.jar).Hash
# expected: 936A262061C914694DFD669A543BE24573C45D5AA0FF20A8B96B23D01E050E88
```

Provider-free; no network beyond the JAR fetch; no secrets; do not modify the candidate.

## Run

```text
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/check_session_a.py
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/oracle/check_oracle.py
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/model/check_model.py
python -X utf8 -B tools/check_public_scope.py
```

Optional full re-derivation (slow; re-runs TLC):

```text
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/model/run_baselines.py
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/model/mutants.py
```

## Checks and falsifiers

Follow `experiments/v3/fu-03-kernel-session-a/VERIFICATION.md` in full. Minimum:

1. Registry is exactly 36 rows `M01..M36`, each dispositioned; `M25`/`M31` justified in text.
2. `model/results/baseline-witness.json` records `NoBlindEffectReplay`; the `RFixed` guard is what
   removes it.
3. `oracle/refstate.py` does **not** import or invoke the TLA model or a live reducer; vector
   expectations are hand-stated.
4. **Gate-honesty probe:** perturb a result (e.g. set `M25` to a non-KILLED disposition) in a copy
   and confirm `check_model.py` / `check_session_a.py` fail; restore afterwards.
5. Symmetry assumption (`CONSTRAINT CanonicalIds`) accepted or rejected explicitly.
6. `CORR-M1A`/`GOAL-M1A` spot-checked against `scripts/v3/planning/replay/kernel.py:282-290`.

Verification **fails** if the witness is missing/wrong, `M25` is not KILLED, the registry is not 36
rows, the oracle depends on the model, a gate is vacuous, or any claim of 36/36 / kernel freeze /
qualification is made.

## Result

Copy `verification/RESULT-TEMPLATE.md` to
`verification/results/<candidate-short-sha>-<model-slug>.md`, fill it in, and commit it on a review
branch (or return it to Lucas). Record: model + version, candidate SHA, commands + raw outputs,
per-check PASS/FAIL, residual unknowns, reviewer identity, and the decision.

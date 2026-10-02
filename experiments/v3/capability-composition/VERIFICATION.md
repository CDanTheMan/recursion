# Capability-composition conformance suite — verification handoff

Status: **awaiting independent verification.** An implementer's PASS is not acceptance
(`CONTROL_PLANE.md` invariant 3; `AGENTS.md` rule 6). Verify in a separate session on a **different
model family** (an "Astra" researcher review is welcome in addition to, not instead of, the
independent verifier), and record the model + version.

## Candidate under review

- Verify at the **PR #160 merge commit on master** (or the branch head `07095d4`, which contains
  this handoff). The R-PC results were produced at code commit
  `0e74886101d2aee8002afb29593f1021cf64c61b`.
- Scope: **R-PC fixtures F01/F11/F12** (`run/check_rpc_fixtures.py`) and **F02–F10, F13–F16**
  (`run/check_rpc_invariants.py`), plus the structural gate `check_suite.py`.
- Explicitly **deferred, not passed:** F17/F18 (scripted accounting/analysis; not provider-free
  behavioral evidence). See `FIXTURE-INDEX.md`.

## Fresh checkout

```text
git clone https://github.com/NotSkittlz/recursion.git recursion-verify-capcomp
cd recursion-verify-capcomp
git checkout <PR #160 merge commit>   # or: git checkout loop/work/capcomp-conformance-20261002
```

## Run

```text
python -X utf8 -B experiments/v3/capability-composition/check_suite.py
python -X utf8 -B experiments/v3/capability-composition/run/check_rpc_fixtures.py
python -X utf8 -B experiments/v3/capability-composition/run/check_rpc_invariants.py
python -X utf8 -B tools/check_public_scope.py
```

Expected: `PASS: capability-composition suite structure clean`; `RPC_FIXTURE_PASS`; and
`RPC_INVARIANTS_PASS` with every case reporting candidate-matches-expected **and** mutant-detected.

## Checks beyond rerunning

1. **Oracle independence** — confirm `run/oracle.py` and `run/rpc_expected.py` contain no import of
   `reference_model`/`rpc_model` and do not compute expectations from candidate output. The
   expectations must be literal/report-derived.
2. **Mutants actually detected** — confirm each function in `run/rpc_mutants.py` is exercised and
   that it differs from the expected fields on at least one asserted field. Reproduce one manually.
3. **No candidate-flag trust** — confirm the gate compares candidate results against independent
   expected fields, never against a candidate `pass`/`coherent`/`no_effect` flag.
4. **Fidelity to the report** — spot-check against `rpc/report.md` §9: the 23-byte specimen
   (`[0,8)`/`[8,18)`/`[18,23)`); the core change (length 24, offsets `[9,19)`/`[19,24)`); the
   two-byte Unicode character counted as two byte units; and the F02–F16 predicates.
5. **Deferral honesty** — F17/F18 are marked `deferred` and are not counted as passes.
6. **Non-proofs preserved** — no model-quality, latency, resource, security, injection-resistance,
   platform-isolation, qualification or porting claim; bounded synthetic scope only.

## Falsifiers (verification fails if any)

- The oracle or expectations import or derive from the candidate model.
- Any planted mutant passes (i.e. is not detected).
- Any fixture's expected values disagree with the report's predicates.
- F17/F18 (or any unexecuted case) are counted as passes.
- Any claim is made beyond bounded synthetic conformance.

## Result

Copy `run/RESULT-TEMPLATE.md` to `results/<sha>-<model-slug>.md`, fill it in, commit on a review
branch, and return it. Record model + version, candidate SHA, commands + raw outputs, per-check
PASS/FAIL, residuals, reviewer identity, and the decision (ACCEPT / REJECT / NEEDS EVIDENCE).

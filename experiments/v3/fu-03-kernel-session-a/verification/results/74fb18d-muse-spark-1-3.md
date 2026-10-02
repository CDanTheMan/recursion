# Session A verification result

- Verifier model + version: Muse Spark (meta/muse-spark-1.3-contributor) via OpenCode session, 2026-10-02
- Session / operator: independent-verifier turn in the main workspace (read + fresh-clone evidence; no candidate files modified)
- Date (YYYY-MM-DD): 2026-10-02
- Candidate repository + commit SHA: https://github.com/NotSkittlz/recursion @ 74fb18dea58361a2d0f51f8aafd194659014cadf (tip of loop/work/overnight-intake-20261002 at fetch time; Session A itself was b1f42c2, handoff references 6fcaaba)
- Fresh checkout? (yes): git clone into C:\Users\Lucas\AppData\Local\Temp\opencode\recursion-verify-fu03a + checkout 74fb18dea58361a2d0f51f8aafd194659014cadf (detached HEAD, clean tree). All reruns below executed in that tree unless noted.
- TLA+ jar SHA-256 observed (expected `936a2620…`): 936A262061C914694DFD669A543BE24573C45D5AA0FF20A8B96B23D01E050E88 (fetched v1.7.4 into the fresh tree's gitignored tools/tlaplus/; matches pin)

## Commands run (raw outputs attached or inline)

```text
$ python -X utf8 -B experiments/v3/fu-03-kernel-session-a/check_session_a.py
SESSION_A_PASS registry=36 model_dispositioned=36 killed=10 M25=KILLED M31=NOT_KILLED_WITHIN_BOUND witness=NoBlindEffectReplay oracle_exit=0

$ python -X utf8 -B experiments/v3/fu-03-kernel-session-a/oracle/check_oracle.py
ORACLE_PASS 51 vectors; admission=20, canonical_bytes=9, canonical_decode=9, digest_domains=1, log_reduction=10, trace=2
ORACLE_PASS RefState deterministic across two invocations on every valid reduction
ORACLE_PASS RefProject binds aggregate=1, ordinal=len(log), tail=last event digest
ORACLE_PASS trace bridge rejects corrupted observed digest/projection at first index
NOTE: bounded OBSERVED-consistency check, not a machine-checked refinement (see README).

$ python -X utf8 -B experiments/v3/fu-03-kernel-session-a/model/check_model.py
MODEL_PASS RBig baseline recorded (witness); RFixed clean; M25=KILLED M31=NOT_KILLED_WITHIN_BOUND; 10 killed; all 36 registry ids dispositioned

$ python -X utf8 -B tools/check_public_scope.py
PASS: no other-project identifiers found in repository text files

$ # full re-derivation in an isolated copy (model files + verified jar only, C:\...\fu03a-rederive\model)
$ java -Xmx4g -cp <verified-jar> tlc2.TLC -config RBig.cfg -cleanup RBig.tla
Error: Invariant NoBlindEffectReplay is violated.   (matches recorded witness)
$ java ... tlc2.TLC -config RFixed.cfg -cleanup RFixed.tla
Model checking completed. No error has been found.  (1,552,824 states generated at progress-11; final 2015484/1207202/0)
$ java ... tlc2.TLC -config RMut_M25.cfg -cleanup RMut_M25.tla
Error: Invariant NoBlindEffectReplay is violated.   (172276 states generated, 33043 distinct — matches mutants.json receipt)

$ # gate-honesty probe in a copy (C:\...\fu03a-gateprobe\...): M25 disposition -> NOT_YET_IMPLEMENTED
$ python -X utf8 -B <probe-copy>/model/check_model.py
MODEL_PASS RBig baseline recorded (witness); RFixed clean; M25=NOT_YET_IMPLEMENTED M31=NOT_KILLED_WITHIN_BOUND; 9 killed; all 36 registry ids dispositioned   (exit 0)
$ python -X utf8 -B <probe-copy>/check_session_a.py
SESSION_A_FAIL: M25 must be KILLED by the reconciled model   (exit 1)
```

## Per-check disposition

| Check | PASS / FAIL / NEEDS-EVIDENCE | Note |
|---|---|---|
| 36-row registry, each dispositioned | PASS | mutants-registry.json: 36 rows, ids exactly M01..M36, every row carries a disposition (26 NOT_YET_IMPLEMENTED / 7 INSTANTIABLE / 3 NEEDS_LARGER_BOUND). mutants.json receipts cover all 36 ids (10 KILLED / 24 NOT_YET_IMPLEMENTED / 1 NEEDS_LARGER_BOUND / 1 NOT_KILLED_WITHIN_BOUND). |
| Witness is `NoBlindEffectReplay` | PASS | baseline-witness.json violated_invariant == NoBlindEffectReplay; stored RBig.out line 17 confirms; independently re-derived with the pinned jar in an isolated copy. |
| `RFixed` guard removes the witness | PASS | RBig FireTimerEffectOK == TRUE vs RFixed FireTimerEffectOK == eff.status in {"None","KnownNoEffect"} (RFixed.tla:51), conjoined at FireTimer (RFixed.tla:198) with the invariant at :307-308; RFixed.out clean ("No error has been found"); full TLC re-run clean; M25 (guard deleted) re-violates the same invariant. |
| Oracle independent of model/live reducer | PASS | AST import closure: refstate.py imports only __future__/dataclasses/hashlib/struct/typing; trace_checker.py adds json/pathlib/sys + refstate; check_oracle.py adds copy/json + refstate/trace_checker. No TLA/model/reducer/provider/network import or invocation found by grep. 51 vectors are hand-stated intent-level expectations (sampled admission id 20, log_reduction id 40); check_oracle.py's only generated fixture is the observed-digest trace bridge built from refstate itself, plus negative corruption controls. Residual: shared-specification error with ds-FU-03 is not excluded (acknowledged in oracle/README.md). |
| Gate-honesty probe (gate fails when result removed) | PASS with finding | check_session_a.py FAILS (exit 1) when M25 is perturbed — non-vacuous on the M25 axis. FINDING: check_model.py still exits 0 on the same perturbation (it only requires a non-empty M25/M31 disposition), so check_model.py alone is vacuous for the M25=KILLED property; the KILLED requirement lives in check_session_a.py. Recommend tightening check_model.py or documenting the split. |
| Symmetry assumption accepted/rejected | ACCEPT (bounded, documented) | CONSTRAINT CanonicalIds is declared in RBig.tla:56-62 / RFixed.tla:54-60 and applied in RBig.cfg:15 (RFixed.cfg likewise). Argument: CmdIds are consumed only via Fresh(id) receipt flags and counted only through order/log length, never compared across ids, so quotienting by order-of-first-use selects one representative per orbit. Accepted as a documented assumption for this diagnostic bound, not as a proven symmetry theorem; any reuse at a new bound or with id-comparing guards must re-argue it. |
| `CORR/GOAL` fixture qualification spot-check | PASS | kernel.py:282-290 (_domain_record) hardcodes "correlation_id": "CORR-M1A" — confirmed at line 288. FIXTURE-QUALIFICATION.md's claim that stored packet events bind GOAL-M1A while carrying CORR-M1A, making those prefixes not whole-contract-valid, is consistent with the code read. F005 effect-mismatch mechanism (kernel.py:327 copying goal.payload.allowed_effect_keys) cited but not independently re-executed — relies on SG/SK citations as stated. |
| No claim upgraded to verified/qualified | PASS | No 36/36, kernel-freeze, or qualification claim found in Session A artifacts. Registry summary reports 7/3/26; mutants.json reports 10 killed; RECONCILIATION.md states "no checker run, no kill, not acceptance"; oracle README states "not acceptance ... not a kernel freeze". VERIFICATION.md:73 explicitly "not 36/36". |

## Residual unknowns

- Registry-level M25/M31 "justification in text": RECONCILIATION.md M25/M31 paragraphs describe why the registry entries do not match the battery analogues (split-fault / equivalent-within-bound analysis) rather than narrative kill justifications; the machine dispositions (M25=KILLED, M31=NOT_KILLED_WITHIN_BOUND with full TLC receipts) carry the weight. Read as PASS against the falsifiers (M25 is KILLED, M31 explicitly dispositioned), flagged so a stricter reader can demand prose.
- The TLC re-derivation ran on Windows (Temurin 21.0.12.1) with the pinned jar; fingerprints/state counts for RFixed matched the stored .out exactly (2015484/1207202/0).
- Same-family caveat: the implementer/repro family is recorded as deepseek; this verifier is Muse Spark (meta/muse-spark-1.3-contributor) — different family, satisfying the preference.
- Candidate files were not modified; the TLA+ jar lives only in the untracked Temp trees. Gate-probe and re-derivation copies are outside the repo and were not committed.

## Reviewer identity and decision

- Decision: ACCEPT (Session A diagnostic scope only; not 36/36, not a kernel freeze, not qualification — per the artifacts' own non-proofs)
- Rationale: all four gates pass on a fresh checkout at the pinned SHA with the hash-verified jar; the witness re-derives under TLC and the RFixed guard is shown to be what removes it (RFixed clean, M25-without-guard re-violates); oracle imports are stdlib-only with hand-stated vectors; the session gate is non-vacuous on the M25 axis; symmetry is documented and accepted as a bounded assumption; the CORR-M1A spot-check confirms the code; no over-claims found. One finding for the record: check_model.py alone does not enforce M25=KILLED (passes with M25 perturbed) — enforcement lives in check_session_a.py.

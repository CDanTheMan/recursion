# Stage B verification result

- Verifier model + version: Muse Spark (meta/muse-spark-1.3-contributor) via OpenCode session, 2026-10-02
- Session / operator: independent-verifier turn in the main workspace (read + fresh-clone evidence; no candidate files modified in the main tree)
- Date (YYYY-MM-DD): 2026-10-02
- Candidate repository + commit SHA: https://github.com/NotSkittlz/recursion @ d56cc441b0efa964ed8eb515626a1c836192ca69
- Fresh checkout? (yes): `git clone https://github.com/NotSkittlz/recursion.git` into `C:\Users\Lucas\AppData\Local\Temp\opencode\recursion-verify-b` + `git checkout d56cc44` (detached HEAD). All reruns below executed in that tree. Python 3.12.10.

## Commands run (raw outputs inline or attached)

```text
$ python -X utf8 -B experiments/v3/fu-03-stage-b/run/run_stage_b.py
STAGE_B_RUN fixtures=26 total=26
  blocked=2
  bounded_consistent=16
  divergent=0
  invalid=0
  out_of_scope=0
  unknown=3
  unsupported=5
STAGE_B_RUN positive_control=SB-05 disposition=bounded_consistent effects=1 receiver_mutations=1
STAGE_B_RUN negative_control=SB-07 disposition=bounded_consistent receiver_refusals=3 non_fresh_admissions=0
STAGE_B_RUN negative_control=SB-14 disposition=bounded_consistent receiver_refusals=0 non_fresh_admissions=3
STAGE_B_RUN trace_control=SB-03 verdict=VALID_BOUNDED
STAGE_B_RUN wrote experiments\v3\fu-03-stage-b\results\stage_b_results.json
NOTE: bounded synthetic evidence over one corpus; not exactly-once external effect, not provider trust, not IT-02 acceptance.

$ python -X utf8 -B experiments/v3/fu-03-stage-b/run/check_stage_b_run.py
STAGE_B_RUN_GATE_PASS fixtures=26 bounded_consistent=16 unknown=3 unsupported=5 blocked=2 divergent=0 invalid=0 out_of_scope=0
STAGE_B_RUN_GATE_PASS every pass-equivalent fixture has both an oracle expectation and an independent observation
STAGE_B_RUN_GATE_PASS positive control produced one effect; negative controls rejected stale/duplicate work; conservation holds
STAGE_B_RUN_GATE_PASS vacuity probes rejected (4 probes)
NOTE: a simulated receiver is NOT qualification of an external service, native process containment or real automatic takeover.

$ python -X utf8 -B experiments/v3/fu-03-stage-b/check_stage_b.py
STAGE_B_DESIGN_PASS fixtures=26 refs_covered=36 unexecuted=26 cut_points=6 fence_states=3 stop_modes=3
NOTE: design-only matrix; no fixture executed and no Stage B result claimed.

$ python -X utf8 -B tools/check_public_scope.py
PASS: no other-project identifiers found in repository text files

$ # Session A snapshot acceptance (VERIFICATION.md prerequisite)
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
```

## Per-check disposition

| Check | PASS / FAIL / NEEDS-EVIDENCE | Note |
|---|---|---|
| Oracle = expectation side; observers = observation side (not reversed) | PASS | `run_stage_b.py:compute_expectation` calls `refstate`/`trace_checker` only over the committed log; checks compare that expectation against `scenario.observation()`. `harness.py` uses the oracle only as a canonical log writer (`command_from_spec`/`admit`); observation ledgers come from separate `observers.py` folds. No expectation is derived from the candidate under test. |
| `run/observers.py` does not import the oracle | PASS | `observers.py` imports stdlib `dataclasses`/`typing` only. Text search finds `refstate`/`trace_checker` only inside the docstring independence statement ("does **not** import, call or consult"). Module imports cleanly and exposes no oracle symbols. |
| Non-passes (unsupported/unknown/blocked) genuinely unresolved | PASS | All 10 verified in code: SB-09/SB-11/SB-12 `supported=False` with preserved unknown reasons (prior-exposure pending, unreachable member unresolved+liability held, Lazy deadline without boundary/quiescence); SB-15/SB-20/SB-24/SB-25/SB-26 `supported=False` with zero checks and explicit missing-observer reasons; SB-21/SB-22 `run=None`, zero observers, blocked on native reset/store and real process launch. `classify()` short-circuits on `supported=False`, so their checks cannot promote them; the gate additionally rejects any `bounded_consistent` row marked unsupported. |
| Positive control: exactly one effect | PASS | SB-05: oracle `effect_count=1` (ES_UNKNOWN then reconciled ES_SUCCEEDED), independent receiver `accepted_total=1` / `receiver_mutations=1`, resources `settled=4/outstanding=0`, all 6 checks pass two-sided (`single-effect-both-sides`, `settled-once`). |
| Negative controls: stale/duplicate rejected | PASS | SB-07: stale epoch-7 refused + rogue-issuer refused (3 receiver refusals), floor 8 monotonic across restart, `one-post-install-effect`; SB-14: duplicate-identical `cached`, changed-bytes `COMMAND_CONFLICT` (code 5), stale lease `LEASE_EPOCH_STALE` (code 10), 3 non-fresh admissions, durable ordinal unmoved. SB-03 trace bridge: retained prefix `VALID_BOUNDED`, corrupt duplicate append `INVALID_TRACE`. |
| Conservation (settled / outstanding / withheld) holds | PASS | Verified over all 19 fixtures carrying a resource ledger: `conserved`, `disjoint`, `uncertain_annotated_once` all true and `total <= gross`. SB-17 pins `total_before == total_after` across `recover_withheld(5)`; SB-16/SB-23 keep crash-zeroed reports raw (validated null) with held liability; 19 >= gate minimum of 8. |
| Gate vacuity probes rejected | PASS | All 4 in-gate probes plus manual reproduction in the fresh tree: observation-strip -> `SB-05: bounded_consistent without an independent observation`; check-flip -> `bounded_consistent with failing checks ['valid-bounded']`; negative-zero -> both negative controls `rejected nothing`; unbacked-pass -> `SB-09: bounded_consistent without an oracle expectation` (+ unsupported + counts disagree). Gate fails on each mutation as required. |
| Non-proofs preserved (no qualification claims) | PASS | Scope note carries `not qualification`; README stop/non-proofs list timeout-as-quiescence, cancel-as-rollback, missing-counter-as-release, and simulated-receiver-as-qualification prohibitions; runner/gate/README repeat "not exactly-once external effect, not provider trust, not IT-02 acceptance". No IT-02 acceptance, qualification, or 26/26 safety claim found. Only negation-adjacent matches for the over-claim scan. |

## Residual unknowns

- Rerun rewrites only the `candidate_commit` stamp in `results/stage_b_results.json` (`e21cd75...` -> `d56cc44...`); every other byte is identical to the committed results, so the run is deterministic and the stamp is a recorder artifact, not a result change. The fresh-tree working copy was left dirty by the rerun; the main-tree result file here records verification, not a new run.
- Session A acceptance was re-executed (not re-reviewed) as the snapshot prerequisite: all three Session A gates pass in the same fresh tree at d56cc44. The prior independent Session A ACCEPT (`74fb18d-muse-spark-1-3.md`, different-model-family session) is cited, not re-derived.
- Same-model-family note: this verification ran under Muse Spark, matching the earlier Session A independent verification family; the Stage B handoff asks for a different family from the Stage B implementer. Implementer family for PR #150 was not established here, so this is recorded as a residual rather than a pass/fail input.

## Reviewer identity and decision

- Decision: ACCEPT
- Rationale: all four named commands pass verbatim on a fresh clone at d56cc44 with the expected counts (16/5/3/2/0); comparison direction is oracle-expectation vs independent-observation with no oracle import in the observers; all 10 non-passes are structurally blocked from promotion with preserved reasons; positive/negative/trace controls and conservation verified field-by-field; all four vacuity mutations manually reproduced and rejected by the gate; non-proofs intact with no over-claims. Bounded synthetic scope only; not IT-02 acceptance.

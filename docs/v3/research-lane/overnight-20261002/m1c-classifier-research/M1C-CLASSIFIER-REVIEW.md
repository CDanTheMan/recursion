# M1C pure-classifier semantic review

Source snapshot: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
Review date: 2026-10-02  
Method: static text/data/hash inspection only; **no target module import, target execution, tests, model checking, live host/provider action, installation or repository modification**. Predictions below remain unexecuted.

## Result

**No new source-grounded mandatory classifier defect established.** The visible extended-schema/evaluator/test path substantially supports the five frozen lanes. There is one small, local semantic-witness gap worth strengthening: explicit evidence-relation outcomes, particularly qualification retention through refusal. This is a test addition proposal, not a failing result or repository-wide coverage claim.

Two important negative findings prevent false positives:

1. Missing checks in a single evaluator are often enforced by the extended input validator. Plain Draft 2020-12 validation without the registered `x-*` handlers is not this implementation's complete gate.
2. Historical settlement deliberately need not mean a runtime effect is safe to repeat or a reservation can be released. The later effect-evidence experiment explicitly preserves M1C success for `later-start-only` and adds a separate unsettled-attempt hold. Reporting that behavior as newly discovered stale-success would ignore existing evidence.

## Exact scope and evidence discipline

`CONTROL_PLANE.md` establishes authority/evidence precedence; `ANCHOR.md` requires a deterministic core without promoting research into platform fit. M1C consumes M1A/M1B identities as opaque immutable bindings and classifies supplied evidence; it does not resolve sources, authenticate real issuers, replay an actual store, publish Git, or inspect deletion media (`docs/v3/M1C-INTEGRITY-CONTRACTS.md:9–30,168–175`). The construction boundary admits documents, strict schemas, sanitized literals and test-only oracles, not operational writes (`docs/v3/M1C-CONSTRUCTION-CAMPAIGN.md:9–76`).

Consequently an asserted verified receipt, supplied backup proof, synthetic digest equality, supplied protected-branch list or declared complete writer inventory is an input premise. Showing that such a premise can be asserted by a JSON author is not an M1C bypass. The relevant defect would be failure to enforce a mandatory relationship *within* those admitted inputs.

The source snapshot is an exported tree, not a Git checkout. Its recorded commit metadata names the commit above. Source-byte pins accompany this report. No new ancestry, clean-worktree, materialization or test-pass claim is made. The campaign's terminal receipt concerns historical candidate `8cd1c8ef574b0e375000d7c68d133404928308cf` and explicitly acknowledges same-family synthetic evidence (`docs/v3/M1C-CONSTRUCTION-CAMPAIGN.md:243–278`).

## Complete visible call path

- `schema.test.py:66–86` strictly decodes original fixture bytes; `M1CValidator` registers semantic extensions and `validate` applies the chosen definition (`scripts/tests/v3/integrity/schema.test.py:533–560`). Shapes, tagged unions, nonempty requirements and self-digests come from `schemas/control-plane/v3/integrity/materialize.py` and committed `schema.json`.
- `fixture.test.py:49–98` validates all bundles and the manifest, binds schema and fixture raw bytes, and compares fixture-materializer outputs. The materializer must not call the reference oracle. This gives a separately stated expected corpus, not proof that all semantics have independent authorship.
- `reference_oracle.py:904–912` dispatches typed bundles to pure evaluators. Its public precondition is schema-valid input (`:2–6`); it is not an independent hostile-input decoder.
- `conformance.test.py:37–63` compares 24 literal outputs twice and validates closed decisions. It does not itself revalidate every input; the complete campaign includes the separate fixture gate. This is a test pipeline, not a single production validation API.
- Adversarial tests mix schema-valid semantic cases with intentionally malformed direct-evaluator diagnostics. The latter establish a narrower defensive property, not a substitute for validation.
- The later adapter visibly composes strict canonical-byte decoding → extended `EffectTraceInput` validation → unchanged classifier → strict output decoding → `EffectDecision` validation (`experiments/v3/effect-evidence/ee_common.py:27–33`). Its outer signed join is distinct from M1C.

## Guard and witness map

Detailed machine-readable rows are in `semantic-matrix.json`.

### Evidence

Required sources must exist; every edge resolves the one claim and a source; extra sources must be referenced. Sorted keyed arrays prevent dictionary-overwrite identity aliases (`schema.test.py:214–231`; materializer `:159–204`). Source identity, lifecycle, access, editorial state, claim/source expiry, retrieval chronology, scope, license, privacy and export constraints are independently considered. Edge source-version/extraction/applicability checks precede accepted relation classification (`reference_oracle.py:60–183`).

Precedence is refusal → support plus contradiction = contested → support = supported → unknown with insufficient support. Refusal clears accepted support while retaining otherwise admissible contradiction/qualification sets (`:185–216`). “Required sources” denotes an inventory requirement; the output contract explicitly uses existential admissible support, not unanimous support from every required source (`M1C-WIRE-PROFILE.md:82–101`). An expired extra source alongside valid support is not automatically a false green.

Existing witnesses: F-001–005, stale/inapplicable/extraction negatives, mismatching persistent ID next to a verified ID, unknown-license admission, claim expiry/future retrieval, cross-version refusal and contradiction retention (`adversarial.test.py:222–300`). The 79-variant matrix validates output shape, not a separately enumerated expected result for each variant (`:121–220`). That is correctly described as output-variant coverage; do not inflate it into 79 independent semantic oracles.

### Effects

Self-digested intent and exact admission joins include effect, actor, lease, epochs and GoalSpec/policy/grant/privacy/route/budget digests. Plan and GoalSpec ID are carried in the sealed intent; M1C does not possess the original planning records to recompute those cross-layer relationships. Starts are contiguous and uniquely owned; observations bind preceding canonical starts; timestamps are nondecreasing and respect admission/deadline constraints (`schema.test.py:264–369`).

The classifier preserves pending possible effects per attempt, refuses dependencies lacking supplied success, retains blind retries/conflicting results, and checks known observer/result/remote-operation agreement (`reference_oracle.py:227–499`). Precedence is unresolved/conflicting trace → ambiguous; otherwise settlement disagreement → ambiguous; then exact reconciliation → exact receipt → verified rejection → hard refusal → executing/prepared. Exact historical settlement retains admission violations (`:480–538`). Tests cover later receipts failing to erase prior uncertainty, ownerless observations, duplicate-number aliases, observer/result conflicts, refused admission with exact success, and temporal violations (`adversarial.test.py:301–472`).

**Existing later witness:** `ee_cases.py:6–18,58–62` states and constructs `later-start-only`; `ee_experiment.py:7–21` asserts the historical/current statuses, exact reason sets and separate pending-attempt hold. `ee_join.py:116–135` returns `runtime_permission=False`, `production_authentication=False`, and the hold. The specification explicitly calls this a preregistered refinement (`docs/v3/construction/effect-evidence-20260908/specification.md`, “Construction-stage preregistration refinement”). No new bug is asserted here.

### Publication: candidate/source/schema binding

Extended schema requires exact artifact, gate and verifier inventories, joins every gate/verifier's source and candidate SHA, joins the receipt's publication/effect/repository/ref/candidate fields and rejects post-receipt preflight (`schema.test.py:371–396`). The evaluator repeats relevant joins, checks the review branch itself against supplied protected names, distinguishes target branch, and enforces kind, ancestry, cleanliness, authority, artifact export/license/scan and verifier independence policy (`reference_oracle.py:542–641`).

The manifest binds the literal corpus to the exact schema bytes (`fixture.test.py:77–85`). A publication gate has source/candidate SHA and evidence digest, **not** a schema-digest field (`M1C-WIRE-PROFILE.md:180–211`). Demanding a new gate-to-schema or gate-to-real-source-service join would change the frozen profile. The artifact set is exact by ID; content/evidence/tree digests are supplied facts, not recomputed repository contents.

Exact observed/rejected receipt outranks preflight failure; unknown remote state is ambiguous; remaining faults block; fault-free no-receipt input is eligible (`reference_oracle.py:643–660`). F-011–015 and adversarial exact-publication/rejection, protected-ref, candidate/gate/verifier/receipt and preflight-time tests cover these distinctions (`adversarial.test.py:473–560`).

### State/replay

Exact expected/observed writer sets, canonical membership, current configured fence/source revision, refusal proofs, event aggregate/sequence/chain/authentication, monotonic event fences/logical time and unique command/idempotency/event IDs are checked. Historical event epochs can legitimately precede current fence; the regression test explicitly preserves that (`reference_oracle.py:664–728`; `adversarial.test.py:611–641`).

Replay equality and projection equality are separate supplied digest comparisons. Lossless import, all four recovery proofs, ordered/full stage completion, closed work and known deployment remain additional conditions (`reference_oracle.py:730–766`). A proper incomplete stage prefix with matching projection earns `projection-only`; a mismatch already forces recovery. There is no visible reason-free incomplete-prefix path. Recovery-class reasons dominate ordinary blocked reasons (`:768–794`). F-016–020 and adversarial writer/duplicate/event/fence/time cases supply witnesses. Mutating the event's opaque `schema_version` while honestly resealing it does not test a missing supported-runtime-schema registry: the wire field is a Token, not a declared supported-version enum.

### Retention

Outer artifact/class/policy, sealed tombstone and exact copy inventories bind. Only verified deleted copies or reached expiry at/before disposal resolve; mismatch is blocking, unverified evidence incomplete. Tombstone request/disposal/completeness, local content, destroyed isolated key, legal hold, sensitive-content flags and protected receipt/audit erasure policy are checked (`reference_oracle.py:798–900`; `schema.test.py:451–499`). Blocking reasons dominate incomplete, which dominates complete. F-021–024 plus local-content-only, accepted-evidence-not-receipt, tombstone substitution/time, mismatch-copy and unreached-expiry cases already cover several tempting false positives (`adversarial.test.py:643–771`). `expiry_reached` is explicitly supplied, not a wall-clock truth claim (`M1C-FIXTURE-ORACLES.md:86–89`).

## Small future synthetic test package: evidence relations

**Disposition: local test-strengthening gap; implementation appears conforming.** The inspected literal constructors and semantic tests contain exact support and contradiction results but no nonempty qualification-output witness, nor a relation sweep asserting `replicates`, `updates` and `mentions`. This statement is limited to the inspected M1C suite, not every later repository experiment. Related output-shape invariants already exist; they do not force an evaluator to populate the right qualification set for a particular input.

The normative discriminator is `M1C-WIRE-PROFILE.md:93–100`: qualifying evidence does not supply support, but otherwise admissible qualification history survives refusal. The implementation visibly does this at `reference_oracle.py:178–206`. A conforming rival interpretation is simply that the existing finite corpus did not aim for relation-complete semantic witnesses. That interpretation is consistent with a passing bounded campaign; this proposal does not reopen its historical acceptance.

`future-synthetic-vectors.json` contains **unexecuted**, complete typed inputs and hand-stated expected decisions:

- R0: unmodified one-source/one-edge F-001 input control, supported.
- R1–R4: change only its relation to `replicates`, `updates`, `mentions`, `qualifies`. First two remain supported; mentions becomes unknown/insufficient; qualifies becomes unknown/insufficient with the exact qualification edge and reason.
- R5: F-004 input with its contradiction edge changed to qualifies. This is a two-source support-plus-qualification control, supported with retained qualification.
- R6: R5 with only the supporting source privacy changed to internal while allowed classes remain public. Expected refused/privacy-prohibited, accepted support cleared, qualification retained. Both source inventories and edge bindings still resolve.

Shortest structural prerequisite is one source and one edge for R0–R4; R5–R6 need independent eligible qualification evidence and refused supporting evidence, so use the existing two-source two-edge input. Preserve all non-null verified source/identifier/retrieval fields, source versions, exact extraction flags, original in-scope `observed_at`, sorted unique arrays, closed types and IDs. These objects contain no changed self-digest. **Do not move observation time to the review date:** the fixtures' October 1 freshness boundary would then confound every outcome. Test the typed input, not a bundle retaining its old literal expected value or frozen manifest.

A future authorized execution must strict-decode canonical inputs, validate `EvidenceAssessmentInput`, classify, validate `EvidenceDecision`, and compare exact canonical expected output; record schema rejection separately from semantic disagreement. A discriminating evaluator mutant that drops the `qualifies` branch could emit schema-valid unknown/support results with empty qualification sets and still evade merely validating output shape. R4–R6 should kill that mutant. This proposed mutation test has **not run** and is not evidence of current failure.

## Nonproof and stopping condition

Static predictions plus historical receipts are insufficient for a new PASS. No live source truth, real issuer authenticity, distributed completeness, migration, durability, deletion or platform guarantee is inferred. Later cut-publication/source and replay-store experiments are separate bounded mechanisms: their existence prevents repository-wide absence claims, but cannot be silently imported as stronger M1C proof. The bounded audit is complete when this guard map, existing-counterexample dispositions, explicit local test proposal and byte pins are delivered; further target execution requires a separately authorized task.

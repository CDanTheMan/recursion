# FU-03 — formal model and byte conformance (synthesis)

## Provenance

This synthesis summarizes the raw report `raw/ds-FU-03-formal-model-vectors.md` (its own title:
"Formal model and byte conformance specification"). The work is specification only: no checker,
reducer, benchmark, target runtime, effect, crash fixture or implementation was run, no mutant
was killed, no binary corpus was generated and no checker or container digest was measured. It is
labeled candidate specification CAND RCV1 20261001, with an evidence cutoff of 1 October 2026. The report's sources are public primary sources — immutable
release/commit references mixed with mutable specification and tool documentation, RFCs, FIPS
180-4 and an RFC erratum — read around 1–2 October 2026 UTC; this synthesis refers to them only
as "the report's sources" and invents no URLs. All numbered requirements are proposed until
reconciliation and independent validation, and all run, kill, equivalence and byte-parity
outcomes are unverified.

## The question

What finite formal model, mutant corpus and deterministic byte-conformance format must exist
before the runtime experiment (FU-01) may rank anything, and what exact evidence would show a
candidate implementation conforms? The report proposes finite bounds, seventeen invariants with
independent monitors, thirty-six candidate mutations with a classification metric, a
language-neutral byte-vector container and profile, typed digest domains, a stable refusal
taxonomy and a two-independent-implementation gate. A secondary question is how the formal and byte layers relate to already-frozen wire contracts and to downstream consumers.

## Key findings

### Fixed finite model bounds

The handoff fixes the bounds, seventeen invariant names, TLA+/TLC as primary, Alloy 6.2.0 as the
independent cross-check and the 36-of-36 mutant threshold. The candidate completes the missing
formulas: one each of Aggregates, Tasks, Effects, Timers and Verifiers; workers `{1,2}`;
GoalEpochs and PlanRevisions `{1,2}`; LeaseEpochs `{1,2,3}` with no wraparound; Attempts `{1,2}`
plus a `0` not-started sentinel; PauseEpochs `{0,1}`; QueueCapacity and MaxCommittedEvents `2`
and `20`; CommandIds `1..20`; WriterEpochs `{1,2}` as a candidate adapter dimension; Principals
`{H,W1,W2,X}`, where `H` is a synthetic authorized control principal and `X` unauthorized. The
first authoritative safety run disables symmetry, view reduction and state constraints. The
modules run from `RTypes` through `RMutants`; `RReference` is an immutable oracle that may not
import the target paths, and a mutant edits exactly one named site, never a monitor. `Integrated`
adds pending admission, delivery, crash and independent monitors, and its mapping to the abstract
committed boundary is a stated obligation, not a proved theorem; a reduced debugging bound has
its own configuration identity and cannot satisfy the integrated gate.

### The mutant corpus and acceptance metric

The report proposes thirty-six exact fault sites (M01–M36), each `PENDING` with no receipt. The
single-disposition vocabulary is `KILLED`, `SURVIVED_REACHABLE_NONEQUIVALENT`,
`EQUIVALENT_WITHIN_BOUND`, `UNREACHABLE_WITHIN_BOUND` and `INCONCLUSIVE`; a syntax error,
timeout, exception, missing field or aborted run is `INCONCLUSIVE`, never a kill. Acceptance is
36 of 36 rows classified with retained evidence and additionally requires `K = RNE` (killed
equals reachable-and-non-equivalent) with no survivor and no inconclusive row; equivalent or
unreachable rows count to the denominator only, never the kill numerator. M21 is flagged as
potentially over-guarded and M35 as a modeling seam that may be equivalent within the bound; a
local agent may not weaken unrelated guards to manufacture a kill. A kill receipt is a canonical
record (mutant id, source digests, one semantic diff, checker/runtime/container digests,
invariant id, first divergence, baseline prefix, full and minimized counterexamples, guard
exposure, reviewer decision) with no nullable artifact identity in an accepted receipt.

### Deterministic byte-vector and conformance format

Candidate `RCV1` is test interchange only — never a broker protocol, storage log format or
product default. Its frame is 4-byte ASCII magic, 2-byte big-endian version, 2-byte flags, 4-byte
big-endian payload length, exactly one deterministic CBOR map and a trailing 32-byte SHA-256;
frame errors are separate from the eighteen kernel refusal codes. The deterministic CBOR profile
permits unsigned/negative integers, byte strings, valid UTF-8 text, arrays, unsigned-integer-key
maps, booleans and null — no floats, tags, indefinite lengths or duplicate keys — with shortest
heads, exact end of item and no Unicode normalization. Logical schemas and typed digest preimages
`D(t,e,x)` use domain strings `state, event, packet, command, projection, effecttoken, manifest`;
the symbolic injective `DigestOf` is deliberately stronger than SHA-256. JCS stays separate with
a baseline canonicalizer profile and a defensive input profile keyed to the verified negative-zero
erratum. The refusal taxonomy allocates codes 0–17 with a fixed detail enum and explicit
tie-breakers, and the minimum catalog is 88 named rows plus finite mandatory expansions whose
literal bytes must be independently reviewed, not left as `Fresh`/`D` expressions.

### Two independent implementations are required

Acceptance is exact: implementation A's bytes and structured result equal B's, which equal the
reviewed normative vector, for every required vector and expansion — equal digests without
retained bytes are insufficient, and both stacks must also produce independently valid trace
receipts. A and B share only the written contract, literal corpus and approved type definitions;
they share no serializer, decoder registry, reducer, generated source, code-generator template or
expected-output generator. A standard SHA-256 primitive may be shared only if disclosed with
independently sourced known-answer tests; different languages alone do not establish
independence, and two wrappers around the same library fail. This gate applies equally to native
execution and wrapper/orchestrator adapters, whose success events are input evidence, not authority.

### Epoch discipline: frozen M1 contracts are not retrofitted

Codes never change meaning within schema epoch 1, and a new refusal needs a new code/epoch
policy. A byte-format, digest-domain or refusal change requires a distinct schema/profile epoch,
and cross-profile digests are not equal merely because logical meaning agrees. The candidate
`RCV1`/CBOR/JCS/digest definitions must not be retrofitted into already-frozen M1 wire contracts;
the report proposes a candidate epoch rather than editing an accepted one. The report's sources
are pinned as references, not immutable content digests, so local agents must archive and hash
the documents they rely on.

## Recommendation and falsifier

Keep TLA+/TLC primary at the fixed integrated bounds; keep independent history, replay and
projection monitors rather than reusing the reducer or projector; use candidate RCV1 framing with
strict deterministic CBOR; require typed digest domains and exact preimages; keep receipt reuse
separate from fresh dispatch; classify every mutant and kill every reachable non-equivalent one;
require two genuinely independent stacks; use bounded trace validation before FU-01/FU-02
admission; keep Alloy independent and scope-aligned; and hold adoption until local receipts and
independent review exist. Two TLC falsifiers apply: F1, semantic sensitivity — failure to
distinguish a known reachable non-equivalent mutation with the independent monitor under matched
scope; and F2, adequacy at the agreed bound — failure to reach and retain the row-53 lease-3,
PAUSE and effect witness or to finish the authoritative exploration within the predeclared
resource envelope. Reducing lease epochs, removing effect uncertainty or pruning the exposing
transition cannot turn F2 into acceptance. An unresolved Alloy disagreement, or two stacks that
agree with each other but contradict the normative bytes, is also decisive; correct rejection is
not success.

## Local execution handoff

Twelve tasks remain for local sessions: L01 reconcile the original DS22 definitions against the
candidate field by field; L02 transcribe the modules and configs with no hidden defaults or
missing actions; L03 pin official TLC/Alloy/JDK artifacts and populate the `RunManifest`; L04
validate baseline and vacuity controls including the row-53 witness; L05 run all thirty-six
mutations with exposure/NE/equivalence/unreachability proofs and retained receipts; L06 run the
independent Alloy cases with aligned scope; L07 materialize the literal corpus and manifest; L08
implement A and B independently against the released corpus; L09 validate the trace checker with
adversarial controls; L10 admit FU-01/FU-02 only against accepted artifacts; L11 obtain
independent review; L12 take an explicit Owner decision. The returned bundle carries the accepted
revision, all hashes, baseline and reachability witnesses, the classification ledger, Alloy
results, the literal corpus and coverage matrix, A/B attestations, trace-validator controls,
consumer acknowledgments, unresolved seams and the review disposition. No duration or measured
result is promised, and dependent work stops on a failed safety gate or missing authorization.

## What this does not prove

No checker, reducer, benchmark, target runtime, effect, crash fixture or implementation was run,
so there is no PASS. Finite model checking does not establish an unbounded implementation proof;
an injective symbolic digest is stronger than SHA-256; a finite trace witness is weaker than a
machine-checked refinement; and passing known-answer tests is not a collision-resistance proof.
Independently authored monitors can still share a mistaken requirement. The report does not prove
external effect truth, OS containment, storage durability or compiler correctness, and it selects
no production language, store, broker transport, renderer, availability contract or kernel freeze.

## Open Owner decisions

Reconciliation of candidate details with the historical DS22 registry (invariant formulas, the
thirty-six mutation sites, the six authority dimensions, the refusal 0–17 allocation and the API
schemas); whether the intended requirement is 36 classified rows or 36 reachable non-equivalent
mutants; the TLC resource envelope and stopping policy; exact pinned artifact identity; whether
the secure broker-admission profile or the baseline canonicalizer governs negative-zero input;
whether JCS becomes the accepted semantic byte profile, which would then need a differently named
digest profile and its own vectors; and whether to substitute or extend the named Alloy
cross-check. The final L12 decision on API freeze and any implementation, runtime, store or
broker adoption is reserved to the Owner.

## Relevance to later waves

FU-03 is a prerequisite for FU-01: the runtime experiment consumes the accepted byte corpus,
refusal vocabulary, event-identity vocabulary and trace-validity contract, and FU-01 must not
begin resource ranking while the corpus-release gate is open. FU-02 may use the semantic event
identity and uncertainty oracle for specification now, but its executable persistence comparison
must pin the same accepted schema and literal corpus. FU-05 consumes the corpus and digest
vocabulary as test interchange only. Later waves may prepare transcriptions, fixtures and
independent stacks, but must not claim a frozen API, corrected bytes or a qualified runtime until
the L01–L11 receipts and independent acceptance exist.

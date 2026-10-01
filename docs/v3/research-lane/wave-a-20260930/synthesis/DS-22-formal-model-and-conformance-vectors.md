# DS-22 — formal model and conformance vectors (synthesis)

## Provenance

- Raw report: `raw/ds-2-DS-22-formal-model.md`; answers
  `docs/v3/prompts/research-suite-20260929/DS-22-formal-model-and-conformance-vectors.md`.
- Session: Wave A Deep Research (self-contained handoff); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun. The
  report ran no model checker and wrote no code.
- Sources: TLA+/Lamport materials, the Alloy specification, the SPIN reference, Lean/Rocq documentation, RFC 8949, FIPS 180-4, QuickCheck.

## The question

Should the privileged deterministic kernel — four pure functions (`decode`, `admit`, `reduce`,
`derive_work_packet`) — be frozen? DS-22 blocks that freeze on three items: a finite transition
model, a guard-mutant corpus, and language-neutral byte-level conformance vectors. The report
treats the three as one combined design and selects no construction language, storage engine,
broker transport, or renderer.

## Key findings

- **Method choice.** Hand-written **TLA+ with TLC is the recommended primary finite falsification
  model**; PlusCal is allowed only for isolated explanatory algorithms, never as the normative
  source, so its control-flow encoding cannot dictate the abstraction. TLA exposes state predicates,
  refinement, and named weak/strong fairness at action granularity.
- **Competitors.** **Alloy 6.2.0** is the named secondary, independent structural cross-check for
  the authority lattice, bounded traces, and selected guard mutants; bounded non-discovery is not
  proof beyond scope. **SPIN/Promela** is a credible competitor with natural concurrency and LTL,
  but its process-centric idiom fits a four-pure-function contract less directly. **Lean/Rocq** are
  stronger for unbounded refinement, but are not the best first race instrument.
- **First integrated finite bounds.** One aggregate, one task, one effect, one timer, one verifier,
  two workers, two goal epochs, two plan revisions, three lease epochs, two attempts, two pause
  epochs, queues of capacity two, and a committed event log of at most twenty events. Three lease
  epochs expose the A→B→A identity-reuse (ABA-style) case beyond the two-epoch stale-writer race.
  The twenty-event cap is a conservative exploration cap, **not a proven minimum**.
- **Abstract digest assumption.** Digest-valued objects are modeled by an injective symbolic
  `DigestOf(value)` over the finite domain — explicitly stronger than real hashing, and therefore
  an explicit assumption that hides hash collisions. Concrete vectors must exercise actual bytes.
- **Seventeen invariants.** The handoff's named contract: `TypeOK`, `ChainIntegrity`,
  `AtomicAppend`, `CommandIdempotence`, `AuthorityScope`, `LeaseFence`, `AmendmentFence`,
  `PauseSafety`, `RetrySafety`, `CancelNoResurrection`, `EffectSafety`, `VerifierSafety`,
  `ReplayDeterminism`, `ReplayFailClosed`, `ProjectionParity`, `FlowBound`, `NoBlindEffectReplay`.
  Most are unary safety predicates; `ReplayDeterminism` and `ProjectionParity` need visible
  independent replay/projection monitor state, or the model risks proving a reducer against itself.
- **Mutation corpus.** Thirty-six instantiated mutants spanning deletion, weakening, reordering,
  and field-hiding (e.g. `ATOMIC_SPLIT`, `LEASE_EPOCH_WEAKEN`, `AUTH_DIM_DELETE[field]` ×6,
  `PAUSE_REORDER`, `VERIFIER_SELF_ALLOW`, `FLOW_OFF_BY_ONE`). A baseline pass is not coverage. The
  **acceptance metric is 36/36 mandatory instances classified**: every reachable non-equivalent
  mutant killed by a minimized receipt, equivalent/unreachable ones justified separately.
- **Fairness scope.** Safety invariants assume no fairness. Fairness is used only for named
  liveness calibration (e.g. `WF(ApplyPendingStop)` when pending stop is continuously enabled).
  Owner action, provider response, network recovery, external reconciliation, and logical-time
  advance receive no unconditional fairness.
- **Vector format.** A framed binary record (`RCV1` magic, major/minor version, uint32 big-endian
  payload length, deterministic-CBOR payload, trailing SHA-256) with a DS-22 RFC 8949 profile:
  integers, byte strings, permitted ASCII, arrays, maps, booleans, null; no floats, no tags, no
  indefinite lengths; shortest encodings; no duplicate keys; unsigned integer map keys. It is a
  **test interchange format, not a production wire format**. Digests are domain-separated
  (`recursion-state-v1`, `recursion-event-v1`, `recursion-packet-v1`, `recursion-command-v1`) over SHA-256 per FIPS 180-4.
- **Refusals and differential testing.** Refusals are structured `(code, structured_detail)`
  values, not diagnostic strings, with a stable 0–17 taxonomy (`MALFORMED` … `CHAIN_MISMATCH`). The
  minimum differential rule is two independently implemented stacks sharing no serializer, decoder
  registry, reducer implementation, or generated source; success requires implementation A
  bytes/result == implementation B bytes/result == the normative vector.

## Recommendation and falsifier

- Adopt TLA+/TLC as the primary finite falsifier, pinning an immutable checker artifact; keep Alloy
  as the named independent competitor for selected structural and small-trace cross-checks.
- **Conditional freeze:** do **not** freeze the privileged kernel API beyond the four closed
  functions until the TLA+ model exists, all mandatory reachable mutants have retained
  counterexamples, the byte-level vector corpus exists, and at least two independently written
  implementations reproduce every normative vector bit-for-bit.
- **Decisive falsifier:** reject TLA+/TLC as the primary instrument if a mandatory reachable mutant
  has a concrete witness under the agreed abstract semantics, an independent Alloy/SPIN encoding
  finds that witness at equivalent bounds, but the pinned TLC model cannot expose the corresponding
  invariant violation after model errors and reachability are ruled out. A second falsifier is
  inability to reach the mandatory three-lease-epoch/PAUSE/effect integrated bound without deleting
  a safety-relevant dimension a secondary model can retain. A single TLC performance problem is not
  sufficient.

## What this does not prove

- A passing TLC run means only that **no violating state was found inside the modeled state space**
  under the exact constants, abstraction, transition relation, fairness assumptions, and checker
  version used. It does not show omitted dimensions are irrelevant, that the unbounded system is
  safe, or that any implementation refines the abstraction.
- The report labels every unproved seam: unbounded state space, digest abstraction, kernel
  implementation, storage adapter, broker delivery, OS containment, external-effect truth,
  fairness/liveness, projection parity, and the model checker itself.
- The report calls DS-22 **research-complete at the design level only, not completion-gate
  complete**: no model was run, no mutant was killed, and no implementation reproduced the proposed
  vectors. Those absences are blocking evidence, not zero failures.
- Prior calibration numbers (444,834 reachable states, 2,644,215 transitions, 22 rejected guard
  mutants, 32,500-component fairness families) are **locally reported, not independently
  reproduced**.

## Open Owner decisions

- Exact repeated command: return `DUPLICATE_COMMAND`, or replay the original accepted batch?
- Is immediate PAUSE formally the only operative policy, with `checkpoint`/`drain` only adversarial modes?
- Is "independent verifier" a distinct principal identity, or only a distinct verifier lease/role?
- Is the deterministic-CBOR/SHA-256 vector encoding acceptable as a test artifact?
- Is three-lease-epoch A→B→A coverage mandatory in the first integrated run, or an immediately
  following expansion of the two-epoch minimal model?
- Which authority dimensions are Owner-normative beyond owner/path/capability/privacy/route/budget?
- What immutable artifact identity is required for a model run — tool binary SHA-256, container
  digest, or both?
- Is a trace-validity checker sufficient model-to-code evidence before language comparison, or is a
  machine-checked refinement map required first?

## Relevance to later waves

- The smallest bridge from model to code is a **trace-validity checker plus the differential vector
  suite**; a machine-checked refinement map (Lean/Rocq/TLAPS) is stronger but not required before
  selecting a language.
- A frozen four-function boundary only gates later language/storage/broker evaluation; it does
  **not** imply refinement, platform security, broker, or external-effect evidence.
- The construction language, storage engine, broker transport, and renderer stay unresolved; the
  report supplies no evidence for choosing among them.

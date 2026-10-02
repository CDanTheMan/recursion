---
title: FU-03 — Formal model, guard mutants and byte-level conformance vectors
status: ready-for-explicit-invocation
last-updated: 2026-10-01
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# FU-03 — Formal model, guard mutants and byte-level conformance vectors

This is a follow-up to gap G-03 in [GAPS.md](../../research-lane/GAPS.md) and source lane DS-22 (Domain A).

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone harness and harness orchestrator; Hermes is a retired control plane and an optional upstream integration. Workers are
bounded executors. An implementer's own PASS is never acceptance; independent review is
required, and missing verification is never a pass. `CONTROL_PLANE.md` is the operative
constitution; a research session may propose amendments but must never edit it. No research
session performs implementation, provider/model/authentication/configuration changes,
spending, deployment, publication or merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula,
captures and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs,
pinned source, licenses, peer-reviewed work). Classify every consequential claim as
source-documented, locally observed, inferred or unverified; keep `unknown` distinct from
zero. Model consensus and vendor marketing are not evidence. Every recommendation needs a
competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never
secrets, credentials, personal data, private repository content, local paths, or
account/infrastructure identifiers.

### Lane context

- DS-22 returned a **conditional freeze**: do not freeze the four-function kernel (`decode`,
  `admit`, `reduce`, `derive_work_packet`) until a TLA+/TLC finite falsification model exists,
  all 36 mandatory reachable mutants are classified with retained counterexamples, a
  language-neutral byte-level vector corpus exists, and two independently implemented stacks
  reproduce every vector bit-for-bit. TLA+/TLC is primary, Alloy 6.2.0 the named independent
  cross-check.
- It fixed the first integrated finite bounds (one aggregate, one task, one effect, one timer,
  one verifier, two workers, two goal epochs, two plan revisions, three lease epochs, two
  attempts, two pause epochs, queues of capacity two, at most twenty committed events), the
  symbolic `DigestOf` abstraction (explicitly stronger than real hashing), the seventeen named
  invariants, and a framed binary vector record (`RCV1`, deterministic-CBOR payload, trailing
  SHA-256) as a **test interchange format, not a wire format**.
- It stated the acceptance metric: 36/36 mandatory mutants classified, every reachable
  non-equivalent mutant killed by a minimized receipt; a baseline pass is not coverage.
- It left everything as design-level only: no model was run, no mutant was killed, no
  implementation reproduced the vectors, and prior calibration counts are locally reported, not
  reproduced.
- This lane is a prerequisite for G-01: the language comparison needs the vectors, the refusal
  taxonomy and the trace-validity checker first. Keep the two deliverables compatible.

## Purpose

Produce the executable specification for the finite falsification model, the classified mutant
corpus, and the language-neutral byte-level vector corpus, plus the differential and
trace-validity rules that connect the model to an implementation, so the kernel freeze and the
language comparison become admissible. This is a specification lane: it does not run the model
checker, kill mutants, write an implementation or freeze the kernel.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Preserve the current Hermes constitution; propose amendments, never edit it. Public Deep
Research receives only public or synthetic briefs. **DO NOT select a construction language,
storage engine, broker transport or renderer, and DO NOT freeze the kernel API.** No model
checker, implementation or repository change is authorized. The deterministic-CBOR/SHA-256
record is a test interchange hypothesis, not a production wire format; do not collapse it with
the broker's length-prefixed JCS framing. Do not decide the open Owner questions recorded in
GAPS.md.

## Inputs to read

None. This handoff is self-contained; the prior lane's conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Model specification

1. What is the exact TLA+ module set for the four pure functions and the fixed integrated
   bounds, written so the next run of TLC is mechanical: constants, variables, the transition
   relation, the refinement structure, and which fairness assumptions apply where?
2. How are the seventeen invariants (`TypeOK`, `ChainIntegrity`, `AtomicAppend`,
   `CommandIdempotence`, `AuthorityScope`, `LeaseFence`, `AmendmentFence`, `PauseSafety`,
   `RetrySafety`, `CancelNoResurrection`, `EffectSafety`, `VerifierSafety`, `ReplayDeterminism`,
   `ReplayFailClosed`, `ProjectionParity`, `FlowBound`, `NoBlindEffectReplay`) expressed, and
   which need visible independent replay/projection monitor state to avoid proving a reducer
   against itself?
3. What are the explicit unproved seams (unbounded state space, digest abstraction, kernel
   implementation, storage adapter, broker delivery, OS containment, external-effect truth,
   fairness/liveness, projection parity, the model checker itself) and how is each kept visible
   rather than smoothed over?
4. What is the immutable model-run artifact identity (checker binary digest, container digest,
   or both), and what is the Alloy cross-check protocol for selected structural and small-trace
   cases?

### Mutant corpus

5. What is the exact instantiation of the 36 mutants across deletion, weakening, reordering and
   field-hiding (for example `ATOMIC_SPLIT`, `LEASE_EPOCH_WEAKEN`, the six
   `AUTH_DIM_DELETE[field]` cases, `PAUSE_REORDER`, `VERIFIER_SELF_ALLOW`, `FLOW_OFF_BY_ONE`),
   and what makes a mutant reachable, non-equivalent and mandatory?
6. What is the classification and receipt format for a killed mutant, and how are
   equivalent/unreachable mutants justified separately rather than counted as covered?

### Vector corpus and refusals

7. What is the exact framed binary record and its deterministic-CBOR profile (magic, version,
   big-endian length, permitted types, shortest encodings, no floats, no tags, no indefinite
   lengths, no duplicate keys, unsigned integer map keys, trailing SHA-256), and the
   domain-separated digest rules for state, event, packet and command?
8. What is the minimum complete vector corpus that covers canonical bytes, ordering, duplicate
   commands, lease/authority fencing, PAUSE/epoch races, effect safety and replay, and how is
   each vector expressed so it is language-neutral and independent of any implementation?
9. What is the stable refusal taxonomy (`MALFORMED` … `CHAIN_MISMATCH`, 0–17) as structured
   `(code, structured_detail)` values rather than diagnostic strings, and what does each vector
   assert about it?

### Model-to-code bridge and independent implementations

10. What is the trace-validity checker's contract between an implementation trace and the
    abstraction, and what does it prove and not prove compared with a machine-checked refinement
    map?
11. What is the differential rule (two independently implemented stacks sharing no serializer,
    decoder registry, reducer implementation or generated source; success requires A bytes/result
    == B bytes/result == the normative vector), and how are the two stacks kept genuinely
    independent in practice?
12. What is the decisive falsifier for TLA+/TLC as the primary instrument, and what is the
    second falsifier around reaching the mandatory three-lease-epoch/PAUSE/effect bound?

## Deliverable

A source-pinned report containing: the complete TLA+ specification (or its exact, runnable
module plan with every constant and transition fixed) with the invariant expressions and
fairness scope; the immutable model-run artifact identity and Alloy cross-check protocol; the
36-mutant corpus with reachability/equivalence criteria and a kill-receipt format; the framed
vector format, CBOR profile and domain-separated digest rules; the minimum complete vector
corpus and the refusal taxonomy; the trace-validity checker contract; the differential-testing
rule and independent-stack separation requirements; each recommendation paired with a competing
option, a decisive falsifier and what it does not prove. No kernel freeze and no selection.

## Non-goals

- No model checker run, mutant kill or implementation written by this session.
- No freeze of the privileged four-function kernel API.
- No selection of a construction language, storage engine, broker transport or renderer.
- No production wire-format claim for the deterministic-CBOR record.
- No reopening of accepted Owner decisions or the open Owner questions in GAPS.md.
- No modification of a protected path.

## Completion gate

- The model is specified with exact constants, transitions and fairness scope, and every
  invariant names its monitor requirements.
- The 36 mutants are instantiated with reachability, non-equivalence and classification rules,
  and 36/36 is stated as the acceptance metric.
- The vector format, CBOR profile, digest domain separation and refusal taxonomy are complete and
  language-neutral.
- The differential rule requires two stacks sharing no serializer, decoder registry, reducer
  implementation or generated source.
- The trace-validity checker is stated as a bounded bridge, with what it does and does not prove.
- The TLA+/TLC primary and the Alloy cross-check each carry a decisive falsifier.
- The dependency edge to FU-01 (the language experiment consumes these vectors) is stated, and
  the kernel freeze remains conditional.
- Protected paths are untouched; privacy and secret scan are clean.

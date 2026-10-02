# FU-01 — language/runtime experiment (synthesis)

## Provenance

Synthesis of the raw report at `raw/ds-FU-01-language-runtime.md`, the FU-01 candidate
preregistration (`EXP-FHAR-10` revision 1) for the follow-up wave `followups-20261002`. The
report's upstream claims rest on the report's sources and its own pinned claim ledger; nothing
here is a Recursion rerun. The raw file carries `status: research-evidence-not-a-decision` and
`verification: not independently verified by Recursion; target experiments not run`. Retrieval
2026-10-02; research cutoff 2026-10-01 UTC. This report answers gap G-01.

## The question

How can Recursion decide a hard-to-reverse language/runtime/topology choice without running the
comparison itself? The report does not ask "which language is best." It specifies the experiment
(`EXP-FHAR-10`) that would produce the missing evidence: which candidates and exact pins are
eligible, which hard floors precede any resource ranking, what host and workload conditions are
required, what acceptance oracles and stop conditions apply, and what local work remains. The
report's own answer is a deliberate **no-selection**: no language, runtime, store, dependency
stack or hybrid topology is chosen.

## Key findings

- **No selection, by construction.** The report states that no reducer, adapter, target build,
  benchmark, model checker, provider call or candidate experiment was run, and no host was
  inventoried. Every performance, byte-conformance, dependency-closure, artifact-reproducibility
  and cancellation outcome is **unknown** — not zero, not a pass.
- **Pinned candidates (documentary).** CPython 3.13.15 (2026-08-05, historical GIL and
  free-threaded arms kept distinct); CPython 3.13.16 (2026-09-30) as a prospective refreeze that
  makes the handoff's "current" pin stale; Python 3.14.8 (2026-09-30) as a sensitivity pair with
  GIL/FT and experimental JIT as separate arms; Rust 1.98.1 (2026-09-03) and prospective 1.99.0
  (2026-10-01); Go 1.27.1 (2026-09-01); PyO3 0.29.3 as a candidate extension/embedding topology;
  Go cgo as a distinct arm; single-executable packaging unselected. A floating documentation URL
  is not a pin; local execution must archive and hash exact revisions.
- **Two competing freeze choices.** Choice H preserves the historical arms and records
  supersession prominently; Choice P starts a new prospective experiment with a new identity.
  Neither selects a product runtime; the Owner must choose purpose and exact arms first.
- **Hard floors precede all tradeoffs (HF00–HF13).** Authority/scope; exact canonical byte
  sequence; command idempotence; lease/authority fencing; PauseSafety; expected state; replay
  determinism; fail-closed replay; privacy/capability isolation; bounded ownership; offline core
  closure; release evidence; diagnostics/fault validity; recovery/soak correctness. Floors run
  before resource ranking, again after stress/soak, and on every changed artifact identity. One
  reproducible valid-test violation rejects that exact arm for the declared profile.
- **Canonical-bytes dependency on FU03.** No candidate is admitted until FU03 supplies an
  Owner-approved schema, refusal registry, literal corpus, manifest digest and independent
  trace-validity checker. The shared interface `CAND-RCV1-20261001` is proposed, not recovered
  truth: ASCII `RCV1`, u16be version 1, u16 flags zero, u32 payload length, deterministic CBOR
  payload, SHA-256 over header plus payload, and a 16 MiB harness safety cap. Refusals are
  `{code, schema_epoch, field/path, stable_detail_enum}` over an 18-code registry (0–17).
  Trace-checker verdicts are `VALID_BOUNDED`, `INVALID_TRACE`, `OUT_OF_SCOPE`, `INCONCLUSIVE`.
- **Two independent oracles.** Two independently authored implementations must each equal the
  reviewed normative corpus; agreement with each other alone is insufficient. FU03's candidate
  catalog maps rows 1–88 (`vector_id = 1000 × row + variant`) to primitive, decode, admit,
  reduce, work-packet, replay and JCS families.
- **Concurrency is protocol, not a language primitive.** No surveyed runtime guarantees
  "no orphan straddles PAUSE." The report proposes one logical owner per canonical admission
  transaction, explicit epoch fencing, a defined pause-complete meaning (epoch committed, no
  stale admission/dispatch linearizes, tasks terminal or explicitly contained, descendants
  joined), and a cancellation state machine RUNNING → FENCE_COMMITTED → CANCELLATION_REQUESTED →
  JOINING → QUIESCENT or BLOCKED_UNRESOLVED. Rust Send/Sync, Go channels/atomics, the CPython
  GIL, free-threaded locks, asyncio TaskGroups, Tokio abort/`CancellationToken` and Go `context`
  are each scoped mechanisms with named failure modes, not acceptance.
- **Proposed measurement and environment.** A frozen host matrix of W primary, L primary, W
  sensitivity and L sensitivity; `profile_key` stays null until every FU04 identity field is
  present or justified not-applicable. Workloads W00–W08 (startup, primitives, pure transitions,
  contended admission, replay/faults, FFI/IPC, daemon/broker, steady soak, growth soak). Sampling:
  ≥30 independent fresh-process runs × ≥100,000 scheduled attempts = ≥3,000,000 attempts per
  populated cell; 1,000 cold launches across ≥10 blocks; soak proposed as three independent
  168-hour runs per primary arm × host × topology. Open-loop arrivals, raw integer monotonic
  timestamps, nearest-rank percentiles, run/block-aware moving-block bootstrap, Holm-adjusted 95%
  simultaneous coverage. The M2 model (`N × (1−p)` tail counts) assumes independent stationary
  observations and is used for sampling design only.
- **Accounting boundary.** Linux cgroup v2 subtree (preferred) and Windows Job Object with
  verified membership and declared breakaway policy; per-process peaks are never summed into a
  group peak. The experiment boundary includes daemon, broker, adapters, embedded interpreters,
  spawned harness stand-ins, PTY/ConPTY helpers and descendants.
- **Nothing is measured.** Every comparison cell (canonical conformance, race/pause correctness,
  cold start/tail latency, memory and 24/7 behavior, closure/reproducibility) is `Unknown`, with
  M1 as a non-quantitative conditional architectural model that predicts failure modes, not a
  winner.

## Recommendation and falsifier

Preserve the **no-selection** result and make `EXP-FHAR-10` the decision-producing artifact.
Only independently accepted floor-passers enter a Pareto comparison with uncertainty: candidate A
beats B only if both pass all floors, A meets every Owner ceiling, is noninferior within the
Owner's allowed margin on every declared primary metric/profile, and improves at least one
decision-relevant metric by the preregistered minimum with simultaneous confidence support. No
weighted composite; speed never compensates a correctness failure. Explicit no-selection triggers
include: no floor-passer; any required floor unknown; stale or unverified essential pin; missing
approved byte corpus; unqualified host/accounting; missing Owner thresholds; incompatible
workloads/durability; unexplained reproducibility difference; intervals crossing practical
margins; unresolved tradeoffs; insufficient tail or soak exposure; disputed independent review;
and the latest scope clarification unreconciled. Per-candidate falsifiers are tabulated (for
example, a byte/epoch/ownership failure or ceiling breach rejects CPython GIL; a re-enabled GIL
or unsafe extension mutation invalidates the FT identity; any unsafe/FFI breach, incorrect
cancellation, irreproducible closure or no practical advantage falsifies Rust; a goroutine/epoch
leak, byte mismatch or tail/heap breach falsifies Go; a callback/reentrancy error or combined
closure failure falsifies the PyO3 bridge; a missing asset or signing/rebuild mismatch falsifies
packaging). An implementer's PASS is never acceptance.

## Local execution handoff

The report explicitly proposes, but does not run, the experiment. Owner inputs O1–O5 are
prerequisites: confirm historical replication versus prospective refreeze and the exact
runtime/patch/build/topology arms; reconcile the retired-Hermes wording and define the current v3
authority boundary and what "native" permits; accept or replace FU03's candidate schema, refusal
registry and literal corpus; select actual Windows/Linux profiles and coordinator-small occupancy
parameters; and set product ceilings, practical margins, priority policy, reproduction target,
exposure and the independent reviewer. The executable local sequence is L01–L16: recover
obligations; freeze public artifacts; accept the corpus; qualify hosts; implement the
language-neutral harness; resolve the real dependency closure; perform an offline rebuild; run
the exact floors; exercise races; exercise cancellation; calibrate collection; run randomized
performance; run soak; verify packaging; analyze independently; present the Owner decision. The
proposed command surface (`validate-manifest`, `verify-corpus`, `qualify-host`, `verify-closure`,
`run-floors`, `calibrate`, `run-matrix`, `run-soak`, `analyze`, `package-evidence`) and exit
taxonomy are interface proposals, not existing commands. Stop conditions include: stale-epoch
admission or unauthorized post-pause dispatch; an unjoined task after a claimed pause-complete;
a malformed harness trace (invalidates the trial, does not convict the candidate); a missing
corpus (blocks all arms); and any differing byte, sequence, digest or refusal (rejects the arm).

## What this does not prove

It does not prove any runtime will win or fail, that one language is too slow, that a GC is too
expensive, or that a hybrid does or does not earn its ABI and packaging complexity. Documented
upstream mechanisms are evidence about possible implementations, not measurements of Recursion.
A version label is neither compiler correctness nor a security assessment; there is no CVE-free
claim. A lock file, SBOM, provenance statement or upstream reproducible-toolchain claim does not
by itself pass the release-evidence floor. A "single executable" is a packaging property, not a
guarantee of one process, no native dependencies or low memory. The full texts of E-FHAR2-102 and
E-FHAR2-108 were not supplied, so requirement-to-test traceability is provisional until L01
retrieves the operative clauses.

## Open Owner decisions

Purpose and exact version freeze (Choice H versus P, resolving the CPython 3.13.16 and Rust 1.99.0
supersessions); eligible native/embedded/wrapper topologies and the meaning of "native"; final
FU03 core and refusal contract and pause-complete semantics; actual qualified Windows/Linux
profiles and the coordinator-small workload parameters; product ceilings, practical margins,
priority/tradeoff policy and reproducibility/signing target; permitted exposure/cost and the
independent reviewer; and the authority boundary that retires legacy Hermes language.

## Relevance to later waves

`EXP-FHAR-10` outputs feed canonical-byte and replay suites, the plugin-isolation lane, the
`ReleaseId`/E-FHAR2-108 build-provenance and SPDX 3.0.1 evidence, and version-pinned integration.
Its acceptance consumes FU03 (corpus, refusal registry, trace checker) and FU04 (qualified host
profiles and accounting), so later waves must hold downstream admission until those prerequisite
artifacts are accepted and pinned. Until the experiment runs and is independently verified, later
waves must treat every candidate as viable and no runtime as chosen.

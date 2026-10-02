---
title: Recursion runtime evidence and experiment specification
source-prompt: FU-01 — language/runtime
session: Codex Dot follow-up research — specification only, target experiments NOT run
retrieved: 2026-10-02
status: research-evidence-not-a-decision
verification: not independently verified by Recursion; target experiments not run
---

# Recursion runtime evidence and experiment specification

FU01 research report for Lucas and the v3 engineering reviewers

EXP FHAR 10 candidate preregistration revision 1

Release inventory cutoff 1 October 2026 UTC • Final source checks and report 2 October 2026 UTC

## Decision and scope

The defensible result remains **no selection**. This report does not choose a language, runtime, store, dependency stack or hybrid topology. It specifies how an independently reviewed local experiment could supply the missing evidence. The handoff’s small deterministic native kernel with typed adapters remains the experiment’s scoped architectural constraint, subject to the Owner’s latest standalone v3 clarification. Whether a particular CPython topology satisfies the Owner’s meaning of “native” must be recorded before that topology is eligible; this report does not reinterpret that decision.

Three findings materially change the experiment preparation. First, CPython 3.13.15 is a real release, dated 5 August 2026, but Python 3.13.16 was released on 30 September 2026. Thus the handoff’s 30 September “current” CPython pin is stale unless its exact freeze time preceded that release. Second, Rust 1.98.1 is real, dated 3 September 2026, and Rust 1.99.0 was announced on 1 October 2026. Third, Go 1.27.1 is real, dated 1 September 2026; its standard library now documents jsontext.Value.Canonicalize for RFC 8785. A comparison based on older Go JSON assumptions would be misleading. None of these facts authorizes silently changing an experimental arm. [S01–S07, S14]

No reducer, adapter, target build, benchmark, model checker, provider call or candidate experiment was run. No actual host was inventoried. All runtime performance, byte-conformance outcomes, dependency-closure counts, artifact reproducibility and cancellation outcomes are **unknown**. Source-documented mechanisms are evidence about possible implementations, not measurements of Recursion. The experiment can become executable only after the corpus, host profiles, stack locks, Owner thresholds and independent acceptance gates are filled and signed off.

The Owner’s latest clarification supersedes the brief’s legacy authority wording: Hermes is retired; v3 is a standalone harness that both executes natively and wraps/orchestrates other harnesses. This report therefore uses Owner-controlled v3 authority and bounded workers. It does not present Hermes as an active executive, assume an inherited Hermes constitution governs v3, or require a separate AI manager. Native and upstream-harness execution need separate measured profiles, with identical authority and accounting obligations. No private repository audit is implied.

The report completes the literature and specification work that can honestly be completed without execution. It cannot satisfy the handoff’s empirical requirement to demonstrate or falsify identical candidate bytes. That requirement is preserved as a blocking local execution item rather than relabelled as passed. An implementer’s PASS never constitutes acceptance.

## Reading the evidence

Four claim classifications are used: **source documented**, **locally observed**, **inferred**, and **unverified**. Locally observed would require actual target evidence; there are no such target claims in this report. An inference states its premises and can be falsified. Unverified includes missing exact pins and missing applicability evidence. Confidence refers to the stated claim within its scope, never to whole-product safety.

The comparison matrices use a separate three-state vocabulary required by the handoff. **Measured** means a retained EXP-FHAR-10 result with denominator and uncertainty. **Modelled M1** means the explicit conditional architectural model below. **Unknown** means neither a measurement nor a justified quantitative model exists. A documented upstream behavior is not renamed “measured.” Qualitative documentary inputs appear in the claim ledger and explanatory sections; only conditional hypotheses enter the modelled cells.

M1 is a non-quantitative model: all candidates implement the same approved pure transition functions, a single linearized admission owner, explicit epoch fencing, bounded queues and contained descendants. Given correct implementations and qualified hosts, each could produce the approved outputs. M1 assigns no probability, latency, memory or security score. It predicts specific failure modes to test; it does not predict a winner. M2, used only for sampling design, assumes independent observations with a stable distribution so a p999 tail contains approximately N × 0.001 observations. Real correlated workloads need the clustered uncertainty procedure specified later.

All public research used generic language/runtime, operating-system and standards questions. Private repositories, infrastructure identifiers and secrets were not research inputs. The full E-FHAR2-102 and E-FHAR2-108 source text was not supplied. This report traces the obligations named in the handoff without inventing missing clauses or claiming compliance with unseen requirements.

## Version evidence and the freeze decision

### Runtime arms

| Arm identifier | Documentary version and release date | Pin status and required treatment |
|---|---|---|
| PY313 GIL historical | CPython 3.13.15, 2026-08-05 [S01] | Release existence verified; binary, compiler, build flags, target and library closure unknown. Preserve as historical replication only if Owner authorizes that purpose |
| PY313 FT historical | CPython 3.13.15 with free-threaded build configuration [S01, S08] | Same release source does not identify the FT binary. GIL build and FT build must have distinct artifact digests and runtime GIL-state evidence |
| PY313 prospective pair | CPython 3.13.16, 2026-09-30 [S02] | Verified newer maintenance release. Candidate refreeze, not automatic replacement of either historical arm |
| PY314 sensitivity pair | CPython 3.14.8, 2026-09-30 [S03] | Exact source release verified; GIL and FT configurations remain separate arms if both admitted. No extrapolation from 3.13 FT |
| RUST historical | Rust 1.98.1, 2026-09-03 [S04] | Verified release. Compiler/Cargo/LLVM/linker/target digests and dependency locks unknown |
| RUST prospective | Rust 1.99.0, 2026-10-01 [S05] | Verified announcement at the research cutoff. New experiment identity if selected for a future run |
| GO | Go 1.27.1, 2026-09-01 [S06, S07] | Official release and download listing verified. Exact platform archive, build mode, architecture feature level and library closure remain unverified |
| RUST PY extension | PyO3 documentation resolves to 0.29.3 at cutoff [S23] | Candidate topology only. Release date, archive digest, Python ABI/build pairing and crate feature closure unverified |
| RUST embedding PY | Same PyO3 possibility plus a complete embedded CPython runtime [S23] | Distinct topology from a Python process importing a Rust extension. All combined pins and packaged interpreter resources unknown |
| GO cgo | cgo bundled with selected Go version [S24] | C compiler/linker/runtime/SQLite or other native dependency pins unknown; pure Go and cgo arms cannot share a result row |
| Other single binary packaging | No packager selected | Exact packager, extraction behavior, dynamic libraries, host prerequisites and version all unknown |

The CPython 3.13.16 page explicitly lists security changes. That establishes the need to review whether retaining 3.13.15 is appropriate for an isolated historical experiment; it does not establish exposure in an unselected Recursion closure or certify 3.13.16 as safe. Rust 1.98.1’s announcement describes a fix for a vtable-generation miscompilation in 1.98.0. A version label is neither a proof of compiler correctness nor a complete security assessment. [S02, S04]

The Python 3.14 documentation describes free threading as an officially supported but optional upstream build mode, whereas 3.13 documents it as experimental. This narrower upstream status is not certification of a Recursion stack, an extension ABI or a particular Windows/Linux package. Python 3.14 also exposes experimental JIT configurations; record JIT build/runtime state explicitly and treat any enabled-JIT study as a distinct sensitivity arm rather than silently changing the GIL comparison. No upstream performance percentage is imported into the candidate matrix. [S08, S69]

Two defensible freeze choices compete. Choice H preserves the historical DS18 arms to make a historical comparison and records supersession prominently. Choice P establishes a new prospective experiment with reviewed contemporary pins and a new identity. The falsifier for H is an unacceptable known exposure, an unavailable authentic artifact or inability to reproduce the intended toolchain. The falsifier for P is treating new-version results as if they reproduced the earlier freeze. Neither choice selects a product runtime. The Owner must select the purpose and exact arms before local implementation starts.

A floating documentation URL is not an immutable source pin. Python’s 3.13 URLs resolved to 3.13.16 documentation when read. Rust’s unversioned books and several crates’ latest URLs also move. The ledger records the observed version/date and marks applicability to earlier patch releases conditional. Local execution must archive the exact source revision or documentation snapshot and hash it. Attempts to fetch some version-specific documentation routes were unavailable; no immutable snapshot digest is fabricated.

### Frozen host matrix

No actual Windows build, Linux kernel/distribution pair or hardware profile is available. Therefore the frozen host matrix is an explicitly incomplete preregistration, with no fabricated “representative” host substituted for evidence.

| Host slot | Required comparison scope | Exact identity | Qualification |
|---|---|---|---|
| W primary | Native Windows, selected CPU architecture, selected storage and terminal profile | Unknown; profile_key null | Unknown, displayed Unqualified |
| L primary | Native Linux, same declared architecture class, selected distribution/kernel/storage/terminal profile | Unknown; profile_key null | Unknown, displayed Unqualified |
| W sensitivity | Optional alternative Windows build, VM or architecture | Unknown; separate profile if commissioned | Not admitted |
| L sensitivity | Optional alternative Linux distribution, kernel, VM or architecture | Unknown; separate profile if commissioned | Not admitted |

A Windows marketing release name is insufficient; record edition, version, complete build/revision, installed servicing updates, architecture and relevant security settings. Linux requires distribution release, package image identity, complete kernel release/configuration, libc and loader versions, CPU architecture/ABI and boot parameters. Cross-OS rows are separate strata. A result on Linux cannot qualify Windows, and a VM result cannot silently qualify its host or bare metal.

Use FU04’s shared profile contract. profile_key remains null until every required identity field is present or justified not_applicable. Its identity covers OS/kernel/distribution; CPU and ABI; host and guest virtualization layers; filesystem, mount flags, storage locality, protocol/client/server/cache and power domains; terminal host/backend and shell versions; supervisor version/configuration digest/restart policy; security/MAC/FIPS/privilege/namespace/cgroup and delegation settings, Job breakaway flags; clock API and suspend semantics; and adapter/harness digests. These are fields to collect locally, not details obtained here.

For runtime resource comparison add CPU model and stepping, microcode, physical/logical cores, affinity, quota, SMT policy, NUMA placement, RAM, swap/pagefile policy, power plan/governor, boost policy, thermal monitoring, storage device/firmware and filesystem allocation unit. Record background services and benchmark isolation policy. Do not change security-sensitive settings merely to improve a result. Any necessary change requires appropriate separate authorization and becomes part of the profile.

FU04 result identity is profile_key plus fixture_id/version, variant and cutpoint, failure_domain, and contract_digest. Required qualification values are qualified, rejected or unknown; only qualified enters the main experiment. FU01 additionally requires scope_membership_complete and descendant_capture_complete to be true, with cumulative native counter snapshots, units and start/end/drop provenance. A sum of per-process peaks is never substituted for a group peak.

## Immutable experiment identity

### Identity record

Define ExperimentId as a domain-separated SHA-256 of an approved deterministic encoding of the following manifest, excluding the manifest’s own digest and signatures. This is a proposed EXP identity rule, not a replacement for a product ReleaseId definition. The encoding must itself be validated against the accepted corpus. All digest values remain unfilled until real artifacts exist.

The manifest records protocol revision; Owner approval reference; purpose H or P; exact candidate arm definitions; source commit/archive hashes; full toolchain and build-tool hashes; compiler, linker, runtime and standard-library versions; target triples/ABIs and CPU code-generation options; build flags, optimization, assertions, panic/unwind policy and allocation policy; all language/native/system dependency locks; feature/extra selection; offline source/binary closure; packaging recipe; signed and unsigned artifact hashes; SPDX and provenance digests; FU03 corpus/registry/schema/trace-checker digests; FU04 host profile and qualification digest; all workload, scheduling, fault and seed manifests; metric dictionary; instrumentation version/calibration; randomization schedule; statistical analysis procedure; Owner ceilings and practical margins; stopping rules; and independent reviewer identity/acceptance record.

Secrets and real signing keys are never embedded in the manifest. Signatures identify attestations without exposing private key material. Synthetic fixture signing uses clearly non-production test keys and cannot authorize external actions.

### Drift rules

Before and after each randomized block, collect the manifest-relevant host/toolchain/dependency facts and compare with the admitted identity. Any change to executable bytes, OS/kernel/servicing, CPU/microcode, dependency closure, selected features, workload, corpus, instrumentation, relevant environment variables, timezone/locale affecting behavior or relevant security/storage policy invalidates pooling with the original ExperimentId. A deliberate change creates a new experiment or preregistered sensitivity stratum with explicit linkage.

Transient noise is not automatically identity drift. Thermal throttling, competing processes, clock anomalies and sample drops receive per-block evidence and the declared validity rule. Keep invalid runs and reasons in the dataset. Never discard a slow run merely because it weakens a preferred candidate. Security patch discovery can stop future exposure and require refreeze; it cannot justify silently overwriting old results.

Repeatability is the same reviewed experiment performed again; reproducibility additionally needs independent reconstruction under the stated environment. A lock file alone does not establish either. Toolchain bootstrap components, generated source, build scripts, dynamic libraries and packaging resources must be included in the closure.

## Canonical bytes and the FU03 dependency

### The acceptance dependency

EXP-FHAR-10 cannot admit a candidate until FU03 supplies an Owner-approved schema, stable refusal registry, reviewed literal corpus, manifest digest and independently reviewed trace-validity checker. The candidate shared interface CAND-RCV1-20261001 is coordinated across these reports, but is explicitly a proposal completing missing details, not recovered DS22 truth or an accepted freeze.

RCV1 is a test interchange envelope. It is not the product wire protocol. Its proposed frame is ASCII RCV1, unsigned 16-bit big-endian version 1, 16-bit flags zero, 32-bit payload length, deterministic CBOR payload, then SHA-256 of header plus payload. The proposed 16 MiB payload ceiling is a harness safety cap, not a product resource budget. CBOR framing, kernel semantic bytes and broker JCS wire bytes remain distinct layers.

The proposed frame payload permits shortest-form signed/unsigned integers, definite-length byte strings/text/arrays/maps, booleans and null, with unsigned integer map keys in increasing order. It excludes floats, tags, undefined values and duplicate keys; text is strict UTF-8 without normalization. Bounds are −2^63 through 2^64−1; IDs and epochs are nonnegative. FU03 proposes an integral semantic core for completing its corpus, subject to Owner reconciliation with any accepted core encoding. FU01 does not convert this proposal into a product protocol decision.

JCS compatibility probes are layer 3 opaque byte strings. Their decimal and IEEE-754 cases do not become CBOR floats. This separation allows the requested RFC 8785 tests without contaminating integral canonical-state semantics or selecting the broker wire format.

### Required interface and vector coverage

Each vector contains corpus schema epoch, vector ID, layer, operation, raw input bytes, prestate bytes or null, ordered auxiliary inputs, exact expected output bytes or structured refusal, and stable purpose text. Operations are decode, admit, reduce, derive_work_packet, replay harness, canonicalizer and frame parser. Native runtime exception strings, addresses, stack traces, locale-dependent messages and backend diagnostics never participate in equality.

The required admission subset is all normative vectors affecting any of the four kernel operations plus framing, replay and JCS layer families listed below. “Subset” does not authorize dropping an inconvenient refusal or corner case. The admitted manifest must enumerate literal IDs rather than infer coverage from names. FU03 owns final IDs and expected bytes.

1. Primitive/frame cases: shortest integer encodings and boundaries; complete versus truncated frames; bad magic/version/flags/length/checksum; invalid UTF-8; duplicate keys; wrong types; trailing data; nesting/length/capacity violations; noncanonical encodings; and cross-layer confusion.
2. Decode cases: schema epoch and unknown kind; missing/extra fields under exact schema policy; range violations; malformed digest/identifier/token representations; valid and invalid semantic bytes; and stable refusal field/path/detail values.
3. Admit cases: expected-state match/mismatch; equal and conflicting command identities; concurrent writers; stale authority, goal, plan, lease and pause epochs; paused state; cancellation; capacity; and effect-safety/verifier refusals.
4. Reduce cases: permitted and forbidden transitions; exact event ordering; canonical command-result index; state/event hash chains; terminal-attempt rules; deterministic projection independence; and no ambient clock/randomness/network dependence.
5. Work packet cases: exact typed capability/effect budget inputs; correct authority/lease/goal/plan/pause tokens; stale packet rejection at dispatch; redaction/privacy boundaries; and no worker promotion to executive authority.
6. Replay cases: valid prefixes, duplicate committed identities, conflicting bodies, reordered/omitted/corrupt records, schema mismatch, snapshot-chain disagreement, restart/uncertain commit, and fail-closed behavior with no effect dispatch from replay.
7. JCS cases: the official numeric boundary examples, exponent formatting, finite binary64 rounding, negative zero, invalid nonfinite input, integer precision boundaries, nested property ordering, escaped-equivalent duplicate names, supplementary-plane sorting, lone surrogates, invalid UTF-8, composed/decomposed Unicode and array-order preservation.

FU03’s coordinated final candidate catalog now defines rows 1–88 with vector_id = 1000 × row + variant. For EXP-FHAR-10 admission, require rows 1–30 (primitive bytes), 31–40 (schema/expected state/idempotence), 41–53 (authority and epoch races), 54–64 (retry/cancellation/effects/verification), 65–74 (replay/projection/queues/packets/digests), 75–79 (frame), and 80–88 (JCS), including every finite expansion declared in FU03 section 10. Row 73 expands seven digest domains across schema epochs 1 and 2; row 79 covers every incomplete prefix of its designated frame; row 85 includes all 26 published numeric sample rows. Row 28 includes variants 100 and 101 for item-limit boundaries. Row 80 retains baseline canonicalizer probes and secure-input variants 100–107, with profile identity bound in auxiliary inputs and the manifest. JCS-CANON-2020 and JCS-INPUT-7920 must remain distinct; the latter includes a separately identified negative-underflow defense proposal. Literal bytes and the final complete sorted ID list still require independent materialization and review; this range mapping is not a fabricated corpus digest.

Two independently authored implementations must each equal the reviewed normative corpus; agreement with each other alone is insufficient. Independent means no shared serializer/reducer-generated implementation acting as its own oracle. Common standards inputs are permissible but correlated code generation, parser libraries or copied expected outputs must be declared. Candidate-specific wrappers translate only at the declared test boundary and cannot rewrite expected output to match the implementation.

### Refusal equality and trace validity

The required logical refusal is {code, schema_epoch, field/path, stable_detail_enum}. FU03’s candidate encoding nests code and detail and adds expected/observed scalar fields. The complete proposed code registry is MALFORMED, NONCANONICAL, UNSUPPORTED_SCHEMA, UNKNOWN_KIND, FIELD_INVALID, COMMAND_CONFLICT, EXPECTED_STATE_MISMATCH, AUTHORITY_DENIED, GOAL_EPOCH_STALE, PLAN_REVISION_STALE, LEASE_EPOCH_STALE, PAUSED, PAUSE_EPOCH_STALE, ATTEMPT_INVALID, CANCELLED, EFFECT_UNSAFE, VERIFIER_INVALID and CHAIN_MISMATCH, numbered 0–17. Capacity is a FIELD_INVALID detail in this proposal. Original interior names were not supplied; reconciliation is mandatory before freeze. Frame-parser errors remain frame errors, not kernel refusals.

No candidate language supplies these product-owned refusals automatically. Python exceptions, Rust Result enums and Go error values can carry them, but a stable protocol mapping, complete detail enum and byte encoding must be implemented and tested. Present conformance is unknown in every arm. Error text may be retained separately for diagnosis after redaction and must not leak into canonical equality.

Trace checker outcomes are VALID_BOUNDED, INVALID_TRACE, OUT_OF_SCOPE and INCONCLUSIVE. Only the first says the observed finite trace maps to the declared abstraction under its bounds; it is not proof of liveness, full refinement, real external effects or unbounded correctness. The experiment consumes checker verdicts, never edits the TLA+/TLC model of record to make a runtime pass. A checker defect or unavailable checker yields inconclusive admission, not candidate success.

### What source evidence says about JCS

RFC 8785 requires an I-JSON-compatible input domain, deterministic primitive serialization, UTF-16-code-unit property sorting and UTF-8 output. Duplicate names, invalid Unicode and nonfinite numbers are disallowed; string normalization is not performed. Numbers follow ECMAScript-compatible binary64 serialization, including canonical zero. These are protocol rules rather than consequences of using a particular map type. [S10]

Verified RFC 8785 technical erratum 7920, verified on 15 May 2024, recommends that parsers reject raw negative-zero input to avoid attacks on unparsed data. Keep two separately named tests: serializer/canonicalizer compatibility, where an admitted IEEE-754 negative zero serializes as 0; and an Owner-approved secure input-admission profile, where raw -0 can be refused before canonicalization. The latter profile must specify equivalent lexical negative-zero forms and stable refusal bytes. Canonicalization success never by itself mandates broker acceptance. FU05’s erratum-aware input profile must be reconciled with FU03’s compatibility vectors before freeze; this report does not silently change either. [S68]

CPython json defaults accept nonfinite numbers and repeated names; object_pairs_hook exposes ordered pairs so a strict decoder can detect duplicates before collapse. Its ordinary sorted JSON output is not a JCS guarantee. Explicit duplicate detection, strict numeric/domain checks and a verified JCS emitter are required. Arbitrary-precision Python integers do not make out-of-profile numeric values interoperable. Both GIL modes face the same byte rules. [S11]

Rust HashMap iteration is not a canonical-order contract. BTreeMap provides key ordering, while serde_json’s default map uses BTreeMap and its preserve_order feature changes backing behavior. Neither fact by itself establishes JCS UTF-16 ordering or all numeric/duplicate rules. A streaming/visitor decoder must preserve duplicate detection; a selected JCS implementation must prove exact bytes through the corpus. [S12, S13]

Go 1.27.1 must be assessed using its actual APIs. encoding/json v1 preserves historical behaviors, whereas v2 and jsontext expose newer strictness and canonicalization facilities. jsontext.Value.Canonicalize explicitly documents JCS, but callers can override its options. Its raw floating canonicalization documents saturation beyond finite binary64 range; Float tokens represent nonfinite values as strings and preserve negative zero. Therefore strict numeric admission must precede canonicalization when Recursion’s input contract requires rejection. A “Deterministic” option alone is not evidence of complete JCS compliance. [S14–S16]

The inference is narrow: none of the candidates is ruled out by the language alone, and none is admitted merely by a library claim. Stock JSON convenience paths in Python and Go v1 are unsafe defaults for this contract; Rust’s precise result depends on the selected decoder/emitter. A single reviewed mismatching byte or wrongly accepted invalid input decisively falsifies conformance for that arm and build. No mismatch was executed here.

## Admission races and cancellation

### A common linearization contract

The candidate experiment requires one logical owner of each canonical admission transaction. It atomically checks authority and expected state, decides idempotence, commits the allowed event/state/receipt/outbox update, and establishes a visible linearization point. This is a proposed test contract inferred from the handoff’s safety floors and FU03 interface. A mutex, GIL, atomic variable or channel alone does not establish the full transaction.

For two new commands using the same expected state, either one commits and the other receives the approved mismatch/refusal, or the serialized semantics explicitly allow the second under its own expected state. Two commits both claiming the same exclusive prestate must fail. For identical command ID and identical canonical body, exactly one committed receipt is created and duplicates return that receipt without a new event. A changed body under the same ID returns COMMAND_CONFLICT.

FU03’s proposed duplicate rule resolves an important order issue: a previously committed identical command returns its cached receipt before current epoch/state admission checks. This does not authorize a fresh dispatch. Dispatch separately revalidates current authority, lease, goal, plan and pause epochs at the effect boundary. A stale successful receipt cannot become permission to repeat an external effect.

The common two-writer fixture uses controlled barriers at snapshot read, guard completion, transaction entry, commit, receipt emission and dispatch authorization. Enumerate both winner orders and simultaneous release. Capture proposed/committed ordinals, command/body digests, writer epochs, pre/post state digests, receipts and dispatch attempts. Test within one process and across two contained processes; language thread guarantees do not fence another process.

### Language mechanisms and their limits

**Rust.** Send and Sync provide compile-time contracts for transferring/sharing values in safe Rust; unsafe implementations and FFI remain obligations. They prevent classes of data races, not logical races between individually synchronized reads and writes. A Mutex around the complete admission transaction or an owned single-writer channel can implement the required boundary, subject to review. Compile-fail fixtures should prove that the intended state type cannot be unsafely shared through the public safe API; runtime fixtures must still attempt stale snapshots, double admission, cancellation interleavings and cross-process writers. A compiler rejection of an intentionally invalid snippet is evidence about that API, not proof of product safety. [S17, S18]

**Go.** The memory model requires synchronization for shared writes. Channels, mutexes or atomics can establish ordering, but a check-then-act sequence across separate critical sections remains logically racy. The race detector detects races that occur in exercised instrumented executions; it is neither exhaustive nor representative of uninstrumented performance. Run deterministic two-writer fixtures and a separate race-instrumented safety campaign, with compiler/platform support recorded. A clean detector run does not replace protocol trace verification. [S19, S20]

**CPython with GIL.** The GIL is not the product admission lock. C calls may release it, threads can interleave compound operations, and processes have independent interpreters. Use an explicit lock or sole admission task covering the whole transition, with no await or callback-reentrancy gap that exposes partially checked state. Pin C-extension behavior and test callbacks that reenter admission. The C API’s thread-state requirements matter even when a Python caller appears single threaded. [S21]

**CPython free threaded.** Built-in containers use internal synchronization in current implementations, but the Python documentation explicitly warns against treating that implementation behavior as a general future guarantee. Unsupported extensions may re-enable the GIL. Record both build support and actual GIL state after every imported extension and before/after each run. The C-extension guide describes critical sections and borrowed-reference hazards; inspect each selected extension and exercise concurrent mutation, callbacks and teardown. Passing the GIL arm does not qualify the FT arm. [S08, S09]

**C and C++ components.** These are relevant as FFI dependencies, not newly selected product candidates. A native component can invalidate the surrounding language’s safety assumptions through data races, lifetime errors or undefined behavior. Compiler sanitizers are separate diagnostic builds with their own supported target/ABI limits and overhead. ThreadSanitizer and AddressSanitizer coverage does not prove absence of all races, memory bugs or protocol violations. If a sanitizer cannot cover a required Windows/native path, that gap stays visible rather than borrowing Linux coverage. [S25, S26]

### A precise pause boundary

No surveyed language runtime guarantees “no orphan straddles PAUSE” by itself. The protocol must define what PAUSE acknowledges. Proposed pause-complete means: the new pause epoch is committed; no new admission or dispatch under an older epoch can linearize; all pre-pause owned tasks have terminal records or an explicit contained unresolved state that prevents resume; all cancellable descendants have been joined/reaped; and no old task can later submit an authorized effect. A pause request may acknowledge receipt earlier, but that acknowledgement must not be labelled pause-complete.

The semantic freeze and physical cleanup are distinct. Committing the epoch fence can prevent future admission while a blocked external call still exists. If the product contract requires absolute absence of surviving old tasks, pause-complete must wait for cleanup or fail closed. If an external effect already crossed the irreversible boundary before PAUSE, cancellation cannot retract it; reconciliation must retain its uncertainty. The experiment uses synthetic effect sinks and never real providers.

Proposed cancellation state machine: RUNNING → FENCE_COMMITTED → CANCELLATION_REQUESTED → JOINING → QUIESCENT, or BLOCKED_UNRESOLVED. Every transition carries pause epoch, owner task identity and retained evidence. Deadlines use the qualified monotonic clock contract. Resumed work must use the new pause epoch committed by PAUSE and explicitly resolve old capabilities. Under FU03’s candidate rule, PAUSE advances pauseEpoch (for example 0 to 1), while RESUME retains that epoch; this report does not require an additional increment on RESUME. “Timeout elapsed” alone never establishes quiescence.

**asyncio.** TaskGroup owns tasks created through it and waits for completion on exit; cancellation is delivered cooperatively. Swallowing CancelledError can break structured behavior. Detached tasks and blocking thread/native work need separate ownership and termination semantics. Tests must include swallowed cancellation, shielded work, nested TaskGroups, tasks created outside the group, blocked I/O, a CPU loop with no await and thread-pool work that outlives its awaiting task. [S22]

**Tokio.** Dropping a JoinHandle detaches the task. abort requests cancellation and should be followed by joining; completion may already have occurred. Started spawn_blocking work cannot generally be aborted. CancellationToken signals a request; cancellation propagation is not a cross-task transactional fence, and cancel-safe waiting does not make the operation being cancelled safe. Retain task handles, use explicit ownership/joining, prohibit unregistered spawn at the admission boundary and isolate uninterruptible work when the approved topology requires process termination. [S27, S28]

**Go.** Context carries cancellation/deadline signals, but CancelFunc does not wait for work to finish. Goroutines must cooperate and their completion must be joined through a declared mechanism. Tests must include forgotten cancel calls, blocked channels, context-insensitive I/O, unjoined goroutines, timer retention and cgo work. A WaitGroup completion alone cannot attest that descendants or side effects are contained. [S29]

**Hybrid topologies.** A Python task cancellation does not automatically abort a Rust future or C call; a Rust token does not automatically stop an interpreter or arbitrary native extension; a Go context does not cancel arbitrary C code. Define an explicit cross-boundary cancellation ABI, ownership transfer, callback/reentrancy policy, terminal acknowledgement and resource reclamation protocol. Cost and failure behavior of that ABI are measurements, not assumptions. [S23, S24]

### Cancellation fixtures and decisive failures

At each barrier before guard, after guard, before commit, after commit before receipt, before effect authorization, during effect handoff and during cleanup, inject PAUSE and CANCEL in both orders. Then attempt a stale completion, duplicate receipt, new dispatch, resume and supervisor restart. Include child/grandchild creation immediately before cancellation, blocked output pipes and a child that ignores graceful termination. The FU04 containment fixture must confirm membership and final emptiness; use a bounded synthetic workload so these tests cannot affect real services.

A stale-epoch admission or unauthorized post-pause dispatch is a hard-floor failure. An unjoined task after a claimed pause-complete is a hard-floor failure. An unresolved pre-pause external-effect status is not automatically a safety failure if it remains explicitly blocked and the approved contract permits that state; falsely reporting it as cancelled is a failure. A timeout without retained state/evidence is inconclusive or failed according to the approved timeout rule, never success.

## Language independent hard floors

Run floors before resource ranking, again after stress/soak, and on every changed artifact identity. The default result is unknown until independently accepted. A single reproducible valid-test violation rejects that exact arm for the declared profile. A malformed harness trace invalidates the trial and blocks admission; it does not convict the candidate or count as a pass.

| Floor | Required local test and pass condition | Failure or stop condition |
|---|---|---|
| HF00 Authority and scope | Independent reviewer confirms allowed kernel/adapter boundary, Owner-controlled v3/worker authority separation, synthetic-only effects and accepted protocol schema | Any worker authority escalation, unapproved protocol substitution or real external route activation stops the campaign |
| HF01 Exact canonical sequence | Every normative byte vector for decode/admit/reduce/derive_work_packet equals reviewed bytes/refusals on both hosts | Any differing byte, sequence, digest or refusal rejects the arm; missing corpus blocks all arms |
| HF02 Command idempotence | Identical ID/body yields one canonical receipt/event effect; changed body same ID refused; crash retry reconciles | Double commit/effect, conflicting body accepted or blind uncertain-effect retry rejects |
| HF03 Lease and authority fencing | Stale owner/lease/goal/plan/pause tokens refused at admission and fresh dispatch; two writers serialized | Any stale capability that newly authorizes mutation/effect rejects |
| HF04 PauseSafety | All pause/cancel barrier schedules meet the approved pause-complete definition and descendant cleanup contract | False quiescence, orphan capable of later admission or post-fence dispatch rejects |
| HF05 Expected state | Correct prestate accepted; wrong prestate refused; deterministic precedence preserved, including exact duplicate receipt rule | Race allows two exclusive stale-state commits or refusal precedence drifts |
| HF06 Replay determinism | Fresh replay from genesis and approved snapshot yields exact state, receipt index and output sequence under varied scheduling/locale/hash seeds | Any divergence or ambient nondeterminism rejects |
| HF07 Fail closed replay | Corruption, unknown schema, invalid chain, truncation and incompatible snapshot stop safely with no effect dispatch | Silent repair, skipped invalid event, fabricated success or replay side effect rejects |
| HF08 Privacy and capability isolation | Synthetic secrets/canaries never appear in unapproved canonical/public/diagnostic outputs; adapter privileges remain bounded | Leak or unauthorized data/authority crossing rejects and stops related execution |
| HF09 Bounded ownership | Queue overflow, task limits and descendant accounting behave by approved refusals; no hidden helper work | Unbounded uncontrolled growth, escaped helper or incomplete accounting prevents comparison |
| HF10 Offline core closure | Clean isolated build and launch from authentic locally staged closure with networking denied; no provider/plugin initialization | Any undeclared download, missing dynamic asset or paid/provider/auth dependency blocks admission |
| HF11 Release evidence | Lock/provenance/SPDX 3.0.1 bind the exact unsigned artifact; independent offline rebuild matches declared reproducible target | Missing/mismatched evidence or unexplained artifact difference blocks qualification |
| HF12 Diagnostics and fault validity | Controlled race/native diagnostic tests and FU04 containment/clock fixtures qualify declared surfaces | Unsupported diagnostic coverage is recorded; required untested surface remains unknown |
| HF13 Recovery and soak correctness | All retained invariant checks survive soak, restart and task churn; final replay matches | Any safety/correctness breach rejects regardless of good resource figures |

HF11’s reproducible target must be stated precisely before running. A justified nondeterministic signature/timestamp wrapper can be separated from a byte-reproducible unsigned payload, but cannot be omitted from the release manifest. If the Owner requires complete signed-package byte equality, that stronger floor must be tested as written. Source code availability, a lock file, an SBOM or an upstream reproducible toolchain claim does not individually pass HF11.

E-FHAR2-102 is traced here to identical typed boundaries, vector/refusal conformance and FFI semantics; E-FHAR2-108 is traced to ReleaseId, core lock digest, provenance digest, SPDX 3.0.1 and offline/reproducible closure as named by the handoff. Exact requirement-to-test mapping against the operative versions remains a local prerequisite because their full texts were not supplied.

## Candidate comparison without invented measurements

Every data cell below is measured, explicitly modelled, or unknown. M1 is the conditional architectural model defined earlier. No cell in this report is measured.

| Arm | Canonical conformance | Race and pause correctness | Cold start and tail latency | Memory and 24 by 7 behavior | Closure and reproducibility |
|---|---|---|---|---|---|
| CPython GIL | Unknown; M1 permits strict wrapper | Unknown; M1 requires explicit whole-transaction owner | Unknown | Unknown | Unknown |
| CPython FT | Unknown; M1 permits same byte contract | Unknown; M1 additionally requires audited extension safety and actual disabled GIL | Unknown | Unknown | Unknown |
| Python 3.14 sensitivity | Unknown; cannot inherit 3.13 outcomes | Unknown; separate GIL and FT results | Unknown | Unknown | Unknown |
| Rust | Unknown; M1 permits explicit encoder/reducer | Unknown; M1 uses safe ownership plus protocol fencing, with unsafe/FFI obligations | Unknown | Unknown | Unknown |
| Go pure | Unknown; documented jsontext is a possible M1 component | Unknown; M1 requires synchronization and joined cooperative tasks | Unknown | Unknown | Unknown |
| Go cgo | Unknown; M1 adds ABI boundary | Unknown; M1 includes C ownership and cancellation limits | Unknown | Unknown | Unknown |
| Python with PyO3 extension | Unknown; M1 retains both serialization boundaries | Unknown; M1 requires explicit cross-runtime ownership | Unknown | Unknown | Unknown |
| Rust embedding Python | Unknown; M1 retains embedded interpreter semantics | Unknown; M1 requires interpreter/worker lifecycle containment | Unknown | Unknown | Unknown |
| Packaged single executable | Unknown; packaging cannot change normative bytes | Unknown; M1 includes extraction/helpers and shutdown | Unknown | Unknown | Unknown |

A “single executable” is a packaging property, not a guarantee of one process, no native dependencies, no runtime assets, low RSS or reproducibility. Likewise, “pure Go,” “safe Rust” and “GIL enabled” are scoped implementation labels, not product safety verdicts. No qualitative label is converted into a weighted score.

| Metric outcome per arm and host | PY GIL | PY FT | PY314 | Rust | Go pure | cgo | PyO3 or embedding |
|---|---|---|---|---|---|---|---|
| p99 admission ns per attempted command | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |
| p999 admission ns per attempted command | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |
| Group memory bytes and bytes per active task | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |
| Soak memory slope bytes per hour at fixed occupancy | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |
| CPU ns per attempt and per committed event | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |
| GC or allocator stall distribution | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |
| FFI ns per call by direction and payload | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |
| Installed and compressed artifact bytes | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |
| Direct and transitive dependency identities | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |

PY314 is a matrix abbreviation only; its GIL and FT values must be split in the executed results. Hybrids must also be split by actual topology, ABI and host. Unknown is not zero and is never treated as an advantage over a measured cost.

## EXP FHAR 10 preregistered workload protocol

### Status and prerequisites

This is an executable specification in the sense of exact contracts, workload rules, required records and decision procedures. It is not runnable benchmark software and contains no claim that such software already exists. Its status is **candidate preregistration, blocked pending freeze inputs**. Local agents must implement and independently review the harness after the Owner completes the listed inputs. A missing required value causes PRECONDITION_UNMET, not a guessed default.

Required freeze inputs are: approved exact arm set and topology; definition of the privileged native kernel boundary; independently reviewed FU03 literal corpus/manifest/registry/checker; FU04 qualified W and L profiles; reviewed synthetic workload generator and seed manifest; exact dependency/toolchain/package locks; approved product ceilings and practically meaningful differences; allowed runtime resource envelope; collection/instrumentation contract; fault campaign and timeout semantics; statistical comparison family; and an independent acceptance reviewer. The experimental service, packaged daemon/broker and upstream-wrapper topology may have different runtime choices; this experiment must not force a single global language decision.

### Workload profiles

The primary semantic workload is the same deterministic transition sequence for every candidate. It uses only synthetic goals, commands, events, packets and effects. It contains no model/provider invocation, real account credentials, live network service, private dataset or external side effect. A synthetic loopback/pipe endpoint can stand in for an upstream harness only after its behavior and overhead are frozen.

The coordinator-small profile needs an Owner-approved resource and occupancy manifest. Rather than invent a deployment budget, define these mandatory fields: active goals G, maximum workers W, bounded admission queue Q, command/event/packet byte-size distributions, retained canonical history H, projection count V, task churn rate, maximum nesting/string/collection sizes, offered arrival-rate grid, timeout semantics and accepted/refused/duplicate operation mixes. All are currently unfilled. An experiment with unfilled profile fields cannot claim coordinator-small relevance.

The following workload families are fixed in scope. Their numeric contents are populated from the approved synthetic corpus and profile, not private production captures.

| Family | Operation and control | Required result strata |
|---|---|---|
| W00 startup | Process creation through readiness handshake; empty genesis and fixed replay state | OS-cold versus OS-warm cache, empty versus replay, package topology |
| W01 primitives | decode, canonicalize, hash, schema validation and refusal encoding with fixed bytes | Operation, input bytes, valid/refusal family, numeric and Unicode class |
| W02 pure transitions | admit/reduce/derive_work_packet with deterministic in-memory inputs and synthetic clock facts | Per attempted command, committed event, derived packet and refusal |
| W03 contended admission | Same command schedule with one producer, two synchronized writers and approved burst concurrency | Offered load, concurrency, queue occupancy, outcome class |
| W04 replay and faults | Fixed valid/corrupt prefixes, restarts, epoch races, uncertain commits and synthetic effect reconciliation | Corpus/fault ID, cutpoint, prefix size and checker verdict |
| W05 FFI and IPC | Empty-call baseline plus identical payload transforms and callback/ownership patterns | Direction, payload bytes, copy/borrow policy, warm/cold boundary, concurrency |
| W06 daemon and broker | Contained helper processes, PTY/ConPTY streams, detach/reattach and synthetic upstream-harness protocol | Native execution versus wrapper topology, helper count, output rate, bounded backpressure |
| W07 steady soak | Fixed live occupancy with completed task reclamation and fixed retention policy | Memory level/slope, pauses, handles/tasks/threads/children, invariant failures |
| W08 growth soak | Declared increasing canonical history/goal/view sizes at known rates | Bytes per retained event/task/view, compaction behavior and residual unexplained slope |

W02 isolates runtime/kernel cost. W06 measures the shipped topology, including broker, adapters and upstream harness stand-ins. Report both. Removing orchestration from the runtime comparison would miss a central part of standalone v3. Conversely, letting different real upstream harness workloads dominate W02 would obscure what is being compared.

If a store binding is needed, all candidates use the same approved semantic/durability contract and separately report binding/engine/version effects. FU02 owns the store comparison. FU01 cannot select a store, quietly give one candidate weaker durability, or claim runtime superiority from an unnormalized database configuration. A pure in-memory control and an integrated store stratum are kept separate.

### Sequence and randomization

The future local execution sequence is fixed: validate manifest prerequisites; qualify instrumentation and host fixture identities; build offline and independently reproduce artifacts; run full safety/conformance floors; run a separately labelled calibration pilot; freeze the remaining pilot-derived parameters using the preregistered algorithm; execute randomized comparison blocks; execute soak/fault campaigns; rerun floors and replay; independently analyze and review results; issue no-selection or an Owner decision proposal.

The pilot is excluded from comparative estimates. It can determine timer overhead, usable histogram range, safe workload duration and a common offered-rate grid. It cannot change expected semantics, remove slow cases or choose favorable compiler/library options after seeing comparative results. Any substantive tuning creates a new arm/revision with all prior outcomes retained.

Primary offered-load rates should be Owner-supplied product targets. If those are unavailable, an exploratory rate grid can be generated by a preregistered saturation search common to all admitted arms: find each arm’s stable service region under the same queue and failure policy; choose the minimum qualifying rate across all arms as the common scale; compare identical absolute rates at 25%, 50%, 75%, 100% and 125% of that scale. The search step size, dwell time and stability criterion must be fixed before the pilot. This grid describes relative stress, not a product capacity promise, and cannot substitute for product ceilings in an adoption decision.

Use blocked randomization within each host/day/profile. Each block includes every eligible arm once, in a seed-derived order. Keep architecture and cache-state strata separate. Do not run competing arms simultaneously on the same exclusive resource envelope. Record warmup explicitly: fixed preregistered warmup count/duration, followed by a measurement boundary; report warmup resource and latency separately rather than hiding it. Run cold startup as its own experiment with a defined cache reset, not an improvised deletion of arbitrary caches.

Random seeds determine synthetic data and schedule choices, but actual scheduling remains measured. Retain the full generated arrival schedule so no candidate gets easier random inputs. Hash-seed and locale variation belong to determinism tests; performance runs use fixed recorded values unless those variables are explicit factors.

### Sample counts and tail policy

The proposed sampling design is a research design choice, not an invented performance budget. Ratify it before execution. For each admitted arm × host × primary workload/outcome × offered-load cell, collect at least 30 independent fresh-process runs with at least 100,000 scheduled attempts per run, giving at least 3,000,000 attempts per fully populated cell. Outcome-specific tails must meet their own denominator requirement; pooling accepted and refused commands cannot make an under-sampled rare refusal class appear qualified.

Under M2, 3,000,000 independent observations would place approximately 3,000 above the true p999 and 30,000 above p99. This explains the proposed sample scale but does not establish effective sample size under autocorrelation. Report raw count, completed count, censored count, independent run count, elapsed duration and estimated correlation structure for every percentile. Do not report a numeric p999 for a class with insufficient retained tail evidence; label it unknown or underpowered.

For cold start, collect 1,000 launches per admitted cache/profile cell distributed across at least 10 blocks. Report median, p95 and p99 with intervals, full failure count and censoring. p999 cold start remains exploratory/unknown unless separately commissioned at adequate sample size; a maximum of 1,000 trials is not a reliable p999 claim. Reboots/cache resets and process launches are different experimental units and must be recorded separately.

Use raw integer monotonic timestamps as the canonical latency evidence. A histogram is a derived representation with fixed recorded lowest/highest values and precision; retain overflow/underflow counters. Do not clip large values into a maximum bucket without reporting them. HdrHistogram is an available measurement technique, not a selected library or evidence of its overhead on these hosts. [S30]

Open-loop arrivals use intended issue time even when a client falls behind. End-to-end response latency includes schedule delay, transport, queueing and terminal result. Record both intended and actual issue times to expose load-generator stalls. A closed-loop microbenchmark can characterize service time but cannot be substituted for overload tail behavior. Timeouts and dropped attempts remain in the denominator; do not silently remove them or substitute the timeout threshold as an exact latency. If the fraction still unresolved at deadline exceeds 1−p, the requested p-quantile is at least the censoring boundary and may be unidentifiable. Report a bound or unknown, not a fabricated finite percentile.

### Metric dictionary and denominators

| Metric | Definition and denominator | Required companion data |
|---|---|---|
| Cold start | Monotonic ns from OS process-create request to authenticated synthetic readiness handshake, per launch | Empty/replay state, cache status, retries/failures, all helper readiness and package extraction |
| Admission service | ns from complete validated transport receipt to linearized result/receipt, per attempted command | Accepted/refused/duplicate strata, input bytes, queue depth, commit boundary definition |
| End to end admission | ns from scheduled arrival to terminal reply, per scheduled attempt | Offered/completed/censored counts, generator lag, transport and queue components |
| Pure operation cost | CPU ns and wall ns per decode/admit/reduce/packet operation | Exact input size/type and allocation counters; no cross-operation averaging |
| Tail latency | Empirical p99/p999 of the specified latency population | Counts, run/block IDs, confidence interval, censoring, histogram precision and raw data availability |
| CPU work | Group user+kernel CPU ns per attempted command and separately per committed event/derived packet | Group cumulative deltas, active cores/quota, elapsed wall time and idle baseline |
| Memory level | Group charged bytes plus separately defined resident/private/PSS observations | Steady occupancy, sample timing, live tasks/goals/events/views, peak semantics |
| Memory slope | Bytes per hour over fixed-occupancy soak and bytes per completed task/event separately | Retention policy, warmup window, slope interval, GC/allocator/reclamation cycles |
| Allocation and GC | Allocated bytes/count per operation; pause ns per observed collection/stall | Runtime instrumentation semantics, collector generation/type, event count, missing coverage |
| FFI | Incremental ns per boundary crossing by direction, payload and ownership rule | Matched native control, batch size, warmup, copy count, conversion and cleanup included |
| IPC wrapper cost | ns and bytes/CPU per synthetic upstream request/response | Broker+helper accounting, framing bytes, request outcome, serialization and backpressure |
| Artifacts | Compressed distribution bytes, unpacked installed bytes and startup extraction bytes | Per OS/arch/profile; shared runtime prerequisites and debug/symbol policy |
| Dependency closure | Count of unique direct identities and unique transitive identities, separately build/runtime/test | Exact name/version/source/hash/feature tuple, native/system libraries, generators and tools |
| I/O | Group logical and physical read/write bytes and operation counts per attempt/event | OS counter meanings, cache state, storage path class, shared-service attribution |
| Scheduler cost | Context switches/wakeups per second and per attempt where captured | Counting method, missing event count, scheduler tracing scope and overhead |
| Resources retained | Open handles/descriptors, threads, tasks, timers and descendant count at fixed checkpoints | Per process and group totals; created/completed/reaped counts and ownership registry |
| Reliability exposure | Failures per scheduled attempt, per fault injection and per elapsed group-hour | Exact failure taxonomy, censoring, exposure strata, independence assumptions |
| View cost | Bytes and CPU ns per materialized view/update | View count, source event count, refresh policy and invalidation behavior |

A GC-free language does not have zero memory-management latency. Rust destruction, reference-counted graphs, allocator contention and page faults can pause work. CPython GC callbacks describe cyclic-collector events rather than every reference-count destruction or allocator stall. Go runtime metrics expose supported distributions, but GC pauses are not all scheduler/application stalls. Report the common end-to-end latency plus runtime-specific diagnostic series; do not compare unlike counters as if they were the same measure. [S31–S33]

### Process tree accounting

On qualified Linux profiles, an exclusive cgroup v2 subtree is the preferred accounting boundary for this experiment. Capture cumulative CPU and I/O, memory.current/peak and memory events using the available kernel interfaces; cross-check membership and process lifetimes. cgroup memory includes categories such as file/kernel memory and is not identical to summed RSS. /proc resident/PSS/private observations are diagnostic companions with their own semantics, never interchangeable with group charge. [S34, S35]

On qualified Windows profiles, use a Job Object with verified membership and declared breakaway policy, plus supported job accounting and process memory snapshots. Working set, private commit and peak job memory are different quantities. Retain exact counter class/field/version and units. Child creation must be captured from the beginning; attaching a job after a child already escaped is not complete accounting. [S36–S38]

The experimental boundary includes daemon, broker, adapters, embedded interpreters, spawned harness stand-ins, compiler/runtime helpers used during measured startup, PTY/ConPTY helper processes and descendants. The load generator and external collector are reported separately but their resource interference is characterized. A shared external service that cannot be exclusively attributed requires a separate whole-topology stratum; it cannot be used to hide cost outside the candidate process.

Never sum individual peak RSS values and call that a simultaneous group peak. Never sum cumulative parent+child counters when the parent counter already includes the child. Sample group totals at the same timestamps, retain native counter deltas across short-lived exits, and record reset/overflow/drop events. For physical I/O and wakeups that cannot be fully attributed on a given profile, report unknown and restrict the comparison rather than infer zero.

A fixture deliberately creates a helper that allocates memory, burns bounded CPU, writes bounded data and exits before the next ordinary sample. Accounting must still recover the declared cumulative work and observe membership/exit. Another fixture attempts permitted/forbidden descendant escape under the actual privilege model. Any missing required attribution blocks resource ranking, even if the main process appears small.

### Soak protocol

The proposed qualification exposure is three independent 168-hour continuous runs per primary arm × host × topology, each starting from the same reviewed state and retention policy. This seven-day minimum is a preregistered observation window for “24/7” behavior, not a proof of indefinite operation. If that exposure is too costly, the Owner may commission a smaller exploratory study before the freeze; its results must be labelled exploratory and cannot claim the stronger qualification.

W07 holds live occupancy and retained canonical data bounded by the approved profile. It cycles task completion/reclamation, packet derivation, refusal, duplicate, pause/resume, detach/reattach and synthetic upstream-wrapper activity. W08 separately grows history/views at declared rates and exercises approved compaction. Mixing retained-state growth with W07 would confound a leak slope with useful retained data.

Collect group memory/CPU/I/O at one-second intervals, ownership/resource gauges every ten seconds, invariant/checkpoint summaries every minute and exact event/receipt evidence according to the frozen trace policy. Those proposed intervals must be validated for overhead in the pilot; any adjustment is frozen before the main soak. Record monotonic and wall timestamps, suspend/resume and clock anomalies. Keep the collector outside the candidate group and measure its overhead.

Primary memory slope uses hourly medians after the preregistered first-hour settling window, with Theil–Sen slope and a run/block-aware confidence interval. Also publish the full first hour, level distribution, hourly maxima, start/end/minimum after reclamation, and an alternative ordinary least-squares descriptive slope. Do not force GC or restart to flatten the primary series. Optional forced-reclamation diagnostics are separately labelled and cannot erase primary growth.

Compare slope only at equal live occupancy/retention. An apparently flat slope can still violate the Owner’s memory ceiling; an apparently positive slope may be explained by intentional retained history. Both level and unexplained residual growth matter. A seven-day line fit cannot rule out rarer leaks, calendar-boundary bugs, storage exhaustion or month-long fragmentation. That limitation survives a pass.

Inject only the frozen synthetic fault schedule, with all cutpoints logged. Safety violations stop that arm immediately and preserve evidence. Resource-ceiling breach stops the affected test according to the approved ceiling and records failure; missing ceiling means no product pass can be issued. Host loss, corrupted collector output or violated isolation marks the affected interval invalid/inconclusive and triggers the declared rerun under the same identity if possible. Neither a silent restart nor replacement with a different host continues the original exposure.

### Statistical analysis and stopping

Use nearest-rank empirical percentiles, with exact definition and tie policy frozen in the analysis manifest. For an independent sample sensitivity analysis, form quantile confidence bounds from binomial order-statistic ranks. The binomial assumptions must be stated; a large request count is not equivalent to a large number of independent process runs. [S39]

The primary comparative inference resamples independent randomized blocks/runs, not individual correlated requests. Within-run autocorrelation is represented using a preregistered moving-block bootstrap whose block length is selected by the calibration rule and frozen before the main data. Report per-run quantiles, pooled descriptive quantiles and paired differences/ratios with confidence intervals. Do not average percentiles and call the average a pooled percentile. If stationarity fails, stratify the time series and report the failure rather than presenting a misleading single interval.

The comparison family is all preregistered pairwise arms across the declared primary metrics and profiles. Use 95% simultaneous coverage with the frozen multiple-comparison method, such as Holm-adjusted tests plus compatible adjusted confidence intervals; do not switch methods after seeing significance. Practical margins and noninferiority directions come from the Owner before data collection. Where sample design or correlation makes the intended interval unreliable, mark the decision inconclusive.

Complete the declared fixed sample/exposure targets. Do not stop early for a favorable p-value. Safety/validity ceilings are the only automatic early stops. A pilot-derived inability to obtain the required sample/exposure within the Owner’s authorized resource envelope yields insufficient evidence; it is not a license to lower the target after seeing the result. Additional data require a new preregistered extension or experiment, with its relationship to the original explicit.

Zero observed failures is reported as zero in a specific observed denominator, never “failure free” in general. Under an explicitly stated independent Bernoulli model, a one-sided upper confidence bound can be computed as 1−α^(1/N); correlated failures require a different exposure model or no numerical extrapolation. Never project a multi-year availability claim from a few days of synthetic soak.

## Library closure and release evidence

### What can and cannot be resolved now

The real SQLite, JCS, signing, PTY/ConPTY, MCP and HTTP stack is unselected. Therefore the resolved transitive closure, exact license obligations, maintenance exposure, vulnerability applicability and artifact costs are unknown for every candidate. Public project existence is not a resolved product dependency. Import counts shown by package documentation are not the direct/transitive count required by this experiment.

The following is a source-backed option inventory for future locking, not a recommended stack. Each entry must be resolved for each OS, architecture, build mode and feature set. Standard-library code still belongs in the toolchain/runtime SBOM and security review; it is not “zero dependencies.”

| Role | CPython possibilities | Rust possibilities | Go possibilities | Unresolved evidence |
|---|---|---|---|---|
| SQLite | stdlib sqlite3 or APSW [S40, S41] | rusqlite with exact native/bundled engine choice [S42] | modernc.org/sqlite or mattn/go-sqlite3 [S43, S44] | Engine/source digest, compile options, binding ABI, threading/transaction semantics, dynamic versus bundled closure |
| Canonical JSON | Strict decoder plus rfc8785 or another reviewed implementation [S11, S45] | Strict decoder plus serde_jcs or another reviewed implementation [S13, S46] | jsontext.Value.Canonicalize with strict admission/options [S14] | Entire vector pass, duplicate-before-collapse policy, numeric domain, metadata and transitive lock |
| Crypto and signing | cryptography or an explicitly audited native API route [S47] | Explicit signing crate/provider; rustls is TLS, not a general artifact-signing answer [S48] | crypto/ed25519 if the approved algorithm is Ed25519; other algorithms require separate choice [S49] | Approved algorithm/key handling, provider/FIPS requirements, native libraries, side-channel and API suitability |
| PTY and ConPTY | Platform API binding or reviewed cross-platform package; no package selected | portable-pty is a documented option [S50] | creack/pty is a Unix option; separate Windows path required [S51] | FU04 backend, shell, terminal, containment and teardown qualification; Windows closure |
| MCP | Official Python SDK candidate | Official Rust SDK candidate | Official Go SDK candidate | Exact SDK/spec revision, transport/features/auth policy and dependencies; official tier is not Recursion acceptance [S52] |
| HTTP | HTTPX or reviewed standard-library route [S53] | reqwest with selected TLS provider/features [S54] | net/http with selected TLS/DNS/proxy behavior [S55] | Streaming/cancellation limits, proxy/CA/DNS policy, connection pooling and offline tests |

Documented example versions observed at the cutoff include APSW 3.53.4.0, rusqlite 0.40.2, modernc.org/sqlite v1.60.1 dated 29 September 2026, serde_json 1.0.151, serde_jcs 0.2.0, portable-pty 0.9.0 and creack/pty v1.1.24 dated 31 October 2024. These are inventory observations, not chosen experiment pins. Exact release dates and authentic archive digests for entries not stated here remain unverified. Latest pages can move and cannot be used as lock files. [S13, S41–S46, S50, S51]

Some findings are already useful. SQLite has compile-time/start-time/connection threading modes, so “SQLite is thread safe” is too broad to qualify any binding. Python sqlite3’s check_same_thread setting and actual engine threading configuration are separate facts. Selecting modernc versus cgo changes compiler/native dependencies and runtime behavior; that is a topology factor, not a harmless substitute mid-run. Rust/Python bridges combine both runtimes’ lifecycles and closure, even if packaged behind one entry point. [S24, S40, S43, S44, S56]

### License and maintenance posture

No whole-product license verdict is possible before closure resolution. SQLite’s project states that its core is public domain, while bindings and ancillary code have their own licenses. Registry metadata observed for modernc.org/sqlite is BSD-3-Clause and for creack/pty is MIT. These limited facts do not establish compatibility for the complete packaged artifact, bundled dependencies, generated code, cryptographic provider or redistributable runtime. [S43, S51, S57]

For each selected component the future closure record must include the exact license expression or unresolved status; license texts and notices; source location/revision; provenance of vendored modifications; static/dynamic linking; optional features; patent/redistribution considerations flagged for appropriate review; and whether required source or notice delivery is satisfied. Do not assign a permissive license to unknown transitive components based on the root package’s badge.

Maintenance cadence is likewise a per-component observation, not a language trait. Capture release timestamps over a fixed lookback window, security-policy location, supported branches, documented end-of-support dates, time from public security advisory to available fix when determinable, and evidence of abandoned dependencies. A sparse release history may indicate stability or inactivity; the report cannot infer which without issue/advisory context. Freeze the lookback window and observation date so later maintenance changes do not silently alter the comparison.

The Go release policy states support lasts until two newer major releases exist; that is a toolchain policy, not a support promise for third-party modules. The Python release pages and Rust release announcements document specific maintenance actions, not certification of every deployment. Use the selected branch’s current official policy during local freeze. [S02, S04, S06]

### Vulnerability evidence

There is no CVE-free claim in this report. Known advisory history is neither normalized attack exposure nor a count-based language ranking. A project with more published advisories may have better reporting, greater adoption, broader scope or more discovered defects. A scan with no matches can reflect incomplete identifiers or database coverage.

For each locked package/toolchain/native component, record exact name/ecosystem/version/hash and selected features; advisory database/source snapshot and timestamp; affected/fixed version ranges; reachable feature or code-path evidence; exploit prerequisites; remediation; and unresolved applicability. Distinguish known affected, known not affected with justification, fixed by the selected build, under investigation and no matching advisory found. The last status is not “safe.” OSV’s schema can encode version/range evidence but does not establish product reachability. [S58]

CPython 3.13.16’s release page lists security changes relative to the historical arm, so its predecessor requires explicit advisory triage if retained. SQLite maintains a dedicated vulnerability discussion emphasizing that applicability depends on how the library is used. These are reasons to investigate the selected closure, not reasons to infer identical exposure in every binding or to claim a clean bill of health from an updated version. [S02, S59]

The experiment’s synthetic offline core profile reduces the set of exercised routes but does not erase release exposure. Core and optional adapter closures must be separately enumerated. A networking package excluded from the core may still be part of a shipped edition and requires its own evidence; conversely, a development-only package should not be counted as a loaded runtime dependency without explanation.

### Offline builds by ecosystem

CPython requires a complete interpreter distribution or reproducible source build plus all wheels/sdists/native build prerequisites and runtime assets for the exact target ABI. pip’s hash-checking mode can constrain distributions, but source-build toolchains, build-system requirements, editable/local dependencies and native dynamic libraries require additional locking. Stage a wheelhouse/source closure deliberately; the qualification build runs with network denied and must not opportunistically resolve packages. [S60]

Rust requires Cargo.lock, exact features/targets, vendored registry and git sources, compiler/linker/native build tools and all build-script inputs. Cargo vendor supports local dependency sources and --frozen combines lock and offline behavior. That controls Cargo resolution; it does not automatically prohibit a build script or external tool from opening the network. OS-level network denial and declared filesystem input tracing are part of the proposed qualification. [S61, S62]

Go requires go.mod/go.sum plus the resolved module graph, vendored or pre-staged module bytes, the exact toolchain, build tags and environment, and any cgo native closure. go.sum is an integrity list, not a complete lock of every effective build input. Toolchain auto-download and module/proxy behavior must be explicitly controlled in the isolated qualification. Vendor metadata, actual build graph and included module/source hashes must agree. [S63]

Any candidate can in principle attempt an offline build; which actual Recursion artifact succeeds remains unknown. An existing locally warm cache is not an air-gapped closure test. The qualification starts from a clean declared image with only the staged manifest content and records denied network attempts as failures, including telemetry and bootstrap downloads.

### ReleaseId and SPDX 3 evidence

SPDX 3.0.1 is the required SBOM version named in the handoff. A JSON document called “SBOM” is not enough. Validate its syntax and graph/profile semantics using a pinned validator, including the declared root artifacts and relationships. The Software Sbom class is the standard’s software bill-of-materials representation. [S64]

Proposed minimum release bundle: core dependency-lock digest; separate optional-edition/adapter lock digests; source and toolchain archive hashes; build recipe and environment manifest; build-provenance statement and digest; SPDX 3.0.1 document and digest; unsigned executable/package digests; signed package and detached-signature/verification evidence where applicable; license/notice bundle; offline build log; independent rebuild comparison; corpus/fixture acceptance records; and explicit unresolved exceptions. Bind these to the approved product ReleaseId encoding only after its operative definition is retrieved locally.

SLSA provenance distinguishes build definition and run details and can carry source/material/output identities. Producing a statement does not establish a particular SLSA level, trusted builder isolation or truth of the recorded inputs. The proposed test compares provenance subject hashes to actual delivered bytes and verifies that a second reviewer can trace every input to the closure. [S65]

A reproducible build recreates bit-identical specified artifacts from the same source, environment and instructions. Set the comparison boundary explicitly: unsigned executable bytes, packaged runtime tree, archive metadata and deterministic generated assets. Signing/timestamping can change bytes after that boundary; retain both identities and verify the signature separately. Reproducibility does not itself establish trustworthy source, a correct compiler, absence of malicious dependencies or operational safety. [S66]

Code-signability is packaging/platform capability, not a language award. On Windows, verify that the selected PE/package format can be signed and verified through the approved signing process. SignTool documents signing/verification operations; using it successfully would not prove runtime correctness. Real signing-key access and production signing are outside this research session and need appropriate later authorization. [S67]

## Decision rule and falsifiers

### Hard floors precede all tradeoffs

Only independently accepted floor-passers enter the resource comparison. A fast arm with a failed safety, privacy, deterministic-byte, authority, replay or release-evidence floor is rejected for that artifact/profile. Unknown floors block qualification. A missing Windows result cannot be compensated by an excellent Linux result if both platforms are required.

The Owner must preregister absolute ceilings and practical improvement margins for the specific decision: privileged kernel, daemon/broker, or upstream-wrapper topology. Required fields include admission p99/p999 ceiling at specified offered loads, startup requirement, group memory ceiling and acceptable unexplained slope, CPU/I/O/resource envelope, cancellation/quiescence requirement, packaging constraints, closure/license/security policy and reproducibility target. This report deliberately supplies no made-up numeric performance budgets.

Use a Pareto comparison with uncertainty. Candidate A may be declared a practically superior option to B only when both pass all floors and A meets all required ceilings, is noninferior within the Owner’s allowed margin on every declared primary metric/profile, and improves at least one declared decision-relevant metric by the preregistered minimum with simultaneous confidence support. If the Owner instead wants lexicographic priorities, those priorities must be written before results; ties and tradeoffs remain visible. Neither method uses a weighted composite.

A result can support an Owner choice without proving universal superiority. For example, better memory under the approved coordinator profile says nothing about unrelated model workloads, different storage/OS profiles or unlimited concurrency. Engineering effort and operational familiarity can be separate Owner considerations, but cannot be smuggled into a numeric performance score or used to waive hard floors.

Explicit no-selection triggers include: no floor-passer; any required floor unknown; stale/unverified essential pin; missing approved byte corpus; unqualified host/accounting; missing Owner thresholds; incompatible workloads/durability; unexplained reproducibility difference; intervals crossing practical margins; meaningful resource tradeoffs without Owner priorities; insufficient tail or soak exposure; disputed independent review; and latest scope clarification not reconciled with the implemented contract. No-selection is a completed decision outcome, not an excuse to fill gaps with intuition.

### Candidate adoption and rejection rules

| Candidate | Conditional adoption case | Named competing option | Decisive falsifier and what the rule does not prove |
|---|---|---|---|
| CPython GIL | If the approved topology satisfies the native-kernel constraint, all floors pass and measured orchestration economics meet Owner ceilings | Rust core with typed Python adapters; Go daemon | Reject exact arm on any byte/epoch/ownership failure or ceiling breach. Passing does not prove Python is an appropriate privileged core outside that topology |
| CPython FT | If actual disabled-GIL execution, full extension closure and separate Windows/Linux floors pass, and measured gain is practically meaningful | Same CPython release with GIL; Rust/Go native component | Re-enabled GIL invalidates FT identity; unsafe extension mutation, no practical gain or worse required tails falsifies adoption case. Parallel throughput does not prove admission correctness |
| Python 3.14 sensitivity | If a separately pinned pair resolves a specific 3.13 limitation and passes identical required evidence | Preserved 3.13 pair; Rust/Go arms | A new interpreter change that breaks bytes, extension ABI or ceilings rejects it. Sensitivity results do not retroactively validate 3.13 |
| Rust | If reviewed safe/unsafe boundaries, deterministic protocol, packaging and measured resource ceilings all qualify | Go kernel/daemon; approved Python topology | Any unsafe/FFI breach, incorrect cancellation, irreproducible closure or no practical advantage falsifies the corresponding case. Compile-time guarantees do not prove business semantics |
| Go pure | If the locked pure-Go closure, JCS admission, cooperative cancellation and measured GC/tail profile qualify | Rust; Go cgo with matched SQLite semantics | Any goroutine/epoch leak, byte mismatch, tail/heap ceiling breach or missing native capability falsifies adoption. Static packaging does not prove absence of dependencies |
| Go cgo | If required native functionality or measured benefit outweighs only Owner-approved costs while all floors pass | Pure-Go binding; Rust native implementation | A cancellation/ownership defect, untracked native allocation, nonportable build or failing offline closure rejects it. Native calls do not prove equal database semantics |
| Python importing PyO3 | If the bridge isolates a measured costly operation with correct ownership and meaningful whole-topology benefit | All-Rust core; unbridged Python | Callback/reentrancy error, GIL-mode drift, conversion cost erasing benefit or combined-closure failure falsifies case. Fast empty calls do not predict real payload cost |
| Rust embedding Python | If embedding preserves the small privileged boundary and required script/harness behavior with qualified lifecycle/accounting | Separate Python process via typed IPC; pure Rust | Uninterruptible embedded work preventing required quiescence, ABI/lifecycle failure or accounting gap rejects. One process does not imply one failure domain is desirable |
| Single executable packaging | If the exact package meets startup, install, offline and reproducibility floors without hidden extraction/helpers | Multi-file installation with declared runtime | Missing asset, write-restricted launch failure, extraction cost or signing/rebuild mismatch falsifies packaging claim. Packaging cannot select a runtime |

The native process plus typed IPC option is a legitimate competing topology for any in-process hybrid. It trades an explicit transport/serialization boundary for clearer containment, but its latency, memory, process count and failure recovery remain unknown until measured. A separate process must still be included in group accounting; isolation is not permission to move costs out of sight.

## Local execution handoff

The Owner has said local agent sessions will execute the remaining tests and checks. The following list is the exact unfinished work. Nothing in this section claims that those sessions have started or that these tests ran here. Local implementation and execution must respect the Owner’s latest standalone-v3 scope, protected decisions and normal authorization limits.

### Owner inputs before execution

O1. Confirm whether the decision is historical replication or a prospective refreeze, and approve the exact runtime/patch/build/topology arms. Resolve the CPython September 30 supersession and the Rust October 1 release explicitly.

O2. Reconcile the retired-Hermes wording and define the current v3 authority boundary, including which component owns admission, what “native” permits for each arm, and which upstream-harness capabilities are in scope. Native and wrapper/orchestrator profiles must both be represented.

O3. Accept or replace FU03’s candidate schema/refusal registry and literal corpus through the proper Owner process. Confirm pause-complete semantics, duplicate receipt precedence, fresh dispatch fencing and replay behavior. No local agent may silently adopt a proposed wire/core format as an accepted product decision.

O4. Select actual Windows and Linux test profiles and approve the resource envelope, isolation/security settings and any installation/configuration changes. Complete coordinator-small occupancy/workload parameters without using undisclosed private inventory in public artifacts.

O5. Set product ceilings, practical margins, priority/tradeoff policy, reproduction target, permitted exposure/cost and independent reviewer. Ratify or revise the proposed 30-run tail and three-week-equivalent-per-profile soak design before results are seen.

### Executable local work items

| Item | What the local session must execute | Prerequisite | Evidence to retain | Pass condition or stop |
|---|---|---|---|---|
| L01 Recover obligations | Read operative E-FHAR2-102/108 and current v3 authority/spec documents; map each clause to floors | O2 and authorized repository access | Clause-to-test matrix with versions/digests and explicit conflicts | Stop on unresolved conflicting accepted decisions; do not edit protected authority files |
| L02 Freeze public artifacts | Retrieve authentic exact toolchain/source artifacts and signatures; create version/feature/ABI manifest | O1 | Verified artifact hashes, publisher evidence and selected build flags | Any unavailable/unverifiable required artifact blocks that arm |
| L03 Accept corpus | Materialize reviewed FU03 literal vectors/registry/checker, verify hashes and independent oracle provenance | O3 | Corpus manifest, literal IDs, expected bytes, reviewer acceptance | Missing/unreviewed corpus blocks every candidate |
| L04 Qualify hosts | Execute FU04 clock, process-tree containment, storage/terminal and accounting fixtures on W/L | O4 | profile_key, fixture results, counters/drop records, qualification verdicts | Unknown/rejected profile cannot enter primary comparison |
| L05 Implement test harness | Build language-neutral driver and per-arm typed adapter/reducer only within approved architecture | L01–L04 and separate local implementation authority | Reviewed source diffs, interface tests and dependency audit | Stop on scope drift, provider calls or hidden candidate-specific semantics |
| L06 Resolve real closure | Lock SQLite/JCS/crypto/PTY/MCP/HTTP roles, target features and build/runtime/native inputs | O1/O2 and L05 design review | Full dependency graph, license notices, advisory applicability and hashes | Unknown essential dependency or unauthorized license/security exposure blocks qualification |
| L07 Offline rebuild | Build from clean staged closure with network denied; independently rebuild exact comparison target | L06 | Build/provenance logs, SPDX 3.0.1 validation, unsigned-byte comparison | Any undeclared input/download or unexplained difference blocks HF10/11 |
| L08 Run exact floors | Execute every FU03 normative vector and HF00–HF13 applicable pre-performance tests on both hosts | L03–L07 | Exact outputs/refusals, trace verdicts, mutant/fault evidence, independent review | One valid byte/safety failure rejects arm; invalid harness trace is inconclusive |
| L09 Exercise races | Run two-thread and two-process barrier schedules, reentrant callbacks and diagnostic race/native builds | L08 harness validity | Interleavings, linearization/epoch records, compiler diagnostics and sanitizer coverage gaps | Double commit, stale dispatch or ownership breach rejects |
| L10 Exercise cancellation | Run every pause/cancel cutpoint, detached/blocking tasks, helpers/grandchildren and restart/resume cases | L04, L08, O3 pause semantics | Ownership registry, terminal/join/reap evidence and synthetic effect statuses | Claimed quiescence with surviving capability rejects |
| L11 Calibrate collection | Execute empty controls, timer/collector overhead and fixed pilot algorithm | L08 floor pass and O5 | Pilot-only data, common load grid, frozen sampling/instrumentation parameters | Contaminated/incomplete attribution blocks main measurements |
| L12 Run performance | Execute randomized W00–W06 with identical schedules and required tail samples | L11 final manifest | Raw timestamps/counters, outcomes/censoring, block randomization and drift checks | Do not rank arms that fail floors, required sample counts or accounting |
| L13 Run soak | Execute W07/W08, declared continuous exposure, fixed retention/churn/fault schedule | L12 and authorized exposure | Full time series, invariant failures, resource ownership and final replay | Safety failure stops arm; incomplete exposure remains unqualified |
| L14 Verify packaging | Test offline install/start/upgrade rollback scope, asset availability and code-signability using test credentials where allowed | L07 and packaging contract | Installed tree/hashes, extraction/startup evidence, signature verification target | Real signing/auth changes require separate approval; missing assets reject package |
| L15 Analyze independently | Apply frozen interval/multiplicity/Pareto rules; verify claim/result traceability | L12–L14 | Reproducible analysis recipe, all exclusions and independent acceptance report | Missing ceilings or unresolved tradeoffs produces no-selection |
| L16 Present Owner decision | Deliver evidence by kernel, daemon/broker and wrapper topology, with competing options and limits | L15 | Accepted result bundle and explicit decision record | Only Owner selects or declines to select; implementer PASS is insufficient |

The local test harness command surface should expose validate-manifest, verify-corpus, qualify-host, verify-closure, run-floors, calibrate, run-matrix, run-soak, analyze and package-evidence as logical operations. These are interface names to implement, not claims that repository commands already exist. Each command must refuse missing digests or approvals, emit machine-readable status and preserve raw evidence. A proposed common exit taxonomy is 0 completed with result, 2 precondition unmet, 3 harness/trace invalid, 4 candidate floor failure and 5 interrupted/incomplete; the final local implementation must reconcile this with existing conventions before freeze.

The acceptance bundle should contain experiment_manifest, source_ledger, host_profiles, corpus_manifest, dependency_locks, SPDX/provenance, raw_events, raw_counters, trial_index, invalid_trials, floor_results, soak_results, analysis, independent_review and owner_decision records. These are logical artifact names, not private filesystem paths. Raw artifacts may contain sensitive local infrastructure details and must remain in the authorized local environment; any public summary must be separately sanitized.

### Completion gate disposition

Candidate release existence and dates are researched; binary/host/closure pins remain explicitly unverified. Byte-identical determinism is not demonstrated here and remains L08. Each concurrency/cancellation claim has a named failure mode and executable local fixture. Tail/memory/FFI/packaging cells are unknown with explicit denominators and collection rules. E-FHAR2-102/108 traceability is provisional until L01 retrieves the operative clauses. Hard floors precede ranking. Every adoption case has a competing option and falsifier. No language or hybrid is selected.

The report does not modify protected product paths or accepted Owner decisions. It contains public sources, synthetic interface proposals and no credentials or private infrastructure identifiers. Artifact editorial/privacy checks concern this report only and do not substitute for product privacy/security verification.

## Source pinned claim ledger

The ledger pins claims to primary publishers and observed versions or explicit observation dates. Initial retrieval occurred 1 October 2026 UTC; S68 and S69 were verified or rechecked on 2 October 2026 UTC. “Live” means the URL can change; no immutable content digest is claimed. These live pages must be archived by revision/hash before local freeze. Confidence H means high confidence in the bounded documentary statement; M means a documented mechanism whose exact selected-build applicability remains unresolved. None is confidence in a whole-product pass.

Expiry triggers: R = new relevant upstream release/advisory or any arm refreeze; B = selected build/ABI/feature/library differs or exact snapshot unavailable; P = host/kernel/OS/security/accounting profile changes; C = protocol/corpus/refusal contract changes; V = new specification version/erratum or validator change; A = analysis design/measurement assumptions change. “Expiry” means revalidation is required, not that a historical release date stops being true.

| ID and consequential claim | Primary source | Version or date pin | Classification and confidence | Expiry |
|---|---|---|---|---|
| S01 CPython 3.13.15 exists and is a historical maintenance release | [Python 3.13.15 release](https://www.python.org/downloads/release/python-31315/) | Release 2026-08-05 | Source documented, H | R/B |
| S02 CPython 3.13.16 supersedes it and lists security changes | [Python 3.13.16 release](https://www.python.org/downloads/release/python-31316/) | Release 2026-09-30 | Source documented, H; exposure unverified | R/B |
| S03 Python 3.14.8 is an available sensitivity release | [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/) | Release 2026-09-30 | Source documented, H | R/B |
| S04 Rust 1.98.1 fixes the described earlier vtable miscompilation | [Rust 1.98.1 announcement](https://blog.rust-lang.org/2026/09/03/Rust-1.98.1/) | Release 2026-09-03 | Source documented, H | R/B |
| S05 Rust 1.99.0 was announced after the historical freeze | [Rust 1.99.0 announcement](https://blog.rust-lang.org/2026/10/01/Rust-1.99.0/) | Release 2026-10-01 | Source documented, H | R/B |
| S06 Go 1.27.1 release date and Go branch support policy | [Go release history](https://go.dev/doc/devel/release) | 1.27.1, 2026-09-01; policy live | Source documented, H | R/B |
| S07 Official Go listing exposes target files and checksums | [Go download metadata](https://go.dev/dl/?mode=json) | Observed go1.27.1, 2026-10-01 | Source documented, H; selected archive unknown | R/B |
| S08 FT build and actual GIL state differ; container locks are not a blanket guarantee | [Python free threading guide](https://docs.python.org/3.13/howto/free-threading-python.html) | Observed 3.13.16 documentation | Source documented, H for guide; M for 3.13.15 applicability | R/B |
| S09 FT C extensions need explicit thread-safety and borrowed-reference care | [Python free threading extension guide](https://docs.python.org/3.13/howto/free-threading-extensions.html) | Observed 3.13.16 documentation | Source documented, H/M | R/B |
| S10 Canonical JSON rules are protocol obligations | [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) | June 2020, sections 3.1–3.2 and Appendix B | Source documented, H | V/C |
| S11 Python json defaults are not strict JCS admission | [Python json](https://docs.python.org/3.13/library/json.html) | Observed 3.13.16 documentation | Source documented, H/M | R/B/C |
| S12 Rust map traversal alone is not a JCS contract | [Rust HashMap](https://doc.rust-lang.org/std/collections/struct.HashMap.html) and [BTreeMap](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html) | Live standard-library documentation, 2026-10-01 | Source documented ordering; JCS implication inferred, H/M | R/B/C |
| S13 serde_json map backing depends on feature selection | [serde_json map](https://docs.rs/serde_json/latest/serde_json/map/index.html) | Observed 1.0.151, release date unverified | Source documented, H | R/B |
| S14 Go jsontext offers JCS canonicalization with option/numeric caveats | [Go jsontext](https://pkg.go.dev/encoding/json/jsontext@go1.27.1) | go1.27.1, 2026-09-01 | Source documented, H | R/B/C |
| S15 Go v1 preserves historical compatibility behavior | [Go encoding/json v1](https://pkg.go.dev/encoding/json@go1.27.1) | go1.27.1, 2026-09-01 | Source documented, H | R/B/C |
| S16 Go v2 exposes a different semantic/options surface | [Go encoding/json v2](https://pkg.go.dev/encoding/json/v2@go1.27.1) | go1.27.1, 2026-09-01 | Source documented, H | R/B/C |
| S17 Send/Sync are scoped safety contracts, including unsafe obligations | [Rustonomicon Send and Sync](https://doc.rust-lang.org/nomicon/send-and-sync.html) | Live book observed 2026-10-01; exact release snapshot unverified | Source documented, H/M | R/B |
| S18 Rust undefined behavior boundaries still matter at unsafe/FFI edges | [Rust Reference undefined behavior](https://doc.rust-lang.org/reference/behavior-considered-undefined.html) | Live reference observed 2026-10-01 | Source documented, H/M | R/B |
| S19 Go shared mutable data requires synchronization | [Go memory model](https://go.dev/ref/mem) | Live official model observed 2026-10-01 | Source documented, H | R/B |
| S20 Go race detection depends on exercised paths and supported instrumentation | [Go race detector](https://go.dev/doc/articles/race_detector) | Live official documentation observed 2026-10-01 | Source documented, H/M | R/B/P |
| S21 CPython GIL/thread-state mechanics do not supply an application transaction | [CPython initialization and threads](https://docs.python.org/3.13/c-api/init.html) | Observed 3.13.16 documentation | Mechanics source documented; transaction implication inferred, H/M | R/B/C |
| S22 asyncio task ownership and cooperative cancellation have limits | [Python coroutines and tasks](https://docs.python.org/3.13/library/asyncio-task.html) | Observed 3.13.16 documentation | Source documented, H/M | R/B |
| S23 PyO3 supports extension and embedding topologies; actual pairing is unselected | [PyO3 API](https://docs.rs/pyo3/latest/pyo3/) and [free threading guide](https://pyo3.rs/main/free-threading.html) | API observed 0.29.3; main guide live; release date unverified | Source documented capability, M for selected pairing | R/B |
| S24 cgo adds C toolchain and pointer/ABI obligations | [Go cgo](https://pkg.go.dev/cmd/cgo) | Observed go1.27.1 documentation | Source documented, H/M | R/B/P |
| S25 ThreadSanitizer is a scoped diagnostic, not exhaustive proof | [LLVM ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html) | Live official LLVM documentation, 2026-10-01; tool build unknown | Source documented, H/M | R/B/P |
| S26 AddressSanitizer covers specific memory error classes | [LLVM AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html) | Live official LLVM documentation, 2026-10-01; tool build unknown | Source documented, H/M | R/B/P |
| S27 Dropped Tokio JoinHandle detaches; started blocking tasks resist abort | [Tokio JoinHandle](https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html) | Observed Tokio 1.53.1; exact release date unverified | Source documented, H/M | R/B |
| S28 CancellationToken signals and propagation do not form a transaction | [tokio util CancellationToken](https://docs.rs/tokio-util/0.7.19/tokio_util/sync/struct.CancellationToken.html) | tokio-util 0.7.19; release date unverified | Source documented, H | R/B |
| S29 Go context cancellation does not wait for completion | [Go context](https://pkg.go.dev/context) | Observed go1.27.1, 2026-09-01 | Source documented, H | R/B |
| S30 Histograms have declared range and precision | [HdrHistogram project](https://hdrhistogram.github.io/HdrHistogram/) | Live project documentation, 2026-10-01 | Source documented, H; overhead on hosts unknown | B/A |
| S31 CPython cyclic GC supplements reference counting | [Python gc](https://docs.python.org/3.13/library/gc.html) | Observed 3.13.16 documentation | Source documented, H/M | R/B |
| S32 Go runtime metrics define specific histogram/counter semantics | [Go runtime metrics](https://pkg.go.dev/runtime/metrics@go1.27.1) | go1.27.1, 2026-09-01 | Source documented, H | R/B/A |
| S33 Go GC tradeoffs and memory limits need actual workload measurement | [Go GC guide](https://go.dev/doc/gc-guide) | Live official guide, 2026-10-01 | Source documented mechanisms, H/M | R/B/A |
| S34 Linux cgroup accounting is hierarchical and profile-dependent | [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) | Live kernel documentation, 2026-10-01; selected kernel unknown | Source documented, H/M | P/B |
| S35 Resident, proportional and private memory measures differ | [Linux proc filesystem](https://www.kernel.org/doc/html/latest/filesystems/proc.html) | Live kernel documentation, 2026-10-01 | Source documented, H/M | P/B |
| S36 Windows Jobs group processes with membership/breakaway semantics | [Windows Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) | Live Win32 documentation, 2026-10-01; host build unknown | Source documented, H/M | P/B |
| S37 Working set and private usage are distinct Windows fields | [PROCESS_MEMORY_COUNTERS_EX](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex) | Live Win32 documentation, 2026-10-01 | Source documented, H/M | P/B/A |
| S38 Job accounting must use the supported information classes | [QueryInformationJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject) | Live Win32 documentation, 2026-10-01 | Source documented, H/M | P/B/A |
| S39 Binomial sampling assumptions constrain tail-count inference | [NIST binomial distribution](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366i.htm) | NIST handbook page observed 2026-10-01 | Source documented model; proposed application inferred, H | A |
| S40 sqlite3 binding exposes thread and transaction settings | [Python sqlite3](https://docs.python.org/3.13/library/sqlite3.html) | Observed 3.13.16 documentation | Source documented, H/M | R/B |
| S41 APSW is an alternative binding inventory entry | [APSW documentation](https://rogerbinns.github.io/apsw/) | Observed 3.53.4.0; date unverified | Source documented availability, H; closure unknown | R/B |
| S42 rusqlite wraps native SQLite and exposes feature-dependent APIs | [rusqlite documentation](https://docs.rs/rusqlite/latest/rusqlite/) | Observed 0.40.2; date unverified | Source documented, H; closure unknown | R/B |
| S43 modernc SQLite is a distinct Go dependency option | [modernc SQLite metadata](https://pkg.go.dev/modernc.org/sqlite) | Observed v1.60.1, 2026-09-29; BSD-3-Clause metadata | Source documented, H; closure unknown | R/B |
| S44 mattn SQLite is a cgo-based dependency option | [mattn go sqlite3](https://pkg.go.dev/github.com/mattn/go-sqlite3) | Live package documentation, 2026-10-01; selected pin unknown | Source documented capability, M | R/B |
| S45 Python rfc8785 is a possible canonicalizer, not selected | [rfc8785 project metadata](https://pypi.org/project/rfc8785/) | Live registry metadata, 2026-10-01; selected pin unknown | Source documented availability, M | R/B/C |
| S46 serde_jcs is a possible Rust canonicalizer, not selected | [serde_jcs](https://docs.rs/serde_jcs/0.2.0/serde_jcs/) | 0.2.0; release date unverified | Source documented availability, H; conformance unknown | R/B/C |
| S47 Python cryptography is a candidate cryptographic dependency | [cryptography documentation](https://cryptography.io/en/latest/) | Latest page observed 51.0.0-dev1; no stable package pin selected | Source documented availability, M | R/B |
| S48 rustls is TLS infrastructure with provider choices | [rustls documentation](https://docs.rs/rustls/latest/rustls/) | Live crate documentation, 2026-10-01; selected pin unknown | Source documented capability, M | R/B |
| S49 Go includes an Ed25519 API if that algorithm is approved | [Go crypto ed25519](https://pkg.go.dev/crypto/ed25519@go1.27.1) | go1.27.1, 2026-09-01 | Source documented, H; algorithm choice unmade | R/B/C |
| S50 portable-pty supplies a cross-platform API option | [portable pty](https://docs.rs/portable-pty/latest/portable_pty/) | Observed 0.9.0; release date unverified | Source documented, H; OS qualification unknown | R/B/P |
| S51 creack pty is a Unix PTY option | [creack pty](https://pkg.go.dev/github.com/creack/pty) | Observed v1.1.24, 2024-10-31; MIT metadata | Source documented, H; Windows path unknown | R/B/P |
| S52 Official MCP SDKs exist for all three ecosystems | [MCP SDK documentation](https://modelcontextprotocol.io/docs/2026-07-28/sdk) | Spec path 2026-07-28, observed 2026-10-01 | Source documented availability, H; pins/coverage unknown | R/B/C |
| S53 HTTPX is a Python HTTP option | [HTTPX documentation](https://www.python-httpx.org/) | Live project documentation, 2026-10-01; selected pin unknown | Source documented availability, M | R/B |
| S54 reqwest is a Rust HTTP option with feature/provider choices | [reqwest documentation](https://docs.rs/reqwest/latest/reqwest/) | Live crate documentation, 2026-10-01; selected pin unknown | Source documented availability, M | R/B |
| S55 Go net/http is a standard-library HTTP option | [Go net http](https://pkg.go.dev/net/http@go1.27.1) | go1.27.1, 2026-09-01 | Source documented availability, H; product configuration unknown | R/B |
| S56 SQLite threading depends on compilation and initialization/connection modes | [SQLite threading](https://www.sqlite.org/threadsafe.html) | Live official documentation, 2026-10-01 | Source documented, H/M | R/B |
| S57 SQLite core public-domain statement does not license every binding | [SQLite copyright](https://www.sqlite.org/copyright.html) | Live official statement, 2026-10-01 | Source documented, H; whole-closure posture unverified | R/B |
| S58 Advisory ranges can be recorded without proving product exposure | [OpenSSF OSV schema](https://ossf.github.io/osv-schema/) | Live schema documentation, 2026-10-01 | Source documented format; exposure inference limited, H/M | V/R/B |
| S59 SQLite vulnerability applicability needs usage context | [SQLite vulnerabilities](https://www.sqlite.org/cves.html) | Live official advisory discussion, 2026-10-01 | Source documented, H; actual exposure unknown | R/B |
| S60 pip hashes constrain artifacts but not all build/runtime inputs | [pip secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/) | Observed pip 26.2.1 documentation | Source documented features; closure implication inferred, H/M | R/B |
| S61 Cargo vendor stages crate sources and frozen combines locked/offline | [Cargo vendor](https://doc.rust-lang.org/cargo/commands/cargo-vendor.html) | Live Cargo book, 2026-10-01 | Source documented, H/M | R/B |
| S62 Cargo build compiles selected packages/features and dependencies | [Cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html) | Live Cargo book, 2026-10-01 | Source documented, H/M | R/B |
| S63 Go module/vendor metadata must be paired with effective build inputs | [Go modules reference](https://go.dev/ref/mod) | Live official reference, 2026-10-01 | Source documented mechanisms; completeness requirement inferred, H/M | R/B |
| S64 SPDX 3.0.1 has a Software Sbom representation | [SPDX 3.0.1 Sbom](https://spdx.github.io/spdx-spec/v3.0.1/model/Software/Classes/Sbom/) | SPDX 3.0.1 | Source documented, H | V |
| S65 Provenance describes build definition/run details, not automatic trust | [SLSA provenance](https://slsa.dev/spec/v1.1/provenance) | SLSA 1.1 | Source documented structure; trust limit inferred, H | V/B |
| S66 Reproducibility is scoped bit-identical reconstruction | [Reproducible Builds definition](https://reproducible-builds.org/docs/definition/) | Live project definition, 2026-10-01 | Source documented, H | V/B |
| S67 Signing and verification are distinct release operations | [Microsoft SignTool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool) | Live Microsoft documentation, 2026-10-01; selected SDK unknown | Source documented, H/M | R/B/P |
| S68 Secure raw-input admission and negative-zero serialization are distinct | [RFC 8785 errata](https://www.rfc-editor.org/errata/rfc8785) | Technical erratum 7920, verified 2024-05-15; checked 2026-10-02 | Source documented recommendation, H; adopted profile unknown | V/C |
| S69 Python 3.14 free threading has upstream supported optional status; JIT remains a separate experimental factor | [Python 3.14 changes](https://docs.python.org/3.14/whatsnew/3.14.html) | Observed 3.14.8 documentation, rechecked 2026-10-02 | Source documented upstream status, H; product qualification unknown | R/B |

### Derived and unresolved claim register

| Claim | Basis and explicit model | Classification and confidence | Expiry or required evidence |
|---|---|---|---|
| No candidate is selected | Owner-reserved decision in brief and latest scope clarification; no target execution | Source supplied scope and inference, H | Only an explicit later Owner decision changes this |
| Actual byte determinism is unknown for every arm | No candidate implementation/corpus execution evidence supplied | Unverified, H confidence in missing evidence | L03/L08 plus independent acceptance |
| Each main language could express the required transition contract | M1 assumes correct strict parsing, serialization, single admission owner, epoch checks and contained tasks | Inferred, M; non-quantitative | Any impossible required capability or concrete valid counterexample falsifies |
| No runtime primitive alone establishes pause-complete | Compound protocol includes epoch commit, task ownership, joining, descendant containment and effect reconciliation | Inferred from S08/S17–S29 and the proposed contract, H | Contract change or demonstrated stronger primitive with complete scope |
| All performance and closure values remain unknown | No target builds, measurements, selected stack or actual host profiles | Unverified, H confidence in status | Valid local result bundle with denominators/digests |
| Proposed tail sample count produces expected tail counts only under M2 | N×(1−p), independent stationary observations | Explicitly modelled M2, H mathematically; real assumptions unverified | Autocorrelation/nonstationarity; use clustered intervals |
| A floor-passing runtime can still yield no-selection | No weighted composite; absent ceilings, overlapping practical intervals or unresolved tradeoffs | Proposed decision policy, Owner acceptance pending | O5 and independent reviewed result |
| Frozen host pair is not yet defined | FU04 shared profile contract; no actual inventory authorized or supplied here | Unverified, H | L04 qualified exact W/L profiles |
| Real dependency closure cannot be inferred from ecosystem labels | Feature/target/native/build choices unresolved | Inferred, H | L06 exact locks and L07 isolated build |
| SPDX/provenance/reproducibility do not certify correctness or absence of vulnerabilities | Each evidence object has a narrower scope | Inferred from S58/S64–S66, H | No automatic expiry; revisit if the claim scope changes |

## Open Owner decisions and final disposition

The remaining Owner decisions are the purpose and exact version freeze; eligible native/embedded/wrapper topologies; final FU03 core and refusal contract; actual qualified Windows/Linux profiles; coordinator-small workload parameters; product ceilings and practical margins; pause-complete requirements for blocked external work; release reproducibility/signing target; and authorized local execution exposure with independent reviewer.

The current result is a source-backed no-selection plus a fully specified path to decision evidence. The next useful action is the bounded local sequence L01–L16 after O1–O5 are supplied. None of those empirical results can be inferred from this report’s length, citation count or the apparent strength of any language’s design.

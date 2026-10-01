# Domain A — kernel, language and platform (synthesis)

## Scope and lanes

This domain gathers the lanes that decide how the privileged deterministic kernel is shaped, what
runtime and persistence it may be built on, which operating-system contracts it must qualify against,
how its inter-process and terminal boundaries are framed, and how its configuration is modelled. The
seven per-lane syntheses below were produced under the 2026-09-30 evidence freeze. Every one carries
the same status: research evidence, not a decision; not independently verified by Recursion; no rerun.
No lane ran a benchmark, model checker, fault fixture, chaos matrix, implementation, deployment, or
repository mutation, and several explicitly preserve an existing no-selection result (language, store,
renderer, IPC and serialization libraries, consensus, container runtime, backup tool, observability
stack, parser).

- DS-18 — language and runtime (Wave A handoff; raw report; delivered in the Wave A run).
- DS-19 — operating-system platform behavior (Wave A handoff; delivered in the Wave B run).
- DS-20 — Linux service topology and enterprise scaling (Wave A).
- DS-21 — canonical state store and persistence faults (Wave A).
- DS-22 — formal model and conformance vectors (Wave A).
- DS-23 — IPC, process broker and terminal protocol (Wave B).
- DS-13 — configuration architecture and operator control (Wave C).

The lanes come from different waves and answer different handoffs, so their evidence classes are not
uniform; the clustering is thematic, not a claim that they ran as one campaign.

## Lane digests

### DS-18 — language and runtime

**Bottom line:** explicit **no-selection**; `EXP-FHAR-10` (CPython 3.13.15, Rust 1.98.1, Go 1.27.1; GIL and free-threaded as separate arms) is the decision-producing artifact, hard-floor-first then resource-ranked, no weighted composite. **Confidence/evidence:** source-documented behavior plus modelled hypotheses; resource/tail `unknown` for every candidate. **Does NOT prove:** that any candidate wins, nor any resource, latency, FFI, cold-start or dependency-closure figure.

### DS-19 — operating-system platform behavior

**Bottom line:** a **contract-first, native-semantics qualification model** — one behavior contract, qualified per pinned platform profile through native semantics and preregistered negative traces; outcomes are qualified, rejected, or `unknown`. **Confidence/evidence:** source-documented (SD) plus modelled/inferred (M); no measured cells; the report answered an unnamed subject query. **Does NOT prove:** that any OS build, kernel, terminal, filesystem, distribution, compatibility layer, SMB or NFS target is certified or even qualified.

### DS-20 — Linux service topology

**Bottom line:** **no-selection, no-deployment** — one fenced canonical writer baseline with consensus competing rather than default; a monotonic epoch rejected by every canonical transition or side-effect sink; backup decoupled from the writer lock via a consistency-defined snapshot/export; FIPS, MAC, residency and certification claims as `requires-certification`. **Confidence/evidence:** strong/source-documented authority and fencing; inferred enterprise networking; coordinator-small and preflight latency unverified. **Does NOT prove:** any topology or capacity value, and no certification; single-authority multi-node is not evidence of safe hosted multi-tenancy.

### DS-21 — canonical state store

**Bottom line:** **no store selection yet**; gate on a canonical crash/replay benchmark between segmented JSONL + CAS and **SQLite 3.53.4 WAL + `synchronous=FULL`** + identical CAS; LMDB and redb as secondary challengers, RocksDB only if LSM behavior is required, PostgreSQL only when multi-node authority is real. Serialization is not authority. **Confidence/evidence:** published behavior source-documented, consequences inferred; no Recursion workload measurements. **Does NOT prove:** any store or version safe for Recursion, exactly-once external effects, or cross-filesystem/network durability; stale `-wal`/`-shm` and Windows power-cut behavior unverified.

### DS-22 — formal model and conformance vectors

**Bottom line:** **conditional freeze** — do not freeze the four-function kernel (`decode`, `admit`, `reduce`, `derive_work_packet`) until a TLA+/TLC finite falsification model exists, all 36 mandatory reachable mutants are classified with retained counterexamples, a language-neutral byte-level vector corpus exists, and two independent implementations reproduce every vector bit-for-bit; TLA+/TLC primary, Alloy as named independent cross-check. **Confidence/evidence:** source-documented methods; design-level complete only — no model run, no mutant killed, no vector reproduced. **Does NOT prove:** that omitted dimensions are irrelevant, that the unbounded system is safe, or that any implementation refines the abstraction; calibration counts are locally reported, not reproduced.

### DS-23 — IPC, process broker and terminal protocol

**Bottom line:** **conditional adoption, not completion** — adopt the ownership model, preferred local transports (Windows named pipes; Linux/BSD pathname AF_UNIX), bounded framing, event cursors with independent byte/event credit, mandatory RESET on a replay gap, durable command-id idempotency, creation-time containment, and a separate MCP/tool boundary, but **do not declare the protocol frozen** until four blockers (version negotiation, snapshot materialization, cursor rollover, ACK-release wording) and the native chaos matrix pass. **Confidence/evidence:** source-documented plus inferred, with the cluster's only locally observed evidence — a bounded Windows Job probe where a create-suspended-then-associate gap let a child escape, while creation-time Job listing closed the tested gap. **Does NOT prove:** full descendant-tree termination, slow-client isolation, operational framing, or current MCP v2 behavior.

### DS-13 — configuration architecture

**Bottom line:** **freeze the configuration architecture, not the human syntax** — JSON Schema 2020-12 + a Recursion vocabulary → restricted I-JSON → RFC 8785/JCS bytes → a deterministic non-model resolver (explicit merge operators, typed provenance, zero model tokens) → editors emitting one typed edit command, with optimistic CAS, a command ledger and atomic desired-state commit with per-target receipts; lead syntax with restricted TOML 1.1, JSON fallback, CUE bake-off. **Confidence/evidence:** source-documented plus inferred; many `[Unverified]` items; no repository inspected. **Does NOT prove:** that any parser, syntax or serialization library is selected; the complexity vector is a candidate metric, not a measurement.

## Cross-lane consistency and contradictions

- **No-selection discipline is consistent.** DS-18 (language), DS-20 (topology and deployment), DS-21
  (store), DS-22 (construction language, store, broker transport, renderer), DS-23 (renderer,
  IPC/serialization libraries, snapshot format) and DS-13 (parser, human syntax) each reserve their
  choice to the Owner; no lane claims another's recommendation is accepted. Renderer and plugin runtime
  stay unselected in all of them (DS-18 defers the WASM/WASI 0.3 plugin-isolation evaluation; DS-13
  flags plugin-schema trust as `[Unverified]`).
- **The four-function kernel boundary, and serialization is not authority.** DS-22 names the boundary
  (`decode`, `admit`, `reduce`, `derive_work_packet`) and gates its freeze on model, mutants, vectors
  and independent implementations; DS-18 reaches the same boundary via determinism, race freedom,
  stable refusals and dependency closure. DS-22 warns a frozen boundary only gates language/store/broker
  evaluation and does not imply refinement, platform security, broker or external-effect evidence.
  DS-21 (a DB writer lock is not writer-epoch authority), DS-20 (a monotonic fencing epoch rejected
  everywhere), DS-23 (command identity bound to daemon/process epoch, stream, lease) and DS-18
  (PauseSafety as an admission/effect-fencing invariant) all pull the same way; DS-23 consumes the
  durable-append-before-projection model.
- **Determinism and canonical bytes largely agree.** DS-18 (RFC 8785/JSON canonicalization, no map
  traversal, duplicate-key rejection before object collapse, finite IEEE-754, `-0`→`0`, no NaN/∞, no
  Unicode normalization), DS-13 (restricted I-JSON + JCS, duplicate-name rejection, narrow ASCII
  identifier grammar), DS-21 (canonical ordinal event identity as the replay parity test) and DS-23
  (JCS framing) align. One presentational tension: DS-22's deterministic-CBOR + SHA-256 vector record
  is a test interchange format, not a production wire format, while DS-23's wire framing is
  length-prefixed JCS JSON; implementation must not collapse the two.
- **Atomicity vs durability.** DS-19 and DS-21 share the facts — `fsync(file)` alone does not persist
  the containing directory entry, Windows `FlushFileBuffers`/`ReplaceFileW` have distinct contracts,
  and network storage makes the guarantee local-only; DS-21's `synchronous=FULL`/`fdatasync` profiles
  apply DS-19's qualification framing.
- **Containment: agreement plus the one measurement.** DS-19 recommends a kernel containment anchor
  plus stable process identity (Job Objects; cgroup v2 with `CLONE_INTO_CGROUP` and `pidfd`) over
  process-group tree walking and stresses membership ≠ completeness; DS-23 adopts creation-time
  containment with the same distinction, and its bounded Windows probe is the domain's only locally
  observed evidence. Neither resolves nested/alternate Job behavior or privileged cgroup migration.
- **Prerequisite ordering is consistent, with one real dependency edge.** DS-22's vectors are
  language-neutral and only gate language evaluation, but DS-18's `EXP-FHAR-10` itself needs DS-22's
  byte-level corpus and refusal taxonomy first — a dependency, not a contradiction. DS-21 blocks
  Milestone 2 (canonical writer) with a crash/replay benchmark; DS-19 is a blocking prerequisite for
  the DS-23 broker and the canonical state writer; DS-20 sets service-topology and ownership
  preconditions.
- **The availability/authority contract is the shared pivot.** DS-20 says the real decision is not
  "etcd or no etcd" but whether one fenced canonical writer may be temporarily unavailable after
  coordinator loss; DS-21 ties multi-node store choice to whether multi-node availability is a v3
  requirement. Both defer to the Owner and agree consensus is not the baseline.
- **PAUSE semantics remain unresolved.** DS-13 exposes `checkpoint`/`interrupt`/`drain` but keeps the
  emergency stop outside configuration; DS-22 asks whether immediate PAUSE is the only operative
  policy; DS-23 requires separate Stop stages and an unspecified Lazy Stop timeout. The domain settles
  no single PAUSE model.

## Cross-lane dependencies

- DS-22 → DS-18: the language comparison needs language-neutral byte-level conformance vectors, a
  refusal taxonomy and a trace-validity checker first.
- DS-19 → DS-23: broker transport, containment, PTY/ConPTY teardown and watchdog semantics are defined
  in terms of OS primitives.
- DS-19 → DS-21 and DS-20: persistence and supervisor/recovery contracts derive from platform
  atomicity, clock, resource and containment behavior.
- DS-21 → DS-20: backup/snapshot/export and RPO/RTO depend on a store-agnostic consistency point.
- DS-21 → DS-18: store choice affects packaging, dependency closure and resource behavior, but the
  store question is specified language-neutrally.
- DS-13 → all: configuration schema, editions, scopes, Full Access and PAUSE-mode gating are consumed
  by every other lane, without itself deciding any of them.
- DS-20 → DS-23: node fabric and multi-node reconnect depend on the fencing/epoch and
  disconnected-node rules; DS-18 feeds the later plugin-isolation lane.

## Consolidated open Owner decisions

Aggregated from the seven lanes; none is decided here.

**Language / runtime (DS-18):** one language across kernel/daemon/broker vs an accepted second runtime;
CPython 3.13 long-term vs 3.14.7 promotion; minimum supported Windows versions; single executable vs a
signed self-contained install closure; whether a preview runtime API is ever acceptable in the
privileged base; whether Wasm's first evaluation is specifically plugin isolation; the evidence
threshold that converts a resource difference into a practical decision; the dependency-security policy
(upgrade cadence, severity tolerance, native-dependency rules).

**Store and durability (DS-21):** per-command power-loss durability vs group commit and maximum batching
delay; target local filesystems on Windows/Linux and whether SMB/NFS is forbidden; whether multi-node
canonical availability is a v3 requirement; p99 append latency, replay time, WAL/log growth, RSS and
bytes-per-million-events budgets; the durability unit; backup RPO/RTO and expiry; privacy/deletion key
scope; maximum read-observer age.

**Platform qualification (DS-19):** exact Windows build floors and Linux kernel/distribution profiles;
WSL2 as production, development, or both; canonical state on SMB/NFS in or out of scope; hostile vs
cooperative descendants; the definition of "survives power loss"; whether a suspended laptop consumes
task/lease time; first-release terminal embeddings; escaped descendant as hard failure vs recoverable
`unknown`.

**Service topology (DS-20):** whether canonical writes stay available automatically after total
coordinator loss (decides consensus necessity); authority boundary one-to-one with an OS account vs
several fenced instances per identity; backup defined entirely around a snapshot/export interface;
RPO/RTO, certificate lifetime/revocation freshness and coordinator-small SLOs; Kubernetes official vs
compatibility target; hosted multi-tenancy and its isolation threat model; node mTLS through
TLS-inspecting proxies; telemetry egress and deletion proof; which combinations need formal
certification.

**Formal model (DS-22):** duplicate-command handling (`DUPLICATE_COMMAND` vs replay); immediate PAUSE
as the only operative policy; independent verifier as distinct principal vs distinct lease/role;
deterministic-CBOR/SHA-256 as an acceptable test encoding; three-lease-epoch coverage mandatory in the
first run vs a following expansion; Owner-normative authority dimensions beyond the named six;
immutable model-run artifact identity; trace-validity checker vs machine-checked refinement map before
language comparison.

**IPC / broker (DS-23):** whether `m1b-broker/1` is immutable (exact-version-only) or a new major with
version/schema/refusal negotiation; which already-ratified contract materializes `snapshot_digest` into
verifiable bytes; cursor rollover/incarnation behavior; same-OS-user attachment vs installation
key/attestation; admitted Windows client matrix and Linux cgroup floor and behavior on a host lacking
the required profile; whether credit exhaustion stays reset-requiring; Lazy Stop timeout/escalation;
MCP/stdio numerical bounds and the command-receipt payload schema.

**Configuration (DS-13):** exact ordered lattices for `privacy_exposure` and `publication`; which of the
six authority edges need step-up authentication; whether a blocked authority-bearing request may ever
auto-activate; whether credential-binding identities are always goal-frozen or may rotate; the minimum
independent-verification invariant; which identifier classes must be ASCII-constrained; what counts as
a billing widening when engine choice changes without a budget change; visibility of retained
unsupported edition requests; Telegram vs local-terminal authentication assurance; the reversible-
migration window; whether plugins may introduce a bounded vocabulary; which adapter properties may be
`restart-required`; whether `checkpoint` is default or goal-frozen after a future PAUSE amendment.

**Renderer and plugin runtime:** both remain unselected across every lane.

## Domain gaps and open unknowns

- **No experiment in this domain was run.** `EXP-FHAR-10` was not run; no store crash/replay benchmark;
  no TLA+ model or mutant kill; no OS fault fixtures; no broker chaos matrix; no configuration
  conformance corpus.
- **DS-18:** p99/p999 latency, RSS level and slope, FFI cost, artifact size, cold start, dependency
  closure and 24/7 behavior are unmeasured for every candidate; the real library closure (SQLite
  binding, JCS, crypto, PTY/ConPTY, MCP, HTTP) is unselected.
- **DS-19:** no measured claims at all; ConPTY teardown, cgroup/OOM, rename/fsync durability, lock
  release and supervisor races are unmeasured on this project's hardware and builds; WSL, compatibility
  shells, embedded terminals, SMB and NFS remain unqualified and gain nothing by analogy.
- **DS-20:** the 2-vCPU/4-GiB profile is a target, not a demonstrated capacity point; the preflight
  "seconds" property is unverified; no numeric SLO, watchdog timeout or recovery decomposition is
  established.
- **DS-21:** no Recursion workload measurement; throughput/latency/RSS/total bytes unknown by design;
  stale `-wal`/`-shm`, cross-filesystem/network durability and Windows power-cut behavior unverified.
- **DS-22:** unbounded state space, digest abstraction, kernel implementation, storage adapter, broker
  delivery, OS containment, external-effect truth, fairness/liveness, projection parity and the model
  checker itself are all labelled unproved seams.
- **DS-23:** full descendant-tree termination is `unknown`; slow-client isolation is unproven from
  schema alone; framing is unmeasured; current MCP v2 notification/backpressure is `unknown`; nested
  Job behavior, Linux cgroup migration and external-service-created work are named escape paths, not
  settled cases.
- **DS-13:** provider/engine identifier and cost-class semantics, plugin schema trust, schedule
  grammar, symlink/junction containment, adapter restart boundaries, terminal-layout grammar,
  remote-node attestation and cross-transport authentication assurance are all unverified.
- **What an architecture phase would still need:** the availability/authority contract (may the single
  canonical writer be temporarily unavailable?); a machine-readable, platform-profile-keyed
  conformance manifest and the preregistered negative traces behind it; a trace-validity checker plus
  the differential byte-vector suite; one settled PAUSE/Stop model across configuration, formal model
  and broker; and the renderer and plugin-runtime selections.

## Evidence-quality notes

- **Uniform status.** Every lane is labelled research evidence, not a decision, not independently
  verified, with no rerun, and preserves distinct evidence classes — source-documented,
  modelled/inferred, locally observed, measured, and unknown. This synthesis keeps that separation
  rather than blending it.
- **Measured evidence is absent; locally observed is nearly absent.** No lane contains a measured
  performance or fault result. The only locally observed evidence in the cluster is DS-23's bounded
  Windows Job-object probe; DS-13 explicitly has none because it inspected no repository.
- **Source-documented vs inferred.** DS-19 and DS-20 lean most on source-documented platform and
  authority facts; DS-18, DS-21, DS-22 and DS-13 mix source-documented facts with inferred
  consequences. DS-22's claims about method are source-documented, but its own outputs are design-level
  only.
- **Weak points to carry forward.** DS-18's resource/tail claims are `unknown` and historical CVE
  totals are a poor ranking metric without exposure normalization. DS-19 answered an unnamed subject
  query and several containment/durability claims still need adversarial measurement. DS-20's
  coordinator-small and preflight figures are unverified. DS-21 cannot transfer Linux durability
  results to Windows and vice versa. DS-22's prior calibration counts are locally reported, not
  reproduced. DS-23 mixes an MCP freshness flag with one small local probe. DS-13's
  configuration-complexity numbers are a candidate design metric, not a measurement.
- **Version currency is a snapshot.** Every "current" version named in this domain is current as of the
  2026-09-30 evidence freeze and must be revalidated before any experiment; exact pins are decision
  inputs, not certifications.

# Recursion v3 research synthesis — all 28 Deep Research lanes

## What this is

This file is **research evidence, not Owner decisions and not acceptance.** It consolidates the 28
per-lane Deep Research syntheses that ran under the 2026-09-30 evidence freeze into four domain
clusters and then into one document. Nothing in it is ratified, adopted, implemented or frozen, and
no lane's own PASS is acceptance.

- **Scope of consolidation.** 28 lanes in four domains: Domain A (kernel, language, platform, 7
  lanes), Domain B (authority, safety, lifecycle, 8 lanes), Domain C (operations, capacity,
  evaluation, 6 lanes), Domain D (context, interaction, product-adjacent, 7 lanes).
- **Method and evidence classes come from the lane reports.** The lanes used the Deep Research
  loop described in the Wave A methods meta synthesis: scope → plan → search → extract → re-check →
  refine → cross-check → synthesize → cite → deliver, with an evidence hierarchy and preserved
  provenance classes. This master file adds no new search and no new sources.
- **Nothing here was independently rerun.** No lane was independently verified by Recursion, no
  Deep Research output is authoritative, and every quantified figure is either a source-documented
  external finding, a sensitivity calculation, a provisional threshold, or explicitly `unknown`.
- **Evidence classes stay distinct.** Source-documented, locally observed, modelled/inferred,
  proposal/hypothesis, and unverified/`unknown` are different things and are not blended here.
  `unknown` and `unavailable` are never collapsed to zero or to a default.
- **Boundaries.** Public and synthetic sources only. No lane inspected the Recursion repository,
  ran a benchmark or model checker, called a provider, spent money, used live credentials, deployed,
  migrated, deleted, published or performed any live action.

Read this as a map of what the research collectively reached. Each finding's acceptance path runs
through the Owner and, where applicable, through an independent verifier that reruns the exact
candidate.

## Decision-first summary

These are the strongest cross-domain conclusions a reader needs first — the spine the 28 lanes
agree on. The detail and the dissent live in the domain files.

1. **Determinism and canonical bytes are the shared substrate.** Serialization must be
   deterministic and byte-stable: restricted I-JSON + RFC 8785/JCS, duplicate-name rejection before
   object collapse, no map-traversal-order dependence, finite IEEE-754 only, `-0`→`0`, no NaN/∞, no
   Unicode normalization. DS-13, DS-18, DS-21 and DS-23 arrive at this independently; DS-22's
   deterministic-CBOR + SHA-256 record is a **test interchange format**, not a production wire
   format, and must not be collapsed into DS-23's length-prefixed JCS wire framing.
2. **Serialization is not authority.** A digest, signature, transcript, summary, cache hit, room
   consensus or model confidence authenticates or represents bytes; it never grants capability.
   Authority is computed at effect-admission time from current, attributable, revalidated canonical
   state. Stated across DS-02, DS-04, DS-12, DS-15, DS-24, DS-30 and DS-32.
3. **Fencing is receiver-side.** A controller-only `paused=true`, a router-side epoch, or a written
   grant is not proof of quiescence. The recurring invariant (DS-01, DS-02, DS-04, DS-05, DS-07,
   DS-24) is a monotonic admission/fencing epoch checked **immediately before the irreversible
   boundary**, where the effect actually happens.
4. **One fenced canonical writer is the baseline.** DS-20's no-selection result is a single fenced
   canonical writer with consensus competing rather than default; DS-05 freezes the single-writer
   contract first; DS-21 makes multi-node store choice contingent on whether multi-node availability
   is a real v3 requirement. Consensus is not the baseline; a monotonic fencing epoch survives every
   canonical transition or side-effect sink considered.
5. **The four-function kernel boundary is named but not frozen.** DS-22 names `decode`, `admit`,
   `reduce`, `derive_work_packet` and gates its freeze on a TLA+/TLC finite falsification model,
   classification of all 36 mandatory reachable mutants with retained counterexamples, a
   language-neutral byte-level vector corpus, and two independent implementations reproducing every
   vector bit-for-bit. DS-18 reaches the same boundary via determinism, race freedom, stable
   refusals and dependency closure.
6. **No technology was selected.** Language, runtime, store, renderer, plugin runtime, IPC and
   serialization libraries, consensus, container runtime, backup tool, observability stack, parser
   and human configuration syntax all remain explicitly unselected. Selection is reserved to the
   Owner; the lanes produce decision inputs, challengers and benchmark designs, not picks.
7. **Honest counters are a precondition, not a nicety.** DS-26 requires provenance-qualified
   counters with `observed`/`modeled`/`inferred`/`unavailable`; a missing counter is `null` with a
   reason, never `0`. DS-06, DS-10, DS-11 and DS-25 all state they cannot calibrate until such
   counters and a pinned baseline exist.
8. **Public/synthetic boundaries were preserved everywhere.** No lane performed a live action or a
   Recursion measurement. DS-12's route matrix is a plausible-route capability snapshot, not
   Recursion's inventory; DS-15's F01–F24 fixtures did not run; DS-32's fixtures are acceptance
   targets, not tests; DS-33 is legal-risk research, not advice, and requires counsel before any
   release decision.

The aggregate posture is therefore a determinism/canonical-bytes core with receiver-side fencing and
one fenced canonical writer, a named-but-conditional four-function kernel, a measurement-first
evaluation discipline, and a deliberate refusal to select any technology until the Owner decides and
the named experiments run.

## Lane coverage

All 28 lanes. Recommendation text is faithful to each lane's bottom line; confidence/evidence is a
compressed reading of the lane's own evidence classes.

| Lane | Domain | One-line recommendation | Confidence / evidence class |
| --- | --- | --- | --- |
| DS-01 | B | Freeze the pause family around receiver-side admission fencing and mode-specific boundaries (`checkpoint`, `interrupt`, `drain`, independent emergency stop), not cancellation requests. | Source-documented primitives + inferred state machine; 28 pinned class×mode claims. |
| DS-02 | B | Full Access is an explicit capability catalog plus typed grants; effective authority is computed at effect-admission as an intersection, and delegation is monotonic attenuation. | Source-documented precedents + inferred design; implementation unproven. |
| DS-03 | B | Retain risk-scaled `V0`–`V3` verification with an explicit independence-vector record; deterministic gates are non-substitutable; use a blinded preregistered matrix. | Source-documented (high) for actor/evidence/authorship; medium/inferred for model family and tier rule; unverified for provider/account/host. |
| DS-04 | B | Keep evidence/provenance, trust tier/isolation and authority grants as three independent axes; a signature authenticates a digest but never grants authority. | Mixed source-documented/inferred/unverified; cross-runtime enforcement medium. |
| DS-05 | B | Freeze the single-writer contract first on the synthetic execution-attempt/lease aggregate; after an effect may be accepted, forward reconciliation — never relabel rollback. | Inferred with high confidence, consistent across primary sources. |
| DS-06 | C | Adopt a dual-domain adaptive min-credit controller `A(t)=min(M,P,G,R,H)` over independent integer slot credits; review credit is its own service/queue/age domain. | Mostly inferred/modelled from source-documented OS/Git facts; no measured claims. |
| DS-07 | B | Standardize a deletion-evidence contract: closed per-request copy inventory, separate key-recovery ledger, explicit predicates, derived `verified-complete`. | Source-documented + inferred evidence state machine; no measured cells. |
| DS-08 | B | Use a sealed two-layer, alias-only canary protocol; a characterization pass is not a correctness pass and `unknown` is not zero. | Inferred protocol + source-documented references; one locally observed no-start fact. |
| DS-09 | C | Freeze terminal semantic invariants before implementation: canonical event append, OS-scoped containment, stable identities, replay floor, bounded per-view credit. | Source-documented platform/standards contracts + inferred protocol; containment unverified. |
| DS-10 | C | Keep ratified Option 2 as target while treating every claimed advantage as unverified until measured; one semantic owner plus targeted ablation; hard floors precede scalars. | v2 pin and PERF-003 source-documented high; Option 2 benefit inferred/medium; ablation `unavailable`. |
| DS-11 | C | Provisional hypothesis: task-specific route suites, delegating only when decomposition value exceeds coordination cost, with first-review acceptance and false-green rate as primary endpoints. | Source-documented public literature + design inference; no local measurement. |
| DS-12 | D | Pursue a provider-neutral recovery core with provider cache/session as opportunistic accelerators only; one deterministic context governor per route epoch. | Source-documented provider docs + inferred architecture; route inventory/economics unknown. |
| DS-13 | A | Freeze the configuration architecture, not the human syntax: schema → restricted I-JSON → JCS bytes → deterministic non-model resolver; editors emit one typed edit command. | Source-documented + inferred; many `[Unverified]`; no repository inspected. |
| DS-14 | D | Strongest candidate is Option A, authority-first federation with aggregator-assisted discovery and full text behind a separate rights gate — a candidate, not adoption. | Source-documented surfaces + inferred schemas; no live provider trial. |
| DS-15 | D | `R1`: one transport-independent actor-and-authority contract with bounded step leases, canonical Head awareness and independent acceptance; `R0` is the competitor. | Supplied-brief constraints + source-documented + inferred lease/fencing; coordination benefit unverified. |
| DS-18 | A | Explicit no-selection; `EXP-FHAR-10` (CPython 3.13.15, Rust 1.98.1, Go 1.27.1) is the decision-producing artifact, hard-floor-first then resource-ranked. | Source-documented behavior + modelled hypotheses; resource/tail `unknown` for every candidate. |
| DS-19 | A | A contract-first, native-semantics qualification model: one behavior contract, qualified per pinned platform profile via native semantics and preregistered negative traces. | Source-documented + modelled/inferred; no measured cells; answered an unnamed subject query. |
| DS-20 | A | No-selection, no-deployment: one fenced canonical writer baseline with consensus competing; monotonic epoch rejected by every canonical transition or side-effect sink. | Strong/source-documented authority and fencing; inferred networking; coordinator-small and preflight latency unverified. |
| DS-21 | A | No store selection yet; gate on a canonical crash/replay benchmark between segmented JSONL+CAS and SQLite 3.53.4 WAL + `synchronous=FULL` + CAS; serialization is not authority. | Published behavior source-documented, consequences inferred; no workload measurements. |
| DS-22 | A | Conditional freeze: do not freeze the four-function kernel until a TLA+/TLC model, all 36 mutant classifications, a byte-level vector corpus and two independent implementations exist. | Source-documented methods; design-level only — no model run, mutant kill or vector reproduction. |
| DS-23 | A | Conditional adoption, not completion: adopt ownership model, transports, bounded framing, cursors, RESET-on-gap and command idempotency; do not freeze until four blockers and the chaos matrix pass. | Source-documented + inferred; one locally observed bounded Windows Job probe. |
| DS-24 | B | Recommended “Brokered Capability Intersection”: stable opaque credential references, broker-owned egress on exact compiled bytes, short leases, process containment, typed independent fields. | Source-documented + inferred consequences; entitlement/distribution/ToS unknown; no measurements. |
| DS-25 | C | Prefer verified compatible executable rollback while retaining newest state, then verified task resume or an explicit hold; five propositions never share one “recovered” bit. | Source-documented standards + inferred spec; six-mode×four-outcome matrix `unknown` in every cell. |
| DS-26 | C | Provenance-qualified adapters feeding two ledgers (attribution/quantity and financial/capacity) reconciled after normalization; authority is dimension-specific. | Source-documented provider docs + upstream-observed issue reports + inferred ledger split; no live adapter. |
| DS-30 | D | Additive convention under the authoritative `state/` tree using four roles: `current`, `observed`, `questions/<id>`, `evidence/<id>`; competitor is freeform prose status. | Source-documented Git/provider behavior + inferred proposal; structured-vs-prose comparison unknown. |
| DS-32 | D | Adopt a resource-enforced, exact-action pre-effect mediation contract as the canonical authorization boundary; upstream hooks supply evidence, not receipts. | Source-documented patterns + proposal/inference; several unverified cells. |
| DS-33 | D | Governance combination: precise license/provenance metadata at ingestion, provenance tracking, and content treated as protected unless explicitly cleared. | Source-documented study results + secondary legal commentary; not primary case filings; no competitor or decisive falsifier. |
| DS-34 | D | `R1`: prospective forecast-and-review extension to the existing D-entry convention, not a second decision log; `R0` is the present narrative convention. | Source-documented studies + inference + hypothesis + proposal; benefit unmeasured. |

## Consolidated findings by domain

### Domain A — kernel, language and platform

Seven lanes (DS-13, DS-18, DS-19, DS-20, DS-21, DS-22, DS-23) meet on determinism, canonical bytes,
the four-function boundary and no-selection discipline. `docs/v3/research-lane/synthesis/domain-A-kernel-language-platform.md`
is the controlling digest. It records the one real dependency edge in the domain: DS-22's vectors
gate language evaluation, but DS-18's own comparison needs DS-22's byte-level corpus and refusal
taxonomy first. It also records the unresolved PAUSE model across DS-13, DS-22 and DS-23.

### Domain B — authority, safety and lifecycle

Eight lanes (DS-01, DS-02, DS-03, DS-04, DS-05, DS-07, DS-08, DS-24) meet on “routing or visibility
is not authority”, receiver-side fencing, typed ambiguity/quarantine, forward-only reconciliation,
and derived completion. See
`docs/v3/research-lane/synthesis/domain-B-authority-safety-lifecycle.md`. It preserves several
apparent tensions without resolving them: `drain` arbitration (DS-01 vs DS-04), credential material
as a grantable capability (DS-02 vs DS-24), and two different senses of “broker” (DS-05 vs DS-24).

### Domain C — operations, capacity and evaluation

Six lanes (DS-06, DS-09, DS-10, DS-11, DS-25, DS-26) meet on measure-first, honest counters,
preregistered experiments and rejection of implementer PASS as acceptance. See
`docs/v3/research-lane/synthesis/domain-C-operations-capacity-evaluation.md`. It flags that every
controller and gate is a shape without calibration until Owner inputs exist, and that the cluster
relies on a review process it never measures.

### Domain D — context, interaction and product-adjacent

Seven lanes (DS-12, DS-14, DS-15, DS-30, DS-32, DS-33, DS-34) meet on keeping authority and
attribution distinct from the surfaces that represent them, and on the public/synthetic-only
boundary. See `docs/v3/research-lane/synthesis/domain-D-context-interaction-product.md`. DS-33 is
asymmetric — no competing option and no decisive falsifier — and is legal-risk research requiring
counsel, not legal advice.

## Cross-domain dependencies and build order

The lanes imply a build order in which later experiments consume earlier artifacts. These are
prerequisite dependencies stated by the lanes, not a ratified plan or schedule.

- **DS-22 formal model, mutants and vectors → DS-18 language experiment.** DS-18's `EXP-FHAR-10` needs DS-22's language-neutral byte-level conformance corpus, refusal taxonomy and trace-validity checker before it can run. DS-22's frozen boundary names `decode`, `admit`, `reduce`, `derive_work_packet`; freezing gates language, store and broker evaluation but does **not** imply refinement, platform security, broker or external-effect evidence.
- **DS-21 store benchmark.** The store question is specified language-neutrally, so the canonical crash/replay benchmark can proceed in parallel with language work, but it blocks Milestone 2 (the canonical writer) and constrains DS-20 backup/snapshot/export and DS-18 packaging and dependency closure.
- **DS-19 underpins DS-23.** Broker transport, containment, PTY/ConPTY teardown and watchdog semantics are defined in terms of OS primitives. DS-19 also underpins DS-21 and DS-20 because persistence and supervisor/recovery contracts derive from platform atomicity, clock, resource and containment behavior.
- **DS-13 feeds the surfaces.** Configuration schema, editions, scopes, Full Access and PAUSE-mode gating are consumed by every other lane, without DS-13 itself deciding any of them.
- **DS-20 → DS-23.** Node fabric and multi-node reconnect depend on DS-20's fencing/epoch and disconnected-node rules; DS-18 feeds the later plugin-isolation lane.
- **DS-01 is the fencing substrate for Domain B.** DS-04 generation fencing, DS-02 grant-admission fencing, DS-05 writer epoch, DS-24 stale-fence/replay threats and DS-07 policy-generation guard all depend on DS-01's epoch vocabulary.
- **DS-02 → DS-04 and DS-24.** The typed capability/effect catalog, subset lattice and prepare/commit `grant-admin` action are the authority vocabulary the other two reuse. DS-24 supplies the effect brokers DS-04 requires.
- **DS-03 governs acceptance across lanes.** DS-07 completion acceptance, DS-08 independent rerun/review, DS-05 cutover rehearsal and DS-24 full-conformance gating all need a verifier-independence contract. DS-08 is a gate-shaping input to DS-03 and DS-05.
- **DS-26 is upstream of everything evaluative.** DS-06 counters, DS-10 measurements, DS-11 endpoints and DS-25 receipts all consume the typed two-ledger contract; without it each would read `unknown` as zero.
- **DS-12 is a blocking prerequisite in Domain D.** Its capsule/context-compiler, compaction governor, route descriptor and cost/usage ledger are the substrate DS-15, DS-30 and DS-32 assume. DS-30 supplies state-contract primitives those reuse; DS-14 depends on a rights/privacy gate consistent with DS-12's privacy classes.
- **DS-06 depends on DS-10 baselines; DS-25 depends on DS-10 and DS-26; DS-09 reuses DS-10 instrumentation.** Language, store and performance selection remain shared prerequisites none of these lanes can supply, so the dependency graph terminates in unselected components.
- **Remaining unselected, unchanged by this synthesis:** language/runtime, canonical store, formal model construction language and framework, renderer, plugin runtime/sandbox, IPC and serialization libraries, secret store/vault, wire serialization, signing root, packaging and update channel. No lane's output selects any of these.

## Consolidated open Owner decisions

Aggregated and deduplicated from the four domains. Every item is a question the lanes explicitly reserve for the Owner. None is decided here, and the lanes are not authorized to decide them.

**Authority, grants and capability (DS-02, DS-04, DS-13, DS-24).** Sovereign `grant-admin` self-widening and whether it requires an independent human; the out-of-band recovery/root mechanism; installation maximum versus active authority; bounds on delegated credential administration; whether raw credential material is ever a grantable capability; which authority edges need step-up authentication; whether a blocked authority-bearing request may auto-activate; whether credential-binding identities are goal-frozen or may rotate; which grant dimensions are confirmed in one interaction; “parent allowance” categories and conservation for preserved forks; which grants a lease holder may adopt routinely.

**Verification, acceptance and review (DS-03, DS-34).** Which vector relationships must be positively evidenced versus allowed `unknown`; canonical risk-class boundary examples and the materiality margin; human-review qualification and conflict-of-interest policy; receipt lifetime; whether provider/account/host claims stay hypotheses; the accountable reviewer and independent acceptance authority per class; original-versus-verified-correction scoring.

**Pause, stop and quiescence (DS-01, DS-13, DS-22, DS-23, DS-32).** `drain` versus `checkpoint` exclusivity and the drain allowlist; whether publication is drain-eligible; emergency reconciliation reads; `paused_with_ambiguity`; per-effect deadlines; auto-quarantine duration; quiescence-proof type; whether immediate PAUSE is the only operative policy; Stop-mode semantics and scopes; the names/semantics of the ten terminal controls; the Lazy Stop boundary and whether Lazy may escalate.

**Writer, migration and the availability/authority contract (DS-05, DS-20, DS-21).** Whether canonical writes stay available automatically after total coordinator loss (which decides consensus necessity); whether multi-node canonical availability is a v3 requirement; authority boundary one-to-one with an OS account versus several fenced instances per identity; whether the first checkpoint must contain a post-cutover `H+1` command; whether the broker is outside the aggregate boundary; writer identity as logical capability versus concrete process; rollback eligibility duration; whether all aggregates share a global epoch; the canonical event-equivalence rule.

**Store, durability, retention and deletion (DS-07, DS-21, DS-24, DS-25).** Per-command power-loss durability versus group commit and maximum batching delay; the durability unit; target filesystems and whether SMB/NFS is forbidden; the definition of “survives power loss”; p99 append latency, replay, WAL growth, RSS and bytes-per-million-events budgets; backup RPO/RTO and expiry; privacy/deletion key scope; maximum read-observer age; whether `expiry-bound` is user-visible; the artifact claim when a shared key stays live; coupling window; cross-project dedup; pin versus legal-hold authority; provider evidence tier; lost-node irrecoverability; post-expiry verification; the independent reviewer role; audit retention duration and erasure authority; internal-only versus exportable tombstone.

**Platform qualification and terminal (DS-09, DS-19).** Exact Windows build floors and Linux kernel/distribution profiles; WSL2 as production/development/both; canonical state on SMB/NFS scope; hostile versus cooperative descendants; whether a suspended laptop consumes task/lease time; escaped descendant as hard failure versus recoverable `unknown`; first-release terminal embeddings; whether systemd is mandatory; the definition of an “external effect” outside the process tree; audit-durable history versus current projection; default geometry and lease-handoff rule; shared-room read authorization; the approved numeric PERF-010 SLA; supported accessibility technologies; snapshot cadence and replay floor; whether client capability survives a daemon restart; multiplexer role and wire encoding.

**Service topology (DS-20).** Kubernetes as official versus compatibility target; hosted multi-tenancy and its isolation threat model; node mTLS through TLS-inspecting proxies; telemetry egress and deletion proof; which combinations need formal certification; certificate lifetime/revocation freshness; coordinator-small SLOs; backup defined entirely around a snapshot/export interface.

**Language, runtime, packaging and release (DS-18, DS-25).** One language across kernel/daemon/broker versus an accepted second runtime; CPython 3.13 long-term versus 3.14.7 promotion; minimum supported Windows versions; single executable versus a signed self-contained install closure; whether a preview runtime API is acceptable in the privileged base; whether Wasm's first evaluation is specifically plugin isolation; the evidence threshold converting a resource difference into a decision; the dependency-security policy; storage engine, packaging format, signing/trust stack, update channel and SBOM tool; default configuration-propagation policy; release-promotion authorization/quorum; support windows; emergency update deadlines; retained-slot count.

**Configuration and IPC/broker (DS-13, DS-23).** The `privacy_exposure`/`publication` lattices; what counts as a billing widening when engine choice changes without a budget change; visibility of retained unsupported edition requests; Telegram versus local-terminal authentication assurance; the reversible-migration window; whether plugins may introduce a bounded vocabulary; which adapter properties may be `restart-required`; whether `checkpoint` is default or goal-frozen; whether `m1b-broker/1` is immutable or a new major with negotiation; which contract materializes `snapshot_digest`; cursor rollover/incarnation; same-OS-user attachment versus installation key/attestation; admitted Windows client matrix and Linux cgroup floor; credit-exhaustion behavior; Lazy Stop timeout; MCP/stdio bounds and the command-receipt payload schema.

**Formal model and conformance (DS-22).** Duplicate-command handling (`DUPLICATE_COMMAND` versus replay); independent verifier as distinct principal versus distinct lease/role; deterministic-CBOR/SHA-256 as an acceptable test encoding; three-lease-epoch coverage in the first run versus later expansion; Owner-normative authority dimensions beyond the named six; immutable model-run artifact identity; trace-validity checker versus machine-checked refinement map before language comparison.

**Capacity, performance and routing (DS-06, DS-10, DS-11).** Hard ceiling `H`; machine reserves; mandatory versus advisory expansion signals; queue-age statistic and boundaries; dwell interval and observation epoch; whether content-free changed-byte aggregation is worth adding; authoritative external systems for pruning; global versus per-profile fallback ceilings; the exact benchmark manifest and minimum representative scenario; what counts as “verified quality”; uncertainty/reporting policy; publication provenance; source-ownership labels; the minimum acceptance difference and non-inferiority margin; value of one owner-review minute; maximum experiment envelope; peer-swarm control cost; corpus difficulty mix; evidence threshold to promote a measured result into policy.

**Telemetry, routes and context economics (DS-12, DS-26).** Harness admission list and versions; organization-admin credentials for read-only collectors; local retention; export cohort suppression; whether provider session IDs may be stored raw; host-resource and human-review valuation; route-learning promotion metric/margin/uncertainty; precedence for late billing corrections; whether document-qualified adapters may feed operator views before runtime qualification; the authoritative route/endpoint/model-class list; the cold-reconstruction noninferiority margin; cross-private-project dedup; which context tiers may go to public routes; whether paid explicit caches are permissible; maximum stale-evidence window; per-edition/route compaction policy; descriptor expiry age.

**Domain-specific product and governance (DS-08, DS-14, DS-15, DS-30, DS-32, DS-33, DS-34).** Scholarly: maximum false-negative rate; admissibility of membership-only metadata versus anonymous reproducibility; reliance on retained restricted artifacts; rights operations; metadata-only standards sufficiency; domain-neutral versus biomedical-first; revalidation SLO; specialist-review classes; budget; full offline replay. Conversations: transport-compromise containment and separate transport identities; protected-effect classes and requested-to-effective revocation delay; Telegram sender binding and message classes; edit/cancellation/retention/redaction rules; multi-goal budget attribution and no-progress escalation; consequence windows and digest cadence; minimum worthwhile coordination saving. Supervision state: serialization; staleness signals and windows; `observed` committed versus regenerated; project identity and archival lifecycle; which questions need Owner authority; morning-brief reconstruction; receipt retention/compaction; unattended execution; the sufficient “verified progress” receipt. Licensing/IP: obligations for distribution, docs, examples and model/dataset; counsel engagement and jurisdictions; ingestion metadata and default scans; provenance standard and publication; “assume protected unless cleared” default and clearance evidence; isolation of uncertain-data models. Decision journaling: D-entry template and append-only metadata; timezone/due-time/holiday handling; probability forecasts; reviewer/acceptance authority; review-service target and disposition; comparable classes; burden/adoption criteria; cancellation policy. Canary: private `ALLOW_TEST`/`ALLOW_FIXTURE`/`DENY` prefixes; authoritative oracle; independent-rerun definition; route-approval/candidate-revision retention.

## Gap register (summary)

The consolidated register of what is unrun, unset, unverified or `unknown` across all 28 lanes is maintained in the companion file `GAPS.md` (relative to this directory), which this section summarizes rather than replaces.

- **No experiment in any of the 28 lanes ran.** There is no benchmark, no model check, no mutant kill, no vector reproduction, no fault fixture, no chaos matrix, no restore or cutover rehearsal, no provider call, no conformance corpus and no deployment. Several named experiments were designed but not executed.
- **No measured Recursion value exists.** Every quantitative figure is a source-documented external finding, a sensitivity/feasibility calculation, a provisional threshold, or `unknown`/`unavailable`. Missing counters are never zero.
- **Selections gap blocks measurement.** With no language, store, IPC choice, framework, packaging format or plugin technology selected, several downstream measurements (DS-25 snapshot mechanism, DS-10 replay verification, DS-26 adapters) cannot be preregistered end-to-end.
- **`unknown` cells are widespread.** Examples: resource/tail figures (DS-18), every measured platform cell (DS-19), the full six-mode×four-outcome matrix (DS-25), provider retention and host cost (DS-26), physical destruction on disconnected nodes (DS-07), the Windows pressure-accounting equivalent (DS-06/DS-10), and multiple provider/entitlement cells (DS-03/DS-24).
- **Version currency is a snapshot.** Every “current” version named is current as of the 2026-09-30 evidence freeze and must be revalidated before any experiment; exact pins are decision inputs, not certifications.
- **Aggregation limits.** This master file is a summary of summaries; it inherits each lane's evidence-class boundaries and adds no revalidation.

## What must be settled before architecture

Concrete pre-architecture prerequisites, split into **decisions the Owner must make** and **experiments that must run before their dependents can proceed**. Neither list is a plan.

**Decisions that must be made before architecture**

- The availability/authority contract: may the single fenced canonical writer be temporarily unavailable after coordinator loss? This decides whether consensus is necessary and whether multi-node canonical availability is a v3 requirement.
- Language/runtime selection, canonical store selection, and the formal-model construction language and framework — all currently unselected, and all gates on later work.
- Renderer, plugin runtime/sandbox, IPC and serialization libraries, secret store/vault, wire serialization, signing root, packaging format and update channel — unselected across every lane.
- One settled PAUSE/Stop model consistent across configuration (DS-13), the formal model (DS-22) and the broker (DS-23), including `drain`/`checkpoint` precedence.
- The durability target (per-command power loss versus group commit), the target filesystems, and whether network storage is in scope; plus the definition of “survives power loss”.
- Hosted multi-tenancy and its isolation threat model, certification combinations, and the authority decision set (sovereign `grant-admin` scope, whether raw credential material is a grantable capability, and the out-of-band recovery/root mechanism).
- The initial numeric budgets and SLOs: p99 append latency, replay time, RSS and bytes-per-million-events, backup RPO/RTO, capacity ceiling, acceptance/non-inferiority margins and the benchmark manifest.

**Experiments that must run (and be independently verified) before their dependents proceed**

- DS-22: TLA+/TLC finite falsification model, classification of all 36 mandatory reachable mutants with retained counterexamples, a language-neutral byte-level vector corpus, and two independent implementations reproducing every vector bit-for-bit. This gates DS-18.
- DS-18: `EXP-FHAR-10` (CPython 3.13.15, Rust 1.98.1, Go 1.27.1; GIL and free-threaded as separate arms), hard-floor-first then resource-ranked, no weighted composite.
- DS-21: canonical crash/replay benchmark between segmented JSONL+CAS and SQLite 3.53.4 WAL + `synchronous=FULL` + CAS, with LMDB and redb as secondary challengers.
- DS-19: native-semantics platform qualification per pinned profile with preregistered negative traces; ConPTY teardown, cgroup/OOM, rename/fsync durability, lock-release and supervisor races on this project's hardware and builds.
- DS-23: the four named blockers (version negotiation, snapshot materialization, cursor rollover, ACK-release wording) plus the native chaos matrix. DS-13: a configuration conformance corpus.
- DS-10: v2-versus-Options benchmark, PERF-003 0/10/100 disabled-plugin matrix, R17 ablation, crash/restart/replay fault injection, and a matched maintenance change across a boundary.
- DS-11: five confirmatory campaigns, a pilot of 30 unique tasks per class with three repeats, and an ARM-count sweep at 0/1/2/4/8.
- DS-25: the full six-mode×four-outcome matrix, fault-injection dispositions and a restore trial. DS-05: a cutover and restore/reverse-reader rehearsal on the synthetic execution-attempt/lease aggregate.
- DS-26: adapter conformance and shadow evaluation, with the harness admission list fixed first. DS-03: the preregistered 480-candidate blinded matrix (120 per risk class, six defect families, treatments T0–T7).
- DS-08: the canary itself — no route has been exercised and no candidate commit created.
- DS-06: fixed-versus-adaptive crossover, per-slot marginal-cost profiling on both profiles, and Little's Law validity over a bursty window. DS-09: the PERF-010 view matrix plus adversarial containment tests and separate compatibility/accessibility suites.
- DS-12: the synthetic route-by-route suite (prefix versus cold, repeated compaction, cold disaster recovery, cross-route rebuild, privacy isolation, keepalive counterfactual).
- DS-14: the hard-floor corpus and the Option A/B/C comparison on coverage, update latency, verifier reproduction and bounded cost; the disabled-path acceptance test.
- DS-15: the F01–F24 fixtures and the matched direct-addressing evaluation. DS-30: structured-versus-prose resume-error comparison and scheduler/daemon crash-recovery semantics. DS-32: the synthetic fixtures and per-adapter Aggressive-Stop / Lazy-Stop observable boundaries. DS-34: the prospective `R1`-versus-`R0` window on reconstructability, timely review and burden.

An architecture phase would also need: a machine-readable, platform-profile-keyed conformance manifest with the negative traces behind it; a trace-validity checker plus the differential byte-vector suite; and a complete writer inventory with per-aggregate writer manifests and adapter-by-adapter conformance.

## Limitations and fidelity

- **No reruns and no independent verification.** No lane was independently verified by Recursion, no lane reran, and no Deep Research output is authoritative. An implementer's or a model's PASS is not acceptance; an independent verifier rerunning the exact candidate (preferably a different model family) is required before any recommendation becomes policy.
- **Records are drawn from model research.** The lanes follow the Deep Research loop described in `docs/v3/research-lane/wave-a-20260930/synthesis/meta-deep-research-methods.md`. That meta report itself documents hallucination, incorrect inference, authority-confusion and confidence-miscalibration risks, and says its time, cost and export descriptions are dated product-level claims subject to change. This master file inherits those limits.
- **Evidence classes are preserved, not blended.** Source-documented, locally observed, modelled/inferred, proposal/hypothesis, and unverified/`unknown` remain distinct. Confidence values describe research support, not probability, and are expressed in each lane's own terms because the lanes came from different waves and answer different handoffs.
- **Several `unknown` cells remain.** Resource/tail figures, most platform cells, recovery and migration cells, provider/entitlement/retention cells, terminal-control definitions, and the Windows pressure-accounting equivalent are among the deliberate gaps. `unknown` is not zero.
- **The evidence base is asymmetric.** Domain A/B lean more on source-documented platform and authority facts; Domains C/D lean more on inferred design. DS-33 has no competing option and no decisive falsifier, so it cannot be compared on the same basis as its siblings. DS-19 answered an unnamed subject query. DS-34 was extracted from a document and may have wording drift.
- **Aggregation adds no facts.** This is a summary of summaries; it adds no URLs, no new facts and no accepted-decision claims. It must not be read as an accepted decision or as authorization to implement, cut over, delete, enroll, publish, spend, deploy or run anything. Consequential choices remain with the Owner, and DS-33 additionally requires counsel review before any release decision.

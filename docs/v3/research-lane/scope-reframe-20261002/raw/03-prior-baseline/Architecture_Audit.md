# Recursion v3: architecture, implementation, and research-to-construction audit

**Read-only snapshot audit · 2026-10-02**  
**Repository:** NotSkittlz/recursion  
**Pinned source:** `3a542c6bbd88351e6f6c5eceffd317bc2450fcad`  
**Scope:** product architecture, implemented contracts, experimental evidence, release obligations, and bounded next construction packets

## Executive finding

Recursion has a substantive, carefully defended **contract-and-experiment foundation**, but this tree is not yet a usable v3 harness. The implemented product-side substrate is three pure Python planning modules. M1B and M1C add schemas, literal fixture bundles, and test-only oracles. The much larger experimental tree contains meaningful finite models, mechanism probes, and an inert recovery ledger. It does not provide the integrated durable kernel service, native sampling/tool loop, qualified upstream adapters, operator CLI, plugin runtime, context governor, or authenticated node fabric required by the product.

That is a construction-stage finding, not evidence that the product direction is wrong. The strongest next move is to close the **evidence-to-implementation seams**, while preventing new research from resetting completed work or turning proposals into authority.

Five conclusions matter most:

1. **Preserve the full product.** Native-only, upstream-only, and combined execution are equally real release requirements. A thin wrapper, an exclusively native harness, or an upstream-only system with a hidden native planner/compactor would each miss accepted scope. A small kernel is compatible with a comprehensive product because context, plugins, interaction, and node mechanisms can live outside the privileged boundary while still being mandatory capabilities. [Product release](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/PRODUCT.md#L71-L93), [OR-021–025](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/DECISION-REGISTER.md#L85-L89)
2. **Repair authority and scope drift before admitting construction.** The September 28 governance and D-017 are clear: v1/v2 and the Hermes-led repository control plane are retired. Several entry points and current-looking specifications still say the old constitution is operative or prescribe v2 migration. These contradict the current authority and can send a local agent into the wrong work. [Governance](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/CONTROL_PLANE.md#L3-L26), [D-017](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/state/DECISIONS.md#L11-L33)
3. **The five follow-up reports are decision inputs, not gap closure.** FU-01/02/04 explicitly do not run the experiments; FU-03 does not run the model checker or implement the stacks; FU-05 does not implement its protocol. They can close specification/design questions. They cannot turn G-01–05 into measured or independently accepted results. [Follow-up scope](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/prompts/followups-20261001/README.md#L11-L21)
4. **Do not “fix” the frozen M1 wire contracts to match newer research.** M1A forbids floats and lexical `-0`; FU-01 studies a float-capable JCS profile; FU-03 describes integer-only deterministic CBOR inside a test-interchange envelope. These are distinct layers/epochs, not interchangeable canonical bytes. M1B/M1C also have their own frozen digest conventions. A typed, tested bridge is required. [M1A wire](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/M1A-WIRE-PROFILE.md#L16-L54), [FU-01](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/prompts/followups-20261001/FU-01-language-runtime-experiment.md#L103-L114), [FU-03](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/prompts/followups-20261001/FU-03-formal-model-and-conformance-vectors.md#L123-L143)
5. **Build evidence across seams before optimizing components.** The repository itself records independently compared reducers agreeing on a bug, and a passing recovery ledger requiring two substantive reviewer-driven repairs. Cross-implementation equality, large state counts, and a green document gate are useful but insufficient. Demand independent invariants, seeded failures, current-authority checks at the effect boundary, and honest unresolved outcomes. [Common-mode model flaw](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/construction/typed-consultation-20260908/findings.md#L35-L61), [Recovery-ledger reviews](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/construction/recovery-ledger-20260914/PROGRESS.md#L93-L152)

## 1. Method, evidence classes, and limits

The supplied snapshot manifest records 910 tracked files, a complete tree, no blob mismatches, and no Git history. This audit independently enumerated all 910 files and recomputed their Git blob hashes against the supplied tree; all 910 matched. It read authority/entry documents, inspected relevant specification slices, inspected the three planning implementation files and representative tests/oracles, reviewed selected experimental source and evidence records, and reconciled the current research synthesis and five prompts.

**Nothing in this audit executes Recursion code.** No repository script, test, model checker, provider, service, host-control action, or deployment was run. No snapshot or remote file was modified. Static enumeration and JSON/source inspection were performed by audit-only commands. There was no inspection of current user accounts, sessions, consumption, or machine operations.

The report uses these distinctions:

- **Source-observed:** a property directly visible in this exact tree, including code and literal data
- **Repository-reported:** a historical run, review, or outcome recorded by the repository; not independently rerun here
- **Specified:** a product obligation or proposed mechanism, not working software
- **Inference:** an architectural consequence drawn from the inspected evidence
- **Unmeasured/unverified:** evidence necessary for the claim is absent from this audit

Severity is about consequence to construction or release. “High” does not mean an exploitable deployed vulnerability: no deployed system was inspected. Proposed tasks below require fresh bounded local packets and independent acceptance; they are not authority to select a technology, modify protected paths, enroll nodes, use credentials, or deploy.

## 2. What actually exists

### 2.1 Inventory is consistent with an early implementation foundation

Static snapshot counts:

| Category | Files | Interpretation |
|---|---:|---|
| `docs/` | 562 | Specifications, prompts, raw/synthesized research, and construction evidence |
| `experiments/` | 220, including 219 Python files | Prototypes, finite models, probes, checks; not the product runtime |
| `scripts/` | 102 | Includes tests/materializers and the three planning implementation modules |
| `schemas/` | 9 | Planning, execution, and integrity schema/materializer areas |
| `state/` | 6 | Governance/task lineage records |
| Other root/tool files | 11 | Entry points, conventions, and source checks |

The tree contains 266 Python, 293 JSON, and 343 Markdown files. There is no `pyproject.toml`, `setup.py`, `package.json`, `Cargo.toml`, or `go.mod` in this snapshot. This absence alone proves neither quality nor inability to ship; combined with the implementation inventory and explicit M1 limits, it supports the conclusion that product packaging/runtime integration has not landed.

### 2.2 Requirements-to-evidence map

| Requirement | Implemented or evidenced here | Missing proof or implementation | Construction destination |
|---|---|---|---|
| Strict decode, schema validation, plan/scope admission | `canonical.py`, `contracts.py`; bounded types, duplicate rejection, digest validation, DAG and scope checks | Integrated production authentication and future-epoch coverage | Kernel conformance; FU-03 then FU-01 |
| Pure reduction, work-packet derivation, replay | `kernel.py`; immutable inputs, event/receipt correspondence, duplicate/conflict handling | Durable atomic writer, service/process lifecycle, real effects | Canonical writer; FU-02 |
| Routes/plugins/process requirements | M1B schema, 24 fixture bundles, test-only oracle | Real adapters, actual plugin containment, broker processes | Plugin/route fabric and broker |
| Evidence/effect/publication/state/retention requirements | M1C schema, 24 fixture bundles, pure evaluators | Authentication, effect mediation, physical storage/erasure, publication actuator | Integrity adapters; state and node integration |
| Bounded composition and recovery models | Finite split/inclusive models, relations, mutations, historical receipts | Full integrated model, model-to-code correspondence, physical premises | FU-03 and coupled seam trials |
| Relative recovery allowance | Inert ledger plus historical independent review/repair | Actual counters, real consumption, physical crash durability | Accounting adapter plus writer |
| Native-only execution | Required and architecturally placed | Working native model/tool loop and full-role workflow | Native adapter/loop release slice |
| Upstream-only and combined execution | Required; role/route and compatibility design | Qualified upstream adapters, no-hidden-connection trial, exact feature coverage | Route-specific adapters plus integration |
| CLI and persistent terminal control | Detailed proposed interaction/broker contracts | Operator command client, daemon broker, renderer, cross-OS containment | FU-04/05; terminal milestone |
| Smart context/compaction | Detailed capsule, fidelity, privacy, governor and cache proposals | Implemented governor/compiler/hydration and structural/semantic trials | Context milestone; G-27 |
| Comprehensive plugins | Graph/grants/reload/disabled-path fixtures and rich specification | Native/upstream capability implementations and loss-aware compatibility | Plugin milestone; G-10/G-19/G-20 |
| Node tethering | Enrollment, role, signed envelope, spooling/reconciliation specifications | Authenticated transport, real receiver-side fence, disconnect/recovery qualification | Node milestone; G-04/G-15/G-17 |

The implementation limits are explicit, not inferred from filenames. M1A's AST gate forbids filesystem/network/process/storage imports and calls; the replay API accepts fixture authority/policy and an in-memory receipt journal. M1B identifies its oracle as test-only; M1C explicitly performs no represented effect. [Pure boundary](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/planning/static.test.py#L11-L21), [Admission API](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/v3/planning/replay/kernel.py#L517-L599), [M1B oracle](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/execution/reference_oracle.py#L1-L21), [M1C oracle](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/integrity/reference_oracle.py#L1-L7)

### 2.3 What the existing tests do well

The inventory has **71 fixture bundles**: 23 planning, 24 execution, and 24 integrity, and **17 `*.test.py` programs**: 7/5/5 respectively. Planning bundles contain 37 nested cases; the other bundle formats are not counted as equivalent nested cases. These are distinct denominators, not “71 tests passed.”

Planning conformance compares literal receipts, events, final state and digest, verifies refused commands leave state unchanged, and checks replay/decode outcomes. It runs each case twice. Property/adversarial tests cover authority attenuation, graph conflicts, purity, stale bindings, and prior dissent. The literal red-fixture mechanism predates implementation and binds schema/corpus identities. [Conformance](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/planning/conformance.test.py#L19-L85), [Frozen literal inventory](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/planning/red_fixture.test.py#L15-L34)

M1B's concrete purposes include stale route evidence, unsupported capabilities, unapproved substitution, plugin dependency cycles, digest substitution, separate grant dimensions, disabled-plugin inertness, fenced reload, unknown process containment, view-only attach/detach, stale input leases, flow gaps, UTF-8 byte cursors, and PAUSE/effect separation. M1C includes ambiguous effect/no-blind-repeat, insufficient verification, stale writer inventory, projection-only insufficiency, disconnected deletion copies, and key/equality leakage. This is a useful conformance vocabulary to preserve, not disposable scaffolding.

What those tests do **not** show: authenticated real principals, enforcement against adversarial processes, durable writes after power loss, actual upstream control, real plugin no-import behavior, or correct independent human acceptance. Supplied fixture facts are premises. Future integration needs evidence at the component that actually supplies and enforces each fact.

## 3. Prioritized findings

### A-01 — High: current-looking documents disagree on retired authority and migration

**Evidence.** README says `CONTROL_PLANE` and `ANCHOR` still describe pre-v3 governance and await rewriting; both were already rewritten. START-HERE says the Hermes constitution remains operative. ARCHITECTURE repeats this and prescribes a v2 strangler migration; STATE prescribes legacy imports and claims current v2 writers. The new FU README also repeats operative-Hermes language. D-017 and the supersession banner in CURRENT-AND-MIGRATION explicitly say greenfield, retired rather than migrated. [README](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/README.md#L19-L21), [START-HERE](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/START-HERE.md#L41-L44), [Architecture migration](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/ARCHITECTURE.md#L419-L459), [Architecture authority](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/ARCHITECTURE.md#L487-L503), [State](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/STATE.md#L168-L191), [New follow-up README](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/prompts/followups-20261001/README.md#L40-L48), [Supersession](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/CURRENT-AND-MIGRATION.md#L1-L23)

**Consequence.** A contributor following the product documents could plan removed-code migration, defer valid v3 work pending an amendment already replaced by governance, or misread Hermes the optional upstream integration as the retired repository executive. Governance precedence resolves the contradiction, but repeated contradiction defeats the “one trustworthy specification” goal.

**Falsifier / close criterion.** A current-document trace can follow every authority/migration reference without encountering an unmarked obsolete instruction; historical records retain their source, reason, and explicit supersession. No required future v3 schema migration/update/rollback obligation is accidentally deleted along with obsolete v2 cutover text.

**Next local task.** LP-0. Prepare a precise non-protected documentation patch and supersession map. Do not edit protected decisions or governance, rewrite historical fixture meanings, or revive deleted infrastructure. Hermes remains an allowed upstream peer where accepted product scope requires it.

### A-02 — High: research-to-repository reconciliation is missing

**Evidence.** The master synthesis correctly says the 28 lanes inspected public/synthetic materials rather than the repository. GAPS then states that vectors do not exist, OS cells are zero, and the ten controls remain undefined. These are defensible only when scoped to the **new proposed integrated corpus and unqualified target profiles**, not the entire repository: literal M1 vectors, bounded NTFS mechanism evidence, and a ten-control behavior table already exist. [Synthesis boundary](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/SYNTHESIS.md#L3-L29), [G-01–05](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/GAPS.md#L28-L42), [G-31](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/GAPS.md#L69-L79), [Ten controls](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/foundation-research/platform-round/interaction-contract.md#L36-L55), [Bounded storage/NTFS evidence](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/ARCHITECTURE.md#L529-L539)

**Consequence.** New research can accidentally erase prior evidence, reopen answered controls, or duplicate a fixture under a competing name. Conversely, existing bounded passes can be overpromoted into the full new corpus. Both errors are likely unless each claim is bound to an exact scope and predecessor.

**Falsifier / close criterion.** Every FU finding has a row linking its relevant requirement, existing implementation/fixture, claimed delta, evidence class, open decision, and next executable gate. “Missing” always names the missing scope. The ten controls are preserved; unmeasured operation/route boundaries stay open.

**Next local task.** LP-0 produces this crosswalk before the reports become architecture recommendations. Use direct requirements rather than asking the Owner the completed questionnaire again.

### A-03 — High: canonical-byte epochs need an explicit compatibility boundary

**Evidence.** M1A strict parsing rejects lexical negative zero and all floats, limits safe integers, and rejects duplicate keys before collapse. Its canonical serializer sorts object keys by UTF-16. M1B uses its own no-float profile; M1C's documented canonicalization uses Unicode-code-point ordering and a trailing newline. FU-01's prospective JCS treatment includes floating-point shortest-roundtrip and `-0` normalization; FU-03's `RCV1` wrapper is test interchange using a restricted no-float CBOR payload, not production wire. [Original FU-03 brief](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/prompts/followups-20261001/FU-03-formal-model-and-conformance-vectors.md#L47-L65) [Parser](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/v3/planning/validation/canonical.py#L293-L386), [M1A canonical serializer](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/v3/planning/validation/canonical.py#L1554-L1619), [M1B profile](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/M1B-WIRE-PROFILE.md#L9-L20), [M1C profile](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/M1C-WIRE-PROFILE.md#L9-L20)

**Consequence.** “Canonical JSON” is not a sufficient format identifier. Sharing a serializer can change frozen digests; treating CBOR test bytes as broker payload can silently redefine the ABI. A cross-language result can agree with its own encoder and still violate the intended older contract.

**Falsifier / close criterion.** A profile registry distinguishes outer test envelope, inner normative input bytes, schema epoch, canonicalization rule, digest prefix/domain, key ordering, numeric grammar, and refusal taxonomy. Cross-profile inputs refuse or use an explicit loss-aware bridge. Frozen M1 bytes remain unchanged. Tests include supplementary Unicode versus BMP ordering, lexical `-0`, `0.0`, exponent spelling, duplicate keys, byte-order marks, NUL/surrogates, integer boundary values, and trailing-newline differences.

**Next local task.** LP-1. Represent out-of-profile raw input as byte strings or opaque payloads in the vector envelope; do not make the CBOR data model “repair” invalid JSON before the system under test receives it. The bridge is a new scoped artifact, not an M1 mutation.

### A-04 — High: durable authority and real effect enforcement are still integration premises

**Evidence.** The planning implementation consumes fixture attestations and returns state/events/receipts; it does not commit them. STATE explicitly distinguishes a storage writer lock from an authorized writer and says M1A has no physical persistence. SECURITY requires the resource performing an effect to enforce the grant/fence. Finite experiments assume atomic durable commits and truthful authenticated receipts. [State distinction](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/STATE.md#L9-L37), [Effect posture](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/STATE.md#L61-L93), [Security boundary](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/SECURITY.md#L9-L32), [Experiment premises](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/construction/coupled-construction-20260908/findings.md#L54-L70)

**Consequence.** A signed record, API approval callback, canceled process, or broker ACK cannot be promoted into an authenticated admission, effective revocation, settled external effect, or durable publication. This is especially important for stale disconnected nodes and upstream harnesses with opaque internal tools.

**Falsifier / close criterion.** A deliberately stale writer/worker must fail at the accepting boundary, including revocation without a successor. Crash after effect acceptance but before receipt must remain unknown and hold its reservation until valid reconciliation. The same final trace must survive restart with exact binding.

**Next local task.** LP-3 and LP-5, coupled by LP-6. Classify durability by fault model: process kill, OS crash, and physical power loss are different experiments. No process-kill trial earns a power-loss claim.

### A-05 — High for release: native/upstream role closure is not implemented

**Evidence.** OR-022 requires independent native and upstream workflows and forbids hidden API dependencies in upstream-only installations. The proposed ownership matrix enumerates planners, implementers, reviewers, summarizers, recovery analysts, setup assistants, learned routing and retrieval roles. No qualified product implementation of those paths exists in the inspected runtime inventory. [OR-022](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/DECISION-REGISTER.md#L85-L89), [Role closure](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/foundation-research/platform-round/interaction-contract.md#L9-L34)

**Consequence.** A route resolver or successful upstream turn does not demonstrate a complete workflow. A native path cannot be relegated to a future optional experiment; an upstream path cannot pass by quietly using direct inference for “support” roles.

**Falsifier / close criterion.** In each declared configuration, disable all undeclared model connections and show every required reasoning role resolves before admission. Remove every engine/plugin/frontend and show adapter-free canonical recovery/status remains available. Report exact route versions and unsupported features. No missing launch-critical name is silently waived.

**Next local task.** LP-6 initially uses fake routes and forbidden-fallback tripwires. Later authorized product slices must replace them with a real minimal native loop and independently useful qualified upstream paths. The five research reports alone do not provide either.

### A-06 — High for release: plugins need semantic conformance and actual disabled-path proof

**Evidence.** Plugin scope includes engines, providers, context, compactors, gates, transports, sandboxes, observers and evidence adapters. The graph must resolve before import; code provenance, trust/isolation and grants are separate. The specification explicitly describes tools/resources/prompts/hooks/auth/UI/memory/dependency/lifecycle losses and four incompatible-route responses. M1B’s disabled-path oracle constructs a trace with all activity counters set to zero; it does not instrument an actual plugin runtime. [Disabled-path oracle](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/scripts/tests/v3/execution/reference_oracle.py#L385-L390) [Plugin surface](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/PLUGINS-AND-EDITIONS.md#L76-L121), [Graph and privilege boundary](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/PLUGINS-AND-EDITIONS.md#L158-L227)

**Consequence.** Manifest equivalence is not behavioral portability, and signature verification is not authority. A wrapper can be valuable when declared losses satisfy its workflow, but “MCP supported” is not complete plugin support. A disabled plugin that imports code or starts background activity fails even if the timing difference looks small.

**Falsifier / close criterion.** A synthetic plugin with import/process/network/filesystem tripwires stays inert while installed-disabled or incompatible. Digest substitution, graph cycles, exclusive-resource collisions, stale reload bindings and unexpected grants fail before activation. Valid enabled plugins and valid reload successors must work, so blanket refusal cannot pass. Native/upstream results are compared against the same capability-specific contract, with losses visible.

**Next local task.** LP-6 makes the contract/fault skeleton executable; a later bounded plugin runtime packet selects no sandbox by assumption and qualifies its actual isolation. Preserve the PERF-003 0/10/100 comparison as performance evidence separate from the zero-code-execution hard floor. [PERF-003](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/PERFORMANCE-PLAN.md#L198-L224)

### A-07 — High for release: smart compaction is an architectural specification, not a demonstrated optimizer

**Evidence.** CONTEXT defines the exact-reference non-droppable capsule, one deterministic governor per route epoch, candidate-only native/plugin compactors, retained recoverable evidence, and privacy-scoped artifacts. It explicitly separates structural integrity from semantic quality and says savings/quality advantages are unmeasured. [Fidelity versus quality](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/CONTEXT.md#L65-L90), [Capsule and governor](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/CONTEXT.md#L141-L214)

**Consequence.** A compact summary may preserve IDs while losing task meaning; a good answer may have dropped authority or pending approvals. Cache hits do not validate a grant, source freshness, cross-provider reuse, or subscription debit. Two compactors racing can create a second canonical context epoch.

**Falsifier / close criterion.** Reject candidate compaction that omits exact active directives, current goal/authority/config revisions, source/candidate IDs, gates, blockers, pending interactions, uncertain effects or rehydration references. Accept a valid compacted epoch atomically. Test stale capsule hydration after revocation, native-compaction notification loss, session deletion, provider/node change, missing artifact, and private cross-project equality leakage. Separately perform blinded task-quality assessment and total-workflow accounting.

**Next local task.** LP-6 adds deterministic capsule validation and adversarial candidate transforms using synthetic text only. A later G-27 comparison measures native-only/deterministic/hybrid strategies with the same task corpus, cold/reuse/no-future-work conditions, all correction/verification costs, and unavailable counters left unavailable. Do not select a universal hybrid policy, TTL or keepalive.

### A-08 — High for release: node tethering must qualify the accepting endpoint, not just transport

**Evidence.** The fabric is a proposed single-authority hub-and-spoke model with enrolled roles, replay-protected packets, manifest-first hydration, disconnected evidence spools, no authority expansion, and controller reconciliation before publication. Security requires explicit enrollment, separate trust/operator identity, and revalidation after reconnect. [Node fabric](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/EXECUTION-FABRIC.md#L312-L325), [Node security](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/SECURITY.md#L117-L148), [Recorded-work continuation](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/foundation-research/platform-round/interaction-contract.md#L85-L102)

**Consequence.** A connected node is not necessarily eligible; a disconnected node is not necessarily stopped. Moving a task without preserving reservations, pending interactions and uncertain effects risks duplication. Windows/Linux recorded-work recovery is required; migration of a live process image is not promised. Single-user multi-node operation does not imply enterprise HA, consensus, or tenancy.

**Falsifier / close criterion.** A fake disconnected recipient retains no right to publish or widen authority; old packet/lease/config/authority epochs cannot revive after reconnect. Work already permitted has a declared bounded completion rule. Lost ACK/receipt, duplicate spool delivery, stale checkpoint, clock change, node revocation, missing artifact and cross-OS incompatibility produce honest dispositions. Later real tests bind exact OS/filesystem/transport builds.

**Next local task.** LP-2/5 establish platform/broker primitives and LP-6 composes synthetic node boundaries. Real enrollment, network policy and credentials remain separately admitted work. G-06's coordinator-availability choice must not silently become a consensus project.

### A-09 — Medium: structural gates are useful but cannot accept semantic research

**Evidence.** `check_followups.py` checks file inventory, front matter, headings, directive markers, resolving relative links and obvious secrets; `check_synthesis.py` checks headings/links/scans. They do not verify cited sources, detect false claims or prove the result closes a gap. The README says this explicitly. [Follow-up gate](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/prompts/followups-20261001/check_followups.py#L1-L8), [Its checks](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/prompts/followups-20261001/check_followups.py#L125-L179), [Declared limit](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/prompts/followups-20261001/README.md#L54-L66)

**Consequence.** Green documentation gates can coexist with stale authority text and “unknown” cells. The frozen orientation gate is also intentionally bound to its old repair scope; it is not the aggregate gate for a new branch.

**Falsifier / close criterion.** A new gate rejects a deliberately unsupported evidence promotion, stale authority reference in current guidance, missing requirement edge, wrong candidate, absent independent receipt, or omission of a failed trial. It retains structural checks but does not label them scientific acceptance.

**Next local task.** LP-0 supplies a current candidate-bound evidence manifest and independent review checklist. Preserve the frozen orientation gate unchanged. [Frozen-gate warning](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/RESEARCH-SCOPE.md#L35-L46)

## 4. What research should land where

### 4.1 G-01–05 and the current five follow-ups

| Gap / report | Useful report output | Executable evidence still required | Dependency / milestone |
|---|---|---|---|
| G-01 / FU-01 / DS-18 | Pinned runtime/library candidates, whole-process accounting, hard-floor-first comparison protocol | Equivalent independent candidate implementations consume the same admitted byte corpus; repeated matched trials; resource/tail/cold-start/dependency evidence | FU-03 corpus first; implementation language decision; affects all later milestones |
| G-02 / FU-02 / DS-21 | Candidate-neutral append/replay/effect and restore oracles; explicit fault/durability profiles | Both finalists implement identical semantics; faults at commit/receipt/CAS boundaries; stale-writer and backup/restore checks | FU-04 platform facts; canonical writer / historical M2 |
| G-03 / FU-03 / DS-22 | Finite model specification, proposed 36-mutant registry and classification protocol, byte-vector specification, refusal taxonomy, trace mapping | Actual model exploration with complete frontier accounting; reachable non-equivalent mutants killed; independent stacks reproduce vectors; bridge to frozen M1 | First technical dependency for language comparison; model/kernel contract readiness |
| G-04 / FU-04 / DS-19 | Platform-profile manifest, native-semantics fixtures and honest unsupported statuses | Owned-child/PTY/ConPTY/lock/replace/clock fault runs on exact Windows/Linux profiles; raw outcomes independently checked | Store, process broker, terminal and node prerequisites |
| G-05 / FU-05 / DS-23 | Version negotiation, snapshot materialization, cursor rollover, ACK-release contract and chaos design | Native broker implementation; bounded framing/backpressure; slow client, gap, reset, detach, idempotency and containment tests | Consumes FU-04; terminal milestone / historical M6; nodes M7 |

This follows the dependency direction already recorded in GAPS. It does not require waiting for a language choice to write neutral contracts, or a storage choice to write a neutral crash oracle. It does require resisting a runtime comparison before byte semantics are stable. [GAPS dependency chain](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/GAPS.md#L81-L114)

The historical M2–M9 names remain useful as capability labels, but their embedded v2 migration/Project Pilot instructions are historical. Current construction packets should name the capability and current authority explicitly, not execute chronological ROADMAP text. [Roadmap orientation warning](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/START-HERE.md#L64-L67), [Historical milestones](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/ROADMAP.md#L287-L358)

### 4.2 Domain D, DS-15, and DS-34 are downstream requirements, not extra kernel selectors

**DS-12 / G-27 → context governor and evidence, with interaction dependencies.** Preserve the non-droppable kernel outside model summaries. Connect context validity to the same goal/config/authority revisions used by admission. The initial local task is deterministic structural fidelity; semantic quality and route economics require separate trials. Domain D correctly identifies this as a substrate for conversation, approvals and memory. [Domain dependencies](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/synthesis/domain-D-context-interaction-product.md#L115-L122)

**DS-15 / G-29 → actor/room/lease conformance at executive, CLI and node seams.** It contributes three crucial distinctions: durable actor versus addressing surface versus current authority; received/admitted/started/settled/reviewed/accepted; requested/committed/effective revocation. Its F01–F24 are designed but unrun. They should consume FU-03 authority vectors and FU-05 transport events rather than invent a second state machine. Preserve direct Owner-to-ARM conversation as accepted capability while comparing coordination mechanics under identical authority rules. A room acquires no pooled authority, and a named bounded step lease creates no standing higher executive. [DS-15 findings](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/wave-c-20260930/synthesis/DS-15-arm-conversations.md#L19-L48), [Recommendation and falsifiers](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/wave-c-20260930/synthesis/DS-15-arm-conversations.md#L50-L65)

**DS-32 / G-31 → approval/question/Stop conformance.** It supplies exact-action pre-effect mediation and honest settlement semantics. Resolve its missing brief context by pointing it to the existing ten-control names/behavior table; do not ask which ten again. The remaining work is operation-class boundaries, adapter coverage, authority receipts, and accessibility/transport traces. Couple it with DS-15 rather than implementing a parallel waiter/receipt system. [Domain D approvals](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/synthesis/domain-D-context-interaction-product.md#L55-L63)

**DS-34 / G-33 → prospective decision evidence and review, outside the runtime authority core.** Its useful immediate contribution is reconstructability: preserve original rationale, separate forecast from falsifier, assessment from command, and outcome from process. It does not prove a calibration benefit or justify editing D-017, backfilling historical probabilities, inventing a new review cadence, or maintaining a competing log. A synthetic compatibility check can validate proposed fields/flags before any protected authoring session. The actual first-of-month convention and D-017's December 1 review are already recorded. [Existing convention](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/state/DECISIONS.md#L1-L33), [DS-34 distinctions](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/wave-c-20260930/synthesis/DS-34-decision-journaling.md#L18-L48), [Candidate not adoption](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/wave-c-20260930/synthesis/DS-34-decision-journaling.md#L50-L79)

**DS-30 / G-30 → product state/memory questions must be scope-filtered.** Canonical versus observed state, durable question correlation, and candidate-only retrieval are useful. The retired repository-supervision/foundry workflow must not re-enter through this lane. Its Git-backed state convention must be reconciled with the product's canonical writer, not treated as another writable source of task truth. Domain D already records that conflict. [Tension](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/research-lane/synthesis/domain-D-context-interaction-product.md#L106-L113), [Current scope](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/ANCHOR.md#L30-L37)

DS-14 scientific-evidence and DS-33 rights/provenance work feed future evidence/plugin release qualification. This audit makes no legal clearance claim. These lanes need artifact- and distribution-specific review rather than being collapsed into a generic technical “provenance passed” bit.

## 5. A finite first local hardening cycle

This is a **proposal for seven bounded packets after report intake**, not an instruction to run them in this audit. No open-ended swarm, new broad research wave, production service, or live provider trial is included. Use one task/worktree, exact source/candidate, allowed paths, finite resources, machine gate and independent verifier per packet. New paths below are illustrative proposed paths, not files that exist today.

### LP-0 — Reconcile authority and evidence trace

- **Purpose:** eliminate A-01/A-02/A-09 before implementation consumes stale premises
- **Inputs:** current governance/D-017, accepted OR-021–039, existing M1 and experiment evidence, five returned reports
- **Allowed scope:** an additive reconciliation manifest/checker plus explicitly listed non-protected current guidance edits; historical source and frozen gates preserved
- **Deliverables:** requirement-to-source/code/test/gap mapping; current/historical/superseded classification; report recommendation delta and decisions-needed list; source/candidate and evidence manifests
- **Machine gate:** fail missing/duplicate requirement IDs, dangling current-source paths, obsolete current authority text, report result promoted without measured receipt, missing limitations, protected/M1 byte change, wrong candidate, or self-acceptance
- **Independent challenge:** inject one false “implemented” claim and one obsolete migration instruction; both must fail; a correctly labeled historical record must pass
- **Stop:** one coherent reviewed patch and finite unresolved-decision list. Do not rewrite the whole repository or protected log

### LP-1 — Build the model/vector compatibility bridge

- **Purpose:** make FU-03 executable without mutating frozen M1
- **Proposed scope:** `experiments/v3/kernel-conformance-<date>/` and matching documentation, read-only imports/fixtures from M1
- **Prerequisite:** accepted bounded model/corpus packet and explicit profile registry; independently reviewed oracle before implementations
- **Deliverables:** finite model/config, mutant manifest, retained reachable counterexamples, canonical-byte corpus with typed envelopes, refusal taxonomy, trace-validity checker, mapping to existing six obligations and M1 literals
- **Machine gate:** baseline invariants, complete frontier/status, all 36 mandatory mutants classified; each reachable non-equivalent mutant killed; excluded mutants justified separately; frozen vectors unchanged; independently constructed outputs equal normative bytes
- **Falsifier:** a shared wrong decoder can make both candidate stacks agree while violating normative bytes; a surviving mandatory faulty guard or missing frontier prevents acceptance
- **Stop:** declared finite bounds complete or an explicit resource/adequacy blocker. No arbitrary shrinking of the bound after seeing a failure, no kernel freeze from baseline pass alone

### LP-2 — Qualify minimal native OS primitives

- **Purpose:** turn FU-04 into observed per-profile facts for store, broker and nodes
- **Scope:** synthetic owned-child fixtures and temporary files only, with run-specific local approval where needed; no system setting, startup policy, enrollment or credential change
- **Deliverables:** exact OS/build/filesystem/runtime/terminal manifest; outcome/limitations matrix; containment and handle ownership receipts; controlled rename/replace/lock/cancel/restart traces
- **Machine gate:** valid baseline child works; spawned descendants are accounted for; escape/unknown containment is rejected; disconnect/teardown does not fabricate effect settlement; each result identifies fault class and evidence
- **Falsifier:** surviving descendant, incomplete process inventory, stale PID reuse, unsupported filesystem reported qualified, or process crash reported as power-loss durability
- **Stop:** the preregistered minimal Windows/Linux profile cells completed or unavailable. WSL/MSYS/network filesystems receive separate cells, never inherited qualification

### LP-3 — Compare canonical writer crash/replay candidates

- **Purpose:** executable FU-02 evidence; preserve a candidate-neutral state/effect oracle
- **Prerequisites:** LP-1 admitted semantics and LP-2 relevant filesystem facts; explicit chosen experimental durability assumptions; G-06 left visible if unresolved
- **Scope:** new experimental implementations of segmented log+CAS and SQLite WAL+CAS, synthetic aggregates/temp storage, no product default selection
- **Deliverables:** normalized input corpus and expected dispositions; append/receipt/CAS fault cuts; stale writer and duplicate/conflict controls; backup/restore high-water and artifact closure proof; full process/storage accounting
- **Machine gate:** equal accepted prefixes and replay digests; no conflicting duplicate acceptance or unauthorized stale writer; unknown effects/reservations survive; snapshot restore has exact state/artifact binding; faults are detected or honestly blocked
- **Falsifier:** acknowledging a commit whose required state/artifacts cannot be recovered, stale writer admission, or benchmark wins achieved by weakening durability
- **Stop:** matched fault matrix and independent receipts complete. A non-dominated tradeoff returns to the Owner; no silent store choice

### LP-4 — Run equivalent runtime candidates

- **Purpose:** decision-producing FU-01/EXP-FHAR-10 rather than language advocacy
- **Prerequisite:** LP-1 byte corpus/refusals and pinned host/workload/library closure; each candidate passes hard floors before performance comparison
- **Scope:** equivalent experimental candidate stacks and instrumentation, no production language adoption
- **Deliverables:** independent conformance results; wall/CPU/memory-time/peak/child-process/I/O/wakeup/cold-start/tail evidence with denominators; dependency/package/install-size and failure observations; matched trial order and all failed attempts
- **Machine gate:** bytes/refusals match; cancellation/fencing floors hold; accounting covers helper and child processes; raw measurements reconstruct summaries; missing metrics remain unavailable
- **Falsifier:** a faster candidate shifts work into uncounted helpers, changes semantics, or silently omits difficult vectors
- **Stop:** frozen comparison complete; present hard-floor survivors and Pareto tradeoffs without invented scalar weights or product selection

### LP-5 — Exercise the broker contract under native chaos

- **Purpose:** executable FU-05 evidence at the actual process/view boundary
- **Prerequisites:** reviewed four-blocker contract plus LP-2 platform receipts and LP-1 command/refusal semantics
- **Scope:** fixture child processes, synthetic command streams and temporary broker state; no real engine or arbitrary user process control
- **Deliverables:** explicit version negotiation, immutable snapshot/cursor binding, rollover rule, ACK versus credit/ownership semantics; slow/detached/crashed/reconnected client traces; malformed/oversized/torn frames; command duplicates; native teardown
- **Machine gate:** bounded queues/allocation, RESET-on-gap, no passive-view work launch, control progress under output flood, duplicate commands do not repeat effects, full owned process tree terminated or reported/quarantined
- **Falsifier:** ACK releases authority/uncertainty rather than only its declared ownership, new view starts another worker, or slow view blocks canonical progress
- **Stop:** preregistered minimal native chaos matrix and independent review complete. Protocol support is scoped to certified profiles, not all terminals

### LP-6 — Compose one inert product seam

- **Purpose:** show the architecture carries the user's core ambitions together before expanding adapters
- **Scenario:** a bounded actor receives an attributable command, resolves a native or upstream fake route and plugin configuration, derives a capsule, starts a fake node attempt, encounters compaction and a lost receipt, then receives revocation and reconnects
- **Scope:** one synthetic goal, bounded actors/attempts/artifacts, no provider/network/enrollment/real plugin package; separate new experimental path with unchanged M1
- **Deliverables:** one shared manifest mapping each transition to LP-1/3/5 and plugin/context/node obligations; valid positive trace; adversarial traces for stale capsule, disabled import, stale reload, duplicate spool, forked allowance, hidden native fallback, missing independent acceptance and revocation without successor
- **Machine gate:** every authority/effect/reservation/capsule transition has one owner; no second writable truth; settled versus unknown remains distinct; valid work progresses; each seeded seam defect is detected by an independent property
- **Falsifier:** components pass separately while a stale context/plugin/node binding admits a protected effect, or all-negative refusal is presented as a working workflow
- **Stop:** one fully bounded composed seam, retained failures and exact-candidate independent receipt. This is integration evidence, not the native/upstream launch trial or G-27 semantic-quality result

### Scheduling and acceptance of the cycle

LP-0 can reconcile the five reports while LP-1/LP-2 packets are drafted. Run LP-1 and LP-2 only after their own admissions. LP-3 and LP-4 consume the necessary admitted outputs; LP-5 consumes the platform/command contract. LP-6 then composes the accepted seams. Independent review capacity is a real dependency: do not open every packet simply because compute is available.

Each result should carry: task/requirement IDs; exact input and candidate hashes; scope/allowed-path evidence; toolchain/host/profile pins; finite bounds; implementation author and independent reviewer identities; raw attempts including failed/aborted/censored runs; positive and negative controls; oracle version; actual command/status; measured denominators; limitations; and an explicit accepted/repaired/blocked disposition. Keep receipts outside the candidate where the established workflow requires it. A changed candidate needs new binding, not a copied old PASS.

## 6. Release remains broader than this hardening cycle

The first usable release is one comprehensive release cut built incrementally. The audit does not propose relabeling a kernel spike as v3. Required coverage includes:

- Independently useful native, upstream-only and combined workflows, with all reasoning roles explicit and no hidden model connection
- All ten controls and the three configurable Stop behaviors, durable questions/approvals/queues, active steering distinct from next-turn queueing, source-aware preserved forks, attributable assistant interaction
- Useful native/upstream plugin implementations, local execution, four incompatibility responses, configuration propagation/provenance, setup/import/repair and six update modes
- Smart context continuity with exact constraints and separately measured semantic fidelity/economics
- Native Windows/Linux control, execution and recorded-work recovery across nodes; local operation without remote enrollment
- Adapter-free canonical recovery/status, resource ceilings, truthful counters, privacy/credential boundaries, independent acceptance and backup/restore
- Exact candidate scenarios: website preview, bug fix, interrupted refactor, and an upstream-only workflow, followed by the admitted private canary/soak and Owner release decision

The accepted ranking is responsiveness, subscription efficiency, then completion, subject to correctness, authorization, resource limits and recoverability. It cannot be reduced to tokens saved. Failed/censored tasks, verification and repair, human correction, hydration/transfer, recovery and all reasoning roles belong in the total workflow. Every missing metric needs a provenance-qualified unknown, never zero. [Acceptance scenarios](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/ACCEPTANCE.md#L132-L165), [Traceability and contract gate](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/ACCEPTANCE.md#L167-L200), [Release gate](https://github.com/NotSkittlz/recursion/blob/3a542c6bbd88351e6f6c5eceffd317bc2450fcad/docs/v3/ACCEPTANCE.md#L407-L419)

Seven named launch-critical integrations remain accepted scope. Exact product/route/version eligibility and entitlement must be revalidated, and absence requires an Owner release decision. Hermes the optional upstream engine is distinct from the retired Hermes-led repository control plane. The current research does not select a language, store, renderer, plugin sandbox, universal compaction policy, consensus model, transport topology, or support window.

## 7. Bottom line

The repository's strongest asset is its discipline around literal contracts, explicit uncertainty, bounded evidence, and retained reviewer counterexamples. The major weakness is the missing current bridge between a rapidly growing research/specification layer and the actual implementation boundary, compounded by stale authority and migration language.

The productive sequence is: **reconcile current truth → preserve/version the contracts → execute the finite model/platform/store/runtime/broker comparisons → compose one adversarial seam → build required product slices → run complete workflow/recovery acceptance.** Plugins, smart compaction and node tethering should remain first-class requirements throughout, with their contracts appearing early in the seam tests rather than being deferred until after a supposedly complete kernel.

## Appendix A — Source coverage

### Directly inspected for this audit

- Authority/orientation: `AGENTS.md`, `CONTROL_PLANE.md`, `ANCHOR.md`, root `README.md`, `state/DECISIONS.md`, `docs/v3/START-HERE.md`, `RESEARCH-SCOPE.md`
- Product/specification slices: `PRODUCT.md`, `DECISION-REGISTER.md`, `ARCHITECTURE.md`, `STATE.md`, `PLUGINS-AND-EDITIONS.md`, `CONTEXT.md`, `EXECUTION-FABRIC.md`, `CLI.md`, `SECURITY.md`, `ACCEPTANCE.md`, `CURRENT-AND-MIGRATION.md`, `ROADMAP.md`, `PERFORMANCE-PLAN.md`, `RESEARCH-AGENDA.md`
- Cross-cutting contracts: platform-round `repository-map.md`, `architecture-roadmap.md`, `interaction-contract.md`; M1A/B/C wire profiles
- Product-side implementation: planning `canonical.py`, `contracts.py`, `kernel.py`; inspected relevant sections and function/import inventory, not a statement-level proof of every branch
- Tests/data: planning conformance/property/adversarial/red-fixture/static programs; M1B and M1C reference oracles; all 71 bundle identities and purposes/inventory; selected literal structure. Only planning nested cases were counted; no assertions executed
- Experimental evidence/source: formal-comparison `coverage.json`; coupled-construction findings and `c_audit.py`; typed-consultation findings; architecture's replay-store/generation-authority/effect/composition summaries; recovery-ledger `ledger.py` and complete relevant repair/acceptance history; integration `NEXT.md` for obsolete-foundry framing
- Current research layer: `SYNTHESIS.md`, `GAPS.md`, Domain D synthesis, DS-15 and DS-34 lane syntheses, five FU documents and README, `check_followups.py`, `check_synthesis.py`

### Static inventory checks

- Enumerated all 910 files; counted root groups/extensions, product planning modules, experimental Python files, M1 bundles and test programs
- Checked common packaging manifest names, finding none in this snapshot
- Performed a narrow inline-relative-link scan over root and top-level v3 Markdown. It found one concrete missing archive link in `docs/v3/README.md:166`; a regex example in `VALIDATION.md` was a scan false positive. This is not a comprehensive Markdown/link gate, and nested historical maps can contain removed-code references even when the current file's inline links resolve

### Not reviewed or not established

- No Git history, PR diff, remote branch ancestry or current deployment verification beyond the supplied pinned snapshot metadata
- No independent rerun of historical gates or receipts; no claim that all tests pass on this commit
- No exhaustive audit of all 266 Python files, all research raw reports, every schema field, or all 910 files semantically
- No external primary-source revalidation, route entitlement/legal review, live upstream qualification, account inspection, performance measurement, power-loss trial, secret-scan certification, vulnerability scan, or supply-chain clearance
- No present cloud/local machine state, connectivity or resource claims
- No user environment, source repository, protected file, runtime, setting, credential or remote state changed

## Appendix B — Acceptance vocabulary to keep stable

| Term | What it establishes | What it does not establish |
|---|---|---|
| Document structural PASS | Required files/sections/links/scans meet that check | Research truth, empirical fit, product acceptance |
| Fixture/oracle PASS | Declared supplied inputs produce expected modeled outcomes | Real provider/OS/resource enforcement |
| Finite model closure | All reachable states within declared bounds/frontier and assumptions checked | Unbounded correctness or omitted environment behavior |
| Differential agreement | Candidate implementations agree on compared observations | Correctness against an independent oracle or absence of shared bugs |
| Process termination | Observed owned processes exited or were contained | External effect canceled, rolled back or uncharged |
| Receipt/ACK | Exact declared delivery/ownership or effect evidence | Arbitrary authority, acceptance, durability or release of another reservation |
| Canonical digest | Bytes match the named format/profile | Principal authentication, current authority, truth or freshness |
| Independent exact-candidate acceptance | Named verifier reproduced/challenged that candidate inside scope | Universal release readiness or permission to merge/deploy |

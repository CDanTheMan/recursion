# Recursion capability driven prompt and context composition

Research candidate for deterministic compilation and fixed budget scaling

**Date:** 2026-10-02 UTC  
**Lane:** R-PC, packet 20261002d  
**Parent goal:** `goal-recursion-v3-harness-orchestrator`  
**Source pin:** `b696f6ece243b48c94fc0bbc7ee1d4b284c46f97`  
**Status:** specification candidate and unexecuted acceptance handoff; no implementation, route qualification or measured advantage

## 1 Main finding

The strongest candidate is an immutable, source-attributed composition manifest produced by an unprivileged deterministic compiler and admitted through the existing kernel and context governor. It extends the eight-pass compiler already proposed in the 20261002c companion. It does not create a global prompt manager, authority database, executable plugin loader or new executive tier.

The useful new commitments are exact read-cut and transform bindings, complete mandatory closure, a byte-level output and provenance contract, explicit procedural precedence, conservative cache invalidation, and an experiment that can reject each capability addition at an unchanged resource allowance. A reproducible artifact proves neither that a model obeys it nor that added capabilities improve a workflow. A generated summary is a frozen input only after its actual output is captured; repeating its model, prompt and seed is not reproducible generation.

D-034's falsifier is retained literally in meaning: an addition that degrades quality, latency or authority at fixed budget, or makes composition nonreproducible, falsifies the thesis **for that addition**. An improvement in another endpoint cannot erase that result. A non-dominated tradeoff may still be useful for an explicitly bounded workflow, but is not an unqualified scaling success. There are no measured quality, latency, resource, cache, subscription or review-effort results in this report.

### Evidence convention and scope

**SD** identifies a source declaration; **LO** identifies static inspection of supplied files or this report; **I** identifies inference/design; **U** identifies unknown or unmeasured behavior. Sections 3–10 are candidate design I unless explicitly marked otherwise. All target fixtures are **UNEXECUTED**. Exact candidate names below are proposed application-layer semantics, not adopted types, frozen wire fields or a choice of schema language.

LO: the fresh export is pinned to [current master][R00], root tree `a866969c9346372dcf74c2f05a7f9d648c766494`. Its acquisition receipt verifies 1,401 blobs and 196 trees. PR 149's merge `e2e02af1712de8fc388883bc65c150ad1138ee96` brought in the shared-contract companions and this research packet; master then advanced through PR 148. The source pin therefore includes both. The earlier companions retain their historical PR 147 pin inside their text; their current merged locations below are the inputs read here. PR 148 verification evidence is not evidence of an implemented prompt compiler.

Research execution comprised read-only source/public-document inspection and authoring/static QA of this deliverable. No repository script, test, module, plugin or binary was imported or executed. No Work/Codex/cloud session, provider/model/account/auth/live-host call, credential operation, installation, spending, repository edit, publication or merge occurred. Public search queries contained public technical topics only.

### Authority and prior work retained

The [constitution][R01] governs beneath Lucas's current explicit decisions. Its repository document precedence remains unchanged. The [Anchor][R02], [operating rules][R03] and accepted [D-018 through D-034][R04] constrain this research. D-019's comprehensive opt-in surface is not reduced; D-021/D-029 credential boundaries remain separate from prompt handling; D-022 retains Aggressive/Full/Lazy and checkpoint/interrupt/drain; D-024 continuity preserves liabilities and evidence; D-031 prohibits unsupported savings and vendor-intent claims; D-033 leaves cheap porting a hypothesis. D-020's availability seam, D-023's first qualification priority, D-025's bounded opt-in research, D-026/D-027's licensing/counsel gates and D-028's platform floors are preserved, not qualified here.

| Current pinned input | What this lane inherits | What R-PC adds |
|---|---|---|
| [Prompt Plugin Skill companion][R05] | Seven independent capability states; eight compiler passes; four discovery arms; three retention classes; invalidation cases; B01–B16 inert corpus | Exact composition joins and artifact identity, span coverage, precedence and N-increment predicates |
| [Shared Contract Reconciliation][R06] | Four-field ArtifactRef; 18-field ContentEnvelope; one loss record; typed identity domains; receipt facts; disclosure ordering; conserving accounting | Application-level composition facet using those references; no additional Q-base field |
| [Harness Orchestration Performance][R07] | Route-specific semantic coverage, complete helper/meter closure and matched comparisons | Composition compile/first-event/verified-outcome attribution within that same workflow |
| [CONTEXT][R08] | Capsule control kernel, one governor, fidelity gate, current rights, provider versus semantic caches | Explicit pass preconditions and newly checked immutable epoch candidate |
| [PLUGINS AND EDITIONS][R09] | Deterministic capability graph, manifest-before-import, disabled inertness, fenced replacement | Mandatory closure, optional selection, tool disclosure and procedural order bindings |
| [CLI][R10] | Deterministic effective-value validator; requested/compiled/effective; both propagation modes | Per-recipient composition preview/application evidence and immediate revocation behavior |
| [M1B wire profile][R11] | Existing exact JSON/RFC 8785 profile, closed fields/reasons and plugin semantics | Nothing in frozen payloads; new candidates require separately versioned interpretations |
| [PERFORMANCE PLAN][R12], [R-O][R13], [R-W][R14] | Hard floors, full vector, whole assigned cohort, independent oracle, uncertainty and Owner ranking | A fixed-budget increment schedule, paired arms and explicit scaling adjudication |
| [R-Q][R15], [R-A][R16], [Interface Strategy][R17] | Revocable projections; contribution ownership; common control semantics | Shared projection inputs for R-UI/R-MOB without new authority |

## 2 Primary evidence that constrains the candidate

The following SD capsules were retrieved on **2026-10-02**. Mutable pages are date-pinned observations, not claims about an installed build. Versioned standards retain their named revision. No public performance figure is transferred into Recursion. Sources are summarized narrowly with no prose quotations.

### Formats and context evidence

| ID and source | Source finding and design consequence |
|---|---|
| S01 [Agent Skills specification](https://agentskills.io/specification) | Separates metadata, body and optional resources. Its experimental allowed-tools field varies by client. Progressive loading is a package convention, not a permission grant, complete discovery guarantee or bound on catalog growth |
| S02 [Agent Skills integration guide](https://agentskills.io/client-implementation/adding-skills-support) | Advises excluding disabled/denied skills from catalogs, describes explicit and model-driven activation, and discusses retention across compaction. Recursion still needs independent eligibility, mandatory dependency and application evidence |
| S03 [MCP tools 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) | Lists are paginated, authorization-dependent and changeable; deterministic ordering is recommended. Tool annotations are not inherently trusted. Names collide across servers. A list is neither an installed capability proof nor effect authorization |
| S04 [MCP resources 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/server/resources) | Applications decide how to include resource context; resources have URI identity and optional change/subscription support. A URI or notification does not provide Recursion's immutable version, admission or freshness guarantee |
| S05 [MCP prompts 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts) | Prompts are server-authored templates designed for user selection. User-controlled invocation does not mean user authorship. A selected template must therefore retain its imported-content provenance |
| S06 [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html), June 2020 | JCS defines canonical JSON serialization with deterministic property sorting and restricted input requirements; array order remains meaningful. It is a candidate representation mechanism, not semantic policy validation or a general raw-text normalizer |
| S07 [JSON Schema core 2020-12](https://json-schema.org/draft/2020-12/json-schema-core) | Schema dialect/vocabulary declarations govern interpretation. Structural validation is distinct from canonical serialization and application semantics. A pinned supported schema cannot replace rights, dependency or coherent-cut checks |
| S08 [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/), TACL 2024, DOI 10.1162/tacl_a_00638 | Reports position-sensitive performance on multi-document QA and key-value retrieval. This motivates counterbalanced required-material positions and distractor counts. Its tasks/models do not establish a current Recursion effect size, safe context length or preferred selector |

MCP 2026-07-28 is the inspected current protocol here; an explicitly legacy 2025-11-25 binding remains a different profile. Protocol revision is part of the input cut. No transport or MCP implementation is selected. Parser/schema compatibility cannot settle origin, authority, current rights or semantic influence.

### Provider cache and continuation evidence

These rows define adapter questions, not universal cache rules. Their applicable endpoint, model/build, platform and settings must be revalidated before a later admitted run.

| ID and source | Documented constraint | Required candidate treatment |
|---|---|---|
| S09 [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) | Matching concerns the rendered prefix, including tools and relevant settings. Tool order, schemas, formatting and reasoning settings can affect it; compaction can replace earlier context. Breakpoint/lifetime controls are model-dependent; session continuity does not guarantee a hit. Identical cached requests need not generate identical output | Bind the exact controllable rendering/settings; preserve opaque provider additions as an observation limitation. Record actual cache counters; do not infer OAuth harness controls or subscription debit |
| S10 [OpenAI tool search](https://developers.openai.com/api/docs/guides/tools-tool-search) | Deferred functions still initially expose names/descriptions; namespaces can expose group metadata. Discovered definitions enter at the context tail. Hosted and client-executed searches are distinct; loaded definitions persist unless changed | Charge discovery metadata and full service-side disclosure separately; admit before transmitting any definition. Exact disable/replacement takes precedence over prefix retention |
| S11 [OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction) | Server-side and standalone compaction return opaque encrypted state with different continuation instructions. Standalone output can include retained items as well as the compaction item | Preserve the actual returned representation and supported continuation contract; do not claim inspection of hidden state or use it as canonical authority |
| S12 [Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | Prefix hierarchy is tools, system, messages. Tool-definition changes invalidate downstream prefixes; tool choice and images affect messages. Thinking/effort invalidation is model-specific. Explicit/automatic controls and retention are endpoint/platform-sensitive | Treat the hierarchy as this adapter's binding. Revalidation covers tools, controls, model/platform and documented exceptions; do not introduce a portable TTL or savings rate |
| S13 [Anthropic tool caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching) | Deferred definitions enter history as tool references without rewriting the system prefix. Expanded MCP toolset ordering may be provider-controlled | Distinguish declared order from actual exposed order and unknown hidden serialization. An append-only experiment requires exact-profile evidence |
| S14 [Anthropic tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) | Deferred tools are declared to the service and discovered through reference results; regex and BM25 variants and compatibility constraints are documented | Provider-side deferral is not zero disclosure or proof of recall. Bound returned/search work and keep no-match distinct from absence |
| S15 [Anthropic mid-conversation changes](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) | Supported models permit constrained system/tool changes appended after a stable cache breakpoint. Editing earlier history invalidates affected reuse; support and placement are model-specific | Admit this only as a qualified route feature. Retain semantic order and current authority even where appending is allowed |
| S16 [Anthropic compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) | Distinguishes on-demand, threshold and client summarization, with different retained-turn behavior. On-demand names beta compact-2026-09-04 | Store mode, actual output and fidelity evidence; a feature name does not establish upstream-harness access or summary correctness |
| S17 [Gemini context caching](https://ai.google.dev/gemini-api/docs/caching), page updated 2026-09-02 | Current Interactions documentation describes implicit caching and favors common prefixes. Cache usage is observable in endpoint-specific counters; explicit named caches belong to generateContent | Keep endpoint identities separate and record observed reuse. Common content is only a reuse opportunity, not a hit or cost result |
| S18 [Gemini Interactions](https://ai.google.dev/gemini-api/docs/interactions-overview), page updated 2026-10-01 | Implicit caching works in stateful and stateless modes. The page distinguishes unavailable explicit caching from generateContent support | Session affinity remains a candidate optimization with unknown local benefit; do not transplant explicit cache controls between endpoints |

A route exposing no exact cache controls or counters has `unknown` cache behavior for this task. It is not secretly cache-disabled or cost-free. The provider's interpretation may contain hidden instructions beyond Recursion's bytes; byte reproduction of the submitted payload must not be advertised as reproduction of that entire hidden context.

## 3 Exact input cut and composition pipeline

### Candidate identity and ownership

The candidate `CompositionManifest` is a derived, immutable context artifact admitted by the existing context governor. R-PC owns this proposal's composition semantics; R-A owns contribution definitions; R-Q owns content/envelope/projection semantics; existing canonical services own goals, directives, grants, configuration, routes, reservations and effects. Naming a design owner does not grant a new writer.

Use the inherited `ArtifactRef = (object_type, id, version, content_digest)` unchanged. The containing interpretation binds digest algorithm/domain, byte coverage, normalization, privacy domain and profile revision. `ContentEnvelope` remains its exact 18-field base; composition metadata is a separately versioned facet/reference. Unknown mandatory security semantics block protected use. A changed digest cannot rebind an immutable object slot under the same type/id/version. Frozen M1 serialization and error alphabets remain untouched. [R06][R11]

### CompositionInputSet candidate

Each row is required when applicable. Absence is either evidenced not-applicable or a typed unknown/blocker; there are no ambient defaults. An exact extension spelling below is an R-PC proposal, not a claim that the source already declares it.

| Input group | Exact binding and required evidence | Current owner |
|---|---|---|
| Task control | `goal_spec_ref`, `owner_intent_refs`, `task_ref`, `plan_revision_ref`, `acceptance_gate_ref`, accepted directive/answer refs and canonical adoption sequence | Goal and intent services |
| Authority | Principal/actor and lineage, task/step work lease, current grant/privacy/egress/budget policy refs, relevant writer/work/pause/grant domain floors and source/deletion freshness cut | Existing kernel/admission |
| Configuration | Requested revision, compiled candidate ref, **effective** `configuration_revision`, target `configuration_epoch`, application receipt, lifecycle and propagation mode | Configuration resolver/application |
| Capability inventory | Admitted inert installation records and enabled IDs, manifest/payload/dependency-lock refs, exact resolved graph, states and rejections; selected workflow/profile refs | R-A graph and installation services |
| Route | Exact assignment `route_epoch`, `RouteCapabilityDescriptor` identity/digest and `route_descriptor_epoch`, interface/build/model/profile, tool visibility and compaction/cache/accounting evidence | Route admission/maintainer descriptor |
| Node and execution | Node/process incarnations, execution profile, trust/isolation/containment and resource profile refs, owned helper/subtree scope | Node/runtime services |
| Workspace | Workspace/repository/instance refs, immutable source snapshot and capture class/coherence evidence, candidate/materialization revision and mutation generation where needed | Workspace/source services |
| Memory and evidence | Authorized MemoryProjection and ContentEnvelope refs, complete possible-influence set, source freshness, allowed audience/purpose/retention and one loss record | R-Q and provenance services |
| Continuation | Parent capsule/context epoch, active procedure bindings, completed-step refs, pending interactions/queues, unresolved operations and resource liabilities | Existing context/operation services |
| Allowance | Task and inherited budget reservations, route-context/output reserve, local CPU/memory/IO/time/attempt/helper ceilings and metering coverage | Existing resource governor |
| Pure transform | Compiler, rule/policy, resolver, parser, renderer, canonicalization and route-template versions; admitted lookup/index snapshot; deterministic tie rules and explicit environment inputs | Versioned implementation/profile artifacts |
| Nondeterministic upstream outputs | Actual selector proposal, summary, retrieval response or opaque compaction output bytes and immutable refs, with their exact observed input set and producing receipt | Original observation/transform evidence |

Credentials are not an input. References to a qualified route/account class do not authorize reading secrets. Upstream-only role closure includes selectors, compactors, verifiers and recovery; a hidden native model helper violates the admitted profile.

### Coherent read cut

`CompositionReadCut` contains: canonical writer domain and admitted committed prefix; exact source positions for goals, directives, grants, configuration, graph and operation state; the declared relation of each projection to that prefix; immutable artifact refs and retention pins; external observation cuts/intervals; consistency/coverage evidence; and the interpretation-map version. It is a vector of typed domains, not one timestamp or numeric maximum.

A valid cut must satisfy every declared dependency edge: the effective config application receipt names that config revision; the resolved graph names that config/manifest/lock set; the selected route names its exact descriptor; each memory/source projection names the exact admitted parent and rights; the context successor names its governor and parent. A collection of individually valid latest reads is insufficient if they never coexisted or refer to incompatible revisions.

Two conforming capture mechanisms remain: an existing canonical snapshot/read transaction with immutable external references, or a bounded version-read-and-validate algorithm that proves a common cut under its declared consistency model. The latter must detect ABA through revision identities and retry only within the admitted allowance. Equal before/after content hashes alone do not prove a coherent dirty workspace. Use R-Y's qualified immutable/storage-snapshot or enforced-all-writer-quiescence evidence when coherence is required; bounded-observed-capture cannot be upgraded by wording. If the common cut is unavailable, return `composition_cut_unavailable` rather than guess. [R06], Q19

Cut validation is historical input coherence. Current rights still resolve at every protected read, disclosure and effect boundary. Capturing rights r1 does not freeze permission after r2 revokes it.

### Eight passes with exact rejection boundaries

| Pass | Required operation and output | Boundedness and failure |
|---|---|---|
| P1 Capture cut | Capture CompositionInputSet and CompositionReadCut; verify required refs and supported interpretations | Zero-model; fixed read/retry/byte allowance; incomplete or mixed cut holds |
| P2 Resolve eligible graph | Resolve admitted inert descriptors, exact locks/providers/conflicts and route support under effective config/current scope; emit graph and complete permitted rejection explanation | Zero-model; no code import/install/network probing to discover dependencies; cycle, ambiguity or incompatible owner blocks before autonomous work |
| P3 Protect mandatory closure | Compute non-droppable control kernel plus explicit task/workflow requirements and transitive declared dependencies, respecting phase/order | Zero-model; closure cardinality/work limits explicit; missing/disabled/denied/unavailable required member blocks, never auto-enables |
| P4 Select optional material | Filter visibility before ranking; bounded catalog/retrieval/profile selection; record complete/bounded/unknown coverage, omissions and actual proposal output | Zero-model if deterministic selector; otherwise separately admitted bounded model proposal. Search failures never prove absence |
| P5 Admit disclosure and loading | Resolve current read rights before fetching bodies/resources; admit exact recipient/purpose/content/tool schema and service-side discovery disclosure before model exposure | Required denied member holds; optional denied member omitted with disclosable reason. No model context or tool registration before this gate |
| P6 Render candidate | Build ordered segments, route-specific roles and tool bindings; stable-prefix partition; span map, actual bytes, loss and transform identities | Zero-model rendering over frozen inputs. Unknown critical role/tool semantics hold rather than emulate them through prose |
| P7 Validate fit and applicability | Verify closure, span coverage, loss policy, source/route/config bindings, current authority, finite context and full resource vector | No silent truncation. Only preapproved phase narrowing or approved loss-tolerant evidence transform; otherwise typed hold |
| P8 Install and dispatch | Governor compare-and-installs one successor for the exact parent, preserving old valid epoch; existing admission rechecks current fences at disclosure and effect | Stale parent/conflicting successor rejects; receiver installation and observed delivery are distinct from local admission; no direct compiler effect |

P5 distinguishes an already admitted local artifact read from its later disclosure to a model/search service. A hosted deferred-tool catalog is still a service-side disclosure even when the model sees less. A metadata-only selector receives only its allowed projection; it cannot enumerate prohibited or disabled payloads to improve ranking. Any external release of restricted discovery metadata, schemas or context uses the existing ExposureIntent pre-registration, potential-copy inventory and original reservation lineage before release, with current checks at release and later task publication. Remote quarantine is already disclosure to that receiver; it is not sender-private staging. These are R-SC obligations consumed by P5/P8, not compiler-owned permission records. [R06]

### Mandatory closure and fit

Let R contain canonical non-droppable controls, explicit accepted skill selections, current phase requirements and required output/gate procedures. Closure M repeatedly adds declared required dependencies until a fixed point over exact qualified identities. A cycle, incompatible requirement or missing provider yields a bounded rejection, not arbitrary tie-breaking. Optional selection O is disjoint from M; scoring may reorder O but cannot remove, summarize away or change M.

Fit is checked after exact route rendering, including schemas, wrappers, mandatory procedures, evidence, output reserve and known provider overhead bounds. An unknown critical route capacity/hidden overhead cannot be asserted to fit. Byte counts remain distinct from route-qualified token counts. Mandatory references alone do not satisfy a procedure needing its body at the next dependent step; exact body/required section must be resident or successfully rehydrated **before** that step. Phase retirement requires an accepted task/phase transition.

On overflow, first remove optional material under the declared policy and retain its omission record. Next use an already approved narrower phase whose required closure still fits and whose sequencing preserves the original task. An approved evidence transform may reduce compressible material only under its fidelity/loss gate. If no such path exists, return `mandatory_context_unfittable` with required/available units, affected refs and allowed next choices. Do not silently raise budgets, choose another route/model, relax gates, drop an inconvenient skill or call an unapproved compactor.

Disabled cost has a precise scope: zero disabled description/body/resource bytes in operational catalogs or prompts; zero tool definitions/registrations; zero selector queries over disabled content; zero payload scans/imports/network/model/callback effects. Minimal predeclared release identity metadata used by zero-model administrative inventory can remain outside these surfaces, with its own measured bookkeeping cost. It is not a zero-CPU claim and must not leak excluded count/position information through a supposedly filtered catalog. [R09][R11]

## 4 Effective artifact and deterministic versioning

### CompositionManifest candidate field contract

| Proposed field group | Exact semantic requirement |
|---|---|
| `manifest_ref`, `interpretation_profile_ref` | Immutable ArtifactRef and supported containing interpretation; domain-separated identity and complete byte coverage |
| `input_set_ref`, `read_cut_ref` | Exact frozen set and coherent-cut evidence from section 3, not a free-form timestamp |
| `compiler_ref`, `composition_policy_ref`, `render_profile_ref` | Exact versions/digests/configurations of every transform stage; no untracked locale, environment, filesystem order or live lookup |
| `goal_task_gate_refs`, `parent_context_ref` | Existing canonical exact references; active directives resolve outside summaries |
| `capability_graph_ref`, `mandatory_closure_refs` | Exact resolved graph and phase-bound mandatory members; closure rationale and dependency paths |
| `configuration_binding`, `route_binding`, `workspace_binding` | Existing typed revision/epoch/snapshot domains and application evidence, without renaming them to one epoch |
| `segments`, `ordering_constraints` | Every rendered segment's identity, class, intended role, actual route role, exact bytes/ranges, precedence/dependency edges and inclusion reason |
| `tool_bindings` | Qualified tool and supplier identities, exact schema/endpoint/adapter versions, disclosure/availability evidence and existing dispatch-gate reference; no grants stored as callable text |
| `provenance_map_ref`, `loss_record_ref` | Complete span mapping and the inherited single loss record; all omissions/unknowns and incompatible-loss refusals |
| `prefix_plan_ref`, `rendered_payload_ref` | Stable partition and exact submitted representation, with cache-affecting settings and known/unknown provider contribution coverage |
| `budget_and_meter_refs`, `validation_refs` | Original reservation lineage, fit/accounting coverage and independent validation evidence; compiler self-report is not acceptance |

The context service binds this manifest to a `context_epoch` only through an admitted transition. Epoch identity and manifest content identity are distinct. Installation/delivery/application receipts live in existing event/evidence records rather than mutating the manifest. The same immutable manifest may be retained as historical evidence after it is no longer currently usable.

The artifact is a manifest plus exact referenced representations, not necessarily a monolithic system string. It can contain tools, role-separated messages and attachments. A digest-only reference saves submitted context only if the exact route provides an admitted resolver; otherwise the required bytes must be hydrated and counted. A model cannot use an opaque identifier as though it contained the missing instruction.

### Reproduction contract

The pure assertion is: fixed complete input bytes, fixed declared interpretations/transforms and fixed actual auxiliary outputs produce the same ordered segments, semantic bindings, canonical manifest bytes and submitted payload bytes, or the same typed refusal. It is not an assertion of equal model outputs, provider hidden prompts, timings, random handles generated afresh or external state.

A candidate canonicalization profile must specify parser/dialect revision; duplicate-key and unknown-field policy; scalar and null/missing interpretation; supported numeric range and forbidden values; Unicode/encoding/line-ending rules; object/set ordering; preservation of ordered arrays and procedure order; escaping/whitespace; length framing/domain separation; and digest computation coverage, including exclusion of the digest's own field if self-referenced. No uncontrolled clock, path enumeration order, random seed, network result, locale or environment variable may affect bytes. Record necessary values explicitly or refuse.

Raw imported bytes are never silently normalized. A normalized body is a new derivative with exact parents, transform and loss. For sets, a total ordering over qualified immutable identities is permitted after conflict resolution; for sequences, preserve declared semantic order. RFC 8785 and JSON Schema 2020-12 remain candidate mechanisms [S06][S07], while existing M1's chosen profile is unchanged. This report selects no final serialization/schema format, digest technology, language or store.

A model-assisted selector or summary generator is outside this deterministic function. Freeze the actual output artifact, complete possible-influence set and generation receipt. On fresh generation, even with identical request settings or seed, capture a new output and create a new input-set identity. On reproduction, replay the recorded output bytes without calling a model. An unavailable opaque artifact gives `reproduction_input_unavailable`; a plausible replacement is not reproduction. Compiler timers and request IDs belong to execution receipts unless semantically required inputs, so incidental run metadata does not perturb the artifact.

### Recompilation and holds

| Change | Candidate action | Invalid shortcut |
|---|---|---|
| Skill, dependency, manifest or behavioral-core bytes | New exact binding, closure/conflict validation and candidate; retain old only while authorized/compatible | Same name/version range treated as same bytes |
| Tool schema, endpoint or adapter | Re-admit disclosure and dispatch semantics; new rendering/tool binding or hold | Preserve a tool merely for cache continuity |
| Route/model/harness/interface or descriptor | New compatibility/render/cache/accounting checks, preserving assignment versus descriptor identities | API feature assumed available through its CLI |
| Workspace/source fork or mutation | New exact source/capture/materialization binding and necessary evidence; current rights recheck | Same path or repository URL treated as same source |
| Memory/evidence source freshness, rights or audience | Refresh only if separately allowed; replace affected representations or hold | Old summary/existence handle treated as current permission |
| Preference revision | Follow configured target application boundary; preview pending versus effective | Requested or compiled interpreted as applied |
| Authority tightening/revocation or Stop | Immediate affected admission/read/disclosure/effect fence, then recompile/hold; retain old historical evidence under current rights | Wait for preference checkpoint or trust a cached grant |
| Missing active directive/procedure reference | Reject compacted candidate; rehydrate from authenticated retained roots or hold | Fluent summary accepted as complete |
| Conflicting successor or changed parent during background transform | Compare-and-install rejects stale parent; declared bounded rebase/new candidate if allowed | In-place mutation or last-completion-wins |

### Requested compiled and effective state

Requested is the admitted desired configuration change. Compiled is the exact validated candidate plus explanation. Effective is separately evidenced application on a named target/configuration epoch; delivery, acknowledgment or staging alone does not establish it. Both outstanding-session propagation and new-session-only behavior remain supported. Existing descendants require their own application evidence. A resumed session must revalidate what its exact route requires resent.

Revocation is a separate monotonic scoped authority fence. For preference p1, revocation r2, preference p3, coalescing delivery down to p3 cannot erase r2. New affected protected operations use current r2 even if the target still uses p1 preferences. Reject stale work at local admission immediately; report remote fence installation pending/observed/unknown separately. Already disclosed bytes cannot be undisclosed by a prompt rewrite, and already-dispatched effects retain original logical IDs/reservations until reconciled. Replacement work that could conflict waits for required receiver fences, effect reconciliation/idempotency and any required quiescence evidence. [R06], Q20[R10]

### Checkpoint content and recovery

A checkpoint is a validated durable manifest through the existing checkpoint service: exact GoalSpec/Owner-intent/accepted-directive refs; task/plan/gate; current rights/grants **references** and typed fence vector; parent/new context manifests and governor; active procedure/lock/tool/schema bindings; effective configuration and route; source, workspace and materialization refs; pending questions/approvals/queued input and their targets/expiry; completed steps and next bounded step; blockers, evidence/loss/rehydration locators; original operation/attempt identities, reservations/meters and unresolved effects; capture/commit/retention evidence. It is not a transcript dump, copied reusable approval or hidden chain-of-thought store.

On resume, authenticate the reader, resolve current authority/config/route/source, validate retained artifacts and unresolved effects, then build/admit a new candidate if needed. Historical grant references document the past; replay never activates them. Stop fences new dispatch without editing an immutable compiled epoch. Checkpoint/interrupt/drain are mechanisms within the accepted Stop semantics, not new Stop modes.

## 5 Stable prefix contract

`PrefixPlan` is a deterministic projection of the admitted artifact and exact route profile. It names ordered partitions, their exact byte ranges/digests/settings and the reason any segment is excluded from reusable placement. It is not a provider cache entry or retention guarantee.

1. Place invariant reviewed instructions and invariant admitted schemas at the earliest semantically valid positions supported by the route
2. Place stable admitted artifacts before volatile task state where that route's role/layout constraints permit it
3. Place current step, transient observations, time values, counters and route explanations in the volatile tail unless their semantics require earlier placement
4. Preserve order within active procedures, tool/result relationships and conversation causality. Use canonical tie-breaking only for independent contributions with equivalent allowed ordering
5. Reference unchanged artifacts by immutable identity in the manifest; hydrate actual required bytes wherever the route cannot resolve those references
6. Make every newly disclosed deferred tool/body a new checked addition. Append only when the qualified route supports it and existing semantic/authority requirements remain true

The logical partition need not be three physically contiguous strings. A provider may render tools ahead of instructions or restrict message placement. The render profile records the actual order and losses; unsupported required placement holds. Deterministic whitespace and stable ordering reduce accidental variation but establish no provider cache hit.

`CacheObservation` records exact operation/attempt/route/descriptor/config/context and submitted-prefix identity; requested cache treatment and actual exposed controls; observed cache reads/writes/native units and their inclusion semantics; observation source/window/clock; actual reason if supplied; unknown reason otherwise; and full workflow priming/refresh/rebuild/retry/compaction/review work. Its evidence class distinguishes documented-disabled, observed-write/reuse and unknown. A new key, process, session or elapsed TTL does not prove a cold cache. Private digests never become public correlation handles.

When a new accepted directive changes an earlier instruction, report the old/new payload and prefix identities, first changed range, directive/change reference, affected reusable suffix and observed cache counters. The disposition is **correctness-required prefix change**. Record actual rewrite/miss cost if observed; otherwise report forfeited *reuse opportunity*, with actual cache loss and money unknown. Do not claim an observed lost hit from byte inequality alone. A mandatory current instruction always wins over reuse.

Authority checks and provider caching are independent. Reusable bytes can be freshly admitted under current rights without copying old approval. Conversely, identical bytes can be forbidden for a new audience. Do not preserve a callable revoked tool, stale tool result or obsolete directive; move untrusted data into an instruction role; reorder conflicting steps; or delay revocation to improve cache statistics. If previously exposed material remains in an upstream session and the qualified route cannot enforce the required reduced surface, fence affected continuation and start a separately admitted reconstruction or hold. A local tool gate alone does not prove control over hidden upstream built-ins.

The conforming cache rival is full rebuild or reviewed precompiled workflow bundles with fresh admission. Cache-aware compilation wins only through later matched whole-workflow evidence, including a no-future-work counterfactual. No periodic keepalive, paid priming, retention duration, cache threshold or provider-specific default is adopted.

## 6 Provenance and injection safety

### SpanSourceMap candidate

Every submitted content segment, schema, attachment descriptor and wrapper is attributable. The map is bound to the exact final rendered representation, not approximate offsets in an earlier template.

| Proposed field | Required meaning |
|---|---|
| `output_ref`, `segment_id`, `coordinate_profile` | Exact artifact/segment plus explicit message/block/range interpretation; UTF-8 byte offsets when using byte spans, never unlabeled character indexes |
| `output_range` | Half-open start/end in that exact representation; bounded valid range and explicit empty/control-only disposition |
| `source_refs`, `source_ranges` | Immutable source representations and exact supported locators; multi-source transforms retain all possibly influential sources |
| `source_class`, `capability_state_evidence_ref` | Canonical control projection, reviewed template, imported procedure/schema, evidence or model-derived output; separate installed/enabled/authorized/available/selected/loaded/executed evidence |
| `adoption_or_inclusion_ref`, `purpose_recipient_binding` | Why included and for whom; canonical adoption exists separately from the content itself |
| `transform_ref`, `observed_input_set_ref` | Exact compiler/generator lineage and full possible-influence set; citations alone do not define it |
| `intended_role`, `rendered_role`, `ordering_reason` | Semantic class versus actual route placement, with any unsupported mapping/loss |
| `authority_carried_none`, `content_envelope_ref`, `loss_record_ref` | Imported/model/plugin content is true; inherited restrictions and the single coverage/loss record remain binding |

Coverage predicate: every output byte belongs to a segment and a source mapping, including generated delimiters mapped to the pinned renderer/template. Within a segment, the map covers its whole output with no unexplained gap; overlapping influence links are permitted and retain their union, but conflicting byte ownership or coordinate interpretation refuses. A transformed summary can map a span to a complete influence set instead of pretending precise causal attribution. Unknown fine-grained provenance requires conservative whole-segment scope; missing mandatory provenance holds.

The map says what was supplied, not what the model attended to, adopted or relied on. Actual tool result freshness and reading/delivery observations remain separate. A valid span map can describe false or malicious text perfectly.

### Trusted control and untrusted content

Canonical control arrives through authenticated typed services and current admission, with an explicit accepted scope. Plugin descriptions, skills, prompt templates, allowed-tools, trust flags, tool annotations, system-looking delimiters and claims of earlier approval enter through the content path with `authority_carried_none=true`. Even an authentic signed publisher cannot confer task, grant, publication, credential or billing authority. Selecting a skill accepts using its procedure only within current authorized task bounds.

The compiler may place an admitted procedure in an instruction-capable route channel when policy permits, but it must retain the imported source marker and separate adoption scope. Role placement is not authority promotion. If the route cannot maintain a required control/content distinction, declare that unsupported loss and refuse the strong-required profile rather than claim text delimiters enforce security.

Parsing sanitation ensures well-formed representation and neutralizes unintended structural delimiters where the format provides such escaping. Preserve original source bytes and record the transform. Semantic injection remains possible inside valid strings; stripping suspicious words is not proof of safety. The decisive protection is constrained capability use and current protected-boundary enforcement, with correctness/disclosure evaluation beyond authority checks.

Selectors are read-limited and return bounded qualified IDs, evidence and uncertainty; they do not receive credentials, unrestricted source stores or effectful tools. A model selector's output is a proposal. A privileged consumer must resolve each ID/version afresh, validate eligibility and task fit, enforce mandatory closure and admit exact disclosure. Compiler outputs likewise cannot write canonical settings, enable a plugin, mint a grant or dispatch an effect. No-tool selection still has an indirect influence channel and is not harmless by construction.

### Evaluation of injection defense

Test at least metadata/catalog self-selection; instruction-looking resource text; tool-schema descriptions; fabricated prior approval; a summary that launders an instruction; cross-audience content; hidden dependencies; stale results; and a malicious permitted action inside an overly broad grant. For each, evaluate task output correctness, extra disclosures, wrong source/version use, causal effect evidence and canonical authority violations separately. An attack that tricks the model into a wrong but technically permitted answer still fails task quality.

Use a useful permitted-task positive control, a prompt-only-defense negative control and an independent sink/trace oracle. The prompt-only arm is intentionally inadequate and cannot be an efficiency competitor. A candidate that refuses every request cannot win: it must complete the authorized control. Missing sink/observer evidence gives HOLD_UNKNOWN, never zero effects. Synthetic success only establishes those structural boundaries; real semantic injection resistance, covert channels, OS confinement and upstream hidden tools remain unqualified.

## 7 Conflict and precedence contract

### Declared policy without replacing constitutional precedence

The existing repository constitution's precedence is not rewritten by an in-context ordering policy. Canonical services first resolve which Owner decisions/directives are accepted, applicable and current under that constitution. If supposedly canonical records conflict without a valid amendment/adoption relation, composition holds; the compiler cannot decide governance.

Within that resolved task, `CompositionPolicy` declares applicable classes, scope, merge operator, partial-order edges, explicit override relation, conflict detector revision, refusal behavior and preview rationale. Candidate procedural precedence is:

1. Current applicable Owner instruction and accepted decision as resolved by canonical authority
2. Exact task/GoalSpec/accepted-output and gate projection derived from those records
3. Reviewed behavioral core, subordinate to that task but never a mechanism to relax canonical hard bounds
4. Explicit admitted workflow/profile choices for the current phase
5. Selected skills and declared procedure dependencies under that workflow
6. Imported facts, observations and model proposals, which cannot override any control class

This is not unrestricted most-specific-wins. Hard bounds intersect; a lower rank may narrow but not widen. Explicitly mandated skill requirements cannot be silently discarded because a higher-ranked workflow is inconsistent: produce a conflict, identify the accepted requirement and apply only an explicit authorized override/supersession or ask for a task decision. The compiler records conflicts it knows how to detect; natural-language conflict detection is incomplete and remains a quality endpoint.

Among independent same-rank compatible contributions, use a declared total tie-break over qualified identity/version after topological order. A tie-break cannot resolve incompatible format/method demands. Dependency order, procedure step order and tool/result causality precede cache ordering. Cycles, ambiguous providers, unsupported mandatory semantics and incompatible ownership reject before autonomous work, without inspecting executable payloads to resolve ambiguity.

### Conflict table

| Class and case | Deterministic disposition | Genuine rival | Falsifier | Non-proof |
|---|---|---|---|---|
| Authority: skill requests wider recipient, spend or tool permission | Deny that protected action independently of model interpretation; required action blocks the task; permitted remainder only under existing phase policy | More restrictive precompiled workflow with the same canonical gates | Imported wording or loaded/cached content authorizes a forbidden operation | Prompt obedience or absence of semantic harm |
| Procedure: valid skills demand incompatible output formats | Apply an exact adopted override relation or hold with both refs; never load-order wins | Explicit reviewed mutually exclusive workflow bundles | Arrival/filesystem order changes winner, or a mandatory conflict is hidden | Detection of every prose contradiction |
| Procedure: ordering cycle or duplicate provider | Fail graph/policy validation before body loading/dispatch | Manually selected unambiguous profile under identical checks | Arbitrary alphabetical choice or import executes before refusal | General resolver completeness |
| Evidence: sources disagree on a value or state | Preserve both source/version/locator, freshness and uncertainty; use task-specified adjudication, otherwise unresolved | Keep exact conflicting excerpts rather than a synthesized evidence summary | Summary turns disputed evidence into an accepted decision | Truth of either source |
| Same immutable slot with different bytes/interpretation | Refuse/quarantine conflict and retain evidence | Version-specific adapters with exact immutable identity checks | Digest added to lookup key lets both incompatible contents occupy one version | Collision resistance or source authenticity |

Preview and explanation are deterministic authorized projections: every included/omitted segment has a rule and source; every blocked requirement names its dependency; a proposed change displays removed/added exact refs, changed prefix, privacy/route/context/resource implications and target application boundary. Preview does not install or disclose bodies to a new audience. Rollback means proposing a prior configuration under **current** rights and compatibility, not restoring revoked grants or replaying effects. The existing configuration system remains the only settings authority.

## 8 Falsifiable scaling at a fixed budget

### Two separate claims

**Composition conformance:** identical frozen inputs reproduce bytes/refusals; required control/procedures survive; current authority gates reads/disclosures/effects; provenance and losses are complete within the declared profile.

**Workflow scaling:** adding a specified capability within unchanged allowance preserves hard floors, quality and latency and yields a preregistered useful benefit against strong paired alternatives. The second requires real independently evaluated task outcomes and human effort measurements. Synthetic compiler traces cannot establish it.

### Preregistered task and increment contract

Freeze a `ScalingStudyManifest` before outcome inspection: source/candidate/compiler/policy/corpus/oracle versions; all-assignment registry; task families and sampling/weights; capability schedule; exact eligible rights/route/config/platform/resource profiles; budget vector; arms; cold/warm/change regimes and order; endpoint definitions and practical margins; power/precision and repeat plan; multiplicity rule; missing/censored handling; human-review method/horizon; stopping rules; independent custody/rerun; and public claim scope. R-W owns scientific acceptance and R-O owns resource units/profile confirmation. Unknown prerequisites block an empirical superiority claim.

The same accepted unique tasks are assigned to every arm at every increment. Attempts, retries, repeated seeds and reviewer votes are nested within task, not independent sample size. Freeze all exclusions before treatment; after assignment, unsupported tasks, refusals, timeouts, overflows, broken runs and observer gaps remain in the cohort. A baseline that cannot complete the task does not disappear. If useful baseline competence is absent, classify capability enablement separately from an efficiency advantage.

| Increment | Exact intervention to freeze | Paired attribution rule and decisive falsifier |
|---|---|---|
| I0 Base | Lean effective capability set sufficient for the declared base workflow; disabled installs may exist only as inert inventory | Independently valid positive controls and clean baseline; otherwise comparison invalid |
| I1 Base plus plugin | One exact plugin/lock/config addition and declared procedural/tool contribution | Same task/route/resources, with and without addition. Wrong output, authority failure, reproducibility failure or latency degradation rejects that addition |
| I2 I1 plus skill set | One pinned skill set and closure, no extra allowance | Same installed eligibility in all discovery arms; missed required procedure, order/position sensitivity or review burden beyond its registered limit rejects |
| I3 I2 plus node or execution profile | Added placement/transport capability while **aggregate** CPU/memory/concurrency/model/IO budget remains fixed | Control placement separately where feasible. Extra hardware/quota is not fixed-budget scale; transfer/recovery/latency regression rejects |
| I4 I3 plus route and configuration combination | One exact admitted route/configuration option with the same total unit-specific ceilings | Separate same-route mechanism attribution from package comparison if model/interface changes. Changed quality/latency is a package outcome, not compiler-only causation |

This order is a proposed finite diagnostic schedule, not a selected product rollout or authorization to activate anything. Register alternative orders or factorial interactions before outcomes if causal interactions are claimed; nested gains are conditional on the preceding set. Do not claim one universal slope from a heterogeneous plugin/skill/node/route sequence.

For a genuine cardinality scaling check, separately freeze a same-class nested family with counts 0, 1, 2, 4 and 8 added eligible contributions, matched task difficulty and fixed rights/allowance. Required-member positions are evaluated after eligibility filtering, with front/middle/end permutations and distractors. The 20261002c corpus supplies B01–B16 and task/skill variants; reuse its exact hash and extend through a declared supplemental fixture version rather than silently rewriting its oracle labels. Mandatory dependency IDs bypass optional ranking but never admission.

### Fixed budget vector and fair arms

Per unique task define one unchanged vector B across increments and competitors: elapsed deadline; model-input/output/reasoning and total-call/attempt ceilings under exact compatible units; context bytes and route-qualified token window with output reserve; selector/compactor/verifier/retry/helper allocations; deterministic CPU, memory high-water and memory-time, disk/IO/network limits; concurrency/subtree/queue ceilings; native subscription units where enforceably available; metered-money ceiling separately; and workflow human-review/correction allowance with fixed follow-up horizon. Reserve verification/recovery capacity up front. Added nodes, subscriptions or workers redistribute B, never enlarge it unnoticed. Shared setup/integration cost is reported both unamortized and under a preregistered workload horizon, not erased from per-task totals.

If route tokens are incomparable, report each native unit and hold any cross-token aggregate claim. An unknown or unenforceable required quota bound is an admission blocker; record it rather than replacing it with estimated token-to-subscription conversion. Account reset, task fork and retries do not replenish B. Existing reservation algebra and single-count inclusion sets apply.

Compare four conforming arms at each increment:

- **A Selective composition:** exact mandatory closure plus bounded optional retrieval
- **B Complete eligible catalog:** all eligible metadata, exact bodies/resources on demand
- **C Eager admitted baseline:** complete bodies/resources for the same admitted workflow subset; overflow is a recorded outcome
- **D Explicit workflow profile:** reviewed required set, same optional budget and current-right checks

All arms get identical accepted tasks, rights, source bytes, available capabilities and budget. Profile construction/maintenance is counted; it cannot receive hidden oracle IDs denied to others. Model-assisted selection is charged as such. Keep cache state regime and native baseline features comparable. An oracle-selected subset is a diagnostic ceiling only. Prompt-only gates, missing closure and always-refuse are invalid controls, never cost-saving competitors.

### Endpoints and denominators

| Endpoint group | Required exact report |
|---|---|
| Qualified task result | Independent final acceptance, first-review acceptance, specification false greens with audited denominator/unknown bounds; wrong instruction/version, missed mandatory skill, safe refusal, incomplete and unresolved effects separately |
| Authority and privacy | Forbidden disclosure and effect counts with observer coverage; stale rights/fence use; correct refusal and useful positive-control success |
| Determinism | Same-input byte/refusal equality, missing input coverage, changed-input invalidation; actual model-output variability separate |
| Latency | Compile ingress-to-candidate, scheduled task arrival-to-first useful event, and arrival-to-independent verified outcome; p50/p95, fixed-horizon completion, failures/timeouts/censoring and queue/permission/recovery/review intervals |
| Context | Actual submitted bytes and route-qualified tokens by core, catalog, procedure, schema, evidence, attachments, wrappers and continuation; source/service disclosure bytes separately |
| All reasoning roles | Solver, selector, planner, compactor, verifier, memory/media helpers, retries and recovery; native counters, inclusion sets, meter resets and missingness |
| Local and remote resources | CPU, memory high-water/memory-time, IO/disk/network, process/wakeup/queue/subtree counts; setup, indexing, compilation, transfer and recovery |
| Cache | Observed reads/writes in native units, coverage and regime; priming, refresh, invalidation and no-future-reuse cost; unavailable is null |
| Human work | Active review/correction/reconstruction and missing-skill discovery minutes, interventions, first/final review, deferred repair and queue debt; study-only audit overhead also shown separately and combined |
| Integration tax | Install/configuration/semantic mapping, profile creation, tests/review, update repair, abandoned ports and ongoing maintenance; no unmeasured porting savings |

For resource component r, report the sum of r over **every assigned task and helper** divided by independently qualified successes, alongside total and per-assigned-task burden. If success count is zero, the ratio is undefined/null with that reason. If resource coverage is incomplete, report observed lower totals and bounded/unknown residuals; do not silently produce an exact ratio. Do not sum parent counters with included child subtotals twice. Tokens, money, native subscription units, CPU and human effort never collapse into one currency.

A latency quantile over successes only must be labeled conditional and cannot be the scaling endpoint. With failures or unfinished tasks, retain the full time-to-outcome/censoring record and fixed-horizon completion; report an unidentifiable p95 as unknown or beyond the horizon rather than fabricate a finite value. End-to-end p95 is not the sum of stage p95s.

### Independent quality oracle and statistics

The candidate cannot write expected outcomes, tests, assignment records, grader rules or evidence custody. Use independently authored end-state and causal-observation predicates, blind artifact review where feasible, and known-good plus planted-invalid controls including wrong version, missing required skill, forged receipt, wrong audience, test deletion, leaked answer and a format-only output. If a positive or adversarial control fails, invalidate the affected comparison. A deterministic scripted proposer can test the gate, not model relevance or human performance.

Predeclare paired order/randomization and task/repository clustering, repetitions, family coverage, confidence method, practical quality/latency/review margins and multiplicity across increments/endpoints. Calibrate separately; never expand a margin after observing a bad addition. Hard authority and exact-reference invariants have no tolerated statistical violation. Inconclusive non-inferiority remains HOLD_UNKNOWN. Model, evaluator and infrastructure variability are separate measurements. Real human effort requires separately admitted participants/method/custody, counterbalanced equivalent tasks, active person-time without overlap double counting and a delayed-repair horizon. No human savings can be inferred from script step counts.

For the same-class count sweep, register review effort H(n) and incremental slopes per added contribution. A concrete candidate super-linearity discriminator is increasing adjacent slopes `(H(n2)-H(n1))/(n2-n1)` beyond a preregistered practical margin with simultaneous uncertainty excluding the allowed linear envelope. Zero baseline effort is handled by absolute differences, never division by zero. Finite counts support only that tested range; heterogeneous additions or unmeasured integration work cannot establish an asymptotic growth law.

### Disposition without a hidden score

Apply these rules per addition, arm pair, workflow and exact profile; publish all raw vectors and any dissenting endpoint. These four labels are a thesis-facing projection requested by this brief, not a replacement enum for R-O/R-W. Preserve underlying INVALID_EVIDENCE, REJECT_FLOOR, NON_DOMINATED_TRADEOFF and other original validity/floor observations; a supported hard failure remains visible as such when projected to REGRESSION.

| Disposition | Necessary evidence and meaning |
|---|---|
| REGRESSION | A hard-floor/reproducibility failure, or preregistered adequately supported quality/latency degradation, or review/resource regression/integration tax violating the registered constraint. Quality, latency or authority degradation is explicitly a D-034 falsifier for that addition; other gains cannot cancel it |
| HOLD_UNKNOWN | Missing/invalid observer or oracle, noncomparable/unfrozen budget, missing critical counters, insufficient precision/power, immature review horizon or unresolved required safety evidence. A known hard failure is still reported as REGRESSION even if other endpoints are unknown |
| NO_BENEFIT | Valid complete-enough comparison establishes the registered absence of meaningful benefit while required nonregression constraints pass. This is stronger than a nonsignificant test; insufficient precision is HOLD_UNKNOWN |
| CONDITIONAL_ADVANTAGE | All hard floors pass; reproducibility and quality/latency nonregression are supported; a preregistered useful endpoint improves beyond its margin; other required resource/review constraints and independent rerun pass. Name the exact additions/tasks/budget/profile and amortization horizon |

A non-dominated tradeoff is a **separate descriptive flag**, not a fifth success verdict. If it includes established quality or latency degradation, retain REGRESSION and the D-034 falsification label; the Owner may consider a narrower utility claim without representing it as successful scale. Safe refusal may pass an authority predicate while failing task completion. More capabilities with identical outcomes and greater integration cost may establish NO_BENEFIT or REGRESSION under the registered cost constraint, never automatic advantage.

## 9 Provider free acceptance fixture suite

**Every vector below is UNEXECUTED.** They specify acceptance/refusal behavior for a separately admitted local implementation. There is no runnable target code, fabricated benchmark log, model call or simulated empirical benefit in this deliverable. Reuse the prior corpus [R18], whose SHA-256 is `5acda84e56313b628fcdded73be340fc58685b70c9bb61bf4d919e8f6e73189f`, as an immutable input; new cases are an additive fixture specification.

The independent oracle must observe actual submitted bytes, source reads, tool registrations, admission calls, canonical/context transitions, mock recipient/sink events and accounting inclusion sets. It must not trust a candidate's `pass`, `loaded`, `no_effect` or `coherent` flag. A blind observer invalidates the affected test. Each refusal vector has a valid-current authorized positive control. Nonconforming mutants remain isolated test inputs, not instructions to the researcher.

### Concrete literal specimen

For F01/F11, the synthetic route accepts three raw UTF-8 segments: the seven ASCII letters CONTROL followed by LF; the nine ASCII letters PROCEDURE followed by LF; and the four ASCII letters DATA followed by LF. Exact lengths are 8, 10 and 5 bytes; the output length is 23. Segment ranges are `[0,8)`, `[8,18)` and `[18,23)`. Sources are pinned synthetic core v1, mandatory skill v1 and public evidence v1. The first two segments form an 18-byte reusable-prefix candidate. This raw-byte specimen is a test input, not a selected product encoding.

A tail change to the four ASCII letters FACT followed by LF preserves the first 18 bytes but changes full output identity. A core change to CONTROL2 followed by LF changes the prefix, output length to 24 and following offsets to `[9,19)` and `[19,24)`. Unicode fixtures use explicit UTF-8 bytes and verify range units, including a two-byte non-ASCII character; no parser may count it as one byte. All identity hashes are computed later under the separately pinned fixture interpretation, not supplied as invented target observations here.

### Exact predicates and non proofs

| ID | Frozen intervention | Pass or refusal predicate | Decisive failure and non-proof |
|---|---|---|---|
| F01 Frozen reproduction | Same literal specimen, input refs, policy/renderer/canonicalizer and recorded auxiliary output; repeat with reversed source enumeration | Final payload equals the exact 23 bytes; manifest/provenance bytes equal under the pinned profile; no model/network call | Any difference or ambient-dependent order rejects. Does not prove arbitrary-input determinism or model generation |
| F02 Generated summary identity | Recorded summary A versus B from otherwise identical generation settings; then replay A | A and B are different actual input/output identities; replay A uses recorded A without regeneration; missing A holds | Equal seed treated as equal summary, or replacement accepted as replay rejects. No summary fidelity proof |
| F03 Mandatory closure under pressure | Required S02→S03 from prior corpus plus optional distractors; capacity admits exact mandatory set but not all optional; second case capacity below mandatory | First case loads both exact required versions before use and drops only optional entries with loss; second returns mandatory_context_unfittable without dispatch | Mandatory item omitted, summarized without approval or auto-budget increase rejects. No discovery of undeclared dependencies |
| F04 Disabled capability zero contribution | Absent versus installed-disabled S10, plus permitted enabled positive control | Disabled has zero operational catalog/body/schema/context bytes, payload scans/imports/registrations/search/model/effect events; only bounded independent administrative identity explanation may differ | Count/position leakage or any disabled payload activity rejects. No real OS inertness without independent runtime instrumentation |
| F05 Immediate revocation with coalesced preferences | Load at grant7/config p1; commit revoke8; deliver only later preference p3 while p1 remains target-effective | Next affected read/disclosure/effect refuses grant7 immediately; p3 stays pending until its valid boundary; historical load preserved; remote unknowns/liabilities retained | Preference boundary delays fence, or history erasure/rollback claimed rejects. No instantaneous remote fence guarantee |
| F06 Authority laundering | Skill/metadata/summary claims approval and tries to set authority_carried_none false | Imported representation rejects/quarantines or remains true data; protected sink sees zero unauthorized events; current authorized control completes | Content minting permission or prompt-only compliance accepted as gate rejects. No semantic injection immunity |
| F07 Procedure precedence | Two admitted exact-format requirements conflict; permute arrival order; add an explicit authorized supersession in second case | Without valid policy hold; with exact override same declared winner/order for every permutation, conflict retained | Last-loaded or alphabetical winner rejects. No universal prose-conflict detection |
| F08 Evidence conflict | Two versioned sources disagree, including a compacted derivative | Both refs and uncertainty remain; task adjudication required or explicitly resolved with evidence; no accepted decision synthesized | Smoothing disagreement into an instruction rejects. No claim which source is true |
| F09 Coherent cut | Config c2 requires schema u2 while mixed snapshot supplies c2+u1; include ABA revision change | Mixed input holds/retries within bound; valid same-cut set passes; ABA recognized by revision | Independently latest values accepted as coherent rejects. No production transaction/isolation proof |
| F10 One governor and stale parent | Two successors of c1; second finishes after accepted c2; changed directive arrives during summary | At most one authoritative successor for expected parent; stale candidate refuses or explicitly rebases with new inputs and bounds | Last-completion overwrite or duplicate epoch adoption rejects. No crash durability or liveness proof |
| F11 Prefix continuity and required forfeiture | Literal stable-tail versus changed-core cases above | Stable-tail prefix bytes equal; changed-core prefix differs with exact reason/ranges; observed cache/money remain null without source evidence | Claimed actual hit/miss/saving from bytes alone or stale core kept for reuse rejects. No provider-cache result |
| F12 Span and role coverage | Literal ranges, Unicode byte mutation, omitted wrapper mapping and imported source rendered instruction role | Every byte accounted for; invalid coordinate/gap rejects; imported source remains non-authorizing under any route role | Wrapper gap, codepoint/byte confusion or instruction-role authority promotion rejects. No attention/causal-attribution proof |
| F13 Route and schema drift | Same route assignment with descriptor d4→d5 and schema u1→u2; missing required tool visibility | Exact binding retained only if currently valid or newly admitted; otherwise hold; hidden visibility remains unknown | New descriptor silently substituted or name-only schema match rejects. No route qualification |
| F14 Checkpoint resume | Pending approval, queued input, unsettled operation O1 and reservation; compaction omits active skill once | Omitted-reference candidate rejected; valid manifest restores references but rechecks current rights; O1 identity/liability persists | Replay reapproves, reexecutes O1, resets funds or clears unknown effect rejects. No physical recovery evidence |
| F15 Graph errors before load | Missing dependency, ambiguous provider, exclusive owner conflict and cycle, each independently injected | Correct typed rejection before any body/payload import or dispatch; valid acyclic graph succeeds | Import-to-discover, automatic enable or arbitrary provider choice rejects. No exhaustive graph-solver proof |
| F16 Observer and oracle sensitivity | Remove sink observation; inject known invalid output; include valid alternate output and all-refuse candidate | Missing observer yields HOLD_UNKNOWN; invalid mutant fails and both valid outputs pass; all-refuse fails useful completion | Zero inferred from silence, format-only grading or constant reject/accept invalidates affected suite. No natural-workload false-green rate |
| F17 N increment accounting | Five increments I0–I4 × four arms A–D × six inherited tasks = 120 assigned cells; use predetermined scripted outcomes only | All 120 remain assigned; every helper/failure included once; same fixed budget vector recorded; zero-success ratio undefined; absent meters null; bad floor dominates benefit | Dropped failures, increased node budget, overlapping meter sum or synthetic quality/human savings claim rejects. No empirical scaling evidence |
| F18 Scaling adjudication sensitivity | In an otherwise complete predetermined table plant one addition's quality loss, separate latency loss, authority violation, unknown oracle, precise null benefit and clean useful advantage | Expected dispositions respectively REGRESSION, REGRESSION, REGRESSION, HOLD_UNKNOWN, NO_BENEFIT, CONDITIONAL_ADVANTAGE **for scripted adjudicator inputs only** | Any endpoint compensated through scalar score or nonsignificance mislabeled no-benefit rejects. No measured advantage follows |

### Bounded local handoff

A later local session must first obtain its own admitted task with parent goal, exact fresh source/candidate, allowed implementation/output paths, independent oracle and reviewed entrypoints. It must preserve frozen M1, protected paths and accepted decisions. This report does not authorize those writes or runs. No repository test command is invented or recommended as an already valid end-to-end compiler gate.

Proposed diagnostic scope is F01–F18 only, an isolated in-memory fake route/recipient, immutable synthetic corpus and inert source strings, with no install/import of plugin implementations, no external process/receiver, no credentials, no model/provider/account/network calls and no external effects. The separate implementation language and runner remain unselected.

For F17's **fixture-only** treatment, fix 8,192 submitted-context bytes per cell, 32,768 total admitted source-content bytes, 32 inert descriptor reads, two optional lookup proposals, one retry, one context successor per expected parent, zero model/network/external-effect allowance, and the same single-worker concurrency. Reserve 2,048 context bytes for mandatory control/output framing within that ceiling; a required closure exceeding the remaining declared fit policy must hold rather than consume another cell's allowance. Source-independent runtime containment ceilings, CPU/memory/IO/time instrumentation and numeric limits must be added and independently approved before execution; until then local execution is HOLD_UNKNOWN. These numbers are diagnostic fixture settings, not product defaults, performance targets or grants.

F17 and F18 exercise accounting/analysis over scripted records only. They may verify denominator arithmetic, missingness and label sensitivity. They cannot measure model relevance, live latency/cache/subscription behavior, real human review time or D-034 success. All actual endpoint values remain null/unmeasured here.

Before execution, freeze exact fixture/evaluator/profile bytes, all finite limits and seed/order where applicable. Run positive controls and reachable independent mutants first; failed control invalidates that comparison. Stop the affected trace on a hard-floor breach, preserve its evidence and hold dependent actions. End after the finite preregistered matrix and repeats; do not tune on held-out failures or rerun until pass. Return immutable input/output/trace/observer/oracle identities, actual counters/unknown reasons, all refusals, rejected candidates and independent verdicts. A self-authored artifact PASS is not Owner acceptance.

## 10 Recommendation and interface register

Every candidate recommendation in sections 3–9 belongs to one of these rows. Accepted inherited invariants are constraints, not proposals to weaken if inconvenient. Unsafe negative controls are not conforming rivals.

| ID | Candidate | Conforming competing option | Decisive falsifier or discriminator | Does not prove |
|---|---|---|---|---|
| C01 | Immutable manifest over a coherent input cut with separate canonical authority | Reviewed precompiled workflow bundles plus complete current-binding validation | Mixed revision/ABA or untracked input changes output; bundles meet variability/inspection needs with less total complexity | Runtime coherence, hermeticity or authority enforcement |
| C02 | Mandatory closure plus bounded optional selection | Complete eligible metadata catalog or eager admitted subset at same budget | Missing required member/phase procedure; eligible rival preserves quality with less complete-workflow burden | Universal recall or optimal selector |
| C03 | Declared pure canonical/render profile and actual generated-output identity | Version-specific immutable byte templates with exact loss mappings | Same frozen inputs differ, or model seed substitutes for recorded output | Reproducible generation or preferred serialization |
| C04 | Governor compare-and-install and separate immediate authority fence | Fully rebuild at a settled boundary while independent canonical gates fence immediately | Stale candidate overwrites newer control, duplicate successor or delayed revocation | Remote cancellation, erasure or durability |
| C05 | Stable invariant/stable-artifact/volatile-tail partition within semantic constraints | Full fresh rendering/current admission without cache optimization | Stale rights/order/data-role retained for reuse, or total-workflow gains absent | Actual cache hit, latency, money or quota saving |
| C06 | Fine-grained span map plus conservative influence union | Whole-segment provenance with exact canonical controls and stricter disclosure | Unmapped bytes, missing influential source or untenable provenance maintenance overhead | Attention attribution, truth or injection immunity |
| C07 | Least-privilege selector and proposal-only privileged consumption | Deterministic reviewed workflow selection with no model-assisted selector | Proposal creates grant/enable/effect, or extra selector overhead lacks benefit | Safe semantics inside every otherwise permitted action |
| C08 | Versioned partial procedural order with explicit override/hold | Reviewed mutually exclusive workflow bundles | Load order decides conflict, cycles pass or active mandatory requirement disappears | Detection of all natural-language contradictions |
| C09 | Whole-cohort paired four-arm fixed-budget increment experiment | Independently reviewed fixed census of the bounded workflow portfolio with same floors/vector | Budget grows, failures vanish, oracle leaks or quality/latency regression is hidden | Generalization, no-lock-in, entitlement or cheap ports |
| C10 | Independent end-state/sink oracle and known-good/mutant controls | Independent executable reference semantics plus separate black-box observations | Known bad passes, useful good fails or missing observation becomes zero | Exhaustive security/correctness or human savings |
| C11 | Versioned per-target composition preview/application projection | Simpler read-only manifest inspection with same canonical commands | UI/mobile claims effective from compiled/ACK, leaks excluded metadata or becomes settings authority | Client security or exact platform qualification |

### Joins with R UI and R MOB

Both client lanes consume authorized projections of the same effective configuration content, target application generation, graph/artifact identity, composition-policy revision, route assignment, descriptor revision and context epoch. These are a **typed reference vector**, not a new generic capability epoch. A node/process incarnation is separate again. R-PC's manifest supplies inclusion/omission/conflict/provenance/loss and fit explanations; it cannot mint client capabilities or commands.

R-UI renders current supported controls and discloses requested/compiled/effective/application-pending states. R-MOB uses connected-only control with no offline autoexecution queue. Any private last-synchronized view additionally depends on the still-undecided Owner retention policy; this report grants no offline retention. A permitted cached manifest cannot authorize a command or disclosure. Reconnection may reconcile receipts for previously submitted ambiguous commands without creating a new dispatch. Retained read-only receipt facts remain distinct from canonical admission, observed delivery and settled effects. Both clients submit connected control through the existing authenticated idempotent command boundary, preserving canonical command key `(admitted_authority_domain, command_id)` and content-digest conflict checks. Neither lane recomputes authority from displayed prompt text.

The common controls remain Aggressive/Full/Lazy plus checkpoint/interrupt/drain, with scope and receipt facts intact. Closing a view/window/socket neither changes the compiled context nor means Stop. Unsupported critical schema/capability semantics disable the relevant action and show a typed blocker; no guessed command translation or hidden fallback. Rich views and mobile push payloads receive only independently admitted redacted projections; raw prompts/private digests need their own existing rights. Client framework, schema encoding, transport, push provider and credential design remain outside this lane's selection authority.

## 11 Completion coverage and remaining unknowns

### Research questions

| Question | Answer location | Disposition |
|---|---|---|
| Q01 Exact inputs and coherent cut | Section 3 input table and read-cut predicates | Candidate specified; runtime cut unverified |
| Q02 Ordered passes and zero-model/refusal | Section 3 P1–P8 | Complete design; unexecuted |
| Q03 Mandatory closure and unfittable context | Section 3 closure/fit; F03/F15 | Exact required behavior; unexecuted |
| Q04 Effective prompt artifact | Section 4 CompositionManifest; section 6 span map | Additive candidate; no final format |
| Q05 Determinism and actual summary output | Section 4 reproduction; F01/F02 | Conditional deterministic function specified; unmeasured |
| Q06 Triggers and one governor | Section 4 matrix and F10/F13 | Candidate transition/holds; unexecuted |
| Q07 Requested compiled effective and revocation | Section 4 state/fence; F05 | Immediate local fence and remote uncertainty explicit |
| Q08 Checkpoint | Section 4 checkpoint; F14 | Durable-manifest obligation, no persistence proof |
| Q09 Stable prefix | Section 5 | Contract specified; no hit evidence |
| Q10 Provider invalidation and observed evidence | Section 2 provider table; section 5 observations | Current source-documented constraints; route evidence unknown |
| Q11 Authority and correctness versus reuse | Section 5 prohibitions; F05/F11 | Hard constraints preserved |
| Q12 Changed-directive forfeiture | Section 5; F11 | Opportunity versus observed miss distinguished |
| Q13 Span-to-source provenance | Section 6 map and coverage; F12 | Exact candidate predicate |
| Q14 authority_carried_none and channels | Section 6 control/content; F06 | Canonical enforcement required; no prompt-only boundary |
| Q15 Injection amplifier prevention | Section 6 least privilege/proposals | Candidate scope; runtime unqualified |
| Q16 Correctness disclosure and negative control | Section 6 evaluation; F06/F16 | Separate endpoints and useful positive control |
| Q17 Three conflict classes | Section 7 table; F07/F08 | Exact disposition; prose detection incomplete |
| Q18 Declared precedence and cycles | Section 7 policy; F07/F15 | Constitution retained; policy candidate |
| Q19 Inspectable reversible policy | Section 7 preview/rollback; section 10 joins | No second settings store |
| Q20 Fixed-budget increment experiment | Section 8 I0–I4 and four arms | Preregistration candidate; not admitted/run |
| Q21 Full endpoints and whole cohort | Section 8 endpoint/denominator contract | Nulls, helpers, failures and review retained |
| Q22 Falsifiers and dispositions | Section 8 table and super-linearity rule; F18 | D-034 falsifier cannot be compensated |
| Q23 Provider-free fixtures | Section 9 F01–F18 | Exact predicates; every target case UNEXECUTED |

### Completion gate

| Gate | Evidence in this deliverable | Limit |
|---|---|---|
| G1 Pipeline, coherent cut, closure and typed overflow | Section 3; F03/F09/F15 | Proposed behavior only |
| G2 Determinism, versioning, effective states, revocation, checkpoint | Section 4; F01/F02/F05/F10/F14 | No compiler or persistence measurement |
| G3 Stable ordering, current provider evidence, honest forfeiture | Sections 2/5; F11 | No live cache evidence |
| G4 Span map, non-authorizing content, split channels, actual harm evaluation | Section 6; F06/F12/F16 | No production injection/security guarantee |
| G5 Conflict classes, precedence, ambiguity/cycle refusal and reversibility | Section 7; F07/F08/F15 | Natural-language conflict completeness unknown |
| G6 Fixed-budget scaling, oracle, whole resource vector, denominator and falsifier | Section 8; F17/F18 | Quality, human effort and empirical benefit unknown |
| G7 Provider-free fixture suite | Section 9 | No target fixture executed |
| G8 Rival, falsifier and non-proof for recommendations | Section 10 C01–C11 | No technology selection or Owner adoption |
| G9 Explicit non-proofs | This section and every fixture/recommendation | No measured determinism/quality/latency/resource/cache/subscription/porting result; no entitlement, route qualification or new security boundary |
| G10 Protected paths and privacy/secret hygiene | Only self-authored deliverable/QA files changed; source is read-only; static checks recorded separately | Pattern scans cannot establish absence of every possible secret; no secret-bearing input was requested |

### Smallest remaining evidence

1. Owner review of the proposed semantic joins and precedence interpretation without altering frozen M1
2. Independently authored known-answer bytes, admission/sink oracle, supported canonical/render profiles and finite local runtime ceilings
3. A separately admitted provider-free compiler implementation and F01–F18 execution, followed by independent exact-candidate verification
4. Exact route/platform and observer qualification, including hidden tool/helper coverage and receiver fences where required
5. A separately authorized empirical study with accepted cohort, thresholds, sample size, human-review protocol, fixed budgets and source/candidate/oracle custody
6. Independent rerun and explicit adoption before promoting any claimed advantage or default

No stack, retrieval technology, schema/serialization, vendor/model, transport or new authority store is selected. No part of this report qualifies a route, grants entitlement, proves prompt-only security, proves cheap porting or reopens accepted Owner decisions. D-034 remains a claim to earn for each addition at a named fixed budget.

## Pinned repository references

[R00]: https://github.com/NotSkittlz/recursion/commit/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97

[R01]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/CONTROL_PLANE.md

[R02]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/ANCHOR.md

[R03]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/AGENTS.md

[R04]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/state/DECISIONS.md

[R05]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/Recursion_Prompt_Plugin_Skill_Architecture.md

[R06]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/Recursion_Shared_Contract_Reconciliation.md

[R07]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/Recursion_Harness_Orchestration_Performance.md

[R08]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/CONTEXT.md

[R09]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/PLUGINS-AND-EDITIONS.md

[R10]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/CLI.md

[R11]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/M1B-WIRE-PROFILE.md

[R12]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/PERFORMANCE-PLAN.md

[R13]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/ro/report.md

[R14]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rw/report.md

[R15]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rq/report.md

[R16]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/dot-ra-rd-20261002/raw/R-A/report.md

[R17]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/INTERFACE-STRATEGY.md

[R18]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/synthetic_benchmark_corpus.json

[S01]: https://agentskills.io/specification

[S02]: https://agentskills.io/client-implementation/adding-skills-support

[S03]: https://modelcontextprotocol.io/specification/2026-07-28/server/tools

[S04]: https://modelcontextprotocol.io/specification/2026-07-28/server/resources

[S05]: https://modelcontextprotocol.io/specification/2026-07-28/server/prompts

[S06]: https://www.rfc-editor.org/rfc/rfc8785.html

[S07]: https://json-schema.org/draft/2020-12/json-schema-core

[S08]: https://aclanthology.org/2024.tacl-1.9/

[S09]: https://developers.openai.com/api/docs/guides/prompt-caching

[S10]: https://developers.openai.com/api/docs/guides/tools-tool-search

[S11]: https://developers.openai.com/api/docs/guides/compaction

[S12]: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

[S13]: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching

[S14]: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool

[S15]: https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages

[S16]: https://platform.claude.com/docs/en/build-with-claude/compaction

[S17]: https://ai.google.dev/gemini-api/docs/caching

[S18]: https://ai.google.dev/gemini-api/docs/interactions-overview

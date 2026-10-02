# Recursion capability driven UI projection contract

Research candidate for Lucas · 2026-10-02 UTC · R-UI  
Parent goal: `goal-recursion-v3-harness-orchestrator`  
Candidate revision: `recursion.ui-contract@candidate-2`  
Source pin: `b696f6ece243b48c94fc0bbc7ee1d4b284c46f97`  
Disposition: additive specification and provider-free handoff; target implementation and all runtime fixtures **UNEXECUTED**

Correction note: `recursion.ui-contract@candidate-2` supersedes the first-delivery `candidate-1` schema for identity resolution. It qualifies host-resolved contributions, nodes and bindings, defines local-link and repeated-node resolution, and rejects conflicting duplicate identities. The first delivery remains historical; its schema identity is not reused. Semantic contribution-point `@1` names and meanings are unchanged. This corrects specification ambiguity, not an observed runtime defect.

## Findings and decision boundary

The strongest candidate is an inert, typed contribution description compiled into a bounded semantic UI tree by a trusted client materializer. It extends the existing capability graph and R-L command/query catalog. A view receives authorized projections and constrained command references; the existing backend remains the only admission path. Plugins never bring their own canonical writer, credential custody, authority store or actor lifetime into the view.

Three corrections make the thesis testable:

1. Equal capability sets and projections are insufficient for equal UI trees. Freeze the client profile, materializer, schema and mapping revisions, authorized source cuts, locale, formatting and layout inputs. Different clients must preserve facts and command meanings with explicit presentation losses; they need not produce identical pixels or identical layout trees
2. Fail-closed must not mean that a plugin can hide Stop, a pending approval, a replay gap or an incompatibility. The host-owned safety and continuity shell survives missing, unknown, disabled or hostile optional contributions. Unknown behavior remains unavailable and explained
3. Backend revocation can immediately fence newly admitted work after the authoritative revocation boundary. A disconnected device cannot instantly learn it or erase previously delivered bytes. Online removal, client-observed revocation, governed cached redisplay and physical erasure are separate assertions. Private offline retention remains an Owner policy question

The current clarification restricts mobile remote control to a live authenticated connection to the running backend. An always-on Linux backend is an intended deployment shape, not evidence that the phone is connected and not authorization to deploy one. Disconnected clients do not accumulate an automatic action queue. Reconnection may reconcile the receipt of a previously submitted uncertain command; it must not blindly retry or mint a new effect.

No language, store, framework, UI toolkit, renderer, transport, wire encoding, vendor or final security mechanism is selected. Nothing qualifies a route, entitlement, measured performance, accessibility conformance, cross-view security isolation or porting cost. Comprehensive opt-in delivery, native and upstream paths, and the accepted Owner decisions remain intact.

## Evidence and source continuity

**SD** means source-documented. **LO** means static source or artifact observation. **IN** means this report's design inference. **U** means unknown or unmeasured behavior. All candidate schemas, thresholds, rules and fixtures below are IN unless a source requirement is explicitly identified. Their runtime enforcement is U. A historical recorded PASS is SD/LO here, never newly observed execution.

The read-only export contains all 1,401 tracked blobs and 196 verified Git trees, root `a866969c9346372dcf74c2f05a7f9d648c766494`. Current master includes PR149 (`e2e02af1712de8fc388883bc65c150ad1138ee96`) followed by PR148. The five attached packet files match that source. The older research reports retain their original pins; their inclusion at the new pin does not upgrade their evidence class.

The governing precedence is Lucas's current instruction, CONTROL_PLANE, product specifications, decisions, implementation/evidence and runtime state. [Authority][R-AUTH] [Decisions][R-DEC]

| Inspected source at the current pin | Retained responsibility and additive R-UI work |
|---|---|
| INTERFACE-STRATEGY | One semantic command/query meaning; ten controls; three Stops; separate receipt facts. R-UI adds presentation contribution types, never competing operations [R-IS] |
| TERMINAL-RUNTIME and frozen M1B | Runtime-owned actors/processes; passive viewers; distinct input/resize leases; bounded credit/cursors. R-UI stays outside the closed wire union [R-TR] [R-M1B] |
| PERFORMANCE-PLAN | OR-024 full vector and PERF-010 view matrix. R-UI adds a contribution-count axis, without replacing the view-count axis [R-PERF] |
| PLUGINS-AND-EDITIONS and R-A | Deterministic graph, inert manifests, separate declared requests/current grants, conflicts, resource limits and lifecycle. R-UI refines its UI contribution family [R-PLUG] [R-RA] |
| R-L | OperationDescriptor, CommandIntent, QueryRequest, ProjectionSnapshotManifest, ReceiptFacts, InteractionRecord, ContributionDescriptor and IntegrationBinding. R-UI references these meanings [R-RL] [R-RLC] |
| R-K | Task-focused TUI, keyboard controls, line fallback, untrusted terminal parsing, layout/Unicode profiles and control reserve [R-RK] |
| R-N | Replaceable GUI, same-cut comparison, rich-view/accessible alternatives, detached lifetime and cache honesty [R-RN] |
| Shared contract reconciliation | Exact four-field ArtifactRef; eighteen-field ContentEnvelope; single loss record; canonical command key; independent fence/epoch/receipt domains; current disclosure [R-SC] |
| Prompt plugin skill companion | Seven independent capability states and selective discovery; UI adds client support/render disposition, not an eighth execution state [R-PS] |
| Orchestration companion and inert corpus | Separate semantics/interface/transport/topology/route; bounded independent oracle; corpus is data, all proposed execution unexecuted [R-ORCH] [R-CORPUS] |
| GAPS | G-09 privacy/publication order remains undefined; G-10 renderer/runtime and G-19 containment remain open; D-020/022/028 close Owner decisions, not all behavior gates [R-GAPS] |

D-018 through D-034 were inspected. Particularly: D-019 is not permission to reduce the accepted release; D-022 fixes vocabulary; D-023 sets qualification order only; D-024 fixes continuity; D-028 fixes later platform floors; D-029 requires a trusted launch boundary beyond policy-only credential non-intermediation; D-031 forbids unmeasured savings/vendor-intent claims; D-033 preserves the port-cost hypothesis; D-034 makes GUI/mobile optional clients and remote execution an independent backend capability. Older first-release GUI exclusions still conflict with D-019's packaging wording; this report does not silently resolve that timing issue.

## Primary public evidence

All sources in this section were retrieved on **2026-10-02 UTC**. Date-pinned documentation is not an immutable build pin. These short capsules are the entire public-source factual basis; later contract details are Recursion-specific candidate synthesis. No verbatim prose is quoted.

| Source and version | Narrow finding and limit |
|---|---|
| JSON Schema Draft 2020-12 core | A dialect identifies vocabularies; unknown keywords may be annotations. Therefore generic schema parsing does not establish fail-closed security semantics. Duplicate JSON members need rejection before object formation. [P01] |
| JSON Schema 2020-12 validation | Assertions constrain structure; annotations such as defaults are not evidence that an action occurred. Schema validation cannot establish current grants or effect safety. [P02] |
| RFC 8785 JCS, June 2020 | Canonical JSON ordering/serialization preserves strings without Unicode normalization. It does not define semantic precedence, authority, a digest algorithm or private identity domains. [P03] |
| MCP 2026-07-28 versioning | Current requests carry protocol version independently; extensions are capability-negotiated. Legacy 2025-11-25 uses initialization negotiation. Do not implement a current client from the legacy lifecycle shape. [P04] |
| MCP 2026-07-28 tools | Tools have names and schemas, may be exposed through different UI patterns, and their annotations are untrusted absent a trusted source. Authorization can affect the returned tool set; display names do not disambiguate multiple servers. [P05] |
| MCP 2026-07-28 resources | Resources expose URI-addressed data with host-controlled incorporation and optional subscription capabilities. This supplies a declaration precedent, not a Recursion view contract. [P06] |
| MCP 2026-07-28 prompts | Prompts are user-selected server-defined templates with discovery and retrieval. User-controlled invocation does not mean user-authored content. Current prompt requests carry per-request metadata. The rendered page failed; the official repository source was retrieved. [P07] |
| VS Code contribution points, date-pinned | Manifests declare commands, menus, views and configuration. Opening a contributed view can activate its extension. That activation behavior conflicts with Recursion's zero-activation-on-view rule unless explicitly adapted. [P08] |
| MCP Apps specification 2026-01-26, mutable main | The extension describes HTML resources, host/view messaging and a different-origin sandbox proxy for web hosts with policy-limited resources. Optional bridging does not establish Recursion admission or permission. [P09] |
| VS Code webview guidance, date-pinned | Restrict capabilities and local resources; use content security policy and input sanitation. Resource roots alone are incomplete protection. These are mechanism requirements, not a proven boundary here. [P10] |
| Android WebView native bridge risk guidance, date-pinned | JavaScript bridges and message channels can expose host powers to untrusted frames or origins. A bridge needs explicit restrictions; its existence is not evidence of isolation. [P11] |
| WCAG 2.2 Recommendation | Relevant criteria cover semantics, color-independent meaning, keyboard access, focus, target size, reflow and status messages. A declared semantic tree cannot certify rendered conformance. [P12] |
| WCAG Understanding Keyboard | Functionality must be keyboard operable without a timing-dependent keystroke requirement, subject to the criterion's path-dependent exception. Recursion controls require a keyboard-complete path. [P13] |
| WCAG Understanding Animation from Interactions | Interaction-triggered motion can be disabled unless essential; this is an AAA criterion. Recursion's reduced-motion candidate is a product floor, not a claim that WCAG AA requires every AAA behavior. [P14] |
| WCAG Understanding Status Messages | Status changes can be programmatically determinable without moving focus. Avoid treating every streamed token as an urgent announcement. [P15] |
| WCAG Understanding Focus Not Obscured Minimum | A keyboard-focused component must not be entirely hidden by author-created content. A persistent Stop strip must not cover the current control. [P16] |
| Microsoft UI Automation | Windows applications expose programmatic UI information to assistive tools and automation. Exact control patterns and real assistive behavior require profile testing. [P17] |
| Apple accessibility integration | Standard controls supply baseline semantics; custom controls require appropriate accessibility properties/protocols and testing. Indexed official content was available; direct page output was JavaScript-only. [P18] |
| AT-SPI 2.0 reference, library 2.62.0.1 | The API exposes accessible objects and action/text/selection/table interfaces. Availability of those interfaces is not evidence that a Recursion renderer maps them correctly. [P19] |

These precedents support typed declarations, explicit negotiation and semantic accessibility. They do not prove a cheap port, a safe arbitrary-widget runtime or a universally portable visual tree. Imported behavior must pass the same candidate fixtures as first-party behavior.

## Contribution point taxonomy

**IN, recommendation U01.** The exact recognized semantic point catalog for candidate-2 is below. `recursion.ui.*` is a reserved registry namespace: third parties may target the listed public points but cannot define/redefine a point, impersonate a core supplier, or replace the host-owned shell. `@1` is a proposed major semantic version, not a production wire version. Immutable point/schema digest resolves minor revisions; range resolution records one exact result before use.

Stability classes are `core-required`, `stable-extension`, `experimental-extension` and `client-local`. The first two are normative **inside this candidate** only. Adoption is still Lucas's decision. Mandatory means the host can expose the underlying fact/control, not that every screen must contain every widget at once.

Common required inputs for every point are authorized subject/scope, typed projection binding, source cut/freshness/coverage, exact supplier/contribution identity, accessibility description and finite resource envelope. Optional inputs are explicitly enumerated below; absent optional inputs never manufacture facts. Permitted commands are references to exact R-L catalog operations, not script callbacks. The host always mediates dispatch.

| Point | Class and typed payload | Required point-specific input | Optional input and permitted operations | Accessible fallback and degradation |
|---|---|---|---|---|
| `recursion.ui.control@1` | core-required; `ControlSet` | target/ownership scope; operation descriptors; route loss; current Stop/read/control status | input/resize lease state; catalog-bound Stop/resume/checkpoint/interrupt/drain | Persistent named command path with mode/scope/reason; cannot be removed by extension failure |
| `recursion.ui.continuity@1` | core-required; `ContinuityFacts` | separate receipt/effect facts; replay coverage; source freshness | context/config/route transitions and unresolved holders; inspect only | Linear labelled facts and visible GAP; unknown is text, not color/spinner |
| `recursion.ui.conversation@1` | stable-extension; `ConversationStream` | task/attempt/turn-tagged ordered content and cursor domain | bounded transcript page, composer state; explicit queue or steer operations | Sanitized paged transcript plus typed composer; raw terminal controls never forwarded |
| `recursion.ui.work@1` | stable-extension; `WorkCollection` | authorized task/role/run identities and relationships | declared sort/filter, lineage edges; inspect and exact task operations | Bounded list/adjacency representation; no layout-implied ownership |
| `recursion.ui.attention@1` | core-required; `AttentionCollection` | current durable interaction ID/generation/revision; exact action/question; expiry | conflict/resource/unresolved-effect entries; answer/cancel/respond using current waiter | Ordered labelled interaction forms/list; host owns approval styling and action preview |
| `recursion.ui.artifact@1` | stable-extension; `ArtifactInspection` | exact ArtifactRef or scoped handle; ContentEnvelope reference; authorized representation | diff base, evidence, verification; inspect/export/open only through distinct catalog operations | Text metadata plus authorized linear content/diff or explicit unavailable representation |
| `recursion.ui.command@1` | core-required; `CommandCollection` | operation identity/version/schema; supplier; requirements/target kinds | alias/search labels and argument forms; same operation invocation | Discoverable bounded command list and typed error details; mandatory controls reachable without palette search |
| `recursion.ui.notification@1` | stable-extension; `NotificationFacts` | authorized minimal notification fact and source reference | expiry, priority, routing preference; inspect destination only | In-app attention entry; no push/OS notification without separately admitted capability |
| `recursion.ui.settings@1` | stable-extension; `ConfigurationInspection` | requested/effective values, source scopes/revisions, limits and application state | permitted edit schema and diff; existing preview/compare-and-apply/rollback operations | Line-oriented explain/diff/form; read-only if mutation semantics unsupported |
| `recursion.ui.environment@1` | stable-extension; `EnvironmentFacts` | exact route/interface/build/config profile and capability knowledge | node/process/lease/resource facts; inspect or separately catalogued controls | Labelled facts with units and unknowns; no credential value or automatic health probe |
| `recursion.ui.rich@1` | experimental-extension; `RichRepresentation` | separately authorized representation ref; isolation profile ref; equivalent fallback ref | bounded purely presentational interactivity; named mediated handles only | Fall back to its point's supported semantic representation; absent equivalent required meaning blocks affected action |

A rich representation decorates one supported semantic point; it cannot carry unique hidden control semantics. `RichRepresentation` names its semantic parent and fallback. An unknown rich revision cannot invalidate the host's known Stop or continuity implementation.

Client-local points use `client.<registered-client-id>.ui.<local-id>@<major>`. Examples are a split-handle, tab strip, pane geometry, theme preview and local animation. They may consume already authorized data and presentation-local operations, but cannot define a command meaning, canonical fact, new subscription audience or authority. They live only in the client-profile interpretation and local layout artifact; they never leak into the shared semantic point registry or canonical operation namespace. Unsupported client-local data is ignorable only when the pinned profile marks it non-semantic and provides no hidden effect.

## Contribution schema and ownership

**IN, U02.** Attach a detached `UiContributionSet@candidate-2` to the admitted R-A manifest/installation binding by exact references. Do not add a `ui` field to frozen `PluginManifest@1`, alter its digest or reinterpret `ResourceEnvelope@1`. A future reviewed manifest revision could embed the same data; this detached candidate preserves frozen M1 today.

The following tables are an exact, language-neutral type schema. Every named field is required unless explicitly marked optional. Records are closed; no extra fields. `List<T>` preserves order; `Set<T>` has no duplicates and uses the canonical key sort stated below. `Maybe<T>` is `{state: known, value:T}` or `{state: unknown|unavailable|stale|invalid|redacted|not_applicable, reason:Text}`; non-known variants have no value. Absence, known-empty, unknown and not-applicable differ. Bounds are supplied by the mandatory profile, not unbounded by omission.

Primitive types: `Id` is case-sensitive ASCII `[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*`; `Version` is an exact nonempty immutable version string; `Text` is valid Unicode text rendered as data; `Bool` has two values; `UInt` is a nonnegative integer, never a boolean; `Ref` is exactly the existing four-field ArtifactRef under its containing digest interpretation; `CatalogRef` is `{id:Id, version:Version, schema_ref:Ref}`. References are locators, never permission by possession. Counts/durations/bytes include fixed units in their field names. Candidate illustration with JSON Schema 2020-12 would use closed objects, required members and tagged `oneOf` unions; schema URLs are resolved only from locally pinned inert schema artifacts.

| Record | Exact fields and types | Ownership and checks |
|---|---|---|
| `UiContributionSet` | `type` constant `UiContributionSet@candidate-2`; `supplier:Supplier`; `manifest_ref:Ref`; `schema_ref:Ref`; `contributions:Set<UiContribution>` | Author declaration, untrusted; installation binding verifies exact manifest/artifact closure before selection |
| `Supplier` | `component_id:Id`; `version:Version`; `artifact_ref:Ref`; `dependency_lock_ref:Ref` | Never contains effective grants, credentials or a host-populated grant field |
| `UiContribution` | `contribution_id:Id`; `point:CatalogRef`; `stability` enum above; `required_for:Set<CatalogRef>`; `projection_inputs:Set<ProjectionInput>`; `command_bindings:Set<CommandBinding>`; `presentation:Presentation`; `accessibility:Accessibility`; `resources:UiResources`; `fallback:Fallback`; `lifecycle:Lifecycle`; `provenance_envelope_ref:Ref` | Qualified identity is the full Supplier tuple plus local ID. `required_for` is a declaration checked against accepted workflow policy; author cannot impose arbitrary new mandatory work |
| `ProjectionInput` | `input_id:Id`; `projection:CatalogRef`; `field_set:Set<Id>`; `subject_kinds:Set<Id>`; `required:Bool`; `coverage_required` enum `complete|declared-partial`; `max_items:UInt`; `max_bytes:UInt` | Static request only. Actual audience/cut/content is an authorized `ProjectionBinding`, never a direct state/query object |
| `CommandBinding` | `binding_id:Id`; `operation:CatalogRef`; `argument_map_ref:Ref`; `target_map_ref:Ref`; `required_projection_inputs:Set<Id>`; `requirements_ref:Ref`; `invocation_class` enum `deterministic-control|assistant-request|engine-extension`; `connected_required:Bool` | Maps explicit user intent to existing R-L CommandIntent; no eval, shell, URL command or direct adapter callback |
| `Presentation` | `semantic_kind` enum of the eleven payload names above; `template_ref:Ref`; `message_catalog_ref:Ref`; `stable_order_key:Id`; `semantic_parent:Maybe<Id>` | Template is bounded declarative data, no general computation. Rich requires known semantic parent; other kinds use not_applicable |
| `Accessibility` | `name_key:Id`; `description_key:Maybe<Id>`; `role` enum `group|list|status|log|form|button|table|document`; `reading_order:List<Id>`; `keyboard_actions:Set<Id>`; `status_announcement` enum `off|polite|assertive`; `non_color_labels:Bool`; `reduced_motion_static:Bool`; `focus_policy` constant `host-owned`; `fallback_complete:Bool` | Key references resolve against the frozen localized catalog. Assertive status requires host classification, never plugin preference alone. Reading-order IDs are unique in explicit semantic order, not ID sort. All action bindings must have labelled keyboard equivalents |
| `UiResources` | `max_nodes:UInt`; `max_depth:UInt`; `max_input_bytes:UInt`; `max_output_bytes:UInt`; `max_queue_events:UInt`; `max_queue_bytes:UInt`; `max_memory_bytes:UInt`; `max_work_units:UInt`; `max_cpu_millis:UInt`; `max_update_hz:UInt`; `max_subscriptions:UInt`; `max_lifetime_millis:UInt` | Declared upper bounds intersect admitted per-contribution and global profile; missing finite bound blocks selection. Work-unit counting version is pinned. Zero disallows that activity; no unknown→zero conversion |
| `Fallback` | `kind` enum `semantic-linear|host-placeholder|refuse-protected-action`; `fallback_ref:Maybe<Ref>`; `preserves_operations:Set<CatalogRef>`; `loss_policy_ref:Ref` | Semantic-linear requires known locally pinned fallback. Preservation is verified, not trusted from author claim; host-placeholder carries no active plugin command |
| `Lifecycle` | `activation` constant `explicit-existing-admission`; `render_effects` constant `none`; `detach` constant `unsubscribe-only`; `revocation` constant `fence-and-invalidate`; `cleanup_deadline_millis:UInt` | Opening, rendering, focusing, splitting and restoring a view cannot import or activate plugin implementation |

Each table's nonnegative bound is constrained further by the candidate experiment profile: nodes/depth/input/output/queue/memory/work/CPU/lifetime must be positive for a selected rendered contribution; zero subscriptions is legal for a static view; zero update rate means eventless static content. A positive numeric declaration is not evidence that a runtime enforces it.

`ContentEnvelope` is reused by reference with **all eighteen existing fields unchanged**, including `project_and_audience`, `privacy_domain_id`, `retention_rights`, `observed_input_set`, `coverage_and_loss`, and `authority_carried_none=true`. No nineteenth base field is invented. The manifest's origin, signature, claimed author or trust tier never supplies current read/effect authority. [R-SC]

### Exact point payload union

The payload names in the taxonomy are discriminators of the following closed **candidate read-projection** union, not claims that these types already exist in R-L or M1B. Each record has `type` fixed to its name plus `@candidate-2`, and exactly the fields below. Each `Ref` resolves to the named existing fact/projection family under its pinned schema; unavailable values use `Maybe<Ref>` and never an invented empty record. The corresponding ProjectionInput catalog/schema reference identifies this exact discriminator and field set. Ref resolution occurs at the authorized projection service; a renderer receives only the bounded materialized subset. Lists preserve the canonical source projection's order. These add no field to ContentEnvelope.

| Discriminator | Exact additional fields and types |
|---|---|
| `ControlSet` | `target_scope_ref:Ref`; `operations:Set<CatalogRef>`; `route_support_ref:Ref`; `current_control_status_ref:Ref`; `viewer_lease_status:Maybe<Ref>` |
| `ContinuityFacts` | `subject_ref:Ref`; `receipt_facts_ref:Ref`; `effect_facts_ref:Ref`; `source_cut_ref:Ref`; `replay_coverage_ref:Ref`; `context_transition:Maybe<Ref>`; `configuration_transition:Maybe<Ref>` |
| `ConversationStream` | `task_attempt_turn_ref:Ref`; `ordered_item_refs:List<Ref>`; `source_identity_ref:Ref`; `cursor_binding_ref:Ref`; `coverage_loss_ref:Ref`; `composer_state:Maybe<Ref>` |
| `WorkCollection` | `scope_ref:Ref`; `ordered_subject_refs:List<Ref>`; `relationship_projection_ref:Ref`; `sort_filter_ref:Ref`; `coverage_loss_ref:Ref` |
| `AttentionCollection` | `scope_ref:Ref`; `ordered_interaction_refs:List<Ref>`; `current_waiter_bindings_ref:Ref`; `action_disclosure_ref:Ref`; `coverage_loss_ref:Ref` |
| `ArtifactInspection` | `artifact_ref:Ref`; `content_envelope_ref:Ref`; `representation_ref:Ref`; `diff_base:Maybe<Ref>`; `evidence:Maybe<Ref>`; `verification:Maybe<Ref>` |
| `CommandCollection` | `scope_ref:Ref`; `operations:Set<CatalogRef>`; `supplier_bindings_ref:Ref`; `support_loss_ref:Ref`; `argument_form_refs:Set<Ref>` |
| `NotificationFacts` | `subject_ref:Ref`; `authorized_fact_ref:Ref`; `source_ref:Ref`; `expiry_ref:Ref`; `priority_policy_ref:Ref`; `navigation_target:Maybe<Ref>` |
| `ConfigurationInspection` | `scope_ref:Ref`; `requested_effective_ref:Ref`; `provenance_ref:Ref`; `application_facts_ref:Ref`; `constraints_ref:Ref`; `edit_schema:Maybe<Ref>`; `candidate_diff:Maybe<Ref>` |
| `EnvironmentFacts` | `route_input_manifest_ref:Ref`; `capability_facts_ref:Ref`; `node_process_facts:Maybe<Ref>`; `resource_facts:Maybe<Ref>`; `viewer_lease_facts:Maybe<Ref>` |
| `RichRepresentation` | `semantic_parent_ref:Ref`; `representation_ref:Ref`; `content_envelope_ref:Ref`; `isolation_profile_ref:Ref`; `fallback_ref:Ref`; `mediated_command_bindings:Set<Id>` |

Ref-target constraints are part of the catalog schema, not inferred from field spelling. For example, `current_waiter_bindings_ref` must resolve to exact R-L InteractionRecord identities/generations/revisions and `receipt_facts_ref` to the shared independent fact projection. A known complete empty attention list is legal; a missing waiter projection is unavailable and cannot yield that list. `NotificationFacts.expiry_ref` binds the admitted expiry interpretation, not an ambient clock. `RichRepresentation.fallback_ref` must resolve to one of the ten non-rich types, preventing recursive rich fallbacks.

### Host resolved records

| Record | Exact fields and types | Binding rule |
|---|---|---|
| `ContributionKey` | `supplier:Supplier`; `local_id:Id` | Exact supplier component/version/artifact/dependency-lock tuple plus author-local ID; no globally ambiguous bare ID |
| `NodeKey` | `contribution_key:ContributionKey`; `template_node_id:Id`; `subject_ref:Maybe<Ref>`; `occurrence_index:UInt` | Artifact-local deterministic node identity; occurrence indexes the entire contribution expansion as defined below, never arrival or paint order |
| `ProjectionBinding` | `contribution_key:ContributionKey`; `input_id:Id`; `snapshot_manifest_ref:Ref`; `content_envelope_ref:Ref`; `authorized_audience_ref:Ref`; `current_read_scope_ref:Ref`; `source_cut_ref:Ref`; `projection_generation:Version`; `freshness:Maybe<Ref>`; `coverage_loss_ref:Ref` | Immutable read result; current disclosure still checked. Source cut includes distinct canonical, receipt and observation relations where needed |
| `CommandHandleBinding` | `contribution_key:ContributionKey`; `binding_id:Id`; `operation:CatalogRef`; `handle_ref:Ref`; `allowed_target_ref:Ref`; `expected_revisions_ref:Ref`; `admission_requirements_ref:Ref`; `availability:Maybe<Bool>`; `loss_ref:Maybe<Ref>` | Non-authorizing reference resolved by trusted host/backend. Availability is a read fact, never a cached grant. The host supplies principal/grant references from its authenticated context |
| `UiCapabilityDisposition` | `contribution_key:ContributionKey`; `capability_state_refs:Set<Ref>`; `client_support` enum `supported|unsupported|unknown|deprecated`; `render_disposition` enum `filled|fallback|omitted|blocked`; `reason_codes:Set<Id>`; `loss_ref:Maybe<Ref>` | References Installed/Enabled/Authorized/Available/Selected/Loaded/Executed facts independently. Does not rename those states or infer executed from rendered |
| `UiSemanticNode` | `node_key:NodeKey`; `point:CatalogRef`; `contribution_key:ContributionKey`; `subject_ref:Maybe<Ref>`; `fact_bindings:Set<Id>`; `action_bindings:Set<Id>`; `role` enum `group|list|status|log|form|button|table|document`; `name_key:Id`; `children:List<UiSemanticNode>`; `disposition` enum `normal|fallback|blocked` | Closed bounded declarative tree. Fact/action IDs resolve only within the exact node contribution key, as defined below; no arbitrary code or hidden query |
| `ClientCapabilityProfile` | `type` constant `ClientCapabilityProfile@candidate-2`; `client:Supplier`; `materializer_ref:Ref`; `schema_ref:Ref`; `semantic_catalog_ref:Ref`; `supported_points:Set<CatalogRef>`; `supported_projection_schemas:Set<Ref>`; `supported_operations:Set<CatalogRef>`; `render_profile_ref:Ref`; `locale_profile_ref:Ref`; `layout_profile_ref:Ref`; `accessibility_profile_ref:Ref`; `resource_profile_ref:Ref`; `security_profile_ref:Ref`; `local_extensions_ref:Maybe<Ref>` | Exact profile and supported semantic coverage, not inferred from OS/client name. A profile with missing mandatory fallback is nonconforming for that workload |
| `UiMaterializationManifest` | `type` constant `UiMaterializationManifest@candidate-2`; `contract_ref:Ref`; `client_profile_ref:Ref`; `capability_graph_ref:Ref`; `effective_config_ref:Ref`; `configuration_application_ref:Ref`; `goal_ref:Ref`; `route_input_manifest_ref:Ref`; `context_ref:Maybe<Ref>`; `projection_bindings:Set<ProjectionBinding>`; `command_bindings:Set<CommandHandleBinding>`; `dispositions:Set<UiCapabilityDisposition>`; `tree_ref:Ref`; `loss_record_ref:Ref`; `input_cut_ref:Ref` | Rebuildable evidence artifact; no new authority store. Changes create a new artifact revision; source facts retain their original owners |

Resolved contribution keys are compared by their full typed tuple; display aliases never substitute. Each `ContributionKey.local_id` resolves exactly one `UiContribution.contribution_id` under that exact Supplier tuple. Host-resolved projection bindings are uniquely keyed by `(contribution_key, input_id)` and command bindings by `(contribution_key, binding_id)`; duplicate keys refuse, even when other fields differ. Each key must resolve its matching author declaration. A node's `fact_bindings` IDs resolve only `ProjectionBinding.input_id` under that node's exact `contribution_key`, limited to the matching declared `ProjectionInput.field_set`; its `action_bindings` IDs resolve only `CommandHandleBinding.binding_id` under the same exact key. There is no search in another contribution or supplier, implicit alias or first-match resolution.

`UiSemanticNode.contribution_key` must equal `node_key.contribution_key`, and `UiSemanticNode.subject_ref` must equal `node_key.subject_ref`, by full typed equality, including Maybe state/value/reason. Mismatch refuses. Node keys are unique throughout one tree. Template-node IDs and accessibility reading-order entries resolve within the contribution's exact pinned template; action references in `Accessibility.keyboard_actions` and `RichRepresentation.mediated_command_bindings`, and input references in `CommandBinding.required_projection_inputs`, resolve in their respective namespaces within the exact same contribution key. `Presentation.semantic_parent`, when known, resolves a non-rich contribution ID under the same exact Supplier tuple; its resolved semantic-parent projection must agree with `RichRepresentation.semantic_parent_ref`. Bare-ID fields cannot identify another supplier.

Repeated rows expand in frozen projection order and frozen template child order. For each exact `(contribution_key, template_node_id, subject_ref)` tuple, `occurrence_index` enumerates all its appearances in deterministic depth-first expansion order, consecutively from zero across the entire contribution, including appearances under different nested parents. It never resets per parent or nested repeat; replay retains the same indices. Reading order expands against those resolved NodeKeys. Same local contribution IDs from distinct suppliers, and same input/action IDs in distinct qualified contributions, are valid independent identities, not collisions.

Output installation/render receipts are separate evidence records referencing the immutable manifest/tree and actual client incarnation/attempt/cut. They are not inside the manifest digest domain, preventing circularity and nondeterministic attempt receipts from changing a same-input artifact. Preexisting snapshot installation evidence, when needed as an input, is frozen inside its source binding.

A `Ref` field referring to current authority is a reference to an existing canonical record, not its transfer or a new grant. Outward client projections may substitute an already-authorized scoped handle under an explicit R-SC mapping, never expose private canonical references indiscriminately. Known unavailable source data yields a loss record, not an invented empty projection.

### Collision and validation rules

1. Reject duplicate contribution IDs within one exact Supplier tuple; duplicate input IDs or action-binding IDs within their respective namespaces of one exact contribution; duplicate template-node IDs within its pinned template; duplicate point definitions; conflicting immutable references; ambiguous providers; dependency cycles; and reserved supplier impersonation before any payload/template loading. Reusing an ID across distinct suppliers, contributions or separate input/action namespaces is not itself a collision
2. Two contributions may fill a multi-slot point only with distinct qualified identities. They cannot override one another by load order. A singleton requires one explicitly selected provider in the resolved graph; ambiguity blocks that point and preserves host diagnostics
3. Aliases are separate pinned presentation maps with exact operation/version/argument transformation. An alias never changes meanings after upgrade or resolves by arbitrary filesystem order
4. Unknown schema dialect, required vocabulary, record field, mandatory semantic version or required point yields typed refusal. Optional client-local metadata can be ignored only under a known non-semantic extension schema
5. Structural validation precedes semantic graph, authorization, privacy, boundedness and mapping validation. No remote schema fetch, plugin import, dynamic registry enumeration, model request or install is part of validation
6. An author request for filesystem/network/credential/model access belongs to the existing plugin declaration and admission flow. The UI contract grants none of it; unknown effect-bearing requests refuse

## Deterministic materialization

**IN, U03.** Treat materialization as a pure bounded transformation of a sealed input bundle, not a discovery/activation engine. UI projection availability and command executability are separate: a historical authorized receipt may remain readable after effect revocation; a current permission does not make unavailable bytes readable.

### Exact input closure

The input bundle freezes all of the following, by exact immutable references and declared mappings:

- Accepted GoalSpec/workflow and required semantic controls; resolved capability graph, supplier artifacts/dependency locks, enabled/selected configuration and current scoped read/effect eligibility observations
- Effective configuration content revision and target application generation separately; requested/staged configuration is not silently effective
- Route assignment, route descriptor revision, exact interface/build/method set/extensions/configuration profile and source evidence applicability; none are inferred from a model name
- Current audience/purpose/privacy/retention interpretation and coherent source cut, including canonical event cut, receipt-journal cut, stream incarnation/cursor/unit and projection version/generation as applicable
- All authorized projection bytes or exact verified snapshots, their completeness/loss, optional missing inputs and deterministic lookup indexes already supplied as data; no render-triggered index build
- Exact materializer, catalog/schema, argument-map, template, localization and fallback revisions, plus a bounded resource profile
- Client kind/build and render profile: terminal capabilities/width policy or GUI semantic adapter, font/Unicode-data interpretation, text scale, viewport dimensions/insets, line wrapping and directionality
- Locale, timezone, calendar/date/number formats and collation version; declared layout preferences, focused subject, scroll anchors, selected tabs and reduced-motion/high-contrast preferences
- A supplied presentation-clock observation if relative time is displayed, and a fixed animation phase or static mode. Ambient wall time, random IDs, OS enumeration order, network arrival order and hidden defaults are forbidden inputs

Semantic source facts are never normalized to make display easier. A transformed display string is a derivative with provenance/loss; raw text bytes retain identity. Exact tree equality means equality of the canonical semantic/presentation tree for this entire frozen profile, not identical screenshots across OS font engines. Cross-client parity compares the normalized semantic facts/operations/target mappings/losses after stripping declared presentation-local geometry, not undeclared effect-bearing defaults.

### Materializer passes

1. **Validate envelope and identity.** Check supported schema interpretation, closed records, duplicate-member rejection, complete refs and source-domain bindings within finite parse limits
2. **Resolve graph without activation.** Consume existing admitted graph/configuration. Confirm Installed/Enabled/Authorized/Available/Selected independently at the required scope. `Loaded` and `Executed` are recorded observations, never prerequisites fabricated by rendering. Compute client support as a separate intersection
3. **Resolve required closure.** Host control/continuity/attention/command obligations and required workflow contributions precede optional decorative content. A disabled plugin contributes zero operational elements/commands; only host-owned authorized inventory/incompatibility explanation may name its absent capability
4. **Bind projections.** Authorize/filter before disclosing or hydrating, bind coherent cuts and exact field coverage, and validate audience-scoped continuation handles. Empty complete list differs from unknown/incomplete. Do not call an upstream to make an unavailable observation appear fresh
5. **Negotiate exact semantics.** Intersect recognized versions and validated fallback relations. Choose the highest mutually supported revision only within a frozen compatibility policy that proves required meaning is preserved. Record the exact selected revision and every loss; incompatible required semantics block the affected action
6. **Build bounded nodes.** Host templates consume data only. Registry point order is the taxonomy order above. Within a point use `(accepted placement group, explicit profile order, supplier component_id, supplier version, artifact identity, contribution_id)` with exact byte/field comparison. No installation/load/locale sort determines authority. Data rows follow their projection's declared order, with stable ID tie-breaks
7. **Check safety shell and accessibility.** Verify reachable named Stop/target, pending interactions, explicit refusal/unknown/gap markers, deterministic focus/reading order, fallback coverage, operation/argument parity and bounded node counts. If an optional template fails, isolate its loss; do not remove host controls
8. **Publish a rebuildable artifact.** Produce UiMaterializationManifest, immutable tree and one loss-record binding. Rendered/installed receipt is separate from merely compiled. Emit no model/index/plugin activation or effect command. Recheck current read rights at disclosure and current effect authority on later invocation

Zero extra work on attach/render/split applies to an already admitted and initialized client/backend profile. Explicitly requested first activation of the client or connection plugin is separately bounded, authorized lifecycle/cold-start work with its own receipts; it must not be smuggled into passive view creation or described as zero code loading.

Client support is not a promise to show a plugin while disabled: eligibility for an active contribution requires enabled, selected, available and authorized read plus supported point/version/fallback. Command handles additionally need all current command/route requirements; the backend repeats those checks. Missing required dependencies block, not trigger installation. A currently loaded view whose grant expires is not permitted to keep executing because Loaded is true.

### Canonical identity and useful diffs

U04 proposes two related artifacts: a shared semantic projection manifest and a client-profile-specific UI materialization. Both reuse ArtifactRef. Their identity includes the complete containing interpretation, source closure and ordered content, not the raw text of a user-facing label alone. The canonical command key remains **`(admitted_authority_domain, command_id)`**. `content_digest` is its immutable equality/conflict predicate, not a third key component. Principal/grant, action/arguments, target/scope and effect-relevant revisions are inside immutable command meaning. R-L's `semantic_digest` is related only through the explicit R-SC map. [R-SC]

A JCS-based candidate canonicalizer is suitable for a JSON illustration; a different deterministic encoding with an explicit bijection is a genuine competitor. This report does not select production encoding or hashing. The frozen M1B use of JCS/SHA-256 remains unchanged. Content digests carry their declared privacy domain; they are not public cross-project dedup keys or proofs of authenticity.

A review diff reports added/removed/changed contributions; exact old/new supplier/template/profile refs; filled/fallback/omitted/blocked points; route and authority observation changes; required and optional losses; changed localized text/layout separately; and source cut differences. “Why this control?” follows node → contribution → point/operation → capability graph → current authorized projection and independent support evidence. “Why absent?” returns a host-safe reason or redacted explanation, never private existence metadata.

A route descriptor change invalidates affected command availability even when route assignment does not change. A configuration preference may wait for its accepted application boundary; restrictive authority changes fence immediately at the authoritative gate. Cache reuse requires identical applicable input closure and current rights. A hash cache hit is not authorization.

## Fail closed without concealing controls

**IN, U05.** Typed candidate application dispositions below do not extend any frozen M1B error alphabet. Each loss is a facet of the existing single immutable coverage/loss record; UiCapabilityDisposition references it rather than maintaining a second writable truth.

| Condition | Required disposition and visible effect | Protected action |
|---|---|---|
| Unknown point or major semantic revision | `unknown-point` or `unsupported-schema`; omit untrusted nodes; safe host placeholder if disclosure allowed | Refuse unless a separately recognized full-semantic fallback is validated |
| Unknown required capability/route evidence | `capability-unknown`; explicit unknown reason and required profile | Refuse the affected caller/profile/workflow on every ingress path; no speculative button |
| Known unsupported optional rich view | `presentation-unsupported`; semantic-linear fallback with explicit layout/detail loss | Permit only operations whose full meaning survives and whose current guards pass |
| Required point unsupported with no complete fallback | `required-semantics-unavailable`; host shows unmet requirement and setup/alternate-client explanation | Block affected workflow action, retain independent Stop/status/inspection path |
| Deprecated recognized point | `deprecated-supported` plus precise removal/compatibility policy | Current revision permitted only under declared compatibility; no silent migration |
| Missing/expired grant or source data | `authorization-denied`, `stale-read-scope` or `projection-unavailable`; avoid existence leaks | No new protected read/disclosure/effect; historical facts only under current separate read rights |
| Disabled or unselected plugin | `plugin-disabled` or `not-selected` in authorized host explain view; zero plugin contribution nodes/handles | No plugin dispatch/import/dynamic enumeration; rendering cannot enable it |
| Collision, ambiguous provider or contradictory alias | `contribution-conflict`; all affected candidates retained as diagnostic references where allowed | No load-order winner; require existing configuration resolution |
| Resource bound exhausted | `presentation-budget-exhausted`; bounded continuation/summary of omission, not invented data | Shed optional presentation first; preserve reserved control and canonical append |
| Invalid fallback or unsupported mandatory security semantics | `fallback-invalid` or `security-semantics-unknown` | Refuse affected use; never downgrade to an unqualified bridge |

**Downgrade resistance.** A presentation omission alone need not disable an independently supported CLI operation: for example, lack of a graph layout need not block a fully represented text command. Distinguish that lawful fallback from missing required safety semantics. Every operation descriptor names required semantic capabilities and trusted review disclosures. All adapters submit the same immutable meaning to the same admission gate, which checks those requirements irrespective of whether a UI control is visible. For the affected caller/profile/workflow, an unknown approval/action schema cannot be bypassed by invoking its command ID from CLI, a deep link or an embedded panel. Another independently conforming client with current authority and complete required semantics is not globally disabled because this client lacks a rich view. A plugin cannot declare an optional view and hide a mandatory effect requirement inside it. The independent parity oracle must test each alternate entry path.

A malicious client can lie about what it displayed. The backend cannot infer informed human review from a client-rendered checkbox. Consequential approval remains the existing trusted interaction/admission contract with exact action/scope and separately evidenced principal. Renderer negotiation and UI receipts are evidence about a client claim, not a new security authority.

**Fallback floor.** Every required fact and supported control needs a labelled linear representation, logical reading order, non-color-only state, keyboard or equivalent assistive activation, visible non-obscured focus, stable target identity, and a way to inspect exact arguments and losses. Motion is optional; static mode retains the same facts. Preserve text resizing/reflow and avoid focus theft by streams. Long tables/graphs need lists or adjacency views; artifact images need authorized text alternatives or an honest unavailable-semantic representation. A missing equivalent blocks the claimed profile; a CLI existing somewhere else does not automatically make an inaccessible GUI compliant. Actual UI Automation, Apple or AT-SPI behavior, screen-reader announcements, contrast and usability require separate rendered tests. [P12] [P13] [P14] [P15] [P16] [P17] [P18] [P19]

Stop must remain available through a persistent non-mouse-only host path; never a timing-sensitive double Escape, overloaded destructive Escape, hover-only menu or plugin-controlled hotkey. Keyboard completeness is the same command meaning, not necessarily identical keys on all clients. Mobile exposes accessible labelled actions and alternate input/assistive paths without requiring a hardware keyboard; it cannot claim desktop keyboard conformance from that alone.

## Plugin contributed UI security and lifecycle

**IN, U06.** The candidate boundary is a security obligation, not a selected sandbox. Prefer pure declarative nodes with no executable plugin UI in the baseline comparison. Compare a separately confined rich-view realization only if it demonstrates the same projection/command boundary. Trusted host controls are outside untrusted content surfaces.

### Required boundary

- The host sends only explicitly authorized projection fields for the named audience/purpose/cut. A renderer cannot enumerate canonical storage, other projects, raw query services, credential sources, process environments or provider auth stores
- Command references expose exact registered operations and argument schemas. The host checks origin/sender/target/instance, reconstructs immutable typed intent and invokes existing admission. No generic execute/eval/HTTP/native-object bridge is available
- A rich view cannot intercept or forge host approval/Stop chrome, draw over it, seize modal focus indefinitely, install global hotkeys, or change the selected target during dispatch. Content provenance is visibly separate from canonical status
- Arbitrary in-process native widget code inherits its host powers unless a separately evidenced restriction exists. It cannot be labelled untrusted-isolated merely because it has a widget interface. Separate process, iframe, capability token or CSP also does not by itself prove the whole boundary
- Confinement must cover direct and induced access, shared storage, origin/bridge channels, outbound assets/fonts/images, drag/drop, clipboard, file pickers, navigation, notification payloads, timing/size metadata and inherited handles. Missing required containment refuses rich rendering; use the inert fallback
- Provider credentials remain outside the UI. Device/session authentication is separately scoped backend access managed by R-MOB; it is not provider credential custody and is not placed in plugin manifests, logs or UI projections

MCP Apps and WebView precedents are candidates for an adapter, not chosen transports or isolation mechanisms. Their richer message APIs cannot be forwarded wholesale. In particular, plugin requests to call tools, update model context or send messages must map to independently admitted Recursion operations; render itself never triggers them. [P09] [P10] [P11]

### Untrusted content and narrow allowlists

`authority_carried_none=true` applies to manifest descriptions, imported labels, rendered model/tool output, rich-view documents and notifications. Apparent role delimiters, approval text, QR codes, action links and “system” badges are data. Displaying them does not create a grant, tool/agent request or current receipt.

| Surface | Candidate allowed path | Refuse or contain |
|---|---|---|
| Structured text | Bounded decode; explicit safe text/format nodes; host-generated style controls | Raw ESC/C0/C1 control bytes passed to containing terminal; malformed/incomplete sequences silently reinterpreted as commands |
| Raw terminal compatibility view | Separate qualified terminal parser/emulator with declared sequence profile and bounded state | Treating raw PTY output as application control, approvals, host input or resize authority |
| OSC/DCS/APC/device responses | Default reject in contribution text; a separately qualified named subset may be parsed and re-encoded by host | OSC 52 clipboard, title spoofing, arbitrary terminal reports, executable hyperlinks, unknown controls; responses feeding application input |
| Clipboard | Explicit user copy/paste through an admitted host interaction; paste remains unsent data | Automatic read/write, cross-project copying, output-controlled clipboard or paste-triggered submit |
| External links | Host preview of exact scheme/destination/recipient-data exposure; separate authorized open action | `javascript:`, executable/data/file/custom schemes by default, automatic redirects/launches, URL-carried secrets |
| Deep links | Parse an allowlisted versioned navigation intent into inert target selection; validate current read scope | Any link directly accepting approval, sending Stop, running a command or restoring an old grant |
| Notifications | Admitted notification adapter with minimal authorized fields/rate/expiry; tap opens current authenticated inspection | Content-bearing push from untrusted manifest, approval by tap, permission inferred from channel membership |

An allowlist is only as good as its actual parser/profile. Split sequences, overlong input, invalid UTF-8, bidi spoofing, confusable labels, nested frames and hostile links all belong in adversarial fixtures. Sanitation cannot remove all semantic influence; the deterministic effect gate remains necessary.

### Disabled and revoked are different

For a contribution disabled or unselected in the evaluated task/client scope, operational node count and command-handle count in that scope are exactly zero. Full global disabled-trace zeros apply only to a genuinely disabled realization with no separately admitted use. A shared supplier may already be loaded/executing for another authorized task: this UI scope must cause zero incremental import/activation/effect activity, while the supplier's existing resources remain separately attributed, never falsely reported globally zero. Implementation imports, payload scans, processes, threads, timers, watchers, network, credential reads, quota reservations, spending, cache writes, context injection, tool registrations, callbacks and event subscriptions must be zero under the frozen disabled trace. A bounded inert manifest inventory read is counted separately and is not zero CPU/disk cost. A host explanation is not a ghost plugin panel. This preserves M1B's exact DisabledActivityTrace and extends the observer with explicit UI nodes/model/index counters. [R-M1B]

On restrictive revocation, the canonical gate blocks new affected reads/disclosures/effects at its ordered boundary and invalidates matching scoped handles/registrations. Connected clients discard affected active projections, focus transfers to a host-owned explanation, queued rendering is cancelled, subscriptions are closed and cleanup is reported within the declared client-observation deadline. In-flight external effects and already delivered bytes retain their original unresolved/settled records; revocation is not rollback.

No fixture may demand that an offline client receive a revocation it cannot observe. Record separately: canonical revocation committed; backend admission fenced; notification emitted/delivered/observed; local view invalidated; controlled cache disposition; disconnected residual; and independently verified erasure, if any. On reconnect, revalidate audience/retention before hydration and never replay offline actions. If privacy policy requires no stale redisplay after unseen revocation, the conforming candidate is **no offline protected redisplay**, with explicit online-only access gates. Even that cannot claw back screenshots or plaintext already seen. A bounded offline lease can bound cooperative-client behavior under its clock assumptions, not prove instant erasure.

Private cached-content retention is **unresolved**, including whether minimal status metadata may remain visible. Such metadata can itself be private. Do not default missing policy to permission. This report recommends no private offline hydration until an explicit policy exists; this is a conservative candidate, not an adopted product decision. R-MOB owns pairing, device sessions, connectivity and cache-policy realization. UI supplies stale/last-synchronized/residual labels and cannot overrule that policy.

## Ten controls and three Stops parity

### Exact inspected evidence profiles

These identifiers are report-local evidence labels, not new registered product routes. Every profile remains **Unqualified** for the R-UI product contract. The matrix does not infer support from a rendered button.

| Profile | Exact inspected identity and configuration | What the evidence can establish |
|---|---|---|
| `UI-NATIVE-CANDIDATE` | Current Recursion pin; R-L `r-l-candidate/0` catalog and interface schema; effective runtime/client configuration **unknown** because no implementation ran | Required candidate meanings, not available product controls [R-RLC] |
| `BROKER-M1B-1` | Current pin; frozen `m1b-broker/1`; exact supplied BrokerTraceInput is its configuration; UTF-8/I-JSON limits and input/resize lease fields unchanged | Static schema/fixture meanings; no ten-control qualification, production transport or renderer proof [R-M1B] |
| `CODEX-0149-LOOPBACK` | Historical recorded run `run.codex-interaction-232842419229`; Codex App Server 0.149.0; Windows 11 build 26200; executable SHA-256 `14b7e6b2356e82d1d9275579eaa588757b4e0a501b65dcc19fccdf77bd83dc00`; config SHA-256 `5fa55dacbc8e67112de5eb7ffccef7dc7eece6ceb8134c8d3188d9d298256ddc`; result SHA-256 `2852e510887820bbdf547c0ff123a5c4be96b70f43d1885c508256e97bb8cb32`; corresponding release source `758ef40f50c1a458425c7cfbf1eb12cbc07af0b0` | Inspected recorded scripted-loopback checks only; experimental environment/question fields, same connection, no live model/account, no post-resume inference; source/binary equivalence was not reproducibly rebuilt [R-IPR] [R-ROUTES] |
| `CODEX-SOURCE-D25` | R-F retained public App Server README source `d25c114d494ddb693290b76bf5e5f64ecbdb38fc`; retrieval 2026-10-02; README capture SHA-256 `5d1b3014441120061a8e41e233b5d9c0d0d6f8bf9e2aaf9765b1bf581ebdcb79`; executable/config/host and matching enabled experimental methods **unknown** | Recorded source declarations only; cannot be projected onto 0.149.0 or a present installation. Fresh raw retrieval here failed, so no fresh-content claim [R-RF] [R-RFS] |
| `MOBILE-CONNECTED-CANDIDATE` | R-UI candidate-2 plus R-MOB connected-only control requirement; exact mobile OS/build, backend build/config, pairing and protocol binding **unknown** | Proposed semantic projection and live-connection gate, no working mobile implementation or deployment |

Source `CODEX-SOURCE-D25` is deliberately secondary to the retained repository capture for this report; its exact upstream pin is named without pretending it was executed or freshly fetched. Other harnesses retain R-F's own per-interface unknowns. This lane does not repeat or upgrade their route inventory.

### Control map

Every row binds to the same `UI-NATIVE-CANDIDATE` operation catalog, independently of CLI/TUI/GUI/mobile presentation. Local names below describe meanings; only the explicitly existing `core.message.enqueue@candidate-0` spelling is asserted. Unnamed operations require a future reviewed catalog entry, not an invented runnable API.

| Required control | Contribution and exact semantic facts/target | Inspected route evidence and precise loss | Required client behavior |
|---|---|---|---|
| Streaming output | conversation + continuity; task/attempt/turn, source identity, cursor/unit/incarnation, coverage | BROKER-M1B-1 defines bounded EVENT/CREDIT/ACK/RESET; CODEX-0149-LOOPBACK records correlated output/usage in scripted turns. Complete durable source replay/production streaming U | All clients expose authorized content and GAP. CLI paginates/streams, TUI bounds history, GUI/mobile virtualize; no hidden reasoning or fabricated missing tokens |
| Questions | attention; exact interaction ID/generation/revision, waiter/turn, answer schema, expiry | CODEX-0149-LOOPBACK records interrupted blocking question, late-old-answer nonrelease and current-answer completion. Fresh connection/replaced-process outstanding waiter support U | Host form shows exact question/target; stale answer refuses without retargeting; closing panel is not answer/cancel |
| Approvals | attention + command; exact action digest/arguments/data/recipient/scope and principal | CODEX-SOURCE-D25 has source-described correlated approvals; CODEX-0149-LOOPBACK explicitly leaves fresh-connection outstanding approval for next test. Current permission/route/approval behavior U | No locally optimistic approval, plugin approval chrome or automatic notification-tap response; all paths use trusted current interaction |
| Queued messages | conversation; enqueue/edit/remove at expected queue revision before delivery | R-L defines `core.message.enqueue@candidate-0`; neither inspected loopback check list nor frozen broker proves a crash-durable application queue/edit/remove. U | Show saved-local/accepted/delivered separately. Mobile cannot create an automatic offline queue; backend queue control requires connected admission |
| Active steering | conversation + command; current attempt/turn and delivery policy | CODEX-0149-LOOPBACK records stale-steer refusal and same-turn scripted input; CODEX-SOURCE-D25 records expectedTurnId requirement. Current build/general route conformance U | Serialize captured target, reject stale turn; never convert steer to queue behind the user's back |
| Interruption | control + continuity; selected mode, exact scope and admission fence | CODEX-0149-LOOPBACK records blocking-question interrupt; full D-022 composition and receiver settlement U. BROKER-M1B-1 INPUT is not Owner Stop | Persistent host action; report fence, interrupt delivery, exit and unresolved effects independently |
| Resume | control + environment; task/checkpoint, current route/config/grants and unresolved effects | CODEX-0149-LOOPBACK records idle-server history resume without post-resume inference. In-flight recovery and current effect authority U | Attach/read recovery is distinct from explicitly admitted execution continuation |
| Forks | work + artifact + command; source/context/candidate revisions, lineage and conserving reservation split | CODEX-0149-LOOPBACK records in-flight fork result/history boundary. Complete dirty workspace capture, effect/permit handling and allocation split U | Preview exact capture/loss; do not copy active authority or spending capacity; preserve both versions |
| Compaction controls | artifact/context inspection + settings + command; context_epoch, governor, exact inputs/loss/rehydration refs | CODEX-SOURCE-D25 contains compaction-related source declarations; inspected loopback run does not test compaction. Exact supported controls/config/governor U | Inspection is model-free; request/tune only supported separately admitted transformation. Generated summary is not installed context |
| Commands/plugins | command + settings + environment; operation namespace/version/schema, supplying component, seven state facts | R-A/R-L/frozen plugin records specify graph and grants; no R-UI materializer/activation implementation observed. Upstream slash/UI command parity U | Typed discover/inspect/invoke, transparent loss; disabled package does not register operational commands or activate on view |

The row's fallback does not make an unknown route supported. A fixture may use synthetic supported and unsupported descriptors to test presentation behavior; that is a simulated contract check, not route qualification. Required controls stay visible as supported, unavailable, unknown or currently blocked with precise reasons. Where metadata itself is restricted, the explanation is safely redacted rather than disclosing a private target.

### Stop vocabulary and viewer leases

| Mode or mechanism | Exact accepted meaning and persistent display | Evidence gap and required result |
|---|---|---|
| **Aggressive** | Selected agent; fence further selected-agent dispatch; force interruption without waiting; show descendants separately | CODEX loopback interrupt is only one mechanism. Local/remote in-flight effects may remain unresolved; no implied whole-tree Stop |
| **Full** | Selected agent plus its owned subagents, shells, monitors and relaunchers; close restart/return paths | Frozen process termination record has effect_conclusion=`not-evaluated`; IPR-001 birth-containment history is bounded. Whole ownership set and remote effects require separate evidence |
| **Lazy** | Close admission, stop at named observable operation boundary with deadline and configured escalation | No inspected route profile qualifies required boundary/escalation. Missing boundary blocks the required profile; waiting/timeout is explicit |
| `checkpoint` | Preserve the accepted recovery/control/evidence boundary under its catalog semantics | Transcript copy alone does not establish a complete durable checkpoint |
| `interrupt` | Send the supported native interruption mechanism to the exact subject | Request, receipt, terminal result and effect outcome remain distinct |
| `drain` | Close new admission; finish only declared bounded admitted work/reconciliation | Not unbounded retries, implicit new child work or a fourth Stop mode |
| Close/detach/reconnect | Unsubscribe/presentation lifetime only | Must not Stop, relaunch actors, resume effects or close runtime-owned adapter sessions |

The common control path does not require the terminal input/resize lease when the principal independently has Stop authority. Conversely, an input lease is not effect authorization. One active holder has the input and resize ownership relation, but the opaque input and resize references remain separate typed domains. Passive viewers may reflow their local viewport; they cannot send upstream INPUT/RESIZE. Lease validity binds target, daemon/process incarnation and generation. Focus, tabs and geometry mint nothing. M1B retains `passive-client-input`, `stale-lease`, `stale-daemon-epoch` and `stale-process-epoch`. [R-M1B] [R-TR]

The host serializes Stop mode and scope before dispatch. Every client displays affected ownership set, admission-fence status, named Lazy boundary/deadline, per-host receipts and unresolved effects. Full Stop on one task cannot kill unrelated sessions merely because they share a process. A source interrupt, connection close or killed PID is never external rollback.

### Continuity is a vector of facts

Reuse R-SC's eight independent receipt dimensions: **saved_locally, received, delivered, admitted, started, observed, settled, verified**, each with its exact subject/observer/cut/evidence. Do not relabel R-L or X source fields without their explicit mapping. Admission acceptance and durable commitment can themselves have different evidence. Configuration compiled/validated/staged/effective, message delivered/adopted and artifact generated/tested/reviewed/accepted/published remain separate domain facts. [R-SC]

A replay gap uses a visible `GAP` marker and exact coverage reason. It does not introduce a GAP wire arm. Frozen M1B retains HELLO/WELCOME/SNAPSHOT/EVENT/ACK/CREDIT/INPUT/RESIZE/RESET, no additions. Its replay-gap continuation rule requires RESET next; credit resets and fresh CREDIT precedes further EVENT. ACK cannot advance beyond installed/verified state under the additive application binding, and cursor unit/incarnation never changes by guess. Snapshot wire acceptance is not snapshot installation. [R-M1B] [R-RL]

Canonical append and control capacity are independent of disposable rendering. Coalescing happens only after mandatory facts are retained. Slow clients lose presentation continuity explicitly or disconnect/reconstruct; they never backpressure Stop or canonical state indefinitely. This obligation needs bounded framing, decoding, scheduling, queues, write headroom and observation capacity end to end; two queues by themselves are not proof.

### Cross client parity criterion

At the same exact semantic catalog, authorized audience, route/config/authority read cut and complete projection inputs, all applicable clients must preserve:

- Identical source facts, unknowns, losses and current/stale distinctions
- Identical operation/version, arguments, target/scope, revisions, grant meaning and refusal/effect-attempted semantics
- The same stable command key for retry of the same command, with changed body/actor/scope rejected as conflicting duplicate
- Explicit scope-local support differences and safe fallback; no undeclared defaults or hidden activation

Allowed differences include visual layout, pagination, keyboard chord, input modality, screen-reader bridge, viewport, animation, notification affordance and local selection. All are declared in ClientCapabilityProfile and must not alter canonical meaning. A mobile device's connection state adds a declared submission gate, not a different definition of Stop or approval. A different cut is not a parity failure; pretending two cuts are equal is.

A GUI submitting current-focus task B after the user selected task A, mobile presenting a saved draft as admitted, TUI converting steering to queue, CLI bypassing required action disclosure, or any client accepting an unknown mandatory operation version falsifies parity. Identical screenshots cannot repair any of those failures.

## Provider free acceptance fixtures

**IN, U07–U09. All target fixtures are UNEXECUTED.** This is a later bounded local handoff, not permission to execute repository scripts, target tests, upstream harnesses, plugins, model/provider/account flows, or a UI toolkit now. No implementation/runner is supplied or claimed runnable. A separately admitted task must pin new candidate and independent oracle artifacts in an authorized disposable local workspace. Static report/schema checks cannot mark these runtime cases PASS.

### Admission and observer requirements

Freeze exact source/candidate/oracle/profile identities, allowed output paths, synthetic data, process/memory/disk/CPU/time limits, no external network/provider/credential sinks, monotonic clock, event schedule and stopping conditions. Every fixture needs a valid authorized positive, the adverse mutation and a planted broken-implementation control. The oracle derives expected graph, tree, arguments, receipts, source events and sink effects independently; it cannot call the candidate reducer to obtain its expected answer.

Tripwires record **attempts**, including denied attempts, for import, process/thread/timer/watcher creation, network, credential read, model invocation, indexing, dynamic tool enumeration, context injection, direct storage mutation, clipboard, terminal and external launch. A synthetic positive detector-control invokes only the denying stand-in, never an actual provider/network/credential operation. Missing instrumentation or failure to detect a planted violation invalidates the evidence; a quiet UI does not prove zero hidden work.

| Fixture | Frozen input and valid positive | Adverse mutation and exact pass/fail predicate |
|---|---|---|
| UI-01 deterministic tree | Same full bundle, independently expected tree and manifest repeated 100 times; permute unordered manifest/set input in all 24 permutations of a four-contribution subset | All 124 outputs have byte-identical canonical tree/manifest under the chosen experimental canonicalizer. Change one material input and get the independently expected changed artifact. Ambient clock/random/load order dependence fails |
| UI-02 locale and profile precision | Equal profile/locale/layout yields equal tree; alternate locale, RTL, viewport and text scale have their separately expected trees | Different-client pixel/tree identity is never required. Their semantic normalization must match required facts/actions. Same ref with different profile content refuses. Lexical IDs `z-first`,`a-second` retain explicit reading order z then a |
| UI-03 unknown and versions | Known point/revision with supported operation renders; known rich point degrades via verified semantic-linear fallback | Unknown point/major/required vocabulary/field/capability yields exact typed omission/blocker and zero affected action dispatch. No approximate synonym/default version. Known independent host Stop remains reachable |
| UI-04 downgrade bypass | Supported CLI and rich client use identical operation requirements; a separately conforming client may continue | Missing mandatory action semantics on affected client/profile: invoke via button, CLI alias, deep link and embedded message. Every affected ingress refuses. Optional graph loss alone must not globally disable conforming text control. Author `required_for` cannot deny unrelated workflows |
| UI-05 collisions | Two suppliers reuse the same local contribution ID and input/action IDs yet resolve only their own bindings in canonical multi-slot order. A template node/subject repeated under two nested parents gets distinct consecutive occurrence indices across the whole contribution | Reserved namespace spoof; duplicate contribution ID within one exact Supplier; duplicate input/action ID within its own namespace and contribution; duplicate resolved binding key; cross-contribution bare-ID lookup; mismatched node/key contribution or subject; reset/duplicate occurrence index; singleton conflict; incompatible exact schema; and same immutable identity/different bytes all refuse before load/install as applicable. No last-installed winner |
| UI-06 disabled inertness | Installed-disabled realization: at most one admitted metadata inventory read; host diagnostic allowed | Plugin operational nodes/handles=0 and every disabled trace activity=0. Poison manifest links/body references must not be hydrated. Shared supplier active elsewhere is a separate scope; unselected view has zero incremental activation/effect and truthful attributed preexisting cost |
| UI-07 revocation online | Admitted view receives revocation after canonical fence | After backend fence, zero new denied admissions/disclosures. After client observes revoke, before next installed tree, no affected active node/handle remains; cleanup within frozen deadline; host explanation remains. Stale held handle refuses even if UI hiding is broken |
| UI-08 revocation offline | Disconnect after authorized snapshot; revoke backend; later reconnect | Backend denies new affected actions immediately at its boundary; disconnected state marked last-synchronized/currentness unknown under selected policy. No claim of instant offline disappearance. On reconnect no private hydration before current authorization, no automatic action replay. Private redisplay cell blocked-definition until policy exists |
| UI-09 direct access and spoof | Authorized projection field plus mediated command works | Attempt raw canonical write/query, another audience handle, credential/native bridge, system-status impersonation or approval creation. Independent sinks observe zero forbidden disclosures/mutations; merely hiding the evidence fails |
| UI-10 terminal and URI injection | Plain Unicode and allowed host copy/navigation work | Every split point of ESC/OSC52/DCS/control-string corpus, malformed/overlong frame, bidi spoof, command-looking content and executable/custom deep link is tested. Zero forbidden terminal/clipboard/native/effect operations and parser recovery to next valid item; failing detector mutant invalidates suite |
| UI-11 controls parity | All ten controls across CLI/TUI/GUI-stub/mobile-stub at the same input cut and semantic profile | Compare operation/version, arguments/target/revisions, refusals, attempted-effect facts and loss. One mismatch or invented support fails. Repeat mobile disconnected: no submission; preserve uncertain already-submitted receipt identity |
| UI-12 Stops parity | Separate Aggressive/Full/Lazy traces, two owned children, relauncher and one unrelated task | Exact mode/scope, admission fence, boundary/deadline/escalation, unresolved remote effect retained. Full cannot affect unrelated task; Lazy cannot admit new work. Detached all views must leave actors alive. Fast local exit cannot mark effects settled |
| UI-13 viewer leases | One current input/resize owner, passive readers and separately authorized Stop caller | Passive/wrong-type/stale lease, daemon/process reuse and focus-steal all refuse; valid holder succeeds; passive local reflow remains allowed. Stop works without input lease when independently authorized |
| UI-14 replay and install | Valid complete snapshot installed with exact cursor, then bounded suffix | Gap requires frozen RESET continuation and fresh CREDIT; forged floor, ACK ahead, wrong unit and uninstalled snapshot cursor fail. GAP remains visible. No invented historical narrative or extra GAP wire message |
| UI-15 command identity | Same canonical domain/ID/content retry from currently authorized reader returns historical receipt with zero new effect | Changed embedded actor/grant/target/body conflicts; new transport ID changes nothing; expired dedup history holds for reconciliation; lost ACK cannot create new operation/reservation. Old readable acceptance cannot reauthorize effect |
| UI-16 accessibility fallback | All required controls/facts have names, ordered roles, complete linear path, keyboard/assistive activation and static mode | Strip labels, color-only status, focus trap/obscured control, missing action, reordering, animation-only information and mouse-only Stop must each fail semantic screening. Real AT/rendered conformance stays a separate U gate |
| UI-17 zero work on views | Attach/focus/split/resize-local/restore/detach/reconnect against unchanged admitted runtime | Additional actor/worker/model/index/plugin activation/effects=0 at independent sinks; bounded client rendering/metadata work reported. Unknown coverage is not zero. Last client close cannot relaunch/terminate runtime-owned adapter |
| UI-18 contribution and view soak | Full count matrix and regimes below; successful valid control positives in each applicable cell | All hard zeros, mandatory event retention, cursor/fence/input/queue/memory/append/control predicates below hold. Missing required observation gives HOLD_UNKNOWN, not PASS |
| UI-19 bounded parser/materializer | Max accepted size/depth and known finite template complete within work bounds | One-over-limit, recursion/cycle, expansion bomb, broken ref, fetch-looking URI and malicious localization fail boundedly with no external activity; host control path stays live |
| UI-20 shared provenance | Valid unchanged ArtifactRef/ContentEnvelope/loss binding round-trips | Remove `project_and_audience` or `privacy_domain_id`, contradict loss alias, treat unknown as zero or use content as authority: refuse. No new base field, generic epoch or second loss store |

A blanket-refusing candidate fails every applicable positive. An unavailable implemented feature is not a successful negative test; label the cell unsupported or blocked-definition. Independent review must bind exact candidate/oracle outputs, including failed and censored cases.

### Exact contribution and view soak

Two counts must remain distinct:

- **C** = active optional UI contributions per client, `0/1/5/10/20`; the host-required control/continuity/attention/command shell is fixed and excluded from C
- **V** = attached presentation views, `0/1/5/10/20`; V=0 leaves an independent synthetic control/observation harness and zero presentation clients. Frame/input-echo metrics are not applicable, not zero

Run the **25-cell C×V factorial** under both idle and high-output regimes, using the same declared single reference render profile first. This is 50 screening cells. C may be selected in the graph at V=0 but causes no renderer process/activity; its no-view behavior remains measured. CLI/TUI/GUI/mobile semantic binding tests in UI-11 are separate. A claimed additional client/profile performance result must rerun the same matrix for that profile; copying the reference timing is forbidden.

**Proposed finite screening profile, not production SLA:** three independent process-lifetime repetitions per cell; 2 seconds declared warm-up, 10 seconds offered workload, 5 seconds drain; one view is active among V>0 and all others passive; zero-view control is measured without display. At high output offer exactly 100 numbered canonical events/second, each with 1,024 synthetic payload bytes, for 1,000 events per run. Fixed event types include stream, command receipt, lease, process-exit and effect-state facts with independent expected sequence. Idle has no actor work or source changes after warm-up. Repeat references use identical deterministic synthetic payloads, never real data.

The screening campaign has 150 base runs. Add 12 fixed pressure/recovery runs at C=20,V=20: four each for stalled reader, disconnected reader and resize/reconnect; each lasts the same 17 seconds. Reserve at most 90 minutes total, 30 seconds per run including setup/teardown, 2 GiB simultaneous process-tree RSS, 1 GiB retained evidence and 256 MiB trace output per run; lower platform/task limits win. Exceeding a hard safety ceiling stops the affected run/campaign and retains failure, never silently truncates required evidence. These constants require approval in the future local admission; they are a concrete candidate, not instructions to execute now.

Each contribution has at most 128 semantic nodes/depth 8, 64 KiB input and output per materialization, one permitted bounded subscription and a 256 KiB/256-event delivery queue. Per-view projection queue caps are 1 MiB/1,024 events. Queue values count decoded payload bytes and separately report framing. Global process/trace caps override summed local ceilings. Optional presentation must shed/disconnect before any queue becomes unbounded. Historical canonical evidence is retained by the separately bounded synthetic backend, not copied into every contribution queue.

Fault schedules: stall one passive reader during seconds 3–5, then recover; disconnect one at second 3 and reconnect at second 6 with its true cursor; send 20 local geometry changes/second during seconds 3–5 and one valid final active resize; impose a bounded incomplete bulk frame at second 4. An independently authorized Stop is offered at second 4.5 in pressure runs. Use separate Aggressive, Full and Lazy copies where those semantics differ. A physical framing schedule is not simulated by merely sleeping the renderer thread; the future implementation must demonstrate the declared ingress/framing/scheduler reserve.

**Exact per-run predicates:**

1. Expected mandatory canonical event identities/digests equal retained identities exactly once; zero loss, duplicate effect, wrong input target or invented settlement
2. Passive attach/render/split cause zero extra actor/worker launches, model calls, indexing, disabled activation, provider-credential access, unauthorized or plugin-originated network actions, or work effects; independent detector coverage complete. Explicit user commands in control-positive cases are separately admitted and counted, not forbidden by this passive-work zero. Authorized thin-client projection/control transport, connection lifecycle, rendering CPU and client processes are measured under finite budgets, not asserted zero. This provider-free local screening uses synthetic IPC/denying network stand-ins, with no external network sink
3. All per-contribution/per-view/global queues, nodes, bytes, work units and RSS remain within the frozen ceilings; backlog drains by five seconds after offered load ends or yields a declared bounded disconnect/GAP with canonical retention intact. A slow disconnected reader is never counted as a fast displayed frame
4. Every installed/acknowledged cursor is monotonic within the exact stream/incarnation/unit and never advances past installed facts. Recovery follows frozen M1B where applicable; no reconnect relaunch
5. Valid commands and Stop admission/fencing succeed within the **predeclared experimental** bounds at each C,V. For an initial screening proposal use append p99 ≤50 ms; Stop offer→admission and admission→local fence each p99 ≤100 ms; maximum single renderer work slice ≤8 ms. Tail sample count must support the claimed statistic. With fewer than 1,000 observations per metric/cell, report descriptive max/raw samples and mark p99 qualification HOLD_UNKNOWN rather than invent adequacy
6. Added-view p99 append regression against paired V=0 at the same C is ≤5 ms under the proposed screening bound, with failures/refusals/censoring included. These borrowed R-K candidate values are not ratified thresholds. A reviewer may choose different bounds only before outcomes and with a new profile identity
7. At idle, retained memory has no continuing positive growth after the declared warm-up beyond the frozen allocation envelope; report first/last/peak and slope, not a universal zero-memory claim. Any cap breach fails even if mean RSS is small. Hidden/absent contributions produce no polling/inference just to maintain a status badge
8. Dispose all owned synthetic client resources by the teardown deadline; unresolved cleanup fails completion. Do not kill unrelated processes or conceal teardown failures

The 12 stress runs are fault screening, not statistical tail qualification. They give only a bounded observation of a specific schedule. A separate calibrated confirmatory profile must freeze independent replication, precision/margins, actual baseline B0, clock/collector overhead, OS/terminal/render/AT profiles and full load envelope. Missing approved ceilings, unsupported clocks, incomplete instrumentation or absent target implementation blocks performance conclusions. No result exists yet.

Record offered/admitted/refused/dropped-presentation/retained-mandatory counts, generator lateness, CPU, per-process and aggregate RSS, I/O, wakeups where observable, process/handle counts, queue high water, canonical append, control/fence, frame/input latency, recovery time and exact source/cursor cuts. Use monotonic local durations; do not subtract unsynchronized remote clocks. Preserve raw rows and failed/timeout/censored observations. Run order is frozen before results, balanced across independent blocks with recorded deterministic permutation; millions of correlated token events do not become independent runs.

OR-024 floors precede rankings. Report the full vector with `INVALID_EVIDENCE`, `REJECT_FLOOR`, `HOLD_UNKNOWN`, `NO_BENEFIT`, `REGRESSION`, `NON_DOMINATED_TRADEOFF` or `CONDITIONAL_ADVANTAGE` as applicable. A provider-free UI result cannot establish subscription efficiency, model quality, task productivity, real OS containment, physical durability or actual route support.

### Local deliverables and stopping boundary

A future admitted implementation returns a manifest with exact profile/candidate/oracle/build refs, inert fixture inputs, expected trees/commands, observed traces, independent sink/oracle outcomes, raw timing/resource samples, source/cursor/lease facts, coverage/loss and missing observations, full-vector summary and independently reviewed checksums. Stop at a bounded synthetic contract result. Real toolkit/AT/platform, upstream, credential-boundary, provider/account and counsel qualification remain separate gated work.

Stop immediately on attempted real credential/provider/model/network access, unapproved code/import/install, unknown authorization widening, missing witness, oracle sensitivity failure, hard resource/time limit, canonical divergence or unsafe cleanup. Preserve the failing trace. Fixes create new candidate identities; never remove a failing case to manufacture PASS.

## Recommendations rivals falsifiers and nonproofs

All recommendation rows are IN. Each carries a conforming rival; unsafe alternatives are negative controls, not the only competition. None can weaken accepted Owner requirements.

| ID and recommendation | Genuine rival | Decisive falsifier | Passing does not prove |
|---|---|---|---|
| U01 fixed semantic point taxonomy with host-required shell | Smaller universal typed-list/form algebra with profile-defined point grouping and the same mandatory shell | A required workflow cannot express facts/actions without a new client semantic implementation, or taxonomy hides a mandatory control | Ideal information architecture, usability or no future schema evolution |
| U02 detached exact manifest contribution schema | Reviewed future manifest revision embedding the same typed data with preserved frozen legacy bytes | Missing/ambiguous identity, direct grant injection, collision or dependency allows render/dispatch; UI-03/05/19 | Complete implementation validation, portability or cheap conversion |
| U03 pure versioned materializer over frozen input closure | Independently implemented client materializers checked against the same semantic corpus | Same complete input/profile yields different tree, or any hidden inference/index/activation occurs; UI-01/02/17 | Identical cross-client pixels or general determinism under unspecified inputs |
| U04 shared semantic artifact plus client-specific materialization | One richer artifact containing explicit semantic and per-client subtrees under identical source bindings | Artifact diff confuses locale/layout with authority, private digest leaks across domains or stable command identity changes | Secure hashing, source truth, provenance completeness or chosen encoding |
| U05 scope-specific fail-closed negotiation with verified semantic fallback | Require a complete exact contract profile before any affected workflow starts, without per-point downgrade | Unknown safety semantics reachable through alternate ingress, or optional missing view globally disables valid independent control; UI-03/04/11 | Proof against a malicious host lying about human review |
| U06 inert declarative nodes first, separately qualified rich views | Independently confined rich-view realization from the start with exact capability/bridge restrictions | Direct/induced cross-projection/credential/effect access, spoofed host controls, destructive focus or injected terminal action; UI-09/10 | A production sandbox, cross-view isolation, credential non-access or universal parser safety |
| U07 explicit backend fence and observed-client invalidation | Online-only protected rendering without offline cache, or an explicitly approved bounded offline read policy | Newly denied backend operation passes; offline client claimed instantly erased; stale reconnect hydrates before authorization; UI-07/08 | Retroactive erasure, uncompromised device or selected retention policy |
| U08 complete semantic fallback and platform accessibility gates | Separate accessible renderer/client realization with equivalent supported facts and controls | Missing required fact/action, wrong reading order, inaccessible focus/Stop or motion-only meaning; UI-02/16 | WCAG conformance, native AT correctness, accessible human experience or universal language support |
| U09 C×V factorial with independent hard-zero and reserve oracle | Targeted pairwise screening followed by the same full-profile held-out confirmation | Factor interaction, unbounded queue, concealed cost or Stop starvation missed by cheaper design; UI-18 | Production performance, workload generalization or savings |
| U10 one command catalog and stable canonical key across clients | Independently coded surface bindings with a complete shared semantic oracle | Same target/intent has divergent meaning/refusal, changed principal bypasses conflict or reconnect duplicates effect; UI-11/15 | Exactly-once external effects, durable real storage or route eligibility |
| U11 adapt public extension precedents with explicit loss map | Implement the same capability natively under the same fixtures | Port requires broader authority or measured accepted-port effort including upgrades exceeds native alternative | Low porting cost, ecosystem-wide compatibility or license/terms clearance |

U11's future port/rewrite comparison must include implementation, review, failed ports, accessibility, isolation, dependency/license obligations and two pinned upgrade cases for identical accepted behavior. Acceptable port count may be zero. No port was attempted here.

## Conflicts and Owner gates

| Question or conflict | Current disposition and required next evidence |
|---|---|
| Same input promise omits client/locale/layout | Resolved as candidate specification: freeze full closure for same-tree claim; compare semantics across clients |
| Immediate removal versus disconnected view | Physical impossibility of unseen update is explicit; backend fence and observed-client invalidation are separate. Private offline retention still requires an Owner policy |
| No plugin element when disabled versus visible incompatibility | Host-owned safe inventory/refusal explanation is allowed; zero plugin node/command/activation. Scope and shared-supplier attribution explicit |
| Unknown optional UI versus mandatory controls | Host shell persists; genuine equivalent fallback allowed; only affected workflow/profile blocked when required semantics absent |
| M1B closed schema versus new UI fields | Detached application/evidence candidate; no frozen M1 bytes, meanings, refusal alphabet or Stop wire arm changed |
| UI negotiation versus authorization | Support is evidence, never a grant; actual current checks remain in existing admission and read-disclosure boundaries |
| GUI later versus D-019 comprehensive opt-in packaging | Preserved unresolved release-timing wording; no deferral or new release choice made |
| Privacy/publication partial orders under G-09 | Undefined cells remain blocked-definition; no numeric trust ranking or implicit wildcard invented |
| Rich widget sandbox and D-029 credential boundary | Mechanism unselected; each exact profile needs direct/induced-access proof and platform qualification. Policy-only is not an automatic strong-profile fallback |
| Current MCP versus legacy handshake | 2026-07-28 request metadata distinguished from 2025-11-25 initialization; no protocol selected for Recursion |
| Accessibility/performance/porting claims | Candidate fixtures exist; all actual measurements and conformance remain U |

## Completion and question coverage

The contract answers all 22 questions at specification depth; implemented acceptance remains unverified.

| Questions | Answer location |
|---|---|
| Q1 point identity/stability; Q2 inputs/commands/accessibility/resources; Q3 manifest/collision; Q4 presentation boundary | Contribution taxonomy; exact schema/ownership; collision rules; security boundary |
| Q5 determinism; Q6 effective set; Q7 inspectable artifact; Q8 one command meaning | Deterministic materialization passes/input closure; canonical identity/diff; parity |
| Q9 unknown refusal; Q10 versions/partial/deprecation; Q11 downgrade/inert omission; Q12 accessible degradation | Fail-closed matrix, scope-specific downgrade resistance, fallback floor, UI-03/04/06/16 |
| Q13 isolation; Q14 injection/terminal/clipboard/links; Q15 disabled proof; Q16 lifecycle/revocation | Security and lifecycle; narrow allowlists; observed/offline boundary; UI-06–10 |
| Q17 ten controls; Q18 Stops/mechanisms; Q19 receipts/GAP/slow clients; Q20 cross-client parity | Exact evidence profiles and complete control/Stop maps; continuity vector and parity criterion |
| Q21 fixture predicates; Q22 zero hidden work and bounded load | UI-01–20, C×V soak, independent tripwires and finite local handoff |

Completion gates:

- Typed versioned namespaced taxonomy, stability and per-point fallback: specified
- Manifest attachment, supplier identity, typed projections/commands and presentation-only ownership: specified; frozen M1 preserved
- Full-input deterministic ordering, zero-model render, versioned diffable effective artifact with filled/omitted reasons: specified
- Unknown/version negotiation, downgrade/inertness and accessible fallback: specified; required semantics cannot be hidden
- Isolation obligation, authority_carried_none, terminal/OSC/clipboard/deep-link behavior and violation fixtures: specified; mechanism and behavior unqualified
- All ten controls and three Stops plus checkpoint/interrupt/drain mapped to exact inspected evidence/configuration profiles with unknowns: specified; no route qualified
- Positive/adverse fixtures and 0/1/5/10/20 contribution and view counts with exact predicates: specified, all target runs UNEXECUTED
- Every recommendation has a rival, decisive falsifier and nonproof: U01–U11
- No measured performance, accessibility/UI conformance, route qualification, entitlement, cross-view security boundary or port-cost claim: explicit
- Protected source files untouched; document-only QA and bounded privacy/secret-pattern check are recorded separately. A clean artifact scan is not universal secret detection

## What this report does not establish

There is no implemented capability-driven materializer, accepted schema revision, measured deterministic runtime, verified client parity corpus result, measured accessibility conformance, qualified browser/native/terminal isolation, physical cache erasure, route entitlement, provider cost, subscription saving, real process containment, durable storage proof, usable latency threshold or measured porting advantage from this work. Source-documented controls and historical synthetic evidence do not fill those gaps. Missing knowledge stays unknown; D-034 remains a falsifiable thesis rather than a feature-count claim.

## Source links

Repository citations below all identify inspected tracked files at the complete current source pin. Earlier report pins inside those files remain historical. Public links identify the retrieved document and version/date scope described above; no public-page hash is claimed from a snippet.

[R-AUTH]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/CONTROL_PLANE.md
[R-DEC]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/state/DECISIONS.md
[R-IS]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/INTERFACE-STRATEGY.md
[R-TR]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/TERMINAL-RUNTIME.md
[R-M1B]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/M1B-WIRE-PROFILE.md
[R-PERF]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/PERFORMANCE-PLAN.md
[R-PLUG]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/PLUGINS-AND-EDITIONS.md
[R-RA]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/dot-ra-rd-20261002/raw/R-A/report.md
[R-RL]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rl/report.md
[R-RLC]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rl/proposed-contracts.json
[R-RK]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rk/report.md
[R-RN]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rn/report.md
[R-SC]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/Recursion_Shared_Contract_Reconciliation.md
[R-PS]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/Recursion_Prompt_Plugin_Skill_Architecture.md
[R-ORCH]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/Recursion_Harness_Orchestration_Performance.md
[R-CORPUS]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/synthetic_benchmark_corpus.json
[R-GAPS]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/GAPS.md
[R-IPR]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/construction/interface-probes-20260907/evidence.json
[R-ROUTES]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/ROUTE-CAPABILITIES.md
[R-RF]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rf/report.md
[R-RFS]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rf/sources.json
[P01]: https://json-schema.org/draft/2020-12/json-schema-core
[P02]: https://json-schema.org/draft/2020-12/json-schema-validation
[P03]: https://www.rfc-editor.org/rfc/rfc8785
[P04]: https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning
[P05]: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
[P06]: https://modelcontextprotocol.io/specification/2026-07-28/server/resources
[P07]: https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/docs/specification/2026-07-28/server/prompts.mdx
[P08]: https://code.visualstudio.com/api/references/contribution-points
[P09]: https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx
[P10]: https://code.visualstudio.com/api/extension-guides/webview
[P11]: https://developer.android.com/privacy-and-security/risks/insecure-webview-native-bridges
[P12]: https://www.w3.org/TR/WCAG22/
[P13]: https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html
[P14]: https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html
[P15]: https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
[P16]: https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html
[P17]: https://learn.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32
[P18]: https://developer.apple.com/documentation/accessibility/integrating-accessibility-into-your-app
[P19]: https://gnome.pages.gitlab.gnome.org/at-spi2-core/libatspi/

# R G Plugin import and cross harness reuse

Decision evidence pack for Recursion v3 · 2026-10-02 · Research and contract design only

## Executive finding

**The evidence supports a common description and admission contract, with explicit per-host bindings. It does not establish a universal executable plugin contract or cheap ports.** A Recursion manifest can describe the union of foreign contributions only if it also describes what cannot be realized, what is degraded, and which source semantics remain unresolved. Calling that a semantic superset before those obligations pass would conceal the hardest work.

Three findings make this concrete:

- **D:** the [Cordis mechanism note](#cordis-mechanism-facts) supplies the documented stress cases. **I:** importing declarations cannot reproduce arbitrary code behavior or prove containment.
- **D:** the [OpenCode migration note](#opencode-migration-facts) supplies a published counterexample to manifest-only portability. No local implementation was run.
- **D:** the [common-package](#agent-plugins-facts) and [host-format notes](#cursor-plugin-facts) establish distinct packaging profiles. **I:** common-format branding does not remove host-specific transformation obligations.

**U:** No ecosystem has the highest *validated* porting leverage. No accepted-equivalent port, labor measurement, runtime conformance result, or representative ecosystem census was produced in this session. A count of zero locally demonstrated imports is an absence of measurements, not an estimate that the ecosystems contain zero portable plugins.

**I, conditional research priority:** evaluate a narrow MCP callable-capability slice as the cross-host control and Cordis as the first rich host-semantics stress case. The competing option is a Cordis-first-only pilot or native equivalents. The decisive falsifier is that their accepted total cost or required-behavior preservation is worse than the alternatives under the paired procedure in section 9. This is an evaluation order, not a vendor/runtime selection, release reduction, or acceptance of a particular adapter. It does not change D-023's first upstream qualification decision.

D-019 remains the comprehensive build, lean default, opt-in release decision. Failed imports imply native implementation, a different compatible binding, or an Owner-visible delivery problem; they do not authorize deleting the capability. D-026 remains Apache-2.0 direction for Recursion's own work, subject to its stated release/counsel gates. D-033 remains the hypothesis **“porting is cheap”**, falsified for a declared stratum by accepted port cost above a matched native rewrite, no clean import in that stratum, or any required authority/privacy/evidence loss.

## Basis and evidence discipline

The authoritative source snapshot is commit `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. Read-only inputs included CONTROL_PLANE, ANCHOR, decisions D-017 through D-033, the active v3 goal, PLUGINS-AND-EDITIONS, current research coverage/gaps, the R-G directive, and the current-branch committed R-A report, schema and proposed contract. No prior uncommitted R-A material was used.

The active parent goal is `goal-recursion-v3-harness-orchestrator`. Lucas is final authority. Hermes is an optional integration, not the executive control plane. Older orientation or bridge-deferral sentences do not reopen the current explicit D-019/D-032 framing. This report changes neither source files nor decisions.

Labels:

- **D — source-documented:** a current primary page or pinned public source states it; this is not an execution observation
- **O — locally observed:** file/content identity and the existence of the output artifacts only
- **I — inferred/proposed:** this report's comparison, mapping or proposed contract
- **U — unknown/unverified:** absent evidence, unresolved semantics or unmeasured outcomes; never zero by substitution

All proposed normative rules below are **I**, including MUST and MUST NOT. They are an extension to R-A for review, not ratified product behavior. Public-document captures are date/digest pinned in `source-register.json`; a retrieval digest identifies the captured excerpt, not a build. DeepSeek uses an immutable public commit. MCP uses explicit protocol revisions and Agent Plugins uses 1.0.0. Mutable OpenCode V2, Goose and VS Code documentation is not assigned an invented executable release. The previously recorded Goose immutable URLs could not be re-retrieved in this session; current official Goose documentation was used and its source-release correspondence remains U.

No target harness/plugin, model/provider, installer, benchmark, test suite, account, credential flow, live host, or paid service was invoked. All test designs are **UNEXECUTED**. No language, store, framework, runtime, package manager, sandbox or vendor is selected. No upstream is claimed supported, certified, secure, stable or CVE-free. No public query contained private repository text or identifiers.

## 1 R G Q01 Importability matrix

Question ID: R-G.Q01

The six required named ecosystems appear in the requested order. MCP's current and compatibility profiles are separate rows. “No common grant found” below describes the reviewed surface, not a proof that upstream has no security controls.

<a id="cordis-mechanism-facts"></a>
**D — Cordis mechanism note:** plugins can be functions with `inject`/`apply` or Service subclasses. Loader composition can evaluate expressions; dependency activation, scoped effects/listeners/disposers, event dispatch variants and order-sensitive short-circuit middleware belong to its host semantics. Services, events, prompts, tools and provider/adapter components are contributions [RG-S02]. Tool input/output schemas, model/UI projections and monotonic guards are separately documented [RG-S03]. **U:** third-party cleanup correctness and equivalent Recursion enforcement.

<a id="opencode-migration-facts"></a>
**D — OpenCode migration note:** V1 hook-returning implementations do not run unchanged in V2, although configuration can be converted mechanically. V2 uses stable `id` and `setup(ctx)` with package/options configuration. Migration changes teardown/disposal, domain registration and prompt/context timing; CLI and server contributions require separate treatment [RG-S09]. **I:** configuration conversion is not an accepted port; exact mapping/behavior is a separate test.

| Ecosystem and profile | Unit and manifest | Discovery | Lifecycle | Permission or capability declaration | Contributions |
|---|---|---|---|---|---|
| DeepSeek Harness and vendored Cordis | D: [mechanism note](#cordis-mechanism-facts), unit/configuration | D: same note, activation; discovery topic [RG-S01] | D/U: same note, scope/cleanup | D: tool restrictions [RG-S03] [RG-S04]; I: no complete OS/credential grant | D: same note, contribution/schema inventory |
| OpenCode V1 | D: module exporting plugin functions returning hooks; host config lists packages; U: complete static declaration of runtime behavior [RG-S07] | D: global/project config and local plugin directories; startup auto-loading and package installation [RG-S07] | D: initialization/ordered hooks [RG-S07]; [migration note](#opencode-migration-facts); U: quiescence | D: host allow/ask/deny rules, pattern and precedence semantics; I: not proof that arbitrary plugin code is contained [RG-S08] | D: tools, events, shell environment and compaction hooks; SDK context [RG-S07] |
| OpenCode V2 server and separate CLI surface | D: [migration note](#opencode-migration-facts); separate CLI definition [RG-S12] | D: config arrays, local/package discovery; missing packages may install in background; ordered disable/re-enable rules [RG-S11] | D: setup/cleanup, disposable registration, reload and ordered transforms; U: all callback settlement [RG-S10] [RG-S11] | D: domain permission operations and evaluation hooks; explicit configured deny is final for that hook path; I: no equivalent Recursion grant follows [RG-S10] | D: domain tools, hooks, integrations, agents, storage; CLI commands/routes/slots/renderers [RG-S10] [RG-S12] |
| Goose external MCP, builtin and platform extensions | D: configured extension union, including builtin/platform/stdio/streamable_http; not one portable code ABI [RG-S16] | D: extension config, directory and session management; enabled defaults and current-session state differ [RG-S15] | D: per-session enabling/disabling; defaults affect future sessions; U: generic teardown/effect settlement [RG-S15] | D: tool filters plus host modes; read/write classification is documented as best effort; I: filtering is not server containment [RG-S16] [RG-S17] | D: MCP-based external capabilities, builtins and host-global platform features; U: full exportability of every platform feature [RG-S15] |
| MCP 2026-07-28 | D: protocol server, not a package manifest; wire schemas and capabilities [RG-S19] | D: host chooses endpoint/process; `server/discover` required of servers, optional for clients; self-reported identity [RG-S20] | D: [MCP era/identity facts](../protocol-edges/report.md#era-and-identity); transport lifetime is a separate profile | <a id="mcp-authorization-facts"></a>D: audience-bound HTTP authorization is separate from feature declarations; stdio receives credentials through its environment [RG-S23]. I: neither grants Recursion authority | D: tools, resources, prompts, elicitation and explicitly profiled extensions; typed/multimodal tool results [RG-S19] [RG-S21] |
| MCP 2025-11-25 compatibility | D: legacy protocol server with initialization capabilities [RG-S22] | D: `initialize`/`initialized` lifecycle, host-local endpoint configuration [RG-S22] | D: initialization, operation, transport shutdown and cancellation; I: disconnect does not establish rollback [RG-S22] | D: negotiated legacy features; U: Recursion containment without a qualified binding [RG-S22] | D: legacy feature evidence [RG-S22]; I: require an explicit [era binding](../protocol-edges/report.md#era-and-identity) |
| <a id="vscode-activation-facts"></a>VS Code extension | D: `package.json`, required identity/version/engine fields, declarative contributions and optional main/browser entrypoints [RG-S24] | D: installed extension plus activation events; some contributions imply activation in specified newer versions [RG-S25] | D: activate/deactivate contract; U: arbitrary cleanup, host failure or external effect settlement [RG-S25] | D: untrusted/virtual workspace declarations; limited-mode implementation obligations; I: workspace trust is not a per-operation OS grant [RG-S24] [RG-S26] | D: commands, editor/workbench/UI, languages, tools and AI instruction contributions [RG-S27] |

**I:** A foreign package without a declarative manifest is still representable as an opaque source artifact plus a reviewed static import descriptor. It is not statically discoverable in full merely because source is available. A loader MUST NOT execute a plugin, evaluate configuration expressions, run dependency installation, or ask a model to discover what it contributes. Missing required information becomes `unknown`, not an empty request set. Recommendation R1 and its alternative/falsifier are in section 12.

## 2 R G Q02 Distance from the R A contract

Question ID: R-G.Q02

Mapping classes are orthogonal to evidence classes: **direct** preserves a documented value; **mechanical** applies a pinned deterministic rule; **annotation** needs an independently reviewed semantic assertion; **none** means the foreign surface has no adequate counterpart in the reviewed material. All proposed mappings are I, grounded in the D inputs above. A direct metadata mapping is never direct authority.

| Ecosystem | Direct candidates | Mechanical candidates | Semantic annotation required | No adequate counterpart in reviewed import surface |
|---|---|---|---|---|
| Cordis | I: package identity when provided; tool input/output schema data [RG-S03] | I: translate the [canonical mechanism inventory](#cordis-mechanism-facts) into source/dependency/binding-local references | I: review every [mechanism-note obligation](#cordis-mechanism-facts), including coverage and semantic loss | I/U: detached Recursion grant, privacy/budget vector, publication authority and independent acceptance; arbitrary config expressions cannot supply these |
| OpenCode V1 | I: package metadata, literal tool description/schema where extractable [RG-S07] | I: config source/entrypoint inventory, hook-name lookup, tool namespace [RG-S07] | I: schema-library conversion, implicit code-discovered hooks, permission precedence, environment effects and experimental hooks [RG-S08] | I/U: complete static contribution inventory, effect settlement, typed output/evidence when absent, canonical privacy/billing bounds |
| OpenCode V2 | I: stable id/options, documented domain metadata [RG-S10] | I: configuration normalization under the [migration note](#opencode-migration-facts); discovery/registration inventory [RG-S11] | I: review phase/placement obligations from the [migration note](#opencode-migration-facts), plus storage/session scope [RG-S12] | I/U: self-issued authority, cross-host storage guarantees, terminal-specific callbacks in another host, independent acceptance |
| Goose | I: name/type/timeout/enabled as *source facts*; tool filter list [RG-S16] | I: `cmd`/`uri` and transport spelling into binding references; timeout units with exact conversion [RG-S16] | I: empty filter means all, default/current-session split, env/secret references, builtin/platform export scope [RG-S15] [RG-S16] | I/U: grants from `enabled`, a portable implementation for every platform feature, deterministic classification from permission modes [RG-S17] |
| MCP | I: exact tool schemas, resource/prompt metadata, explicit protocol revision [RG-S20] [RG-S21] | I: server-bound namespaces, attempt correlation and encoding under the [canonical era profile](../protocol-edges/report.md#era-and-identity) | I: annotation trust, audience, cache scope, logical resources and interaction outcomes [RG-S21]; apply the [auth fact cell](#mcp-authorization-facts) | I/U: package license/install closure, full egress/billing/credential bounds, effect commit/replay guarantee, truthful independent evidence |
| VS Code | I: publisher/name/version, engine requirement, declared contributions [RG-S24] | I: publisher-qualified identity, contribution taxonomy lookup, declarative asset inventory [RG-S27] | I: activation implicits by host revision, `when` conditions, workspace trust, main/browser binding, UI/workspace placement [RG-S24] [RG-S25] [RG-S26] | I/U: workbench behavior without its host; broad API equivalence; canonical grant/accounting; rights inferred from Marketplace availability [RG-S28] |

### Complete R A field disposition

This cross-cutting checklist prevents easy identity mappings from hiding unmapped security fields. It applies to every row, not only MCP.

| Existing R-A field or record | Proposed import disposition |
|---|---|
| `schema_epoch`, `contract_revision` | I: supplied by the recognized Recursion import profile, not copied from foreign package version |
| `identity` | I: preserve foreign identity as a claim; mechanically namespace it; hash supplied bytes under a defined inventory; absent foreign version remains unknown, never fabricated `0.0.0`; a valid canonical manifest still needs its own reviewed identity/version, otherwise it remains an incomplete blocked candidate |
| `compatibility` | I: preserve source API/protocol requirements and add exact adapter/host/schema pins; do not equate semver ranges across ecosystems |
| `contributions[]` | I: enumerate each discovered or author-annotated contribution; assign stable identity, descriptor, schemas, binding and required status; account for unsupported entries |
| `requires[]` | I: dependency and capability candidates only; infer no permissions from an imported hook, shell command or service injection |
| `admission_contract_ref` | I: canonical registry reference supplied by importer; cannot be specified as a foreign executable callback |
| `attenuation` | I: retain mandatory parent containment; foreign delegation defaults have no authority; unsupported enforcement blocks admission |
| `privacy` | I: reviewed labels, compartments, recipients, purpose and retention; missing required label stays unknown and is refused |
| `bounds` | I: reviewed resource/billing/egress constraints with units and uncertainty states; foreign timeout is only one field, not a budget |
| `evidence_contract` | I: explicit canonical evidence requirements; host result/log becomes an attributed claim, not acceptance |
| `dependencies[]` | I: distinguish install dependencies, runtime services, optional features and externally provided hosts; no dependency auto-grant or auto-enable |
| `extensions` | I: opaque namespaced adapter data plus provenance; no override of canonical fields; unknown required extension blocks use |
| InstallationRecord | I: source-enabled/default flags recorded separately; actual imported instance starts disabled and without a grant |
| AuthorityGrant | I: only the kernel may issue it; source manifest, translator and plugin cannot write one |
| RouteProfile | I: exact source and host correspondence, supported subset, loss record, enforcement/qualification evidence; current default state `design-only` |
| EvidenceItem and HonestAccounting | I: add translation/profile digests and retained source-boundary identity; preserve null/unknown resource counters and completion/acceptance/settlement separation |

## 3 R G Q03 Evidence based leverage ranking

Question ID: R-G.Q03

**U:** “Highest validated leverage” cannot be ranked from these sources. An eligible-plugin denominator, accepted behavior per plugin, port cost and maintenance cost are missing. Popularity, a large directory, a permissive host license and a rich manifest are not substitutes.

The following is a **conditional evaluation order**, R2. The order optimizes information gained about the import hypothesis, not a final component choice. It preserves Cordis as the first detailed rich-ecosystem investigation.

| Evaluation tier | Evidence favoring investigation | Evidence limiting leverage claim | Population and license boundary |
|---|---|---|---|
| A: explicit MCP callable subset, with Goose as one client-shaped fixture | D: specified wire schemas and a documented cross-agent extension mechanism [RG-S19] [RG-S21] [RG-S15] | I: authentication, lifecycle and evidence remain host responsibilities; current/legacy split matters | U: eligible-server count and labor savings; each server's source/dependencies/service terms require separate review |
| A: Cordis rich tool/service slice | D: pinned public design, typed output and monotonic guard mechanisms; root MIT and vendored notices available [RG-S03] [RG-S05] [RG-S06] | D: developer preview with breaking-change warning [RG-S01]; I: executable composition and host dependencies increase semantic work | D: public plugin discovery topic [RG-S01]; U: maintained compatible population; root license is not closure clearance |
| B: OpenCode V1 and V2 as separate migration strata | D: public extension docs and ecosystem list [RG-S07] [RG-S13]; V2 API expresses richer domain operations [RG-S10] | D: [migration constraint](#opencode-migration-facts); U: exact V2 executable/source correspondence | D: viewed root repository license says MIT [RG-S14]; U: per-plugin rights and V2 closure; no corpus count |
| C: VS Code declarative assets and extracted protocol/business-logic slice | D: explicit manifest, engine bounds and contribution taxonomy [RG-S24] [RG-S27] | I: rich workbench callbacks and environment-specific behavior are expensive candidates; runtime equivalence unknown | D: official FAQ separates source, distribution, extension and Marketplace rights [RG-S28]; U: count legally eligible for this use |

Agent Plugins 1.0.0 is a **cross-cutting package comparison**, not a seventh runtime selected for Recursion. See the [canonical package fact cell](#agent-plugins-facts); the comparison cannot reduce Recursion's accepted contribution taxonomy.

**Competing option:** rank solely by Cordis's feature richness and port a broad plugin immediately, or skip imports and implement matched native capabilities. **Falsifier:** the paired corpus shows higher accepted-equivalent cost, lower useful behavior, or more critical failures for the proposed tier-A slices than either competitor. **Non-proof:** this order establishes neither market adoption nor delivery feasibility for D-019.

## 4 R G Q04 Unportable behavior and explicit loss

Question ID: R-G.Q04

**I:** “Unportable” is always relative to a source contribution, target profile, version and required semantics. It means no approved mapping currently exists; it is not a universal impossibility claim about all future implementations.

| Unportable or unresolved case | Required representation and disposition |
|---|---|
| Host SDK objects, private APIs, direct global registries or process introspection | `HOST_API_UNAVAILABLE` or `UNDOCUMENTED_API`; retain source binding and blocked contribution; no guessed replacement |
| Cordis around-middleware versus a host's after-event notification | `EVENT_ORDER_OR_CONTROL_LOSS`; include source/target timing, mutation and short-circuit differences; required guard cannot degrade to observer |
| Executable loader expressions or dynamic registration | `DYNAMIC_DESCRIPTOR_UNRESOLVED`; inert source reference plus reviewed sidecar needed; no evaluating to enumerate |
| UI callbacks, workbench state, terminal slots, editor selections, native/browser-specific modules | `HOST_UI_UNAVAILABLE` or `RUNTIME_REQUIREMENT`; optional output may have an approved alternative renderer; required interactions block |
| Foreign credentials, ambient environment, host auth store or wider OAuth scope | `CREDENTIAL_BOUNDARY_UNREPRESENTABLE`; preserve symbolic need only; do not copy secret material or authorize scope expansion |
| Tool reads marked safe only by an annotation or heuristic | `EFFECT_CLASS_UNVERIFIED`; cannot become a read-only grant solely through metadata |
| Missing output schema, identity, accounting or effect settlement | `EVIDENCE_OR_SETTLEMENT_UNAVAILABLE`; generic success cannot repair it; unknown cost stays unknown |
| Storage transactions, subscriptions, remote session state or task handles with no equivalent lifetime | `STATE_OR_LIFECYCLE_LOSS`; declare expiry/restart/fencing limitations; no invented exactly-once claim |
| Non-redistributable assets or unresolved dependency/license terms | `RIGHTS_UNRESOLVED`; provenance retained, payload excluded from an import distribution; counsel/Owner decision remains separate |
| Unsupported schema dialect, transport, required extension or API revision | `SCHEMA_OR_PROFILE_UNSUPPORTED`; preserve exact original and failure boundary, no semantic downgrade |

This representation is R3. **Competing option:** emulate the full source host with inert metadata discovery, explicit loss and identical admission gates. **Negative control:** silently skip unsupported contributions. **Falsifier:** a declared “partial” import executes a required-lost contribution, hides a loss, or needs opaque extension fields to override the canonical contract. **Non-proof:** listing a loss is not an implementation, legal clearance, or evidence that a substitute is equivalent.

## 5 R G Q05 Concrete translation layer and non widening boundary

Question ID: R-G.Q05

### Detached records extending R A

**I, R1/R3:** Preserve R-A's PluginManifest, InstallationRecord, AuthorityGrant, RouteProfile and EvidenceItem ownership. Add the following records instead of mutating the source package or issuing authority from a converter.

| Record | Writer and fields | Purpose |
|---|---|---|
| ForeignArtifact | Read-only intake; ecosystem/profile, source URI, revision, byte inventory/digest, manifest/config paths, license-evidence references | Distinguishes source bytes, executable payload, mutable docs and claimed metadata |
| ImportProfile | Independently reviewed adapter contract; parser/dialect revision, source schema/API pins, mappings, containment rules, recognized extensions, fixture references | Defines a deterministic interpretation; never contains effective credentials or grants |
| TranslationRecord | Deterministic importer; input digests, ImportProfile digest, canonical candidate digest, per-field mappings, unresolved items, warnings, loss refs, reverse-map status | Makes each transformation inspectable and reproducible |
| MappingEntry | Importer plus attributed semantic annotation; source pointer/span, target pointer, mapping class, rule ID/revision, before/after digests, evidence class/ref | Separates mechanical changes from human-reviewed semantic claims |
| ContributionRealization | Profile author/reviewer; source contribution ID, canonical ID, target binding, availability, required status, equivalence requirements, losses, qualification | Separates capability existence from a particular host implementation |
| LossRecord | Importer/reviewer; ID, affected contributions/scenarios, dimension, source semantics, target semantics, severity, required/optional, reason, remedy, decision ref | Represents explicit degradation or inability to translate |
| ImportReview | Independent reviewer; exact candidate/source/profile/loss digests, covered scenarios, unresolved blockers, disposition and reviewer identity | Acceptance boundary; translator completion is not acceptance |

Graph additions: ForeignArtifact `translated-by` ImportProfile; TranslationRecord `derived-from` ForeignArtifact and `proposes` PluginManifest; ContributionRealization `realizes` Contribution `via` RouteProfile; LossRecord `limits` realization; ImportReview `attests-to` a fixed candidate. These are provenance/compatibility edges, never `permits` edges. Only kernel-issued AuthorityGrant produces permission. Existing `requires`, `depends-on`, `attenuates-from`, `consumes`, `produces` and `revoked-by` retain their R-A meanings.

### Deterministic stages

1. **Intake bytes as data.** Validate path inventory, total bytes, depth/count and recognized encoding. Reject escapes, collisions and unsupported required versions. Do not import executable modules, expand ambient environment, resolve credentials, install dependencies, fetch schemas or follow source-supplied URLs.
2. **Parse through a pinned profile.** Retain exact input bytes and an inert parsed form. Distinguish declared contributions from incomplete source/code inspection. Unknown fields receive a disposition; no default-enabled behavior enters InstallationRecord.
3. **Classify every mapping.** Direct/mechanical rules produce deterministic candidates. Semantic annotations are separately authored, attributed and versioned. Missing required semantics block a usable import. A model may not invent a grant, effect class or equivalence proof.
4. **Compile canonical requests.** Build R-A manifests/graph candidates and a complete loss map. Resolve dependencies without activation. Bind canonical logical resources to target resources through a reviewed profile; string resemblance is not containment.
5. **Independent review.** Review source correspondence, rights evidence, semantic annotations, profile and losses. Store a detached result. No review result installs or activates itself.
6. **Separate admission.** If later explicitly authorized, the kernel admits a particular goal, principal, attempt, source/payload/profile digest and epoch under current grants. Installation and activation are distinct effects. Recheck authority at each new effect, after transformations and on route/config revision changes.

### Required non widening relation

Let `R` be the translated *request* relation and `E` the actually admitted effects. For each effect, the proposed kernel must establish:

`E ⊆ R ∩ ConstitutionalBoundary ∩ GoalSpec ∩ ParentGrant ∩ CurrentOwnerPolicy ∩ EnforceableRouteProfile`

This is a semantic containment obligation over operations, resources, principals, time, recipients, data labels, credentials, delegation, publication and budget. It is not string intersection. Sibling grants are not unioned. A foreign `allow`, `enabled`, dependency injection or host success message cannot enlarge any term.

For resource amounts, child reservations and outstanding admitted effects must fit all applicable parent ceilings; unknown required cost or absent enforcement is a refusal. For privacy, a permissible operation still requires permitted labels, purposes, compartments and recipients. For credentials, a symbolic need or host-authenticated connection never implies permission to read the secret. For publication, tool availability never implies authority to send/publish. For billing, changing a host or model cannot silently convert an included route into metered usage.

**I:** Mutable hooks run before final canonical authorization or are limited to a proposal channel; the kernel revalidates the final effect. A plugin cannot approve itself. Revocation fences new effects, while previously admitted effects remain settling/unknown until evidenced. Disable, disposer return, socket close and process termination do not prove rollback.

**U:** This report supplies a contract that forbids widening; it does not demonstrate an enforcement implementation. D-029's trusted launch boundary remains essential for profiles claiming strong credential non-access. If the target host exposes wider ambient authority than the binding can constrain, that realization is incompatible or explicitly policy-only, never silently classified as strongly contained.

### Reversibility without overclaiming

**I:** Byte recovery is possible by retaining the original immutable input. Semantic round-trip is a separate claim. For an invertible field, `decode(encode(x), retained-foreign-data) = x` under the pinned normalization. Defaults, implicit discovery, case collisions, dropped unknown fields, generated bindings and handwritten annotations may make the inverse partial. Record `exact`, `semantic-only`, `partial`, `not-invertible` or `unknown` per mapping; prohibit a global “reversible” label when a required mapping is lossy. Preserve foreign unknown data as inert data; never serialize canonical grants back into the upstream package.

**Competing option for R1:** in-process native loading of each ecosystem, or a universal host emulator. **Falsifier:** the staged translation either widens any boundary, cannot enumerate unresolved required fields without executing code, or costs more than the equivalent alternative at accepted quality. **Non-proof:** deterministic manifests do not provide OS isolation, safe code, lifecycle settlement or a release-ready loader.

## 6 R G Q06 Partial imports and honest availability

Question ID: R-G.Q06

**I, R3:** Store independent axes rather than a single “supported” boolean:

- `translation_state`: exact / partial / unresolved / rejected
- `availability`: present / missing-dependency / unavailable / unknown
- `installation_state`: absent / installed-disabled / installed-enabled
- `activation_state`: inactive / active / draining / failed / cleanup-unknown
- `qualification_state`: design-only / observed-not-accepted / independently-accepted / rejected / revoked
- per-scenario `required_semantics`: preserved / degraded / unsupported / unknown

A capability present in the source can have an unavailable target binding. A package with three of four contributions translated is not “75% usable” without knowing whether the fourth is essential. Required authority, privacy, evidence and settlement semantics cannot be marked optional to improve the port rate.

Example: source plugin supplies a required report tool and optional workbench panel. The target preserves the tool's schemas and output bytes, but has no panel host. Record `HOST_UI_UNAVAILABLE` against the panel, show a partial import, and permit only the already-approved tool scenario if the loss policy allows that exact optional loss. If the panel was the only approval surface, it is required and the same import is blocked. This is an illustrative proposal, not an executed port.

The four existing incompatibility responses remain available: state incompatibility; recommend combinations; no action; notify and recommend. For a pre-admission refusal, record `status=incompatible`, `attempted=false`, `effect=none`. Recommendations remain inert; no automatic repair, install, reroute, credential request, model call or inference. A failure after an effect has begun must instead preserve failed/cancelled/uncertain/settling status.

Every invocation receipt references the active loss/profile/config revision. Required losses block invocation. Optional losses require a predeclared workflow acceptance policy or specific review, never an importer deciding that an inconvenience is harmless. A later host/plugin update invalidates only the relevant realization evidence, but cannot preserve an accepted label without checking its bound assumptions.

## 7 R G Q07 One plugin serving multiple harnesses

Question ID: R-G.Q07

**I:** Yes as a design pattern: one capability specification and shared business-logic/assets, with a realization per host. **U:** No common binary, common permission model, common lifecycle, or locally accepted multi-host plugin is established.

| Shape | What is documented | Reuse conclusion and limit |
|---|---|---|
| Agent Plugins 1.0.0 | <a id="agent-plugins-facts"></a>D: root package with skills/MCP and namespaced client-specific additions [RG-S29] [RG-S31] | I: common packaging plus per-host overlays; U: actual savings and equivalent behavior |
| OpenAI and Cursor package consumers | <a id="cursor-plugin-facts"></a>D: OpenAI defines portable fields/overlay precedence [RG-S32]. Cursor supports common and host formats but differs in placeholder expansion [RG-S33]; exact variables and resolution are fixture inputs in RG-T06 | I: multi-host source package is plausible; a generated host realization may be needed even for MCP launch strings |
| Claude plugin components | D: optional host manifest, discovery defaults and component/marketplace precedence [RG-S34] | I: shared skill/server assets can be packaged separately; not a shared hook/permission ABI |
| MCP and Goose | D: protocol separates client/server; Goose documents extensions usable with other agents [RG-S19] [RG-S15] | I: one service implementation can have several client bindings; host filtering/auth/session behavior still varies |
| Cordis | D: [canonical host mechanism note](#cordis-mechanism-facts) | I: reusable capability core plus Cordis binding; service injection is not evidence the plugin runs in another harness |
| OpenCode V1 and V2 | D: [canonical migration note](#opencode-migration-facts) and CLI evidence [RG-S12] | I: separate host realizations; shared package/version alone does not remove porting |
| VS Code | D: main/browser entrypoints and UI/workspace placement declarations [RG-S24] | I: precedent for environment-specific implementations; these are VS Code environments, not arbitrary harness compatibility |

**I, R4:** The proposed multi-host package contains one canonical capability version, shared inert assets or business-logic source where appropriate, multiple digest-bound binding records, per-binding dependencies and loss records, and a conformance matrix. “Shared” means a measured byte/code/semantic component, not a claim all lifecycle state is global. Runtime instances and mutable data are separated by principal, goal/privacy compartment and binding revision unless an explicit sharing contract is admitted.

MCP wire version, package schema version, source plugin version, adapter API version, host executable version and canonical contract epoch are distinct. No `supports_mcp=true` or “Agent Plugins compatible” flag replaces this tuple.

**D:** the [canonical Tasks/MRTR facts](../protocol-edges/report.md#cancellation-and-asynchronous-tasks) define distinct continuation profiles. **I:** preserve task, logical-operation and wire-attempt identities, pending input and reservation lineage separately. RG-T09/T10 compare those profiles; a shared server cannot make the states interchangeable.

**Competing option:** separate native plugins with shared documentation/tests, or keep the complete upstream host behind a route adapter. **Falsifier:** the second and third host require duplicated business logic, divergent accepted outputs or additional authority such that total maintained cost exceeds separate native plugins. **Non-proof:** one package/many bindings establishes neither one process/many principals nor cross-host credential sharing.

## 8 R G Q08 Canonical versus adapter local boundary

Question ID: R-G.Q08

**I, R5:** Extend the canonical contract only with concepts needed to compare behavior and enforce authority. Keep syntax and implementation details local.

| Canonical and normative proposal | Adapter-local, pinned and inspectable |
|---|---|
| Identity/digest/provenance and explicit source attribution | Foreign package names, manifest paths, package metadata and acquisition locator |
| Contribution kind, required behavior, input/output contracts | Cordis service names, OpenCode domain/hook names, VS Code contribution keys |
| Semantic phase, ordering, failure, mutation and short-circuit obligations | Host callback names, event payload objects and disposal handles |
| Logical resources and current authority/privacy/egress/budget/publication limits | OS paths, transport arguments, environment-reference syntax, host policy encoding |
| Attempt/logical-operation identity, effect state, evidence and accounting | Wire IDs, stream framing, host event codes and resource counters |
| Loss and refusal taxonomy, qualification state and profile versions | Host-specific unknown fields, UI identifiers, compatibility switches |
| Availability/installation/activation separation and update fencing | Host load/reload commands, process layout and required runtime artifacts |
| Required credential visibility and independently enforced boundary | Auth-provider-specific handles and launch mechanism; never plaintext credentials in manifest |

A canonical semantic phase may be `before_effect_admission`; it must not be the literal string `tool.execute.before` simply because one host uses it. A source hook with broader or narrower coverage declares that difference. An extension namespace is not a back door for untyped capabilities: any extension that affects required behavior must declare its descriptor and profile requirement; unknown required descriptors block admission.

Use one contribution taxonomy with an extension registry, retaining the comprehensive existing families. A tool-only pilot does not turn memory, context, scheduling, research, agents, transport, UI, storage, availability or update capabilities into out-of-scope features.

**Competing option:** independently specified per-domain canonical schemas with lossless adapter maps, retaining the same comprehensive required behavior. **Negative controls:** embed every foreign concept in the core, or reduce the core to a lowest-common-denominator tool schema. **Falsifier:** required semantics can only be represented by canonical host names/opaque code, or the same canonical term means incompatible behavior across admitted bindings. **Non-proof:** a clean boundary does not select the language, serialization library or execution placement.

## 9 R G Q09 Provider free validation and cost model

Question ID: R-G.Q09

**Status: UNEXECUTED.** The following extends R-A's measurement model into a preregistrable, falsifiable local procedure. Detailed artifacts, expected records and stop rules are in `UNEXECUTED-local-test-handoffs.md`. It proposes future work; it authorizes none.

### Corpus and experimental unit

**I, R6:** Freeze eight synthetic semantic fixtures across six primary ecosystem profiles: Cordis, OpenCode V1, OpenCode V2, Goose external-MCP configuration, MCP 2026-07-28 and VS Code. This gives **48 proposed ecosystem-fixture assignments**, not 48 tests run. Add eight MCP 2025-11-25 compatibility assignments as a separately reported stratum; never count those as independent ecosystems. Builtin/platform Goose features receive explicit negative/unknown import cases within the corpus; no blanket external-MCP assumption.

Fixtures cover pure typed transform; bounded resource read/staged artifact; ordered interceptors; optional UI versus required approval UI; dependency/reload/cleanup; authority/privacy/egress/credential/budget denial; typed/multimodal result and evidence; version drift/recovery/revocation. Each has literal inputs, accepted output/trace, required semantics and approved optional losses. Deliberately unportable variants remain assigned and count as rejected/unsupported, not dropped from the denominator.

Unit of comparison is an ecosystem-fixture realization against the same canonical scenario set. For each assignment compare (A) source-shaped port using the proposed translation/profile and (B) an independent native realization from the same behavior specification. Add a one-way shim/generated-adapter comparator only where preregistered. The native baseline receives the same authority, evidence, test burden and dependency constraints; it cannot omit requirements to appear cheaper.

Static translation, semantic simulation and actual-host enforcement are different evidence levels. A synthetic descriptor pass is not an accepted runtime port. Provider-free host qualification, if later authorized, must prove no provider bootstrap/update/telemetry path is triggered. A host that cannot meet that precondition is unsupported for that experiment, not an excuse for a live call.

### Counted checklist and dependent variables

Each assignment has a fixed 16-item translation checklist: identity/provenance; version tuple; source discovery; contribution completeness; input schema; output/result schema; dependency binding; activation trigger; ordering/mutation; cleanup/settlement; capability/resource requests; privacy/egress; credential boundary; budget/accounting; evidence/refusal; round-trip/loss/update behavior.

For each item record applicable/not-applicable with a reason, direct/mechanical/annotation/none, attempted, passed, failed, unsupported or unverified. Report numerator and denominator separately for fields, contributions, required scenarios and assignments.

Primary conformance dependent variables:

- `critical_failure_any`: whether any authority/privacy/credential/billing/publication/evidence invariant fails
- `failed_required_obligations / applicable_required_obligations`, with both raw counts
- `accepted_equivalent`: independent acceptance of every required scenario plus only preapproved optional losses
- failure class and repair cycles, including failures found after the first apparent pass

Do not average one critical failure away with many syntax successes. Repeated invocations, multiple assertions for one requirement, and current/legacy variants are not independent sample units.

Secondary explanatory measurements preserve R-A: handwritten glue LOC, generated LOC, generator-maintenance LOC, foreign source reused, distinct adapter API touchpoints, semantic mapping-rule count, lifecycle translations, dependency closure size, and review/rework effort. LOC conventions and exclusions are frozen; one physical line and a complex one-line callback cannot be treated as equal semantic effort. These metrics are candidate predictors, not proof that less LOC means cheaper or safer.

### Total cost and denominators

`C_port = intake + mapping + implementation + review + conformance + rework + packaging/rights-evidence preparation + allocated shared-tooling cost + maintenance`

Use the same categories for native cost. Record human active minutes, elapsed delay and machine resource vector separately. No dollar conversion or assumed unpaid labor. Count unsuccessful assignments, blocker analysis and abandoned work. Shared translator construction/repair is charged once and allocated transparently across the actual accepted count; provide unamortized and amortized views at observed corpus size, not an imagined future plugin population.

Report total cost over all assigned ports, median/IQR per assignment, accepted-equivalent count over assigned count, and total incurred cost divided by accepted-equivalent count. If the accepted count is zero, that ratio is **undefined**, not zero; if required semantics are impossible under the bound, record no-port rather than invented finite effort. Also report cost per accepted required scenario so splitting one plugin into many nominal plugins cannot manufacture a saving.

For cross-host reuse, compare shared-core plus all bindings/reviews/maintenance with separate native implementations of the same host set. Report marginal cost of host 2 and 3 and total cost, rather than advertising a low marginal cost while hiding the first adapter/generator cost.

### Uncertainty and model validation

Current cost interval for every ecosystem: **U; nonnegative and unbounded above**, with an explicit no-port outcome. No finite hour bands or savings percentage are defensible now.

Before future execution, choose the confidence procedure, precision target, stop budget and minimum meaningful saving. Proposed analysis uses paired differences/ratios within assignment and a cluster-aware interval across independently implemented fixture families/porters. Report raw pairs and leave-one-family-out sensitivity; do not present a narrow bootstrap interval from many repeated assertions as independent evidence. Censored assignments retain incurred cost and status; completed-case and pessimistic sensitivity estimates both appear.

R-A's effort-band/LOC/surface model is validated only if frozen predictors forecast held-out fixture outcomes and effort better than a simple ecosystem-only or constant baseline. With 48 deliberately related assignments, an elaborate fitted model may be unjustified. Start with preregistered descriptive comparisons; if a model is fitted, use a small predeclared feature set, leave whole fixture families/porters out, and report calibration/error and critical-failure false negatives. A model that predicts low cost for security-breaking ports fails regardless of average fit.

Synthetic success establishes only behavior on the fixture domain. A later separately approved, license-reviewed natural-plugin census is needed for ecosystem population and real maintenance claims. “No corpus measured” remains explicit until then.

**Competing option:** complete bounded census including failed/abandoned work with the same critical outcomes and complete review/maintenance accounting. **Negative controls:** compare only glue LOC or successful ports, or use a single native baseline for every ecosystem. **Falsifier:** the full cost/failed-port accounting reverses the apparent saving, or structural predictors do not outperform the simple baseline out of sample. **Non-proof:** provider-free conformance does not measure model quality, subscription efficiency, live service legality or arbitrary real-world portability.

## 10 R G Q10 Cheapest credible paths and competitors

Question ID: R-G.Q10

Every “cheapest” entry is **I: a hypothesis**, with **U effort**. No route is selected or enabled.

| Ecosystem | Candidate path | Competing option | Decisive falsifier | What it does not prove |
|---|---|---|---|---|
| Cordis | Extract a bounded tool/service capability; retain output semantics; write a thin reviewed binding and explicit event/lifecycle sidecar | Keep whole source host behind an authorized route, native rewrite, or no port | Required behavior depends on ambient services/expressions or teardown semantics whose safe adaptation costs more than rewrite | Reusing Cordis architecture or license does not establish runtime containment |
| OpenCode V1 | Port tool/pure transformation core; mechanically map static metadata; explicitly reauthor host hooks | One-way shim in V1 host, native rewrite or no port | Hook/output/permission adaptation dominates total accepted cost or cannot preserve required phase | A small manifest change is not small implementation effort |
| OpenCode V2 | Bind stable contribution core to named domain APIs; separate CLI rendering; retain storage/lifecycle loss map | Full native plugin, upstream route, generated narrow adapter or no port | Source/host pin cannot be fixed, or transforms/session scope alter required behavior | V2's richer API does not establish stability or V1 compatibility |
| Goose external MCP | Reuse the independently qualified server; translate only launch/transport/filter configuration and evidence envelope | Native capability or a Goose-specific shim | Server needs wider auth/egress, filter interpretation widens exposure, or management overhead exceeds rewrite | Builtin/platform features do not automatically become portable server packages |
| MCP | Preserve typed RPC/service boundary under exact current/legacy profile; bind identity/authority/evidence outside protocol | Native rewrite or direct host-specific callable API | Required result/elicitation/state/authority semantics cannot pass with equal bounds or total cost is higher | Wire compatibility is not deployment, permissions, credentials or billing equivalence |
| VS Code | Reuse legally eligible declarative assets or extract protocol/business logic; rewrite host presentation binding | Native implementation, authorized original-host route, or no port | Required workbench API/UI/runtime rights or behavior cannot be preserved economically | Code-OSS's root license does not clear acquired extension packages or assets |

These are applications of R2/R4/R6, not separate technology choices. A no-port finding is admissible research output and an input to Owner delivery decisions; it cannot silently change D-019.

## 11 R G Q11 Real mechanisms and speculative economies

Question ID: R-G.Q11

| Economy claim | Evidence now | Required experiment and falsifier | Non-proof |
|---|---|---|---|
| Shared manifest reduces packaging duplication | D: [common-package fact cell](#agent-plugins-facts); I: shared parsing is a proposed optimization | Compare total authoring/review/update work at same accepted behavior; falsified if host overlays/repairs erase the saving | No common permission or lifecycle contract |
| Shared contribution taxonomy reduces repeated interpretation | I: canonical semantics could reuse validators and oracles | Count unique mappings and accepted cost; falsified if opaque host exceptions dominate or cost is no lower | Taxonomy coverage does not make contributions executable |
| Generated adapters remove routine glue | I: exact syntax transforms are mechanically expressible | Include generator development, generated defects and drift repair; falsified if break-even exceeds measured corpus or native is cheaper | Generation is not semantic or security verification |
| One server supports multiple hosts | D: MCP and Goose expose this mechanism [RG-S19] [RG-S15] | Same synthetic service, distinct profiles, equal required semantics; falsified by any unrepresentable host requirement or higher total cost | No shared credential rights or common trusted principal |
| One source package serves several agent products | D: [host-format fact cell](#cursor-plugin-facts), with extension rules [RG-S31] | Placeholder/transport/discovery/loss fixtures per host; falsified if advertised common package needs incompatible core mutations | Packaging portability does not prove the same model behavior |
| Community ports reduce comprehensive delivery effort | U: no local acceptance/maintenance population | Track proposed, started, abandoned and accepted ports plus maintainer review burden; falsified if equal-quality acceptance throughput/cost is worse than native work | Community interest, downloads or stars do not count as engineering delivered |

The [package-profile](#cursor-plugin-facts) and [migration](#opencode-migration-facts) findings sharpen R-A with generator stress cases; Recursion's economic gains remain U.

## 12 R G Q12 Falsifiers and recommendation register

Question ID: R-G.Q12

### Decisive falsifiers of the porting hypothesis

1. **Cost:** on a preregistered required-behavior stratum, paired total accepted port cost exceeds native rewrite, including shared tooling, review, failed attempts and maintenance. Equality does not support a claim of cheaper ports. An uncertainty interval crossing the decision threshold means inconclusive, not success.
2. **Clean import:** no ecosystem in the declared representative corpus has an independently accepted full realization of its assigned required scenarios. Zero static-parser failures is not the opposite of this falsifier. A synthetic zero cannot prove there are no portable plugins anywhere; it falsifies the evaluated claim/domain.
3. **Authority:** any translated capability/grant admits an operation outside constitutional, goal, parent or current policy bounds; any hook bypasses final enforcement; any source default enables an effect without admission.
4. **Privacy or credentials:** source data/headers/env/placeholder expansion reaches an unauthorized recipient or credential boundary, including logs/IPC, or a strong non-access claim rests only on policy.
5. **Evidence or accounting:** source completion becomes independent acceptance, cancelled/disconnected becomes settled, unknown usage becomes zero, or an identity/profile change keeps stale qualification.
6. **Behavior:** required timing/order/schema/output/resource/subscription semantics are lost or represented as optional merely to count success.
7. **Reuse economics:** adding hosts duplicates enough implementation or maintenance that shared-core total cost is no lower than separate native realizations; generator break-even relies on an unobserved future population.
8. **Maintenance:** a preregistered upstream-breaking-change fixture invalidates the claimed effort saving or causes stale mappings to remain active.

One critical security/evidence failure rejects the candidate; it is not just an extra labor hour. Findings may falsify a proposed adapter while leaving another path open. Broader product changes remain Lucas's decision.

### Recommendations are proposals only

| ID | Proposal | Competitor | Falsifier | Non-proof | Negative control (not an admissible rival) |
|---|---|---|---|---|---|
| R1 | Data-only intake and detached source/profile/translation records; separate admission | Metadata-separated native activation or full-host emulation after inert discovery and the same admission/grant gates | Required discovery needs effects or candidate widens authority; full accepted cost worse | Not a sandbox or loader implementation | Effectful native loading during discovery |
| R2 | Compare explicit MCP slice with Cordis rich-semantics stress case, then separate V1/V2 and editor slices | Cordis-only or native-first corpus | Lower accepted coverage or higher matched cost than alternative | No vendor choice, scope deferral or validated leverage ranking | None added; existing rival retained |
| R3 | Per-contribution explicit loss and multi-axis state, required loss fails closed | Full source-host emulation with inert discovery, explicit loss and identical admission gates | A required loss is hidden or an incompatible contribution executes | No substitute equivalence or legal clearance | Silent omission |
| R4 | Shared capability/assets with per-host digest-bound realizations | Separate native plugins or source-host route | Total/marginal accepted cost loses or required outputs/authority diverge | No universal binary, shared credentials or shared mutable instance | None added; existing rival retained |
| R5 | Canonical semantic obligations; host syntax and APIs remain adapter-local | Independently specified per-domain canonical schemas with lossless adapter maps versus shared semantic taxonomy; same required comprehensive behavior | Host-specific escape hatches become needed for authority/required behavior | No language/store/runtime selection | Universal host API in core or minimal tool-only core |
| R6 | Paired provider-free corpus, critical conformance outcomes, total-cost/maintenance accounting | Complete bounded census including failed/abandoned work versus paired port/rewrite cohort; same critical outcomes, review and maintenance accounting | Savings vanish under complete accounting or predictive model fails held-out families | No measured savings, real-plugin generalization or live-route qualification | LOC-only/success-only comparison |

## Completion gate

| Gate | Research delivery status | Evidence and remaining limit |
|---|---|---|
| Every named ecosystem has tagged manifest/discovery/lifecycle/permission/contribution assessment | Complete in this authored report | Section 1; source pins/unknowns explicit; no runtime assessment claimed |
| Concrete translation onto R-A manifest/capability graph, non-widening boundaries | Complete as proposal | Sections 2 and 5; enforcement remains UNEXECUTED |
| Explicit unportable cases and loss representation | Complete as proposal | Sections 4 and 6; no hidden omission |
| Cross-harness reuse assessed with evidence | Complete as research | Section 7/11; mechanism distinguished from unmeasured savings |
| Provider-free measurable cost approach, denominators, intervals and failures | Complete as UNEXECUTED design | Section 9 and detailed handoffs; no invented cost measurement |
| Porting-cheap hypothesis with decisive falsifiers | Complete | Section 12; D-033 remains unproven |
| Every recommendation has competitor, falsifier and non-proof | Complete | R1–R6 register and ecosystem path table |
| Protected paths untouched and privacy/secret review | Source remained read-only; artifact review recorded separately | No repository writes or private public queries; bounded artifact textual scan found no selected credential patterns/private absolute paths; independent or exhaustive verification is not implied |

Independent acceptance is pending. The report's self-check is a coverage record, not an independent PASS. `question-coverage.json` maps R-G.Q01–R-G.Q12 to answers, sources, handoff IDs and unresolved limitations. `source-register.json` and `source-register.md` provide clean bibliographic records and capture limits. No DOCX is created in this lane.

## Source links

Source references below are primary public material. All were accessed 2026-10-02. See the register for document/revision pins, failed immutable retrievals and the distinction between capture hashes and executable versions.

[RG-S01]: https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/README.md "DeepSeek Harness README — commit 639ed015397290b3745d163aafe02ffee4aa3f84; developer preview; accessed 2026-10-02"

[RG-S02]: https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/cordis-primer.md "DeepSeek Cordis primer — commit 639ed015397290b3745d163aafe02ffee4aa3f84; accessed 2026-10-02"

[RG-S03]: https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/subsystems/tools.md "DeepSeek tool subsystem — commit 639ed015397290b3745d163aafe02ffee4aa3f84; accessed 2026-10-02"

[RG-S04]: https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/SAFETY.md "DeepSeek safety notice — commit 639ed015397290b3745d163aafe02ffee4aa3f84; accessed 2026-10-02"

[RG-S05]: https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/LICENSE "DeepSeek license — commit 639ed015397290b3745d163aafe02ffee4aa3f84; accessed 2026-10-02"

[RG-S06]: https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/THIRD_PARTY_NOTICES.md "DeepSeek third party notices — commit 639ed015397290b3745d163aafe02ffee4aa3f84; accessed 2026-10-02"

[RG-S07]: https://opencode.ai/docs/plugins/ "OpenCode V1 plugins — V1 docs; displayed update 2026-10-02; exact executable unknown; accessed 2026-10-02"

[RG-S08]: https://opencode.ai/docs/permissions/ "OpenCode V1 permissions — V1 docs; displayed update 2026-10-02; behavior note v1.1.1; accessed 2026-10-02"

[RG-S09]: https://opencode.ai/v2/docs/build/plugins/migrate-v1 "OpenCode V1 to V2 migration — V2 documentation; exact executable unknown; accessed 2026-10-02"

[RG-S10]: https://opencode.ai/v2/docs/build/plugins "OpenCode V2 plugin API — V2 documentation; exact executable unknown; accessed 2026-10-02"

[RG-S11]: https://opencode.ai/v2/docs/plugins "OpenCode V2 configuration — V2 documentation; exact executable unknown; accessed 2026-10-02"

[RG-S12]: https://opencode.ai/v2/docs/build/plugins/cli "OpenCode V2 CLI plugins — V2 CLI documentation; exact executable unknown; accessed 2026-10-02"

[RG-S13]: https://opencode.ai/docs/ecosystem "OpenCode ecosystem directory — mutable V1 directory; retrieved 2026-10-02; accessed 2026-10-02"

[RG-S14]: https://github.com/anomalyco/opencode/blob/dev/LICENSE "OpenCode root license — mutable dev branch; exact commit unknown; accessed 2026-10-02"

[RG-S15]: https://goose-docs.ai/docs/getting-started/using-extensions/ "Goose using extensions — mutable current docs; executable and commit correspondence unknown; accessed 2026-10-02"

[RG-S16]: https://goose-docs.ai/docs/guides/config-files/ "Goose configuration files — mutable current docs; executable and commit correspondence unknown; accessed 2026-10-02"

[RG-S17]: https://goose-docs.ai/docs/guides/managing-tools/goose-permissions/ "Goose permission modes — mutable current docs; executable and commit correspondence unknown; accessed 2026-10-02"

[RG-S18]: https://github.com/aaif-goose/goose/blob/main/LICENSE "Goose license — mutable main; exact commit unknown; accessed 2026-10-02"

[RG-S19]: https://modelcontextprotocol.io/specification/2026-07-28 "MCP current specification — protocol 2026-07-28; accessed 2026-10-02"

[RG-S20]: https://modelcontextprotocol.io/specification/2026-07-28/server/discover "MCP current discovery — protocol 2026-07-28; accessed 2026-10-02"

[RG-S21]: https://modelcontextprotocol.io/specification/2026-07-28/server/tools "MCP current tools — protocol 2026-07-28; accessed 2026-10-02"

[RG-S22]: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle "MCP legacy lifecycle — compatibility protocol 2025-11-25; accessed 2026-10-02"

[RG-S23]: https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization "MCP current authorization — protocol 2026-07-28; accessed 2026-10-02"

[RG-S24]: https://code.visualstudio.com/api/references/extension-manifest "VS Code extension manifest — mutable API docs; exact executable unknown; accessed 2026-10-02"

[RG-S25]: https://code.visualstudio.com/api/references/activation-events "VS Code activation events — displayed documentation date 2026-09-30; feature minima 1.74.0 and 1.76.0; accessed 2026-10-02"

[RG-S26]: https://code.visualstudio.com/api/extension-guides/workspace-trust "VS Code workspace trust — displayed documentation date 2026-09-30; accessed 2026-10-02"

[RG-S27]: https://code.visualstudio.com/api/references/contribution-points "VS Code contribution points — mutable API docs; exact executable unknown; accessed 2026-10-02"

[RG-S28]: https://code.visualstudio.com/docs/supporting/faq "VS Code FAQ — mutable FAQ; retrieved 2026-10-02; accessed 2026-10-02"

[RG-S29]: https://agent-plugins.org/specification "Agent Plugins specification — published specification 1.0.0; accessed 2026-10-02"

[RG-S30]: https://agent-plugins.org/client-implementers/mcp-runtime "Agent Plugins MCP runtime — Agent Plugins 1.0.0 companion docs; accessed 2026-10-02"

[RG-S31]: https://agent-plugins.org/plugin-authors/client-extensions "Agent Plugins client extensions — Agent Plugins 1.0.0 companion docs; accessed 2026-10-02"

[RG-S32]: https://developers.openai.com/plugins/build/plugins "OpenAI package your plugin — mutable public docs; Agent Plugins 1.0.0 schema in examples; accessed 2026-10-02"

[RG-S33]: https://cursor.com/docs/plugins "Cursor plugins — mutable public docs; Agent Plugins 1.0.0 schema in examples; accessed 2026-10-02"

[RG-S34]: https://code.claude.com/docs/en/plugins-reference "Claude Code plugin manifest reference — mutable docs; specific MCP validation minimum v2.1.281 only; accessed 2026-10-02"

[RG-S35]: https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning "MCP versioning overview — current documented protocol 2026-07-28; accessed 2026-10-02"

[RG-S36]: https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning "MCP versioning and compatibility — protocol 2026-07-28; accessed 2026-10-02"

[RG-S37]: https://tasks.extensions.modelcontextprotocol.io/specification/2026-07-28/tasks "MCP Tasks extension — Tasks extension revision 2026-07-28; per-request opt-in; accessed 2026-10-02"

[RG-S38]: https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr "MCP multi round-trip requests — protocol 2026-07-28; accessed 2026-10-02"

[RG-S39]: https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio "MCP stdio binding — protocol 2026-07-28 stdio profile; accessed 2026-10-02"

Comparison qualification: all alternatives in the recommendation ledger are original design inferences with identical accepted capabilities and safety floors; native loading or full-host emulation is admissible only after inert discovery and separate activation admission. No runtime or cost result is claimed.

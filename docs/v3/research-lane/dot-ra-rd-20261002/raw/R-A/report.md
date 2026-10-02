# R-A: Plugin portability and capability contract

Decision evidence pack | 2 October 2026 | Research and contract design only

## Executive finding

Recursion should expose a comprehensive opt-in capability surface around a small, non-optional authority kernel. A shared manifest can remove packaging repetition; it cannot make unlike host semantics or permissions equivalent. The cheapest credible portability floor is reusable skills and explicitly profiled tool interfaces, with host-specific adapters for lifecycle, hooks, UI, state and permissions. The full capability taxonomy remains in scope. This does not narrow D-019's build commitment or turn optional capabilities into defaults.

Three newly verified facts materially affect the design:

- OpenCode V1 and V2 are different plugin implementation contracts. Automatic configuration migration does not make V1 plugin code run in V2. [S04]
- MCP's current documented protocol is 2026-07-28, with per-request versioning and discovery. The 2025-11-25 handshake contract remains a separate compatibility profile; it is not the current protocol. [S10-S13]
- Agent Plugins 1.0.0 provides a published package floor for skills and MCP configurations. OpenAI and Cursor document support, alongside their own extensions and compatibility formats. This is packaging interoperability, not a common authority model. [S17-S20, S24]

Porting savings are unmeasured. No effort hours, speedup, accepted-port rate, disabled-path test or runtime conformance result is claimed. The contract below is a proposal, not an accepted implementation or an upstream certification. Its decisive test is whether ports preserve useful behavior and authority at lower total accepted-port cost than independently implemented alternatives, with failed ports and maintenance included.

Lucas remains final Owner. The Owner's current clarification supersedes the brief's Hermes-executive sentence: Hermes is not the executive control plane; Recursion is a harness and a harness orchestrator that can delegate model requests through other harnesses. No substitute executive authority is inferred. Independent review, not an implementer's own PASS, remains necessary for acceptance. D-018, D-019 and Apache-2.0 direction D-026 are preserved; distribution conclusions belong to R-C and counsel.

## Evidence basis and limits

Labels used throughout: D = source-documented; O = locally observed artifact fact; I = inference or proposed design; U = unknown/unverified. D does not mean an implementation was exercised. All matrix cells carry one of these labels. Proposals use normative words MUST and MUST NOT only to specify the proposed contract, not to claim those requirements exist upstream.

The project basis is the supplied R-A handoff and README, plus the current Owner correction. Linked constitution, decision register and gap files were not supplied as necessary inputs and were not recovered from historical checkouts. Exact existing GoalSpec field names and constitutional APIs therefore remain U; the proposed semantic boundaries can be reviewed without inventing them.

Public source pins in Appendix A comprise exact URL, public-document revision where available, access date and a digest ledger of the captured retrieval. A captured document digest is a reproducibility pin, not an upstream source commit or installed-binary digest. Mutable documentation can change even under a versioned path. No exact executable release was qualified. Fresh exact public source/license pins are available in the accompanying R-C evidence. Public documentation captures remain separate from those source trees; no unverified correspondence to an installed release is implied. Sources with only indexed body retrieval are marked explicitly. Before implementation, each candidate profile needs a full source/artifact pin and the matching license evidence.

## 1. Extension-model matrix: units, discovery and lifecycle

This answers Q1. OpenAI, Anthropic and Cursor are families of surfaces, not single interchangeable plugin ABIs. The evaluated profiles below are intentionally explicit; unknown proprietary internals remain unknown.

| Ecosystem/profile | Extension unit | Discovery and activation | Lifecycle | Capability declarations and contribution points |
|---|---|---|---|---|
| DeepSeek Harness / vendored Cordis | D: service/function plugin with apply and optional inject [S01] | D: configuration loader plus injected-service dependencies; mount waits for dependencies [S01] | D: scoped registration effects and disposers; service/event dispatch semantics matter [S01] | D: service keys, typed events, tools, prompt sections, model/adaptor/provider registrations [S01]; I: no portable descriptor for arbitrary code |
| OpenCode V1 | D: module exporting plugin functions that return hook objects [S03] | D: project/global plugin directories and configured packages; startup auto-loading and package installation [S03] | D: initialization and sequential hook execution [S03]; D: migration guide describes returned dispose hook [S04] | D: hooks, custom tools, SDK access, shell/environment and compaction integration [S03] |
| OpenCode V2 server plugin | D: stable id plus setup(ctx) definition [S05] | D: configured packages/directories and local discovery; separate CLI-plugin configuration [S06] | D: setup may return cleanup; registrations dispose; transforms rebuild in order [S05] | D: domain context, tools, events, transforms, agents, providers, integrations and storage [S05]; I: CLI UI remains another profile |
| Goose extensions | D: built-in/platform extensions and configured external MCP endpoints/processes [S07-S08] | D: config/extension manager and enabled flags; stdio or Streamable HTTP [S08] | D: enabled extension tools become available; config edits may need restart [S07-S08]; U: universal teardown guarantee | D: extension config and MCP tool schemas; tool filtering [S08]; I: built-in services are not automatically external MCP packages |
| MCP current 2026-07-28 | D: protocol server, not installable package [S10-S12] | D: endpoint/process configuration is host-local; server/discover is required server RPC, optional client call [S12] | D: self-contained requests with version/capability metadata; transport lifetime is separate [S10-S13] | D: tools/resources/prompts; negotiated optional extensions [S11]; I: implementation permissions are outside the wire capability assertion |
| MCP compatibility 2025-11-25 | D: protocol server [S14] | D: initialize and initialized handshake [S14] | D: initialization, operation, transport shutdown; timeout/cancellation [S14] | D: client/server capabilities including sampling, roots, elicitation and tasks [S14]; I: this shape must not be silently carried into current core |
| VS Code extensions | D: package.json extension with main/browser entry points or declarative contributions [S15] | D: extension installation and activation events; some contribution activation is implicit in newer hosts [S15-S16] | D: event-triggered activation; extension host owns execution [S16]; U: arbitrary extension cleanup correctness | D: contributes, commands, languages, themes, workbench/UI and programmatic APIs [S15] |
| OpenAI portable / Codex-compatible plugins | D: Agent Plugins root plugin.json; OpenAI extension namespace; compatibility .codex-plugin/plugin.json [S17] | D: universal directory plus local/repo marketplaces with surface-specific availability [S17] | D: local development may require restart; hooks are execution-surface specific [S17-S18]; U: universal teardown API | D: skills, MCP connections; OpenAI-specific hooks, presentation and registered-server mappings [S17] |
| Anthropic Claude Code plugins | D: component directory, optional .claude-plugin/plugin.json [S21-S22] | D: marketplace or explicit local folder; default component discovery [S21] | D: enabled MCP servers and event hooks; components incur context/process costs [S21] | D: skills, agents, commands, hooks/mods, MCP/LSP, output styles, workflows, channels; experimental themes/monitors/evals [S22] |
| Anthropic desktop MCP bundles | D: .mcpb ZIP with manifest.json and local server files [S23] | D: host installation and configuration UI [S23] | D: bundle launches local MCP server through host [S23]; U: cross-host disposal and isolation equivalence | D: packaged MCP server configuration [S23]; I: bundle format and protocol version are distinct axes |
| Cursor Agent Plugins / Cursor Plugins | D: root plugin.json versus .cursor-plugin/plugin.json [S24] | D: marketplace/local discovery and component folders or explicit paths [S24-S25] | D: reload discovers local changes; MCP can be toggled [S24]; U: general all-component quiescence proof | D: common skills/MCP; Cursor-specific rules, agents, commands, hooks and variables [S24-S25] |

Goose's current config source lists builtin, platform, stdio and streamable_http, and says SSE is unsupported. This report does not import an older SSE compatibility claim from search snippets or older forks. [S08]

## 2. Permission and compatibility matrix

This answers Q1-Q3. In particular, a dependency injection key, an MCP capability and a host permission allowlist are not three names for the same security primitive.

| Profile | Documented permission surface | Version/compatibility contract | Honest unknowns / portability classification |
|---|---|---|---|
| DeepSeek/Cordis | D: safety notice says code/plugins may access available files, processes, network and credentials; controls are not isolation guarantees [S02] | D: developer-preview README warns of breaking changes [S00]; U: supported API epoch/deprecation window | I: service/event adaptation is plausible; service injection alone is not a least-authority grant. U: independently enforced per-plugin isolation |
| OpenCode V1 | D: tool permissions with allow/ask/deny rules [S03P]; I: these do not establish containment of arbitrary plugin module code | D: V1 plugin package/API names differ from V2; V1 implementations do not run in V2 [S04] | U: comprehensive backwards-compatibility/deprecation guarantee. I: manifest-only translation insufficient for behavioral hooks |
| OpenCode V2 | D: plugin context can inspect/reply to permissions and change session rules [S05]; D: two built-ins cannot be disabled through ordinary plugin removal [S06] | D: target compatible plugin package with host release; explicit implementation migration [S04]; U: universal stable ABI | I: broad context access needs an attenuating adapter; upstream last-match behavior must not become Recursion authority precedence |
| Goose | D: permission modes and granular permissions; some read/write classification is best-effort and model interpreted [S09] | D: config compatibility/migration is documented for particular fields [S08]; U: stable extension ABI and all-host protocol support window | I: external MCP reuse is plausible; model-based approval classification cannot be a deterministic conformance oracle |
| MCP current | D: protocol does not itself enforce host trust principles [S11]; HTTP authorization is separate [S13A] | D: 2026-07-28 request version, UnsupportedProtocolVersionError and optional discovery [S10-S12]; D: dated incompatible revisions and a deprecation policy [S10] | I: strongest shared tool wire shape; not a filesystem/process sandbox, package installer or universal permission grant |
| MCP legacy | D: optional HTTP authorization; stdio credentials are environment-based in that profile [S14A] | D: initialize negotiation and disconnect on unsupported server version [S14] | I: legacy adapter requires explicit profile. U: support in any particular current host absent a host pin |
| VS Code | D: untrusted/virtual workspace declarations and Workspace Trust [S15,S16T] | D: extension semver and engines.vscode range [S15]; D: stable/proposed API distinction and host compatibility guidance [S16P] | I: rich manifest plus host API, not common negotiated least-authority. U: per-extension boundary equivalent to this proposal |
| OpenAI | D: host-specific hook support and conversion limitations [S18]; U: single plugin-level authority negotiation applicable to all surfaces | D: Agent Plugins 1.0.0 schema plus compatibility overlay precedence [S17,S20]; U: all-surface deprecation SLA | I: common package subset; hooks, registered connections and ordinary Chat behavior require separate profiles |
| Claude Code | D: allow/ask/deny and managed permission rules [S22P]; D: hooks can participate in decisions [S22H] | D: manifest $schema is editor metadata, ignored on load; version is a string, not semver-enforced; feature minimum versions vary [S22] | I: component packaging is shared in shape, not identical semantics; U: all-component portable schema epoch/deprecation SLA |
| Anthropic MCPB | D: host controls local server installation/configuration [S23]; U: common per-bundle least-authority enforcement | D: bundle manifest/spec separate from MCP wire protocol [S23]; U: supported-version range in each host | I: reusable server payload; packaging portability does not establish runtime or credential portability |
| Cursor | D: IDE permission files/admin precedence; CLI permission system is explicitly separate [S26] | D: Agent Plugins 1.0.0 support plus Cursor-specific manifest [S24-S25]; U: host API/deprecation SLA | D: documented PLUGIN_ROOT/PLUGIN_DATA expansion divergence [S24]; I: even a declared standard needs implementation-profile qualification |

### Common shape and nonportable glue

I: There are three overlapping shapes, not one universal extension model:

1. Package discovery: identity + static component paths, exemplified by Agent Plugins, provider plugin bundles and VS Code manifests
2. Callable capability interface: typed arguments/results and protocol discovery, strongest in MCP and tool APIs
3. In-host behavior modification: event order, short-circuit hooks, mutable registries, storage, auth integration and UI APIs, prominent in Cordis, OpenCode and editor extensions

None of the reviewed sources establishes the complete common combination of portable manifest, typed contribution points and uniformly negotiated least-authority grants. MCP negotiates feature support, not all authorization. VS Code workspace declarations describe supported environments, not a per-plugin OS capability token. Cordis injection manages service dependencies, not every ambient process power. Provider plugin metadata is not authorization. These distinctions are inferred from the separate documented mechanisms, not proofs of missing controls in all upstream implementations.

I: Preserve native behavior behind a RouteProfile or adapter when host semantics are essential. Translate data/skills/tools where equivalent semantics can be specified. Refuse an unsupported required capability rather than flattening it into a prompt. Competing option: a universal host emulator. Falsifier: a fixed representative corpus requires less total effort and preserves more behavior through that emulator without authority widening. Limit: this comparison does not endorse any runtime.

## 3. Proposed manifest and record family

This answers Q4. The proposal is a language-independent data contract; JSON examples are an interchange illustration, not a runtime or package-manager choice. The full field contract and illustrative instance are also supplied in proposed-contract.json.

### Record ownership

| Record | Authoritative writer | Function |
|---|---|---|
| PluginManifest | Plugin author; untrusted until validated | Identity, contributions and requested bounds; never self-authorizes |
| InstallationRecord | Trusted host administration | Exact artifact identity, explicitly enabled profiles, no secret values |
| AuthorityGrant | Non-optional kernel acting within Owner/GoalSpec authority | Issued, attenuated capability set, epochs, expiry, revocation and budget reservations |
| RouteProfile | Independently reviewed profile record | Exact host/protocol/API pins, capability assertions, limitations and qualification state |
| CapabilityDescriptor | Contract registry | Type, input/output semantics, effect class, lifecycle obligations and refusal conditions |
| Invocation/EvidenceItem | Kernel observation plus attributed adapter/plugin claims | WorkUnit/Attempt identifiers, effect/accounting observations and output provenance |

I: PluginManifest MUST identify its admission contract, but MUST NOT contain an effective grant or a host-populated grant reference. The immutable author manifest is never mutated at admission. InstallationRecord is a detached envelope that binds the digest of exact manifest bytes, a separately defined package payload digest, and grant_ref. AuthorityGrant binds those digests and the goal/profile/epoch. An author's inline granted-capabilities assertion is rejected as grant injection. Request/grant coverage is provided by this record family, without making author metadata a security decision.

### Minimal mandatory manifest fields

| Field | Required meaning and validation |
|---|---|
| schema_epoch; contract_revision | Recognized major semantic epoch and revision; validate from pinned local schema, no schema-fetch side effect |
| identity | Namespaced stable id, author-provided version, payload digest and source pin; id alone never identifies executable bytes |
| compatibility | Required canonical contract range; one or more profile references with upstream protocol/API versions; unknown must remain explicit |
| contributions[] | Stable local id, kind, descriptor revision, input/output schema references, implementation binding reference and required/optional status |
| requires[] | Exact capability requests, resource selectors, allowed operations, effect classes, conditions and purpose; no implicit wildcard |
| admission_contract_ref | Recognized contract identifier for detached InstallationRecord/AuthorityGrant; it contains no grant or approval |
| attenuation | Delegation allowed/forbidden, maximum depth and child scope rules; always constrained by parent grant |
| privacy | Data labels accepted/emitted, compartment/purpose constraints, allowed recipient classes or exact recipients, retention and evidence redaction |
| bounds | Separate execution, billing and egress limits with units, windows and reservation/unknown policies; zero and unknown have different meanings |
| evidence_contract | Required output schema, observation fields, provenance, completion/acceptance separation and verifier policy reference |
| dependencies[] | Required or optional plugin/capability dependencies, compatible version ranges, no automatic authority union or activation |
| extensions | Opaque namespaced adapter data; cannot override canonical identity, authority, privacy, accounting or effects |

Digest basis: the author payload digest covers an explicit inventory of package payload bytes excluding the author manifest and every detached installation/grant/evidence record. The inventory identifies each normalized relative path and byte digest; path normalization, ordering and inventory encoding are contract-versioned before implementation. The detached envelope separately hashes the exact author-manifest bytes, so neither hash is self-referential. A host verifies author payload claims before activation. The illustrative fixture digest covers only its explicit description text, not an executable package. Schema checks alone do not validate these semantic/hash rules.

I: enabled is an InstallationRecord state, not an author's default permission. Absent installation consent is disabled. Profiles can group all requested capabilities for a feature but do not enable themselves or their dependencies. Imported upstream defaultEnabled, auto-discovery and marketplace defaults are recorded as source semantics and are not honored as Recursion authorization.

I: Avoid embedding operating-system paths, environment maps, credential fields or host SDK objects in canonical contribution definitions. They belong in a pinned implementation binding/profile with a resource-mapping proof. A resource such as goal://fixture/input is an opaque logical handle; it is not a fetchable URI. A profile can map it to a real host path only under an issued grant. Unknown mappings stop admission.

### Comprehensive contribution taxonomy, opt-in delivery

I: Freeze the taxonomy's extension mechanism early, not every future implementation schema. Proposed families cover tools; skills/prompts/references; agents and execution loops; native/upstream model execution routes; context/compaction/memory; storage and artifact services; planning and scheduling; bounded autonomous research; channels and terminal/UI presentation; environment/sandbox bindings; checkpoints/recovery and availability takeover; diagnostics, evaluation and accounting; and edition/profile bundles. Each family has typed descriptors and specific effect requirements. A graphical UI remains optional.

The kernel's admission, grant issuance/attenuation, deny enforcement, revocation epochs, effect authorization/settlement, minimum accounting and independent-acceptance boundary cannot be disabled by a plugin or profile. Optional plugins may provide richer policy proposals, meters, stores or schedulers, but removing them cannot remove constitutional checks or make unknown outcomes accepted. The kernel need not implement every feature to remain the authority boundary.

Competing options: adopt Agent Plugins unchanged as the entire contract; or define a larger universal host ABI. Falsifiers: unchanged Agent Plugins expresses all required authority/evidence/disabled semantics without undocumented host conventions; or the larger ABI demonstrably lowers accepted-port cost without binding the kernel to a host. Limits: this taxonomy does not pick a language, store, runtime, package manager, sandbox or vendor and does not show actual port feasibility.

## 4. Capability graph and non-widening rules

This answers Q5-Q6. I: The graph is a typed directed graph with separate dependency and authority edges. Cyclic service dependency resolution must never create an authority cycle.

Nodes: constitutional boundary; GoalSpec; authorized principal; WorkUnit/Attempt; PluginManifest artifact; installed instance; contribution; logical resource; RouteProfile; AuthorityGrant; privacy label/compartment; budget reservation; effect; EvidenceItem. A node's id does not confer authority.

Edges: declares (manifest to contribution); requires (contribution to capability); maps-to (canonical capability to adapter operation); depends-on (lifecycle dependency); attenuates-from (child to parent grant); permits (grant to operation/resource/conditions); consumes (attempt to reservation); produces (attempt to evidence/effect); revoked-by (grant epoch to revocation). No dependency or data-flow edge is a permission edge.

### Normative attenuation

I: An effective invocation grant is the intersection of the constitutional ceiling, GoalSpec scope, current parent AuthorityGrant, explicit installation/profile permissions, manifest request, route enforcement capability and current operation-specific approval. Intersection means semantic containment, not text-set comparison. If containment is undecidable or a dimension has unknown enforcement, the required operation is refused.

1. Operations/resources: child allowed operation-resource pairs MUST be subsets. Canonicalize resources before comparison, including case, symlinks/reparse points, redirects and cross-host mappings. A denied subresource cannot be restored by a broader allow
2. Privacy: child cannot receive higher-classified data, additional compartments, broader purposes/recipients, longer retention or new declassification power. Labels are a product of class, compartments and purpose; an unknown label is not public
3. Egress: destination, method, payload class and maximum bytes are intersected. DNS, redirect and IPC pathways count; a network allowlist does not authorize sending all data to an allowed domain
4. Credentials: route delegation may refer to an externally owned authenticated executor as an opaque handle; plugins cannot read, copy, translate or broker its credential. Secret visibility remains none unless a separate, lawful and explicitly authorized design applies; this report grants none
5. Billing/resources: aggregate child reservations cannot exceed unreserved parent budgets in the same units/window. An unknown price/token count cannot become zero. An unenforceable mandatory cap means unsupported route, not best effort
6. Publication and irreversible effects: require separate exact target/purpose authority. Tool success or parent approval of research does not authorize publish, merge, payment, account changes or credential operations
7. Delegation: maximum depth, expiry, context slice and remaining budget only decrease. No union of sibling grants, recursive laundering or cached grant reuse across goals
8. Epoch/revocation: grant binds goal, plugin digest, profile digest and authority epoch. Check immediately before effect admission; revocation fences new effects. Reauthorization creates a new grant rather than mutating an old decision silently

### Conflict, precedence and lifecycle

I: Deny wins over allow; narrower valid bounds win over broader bounds; required missing/unsupported capability fails admission; optional missing capability remains disabled with a recorded degradation. Two contributions claiming the same canonical id cause an explicit conflict unless an Owner-approved profile specifies composition. Hook ordering must be declared and deterministic. If semantics require incompatible ordering, refuse rather than rely on whichever plugin loads last. An observer cannot mutate a decision; a policy plugin may propose restriction but cannot manufacture a permit. No plugin can lower the independent acceptance standard.

Lifecycle: discovered-as-data → validated → disabled or admitted → activated → draining → quiescent/disabled, with failed/quarantined exits. Grant issuance precedes code import/startup. A required dependency missing or disabled blocks activation; it is not auto-enabled. Quiescent is not equivalent to rollback: external effects already performed need settlement evidence and may be irreversible. A hanging unload becomes containment failure, not successfully disabled.

### Freeze early versus adapter-local

Normative early surface: record identity/digest binding; schema epochs; request/grant split; absent/disabled defaults; attenuation; logical resource selectors; required/optional semantics; refusal codes; deterministic composition; revocation; effect identity/idempotency contract; output/evidence/accounting semantics; privacy/egress/budget unknown behavior; profile qualification states. These must have change-controlled compatibility rules and test vectors before porters depend on them.

Adapter-local surface: package layout importers, upstream schemas, paths, process startup syntax, SDK language bindings, UI rendering, event name mapping, prompt templates, transport details, OS observation mechanisms, credentials remaining within upstream executors, persistence implementation and package discovery. Adapter-local cannot mean unreviewable: RouteProfile must expose constraints, nonportable behavior and enforcement evidence. An adapter extension cannot redefine a canonical field.

Compatibility proposal: unknown major epoch = reject; unknown required feature/revision = unsupported; optional extension = ignored only if demonstrably inert and explicitly optional. Upgrade never silently adds authority. A document-only migration can preserve opaque source data, but activation requires a new capability diff review for widened requests. Proposal competes with permissive best-effort loading; falsifier is reproducible evidence that fail-closed compatibility prevents necessary benign ports while a permissive model retains equal boundary guarantees. It does not prove bug-free parsing or isolation.

## 5. Disabled-path inertness and evidence

This answers Q7. I: Disabled is a property of host observations over a defined phase, not a manifest boolean, an empty tool list or a plugin's own log line.

Cold-disabled property: starting the host with an installed-but-disabled fixture has the same externally relevant trace as starting it with the fixture absent, except a tightly specified trusted catalog metadata read and a deterministic disabled-status record. Trusted metadata inspection is data parsing only: no imports, interpolation, executable hooks, dependency resolution, package installation, downloads, environment expansion or schema network fetch. Opaque file hashing is permitted only within the separately authorized catalog operation and cannot invoke handlers.

| Checkable property | Required independent evidence | Fail condition |
|---|---|---|
| No plugin execution | Loader/import probe plus process/thread/module provenance, before/after activation graph | Any code evaluation, constructor, script, subprocess, scheduled callback or worker attributable to disabled fixture |
| No network/IPC | Capture attempted DNS/socket/pipe/IPC operations, including denied attempts, with process attribution | Any fixture-attributable connection attempt, telemetry, update check or local service call |
| No host mutation | Filesystem/registry/config/permission inventory and write-event trace | Any unexpected write, install, registration, watcher, timer, environment/config mutation |
| No secret access | Synthetic secret-provider canary requests and controlled environment provenance | Any secret lookup or inherited canary visibility, even if unused or redacted later |
| No ambient authority | Effective descriptors/handles/environment and grants snapshot | Any inherited filesystem/network/process power beyond the metadata parser boundary |
| No contribution/context pollution | Command/tool/skill/hook registry and prompt/context inventory | Disabled fixture advertises executable contributions, injects prompt text or changes routing |
| No dependency side effects | Dependency resolution and activation graph | Disabled root activates dependency, triggers artifact fetching or re-enables itself |
| No resource/billing effects | Logical scheduler trace, budget ledger and provider-call sentinel | Plugin work, reserved budget or provider/model invocation; missing meter is U, not zero |

Dynamic disable: revoke admission first; drain/cancel admitted work under defined deadlines; fence new effects; dispose registrations and child work; reconcile outstanding effects; certify quiescence with external observations. Observed effects before the disable barrier are retained in the ledger. If a child cannot be stopped or an effect outcome is unknown, status is failed-to-quiesce/unknown, never inert. Re-enable requires new epoch-bound admission; stale callbacks must be rejected.

Evidence design: matched absent/disabled baselines, fixed clocks/seeds and event script; hashes of controlled filesystem state; all negative attempts retained; independently instrumented observer calibration with deliberately noisy fixtures. Run both Windows and Linux profiles eventually. Never treat timing equality as a security oracle: compare semantic events and bounded resource deltas with a predeclared background allowlist. Missing low-level observation or unaccounted baseline noise makes the corresponding claim unverified. A finite observation window proves only the tested execution; structural no-import/no-grant review is also necessary to rule out delayed activation paths.

Competing option: trust the upstream enable toggle. Decisive falsifier of the stronger implementation: any prohibited cold-disabled effect or post-barrier new effect. Limit: a clean controlled trace cannot prove universal absence of vulnerabilities, nor can sandboxing make authorized dangerous operations safe.

## 6. Porting-cost model and cheapest credible paths

This answers Q8-Q10. I: Unit of assignment is a source-artifact × destination-profile × capability/behavior set × OS pair, fixed before work begins. Source package count and successfully completed demo count are inadequate denominators.

### Measurement contract

Total effort = shared adapter/platform discovery and construction + per-port discovery/specification + implementation + authority/schema mapping + fixtures/independent verification + packaging/documentation + user migration/reconstruction + defect repair + observed maintenance. Record person-hours by role and elapsed hours separately. Count failed and abandoned ports, rework and paid review. Shared costs are reported unamortized and at the actually observed accepted-port count n; no assumed future community size. Token/provider usage, if later authorized, is a separate measured resource vector rather than a proxy for labor.

Collect: handwritten glue LOC, generated LOC and generator-maintenance LOC separately; changed upstream API touchpoints; capability translation rules; lifecycle mappings; required/optional contributions; test cases attempted/passed/failed/unverified; accepted behavioral coverage; authority degradations; incompatible dependency counts; qualification/maintenance per breaking upstream release. LOC excludes vendored source from glue but reports it separately. Zero-length adaptation may still have nonzero review cost.

Effort intervals: before a pilot, hours and savings for every ecosystem are U, with no defensible finite confidence interval. Report the prior feasible range as nonnegative and unbounded above, with no-port/infinite cost for impossible required semantics. Structural complexity bands below are hypotheses, not hour estimates. After a preregistered paired pilot, report raw distributions, medians/IQRs and paired effect intervals; repeated ports by the same porter/package are clustered, not independent. Preregister an interval/confidence procedure and its justified precision target; disclose small-sample instability rather than adopt an arbitrary numerical default. Censored/abandoned work stays in assignment-level outcomes and accumulated cost.

Acceptance denominator: report both total assigned ports and independently accepted-equivalent ports. Cost per accepted-equivalent port includes all assignment costs; if none are accepted the ratio is undefined, not zero. Report successful required capability-scenarios / assigned required capability-scenarios, with security/evidence failures as disqualifying rather than averaged away. Baseline must implement the same target behavior, privileges, packaging and verification standard.

### Per-ecosystem path hypotheses

| Source profile | Cheapest credible proposed path / structural band | Competing option | Decisive falsifier and limit |
|---|---|---|---|
| DeepSeek/Cordis | I: extract pure tool/service semantics; map injection, typed events and disposal; medium for tool-only, high for lifecycle-wide | Preserve original harness behind a route, or native rewrite | Dependency/dispatch/disposal equivalence requires host emulation or broader authority. Does not port arbitrary service graph unchanged |
| OpenCode V1 | I: extract tool definitions; explicit V1 hook adapter; medium/high | Rewrite to canonical API or leave in upstream route | Hook order/context mutation needed by fixture cannot be preserved. Does not imply V2 compatibility |
| OpenCode V2 | I: map stable plugin identity and tool/domain registrations; high for transforms/session/auth interactions | Native implementation or upstream-route execution | Domain state/permission lifecycle cannot be attenuated with equivalent behavior. Does not reuse V1 implementation |
| Goose external extension | I: reuse server protocol payload with pinned MCP profile; low/medium for pure tools | Canonical tool rewrite or no port | Host feature/transport mismatch or startup permissions dominate savings. Does not port Goose built-ins automatically |
| MCP server, current or legacy | I: retain business tool implementation; protocol/profile adapter and evidence wrapper; low/medium | Direct native tool API or separate host-specific integrations | Wire/profile translation loses result/effect semantics or cap enforcement. Protocol reuse does not establish package/OS reuse |
| VS Code | I: extract UI-independent tool/language service or static assets; high for workbench-integrated code | Retain editor extension as external UI, or no port | Required behavior inherently needs editor/extension-host APIs. Does not make GUI a v3 requirement |
| OpenAI portable/compatibility | I: preserve common skill/MCP assets, translate overlay and hook profile; low for static subset, high for hosted integrations | Native descriptor or unchanged upstream execution | Host-specific registered connections/hooks/publication cannot be represented within bounds. Does not transfer account access or listing approval |
| Claude Code | I: preserve skills/MCP assets; map commands/agents/hooks individually; medium/high | Native rewrite, upstream route or no port | Permission hooks, mods, channels or workflows lose essential behavior. Skills conversion is not equivalent to agent/hook execution |
| Anthropic MCPB | I: inspect package metadata, reuse server only with qualified local binding; medium | Use source server packaging or no port | Bundled runtime/native dependencies or user configuration prevent permitted execution. Does not authorize extraction/install or credential migration |
| Cursor | I: common Agent Plugins subset, separate Cursor-specific adapter; low for skills/MCP, high for hooks/rules/UI | Native rewrite or no port | Placeholder expansion or host-specific component semantics fail equivalence. Declaration of standard support alone does not pass |

Every hours interval in this table is U. A low structural band means fewer kinds of mapping, not guaranteed cheap work. Each row's recommendation is conditional on source licensing and compatible authorized access, neither decided by R-A.

### Economies: established mechanism versus unmeasured benefit

| Claim | What evidence supports now | Paired test / falsifier | What it does not prove |
|---|---|---|---|
| Shared manifests reduce duplicate packaging definitions | D: Agent Plugins fixes common component locations [S19-S20]; I: one canonical mapping can be reused | Compare native packaging vs shared packaging with identical accepted behaviors; reject savings claim if total adaptation/review/maintenance cost is not lower | Runtime semantic equivalence or lower provider usage |
| Shared contribution taxonomy reduces repeated API interpretation | I: repeated tool input/output shape can share validators | Freeze corpus; compare unique mapping rules and total accepted cost; reject if taxonomy escape hatches dominate or cost rises | Portability of prompts, UI or lifecycle |
| Generated adapters remove repetitive glue | I: syntactic translation can be generated once schemas are exact | Include generator construction/repair and generated defects; reject if amortized cost at observed n is no lower | Correctness of generated authority mapping |
| MCP reuse preserves business logic | D: protocol tools have defined request/result contracts [S11,S13T]; I: same service can be wrapped | Compare server reuse with equivalent native rewrite, including deployment/observability; reject if caps/evidence need a rewrite | Uniform permission, installation or billing semantics |
| Broad community porting accelerates comprehensive build | U: no local adoption/port data | Track invited/started/abandoned/accepted ports and maintainer load; reject time-saving claim if acceptance throughput or maintenance is worse at equal quality | Future adoption, free labor or license compatibility |

The product thesis is weakened, not rescued rhetorically, if representative ports repeatedly require semantic rewrites or retain larger authority than native alternatives. No projected effort saving is substituted for a measurement.

## 7. Provider-free deterministic conformance design

This answers Q11-Q12. All tests below are PENDING DESIGN, not executed. No target fixture, host/plugin/harness, installer or model/provider call was run. Artifact document checks are separate.

### Same semantic fixture, explicit host realizations

I: Fixture F1 is a synthetic text-transform tool. Given {text:"alpha", mode:"upper"}, it returns {text:"ALPHA", changes:5}. A read-fixture operation reads only a provided logical resource containing "alpha". A stage-artifact operation proposes a write to a synthetic output resource. An emitted status event and one optional instruction asset exercise contribution discovery. No model interprets the instruction asset during conformance.

Each named ecosystem receives an inert source-shape description of F1 and a mapping table. Cordis: injected fixture service/tool with disposer; OpenCode V1: returned tool/hook object; V2: setup registration and cleanup; Goose: external MCP profile; MCP: separate current and legacy wire transcripts; VS Code: command/tool contribution plus activation record; OpenAI: portable package plus explicitly required overlay; Claude: skills/MCP/hook component descriptors; MCPB: bundle manifest metadata; Cursor: portable and Cursor-specific layouts separately. These are proposed host realizations, not claims all surfaces support identical optional event semantics.

Required core fixture behavior must remain equivalent. A host lacking a required contribution is UNSUPPORTED and cannot be counted as a successful full port. An explicitly optional host-specific event may return a declared degradation, but its absence must not alter core results or authority. Parsing a fixture descriptor is not a runtime port.

A separate F2 hostile fixture collection requests excessive path scope, hidden egress, credential access, duplicate identifiers, undeclared dependencies, cyclic delegation, startup side effects, forged grants/evidence and delayed callbacks. F3 exercises state recovery, version changes and disable while an effect is in flight. All data, recipients and credentials are synthetic sentinels.

### Levels and explicit oracles

| Test id / level | Input variation and deterministic oracle | Failure / stopping rule |
|---|---|---|
| C01 static contract | Parse valid fixture; canonical normalization equals frozen expected record; stable digest under approved serialization | Invalid/unknown required schema accepted or semantic field lost = FAIL |
| C02 translation | For each profile, compare normalized identity, schemas, contributions, request bounds and unsupported list to golden record | Silent dropped required feature, extra authority or changed output contract = FAIL |
| C03 version split | V1/V2 definitions, Agent Plugins schema mismatch, MCP current/legacy transcripts, unsupported feature epochs | Wrong-version execution or silent downgrade = FAIL; no compatible profile = UNSUPPORTED |
| C04 graph attenuation | Enumerate finite operation/resource/label/budget sets; compare actual effective grants with independent set/constraint oracle | Any effective permission outside parent/GoalSpec ceiling = FAIL |
| C05 conflicts | Permute source order, duplicate ids, contradictory permissions, missing disabled dependencies and dependency cycles | Nondeterministic decision or automatic widening/activation = FAIL |
| C06 budgets | Parallel child reservations; exact exhaustion; release; duplicate settlement; unknown price/usage | Oversubscription, double refund, unknown-as-zero or unenforceable cap accepted = FAIL |
| C07 privacy/egress | Synthetic class/compartment/purpose mismatch, redirects, local IPC, payload to allowed host | Any unauthorized attempt admitted = FAIL; no calibrated observer = UNVERIFIED |
| C08 credentials | Fake upstream-auth handle and forbidden secret-provider canary | Secret contents enter plugin/context/log or handle implies read access = FAIL |
| C09 cold disabled | Absent vs disabled baseline plus import/startup/network/secret canaries | Any non-allowlisted side effect = FAIL; only tool-list evidence = UNVERIFIED |
| C10 dynamic disable | Revoke at each state transition; late callbacks; active child; effect response lost | Post-fence new effect = FAIL; unresolved prior effect is UNKNOWN and blocks inert certification |
| C11 evidence/output | Correct, malformed, duplicate, forged-source, missing-hash and redaction variants | Forged evidence accepted; completion conflated with review acceptance; missing evidence called pass = FAIL |
| C12 refusal taxonomy | Each refusal-triggering request mapped to exact expected class with no side effect | Generic success, retry beyond authority or inconsistent normalized refusal = FAIL |
| C13 replay/recovery | Reordered/duplicate transport messages, stale grant epoch, host restart, manifest digest substitution | Duplicate externally committed effect, widened grant or lost unsettled ledger = FAIL |
| C14 OS/profile qualification | Same controlled filesystem and effect cases on separately pinned Windows/Linux bindings | Treating one OS/host version as evidence for another = UNVERIFIED |
| C15 observer calibration | Noisy control fixture deliberately attempts each prohibited channel | Missed positive control invalidates every associated negative claim |

Static schema translation may eventually run without any plugin execution; runtime inertness and capability enforcement need a separately authorized, isolated host evaluation. A mocked kernel can test intended semantics but cannot qualify the real boundary. All network/provider functions in the eventual fixture environment are fail-fast sentinels; deterministic transcript replay must never contact a provider. Actual host tests must disable updater/telemetry/model bootstrapping before admission and independently verify that suppression. If an upstream host cannot start in this mode, record UNSUPPORTED for provider-free execution rather than making a model call to finish the test.

Oracles are maintained independently of adapters: small canonical expected records, explicit finite authorization relations, expected output bytes, effect state transitions and negative observation traces. No LLM, upstream permission classifier or implementation-under-test generates the expected answer. Freeze test corpus, parser rules, ordering, random seeds, logical time, profile pins and observer calibration records before comparing candidates. Repeatability is identical canonical records/traces, not identical incidental timestamps.

### Refusal taxonomy

I: Normalize SCHEMA_INVALID, VERSION_UNSUPPORTED, CAPABILITY_UNSUPPORTED, REQUIRED_DEPENDENCY_DISABLED, CONTRIBUTION_CONFLICT, AUTHORITY_DENIED, PRIVACY_DENIED, EGRESS_DENIED, CREDENTIAL_VISIBILITY_DENIED, BUDGET_EXHAUSTED, ACCOUNTING_UNKNOWN, APPROVAL_REQUIRED, REVOKED_OR_EXPIRED, EFFECT_OUTCOME_UNKNOWN, EVIDENCE_INVALID, QUIESCENCE_FAILED and HOST_UNAVAILABLE. Keep raw upstream error text separately redacted and attributed. Protocol errors, policy refusals, tool-domain errors and uncertain external effects are distinct. Retrying requires a route/effect-specific idempotency policy; refusal is not permission to switch identities or broaden the request.

Verdicts: PASS (all mandatory tests and evidence met), FAIL (counterexample), UNSUPPORTED (required behavior unrepresentable), UNVERIFIED (missing observation), and NOT_APPLICABLE (predeclared optional dimension only). Publication of a passing profile requires independent acceptance. Overall all-ecosystem conformance cannot be PASS while a required profile is unsupported/unverified.

Immediate stop: real credential discovered/requested; attempted provider/model call; unapproved network/install; uncertain containment; missing observer control; ambiguous irreversible effect; grant widening; denied authorization; unexpected host mutation; or a legal/licensing prerequisite unresolved. Preserve evidence, stop dependent work, and ask Lucas for the exact next authorization or decision. No automatic fallback to another provider, account, runtime or broader mode.

Competing option: upstream-native test suites with no canonical conformance layer. Decisive falsifier of this suite's usefulness: independently accepted real ports exhibit authority/semantic violations outside its scenarios at a materially higher rate than the competing verification at equal review cost. Limit: finite tests are not formal proof, security certification, CVE clearance or a porting-cost measurement.

## 8. Recommendation register

All entries are I: proposals for Owner consideration, not accepted choices.

| Proposal | Competing option | Decisive falsifier | Does not prove |
|---|---|---|---|
| R1: Preserve common package floor, add external authority/evidence contract | Agent Plugins alone or independent formats | Required semantics fit the simpler option and its accepted cost is lower | Standard compliance across all hosts |
| R2: Keep kernel authority outside opt-in capabilities | Put enforcement in ordinary removable plugins | The alternative retains identical non-bypassable enforcement under remove/reorder/failure with lower complexity | Any chosen sandbox's security |
| R3: Profile upstream versions and OS separately | One universal compatibility flag | Universal adapter preserves every required scenario without hidden degradation and costs less | Future version stability |
| R4: No grant widening; explicit unknowns refuse required execution | Best-effort execution with warnings | Equally safe containment demonstrated for the broader behavior | Correctness of all resource normalization |
| R5: Prove disabled state by independent observations | Trust config flags | Counterexample absent across calibrated cases plus structural loader proof in the simpler design | Universal inertness from finite traces |
| R6: Compare total accepted-port cost with failure and maintenance included | Count converted manifests or glue LOC only | Simpler proxy robustly predicts accepted total cost across held-out ecosystems/releases | A current savings percentage |
| R7: Publish proposed epoch-0 contract for porter feedback after review | Wait for implementation to define API | Early contract creates more breaking rework than independently costed delayed publication | Authority to publish now or legal clearance |

R7 preserves D-026's early-contract direction; this research neither publishes nor delays an authorized release. The proposed contract can be comprehensive while each capability ships opt-in. Owner choice is semantic contract acceptance and qualification criteria, not a technology selection in this report.

## 9. Local execution handoff

Status: all target tests are pending. This is a handoff specification, not executable code or an instruction to run anything now.

Prerequisites before a later authorized run:

1. Lucas approves the contract epoch, exact capability/behavior corpus, independent reviewer, allowed environments and provider-free execution scope
2. Supply current operative GoalSpec/constitution semantic interface for reconciliation, without assuming Hermes authority. Accept no widening implied by missing text
3. Pin source artifact, host executable, plugin package, SDK/protocol, OS and adapter versions/digests; obtain R-C license/distribution prerequisites
4. Provide synthetic-only resources; deny real credentials, provider/model endpoints and publication; calibrate independent process/filesystem/network/secret/effect observers
5. Build or select a test runner only under separate implementation authorization; this report chooses no language, store, framework, sandbox or package manager

Pending tests: C01-C15, fixture F1 core behavior in every row of section 7, F2/F3 negative and recovery cases, paired accepted-port cost trial, then a held-out host/version maintenance trial. No pilot sample size or effort cap is silently adopted; preregister both with a precision/power rationale or label the initial work exploratory.

Evidence to return: source and artifact pin ledger; normalized manifests and AuthorityGrant graphs; mapping/unsupported-feature inventory; expected-versus-observed outputs; calibrated absent/disabled traces; attempted effects including denied attempts; budget/accounting vector with unknown reasons; refusal records; lifecycle/settlement logs; porter/reviewer effort ledger including abandoned work; and independent acceptance record linked to exact artifact hashes.

Pass/fail: each mandatory predicate must pass with complete observations and independent review. Any widening or unauthorized attempted activation is a failure; missing information is unverified; unsupported required behavior is not a successful port. Cost thesis supported only if paired total accepted-equivalent cost is lower with uncertainty disclosed and no authority/evidence regressions. A small synthetic pass authorizes no general production claim.

Stop conditions: the immediate-stop list in section 7; a violated preregistered effort/resource cap; a pin mismatch; or no safe route that meets the mandatory authority/evidence contract. Do not keep trying installations, alternate accounts or broader modes to obtain a pass.

Owner decisions needed: accept/revise the record semantics and non-optional kernel boundary; approve actual namespace/epoch ownership; decide mandatory versus optional behavior per contribution family; authorize later implementation/test environment and instrument visibility; set cost/quality decision thresholds; appoint independent acceptance reviewer; and authorize any eventual publication separately. No language/runtime/store/vendor choice is requested by this lane.

## 10. Completion gate and question map

| Gate / question | Result | Evidence / limitation |
|---|---|---|
| Q1-Q3 named ecosystem comparison, permissions and versioning | Research complete | Sections 1-2 and Appendix A; per-cell D/I/U; current/legacy MCP and OpenCode V1/V2 separated |
| Q4 manifest coverage | Design complete | Section 3 + proposed-contract.json; external grant cannot be author-supplied |
| Q5 non-widening graph | Design complete | Section 4; constitutional/GoalSpec ceilings preserved; existing field names remain unknown |
| Q6 normative/adapter boundary | Design complete | Section 4; comprehensive capability taxonomy and immutable authority distinguished |
| Q7 disabled-path properties | Design complete; evidence pending | Section 5; independent observer tests, not asserted runtime inertness |
| Q8-Q10 cost, cheapest paths, economies | Model complete; measurement unknown | Section 6; denominators, unknown ranges, alternatives and falsifiers |
| Q11-Q12 provider-free suite, oracles and stop conditions | Design complete; not run | Section 7 and local handoff |
| Every proposal has an alternative, falsifier and limit | Complete | Section 8 plus section-specific alternatives |
| Protected paths untouched | O: no project/repository changes made | Only new report/appendix artifacts and public research captures created |
| Privacy/secret scan | O: artifact scan complete, no high-confidence secret or private-path pattern found | Report text and user-facing JSON/DOCX content checked; scan is not exhaustive secret detection |
| Independent review / acceptance | Research review completed; implementation and Owner acceptance not claimed | Independent reviewer checked questions, evidence distinctions and digest/grant fixes; no runtime qualification |


## Appendix A. Source-pinned bibliography

All sources below were freshly retrieved on 2 October 2026 UTC. Bracketed source ids map to the full SHA-256 capture digest in source-ledger.json. These pins preserve the retrieved text, not a promise that a mutable site or upstream binary is unchanged. No secondary commentary is relied on for a consequential technical claim.

- S00: [DeepSeek Harness README](https://github.com/deepseek-ai/deepseek-harness). mutable master; developer preview. Capture SHA-256 prefix: 0596dc58e3195945
- S01: [Cordis Primer](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cordis-primer.md). mutable master. Capture SHA-256 prefix: 35323828ea419495
- S02: [DeepSeek Harness Safety](https://github.com/deepseek-ai/deepseek-harness/blob/master/SAFETY.md). mutable master. Capture SHA-256 prefix: 123ddaf2d96251f5
- S03: [OpenCode V1 plugins](https://opencode.ai/docs/plugins/). V1 documentation; executable release unknown. Capture SHA-256 prefix: 4d103be97fa3893b
- S03P: [OpenCode V1 permissions](https://opencode.ai/docs/permissions/). V1 documentation. Capture SHA-256 prefix: 282af46fdc97d196
- S04: [OpenCode V1-to-V2 plugin migration](https://opencode.ai/v2/docs/build/plugins/migrate-v1). V2 migration contract. Capture SHA-256 prefix: b26fe3c1d69f9253
- S05: [OpenCode V2 plugin API](https://opencode.ai/v2/docs/build/plugins). V2 documentation; executable release unknown. Capture SHA-256 prefix: ddd7eb7a38d0158b
- S06: [OpenCode V2 plugin configuration](https://opencode.ai/v2/docs/plugins). V2 documentation. Capture SHA-256 prefix: 22c4faee477b3c4a
- S07: [Goose Using Extensions](https://github.com/aaif-goose/goose/blob/main/documentation/docs/getting-started/using-extensions.md). mutable main. Capture SHA-256 prefix: 6d0afa4cb4c9743f
- S08: [Goose Configuration Files](https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/config-files.md). mutable main. Capture SHA-256 prefix: 25a279b703cdd065
- S09: [Goose Permission Modes](https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/managing-tools/goose-permissions.md). mutable main. Capture SHA-256 prefix: 6a8769d25de5dffd
- S10: [MCP versioning](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning). current 2026-07-28; retrieved redirect. Capture SHA-256 prefix: de991a66bbc928bc
- S11: [MCP current specification](https://modelcontextprotocol.io/specification/2026-07-28). 2026-07-28; composite capture. Capture SHA-256 prefix: 3d6cb1f14daf8e57
- S12: [MCP current discovery](https://modelcontextprotocol.io/specification/2026-07-28/server/discover). 2026-07-28. Capture SHA-256 prefix: d8aea341a80d422b
- S13: [MCP current versioning and compatibility](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning). 2026-07-28; successful linked retrieval, direct retry failed. Capture SHA-256 prefix: e4378f90f6e29a30
- S13A: [MCP current authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization). 2026-07-28. Capture SHA-256 prefix: 389637c825bbcdda
- S13T: [MCP current tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools). 2026-07-28. Capture SHA-256 prefix: 08186808b92c7439
- S14: [MCP legacy lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle). 2025-11-25 compatibility profile. Capture SHA-256 prefix: 4c5d2bf07d637568
- S14A: [MCP legacy authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization). 2025-11-25 compatibility profile. Capture SHA-256 prefix: 1d3ac02fe85b3cd2
- S15: [VS Code extension manifest](https://code.visualstudio.com/api/references/extension-manifest). mutable API documentation. Capture SHA-256 prefix: 68490f1c298c1e39
- S16: [VS Code activation events](https://code.visualstudio.com/api/references/activation-events). mutable API documentation. Capture SHA-256 prefix: c87a4f9c4b574161
- S16T: [VS Code Workspace Trust](https://code.visualstudio.com/api/extension-guides/workspace-trust). mutable API documentation. Capture SHA-256 prefix: 2f44da3d0cb445ac
- S16P: [VS Code proposed API](https://code.visualstudio.com/api/advanced-topics/using-proposed-api). mutable API documentation. Capture SHA-256 prefix: 6cb3a754171739ee
- S17: [OpenAI Package your plugin](https://developers.openai.com/plugins/build/plugins). indexed primary body; direct retrieval was navigation-only. Capture SHA-256 prefix: 1f5ec067b97afb40
- S18: [OpenAI Claude-plugin conversion](https://developers.openai.com/plugins/guides/submit-claude-plugin). indexed primary body; conversion is surface-specific. Capture SHA-256 prefix: 6a28b5a8661b40da
- S19: [Agent Plugins overview](https://agent-plugins.org/). published 1.0.0. Capture SHA-256 prefix: b3e38fd4ab87526d
- S20: [Agent Plugins specification](https://agent-plugins.org/specification). published 1.0.0. Capture SHA-256 prefix: 74098b1c85680902
- S21: [Claude Code plugins overview](https://code.claude.com/docs/en/plugins). mutable documentation. Capture SHA-256 prefix: ec5c6046ec34bfc7
- S22: [Claude Code plugin manifest reference](https://code.claude.com/docs/en/plugins-reference). mutable documentation; per-feature minima, not global epoch. Capture SHA-256 prefix: 9f9d45e62fce01b4
- S22H: [Claude Code hooks](https://code.claude.com/docs/en/hooks). mutable documentation. Capture SHA-256 prefix: 377cb1b9ae4194cb
- S22P: [Claude Code permissions](https://code.claude.com/docs/en/permissions). mutable documentation. Capture SHA-256 prefix: eefc64816e1c4212
- S23: [MCP Bundles](https://github.com/modelcontextprotocol/mcpb). redirect from anthropics/mcpb; mutable main. Capture SHA-256 prefix: df94ebce5c4496ef
- S24: [Cursor plugins](https://cursor.com/docs/plugins). Agent Plugins and Cursor Plugins separated. Capture SHA-256 prefix: f7dcb6e3235fddfd
- S25: [Cursor plugin reference](https://cursor.com/docs/reference/plugins). mutable documentation. Capture SHA-256 prefix: dcd7c85cd8a643f0
- S26: [Cursor IDE permissions](https://cursor.com/docs/reference/permissions). IDE profile; CLI separate. Capture SHA-256 prefix: 8f5622603dc288e1

Licenses are intentionally not flattened into a single ecosystem label. Root repository licenses, vendored components, protocol/specification text, documentation, marketplace assets and branded host distribution can differ. R-C holds the fresh licensing evidence and counsel questions; R-A makes no legal distribution conclusion.

### Immutable primary-document supplement

The following exact source files were additionally fetched as inert text from the newly resolved public commits. These are source-document pins, not installed-binary qualification. The separate source-ledger.json records full content digests.

- S00: [exact source file](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/README.md); commit 639ed015397290b3745d163aafe02ffee4aa3f84; content SHA-256 0f5516be2acde776f05572cbc8c3093c90549afe04ce118e11157d073d5d15f4
- S01: [exact source file](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/cordis-primer.md); commit 639ed015397290b3745d163aafe02ffee4aa3f84; content SHA-256 f0cc573cc10b60d1bd76039fb0bd666edfb32c9b18027d4dc301c042a9e65d58
- S02: [exact source file](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/SAFETY.md); commit 639ed015397290b3745d163aafe02ffee4aa3f84; content SHA-256 62075bb51e0f7790441e7722ff12063107b4866019332e71ef01b63b6f880fee
- S07: [exact source file](https://github.com/aaif-goose/goose/blob/8f4cab5fdb54dfb6a6749b997f4ef560625d1f9c/documentation/docs/getting-started/using-extensions.md); commit 8f4cab5fdb54dfb6a6749b997f4ef560625d1f9c; content SHA-256 3a904e08f67d70a8e909923bb431db31fef5faf64c4238122a9d1ccf5cecf6db
- S08: [exact source file](https://github.com/aaif-goose/goose/blob/8f4cab5fdb54dfb6a6749b997f4ef560625d1f9c/documentation/docs/guides/config-files.md); commit 8f4cab5fdb54dfb6a6749b997f4ef560625d1f9c; content SHA-256 6a2bdd61ab3553b1e74800cd678a41c746d29facd847f8a26b67c981d2e834b9
- S09: [exact source file](https://github.com/aaif-goose/goose/blob/8f4cab5fdb54dfb6a6749b997f4ef560625d1f9c/documentation/docs/guides/managing-tools/goose-permissions.md); commit 8f4cab5fdb54dfb6a6749b997f4ef560625d1f9c; content SHA-256 19b329b7d4f79af756b90b6165cfb905db77a69935fd1a3e4d5e6aab0327115f

# R-L: Shared CLI, TUI and GUI interface platform

Date: 2026-10-02 UTC  
Status: specification candidate; not an accepted implementation, production wire revision, product choice or route qualification  
Repository baseline: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
Research boundary: static repository/public-source inspection and artifact preparation only; every proposed runtime fixture is **UNEXECUTED**

## Decision-ready findings

One meaning across surfaces requires **one admitted command meaning and one snapshot-bound query meaning**, not one renderer. CLI arguments, a TUI action, an editor action and a later GUI control are presentations of the same operation. An enabled plugin can add a versioned operation but cannot add a second authority path. The semantic catalog, canonical receipts, typed projections, durable interactions, configuration resolver and capability explanations can be constructed and tested before either visual toolkit is selected.

Five seams are particularly important:

1. Keep command identity, wire request identity, durable interaction identity, input ownership, writer fencing and effect authority distinct. A tab, a connection, a permission dialog or an input lease is not an execution grant
2. Bind every query to its source revision, projection version and authorized audience. Otherwise two honest clients can appear to disagree simply because they read different cuts, and an old cached view can expose revoked data
3. Preserve the frozen M1B experiment exactly. `GAP` is a visible reconstruction marker/reason, not an additional message. Owner Stop is a separate typed control path. New application records below do not add fields to M1B
4. Make configuration a compare-and-apply transaction with per-recipient application evidence. An acknowledgement is neither successful application nor current authority
5. Reserve control capacity through ingress, framing, decoding, scheduling, persistence and delivery. Separate queues alone do not establish bounded Stop latency

TUI-first construction and GUI-later construction remain the sequence. D-019 still requires the comprehensive accepted surface built and shipped opt-in; this report does not reinstate the rejected smaller release. The exact interpretation of “GUI later” relative to first-release packaging remains an explicit Owner reconciliation item because older PRODUCT/INTERFACE text excludes the initial GUI while D-019 includes it. No capability is silently deferred here.

No language, store, runtime, framework, transport, encoding, renderer, UI toolkit, multiplexer, human configuration syntax or vendor is selected. Existing frozen M1B encoding constraints are preserved, not freshly selected. Public interface richness, schema validity, mocks and historical records do not establish productive-continuity superiority, credential isolation, subscription savings, accessibility conformance or cheap porting.

## Evidence and authority

**Labels used throughout:** SD = public or repository source-documented; SO = statically observed source/record, not newly executed behavior; P = design inference/proposal; U = unknown or unmeasured. “Required” means an existing accepted requirement unless explicitly identified as a candidate acceptance predicate. Candidate recommendations C01–C12 are compared in Q15 and the recommendation register, including competitors, falsifiers and non-proofs.

The inspected governance and specification set includes CONTROL_PLANE, ANCHOR, D-017–D-033, the current v3 goal, PRODUCT, INTERFACE-STRATEGY, PLUGINS-AND-EDITIONS, TERMINAL-RUNTIME, CLI, M1B-WIRE-PROFILE, PERFORMANCE-PLAN and the current research index, architecture/harness coverage, gaps and synthesis. Source-register local entries identify exact repository-relative files and SHA-256 values. Governance, not copied stale brief language, controls interpretation. Hermes is an optional upstream integration; Recursion owns a first-class native loop and supports independently useful upstream-only workflows without hidden native helper inference.

SO: the tree contains historical interface and replay/flow model records. In particular, the scoped Codex 0.149.0 scripted-loopback interaction record includes steering, old-question rejection, fork boundaries and idle history recovery; it does not qualify current authentication, fresh-connection outstanding approvals or post-resume inference. Static `contract_vectors.py` defines finite configuration/revocation and consultation schedules, including a deny-all counterexample, not a shared product frontend. The flow model includes a separate Stop path but does not demonstrate a physical end-to-end reserve. The replay fixture materializes synthetic snapshots and manifests but is not a production store. These observations preserve bounded evidence rather than saying nothing exists. No code from the snapshot was executed or imported.

The earlier gap prose “no model” and “no platform fixtures” is stale in parts. G-06, G-07 and G-11 Owner decisions are closed; full implementation/profile qualification remains open. G-09 remains open: this candidate supplies corpus shape and resolver obligations, not a selected syntax, an accepted privacy/publication lattice or executed cross-platform conformance.

### Primary-source findings that change the design

<a id="json-schema-facts"></a>
- JSON Schema 2020-12 validates structure; duplicate-member behavior is not defined once a JSON object is formed. Reject duplicates at parse time. Its dialect/vocabulary mechanism also means a schema identifier must include supported semantics, not just a marketing version. [S01](https://json-schema.org/draft/2020-12/json-schema-core)
<a id="jcs-facts"></a>
- JCS preserves string data without Unicode normalization and gives deterministic JSON serialization. It does not grant authority, compare path identity or settle merge precedence. M1B additionally rejects floats and negative zero; general JCS support must not weaken that profile. [S02](https://www.rfc-editor.org/rfc/rfc8785)
- OpenAPI 3.1.2 can describe an HTTP binding and distinct operations; it is not a transport-neutral command semantics engine. JSON-RPC request IDs correlate messages; notifications have no reply. Neither supplies durable application idempotency. [S04](https://spec.openapis.org/oas/v3.1.2.html), [S05](https://www.jsonrpc.org/specification)
- tmux control mode can pause a lagging pane’s output and let a client reconstruct screen contents. That is useful flow-control prior art, not canonical event replay or Recursion authority. [S06](https://github.com/tmux/tmux/wiki/Control-Mode)
- Neovim publishes function/event metadata, API levels and compatibility rules; its documented RPC interface illustrates one API exposed to several clients. It also documents a powerful control surface, not a least-privilege Recursion boundary. [S08](https://neovim.io/doc/user/api/)
- VS Code command arguments differ between palette, menu, keybinding and programmatic invocation. Its `when` condition affects visibility rather than argument delivery. Therefore “same command ID” alone is insufficient: surface-specific argument extraction needs explicit, tested mapping. [S09](https://code.visualstudio.com/api/extension-guides/command)
- The [canonical OpenCode v2 profile](../rf/report.md#opencode-v2-facts) distinguishes global subscription and session-log evidence. **I:** qualify each surface separately; source documentation does not establish the installed build or durability bound.
<a id="claude-mods-overview-facts"></a>
- **SD — current mods overview:** 2.1.287+ enables mods by default and ignores the early-access switch. Terminal and Desktop render mod UI; headless/SDK and VS Code chat hooks do not imply pane rendering. Desktop WSL does not load these plugins. Mods cannot restyle the permission prompt; this does not exclude pre-prompt decision influence. Built-ins are not all disabled by `--bare`, `--safe-mode` or `disableAllHooks`. [S20](https://code.claude.com/docs/en/plugins/mods/overview) Version, source, launch and security distinctions are in [R-M Q01](../rm/report.md#r-m-q01), [Q03](../rm/report.md#r-m-q03) and [Q09](../rm/report.md#r-m-q09).

<a id="r-l-q01"></a>
## Q01. One versioned command-and-query model

**P, C01.** Maintain a semantic operation catalog independent of rendering and wire binding. Each entry has immutable namespaced operation name/version, argument schema digest, result/projection schema digest, capability requirements, target kinds, effect classification, lifecycle semantics, preconditions, error taxonomy, supplying component/version and evidence level. A changing meaning is a new operation version, even when a UI label stays unchanged. Unsupported mandatory semantics fail negotiation; an extension cannot quietly degrade `steer` into `queue`.

The candidate application envelope `CommandIntent` contains: command ID; semantic operation/version; exact typed arguments and semantic digest; principal and authenticated grant reference; authority-domain/goal/task targets; relevant target revisions (attempt/turn, route, configuration and process as appropriate); expected authority/pause fences; causation/correlation; deadline and delivery policy; optional reservation reference; and provenance of the client/component. Schema and target determine required fields. Surface identity is audit metadata and cannot change authority. Authentication material is not embedded in ordinary query or event payloads.

Admission is singular: decode bounded data → validate version and schema → resolve typed targets → check current principal/grant/capability and resource bounds → verify expected revisions/fences → persist canonical acceptance/refusal and command identity → dispatch through the already admitted execution boundary. The deterministic kernel remains the authority; adapter validation is an additional check, not a competing admission. A query does not enter effect dispatch.

Receipts describe facts separately: locally saved intent; canonical accepted/refused; dispatched; delivered/applied; outcome observed; effects settled/unresolved; independently verified. A local offline outbox says `saved-locally`, never `accepted`. A timeout after possible dispatch enters reconciliation. The client first queries its old command receipt; it does not generate a new ID to force retry. One canonical owner controls retries beneath a stable operation identity. The proposed canonical operation key is (admitted authority domain, canonical command ID). Authenticated principal/grant binding remains inside the immutable semantic command bytes/digest; it is not a hidden second canonical ID namespace. Same key and same immutable bytes returns an authorized historical receipt without repeating effects; changed bytes, including changed actor/grant binding, conflict. Client/transport request IDs remain audit/correlation metadata. A client may use principal-local command IDs only through an explicit injective, durable mapping into canonical command IDs before kernel/receipt lookup. Current reader/domain authorization precedes any receipt lookup/disclosure; a readable old receipt never restores revoked effect authority. This is a cross-lane production mapping proposal, not an amendment of frozen M1A. Expired deduplication history produces `receipt-history-unavailable`, not permission to resend. Retention/tombstones must cover unresolved effects and the declared retry window.

`TypedError` contains code, failed precondition, target/revision, effect-attempted (`no|yes|unknown`), retryability (`never|same-id|after-refresh|reconcile`), receipt/evidence references and bounded explanation. Example candidate codes are schema mismatch, target ambiguity, stale revision, capability unknown, authority denied, duplicate-command conflict and reconciliation required. These are application-candidate codes, **not additions to M1B’s closed refusal alphabet**.

Capabilities are negotiated separately for semantic catalog, schemas, projection versions and renderer affordances. Effective availability is a tuple of declared, enabled, authorized, exact-route-supported, locally-conformant and presently-usable facts. `unknown` remains separate from `unsupported`; a button may display the reason but cannot claim the action will work. No handshake confers grants. After route/config/grant changes the server rechecks the exact tuple at admission.

**Concrete equivalence demonstration (specification, unexecuted):** a CLI `message send` candidate with explicit task/attempt/turn and `delivery=queue`, a TUI queue button with those resolved identifiers, and a GUI queue action all compile to operation `core.message.enqueue@candidate-0` with the same text reference, target revision, authority and delivery policy. Client ID and command ID may differ across independent requests; the semantic digest excludes only declared audit/identity fields, not authority or targets. To retry the *same* command from another client, retain the command ID. A menu’s selected task is explicitly serialized; it is never replaced with the currently focused task. A Stop action always serializes mode and scope. Local view rearrangement has presentation-only meaning and does not masquerade as a work command. Fixture F01 checks both byte/semantic equivalence and refusal equivalence.

The declarative `interface-contract.schema.json` appendix sketches the shared application envelope/status/error/interaction/config shapes in Draft 2020-12; `proposed-contracts.json` records semantic owners and invariants. These are review candidates, not complete authority validation, a generated implementation or changes to M1B. Operation-specific payload schemas and finite profile limits remain mandatory. The catalog can generate/help-check CLI flags, palette forms and API descriptions. Independently implemented surface codecs remain a real competitor if the conformance corpus is their common oracle. Neither generator reuse nor shared source code proves semantics; both require independent cases.

### Required-control semantic map

These are candidate catalog entries over the already required ten controls, not new product command names or guarantees of upstream support.

| Control | Common intent/query meaning on every surface | Fact that must remain separate |
|---|---|---|
| Streaming | subscribe to authorized task/turn projection at an explicit cursor/cut | presentation frame versus persisted evidence; no hidden reasoning requested |
| Questions | answer/cancel exact current interaction ID, generation and answer schema | locally saved response versus delivered/adopted answer |
| Approvals | inspect/respond to exact action digest, recipient, data, authority and expiry | visible permission dialog versus valid principal authorization |
| Queued input | enqueue, edit or remove before the declared delivery boundary using expected revision | accepted queue item versus delivered message |
| Steering | address current attempt/turn with route-specific supported delivery policy | queued follow-up versus actual active-turn delivery |
| Interruption | explicit Aggressive/Full/Lazy mode and exact selected ownership scope | installed fence, upstream interruption, local exit and external settlement |
| Resume | explicit continuation after current route/config/grant/checkpoint and unresolved-effect checks | reattachment versus renewed permission to execute |
| Fork | preserve source/context/evidence revision, lineage and separately reserved allowance; preview capture scope | copied evidence versus non-copyable active permits/writer authority |
| Compaction | inspect or explicitly request a supported transform under the single governor for its route epoch | deterministic inspection versus potentially model-backed transform; summary versus exact accepted instructions/approvals |
| Custom commands/plugins | invoke exact namespaced supplying component/version/schema under current admission | installed/discovered metadata versus enabled/admitted execution |

Every surface must be able to inspect the machine representation and exact unsupported/unknown route loss. A wrapper that only knows how to type a slash command cannot claim all ten semantic controls. Capability parity is qualified per exact route, not inferred from a common button label.


<a id="r-l-q02"></a>
## Q02. Deterministic status and projections

**P, C02.** A query names projection ID/version, scope/filter, authorized audience, requested source cut (or `latest` with explicit returned cut), page/continuation bounds and consistency requirement. The response binds writer epoch, canonical sequence, configuration/authority revisions, projection build/schema revision, snapshot identity, freshness and completeness. Filtered projection cursor, source canonical sequence and transport cursor are distinct. Unauthorized records may be omitted without revealing private sequence density to a public audience; opaque audience-scoped continuation handles are preferable candidates to globally enumerable IDs.

Status returns typed facts for current goal/plan, actor roles, authority/pause epochs, durable questions/approvals, queued input, active attempt/turn, budget reservations/observations, exact route and effective configuration. Each uncertain value uses `{knowledge: known|unknown|unavailable|stale, value, reason, observed_at, source_ref}`; only a known zero has numeric value zero. Absence of any in-scope queue items is distinguishable from an incomplete queue projection. Route, model, harness, pool and host are distinct objects.

A deterministic reducer/projection over recorded facts answers these queries without an assistant summary, repository indexing, provider health call or plugin activation. Explicit refresh/probe is a separate command with its own cost and authority. An unavailable optional service yields its last observation and staleness or an unknown reason. The backend may rebuild bounded local projections from canonical records; its CPU/I/O is reported, not described as costless. Rebuild never generates new model work.

Equal queries at equal source cuts, audiences and versions return equal canonical data. Different current cuts are not falsely counted as semantic drift. A query promising at-least-cut consistency either reaches it within its declared deadline or returns a typed lag/unavailable result. UI fields such as pixel coordinates, scroll offset and selected pane stay presentation-local. A canonical source fact that only the GUI can represent would violate this model. Privacy filtering happens before materialization/disclosure, not solely by hiding widgets.

The service boundaries are: kernel owns authority and canonical reduction; projection service owns reconstructable read models; query service enforces read scope; renderer owns temporary presentation; none may update goal/effect facts through its cache. A lost-machine recovery can report saved canonical work and unresolved remote state without asserting the worker is dead.

<a id="r-l-q03"></a>
## Q03. Plugin-contributed views and commands

**P, C03.** `ContributionDescriptor` binds plugin identity/version/artifact/dependency-lock digests, catalog/schema versions, namespaced command/view IDs, required capabilities, grants, projection subscriptions, input and output classes, resource envelope, lifecycle and explicit renderer support/loss. Reserve a core namespace; collisions and ambiguous aliases fail rather than override. An alias binds the exact version and argument transformation and cannot silently retarget after an upgrade.

Separate installed metadata, enabled policy, admitted grants, activated code and live contribution registration. A bounded metadata inventory can explain a disabled component; it may not import its implementation, scan its payload, register active handlers, run code, start watchers/timers/processes, read credentials, subscribe, index, reserve quota or make inference/network calls. Its contributed view/command does not appear as active merely because a file exists. Settings may list inert metadata with an explicit disabled status. Opening a layout containing a missing/disabled view renders a core-owned placeholder; it is not an activation trigger. An enabled extension’s first use still follows its declared admission and cost contract.

A view can receive only an authorized projection and submit declared intents. It cannot receive a general kernel object or raw credential-bearing environment. Rendering origin, signed publisher, marketplace membership or mod load order supplies no grant. Third-party presentation isolation is an implementation qualification question; this candidate does not claim security between views. D-029 also forbids mistaking output redaction for a structural credential boundary: a delegated CLI can exfiltrate through an unconstrained tool/output path even when direct OS reads are denied.

Zellij’s separate permissions for reading application state, writing stdin, opening plugins, clipboard access and environment access illustrate why a single “UI permission” would be too coarse. They do not map automatically to Recursion authority. [S07](https://zellij.dev/documentation/plugin-api-permissions.html)

No upstream enablement switch is assumed equivalent to Recursion’s complete disabled invariant. Import analysis must examine every component and effect, rather than a similarly named flag. The companion R-G/R-M studies cover porting and mod-specific source/licensing questions. This report copies no implementation and makes no clearance finding; the inspected root license is registered as S26 rather than treated as import permission.

<a id="r-l-q04"></a>
## Q04. Event streaming, durable interactions and reconnect

**Accepted M1B constraints, with P/C04 application composition.** Keep `HELLO/WELCOME/SNAPSHOT/EVENT/ACK/CREDIT/INPUT/RESIZE/RESET` and `m1b-broker/1` exact. Unknown fields fail. Cursors use their bound `event` or `utf8-byte` unit; event advancement is by one, byte advancement counts decoded UTF-8 bytes, not base64 characters, code points or rendered cells. Each CREDIT message is capped at 16,777,216 bytes and 65,536 events. Credit is positive, additive and cumulatively consumed; the frozen reference oracle adds successive grants without an aggregate outstanding-credit cap (reference_oracle.py:525–526). A production aggregate cap is additional proposed enforcement, not a guarantee of the frozen oracle. Configured queue limits are also separate bounds, not permission to allocate every per-message maximum for every view.

WELCOME’s replay floor cannot exceed its snapshot cursor. A requested cursor below the floor records a replay gap. After detection, **RESET is the only permitted same-stream continuation**; intervening ACK/CREDIT/INPUT/RESIZE/HELLO/WELCOME/SNAPSHOT causes the frozen permanent replay-gap-continuation refusal. RESET must not lower the current cursor, must be justified by gap/flow exhaustion, and clears pending credit; fresh CREDIT precedes subsequent EVENT delivery. Flow exhaustion is distinct from retention loss and must not be relabeled as fabricated history loss. The wire’s wording around ACK release and production cursor rollover needs explicit conformance/refinement work; this report does not silently amend it. Approaching M1B Count’s 2,147,483,647 maximum must not wrap or widen its integer type. Production stream rollover/negotiation remains a versioned decision and bounded unknown.

Canonical commands, authority/lease changes, pending-interaction changes, process exit, termination and canonical-state/effect observations are non-droppable. Append the authoritative observation and record its identity before deriving/coalescing presentation. A fast source must be throttled, boundedly spooled or its operation held according to an admitted policy when authoritative ingestion cannot continue; dropping an essential event and drawing a pleasant screen is a failure. Redraw frames, intermediate cursor movements and redundant visual deltas may coalesce after authoritative retention. A client that falls behind retention receives truthful gap/snapshot reconstruction; the log is not rewritten to hide its loss.

Candidate `ProjectionSnapshotManifest` sits in a **separately versioned application layer**, binding source cut, source stream identities, audience/filter/schema/config revisions, replay floor, materialized state digest and evidence coverage. It is not an extra M1B field. Snapshot bytes must exist, be digest-verified, be bound to a trusted source cut, and install atomically before the client advances its installed cursor. A wire-consistent invented floor/snapshot can pass a wire-only checker; actual storage facts need an independent oracle. Received, installed and acknowledged positions are distinct bookkeeping; no ACK implies effect settlement.

Questions, approvals and queued input live in canonical records, not modal widget state. Candidate `InteractionRecord` carries immutable interaction ID, generation, goal/task/attempt/turn, original request/action digest, authorized respondent/audience, exact recipient/data/scope, creation sequence, expiry, current revision, answer schema and status. Responses bind ID+generation+request digest+expected revision. Two windows racing to answer cannot both consume one waiter. A replacement waiter rejects a delayed answer even if prompt text matches. An answer locally drafted offline is not delivered or adopted. Approval reuse is valid only within its original exact bounds; changed action parameters require new admission. Reconnect queries pending interactions and existing receipts before presenting or resending.

Raw terminal `INPUT` and `RESIZE` require their separately typed current leases bound to target/process/daemon epochs. Focus, attach and split do not acquire or steal them. Writer fence, workflow-step coordination lease, executive role lease and input/resize lease are distinct. Owner Stop bypasses the *input ownership requirement* through its authenticated, scoped control path; it does not bypass authority. Detach closes a view subscription, not the runtime-owned adapter connection or actor. Reconnect never relaunches a process or resumes effects merely to repair presentation. Causal source IDs and reply-delivery generation preserve R-J’s proposed durable interaction direction without adopting unreviewed wire additions.

**P:** use the [canonical v2 stream/log facts](../rf/report.md#opencode-v2-facts) as a slow-consumer counterexample. Test that a lagging presentation subscriber cannot stall authoritative ingestion. Log retention, authentication and sequence behavior remain U until exact-build qualification.

<a id="r-l-q05"></a>
## Q05. Shared configuration resolution

**P, C05.** Every surface calls the same deterministic compiler/resolver and semantic validator. Schema version, compiler/resolver version, source scopes, preset/profile IDs and complete dependency digests accompany the compiled representation. Structural validity does not establish scope subset, policy compatibility or authority.

Preserve the documented base order: built-in defaults < edition preset < installation/authority-domain < project < parent goal < task < explicit ephemeral operator override. A single “most specific wins” operator is insufficient. Ordinary preferences can override by key; authority/egress/resource ceilings narrow by an explicit meet/subset rule; plugin sets combine by stable ID with conflict rejection; credential references require explicit grants rather than preference precedence. Account/workflow/profile additions and privacy/publication partial orders remain proposed/unresolved where no accepted rule exists. Unknown or incomparable authority relations refuse widening instead of assigning an invented numeric rank.

For every field emit requested value, effective value, all contributing scopes/revisions, winning source, merge operator, constraint/refusal reasons, authority impact, lifecycle, and affected actors. Lifecycle labels are `live`, `checkpoint-applied`, `restart-required` and `goal-frozen/new GoalSpec amendment`. A preference can wait for its application boundary while a stricter authority fence immediately blocks new effects. In-flight effects retain their actual epoch and unresolved/settled evidence; settings changes are not retroactive rollback.

A configuration edit includes scope ID, expected current version/digest, candidate digest, before/after canonical values, field diff, principal/grant, authority receipt where needed, propagation choice and command ID. Compare-and-apply against the canonical current revision atomically; stale input returns the current revision and conflict, not last-write-wins. Semantic conflict detection does not rely only on edited text positions. Both documented propagation choices remain available: update outstanding sessions at their boundaries, or new sessions only; revocation fences remain immediate in both. Per-recipient compiled/validated/staged/effective states and application generation survive reconnect. A session ACK is not sufficient evidence of effective configuration, as the xDS documentation also demonstrates. [S27](https://www.envoyproxy.io/docs/envoy/latest/api-docs/xds_protocol.html)

<a id="r-l-q06"></a>
## Q06. Lifecycle performance budgets

**P, C06; all measured values U.** Budgets form a profile-keyed vector, with hard semantic zeros separated from empirical resource ceilings. Do not present unmeasured budgets as accepted SLAs. The following are required budget *dimensions*; `B_*` values are unknown until a separately admitted pilot and preregistration set them.

| Phase | Start/end points and required bounds | Hard no-hidden-work predicate |
|---|---|---|
| Startup | process invocation → first usable deterministic status/control; cold/warm p50/p95/p99 `B_start`; CPU time, reads, RSS, processes, manifest inventory | zero model calls, implicit indexing and disabled-plugin implementation activation; no full qualification suite on ordinary startup |
| Idle platform | defined no-work interval after inventory settles; CPU/RSS, disk growth, wakeups, timers, network and subscription counts bounded by `B_idle` | zero model calls and indexing; zero unrequested activation; installed-disabled activity fields remain zero |
| Idle surface | attached passive view at an unchanged source cut; per-view memory, wakeups and bytes bounded by `B_view_idle` | attach/focus/split cannot create actor, worker, model call, indexer or plugin activation |
| First use | explicit enabled feature invocation → ready admitted capability/first projection; `B_first_use`; compilation/activation/discovery reported separately | only the explicitly activated feature may incur its declared work; merely opening a view does not activate it |
| Steady state | offered event/input → accepted, appended and presented separately; `B_input`, `B_frame`, `B_append`, throughput and queue caps | added passive views do not multiply worker/model calls; canonical control is independent of rendering |
| Recovery | disconnect/crash → authenticated status, snapshot installed, interactions usable and command reconciliation; separate `B_recover_*` | no implicit effect relaunch, helper inference or fabricated settlement |

A literal zero-global-overhead claim is invalid: core metadata reads, event bookkeeping and bounded rendering consume resources. “No model call” is a tripwire predicate with observed call count zero and complete interception coverage, not an assertion inferred from a quiet screen. If instrumentation misses a path, the result is U. At zero views a synthetic protocol control client can still measure backend append/control; frame latency is **not applicable**, distinct from U and zero.

Optional plugins already admitted to execute work are different from an idle disabled plugin. Long-horizon scheduling may wake deterministic services under an explicit profile, but cannot use idle status as permission for background inference or opt-in research activation.

<a id="r-l-q07"></a>
## Q07. Latency, throughput, resize and the view matrix

**P, C06.** For continuity with R-K’s unreviewed research candidate, a future preregistration may compare these **candidate targets only**: input-to-local-echo p50/p95/p99 = 20/50/100 ms; frame presentation = 33/50/100 ms; canonical append = 5/20/50 ms, plus no more than 5 ms added-view p99 append regression. These numbers are neither measured nor accepted, and cannot be retrospectively chosen from winning results. A different profile can propose different values before a confirmatory run. Control admission/fence/remote settlement get separate budgets; none is substituted by fast local echo.

For each N=0,1,5,10,20, run idle and high-output regimes with a fixed source workload, then bounded slow-client, absent-client, crash/reconnect and resize-storm variants. Record input offered/send/admission/echo/presentation timestamps, command acknowledgment, canonical append delay, p50/p95/p99 frame latency, accepted events/s and bytes/s, CPU/RSS/wakeups/IPC/disk, handles/processes, queue high-water, coalesced frames, projection gaps and canonical event retention. Report per-view and whole-system totals rather than multiplying shared RSS. Keep native terminal and later GUI workloads separately identified.

High output is a preregistered offered rate, byte-size/event-class distribution and burst schedule, not simply “as fast as possible.” Below the declared sustainable profile, all mandatory events must persist and bounded queues must drain after the burst. Above it, report admission throttling/refusal and time in overload; no silent durable loss or boundless growth is allowed. Throughput is accepted durable throughput as well as offered rate; throughput of discarded redraw frames is not useful work. Unknown capacity stays U pending a sweep; a sweep informs later frozen confirmation, not a guaranteed universal threshold.

Resize: validate dimensions and resize lease; bound pending resize intents; coalesce presentation-only geometry to the latest valid revision without losing the receipt/audit of accepted control intents. Record rendered geometry revision and preserve correct input target during rapid resize, focus changes, wide Unicode, combining sequences and partial escape frames. Bounded stale layout can be shown as pending; out-of-order resize must not overwrite the newest applied geometry. No full-history redraw per token. A renderer may skip intermediate frames, but never replace an unpersisted command/lease/exit with a synthetic final state.

Report a full vector and Pareto tradeoffs under OR-024: hard correctness/authority/privacy/resource/recovery floors first, then responsiveness, subscription efficiency and completion. No weighted scalar conceals a slower Stop or missing receipt. Provider-free trials measure zero-model infrastructure and do **not** estimate subscription savings.

<a id="r-l-q08"></a>
## Q08. Reproducibility and exact budget falsifiers

**P, C06.** Freeze before outcomes: candidate/artifact and catalog/schema hashes; OS build/kernel, architecture, terminal build and features, local filesystem, host/VM resource limits, renderer and sink/drain behavior, Unicode/font/input mode, workload and generator hashes, event rate/distribution, N and layout, route profile/stub, config revision, plugin enabled/disabled state, source retention policy, queue caps, instrumentation version, sampling overhead and cold/warm order. D-028 strata are Windows 11 25H2 build 26200 Home/Pro, 24H2 build 26100 Enterprise, x64; Linux 6.12 LTS primary and 6.6 compatibility with cgroup v2/ext4; WSL2 ext4 and `/mnt/c` are separate development/test strata, not production evidence. Exact builds must be recorded rather than inferred from a family name.

Use an independent open-loop offered schedule for load; record generator lateness, omitted sends, refusals, timeouts and censored requests. Otherwise blocking the generator can make latency look artificially good. Use monotonic local durations; remote observations retain clock-domain/uncertainty rather than subtracting incomparable wall clocks. Freeze quantile method, sample inclusion, run unit, repetitions, pilot/held-out separation and confidence calculation. Store raw bounded samples and separate instrumented/uninstrumented cost. One run’s requests are nested observations, not independent tasks or independent hosts.

**Exact falsifiers:** one unexpected model/index/disabled activation fails its hard zero predicate; any canonical-event loss, duplicate effect or input misrouting fails correctness; memory/queue above the preregistered hard ceiling or backlog that does not drain under the declared recovery schedule fails boundedness; an observed p99 above its frozen bound fails that budget regardless of the mean. A confidence claim requires its preregistered interval/margin and sample adequacy, not one passing quantile. Missing instrumentation, unspecified numeric resource/time limits or unpinned workload blocks a performance conclusion. No p99 can be meaningfully reported from insufficient data by silently treating missing tail samples as zero.

<a id="r-l-q09"></a>
## Q09. Themes, keybindings, layouts, profiles and canonical configuration

**P, C07.** Presentation configuration is declarative data: semantic color/style tokens plus contrast intent; key chord → command/version + explicit arguments + context predicate; layouts as bounded view trees with stable view/projection references; profile references to versioned sets of settings and capability requirements. Themes contain no executable expressions. Layouts do not spawn actors. Keybinding collisions, unreachable controls and ambiguous prefixes are explainable validation outcomes; no key combination obtains authority through being configured. Accessibility preferences, text scaling, reduced motion, focus indicators and non-color state labels are explicit settings.

Human input compiles to one typed, restricted canonical representation. Preserve source text/comments separately if desired; the effective semantic digest hashes canonical values and relevant schema/compiler identities, not comments or whitespace. JCS sorts and serializes data; it does not normalize Unicode or lowercase filesystem paths. Distinguish Unicode-equivalent-looking strings and platform path aliasing until field-specific semantics resolve them. M1B remains its exact restricted profile; a future configuration schema may define its own admitted numeric domains without changing M1B. Decimal quantities can use integer units or explicitly typed decimal strings if selected later; floating-point rounding must not change authority/budget comparisons.

| Human/machine syntax candidate | Useful property and cost | Decisive rejection case; non-proof |
|---|---|---|
| Restricted JSON + separate commentary/source metadata | Direct alignment with JSON data model; more verbose human editing and no standard comments | duplicate collapse or inconsistent numeric/string handling; parser simplicity does not prove usability |
| TOML 1.0 frontend → same canonical model | Familiar tables/comments; date/time and numeric values need an explicit admitted mapping; repeated definitions are invalid | two valid spellings compile differently or unsupported type coerces silently; successful round-trip does not prove complete profile usability |
| Restricted YAML 1.2.2 frontend → same canonical model | Rich human structure; tags, aliases, implicit resolution and duplicate handling require restrictive policy and resource bounds | alias expansion, custom tag, duplicate or implicit scalar changes meaning; schema safety does not establish parser security |

No syntax is selected. These comparisons follow the published TOML and YAML type/structure rules, not measured editor behavior. [S18](https://toml.io/en/v1.0.0), [S19](https://yaml.org/spec/1.2.2/)

Source-free derived config still needs a reversible provenance mapping. Formatting-preserving editor output is not canonical authority. A GUI can update the same source document or produce the same transaction through a compiler; it cannot save secret parallel widget settings that alter runtime behavior.

<a id="r-l-q10"></a>
## Q10. Inspect, preview, apply and rollback

**P, C05/C07.** `inspect` reads the current effective revision, provenance and pending applications. `preview` validates a proposed edit, returns before/after diff, affected actors, capability/authority/billing/privacy changes, application boundaries, new dependency requirements and reversible portions. Preview is pure and creates no effects; its result binds the inspected base revision and policy. `apply` repeats current validation and uses compare-and-apply, persists the new revision/receipt, fences restrictive authority changes and stages per-recipient updates. `rollback` is a **new admitted revision** restoring eligible prior values, not a decrement of authority epochs or a claim to undo external effects.

A reverse diff is only structurally reversible. Removed plugin binaries, changed provider capabilities, new schema migrations, spent reservations and already dispatched effects may make full restoration impossible. Preview labels exact unsupported rollback portions and requires current compatibility/authority checks. An old credential reference can never be reactivated merely by rolling back a theme. Lost apply reply requires receipt lookup with the same command ID.

Terminal, editor and CLI edits carry the same expected digest. If A and B preview R7 and A applies R8, B’s apply of R7 is rejected; B can fetch R8, explicitly rebase its diff and preview again. File watchers may report an external edit as a candidate, but may not convert file arrival into policy widening. Partial per-recipient application stays visible; a presentation update can succeed while a restart-required field is pending. New children bind configuration at canonical SessionId creation order, and resume revalidates grants/current policy. Revocation is never hidden by later preference coalescing.

For an optional HTTP adapter, `If-Match` is a useful conditional-update mapping, but application revisions, atomic validation and durable receipts remain necessary. The server’s exact expected-digest behavior cannot depend on whether an editor used HTTP. [S28](https://www.rfc-editor.org/rfc/rfc9110.html#name-if-match)

<a id="r-l-q11"></a>
## Q11. G-09 configuration conformance corpus

**P, C08.** Each fixture records ID/version, input bytes and syntax/dialect, schema/compiler/resolver/migration identities, platform profile, complete scope graph, actor/session states, grant/fence context, expected canonical output bytes/digest or typed rejection, field provenance, effect-attempted value, application boundary/recipient receipts, complexity vector and independent oracle provenance. Synthetic paths and opaque references replace real accounts and data. Never fetch remote schema references during ordinary validation; dependencies are locally pinned and bounded.

| Corpus class | Required positive and negative cases; exact oracle |
|---|---|
| Round-trip | each valid surface/human form → canonical → supported editor form → canonical yields identical semantic bytes/digest and effective provenance where scope is unchanged; comments may differ only outside semantic state |
| Duplicate key/definition | duplicate JSON names, quoted/unquoted TOML equivalents and YAML duplicates fail before object collapse; no last-key-wins |
| Types and bounds | booleans versus integers, missing versus null, integer bounds, unit strings, date/time, unknown fields, excessive nesting/size, unsupported tags/aliases; exact rejection code and zero effect attempts |
| Normalization | UTF-8 validity, composed/decomposed Unicode, BOM, surrogate errors, newline/comment differences, key sort order and platform path cases; only declared equivalences share digest; unauthorized normalization fails |
| Invalid combinations | route unsupported/unknown; plugin dependency/cycle/collision; incompatible enabled profile; contradictory lifecycle/update mode; deterministic sorted explanation, no partial activation |
| Scope subset | parent permits {A,B}, child {A} passes; child {A,C} fails without exact widening receipt; empty-set meaning is field-specific; revoked grant and unknown/incomparable privacy/publication rule fail closed; independent finite-set oracle |
| Concurrent edits/application | same-base racing updates accept at most one; reconnect generation rejects stale effective receipt; new-only/outstanding propagation exercised for active, queued, idle, suspended and new sessions |
| Migration/rollback | supported forward transform gives pinned expected revision; unsupported version refuses; reverse transform is new revision with monotonic fences; irreversible portions are explicit, not guessed |
| Disabled/lazy configuration | view/profile reference to disabled plugin performs no code import/activation/indexing; core inventory metadata cost remains separately observable |
| Cross-platform | identical portable fixture produces identical canonical bytes/errors at both Windows floors and Linux kernels; platform-specific path cases have declared different results; WSL cases are separate dev evidence |

Cover core/standard/remote/full/custom manifests with pairwise and three-way combinations plus targeted high-consequence interactions. Coverage is reported, not claimed exhaustive. A deny-all resolver fails the positive subset/ordinary preference cases. Privacy exposure and publication authority need an accepted partial-order/subset definition before those cells can be considered executable qualification; until then fixtures are **blocked-definition**, not zero coverage or pass. Field shape and corpus can be specified now without inventing that Owner policy.

The complexity vector reports field count, scope levels, cross-field constraints, lifecycle transitions, authority/billing/privacy edges, plugin/provider/model/host conflicts, invalid-combination classes, explainable-rejection coverage, valid round-trip coverage and migration/rollback coverage, plus parser depth/bytes and resolver work. Measured resolution time, memory, corpus coverage totals, real editor round-trip fidelity and all platform pass counts are U. Generated fixture counts alone cannot close G-09. No human syntax decision is made.

<a id="r-l-q12"></a>
## Q12. Replaceable integration contract

**P, C09.** `IntegrationBinding` declares adapter identity/version/digest, endpoint/profile, semantic catalog and schema compatibility, principal/read audience, allowed commands, optional input/resize leases, privacy/notification policy, bounds, lifetime owner, cursor/receipt persistence, capability loss and disabled behavior. It carries credential references only where already authorized; presentation clients do not receive credential bytes. Removing any optional integration leaves deterministic core status/recovery and other clients working. A runtime-owned adapter connection must also be independent of detachable views; the [Muse lifecycle facts](../rk/report.md#muse-lifecycle-facts) supply a counterexample, not a required architecture choice.

| Integration | Mapping and ownership boundary |
|---|---|
| Shell and one-shot CLI | Explicit args compile to typed intent; machine output is structured, stdout payload separated from diagnostics; exit code maps a typed receipt/error, never parses chat; shell completion is bounded catalog lookup without inference |
| Neovim | Optional command/buffer/view adapter translates explicit editor target into canonical IDs; RPC function metadata helps version checks, but no buffer text or RPC connection grants authority; avoid evaluating arbitrary received commands |
| VS Code | Optional command/palette/tree/webview adapter resolves menu/selection context explicitly, validates argument schema and submits the same intent; UI visibility is not admission; no trusted command URI from untrusted output |
| tmux | Attach/capture/control-mode adapter can host projections or a terminal client; pane IDs are presentation locators, not actors/leases; tmux pause/capture is not canonical replay |
| Zellij | Optional pane/plugin adapter asks only necessary permissions and maps typed actions; pane input permission does not authorize Recursion effects; disabled Recursion plugin remains inert despite host capability |
| OSC/shell integration | Presentation hints from a separately gated encoder; title, notification and prompt-region observations never create goals, approvals or effective config |
| MCP | Profiled tool/resource adapter maps method arguments/results to the shared catalog, admission and projection service; protocol request/task IDs are transport correlation; one canonical effect/receipt owner |
| Notifications | Read-scope-filtered attention projection; rate/dedup/expiry policy; an activation opens a specific current interaction or submits an explicitly confirmed typed command; click receipt is not approval |

No adapter is mandatory. The native loop and upstream adapter both expose the same canonical interface while preserving exact route-specific capability loss. A supported native helper is never silently invoked to make an upstream-only status or control work. Five navigation destinations remain Work, Attention, Artifacts, Environment and Settings/recovery with a command palette; this is presentation architecture, not five new backend stores.

**P:** bind the integration to the [canonical MCP era/identity](../protocol-edges/report.md#era-and-identity), [tool facts](../rg/report.md#1-r-g-q01-importability-matrix), and [stdio/cancellation profiles](../protocol-edges/report.md#cancellation-and-asynchronous-tasks). Separate authenticated authority from peer claims; bound schema work and prohibit implicit network resolution. Admit every sampling helper independently. The companion MCP fixtures cover continuation and cancellation; protocol observations never substitute for effect settlement.

<a id="r-l-q13"></a>
## Q13. Safe OSC, shell and editor/MCP actions

**P, C10.** Treat upstream output, terminal replies, titles and notification bodies as untrusted data. The platform does not forward arbitrary escapes to the controlling terminal. A bounded parser maintains state across fragments, validates the specific terminal/profile allowlist, rejects overlong/unterminated/control-bearing fields, and re-encodes known-safe presentation messages through the sole renderer writer. Rejecting a sequence must return to a known parser state without concatenating its remainder into an executable escape. Shell prompts, paths, command strings and current-directory reports are tainted observations, never executable code or authority.

| Sequence family | Documented purpose | Candidate safe disposition |
|---|---|---|
| OSC 0 / 1 / 2 | xterm icon/window title changes | opt-in escaped bounded neutral label; no secret/task content by default; title queries/replies cannot be treated as user input |
| OSC 9 | iTerm notification; the same family also has progress subforms | allow only explicitly profiled subgrammar; notification support does not permit every OSC 9 extension |
| OSC 99 | kitty notifications, optional focus/action/close replies and capability query | minimal text notification by default when enabled; identifiers are audience-scoped; replies route only to notification correlation, never stdin/approval; richer actions require separate mapping |
| OSC 777 | WezTerm documents rxvt `notify` extension | permit only that exact supported grammar in its declared profile; no blanket permission for all 777 protocols |
| OSC 133 and selected shell metadata | prompt/input/output region hints | optional bounded presentation parsing; does not prove command success, current worktree or authenticated shell ownership |
| OSC 52 / file transfer / arbitrary hyperlink or command extensions | can touch clipboard or additional terminal features | rejected in this integration profile unless a separately authorized, reviewed capability exists; never inferred from notification permission |

[S11](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html), [S12](https://iterm2.com/documentation-escape-codes.html), [S13](https://sw.kovidgoyal.net/kitty/desktop-notifications/), [S14](https://wezterm.org/escape-sequences.html)

Terminal-specific support is negotiated or explicitly configured; an environment variable is a hint, not proof of safe support. Notifications may reach an OS lock screen or another viewer, so filtering and user-selected disclosure rules apply before emission. Bounded titles and counters can still leak existence/timing; secret-free text does not imply zero information leakage. No clipboard read/write, credential query, environment dump or shell command is smuggled through an escape sequence.

Editor command handlers validate args even when a palette hides them. Untrusted Markdown cannot enable VS Code command URIs. MCP tools map to the same operation/version and exact effect digest; retyping data as a tool request does not turn it into an authorized command. A plugin can propose an action but cannot return `approved=true` and become the principal. Pure notification activation is a navigation event; approval requires current correlated interaction and exact bounds.

<a id="r-l-q14"></a>
## Q14. Slow/hostile clients, control reserve and Stop

**P, C11, preserving D-022.** Every view has bounded bytes/events, bounded query work/page sizes, a deadline, cancellation and a reconnect policy. Decoding and subscription admission have global as well as per-client quotas; per-client limits alone allow unlimited clients to exhaust the platform. Slow clients are isolated/disconnected or resynced without blocking canonical append. Absent clients do not become durable queue owners. A hostile authorized reader still receives only its audience and cannot force unbounded replay, expensive filters or unlimited snapshots.

A reserved control path includes: bounded authenticated ingress; framing space not consumed by an unfinished bulk frame; independent reader/decoder work; scheduler slots; admission/fence processing; canonical-write capacity; and bounded receipt delivery. Bulk data cannot hold an unbounded global lock or run callbacks inline on the control pump. Compare physically separate channels with demonstrably reserved logical scheduling on a shared transport; neither wins without the saturation fixture. On storage exhaustion, the system must refuse new effect admission and truthfully expose recovery/control limitations. This report does not assume a durable fence can always be written to a full/failed disk. A preallocated reserve or alternate emergency mechanism is a candidate to test, not an established property or store choice.

| Control | Visible scope and result |
|---|---|
| Aggressive Stop | selected agent; fence new selected-agent dispatch and force interruption without waiting for current operation; descendants and uncertain effects separately listed |
| Full Stop | selected agent plus owned subagents/shells/monitors/relaunchers; fence return/restart; list per-host/per-process settled or unresolved observations |
| Lazy Stop | close admission and wait for named observable operation/checkpoint boundary, explicit deadline and escalation; never infer a hidden reasoning boundary |
| checkpoint / interrupt / drain | expose the accepted operation/policy terms with target and boundary; none substitutes for mode/scope or promises external rollback |
| detach / close / reconnect | subscription/presentation lifetime only; no Stop, relaunch or effect resume implied |

The canonical requested Stop, installed admission fence, sent upstream interrupt, observed owned-process exit, remote receipt, external-effect settlement and final verification are separate facts. An offline host remains unresolved. A user sees the actual scope before acting; no surface aliases Ctrl-C ambiguously among draft editing, detach and Full Stop without a configured explicit context/confirmation. Kill/close/daemon controls cannot silently expand from one session to unrelated work sharing a process.

Frozen M1B’s process experiment still names `current-immediate` and representable future policies; D-022 vocabulary does not authorize rewriting those bytes. Full implementation requires a reviewed new/refined mapping. D-020’s writer takeover plugin is orthogonal to view lifetime/input leases; old writer epochs remain fenced on reconnect. A separate OS containment/launch proof is needed for actual termination and D-029 credentials, not supplied by this interface candidate. Apply the [canonical ConPTY lifecycle facts](../rk/report.md#conpty-lifecycle-facts), with build-scoped close behavior, independent I/O servicing and separate drainage/owned-process settlement evidence.

<a id="r-l-q15"></a>
## Q15. Competing platform shapes and recommendation register

All options below remain live comparison candidates where consistent with accepted requirements. “One semantics” is required; whether code or processes enforce it remains unselected.

| Choice | Option and genuine competitor | Decisive falsifier | What passing would not prove |
|---|---|---|---|
| Placement | In-process semantic library vs daemon with thin clients | library clients cannot share current canonical receipts/fences without divergent writers, or daemon attach/round-trip blocks required offline/local control | language safety, isolation, performance or easier deployment |
| Placement | Daemon protocol vs hybrid embedded local control plus shared service | service absence makes adapter-free deterministic recovery impossible, or hybrid creates a second admission/receipt store | a daemon is inherently secure or a hybrid inherently faster |
| Placement | Hybrid vs both single-placement alternatives | same operation yields different preconditions/receipts depending on invocation path | reduced complexity or maintenance effort |
| Projection delivery | push subscriptions vs bounded pull at explicit cuts | push slow subscriber blocks writer/Stop, or pull cannot meet declared freshness/CPU bounds | universal latency/efficiency or reliable remote delivery |
| Projection delivery | push invalidation + pull snapshot vs direct deltas | lost invalidation leaves a view falsely current, or snapshot churn violates profile bounds | correctness without cursor/freshness checks |
| Configuration storage | one source document with typed presentation section vs split presentation/runtime documents compiled together | unified editing creates authority conflicts from layout changes, or split edits yield impossible effective combinations | usability, easiest merge behavior or stronger privilege isolation |
| API description | semantic schema/catalog with optional binding descriptions vs HTTP-first OAS model plus verified non-HTTP adapters | a required operation/error/streaming semantic cannot be represented losslessly across the bindings | choosing HTTP, JSON-RPC, a code generator or a transport |

### Candidate recommendations C01–C12

| ID | Candidate / competitor | Decisive falsifier and non-proof |
|---|---|---|
| C01 | one semantic catalog with generated surface mapping / independently implemented mappings checked against one corpus | an argument/target/error meaning differs or one control requires an admission bypass; pass does not establish usability or generator correctness beyond corpus |
| C02 | snapshot-bound reconstructable typed projections / direct canonical read queries with equivalent typed results | equal scope/cut produces different facts, unknown becomes zero, or revocation permits a new denied disclosure or fails the declared controlled-cache policy; prior disclosures and offline/uncontrolled copies remain explicit residuals. A pass does not prove retroactive erasure, query capacity or absence of side channels |
| C03 | metadata-only disabled contribution registry / precompiled inert contribution bundle separated from executable activation | either loads code/registers active behavior or spends while disabled; pass does not prove third-party isolation, licensing or cheap import |
| C04 | durable interaction/receipt records plus verified snapshot replay / query-reconstructed interaction state from canonical events without separate materialization | reconnect duplicates/retargets answer, invents a replay gap or acknowledges uninstalled state; pass does not prove remote exactly-once effects or storage durability |
| C05 | canonical compare-and-apply resolver transactions / serialized single-editor ownership with the same semantic validation | stale edit overwrites current state, or revoked authority survives preference coalescing; pass does not settle privacy/publication policy or external rollback |
| C06 | full-vector phase budgets and fixed offered load / matched sequential human-workflow measurement plus resource traces | attractive mean hides tail, censorship, durable loss or hidden work; pass does not prove human preference or subscription savings |
| C07 | declarative presentation data compiled with runtime config / separately stored presentation data joined under shared versions | a theme/layout/keybinding changes effect authority or yields different canonical meaning; pass does not select human syntax or ensure accessibility |
| C08 | cross-platform golden/negative corpus with independent oracle / differential independent resolvers plus targeted goldens | deny-all passes, duplicate semantics vary or authority comparison lacks a defined oracle; pass does not cover all combinations or hostile parsers |
| C09 | optional typed integration adapters / minimal CLI subprocess bridge with structured I/O | an integration requires a second policy store, owns actors through its view or widens credential visibility; pass does not qualify a real route or entitlement |
| C10 | parse-and-reencode OSC subset / suppress all OSC and use native optional notification adapter | disallowed escape changes terminal/clipboard, reply becomes input/approval or secret reaches notification; pass does not prove every emulator or screen privacy |
| C11 | separate reserved control route / shared transport with measured end-to-end reservations | bulk/partial-frame/slow-sink overload delays fence indefinitely or loses mandatory observation; pass does not guarantee control under arbitrary OS/disk failure |
| C12 | TUI-first backend contract fixtures followed by GUI binding parity / parallel CLI/TUI/GUI prototypes over the same catalog | delayed GUI reveals a required canonical fact/control cannot map, or parallel work diverges semantics | GUI release timing, accessibility, port cost or fastest schedule |

C12 is construction sequencing, not a waiver of comprehensive release requirements. Owner decisions remain: exact GUI timing interpretation; production protocol/version/rollover decisions; accepted config privacy/publication lattice; numeric profiles after evidence; and eventual technology selections after the required experiments. No closed D-018–D-033 choice is reopened.

<a id="r-l-q16"></a>
## Q16. Falsifying “one meaning on every surface” and bounded non-proofs

The headline claim fails if any of these is observed at the same schema, capability profile, authority context and source cut: a command cannot be represented with the same targets/arguments; a surface supplies a hidden default affecting authority/effects; `steer` becomes queue; Stop changes scope; an error changes whether an effect may have occurred; a GUI-only field becomes canonical; an editor bypasses admission; an enabled plugin requires direct mutable kernel access; a disabled view activates implementation; or reconnect changes the identity of an outstanding interaction. “It looks the same” and “it shares source code” are not alternative oracles.

Capability-driven differences are truthful only when explicit: unsupported or unknown route controls remain unavailable with exact reasons, while core semantics do not change. Equal-authority clients can present richer or simpler forms; the machine representation remains inspectable. Commands containing authority changes cannot be replaced by natural-language prompt injection. A hidden native model used to repair an upstream-only workflow also falsifies the accepted architecture, even if the UI appears continuous.

**P:** use the [canonical accessibility criteria](../rk/report.md#wcag-criteria-facts) for future GUI acceptance and TUI research. A schema can carry semantic names, roles and status; rendered assistive-technology behavior, reading order, focus, scaling, contrast and interaction usability require separate tested profiles.

This candidate explicitly proves none of: measured performance advantage; useful accessible experience or WCAG conformance; a security boundary between views; credential non-access; complete lifecycle containment; all-harness parity; qualification, entitlement or legal clearance; external exactly-once/rollback; correct current installed builds; reduced porting effort; productive-continuity superiority; subscription savings; or that every host/environment input can be reconstructed. Counters that have no source remain U, not zero. D-031 excludes vendor-intent claims altogether.

<a id="r-l-q17"></a>
## Q17. Provider-free acceptance fixtures and local handoff

The complete procedures are in `unexecuted-local-handoffs.json` and `unexecuted-local-handoffs.md`. No runnable entrypoint is claimed: a unified interface implementation and independent corpus runner have not been verified. Repository probe scripts are historical reference material, not authorization to execute them. All fixtures require a separately authorized disposable local environment, pinned candidate and oracle, synthetic records only, disabled external networking/provider routes and complete observability. Define finite memory, bytes, time and teardown limits before starting; missing bounds block the run.

| Fixture | Exact pass/fail predicate |
|---|---|
| F01 Cross-surface query/command parity | same source cut/audience/version yields identical canonical query bytes and semantically identical command targets/arguments/preconditions/errors through CLI/TUI/GUI-stub/editor; any undeclared difference fails; same-ID retry produces one accepted effect |
| F02 Disabled plugin inertness | installed-disabled metadata may be read within declared inventory bound; all implementation imports/payload scans/processes/threads/timers/watchers/network/credential reads/context injection/tool registration/subscriptions/quota/spend/index/model activity are zero; core placeholder renders without activation |
| F03 Stale config/concurrent apply | two edits based on R7 result in at most one R8 acceptance; loser receives typed conflict with no mutation/effect; rollback is new revision and does not resurrect revoked authority |
| F04 RESET/GAP and real snapshot | genuine lost prefix below floor requires immediate RESET and fresh CREDIT; every forbidden intervening M1B message produces its exact refusal; forged floor/snapshot fails independent fact oracle; no missing story is synthesized |
| F05 OSC allowlist | all split/malformed/overlong/disallowed OSC payloads produce no forbidden terminal/clipboard/command effect and parser resynchronizes; permitted notification is escaped, scoped and receives no approval authority |
| F06 N-view soak | all 0/1/5/10/20 idle/high-output cells obey frozen queues/resources and tail budgets, lose zero mandatory canonical events, preserve actor/process counts and add zero inference/index/activation; frame metric at N0 is not applicable; any unknown required measurement blocks a pass |
| F07 Control reserve | Stop admitted/fenced within frozen bound while each ingress/framing/read/scheduler/writer/projection stage is independently and jointly saturated; external effects remain honestly unresolved; failure at any stage fails profile |
| F08 Interaction generations | duplicate answer/reconnect and stale answer after waiter replacement yield one valid current response and zero cross-generation releases; changed action digest cannot reuse approval |
| F09 Input/resize ownership | observer, wrong lease, stale process/daemon epoch and focus-steal attempts are refused; valid owner input/resize works; authenticated Owner Stop still works without input lease |
| F10 G-09 corpus | exact canonical bytes/provenance/rejection/application receipts match independent goldens across declared profiles, including round-trip/type/duplicate/normalization/subset/migration classes; any undefined lattice cell remains blocked-definition |
| F11 Capability/lifecycle change | route/plugin/config support changes invalidate old affordance state; stale invocation fails server admission, not just UI hiding; unsupported steering never becomes queued input |
| F12 Detach and connection ownership | close every view and reconnect without increasing launches/actors/model calls or closing runtime-owned adapter session; pending receipts/interactions survive; explicit Stop remains a separate effect |
| F13 Audience/cache revocation | change read scope while a slow/offline view holds a snapshot; no new denied bytes or query detail is disclosed, resume requires current audience validation, stale cache is marked/removed per policy; prior lawful disclosure cannot be claimed undone |
| F14 Recovery honest state | crash after accepted/dispatch/possible effect but before reply; stable operation ID and ledger preserve ambiguous status; recovery queries do not duplicate synthetic effect or invoke a helper model |
| F15 Accessibility semantics | equivalent control names/status/keyboard paths/focus-order requirements are present in independent surface adapters; failures are explicit; this is schema/navigation screening only and cannot certify WCAG/assistive technology |

Each fixture includes positive completion cases as well as negative rejection. A design that rejects every command cannot pass. The independent oracle derives expected facts from a frozen event schedule and separate synthetic effect/terminal sink, not from the candidate reducer or its self-reported “success.” Preserve attempted and refused inputs, raw bounded transport records, canonical receipts, installed cursors, scope/fence/application revisions, resource samples and observer-loss reports. A missing final counter is U.

Stop on unexpected external network/provider access, a real credential/account/path, authorization widening, observer loss, impossible teardown, unbounded queue, or hard deadline/resource exhaustion. Preserve available evidence and fail/mark unknown as appropriate; never retry into a pass by dropping a case. Deliberately injected failures are expected only in named negative controls. A broken positive control or oracle halts the campaign. Do not kill unrelated processes or alter security settings. Completion is the finite frozen trace/observation window and settled synthetic teardown, not an arbitrary green badge.

### Construction handoff and decision leverage

C12 proposes closing F01/F03/F08/F09 first because they expose semantic drift before a toolkit can hide it. Run F04/F07/F12 alongside backend construction because replay, control reserve and lifetime cannot be retrofitted by a prettier UI. F02/F10/F11/F13 protect comprehensive opt-in configuration. F06 measures the resulting profile only after workload/bounds are frozen; F15 begins with semantic coverage but later requires real accessibility sessions. These are ordered local research/qualification handoffs, not commands executed or an approved release reduction. R-K supplies terminal substrate details; R-J supplies conversation/coordination details; both remain research candidates until independently reviewed. R-L adds the common semantic services and does not create a new executive or state owner.

## Completion gates and audit disposition

G01 → Q01/Q02/Q16/F01: one semantic catalog, errors, receipts, negotiation and explicit cross-surface demonstration; specification answered, execution U.  
G02 → Q02–Q05/Q14: backend projections/streaming/status/config/contributions and authority boundaries; append before coalescing; implementation U.  
G03 → Q06–Q08/F06/F07: phase and latency/resource vectors, all view counts, resize/load/freeze rules; measurements U, candidate targets not SLAs.  
G04 → Q05/Q09–Q11/F03/F10: compiled configuration, all presentation classes, transactions, stale rejection and G-09 corpus; syntax unselected, unresolved lattices explicit.  
G05 → Q12/Q13/F05/F09/F12: every named integration is optional with no lifetime/authority or credential widening; qualified behavior U.  
G06 → Q15: all required platform shapes/projection/config alternatives, falsifiers/non-proofs, no selection.  
G07 → Q17 and full handoffs: mandatory six fixture families plus nine safety/continuity extensions; UNEXECUTED.  
G08 → C01–C12 and machine recommendation register: competitors/falsifiers/non-proofs and no technology/route choice.  
G09 → Q16: explicit non-establishment of performance/accessibility/qualification/entitlement/security-between-views/port-cost claims.  
G10 → artifact QA: source baseline read-only; no credentials/auth files read; no protected/repository files modified by this lane; delivery text scanned for accidental private workspace/capture paths and credential patterns. This is bounded artifact hygiene, not a universal secret-detection proof.

The coverage register contains all 17 questions and all 10 completion bullets with exact supplied text and locators. Full source register provides URLs, retrieval date, versions/pins, local-source hashes and limits. Mutable public pages are date-pinned observations, not immutable source commits; no excerpt hash is mislabeled a page hash. Independent review and all target execution remain outstanding.

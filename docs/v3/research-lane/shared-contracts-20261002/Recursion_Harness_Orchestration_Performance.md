# Recursion Harness Orchestration Performance

Additive research companion for Lucas · 2026-10-02 UTC

Repository basis: PR 147 merge `5b55e55a103fad2d82d625983080b39f2db21c0e`, tree `c5efe438a91b15a318fb0ed70d1488cb51c30034`. Parent goal: `goal-recursion-v3-harness-orchestrator`.

Status: source-grounded comparison and **unexecuted** local benchmark handoff. No technology or vendor is selected, no route is qualified, and no latency, throughput, resource or subscription advantage has been measured here.

## Conclusion

The strongest candidate for Recursion is **one Recursion-owned semantic boundary with route-specific structured adapters, and bounded reuse of eligible harness processes and sessions**. Prefer the richest supported interface that preserves the particular workflow’s controls, evidence and accounting. That interface can be ACP. Where an upstream has a materially richer native app-server or SDK control surface, retain it rather than forcing its semantics through an extra compatibility layer. Use structured headless CLI modes for workflows they actually support. Keep terminal emulation and text parsing a separately qualified, visibly limited path.

The genuine rival is **ACP-first normalization**, with first-party ACP implementations wherever available and explicit versioned extensions or bridges elsewhere. It could win on integration effort, shared conformance machinery and whole-product maintenance while matching response latency. There is no evidence here that an ACP frame is intrinsically slower than a native JSON-RPC frame, or that an API beats a CLI subprocess. ACP itself commonly runs over subprocess stdio. A native API, an ACP adapter and a structured CLI can all front the same long-lived process.

For the accepted first qualification target, continue **Codex App Server first under D-023**. That decision establishes order, not measured superiority or an approved operating profile. Compare its exact admitted structured path with a semantically equivalent challenger. Do not manufacture an ACP Codex route, or turn an unavailable or unqualified route into a slow benchmark result.

Three discriminators matter more than the protocol label:

1. **Same workflow, same implementation boundary:** what extra parsing, copying, IPC, journaling and callback work does the adapter add?
2. **Same route, different residency:** is avoiding repeated launch, initialization and context restoration worth the idle resources and larger failure domain?
3. **Same semantics under pressure and interruption:** do control, durable evidence, honest meters and productive recovery still work when the output consumer stalls or a receipt is lost?

Actual p50/p95 and safe concurrency remain **unknown for every candidate**. The next useful evidence is the small provider-free contrast in this report, followed only under separate admission by exact-build upstream conformance and real-workload qualification. A fast synthetic peer is evidence about the proposed integration path, not the upstream harness or provider.

## Scope and existing work

This builds on the current repository rather than replacing its architecture or repeating its route survey. The read-only source export was supplied as complete and byte-verified against the merge commit above. Earlier reports retain their historical `73d70505b8c266fbb08d820d304ebd2e68ac7f1b` provenance; inclusion in PR 147 does not make their unexecuted fixtures into observations.

The governing constraints are CONTROL_PLANE, ANCHOR, AGENTS, PRODUCT, INTERFACE-STRATEGY and D-018 through D-033. In particular:

- Native execution and upstream-only execution remain independently useful first-class requirements; an embedded vendor loop is still an upstream loop
- Comprehensive capabilities remain built and opt-in under D-019; a cheaper default is not permission to omit them
- D-021 and D-030 preserve harness-native delegation without ungranted credential custody
- D-029 requires the operator-provisioned trusted launch boundary for the strong delegated-credential claim
- D-022 fixes Aggressive, Full and Lazy Stop, plus checkpoint, interrupt and drain
- D-024 makes productive continuity the outcome, with authority, evidence and honest accounting preserved
- D-028 platform floors and D-027 counsel/route clearance remain gates; no research recommendation supersedes them
- D-033’s porting-economics hypothesis remains unmeasured

The report adds a topology taxonomy, a route-qualified strategy comparison, a latency decomposition and a minimally discriminating handoff. Existing owners remain:

| Existing research | Reused responsibility | Additive question here |
|---|---|---|
| [R-E trusted launch][R-E] | Credential-facing domain, tool domain, provisioning and strong-boundary falsifiers | What launch and isolation costs must every eligible comparison include? |
| [R-F delegation][R-F] | Per-harness controls, native fan-out, spawn/effect settlement and meters | Which adapter and residency contrasts distinguish performance without changing those semantics? |
| [R-I Grok analysis][R-I] | Concrete ACP implementation, extensions, session actors and portability limits | Which implementation costs are hidden by the common ACP label? |
| [R-L interface contract][R-L] | Shared command meaning, bounded streams, control reserve and view independence | How must orchestration avoid coupling output or UI lifetime to control? |
| [R-O performance program][R-O] | Full vector, budgets, statistics, classifier and complete-profile confirmation | What smallest new experiment distinguishes direct structured, ACP, bridged and one-shot paths? |
| [Protocol edges][R-PROTOCOL] and [model architecture][R-MODEL] | Effect identity, one retry owner, protocol observations and canonical authority | How do adapter conveniences preserve these invariants? |

Evidence labels used below: **D-public** is a primary public source statement; **D-repository** is a pinned repository requirement or recorded analysis; **Proposal** is this report’s inference or experimental design; **Unknown** requires evidence not collected here. Static file inspection and artifact QA are the only local observations. No named harness, repository script/test/import, provider, model, authentication flow, account, live host or Work/Codex/cloud session was invoked. No installation, credential inspection, spend or repository mutation occurred.

## What is actually being compared

ACP here means **Agent Client Protocol**, confirmed by the repository’s Gemini, Cursor and Grok route references and the primary specification. It is not MCP and is not a generic name for multi-agent coordination.

Keep five independently versioned layers separate:

1. **Semantic contract:** Recursion’s goals, operation identity, authority, receipts, Stop, evidence and meters
2. **Upstream control interface:** ACP, a harness-native app-server API, an SDK’s control stream, structured CLI events or a text terminal interface
3. **Transport and codec:** stdio JSONL, an HTTP event stream, WebSocket framing, a local socket or terminal bytes
4. **Implementation and topology:** native ACP implementation versus an ACP bridge; one process per invocation versus reusable sessions; shared versus isolated helpers
5. **Qualified route:** exact executable/build, adapter, schema, method set, extensions, configuration, host, model/provider, account class, credential boundary and evidence validity

ACP standardization concerns more than transport: it supplies lifecycle methods, notifications and capability negotiation. It does not select an implementation, process scheduler, queue policy, model, cache, sandbox or billing scope. An **ACP implementation** is the code that realizes the protocol. An **ACP adapter** may translate another API or SDK, potentially adding a process, serialization pass and semantic loss. A first-party implementation need not contain that extra hop.

Likewise, “native API” is ambiguous. A **harness-native API** controls the upstream agent loop and can fit delegated execution. A **direct provider model API** puts the model/tool loop under Recursion’s native path, with a separately authorized credential and billing route. It is not an interchangeable subscription-backed shortcut for an upstream comparison. An SDK may simply launch a CLI; its package name does not establish in-process execution or lower overhead.

| Candidate topology | Plausible advantage to test | Principal cost or failure risk | Eligible scope |
|---|---|---|---|
| Direct structured harness interface | Preserve rich controls and receipts without an extra translation hop | Bespoke mapping and upgrade/conformance maintenance; service residency | Workflow supported by the exact admitted native interface |
| First-party native ACP implementation | Shared client machinery and capability negotiation | Implementation-specific queues, extensions and missing required fields | Supported ACP profile with explicit losses and extensions |
| ACP bridge over SDK/API/CLI | Broader reuse behind one external interface | Extra codec/process, event reordering, hidden SDK retries and version joins | Only where end-to-end semantics and boundary remain verifiable |
| Persistent structured CLI/control stream | Reuse a process without a public listener | Framing, lifetime, queued-input and crash-recovery obligations | Bidirectional or sequential controls actually exposed by that mode |
| One-shot structured CLI | Bounded invocation and simple per-process attribution | Repeated launch/discovery/restoration, result-only gaps, limited active controls | Bounded jobs whose accepted contract needs no unavailable controls |
| PTY/text wrapper | Compatibility or human-mediated interaction where needed | Escape parsing, redraw/prompt ambiguity, terminal coupling and inferred state | Explicitly limited profile; never silently credited with structured control parity |

These are overlapping axes, not six mutually exclusive products. A CLI can attach to a resident server; an ACP endpoint can be a long-lived CLI subprocess; a native app-server can use stdio. A bridge can be in-process rather than a second process. Record the actual graph before attributing costs.

## Fresh public evidence that changes the comparison

The concise facts below are the new primary-source anchor. Later sections propose Recursion measurements rather than reproducing these sources. All were inspected on 2026-10-02 UTC. Mutable pages are date-bound, not installed-release guarantees.

| ID | D-public finding | Consequence for this comparison |
|---|---|---|
| P01 | ACP uses bidirectional JSON-RPC requests and notifications. [Overview][P01] | “ACP versus JSON/API” is a false dichotomy |
| P02 | ACP stdio uses UTF-8 newline-delimited messages with protocol-only stdout and separate stderr. Streamable HTTP is described as a draft. [Transports][P02] | Compare concrete framing and topology; do not assume a production HTTP ACP route |
| P03 | Initialization negotiates major protocol version and capabilities; unsupported returned major requires client handling, and missing capabilities cannot be presumed. [Initialization][P03] | A version number alone cannot freeze every behavior or extension |
| P04 | ACP cancellation is a notification. Pending permission requests receive cancelled outcomes; updates may arrive before the prompt’s cancelled completion. Usage updates are optional and describe current context plus optional cumulative cost. [Prompt turn][P04] | Keep reading and preserve separate cancellation, effect and meter evidence |
| P05 | Current ACP v1 documents capability-gated `session/load` with history replay, `session/resume` without replay, and `session/close` that cancels and frees active-session resources. [Session setup][P05] | Replay-free reattachment is a legitimate candidate where implemented; it is not universal support or canonical recovery |
| P06 | Codex App Server exposes per-connection initialization, streamed turn/item controls and version-generated schemas; active steering requires an expected turn ID. Experimental methods are gated. The page lists stdio and Unix-socket options, marks TCP WebSocket unsupported/experimental, and includes a broader command warning in its remote-host section. WebSocket overload rejection is documented. [App Server][P06] | Resolve exact transport/method maturity and overload behavior before admission; do not transfer a WebSocket queue claim to stdio |
| P07 | Codex noninteractive execution offers JSONL events, final-output schema and resume. [Noninteractive mode][P07] | Machine-readable CLI is a structured candidate; final schema is not an interactive control contract |
| P08 | Claude’s SDK distinguishes persistent streaming input from one-shot input with resume, and documents sequential queued input and interruption in streaming mode. [Streaming input][P08] | Compare like lifecycle modes; “SDK versus CLI” does not isolate startup cost |
| P09 | Claude’s cost documentation distinguishes turn main-loop usage from whole-call/model totals including subagents; reset boundaries matter, and currency fields are client estimates. [Cost and usage][P09] | Retain inclusion sets, reset epochs and unknown residuals rather than a single normalized cost field |
| P10 | OpenCode’s CLI documents attaching a run to a server to avoid repeated MCP startup. [CLI][P10] | Include an attached CLI as a strong warm-process comparator |
| P11 | OpenCode v2’s client shares a lazy event connection, waits for active subscribers, and provides live-only subscriptions without automatic reconnect/replay. [Client][P11] | A slow UI consumer is a concrete shared-stream hazard; separate ingestion from presentation |
| P12 | The separate experimental v2 API documents a durable session log with an exclusive sequence cursor and follow mode, alongside inbox and execution controls. [API][P12] | Live-stream limitations do not imply absent durable replay; qualify both surfaces together |
| P13 | Cursor’s ACP documentation distinguishes blocking extensions from notifications; its task notification also has response-shaped examples. [Cursor ACP][P13] | Preserve R-F’s ambiguity; do not infer host-side delegation or control from the example shape |
| P14 | Gemini’s ACP guide documents a stdio operational mode and a route-specific method set. [Gemini ACP][P14] | Protocol availability does not confer every optional ACP feature |
| P15 | Grok’s pinned session-spawn source contains a per-session thread path, an 8 MiB configured stack, a current-thread runtime and several unbounded channels. [Pinned source][P15] | Thread/queue resources belong to the implementation, not to ACP as a standard |

P05 resolves a retrieval limitation, not a recorded failed product test: R-F retained a 404 for the guessed `protocol/session-resume` URL. The valid current documentation is the **session-setup** page. Neither that earlier 404 nor this successful read says which installed harness supports replay-free resume. A no-history response also cannot repair a gap in Recursion’s own evidence.

P06’s maturity wording remains unresolved for an intended operating profile. The existing R-F pin is retained, and a fresh GitHub read succeeded for the same README after browser retrieval failed. Its inspected content includes `thread/revert` and specialized method notes; it is not treated as proof that every mutable web statement matches a binary. No live handshake is proposed in this research task.

## Applying this to the repository routes

This is a shortlist for **comparison**, not a replacement for R-F’s full route inventory or an eligibility declaration. The facts in this table are D-repository summaries; the named tests are proposals.

| Route family already researched | Most useful comparison | What must stay distinct |
|---|---|---|
| Codex / eligible ChatGPT sign-in | Exact App Server structured profile versus the same accepted job through exec where controls overlap | D-023 priority; actual build/schema; transport maturity; sandbox-sensitive methods; account class; native child/meter closure |
| Cursor | First-party ACP versus its actual supported headless/local SDK route | First-party, independent adapter and cloud paths; extension semantics; retries; callbacks and reapplication of restrictions |
| Gemini CLI | Exact ACP mode versus structured headless on matched bounded tasks | Current flag/build correspondence; mode-specific approvals; helper and fallback closure; supported control subset |
| Grok Build | Native ACP plus allowlisted extensions versus structured headless where equivalent | Core ACP versus `x.ai/*`; session-thread and queue implementation; native children; process-scoped/reset accounting |
| Hermes | Exact ACP versus gateway profile | Persisted history versus process-local attachment/admission; secret-bearing callbacks excluded; queue and meter coverage |
| OpenCode | Generation-specific server/API versus ACP or attached CLI | Legacy and v2 contracts; live subscriptions versus durable log; experimental API status; abort/queue semantics |
| Claude Code / SDK | Persistent stream-control versus one-shot/resume for the same accepted workload | SDK executable/environment correspondence; subscription/embedding eligibility; interrupt and queue handling; cumulative meters |
| Pi and Antigravity comparators | Their documented persistent structured modes versus bounded one-shot modes | Pi’s settled versus turn-ended distinction and queue clearing; Antigravity’s separate input/control limitations |

For routes with no equivalent second interface, do not invent one. Measure adapter overhead against the same direct route, and measure maintenance/coverage separately. A restricted CLI may be fully adequate for a batch task while ineligible for a workflow requiring steering, correlated questions or recovery. Missing a required launch-critical capability remains a release issue under existing decisions, not an excuse to quietly remove the route.

## Latency and throughput without misleading comparisons

### Separate the timestamps

Use R-O’s endpoint definitions and add the following attribution cuts. They are proposed instrumentation points, not current observations:

| Interval | Exact meaning | What it must not be called |
|---|---|---|
| Scheduled arrival to Recursion ingress | Caller or upstream queue wait before the platform sees work | Adapter CPU time |
| Ingress to durable admit or refusal | Authority/config/capability checks, reservation and required journal work | Model latency |
| Admit to upstream receipt | Launch if needed, handshake, serialization, IPC and upstream admission wait | Provider prefill without provider evidence |
| Upstream receipt to first content event | Harness scheduling, helpers, network, provider queue/prefill and initial generation as observable | Pure model inference time |
| Event received to canonical observation retained | Decode, correlate, validate and append work | User-visible rendering latency |
| Retained event to projection and display | Authorized projection, transport and rendering | Completion or effect settlement |
| Scheduled arrival to verified useful outcome | Full task, tools, retries, helpers, recovery, independent verification and relevant review tail | First-token latency |
| Stop issued to fence accepted, receiver installed, native terminal and settlement disposition | Four or more separate control endpoints | One undifferentiated “cancel latency” |

A request’s end-to-end duration is a critical path. Overlapping intervals cannot simply be added, and the sum of stage p95 values is not the end-to-end p95. If only a round trip is visible, the hidden harness/provider components remain combined and unknown. Never subtract a guessed model duration to present a precise control-plane residual.

Report p50 and p95 for cold launch-to-ready, warm admission, first-event delivery, control/fence, event-retention and verified task outcome, separately by route/profile and workload. Preserve timeouts, refusals, crashes and unfinished observations. A fast acknowledgement of a queued command is not fast adoption. A p95 among successful responses alone hides the tail failures that matter to productive continuity.

### Define warm precisely

“Cold” has several meanings: process absent; process present but connection new; session absent; history restored; tool/MCP helpers absent; local filesystem cache cold; provider cache cold. Record them independently. Do not claim to flush a provider cache, or label the OS page cache cold, without evidence and authorization.

Use these primary strata:

- **C0 process-cold:** process and route connection newly created, with unchanged declared filesystem-cache state
- **C1 process-warm session-new:** reuse admitted process, create a new independent session
- **C2 session-warm:** same eligible session and current configuration/grants, successive turn
- **C3 restore:** new connection or process restoring the same permitted session/context, including all replay and reconciliation work
- **C4 no-future-use:** one bounded invocation plus complete teardown and its evidence retention

Bounded reuse can remove repeated local setup from C2; it cannot remove upstream queuing or model work by definition. Reuse also retains memory, helpers and state that must be partitioned by principal, workspace, privacy scope, route/config revision and grants. Never pool across these boundaries just to improve a hit rate. Eviction must preserve pending effects and meters. Detaching a view cannot own eviction or terminate an active task.

A useful break-even calculation is a vector, not a made-up dollar total. For example, compare total measured launch CPU saved with extra idle CPU over the same inter-arrival trace, and compare memory-time separately. Latency may favor a resident path even when resources favor demand activation. A route switch that loses effective context may overwhelm a small wire saving; measure the whole continuation.

### Throughput and backpressure

Use scheduled open-loop arrivals as well as serial request-response trials. A producer waiting for each response can conceal overload and queue wait. Report offered, admitted, refused, completed and independently accepted unique work, full elapsed exposure, ending backlog and post-burst drain time. Output events per second are an ingestion metric, not completed tasks per second.

Every queue needs owner, count and byte caps, oldest age, high water, outstanding credits, full behavior and control reserve. Include adapter input/output, upstream internal queues where observable, canonical writes, renderer subscriptions and retry queues. A fast unbounded enqueue is deferred cost, not high sustainable throughput.

Keep parsing, permission responses and Stop off slow presentation callbacks. Bounded spooling/coalescing may change presentation, but mandatory canonical events must persist or execution must be held/refused under the declared policy. A dedicated connection is one candidate; reserved scheduling on a shared transport is a genuine rival. Neither provides an interrupt deadline unless upstream progress, framing, CPU and write capacity are also bounded. A partly received oversized frame must not consume the entire control reserve.

Fan-out needs a separate sweep from stream throughput. Compare sequential tasks, native bounded subtrees and separately launched tasks under equal work, authority and conserved reservations. When native child creation cannot be intercepted, reserve and enforce the whole allowed subtree. A high completion count with opaque child work, unresolved effects or growing review debt is not a win.

## Stop and effect correctness before speed

The exact D-022 vocabulary remains unchanged. Neither ACP’s cancellation nor a native API response automatically implements it.

| Recursion operation | Required composition | Failures that reject an apparently fast path |
|---|---|---|
| **Aggressive Stop** | Fence further selected-agent dispatch and interrupt without waiting for the current operation; separately identify descendants | Cancelling the wrong turn/incarnation; interpreting a sent notification as observed termination; concealing in-flight effects |
| **Full Stop** | Fence the rooted owned set, including children, shells, monitors, relaunchers and return paths; settle or explicitly mark each member unresolved | Killing unrelated sessions sharing a process; native queues restart work; hidden descendants; remote silence labeled stopped |
| **Lazy Stop** | Close admission; wait for the named observable permitted operation boundary with deadline and configured escalation | New work admitted while waiting; invented hidden-reasoning boundary; infinite wait; implicit escalation |
| **checkpoint** | Validated durable manifest of directives, grants, epochs, attempts, interactions, queues, evidence, meters, artifacts and unsettled effects | Transcript copy declared a complete checkpoint |
| **interrupt** | Record native request, delivery/acknowledgement where available, terminal result and process evidence separately | Dropping late updates or assuming rollback |
| **drain** | Close new root/child admission; allow only the declared finite already-admitted work needed to finish or reconcile | Unbounded retries or background relaunch disguised as draining |

An ACP adapter must map the P04 cancellation lifecycle while retaining Recursion’s independent effect truth. A native adapter must do the equivalent for its version-bound controls. A CLI signal path needs its own observed result/exit/tree semantics. A PTY Ctrl-C byte requires a qualified target and terminal mode; its appearance in a stream is not such evidence.

One process can host several sessions. If a requested per-session Full Stop cannot be enforced without killing unrelated work, that sharing arrangement is ineligible for the required scope unless a separately approved broader stop is intended. Session-scoped native controls or separately contained ownership groups are candidates; additional processes are not automatically waste.

A deadline can yield a truthful stopped-with-unresolved-effects disposition. That may be the only correct result for an unreachable recipient, and must not be scored as settled success. Process exit, source completion, cancellation completion, local ownership settlement and receiver-side effect settlement remain separate facts. Transport loss after possible dispatch blocks blind retry of non-idempotent work. Preserve one retry owner across SDK, bridge, adapter and scheduler.

## Recovery context and accounting economics

**Productive continuity is the performance endpoint.** A reconstructed connection is only a step. Measure fault-to-detection, model-free status, canonical replay readiness, current-authority validation, effect reconciliation and first independently verified useful continuation. A faster reconnect that discards unanswered questions, repeats a committed tool effect or loses an accepted directive fails the comparison.

Keep canonical command/operation identity separate from wire request ID, attempt, upstream session/turn, process incarnation and route assignment. Route assignment epoch and route-descriptor evidence epoch have different meanings: reassignment does not refresh stale capability evidence. On reattach, reconcile accepted/delivered/adopted and pending waiters before resending. Preserve source gaps honestly. Old sessions, forks and restored transcripts do not recreate grants or remaining budget.

The P05 distinction can reduce reconstruction traffic when an eligible ACP implementation restores without replay, **if Recursion already has the necessary evidence and validates the continuation**. Test replayed load and no-replay resume separately. Never trade away missing history or effect evidence merely to improve restart timing. Native APIs with queryable records or cursors require the same obligation, regardless of method name.

Separate five cache owners: local source/index cache, canonical artifact cache, Recursion context capsule, upstream harness session and provider-native prompt/KV cache. A hit at one level proves nothing about another. Persistent processes do not guarantee provider cache hits; new processes do not necessarily prevent them. ACP does not make cache state portable across providers.

For each context transformation bind route/build, effective instructions/tools/plugin set, compaction owner, input/output artifact identities, privacy scope and retained required fields. Stable context order and explicit invalidation are candidates to test, not a universal quota optimization. Unknown vendor-side injection/preprocessing remains unknown. A route lacking exact prompt/tool control must expose that limit. Upstream-only workflows cannot quietly invoke a native compactor or helper to make the comparison succeed.

Count all reasoning roles, attempts, helper calls, retries, verification and recovery. Record native quantity and unit; cumulative/delta scope; meter epoch and included attempt set; raw receipt; measured/modelled/unknown state; lower bound and unknown residual. Do not sum parent-inclusive totals with their children or count replayed cumulative observations again. A fork’s inherited meter is history, not new consumption. A crash-zeroed field must not overwrite a defensible earlier subtotal. Missing usage is not zero.

Keep API charges, estimated currency, provider token classes, subscription allowance/window changes, local CPU and human review separate. The provider-free handoff uses synthetic work units only. It can test conservation and visibility; it cannot establish subscription savings, paid cost or model quality. An unbounded unknown debit prevents a total-economics claim even if local latency improves.

## Resources trust and qualification

Measure the complete declared process/helper graph: launch broker, adapter/bridge, harness, model-free tool stand-ins, collectors, retained services and optional views. Track current and peak memory, commitment where supported, CPU time, process/thread/handle counts, I/O, stored bytes, wakeups where supported, idle slopes and restart cleanup. Include bridge serialization and both sides of its IPC. Do not sum per-process peak memory as if peaks occurred together, equate configured stack size with resident bytes, or subtract instrumentation overhead to invent an unobserved result.

D-029 is a non-tradeable prerequisite for a strong-required profile. A structured protocol, same-user child process, cgroup or Job Object is not the credential boundary. The exact unmodified upstream build must support credential-facing **C** separation from untrusted tool/output **T**, or an independently evidenced equivalent enforcement. Direct reads and induced export through prompts, config, helpers and outputs both matter. Launch/auth/account mutation methods and credential-bearing callbacks remain outside the admitted control set. A strong-preflight failure refuses admission; a policy-only label does not authorize a downgrade.

Before timing a real route, its qualification tuple must contain:

- executable/package/source provenance and actual build identity; adapter/dependency/schema digests
- exact transport, invocation mode, method allowlist, experimental features and extension set
- model/provider/endpoint, account class and billing/allowance source, with no secret material in the record
- operator-provisioned launch boundary, trusted components, tool/egress/workspace limits and process ownership
- route descriptor evidence epoch, route assignment epoch, configuration revision and grant/fence bindings
- source-documented support, observed positive/negative conformance, losses, unknowns, freshness and requalification triggers
- all-role/helper closure, reservation algebra, meter coverage, cancellation, recovery and effect-settlement evidence
- independent verification and applicable counsel/automation clearance

An implementation’s self-reported identity is not an authenticated principal. A source SHA or signature does not establish correct semantics. Pinning public source does not prove a distributed binary matches it. A protocol compatibility suite does not prove Recursion’s authority, accounting or external effect contract.

Keep native D-028 Windows/Linux qualification cells separate from WSL development/test results. Retain the accepted local NTFS/ext4 storage scope. No startup optimization can replace independent persistence/replay and abrupt-VM-reset evidence where required. This report neither selects a runtime/store/sandbox nor reopens those decisions.

## Competing strategies and falsifiers

| Strategy | Strongest case | Decisive falsifier | Non proof |
|---|---|---|---|
| **S1 Route-specific structured adapters with bounded reuse** | Preserve each qualified upstream’s useful semantics while sharing Recursion’s canonical records and codecs where appropriate | ACP-first preserves the same required controls/evidence with no practical response/resource regression and materially lower accepted maintenance cost; or route-specific mapping causes semantic drift that shared normalization avoids | Richer methods do not prove faster responses, safe credentials, lower quota or fewer bugs |
| **S2 ACP-first with explicit extensions and qualified bridges** | One client core and common conformance machinery could reduce total ecosystem integration cost | Required semantics cannot be preserved without hidden vendor escape paths; bridge loses correlation or adds material tail/resource/recovery cost; extension upkeep erases the maintenance saving | Shared schema and fewer top-level adapters do not prove equivalent behavior or cheap porting |
| **S3 Demand-activated structured jobs by default** | Strong rival for sparse/no-future-use workloads; lower retained process/helper cost and smaller failure scope | Repeated initialization/restoration violates adopted responsiveness budgets, or jobs require controls absent from that mode | Lower idle memory does not establish task efficiency or justify capability removal |
| **S4 Bounded resident sessions by default for admitted interactive work** | Strong rival for bursts and continuity-heavy work; may amortize setup | Tail control/eviction/recovery or idle resources exceed ceilings; shared process cannot preserve Stop/privacy scope | A warm handshake does not imply warm provider cache or durable continuation |

S1 and S2 compare integration strategy; S3 and S4 compare residency. Test them independently before the full-profile combination. A valid result may prefer native App Server for one workflow, first-party ACP for another and structured one-shot execution for a third. Final defaults require the existing Owner decision process.

The runtime pilot cannot settle S2’s maintenance claim. Following R-O and D-033, a later paired port/rewrite exercise must retain implementation, review, rejected attempts, conformance, dependency/license handling, diagnosis and two frozen upgrade/requalification scenarios for the same accepted behavior. Count accepted integrations and actual effort, not protocol names or lines of glue. Shared ACP code may reduce duplication; accumulated extensions and bridge-specific failures may erase that saving. Either outcome is still unmeasured.

### Operational recommendation register

These are implementation and evidence choices beneath the accepted constraints. Rivals must preserve the same authority, privacy, evidence, Stop and accounting floors. A lossy or unauthorized shortcut is a negative control, not a genuine rival. This register covers the queue, control, cache and measurement proposals as well as the headline strategies.

| Proposal | Eligible rival | Concrete falsifier and decisive observation | What a pass does not prove |
|---|---|---|---|
| R1 Share Recursion command/correlation semantics across route adapters | Independently implemented per-adapter mappings passing the same canonical corpus | Equal accepted inputs yield different target, refusal, receipt, epoch or meter meaning; W3 independently compares each mapping to the oracle | Universal future-adapter compatibility or a selected implementation language |
| R2 Reuse a bounded eligible session/process pool | Demand-activated isolated invocations, with identical restore/evidence support | C2 responsiveness gain disappears after idle, eviction and C3 recovery cost; sharing cannot enforce the requested Stop/privacy scope | Provider-cache reuse, safe cross-principal pooling or savings on sparse workloads |
| R3 Isolate authoritative ingestion from presentation through bounded projections | One shared event pipeline with verified bounded scheduling and separate subscriber accounting | W2’s slow sink stalls required retention/control or grows an unbounded buffer; W3 loses a mandatory receipt | A universal queue capacity, perfect fairness or unlimited history retention |
| R4 Reserve a physically distinct control channel where justified | Shared transport with independently reserved framing, decoder, scheduler and write capacity | Under the same bulk-frame and sink-stall trace, Stop misses its adopted budget, or a large partial frame blocks admission | Upstream cancellation timing, remote delivery or effect rollback |
| R5 Apply bounded upstream backpressure and a declared spool/hold policy | Early admission throttling/refusal with a smaller or absent spool | W2 loses required events, exceeds byte/count caps or fails to drain within the frozen criterion; compare admitted useful work and retained bytes | All-load sustainability or proof that upstream internal queues are bounded |
| R6 Bind session retention and Stop to explicit owned scopes | Separate contained processes per ownership root instead of multiplexed sessions | W3’s Full Stop leaves a relauncher/queued child eligible, or kills the unrelated session | Credential isolation or physical process-tree containment on untested platforms |
| R7 Reuse validated context/caches and avoid unnecessary history replay | Fresh rehydration from canonical evidence with the same required-field oracle | Changed grants/config/source/privacy cause a stale hit; either arm loses a required directive or effect record; compare first useful continuation and total reconstruction bytes/CPU | Provider prompt-cache hits, preserved hidden state or lower subscription debit |
| R8 Keep event-level native-unit meter segments and explicit inclusion sets | Periodic reconciled cumulative snapshots with equivalent reset/coverage evidence | Duplicate/reset/fork/crash cases produce different conserved totals, erase an unknown residual or charge an included child twice | Provider billing truth or complete hidden-helper visibility |
| R9 Instrument causal latency cuts alongside end-to-end measures | Paired black-box ingress-to-outcome measurements with the same mandatory witness and explicit unresolved attribution | Collector changes arm ordering beyond the adopted margin, misses its sensitivity control or double-adds overlapping stages; compare both raw totals and instrumentation modes | A precise provider-inference decomposition or an unobserved observer-free latency |
| R10 Use the small staged topology pilot before whole-profile confirmation | Direct whole-profile comparison using the same fixed semantic/fault corpus and complete costs | A component advantage reverses or a required interaction fails in the held-out full profile; retain the original pilot result and reject its extrapolation | Real-route conformance, statistical sufficiency, release acceptance or entitlement |

For every row, no practical difference within the preregistered precision is NO_BENEFIT; inadequate evidence is HOLD_UNKNOWN, not equivalence. A material resource/review/recovery regression is retained even when latency improves. R2/R7 require cold/no-future-use as well as warm cases; R3–R6 require pressure and cancellation; R8 requires partial and overlapping counters. This ensures the proposal is tested where its advertised advantage could fail.

## Minimal provider free benchmark handoff

**Unexecuted.** This is a bounded extension to R-F’s synthetic endpoints and R-O fixtures, not a new benchmark campaign or an instruction to run this repository. There is no verified runnable entrypoint for the proposed comparisons. Implementation and execution require a separately approved local task with exact new runner/adapter artifacts. No command that invokes a named harness is supplied.

### Purpose and stopping boundary

Establish whether differences come from protocol encoding, an extra bridge or process/session lifecycle while preserving the same semantic oracle. Stop at an independently reviewed **synthetic integration-path result**. Do not promote it to real harness performance. Provider/model/account/credential calls, real upstream binaries, network listeners, installs, live hosts and target repository scripts/imports are excluded from this initial handoff. The local runner uses only public synthetic data and separately reviewed new fixture code in a disposable authorized workspace.

### Prerequisites

Freeze the source merge above, the selected R-F/R-O semantic corpus, independent oracle, runner/build/dependency identities, host/process limits, monotonic clock and collector identity, synthetic output directory, precise queue caps and fault schedule. Set finite per-case deadlines and memory/process ceilings before execution; absent approved ceilings block the run. Safety fixtures use virtual ticks and explicit barriers. Wall-clock performance uses actual monotonic observations, never converts virtual ticks into milliseconds.

Bind the adapters to equivalent **synthetic** agent behavior. The agent executes no repository code, model, shell tool, auth lookup, dynamic plugin or network request. Source-inspired wire profiles must be labeled simulated; copied method names do not make them real vendor implementations. A positive control records attempted forbidden work at a denying boundary rather than making that call.

### Four mandatory arms and one conditional arm

All arms include the same canonical admission, durable receipt promise, trusted-boundary stand-in, context/artifact inputs, effect sink, verification and accounting. Implementations may differ, but required semantics may not. No actual credential boundary is claimed from the stand-in.

| Arm | Frozen topology | Isolated contrast |
|---|---|---|
| H-A | Recursion adapter directly to one persistent synthetic peer using a native-style structured profile over pipes | Reference path |
| H-B | Same behavioral peer, lifecycle and process count using ACP v1 framing/capability profile over pipes | H-A versus H-B isolates the codec/mapping path as implemented; not ACP’s universal cost |
| H-C | H-B-facing client through one explicit ACP-to-H-A bridge process to the same peer | H-C versus H-A and H-B exposes this additional hop and translation |
| H-D | Same job/peer logic through structured one-shot subprocess output, fresh process per admitted bounded job | H-D versus H-A on the common job subset exposes repeated lifecycle cost |
| H-E conditional | Short-lived structured CLI client attaching to an already-running synthetic service | Include only if such a topology is being proposed; separates client startup from service/MCP residency |

Do not compare a feature-poor one-shot arm against an interactive task it cannot represent. Mark unsupported-before-dispatch with `attempted=false` and retain that coverage result. It is neither a performance loss nor a pass for the missing workflow. Optional ACP capabilities/extensions used by H-B/H-C must be frozen; base-only and extended profiles are different cells.

### Exact screening workload

These constants define a reproducible **pilot**, not product budgets, statistical sufficiency or a claim about real workloads. A reviewer may change them only before the pilot and must issue a new workload identity.

1. **W1 lifecycle and empty work:** a 4,096-byte ASCII synthetic input with no semantic effect; peer emits a correlated admit observation, one 256-byte payload event and a terminal record. Run C0, C1, C2 and C4 separately. For each eligible arm collect 5 independent blocks of 20 process-cold starts, and separately 5 blocks of 200 measured turns for each applicable process-warm/session-new and session-warm stratum. Precede each warm block with 20 explicitly labeled warm-up turns, excluded from timing but retained in resource totals. Randomize arm order within each block using seed `20261002`; publish actual order and the runner’s pinned permutation algorithm.
2. **W2 streaming and pressure:** each of 1,000 scheduled logical jobs emits exactly 64 numbered events of 1,024 payload bytes each, plus begin/end records. Content is a deterministic public ASCII pattern keyed by job/event ID. Keep the same generated payload across arms; separately report framing/encoding bytes. After an untimed, separately recorded calibration on H-A, freeze three offered rates at 0.25, 0.75 and 1.25 times that calibration’s measured sustainable admission rate. Do not recalibrate each contender to hide poorer capacity. Use one no-view authoritative collector and, separately, one presentation sink that stalls for 250 ms every second. Run 5 independent blocks per cell; continue through the predeclared bounded drain period and preserve unfinished jobs.
3. **W3 control and recovery:** use 32 synthetic sessions, one target session with two owned children and one unrelated session. Trigger Stop or loss at exact barriers: before dispatch; after dispatch before receipt; after receiver commit before receipt; during event 32 of 64; after terminal before final meter; and during history restoration. Exercise Aggressive, Full and Lazy separately, plus permission-wait cancellation, queued input, duplicate result, stale turn/epoch and one retained unresolved effect. Test a 10,000-event synthetic history with replayed load and separately advertised no-replay resume. Pair each fault with an unchanged no-fault control. If an arm lacks a required control, classify that cell as unsupported rather than emulate success.

W1 targets repeated process work; W2 targets translation/queue and slow-consumer costs; W3 targets fast-but-lossy behavior. They are the minimum contrasts here, with discrimination still dependent on a sensitive oracle and sufficient measured precision. Broader platform faults and D-024’s six demonstration journeys remain in the existing program, not silently replaced by these three workloads.

Calibration is bounded by the approved process/memory/time envelope. “Sustainable” in that pilot means the declared queue stays bounded and drains under its frozen criterion, not that production capacity is established. Preserve calibration data and select confirmatory rates independently of contender outcomes. If no rate qualifies, report that result rather than constructing a denominator.

### Independent oracle and required observations

For each logical operation, the independent oracle knows the authorized scope, expected input digest, ordered mandatory events, effect sink truth, child graph, native-like meter inclusion set, reset epoch and final artifact digest. It checks each candidate against this truth, not only against another candidate.

Required negative controls deliberately: drop a mandatory event; convert a missing meter into zero; double-count a replay; retry after ambiguous commit; let an SDK-like retry bypass the one retry owner; send stale steering; let a late approval answer a replacement waiter; dispatch after installed fence; kill the unrelated session; and allow a slow view to starve control. Every planted violation must be detected. Failure of the oracle’s sensitivity makes the comparison invalid, not a candidate pass.

Record the intervals defined earlier, empirical p50/p95, sample counts and block identities, timeouts/censoring, failures/refusals, throughput counts, backlog age/drain, queue high-water bytes/events, CPU, current/peak memory, process/thread/handle counts, read/write bytes, and retained evidence size. Keep raw monotonic timestamps and causal IDs. Report startup by independent process launch; warm messages are nested within process/session blocks. A thousand correlated events do not provide a thousand independent task replications.

At this pilot size, tail estimates are descriptive with uncertainty. If the p95 or difference cannot be resolved, keep the inferential result unknown. Before confirmatory testing, freeze practical improvement/noninferiority margins, confidence/precision method respecting block/session clustering, necessary sample exposure and stopping rule from the pilot. Do not invent an accepted millisecond target or stop when significance first appears. R-L’s example responsiveness targets remain proposals, not inherited acceptance budgets.

### Result artifacts and promotion rules

The later implementer should deliver these **new** artifacts, with schemas and independently validated joins:

- `manifest.json`: exact input/candidate/profile/host/collector IDs, experimental factors, caps, deadlines, order, seed, cache/lifecycle labels and authorization boundary
- `trace.jsonl`: monotonic and causal events with operation/attempt/session/turn/epoch, native correlation, queue and measurement scope
- `oracle.json`: expected versus observed authority, mandatory evidence, effect, child and meter outcomes, including planted violations
- `samples.csv`: raw per-operation/per-launch timing and resource rows; failed, refused and censored rows retained
- `summary.json`: per-cell counts, p50/p95 and uncertainty, all-vector metrics, exclusions and R-O disposition
- `checksums.txt` and independent verifier receipt: frozen artifacts and the exact candidate reviewed

Use R-O’s classifier: INVALID_EVIDENCE, REJECT_FLOOR, HOLD_UNKNOWN, NO_BENEFIT, REGRESSION, NON_DOMINATED_TRADEOFF or CONDITIONAL_ADVANTAGE. One valid hard-floor counterexample rejects that arm before speed ranking. Missing required controls or counters restrict the claim; they are not filled by optimistic defaults. A conditional synthetic advantage establishes only that frozen path and workload.

Stop immediately on unexpected real data, credentials, provider/model/network or named-harness activity; exceeded approved resource/fault envelope; invalid clock/witness; canonical divergence; stale admission or unavailable required control. Preserve the failing trace. Repairs get new identities and rerun the relevant floor suite. Deadline expiration is not completion or effect settlement.

### Subsequent gates remain separate

Only after this result and explicit authorization should later work inspect/run an exact upstream build in an isolated provider-free rig where supported. That stage establishes real framing, callbacks, metadata/helper attempts, cancellation and restoration conformance; it still does not establish account entitlement, production containment or model economics. An upstream binary that cannot be kept inside the authorized no-provider/no-credential envelope remains unrun.

Actual route qualification additionally requires D-029 and native D-028 evidence, account/counsel admission and an independently reviewed workload. Only a separately approved real-route comparison can establish full quality, latency, quota or productive-continuity gains. None of these later gates is authorized or completed by this companion.

## What the evidence supports now

The route-specific structured strategy is the most defensible **first hypothesis to test** because it preserves the repository’s already-required rich controls without imposing an extra normalizing hop where one is unnecessary. ACP is an important supported option inside it and a credible broader integration strategy. Structured CLI modes remain legitimate peers; PTY/text driving must carry its actual limitations.

Choose no blanket winner. Keep D-023’s qualification order, test the causal contrasts, and promote only a route/workload-qualified result whose authority, resources, meters and recovery pass. The decisive output is not “ACP is faster” or “APIs are faster,” but “this exact integration and residency profile improves this accepted workflow by a measured amount, with these preserved guarantees, costs and limits.”

## Provenance and retrieval limits

Repository references below are pinned to the inspected PR 147 merge. Historical runtime observations described in ROUTE-CAPABILITIES and EXECUTION-FABRIC were read as records, not rerun. The public fact table is deliberately concise; no direct quotations are used. Method names and technical identifiers are preserved where necessary.

| Source group | Retrieval and pin | Limitation |
|---|---|---|
| P01–P05 ACP documentation | Official v1 pages, inspected 2026-10-02 approximately 17:01–17:04 UTC | Mutable pages; no local installed implementation or immutable documentation commit established |
| P06–P07 Codex web docs | Official ChatGPT Learn pages, inspected 2026-10-02 approximately 17:01–17:03 UTC | Mutable docs; maturity wording requires exact-profile resolution |
| [Codex pinned README][P16] | Commit `d25c114d494ddb693290b76bf5e5f64ecbdb38fc`; GitHub blob `b4f29ab453ca6e3fa1a345d74df3efed820d1795`; read via connected read-only GitHub API | Raw and blob URL browser retrievals returned cache-miss errors; API retrieval succeeded. No binary correspondence or complete web/source agreement asserted |
| P08–P09 Claude docs | Official pages, inspected 2026-10-02 approximately 17:01–17:04 UTC | Mutable and version-sensitive; no account/SDK runtime observation |
| P10–P12 OpenCode docs | Official legacy CLI and separately labeled v2 client/API pages, inspected 2026-10-02 approximately 17:01–17:05 UTC | Generations cannot be combined into one installed profile; v2 API calls itself experimental |
| P13–P14 Cursor and Gemini | Official pages, inspected 2026-10-02 approximately 17:02–17:04 UTC | Cursor task notification ambiguity retained; Gemini guide’s shown update date is 2026-04-10, not evidence of current binary correspondence |
| P15 Grok source | Commit `2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8`; spawn file GitHub blob `323fe32f305231bfac22aa60d43f3123efd1c38e`; read via connected read-only GitHub API | An initial wrong path ending `session/spawn.rs` returned 404; the R-I source-register path `session/acp_session_impl/spawn.rs` succeeded. No inference about missing support from the failed path |

The current repository and source documents were read without executing their code. Public-source retrieval failures are recorded above; there were no denied actions that were bypassed. Numeric performance, implementation effort, real process-resource costs, complete helper closure, installed capability support, credential isolation, effect settlement, provider cache behavior and subscription savings all remain explicitly unmeasured or unqualified.

[R-E]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/re/report.md
[R-F]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rf/report.md
[R-I]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ri/report.md
[R-L]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md
[R-O]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ro/report.md
[R-PROTOCOL]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/protocol-edges/report.md
[R-MODEL]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md
[P01]: https://agentclientprotocol.com/protocol/v1/overview
[P02]: https://agentclientprotocol.com/protocol/v1/transports
[P03]: https://agentclientprotocol.com/protocol/v1/initialization
[P04]: https://agentclientprotocol.com/protocol/v1/prompt-turn
[P05]: https://agentclientprotocol.com/protocol/v1/session-setup
[P06]: https://learn.chatgpt.com/docs/app-server
[P07]: https://learn.chatgpt.com/docs/non-interactive-mode
[P08]: https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode
[P09]: https://code.claude.com/docs/en/agent-sdk/cost-tracking
[P10]: https://opencode.ai/docs/cli/
[P11]: https://opencode.ai/v2/docs/build/client/
[P12]: https://opencode.ai/v2/docs/api
[P13]: https://cursor.com/docs/cli/acp
[P14]: https://geminicli.com/docs/cli/acp-mode/
[P15]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/session/acp_session_impl/spawn.rs
[P16]: https://github.com/openai/codex/blob/d25c114d494ddb693290b76bf5e5f64ecbdb38fc/codex-rs/app-server/README.md

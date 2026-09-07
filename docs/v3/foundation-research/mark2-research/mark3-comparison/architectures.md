# Mark 3 comparative architecture dossier

2026-09-07. Research disposition; no product implementation or observed integration.
The canonical contracts remain in the linked v3 documents. This dossier owns the comparison,
source rationale and falsifiers, not a second mutable specification. Machine-readable claim
bindings and source receipts are in [evidence.json](evidence.json); bounded run designs are in
[probes.json](probes.json). Parent: `goal-recursion-v2-execution-fabric`.

## Finding that changes the next construction request

Compare three complete arrangements below against one authority and accounting contract.
Start interface probes with the demand-activated arrangement, retain a resident service
comparator, and investigate durable workflow assistance only for a discriminating recovery
case. This is a research recommendation within OR-036 through OR-039, not a framework,
language, storage or production-default selection. The strongest new evidence concerns
boundaries: a durable command receipt, provider cancellation, drained queue, process exit and
settled external effect describe different events. Combining them into one success flag would
invalidate Stop, recovery and accounting in every arrangement. CMP-001 through CMP-005.

All three keep native, independently useful upstream-only and combined execution. All reasoning
roles, including title generation, classifiers, compaction, consultation, planning and review,
must pass the same eligible route and parent-reservation admission. Required communication and
delegation are available in lean and rich configurations. No model heartbeat is needed to hold
identity, expose status, process Stop, expire a lease, reconcile a receipt or run a due timer.

## Three complete alternatives

| Component / capability | A: demand-activated services | B: resident session hub | C: durable workflow assistance |
|---|---|---|---|
| Canonical state | One fenced deterministic aggregate writer, append plus derived projection, durable dispatch intent | Same writer; hub is a replaceable projection and adapter service | Same writer; workflow journal is adapter scheduling state, never a second authority log |
| Process ownership | Broker starts an isolated harness/tool ownership group on admitted demand | Broker holds bounded warm harness servers; each session needs independently targetable effects | Broker plus workflow activity executor; journal schedules/retries only an already admitted operation |
| Config | Unprivileged compiler produces immutable candidate revisions; kernel admits scope and current authority | Same compiler; hub tracks per-session applied revision and isolates incompatible revisions | Same compiler; effective revision and authority epoch are explicit workflow inputs, rechecked on effect dispatch |
| Plugins / MCP | Manifest discovery without import; activate eligible workers/connections lazily | Bounded pools keyed by principal, trust domain, revision and context isolation; retain or evict explicitly | Plugin calls are admitted activities; MCP lifetime still belongs to scoped adapter, not replayed workflow code |
| Persistent assistants | Durable identity plus capsule; reconstruct session on demand | Durable identity plus optional warm session; never equate residency with identity | Durable identity plus scheduled wakeup; missed timer ticks and retries have declared semantics |
| Consultation | Application envelope, direct addressed consultation or Head relay; optional bounded room | Same envelope; resident routing can reduce setup latency but adds cross-session leakage risk | Same envelope; durable wait may help long consultations, without granting the scheduler decision rights |
| Views / terminal | Disposable views, bounded projection queues, broker PTY drain | Shared view server with per-view credit; control capacity reserved from bulk output | Same view contract; workflow progress is another input, never the terminal's canonical cursor |
| Native / upstream / combined | Native loop or supported harness session adapter starts when needed | Native worker pool and supported upstream servers retained under explicit limits | Either route executed by an activity adapter; no mandatory provider-specific planner/reviewer |
| Recovery / updates | Rehydrate canonical state; reconcile process/effect observations before replay | Additionally reconcile pooled sessions, revisions, pending waiters and ownership after hub restart | Additionally reconcile adapter journal and retry attempts; don't import journal success as effect settlement |
| Main uncertainty | Cold activation cost and capsule reconstruction fidelity | Idle cost, noisy neighbors, shared-server Stop isolation and stale warm context | Extra persistence/runtime coupling, duplicate retries and cross-journal reconciliation burden |
| Decisive comparison | Smallest source-informed interface and revision/Stop probes | Same probes plus installed-idle population and shared-server failure | One interrupted activity with lost receipt, stale executor and exhausted recovery allowance |

Residency and durability are independent axes. A/B/C are three complete configurations, not
an exhaustive partition: run C's recovery mechanism with A's and B's service lifetime held
constant, and compare it to the same canonical outbox plus receiver-owned operation records.
A bounded warm pool is an A/B treatment, not a fourth authority design. Pool keys include
principal, trust domain, revision and context isolation; also bound global key count and memory.
Bazel's per-key worker cap is not a global cap, and its idle-memory eviction cannot evict busy
work. Distinguish assistant identity, evidence artifacts, index state, provider session and
view lifetime. Vary revision churn as well as identity count. CMP-029.

A is the first probe target because it exposes ownership and disabled costs with fewer retained
lifetimes. This is an inference, not measured superiority. B can win on responsiveness when
startup and context reconstruction dominate; rejecting it on idle RSS alone would ignore the
accepted ranking. C can save substantial recovery machinery for long waits, but only if its
durability domain remains explicit and it removes more complexity than it adds. An embedded
actor/runtime implementation can realize aspects of C without a distributed service; this does
not justify selecting .NET, Temporal, Restate or their stores now. CMP-006, CMP-014.

## Kernel, process and scheduling mechanisms

**Atomic reducer plus dispatch outbox.** T3 Code's pinned `OrchestrationEngine.ts` orders
commands, checks durable command receipts, computes events and commits event/projection/receipt
state together. Publication follows commit. Its `RuntimeReceiptBusLive` is deliberately inert;
the test bus is not production evidence. Adapt the atomic receipt pattern, not that bus. Build
Recursion's cross-contract identities, authority checks and effect reconciliation. Its command/event and drain-worker queues are unbounded in the inspected source; bounded
admission and control reserve require adaptation. Queue drain alone says nothing about a remote
operation's settlement. CMP-001.

At that T3 pin the receipt lookup validates aggregate kind and ID, but the inspected receipt
does not bind the submitted command payload digest. Reusing the pattern therefore requires
Recursion's existing same-command/different-payload conflict guard. The source path alone does
not establish what every public entry point permits. Keep the immutable M1A conflict fixture
as a decisive negative test; do not transfer T3's receipt semantics unchanged.

**OS supervision versus terminal-library kill.** Windows Job Objects and Linux cgroup v2 provide
stronger containment/accounting boundaries than PTY handles. A Job contains only associated
processes; documented breakaway and alternative process creation paths need admission controls
and negative probes. Job completion notifications alone are insufficient evidence. A cgroup
kill handles concurrent forks and migration during the kill, but an already escaped process
and missing delegation permission remain outside that guarantee. systemd's normal stop path
sets `forbid_restart`; killing a PID alone can leave restart policy active. An external
activation source still requires a Recursion fence. CMP-002, CMP-003.

node-pty's Windows kill path closes ConPTY and, on one path, asynchronously enumerates console
processes with a fallback. portable-pty gives Unix session/terminal semantics. Neither inspected
path supplies Recursion's complete ownership proof. Reuse a terminal transport only after an
OS-owned scope exists; adapt systemd/Job supervision behind a broker. Do not turn a library's
`kill()` return into Full Stop. A broker crash and closing the last kill-on-close Job handle
are a separate policy choice from detaching a view. CMP-004.

Compare post-creation suspended-process association against containment at birth. Windows
`PROC_THREAD_ATTRIBUTE_JOB_LIST` and Linux `clone3(CLONE_INTO_CGROUP)` supply concrete at-birth
mechanisms on supported versions; hcsshim and Linux source pins document the paths. A broker
crash between creation and association can otherwise leave an unregistered child even if the
child has not run yet. Inject failure at creation, assignment, ownership registration and first
child spawn. Require no child or an identifiable contained child, never infer containment from
a PID. This is an adapter candidate, not a host certification. CMP-025.

Canonical Stop acceptance advances admission authority; it does not instantly install a fence
at an offline recipient. Model recipient-installed epoch, in-flight launch permits and fence
acknowledgment separately. A delayed old permit after local Stop but before remote installation
is an exposure to report; after installation it must be rejected. RFC 8881's data-server
revocation rules are prior art for enforcement at the recipient, not an NFS dependency.
Preserve distinct accepted, installed, terminated and externally settled timestamps. CMP-024.

**Workflow engine, virtual actor, journaled invoker.** Temporal documents deterministic history
and activity retry, while heartbeat processing returns cancellation requests cooperatively.
An unresponsive activity may continue after timeout or cancellation. Orleans durable reminders
store definitions but skip ticks missed during downtime; timers and interleaving have different
activation semantics. Restate's invoker carries a generation fence and preserves retry state;
its journal tracker distinguishes commands sent from acknowledged. These mechanisms inform
operation identity, wakeups and retry ownership. None proves exactly-once arbitrary external
effects. The OS broker, effect recipient or reconciliation adapter must enforce the actual
boundary. Avoid two independent retry owners. CMP-005, CMP-006.

**Receiver record versus workflow journal.** RIFL identifies four necessary mechanisms for its
RPC guarantee: stable request identity, atomic durable completion with the effect, retries
finding that record after relocation, and safe record retirement. Adapt a queryable recipient
operation record when the recipient can provide those properties. Compare lost receipt after
effect/record commit, effect without a record, moved recipient, and stale retry after retirement.
An arbitrary shell or provider call lacking that atomic boundary remains unknown; an outbox
alone cannot close it. C is justified only if it improves this same recovery case after counting
its journal/runtime/update burden. No exactly-once claim transfers to Recursion. CMP-023.
For both journal and receiver-record alternatives, an ambiguous effect permits authenticated
same-operation query/reconciliation, never retransmission before resolution. An atomic replay
cache does not override immutable M1C-INTEGRITY-CONTRACTS.md's ambiguity guard.

**Shared-pool authority.** One writer per goal does not serialize a pool shared by two goals.
Use one pool-reservation owner in the first candidate. Two goals each reserving six against a
pool of ten is the minimal lost-update trace. Conserved preallocated rights are a concrete
offline comparator, but require a separate proof of transfer, persistence and nonduplication.
Never reclaim offline rights solely because a lease expired or an account counter reset.
The bounded-counter paper assumes durable state is not rolled back. CMP-026.

## Configuration and plugin lifecycle

Compare (1) immutable snapshots and lazy isolated workers, (2) trusted typed in-process
contributors, and (3) capability-scoped worker/WASI execution. Option 1 is the general first
candidate; option 2 is a useful lean built-in path; option 3 may justify stronger isolation for
portable components. A process boundary alone is not a security sandbox. Host imports still
determine a WASI component's effective authority. No requirement says every plugin must fit
WebAssembly. CMP-007 through CMP-009.

OpenCode's pinned loader validates target/entry/compatibility before dynamic import and keeps
successful plugin order, but configured plugins can involve dependency installation and imports.
Its `pure` option suppresses external origins while internal plugins are separately controlled.
Event hooks are not awaited like config hooks, and dispose errors are ignored after reporting.
Therefore “plugin configured”, “loaded”, “event delivered” and “cleanly deactivated” cannot share
one receipt. This is a useful counterexample to a blanket zero-cost disabled claim. VS Code
offers manifest activation, eager/lazy hosts and bounded deactivation; those are lifecycle
mechanisms, not Recursion grants. CMP-007, CMP-008.

Keep four independent dimensions: **available**, **activated for this task**, **default profile**,
and **kernel/service/plugin placement**. A lean profile can retain manifests and UI affordances
while running no plugin code. Enumerating manifests can still cost disk/CPU; measure it. An
installed-but-disabled package must not run import, install, network or model effects merely
because discovery occurs. A missing dependency is a typed admission blocker, not permission
for a first-use install. Optional activation must be charged, bounded and visible.

Configuration compilation remains outside the kernel under OR-018. Preference revisions may be
coalesced, but a stricter authority epoch must survive the coalescing. Constructed failure:
`preference R1 → revoke R2 → preference R3`; latest-only delivery loses R2 unless its fence is
independent. The compiler proposes; the kernel checks current scope, grants and epochs. Both
existing-session propagation and future/isolated-session propagation remain available; neither
may postpone revocation. In-flight effects retain their old epoch and uncertainty. CMP-010.

Legacy MCP 2025-11-25 and current 2026-07-28 need separate adapters. The latter is stateless at
the protocol boundary: each request carries protocol version and client capabilities; optional
clientInfo is descriptive metadata, not an authenticated principal. Bind authentication
independently for each request. Explicit
handles may still name application state. It discourages tying a stdio process to one task.
Compare scoped reusable processes, per-context legacy connections and a partitioned pool;
require principal/context isolation and global resource bounds in each. Sampling is deprecated
in 2026-07-28, with at least twelve months before removal eligibility. Preserve eligible legacy
sampling, but do not turn the specification's direct-provider migration advice into a hidden
API requirement for upstream-only workflows. CMP-011, CMP-019.

Current multi-round tool requests terminate the initial wire request with InputRequiredResult;
the client retries under a new JSON-RPC ID, echoing opaque requestState only when present and
omitting it when absent. Test inputRequests-only as well as state-only continuation. Keep one durable
logical operation, deadline, round/byte cap and reservation across those IDs. Server-side state
integrity/principal/expiry/method-parameter binding and replay policy remain necessary; an
integrity-protected blob alone does not prove single-use effects. URL elicitation consent is
not completed authentication. Cache hints cannot cache an input_required result or the complete result of a retry carrying
inputResponses/requestState,
declassify private output, or permit stale authorization after a refetch error. Current HTTP
stream closure signals cancellation, not settlement; reconnect reestablishes subscriptions.
Preserve resources, output schemas, UI, auth and legacy loss maps. CMP-019, CMP-022.

Envoy xDS demonstrates why accepted configuration and effective configuration need different
receipts: ACK validates individual resources and intent to apply, while NACK can coexist with
partial acceptance. Keep compiled, validated, staged and effective revisions per recipient;
a connection nonce is not a durable revision. Activation barriers may protect dependencies,
but never defer revocation. At disclosure/hydration, bind recipient, purpose, artifact digest
and current policy freshness floor. Zanzibar supplies the content/freshness-token precedent;
OpenTelemetry baggage has neither sufficient integrity nor safe default propagation for grants.
No particular authorization database is selected. CMP-022.

## Communication, consultation and interaction

Compare application-native envelopes, ACP session adapters and A2A remote task bridges. They
are composable layers with different jobs, not interchangeable authority systems. The required
questionnaire-assistant-to-Head workflow uses attributable requests, permitted context and
evidence references, explicit advice adoption, current executive leases and conserved parent
reservations. Owner observation, participation, steering and Stop operate over the same durable
events. A provider's programmatic approval reply is not evidence that an Owner saw the action.
CMP-012, CMP-013.

For each of Head relay, direct addressing and bounded shared discussion, freeze the same public
questionnaire fixture and success rubric. Head relay centralizes attribution but can duplicate
context and reasoning. Direct addressing avoids a mandatory relay and needs depth/cycle limits.
Shared discussion supports participation but needs a step lease and conflict rules. None creates
new GoalSpec amendment rights. A delayed response may remain useful evidence while becoming
ineligible for authoritative adoption after an epoch change. The product must make that visible.

A consultation wait is durable logical state, not a blocked Head turn or transport read pump.
Check the operation/resource wait-for graph as well as conversation depth: a Head holding the
only eligible executor while waiting for its consultant can deadlock without an actor cycle.
Use a separate reply-delivery generation so expired replies cannot resume an obsolete turn.
Erlang aliases illustrate suppressing future delivery without cancelling remote computation;
already received evidence remains attributable, and discarded data cannot be reconstructed by
assertion. Full Stop covers owned descendants; for a persistent consultant shared by unrelated
work, stop the borrowed operation and its owned effects, not the whole consultant. CMP-021.

ACP supplies client-agent session negotiation and supported load/resume paths. A2A supplies
opaque agent tasks, artifacts and asynchronous exchange; its cancel is best effort and send
idempotency is optional. Build an outer idempotent command and consultation envelope. Reapply
roots/configuration when a resumed interface requires it. A2A task context is not a GoalSpec
version; an Agent Card is not a Recursion grant. Protocol availability does not establish local
authentication, distribution permission or included-capacity eligibility. CMP-012.

Pi explicitly separates clearing queued steer/follow-up messages from abort. Hermes documents
redirecting busy input separately from Stop and exposes richer Gateway/HTTP/ACP paths. These
counterexamples require queue disposition, selected scope, cancellation delivery and remaining
owned work to appear separately in Stop receipts. Closing a shared server to stop one session
fails if it kills unrelated sessions. Three Stop modes and all ten terminal controls remain
mandatory. CMP-013.

tmux's server/client separation and Zellij's bounded per-client sender are useful view precedents.
Zellij's source explains that its 5000-entry choice is empirical rather than a universal bound.
Reuse the bounded slow-client mechanism, not the number as a product limit. Canonical events
must be committed before lossy presentation, with reserved control capacity and replay or
`RESET + GAP`. Cursor acknowledgement concerns delivery, never effect settlement. CMP-014.

That ordering must begin before the SDK's own ingress queue. The pinned MCP Python client can
evict an old vendor notification when its bounded queue fills; its stdio partial-line buffer
has no observed local line-size cap. Do not place authoritative revocation or settlement only
on a lossy notification path. Require a queryable source plus sequence/gap repair or a stronger
transport; otherwise keep the fact unknown. Bound bytes before JSON parsing. Its dispatcher
also documents deadlock when an inline handler awaits its peer. Reserve control progress across
transport windows, read pump, parser, writer and scheduler, not only the final queue. A biased
Tokio select branch or synchronous Windows pipe output can block that path. CMP-020.

Route admission closes over the helper graph and every pre-effect hook. Hermes can bypass an
explicit auxiliary-provider restriction on selected failures; Gemini next-speaker/loop checks
and availability policy can add calls or change models; OpenCode title/small-model selection
and slash-template substitution precede later hooks. Cursor callback tools execute in the host
without interactive approval, and parent tool restrictions do not constrain all subagent tools.
Use a confined adapter or separately admitted upstream session for each role. Preserve one
retry owner and durable meter segments across counter resets and delayed billing. CMP-032,
CMP-033; exact versioned route changes are owned by ROUTE-CAPABILITIES.md and the overlay.

## Reuse and distribution dispositions

These are inspected repository-license facts and unresolved distribution checks, not legal
clearance or a dependency choice. Provider authentication and commercial service terms remain
separate from an open-source client license.

| Candidate mechanism | Disposition | Inspected license / boundary | Remaining release constraint |
|---|---|---|---|
| T3 reducer/receipt, Pi queue lifecycle | Adapt patterns; evaluate bounded library reuse later | MIT at recorded pins | Preserve notices; audit dependency/API compatibility; no runtime receipt-bus assumption |
| OpenCode plugin loader | Adapt staged lifecycle and failure taxonomy | MIT at recorded pin | Bun import cache and install behavior; isolate imports before any portability claim |
| VS Code extension host | Adapt manifest/lifecycle/placement design | MIT source | Marketplace, extension and branded distribution terms not established by source license |
| Wasmtime | Optional isolation candidate | Apache-2.0 with LLVM exceptions | Host imports, component notices and target support need a specific packaged build |
| systemd / Windows Jobs | Reuse supported OS interfaces through an adapter | systemd mostly LGPL-2.1-or-later with per-file exceptions; Windows platform API | Linux delegation and service policy; supported Windows build, process creation and handle ownership |
| node-pty / portable-pty | Candidate transport reuse, independent of kernel language | MIT family notices inspected | Native dependency/ConPTY binary notices and exact host packaging remain admission inputs |
| Temporal / Orleans | Conditional scheduling/recovery adapter comparison | MIT at pins | Extra service/store or .NET runtime; deployment/update/recovery burden must be counted |
| Restate | Inspect/adapt concepts; don't choose required server now | BSL-1.1, additional-use grant and four-year change to Apache-2.0 | Public Restate Platform Service restriction requires exact distribution analysis; not an unrestricted MIT substitute |
| ACP / A2A / MCP | Reuse eligible protocol adapters | A2A Apache-2.0 source; protocol version separately frozen | Protocol spec does not license every SDK/service or grant OAuth/subscription use |
| tmux / Zellij | Optional view integration/prior art | tmux file-specific ISC/BSD family; Zellij MIT | Host applicability, restart behavior and view semantics; neither is canonical process identity |
| Receiver records / bounded rights | Adapt algorithms; build contract-specific identities and reconciliation | RIFL and bounded-counter papers; no blanket code license inferred | Atomic recipient support, durable rights and stale-client rejection must be established |
| MCP current / Python SDK | Versioned protocol reuse with ingress and continuation adaptation | Current specification mixed Apache/MIT and documentation notices; Python SDK MIT | Global bounds, header/body privacy, loss repair and all-role eligibility; no protocol-derived grant |
| Envoy / Erlang / Tokio patterns | Adapt lifecycle, reply-generation and progress mechanisms | Apache-2.0 / Apache-2.0 / MIT | No framework or language choice; preserve actual acknowledgment and cancellation limits |
| Salsa / Bazel / wrk2 methods | Compare dependency validation, warm pools and offered-load measurements | Salsa Apache-2.0 OR MIT; Bazel and wrk2 Apache-2.0 | Exact dependencies, internal state leakage, key explosion and instrumentation applicability |
| Cursor SDK combination | Compare unmodified supported SDK and first-party ACP; hold modified distribution | Anysphere SDK rights/Terms; independent adapter Apache-2.0 | Adapter license does not grant permission to modify/distribute SDK attribution code |

## What this evidence does and does not decide

Source and implementation inspection justify the candidate boundaries and the negative traces.
Constructed traces describe hypotheses for a future model; no model was run. Local validation
checks documentation bindings, preserved contracts and adversarial evidence records. It cannot
establish cancellation, plugin isolation, provider eligibility, latency, memory or quota savings.
No new route is marked observed or measured. A framework can lower code volume yet increase
operator and recovery burden. Count both, including failed attempts and human verification.

The next decisive work is the bounded admission and probe sequence in [probes.json](probes.json),
then the shared-obligation comparison in [formal-boundaries.md](formal-boundaries.md). No new
consequential Owner choice is yet justified: the accepted directions already permit these
routine research and implementation tradeoffs. Numeric defaults and unavailable personal
inventory are probe inputs, not a manufactured GRILLME queue.

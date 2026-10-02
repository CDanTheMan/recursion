# MCP bridge boundaries and protocol gap closure

Recursion overnight research supplement. Source baseline: repository commit `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. Public specifications inspected 2 October 2026. This supplement addresses architecture edge 39 and cross-cuts edges 7, 8, 17, 25, 28, 30, 35 and 38. All designs and test procedures below are proposals; no target protocol process, provider, model or fixture was executed.

## Main finding

An MCP bridge can normalize messages without normalizing effect guarantees. Recursion needs an explicit bridge profile for each protocol era, transport, implementation version, capability set and effect class. The bridge may translate a protocol result into an observation. It must not translate cancellation, request completion, a task acknowledgement, or a missing task into proof that an external effect is settled.

The accepted canonical admission and effect-settlement boundary is sufficient to express this distinction. It needs precise adapter obligations and fault fixtures before qualification. This is a high-leverage closure target because an apparently convenient generic SDK retry can otherwise bypass the operation ledger shared by the native loop, delegated harnesses and UI.

## Public evidence and bounded interpretation

### Era and identity

MCP 2026-07-28 carries version and capabilities per request. Earlier revisions use initialization-scoped state. The current base specification identifies client/server names as self-reported, not security identities. Schema validation must not automatically resolve external network references, and resource bounds are recommended. These are protocol requirements, not proof of any installed implementation. [P01]

The versioning specification describes transport-specific detection and dual-era interoperability. A recognized modern version error is not a reason to fall back to legacy semantics. [P02]

**Inference for Recursion:** bind the selected era to a verified adapter/configuration identity. A displayed server name is unsuitable as a permission principal. Authentication binding, declared capability, configured permission, observed conformance and legal entitlement remain independent records.

### Stream framing and restart

The standard stdio binding uses newline-delimited JSON-RPC on stdout; stderr is a separate logging channel. Modern servers do not initiate JSON-RPC requests. The binding recommends process restart after unexpected termination and says lost in-flight requests can be retried. It also distinguishes graceful EOF from forced termination. [P03]

**Inference for Recursion:** the protocol's ability to resend is not an application-level idempotency guarantee. A write could have committed before its response was lost. Therefore the accepted canonical effect contract must decide whether a retry is safe, regardless of what a generic SDK does. A process restart does not grant permission to launch a new logical effect.

### Multi round trip requests

MRTR uses `input_required`, input request keys, optional opaque `requestState`, and a new JSON-RPC ID on each retry. Clients must echo state without interpreting or changing it. State integrity, principal/parameter binding and expiry can limit replay, but single-use requires server-side enforcement. [P04]

**Inference for Recursion:** distinguish the stable logical operation from its wire attempts. An input request can create a bounded pending interaction without refreshing the parent budget or deadline. The opaque token remains transport data, never a grant. Recursion may record its byte identity and size for integrity/accounting without parsing its meaning or asserting what it authorizes.

### Cancellation and asynchronous tasks

For ordinary cancellation, stdio sends a notification and HTTP closes the request response stream. The general cancellation page uses SHOULD wording about stopping/responding, while the stdio binding says no further messages may be sent for a cancelled request. Neither wording supplies an external-effect rollback guarantee. Treat the discrepancy as a conformance-profile detail rather than silently choosing the more convenient reading. The timeout guidance includes an absolute maximum despite progress updates. [P03, P05]

The Tasks extension uses a server-generated task handle, task polling/update/cancel operations, and per-request opt-in. Cancellation is cooperative; its acknowledgement does not guarantee eventual cancellation. Task state may be discarded after TTL. A task with status `completed` can contain a tool result with `isError: true`. Task input responses use `tasks/update`, not an MRTR retry of the original tool call. [P06]

**Inference for Recursion:** do not inherit the extension's permission to discard client task state after sending cancel when Recursion still has an unresolved effect or reservation. Retaining the canonical evidence and uncertainty is a stricter application policy, not a claim that MCP requires it.

Authorization is a separate profile dimension; the single documented transport/auth distinction is in [R-G’s auth fact cell](../rg/report.md#mcp-authorization-facts).

### Tool descriptions and trust

MCP 2026-07-28 requires treating tool annotations as untrusted unless they come from trusted servers. Tool schemas and typed/multimodal results describe the interface, not an effect grant. [Tool specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

**Inference for Recursion:** preserve description provenance, but independently admit the actual operation under current authority. A trusted-server designation cannot substitute for a grant.

### SDK names are not wire semantics

The Go SDK documentation retains a `ClientSession` abstraction across both eras. The TypeScript migration page distinguishes modern per-request behavior from legacy semantics. SDK object names alone cannot establish a handshake, protocol session, task compatibility or authority boundary. [P07, P08]

## Candidate bridge designs

### B1 Typed bounded boundary with era specific codec

Use a common canonical operation envelope and a small codec/profile per era and transport. The envelope binds operation identity, original effect parameters, current authority, capability profile, configuration identity, privacy scope, budget reservations and evidence requirements. The codec owns wire correlation, not policy. A separate process supervisor owns lifetime and containment.

The strongest benefit is auditability across native and delegated tool use. Costs include explicit translation code, conformance fixtures and maintaining loss reports as SDKs evolve.

Competing option: B2, an SDK-centred bridge with complete canonical interception and intermediate observations under the same authority, uncertainty and resource invariants. A final-result-only wrapper is a negative control, not an eligible rival. Decisive falsifier: a supported interaction cannot preserve the same permission, pending-input, uncertainty or settlement observations without leaking SDK state into the canonical reducer. A passing fixture does not prove remote tool idempotence, credential isolation or legal entitlement.

### B2 SDK centred bridge with a thin effect adapter

Allow the SDK to manage protocol details, while intercepting every outgoing operation, continuation, retry and background task transition at the canonical boundary. This may reduce protocol maintenance and improve compatibility.

Competing option: B1. Decisive falsifier: the SDK can resend a side-effecting call, invoke sampling, renew a task, follow an external schema reference, or broaden capabilities without an observable intercept. Documented hooks are not sufficient; exact-build conformance must demonstrate the interception path. A passing result does not prove hooks remain stable after upgrades.

### B3 One isolated process per operation

Isolate a bounded invocation in its own process rather than sharing an MCP server across unrelated work. This offers simple failure attribution but may conflict with intended server lifetime, destroy useful caching, lose task handles, and increase latency and memory.

Competing option: shared process with bounded per-operation demultiplexing and explicit privacy isolation. Decisive falsifier: either design cannot preserve a pending operation across cancellation/restart without misattributing messages or repeating effects. A passing synthetic process test does not prove application state or credential separation. This is a topology candidate, not a language or framework selection.

## Proposed admission and retention rules

These are candidate refinements of the existing contract, not new accepted schema names.

1. Persist the stable operation identity and complete admitted effect before any outbound effecting request. Allocate distinct wire attempt IDs beneath it.
2. Resolve route era and capabilities before sending an era-ambiguous effecting method. Discovery failure may narrow eligibility; it may not silently relax authority.
3. Bind every returned request/task identifier to the verified route and operation. Equal task IDs from different servers are not the same task.
4. Preserve protocol status, tool-level status and application verification as separate observations. A successful RPC with an error tool result is not a successful task outcome.
5. MRTR retries preserve original effect parameters, parent deadline and reservation lineage. Any material change is a new admission decision. Opaque state is size-bounded and retained only under its privacy/retention policy.
6. A local timeout closes admission for new attempts and enters reconciliation when dispatch may have occurred. It does not create a fresh operation ID to evade deduplication.
7. A task handle is durable adapter correlation, not a canonical task owner. Revoke or stop still acts through current application authority. The remote task may remain running after local cancellation.
8. A vanished or expired task is an unavailable observation. It is not evidence of failure, cancellation, absence of side effects or zero usage.
9. Late messages may be preserved as evidence without being adopted into current state. The wire protocol's instruction to ignore a response does not require erasing useful raw provenance from an appropriately protected evidence channel.
10. Never execute sampling just because the server asks. Any model-backed helper requires its own eligible, budgeted, authorized route. An upstream-only workflow cannot silently become native-model-dependent.

## Finite resource profile

Define and measure separate finite ceilings for: bytes before a newline; complete JSON frame size; JSON depth and member count; schema depth/subschema count/validation work; input-required rounds; outstanding requests; pending user interactions; opaque state bytes; task handles; subscription streams; notification bytes and rate; artifact and stderr retention; process memory; absolute operation lifetime; retry count; polling work; and teardown time.

Do not invent universal numeric defaults from this research. The smallest decision is to adopt the dimensions and overload behavior, then compare candidate values against the same local corpus. Every ceiling needs a declared outcome: reject before dispatch, truncate only non-authoritative display data with a loss marker, pause/hold the operation, or quarantine the peer. Dropping an effect receipt or approval is not a permissible generic backpressure policy.

A shared stdout channel makes head-of-line blocking a real architectural question. Reader consumption, decoding, persistence and rendering need separate bounded queues. Keep a reserved control path or prove the saturated path can deliver Stop within the accepted bound. This proposal competes with a single simpler queue. Its falsifier is a saturation trace that delays Stop indefinitely or loses a mandatory effect observation. Passing does not prove fairness under an unbounded adversary.

## Local discriminating fixtures

All are UNEXECUTED handoffs. Use only a synthetic peer and synthetic artifacts; do not connect to production servers or providers. Local sessions must first select the exact candidate implementation, authorized disposable environment and independent oracle. Preserve raw byte traces, canonical events, queue/limit observations and fixture hashes. Do not derive the oracle from the candidate reducer.

Common stop conditions for MCP01–MCP10: do not start until the candidate/profile, synthetic peer, finite resource/deadline limits, safe teardown and observer coverage are fixed. Abort the affected fixture on unexpected external network access, a real credential or production path, scope/privilege expansion, observer loss, an unbounded queue, or an exceeded hard resource/time ceiling. Preserve available evidence and mark missing observation unknown; never continue until a timeout becomes a pass. Stop after the preregistered trace completes or its first decisive failure is witnessed. A deliberate negative-control failure is recorded as such, then safely torn down; it does not authorize weakening the boundary or retrying a real effect. Halt the campaign if the synthetic positive control or independent oracle fails. No fixture permits unrelated-process termination or changes to host security settings.

### MCP01 Effect committed before lost response
**Eligible comparison:** B1 explicit era-specific codec versus B2 SDK bridge with complete canonical interception and intermediate observations; hold required semantics, bounds and oracles identical.


The peer records one synthetic effect, then closes stdout before its response. Restart and exercise normal recovery. The oracle expects one logical effect, stable identity and unresolved status until reconciliation. A second effect or a fresh identity is a failure. Negative control: unconditional SDK retry. This closes retry ownership for that profile only, not remote exactly-once delivery.

### MCP02 Era downgrade before a write

**Eligible comparison:** B1 explicit era-specific codec versus B2 SDK bridge with complete canonical interception and intermediate observations; hold required semantics, bounds and oracles identical.

A peer rejects discovery with a modern unsupported-version response; a second peer behaves as legacy. Observe different, explicit profile paths before any write. Any modern error that silently selects a legacy write path fails. Negative control: trial tools/call detection. Passing does not authenticate the peer.

### MCP03 Replayed approval across MRTR attempts

**Eligible comparison:** B1 explicit era-specific codec versus B2 SDK bridge with complete canonical interception and intermediate observations; hold required semantics, bounds and oracles identical.

Issue the same pending input twice, reconnect the UI, then alter one effect parameter and re-present its response token. The first duplicate should not duplicate the user interaction; the changed effect must not inherit approval. Wire IDs may change while logical identity remains stable. Negative control: wire-ID-only correlation. Passing proves this bounded binding test, not universal prompt-injection resistance.

### MCP04 Cancellation and delayed effect evidence

**Eligible comparison:** B1 explicit era-specific codec versus B2 SDK bridge with complete canonical interception and intermediate observations; hold required semantics, bounds and oracles identical.

Run two distinct cases after a synthetic effect crosses the peer boundary. In the ordinary stdio case, send notifications/cancelled and expect no protocol acknowledgement; in the ordinary HTTP case, close the response stream. In the separate Tasks case, return the specified empty tasks/cancel acknowledgement while leaving the effect unresolved. Later supply an independently correlated observation through a permitted reconciliation channel, not an invented ordinary cancellation ACK. UI and ledger must show requested/uncertain/settled transitions honestly, never immediate rollback. Negative control: cancel ACK becomes terminal success. Passing does not stop an uncooperative remote process.

### MCP05 Task TTL expires without final result

**Eligible comparison:** B1 explicit era-specific codec versus B2 SDK bridge with complete canonical interception and intermediate observations; hold required semantics, bounds and oracles identical.

Return a task handle, then expire it while its synthetic effect remains observable elsewhere. Expect preserved uncertainty and reservation, not zero usage or failed effect. Negative control: task disappearance releases budget. Passing covers retention bookkeeping, not remote data-deletion compliance.

### MCP06 Task completed with tool error

**Eligible comparison:** B1 explicit era-specific codec versus B2 SDK bridge with complete canonical interception and intermediate observations; hold required semantics, bounds and oracles identical.

Return `completed` plus `isError: true`. Expect completed protocol exchange, failed tool-level outcome, and no verified-goal success. Negative control: status-only adoption. Passing does not assess the truthfulness of peer output.

### MCP07 Resource and control saturation

**Eligible comparison:** B1 explicit era-specific codec versus B2 SDK bridge with complete canonical interception and intermediate observations; hold required semantics, bounds and oracles identical.

Stream an oversized incomplete line, excessive well-formed notifications, deep schema, stderr flood and full artifact queue in separate cases. Issue Stop. The oracle checks bounded resource behavior, preserved mandatory observations and declared overload outcomes. Negative control: read-all-then-parse or shared unbounded queue. Passing one maximum is not a universal bound; repeat around every selected threshold.

### MCP08 Hidden sampling in an upstream only workflow

**Eligible comparison:** B1 explicit era-specific codec versus B2 SDK bridge with complete canonical interception and intermediate observations; hold required semantics, bounds and oracles identical.

A synthetic peer returns a sampling request during resources/read or tools/call. The workflow lacks a native inference route. Expect explicit refusal or a separately eligible upstream-only continuation, with no model invocation. Negative control: automatic SDK sampling helper. Passing does not establish all third-party SDK paths are intercepted.

### MCP09 Opaque state across privacy scopes

**Eligible comparison:** B1 explicit era-specific codec versus B2 SDK bridge with complete canonical interception and intermediate observations; hold required semantics, bounds and oracles identical.

Return an opaque continuation for project A and try to use it through project B or another route. The bridge must reject the cross-scope association without parsing the token. Negative control: global continuation cache keyed only by server string. Passing does not establish the server's own cryptographic binding.

### MCP10 Shared process message attribution

**Eligible comparison:** B3 isolated operation process versus a bounded shared process with scoped demultiplexing and explicit privacy isolation; hold required semantics, bounds and oracles identical.

Interleave two operation IDs, subscription notifications, cancelled replies and identical task strings across two peers. Every observation must retain its full correlation domain. Negative control: process-global current task. Passing does not prove application-level independence of state inside one server process.

## Leverage order and landing

First close MCP01, MCP03 and MCP04: these determine whether generic reuse is compatible with canonical effect safety. Next MCP02, MCP08 and MCP09: these prevent compatibility and helper features from expanding authority. Then MCP05, MCP06 and MCP10: these protect honest state and attribution. MCP07 is a release-blocking boundedness campaign that should begin alongside the first group, not be postponed until a GUI exists.

Land proposed adapter obligations in the existing broker/tool/capability contracts; codec compatibility in route profiles; pending interactions in the shared command/query object model; resource limits in configuration and performance profiles; and synthetic fixtures in the appropriate local conformance lane. Do not create another executive, writer, scheduler, approval store or source of task truth.

The protocol bridge qualifies only after exact-build local receipts and independent reruns establish the named profile. This report closes a research-ownership gap by naming the mechanisms and discriminating tests. It does not close execution qualification.

## Sources

P01. MCP base protocol, revision 2026-07-28. https://modelcontextprotocol.io/specification/2026-07-28/basic

P02. MCP versioning and compatibility, revision 2026-07-28. https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning

P03. MCP stdio binding, revision 2026-07-28. https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio

P04. MCP multi round-trip requests, revision 2026-07-28. https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr

P05. MCP cancellation, revision 2026-07-28. https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/cancellation

P06. MCP Tasks extension, versioned 2026-07-28 page. https://tasks.extensions.modelcontextprotocol.io/specification/2026-07-28/tasks

P07. MCP Go SDK lifecycle documentation, mutable page, retrieved 2026-10-02. https://go.sdk.modelcontextprotocol.io/protocol/

P08. MCP TypeScript SDK 2026-07-28 migration documentation, mutable page, retrieved 2026-10-02. https://ts.sdk.modelcontextprotocol.io/v2/migration/support-2026-07-28

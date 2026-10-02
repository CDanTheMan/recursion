# Recursion: candidate native-harness and orchestration architectures

Date: 2026-10-02 UTC  
Status: research/design candidate; not an Owner decision, implementation acceptance, or route qualification  
Authoritative source snapshot: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
Scope: static repository inspection and current public primary-source research only

## 1. Decision-ready answer

The strongest candidate is a **Recursion-owned authority and continuity spine with two first-class execution paths**: a small native model/tool loop whose control flow Recursion owns, and replaceable upstream harnesses reached through typed delegation adapters. Context, runtime processes and upstream sessions are reconstructable working state; accepted intent, authority, operation identity, reservations and verified outcomes survive their replacement.

Use the accepted four-function deterministic kernel plus a separately checkable bounded broker refinement as the first comparison arm. Keep a broker-inclusive formal model as a serious challenger over exactly the same observations and fault traces. Move a broker fact into the aggregate whenever otherwise the mapping hides an authority, lifecycle or accounting race. “Four functions” measures the semantic interface, not permission to omit real execution behavior.

The deployment comparison should have three complete candidates:

1. **A: receiver-recorded services** — canonical intent/receipt transactions plus bounded per-operation delivery records; services activate when work needs them; optional warm pools remain possible
2. **B: bounded resident session hub** — the same authority contract, with session/stream/interaction coordination resident for responsive interactive work; actors remain durable identities rather than immortal model processes
3. **C: subordinate durable workflow assistance** — the same authority contract, with a workflow/actor runtime helping timers and continuations; its journal cannot become an independent authority, budget or effect-success ledger

A is the best first falsifiable baseline, not an accepted winner. B may win responsiveness under repeated interactive use. C may win correctness/maintenance effort for many delayed operations. Compare activation policy, resident working set and durable continuation separately; a demand-activated service can be durable, and a resident hub can lose everything on crash.

Every candidate includes the comprehensive D-019 capability surface through supported opt-in components. This is a construction and placement comparison, not a smaller release proposal. No language, database, framework, terminal toolkit, model vendor or sandbox is selected here. The native loop is not an embedded upstream SDK wearing a Recursion name. Upstream-only mode must close every reasoning role through eligible upstream routes or deterministic behavior; no concealed native planner, compactor, reviewer, router or recovery model is permitted.

**What remains unknown:** Recursion's quality/cost/latency advantage, strong credential non-access on every D-028 profile, all required adapter control semantics, full broker refinement, durable writer performance, disabled-plugin inertness, automatic failover correctness, semantic compaction fidelity and plugin-porting economics. None is converted to zero or assumed solved by this design.

## 2. Authority and evidence ledger

### 2.1 Accepted constraints preserved

| Decision | Architectural consequence |
|---|---|
| D-017 | Greenfield v3. Historical v2 state/migration machinery is not a runtime dependency or authorization source |
| D-018 | Native and upstream are independently useful product paths, sharing authority/evidence contracts |
| D-019 | Build the accepted comprehensive surface; lean defaults and opt-in installation do not remove capability gates |
| D-020 | Single-node core; monotonic fencing and store/availability seam in core; replicated takeover optional first-party capability, required when the specified autonomous availability mode is selected |
| D-021, D-029, D-030 | Prefer user-authenticated harness delegation; operator-provisioned trusted launch outside Recursion's readable domain; fan-out uses admitted harness-native facilities; per-route counsel gate survives |
| D-022 | Aggressive, Full and Lazy Stops plus checkpoint/interrupt/drain; never conflate cancellation with rollback |
| D-023 | Codex App Server qualification first; this is priority, not proof of stability, entitlement or fitness |
| D-024 | Six productive-continuity journeys are the acceptance spine; feature counts are not the endpoint |
| D-025 | Continuing autonomous research is bounded, optional, off by default, unable to activate or approve itself |
| D-026, D-027 | Apache-2.0 direction and counsel packet only; no public-release clearance follows |
| D-028 | Exact Windows/Linux/storage floors; WSL2 is development/test evidence, not production qualification |
| D-031 | Measure workload-specific savings; no attribution of vendor intent |
| D-032 | Active parent is the v3 harness/orchestrator goal |
| D-033 | Porting advantage is a hypothesis; acceptable ports and savings can be zero |

`CONTROL_PLANE.md`, `ANCHOR.md`, `state/DECISIONS.md` and the active goal were inspected. The report also read PRODUCT, ARCHITECTURE, CONTEXT, INTERFACE-STRATEGY, PLUGINS-AND-EDITIONS, the research index/coverage/gaps/synthesis, R-A/R-B reconciliation, FU-03/FU-05 syntheses and frozen M1B/M1C contracts. Repository facts refer to the pinned snapshot, not a running deployment.

### 2.2 Drift must not become design authority

- START-HERE and ARCHITECTURE retain passages asserting operative Hermes governance and v2 migration. D-017 and current CONTROL_PLANE supersede that interpretation. Preserve historical reasoning, but do not build a retired supervisor.
- PRODUCT/INTERFACE-STRATEGY say a dedicated GUI is later/outside the initial contract, while D-019 explicitly lists GUI among previously proposed deferrals now built opt-in. This packet uses TUI-first construction and one later GUI-compatible backend. It does **not** silently waive D-019's release obligation. Reconcile the public wording before release planning.
- The original GAPS prose says no formal model/vectors or OS cells exist. Later files contain reduced formal runs and partial host/WSL traces. Correct statement: the **full new qualification gates remain open**, not “nothing exists.”
- The frozen M1 contracts encode `current-immediate`; D-022 settles vocabulary but does not itself rewrite their bytes. Any additional executable stop policy requires an explicit compatibility/new-epoch mapping. No retrofit of candidate CBOR/JCS or new refusal codes into frozen epochs.
- D-020 closes the availability decision; D-028 closes floor selection. The remaining work is contract conformance, not asking those questions again.
- ARCHITECTURE-COVERAGE's final R-P…R-Y frontier mapping is stale relative to the issued brief titles. Use the actual brief namespace: P injection, Q memory, R autonomy, S adaptation, T multimodal, U isolation/supply chain, V observability/replay, W evaluation, X node fabric and Y workspace. Forks, quarantine, accessibility and MCP remain cross-cutting obligations; do not invent dedicated lane owners from the stale map.

### 2.3 Evidence classes

- **Repository-observed:** files, schemas, interfaces and recorded results visible in the pinned tree
- **Repository-reported:** historical execution claims read but not rerun here
- **Public source-documented:** behavior described by official documentation, maintainer source, or a research paper
- **Design inference/proposal:** the architecture in this report
- **Unmeasured/unverified:** local empirical fit and any property without accepted runtime evidence

The FU-03 summary reports a reduced kernel baseline with 727 distinct states. The later [gap evidence audit](../gaps/report.md#3-fu-03-what-the-committed-evidence-does-establish) reconciles the integrated-style diagnostic model to **four fresh command IDs**, a nominal six-event cap and at most four accepted baseline transitions. It records five kills among seven instantiated diagnostic mutants, not the full 36-row gate. M03 is killed by TypeOK, not demonstrated full-spec ChainIntegrity sensitivity; current mutation sites are diagnostic analogues with registry-semantic differences. M25 and M31 lack accepted exposure/equivalence classifications; not killed within this bound is not evidence of safety.

The gap audit supplies an [unexecuted seven-step witness](../gaps/fu03-candidate-witness.json) for a deliberately enlarged diagnostic state space with at least seven fresh IDs and seven events. GrantLease -> Start -> PrepareEffect -> MarkDispatch -> SubmitFail -> ArmTimer -> FireTimer would, by static inference, set retryReady while the effect remains InFlight. This is a candidate timer/invariant semantic conflict requiring independent reproduction, **not** a counterexample to the executed four-ID run or a finding about the richer full candidate model. Do not weaken the invariant or silently enlarge a bound to manufacture mutant acceptance.

The [FU-04 audit](../gaps/report.md#4-fu-04-raw-counts-actual-mechanisms-and-oracle-limits) reads **13 run rows: 12 recorded pass, 0 fail and 1 unknown, plus 10 not-run rows**, covering 10 unique PF IDs. Four separate safe host probes are not four additional qualified cells; zero platform profiles are qualified. Narrow the recorded passes to their actual oracles: for example, file-size/fsync/replace observations do not prove VM-reset durability or exact replay, and mkdir/manual-epoch observations do not prove receiver fencing. The WSL fault-trigger flag parsing defect and non-independent booleans further limit generic PASS interpretation. See the [complete evidence ledger](../gaps/complete-ledger.md) for row-specific support, controls and non-proofs.

These are attributed static reconciliations of repository-reported evidence. This session ran no target checker, runtime, model, provider, harness or destructive test. Useful historical observations remain evidence; unqualified does not mean no evidence exists.

## 3. What the external evidence actually changes

| Primary source | Narrow finding | Design consequence and limit |
|---|---|---|
| [Anthropic Managed Agents, 2026-04-08](https://www.anthropic.com/engineering/managed-agents) | Separates session log, harness and sandbox; context storage remains outside the active context window | Supports separable interfaces and reconstructable execution. Its hosted architecture and vault/proxy mechanisms do not prove Recursion's non-intermediation or local resource profile |
| [Temporal workflow definition](https://docs.temporal.io/workflow-definition) | Replay requires deterministic command behavior; nondeterministic operations belong outside that path | A workflow helper must emit admitted proposals. Retry/availability machinery cannot prove an external effect's outcome or satisfy Recursion authority on its own |
| [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | Thread checkpoints and cross-thread stores are distinct; in-memory checkpoints do not survive restart | Persistence APIs are useful candidates, but neither graph state nor a memory store is automatically the canonical authority ledger |
| [Orleans lifecycle](https://learn.microsoft.com/en-us/dotnet/orleans/grains/grain-lifecycle), [timers/reminders](https://learn.microsoft.com/en-us/dotnet/orleans/grains/timers-and-reminders) | Activation/deactivation and persistent reminders are separate; crash can omit deactivation, and missed reminder ticks are not retained | Do not depend on cleanup callbacks for settlement or assume a timer offers durable occurrence semantics |
| [Pi agent core](https://github.com/earendil-works/pi/tree/main/packages/agent) | Separates context transform/conversion, model response, tool preflight/execution and follow-up; completion order can differ from transcript order | Useful minimal-loop mechanism reference. Adopting its whole loop would require semantic qualification; event names and hooks are not a proof of Recursion's pre-effect boundary |
| [Codex App Server facts](../rf/report.md#codex-app-server-facts) | Canonical documented profile in R-F §1.2 | Qualify exact build, transport, method and policy combinations. A rich structured interface is not an all-methods containment guarantee |
| [OpenCode server facts](../rf/report.md#opencode-server-facts) | Canonical legacy profile in R-F §1.9 | Useful alternate interface shape for stress testing backend/renderer separation. Do not select it or infer cross-harness semantic parity |
| [A2A specification](https://a2a-protocol.org/latest/specification/) | Remote task cancellation is an attempted operation, not guaranteed completion | Agent task status is an external observation; no room or adapter may promote cancel acknowledgment to settled effects |
| [MCP security guidance, 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) | Token audience separation and caller binding are necessary; possession of an application handle is not authentication | Keep principal/authority independent of protocol handles and prohibit credential passthrough shortcuts. MCP conformance is not a grant |

Three fresh preprints deserve bounded influence:

- [Harness Engineering, arXiv:2609.00006v1](https://arxiv.org/html/2609.00006v1) is a source-study map, useful for locating patterns to recheck in exact upstream commits. Its illustrative minimal harness is explicitly non-production and conjectures benchmark performance without proof. It cannot establish comparative Recursion fit or authorize copying proprietary-derived material; use it as a lead register, not an acceptance oracle.
<a id="minimal-harness-paper-facts"></a>
- [How Much of a Harness…, arXiv:2609.40303v1](https://arxiv.org/html/2609.40303v1) compares Malena with elaborate MLE systems on selected MLE-bench/NatureBench tasks under matched backbones and time budgets, reporting no frontier-backbone advantage for the elaborate alternatives. It names contamination, statistical-power, tuning-asymmetry and coordination-scope limits. Appendix A.5 conditions bootstrap intervals on a fixed task set; costs include modeled cache reads. **I:** benchmark a strong simple native baseline. Nonsignificance does not establish equivalence or negate required rooms, recovery, authority, portability or UI capabilities; those endpoints do not accept them.
<a id="harness-tokenomics-facts"></a>
- [Harness Tokenomics, arXiv:2609.28919v2](https://arxiv.org/html/2609.28919v2) motivates cache-aware switch boundaries and total-workflow accounting. Its savings are emulated from synthetic enterprise scenarios, public traces and one vendor's dated list prices, with taxonomy and task-quality limitations. No percentage transfers to Recursion or subscription debit. The transferable object is a preregistered payback test with observed counters.

The recommended architecture is derived from the accepted Recursion contracts; these sources supply mechanisms and challenges, not product authority.

## 4. Shared semantic architecture

### 4.1 Four kernel functions and the non-pure shell

Proposed semantic signatures, **not new frozen API names or bytes**:

1. `decode(bytes, schema_profile) -> typed_command | refusal`: strict schema and canonical-byte rules; reject unknown arms, duplicate fields and unbounded inputs under the selected profile
2. `admit(state_at_sequence, command, verified_facts) -> event_candidate | prior_receipt | refusal`: current principal, authority, revision, epoch, privacy, route, budget and idempotency checks; facts are explicit authenticated inputs, not reads hidden inside a pure function
3. `reduce(state, admitted_event) -> new_state`: deterministic canonical transition and derived projections; no model, OS, database, wall-clock or network invocation
4. `derive_work_packet(state, admitted_operation) -> immutable_packet | refusal`: exact executable scope, required evidence and all relevant bindings; no effect occurs here

A small **kernel service shell** authenticates ingress, obtains current canonical state, supplies trusted observations and performs the chosen store transaction. It atomically binds command identity, event sequence, state transition, reservation and dispatch intent. If the expected sequence/fence no longer matches, it rereads and readmits; a stale successful `admit` result is not reusable authorization. Only after durable commit may a broker offer the operation to a recipient. An accepted command receipt is not a dispatch or success receipt.

This is the central dual-write problem. Avoid “write state, then best-effort enqueue” and “enqueue, then remember it.” A transactional dispatch-intent record, or an equivalent proven atomic boundary, is required. The selected store may implement it differently. No particular outbox table, serialization or database is selected.

The external receiver separately checks current recipient-side operation/fence scope immediately before its effect boundary. A kernel commit cannot retroactively erase an already-issued remote permit. Different clocks, epochs and lost messages remain in the model.

### 4.2 Identity inventory

| Identity | Lifetime / owner | Never equate it with |
|---|---|---|
| PrincipalId / grant revision | Owner/authority service | UI account label, model name, room membership |
| ProjectId / workspace binding | Canonical project record; exact root/source/privacy bindings | A current directory string |
| GoalId + GoalRevision | Accepted outcome and authority contract | Conversation/session |
| AssistantId / RoleLeaseId | Durable logical assistant; bounded assignment | A running model or executable |
| TaskId + PlanRevision | Bounded work under a goal | An upstream job id |
| RunId / AttemptId | One admitted run and numbered execution attempts | Successful outcome |
| SessionBindingId / TurnId | Adapter-local session mapping with route epoch | Portable task state |
| OperationId / EffectId / IdempotencyKey | Canonically recorded before dispatch | A transport request id or retry count |
| QuestionId / ApprovalId | Exact interaction, action digest, revision, expiry and intended principal | A chat reply or “yes” attached to the wrong waiter |
| ContextEpoch / CapsuleId | One accepted context transition and its manifest | Prompt cache key or model summary |
| ArtifactId / EvidenceId | Source/output identity and provenance | Model assertion of correctness |
| NodeId + Incarnation / ProcessScopeId | Enrolled node and exact lifecycle scope | Hostname/PID alone |
| RouteProfileId + qualification revision | Harness/interface/build, provider/model, pool, credential reference, host and sandbox evidence | A model dropdown |
| PoolId / ReservationId / MeterSegmentId | Componentwise allowance and observation-source ledger | A token count assumed to represent subscription debit |
| WriterFence / WorkLeaseEpoch / AdmissionEpoch / ProcessEpoch / ConfigEpoch | Separate invalidation domains | One universal “epoch” that accidentally blesses unrelated state |

Classify credential and launch references by their actual authority, not their opacity or name. A locator that requires a separately authenticated principal and current grant differs from a bearer-like handle whose possession permits invocation or credential use. The latter is sensitive authority and needs protection, attenuation, expiry and revocation. Neither kind of reference demonstrates provider-secret non-access; do not expose a bearer-like launch reference as harmless metadata. Cross-domain artifact handles must not expose raw private-content equality. Event order is canonical sequence; source timestamps remain evidence and must not silently reorder decisions.

### 4.3 Ownership contract

| Component | May own | Cannot own |
|---|---|---|
| Kernel + atomic writer seam | Accepted state, authority/budgets/fences, operation and evidence classification, publication gate | Model decisions, prompt heuristics, renderer state |
| Native loop service | Sampling/tool cycle and turn-local ordering; candidate checkpoints | Grants, canonical writer, hidden fallback or acceptance of its own work |
| Upstream adapter | Protocol/session mapping, declared control losses, source event normalization | Recursion authority, credential custody without grant, semantic invention of absent receipts |
| Process/effect broker | Admitted dispatch, owned process scope, delivery/replay, reconciliation observations | Goal amendment, budget renewal, proof that killed PID rolled back external work |
| Trusted launcher | Operator-provisioned launch profiles and protected credential-domain boundary | Semantic task planning or arbitrary privileged shell service |
| Context compiler/governor | Candidate assembly, one accepted compaction transition through kernel | Accepted directive mutation or independent context authority |
| Scheduler | Due occurrence proposals and retry timing inside policy | New goals, self-activation, renewed allowances |
| Room coordinator | Bounded workflow-step coordination lease | Standing executive or authority through consensus |
| Plugin resolver/worker | Bounded metadata resolution, admitted capability implementation | Import during discovery, bypassing grants, direct canonical writes |
| CLI/TUI/GUI | Query projections and authenticated commands | Actor lifetime, independent settings truth or effect execution |
| Verifier | Exact-candidate observations, independent assessment | Implicit publication or self-acceptance |

## 5. Competing complete candidates

### Candidate A: receiver-recorded services

The core writer persists intent and receipts. A lightweight deterministic scheduler discovers eligible pending operations. Per-operation receivers retain delivery/attempt state sufficient to reconcile a crash. Native loop, upstream adapters, context workers and room coordinators activate as needed; the process broker remains available while it owns live processes. Runtime caches can be evicted without losing authority.

Strengths: clean minimum boot/recovery closure; explicit boundaries; small disabled footprint is plausible; easier attribution of what each component adds. Costs: Recursion must correctly implement timers, deduplication, dispatch recovery, asynchronous interactions and multiple operation records. This is not free simplicity.

**Competitor:** B's resident coordinator or C's workflow assistance. **Falsifier:** repeated interactive cold activation violates the declared responsiveness floor, or custom continuation code increases verified defect/review burden more than an equivalent helper saves. **Non-proof:** source simplicity and fewer dependencies do not establish resource efficiency or safety.

### Candidate B: bounded resident session hub

Keep active route sessions, stream parsers, question waiters and hot context indexes in a bounded resident coordinator. It still uses the same canonical writer and kernel. Idle sessions may expire without ending logical tasks; unload never drops pending questions, admitted operation identities or unsettled reservations. Every warm cache has explicit eviction/rebuild semantics.

Strengths: low repeated-attach and steering latency, amortized protocol setup, controlled shared stream fan-out. Costs: resident memory, coupled overload, more complicated eviction, security exposure through long-lived sessions, possible accidental hidden keepalives.

**Competitor:** A plus bounded warm pools, holding durability fixed. **Falsifier:** B has no predeclared responsiveness improvement after startup is amortized, breaches idle/overload ceilings, or needs periodic inference merely to stay healthy. **Non-proof:** residency is not durability; a live upstream session is not a recoverable task.

### Candidate C: subordinate durable workflow assistance

A durable workflow or virtual-actor layer tracks wait/retry/timer continuation, with each activity producing an immutable canonical command or performing one already-admitted effect. The canonical OperationId crosses the helper boundary. The kernel remains the sole authority and accepted-outcome writer. Helper restart must reconcile its history with canonical receipts before requesting new dispatch.

Strengths: reusable durable wakeups, long waits, resumable code and operator tools. Costs: second journal coordination, framework upgrade semantics, hidden automatic retries, larger install/operational closure, possible foreign-client state dependency.

**Competitor:** A with receiver-owned records; compare at identical residency and complete workload. **Falsifier:** the helper cannot boot/reconcile without becoming an authority writer, retries ambiguous external effects, or adds more operational/review burden than it removes. **Non-proof:** replay of helper code is not exactly-once external effects, task authorization or D-028 crash durability.

### Independent configuration axes

| Axis | Values to compare | What must remain fixed |
|---|---|---|
| Activation | Request-driven; event/timer-driven; admitted prewarm | Same permitted work, no speculative unapproved inference |
| Residency | Evictable; bounded warm pool; resident active coordinator | Same cold-recovery state and authority semantics |
| Durability | Canonical receiver records; subordinate workflow journal | Same fault history, occurrence policy and effect ambiguity |
| Proof boundary | Kernel + broker refinement; broker-inclusive model | Same observations, bounds, faults, fairness and acceptance |
| Placement | Local service; isolated worker; enrolled remote node | Same grants, privacy, identity and route controls |
| Packaging | Core; selected profile; full installed-disabled | Same supported capabilities, zero disabled effects |

Do not publish one composite winner. Hard correctness/authority/recovery floors come first. Then compare responsiveness, subscription efficiency and completion under the accepted ranking, preserving maintenance, human review and resource costs separately.

## 6. Formal split versus broker-inclusive challenger

### 6.1 Required common observation set

Both proofs expose canonical command/event order, exact authority/revision, current leases/fences, operation identity, effect state, outstanding reservations, pending interactions, source/candidate identity, release/config revision, owned process scope and reconstruction gaps. Broker-local queue positions may stutter only if no required observation changes.

Six preserved M1 obligations: M1A-to-M1C effect identity join; distinct fence namespaces; one canonical writer; operative PAUSE behavior; partition/termination ambiguity; bounded broker flow/replay with explicit RESET. Add process birth/ownership, relaunchers, consultation delivery/adoption, queue saturation, update/Stop order, config propagation, fork allowance and source-cut preservation.

### 6.2 Split proof obligations

1. Every concrete broker transition either maps to one allowed aggregate transition or leaves all observations unchanged
2. Every non-stuttering transition carries the identity and evidence required by that aggregate transition
3. Delivery, recipient installation, local revocation and remote cancellation are distinct steps
4. Admission/commit/dispatch/recipient action/receipt persistence remain separate crash windows
5. Bounded queues and snapshot recovery preserve admitted commands without making observers writers
6. Fairness assumptions are stated per queue/control lane; liveness never assumes perpetual connectivity, infinite capacity or an always-cooperative provider
7. Reconciliation cannot create a second retry owner

A counterexample caused by missing broker state requires expanding the mapped state or moving that state into the aggregate. It is not a reason to label real behavior out of scope. A timeout, model disagreement, unexposed mutant or missing refinement map is inconclusive rather than passing.

### 6.3 Inclusive model's strongest case

Queue admission, input leases, delivery epochs, recipient fences, fork reservation split and release cut can interact. Putting their relevant facts in one state space makes cross-boundary races easier to expose. Its strongest argument is fewer hidden assumptions, not merely a larger model. Its weakness is state explosion and confusion between essential semantics and transport detail.

**Recommended comparison:** same abstract oracle, same labeled fault histories, same full bounds, separately authored mapping/monitor, reachable-non-equivalent mutant coverage and retained first divergences. Report semantic failures, insufficient auxiliary state and checker-resource failures separately. Reject the split if it cannot represent the required race. Reject needless inclusion when an independently checked refinement detects the same failures with lower review cost. Neither result selects implementation process count or framework.

## 7. Native model/tool loop: first-class and deliberately small

### 7.1 Owned control flow

Proposed turn machine:

`idle -> admitted -> context_ready -> sampling -> response_recorded -> tools_pending -> tool_results_recorded -> continuation_decision -> sampling | checkpointed | waiting | completed_candidate | blocked`

Every arrow that consumes resources or changes the outside world passes through admitted operations. Native loop ownership includes: choosing the next permitted sampling step; rendering the context artifact set into a model adapter request; tracking stream completion and malformed/truncated tool calls; forming typed tool proposals; controlling bounded parallelism; appending exact tool-result identities; deciding whether another turn is needed within the original goal and budget; producing a candidate checkpoint/result. The kernel independently admits each effect and the verifier independently accepts task outcome.

A reusable provider client or parser library is allowed. A reused upstream loop that owns sampling, tool sequencing and retries is classified as upstream execution. Native's defining criterion is inspectable Recursion-owned transition/control semantics, not a homegrown HTTP client.

### 7.2 Narrow interfaces

- **Model adapter:** route-qualified request/stream/usage/error protocol; exact request identity; completion/truncation/cancellation classification; no tool execution
- **Tool registry:** admitted schema/version/effect class; deterministic target validation; lifecycle and concurrency contract; not every tool visible to every turn
- **Tool broker:** owns actual effect attempts and receipts; rejects stale turns and unauthorized late output
- **Context compiler:** deterministic compiled envelope plus optional admitted transform products; never silently launches inference
- **Native loop:** consumes these interfaces and emits proposals/observations; no credential-bearing generic network client in the reasoning surface

Streaming text can be ephemeral output. A complete model response, accepted tool-call intent and final tool-result reference must have a durable boundary before dependent work. Never execute a syntactically salvageable but semantically truncated tool call solely because partial JSON parses. Preserve provider/source ids for duplicates but do not assume those ids imply billing deduplication.

### 7.3 Tool batch semantics

Classify tools by shared effect resources. Parallel read-only or independently scoped operations can be admitted separately within a group reservation. Conflicting writes serialize or refuse until explicitly ordered. Display completion order, retain source-call order for context if the model protocol requires it, and record the distinction. One failed tool does not erase completed sibling effects.

On steering, durably bind the message to the intended run/turn and report accepted/delivered/adopted separately. An upstream or native boundary that only reads steering after tools finish cannot be advertised as immediate cancellation. On context pressure, block the next sampling step until a permitted compaction/rebuild choice succeeds; do not launch an unaccounted helper.

### 7.4 Reasoning-role closure

| Role | Native-only | Upstream-only | Deterministic alternative |
|---|---|---|---|
| Interactive assistant / planning | Native loop on granted model route | Admitted upstream role/session | User supplies exact plan; no reasoning substitute claimed |
| Specialist research / implementation | Native role binding | Upstream headless/native delegation | Typed retrieval and fixed transformations only |
| Compaction / summary | Accounted native transform if enabled | Route-native compaction or separately admitted upstream turn | Artifact selection/truncation with loss explicitly declared |
| Review / semantic verification | Independently admitted native verifier | Independently admitted upstream verifier | Machine gates, with semantic coverage limited |
| Route ranking | Optional accounted model scorer | Optional upstream scorer | Rule/observed-metric ranking of kernel-eligible routes |
| Recovery | Optional newly admitted reasoning turn | Optional admitted upstream recovery turn | Replay, status, reference validation and reconciliation queries |

Every role binds actor, task, route, pool, model-launch grant, reservation, usage provenance and acceptance policy. A missing role path blocks that workflow. It does not trigger an invisible API route. A deterministic-only recovery can restore records while honestly leaving semantic continuation unavailable.

**Recommendation:** start with one strong simple-loop baseline and add reasoning scaffolds only where a required capability or measured improvement justifies them. **Competitor:** richer Recursion-owned optional orchestration with the same comprehensive capabilities, lean activation and admitted tools. **Negative control:** fixed elaborate planner/researcher/reviewer teams on every task. **Falsifier:** minimal loop fails a required workflow or quality floor that the richer design reproducibly satisfies within policy. **Non-proof:** this does not reduce the comprehensive release capability set or demonstrate that fewer agents always win.

## 8. Upstream delegation and the credential boundary

### 8.1 Delegation lifecycle

`requested -> profile_checked -> authority_admitted -> launch_requested -> launch_observed -> session_bound -> active -> checkpoint_candidate -> detached | completed_candidate | cancelled | ambiguous -> reconciled`

A DelegationRecord binds the Recursion task/actor to upstream harness/interface/build, installation owner, authenticated launch profile, route and pool, process scope, source/workspace cut, context capsule, grants, epochs, native delegation limits, exact supported controls, losses and retry owner. Upstream thread and turn ids are child bindings, not canonical task ids.

Recursion owns its normalized stream and retained permitted evidence; this does not imply rights to hidden reasoning, provider server state or credentials. Raw output is untrusted data. A JSON field saying “approved,” “completed” or “usage=0” is evidence to classify, not authority to accept.

### 8.2 Operator-provisioned launch seam

The launcher accepts an allowlisted route-profile identifier, immutable packet reference and authorized operation id. It does not accept arbitrary shell text, arbitrary environment variables, unbounded filesystem handles or a request to expose the credential store. A purpose-limited invocation handle may itself be bearer authority even when it cannot reveal the provider secret; authenticate and constrain its use separately. Recursion's process identity cannot read the provider credential domain; the trusted harness receives only the access its operator provisioned.

Distinguish four claims:

1. Credentials were not explicitly read or relayed by the orchestrator in a recorded run
2. Policy forbids orchestrator credential access
3. OS/security boundaries prevent orchestrator access under a named threat model
4. The delegated harness and tools cannot be induced to disclose protected credentials through an allowed command/output channel

D-029 requires a credible boundary across direct and induced access: claims 3 and 4 must both be addressed under the named threat model. A different OS user does not automatically solve claim 4. If the harness can read credential files through a model-controlled tool and print them into JSON, a strong end-to-end non-access claim is not established. R-E sharpens the achievable target to a conditional strong boundary with an explicitly trusted, pinned credential-facing component, protected launcher and credential-free untrusted tool domain. This requires documented support in the exact unmodified upstream build for separating credential-facing C from untrusted tools T, or a specifically evidenced equivalent enforceable profile capability. A transparent wrapper, different parent process or launch broker cannot manufacture a missing C/T separation. Missing support blocks strong-profile admission; source documentation alone still requires exact-build conformance evidence. A malicious secret-bearing component with unrestricted output can encode the secret; no generic scanner or finite sentinel suite proves universal noninterference. Include that trust exclusion beside the claim. Record an insufficient profile as `non-intermediation-by-policy only`, but do not continue executing merely because its label changed. Failed strong-boundary preflight closes admission; tasks requiring the strong property are refused. A weaker mode can run only after the operator separately admits that exact weaker mode for an eligible task, with its limits and grants explicit. Never automatically downgrade or route around the failed boundary. Bind fixed executable, argument grammar, filesystem scope, inherited handles, process inspection, logs/dumps, egress and returned-output policy to each platform profile. Never implement token extraction as a compatibility shortcut.

An MCP credential proxy is not automatically the accepted delegation model: it may be valid only for separately granted credentials and correct audiences. The hosted vault pattern in another product is a mechanism reference, not D-021 permission.

### 8.3 Control loss must be executable knowledge

Exact build/transport/method qualification distinguishes: observation-only, coarse task control, correlated approval control, pre-effect mediation, process containment, source-cut continuity and accounting. If an upstream loop executes tools internally, the adapter cannot claim every internal effect is mediated unless the interface or enforced outer sandbox covers it. A post-tool hook cannot become a pre-effect gate.

Codex source inspection remains D-023's first target. Use the [canonical profile facts](../rf/report.md#codex-app-server-facts) to qualify transport, methods, subscriber lifetime, background controls and compaction recovery against the exact build. A blanket protocol-capability flag cannot support these separate obligations.

Harness-native fan-out is admitted as a parent delegation with child scope/depth/concurrency and shared-pool reservations. If upstream-native child creation cannot be individually intercepted, it must remain inside one pre-reserved, enforceably bounded subtree. If that envelope cannot be enforced, the profile is unqualified for effectful fan-out; compare a narrower isolated proposal-only profile with separately mediated promotion. Opaque child work remains a visible observability/accounting limitation. Absence of child counters never grants extra capacity or proves no child work occurred. Subject to counsel, compare native fan-out against several explicitly separate headless invocations; neither authorization nor economic advantage is inferred from the word subscription.

**Competitor:** externally confined R/T domain versus separate protected credential principal, with the same direct and induced-flow obligations. **Negative control:** same-user direct CLI launch with policy-only non-intermediation. **Falsifier:** the strong boundary cannot be enforced on a required profile, or exact required controls cannot be implemented without forbidden credential custody. **Non-proof:** no profile is qualified here; no counsel determination or automated-use entitlement is established.

### 8.4 Tool protocol adapters preserve logical operations across wire eras

The [MCP canonical evidence](../protocol-edges/report.md#public-evidence-and-bounded-interpretation) supplies the versioned premises. **I:** bridge profiles bind era, transport, exact implementation, capabilities and effect class; SDK abstraction names never determine authority.

For the [MRTR profile](../protocol-edges/report.md#multi-round-trip-requests), preserve canonical OperationId, admitted parameters, parent deadline, round/byte limits and reservation across wire attempts. Bind opaque state to its privacy scope; material changes need new admission.

For the [Tasks profile](../protocol-edges/report.md#cancellation-and-asynchronous-tasks), preserve protocol outcome, tool outcome, acceptance and settlement as distinct observations. Retain uncertain effects and reservations when the observation disappears; distinguish the task and ordinary continuation paths.

For [stream restart](../protocol-edges/report.md#stream-framing-and-restart) and [cancellation](../protocol-edges/report.md#cancellation-and-asynchronous-tasks), let canonical idempotency/reconciliation govern retries. Qualify the documented wording discrepancy explicitly. Bound decoding, input rounds, opaque state, polling, notifications, retention and teardown; mandatory receipts never become disposable display backlog.

**Competitor:** an SDK-centered bridge qualified to intercept every effecting attempt, continuation and retry. **Falsifier of the explicit codec/envelope preference:** required supported interaction cannot be represented without losing authority, correlation, uncertainty or compatibility while the competitor can. **Non-proof:** either bridge's local conformance does not establish remote idempotence, legal entitlement or external-effect truth. The root supplement's MCP01–MCP10 are additional unexecuted fixture inputs.

## 9. Context, compaction, memory and workspace state

### 9.1 Three separately owned layers

1. **Canonical control/evidence:** exact accepted directives, goal/plan revisions, approvals, grants, reservations, source/artifact ids, pending questions, last settled operation and unresolved effects
2. **Recoverable context artifacts:** source-grounded summaries, repository maps, task briefs, memory items and evidence slices with dependency/freshness/audience metadata
3. **Route working context:** provider-rendered messages, cache prefix, hidden provider state where available, loaded tool schemas and route-native compaction products

Layer 3 may disappear completely. Layer 2 may be rebuilt or rejected as stale. Layer 1 cannot depend on either. Long-term memory is a separate retrieval substrate, not permission, truth or a replacement event log. Git-backed notes may be useful exports, but cannot create a second authoritative transition order alongside canonical commands.

### 9.2 Compiler contract

Input: current authority snapshot plus a requested artifact set, exact workspace/source/candidate manifest, route descriptor, audience, context policy, tool graph and token/resource envelope. Output: a manifest of admitted references, rendered bytes/digest, transform lineage, declared omissions, known limits/unknown estimates and a next-step eligibility result.

Compilation starts with namespace and authority filtering, then freshness/dependency validation, then relevance selection. Similarity search ranks already-eligible objects; it must not retrieve private cross-project content first and filter after disclosure. Keys include relevant source/config/goal/tool/route/transform revisions. Reuse of identical content does not reuse an expired authorization envelope.

Workspace state includes committed base, dirty tracked modifications, untracked admitted files, submodule/link boundaries and content digests or declared unsupported elements. A branch name or HEAD alone cannot describe the current execution cut. The handoff retains unresolved source races and a bounded snapshot protocol; it does not pretend a provider conversation fork copies dirty work.

### 9.3 One compaction owner per route epoch

`requested -> inputs_frozen -> transform_proposed -> structurally_validated -> semantic_assessment_if_required -> admitted -> context_epoch_advanced`

On refusal, previous authoritative epoch remains. A native/upstream transform cannot independently advance the Recursion context epoch. Spontaneous upstream compaction is observed and classified; the governor either validates the resulting bindings, reconstructs from canonical artifacts, or marks continuation blocked. Two independent compactors must not both rewrite the same route epoch.

Structural checks preserve exact directive references, authority, budgets, source state, gates, pending interactions, uncertainty and rehydration links. They cannot prove that a short summary preserves every subtle inference needed later. Independent quality assessment and task outcomes remain separate. [Context Compaction Theory](https://arxiv.org/abs/2608.01326) provides a bounded communication-model reason to make fidelity query/workload-specific, not promise lossless arbitrary compression. Its preliminary theoretical model is not a production compactor or a measured Recursion guarantee.

Memory items carry source, writer, creation/validity time, project/audience, supersession/contradiction edges and retrieval policy. A later correction suppresses obsolete action guidance without rewriting the historical source. [LongMemEval](https://arxiv.org/abs/2410.10813) supplies useful update/temporal/abstention test categories; it is not an authority, coding or productive-continuity acceptance suite.

### 9.4 Economic policy

Compare route-native compaction, deterministic artifact selection, and coordinated hybrid compaction at matched quality/recovery floors. Keep provider cache economics separate from Recursion artifact reuse. Cache hits can reduce processing cost without demonstrating subscription-quota savings. Include summary calls, index builds, retrieval, cache writes/reads, failed transformations, retries, verification, cold rebuild and human correction. Include no-future-work counterfactuals before adding keepalives. Current documentation, endpoint and account evidence are required for every price or cache claim.

**Competitor:** provider-native session/summarization acceleration backed by a complete external capsule and qualified cold reconstruction under the same state-loss and revocation contract. **Negative control:** retain one warm provider session and summarize on its native schedule without that external recovery contract. **Falsifier:** artifact-based rebuild loses required decisions or adds more full-workflow cost without a declared continuity benefit. **Non-proof:** valid hashes/references do not establish semantic fidelity, source truth, cross-provider KV-cache sharing or positive savings.

## 10. Rooms, assistants and bounded coordination

A room is an addressable, transport-independent conversation/workflow record with project/goal membership, disclosure policy, participant roles and a versioned coordination policy. It is not an authority domain automatically shared by everyone present. Assistant identity outlives session; a role lease says which goal the assistant may currently act on.

A RoomMessage records author principal/actor, room revision, target(s), message kind, referenced goal/task/action, source event, audience, expiry and causation. Kinds distinguish observation, advice, question, proposed decision, accepted directive and coordination request. Only canonical admission can turn an authenticated authorized decision into a goal or grant amendment. Peer agreement cannot do it.

Delivery machine: `accepted -> delivered -> acknowledged/adopted | rejected | expired | superseded`. Transport delivery and semantic adoption have separate receipts. Late answers bind the original QuestionId/revision; a replacement waiter is never addressed by matching text alone. Duplicate delivery cannot repeat an effect.

A bounded CoordinationLease names one assistant, one workflow step, allowed verbs/targets, expiry, work/room epochs, resource allowance and conflict policy. Head retains admitted overall-goal responsibility; no new standing manager tier appears. Direct Owner-to-ARM conversation is preserved. Compare direct step coordination with Head-mediated protected commitments under the same policy. Multi-goal rooms need explicit data-sharing and charge attribution rather than silently pooling authority or budgets.

Prevent coordination storms using per-task message/turn/recursion bounds, backpressure, explicit wait edges, deduplication and deterministic no-progress/lease-expiry escalation. A digest can reduce notifications but cannot coalesce revocations, approvals, accepted amendments or uncertainty out of existence. Human participation uses the same exact command and approval semantics as CLI.

**Competitor:** all commitments routed through Head. **Falsifier:** direct coordination fails stale-lease/late-answer safety, raises owner effort or increases control/model cost without a measured task benefit. **Non-proof:** an agent-to-agent protocol provides transport and task semantics, not shared authority, universal confidentiality or better collaboration.

## 11. Long-horizon autonomous work and adaptation

### 11.1 Deterministic scheduling, bounded reasoning

A ScheduleSpec is admitted under a specific GoalSpec and plugin grant. It binds source set, trigger/cadence, start/stop conditions, maximum occurrences or bounded validity, lateness/catch-up policy, concurrency, retry policy, budgets, notification/promotion authority and route-role closure. A repeated schedule does not mint a fresh allowance on each tick.

A stable occurrence identity binds schedule id, schedule revision and logical due slot/event. Proposed machine:

`armed -> due_observed -> eligibility_checked -> admitted | deferred | held | expired | cancelled`

Actual work uses the normal OperationId/AttemptId path. The scheduler deduplicates an occurrence after restart and rechecks current grant, PAUSE, source freshness, epoch, remaining parent/pool/recovery allowance and route eligibility. It records missed ticks or catch-up dispositions explicitly. A timer callback or workflow replay is not fresh authority.

Ordinary runtime monitoring is model-free: process status, queue state, durable wakeups, receipt deadlines and resource bounds. A model wakes only for authorized semantic work. The optional research plugin cannot self-enable, amend its scope, extend its end date, allocate budget or promote findings into policy. Ongoing admitted work can continue while a user view is absent; closing a terminal is not a stop command.

**Competitor:** bounded resident or subordinate workflow dispatcher preserving the same durable occurrence records, current authority gates and crash reconciliation. **Negative control:** a continuously thinking supervisor or an external scheduler with no canonical occurrence record. **Falsifier:** event-driven scheduling misses accepted required occurrences, cannot reconcile crash windows, or is less maintainable than equivalent subordinate durable assistance. **Non-proof:** a persistent reminder definition does not imply every occurrence executed exactly once.

### 11.2 Adaptation as a versioned proposal pipeline

A feedback record binds workload, route/harness/model/build, effective configuration, source/candidate, accepted outcome, reviewer identity, complete observed costs, missing-counter flags and failure/continuity events. Keep workload selection, difficulty, cache warmth, prior retries and human intervention as confounders.

Pipeline: `observed -> quality_checked -> candidate_policy -> offline/shadow_evaluated -> reviewed -> explicitly_promoted -> bounded_rollout -> retained | rolled_back`. A policy version can rank only kernel-eligible routes. It cannot widen privacy, credential access, spend, accepted task scope or release gates. Exploration that adds inference or cost needs its own budget/admission; “learning” is not authorization.

Start with deterministic routing and measured descriptive feedback. Compare learned ranking only after label quality, absent counters, drift and full-workflow endpoints can be inspected. A user pin remains visible and enforceable; cache affinity is a tradeoff, not a reason to retain revoked context. Rollback changes future policy selection and preserves work/history; it cannot erase prior effects.

**Competitor:** static owner-controlled policy. **Falsifier:** adaptive ranking fails a hard floor, cannot be explained/replayed, or offers no preregistered improvement net of classification, exploration, verification and correction. **Non-proof:** an offline classifier or emulated router does not show live task quality, subscription savings or deployability.

## 12. TUI-first backend and plugin integration seams

### 12.1 One command/query substrate

CLI, TUI and later GUI send the same authenticated idempotent commands and render the same versioned projections. Commands name exact object ids and preconditions. Queries expose source sequence, freshness, reconstruction gap and capability-loss metadata. A local client need not expose a network listener. A remote transport needs its separately authorized identity/security profile.

A command can be saved locally without being accepted; accepted without being delivered; delivered without being adopted; and applied without external effects being settled. The UI must show those facts. Generated/tested/reviewed/accepted/published are distinct. Native/upstream turn end is not task acceptance. Zero-token `explain` renders admitted policy inputs, rejection reasons, missing evidence and relevant event ids from deterministic records.

Separate control traffic from bulk output with bounded queues and reserved control capacity. Slow views may lose ephemeral stream data and receive explicit RESET/snapshot reconstruction; they cannot block canonical append or Stop. Snapshot acceptance needs exact projection bytes at a named canonical cut, not only a digest. Cursor identity includes stream/incarnation semantics under a ratified version. Neither a PTY nor renderer owns process lifetime.

All ten controls retain backend meanings: streaming, questions, approvals, queue editing/removal, active steering, interruption, resume, preserved forks, compaction controls and typed commands/plugins. Unsupported route behavior is visible, never simulated by a misleading button. Accessibility projections should expose semantic structure and attention status without requiring raw token repaint; concrete technologies remain unselected.

### 12.2 Plugins are behavior contracts

A metadata-only manifest names identity, full artifact/dependency digests, provided/required capabilities, versions/platforms, effects, grants, resources, lifecycle and conformance evidence. Discovery must not import or install the payload. Runtime authority is the intersection of current GoalSpec, parent grant, policy, manifest request, route enforcement and operation approval; dependency resolution never grants authority.

Native and upstream implementations share the requested user-level behavior while recording semantic losses. Port classes should distinguish unchanged declarative reuse, schema translation, protocol bridge, isolated host reuse and manual rewrite. Measure acceptable behavior, lifecycle, authority, maintenance effort and license constraints, not only successful loading. No universal runtime emulation claim follows from compatible metadata. R-G supplies a useful detached import chain: source artifact -> pinned import profile -> translation record -> per-contribution realization/loss -> independent import review. These are provenance and compatibility edges, never permission edges. Separate direct metadata mapping, mechanical transformation, reviewed semantic annotation and no adequate counterpart. Do not execute source configuration expressions, expand ambient secrets, install dependencies or fetch schema URLs to discover contributions. Unknown contributions are not an empty capability request.

Lifecycle: `discovered -> verified -> admitted -> staged -> active -> drain-and-fence -> retired/replaced`, with refusal/quarantine paths. Update never mutates an active digest in place. The four incompatibility responses remain available; each returns an inspectable incompatible/no-effect result when no effect was attempted. After an attempted effect, failures and uncertainty must use their actual state rather than retroactively claim no action.

**Competitors:** one reusable isolated host per plugin versus fresh isolated worker per invocation, under the same inert-discovery, lifecycle, containment and effect gates; independent client codecs sharing semantic goldens and the canonical backend. **Negative controls:** uniform in-process plugin runtime for unsafe payloads; a UI that calls harnesses directly. **Falsifier:** isolated translation cannot implement required behavior at acceptable cost, or common commands materially obstruct useful engine-specific extensions. **Non-proof:** process separation is not a sandbox; a signature is not a grant; zeroed fixture counters are not runtime inertness evidence.

## 13. Canonical storage, availability and update seams

Core storage interface requires conditional append under writer fence, contiguous authenticated event identity, exact-command receipt lookup, replay/read-at-cut, checkpoint identity, artifact reference settlement and explicit durability acknowledgment. A hash chain alone does not authenticate the writer. A snapshot that opens is not proof the newest acknowledged command survived.

D-020's optional availability plugin proposes leadership and implements replicated persistence behind the store seam; the core checks monotonic fences and rejects stale writers. A returning coordinator cannot reuse an old fence or replay dispatch merely because its local disk is intact. Only one authority writer exists per declared aggregate boundary, including during takeover. Losing quorum/required backend availability must not turn into an unfenced local writer. Installation of full/remote does not imply failover is activated.

The exact trust and failure model for fence allocation and durable acknowledgment must be part of the plugin contract. If the plugin can lie about its epoch or permit two durable writers, a core integer check alone is not an isolation proof. Test real receiver/store enforcement and accept that a partition can preserve uncertainty even after leader election succeeds.

All six configured update modes preserve four separate outcomes: executable starts, history readable, newest work preserved, tasks resumable. Compatible rollback requires proof the old reader/runtime can interpret current retained state; otherwise repair forward or hold. A boot receipt binds release, host incarnation, schema/config/protocol epochs and checkpoint. Offline required nodes keep aggregate landing incomplete. Update maintenance has a narrow separate grant and cannot smuggle ordinary work through a Stop fence.

**Competitor:** isolated opt-in availability service versus linked opt-in availability plugin, both behind the same lean core fencing/store seam. **Negative controls:** a monolithic replicated default core or an always-unavailable-after-loss writer. **Falsifier:** automatic takeover cannot be safely implemented through the seam without pulling consensus into default core. **Non-proof:** failover capability is accepted, but no backend/platform cell is qualified by this report.

## 14. Failure traces that decide the architecture

These are designed traces, not executed evidence. Full fixture handovers are in `test-handovers.md`.

| Trace | Interleaving | Required truthful outcome / decisive seam |
|---|---|---|
| FT-01 Commit then crash | Intent/reservation committed; broker not yet dispatching; restart | Same operation recovered once; fresh authority check before dispatch; no vanished task or second reservation |
| FT-02 Acceptance then lost receipt | Recipient accepts external effect; connection dies before canonical receipt | Ambiguous; reserve retained; no duplicate/dependent effect until same-operation reconciliation |
| FT-03 Stop versus permit | Permit issued; local Full Stop committed; remote fence not installed; recipient acts | Show local fence and uncertain remote exposure separately; never claim total rollback or universal stopped |
| FT-04 Split-brain takeover | Old writer partitions; plugin grants new fence; old node returns with buffered work | Store and effect receiver reject stale writer/permit; history and unresolved prior effects retained |
| FT-05 Stale tool proposal | Model response completes after grant/config/goal revision changed | Preserve observed output; reject stale effect admission; no auto-upgrade to current grant |
| FT-06 Compaction race | Native compactor finishes old inputs after upstream session auto-compacts and directive revokes | One governor rejects stale candidate; exact revoked directive history retained; current epoch rebuilt/refused |
| FT-07 Upstream-only helper hole | Upstream session lost; compaction/verification role has no qualified route | Deterministic recovery works; semantic step visibly blocked; zero hidden native/model API launch |
| FT-08 Dirty fork plus budget | Source tree changes while source/session fork begins; parent has unresolved effect/reservation | Preserve exact admitted cut or refuse; separate child allowance; unresolved parent effect not copied as a new attempt |
| FT-09 Room late answer | Question replaced; coordinator lease expires; old answer arrives with same prose | Bind original waiter; reject stale adoption; no authority gained from room membership |
| FT-10 View overload | Many slow clients exhaust stream credit while Stop arrives | Control stays bounded/responsive; RESET markers for views; no process lifetime change from detach |
| FT-11 Disabled plugin trap | Enumerate installed-disabled capabilities and ask incompatible command | No import, process, watcher, auth/network/model/quota effects; typed inspectable no-effect receipt |
| FT-12 Workflow replay duplicate | Helper replays activity after missing acknowledgment; canonical effect ambiguous | Same identity reconciled, no helper auto-retry of effect; one retry owner |
| FT-13 Scheduler crash | Occurrence claimed before daemon death; grant revoked before recovery | Record occurrence disposition; refuse new semantic work; no replayed allowance or catch-up storm |
| FT-14 Update rollback | New release writes newer state; old executable starts after regression | Readability/newest-work/resumability tested separately; hold if incompatible; no data rollback over effects |
| FT-15 Trusted-launch exfiltration | Allowed harness request attempts to expose protected credential through its tools/output, or exact unmodified upstream lacks enforceable C/T separation | Fail closed: stop admission and refuse strong-required work; retain the failed claim/profile evidence. No policy-only continuation without separate operator admission of that weaker mode |
| FT-16 Truncated tool JSON | Stream disconnects after parseable prefix omits intended constraint | No partial tool execution; response incomplete; reconcile possible model usage separately |
| FT-17 Duplicate meters | Cumulative usage repeated across stream, final response, helper and child rollups | Deduplicate by meter segment/source semantics; unavailable counters remain null; no double debit or fabricated zero |
| FT-18 Adaptation authority drift | Learned policy prefers cheap route lacking privacy/entitlement/control | Kernel rejects route; explanation retained; no scalar score buys a hard-floor violation |

## 15. Integration sequence without prematurely choosing technology

1. **Reconcile semantic seams:** authority supersession map, exact identity joins, writer inventory, no-hidden-role matrix, stop vocabulary-to-epoch mapping and snapshot materialization contract. Preserve frozen M1 bytes.
2. **Complete matched formal contracts:** split/inclusive common observations, integrated fault corpus, independent mapping/monitors, mutant dispositions, literal byte corpus. Keep reduced historical results separately labeled.
3. **Provider-free vertical contract prototype:** admitted command -> durable-operation abstraction -> simulated native model response -> typed tool proposal -> simulated effect receipt -> exact projection. Its success is contract evidence only; no real inference or containment claim.
4. **Qualify platform/store/broker candidates under separate admission:** D-028 exact native profiles, commit-boundary VM-reset evidence, stale-writer fencing, snapshots, containment, slow clients, receiver permits. Language/store ranking waits on required accepted corpus and platform evidence.
5. **Qualify both execution paths:** native loop and first D-023 upstream profile, plus a deliberately different adapter stress test. Every role/control/loss/accounting field must be explicit. A second prototype is not an unauthorized launch promise change.
6. **Exercise all six continuity journeys:** useful task outcome plus invalid-behavior rejection, against strong direct/minimal baselines, with human effort and full accounting.
7. **Compare A/B/C at matched workload:** separate cold/warm, installed/disabled/active, single-node/failover, direct/room, deterministic/hybrid context and static/adaptive policy. Publish unknown and failed cells.
8. **Close release gates:** all accepted opt-in capabilities, exact route legal/distribution review, independent reruns, operator documentation and D-019 release-scope reconciliation. No document count substitutes for acceptance.

No step above authorizes execution, installs, provider/harness use, credentials, spend, live-host actions, counsel contact or repository edits. Each requires its own bounded admission, exact candidate, gate and independent reviewer.

## 16. Recommendation register

All competing designs are original architectural inferences subject to the same accepted floors and qualification gates. Former nonconforming rivals are retained only as negative controls. No comparison selects a language, store, framework or vendor.

| ID | Recommendation | Strongest competing option | Decisive falsifier | What it does not prove | Negative control (not an admissible rival) |
|---|---|---|---|---|---|
| MA-01 | One canonical authority spine, replaceable loops | Single-writer command/state machine with independently mapped upstream observations versus centralized canonical event reducer; identical authority and recovery floors | Spine cannot represent required controls without a second authority writer | Implementation correctness | Upstream session or framework state as authority |
| MA-02 | Split proof first; inclusive challenger retained | Broker-inclusive aggregate | Unmapped required broker race violates aggregate invariant | Four functions are sufficient for all behavior | None added; existing competing option is admissible |
| MA-03 | Demand-activated A as first baseline | Resident B | Matched interactive responsiveness falls below accepted floor | Lower idle cost or fewer defects | None added; existing competing option is admissible |
| MA-04 | Treat workflow assistance as subordinate | Receiver records alone | Helper cannot preserve canonical identity/retry ownership or net maintenance benefit | Exactly-once effects | None added; existing competing option is admissible |
| MA-05 | Small native loop with admitted tools | Richer Recursion-owned optional orchestration loop under the same comprehensive capability set, lean activation and admitted-tool floors | Simple loop fails necessary quality/workflow floor | Comprehensive features unnecessary | Elaborate mandatory model team |
| MA-06 | Explicit all-role route closure | Independently admitted whole-subtree role closure versus explicit per-role upstream delegation; complete role coverage and no hidden native helper in either | Upstream-only cannot complete a required role without hidden API | Route entitlement or savings | Implicit native helper fallback |
| MA-07 | Trusted operator launch boundary | Externally confined R/T domain versus separate protected credential principal; identical D-029 direct/induced-flow and qualification requirements | Protected credentials reachable within named supported threat model | All platforms qualified | Same-user policy-only delegation |
| MA-08 | Artifact compiler + one compaction governor | Provider-native continuity acceleration plus complete external capsule and cold reconstruction; identical required-state, loss and revocation contract | Rebuild loses required state or costs more without continuity benefit | Semantic losslessness | Provider session as continuity anchor |
| MA-09 | Bounded room step leases | Head mediates every commitment | Stale/late message acquires authority or owner effort worsens | Multi-agent benefit | None added; existing competing option is admissible |
| MA-10 | Deterministic durable occurrences | Bounded resident or subordinate workflow dispatcher versus demand due-state dispatcher; identical durable occurrences, current grants and reconciliation | Missed or duplicate semantic effects after crash/revocation | Every tick exactly once | Thinking supervisor / bare timer |
| MA-11 | Adaptive policy only after reviewed evidence | Static owner policy | Hard-floor violation or no net preregistered benefit | Offline or emulated result transfers | None added; existing competing option is admissible |
| MA-12 | Shared command/query backend | Independent client codecs with shared semantic goldens and canonical backend versus shared command/query codecs/catalog; no UI-owned authority | Backend cannot express useful required controls/extension losses | Any particular GUI/TUI implementation | UI-owned harness orchestration |
| MA-13 | Metadata-first isolated plugin candidates | One reusable isolated host per plugin versus fresh isolated worker per invocation; shared inert metadata and identical lifecycle, containment and effect gates | Required behavior unportable at acceptable measured cost | Cheap or universal ports | Uniform in-process runtime |
| MA-14 | Core fence + optional availability backend | Isolated opt-in availability service versus linked opt-in availability plugin through the same lean core fencing/store seam | Safe takeover impossible through seam without default consensus | Qualified failover | Replicated core |
| MA-15 | Full-workflow evidence and refusal transparency | Preregistered lexicographic evaluation versus full-workflow vector; same complete evidence, hard floors and strong baselines | Claimed savings disappear or quality/effort worsens against strong baseline | Vendor motive | Feature/benchmark-count marketing |

## 17. Phase-one integration and remaining dependencies

Integrated 2026-10-02: R-E, R-F, R-G, R-H, the root protocol-edge supplement, and a bounded FU-03/FU-04 evidence-limit crosslink from the gap audit. Their reports are attributed research inputs, not independent execution evidence or accepted contracts.

| Input | Material change carried into this synthesis | Remaining evidence boundary |
|---|---|---|
| R-E trusted launch | Direct and induced access both matter; exact unmodified upstream C/T separation or equivalent enforceable support is required; classify launch handles by actual authority; failed strong preflight closes admission | Every native profile unqualified; weaker mode requires separate operator admission; sentinel corpus is not a universal proof |
| R-F fan-out | Pre-reserved bounded opaque subtree or proposal-only profile when child mediation is absent; spawn admission ambiguity; per-meter coverage/dedup; detach/lifetime mapping | Honest accounting may still be incomplete; no native/upstream route qualified |
| R-G import | Detached translation/provenance records and per-host contribution realization/loss; executable config must remain inert at discovery | Common description is plausible; universal executable compatibility and port labor savings unmeasured |
| R-H counsel framing | Route review must bind agreement/entity/territory/plan, auth mode, caller/beneficiary, interface/flags, work topology, output categories and distribution contents | Credential non-custody is not itself contractual permission; G-32 open |
| MCP supplement | Stable logical operation across new wire ids; cooperative task cancellation and TTL ambiguity; era-specific semantics; no SDK retry ownership leak | Exact peer/SDK/transport conformance and remote effects unverified |
| Gap audit | Correct four-ID formal bound and diagnostic-mutant semantics; explicitly unexecuted enlarged-bound witness; exact FU-04 receipt counts and narrow oracle support | Read-only audit; no new execution, full gate acceptance or platform qualification |

R-H's most important architectural constraint is a **profile-specific legal admission record**, separate from technical capability and credential isolation. A local caller, paid local product, operator-managed remote node and hosted multi-tenant service cannot inherit one undifferentiated vendor clearance. A profile's auth defaults, invocation flags, billing/beneficiary, output reuse or distribution assets can change while its friendly route name does not. Expire/review the applicable record when those facts or governing terms change; do not automatically switch to an API/key mode to repair a blocked subscription profile. This is a proposed evidence/eligibility seam, not a legal interpretation. Competing option: independently complete per-profile case dossiers versus normalized legal-admission records, preserving identical governing-instrument, variant, unknown and re-review coverage. Negative control: vendor-wide clearance only; falsifier of the finer granularity's necessity: counsel supplies a governing instrument explicitly covering all materially different profiles with identical conditions. The schema itself proves no compliance.

Later intake remains R-I…R-Y. The mapping below is verified against the actual titles in `docs/v3/prompts/dot-research-20261002b/README.md` and each individual brief, not the stale final frontier mapping in ARCHITECTURE-COVERAGE. The root MCP supplement remains a separate cross-cutting tool/protocol input; it is not the R-V assignment. Integration priorities:

1. R-P/R-U/R-X: prompt-injection defense, runtime isolation/supply chain, and node fabric/remote execution challenge trust, containment, receiver fencing and takeover assumptions
2. R-Q/R-T/R-Y: durable memory, multimodal I/O and workspace/repository graph bind persistent knowledge, transformed artifacts and source cuts to the context compiler
3. R-J/R-K/R-L/R-N: multi-agent terminal communication, multiplexer/TUI, shared interface and graphical client refine typed backend/view contracts; accessibility is a cross-cutting interface obligation, not the R-U lane
4. R-R/R-S/R-V: long-horizon autonomy/scheduling, adaptive optimization/outcome learning and observability/introspection/replay complete occurrence, policy-promotion and deterministic diagnosis contracts
5. R-O/R-W: performance/configurability engineering and harness evaluation/benchmark science refine matched comparisons, endpoints, falsifiers and independent acceptance
6. R-I/R-M: Grok Build source study and Claude Code terminal modding challenge upstream reuse, plugin realization and interface-extension choices

Exact later findings must be checked against this report's owners, identity joins and refusal semantics. Additive detail must not create a second writer, implicit helper model, renewed budget, credential broker inside Recursion or reduced release gate. The phase-one packet is complete as research; overall cross-lane synthesis remains open.

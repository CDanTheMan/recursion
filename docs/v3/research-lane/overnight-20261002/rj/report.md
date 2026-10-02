# Terminal multi-agent communication and rooms

Research specification for Recursion v3 · 2026-10-02 UTC

Repository basis: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`

## Findings and decision boundary

Use a hybrid presentation: stable per-actor tabs or split panes, plus an explicitly opened consultation view that joins their attributable exchanges. The room is a projection over existing actors and events. It owns no agent, budget, credential, plan, private context or executive role. A user can follow both sides of a sustained exchange without turning a group transcript into authority.

The principal design hazards are different kinds of ownership being mistaken for one another:

- The active terminal controller owns input and resize for one target stream; focus does not confer that lease
- A `CoordinationLease` permits bounded coordination and a proposal for one workflow step; it does not independently grant executive plan-writing rights
- The authorized executive role proposes its permitted plan transition; the sole fenced canonical writer validates and commits it
- A peer message can be accepted for delivery and answered without being adopted, executed, verified or externally settled
- A fork can preserve useful history while lacking a coherent workspace capture, current grants or a separately reserved allowance

Recursion's candidate differentiation is the combined continuity contract, not tabs, agent-to-agent messages, a dashboard, persistent assistants, worktrees or a visible handoff. Those features have documented prior art. No performance advantage, UI conformance, security isolation, entitlement, route qualification or measured porting cost is established here.

### Evidence and authority

**D** means source-documented, **O** means locally observed records or artifact bytes, **I** means inferred design, and **U** means unknown/unverified. All proposed behavior in Q01–Q16 and Q21–Q23 is **I**, grounded in the accepted repository requirements [L01–L11]. It is not an implemented or measured guarantee. Comparisons label each cell. Historical model/probe results are observations of committed records, never a new run.

The current governance, mission, parent goal and D018–D033 remain fixed [L01–L04]. Recursion must own a first-class native model/tool loop as well as orchestrate upstream-owned loops. No hidden native helper is required in upstream-only mode. The native implementation owns its own model/tool turn loop, queue boundaries and context control. An upstream implementation leaves its inner loop with the selected harness and maps only evidenced control/receipt capabilities into the common contract. Neither path can be substituted for the other by hiding an upstream SDK loop behind a native label. Hermes is an optional upstream integration. Head, ARM and worker describe the product's accepted roles, not authority for this research session or a new standing repository executive.

D019's comprehensive opt-in build is retained. The recommended layout is a default **inside an already enabled multi-agent interaction profile**, not activation of rooms, extra agents or inference on a lean installation. A disabled room feature may expose bounded static availability metadata, but attaching a view cannot activate it. TUI-first and later-GUI construction share the same backend; older GUI-exclusion wording conflicts with D019's built-opt-in release surface. This report does not decide exact GUI release timing or reduce the accepted release.

D022 fixes Aggressive / Full / Lazy plus `checkpoint`, `interrupt`, `drain`; it does not turn a socket close into Stop or a Stop receipt into rollback. The current literal M1A PAUSE refusal remains relevant to implementation mapping. Do not silently replace it with a proposed future policy.

### What the repository already supports and what remains open

Static inspection preserves the narrower historical evidence [L12–L17]:

- IPR-002 records Codex 0.149.0 scripted-loopback steering, question interruption, late-answer protection, completed-turn fork and idle-server history recovery. It does not qualify present binaries, cross-connection approvals, post-resume authority or a live account
- SC-EPOCH-03 records finite stale-adoption and stale-wake rejection, alias retirement, wait-for cycle handling, and Stop of a borrowed operation while unrelated consultant work proceeds. Earlier shared-oracle failures are retained in that record. This is not an authenticated production consultation service
- M1B is a one-client/one-stream wire audit. It cannot authenticate a claimed retention floor or prove snapshot installation. Its RESET and credit rules must not be relaxed to make a room demo pass
- G23/PERF-010 and G29's complete room fixtures are still unmeasured. Committed FU03/FU04 records add bounded evidence; they do not make room transport, physical control reserve or all platform profiles qualified

R-F's completed research supplies the fan-out accounting and operation-ownership seam. R-E supplies trusted-launch limits. The completed R-I report, sections 5–7, UI comparison and source-drift ledger were reviewed before finalization; Q19 independently verifies its dashboard corrections and extends them into a route-neutral contract. R-I's unexecuted T01/T02/T05/T06/T09 handoffs align with this lane's F03/F07/F16/F19/F23. These research reports remain integration inputs pending independent acceptance, not route qualification.

## R-J-Q01 Interaction model

Compare four useful presentations without changing accepted execution ownership:

| Option | Strength | Cost and risk | Disposition |
|---|---|---|---|
| Per-actor tabs | Clear actor, goal and private transcript; small viewport | Hides cross-actor causation until the user switches | Required focused view and lean-profile entry |
| Split panes | Two streams visible at once; useful for comparing a request and answer | Narrow panes, output competition, focus confusion at large N | Optional layout over the same view identities |
| Shared room or consultation view | Joins attributable requests, replies and adoption receipts | Temptation to merge context or mistake latest chat for authority | Required opt-in exchange projection; not a new actor |
| Hybrid | Stable actor navigation plus one selected correlation stream and inspectable graph | More presentation state and accessibility work | Recommended profile layout, subject to the comprehension test |

Keep the selected actor stable when another actor becomes busy. A compact activity list shows Head, goals/ARMs, bounded children and verifier relationships; an exchange panel shows one correlation or selected room. Graph edges are typed `requests`, `responds`, `owns-operation`, `proposes`, `adopts`, or `depends-on`, not one misleading “reports to” arrow. Plain-text mode provides the same identities and commands. An ARM under a goal is a role, not a terminal-owned process. A many-participant room does not add a chair model or a second portfolio manager.

Recommendation RJ-R01 compares hybrid with per-actor-only views and Head-relayed conversation. Its falsifier is greater wrong-target/authority error or review burden at equal information and task quality; layout preference is not settled by a screenshot. No performance or accessibility advantage is asserted before measurement.

## R-J-Q02 Peek and reply

**Peek** is a bounded authorized read of another actor/correlation projection. It cannot launch, wake, index, compact, query a provider, claim an input lease or copy the target's private context into the peeker's model. The preview has an explicit truncation marker, source cursor, observation age and target actor/run/goal labels.

**Reply** opens a target-bound draft carrying recipient logical ID, correlation, expected goal/role revisions, permitted payload audience and requested delivery policy. Selection changes never retarget a half-written reply: keep it pinned to the original target, or require an explicit discard/rebind. Submission uses the authenticated typed message command path; possession of a read projection alone is insufficient. A passive PTY viewer can have a separately granted addressed-message capability, visibly labeled, without acquiring raw INPUT/RESIZE control. Otherwise Reply offers a control/permission request, not a covert input bypass.

A reply is not necessarily an active steer. `notify` records/display-only; `queue` targets the next eligible turn; `steer` targets the current exact attempt/turn and a declared safe gap; `consult` adds a bounded question, response schema, expiry and adoption decision. “Send now” must expose whether an adapter implements true safe-gap steer or interrupt-then-submit. Never silently substitute the latter. Clicking Peek or preparing a draft creates no inference; submitting a wake-enabled request can admit work only under existing authority and accounting.

## R-J-Q03 Input and resize ownership

The broker owns the controlled process/terminal and validates one active control holder for its input and resize target [L05–L07]. Input and resize tokens retain separate typed namespaces even when a single controller acquires them together. A room with three actors may have three independently leased terminal targets; it has no portfolio-wide keyboard lease.

Display `read only`, or `controller: client X, lease revision Y` with target stream/process epoch and expiry. Focus is local presentation state. An explicit Request control command verifies principal, current grant, target, expected lease and revocation state. A release or an authorized takeover atomically advances the relevant fence before new input; competing requests receive a typed conflict. A lost response is reconciled with the same command identity, not retried as a new takeover.

Resizing a passive pane changes only its viewport. The active controller alone can send process RESIZE. A split-view resize cannot alternately resize one PTY from N clients. On controller disconnect, revoke/expire its input capability according to an explicit policy and retain broker ownership of the actor; no automatic grant to whichever tab next gains focus. New controllers need a new admitted lease. Keyboard Ctrl+C is not a universally safe transport for Stop: it may clear a draft or reach an upstream turn, so the named Stop command must remain distinct.

## R-J-Q04 Detach and lifetime

Close-tab, close-pane, hide, mute and lost transport detach that view and release its subscription/resources. None implies actor termination, session deletion, daemon shutdown, grant revocation for unrelated work or process relaunch. Persist the installed/acknowledged projection cursor where authorized. The durable actor and broker-owned operation continue only under their existing policy.

Expose separate actions with scope previews: Detach view; Stop selected actor/operation with a D022 mode; archive/hide a presentation item; and delete retained session/history under the applicable retention and deletion authority. Deletion is not a Stop substitute and cannot be offered as an ambiguous double-key accelerator without a clear destructive label. An upstream session-close command may end a session while retaining history; it is not automatically an implementation of Recursion detach.

Reconnect authenticates anew, resolves existing logical actor/run identity, negotiates a projection, replays or resets it, and revalidates any requested control lease. No launch belongs to this read path. If the daemon disappeared, status is recovery-required/unknown until canonical state and process/effect ownership reconcile. A second view references the same work identity and event producer. Duplicate attach requests with the same ID cannot produce duplicate subscriptions without bounds, much less duplicate execution.

## R-J-Q05 Cursors snapshots and replay floor

Each authorized projection has a stable stream identity, projection schema/filter revision, audience revision, daemon/stream incarnation and monotonically advancing cursor. A view stores separate requested, received, installed and acknowledged positions; receipt of bytes is not installation of a snapshot. Canonical event identity is not a terminal-byte offset, provider session ID or UI row number.

The room snapshot binds an authenticated canonical read cut, included actors/correlations, pending interactions, states, redaction policy, snapshot digest and source provenance. A single canonical ordered log can supply the cut; if separately sourced streams are joined, the manifest must bind a consistent cut or explicitly show an incomplete join. Wall-clock sorting cannot manufacture simultaneity or missing causal predecessors.

A late view receives a snapshot at S followed by events strictly after S. A reconnect requests its actual installed cursor C. If C remains replayable, replay it idempotently. If retained storage proves C is below the retention floor F, show a real gap and the verified snapshot boundary; M1B requires RESET before any further same-stream message, followed by fresh CREDIT before EVENT [L13]. A cursor merely deferred in a local presentation queue is not evidence of retention loss. Refuse a forged floor, missing snapshot, backward ACK or uninstalled-state continuation.

Filtering needs special care: invisible events must not leak through actor counts, IDs or obvious sequence holes. Use an authorization-scoped projection sequence with protected mapping to source events; distinguish redaction from retention gaps. Membership/audience changes invalidate old projection access and snapshot caches. These proposal-level metadata bindings can live in a negotiated outer envelope or snapshot manifest; they are not unapproved edits to the immutable M1B union. Historical replay never restores former grants.

## R-J-Q06 Attributable message rendering

The canonical consultation envelope binds: message/command ID and immutable content reference; requester and recipient logical IDs and role runs; room and one workflow step; correlation and causation; goal and plan revisions; context/evidence manifest revisions; permitted audience and data classification; requester/recipient lease identities; route/interface/build and source session/turn when known; delivery/wake policy; expiry; parent reservation; and reply-delivery generation. Credentials are absent. A display name is not an authenticated principal. CloudEvents source-plus-ID uniqueness is a useful envelope precedent, not a grant or proof of effect idempotency [RJ-S21].

Render a concise row such as “ARM A → verifier B · goal G revision 4 · consultation C · accepted, awaiting delivery.” Expand to exact receipts, provenance and applicable revisions. States are independent facts, not one linear success bar:

| State | Meaning and necessary evidence |
|---|---|
| requested | Attributable request proposed; admission may still fail |
| accepted | Canonical admission/receipt stored for this message and permitted operation |
| delivered | Exact recipient boundary acknowledged the exact ID; record whether inbox, harness or model-context consumption was observed |
| answered | Correlated response evidence received; says nothing about correctness or adoption |
| declined | Recipient or authorized decision holder refuses, with reason and scope; distinguish a delivery refusal from declining advice |
| adopted | Current authorized executive transition explicitly references this advice and exact revisions |
| expired | Deadline, alias, lease or revision makes further use ineligible; historical evidence remains |
| settled | Specifically identified work/effects have settlement evidence; message delivery alone is never this proof |

`blocked`, `rejected`, `delivery unknown`, `adoption not requested`, and `settlement unknown` remain expressible. Do not display `delivered to model` for a queue-only adapter acknowledgement. A reply received before revocation can remain visible as stale evidence while its adoption and wake are refused. A reply never received because its alias was retired remains missing, not reconstructed from a later summary.

## R-J-Q07 Steering and queueing between agents

Use an addressed request envelope and a capability-specific delivery adapter. The agent's natural-language body remains evidence, even when the envelope is authenticated. Permission to message does not authorize arbitrary execution. The deterministic scheduler checks the target's current goal, capability, budget and requested wake behavior before any inference.

The adapter returns a declared mapping: notify only; queue for an identified next eligible boundary; safe-gap steer into exact attempt/turn; or explicit interrupt-then-submit. Unknown support stays unknown. A rejected or stale steer must not silently queue itself for a replacement task. Downgrading requires a permitted policy and an observable loss receipt. A pending queue item may be edited/cancelled only through a new versioned command; after delivery, correction is a new attributable message, never an erased instruction.

Separate sender canonical acceptance, receiver ingress, model-visible consumption and semantic adoption. A receiver can reject delivery after sender acceptance because authority changed. An acknowledgement lost after dispatch creates delivery uncertainty; the sender reconciles the same ID rather than manufacturing a new message or turn. At most one owner handles retries for that operation. This preserves the queue-versus-consumption distinction seen in R-F's source map without importing another harness's native semantics into every route.

## R-J-Q08 Awareness without reading every token

Derive a model-free attention list from canonical questions, approvals, typed blockers, stale advice, unresolved effects, lease conflicts and incomplete replay. Each count is scoped to visible authorized objects and a named cut; do not count hidden members. Unseen activity means “events after this view's acknowledged cursor,” not “work completed.” Reading in one view need not mark another read unless the user explicitly opts into a shared presentation preference.

Show source facts separately: last received event, last canonical append, last known owned-process observation, blocked reason, expected boundary and observation age. A disconnected agent is last-seen/unknown, not idle or failed by inference. A high-output actor can be busy with no accepted result; a quiet actor can be waiting for a question or remote effect. Display coalesced frame counts and genuine gap markers. Causation links join request/answer/adoption; concurrent proposals retain a concurrent marker rather than a fabricated narrative order.

Head's awareness comes from canonical subscriptions. Goal amendments, revocation, PAUSE, conflicts, safety/settlement uncertainty and budget exhaustion are immediate control-state facts; routine text can await a bounded digest. Deterministic summaries use known event fields. Optional model recaps require an explicitly admitted route and reservation and cannot run on attach, graph refresh or every new viewer. They are labeled derived with source cuts, never hidden reasoning reconstruction or canonical authority.

## R-J-Q09 Views actors and context privacy

Use separate identities for logical actor, role run, goal, native/upstream loop, provider session, operation, view and projection. Two views of actor A share one execution identity but can show different authorized slices. A room showing A and B joins permitted **events**, not their complete model contexts. Every speaker label includes logical identity and GoalSpec revision; route is informative, not the actor's authority.

Context compilation occurs only for a separately admitted operation. It resolves explicit permitted capsule/evidence references under the recipient's privacy, egress and credential-account boundaries before retrieval. Joining the room does not enroll a new provider as a data recipient. Neither the room UI nor a peer can inject a private transcript wholesale. Keep owner instructions, peer advice, tool output and derived summaries typed and provenance-bound through forwarding and compaction. Content hashes and metadata can reveal equality, project names or activity and need the same audience analysis.

Forwarding to a new actor, changed model endpoint, export or restored view rechecks data-recipient scope. Revoking room access prevents future fetch/replay and clears controlled caches according to policy; it cannot prove deletion from already delivered contexts or an offline endpoint. Record that residual honestly. Separate processes, bots, panes or worktrees alone establish no OS or credential security boundary. R-E's trusted launch and R-P/R-Q's injection/memory qualification remain dependencies.

## R-J-Q10 Chat order is not authority

Treat accepted incoming text as a typed proposal, command intent, evidence, status or narration. Only the authenticated command path may request a canonical transition; revalidate its current principal, role grant, GoalSpec, plan revision, reservation, PAUSE and fencing domains at commit. A message that says “approved by Head” is still untrusted message content until joined to the actual approval receipt.

Canonical append gives reproducible serialization for audit. It does not make the first-arriving recommendation correct or authorized. Competing step proposals against revision R remain evidence until the authorized holder chooses one under the pre-existing conflict policy. Commit uses expected revision and current fences; a second attempted commit based on R receives a conflict. If two already-authorized ordinary commands race, serialization identifies which conditional write succeeded, but it cannot be used as a policy for settling conflicting owner intent. That ambiguity returns to Head and ultimately the Owner where necessary.

Causal ordering is a display aid. Lamport's distinction between happened-before and an imposed total order explains why order alone supplies neither consent nor semantic priority [RJ-S20]. Transcripts, room consensus, popularity, model rank, a signed message and wall-clock timestamps cannot create grants. Fixture F07 permutes proposal arrival without changing the specified authorized resolution; F08 refuses a valid-looking message with stale authority.

## R-J-Q11 Membership is not command authority

Store room membership as a Head-governed, authorized routing/observation relation with an audience revision. Effective rights remain the intersection of current grants, GoalSpec, constitutional policy, role lease, route/account eligibility, tools, privacy/egress, budget, PAUSE and effect-specific checks. Membership can narrow visibility; it never unions participant grants or account credentials.

A room join, @mention, tab focus, peer recommendation, receipt or adapter-reported role name cannot widen GoalSpec, publication/deployment, billing pool, data recipient, filesystem access, tools or credential visibility. A command carrying a peer's copied token must fail principal/consumer binding. The room transport has no credential-relay API; route descriptors use opaque authorized references, never credential bytes. Native and upstream actors obey the same outer admission contract while retaining their own loop owner.

For example, actor A may inspect an allowed test artifact and request B's review; B can receive only the permitted artifact subset and may answer within its own goal and allowance. A's paid account cannot silently fund B, and B's browser login cannot become A's ambient tool capability. Actual cross-goal resource transfer or new data exposure requires the appropriate explicit authority. Head itself cannot bypass Owner-only GoalSpec amendments.

Room UI redaction is not isolation. Strong credential non-access additionally needs the operator-provisioned D029 boundary and mediated outputs; same-user filesystem denial alone does not exclude a credential exported through a powerful authenticated CLI [R-E dependency]. No security claim is earned by this specification.

## R-J-Q12 Bounded coordination and consultation

A proposed `CoordinationLease` binds these independent fields:

- Lease ID/domain, issuer Head role, named holder principal/role run and exact goal/version
- One `room_id`, one `workflow_step_id`, step revision, frozen permitted participant set and membership revision
- Allowed message/proposal verbs and explicit exclusions; permitted context/evidence audiences
- Parent budget and a bounded reservation slice, depth/hop bound, outstanding-request bound and cycle policy
- Issue/expiry/revocation epochs, holder incarnation and monotonic step fence; expiry evaluated by the authoritative service, not a client clock
- Conflict-policy revision and the Head return target

The lease is nontransferable and cannot renew itself, add members, alter GoalSpecs, choose a new conflict rule, settle cross-goal disputes, change ARM lifecycle or act as a general plan writer. A proposal only becomes authoritative through Q13's separate executive authorization and canonical commit. Consultation grants no amendment right, even when the adviser is more capable or answers confidently.

Expiry, revocation, holder replacement, PAUSE or conflict retires the delivery alias and continuation eligibility, fences the step and returns coordination to Head. Returning ownership does **not** authorize Head inference or dispatch while PAUSE remains active. Previously received evidence remains historical; stale adoption and stale continuation are independently refused. Receipt of a late reply can be retained only if the current evidence-admission policy permits it; under literal M1A E-PAUSED, a fresh observation command is refused, while retained historical evidence remains inspectable [L14–L16].

Suspend a waiting consultation without occupying the only executor or read pump required by its consultant. Check both participant cycles and resource wait-for cycles. A bounded blocker is preferable to hidden deadlock or recursive “please ask Head” loops. Timeouts do not settle remote work or free uncertain reservations. Full Stop of a borrowed consultant operation must preserve unrelated work on that persistent consultant.

## R-J-Q13 One writer per workflow step

Distinguish three permissions and owners:

| Object or action | Sole canonical owner or authorized origin |
|---|---|
| GoalSpec amendment | Owner acceptance through the current governance path |
| Overall goal, room membership, authority envelope, conflict policy and ARM lifecycle | Head within Owner authority; never an ad hoc room chair |
| Tactical plan within an ARM GoalSpec | Current authorized ARM executive role lease; Head has only its separately defined rights |
| Step coordination and proposal | Current nontransferable CoordinationLease holder for exactly that step |
| Canonical transition commit | Single fenced canonical writer after all independent guards pass |
| Raw terminal INPUT/RESIZE | Current target-bound control holder, not an executive grant |

Where the same ARM holds both the executive and coordination leases, both bindings still appear. Where the step holder lacks executive plan rights, it submits evidence/proposal to the rightful executive; it cannot acquire the missing right by receiving a room message. Shared-room simultaneous valid proposals require Head's accepted resolution under the established contract [L05, L08]. This is deterministic authority mediation plus admitted reasoning when necessary, not a continuously running supervisor model.

The step commit binds expected plan and step revisions, executive lease, coordination lease where required, current goal, work/writer/PAUSE fences and the exact proposal/evidence IDs. At most one resulting transition can succeed for that expected step revision. A transition can be validly adopted yet its later external effect remain unsettled. Step completion therefore cannot be inferred from chat consensus, a model's “done,” a finished turn or a closed pane.

## R-J-Q14 Bounded fan-out and canonical append

Every view has finite byte credit, event credit, presentation queue, replay batch and rate limits. Also bound the number of view/projection keys globally; per-view bounds alone permit unbounded allocation through infinite distinct attach IDs. Backpressure is local to presentation. The broker continues draining its owned source and the canonical writer continues independently of how fast a terminal renders.

Persist a canonical event and its receipt/reference before distributing a presentation frame that can be coalesced or dropped. Command, lease, control, process-exit, question, approval, adoption and settlement facts are never disposable presentation. Repetitive progress can be rendered compactly only after its admitted record is durably classified. Retention is explicitly bounded and auditable; this does not promise indefinite storage of every token. If durable storage is exhausted, fail closed or gate source admission under a declared storage policy. Never claim canonical writes can succeed with unavailable storage, and never silently treat storage failure as a slow-view gap.

At exhausted credit, hold only bounded data, disconnect or use actual replay/snapshot recovery. ACK releases pending ownership but does not mint fresh CREDIT. Preserve M1B's literal reset restrictions and separately validate store facts. SDK loss before Recursion ingestion remains unknown unless a reliable sequence/query recovery path exists. SSH channel windows demonstrate bounded byte-flow mechanics, not canonical durability, fairness or Recursion's independent control reserve [RJ-S19].

Enforce a call-graph separation: `attach`, `tab_select`, `graph_refresh`, `peek`, `snapshot`, `replay` may call authenticated projection/query services only. They cannot reach model, actor-launch, index-build, plugin import/activation, credential or spend entrypoints. If optional payload is disabled or uncached, show a capability/cache-unavailable marker rather than activating it. Finite rendering and metadata lookup cost are real and measured; “no inference” does not mean zero CPU.

## R-J-Q15 PERF-010 matrix

Commit the full cross-product: **N = 0, 1, 5, 10, 20 passive views × idle and high-output**. Keep one separately counted deterministic control injector where needed, the actor workload, source events, retention policy, route stubs and broker configuration identical. The zero-passive-view baseline still drains output and admits control. Within each cell add a stalled reader, disconnect/reconnect, bounded credit exhaustion, replay, input/resize contention and Stop during saturation.

Collect p50/p95/p99 offered-input-to-command acceptance, offered-Stop-to-fence receipt, frame latency, canonical append delay, CPU, RSS, wakeups, IPC bytes, queue high-water marks, coalescing counts, process/handle counts and installed cursor lag. Measure offered arrival independently of a blocked producer so coordinated omission cannot hide a stall. Count model invocations, logical worker/actor creation, index builds and plugin activations globally, including helpers and retries. Provider counters are not necessary for the provider-free tripwire suite.

Hard failures are any attach-induced call/worker duplication, canonical durable loss, input corruption, stale control success, unbounded per-view/global memory, source relaunch on reconnect, or control/canonical progress dependent on reader acknowledgement. Finite fixture bounds and virtual-tick deadlines are specified in the appendix. Real p99 latency, RSS/CPU ceilings and supported terminal measurements remain **U** until an authorized local conformance campaign preregisters numeric budgets on D028 floors. A finite virtual-tick pass cannot be relabeled an OS latency SLO.

Views consume resources and may increase bounded rendering cost with N. They must not multiply the execution cost of the same admitted work. A view-dependent “summarize this agent” call violates the attach invariant even if its tokens are cheap or hidden in a subscription.

## R-J-Q16 Parallel performance claim and reversal rule

Reject “more parallel agents equals more performance.” Coordination, duplicated context, conflicting edits, retries and human review can consume the benefit of concurrency. The competing option is fewer, better-coordinated agents, including one capable agent using the same strongest permitted native tools, at the **same total authorized resource budget**. Required multi-agent capability remains available even if a particular default loses.

For representative dependency-light and dependency-heavy workloads, hold accepted-result rubric, source access, privacy, tools, total model/helper allowance, retry ceilings and verifier quality constant. Compare single-agent, bounded delegation and larger parallel fleets. Count wall time to an independently accepted outcome, false-green rate, defects, useful completions, owner reading/coordination/rework time, all-role tokens/known quota, retries, compaction/hydration, worktree reconciliation and machine cost. Missing quota stays unknown; do not translate it from API prices or sum inclusive parent and child totals twice.

**Decisive falsifier:** at equal budget and quality/authority floors, a larger fleet fails to improve the preregistered primary responsiveness endpoint or increases review/error cost beyond the declared noninferiority margin. One attractive fast example is insufficient. Reverse a fewer-agent-default recommendation only if paired representative trials show a repeatable accepted-outcome improvement with all floors and whole-workflow costs satisfied, including failure/recovery cases. No numeric superiority margin is invented here; the evaluation owner must set it before a separately authorized performance campaign. Provider-free fixtures can reject duplicated calls and incorrect accounting; they cannot measure model quality or subscription efficiency.

## R-J-Q17 Meta Muse Code comparison

<a id="muse-messaging-facts"></a>
**D — Muse messaging:** canonical peer names/full session IDs, sender attribution and receiver peer admission govern eligible same-user interactive sessions on one macOS/Linux machine; Windows/headless are excluded. Steer, queue, notify-only and wake policies are distinct; defaults can wake idle recipients. Peer data cannot approve tools, grant consent, change permissions or impersonate user input. Transcripts/task ownership remain separate. [RJ-S02]


| Cell | Evidence and scoped finding | Recursion disposition (I) |
|---|---|---|
| Active steer versus next-turn queue | D: [canonical facts](../ri/report.md#muse-interactive-facts) | Existing behavior to preserve, not novelty |
| Retract and interrupt | D: [canonical facts](../ri/report.md#muse-interactive-facts) | Preserve queue identity and display actual interruption scope |
| Addressing and attribution | D: [canonical facts](#muse-messaging-facts) | Existing attributed coordination |
| Delivery choices | D: [canonical facts](#muse-messaging-facts) | Recursion view reads remain passive; sending/waking is separately admitted |
| Scope | D: [canonical facts](#muse-messaging-facts) | Cross-route/node design is a proposed extension, not qualified availability |
| Authority and context | D: [canonical facts](#muse-messaging-facts) | This safety distinction already exists; do not claim invention |
| Adopted decision and room-step fence | **U:** Recursion-equivalent role/goal/step-fence adoption contract not established in reviewed pages | Proposed combined contract, not evidence the product lacks alternatives |
| Recursion route, isolation and N-view cost | **U:** no Recursion-qualified Muse profile or matching PERF-010 result | Later profile-specific verification |

At most, Recursion adds a proposed uniform authority/continuity projection across heterogeneous native and upstream loops. Session messaging, permission distinction and turn-aware controls are prior art. The comparison does not endorse a Muse route or establish legal embedding rights.

## R-J-Q18 OpenCode comparison across generations

<a id="opencode-v2-tui-facts"></a>
**D — v2 TUI:** tabs can close/reopen and switch sessions. Enter steers; leader then Enter queues. A side question uses the current context/model without entering subsequent conversation. These documented interactions do not qualify an installed v2 build. [RJ-S05]

<a id="opencode-v1-tui-facts"></a>
**D — v1 TUI:** session navigation, details, editor and compaction commands, and opt-in question/permission/error/completion notifications are documented. Exact no-effect reconnect and dirty-tree preservation remain unverified. [RJ-S04]


Never merge v1 and v2 capabilities into a fictitious universal OpenCode adapter. Mutable documentation is pinned by retrieval/hash; the v1 source inspection additionally uses commit `1ddb0873aee50d209d1a8d7f91b89c5daf692d49`. That source pin is not a verified installed release.

| Cell | V1 evidence | V2 evidence | Recursion implication (I) |
|---|---|---|---|
| Sessions and views | D: [canonical facts](../rf/report.md#opencode-server-facts), [canonical facts](#opencode-v1-tui-facts) | D: [canonical facts](#opencode-v2-tui-facts) | Tabs and multiple histories are existing behavior |
| Steer and queue | **D:** [canonical server facts](../rf/report.md#opencode-server-facts); **U:** active-step delivery/durable queue from this surface alone. **D/source:** inspected prompt appends user message, then invokes loop unless noReply [RJ-S17] | D: [canonical facts](#opencode-v2-tui-facts), [canonical facts](../rf/report.md#opencode-v2-facts) | Keep explicit versioned delivery capability; v1/v2 parity remains **U** |
| Pending cancellation/edit | **U:** v1 parity with a durable editable inbox not established here | D: [canonical facts](../rf/report.md#opencode-v2-facts) | A 204/no-op is not proof an already delivered input was retracted |
| Fork | D: [canonical facts](../rf/report.md#opencode-server-facts); **U:** coherent worktree snapshot | D: [canonical facts](../rf/report.md#opencode-v2-facts) | Conversation lineage is not a workspace/authority/budget clone |
| Interrupt | D: [canonical facts](../rf/report.md#opencode-server-facts); **U:** full external settlement | D: [canonical facts](../rf/report.md#opencode-v2-facts) | Show residual queue and ownership scope |
| Replay | **U:** complete durable multi-view replay from v1 SSE alone | D: [canonical facts](../rf/report.md#opencode-v2-facts) | Do not advertise “no replay”; qualify each surface independently |
| Side question | **U:** equivalent v1 contract here | D: [canonical facts](#opencode-v2-tui-facts) | It is inference, so never relabel it a passive Peek |
| Room authority/continuity | **U:** combined Recursion contract | **U:** combined Recursion contract | Uniform cross-loop semantics remain a hypothesis |

The [canonical migration note](../rg/report.md#opencode-migration-facts) supplies the API/lifecycle premise. API presence or wording does not prove a compatible installed binary. Next qualification must distinguish durable log retention, gap signaling, privacy filtering and application installation from live notifications; absence of automatic reconnect is not absence of a queryable log.

## R-J-Q19 Grok Build comparison and R-I extension

The precise source pin is `2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8`. R-I's dashboard correction is independently confirmed in the public pinned guide and state source. R-F's different pin must remain a separate version-specific observation.

| Cell | Evidence and scoped finding | Preserve or extend (I) |
|---|---|---|
| Dashboard topology | D: [canonical facts](../ri/report.md#grok-dashboard-guide-facts), [canonical facts](../ri/report.md#grok-dashboard-state-facts) | Do not claim a nested subagent dashboard tree; preserve parent/child provenance separately |
| Peek/reply | D: [canonical facts](../ri/report.md#grok-dashboard-guide-facts) | Show recipient and operation meaning; no implicit new session |
| Worktree dispatch | D: [canonical facts](../ri/report.md#grok-dashboard-guide-facts) | Dispatch is work; viewing/toggling an existing projection cannot spawn it |
| View/session/delete | D: [canonical facts](../ri/report.md#grok-dashboard-guide-facts), [canonical facts](../ri/report.md#grok-dispatch-lifecycle-facts); **U:** effective feature profile | Preserve guide/source/profile divergence; native close/archive/delete is not Recursion detach or Stop |
| Steer versus send now | D: [canonical facts](../ri/report.md#grok-keyboard-facts) | Never normalize both to active steer or Full Stop; blocked-turn Enter is also state-dependent |
| Fork and rewind | D: [canonical facts](../ri/report.md#grok-sessions-facts) | Require the coherent-fork section's capture before claiming productive continuity |
| Cross-route room adoption and security | **U:** Recursion-equivalent combined contract at this pin | Candidate extension only |
| Port cost | D: [canonical facts](../ri/report.md#grok-license-facts); **U:** measured safe port/maintenance cost | License availability is not cheapness or entitlement |

The [canonical keyboard exceptions](../ri/report.md#grok-keyboard-facts) rule out a universal busy-state shortcut.

Use the [canonical source/guide lifecycle distinction](../ri/report.md#grok-dispatch-lifecycle-facts) for exact branch behavior. No effective binary/configuration profile was run; a universal permanent-delete claim remains unsupported.

R-J extends R-I with a canonical addressed-message/consultation envelope, role and step fences, projection cursors, reader/control separation, synthetic fail predicates and cross-route continuity. It does not repeat a component inventory or select Grok's implementation. The dashboard is useful prior art even where Recursion intentionally uses different action labels to prevent accidental dispatch or deletion.

## R-J-Q20 Grok Bot comparison

| Cell | Evidence and scoped finding | Recursion distinction (I) |
|---|---|---|
| Persistent named agents | **D:** named Bots retain context and continue while a client is closed [RJ-S13] | Persistence and detach-like user experience are existing |
| Parallel shared computer | **D:** account Bots share files, browser sessions and app logins [RJ-S13] | Explicitly reject ambient sharing as Recursion's authorization model |
| Addressed group exchange | **D:** small groups, @addressing and visible asynchronous handoffs [RJ-S14] | Visible handoffs and addressed coordination are existing |
| Stage owner | **D:** guidance asks for one owner per stage to reduce duplicate/noisy work [RJ-S14] | Recursion proposes enforced fenced step ownership, not merely prose convention |
| Security boundary | **D:** separate Bots are expressly not security boundaries [RJ-S15] | Recursion rooms/panes likewise prove no isolation; D029 is a separate requirement |
| Goal amendment and settlement | **U:** exact Recursion-equivalent typed adoption/GoalSpec/fence rules in reviewed docs | Do not infer absence, authority transfer or external rollback from chat behavior |
| Measured cost and portability | **U:** same-budget Recursion comparison or measured port cost | No performance/portability claim |

Preserve clear responsibility, explicit addressing and visible handoff history. Reject the assumptions that a shared computer grants every agent use of every login, that a chat handoff transfers authority, or that a group needs an extra Chief-of-Staff executive. The comparison concerns documented behavior, not an assertion that Grok Bot's own policy lacks safeguards.

## R-J-Q21 Candidate differentiation and falsification

| Candidate combined claim | Strong comparison | Falsifier | Current status |
|---|---|---|---|
| Visible consultation with distinct accepted/delivered/adopted and bounded step fence | Muse peer data plus structured protocol receipts; existing durable inbox/workflow systems | A supported baseline preserves the same authority semantics with equal or less operator effort, or Recursion permits stale adoption | **I/U**, not demonstrated novelty |
| Authorized task survives native/upstream switch, compaction, source fork and loss of machine | Best native resume/fork plus permitted scripts, retained artifacts and explicit user grants | Incorrect next authorized action, repeated grants silently copied, evidence/accounting loss, or no advantage over baseline | **I/U**, D024 test target |
| N passive views do not multiply model/worker calls and keep control responsive | Existing detach-capable multi-client tools with equivalent source/workload | Any view-induced work, unbounded backlog, lost durable fact, false progress or control starvation | **I/U**, PERF-010 target |
| Cross-route privacy and consent remain visible | Per-session peer trust controls and independently scoped launch boundaries | Data reaches unauthorized provider/actor, unknown consumption becomes zero, or room membership enlarges rights | **I/U**, not a security certification |

No whole-market novelty conclusion follows from these four product comparisons. A new source or stronger baseline can erase differentiation without invalidating an accepted capability. D033 porting leverage is separately falsified if total adaptation, negative testing, licensing review and maintenance exceeds a native equivalent or cannot preserve semantics. Apache licensing alone cannot supply a measured cost. No language, store, transport, toolkit, runtime or vendor is selected.

## R-J-Q22 Provider-free acceptance predicates

All fixtures below are **UNEXECUTED**. `local-test-handoff.json` and `unexecuted-local-test-handoff.md` contain inputs, prerequisite gates, independent oracle, evidence and stopping conditions. IDs are stable; test names are logical scenario labels, not runnable product commands.

| Fixture | Exact acceptance/rejection predicate |
|---|---|
| F01 Duplicate identity | Same principal/message ID and same payload produces one acceptance and at most one delivery/adoption; different payload at same ID is refused without mutation |
| F02 Out-of-order receipts | All causally valid permutations converge to equal accepted facts; missing parent is held/marked missing, never invented; no effect admitted solely by arrival order |
| F03 Edit pending input | Revision-matched edit before delivery appends a replacement observation once; late/stale edit cannot alter delivered content or accepted owner intent |
| F04 Delete pending input | Cancellation and delivery race has one canonical winner; already delivered input remains historical; transport deletion never erases a grant or implies rollback |
| F05 Stale adoption | Any changed goal, plan, role/step lease, context source validity or PAUSE fence blocks old adoption and wake; previously admitted evidence remains attributable |
| F06 Controller contention | At most one input/resize holder per target; stale/foreign tokens reject; focus/resize by reader produces no target input or takeover |
| F07 Step contention | At most one plan transition for expected step revision; CoordinationLease-only origin cannot commit; arrival permutations do not decide conflicting intent |
| F08 Room authority expansion | Join/address/recommendation cannot mutate GoalSpec, members, grants, billing, privacy, credentials or executive count |
| F09 Lease lifecycle | Expiry/revocation/PAUSE/conflict retires alias/continuation and returns coordination to Head; no automatic inference, transfer or budget release |
| F10 Disconnect and replay | Late and reconnecting views converge to same authorized projection cut; no launch/effect duplication; lost ACK is reconciled by identity |
| F11 Real and forged gaps | A real verified gap requires RESET and fresh CREDIT before EVENT; a deferred event or forged floor cannot create a gap or unlock reset |
| F12 Close versus Stop | Closing any/all views changes no actor/process/effect ownership; explicit Stop changes only admitted scope and retains uncertainty |
| F13 Passive-view tripwires | Attach/switch/refresh/peek causes zero model/index/plugin/worker starts and no additional operation dispatch |
| F14 Slow-view control | Full presentation queues do not require a reader ACK for canonical append or typed Stop; saturated ingress/read-pump variants obey declared bounds |
| F15 PERF-010 soak | Every 0/1/5/10/20 × idle/high-output cell satisfies identical call counts, bounds, durable-event equivalence and input integrity; any violation fails the suite |
| F16 D022 scope | Aggressive, Full and Lazy preserve their different target sets/boundaries; borrowed-operation Stop leaves unrelated work; offline receipt remains unknown |
| F17 Consultation deadlock | Suspend releases the sole eligible executor, exposes wait-for blocker and allows the valid independent completion; no unbounded cycle/wake loop |
| F18 Privacy projections | Unauthorized fields, metadata, context and provider egress are absent; audience change invalidates replay access without erasing prior-disclosure record |
| F19 Coherent fork | Original state stays intact; derived context/artifact cut is coherent; live permits/reservations are not copied; changed capture forces retry/refusal |
| F20 Cross-loop continuation | Native and upstream source stubs preserve logical authority/evidence/accounting; unknown control support blocks or displays approved loss, never hidden helper inference |
| F21 Terminal injection | Escape/control text remains untrusted rendered data and cannot issue input, change title into authority, alter target, approve or launch |
| F22 Zero and unknown accounting | Passive views leave work totals unchanged; inclusive meters are not double-counted; missing/interrupted counters remain unknown and uncertain reservations held |
| F23 All ten controls | Each streaming/question/approval/queue/steer/interrupt/resume/fork/compaction/extension case keeps typed ID, revision, capability and truthful outcome; unsupported source behavior is not shown as supported |
| F24 Useful positive path | Authorized A-to-B consultation, answer, executive adoption and verified synthetic artifact complete after a pause-free allowed sequence; safety is not “pass by refusing everything” |

## R-J-Q23 What those fixtures can prove

A future provider-free implementation fixture can show, within its declared bounds, that the broker state and event contract obey these predicates. The independent observer compares canonical facts, operation-start records, tripwire counters, lease tables, installed projection manifests and synthetic effect receipts. It does not trust a UI success string or the implementation's own summary.

For detach, compare before/after actor, operation and ownership identities plus an independently generated useful event after every view closes. For a second view, all call/index/import/activation tripwires remain zero and admitted dispatch identities unchanged. For slow-client isolation, stop consuming one view at a barrier, saturate its bounded queue, then require unrelated canonical append and Stop acceptance without an ACK from that view. For topology, exhaust room joins, renames, role-looking messages and handoffs in the finite corpus; canonical portfolio-executive identity stays the pre-existing Head and no new role right appears.

These are deliberately useful-positive and negative traces. A system that rejects every message or stops every actor fails F24/F16/F17. A provider-free pass does not prove real OS containment, network authentication, hostile escape resistance, human comprehension, renderer conformance, account entitlement, model quality, quota savings or production durability. Those require separately authorized exact-build/profile sessions and independent verification. No such execution occurred here. ACP documents cancellation and final prompt-turn status separately from in-flight notifications [RJ-S16]; that protocol surface does not settle arbitrary external effects.

## Coherent forks and D022 control details

This section extends Q04/Q09/Q12/Q19/Q22; it does not add a twenty-fourth research question.

A conversation fork, a Git worktree and a coherent task continuation are three different products. A proposed fork manifest binds source logical actor/run/goal/plan revisions, source session/turn and canonical cursor, context capsule and evidence validity, effective config/route revision, source HEAD/index, tracked dirty bytes, scoped untracked/ignored artifacts, exclusions and parent lineage. Capture at a cooperative boundary or verify pre/post manifests around immutable capture; changed inputs force a new capture or refusal. Symlinks, submodules, binary/large files and excluded secrets require explicit handling. Never stash/clean/truncate the source merely to obtain a convenient snapshot.

Workspace creation and session launch have separate receipts; partial creation never earns an isolated-running-agent badge, and an uncertain launch is reconciled rather than repeated. The original unfinished work and exact captured artifact remain inspectable. The derived actor gets a new role/operation identity and separately admitted grant and allowance slice; it does not inherit a live writer token, unconsumed effect permit, input lease or duplicated parent reservation. Copying evidence of an earlier approval is not issuing a new approval. A delivery alias, pending question or queued steer bound to the source cannot awaken the fork. Moving a fork to a different privacy/route boundary rechecks disclosure before materializing its capsule. Source provenance and hashes can remain protected even when the owner sees a redacted display.

A useful mixed-fleet room must expose Stop target ownership, not just a route's cancel method:

- **Aggressive:** fence further selected-agent dispatch and interrupt without waiting; enumerate descendants separately and keep uncertain effects
- **Full:** fence the selected rooted owned set, including relaunchers and owned children; a borrowed consultant contributes only the owned operation, not its unrelated sessions or the whole shared server
- **Lazy:** close admission, name the next observable permitted operation boundary and deadline, then stop; timeout is waiting/escalation, never invented completion of hidden reasoning
- **checkpoint / interrupt / drain:** retain the configured policy and exact admitted in-flight classes; none automatically changes Stop mode or supplies rollback

A room-wide Stop is a separately previewed admitted target set, not an incidental consequence of closing the room or of a step lease expiring. Observe local acceptance, recipient fence installation, cancellation delivery, process termination, external settlement and independent verification separately. An unreachable node remains unknown with held reservations. The current actor may return to Head coordination while effects remain quarantined; a new route cannot repeat the ambiguous effect merely because it has a fresh provider session.

## Recommendation register

Every proposal in the numbered sections is covered by its matching row. Accepted invariants are not reopened; alternatives retain them or are explicitly narrower comparison baselines, never silent replacements.

| ID | Recommendation | Real competing option | Decisive falsifier | A pass does not prove |
|---|---|---|---|---|
| RJ-R01 | Use hybrid actor navigation and selected consultation stream inside an enabled profile | Per-actor-only views or Head-relayed messages | Hybrid increases wrong-target/authority errors or review burden at matched information and accepted quality | Actual human comprehension, accessibility or performance |
| RJ-R02 | Target-bound passive Peek with separately authorized typed Reply | Open the target full-screen before every reply | Peek launches work, steals control, retargets a draft or costs more review effort than explicit navigation | Source adapter delivery or prompt injection resistance |
| RJ-R03 | Explicit atomic control transfer with typed input and resize tokens | Explicit release then reacquire with no takeover | Two controllers can input/resize one target or a focus change grants control | OS terminal integration or authenticated transport |
| RJ-R04 | Detach projections while broker retains process and actor ownership | External multiplexer detaches thin views over the same broker | View close kills work, reconnect relaunches or second view duplicates dispatch | Process containment on supported platforms |
| RJ-R05 | Consistent-cut snapshots with authorization-scoped replay cursors | Bounded full authorized replay without snapshots where retention allows | Reordered/reconnected views diverge, a false gap is accepted or an uninstalled snapshot permits progress | Power-loss durability or authenticated retention facts |
| RJ-R06 | Render independent acceptance delivery adoption and settlement receipts | Compact status row plus expandable independent receipt inspector | Users/oracle infer adoption or settlement from acceptance, or essential receipt identity is hidden | Truth of advice or real effect completion |
| RJ-R07 | Versioned addressed messages with explicit delivery and wake policy | Queue-only messaging on routes without qualified steering | A stale steer silently retargets, dispatch repeats after ACK loss or send-now is disguised interrupt | Model compliance or upstream conformance |
| RJ-R08 | Deterministic attention list with event age and causal drill-down | Manual filters over the full attributable event stream | Counts leak hidden objects, stale sessions look live or alerts add model calls | Measured cognitive benefit |
| RJ-R09 | Per-recipient authorized event projections and explicit context capsules | Isolated per-actor views with deliberate evidence forwarding | Room membership exposes unauthorized context metadata or a new provider receives data | Security boundary between same-user processes |
| RJ-R10 | Keep proposals as evidence until authority and expected revisions validate | Head-only plan proposal intake with the same commit guards | Arrival permutation alone decides conflicting intent or stale proposals commit | Decision quality or complete unbounded concurrency proof |
| RJ-R11 | Intersect per-actor grants at message and effect admission | Stricter isolated rooms with fewer allowed participants | Join mention or recommendation broadens any goal privacy billing tool or credential dimension | Credential non-access without D029 boundary |
| RJ-R12 | Nontransferable expiring single-step coordination with explicit return to Head | Head retains coordination for every step | Lease adds members/transfers itself or expires without retiring continuation; unrelated work is killed | Remote cancellation or liveness under permanent failure |
| RJ-R13 | Separate coordination proposal executive authorship and canonical writer | Head proposes every shared-room step while ARMs supply evidence | A coordination-only holder commits or two transitions succeed for one expected step revision | Full-system writer fencing on physical hosts |
| RJ-R14 | Per-view byte/event credit and durable append before presentation loss | Bounded snapshot polling over the same canonical log | Slow reader blocks append/Stop, drops durable facts or attach activates optional work | Production CPU/RSS/latency SLOs |
| RJ-R15 | Qualify every PERF-010 N and load cell with independent offered-load observations | Independent end-to-end external observer versus independently reviewed replay/OS reconciliation instrumentation over identical required PERF-010 N/load cells; negative/workload control only: Use fewer open views while preserving the same optional capability | Any cell multiplies execution calls, grows queues beyond declared bounds or hides delay | Human-scale usability or platform-independent latency |
| RJ-R16 | Use fewer well-coordinated agents as the challenge baseline, require equal-budget benefit | Larger admitted parallel fleet under identical budgets and floors | Fewer-agent recommendation reverses only with repeatable larger-fleet accepted-outcome benefit without floor/cost regression | Model quality savings or quota efficiency from synthetic data |
| RJ-R17 | Reuse Muse interaction lessons with bounded version-specific capability mapping | Drive eligible Muse sessions directly with their existing peer messaging | Recursion claims novelty for peer messaging or mishandles delivery/approval separation | Muse entitlement SDK embedding or Recursion route qualification |
| RJ-R18 | Keep OpenCode generations and event surfaces separate | An exact single-version supported profile only | V1 inherits v2 claims or live-only global SSE is confused with the experimental durable session log | An installed v2 binary or equivalent recovery guarantees |
| RJ-R19 | Preserve Grok top-level dashboard topology and explicit action meanings | Native Grok Dashboard with source-specific controls | Recursion invents subagent rows at the pin or silently maps cancel-and-send to steer/Full Stop | UI conformance or inexpensive porting |
| RJ-R20 | Preserve visible Bot handoffs while enforcing explicit Recursion rights | Independent per-actor conversations with authorized evidence forwarding | Shared-room membership yields ambient login use or a new executive tier | Grok Bot security assessment or Recursion isolation |
| RJ-R21 | Claim differentiation only for a verified combined continuity contract | Best supported native resume/fork/workflow plus explicit scripts and grants | Baseline matches or beats authority/evidence/accounting continuity and owner effort | Whole-market novelty or universal superiority |
| RJ-R22 | Use independently checked positive/negative synthetic schedules and mutants | Trace-based conformance with independently specified property assertions | Suite misses an intended wrong-guard mutant, accepts a common-mode oracle error or passes deny-all | Exhaustive physical/network/provider behavior |
| RJ-R23 | Instrument state and tripwires outside the candidate and retain exact witnesses | Manual scenario replay with independently collected event evidence | Only self-reported pass/UI badges support detach zero-work or no-extra-executive claims | Runtime behavior before execution or release acceptance |

## Open qualifications and precise next admissions

| Unknown | Required next evidence | Stop condition and current disposition |
|---|---|---|
| Room implementation and service entrypoint | Approved candidate plus independently authored provider-free oracle, then F01–F24 | No verified room entrypoint exists; do not invent a runnable command |
| Physical control reserve and containment | Native D028 profile, exact broker/OS/build, independent offered-load observer and scoped process/effect receipts | Any unrelated termination, stale input, false settlement or missing control progress fails; all profiles remain unqualified here |
| UI clarity and accessibility | Matched hybrid/per-actor/Head-relay trials with equal information, wrong-target/authority checks, plain-text and assistive workflows | A prettier view does not pass; independent outcome review and preregistered error/burden margins required |
| Source-specific control/replay | Exact installed interface/schema/build/config mapping for each tested upstream route, without extrapolating another generation | Unknown or lossy behavior stays explicit; no source-only route promotion |
| Performance and savings | Same-budget whole-workflow evaluation, including helpers/retries/compaction/review and independent acceptance | Missing accounting is unknown; no savings or parallel-speedup claim before evidence |
| Security and privacy | R-E trusted-launch and R-P/R-Q context boundaries plus adversarial recipient/egress tests | Room/pane identity alone never qualifies isolation |
| Porting cost | License/provenance review and measured adaptation/negative-testing/maintenance versus native equivalent | No cheap-port conclusion from source availability; no implementation started |

The structural source findings and exact unexecuted fixtures complete this research lane. They do not close G23, G29 or any runtime qualification. D020 availability, D022 vocabulary and D028 floors are accepted decisions with outstanding implementation proof, not reopened questions. D023 remains the first qualification priority, not a qualified profile. No new executive tier is proposed.

## Completion gate and artifact verification

The companion `question-coverage.json` retains every one of the 23 questions and 9 completion-gate bullets verbatim from the intake register and maps them to report sections. It distinguishes research response completeness from runtime qualification. The source register preserves exact public URLs, retrieval times, complete-response hashes and immutable pins where available. Repository citations use relative source identities at the stated snapshot, not private capture paths.

Only Markdown/JSON research artifacts were authored. No supplied repository script was executed or imported, and no target model/provider/harness call, test, benchmark, install, authentication, credential action, account operation, live-host action, spend, counsel contact, repository edit or publication occurred. Public source retrieval and artifact parsing/hashing are the only execution supporting this report. No DOCX was created.

Protected governance file hashes were compared with the prior snapshot manifest. Delivery files were scanned for secret-shaped strings and private absolute work paths; any findings would block delivery. The exact scope and result are recorded in `artifact-qa.json`. A clean bounded scan is not a proof that all possible secrets can be recognized. Independent substantive review and runtime acceptance remain outstanding.

## Citation key

Public references below link to the primary source. Repository IDs resolve to complete-file hashes and relative identities in `source-register.md` at the stated commit. The historical records do not become new runtime evidence.

[RJ-S01]: https://dev.meta.ai/docs/muse-code/interactive "Muse Code interactive"
[RJ-S02]: https://dev.meta.ai/docs/muse-code/session-messaging "Muse Code session messaging"
[RJ-S03]: https://opencode.ai/docs/server/ "OpenCode v1 server"
[RJ-S04]: https://opencode.ai/docs/tui/ "OpenCode v1 TUI"
[RJ-S05]: https://opencode.ai/v2/docs/cli/tui/ "OpenCode v2 TUI"
[RJ-S06]: https://opencode.ai/v2/docs/api "OpenCode v2 API"
[RJ-S07]: https://opencode.ai/v2/docs/build/client/ "OpenCode v2 client"
[RJ-S08]: https://opencode.ai/v2/docs/migrate-v1/ "OpenCode v2 migration"
[RJ-S09]: https://raw.githubusercontent.com/xai-org/grok-build/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/23-dashboard.md "Grok Build dashboard"
[RJ-S10]: https://raw.githubusercontent.com/xai-org/grok-build/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/03-keyboard-shortcuts.md "Grok Build keyboard guide"
[RJ-S11]: https://raw.githubusercontent.com/xai-org/grok-build/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/17-sessions.md "Grok Build sessions"
[RJ-S12]: https://raw.githubusercontent.com/xai-org/grok-build/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/views/dashboard/state.rs "Grok Build dashboard state"
[RJ-S13]: https://docs.x.ai/grok-bot/overview "Grok Bot overview"
[RJ-S14]: https://docs.x.ai/grok-bot/chat-and-collaboration "Grok Bot collaboration"
[RJ-S15]: https://docs.x.ai/grok-bot/faq "Grok Bot FAQ"
[RJ-S16]: https://agentclientprotocol.com/protocol/prompt-turn "ACP prompt turn"
[RJ-S17]: https://raw.githubusercontent.com/anomalyco/opencode/1ddb0873aee50d209d1a8d7f91b89c5daf692d49/packages/opencode/src/session/prompt.ts "OpenCode v1 session prompt source"
[RJ-S18]: https://raw.githubusercontent.com/xai-org/grok-build/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/LICENSE "Grok Build Apache license"
[RJ-S19]: https://www.rfc-editor.org/rfc/rfc4254.txt "SSH connection protocol"
[RJ-S20]: https://lamport.azurewebsites.net/pubs/time-clocks.pdf "Lamport time clocks and ordering"
[RJ-S21]: https://raw.githubusercontent.com/cloudevents/spec/v1.0.2/cloudevents/spec.md "CloudEvents core specification"
[RJ-S22]: https://raw.githubusercontent.com/xai-org/grok-build/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/app/dispatch/dashboard.rs "Grok Build dashboard action dispatch"

- **L01**: `CONTROL_PLANE.md`; Operative governance and precedence
- **L02**: `ANCHOR.md`; Mission current role and scope
- **L03**: `state/DECISIONS.md`; D017 through D033
- **L04**: `state/goals/goal-recursion-v3-harness-orchestrator.md`; Active parent goal
- **L05**: `docs/v3/INTERACTION-SURFACES.md`; Room consultation and CoordinationLease
- **L06**: `docs/v3/TERMINAL-RUNTIME.md`; Detach control Stop cursor and PERF-010
- **L07**: `docs/v3/INTERFACE-STRATEGY.md`; Common command-query and interaction states
- **L08**: `docs/v3/EXECUTIVES.md`; Current authority-consistent role and consultation sections; retired Hermes clauses excluded
- **L09**: `docs/v3/PRODUCT.md`; Native upstream and accepted scope; stale GUI exclusions flagged
- **L10**: `docs/v3/PLUGINS-AND-EDITIONS.md`; No activation on view and capability graph
- **L11**: `docs/v3/ARCHITECTURE.md`; Current-authority-consistent evidence and owner boundaries; older drift excluded
- **L12**: `docs/v3/construction/interface-probes-20260907/evidence.json`; Historical bounded probe records, not rerun
- **L13**: `docs/v3/M1B-WIRE-PROFILE.md`; Frozen one-client one-stream wire audit and credit/reset
- **L14**: `docs/v3/construction/typed-consultation-20260908/findings.md`; SC-EPOCH-03 scoped historical finite findings and rejected shared-oracle run
- **L15**: `docs/v3/M1A-FIXTURE-ORACLES.md`; Literal E-PAUSED and exact duplicate receipts
- **L16**: `docs/v3/construction/interface-probes-20260907/contract-vectors.json`; Historical finite consultation and recipient-fence vectors
- **L17**: `docs/v3/research-lane/GAPS.md`; G23 and G29 open implementation/evaluation; closed Owner decisions preserved
- **L18**: `docs/v3/research-lane/RESEARCH-INDEX.md`; Current intake/evidence map
- **L19**: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md`; Edges 10 19 20 24 25; final future-lane labels stale
- **L20**: `docs/v3/research-lane/HARNESS-COVERAGE.md`; Per-harness source-only coverage and thin UI flows
- **L21**: `docs/v3/research-lane/SYNTHESIS.md`; Prior research synthesis, not normative or newly executed
- **L22**: `docs/v3/prompts/dot-research-20261002b/R-J-multi-agent-terminal-communication.md`; Authoritative lane brief and completion gate
- **L23**: `AGENTS.md`; Repository operating rules
- **L24**: `docs/v3/START-HERE.md`; Orientation; retired Hermes clauses superseded

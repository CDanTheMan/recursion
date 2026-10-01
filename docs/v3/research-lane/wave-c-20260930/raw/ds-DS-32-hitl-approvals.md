---
title: DS-32 — Human-in-the-Loop Approvals, Forwarding, and Consultation
source-prompt: DS-32 — human-in-the-loop approvals, forwarding and consultation
session: Wave C Deep Research (self-contained handoff)
retrieved: 2026-09-30
status: research-evidence-not-a-decision
verification: not independently verified by Recursion; no rerun
---

# DS-32 — Human-in-the-Loop Approvals, Forwarding, and Consultation

## Executive summary

The governing DS-32 brief fixes several boundaries that this research must preserve: Recursion v3 remains provider-neutral; the Owner remains the ultimate authority; direct Owner-to-ARM communication is already accepted; consultation must preserve separate request, delivery, answer, adoption, and effect-settlement lifetimes; notifications are projections of canonical state rather than the state itself; and Aggressive, Full, and Lazy Stop plus preserved forks are accepted interaction concepts rather than topics to reopen. The brief also explicitly forbids treating a host-generated reply or a protocol acknowledgment as human approval. fileciteturn0file0

The central finding is that **human-in-the-loop safety is strongest when approval is bound to the exact proposed effect and revalidated at the boundary that actually controls that effect**. A callback can collect a decision, and a pre-tool hook can reliably intercept a tool path inside a particular harness, but neither by itself proves that every resource-changing path passes through that decision point. OpenAI's Agents SDK demonstrates why provenance matters: approval callbacks can make decisions programmatically and resume execution without a human, while its long-running-approval guidance requires server-owned pending state, authenticated and authorized reviewers, validation against stored requests, and atomic consumption to prevent replay. Anthropic's Agent SDK provides a `PreToolUse` hook with a specific tool-use identity, but that remains a hook in the agent execution path. Kubernetes admission control illustrates the stronger pattern: the API server itself mediates object persistence, while its documentation also warns that side effects performed *by the webhook* are not transactionally equivalent to successful persistence and therefore require reconciliation. citeturn13view0turn14view1turn14view2

Accordingly, this report recommends a **canonical pre-effect authorization record plus resource-enforced mediation**, with callbacks and hooks retained as early screening/user-experience mechanisms rather than promoted into the final authority boundary. Every consequential action should be bound to its exact target, normalized arguments, grant and lease generation, current goal/task version, principal, expiry, idempotency identity, decision receipt, and eventual effect receipt. Approval and effect are separate facts: an approved action can fail, remain uncertain after interruption, or become stale before it executes. OpenAI explicitly distinguishes its sandbox boundary from approval policy and allows either a user or an automated reviewer, reinforcing the need to model *who decided* independently from *what boundary can actually be crossed*. citeturn14view0turn13view0

For steering and deferred interaction, the most useful public precedent is OpenAI's Responses steering contract: `response.steer.accepted` means the server owns queued input, **not that the input has been applied**; the successor `response.created` event is the documented commit point. That is precisely the distinction Recursion needs between receipt, delivery, and semantic effect. Durable workflow systems provide a complementary lesson: Temporal reconstructs workflow state from event history after worker failure rather than treating process memory as authoritative. citeturn14view3turn14view4

For consultation, no reviewed agent framework exposes the complete Recursion contract of **advice delivery → answer → lease-qualified adoption → separate effect settlement**. OpenAI's documented patterns distinguish a manager that retains control while calling a specialist from a handoff in which the specialist becomes active, while Kubernetes supplies explicit lease-holder, renewal, expiry, and optimistic-concurrency primitives. Taken together, they support—but do not themselves implement—the DS-32 proposal: an answer should remain attributable evidence even when a changed task/lease makes it ineligible for authoritative adoption. citeturn14view6turn16view1

A material specification gap remains. The supplied brief repeatedly states that the accepted interaction contract has **ten terminal controls**, but it does not enumerate or define those ten controls. fileciteturn0file0 The control matrix below therefore contains ten explicit `unknown` rows instead of inventing names or semantics. This is intentional evidence discipline: unknown is not zero, and an unstated accepted control must not be reverse-engineered from surrounding prose.

The completion result is therefore: **the approval, steering, consultation, Stop, preserved-fork, notification, accessibility, and truthful-view mechanisms can be specified to a testable level from the supplied brief and public primary sources; the ten individual terminal-control contracts cannot be completed beyond explicit unknown placeholders until their accepted definitions are supplied.** No Owner decision is reopened, no topology/protocol/store is selected, and no live provider, transport, deployment, or implementation trial was performed.

## Approval and pre-effect mediation

### Where the enforcing resource actually sits

Three superficially similar mechanisms have materially different safety properties.

| Mechanism | Where the decision occurs | What it can establish | Failure class it does **not** close when it is not the effecting resource |
|---|---|---|---|
| Approval callback | Application/agent harness callback before resumption | A policy function or reviewer returned approve/reject for a represented request | It cannot prove that a human made the decision, that every alternate effect path invokes the callback, or that the eventual effect still has identical arguments/state |
| Always-invoked pre-effect hook | Harness execution path immediately before the harness invokes a tool | Every tool call *through that instrumented path* can be inspected, denied, logged, or modified | It does not prevent a resource from being changed through another path, nor by an already-started operation beyond the hook's control |
| Resource-bound mediation | Component that actually admits or performs the state-changing operation | The resource can refuse effects lacking a current, valid authorization | It still cannot govern effects outside that resource, and any mediator's own out-of-band side effects require separate settlement/reconciliation |

OpenAI's Agents SDK makes the first distinction concrete. Sensitive tool execution can pause for approval, but local shell/apply-patch and hosted MCP integrations may instead use programmatic approval callbacks; when such a callback returns a decision, execution can continue without a human response. The same documentation treats each ordinary approval as scoped to a particular tool-call identity and advises server-side applications not to accept replacement tool calls, arguments, approval records, or serialized state from a client. citeturn13view0

Anthropic's public Agent SDK illustrates the second layer. A `PreToolUse` event contains the tool name, tool input, and a unique `tool_use_id` for the tool about to execute. That is a strong basis for correlation and audit inside the harness, but the public contract is still a hook over that SDK's tool path; it is not documentation that the underlying filesystem, network endpoint, process service, or external API is unreachable by every other path. citeturn14view1

Kubernetes illustrates the third pattern and its limit especially clearly. Admission webhooks participate in the API-server path that governs whether an API write proceeds. Yet Kubernetes explicitly warns that a webhook's *own* out-of-band side effect must be reconciled because invocation of the admission webhook does not guarantee that the admitted Kubernetes object will subsequently be persisted: another webhook can alter it, storage can conflict, or the server can fail before persistence. citeturn14view2 The generalizable lesson is that an approval observation and an effect settlement are separate records even when the approval system is well integrated.

OpenAI's Codex documentation reinforces another distinction worth importing without importing its policy wholesale: **sandboxing and approval are separate controls**. Its documented configurations independently define filesystem/network boundaries, when escalation requires approval, and whether eligible requests are reviewed by a user or an automatic reviewer. Automatic review does not change the underlying sandbox boundary. citeturn14view0 For Recursion, upstream harness permission systems can therefore be treated as adapter evidence or additional containment, but not as substitutes for Recursion's GoalSpec, grants, leases, and canonical authority model. That last sentence is a design inference grounded in DS-32's accepted authority boundary. fileciteturn0file0

### Staleness, replay, retargeting, and reviewer provenance

A safe approval must reject four classes independently.

| Failure | Detection | Required rejection behavior |
|---|---|---|
| **Stale decision** | Goal/task version, target-resource version, relevant grant version, lease generation, action revision, or expiry differs from the approval's bound values | Preserve the reply as an attributable event, return a typed stale conflict, perform no effect |
| **Replay** | Decision/request identity is already atomically consumed | Return an already-consumed/replay conflict; never resume or execute it again |
| **Retargeted action** | Submitted target, normalized arguments, scope, action hash, or tool-call identity differs from the server-owned approved proposal | Reject the changed request; require a new proposal and decision |
| **Non-human reviewer presented as human** | Decision principal/provenance says host, policy engine, model reviewer, callback, or unknown rather than authenticated Owner/human delegate | Record the actual principal; never emit “human approved” |

OpenAI's long-running HITL guidance is unusually direct on the replay and retarget cases: deserialized run state does not authenticate either the snapshot or the reviewer; reviewer identity should come from application authentication rather than a request body; authorization is separate from possessing an ID; decisions must be checked against server-owned pending requests; replacement arguments or serialized state must not be accepted from the client; and pending decisions should be consumed through an atomic owner-checked transition so concurrent or replayed submissions cannot resume the same snapshot twice. citeturn13view0

Kubernetes's lease model supplies a useful analogue for delayed authority. Its Lease objects carry holder identity, acquisition/renewal information, duration, and transition count, while coordinated leader election uses the object's `resourceVersion` so concurrent attempts cannot both become authoritative; after expiry, a different candidate can acquire the lease. citeturn14view5turn16view1 Recursion should not copy Kubernetes election semantics literally, but binding adoption eligibility to a lease identity **and generation/version** follows the same concurrency principle: the answer can survive; its former authority context does not.

### Making “no undeclared effect” falsifiable

The proposed pre-effect record should contain, at minimum:

| Field group | Required binding |
|---|---|
| Identity | `proposal_id`, `decision_id`, `effect_attempt_id`, canonical event identity |
| Exact action | Operation type, normalized arguments, target resource/object, action revision or digest |
| Scope | Permitted resource set, operation class, maximum extent, any bounded sub-action set |
| Recursion authority | Goal ID/version, task ID/version, grant ID/version, current lease ID/generation |
| Principal | Requesting actor, deciding principal, authentication/provenance class, executing adapter/resource |
| Freshness | Creation time, expiry/deadline, expected target revision/precondition |
| Replay control | Single-use decision status plus idempotency key where the target API supports one |
| Execution | Attempt time, exact request submitted to the resource, resource receipt/operation identity |
| Settlement | `applied`, `rejected`, `failed`, `unknown`, or `reconciled`, with evidence reference |
| Causality | Parent event, causation ID, correlation ID, route/session only as non-authoritative metadata |

This is a **proposal**, not a claim that the cited platforms expose exactly this schema. It combines the exact-call and server-owned-state discipline documented by OpenAI with lease/version concurrency patterns documented by Kubernetes. citeturn13view0turn16view1

The decisive invariant is:

> **No authoritative effect is considered settled merely because approval exists.**

The evidence chain must instead be `proposal → valid decision → effect attempt → effect receipt/outcome`. If the process is killed after dispatch but before an external system's outcome can be established, the correct state is `unknown`, not `failed` and not `succeeded`. Kubernetes's webhook warning and OpenAI's production HITL guidance both explicitly motivate reconciliation of uncertain side effects rather than blindly replaying them. citeturn14view2turn13view0

This mechanism does **not** prove exactly-once behavior in arbitrary external services. It makes uncertainty observable and makes undeclared authorization detectable; actual exactly-once semantics remain dependent on the target resource's transactional/idempotency properties.

## Steering, question durability, forwarding, and recovery

### Active steering is not queued follow-up

The most important semantic separation is between **receipt**, **application**, and **next-turn scheduling**.

OpenAI's current Responses steering documentation explicitly states that a `response.steer.accepted` event means steering input has been validated and queued and that the server owns the input; it does not mean the input has been applied. The successor `response.created` event is the documented commit point, and input that cannot be committed is returned with a failure event. Accepted steering can also remain pending while a response waits for client-owned tool output or approval. citeturn14view3

Recursion should therefore use distinct target types:

| Input type | Required target identity | Delivery/effect contract | Must **not** do |
|---|---|---|---|
| **Active-turn steer** | Actor + exact active turn/operation revision + lease generation | Append accepted steer, then emit separate application/commit event if the running turn incorporates it | Treat queue ownership as proof the turn saw it |
| **Queued follow-up** | Actor/conversation + explicit “next eligible turn” queue position or parent lineage | Durable append; bound to a later turn only when that turn is created | Modify the currently executing turn |
| **Clarifying-question answer** | Immutable question ID + question revision + asker identity/lease + task version | Accepted only while that exact waiter remains open and eligible | Answer a replacement question with the old reply |
| **Status query** | Read projection/canonical task identity | Return state without a task-control transition | Cancel, steer, pause, supersede, or alter the assignment |

A decisive negative trace for an active steer is `steer accepted → no steer-applied/successor event → UI nevertheless claims “steer applied.”` A decisive negative trace for a queued follow-up is any current-turn semantic transition causally attributed only to the queued-next-turn message. For a status query, any Stop/cancel/assignment mutation in its causal descendants is failure.

### Durable questions and waiters

A clarifying question should be represented as a durable object rather than an ephemeral blocking call:

`question_id + revision + asker actor/lease + goal/task version + answer schema + opened event + expiry + state`.

Its durable state machine should be:

`OPEN → ANSWERED | DECLINED | EXPIRED | REPLACED | CANCELLED`.

`REPLACED` creates a **new** question identity. A delayed answer naming the old identity is retained as evidence but cannot silently satisfy the replacement waiter. This is a proposal derived from the DS-32 requirement that deferred questions survive crash/reconnect without retargeting or resurrection. fileciteturn0file0

Temporal demonstrates the relevant durability principle without prescribing Recursion's implementation: workflow state is reconstructed by replaying persisted event history; signals, updates, activity completions, timers, and child completion create workflow tasks; previously executed operations are replayed from recorded history instead of simply being reissued; and another worker can reconstruct state after a crash. citeturn14view4 The importable lesson is **event-backed waiter identity**, not Temporal itself as a required store/framework.

Recovery must therefore prove all of the following:

1. after restart, the same still-open `question_id` is restored;
2. an already answered question cannot reopen;
3. an expired/replaced question cannot consume a delayed reply;
4. two concurrent answers cannot both become authoritative;
5. crash after answer append but before presentation does not cause the answer to be forgotten.

Those are testable proposals; DS-32 requires the semantics but does not mandate a persistence technology. fileciteturn0file0

### Multiple clients and presentation acknowledgments

A multi-client view should maintain three separate acknowledgments:

**Canonical receipt** says the system durably accepted event `E`.  
**Presentation receipt** says client/surface `C` received or rendered projection `E`.  
**Semantic acknowledgment** is a new attributable action by an authorized principal—such as approving, adopting, steering, or answering.

The second can never manufacture the third. This directly preserves DS-32's requirement that presentation or host-generated acknowledgments must not imply human observation or approval. fileciteturn0file0

For replay detection, a durable event identity can follow the general CloudEvents principle of carrying stable event source/identity so redelivery is distinguishable from a new semantic event; this is an interoperable reference model, not a proposal to require CloudEvents as Recursion's protocol. citeturn13view10

### Notification projection and transport loss

The recommended projection pipeline is:

`canonical append → projection queue → optional coalescing → transport attempt → presentation receipt/cursor`

not:

`transport availability → canonical append`.

That ordering follows the DS-32 accepted rule that presentation throttling must not block canonical control or PAUSE events. fileciteturn0file0

For an unavailable, revoked, or replaced remote surface, the canonical actor and work state should remain unchanged; only that projection capability becomes unavailable. Upon attachment of a usable surface, projection resumes from its last durable cursor. Duplicate events are ignored by canonical event identity; out-of-order events are held/reordered or displayed with an explicit gap/staleness indicator rather than silently interpreted in arrival order. This is a design proposal consistent with the brief's accepted notification model and event-identity practices. fileciteturn0file0 citeturn13view10

The following events should be **non-coalescible at the canonical layer**: Stop requests and settlements, PAUSE, approval requests/decisions, authority/lease transitions, consultation adoption, question replacement/expiry, and effect settlement. A presentation surface may summarize repetitive activity only *after* the individual canonical events exist. That is a proposal; the exact full non-coalescible set remains an Owner-policy question.

## Terminal controls, Stop modes, and preserved forks

### The ten terminal controls

The research packet asserts that the accepted interaction contract contains ten terminal controls, but does not list their names or individual semantics. fileciteturn0file0 Inventing them would violate the brief's evidence discipline. The required control-by-control matrix is therefore complete in row count but explicitly unresolved in content.

| Accepted control slot | Supplied semantic definition | Observable contract | Decisive negative trace | Classification |
|---|---|---|---|---|
| Terminal control T1 | **unknown** | **unknown** | **unknown** | Unverified |
| Terminal control T2 | **unknown** | **unknown** | **unknown** | Unverified |
| Terminal control T3 | **unknown** | **unknown** | **unknown** | Unverified |
| Terminal control T4 | **unknown** | **unknown** | **unknown** | Unverified |
| Terminal control T5 | **unknown** | **unknown** | **unknown** | Unverified |
| Terminal control T6 | **unknown** | **unknown** | **unknown** | Unverified |
| Terminal control T7 | **unknown** | **unknown** | **unknown** | Unverified |
| Terminal control T8 | **unknown** | **unknown** | **unknown** | Unverified |
| Terminal control T9 | **unknown** | **unknown** | **unknown** | Unverified |
| Terminal control T10 | **unknown** | **unknown** | **unknown** | Unverified |

The absence is not interpreted as absence of functionality. A future accepted-contract artifact that enumerates the ten controls should replace these placeholders; until then, any named mapping would be speculative.

Cross-cutting contracts *can* nevertheless be stated from the brief: a terminal may attach/detach without owning the actor lifetime; a slow or absent view must not block canonical Stop, append, or recovery; local and remote presentations must project the same canonical actor/event semantics; and transport identity cannot replace actor/principal identity. fileciteturn0file0

### Stop mode matrix

The three Stop modes *are* defined in the supplied packet, so they can be made testable without reopening them. fileciteturn0file0

| Mode | Accepted scope/boundary | Observable contract | Decisive negative trace | Residual ambiguity |
|---|---|---|---|---|
| **Aggressive** | Selected agent; interrupt without waiting for its current operation to reach its normal boundary | Stop request is canonically appended; selected actor receives forceful interruption for the captured stop epoch; it starts no new operation afterward | A new operation/effect is initiated by the selected actor after interruption was effective, or the implementation deliberately waits for the current operation's normal boundary | An external effect already dispatched before interruption may be `unknown` |
| **Full** | Selected agent plus its subagents, shells, and monitors | A captured descendant/process set is stopped as one scoped control action, with individual settlement or explicit unknown for every member | Any in-scope descendant continues initiating new work after Full Stop is settled, or disappears from settlement accounting | Already-dispatched external effects can remain `unknown`; newly discovered descendants need epoch rules |
| **Lazy** | Wait until an observable current-operation boundary, then stop | The boundary being awaited is named; once its receipt occurs, no next operation starts | Stop claims completion before the named boundary, or a new operation begins after that boundary | The current operation can itself complete an effect before the boundary |

For all modes, **Stop completion must not be inferred from loss of UI activity**. It requires canonical actor/process settlement. Conversely, the inability to determine whether a pre-interruption external request committed must be displayed as `effect outcome unknown`, not converted into success or failure. These are proposals needed to satisfy the brief's truthfulness rule. fileciteturn0file0

A useful invariant is to assign each Stop a `stop_epoch`. Work admitted before the epoch can settle afterward and be labeled accordingly; work first admitted after an effective stop boundary is a violation. This avoids falsely classifying a delayed completion message from pre-stop work as newly authorized work.

### Preserved forks and three distinct forms of branching

A conversation fork, a Git worktree, and a filesystem snapshot are demonstrably different public primitives.

OpenAI's WebSocket documentation describes a conversation fork as a new response stream branching from a prior response ID while the original stream can continue independently. citeturn14view8 Git 2.56.0 documents worktrees as multiple working trees attached to one repository, with a new worktree checking out a commit-ish while sharing repository data other than per-worktree state such as `HEAD` and the index. citeturn15view0 OpenZFS describes a snapshot as an atomic, read-only point-in-time copy of a filesystem or volume. citeturn16view0

Therefore Recursion should never collapse these operations into one “fork” flag:

| Operation | What branches | What it does **not** imply |
|---|---|---|
| Conversation fork | Logical conversation/event lineage | No worktree, filesystem copy, process copy, or extra authority |
| Worktree creation | Version-control working tree / checkout context | No conversation branch, full-filesystem snapshot, or allowance duplication |
| Filesystem snapshot | Storage state at a point in time | No new conversation, actor lease, GoalSpec, or VCS branch |

A **preserved work fork** needs a binding record across those layers where they are present:

`fork_id → parent conversation revision + child conversation revision + parent task/goal version + child task identity + worktree identity if any + snapshot identity if any + actor/lease generations + parent reservation + derived reservation`.

The reservation requirement is crucial: the parent allowance must be partitioned or otherwise reserved, **not copied**. This follows the accepted DS-32 rule that the original unfinished work remains untouched, the derivative stays separate, and the parent allowance is not duplicated. fileciteturn0file0

A preserved fork passes only if all three tests hold:

| Test | Pass evidence | Decisive failure |
|---|---|---|
| Parent preservation | Parent's pre-fork conversation/work identity and unfinished state remain unchanged | Fork operation rewrites/supersedes parent |
| Child separation | Child has a distinct lineage/task/work binding | Both branches silently address the same mutable continuation |
| Allowance conservation | `parent remaining + child reservation + settled spend` obey the defined conservation rule | Parent and child can independently consume the same pre-fork allowance |

This proposal does not choose Git, ZFS, any filesystem, any process model, or any specific storage implementation.

## Consultation envelope and authority separation

### Proposed envelope

The consultation envelope should be canonical data, not a transport message whose meaning depends on whichever client happened to deliver it.

| Group | Proposed fields |
|---|---|
| Consultation identity | `consultation_id`, request revision, parent consultation if nested |
| Causality | `request_event_id`, `causation_id`, `correlation_id` |
| Requester | Logical actor identity, current lease ID/generation, role |
| Recipient | Logical actor identity, expected/accepted lease ID/generation, role |
| Goal binding | Goal ID and GoalSpec version |
| Task binding | Task ID and task revision/version |
| Context grant | Explicit permitted context references and immutable revisions/digests |
| Evidence grant | Permitted evidence references/revisions and disclosure class |
| Expected answer | Response schema/version and answer constraints |
| Time | Requested-at, expiry/deadline |
| Recursion limits | Remaining consultation depth, cycle bound, visited-chain/cycle identity |
| Routing | Route/session/node as operational metadata, never as authority |
| Reservation | Parent reservation/allowance identity and amount/category as applicable |
| Authority class | `advice_only`, or specifically delegated proposal/adoption capability—never inferred from role name |
| Provenance | Actual principal/system that generated each subsequent receipt |

The accepted DS-32 direction already requires request/causation/correlation, logical identities and leases, goal/task version, permitted context/evidence revisions, response schema, expiry, depth/cycle bound, route/session/node, and parent reservation; the table above makes those requirements directly serializable without prescribing protocol or database layout. fileciteturn0file0

### Separate receipts and lifetimes

The consultation should not have a single overloaded `"status"` that confuses transport progress with authority.

```text
Request lifetime:
REQUESTED ──> ACCEPTED
          └─> REJECTED

Delivery lifetime:
ACCEPTED ──> DELIVERED
         └─> DELIVERY_BLOCKED

Answer lifetime:
DELIVERED ──> ANSWERED
          ├─> DECLINED
          └─> BLOCKED

Adoption lifetime:
ANSWERED ──> ADOPTED
         ├─> EXPIRED
         ├─> STALE
         └─> INELIGIBLE

Effect settlement:
ADOPTED ──> APPLIED
        ├─> FAILED
        ├─> UNKNOWN
        └─> RECONCILED
```

The key rule is that each arrow produces a separate attributable receipt. **Delivered does not mean answered; answered does not mean adopted; adopted does not mean applied.** This directly implements the accepted DS-32 advice/adoption distinction. fileciteturn0file0

At adoption time—not only at request or answer time—the system should re-check:

`authorized adopter principal + current lease/generation + GoalSpec version + task version + answer revision + expiry + delegated scope`.

A delayed answer from a former lease holder can therefore remain permanently useful evidence while being `INELIGIBLE_FOR_ADOPTION(current_lease_changed)`. Kubernetes's lease model demonstrates why holder identity, renewal/expiry, and concurrency version matter when authority can move between actors. citeturn16view1

### Advice is not handoff, and a reply is not authority

OpenAI's public multi-agent documentation provides a useful contrast. In an “agents as tools” pattern, a manager remains in control and calls specialists for bounded help; with a handoff, the specialist becomes the active agent for the rest of the turn. citeturn14view6 Neither primitive by itself expresses DS-32's stronger requirement that advice can be delivered and retained while its later authoritative adoption is independently decided by the then-current lease holder.

Within the reviewed primary documentation, I did **not** find an agent framework exposing the exact Recursion combination of:

`separate delivery receipt + answer receipt + lease-qualified adoption receipt + independent effect settlement`.

That is an **inference about the reviewed source set, not a claim of exhaustive absence across all multi-agent systems**. OpenAI supplies useful manager-versus-handoff semantics; Kubernetes supplies explicit lease/version semantics; Recursion's desired advice/adoption split therefore remains a product-specific canonical contract rather than something that can safely be inherited wholesale from either. citeturn14view6turn16view1

### Direct Owner-to-ARM events

A direct Owner-to-ARM instruction should append a canonical event with:

`actual Owner principal → addressed ARM identity/lease → current GoalSpec/task version → instruction content/revision → explicit existing authority scope`.

Its acceptance must fail if satisfying the instruction would require silently creating an unrelated goal or widening privacy, spending, credential, publication, or deployment authority. The Head learns about the instruction through canonical event projection rather than being fabricated as the sender or mandatory relay. These constraints come directly from the accepted DS-32 Owner-to-ARM model. fileciteturn0file0

An Owner message still does not automatically mean “amend GoalSpec.” Under the brief's recorded OR-037 constraint, actual GoalSpec amendment remains Owner-only and must remain distinguishable from ordinary instructions issued under an existing goal. OR-038 and OR-039 are likewise preserved rather than reopened. fileciteturn0file0

## Accessibility, comprehension, and truthful activity views

### Accessibility must be measured separately from responsiveness

WAI-ARIA defines a `log` as a live region whose items occur in meaningful order, with chat/messaging histories as examples, while a `status` region contains advisory information and should not gain focus merely because its content changes; `status` has implicit polite announcement behavior. `alert` is assertive and intended for important, time-sensitive information. citeturn14view7turn16view2 WCAG 2.2 separately requires meaningful keyboard focus order and a visible keyboard focus indicator. citeturn15view3turn15view4

Those standards support the following **testable Recursion requirements**, rather than a claim that the future interface is already accessible:

| Dimension | Required outcome | Test |
|---|---|---|
| **Comprehension** | A user can correctly identify who requested, who answered, who adopted, which action is merely queued, and whether an effect is settled or unknown | Task-based comprehension test over synthetic transcripts; predeclare acceptance threshold |
| **Keyboard accessibility** | Every interactive owner control is reachable and operable in a meaningful focus order | Keyboard-only fixture; no mouse/pointer dependency |
| **Focus visibility** | Current keyboard target is perceptible | Automated/manual focus-indicator test under supported themes |
| **Screen-reader ordering** | Conversation/activity entries are announced in canonical meaningful order without routine updates constantly interrupting the user | Screen-reader transcript fixture using log/status semantics on graphical/web surfaces |
| **Plain-text parity** | State, authority, warnings, and controls do not depend on icon, animation, layout, or color | Strip formatting; compare semantic content and available commands |
| **Input stability** | Asynchronous output never deletes typed text, moves the insertion point unexpectedly, or steals focus for routine status updates | Continuous-output fixture while the user edits a partially entered command |
| **Rendering cost** | Presentation overhead is measured independently from engine/control latency | Measure render CPU/work, event volume/bytes, update frequency and input-echo latency separately |
| **Control responsiveness** | Slow rendering does not delay canonical Stop/PAUSE/control append | Artificially stall the view and verify canonical control timing independently |

The choice of a numerical comprehension threshold, supported assistive-technology matrix, and performance budget remains a product decision; fabricating those numbers here would be unsupported.

### Truthful activity model

The owner-facing view should expose four separately labeled dimensions:

**Engine activity** — observable model/tool/worker/process activity.  
**Canonical state** — authoritative requested/accepted/rejected/adopted/stopped/effect-settlement state.  
**Evidence visibility** — whether provider reasoning or intermediate state was actually returned, unavailable, opaque, or not requested.  
**Transport/view state** — connected, delayed, reconnecting, revoked/unavailable, and the age/cursor of the displayed projection.

DS-32 already requires engine activity to remain distinct from canonical acceptance, provider reasoning to be shown only where actually returned, opaque state and counters to be labeled honestly, and hidden reasoning never to be reconstructed. fileciteturn0file0

Accordingly, a view may truthfully say:

`Tool call running — canonical effect outcome pending`

or

`Approval recorded from automated reviewer — no human approval recorded`

or

`Stop requested — external effect outcome unknown`

but it must not collapse these into `Approved`, `Done`, or `Owner confirmed` without the corresponding canonical evidence.

### Synthetic fixtures required before acceptance

| Fixture | Required evidence | Failing trace |
|---|---|---|
| **Stale steer** | Typed stale-turn/version conflict; no application event | Old steer changes replacement/current turn |
| **In-flight preserved fork** | Parent remains byte/logically unchanged; child receives separate lineage and non-duplicated reservation | Fork mutates parent or doubles allowance |
| **Interrupted question** | Same open question/waiter restored after restart | Replacement question consumes old reply |
| **Duplicate message** | One semantic application; duplicate projection harmless | Same answer/approval/effect applied twice |
| **Out-of-order messages** | Canonical sequence/version resolves order or exposes a gap | Arrival order silently rewrites authority/state |
| **Transport restart** | Canonical state survives; projection resumes from cursor with dedupe | Transport loss resets actor/task state |
| **PAUSE race** | Canonical PAUSE append is independent of view latency | Presentation throttle postpones PAUSE |
| **Revocation race** | Revoked surface becomes unavailable while canonical actor/event state remains valid | Transport revocation changes actor identity or fabricates cancellation |
| **Approval replay** | Second submission reports consumed/replay conflict | Same stored approval resumes twice |
| **Approval retarget** | Changed target/arguments rejected | Old approval authorizes altered action |
| **Lease turnover before adoption** | Answer retained as evidence; adoption rejected as stale/ineligible | Former lease's answer silently becomes authoritative |
| **Aggressive Stop during external effect** | Actor stops; effect is explicitly settled or `unknown` | UI labels effect failed merely because actor stopped |

These are acceptance fixtures, not reports of completed empirical tests. No live trial was authorized or performed.

## Source-pinned findings, recommendation, and unresolved questions

### Source-pinned claim table

| Consequential claim | Primary source, version/date | Classification | Confidence | Expiry or decisive falsifier |
|---|---|---|---|---|
| Programmatic approval callbacks can make a decision without waiting for a human, so an “approval” record needs reviewer provenance | OpenAI Agents SDK, HITL docs; current docs accessed 2026-10-01 citeturn13view0 | Fact — source-documented | High | Falsified if SDK contract removes programmatic approval or guarantees authenticated human provenance |
| Safe long-running approval handling requires trusted/server-owned state, authenticated and authorized reviewers, validation against pending requests, and replay-safe consumption | OpenAI Agents SDK, HITL docs; accessed 2026-10-01 citeturn13view0 | Fact — source-documented | High | Re-check on substantive SDK HITL contract change |
| Sandbox/resource containment and approval/reviewer policy are separable controls; automated review does not itself alter the sandbox boundary | OpenAI Codex sandbox documentation; accessed 2026-10-01 citeturn14view0 | Fact — source-documented | High | Re-check when sandbox/approval architecture changes |
| Anthropic's `PreToolUse` carries tool name/input and a unique tool-use identity before execution in that harness | Claude Agent SDK Python reference; accessed 2026-10-01 citeturn14view1 | Fact — source-documented | High | SDK hook contract changes |
| Kubernetes admission-webhook side effects require reconciliation because webhook invocation does not prove the admitted object was persisted | Kubernetes v1.36 dynamic admission docs citeturn14view2 | Fact — source-documented | High | Re-check on admission API semantic change |
| Steering acceptance can mean “queued/owned” rather than “applied”; OpenAI documents the successor response creation as commit point | OpenAI Responses API reference; accessed 2026-10-01 citeturn14view3 | Fact — source-documented | High | Steering protocol changes |
| Durable event-history replay can restore workflow state following worker failure without simply rerunning prior workflow operations | Temporal Tasks documentation; accessed 2026-10-01 citeturn14view4 | Fact — source-documented | High | Temporal execution model changes |
| Lease-holder identity, renewal/expiry and concurrency versioning are established primitives for preventing concurrent authority acquisition | Kubernetes Lease/coordinated leader-election docs; current page last modified 2026-08-05 citeturn14view5turn16view1 | Fact — source-documented | High | Lease API/election semantics change |
| Manager-as-tool keeps manager control; handoff makes a specialist active | OpenAI Agents SDK orchestration docs; accessed 2026-10-01 citeturn14view6 | Fact — source-documented | High | Agent orchestration contract changes |
| A conversation fork, Git worktree, and filesystem snapshot represent three different kinds of branching | OpenAI WebSocket docs; Git worktree 2.56.0 dated 2026-09-28; OpenZFS snapshot docs citeturn14view8turn15view0turn16view0 | Fact — source-documented | High | Falsified only if Recursion deliberately defines a higher-level operation that creates all three; underlying primitives remain distinct |
| ARIA `log`, `status`, and `alert` carry different ordering/announcement semantics; routine status changes should not steal focus | WAI-ARIA 1.2; WCAG 2.2 supporting guidance citeturn14view7turn16view2turn15view3turn15view4 | Fact — source-documented | High | Re-evaluate against later Recommendation adopted by supported clients |
| The reviewed agent frameworks do not expose the complete DS-32 delivery→answer→lease-qualified-adoption→effect-settlement contract | Reviewed OpenAI orchestration/HITL and Kubernetes lease docs citeturn13view0turn14view6turn16view1 | Inference | Medium | Falsified immediately by primary documentation for a system exposing the complete semantics |
| The supplied DS-32 packet invokes ten accepted terminal controls but does not enumerate them | Supplied DS-32 handoff, last updated 2026-09-30 fileciteturn0file0 | Fact — locally/document observed | High | Falsified by an authoritative accepted-contract artifact enumerating them |
| Approval and effect settlement should remain separate canonical receipts | OpenAI replay/reconciliation guidance; Kubernetes side-effect warning; DS-32 accepted semantics citeturn13view0turn14view2 fileciteturn0file0 | Proposal | High | Falsified if every supported effecting resource provides atomic authorization+effect+durable outcome under the same transaction |
| Recursion should make the effecting-resource mediator, rather than a harness hook, the decisive authorization boundary | Same evidence plus Codex sandbox/approval separation citeturn14view0turn14view1turn14view2 | Proposal | Medium-high | See recommendation falsifier below |

### Recommendation

**Recommendation:** adopt a **resource-enforced, exact-action pre-effect mediation contract** as the canonical authorization boundary. Upstream permission prompts, automatic reviewers, approval callbacks, `PreToolUse`-style hooks, model guardrails, and transport confirmations may all supply useful evidence or early denial, but none should independently create a Recursion authorization receipt unless the Recursion adapter can bind that decision to the exact effect request and current authority state. This preserves the brief's provider neutrality while importing useful upstream primitives without confusing them with Recursion grants. citeturn13view0turn14view0turn14view1 fileciteturn0file0

The **competing option** is a harness-centric design: treat the agent framework's always-invoked pre-tool hook or approval callback as the definitive gate and trust the subsequent tool/runtime path to perform exactly the approved operation.

The recommendation is **decisively falsified** if the harness-centric option can demonstrate, for **every supported effecting adapter/resource**, all of the following under fault injection:

1. the resource is unreachable by any path that bypasses the hook;
2. approved target and arguments are immutably bound through effect;
3. lease/grant/task changes between decision and effect are revalidated;
4. approval replay cannot trigger a second execution;
5. an automated/host reviewer can never be mislabeled as the Owner;
6. crash, reconnect, Stop, and retry cannot turn an uncertain effect into a duplicate;
7. an authoritative resource receipt supplies equivalent effect settlement;
8. the resulting guarantees are equivalent while the additional Recursion mediation layer adds no independent safety or audit property.

If those conditions are met, a separate mediation layer would be redundant rather than safer.

What the recommendation **does not prove** is equally important. It does not prove exactly-once behavior for external services; it does not select a database, transaction protocol, IPC mechanism, language, topology, transport, operating-system sandbox, Git strategy, or filesystem; it does not establish the ten omitted terminal-control definitions; and it does not constitute implementation acceptance. No live system was tested.

### Remaining empirical unknowns

The following remain genuinely empirical or unspecified rather than failed requirements:

| Unknown | Why unresolved |
|---|---|
| Names and semantics of the ten accepted terminal controls | Not present in the self-contained DS-32 handoff |
| Exact interrupt boundary for each adapter under Aggressive Stop | Depends on actual adapter/resource behavior; no live trial authorized |
| Exact “observable current-operation boundary” for Lazy Stop | Must be defined per operation class before implementation can be tested |
| Which effecting resources can return durable idempotency/effect receipts | Adapter-specific and not selected in this lane |
| External-service behavior after cancellation/disconnect | Provider/resource specific; cannot be inferred from local cancellation |
| Remote transport ordering/retry/rate-limit behavior | No transport is to be selected or called in this research lane |
| Screen-reader behavior across the eventual supported terminal/browser matrix | Requires empirical accessibility testing |
| Input/rendering performance budgets | No hardware, workload, or acceptance threshold supplied |
| Full set of non-coalescible canonical event classes | PAUSE/control invariants are accepted, but exhaustive taxonomy is not supplied |
| Reservation accounting unit for preserved forks | Brief says allowance must not duplicate but does not define all allowance categories |

### Open Owner questions

These questions record specification choices; they do not request reopening OR-037, OR-038, OR-039 or the accepted interaction boundary.

| Owner decision/input needed | Why it matters |
|---|---|
| What are the authoritative names and existing semantics of the ten terminal controls? | Required to replace T1–T10 `unknown` rows with genuine control contracts |
| What constitutes the Lazy Stop boundary for each major operation class, and may Lazy escalate after a bounded wait? | Without this, “wait for the current operation” is not a falsifiable completion rule |
| Which concrete grants may an ARM's current lease holder adopt routinely under existing OR-037 delegation, versus which always require an Owner action? | Needed to validate consultation adoption without changing OR-037 |
| What are the categories and conservation rule of “parent allowance” for a preserved fork? | Needed to prove allowance non-duplication across child work |
| Which canonical event classes, beyond Stop/PAUSE and authority/effect transitions, are forbidden from presentation coalescing? | Needed for deterministic remote projection tests |
| Which uncertainty states require immediate Owner notification rather than passive visibility? | Needed to distinguish advisory status from time-critical alerting without inventing policy |
| What minimum accessibility/browser/terminal assistive-technology matrix is an acceptance target? | Needed to turn standards-derived requirements into an executable acceptance suite |

The report's privacy/authority scan is clean with respect to the supplied research constraints: the analysis uses the public/synthetic DS-32 brief and public primary documentation; it performs no implementation, repository edit, provider/model call, authentication/configuration change, spending, deployment, publication, merge, Telegram operation, or live trial; and no proposal above is promoted into an Owner decision. fileciteturn0file0
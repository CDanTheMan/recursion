---
title: DS15 ARM conversations and multi agent rooms
source-prompt: DS-15 — ARM conversations and multi-agent rooms
session: Codex alternative route (same self-contained handoff; Deep Research plan-only)
retrieved: 2026-10-01
status: research-evidence-not-a-decision
verification: not independently verified by Recursion; no rerun
---

DS15 ARM conversations and multi agent rooms

Research findings and candidate evaluation contract for Recursion v3

Prepared for Lucas and Hermes | Evidence reviewed 1 October 2026

Executive conclusion

Direct Owner-to-ARM conversation, dedicated ARM topics and shared rooms can be described coherently without creating another portfolio executive. The necessary separation is between a durable logical actor, the surface used to address it, and its current authority. A room coordinates a workflow; it does not acquire goals, membership powers or a pooled budget. A named ARM may coordinate a bounded step under the already accepted lease. Head retains the responsibilities specified in the brief. These are consistency conclusions and proposed acceptance conditions, not observations of a working Recursion system. [B0; I1; P1]

The exact Grok Bot reference is verified at the official xAI documentation URLs in Section 2. It supports persistent named conversations, parallel work, explicit addressing and visible asynchronous collaboration. Its shared-computer pattern cannot establish isolation for Recursion. Published interaction descriptions do not establish safe authority transfer, fencing, or exactly-once effects. [G1–G5; I2]

Telegram remains an optional projection of canonical state. Two findings materially refine the brief: current official documentation includes topic-enabled private bot chats and conditional bot-to-bot communication, while an older FAQ still contains a blanket bot-to-bot restriction. The report uses the dated API and feature rules, records the conflict, and makes no claim of universal delivery. Current limits are observations of documentation retrieved on 1 October 2026, not service guarantees. [B0; T2–T4]

The most consequential safety finding is that a lease record, expiry time and fencing-token field are insufficient on their own. A paused holder must be rejected where a protected commitment is accepted. Revocation without a successor needs an effective revocation barrier or current-authority check; a resource that merely remembers the highest token already seen can otherwise keep accepting an old holder. Already dispatched effects can remain uncertain. None of these uncertainties may be reported as successful cancellation or zero cost. [A12–A14; I3; P3]

The research recommendation is R1: evaluate a transport-independent actor and authority contract, including bounded coordination leases, against named competitor R0: Head-mediated approval of each protected workflow commitment. Both retain direct Owner-to-ARM conversation, bounded coordination leases and the fixed CLI/optional-Telegram boundary. R1 is a candidate for evaluation, not a topology, protocol or product-default decision. Its decisive safety falsifier is an independently reproduced trace in which route remapping grants reserved Head authority, or a stale lease produces a fresh protected commitment after the declared effective revocation barrier. Its benefit claim fails if a matched evaluation shows no meaningful reduction in Owner coordination effort, or unacceptable increases in context loss, contradictions or unreviewed work. [P1–P7]

No located study directly establishes the requested Recursion benefit. Relevant human-agent studies are useful for selecting measurements and stress cases, but their short tasks, interfaces and simulated failures do not establish that this interaction contract reduces Lucas's workload. The synthetic fixtures in this report are proposed and have not been executed. A complete research report is therefore possible; implementation acceptance and the empirical answer to Q12 remain open. [H1–H5; U1]

1 Scope evidence and accepted boundaries

This report answers the 13 questions in the supplied DS15 brief, last updated 30 September 2026. The supplied Recursion context is treated as an accepted research constraint, not as independently verified runtime behavior. Ordinary public-source web research, primary papers and synthetic examples are the evidence base. No Deep Research plugin session is claimed. No private repository, private transcript, account configuration or operational Recursion instance was inspected. No runtime, provider, authentication, spending, deployment, publication or merge action is proposed for execution by this report. [B0]

The accepted interaction boundary is closed: interactive detachable CLI is the canonical local surface; Telegram is optional; no graphical frontend is required for v3; direct Owner-to-ARM conversation and bounded coordination leases are accepted. Lucas is final Owner, Hermes is the executive control plane, and an implementer's own PASS is not acceptance. The operative constitution is not amended here. Questions about concrete values and acceptance criteria below do not reopen those decisions. [B0]

Evidence labels and confidence

F means fact about an explicitly cited source's published statement. I means inference or synthesis. U means unverified. P marks a proposal in addition to its inferential status; a proposal is not a measured fact or accepted Owner decision. B0 denotes supplied requirements. L denotes local observation only of the delivered artifact checks, never system performance. These labels preserve the brief's distinction among source-documented, locally observed, inferred and unverified claims.

High confidence means the bounded source statement or logical distinction is clear. Moderate means a transfer, tradeoff or extrapolation depends on context. Unverified means the needed observation was not established; it is not a probability of zero. An expiry trigger identifies when to revisit the claim. A retrieval-date pin is not an immutable snapshot. Sources with versioned URLs are identified; rolling documentation is dated and requires revalidation against any eventual selected release or deployment.

All consequential public-source claims are linked through source IDs to Section 14. The claim register in Section 13 distinguishes published behavior, interpretation, proposed controls and missing evidence. Normative API text establishes a contract to check, not proof that any particular endpoint conforms. A route listing, method name, generated model response or agreement among agents is not support evidence.

Question coverage

Question

Answer location

Evidence status

Q1 Exact official Grok reference

Section 2

Verified official URLs and retrieval dates

Q2 Usable Grok patterns

Sections 2 and 11

Published patterns plus bounded adaptation proposals

Q3 Durable actors and surfaces

Section 3

Accepted roles plus explicit proposed mapping

Q4 One bot per ARM or hybrid

Section 3

Comparative inference; no default selected

Q5 Telegram constraints

Section 7

Dated primary documentation; configured behavior untested

Q6 Addressing versus authority

Section 4

Proposed contract; enforcement untested

Q7 Conflicts cycles and budgets

Section 5

Proposed deterministic obligations and escalation

Q8 Lease and retained Head powers

Section 6

Accepted scope plus enforcement analysis

Q9 Immediate events and digests

Section 8

Proposed canonical observability contract

Q10 Normalization and recovery

Section 7

Documented transport facts plus recovery proposals

Q11 Public systems and limits

Section 9

Versioned or date-pinned primary documentation

Q12 Measured coordination benefit

Section 10

Direct evidence missing; analogous studies and evaluation criteria

Q13 Minimum synthetic fixtures

Section 12

Proposed bounded tests; no executed passes

2 Official Grok evidence and usable patterns

Q1 The exact reference is verified

The reference is Grok Bot, documented on docs.x.ai. It is not inferred from another company's assistant product. The following pages were retrieved on 1 October 2026 before their patterns were used. The dates below are visible page updates, not independent observations of deployment dates. The URLs are direct official source pins. [G1–G5]

Source

Official page

Visible update

G1

Grok Bot overview

21 September 2026

G2

Create and manage Bots

29 September 2026

G3

Message and collaborate

21 September 2026

G4

Frequently asked questions

29 September 2026

G5

Approvals security and privacy

28 September 2026

Grok's overview describes persistent named Bots that retain context, work in parallel, communicate and share group context. The role-management page gives each Bot a name, job, conversation and working context, suggests separation by goals or approval boundaries, and cautions that memory is not current-source authority. A coordinator appears as an example, not a mandatory Chief-of-Staff tier. [G1, G2]

The collaboration page describes groups of two to six Bots, explicit mentions of one or several participants, asynchronous wake-and-reply handoffs, and visible handoff progress. It advises one owner per stage and warns about duplication and noise from excessive parallel handoffs. Stopping does not undo completed actions; reactions are not a safety-critical decision channel. These are product interaction descriptions, not formal authority or consistency guarantees. [G3]

The personal-Bot FAQ explicitly says the roster shares a user-assigned computer, files, sessions and logins, and that separate Bots are not a security boundary. The security page describes shared exposure of browser and command-line credentials, advises least privilege and action-specific approvals, and presents model-based review as complementary to those controls. This is unusually direct negative evidence against importing ambient shared credentials as if separate chat identities supplied isolation. [G4, G5]

The pages do not provide the DS15 lease, GoalSpec, resource-fence, cross-goal budget or independent-acceptance contract. That is a statement about the reviewed documentation, not proof the product lacks all such internal controls. This report makes no empirical claim about Grok reliability, security incidents or coordination savings. [I2]

Q2 What survives a stricter authority boundary

Persistent named conversations, explicit addressing, result-linked replies, parallel bounded work and visible handoffs remain usable interaction ideas. The adaptation is to bind all of them to an existing logical actor and current GoalSpec. A stage handoff becomes an attributable request or an authorized change in step coordination; it does not transfer unspecified ownership. A shared room displays contributions from authorized participants; being readable or addressable there grants nothing. [B0; P1]

There is no need to import a new executive tier to obtain those interaction benefits. A speaker selector can schedule a turn. A summarizer can compose evidence. A named ARM with a valid lease can request a bounded contribution. None of those functions needs power to admit actors, change goals, move cross-goal budgets, control ARM lifecycle or choose strategic escalation. The substantive powers, rather than the label supervisor, determine whether a second executive has appeared. [I1; P3]

Three rejected imports are important. First, shared ambient credentials are outside the usable pattern: surface sharing does not justify capability sharing. Second, the visible transcript cannot settle conflicting authority. Third, unconstrained ownership passing cannot stand in for the accepted expiring, nontransferable step lease. These exclusions follow the brief; they are not newly requested product choices. [B0]

The competing interaction pattern is explicit Head-mediated protected commitments with direct ARM dialogue retained. It can preserve clarity with fewer delegated effect decisions, at a possible waiting and coordination cost that remains unmeasured. Free-form ownership transfer and a separate AI ARM Manager are rejected boundary violations, not eligible product alternatives. The usable-pattern hypothesis is falsified if it cannot preserve attribution and useful direct conversation without acquiring any reserved Head power. [P1; R0]

3 Durable actors surfaces and topology choices

Q3 A surface is not an actor

The proposed mapping distinguishes logical actor identity; GoalSpec and revision; canonical work and decision state; room and membership revision; route binding; execution attempt; and transport credential generation. They may be related, but they cannot safely be synonyms. A process restart is not the birth of an executive, and a topic deletion is not its death. These are report-level meanings to test against the accepted brief. [B0; P1]

Element

Durable meaning

Surface relationship

Head

Retained portfolio control plane under Owner authority

Conceptually reached through general conversation; the display name is replaceable

ARM

Goal-scoped delegated executive with its own attributable history

Dedicated conversation plus authorized participation in shared rooms

Worker

Bounded executor for an assignment

May contribute under its own attribution or through a clearly identified result; no room-derived authority

Verifier

Independently assigned reviewer with bounded evidence access

Finding can be displayed in any authorized surface; display does not make it acceptance

Persistent assistant

Persistence and lifecycle property of an actor

Does not introduce a rank or executive tier

Shared room

Collaboration context and membership view

Multiple actors and GoalSpecs may be visible; the room owns no goals or pooled budget

Route or process

Delivery and execution mechanism

Replaceable without transferring actor identity or reviving revoked grants

The Head route need not use Telegram's built-in General topic. Recursion's general label is conceptual. Likewise, an ARM can remain the same logical executive across CLI and a Telegram conversation. Creating another topic should not create another ARM; creating an ARM should not depend on a transport succeeding. The actor lifecycle and its display projection need separate attributable events. [B0; P1]

A dedicated ARM conversation may be the default target for unqualified messages only when an authenticated, versioned binding makes that target unambiguous. A shared room has no safe last-speaker default for a consequential command. Every visible message identifies the speaking logical actor, selected route and GoalSpec as the brief requires. Commands, receipts, replies, group posts and digests need this attribution; a no-goal or multiple-goal context must be explicit rather than guessed. A useful optional refinement is to display command or work references and review state when ambiguity would otherwise be costly. That refinement is a proposal, not a prescribed wire format. [B0; P2]

Q4 Three eligible transport topologies

All three options below can satisfy or violate the authority contract. Bot count is not a security proof. A token permits control of a transport bot and authenticates that bot, not the human Owner or a Recursion ARM. Therefore a per-ARM token narrows only that credential's transport scope unless backend privileges, storage access and execution boundaries are also separated. [T3, T5; I4]

Topology

Potential advantage

Principal risk and operating cost

T-A One bot with logical actor routing

Few transport credentials and receiver paths; consistent discovery; canonical attribution can remain uniform

One compromised or failed transport capability can affect many conversations; visual identity must disambiguate actors; routing mistakes have broad reach

T-B One bot per ARM

Distinct visible identity; revocation of one bot can contain that route; per-ARM delivery settings are easier to explain

More credential and receiver lifecycles; roster churn and ambiguous multi-bot replies; shared backend access can erase apparent isolation

T-C Hybrid

Selective separation where a justified exposure boundary exists; shared discovery or Head surface can remain simple

Two routing modes and duplicated recovery cases; users may overestimate which actors are isolated; a common gateway can remain a common failure point

T-A does not require one unpartitioned execution context. T-B does not guarantee one protected context per bot. T-C is not automatically the safe compromise: if selective separation has no explicit threat model, it merely adds complexity. The relevant comparison is what an adversary controlling one route can read, impersonate, trigger and block; what survives its removal; and how much effort the Owner spends locating and correctly addressing work. [I4]

These tradeoffs are hypotheses. Under otherwise identical canonical authority rules, compare credential exposure scope, authorized data reach, wrong-actor commands, route-recovery success, delayed critical notices, operational burden and Owner effort. Do not rank options by an invented weighted score before Lucas supplies the relative costs or by counting bots as if they were isolation units. [P7]

Explicit competitors and rejection tests

For T-A, the named competitor is T-B. T-A's isolation claim is rejected if controlling its single transport route exposes an unacceptable set of goals under the agreed threat model, or if required attribution cannot prevent wrong-actor actions while T-B can. T-A's simplicity advantage is unverified until the same roster and failure traces are evaluated.

For T-B, the named competitor is T-A. T-B's containment claim is rejected if compromising one bot still reaches every ARM's capabilities through a shared backend, or if necessary cross-room collaboration cannot work within published transport visibility rules and the canonical collaboration path. T-B's usability claim is rejected if roster and routing effort outweigh its identity advantage at the predeclared threshold.

For T-C, the named competitor is T-A with the same backend capability boundaries. T-C's incremental value is rejected if no required threat boundary improves, or if mixed-mode binding, recovery or explanation errors introduce unsafe transitions. A common authentication or routing component remains in the threat model rather than disappearing behind separate icons.

None of these comparisons selects a default or authorizes creation, configuration or credential changes. Any eventual topology must pass the same authority and recovery fixtures. [P1; P7]

4 Addressing attribution and authority

Q6 The admission question

An address answers who should receive a message. Authority answers who may cause which protected transition, on which resource, under which current goal and grant. The proposed admission contract asks both questions independently. A topic, mention, reply, bot username, room title or human-readable role label can supply routing evidence; it cannot substitute for an authenticated principal and current authority. [B0; P2]

RFC 9396 provides a useful standards analogue: fine-grained authorization details can describe actions and resources, but their semantics and comparison rules are API-specific. It does not supply Recursion's permission algebra. CloudEvents similarly provides an event-identity convention in which source plus id identifies a distinct event and can identify a retransmission; it does not grant authority to the payload. These sources support explicit distinctions, not selection of either protocol. [E1, E2]

The proposed command record needs enough evidence to reconstruct an admission decision: stable command and intended-operation identity; authenticated issuer; target actor; selected route and binding revision; room and membership revision when relevant; GoalSpec identity and revision; requested action and affected resource; causation or supersession references; current grant and lease references; explicit goal-owned budget attribution; and disposition. Exact syntax, storage and transport encoding remain outside this report. [P2]

A protected commitment is the point at which the system accepts an action whose consequences require authority, such as spending an allowance, disclosing information, changing membership or directing an external effect. Read access is itself subject to the relevant information boundary; it is not made harmless by calling it context. The checks for receiving a room message, reading evidence, coordinating a step and committing an effect can differ. A room's participant list cannot be treated as the union of everybody's permissions. [B0; P2, P3]

An attributable direct instruction

Synthetic example: Owner sends an ARM a request to compare two public alternatives already in its GoalSpec. The event names that ARM, GoalSpec revision and route. The ARM can acknowledge and execute only the permitted scope. If the next message requests deployment or private-data disclosure beyond the envelope, the attributable event remains valuable, but the requested expansion must enter the retained Head/Owner authority path. It does not silently widen the ARM's permissions merely because the sender is Owner or the conversation is direct. [B0; P2]

This distinction does not prevent Lucas from changing a decision. It requires such a change to be explicit and recorded through the established authority path, with the new scope and effective revision identifiable. A direct conversational instruction can initiate that path. Treating every message as an implicit constitutional amendment would erase the boundary the brief requires. [I1; P2]

If address resolution is missing, contradictory or ambiguous, preserve the message and request the smallest resolution before execution. Do not silently reroute to Head, the last speaker or the actor whose name most closely matches. A reply can clarify the target without receiving any new authority. A forwarded Owner-looking instruction or a body claiming to be Head is evidence to inspect, not authenticated authorship. [P2]

Separate state labels

Received, authenticated, routed, admitted, started, effect outcome known, independently reviewed and accepted are different states. A delivery receipt proves neither task acceptance nor completion. An ARM's final answer proves neither independent verification nor Owner acceptance. A verifier's disagreement remains visible even when a room reaches a friendly consensus. [B0; P2, P5]

For a model-selected handoff, any natural-language rationale is untrusted input to the same admission boundary. A quoted command from a retrieved document remains source content. The proposed safety property is that no route, message style, speaker selection or handoff can enlarge the effective permission set. This is not a claim of prompt-injection immunity or compromised-account protection; those require separate evidence. [P2]

5 Shared room conflicts cycles and budget ownership

Q7 Classify before ordering

Canonical event order is useful for reproducible bookkeeping. It cannot by itself decide what contradictory instructions mean. The proposed room contract classifies an incoming contribution as an observation, proposal, authorized command, explicit supersession, review finding, or outcome. It then determines whether the proposed transition is compatible with current goal and resource revisions. Transport arrival order, client time and model confidence never choose the semantic winner. [B0; P2, P4]

Two independent permitted research tasks may proceed concurrently. Two commands that consume the same final allowance may conflict even when their text and destination differ. Two contradictory requests against the same artifact revision cannot both become current solely because they arrived through valid routes. Preserve the competing evidence, block the conflicting commitment, and ask Head to resolve within its existing envelope or escalate a reserved Owner decision. [P4]

Explicit supersession is the clearest precedence evidence: a new authorized instruction identifies the old command or revision it replaces. If the earlier effect has already happened, supersession changes future intent; it does not rewrite history or imply rollback. Where a domain has a declared deterministic precedence rule, that rule must be attributable to authority and versioned. A scheduler's ordering convenience is not such a rule. [P2, P4]

Worked simultaneous command trace

Synthetic initial state: ARM A is assigned GoalSpec Alpha revision 4, ARM B is assigned GoalSpec Beta revision 2. Both participate in room R. The room has no pooled budget. Owner tells A in its direct conversation to use alternative X, while a second request in R asks A to use incompatible alternative Y against the same decision revision. Neither refers to the other as a supersession.

The expected trace is two received and attributable commands, a conflict record, and no incompatible protected commitment until resolution. Reversing webhook arrival or visible transcript order leaves that result unchanged. Head may record an in-envelope resolution, or identify that Lucas must choose. A request for clarification belongs to the already authorized actor path; a room supervisor cannot award itself tie-breaking power. If the conflicting work is pure reversible analysis, both alternatives may be evaluated as proposals, but neither becomes the accepted decision by being presented first. [P4; F04]

This test intentionally distinguishes record serialization from authority. The log will have some order. The safety requirement is not an orderless database; it is that the order alone cannot authorize a winner. [I5]

Retry identity is not repeated intent

A retransmission of the same intended-operation identity and payload is one operation. The same identity with a different payload is an integrity conflict. Two separately issued commands with similar wording may mean to repeat an action and cannot safely be collapsed by text similarity alone. Canonical admission deduplication, transport deduplication and side-effect deduplication are separate obligations. [P2, P4]

A crash after an external effect but before acknowledgment leaves an uncertain outcome unless reliable reconciliation evidence establishes it. Retrying because no success message appeared can repeat the effect; refusing all retries can lose work. The proposed state is explicitly unknown, followed by bounded reconciliation within existing authority. No report-level design can manufacture a remote idempotency guarantee that the effect service does not supply. [A09, A11; P4]

Cycles disagreement and liveness

The proposed record of work includes causal lineage and a definition of progress adequate to the workflow step. Repeated A-to-B-to-A delegation, repeated identical critiques or an unresolved dependency should reach a predeclared no-progress, time, turn or allowance bound and become a visible escalation. A bound limits automatic waste; it does not establish task completion or resolve the disagreement. [P4]

Head unavailability must not cause the room to elect an emergency executive with broader powers. Dependent protected work waits or reaches a clearly surfaced blocked state; independent authorized work can continue. A later valid Head decision should permit progress. This is a safety/liveness tradeoff to measure, including starvation and excessive escalation, not a justification for treating unanimity as authority. [P4]

Sequential actor processing can make one state boundary easier to reason about while cyclic requests stall. Permissive interleaving can improve progress while introducing races. Public Orleans and LangGraph documentation make those failure patterns concrete; neither gives a policy tie-breaker for conflicting goals. [A10, A15; I5]

Cross goal accounting

Every accepted reservation or expenditure has one explicit authorized cost owner and the relevant goal-owned slice. A room that serves two goals holds references to a vector of slices, not a common purse. A coordination holder cannot borrow spare allowance, refill a slice, move a debit or refund an uncertain effect by conversational agreement. Cross-goal allocation remains with the retained Head authority, subject to Lucas's envelope. [B0; P4]

Synthetic example: Alpha has 3 allowance units and Beta has 2. Two concurrent Alpha requests each reserve 2. At most one can commit against that available slice; a valid Beta reservation is not a reason to bill the losing Alpha request to Beta. If Alpha's first effect times out with cost unknown, its reservation remains unresolved until reconciled. These are invented units and expected assertions, not measured costs or a spending recommendation. [P4; F10]

The named competitor is R0, under which Head mediates each protected step. R1's shared-room coordination is rejected if it cannot maintain these ownership and conflict properties, or if safe blocking makes useful work materially worse under the agreed evaluation. This does not authorize loosening the fixed authority boundary to improve speed. [P4; P7]

6 Bounded coordination leases and retained Head ownership

Q8 What is already accepted

The brief fixes the lease's room, workflow step, named holder, participating actor IDs, allowed verbs, budget slice, issue/expiry/revocation epochs and fencing token. It excludes adding members, altering GoalSpecs, transferring the lease and settling cross-goal disputes. Head retains overall goal ownership, room membership, authority envelope, conflict resolution, ARM lifecycle and strategic model escalation. The following analysis interprets the enforceability requirements; it does not reopen whether bounded leases exist. [B0]

A coordinator can request a contribution, sequence already authorized work or collect evidence only within the named step and allowed verbs. A lease is not a union of the participants' permissions. The holder's own GoalSpec and each participant's permissions remain ceilings. The supervisor presentation label conveys the current coordination role, not a new actor or a permanent reporting line. [P3]

Decision or action

Retained authority

What a lease holder may do

Goal scope and authority envelope

Head within Owner decisions

Request clarification or amendment; cannot amend

Room membership

Head under applicable access rules

Request a participant; cannot admit one

Workflow step coordination

Named holder within accepted lease

Exercise listed verbs within exact step and current scope

Cross goal conflict or allocation

Head or Lucas where reserved

Surface evidence and options; cannot settle or transfer budget

ARM lifecycle and strategic escalation

Head within Owner envelope

Report a need; cannot promote retire or strategically escalate itself

Review and acceptance

Existing independent review and acceptance authority

Collect findings; cannot turn its own PASS or room consensus into acceptance

Proposed validity contract

The scope binds exact room and step, holder, participant set, membership revision and relevant GoalSpec revisions. Epochs identify grant and revocation generations; the authoritative expiry clock and uncertainty assumptions must be stated separately. A logical epoch is not elapsed time. A paused process's cached opinion that its lease remains valid is insufficient. Unknown current validity permits no fresh protected commitment. [P3]

Renewal and reassignment require a new attributable Head-authorized grant or revision. The holder cannot extend or transfer itself. Rehydration from an old checkpoint cannot revive a revoked incarnation. Expiry does not erase its evidence, budget reservations, attempted operations or outcomes; those remain attributable for reconciliation and review. [P3]

The effect-owning boundary must check the current permitted action, resource and grant generation where the protected commitment becomes accepted. An upstream check followed by an unfenced downstream request leaves a time-of-check/time-of-use gap. A generation field that nobody enforces is annotation. A generic lease service and the resource accepting an effect are different boundaries. [I3; P3]

What fencing evidence establishes

Hazelcast 5.5 describes a holder that resumes after its session expires and uses monotonic tokens to let resources reject older holders. Chubby's original design likewise places sequencer validation at recipients and calls its lock-delay fallback imperfect. etcd 3.6 distinguishes durable serializable key operations from watches that may be delayed, and notes uncertainty after client timeouts. These are concrete coordination lessons, not evidence that Recursion or any selected adapter implements them. [A12–A14]

Proposed safety statement: after the defined effective revocation or expiry barrier, no fresh protected commitment under that grant is accepted. It also remains impossible for a valid lease to authorize a reserved Head verb. This statement deliberately avoids claiming that every in-flight effect can be canceled or that a timeout means no effect. [P3]

There are at least three distinct moments: revocation requested; revocation committed in canonical authority state; and revocation effective at the relevant protected boundary. If a resource only tracks the highest token it has previously seen, an old token might still be accepted before a newer fence reaches it. Revocation without a replacement exposes this problem particularly clearly. The acceptance contract must name the effective barrier or current-grant check and the disposition of requests already dispatched. [I3; P3]

Synthetic trace: holder A has generation 7, pauses, and is revoked. No successor is issued. The resource has seen only generation 7. A resumes and submits an operation. A test that merely compares 7 against the resource's maximum of 7 can accept stale authority. The expected safe trace either rejects it through an effective revocation/current-authority check, or accurately reports that strong revocation is unsupported and does not claim a pass. When generation 8 is issued, test both old-first and new-first delivery; only testing the easy new-first schedule conceals the gap. [P3; F07, F08, F14]

Where an external effect boundary cannot honor the required contract, R1 cannot claim immediate revocation there. A narrower pre-dispatch guarantee may be described, with in-flight effects explicitly unknown, but it is a different guarantee requiring appropriate acceptance. R0 is a compatible competitor for protected commitments; it is not automatically safe either if a stale Head-approved request can commit after its authorization changes. The same effect-boundary reasoning applies. [P3]

The liveness claim is conditional: with reachable canonical authority, functioning enforcement and an available Head, blocked work eventually receives a successor decision or a surfaced terminal/escalation outcome. No liveness guarantee is claimed under an unbounded partition or indefinite unavailability. [P3]

7 Telegram constraints normalization and recovery

Q5 Dated primary API observations

The following compact API capsule describes the primary HTTP Bot API as retrieved on 1 October 2026. The current displayed release is 10.3, dated 24 August 2026. It is documentation evidence; no configured bot or receiver was tested. [T4]

Polling and webhooks are exclusive; updates persist at most 24 hours. After at least one update-free week, the next update_id is random. New and edited messages are separate updates; ordinary deletion has no general Update field. Message IDs are chat-local; topic IDs are separate. message_thread_id supports forum supergroups and topic-enabled private bot chats. Polling confirms IDs below offset; negative offsets discard earlier updates. Webhooks retry failed delivery for unspecified attempts. secret_token marks configured webhook requests; allowed_updates changes are not retrospective. WebhookInfo exposes backlog/errors. sender_chat can represent anonymous administrators. getMe identifies the bot; retry_after gives a flood-control wait. No guaranteed outgoing idempotency key or token-rotation queue/webhook survival is documented. [T1]

The FAQ's free-limit guidance is roughly one message per second in one chat, 20 per minute in a group, and about 30 per second for bulk broadcasts. Bursts may be followed by 429 errors. These are dated operational guidance, not guaranteed capacity, and do not establish independent per-topic budgets. Paid broadcasts are a separate capability and are not a fallback in this report. The FAQ also describes privacy-mode filtering and reply precedence. [T2]

Current feature documentation permits conditional bot-to-bot communication: group commands/replies can pass when at least one bot has the communication mode enabled; broader receiving depends on the receiver's mode and admin/privacy conditions. Private bot messaging requires both bots enabled. The feature page requires loop safeguards. The dated changelog identifies these additions in version 10.0 on 8 May 2026, and earlier private-topic additions. An older blanket FAQ restriction conflicts with this newer material. Use the conditional rule, not either a blanket prohibition or universal visibility. [T3, T4]

The feature page describes replacement-token controls, and the official tutorial identifies a token as bot authentication rather than human-account authentication. This does not establish a Recursion Owner binding. Telegram's separate MTProto forum documentation contains deletion mechanisms; those cannot be imported as ordinary HTTP Bot API delivery guarantees. Protocol names and similarly named fields are not interchangeable support evidence. [T3, T5, T6]

What these observations constrain

The canonical command history cannot depend on Telegram keeping a recoverable transcript or queue. Receiving a transport update, acknowledging it, admitting an instruction and learning an effect's result need separate evidence. Topics are presentation addresses; rate pressure belongs to the applicable chat/group limits rather than a fictional allowance per ARM. Message normalization needs a capability matrix for the exact supported context, including any business, guest or ephemeral-message variants; unsupported variants remain explicit rather than coerced into ordinary-message assumptions. [B0; I6; P4]

Bot-to-bot support is useful as a conditional presentation feature, but canonical inter-actor collaboration must not rely solely on bots overhearing one another. No setting changes, admin grants, privacy changes, managed-bot privileges or paid delivery are authorized here. The accepted design must remain intelligible and controllable in CLI when transport projection is delayed. [B0; P4]

Q10 A normalized ingress record

The proposed normalization boundary retains distinct logical actor, authenticated principal, transport bot identity, route binding, credential generation, canonical command identity, intended-operation identity and observed transport identifiers. A credential string is never an actor key. A display name is never a principal proof. A route namespace includes context kind and the relevant bot/chat/topic bindings so that identifiers from different scopes cannot collide accidentally. [P2, P4]

Persist the authenticated ingress and its disposition before advancing the transport acknowledgment or polling cursor. A replay may reproduce a receipt without minting new execution authority. An edit is a new revision of a transport message, not a new unconditionally executable instruction. The canonical accepted version is retained separately from the current display version. Exact retention content, redaction and access policy remain Owner choices rather than an automatic promise to keep every message forever. [P4]

A dependency that has not arrived is missing evidence. Buffer it or mark the command unresolved; do not fill it from presumed chronology. A transport timestamp may help investigate timing but does not rank authority. A same-operation replay with changed content is an integrity conflict, and a semantic similarity detector cannot silently erase separately authorized repeated intent. [P2, P4]

Edits deletions and correction semantics

A metadata-only edit should not schedule new work. A semantic edit changes the requested action, affected resource, amount, destination or relevant scope and therefore needs a new attributable admission decision. If the first revision has already begun or completed, retain that fact. An explicit supersession or cancellation addresses future work; rollback is a separate action requiring its own authority and evidence. If an edited revision is received before its original, preserve it as unresolved revision evidence rather than inventing intermediate history. [P4]

Ordinary message or topic disappearance cannot safely mean cancellation, lease revocation, actor retirement or an audit-erasure request. A missing lookup can mean unavailable, not necessarily deleted. The proposed explicit canonical cancel/revoke/retire mechanisms have distinct meanings and authorization. A transport deletion event, where supported, can change presentation availability without rewriting a past accepted effect. [B0; P4]

Synthetic example: an already admitted request to prepare a public comparison is edited into a request to publish. The expected result is a new scope-sensitive admission decision, not automatic publication under the earlier harmless request. Removing the visible topic later leaves the ARM and its review state intact. These are required assertions, not observed behavior. [P4; F15, F16]

Intake gaps and week long inactivity

A permanently increasing numeric cursor is not sufficient across all documented intake conditions. Distinguish a confirmed update-free interval from a receiver outage during which updates may have existed. A proposed recovery record states the last durably accepted ingress, the continuity assumptions that still hold, and any interval whose completeness is unknown. An intake epoch may distinguish continuity regimes, but cannot disable deduplication or reauthorize old commands. [I6; P4]

Recovery should avoid blindly confirming an unknown backlog with an old cursor. The exact safe rediscovery procedure is an adapter acceptance question, not a protocol selected here. A numeric gap alone does not prove loss; an empty queue does not prove completeness. When content was never ingested and is no longer recoverable, the truthful outcome is a gap and, if necessary, an authenticated reissue by Owner. Reconstructing a plausible transcript is not recovery evidence. [P4; U2]

Token compromise revocation and replacement

The proposed recovery sequence is conceptual and does not authorize credential operations. Mark the affected route unavailable or suspect; preserve canonical actor, GoalSpec, work and review state; identify the compromise window and quarantine questionable intake; use the authorized secure credential process; verify recovered transport identity and intended binding; verify receiver configuration and subscriptions; reconcile backlog against accepted command records; record unresolved gaps; and resume with a single current receiver generation. [P4]

A successful token check is only one recovery observation. It does not prove end-to-end command receipt, correct subscriptions, absence of stale receivers or queue continuity. Do not assume a webhook secret changed with the bot token. Replacing a token for the same bot differs from binding a different bot account, even when its name and icon match. The latter needs explicit identity and trust validation. Neither operation creates a new ARM or revives old grants. [P4; U2]

If a compromise may have admitted a real command, changing the transport credential does not retrospectively certify the command's authority. Review canonical provenance and affected effects under existing incident authority. An unknown effect stays unknown until reconciled. A stale receiver must not keep admitting commands merely because it can reach an internal endpoint. [P2, P4]

Backpressure and truthful delivery

The proposed display policy coalesces routine progress, preserves unresolved critical notices and exposes delivery lag. It respects published limits and server backpressure. It does not add bots, switch identities or invoke paid broadcast to evade controls. A critical notification cannot be promised within an untested latency bound; the canonical status must remain inspectable through the accepted local surface. [P4, P5]

Outgoing delivery can be uncertain after a timeout. Record whether a message was computed, submitted, provider-acknowledged or remains unknown. Provider acknowledgment is not evidence of human receipt, reading or attention. Resending a digest is not a new canonical decision, but can still produce duplicate presentation. The system must not represent an unseen notification as Owner approval or a successful send as a verified effect. [P4, P5]

The named compatible competitor for these proposals is a narrower intake contract that requires explicit new commands for semantic edits and treats ambiguous recovery as manual reissue, while keeping canonical history and direct conversation. Transcript-first last-message-wins and token-coupled actor identity are invalid boundary violations. The recovery recommendation is falsified by an authenticated retry, edit, disappearance or credential change that grants new authority or duplicates a protected effect without a new authorized operation. [P4]

8 Canonical Head awareness and Owner digests

Q9 Head observation is different from Owner interruption

Head needs canonical awareness of accepted state changes even when Lucas need not be interrupted. Immediate in this report means processed as a control-relevant event without waiting for digest time, and before dependent protected action. It does not invent a millisecond SLA. Digest frequency can never postpone revocation, conflict checks, independent-review gates or authority changes. Exact consequence windows remain to be chosen and tested. [B0; P5]

Event class

Canonical Head treatment

Owner communication candidate

Direct command and authority change

Record admission or rejection, current scope and affected dependency

Immediate when a decision or urgent correction is needed; otherwise summarized

Lease expiry revocation or fence failure

Update current validity and gate dependent commitments

Prompt notice for unsafe attempt, lost control or unresolved required decision

Conflicting commands or cross goal dispute

Preserve alternatives and explicit resolution state

Present the consequential choice; no conversational winner

Budget uncertainty dependency cycle or terminal failure

Record ownership impact and blocked goal state

Interrupt when waiting has material consequence or Head cannot resolve

Review failure missing review or invalidated evidence

Keep submitted reviewed and accepted states distinct

Prompt correction if an earlier result is already being relied on

Routine bounded progress

Current work state and evidence links remain available

Coalesce into useful status changes rather than token streams

Route failure token replacement or topic loss

Track transport health separately from actor health

Interrupt only when timely awareness or control is materially affected

These are proposed event-policy classes, not an external standard or a report of installed behavior. An ARM need not relay every conversational sentence through Head for Head to observe the canonical commitments and exceptions that matter. The goal is complete state awareness at the relevant control boundaries, not centralized transcription of every token. Head receives only authorized minimum control metadata and evidence references; canonical monitoring does not widen privacy or authorize copying all private ARM content. [P5]

Digest correctness

A digest is computed from canonical actor/goal state and attributable events at a stated as-of revision or coverage watermark. Its entries identify actor and GoalSpec, current status, last verified evidence, independent-review/acceptance state, unresolved decisions, material dependencies or budget exceptions, and freshness or coverage gaps. Unknown, not checked, submitted, failed and accepted remain distinct. [P5]

A new progress update may replace older routine progress in a summary. It cannot suppress an unresolved cancellation, contradictory instruction, failed review, lost-ingestion interval or required Owner decision. A task marked complete without review remains unaccepted. A digest that is stale should disclose staleness rather than presenting itself as current. Computation coverage and delivery coverage are separate: retrying a view does not replay authority. [P5]

The Azure event-sourcing pattern describes an authoritative event record and query projections, along with replay, concurrency and schema-evolution complexity. It does not require Recursion to adopt event sourcing. Canonical transactional state with an attributable decision/audit journal is a compatible alternative. The research requirement is reconstructable, permission-aware truth; the storage pattern remains undecided. [E3; P5]

Preventing the hidden second executive

A digest generator has no mutation authority merely because it synthesizes the portfolio. It may render current priorities that Head has already decided; it may not silently choose new priorities, allocate cross-goal budgets, grant leases, accept work or retire an ARM. If a generated summary suggests a decision, it is a proposal linked to evidence. The authoritative decision is a separate attributable event by the authorized actor. [P5]

Likewise, monitoring is observation plus the already approved reactions, not an open-ended license to resolve every exception. A deterministic scheduler need not be an executive; an LLM summarizer need not be an executive. Either becomes a second executive if it can exercise the reserved powers independently. Conversely, a harmless component named manager does not prove the architecture violates the boundary. The acceptance test examines reachable authority transitions. [I1; P5]

For Owner reporting, compare exception-sensitive notices plus a canonical digest with a fixed-interval-only Owner summary, while immediate Head control handling remains identical. A missed urgent event, unbounded undisclosed view lag, or decisions that change after presentation deletion rejects the proposed digest contract. Lower notification count alone is not success if discovery and recovery effort increase. [P5, P7]

9 Public orchestration systems and documented limits

Q11 What the sources actually expose

This comparison is a source-supported capability map, not a product selection or conformance certification. D means documented in the cited material. A means explicitly application-defined or an application obligation. NC means not covered by the reviewed material; it does not mean impossible or absent everywhere in the product. Actor identity here means addressability unless stronger persistence evidence is explicitly stated.

System

Actor and message model

Lease and authority boundary

AutoGen 0.4.6

D type/key identities, direct messages, topics and subscriptions, sequential group-chat example

DS15 lease NC; GoalSpec and retained Head powers NC

OpenAI Agents SDK rolling docs

D caller-controlled tools and specialist handoffs

DS15 lease NC; argument-sensitive authorization A

LangGraph Python rolling docs

D thread checkpoints, cross-thread store and replayable work

DS15 lease NC; persistence is not authority

A2A 1.0.1

D messages tasks contexts and lifecycle

Authorization policy A; DS15 semantic lease NC

Orleans rolling docs

D request scheduling and interleaving

DS15 lease and agent permission model NC in cited scheduling page

Chubby Hazelcast and etcd

D lock key and lease coordination primitives

D generic fence/lease mechanisms; DS15 goal budget and executive semantics NC

AutoGen 0.4.6 uses a type/key agent ID and maps topics through subscriptions; unsubscribed topics have no recipients. Its lifecycle documentation explicitly says paging in/out was not implemented in that version. Its group-chat example selects one speaker at a time through a manager. State-saving documentation warns that custom agents need overrides because default state methods save and load empty state. Named agents and save/load method names therefore do not prove crash durability or complete authority-state recovery. [A01–A04]

The Agents SDK distinguishes agents-as-tools, where the caller keeps conversation control, from handoffs that make a specialist active for the remaining turn. Its handoff documentation places argument-sensitive authorization in the callback before effects. Its guardrail documentation describes first/final-agent boundaries, parallel input checks that can finish after tools run, and coverage limits for tool guardrails. Those are explicit reasons to examine the actual enforcement path rather than treating guardrail as a universal guarantee. [A05–A07]

LangGraph distinguishes thread-scoped checkpoints from cross-thread stores. Its functional API explains that completed task results can be reused during replay while an unfinished task can run again, requiring idempotent effects or result checks. Its recursion-limit error can indicate a cycle or simply a large finite graph. Checkpointing and a step cap are useful mechanisms; neither supplies exactly-once remote effects, semantic progress or a DS15 authority model. [A08–A10]

A2A 1.0.1 distinguishes conversation/task context from authenticated identity and server authorization. Send Message idempotency is optional, and cancellation is an attempt rather than guaranteed success. Opaque routing fields are not permissions. These are normative protocol obligations and options to validate in an adapter, not proof that an endpoint supports the desired semantics. [A11]

Orleans documents non-reentrant request processing, cyclic-call deadlocks and the stronger state reasoning needed when reentrancy permits interleaving. Chubby, Hazelcast and etcd contribute the coordination distinctions in Section 6. None of the reviewed sources establishes the entire Recursion GoalSpec, Head, budget, lease and independent-acceptance contract. That bounded finding does not claim an exhaustive impossibility theorem about all orchestration systems. [A12–A15; I7]

Transferable lessons without adopting a framework

The useful transfers are conceptual: keep recipient identity separate from broadcast surfaces; define what state is durable; distinguish conversation control from authority; check authorization on the actual effect path; expect replay and uncertain completion; and treat concurrency bounds as safety/liveness mechanisms with limitations. No framework name, protocol endpoint or method listing removes those proof obligations. [I7]

An actor abstraction does not automatically solve natural-language conflicts. A checkpoint does not retroactively cancel effects. A cancellation method does not imply interruption before commitment. A manager label does not establish portfolio authority. A lease primitive does not encode GoalSpec semantics. These distinctions explain why the synthetic suite tests concrete transitions rather than architectural vocabulary. [I3, I5, I7]

10 Human coordination evidence and the open empirical question

Q12 No direct benefit estimate is established

The direct answer is unverified. This investigation did not locate a primary study measuring Recursion Owner-to-ARM conversation against a matched alternative for total coordination effort, lost context, contradictory instructions and independent-review bypass. That is an evidence gap, not a finding of no benefit. Direct conversation remains accepted regardless of whether a particular supporting topology or display arrangement proves better. [U1; B0]

The studies below are primary evidence about their own settings. They help identify plausible mechanisms, failure modes and measurements. None selects Telegram bot count, proves a CLI disadvantage, requires a graphical frontend, or demonstrates safe portfolio authority. The cited arXiv versions are the versions actually examined; a later publication record is not silently substituted for them.

Study

Bounded finding

Transfer limit

Perspectra H1

18 participants; counterbalanced short ideation sessions; targeted mentions threads and mind-map support compared with group chat; workload differences were not statistically significant

Bundled interface changes; no isolated direct-address effect or longitudinal portfolio study

AgentCoord H2

12-person evaluation after formative work; structured strategy interface received more favorable comprehension exploration and satisfaction ratings

Static strategy design and subjective measures; loops and missing content were not eliminated

AGDebugger H3

Six error-identification and eight different steering participants; only two of eight achieved the exact correct answer in the steering evaluation

Small debugging sample and narrow tasks; preference for controls did not establish effective repair

Sensemaking H4

12-person qualitative study of five mock interfaces; agreement agent count and critique shaped reliability judgments

All final answers shown were accurate; no causal estimate of error detection or review safety

When Should Users Check H5

48 participants in simulated tasks; intermediate checks reduced mean trial time 13.54 percent and were preferred by 81 percent

Controlled errors and time objective; late errors could make extra checks slower; no live multi-ARM safety test

Perspectra's non-significant workload result is not evidence of equivalence. AgentCoord's favorable ratings are not measured contradiction reduction. AGDebugger's ability to edit or reset conversation state is not proof that arbitrary external effects can be undone. Sensemaking's trust cues caution against treating visible consensus or a critic persona as independent verification. The confirmation-timing study shows why repair cost and error location matter, while leaving mandatory safety and authority gates intact. [H1–H5; I8]

A bounded evaluation proposal

The proposed study concerns the realized costs of an accepted interaction, not whether to remove it. Direct addressing remains available in every shipping candidate. A Head-relayed condition could be a research reference only, never an alternative product decision that reopens the boundary. The primary product-facing comparison is direct addressing with explicit canonical context/admission receipts versus direct addressing with minimal receipts, under the same authority and review rules. Bot topology can be compared in a separate matched stage. [P7]

Hold task goals, actor capabilities, GoalSpecs, review requirements, latency/error scripts and difficulty constant. Use synthetic projects with known constraints and independently specified ground truth. Counterbalance condition and task order, report training costs, and retain failed tasks in workload reporting. Include simple clarification, parallel goals, interdependent changes, conflicting commands, absent/resuming Owner, actor discovery, failed review, stale state and transport outage. A combined comparison that changes interface, agents, latency and permission rules at once cannot identify a direct-addressing effect. [P7]

Primary effort measure: total active Owner time spent finding and routing work, restating context, reconciling instructions, checking current state and repairing errors. Report all component times and aggregate them over all attempted tasks, alongside independently accepted task count, failure count and effort per accepted task. A design that drops failures from the numerator or shrinks the denominator silently can look efficient while making less useful progress. [P7]

Secondary measures include context-restatement turns, actor switches, routing corrections, time to locate current decisions and evidence, end-to-end completion time, reviewer effort, a predeclared workload measure, and confidence about what has actually been accepted. Preference and lower message count are useful observations but not substitutes for the primary outcome. [P7]

Safety and quality measures come from canonical truth and blinded independent review: missing required constraints at action time; incompatible executable instruction pairs; wrong-goal actions; unauthorized mutations; accepted artifacts without independent review; stale-lease commitments; missed urgent events; and mistaken Owner beliefs about acceptance. The study must not request hidden chain-of-thought. Plans, actions, decisions, concise explanations and evidence are the relevant observable material. [P7]

Lucas must set the minimum worthwhile effort reduction and tolerable nonsafety tradeoffs before outcomes are examined. Enumerated authority violations have zero tolerance in the conformance fixtures. Human safety noninferiority needs a justified exposure and uncertainty analysis, with participant/task dependence addressed; zero observed violations is not a universal zero-risk result. A small nonsignificant comparison is inconclusive, not a pass. [P7]

The benefit claim fails if the predeclared effort criterion is not met with adequate evidence, or context, contradiction or review outcomes exceed the allowed margin. A hard authority invariant failure rejects the candidate regardless of preference scores. If direct conversation proves useful for autonomy or clarity without measured effort savings, report that narrower result instead of inventing a speedup. [P7]

11 Recommendation alternatives and decisive falsifiers

R1 Candidate to evaluate

Evaluate one transport-independent actor/authority contract with attributable direct commands, explicit GoalSpec revisions, current step leases enforced at protected boundaries, canonical Head awareness and independent acceptance. Compare it with R0, Head-mediated approval of each protected workflow commitment, under the same direct-conversation and transport boundaries. R1 delegates bounded coordination; R0 retains bounded step leases for permitted coordination while Head mediates each protected commitment. Neither entails a new executive. This is a recommendation for evaluation, not an instruction to implement, deploy or adopt a default. [P1–P7]

The principal reason to prefer evaluating R1 is that it expresses the accepted direct-conversation and bounded-lease intent without making Head a relay for every sentence. The proposed advantage is less coordination and waiting for already authorized work. That advantage is unverified. The reason to retain R0 as a serious competitor is simpler attribution of protected decisions and potentially fewer distributed validity checks. Its potential disadvantages are Head workload, delay and a concentrated availability dependency, which are also unmeasured. [I9]

R1 is decisively rejected for the affected scope if an independently reproducible test admits reserved Head powers through a route or room role, accepts a fresh protected commitment after the declared effective fence, or treats missing independent review as acceptance. The strong fence claim is also unsupported for a necessary effect class without an enforceable boundary. A conformance pass would not establish human benefit; that requires Section 10. Failure does not justify adding a second executive or withdrawing the accepted direct route. [P1–P7]

Recommendation register

Each proposal below is subordinate to R1 and has a named compatible competitor, rejection evidence and a bounded claim. The fixture identifiers refer to Section 12. Rejected boundary violations are listed only as hazards, not as eligible alternatives.

Proposal

Compatible competing option

Decisive falsifier and what is not proved

P1 Separate actor identity from surfaces and test T-A T-B T-C

Per-conversation actor instances explicitly linked to the same goal and retained Head authority

Reject if attribution or required privacy cannot survive route remapping while competitor can; does not prove operational isolation or effort reduction

P2 Attributable admission with explicit target scope and revisions

Authenticated route-bound narrow capability with equivalent current-scope checks

Reject any route-only permission enlargement or wrong-principal admission; does not prove authentication integrity or prompt-injection immunity

P3 Enforce bounded lease at protected boundary

R0 Head-mediated protected commitments with equivalent current validity checks

Reject stale post-barrier commit or reserved-power exercise; does not undo prior effects or promise universal fencing support

P4 Canonical normalization and explicit uncertain recovery

Narrow intake requiring new commands for edits and manual authenticated reissue after gaps

Reject duplicate effect silent history rewrite or false complete recovery; does not guarantee transport completeness or exactly-once delivery

P5 Canonical event views and exception-sensitive Owner notice

Canonical fixed-interval Owner summary with identical immediate control handling

Reject hidden urgent event decision-changing projection loss or undisclosed lag beyond accepted consequence window; does not prove lower human workload

P6 Independent adversarial fixture gate across topologies

Independently reviewed bounded formal model plus adapter conformance tests covering the same invariants

Reject if negative controls pass unsafe behavior or a required path lacks evidence; does not prove all schedules or real deployment safety

P7 Matched empirical evaluation before claiming benefit

Direct conversation with minimal receipts and identical authority/review rules

Reject claimed benefit if effort criterion fails or harm margins fail with adequate evidence; inconclusive data is not a pass or universal falsification

For P1, any per-conversation instance competitor still needs an unambiguous logical authority owner; it cannot use duplicated actor instances to multiply grants. For P6, formal reasoning and examples are complementary: a proof about an abstract model cannot substitute for evidence that a transport adapter implements that model. No universal minimum sample size, timeout, lease duration, digest cadence or notification threshold is selected here. [P1, P6, P7]

12 Synthetic acceptance fixtures and proof limits

Q13 The minimum credible test target

No finite set of chat examples proves that every possible topology lacks a second executive. The credible target is a bounded noninterference property: when logical actors, goals, grants and intended commands are unchanged, changing route topology or presentation order does not create new authority, alter cost ownership or bypass review. Tests can decisively find a counterexample and establish conformance for stated traces; universal claims require a stronger justified coverage argument. [P6]

Use synthetic Head H, ARM A for goal Alpha, ARM B for goal Beta, bounded worker W and independent verifier V. The fixture state includes separate GoalSpec revisions, room membership, allowed verbs, synthetic allowance units and lease generations. Exercise the CLI, T-A, T-B and each explicitly defined T-C configuration. A fake effect boundary must be able to enforce, delay or ignore fences so the suite contains a meaningful negative control. No real credentials, account setup, purchases or provider actions are part of these proposed fixtures. [P6]

For every run, evidence includes initial and final authority graphs, accepted and rejected transitions, normalized principal/target/command identities, current scope revisions, lease and fence state, budget reservations and outcomes, canonical Head events, digest coverage and independent findings. Preserve failing traces. A generated expected transcript, implementer's PASS or a model's explanation is not an executed test result. The fixtures below are all NOT RUN. [P6]

Authority and coordination fixtures

Fixture

Adversarial input or fault

Required assertion

F01 Topology noninterference

Replay same commands across routes; rename reorder and rebind presentation labels

Same authority and ownership outcomes after projection metadata is ignored; no extra portfolio actor

F02 Direct address scope

In-scope direct Owner instruction followed by spending privacy or deployment expansion; forged Head body

Correct attribution; expansion pending explicit authority path; forged body grants nothing

F03 Reserved powers

Valid holder attempts membership GoalSpec lease transfer cross-goal settlement ARM retirement and strategic escalation

Every forbidden transition rejected; corresponding authorized Head positive controls succeed

F04 Simultaneous conflict

Contradictory commands at same revision in different arrival and timestamp orders

No two incompatible current commitments; explicit authoritative resolution rather than transport winner

F05 Compatible concurrency

Independent commands with separate resources then common remaining allowance

Valid independent work progresses under stated assumptions; shared resource cannot be oversubscribed

F06 Retry and repeated intent

Same operation twice; same ID changed payload; distinct similar commands; crash after effect

Retry does not mint authority; mismatch rejected; intentional repetition preserved; uncertain effect reconciled

F07 Paused expired holder

Pause before expiry; issue successor; resume old action in old-first and new-first schedules

Stale generation rejected at defined effective boundary; both schedules checked

F08 Revocation without successor

Revoke centrally; delay resource observation; submit old in-flight and fresh actions

Barrier status truthful; no false cancellation; no fresh post-barrier commitment

F09 Scope revision race

Remove member or change scope after admission; restart from old checkpoint

No revived membership grant or stale authority; evidence access checked separately

F10 Budget ownership

Competing reservations; borrow refill transfer or refund unknown outcome

No implicit cross-goal transfer double debit or invented refund; unknown is retained

F11 Cycle and unavailable Head

A and B repeatedly delegate; Head absent then restored

Bounded automatic work and escalation; no self-promoted coordinator; valid resolution later progresses

F12 Independent review

Worker PASS echoed by room; missing failed or nonindependent verifier

Unaccepted remains unaccepted; authorized independent review path can advance state

F13 Lost projections

Remove mute archive or rewrite every presentation after canonical recording

Same canonical decisions and unresolved exceptions at same watermark; actor survives

F14 Nonfencing negative control

Effect resource ignores token or times out after committing

Strong safety or exactly-once claim must fail; unsupported or unknown surfaced

Transport and digest fixtures

Fixture

Adversarial input or fault

Required assertion

F15 Edit semantics

Metadata-only edit; semantic escalation; edit before original; edit after effect

No work from metadata; fresh admission for semantics; no fabricated revision or rollback

F16 Deletion and explicit cancel

Ordinary deletion unobserved; supported deletion observed; topic disappears

Availability updates cannot retire ARM or cancel effect; explicit authorized cancel remains distinct

F17 Intake discontinuity

Eight-day update-free interval with lower next ID; separate outage beyond retention

No stale-cursor discard; unknown interval explicit; no invented completeness from empty queue

F18 Credential recovery

Revoke route mid-step; old receiver replay; same-bot replacement; different-bot substitution

Actor state unchanged; current binding verified; stale receiver blocked; unresolved gaps remain visible

F19 Identity and visibility

Anonymous admin forwarded Owner-looking text duplicate names stale replies and mention ambiguity

No Owner spoof; ambiguous target unresolved; visibility never creates authority

F20 Conditional bot delivery

Bot modes off one-on both-on; group mention reply privacy/admin combinations

Capability claims match verified context; canonical collaboration survives unavailable transport path

F21 Rate pressure and loops

Many topics plus automatic replies and 429/backpressure

Bounded messages and no evasion; critical status remains canonical; delays honestly surfaced

F22 Digest and delivery lag

Stall generation drop send duplicate send and delay Head event consumer

Control gates unaffected; coverage and delivery distinct; acknowledgment never approval

F23 Selective privacy

Head view requests private content outside its allowed exposure; room receives mixed-goal digest

Only authorized minimum control metadata and evidence references exposed; no cross-goal content spill

F24 Surface authority equivalence

Valid step on CLI and Telegram while transport token changes

Equivalent authorization result; token generation cannot alter GoalSpec or accept work

These are minimum families rather than 24 single happy-path scripts. Permute relevant delivery orders, crash points, duplicate counts, expected revisions and actor names. Combine lease expiry with checkpoint replay and route replacement; combine conflicting commands with uncertain budget effects. Every mandatory state mutation and reserved power must map to a fixture or a justified formal argument. Untested combinations remain unverified. [P6]

Positive controls matter. A suite that rejects everything proves no useful liveness. In-scope commands, valid successor grants, authorized Head decisions and genuinely independent review must also succeed under their stated assumptions. Negative controls matter equally: accepting the nonfencing resource or treating an implementer as an independent verifier must make the suite fail. A fixture framework that always reports PASS has no evidentiary value. [P6]

Evidence and acceptance boundary

Independent review must check both the expected invariants and the recorded transitions, with no reliance on an implementer's own success label. Review includes whether the attempted effect actually reached the enforcing boundary, whether the revocation barrier was effective, whether the cost outcome is known and whether the checker can distinguish projections from authority. Passing only a mock adapter cannot certify a different real adapter. [B0; P6]

A successful bounded run could establish route-invariant authority and correct handling for its tested states and faults. It cannot establish security against arbitrary credential compromise, correctness of all natural-language interpretation, all schedules or actor counts, fairness under endless load, universal external-effect idempotency, or reduced Owner effort. The report supplies a testable contract and rejection evidence; it does not label any fixture passed. [P6; U1–U4]

13 Source pinned claim register

All public sources below were retrieved on 1 October 2026 UTC. Exact URLs, versions and sections appear in Section 14 under the same IDs. F is source-documented fact, I inference, U unverified and P a proposal marker. Confidence applies only to the narrow claim. B0 is supplied authority context. No source-supported claim is presented as locally tested implementation behavior.

Claim or family

Classification and confidence

Pin and bounded support

Expiry or recheck trigger

C01 Accepted roles direct conversation lease fields and interaction boundary

B0 supplied requirement; high fidelity

B0 full brief; Sections 1 3 6

Explicit later Owner amendment

C02 Exact official Grok Bot reference identified

F high

G1–G5 official pages; Section 2

URL page ownership or product revision

C03 Persistent role conversations and collaboration patterns

F high about description

G1 G2; Section 2

Page revision or contrary observation

C04 Mentioned group handoffs and stage ownership guidance

F high about description

G3 collaboration sections; Section 2

Feature or rollout change

C05 Personal Bots share ambient computer resources without isolation claim

F high

G4 G5 shared-computer sections

Changed personal or team product boundary

C06 / I2 Grok interaction pattern is not DS15 authority proof

I high about evidence limit

G1–G5 reviewed scope; I2

Explicit enforceable contract and independent evidence

C07 Dated API intake identifiers and recovery limits

F high; absence claims I high

T1 compact capsule in Section 7

Bot API schema or semantics revision

C08 Rate guidance and FAQ conflict

F high as dated documentation; current behavior conditional

T2–T4; Section 7

Revised FAQ limits feature rules or observed backpressure

C09 Conditional bot visibility and topic evolution

F high

T3 T4 current features and dated history

New API or configured capability evidence

C10 Token is bot authentication and can be replaced or revoked

F high

T3 T5; Sections 3 and 7

Authentication contract or account-binding change

C11 MTProto deletion does not establish Bot API delivery

F about interfaces and I high

T1 T6; Section 7

Explicit ordinary Bot API coverage

C12 AutoGen identity addressing and lifecycle caveat

F high for 0.4.6

A01 A02; Section 9

Selected version or lifecycle implementation changes

C13 AutoGen group example and state save limitations

F high for 0.4.6

A03 A04; Section 9

Group pattern custom state or runtime changes

C14 Agents SDK control paths and authorization location

F high about rolling docs

A05 A06; Section 9

Handoff or callback pipeline change

C15 Guardrail coverage and timing limitations

F high about rolling docs

A07; Section 9

Execution mode or tool-category changes

C16 LangGraph state replay and step bounds

F high about rolling docs

A08–A10; Section 9

Checkpointer task or termination changes

C17 A2A routing policy and lifecycle obligations

F high for 1.0.1

A11 specified sections; Section 9

Protocol adapter or endpoint version change

C18 Resource-side stale-holder enforcement examples

F high within source scope

A12 A13; Section 6

Resource or lock configuration and failure model change

C19 Durable state delayed observations and uncertain completion differ

F high for etcd semantics

A14; Section 6

Read mode cluster settings or version change

C20 Actor scheduling has safety and liveness tradeoffs

F high about Orleans documentation

A15; Section 9

Reentrancy or scheduling change

C21 Fine-grained authority details need domain semantics

F high

E1 RFC9396; Section 4

New relevant standard or changed permission model

C22 Event identity does not carry authorization by itself

F for identity and I high for boundary

E2 CloudEvents1.0.2; Section 4

Event-contract or authentication changes

C23 Canonical event projections are documented with complexity costs

F high; application transfer I

E3; Section 8

State architecture or projection requirements change

C24 Perspectra findings and workload uncertainty

F high for examined v1; transfer moderate

H1 §§4–5 7; Section 10

Correction final-version difference or matching replication

C25 AgentCoord ratings do not measure live portfolio safety

F and I moderate transfer

H2 §§3 6 7.3; Section 10

Dynamic-workflow or CLI replication

C26 AGDebugger steering preference is not reliable repair proof

F high; inference moderate

H3 §§5–7; Section 10

Broader tasks external-effect restoration evidence

C27 Sensemaking study is qualitative and lacks erroneous final outputs

F high

H4 §§4.4 5 6.4; Section 10

Error-containing causal study or replication

C28 Confirmation timing benefit is setting dependent

F high for simulated v4 study

H5 §§6–8; Section 10

Real deployment safety-aware or changed-latency evidence

I1 Room role differs from portfolio authority

I high for consistency with brief

B0 A03; Sections 2 3 8

Reachable reserved-power counterexample

I3 Lease validity needs effect-boundary enforcement

I high under stated failure model

A12–A14; Section 6

Different boundary semantics or counterexample

I4 Bot count alone does not prove isolation or usability

I high containment logic; usability U

T3 T5; Section 3

Verified trust-domain and human results

I5 Log order is not policy precedence

I high under accepted boundary

B0; Sections 5 6

Owner-authorized explicit precedence changes

I6 Telegram cannot be the sole canonical recovery record

I high under brief and API limits

B0 T1; Section 7

Boundary changes or stronger authorized transport evidence

I7 Reviewed systems do not establish the full DS15 contract

I high as bounded review finding

A01–A15; Section 9

New specific source or independently tested conformance

I8 Human studies inform measurement rather than prove ARM benefit

I moderate transfer

H1–H5; Section 10

Matched longitudinal Owner-to-ARM study

I9 R1 and R0 workload and availability tradeoffs

I moderate; magnitude U

B0 and contract analysis; Section 11

Matched empirical results

P1 Actor and topology evaluation contract

I plus P; moderate adequacy

Sections 3 11 12; B0 A01 A02

Attribution privacy or topology-invariance falsifier

P2 Command admission and authority separation

I plus P; high consistency; untested

Sections 4 11 12; B0 E1 E2

Route-only grant or wrong-principal acceptance

P3 Enforceable bounded lease contract

I plus P; high consistency; untested

Sections 6 11 12; B0 A12–A14

Stale post-barrier or reserved-power commitment

P4 Normalization recovery and accounting

I plus P; moderate adequacy; untested

Sections 5 7 11 12; B0 T1–T6 A09

Duplicate effect false recovery or ownership violation

P5 Canonical monitoring and digest contract

I plus P; moderate adequacy; untested

Sections 8 11 12; B0 E3

Lost urgent event authority-changing summary or privacy spill

P6 Independent fixture and bounded proof gate

I plus P; high evidence discipline; unrun

Sections 11 12; B0 and stated model

Unsafe negative control passes or required path omitted

P7 Human and topology evaluation criteria

I plus P; moderate design; unrun

Sections 3 10 11; H1–H5

Predeclared effect or safety criterion fails

U1 Direct Owner coordination benefit and error rates

U; no direct estimate

Section 10; no Recursion study performed

Adequately designed matched study

U2 Configured Telegram recovery visibility and latency

U; no runtime observation

Section 7; T1–T6 limits

Authorized adapter and transport acceptance evidence

U3 Actual credential/backend containment and effect enforcement

U

Sections 3 6 12; no system inspected

Independent fault and boundary evaluation

U4 General safety all schedules and production conformance

U

Section 12 finite-scope limitation

Justified formal coverage plus adapter/deployment evidence

14 Primary source bibliography

B0. Supplied DS15 ARM conversations and multi-agent rooms brief, last updated 30 September 2026. Full 109 lines examined. Authoritative for the research's accepted constraints only; not public empirical evidence or a runtime inspection.

G1. xAI. Grok Bot overview. Updated 21 September 2026. Introduction and What makes Grok Bot different. Retrieved 1 October 2026.

G2. xAI. Create and manage Bots. Updated 29 September 2026. What a Bot remembers and Organize a team of Bots. Retrieved 1 October 2026.

G3. xAI. Message and collaborate. Updated 21 September 2026. Group chat, Direct a message, handoffs, threads and reactions. Retrieved 1 October 2026.

G4. xAI. Grok Bot frequently asked questions. Updated 29 September 2026. Shared computer and parallel work. Retrieved 1 October 2026.

G5. xAI. Approvals security and privacy. Updated 28 September 2026. Shared-computer boundary, least privilege and Auto Review. Retrieved 1 October 2026.

T1. Telegram. Bot API reference. Visible release 10.3, 24 August 2026. Getting updates; Update; getUpdates; setWebhook; WebhookInfo; Message; User; sendMessage; ResponseParameters; getMe. Rolling reference retrieved 1 October 2026.

T2. Telegram. Bots FAQ. Rate limits, message visibility and bot-message FAQ. Undated rolling page retrieved 1 October 2026; documented conflicts with newer sources are retained in Section 7.

T3. Telegram. Bot features. Bot-to-bot communication; generating an authentication token; managed bots. Undated rolling page retrieved 1 October 2026.

T4. Telegram. Bot API changelog. Versions 10.3 on 24 August 2026, 10.0 on 8 May 2026, 9.6 on 3 April 2026, 9.4 on 9 February 2026 and 9.3 on 31 December 2025. Retrieved 1 October 2026.

T5. Telegram. From BotFather to Hello World. Obtain Your Bot Token. Undated rolling page retrieved 1 October 2026.

T6. Telegram. Forum topics in the MTProto API. Deletion mechanisms. Undated rolling page retrieved 1 October 2026; explicitly not used as HTTP Bot API support evidence.

A01. Microsoft. AutoGen agent identity and lifecycle. Version 0.4.6, Agent ID and Agent Lifecycle. Retrieved 1 October 2026.

A02. Microsoft. AutoGen topic and subscription. Version 0.4.6, Topic and Subscription. Retrieved 1 October 2026.

A03. Microsoft. AutoGen group chat. Version 0.4.6, design example and message protocol. Retrieved 1 October 2026.

A04. Microsoft. AutoGen managing state. Version 0.4.6, Saving and Loading Agents and Teams. Retrieved 1 October 2026.

A05. OpenAI. Agents SDK agent orchestration. Core SDK patterns. Rolling Python documentation retrieved 1 October 2026; no installed release tested.

A06. OpenAI. Agents SDK handoffs. Argument-sensitive authorization and handoff callback discussion. Rolling Python documentation retrieved 1 October 2026.

A07. OpenAI. Agents SDK guardrails. Workflow boundaries, execution modes and tool guardrails. Rolling Python documentation retrieved 1 October 2026.

A08. LangChain. LangGraph persistence. Checkpoints, threads and stores. Rolling Python documentation retrieved 1 October 2026.

A09. LangChain. LangGraph functional API. Determinism and idempotency. Rolling Python documentation retrieved 1 October 2026.

A10. LangChain. LangGraph recursion limit. Description and troubleshooting. Rolling Python documentation retrieved 1 October 2026.

A11. A2A project. A2A specification version 1.0.1. Sections 3.1.5, 3.3.1, 3.4.1, 4.4.6 and 7.5. Retrieved 1 October 2026. Protocol text is not endpoint conformance evidence.

A12. Hazelcast. FencedLock. Version 5.5, Fencing Tokens and consistency configuration warning. Retrieved 1 October 2026.

A13. Mike Burrows. The Chubby lock service for loosely coupled distributed systems. OSDI 2006, Section 2.4, pages 4–5. Publisher research record. Retrieved 1 October 2026.

A14. etcd project. etcd API guarantees. Version 3.6, KV, Watch, Lease and Operation completed sections; page modified 26 September 2025. Retrieved 1 October 2026.

A15. Microsoft. Orleans request scheduling. Non-reentrant model and Reentrancy. Rolling documentation retrieved 1 October 2026.

E1. Lodderstedt, Richer and Campbell. RFC 9396 OAuth 2 Rich Authorization Requests. May 2023, Sections 2 and 2.2 and authorization comparison discussion. Retrieved 1 October 2026.

E2. CloudEvents project. CloudEvents specification version 1.0.2. Required id and source attributes; versioned public specification. Retrieved 1 October 2026 through public web research, not a repository connector.

E3. Microsoft Azure Architecture Center. Event Sourcing pattern. Authoritative records, projections and complexity considerations. Rolling documentation retrieved 1 October 2026.

H1. Liu and colleagues. Perspectra Choosing Your Experts Enhances Critical Thinking in Multi Agent Research Ideation. Examined arXiv 2509.20553v1, 24 September 2025, Sections 4–5 and 7. CHI 2026 publication record. Retrieved 1 October 2026; v1 findings are not silently attributed to a different final version.

H2. Pan and colleagues. AgentCoord Visually Exploring Coordination Strategy for LLM based Multi Agent Collaboration. Examined arXiv 2404.11943v1, 18 April 2024, Sections 3, 6 and 7.3. Retrieved 1 October 2026.

H3. Epperson and colleagues. Interactive Debugging and Steering of Multi Agent AI Systems. Examined arXiv 2503.02068v1, 3 March 2025, Sections 5–7. CHI 2025 publication record. Retrieved 1 October 2026.

H4. Pareek and colleagues. Sensemaking in Multi Agent LLM Interfaces. Author full text, CHI 2026, Sections 4.4, 5 and 6.4. Publication record. Retrieved 1 October 2026.

H5. Zhou and colleagues. When Should Users Check Modeling Confirmation Frequency in Multi Step Agentic AI Tasks. Examined arXiv 2510.05307v4, revised 15 September 2026, Sections 6–8. Version history and CHI publication record. Retrieved 1 October 2026.

15 Open decisions empirical gaps and completion gate

Questions reserved for Lucas

What transport-compromise containment is acceptable, and which genuine privacy or capability domains merit separate transport identities? This informs eventual comparison of T-A, T-B and T-C; it does not select one now.

Which protected-effect classes may a bounded step lease coordinate within the existing envelope, and what delay between requested and effective revocation is acceptable for each? Effects that cannot support the required boundary must be named rather than assumed safe.

What authenticated sender-to-Owner binding and supported message classes are acceptable for optional Telegram use? Unsupported contexts must remain explicit.

What semantic edit, explicit cancellation, retention and redaction rules should govern canonical evidence? Presentation deletion and authority revocation remain distinct.

What budget attribution applies to legitimate multi-goal work, and what no-progress conditions require escalation? A room must not invent its own allocation rule.

What consequence windows warrant immediate Owner notice, and what digest cadence and evidence detail are useful without copying private ARM content unnecessarily?

What is the minimum worthwhile coordination saving, and what nonsafety usability tradeoffs are acceptable? Acceptance still requires independent review and the fixed authority constraints.

These are value and policy choices public sources cannot make. They are not permission requests that block the report. Fixed decisions are not in the question list: direct ARM conversation, Head retention, bounded leases, no new executive tier, canonical interactive CLI and optional Telegram remain intact. [B0]

Empirical questions still open

Actual routing mistakes, Owner effort, context loss, contradiction frequency and review bypass are unknown. So are deployed credential containment, supported Telegram visibility combinations, queue/configuration behavior through token replacement, gap recovery correctness, effect-boundary fencing, notification latency under pressure and starvation under conflicting work. No score, zero count or PASS has been substituted for those missing observations. [U1; U2; U3; U4]

A future authorized evaluation should stop claiming success at the boundary its evidence reaches. A clean synthetic authority trace can support bounded conformance. A matched human study can estimate effort for its participants and tasks. Neither certifies the other, and neither grants permission to change the accepted constitution or deploy a default. [P6, P7]

Completion gate

Required item

Research result

Remaining boundary

Exact Grok reference pinned or dropped

Verified official G1–G5 with retrieval dates before use

Product behavior not operationally tested

Consequential claims sourced or unverified

Inline IDs and claim register distinguish F I U and proposals

Rolling pages expire on stated triggers

Every recommendation has competitor and falsifier

Sections 3 and 11 give eligible alternatives and rejection tests

No product-default decision made

Accepted Owner decisions remain closed

Fixed boundary retained throughout

Open questions concern unresolved values only

Protected paths untouched and output report only

Public and synthetic research; no product edits or runtime actions

No implementation acceptance claimed

Privacy and secret check

Public URLs supplied role context and invented fixture data only

No credentials private transcripts account identifiers or private repository material included

Telegram limits dated

Documentation reviewed 1 October 2026; conflicting FAQ statement identified

No SLA or tested configuration inferred

Empirical and Owner gaps explicit

Sections 10 12 and 15 enumerate them

Missing verification is never a pass

The research supports a precise acceptance question: can every surface preserve the same bounded actors and grants while improving Owner coordination under measured conditions? It does not support declaring a winning bot topology, unconditional transport reliability, or an additional executive that resolves the hard cases by acquiring more authority.


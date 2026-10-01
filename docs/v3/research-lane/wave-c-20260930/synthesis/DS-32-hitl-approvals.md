# DS-32 — Human-in-the-loop approvals and consultation (synthesis)

## Provenance

- Raw report: `raw/ds-DS-32-hitl-approvals.md`.
- Source prompt: DS-32 — human-in-the-loop approvals, forwarding and consultation.
- Session: Wave C Deep Research (self-contained handoff); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved: source-documented, locally-observed (the supplied brief), inference, proposal, and unverified/unknown.
- The report treats Aggressive/Full/Lazy Stop, preserved forks, direct Owner-to-ARM communication, and notification-as-projection as accepted boundaries it must not reopen.
- The report states it performed no implementation, repository edit, provider/model call, auth/config change, spending, deployment, publication, merge, or live trial.

## The question

How can human-in-the-loop approvals, steering and forwarding, consultation, terminal controls, preserved forks, notifications, and owner-facing activity views be specified to a testable level while preserving Recursion's accepted authority boundary — provider neutrality, Owner as final authority, separate request/delivery/answer/adoption/effect lifetimes, notifications as projections of canonical state, and the rule that a host reply or protocol acknowledgment is never human approval?

## Key findings

**(a) Three superficially similar approval mechanisms have different safety properties.** An approval **callback** occurs in the application/agent harness before resumption and cannot prove a human decided, that every effect path invokes it, or that arguments/state are unchanged. An always-invoked **pre-effect hook** inspects tool calls only through the instrumented harness path. **Resource-bound mediation** occurs at the component that actually admits or performs the state-changing operation and can refuse effects lacking current valid authorization.

**(b) The report recommends resource-enforced mediation as the canonical authorization boundary.** OpenAI's Agents SDK shows programmatic approval callbacks can decide without a human and advises server-side ownership and replay-safe consumption; Anthropic's Agent SDK exposes a `PreToolUse` hook with a specific tool-use identity; Kubernetes admission control illustrates the stronger resource-side pattern and warns that a webhook's own out-of-band side effects must be reconciled because invocation does not guarantee persistence.

**(c) Sandboxing and approval are separate controls.** OpenAI Codex documentation independently defines filesystem/network boundaries, escalation-approval policy, and whether a user or automatic reviewer decides; automatic review does not change the sandbox boundary. Upstream harness permissions should be adapter evidence or extra containment, not substitutes for Recursion's GoalSpec, grants, leases, and authority model.

**(d) Safe approvals must reject four classes independently:** **stale decision** (goal/task/target/grant/lease/action revision or expiry differ — preserve as evidence, return typed conflict, no effect); **replay** (decision identity already atomically consumed); **retargeted action** (submitted target, arguments, scope, action hash, or tool-call identity differ from the server-owned proposal); and **non-human reviewer presented as human** (record the actual principal; never emit "human approved").

**(e) Approval and effect are separate facts.** The recommended pre-effect record binds identity, exact action and normalized arguments, scope, Recursion authority (goal/task/grant/lease generations), principal and provenance class, freshness/expiry, replay control, execution attempt, settlement (`applied`/`rejected`/`failed`/`unknown`/`reconciled`), and causality. The decisive invariant: **no authoritative effect is settled merely because approval exists**; if the outcome cannot be established after dispatch, the state is `unknown`.

**(f) Steering separates receipt, application, and next-turn scheduling.** OpenAI's Responses steering contract documents that `response.steer.accepted` means the server owns queued input, not that it was applied; the successor `response.created` is the commit point. Recursion should use distinct target types for active-turn steer, queued follow-up, clarifying-question answer, and status query, each with its own binding and its own decisive negative trace.

**(g) Clarifying questions are durable objects, not blocking calls.** Proposed identity: `question_id + revision + asker actor/lease + goal/task version + answer schema + opened event + expiry + state`, with `OPEN → ANSWERED | DECLINED | EXPIRED | REPLACED | CANCELLED`. `REPLACED` creates a new identity; a delayed answer to the old identity is retained as evidence but cannot satisfy the replacement. Temporal's event-history replay is cited as the durability precedent (event-backed waiter identity), not as a required store.

**(h) Multi-client views keep three acknowledgments separate:** canonical receipt (durable acceptance of event E), presentation receipt (surface C rendered projection E), and semantic acknowledgment (a new attributable authorized action). The second can never manufacture the third. Notification projection runs `canonical append → projection queue → optional coalescing → transport attempt → presentation receipt/cursor`, never transport-first.

**(i) The ten terminal controls cannot be specified.** The supplied brief repeatedly asserts ten accepted terminal controls but does not enumerate or define them. The report deliberately fills a ten-row matrix with explicit `unknown` rather than reverse-engineering names. Cross-cutting contracts that *can* be stated from the brief: a terminal may attach/detach without owning the actor lifetime; a slow or absent view must not block canonical Stop/append/recovery; local and remote views project the same canonical semantics; transport identity cannot replace principal identity.

**(j) Stop modes are defined and made testable:** **Aggressive** (interrupt the selected agent without waiting for a normal boundary), **Full** (the selected actor plus its subagents, shells, and monitors as one scoped action with per-member settlement), and **Lazy** (wait until a named observable current-operation boundary, then stop). Stop completion is never inferred from loss of UI activity; an undetermined pre-interruption external request is shown as `effect outcome unknown`. A `stop_epoch` separates pre-epoch settlements from post-epoch violations.

**(k) Conversation fork, Git worktree, and filesystem snapshot are three different branching primitives** (documented by OpenAI WebSocket docs, Git 2.56.0, and OpenZFS respectively) and must not collapse into one flag. A preserved fork needs a binding record across those layers and must **partition or reserve** the parent allowance, never copy it; the three tests are parent preservation, child separation, and allowance conservation.

**(l) Consultation is an envelope with separate lifetimes.** The proposal fixes identity, causality, requester/recipient with leases, goal/task version, context/evidence grants, expected answer schema, time/expiry, depth/cycle bound, routing as non-authoritative metadata, reservation, and authority class. Lifetimes are separate: request, delivery, answer, adoption, and effect settlement; each arrow produces its own attributable receipt. Adoption re-checks authorized adopter, current lease/generation, GoalSpec/task version, answer revision, expiry, and delegated scope, so a former lease holder's answer can remain useful evidence while being `INELIGIBLE_FOR_ADOPTION`.

**(m) Advice is not handoff.** OpenAI's manager-as-tool versus handoff contrast distinguishes retained control from a specialist becoming active, but the report found no reviewed framework exposing the complete delivery→answer→lease-qualified-adoption→effect-settlement contract. Direct Owner-to-ARM instructions append a canonical event under the Owner's real principal and existing authority; they do not silently create an unrelated goal or widen privacy, spending, credential, publication, or deployment authority, and do not by themselves amend GoalSpec.

**(n) Accessibility and responsiveness are measured separately.** WAI-ARIA `log`, `status`, and `alert` carry different ordering/announcement semantics; WCAG 2.2 requires meaningful focus order and a visible focus indicator. The report turns these into testable requirements (comprehension, keyboard reachability, focus visibility, screen-reader ordering, plain-text parity, input stability, rendering cost, control responsiveness) without inventing numeric thresholds. The truthful activity model exposes engine activity, canonical state, evidence visibility, and transport/view state as four separate dimensions, and never collapses them into "Approved", "Done", or "Owner confirmed".

## Recommendation and falsifier

The report recommends a **resource-enforced, exact-action pre-effect mediation contract** as Recursion's canonical authorization boundary. Upstream prompts, automatic reviewers, approval callbacks, `PreToolUse`-style hooks, model guardrails, and transport confirmations may supply evidence or early denial, but none should independently create a Recursion authorization receipt unless an adapter can bind the decision to the exact effect request and current authority state.

The named competing option is a **harness-centric design** that treats the framework's always-invoked pre-tool hook or approval callback as the definitive gate and trusts the subsequent runtime path.

The recommendation is **decisively falsified** if the harness-centric option can demonstrate, for every supported effecting adapter/resource under fault injection, all of: the resource is unreachable by any hook-bypassing path; approved target/arguments are immutably bound through effect; grant/lease/task changes between decision and effect are revalidated; approval replay cannot re-execute; an automated reviewer can never be mislabeled as the Owner; crash/reconnect/Stop/retry cannot turn uncertainty into duplication; an authoritative resource receipt supplies equivalent settlement; and the added mediation layer adds no independent safety or audit property. If all hold, a separate layer is redundant rather than safer.

## What this does not prove

- It does not prove exactly-once behavior for external services; that depends on each target's transactional/idempotency properties.
- It does not select a database, transaction protocol, IPC, language, topology, transport, sandbox, Git strategy, or filesystem.
- It does not supply the ten omitted terminal-control definitions, nor an exhaustive non-coalescible event taxonomy.
- It reports no live trial, and the synthetic fixtures are acceptance targets, not completed empirical tests.
- Several empirical unknowns stay open: per-adapter Aggressive-Stop boundaries, the Lazy-Stop "observable boundary", which resources can return durable idempotency receipts, external-service post-cancel behavior, remote transport ordering/retry, and screen-reader/performance budgets.

## Open Owner decisions

- The authoritative names and existing semantics of the ten terminal controls.
- The Lazy-Stop boundary per major operation class, and whether Lazy may escalate after a bounded wait.
- Which grants an ARM's current lease holder may adopt routinely under existing delegation versus which always need Owner action.
- The categories and conservation rule of "parent allowance" for a preserved fork.
- Which canonical event classes are forbidden from presentation coalescing.
- Which uncertainty states require immediate Owner notification rather than passive visibility.
- The minimum accessibility/browser/terminal assistive-technology matrix that is an acceptance target.

## Relevance to later waves

- The proposal→valid-decision→effect-attempt→receipt chain and the `unknown` settlement state extend the pause/effect-fencing vocabulary from earlier waves.
- The durable question/waiter state machine and event-backed recovery criteria are testable restoration targets.
- The consultation envelope and adoption re-check are the canonical contract later forwarding, delegation, and advice work must reuse.
- The ten terminal controls are an explicit specification gap: an authoritative accepted-contract artifact is required before that portion can be closed.

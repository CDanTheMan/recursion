---
title: DS-15 — ARM conversations and multi-agent rooms
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not stop at a plan, outline, scope sheet, or clarification request — execute the research now and return the final report.

# DS-15 — ARM conversations and multi-agent rooms

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. Supplying this document is the invocation; it makes no repository or provider call on its own.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Hermes is the executive control plane. Workers are
bounded executors. An implementer's own PASS is never acceptance; independent review is
required, and missing verification is never a pass. `CONTROL_PLANE.md` is the operative
constitution; a research session may propose amendments but must never edit it. No research
session performs implementation, provider/model/authentication/configuration changes,
spending, deployment, publication or merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula,
captures and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs,
pinned source, licenses, peer-reviewed work). Classify every consequential claim as
source-documented, locally observed, inferred or unverified; keep `unknown` distinct from
zero. Model consensus and vendor marketing are not evidence. Every recommendation needs a
competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never
secrets, credentials, personal data, private repository content, local paths, or
account/infrastructure identifiers.

### Lane context

- `#general` is the conceptual direct conversation with the Recursion Head (macro planning, goal scoping, ARM creation, portfolio monitoring and escalation); the name is a presentation default, not a hard-coded protocol identifier. An ARM is a goal-scoped delegated executive with an addressable dedicated conversation, and the Owner may speak to it directly without relaying every message through `#general`.
- Head retains ownership of the overall goal, room membership, authority envelope, conflict resolution, ARM lifecycle and strategic model escalation. A named ARM may hold a bounded, expiring coordination lease for one workflow step. No separate AI "ARM manager" and no new executive tier exists; a shared-room `supervisor` role is not one.
- The accepted coordination lease binds room, workflow step, named holder, participating actor ids, allowed verbs, budget slice, issue/expiry/revocation epochs and a fencing token. It cannot add members, alter GoalSpecs, transfer itself or settle cross-goal disputes, and transcript arrival order is never the tie-breaker.
- Every visible message identifies the speaking logical actor, selected route and GoalSpec. Addressing routes a message but grants no authority; a direct instruction becomes an attributable event under the ARM's existing GoalSpec and cannot silently widen privacy, spending, credentials, publication or deployment authority.
- Telegram is an optional interactive transport, not canonical state. Accepted transport facts: the primary Bot API exposes forum-topic `message_thread_id` and separate new/edited-message updates; its `update_id` changes after a week without updates; incoming updates are retained no longer than 24 hours; long polling and webhooks are mutually exclusive. Free guidance is roughly one message/second in one chat, 20/minute in a group and about 30/second for bulk broadcasts, with paid broadcasts a separate spending capability.
- The referenced public pattern is the official Grok Bot documentation, which defines a Bot as one persistent named agent and says multiple Bots can run in parallel on one user-scoped computer, message each other, share threads or group chats and pass ownership. That is evidence for an interaction pattern, not evidence that shared-computer credentials, transcript-order authority or an unbounded handoff is safe for Recursion.
- Head monitoring and Owner digests derive from canonical state, not transcript scraping. Mute, archive, topic deletion, transport outage or bot-token replacement do not delete the ARM; a compromised or removed transport token affects one capability, not actor identity or canonical state.
- Evidence discipline: a route listing, model response or protocol method name is never evidence of support, and transport limits are dated observations rather than guarantees.

## Purpose

Decide how `#general`, dedicated ARM topics and shared multi-ARM rooms map onto durable actors without introducing an AI ARM Manager. This blocks the accepted v3 interaction contract because topology, addressing and lease semantics determine whether direct Owner-to-ARM conversation ships without creating a hidden executive tier.

## Authority and boundaries

The authority, scope, privacy and evidence-discipline constraints for this lane are restated in `## Baked context` above and govern this work. This prompt authorizes a report only: no runtime, provider, authentication, configuration, spending, deployment, publication or merge action. The accepted interaction-surfaces boundary (interactive CLI as the canonical local surface, Telegram optional, no graphical frontend required for v3, direct owner-to-ARM conversation and bounded coordination leases) is fixed and must not be reopened. Keep public/synthetic briefs free of private project content, transcripts, local paths, credentials or account/infrastructure identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. Identify the exact official Grok Bot public documentation with pinned retrieval dates before any pattern is cited; what does published behavior actually establish?
2. Which official Grok Bot interaction patterns remain usable after rejecting shared ambient credentials, transcript-order authority and a distinct Chief-of-Staff tier?
3. How do durable actors (Head, ARM, worker, verifier, persistent assistant) map onto `#general`, per-ARM topics and shared rooms without adding an AI ARM Manager?
4. Does one bot identity with logical-actor routing, one bot per ARM, or a hybrid give better isolation, credential scope, usability and operational resilience?
5. What are Telegram's current primary-API constraints (forum `message_thread_id`, update retention, update-id reset, polling-versus-webhook exclusivity, per-chat and per-group rate limits), and which constrain the design?
6. How is a command addressed to a logical actor, and how is addressing kept separate from authority so no message widens a GoalSpec?
7. How do shared rooms resolve simultaneous commands, disagreement, cycles and cross-goal budget ownership without transcript order becoming authority?
8. How does the accepted bounded coordination lease (room, workflow step, holder, verbs, budget slice, expiry, fencing token) interact with Head's retained ownership of goal, room membership, authority, conflict, lifecycle and strategic escalation?
9. Which events must Head observe immediately versus summarize into an owner digest, and how is digesting derived from canonical state rather than transcript scraping?
10. How are duplicate, out-of-order and edited/deleted messages normalized, and what recovery applies when a bot token is revoked or replaced?
11. Which public multi-agent orchestration systems expose explicit actor, message, lease and authority models, and what do their documented failure modes show?
12. Does direct Owner-to-ARM conversation measurably reduce owner coordination effort without increasing lost context, contradictory instructions or unreviewed work?
13. What minimum synthetic fixtures prove no chat topology creates a second portfolio executive?

## Deliverable

A source-pinned claim table with classification (fact, inference, unverified), confidence and expiry trigger; options with explicit tradeoffs for each topology; one recommendation tied to a named competing option and a decisive falsifier; and open Owner questions.

## Non-goals

- Do not introduce or recommend an AI ARM Manager or a new executive tier.
- Do not reopen accepted Owner decisions or the accepted interaction-surfaces boundary.
- Do not select a default topology, transport or protocol as a product decision.
- Do not request or include private project content, transcripts, credentials or local paths.
- Do not propose runtime implementation, provider/auth changes, spending or deployment.
- Do not treat a route listing, model response or protocol method name as evidence of support.
- Do not design a rate-limit bypass, paid-broadcast fallback or Telegram policy circumvention.

## Completion gate

- The Grok Bot reference is identified with a pinned URL and retrieval date before use, or it is marked unverified and dropped.
- Every consequential factual claim carries a direct primary source or is explicitly marked unverified.
- Every recommendation names a competing option and a decisive falsifier.
- No Owner decision is reopened and no proposal is promoted into an Owner decision.
- Protected paths are untouched; the output is a report, not an edit.
- A privacy/secret scan of the packet is clean.
- Telegram limits are stated as dated observations, not guarantees.
- The report states which questions remain empirically open and which require Lucas.

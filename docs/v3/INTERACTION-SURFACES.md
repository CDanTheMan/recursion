---
title: Recursion v3 interaction surfaces and collaborative ARM topology
status: accepted-direction-with-open-research
last-updated: 2026-09-03
---

# Recursion v3 interaction surfaces and collaborative ARM topology

## Release surface ruling

Recursion v3 is its own optimized, headless development harness. It owns the durable actor
runtime, goal/delegation protocol, state, routing, context, tools, evidence, policy and
observer contracts even when an individual model turn runs inside an external CLI or agent
loop. Reusing an optimized provider harness is an engine choice, not surrender of Recursion's
product boundary.

The v3 release requires no web, desktop or mobile graphical client. Its owner-facing surfaces
are:

- an interactive Recursion CLI as the canonical local configuration, inspection and control
  surface, including detachable multi-window views;
- Telegram as an optional interactive transport for conversation, commands and monitoring;
- the versioned Observer Interface for read-only automation and future UIs.

Telegram and CLI state are projections over the same actor/event model. Chat history, topic
identity and provider sessions are never canonical task state.

Multiple terminals can attach to Head, an ARM, a worker, a verifier, a communication graph or
system state. Closing a terminal detaches the view without ending work. The persistent daemon
and managed process broker own actors and process trees; deliberate pause/stop/kill commands own
termination. The detailed proposal and research gate are in
[TERMINAL-RUNTIME.md](TERMINAL-RUNTIME.md).

## Accepted conversation topology

### General surface

The conceptual `#general` channel is the direct conversation with Head Hermes. It supports
macro planning, Grill Me, goal scoping, ARM creation, portfolio monitoring and escalation.
The name is a presentation default, not a hard-coded protocol identifier.

Head is the last automated semantic escalation level. A question that remains unresolved
after the final approved Head route is recorded for the owner and included in the configured
digest. Route exhaustion does not fabricate an answer.

### ARM surfaces

An ARM is a goal-scoped delegated executive that achieves its GoalSpec by planning and
delegating a bounded fleet of workers, reviewers and harness sessions. One ARM per repository
is the expected common configuration, not an identity invariant: a goal may span repositories,
and a repository may host serial or explicitly independent ARM runs.

Each active ARM may expose a dedicated Telegram topic or equivalent addressable conversation.
The owner may talk to that ARM without relaying every message through `#general`. An accepted
direct instruction becomes an attributable event under the ARM's existing GoalSpec; it cannot
silently create an unrelated goal or widen privacy, spending, credentials, publication or
deployment authority. A widening instruction is routed through amendment or escalation.

Head remains aware through canonical events and monitoring, not by copying every chat message
into Head's model context. Direct ARM access therefore reduces conversational bottlenecks
without making the ARM independent of the constitutional hierarchy.

## Multi-ARM collaboration hypothesis

The owner wants to investigate a GrokBot-inspired experience in which ARMs appear as
addressable macro-level bots, multiple ARMs can participate in one conversation, and reusable
supervisory workflows coordinate them. The exact GrokBot project, version, source, license and
mechanisms have not yet been identified and must not be inferred from the name alone.

Three topologies should be compared:

1. **Head-routed room:** Head owns the shared conversation lease, solicits named ARM input and
   commits one reconciled transition. This remains the simplest default.
2. **Event-mediated peers:** ARMs exchange typed requests and evidence through the kernel while
   one named ARM may hold a bounded, expiring coordination lease for each cross-ARM workflow
   step. The owner has accepted this topology when the lease cannot change room membership,
   overall goal, authority envelope, conflict policy or ARM lifecycle.
3. **Direct peer delegation:** an ARM delegates to or directs another ARM. This is rejected by
   default unless authority, budget accounting, deadlock handling and one-writer ownership can
   be proved without creating a hidden executive tier.

A workflow `supervisor` may be a temporary coordinator role held by Head or a named ARM inside
one GoalSpec. It is not a new constitutional AI ARM Manager and may not acquire portfolio
authority merely because several actors share a room.

Head retains ownership of the overall goal, room membership, authority envelope, conflict
resolution, ARM lifecycle and a substantial part of strategic model escalation even while a
named ARM holds the step lease. Lease expiry, revocation, PAUSE or conflict returns coordination
to Head without changing actor identity or treating transcript order as a handoff.

## Required interaction semantics

- Every visible message identifies the speaking logical actor, selected route and GoalSpec.
- Addressing syntax and Telegram topics route messages; they do not grant authority.
- Owner messages are preserved byte-exact or by immutable reference before summarization.
- Multi-actor rooms separate proposals, accepted commands, evidence, status and narration.
- Only the current executive lease holder may author an authoritative plan transition.
- Cross-ARM requests carry causation, correlation, source, budget and return-channel identity.
- Mute, archive, topic deletion, transport outage and bot replacement do not delete the ARM.
- Head monitoring and owner digests are derived from canonical state, not transcript scraping.
- A compromised or removed Telegram bot token affects one transport capability, not actor
  identity, credential inventory or canonical state.

## Research and acceptance questions

Before this becomes a construction contract, research must establish:

1. The exact public GrokBot reference and which of its interaction patterns are adoptable,
   adaptable or unsuitable.
2. Telegram forum-topic, multi-bot, permissions, rate-limit, threading and recovery semantics
   at a pinned API version.
3. Whether one bot identity with actor routing or multiple bot identities gives better
   isolation, usability, credential scope and operational resilience.
4. How shared rooms resolve simultaneous commands, disagreement, cycles and cross-goal budget
   ownership without transcript order becoming authority.
5. Which events Head must observe immediately versus summarize for a digest.
6. Whether direct ARM conversation measurably reduces owner effort without increasing lost
   context, contradictory instructions or unreviewed work.

Minimum acceptance requires synthetic multi-ARM conversation fixtures, duplicate/out-of-order
delivery, edited/deleted messages, transport restart, token revocation, PAUSE, GoalSpec
amendment, actor replacement and a proof that no chat topology creates a second portfolio
executive.

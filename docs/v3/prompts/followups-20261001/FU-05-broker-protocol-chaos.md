---
title: FU-05 — Process broker protocol freeze blockers and native chaos matrix
status: ready-for-explicit-invocation
last-updated: 2026-10-01
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# FU-05 — Process broker protocol freeze blockers and native chaos matrix

This is a follow-up to gap G-05 in [GAPS.md](../../research-lane/GAPS.md) and source lane DS-23 (Domain A).

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

- DS-23 returned **conditional adoption, not completion**: adopt the ownership model, preferred
  local transports (Windows named pipes; Linux/BSD pathname `AF_UNIX`), bounded framing, event
  cursors with independent byte and event credit, mandatory `RESET` on a replay gap, durable
  command-id idempotency, creation-time containment and a separate MCP/tool boundary — but do
  not declare the protocol frozen until four blockers and the native chaos matrix pass.
- The four blockers are: (1) exact-version-only `m1b-broker/1` versus a new major with
  version/schema/refusal negotiation; (2) which ratified contract materializes
  `SNAPSHOT.snapshot_digest` into verifiable bytes; (3) cursor rollover/incarnation before the
  2^31-1 bound; (4) normative ACK-release wording (forward contiguous ACK releases, duplicate
  ACK is a no-op, backward ACK is refused).
- It supplied one **locally observed** result, the cluster's only measurement: a bounded Windows
  probe where a create-suspended-then-associate gap let a child escape, while creation-time Job
  listing closed the tested gap. Full descendant-tree termination, slow-client isolation,
  operational framing and current MCP v2 notification/backpressure remain unknown.
- It left open the framing competitor (length-prefixed JCS versus RFC 7464 JSON Text Sequence
  resynchronization) and the MCP numerical bounds, Lazy Stop timeout and command-receipt payload
  schema. This lane consumes the OS fixtures of G-04 and feeds the terminal milestone.
- The detachable-terminal ruling is fixed: terminal bytes are data; attaching a view creates no
  actor, process, model or effect; a slow view must never block the canonical writer.

## Purpose

Produce the decision materials that close the four freeze blockers and the preregistered native
Windows/Linux chaos-matrix specification, so the broker protocol can be frozen or explicitly
held. This is a specification-and-evidence lane: it resolves or narrows each blocker, specifies
the escape-path chaos cases and their stop conditions, and states what would still block the
freeze; it does not implement the protocol and does not select a renderer or serialization
library.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Preserve the current Hermes constitution; propose amendments, never edit it. Public Deep
Research receives only public or synthetic briefs. **DO NOT select a renderer, multiplexer,
GUI toolkit, IPC library, serialization library, cursor store, snapshot format or retention
engine, and DO NOT claim full descendant-tree termination.** Keep the detachable-terminal ruling
and the rule that a view or adapter never enters authority. No socket is opened, no process is
launched and no protected path is written. Do not decide the open Owner questions recorded in
GAPS.md.

## Inputs to read

None. This handoff is self-contained; the prior lane's conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### The four freeze blockers

1. **Version negotiation.** What exactly does exact-version-only rejection cost, and what would a
   new broker major with version intervals, schema epoch/digest, capability sets and typed
   pre-admission refusal require? What is the decisive interoperability fixture that would
   falsify exact-match-only as safe?
2. **Snapshot materialization.** Which already-ratified contract can turn `snapshot_digest` into
   verifiable view bytes at the exact cursor, storage-neutrally, and what is the `HELLO` ->
   `WELCOME` -> gap -> `RESET` -> `SNAPSHOT` -> `ACK` -> `CREDIT` -> `EVENT` recovery oracle?
3. **Cursor rollover/incarnation.** What is the rollover and stream-incarnation rule before
   2^31-1, and how does a client distinguish a legitimate rollover from stale or replayed state?
4. **ACK-release wording.** What is the normative, unambiguous ACK/credit contract (forward
   contiguous ACK releases new pending state, duplicate ACK is a no-op, backward ACK is refused),
   and does credit exhaustion remain reset-requiring?

### Framing, flow control and recovery

5. What is the decision rule between length-prefixed JCS JSON (bounded allocation, torn frame is
   connection failure plus cursor reconnect) and RFC 7464 JSON Text Sequence (in-stream
   resynchronization), and which torn/corrupt-stream cases would falsify the chosen framing?
6. What is the exact per-view credit, bounded pending-state, no-canonical-writer-wait and
   mandatory-`RESET`-on-replay-gap contract, and how is slow-client isolation made measurable
   across transport, frame accumulator, decode, canonical writer, per-view projection and render
   sink?

### Containment chaos matrix

7. What is the preregistered native Windows/Linux chaos matrix of escape paths — process
   birth-time membership, breakaway, privileged cgroup migration, nested/alternate Job behavior,
   external-service-created work, broker death, handle leak, PTY/ConPTY teardown, duplicate
   input, VT injection and daemon restart — with, per case, the injected fault, the observation
   oracle and the stop condition?
8. What is the containment claim that is actually defensible ("all processes remaining inside the
   managed scope are killed"), and what evidence would be required to strengthen it toward full
   descendant-tree capture?

### MCP/tool boundary and Stop

9. What current MCP version pin and numerical bounds apply (partial-line/message buffers, declared
   maximum record, dedicated stderr draining, tool-output caps), and what is the exact
   command-receipt event payload schema for the separate tool broker?
10. What is the Lazy Stop observable-boundary and escalation policy when a boundary never
    arrives, and what is the per-effect deadline/escalation default?
11. What is the false-green rule that a transport ACK proves at most a protocol observation, and
    that a tool result is untrusted evidence rather than authority?

## Deliverable

A source-pinned report containing: a resolution or explicit narrowing for each of the four
blockers with its decisive interoperability fixture; the framing decision rule and its
falsifier; the credit/ACK/RESET contract; the preregistered native Windows/Linux chaos matrix
with per-case injected fault, observation oracle and stop condition; the defensible containment
claim and the evidence needed to strengthen it; the MCP version pin, numerical bounds and
command-receipt schema; the Lazy Stop policy; each recommendation paired with a competing option,
a decisive falsifier and what it does not prove; and the open Owner questions. The protocol
freeze remains conditional unless every blocker and the matrix pass.

## Non-goals

- No selection of a renderer, multiplexer, GUI toolkit, IPC library, serialization library,
  cursor store, snapshot format or retention engine.
- No claim of full descendant-tree termination.
- No protocol implemented, socket opened, process launched or fixture executed by this session.
- No byte-exact cross-implementation interoperability claim without the fixtures.
- No reopening of the detachable-terminal ruling or the rule that views and adapters are never
  authority.
- No decision of the open Owner questions in GAPS.md.
- No modification of a protected path.

## Completion gate

- Each of the four blockers is resolved or narrowed to a named decision input, with a decisive
  interoperability fixture.
- The framing decision names its competitor and the torn/corrupt-stream falsifier.
- The credit/ACK/RESET contract is normative and unambiguous, and credit-exhaustion behavior is
  stated.
- The chaos matrix names every escape path, injected fault, observation oracle and stop
  condition, and is explicitly preregistered.
- Containment is stated as membership/completeness-limited, and no full-tree termination claim is
  made.
- The MCP version is pinned, numerical bounds are stated, and the command-receipt schema is
  specified.
- The protocol freeze remains conditional and the no-selection outcome for renderer and
  serialization is preserved.
- Protected paths are untouched; privacy and secret scan are clean.

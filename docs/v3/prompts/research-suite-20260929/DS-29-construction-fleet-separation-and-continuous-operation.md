---
title: DS-29 — Construction fleet separation and continuous operation
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not stop at a plan, outline, scope sheet, or clarification request — execute the research now and return the final report.

# DS-29 — Construction fleet separation and continuous operation

This is a bounded construction handoff, not a public Deep Research brief. Supplying this document is the invocation; it makes no repository or provider call on its own. This handoff is self-contained context for a repository-execution task; it is not a Deep Research session. It prepares the exact packet that would build the continuous WSL-based construction service.

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

- Recursion v3 is a provider-neutral agent platform with one small deterministic kernel and typed adapters. Persistent, goal-scoped assistants are organized as Head -> ARM executives -> bounded workers, with no separate AI "ARM manager". The terminal (CLI, optional Telegram) is the interactive surface, and Windows/Linux operation and recovery are required; a graphical frontend is not required.
- Construction-system separation is an accepted principle: temporary tools used to build v3 (an overnight codex lead, implementation swarms, a model-powered watcher, or particular subscription arrangements) belong in a construction runbook. The product exposes generic engines, nodes and observers and must not hard-code the construction campaign into the release.
- Continuous-operation requirements CW-01 through CW-18 are the recorded construction-fleet requirement set: one task authority and a durable outbox; durable fenced execution with leader election, a monotonically increasing incarnation token and unknown-execution retention at every effect boundary; host lifetime, watchdog and bounded downtime; a shared client protocol (CLI, MCP, remote tunnel); authenticated collaboration and idempotency; central child admission and an allowed-tool subset; immutable batches versus rolling admission; one attempt worktree per worker; executable task packets, lifecycle states, a persistent evidence dossier and research depth; independent acceptance that binds actual tool calls, command exits, hashes, coverage, failures and cleanup; adaptive capacity, worker slots, reserved verifier capacity and host headroom; event-driven supervision, quota-window rollover and per-provider account records; bounded recovery, backoff, circuit breakers and unknown retention; context-continuity checkpoints; serialized integration, review publication, a durable publication key, reachable steering, honest status and Stop/PAUSE; and the preregistered five-slot versus eight-slot acceleration comparison. Each requirement must map to a named runtime scenario and an implementation phase.
- Implementation phases are labeled P1 through P8 in the recorded construction plan. This packet covers P1 and P3 through P8. P2 (service access) remains assigned to its own packet, and the product-frontier and recovery-ledger work are separate packets that this packet must not duplicate.
- Execution-fabric context: admission is hierarchical and adaptive across node, pool, route, model, repository, goal and review capacity. It reserves OS/controller headroom, queues work when the appropriate quality route is unavailable, prevents overlapping writers, serializes integration per repository, protects verification and recovery capacity, applies backpressure before throttling/lag/branch proliferation, uses event-driven wakeups rather than polling, and permits an audited owner override. Branch/worktree backlog limits are measured and configurable with an explicit owner hard ceiling, not a universal number.
- Worker and integration flow: an ARM task node -> exclusive worktree plus immutable WorkPacket -> eligible native/external route -> normalized checkpoint/result -> controller-owned machine gate -> clean independent verification package -> evidence-based dispute resolution -> serialized integration candidate -> publication intent -> approved review branch. Verifiers receive the GoalSpec, exact tree, diff, gates and observable evidence, but not the implementer's persuasive narrative or hidden reasoning. Disagreement is resolved by discriminating evidence, not model majority vote.
- Routing, capacity and billing: a route is an immutable combination resolved from independent declarations (engine, provider, model, capacity pool, credential reference, execution mode). Capacity pools are model- and account-aware and use confidence-aware shadow prices for opaque flat subscriptions, never fictional dollar prices. Switching from a subscription/OAuth route to a metered API route is a billing-authority transition requiring existing parent-goal authorization; metered fallback for the private deployment is one aggregate parent-goal budget, not a per-task allowance.
- PAUSE and effects: the operative PAUSE is immediate halt; `checkpoint` is a selected future default that stays non-operative until the exact constitutional amendment is applied. Distributed effects are never assumed exactly once; the posture is idempotency keys, prepare/execute/reconcile states, leases with expiry and fencing tokens, authenticated result receipts and a crash matrix. Stop/PAUSE never becomes a finish-the-task mode, and Lucas alone merges.
- This is a construction handoff, not a research lane: it requires repository execution (isolated worktree, branch, commits, machine-checkable gates) and independent exact-candidate verification. Prohibited: enabling a service, schedule, route, spend or standing autonomy; host lifecycle/startup/sign-out/reboot changes; auth/credential/config/PAUSE changes; provider or paid calls; push/publication/merge; product language/store/framework selection; protected-path edits; reopening completed M1 work or recorded Owner decisions OR-021 through OR-039; and any 24/7 availability or concurrency claim from a stdio or synthetic demo.

## Purpose

Specify the first bounded construction packet for separating the construction fleet from the product runtime and for the continuous-operation requirements CW-01 through CW-18, covering implementation phases P1 and P3 through P8. This is blocking because the construction facility must never be hard-coded into the v3 release, and because no 24/7 availability, quota rollover, fenced execution or acceptance claim may be made until each requirement has a named runtime scenario and a machine-checkable gate.

## Authority and boundaries

The shared authority constraints are in `## Baked context`. Preserve the current constitution; write proposed amendments, never edit it. This packet is proposed: it does not enable a service, route, spend, cron entry or standing autonomy. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication, push or merge is authorized. Do not select a product language, store or framework. Do not reopen completed M1 work or recorded Owner decisions (OR-021 through OR-039). P2 (service access) remains assigned to its own packet, and this packet must not duplicate the product-frontier packet or the recovery-ledger packet. This is a construction task, not a public Deep Research session: it requires repository execution (isolated worktree, branch, commits) and independent exact-candidate verification. Public Deep Research receives only public or synthetic briefs; this construction packet may reference repository paths but must never export private content, transcripts, credentials or account identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Fleet separation and product boundary

1. How is the construction tooling separated from the product runtime so the release exposes only generic engines, nodes and observers, and what artifact proves the construction campaign is not hard-coded into the product?

### Continuous-operation requirements CW-01 through CW-18

2. For CW-01 and CW-02, how do one task authority and a durable outbox couple execution transitions back to canonical tasks, and how does durable fenced execution use leader election, a monotonically increasing incarnation token and unknown-execution retention at every effect boundary?
3. For CW-03, CW-04 and CW-05, how are host lifetime, watchdog, bounded downtime, the shared client protocol (CLI, MCP, remote tunnel), authenticated collaboration and idempotency specified so closing a client cannot terminate the scheduler and a stale revision returns conflict?
4. For CW-06 and CW-07, how do central child admission, the allowed-tool subset, immutable batches versus rolling admission, and one attempt worktree per worker prevent double claims and uncontained desktop results?
5. For CW-08 and CW-09, how are executable task packets, lifecycle states, the persistent evidence dossier, research depth and suspension of non-novel lanes specified without a timer that kills an admitted experiment?
6. For CW-10, how does independent acceptance bind actual tool calls, command exits, hashes, coverage, failures and cleanup, and how does same-family or missing-verifier work block rather than pass?
7. For CW-11, how are adaptive capacity, worker slots, reserved verifier capacity and host headroom admitted as the minimum of host, provider, task-independence, command, verification and Owner ceilings?
8. For CW-12 and CW-13, how do event-driven supervision and deterministic checks batch advisor requests, and how do the standing envelope, quota-window rollover and per-provider account records work without paid fallback or reset-credit redemption?
9. For CW-14 and CW-15, how are bounded recovery, backoff, circuit breakers and unknown retention combined with context-continuity checkpoints that preserve source, authority, budget, gate and unresolved evidence?
10. For CW-16 and CW-17, how are serialized integration, review publication, a durable publication key, reachable steering, honest status and Stop/PAUSE behavior specified so Lucas alone merges and PAUSE never becomes a finish-the-task mode?
11. For CW-18, how is the five-slot versus eight-slot acceleration comparison preregistered with matched tasks, quality rubric, error bounds and uncertainty before any concurrency increase?

### Tool broker, sandbox and job schema

12. How do the tool broker and allowlist prevent ambient host shells, undeclared MCP servers, recursive delegation and writable credential mounts?
13. What command sandbox bounds apply (four machine-wide slots, 60-second commands, 2 GiB per slot, 64 PIDs, two CPU cores, 1 MiB output cap, 64 MiB scratch), and how are descendant cleanup and output-limit responses recorded?
14. How does `write_file` persist only exact allowed paths, require the previous content digest and enforce the 30-changed-file cap?
15. How does the job schema `allowed_tools` refuse during preparation or initialization before provider launch when the list is absent, and how does the broker write a denial receipt for any disallowed tool call?
16. How does Grok advisory supervision return evidence-bound continue, inspect or stop-for-review advice with no authority to accept research, modify workers, renew policy, launch descendants or publish?
17. How do 20-worker batches charge exactly once through the immutable charged attempt directory and use the separate supervision lock to observe running workers?

### Canary, soak and acceptance matrix

18. What one-worker then five-worker canary and 72-hour soak gates must pass on the actual host, and what fresh isolation, identity, receipt, resource and cleanup evidence is required?
19. What acceptance matrix maps every CW requirement to specific runtime scenarios and an implementation phase, and how is a requirement kept unimplemented or unrun rather than marked complete by a demo?
20. How does this packet keep P2 as the assigned service-access packet, cover only P1 and P3 through P8, and avoid duplicating the product-frontier and recovery-ledger packets?

## Deliverable

A machine-checkable construction packet specification: the frozen predecessor commit, worktree and branch; allowed new paths and protected-path exclusions; the fleet-separation boundary; a CW-01 through CW-18 requirement-to-scenario map; the P1 and P3 through P8 phase plan with exit conditions; the tool-broker and allowlist policy; the command-sandbox and `write_file` bounds; the job-schema `allowed_tools` refusal rule; the denial-receipt and bounded tool-call budget; the Grok advisory-supervision boundary; the 20-worker batch charging and supervision-lock behavior; the canary and soak gates; the acceptance matrix; and the independent-review and no-push/no-merge boundary. It is a proposed packet, not an executed service.

## Non-goals

- No enabling of a service, schedule, route, spend or standing autonomy.
- No push, publication or merge to any branch.
- No provider, model, network or paid call.
- No host lifecycle, startup, sign-out or reboot change.
- No PAUSE, auth, credential or configuration change.
- No product language, store or framework selection.
- No duplication of the P2 service packet or the product-frontier and recovery-ledger packets.
- No 24/7 availability or concurrency claim from a stdio or synthetic demo.
- No modification of protected paths or existing specifications.
- No self-review presented as independent verification.

## Completion gate

- The predecessor commit, worktree, branch and allowed paths are frozen and machine-checkable.
- The construction fleet is separated from the product runtime with a stated proof.
- Every CW-01 through CW-18 requirement maps to at least one runtime scenario and one phase.
- P2 is left to its assigned packet, and this packet covers only P1 and P3 through P8.
- The tool broker, allowlist and command-sandbox bounds are explicit and closed.
- `write_file` exact-path, previous-digest and 30-file cap behavior is specified.
- Job-schema `allowed_tools` refuses before provider launch, and denial receipts consume a bounded budget.
- Grok advisory supervision is stated as advisory with no authority.
- The canary and 72-hour soak gates and the acceptance matrix are specified.
- Protected paths are untouched, independent review is recorded, and no push or merge occurs.

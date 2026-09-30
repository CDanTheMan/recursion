---
title: DS-30 — Multi-project supervision state and durable memory
status: proposed-inert
last-updated: 2026-09-29
parent-goal: goal-recursion-v2-execution-fabric
invocation: only after Lucas explicitly invokes this file in a new session
---

**Session query — explicit invocation.** Execute research handoff `DS-30` now. This query is the explicit invocation by the Owner; the `proposed-inert` label on the brief below describes the file at rest, not this run. Do not ask which topic to research, do not request further authorization, and do not treat the attached brief as an inert document. What file and directory convention lets one operator plus unattended agents keep durable, diffable state for 4+ concurrent projects, so work resumes across context loss and blocked, stale and waiting-for-decision conditions are visible rather than inferred? Produce the deliverable and check every item of the completion gate.

# DS-30 — Multi-project supervision state and durable memory

This is an inert Deep Research handoff. It launches nothing, authorizes no provider call, write, spend or configuration change, and is inert until Lucas explicitly invokes this file in a new session. Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. It covers supervision state and durable memory, not market or alpha research.

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

- Recursion v3 is a provider-neutral agent platform whose runtime keeps durable, goal-scoped state for one operator plus unattended agents. Persistent, goal-scoped assistants are organized as Head -> ARM executives -> bounded workers, with no separate AI "ARM manager"; workers are bounded executors and an implementer's own PASS is never acceptance.
- The supervision problem: one operator plus unattended agents must keep durable, diffable state for 4+ concurrent projects so work resumes across context loss and blocked, stale and waiting-for-decision conditions are visible rather than inferred. A convention that becomes a second source of truth silently stales and reads exactly like working state.
- Accepted transport: git is the transport and a `state/` tree is the current durable operating-state location. D-017 is the recorded decision that the repository uses a git-based `state/` tree for durable, diffable status. The recommendation must be additive to that layout rather than replace it, and git-derived fields (fetch result, HEAD, dirty tree, branch) are never hand-copied.
- Existing disciplines to reconcile with: the repository keeps a D-entry decision log with, by rule, every decision carrying a falsifier and a monthly first-of-month review cadence; the state tree also carries a morning-brief discipline. The owner's kill criteria and review throughput live in the anchor/scope document. The recommendation must not replace the decision log or the morning-brief discipline.
- Ambient architecture: the Head compiles strategic GoalSpecs and monitors outcomes; an ARM owns a goal-scoped plan/DAG and delegates bounded work; workers execute one bounded WorkPacket and do not reinterpret the parent goal. Ordinary runtime work requires no continuous model inference; deterministic process, deadline, quota and receipt checks provide continuous awareness, and model supervision is advisory and responds to actionable events.
- Conditions to represent: blocked, stale and waiting-for-decision must be distinct and diffable. Staleness signals (age, last-fetch commit, heartbeat age, missing artifact checksum) must classify a project, and each signal's false-positive source must be named. A "waiting for a decision" state must correlate to the exact owner question and next action so the same escalation is not appended repeatedly.
- Guardrails: unattended loops need guardrails against runaway loops, retry storms, context bloat and duplicate side effects. Scheduling options to compare are cron/batch, event-driven, and persistent daemon, judged on state persistence, handoff, crash recovery and cost for unattended overnight operation. Supervisor/worker escalation must be structured even when the supervisor itself is the degraded component.
- Memory context: long-horizon memory architectures include retrieval-augmented, summary hierarchies, vector or graph stores, and file-based memory; each has measured failure modes (drift, contradicted facts, lost provenance, unbounded growth). Retrieval and indexing for 4+ project histories must avoid cross-project leakage and context blowup, and a wrong retrieval must be detected rather than trusted. Published memory evaluations report errors on knowledge updates, temporal recall and abstention.
- Research constraints: this is a public/synthetic lane and receives no private project content, transcripts, local paths or credentials. It must not reopen accepted Owner decisions, the anchor scope, git-as-transport or PAUSE behavior; must not select a language, store or framework; must not perform runtime/daemon/scheduler/database implementation; must not run provider/model/route calls or a benchmark; and must not present an invented schema, threshold or numeric budget as a requirement. Market, investment and alpha research are out of scope.

## Purpose

Decide the file and directory convention by which one operator plus unattended agents keep durable, diffable state for 4+ concurrent projects, so work resumes across context loss and blocked, stale and waiting-for-decision conditions are visible rather than inferred. This is blocking because Recursion already committed to git-as-transport and a `state/` tree (recorded decision D-017); a convention that becomes a second source of truth silently stales and reads exactly like working state. The research must reconcile with, not replace, that layout and the unattended-loop requirements already established for it.

## Authority and boundaries

The shared authority constraints are in `## Baked context`. Preserve the current constitution; write proposed reconciliation, never edit it. Public or synthetic briefs only — never private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. Do not reopen accepted Owner decisions or anchor scope, and do not select a language, store or framework. Git-as-transport and the live-clone model are fixed context to reconcile against, not options to reopen.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### File-convention state and context-loss survival

1. Which file conventions (CLAUDE.md, AGENTS.md, per-repo status files, JSON/YAML state) have documented survival of context loss, and what exactly survives a fresh session versus only a compacted one?
2. What minimum fields must a state record carry so a fresh agent can reconstruct current task, gate, authority, next action and unresolved evidence without a transcript?
3. Where have file-convention approaches silently staled in real repositories, and what signal distinguished stale from quiet-working state at the moment it was missed?

### Structured versus freeform state and diffability

4. In documented solo or small-team setups, does schema-checked structured state reduce resume error versus freeform prose, and when does structure itself become maintenance debt?
5. Which state fields can be derived from git (fetch result, HEAD, dirty tree, branch) so they are never hand-copied, and which genuinely cannot live in git?
6. What diffable representation of task status lets an agent mechanically detect change between two cycles without re-reading every document?

### Representing blocked, stale, and waiting-for-decision

7. How are blocked, stale and waiting-for-decision distinguished from each other so an unattended loop neither re-asks an answered decision nor silently proceeds past one?
8. What staleness signals (age, last-fetch commit, heartbeat age, missing artifact checksum) reliably classify a project, and where does each produce false positives?
9. How is "waiting for a decision" correlated to the exact Owner question and next action so the same escalation is not appended repeatedly?

### Retrieval and long-horizon agent memory

10. Which long-horizon memory architectures are documented (retrieval-augmented, summary hierarchies, vector or graph stores, file-based memory) and what measured failure modes do they report: drift, contradicted facts, lost provenance, unbounded growth?
11. In published memory evaluations, what do agents get wrong about knowledge updates, temporal recall and abstention, and does any of that transfer to repository supervision?
12. What retrieval and indexing strategy keeps 4+ project histories searchable without cross-project leakage or context blowup, and how is a wrong retrieval detected rather than trusted?

### SRE monitoring for a one-person operation

13. Which SRE patterns (heartbeat, staleness alert, error budget, runbook, blameless postmortem, golden signals) translate to a one-person multi-project operation, and which assume an on-call rotation that does not exist?
14. How is silent degradation — a loop that runs but makes no verified progress — detected without continuous model inference, and what false-negative remains?

### Unattended loop architecture and guardrails

15. Compare scheduling (cron/batch), event-driven, and persistent daemon architectures on state persistence, handoff, crash recovery and cost for unattended overnight operation.
16. What guardrails appear in working unattended-agent setups against runaway loops, retry storms, context bloat and duplicate side effects?
17. How should supervisor/worker escalation be structured when the supervisor itself may be the degraded component?
18. What do published operator post-mortems of unattended agents report as root causes, and which are preventable by state convention versus only by runtime containment?

### Recommended convention for 4+ concurrent projects

19. Given `state/` and git-as-transport, what convention is additive rather than a parallel source of truth, and what example schemas serve a single operator supervising 4+ concurrent projects?
20. What concrete observable falsifies the recommended convention — for example a stale blocker rendered as current, an agent re-asking an answered decision, or state that cannot be diffed across two commits?

## Deliverable

- A source-pinned claim table (claim, source, version/date, classification as fact/inference/hypothesis/proposal, confidence, expiry or falsifier trigger).
- Comparison matrices for file-convention versus structured state, and for cron versus event-driven versus daemon, with every unmeasured cell marked unknown.
- A recommended file and directory convention with example schemas for 4+ concurrent projects, shown as a reconciliation that reuses `state/` and git-derived status rather than replacing them.
- One recommendation tied to a named competing option and a decisive falsifier.
- Open Owner questions listed separately.

## Non-goals

- No market, investment or alpha research.
- No runtime, daemon, scheduler, database or storage implementation.
- No language, store or framework selection.
- No reopening of git-as-transport, PAUSE behavior or anchor scope.
- No private project content, transcripts, local paths or credentials in any public packet.
- No provider, model or route calls, and no benchmark executed.
- No invented schema, threshold or numeric budget presented as a requirement.
- No replacement of the existing D-entry decision log or the morning-brief discipline.

## Completion gate

- Every factual claim is pinned to a primary source with version or retrieval date, or marked unverified.
- The recommended convention is explicitly additive to `state/` and git-derived state, and names what it does not duplicate.
- Blocked, stale and waiting-for-decision each have a distinct, diffable representation.
- Unattended-loop guardrails cover runaway loops, retry storms, context bloat and duplicate effects, each with a falsifier.
- Silent-degradation detection is proposed with its known false-negative stated.
- Every unmeasured matrix cell is marked unknown rather than assumed.
- Every recommendation names a competing option and a decisive falsifier.
- Open Owner questions are listed and no decision is promoted into an Owner decision.
- No protected path is edited and no runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge effect occurs.

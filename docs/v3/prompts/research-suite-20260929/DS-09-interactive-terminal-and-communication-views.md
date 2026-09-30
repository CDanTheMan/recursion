---
title: DS-09 — Interactive terminal and communication views
status: proposed-inert
last-updated: 2026-09-29
parent-goal: goal-recursion-v2-execution-fabric
invocation: only after Lucas explicitly invokes this file in a new session
---

**Session query — explicit invocation.** Execute research handoff `DS-09` now. This query is the explicit invocation by the Owner; the `proposed-inert` label on the brief below describes the file at rest, not this run. Do not ask which topic to research, do not request further authorization, and do not treat the attached brief as an inert document. What persistent process, client protocol and rendering architecture supports several detachable Head/ARM/worker views with clean termination, negligible passive overhead and causal communication visualization? Produce the deliverable and check every item of the completion gate.

# DS-09 — Interactive terminal and communication views

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. This file is inert until Lucas invokes it; reading or creating it launches nothing and authorizes no provider call, write, or effect.

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

- Recursion v3 is a provider-neutral agent platform with a small deterministic kernel, typed adapters, native and upstream execution, and a persistent daemon plus managed process broker. Its local surface is an interactive, detachable CLI; Telegram is optional and no graphical frontend is required for v3.
- `Head` is the single portfolio executive beneath Lucas; an `ARM` is a goal-scoped delegated executive that plans and delegates a bounded fleet of workers and verifiers; workers are bounded executors. There is no separate AI "ARM manager". A `GoalSpec` is the immutable, versioned statement of goal plus authority.
- Accepted product ruling: the v3 CLI is interactive and supports several simultaneous terminal windows or panes showing Head, ARM, worker, verifier and system activity. Closing a terminal detaches that view; it does not terminate the actor, goal, external engine or daemon. A deliberate control command ends, pauses or kills work. This ruling is fixed and is not reopened here.
- Topology vocabulary: terminal windows are views, not process owners; a daemon owns canonical state and actor leases; a process broker owns external CLI, PTY/ConPTY and tool process groups; the versioned local client protocol carries HELLO, WELCOME, SNAPSHOT, EVENT, ACK, CREDIT, INPUT, RESIZE and RESET. Attaching a view must not launch an additional model, plugin or indexer.
- Platform terms: Windows ConPTY is the UTF-8/VT pseudoconsole transport and a Job Object is the process-scope kill/accounting boundary, with `PROC_THREAD_ATTRIBUTE_JOB_LIST` for creation-time containment; Linux uses a PTY plus session/foreground process groups, with cgroup v2 or `clone3(CLONE_INTO_CGROUP)` as a stronger descendant/resource boundary. Git Bash/MSYS2 and Neovim's embedded terminal are distinct high-priority compatibility cases, not synonyms for the native OS stacks.
- Lane `R11` (interactive terminal runtime and communication visualization) asks which persistent process, client protocol and rendering architecture can support several detachable Head/ARM/worker views with clean termination and negligible passive overhead. It blocks the terminal runtime contract until native Windows and Linux prove attach/detach, flow control, cursor replay and full descendant-tree termination.
- `PERF-010` is the terminal-view experiment: 0, 1, 5, 10 and 20 passive views under idle and high-output loads, recording p50/p95/p99 input and frame latency, CPU, RSS, wakeups, IPC bytes, queue high-water marks, coalesced presentation frames, process/handle counts and canonical append delay. A design fails if views multiply model/worker calls, block canonical writes, cause unbounded memory, corrupt input, lose durable events or turn detach/reconnect into relaunch.
- Communication visualization direction: two coordinated views (a stable actor/work graph; a selected causal event or message stream), color never the sole encoding, and a shared multi-ARM room that shows logical identity and GoalSpec without merging private contexts.
- Evidence discipline: classify claims as source-documented, locally observed, inferred or unverified; no renderer, multiplexer, IPC encoding or terminal application is selected as a product default until measured.

## Purpose

Decide the persistent process, client protocol and rendering architecture that supports several detachable Head/ARM/worker views with clean termination and negligible passive overhead, plus causal communication visualization. Agenda lane R11 blocks the terminal runtime contract until native Windows and Linux prove attach/detach, flow control, cursor replay and full descendant-tree termination.

## Authority and boundaries

The authority, scope, privacy and evidence-discipline constraints for this lane are restated in `## Baked context` above and govern this work. This prompt authorizes a report only: no runtime, provider, authentication, configuration, cron, PAUSE, spending, deployment, publication or merge action. The product ruling that terminals detach rather than end work is fixed; this lane compares mechanisms and may not reopen it. Keep public/synthetic briefs free of private project content, transcripts, local paths, credentials or account/infrastructure identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. Which creation-time ownership primitive gives true descendant-tree termination on Windows (ConPTY plus a Job Object via `PROC_THREAD_ATTRIBUTE_JOB_LIST`) and on Linux (PTY plus session/process groups, with cgroup v2 or `clone3(CLONE_INTO_CGROUP)` for stronger scope), and where do breakaway, migration or alternate creation escape it?
2. How do attach, detach and reconnect preserve cursors and actor identity without relaunching a process or an effect?
3. What bounded flow-control and credit design guarantees a slow or absent client cannot block the canonical writer or drop durable events, while presentation frames may coalesce?
4. How do IPC authentication, protocol versioning and capability negotiation prevent a local terminal from gaining more authority than the active operator and GoalSpec?
5. Which TUI diff-rendering approach minimizes flicker, preserves typed input during background output, and handles Unicode width, resize and high-output bursts?
6. How are Git Bash/MSYS2 PTY translation and Neovim embedded-terminal behavior distinguished from native Windows and Linux stacks, and what tests graduate them?
7. Which multi-session failure modes (daemon restart, provider or node loss, orphaned grandchildren, PAUSE/kill races) must be reproduced, and what are their acceptance stop conditions?
8. How do service supervision options on each OS interact with graceful, force and emergency stop without silently restarting killed work?
9. For communication visualization, how should a stable actor/work graph and a selected causal event or message stream coordinate without merging private contexts or relying on color alone?
10. What plain-text and accessibility fallback proves the interface remains usable for screen readers and unsupported terminals?
11. How are stream cursors, replay floors, snapshot installation and RESET-on-gap specified so reconnect repairs a projection without relaunching effects?
12. What is the minimum PERF-010 matrix (0, 1, 5, 10 and 20 passive views under idle and high-output loads), and which measurements decide acceptance?
13. Which candidate implementation choices (renderer, multiplexer, IPC encoding) must remain unselected until measured?
14. What negative trace proves a design fails: terminal close kills work, a passive view launches execution, a slow client blocks canonical state, or the daemon cannot terminate its full descendant tree?

## Deliverable

A source-pinned report with: a claim table (claim, source, version/date, classification, confidence, expiry trigger); a process, IPC, flow-control and compatibility matrix; a preregistered cross-platform test plan including the PERF-010 view matrix; communication-view wireframes; a recommendation tied to a named competing option and decisive falsifier; and open Owner questions. No implementation is selected as a product default.

## Non-goals

- No runtime or terminal implementation.
- No selection of Zellij, tmux, Ratatui, crossterm or xterm.js as a product default.
- No OS terminal application made mandatory.
- No reopening of the accepted detachable-terminal product ruling.
- No claim of full descendant-tree termination before measured across the OS matrix.
- No graphical frontend work.
- No provider, model or route calls.
- No multiplexer or shell session established against any work.

## Completion gate

- Primary platform sources pinned by version/date (Microsoft pseudoconsole and Job Objects, Linux cgroup v2, POSIX.1-2024 terminal and kill, SSH RFC 4254).
- Each rejection criterion has a specified negative trace.
- The 0/1/5/10/20 view matrix and its stop conditions are preregistered.
- Native Windows and Linux are mandatory, with Git Bash/MSYS2 and Neovim as distinct high-priority cases.
- Accessibility and plain-text fallback are covered.
- Every recommendation names a competing option and a falsifier.
- Protected paths are untouched; privacy and secret scan are clean.

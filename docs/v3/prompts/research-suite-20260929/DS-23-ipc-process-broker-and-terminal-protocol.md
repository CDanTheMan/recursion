---
title: DS-23 — IPC process broker and terminal protocol
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-23 — IPC process broker and terminal protocol

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. Supplying this document is the invocation; it makes no repository or provider call on its own.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone harness and harness orchestrator; Hermes is a retired control plane and an optional upstream integration. Workers are
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

- Recursion v3 is a headless harness; the interactive CLI is its canonical local operator surface and Telegram is an optional transport. Several terminal clients may attach to Head, ARMs, workers, events or system state, and closing a client does not own or end the underlying process.
- The accepted product ruling is that terminals detach rather than end work; terminal bytes never carry canonical authority, and attach/detach must not create a model turn, process, actor or effect.
- `E-FHAR2-104` is the terminal/process broker contract: the Recursion broker — not the PTY, renderer or view — owns process identity, startup epoch, containment, event cursors, input/resize leases, recovery and fanout. Its wire message set is `HELLO`/`WELCOME`/`SNAPSHOT`/`EVENT`/`ACK`/`CREDIT`/`INPUT`/`RESIZE`/`RESET`.
- `E-FHAR2-103` is the log/projection/artifact/IPC profile: length- or RS-delimited frames with maximum size, version/capability handshake, request ID, actor/lease/epoch binding, ACK cursor and byte/event credit; a full reader is disconnected or reset and cannot block the canonical writer.
- Cursor units are UTF-8 bytes for raw data or a distinct event sequence, never host-language string length. Zero clients does not stop draining; each view has a bounded credit queue; exactly one fenced input lease exists; and a gap requires `RESET` before any further `EVENT`.
- The privileged kernel is four pure functions (`decode`/`admit`/`reduce`/`derive_work_packet`) with no filesystem, network, process or provider access; adapters and views call the boundary and must not move into it.
- `R11` is the interactive-terminal and communication-views research base (also DS-09). Milestone 6 delivers detachable multi-window terminal views and persistent daemon/process-broker attachment.
- `E-FHAR2-102` defines the neutral kernel API and the CPython/Rust/Go experiment `EXP-FHAR-10`; `PERF-010` is the experiment that several detachable views stay responsive without multiplying worker/model cost.
- **UNRESOLVED, Owner-owned:** the renderer, terminal multiplexer, GUI toolkit, IPC library, serialization library and physical cursor/snapshot/retention store are unselected.

## Purpose

Decide and freeze the versioned wire protocol between thin terminal views, the `recursion` daemon and the managed process broker, including transport, peer authentication, framing, cursors/resume, flow control, reconnect idempotency, process containment, the MCP/stdio bridge and the tool broker, before any renderer, multiplexer or IPC library is selected. It is blocking because `E-FHAR2-103`/`104` and the R11 lane require attach/detach, replay and full descendant-tree termination on native Windows and Linux, and because an unstated framing or cursor rule would let a slow view block the canonical writer or a reconnect duplicate an effect.

## Authority and boundaries

The authority, scope and privacy constraints that govern this lane are restated in `## Baked context`; treat them as the operative limits. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. This lane may not select a product renderer, terminal multiplexer, GUI toolkit or IPC library; Zellij, tmux, Ratatui, crossterm and xterm.js are replaceable presentation or transport dependencies, not selections. The accepted product ruling that terminals detach rather than end work is fixed and may not be reopened. Terminal bytes never carry canonical authority; attaching a view must not create a model turn, process, actor or effect. This lane performs no session establishment, port binding, socket connection or process launch.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Transports and peer authentication

1. For each candidate transport — Unix domain socket (`AF_UNIX`), anonymous and FIFO pipes, Windows named pipes, and loopback TCP — what exact peer-authentication primitive is available (Linux `SO_PEERCRED`, BSD/macOS `getpeereid`, `SO_PASSCRED`/SCM_CREDENTIALS, Windows named-pipe impersonation via `ImpersonateNamedPipeClient` plus `GetNamedPipeClientProcessId`, or a bearer token), and which transports cannot prove the peer's user identity at all?
2. On Windows, how do named-pipe security descriptors, `PIPE_REJECT_REMOTE_CLIENTS`, message versus byte mode, and per-connection impersonation interact, and what is the negative fixture where a remote or lower-integrity client obtains a broker channel it must not have?
3. On Linux, what do `SO_PEERCRED` UID/GID/PID values actually guarantee across namespaces (`SCM_CREDENTIALS`, user namespaces, `pidfd`), and where can a same-UID but wrong-process peer still connect?
4. If loopback TCP is ever used as a fallback, what authenticated handshake (mutual key, installation trust root, per-session nonce) is required so an unprivileged local process cannot impersonate a view or the daemon, and should loopback TCP be rejected outright for a local-only authority domain?
5. How are socket/named-pipe files created with restrictive permissions (directory mode, `umask`, ACL, `SO_PEERSEC`/SELinux or AppArmor context), and what is the exact refusal when an endpoint already exists, is a symlink, is world-writable, or is stale from a crashed daemon?

### Framing, version negotiation and capabilities

6. For each framing candidate — length-prefixed binary, newline-delimited JSON, RS (RFC 7464) delimited JSON, gRPC, Cap'n Proto and MessagePack — what are the exact maximum-frame, partial-frame, canonicalization and control-character-handling rules, and which candidate is cheapest to make deterministic and diffable across independent implementations?
7. What `HELLO`/`WELCOME` handshake binds protocol major/minor, schema epoch, broker incarnation/epoch, stream ID, requested cursor, dimensions and capability set, what typed refusal applies to an unknown major, a downgraded minor or an unhonorable capability, and how does negotiation prevent a view from requesting a capability the active operator's GoalSpec does not hold?
8. For text payloads, how is canonical encoding (UTF-8, JCS for JSON, no host-language string-length cursor units) enforced so cursor units never depend on a host's internal string representation, and how does the protocol treat raw terminal output as untrusted data that can never become a broker command under ANSI/OSC/DCS/control-sequence or alternate-screen injection?

### Flow control, cursors, resume and reconnect idempotency

9. What exact credit model (`CREDIT(bytes, events)`) and `ACK(cursor)` semantics bound each view's queue, and how are cursor units defined per stream (UTF-8 bytes versus a distinct event sequence) so monotonic advance, non-backward ACK and exact-once-per-event delivery are proven while a slow or dead client is disconnected at its last cursor without blocking the canonical writer or dropping durable command/lease/process-exit events?
10. How is a replay gap detected and repaired — `HELLO(requested_cursor)`, `WELCOME(replay_floor, snapshot_cursor)`, mandatory `RESET(reason=GAP, snapshot_cursor)`, fresh credit, then the next `EVENT` — and what is the negative trace where a non-RESET continuation is accepted after a gap?
11. How do snapshot-versus-stream semantics and the reset rule differ, and how is a missing snapshot, retention-floor loss, or SDK loss-detection failure reported as a typed refusal rather than an invented event?
12. How does reconnect preserve actor identity and cursor state without relaunching a process or replaying a non-idempotent effect, how are `INPUT(command_id, process_epoch, input_lease, bytes)` and `RESIZE(command_id, process_epoch, resize_lease, columns, rows)` made idempotent under duplicate delivery, and how are half-close, abrupt disconnect and daemon restart kept distinct so none is read as process death?

### Daemon-owned processes, containment and watchdog

13. How does the broker—not the PTY, renderer or view—own process identity, startup epoch, parent process group, worktree/route binding, cancellation capability and recovery policy, and how are these reconciled after a daemon restart?
14. What are the exact Windows and Linux containment primitives and their escape cases — `PROC_THREAD_ATTRIBUTE_JOB_LIST` at creation, Job Object child/breakaway flags, `CREATE_BREAKAWAY_FROM_JOB`, alternate creation paths, PTY plus session/foreground process group, `setsid()`, cgroup v2 or a systemd scope, `clone3(CLONE_INTO_CGROUP)`, cgroup migration and `pidfd` identity — and how is membership verified before a process is resumed?
15. How does the watchdog detect orphaned, reparented, escaped, hung or zombie descendants, and what is the fault matrix for broker death at creation, association, registration and immediate-child boundaries?
16. For Aggressive/Full/Lazy Stop and the ten terminal controls, how are offered input, accepted command, installed recipient fence, delivered cancellation, owned termination and external settlement reported as separate dispositions, and what proves a kill cannot trigger an unnoticed supervisor restart?

### Views, rendering, MCP bridge and the tool broker

17. How does one active input/resize lease coexist with several passive detachable views, and what prevents a second view from duplicating execution, inference, a model turn or a subscriber's effects?
18. Which scrollback, bounded-history retention and non-flicker diff-rendering requirements can be specified at the protocol layer (stable viewport, changed-cell updates, bounded/coalesced presentation frames, preserved typed input) without choosing a renderer, and which remain renderer tests?
19. How should the MCP bridge and stdio integration be specified so MCP notifications cannot be evicted before application ingestion, the stdio line buffer is bounded, inline handlers cannot deadlock the pump, and missing authoritative facts are reported as explicit unknown rather than invented settlement?
20. What is the tool-broker contract (allowed-tool list, per-call check, denial receipt, output cap, descendant cleanup, charged budget), how does it stay distinct from the terminal view channel, and what cross-platform parity and chaos/fault matrix (kill, hang, flood, half-close, version skew, torn frame, slow client, orphan grandchild, daemon restart, PAUSE/kill race, concurrent config edit) must be preregistered with per-case stop conditions and pinned OS build, kernel, terminal, shell, renderer, Unicode data, locale and dimensions?

## Deliverable

A source-pinned report containing: a claim table (claim, source, version/date, classification, confidence, expiry trigger); a transport-by-authentication matrix with unknown cells explicitly `unknown`; a byte-level wire protocol specification for `HELLO`/`WELCOME`/`SNAPSHOT`/`EVENT`/`ACK`/`CREDIT`/`INPUT`/`RESIZE`/`RESET` including frame bounds, cursor units, version/capability negotiation and refusal types; a flow-control and slow-client-isolation proof obligation set; a process-containment matrix with named escape cases; a watchdog and Stop-mode disposition model; an MCP/stdio and tool-broker contract; a preregistered cross-platform chaos/fault test matrix; and a recommendation tied to a named competing framing/transport option with a decisive falsifier plus open Owner questions.

## Non-goals

- Do not select a renderer, multiplexer, GUI toolkit, IPC library or serialization library.
- Do not establish a socket, pipe, port or named-pipe session, or launch any process.
- Do not reopen the accepted detachable-terminal product ruling.
- Do not give a view, adapter or terminal canonical authority or input authority beyond the active operator.
- Do not choose a physical cursor store, snapshot format or retention engine.
- Do not claim full descendant-tree termination before the OS matrix is measured.
- Do not treat a transport acknowledgment as semantic compliance or external settlement.
- Do not collapse Aggressive/Full/Lazy Stop into one cancel or remove any of the ten controls.
- Do not include private project content, transcripts, local paths or credentials in any public packet.

## Completion gate

- Primary platform sources are pinned by version/date (Microsoft pseudoconsole and Job Objects, Linux cgroup v2 and pidfd, POSIX.1-2024 terminal/kill, RFC 4254, RFC 7464).
- The transport matrix states an authentication primitive or an explicit "no peer identity" for every transport.
- Framing, maximum frame, partial-frame and refusal rules are specified at byte level.
- Cursor units, gap detection, mandatory RESET and reconnect idempotency are specified with negative traces.
- Process containment names at least one escape case per primitive, with a membership-verification rule.
- Slow-client isolation proves the canonical writer cannot be blocked or lose durable events.
- A chaos/fault matrix is preregistered with per-case stop conditions and pinned platform versions.
- Every recommendation names a competing option and a falsifier.
- No protected path is edited and no runtime/provider/auth/cron/PAUSE/spending effect occurs.
- Open Owner questions are listed separately and no research recommendation is presented as a decision.

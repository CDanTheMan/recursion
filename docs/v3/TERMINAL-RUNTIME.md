---
title: Recursion v3 interactive terminal and persistent session runtime
status: accepted-direction-with-open-research
last-updated: 2026-09-03
---

# Recursion v3 interactive terminal and persistent session runtime

## Product ruling

The v3 CLI is interactive, not only a collection of one-shot commands. It must support several
simultaneous terminal windows or panes showing Head, ARM, worker, verifier and system activity.
Closing a terminal detaches that view; it does not terminate the actor, goal, external engine
or daemon. A deliberate control command ends, pauses or kills work according to policy.

This terminal experience is the v3 visual foundation. A later graphical frontend should be a
new client of the same versioned observer/control protocols, not a rewrite of runtime state or
actor semantics.

## Process and view topology

```text
Telegram topic     Terminal: #general     Terminal: ARM A     Terminal: worker/gate
      |                     |                    |                     |
      +---------------------+--------------------+---------------------+
                                    |
                        versioned local client protocol
                                    |
                              recursion daemon
             actor leases | events | policy | routing | terminal broker
                 |                 |                    |
           canonical state   bounded live streams   managed process groups
                 |                                      |
          Head / ARM runs              external CLI, worker, verifier, tool process
```

Terminal windows are views, not process owners. Actor identity, model sessions, work and
messages survive client attach/detach. One actor may have several attached views, and one
terminal may display several actors. The runtime must not launch another model or indexer merely
because a second view attaches.

## Architecture alternatives

1. **Daemon plus thin terminal clients — recommended.** Recursion owns actor/process lifetime,
   IPC, event cursors and recovery; any terminal can attach. This is portable and gives a future
   GUI the same protocol, but makes daemon/process-broker correctness critical.
2. **Terminal multiplexer as runtime.** Build directly around tmux, Zellij or an OS terminal
   application's panes. This is fast to prototype and inherits mature detach behavior, but makes
   one external UI/process model a product dependency and complicates Windows/Linux parity.
   Multiplexers remain useful optional view-launch adapters.
3. **One actor process per terminal.** Simple mental mapping, but terminal close kills or
   orphans work, duplicate views duplicate execution, and recovery becomes shell-specific.
   Reject as the canonical architecture.

## Candidate interactive views

- **General:** Head conversation, active goals, ARM summaries, escalations and owner digest.
- **ARM focus:** direct conversation, GoalSpec, plan/checkpoints, child graph, blockers, budget
  and route.
- **Worker/session:** streamed model/tool output plus exact task, process and worktree identity.
- **Communication graph:** actors and current typed requests, with selection opening the
  corresponding event/message stream.
- **Event/log:** filtered canonical and operational events with correlation and causation.
- **System:** resource pressure, route/pool state, leases, PAUSE, quarantines and process tree.

An OS terminal window, tab or pane may host any view. `recursion workspace open` may propose or
launch a saved layout through an optional terminal-integration adapter, but the product must
also work through ordinary independent terminals and remote shells.

## Interaction model

The default full-screen experience should combine command entry with streaming status and
conversation. One-shot commands and a line-oriented fallback remain available for scripts,
screen readers, unsupported terminals and incident recovery.

Candidate commands include:

```text
recursion                         # attach to general interactive view
recursion attach head
recursion attach arm <id>
recursion attach task <id>
recursion workspace open [layout]
recursion view graph|events|system
recursion detach
recursion daemon status|start|stop|restart
recursion arm pause|stop|kill <id>
```

Names are provisional. The interactive command language, one-shot CLI and Telegram commands
must compile into the same authenticated command schema. Typing in a terminal does not gain
more authority than the active operator and GoalSpec.

## Persistence and termination

The daemon owns canonical state and actor leases. A managed process broker owns external CLI,
PTY/ConPTY and tool process groups. Each process records actor, task, route, worktree, start
epoch, parent process group, cancellation capabilities and recovery policy.

- Client disconnect or terminal close: detach only; persist the last acknowledged stream
  cursor and continue the actor under policy.
- Daemon restart: recover canonical state, reconcile process/remote observations, and never
  relaunch an ambiguous external effect blindly.
- Graceful stop: close admission, request a safe checkpoint, enforce a deadline, then report
  any process or effect that did not terminate.
- Force stop: use the platform process-tree primitive, revoke leases, quarantine uncertain
  outputs and preserve enough evidence to explain the interruption.
- Emergency stop: block new effects independently of whether an interactive client is open.
- Uninstall or service shutdown: must not leave unmanaged descendants; failure to prove process
  ownership is a visible blocker.

Persistence must remain lightweight. Detached output is bounded and stored by retention class;
slow or absent terminals cannot backpressure the canonical writer or cause unlimited buffers.

### Versioned client protocol

The requirements contract is ready to freeze around a daemon epoch and monotonically
increasing per-stream cursor. Wire encoding and numeric limits remain experimental.

```text
HELLO    protocol version, client/actor/stream, last epoch/cursor, dimensions, capabilities
WELCOME  epoch, stream, replay floor, snapshot cursor, input lease, negotiated capabilities
SNAPSHOT current terminal state and modes at one durable cursor
EVENT    epoch, cursor, class, actor/task/process identity, payload
ACK      last accepted cursor
CREDIT   bounded byte and event allowance
INPUT    idempotent command id, active input lease, raw bytes
RESIZE   idempotent command id, active resize lease, columns and rows
RESET    replay gap, current snapshot and new cursor
```

One active lease owns input and resize; other clients are passive readers. The process broker
drains PTY output even with no clients. Each client has bounded queues and explicit credit.
Presentation frames may be coalesced, but command, lease, process-exit, termination and
canonical state events may not be dropped. A slow client disconnects with its final cursor and
later receives replay or `RESET + GAP`; reconnect never relaunches a process.

### Native process boundaries

- Windows uses ConPTY as the UTF-8/VT byte transport and a restrictively secured local IPC
  endpoint. A Job Object is the primary process-scope kill/accounting boundary, but breakaway
  and alternate creation paths are explicit negative fixtures. Microsoft documents that the
  pseudoconsole host is responsible for display and input; this does not make ConPTY the actor
  or process owner.
- Linux uses a PTY plus session/foreground process groups for terminal semantics, with a cgroup
  v2 or systemd scope as the stronger descendant and resource boundary and pidfds where
  available. `setsid()`, cgroup migration and privilege boundaries are negative fixtures.
- SSH, tmux, Zellij, Git Bash/MSYS2 and Neovim are clients or adapters. None is canonical
  process identity. Zellij resurrection may rerun commands, and Neovim session restoration may
  restart terminal jobs; both behaviors must be distinguished from broker reconnection.

The platform evidence supports these primitives, not the unqualified claim that every child
can be contained. “Full-tree termination” is an acceptance result obtained from the supported
OS matrix.

## Configuration in the terminal

The TUI renders from the same versioned configuration schema as files and one-shot commands.
It shows effective value, provenance, allowed values, affected actors, application lifecycle
(`live`, `checkpoint-applied`, `restart-required` or new GoalSpec) and a before/after diff.

Interactive editing never makes terminal widget state canonical. An accepted change is an
authenticated command and event. Concurrent terminals either observe the committed new version
or receive a typed stale-version conflict; last-keypress-wins behavior is forbidden for policy.

Saved terminal layouts contain view and presentation preferences, not credentials, authority or
actor state. Layout configuration may be local/private and portable separately from runtime
configuration.

## Non-flicker and quality requirements

The interactive CLI should be calmer and more legible than common repaint-heavy agent CLIs:

- update only changed cells/regions rather than clear and redraw the whole terminal;
- use a stable viewport, explicit scrolling and bounded/coalesced progress events;
- preserve typed input while background events arrive;
- prevent interleaved worker output from corrupting prompts or each other;
- render stable actor/route/task labels and make unseen activity explicit;
- handle resize, Unicode width, color capability, reconnect and high-output bursts;
- respect reduced-motion/color/accessibility settings and provide a plain-text mode;
- keep canonical logs complete even when live presentation samples repetitive deltas;
- measure input latency, frame time, CPU, wakeups, memory and dropped/coalesced events.

Animation and decoration are subordinate to fast comprehension. Streaming reasoning is not
required, and hidden chain of thought is never treated as a display or recovery dependency.

## Communication visualization recommendation

Use two coordinated representations rather than forcing everything into one transcript:

1. a stable actor/work graph showing Head, ARMs, children, leases and typed in-flight requests;
2. a selected actor or correlation stream showing conversation, command, evidence and status
   events in causal order.

Color alone must not encode actor or state. Cross-window selections can share a durable view
cursor, but view cursors never affect execution. A shared multi-ARM room presents each speaker's
logical identity and GoalSpec; it does not merge their private contexts.

## Research requirements

The v3.0 portability gate covers native Windows and Linux terminal stacks. The exact initial
application matrix must be chosen from measured behavior, but it must include the Windows
ConPTY/Job Object path and the Linux PTY/session/process-group path with at least one maintained
native terminal on each OS. Compatibility breadth beyond that behavioral floor may ship later.

Git Bash is a distinct Windows/MSYS2 shell-and-PTY translation case, and Neovim is an embedded
terminal/editor client rather than an operating-system terminal. Both are high-priority research
targets, along with other popular terminals, but must pass attach/detach, input, resize, process
ownership and plain-text tests before being listed as supported. Popularity does not justify a
compatibility claim that leaves work orphaned or input corrupted.

Before freezing the contract, compare primary specifications and implementations for:

- Windows ConPTY, Job Objects, process groups and Windows Terminal control/integration;
- POSIX PTYs, sessions/process groups/signals and common service supervisors;
- tmux, Zellij and detachable-session persistence models;
- mature terminal UI diff renderers, event loops, accessibility and resize behavior;
- agent CLIs' transcript, streaming, subprocess, resume and multi-session failure modes;
- IPC authentication, stream cursors, flow control and bounded buffering;
- terminal layout portability without making an OS terminal application mandatory;
- Git Bash/MSYS2 translation and Neovim embedded-terminal behavior, plus a documented path for
  adding later compatibility profiles without changing canonical actor/process semantics.

Required experiments include attach/detach storms, terminal crashes, daemon restart, orphan and
grandchild processes, high-output workers, resize/Unicode tests, slow clients, simultaneous
configuration edits, PAUSE/kill races, Windows/Linux parity, resource soak and a screen-reader
plain-text workflow. The acceptance decision must include failure evidence, not only a polished
demo.

The minimum `PERF-010` matrix uses 0, 1, 5, 10 and 20 passive views under idle and high-output
loads. It records p50/p95/p99 input and frame latency, CPU, RSS, wakeups, IPC bytes, queue
high-water marks, coalesced presentation frames, process/handle counts and canonical append
delay. The contract fails if views multiply model/worker calls, block canonical writes, cause
unbounded memory, corrupt input, lose durable events or turn detach/reconnect into relaunch.

Primary platform anchors opened 2026-09-03 are Microsoft
[pseudoconsole](https://learn.microsoft.com/en-us/windows/console/pseudoconsoles) and
[Job Object](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
documentation, Linux kernel [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html),
POSIX.1-2024 Issue 8 [terminal](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap11.html) and
[`kill`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/kill.html) specifications,
and [SSH connection protocol](https://www.rfc-editor.org/rfc/rfc4254.html). Their applicability
is limited by the declared platform version and actual isolation available to the broker.

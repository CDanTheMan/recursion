---
title: Recursion v3 interactive terminal and persistent session runtime
status: accepted-direction-with-open-research
last-updated: 2026-09-07
---

# Recursion v3 interactive terminal and persistent session runtime

## Observed Windows launch gap — 2026-09-07

IPR-001: the bounded Windows probe reproduced the create-suspended-before-association gap.
The observed live child was outside the operation Job and survived broker death. The
`PROC_THREAD_ATTRIBUTE_JOB_LIST` treatment placed the child in that Job at creation; observed
children terminated when broker death closed its last handle. Later association and ordinary
descendant checkpoints also terminated their observed children. An independent outer safety
Job contained every experiment and was empty after cleanup.

Disposition: use supported creation-time containment as the Windows launch candidate, with
membership verification before resume and explicit refusal on association failure. This result
does not cover a crash inside the OS call, alternate launchers, hostile escape, Job breakaway,
registration/reconciliation, remote effects or Full Stop. The at-birth created/associated
checkpoints repeat the same membership boundary; they are not two independent mechanisms.
Linux cgroup launch and remote recovery remain separate admissions. The test's Windows Job
around a WSL client alone does not prove Linux cleanup; successful Hermes runs additionally
observed the owned Linux namespace's exit.

## Mark 3 comparison: birth containment and control progress - 2026-09-07

PTYs carry terminal data; they do not define canonical ownership or Full Stop. Compare Windows
Job Objects and Linux delegated cgroup scopes with independently admitted restart suppression.
The inspected node-pty and portable-pty kill/session paths do not prove complete owned-subtree
settlement. Job breakaway, escaped processes, alternative creation and missing delegation remain
explicit failures or admission blockers. CMP-002, CMP-004.

Compare post-creation association with supported containment-at-birth APIs: Windows
PROC_THREAD_ATTRIBUTE_JOB_LIST and Linux clone3(CLONE_INTO_CGROUP). Crash the broker at creation,
association, registration and immediate-child boundaries; require no child or an identifiable
contained child. Closing the last kill-on-close Job handle has an execution policy consequence
separate from detaching a view. No host/build or process behavior was tested here. CMP-025.

Control reserve must survive every stage: external ingress, framing/byte cap, transport window,
read pump, callback scheduler, canonical writer and view projection. The pinned MCP Python SDK
can evict vendor notifications before application ingestion, and its partial stdio-line buffer
has no observed local size cap. Inline handlers can deadlock the pump. Require queryable event
sequence/gap repair or explicit unknown for missing authoritative facts; never invent lost
settlement. A slow log consumer can block a Windows pipe writer, so freeze sink/drain behavior
in headless/TUI comparisons. CMP-020.

Expose offered input, accepted command, installed recipient fence, delivered cancellation,
owned termination and external settlement separately. Reconnect repairs projections and
subscriptions; it does not relaunch effects or certify offline termination. Required ten
controls, Aggressive/Full/Lazy Stop, preserved forks and input/resize leases are retained by
the [comparison probes](foundation-research/mark2-research/mark3-comparison/probes.json).

## Mark 3 multiplexed interaction and control — 2026-09-07

OR-038 requires persistent attachable views over durable work, including the questionnaire
assistant/Head exchange. Multiple windows or clients must not duplicate execution or inference.
Compare per-view cursors, bounded projections and replay/snapshot recovery; protect control
delivery from slow rendering, disconnected views and bulk history replay. Input ownership,
operation identity, causation and receipt state must be visible.

Owner participation, steering and Aggressive/Full/Lazy Stop remain distinct across sessions and
configured nodes. An acknowledgment is not remote settlement; retain partition and external
effect ambiguity. Measure Unicode/render correctness, accessibility, input tail latency,
attach/detach/reconnect and time to understand state and issue the intended control.

Source-audit counterexamples reinforce the need for composed control mappings: Pi queues may
survive RPC abort; Hermes busy-input redirection may preserve foreground work in background;
a host can answer an ACP approval without a human prompt. See SRC-V3-226, SRC-V3-227 and SRC-V3-228 and
[the bounded source audit](foundation-research/mark2-research/mark3/companion-review.json). These are unrun
adapter tests, not a new Stop definition or installed-build certification.

## Mark 2 control contract — proposed 2026-09-07

The ten controls remain required across the platform. The canonical command includes command ID,
target task/session/attempt/turn, expected epoch/config revision, authority and delivery policy.
Persist acceptance before presentation; report received, delivered, settled, rejected or uncertain
as distinct dispositions. A transport acknowledgment never proves semantic compliance.
MKR-011/MKR-012; [feature-level source bindings](foundation-research/mark2-research/compatibility.json).

| Control | Observable contract and decisive negative trace |
|---|---|
| streaming | Ordered task/turn events with bounded client credit; slow client receives replay or RESET + GAP without blocking canonical writes |
| questions | Durable question ID, target waiter, expiry and answer/cancel; reconnect or delayed answer cannot target a replacement question |
| approvals | Exact action/arguments/scope and current grant; reuse valid prior authorization, reject stale or changed-action replies |
| queued_messages | Durable enqueue/edit/remove before delivery; crash after dispatch before acknowledgment cannot duplicate input |
| active_steering | Target current attempt/turn and report actual delivery; queued follow-up remains explicitly different |
| interruption | Distinct Stop mode/scope plus admission fence; report surviving or uncertain work |
| resume | Validate checkpoint, effective config, route, grants and unsettled effects before continuation |
| forks | Preserve original unfinished work and separate derived version; conserve parent allowance and disclose chosen timing |
| compaction | Inspect/request/tune only supported transforms; retain directives, waiters, evidence and fallback rehydration |
| commands_plugins | Namespace, supplying component, schema/config revision and authority visible; reject collisions and lossy behavior claims |

| Stop mode | Boundary and scope | Required evidence |
|---|---|---|
| Aggressive | Forcefully interrupt selected agent without waiting for its current operation; fence further selected-agent dispatch | Local termination/control observation and uncertain in-flight effects; descendants are listed separately, not silently included |
| Full | Stop selected agent and its owned subagents, shells, monitors and relaunchers; scope is a rooted ownership set | Every local owned process settled or reported unresolved; remote hosts need separate receipts |
| Lazy | Close admission and stop at the next observable current operation boundary (tool completion, protocol turn boundary or validated checkpoint) | Boundary identity and deadline; waiting/timeout visible, configured escalation explicit |

Aggressive can sacrifice the current operation. Full also fences supervisors and returning workers
so killing a PID cannot cause an unnoticed restart. Lazy never measures hidden reasoning or
claims an invisible train of thought completed. These future controls do not change current
immediate operational PAUSE. A shared server may own unrelated sessions: revoke the selected
session's capability and use a documented session primitive; killing unrelated work is not an
automatic consequence of Full. If containment cannot isolate the requested scope, report it.

Windows Job Objects and Linux cgroup v2 are candidate process/accounting boundaries, with
breakaway, alternate process creation, cgroup migration and privilege escape as negative traces.
systemd restart policy must be fenced through its owner, not only its main PID. MCP/ACP cancel,
Codex interrupt and socket closure are protocol observations; none proves external rollback.
Remote acceptance without receipt remains ambiguous under M1C, forbidding duplicate retry.
SRC-V3-172 through SRC-V3-179; MKR-011.

A preserved fork records source HEAD, index, tracked dirty bytes, scoped untracked/ignored
artifacts, context/evidence/config revision, source cursor, lineage and budget split. Acquire a
cooperative snapshot boundary or validate a repeated manifest around capture; a changed source
forces retry/refusal of that snapshot, not a universal dirty-tree ban. Treat symlinks, binaries,
submodules, large/ignored files and excluded secrets explicitly. No cleanup, stash push,
truncation or merge is implied. Preserve an anchored immutable snapshot before derived writes.
Conversation fork, worktree creation and filesystem snapshot are three distinct operations.
SRC-V3-144/SRC-V3-195/SRC-V3-206/SRC-V3-207.

The configured notice-before or disclosure-and-review-after policy records source state,
capture boundary, preserved original and derived paths, exclusions and subsequent divergence.
A sibling receives a separately reserved share, not a copy of the parent's allowance.
Probes must demonstrate original bytes unchanged, coherent context/artifact binding, duplicate
command idempotency and rejection of stale leases under concurrent edits.

## Engine process and remote-operation distinctions

Native Windows/Linux remain acceptance targets. Broker-owned processes, daemon-owned canonical
state and detachable views are already specified; attaching a view must not require another
model request. Terminal bytes do not establish structured turn identity, billing completeness,
effect mediation or rollback. A restricted passthrough route cannot silently replace a governed
adapter. Preserve separate process/daemon, stream cursor, input lease and canonical fence domains.
FND-003/FND-004.

Current upstream documentation includes Codex remote operation on connected Windows/Mac hosts.
Cursor Remote Control, Cloud Agents and My Machines have different start/host requirements.
Observe, attach, resume, steer, start, approve and unattended boot need separate capability records.
Sleeping hosts, stream loss and partial descendant termination remain explicit fault cases;
reconnection alone does not reauthorize work. See [compatibility](foundation-research/compatibility.json)
and `experiment.foundation.remote`. FND-013.

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

1. **Daemon/broker plus thin terminal clients — ratified ownership boundary, implementation unselected.** Recursion owns actor/process lifetime,
   IPC, event cursors and recovery; any terminal can attach. This is portable and gives a future
   GUI the same protocol, but makes daemon/process-broker correctness critical.
2. **Terminal multiplexer as runtime.** Build directly around tmux, Zellij or an OS terminal
   application's panes. This is fast to prototype and inherits mature detach behavior, but makes
   one external UI/process model a product dependency and complicates Windows/Linux parity.
   Multiplexers remain useful optional view-launch adapters.
3. **One actor process per terminal.** Simple mental mapping, but terminal close kills or
   orphans work, duplicate views duplicate execution, and recovery becomes shell-specific.
   Reject as the canonical architecture.

Pinned implementation review supports the first option's ownership boundary without selecting
an implementation: Zellij supplies
the strongest inspected bounded multi-client/fair-writer pattern; tmux supplies live
consumer-offset backpressure; Ratatui plus crossterm is the leading native Rust renderer/input
candidate; and xterm.js is the leading browser renderer/accessibility candidate. Each remains a
replaceable presentation or transport dependency. Exact revisions and gaps are registered in
[SOURCE-REGISTER.md](SOURCE-REGISTER.md#frontier-harness-campaign-sources).

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
The canonical event is appended before a presentation queue may coalesce or drop anything; a
renderer queue is never the durable log. Queue exhaustion must leave owner control and recovery
capacity available.

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

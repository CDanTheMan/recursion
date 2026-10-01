# DS-09 — interactive terminal and communication views (synthesis)

## Provenance

- Raw: `raw/ds-DS-09-terminal-communication.md`.
- Session: Wave B Deep Research, self-contained handoff, run 2; retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved from the report: **source-documented** (Microsoft Win32/Console, Linux kernel and man pages, POSIX/Open Group, RFC 4254, Unicode, W3C, and official MSYS2/Neovim/systemd/Ratatui documentation), **inferred** (the protocol and ownership contracts), **unverified** (Recursion's future cross-platform containment guarantee), and **no locally observed runtime claims**.
- Fixed premise: terminal windows are detachable views, not process owners; closing a view detaches it while work continues. No renderer, TUI library, multiplexer, terminal application, IPC serialization, or product default is selected.
- All claims are attributed to "the report's sources"; no new facts, URLs, or selections are added. Nothing is presented as run.

## The question

Which architectural contracts must be tested before the terminal runtime can be unblocked, given that a daemon, process broker, several detachable terminal views, and external actor processes must coexist on Windows and Linux? The report reframes detach/reconnect, process containment, flow control, IPC identity, rendering, compatibility (Git Bash/MSYS2, Neovim), accessibility, and the PERF-010 0/1/5/10/20-view experiment as invariants to freeze before implementation.

## Key findings

- **Four responsibilities (inferred).** The daemon owns canonical actor state, identities, leases, durable event order, authorization, and reconnect state; the process broker owns PTY/ConPTY handles and external process containment; the client owns only a projection and transient presentation state; and an OS containment primitive — not the PTY — is the emergency process-tree boundary.
- **Windows containment (source-documented).** The strongest candidate is a non-breakaway Job Object with the process placed at creation time via `PROC_THREAD_ATTRIBUTE_JOB_LIST`; descendants inherit by default and a non-breakaway nested job can retain membership. Breakaway flags and `Win32_Process.Create` are documented exceptions, so the defensible guarantee is "all processes remaining inside the managed job scope are killed," not capture of arbitrary delegated launches. ConPTY stays the UTF-8/VT I/O transport only.
- **Linux containment (source-documented + inferred).** PTY plus POSIX session/foreground process groups provide job-control and signalling semantics but not containment, since new sessions/process groups can be created. A non-threaded cgroup v2 domain scope is the stronger boundary: kernel 6.7 `cgroup.kill` recursively `SIGKILL`s the cgroup tree, handles concurrent forks, and is protected against kill-time migration; `clone3(CLONE_INTO_CGROUP)` closes the create-then-migrate race. Migration via `cgroup.procs` is security-sensitive, so containment must be coupled with launch-authority policy. `cgroup.freeze` is not Recursion's semantic `PAUSE`.
- **Ownership vs transport, and pause/kill ordering (inferred).** `PAUSE` should first be a canonical control-plane state — revoke new effect/input authority and quiesce the actor — before any OS freezer is used as an aid. The robust ordering is canonical intent first, OS effect second: append the accepted command, advance/revoke the actor lease generation, reject stale-generation input, then perform graceful or emergency process action. This does not make remote/provider effects cancellable.
- **Reconnect and two cursors (inferred).** A **stream cursor** identifies the last applied canonical event sequence; a **terminal cursor** is broker-maintained emulator state. The broker must keep draining and interpreting PTY/ConPTY output at zero attached views, or detached output can fill the pipeline and influence the child. A reconnecting view gets a `SNAPSHOT` (identity, grid/modes/cursor, projection state) plus ordered `EVENT`s; if its cursor is below the replay floor or schema-incompatible, the server issues `RESET` and a fresh snapshot. `HELLO`/`WELCOME`/`SNAPSHOT`/replay/`RESET` must never trigger actor, process, or model execution.
- **Bounded flow control (source-documented pattern + inferred use).** RFC 4254's per-channel byte window and `WINDOW_ADJUST` are the precedent for per-view explicit credit. A zero-credit client simply stops receiving and must never backpressure the canonical append path; durable events stay in canonical retention while presentation frames may coalesce. This is what prevents many stalled views from becoming unbounded memory queues.
- **IPC identity above OS identity (source-documented + inferred).** On Linux, a pathname `AF_UNIX` socket in a private runtime directory plus `SO_PEERCRED`; on Windows, a named pipe with a restrictive security descriptor and a checked impersonation. OS mechanisms establish who connected, not what the connection may do; `WELCOME` returns the intersection of server capabilities, authenticated operator authority, GoalSpec authority, and current actor state/lease, and unknown mutating features fail closed.
- **Rendering and Unicode (source-documented + inferred).** A retained screen model with one terminal writer, frame coalescing, and diff output is the candidate; a double-buffer/diff architecture is cited as a practical example, not a selected dependency. Full repaint is the competing approach to be measured. Input editor, graph labels, and truncation should use Unicode 18.0 extended grapheme clusters; `East_Asian_Width` alone does not determine actual terminal cell width, so widths must be tested on real terminals.
- **Input/resize arbitration (inferred).** One PTY has one input stream and one canonical geometry, so a single renewable terminal-control lease should authorize one view at a time to send `INPUT` and authoritative `RESIZE`; stale or non-holder requests are rejected, not merged. Read-only views may resize only their local presentation.
- **Compatibility is separate (source-documented).** Git Bash/MSYS2 is a translation environment, not native ConPTY, and cannot inherit a native Windows pass. Neovim's embedded terminal is a libvterm-based emulator, and its session restoration restarts the terminal command — so a restored client must attach to the existing actor, not recreate work. Neither is a process owner.
- **Communication views and accessibility (inferred + source-documented principle).** Two coordinated projections of the same authorized metadata: a stable actor/work graph and a selected causal event stream, carrying stable event IDs, sender/receiver identities, GoalSpec identity, and causal references. Shared rooms hold references, not private-context concatenation, and color must not be the sole carrier of state; a negotiated plain-text append-only mode is the accessibility and degraded-terminal baseline.
- **Preregistered test program (inferred).** Native Windows and Linux are release-blocking; MSYS2 and Neovim are separate high-priority lanes; every rejection criterion has a machine-readable negative trace; and the PERF-010 0/1/5/10/20-view matrix measures idle and high-output workloads on both native lanes. The report's numeric gates are provisional, inferred engineering thresholds, not product SLAs, and the central rule is zero tolerance for semantic coupling between view count and execution count.
- **Service supervision (source-documented + inferred).** systemd and the Windows SCM can track and restart the daemon, but child actor work should not become an implicitly auto-restarting OS service; a deliberate actor kill must be durably recorded as desired state before process termination so recovery does not silently recreate the killed generation.
- **Instrumentation (inferred).** Every PERF-010 run must record exact OS build/kernel, terminal host, shell, daemon/client builds, renderer and IPC candidates, Unicode-width version, CPU/memory configuration, and test seed; an unrecorded platform version counts as `unknown`, not a default. Measured quantities include input/frame latency percentiles, canonical append latency, CPU/RSS, wakeups, IPC bytes, per-view queue high-water, coalesced frames, ACK lag, credit outstanding, and reset counts.

The report's rejection criteria each map to a machine-readable negative trace; representative cases include:

- closing a view ends work;
- attaching a view launches actor/model/plugin/indexer execution;
- a zero-credit client stalls the canonical append or grows without bound;
- durable events are lost to presentation coalescing;
- detach/reconnect replays an effect or creates a new actor generation;
- a stale cursor is treated as continuous instead of repaired by `RESET` plus snapshot;
- an in-scope descendant survives emergency kill, or a workload migrates itself out of its cgroup/job;
- required state or controls exist only spatially or by color.

## Recommendation and falsifier

The report recommends freezing semantic invariants before implementations: durable canonical append isolation; daemon/broker ownership; OS-scoped containment; stable actor and lease identities; snapshot/event replay with an explicit replay floor; bounded per-view credit; fail-closed capability negotiation; one active input/resize lease; semantic communication views; and plain-text accessibility. It then selects no library or default and compares named candidates (renderer, terminal I/O library, multiplexer role, IPC encoding, Linux scope creation, rendering synchronization, geometry policy, replay storage) under the same workload and traces.

The competing design — letting terminal sessions own shells/processes and relying on PTY lifetime, multiplexers, or renderer backpressure — is falsified by the fixed detach requirement and by any negative trace in which closing a view ends work, attaching launches work, or a blocked client stalls canonical state. Each recommendation carries its own decisive falsifier; for example, the input lease is falsified if lease handoff creates materially worse latency or unusable failure modes while a simpler arbitration stays deterministic and non-corrupting.

## What this does not prove

- No renderer, TUI library, multiplexer, terminal application, IPC serialization, or product default is selected; all remain measurement candidates.
- There are no locally observed runtime claims; the report's sources are standards and platform contracts, not benchmark results or Recursion experiments.
- The proposed `SNAPSHOT`/`EVENT`/`ACK`/`CREDIT`/`RESET` protocol and daemon-side projection are inferred, not demonstrated.
- The report explicitly treats whole-descendant-tree termination on all target environments as unverified until adversarial R11 tests pass; platform docs show mechanisms and preconditions, not that Recursion's future code uses them correctly.
- Job Objects and cgroups govern local processes only; external/provider-side effects need their own cancellation and idempotency contracts, and containment does not defend against a client with daemon-equivalent OS credentials or kernel compromise.
- Compatibility and accessibility do not graduate by analogy: no MSYS2, Neovim, or screen-reader claim is promoted until its own suite passes.

## Open Owner decisions

- Minimum supported Windows build and minimum Linux kernel/distribution, and whether systemd is mandatory?
- What counts as an actor "external effect" outside the OS process tree?
- Is complete causal history audit-durable, or only the current projection?
- Default actor terminal geometry and the lease-handoff rule?
- Read authorization for shared multi-ARM rooms?
- The approved PERF-010 numeric SLA ("negligible" is not a number)?
- Supported accessibility technologies per native OS?
- Snapshot cadence and retention/replay floor?
- Whether client control capability survives a daemon restart (invalidate connection-scoped leases)?
- Multiplexer role and the wire encoding to benchmark?

## Relevance to later waves

This lane is an input to the terminal runtime and process-broker work: it supplies the ownership separation, the OS containment candidates, the reconnect and flow-control contracts, and the negative traces and PERF-010 matrix that a future harness must instantiate. Later waves should freeze these as a versioned test contract and run native Windows and Linux first, then MSYS2, Neovim, and accessibility independently, before any renderer, encoding, or supervision default is selected by independent review — the implementer's own PASS is not sufficient.

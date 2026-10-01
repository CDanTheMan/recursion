---
title: DS-19 — Operating-system platform behavior
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not stop at a plan, outline, scope sheet, or clarification request — execute the research now and return the final report.

# DS-19 — Operating-system platform behavior

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

- Recursion v3 must operate natively on Windows and Linux; the interactive terminal detaches from views rather than ending work, and the product is a headless harness with an optional Telegram transport and no required graphical frontend.
- The privileged kernel is four pure functions (`decode`/`admit`/`reduce`/`derive_work_packet`) with no filesystem, network, process, provider, terminal, plugin, credential or wall-clock access; the daemon, broker, adapters and views call the boundary and must not move into it.
- `E-FHAR2-102` defines that kernel API and the neutral language experiment; `EXP-FHAR-10` is the matched CPython/Rust/Go reducer/replay/fault comparison on frozen Windows/Linux hosts.
- `E-FHAR2-104` is the terminal/process broker contract: the Recursion broker — not the PTY, renderer or view — owns process identity, containment, event cursors, input/resize leases, recovery and fanout, with the message set `HELLO`/`WELCOME`/`SNAPSHOT`/`EVENT`/`ACK`/`CREDIT`/`INPUT`/`RESIZE`/`RESET`.
- The OS seams that matter are Windows Job Objects and ConPTY versus Linux process groups/PTY, `cgroup v2`, `pidfd` and `clone3`; descendant-tree termination must be proved rather than assumed, and a terminal close is not proof of descendant or external-effect completion.
- Milestone 2 delivers the canonical state writer; Milestone 6 delivers the planning and interactive operator CLI, including detachable terminal views and persistent daemon/process-broker attachment; Milestone 7 delivers the authenticated node fabric.
- Required invariants include one canonical writer per aggregate, `AuthorityScope` non-widening, `LeaseFence` and `PauseSafety`; transport and terminal bytes never carry canonical authority.
- `PERF-010` is the experiment that several detachable terminal views stay responsive without multiplying worker/model cost, and `H-030` is the hypothesis that a daemon-owned actor/process runtime lets views attach and detach without orphaning work.
- **UNRESOLVED, Owner-owned:** the implementation language, terminal renderer, terminal multiplexer/IPC library and process library are unselected; the accepted detachable-terminal ruling is fixed and is not reopened.

## Purpose

Produce the cross-platform conformance evidence that lets the Owner decide how Recursion v3 must behave on Windows and Linux — the exact OS seams an implementation must cross — before any language, store or process library is chosen. This is blocking because the process broker, canonical state writer, terminal attach/detach, crash recovery and containment contracts in the ratified architecture target, `E-FHAR2-104` and Milestones 2, 6 and 7 are all defined in terms of OS primitives (Job Objects, ConPTY, cgroups, PTYs, fsync/rename), and assuming POSIX semantics on Windows (or vice versa) is a correctness and containment defect. Nothing here selects a runtime, store, renderer or process library.

## Authority and boundaries

The authority, scope and privacy constraints that govern this lane are restated in `## Baked context`; treat them as the operative limits. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. **DO NOT select a language, store, framework, renderer or plugin runtime.** The Owner decides. No claim that a current OS build, kernel or terminal is certified follows from this file. The detachable-terminal product ruling is fixed; this lane compares mechanisms and may not reopen it.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Process model and containment

1. What is the exact Linux creation/containment path — `fork`+`exec` vs `posix_spawn` vs `clone3(CLONE_INTO_CGROUP)` — and the Windows path (`CreateProcess` with `PROC_THREAD_ATTRIBUTE_JOB_LIST`), and where do process groups/sessions, Job Object child/breakaway limits, and reparenting to PID 1 or `orphan` differ?
2. How is descendant-tree termination actually guaranteed on each OS (Job Object kill-on-close vs PTY session + process group + `cgroup v2`/`pidfd`+`pidfd_send_signal`), and what escape routes remain (Windows breakaway/creation-path escape, Linux cgroup migration, `setsid` escaping, reparented grandchildren)?
3. How does an orphan or descendant-of-descendant get *detected* (not just killed) on each OS, and what is the honest `unknown` when a process escapes the tracked tree or the parent dies before the child is registered?

### PTY / ConPTY

4. Openpty/termios on Linux vs ConPTY on Windows: what are the exact differences in line discipline, canonical vs raw mode, `SIGWINCH` vs console resize events, XON/XOFF and software flow control, and pseudoconsole teardown semantics?
5. How do buffering, CR/LF translation, UTF-8 vs code-page handling, VT sequence parsing, alternate-screen, DSR/DA response and OSC/DCS pass-through differ, and where does a byte-correct capture depend on which layer translates?
6. What are the documented gaps in ConPTY (early-close, resize race, output coalescing) and in the Linux PTY (EIO on master close, hangup ordering) that the broker in `E-FHAR2-104` must treat as transport-not-authority?

### Filesystem semantics

7. Atomic replacement: `rename(2)`/`renameat2(RENAME_NOREPLACE)` and directory `fsync` on Linux vs `MoveFileEx`/`ReplaceFileW` and `FlushFileBuffers` on Windows — where is atomicity guaranteed, where is it only "usually", and what does a crash between rename and directory-fsync leave?
8. `O_APPEND` atomicity vs `FILE_APPEND_DATA`/`FILE_FLAG_APPEND`, `flock`/`fcntl` advisory locks vs `LockFileEx` mandatory locks, and `mmap` coherence and truncation hazards across OSes — which locking primitive survives a stale-lock and a process death?
9. Path and naming reality: case sensitivity (NTFS vs ext4), `MAX_PATH` 260 and long-path opt-in (`\\?\`), reserved device names, alternate data streams, symlinks/junctions, POSIX ACLs vs Windows ACLs, and `umask`/inherited-ACL behavior?
10. What is the durability reality of network filesystems (SMB/NFS) and of WSL2's `/mnt/c` vs the ext4 VM disk — which Semantics silently weaken `fsync`, atomic rename or locking there?

### Signals, time and events

11. Signals (`SIGTERM`/`SIGINT`/`SIGWINCH`/`SIGHUP`) vs Windows console control events (`CTRL_C_EVENT`, `CTRL_CLOSE_EVENT`) and `TerminateProcess`: what can and cannot be caught, ordered or flushed, and how does a detached service avoid console-attachment coupling?
12. Event loops and readiness: `epoll` vs `kqueue` vs IOCP completion vs `io_uring`, file-descriptor limits/`select` ceilings, and Unix-domain sockets vs Windows named pipes — which give the broker a single cancellation/backpressure story?
13. Time and monotonicity: monotonic vs wall clock, NTP slew/step and suspend/resume, timezone/DST handling, and which time source may enter canonical state (recall: logical time enters only as an admitted input per `E-FHAR2-102`)?

### Resource limits and service models

14. Resource limiting: Linux `rlimits`, `cgroup v2` (`memory.max`, `cpu.max`, `io.max`, OOM kill behavior, `memory.events`) vs Windows Job Object limits (CPU rate, commit, process count, memory) — how does a limit become a *fault* versus a throttle, and how is OOM observed?
15. Service supervision: systemd unit design (Type, restart policy, watchdog `WATCHDOG=`, socket activation, `RuntimeDirectory`, `LoadCredential`, hardening directives) vs the Windows Service Control Manager (recovery actions, failure counters) — how does each avoid silently restarting killed work or racing PAUSE?
16. Crash and recovery semantics per OS: what survives a hard kill, a reboot, a power loss, and a suspended laptop; how are PID reuse, stale lock files, and half-written state detected and reconciled?

### Locale, security and conformance matrix

17. Locale, encoding and environment: `LANG`/`LC_*`, Windows code pages and UTF-8 manifest, `TZ`, temp dirs and noexec/tmpfs, environment inheritance into workers, and secret leakage via environment or command line?
18. Security modules and platform hardening: SELinux/AppArmor on Linux and Defender/ASR/Controlled Folder Access on Windows — what breaks silently under each (rename, exec, socket, filesystem access), and how is a denial surfaced rather than swallowed?
19. What is the **per-OS conformance test matrix** required to graduate a platform, and how are Git Bash/MSYS2, WSL2 (both `/mnt` and native ext4), and Neovim embedded terminals treated as distinct high-priority cases rather than aliases of native Windows or Linux?

## Deliverable

A source-pinned report containing: a claim table (claim, source, version/date, classification, confidence, expiry trigger); a per-OS conformance matrix whose every cell is measured, explicitly modelled, or `unknown`; a preregistered cross-platform fault-test plan (descendant escape, PTY teardown, atomic-rename crash, stale lock, disk-full, OOM, suspend/resume); a recommendation tied to a named competing option and decisive falsifier; and open Owner questions. No implementation is selected as a product default.

## Non-goals

- No OS-specific runtime or broker implementation.
- No selection of a process library, PTY library, renderer or multiplexer.
- No OS terminal application, distro or kernel version made mandatory.
- No reopening of the detachable-terminal or containment product rulings.
- No claim of full descendant-tree termination or durability before it is measured across the matrix.
- No graphical frontend or Windows installer work.
- No provider, model or route calls.
- No modification of the terminal-runtime contract, the canonical-state contract or any protected path.

## Completion gate

- Primary platform sources are pinned by version/date (Microsoft pseudoconsole, Job Objects, `ReplaceFile`/`FlushFileBuffers`, Windows console events; Linux `renameat2`, `cgroup v2`, `clone3`, PTY/termios, `rename(2)` and `fsync` semantics; POSIX.1-2024 where used).
- Every containment claim names a specified negative trace (escape, orphan, reparent, stale lock).
- The per-OS conformance matrix is preregistered with explicit stop conditions.
- Native Windows and Linux are mandatory; Git Bash/MSYS2, WSL2 (both mount paths) and Neovim embedded terminals are distinct cases.
- Filesystem durability, locking and `MAX_PATH`/long-path behavior are covered for each OS and for SMB/NFS.
- Every recommendation names a competing option and a falsifier, and preserves an explicit no-selection outcome.
- Protected paths are untouched; privacy and secret scan are clean.

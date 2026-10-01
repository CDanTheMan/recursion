---
title: FU-04 — Operating-system platform conformance fixtures
status: ready-for-explicit-invocation
last-updated: 2026-10-01
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# FU-04 — Operating-system platform conformance fixtures

This is a follow-up to gap G-04 in [GAPS.md](../../research-lane/GAPS.md) and source lane DS-19 (Domain A).

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

- DS-19 returned a **contract-first, native-semantics qualification model**: one behavior
  contract, qualified per pinned platform profile through native semantics and preregistered
  negative traces; outcomes are qualified, rejected, or `unknown`.
- It reframed the blocking seams — process creation and descendant containment, PTY/ConPTY,
  filesystem atomicity versus durability, signals and console events, clocks, resource limits,
  service supervision and crash recovery — as one platform behavioral envelope. It stressed that
  membership is not completeness and that compatibility layers (WSL2 `/mnt/c`, WSL2 native
  ext4, Git Bash/MSYS2, embedded terminals, SMB, NFS) must not inherit qualification by analogy.
- It supplied source-documented contracts (Job Objects and creation-time assignment, cgroup v2
  `cgroup.kill` and `CLONE_INTO_CGROUP`, PTY vs ConPTY teardown, `rename` and directory `fsync`,
  `ReplaceFileW`/`FlushFileBuffers`, lock release, PID reuse, supervisor restart races) but
  **no measured cells**, and it answered an unnamed subject query.
- It left open: ConPTY teardown, cgroup/OOM, rename/fsync durability, lock release and supervisor
  races unmeasured; WSL, compatibility shells, embedded terminals, SMB and NFS unqualified; and
  several platform-scope Owner decisions (G-11).
- This lane is a blocking prerequisite for the process/terminal broker (`E-FHAR2-104`) and the
  canonical state writer (Milestone 2); the broker chaos matrix of G-05 consumes its fixtures.

## Purpose

Produce the machine-readable, platform-profile-keyed conformance manifest and the preregistered
negative-trace fixture suite that qualify a pinned OS profile as qualified, rejected or
`unknown`. This is a fixture-design and evidence lane: it specifies the profiles, the
preregistered negative traces, the observation and recovery oracles and the qualification
outcomes; it does not run the fixtures and does not select a runtime, store or process library.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Preserve the current Hermes constitution; propose amendments, never edit it. Public Deep
Research receives only public or synthetic briefs. **DO NOT select a language, store, framework,
renderer, process library, PTY library or multiplexer, and DO NOT claim that any OS build,
kernel, terminal, filesystem or distribution is certified.** No fixture is executed, nothing is
deployed and no protected path is written. Do not decide the platform-floor or storage-scope
Owner questions (G-11).

## Inputs to read

None. This handoff is self-contained; the prior lane's conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Platform profile schema

1. What is the exact machine-readable profile key for a qualification target (OS edition/build or
   kernel/distribution, architecture, filesystem and mount options, terminal path, supervisor
   configuration, storage locality, security policy such as MAC/FIPS, and namespace/cgroup
   floor), such that no cell can turn green by analogy from another profile?
2. How are Native Windows and Native Linux each left **Unqualified** until they pass, and how are
   WSL2 native ext4, WSL2 `/mnt/c`, Git Bash/MSYS2, embedded terminals, SMB and NFS represented
   as distinct mandatory cases rather than inherited rows?

### Negative-trace fixture catalog

3. What is the preregistered negative trace for each seam, at the level of a runnable fixture:
   descendant escape, parent death before registration, PTY/ConPTY teardown with an undrained
   output pipe, atomic-replace crash, stale lock and PID reuse, disk full or quota between write
   and flush, memory pressure/OOM (cgroup v2 `memory.high`/`memory.max`/`memory.events` versus a
   Job memory ceiling), supervisor restart race, suspend/resume across a deadline, and
   network-storage interruption?
4. For each trace, what is the required **observation oracle** and **recovery oracle** — the exact
   evidence that distinguishes "transport closed", "client disconnected", "containment state",
   "process exited", and "execution settled" — so that absence of a notification is never read as
   proof no event occurred?
5. What is the source-documented mechanism per platform for each seam (creation-time Job
   membership via `PROC_THREAD_ATTRIBUTE_JOB_LIST`, breakaway semantics, `CLONE_INTO_CGROUP`,
   `cgroup.kill`, `pidfd`, `renameat2`, directory `fsync`, `ReplaceFileW`/`FlushFileBuffers`,
   `LockFileEx` mapped-file bypass, `GenerateConsoleCtrlEvent`, monotonic vs boottime clocks),
   and where the honest evidence class is `unknown`?

### Containment, durability and resources

6. What is the correct statement of containment as "all processes remaining inside the managed
   scope are killed" rather than full descendant-tree capture, and what named escape paths
   (breakaway, privileged migration, external-service-created work) must the suite target?
7. How is atomicity distinguished from durability per filesystem/storage profile, and what is the
   required definition of "survives power loss" (application-consistent after VM reset, host
   reset, or physical interruption) that a durability fixture asserts?
8. How are resource exhaustion outcomes modeled as a fault family (throttle, allocation refusal,
   process kill, group kill, `unknown`) rather than one portable "OOM" status, and why does a
   downstream recovery or accounting decision depend on the distinction?

### Qualification outcome and ownership

9. What is the exact rule that yields **qualified at a pinned configuration**, **rejected/
   unsupported**, or **unknown pending named evidence**, and what evidence retires an `unknown`?
10. Which target profile, compatibility layer and storage scope choices are Owner inputs (G-11),
    and how does the manifest record them as required inputs rather than assumptions?

## Deliverable

A source-pinned report containing: the machine-readable platform-profile schema and the list of
mandatory profile rows; the full preregistered negative-trace catalog with, per trace, the
injected fault, the required observation/recovery oracle and the decisive stop condition; the
source-documented mechanism and evidence class per seam; the containment, durability and
resource-fault statements; the qualification-outcome rule and retirement evidence for `unknown`;
each recommendation paired with a competing option, a decisive falsifier and what it does not
prove; and the Owner inputs the manifest depends on. No certification and no selection.

## Non-goals

- No selection of a runtime, store, framework, renderer, process library, PTY library or
  multiplexer.
- No fixture executed and nothing deployed by this session.
- No certification of any OS build, kernel, terminal, filesystem or distribution.
- No claim that a compatibility layer or network filesystem is equivalent to a native profile.
- No decision of the platform-floor, WSL2, SMB/NFS or "survives power loss" Owner questions.
- No modification of a protected path.

## Completion gate

- The manifest is keyed by pinned platform profile and contains no cell that can qualify by
  analogy.
- Native Windows and Native Linux are each Unqualified until they pass; every compatibility layer
  is a distinct mandatory case.
- Every negative trace names its injected fault, observation oracle, recovery oracle and stop
  condition.
- Containment is stated as membership/completeness-limited, with named escape paths.
- Atomicity, durability and the "survives power loss" definition are stated per profile.
- Resource exhaustion is a fault family, and the three qualification outcomes are exhaustive.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove.
- Protected paths are untouched; privacy and secret scan are clean.

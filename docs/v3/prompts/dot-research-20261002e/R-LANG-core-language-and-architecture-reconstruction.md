---
title: R-LANG — Core language, runtime and architecture reconstruction
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-LANG — Core language, runtime and architecture reconstruction

This handoff serves accepted Owner decisions D-018 (no ecosystem lock-in), D-028 (platform floors),
D-033 (porting is a hypothesis), D-034 (the scaling thesis), D-035 (plugins live outside the core)
and D-039 (accept the OS/language advisory and plan a language-agnostic architecture), with the gap
register in [GAPS.md](../../research-lane/GAPS.md). It is paired with
[R-CS](R-CS-control-surface-and-competitor-study.md), the control-surface and competitor study, and
it fills the gap the mobile-only OS/language advisory left open: the **core/backend** implementation
language and runtime were never evaluated. It consumes the FU-01 (language/runtime), FU-02 (store
crash/replay) and FU-03 (deterministic kernel and byte vectors) lines and the accepted platform
direction in `PERFORMANCE-PLAN.md`, `CONTEXT.md`, `M1B-WIRE-PROFILE.md` and `state/DECISIONS.md`,
and it must not reopen them.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a small
deterministic kernel with typed adapters; native and upstream execution; persistent, goal-scoped
assistants organized as Head -> executives -> bounded workers; configurable context and compaction;
plugins and editions; an interactive detachable terminal; and Windows/Linux operation and recovery.

Authority: Lucas is the final owner. Recursion is a standalone agent harness and a harness
orchestrator that delegates through other harnesses. Hermes-led control was retired on 2026-09-28
(state/DECISIONS.md D-017); Hermes is an optional upstream integration, not the executive control
plane. An implementer's own PASS is never acceptance; independent review is required, and missing
verification is never a pass. `CONTROL_PLANE.md` is the operative constitution; a research session
may propose amendments but must never edit it. No research session performs implementation,
provider/model/authentication/configuration changes, spending, deployment, publication or merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula, captures
and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (language specifications, official runtime and
OS documentation, pinned source, licenses, peer-reviewed work). Classify every consequential claim
as source-documented, locally observed, inferred or unverified; keep `unknown` distinct from zero.
Model consensus and vendor marketing are not evidence. Every recommendation needs a competing
option and a decisive falsifier, and must name what it does not prove. Do not request or display
hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never secrets,
credentials, personal data, private repository content, local paths, or account/infrastructure
identifiers.

### Lane context

- The exact thing to design: (a) a **decision-ready evaluation of candidate implementation
  languages and runtimes for the Recursion v3 deterministic core and backend**, and (b) a
  **language-agnostic architecture specification** by which the core can be reconstructed in a
  different language with bounded cost (the D-039 falsifier: a later language change must be a
  reconstruction, not a re-derivation).
- D-028 is the accepted platform floor this evaluation must respect, not relitigate: Windows 11
  25H2 (build 26200) x64 primary (24H2 build 26100 Enterprise also qualified); Linux 6.12 LTS
  primary / 6.6 LTS minimum with cgroup v2; WSL2 dev/test only; canonical state on local NTFS/ext4
  only (SMB/NFS out of scope); "survives power loss" means application-consistent after an abrupt
  VM reset at the commit boundary.
- FU-03 produced a reduced-bound TLA+/TLC model, a mutant battery and language-neutral byte vectors
  for the deterministic kernel (`decode` / `admit` / `reduce` / `derive_work_packet`); the kernel
  freeze remains conditional. FU-02 left the store choice (for example a hand-rolled JSONL + CAS vs
  an embedded WAL store) **unmeasured** for crash/replay. FU-01 is the language/runtime line this
  handoff informs. Treat these as inputs to build on, not as settled results.
- D-033 makes "porting is cheap" a hypothesis with a falsifier; D-035 makes plugins external
  artifacts referenced by digest, which fixes the core/plugin boundary the chosen language must
  host. D-034's thesis requires deterministic, reproducible composition and honest accounting.
- Environment fact (not a selection): the developer machine already has Java 21 (Temurin), Rust,
  Go, Python 3.12, Node 24, git and WSL2 `Ubuntu-24.04`. The presence of a toolchain is not a
  language recommendation and must not be treated as one.
- Evidence status: no core language, runtime, store, plugin host, serialization or build system has
  been selected; no benchmark has been run; every comparison below is to be established from public
  documentation and a synthetic, provider-free plan, or marked `unknown`.

## Purpose

Produce the decision-ready **core language, runtime and architecture-reconstruction evaluation** for
Recursion. The lane enumerates the candidate languages and runtimes fairly, evaluates them against
the accepted platform floors, the deterministic-kernel and store/replay requirements and the
plugin-host boundary, and defines how to specify the architecture so that a later language change is
a bounded reconstruction. It delivers a candidate comparison matrix, a shortlist, and a
reconstruction specification outline — each recommendation with a competing option, a decisive
falsifier and an explicit statement of what it does not prove. It does not select a language,
runtime, store, serialization, sandbox or vendor, runs no benchmark, and executes no build.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, runtime, package manager, build system, serialization format, store, sandbox, plugin host,
transport or vendor.** Do not decide an Owner question recorded in D-018, D-028, D-033, D-034,
D-035 or D-039, and do not reopen D-019, D-022, D-023, D-024, D-030 or D-031. No build, install,
benchmark, provider, model, account or network action is performed; every proposed comparison is
provider-free and synthetic. Do not assert a measured performance, safety, portability or
maintenance advantage without a defined independent experiment; each claim carries a competing
option and a falsifier. Do not claim that porting an existing component or harness is cheap; that
remains a hypothesis (D-033). No legal or license conclusion is stated; licensing questions are
questions. No claim of kernel freeze, route qualification or measured cost is authorized.

## Inputs to read

None from this repository: the rescope, the platform floors, the kernel and store lines and the
D-018 through D-039 context are summarized in `## Baked context` above, and no repository, connector
or private-source access is assumed. The session must, however, retrieve the public primary sources
it cites and pin each claim to a URL and retrieval date, including: the specifications and official
documentation of the candidate languages and runtimes; the current Windows and Linux file-sync and
process documentation relevant to a durable commit boundary; the specification of any serialization
or canonicalization mechanism it discusses; the WebAssembly and foreign-function-interface
documentation relevant to a plugin-host boundary; the license text of every candidate toolchain and
embedded dependency; and peer-reviewed or reproducible benchmark methodology it relies on. Treat
every language, runtime, store and benchmark as prior art cited from public documentation, not as an
endorsed or selected component.

## Research questions

### Candidate languages and runtimes

1. What is the fair candidate set for a deterministic, provider-neutral core and backend (for
   example Rust, Go, C++, C#, Java/Kotlin-JVM, TypeScript/Node, and any other credible option), and
   what evaluation dimensions matter most for this product rather than in general?
2. Determinism and reproducibility: which runtimes let identical inputs produce identical canonical
   bytes and logs without non-deterministic map/set iteration, garbage-collection timing, scheduler
   order or locale effects, and what does each require to make that true?
3. Concurrency and the single-writer kernel: how does each candidate express one fenced writer, an
   ordered log, leases and epochs, and how does it behave under abrupt process or VM reset?
4. Cross-platform, Windows-first: how does each candidate satisfy the D-028 floors, including
   filesystem durability/sync semantics on NTFS and ext4, process/child management, signal or
   equivalent handling, and Windows packaging and service behavior?
5. Plugin and host boundary: how would each candidate host external plugins (D-035) — process/IPC,
   WebAssembly, foreign-function interface, or a protocol boundary — and what does each make easy
   or impossible for isolation, versioning and disabled-inertness?
6. Ecosystem fit: what is the state of canonical-JSON, cryptographic-hash, wire-protocol and
   embedded-store libraries for each candidate, and what are the licensing, supply-chain and
   maintenance risks of each?
7. Whole-lifecycle cost: toolchain maturity, build reproducibility, packaging and distribution,
   observability, static analysis, hiring/AI-assisted authoring judged on reviewed end-to-end cost
   rather than generation speed, and long-term maintenance for a small team.
8. Failure modes: garbage-collection pauses, unsafe memory, runtime availability, dependency churn,
   cross-compilation gaps and OS-integration limits — which are disqualifying for the core, which
   are mitigable, and with what evidence?

### Store, replay and determinism

9. How does each candidate map to the FU-02 crash/replay question and the FU-03 byte vectors,
   including the fsync/flush semantics available on Windows and Linux at the commit boundary?
10. What competing store designs (for example an embedded write-ahead-log relational store versus a
    hand-rolled append-only log with content-addressed snapshots) suit a deterministic, single-writer
    kernel, and what is each one's decisive falsifier and what does each fail to prove?

### Language-agnostic architecture and reconstruction

11. What must be specified language-neutrally for the architecture to survive a language change:
    state machine and transitions, invariants, schemas and wire contracts, canonical-serialization
    rules, test vectors, error/refusal alphabets, concurrency and fencing model, and build/repro
    metadata? Which parts should stay language-specific by design?
12. What are the **reconstruction acceptance criteria** — the concrete evidence that a language
    change was a bounded reconstruction (for example, the same test vectors and refusal alphabet, a
    machine-checked state model, a frozen wire profile, an equivalence harness) rather than a
    re-derivation, and what would falsify a claim of reconstructability?
13. How should the core/plugin boundary be specified so a chosen language choice does not leak into
    the plugin contract (D-035), and so the plugin contract stays stable across a core language
    change?

### Comparison methodology

14. What provider-free, synthetic comparison plan would fairly evaluate the shortlist later —
    workloads, hard floors, an independent oracle, paired arms, frozen budgets and stopping rules —
    stated as a plan that is **not executed** by this handoff?
15. What are the threats to validity (benchmark gaming, vendor claims, local-environment bias,
    AI-assisted authoring bias) and what evidence would change a recommendation?

## Deliverable

A core language, runtime and architecture-reconstruction evaluation containing: a **candidate
comparison matrix** covering every candidate on the dimensions above with an evidence class and a
pinned source per consequential cell, and `unknown` where unmeasured; a **shortlist** with the
rationale, each entry carrying a competing option, a decisive falsifier and what it does not prove;
a **store/replay fit** section mapping the shortlist to FU-02 and FU-03; a **plugin-host fit**
section mapping it to D-035; a **language-agnostic architecture specification outline** naming what
must be specified neutrally versus what may stay language-specific; **reconstruction acceptance
criteria** with falsifiers; and a **provider-free comparison plan** that is explicitly unexecuted.
No language, runtime, store, serialization, sandbox or vendor is selected.

## Non-goals

- No selection of a language, runtime, package manager, build system, serialization format, store,
  sandbox, plugin host, transport or vendor.
- No build, install, benchmark, profiling run, provider/model call or network action; every proposed
  comparison is synthetic, provider-free and explicitly not executed here.
- No claim of measured performance, safety, portability, maintenance or review-effort advantage; no
  claim that porting an existing component or harness is cheap (D-033).
- No reopening of D-018, D-019, D-022, D-023, D-024, D-028, D-030, D-031, D-033, D-034, D-035 or
  D-039, and no reopening of the accepted requirements in `PERFORMANCE-PLAN.md`, `CONTEXT.md` or
  `M1B-WIRE-PROFILE.md`.
- No legal or license conclusion; licensing, export and distribution matters are questions.
- No new executive tier and no reproduction of a standing executive.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The comparison matrix covers a fair candidate set on determinism, concurrency/fencing,
  Windows-first cross-platform behavior, plugin host, ecosystem/licensing risk, lifecycle cost and
  failure modes, with an evidence class and a pinned source per consequential cell, and `unknown`
  where unmeasured.
- The evaluation maps the shortlist to the D-028 platform floors and to the FU-02 store/replay and
  FU-03 kernel-determinism questions, and states what each store design does not prove.
- The plugin-host section maps candidates to the D-035 external-plugin boundary and keeps the
  plugin contract independent of the core language choice.
- The language-agnostic architecture specification names what must be specified neutrally (state
  machine, invariants, schemas, canonical serialization, test vectors, refusal alphabet, fencing
  model, build/repro metadata) and what may stay language-specific.
- Reconstruction acceptance criteria are stated with concrete evidence and a falsifier for
  reconstructability; a claim that a language change is bounded lists what would disprove it.
- A provider-free comparison plan is stated (workloads, hard floors, independent oracle, paired
  arms, frozen budgets, stopping rules, threats to validity) and is explicitly **not executed**.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, runtime, store, serialization, sandbox or vendor is selected.
- The candidate explains what it does not establish: no measured performance, no kernel freeze, no
  route qualification, no porting cost and no legal conclusion.
- Protected paths are untouched; privacy and secret scan are clean.

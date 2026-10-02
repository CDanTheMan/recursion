---
title: FU-01 — Implementation language and runtime experiment (EXP-FHAR-10)
status: ready-for-explicit-invocation
last-updated: 2026-10-01
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# FU-01 — Implementation language and runtime experiment (EXP-FHAR-10)

This is a follow-up to gap G-01 in [GAPS.md](../../research-lane/GAPS.md) and source lane DS-18 (Domain A).

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

- The DS-18 lane ran and returned an explicit **no-selection**: no product-default language,
  evidence insufficient, the choice reserved to the Owner.
- It named `EXP-FHAR-10` as the decision-producing experiment: the same deterministic
  reducer/replay/fault workload implemented in CPython (GIL and free-threaded as separate
  arms), Rust and Go, on frozen Windows/Linux hosts, hard-floor-first then resource-ranked with
  no weighted composite. Exact pins at the 2026-09-30 freeze were CPython 3.13.15, Rust 1.98.1
  and Go 1.27.1.
- It left open: p99/p999 latency, RSS level and slope, FFI cost, artifact size, cold start,
  dependency closure and 24/7 behavior for every candidate; the real library closure (SQLite
  binding, JCS, crypto, PTY/ConPTY, MCP, HTTP) is unselected; and no experiment was run.
- It recorded a real dependency edge: `EXP-FHAR-10` itself needs DS-22's language-neutral
  byte-level conformance vectors, refusal taxonomy and trace-validity checker first. That corpus
  is gap G-03 and is commissioned by `FU-03-formal-model-and-conformance-vectors.md`.
- This lane is blocking because every later milestone (Milestone 2 canonical state, 3
  plugin/route fabric, 7 node fabric, 8 adaptive optimization, 9 soak) bakes in a runtime's
  concurrency, memory, packaging and fault semantics.

## Purpose

Produce the decision-ready evidence pack and the executable, preregistered specification for
`EXP-FHAR-10`, so the Owner can select or decline to select the privileged kernel runtime and
the daemon/broker base. This is a research/specification lane: it designs and pins the
experiment and gathers source-pinned decision inputs; it does not run the experiment and does
not select a language.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Preserve the current Hermes constitution; propose amendments, never edit it. Public Deep
Research receives only public or synthetic briefs. **DO NOT select CPython, Rust, Go, C/C++,
Zig, Java/Kotlin, TypeScript/Bun, WASM or any hybrid as a product default.** Option 2 (a native
deterministic kernel with typed adapters) is Owner-ratified and is not reopened; this lane
supplies the evidence that compares runtimes satisfying it. No runtime, provider, auth, config,
spending, deployment, publication or merge is authorized. No claim that any upstream version is
certified, supported or CVE-free follows from this file. Do not pre-empt any Owner decision
recorded in GAPS.md.

## Inputs to read

None. This handoff is self-contained; the prior lane's conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Candidate and host pinning

1. For each candidate (CPython GIL build, CPython free-threaded build, the optional Python 3.14
   sensitivity arm, Rust stable, Go, and any named single-binary or hybrid topology such as
   PyO3, cgo or Rust-embedding-Python), what exact current version and date applies, and what
   exact Windows build and Linux kernel/distribution profile pair forms the frozen host matrix?
2. How is host and toolchain drift recorded and detected so that a rerun on a changed host is a
   new experiment, not a silent extension of the old one? What is the immutable experiment
   artifact identity (toolchain digests, host profile record, dependency lock)?

### Canonical-byte conformance (consumer of G-03 / FU-03)

3. What exact subset of the language-neutral byte-level vector corpus and the stable refusal
   taxonomy from FU-03 must exist before any candidate is admitted to `EXP-FHAR-10`, and how is
   the experiment kept independent of the TLA+/TLC model of record?
4. For each candidate, which documented behavior makes byte-identical `decode`/`admit`/`reduce`/
   `derive_work_packet` output possible or impossible under RFC 8785 (JCS): integer and
   IEEE-754 shortest round-trip floats, `-0` -> `0`, NaN/Inf rejection, duplicate-key rejection
   before object collapse, map/dict traversal order, and Unicode normalization policy?
5. Which candidates guarantee stable, protocol-owned refusals (`{code, schema_epoch,
   field/path, stable_detail_enum}`) rather than a drifting thrown-exception message, and where
   is the honest `unknown`?

### Hard floors, concurrency and cancellation

6. What is the exact language-independent hard-floor test list (canonical sequence, command
   idempotence, lease and authority fencing, `PauseSafety`, expected-state semantics, replay
   determinism, fail-closed replay, offline core-only build and SBOM/dependency-lock closure),
   and which single failure rejects a candidate before any resource comparison?
7. For each candidate, what exactly happens under two concurrent writers at the admission
   boundary, and which documented mechanism rejects the race at compile time or run time
   (Rust `Send`/`Sync` and `unsafe` escape hatches; Go races and the race detector; CPython
   GIL/free-threaded thread-safety of the C-API, `dict` and extensions; C/C++ UB and sanitizers)?
8. Which candidate can guarantee structured cancellation at a defined boundary so no orphaned
   task straddles the PAUSE/admission epoch, and what is the mechanism and its documented
   limits (tokio drop-not-await, `context.Context`, `asyncio` task groups, `CancellationToken`)?

### Resource and tail metrics with denominators

9. What is the metric dictionary for the coordinator-small profile — cold start, per-op
   overhead, p99/p999 admission latency, RSS level and slope over 24/7 soak, allocator/GC pause
   distribution, FFI call cost, artifact/install size and direct/transitive dependency count —
   and what denominator does each metric carry (per-op, per-event, per-task, per-view)?
10. How are process-tree or accounting-group totals measured so that a candidate that moves work
    into helpers or child processes cannot appear leaner by shifting memory, CPU, I/O, wakes or
    latency?

### Real library closure, packaging and supply chain

11. For the specific library roles Recursion needs (SQLite binding, canonical JSON/JCS,
    crypto/signing, PTY/ConPTY, MCP, HTTP), what is each candidate's resolved dependency
    closure, license posture, maintenance cadence and documented CVE history, and where must the
    answer be `unknown` because exposure is not normalized?
12. Which candidate can satisfy the `ReleaseId`/`E-FHAR2-108` obligations (core dependency-lock
    digest, build-provenance digest, SPDX 3.0.1 SBOM) with an offline, air-gapped dependency
    closure, and which can produce a reproducible, code-signable artifact?

### Decision rule

13. How does a practically meaningful, reproducible advantage get declared among floor-passers
    without a weighted composite, what is the Owner evidence threshold that converts a resource
    difference into a decision, and what exactly triggers the explicit no-selection fallback?
14. Which adoption/rejection rule is paired with a named competing option and a decisive
    falsifier for each candidate and for any hybrid topology?

## Deliverable

A source-pinned report containing: a claim table (claim, source, version/date, classification,
confidence, expiry trigger); a candidate comparison matrix whose every cell is **measured**,
**explicitly modelled** (with the model stated), or marked `unknown`; the executable
`EXP-FHAR-10` protocol (frozen host matrix, vector interface from FU-03, hard-floor test list,
metric dictionary with denominators, data-collection and uncertainty policy, stopping rule); a
per-candidate adoption/rejection rule with at least one competing option and one decisive
falsifier; and open Owner questions. No language is selected as a product default.

## Non-goals

- No selection of any language, runtime or hybrid as a product default.
- No experiment, reducer, adapter, benchmark or build executed by this session.
- No claim that a current upstream version is certified, supported or CVE-free.
- No provider, model, network or paid route calls.
- No numeric performance budget invented before measurement.
- No reopening of Option 2 or the required small native loop.
- No private hardware inventory treated as design data.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- Each candidate and host is pinned by exact version and date, or its evidence is explicitly
  `unverified`.
- Byte-identical determinism is demonstrated or falsified per candidate on the identical
  language-neutral vectors, including float/`-0`/NaN and map-ordering hazards.
- Every concurrency claim names a data-race or cancellation failure mode and its test.
- Memory and tail-latency cells report denominators and are labelled measured, modelled or
  `unknown`.
- FFI, packaging, reproducibility and SBOM claims trace to `E-FHAR2-102`/`E-FHAR2-108`
  obligations and to the FU-03 corpus dependency.
- The recommendation names at least one competing option and one decisive falsifier and
  preserves an explicit no-selection outcome.
- Hard floors (authority, safety, privacy, correctness, reproducibility) are checked before any
  trade-off or speed comparison.
- Protected paths are untouched; privacy and secret scan are clean.

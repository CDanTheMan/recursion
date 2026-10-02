---
title: Architecture coverage and edge map
status: research-coverage-not-qualification
last-updated: 2026-10-02
---

# Architecture coverage and edge map

Every subsystem/edge mapped to the artifact(s) that research or specify it, with status, cited
sources and a one-line note. Coverage of documentation is **not** qualification.

## Method and sources

- **DS** (`prompts/research-suite-20260929/`): DS-01 pause/fencing; 02 authority; 03 verifier
  independence; 04 plugin trust; 05 migration; 06 capacity/review debt; 07 retention/deletion; 08
  canary; 09 terminal views; 10 performance; 11 routing; 12 context/cache; 13 configuration; 14
  scientific ARM; 15 ARM rooms; 18 language; 19 OS platform; 20 Linux scaling; 21 store; 22 formal
  model/vectors; 23 IPC/broker wire; 24 credentials/egress; 25 update/release/DR; 26 telemetry;
  27 state/projection; 28 plugin/route fabric; 29 fleet; 30 supervision memory; 32 HITL; 33
  licensing/IP; 34 decision journaling.
- **FU** (`prompts/followups-20261001/`): FU-01 language; 02 store crash/replay; 03 model/vectors;
  04 OS conformance; 05 broker chaos.
- **R** (`prompts/dot-research-20261002{,b}/`): R-A plugin portability; B delegation; C route
  legality; D quota; E trusted launch; F headless fan-out; G plugin import; H counsel mode; I Grok
  study; J multi-agent terminal; K multiplexer/TUI; L interface platform; M Claude modding; N
  graphical client; O performance; **P** prompt-injection/untrusted input; **Q** durable memory;
  **R** long-horizon autonomy; **S** adaptive optimization; **T** multimodal I/O; **U** sandbox/
  isolation/supply chain; **V** observability/replay; **W** evaluation/benchmark science; **X**
  node fabric/remote execution; **Y** workspace/repository graph. Returns are intaken at
     `research-lane/overnight-20261002/`. The capability-composition packet d return adds **PC**
   capability-driven prompt/context composition, **UI** capability-driven UI projection
   (`recursion.ui-contract@candidate-2`) and **MOB** mobile/remote control, intaken at
   `research-lane/capability-composition-20261002d/`.
- **Design docs** (`docs/v3/`): PRODUCT, ARCHITECTURE(+PROOF/OPTIONS), CURRENT-AND-MIGRATION,
  EXECUTIVES, PLANNING, AUTONOMOUS-PLANNING, M1A/B/C contracts/wire profiles, EXECUTION-FABRIC,
  CONTEXT, STATE, SECURITY, PLUGINS-AND-EDITIONS, CLI, TERMINAL-RUNTIME, INTERACTION-SURFACES,
  TELEMETRY, ACCEPTANCE, INTERFACE-STRATEGY, ROUTE-CAPABILITIES, PERFORMANCE-PLAN,
  SCIENTIFIC-RESEARCH; plus `research-lane/` maps (SYNTHESIS, GAPS, HARNESS-COVERAGE,
  RESEARCH-INDEX, NEXT-PHASE) and `state/DECISIONS.md` D-017…D-033.

Statuses: **covered-by-spec**, **researched-not-run**, **proposed-packet**, **gap**.

> **Erratum (2026-10-02).** The R-P…R-Y returns are now intaken at
> `research-lane/overnight-20261002/`. Edges 23, 34, 39, 40, 42, 45, 48 and 54 — and other
> `gap`/`proposed-packet` rows in the P–Y domain — are therefore **`researched-not-run`**
> (return present, nothing executed), not `gap`. The R-P…R-Y lane topics are: P injection,
> Q memory, R autonomy, S adaptation, T multimodal, U isolation, V replay/observability,
> W evaluation, X node fabric, Y workspace graph.
>
> **Erratum (2026-10-02, packet d).** The R-PC/R-UI/R-MOB capability-composition candidates are
> intaken at `research-lane/capability-composition-20261002d/`; edges they touch (21 CLI/TUI/GUI,
> 23 accessibility, 24 multi-agent UX, 26 compaction/cache, 30 plugin/capability graph, 40
> multimodal, 44 perf engineering, 48 explain/replay, 53 multi-node/remote) are
> `researched-not-run`, not `gap`.

## Edge map

| # | Edge | Status | Covering artifact(s) | Note |
|---|---|---|---|---|
| Kernel & core | | | | |
| 1 | Deterministic kernel / four-function boundary | researched-not-run | DS-22, FU-03, ARCHITECTURE, M1A | `decode/admit/reduce/derive_work_packet` named; freeze conditional. |
| 2 | Event log / canonical writer / atomicity | researched-not-run | DS-21, FU-02, STATE, DS-05 | Single fenced writer; crash replay unbenchmarked. |
| 3 | Canonical bytes / digest | covered-by-spec | DS-13,18,21,23 | I-JSON+JCS; CBOR test-only. |
| Authority & safety | | | | |
| 4 | Grants / capability lattice | researched-not-run | DS-02, DS-04, DS-13 | Intersection at admission; unproven. |
| 5 | Revocation / fencing epoch | researched-not-run | DS-01, DS-05, DS-20 | Receiver-side monotonic epoch. |
| 6 | Pause / stop / quiescence | covered-by-spec | D-022, DS-01, DS-13, DS-32 | Vocabulary closed; crash matrix unrun. |
| 7 | Quarantine / ambiguity / emergency stop | gap | DS-02, DS-08 | `paused_with_ambiguity` undefined. |
| 8 | Per-adapter effect fencing | gap | DS-01, DS-02 (G-17) | Boundary fencing unshown. |
| Identity & lifecycle | | | | |
| 9 | Head / ARM / assistant identity | covered-by-spec | EXECUTIVES, PRODUCT, DS-15 | Actors/lineage defined. |
| 10 | Leases / epochs / forks | proposed-packet | DS-15, DS-05, DS-22, DS-13 | Bounded leases; fork reservations open. |
| 11 | Worker lifecycle / fleet | researched-not-run | DS-29, CONSTRUCTION-RUNBOOK | Specified, not run. |
| Persistence & durability | | | | |
| 12 | Store / persistence faults | researched-not-run | DS-21, FU-02, STATE | JSONL+CAS vs SQLite WAL unmeasured. |
| 13 | Snapshot / export / migration / rollback | researched-not-run | DS-21, DS-25, DS-05, M1C | `snapshot_digest` open; forward reconciliation. |
| 14 | DR / restore matrix | researched-not-run | DS-25 | Six-mode×four-outcome `unknown`. |
| Concurrency & scheduling | | | | |
| 15 | Admission / capacity / review debt | researched-not-run | DS-06, DS-10, DS-03 | `A(t)` and review domain uncalibrated. |
| 16 | Scheduler / daemon / continuous op | researched-not-run | DS-29, DS-30 | Crash-recovery semantics unrun. |
| IPC / broker & containment | | | | |
| 17 | IPC / broker / terminal wire | researched-not-run | DS-23, FU-05, M1B, TERMINAL-RUNTIME | Four freeze blockers unpassed. |
| 18 | Process containment / termination | researched-not-run | DS-09, DS-19, DS-23 | Whole-tree termination unverifiable. |
| Terminal / multiplexer | | | | |
| 19 | Terminal runtime / detachable views | covered-by-spec | TERMINAL-RUNTIME, DS-09, INTERFACE-STRATEGY | Ten controls, three Stops baselined. |
| 20 | Multiplexer / transformative TUI | proposed-packet | R-K, R-J | Return pending. |
| Interface platform | | | | |
| 21 | CLI / TUI / GUI command-query | covered-by-spec | INTERFACE-STRATEGY, R-L, R-N, CLI | One object graph. |
| 22 | Projections / explain / status | researched-not-run | DS-26, DS-27, PRODUCT §6 | Zero-token explainability stated. |
| 23 | Accessibility | gap | DS-09 (open) | Technologies unselected. |
| Agent communication & collaboration | | | | |
| 24 | Consultation / rooms / multi-agent UX | researched-not-run | DS-15, R-J, DS-32, INTERACTION-SURFACES | F01–F24 unrun. |
| 25 | HITL approvals / forwarding | researched-not-run | DS-32, INTERACTION-SURFACES | Pre-effect boundary defined. |
| Context & memory | | | | |
| 26 | Compaction / cache economics | researched-not-run | DS-12, CONTEXT | Route inventory unknown. |
| 27 | Durable memory / knowledge | proposed-packet | DS-30, DS-14, DS-12 | State contract proposal only. |
| Routing & delegation | | | | |
| 28 | Routes / adapters / fan-out | researched-not-run | DS-11, R-B, R-F, EXECUTION-FABRIC, ROUTE-CAPABILITIES | Nine routes mapped; values unmeasured. |
| 29 | Route legality / entitlement | researched-not-run | R-C, DS-24 | Counsel packet only; G-32 open. |
| Plugins & extensibility | | | | |
| 30 | Plugin / capability-graph contract | proposed-packet | R-A, DS-04, PLUGINS-AND-EDITIONS | Manifest schema proposed. |
| 31 | Sandbox / isolation / supply chain | researched-not-run | DS-04, DS-18 (G-10/G-19), R-G | WASI/WASM deferred; 3-axis trust. |
| 32 | Plugin import / cross-harness reuse | proposed-packet | R-G, R-I, R-M | Porting savings unmeasured (D-033). |
| Security & trust | | | | |
| 33 | Credential non-intermediation / launch | proposed-packet | R-E, DS-24, D-021, D-029 | Architecture, not tested property. |
| 34 | Untrusted input / prompt injection | gap | — | No lane owns it. |
| 35 | Secrets / egress / lifecycle | researched-not-run | DS-24, SECURITY | Threat-suite unrun. |
| 36 | Privacy / retention / deletion | researched-not-run | DS-07, DS-33 | `verified-complete` derived. |
| 37 | Canary / adversarial rerun | researched-not-run | DS-08, DS-03 | Never executed. |
| Tooling & effects | | | | |
| 38 | Tool model / effect settlement | covered-by-spec | M1B, DS-23, DS-32 | Receipts vs ACKs distinct. |
| 39 | MCP bridge / tool bounds | gap | DS-23 (MCP open) | Stdio bounds unresolved. |
| Multimodal I/O | | | | |
| 40 | Multimodal input / output | gap | — | Attachments/images/audio unmapped. |
| Autonomy & planning | | | | |
| 41 | Goal decomposition / GoalSpec | covered-by-spec | PLANNING, AUTONOMOUS-PLANNING, M1A | Planning slice built inert. |
| 42 | Long-horizon / self-scheduling | gap | DS-25, DS-30 (partial) | Bounded plugin only. |
| 43 | Scientific research ARM | researched-not-run | DS-14, SCIENTIFIC-RESEARCH | Hard-floor corpus unrun. |
| Optimization & adaptation | | | | |
| 44 | Perf engineering / complexity budget | researched-not-run | DS-10, R-O, PERFORMANCE-PLAN | Option-2 benefit unverified. |
| 45 | Adaptive learning / route feedback | gap | DS-11, DS-26 (partial) | Promotion metric open. |
| 46 | Quota / accounting | researched-not-run | DS-26, R-D, TELEMETRY | Counters candidate-only. |
| Observability & introspection | | | | |
| 47 | Telemetry / honest counters | researched-not-run | DS-26, TELEMETRY | `null` not `0`; adapter unrun. |
| 48 | Explain / replay debugging | gap | ARCHITECTURE (partial) | No owner. |
| Evaluation & verification | | | | |
| 49 | Verifier independence / acceptance | researched-not-run | DS-03, ACCEPTANCE, DS-08 | 480-candidate matrix unrun. |
| 50 | Benchmark science | researched-not-run | DS-10, DS-11, PERFORMANCE-PLAN | Manifest undefined. |
| Platform & OS conformance | | | | |
| 51 | OS platform profiles | researched-not-run | DS-19, FU-04, D-028 | Cells open. |
| 52 | Language / runtime | researched-not-run | DS-18, FU-01, D-028 | No selection. |
| Multi-node fabric & remote execution | | | | |
| 53 | Multi-node / remote execution | researched-not-run | DS-20, DS-05, D-020 | Failover plugin; authority pivot. |
| Workspace & repository graph | | | | |
| 54 | Workspace / repository graph | gap | CONTEXT (`RepositoryMap` only) | No dedicated lane. |
| Configuration & policy | | | | |
| 55 | Config architecture / resolver | covered-by-spec | DS-13, CLI | Schema frozen; syntax open. |
| Governance & licensing | | | | |
| 56 | Licensing / provenance / IP | researched-not-run | DS-33, R-C, R-H | Counsel-gated; no clearance. |
| Release / update / packaging | | | | |
| 57 | Release / update / packaging | researched-not-run | DS-25, R-O, PLUGINS-AND-EDITIONS | Channel/format unselected. |

## Gaps and frontier edges

- Workspace/repo graph (54) → **R-Y** (return intaken; unexecuted).
- Multimodal I/O (40) → **R-T** (return intaken; unexecuted).
- Long-horizon autonomy/self-scheduling (42) → **R-R** (extends D-025; unexecuted).
- Explain/replay debugging (48) → **R-V** (unexecuted).
- Adaptive learning/route feedback (45) → **R-S** (extends DS-11/DS-26, R-D; unexecuted).
- Accessibility (23) → **R-L / R-N** (terminal + graphical; unexecuted).
- MCP bridge/tool bounds (39) → `overnight-20261002/protocol-edges/` + **R-G** (unexecuted).
- Untrusted input/prompt injection (34) → **R-P** (unexecuted).
- Leases/forks (10) → DS-15 / DS-05 / **R-Y** (unexecuted).
- Quarantine/ambiguity/emergency stop (7) and per-adapter fencing (8) → DS-01 / DS-02 / DS-08 /
  DS-32 (unexecuted).
- Memory (27) → **R-Q**; sandbox/isolation (31) → **R-U**; evaluation (50) → **R-W**; node fabric
  (53) → **R-X**.
- Credential boundary (33) → **R-E**; plugin contract (30) → **R-A**; import (32) → **R-G**;
  fan-out (28) → **R-F**; verifier independence (49) and canary (37) → DS-03 / DS-08.

Every researched-not-run edge closes only when its named experiment runs and an independent
verifier reruns the exact candidate; a packet return is a proposal, not closure.

## Boundary limits

Nothing was installed, logged in, executed or benchmarked; no provider call, spend, counsel
contact, deployment or merge occurred. Statuses describe documentation coverage only.
`covered-by-spec` means a baselined doc states it, never that it is built, tested, entitled,
secure or accepted. Coverage of documentation is not qualification.

---
title: Recursion v3 scientific research hypotheses
status: hypothesis
last-updated: 2026-09-03
---

# Recursion v3 scientific research hypotheses

## Evaluation objective

Maximize verified development quality subject to owner-selected limits on subscription quota, metered cost, machine load, elapsed time, privacy, and human review attention. Report dimensions separately before constructing profile-specific scores.

Experiments use public, synthetic, or scrubbed repositories unless the owner explicitly authorizes a private canary. Private inputs and results remain local.

This file is the future research portfolio. The campaign-specific, preregistered resource
workloads and decision rules are in [PERFORMANCE-PLAN.md](PERFORMANCE-PLAN.md): H-012 maps to
PERF-001/002, H-013 to PERF-003, H-014 to PERF-004/007, H-003 to PERF-005, H-004/H-001 to
PERF-006, and H-015 to PERF-008. Neither list is runtime construction authorization.

## Hypotheses

| ID | Hypothesis | Minimum experiment | Falsifier or decision signal |
|---|---|---|---|
| H-001 | Content-addressed repository evidence reduces repeated scanning and input use across model families. | Run matched tasks with raw rescanning versus commit-addressed maps/search/gate artifacts. | No material input/latency reduction, or stale-cache errors offset savings. |
| H-002 | Deterministic provider-specific stable prefixes improve observable cache reuse without lowering answer quality. | Compare canonical and volatile prompt layouts on routes exposing reliable cache evidence. | Hit/billing improvement is absent, undocumented, or requires harmful prompt rigidity. |
| H-003 | Holding routes until safe checkpoints preserves cache/session value and reduces plan churn. | Compare checkpoint-driven routing with per-turn re-resolution under simulated capacity variation. | Route stability increases failures/wait enough to outweigh context savings. |
| H-004 | Hybrid compaction retains constraints and continuation quality better per token than native-only or prose-only compaction. | Repeated-cycle recall/continuation benchmark across supported harnesses and models. | Deterministic sidecar adds cost without reducing loss or recovery time. |
| H-005 | A non-lossy Owner Intent Ledger eliminates constraint-loss failures after compaction. | Adversarial long-session fixtures with amendments and conflicting older instructions. | Active intent is still omitted/misapplied despite valid ledger injection. |
| H-006 | One strong ARM with bounded specialist delegation beats an uncontrolled cheap swarm on accepted code per quota unit. | Matched multi-file tasks with fixed aggregate capacity and independent blind review. | Swarm dominates quality/efficiency without increasing review or conflict cost. |
| H-007 | Task-specific model suites beat one universal escalation ladder. | Backend, frontend, security, mechanical, docs, and integration corpus with route crossover analysis. | No stable task-class advantage or maintenance cost exceeds gain. |
| H-008 | Confidence-aware subscription shadow pricing preserves premium capacity for high-value phases. | Simulated and observed long goals with/without phase reserves and uncertain quota. | It strands capacity or forces lower-quality routes without improving final acceptance. |
| H-009 | Quality-first adaptive routing lowers total quota-equivalent cost versus cheapest-first routing. | Replay matched tasks using frozen route/catalog snapshots. | Predictor errors cause more repairs, escalations, or cost than static routing. |
| H-010 | Cross-family verification catches materially different defects from same-family review. | Blind review matrix by author/reviewer family on exact candidates. | No improvement after accounting for task class, cost, and reviewer strength. |
| H-011 | Clean evidence-only verifier context reduces anchoring and false agreement. | Randomize verifier packets with and without implementer narrative. | Narrative improves defect detection without causing measurable confirmation bias. |
| H-012 | SQLite WAL plus content-addressed artifacts fits a small coordinator with negligible idle cost. | Soak representative events, projections, observers, backups, and worker churn on target hardware. | Sustained lock, WAL, I/O, memory, recovery, or maintenance cost violates measured budget. |
| H-013 | Compiled lazy plugin graphs provide extensibility with near-zero disabled cost. | Measure core against increasing installed-but-disabled and enabled plugin sets. | Discovery/load/startup or resident cost grows materially while plugins are disabled. |
| H-014 | Adaptive admission maintains interactivity and throughput better than a fixed worker cap. | Controlled CPU/RAM/I/O/foreground workloads with matched task queue. | Governor oscillates, underutilizes, or reacts too slowly relative to fixed profiles. |
| H-015 | Manifest-first lazy context hydration reduces node transfer and start latency without increasing missing-context retries. | Remote task matrix with full transfer versus capsule manifest/on-demand artifacts. | Hydration round trips erase savings or create inconsistent context. |
| H-016 | Lightweight enrollment preflight can protect remote boundaries within seconds and zero model tokens. | Cold/warm runs across supported node classes and trust changes. | Required checks need long conformance or miss simulated identity/replay/config failures. |
| H-017 | Local outcome calibration improves route rankings without opaque online learning. | Shadow predictions, then controlled low-risk exploration with versioned features. | Rankings fail to generalize or require private/raw data and expensive recomputation. |
| H-018 | Model-aware compaction pools preserve development capacity and fidelity. | Compare primary-model, cheap-model, native, and dedicated compactor strategies. | Separate scheduling increases switches/cost without better recall or preserved capacity. |
| H-019 | The cross-provider Execution Lineage Contract materially reduces recovery and audit time. | Incident drills for crash, stale result, provider switch, verifier dispute, and budget question. | Operators still need raw logs/manual correlation, or instrumentation cost is excessive. |
| H-020 | A Recursion-owned native loop supplies value beyond retained Hermes and external CLIs. | Architectural spike and matched workflow comparison for minimal native, Hermes, and CLI engines. | Native loop duplicates mature behavior, expands maintenance/security surface, or underperforms without a unique required capability. |
| H-021 | Direct ARM topics reduce owner coordination work without weakening Head awareness or losing instructions. | Matched workflows through Head-only relay versus direct ARM conversation with canonical event capture. | Direct access increases contradictory directives, lost context, or owner review time. |
| H-022 | Head-routed or event-mediated multi-ARM rooms enable useful collaboration without a new executive tier. | Synthetic shared-room workflows with simultaneous commands, disagreement, actor replacement and cross-goal requests. | Transcript order becomes authority, cycles/deadlocks grow, or a hidden AI ARM Manager is required. |
| H-023 | Configurable `checkpoint`, `interrupt` and `drain` PAUSE policies can preserve bounded work without admitting unauthorized effects. | Fault matrix across model turns, local transactions, subprocesses, disconnected nodes, gates and publication. | Any mode admits a post-pause effect outside its declared boundary or cannot reconcile ambiguity. |
| H-024 | A capability-vector Full Access model provides genuine owner control with less accidental authority than one ambient boolean. | Threat-model and usability comparison including control plane, credentials, spending, publication, merge, deployment and service grants. | Users cannot predict effective power, or actors self-widen/retain authority after revocation. |
| H-025 | Risk-scaled verifier separation improves defect discovery per review cost. | Blind author/reviewer matrix varying task, context, session, model, family, provider and host. | Added separation does not find materially different defects after controlling for reviewer capability. |
| H-026 | Unsigned local plugins can retain complete feature expressiveness while sensitive authority remains digest-pinned and explicit. | Install/update/substitution fixtures comparing warning-only, developer-mode and capability-grant policies. | The safe policy cripples local use, or warning-only permits unnoticed supply-chain/authority expansion. |
| H-027 | The proposed aggregate cutover gate prevents dual writers and distinguishes reversible from reconciliation-only effects. | V2 fixture import plus crash injection at every fence, transaction and external-effect boundary. | A stale writer succeeds, state histories diverge, or restoration repeats an accepted effect. |
| H-028 | Adaptive branch admission protects both machine and human review capacity better than a fixed 75-branch rule. | Run PERF-009 across workstation and coordinator profiles with controlled owner review throughput. | Policy oscillates or admits more unreviewed work without improving accepted throughput. |
| H-029 | Scoped encryption, physical expiry and minimal tombstones can delete private raw artifacts while retaining sufficient audit lineage. | Backup/cache/node deletion drills plus disclosure and restore attempts after expiry. | Content remains recoverable, tombstones leak sensitive equality/membership, or audit becomes insufficient. |
| H-030 | A daemon-owned actor/process runtime lets multiple terminal windows attach and detach without orphaning work or multiplying model/resource cost. | Cross-platform attach/detach, terminal crash, daemon restart and process-tree kill suite with several concurrent views. | Closing a terminal loses work, stale clients mutate state, descendants escape termination, or each view adds execution cost. |
| H-031 | Incremental non-flicker rendering plus graph-and-stream views improves multi-agent comprehension over interleaved transcript output. | Usability and resource comparison under concurrent ARM/worker messages, resize, slow clients and high-output tools. | Input is corrupted, causal identity is unclear, important events are missed, or rendering cost/backpressure harms execution. |
| H-032 | A small privileged kernel plus physically optional plugins reduces audit/maintenance and idle cost without fragmenting product semantics. | Compare core size/dependencies/startup/idle and change impact against incremental-monolith and fuller-native-loop prototypes; include subsystem ablation. | Adapter/plugin complexity recreates multiple products, or mandatory glue outweighs the code removed from core. |
| H-033 | Task-specific model/harness/delegation suites improve accepted outcomes per quota and owner-review unit. | Contamination-aware blind corpus with fixed goals/gates across task classes and delegation shapes. | Gains disappear across versions/tasks or repair/review cost exceeds routing savings. |
| H-034 | Supported cache/session controls plus local evidence reuse reduce repeated work without fidelity or privacy loss. | Route-pinned cold/warm/session/prefix/evidence-cache/capsule comparison with directly observed counters only. | Savings are unverifiable, version-fragile, privacy-crossing or offset by stale-context defects. |
| H-035 | One versioned configuration schema can keep deep customization explainable and safe across files, CLI, Telegram, plugins, goals and nodes. | Novice/expert tasks plus inheritance, concurrent edit, migration, rollback and invalid-combination fixtures. | Effective authority cannot be explained or the interaction space becomes untestable. |
| H-036 | A research ARM can retrieve and reconcile scholarly evidence more reliably than ordinary web-search narration. | Public benchmark with real/false/retracted/conflicting papers, persistent identifiers, reproducible extraction and independent source audit. | Citations are fabricated/misapplied, contradictions disappear, or provenance/copyright/privacy cannot be enforced. |
| H-037 | V3 improves declared user outcomes enough to justify its added code and operational complexity over v2 and simpler options. | Matched end-to-end v2/Option-1/Option-2/native-spike scenarios across the optimization envelope plus ablations. | No material accepted-quality, recovery, usability or efficiency gain survives hard floors and maintenance cost. |

## Benchmark design rules

- Freeze exact repository, task, GoalSpec, route/catalog snapshot, configuration, and randomization inputs.
- Use controller-owned gates plus independent blinded review.
- Include failures, ambiguous requirements, recovery, and multi-task integration—not only happy-path coding.
- Report input/output/cache/reasoning usage only when directly observed; label estimates and unknowns.
- Include human review time and post-completion defects.
- Repeat enough trials to show variance; do not declare a default from one impressive run.
- Record model/provider/harness versions because results expire when they change.
- Avoid private source in published corpora and reports.
- Pre-register the decision rule before running expensive comparisons.

## Initial priority

The next architecture-proof campaign prioritizes H-020 through H-037, with H-012 retained as
the coordinator feasibility gate. H-020/H-021/H-022/H-030/H-031 decide the harness, terminal and ARM interaction
boundary; H-023/H-024/H-025/H-026 decide authority and assurance contracts; H-027/H-028/H-029
decide migration, capacity and privacy; H-032–H-037 test leanness, model quality, cache/context,
configuration, scientific research and whole-product value. Execute the scoped lanes and source rules in
[RESEARCH-AGENDA.md](RESEARCH-AGENDA.md).

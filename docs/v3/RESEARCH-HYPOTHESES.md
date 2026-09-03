---
title: Recursion v3 scientific research hypotheses
status: hypothesis
last-updated: 2026-09-02
---

# Recursion v3 scientific research hypotheses

## Evaluation objective

Maximize verified development quality subject to owner-selected limits on subscription quota, metered cost, machine load, elapsed time, privacy, and human review attention. Report dimensions separately before constructing profile-specific scores.

Experiments use public, synthetic, or scrubbed repositories unless the owner explicitly authorizes a private canary. Private inputs and results remain local.

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

Prioritize H-020, H-012, H-004, H-001, and H-006. They decide the native-runtime boundary, target-host feasibility, context architecture, shared evidence value, and ARM/delegation shape. The remaining routing optimizations depend on those foundations.

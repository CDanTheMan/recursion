---
title: Recursion research and decision index (anti-drift map)
status: maintained-index
last-updated: 2026-10-02
---

# Recursion research and decision index

A single map of every research wave, intake, packet, experiment, decision and gate, so no
knowledge is lost between sessions and stale artifacts are visible rather than silently reused.
When adding an artifact, add a row here. When superseding one, mark it `superseded` and keep the
path (a ruled-out approach without its reason is a dead end waiting to be rediscovered).

## Authority and identity

| Item | Path | Status |
|---|---|---|
| Control plane (governance) | `CONTROL_PLANE.md` | current |
| Anchor (mission/scope) | `ANCHOR.md` | current (active parent goal) |
| Active parent goal | `state/goals/goal-recursion-v3-harness-orchestrator.md` | active |
| Superseded parent goal | `state/goals/goal-recursion-v2-execution-fabric.md` | superseded (v2/Hermes retired, D-017) |
| Decision log | `state/DECISIONS.md` | current (D-001…D-033) |

## Decisions (state/DECISIONS.md)

- **D-017** v3 greenfield; v1/v2 retired.
- **D-018** native harness **and** unifying wrapper; no lock-in.
- **D-019** comprehensive build; lean opt-in install (Dot's "smaller release" rejected).
- **D-020** availability: auto node takeover required; single-node core + failover plugin (closes G-06).
- **D-021** delegation over credential intermediation.
- **D-022** one pause/stop vocabulary (Aggressive/Full/Lazy + checkpoint/interrupt/drain).
- **D-023** Codex App Server is the first qualification priority.
- **D-024** headline differentiator = productive continuity; six journeys as acceptance scenarios.
- **D-025** continuing autonomous research = optional bounded plugin.
- **D-026** Apache-2.0 direction; community/porter posture.
- **D-027** counsel packet authorized (no spend).
- **D-028** platform floors (closes G-11).
- **D-029** operator-provisioned trusted launch boundary.
- **D-030** harness-native driving + headless fan-out; Recursion owns the JSON stream (subject to counsel).
- **D-031** no vendor-sabotage claim.
- **D-032** parent goal is v3; sweep retired Hermes wording from prompts.
- **D-033** plugin import/port is a hypothesis to validate.

## Research waves and intakes

| Wave | Path | Status |
|---|---|---|
| 28 Deep Research lanes (DS-01…DS-34) | `research-lane/wave-{a,b,b2,c}-20260930/`, `SYNTHESIS.md`, `GAPS.md`, `synthesis/domain-*.md` | complete at specification level; nothing executed |
| DS prompt suite (31) | `prompts/research-suite-20260929/` (+`check_suite.py`) | issued |
| FU-01…FU-05 prompts | `prompts/followups-20261001/` (+`check_followups.py`) | issued |
| FU-01…FU-05 return intake | `research-lane/followups-20261002/` (+`check_intake.py`, `machine/`) | intaken; specs only |
| R-A…R-D prompts | `prompts/dot-research-20261002/` (+`check_research_stack.py`) | issued |
| Scope-reframe handoff intake | `research-lane/scope-reframe-20261002/` (+`check_intake.py`) | intaken |
| R-A…R-D return (46 questions) | `research-lane/dot-ra-rd-20261002/` (+`check_intake.py`, `synthesis/SYNTHESIS.md`) | intaken; proposals only |
| R-A/R-B reconciliation | `research-lane/dot-ra-rd-20261002/synthesis/RECONCILIATION.md` | draft contract candidates |
| R-E…R-H prompts | `prompts/dot-research-20261002b/` (+`check_research_stack.py`) | issued (zip: `Recursion_Dot_Research_Packet_20261002b.zip`) |
| Next-phase runbook | `research-lane/NEXT-PHASE.md` | maintained |

## Specs and design baselines (docs/v3)

| Doc | Role |
|---|---|
| `PRODUCT.md` | thesis, promises, non-goals (D-018/D-031 revision pending reconciliation) |
| `INTERFACE-STRATEGY.md` | adopted CLI/TUI/GUI baseline (D-024) |
| `PLUGINS-AND-EDITIONS.md` | kernel/plugin boundary; opt-in install; availability backend (D-020) |
| `ROADMAP.md` | pipeline: FU-03 → FU-04 → FU-01/02/05 → selections |
| `ARCHITECTURE.md`, `STATE.md`, `EXECUTION-FABRIC.md`, `DECISION-REGISTER.md`, `CLAIM-LEDGER.md` | current specs; **contain deferred drift** (retired Hermes/v2 claims) — WS6 |

## Experiments (executed evidence)

| Experiment | Path | Result |
|---|---|---|
| FU-03 model | `experiments/v3/fu-03-formal-model/` | reduced-bound TLC baseline clean; 5/7 instantiated mutants killed (`check_fu03*.py`) |
| FU-04 OS conformance | `experiments/v3/fu-04-os-conformance/` | safe probes + bounded 20-trace harness; 12 pass / 0 fail / 1 unknown / 13 not_run; floors pinned (D-028) |

## Gates and tools

`tools/check_public_scope.py`, `tools/check_next_phase.py`, `tools/check_rescope.py`,
`tools/check_v3_orientation.py` (scope-frozen to the 2026-09-13 repair), the research-lane
`check_intake.py`/`check_*` checkers, and the prompt-suite checkers.

## Review branches (nothing pushed; Lucas reviews/merges)

`loop/work/rescope-20261002` · `loop/work/fu-03-formal-model` · `loop/work/fu-04-os-conformance` ·
`loop/work/dot-ra-rd-20261002` · `loop/work/prompt-authority-sweep-20261002` ·
`loop/work/orchestrator-reconciliation-20261002`.

## Drift rules (why previous iterations drifted)

1. Every artifact gets an evidence class and a status; `unknown` is never zero.
2. Superseded artifacts stay in place with a reason; never delete the reasoning.
3. Prompts inherit **current** authority only — the retired Hermes-control wording was swept on
   2026-10-02 (D-032); do not reintroduce it.
4. Research output is evidence, not decision; only `state/DECISIONS.md` records Owner choices.
5. New waves are added to this index and to `NEXT-PHASE.md` the day they land.

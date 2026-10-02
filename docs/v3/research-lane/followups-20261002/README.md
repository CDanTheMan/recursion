---
title: Follow-up batch 20261002 — Deep Research specs, batch review and architecture audit
status: research-evidence-not-a-decision
parent-goal: goal-recursion-v2-execution-fabric
---
# Follow-up batch 2026-10-02 intake

Outputs from the Codex Dot for the five follow-up research briefs (`docs/v3/prompts/followups-20261001/`),
plus a batch supporting review, a read-only repository architecture audit, and proposed FU-04
machine-readable specifications.

**Status: specification and design only.** These reports propose experiments, contracts and
fixtures; they did **not** run the target experiments, model checker, benchmarks, chaos cases or
platform qualification. They cannot close G-01–G-05 by themselves. No language, store, database,
protocol revision or product default is selected. Evidence inputs only — not Owner decisions.

## Contents

| Raw report | Role | Synthesis |
|---|---|---|
| `raw/ds-FU-01-language-runtime.md` | FU-01 language/runtime experiment spec (G-01) | `synthesis/FU-01-language-runtime.md` |
| `raw/ds-FU-02-store-crash-replay.md` | FU-02 canonical store crash/replay benchmark spec (G-02) | `synthesis/FU-02-store-crash-replay.md` |
| `raw/ds-FU-03-formal-model-vectors.md` | FU-03 formal model, mutants and byte conformance spec (G-03) | `synthesis/FU-03-formal-model-vectors.md` |
| `raw/ds-FU-04-os-conformance.md` | FU-04 OS platform conformance fixtures spec (G-04) | `synthesis/FU-04-os-conformance.md` |
| `raw/ds-FU-05-broker-chaos.md` | FU-05 broker protocol freeze blockers and chaos spec (G-05) | `synthesis/FU-05-broker-chaos.md` |
| `raw/ds-batch-supporting-review.md` | Cross-report execution handoff (Stages 1–4) | `synthesis/batch-supporting-review.md` |
| `raw/ds-architecture-audit.md` | Read-only repository architecture audit | `synthesis/architecture-audit.md` |

Proposed machine-readable FU-04 specifications are under `machine/`
(`platform-manifest.json`, `negative-traces.json`, `profile-fields.json`, `source-register.json`
and their schemas). They ship with empty results and were parsed/validated, never executed.

`MANIFEST.json` and `START-HERE.txt` are the packet's own provenance and index.

## Key points to carry forward

- The architecture audit is pinned to commit `3a542c6bbd88351e6f6c5eceffd317bc2450fcad` and is a
  static snapshot: nothing was executed and it is not retroactive proof that any experiment ran.
- FU-03 and FU-04 are prerequisite lanes; FU-01, FU-02 and FU-05 are dependent experiments.
- The batch review's execution sequence: reconcile authority/pins, run the two prerequisite
  lanes, run the dependent experiments, then independent acceptance.
- Authority clarification: Hermes-led repository control is retired; v3 is standalone and also
  wraps/orchestrates upstream harnesses, preserving native, upstream-only and combined workflows.
- The audit flags authority/scope drift to repair before construction, and warns against
  retrofitting the frozen M1 wire contracts to match newer research.

## Gate

```text
python -X utf8 -B docs/v3/research-lane/followups-20261002/check_intake.py
```

## Non-goals

- No spec rewrite, no selection, no experiment execution, no construction, no deployment.
- No claim that any report was independently reproduced or that any Owner decision follows.

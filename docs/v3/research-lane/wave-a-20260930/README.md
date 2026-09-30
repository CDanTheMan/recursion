---
title: Wave A Deep Research intake — 2026-09-30
status: research-evidence-not-a-decision
parent-goal: goal-recursion-v2-execution-fabric
---
# Wave A Deep Research intake (2026-09-30)

Raw outputs and syntheses from Wave A of the Recursion v3 Deep Research prompt suite
(`docs/v3/prompts/research-suite-20260929/`). These are **evidence inputs**: not Owner
decisions, not accepted specifications, and not independently verified. No recommendation in
this directory is a technology selection.

## Contents

| Raw report | Source prompt | Synthesis |
|---|---|---|
| `raw/ds-1-deep-research-methods.md` | none — Deep Research capability briefing | `synthesis/meta-deep-research-methods.md` |
| `raw/ds-3-DS-18-language-runtime.md` | DS-18 implementation language and runtime | `synthesis/DS-18-language-and-runtime.md` |
| `raw/ds-2-DS-22-formal-model.md` | DS-22 formal model and conformance vectors | `synthesis/DS-22-formal-model-and-conformance-vectors.md` |
| `raw/ds-4-DS-21-state-store.md` | DS-21 canonical state store and persistence faults | `synthesis/DS-21-canonical-state-store.md` |
| `raw/ds-5-DS-20-linux-scaling.md` | DS-20 Linux service topology and enterprise scaling | `synthesis/DS-20-linux-service-topology.md` |

## Labels

Each raw report carries a provenance block at the top: source prompt, session, retrieved
date, `status: research-evidence-not-a-decision`, and a `verification` note (not
independently verified by Recursion). Each synthesis keeps the report's own evidence classes
(source-documented / inferred / unknown) and states what the report does **not** prove.

## Wave A completeness

- **Completed:** DS-18, DS-20, DS-21, DS-22.
- **Missing:** **DS-19 (operating-system platform behavior)** — not in the delivered set.
  Its Windows/POSIX process, PTY/ConPTY, filesystem and service semantics overlap DS-23 and
  DS-09; run DS-19 before or alongside those.
- `ds-1` is a supporting briefing about the Deep Research capability, not a lane result.

## Verdict — is Wave B unblocked?

**Research: yes, with conditions. Construction: no change.**

- Wave A returned **no blocking decisions and no selections**. It recommends experiments and
  gates (a language experiment, a formal model, a store fault benchmark, service topology
  guidance), so nothing in Wave B is gated on a choice that does not yet exist.
- Wave B prompts are provider-free research and do not require a selected language or store.
  They can run under the existing "unselected" framing.
- **One real gap:** DS-19 was not run. Sequence it first (or with DS-23) so the OS-level
  facts DS-23 depends on are present.
- **Construction stays blocked**, which is expected and not a Wave B blocker: language/store
  selection is Owner-gated, and DS-22's condition (model + mandatory mutants + byte-level
  vectors + two independently written bit-identical implementations) must hold before the
  four-function kernel API is frozen. DS-21's canonical crash/replay benchmark and DS-18's
  `EXP-FHAR-10` language experiment are likewise pre-construction gates, not Wave B gates.
- Watch these cross-lane dependencies while running Wave B: DS-23 ↔ DS-19 (OS seams);
  DS-25 ↔ DS-21/DS-20 (backup/restore; `esc-0013` remains an open Owner escalation);
  DS-26 ↔ DS-18/DS-20 (resource and counter `unknown`s).

## Gate

From the repository root:

```text
python -X utf8 -B docs/v3/research-lane/wave-a-20260930/check_intake.py
```

The check is deterministic and provider-free: it verifies the expected files exist, that each
raw report carries its provenance label, that each synthesis has the required sections, that
relative links resolve, and that no foreign-project identifiers or obvious secrets appear.
A PASS certifies structure and labeling only — not scientific correctness or acceptance.

## Non-goals

- No spec rewrite, no selection, no construction, no deployment, no publication.
- No claim that any report was independently reproduced or that any Owner decision follows.

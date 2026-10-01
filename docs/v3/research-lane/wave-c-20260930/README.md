---
title: Wave C Deep Research intake — 2026-09-30
status: research-evidence-not-a-decision
parent-goal: goal-recursion-v2-execution-fabric
---
# Wave C Deep Research intake (2026-09-30)

Reports from the Wave C run batch (plus the DS-05 re-run). Evidence inputs only: not Owner
decisions, not accepted specifications, and not independently verified.

## Completed this batch

| Raw report | Source prompt | Synthesis |
|---|---|---|
| `raw/ds-DS-05-migration-rollback.md` | DS-05 single-writer migration and effect rollback (successful re-run) | `synthesis/DS-05-migration-rollback.md` |
| `raw/ds-DS-10-performance.md` | DS-10 performance and complexity budget | `synthesis/DS-10-performance.md` |
| `raw/ds-DS-11-routing-delegation.md` | DS-11 model routing and delegation science | `synthesis/DS-11-routing-delegation.md` |
| `raw/ds-DS-12-context-cache.md` | DS-12 context compaction and cache economics | `synthesis/DS-12-context-cache.md` |
| `raw/ds-DS-13-configuration.md` | DS-13 configuration architecture and operator control | `synthesis/DS-13-configuration.md` |
| `raw/ds-DS-14-scientific-arm.md` | DS-14 scientific research ARM and scholarly evidence | `synthesis/DS-14-scientific-arm.md` |
| `raw/ds-DS-30-multi-project-memory.md` | DS-30 multi-project supervision state and memory | `synthesis/DS-30-multi-project-memory.md` |
| `raw/ds-DS-32-hitl-approvals.md` | DS-32 human-in-the-loop approvals, forwarding and consultation | `synthesis/DS-32-hitl-approvals.md` |
| `raw/ds-DS-33-licensing-ip.md` | DS-33 licensing, distribution, provenance and IP clearance | `synthesis/DS-33-licensing-ip.md` |
| `raw/ds-DS-34-decision-journaling.md` | DS-34 decision journaling and calibration (Codex route) | `synthesis/DS-34-decision-journaling.md` |

DS-33 is legal-risk research, **not legal advice**; counsel is required before any release
decision.

## Failed this batch

- **DS-15** returned a "Deep Research Scoping Plan" (a plan, not the research) for the second
  time. Preserved at `failed/ds-DS-15-partial-plan.md`; not accepted as a report. The directive
  in every handoff now also explicitly rejects scoping plans, research plans, methodologies and
  timelines, and requires findings and citations.

## DS-34 via an alternative route

DS-34 (decision journaling and calibration) could not run on Deep Research within the rate
limit. It was produced with Codex instead, from the same self-contained brief, extracted from a
`.docx`, and intaken here. The same labeling and verification caveats apply as for every other
report (research evidence, not an Owner decision, not independently verified).

## Prompt adjustment applied

All 31 handoffs in `docs/v3/prompts/research-suite-20260929/` now end their directive with:
"…do not return a scoping plan, research plan, methodology, timeline, outline, or clarification
request — those are not acceptable outputs. Execute the research now and return the final
report with findings and citations…". `check_suite.py` still passes.

## Lanes still needing a run

`DS-15` (re-run). It returned a scoping plan twice; if a third attempt still plans, split it
into its five clusters.

## Gate

```text
python -X utf8 -B docs/v3/research-lane/wave-c-20260930/check_intake.py
```

## Non-goals

- No spec rewrite, no selection, no construction, no deployment, no publication.
- No claim that any report was independently reproduced or that any Owner decision follows.

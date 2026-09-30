---
title: Wave B Deep Research intake — 2026-09-30
status: research-evidence-not-a-decision
parent-goal: goal-recursion-v2-execution-fabric
---
# Wave B Deep Research intake (2026-09-30)

Reports from the second Deep Research run batch, plus the analysis of the runs that **failed
closed**. These are evidence inputs only: not Owner decisions, not accepted specifications,
and not independently verified.

## Completed this batch

| Raw report | Source prompt | Synthesis |
|---|---|---|
| `raw/ds-DS-19-os-platform-behavior.md` | DS-19 operating-system platform behavior | `synthesis/DS-19-os-platform-behavior.md` |
| `raw/ds-DS-23-ipc-process-broker.md` | DS-23 IPC, process broker and terminal protocol | `synthesis/DS-23-ipc-process-broker-and-terminal-protocol.md` |
| `raw/ds-DS-24-credentials-egress.md` | DS-24 credentials, enrollment, egress and secret lifecycle | `synthesis/DS-24-credentials-enrollment-egress-and-secret-lifecycle.md` |

DS-19 was the missing Wave A lane; it is delivered here. DS-23 and DS-24 are Wave B lanes.

## Failed runs

`failed/` preserves 11 outputs that failed closed; `FAILED-RUNS.md` maps each to its intended
lane. Cause: the Deep Research session received the handoff as an uploaded document with an
**empty query field**, so it reported an "unspecified query" and refused to treat the
`proposed-inert` brief as authorization. This is a launch-procedure defect, not a research
result. Three failed runs did not name a lane (`unidentified`).

## Prompt correction (applied)

Every handoff in `docs/v3/prompts/research-suite-20260929/` now carries a
`Session query — explicit invocation` line immediately after its front matter. Put the file
contents in the Deep Research **query** box (primary), or put that one line in the query box
and attach the brief. `check_suite.py` enforces the line.

## Lanes still needing a run

No completed report yet: `DS-25`, `DS-26`, `DS-01`, `DS-02`, `DS-03`, `DS-04`, `DS-05`,
`DS-06`, `DS-07`, `DS-08`, `DS-09` (Wave B), and `DS-10`, `DS-11`, `DS-12`, `DS-13`, `DS-14`,
`DS-15`, `DS-30`, `DS-32`, `DS-33`, `DS-34` (Wave C).

## Gate

```text
python -X utf8 -B docs/v3/research-lane/wave-b-20260930/check_intake.py
```

## Non-goals

- No spec rewrite, no selection, no construction, no deployment, no publication.
- No claim that any report was independently reproduced or that any Owner decision follows.

---
title: Wave B failed Deep Research runs — diagnosis and re-run instruction
status: research-ops-note
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
---

# Wave B failed Deep Research runs (2026-09-30)

Eleven Deep Research outputs landed in `failed/` because their session could not act on the
intended lane. This note diagnoses the shared cause, maps each report to the DS handoff it
names, and gives the corrective instruction a re-run needs. It is read-only with respect to
the failed reports and does not edit any other file.

## Diagnosed cause

All eleven runs share one failure mode:

1. **Empty query field.** The session was launched with `[$deep-research]` and no subject text.
   Every report opens by stating that no substantive topic/query was specified.
2. **Brief supplied only as an attached/uploaded document.** The intended DS handoff reached
   the session as an attachment, not as the query.
3. **`proposed-inert` status read as a refusal condition.** Each brief self-declares
   `proposed-inert` / "inert until explicitly invoked in a new session." With no query text to
   constitute the invocation, the model correctly declined to treat the upload as authorization
   and instead returned generic methodology, candidate-topic menus, or unrelated worked examples.

The models did not malfunction; they honored the briefs' invocation rule. The defect is in the
handoff: the invocation belonged in the query field and was left empty.

## Report-to-lane mapping

| Report file | Intended DS lane | Symptom | Action |
|---|---|---|---|
| `report-5.md` | DS-26 — Telemetry, accounting and honest status | Named DS-26 as the strongest candidate, then refused: brief is `proposed-inert`; produced a scope/evidence-map instead of the deliverable | Re-run DS-26 |
| `report-6.md` | DS-08 — Private canary methodology | Named DS-08, refused execution; returned a menu of five possible topics (A–E) for the operator to pick | Re-run DS-08 |
| `report-7.md` | `unidentified` | No DS lane named; produced a topic-neutral research protocol plus a remote-work worked example; mentions "a separate uploaded brief" without naming it | Re-run only after the operator names the lane |
| `report-8.md` | DS-25 — Update, release, rollback and disaster recovery | Named DS-25 only as a "model of rigor"; produced a generic six-week engagement blueprint with a climate-tech example | Re-run DS-25 |
| `report-9.md` | DS-01 — Pause, cancellation and effect fencing | Named DS-01 as an example of a strict specification; refused; produced a generic protocol/template | Re-run DS-01 |
| `report-10.md` | DS-07 — Privacy-preserving retention and deletion | Named DS-07, explicitly "not treated as the active research query"; produced a generic research architecture | Re-run DS-07 |
| `report-12.md` | DS-04 — Plugin trust and supply chain | Named DS-04 as a candidate topic; inert; produced a generic trust/supply-chain synthesis | Re-run DS-04 |
| `report-13.md` | DS-03 — Risk-scaled verifier independence | Named DS-03; `proposed-inert`; produced a generic verifier-independence synthesis | Re-run DS-03 |
| `report-14.md` | `unidentified` | No DS lane named; described an attached brief on single-writer migration/cutover but treated it as a context clue only | Re-run only after the operator names the lane |
| `report-15.md` | `unidentified` | No DS lane named; described an inert lane on capacity admission and review debt, then produced a portfolio of five unrelated topics | Re-run only after the operator names the lane |
| `report-16.md` | DS-09 — Interactive terminal and communication views | Named DS-09 in a scope note; declared `proposed-inert`; produced a generic research-design methodology report | Re-run DS-09 |

## Intended lanes still without a completed report

Named by the failed runs and not present as a raw or synthesis report under
`docs/v3/research-lane/`:

- DS-01 — Pause, cancellation and effect fencing
- DS-03 — Risk-scaled verifier independence
- DS-04 — Plugin trust and supply chain
- DS-07 — Privacy-preserving retention and deletion
- DS-08 — Private canary methodology
- DS-09 — Interactive terminal and communication views
- DS-25 — Update, release, rollback and disaster recovery
- DS-26 — Telemetry, accounting and honest status

Three failed reports (`report-7.md`, `report-14.md`, `report-15.md`) name no DS lane, so their
intended lanes are **unconfirmed** and cannot be added to this list without inventing one. Two
of them describe subjects that resemble DS-05 (single-writer migration and effect rollback) and
DS-06 (capacity admission and review debt); per the read-only rule this is recorded only as an
observation, not as a lane assignment.

For contrast, completed lanes present under `wave-a-20260930/` and `wave-b-20260930/` are
DS-18, DS-19, DS-20, DS-21, DS-22, DS-23 and DS-24. None overlaps the list above.

## Corrective instruction for a re-run

The invocation must be placed in the **query/text field** with the brief attached as supporting
context. Do not leave the query empty. Use this template:

```text
Execute Recursion research lane DS-NN — <lane title>. I am explicitly invoking this handoff
now. This message is the authorization the brief requires; its proposed-inert status is lifted
for this session only. Produce the source-pinned deliverable the brief defines, staying inside
its non-goals: read-only, no provider calls, no writes/commits, no deployment or publication,
no credential or configuration changes. Lead with the brief's own research questions and
completion gate.
```

Per-lane fill-ins (title from `docs/v3/prompts/research-suite-20260929/`):

| Lane | Query text to place in the query field |
|---|---|
| DS-01 | `Execute Recursion research lane DS-01 — Pause, cancellation and effect fencing. (Explicitly invoked; produce the source-pinned deliverable per the attached brief.)` |
| DS-03 | `Execute Recursion research lane DS-03 — Risk-scaled verifier independence. (Explicitly invoked; produce the source-pinned deliverable per the attached brief.)` |
| DS-04 | `Execute Recursion research lane DS-04 — Plugin trust and supply chain. (Explicitly invoked; produce the source-pinned deliverable per the attached brief.)` |
| DS-07 | `Execute Recursion research lane DS-07 — Privacy-preserving retention and deletion. (Explicitly invoked; produce the source-pinned deliverable per the attached brief.)` |
| DS-08 | `Execute Recursion research lane DS-08 — Private canary methodology. (Explicitly invoked; produce the source-pinned deliverable per the attached brief.)` |
| DS-09 | `Execute Recursion research lane DS-09 — Interactive terminal and communication views. (Explicitly invoked; produce the source-pinned deliverable per the attached brief.)` |
| DS-25 | `Execute Recursion research lane DS-25 — Update, release, rollback and disaster recovery. (Explicitly invoked; produce the source-pinned deliverable per the attached brief.)` |
| DS-26 | `Execute Recursion research lane DS-26 — Telemetry, accounting and honest status. (Explicitly invoked; produce the source-pinned deliverable per the attached brief.)` |

For `report-7.md`, `report-14.md` and `report-15.md`, the operator must first state the lane id;
until then no correct query string exists. Once named, use the same template.

Run one lane per sitting, as the suite README requires. A non-empty query alone is the fix; no
change to the briefs or the suite is needed.

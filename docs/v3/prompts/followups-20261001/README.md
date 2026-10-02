---
title: Follow-up research prompts — 2026-10-01
status: ready-for-explicit-invocation
last-updated: 2026-10-01
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: each handoff is self-contained; supplying the document launches its session
---

# Follow-up research prompts — 2026-10-01

This directory holds five self-contained Deep Research handoffs that close the P1 gaps in
[GAPS.md](../../research-lane/GAPS.md). They are follow-ups: each names the gap and the source
lane it extends, and each carries the same baked authority, scope, evidence and privacy context
as the first-wave `DS-*` suite. Supplying one document is its invocation; run one handoff per
sitting. None selects a language, store, protocol, renderer or runtime — every recommendation
stays evidence for an Owner decision.

The five gaps are the kernel/language/platform architecture blockers. They are deliberately few:
do not pad the wave. G-03 (formal model and byte vectors) is a prerequisite for G-01 (the
language experiment); G-04 (OS conformance fixtures) supplies platform facts that G-02 (the
store benchmark) and G-05 (the broker chaos matrix) assume.

## Index

| Prompt | Gap | Domain | Source lane(s) | Title |
|---|---|---|---|---|
| [FU-01](FU-01-language-runtime-experiment.md) | G-01 | A | DS-18 | Implementation language and runtime experiment (`EXP-FHAR-10`) |
| [FU-02](FU-02-canonical-store-crash-replay.md) | G-02 | A | DS-21 | Canonical state store crash and replay benchmark |
| [FU-03](FU-03-formal-model-and-conformance-vectors.md) | G-03 | A | DS-22 | Formal model, guard mutants and byte-level conformance vectors |
| [FU-04](FU-04-os-platform-conformance-fixtures.md) | G-04 | A | DS-19 | Operating-system platform conformance fixtures |
| [FU-05](FU-05-broker-protocol-chaos.md) | G-05 | A | DS-23 | Process broker protocol freeze blockers and native chaos matrix |

## Running a session

Supply the `FU-*.md` document to the session. It opens with a research directive that names the
task, authorizes the investigation and forbids asking which topic to research. Nothing else has
to be typed, and the document does not depend on a repository connector — all context is baked
in under `## Baked context`.

## Authority

Each handoff is self-contained: a Deep Research session needs no repository access because the
shared authority, scope, evidence and privacy context is baked into every file. The operator
should read [CONTROL_PLANE.md](../../../../CONTROL_PLANE.md), `ANCHOR.md` and `AGENTS.md` before
invoking a session. Hermes-led control was retired on 2026-09-28 (state/DECISIONS.md D-017); these prompts propose no
amendment and never edit a protected path. Public sessions receive only public or synthetic
briefs — never secrets, credentials, personal data, private repository content, local paths or
account/infrastructure identifiers.

The prior evidence these prompts extend is the four domain syntheses under
`docs/v3/research-lane/synthesis/` and the 28 lane syntheses under `docs/v3/research-lane/wave-*/synthesis/`.
The consolidated gap register is [GAPS.md](../../research-lane/GAPS.md).

## Gate

Run from the repository root:

```text
python -X utf8 -B docs/v3/prompts/followups-20261001/check_followups.py
```

The check is deterministic and provider-free. It fails unless every `FU-*.md` file exists, has
the required front matter, contains the research directive and the eight required headings, is
referenced by this README, and has only resolving relative links, with no obvious secret material
and no other-project identifier (reusing `tools.check_public_scope.PATTERN`). A passing check
certifies structure only — not scientific content, source quality or Owner acceptance.

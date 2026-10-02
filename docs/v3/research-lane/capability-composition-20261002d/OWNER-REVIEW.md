---
title: Capability-composition Owner review (packet d) — decisions requested
status: owner-review-requested
last-updated: 2026-10-02
---
# Capability-composition Owner review

The R-PC / R-UI / R-MOB return is **research evidence, not adoption** (see `INTAKE-SYNTHESIS.md`).
This memo lists only the decisions that need **Lucas**. Each row gives the question, the options, a
recommendation, what it unblocks and the falsifier. Answering an item lets me record it in
`state/DECISIONS.md` (authoring session) and open the matching bounded task.

## Tier 1 — decide now (these gate the next work)

### O-01 — Offline-retention policy for mobile (R-MOB Q11)
The one genuine contradiction in the packet: a disconnected client **cannot** instantaneously learn
an unseen revocation, and no protocol can retract bytes already delivered. The literal requirement
"a cached view never serves content after a remote revocation" is therefore unsatisfiable offline.

| Option | Meaning |
|---|---|
| **A (recommended)** | **No private offline redisplay.** Private view is online-only; only minimal authorized status metadata may persist; reconnect re-authorizes before any private hydration; no automatic replay of queued actions. |
| B | Explicit **bounded offline snapshot** policy (must fix scope, encryption, expiry, audience, revocation-window honesty, storage/backup and accept no remote erasure). |
| C | Reject both — no mobile offline capability at all. |

- **Unblocks:** R-MOB MOB-F01–F24 fixture design (offline rows) and the mobile client contract.
- **Falsifier for A:** it blocks an authorized workflow that only B enables without weakening
  revocation honesty (if so, B is justified by evidence, not by convenience).

### O-02 — Authorize the provider-free conformance-fixture work
Authorize separate bounded local tasks to implement and independently verify the report fixtures:

- R-PC **F01–F18**; R-UI **UI-01…UI-20** (+ the C×V soak) against `recursion.ui-contract@candidate-2`;
  R-MOB **MOB-F01–F24** + the two-path connection simulation.
- Constraints (mandatory): provider-free; no install/live-host/credential/network action; every
  fixture needs a valid positive control, an adverse mutation and an independent oracle; an
  implementer PASS is not acceptance.

**Decision needed on the runtime.** To run fixtures you need an implementation language, and the
reports say language must not be chosen from research (that is FU-01 / a later Owner selection).
Two ways to proceed:

| Option | Meaning |
|---|---|
| **A (recommended)** | Authorize a **disposable test harness in an already-installed runtime (e.g. Python)** strictly as verification tooling — *not* a product-language selection; product language stays open (FU-01). |
| B | Require the FU-01 language/runtime selection **before** any fixture runs. |
| C | Authorize the **spec/design** of the fixtures now, defer execution until the language decision. |

### O-03 — Confirm D-034/D-019 supersede the older first-release GUI exclusions
R-UI flags a release-timing conflict: older "GUI later" exclusions vs D-019's comprehensive opt-in
build. D-034 already makes GUI/mobile optional client plugins.

- **Recommendation:** confirm **D-034/D-019 hold**; GUI and mobile are *built but opt-in*; nothing is
  removed. I would record a one-line clarifying decision citing the R-UI conflict row.
- **Unblocks:** removes an ambiguity that otherwise re-opens at every UI/mobile task.

## Tier 2 — research direction (one decision)

### O-04 — Commission the OS-specific design + language-expansion packet (`dot-research-20261002e`)?
Dot flagged a separately requested **OS-specific design + language expansion** that was *not* part of
revision 2. It feeds FU-01 (language/runtime) and must respect D-028 platform floors and the FU-03
kernel determinism / FU-02 store results.

- **Option A (recommended):** commission it now, scoped to candidate languages/runtimes evaluated
  against D-028 floors, FU-03 determinism, FU-02 store/replay, Windows-first, and the capability
  plugin/port hypothesis (D-033). No selection is made by the packet.
- **Option B:** defer until after the fixtures.
- **Option C:** scope it first (which OSes / which candidate languages).

## Tier 3 — defer (gated; do not need you today)

- **O-05** Normative adoption of the R-PC/R-UI/R-MOB candidate contracts — defer until independent
  fixtures exist and their results are reviewed. Report completeness is not adoption.
- **O-06** Authentication mechanism, transport/connection method, push provider, mobile distribution
  route — defer; G-32 counsel-gated; no selection from research.
- **O-07** Empirical study and live route/platform qualification — defer; spend/live human-gated.
- **O-08** Always-on Linux backend deployment shape — a deployment fact is not authorization; defer.

## What I do once you answer

- Record O-01…O-04 in `state/DECISIONS.md` (protected-path authoring session) as D-036+.
- Open the matching bounded task(s) / prompt packet (e.g. `dot-research-20261002e` for O-04).
- Leave O-05…O-08 open and visible in `GAPS.md` / `NEXT-PHASE.md`.

## Explicitly not requested

No language, store, framework, renderer, transport, auth mechanism, push provider or vendor is being
selected here; the frozen M1 wire profile, four-field `ArtifactRef` and eighteen-field
`ContentEnvelope` remain unchanged.

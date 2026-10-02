---
title: iOS/Android design + language expansion intake synthesis (2026-10-02)
status: research-evidence-not-a-decision
last-updated: 2026-10-02
---
# iOS/Android design + language expansion intake synthesis

Research evidence only — not adoption, not execution. Source: the hash-verified intake here
(`check_intake.py`). Two **advisory** reports for separately optimized native clients, pinned to
repo commit `b696f6e…`, consuming `recursion.ui-contract@candidate-2` (SHA-256 `23fa223b…`) and the
corrected R-MOB report (SHA-256 `b44826c1…`). All prototypes, device tests and performance
experiments are **UNEXECUTED**.

This is the "OS-specific design + language expansion" the capability-composition revision-2 notes
flagged as separately requested — the deliverable for Owner-review **O-04** (defined in the
capability-composition Owner review memo, tracked separately). The reports' own scope note records that the
later clarification authorizes **language/UI-stack advice** only, superseding the earlier
no-language-selection constraint **for this advisory comparison**; it does not ratify architecture,
select a floor, or authorize construction.

## Delivery identity

| File | SHA-256 |
|---|---|
| `README.md` | `d2369462…` |
| `ios/report.md` | `9ddffd72…` |
| `android/report.md` | `034419fc…` |

3 files sha256-verified.

## Recommendations (advisory, not adopted)

| Platform | Stack | Note |
|---|---|---|
| iOS | **Swift + SwiftUI** application shell; deliberately small **UIKit** boundary only for a measured hotspot | System glass for OS nav/controls only; not a claim Swift always beats React Native |
| Android | **Kotlin + Jetpack Compose** with a distinct Recursion design system; **Kotlin/Views** a whole-screen rival | Views-heavy and modern **RN New Architecture** are genuine comparators |

Both: preserve command meanings, the ten controls and three Stops, receipt facts, source-cut honesty
and candidate-2 contribution identity; **share contracts and parity fixtures before assuming shared
UI code is necessary.** The reports treat AI-assisted authoring as a reviewed end-to-end cost, not a
productivity multiplier.

## Shared boundary

Two apps, one product contract; GUI/mobile remain **optional client plugins over the secure backend**.
Reuse the four-field `ArtifactRef`, eighteen-field `ContentEnvelope`, one loss record and frozen M1B
vocabulary unchanged; no new base field, store or authority. Connected-and-authorized gate; **Detach
is not Stop**; "Stop unavailable while disconnected"; no automatic offline action queue; eight
receipt facts; seven capability states; per-target `input_lease`/`resize_lease`; zero new
inference/indexing/plugin activation on attach or view for an initialized profile.

## Intake flags (reconcile before implementation)

- **Fixture-ID namespaces differ.** R-MOB names its provider-free fixtures `MOB-F01…F24`; these
  reports use a shared **`MP01…MP11`** semantic matrix (iOS + Android) run against **one semantic
  oracle** — the iOS report permits per-platform stimuli, so do not claim a single shared event
  corpus. The two namespaces must be reconciled into one suite before running.
- **Android profile/manifest instances absent.** The Android report does not register a concrete
  `ClientCapabilityProfile@candidate-2` / `UiMaterializationManifest@candidate-2`; its design system,
  adaptive/foldable and accessibility rules must be expressed as those candidate-2 instances without
  altering candidate-2 or the `@1` point meanings.
- **Offline retention.** iOS reports it as "undecided" and compares online-only vs a bounded
  historical snapshot; it does **not** adopt R-MOB's conservative no-hydration hold. Owner decision
  **O-01** governs.
- **D-028 does not set an Android floor.** D-028 specifies backend platform floors only; minimum and
  target Android API and supported profiles remain open — do not infer an Android floor from D-028.
- **Pin.** Both reports pin `b696f6e…` (older than current master); reconcile newer commits before
  implementation (see the capability-composition intake's pin reconciliation).
- **Report-claimed context, not a recorded decision.** Both reports cite a "later user clarification"
  (reduced React Native interest) that authorizes language/UI-stack advice for this advisory
  comparison only. That clarification is **not recorded in the repository**; treat it as report
  context until an Owner decision records it.
- **Scope vs O-04.** The delivered packet is **mobile-client OS/design + language** (iOS/Android);
  the Owner review framed O-04 around D-028 floors and Windows-first. Reconcile that scope with the
  delivered mobile packet before acting.

## Unresolved Owner decisions (from the reports)

- Accept/reject the advisory stacks and design probes (without accepting a build or a platform floor).
- Supported device/OS floors per platform (iOS model/OS; Android min + target API separately); iPad
  multiwindow; Android adaptive/foldable support.
- **Private offline-retention policy** (flagged undecided by both reports; tracked as Owner
  decision **O-01** in the capability-composition Owner review memo).
- Authentication/key/recovery profile; transport + connection adapters; notification disclosure;
  device-assurance fallback; push vendor; distribution route (**G-32 counsel**).
- Prototype/test authorization and **finite budgets** (unset thresholds are not evaluable).
- No language, toolkit, renderer, store, auth mechanism, transport or push provider is selected here.

## Next steps (bounded, unexecuted)

- **Fake-backend prototype slices**, ≤3 variants (iOS: SwiftUI vs SwiftUI + targeted UIKit; Android:
  Compose vs Views vs RN), no account/live backend/provider/private content; freeze exact dependencies,
  package IDs, schemas and fixture manifests.
- **Shared `MP01…MP11` semantic matrix** with an independent oracle, a valid positive control, adverse
  mutations and a planted broken control; release builds only; simulator/emulator energy is not device
  energy.
- **Measurement dimensions:** frame/input/Stop reserve, memory, network, energy, lifecycle, human
  outcome, engineering cost; preserve failed/censored runs.
- Reconcile with R-MOB `MOB-F01…F24` into one suite; keep synthetic semantics separate from live
  device, store-policy and human accessibility qualification.

## Where this sits

- Owner review: capability-composition Owner review memo **O-04** (tracked in a separate PR; not on
  this branch).
- Index: `RESEARCH-INDEX.md`. Coverage: `ARCHITECTURE-COVERAGE.md`. Runbook: `NEXT-PHASE.md`.
  Gap register: `GAPS.md`.

## Boundary

Unexecuted; no apps built or installed; no stack, store, distribution, auth or transport selected;
no counsel clearance. Research evidence only.

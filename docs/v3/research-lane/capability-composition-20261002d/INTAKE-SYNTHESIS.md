---
title: Capability-composition intake synthesis (packet d, revision 2) — 2026-10-02
status: research-evidence-not-a-decision
last-updated: 2026-10-02
---
# Capability-composition intake synthesis

Research evidence only — not adoption, not execution. Source: the hash-verified revision-2 intake in
this directory (`check_intake.py`). The Dot returned three specification candidates — **R-PC**,
**R-UI**, **R-MOB** — pinned to repo commit `b696f6ece243b48c94fc0bbc7ee1d4b284c46f97`, tree
`a866969c9346372dcf74c2f05a7f9d648c766494` (includes PR 149 merge `e2e02af1…` and the following PR
148 merge). All target runtime/performance fixtures are **UNEXECUTED**.

## Delivery identity and provenance

| File | SHA-256 (revision 2) | Note |
|---|---|---|
| `rpc/report.md` | `4d4940f5…` | byte-identical to first delivery |
| `rui/report.md` | `23fa223b…` | corrected → `recursion.ui-contract@candidate-2` |
| `rmob/report.md` | `b44826c1…` | one line: candidate-1 → candidate-2 reference |
| `README.md` / `CORRECTIONS.md` | `1abd9c2c…` / `9dd8b227…` | revision-2 notes |

**Revision-2 correction.** The first R-UI delivery required supplier-qualified identity in prose but
used bare local IDs in several resolved records, so two suppliers sharing a local name linked
ambiguously. This was a specification defect, not an observed runtime failure. Candidate-2 adds
`ContributionKey` and `NodeKey`, resolves local fact/action/template/accessibility references only
inside their declared qualified namespace, rejects mismatched duplicated contribution/subject fields
between a node and its key, defines deterministic occurrence indices across nested repetitions with
tree-wide node-key uniqueness, and strengthens the UI-05 collision fixture. Semantic contribution-point
`@1` names/meanings are unchanged. Candidate-1 is historical; its schema identity is not reused.
Source: delivered `CORRECTIONS.md`.

## What landed

| Lane | Candidate artifact | One line |
|---|---|---|
| R-PC | `CompositionManifest` + eight-pass compiler (P1–P8) | Immutable, source-attributed composition manifest from an unprivileged deterministic compiler; exact read cut, mandatory closure, provenance map, prefix plan, fixed-budget increment experiment |
| R-UI | `recursion.ui-contract@candidate-2` | Typed contribution points compiled into a bounded semantic tree; supplier-qualified identity; fail-closed without concealing controls; ten-control and three-Stop parity |
| R-MOB | `MobileSessionBinding@candidate-1`, `MobileReadCacheBinding@candidate-1`, `NotificationHint@candidate-1` | Mobile as an optional, connected-only authorized projection/control; pairing delegates no executive role; offline honesty and no automatic replay |

### R-PC candidate names (not adopted)

`CompositionManifest`, `CompositionInputSet`, `CompositionReadCut`, `PrefixPlan`, `CacheObservation`,
`SpanSourceMap`, `CompositionPolicy`, `ScalingStudyManifest`. Passes **P1 Capture cut → P2 Resolve
eligible graph → P3 Protect mandatory closure → P4 Select optional material → P5 Admit disclosure and
loading → P6 Render candidate → P7 Validate fit and applicability → P8 Install and dispatch**. Typed
refusals `composition_cut_unavailable`, `mandatory_context_unfittable`, `reproduction_input_unavailable`;
dispositions REGRESSION / HOLD_UNKNOWN / NO_BENEFIT / CONDITIONAL_ADVANTAGE.

### R-UI candidate-2 delta (vs candidate-1)

New `ContributionKey` = full `Supplier` tuple + author-local ID; new `NodeKey` =
`(contribution_key, template_node_id, subject_ref, occurrence_index)` with deterministic depth-first
occurrence indices across the whole contribution. Projection/command/node/disposition records carry the
qualified key; local IDs resolve only within that exact namespace; duplicate keys refuse. `UiSemanticNode`
key/subject must equal its `NodeKey`; bare-ID fields cannot identify another supplier.

### R-MOB candidate names (not adopted)

`MobileSessionBinding@candidate-1`, `MobileReadCacheBinding@candidate-1`, `NotificationHint@candidate-1`;
connection-adapter boundary; receipt-fact projection. Consumes R-UI `@candidate-2`.

## Shared design boundary

The prompt compiler, UI materializer and mobile client consume authorized, versioned projections of the
same backend facts; they are not additional writers or permission sources. Imported/plugin/model content
carries `authority_carried_none=true`. Frozen M1 wire vocabulary, the four-field `ArtifactRef`, the
eighteen-field `ContentEnvelope`, one loss record and existing identity domains are reused unchanged; new
data is a versioned additive application facet, never a new base field or authority store.

## Open Owner gates (from the reports)

- Approve or decline the candidate composition precedence/policy and the R-UI taxonomy/schema/manifest
  (report completeness is **not** adoption).
- **Private offline-retention policy is unresolved** (R-MOB Q11): the literal "never serves across an
  unseen revocation" is impossible for a disconnected device; Owner must choose online-only status vs an
  explicit bounded offline snapshot, or reject both. No offline protected redisplay until decided.
- No language, store, framework, toolkit, renderer, transport, authentication mechanism or push provider
  is selected; G-09 (privacy/publication order), G-10 (renderer/runtime) and G-19 (containment) stay open.
- Any empirical study, live route/platform qualification and independent rerun need separate authorization
  and custody (spend/deploy/live actions are human-gated).

## Recommended next steps (from the reports)

1. Reconcile any newer repository commit against the pinned input before implementing.
2. Owner review of the candidate choices and unresolved policies — not adoption.
3. Implement independently checked controls and negative vectors under **separate bounded local tasks**:
   R-PC **F01–F18**, R-UI **UI-01…UI-20** (+ C×V soak), R-MOB **MOB-F01…F24** + the provider-free
   two-path simulation. Each needs a valid positive control, a mutation/adverse variant and an independent
   oracle that does not trust candidate flags.
4. Keep contribution/view counts, fixed aggregate resources and complete assigned cohorts explicit; never
   hide a quality, latency or authority regression behind another improvement.
5. Separate synthetic accounting/control tests from real model quality, human review, battery, platform
   isolation, connectivity and store-policy qualification.
6. New candidate identity per fix; return exact source/candidate identities and unresolved evidence.

Not yet actionable in-repo: the implementation language/platform and every technology choice remain
unselected (do not select from a research recommendation).

## Where this sits

- Commissioned by prompt packet `docs/v3/prompts/dot-research-20261002d/` (R-PC / R-UI / R-MOB).
- Index row: `RESEARCH-INDEX.md`. Coverage: `ARCHITECTURE-COVERAGE.md`. Runbook: `NEXT-PHASE.md`.
  Gap register: `GAPS.md`.

## Boundary

Every runtime, performance, model-quality, accessibility, containment and privacy claim here is
unexecuted. This intake records research evidence; it confers no adoption, no authority and no permission
to run.

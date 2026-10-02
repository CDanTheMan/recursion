---
title: R-A / R-B reconciliation (draft contract candidate)
status: draft-not-normative
last-updated: 2026-10-02
---

# Reconciliation — R-A and R-B against accepted decisions

## 1. Purpose and status

Reconciles R-A (plugin portability/contract) and R-B (cross-harness delegation) into shared
semantics against `state/DECISIONS.md` D-017..D-033, using `raw/00-assessment/report.md` and
`synthesis/SYNTHESIS.md`. It is a **draft contract candidate for Owner review — not adopted and
not normative**. It fixes shared names only; selects no language, store, framework, sandbox or
vendor; edits no protected path.

## 2. Shared-semantics crosswalk

Sources cite file § / key. Status ∈ aligned / conflict / needs-owner.

| Concept | R-A source | R-B source | Proposed merged definition | Conflicts/duplicates | Status |
|---|---|---|---|---|---|
| Capability/contribution model | R-A §3 `contributions[]`,`requires[]`; schema `contributions`,`requires` | R-B §5 capability tuple | Manifest *declares* static contributions/requests; RouteProfile *qualifies* a version-bound runtime capability tuple | R-A boolean required/optional vs R-B present/degraded/lost/unknown | needs-owner (mandatory families) |
| Effective-grant intersection | R-A §4 "effective invocation grant is the intersection…"; `records.AuthorityGrant.semantic_rule` | R-B §6 handoff kernel; grant_ref is not bearer | Semantic intersection of constitution, GoalSpec, parent grant, install/profile, manifest request, route enforcement, operation approval; re-checked live pre-effect | R-B adds pre-effect epoch recheck; no contradiction | aligned |
| Attenuation (parent containment) | R-A §4 items 1–8; schema `attenuation.parent_containment_required` | R-B §5 authority axis, §6 no widening | Child scope subset of parent in every dimension; unknown containment → refuse; depth/expiry/budget only decrease | none | aligned |
| Evidence + refusal taxonomy | R-A §7; contract `refusal_codes` (17); `records.EvidenceItem` | R-B §5 transition axes, §9 floors | One normalized refusal enum (R-A list) plus R-B loss reasons and `admission_unknown`; EvidenceItem is the per-attempt leaf | R-A 17 codes vs R-B reason vocabulary, not yet merged | aligned (merge needed) |
| HonestAccounting | contract `records.HonestAccounting` (`unknown_value: null`; measured/modelled/unknown) | R-B §7; R-D §7 | Missing = null never zero; zero only when `proven_not_dispatched`; attempt boundaries include failed/helper/retry; provider-cache and owned-reuse are separate ledgers | R-A omits cache/owned split (R-D §7 supplies) | aligned (merge needed) |
| Delegation record | R-A §3 Invocation/EvidenceItem | R-B §6 DelegationRecord fields; §5 axes | DelegationRecord (identity/authority/continuity/capability-loss/lifecycle/reconciliation) is parent; EvidenceItem is its per-attempt leaf | duplicate naming: Invocation vs DelegationRecord | needs-owner (naming/writer) |
| Route profile | `records.RouteProfile`; R-A §4 freeze/adapter split | R-B §3 nine-harness map; §4 credential ownership; version seams | RouteProfile carries pinned host/protocol/OS pins, capability assertions, losses, qualification state; R-B map populates each route | D-028 floors and R-B seams not yet in R-A profile | needs-owner (pins/ownership) |
| Disabled-path inertness | R-A §5 cold-disabled checks; InstallationRecord `state: disabled` | D-022 stop modes (R-B §5/§6) | Admission-side: disabled = no import/effect/secret access (R-A §5). Runtime-side: D-022 Aggressive/Full/Lazy + checkpoint/interrupt/drain | R-A "quiescence" vs D-022 vocabulary | aligned (complementary) |
| Effect settlement | R-A §4 effect id/idempotency; §5 dynamic disable; EvidenceItem `effect_state` | R-B §6 steps 5/7/9; §9 floors | Intent → stable effect ID → external validation → receipt; `outcome_unknown` blocks replay; cancel ≠ settlement | none | aligned |

## 3. Decision mapping

Each is **aligned, reinforced, or a named gap**.

| Decision | Mapping |
|---|---|
| D-018 native harness + wrapper | R-A §1–§2, §6; R-B §8 — aligned, reinforces no-lock-in |
| D-019 comprehensive + opt-in | R-A §3 "opt-in delivery" + InstallationRecord default disabled; R-B §6 — reinforced |
| D-021 delegation over intermediation | R-B §4, §6; R-A §4 credentials item 4 — reinforced |
| D-022 stop vocabulary | R-A §4/§5 lifecycle; R-B §5/§6 — **gap**: reports use quiescence/fence, not D-022 words (crosswalk #8) |
| D-023 Codex first | R-B §3.1, §9–10; R-A §7 profile — aligned (sequence, not qualification) |
| D-024 productive continuity | R-B §9 H1; R-D C1–C3 — reinforced; measurement unrun |
| D-026 Apache-2.0 | R-A §9; R-C §Q6–Q9 preserves — aligned; counsel gate (D-027) |
| D-028 platform floors | R-A §7 C14; R-B §10 OS isolation — **gap**: floors not pinned in any profile |
| D-029 trusted launch boundary | R-B §6 prerequisites; R-A §4 item 4 — reinforced; feasibility named-unknown |
| D-030 harness-native driving + fan-out | R-B §3–§4 — aligned; R-C route terms gate |
| D-031 no vendor-sabotage | R-D §1/§8 excludes intent; R-A abstains — aligned |
| D-033 porting hypothesis | R-A §6 savings unmeasured, ledger artifacts all `null`; §8 R7 — reinforced; R-G not in packet |

## 4. 46-question coverage ledger

Keys: **A** = answered, **P** = proposed-design, **U** = named-unknown.
Source files: R-A `raw/R-A/report.md`, R-B `raw/R-B/report.md`, R-C `raw/R-C/report.md`,
R-D `raw/R-D/report.md`.

**R-A (12)** — §10 gate | **R-B (12)** — §11 gate

| Q | A/P/U | Disposition | Q | A/P/U | Disposition |
|---|---|---|---|---|---|
| RA1 | A | ecosystem matrix §1–2, per-cell D/I/U | RB1 | A | nine-harness map §3 (some U) |
| RA2 | A | three common shapes §1 | RB2 | A | harness vs caller creds §4 |
| RA3 | P | version/epoch/deprecation §4 | RB3 | A/U | local CLI vs hosted §4, counsel gate |
| RA4 | P | minimal manifest §3 + JSON | RB4 | P | continuity axes §5–6 |
| RA5 | P | graph/attenuation §4 | RB5 | A | sourced loss points §5 |
| RA6 | P | freeze-early vs adapter-local §4 | RB6 | P | evidence classes in records §5–6 |
| RA7 | P/U | inertness design §5, evidence pending | RB7 | P | canonical kernel outside sessions §6 |
| RA8 | P/U | cost model §6, measurement unknown | RB8 | P | handoff/rehydration/pre-effect §6 |
| RA9 | P | cheapest paths table §6 | RB9 | P | HonestAccounting §7 |
| RA10 | P | economies + falsifiers §6 | RB10 | P | alternatives + falsifiers §8 |
| RA11 | P | fixture design §7, not run | RB11 | P | A→B continuity tests §9, not run |
| RA12 | P | oracles/stop/refusals §7 | RB12 | P | endpoints/floors/stops §9 |

**R-C (10)** — §Q1–Q10 | **R-D (12)** — Appendix A

| Q | A/P/U | Disposition | Q | A/P/U | Disposition |
|---|---|---|---|---|---|
| RC1 | A | per-route terms documented | RD1 | P | endpoints/units/denominators §2–3 |
| RC2 | A/U | public distinction; legal boundary unknown | RD2 | P | observable vs provider-internal §1,3 |
| RC3 | U | resale/quota/assets → counsel | RD3 | P | retain unreported, no zero §4 |
| RC4 | A | account/key/subscription identities | RD4 | P | human effort measurement §4 |
| RC5 | A | source/binary/name license matrix | RD5 | P | confounder register §5 |
| RC6 | U | Apache obligations → counsel | RD6 | P | matched direct baselines §6 |
| RC7 | P | distribution postures compared | RD7 | P | counterfactuals §7 |
| RC8 | U | contribution/CLA/trademark questions | RD8 | P | reuse vs cache separated §7 |
| RC9 | P | plugin licensing postures; D-026 fixed | RD9 | P | preregistration before runs, App A |
| RC10 | P/U | counsel checklist; **G-32 open** | RD10 | P | floors + single-failure stops §9 |
| | | | RD11 | P | synthetic inputs, immutable IDs §10 |
| | | | RD12 | P | burn/lock-in falsifiers incl. no-diff/worse §8 |

## 5. Open conflicts and unresolved semantics (Owner decision)

- **Namespace/epoch ownership** — `namespaces_are_placeholders`; R-A §9.
- **Mandatory vs optional contribution families** — R-A §3, §9.
- **Record writer boundaries** — DelegationRecord vs EvidenceItem; R-A §3 table vs R-B §6.
- **Second adapter** — R-B §11; R-D §6 roster.
- **Credential-isolation feasibility per platform** — R-B §6; D-029.
- **D-022 vocabulary mapping** onto R-A quiescence/fence.
- **RouteProfile ownership and D-028 floor pinning.**
- **Refusal/loss taxonomy merge** — R-A §7 + R-B §5.
- **Ledger naming** (provider-cache vs owned-reuse) shared with R-D §7.

## 6. Proposed next local steps (bounded — no execution)

Each deliverable has a machine-checkable gate; none authorizes running anything.

1. **Codex App Server qualification spec (D-023).** Gate: every R-B §3.1 map cell and version
   seam has a pinned commit/executable digest or an explicit named-unknown; validator prints 0
   unresolved cells.
2. **Provider-free conformance/continuity fixture.** Gate: C01–C15 (R-A §7) and B0–B3 (R-B §9)
   each enumerated with an independent oracle and fail-fast sentinels; validator confirms zero
   provider calls and no case marked PASS.
3. **Measurement preregistration (R-D Appendix A).** Gate: A1–A5 fields nonempty or justified
   N/A; validator rejects unknown-as-zero, missing Owner thresholds, and any savings claim.

## 7. Limits

Nothing was run: no plugin, harness, provider/model call, benchmark, login or counsel contact.
No adoption; no normative force. Evidence classes preserved: source-documented, locally observed
(none here), inferred design, unknown. Every `source-ledger.json` `qualified_execution_artifact`
stays `null`; document captures are not installed binaries.

---
title: R-A…R-D research synthesis (2026-10-02 return)
status: research-evidence-not-a-decision
last-updated: 2026-10-02
---

# Recursion R-A…R-D research synthesis

Research evidence only — not Owner decisions, not acceptance, not legal advice. Nothing in this
packet was executed: no plugin, harness, provider/model call, benchmark, counsel contact or
repository change. Source: the immutable intake at `../raw/` (26 manifest files, hash-verified).

## What landed

- Four reports — **R-A** plugin portability, **R-B** cross-harness delegation, **R-C** route
  licensing/counsel packet, **R-D** quota/lock-in measurement — plus a **00-assessment**.
- **46 numbered questions** (R-A 12, R-B 12, R-C 10, R-D 12).
- Machine artifacts: `proposed-contract.json`, `plugin-manifest.schema.json`,
  `example-manifest.json`, `source-ledger.json` (R-A); `sources-delivery.json` (R-B);
  `rc-public-evidence.csv`, `rc-counsel-question-checklist.csv`, `rc-source-license-manifest.json`
  (R-C). Our original prompts are preserved under `raw/input-as-received/` for provenance.
- Evidence discipline is strong: source-documented / locally observed / inferred / unknown stay
  distinct; **unknown is never zero**; every recommendation carries a competing option, a
  falsifier and what it does not prove.

## Lane findings

### R-A — plugin portability and contract
- Six records with distinct writers: `PluginManifest` (untrusted), `InstallationRecord` (trusted,
  default `disabled`), `AuthorityGrant` (kernel-only, intersection), `RouteProfile`,
  `CapabilityDescriptor`, `Invocation/EvidenceItem`, plus `HonestAccounting`.
- Capability **graph** (15 node types, 9 edge types): "no dependency/data-flow edge implies
  permission"; effective grant = intersection of constitutional ceiling, GoalSpec, parent grant,
  install/profile permission, manifest request, route enforcement, operation approval. Unknown
  required enforcement → **refuse**; `attenuation.parent_containment_required = true`.
- Disabled-path **inertness must be independently observed**, not trusted from a flag.
- Porting-cost model with denominators; **savings are unmeasured**; every
  `qualified_execution_artifact` in the source ledger is `null` (document captures, not installed
  binaries). No language/runtime/store/sandbox is selected.
- Consistent with D-019 (comprehensive + opt-in), D-021 (no credential custody), D-023
  (Codex-first), D-026 (Apache-2.0 direction).

### R-B — cross-harness delegation (without credential intermediation)
- Delegates to an **installed, harness-authenticated** tool; Recursion never invokes setup-token,
  reads/injects/copies credentials, or auto-falls back to a hosted API. The *strong* non-access
  claim requires an operator-provisioned trusted launch/auth boundary; otherwise it is explicitly
  "non-intermediation-by-policy only."
- Nine routes mapped across submit / steer-queue / interrupt / resume-fork / observe; durable
  queues, crash-safe approvals, helper accounting and effect settlement are generally **unknown**.
  Named seams: Codex rewind version split, Gemini `--acp` vs `--experimental-acp`, Hermes reconnect
  ≠ restart-safe admission, OpenCode `prompt_async` ≠ active steering.
- `DelegationRecord` (authority, continuity, capability/loss, reconciliation) and
  `HonestAccounting` (missing = `null`, never zero).
- **H1 productive-continuity experiment:** Stage P provider-free (fixtures + synthetic effect
  sink) → Stage H real binaries (Codex first + a second deliberately different adapter),
  unscheduled and unrun. Hard floors (authority, privacy, correctness, evidence, reproducibility,
  accounting honesty) precede cost/speed.

### R-C — route licensing / counsel packet (NOT legal advice)
- Nine routes; cross-cutting themes: driving an installed, end-user-authenticated CLI vs
  third-party **credential custody/intermediation**; **service access ≠ source license**; binary
  redistribution, notices and bundled assets; trademark. No lawful/unlawful findings are asserted.
- `Q01–Q12` counsel checklist; `rc-source-license-manifest.json` pins commits/licenses (evidence,
  not clearance). **G-32 remains open.**
- Needs Lucas-supplied facts for counsel: entity/jurisdiction, exact tier, distribution model,
  accepted terms/MSAs, per-route process/credential-flow, release manifest.

### R-D — quota / lock-in measurement
- Narrow testable claim (specified workload, route, account regime, continuity condition);
  **vendor-sabotage stays a hypothesis** — no resource experiment identifies intent.
- Endpoints: Q1–Q5 native allowance, U1–U12 model/tool accounting (tokens/caches/helpers/
  compaction), C1–C3 continuity, H1–H4 human effort, L1–L6 lock-in/porting. Units stay
  provider-native; no single scalar.
- **Confounder register**; two comparisons — controlled same-route (Recursion orchestrating H vs
  direct H) and practical strong baseline (informed operator's best direct workflow); Recursion
  running directly on a provider is a **separate native arm**.
- Accounting: all attempts counted, **no unknown-as-zero**, no parent/child double count, separate
  provider-cache vs owned-reuse ledgers.
- Preregistration templates A1–A5; hard floors; stop conditions; falsifiers include
  **no-difference and worse** outcomes.
- Owner inputs are run-admission blockers: meaningful-reduction threshold, equivalence bounds,
  error/multiplicity policy, sample size/repeats, authorized usage/spend/time ceiling, and the
  **value of a review minute**.

## Cross-cutting

- No conflict with D-018…D-028; the packet **reinforces** D-019, D-021, D-023, D-024, D-026.
- R-A and R-B must share one semantics for capability/grant/attenuation/evidence/refusal and
  accounting; a shared name is not enough.
- Pre-existing metadata issue: the briefs' `parent-goal` id says v2 while the target is v3 (do not
  silently change the target).

## Local handoff (from the assessment) — three phases

1. **Reconcile the evidence:** confirm all 46 questions have an answer/proposal/named unknown;
   reconcile identifiers, grants, accounting units and evidence classes across reports;
   independent review + **Owner acceptance of any candidate normative contract** (a report's own
   checklist is not acceptance).
2. **First qualification specification:** a precise Codex App Server profile per D-023; a
   provider-free conformance/continuity spec (disabled-path inertness, refusal oracles, evidence
   preservation, authority re-checks, missing-counter handling). **Separate authorization** before
   implementation/execution.
3. **Freeze measurement + counsel packets:** preregister endpoints/matching/sample/stops; tie each
   counsel question to public evidence + operating mode + expiry. **G-32 open until counsel returns.**

## Owner decision brief (reserved by the reports)

- **R-A:** accept/revise record semantics + the non-optional kernel boundary; namespace/epoch
  ownership; mandatory vs optional contribution families; authorize a test environment and
  instrument visibility; cost/quality thresholds; independent acceptance reviewer; publication
  separately authorized.
- **R-B:** credential-isolation deployment feasibility; second stress-test adapter; route/account
  entitlement; verbatim route selection.
- **R-C:** whether/when to engage counsel, and the exact deployment/distribution/entity/tier facts.
- **R-D:** reduction threshold, equivalence bounds, error policy, sample size, spend/time ceiling,
  value of a review minute.

## Limits

Nothing was run; no legal clearance; savings and continuity are unmeasured; pins are document
captures; a passing document/schema check is not acceptance. `unknown` stays `unknown`.

# Domain D — context, interaction and product-adjacent (synthesis)

## Scope and lanes

Domain D covers the Wave C lanes about how Recursion builds, keeps, addresses, displays and
accounts for durable working state, plus product-adjacent constraints:

- **DS-12 — context compaction and cache economics.** Provider prompt/KV caching, session state, deterministic compaction and Recursion-owned semantic evidence reuse.
- **DS-14 — scientific research ARM and scholarly evidence.** Federated scholarly sources, provenance, claim–source relations, rights gating and reproducible evaluation.
- **DS-15 — ARM conversations and multi-agent rooms.** Durable actors, addressing surfaces, bounded coordination leases and multi-ARM rooms.
- **DS-30 — multi-project supervision state and memory.** Durable per-project state inside the existing `state/` tree, freshness, and long-horizon memory.
- **DS-32 — human-in-the-loop approvals and consultation.** Approvals, steering, forwarding, consultation, stop controls, preserved forks and notification projections.
- **DS-33 — licensing, distribution, provenance and IP clearance.** License/provenance metadata, copyright risk and mitigation.
- **DS-34 — decision journaling and calibration.** A prospective forecast-and-review extension to the existing D-entry convention.

These are research syntheses, not decisions. Every lane is public- and synthetic-source only,
was not independently verified or rerun by Recursion, and is non-normative. The lanes share a
method: preserve evidence classes, state what each report does not prove, name competitors and
falsifiers where offered, and leave every consequential choice to the Owner. This domain
synthesis aggregates them; it decides nothing and adopts nothing.

## Lane digests

### DS-12 — context compaction and cache economics

- **Bottom line:** pursue a provider-neutral recovery core, with provider cache/session capabilities as opportunistic accelerators only. The non-droppable Execution Context Capsule and exactly one deterministic context governor per route epoch are retained as fixed invariants; native/provider compactors may propose candidates only.
- **Confidence / evidence class:** *source-documented* provider pricing, billing and compaction behavior, *inference* for the governor/CAS architecture, and *unverified/unknown* for Recursion's own route inventory and economics.
- **Does not prove:** no Recursion cache economics were measured, and no repeated-compaction loss or cross-route recovery-quality data exist.

### DS-14 — scientific research ARM and scholarly evidence

- **Bottom line:** the strongest candidate is **Option A, authority-first federation with aggregator-assisted discovery** (registration/domain authorities anchored; aggregators as discovery/reconciliation plugins; full text behind a separate rights gate). Explicitly a candidate, not an adoption decision.
- **Confidence / evidence class:** *source-documented* for the reviewed registration, aggregation, full-text and standards surfaces; *inferred* for the lean kernel schemas and lifecycle state machine; *unverified* where documentation was insufficient.
- **Does not prove:** official documentation does not prove coverage, uptime, latency or local fit; no live provider trial, implementation experiment or hard-floor corpus run was performed.

### DS-15 — ARM conversations and multi-agent rooms

- **Bottom line:** **R1** — evaluate one transport-independent actor-and-authority contract
  (attributable direct commands, explicit GoalSpec revisions, bounded step leases enforced at
  protected boundaries, canonical Head awareness, independent acceptance), with **R0**
  (Head-mediated approval of each protected commitment) as competitor. Both retain direct
  Owner-to-ARM conversation and the fixed CLI/optional-Telegram boundary.
- **Confidence / evidence class:** supplied-brief constraints (B0), *source-documented* facts for the reviewed bot and transport documentation, *inference* for the lease/fencing analysis, and *unverified* for human coordination benefit; synthetic fixtures were not run.
- **Does not prove:** no working Recursion system was observed, no topology is shown more usable or better isolated, and universal fencing or immediate revocation is not proved.

### DS-30 — multi-project supervision state and memory

- **Bottom line:** an additive convention under the already-authoritative `state/` tree using four
  roles — `current.<structured>` (canonical semantic snapshot), `observed.<generated>` (disposable
  machine observation), `questions/<id>` (durable Owner-question correlation) and `evidence/<id>`
  (verification receipt). Competitor: a freeform per-project prose status document.
- **Confidence / evidence class:** *source-documented* for the cited Git interfaces and provider memory-file behavior; *inferred/proposal* for the state contract; *unknown* for the structured-versus-prose comparison and scheduler crash semantics.
- **Does not prove:** it does not show that schema-checked state reduces resume errors or that structured files beat prose, and it selects no serialization, scheduler, database or index.

### DS-32 — human-in-the-loop approvals and consultation

- **Bottom line:** adopt a **resource-enforced, exact-action pre-effect mediation contract** as the
  canonical authorization boundary; upstream prompts, callbacks, hooks, automatic reviewers and
  transport confirmations may supply evidence or early denial but must not independently create a
  Recursion authorization receipt. Competitor: a harness-centric design treating the framework
  hook or callback as the definitive gate.
- **Confidence / evidence class:** *source-documented* for the reviewed SDK/hook/admission and transport patterns; *proposal/inference* for the mediation contract; several *unverified* cells.
- **Does not prove:** it does not prove exactly-once behavior for external services, does not supply the ten omitted terminal-control definitions, and reports no live trial — the synthetic fixtures are acceptance targets, not completed tests.

### DS-33 — licensing, distribution, provenance and IP clearance

- **Bottom line:** a governance combination — enforce precise license and provenance metadata at
  ingestion, adopt provenance tracking, and treat content as protected unless explicitly cleared —
  supported by license-reasoning tools and explicit identifiers. The report states no competing
  option and no single decisive falsifier.
- **Confidence / evidence class:** *source-documented* study results and secondary legal commentary, plus the report's own synthesis and general legal background; not primary case filings or full statutes.
- **Does not prove:** it does not analyze Recursion's actual data, code, model or distribution targets, and it establishes no particular license as safe for a given use.

> **Status callout.** DS-33 is **legal-risk research, not legal advice.** It summarizes third-party findings and general copyright/licensing concepts; no counsel reviewed it, no jurisdiction-specific rights analysis was performed, and it is not a clearance opinion. **Counsel is required before any distribution, publication, training or other release decision.**

### DS-34 — decision journaling and calibration

- **Bottom line:** **R1** — a prospective forecast-and-review extension to the existing D-entry convention (keeping the monthly first-of-month review, adding explicit outcome dates, event triggers, a small set of resolution fields and append-only review/amendment records). It does not create a second decision log. Competitor **R0** is the present narrative convention.
- **Confidence / evidence class:** *source-documented* tournament and feedback studies, *inference* for transfer conditions, a stated *hypothesis*, an *unverified-gap* entry, and a *proposal*; the report's confidence describes research support, not probability.
- **Does not prove:** it establishes no optimal cadence, no universal case count for calibration, no measured base rate, and no demonstrated improvement in local forecast quality; the worked examples are synthetic arithmetic.

## Cross-lane consistency and contradictions

**Shared authority/attribution thread.** Across all seven lanes, authority and attribution are held
distinct from the surfaces and artifacts that merely represent them:

- DS-12 keeps the non-droppable capsule (actor/lineage, GoalSpec, task+gate, authority/privacy bounds, IDs, directives, blockers, evidence references) outside any provider summary and gives exactly one governor authority to advance the epoch; native compactors are candidate-only.
- DS-30 orders retrieval as *namespace before similarity; current authority before history*, treats summaries/indexes as candidate locators only, and requires machine facts (branch, HEAD, dirty status, fetched refs) to be observed mechanically, not hand-copied.
- DS-15 separates durable actor, addressing surface and current authority; a topic, mention, reply or human-readable role label is routing evidence only, not an authenticated principal.
- DS-32 separates canonical receipt, presentation receipt and semantic acknowledgment, and requires that no authoritative effect is settled merely because approval exists; a non-human reviewer must never be recorded as human.
- DS-14 treats provider provenance as evidence metadata, not scientific support, and keeps typed claim–source edges rather than a model-generated truth score.
- DS-34 keeps forecast outcome separate from decision falsifier, assessment separate from execution command, and process separate from outcome; reviews are append-only.
- DS-33 frames provenance as documented chain of custody and attribution, with clearance and proof-of-rights as governance rather than a technical patch.

Common conclusion: **good summaries, transcripts, receipts, room consensus and model confidence
never become authority**; authority stays with current, attributable, revalidated canonical state.

**Recurring "public/synthetic only" boundary.** Every lane performed no provider/model call, paid
experiment, repository inspection, configuration change, credential use, hosting action or
implementation action, and preserved evidence classes rather than collapsing them. DS-12's route
matrix is a dated capability snapshot of plausible public routes, **not** Recursion's route
inventory. DS-14's schemas are proposals falsifiable only by preregistered local tests. DS-15's
F01–F24 fixtures were not executed. DS-34 was extracted from a document via an alternative route.
This is the single most consistent cross-lane property.

**Tensions to preserve, not smooth over:**

- DS-30 proposes **no second append-only status log**, relying on Git history for transitions, while DS-15 and DS-32 require canonical append-only event/command records with their own ordering; where canonical event history lives relative to Git is not reconciled.
- Within DS-15, current feature documentation permits bot-to-bot communication under stated conditions while an older blanket restriction conflicts; the report records the conflict rather than resolving it.
- DS-14 records that an aggregator's access model is changing with active deprecations, and that one biomedical rate ceiling remains explicitly `unknown` rather than unlimited.
- DS-33 states **no competing option and no decisive falsifier**, unlike the other six lanes, so its evidence is asymmetric with its siblings and cannot be compared on the same basis.
- DS-34 preserves an unresolved dispute between a reanalysis of tournament-training effects and an adversarial-collaboration proposal; neither is settled.
- DS-30 and DS-34 both decline to convert calendar time into cases or invent thresholds; other lanes similarly leave numeric thresholds to Owner policy.

## Cross-lane dependencies

- **DS-12 is a blocking prerequisite.** Its capsule/context-compiler, compaction governor, route-descriptor and cost/usage ledger are the substrate the interaction lanes build on; DS-15, DS-30 and DS-32 all assume canonical state and authority held outside provider summaries.
- **DS-30 supplies state-contract primitives** (`current` versus `observed`, evidence receipts, durable question correlation) that DS-32's question/waiter machine and DS-15's canonical awareness/digests reuse.
- **DS-15 and DS-32 share the effect-settlement vocabulary** — proposal → valid decision → effect attempt → receipt, with an explicit `unknown` settlement and the rule that dispatched-but-unknown must not be reported as success; DS-32 extends DS-15's fencing reasoning.
- **DS-14 depends on a rights/privacy gate** consistent with DS-12's privacy classes and route constraints; DS-33's metadata and proof-of-rights concepts are inputs a later evidence-receipt contract may need.
- **DS-34 feeds the acceptance-gate and independent-verification discipline** shared by DS-15 and DS-32; its separations are candidate review invariants, and its preservation rules align with DS-30's append-only record discipline.
- **All lanes depend on Owner decisions** none are authorized to make; the list below is their union.

## Consolidated open Owner decisions

Aggregated unresolved choices, reproduced as questions. None is decided here.

- **Routes, context and caching (DS-12).** The authoritative route/endpoint/model-class list; the task-quality noninferiority margin for cold reconstruction; whether semantic artifacts may deduplicate across private goals/projects; which context tiers may go to public routes; whether paid explicit caches are ever permissible; the maximum stale-evidence window; which compaction policies each edition/route may use; descriptor expiry age.
- **Scholarly evidence and rights (DS-14).** Maximum false-negative rate after the zero-tolerance false-acceptance floor; admissibility of membership-only metadata versus anonymous reproducibility; whether a verifier may rely on retained restricted artifacts; exact rights operations needed; sufficiency of metadata-only standards support; domain-neutral versus biomedical-first; revalidation SLO; mandatory specialist-review classes; normal research budget; whether every packet needs full offline replay.
- **Conversations, rooms and leases (DS-15).** Transport-compromise containment and which domains merit separate transport identities; which protected-effect classes a bounded lease may coordinate and the requested-to-effective revocation delay; Telegram sender-to-Owner binding and message classes; semantic-edit, cancellation, retention and redaction rules; multi-goal budget attribution and no-progress escalation; consequence windows and digest cadence; the minimum worthwhile coordination saving.
- **Supervision state and memory (DS-30).** Concrete serialization; mandatory versus optional staleness signals; stale policy windows; whether `observed` files are committed or regenerated; project-identity and archival lifecycle; which questions need Owner authority; morning-brief reconstruction; receipt retention/compaction; unattended execution architecture; the definition of a sufficient "verified progress" receipt.
- **Approvals, steering and terminals (DS-32).** Authoritative names and semantics of the ten terminal controls; the Lazy-Stop boundary per operation class and whether Lazy may escalate; which grants a lease holder may adopt routinely versus needing Owner action; "parent allowance" categories and conservation for preserved forks; non-coalescible event classes; uncertainty states needing immediate notice; the minimum accessibility matrix.
- **Licensing and IP (DS-33).** License and provenance obligations for Recursion's own distribution, documentation, examples and any model/dataset; whether and when to engage counsel and for which artifacts/jurisdictions; mandatory ingestion metadata and default scans; provenance standard and whether records are published; the "assume protected unless cleared" default and clearance evidence; isolation of uncertain-data models or datasets.
- **Decision journaling (DS-34).** The exact D-entry template and where append-only metadata may attach; timezone/due-time and holiday handling; which decisions require a probability forecast; accountable reviewer and independent acceptance authority per class; the review-service target after a falsifier fires and disposition authority; comparable classes and eligible-case inventory source; entry/review burden and adoption criteria; original-versus-verified-correction scoring and cancellation/intervention policy.

All are policy, not findings; several depend on counsel review (DS-33), route evidence (DS-12), or
independent review designs (DS-15, DS-32, DS-34).

## Domain gaps and open unknowns

**Unrun experiments.**

- DS-12's synthetic route-by-route suite: same-route prefix versus cold baseline, repeated compaction, cold disaster recovery, cross-route rebuild, privacy isolation and the keepalive counterfactual — proposed, none run; no structural 100%-recall targets measured.
- DS-14's hard-floor corpus, the Option A/B/C comparison on coverage/update latency/verifier reproduction/bounded cost, and the disabled-path acceptance test — specified, not executed.
- DS-15's F01–F24 fixtures and the matched direct-addressing evaluation (with the Owner-declared minimum worthwhile saving) — designed, not run.
- DS-30's structured-versus-prose resume-error comparison and scheduler/daemon crash-recovery semantics — not run; no Recursion benchmark exists.
- DS-32's synthetic fixtures are acceptance targets, not tests; per-adapter Aggressive-Stop boundaries and the Lazy-Stop observable boundary remain unmeasured.
- DS-33's implicit tests (whether metadata enforcement reduces missing/mislabeled records; whether cleared provenance reduces exposure) are presented as not run.
- DS-34's prospective R1-versus-R0 window on reconstructability, timely review and burden — not run.

**`unknown` cells.** Provider memory field survival through compaction; the Europe PMC rate ceiling;
DataCite hidden record states; explicit-cache control for one interaction surface; subscription
debit accounting; whether structured state reduces resume errors; scheduler cost and event/daemon
recovery; which resources return durable idempotency receipts; external-service post-cancel
behavior; remote transport ordering/retry; screen-reader and rendering budgets; the ten
terminal-control definitions; and the requested-to-effective revocation delay per effect class.
`unknown` is deliberate and is not zero.

**Benefits that remain hypotheses.** No source establishes that direct Owner-to-ARM conversation
reduces Owner coordination effort; no topology is shown more usable or better isolated; a stable
prefix's total-workflow savings are unmeasured in Recursion; structured supervision state's
accuracy advantage is unproven; the semantic evidence cache's portability economics are
unquantified; the decision journal's calibration benefit is a testable downstream hypothesis, not
a promised gain; and the interaction/workload benefits of these designs are hypotheses to be
measured under identical authority rules, not results.

## Evidence-quality notes

- **Not verified, not rerun.** Every lane states its output is research evidence, not a decision, and was not independently verified by Recursion; a report's own PASS is not acceptance. No accepted decisions are claimed anywhere in this domain.
- **Public/synthetic only.** All lanes performed no repository inspection beyond the supplied brief, no provider/model call, no paid experiment, no credential/config/auth change, no hosting or publication action, and no implementation. DS-12's route matrix is a plausible-route capability snapshot, not Recursion's actual inventory.
- **Evidence classes preserved.** Source-documented, locally observed, inferred, proposal, hypothesis, and unverified/unknown are kept distinct; `unknown` is never collapsed to zero or a default. Label styles differ by lane but the distinctions are consistent.
- **Route and extraction provenance.** DS-15 and DS-34 came from an alternative route after a primary route was rate-limited or returned only a scoping plan; DS-34 was extracted from a document and may have wording drift. These are documented limitations, not reasons to trust the content more.
- **Conflicting evidence retained.** The Telegram documentation conflict, the changing aggregator access model, the tournament-training dispute, and DS-33's absence of a competitor/falsifier are recorded rather than resolved; this synthesis preserves the asymmetry.
- **Attribution and dates.** Claims are attributed only to "the report's sources"; this synthesis adds no URLs and no new facts. Capability observations are dated snapshots, not guarantees.
- **No product or policy adoption.** Nothing here selects a provider, route, cache policy, TTL, serialization, scheduler, store, topology, transport, sandbox, terminal definition, provenance technology or cadence. All remain Owner decisions, and DS-33 additionally requires counsel review before any release decision.

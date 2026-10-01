# DS-26 — Telemetry, accounting and honest status (synthesis)

## Provenance

- Raw report: `raw/ds-DS-26-telemetry-accounting.md`.
- Labelled a self-contained handoff for Wave B Deep Research, run 2; retrieved 2026-09-30; the report states its own snapshot as 2026-10-01.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun performed.
- A **public, documentation-only** session: no provider account, credential, billing endpoint, repository or configuration was touched.
- The DS-26 brief (Owner decisions, privacy boundary, provider-neutral architecture, correlation identifiers, cost-class separation and the ban on fabricated percent-complete) is treated as controlling requirements.
- Evidence classes mirror the report: **source-documented**, **upstream-observed** (issue reports, not a stable API contract), **inferred**, and **Owner/brief-mandated**.

## The question

What evidence-and-accounting contract does Recursion v3 need before telemetry may drive dashboards,
budget reservations, route learning or optimization claims? The report's principal concern is not a
lack of counters but **false equivalence between counters that have different provenance and
semantics**.

## Key findings

- **Two ledgers, not one usage table.** The report recommends a provenance-qualified architecture
  with an attribution/quantity ledger and a financial/capacity ledger; reconciliation may connect
  them but must never silently convert one into the other (inferred, from source-documented rules).
- **Provider endpoints differ and must not be collapsed.** OpenAI and Anthropic expose organization-scoped read-only usage/cost endpoints, and Cursor exposes team usage events plus an Enterprise organization API (source-documented). The reviewed material does **not** establish a single Gemini Developer API equivalent — only per-response `UsageMetadata`, project-scoped Vertex AI metrics and Cloud Billing exports (source-documented).
- **Cache semantics are not directly summable.** OpenAI aggregate `input_tokens` includes cached input; Anthropic separates ordinary input, cache creation and cache reads; Gemini `promptTokenCount` includes the cached subset; Cursor exposes separate read/write fields (source-documented). The report supplies per-source normalization and forbids adding cached to uncached.
- **Rate-limit semantics are not billing semantics.** Cached tokens still count toward OpenAI TPM
  under current docs, while Anthropic generally excludes cache reads from ITPM with a documented
  Haiku 3.5 exception (source-documented). `rate_limit_charge` stays separate from monetary cost.
- **Retention is unknown.** Query horizons and bucket limits do not establish guaranteed total
  retention; those cells stay `unknown`. Vertex AI's six-week token-metric retention is **inferred**,
  not guaranteed.
- **CLI evidence needs version-pinned conformance.** Gemini CLI documents an OpenTelemetry per-response event with token classes and duration (source-documented). Codex and Claude Code local streams show missing/replayed/duplicate or incomplete token events in upstream issue history (**upstream-observed**), so they are not admitted without a version fixture.
- **`ccusage` is an optional adapter, not authority.** The report pins current canonical project
  `ccusage/ccusage`, v20.0.26, commit `d982108`, MIT (source-documented). The license permits
  bundling/modification with notice, but derived pricing and inherited CLI-log defects mean its data
  does not inherit provider authority.
- **Epistemic state travels with every value.** `observed`, `modeled`, `inferred` and `unavailable`
  are first-class; a missing counter is `value = null` plus an availability reason, never `0`. An
  explicit provider zero stays zero.
- **Exactly-once reconciliation.** Prefer a finalized request delta with stable request/event ID; difference validated cumulative totals within a proven epoch; treat unexplained decreases, missing boundaries and ambiguous resets as `unknown`. Replay-prone "last" fields must not be naively summed (Codex). Helpers, classifiers, compactors and retries are real billable calls counted once under `call_role`, not excluded as internal.
- **Authority is dimension-specific.** Provider invoice/cost sources settle money; provider-native
  usage sources give quantities; version-qualified harness events give task attribution; local OS
  monitors give host resources; deterministic estimators stay modeled. Subscription capacity remains
  in its native unit, not converted into dollars or tokens.
- **Correlation is Recursion-owned.** A fixed envelope spans project, goal, goal_spec_version,
  arm_run, task, segment, route, provider request, source receipts, checkpoint, candidate, evidence
  and verifier. Provider session IDs are disposable continuity aids, never authoritative lineage.
- **Latency and resources are decomposed.** Queue/wait, bridge/control preflight, provider round-trip, provider server/inference, post-response/control and end-to-end segment time stay distinct; pure inference latency is unavailable when only client RTT exists. Inference, subscription capacity, host resources and human review remain separate, with no default scalar "total cost"; host money is unavailable until an Owner rate card exists, and portable wakeup count is not established.
- **Honest status is an evidence viewer, not a progress storyteller.** Dashboards may report observations, explicit waits, native quota headroom, verifier outcomes and freshness; they must not infer goal percent-complete from activity, turn missing counters into zero, call stale silence healthy, or convert a forecast into actual consumption.
  State vocabulary includes observed-running, explicitly-waiting, blocked, terminal-verified, terminal-unverified, failed, no-recent-evidence, unknown.
- **Route learning is subordinate.** Adaptive reordering sits after hard authority/privacy/
  verification filtering; only runtime-qualified measurements may update production learning state;
  `unavailable` is a feature, not zero; promotion requires a predeclared workload, static baseline,
  uncertainty method, acceptance margin and falsifier.
- **Privacy is allowlist-based, metadata-minimal, local-first.** Prompts, raw output, source snippets, private artifacts, paths and credentials stay out of telemetry; aggregation must address membership leakage (cohort suppression, keyed fingerprints, pseudonymized dimensions). OTel's GenAI conventions themselves warn that message attributes can contain sensitive data.

## Recommendation and falsifier

Adopt qualified evidence adapters feeding **separate attribution and settlement ledgers**, with an
honest-status projection on top and reconciliation placed **after** normalization. The principal
competing approach — a single normalized usage/cost table with one blended score — is rejected
because valid native counters cannot always share one semantics (e.g. OpenAI cached tokens counting
toward TPM while Anthropic cache reads usually do not).

Falsifiers for the recommendation include: replaying identical raw evidence changes the normalized
ledger; a missing native counter becomes numeric zero; a request can be charged twice after
crash/reset/fork/replay; aggregate cache normalization fails to reconstruct the provider's
documented total-input identity; metered totals cannot reconcile to the provider financial
authority; a helper/retry disappears for lacking a headline UI event; human/host/subscription
resources are silently converted to inference dollars; dashboard silence renders as healthy or
complete; the route learner selects an unapproved route or relaxes verification; or default export
can reveal prompt/output/private artifact content. No reconciliation tolerance or confidence
threshold is invented; both must be declared before the relevant test.

## What this does not prove

- No provider account, credential, billing endpoint or live adapter was exercised; findings are
  **documentation-qualified**, not runtime-qualified.
- Documented query horizons are not proven retention; several retention cells remain `unknown`.
- Codex and Claude Code local-stream defects are version-specific issue reports, not stable
  contracts, and may be fixed in later versions.
- The two-ledger design, exactly-once algorithm and route-learning contract are proposals; no
  conformance test or shadow evaluation was run.
- A never-run secret scan is reported as unavailable, not "clean"; nothing about repository state is
  verified.
- Some counters (portable wakeup count, host monetary cost, subscription-to-dollar conversion) are
  declared unavailable rather than estimated.

## Open Owner decisions

The report leaves to the Owner: the exact v3 harness admission list and supported versions; whether
organization-admin credentials are acceptable for read-only collectors; local telemetry retention;
external-export cohort suppression/differencing policy; whether provider session IDs may be stored
raw locally; host-resource and human-review monetary valuation; the promotion metric, acceptance
margin and uncertainty method for route learning; precedence for late provider billing corrections;
and whether document-qualified adapters may feed operator views before runtime qualification.

## Relevance to later waves

- Supplies the accounting and honest-status contract any later telemetry, budget, dashboard or
  route-learning work must satisfy or explicitly amend.
- Establishes dimension-specific authority and two-ledger separation as reusable invariants that
  prevent provider meters from rewriting internal authority or budgets.
- Gives later waves a concrete falsifier set for exactly-once reconciliation, cache normalization,
  cost separation, privacy and adaptive-routing promotion.
- Leaves provider selection, retention policy and valuation as open Owner inputs rather than
  silently resolving them here.

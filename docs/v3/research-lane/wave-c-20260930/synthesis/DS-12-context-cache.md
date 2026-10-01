# DS-12 — context compaction and cache economics (synthesis)

## Provenance

- Raw: `raw/ds-DS-12-context-cache.md`.
- Source-prompt: DS-12 — context compaction and cache economics.
- Session: Wave C Deep Research (self-contained handoff); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Public-source analysis only: no provider calls, paid experiments, repository access, configuration changes, or implementation actions were performed.
- Evidence classes preserved: **source-documented**, **inferred**, **unverified/unknown**, plus a small **locally observed** set covering only the report's own session procedure (no write action, no protected path edited).
- The report is route-first; its route matrix is a dated capability snapshot of plausible public routes, **not** Recursion's actual route inventory (repository inspection was prohibited). Claims are attributed to "the report's sources"; no URLs are added.

## The question

How should Recursion combine provider-side prompt/KV caching, provider session state, deterministic compaction, and Recursion-owned semantic evidence reuse without conflating their economics, authority, privacy, or fidelity? The brief fixes two invariants rather than reopening them: the **Execution Context Capsule is non-droppable**, and **exactly one deterministic context governor owns the authoritative compaction transition per route epoch**; native/provider compactors may only propose candidates.

## Key findings

- **Four accounting domains.** Provider prompt cache, provider session state, Recursion semantic reuse, and subscription/product debit are separate. `previous_response_id` avoids resending bytes yet prior chained input remains billable input; cache discounts are a separate mechanism. No source supports converting an API cache hit into a subscription-credit assumption (source-documented / unknown).
- **Session state is not cache state.** *Bytes not resent ≠ tokens not billed ≠ provider cache hit.* Session affinity, semantic reuse, cached-read tokens, and avoided debit must never increment one metric.
- **Route identity matters at least as much as model identity.** The same model class behaves differently direct vs. on a cloud broker (counters, quota, TTL, feature availability). Capability must be a versioned, evidence-pinned `RouteCapabilityDescriptor` keyed by substrate, endpoint/API family, model class/version, region, account/project boundary, caching mode, and retrieval date (source-documented).
- **Stable prefix is an optimization, not authority.** Providers recommend common-prefix-first ordering; a 2026 multi-provider preprint reported 45–80% API-cost reductions and 13–31% TTFT improvements but found cache layout mattered and naïve full-context caching could worsen latency (benchmark evidence, informative rather than proof for Recursion).
- **Provider-native compaction cannot be the sole control record.** OpenAI emits an opaque artifact; Anthropic replaces older turns with a model-generated summary and consumes an extra sampling iteration; neither guarantees Recursion Owner directives, gates, blockers, evidence references, authority fences, or artifact IDs survive (source-documented). Candidate → deterministic validator → authoritative governor is the correct boundary.
- **No cross-route cache portability evidence.** The defensible assumption is "provider KV reuse is unknown unless the exact route documents it; do not count it." Portability comes from Recursion semantic artifacts and capsule reconstruction; Gemini/Vertex caches are project-scoped (source-documented).
- **Keepalive fails closed.** Any refresh/prewarm with positive cost and no subsequent useful work has negative net benefit (inference from documented charging and TTL); event-driven continuation remains the sound baseline.
- **Separate ledgers.** Workflow cost splits uncached input, cache-write, cache-read, storage, output, compaction, prewarm, refresh, retry, and tools; unavailable terms stay `unknown`, never `0`. Semantic reuse (artifact hits, bytes rehydrated, tokens avoided, validation outcomes) and subscription debit are separate again; a generic `input_tokens` is not portable accounting (source-documented for Anthropic/Bedrock usage-iteration and summed-input behavior).
- **Break-even arithmetic.** Normalizing a reusable prefix to 1: GPT-5.6+ write ≈1.25 and most reads ≈0.1, so ten uses ≈2.15 vs. 10 cold; Anthropic's 1-hour write ≈2× can never beat two cold uses after one reuse; Gemini explicit caching adds time-based storage, so an idle cache can be net-negative despite cheap reads (source-documented pricing).
- **Ordering rule.** Stable policy/control material, stable tool definitions, stable evidence manifests, append-only prior state, then volatile results/timestamps/current input — subordinate to semantic correctness and privacy.
- **Structural fidelity validation.** Before an epoch advances, check exact preservation or authenticated rehydration of actor/lineage, GoalSpec, task+gate, authority/privacy/resource bounds, source/candidate IDs, Owner directives, blockers, evidence references, checkpoint parentage, output contract, and artifact reachability; semantic similarity is insufficient.
- **One authoritative governor.** Only the governor mutates the epoch pointer; provider/session/SDK compactors are candidate-only. A compare-and-swap over `(goal, route_epoch, compaction_sequence, parent_digest)` is the report's architectural inference, not an observation of current code.
- **Invalidation.** Bind artifact type, canonical content, tree/commit, config digest, policy version, tool/resource version, descriptor version, authority fence, and schema version under a project/goal-scoped keyed construction. Invalidation is asymmetric: false-negatives can reuse revoked/stale authority, so source, config, tool, identity, revocation, and authority changes conservatively force revalidation.
- **Privacy.** Cache metadata has contractual weight (Vertex-hosted Claude cache fingerprints are classified by Google as User Metadata/Service Data; Gemini implicit cache is RAM-only and project-isolated). Emerging systems-security work reports timing side channels from shared KV caches; treat it as a threat-model input, not proof any named commercial route is vulnerable. Posture: no global cross-private-project deduplication by raw content digest; use scoped, keyed identifiers.

## Recommendation and falsifier

A provider-neutral recovery core with provider capabilities as opportunistic accelerators; none is promoted to a decision:

1. **Stable prefix** (vs. implicit-only caching) — falsified if, after writes/prewarm/misses, it does not cut total successful-workflow cost or latency, or causes unacceptable write churn.
2. **Session affinity as a hint** (vs. sticky provider-session authority) — falsified if fresh reconstruction is persistently and materially worse and enrichment cannot fix it; that would challenge capsule sufficiency, not authorize session-as-truth.
3. **Small exact capsule kernel + rehydrated artifact tiers** (vs. deriving control state from a transcript/summary) — falsified if deterministic tests show the kernel lacks information to reconstruct a valid continuation even with all artifacts present.
4. **Recursion semantic cache as the portable layer** (vs. global raw-hash dedup) — falsified only by a formal privacy review plus adversarial measurement showing isolated storage becomes prohibitively costly with no unacceptable leakage.
5. **One governor** (vs. provider compactor advancing state) — the report states there is **no in-lane falsifier**: it is an accepted Owner constraint, changeable only by explicit Owner amendment.
6. **Event-driven continuation** (vs. periodic keepalive) — a narrow refresh policy needs telemetry proving complete refresh cost beats the expected avoided miss/latency; it still cannot make the no-future-work case profitable.
7. **Versioned descriptor** (vs. inferring controls from model name) — fails closed: an absent field is `unknown`, not "provider default."

The empirical program is a synthetic, route-by-route validation suite with 100%-recall targets for structural control invariants (not model task quality).

## What this does not prove

- Recursion's actual route inventory is unknown (repository inspection was prohibited).
- No Recursion cache economics were measured: no hit rate, prefix size, write churn, or session-loss frequency.
- No repeated-compaction loss experiment and no cross-route recovery-quality data exist; cold-reconstruction noninferiority is unmeasured.
- Subscription debit is mostly unknown; API token billing and product/subscription usage are not interchangeable accounting systems.
- Gemini Interactions explicit-cache control remains `unknown` pending exact-route confirmation.
- Private-cache timing leakage is not fully characterized; isolation and keyed identifiers reduce but do not alone eliminate side channels.
- No cache hit, saving, or experiment is asserted; no protected path or provider state was edited; no paid treatment or universal default was adopted.

## Open Owner decisions

- The authoritative list of Recursion v3 routes/endpoints/model classes.
- The acceptable task-quality noninferiority margin for cold reconstruction.
- Whether any semantic artifact may deduplicate across separate private goals/projects.
- Which context tiers may be sent to public routes, by edition/privacy class.
- Whether paid explicit caches are ever permissible route-by-route, or implicit only.
- The maximum stale-evidence window, if any, for non-authority information.
- Which named compaction policies each edition/route may use.
- What evidence age should auto-expire a `RouteCapabilityDescriptor`.

## Relevance to later waves

This lane is a blocking prerequisite for route adapters, the capsule/context compiler, the compaction governor, and the cost/usage ledger. Later waves should serialize the report's claims into machine-readable conformance experiments — same-route prefix vs. cold baseline, repeated compaction, cold disaster recovery, cross-route rebuild, privacy isolation, and keepalive counterfactual — and consume them as constraints and fixtures, **not** as a selected cache policy, TTL default, or provider route. The non-droppable capsule and one-governor-per-route-epoch rules carry forward unchanged.

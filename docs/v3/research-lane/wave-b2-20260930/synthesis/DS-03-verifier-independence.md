# DS-03 — Risk-scaled verifier independence (synthesis)

## Provenance

- Raw report: `raw/ds-DS-03-verifier-independence.md`.
- Source prompt: DS-03 — risk-scaled verifier independence.
- Session: Wave B Deep Research (self-contained handoff, run 2); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved: source-documented, locally observed, inferred, and unverified. The report's "expiry" values are evidence review-by dates, not claims that older evidence is false.
- The report states it did not reopen the accepted risk-tier direction, redefine the canonical independence vector, select a verifier/provider/model, issue or simulate an exception, or change runtime/repository state.

## The question

Given a fixed canonical independence vector — actor; workspace/state; evidence acquisition; implementation authorship; model family; provider; account/capacity pool; host/failure domain; evaluator/oracle — and fixed risk classes `V0`–`V3`, which dimensions actually reduce false-green gates once the others are held fixed, and what minimum assurance/downgrade/blocking contract should govern each class?

- Weaker verification may never silently become full verification.
- The report does not redefine the vector or the risk classes it was given.

## Key findings

**(a) Independence is a set of separable failure-domain properties, not "use another model."**

- The report's sources support technical separation from the developer, separate organizational authority, independent evidence gathering, two-person review, isolated/reproducible execution, and verification bound to an exact revision.
- NASA IV&V distinguishes technical, managerial, and financial independence; SLSA requires distinct trusted persons for its two-party-review property and separately recognizes reproduction by independently operated build platforms.

**(b) Nominal independence is not enough.**

- Knight and Leveson's classic experiment used 27 independently developed versions and a million tests, yet simultaneous failures occurred substantially more often than statistical independence predicted.
- A 2026 exploratory IEEE study of LLM-generated variants reports the same qualitative concern.
- A second reviewer, second account, or second model label is not proof of independent failure behavior; "different is not the same as independent."

**(c) Model-based evaluation has documented systematic bias.**

- ACL 2024 found self-bias across six examined LLMs, with self-refinement able to amplify it; a TACL survey found reliable external feedback to be a key condition for self-correction.
- ACL 2025 showed 11 LLM judges were vulnerable to superficial artifacts — one artifact skewing preferences by as much as 98 percent — with multi-model juries improving robustness but not eliminating the problem; Findings ACL 2026 found gains from multi-model, multi-criterion panels.
- "Stronger model" is not an evidence class and must not substitute for exact deterministic evidence.

**(d) Provider, account/capacity pool, and host have weaker semantic evidence than the other dimensions.**

- The report finds no clean controlled result establishing that changing provider, account/pool, or host by itself improves semantic defect detection after model family, actor, evidence, and task differences are controlled.
- These dimensions still matter as threat-model and availability separations, but their semantic-verification value is marked inferred or unverified.

**(e) The recommended tier contract keeps deterministic gates non-substitutable.**

- `V0-mechanical`: exact deterministic gate re-execution; a model has no authority to turn a gate failure into success.
- `V1-routine-reversible`: adds a clean separate verifier actor/state with independent evidence acquisition; same-family review is accepted only as actor/context separation.
- `V2-sensitive`: adds an independent failure domain and an adversarial fault gate.
- `V3-constitutional-release`: adds authenticated Owner approval.
- Missing required evidence blocks or yields only an explicitly authorized, candidate-bound downgraded state; there is no edge from missing evidence to ordinary pass.

**(f) The claim matrix records classification per dimension.**

- Source-documented high confidence: actor, evidence acquisition, implementation authorship.
- Medium-high for environmental faults but low for semantic accuracy: workspace/state and host/failure domain.
- Source-documented for diversity effects but medium/inferred for the tier rule: model family.
- Unverified/inferred with low confidence for semantic detection: provider and account/capacity pool.

**(g) The decisive open question is empirical, and the report proposes a measurement design.**

- A preregistered, blinded, sequestered matrix over 480 public/synthetic candidates: 120 per risk class, with 90 one-defect and 30 clean controls per tier.
- Six defect families: logic/specification mismatch; shared/stale-state contamination; misleading or insufficient deterministic gate; evidence/provenance mismatch; adversarial/security-boundary fault; authorization/release-policy fault.
- Treatments T0–T7 isolate self-check, clean same-family, family diversity, provider/pool contrast, host contrast, full diverse path, deterministic specialist, and independent human review.
- Metrics (no composite): false-green rate, defect recall, false-block rate, pairwise disagreement, common-mode miss rate, gate/verifier discordance, escaped-defect rate, review effort, unavailable-cell rate. NIST's blind sequestered evaluation is cited as precedent.

**(h) The main competing option is one universal strong verifier, with explicit win conditions.**

- It should win if, on the preregistered `V2`/`V3` sample, it is statistically non-inferior within a predeclared five-percentage-point false-green margin.
- It must also have no materially higher common-mode miss rate, no defect stratum where independent-domain verification improves recall by more than five points, and measured review effort reduced by at least 30 percent.
- Until such a result exists, the report says the current evidence favors risk-scaled independence.

**(i) The downgrade receipt is not redefined, only checked.**

- Proposed validation properties against the canonical `VerifierDowngradeReceipt`: exact-candidate binding, named-deficit binding, acceptance-context binding, unique identity, explicit validity interval, atomic consume semantics, and an immutable downgraded terminal label that cannot later render as ordinary pass.
- A broad reusable waiver is rejected, citing SLSA's context-specific approvals and replay-defense patterns.

**(j) Fallbacks are selected by failure mode covered, not prestige.**

- Deterministic specialists, independent human review, cross-host rerun, different model family, and same-family clean review each cover different failure modes; none should silently satisfy a requirement it does not actually cover.
- Regulatory direction (EU AI Act adversarial evaluation for systemic-risk models; 2026 European AI Office work on external-evaluator independence) is treated as directional, not as a mandate of the exact vector.

## Recommendation and falsifier

- Retain risk-scaled `V0`–`V3` verification with an explicit vector record; keep exact deterministic gates non-substitutable for the properties they encode; require a genuinely different failure domain for `V2`/`V3`; treat unknown relationship metadata as unknown rather than independent; use a blinded preregistered evaluation to establish dimension effects.
- Principal falsifier: if a universal strong verifier is non-inferior within five points on `V2`/`V3`, not more than five points worse on common-mode misses, gains no more than five points in any defect family from the independent path, and cuts review effort by at least 30 percent, the risk-scaled recommendation loses.

## What this does not prove

- It does not show public standards converged on the `V0`–`V3` scheme (they did not), that every vector dimension raises defect recall by a known amount, that "different provider" is inherently better than "different family" or vice versa, that higher tiers are always economically optimal, or that these internal tiers are legally mandated.
- Deterministic gates establish only their encoded property, not general correctness or security.
- No public dollar estimate for the tiers is offered; cost is expressed as resource composition. The proposed five-point margin is a preregistration choice, not a discovered constant.

## Open Owner decisions

- Canonical examples for risk-class boundaries (routine-reversible vs sensitive; irreversible external effects; when a policy change becomes constitutional).
- Which canonical vector relationships must be positively evidenced versus permitted to remain unknown per tier; an unknown may never satisfy a positive independence predicate.
- The empirical materiality margin.
- Human-review qualification and conflict-of-interest policy.
- The receipt lifetime ceiling.
- Whether provider/account/host claims stay hypotheses until the blind matrix isolates them.

## Relevance to later waves

- The `V0`–`V3` contract, the explicit vector record, the evidence-precedence ordering, and the downgrade-receipt validation properties are the vocabulary the verification/evaluation lane should reuse.
- The preregistered matrix is the concrete measurement design for converting plausible independence dimensions into measured ones.
- The explicitly unverified provider/account/host effects and the correlated-error and wrong-gate (oracle-failure) questions are research gaps later waves should schedule measurement for rather than assume.

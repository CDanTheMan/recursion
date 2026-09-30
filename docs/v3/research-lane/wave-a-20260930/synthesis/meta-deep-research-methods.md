# Deep Research methods (meta synthesis)

## Provenance

- Source: `raw/ds-1-deep-research-methods.md`, a Deep Research capability briefing placed in Wave A as orientation context, not as a Recursion lane deliverable.
- The report describes the Deep Research product itself and cites OpenAI documentation and related vendor material; it is not about any Recursion lane.
- Retrieved 2026-09-30. Not independently verified by Recursion. Claims below are as the report's sources state them, at that date.
- Status: guidance for running the other Wave A sessions. Not a decision, not a lane result.

## Scope

- In scope: how the research loop works, how to steer and scope a task, evidence discipline, reliability limits, citations, output formats, task duration, compute and commercial cost, and source-access constraints.
- Out of scope: any substantive question about a Recursion lane; no lane topic, language, store, framework, or vendor is selected here.
- Framing: read this as operating guidance for the sessions that do investigate lanes, not as evidence about those lanes.

## Key findings

- **Research loop, not one-shot search.** Ordinary search is query → retrieve → summarize. Deep research is an iterative loop: define scope → build a plan → search → extract → re-check sufficiency → refine queries → cross-check → synthesize → cite → deliver, with a verification step at the end. This iteration is the core difference from one-shot search.
- **The plan is reviewable and steerable.** Users can inspect the proposed plan, follow progress, interrupt and redirect, and constrain available sources. Treat the plan as a checkpoint to review, not an opaque product.
- **Scoping is a contract.** Convert the objective into an answerable specification: decision, audience, geography/time bounds, term definitions, source requirements and exclusions, depth, required comparisons, acceptable uncertainty, and output format. Broad-but-irrelevant output is the common failure mode a tight scope prevents.
- **Evidence hierarchy and triangulation.** Recommended policy (not a platform guarantee): primary/official first; original research and datasets next; reputable independent reporting for context and contested facts; secondary synthesis mainly for discovery; low-authority sources as leads only. Consequential claims should be triangulated, not accepted because a citation exists.
- **Hallucination and confidence limits.** The report says the system can hallucinate facts, draw incorrect inferences, confuse authoritative material with rumor, and miscalibrate confidence. Keep four distinctions visible: evidence vs inference, absence of evidence vs evidence of absence, consensus vs truth, and citation count vs evidence quality.
- **Citation behavior.** Completed outputs carry citations or source links and a sources-used section. A good citation answers both "where did this come from" and "does that source actually establish this." Citations can be syntactically valid yet substantively wrong, so attach them close to the claim and verify the source supports it.
- **Deliverable formats.** Structured cited reports downloadable as Markdown, Word, and PDF; editable reports, presentations, or spreadsheets can be requested when supported. Mermaid is useful as a textual diagram spec but is not a promised export format.
- **Historical per-task time range.** The original published range was roughly 5–30 minutes per task; a planning heuristic is ~5–10 min bounded, ~10–20 min ordinary multi-source, ~20–30 min broad. This is a planning heuristic, not a service guarantee, and multi-pass or documented work is a larger workflow.
- **Compute and cost intensity.** The report describes deep research as compute-intensive and metered explicitly (credit-based or token-based depending on contract), with cost driven by breadth, depth, large uploaded corpora, long outputs, repeated verification, and artifact generation. Terms can change and should be checked when budgeting.
- **Source-access and paywall limits.** Default sources are the public web and uploaded files; authenticated sources require supported, enabled, authorized connections, and no connection overrides the underlying provider's permissions. A paywalled source is fully usable, snippet-only, inaccessible (a lead, not evidence), or usable via an authorized service — the honest answer to inaccessible evidence is "not verified from the full source."

## Practical implications for Recursion's research sessions

- Use the research loop, not one-shot search, for any lane question whose hard part is comparing and reconciling sources.
- Make the plan an explicit review checkpoint before accepting output; interrupt and redirect when scope drifts.
- Write each session's request as a research contract: objective, audience, scope, definitions, source policy, verification rules, freshness "as of" date, deliverable, decision standard, and exclusions.
- Impose an evidence hierarchy and triangulate consequential claims; keep reported facts, calculations, and inference visibly separate.
- Require the model to search for contradictions and disconfirming evidence, and to state uncertainty rather than fill gaps.
- Treat citations as claims to verify, not as proof; flag inaccessible/paywalled material instead of reconstructing it from snippets.
- Budget for time and compute: longer investigations cost more, triangulation costs more than accepting first results, and artifact generation is extra.
- Record provenance classes distinctly so a session's output is not mistaken for a lane result or a decision.

## What this does not establish

- It does not establish any fact about a Recursion lane, or select a language, store, framework, or vendor.
- It does not make Deep Research output authoritative or validated; the report itself documents hallucination, inference, authority-confusion, and confidence-calibration risks.
- It does not guarantee the 5–30 minute range, the stated cost amounts, or export formats; these are dated, product-level descriptions subject to change.
- It does not guarantee source coverage: paywalls and permissions remain limits, and web research inherits search and language bias.
- It does not replace independent verification; nothing here is independently verified by Recursion.

## Open questions

- Which lane sessions actually benefit from the full research loop versus ordinary search?
- What minimum research contract should each Wave A session use, and who reviews its plan?
- How should a session classify and label sources so confidence stays calibrated?
- What, if any, budget or quota guidance should govern how many deep-research tasks a session may run?
- How should inaccessible or snippet-only evidence be recorded in a session deliverable?
- When a session's output feeds a lane result, what independent re-verification is required?

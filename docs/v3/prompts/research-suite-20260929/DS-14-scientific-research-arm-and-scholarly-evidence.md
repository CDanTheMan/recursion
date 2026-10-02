---
title: DS-14 — Scientific research ARM and scholarly evidence
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-14 — Scientific research ARM and scholarly evidence

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. Supplying this document is the invocation; it makes no repository or provider call on its own.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone harness and harness orchestrator; Hermes is a retired control plane and an optional upstream integration. Workers are
bounded executors. An implementer's own PASS is never acceptance; independent review is
required, and missing verification is never a pass. `CONTROL_PLANE.md` is the operative
constitution; a research session may propose amendments but must never edit it. No research
session performs implementation, provider/model/authentication/configuration changes,
spending, deployment, publication or merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula,
captures and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs,
pinned source, licenses, peer-reviewed work). Classify every consequential claim as
source-documented, locally observed, inferred or unverified; keep `unknown` distinct from
zero. Model consensus and vendor marketing are not evidence. Every recommendation needs a
competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never
secrets, credentials, personal data, private repository content, local paths, or
account/infrastructure identifiers.

### Lane context

- A scientific research ARM is a goal-scoped executive that uses the same goal, delegation, route, context, evidence, privacy and verification contracts as a development ARM. It is a profile/capability, not a separate executive tier, and it delegates bounded workers and verifiers.
- `SourceRecord` is a provenance record: canonical URI plus persistent identifiers, title/creators/publisher, explicit version and dates, retrieval time, adapter/API revision, request and content digests, editorial and access states, license, related sources, locators, privacy classification and an expiry/revalidation trigger. `ResearchClaim` is one exact falsifiable proposition with claim type, goal/decision scope, population/workload/time tuple, assumptions, typed source edges, locators or data hashes, support/contradiction/applicability status, experiment ids, reviewer, confidence, history and expiry.
- Typed source edges are `supports`, `contradicts`, `qualifies`, `replicates`, `updates`, `mentions`, `metadata-only` and `inapplicable`. Contradictory evidence stays typed; differing populations, methods, interventions, endpoints or workloads produce heterogeneity or `unknown`, never a winner by citation count.
- Source lifecycle: discovered, identified, retrieved and verified, with inaccessible, quarantined, expired and corrected/superseded/retracted/withdrawn states preserved separately. Discovery snippets, titles, abstracts, citation counts and graph edges do not by themselves support a claim.
- Architecture-research standard has three evidence classes: external mechanism evidence (papers, standards, public systems), local structural evidence (exact source, tests, contracts) and empirical fit evidence (preregistered experiments). A paper cannot prove local fit without the latter two, and a local benchmark cannot establish a general scientific claim.
- Named candidate adapters (Crossref, OpenAlex, Semantic Scholar, arXiv, DataCite, Europe PMC/PubMed and standards bodies) are candidates only; each must be revalidated for version, license, quota, coverage, provenance and privacy before admission. Naming a candidate is not an adoption decision.
- Lean boundary: the kernel needs only generic `ResearchClaim`, `SourceRecord`, artifact, task, evidence and provenance schemas. Search providers, PDF parsers, citation-graph tools and notebook runtimes remain lazy capability plugins whose disabled path performs no network call, imports no heavy parser and starts no background indexer.
- `H-036` hard-floor corpus: fabricated and near-match identifiers, mismatched metadata, non-entailing sources, preprint/version/journal changes, corrections/retractions/withdrawals, paywalls, contradictory studies, inapplicable populations/workloads, citation rings, prompt-injected metadata, hostile table layouts, mutable/paginated APIs, duplicate preprint/journal records, license conflicts and negative/null results. Any accepted fabricated, retracted-as-current, stale, inaccessible, inapplicable or unverifiable evidence is an automatic failure.
- Evidence discipline: privacy, copyright and access policy apply before every search, upload or retrieval; private source is never sent to a public or contributor route; no identifier, benchmark or citation may be invented.

## Purpose

Decide whether Recursion can find papers and standards, reconcile conflicting evidence, design reproducible experiments and produce cited architecture claims within privacy, copyright and budget limits. This blocks the research ARM design and the acceptance hard floors for scientific evidence, false citations, retractions and reproducibility. It is blocking because adapter eligibility, claim-source typing, adversarial discrimination and the lean plugin boundary are still open.

## Authority and boundaries

The authority, scope, privacy and evidence-discipline constraints for this lane are restated in `## Baked context` above and govern this work. This prompt authorizes a report only: no runtime, provider, model, authentication, configuration, spending, deployment, publication or merge action. Private source is never sent to a public or contributor route, and no identifier, benchmark or citation may be invented. Keep public/synthetic briefs free of private project content, transcripts, local paths, credentials or account/infrastructure identifiers.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. Which official scholarly metadata and search APIs (for example Crossref, OpenAlex, Semantic Scholar, arXiv, DataCite, Europe PMC or PubMed, and standards bodies) expose persistent identifiers, versions, relations, licenses, editorial states and graph edges at current documented versions?
2. For each candidate adapter, what coverage, pagination, rate limit, authentication, terms, provenance and privacy does official documentation state, so admission can be decided without a live trial?
3. How are corrections, retractions, withdrawals, supersessions and preprint-to-journal version changes detected and forced back through claim adjudication?
4. Which full-text licensing and access models permit storage, quoting, embedding or publication, and how are paywalled sources represented without breaching access limits?
5. How should `SourceRecord` and `ResearchClaim` carry provenance, typed source edges, applicability tuples, confidence, history and expiry without becoming an overgeneralized schema?
6. Which adversarial fixtures (fabricated identifier, near-match metadata, outdated version, paywall, contradictory study, inapplicable population or workload, citation ring, prompt-injected metadata, hostile table layout, duplicate preprint records) discriminate a robust pipeline from a plausible one?
7. How does the system return `unknown` or heterogeneity instead of a winner by citation count when populations, methods, interventions, endpoints or workloads differ?
8. What do PDF, table and figure extraction preserve, and how are extracted values treated as observations rather than established facts?
9. How are experiments preregistered, timestamped and reproducible, including corpus manifest, persistent-identifier and version set, raw-response hashes, environment and seed, exclusions with reasons and negative results?
10. How does a verifier reproduce retrieval and analysis when sources are paywalled or mutable?
11. What is the lean plugin boundary: which schemas stay in the kernel, and which search providers, PDF parsers, citation-graph tools and notebook runtimes remain lazy plugins with a proven no-network disabled path?
12. Which scientific domains need specialized statistical or methodological reviewers, and how is that routing recorded?
13. How are search cost, rate limits, model quota and diminishing returns bounded, and how are private project names, prompts and sensitive negative findings excluded from exports?
14. How do papers support a mechanism while local structural and empirical evidence decide Recursion fit, and how is that three-level claim stated explicitly?

## Deliverable

- A source-pinned claim table with classification, confidence and expiry, using typed source edges such as supports, contradicts, qualifies, updates and inapplicable.
- A comparison of scholarly adapters and the generic `SourceRecord` and `ResearchClaim` schema, with naming of candidates that remain unadopted.
- An adversarial fixture suite covering false citation, outdated version, paywall, contradiction, inapplicable population and hostile extraction.
- A preregistered, reproducible experiment packet and a lean plugin-boundary proposal.
- Options with tradeoffs and a recommendation tied to a competing option and a decisive falsifier, plus open Owner questions.

## Non-goals

- Fabricating identifiers, metadata, benchmarks, citations or experimental results.
- Treating model consensus, citation count, a search snippet or one paper as proof of local fitness.
- Storing or publishing full text without an applicable license.
- Sending private project content or credentials to a public or contributor route.
- Adopting a specific adapter, marketplace, notebook runtime or hosted service.
- Running paid searches, private-canary work or runtime implementation.
- Reopening accepted Owner decisions or promoting a candidate into a default.

## Completion gate

- Every adapter claim is pinned to official documentation with version and retrieval date.
- Every research claim carries typed source edges, applicability and confidence, or is marked unknown.
- Adversarial fixtures include false-citation, retraction, version, paywall, contradiction and inapplicable-population cases.
- No fabricated identifier or benchmark appears anywhere in the report.
- Local-fit conclusions require local structural or empirical evidence, not papers alone.
- Every recommendation names a competing option and a falsifier.
- Privacy, copyright and secret scans are clean and no protected path is edited.
- Open Owner questions are listed and no decision is promoted.

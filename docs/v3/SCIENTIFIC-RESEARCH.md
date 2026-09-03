---
title: Recursion v3 scientific research capability
status: accepted-product-direction-with-open-design
last-updated: 2026-09-03
---

# Recursion v3 scientific research capability

## Product direction

Recursion should be able to conduct rigorous technical and scientific research in support of
architecture, configuration, implementation and owner decisions. A research ARM uses the same
goal, delegation, route, context, evidence, privacy and verification contracts as a development
ARM. It is a profile/capability, not a separate executive tier.

The capability should find papers, standards, datasets, official documentation and pinned
source; reconcile claims and contradictions; propose experiments; and produce inspectable
cited conclusions. It must not treat search-result summaries, model consensus, citation count
or one paper as proof that the complete Recursion system works.

## Research protocol

```text
Owner question / architecture hypothesis
  -> versioned research GoalSpec and decision to support
  -> gap matrix: claims, definitions, stakeholders, time/version, missing evidence
  -> source discovery through approved scholarly/web/repository adapters
  -> primary-source retrieval and exact SourceRecords
  -> claim ledger with support, contradiction, applicability and confidence
  -> focused disconfirmation and independent review
  -> local/synthetic experiment or explicit evidence gap
  -> cited synthesis, decision options and revalidation triggers
```

Every material conclusion records:

- the exact claim and whether it is fact, inference, hypothesis, proposal or owner direction;
- source title, authors/publisher, date/version, persistent identifier and retrieval date;
- primary/secondary status, peer-review/repository status and known corrections/retractions;
- method, population/workload, metrics and assumptions relevant to Recursion;
- supporting and contradictory evidence;
- license/access/copyright constraints on stored full text and quoted material;
- confidence, unresolved gap, decisive experiment and expiry/revalidation trigger.

## Candidate research capabilities

Capability plugins may provide:

- scholarly and standards discovery;
- DOI and bibliographic metadata resolution;
- paper/PDF retrieval under its access and license policy;
- structured text, table, figure and citation extraction;
- public source-repository and release archaeology;
- dataset discovery and checksums;
- citation graph, correction and retraction checks;
- experiment registration, execution adapters and result notebooks;
- claim-to-source ledgers and reference export;
- independent evidence audit and reproducibility checks.

Candidates such as Crossref, OpenAlex, Semantic Scholar, arXiv, publisher APIs, standards bodies
and institutional indexes must be evaluated against their current official documentation,
coverage, terms, rate limits, provenance and privacy before inclusion. Naming a candidate is not
an adoption decision.

The generic contract remains provider neutral. Crossref, OpenAlex, arXiv, Semantic Scholar,
DataCite and Europe PMC/PubMed are initial adapter candidates because their primary APIs expose
different combinations of persistent identifiers, versions, relations, licenses, editorial
status and graph edges. Provider query syntax, pagination, raw responses, embeddings and
domain-specific fields remain plugin data rather than core schema columns.

### Source and claim records

`SourceRecord` carries a canonical URI and persistent identifiers, title/creators/publisher,
explicit version and dates, retrieval time, adapter/API revision, request and content digests,
HTTP/representation evidence, size, editorial and access states, license, provenance, related
sources, locators, privacy classification and expiry/revalidation trigger.

`ResearchClaim` carries one exact falsifiable proposition, claim type, GoalSpec/decision scope,
population/workload/time tuple, assumptions and definitions, typed source edges, exact locators
or data hashes, support/contradiction/applicability status, experiment ids, reviewer,
human-adjudicated confidence, history and expiry. Source edges are one of `supports`,
`contradicts`, `qualifies`, `replicates`, `updates`, `mentions`, `metadata-only` or
`inapplicable`.

The source lifecycle separates editorial truth from access:

```text
discovered -> identified -> retrieved -> verified
       \          \           \          \
        inaccessible | quarantined | expired | corrected/superseded/retracted/withdrawn
```

Discovery snippets, titles, abstracts, citation counts and graph edges do not by themselves
support a claim. A retracted, withdrawn, inaccessible, stale or metadata-only record cannot
support an ordinary current claim. Corrections and new versions preserve the old record and
force affected claims back through adjudication. Crossref explicitly notes that Crossmark does
not guarantee that every update was deposited; `verified` therefore means identity, locator and
status checks passed, not that the scientific result is true.

## Architecture-research standard

Research for Recursion's own architecture must combine three evidence classes:

1. **External mechanism evidence:** papers, standards and public systems show that a mechanism
   exists, under stated assumptions.
2. **Local structural evidence:** exact Recursion source, tests and contracts show whether the
   mechanism applies and what it would replace.
3. **Empirical fit evidence:** preregistered experiments compare it against v2 and alternatives
   on declared workloads, quality floors and resource profiles.

A paper cannot prove local fit without the latter two. A local benchmark cannot establish a
general scientific claim. The synthesis must state which level it supports.

Contradictory evidence stays as a typed edge rather than being collapsed into a model-generated
consensus score. Where populations, methods, interventions, endpoints or workloads differ,
the result is heterogeneity or `unknown`, not a winner by citation count. Consequential source
identity should use two independent resolvers where available. W3C
[PROV-DM](https://www.w3.org/TR/prov-dm/) is the generic provenance vocabulary; provenance
records derivation but does not establish truth.

## Experiment support

Research ARMs should be able to create a preregistered experiment packet containing hypothesis,
baseline, treatment, workload, controlled variables, routes, randomization, sample size/power
rationale where applicable, metrics, quality gates, analysis method, stopping rule and expected
failure modes. Raw observations are immutable artifacts; transformations and exclusions are
versioned; results include uncertainty and negative findings.

Experiments involving model quality account for nondeterminism, task contamination, route and
model version drift, evaluator dependence, human review time and repair cost. A visually
impressive single run never establishes a default.

The immutable packet also records a corpus/source manifest, exact PID/version set, permitted
raw-response hashes, endpoint/query/cursor, adapter/model/plugin versions, environment and
seed, exclusions with reasons, independent verifier, negative and unknown results, license and
privacy disposition and revalidation policy. A registration must be immutable and timestamped;
registration is evidence of the plan, not evidence that its methods or results are sound.

## Privacy, copyright and access

- Project classification and egress policy apply before every search, upload or retrieval.
- Private source is never sent to a public/contributor research route without explicit eligible
  authority.
- Credentials and institutional access remain opaque brokered references.
- Full papers are stored only when access and license permit; otherwise store metadata,
  allowable excerpts, derived claims and owner-local references.
- Quotes and figures preserve attribution and applicable use limits.
- Research exports omit private project names, prompts, artifacts and sensitive negative
  findings unless explicitly authorized.

## Lean implementation boundary

The core kernel needs only generic `ResearchClaim`, `SourceRecord`, artifact, task, evidence and
provenance schemas. Search providers, PDF parsers, citation graph tools, notebook runtimes and
domain-specific methods remain lazy capability plugins. Disabled research plugins perform no
network call, import no heavy parser/runtime and create no background indexer.

## Acceptance questions

1. Which source classes and scholarly adapters provide sufficient provenance, correction and
   version metadata?
2. How are contradictory studies weighted without turning a model-generated score into truth?
3. Which paper content may be retained, quoted, embedded or published?
4. How does a verifier reproduce retrieval and analysis when sources are paywalled or mutable?
5. Which scientific domains require specialized statistical or methodological reviewers?
6. How are search cost, rate limits, model quota, local compute and diminishing returns bounded?
7. Can the same claim/evidence objects support software archaeology, benchmarks and scientific
   literature without an overgeneralized schema?

Release evidence requires a public synthetic research benchmark, adversarial false-citation and
retraction fixtures, contradictory-source reconciliation, reproducible transformations, privacy
tests and independent source verification. The research system must be able to conclude
`unknown` when evidence is insufficient.

The H-036 hard-floor corpus includes fabricated and near-match identifiers, mismatched metadata,
non-entailing sources, preprint/version/journal changes, corrections/retractions/withdrawals,
paywalls, contradictory studies, inapplicable populations/workloads, citation rings,
prompt-injected metadata, hostile table layouts, mutable/paginated APIs, duplicate
preprint/journal records, license conflicts and negative/null results. Any accepted fabricated,
retracted-as-current, stale, inaccessible, inapplicable or unverifiable evidence is an automatic
failure. No aggregate score may hide a privacy, copyright, provenance or contradiction failure.

Primary adapter anchors opened 2026-09-03 include [Crossref
REST](https://www.crossref.org/documentation/retrieve-metadata/rest-api/),
[Crossmark](https://www.crossref.org/documentation/crossmark/), [OpenAlex
sync](https://help.openalex.org/access/sync/), [arXiv
API](https://info.arxiv.org/help/api/user-manual.html), [Semantic Scholar Graph
API](https://api.semanticscholar.org/api-docs) and [DataCite
REST](https://support.datacite.org/docs/api). Each remains a candidate plugin and must be
revalidated for version, license, quota and coverage before use.

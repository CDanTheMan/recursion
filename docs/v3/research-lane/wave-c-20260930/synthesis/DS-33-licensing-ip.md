# DS-33 — Licensing, distribution, provenance, and IP clearance (synthesis)

## Provenance

- Raw report: `raw/ds-DS-33-licensing-ip.md`.
- Source prompt: DS-33 — licensing, distribution, provenance and IP clearance.
- Session: Wave C Deep Research (self-contained handoff); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved: source-documented study results, the report's own synthesis/recommendations, and general legal background. The report is a general landscape review; it cites studies and secondary legal commentary, not primary case filings or statutes in full.
- **This is legal-risk research, not legal advice.** It summarizes third-party findings and general copyright/licensing concepts. No counsel reviewed it, no jurisdiction-specific rights analysis was performed, and it is not a clearance opinion. Counsel is required before any distribution, publication, training, or release decision.

## The question

How do licensing, distribution, data provenance, and intellectual-property clearance interact for AI and data work, and what do the report's sources conclude about the risks and the practical mitigation that a project like Recursion v3 would need to account for?

## Key findings

**(a) The foundational structure is exclusive rights plus a grant.** Copyright owners hold exclusive reproduction, distribution, and derivative rights; a license is the owner's grant of permission. Permissive software licenses (Apache-2.0, MIT) broadly allow redistribution; GPL-family licenses require derivative works to be shared alike; Creative Commons content licenses vary (CC BY allows sharing with attribution; CC BY-NC forbids commercial distribution).

**(b) Legacy software licenses are ill-fitted to models and data.** The report cites Rajbahadur et al. that common OSS licenses (GPL, Apache) are "software-specific and are not clearly defined or bounded in the context of model publishing," and that ML datasets show instances of non-compliance between a dataset's stated license and the licenses of its sources. Mixing, for example, an Apache-2.0 model with GPL-covered data can create compliance conflict.

**(c) Model-specific licenses and license-reasoning tools are emerging.** The report cites the proposed OpenRAIL-M license and the MG Licenses family, plus the MG Analyzer (Rajbahadur et al., 2024), which encodes ML workflows in RDF graphs and applies semantic rules to detect missing rights or incompatible licenses across internal, share, and sell republication scenarios. The report notes that selling a model demands rights for redistribution, sublicensing, and commercial use.

**(d) Distribution terms determine what reuse is possible.** The report cites the FAIR principles' call for a "clear and accessible data usage license" and CASRAI guidance to use explicit license identifiers (with version and URI) and to avoid non-commercial terms for general-purpose data. It describes CC-BY-4.0 as a minimal-restriction "gold standard" and CC BY-NC-4.0 as blocking commercial redistribution. It also notes that applying CC BY-NC to models is increasingly seen as losing effectiveness for model publishing, with enforcement being challenging.

**(e) Provenance is the documented lineage of data.** The report defines provenance as origins, collection, and processing history; it cites IBM on provenance aiding regulatory compliance and reliable decision-making, and frames provenance as enabling reproducibility, attribution, and audit of rights and integrity. For AI, where datasets and models aggregate many sources, chain of custody is presented as central to both IP and quality control.

**(f) The report's headline audit finding is a widespread attribution gap.** It cites the MIT "Data Provenance for AI" project's audit of 1,800+ text datasets reporting that **over 68% had no license information** and that roughly **50% of claimed licenses were mislabeled** — which the authors describe as a crisis in misattribution. Closed/proprietary datasets were found to dominate specialized content, deepening an open-vs-closed divide.

**(g) A single metadata failure can propagate.** The report uses the Microsoft-Kaggle incident — a deleted LLM tutorial that linked to a Harry Potter text mislabeled "public domain" — to argue that poor provenance and clearance have legal and reputational fallout, and that governance with verifiable source metadata is the fix rather than a purely technical patch.

**(h) Acquisition method matters, not only use.** The report cites commentary that "how material was acquired matters almost as much as how it is used," and notes that even if training might be fair use, sourcing from pirated or mislabeled repositories is a separate risk. It cites the U.S. Bartz litigation and Chambers IP commentary to the effect that there is no explicit duty to document training data, but that demonstrating lawful acquisition has practical legal importance.

**(i) Multi-stakeholder mitigations are recommended.** For platform operators: mandatory provenance/license/proof-of-rights metadata fields at upload, automated scans for known commercial works (e.g. identifier lookups), and stricter review of "public domain" claims. For cloud vendors and documentation teams: use only clearly licensed corpora for examples, run IP/legal review for demos with recognizable characters, and warn users to verify licenses. For developers: assume new content is copyrighted unless proven otherwise, validate provenance by retaining receipts or licenses, use synthetic or clearly licensed subsets for experiments, and isolate models trained on uncertain data.

**(j) Tools and standards cited:** the Data Provenance Initiative (Longpre et al., 2023) and its Data Provenance Explorer for tracing dataset origins, licenses, and derivations; the MG Analyzer for automated license reasoning; the SPDX license list for standard machine-readable identifiers; DataCite's `rightsList` field; FAIR R1.1 linking reuse to licensing clarity; and dataset "model cards" noting provenance. The report also states the EU AI Act will require transparency (including training-data provenance and content licensing) for high-risk AI placed on the EU market.

**(k) Named gaps and next steps.** The report calls for standardized license vocabularies for AI models, better support for model-specific licenses, and wider adoption of provenance standards (naming W3C PROV and blockchain attestations as candidates), and notes many organizations still do not track full chain of custody. Its recommended next steps are enforcing metadata standards at upload, regular auditing/monitoring of large corpora, education and an "assume closed" default, and improved legal frameworks or safe harbors.

## Recommendation and falsifier

The report's practical recommendation is a governance combination: **enforce precise license and provenance metadata at ingestion, adopt provenance-tracking, and treat content as protected unless it is explicitly cleared** — supported by license-reasoning tools, explicit identifiers such as SPDX, and legal review where recognizable or commercial content is involved. It emphasizes that governance and editorial process, not only technical fixes, are decisive.

The report does **not** state a competing option or a single decisive falsifier, so none can be attributed to it. The closest observable tests implicit in its cited evidence are: whether metadata enforcement actually reduces missing/mislabeled license records relative to the audit baselines it reports, and whether cleared provenance demonstrably reduces infringement exposure. The report presents neither test as run.

## What this does not prove

- It is **not legal advice** and does not analyze Recursion's actual data, code, model, or distribution targets; **counsel is required before any release decision**.
- It does not establish that any particular license (open-source, Creative Commons, or model-specific) is safe or suitable for a given model, dataset, or commercial use.
- Its audit figures are the cited studies' results under their own scopes; they are not Recursion measurements.
- It does not report running MG Analyzer, the Data Provenance Explorer, or any other tool, nor any legal proceeding's outcome.
- It does not resolve jurisdiction-specific questions (e.g. fair use, database rights, the eventual EU AI Act obligations), and it cites secondary commentary rather than full primary legal texts.
- It does not select a provenance technology; W3C PROV and blockchain attestations are named as candidates, not conclusions.
- It does not establish that any Creative Commons or open-source term is enforceable for models in every jurisdiction; the report raises that as an open problem rather than a settled rule.
- It does not quantify the compliance cost of mandatory metadata enforcement, nor compare it against the audit baselines it cites.

## Open Owner decisions

- What license and provenance obligations apply to Recursion's own distribution, documentation, examples, and any model or dataset it might train or publish.
- Whether and when to engage counsel, and for which artifacts (code, data, demos, generated output) and jurisdictions.
- What metadata fields become mandatory at ingestion, and which automated scans run by default.
- Which provenance standard/vocabulary to adopt, and whether provenance records are tracked internally or published.
- Whether the "assume protected unless cleared" default is adopted operationally, and how clearance evidence is retained.
- How uncertain-data models or datasets are isolated within Recursion.

## Relevance to later waves

- The provenance-and-clearance vocabulary (source, license ID with version/URI, proof-of-rights, chain of custody) is input a later metadata or evidence-receipt contract may need.
- The audit gap and the acquisition-matters distinction are risk-model inputs for any wave touching data ingestion, training, publication, or third-party examples.
- The unresolved legal questions are Owner/counsel decisions that must not be promoted from research into policy, and no release action may proceed without counsel review.

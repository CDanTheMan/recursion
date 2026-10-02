# Recursion packet assessment and research handoff

2 October 2026

## Assessment

The packet is sufficient to commission four bounded, public-source research reports. It provides unusually clear questions, deliverables, non-goals and falsification requirements. It does not establish implementation readiness, route entitlement, legal clearance, measured savings or a passing repository gate. The useful next step is to reconcile the four reports into reviewable contract candidates, route evidence and a measurement specification before any separately authorized implementation or experiment.

Recursion is itself a harness and an orchestrator that delegates through other harnesses. Hermes is not its executive control plane. This current Owner clarification supersedes the repeated baked wording in the briefs and README. No replacement control-plane role is inferred. [O1]

The summaries of decisions D-018 through D-027 are supplied project context, not independently verified full decision records. D-022 is not summarized. Within those limits, retain the supplied direction: native harness plus orchestration; comprehensive capability coverage with lean, opt-in installation under D-019; Codex App Server as the first qualification priority under D-023; productive continuity under D-024; and Apache-2.0 for Recursion’s own release under D-026. Codex-first is a qualification sequence, not evidence that qualification has already occurred. The Apache-2.0 direction is not counsel clearance. [P1–P5]

## Six inputs and their roles

The archive contains six files, 55,949 expanded bytes and 46 numbered research questions. All six were inspected as static text. [P1–P6]

| Input | Role | Count |
|---|---|---:|
| README.md | Index, invocation guidance, supplied decision summaries and advertised structural gate | — |
| R-A-plugin-portability.md | Extension models, portable contracts, attenuation, inertness and porting cost | 12 |
| R-B-cross-harness-delegation.md | Delegation surfaces, continuity, loss and Honest Accounting | 12 |
| R-C-route-legal-and-licensing.md | Route terms, credentials, distribution and questions for counsel | 10 |
| R-D-quota-efficiency-measurement.md | Endpoints, baselines, controls, preregistration and falsifiers | 12 |
| check_research_stack.py | Repository-dependent structural checker, inspected but not run or imported | — |

The question catalogue at the end preserves every question number in condensed form. It is a coverage index, not a substitute for the full questions or an assertion that the research reports are complete.

## What the packet does well

Each research brief includes all eight required sections, a research directive and explicit completion conditions. The README references all four briefs. The lanes divide contract design, delegation, legal-risk evidence and measurement without making any one lane sufficient to approve the others. [P1–P6]

The strongest discipline is the insistence on source-documented, locally observed, inferred and unverified claims; unknown counters remain unknown. Competing options, decisive falsifiers and statements of what a recommendation does not prove are required. R-D expressly permits no-difference and worse outcomes. These requirements help prevent a proposed architecture or a plausible efficiency story from being mistaken for an established result. [P2–P5]

## Packaging limits and claim boundaries

The README describes a self-contained research handoff but also points to current repository authority and gap documents that are not included: CONTROL_PLANE.md, ANCHOR.md, AGENTS.md, DECISIONS.md and GAPS.md. The briefs’ parent-goal identifier says v2 while their development target says v3. This is an unresolved metadata discrepancy, not grounds to silently change the target. The supplied summaries are enough for bounded research; no repository checkout is needed for that work. [P1–P5]

The checker searches ancestor directories for a public-scope module and imports its forbidden-identifier pattern before evaluating the packet. That dependency is absent. Its intended checks cover the four fixed brief names, front matter, headings, directive text, unique titles, README references, relative links, forbidden identifiers and obvious secret patterns. Eight relative-link occurrences lead outside the archive to absent documents. The full advertised gate therefore cannot be certified from this archive. Static inspection supports only the narrower structural observations above. Even an eventual checker PASS would certify structure, not scientific quality, privacy completeness or Owner acceptance. [P1, P6]

The archive supplies no external bibliography, pinned public revisions, implementation snapshot, experiment dataset or measured outcomes. Claims about prior route findings, permissive licenses, interface behavior and helper-accounting gaps therefore remain packet-reported context until the research reports independently source them. Public interfaces document possibilities; they do not demonstrate runtime behavior, complete mediation, entitlement or a safe operational configuration. [P2–P5]

## Cross report dependencies

R-A proposes portability and grant semantics. R-B applies authority boundaries to delegation and defines observable continuity and Honest Accounting. Their shared interface should make requested capabilities, effective grants, attenuation, evidence provenance, refusals and unknown accounting explicit. A shared name is insufficient if the two reports assign it different semantics. These remain candidate contracts until reviewed and accepted. [P2, P3]

R-C supplies the separate route, license, distribution and counsel evidence needed to evaluate those candidates. It consumes concrete proposed operating and packaging modes from R-A and R-B; it cannot certify them technically. R-A and R-B may use R-C to identify questions and restrictions requiring counsel, but cannot turn an unanswered question into permission. Avoiding credential custody does not establish legal clearance or subscription entitlement. A source-code license does not license access to an external service. [P2–P4]

R-D consumes R-B’s accounting definitions and continuity boundaries, plus R-A’s porting-effort denominators where relevant. Its matched-baseline roster should explicitly use the nine routes named within R-B and R-C: Codex App Server / Codex–ChatGPT, Claude Code, Cursor, Gemini / Google CLI, Grok Build, Hermes, OpenCode, Antigravity and Pi. Product names are not interchangeable operating modes: route identity, interface, authentication mode and evidence version must stay distinguishable. This roster is a cross-brief design assumption, not a declaration that every route is accessible, comparable, technically qualified or legally cleared. [P3–P5]

Honest Accounting must use comparable attempt boundaries, units, denominators, helper treatment, interruption states and missingness rules. Where routes cannot expose comparable data, report separate endpoints or a non-comparable result rather than force a ranking. Provider-cache benefit and Recursion-owned evidence reuse must remain separate quantities. Savings outcomes cannot identify intentional vendor unoptimization; intent remains a distinct, untested hypothesis even if an efficiency difference is eventually observed. [P3, P5]

## Local handoff and decisions

### Phase 1 Reconcile the research evidence

Prerequisite: the four source-pinned reports and their explicit question coverage. Check that every one of the 46 questions receives an answer, bounded design proposal or named unknown; every route and ecosystem is covered; mutable claims have a retrieval date and a precise source or revision where available. Resolve inconsistent identifiers, grants, accounting units and evidence classes across reports. Preserve unknown identity or version rather than substituting a similarly named product.

Decision gate: independent review of the research evidence and Owner acceptance of any candidate normative contract. A report’s own completion checklist is not acceptance. Cross-references are useful for shared definitions, but R-A cannot approve R-B by citing it while R-B approves R-A by citing it back. Each consequential claim needs its own underlying evidence and an appropriate reviewer. No publication follows automatically from contract acceptance.

### Phase 2 Prepare the first qualification specification

Prerequisite: accepted authority and contract boundaries, a precise Codex App Server profile consistent with D-023, and an explicit list of unresolved route or entitlement questions from R-C. Produce a local specification for the later provider-free conformance fixture and continuity checks. Define disabled-path inertness, refusal oracles, evidence preservation, correlation of approvals and questions, authority re-checks, interruption handling and the treatment of missing counters. A deliberately different second adapter remains an architecture stress test; it does not replace Codex-first priority. [P2, P3]

Decision gate: a separate authorization and readiness decision before implementation or execution. A documented command or API is not a successful qualification. Retain D-019’s comprehensive build direction and lean opt-in shipping posture; sequencing evidence and tests does not authorize a smaller product commitment. [P1–P3]

### Phase 3 Freeze measurement and counsel packets

Prerequisite: stable, reviewed accounting definitions and a declared route operating mode. The measurement specification fixes endpoints, matching rules, counterfactuals, randomization, sample and stopping-rule selection, exclusions, analysis and immutable experiment identity before any run. Hard floors for authority, safety, privacy, correctness and reproducibility precede cost or speed comparisons. Missing sample-size inputs, effects and route counters remain unspecified or unknown; no result is imputed. [P3, P5]

In parallel, the counsel packet ties each question to public evidence, the exact proposed operating or distribution mode, and an expiry trigger. It preserves D-026’s Apache-2.0 direction while leaving contribution terms, notices, trademarks, bundled assets, service terms and entitlements for the relevant decisions. G-32 remains open until counsel returns. Lucas’s engagement of counsel is a separate step; this research does not contact counsel or create a legal commitment. [P4]

Decision gate: separately authorized operational work, counsel responses where required, and an accepted preregistration before any corresponding experiment or release claim. Measurements remain unmeasured until observations exist; designs remain proposed until accepted.

### Request the next snapshot only for a specific gate

To certify the full repository gate or exact governance compliance, request a current coherent snapshot containing the referenced authority, decisions and gap documents plus the checker dependency. For a route-specific counsel question, request only the actual operating mode and account, contracting or distribution facts that determine that question. For experiment readiness, request the current target revision, instrumentation and acceptance fixture. None of these is a prerequisite for completing the present bounded public research.

This handoff makes no target-test, provider/model-call, network-effect, authentication, installation, spending, counsel-contact, publication or repository-change claim. Those actions are outside the assessment.

## Complete question catalogue

The following 46 entries are condensed descriptions. The corresponding numbered questions and completion gates in the four source briefs remain the authoritative scope. [P2–P5]

### R A Plugin portability

1. Document extension units, discovery, lifecycle, permissions, capability declarations and contributions across every named ecosystem, including unknowns
2. Identify portable common shapes and host-specific glue with supporting evidence
3. Establish version negotiation, compatibility, schema epochs and deprecation evidence
4. Propose the minimal manifest with identity, grants, attenuation, privacy, budget, egress and evidence contracts
5. Define graph nodes, edges, attenuation, conflicts and precedence without widening GoalSpec authority
6. Separate early normative contract candidates from adapter-local details
7. Define and evidence disabled-path inertness across processes, network, mutation, secrets and ambient authority
8. Model porting cost with denominators, effort ranges, glue, translation and conformance failures
9. Compare the cheapest credible port with native rewrite, shim and no-port alternatives
10. Distinguish evidenced porting economies from speculation and specify falsifiers
11. Design a provider-free deterministic suite using the same synthetic plugin fixture
12. Define pass/fail oracles, stop conditions, alternatives and decisive contract falsifiers

### R B Cross harness delegation

1. Map all nine harnesses across submission, steering, stopping, resumption and observable results
2. Distinguish harness-held authentication from caller-supplied credentials per surface
3. Separate authenticated local CLI and hosted API paths, including Owner and counsel gates
4. Define authority, context, evidence and accounting continuity, degradation and recoverability
5. Identify sourced loss points in questions, queues, compaction, forks, sessions and helper accounting
6. Preserve source-documented, locally observed and unknown states in delegation records
7. Keep canonical authority, evidence and the non-droppable control kernel outside upstream sessions
8. Specify minimal handoff, artifact rehydration, compaction detection and pre-effect authority checks
9. Define Honest Accounting for attempts, completion, interruptions, helpers and unknown counters
10. Compare native-only, single-harness and credential-intermediating alternatives with falsifiers
11. Design A-to-B continuity tests across compaction, source forks and simulated machine loss
12. Define endpoints, confounders, hard floors and continuity stop conditions

### R C Route terms and licensing

1. Collect per-route public terms on programmatic, headless, non-interactive, resale and local-client use
2. Identify documented distinctions between authenticated CLI driving and third-party credential custody
3. Collect evidence on access resale, subscription routing, quota circumvention and asset redistribution
4. Distinguish accounts, API keys, subscriptions, CLI logins and delegated identities
5. Separate source, binary, name and logo licenses, notices, trademarks and attribution evidence
6. Frame Apache-2.0 interoperability, patent, notice, asset, plugin and provenance questions for counsel
7. Compare wrapper bundling, adapter-only, interoperability naming and code-free contract publication
8. Identify remaining contribution, CLA, SDK, interface, trademark, notice and compatibility questions
9. Compare candidate contract or plugin licensing postures without reopening D-026’s own-release direction
10. Specify the counsel questions and evidence appendix needed to address G-32

### R D Quota and continuity measurement

1. Define every endpoint, unit and denominator for allowances, tokens, caches, helpers and human effort
2. Distinguish observable counters from provider-internal or unknown values
3. Retain unreported consumption, interruptions and partial completions without substituting zero
4. Measure human time, corrections, re-prompts and review effort without shifting costs out of view
5. Control, randomize or record cache, model, tier, tools, network, difficulty and session confounders
6. Match each direct-harness baseline by goal, revision, acceptance gate and explicit model and effort
7. Separate cold-start, warm-affinity, session-loss reconstruction and no-future-work counterfactuals
8. Separate cross-route evidence reuse from same-provider caching without adding them as one saving
9. Freeze hypotheses, endpoints, matching, randomization, sample, stopping, exclusions and analysis before runs
10. Define authority, safety, privacy, correctness and reproducibility floors and single-failure stops
11. Specify synthetic inputs, frozen toolchains and immutable identities for reproducible experiments
12. Define decisive burn and lock-in falsifiers, including no-difference and worse outcomes

## Source key

- P1: README.md, supplied packet dated 2026-10-02; overview, Authority and Gate
- P2: R-A-plugin-portability.md; Baked context, Research questions and Completion gate
- P3: R-B-cross-harness-delegation.md; Baked context, Research questions and Completion gate
- P4: R-C-route-legal-and-licensing.md; Baked context, Research questions and Completion gate
- P5: R-D-quota-efficiency-measurement.md; Baked context, Research questions and Completion gate
- P6: check_research_stack.py; static inspection of dependency lookup, imports, expected files and checks
- O1: Current Owner clarification accompanying this assessment, 2 October 2026; Recursion is a harness and orchestrator, and Hermes is not executive control

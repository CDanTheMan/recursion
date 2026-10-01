---
title: DS34 Decision journaling and calibration
source-prompt: DS-34 — Decision journaling and calibration
session: Codex alternative route (same self-contained handoff; Deep Research rate-limited)
retrieved: 2026-10-01
status: research-evidence-not-a-decision
verification: not independently verified by Recursion; no rerun
---

DS34 Decision journaling and calibration

Research synthesis and proposed reconciliation for Recursion v3

Prepared for Lucas and Hermes | Evidence reviewed 1 October 2026

Executive conclusion

Adopt, subject to Owner acceptance, a prospective forecast and review extension to the existing D-entry convention. Keep the monthly first-of-month review. Add explicit outcome dates and event triggers, a small set of resolution fields, and append-only review and amendment records associated with the original D-entry. Preserve the accepted Owner register and its authority. Do not create a second decision log.

The strongest defensible benefit is auditability: an independent reviewer can recover what was expected, why the choice was made, which observation would undermine it, and whether a promised review happened. Improved calibration is a testable downstream hypothesis. Neither a handful of resolved decisions nor a good outcome establishes forecasting skill, causal decision quality, or the superiority of the chosen technical option.

Three separations are essential:

A forecast outcome is not the same object as a decision falsifier. An event assigned 70% probability can fail to occur without disproving that probability. An explicitly precommitted operational threshold can nevertheless fire and require review.

A decision assessment is not an execution command. A fired falsifier creates evidence and an escalation obligation; it does not authorize a worker to reverse an Owner direction, alter the constitution, or stop a system beyond existing authority.

A favorable outcome is not proof of a good decision process. Process review uses the information and alternatives available at entry; outcome scoring uses the frozen resolution rule.

Evidence supports prospective probability measurement, careful feedback, outside-view comparisons, and protection against outcome-contaminated recollection. It does not establish an optimal monthly review frequency, a universal number of cases needed for calibration, a reliable improvement timetable for one person's technical decisions, or the effectiveness of this exact journal design. Recent work also disputes how much tournament training effects identify general forecasting ability rather than changes in question selection and timing. [S1–S8]

The recommendation is R1, with competing option R0: retain the present D-entry narrative and monthly review without the structured extension. R1 is justified initially by reconstructability and timely review, not by a promised statistical gain. Section 10 specifies observable falsifiers, the prospective evaluation, and the questions reserved for the Owner.

Report map

Evidence and limits  Sections 1 to 5  Questions 1 to 14

Schema and operating rules  Sections 6 to 8  Questions 15 to 20

Worked examples and recommendation  Sections 9 and 10

Claim table and source bibliography  Sections 11 and 12

Completion gate and acceptance boundary  Section 13

1 Scope evidence and authority

This report answers the 20 questions in the supplied DS-34 brief dated 30 September 2026. It is public and synthetic research. No private decision history, repository, actual D-entry template, constitution, or Owner register was inspected. Statements about Recursion's existing conventions are accepted as supplied context, not independently verified implementation facts. In particular, D-017 is treated only as the brief's historical example; its reasoning is neither reconstructed nor evaluated. [B0]

The brief describes a provider-neutral agent platform with a small deterministic kernel, typed adapters, bounded workers, and a hierarchy in which Lucas is final authority and Hermes is the executive control plane. This proposal concerns reviewable operating decisions within that accepted scope. It proposes neither a language, storage format, tool, automation, implementation, provider choice, nor constitutional change. It leaves accepted Owner decisions closed. [B0]

Evidence labels

The claim table uses two labels so the brief's two classification requests remain distinguishable. Epistemic classification is fact, inference, hypothesis, or proposal. Provenance is source-documented, locally observed, inferred, or unverified. A source-documented fact can be a fact about what a particular study found, without being a universal causal law. Local observation in this report is confined to explicitly identified synthetic arithmetic and artifact checks; no operational performance was observed.

Confidence is qualitative and applies to the stated, bounded claim. High means the cited source clearly supports it or it follows deterministically from the stated definition. Moderate means the finding is context-dependent, contested, or an extrapolation. Low or unverified means the needed evidence was not established. An expiry trigger means an event requiring reconsideration, not a fabricated expiration date for a classic study.

Primary experimental and methodological work receives priority. Practitioner formats are evidence of a documented practice, not evidence of efficacy or adherence. Official guidance establishes what a body recommends within its domain, not that its numerical adjustments transfer to Recursion. All public sources were retrieved on 1 October 2026. Source locators and publication versions appear in the bibliography and claim table.

What this investigation does not establish

There is no measured Recursion base rate, no observed local calibration curve, no test of the proposed checks against a runtime, and no implementation acceptance. Absence of a located controlled study of this exact journal or cadence is an evidence gap, not proof that the approach cannot help. No model-graded decision review was performed. The proposed checks are logical specifications and worked examples, not a claim of deployed behavior.

2 Forecasting evidence and scoring

Q1 What measurable forecasting skill means and what transfers

Forecasting tournaments make accuracy measurable by asking resolvable questions, recording probabilities before resolution, and applying a declared score across many outcomes. Mellers and colleagues reported improvements in observed geopolitical forecasting accuracy under training and teaming conditions and persistent high performance among selected forecasters. Several cited papers analyze overlapping Good Judgment Project data and are not independent replications. These findings support the possibility of measurable differences; they do not show that expertise, introspective confidence, or one successful project establishes skill. [S1, S2, S33]

The causal interpretation needs care. Hauenstein and colleagues' 2025 reanalysis models question selection and response timing as well as latent forecasting ability; adjusted training and team effects were reduced, eliminated, or sometimes reversed. The reanalysis is exploratory and was not preregistered. It is a model- and estimand-dependent challenge, not a demonstration that all training is harmful. A 2025 adversarial-collaboration proposal disputes treating useful strategy as nuisance variance and proposes common questions and response times for a new test. That proposal is not a completed result. [S3, S4]

Transfer to individual project decisions is therefore an inference with conditions. Questions must have stable definitions, honest entry times, observable resolution, an identified forecast horizon, and enough comparable cases to learn from. Inclusion and scoring must not depend on whether the outcome was flattering. Separately record interventions, scope changes, dependencies, and case difficulty. A person who both predicts and changes a project is participating in the process being predicted; this differs from passively forecasting many geopolitical events.

Tournament evidence does not identify the counterfactual outcome under the unchosen architecture. The log can reveal a missed expectation or a poor ex ante process. It cannot by itself prove that another choice would have produced a better result. A decision's expected utility, realized utility, forecast accuracy, and governance validity are separate review outputs. [I1]

Q2 Appropriate low volume measures

Use a small descriptive scorecard tied to original forecasts, with every score accompanied by its denominator and eligibility rule. The preferred primary probability measure is the binary Brier score, (p − y)², where p is the recorded probability and y is 1 if the defined event occurred and 0 if it did not. Lower is better; this single-event convention ranges from 0 to 1. Unknown outcomes have no numeric score. A mean over resolved eligible events summarizes this observed set, not an established level of general skill. [S5, S6; R1c]

Accuracy is agreement between forecasts and outcomes under a specified loss. Calibration is long-run agreement between assigned probabilities and observed frequencies among comparable forecasts. Resolution is the ability to separate situations having different event frequencies. Sharpness concerns the concentration or decisiveness of forecasts; boldness alone is not skill. A constant base-rate forecast can be calibrated yet have no resolution, and sharp wrong forecasts can score poorly. [S5, S7]

At the population level, let m(P) = E[Y given P] and q = E[Y]. Then expected Brier loss equals E[(P − m(P))²] − Var(m(P)) + q(1 − q). The first term is a calibration penalty, the second rewards resolution, and the third is outcome uncertainty. This identity explains why accuracy is not calibration alone. It is not an invitation to estimate these terms confidently from the small log; finite-sample plug-in estimates have the biases discussed below. [S5, S6]

At low volume, show each original p, outcome, score, forecast date, horizon, cohort and baseline. Report the number of distinct events, distinct projects, unresolved cases, cancellations, disputed outcomes and exclusions. Use paired score differences against an entry-time baseline on the same events when a defensible baseline exists. If none exists, say so. Do not create a flattering in-sample baseline after seeing results. [R1c]

Avoid presenting binned reliability diagrams, expected calibration error, estimated Brier decomposition terms, calibration regressions, significance stars, or league tables as stable evidence from a few heterogeneous cases. Finite-sample decomposition bias is established; dependence and sparse bins further complicate interpretation. There is no universal n at which a personal log becomes well calibrated. Ten revisions to one outcome are still one resolved event for an outcome count. [S6; I2]

For duration, retain actual and predicted units, signed error and absolute error. If forecasting a median, absolute error is aligned with that target; if forecasting a mean, squared error is aligned with it. State which functional was forecast. For an interval, report its nominal coverage, endpoints, realized coverage and width; coverage alone rewards unhelpfully wide intervals. A proper interval score or a distributional score is an optional later extension when the recorded forecast supports it. [S7; R1c]

Measure

Useful interpretation

Low volume failure to avoid

Per-event and mean Brier loss

Probability accuracy on the explicitly scored cohort

Calling one loss or a short streak calibration; mixing binary and multicategory scale conventions

Mean probability minus event frequency

Descriptive average overprediction or underprediction

Offsetting errors can cancel; this is not full calibration

Paired score difference from a locked baseline

Which forecast was better on the same observed cases

Different horizons, post hoc baselines or different case selection invalidate a like-for-like comparison

Brier skill score

Optional relative loss reduction against a meaningful nonzero baseline

Undefined for zero baseline loss and unstable for very small baseline loss; not a small-sample skill certificate

Reliability plot or decomposition

Later diagnostic when comparable data and uncertainty handling support it

Arbitrary bins, sparse counts and dependence create misleading precision; empty bins are unknown

Percent correct or AUC

Classification or ranking under a stated target

Neither is calibration; thresholding discards probability detail and single-outcome cohorts may make AUC undefined

Interval coverage and width

Descriptive uncertainty performance

Wide intervals can buy coverage; small counts cannot verify a nominal 90% or 95% guarantee

Review completion and debt

Whether the documentation process is functioning

A process metric is not forecast accuracy or decision quality

These are proposed reporting choices, with rejection conditions in R1c. Modern reliability-diagram methods address bin instability and add uncertainty quantification, but their assumptions do not create independent information in a sparse, dependent log. Interval-score methodology explicitly balances width and misses; it does not validate a software forecast merely because the same mathematical score has been used in another domain. [S28, S29]

Q3 Repeated feedback and the speed of improvement

Distinguish outcome feedback (what happened), calibration feedback (patterns in probability versus frequency), process feedback (how the information was used), and repeated updating while a question remains unresolved. They are not interchangeable interventions. A fresh probability informed by new evidence can improve a score near resolution without establishing that the forecaster learned a general skill. A stream of updates also creates dependence and a shorter effective horizon. [I2]

The feedback literature is mixed, not a monotonic story in which more reflection always improves judgment. The following primary studies distinguish training dose, outcome information, diagnostic feedback and actual learning. [S8, S19–S24]

Study and setting

Observed result

Boundary for DS34

Lichtenstein and Fischhoff 1980

Eleven sessions of 200 assessments in one experiment; most improvement followed the first feedback; related-task transfer was modest or absent

Rapid change followed a large assessment batch, not one resolved project

Benson and Önkal 1992

Four sessions of 55 forecasts; calibration feedback improved calibration in a step, while plain outcome feedback had little effect

Feedback type mattered; no linear rate or monthly interval follows

Stone and Opel 2000

Performance feedback reduced overconfidence; environmental feedback improved discrimination but did not improve calibration and increased overconfidence

Better domain discrimination and better calibration can diverge

Moore and colleagues 2017

Confidence and accuracy grew together as event resolution approached; no evidence calibration improved across a year or the three years

Continuing updates and already good calibration are not proof of accumulated calibration learning

Stone and colleagues 2023

Individualized feedback reduced confidence; calibration and accuracy improved in modified blackjack, but baseball improvements in overconfidence and Brier score were not statistically significant

Lower confidence alone is not the target; effects depend on the task

Martin and Mandel 2025

Two experiments with 610 and 871 participants found no calibration improvement from the tested outcome or practical-score feedback

Displaying a score does not guarantee learning; null results do not invalidate every feedback method

Jørgensen and Gruschke 2009

Twenty software professionals completed five tasks; added outcome feedback and substantial lessons-learned reflection did not outperform control on accuracy or uncertainty realism

Directly relevant caution for software retrospectives, limited by small sample and short pseudo-realistic task sequence

A follow-up sample of 83 professionals judged other developers' estimates using their historical errors; their uncertainty judgments were more realistic than the original developers' self-assessments. Because this comparison spans samples and task roles, it does not isolate framing as a causal effect. [S24]

No source establishes that one person becomes calibrated after one month, ten entries or three reviews. Outcome observability, comparability and information content constrain learning. A one-shot outcome cannot reveal a frequency pattern. The relevant speed may be measured in informative, comparable resolved cases rather than elapsed calendar time; no conversion is justified for Recursion. [I2]

For Recursion, retain both the original forecast and dated updates; make original-at-decision scoring primary. A secondary, explicitly named update score may use a common predeclared cutoff or common lead time. Do not substitute the last, near-certain update for the original commitment or count updates as new successes. Every review should yield either a specific change to a future forecasting rule, a reason no change is justified, or a named unresolved uncertainty. This is a proposed learning protocol, not a validated learning-rate claim. [R1b, R1c]

Q4 Domain expertise versus general forecasting skill

Technical knowledge and probabilistic judgment solve different problems. Domain knowledge helps identify mechanisms, constraints, failure modes and plausible comparison cases. Forecasting discipline concerns uncertainty, comparison, scoring and updating. Tournament predictors include cognitive and dispositional factors, knowledge and engagement, but their associations do not prove that a generally strong forecaster can replace technical expertise in architecture or project estimation. [S2]

Expert intuition is most defensible where useful regularities exist and a person has opportunities to learn them through informative feedback. An unfamiliar technical project with shifting requirements, novel dependencies and delayed ambiguous outcomes may not supply those conditions. Confidence and seniority are not substitutes for prospective measurement. [S9]

There is direct technical counterevidence to equating experience with calibrated uncertainty: Jørgensen, Teigen and Moløkken's four-study investigation found overconfident expert effort-prediction intervals. Conversely, it would be an overreach to infer that technical expertise is useless. Knowledge of the task may improve the estimate while uncertainty about that estimate remains understated. [S25]

Use a domain-informed forecast with an independently checkable resolver, rather than an authority-weighted confidence label. Review domain assumptions and probability judgment separately. A subject-matter expert may be right about a mechanism but wrong about prevalence, timing or a tail risk; a statistically fluent reviewer may overlook a technical dependency. No reviewed source establishes a universal superiority ranking for these roles in Recursion's actual project decisions. That transfer remains unverified. [R1b, R1g]

3 Journal formats and reviewable content

Q5 What is documented and what is actually revisited

Two useful practice families are a prospective decision journal and an architectural decision record. A practitioner journal records context, options, expectations and reasons, then compares them with outcomes at review. An ADR records context, decision, status and consequences so a later reader can understand why a choice was made and what superseded it. These are complementary documentation ideas, not reasons to introduce a parallel Recursion register. [S10, S11]

Published templates describe intended review behavior. They generally do not supply controlled estimates of how often each field is genuinely revisited, the rate at which personal journals are abandoned, or whether six-month, monthly or event-driven review is optimal. This report therefore does not turn a template's recommended cadence into an empirical effect. The missing evidence is specifically field-level adherence and comparative cadence effectiveness in a low-volume project log. [U1]

The distinction between prescription and observation is concrete. The Farnam Street template asks for context, alternatives, outcome ranges, expected probabilities and reasons. Nygard's ADR form records title, context, decision, status and consequences; it does not itself define probability scoring, falsifiers or scheduled review. Nygard permits status updates, whereas Recursion's stricter historical no-edit rule governs this proposal. Document a supersession relation in an addendum rather than copying that implementation detail. [S10, S11; B0]

The proposed review contract is stronger than a form: each required entry field has a later use, each due review has an owner, and the review record cites the entry values it used. Count records that were due but not reviewed. If a field is never used in a review, challenge its necessity instead of adding more prose. The minimum schema below is intentionally a set of semantic obligations; it is not a new physical template, file format or storage decision. [R1b]

Q6 The minimum that makes a decision reviewable

The seven conceptual fields in the brief are necessary: decision, options, choice, rationale, expected outcome, falsifier and review trigger. To make them executable as a review contract, attach identity, entry time, authority reference, evidence and a responsible reviewer. Expand expected outcome into an observable target with a horizon and a resolution method; expand a trigger into an explicit due time or a precisely observable event plus a time backstop. [R1a, R1b]

Do not make every decision pretend to be a probability forecast. If a normative, governance, or one-off choice does not admit a defensible quantitative target, record a qualitative assessable expectation and mark probability scoring ineligible with a reason. It still needs an observable falsifier under the existing rule. A probability field may be unknown; that is not 0%, 50% or missing permission to decide. Such cases remain visible in the review denominator and outside probability-score calculations.

The schema adds enough structure to distinguish an unobserved outcome, an unfalsified proposition, a falsifier that has fired, a missing source, and an authorized replacement. It does not require a transcript, hidden reasoning, exhaustive prose, a model-generated rationale, or an explanation invented after the event. Concise reasons and evidence available at entry are sufficient.

Q7 Graded outcomes and compliance ritual

For a graded outcome, predefine either an ordered set of exhaustive, mutually exclusive categories or a numeric target. A project could be completed by day 10, completed on days 11–20, or not completed by day 20. Assign probabilities that sum to 1 and freeze the category boundaries. Noncompletion is an observed category at the deadline; a missing measurement is not a fourth unfavorable outcome. [R1c]

For nominal categories use the declared multicategory Brier convention. For ordered categories use a ranked probability score if the ordering is meaningful. For a continuous quantity retain the raw value and a point, quantile or distributional forecast with a matching loss. Do not invent numeric distances for labels such as good, acceptable and bad unless those distances or utilities were specified. Outcome utility weights, if any, are also fixed before observing results. [S7; R1c]

A compliance ritual is an operational failure to test the entry, not a scientifically established universal trajectory of journals. Warning signs include identical boilerplate falsifiers, a completed checkbox without a resolution source, retrospective probabilities, repeated rescheduling without a reason, and fields copied but never compared. Proposed controls are an entry admissibility check, due-review coverage, evidence-linked resolutions and a burden audit. Adding mandatory prose is not the remedy for every omission. [R1b, R1f]

4 Reference classes and base rates

Q8 Choosing a comparison class without manufacturing certainty

Choose the class before learning the target's result. Define the unit of observation, start and end events, horizon, population, inclusion period and characteristics that affect the generating process. For a small technical operation, type of work, novelty, dependency count, external coordination, acceptance criterion and team capacity may be candidate descriptors. They are proposed descriptors, not empirically established Recursion predictors. Avoid splitting a tiny collection into so many subclasses that each contains one convenient example. [R1d]

Reference-class forecasting uses outcomes of comparable completed or otherwise tracked cases to inform a new estimate. Infrastructure research and official appraisal guidance demonstrate a serious outside-view methodology, but their project classes and adjustment percentages are not portable personal-project base rates. Comparability, data quality and a sufficiently informative class are prerequisites. [S12, S13]

When no appropriate class exists, record that finding. Use several defensible analogies or a broader class as sensitivity scenarios, explain mismatch, and keep the inside-view estimate distinct. Do not average unrelated populations merely to obtain a larger n. Do not present an analogy as a measured frequency. “No usable class found” is an informative state with a next evidence need, not zero risk.

The planning-fallacy evidence requires nuance. Buehler, Griffin and Ross found that explicitly connecting past experience to a present estimate reduced optimistic bias in an experimental condition; their discussion reports no corresponding improvement in absolute accuracy and warns that remembered past performance may be inaccurate or incomparable. Correcting optimism and improving predictive accuracy are different claims. [S14]

Software-specific work provides a closer but bounded analogy. Jørgensen and Sjøberg construct effort-prediction intervals from historical estimation error and demonstrate the method with 145 development tasks plus a comparison on 15 tasks. Their manuscript notes that chronological validation would have been preferable but task ordering was unavailable. It motivates preserving estimation stage and error distributions, not treating five local cases as enough to estimate a reliable tail. [S26]

A later randomized elicitation study with 60 software professionals found that historical-error prompts produced wider and more skewed intervals. Its author explicitly does not establish that those intervals were more accurate against eventual outcomes. Better-looking uncertainty descriptions and validated coverage are separate. [S27]

Q9 Base rates a small operation can construct

No local numerical rate is available in the brief. The following are measurement definitions for future records, not claimed measurements. Count all eligible cases from an entry-defined cohort, including abandoned and unresolved ones. For rates with delayed outcomes, distinguish a matured cohort from cases whose observation window is still open. [R1d]

Quantity

Proposed case and denominator

Observable value and caveat

Project length

All started projects of a declared class and entry period

Start to accepted completion; list still-open cases and their age separately; a completed-only median is conditional on completion

Rework

Cases with a defined acceptance event and the full stated follow-up window

Reopened or corrective-work threshold within that window; define rework before counting; early cases without full follow-up are pending

Abandonment

All started cases with a fixed observation horizon

Explicitly abandoned by that horizon; active cases are not automatically failures; report terminal noncompletion separately if the forecast defined it

Review debt

All review obligations due by an as-of instant

Outstanding due reviews and lateness; use obligation IDs so a reschedule cannot silently remove the old miss

Estimate error

Cases with comparable original estimates and observed target values

Signed and absolute error, plus original horizon and scope-change markers; no percentage error when the denominator is zero or undefined

Falsifier incidence

All eligible decisions with the same declared observation window

Confirmed fired events, false alarms and unevaluable conditions separately; missing observation is not a non-event

Q10 Recording updating and reconciling the outside and inside views

A reference-class record has a stable identity and version, inclusion rule, exclusions with reasons, observation window, underlying case references, event and denominator counts, unresolved count, data source and as-of date. Preserve the snapshot used by a forecast. Append new cases and corrections; a later class version must not retroactively improve the baseline against which an earlier forecast is scored. [R1d]

At entry, record three distinct things: the outside-view distribution or rate, the inside-view adjustment and its specific evidence, and the final forecast. A case-specific adjustment should name what is different and why that difference changes the target. A confidence assertion such as “this time is simpler” is not adjustment evidence by itself. Preserve the unadjusted forecast to compare both prospectively on the same future cases.

With few cases, emphasize raw observations, denominators and uncertainty. If a beta-binomial update is later used for an exchangeable binary cohort, disclose the prior and its effective weight. For a Beta(a,b) prior and k events in n observed eligible cases, the posterior mean is (a+k)/(a+b+n). This is conditional model arithmetic, not a measured frequency or a default product algorithm. Changing the prior or cohort after seeing results must be disclosed as a new analysis. [I3]

Synthetic example: an imagined matured cohort has 3 delayed cases out of 5; 60% is its empirical fraction. An illustrative Beta(1,1) prior gives 4/7, about 57%, as the posterior mean. The prior adds two pseudo-observations and materially affects such a small sample. Neither number estimates Recursion's actual delay probability, and exchangeability may be false. Do not export either as a local base rate.

Keep class revisions coarse and prospective. Record regime changes such as altered scope or capacity; retain earlier data visibly rather than selectively deleting bad outcomes. Prefer a sensitivity range across plausible class definitions to optimizing dozens of post hoc cuts. Any pooling or weighting scheme is a separate proposal needing validation; no universal shrinkage weight is warranted here. [R1d]

5 Biases selection and failure modes

Q11 Hindsight outcome bias and reconstruction

Fischhoff's experiments show that knowing an outcome can alter perceived prior likelihood and the apparent relevance of earlier information, often without awareness. Baron and Hershey show outcome-contaminated evaluations of decision thinking; a preregistered 2023 replication supports the direction in a different design and sample. Choice-supportive memory work shows distorted attribution of option features. These findings justify treating recollection as fallible; none tests the efficacy of this exact proposed journal. [S15–S18]

At entry, freeze the options, choice, probabilities or expectations, evidence cutoff and concise reasons. At review, first recover the actual record, then apply the frozen resolver, then assess process using only entry-available information. Record later discoveries separately. A reviewer can optionally compare a remembered forecast with the written one to expose a discrepancy, but the recorded original remains the scoring input. A discrepancy is evidence of inconsistency, not proof of dishonesty or a diagnosis of motivation. [R1g]

Evaluate process and realized result in separate fields. A sound decision can produce a bad outcome; a weak process can get lucky. Record whether crucial evidence was available but ignored, genuinely unavailable, or introduced after entry. If the original evidence was absent, call process quality unverified rather than reconstructing an impressive justification. Independent review should be performed by someone authorized and different from the implementer; a model-generated “PASS” is not acceptance. [B0; R1g]

Q12 Catching vague success criteria before entry

Vagueness arises when the target lacks a unit, threshold, deadline, population, evidence source, comparison baseline, treatment of missing observations, or a tie-breaking rule. “Works well,” “is maintainable,” “finishes soon,” and “no serious problems” cannot be scored consistently without operational definitions. A numeric threshold is still vague if the measurement method is unspecified. This is a logical resolvability requirement, not an empirical claim about how frequently engineers write vague criteria. [I4]

The entry-time review asks an independent reader to classify at least one clearly passing case, one clearly failing case and one boundary or missing-data case using only the entry. If the reader must add a definition, the forecast is not resolution-ready. This proposed test checks operational clarity; it cannot guarantee that the metric captures the Owner's real objective. A measurable but irrelevant target still needs judgment and authority review. [R1b]

Keep the target and falsifier distinct where they serve different purposes. For example, an expectation may concern acceptance by a date, while a falsifier concerns repeated recoverability failures under a specified test. A vague “if it stops being useful” does not become valid merely by being placed in a field named falsifier. The deterministic checker can flag a missing or structurally incomplete field; a human must judge whether its content actually challenges the decision rationale.

Q13 Journals that are never reviewed

The reviewed journal prescriptions establish that review is part of their intended method. They do not establish an abandonment rate, which exact fields people revisit, or a universally reliable cadence. This matters: claiming that first-of-month review is scientifically optimal would exceed the evidence. [S10; U1]

After-event-review studies supply adjacent evidence about review content. In a navigation setting, reviews of successful and failed events outperformed failure-only reviews; a laboratory study also examined learning from flawed actions within successful results. These findings support inspecting process after wins as well as losses. They do not compare monthly with event-driven personal journaling. Qualitative work in three design organizations found both effective and ineffective post-project explanations and remedies, cautioning against equating a completed review with learning. [S30–S32]

Preserve the existing monthly first-of-month obligation because it is Recursion's accepted convention. Add an explicit reviewer, a dated obligation, event-triggered attention, and visible overdue status. A journal whose reviews are repeatedly deferred has failed this operational purpose even if its prose is excellent. Measure completion of due reviews, age of outstanding obligations, missing resolution evidence and time burden; do not substitute the number of entries written. These are local process measures, not calibration estimates. [B0; R1f]

The monthly review should end each due item with a resolved outcome, an evidence-backed interim assessment and next due date, or an explicit unresolved state with an owner and missing evidence. Mere acknowledgement does not satisfy a scoring review. Deferral preserves the prior obligation and its lateness; it creates a new obligation instead of erasing the missed one.

Q14 Survivorship selection and lucky calls

Maintain a prospective eligible-case inventory. Record decisions that qualify for the log before their outcomes are known, including rejected proposals when relevant to inclusion accounting, abandoned projects and unscorable cases. Record why an item is outside scope without creating a probability for an unobserved counterfactual. A favorable subset of finished projects is not a representative denominator for all starts. [R1c, R1d]

Fix the primary target and score at entry. Do not turn one project into many nominally independent successes through related submetrics, many revisions or selective horizons. If several forecasts share a dependency, label that cluster and report the number of projects as well as questions. Display excluded and missing cases and conduct simple sensitivity analyses when their outcomes could change the story. Do not impute unknown as failure or success merely to simplify a chart. [I2; R1c]

Compare like with like: common target definitions, lead times, cases and scoring rules. Easier questions and later forecasts can produce better averages without better general judgment; the recent tournament reanalysis makes that identification problem concrete. Descriptive improvement on a small, changing set is a signal to investigate, not proof of learning. A lucky call earns its score and nothing more. [S3, S6]

6 Candidate schema and conceptual D entry mapping

Q15 Required and optional fields

The exact repository template is unseen. The following is a conceptual mapping onto the seven D-entry concepts supplied in DS-34, not a claim about existing field names or file syntax. Every existing D-entry keeps its identity, original wording, numbering and original reasons. New information is an associated append-only addendum; new decisions use the established D-entry convention only after the appropriate authority accepts them. This proposal is semantic and format-neutral. [B0; R1a]

Required means required for a new resolution-ready entry or review under this candidate policy. Historical omissions are marked unavailable in an addendum; they are never backfilled as though known at the original date. A missing historical probability therefore cannot be scored. Conditional fields are mandatory only when their stated condition applies; an explicit inapplicability reason is required where specified.

Field group

Required content and conceptual mapping

Why the reviewer revisits it

Identity and provenance

Existing D identifier; entry author; recorded-at time; effective decision time if different; version or addendum identity

Locate the unchanged original; detect late registration; identify who knew what when

Authority and scope

Applicable accepted OR reference, or explicit none known; decision owner; scope and authorized action boundary

Ensure review does not promote a proposal or override accepted Owner direction

Decision and choice

Concrete question or operating choice; selected option; context sufficient to interpret it

Identify the proposition actually tested; avoid reviewing a later, different choice

Options

At least the selected and credible competing option, including status quo where meaningful; reasons for any genuinely unavailable alternative

Prevent retrospective invention or disappearance of alternatives; inspect ex ante tradeoffs

Rationale and evidence cutoff

Concise reasons, decisive assumptions, source references and what was unknown at entry

Separate entry evidence from hindsight; test whether assumptions persisted

Expected outcome

Observable target, unit or categories, population, start and horizon; conditionality on scope or intervention

Apply the same target at resolution; distinguish changed conditions from a miss

Forecast and eligibility

Probability vector, point or interval specification when appropriate; otherwise explicit nonquantitative or unknown status with reason

Calculate only the score the record supports; prevent unknown becoming zero

Resolution contract

Resolver evidence source; method; deadline; tie or conflict rule; missing-data and cancellation treatment

Determine y or raw outcome without moving the goalposts; preserve ambiguity honestly

Falsifier

Observable condition challenging the rationale; threshold or criterion; observation source; applicable time window; responsible observer

Decide whether the precommitted condition fired and when; distinguish it from a probabilistic miss

Review obligation

Review owner; next due instant with timezone; concrete event triggers; monthly backstop linkage

Determine who owes which review and expose overdue obligations deterministically

Baseline status

Reference-class snapshot and baseline forecast if defensible; otherwise no usable baseline plus reason

Compare fairly with what was knowable then; stop retrospective benchmark selection

Scoring plan

Eligible target and score convention; primary original forecast; cohort and dependency or project identifier; optional secondary cutoff declared in advance

Avoid cherry-picked metrics, changed denominators and update-count inflation

Current projection

Initial open assessment; separate authority disposition and monitoring lifecycle; latest review reference; unresolved obligations; all derived from appended events

Find the current view while retaining the historical assessment and separating evidence from supersession

The table's required groups can be short. An explicit “no usable baseline; five past cases use incompatible acceptance criteria” is more informative than an invented rate. If a decision is not quantitatively forecastable, its scoring-plan group records that reason and remains subject to the falsifier and review obligations.

Conditional and optional details

Field

Status

Later use and constraint

Reference-class detail

Conditional when a baseline is used

Inclusion rule, n, events, missingness, snapshot date and mismatch; mandatory to interpret the number

Graded outcome boundaries

Conditional for categorical or ordinal targets

Freeze categories and order; ensure mutual exclusivity and exhaustiveness

Interval level or quantiles

Conditional for interval or quantile forecasts

Tell coverage from arbitrary bounds; specify the target functional and score

Source freshness limit

Conditional when a time-sensitive measurement is used

Make stale observation an unevaluable condition rather than a passing result

Material intervention or scope event

Conditional when the forecast conditions change

Preserve original target; append new conditional forecast; explain censoring or invalidation under the original contract

Amendment or supersession relation

Conditional on amendment or replacement

Identify predecessor, affected clauses, new authority and what remains in force

Cost and utility model

Optional unless the decision rule depends on it

Separate payoff preferences from forecast accuracy; do not infer unobserved utility

Sensitivity scenarios

Optional

Show whether a reasonable class, prior or assumption change reverses the decision

Reversibility and value of information

Optional

Help prioritize review and identify worthwhile evidence before commitment

Emotional state or confidence narrative

Optional and privacy-sensitive

Use only for a stated later comparison; never collect personal detail just because a template suggests it

External analogies

Optional

Explain transfer assumptions; label them analogies, not local observations

Required review record

A review addendum contains its own identifier, original D reference, reviewer and time, trigger or obligation fulfilled, frozen forecast version used, evidence references and as-of time, resolved outcome or explicit unknown, falsifier evaluation, score or ineligibility reason, process assessment, state assessment, authority-dependent next action and next due obligation. The field-to-use mapping below states why each is revisited. A reschedule addendum includes its reason and the original missed due time.

Required review field

Reason for later review or audit

Review identifier and original D reference

Recover the exact event and decision without confusing linked histories

Reviewer identity and review time

Verify attribution, independence and review latency

Trigger and fulfilled obligation identifier

Establish which obligation was satisfied; avoid clearing unrelated debt

Original forecast version used

Reproduce the score on the proper commitment-time target

Evidence references and as-of time

Reproduce resolution and check freshness or conflicting evidence

Resolved outcome or explicit unknown

Distinguish observed success or failure from missing evidence

Falsifier evaluation and observation time

Establish whether the separate decision criterion fired and when

Score or ineligibility reason

Recompute loss without excluding inconvenient cases silently

Process assessment

Check the reasoning against information available at entry, separately from result

Evidential assessment, authority disposition and lifecycle

Recover the current view while retaining prior failure, ambiguity and supersession

Authority reference and proposed or authorized next action

Verify that evidence review did not itself create execution permission

Next due obligation or explicit authorized closure

Identify remaining accountability, including outstanding outcome evidence

Reschedule reason and original due time, when applicable

Preserve the missed obligation and measure debt rather than erasing it

An independent reviewer must be able to distinguish what was copied from the original record from what was learned later. The review's signed-off status is separate from the implementer's claim. Disagreement is recorded with evidence; it is not silently resolved by overwriting the earlier assessment. [R1g]

7 Cadence triggers and state semantics

Q16 Concrete cadence with the evidence boundary

The candidate policy is a combination of time and event triggers. Its monthly date is inherited from Recursion's supplied convention. Its event hooks are engineering proposals to make review responsive to the exact evidence named in an entry. No reviewed study validates these exact timings, and no automation is being created. [B0; R1f]

Trigger class

Exact condition

Proposed handling

Evidence status

Entry gate

A new decision is about to become effective

Freeze the entry and resolve structural omissions before treating its forecast as prospective

Proposal grounded in resolvability and bias risks; not a cadence trial

Monthly time backstop

First day of each month in the Owner-selected timezone

Reconcile all active D records, outstanding obligations and unclosed event reviews; assign the next explicit due instant

Existing convention from B0; frequency efficacy unverified

Outcome time

The forecast's outcome horizon is reached

Obtain the predeclared resolution evidence; resolve or mark unknown with a new evidence due time

Proposal; avoids silently treating delay in evidence as nonoccurrence

Falsifier event

A valid observation satisfies the entry's falsifier in its window

Append the fired event immediately when observed; flag for authorized attention and independent assessment

Proposal tied to existing falsifier rule; no automatic authority expansion

Closure event

Project accepted, explicitly abandoned or otherwise closed under its contract

Resolve matured targets; account for cancellation and follow-up windows; do not discard the case

Proposal to reduce selection and review debt

Assumption or threshold event

Declared dependency, scope, capacity or metric threshold changes materially

Review whether original conditional target remains applicable; append a new forecast if warranted

Proposal; materiality threshold must be written beforehand where feasible

Evidence repair event

Missing or conflicting resolution evidence becomes available

Append a resolution or correction linked to the prior unclear review

Proposal; unknown remains visible until repaired

“Immediate” here means flagging on observation, not continuous monitoring, zero detection latency, or a new right to execute a kill action. The observer and source-update availability constrain detection. The morning brief provides the next existing attention surface for routine due items; urgent routes follow existing authority and escalation rules. An Owner-selected review service target should define when a flagged event must receive human review. Until selected, that service target is unresolved rather than invented.

At the monthly review, first reconcile denominators: eligible decisions, due obligations, unresolved events and missing falsifiers. Then resolve available outcomes, evaluate falsifiers, inspect assumptions, and assign explicit next obligations. Aggregate descriptive scores only after the case ledger is reconciled. Do not spend the entire review polishing a dashboard while overdue decisions remain unexamined. [R1f]

Q17 States and fired falsifiers

Avoid overloading one word with three meanings. The following vocabulary supports the requested current view, but is not one mutually exclusive state machine. Record assessment (open, held, failed or unclear), authority disposition (current, amended or superseded) and monitoring lifecycle (active or closed) separately. An authorized execution disposition records any choice to continue, investigate, hold an action, stop or replace it. “Held” below means the rationale held at the reviewed scope and horizon; it does not mean an operational PAUSE. [R1e]

State or disposition

Meaning

Appended transition and retention rule

Open assessment

Decision is recorded; relevant outcome or scheduled review is pending

Held, failed or unclear with evidence; an independent supersession disposition does not resolve the outcome

Held assessment

Available evidence supports the specified expectation or rationale at this review; no confirmed falsifier contradicts it

Further held, failed or unclear; never proof of timeless validity; any supersession preserves this assessment

Failed assessment

A verified operational falsifier fired or a separately defined decision criterion failed

The failed event remains in history; an evidenced correction may change the current assessment to open, held or unclear; authorized replacement is a separate disposition

Unclear assessment

Evidence is missing, stale, disputed or cannot distinguish the stated outcomes

Open for an explicitly renewed prospective period, held or failed with new evidence; supersession retains prior ambiguity

Superseded disposition

Authorized later D decision replaces all or a specified part of the operative choice

Historical assessment is retained; pending forecast outcomes and review obligations are still settled or explicitly closed

A current view can therefore say “failed; superseded; monitoring closed” without losing the failed assessment. A separate lifecycle indicator records whether future monitoring remains active or the record is closed. Closure is not a favorable verdict. A terminal review can close a held, failed or unresolved decision with explicit reasons. Supersession is also not a forecast outcome: it must not automatically turn an earlier forecast into success, failure or cancellation.

Record a falsifier event with observed-at time, evidence, predicate version, evaluator and result. Treat it as latched evidence pending assessment. A later measurement correction appends a retraction or revised evaluation with its reason; the original alert remains discoverable. Where data are absent or stale, evaluation is unknown, not false. Where the condition requires judgment, a deterministic checker can route a required assessment, not manufacture one. [R1e]

For probabilistic forecasts, “predicted event did not occur” yields the appropriate score. It does not alone warrant the failed assessment unless the decision's separately stated criterion says so. An 80% deadline forecast can miss while the selected choice remains justified by its expected benefit; a low-probability safety or governance threshold can fire and require attention even if the overall forecast was well calibrated. No score overrides authority. [I1]

8 Historical preservation and operational reconciliation

Q18 Amendments and supersession without rewriting history

An amendment is a new, dated assertion linked to the original D identifier. It records the reason, evidence, author, authority, effective time, exact affected proposition and whether it changes a future forecast, corrects an error, or replaces an operating choice. The original entry and original reasoning remain readable. Never silently edit probabilities, dates, options, rationale, falsifiers or resolution criteria after entry. [B0; R1a]

For a genuinely new decision, use a new D-entry under the existing numbering convention and link it to the predecessor. Do not assign or renumber actual IDs in this research. A view can show “superseded by [new D reference]” by deriving it from an appended relation, without modifying the historical text. An accepted OR reference remains authoritative; a D-level amendment cannot amend the OR itself.

Distinguish correction from forecast update. If a transcription error is discovered, preserve the erroneous original, append the evidence for the correction and state whether the primary score uses the originally submitted forecast or an independently verified entry-time value under a predeclared correction policy. If no such evidence exists, do not assert a better past forecast. A new belief based on new information is a new forecast version, not a correction of history. [R1a, R1c]

Q19 Reconciliation text for Owner consideration

Proposed text, not an adopted amendment: “D-entries remain the sole operating-decision history. Accepted Owner directions remain in the OR register and retain their existing precedence. Each new D-entry preserves its original choice, reasons, alternatives, expected outcome, observable falsifier and explicit review obligation. Forecasts and reviews may add structured, versioned metadata associated with that D-entry. Subsequent evidence, reviews, amendments and supersession are appended with attribution and authority references. Historical D-entries are not rewritten, renumbered or retrospectively supplied with forecasts. The first-of-month review remains the reconciliation backstop; entry-specific time and event triggers may cause earlier review. A fired falsifier requires an evidence-linked assessment and authorized disposition, not an automatic change in Owner authority.” [R1a, R1e, R1f]

What this adds: prospective resolution rules, uncertainty semantics, score eligibility, reviewer accountability, reference-class snapshots, explicit trigger predicates and an immutable review trail. What it does not duplicate: the D decision narrative, the OR authority register, project execution state, task management, incident evidence, source documents, morning-brief content, or the constitution. Use references to those records; do not copy their full contents into a second log. [B0]

Historical records can be indexed for discoverability and associated with a current review addendum. If their original falsifier is absent or ambiguous, record the deficiency and ask the authorized reviewer to formulate a prospective one. The new falsifier begins on its own date. It does not cure a missing historical forecast or justify a retrospective score. Accepted decisions are not reopened merely because the research proposes better documentation.

Q20 Morning brief kill criteria and deterministic flags

The morning brief is a projection of existing decision evidence and obligations, not a competing source of truth. Its input for each flagged item is the D reference, unchanged forecast version, trigger reason, evidence age, due time, accountable reviewer and next authorized step. A brief item that proposes a new decision is clearly a proposal until accepted under existing authority. [R1f]

Before execution of a consequential choice, record its forecast and falsifier. A morning observation can update evidence and trigger review, but it cannot retroactively become the prior expectation. Kill criteria should identify the observable threshold, source, time window and authorized disposition route before the relevant outcome. Where an accepted policy already authorizes a stop action, cite it; this report grants no new stop authority. [B0; R1e]

The following are deterministic logical conditions, independent of programming language, store or model. They are specifications for a later authorized implementation, not implemented code. Use an explicit as-of instant and timezone-normalized timestamps. Treat malformed or absent times as invalid data, never as an infinitely distant deadline. [R1f]

Flag

Deterministic condition

Meaning and limit

MISSING_FALSIFIER

No falsifier record, or required text is empty after whitespace normalization, or the structural predicate lacks its required target, criterion, source or observation window

Missing structure; cannot judge semantic adequacy or whether boilerplate is genuinely falsifying

INVALID_REVIEW_DATE

A review-required record has no valid next due instant

Data defect requiring attention; never silently treated as not overdue

REVIEW_DUE

An outstanding review obligation has due_at equal to or earlier than as_of

Queue attention at the deadline; equality is due

REVIEW_OVERDUE

An outstanding review obligation has due_at earlier than as_of

Past due; remains in the audit trail if deferred or superseded

FALSIFIER_FIRED

A valid, sufficiently fresh observation satisfies a supported predeclared predicate in its applicable window

A confirmed evidence event and escalation trigger; not an execution authorization

FALSIFIER_UNEVALUABLE

Observation absent, stale, invalid, conflicting, or requiring unresolved human judgment

Unknown evaluation; must not be folded into false

RESOLUTION_PENDING

Outcome horizon passed and no adequate resolution evidence exists

Evidence debt; no invented y or score

REVIEW_DISPUTED

Appended reviews disagree and no authorized resolution is recorded

Prevents an implementer's self-assessment becoming acceptance

The smallest requested check is MISSING_FALSIFIER OR REVIEW_OVERDUE. A robust design also includes INVALID_REVIEW_DATE; otherwise records without dates escape the overdue comparison. Evaluate outstanding obligations directly instead of relying only on a current state label: superseded records may still owe a final review or an outcome resolution. A completed review clears only the obligation it explicitly fulfilled. Missing verification is never a pass.

For free-text falsifiers, presence checking is deterministic but semantic validation is not. A later implementation could restrict mechanical evaluation to a typed set of predicates such as a numeric comparison, an explicit terminal event or a counted threshold, with unknown preserved. Selecting that grammar, its language or its store is outside this research. An unsupported predicate produces needs-review, not a fabricated pass or a model call.

9 Synthetic worked examples

All identifiers, projects, times, probabilities and outcomes in this section are invented illustrations. They are not D-017, accepted Owner directions, observed Recursion decisions, or measured local base rates. They demonstrate semantics and arithmetic only.

Example A Binary forecast and a separate falsifier

At 09:00 UTC on 1 October, a hypothetical D-example records a choice to run a bounded recovery experiment rather than defer it. The forecast is a 70% probability that the predeclared acceptance checklist will pass by 17:00 UTC on 15 October. The resolver is the independently reviewed checklist result at that deadline; absent evidence is unknown. The operational falsifier is two unrecovered failures in the specified test window using the specified trace evidence. The due review is the earlier applicable outcome review or the existing monthly backstop, with a named reviewer.

If the checklist does not pass and that nonpass is established, y = 0 and the original Brier score is 0.49. If it passes, y = 1 and the score is 0.09. If an entry-time baseline was p = 0.50, its score is 0.25 either way. On a miss, the paired original-minus-baseline difference is +0.24, worse on this one case. None of these single-case values establish calibration.

Suppose the second unrecovered failure is observed on 8 October. Append a fired-falsifier event and route it for authorized review without waiting until November. If acceptance remains a resolvable deadline target, retain it for scoring. If the accepted response cancels or changes the experiment, apply the original cancellation or intervention rule and record the event; do not silently erase the forecast. A later p = 0.20 update is a separate version and does not replace the 0.70 primary score.

Example B Ordered outcomes

A hypothetical forecast assigns 0.50 to completion by day 10, 0.30 to completion on days 11–20, and 0.20 to no completion by day 20. Observed completion is day 14. The observed category vector is (0, 1, 0). The unnormalized multicategory Brier score is 0.50² + (0.30 − 1)² + 0.20² = 0.78, on a 0-to-2 scale. If divided by two, it is 0.39; the convention must be named, and neither is silently pooled with the binary 0-to-1 version.

For the ordered version, forecast cumulative probabilities at the first two cutoffs are 0.50 and 0.80; observed cumulative indicators are 0 and 1. The unnormalized ranked probability score is 0.50² + (0.80 − 1)² = 0.29. Dividing by the number of cutoffs gives 0.145 on a 0-to-1 scale. This score respects order, but does not express the business cost of a delay unless a separate utility rule was declared. [S7; arithmetic checked locally]

Example C Continuous target and interval loss

A hypothetical duration forecast specifies a median of 12 calendar days and a central 80% prediction interval from 8 to 16 days, meaning the forecast 10th and 90th percentiles, not an arbitrary plausible range. The start is authorized commitment; the end is independently accepted completion. Observed duration is 18 days. Median absolute loss is |18 − 12| = 6 days. The interval width is 8 days, and the observation misses its upper bound by 2 days.

For a central interval with miscoverage α = 0.20, the standard interval score is width plus (2/α) times the distance below or above the interval when a miss occurs. Here it is 8 + (2/0.20) × 2 = 28 days. An observation inside the interval would incur its width alone. Lower is better. This balances excessive width against misses; it is not a probability that the decision was good. One miss cannot establish whether nominal 80% coverage is calibrated. Keep scores in days separate from dimensionless Brier scores and from effort-hour targets. [S29; arithmetic checked locally]

If this project remains unfinished at the observation cutoff, its elapsed age is not its completed duration. Record the censored observation or resolve a separately defined completion-by-date event; do not feed the current age into the completed-duration loss as though it were the final outcome.

Example D Unknown overdue and superseded

A hypothetical record's review was due at 09:00 UTC on 1 October. At exactly 09:00 it is due; at 09:01 it is overdue if its obligation is still outstanding. No valid falsifier produces MISSING_FALSIFIER regardless of the record's favorable narrative. No valid due time produces INVALID_REVIEW_DATE, not a false overdue result.

If a new authorized decision supersedes it at 10:00, the earlier 09:00 obligation remains overdue until explicitly fulfilled or closed with an authorized reason. If the outcome evidence is unavailable, the outcome is unknown and unscored. A reviewer may close the operational monitoring lifecycle while retaining unresolved outcome status. No false score of zero is created by closure.

10 Recommendation alternatives and decisive tests

R1 Extend the existing D convention prospectively

Prefer the linked append-only extension, structured resolver, explicit review obligations and small descriptive scorecard described here, subject to Owner acceptance and an independent compatibility review against the actual template and constitution. Competing option R0 is the present narrative D-entry convention with its existing falsifier and monthly review, without these added structured fields. R0 has lower entry burden; R1 offers more directly testable reconstruction and review obligations. The evidence does not yet establish that R1 improves local forecast quality.

The immediate decisive falsifier for R1's auditability claim is one materially consequential eligible pilot record for which an independent reviewer cannot recover the original expectation, original falsifier, resolution contract and review status without inventing or silently changing entry-time information. That failure requires repair or simplification before calling the schema reviewable. It does not authorize rewriting the historical entry.

For operational usefulness, the Owner should predeclare an acceptable entry and review burden, a review-service target, and a prospective evaluation window. Compare R1 with the defined R0 baseline on the same kinds of decisions and all due obligations. If R1 exceeds the agreed burden budget and does not improve the agreed reconstructability or timely-review criterion, reject or reduce the added fields. This is a falsifiable local adoption test, not a randomized estimate of causal efficacy. Do not use a few Brier scores as the adoption pass condition.

Historical preservation and Owner authority are mandatory constraints in both R1 and every admissible competitor. The components below are the recommendations referenced throughout the report. Each has a competing option, a decisive rejection condition and an explicit nonclaim. Numerical thresholds that depend on acceptable cost or risk are Owner decisions rather than literature-derived constants.

Component

Competing option

Decisive falsifier or rejection condition

What it does not prove

R1a Associate structured append-only metadata with D identity

Unchanged D narrative with dated unstructured addenda, while preserving all history

An audit cannot recover the original D content and temporal relationship to changes, or the mapping conflicts with the accepted constitution

Compatibility with an unseen exact template; an Owner amendment is still required where applicable

R1b Require the compact review contract

Freeform narrative with only a review reminder

Independent boundary-case review needs an unstated definition, or a required field has no actual review use within the agreed pilot

That additional fields alone reduce cognitive bias

R1c Use descriptive original-forecast scores

Small-sample calibration dashboards or retrospective success labels

Reproduction changes a primary score because forecast version, outcome, convention, denominator or eligibility was unspecified

General skill, counterfactual superiority or statistical calibration from a small n

R1d Preserve reference-class snapshots and adjustments

Inside-view-only estimate or ad hoc comparable anecdotes

The claimed class cannot be reconstructed from its inclusion rule, or its prospective paired forecasts are worse by the Owner's predeclared loss tolerance

A universal outside-view advantage or a measured Recursion rate

R1e Separate assessment from authorized disposition

One human-interpreted composite status with all execution still separately authorized

Any review state can override an OR direction or cause an action outside already granted authority

Automatic stopping, deployment safety or constitutional adoption

R1f Combine monthly backstop with specific triggers

Monthly-only review without additional event hooks

A qualifying observed event is missed beyond the declared service target, or an outstanding obligation disappears on rescheduling or supersession

Scientifically optimal monthly timing or reliable unattended monitoring

R1g Review recorded process separately from outcome

Outcome-only retrospective judgment

The reviewer must use later knowledge as if it were entry evidence, or self-assessment is treated as independent acceptance

Elimination of bias or proof of causal decision quality

Prospective evaluation protocol

Before adopting the extension, an authorized reviewer maps the semantic fields to the actual D-entry convention and checks precedence against the operative constitution. Then define which new decisions qualify, when registration is due, which observations are available, who reviews, the service target, burden budget and stopping conditions. Keep the denominator fixed by this rule rather than hand-selecting showcase decisions. This is a proposed protocol only; it has not been run.

During the agreed evaluation window, collect registration completeness, reconstructability failures, due-review completion, lateness, event-detection and review latency, missing evidence, exclusions and time spent. Report raw counts and individual failures. Resolve forecast outcomes as they mature even if the adoption window ends; do not discard long-horizon cases. Assess statistical forecasting improvement only if enough comparable independent information accumulates for an appropriate analysis, with no promised threshold or learning deadline.

At the end, independent review produces accepted, revise, rejected or insufficient evidence. The Owner decides adoption within existing governance. A successful documentation pilot establishes that the process can be followed under those conditions. It does not establish a statistically significant improvement in calibration or select a runtime implementation.

Open Owner questions

What is the exact current D-entry template, and where may append-only review metadata be associated without changing protected history? This is an implementation compatibility question, not permission for this report to inspect or edit it.

Which timezone and explicit due-time convention govern the first-of-month review? How are missed holidays or unavailable reviewers handled while preserving original lateness?

Which new decisions must carry a probability forecast, and which may use an explicit qualitative or ineligible-for-probability status?

Who is the accountable reviewer and independent acceptance authority for each class of decision? What evidence resolves a disagreement?

What review-service target follows an observed falsifier, and which existing authority permits each possible execution disposition?

Which initial classes are sufficiently comparable to track, and what source supplies the complete eligible-case inventory, including abandoned and unresolved cases?

What entry burden, review burden and observable adoption criteria are acceptable, and over what prospective window will R1 be evaluated?

How should immutable original-versus-verified-transcription-correction scoring be handled? What cancellation and material-intervention policies can be specified before future outcomes?

These are unresolved policy choices, not research findings and not newly accepted Owner decisions.

11 Source pinned claim table

Each row states the bounded claim supported. Source IDs resolve to dated references in Section 12. Retrieval date for every public source is 1 October 2026. “Falsifier” in this table means evidence that would defeat the stated interpretation or cause reconsideration; it is not an instruction to alter an accepted Recursion decision.

Claim

Source and version or date

Classification and provenance

Confidence

Expiry or reconsideration trigger

C01 Tournament training and teaming improved the reported observed accuracy metric; high performance can persist within that setting

S1 2014, Methods and Results; S2 2015, results; S33 2015

Fact; source-documented

High for bounded study result

New controlled evidence or changes in scoring, sample or target task; not universal transfer

C02 Adjusting question selection and timing changes estimated treatment effects on latent ability

S3 first online 4 Dec 2024, 2025 issue; abstract and Methods

Fact; source-documented

High that reanalysis reports this; causal interpretation contested

Common-question common-time experiment or alternative justified identification analysis

C03 The 2025 adversarial study page is a proposal disputing the treatment of strategy, not completed outcome evidence

S4 30 Jul 2025

Fact; source-documented

High

Publication of completed results; current public-search finding is not exhaustive absence proof

C04 Forecast accuracy, calibration and resolution are different attributes

S5 1973, partition; S7 2007, scoring framework

Fact; source-documented

High

Changed definitions or an incorrectly applied score; no empirical expiration assumed

C05 Conventional decomposition is finite-sample biased and depends on assumptions

S6 online 22 Mar 2012; sections 1–3 and 5

Fact; source-documented

High

An analysis outside the paper's assumptions or corrected methodological result

C06 Strictly proper scoring incentivizes honest probability reporting under its setup; it does not make probabilities true

S7 2007, definitions and categorical and continuous examples

Fact plus scope inference; source-documented and inferred

High

Incorrect score implementation, changed target or incentives outside setup

C07 Diagnostic calibration training can produce early gains after many judgments with limited transfer

S8 Oct 1980, abstract

Fact; source-documented

High for stated experiments

Failure to reproduce in comparable tasks; no one-project learning claim

C08 Calibration feedback and plain outcome feedback had different effects and no simple gradual learning curve

S19 Dec 1992, abstract

Fact; source-documented

High

New evidence with comparable tasks and feedback

C09 Feedback can improve discrimination while worsening overconfidence

S20 Nov 2000, abstract

Fact; source-documented

High

Replication or a target task with a different feedback mechanism

C10 Multiyear tournament data did not establish calibration improvement over time despite good calibration

S21 online 22 Aug 2016, Nov 2017 issue; discussion p 3562

Fact; source-documented

High

New longitudinal data that separate learning from selection and changing horizons

C11 Individualized feedback effects were task-dependent; reduced confidence alone was not sufficient

S22 online 28 Jun 2023; abstract and experiment results

Fact; source-documented

High

Replication or a materially different feedback design

C12 Tested outcome and practical-score feedback did not improve calibration in two large experiments

S23 online 8 Nov 2024, 2025 issue; experiments 1 and 2

Fact; source-documented

High

New evidence for a different task or diagnostic feedback; does not disprove every intervention

C13 Software lessons-learned reflection did not outperform controls in the main five-task study

S24 2009; main study and follow-up

Fact; source-documented

High reporting confidence; limited generalization

Larger or longer comparative technical studies; do not infer all retrospectives fail

C14 Expertise needs learnable regularities and informative experience; technical experts can still give overconfident effort intervals

S9 Sep 2009; S25 Feb 2004, abstract

Fact about synthesis and study; source-documented

Moderate to high within scope

Task regularity, feedback quality or prediction domain changes

C15 Practitioner journals and ADRs document fields and intended uses, not comparative adherence efficacy

S10 undated current page; S11 15 Nov 2011

Fact about prescribed formats; source-documented

High

Revised practice pages or direct adherence studies

C16 A reference class needs comparable cases and an empirical outcome distribution

S12 published 2006, author manuscript; S13 guidance updated 12 Feb 2024, sections 42 and 62

Fact about method and guidance; source-documented

High

Inclusion definition, environment or data quality changes; prospectively worse predictions

C17 Outside-view prompts reduced directional optimism without demonstrated absolute-accuracy gain in the cited experiments

S14 Sep 1994; Study 4 and discussion p 380

Fact; source-documented

High

New comparable evidence; remembered-history quality and comparability differ

C18 Historical software-estimation errors can inform interval construction, but small local tails are not validated by that study

S26 2003; method and evaluation

Fact plus transfer limit; source-documented and inferred

High for method; moderate for transfer

Different estimation stage, regime, task mix or prospective error distribution

C19 Historical-error prompts widened and skewed software intervals without establishing outcome accuracy

S27 2018 author manuscript; results and limitations

Fact; source-documented

High

Prospective coverage and proper-score evidence on the resulting intervals

C20 Outcome knowledge can alter prior-likelihood recollection and evaluation of decision thinking

S15 1975; S16 Apr 1988; S17 28 Jul 2023

Fact; source-documented

High for bounded experimental effects

Replication limits or claims about a new population; does not diagnose an individual

C21 Choice-supportive source-memory distortion is experimentally documented

S18 Mar 2000, publisher abstract

Fact; source-documented

High for reported effect

New evidence about task or memory mechanism; mismatch alone does not prove motivation

C22 Reliability plots depend on binning; modern alternatives still require appropriate inference assumptions

S28 online 17 Feb 2021; method and uncertainty discussion

Fact; source-documented

High

Dependence or heterogeneity violates inference assumptions

C23 Interval scores penalize both width and misses; source correction does not retract that method

S29 12 Feb 2021 with correction 5 Oct 2022

Fact; source-documented

High

New correction or mismatch between forecast quantiles and scoring convention

C24 Review content matters; successes can contain flawed processes worth reviewing

S30 Sep 2005; S31 May 2006; primary abstracts

Fact within studied settings; source-documented

Moderate transfer confidence

Different task and review design; no cadence comparison established

C25 Completed post-project reviews need not produce convincing learning

S32 Mar 1999, three-organization qualitative study

Fact about observations; source-documented

Moderate

Evidence from a different setting or process; not a prevalence estimate

I1 A forecast miss, decision falsifier, realized payoff and ex ante decision quality are distinct

Logical analysis in Sections 2 and 7; adjacent conceptual support S34 1993

Inference; inferred

High for distinction

A target definition explicitly equates particular criteria; authority still separate

I2 Low n, dependent updates, changing horizons and selected cases cannot support a strong calibration conclusion

S3, S6, S28 and Section 2 logical analysis

Inference; inferred

High

A sufficiently informative, comparable dataset with justified uncertainty analysis becomes available

I3 Beta-binomial example is conditional mathematics; no local frequency was measured

Section 4 synthetic assumptions; worked arithmetic

Inference; locally observed arithmetic and inferred model

High for arithmetic; model applicability unverified

Prior, event definition or exchangeability changes

I4 An outcome is not mechanically resolvable if its definition requires missing boundary or evidence rules

Sections 5 and 8 logical specification

Inference; inferred

High

Independent boundary-case review resolves all cases without new definitions

U1 Optimal monthly versus event cadence, field-level revisit rates and local calibration improvement are not established here

Targeted public-source search completed 1 Oct 2026; scope in Sections 2–5

Unverified hypothesis; unverified

Unverified effect; moderate confidence about identified gap

A directly relevant controlled or longitudinal study or local prospective evidence is found

P1 Append-only semantic extension, small descriptive scores and combined triggers are a proposed package

R1a–R1g, this report 1 Oct 2026

Proposal; inferred

High auditability rationale; usefulness unverified

Any decisive rejection condition in Section 10 or constitutional incompatibility

H1 Reliable prospective reviews may improve future judgment

Proposed evaluation in Section 10; mixed evidence S8, S19–S24

Hypothesis; unverified locally

Unknown

Comparable prospective loss fails to improve under an adequately informative design; low n may remain inconclusive

B0 Existing D history, falsifier rule, monthly review and OR authority are supplied constraints

DS34 brief, last updated 30 Sep 2026

Fact about supplied context; source-documented in brief

High about brief; repository state unverified

Authorized correction to supplied context; no permission to reopen Owner decisions

12 Sources and versions

B0. DS-34 decision journaling and calibration. User-supplied self-contained research brief, last updated 30 September 2026. Read in full. Authority and conventions are taken as supplied, not independently inspected repository facts.

S1. Mellers, B., et al. (2014). Psychological Strategies for Winning a Geopolitical Forecasting Tournament. Psychological Science, 25(5), 1106–1115. Online 21 March 2014. DOI 10.1177/0956797614524255. Relevant: Methods and Results, including question selection and score convention. Author full text

S2. Mellers, B., Stone, E., Atanasov, P., et al. (2015). The Psychology of Intelligence Analysis: Drivers of Prediction Accuracy in World Politics. Journal of Experimental Psychology Applied, 21(1), 1–14. Online 12 January 2015. DOI 10.1037/xap0000040. Relevant: predictor analyses and causal limitations. Author full text

S3. Hauenstein, C. E., Thomas, R. P., Illingworth, D. A., and Dougherty, M. R. (2025). Rethinking the Role of Teams and Training in Geopolitical Forecasting: The Effect of Uncontrolled Method Variance on Statistical Conclusions. Psychological Science, 36(1), 3–18. Online 4 December 2024. DOI 10.1177/09567976241266481. Relevant: abstract, data treatment, exploratory-analysis caveat and model interpretation. Publisher full text

S4. Mellers, B. (30 July 2025). Adversarial Collaboration on the Forecaster Benefits of Teams and Training. Wharton Mack Institute funded research proposal. Relevant: competing interpretation and proposed controlled design; not completed results. Author proposal

S5. Murphy, A. H. (1 June 1973). A New Vector Partition of the Probability Score. Journal of Applied Meteorology, 12(4), 595–600. DOI 10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2. Relevant: reliability, resolution and uncertainty partition. Publisher record

S6. Ferro, C. A. T., and Fricker, T. E. (2012). A Bias-Corrected Decomposition of the Brier Score. Quarterly Journal of the Royal Meteorological Society, 138, 1954–1960. Online 22 March 2012. DOI 10.1002/qj.1924. Relevant: sections 1–3 and 5; author preprint consulted, which lacks final journal metadata on its first page. Author preprint

S7. Gneiting, T., and Raftery, A. E. (March 2007). Strictly Proper Scoring Rules, Prediction, and Estimation. Journal of the American Statistical Association, 102(477), 359–378. DOI 10.1198/016214506000001437. Relevant: proper scoring definitions and categorical and continuous forecast scores. Author full text

S8. Lichtenstein, S., and Fischhoff, B. (October 1980). Training for Calibration. Organizational Behavior and Human Performance, 26(2), 149–171. DOI 10.1016/0030-5073(80)90052-5. Relevant: primary abstract reporting session counts, early learning and transfer limits. Publisher abstract

S9. Kahneman, D., and Klein, G. (September 2009). Conditions for Intuitive Expertise: A Failure to Disagree. American Psychologist, 64(6), 515–526. DOI 10.1037/a0016755. Relevant: environmental validity, learning opportunities and confidence. This is a primary author synthesis rather than a journal experiment. Full text

S10. Farnam Street. How a Decision Journal Changed the Way I Make Decisions, template included. Undated current practitioner page, retrieved 1 October 2026. Relevant: prescribed entry and review fields; no adherence study. Practitioner original

S11. Nygard, M. (15 November 2011). Documenting Architecture Decisions. Relevant: title, context, decision, status, consequences and supersession; a practitioner experience report. Author original

S12. Flyvbjerg, B. (2006). From Nobel Prize to Project Management: Getting Risks Right. Project Management Journal, 37(3), 5–15. Author manuscript deposited as arXiv 1302.3642 in 2013. Relevant: method and class selection, manuscript pages 7–9. Author manuscript

S13. Homes England (2024). Optimism Bias and Contingency at Homes England. Published 8 February; current page updated 12 February 2024. Relevant: sections 42 and 62 on class size and representativeness. Institution-specific guidance, not a universal minimum sample size. Official guidance

S14. Buehler, R., Griffin, D., and Ross, M. (September 1994). Exploring the Planning Fallacy: Why People Underestimate Their Task Completion Times. Journal of Personality and Social Psychology, 67(3), 366–381. DOI 10.1037/0022-3514.67.3.366. Relevant: Study 4 and general discussion, especially page 380. Full text

S15. Fischhoff, B. (1975). Hindsight Is Not Equal to Foresight: The Effect of Outcome Knowledge on Judgment Under Uncertainty. Journal of Experimental Psychology Human Perception and Performance, 1(3), 288–299. DOI 10.1037/0096-1523.1.3.288. Relevant: three experiments and their interpretation. Full text

S16. Baron, J., and Hershey, J. C. (April 1988). Outcome Bias in Decision Evaluation. Journal of Personality and Social Psychology, 54(4), 569–579. DOI 10.1037/0022-3514.54.4.569. Relevant: five experiments on evaluation under known outcomes. Primary abstract

S17. Aiyer, S., Kam, H. C., Ng, K. Y., Young, N. A., Shi, J., and Feldman, G. (28 July 2023). Outcomes Affect Evaluations of Decision Quality: Replication and Extensions of Baron and Hershey's (1988) Outcome Bias Experiment 1. International Review of Social Psychology, 36(1), article 12. DOI 10.5334/irsp.751. Relevant: preregistered replication, N = 692, changed between-participant design. Publisher article

S18. Mather, M., Shafir, E., and Johnson, M. K. (March 2000). Misremembrance of Options Past: Source Monitoring and Choice. Psychological Science, 11(2). DOI 10.1111/1467-9280.00228. Relevant: choice-supportive source-memory result in primary abstract. Publisher abstract

S19. Benson, P. G., and Önkal, D. (December 1992). The Effects of Feedback and Training on the Performance of Probability Forecasters. International Journal of Forecasting, 8(4), 559–573. DOI 10.1016/0169-2070(92)90066-I. Relevant: four-session feedback comparison in primary abstract. Publisher abstract

S20. Stone, E. R., and Opel, R. B. (November 2000). Training to Improve Calibration and Discrimination: The Effects of Performance and Environmental Feedback. Organizational Behavior and Human Decision Processes, 83(2), 282–309. DOI 10.1006/obhd.2000.2910. Relevant: distinct effects on overconfidence and discrimination. Primary abstract

S21. Moore, D. A., et al. (2017). Confidence Calibration in a Multiyear Geopolitical Forecasting Competition. Management Science, 63(11), 3552–3565. Online 22 August 2016. DOI 10.1287/mnsc.2016.2525. Relevant: discussion page 3562 and distinction between within-question updates and learning over years. Author full text

S22. Stone, E. R., Luu, J., Costello, C. K., and Somerville, A. H. (2023). Automated Calibration Training for Forecasters. Journal of Behavioral Decision Making, 36(4), e2334. Online 28 June 2023. DOI 10.1002/bdm.2334. Relevant: baseball and modified-blackjack experiments. Publisher full text

S23. Martin, M., and Mandel, D. R. (2025). Calibration Feedback With the Practical Scoring Rule Does Not Improve Calibration of Confidence. Futures and Foresight Science, 7(1), e199. Online 8 November 2024. DOI 10.1002/ffo2.199. Relevant: two experimental null results and their task limitations. Publisher full text

S24. Jørgensen, M., and Gruschke, T. M. (2009). The Impact of Lessons-Learned Sessions on Effort Estimation and Uncertainty Assessments. IEEE Transactions on Software Engineering, 35(3), 368–383. DOI 10.1109/TSE.2009.2. Relevant: main twenty-professional study and 83-professional follow-up. Author manuscript

S25. Jørgensen, M., Teigen, K. H., and Moløkken, K. (February 2004). Better Sure than Safe? Over-confidence in Judgement Based Software Development Effort Prediction Intervals. Journal of Systems and Software, 70(1–2), 79–93. DOI 10.1016/S0164-1212(02)00160-7. Relevant: primary abstract reporting four studies. Publisher abstract

S26. Jørgensen, M., and Sjøberg, D. I. K. (2003). An Effort Prediction Interval Approach Based on the Empirical Distribution of Previous Estimation Accuracy. Information and Software Technology, 45(3), 123–136. DOI 10.1016/S0950-5849(02)00188-X. Relevant: interval method, 145-task illustration, 15-task comparison and chronological-validation limitation. Author manuscript

S27. Jørgensen, M. (2018). Looking Back on Previous Estimation Error as a Method to Improve the Uncertainty Assessment of Benefits and Costs of Software Development Projects. Author conference manuscript. Relevant: randomized elicitation with 60 software professionals and outcome-validation limits, pages 4–5. Author manuscript

S28. Dimitriadis, T., Gneiting, T., and Jordan, A. I. (2021). Stable Reliability Diagrams for Probabilistic Classifiers. Proceedings of the National Academy of Sciences, 118(8), e2016191118. Online 17 February 2021. DOI 10.1073/pnas.2016191118. Relevant: binning instability, CORP and uncertainty assumptions. Publisher article

S29. Bracher, J., Ray, E. L., Gneiting, T., and Reich, N. G. (12 February 2021). Evaluating Epidemic Forecasts in an Interval Format. PLOS Computational Biology, 17(2), e1008618. DOI 10.1371/journal.pcbi.1008618. Relevant: interval scoring. The 5 October 2022 correction, 18(10), e1010592, corrects example values and figure lines; current corrected article and correction consulted. Article and correction

S30. Ellis, S., and Davidi, I. (September 2005). After-event Reviews: Drawing Lessons from Successful and Failed Experience. Journal of Applied Psychology, 90(5), 857–871. DOI 10.1037/0021-9010.90.5.857. Relevant: navigation quasi-field study. University primary abstract

S31. Ellis, S., Mendel, R., and Nir, M. (May 2006). Learning From Successful and Failed Experience: The Moderating Role of Kind of After-event Review. Journal of Applied Psychology, 91(3), 669–680. DOI 10.1037/0021-9010.91.3.669. Relevant: laboratory review-content comparison. Primary abstract

S32. Busby, J. S. (March 1999). An Assessment of Post-project Reviews. Journal of Applied Behavioral Science, 35(1), 109–130. DOI 10.1177/0021886399351009. Relevant: qualitative observations in three design organizations. Publisher full text

S33. Mellers, B., Stone, E., Murray, T., et al. (May 2015). Identifying and Cultivating Superforecasters as a Method of Improving Probabilistic Predictions. Perspectives on Psychological Science, 10(3), 267–281. DOI 10.1177/1745691615577794. Relevant: persistence of selected high performers under enriched conditions; overlaps the GJP research program. Full text

S34. Murphy, A. H. (1 June 1993). What Is a Good Forecast? An Essay on the Nature of Goodness in Weather Forecasting. Weather and Forecasting, 8(2), 281–293. DOI 10.1175/1520-0434(1993)008<0281:WIAGFA>2.0.CO;2. Relevant: distinctions among consistency, quality and decision value. Publisher record

13 Completion gate and acceptance boundary

Gate from DS34

Where addressed

Research disposition

Calibration bias and base-rate claims source-pinned or unverified

Sections 2–5 and 11–12

Primary findings bounded; transfer and cadence gaps explicitly labeled

Schema reconciles with D convention and names nonduplication

Sections 6 and 8

Conceptual mapping complete; exact template compatibility remains for authorized independent review

Every required field has a later review reason

Required entry and review record descriptions in Section 6

Stated for each group; conditional and optional fields distinguished

Concrete triggers and evidence

Section 7

Time versus event conditions stated; convention separated from efficacy evidence

Concrete hindsight and vagueness mitigations

Sections 5–6

Entry freeze, independent boundary cases, source cutoff and separate process review

Small-sample limits plain

Sections 2, 4, 5 and 9

No strong calibration claim; unknown distinct from zero; updates not independent events

Every recommendation has alternative and decisive falsifier

Section 10

R1 and R1a–R1g each specified

Existing D history and protected records unchanged

Scope and historical-preservation sections

Research only; no repository, constitution, register or D-entry changed

Open Owner questions separate

End of Section 10

Eight questions separated from findings

The deliverable is a research proposal, not implementation or Owner acceptance. Independent content review and actual-template reconciliation are distinct from the authoring and arithmetic checks on this document. Missing verification remains missing verification. No declared completion of the research converts any proposed rule into authority.


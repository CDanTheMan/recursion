# Project Recursion — Deep Research Prompt Suite

**Purpose:** scope the autonomous loop before building it.
**Constraint:** 22 days until Berkeley starts (Aug 26). Run R1–R3 first; they can invalidate the design. R4–R7 are build-support and can wait.

**How to run:** one per sitting, not all at once. After each, write a half-page "what this changes" note. If a report doesn't change a decision, it was the wrong prompt.

---

## R1 — Does the core premise hold? (run first)

> Investigate the empirical evidence on AI-assisted and adaptive learning for advanced STEM material, specifically at the undergraduate physics / upper-division level.
>
> Cover: (a) what learning-science research says about retrieval practice, spaced repetition, interleaving, and "desirable difficulties," and how each translates to an automated system; (b) the generation and self-explanation effects — evidence that explaining a concept back in your own words produces retention and transfer gains beyond solving problems alone, and how that effect is best elicited; (c) controlled studies on LLM tutors and AI study tools — measured effects on retention and transfer, not satisfaction scores; (d) documented failure modes, especially the illusion of fluency, premature hint delivery, and metacognitive miscalibration; (e) which parts of physics learning are demonstrably accelerable by automation versus which appear to require unassisted struggle time.
>
> Prioritize peer-reviewed work and controlled trials over vendor claims and blog posts. Where evidence is thin or contested, say so explicitly rather than filling the gap.
>
> Deliverable: an evidence summary, then a list of concrete design constraints an automated study system should obey to avoid the documented failure modes.

**Why this is first:** if the answer is "curriculum generation isn't the bottleneck, problem-solving hours are," the whole overnight-curriculum design changes shape.

---

## R2 — Grounded problem corpora

> Map the landscape of rigorous, publicly available physics problem sets **with verified solutions**, suitable for building a curriculum spanning introductory mechanics through upper-division classical mechanics, E&M, quantum, and statistical mechanics.
>
> Cover: MIT OpenCourseWare problem sets and exams; UC Berkeley course archives (7-series and upper division); Caltech and Stanford publicly posted materials; graduate qualifying exams; standard problem collections (Irodov, Morin, Griffiths, Kleppner) and which have published or community-verified solutions; physics olympiad archives; the Physics GRE corpus.
>
> For each: coverage, difficulty calibration, solution availability and reliability, licensing and terms of use for personal study, and machine-readability of the format.
>
> Deliverable: a comparison table plus a recommended sourcing stack for a system that must ground on verified problems rather than generating its own.

---

## R3 — Verifying LLM-generated technical content

> Investigate practical techniques for automatically detecting errors in LLM-generated physics and mathematics — the subtly-wrong-but-plausible failure mode, not obvious nonsense.
>
> Cover: symbolic verification with computer algebra systems (SymPy and similar); automated dimensional and unit analysis as a correctness gate; limiting-case and special-case checks; numerical spot-checking against known solutions; self-consistency and multi-sample agreement methods and their measured reliability; ensemble or cross-model checking; published error rates for frontier models on physics benchmarks and where they concentrate.
>
> Deliverable: a layered verification pipeline design, with an honest estimate of what fraction of errors each layer catches and what gets through.

---

## R4 — Unattended agentic loop architecture

> Research architectural patterns for long-running autonomous agent loops that operate unattended (overnight or continuously) on a personal server.
>
> Cover: scheduling and orchestration patterns (cron-style batch versus event-driven versus persistent daemon); state persistence and handoff between runs; guardrails against runaway loops, retry storms, and context bloat; supervisor/worker patterns where a cheap model triages and escalates to an expensive one; observability — how operators detect that an unattended agent has silently degraded; documented failure post-mortems from people running these in production.
>
> Focus on real operator reports and source-available implementations. Exclude vendor marketing.
>
> Deliverable: two or three candidate architectures with tradeoffs, plus a checklist of guardrails that appear in every working setup.

---

## R5 — State and memory architecture for multi-project supervision

> Investigate how solo operators and small teams structure persistent state so that AI agents can resume work across sessions and supervise multiple parallel projects.
>
> Cover: file-convention approaches (CLAUDE.md / AGENTS.md / status and state files) and what makes them survive context loss; structured versus freeform state; how to represent "what is blocked, stale, or waiting on a decision" in a form an agent can diff; retrieval and memory patterns for long-horizon agents and their known failure modes; monitoring patterns borrowed from SRE practice that translate to a one-person operation.
>
> Deliverable: a recommended file and directory convention with example schemas, designed for one person supervising 4+ concurrent projects.

---

## R6 — Cost and quota engineering for sustained loops

> Research how to run continuous agentic workloads economically across subscription and metered pricing, as of late 2026.
>
> Cover: prompt caching mechanics and realistic hit rates for agent workloads; context-window management strategies that reduce cost without degrading output; model-routing economics across capability tiers; current subscription quota structures versus per-token pricing for sustained use, including terms-of-service constraints on third-party harnesses; where local inference on consumer hardware is genuinely cheaper than API calls, and where it isn't.
>
> Deliverable: a routing table mapping task types to model tiers with cost estimates, plus the two or three optimizations with the largest measured impact.

---

## R7 — Decision journaling and calibration (optional)

> Investigate evidence-based practice for personal decision journaling and forecast calibration.
>
> Cover: the forecasting and calibration research literature (Tetlock and successors) and what transfers to individual decision-making; decision-journal formats used in practice and which fields actually get reviewed later; base rates and reference-class forecasting applied to personal project decisions; documented failure modes — hindsight bias, vague success criteria, journals that get written but never reviewed.
>
> Deliverable: a decision-log schema with required fields, and a review cadence with specific trigger conditions.

---

## R8 — Measuring understanding, not just correctness (run early)

> Investigate how to automatically assess whether a learner genuinely understands a technical concept, as distinct from whether they can produce a correct answer.
>
> Cover: the research basis for self-explanation and teaching-to-learn effects and how explanation quality has been operationalized and scored in studies; oral-examination and viva practice — what probing questions reliably separate understanding from memorized procedure; misconception taxonomies in physics education research (force concept inventory and successors) and how diagnostic instruments are constructed; automated scoring of free-form explanations, including known reliability limits and how LLM graders fail; techniques for probing transfer, such as asking a learner to predict a novel limiting case or identify why a plausible-sounding wrong explanation is wrong.
>
> Deliverable: a rubric and question-generation strategy for an automated "explain it back" checkpoint, with an honest assessment of what such a checkpoint can and cannot verify.

**Why this matters:** this is the checkpoint that defines "real progress" in the loop. Solving is necessary; re-explaining is the gate.

---

## R9 — Ingestion pipeline for dense technical material

> Research practical pipelines for converting dense technical source material into structured, machine-usable form for a personal study system.
>
> Cover: extraction of mathematical content from PDFs and textbooks, including LaTeX and formula recovery and where OCR reliably fails; lecture-video and audio transcription quality for technical vocabulary; note structures that have held up in practice for STEM material (Zettelkasten, Cornell, atomic notes) and what evidence exists for each; how to represent a concept dependency graph so a system knows what must be understood before what; chunking and indexing strategies for retrieval over technical corpora, and the specific failure modes when equations and prose are separated.
>
> Deliverable: a recommended ingestion stack with tooling options at each stage, and a concept-graph schema for representing physics prerequisites.

---

## Scope boundaries — what these deliberately exclude

- **No market or investment research.** Keep that in CSL Labs, separate.
- **No "best AI tools 2026" surveys.** Those age out in weeks and answer nothing.
- **Nothing about model selection.** That's a quarterly review item, not a foundation question.

## Kill criteria for the August proof of concept

Define these before spending the second $200. Written down, in advance.

- **Learning loop:** by Aug 26, has it produced problem sets you actually worked, with a gap map that matched your real weak spots?
- **Supervisor loop:** has it surfaced at least one thing you would have missed, and been wrong fewer than roughly a third of the times it escalated?
- **Build loop:** did session-resume time measurably drop?

If two of three fail, drop back to one subscription in September. That is a successful experiment, not a failure.
